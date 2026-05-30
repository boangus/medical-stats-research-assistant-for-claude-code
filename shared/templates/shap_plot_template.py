"""
shap_plot_template.py — SHAP 可视化模板（Python）
==================================================
适用于：机器学习模型的可解释性分析、特征重要性评估

支持图表类型：
  1. Summary Plot (蜂群图): 全局特征重要性 + 方向
  2. Dependence Plot: 单个特征与 SHAP 值的关系
  3. Waterfall Plot: 单个样本的预测分解
  4. Force Plot: 单个样本的预测分解 (HTML)
  5. Bar Plot: 简单特征重要性条形图
  6. Beeswarm Plot: 与 Summary Plot 类似但更精细

依赖: numpy, pandas, sklearn, shap, matplotlib
安装: pip install numpy pandas scikit-learn shap matplotlib

作者: MSRA Team
版本: 0.1.0

使用场景：
  - 预测模型开发后，解释哪些特征对预测贡献最大
  - 亚组分析中，理解异质性处理效应的来源
  - 临床预测模型的可解释性报告
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# ============================================================================
# 1. SHAP 计算
# ============================================================================


def compute_shap_values(
    model: Any,
    X: pd.DataFrame,
    model_type: str = "tree",
    background_data: Optional[pd.DataFrame] = None,
    n_samples: int = 100,
) -> Any:
    """计算 SHAP 值

    Parameters
    ----------
    model : Any
        训练好的 sklearn/xgboost/lightgbm 模型
    X : pd.DataFrame
        解释数据集
    model_type : str
        'tree' (XGBoost/LightGBM/Random Forest) 或 'linear'/'kernel'
    background_data : Optional[pd.DataFrame]
        KernelExplainer 的背景数据（仅 kernel 模式需要）
    n_samples : int
        KernelExplainer 的采样数

    Returns
    -------
    shap.Explanation 或 shap.ShapleyExplanation
        SHAP 值对象
    """
    import shap

    if model_type == "tree":
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
    elif model_type == "linear":
        explainer = shap.LinearExplainer(model, X)
        shap_values = explainer.shap_values(X)
    elif model_type == "kernel":
        if background_data is None:
            # 随机采样作为背景
            bg = shap.sample(X, min(100, len(X)))
        else:
            bg = background_data
        explainer = shap.KernelExplainer(model.predict_proba, bg)
        shap_values = explainer.shap_values(X.iloc[:n_samples])
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    return shap_values, explainer


# ============================================================================
# 2. Summary Plot (蜂群图)
# ============================================================================


def plot_summary(
    shap_values: Any,
    X: pd.DataFrame,
    feature_names: Optional[List[str]] = None,
    max_display: int = 20,
    title: str = "SHAP Summary Plot",
    figsize: Tuple[float, float] = (10, 8),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """SHAP Summary Plot (蜂群图)

    展示每个特征对预测的贡献方向和大小：
    - x 轴: SHAP 值（正=推高预测，负=拉低预测）
    - 颜色: 特征值（红=高，蓝=低）
    - 每个点: 一个样本

    Parameters
    ----------
    shap_values : Any
        compute_shap_values 的输出
    X : pd.DataFrame
        特征数据
    feature_names : Optional[List[str]]
        特征名列表
    max_display : int
        最多展示的特征数
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
    import shap

    fig, ax = plt.subplots(figsize=figsize)

    shap.summary_plot(
        shap_values,
        X,
        feature_names=feature_names,
        max_display=max_display,
        show=False,
    )

    plt.title(title, fontsize=13, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Summary Plot saved to: {save_path}")

    if show:
        plt.show()

    return plt.gcf()


# ============================================================================
# 3. Bar Plot (特征重要性条形图)
# ============================================================================


def plot_bar(
    shap_values: Any,
    X: pd.DataFrame,
    feature_names: Optional[List[str]] = None,
    max_display: int = 20,
    title: str = "SHAP Feature Importance (Bar)",
    figsize: Tuple[float, float] = (8, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """SHAP Bar Plot

    简单的特征重要性条形图（基于 |SHAP| 均值）。

    Parameters
    ----------
    shap_values : Any
        compute_shap_values 的输出
    X : pd.DataFrame
        特征数据
    feature_names : Optional[List[str]]
        特征名列表
    max_display : int
        最多展示的特征数
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
    import shap

    fig, ax = plt.subplots(figsize=figsize)

    shap.summary_plot(
        shap_values,
        X,
        feature_names=feature_names,
        plot_type="bar",
        max_display=max_display,
        show=False,
    )

    plt.title(title, fontsize=13, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Bar Plot saved to: {save_path}")

    if show:
        plt.show()

    return plt.gcf()


# ============================================================================
# 4. Dependence Plot (特征依赖图)
# ============================================================================


def plot_dependence(
    shap_values: Any,
    X: pd.DataFrame,
    feature: str,
    interaction_feature: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (8, 5),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """SHAP Dependence Plot

    展示单个特征值与 SHAP 值的关系：
    - x 轴: 特征值
    - y 轴: SHAP 值
    - 颜色: 交互特征值（可选）

    Parameters
    ----------
    shap_values : Any
        compute_shap_values 的输出
    X : pd.DataFrame
        特征数据
    feature : str
        要展示的特征名
    interaction_feature : Optional[str]
        交互特征名（用于颜色编码）
    title : Optional[str]
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
    import shap

    fig, ax = plt.subplots(figsize=figsize)

    shap.dependence_plot(
        feature,
        shap_values,
        X,
        interaction_index=interaction_feature,
        show=False,
    )

    plt.title(title or f"SHAP Dependence: {feature}",
              fontsize=13, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Dependence Plot saved to: {save_path}")

    if show:
        plt.show()

    return plt.gcf()


# ============================================================================
# 5. Waterfall Plot (单样本分解)
# ============================================================================


def plot_waterfall(
    shap_values: Any,
    X: pd.DataFrame,
    index: int = 0,
    max_display: int = 15,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (8, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """SHAP Waterfall Plot

    展示单个样本的预测分解：每个特征如何将基线预测推向最终预测。

    Parameters
    ----------
    shap_values : Any
        compute_shap_values 的输出
    X : pd.DataFrame
        特征数据
    index : int
        要解释的样本索引
    max_display : int
        最多展示的特征数
    title : Optional[str]
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
    import shap

    fig, ax = plt.subplots(figsize=figsize)

    # 获取单个样本的 SHAP 值
    if isinstance(shap_values, list):
        sv = shap_values[0][index]  # 二分类取 class 1
    elif hasattr(shap_values, 'values'):
        sv = shap_values[index]
    else:
        sv = shap_values[index]

    shap.waterfall_plot(
        sv,
        max_display=max_display,
        show=False,
    )

    plt.title(title or f"SHAP Waterfall: Sample #{index}",
              fontsize=13, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Waterfall Plot saved to: {save_path}")

    if show:
        plt.show()

    return plt.gcf()


# ============================================================================
# 6. 特征重要性汇总表
# ============================================================================


def feature_importance_table(
    shap_values: Any,
    X: pd.DataFrame,
    feature_names: Optional[List[str]] = None,
    top_n: Optional[int] = None,
) -> pd.DataFrame:
    """生成 SHAP 特征重要性汇总表

    Parameters
    ----------
    shap_values : Any
        compute_shap_values 的输出
    X : pd.DataFrame
        特征数据
    feature_names : Optional[List[str]]
        特征名列表
    top_n : Optional[int]
        返回前 N 个特征

    Returns
    -------
    pd.DataFrame
        包含 Feature, Mean_SHAP, Std_SHAP, Mean_abs_SHAP, Rank
    """
    if hasattr(shap_values, 'values'):
        sv = shap_values.values
    elif isinstance(shap_values, np.ndarray):
        sv = shap_values
    else:
        sv = np.array(shap_values)

    if feature_names is None:
        feature_names = X.columns.tolist()

    # 如果是二分类，取 class 1 的 SHAP 值
    if sv.ndim == 3:
        sv = sv[:, :, 1]

    mean_shap = np.mean(sv, axis=0)
    std_shap = np.std(sv, axis=0)
    mean_abs = np.mean(np.abs(sv), axis=0)

    df = pd.DataFrame({
        "Feature": feature_names[:len(mean_shap)],
        "Mean_SHAP": mean_shap,
        "Std_SHAP": std_shap,
        "Mean_abs_SHAP": mean_abs,
    })

    df["Rank"] = df["Mean_abs_SHAP"].rank(ascending=False).astype(int)
    df = df.sort_values("Rank")

    if top_n:
        df = df.head(top_n)

    return df.reset_index(drop=True)


# ============================================================================
# 7. 完整 SHAP 分析工作流
# ============================================================================


def full_shap_workflow(
    model: Any,
    X: pd.DataFrame,
    y: Optional[pd.Series] = None,
    model_type: str = "tree",
    feature_names: Optional[List[str]] = None,
    max_display: int = 20,
    output_dir: Optional[str] = None,
) -> Dict:
    """完整 SHAP 分析工作流

    步骤: SHAP 计算 → Summary → Bar → Top Dependence → Waterfall → 汇总表

    Parameters
    ----------
    model : Any
        训练好的模型
    X : pd.DataFrame
        解释数据集
    y : Optional[pd.Series]
        标签（用于打印模型性能）
    model_type : str
        模型类型
    feature_names : Optional[List[str]]
        特征名
    max_display : int
        最多展示的特征数
    output_dir : Optional[str]
        输出目录

    Returns
    -------
    Dict
        包含所有图表和汇总表
    """
    results = {}

    # Step 1: 计算 SHAP 值
    print("=" * 60)
    print("Step 1: 计算 SHAP 值")
    print("=" * 60)
    shap_values, explainer = compute_shap_values(model, X, model_type)
    results["shap_values"] = shap_values
    results["explainer"] = explainer

    # Step 2: Summary Plot
    print("\n" + "=" * 60)
    print("Step 2: SHAP Summary Plot")
    print("=" * 60)
    save_path = f"{output_dir}/shap_summary.png" if output_dir else None
    results["summary_plot"] = plot_summary(
        shap_values, X, feature_names, max_display,
        save_path=save_path, show=False)

    # Step 3: Bar Plot
    print("\n" + "=" * 60)
    print("Step 3: SHAP Bar Plot")
    print("=" * 60)
    save_path = f"{output_dir}/shap_bar.png" if output_dir else None
    results["bar_plot"] = plot_bar(
        shap_values, X, feature_names, max_display,
        save_path=save_path, show=False)

    # Step 4: Top 3 Dependence Plots
    print("\n" + "=" * 60)
    print("Step 4: SHAP Dependence Plots (Top 3)")
    print("=" * 60)
    imp_table = feature_importance_table(shap_values, X, feature_names)
    results["importance_table"] = imp_table

    top_features = imp_table["Feature"].head(3).tolist()
    results["dependence_plots"] = {}

    for feat in top_features:
        save_path = f"{output_dir}/shap_dependence_{feat}.png" if output_dir else None
        results["dependence_plots"][feat] = plot_dependence(
            shap_values, X, feat,
            save_path=save_path, show=False)

    # Step 5: Waterfall Plot (first sample)
    print("\n" + "=" * 60)
    print("Step 5: SHAP Waterfall Plot (Sample #0)")
    print("=" * 60)
    save_path = f"{output_dir}/shap_waterfall.png" if output_dir else None
    results["waterfall_plot"] = plot_waterfall(
        shap_values, X, index=0,
        save_path=save_path, show=False)

    # 打印汇总
    print("\n=== SHAP 特征重要性汇总 ===")
    print(imp_table.to_string(index=False))

    print("\n✅ SHAP 分析完成")
    return results


# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
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

    # 训练模型
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print(f"Model accuracy: {model.score(X_test, y_test):.3f}")

    # 运行 SHAP 分析
    results = full_shap_workflow(
        model, X_test, y_test,
        model_type="tree",
        max_display=10,
    )
