#!/usr/bin/env python3
"""
MSRA Material Passport — 跨阶段产物追踪管理器

Usage:
    from passport import PassportManager
    
    pm = PassportManager("/path/to/project/.msra/passport.json")
    pm.add_artifact({"id": "cleaned_data", "stage": "stage_1", ...})
    pm.update_status("cleaned_data", "completed", "sha256:abc...")
    ok, missing = pm.verify_prerequisites("stage_2")
    resume_point = pm.get_resume_point()
"""

import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Optional


DEFAULT_ARTIFACT_TEMPLATE = {
    "id": "",
    "stage": "",
    "name": "",
    "type": "dataset",
    "format": "",
    "status": "planned",
    "path": "",
    "hash": None,
    "version": "v1",
    "produced_by": "",
    "consumed_by": [],
}

STAGE_ORDER = [
    "stage_1", "stage_1.5", "stage_2", "stage_2.5",
    "stage_3", "stage_3.5", "stage_4"
]

STAGE_PREREQUISITES = {
    "stage_1":      [],  # 入口阶段无需前置
    "stage_1.5":    ["cleaned_data", "cleaning_log", "variable_list", "blinding_review", "db_lock_record"],
    "stage_2":      ["cleaned_data", "gate_stage_1.5"],
    "stage_2.5":    ["sap"],
    "stage_3":      ["cleaned_data", "sap", "gate_stage_2.5"],
    "stage_3.5":    ["analysis_results", "quality_check"],
    "stage_4":      ["analysis_results", "gate_stage_3.5"],
}

MID_ENTRY_ARTIFACTS = {
    "stage_1":      [],
    "stage_2":      ["cleaned_data"],
    "stage_3":      ["cleaned_data", "sap"],
    "stage_4":      ["analysis_results"],
}


class PassportError(Exception):
    """护照操作异常"""
    pass


class PassportManager:
    """Material Passport 管理器"""

    def __init__(self, passport_path: str):
        self.path = passport_path
        self.data = self._load_or_create()

    # ── 核心 CRUD ──

    def get_artifact(self, artifact_id: str) -> Optional[dict]:
        """按 ID 查询产物"""
        for a in self.data.get("artifacts", []):
            if a["id"] == artifact_id:
                return a
        return None

    def add_artifact(self, artifact: dict) -> str:
        """添加新产物记录"""
        if self.get_artifact(artifact["id"]):
            raise PassportError(f"产物 {artifact['id']} 已存在")

        entry = {**DEFAULT_ARTIFACT_TEMPLATE, **artifact}
        entry.setdefault("status", "planned")
        self.data.setdefault("artifacts", []).append(entry)
        self._save()
        return artifact["id"]

    def update_status(self, artifact_id: str, status: str,
                      file_hash: str = None, path: str = None):
        """更新产物状态"""
        a = self.get_artifact(artifact_id)
        if not a:
            raise PassportError(f"产物 {artifact_id} 不存在")

        if status not in ("planned", "in_progress", "completed",
                          "verified", "consumed", "skipped", "error", "rollback"):
            raise PassportError(f"无效状态: {status}")

        a["status"] = status
        if file_hash:
            a["hash"] = file_hash
        if path:
            a["path"] = path
        self.data["updated_at"] = self._now()
        self._save()

    def mark_consumed(self, artifact_id: str, consumer: str):
        """标记产物已被下游消费"""
        a = self.get_artifact(artifact_id)
        if not a:
            raise PassportError(f"产物 {artifact_id} 不存在")
        if consumer not in a.get("consumed_by", []):
            a.setdefault("consumed_by", []).append(consumer)
        a["status"] = "consumed"
        self._save()

    # ── 阶段查询 ──

    def get_stage_artifacts(self, stage: str) -> list[dict]:
        """获取某阶段所有产物"""
        return [a for a in self.data.get("artifacts", [])
                if a["stage"] == stage]

    def get_stage_status(self, stage: str) -> str:
        """计算某阶段完成状态"""
        artifacts = self.get_stage_artifacts(stage)
        if not artifacts:
            return "planned"
        statuses = {a["status"] for a in artifacts}
        if "error" in statuses:
            return "error"
        if all(s in ("completed", "verified", "consumed") for s in statuses):
            return "completed"
        if "in_progress" in statuses:
            return "in_progress"
        return "planned"

    # ── 前置条件验证 ──

    # 阶段 → 对应门闸 stage 映射
    STAGE_GATE_MAP = {
        "stage_2": "stage_1.5",
        "stage_3": "stage_2.5",
        "stage_4": "stage_3.5",
    }

    def verify_prerequisites(self, stage: str) -> tuple:
        """检查进入某阶段所需的前置产物是否齐全
        
        同时验证：
        1. 所有前置 artifact 状态不为 planned/error/rollback
        2. 对应 gate 的 result 不为 blocked（passed 或 conditional 均可）
        
        Returns:
            (ok: bool, missing: list[str])
        """
        required = STAGE_PREREQUISITES.get(stage, [])
        missing = []
        for art_id in required:
            a = self.get_artifact(artifact_id=art_id)
            if not a or a["status"] in ("planned", "error", "rollback"):
                missing.append(art_id)

        # 检查 gate result（如果该阶段有前置 gate）
        gate_stage = self.STAGE_GATE_MAP.get(stage)
        if gate_stage:
            gate_info = self.data.get("gates", {}).get(gate_stage)
            if gate_info:
                gate_status = gate_info.get("status", "")
                if gate_status == "blocked":
                    missing.append(f"gate_{gate_stage}(blocked)")
            else:
                # gate 不存在视为未通过
                missing.append(f"gate_{gate_stage}(not_found)")

        return len(missing) == 0, missing

    def verify_mid_entry(self, stage: str) -> tuple:
        """检查中途切入某阶段所需的最小产物"""
        required = MID_ENTRY_ARTIFACTS.get(stage, [])
        missing = []
        for art_id in required:
            a = self.get_artifact(art_id)
            if not a or a["status"] in ("planned", "error", "rollback"):
                missing.append(art_id)
        return len(missing) == 0, missing

    # ── 恢复 / 回滚 ──

    def get_resume_point(self) -> str:
        """获取可恢复的最近检查点"""
        cp = self.data.get("checkpoints", {}).get("last_completed")
        if not cp:
            return "stage_1"
        # 找到检查点在 STAGE_ORDER 中的下一个
        try:
            idx = STAGE_ORDER.index(cp)
            if idx + 1 < len(STAGE_ORDER):
                return STAGE_ORDER[idx + 1]
            return "completed"  # 所有阶段已完成
        except ValueError:
            return "stage_1"

    def rollback_to(self, target_stage: str) -> list[str]:
        """回退到指定阶段，返回被标记为 rollback 的产物ID列表"""
        rolled = []
        for a in self.data.get("artifacts", []):
            a_stage = a["stage"]
            try:
                a_idx = STAGE_ORDER.index(a_stage)
                target_idx = STAGE_ORDER.index(target_stage)
            except ValueError:
                continue
            if a_idx >= target_idx and a["status"] not in ("planned",):
                a["status"] = "rollback"
                rolled.append(a["id"])

        self.data["checkpoints"]["last_completed"] = (
            STAGE_ORDER[STAGE_ORDER.index(target_stage) - 1]
            if STAGE_ORDER.index(target_stage) > 0 else "stage_1"
        )
        self.data["current_stage"] = target_stage
        self._save()
        return rolled

    def update_checkpoint(self, stage: str):
        """更新完成检查点"""
        self.data.setdefault("checkpoints", {})
        self.data["checkpoints"]["last_completed"] = stage
        self.data["checkpoints"]["last_verified"] = stage
        self.data["current_stage"] = self.get_resume_point()
        self._save()

    # ── 门闸追踪 ──

    def set_gate_result(self, gate_stage: str, status: str,
                        passed: int, total: int):
        """记录质量门闸结果"""
        self.data.setdefault("gates", {})
        self.data["gates"][gate_stage] = {
            "status": status,  # "passed" | "conditional" | "blocked"
            "passed_items": passed,
            "total_items": total,
        }
        self._save()

    # ── 快照 ──

    def create_snapshot(self) -> dict:
        """创建当前护照快照（用于 checkpoint 备份）"""
        return {
            "passport_id": self.data["passport_id"],
            "pipeline_version": self.data["pipeline_version"],
            "created_at": self.data["created_at"],
            "updated_at": self._now(),
            "status": self.data["status"],
            "current_stage": self.data.get("current_stage"),
            "checkpoints": dict(self.data.get("checkpoints", {})),
            "artifacts": [dict(a) for a in self.data.get("artifacts", [])],
        }

    def load_snapshot(self, snapshot: dict):
        """从快照恢复护照"""
        self.data = snapshot
        self._save()

    # ── 版本兼容性 ──

    PASSPORT_SCHEMA_VERSION = "1"

    @classmethod
    def check_version_compatibility(cls, data: dict) -> tuple:
        """检查护照 schema 版本兼容性
        
        Returns:
            (compatible: bool, message: str)
        """
        schema_ver = data.get("passport_schema_version", "0")
        if schema_ver == cls.PASSPORT_SCHEMA_VERSION:
            return True, "版本匹配"
        if schema_ver == "0":
            return True, "旧版护照（无 schema 版本）—— 向前兼容，建议升级"
        return False, f"不兼容的 schema 版本: {schema_ver}，当前支持: {cls.PASSPORT_SCHEMA_VERSION}"

    # ── 哈希计算 ──

    @staticmethod
    def compute_hash(filepath: str, algorithm: str = "sha256") -> str:
        """计算文件哈希"""
        if not os.path.exists(filepath):
            return ""
        h = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return f"{algorithm}:{h.hexdigest()}"

    # ── 内部方法 ──

    def _load_or_create(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                compatible, msg = self.check_version_compatibility(data)
                if not compatible:
                    raise PassportError(f"护照版本不兼容: {msg}")
                # 旧版护照（无 schema 版本）自动补全
                if "passport_schema_version" not in data:
                    data["passport_schema_version"] = self.PASSPORT_SCHEMA_VERSION
                return data
        # 创建默认护照
        return {
            "passport_id": f"msra-{self._now()[:10].replace('-', '')}-001",
            "passport_schema_version": PassportManager.PASSPORT_SCHEMA_VERSION,
            "pipeline_version": "0.7.5",
            "created_at": self._now(),
            "updated_at": self._now(),
            "status": "in_progress",
            "study_type": None,
            "current_stage": "stage_1",
            "artifacts": [],
            "checkpoints": {
                "last_completed": None,
                "last_verified": None,
                "resume_point": "stage_1",
            },
            "gates": {},
        }

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


# ── CLI ──

if __name__ == "__main__":
    import sys

    def usage():
        print("用法:")
        print("  passport.py <passport.json> <命令> [参数]")
        print("命令:")
        print("  status              — 显示当前护照状态")
        print("  add <id> <stage> <name>  — 添加产物")
        print("  update <id> <status>     — 更新产物状态")
        print("  check <stage>            — 检查前置条件")
        print("  resume                   — 显示恢复点")
        print("  rollback <stage>         — 回退到指定阶段")

    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    pm = PassportManager(sys.argv[1])
    cmd = sys.argv[2]

    if cmd == "status":
        d = pm.data
        print(f"护照: {d['passport_id']}")
        print(f"版本: {d['pipeline_version']}")
        print(f"当前阶段: {d.get('current_stage', 'unknown')}")
        print(f"状态: {d['status']}")
        print(f"\n产物 ({len(d.get('artifacts', []))} 个):")
        for a in d.get("artifacts", []):
            print(f"  [{a['status']:>10}] {a['id']} ({a['stage']})")
        print(f"\n门闸:")
        for g, r in d.get("gates", {}).items():
            print(f"  {g}: {r['status']} ({r['passed_items']}/{r['total_items']})")
        print(f"\n检查点: {d.get('checkpoints', {})}")

    elif cmd == "add" and len(sys.argv) >= 5:
        art = {"id": sys.argv[3], "stage": sys.argv[4], "name": sys.argv[5] if len(sys.argv) > 5 else sys.argv[3]}
        pm.add_artifact(art)
        print(f"已添加: {art['id']}")

    elif cmd == "update" and len(sys.argv) >= 5:
        pm.update_status(sys.argv[3], sys.argv[4])
        print(f"已更新: {sys.argv[3]} -> {sys.argv[4]}")

    elif cmd == "check" and len(sys.argv) >= 4:
        ok, missing = pm.verify_prerequisites(sys.argv[3])
        if ok:
            print(f"✅ 前置条件全部满足")
        else:
            print(f"❌ 缺失: {', '.join(missing)}")

    elif cmd == "resume":
        rp = pm.get_resume_point()
        print(f"恢复点: {rp}")

    elif cmd == "rollback" and len(sys.argv) >= 4:
        rolled = pm.rollback_to(sys.argv[3])
        print(f"已回退至 {sys.argv[3]}，{len(rolled)} 个产物标记为 rollback")
        for r in rolled:
            print(f"  ↻ {r}")
