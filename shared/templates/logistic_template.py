"""
logistic_template.py — Logistic 回归分析模板
==============================================
适用于：二分类结局的预测模型、风险因素分析、混杂调整

依赖: statsmodels, pandas, numpy, matplotlib, sklearn
安装: pip install statsmodels pandas numpy matplotlib scikit-learn

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import (
    auc,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from statsmodels.formula.api import logit
from statsmodels.stats.outliers_influence import variance_inflation_factor
import logging

logger = logging.getLogger(__name__)

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# ============================================================================
# 1. 基本 Logistic 回归
# ============================================================================


def run_logistic_regression(
    df: pd.DataFrame,
    outcome: str,
    predictors: List[str],
    cat_vars: Optional[List[str]] = None,
    add_intercept: bool = True,
) -> sm.discrete.DiscreteResultsWrapper:
    """运行基本的 Logistic 回归分析

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名（二分类，编码为 0/1）
    predictors : List[str]
        预测变量/协变量列表
    cat_vars : Optional[List[str]]
        分类变量列表（将自动转换为 dummy variables）
    add_intercept : bool
        是否加入截距项

    Returns
    -------
    sm.discrete.DiscreteResultsWrapper
        模型拟合结果
    """
    # 复制数据以避免修改原始数据
    data = df[[outcome] + predictors].copy()
    data = data.dropna()

    # 处理分类变量
    if cat_vars:
        data = pd.get_dummies(data, columns=cat_vars, drop_first=True)

    # 提取 outcome 和 predictors
    X = data.drop(columns=[outcome])
    y = data[outcome]

    if add_intercept:
        X = sm.add_constant(X)

    # 拟合模型
    model = logit(y, X)
    result = model.fit(disp=False, maxiter=100)

    return result


def summarize_logistic(result) -> pd.DataFrame:
    """提取 Logistic 回归结果的 OR 和 95% CI

    Parameters
    ----------
    result : sm.discrete.DiscreteResultsWrapper
        statsmodels 拟合结果

    Returns
    -------
    pd.DataFrame
        包含 OR, 95% CI, p-value 的摘要表
    """
    summary_df = pd.DataFrame(
        {
            "Variable": result.params.index,
            "OR": np.exp(result.params),
            "OR_Lower_95": np.exp(result.conf_int()[0]),
            "OR_Upper_95": np.exp(result.conf_int()[1]),
            "Coefficient": result.params,
            "SE": result.bse,
            "z": result.tvalues,
            "p_value": result.pvalues,
        }
    )
    summary_df["OR_CI"] = summary_df.apply(
        lambda row: f"{row['OR']:.3f} ({row['OR_Lower_95']:.3f}, {row['OR_Upper_95']:.3f})",
        axis=1,
    )
    summary_df["Signif"] = summary_df["p_value"].apply(
        lambda p: "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    )
    return summary_df


# ============================================================================
# 2. 模型诊断
# ============================================================================


def check_multicollinearity(X: pd.DataFrame, threshold: float = 10.0) -> pd.DataFrame:
    """检查多重共线性（VIF）

    Parameters
    ----------
    X : pd.DataFrame
        自变量矩阵（已含截距）
    threshold : float
        VIF 阈值，默认 10

    Returns
    -------
    pd.DataFrame
        VIF 值及标记
    """
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [
        variance_inflation_factor(X.values, i) for i in range(X.shape[1])
    ]
    vif_data["Flag"] = vif_data["VIF"].apply(
        lambda v: "⚠️ 高共线性" if v > threshold else "OK"
    )
    return vif_data


def hosmer_lemeshow_test(
    model, X: pd.DataFrame, y: pd.Series, g: int = 10
) -> Dict:
    """Hosmer-Lemeshow 拟合优度检验

    Parameters
    ----------
    model : fitted model
        拟合的模型对象（需有 .predict() 方法）
    X : pd.DataFrame
        自变量矩阵
    y : pd.Series
        实际观测值
    g : int
        分组数，默认 10

    Returns
    -------
    Dict
        检验统计量、p 值和分组表
    """
    from scipy.stats import chi2

    y_pred = model.predict(X)
    data = pd.DataFrame({"y_true": y, "y_pred": y_pred})
    data["decile"] = pd.qcut(data["y_pred"], g, labels=False, duplicates="drop")

    actual_groups = data.groupby("decile")["y_true"].sum()
    expected_groups = data.groupby("decile")["y_pred"].sum()
    n_groups = data.groupby("decile").size()

    chi2_stat = np.sum(
        (actual_groups - expected_groups) ** 2
        / (expected_groups * (1 - expected_groups / n_groups))
    )
    df = len(actual_groups) - 2
    p_value = 1 - chi2.cdf(chi2_stat, df)

    return {
        "chi2": chi2_stat,
        "df": df,
        "p_value": p_value,
        "groups": pd.DataFrame(
            {
                "decile": actual_groups.index,
                "n": n_groups,
                "observed": actual_groups.values,
                "expected": expected_groups.values,
            }
        ),
    }


# ============================================================================
# 3. 模型评估
# ============================================================================


def evaluate_logistic_model(
    model, X: pd.DataFrame, y: pd.Series, threshold: float = 0.5
) -> Dict:
    """综合评估 Logistic 回归模型

    Parameters
    ----------
    model : fitted model
        拟合的模型
    X : pd.DataFrame
        自变量矩阵
    y : pd.Series
        实际观测值
    threshold : float
        分类阈值，默认 0.5

    Returns
    -------
    Dict
        包含 AUC、分类报告、混淆矩阵等
    """
    y_pred_prob = model.predict(X)
    y_pred_class = (y_pred_prob >= threshold).astype(int)

    fpr, tpr, thresholds_roc = roc_curve(y, y_pred_prob)
    roc_auc = auc(fpr, tpr)

    cm = confusion_matrix(y, y_pred_class)
    tn, fp, fn, tp = cm.ravel()

    return {
        "auc": roc_auc,
        "sensitivity": tp / (tp + fn) if (tp + fn) > 0 else np.nan,
        "specificity": tn / (tn + fp) if (tn + fp) > 0 else np.nan,
        "ppv": tp / (tp + fp) if (tp + fp) > 0 else np.nan,
        "npv": tn / (tn + fn) if (tn + fn) > 0 else np.nan,
        "accuracy": (tp + tn) / (tp + tn + fp + fn),
        "confusion_matrix": cm,
        "classification_report": classification_report(
            y, y_pred_class, output_dict=True
        ),
        "roc_data": {"fpr": fpr, "tpr": tpr, "thresholds": thresholds_roc},
    }


# ============================================================================
# 4. 逐步回归（向前/向后/双向）
# ============================================================================


def stepwise_logistic(
    df: pd.DataFrame,
    outcome: str,
    candidate_vars: List[str],
    cat_vars: Optional[List[str]] = None,
    direction: str = "both",
    p_enter: float = 0.05,
    p_remove: float = 0.10,
) -> List[str]:
    """逐步 Logistic 回归变量筛选

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名
    candidate_vars : List[str]
        候选变量列表
    cat_vars : Optional[List[str]]
        分类变量
    direction : str
        筛选方向: 'forward', 'backward', 'both'
    p_enter : float
        进入模型的 p 值阈值
    p_remove : float
        移出模型的 p 值阈值

    Returns
    -------
    List[str]
        最终保留的变量列表
    """
    selected = list(candidate_vars) if direction in ["backward", "both"] else []

    def _fit_and_get_p(vars_list):
        if not vars_list:
            return None, None
        try:
            result = run_logistic_regression(df, outcome, vars_list, cat_vars)
            return result, result.pvalues.drop("const", errors="ignore")
        except Exception:
            return None, None

    def _get_worst_p(pvals):
        return pvals.idxmax(), pvals.max()

    def _get_best_p(pvals):
        return pvals.idxmin(), pvals.min()

    max_steps = min(len(candidate_vars) * 2, 50)
    for _ in range(max_steps):
        result, pvals = _fit_and_get_p(selected)
        if pvals is None or pvals.empty:
            break

        if direction == "backward":
            worst_var, worst_p = _get_worst_p(pvals)
            if worst_p > p_remove and len(selected) > 1:
                selected.remove(worst_var)
            else:
                break
        elif direction == "forward":
            remaining = [v for v in candidate_vars if v not in selected]
            if not remaining:
                break
            best_p = 1.0
            best_var = None
            for v in remaining:
                _, pvals_temp = _fit_and_get_p(selected + [v])
                if pvals_temp is not None:
                    v_p = pvals_temp.get(v, 1.0)
                    if v_p < best_p:
                        best_p = v_p
                        best_var = v
            if best_var and best_p <= p_enter:
                selected.append(best_var)
            else:
                break
        else:  # both
            # 尝试移除
            if len(selected) > 1:
                worst_var, worst_p = _get_worst_p(pvals)
                if worst_p > p_remove:
                    selected.remove(worst_var)
                    continue
            # 尝试加入
            remaining = [v for v in candidate_vars if v not in selected]
            if remaining:
                best_p = 1.0
                best_var = None
                for v in remaining:
                    _, pvals_temp = _fit_and_get_p(selected + [v])
                    if pvals_temp is not None:
                        v_p = pvals_temp.get(v, 1.0)
                        if v_p < best_p:
                            best_p = v_p
                            best_var = v
                if best_var and best_p <= p_enter:
                    selected.append(best_var)
                    continue
            break

    return selected


# ============================================================================
# 5. 完整工作流示例
# ============================================================================


def full_logistic_workflow(
    df: pd.DataFrame,
    outcome: str,
    predictors: List[str],
    cat_vars: Optional[List[str]] = None,
) -> Dict:
    """完整的 Logistic 回归分析工作流

    执行: 模型拟合 → 摘要 → 诊断 → 评估

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量
    predictors : List[str]
        预测变量
    cat_vars : Optional[List[str]]
        分类变量

    Returns
    -------
    Dict
        包含所有分析结果
    """
    results = {}

    # 1. 基本模型
    model = run_logistic_regression(df, outcome, predictors, cat_vars)
    results["model"] = model
    results["summary"] = summarize_logistic(model)

    # 2. 模型拟合统计量
    results["log_likelihood"] = model.llf
    results["log_likelihood_null"] = model.llnull
    results["pseudo_r2"] = model.prsquared  # McFadden's R²
    results["aic"] = model.aic
    results["bic"] = model.bic

    # 3. 似然比检验
    results["lrt_stat"] = model.lr_statistic
    results["lrt_pvalue"] = np.nan if model.lr_statistic is None else model.lr_pvalue

    # 4. 模型评估
    data = df[[outcome] + predictors].dropna()
    X = data.drop(columns=[outcome])
    y = data[outcome]
    if cat_vars:
        X = pd.get_dummies(X, columns=cat_vars, drop_first=True)
    X_with_const = sm.add_constant(X)
    results["evaluation"] = evaluate_logistic_model(model, X_with_const, y)

    return results


# ============================================================================
# 示例用法
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 模拟数据
    np.random.seed(42)
    n = 200
    df_demo = pd.DataFrame(
        {
            "outcome": np.random.binomial(1, 0.3, n),
            "age": np.random.normal(60, 10, n),
            "bmi": np.random.normal(25, 5, n),
            "sex": np.random.choice(["M", "F"], n),
            "treatment": np.random.binomial(1, 0.5, n),
        }
    )

    # 完整工作流
    res = full_logistic_workflow(
        df_demo,
        outcome="outcome",
        predictors=["age", "bmi", "treatment"],
        cat_vars=["sex"],
    )

    logger.info("=== Logistic 回归结果 ===")
    logger.info(f"Pseudo R² (McFadden): {res['pseudo_r2']:.4f}")
    logger.info(f"AIC: {res['aic']:.2f}, BIC: {res['bic']:.2f}")
    logger.info(f"LRT p-value: {res['lrt_pvalue']:.4f}")
    logger.info("\n=== OR 表 ===")
    logger.info("%s %s %s %s %s %s", res["summary"][["Variable", "OR", "OR_Lower_95", "OR_Upper_95", "p_value", "Signif"]].to_string(index=False))
    logger.info(f"\n=== 模型评估 ===")
    logger.info(f"AUC: {res['evaluation']['auc']:.3f}")
    logger.info(f"Sensitivity: {res['evaluation']['sensitivity']:.3f}")
    logger.info(f"Specificity: {res['evaluation']['specificity']:.3f}")

    logger.info("\n✅ Logistic 回归分析完成")
