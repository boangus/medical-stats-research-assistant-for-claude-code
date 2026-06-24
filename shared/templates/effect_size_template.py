"""
effect_size_template.py — 效应量计算模板（Python）
==================================================
适用于：医学研究中常用效应量的标准化计算

支持的效应量：
  - Cohen's d (两样本 t 检验)
  - Hedges' g (小样本校正)
  - Cohen's f (ANOVA)
  - Eta-squared (η²)
  - Omega-squared (ω²)
  - Cramér's V (分类变量)
  - Rank-biserial r (非参数检验)
  - Odds Ratio / Risk Ratio
  - Hazard Ratio (对数尺度)
  - NNT (Number Needed to Treat)
  - R² / Adjusted R²
  - ICC (组内相关系数)

依赖: numpy, scipy, pandas
安装: pip install numpy scipy pandas

参考文献:
  - Cohen J. Statistical Power Analysis for the Behavioral Sciences (1988)
  - Lakens D. Computing and reporting effect sizes (2013)
  - Fritz CO et al. Reporting effect size (2012)

作者: MSRA Team
版本: 0.1.0
"""

import logging
from typing import Dict

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 连续变量效应量
# ============================================================================


def cohens_d(
    group1: np.ndarray,
    group2: np.ndarray,
    pooled: bool = True,
) -> float:
    """计算 Cohen's d

    Parameters
    ----------
    group1, group2 : array-like
        两组数据
    pooled : bool
        是否使用合并标准差（默认 True）

    Returns
    -------
    float
        Cohen's d 值
    """
    n1, n2 = len(group1), len(group2)
    m1, m2 = np.mean(group1), np.mean(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)

    if pooled:
        sp = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
        return (m1 - m2) / sp if sp > 0 else 0.0
    else:
        return (m1 - m2) / np.sqrt((s1**2 + s2**2) / 2)


def hedges_g(
    group1: np.ndarray,
    group2: np.ndarray,
) -> float:
    """计算 Hedges' g（小样本校正的 Cohen's d）

    Parameters
    ----------
    group1, group2 : array-like
        两组数据

    Returns
    -------
    float
        Hedges' g 值
    """
    d = cohens_d(group1, group2)
    n = len(group1) + len(group2)
    # 小样本校正因子
    correction = 1 - 3 / (4 * n - 9) if n > 9 else 1.0
    return d * correction


def eta_squared(
    groups: list,
) -> float:
    """计算 η² (Eta-squared) — ANOVA 效应量

    Parameters
    ----------
    groups : list of array-like
        多组数据

    Returns
    -------
    float
        η² 值 (0-1)
    """
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)

    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_total = np.sum((all_data - grand_mean) ** 2)

    return ss_between / ss_total if ss_total > 0 else 0.0


def omega_squared(
    groups: list,
) -> float:
    """计算 ω² (Omega-squared) — ANOVA 效应量（无偏估计）

    Parameters
    ----------
    groups : list of array-like
        多组数据

    Returns
    -------
    float
        ω² 值
    """
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)
    k = len(groups)
    n = len(all_data)

    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_within = sum(np.sum((g - np.mean(g)) ** 2) for g in groups)
    ms_within = ss_within / (n - k)

    numerator = ss_between - (k - 1) * ms_within
    denominator = ss_total = ss_between + ss_within + ms_within

    return max(0, numerator / denominator) if denominator > 0 else 0.0


def cohens_f_from_eta2(eta2: float) -> float:
    """从 η² 计算 Cohen's f

    Parameters
    ----------
    eta2 : float
        η² 值

    Returns
    -------
    float
        Cohen's f 值
    """
    return np.sqrt(eta2 / (1 - eta2)) if eta2 < 1 else float('inf')


# ============================================================================
# 2. 分类变量效应量
# ============================================================================


def cramers_v(
    contingency_table: np.ndarray,
) -> float:
    """计算 Cramér's V — 分类变量关联强度

    Parameters
    ----------
    contingency_table : array-like
        列联表 (r × c)

    Returns
    -------
    float
        Cramér's V 值 (0-1)
    """
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = np.sum(contingency_table)
    k = min(contingency_table.shape) - 1

    return np.sqrt(chi2 / (n * k)) if n * k > 0 else 0.0


def risk_ratio(
    a: int, b: int, c: int, d: int,
) -> Dict[str, float]:
    """计算风险比 (Risk Ratio) 及置信区间

    Parameters
    ----------
    a : int
        暴露组事件数
    b : int
        暴露组非事件数
    c : int
        对照组事件数
    d : int
        对照组非事件数

    Returns
    -------
    Dict
        RR 值和 95% CI
    """
    n_exp = a + b
    n_ctrl = c + d
    rr = (a / n_exp) / (c / n_ctrl) if c > 0 and n_exp > 0 else float('inf')

    # 对数尺度标准误
    se = np.sqrt(1 / a - 1 / n_exp + 1 / c - 1 / n_ctrl) if a > 0 and c > 0 else 0
    log_rr = np.log(rr) if rr > 0 else 0

    return {
        "risk_ratio": rr,
        "ci_lower": np.exp(log_rr - 1.96 * se),
        "ci_upper": np.exp(log_rr + 1.96 * se),
        "log_rr": log_rr,
        "se_log_rr": se,
    }


def odds_ratio(
    a: int, b: int, c: int, d: int,
) -> Dict[str, float]:
    """计算比值比 (Odds Ratio) 及置信区间

    Parameters
    ----------
    a, b, c, d : int
        2×2 列联表单元格

    Returns
    -------
    Dict
        OR 值和 95% CI
    """
    or_val = (a * d) / (b * c) if b * c > 0 else float('inf')
    se = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d) if min(a, b, c, d) > 0 else 0
    log_or = np.log(or_val) if or_val > 0 else 0

    return {
        "odds_ratio": or_val,
        "ci_lower": np.exp(log_or - 1.96 * se),
        "ci_upper": np.exp(log_or + 1.96 * se),
        "log_or": log_or,
        "se_log_or": se,
    }


# ============================================================================
# 3. 非参数效应量
# ============================================================================


def rank_biserial_r(
    group1: np.ndarray,
    group2: np.ndarray,
) -> float:
    """计算 rank-biserial r — Mann-Whitney U 的效应量

    公式: r = 1 - (2U) / (n1 × n2)

    Parameters
    ----------
    group1, group2 : array-like
        两组数据

    Returns
    -------
    float
        rank-biserial r 值 (-1 到 1)
    """
    u_stat, _ = stats.mannwhitneyu(group1, group2, alternative='two-sided')
    n1, n2 = len(group1), len(group2)
    return 1 - (2 * u_stat) / (n1 * n2)


def cliffs_delta(
    group1: np.ndarray,
    group2: np.ndarray,
) -> float:
    """计算 Cliff's delta — 非参数效应量

    Parameters
    ----------
    group1, group2 : array-like
        两组数据

    Returns
    -------
    float
        Cliff's delta 值 (-1 到 1)
    """
    n1, n2 = len(group1), len(group2)
    dominance = 0
    for x in group1:
        for y in group2:
            if x > y:
                dominance += 1
            elif x < y:
                dominance -= 1
    return dominance / (n1 * n2)


# ============================================================================
# 4. 效应量解读
# ============================================================================


def interpret_effect_size(
    value: float,
    measure: str,
) -> str:
    """解读效应量大小

    Parameters
    ----------
    value : float
        效应量值
    measure : str
        效应量类型: 'd', 'g', 'eta2', 'f', 'v', 'r', 'or'

    Returns
    -------
    str
        解读: 'negligible', 'small', 'medium', 'large'
    """
    abs_val = abs(value)

    thresholds = {
        'd': (0.2, 0.5, 0.8),
        'g': (0.2, 0.5, 0.8),
        'eta2': (0.01, 0.06, 0.14),
        'f': (0.10, 0.25, 0.40),
        'v': (0.10, 0.30, 0.50),
        'r': (0.10, 0.30, 0.50),
        'or': (1.5, 2.0, 3.0),
    }

    if measure not in thresholds:
        return "unknown"

    small, medium, large = thresholds[measure]

    if measure == 'or':
        if abs_val < small:
            return "negligible"
        elif abs_val < medium:
            return "small"
        elif abs_val < large:
            return "medium"
        else:
            return "large"
    else:
        if abs_val < small:
            return "negligible"
        elif abs_val < medium:
            return "small"
        elif abs_val < large:
            return "medium"
        else:
            return "large"


# ============================================================================
# 5. NNT 计算
# ============================================================================


def nnt_from_risk_diff(
    risk_diff: float,
) -> float:
    """从风险差计算 NNT

    Parameters
    ----------
    risk_diff : float
        绝对风险差 (ARR)

    Returns
    -------
    float
        NNT 值
    """
    if risk_diff == 0:
        return float('inf')
    return abs(1 / risk_diff)


def nnt_from_or(
    or_val: float,
    control_event_rate: float,
) -> float:
    """从 OR 和对照组事件率计算 NNT

    Parameters
    ----------
    or_val : float
        比值比
    control_event_rate : float
        对照组事件率 (CER)

    Returns
    -------
    float
        NNT 值
    """
    cer = control_event_rate
    # OR → ARR
    cer_or = cer * or_val
    arr = cer_or - cer
    if arr == 0:
        return float('inf')
    return abs(1 / arr)


# ============================================================================
# 示例
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    np.random.seed(42)

    # 两样本 t 检验效应量
    g1 = np.random.normal(50, 10, 50)
    g2 = np.random.normal(55, 10, 50)

    d = cohens_d(g1, g2)
    g = hedges_g(g1, g2)
    r = rank_biserial_r(g1, g2)

    logger.info("=== 连续变量效应量 ===")
    logger.info(f"  Cohen's d = {d:.3f} ({interpret_effect_size(d, 'd')})")
    logger.info(f"  Hedges' g = {g:.3f} ({interpret_effect_size(g, 'g')})")
    logger.info(f"  Rank-biserial r = {r:.3f} ({interpret_effect_size(r, 'r')})")

    # ANOVA 效应量
    g3 = np.random.normal(60, 10, 50)
    eta2 = eta_squared([g1, g2, g3])
    omega2 = omega_squared([g1, g2, g3])
    f = cohens_f_from_eta2(eta2)

    logger.info("\n=== ANOVA 效应量 ===")
    logger.info(f"  η² = {eta2:.3f} ({interpret_effect_size(eta2, 'eta2')})")
    logger.info(f"  ω² = {omega2:.3f}")
    logger.info(f"  Cohen's f = {f:.3f} ({interpret_effect_size(f, 'f')})")

    # OR/RR
    or_result = odds_ratio(30, 70, 20, 80)
    rr_result = risk_ratio(30, 70, 20, 80)

    logger.info("\n=== OR/RR ===")
    logger.info(f"  OR = {or_result['odds_ratio']:.3f} (95% CI: {or_result['ci_lower']:.3f}-{or_result['ci_upper']:.3f})")
    logger.info(f"  RR = {rr_result['risk_ratio']:.3f} (95% CI: {rr_result['ci_lower']:.3f}-{rr_result['ci_upper']:.3f})")

    # NNT
    nnt = nnt_from_or(or_result['odds_ratio'], 20 / 100)
    logger.info(f"\n  NNT = {nnt:.1f}")

    logger.info("\n✅ 效应量计算示例完成")
