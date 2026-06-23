"""
regression_discontinuity_template.py — 断点回归分析模板
==========================================================
适用于：断点回归设计（RD）的因果效应估计、设计验证、
       最优带宽选择、模糊 RD、敏感性分析

依赖: rdrobust, numpy, pandas, matplotlib, scipy
安装: pip install rdrobust numpy pandas matplotlib scipy

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
import logging

logger = logging.getLogger(__name__)

# 延迟导入 rdrobust（在函数内部导入），以便模块在缺少依赖时仍可加载

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. RD 设计验证
# ============================================================================


def density_test(
    df: pd.DataFrame,
    running_var: str,
    cutoff: float = 0.0,
    n_bins: int = 30,
) -> Dict[str, Any]:
    """McCrary 密度检验（操纵检验）

    检验断点处运行变量的密度是否存在跳跃，以排除样本操纵。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    running_var : str
        运行变量（驱动变量）名
    cutoff : float
        断点值（默认 0）
    n_bins : int
        直方图分组数

    Returns
    -------
    Dict[str, Any]
        包含检验统计量、p 值和判断结果

    Examples
    --------
    >>> result = density_test(df, 'score', cutoff=50)
    >>> print(f"p-value = {result['p_value']:.4f}")
    """
    x = df[running_var].dropna().values
    x_centered = x - cutoff

    # 分箱
    bins = np.linspace(x_centered.min(), x_centered.max(), n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    # 分别计算断点左右的密度
    left_mask = bin_centers < 0
    right_mask = bin_centers >= 0

    counts, _ = np.histogram(x_centered, bins=bins)
    bin_width = bins[1] - bins[0]

    # 简化的 McCrary 检验
    # 比较断点左右紧邻的密度
    n_left = np.sum(x_centered < 0)
    n_right = np.sum(x_centered >= 0)

    # 使用局部线性回归估计断点处的密度跳跃
    # 简化方法：比较断点附近两侧的频率
    bandwidth = np.percentile(np.abs(x_centered), 25)  # 使用 25% 分位数作为带宽
    near_left = x_centered[(x_centered >= -bandwidth) & (x_centered < 0)]
    near_right = x_centered[(x_centered >= 0) & (x_centered <= bandwidth)]

    density_left = len(near_left) / (bandwidth * n_left) if n_left > 0 else 0
    density_right = len(near_right) / (bandwidth * n_right) if n_right > 0 else 0

    # 对数密度差
    if density_left > 0 and density_right > 0:
        log_diff = np.log(density_right) - np.log(density_left)
        # 标准误（近似）
        se = np.sqrt(1 / len(near_left) + 1 / len(near_right)) if len(near_left) > 0 and len(near_right) > 0 else 1
        z_stat = log_diff / se if se > 0 else 0
        p_value = 2 * stats.norm.sf(abs(z_stat))
    else:
        log_diff = np.nan
        z_stat = np.nan
        p_value = np.nan

    result = {
        "log_density_diff": float(log_diff) if not np.isnan(log_diff) else None,
        "z_statistic": float(z_stat) if not np.isnan(z_stat) else None,
        "p_value": float(p_value) if not np.isnan(p_value) else None,
        "density_left": density_left,
        "density_right": density_right,
        "n_left": n_left,
        "n_right": n_right,
        "bandwidth": bandwidth,
        "manipulation_detected": (not np.isnan(p_value)) and (p_value < 0.05),
        "method": "McCrary density test (simplified)",
    }

    logger.info(f"  对数密度差: {log_diff:.4f}" if not np.isnan(log_diff) else "  对数密度差: N/A")
    logger.info(f"  z 统计量: {z_stat:.4f}" if not np.isnan(z_stat) else "  z 统计量: N/A")
    logger.info(f"  p 值: {p_value:.4f}" if not np.isnan(p_value) else "  p 值: N/A")
    logger.info(f"  操纵检测: {'是' if result['manipulation_detected'] else '否'}")

    if result["manipulation_detected"]:
        warnings.warn(
            "McCrary 检验检测到可能的样本操纵（p < 0.05）。"
            "断点处的样本可能非随机分布，RD 设计的有效性可能受影响。",
            RuntimeWarning,
        )

    return result


def covariate_balance_test(
    df: pd.DataFrame,
    running_var: str,
    cutoff: float,
    covariates: List[str],
    bandwidth: Optional[float] = None,
) -> pd.DataFrame:
    """协变量平衡检验

    检验断点处协变量是否平衡（即协变量在断点处不应有跳跃）。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    running_var : str
        运行变量名
    cutoff : float
        断点值
    covariates : List[str]
        协变量列表
    bandwidth : Optional[float]
        带宽（默认自动选择）

    Returns
    -------
    pd.DataFrame
        各协变量的平衡检验结果

    Examples
    --------
    >>> result = covariate_balance_test(df, 'score', 50, ['age', 'sex'])
    """
    data = df.copy()
    data["_x_centered"] = data[running_var] - cutoff

    if bandwidth is None:
        bandwidth = np.percentile(np.abs(data["_x_centered"]), 25)

    results = []
    for cov in covariates:
        # 在断点附近进行局部线性回归
        subset = data[np.abs(data["_x_centered"]) <= bandwidth].dropna(subset=[cov])

        if len(subset) < 10:
            results.append({
                "Covariate": cov,
                "RD_Estimate": np.nan,
                "SE": np.nan,
                "p_value": np.nan,
                "Balanced": "Insufficient data",
            })
            continue

        # 简单的局部线性回归
        from numpy.polynomial import polynomial as P

        left = subset[subset["_x_centered"] < 0]
        right = subset[subset["_x_centered"] >= 0]

        if len(left) < 5 or len(right) < 5:
            results.append({
                "Covariate": cov,
                "RD_Estimate": np.nan,
                "SE": np.nan,
                "p_value": np.nan,
                "Balanced": "Insufficient data",
            })
            continue

        # 左侧线性回归
        X_left = np.column_stack([np.ones(len(left)), left["_x_centered"]])
        beta_left = np.linalg.lstsq(X_left, left[cov], rcond=None)[0]

        # 右侧线性回归
        X_right = np.column_stack([np.ones(len(right)), right["_x_centered"]])
        beta_right = np.linalg.lstsq(X_right, right[cov], rcond=None)[0]

        # 断点处的跳跃
        rd_estimate = beta_right[0] - beta_left[0]

        # 标准误（近似）
        resid_left = left[cov] - X_left @ beta_left
        resid_right = right[cov] - X_right @ beta_right
        se_left = np.sqrt(np.var(resid_left) / len(left))
        se_right = np.sqrt(np.var(resid_right) / len(right))
        se = np.sqrt(se_left ** 2 + se_right ** 2)

        z_stat = rd_estimate / se if se > 0 else 0
        p_value = 2 * stats.norm.sf(abs(z_stat))

        balanced = p_value >= 0.05

        results.append({
            "Covariate": cov,
            "RD_Estimate": round(rd_estimate, 4),
            "SE": round(se, 4),
            "p_value": round(p_value, 4),
            "Balanced": "Yes" if balanced else "No (jump detected)",
        })

    return pd.DataFrame(results)


# ============================================================================
# 2. 局部线性回归估计
# ============================================================================


def rd_estimate(
    df: pd.DataFrame,
    outcome: str,
    running_var: str,
    cutoff: float = 0.0,
    bandwidth: Optional[float] = None,
    kernel: str = "triangular",
    p: int = 1,
    covariates: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """局部线性回归 RD 估计

    使用 rdrobust 进行断点回归的局部多项式估计。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    running_var : str
        运行变量名
    cutoff : float
        断点值（默认 0）
    bandwidth : Optional[float]
        带宽（默认使用 IK 最优带宽）
    kernel : str
        核函数: 'triangular'（默认）、'uniform'、'epanechnikov'
    p : int
        多项式阶数（默认 1，局部线性）
    covariates : Optional[List[str]]
        协变量列表

    Returns
    -------
    Dict[str, Any]
        包含 RD 估计值、标准误、置信区间、带宽等

    Examples
    --------
    >>> result = rd_estimate(df, 'outcome', 'score', cutoff=50)
    >>> print(f"RD effect = {result['estimate']:.4f}")
    """
    try:
        from rdrobust import rdrobust
    except ImportError:
        # 回退到手动实现
        return _rd_estimate_manual(df, outcome, running_var, cutoff,
                                   bandwidth, kernel, p, covariates)

    data = df[[outcome, running_var] + (covariates or [])].dropna()
    y = data[outcome].values
    x = data[running_var].values

    kwargs = {
        "c": cutoff,
        "kernel": kernel,
        "p": p,
    }
    if bandwidth is not None:
        kwargs["h"] = bandwidth
    if covariates:
        kwargs["covs"] = data[covariates].values

    rd_result = rdrobust(y=y, x=x, **kwargs)

    # 提取结果
    estimate = float(rd_result.coef.iloc[0, 0]) if hasattr(rd_result.coef, 'iloc') else float(rd_result.coef[0])
    se = float(rd_result.se.iloc[0, 0]) if hasattr(rd_result.se, 'iloc') else float(rd_result.se[0])
    ci_lower = float(rd_result.ci.iloc[0, 0]) if hasattr(rd_result.ci, 'iloc') else float(rd_result.ci[0, 0])
    ci_upper = float(rd_result.ci.iloc[0, 1]) if hasattr(rd_result.ci, 'iloc') else float(rd_result.ci[0, 1])
    z_stat = estimate / se if se > 0 else 0
    p_value = 2 * stats.norm.sf(abs(z_stat))

    # 带宽
    try:
        h = float(rd_result.bws.iloc[0, 0]) if hasattr(rd_result.bws, 'iloc') else float(rd_result.bws[0])
    except Exception:
        h = bandwidth if bandwidth else np.nan

    result = {
        "estimate": estimate,
        "se": se,
        "z_statistic": z_stat,
        "p_value": p_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "bandwidth": h,
        "kernel": kernel,
        "poly_order": p,
        "n_obs": len(data),
        "n_left": int(np.sum(x < cutoff)),
        "n_right": int(np.sum(x >= cutoff)),
        "method": f"rdrobust (kernel={kernel}, p={p})",
        "rd_result": rd_result,
    }

    logger.info(f"  RD 估计值: {estimate:.4f}")
    logger.info(f"  标准误: {se:.4f}")
    logger.info(f"  95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    logger.info(f"  z 统计量: {z_stat:.4f}")
    logger.info(f"  p 值: {p_value:.4f}")
    logger.info(f"  带宽: {h:.4f}")
    logger.info(f"  有效样本: 左 {result['n_left']}, 右 {result['n_right']}")

    return result


def _rd_estimate_manual(
    df, outcome, running_var, cutoff, bandwidth, kernel, p, covariates
):
    """手动实现的局部线性 RD 估计（当 rdrobust 不可用时）"""
    data = df[[outcome, running_var]].dropna()
    y = data[outcome].values
    x = data[running_var].values - cutoff

    if bandwidth is None:
        # IK 带宽的简化近似
        bandwidth = np.percentile(np.abs(x), 25) * 2

    # 权重函数
    def _weights(x, h, kernel):
        u = x / h
        if kernel == "triangular":
            w = np.maximum(0, 1 - np.abs(u))
        elif kernel == "uniform":
            w = (np.abs(u) <= 1).astype(float)
        elif kernel == "epanechnikov":
            w = np.maximum(0, 1 - u ** 2)
        else:
            w = (np.abs(u) <= 1).astype(float)
        return w

    # 左侧回归
    left_mask = (x < 0) & (np.abs(x) <= bandwidth)
    right_mask = (x >= 0) & (x <= bandwidth)

    w_left = _weights(x[left_mask], bandwidth, kernel)
    w_right = _weights(x[right_mask], bandwidth, kernel)

    # 构建设计矩阵（局部线性: 截距 + x）
    X_left = np.column_stack([np.ones(left_mask.sum()), x[left_mask]])
    X_right = np.column_stack([np.ones(right_mask.sum()), x[right_mask]])

    # 加权最小二乘
    W_left = np.diag(w_left)
    W_right = np.diag(w_right)

    beta_left = np.linalg.solve(
        X_left.T @ W_left @ X_left, X_left.T @ W_left @ y[left_mask]
    )
    beta_right = np.linalg.solve(
        X_right.T @ W_right @ X_right, X_right.T @ W_right @ y[right_mask]
    )

    # RD 估计 = 右侧截距 - 左侧截距
    estimate = beta_right[0] - beta_left[0]

    # 标准误
    resid_left = y[left_mask] - X_left @ beta_left
    resid_right = y[right_mask] - X_right @ beta_right
    sigma2_left = np.sum(w_left * resid_left ** 2) / np.sum(w_left)
    sigma2_right = np.sum(w_right * resid_right ** 2) / np.sum(w_right)

    var_left = sigma2_left * np.linalg.inv(X_left.T @ W_left @ X_left)[0, 0]
    var_right = sigma2_right * np.linalg.inv(X_right.T @ W_right @ X_right)[0, 0]
    se = np.sqrt(var_left + var_right)

    z_stat = estimate / se if se > 0 else 0
    p_value = 2 * stats.norm.sf(abs(z_stat))

    result = {
        "estimate": float(estimate),
        "se": float(se),
        "z_statistic": float(z_stat),
        "p_value": float(p_value),
        "ci_lower": float(estimate - 1.96 * se),
        "ci_upper": float(estimate + 1.96 * se),
        "bandwidth": float(bandwidth),
        "kernel": kernel,
        "poly_order": p,
        "n_obs": len(data),
        "n_left": int(left_mask.sum()),
        "n_right": int(right_mask.sum()),
        "method": f"Manual local linear (kernel={kernel}, p={p})",
    }

    logger.info(f"  RD 估计值: {estimate:.4f}")
    logger.info(f"  标准误: {se:.4f}")
    logger.info(f"  95% CI: [{result['ci_lower']:.4f}, {result['ci_upper']:.4f}]")
    logger.info(f"  p 值: {p_value:.4f}")
    logger.info(f"  带宽: {bandwidth:.4f}")

    return result


# ============================================================================
# 3. 最优带宽选择
# ============================================================================


def optimal_bandwidth(
    df: pd.DataFrame,
    outcome: str,
    running_var: str,
    cutoff: float = 0.0,
    kernel: str = "triangular",
) -> Dict[str, Any]:
    """最优带宽选择（Imbens-Kalyanaraman, IK）

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    running_var : str
        运行变量名
    cutoff : float
        断点值
    kernel : str
        核函数

    Returns
    -------
    Dict[str, Any]
        包含最优带宽和相关信息

    Examples
    --------
    >>> bw = optimal_bandwidth(df, 'outcome', 'score', cutoff=50)
    >>> print(f"Optimal bandwidth = {bw['bandwidth']:.4f}")
    """
    try:
        from rdrobust import rdbwselect
        data = df[[outcome, running_var]].dropna()
        y = data[outcome].values
        x = data[running_var].values

        bw_result = rdbwselect(y=y, x=x, c=cutoff, kernel=kernel)
        try:
            h = float(bw_result.bws.iloc[0, 0]) if hasattr(bw_result.bws, 'iloc') else float(bw_result.bws[0])
        except Exception:
            h = float(bw_result.bws[0])

        result = {
            "bandwidth": h,
            "method": "Imbens-Kalyanaraman (IK)",
            "kernel": kernel,
            "cutoff": cutoff,
        }
    except ImportError:
        # 手动 IK 带宽选择（简化）
        data = df[[outcome, running_var]].dropna()
        y = data[outcome].values
        x = data[running_var].values - cutoff

        # IK 带宽的简化实现
        # 1. 估计条件方差和密度
        n = len(y)
        left = x < 0
        right = x >= 0

        # 局部线性回归的残差方差
        if left.sum() > 10 and right.sum() > 10:
            from numpy.polynomial import polynomial as P
            # 左侧
            X_l = np.column_stack([np.ones(left.sum()), x[left]])
            beta_l = np.linalg.lstsq(X_l, y[left], rcond=None)[0]
            resid_l = y[left] - X_l @ beta_l
            sigma2_l = np.var(resid_l)

            # 右侧
            X_r = np.column_stack([np.ones(right.sum()), x[right]])
            beta_r = np.linalg.lstsq(X_r, y[right], rcond=None)[0]
            resid_r = y[right] - X_r @ beta_r
            sigma2_r = np.var(resid_r)

            # 密度估计（简化）
            range_x = x.max() - x.min()
            f_c = n / range_x  # 断点处的近似密度

            # IK 带宽公式（简化）
            # h_IK ~ C * (sigma^2 / (f_c * (f'(c+) - f'(c-))^2))^(1/5) * n^(-1/5)
            # 这里使用简化版本
            sigma2 = (sigma2_l + sigma2_r) / 2
            h = 3.56 * (sigma2 / (f_c + 1e-10)) ** 0.2 * n ** (-0.2) * range_x ** 0.4
            h = max(h, np.percentile(np.abs(x), 10))  # 最小带宽
        else:
            h = np.percentile(np.abs(x), 25)

        result = {
            "bandwidth": float(h),
            "method": "Imbens-Kalyanaraman (IK, simplified)",
            "kernel": kernel,
            "cutoff": cutoff,
        }

    logger.info(f"  最优带宽 (IK): {result['bandwidth']:.4f}")
    return result


# ============================================================================
# 4. 模糊 RD（Fuzzy RD）
# ============================================================================


def fuzzy_rd_estimate(
    df: pd.DataFrame,
    outcome: str,
    treatment: str,
    running_var: str,
    cutoff: float = 0.0,
    bandwidth: Optional[float] = None,
    kernel: str = "triangular",
) -> Dict[str, Any]:
    """模糊断点回归（Fuzzy RD）估计

    在模糊 RD 设计中，断点处处理状态不完全确定，
    使用断点作为工具变量进行 2SLS 估计。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    treatment : str
        处理变量名（0/1）
    running_var : str
        运行变量名
    cutoff : float
        断点值
    bandwidth : Optional[float]
        带宽
    kernel : str
        核函数

    Returns
    -------
    Dict[str, Any]
        包含模糊 RD 估计值（LATE）、第一阶段结果等

    Examples
    --------
    >>> result = fuzzy_rd_estimate(df, 'y', 'treated', 'score', cutoff=50)
    >>> print(f"Fuzzy RD LATE = {result['late']:.4f}")
    """
    data = df[[outcome, treatment, running_var]].dropna()
    y = data[outcome].values
    d = data[treatment].values
    x = data[running_var].values - cutoff

    if bandwidth is None:
        bw_result = optimal_bandwidth(df, outcome, running_var, cutoff, kernel)
        bandwidth = bw_result["bandwidth"]

    # 权重
    def _weights(x, h, kernel):
        u = x / h
        if kernel == "triangular":
            return np.maximum(0, 1 - np.abs(u))
        elif kernel == "uniform":
            return (np.abs(u) <= 1).astype(float)
        elif kernel == "epanechnikov":
            return np.maximum(0, 1 - u ** 2)
        return (np.abs(u) <= 1).astype(float)

    w = _weights(x, bandwidth, kernel)
    mask = w > 0

    x_m = x[mask]
    y_m = y[mask]
    d_m = d[mask]
    w_m = w[mask]

    left = x_m < 0
    right = x_m >= 0

    # 简化估计: LATE = (E[Y|X=0+] - E[Y|X=0-]) / (E[D|X=0+] - E[D|X=0-])
    # 即 reduced form / first stage

    # Reduced form: 结局变量在断点处的跳跃
    rf_left = _local_linear_intercept(x_m[left], y_m[left], w_m[left])
    rf_right = _local_linear_intercept(x_m[right], y_m[right], w_m[right])
    reduced_form = rf_right - rf_left

    # First stage: 处理变量在断点处的跳跃
    fs_left = _local_linear_intercept(x_m[left], d_m[left], w_m[left])
    fs_right = _local_linear_intercept(x_m[right], d_m[right], w_m[right])
    first_stage = fs_right - fs_left

    # LATE = reduced_form / first_stage
    if abs(first_stage) > 1e-10:
        late = reduced_form / first_stage
    else:
        late = np.nan
        warnings.warn(
            "第一阶段跳跃接近零，模糊 RD 估计不可靠。"
            "断点处处理状态变化不显著。",
            RuntimeWarning,
        )

    # 标准误（简化: Delta 方法）
    n_eff = mask.sum()
    se_rf = np.std(y_m) / np.sqrt(n_eff)
    se_fs = np.std(d_m) / np.sqrt(n_eff)
    if abs(first_stage) > 1e-10:
        se_late = abs(late) * np.sqrt(
            (se_rf / reduced_form) ** 2 + (se_fs / first_stage) ** 2
        ) if abs(reduced_form) > 1e-10 else se_rf / abs(first_stage)
    else:
        se_late = np.nan

    z_stat = late / se_late if se_late and se_late > 0 else 0
    p_value = 2 * stats.norm.sf(abs(z_stat)) if z_stat else np.nan

    result = {
        "late": float(late) if not np.isnan(late) else None,
        "se": float(se_late) if not np.isnan(se_late) else None,
        "z_statistic": float(z_stat) if z_stat else None,
        "p_value": float(p_value) if not np.isnan(p_value) else None,
        "ci_lower": float(late - 1.96 * se_late) if not np.isnan(late) and not np.isnan(se_late) else None,
        "ci_upper": float(late + 1.96 * se_late) if not np.isnan(late) and not np.isnan(se_late) else None,
        "reduced_form": float(reduced_form),
        "first_stage": float(first_stage),
        "bandwidth": float(bandwidth),
        "kernel": kernel,
        "n_obs": int(mask.sum()),
        "method": "Fuzzy RD (Wald estimator)",
    }

    logger.info(f"  模糊 RD LATE: {late:.4f}" if not np.isnan(late) else "  模糊 RD LATE: N/A")
    logger.info(f"  Reduced form: {reduced_form:.4f}")
    logger.info(f"  First stage: {first_stage:.4f}")
    logger.info(f"  带宽: {bandwidth:.4f}")

    return result


def _local_linear_intercept(x, y, w):
    """加权局部线性回归在 x=0 处的截距"""
    if len(x) < 3:
        return np.mean(y) if len(y) > 0 else 0
    X = np.column_stack([np.ones(len(x)), x])
    W = np.diag(w)
    try:
        beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
        return beta[0]
    except np.linalg.LinAlgError:
        return np.average(y, weights=w)


# ============================================================================
# 5. 平滑性检验
# ============================================================================


def smoothness_test(
    df: pd.DataFrame,
    outcome: str,
    running_var: str,
    cutoff: float = 0.0,
    bandwidth: Optional[float] = None,
    n_placebo_cutoffs: int = 5,
) -> Dict[str, Any]:
    """平滑性检验（安慰剂断点检验）

    在非真实断点处检验是否存在虚假的跳跃，验证结局变量在断点处的跳跃不是偶然现象。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    running_var : str
        运行变量名
    cutoff : float
        真实断点值
    bandwidth : Optional[float]
        带宽
    n_placebo_cutoffs : int
        安慰剂断点数

    Returns
    -------
    Dict[str, Any]
        包含各安慰剂断点的检验结果

    Examples
    --------
    >>> result = smoothness_test(df, 'y', 'score', cutoff=50)
    >>> print(result['placebo_results'])
    """
    data = df[[outcome, running_var]].dropna()
    x_range = (data[running_var].min(), data[running_var].max())

    # 选择安慰剂断点（远离真实断点）
    placebo_cutoffs = np.linspace(
        x_range[0] + 0.2 * (cutoff - x_range[0]),
        x_range[1] - 0.2 * (x_range[1] - cutoff),
        n_placebo_cutoffs,
    )
    # 排除接近真实断点的点
    placebo_cutoffs = [c for c in placebo_cutoffs if abs(c - cutoff) > 0.1 * (x_range[1] - x_range[0])]

    placebo_results = []
    for pc in placebo_cutoffs:
        try:
            est = rd_estimate(data, outcome, running_var, cutoff=pc,
                              bandwidth=bandwidth, kernel="triangular")
            placebo_results.append({
                "placebo_cutoff": float(pc),
                "estimate": est["estimate"],
                "se": est["se"],
                "p_value": est["p_value"],
                "significant": est["p_value"] < 0.05,
            })
        except Exception as e:
            placebo_results.append({
                "placebo_cutoff": float(pc),
                "estimate": np.nan,
                "se": np.nan,
                "p_value": np.nan,
                "significant": False,
                "error": str(e),
            })

    placebo_df = pd.DataFrame(placebo_results)
    n_significant = placebo_df["significant"].sum()

    result = {
        "placebo_results": placebo_df,
        "n_placebo_cutoffs": len(placebo_cutoffs),
        "n_significant": int(n_significant),
        "smoothness_confirmed": n_significant <= 1,  # 最多 1 个显著（5% 水平下的偶然）
        "real_cutoff": cutoff,
    }

    logger.info(f"  安慰剂断点数: {len(placebo_cutoffs)}")
    logger.info(f"  显著的安慰剂断点: {n_significant}")
    logger.info(f"  平滑性确认: {'是' if result['smoothness_confirmed'] else '否'}")

    if not result["smoothness_confirmed"]:
        warnings.warn(
            "多个安慰剂断点处检测到显著跳跃，结局变量可能在其他位置也存在不连续，"
            "RD 设计的有效性可能受影响。",
            RuntimeWarning,
        )

    return result


# ============================================================================
# 6. 敏感性分析（带宽敏感性）
# ============================================================================


def bandwidth_sensitivity(
    df: pd.DataFrame,
    outcome: str,
    running_var: str,
    cutoff: float = 0.0,
    bandwidth_multipliers: Optional[List[float]] = None,
    kernel: str = "triangular",
) -> pd.DataFrame:
    """带宽敏感性分析

    在不同带宽下重复 RD 估计，检验结果的稳健性。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    running_var : str
        运行变量名
    cutoff : float
        断点值
    bandwidth_multipliers : Optional[List[float]]
        带宽乘数列表（相对于最优带宽），默认 [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    kernel : str
        核函数

    Returns
    -------
    pd.DataFrame
        各带宽下的 RD 估计结果

    Examples
    --------
    >>> result = bandwidth_sensitivity(df, 'y', 'score', cutoff=50)
    >>> print(result)
    """
    if bandwidth_multipliers is None:
        bandwidth_multipliers = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

    # 获取最优带宽
    bw_opt = optimal_bandwidth(df, outcome, running_var, cutoff, kernel)
    h_opt = bw_opt["bandwidth"]

    results = []
    for mult in bandwidth_multipliers:
        h = h_opt * mult
        try:
            est = rd_estimate(df, outcome, running_var, cutoff,
                              bandwidth=h, kernel=kernel)
            results.append({
                "bandwidth_multiplier": mult,
                "bandwidth": round(h, 4),
                "estimate": round(est["estimate"], 4),
                "se": round(est["se"], 4),
                "ci_lower": round(est["ci_lower"], 4),
                "ci_upper": round(est["ci_upper"], 4),
                "p_value": round(est["p_value"], 4),
                "n_left": est["n_left"],
                "n_right": est["n_right"],
                "significant": est["p_value"] < 0.05,
            })
        except Exception as e:
            results.append({
                "bandwidth_multiplier": mult,
                "bandwidth": round(h, 4),
                "estimate": np.nan,
                "se": np.nan,
                "ci_lower": np.nan,
                "ci_upper": np.nan,
                "p_value": np.nan,
                "n_left": 0,
                "n_right": 0,
                "significant": False,
                "error": str(e),
            })

    return pd.DataFrame(results)


# ============================================================================
# 7. 可视化
# ============================================================================


def plot_rd(
    df: pd.DataFrame,
    outcome: str,
    running_var: str,
    cutoff: float = 0.0,
    bandwidth: Optional[float] = None,
    n_bins: int = 20,
    figsize: Tuple[float, float] = (10, 6),
) -> "matplotlib.figure.Figure":
    """绘制 RD 散点图和拟合线

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    running_var : str
        运行变量名
    cutoff : float
        断点值
    bandwidth : Optional[float]
        带宽（用于标注）
    n_bins : int
        分箱数
    figsize : Tuple[float, float]
        图形大小

    Returns
    -------
    matplotlib.figure.Figure
        RD 图

    Examples
    --------
    >>> fig = plot_rd(df, 'y', 'score', cutoff=50)
    """
    import matplotlib.pyplot as plt

    data = df[[outcome, running_var]].dropna()
    x = data[running_var].values
    y = data[outcome].values
    x_centered = x - cutoff

    fig, ax = plt.subplots(figsize=figsize)

    # 分箱均值
    left = x_centered < 0
    right = x_centered >= 0

    for mask, color, label in [(left, "#3498db", "Below cutoff"),
                                (right, "#e74c3c", "Above cutoff")]:
        if mask.sum() == 0:
            continue
        x_sub = x_centered[mask]
        y_sub = y[mask]

        # 分箱
        bins = np.linspace(x_sub.min(), x_sub.max(), n_bins // 2 + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        bin_means = []
        bin_ses = []
        for i in range(len(bins) - 1):
            in_bin = (x_sub >= bins[i]) & (x_sub < bins[i + 1])
            if in_bin.sum() > 0:
                bin_means.append(np.mean(y_sub[in_bin]))
                bin_ses.append(np.std(y_sub[in_bin]) / np.sqrt(in_bin.sum()))
            else:
                bin_means.append(np.nan)
                bin_ses.append(0)

        ax.errorbar(bin_centers + cutoff, bin_means, yerr=bin_ses,
                    fmt="o", color=color, alpha=0.6, markersize=5,
                    capsize=3, label=label)

        # 局部线性拟合线
        X_fit = np.column_stack([np.ones(mask.sum()), x_sub])
        beta = np.linalg.lstsq(X_fit, y_sub, rcond=None)[0]
        x_line = np.linspace(x_sub.min(), x_sub.max(), 100)
        y_line = beta[0] + beta[1] * x_line
        ax.plot(x_line + cutoff, y_line, color=color, linewidth=2)

    # 断点线
    ax.axvline(x=cutoff, color="black", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.annotate("Cutoff", xy=(cutoff, ax.get_ylim()[1]),
                xytext=(cutoff + 0.02 * (x.max() - x.min()), ax.get_ylim()[1] * 0.95),
                fontsize=10, fontweight="bold")

    if bandwidth:
        ax.axvspan(cutoff - bandwidth, cutoff + bandwidth,
                   alpha=0.1, color="grey", label=f"BW={bandwidth:.2f}")

    ax.set_xlabel(running_var)
    ax.set_ylabel(outcome)
    ax.set_title("Regression Discontinuity Plot", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3, linestyle=":")

    plt.tight_layout()
    return fig


# ============================================================================
# 8. 完整 RD 工作流
# ============================================================================


def full_rd_workflow(
    df: pd.DataFrame,
    outcome: str,
    running_var: str,
    cutoff: float = 0.0,
    covariates: Optional[List[str]] = None,
    treatment: Optional[str] = None,
    do_sensitivity: bool = True,
    do_plots: bool = True,
) -> Dict[str, Any]:
    """完整的断点回归分析工作流

    执行：密度检验 → 协变量平衡 → 最优带宽 → RD 估计 →
         （模糊 RD）→ 平滑性检验 → 带宽敏感性 → 可视化

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    running_var : str
        运行变量名
    cutoff : float
        断点值
    covariates : Optional[List[str]]
        协变量列表
    treatment : Optional[str]
        处理变量名（模糊 RD 时提供）
    do_sensitivity : bool
        是否执行敏感性分析
    do_plots : bool
        是否生成可视化

    Returns
    -------
    Dict[str, Any]
        包含所有分析结果

    Examples
    --------
    >>> results = full_rd_workflow(df, 'y', 'score', cutoff=50)
    """
    results = {}

    # Step 1: 密度检验
    logger.info("=" * 50)
    logger.info("Step 1: McCrary 密度检验（操纵检验）")
    logger.info("=" * 50)
    results["density_test"] = density_test(df, running_var, cutoff)

    # Step 2: 协变量平衡检验
    if covariates:
        logger.info("\n" + "=" * 50)
        logger.info("Step 2: 协变量平衡检验")
        logger.info("=" * 50)
        results["covariate_balance"] = covariate_balance_test(
            df, running_var, cutoff, covariates
        )
        logger.info(results["covariate_balance"].to_string(index=False))

    # Step 3: 最优带宽
    logger.info("\n" + "=" * 50)
    logger.info("Step 3: 最优带宽选择")
    logger.info("=" * 50)
    bw = optimal_bandwidth(df, outcome, running_var, cutoff)
    results["optimal_bandwidth"] = bw

    # Step 4: RD 估计
    logger.info("\n" + "=" * 50)
    logger.info("Step 4: RD 估计（局部线性回归）")
    logger.info("=" * 50)
    rd_est = rd_estimate(df, outcome, running_var, cutoff,
                         bandwidth=bw["bandwidth"], covariates=covariates)
    results["rd_estimate"] = rd_est

    # Step 5: 模糊 RD（如果提供了处理变量）
    if treatment:
        logger.info("\n" + "=" * 50)
        logger.info("Step 5: 模糊 RD 估计")
        logger.info("=" * 50)
        fuzzy = fuzzy_rd_estimate(df, outcome, treatment, running_var, cutoff,
                                  bandwidth=bw["bandwidth"])
        results["fuzzy_rd"] = fuzzy

    # Step 6: 平滑性检验
    logger.info("\n" + "=" * 50)
    logger.info("Step 6: 平滑性检验（安慰剂断点）")
    logger.info("=" * 50)
    smooth = smoothness_test(df, outcome, running_var, cutoff,
                             bandwidth=bw["bandwidth"])
    results["smoothness_test"] = smooth

    # Step 7: 带宽敏感性
    if do_sensitivity:
        logger.info("\n" + "=" * 50)
        logger.info("Step 7: 带宽敏感性分析")
        logger.info("=" * 50)
        sensitivity = bandwidth_sensitivity(df, outcome, running_var, cutoff,
                                            kernel="triangular")
        results["bandwidth_sensitivity"] = sensitivity
        logger.info(sensitivity[["bandwidth_multiplier", "bandwidth", "estimate",
                           "se", "p_value", "significant"]].to_string(index=False))

    # Step 8: 可视化
    if do_plots:
        logger.info("\n" + "=" * 50)
        logger.info("Step 8: 可视化")
        logger.info("=" * 50)
        results["rd_plot"] = plot_rd(df, outcome, running_var, cutoff,
                                     bandwidth=bw["bandwidth"])
        logger.info("  RD 图已生成")

    logger.info("\n 断点回归分析完成")
    return results


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 模拟 RD 数据
    np.random.seed(42)
    n = 1000

    # 运行变量（标准化考试分数）
    score = np.random.normal(50, 15, n)

    # 断点: score = 50
    cutoff = 50
    treated = (score >= cutoff).astype(int)

    # 结局变量: 在断点处有跳跃（真实效应 = 5.0）
    y = 10 + 0.3 * (score - cutoff) + 5.0 * treated + np.random.normal(0, 3, n)

    # 协变量（不应在断点处跳跃）
    age = 60 + 0.1 * (score - cutoff) + np.random.normal(0, 8, n)
    bmi = 25 + 0.05 * (score - cutoff) + np.random.normal(0, 4, n)

    df = pd.DataFrame({
        "outcome": y,
        "score": score,
        "treated": treated,
        "age": age,
        "bmi": bmi,
    })

    # RD 估计
    logger.info("=" * 60)
    logger.info("RD 估计（局部线性回归）")
    logger.info("=" * 60)
    rd_est = rd_estimate(df, "outcome", "score", cutoff=cutoff)
    logger.info(f"\n  RD 效应: {rd_est['estimate']:.4f} (真实值: 5.0)")

    # 密度检验
    logger.info("\n" + "=" * 60)
    logger.info("McCrary 密度检验")
    logger.info("=" * 60)
    density = density_test(df, "score", cutoff=cutoff)

    # 协变量平衡
    logger.info("\n" + "=" * 60)
    logger.info("协变量平衡检验")
    logger.info("=" * 60)
    balance = covariate_balance_test(df, "score", cutoff, ["age", "bmi"])
    logger.info("balance.to_string(index=False)")

    # 带宽敏感性
    logger.info("\n" + "=" * 60)
    logger.info("带宽敏感性分析")
    logger.info("=" * 60)
    sensitivity = bandwidth_sensitivity(df, "outcome", "score", cutoff=cutoff)
    logger.info("%s %s %s %s", sensitivity[["bandwidth_multiplier", "estimate", "se", "p_value"]].to_string(index=False))

    # 模糊 RD
    logger.info("\n" + "=" * 60)
    logger.info("模糊 RD 估计")
    logger.info("=" * 60)
    # 创建不完全遵从的处理变量
    compliance = np.random.binomial(1, 0.8, n)  # 80% 遵从
    df["treated_fuzzy"] = treated * compliance
    fuzzy = fuzzy_rd_estimate(df, "outcome", "treated_fuzzy", "score", cutoff=cutoff)
    logger.info(f"\n  模糊 RD LATE: {fuzzy['late']:.4f}" if fuzzy['late'] else "  N/A")

    logger.info("\n 断点回归分析模板示例完成")
