"""
overlapping_weighting_template.py — Overlapping Weighting 模板（Python）
=========================================================================
适用于：观察性研究的因果推断、混杂调整

Overlapping Weighting (OW) 是 IPTW 的替代方案，通过 overlap weight 使
倾向性评分分布在处理组和对照组之间最大化重叠，从而：
  1. 自动截断极端权重（PS→0 或 PS→1 的个体权重趋于 0）
  2. 减少方差膨胀，比 IPTW 更稳健
  3. 估计的是 ETTE（Effect in the Treated and Control）即 overlap population 的效应

参考：
  - Li, Morgan, Zaslavsky (2018). Overlapping weighting: a more
    balanced and efficient approach to causal inference with
    propensity scores. Statistics in Medicine.
  - Li & Thomas (2019). Sensitivity analysis for sensitivity analysis
    for causal inference with overlap weights.

依赖: numpy, pandas, sklearn, scipy, matplotlib, statsmodels
安装: pip install numpy pandas sklearn scipy matplotlib statsmodels

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
import logging

logger = logging.getLogger(__name__)

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. Overlapping Weight 计算
# ============================================================================


def compute_overlap_weights(
    ps: np.ndarray,
    treatment: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """计算 Overlapping Weight (OW)

    OW 权重公式:
      - 处理组: w_i = 1 - PS_i
      - 对照组: w_i = PS_i

    这使得两组权重分布最大化重叠，自动截断极端 PS 值。

    Parameters
    ----------
    ps : np.ndarray
        倾向性评分 (0-1)
    treatment : np.ndarray
        处理变量 (0/1)

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (加权后的处理组权重, 加权后的对照组权重)
        每个权重已归一化，使得加权后样本量等效于原始样本量
    """
    treatment = np.asarray(treatment)
    ps = np.asarray(ps)

    # 基础 OW 权重
    w = np.where(treatment == 1, 1 - ps, ps)

    # 归一化: 使得加权后处理组和对照组的有效样本量之和 = N
    # 即 sum(w * treatment) + sum(w * (1-treatment)) = N
    n_treated = treatment.sum()
    n_control = (1 - treatment).sum()

    w_treated = np.where(treatment == 1, w / n_treated * n_treated, 0)
    w_control = np.where(treatment == 0, w / n_control * n_control, 0)

    return w_treated, w_control


def compute_overlap_weights_simple(
    ps: np.ndarray,
    treatment: np.ndarray,
) -> np.ndarray:
    """计算简化的 Overlapping Weight

    返回统一的权重向量（不区分组别归一化），
    适用于 weighted regression。

    Parameters
    ----------
    ps : np.ndarray
        倾向性评分 (0-1)
    treatment : np.ndarray
        处理变量 (0/1)

    Returns
    -------
    np.ndarray
        OW 权重: 处理组=1-PS, 对照组=PS
    """
    treatment = np.asarray(treatment)
    ps = np.asarray(ps)
    return np.where(treatment == 1, 1 - ps, ps)


# ============================================================================
# 2. 倾向性评分估计（复用 psm_template 的逻辑）
# ============================================================================


def estimate_propensity(
    df: pd.DataFrame,
    treatment_col: str,
    covariate_cols: List[str],
    cat_vars: Optional[List[str]] = None,
) -> pd.DataFrame:
    """估计倾向性评分（Logistic 回归）

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    treatment_col : str
        处理变量（0/1）
    covariate_cols : List[str]
        协变量列表
    cat_vars : Optional[List[str]]
        分类变量（将自动 one-hot 编码）

    Returns
    -------
    pd.DataFrame
        包含 ps_score 列的数据副本
    """
    data = df.copy()

    if cat_vars:
        data = pd.get_dummies(data, columns=cat_vars, drop_first=True)
        covariate_cols = [c for c in data.columns if c != treatment_col]

    X = data[covariate_cols].fillna(data[covariate_cols].median())
    y = data[treatment_col]

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X, y)
    data["ps_score"] = model.predict_proba(X)[:, 1]

    # C-statistic
    from sklearn.metrics import roc_auc_score
    c_stat = roc_auc_score(y, data["ps_score"])
    logger.info(f"  C-statistic (AUC): {c_stat:.3f}")

    return data


# ============================================================================
# 3. 平衡诊断
# ============================================================================


def balance_check(
    data: pd.DataFrame,
    treatment_col: str,
    covariate_cols: List[str],
    weight_col: Optional[str] = None,
) -> pd.DataFrame:
    """加权平衡诊断

    Parameters
    ----------
    data : pd.DataFrame
        数据
    treatment_col : str
        处理变量
    covariate_cols : List[str]
        协变量
    weight_col : Optional[str]
        权重列名（None 时使用原始数据）

    Returns
    -------
    pd.DataFrame
        平衡诊断表（SMD 和方差比）
    """
    if weight_col and weight_col in data.columns:
        weights = data[weight_col].values
        w_t = weights[data[treatment_col] == 1]
        w_c = weights[data[treatment_col] == 0]
    else:
        w_t = None
        w_c = None

    treated = data[data[treatment_col] == 1]
    control = data[data[treatment_col] == 0]

    results = []
    for var in covariate_cols:
        t_vals = treated[var].dropna().values
        c_vals = control[var].dropna().values

        if w_t is not None:
            t_w = w_t[treated[var].dropna().index]
            c_w = w_c[control[var].dropna().index]
            # 加权均值和方差
            t_mean = np.average(t_vals, weights=t_w)
            c_mean = np.average(c_vals, weights=c_w)
            t_var = np.average((t_vals - t_mean)**2, weights=t_w)
            c_var = np.average((c_vals - c_mean)**2, weights=c_w)
        else:
            t_mean = np.mean(t_vals)
            c_mean = np.mean(c_vals)
            t_var = np.var(t_vals, ddof=1)
            c_var = np.var(c_vals, ddof=1)

        pooled_sd = np.sqrt((t_var + c_var) / 2)
        smd = (t_mean - c_mean) / pooled_sd if pooled_sd > 0 else 0
        var_ratio = t_var / c_var if c_var > 0 else np.nan

        results.append({
            "Variable": var,
            "Treated_Mean": t_mean,
            "Control_Mean": c_mean,
            "SMD": abs(smd),
            "Var_Ratio": var_ratio,
            "Balance": "✅" if abs(smd) < 0.1 else ("⚠️" if abs(smd) < 0.2 else "❌"),
        })

    return pd.DataFrame(results)


def love_plot(
    balance_before: pd.DataFrame,
    balance_after: pd.DataFrame,
    title: str = "Covariate Balance (Love Plot) — Overlapping Weighting",
    figsize: Tuple[float, float] = (8, 6),
) -> plt.Figure:
    """Love Plot: 加权前后的 SMD 对比"""
    fig, ax = plt.subplots(figsize=figsize)
    y_pos = range(len(balance_before))

    ax.scatter(balance_before["SMD"], y_pos,
               color="red", alpha=0.6, s=40, label="Before Weighting")
    ax.scatter(balance_after["SMD"], y_pos,
               color="steelblue", alpha=0.8, s=40, label="After OW Weighting")
    ax.axvline(x=0.1, linestyle="--", color="grey", alpha=0.5, label="SMD=0.1")
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(balance_before["Variable"])
    ax.set_xlabel("Absolute Standardized Mean Difference")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3, linestyle=":")
    ax.invert_yaxis()
    plt.tight_layout()
    return fig


# ============================================================================
# 4. 加权效应估计
# ============================================================================


def weighted_ate(
    data: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    weight_col: str,
    outcome_type: str = "continuous",
) -> Dict:
    """加权平均处理效应估计

    Parameters
    ----------
    data : pd.DataFrame
        含权重的数据
    treatment_col : str
        处理变量
    outcome_col : str
        结局变量
    weight_col : str
        权重列
    outcome_type : str
        'continuous' 或 'binary'

    Returns
    -------
    Dict
        ATE 估计结果
    """
    import statsmodels.api as sm

    w = data[weight_col].values

    if outcome_type == "continuous":
        # 加权线性回归
        X = sm.add_constant(data[[treatment_col]].values)
        model = sm.WLS(data[outcome_col].values, X, weights=w).fit()
        ate = model.params[1]
        se = model.bse[1]
        ci = model.conf_int().iloc[1]
        p_val = model.pvalues[1]
    elif outcome_type == "binary":
        # 加权 Logistic 回归
        X = sm.add_constant(data[[treatment_col]].values)
        model = sm.GLM(data[outcome_col].values, X,
                        family=sm.families.Binomial(),
                        freq_weights=w).fit()
        ate_or = np.exp(model.params[1])
        se = model.bse[1]
        ci_or = np.exp(model.conf_int().iloc[1])
        p_val = model.pvalues[1]
        return {
            "OR": ate_or,
            "OR_CI_lower": ci_or[0],
            "OR_CI_upper": ci_or[1],
            "p_value": p_val,
            "method": "Weighted Logistic regression",
            "outcome_type": "binary",
        }
    else:
        raise ValueError(f"Unsupported outcome_type: {outcome_type}")

    return {
        "ATE": ate,
        "SE": se,
        "CI_lower": ci[0],
        "CI_upper": ci[1],
        "p_value": p_val,
        "method": "Weighted OLS regression",
        "outcome_type": "continuous",
    }


# ============================================================================
# 5. OW vs IPTW 对比
# ============================================================================


def compare_ow_iptw(
    data: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    covariate_cols: List[str],
    outcome_type: str = "continuous",
) -> Dict:
    """OW 与 IPTW 的对比分析

    Parameters
    ----------
    data : pd.DataFrame
        原始数据
    treatment_col : str
        处理变量
    outcome_col : str
        结局变量
    covariate_cols : List[str]
        协变量
    outcome_type : str
        结局类型

    Returns
    -------
    Dict
        包含 OW 和 IPTW 的结果对比
    """
    # PS 估计
    data_ps = estimate_propensity(data, treatment_col, covariate_cols)

    ps = data_ps["ps_score"].values
    treatment = data_ps[treatment_col].values

    # --- OW ---
    ow_weights = compute_overlap_weights_simple(ps, treatment)
    data_ps["ow_weight"] = ow_weights

    balance_ow_before = balance_check(data_ps, treatment_col, covariate_cols)
    balance_ow_after = balance_check(data_ps, treatment_col, covariate_cols, "ow_weight")
    ate_ow = weighted_ate(data_ps, treatment_col, outcome_col, "ow_weight", outcome_type)

    # --- IPTW ---
    iptw_weights = np.where(treatment == 1, 1 / ps, 1 / (1 - ps))
    # 截断极端权重 (1st-99th percentile)
    p1, p99 = np.percentile(iptw_weights, [1, 99])
    iptw_weights_clipped = np.clip(iptw_weights, p1, p99)
    data_ps["iptw_weight"] = iptw_weights_clipped

    balance_iptw_before = balance_check(data_ps, treatment_col, covariate_cols)
    balance_iptw_after = balance_check(data_ps, treatment_col, covariate_cols, "iptw_weight")
    ate_iptw = weighted_ate(data_ps, treatment_col, outcome_col, "iptw_weight", outcome_type)

    # --- 对比 ---
    logger.info("\n" + "=" * 60)
    logger.info("OW vs IPTW 对比")
    logger.info("=" * 60)

    if outcome_type == "continuous":
        logger.info(f"  OW  ATE = {ate_ow['ATE']:.4f} (95% CI: {ate_ow['CI_lower']:.4f}, "
                    f"{ate_ow['CI_upper']:.4f}, p = {ate_ow['p_value']:.4f})")
        logger.info(f"  IPTW ATE = {ate_iptw['ATE']:.4f} (95% CI: {ate_iptw['CI_lower']:.4f}, "
                    f"{ate_iptw['CI_upper']:.4f}, p = {ate_iptw['p_value']:.4f})")
    else:
        logger.info(f"  OW  OR = {ate_ow['OR']:.3f} (95% CI: {ate_ow['OR_CI_lower']:.3f}, "
                    f"{ate_ow['OR_CI_upper']:.3f}, p = {ate_ow['p_value']:.4f})")
        logger.info(f"  IPTW OR = {ate_iptw['OR']:.3f} (95% CI: {ate_iptw['OR_CI_lower']:.3f}, "
                    f"{ate_iptw['OR_CI_upper']:.3f}, p = {ate_iptw['p_value']:.4f})")

    # 权重分布
    logger.info(f"\n  OW 权重分布: min={ow_weights.min():.4f}, "
                f"median={np.median(ow_weights):.4f}, max={ow_weights.max():.4f}")
    logger.info(f"  IPTW 权重分布 (clipped): min={iptw_weights_clipped.min():.4f}, "
                f"median={np.median(iptw_weights_clipped):.4f}, max={iptw_weights_clipped.max():.4f}")

    return {
        "ow": {
            "weights": ow_weights,
            "balance_before": balance_ow_before,
            "balance_after": balance_ow_after,
            "ate": ate_ow,
        },
        "iptw": {
            "weights": iptw_weights_clipped,
            "balance_before": balance_iptw_before,
            "balance_after": balance_iptw_after,
            "ate": ate_iptw,
        },
        "data": data_ps,
    }


# ============================================================================
# 6. 权重分布可视化
# ============================================================================


def plot_weight_comparison(
    ow_weights: np.ndarray,
    iptw_weights: np.ndarray,
    treatment: np.ndarray,
    figsize: Tuple[float, float] = (12, 5),
) -> plt.Figure:
    """OW vs IPTW 权重分布对比图

    Parameters
    ----------
    ow_weights : np.ndarray
        OW 权重
    iptw_weights : np.ndarray
        IPTW 权重（已截断）
    treatment : np.ndarray
        处理变量
    figsize : Tuple[float, float]
        图片尺寸

    Returns
    -------
    plt.Figure
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    treatment = np.asarray(treatment)

    # OW 权重分布
    ax1 = axes[0]
    ax1.hist(ow_weights[treatment == 1], bins=30, alpha=0.6,
             color="steelblue", label="Treated", density=True)
    ax1.hist(ow_weights[treatment == 0], bins=30, alpha=0.6,
             color="coral", label="Control", density=True)
    ax1.set_xlabel("Overlap Weight")
    ax1.set_ylabel("Density")
    ax1.set_title("OW Weight Distribution")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # IPTW 权重分布
    ax2 = axes[1]
    ax2.hist(iptw_weights[treatment == 1], bins=30, alpha=0.6,
             color="steelblue", label="Treated", density=True)
    ax2.hist(iptw_weights[treatment == 0], bins=30, alpha=0.6,
             color="coral", label="Control", density=True)
    ax2.set_xlabel("IPTW Weight")
    ax2.set_ylabel("Density")
    ax2.set_title("IPTW Weight Distribution (clipped)")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.suptitle("Weight Distribution Comparison: OW vs IPTW",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return fig


# ============================================================================
# 7. 完整 OW 工作流
# ============================================================================


def full_ow_workflow(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    covariate_cols: List[str],
    cat_vars: Optional[List[str]] = None,
    outcome_type: str = "continuous",
    compare_iptw: bool = True,
) -> Dict:
    """完整 Overlapping Weighting 工作流

    步骤: PS 估计 → OW 权重 → 平衡诊断 → 效应估计 → (可选) IPTW 对比

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    treatment_col : str
        处理变量
    outcome_col : str
        结局变量
    covariate_cols : List[str]
        协变量
    cat_vars : Optional[List[str]]
        分类变量
    outcome_type : str
        结局类型
    compare_iptw : bool
        是否与 IPTW 对比

    Returns
    -------
    Dict
        完整分析结果
    """
    results = {}

    # Step 1: PS 估计
    logger.info("=" * 60)
    logger.info("Step 1: 估计倾向性评分")
    logger.info("=" * 60)
    data_ps = estimate_propensity(df, treatment_col, covariate_cols, cat_vars)
    results["ps_data"] = data_ps

    # Step 2: 计算 OW 权重
    logger.info("\n" + "=" * 60)
    logger.info("Step 2: 计算 Overlapping Weight")
    logger.info("=" * 60)
    ps = data_ps["ps_score"].values
    treatment = data_ps[treatment_col].values
    ow_weights = compute_overlap_weights_simple(ps, treatment)
    data_ps["ow_weight"] = ow_weights
    results["ow_weights"] = ow_weights

    logger.info(f"  OW 权重分布: min={ow_weights.min():.4f}, "
                f"median={np.median(ow_weights):.4f}, max={ow_weights.max():.4f}")

    # Step 3: 平衡诊断
    logger.info("\n" + "=" * 60)
    logger.info("Step 3: 平衡诊断")
    logger.info("=" * 60)
    balance_before = balance_check(data_ps, treatment_col, covariate_cols)
    balance_after = balance_check(data_ps, treatment_col, covariate_cols, "ow_weight")
    results["balance_before"] = balance_before
    results["balance_after"] = balance_after

    if len(balance_before) == len(balance_after):
        results["love_plot"] = love_plot(balance_before, balance_after)

    # Step 4: 效应估计
    logger.info("\n" + "=" * 60)
    logger.info("Step 4: 加权效应估计 (OW)")
    logger.info("=" * 60)
    ate_ow = weighted_ate(data_ps, treatment_col, outcome_col, "ow_weight", outcome_type)
    results["ate_ow"] = ate_ow

    if outcome_type == "continuous":
        logger.info(f"  ATE (OW) = {ate_ow['ATE']:.4f} "
                    f"(95% CI: {ate_ow['CI_lower']:.4f}, {ate_ow['CI_upper']:.4f}, "
                    f"p = {ate_ow['p_value']:.4f})")
    else:
        logger.info(f"  OR (OW) = {ate_ow['OR']:.3f} "
                    f"(95% CI: {ate_ow['OR_CI_lower']:.3f}, {ate_ow['OR_CI_upper']:.3f}, "
                    f"p = {ate_ow['p_value']:.4f})")

    # Step 5: (可选) IPTW 对比
    if compare_iptw:
        logger.info("\n" + "=" * 60)
        logger.info("Step 5: IPTW 对比分析")
        logger.info("=" * 60)
        iptw_weights = np.where(treatment == 1, 1 / ps, 1 / (1 - ps))
        p1, p99 = np.percentile(iptw_weights, [1, 99])
        iptw_weights_clipped = np.clip(iptw_weights, p1, p99)
        data_ps["iptw_weight"] = iptw_weights_clipped

        ate_iptw = weighted_ate(data_ps, treatment_col, outcome_col,
                                "iptw_weight", outcome_type)
        results["ate_iptw"] = ate_iptw

        balance_iptw = balance_check(data_ps, treatment_col, covariate_cols, "iptw_weight")
        results["balance_iptw"] = balance_iptw

        # 权重对比图
        results["weight_plot"] = plot_weight_comparison(
            ow_weights, iptw_weights_clipped, treatment)

        if outcome_type == "continuous":
            logger.info(f"  ATE (IPTW) = {ate_iptw['ATE']:.4f} "
                        f"(95% CI: {ate_iptw['CI_lower']:.4f}, {ate_iptw['CI_upper']:.4f}, "
                        f"p = {ate_iptw['p_value']:.4f})")
        else:
            logger.info(f"  OR (IPTW) = {ate_iptw['OR']:.3f} "
                        f"(95% CI: {ate_iptw['OR_CI_lower']:.3f}, {ate_iptw['OR_CI_upper']:.3f}, "
                        f"p = {ate_iptw['p_value']:.4f})")

    results["data"] = data_ps

    logger.info("\n✅ Overlapping Weighting 分析完成")
    return results


# ============================================================================
# 8. 报告模板
# ============================================================================


def generate_ow_report(results: Dict) -> str:
    """生成 OW 分析的统计方法学描述

    Parameters
    ----------
    results : Dict
        full_ow_workflow 的输出

    Returns
    -------
    str
        可直接插入论文 Methods 段落的文本
    """
    ate = results["ate_ow"]
    outcome_type = ate.get("outcome_type", "continuous")

    lines = [
        "倾向性评分采用 Logistic 回归模型估计，纳入以下协变量：",
        f"{', '.join(results.get('balance_before', pd.DataFrame())['Variable'].tolist())}。",
        "",
        "采用 Overlapping Weighting (OW) 方法进行因果效应估计 [Li et al., 2018]。",
        "与传统 IPTW 不同，OW 通过 overlap weight（处理组权重=1-PS，对照组权重=PS）",
        "使两组倾向性评分分布最大化重叠，从而自动截断极端权重，减少方差膨胀。",
        "",
    ]

    if outcome_type == "continuous":
        lines.append(
            f"主要分析采用加权最小二乘回归估计平均处理效应 (ATE)。"
            f"OW 加权后 ATE = {ate['ATE']:.4f} "
            f"(95% CI: {ate['CI_lower']:.4f}–{ate['CI_upper']:.4f}, "
            f"p = {ate['p_value']:.4f})。"
        )
    else:
        lines.append(
            f"主要分析采用加权 Logistic 回归估计比值比 (OR)。"
            f"OW 加权后 OR = {ate['OR']:.3f} "
            f"(95% CI: {ate['OR_CI_lower']:.3f}–{ate['OR_CI_upper']:.3f}, "
            f"p = {ate['p_value']:.4f})。"
        )

    if "ate_iptw" in results:
        ate_iptw = results["ate_iptw"]
        lines.extend([
            "",
            "作为敏感性分析，同时采用逆概率加权 (IPTW) 方法，",
            "权重截断至第 1–99 百分位以减少极端权重影响。",
            "协变量平衡通过标准化差异 (SMD) 评估，SMD < 0.1 视为平衡良好。",
        ])

    return "\n".join(lines)


# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    np.random.seed(42)
    n = 500

    # 模拟观察性数据
    age = np.random.normal(60, 10, n)
    bmi = np.random.normal(26, 5, n)
    smoking = np.random.binomial(1, 0.3, n)

    # 处理分配（受协变量影响 → 存在混杂）
    logit_treat = -2 + 0.03 * age + 0.05 * bmi + 0.5 * smoking
    prob_treat = 1 / (1 + np.exp(-logit_treat))
    treatment = np.random.binomial(1, prob_treat)

    # 连续结局
    outcome = 50 + 0.5 * treatment + 0.2 * age + 0.3 * bmi + 2.0 * smoking + np.random.normal(0, 5, n)

    df = pd.DataFrame({
        "treatment": treatment,
        "outcome": outcome,
        "age": age,
        "bmi": bmi,
        "smoking": smoking,
    })

    logger.info(f"模拟数据: N={n}, 处理组={treatment.sum()}, 对照组={n - treatment.sum()}")
    logger.info("")

    # 运行完整 OW 工作流
    results = full_ow_workflow(
        df, treatment_col="treatment", outcome_col="outcome",
        covariate_cols=["age", "bmi", "smoking"],
        outcome_type="continuous",
        compare_iptw=True,
    )

    # 打印平衡诊断
    logger.info("\n=== 加权前平衡诊断 ===")
    logger.info(results["balance_before"].to_string(index=False))
    logger.info("\n=== 加权后平衡诊断 (OW) ===")
    logger.info(results["balance_after"].to_string(index=False))

    if "balance_iptw" in results:
        logger.info("\n=== 加权后平衡诊断 (IPTW) ===")
        logger.info(results["balance_iptw"].to_string(index=False))

    # 生成方法学描述
    report = generate_ow_report(results)
    logger.info("\n=== 统计方法学描述 ===")
    logger.info("report")

    logger.info("\n✅ Overlapping Weighting 完整分析完成")
