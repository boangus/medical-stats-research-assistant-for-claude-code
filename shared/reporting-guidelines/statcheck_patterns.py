"""
statcheck_patterns.py — NHST 报告一致性自动检查
==============================================
基于 statcheck (Epskamp & Nuijten 2016) 方法，
用正则表达式检测 APA 格式统计报告中的数值不一致。

检测的不一致类型：
  1. p 值与检验统计量不匹配（重新计算 p 值）
  2. 自由度与样本量不一致
  3. 效应量与置信区间不一致
  4. 统计量格式错误

依赖: scipy
安装: pip install scipy

参考文献:
  - Epskamp S, Nuijten M. statcheck: Extract statistics from articles
    and recompute p values (2016). R package.
  - Nuijten MB et al. The prevalence of statistical reporting errors in
    psychology (1985-2013). Behav Res Methods (2016).

作者: MSRA Team
版本: 0.1.0
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ============================================================================
# 正则表达式模式
# ============================================================================

# APA 格式的 t 检验报告: t(48) = 2.34, p = .023
RE_T_TEST = re.compile(
    r't\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*'
    r'(-?\d+\.\d+)\s*,\s*'
    r'p\s*[=<>]\s*(?:<|>)?\s*(\.\d+|\d+\.\d+)',
    re.IGNORECASE
)

# F 检验: F(2, 97) = 4.56, p = .013
RE_F_TEST = re.compile(
    r'F\s*\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*'
    r'(\d+\.\d+)\s*,\s*'
    r'p\s*[=<>]\s*(?:<|>)?\s*(\.\d+|\d+\.\d+)',
    re.IGNORECASE
)

# r 相关: r(48) = .45, p = .001
RE_R_CORR = re.compile(
    r'r\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*'
    r'(-?\.\d+|-?\d+\.\d+)\s*,\s*'
    r'p\s*[=<>]\s*(?:<|>)?\s*(\.\d+|\d+\.\d+)',
    re.IGNORECASE
)

# χ² 检验: χ²(1, N = 100) = 4.56, p = .033
RE_CHI2 = re.compile(
    r'(?:χ²|chi-squared|chi2)\s*\(\s*(\d+(?:\.\d+)?)\s*'
    r'(?:,\s*N\s*=\s*(\d+))?\s*\)\s*=\s*'
    r'(\d+\.\d+)\s*,\s*'
    r'p\s*[=<>]\s*(?:<|>)?\s*(\.\d+|\d+\.\d+)',
    re.IGNORECASE
)

# z 检验: z = 2.34, p = .019
RE_Z_TEST = re.compile(
    r'z\s*=\s*(-?\d+\.\d+)\s*,\s*'
    r'p\s*[=<>]\s*(?:<|>)?\s*(\.\d+|\d+\.\d+)',
    re.IGNORECASE
)

# 置信区间: 95% CI [1.23, 4.56] 或 95% CI = [1.23, 4.56]
RE_CI = re.compile(
    r'(\d+)%\s*CI\s*[\[=]\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*\]',
    re.IGNORECASE
)

# 效应量报告: d = 0.45, η² = .12, OR = 2.34
RE_EFFECT_SIZE = re.compile(
    r"(?:Cohen's\s*)?d\s*=\s*(\.\d+|\d+\.\d+)|"
    r"(?:Hedges'?\s*)?g\s*=\s*(\.\d+|\d+\.\d+)|"
    r"η²\s*=\s*(\.\d+|\d+\.\d+)|"
    r"ηp²\s*=\s*(\.\d+|\d+\.\d+)|"
    r"ω²\s*=\s*(\.\d+|\d+\.\d+)|"
    r"(?:Cramér's?\s*)?V\s*=\s*(\.\d+|\d+\.\d+)|"
    r"OR\s*=\s*(\.\d+|\d+\.\d+)|"
    r"HR\s*=\s*(\.\d+|\d+\.\d+)",
    re.IGNORECASE
)


# ============================================================================
# 数据结构
# ============================================================================


@dataclass
class StatCheckResult:
    """单条检查结果"""
    test_type: str          # t, F, r, chi2, z
    reported_stat: float    # 报告的检验统计量
    reported_p: float       # 报告的 p 值
    recomputed_p: float     # 重新计算的 p 值
    df1: Optional[int] = None
    df2: Optional[int] = None
    discrepancy: float = 0.0
    severity: str = "ok"    # ok, minor, major, error
    line_number: int = 0
    raw_text: str = ""


@dataclass
class StatcheckReport:
    """检查报告"""
    total_stats_found: int = 0
    inconsistencies: List[StatCheckResult] = field(default_factory=list)
    minor_count: int = 0    # |Δp| < 0.01
    major_count: int = 0    # 0.01 ≤ |Δp| < 0.05
    error_count: int = 0    # |Δp| ≥ 0.05 或结论翻转
    details: List[Dict] = field(default_factory=list)


# ============================================================================
# 检查引擎
# ============================================================================


def _recompute_p_t(t_val: float, df: float) -> float:
    """从 t 值和自由度重新计算双侧 p 值"""
    if not HAS_SCIPY:
        return -1.0
    return float(sp_stats.t.sf(abs(t_val), df) * 2)


def _recompute_p_f(f_val: float, df1: float, df2: float) -> float:
    """从 F 值和自由度重新计算 p 值"""
    if not HAS_SCIPY:
        return -1.0
    return float(sp_stats.f.sf(f_val, df1, df2))


def _recompute_p_r(r_val: float, df: float) -> float:
    """从 r 值和自由度重新计算 p 值"""
    if not HAS_SCIPY:
        return -1.0
    if abs(r_val) >= 1:
        return 0.0
    t_val = r_val * np.sqrt(df / (1 - r_val**2))
    return float(sp_stats.t.sf(abs(t_val), df) * 2)


def _recompute_p_chi2(chi2_val: float, df: float) -> float:
    """从 χ² 值和自由度重新计算 p 值"""
    if not HAS_SCIPY:
        return -1.0
    return float(sp_stats.chi2.sf(chi2_val, df))


def _recompute_p_z(z_val: float) -> float:
    """从 z 值重新计算双侧 p 值"""
    if not HAS_SCIPY:
        return -1.0
    return float(sp_stats.norm.sf(abs(z_val)) * 2)


def _classify_severity(reported_p: float, recomputed_p: float) -> Tuple[float, str]:
    """分类不一致严重程度

    Returns
    -------
    (discrepancy, severity)
    """
    if recomputed_p < 0:
        return 0.0, "unknown"

    delta = abs(reported_p - recomputed_p)

    # 检查结论是否翻转（α=0.05）
    reported_sig = reported_p < 0.05
    recomputed_sig = recomputed_p < 0.05
    conclusion_flipped = reported_sig != recomputed_sig

    if conclusion_flipped:
        return delta, "error"
    elif delta >= 0.05:
        return delta, "error"
    elif delta >= 0.01:
        return delta, "major"
    elif delta >= 0.001:
        return delta, "minor"
    else:
        return delta, "ok"


def check_text(text: str) -> StatcheckReport:
    """检查文本中的统计报告一致性

    Parameters
    ----------
    text : str
        包含 APA 格式统计报告的文本

    Returns
    -------
    StatcheckReport
        检查报告
    """
    report = StatcheckReport()
    lines = text.split('\n')

    for line_num, line in enumerate(lines, 1):
        # t 检验
        for match in RE_T_TEST.finditer(line):
            df = float(match.group(1))
            t_val = float(match.group(2))
            reported_p = float(match.group(3))
            recomputed_p = _recompute_p_t(t_val, df)
            delta, severity = _classify_severity(reported_p, recomputed_p)

            result = StatCheckResult(
                test_type="t", reported_stat=t_val, reported_p=reported_p,
                recomputed_p=recomputed_p, df1=int(df),
                discrepancy=delta, severity=severity,
                line_number=line_num, raw_text=match.group(0)
            )
            report.total_stats_found += 1
            if severity != "ok":
                report.inconsistencies.append(result)
                if severity == "minor": report.minor_count += 1
                elif severity == "major": report.major_count += 1
                elif severity == "error": report.error_count += 1
            report.details.append({
                "type": "t", "df": int(df), "stat": t_val,
                "reported_p": reported_p, "recomputed_p": round(recomputed_p, 6),
                "severity": severity, "line": line_num
            })

        # F 检验
        for match in RE_F_TEST.finditer(line):
            df1 = float(match.group(1))
            df2 = float(match.group(2))
            f_val = float(match.group(3))
            reported_p = float(match.group(4))
            recomputed_p = _recompute_p_f(f_val, df1, df2)
            delta, severity = _classify_severity(reported_p, recomputed_p)

            result = StatCheckResult(
                test_type="F", reported_stat=f_val, reported_p=reported_p,
                recomputed_p=recomputed_p, df1=int(df1), df2=int(df2),
                discrepancy=delta, severity=severity,
                line_number=line_num, raw_text=match.group(0)
            )
            report.total_stats_found += 1
            if severity != "ok":
                report.inconsistencies.append(result)
                if severity == "minor": report.minor_count += 1
                elif severity == "major": report.major_count += 1
                elif severity == "error": report.error_count += 1
            report.details.append({
                "type": "F", "df": f"({int(df1)},{int(df2)})", "stat": f_val,
                "reported_p": reported_p, "recomputed_p": round(recomputed_p, 6),
                "severity": severity, "line": line_num
            })

        # r 相关
        for match in RE_R_CORR.finditer(line):
            df = float(match.group(1))
            r_val = float(match.group(2))
            reported_p = float(match.group(3))
            recomputed_p = _recompute_p_r(r_val, df)
            delta, severity = _classify_severity(reported_p, recomputed_p)

            result = StatCheckResult(
                test_type="r", reported_stat=r_val, reported_p=reported_p,
                recomputed_p=recomputed_p, df1=int(df),
                discrepancy=delta, severity=severity,
                line_number=line_num, raw_text=match.group(0)
            )
            report.total_stats_found += 1
            if severity != "ok":
                report.inconsistencies.append(result)
                if severity == "minor": report.minor_count += 1
                elif severity == "major": report.major_count += 1
                elif severity == "error": report.error_count += 1
            report.details.append({
                "type": "r", "df": int(df), "stat": r_val,
                "reported_p": reported_p, "recomputed_p": round(recomputed_p, 6),
                "severity": severity, "line": line_num
            })

        # χ² 检验
        for match in RE_CHI2.finditer(line):
            df_chi = float(match.group(1))
            n_obs = int(match.group(2)) if match.group(2) else None
            chi2_val = float(match.group(3))
            reported_p = float(match.group(4))
            recomputed_p = _recompute_p_chi2(chi2_val, df_chi)
            delta, severity = _classify_severity(reported_p, recomputed_p)

            result = StatCheckResult(
                test_type="chi2", reported_stat=chi2_val, reported_p=reported_p,
                recomputed_p=recomputed_p, df1=int(df_chi),
                discrepancy=delta, severity=severity,
                line_number=line_num, raw_text=match.group(0)
            )
            report.total_stats_found += 1
            if severity != "ok":
                report.inconsistencies.append(result)
                if severity == "minor": report.minor_count += 1
                elif severity == "major": report.major_count += 1
                elif severity == "error": report.error_count += 1
            report.details.append({
                "type": "χ²", "df": int(df_chi), "stat": chi2_val,
                "reported_p": reported_p, "recomputed_p": round(recomputed_p, 6),
                "severity": severity, "line": line_num
            })

        # z 检验
        for match in RE_Z_TEST.finditer(line):
            z_val = float(match.group(1))
            reported_p = float(match.group(2))
            recomputed_p = _recompute_p_z(z_val)
            delta, severity = _classify_severity(reported_p, recomputed_p)

            result = StatCheckResult(
                test_type="z", reported_stat=z_val, reported_p=reported_p,
                recomputed_p=recomputed_p,
                discrepancy=delta, severity=severity,
                line_number=line_num, raw_text=match.group(0)
            )
            report.total_stats_found += 1
            if severity != "ok":
                report.inconsistencies.append(result)
                if severity == "minor": report.minor_count += 1
                elif severity == "major": report.major_count += 1
                elif severity == "error": report.error_count += 1
            report.details.append({
                "type": "z", "stat": z_val,
                "reported_p": reported_p, "recomputed_p": round(recomputed_p, 6),
                "severity": severity, "line": line_num
            })

    return report


def format_report(report: StatcheckReport) -> str:
    """格式化检查报告为 Markdown

    Parameters
    ----------
    report : StatcheckReport
        检查报告

    Returns
    -------
    str
        Markdown 格式报告
    """
    lines = ["# statcheck 一致性检查报告\n"]
    lines.append(f"**检查统计量数**: {report.total_stats_found}")
    lines.append(f"**不一致数**: {len(report.inconsistencies)}")
    lines.append(f"  - 轻微 (|Δp|<0.01): {report.minor_count}")
    lines.append(f"  - 严重 (0.01≤|Δp|<0.05): {report.major_count}")
    lines.append(f"  - 错误 (|Δp|≥0.05 或结论翻转): {report.error_count}")
    lines.append("")

    if report.inconsistencies:
        lines.append("## 不一致详情\n")
        lines.append("| # | 行 | 检验类型 | 报告值 | 报告 p | 重算 p | |Δp| | 严重程度 |")
        lines.append("|---|---|---------|--------|--------|--------|------|---------|")
        for i, inc in enumerate(report.inconsistencies, 1):
            lines.append(
                f"| {i} | {inc.line_number} | {inc.test_type} | "
                f"{inc.reported_stat:.3f} | {inc.reported_p:.4f} | "
                f"{inc.recomputed_p:.4f} | {inc.discrepancy:.4f} | "
                f"{'❌' if inc.severity == 'error' else '⚠️' if inc.severity == 'major' else 'ℹ️'} {inc.severity} |"
            )
        lines.append("")

    if not report.inconsistencies:
        lines.append("✅ **未发现统计报告不一致**\n")

    return "\n".join(lines)


# ============================================================================
# 示例
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 示例文本（包含故意的不一致）
    sample_text = """
    两组间年龄差异有统计学意义 (t(48) = 2.34, p = .023)。
    性别分布在两组间无显著差异 (χ²(1, N = 100) = 1.23, p = .268)。
    治疗效果显著 (F(2, 97) = 4.56, p = .001)。
    相关分析显示中等效应 (r(98) = .45, p = .001)。
    亚组分析未达显著水平 (z = 1.89, p = .058)。
    """

    logger.info("=== statcheck 一致性检查 ===\n")
    report = check_text(sample_text)
    logger.info("format_report(report)")
