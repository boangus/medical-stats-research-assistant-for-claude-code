# MSRA Material Passport

> 跨阶段产物追踪与可恢复性框架。借鉴 ARS v3.9.4.2 Material Passport 模式。
> 版本: 0.1.0 | 2026-05-29

---

## 设计目标

1. **追踪**：Pipeline 各阶段产物的完整生命周期（planned → in_progress → completed → verified → consumed）
2. **恢复**：从中途中断处继续，无需重跑已完成阶段
3. **验证**：进入下一阶段前确认所有前置产物存在且有效
4. **回滚**：标记失效产物，支持回退到指定检查点

---

## Passport JSON 结构

### 完整护照文件 (MSRA/passport.json)

```json
{
  "passport_id": "msra-20260529-001",
  "passport_schema_version": "1",     # 加：schema 版本，变更时递增
  "pipeline_version": "0.4.1",
  "created_at": "2026-05-29T21:00:00+08:00",
  "updated_at": "2026-05-29T21:30:00+08:00",
  "status": "in_progress",
  "study_type": "RCT",
  "current_stage": "stage_2",
  "artifacts": [
    { "id": "raw_data", "stage": "stage_1", "name": "原始数据", 
      "type": "dataset", "format": "csv",
      "status": "consumed", "path": "data/raw/raw_data.csv",
      "hash": "sha256:a1b2c3...", "version": "v1",
      "produced_by": "user", "consumed_by": ["stage_1"] },
    { "id": "cleaned_data", "stage": "stage_1", "name": "清洗后数据",
      "type": "dataset", "format": "csv",
      "status": "completed", "path": "data/cleaned/cleaned_data_v1.csv",
      "hash": "sha256:d4e5f6...", "version": "v1",
      "produced_by": "data_validator", "consumed_by": ["stage_2", "stage_3"] },
    { "id": "cleaning_log", "stage": "stage_1", "name": "清洗日志",
      "type": "report", "format": "md",
      "status": "completed", "path": "reports/cleaning_log_v1.md",
      "hash": "sha256:g7h8i9...", "version": "v1",
      "produced_by": "data_validator", "consumed_by": ["stage_1.5"] },
    { "id": "gate_stage_1.5", "stage": "stage_1.5", "name": "数据质量门闸报告",
      "type": "gate_report", "format": "md",
      "status": "completed", "path": "reports/gate_stage_1_5.md",
      "hash": "sha256:j0k1l2...", "version": "v1",
      "produced_by": "qc_inspector", "consumed_by": ["stage_2"] },
    { "id": "sap", "stage": "stage_2", "name": "统计分析计划",
      "type": "plan", "format": "md",
      "status": "in_progress", "path": "reports/SAP_v1.md",
      "hash": null, "version": "v1",
      "produced_by": "method_consultant", "consumed_by": ["stage_2.5", "stage_3"] }
  ],
  "checkpoints": {
    "last_completed": "stage_1.5",
    "last_verified": "stage_1.5",
    "resume_point": "stage_2"
  },
  "gates": {
    "stage_1.5": { "status": "passed", "passed_items": 7, "total_items": 7 },
    "stage_2.5": { "status": "pending", "passed_items": 0, "total_items": 7 },
    "stage_3.5": { "status": "pending", "passed_items": 0, "total_items": 7 }
  }
}
```

### 产物状态机

```
        失败/回退
        ┌─────────┐
        ▼         │
planned → in_progress → completed → verified → consumed
          │            │              │
          ▼            ▼              ▼
        error        skipped       rollback
```

| 状态 | 含义 |
|------|------|
| `planned` | 已计划但尚未开始生成 |
| `in_progress` | 正在生成中 |
| `completed` | 已生成，可通过 hash 校验 |
| `verified` | 已通过质量门闸验证 |
| `consumed` | 已被下游阶段使用 |
| `skipped` | 用户选择跳过 |
| `error` | 生成失败 |
| `rollback` | 因回退而失效 |

---

## 数据层实现

### PassportManager 类 (`shared/passport/passport.py`)

```python
class PassportManager:
    """Material Passport 管理器"""
    
    def __init__(self, passport_path: str):
        self.path = passport_path
        self.data = self._load_or_create()
    
    def get_artifact(self, artifact_id: str) -> dict | None
    def add_artifact(self, artifact: dict) -> str
    def update_status(self, artifact_id: str, status: str, hash: str = None)
    def mark_consumed(self, artifact_id: str, consumer: str)
    def get_stage_artifacts(self, stage: str) -> list[dict]
    def verify_prerequisites(self, stage: str) -> tuple[bool, list[str]]
    def get_resume_point(self) -> str
    def rollback_to(self, stage: str) -> list[str]
    def create_snapshot(self) -> dict
    def load_snapshot(self, snapshot: dict)
    
    def _load_or_create(self) -> dict
    def _save(self)
    def _compute_hash(self, filepath: str) -> str
```

### 集成方式

Pipeline 在以下时机调用 Passport：

```
/msra 开始 → 创建 passport → status: in_progress
  │
  ▼
Stage 1 开始 → add_artifact(cleaned_data, planned)
Stage 1 完成 → update_status(cleaned_data, completed, hash)
  │
  ▼
Stage 1.5 通过 → update_status(gate_stage_1.5, completed)
               → mark_consumed(cleaned_data, stage_2)
               → update checkpoints.last_completed
  │
  ▼
/msra --status → 读取 passport 展示当前进度
/msra --resume → 读取 passport.get_resume_point()
回退 Stage 1 → rollback_to(stage_1)
               → 标记 stage_1 以后所有产物为 rollback
```

---

## Pipeline 集成

### 前置检查增强

Pipeline 现有的 Mid-Entry 前置检查改由 Passport 驱动：

```python
def check_entry(stage: str, passport: PassportManager) -> bool:
    """检查进入 stage 的所有前置条件"""
    ok, missing = passport.verify_prerequisites(stage)
    if not ok:
        for m in missing:
            print(f"  ❌ 缺失: {m}")
        print(f"  回退到最近的检查点")
    return ok
```

### 恢复流程

```python
def resume(passport_path: str) -> str:
    pm = PassportManager(passport_path)
    resume_point = pm.get_resume_point()
    print(f"从 {resume_point} 恢复")
    return resume_point
```

---

## 文件位置

| 文件 | 路径 |
|------|------|
| Passport 运行时文件 | `{project_root}/.msra/passport.json` |
| 设计文档（本文件） | `shared/passport/passport_schema.md` |
| Python 实现 | `shared/passport/passport.py` |
| Pipeline 集成 | `skills/pipeline/SKILL.md` (更新 §5 产物追踪) |



