"""
adaptive_interim_analysis_template.py — 适应性设计与期中分析模板
================================================================
适用于：临床试验中的成组序贯设计（Group Sequential Design）、期中分析、
       样本量重新估计（Sample Size Re-estimation）、适应性随机化
       （Adaptive Randomization）、多重性校正（Multiplicity Correction）

本模板提供以下功能模块：
  1. 成组序贯设计：O'Brien-Fleming 边界、Pocock 边界、Lan-DeMets α 消耗函数
  2. 期中分析样本量重新估计：盲态观察效应量重新估计、条件把握度重新估计
  3. 适应性随机化：响应自适应随机化（Randomized Play-the-Winner）、最小化随机化
  4. 期中分析决策规则：优效性停止、无效性停止、继续试验
  5. 多重性校正：α 消耗函数、封闭检验程序
  6. 报告生成：期中分析报告（Markdown 格式）、决策建议
  7. 可视化：停止边界图、条件把握度曲线

依赖: scipy, numpy, pandas, matplotlib, statsmodels
安装: pip install scipy numpy pandas matplotlib statsmodels

作者: MSRA Team
版本: 0.1.0
"""

import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import brentq

logger = logging.getLogger(__name__)

# matplotlib 延迟导入（在绘图函数内部导入），以便模块在缺少 matplotlib 时
# 仍可加载统计计算功能。

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. 成组序贯设计（Group Sequential Design）
# ============================================================================
#
# 成组序贯设计允许在预先设定的信息比例处进行多次期中分析，通过 α 消耗函数
# 控制总 I 类错误率。检验统计量 Z_1, Z_2, ..., Z_K 服从多元正态分布：
#   - E[Z_k] = 0（H0 下），E[Z_k] = μ·√(t_k)（H1 下）
#   - Var(Z_k) = 1
#   - Corr(Z_j, Z_k) = √(t_j / t_k)，j ≤ k
#
# 边界通过递归数值积分求解，使得累积越界概率等于 α 消耗函数值。


def alpha_spending_function(
    t: Union[float, np.ndarray],
    alpha: float,
    spending_type: str = "of",
) -> Union[float, np.ndarray]:
    """Lan-DeMets α 消耗函数

    根据信息比例 t 计算累积消耗的 α 值。

    Parameters
    ----------
    t : float 或 np.ndarray
        信息比例（0 到 1 之间），t = I_k / I_K
    alpha : float
        总 I 类错误率（单侧）
    spending_type : str
        消耗函数类型：
        - "of"：O'Brien-Fleming 型，早期消耗极少 α，最终边界接近固定设计
        - "pocock"：Pocock 型，各期中分析消耗均匀，边界恒定
        - "rho_family"：ρ 族（ρ=3 近似 OF，ρ=1 近似 Pocock）

    Returns
    -------
    float 或 np.ndarray
        累积 α 消耗值

    Examples
    --------
    >>> alpha_spending_function(0.5, 0.025, "of")
    0.0028...
    >>> alpha_spending_function(1.0, 0.025, "of")
    0.025
    """
    spending_type = spending_type.lower()
    t = np.asarray(t, dtype=float)

    if spending_type == "of":
        # O'Brien-Fleming 型: α(t) = 2 - 2Φ(Z_{α/2} / √t)
        z_alpha2 = stats.norm.ppf(1 - alpha / 2)
        return 2.0 * (1.0 - stats.norm.cdf(z_alpha2 / np.sqrt(t)))
    elif spending_type == "pocock":
        # Pocock 型: α(t) = α · ln(1 + (e-1)·t)
        return alpha * np.log(1.0 + (np.e - 1.0) * t)
    elif spending_type in ("rho_family", "rho"):
        # ρ 族: α(t) = α · t^ρ（默认 ρ=3，近似 OF）
        return alpha * t ** 3
    else:
        raise ValueError(
            f"不支持的消耗函数类型: {spending_type}，"
            f"可选: 'of', 'pocock', 'rho_family'"
        )


def _prob_no_cross(
    boundaries: np.ndarray,
    info_rates: np.ndarray,
    grid_size: int = 200,
    grid_range: float = 8.0,
) -> float:
    """计算 P(Z_1 ≤ c_1, ..., Z_K ≤ c_K)（未越界概率）

    使用递归数值积分求解多元正态分布的累积概率。
    内部函数，不对外暴露。

    Parameters
    ----------
    boundaries : np.ndarray
        上侧边界 c_1, ..., c_K
    info_rates : np.ndarray
        信息比例 t_1, ..., t_K
    grid_size : int
        数值积分网格点数
    grid_range : float
        网格范围（±grid_range）

    Returns
    -------
    float
        未越界概率
    """
    k_max = len(boundaries)
    grid = np.linspace(-grid_range, grid_range, grid_size)
    dz = grid[1] - grid[0]

    # 第 1 次分析的密度：f_1(z) = φ(z)，在 c_1 处截断
    density = stats.norm.pdf(grid)
    density[grid > boundaries[0]] = 0.0

    if k_max == 1:
        return float(np.trapz(density, grid))

    # 递归计算第 2 到 K 次分析的密度
    for k in range(1, k_max):
        t_prev = info_rates[k - 1]
        t_curr = info_rates[k]
        rho = np.sqrt(t_prev / t_curr)
        sigma_cond = np.sqrt(1.0 - t_prev / t_curr)

        # 向量化计算: f_k(z_i) = ∫ f_{k-1}(x_j) · φ((z_i - x_j·ρ)/σ_cond) / σ_cond dx
        diff = grid[:, None] - grid[None, :] * rho  # (grid_size, grid_size)
        cond_pdf = stats.norm.pdf(diff / sigma_cond) / sigma_cond
        new_density = np.trapz(density[None, :] * cond_pdf, grid, axis=1)

        # 在 c_k 处截断
        new_density[grid > boundaries[k]] = 0.0
        density = new_density

    return float(np.trapz(density, grid))


def _prob_no_cross_drift(
    boundaries: np.ndarray,
    info_rates: np.ndarray,
    drift: float,
    **kwargs: Any,
) -> float:
    """计算 H1 下 P(Z_1 ≤ c_1, ..., Z_K ≤ c_K)

    通过边界平移将 H1 问题转化为 H0 问题：
    Z_k - μ·√(t_k) 在 H0 下服从标准多元正态。

    Parameters
    ----------
    boundaries : np.ndarray
        上侧边界
    info_rates : np.ndarray
        信息比例
    drift : float
        漂移参数 μ = E[Z_K]（最终分析时的期望 Z 值）
    **kwargs
        传递给 _prob_no_cross 的额外参数

    Returns
    -------
    float
        H1 下的未越界概率
    """
    shifted = boundaries - drift * np.sqrt(info_rates)
    return _prob_no_cross(shifted, info_rates, **kwargs)


def _find_efficacy_boundary(
    k: int,
    prev_boundaries: List[float],
    info_rates: np.ndarray,
    alpha_target: float,
    grid_size: int = 200,
) -> float:
    """求解第 k 次分析的优效性边界 c_k

    使得 P(Z_1 ≤ c_1, ..., Z_k ≤ c_k) = 1 - α_target

    Parameters
    ----------
    k : int
        当前分析序号（0-indexed）
    prev_boundaries : List[float]
        前 k-1 次分析的边界
    info_rates : np.ndarray
        信息比例（前 k 个）
    alpha_target : float
        累积 α 消耗目标值

    Returns
    -------
    float
        边界 c_k
    """

    def objective(c: float) -> float:
        bounds = np.array(list(prev_boundaries) + [c])
        prob = _prob_no_cross(bounds, info_rates[: k + 1], grid_size=grid_size)
        return prob - (1.0 - alpha_target)

    # 边界随 c 单调递增，使用 brentq 求根
    return brentq(objective, -6.0, 12.0, xtol=1e-6)


def group_sequential_design(
    k_max: int = 3,
    alpha: float = 0.025,
    beta: float = 0.2,
    info_rates: Optional[np.ndarray] = None,
    spending_type: str = "of",
    futility: Optional[str] = "non-binding",
    futility_cp_threshold: float = 0.2,
    grid_size: int = 200,
) -> Dict[str, Any]:
    """成组序贯设计

    基于 Lan-DeMets α 消耗函数构建成组序贯设计，计算优效性停止边界
    和（可选）无效性停止边界。

    Parameters
    ----------
    k_max : int
        最大分析次数（含最终分析），≥ 2
    alpha : float
        总 I 类错误率（单侧），默认 0.025
    beta : float
        总 II 类错误率，默认 0.2（把握度 = 80%）
    info_rates : Optional[np.ndarray]
        信息比例向量，默认等距 (1, 2, ..., k_max) / k_max
    spending_type : str
        α 消耗函数类型: "of"（O'Brien-Fleming）或 "pocock"
    futility : Optional[str]
        无效性边界类型: "non-binding"（默认）、"binding" 或 None
    futility_cp_threshold : float
        基于条件把握度的无效性阈值，默认 0.2（CP < 20% 则建议停止）
    grid_size : int
        数值积分网格点数

    Returns
    -------
    Dict[str, Any]
        设计对象，包含：
        - 'efficacy_boundaries': 优效性边界数组
        - 'futility_boundaries': 无效性边界数组（或 None）
        - 'info_rates': 信息比例
        - 'alpha_spent': 各次分析累积 α 消耗
        - 'drift': 达到目标把握度所需的漂移参数
        - 'power': 达到的把握度
        - 'design_type': 设计类型描述
        - 'k_max': 分析次数
        - 'alpha': 总 α
        - 'beta': 总 β

    Examples
    --------
    >>> design = group_sequential_design(k_max=3, alpha=0.025, spending_type="of")
    >>> print(design['efficacy_boundaries'])
    """
    if k_max < 2:
        raise ValueError("k_max 必须 ≥ 2")

    if info_rates is None:
        info_rates = np.arange(1, k_max + 1, dtype=float) / k_max
    else:
        info_rates = np.asarray(info_rates, dtype=float)
        if len(info_rates) != k_max:
            raise ValueError(f"info_rates 长度必须等于 k_max={k_max}")
        if info_rates[-1] != 1.0:
            raise ValueError("info_rates 最后一个元素必须为 1.0")

    # 计算 α 消耗
    alpha_spent = np.array(
        [alpha_spending_function(t, alpha, spending_type) for t in info_rates]
    )

    # 递归求解优效性边界
    efficacy_boundaries = np.zeros(k_max)
    prev_bounds: List[float] = []
    for k in range(k_max):
        c_k = _find_efficacy_boundary(
            k, prev_bounds, info_rates, alpha_spent[k], grid_size
        )
        efficacy_boundaries[k] = c_k
        prev_bounds.append(c_k)

    # 求解达到目标把握度所需的漂移参数
    target_power = 1.0 - beta

    def power_obj(drift: float) -> float:
        prob_no_cross_h1 = _prob_no_cross_drift(
            efficacy_boundaries, info_rates, drift, grid_size=grid_size
        )
        return (1.0 - prob_no_cross_h1) - target_power

    drift = brentq(power_obj, 0.0, 15.0, xtol=1e-6)

    # 计算无效性边界（基于条件把握度）
    futility_boundaries = None
    if futility is not None:
        futility_boundaries = np.full(k_max, np.nan)
        # 最终分析的无效性边界 = 优效性边界
        futility_boundaries[-1] = efficacy_boundaries[-1]

        for k in range(k_max - 1):
            t_k = info_rates[k]
            t_K = info_rates[-1]
            ratio = np.sqrt(t_k / t_K)
            sigma_cond = np.sqrt(1.0 - t_k / t_K)
            c_K = efficacy_boundaries[-1]

            # 求解 z 使得 CP = futility_cp_threshold
            # CP = 1 - Φ((c_K - ratio·z - drift·(1-t_k/t_K)) / σ_cond)
            # 设 CP = cp_threshold:
            # Φ((c_K - ratio·z - drift·(1-t_k/t_K)) / σ_cond) = 1 - cp_threshold
            z_crit = stats.norm.ppf(1.0 - futility_cp_threshold)
            futility_boundaries[k] = (
                c_K - drift * (1.0 - t_k / t_K) - z_crit * sigma_cond
            ) / ratio

    # 计算实际把握度
    actual_power = 1.0 - _prob_no_cross_drift(
        efficacy_boundaries, info_rates, drift, grid_size=grid_size
    )

    design_type_map = {"of": "O'Brien-Fleming", "pocock": "Pocock"}
    return {
        "efficacy_boundaries": efficacy_boundaries,
        "futility_boundaries": futility_boundaries,
        "info_rates": info_rates,
        "alpha_spent": alpha_spent,
        "drift": drift,
        "power": actual_power,
        "design_type": design_type_map.get(spending_type, spending_type),
        "k_max": k_max,
        "alpha": alpha,
        "beta": beta,
        "spending_type": spending_type,
        "futility": futility,
        "futility_cp_threshold": futility_cp_threshold,
    }


def obrien_fleming_design(
    k_max: int = 3,
    alpha: float = 0.025,
    beta: float = 0.2,
    info_rates: Optional[np.ndarray] = None,
    futility: Optional[str] = "non-binding",
    **kwargs: Any,
) -> Dict[str, Any]:
    """O'Brien-Fleming 成组序贯设计（便捷封装）

    早期边界非常保守，最终分析边界接近固定设计水平。
    适用于希望尽可能减少早期停止机会的设计。

    Parameters
    ----------
    k_max : int
        最大分析次数
    alpha : float
        总 I 类错误率（单侧）
    beta : float
        总 II 类错误率
    info_rates : Optional[np.ndarray]
        信息比例
    futility : Optional[str]
        无效性边界类型
    **kwargs
        传递给 group_sequential_design 的额外参数

    Returns
    -------
    Dict[str, Any]
        设计对象

    Examples
    --------
    >>> design = obrien_fleming_design(k_max=3, alpha=0.025)
    """
    return group_sequential_design(
        k_max=k_max,
        alpha=alpha,
        beta=beta,
        info_rates=info_rates,
        spending_type="of",
        futility=futility,
        **kwargs,
    )


def pocock_design(
    k_max: int = 3,
    alpha: float = 0.025,
    beta: float = 0.2,
    info_rates: Optional[np.ndarray] = None,
    futility: Optional[str] = "non-binding",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Pocock 成组序贯设计（便捷封装）

    各次分析使用恒定边界，早期停止机会较大。
    适用于希望在有早期信号时尽早停止的设计。

    Parameters
    ----------
    k_max : int
        最大分析次数
    alpha : float
        总 I 类错误率（单侧）
    beta : float
        总 II 类错误率
    info_rates : Optional[np.ndarray]
        信息比例
    futility : Optional[str]
        无效性边界类型
    **kwargs
        传递给 group_sequential_design 的额外参数

    Returns
    -------
    Dict[str, Any]
        设计对象

    Examples
    --------
    >>> design = pocock_design(k_max=3, alpha=0.025)
    """
    return group_sequential_design(
        k_max=k_max,
        alpha=alpha,
        beta=beta,
        info_rates=info_rates,
        spending_type="pocock",
        futility=futility,
        **kwargs,
    )


def lan_demets_design(
    k_max: int = 3,
    alpha: float = 0.025,
    beta: float = 0.2,
    info_rates: Optional[np.ndarray] = None,
    spending_type: str = "of",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Lan-DeMets 成组序贯设计（便捷封装）

    使用 Lan-DeMets α 消耗函数框架，支持灵活的信息比例和消耗函数类型。
    本函数是 group_sequential_design 的别名，强调 Lan-DeMets 框架。

    Parameters
    ----------
    k_max : int
        最大分析次数
    alpha : float
        总 I 类错误率（单侧）
    beta : float
        总 II 类错误率
    info_rates : Optional[np.ndarray]
        信息比例（无需等距，Lan-DeMets 框架的优势）
    spending_type : str
        α 消耗函数类型: "of" 或 "pocock"
    **kwargs
        传递给 group_sequential_design 的额外参数

    Returns
    -------
    Dict[str, Any]
        设计对象

    Examples
    --------
    >>> # 非等距信息比例
    >>> design = lan_demets_design(
    ...     k_max=3, alpha=0.025,
    ...     info_rates=np.array([0.3, 0.7, 1.0]),
    ... )
    """
    return group_sequential_design(
        k_max=k_max,
        alpha=alpha,
        beta=beta,
        info_rates=info_rates,
        spending_type=spending_type,
        **kwargs,
    )


# ============================================================================
# 2. 期中分析样本量重新估计（Sample Size Re-estimation）
# ============================================================================
#
# 样本量重新估计分为两类：
#   (a) 盲态重新估计：不揭盲，基于合并方差/合并效应量重新估计样本量
#   (b) 非盲态重新估计：基于观察到的组间效应差重新估计（需独立统计师执行）
#
# 条件把握度（Conditional Power）是期中分析决策的核心指标：
#   CP = P(最终分析显著 | 当前期中结果, 假设效应方向)


def conditional_power(
    z_interim: float,
    t_interim: float,
    t_final: float,
    boundary_final: float,
    drift: float,
) -> float:
    """条件把握度计算

    给定期中分析的检验统计量，计算最终分析达到显著性的条件概率。

    条件分布: Z_final | Z_interim = z ~ N(√(t_k/t_K)·z + μ·(1-t_k/t_K), 1-t_k/t_K)

    Parameters
    ----------
    z_interim : float
        期中分析的检验统计量 Z_k
    t_interim : float
        期中分析的信息比例 t_k
    t_final : float
        最终分析的信息比例 t_K（通常为 1.0）
    boundary_final : float
        最终分析的优效性边界 c_K
    drift : float
        漂移参数 μ = E[Z_final]（H1 下的期望 Z 值）
        - drift > 0：按设计假设的效应方向
        - drift = 0：按 H0（零效应）
        - drift = z_interim / sqrt(t_interim)：按观察效应量

    Returns
    -------
    float
        条件把握度 CP ∈ [0, 1]

    Examples
    --------
    >>> cp = conditional_power(z_interim=1.5, t_interim=0.5, t_final=1.0,
    ...                        boundary_final=1.99, drift=3.0)
    >>> print(f"条件把握度: {cp:.4f}")
    """
    ratio = np.sqrt(t_interim / t_final)
    sigma_cond = np.sqrt(1.0 - t_interim / t_final)

    # 条件均值和标准差
    cond_mean = ratio * z_interim + drift * (1.0 - t_interim / t_final)
    cond_sd = sigma_cond

    # CP = P(Z_final > boundary_final | Z_interim = z)
    cp = 1.0 - stats.norm.cdf((boundary_final - cond_mean) / cond_sd)
    return float(cp)


def blinded_sample_size_reestimation(
    n_obs: int,
    pooled_sd: float,
    effect_size: float,
    alpha: float = 0.025,
    power: float = 0.8,
    allocation_ratio: float = 1.0,
) -> Dict[str, Any]:
    """基于盲态观察的样本量重新估计

    在不揭盲的情况下，利用合并标准差（连续型终点）重新估计所需样本量。
    此方法不改变试验的 I 类错误率，因为未使用组间差异信息。

    Parameters
    ----------
    n_obs : int
        期中分析时已观察的受试者总数
    pooled_sd : float
        盲态合并标准差（所有组数据合并后计算）
    effect_size : float
        假设的组间效应差（原始尺度，如均值差）
    alpha : float
        显著性水平（单侧），默认 0.025
    power : float
        目标把握度，默认 0.8
    allocation_ratio : float
        分配比（试验组:对照组），默认 1:1

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'n_per_group_original': 原始每组样本量（基于初始假设）
        - 'n_per_group_reestimated': 重新估计的每组样本量
        - 'n_total_reestimated': 重新估计的总样本量
        - 'pooled_sd': 使用的合并标准差
        - 'effect_size': 假设效应量
        - 'adjustment_factor': 调整因子（重新估计/原始）

    Examples
    --------
    >>> result = blinded_sample_size_reestimation(
    ...     n_obs=100, pooled_sd=12.5, effect_size=5.0,
    ...     alpha=0.025, power=0.8,
    ... )
    >>> print(result['n_per_group_reestimated'])
    """
    z_alpha = stats.norm.ppf(1 - alpha)
    z_beta = stats.norm.ppf(power)

    # 标准化效应量（Cohen's d）
    d = effect_size / pooled_sd

    # 每组样本量公式（两样本 t 检验，1:1 分配）
    # n = (z_alpha + z_beta)^2 * (1 + 1/r) / d^2，r = allocation_ratio
    r = allocation_ratio
    n_per_group = (z_alpha + z_beta) ** 2 * (1.0 + 1.0 / r) / d ** 2
    n_per_group = int(np.ceil(n_per_group))
    n_total = n_per_group * (1 + int(r)) if r == int(r) else int(np.ceil(n_per_group * (1 + r)))

    return {
        "n_per_group_reestimated": n_per_group,
        "n_total_reestimated": n_total,
        "pooled_sd": pooled_sd,
        "effect_size": effect_size,
        "standardized_effect": d,
        "n_obs_at_interim": n_obs,
        "alpha": alpha,
        "power": power,
        "allocation_ratio": allocation_ratio,
    }


def conditional_power_reestimation(
    z_interim: float,
    t_interim: float,
    design: Dict[str, Any],
    target_cp: float = 0.8,
    max_inflation: float = 1.5,
) -> Dict[str, Any]:
    """基于条件把握度的样本量重新估计

    根据期中分析观察到的效应量，重新估计达到目标条件把握度所需的样本量。
    此方法为非盲态，需由独立统计师执行以保护试验完整性。

    Parameters
    ----------
    z_interim : float
        期中分析的检验统计量
    t_interim : float
        期中分析的信息比例
    design : Dict[str, Any]
        成组序贯设计对象（来自 group_sequential_design）
    target_cp : float
        目标条件把握度，默认 0.8
    max_inflation : float
        最大样本量膨胀因子（相对于原始设计），默认 1.5

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'cp_current': 当前条件把握度（按观察效应量）
        - 'cp_design': 按设计假设的条件把握度
        - 'cp_null': 按 H0 的条件把握度
        - 'n_inflation_factor': 所需样本量膨胀因子
        - 'recommendation': 建议（'increase'/'maintain'/'stop_futility'）
        - 'new_t_final': 新的最终信息比例

    Examples
    --------
    >>> design = obrien_fleming_design(k_max=3, alpha=0.025)
    >>> result = conditional_power_reestimation(
    ...     z_interim=1.2, t_interim=0.5, design=design, target_cp=0.8,
    ... )
    >>> print(result['recommendation'])
    """
    t_final_orig = design["info_rates"][-1]
    boundary_final = design["efficacy_boundaries"][-1]
    drift_design = design["drift"]

    # 观察效应量估计的漂移
    drift_observed = z_interim / np.sqrt(t_interim)

    # 三种假设下的条件把握度
    cp_observed = conditional_power(
        z_interim, t_interim, t_final_orig, boundary_final, drift_observed
    )
    cp_design = conditional_power(
        z_interim, t_interim, t_final_orig, boundary_final, drift_design
    )
    cp_null = conditional_power(
        z_interim, t_interim, t_final_orig, boundary_final, 0.0
    )

    # 求解达到目标 CP 所需的信息比例膨胀
    # 增加总信息量 → t_interim 减小 → 条件把握度变化
    def cp_obj(inflation: float) -> float:
        new_t_final = t_final_orig * inflation
        new_t_interim = t_interim / inflation  # 期中信息量不变，但占总信息比例减小
        cp = conditional_power(
            z_interim, new_t_interim, new_t_final, boundary_final, drift_observed
        )
        return cp - target_cp

    # 搜索膨胀因子
    try:
        if cp_obj(1.0) >= 0:
            # 当前设计已满足目标 CP
            inflation = 1.0
        else:
            inflation = brentq(cp_obj, 1.0, max_inflation + 0.01, xtol=1e-4)
            inflation = min(inflation, max_inflation)
    except (ValueError, RuntimeError):
        inflation = max_inflation

    # 决策建议
    if cp_observed < design.get("futility_cp_threshold", 0.2):
        recommendation = "stop_futility"
    elif inflation > 1.0:
        recommendation = "increase"
    else:
        recommendation = "maintain"

    return {
        "cp_current": cp_observed,
        "cp_design": cp_design,
        "cp_null": cp_null,
        "n_inflation_factor": inflation,
        "recommendation": recommendation,
        "new_t_final": t_final_orig * inflation,
        "target_cp": target_cp,
        "drift_observed": drift_observed,
        "drift_design": drift_design,
    }


# ============================================================================
# 3. 适应性随机化（Adaptive Randomization）
# ============================================================================
#
# 适应性随机化根据已入组受试者的基线特征或治疗反应动态调整分配概率，
# 提高试验的伦理性和效率。


def randomized_play_the_winner(
    n: int,
    p_success_a: float,
    p_success_b: float,
    a0: int = 1,
    a1: int = 1,
    random_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """随机化胜者分配（Randomized Play-the-Winner, RPW）模型

    基于 urn 模型的响应自适应随机化。成功结局增加同组球的数目，
    失败结局增加对侧组的球数目，使更多受试者被分配到更优治疗组。

    RPW(a0, a1) 模型：
    - 初始 urn 中有 a0 个 A 球和 a0 个 B 球
    - 每次抽球决定分配，抽后放回
    - 若结果为成功：向 urn 中加入 a1 个同组球
    - 若结果为失败：向 urn 中加入 a1 个对侧组球

    Parameters
    ----------
    n : int
        总样本量
    p_success_a : float
        A 组成功率
    p_success_b : float
        B 组成功率
    a0 : int
        初始球数（每组），默认 1
    a1 : int
        每次反应后添加的球数，默认 1
    random_seed : Optional[int]
        随机种子

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'assignments': 分配序列（0=A, 1=B）
        - 'outcomes': 结局序列（0=失败, 1=成功）
        - 'n_a': A 组样本量
        - 'n_b': B 组样本量
        - 'success_a': A 组成功数
        - 'success_b': B 组成功数
        - 'allocation_ratio': 实际分配比 n_b/n_a

    Examples
    --------
    >>> result = randomized_play_the_winner(
    ...     n=100, p_success_a=0.3, p_success_b=0.6, random_seed=42,
    ... )
    >>> print(f"B组分配比例: {result['n_b']/100:.2%}")
    """
    rng = np.random.default_rng(random_seed)

    balls_a = a0
    balls_b = a0
    assignments = np.zeros(n, dtype=int)
    outcomes = np.zeros(n, dtype=int)

    for i in range(n):
        # 抽球决定分配
        prob_a = balls_a / (balls_a + balls_b)
        assignments[i] = 0 if rng.random() < prob_a else 1

        # 模拟结局
        if assignments[i] == 0:
            outcomes[i] = 1 if rng.random() < p_success_a else 0
        else:
            outcomes[i] = 1 if rng.random() < p_success_b else 0

        # 根据 urn 规则添加球
        if outcomes[i] == 1:
            # 成功：加同组球
            if assignments[i] == 0:
                balls_a += a1
            else:
                balls_b += a1
        else:
            # 失败：加对侧组球
            if assignments[i] == 0:
                balls_b += a1
            else:
                balls_a += a1

    n_a = int(np.sum(assignments == 0))
    n_b = int(np.sum(assignments == 1))
    success_a = int(np.sum((assignments == 0) & (outcomes == 1)))
    success_b = int(np.sum((assignments == 1) & (outcomes == 1)))

    return {
        "assignments": assignments,
        "outcomes": outcomes,
        "n_a": n_a,
        "n_b": n_b,
        "success_a": success_a,
        "success_b": success_b,
        "allocation_ratio": n_b / max(n_a, 1),
        "method": "RPW",
        "params": {"a0": a0, "a1": a1},
    }


def minimization_randomization(
    factor_matrix: np.ndarray,
    n_treatments: int = 2,
    weights: Optional[np.ndarray] = None,
    p_rand: float = 0.8,
    random_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """最小化随机化（Minimization）

    基于多个预后因子的动态分配方法，使各治疗组在各因子水平上的不平衡
    最小化。适用于多中心试验或需要精确平衡多个协变量的场景。

    Parameters
    ----------
    factor_matrix : np.ndarray
        预后因子矩阵，形状 (n_patients, n_factors)，每列为一个因子的
        水平编码（整数）
    n_treatments : int
        治疗组数，默认 2
    weights : Optional[np.ndarray]
        各因子权重，默认等权
    p_rand : float
        分配到最优组的概率（0.5=完全随机, 1.0=确定性分配），
        默认 0.8（Pocock-Simon 建议）
    random_seed : Optional[int]
        随机种子

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'assignments': 分配序列（0, 1, ..., n_treatments-1）
        - 'imbalance_history': 每步的总不平衡量
        - 'final_imbalance': 最终不平衡量
        - 'factor_balance': 各因子各水平各组的计数

    Examples
    --------
    >>> # 3 个预后因子：性别(0/1)、年龄组(0/1/2)、中心(0/1)
    >>> factors = np.array([
    ...     [0, 0, 0], [1, 1, 0], [0, 2, 1], [1, 0, 1],
    ... ])
    >>> result = minimization_randomization(factors, n_treatments=2, random_seed=42)
    >>> print(result['assignments'])
    """
    rng = np.random.default_rng(random_seed)
    n_patients, n_factors = factor_matrix.shape

    if weights is None:
        weights = np.ones(n_factors)
    weights = np.asarray(weights, dtype=float)

    assignments = np.zeros(n_patients, dtype=int)
    imbalance_history = np.zeros(n_patients)

    # 各因子各水平各组的累计计数
    # balance[f, level, treatment] = 该因子该水平该组的受试者数
    factor_levels = [int(factor_matrix[:, f].max()) + 1 for f in range(n_factors)]
    balance = np.zeros((n_factors, max(factor_levels), n_treatments), dtype=int)

    for i in range(n_patients):
        patient_factors = factor_matrix[i]

        # 计算分配到每个治疗组的加权不平衡量
        imbalances = np.zeros(n_treatments)
        for t in range(n_treatments):
            total_imbalance = 0.0
            for f in range(n_factors):
                level = int(patient_factors[f])
                # 该因子该水平各组的计数
                counts = balance[f, level, :].astype(float)
                # 假设分配到组 t 后的计数
                counts[t] += 1
                # 不平衡量 = 该水平最大组计数 - 最小组计数
                total_imbalance += weights[f] * (counts.max() - counts.min())
            imbalances[t] = total_imbalance

        # 选择不平衡量最小的组
        min_imbalance = imbalances.min()
        best_groups = np.where(imbalances == min_imbalance)[0]

        if len(best_groups) == 1:
            best_group = best_groups[0]
        else:
            # 多个组并列最优，随机选择
            best_group = rng.choice(best_groups)

        # 以概率 p_rand 分配到最优组，否则随机分配
        if rng.random() < p_rand:
            assignments[i] = best_group
        else:
            assignments[i] = rng.integers(0, n_treatments)

        # 更新平衡计数
        for f in range(n_factors):
            level = int(patient_factors[f])
            balance[f, level, assignments[i]] += 1

        imbalance_history[i] = min_imbalance

    return {
        "assignments": assignments,
        "imbalance_history": imbalance_history,
        "final_imbalance": float(imbalance_history[-1]),
        "factor_balance": balance,
        "method": "Minimization",
        "params": {"weights": weights, "p_rand": p_rand},
    }


# ============================================================================
# 4. 期中分析决策规则（Interim Analysis Decision Rules）
# ============================================================================
#
# 根据期中分析的检验统计量与设计边界的比较，做出试验决策：
#   - 优效性停止：Z_k ≥ 优效性边界 → 提前结束，结论优效
#   - 无效性停止：Z_k ≤ 无效性边界 → 提前结束，结论无效
#   - 继续试验：无效性边界 < Z_k < 优效性边界 → 继续入组


def interim_decision(
    z_stat: float,
    look: int,
    design: Dict[str, Any],
    n_obs: Optional[int] = None,
    n_planned: Optional[int] = None,
) -> Dict[str, Any]:
    """期中分析决策

    根据期中检验统计量与成组序贯设计边界比较，给出试验决策建议。

    Parameters
    ----------
    z_stat : float
        期中分析的检验统计量 Z_k
    look : int
        期中分析序号（1-indexed，1 表示第一次期中分析）
    design : Dict[str, Any]
        成组序贯设计对象
    n_obs : Optional[int]
        当前已入组/已观察的受试者数
    n_planned : Optional[int]
        计划总样本量

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'decision': 决策（'stop_efficacy'/'stop_futility'/'continue'）
        - 'z_stat': 检验统计量
        - 'efficacy_boundary': 当前优效性边界
        - 'futility_boundary': 当前无效性边界（如适用）
        - 'look': 期中分析序号
        - 'info_rate': 当前信息比例
        - 'alpha_spent': 累积 α 消耗
        - 'conditional_power': 条件把握度（如可计算）
        - 'recommendation': 文字建议

    Examples
    --------
    >>> design = obrien_fleming_design(k_max=3, alpha=0.025)
    >>> result = interim_decision(z_stat=2.5, look=1, design=design)
    >>> print(result['decision'])
    """
    k = look - 1  # 转为 0-indexed
    if k < 0 or k >= design["k_max"]:
        raise ValueError(
            f"look 必须在 1 到 {design['k_max']} 之间"
        )

    eff_boundary = design["efficacy_boundaries"][k]
    fut_boundary = None
    if design["futility_boundaries"] is not None:
        fut_boundary = design["futility_boundaries"][k]
        if np.isnan(fut_boundary):
            fut_boundary = None

    info_rate = design["info_rates"][k]
    alpha_spent = design["alpha_spent"][k]

    # 决策逻辑
    if z_stat >= eff_boundary:
        decision = "stop_efficacy"
        recommendation = (
            f"检验统计量 Z = {z_stat:.4f} ≥ 优效性边界 {eff_boundary:.4f}，"
            f"建议提前停止试验，结论优效。"
        )
    elif fut_boundary is not None and z_stat <= fut_boundary:
        decision = "stop_futility"
        recommendation = (
            f"检验统计量 Z = {z_stat:.4f} ≤ 无效性边界 {fut_boundary:.4f}，"
            f"建议提前停止试验，结论无效（治疗效应不足以支持继续）。"
        )
    else:
        decision = "continue"
        if fut_boundary is not None:
            recommendation = (
                f"检验统计量 Z = {z_stat:.4f} 位于无效性边界 "
                f"{fut_boundary:.4f} 与优效性边界 {eff_boundary:.4f} 之间，"
                f"建议继续试验。"
            )
        else:
            recommendation = (
                f"检验统计量 Z = {z_stat:.4f} < 优效性边界 "
                f"{eff_boundary:.4f}，建议继续试验。"
            )

    # 条件把握度（如果不是最终分析）
    cp = None
    if k < design["k_max"] - 1:
        t_final = design["info_rates"][-1]
        boundary_final = design["efficacy_boundaries"][-1]
        # 按观察效应量估计漂移
        drift_obs = z_stat / np.sqrt(info_rate) if info_rate > 0 else 0.0
        cp = conditional_power(
            z_stat, info_rate, t_final, boundary_final, drift_obs
        )

    result = {
        "decision": decision,
        "z_stat": z_stat,
        "efficacy_boundary": float(eff_boundary),
        "futility_boundary": float(fut_boundary) if fut_boundary is not None else None,
        "look": look,
        "info_rate": float(info_rate),
        "alpha_spent": float(alpha_spent),
        "conditional_power": cp,
        "recommendation": recommendation,
    }

    if n_obs is not None:
        result["n_obs"] = n_obs
    if n_planned is not None:
        result["n_planned"] = n_planned
        result["enrollment_pct"] = n_obs / n_planned if n_obs else None

    return result


# ============================================================================
# 5. 多重性校正（Multiplicity Correction）
# ============================================================================
#
# 当试验涉及多个主要终点、多次期中分析或多个假设检验时，需控制
# 总 I 类错误率（FWER）。


def alpha_spending_correction(
    looks: int,
    alpha: float = 0.025,
    spending_type: str = "of",
) -> Dict[str, Any]:
    """α 消耗函数多重性校正

    使用 Lan-DeMets α 消耗函数在多次期中分析间分配 α，
    控制总 I 类错误率。

    Parameters
    ----------
    looks : int
        分析次数
    alpha : float
        总 I 类错误率（单侧）
    spending_type : str
        消耗函数类型: "of" 或 "pocock"

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'alpha_cumulative': 各次分析累积 α
        - 'alpha_incremental': 各次分析增量 α
        - 'boundaries': 对应的 Z 边界（单次检验）
        - 'spending_type': 消耗函数类型

    Examples
    --------
    >>> result = alpha_spending_correction(looks=3, alpha=0.025, spending_type="of")
    >>> print(result['alpha_cumulative'])
    """
    info_rates = np.arange(1, looks + 1, dtype=float) / looks
    alpha_cum = np.array(
        [alpha_spending_function(t, alpha, spending_type) for t in info_rates]
    )
    alpha_inc = np.diff(alpha_cum, prepend=0.0)

    # 单次检验的 Z 边界（近似，未考虑相关性）
    boundaries = stats.norm.ppf(1 - alpha_inc)

    return {
        "alpha_cumulative": alpha_cum,
        "alpha_incremental": alpha_inc,
        "boundaries": boundaries,
        "info_rates": info_rates,
        "spending_type": spending_type,
        "total_alpha": alpha,
    }


def closed_testing_procedure(
    p_values: np.ndarray,
    alpha: float = 0.05,
    local_test: str = "bonferroni",
) -> Dict[str, Any]:
    """封闭检验程序（Closed Testing Procedure）

    控制多重检验的 FWER（族系错误率）。对原假设的所有交集进行检验，
    仅当包含某假设的所有交集均被拒绝时，才拒绝该假设。

    Parameters
    ----------
    p_values : np.ndarray
        m 个假设的 p 值
    alpha : float
        显著性水平，默认 0.05
    local_test : str
        交集假设的局部检验方法:
        - "bonferroni": Bonferroni 检验（等价于 Holm 步降法）
        - "sidak": Šidák 检验
        - "simes": Simes 检验（等价于 Hochberg 步升法）

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'rejected': 各假设是否被拒绝的布尔数组
        - 'adjusted_p_values': 调整后 p 值
        - 'alpha': 显著性水平
        - 'local_test': 局部检验方法

    Examples
    --------
    >>> pvals = np.array([0.01, 0.04, 0.03])
    >>> result = closed_testing_procedure(pvals, alpha=0.05, local_test="bonferroni")
    >>> print(result['rejected'])
    """
    p_values = np.asarray(p_values, dtype=float)
    m = len(p_values)
    rejected = np.zeros(m, dtype=bool)
    # 初始化为 0：H_i 的调整 p 值 = max(包含 i 的所有交集假设的 p 值)
    adjusted_p = np.zeros(m)

    # 对所有 2^m - 1 个非空子集计算交集假设的 p 值
    for mask in range(1, 2 ** m):
        subset_idx = np.where(mask & (1 << np.arange(m)))[0]
        subset_size = len(subset_idx)
        subset_p = p_values[subset_idx]

        if local_test == "bonferroni":
            intersection_p = min(subset_size * subset_p.min(), 1.0)
        elif local_test == "sidak":
            intersection_p = 1.0 - (1.0 - subset_p.min()) ** subset_size
        elif local_test == "simes":
            sorted_p = np.sort(subset_p)
            simes_p = (subset_size * sorted_p / np.arange(1, subset_size + 1)).min()
            intersection_p = min(simes_p, 1.0)
        else:
            raise ValueError(f"不支持的局部检验方法: {local_test}")

        # 更新调整 p 值：H_i 的调整 p 值 = max(包含 i 的所有交集的 p 值)
        for i in subset_idx:
            adjusted_p[i] = max(adjusted_p[i], intersection_p)

    # 封顶为 1.0
    adjusted_p = np.minimum(adjusted_p, 1.0)

    # 拒绝规则：调整 p 值 ≤ α
    rejected = adjusted_p <= alpha

    return {
        "rejected": rejected,
        "adjusted_p_values": adjusted_p,
        "alpha": alpha,
        "local_test": local_test,
        "n_hypotheses": m,
    }


# ============================================================================
# 6. 报告生成（Report Generation）
# ============================================================================


def generate_interim_report(
    design: Dict[str, Any],
    interim_results: Optional[List[Dict[str, Any]]] = None,
    study_info: Optional[Dict[str, Any]] = None,
) -> str:
    """生成期中分析报告（Markdown 格式）

    Parameters
    ----------
    design : Dict[str, Any]
        成组序贯设计对象
    interim_results : Optional[List[Dict[str, Any]]]
        各次期中分析的结果列表（来自 interim_decision）
    study_info : Optional[Dict[str, Any]]
        研究信息字典，可包含 'study_title', 'study_id', 'sponsor' 等

    Returns
    -------
    str
        Markdown 格式的期中分析报告

    Examples
    --------
    >>> design = obrien_fleming_design(k_max=3, alpha=0.025)
    >>> decision = interim_decision(z_stat=1.5, look=1, design=design)
    >>> report = generate_interim_report(design, [decision])
    >>> print(report[:200])
    """
    info = study_info or {}
    lines: List[str] = []

    # 标题
    lines.append("# 期中分析报告\n")
    lines.append(f"**研究标题**：{info.get('study_title', '[{研究标题}]')}\n")
    lines.append(f"**研究ID**：{info.get('study_id', '[{研究ID}]')}\n")
    lines.append(f"**申办方**：{info.get('sponsor', '[{申办方}]')}\n")
    lines.append(f"**报告日期**：{info.get('report_date', '[{日期}]')}\n")
    lines.append("---\n")

    # 1. 设计概要
    lines.append("## 1. 设计概要\n")
    lines.append(f"- **设计类型**：成组序贯设计（{design['design_type']}边界）\n")
    lines.append(f"- **分析次数**：{design['k_max']}\n")
    lines.append(f"- **总α（单侧）**：{design['alpha']}\n")
    lines.append(f"- **目标把握度**：{1 - design['beta']:.0%}\n")
    lines.append(f"- **实际把握度**：{design['power']:.2%}\n")
    lines.append(f"- **漂移参数**：{design['drift']:.4f}\n")
    lines.append(f"- **无效性边界**：{design['futility'] or '无'}\n")
    if design["futility"] is not None:
        lines.append(
            f"- **无效性 CP 阈值**：{design['futility_cp_threshold']:.0%}\n"
        )
    lines.append("")

    # 2. 边界表
    lines.append("## 2. 停止边界\n")
    lines.append("| 分析序号 | 信息比例 | 优效性边界 | 无效性边界 | 累积α消耗 |")
    lines.append("|:--------:|:--------:|:----------:|:----------:|:---------:|")
    for k in range(design["k_max"]):
        fut = (
            f"{design['futility_boundaries'][k]:.4f}"
            if design["futility_boundaries"] is not None
            and not np.isnan(design["futility_boundaries"][k])
            else "—"
        )
        lines.append(
            f"| {k + 1} | {design['info_rates'][k]:.2f} | "
            f"{design['efficacy_boundaries'][k]:.4f} | {fut} | "
            f"{design['alpha_spent'][k]:.4f} |"
        )
    lines.append("")

    # 3. 期中分析结果
    if interim_results:
        lines.append("## 3. 期中分析结果\n")
        for res in interim_results:
            lines.append(f"### 第 {res['look']} 次期中分析\n")
            lines.append(f"- **检验统计量 Z**：{res['z_stat']:.4f}\n")
            lines.append(f"- **优效性边界**：{res['efficacy_boundary']:.4f}\n")
            if res.get("futility_boundary") is not None:
                lines.append(
                    f"- **无效性边界**：{res['futility_boundary']:.4f}\n"
                )
            lines.append(f"- **信息比例**：{res['info_rate']:.2f}\n")
            lines.append(f"- **累积α消耗**：{res['alpha_spent']:.4f}\n")
            if res.get("conditional_power") is not None:
                lines.append(
                    f"- **条件把握度**：{res['conditional_power']:.2%}\n"
                )
            if res.get("n_obs") is not None:
                lines.append(
                    f"- **已入组例数**：{res['n_obs']}\n"
                )
            lines.append(f"- **决策**：**{res['decision']}**\n")
            lines.append(f"- **建议**：{res['recommendation']}\n")
            lines.append("")

    # 4. 决策建议汇总
    if interim_results:
        lines.append("## 4. 决策建议汇总\n")
        decisions = [r["decision"] for r in interim_results]
        if "stop_efficacy" in decisions:
            lines.append(
                "> **建议**：至少一次期中分析达到优效性停止边界，"
                "建议提前结束试验并申报优效结论。\n"
            )
        elif "stop_futility" in decisions:
            lines.append(
                "> **建议**：至少一次期中分析达到无效性停止边界，"
                "建议提前结束试验。\n"
            )
        else:
            lines.append(
                "> **建议**：所有期中分析均未达到停止边界，建议继续试验至下一阶段。\n"
            )
        lines.append("")

    # 5. 注意事项
    lines.append("## 5. 注意事项\n")
    lines.append("- 本报告仅供独立数据监查委员会（IDMC）内部使用\n")
    lines.append("- 期中分析结果在试验结束前对申办方和研究者保持盲态\n")
    lines.append("- 任何基于期中分析的方案修改需经 IDMC 建议并报监管机构备案\n")
    lines.append("- 条件把握度基于观察效应量估计，存在不确定性\n")
    lines.append("")

    lines.append("---")
    lines.append(
        f"\n*报告由 adaptive_interim_analysis_template.py 自动生成 | "
        f"设计类型: {design['design_type']} | α={design['alpha']}*\n"
    )

    return "\n".join(lines)


# ============================================================================
# 7. 可视化（Visualization）
# ============================================================================


def _setup_cjk_font() -> None:
    """配置 matplotlib 中文字体（内部辅助函数）

    尝试设置系统可用的中文字体，避免中文标签显示为方框。
    若无中文字体则静默降级为默认字体。
    """
    import matplotlib
    import matplotlib.font_manager as fm

    # 常见中文字体名称（按优先级排列）
    cjk_candidates = [
        "Microsoft YaHei", "SimHei", "SimSun", "KaiTi",
        "WenQuanYi Micro Hei", "Noto Sans CJK SC", "Noto Sans SC",
        "PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    cjk_font = next((f for f in cjk_candidates if f in available), None)

    if cjk_font is not None:
        matplotlib.rcParams["font.sans-serif"] = [cjk_font] + matplotlib.rcParams.get(
            "font.sans-serif", []
        )
        matplotlib.rcParams["axes.unicode_minus"] = False


def plot_stopping_boundaries(
    design: Dict[str, Any],
    z_stats: Optional[List[float]] = None,
    save_path: Optional[str] = None,
    figsize: Tuple[float, float] = (10, 6),
    dpi: int = 150,
) -> Any:
    """绘制停止边界图

    可视化成组序贯设计的优效性边界和无效性边界，以及实际检验统计量轨迹。

    Parameters
    ----------
    design : Dict[str, Any]
        成组序贯设计对象
    z_stats : Optional[List[float]]
        各次分析的实际检验统计量（用于叠加在图上）
    save_path : Optional[str]
        图片保存路径（如指定则保存为文件）
    figsize : Tuple[float, float]
        图形尺寸
    dpi : int
        分辨率

    Returns
    -------
    matplotlib.figure.Figure
        图形对象

    Examples
    --------
    >>> design = obrien_fleming_design(k_max=3, alpha=0.025)
    >>> fig = plot_stopping_boundaries(design, z_stats=[1.5, 2.2, 2.1])
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _setup_cjk_font()

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    info_rates = design["info_rates"]
    eff_bounds = design["efficacy_boundaries"]
    fut_bounds = design["futility_boundaries"]

    # 优效性边界
    ax.plot(
        info_rates, eff_bounds, "o-", color="#d62728", linewidth=2,
        markersize=8, label="优效性停止边界", zorder=3,
    )

    # 无效性边界
    if fut_bounds is not None:
        valid_fut = ~np.isnan(fut_bounds)
        ax.plot(
            info_rates[valid_fut], fut_bounds[valid_fut], "s--",
            color="#1f77b4", linewidth=2, markersize=8,
            label="无效性停止边界", zorder=3,
        )

    # 继续区域填充
    if fut_bounds is not None:
        valid_mask = ~np.isnan(fut_bounds)
        ax.fill_between(
            info_rates[valid_mask],
            fut_bounds[valid_mask],
            eff_bounds[valid_mask],
            alpha=0.08, color="#2ca02c", label="继续试验区域",
        )

    # 实际 Z 统计量
    if z_stats is not None:
        n_stats = len(z_stats)
        ax.plot(
            info_rates[:n_stats], z_stats, "D-",
            color="#ff7f0e", linewidth=2, markersize=10,
            label="实际检验统计量 Z", zorder=4,
        )
        # 标注数值
        for i, z in enumerate(z_stats):
            ax.annotate(
                f"Z={z:.2f}",
                (info_rates[i], z),
                textcoords="offset points",
                xytext=(10, 5),
                fontsize=9,
            )

    ax.set_xlabel("信息比例 (Information Fraction)", fontsize=12)
    ax.set_ylabel("检验统计量 Z", fontsize=12)
    ax.set_title(
        f"成组序贯设计停止边界（{design['design_type']}，"
        f"α={design['alpha']}，K={design['k_max']}）",
        fontsize=13,
    )
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1.05)
    ax.axhline(y=0, color="gray", linewidth=0.5, linestyle="-")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
    return fig


def plot_conditional_power(
    design: Dict[str, Any],
    look: int,
    z_range: Optional[Tuple[float, float]] = None,
    drift_scenarios: Optional[List[float]] = None,
    save_path: Optional[str] = None,
    figsize: Tuple[float, float] = (10, 6),
    dpi: int = 150,
) -> Any:
    """绘制条件把握度曲线

    展示给定信息比例下，条件把握度随期中检验统计量 Z 的变化，
    并对比不同漂移假设（H0、设计效应、观察效应）。

    Parameters
    ----------
    design : Dict[str, Any]
        成组序贯设计对象
    look : int
        期中分析序号（1-indexed）
    z_range : Optional[Tuple[float, float]]
        Z 轴范围，默认 (−1, 4)
    drift_scenarios : Optional[List[float]]
        漂移参数场景列表，默认 [0, drift_design, observed]
    save_path : Optional[str]
        图片保存路径
    figsize : Tuple[float, float]
        图形尺寸
    dpi : int
        分辨率

    Returns
    -------
    matplotlib.figure.Figure
        图形对象

    Examples
    --------
    >>> design = obrien_fleming_design(k_max=3, alpha=0.025)
    >>> fig = plot_conditional_power(design, look=1)
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _setup_cjk_font()

    k = look - 1
    t_interim = design["info_rates"][k]
    t_final = design["info_rates"][-1]
    boundary_final = design["efficacy_boundaries"][-1]
    drift_design = design["drift"]

    if z_range is None:
        z_range = (-1.0, 4.0)
    z_vals = np.linspace(z_range[0], z_range[1], 200)

    if drift_scenarios is None:
        drift_scenarios = [0.0, drift_design]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    colors = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"]
    labels = {
        0.0: "H0 (μ=0)",
        drift_design: f"设计效应 (μ={drift_design:.2f})",
    }

    for i, drift in enumerate(drift_scenarios):
        cp_vals = [
            conditional_power(z, t_interim, t_final, boundary_final, drift)
            for z in z_vals
        ]
        label = labels.get(drift, f"μ={drift:.2f}")
        ax.plot(
            z_vals, cp_vals, linewidth=2,
            color=colors[i % len(colors)], label=label,
        )

    # 参考线
    ax.axhline(y=0.8, color="gray", linestyle=":", linewidth=1, label="CP=80%")
    ax.axhline(y=0.2, color="gray", linestyle="--", linewidth=1, label="CP=20%（无效性阈值）")
    ax.axhline(y=0.5, color="gray", linestyle="-.", linewidth=0.5, alpha=0.5)

    # 标注无效性和优效性边界处的 CP
    eff_b = design["efficacy_boundaries"][k]
    ax.axvline(x=eff_b, color="#d62728", linestyle=":", linewidth=1, alpha=0.5)
    ax.annotate(
        f"优效性边界\nZ={eff_b:.2f}",
        (eff_b, 0.05),
        fontsize=8, color="#d62728", ha="center",
    )

    if design["futility_boundaries"] is not None:
        fut_b = design["futility_boundaries"][k]
        if not np.isnan(fut_b):
            ax.axvline(x=fut_b, color="#1f77b4", linestyle=":", linewidth=1, alpha=0.5)
            ax.annotate(
                f"无效性边界\nZ={fut_b:.2f}",
                (fut_b, 0.05),
                fontsize=8, color="#1f77b4", ha="center",
            )

    ax.set_xlabel("期中检验统计量 Z", fontsize=12)
    ax.set_ylabel("条件把握度 (Conditional Power)", fontsize=12)
    ax.set_title(
        f"条件把握度曲线（第 {look} 次期中分析，"
        f"信息比例={t_interim:.2f}）",
        fontsize=13,
    )
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(z_range)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
    return fig


# ============================================================================
# 示例
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger.info("=" * 72)
    logger.info("适应性设计与期中分析模板 — 示例演示")
    logger.info("=" * 72)

    # ----------------------------------------------------------------------
    # 示例 1: 成组序贯设计
    # ----------------------------------------------------------------------
    logger.info("\n[1] 成组序贯设计\n")

    # O'Brien-Fleming 设计
    design_of = obrien_fleming_design(
        k_max=3, alpha=0.025, beta=0.2, futility="non-binding"
    )
    logger.info("O'Brien-Fleming 设计:")
    logger.info(f"  分析次数: {design_of['k_max']}")
    logger.info(f"  信息比例: {design_of['info_rates']}")
    logger.info(f"  优效性边界: {design_of['efficacy_boundaries']}")
    logger.info(f"  无效性边界: {design_of['futility_boundaries']}")
    logger.info(f"  累积α消耗: {design_of['alpha_spent']}")
    logger.info(f"  实际把握度: {design_of['power']:.2%}")
    logger.info(f"  漂移参数: {design_of['drift']:.4f}")

    # Pocock 设计
    design_pk = pocock_design(
        k_max=3, alpha=0.025, beta=0.2, futility="non-binding"
    )
    logger.info("\nPocock 设计:")
    logger.info(f"  优效性边界: {design_pk['efficacy_boundaries']}")
    logger.info(f"  无效性边界: {design_pk['futility_boundaries']}")
    logger.info(f"  实际把握度: {design_pk['power']:.2%}")

    # Lan-DeMets 设计（非等距信息比例）
    design_ld = lan_demets_design(
        k_max=3, alpha=0.025, beta=0.2,
        info_rates=np.array([0.3, 0.7, 1.0]),
        spending_type="of",
    )
    logger.info("\nLan-DeMets 设计（非等距信息比例 [0.3, 0.7, 1.0]）:")
    logger.info(f"  优效性边界: {design_ld['efficacy_boundaries']}")
    logger.info(f"  累积α消耗: {design_ld['alpha_spent']}")

    # ----------------------------------------------------------------------
    # 示例 2: 期中分析决策
    # ----------------------------------------------------------------------
    logger.info("\n[2] 期中分析决策\n")

    # 模拟第 1 次期中分析，Z = 1.5
    decision1 = interim_decision(
        z_stat=1.5, look=1, design=design_of, n_obs=120, n_planned=300
    )
    logger.info("第 1 次期中分析 (Z=1.5):")
    logger.info(f"  决策: {decision1['decision']}")
    logger.info(f"  条件把握度: {decision1['conditional_power']:.2%}")
    logger.info(f"  建议: {decision1['recommendation']}")

    # 模拟第 1 次期中分析，Z = 3.0（超过优效性边界）
    decision2 = interim_decision(
        z_stat=3.0, look=1, design=design_of
    )
    logger.info("\n第 1 次期中分析 (Z=3.0):")
    logger.info(f"  决策: {decision2['decision']}")
    logger.info(f"  建议: {decision2['recommendation']}")

    # 模拟第 1 次期中分析，Z = -0.5（低于无效性边界）
    decision3 = interim_decision(
        z_stat=-0.5, look=1, design=design_of
    )
    logger.info("\n第 1 次期中分析 (Z=-0.5):")
    logger.info(f"  决策: {decision3['decision']}")
    logger.info(f"  建议: {decision3['recommendation']}")

    # ----------------------------------------------------------------------
    # 示例 3: 条件把握度与样本量重新估计
    # ----------------------------------------------------------------------
    logger.info("\n[3] 条件把握度与样本量重新估计\n")

    # 条件把握度（不同漂移假设）
    t_interim = design_of["info_rates"][0]
    t_final = design_of["info_rates"][-1]
    b_final = design_of["efficacy_boundaries"][-1]

    for drift_label, drift_val in [
        ("H0 (μ=0)", 0.0),
        ("设计效应", design_of["drift"]),
        ("观察效应", 1.5 / np.sqrt(t_interim)),
    ]:
        cp = conditional_power(1.5, t_interim, t_final, b_final, drift_val)
        logger.info(f"  Z=1.5, {drift_label} (μ={drift_val:.3f}): CP = {cp:.2%}")

    # 盲态样本量重新估计
    ssr = blinded_sample_size_reestimation(
        n_obs=100, pooled_sd=12.5, effect_size=5.0,
        alpha=0.025, power=0.8,
    )
    logger.info("\n  盲态样本量重新估计:")
    logger.info(f"    合并SD={ssr['pooled_sd']}, 效应量={ssr['effect_size']}")
    logger.info(f"    标准化效应量(d)={ssr['standardized_effect']:.4f}")
    logger.info(f"    重新估计每组样本量: {ssr['n_per_group_reestimated']}")
    logger.info(f"    重新估计总样本量: {ssr['n_total_reestimated']}")

    # 基于条件把握度的样本量重新估计
    cpr = conditional_power_reestimation(
        z_interim=1.2, t_interim=0.5, design=design_of, target_cp=0.8
    )
    logger.info("\n  条件把握度样本量重新估计 (Z=1.2, t=0.5):")
    logger.info(f"    当前CP(观察效应): {cpr['cp_current']:.2%}")
    logger.info(f"    当前CP(设计效应): {cpr['cp_design']:.2%}")
    logger.info(f"    当前CP(H0): {cpr['cp_null']:.2%}")
    logger.info(f"    样本量膨胀因子: {cpr['n_inflation_factor']:.2f}")
    logger.info(f"    建议: {cpr['recommendation']}")

    # ----------------------------------------------------------------------
    # 示例 4: 适应性随机化
    # ----------------------------------------------------------------------
    logger.info("\n[4] 适应性随机化\n")

    # 随机化胜者分配
    rpw = randomized_play_the_winner(
        n=100, p_success_a=0.3, p_success_b=0.6, random_seed=42
    )
    logger.info("  随机化胜者分配 (RPW):")
    logger.info(f"    A组: n={rpw['n_a']}, 成功={rpw['success_a']} "
          f"({rpw['success_a']/max(rpw['n_a'],1):.1%})")
    logger.info(f"    B组: n={rpw['n_b']}, 成功={rpw['success_b']} "
          f"({rpw['success_b']/max(rpw['n_b'],1):.1%})")
    logger.info(f"    分配比(B/A): {rpw['allocation_ratio']:.2f}")

    # 最小化随机化
    factors = np.array([
        [0, 0, 0], [1, 1, 0], [0, 2, 1], [1, 0, 1],
        [0, 1, 0], [1, 2, 1], [0, 0, 1], [1, 1, 0],
        [0, 2, 0], [1, 0, 1],
    ])
    minim = minimization_randomization(factors, n_treatments=2, random_seed=42)
    logger.info("\n  最小化随机化:")
    logger.info(f"    分配序列: {minim['assignments']}")
    logger.info(f"    最终不平衡量: {minim['final_imbalance']:.1f}")

    # ----------------------------------------------------------------------
    # 示例 5: 多重性校正
    # ----------------------------------------------------------------------
    logger.info("\n[5] 多重性校正\n")

    # α 消耗函数
    as_corr = alpha_spending_correction(looks=3, alpha=0.025, spending_type="of")
    logger.info("  α消耗函数校正 (3次分析, OF型):")
    logger.info(f"    累积α: {as_corr['alpha_cumulative']}")
    logger.info(f"    增量α: {as_corr['alpha_incremental']}")

    # 封闭检验程序
    pvals = np.array([0.01, 0.04, 0.03])
    for method in ["bonferroni", "simes"]:
        ct = closed_testing_procedure(pvals, alpha=0.05, local_test=method)
        logger.info(f"\n  封闭检验 ({method}):")
        logger.info(f"    p值: {pvals}")
        logger.info(f"    调整p值: {ct['adjusted_p_values'].round(4)}")
        logger.info(f"    拒绝: {ct['rejected']}")

    # ----------------------------------------------------------------------
    # 示例 6: 报告生成
    # ----------------------------------------------------------------------
    logger.info("\n[6] 报告生成\n")

    report = generate_interim_report(
        design=design_of,
        interim_results=[decision1],
        study_info={
            "study_title": "示例临床试验",
            "study_id": "EX-001",
            "sponsor": "示例申办方",
            "report_date": "2026-06-19",
        },
    )
    logger.info("report[:500]")
    logger.info("  ...（报告已生成，完整内容见返回字符串）")

    # ----------------------------------------------------------------------
    # 示例 7: 可视化
    # ----------------------------------------------------------------------
    logger.info("\n[7] 可视化\n")

    # 停止边界图
    fig1 = plot_stopping_boundaries(
        design_of, z_stats=[1.5, 2.2, 2.1],
        save_path="stopping_boundaries_demo.png",
    )
    logger.info("  停止边界图已生成: stopping_boundaries_demo.png")

    # 条件把握度曲线
    fig2 = plot_conditional_power(
        design_of, look=1,
        save_path="conditional_power_demo.png",
    )
    logger.info("  条件把握度曲线已生成: conditional_power_demo.png")

    logger.info("\n" + "=" * 72)
    logger.info("示例演示完成")
    logger.info("=" * 72)
