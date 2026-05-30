"""
ml_analysis_template.py — 机器学习分析模板（Python）
=====================================================
适用于：医学预测模型开发、特征选择、模型比较

支持模型：
  1. Logistic 回归 (基线)
  2. Random Forest
  3. XGBoost
  4. LightGBM
  5. 支持向量机 (SVM)
  6. Elastic Net

支持任务：
  - 二分类预测 (主要)
  - 特征重要性 (MDI / Permutation / SHAP)
  - 模型比较 (AUC / Accuracy / F1 / Brier Score)
  - 交叉验证 + 超参数调优
  - 校准曲线 (Calibration Curve)

依赖: numpy, pandas, sklearn, xgboost, lightgbm, shap, matplotlib
安装: pip install numpy pandas scikit-learn xgboost lightgbm shap matplotlib

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

warnings.filterwarnings("ignore")


# ============================================================================
# 1. 模型训练
# ============================================================================


def train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    models: Optional[Dict[str, Any]] = None,
    random_state: int = 42,
) -> Dict[str, Any]:
    """训练多个模型

    Parameters
    ----------
    X_train : pd.DataFrame
        训练特征
    y_train : pd.Series
        训练标签
    models : Optional[Dict[str, Any]]
        自定义模型字典。None 时使用默认模型集
    random_state : int
        随机种子

    Returns
    -------
    Dict[str, Any]
        训练好的模型字典 {name: model}
    """
    if models is None:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC

        models = {
            "Logistic Regression": LogisticRegression(
                max_iter=1000, random_state=random_state),
            "Random Forest": RandomForestClassifier(
                n_estimators=100, random_state=random_state),
            "SVM (RBF)": SVC(
                probability=True, random_state=random_state),
        }

        # 尝试导入 XGBoost 和 LightGBM
        try:
            import xgboost as xgb
            models["XGBoost"] = xgb.XGBClassifier(
                n_estimators=100, use_label_encoder=False,
                eval_metric="logloss", random_state=random_state)
        except ImportError:
            pass

        try:
            import lightgbm as lgb
            models["LightGBM"] = lgb.LGBMClassifier(
                n_estimators=100, random_state=random_state, verbose=-1)
        except ImportError:
            pass

    trained = {}
    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        trained[name] = model

    print(f"  ✅ 训练完成: {list(trained.keys())}")
    return trained


# ============================================================================
# 2. 模型评估
# ============================================================================


def evaluate_models(
    models: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    average: str = "binary",
) -> pd.DataFrame:
    """评估多个模型性能

    Parameters
    ----------
    models : Dict[str, Any]
        训练好的模型字典
    X_test : pd.DataFrame
        测试特征
    y_test : pd.Series
        测试标签
    average : str
        F1/Precision/Recall 的 average 参数

    Returns
    -------
    pd.DataFrame
        模型性能对比表
    """
    results = []

    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        auc = roc_auc_score(y_test, y_prob)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average=average)
        prec = precision_score(y_test, y_pred, average=average, zero_division=0)
        rec = recall_score(y_test, y_pred, average=average, zero_division=0)
        brier = brier_score_loss(y_test, y_prob)

        results.append({
            "Model": name,
            "AUC": auc,
            "Accuracy": acc,
            "F1": f1,
            "Precision": prec,
            "Recall": rec,
            "Brier_Score": brier,
        })

    df = pd.DataFrame(results).sort_values("AUC", ascending=False)
    return df


def cross_validate_models(
    X: pd.DataFrame,
    y: pd.Series,
    models: Optional[Dict[str, Any]] = None,
    cv: int = 5,
    scoring: str = "roc_auc",
    random_state: int = 42,
) -> pd.DataFrame:
    """交叉验证评估

    Parameters
    ----------
    X : pd.DataFrame
        全部特征
    y : pd.Series
        全部标签
    models : Optional[Dict[str, Any]]
        模型字典
    cv : int
        折数
    scoring : str
        评估指标
    random_state : int
        随机种子

    Returns
    -------
    pd.DataFrame
        交叉验证结果表
    """
    from sklearn.model_selection import cross_val_score

    if models is None:
        trained = train_models(X, y, random_state=random_state)
    else:
        trained = models

    results = []
    for name, model in trained.items():
        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
        results.append({
            "Model": name,
            "Mean_CV_AUC": scores.mean(),
            "Std_CV_AUC": scores.std(),
            "Min_CV_AUC": scores.min(),
            "Max_CV_AUC": scores.max(),
        })

    return pd.DataFrame(results).sort_values("Mean_CV_AUC", ascending=False)


# ============================================================================
# 3. 特征重要性
# ============================================================================


def feature_importance(
    model: Any,
    feature_names: List[str],
    method: str = "mdi",
    X_test: Optional[pd.DataFrame] = None,
    y_test: Optional[pd.Series] = None,
    top_n: Optional[int] = None,
) -> pd.DataFrame:
    """提取特征重要性

    Parameters
    ----------
    model : Any
        训练好的模型
    feature_names : List[str]
        特征名列表
    method : str
        'mdi' (Mean Decrease Impurity) 或 'permutation'
    X_test : Optional[pd.DataFrame]
        测试集（permutation 需要）
    y_test : Optional[pd.Series]
        测试标签（permutation 需要）
    top_n : Optional[int]
        返回前 N 个特征

    Returns
    -------
    pd.DataFrame
        特征重要性表
    """
    if method == "mdi":
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_[0])
        else:
            raise ValueError("Model does not support MDI feature importance")
    elif method == "permutation":
        from sklearn.inspection import permutation_importance
        if X_test is None or y_test is None:
            raise ValueError("permutation method requires X_test and y_test")
        result = permutation_importance(model, X_test, y_test, n_repeats=10,
                                        random_state=42)
        importances = result.importances_mean
    else:
        raise ValueError(f"Unsupported method: {method}")

    df = pd.DataFrame({
        "Feature": feature_names[:len(importances)],
        "Importance": importances,
    }).sort_values("Importance", ascending=False)

    df["Rank"] = range(1, len(df) + 1)

    if top_n:
        df = df.head(top_n)

    return df.reset_index(drop=True)


# ============================================================================
# 4. ROC 曲线
# ============================================================================


def plot_roc_comparison(
    models: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    title: str = "ROC Curve Comparison",
    figsize: Tuple[float, float] = (8, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """多模型 ROC 曲线对比

    Parameters
    ----------
    models : Dict[str, Any]
        训练好的模型字典
    X_test : pd.DataFrame
        测试特征
    y_test : pd.Series
        测试标签
    title : str
        图表标题
    figsize : Tuple[float, float]
        图片尺寸
    show : bool
        是否显示
    save_path : Optional[str]
        保存路径

    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    colors = plt.cm.Set1(np.linspace(0, 1, len(models)))

    for (name, model), color in zip(models.items(), colors):
        y_prob = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        auc = roc_auc_score(y_test, y_prob)
        ax.plot(fpr, tpr, color=color, lw=2,
                label=f"{name} (AUC = {auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Chance")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  ROC Curve saved to: {save_path}")

    if show:
        plt.show()

    return fig


# ============================================================================
# 5. 校准曲线
# ============================================================================


def plot_calibration(
    models: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_bins: int = 10,
    title: str = "Calibration Curve",
    figsize: Tuple[float, float] = (8, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """校准曲线 (Reliability Diagram)

    Parameters
    ----------
    models : Dict[str, Any]
        训练好的模型字典
    X_test : pd.DataFrame
        测试特征
    y_test : pd.Series
        测试标签
    n_bins : int
        分箱数
    title : str
        图表标题
    figsize : Tuple[float, float]
        图片尺寸
    show : bool
        是否显示
    save_path : Optional[str]
        保存路径

    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    colors = plt.cm.Set1(np.linspace(0, 1, len(models)))

    for (name, model), color in zip(models.items(), colors):
        y_prob = model.predict_proba(X_test)[:, 1]
        fraction_pos, mean_pred = calibration_curve(y_test, y_prob, n_bins=n_bins)
        brier = brier_score_loss(y_test, y_prob)
        ax.plot(mean_pred, fraction_pos, "s-", color=color, lw=2,
                label=f"{name} (Brier = {brier:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Perfectly Calibrated")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Calibration Curve saved to: {save_path}")

    if show:
        plt.show()

    return fig


# ============================================================================
# 6. 完整 ML 分析工作流
# ============================================================================


def full_ml_workflow(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    models: Optional[Dict[str, Any]] = None,
    feature_names: Optional[List[str]] = None,
    cv: int = 5,
    output_dir: Optional[str] = None,
) -> Dict:
    """完整机器学习分析工作流

    步骤: 训练 → 评估 → 交叉验证 → 特征重要性 → ROC → 校准 → SHAP

    Parameters
    ----------
    X_train : pd.DataFrame
        训练特征
    y_train : pd.Series
        训练标签
    X_test : pd.DataFrame
        测试特征
    y_test : pd.Series
        测试标签
    models : Optional[Dict[str, Any]]
        自定义模型集
    feature_names : Optional[List[str]]
        特征名
    cv : int
        交叉验证折数
    output_dir : Optional[str]
        输出目录

    Returns
    -------
    Dict
        完整分析结果
    """
    results = {}

    if feature_names is None:
        feature_names = X_train.columns.tolist()

    # Step 1: 训练模型
    print("=" * 60)
    print("Step 1: 训练模型")
    print("=" * 60)
    trained_models = train_models(X_train, y_train, models)
    results["models"] = trained_models

    # Step 2: 评估
    print("\n" + "=" * 60)
    print("Step 2: 模型评估")
    print("=" * 60)
    eval_table = evaluate_models(trained_models, X_test, y_test)
    results["evaluation"] = eval_table
    print(eval_table.to_string(index=False))

    # Step 3: 交叉验证
    print("\n" + "=" * 60)
    print(f"Step 3: {cv}-Fold 交叉验证")
    print("=" * 60)
    X_all = pd.concat([X_train, X_test], axis=0)
    y_all = pd.concat([y_train, y_test], axis=0)
    cv_table = cross_validate_models(X_all, y_all, trained_models, cv=cv)
    results["cross_validation"] = cv_table
    print(cv_table.to_string(index=False))

    # Step 4: 特征重要性 (基于最佳模型)
    print("\n" + "=" * 60)
    print("Step 4: 特征重要性")
    print("=" * 60)
    best_model_name = eval_table.iloc[0]["Model"]
    best_model = trained_models[best_model_name]

    try:
        imp_table = feature_importance(best_model, feature_names, method="mdi")
        results["feature_importance"] = imp_table
        print(f"  最佳模型: {best_model_name}")
        print(imp_table.to_string(index=False))
    except (ValueError, AttributeError):
        print(f"  ⚠️ {best_model_name} 不支持 MDI 特征重要性")

    # Step 5: ROC 曲线
    print("\n" + "=" * 60)
    print("Step 5: ROC 曲线对比")
    print("=" * 60)
    save_path = f"{output_dir}/ml_roc_comparison.png" if output_dir else None
    results["roc_plot"] = plot_roc_comparison(
        trained_models, X_test, y_test, save_path=save_path, show=False)

    # Step 6: 校准曲线
    print("\n" + "=" * 60)
    print("Step 6: 校准曲线")
    print("=" * 60)
    save_path = f"{output_dir}/ml_calibration.png" if output_dir else None
    results["calibration_plot"] = plot_calibration(
        trained_models, X_test, y_test, save_path=save_path, show=False)

    # Step 7: SHAP (如果可用)
    try:
        print("\n" + "=" * 60)
        print("Step 7: SHAP 可解释性分析")
        print("=" * 60)
        from shap_plot_template import full_shap_workflow
        save_path = output_dir if output_dir else None
        shap_results = full_shap_workflow(
            best_model, X_test, y_test,
            model_type="tree" if hasattr(best_model, "feature_importances_") else "kernel",
            output_dir=save_path)
        results["shap"] = shap_results
    except ImportError:
        print("  ⚠️ shap 未安装，跳过 SHAP 分析")

    print("\n✅ 机器学习分析完成")
    return results


# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    # 模拟数据
    np.random.seed(42)
    X_sim, y_sim = make_classification(
        n_samples=500, n_features=10, n_informative=5,
        n_redundant=2, random_state=42)
    feature_names = [f"Feature_{i}" for i in range(X_sim.shape[1])]
    X_df = pd.DataFrame(X_sim, columns=feature_names)
    y_series = pd.Series(y_sim)

    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y_series, test_size=0.3, random_state=42)

    print(f"训练集: {X_train.shape[0]} 样本, 测试集: {X_test.shape[0]} 样本")
    print(f"阳性率: {y_train.mean():.1%} (训练), {y_test.mean():.1%} (测试)")
    print()

    # 运行完整 ML 分析
    results = full_ml_workflow(X_train, y_train, X_test, y_test, cv=5)
