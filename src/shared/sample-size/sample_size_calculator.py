"""
sample_size_calculator.py — 样本量计算模板（Python）
===================================================
适用于：临床试验和观察性研究的样本量/把握度计算

依赖: numpy, scipy, statsmodels
安装: pip install numpy scipy statsmodels

作者: MSRA Team
版本: 0.1.0
"""

import logging
from typing import Dict

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 连续变量（t 检验）
# ============================================================================


def calc_sample_size_t(
    delta: float,
    sd: float,
    alpha: float = 0.05,
    power: float = 0.80,
    ratio: float = 1.0,
    sided: str = "two.sided",
) -> Dict:
    """两独立样本 t 检验的样本量计算

    Parameters
    ----------
    delta : float
        组间均值差
    sd : float
        标准差
    alpha : float
        显著性水平
    power : float
        把握度
    ratio : float
        对照组:试验组比例
    sided : str
        'two.sided' 或 'one.sided'

    Returns
    -------
    Dict
        样本量计算结果
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z_beta = stats.norm.ppf(power)

    d = delta / sd  # Cohen's d
    n_per_group = int(np.ceil(2 * (z_alpha + z_beta)**2 / d**2))
    n1 = n_per_group
    n2 = int(np.ceil(n_per_group * ratio))

    return {
        "n_total": n1 + n2,
        "n1": n1,
        "n2": n2,
        "n_per_group": n_per_group,
        "power": power,
        "delta": delta,
        "sd": sd,
        "d": d,
        "alpha": alpha,
        "method": "Two-sample t-test",
    }


def calc_sample_size_paired_t(
    delta: float,
    sd_diff: float,
    alpha: float = 0.05,
    power: float = 0.80,
    sided: str = "two.sided",
) -> Dict:
    """配对 t 检验的样本量计算"""
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z_beta = stats.norm.ppf(power)
    d = delta / sd_diff

    n = int(np.ceil((z_alpha + z_beta)**2 / d**2))

    return {
        "n": n,
        "power": power,
        "d": d,
        "alpha": alpha,
        "method": "Paired t-test",
    }


# ============================================================================
# 2. 分类变量（率比较）
# ============================================================================


def calc_sample_size_prop(
    p1: float,
    p2: float,
    alpha: float = 0.05,
    power: float = 0.80,
    ratio: float = 1.0,
    sided: str = "two.sided",
) -> Dict:
    """两样本率比较的样本量计算"""
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z_beta = stats.norm.ppf(power)

    # 使用 arcsine 变换
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))

    n_per_group = int(np.ceil((z_alpha + z_beta)**2 * 2 / h**2))
    n1 = n_per_group
    n2 = int(np.ceil(n_per_group * ratio))

    return {
        "n_total": n1 + n2,
        "n1": n1,
        "n2": n2,
        "n_per_group": n_per_group,
        "power": power,
        "p1": p1,
        "p2": p2,
        "h": abs(h),
        "alpha": alpha,
        "method": "Two-sample proportion test",
    }


# ============================================================================
# 3. 方差分析
# ============================================================================


def calc_sample_size_anova(
    k: int,
    f: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> Dict:
    """ANOVA 的样本量计算

    Parameters
    ----------
    k : int
        组数
    f : float
        Cohen's f (小=0.10, 中=0.25, 大=0.40)
    alpha, power : float
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    # 近似公式
    n_per_group = int(np.ceil((z_alpha + z_beta)**2 / (f**2) + k / (2 * f)))

    return {
        "n_per_group": n_per_group,
        "n_total": n_per_group * k,
        "power": power,
        "f": f,
        "alpha": alpha,
        "method": "One-way ANOVA",
    }


# ============================================================================
# 4. 生存分析
# ============================================================================


def calc_sample_size_survival(
    hr: float,
    prop_event: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.80,
    sided: str = "two.sided",
) -> Dict:
    """生存分析的样本量计算（Schoenfeld 公式）"""
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z_beta = stats.norm.ppf(power)

    n_events = int(np.ceil((z_alpha + z_beta)**2 / ((np.log(hr))**2 * prop_event * (1 - prop_event))))
    n_total = int(np.ceil(n_events / prop_event))
    n_per_group = int(np.ceil(n_total / 2))

    return {
        "n_events": n_events,
        "n_total": n_total,
        "n_per_group": n_per_group,
        "hr": hr,
        "prop_event": prop_event,
        "power": power,
        "alpha": alpha,
        "method": "Survival analysis (Schoenfeld)",
    }


# ============================================================================
# 5. 回归分析
# ============================================================================


def calc_sample_size_logistic(
    n_predictors: int,
    prop_events: float,
    epv: int = 10,
) -> Dict:
    """Logistic 回归的样本量计算（EPV 规则）"""
    n_events = n_predictors * epv
    n_total = int(np.ceil(n_events / prop_events))

    return {
        "n_total": n_total,
        "n_events": n_events,
        "n_predictors": n_predictors,
        "epv": epv,
        "prop_events": prop_events,
        "method": "Logistic regression (EPV rule)",
    }


# ============================================================================
# 6. 非劣效性试验
# ============================================================================


def calc_sample_size_noninf(
    delta: float,
    sd: float,
    alpha: float = 0.025,
    power: float = 0.80,
) -> Dict:
    """非劣效性试验的样本量计算（连续变量）"""
    z_alpha = stats.norm.ppf(1 - alpha)
    z_beta = stats.norm.ppf(power)

    n_per_group = int(np.ceil(2 * (z_alpha + z_beta)**2 * sd**2 / delta**2))

    return {
        "n_per_group": n_per_group,
        "n_total": n_per_group * 2,
        "delta": delta,
        "sd": sd,
        "alpha": alpha,
        "power": power,
        "method": "Non-inferiority trial",
    }


# ============================================================================
# 7. 把握度计算（反向）
# ============================================================================


def calc_power_t(
    n: int,
    delta: float,
    sd: float,
    alpha: float = 0.05,
    sided: str = "two.sided",
) -> Dict:
    """已知样本量反向计算把握度（t 检验）"""
    d = delta / sd
    ncp = d * np.sqrt(n / 2)  # 非中心参数
    df = 2 * n - 2

    if sided == "two.sided":
        t_crit = stats.t.ppf(1 - alpha / 2, df)
        power = 1 - stats.nct.cdf(t_crit, df, ncp) + stats.nct.cdf(-t_crit, df, ncp)
    else:
        t_crit = stats.t.ppf(1 - alpha, df)
        power = 1 - stats.nct.cdf(t_crit, df, ncp)

    return {
        "power": power,
        "n": n,
        "d": d,
        "alpha": alpha,
        "method": "Power calculation (t-test)",
    }


# ============================================================================
# 7. 诊断试验样本量
# ============================================================================


def calc_sample_size_diagnostic(
    sensitivity: float,
    specificity: float,
    prevalence: float,
    ci_width: float = 0.10,
    alpha: float = 0.05,
) -> Dict[str, int]:
    """诊断试验样本量计算

    基于灵敏度/特异度的置信区间宽度反推所需病例数。
    公式: n = Z²α/2 × p(1-p) / (d/2)²
    其中 p 为目标指标值，d 为期望的 CI 宽度。

    Parameters
    ----------
    sensitivity : float
        预期灵敏度 (0-1)
    specificity : float
        预期特异度 (0-1)
    prevalence : float
        目标人群中阳性比例 (0-1)
    ci_width : float
        期望的 95% CI 宽度 (默认 0.10)
    alpha : float
        显著性水平 (默认 0.05)

    Returns
    -------
    Dict
        所需阳性病例数、阴性病例数和总病例数
    """
    z = stats.norm.ppf(1 - alpha / 2)

    # 灵敏度所需的阳性病例数
    n_pos = int(np.ceil((z**2 * sensitivity * (1 - sensitivity)) / (ci_width / 2) ** 2))

    # 特异度所需的阴性病例数
    n_neg = int(np.ceil((z**2 * specificity * (1 - specificity)) / (ci_width / 2) ** 2))

    # 考虑患病率后的总样本量
    n_total_sens = int(np.ceil(n_pos / prevalence))
    n_total_spec = int(np.ceil(n_neg / (1 - prevalence)))
    n_total = max(n_total_sens, n_total_spec)

    return {
        "n_positive": n_pos,
        "n_negative": n_neg,
        "n_total": n_total,
        "alpha": alpha,
        "ci_width": ci_width,
        "method": "Diagnostic test sample size (CI width)",
    }


# ============================================================================
# 示例
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger.info("=== 两样本 t 检验 ===")
    res = calc_sample_size_t(delta=5, sd=10)
    logger.info(f"  n_per_group = {res['n_per_group']}, n_total = {res['n_total']}")

    logger.info("\n=== 率比较 ===")
    res = calc_sample_size_prop(p1=0.3, p2=0.5)
    logger.info(f"  n_per_group = {res['n_per_group']}, n_total = {res['n_total']}")

    logger.info("\n=== 生存分析 ===")
    res = calc_sample_size_survival(hr=0.7)
    logger.info(f"  n_events = {res['n_events']}, n_total = {res['n_total']}")

    logger.info("\n=== Logistic 回归 (EPV=10) ===")
    res = calc_sample_size_logistic(n_predictors=5, prop_events=0.3)
    logger.info(f"  n_total = {res['n_total']}")

    logger.info("\n=== 效应量参考 ===")
    logger.info("Cohen's d: 小=0.2, 中=0.5, 大=0.8")
    logger.info("Cohen's f: 小=0.10, 中=0.25, 大=0.40")
    logger.info("OR/HR:     小=1.5, 中=2.0, 大=3.0")

    logger.info("\n✅ 样本量计算示例完成")
