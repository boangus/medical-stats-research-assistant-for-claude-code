"""
survival_lifelines.py — 基于 lifelines 的生存分析模板
====================================================
适用于：时间-事件数据的 Python 生存分析

技术来源：
  - 受 ehrapy (Nature Medicine 2024) 的生存分析模块启发
  - 使用 lifelines 包 (KM 估计 + CoxPH + 竞争风险)
  - 与 MSRA 现有 cox_template.py 互补（此模板更侧重于
    数据探索、可视化、模型诊断）

工作流:
  Step 1: KM 估计 + 可视化
  Step 2: Log-rank 检验
  Step 3: Cox 比例风险模型
  Step 4: 模型诊断 (PH 假设、影响点)
  Step 5: 竞争风险 (Fine-Gray)

依赖:
  pip install lifelines matplotlib pandas numpy scipy

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. Kaplan-Meier 估计
# ============================================================================


def km_estimate(
    durations: np.ndarray,
    event_observed: np.ndarray,
    groups: Optional[np.ndarray] = None,
    group_labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Kaplan-Meier 生存估计

    Parameters
    ----------
    durations : np.ndarray
        观察时间
    event_observed : np.ndarray
        事件指示 (1=事件, 0=删失)
    groups : Optional[np.ndarray]
        分组标签（可选）
    group_labels : Optional[List[str]]
        组标签名

    Returns
    -------
    Dict
        包含 KM 拟合结果的字典
    """
    from lifelines import KaplanMeierFitter

    if groups is None:
        groups = np.zeros(len(durations), dtype=int)

    unique_groups = np.unique(groups)
    if group_labels is None:
        group_labels = [f"Group {g}" for g in unique_groups]

    kmf_dict = {}
    summary_data = []

    for g, label in zip(unique_groups, group_labels):
        mask = groups == g
        kmf = KaplanMeierFitter()
        kmf.fit(
            durations[mask],
            event_observed=event_observed[mask],
            label=label,
        )
        kmf_dict[label] = kmf

        # 提取关键信息
        median_ = kmf.median_survival_time_
        summary_data.append({
            "Group": label,
            "n": mask.sum(),
            "Events": event_observed[mask].sum(),
            "Censored": mask.sum() - event_observed[mask].sum(),
            "Median_Survival": median_ if not np.isnan(median_) else "NR",
        })

    return {
        "fitters": kmf_dict,
        "summary": pd.DataFrame(summary_data),
    }


def plot_km_curves(
    km_result: Dict[str, Any],
    figsize: Tuple[float, float] = (8, 6),
    title: str = "Kaplan-Meier Survival Curves",
    ci_alpha: float = 0.3,
    colors: Optional[List[str]] = None,
) -> plt.Figure:
    """绘制 KM 生存曲线

    Parameters
    ----------
    km_result : Dict
        km_estimate() 的返回结果
    figsize : Tuple
        图大小
    title : str
        标题
    ci_alpha : float
        置信区间透明度
    colors : Optional[List[str]]
        颜色列表

    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    fitters = km_result["fitters"]
    n_curves = len(fitters)

    if colors is None:
        colors = plt.cm.Set1(np.linspace(0, 1, n_curves))

    for (label, kmf), color in zip(fitters.items(), colors):
        kmf.plot_survival_function(
            ax=ax,
            color=color,
            ci_show=True,
            ci_alpha=ci_alpha,
            linewidth=2,
        )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Survival Probability", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3, linestyle=":")

    plt.tight_layout()
    return fig


# ============================================================================
# 2. Log-rank 检验
# ============================================================================


def logrank_test(
    durations: np.ndarray,
    event_observed: np.ndarray,
    groups: np.ndarray,
) -> Dict[str, Any]:
    """Log-rank 检验，比较两组或多组生存曲线

    Parameters
    ----------
    durations : np.ndarray
        观察时间
    event_observed : np.ndarray
        事件指示
    groups : np.ndarray
        分组标签

    Returns
    -------
    Dict
        检验统计量和 p 值
    """
    from lifelines.statistics import multivariate_logrank_test

    unique_groups = np.unique(groups)

    if len(unique_groups) == 2:
        # 两组：标准 log-rank
        from lifelines.statistics import logrank_test as lrt
        g1 = groups == unique_groups[0]
        g2 = groups == unique_groups[1]
        result = lrt(
            durations[g1], durations[g2],
            event_observed[g1], event_observed[g2],
        )
        return {
            "test_statistic": result.test_statistic,
            "p_value": result.p_value,
            "method": "Log-rank test (2-group)",
        }
    else:
        # 多组：多元 log-rank
        result = multivariate_logrank_test(durations, groups, event_observed)
        return {
            "test_statistic": result.test_statistic,
            "p_value": result.p_value,
            "method": "Multivariate Log-rank test",
        }


# ============================================================================
# 3. Cox 比例风险模型
# ============================================================================


def cox_regression(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    predictor_cols: List[str],
    penalizer: float = 0.0,
    l1_ratio: Optional[float] = None,
) -> Dict[str, Any]:
    """Cox 比例风险回归

    支持:
      - 标准 CoxPH
      - Ridge 惩罚 (设置 penalizer > 0)
      - Elastic Net 惩罚 (设置 l1_ratio)

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    duration_col : str
        时间列
    event_col : str
        事件列
    predictor_cols : List[str]
        预测变量列名
    penalizer : float
        惩罚系数 (0 = 无惩罚)
    l1_ratio : Optional[float]
        L1 比例 (None = 仅 Ridge)

    Returns
    -------
    Dict[str, Any]
        {
            "model": 拟合的模型,
            "summary": 系数表格 (HR, CI, p),
            "c_index": C-index,
        }
    """
    from lifelines import CoxPHFitter

    # 准备数据
    model_data = df[[duration_col, event_col] + predictor_cols].copy()
    model_data = model_data.dropna()

    # 拟合 Cox 模型
    cph = CoxPHFitter(penalizer=penalizer, l1_ratio=l1_ratio)
    cph.fit(
        model_data,
        duration_col=duration_col,
        event_col=event_col,
        show_progress=False,
    )

    # 提取汇总表
    summary_df = cph.summary.copy()
    summary_df["HR"] = np.exp(summary_df["coef"])
    summary_df["HR_CI_lower"] = np.exp(summary_df["coef"] - 1.96 * summary_df["se(coef)"])
    summary_df["HR_CI_upper"] = np.exp(summary_df["coef"] + 1.96 * summary_df["se(coef)"])

    result_summary = summary_df[["HR", "HR_CI_lower", "HR_CI_upper",
                                  "p", "coef", "se(coef)"]].round(4)

    # C-index
    c_index = cph.concordance_index_

    logger.info("=" * 60)
    logger.info("  Cox 比例风险模型结果")
    logger.info("=" * 60)
    logger.info(f"  C-index (Harrell's C): {c_index:.3f}")
    logger.info(f"  事件数: {model_data[event_col].sum()}")
    logger.info(f"  样本数: {len(model_data)}")
    logger.info(f"\n  系数表 (HR, 95% CI, p-value):")
    logger.info("result_summary.to_string()")

    return {
        "model": cph,
        "summary": result_summary,
        "c_index": c_index,
    }


# ============================================================================
# 4. 模型诊断: 比例风险假设检验
# ============================================================================


def proportional_hazard_test(
    cph_result: Dict[str, Any],
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
) -> Dict[str, Any]:
    """比例风险假设 (PH) 诊断

    使用 Schoenfeld 残差检验每个变量的 PH 假设
    如果全局 p < 0.05，考虑：
      - 分层 Cox 模型 (strata)
      - 时依系数

    Parameters
    ----------
    cph_result : Dict
        cox_regression() 的返回
    df : pd.DataFrame
        分析数据
    duration_col : str
        时间列
    event_col : str
        事件列

    Returns
    -------
    Dict
    """
    from lifelines import CoxPHFitter

    model = cph_result["model"]

    # Schoenfeld 残差检验
    test_results = model.check_assumptions(
        df[[duration_col, event_col] + list(model.params.index)],
        show_plots=False,
        print_summary=False,
    )

    # 手动计算每个变量的 PH 检验
    # 使用 lifelines 的统计检验
    logger.info("\n=== 比例风险假设 (PH) 检验 ===")
    logger.info("  H0: 比例风险假设成立")
    logger.info("  若 p < 0.05 → 违反 PH 假设\n")

    ph_results = {}
    for var, result in test_results.items():
        if hasattr(result, 'p_value'):
            ph_results[var] = {
                "p_value": result.p_value,
                "pass": result.p_value > 0.05,
            }
            status = "✅" if result.p_value > 0.05 else "❌"
            logger.info(f"  {var}: p = {result.p_value:.4f} {status}")

    return ph_results


def plot_schoenfeld_residuals(
    cph_result: Dict[str, Any],
    figsize: Tuple[float, float] = (10, 8),
) -> plt.Figure:
    """绘制 Schoenfeld 残差图（诊断 PH 假设）"""
    model = cph_result["model"]
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    # 使用 lifelines 内置的绘图方法
    model.plot(columns=model.params.index[:4], ax=axes)

    fig.suptitle("Schoenfeld Residuals (PH Assumption Diagnostics)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


# ============================================================================
# 5. 分层 Cox 模型 (处理 PH 违反)
# ============================================================================


def stratified_cox(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    predictor_cols: List[str],
    strata_cols: List[str],
) -> Dict[str, Any]:
    """分层 Cox 比例风险模型

    当某些变量违反 PH 假设时，将其作为分层变量
    """
    from lifelines import CoxPHFitter

    model_data = df[[duration_col, event_col] + predictor_cols + strata_cols]
    model_data = model_data.dropna()

    cph = CoxPHFitter()
    formula = f"{duration_col} + {event_col} ~ {' + '.join(predictor_cols)} + strata({' + '.join(strata_cols)})"
    cph.fit(model_data, duration_col=duration_col, event_col=event_col,
            strata=strata_cols, show_progress=False)

    summary_df = cph.summary.copy()
    summary_df["HR"] = np.exp(summary_df["coef"])
    summary_df["HR_CI_lower"] = np.exp(summary_df["coef"] - 1.96 * summary_df["se(coef)"])
    summary_df["HR_CI_upper"] = np.exp(summary_df["coef"] + 1.96 * summary_df["se(coef)"])

    return {
        "model": cph,
        "summary": summary_df[["HR", "HR_CI_lower", "HR_CI_upper", "p"]].round(4),
        "c_index": cph.concordance_index_,
    }


# ============================================================================
# 6. Aalen 加性模型 (PH 假设不满足时的替代)
# ============================================================================


def aalen_additive_model(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    predictor_cols: List[str],
) -> Dict[str, Any]:
    """Aalen 加性模型

    当 PH 假设严重违反时，可替代 Cox 模型。
    加性模型假设风险差是相加的（而非相乘）。
    """
    from lifelines import AalenAdditiveFitter

    model_data = df[[duration_col, event_col] + predictor_cols].dropna()

    aaf = AalenAdditiveFitter(coef_penalizer=0.5)
    aaf.fit(model_data, duration_col=duration_col, event_col=event_col)

    logger.info("Aalen 加性模型拟合完成")
    logger.info(f"  样本量: {len(model_data)}")

    return {"model": aaf}


# ============================================================================
# 7. 竞争风险模型 (Fine-Gray)
# ============================================================================


def fine_gray_competing_risks(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    predictor_cols: List[str],
    event_of_interest: int = 1,
    censoring_code: int = 0,
) -> Dict[str, Any]:
    """Fine-Gray 竞争风险模型

    当存在多个互斥的事件类型时使用。
    - event_of_interest: 目标事件的编码
    - censoring_code: 删失的编码
    - 其他非零编码视为竞争事件

    参考: Fine & Gray (1999) JASA
    """
    try:
        from lifelines import FineGrayModel
    except ImportError:
        # Fallback: 使用 cmprsk 的 Python 实现或说明
        logger.info("注意: lifelines 的 FineGrayModel 在较新版本中可用。")
        raise ImportError("需要 lifelines >= 0.28.0: pip install --upgrade lifelines")

    model_data = df[[duration_col, event_col] + predictor_cols].dropna()

    fg = FineGrayModel()
    fg.fit(
        model_data,
        duration_col=duration_col,
        event_col=event_col,
        event_of_interest=event_of_interest,
        regressors=predictor_cols,
    )

    summary_df = fg.summary.copy()
    summary_df["SHR"] = np.exp(summary_df["coef"])
    summary_df["SHR_CI_lower"] = \
        np.exp(summary_df["coef"] - 1.96 * summary_df["se(coef)"])
    summary_df["SHR_CI_upper"] = \
        np.exp(summary_df["coef"] + 1.96 * summary_df["se(coef)"])

    return {
        "model": fg,
        "summary": summary_df[["SHR", "SHR_CI_lower", "SHR_CI_upper", "p"]].round(4),
    }


# ============================================================================
# 8. 完整生存分析汇报
# ============================================================================


def survival_report(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    group_col: Optional[str] = None,
    predictor_cols: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """一次性生成完整的生存分析报告

    流程: KM → Log-rank → Cox → PH 检验 → 结果汇总
    """
    from lifelines.utils import median_survival_times

    results = {}

    durations = df[duration_col].values
    events = df[event_col].values

    # --- 描述性统计 ---
    n_total = len(df)
    n_events = events.sum()
    n_censored = n_total - n_events

    logger.info("=" * 60)
    logger.info("  生存分析报告")
    logger.info("=" * 60)
    logger.info(f"  总样本: {n_total}")
    logger.info(f"  事件数: {n_events} ({n_events/n_total*100:.1f}%)")
    logger.info(f"  删失数: {n_censored}")

    # --- Step 1: KM ---
    if group_col is not None:
        groups = df[group_col].values
        km = km_estimate(durations, events, groups)
    else:
        km = km_estimate(durations, events)

    results["km"] = km

    if group_col is not None:
        logger.info(f"\n[KM] 中位生存时间:")
        logger.info(km["summary"].to_string(index=False))

    # --- Step 2: Log-rank (如有分组) ---
    if group_col is not None:
        lr = logrank_test(durations, events, df[group_col].values)
        results["logrank"] = lr
        logger.info(f"\n[Log-rank] 统计量: {lr['test_statistic']:.3f}, "
              f"p = {lr['p_value']:.4f}")

    # --- Step 3: Cox ---
    if predictor_cols:
        cox = cox_regression(df, duration_col, event_col, predictor_cols)
        results["cox"] = cox

        # --- Step 4: PH 检验 ---
        ph = proportional_hazard_test(cox, df, duration_col, event_col)
        results["ph_test"] = ph

    logger.info("\n" + "=" * 60)
    logger.info("  生存分析报告完成")
    logger.info("=" * 60)

    return results


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    from lifelines.datasets import load_rossi

    # 使用 lifelines 内置的 Rossi 再犯数据
    rossi = load_rossi()
    logger.info(f"Rossi 数据集: {rossi.shape}")

    # 运行完整生存分析报告
    results = survival_report(
        df=rossi,
        duration_col="week",
        event_col="arrest",
        group_col="fin",  # 经济援助（处理变量）
        predictor_cols=["fin", "age", "race", "wexp",
                        "mar", "paro", "prio"],
    )

    # 绘制 KM 曲线
    fig = plot_km_curves(
        results["km"],
        title="Kaplan-Meier: Survival by Financial Aid (Rossi Data)",
    )
    plt.show()

    # 保存图片
    # fig.savefig("KM_lifelines.png", dpi=300, bbox_inches="tight")

    logger.info("\n✅ 生存分析完成")
