"""
roc_template.py — ROC 曲线与诊断试验分析模板
===============================================
适用于：二分类诊断试验的 accuracy 评估、最佳截断值选择、多模型比较

依赖: sklearn, pandas, numpy, matplotlib, scipy, statsmodels
安装: pip install sklearn pandas numpy matplotlib scipy statsmodels

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (
    auc,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.utils import resample
import logging

logger = logging.getLogger(__name__)

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# ============================================================================
# 1. 基本 ROC 分析
# ============================================================================


def compute_roc(
    y_true: np.ndarray, y_score: np.ndarray
) -> Dict:
    """计算 ROC 曲线数据

    Parameters
    ----------
    y_true : np.ndarray
        真实标签（0/1）
    y_score : np.ndarray
        预测概率或评分

    Returns
    -------
    Dict
        FPR, TPR, 阈值, AUC
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)

    return {
        "fpr": fpr,
        "tpr": tpr,
        "thresholds": thresholds,
        "auc": roc_auc,
    }


def get_best_threshold(
    y_true: np.ndarray,
    y_score: np.ndarray,
    method: str = "youden",
) -> Tuple[float, Dict]:
    """选择最佳截断值

    Parameters
    ----------
    y_true : np.ndarray
        真实标签
    y_score : np.ndarray
        预测概率
    method : str
        方法: 'youden' (Youden Index), 'closest_topleft' (距左上角最近),
               'cost' (最小代价)

    Returns
    -------
    Tuple[float, Dict]
        最佳阈值及其对应的指标
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_score)

    if method == "youden":
        youden_idx = tpr - fpr
        best_idx = np.argmax(youden_idx)
    elif method == "closest_topleft":
        dist = np.sqrt((1 - tpr) ** 2 + fpr ** 2)
        best_idx = np.argmin(dist)
    elif method == "cost":
        # 假设假阳性成本为假阴性的 1/2
        cost_ratio = 0.5
        prevalence = y_true.mean()
        cost = (
            fpr * (1 - prevalence) * cost_ratio
            + (1 - tpr) * prevalence * (1 - cost_ratio)
        )
        best_idx = np.argmin(cost)
    else:
        raise ValueError(f"Unknown method: {method}")

    best_threshold = thresholds[best_idx]
    y_pred = (y_score >= best_threshold).astype(int)
    metrics = compute_diagnostic_metrics(y_true, y_pred, y_score)

    return best_threshold, metrics


def compute_diagnostic_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_score: Optional[np.ndarray] = None,
) -> Dict:
    """计算诊断试验综合指标

    Parameters
    ----------
    y_true : np.ndarray
        真实标签
    y_pred : np.ndarray
        预测类别
    y_score : Optional[np.ndarray]
        预测概率（用于 AUC）

    Returns
    -------
    Dict
        所有诊断指标
    """
    cm = pd.crosstab(
        pd.Series(y_true, name="True"),
        pd.Series(y_pred, name="Predicted"),
    )

    tn = cm.iloc[0, 0] if 0 in cm.index and 0 in cm.columns else 0
    fp = cm.iloc[0, 1] if 0 in cm.index and 1 in cm.columns else 0
    fn = cm.iloc[1, 0] if 1 in cm.index and 0 in cm.columns else 0
    tp = cm.iloc[1, 1] if 1 in cm.index and 1 in cm.columns else 0

    n = tn + fp + fn + tp
    prevalence = (tp + fn) / n if n > 0 else 0

    metrics = {
        "sensitivity": tp / (tp + fn) if (tp + fn) > 0 else np.nan,
        "specificity": tn / (tn + fp) if (tn + fp) > 0 else np.nan,
        "ppv": tp / (tp + fp) if (tp + fp) > 0 else np.nan,
        "npv": tn / (tn + fn) if (tn + fn) > 0 else np.nan,
        "accuracy": (tp + tn) / n if n > 0 else np.nan,
        "prevalence": prevalence,
        "positive_lr": (tp / (tp + fn)) / (fp / (fp + tn))
        if (tp + fn) > 0 and (fp + tn) > 0 and fp > 0
        else np.nan,
        "negative_lr": (fn / (tp + fn)) / (tn / (fp + tn))
        if (tp + fn) > 0 and (fp + tn) > 0 and tn > 0
        else np.nan,
        "disease odds": (tp / (tp + fn)) / (fn / (tp + fn))
        if tp > 0 and fn > 0
        else np.nan,
        "f1_score": 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else np.nan,
        "confusion_matrix": pd.DataFrame(
            [[tn, fp], [fn, tp]],
            index=["True Negative", "True Positive"],
            columns=["Predicted Negative", "Predicted Positive"],
        ),
    }

    if y_score is not None:
        metrics["auc"] = roc_auc_score(y_true, y_score)

    return metrics


# ============================================================================
# 2. AUC 比较与置信区间
# ============================================================================


def auc_ci(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_bootstrap: int = 2000,
    alpha: float = 0.05,
) -> Dict:
    """用 Bootstrap 计算 AUC 的置信区间

    Parameters
    ----------
    y_true : np.ndarray
        真实标签
    y_score : np.ndarray
        预测概率
    n_bootstrap : int
        Bootstrap 重抽样次数
    alpha : float
        显著性水平

    Returns
    -------
    Dict
        AUC 及其置信区间
    """
    n = len(y_true)
    auc_scores = np.zeros(n_bootstrap)
    auc_obs = roc_auc_score(y_true, y_score)

    for i in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        # 确保 bootstrap 样本中两类都有
        if len(np.unique(y_true[idx])) < 2:
            continue
        try:
            auc_scores[i] = roc_auc_score(y_true[idx], y_score[idx])
        except Exception:
            continue

    auc_scores = auc_scores[auc_scores > 0]
    lower = np.percentile(auc_scores, 100 * alpha / 2)
    upper = np.percentile(auc_scores, 100 * (1 - alpha / 2))
    se = np.std(auc_scores)

    return {
        "auc": auc_obs,
        "ci_lower": lower,
        "ci_upper": upper,
        "se": se,
        "bootstrap_samples": auc_scores,
    }


def compare_two_aucs(
    y_true: np.ndarray,
    score1: np.ndarray,
    score2: np.ndarray,
    method: str = "delong",
    n_bootstrap: int = 2000,
) -> Dict:
    """比较两个模型的 AUC

    Parameters
    ----------
    y_true : np.ndarray
        真实标签
    score1 : np.ndarray
        模型 1 预测概率
    score2 : np.ndarray
        模型 2 预测概率
    method : str
        方法: 'delong' (DeLong 检验), 'bootstrap' (Bootstrap 检验)
    n_bootstrap : int
        Bootstrap 重抽样次数（仅 method='bootstrap' 时使用）

    Returns
    -------
    Dict
        比较结果
    """
    auc1 = roc_auc_score(y_true, score1)
    auc2 = roc_auc_score(y_true, score2)

    if method == "delong":
        # 实现 DeLong 检验（简化版）
        from scipy import stats as sc_stats

        n1 = np.sum(y_true == 1)
        n0 = np.sum(y_true == 0)

        # 计算两组秩
        r1_1 = stats.rankdata(score1[y_true == 1])
        r1_0 = stats.rankdata(score1[y_true == 0])
        r2_1 = stats.rankdata(score2[y_true == 1])
        r2_0 = stats.rankdata(score2[y_true == 0])

        # 计算方差协方差矩阵
        v10 = np.var(r1_0) / n0
        v20 = np.var(r2_0) / n0
        v11 = np.var(r1_1) / n1
        v21 = np.var(r2_1) / n1

        c10 = np.cov(r1_0, r2_0)[0, 1] / n0 if n0 > 1 else 0
        c11 = np.cov(r1_1, r2_1)[0, 1] / n1 if n1 > 1 else 0

        var_diff = v10 + v20 - 2 * c10 + v11 + v21 - 2 * c11
        z = (auc1 - auc2) / np.sqrt(var_diff) if var_diff > 0 else 0
        p_value = 2 * (1 - sc_stats.norm.cdf(abs(z)))

        return {
            "auc1": auc1,
            "auc2": auc2,
            "auc_diff": auc1 - auc2,
            "z_statistic": z,
            "p_value": p_value,
            "method": "DeLong",
        }

    elif method == "bootstrap":
        n = len(y_true)
        diffs = np.zeros(n_bootstrap)
        for i in range(n_bootstrap):
            idx = np.random.choice(n, n, replace=True)
            if len(np.unique(y_true[idx])) < 2:
                continue
            try:
                a1 = roc_auc_score(y_true[idx], score1[idx])
                a2 = roc_auc_score(y_true[idx], score2[idx])
                diffs[i] = a1 - a2
            except Exception:
                continue

        diffs = diffs[~np.isnan(diffs)]
        ci_lower = np.percentile(diffs, 2.5)
        ci_upper = np.percentile(diffs, 97.5)
        p_value = 2 * min(
            np.mean(diffs >= 0), np.mean(diffs <= 0)
        )

        return {
            "auc1": auc1,
            "auc2": auc2,
            "auc_diff": auc1 - auc2,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "p_value": p_value,
            "method": "Bootstrap",
        }

    else:
        raise ValueError(f"Unknown method: {method}")


# ============================================================================
# 3. 多模型 ROC 比较
# ============================================================================


def compare_multiple_models(
    y_true: np.ndarray,
    model_scores: Dict[str, np.ndarray],
) -> pd.DataFrame:
    """比较多个模型的 ROC-AUC

    Parameters
    ----------
    y_true : np.ndarray
        真实标签
    model_scores : Dict[str, np.ndarray]
        模型名到预测概率的映射

    Returns
    -------
    pd.DataFrame
        各模型的 AUC 排名表
    """
    results = []
    for name, score in model_scores.items():
        roc_auc = roc_auc_score(y_true, score)
        auc_info = auc_ci(y_true, score)
        results.append(
            {
                "Model": name,
                "AUC": roc_auc,
                "AUC_Lower_95": auc_info["ci_lower"],
                "AUC_Upper_95": auc_info["ci_upper"],
                "AUC_SE": auc_info["se"],
            }
        )

    df = pd.DataFrame(results).sort_values("AUC", ascending=False)
    df["Rank"] = range(1, len(df) + 1)
    df["AUC_CI"] = df.apply(
        lambda r: f"{r['AUC']:.3f} ({r['AUC_Lower_95']:.3f}, {r['AUC_Upper_95']:.3f})",
        axis=1,
    )
    return df


# ============================================================================
# 4. 校准曲线
# ============================================================================


def calibration_curve(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_bins: int = 10,
) -> pd.DataFrame:
    """计算校准曲线

    Parameters
    ----------
    y_true : np.ndarray
        真实标签
    y_score : np.ndarray
        预测概率
    n_bins : int
        分箱数

    Returns
    -------
    pd.DataFrame
        校准曲线数据（每箱的预测概率均值 vs 实际事件率）
    """
    from sklearn.calibration import calibration_curve as sk_calibration

    prob_true, prob_pred = sk_calibration(y_true, y_score, n_bins=n_bins, strategy="quantile")

    return pd.DataFrame(
        {
            "Predicted_Prob": prob_pred,
            "Observed_Fraction": prob_true,
            "Ideal": prob_pred,
        }
    )


# ============================================================================
# 5. 完整工作流示例
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 模拟两组诊断数据
    np.random.seed(42)
    n = 300

    # 健康对照
    controls = np.random.normal(30, 10, n // 2)
    # 疾病组
    patients = np.random.normal(70, 15, n // 2)

    y_true = np.concatenate([np.zeros(n // 2), np.ones(n // 2)])
    y_score = np.concatenate([controls, patients])
    y_score = (y_score - y_score.min()) / (y_score.max() - y_score.min())

    # 1. ROC 分析
    roc_result = compute_roc(y_true, y_score)
    logger.info(f"=== ROC 分析 ===")
    logger.info(f"AUC: {roc_result['auc']:.4f}")

    # 2. 最佳截断值
    best_th, metrics = get_best_threshold(y_true, y_score, method="youden")
    logger.info(f"\n=== 最佳截断值 (Youden Index) ===")
    logger.info(f"Threshold: {best_th:.4f}")
    logger.info(f"Sensitivity: {metrics['sensitivity']:.3f}")
    logger.info(f"Specificity: {metrics['specificity']:.3f}")
    logger.info(f"PPV: {metrics['ppv']:.3f}")
    logger.info(f"NPV: {metrics['npv']:.3f}")
    logger.info(f"Accuracy: {metrics['accuracy']:.3f}")

    # 3. AUC 置信区间
    auc_result = auc_ci(y_true, y_score)
    logger.info(f"\n=== AUC 置信区间 ===")
    logger.info(f"AUC = {auc_result['auc']:.3f} (95% CI: {auc_result['ci_lower']:.3f}, {auc_result['ci_upper']:.3f})")

    # 4. 模型比较（模拟两个模型）
    score2 = y_score + np.random.normal(0, 0.05, len(y_score))
    score2 = np.clip(score2, 0, 1)
    comp = compare_two_aucs(y_true, y_score, score2, method="delong")
    logger.info(f"\n=== AUC 比较 ===")
    logger.info(f"Model 1 AUC: {comp['auc1']:.3f}, Model 2 AUC: {comp['auc2']:.3f}")
    logger.info(f"Difference: {comp['auc_diff']:.3f}, p = {comp['p_value']:.4f}")

    # 5. 校准曲线
    cal_df = calibration_curve(y_true, y_score)
    logger.info(f"\n=== 校准曲线 ===")
    logger.info("cal_df.round(3).to_string(index=False)")

    logger.info("\n✅ ROC 诊断分析完成")
