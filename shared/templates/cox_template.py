"""
cox_template.py — Cox 比例风险回归模板
========================================
适用于：生存分析的独立预后因素分析、治疗效应估计、混杂调整

依赖: lifelines, pandas, numpy, matplotlib, scipy
安装: pip install lifelines pandas numpy matplotlib scipy

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test
from scipy import stats

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# ============================================================================
# 1. 基本 Cox 回归
# ============================================================================


def run_cox_regression(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    predictors: List[str],
    penalizer: float = 0.0,
    l1_ratio: float = 0.0,
    strata: Optional[List[str]] = None,
) -> CoxPHFitter:
    """运行 Cox 比例风险回归

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集（长格式，每行一个受试者）
    duration_col : str
        生存时间变量名
    event_col : str
        事件状态变量名（1=事件发生，0=删失）
    predictors : List[str]
        预测变量/协变量列表
    penalizer : float
        惩罚项系数（用于 Ridge 正则化）
    l1_ratio : float
        L1 比例（0=Ridge, 1=Lasso, 0~1=ElasticNet）
    strata : Optional[List[str]]
        分层变量列表

    Returns
    -------
    CoxPHFitter
        拟合的 Cox 模型
    """
    # 准备数据
    cols = [duration_col, event_col] + predictors
    if strata:
        cols += strata
    data = df[cols].dropna().copy()

    # 创建模型
    cph = CoxPHFitter(penalizer=penalizer, l1_ratio=l1_ratio)
    cph.fit(
        data,
        duration_col=duration_col,
        event_col=event_col,
        strata=strata,
    )

    return cph


def summarize_cox(cph: CoxPHFitter) -> pd.DataFrame:
    """提取 Cox 模型结果的 HR 和 95% CI

    Parameters
    ----------
    cph : CoxPHFitter
        lifelines 拟合的 Cox 模型

    Returns
    -------
    pd.DataFrame
        包含 HR, 95% CI, p-value 的摘要表
    """
    summary_df = cph.summary.copy()
    summary_df = summary_df.reset_index()
    summary_df.columns = [
        "Variable",
        "coef",
        "exp(coef)_HR",
        "se(coef)",
        "z",
        "p_value",
        "HR_Lower_95",
        "HR_Upper_95",
    ]
    summary_df["HR_CI"] = summary_df.apply(
        lambda row: f"{row['exp(coef)_HR']:.3f} ({row['HR_Lower_95']:.3f}, {row['HR_Upper_95']:.3f})",
        axis=1,
    )
    summary_df["Signif"] = summary_df["p_value"].apply(
        lambda p: "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    )
    return summary_df


# ============================================================================
# 2. 比例风险假设检验
# ============================================================================


def test_ph_assumption(
    cph: CoxPHFitter, df: pd.DataFrame, duration_col: str, event_col: str
) -> pd.DataFrame:
    """检验 Cox 模型的比例风险假设

    Parameters
    ----------
    cph : CoxPHFitter
        拟合的 Cox 模型
    df : pd.DataFrame
        原始数据
    duration_col : str
        生存时间变量
    event_col : str
        事件变量

    Returns
    -------
    pd.DataFrame
        每个变量的 Schoenfeld 残差检验结果
    """
    # 计算 Schoenfeld 残差
    schoenfeld = cph.compute_residuals(df, "schoenfeld")

    # 全局检验和逐变量检验
    test_result = cph.check_assumptions(
        df,
        show_plots=False,
        plot_n_bootstraps=0,
    )

    return test_result


# ============================================================================
# 3. Kaplan-Meier 生存曲线
# ============================================================================


def fit_km_curves(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    group_col: Optional[str] = None,
) -> Dict:
    """拟合 Kaplan-Meier 生存曲线

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    duration_col : str
        生存时间变量
    event_col : str
        事件变量
    group_col : Optional[str]
        分组变量（如 treatment 组）

    Returns
    -------
    Dict
        KM 拟合结果，包含生存概率和时间点
    """
    kmf = KaplanMeierFitter()
    results = {}

    if group_col:
        groups = df[group_col].unique()
        for g in sorted(groups):
            mask = df[group_col] == g
            kmf.fit(
                df.loc[mask, duration_col],
                event_observed=df.loc[mask, event_col],
                label=str(g),
            )
            surv_df = pd.DataFrame(
                {
                    "time": kmf.survival_function_.index,
                    "survival": kmf.survival_function_.values.flatten(),
                    "group": str(g),
                }
            )
            surv_df["lower_ci"] = kmf.confidence_interval_[
                kmf.confidence_interval_.columns[0]
            ].values
            surv_df["upper_ci"] = kmf.confidence_interval_[
                kmf.confidence_interval_.columns[1]
            ].values
            results[str(g)] = {
                "model": kmf,
                "median_survival": kmf.median_survival_time_,
                "survival_data": surv_df,
                "timeline": kmf.event_table,
            }

        # Log-rank 检验
        if len(groups) == 2:
            g1, g2 = sorted(groups)
            lr_result = logrank_test(
                df.loc[df[group_col] == g1, duration_col],
                df.loc[df[group_col] == g2, duration_col],
                event_observed_A=df.loc[df[group_col] == g1, event_col],
                event_observed_B=df.loc[df[group_col] == g2, event_col],
            )
            results["logrank_stat"] = lr_result.test_statistic
            results["logrank_pvalue"] = lr_result.p_value
        elif len(groups) > 2:
            lr_result = multivariate_logrank_test(
                df[duration_col],
                df[event_col],
                df[group_col],
            )
            results["logrank_stat"] = lr_result.test_statistic
            results["logrank_pvalue"] = lr_result.p_value
    else:
        kmf.fit(df[duration_col], event_observed=df[event_col], label="All")
        surv_df = pd.DataFrame(
            {
                "time": kmf.survival_function_.index,
                "survival": kmf.survival_function_.values.flatten(),
            }
        )
        results["all"] = {
            "model": kmf,
            "median_survival": kmf.median_survival_time_,
            "survival_data": surv_df,
        }

    return results


# ============================================================================
# 4. 生存率预测
# ============================================================================


def predict_survival(
    cph: CoxPHFitter,
    new_data: pd.DataFrame,
    times: Optional[List[float]] = None,
) -> pd.DataFrame:
    """预测新个体的生存概率

    Parameters
    ----------
    cph : CoxPHFitter
        拟合的 Cox 模型
    new_data : pd.DataFrame
        新个体的协变量数据
    times : Optional[List[float]]
        指定时间点，默认使用模型中的时间点

    Returns
    -------
    pd.DataFrame
        每个个体在指定时间点的生存概率
    """
    surv_fn = cph.predict_survival_function(new_data, times=times)
    return surv_fn.T


# ============================================================================
# 5. 完整生存分析工作流
# ============================================================================


def full_survival_workflow(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    predictors: List[str],
    group_col: Optional[str] = None,
    strata: Optional[List[str]] = None,
) -> Dict:
    """完整的生存分析工作流

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    duration_col : str
        生存时间变量
    event_col : str
        事件变量
    predictors : List[str]
        预测变量
    group_col : Optional[str]
        分组变量
    strata : Optional[List[str]]
        分层变量

    Returns
    -------
    Dict
        包含所有分析结果
    """
    results = {}

    # 1. KM 曲线
    results["km"] = fit_km_curves(df, duration_col, event_col, group_col)

    # 2. Cox 回归
    cph = run_cox_regression(
        df, duration_col, event_col, predictors, strata=strata
    )
    results["cox_model"] = cph
    results["cox_summary"] = summarize_cox(cph)

    # 3. C-index
    results["c_index"] = cph.concordance_index_

    # 4. 模型统计量
    results["log_likelihood"] = cph.log_likelihood_
    results["partial_aic"] = cph.AIC_partial_

    # 5. 比例风险假设检验（仅当变量数 <= 10）
    if len(predictors) <= 10:
        try:
            results["ph_test"] = test_ph_assumption(cph, df, duration_col, event_col)
        except Exception as e:
            results["ph_test"] = f"PH assumption test failed: {str(e)}"

    return results


# ============================================================================
# 生存率表
# ============================================================================


def survival_table_at_times(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    times: List[float],
    group_col: Optional[str] = None,
) -> pd.DataFrame:
    """生成指定时间点的生存率汇总表

    Parameters
    ----------
    df : pd.DataFrame
        数据集
    duration_col : str
        生存时间变量
    event_col : str
        事件变量
    times : List[float]
        指定时间点列表
    group_col : Optional[str]
        分组变量

    Returns
    -------
    pd.DataFrame
        生存率表
    """
    from lifelines import KaplanMeierFitter

    kmf = KaplanMeierFitter()
    rows = []

    if group_col:
        groups = df[group_col].unique()
        for g in sorted(groups):
            mask = df[group_col] == g
            kmf.fit(
                df.loc[mask, duration_col],
                event_observed=df.loc[mask, event_col],
            )
            for t in times:
                surv = kmf.predict(t)
                ci = kmf.confidence_interval_
                ci_lower = ci.loc[min(ci.index, key=lambda x: abs(x - t))].iloc[0] if t <= ci.index.max() else np.nan
                ci_upper = ci.loc[min(ci.index, key=lambda x: abs(x - t))].iloc[1] if t <= ci.index.max() else np.nan
                rows.append(
                    {
                        "Group": str(g),
                        "Time": t,
                        "Survival": surv,
                        "Lower_95": ci_lower,
                        "Upper_95": ci_upper,
                        "At_Risk": kmf.event_table.loc[
                            kmf.event_table.index <= t, "at_risk"
                        ].iloc[-1]
                        if t >= kmf.event_table.index.min()
                        else np.nan,
                    }
                )
    else:
        kmf.fit(df[duration_col], event_observed=df[event_col])
        for t in times:
            surv = kmf.predict(t)
            ci = kmf.confidence_interval_
            ci_lower = ci.loc[min(ci.index, key=lambda x: abs(x - t))].iloc[0] if t <= ci.index.max() else np.nan
            ci_upper = ci.loc[min(ci.index, key=lambda x: abs(x - t))].iloc[1] if t <= ci.index.max() else np.nan
            rows.append(
                {
                    "Time": t,
                    "Survival": surv,
                    "Lower_95": ci_lower,
                    "Upper_95": ci_upper,
                }
            )

    return pd.DataFrame(rows)


# ============================================================================
# 示例用法
# ============================================================================
if __name__ == "__main__":
    # 模拟生存数据
    np.random.seed(42)
    n = 200

    # 使用 Weibull 分布生成生存时间
    df_demo = pd.DataFrame(
        {
            "id": range(n),
            "age": np.random.normal(60, 10, n),
            "treatment": np.random.binomial(1, 0.5, n),
            "sex": np.random.choice(["M", "F"], n),
        }
    )
    # 生成生存时间
    base_hazard = np.random.exponential(scale=24, size=n)
    hr_treatment = 0.6  # 治疗组降低 40% 风险
    df_demo["survival_time"] = base_hazard / (
        hr_treatment ** df_demo["treatment"]
    )
    df_demo["event"] = np.random.binomial(
        1, 0.7, n
    )  # 70% 事件发生率
    df_demo.loc[df_demo["survival_time"] > 36, "event"] = 0
    df_demo["survival_time"] = df_demo["survival_time"].clip(upper=36)

    # 完整工作流
    res = full_survival_workflow(
        df_demo,
        duration_col="survival_time",
        event_col="event",
        predictors=["age", "treatment"],
        group_col="treatment",
    )

    print("=== KM 分析 ===")
    for g, data in res["km"].items():
        if g != "logrank_stat" and g != "logrank_pvalue":
            print(f"  组 {g}: 中位生存期 {data['median_survival']:.2f}")
    if "logrank_pvalue" in res:
        print(f"  Log-rank p-value: {res['logrank_pvalue']:.4f}")

    print("\n=== Cox 回归结果 ===")
    print(res["cox_summary"][["Variable", "exp(coef)_HR", "HR_Lower_95", "HR_Upper_95", "p_value", "Signif"]].to_string(index=False))
    print(f"\n  C-index: {res['c_index']:.3f}")
    print(f"  Partial AIC: {res['partial_aic']:.2f}")

    print("\n✅ 生存分析完成")
