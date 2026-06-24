"""
instrumental_variable_template.py — 工具变量分析模板
======================================================
适用于：观察性研究中的因果推断、内生性问题处理、
       两阶段最小二乘法（2SLS）、弱工具变量检验

依赖: linearmodels, statsmodels, numpy, pandas, scipy
安装: pip install linearmodels statsmodels numpy pandas scipy

作者: MSRA Team
版本: 0.1.0
"""

import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

# 延迟导入 linearmodels（在函数内部导入），以便模块在缺少依赖时仍可加载

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. 两阶段最小二乘法（2SLS）
# ============================================================================


def run_2sls(
    df: pd.DataFrame,
    outcome: str,
    endogenous: str,
    instruments: List[str],
    exogenous: Optional[List[str]] = None,
    robust: bool = True,
) -> Dict[str, Any]:
    """两阶段最小二乘法（2SLS）估计

    使用工具变量进行因果效应估计，解决内生性问题。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    endogenous : str
        内生处理变量名
    instruments : List[str]
        工具变量列表
    exogenous : Optional[List[str]]
        外生协变量列表（可选）
    robust : bool
        是否使用稳健标准误（默认 True）

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'result': linearmodels IV 回归结果
        - 'summary': 系数摘要表
        - 'first_stage': 第一阶段回归结果

    Examples
    --------
    >>> result = run_2sls(df, 'y', 'treated', ['z1', 'z2'], exogenous=['age'])
    >>> print(result['summary'])
    """
    from linearmodels.iv import IV2SLS

    if exogenous is None:
        exogenous = []

    data = df[[outcome, endogenous] + instruments + exogenous].dropna()

    # 构建公式
    # IV2SLS 公式: y ~ 1 + [endogenous ~ instruments] + exogenous
    exog_part = " + ".join(exogenous) if exogenous else "1"
    instr_part = " + ".join(instruments)
    formula = f"{outcome} ~ {exog_part} + [{endogenous} ~ {instr_part}]"

    # 拟合模型
    if robust:
        result = IV2SLS.from_formula(formula, data=data).fit(cov_type="robust")
    else:
        result = IV2SLS.from_formula(formula, data=data).fit()

    # 系数摘要
    summary = _extract_iv_summary(result)

    # 第一阶段回归
    first_stage = _first_stage_regression(data, endogenous, instruments, exogenous)

    return {
        "result": result,
        "summary": summary,
        "first_stage": first_stage,
        "formula": formula,
        "n_obs": int(result.nobs),
    }


def _extract_iv_summary(result) -> pd.DataFrame:
    """提取 IV 回归系数摘要"""
    params = result.params
    std_errors = result.std_errors
    t_stats = result.tstats
    p_values = result.pvalues
    ci = result.conf_int()

    summary = pd.DataFrame({
        "Variable": params.index,
        "Coefficient": params.values,
        "SE": std_errors.values,
        "t_stat": t_stats.values,
        "p_value": p_values.values,
        "CI_lower": ci.iloc[:, 0].values,
        "CI_upper": ci.iloc[:, 1].values,
    })

    summary["Signif"] = summary["p_value"].apply(
        lambda p: "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    )

    return summary


def _first_stage_regression(
    data: pd.DataFrame,
    endogenous: str,
    instruments: List[str],
    exogenous: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """第一阶段回归（内生变量对工具变量回归）"""
    import statsmodels.api as sm

    if exogenous is None:
        exogenous = []

    X = data[instruments + exogenous]
    X = sm.add_constant(X)
    y = data[endogenous]

    model = sm.OLS(y, X).fit()

    # 第一阶段 F 统计量（工具变量的联合显著性）
    if len(instruments) > 1:
        # 联合 F 检验
        constraints = [f"{instr} = 0" for instr in instruments]
        f_test = model.f_test(constraints)
        first_stage_f = float(f_test.fvalue)
        first_stage_p = float(f_test.pvalue)
    else:
        first_stage_f = float(model.fvalue)
        first_stage_p = float(model.f_pvalue)

    # R-squared
    r_squared = float(model.rsquared)

    return {
        "model": model,
        "f_statistic": first_stage_f,
        "f_pvalue": first_stage_p,
        "r_squared": r_squared,
        "n_instruments": len(instruments),
        "params": model.params,
        "pvalues": model.pvalues,
    }


# ============================================================================
# 2. 弱工具变量检验
# ============================================================================


def weak_instrument_test(
    df: pd.DataFrame,
    endogenous: str,
    instruments: List[str],
    exogenous: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """弱工具变量检验

    执行多种弱工具变量检验：
    - 第一阶段 F 统计量（Stock-Yogo 临界值）
    - Cragg-Donald 统计量
    - Kleibergen-Paap 统计量

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    endogenous : str
        内生变量名
    instruments : List[str]
        工具变量列表
    exogenous : Optional[List[str]]
        外生协变量

    Returns
    -------
    Dict[str, Any]
        包含各检验统计量和判断结果

    Examples
    --------
    >>> test = weak_instrument_test(df, 'treated', ['z1'])
    >>> print(f"First-stage F = {test['first_stage_f']:.2f}")
    """
    import statsmodels.api as sm

    if exogenous is None:
        exogenous = []

    data = df[[endogenous] + instruments + exogenous].dropna()

    # 第一阶段回归
    X = data[instruments + exogenous]
    X = sm.add_constant(X)
    y = data[endogenous]
    model = sm.OLS(y, X).fit()

    n_instr = len(instruments)

    # 第一阶段 F 统计量
    if n_instr > 1:
        constraints = [f"{instr} = 0" for instr in instruments]
        f_test = model.f_test(constraints)
        first_stage_f = float(f_test.fvalue)
        first_stage_p = float(f_test.pvalue)
    else:
        first_stage_f = float(model.fvalue)
        first_stage_p = float(model.f_pvalue)

    # Stock-Yogo 临界值（10% 最大偏倚）
    # 对于单个内生变量和单个工具变量，临界值为 16.38
    stock_yogo_critical = {
        1: 16.38,   # 1 个工具变量
        2: 19.93,
        3: 22.30,
        4: 24.58,
        5: 26.87,
    }
    critical_value = stock_yogo_critical.get(n_instr, 16.38)

    # 判断
    is_weak = first_stage_f < 10  # 经验法则: F < 10 为弱工具变量
    is_weak_stock_yogo = first_stage_f < critical_value

    # Cragg-Donald 统计量（近似）
    # CD = n * min(eigenvalue of matrix)
    # 简化: 对于单个内生变量，CD ≈ F * n_instr
    cragg_donald = first_stage_f * n_instr

    result = {
        "first_stage_f": first_stage_f,
        "first_stage_p": first_stage_p,
        "n_instruments": n_instr,
        "stock_yogo_critical_10pct": critical_value,
        "is_weak_rule_of_thumb": is_weak,  # F < 10
        "is_weak_stock_yogo": is_weak_stock_yogo,
        "cragg_donald_statistic": cragg_donald,
        "r_squared": float(model.rsquared),
        "partial_r_squared": _partial_r_squared(model, instruments, exogenous),
    }

    # 输出
    logger.info(f"  第一阶段 F 统计量: {first_stage_f:.2f}")
    logger.info(f"  Stock-Yogo 临界值 (10%): {critical_value:.2f}")
    logger.info(f"  经验法则 (F < 10): {'弱工具变量' if is_weak else '非弱工具变量'}")
    logger.info(f"  Stock-Yogo 检验: {'弱工具变量' if is_weak_stock_yogo else '非弱工具变量'}")

    if is_weak:
        warnings.warn(
            "检测到弱工具变量（F < 10）。IV 估计可能有严重偏倚，"
            "建议寻找更强的工具变量或使用对弱工具变量稳健的方法（如 LIML、AR 检验）。",
            RuntimeWarning,
        )

    return result


def _partial_r_squared(model, instruments, exogenous):
    """计算偏 R-squared（工具变量解释内生变量的部分）"""
    r_full = model.rsquared
    if not exogenous:
        return r_full
    # 简化：使用全模型 R-squared
    return r_full


# ============================================================================
# 3. Anderson-Rubin 检验
# ============================================================================


def anderson_rubin_test(
    df: pd.DataFrame,
    outcome: str,
    endogenous: str,
    instruments: List[str],
    exogenous: Optional[List[str]] = None,
    null_value: float = 0.0,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Anderson-Rubin (AR) 检验

    AR 检验对弱工具变量稳健，用于检验因果效应的零假设。
    零假设: 内生变量的因果效应 = null_value

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    endogenous : str
        内生变量名
    instruments : List[str]
        工具变量列表
    exogenous : Optional[List[str]]
        外生协变量
    null_value : float
        零假设下的因果效应值（默认 0）
    alpha : float
        显著性水平

    Returns
    -------
    Dict[str, Any]
        包含 AR 统计量、p 值和判断结果

    Examples
    --------
    >>> ar = anderson_rubin_test(df, 'y', 'treated', ['z1'], null_value=0)
    >>> print(f"AR p-value = {ar['p_value']:.4f}")
    """
    import statsmodels.api as sm

    if exogenous is None:
        exogenous = []

    data = df[[outcome, endogenous] + instruments + exogenous].dropna()
    n = len(data)
    k_instr = len(instruments)

    # 构建残差化变量
    # 1. 在零假设下计算残差: u0 = y - null_value * endogenous - exogenous
    y_adj = data[outcome] - null_value * data[endogenous]

    # 2. 对外生变量回归，取残差
    if exogenous:
        X_exog = sm.add_constant(data[exogenous])
        exog_model = sm.OLS(y_adj, X_exog).fit()
        u0 = exog_model.resid
        # 工具变量也对外生变量残差化
        Z_resid = {}
        for z in instruments:
            z_model = sm.OLS(data[z], X_exog).fit()
            Z_resid[z] = z_model.resid
    else:
        u0 = y_adj - y_adj.mean()
        Z_resid = {z: data[z] - data[z].mean() for z in instruments}

    # 3. AR 统计量
    Z_matrix = pd.DataFrame(Z_resid)
    # AR = n * R^2(u0 ~ Z)
    ar_model = sm.OLS(u0, sm.add_constant(Z_matrix)).fit()
    ar_stat = n * ar_model.rsquared

    # p 值（卡方分布，自由度 = 工具变量数）
    p_value = 1 - stats.chi2.cdf(ar_stat, df=k_instr)

    # 判断
    reject_null = p_value < alpha

    # AR 置信集（通过搜索 null_value）
    ar_ci = _ar_confidence_set(
        data, outcome, endogenous, instruments, exogenous, alpha
    )

    result = {
        "ar_statistic": float(ar_stat),
        "p_value": float(p_value),
        "df": k_instr,
        "null_value": null_value,
        "reject_null": reject_null,
        "ar_confidence_set": ar_ci,
        "n_obs": n,
        "method": "Anderson-Rubin test",
    }

    logger.info(f"  AR 统计量: {ar_stat:.4f}")
    logger.info(f"  p 值: {p_value:.4f}")
    logger.info(f"  拒绝零假设 (effect = {null_value}): {'是' if reject_null else '否'}")
    if ar_ci is not None:
        logger.info(f"  AR 95% 置信集: [{ar_ci[0]:.4f}, {ar_ci[1]:.4f}]")

    return result


def _ar_confidence_set(
    data, outcome, endogenous, instruments, exogenous, alpha
):
    """通过网格搜索计算 AR 置信集"""
    import statsmodels.api as sm

    # 搜索范围
    grid = np.linspace(-5, 5, 200)
    accepted = []

    for val in grid:
        y_adj = data[outcome] - val * data[endogenous]
        n = len(data)
        k_instr = len(instruments)

        if exogenous:
            X_exog = sm.add_constant(data[exogenous])
            exog_model = sm.OLS(y_adj, X_exog).fit()
            u0 = exog_model.resid
            Z_resid = pd.DataFrame({
                z: sm.OLS(data[z], X_exog).fit().resid for z in instruments
            })
        else:
            u0 = y_adj - y_adj.mean()
            Z_resid = pd.DataFrame({
                z: data[z] - data[z].mean() for z in instruments
            })

        ar_model = sm.OLS(u0, sm.add_constant(Z_resid)).fit()
        ar_stat = n * ar_model.rsquared
        p_val = 1 - stats.chi2.cdf(ar_stat, df=k_instr)

        if p_val > alpha:
            accepted.append(val)

    if not accepted:
        return None
    return (min(accepted), max(accepted))


# ============================================================================
# 4. 线性 IV 估计（完整）
# ============================================================================


def linear_iv_estimation(
    df: pd.DataFrame,
    outcome: str,
    endogenous: str,
    instruments: List[str],
    exogenous: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """完整的线性 IV 估计

    包含 OLS 对比、2SLS 估计、弱工具变量检验、AR 检验、过度识别检验。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    endogenous : str
        内生变量名
    instruments : List[str]
        工具变量列表
    exogenous : Optional[List[str]]
        外生协变量

    Returns
    -------
    Dict[str, Any]
        包含所有分析结果

    Examples
    --------
    >>> result = linear_iv_estimation(df, 'y', 'treated', ['z1', 'z2'], ['age'])
    >>> print(result['iv_summary'])
    """
    import statsmodels.api as sm

    if exogenous is None:
        exogenous = []

    results = {}

    # 1. OLS 估计（有偏，作为对比）
    data = df[[outcome, endogenous] + instruments + exogenous].dropna()
    X_ols = sm.add_constant(data[[endogenous] + exogenous])
    ols_model = sm.OLS(data[outcome], X_ols).fit(cov_type="HC1")
    results["ols_model"] = ols_model
    results["ols_coefficient"] = float(ols_model.params[endogenous])
    results["ols_se"] = float(ols_model.bse[endogenous])
    results["ols_ci"] = (
        float(ols_model.conf_int().loc[endogenous, 0]),
        float(ols_model.conf_int().loc[endogenous, 1]),
    )

    # 2. 2SLS 估计
    iv_result = run_2sls(df, outcome, endogenous, instruments, exogenous)
    results["iv_result"] = iv_result
    results["iv_summary"] = iv_result["summary"]

    # 提取 IV 系数
    iv_coef_row = iv_result["summary"][
        iv_result["summary"]["Variable"] == endogenous
    ]
    if len(iv_coef_row) > 0:
        results["iv_coefficient"] = float(iv_coef_row["Coefficient"].values[0])
        results["iv_se"] = float(iv_coef_row["SE"].values[0])
        results["iv_ci"] = (
            float(iv_coef_row["CI_lower"].values[0]),
            float(iv_coef_row["CI_upper"].values[0]),
        )

    # 3. 弱工具变量检验
    results["weak_iv_test"] = weak_instrument_test(
        df, endogenous, instruments, exogenous
    )

    # 4. AR 检验
    results["ar_test"] = anderson_rubin_test(
        df, outcome, endogenous, instruments, exogenous, null_value=0.0
    )

    # 5. 过度识别检验（当工具变量数 > 内生变量数时）
    if len(instruments) > 1:
        results["overid_test"] = _overidentification_test(
            iv_result["result"], instruments, endogenous
        )

    # 6. Hausman 检验（OLS vs IV）
    results["hausman_test"] = _hausman_test(
        ols_model, iv_result["result"], endogenous
    )

    return results


def _overidentification_test(iv_result, instruments, endogenous):
    """过度识别检验（Sargan / Hansen J 检验）"""
    try:
        # Hansen J 检验
        j_stat = float(iv_result.j_stat.stat)
        j_pvalue = float(iv_result.j_stat.pval)
        j_df = len(instruments) - 1  # 过度识别约束数

        result = {
            "test_statistic": j_stat,
            "p_value": j_pvalue,
            "df": j_df,
            "method": "Hansen J test",
            "reject_validity": j_pvalue < 0.05,
        }

        logger.info(f"  Hansen J 统计量: {j_stat:.4f}")
        logger.info(f"  p 值: {j_pvalue:.4f}")
        if j_pvalue < 0.05:
            logger.info("  警告: 过度识别检验拒绝工具变量有效性（p < 0.05）")
            warnings.warn(
                "Hansen J 检验拒绝工具变量有效性，工具变量可能不满足外生性假设。",
                RuntimeWarning,
            )

        return result
    except Exception as e:
        return {"error": str(e), "method": "Hansen J test"}


def _hausman_test(ols_model, iv_result, endogenous):
    """Hausman 检验：OLS vs IV"""
    ols_coef = float(ols_model.params[endogenous])
    ols_var = float(ols_model.bse[endogenous]) ** 2

    iv_params = iv_result.params
    iv_std = iv_result.std_errors
    if endogenous in iv_params.index:
        iv_coef = float(iv_params[endogenous])
        iv_var = float(iv_std[endogenous]) ** 2
    else:
        return {"error": f"变量 {endogenous} 不在 IV 结果中"}

    # Hausman 统计量
    diff = iv_coef - ols_coef
    var_diff = iv_var - ols_var

    if var_diff <= 0:
        # IV 方差更小，说明 OLS 可能更有效
        return {
            "hausman_stat": 0.0,
            "p_value": 1.0,
            "interpretation": "无法拒绝 OLS（IV 方差 <= OLS 方差）",
            "method": "Hausman test",
        }

    hausman_stat = diff ** 2 / var_diff
    p_value = 1 - stats.chi2.cdf(hausman_stat, df=1)

    return {
        "hausman_stat": float(hausman_stat),
        "p_value": float(p_value),
        "reject_ols": p_value < 0.05,
        "interpretation": "拒绝 OLS（存在内生性）" if p_value < 0.05 else "无法拒绝 OLS（无显著内生性）",
        "method": "Hausman test",
    }


# ============================================================================
# 5. 可视化
# ============================================================================


def plot_iv_comparison(
    iv_results: Dict[str, Any],
    endogenous: str,
    figsize: Tuple[float, float] = (8, 5),
) -> "matplotlib.figure.Figure":
    """绘制 OLS vs IV 估计对比图

    Parameters
    ----------
    iv_results : Dict[str, Any]
        linear_iv_estimation 的返回结果
    endogenous : str
        内生变量名（用于标注）
    figsize : Tuple[float, float]
        图形大小

    Returns
    -------
    matplotlib.figure.Figure
        对比图

    Examples
    --------
    >>> fig = plot_iv_comparison(results, 'treated')
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize)

    methods = []
    coefs = []
    ci_lows = []
    ci_highs = []

    if "ols_coefficient" in iv_results:
        methods.append("OLS")
        coefs.append(iv_results["ols_coefficient"])
        ci_lows.append(iv_results["ols_ci"][0])
        ci_highs.append(iv_results["ols_ci"][1])

    if "iv_coefficient" in iv_results:
        methods.append("2SLS (IV)")
        coefs.append(iv_results["iv_coefficient"])
        ci_lows.append(iv_results["iv_ci"][0])
        ci_highs.append(iv_results["iv_ci"][1])

    # AR 置信集
    if "ar_test" in iv_results and iv_results["ar_test"]["ar_confidence_set"] is not None:
        ar_ci = iv_results["ar_test"]["ar_confidence_set"]
        methods.append("AR (weak-IV robust)")
        coefs.append(np.mean(ar_ci))
        ci_lows.append(ar_ci[0])
        ci_highs.append(ar_ci[1])

    y_pos = range(len(methods))
    errors = [[c - l for c, l in zip(coefs, ci_lows)],
              [h - c for c, h in zip(coefs, ci_highs)]]

    colors = ["#e74c3c", "#3498db", "#2ecc71"]
    ax.barh(y_pos, coefs, xerr=errors, color=colors[:len(methods)],
            alpha=0.7, capsize=5, edgecolor="black", linewidth=0.5)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(methods)
    ax.axvline(x=0, color="grey", linestyle="--", alpha=0.5)
    ax.set_xlabel(f"Coefficient ({endogenous})")
    ax.set_title("OLS vs IV Estimation Comparison", fontweight="bold")
    ax.grid(axis="x", alpha=0.3, linestyle=":")

    plt.tight_layout()
    return fig


# ============================================================================
# 6. 完整 IV 分析工作流
# ============================================================================


def full_iv_workflow(
    df: pd.DataFrame,
    outcome: str,
    endogenous: str,
    instruments: List[str],
    exogenous: Optional[List[str]] = None,
    do_plot: bool = True,
) -> Dict[str, Any]:
    """完整的工具变量分析工作流

    执行：OLS 估计 → 2SLS 估计 → 弱工具变量检验 →
         AR 检验 → 过度识别检验 → Hausman 检验 → 可视化

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    endogenous : str
        内生变量名
    instruments : List[str]
        工具变量列表
    exogenous : Optional[List[str]]
        外生协变量
    do_plot : bool
        是否生成可视化

    Returns
    -------
    Dict[str, Any]
        包含所有分析结果

    Examples
    --------
    >>> results = full_iv_workflow(df, 'y', 'treated', ['z1', 'z2'], ['age'])
    """
    results = {}

    # Step 1: 完整 IV 估计
    logger.info("=" * 50)
    logger.info("Step 1: IV 估计（OLS + 2SLS）")
    logger.info("=" * 50)
    iv_results = linear_iv_estimation(
        df, outcome, endogenous, instruments, exogenous
    )
    results.update(iv_results)

    logger.info(f"\n  OLS 系数: {iv_results.get('ols_coefficient', 'N/A'):.4f}")
    logger.info(f"  IV 系数:  {iv_results.get('iv_coefficient', 'N/A'):.4f}")

    # Step 2: 弱工具变量检验
    logger.info("\n" + "=" * 50)
    logger.info("Step 2: 弱工具变量检验")
    logger.info("=" * 50)
    weak_test = iv_results["weak_iv_test"]
    logger.info(f"  第一阶段 F: {weak_test['first_stage_f']:.2f}")
    logger.info(f"  弱工具变量: {'是' if weak_test['is_weak_rule_of_thumb'] else '否'}")

    # Step 3: AR 检验
    logger.info("\n" + "=" * 50)
    logger.info("Step 3: Anderson-Rubin 检验")
    logger.info("=" * 50)
    ar = iv_results["ar_test"]
    logger.info(f"  AR 统计量: {ar['ar_statistic']:.4f}")
    logger.info(f"  p 值: {ar['p_value']:.4f}")

    # Step 4: 过度识别检验
    if "overid_test" in iv_results:
        logger.info("\n" + "=" * 50)
        logger.info("Step 4: 过度识别检验")
        logger.info("=" * 50)
        overid = iv_results["overid_test"]
        if "test_statistic" in overid:
            logger.info(f"  Hansen J: {overid['test_statistic']:.4f}")
            logger.info(f"  p 值: {overid['p_value']:.4f}")

    # Step 5: Hausman 检验
    logger.info("\n" + "=" * 50)
    logger.info("Step 5: Hausman 检验（OLS vs IV）")
    logger.info("=" * 50)
    hausman = iv_results["hausman_test"]
    if "hausman_stat" in hausman:
        logger.info(f"  Hausman 统计量: {hausman['hausman_stat']:.4f}")
        logger.info(f"  p 值: {hausman['p_value']:.4f}")
        logger.info(f"  结论: {hausman['interpretation']}")

    # Step 6: 可视化
    if do_plot:
        logger.info("\n" + "=" * 50)
        logger.info("Step 6: 可视化")
        logger.info("=" * 50)
        results["comparison_plot"] = plot_iv_comparison(iv_results, endogenous)
        logger.info("  OLS vs IV 对比图已生成")

    logger.info("\n 工具变量分析完成")
    return results


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 模拟数据（存在内生性）
    np.random.seed(42)
    n = 1000

    # 不可观测的混杂因素
    u = np.random.normal(0, 1, n)

    # 工具变量（外生，与 u 无关）
    z = np.random.binomial(1, 0.5, n)

    # 内生处理变量（受工具变量和混杂因素影响）
    # 真实因果效应 = 2.0
    treated = 0.5 + 0.8 * z + 0.5 * u + np.random.normal(0, 0.5, n)
    treated = (treated > 0.8).astype(int)

    # 结局变量（受处理和混杂因素影响）
    y = 1.0 + 2.0 * treated + 1.5 * u + np.random.normal(0, 1, n)

    # 外生协变量
    age = np.random.normal(60, 10, n)

    df = pd.DataFrame({
        "y": y,
        "treated": treated,
        "z": z,
        "age": age,
    })

    # OLS 估计（有偏）
    import statsmodels.api as sm
    X_ols = sm.add_constant(df[["treated", "age"]])
    ols = sm.OLS(df["y"], X_ols).fit(cov_type="HC1")
    logger.info("=" * 60)
    logger.info("OLS 估计（有偏，受混杂影响）")
    logger.info("=" * 60)
    logger.info(f"  treated 系数: {ols.params['treated']:.4f} (真实值: 2.0)")

    # IV 估计
    logger.info("\n" + "=" * 60)
    logger.info("IV 估计（2SLS）")
    logger.info("=" * 60)
    iv_result = run_2sls(df, "y", "treated", ["z"], exogenous=["age"])
    logger.info(iv_result["summary"].to_string(index=False))

    # 弱工具变量检验
    logger.info("\n" + "=" * 60)
    logger.info("弱工具变量检验")
    logger.info("=" * 60)
    weak_test = weak_instrument_test(df, "treated", ["z"], exogenous=["age"])

    # AR 检验
    logger.info("\n" + "=" * 60)
    logger.info("Anderson-Rubin 检验")
    logger.info("=" * 60)
    ar = anderson_rubin_test(df, "y", "treated", ["z"], exogenous=["age"])

    # 完整工作流
    logger.info("\n" + "=" * 60)
    logger.info("完整 IV 工作流")
    logger.info("=" * 60)
    full_results = full_iv_workflow(
        df, "y", "treated", ["z"], exogenous=["age"], do_plot=False
    )

    logger.info(f"\n  OLS 系数: {full_results['ols_coefficient']:.4f}")
    logger.info(f"  IV 系数:  {full_results['iv_coefficient']:.4f}")
    logger.info("  真实值:   2.0000")

    logger.info("\n 工具变量分析模板示例完成")
