#!/usr/bin/env python3
"""
generate_msra_handoff_bundle.py — MSRA Handoff Bundle 生成器

生成 Stage 5.0 Paper Intake 所需的 MSRA Handoff Bundle 文件，
将 MSRA 统计分析产物传递给 academic-paper 进行论文写作。

Usage:
    from generate_msra_handoff_bundle import generate_handoff_bundle

    pm = PassportManager("path/to/passport.json")
    bundle_path = generate_handoff_bundle(pm, sap_path="MSRA/SAP.md")
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from shared.passport.passport import PassportManager, PassportError


def _extract_rq_from_sap(sap_path: str) -> str:
    """从 SAP.md 中提取研究问题"""
    if not os.path.exists(sap_path):
        return "[待填写: SAP 文件不存在]"
    with open(sap_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 尝试多种 RQ 标记格式
    for pattern in [
        r"(?:研究问题|研究目的|Research Question|Objectives?)[：:\s]*\n?(.+?)(?:\n\n|\n#|\Z)",
        r"## (?:研究问题|Research Question)\s*\n(.+?)(?:\n##|\Z)",
    ]:
        m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if m:
            rq = m.group(1).strip()
            if rq and len(rq) > 10:
                return rq[:500]  # 截断超长内容
    return "[待填写: 未能从 SAP.md 自动提取研究问题]"


def _find_tables(msra_dir: str) -> list[str]:
    """列出 MSRA 输出中的表格文件"""
    tables_dir = os.path.join(msra_dir, "reports", "tables")
    if not os.path.isdir(tables_dir):
        return []
    tables = []
    for f in sorted(os.listdir(tables_dir)):
        if f.endswith((".docx", ".xlsx", ".csv")):
            tables.append(f"tables/{f}")
    return tables


def _find_figures(msra_dir: str) -> list[str]:
    """列出 MSRA 输出中的图表文件"""
    figures_dir = os.path.join(msra_dir, "reports", "figures")
    if not os.path.isdir(figures_dir):
        return []
    figures = []
    for f in sorted(os.listdir(figures_dir)):
        if f.endswith((".png", ".jpg", ".svg", ".pdf")):
            figures.append(f"figures/{f}")
    return figures


def _extract_methods_summary(sap_path: str, final_report_path: str) -> str:
    """从 SAP + final_report 提取方法学摘要"""
    methods = []
    # 从 SAP 提取统计方法
    if os.path.exists(sap_path):
        with open(sap_path, "r", encoding="utf-8") as f:
            content = f.read()
        for pattern in [
            r"## (?:统计方法|Statistical Methods)\s*\n(.+?)(?:\n##|\Z)",
            r"(?:统计方法|Statistical Methods)[：:\s]*\n?(.+?)(?:\n\n|\Z)",
        ]:
            m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if m:
                methods.append(f"### 统计方法（来自 SAP）\n{m.group(1).strip()[:1000]}")
                break

    # 从 final_report 提取 Phase 5 方法学描述
    if os.path.exists(final_report_path):
        with open(final_report_path, "r", encoding="utf-8") as f:
            content = f.read()
        for pattern in [
            r"## (?:方法学描述|Methodology Description|Phase 5)\s*\n(.+?)(?:\n##|\Z)",
            r"### (?:统计方法|Methodology)\s*\n(.+?)(?:\n###|\Z)",
        ]:
            m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if m:
                methods.append(f"### 方法学描述（来自报告 Phase 5）\n{m.group(1).strip()[:1000]}")
                break

    if methods:
        return "\n\n".join(methods)
    return "[待填写: 未能从 SAP 或报告自动提取方法学描述]"


def _extract_study_type(pm: PassportManager) -> str:
    """从 passport 推导研究类型"""
    study_type = pm.data.get("study_type")
    if study_type:
        return study_type
    # 尝试从 artifacts 推断
    gate_report = pm.get_artifact("gate_stage_3.5")
    if gate_report and gate_report.get("path"):
        path = gate_report["path"]
        if "rct" in path.lower():
            return "RCT"
        if "observ" in path.lower():
            return "观察性研究"
    return "未指定"


def _derive_discipline(study_type: str) -> str:
    """从 study_type 推导学科"""
    mapping = {
        "RCT": "临床医学",
        "临床试验": "临床医学",
        "观察性研究": "临床医学",
        "队列研究": "临床医学",
        "病例对照": "临床医学",
        "诊断试验": "诊断医学",
        "系统综述": "循证医学",
        "Meta分析": "循证医学",
    }
    return mapping.get(study_type, "医学研究")


def _derive_reporting_guideline(study_type: str) -> str:
    """从 study_type 推导报告规范"""
    mapping = {
        "RCT": "CONSORT",
        "临床试验": "CONSORT",
        "观察性研究": "STROBE",
        "队列研究": "STROBE",
        "病例对照": "STROBE",
        "诊断试验": "STARD",
        "系统综述": "PRISMA 2020",
        "Meta分析": "PRISMA 2020",
    }
    return mapping.get(study_type, "CONSORT")


def generate_handoff_bundle(
    pm: PassportManager,
    sap_path: str = None,
    output_dir: str = None,
    project_root: str = None,
) -> str:
    """
    生成 MSRA Handoff Bundle 文件。

    Args:
        pm: 已初始化的 PassportManager（track 必须为 full_paper）
        sap_path: SAP 文件路径（相对于项目根目录，默认 MSRA/SAP.md）
        output_dir: 输出目录（默认 MSRA/）
        project_root: 项目根目录（默认自动检测；测试时传入 tmp_dir）

    Returns:
        生成的 bundle 文件绝对路径

    Raises:
        ValueError: 若 pm.get_track() != "full_paper"
        FileNotFoundError: 若 final_report 产物不存在
    """
    # 守卫检查
    track = pm.get_track()
    if track != "full_paper":
        raise ValueError(
            f"Handoff Bundle 仅在 track='full_paper' 时生成（当前 track={track}）。"
            "请先在 Stage 4 checkpoint 选择 [B] 并调用 pm.set_track('full_paper')."
        )

    # 获取路径
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sap_path is None:
        sap_path = os.path.join(project_root, "MSRA", "SAP.md")
    if output_dir is None:
        output_dir = os.path.join(project_root, "MSRA")

    # 验证 final_report 存在
    final_report_artifact = pm.get_artifact("final_report")
    if not final_report_artifact:
        raise FileNotFoundError("passport 中未找到 final_report 产物")
    final_report_path = os.path.join(project_root, final_report_artifact.get("path", ""))
    if not os.path.exists(final_report_path):
        raise FileNotFoundError(f"final_report 文件不存在: {final_report_path}")

    # 提取字段
    passport_id = pm.data.get("passport_id", "unknown")
    study_type = _extract_study_type(pm)
    discipline = _derive_discipline(study_type)
    reporting_guideline = _derive_reporting_guideline(study_type)
    rq = _extract_rq_from_sap(sap_path)
    methods = _extract_methods_summary(sap_path, final_report_path)
    msra_dir = os.path.join(project_root, "MSRA")
    tables = _find_tables(msra_dir)
    figures = _find_figures(msra_dir)

    # 门闸报告路径
    gate_artifact = pm.get_artifact("gate_stage_3.5")
    gate_path = gate_artifact.get("path", "MSRA/reports/gate_stage_3_5.md") if gate_artifact else "[门闸报告未找到]"

    # 生成 bundle 内容
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    bundle_content = f"""# MSRA Handoff Bundle

## Source
- passport_id: {passport_id}
- study_type: {study_type}
- msra_version: 0.8.0
- track: full_paper
- generated_at: {now}

## Research Question
{rq}

## Results Bundle
### 结果解读
[{final_report_path}]

### Tables
{chr(10).join(f'- {t}' for t in tables) if tables else '[无表格产物]'}

### Figures
{chr(10).join(f'- {f}' for f in figures) if figures else '[无图表产物]'}

## Methods Summary
{methods}

## Quality Gate Report
[{gate_path}]

## Literature Seed
[MSRA Phase 1 文献对比的关键文献 — 由 deep-research 在 Stage 5.1 扩展]

## Journal Template (if selected)
- template: General
- source: shared/journal-templates/

## Paper Configuration (预填)
- Discipline: {discipline}
- Paper Type: IMRaD
- Citation Format: Vancouver
- Body Language: Bilingual
- Existing Materials: Data ✅ | Results ✅ | Tables {'✅' if tables else '❌'} | Figures {'✅' if figures else '❌'}
- Reporting Guideline: {reporting_guideline}

## Bibliography
[EMPTY — 由 Stage 5.1 deep-research 补充；MSRA seed 先行]
"""

    # 写入文件
    os.makedirs(output_dir, exist_ok=True)
    bundle_path = os.path.join(output_dir, "msra_handoff_bundle.md")
    with open(bundle_path, "w", encoding="utf-8") as f:
        f.write(bundle_content)

    return bundle_path


# ── CLI ──

if __name__ == "__main__":
    import sys

    def usage():
        print("用法:")
        print("  generate_msra_handoff_bundle.py <passport.json> [sap_path] [output_dir]")
        print()
        print("示例:")
        print("  python generate_msra_handoff_bundle.py MSRA/passport.json MSRA/SAP.md MSRA/")

    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    passport_path = sys.argv[1]
    sap_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None

    pm = PassportManager(passport_path)
    try:
        path = generate_handoff_bundle(pm, sap_path=sap_path, output_dir=output_dir)
        print(f"✅ Handoff Bundle 已生成: {path}")
    except ValueError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
        sys.exit(1)
