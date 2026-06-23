#!/usr/bin/env python3
"""
generate_msra_handoff_bundle.py ?MSRA Handoff Bundle 生成?

生成 Stage 5.0 Paper Intake 所需?MSRA Handoff Bundle 文件?
?MSRA 统计分析产物传递给 medical-paper 进行论文写作?

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
        return "[待填] SAP 文件不存在"
    with open(sap_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 尝试多种 RQ 标记格式
    for pattern in [
        r"(?:研究问题|研究目的|Research Question|Objectives?)[?\s]*\n?(.+?)(?:\n\n|\n#|\Z)",
        r"## (?:研究问题|Research Question)\s*\n(.+?)(?:\n##|\Z)",
    ]:
        m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if m:
            rq = m.group(1).strip()
            if rq and len(rq) > 10:
                return rq[:500]  # 截断超长内容
    return "[待填? 未能?SAP.md 自动提取研究问题]"


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
    # ?SAP 提取统计方法
    if os.path.exists(sap_path):
        with open(sap_path, "r", encoding="utf-8") as f:
            content = f.read()
        for pattern in [
            r"## (?:统计方法|Statistical Methods)\s*\n(.+?)(?:\n##|\Z)",
            r"(?:统计方法|Statistical Methods)[?\s]*\n?(.+?)(?:\n\n|\Z)",
        ]:
            m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if m:
                methods.append(f"### 统计方法（来?SAP）\n{m.group(1).strip()[:1000]}")
                break

    # ?final_report 提取 Phase 5 方法学描?
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
    return "[待填] 未能从 SAP 或报告自动提取方法学描述"


def _extract_key_findings(final_report_path: str) -> str:
    """从 final_report 中提取核心发现（用于 Introduction/Discussion）"""
    if not os.path.exists(final_report_path):
        return "[待填] final_report 不存在"
    with open(final_report_path, "r", encoding="utf-8") as f:
        content = f.read()

    findings = []
    # 提取显著性结果：p < 0.05 的行
    for line in content.split("\n"):
        if re.search(r"p\s*[<≤]\s*0\.05", line, re.IGNORECASE) and len(line.strip()) > 15:
            findings.append(line.strip().strip("- *").strip())
    # 提取效应量相关行
    for line in content.split("\n"):
        if re.search(r"(?:Cohen|效应量|effect size|OR|HR|RR|d\s*=\s*\d)", line, re.IGNORECASE):
            cleaned = line.strip().strip("- *").strip()
            if cleaned and cleaned not in findings:
                findings.append(cleaned)

    if findings:
        # 去重并取?8 ?
        seen = set()
        unique = []
        for f in findings:
            key = f[:60]
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return "\n".join(f"- {f}" for f in unique[:8])
    return "[待填] 未能自动提取核心发现"


def _extract_safety_findings(final_report_path: str) -> str:
    """从 final_report 中提取安全性分析结果"""
    if not os.path.exists(final_report_path):
        return "[无安全性数据]"
    with open(final_report_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 查找安全性相关段?
    for pattern in [
        r"## (?:安全性|Safety|Adverse Events)\s*\n(.+?)(?:\n##|\Z)",
        r"### (?:安全性|Safety)\s*\n(.+?)(?:\n###|\Z)",
    ]:
        m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if m:
            text = m.group(1).strip()[:800]
            if len(text) > 20:
                return text
    return "[无安全性数据]"


def _extract_limitations(final_report_path: str) -> str:
    """从 final_report 中提取局限性讨论"""
    if not os.path.exists(final_report_path):
        return "[待填] final_report 不存在"
    with open(final_report_path, "r", encoding="utf-8") as f:
        content = f.read()

    for pattern in [
        r"## (?:局限性|Limitations?)\s*\n(.+?)(?:\n##|\Z)",
        r"### (?:局限性|Limitations?)\s*\n(.+?)(?:\n###|\Z)",
        r"(?:局限性|Limitations?)[?\s]*\n?(.+?)(?:\n\n|\Z)",
    ]:
        m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if m:
            text = m.group(1).strip()[:800]
            if len(text) > 20:
                return text
    return "[待填] 未能自动提取局限性讨论"


def _extract_methods_for_paper(sap_path: str, final_report_path: str) -> str:
    """提取论文 Methods 段落可直接引用的结构化文段"""
    methods_blocks = []

    # 从 SAP 提取（更权威）
    if os.path.exists(sap_path):
        with open(sap_path, "r", encoding="utf-8") as f:
            sap_content = f.read()
        # 提取统计方法
        for pattern in [
            r"## (?:统计方法|Statistical Methods)\s*\n(.+?)(?:\n##|\Z)",
            r"### (?:主分析|Primary Analysis)\s*\n(.+?)(?:\n###|\Z)",
        ]:
            m = re.search(pattern, sap_content, re.DOTALL | re.IGNORECASE)
            if m:
                methods_blocks.append(f"**主分析方?*:\n{m.group(1).strip()[:600]}")
                break
        # 提取样本?
        for pattern in [
            r"(?:样本量|Sample Size)[?\s]*\n?(.+?)(?:\n\n|\n#|\Z)",
        ]:
            m = re.search(pattern, sap_content, re.DOTALL | re.IGNORECASE)
            if m:
                methods_blocks.append(f"**样本量计?*:\n{m.group(1).strip()[:300]}")
                break

    # ?final_report 补充敏感性分?
    if os.path.exists(final_report_path):
        with open(final_report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        for pattern in [
            r"## (?:敏感性|Sensitivity Analysis)\s*\n(.+?)(?:\n##|\Z)",
            r"### (?:敏感性|Sensitivity)\s*\n(.+?)(?:\n###|\Z)",
        ]:
            m = re.search(pattern, report_content, re.DOTALL | re.IGNORECASE)
            if m:
                methods_blocks.append(f"**敏感性分?*:\n{m.group(1).strip()[:400]}")
                break

    if methods_blocks:
        return "\n\n".join(methods_blocks)
    return "[待填] 未能提取论文 Methods 文本"


def _extract_rq_consistency(sap_path: str, final_report_path: str) -> str:
    """比较 SAP 与 final_report 中的研究问题（RQ）一致性。

    用于论文 Introduction 中 RQ 与 SAP 中 RQ 一致性校验，
    输出一致性报告（一致/不一致/差异说明）。
    """
    # 从 SAP 提取 RQ（复用已有函数）
    sap_rq = _extract_rq_from_sap(sap_path)

    # ?final_report 提取 RQ
    report_rq = "[待填] final_report 不存在"
    if os.path.exists(final_report_path):
        with open(final_report_path, "r", encoding="utf-8") as f:
            content = f.read()
        for pattern in [
            r"(?:研究问题|研究目的|Research Question|Objectives?)[?\s]*\n?(.+?)(?:\n\n|\n#|\Z)",
            r"## (?:研究问题|Research Question|研究目的|Objectives?)\s*\n(.+?)(?:\n##|\Z)",
        ]:
            m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if m:
                rq = m.group(1).strip()
                if rq and len(rq) > 10:
                    report_rq = rq[:500]
                    break
        else:
            report_rq = "[待填? 未能?final_report 自动提取研究问题]"

    # 归一化文本以便比较：去除空白与标点，统一小写
    def _normalize(text: str) -> str:
        return re.sub(
            r"[\s\u3000.,;:!?，。；：！？、\"'“”‘?)（）\[\]【】]+",
            "",
            text,
        ).lower()

    sap_norm = _normalize(sap_rq)
    report_norm = _normalize(report_rq)

    # 判断一致?
    if sap_norm and report_norm and "[待填" not in sap_rq and "[待填" not in report_rq:
        if sap_norm == report_norm:
            status = "一致"
            diff_note = "SAP 与 final_report 中的研究问题完全一致"
        elif sap_norm in report_norm or report_norm in sap_norm:
            status = "⚠️ 基本一致（存在表述差异）"
            diff_note = "一方为另一方的子集，核心研究问题一致但表述详略不同"
        else:
            status = "❌ 不一致"
            diff_note = "SAP 与 final_report 中的研究问题存在实质性差异，请人工核查"
    else:
        status = "⚠️ 无法自动判定"
        diff_note = "未能从 SAP 与 final_report 中完整提取研究问题，需人工核对"

    report = (
        f"**一致性状?*: {status}\n\n"
        f"**SAP 中的研究问题**:\n{sap_rq}\n\n"
        f"**final_report 中的研究问题**:\n{report_rq}\n\n"
        f"**差异说明**:\n{diff_note}"
    )
    return report


def _extract_results_to_claims_mapping(final_report_path: str) -> str:
    """从 final_report 提取主要统计结果并生成 Claim 映射。

    为每个统计结果（效应量、p值、CI）生成一个 Claim ID（如 CLAIM-001），
    输出结果到论文 Claim 的映射表（Markdown 表格格式），
    用于建立统计结果与论文 Claim 的双向追溯链。
    """
    if not os.path.exists(final_report_path):
        return "[待填] final_report 不存在"

    with open(final_report_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 识别包含统计结果的行：效应量 / p值 / CI
    result_patterns = [
        r"(?:OR|HR|RR|IRR)\s*=?\s*\d+\.?\d*",
        r"(?:Cohen'?s?\s*d|Hedges'?\s*g)\s*=?\s*[-+]?\d+\.?\d*",
        r"(?:β|beta|B)\s*=?\s*[-+]?\d+\.?\d*",
        r"p\s*[<=]\s*0\.\d+",
        r"(?:95%?\s*CI|confidence interval)\s*[:\(]?\s*\d+\.?\d*\s*[-–to]+\s*\d+\.?\d*",
        r"(?:MD|mean diff|差值)\s*=?\s*[-+]?\d+\.?\d*",
    ]

    # 提取关键统计量的正则（用于表格展示）
    key_stat_regex = re.compile(
        r"((?:OR|HR|RR|IRR|Cohen'?s?\s*d|Hedges'?\s*g|MD|β|beta|B)\s*=?\s*[-+]?\d+\.?\d*"
        r"|p\s*[<=]\s*0\.\d+"
        r"|(?:95%?\s*CI|confidence interval)\s*[:\(]?\s*\d+\.?\d*\s*[-–to]+\s*\d+\.?\d*)",
        re.IGNORECASE,
    )

    claims = []
    claim_counter = 0
    seen = set()

    for line in content.split("\n"):
        line_stripped = line.strip()
        if len(line_stripped) < 10:
            continue
        for pattern in result_patterns:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                # 基于前60字符去重
                key = line_stripped[:60]
                if key not in seen:
                    seen.add(key)
                    claim_counter += 1
                    claim_id = f"CLAIM-{claim_counter:03d}"
                    stat_match = key_stat_regex.search(line_stripped)
                    key_stat = stat_match.group(1).strip() if stat_match else "-"
                    claims.append(
                        {
                            "id": claim_id,
                            "result_text": line_stripped[:200],
                            "key_statistic": key_stat,
                        }
                    )
                break  # 一行只生成一个 claim

    if not claims:
        return "[待填] 未能从 final_report 自动提取统计结果"

    # 生成 Markdown 表格
    header = "| Claim ID | 关键统计量 | 结果描述（来源行） | 论文对应章节建议 |\n"
    separator = "|----------|-----------|-------------------|------------------|\n"
    rows = ""
    for c in claims:
        stat = c["key_statistic"].lower()
        if stat.startswith("p") or "ci" in stat:
            section = "Results"
        elif any(k in stat for k in ["or", "hr", "rr", "β", "beta", "d"]):
            section = "Results / Abstract"
        else:
            section = "Results"
        # 转义管道符避免破坏表格
        result_text = c["result_text"].replace("|", "\\|")
        rows += f"| {c['id']} | {c['key_statistic']} | {result_text} | {section} |\n"

    mapping_table = header + separator + rows

    report = (
        f"共识别 {len(claims)} 个可追溯的统计结果-Claim。\n\n"
        f"{mapping_table}\n"
        f"**使用说明**:\n"
        f"- 每个 CLAIM-NNN 对应 final_report 中的一条统计结果\n"
        f"- 论文写作时，在 Results 段落引用对应 Claim ID 以建立双向追溯链\n"
        f"- 论文定稿后，可通过 Claim ID 反查 final_report 中的原始统计输出\n"
    )
    return report


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
    return "未指明"


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
    生成 MSRA Handoff Bundle 文件?

    Args:
        pm: 已初始化?PassportManager（track 必须?full_paper?
        sap_path: SAP 文件路径（相对于项目根目录，默认 MSRA/SAP.md?
        output_dir: 输出目录（默?MSRA/?
        project_root: 项目根目录（默认自动检测；测试时传?tmp_dir?

    Returns:
        生成?bundle 文件绝对路径

    Raises:
        ValueError: ?pm.get_track() != "full_paper"
        FileNotFoundError: ?final_report 产物不存?
    """
    # 守卫检?
    track = pm.get_track()
    if track != "full_paper":
        raise ValueError(
            f"Handoff Bundle 仅在 track='full_paper' 时生成（当前 track={track}）。\n"
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
    data_exists = os.path.exists(sap_path)
    results_exists = bool(final_report_artifact)
    tables = _find_tables(msra_dir)
    figures = _find_figures(msra_dir)

    # 论文素材提取（Optimization #4: Enhanced Handoff）
    key_findings = _extract_key_findings(final_report_path)
    safety_findings = _extract_safety_findings(final_report_path)
    limitations = _extract_limitations(final_report_path)
    methods_for_paper = _extract_methods_for_paper(sap_path, final_report_path)

    # Sprint D: MSRA-MSRA 融合点强化（RQ 一致性 + 结果-Claim 映射）
    rq_consistency = _extract_rq_consistency(sap_path, final_report_path)
    results_to_claims_mapping = _extract_results_to_claims_mapping(final_report_path)

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

## Key Findings (for Introduction/Discussion)
{key_findings}

## Safety Findings (for Discussion)
{safety_findings}

## Limitations (for Discussion)
{limitations}

## Methods (Paper-Ready Format)
{methods_for_paper}

## RQ Consistency Check (SAP vs Report)
{rq_consistency}

## Results to Claims Mapping (for Paper Traceability)
{results_to_claims_mapping}

## Quality Gate Report
[{gate_path}]

## Literature Seed
[MSRA Phase 1 文献对比的关键文献，systematic-survey 在 Stage 5.1 扩展]

## Journal Template (if selected)
- template: General
- source: shared/journal-templates/

## Paper Configuration (预填)
- Discipline: {discipline}
- Paper Type: IMRaD
- Citation Format: Vancouver
- Body Language: Bilingual
- Existing Materials: Data {'✓' if data_exists else '✗'} | Results {'✓' if results_exists else '✗'} | Tables {'✓' if tables else '✗'} | Figures {'✓' if figures else '✗'}
- Reporting Guideline: {reporting_guideline}

## Bibliography
[EMPTY — Stage 5.1 systematic-survey 补充；MSRA seed 先行]
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
        print(f"?Handoff Bundle 已生? {path}")
    except ValueError as e:
        print(f"?错误: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"?文件未找? {e}")
        sys.exit(1)
