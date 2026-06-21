"""
prediction_model_template.py — 临床预测模型完整模板（Python）
==============================================================
适用于：TRIPOD 合规的临床预测模型开发、验证与报告

参考文献：
  - Collins et al. (2024). Evaluation of clinical prediction models (part 1-3). BMJ.
  - TRIPOD+AI Statement (2024). BMJ.
  - Riley et al. (2020). Clinical Prediction Models. Springer.
  - pmsampsize: Sample size for prediction model development.
  - dcurves: Decision Curve Analysis (MSKCC-Epi-Bio).
  - simpleNomo: Python nomogram visualization.

完整工作流（TRIPOD Type 1/2）：
  Phase 1: 样本量评估 (EPV ≥ 10-20)
  Phase 2: 模型开发 (多模型比较)
  Phase 3: 内部验证 (Bootstrap optimism correction)
  Phase 4: 模型校准 (Calibration)
  Phase 5: 临床效用评估 (DCA + Clinical Impact Curve)
  Phase 6: 列线图可视化 (Nomogram)
  Phase 7: TRIPOD 合规报告

依赖: numpy, pandas, sklearn, matplotlib, scipy, dcurves, simpleNomo
安装: pip install numpy pandas scikit-learn matplotlib scipy dcurves simpleNomo

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
    roc_auc_score,
    roc_curve,
)
import logging

logger = logging.getLogger(__name__)

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. 样本量评估 (EPV)
# ============================================================================


def assess_sample_size(
    n_events: int,
    n_predictors: int,
    target_epv: float = 10.0,
    outcome_prevalence: Optional[float] = None,
    n_total: Optional[int] = None,
) -> Dict:
    """评估预测模型开发的样本量充分性

    基于 Riley et al. (2020) 的 EPV (Events Per Variable) 方法。

    Parameters
    ----------
    n_events : int
        结局事件数（阳性样本数）
    n_predictors : int
        候选预测因子数（含分类变量展开后的总列数）
    target_epv : float
        目标 EPV（通常 10-20）
    outcome_prevalence : Optional[float]
        结局发生率（0-1）
    n_total : Optional[int]
        总样本量

    Returns
    -------
    Dict
        样本量评估结果
    """
    epv = n_events / n_predictors if n_predictors > 0 else float("inf")

    if n_total and outcome_prevalence:
        expected_events = n_total * outcome_prevalence
        expected_epv = expected_events / n_predictors
    else:
        expected_events = None
        expected_epv = None

    # 判定
    if epv >= 20:
        assessment = "充分"
        risk = "低"
    elif epv >= 10:
        assessment = "基本充分"
        risk = "中"
    elif epv >= 5:
        assessment = "不足"
        risk = "高"
    else:
        assessment = "严重不足"
        risk = "极高"

    # 建议
    if epv < 10:
        min_events = int(target_epv * n_predictors)
        min_total = int(min_events / outcome_prevalence) if outcome_prevalence else None
        suggestion = (
            f"建议至少 {min_events} 个事件"
            + (f"（约 {min_total} 例样本）" if min_total else "")
        )
    else:
        suggestion = "样本量满足要求"

    return {
        "n_events": n_events,
        "n_predictors": n_predictors,
        "epv": epv,
        "target_epv": target_epv,
        "assessment": assessment,
        "risk": risk,
        "suggestion": suggestion,
        "prevalence": outcome_prevalence,
        "min_events_needed": int(target_epv * n_predictors) if epv < target_epv else n_events,
    }


# ============================================================================
# 2. 多模型开发与比较
# ============================================================================


def develop_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    models: Optional[Dict[str, Any]] = None,
    random_state: int = 42,
) -> Dict:
    """开发并比较多个预测模型

    Parameters
    ----------
    X_train, y_train : 训练集
    X_test, y_test : 测试集
    models : 自定义模型字典
    random_state : 随机种子

    Returns
    -------
    Dict
        包含训练好的模型和评估结果
    """
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC

    if models is None:
        models = {
            "Logistic Regression": LogisticRegression(
                max_iter=1000, random_state=random_state),
            "Random Forest": RandomForestClassifier(
                n_estimators=100, random_state=random_state),
            "Gradient Boosting": GradientBoostingClassifier(
                n_estimators=100, random_state=random_state),
        }

        try:
            import xgboost as xgb
            models["XGBoost"] = xgb.XGBClassifier(
                n_estimators=100, use_label_encoder=False,
                eval_metric="logloss", random_state=random_state)
        except ImportError:
            pass

    # 训练
    trained = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        trained[name] = model

    # 评估
    results = []
    for name, model in trained.items():
        y_prob = model.predict_proba(X_test)[:, 1]
        y_pred = model.predict(X_test)

        auc = roc_auc_score(y_test, y_prob)
        brier = brier_score_loss(y_test, y_prob)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        # 校准
        fraction_pos, mean_pred = calibration_curve(y_test, y_prob, n_bins=5)
        cal_slope, cal_intercept = _fit_calibration(y_test, y_prob)

        results.append({
            "Model": name,
            "AUC": auc,
            "Brier_Score": brier,
            "Accuracy": acc,
            "F1": f1,
            "Cal_Slope": cal_slope,
            "Cal_Intercept": cal_intercept,
        })

    eval_df = pd.DataFrame(results).sort_values("AUC", ascending=False)

    return {
        "models": trained,
        "evaluation": eval_df,
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
    }


def _fit_calibration(y_true, y_prob):
    """拟合校准曲线的斜率和截距"""
    from scipy import stats
    fraction_pos, mean_pred = calibration_curve(y_true, y_prob, n_bins=5)
    if len(mean_pred) < 2:
        return 1.0, 0.0
    slope, intercept, _, _, _ = stats.linregress(mean_pred, fraction_pos)
    return slope, intercept


# ============================================================================
# 3. 内部验证 (Bootstrap Optimism Correction)
# ============================================================================


def bootstrap_validation(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    n_bootstraps: int = 200,
    random_state: int = 42,
) -> Dict:
    """Bootstrap 内部验证（乐观校正）

    基于 Harrell (2015) 的方法：
    1. 从原始数据有放回抽样
    2. 在 bootstrap 样本上重新拟合模型
    3. 在原始数据上评估 bootstrap 模型
    4. 乐观值 = bootstrap 评估性能 - 原始训练性能

    Parameters
    ----------
    model : Any
        训练好的模型
    X, y : 原始数据
    n_bootstraps : int
        Bootstrap 次数

    Returns
    -------
    Dict
        校正后的性能指标
    """
    np.random.seed(random_state)

    # 原始性能
    y_prob_orig = model.predict_proba(X)[:, 1]
    auc_orig = roc_auc_score(y, y_prob_orig)
    brier_orig = brier_score_loss(y, y_prob_orig)

    optimism_auc_list = []
    optimism_brier_list = []

    for i in range(n_bootstraps):
        # Bootstrap 采样
        idx = np.random.choice(len(X), size=len(X), replace=True)
        oob_idx = np.setdiff1d(np.arange(len(X)), idx)

        if len(oob_idx) < 10:
            continue

        X_boot, y_boot = X.iloc[idx], y.iloc[idx]
        X_oob, y_oob = X.iloc[oob_idx], y.iloc[oob_idx]

        # 重新拟合
        from sklearn.base import clone
        model_boot = clone(model)
        model_boot.fit(X_boot, y_boot)

        # 在 bootstrap 样本上评估
        y_prob_boot = model_boot.predict_proba(X_boot)[:, 1]
        auc_boot = roc_auc_score(y_boot, y_prob_boot)
        brier_boot = brier_score_loss(y_boot, y_prob_boot)

        # 在 OOB 样本上评估
        y_prob_oob = model_boot.predict_proba(X_oob)[:, 1]
        auc_oob = roc_auc_score(y_oob, y_prob_oob)
        brier_oob = brier_score_loss(y_oob, y_prob_oob)

        optimism_auc_list.append(auc_boot - auc_oob)
        optimism_brier_list.append(brier_boot - brier_oob)

    optimism_auc = np.mean(optimism_auc_list) if optimism_auc_list else 0
    optimism_brier = np.mean(optimism_brier_list) if optimism_brier_list else 0

    auc_corrected = auc_orig - optimism_auc
    brier_corrected = brier_orig + optimism_brier

    return {
        "apparent_auc": auc_orig,
        "optimism_auc": optimism_auc,
        "corrected_auc": auc_corrected,
        "apparent_brier": brier_orig,
        "optimism_brier": optimism_brier,
        "corrected_brier": brier_corrected,
        "n_bootstraps": n_bootstraps,
        "optimism_auc_list": optimism_auc_list,
    }


# ============================================================================
# 4. 决策曲线分析 (DCA)
# ============================================================================


def decision_curve_analysis(
    y_true: pd.Series,
    y_prob: np.ndarray,
    model_name: str = "Model",
    thresholds: Optional[np.ndarray] = None,
    figsize: Tuple[float, float] = (10, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """决策曲线分析 (Decision Curve Analysis)

    评估模型在不同阈值概率下的临床净效益。

    Parameters
    ----------
    y_true : pd.Series
        真实标签
    y_prob : np.ndarray
        预测概率
    model_name : str
        模型名称
    thresholds : Optional[np.ndarray]
        阈值概率范围
    figsize : Tuple
        图片尺寸
    show : bool
        是否显示
    save_path : Optional[str]
        保存路径

    Returns
    -------
    plt.Figure
    """
    try:
        from dcurves import dca, plot_graphs

        df = pd.DataFrame({"outcome": y_true.values, model_name: y_prob})

        if thresholds is None:
            thresholds = np.arange(0.01, 0.99, 0.01)

        df_dca = dca(
            data=df,
            outcome="outcome",
            modelnames=[model_name],
            thresholds=thresholds,
        )

        fig, ax = plt.subplots(figsize=figsize)
        plot_graphs(plot_df=df_dca, graph_type="net_benefit")
        plt.title(f"Decision Curve Analysis — {model_name}", fontsize=13, fontweight="bold")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        if show:
            plt.show()

        return plt.gcf()

    except ImportError:
        # Fallback: 手动实现 DCA
        return _dca_manual(y_true.values, y_prob, model_name, thresholds,
                           figsize, show, save_path)


def _dca_manual(y_true, y_prob, model_name, thresholds, figsize, show, save_path):
    """手动实现 DCA（无 dcurves 依赖时）"""
    if thresholds is None:
        thresholds = np.arange(0.01, 0.99, 0.01)

    prevalence = y_true.mean()
    n = len(y_true)

    net_benefits = []
    for pt in thresholds:
        tp = np.sum((y_prob >= pt) & (y_true == 1))
        fp = np.sum((y_prob >= pt) & (y_true == 0))

        net_benefit = (tp / n) - (fp / n) * (pt / (1 - pt))
        net_benefits.append(net_benefit)

    # Treat all
    nb_all = prevalence - (1 - prevalence) * (thresholds / (1 - thresholds))
    # Treat none
    nb_none = np.zeros_like(thresholds)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(thresholds, net_benefits, "b-", lw=2, label=model_name)
    ax.plot(thresholds, nb_all, "r--", lw=1, label="Treat All")
    ax.plot(thresholds, nb_none, "k:", lw=1, label="Treat None")
    ax.set_xlabel("Threshold Probability")
    ax.set_ylabel("Net Benefit")
    ax.set_title(f"Decision Curve Analysis — {model_name}", fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xlim([0, 1])

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()

    return fig


# ============================================================================
# 5. 临床影响曲线 (Clinical Impact Curve)
# ============================================================================


def clinical_impact_curve(
    y_true: pd.Series,
    y_prob: np.ndarray,
    model_name: str = "Model",
    thresholds: Optional[np.ndarray] = None,
    n_per_threshold: int = 1000,
    figsize: Tuple[float, float] = (10, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """临床影响曲线 (Clinical Impact Curve)

    展示在每个阈值概率下，模型预测为高风险的人数和实际阳性人数。

    Parameters
    ----------
    y_true : pd.Series
        真实标签
    y_prob : np.ndarray
        预测概率
    model_name : str
        模型名称
    thresholds : Optional[np.ndarray]
        阈值概率范围
    n_per_threshold : int
        每个阈值对应的标准化人数
    figsize : Tuple
        图片尺寸
    show : bool
        是否显示
    save_path : Optional[str]
        保存路径

    Returns
    -------
    plt.Figure
    """
    if thresholds is None:
        thresholds = np.arange(0.01, 0.99, 0.01)

    n = len(y_true)
    prevalence = y_true.mean()

    n_high_risk = []
    n_true_pos = []

    for pt in thresholds:
        n_hr = np.sum(y_prob >= pt)
        n_tp = np.sum((y_prob >= pt) & (y_true == 1))
        n_high_risk.append(n_hr / n * n_per_threshold)
        n_true_pos.append(n_tp / n * n_per_threshold)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(thresholds, n_high_risk, "b-", lw=2,
            label=f"{model_name} — High risk")
    ax.plot(thresholds, n_true_pos, "r--", lw=2,
            label=f"{model_name} — True positives")
    ax.axhline(y=prevalence * n_per_threshold, color="grey", linestyle=":",
               lw=1, label="Prevalence")

    ax.set_xlabel("Threshold Probability")
    ax.set_ylabel(f"Number per {n_per_threshold}")
    ax.set_title(f"Clinical Impact Curve — {model_name}",
                 fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xlim([0, 1])

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()

    return fig


# ============================================================================
# 6. 列线图 (Nomogram)
# ============================================================================


def generate_nomogram(
    coefficients: Dict[str, float],
    variable_ranges: Dict[str, Tuple[float, float]],
    intercept: float,
    model_name: str = "Prediction Model",
    output_excel: Optional[str] = None,
    figsize: Tuple[float, float] = (12, 8),
    show: bool = True,
    save_path: Optional[str] = None,
) -> Optional[plt.Figure]:
    """生成列线图 (Nomogram)

    使用 simpleNomo 包或手动实现。

    Parameters
    ----------
    coefficients : Dict[str, float]
        模型系数 {变量名: 系数}
    variable_ranges : Dict[str, Tuple[float, float]]
        变量范围 {变量名: (最小值, 最大值)}
    intercept : float
        截距
    model_name : str
        模型名称
    output_excel : Optional[str]
        输出 Excel 路径（供 simpleNomo 使用）
    figsize : Tuple
        图片尺寸
    show : bool
        是否显示
    save_path : Optional[str]
        保存路径

    Returns
    -------
    plt.Figure 或 None
    """
    # 尝试使用 simpleNomo
    try:
        import simpleNomo
        if output_excel is None:
            output_excel = "nomogram_input.xlsx"

        # 生成 Excel 模板
        rows = []
        for var, coef in coefficients.items():
            lo, hi = variable_ranges.get(var, (0, 1))
            rows.append({
                "Variable": var,
                "Coefficient": coef,
                "Min": lo,
                "Max": hi,
            })
        df_template = pd.DataFrame(rows)
        df_template.to_excel(output_excel, index=False)

        nomo = simpleNomo.nomogram(path=output_excel)
        return None  # simpleNomo 自己生成图表

    except (ImportError, Exception):
        pass

    # 手动实现列线图
    vars_list = list(coefficients.keys())
    coefs = np.array([coefficients[v] for v in vars_list])

    # 标准化系数到 0-100 分
    max_abs_coef = np.max(np.abs(coefs))
    points = (coefs / max_abs_coef * 50 + 50).astype(int)
    total_max = np.sum(points)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, total_max + 10)
    ax.set_ylim(-0.5, len(vars_list) + 2.5)
    ax.axis("off")

    # Points 轴
    ax.plot([0, total_max], [len(vars_list) + 1.5, len(vars_list) + 1.5],
            "k-", lw=2)
    ax.text(-2, len(vars_list) + 1.5, "Points", fontsize=10, va="center",
            fontweight="bold")

    tick_positions = np.linspace(0, total_max, 11).astype(int)
    for tp in tick_positions:
        ax.plot([tp, tp], [len(vars_list) + 1.4, len(vars_list) + 1.6],
                "k-", lw=1)
        ax.text(tp, len(vars_list) + 1.7, str(tp), fontsize=8, ha="center")

    # 各变量轴
    cumulative = 0
    for i, var in enumerate(vars_list):
        y_pos = len(vars_list) - i
        lo, hi = variable_ranges.get(var, (0, 1))
        coef = coefficients[var]

        # 变量轴
        ax.plot([cumulative, cumulative + points[i]], [y_pos, y_pos],
                "b-", lw=3)

        # 标签
        ax.text(cumulative - 1, y_pos, var, fontsize=10, va="center",
                ha="right", fontweight="bold")

        # 刻度
        ax.text(cumulative, y_pos - 0.15, f"{lo:.1f}", fontsize=8, ha="center")
        ax.text(cumulative + points[i], y_pos - 0.15, f"{hi:.1f}",
                fontsize=8, ha="center")

        cumulative += points[i]

    # Total Points 轴
    ax.plot([0, total_max], [-0.5, -0.5], "k-", lw=2)
    ax.text(-2, -0.5, "Total Points", fontsize=10, va="center",
            fontweight="bold")

    tick_positions = np.linspace(0, total_max, 11).astype(int)
    for tp in tick_positions:
        ax.plot([tp, tp], [-0.6, -0.4], "k-", lw=1)
        ax.text(tp, -0.8, str(tp), fontsize=8, ha="center")

    # Risk 轴
    ax.plot([0, total_max], [-1.5, -1.5], "k-", lw=2)
    ax.text(-2, -1.5, "Risk", fontsize=10, va="center", fontweight="bold")

    risk_ticks = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
    for r in risk_ticks:
        # 简化的 logit 映射
        logit = np.log(r / (1 - r))
        x_pos = (logit - intercept) / max_abs_coef * 50 + 50
        if 0 <= x_pos <= total_max:
            ax.plot([x_pos, x_pos], [-1.6, -1.4], "k-", lw=1)
            ax.text(x_pos, -1.8, f"{r:.0%}", fontsize=8, ha="center")

    ax.set_title(model_name, fontsize=14, fontweight="bold", pad=20)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()

    return fig


# ============================================================================
# 7. 综合评估报告
# ============================================================================


def generate_prediction_model_report(
    dev_results: Dict,
    bootstrap_results: Optional[Dict] = None,
    report_guideline: str = "TRIPOD",
) -> str:
    """生成预测模型综合评估报告

    Parameters
    ----------
    dev_results : Dict
        develop_models 的输出
    bootstrap_results : Optional[Dict]
        bootstrap_validation 的输出
    report_guideline : str
        报告规范

    Returns
    -------
    str
        结构化报告文本
    """
    eval_df = dev_results["evaluation"]
    best = eval_df.iloc[0]

    lines = [
        f"## 预测模型评估报告 ({report_guideline} 合规)",
        "",
        "### 模型比较",
        eval_df.to_markdown(index=False),
        "",
        f"**最佳模型**: {best['Model']}",
        f"- AUC = {best['AUC']:.3f}",
        f"- Brier Score = {best['Brier_Score']:.3f}",
        f"- 校准斜率 = {best['Cal_Slope']:.3f} (目标: 1.0)",
        f"- 校准截距 = {best['Cal_Intercept']:.3f} (目标: 0.0)",
        "",
    ]

    if bootstrap_results:
        lines.extend([
            "### Bootstrap 内部验证",
            f"- 表观 AUC = {bootstrap_results['apparent_auc']:.3f}",
            f"- 乐观值 = {bootstrap_results['optimism_auc']:.3f}",
            f"- 校正后 AUC = {bootstrap_results['corrected_auc']:.3f}",
            f"- Bootstrap 次数 = {bootstrap_results['n_bootstraps']}",
            "",
        ])

    lines.extend([
        "### TRIPOD 检查要点",
        "- [ ] 研究设计：前瞻性/回顾性/横断面",
        "- [ ] 数据来源：单中心/多中心/数据库",
        "- [ ] 结局定义：明确的定义和测量方法",
        "- [ ] 缺失数据：处理方法描述",
        "- [ ] 预测因子：测量方法和时间点",
        "- [ ] 模型开发：变量选择方法",
        "- [ ] 模型规格：完整方程",
        "- [ ] 性能：区分度 + 校准度",
        "- [ ] 内部验证：Bootstrap/交叉验证",
        "- [ ] 外部验证：独立数据集",
        "- [ ] 补充材料：代码和数据",
    ])

    return "\n".join(lines)


# ============================================================================
# 8. 完整工作流
# ============================================================================


def full_prediction_model_workflow(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_predictors: Optional[int] = None,
    outcome_name: str = "outcome",
    output_dir: Optional[str] = None,
) -> Dict:
    """完整临床预测模型工作流

    步骤: 样本量 → 开发 → Bootstrap → DCA → 临床影响 → 报告

    Parameters
    ----------
    X_train, y_train : 训练集
    X_test, y_test : 测试集
    n_predictors : 候选预测因子数
    outcome_name : 结局变量名
    output_dir : 输出目录

    Returns
    -------
    Dict
        完整分析结果
    """
    results = {}

    # Phase 1: 样本量评估
    logger.info("=" * 60)
    logger.info("Phase 1: 样本量评估")
    logger.info("=" * 60)
    n_events = int(y_train.sum())
    n_pred = n_predictors or X_train.shape[1]
    prevalence = y_train.mean()

    sample_assess = assess_sample_size(
        n_events, n_pred, outcome_prevalence=prevalence, n_total=len(y_train))
    results["sample_size"] = sample_assess
    logger.info(f"  EPV = {sample_assess['epv']:.1f} ({sample_assess['assessment']})")
    logger.info(f"  {sample_assess['suggestion']}")

    # Phase 2: 模型开发
    logger.info("\n" + "=" * 60)
    logger.info("Phase 2: 模型开发与比较")
    logger.info("=" * 60)
    dev_results = develop_models(X_train, y_train, X_test, y_test)
    results["development"] = dev_results
    logger.info(dev_results["evaluation"].to_string(index=False))

    best_name = dev_results["evaluation"].iloc[0]["Model"]
    best_model = dev_results["models"][best_name]
    y_prob_best = best_model.predict_proba(X_test)[:, 1]

    # Phase 3: Bootstrap 内部验证
    logger.info("\n" + "=" * 60)
    logger.info("Phase 3: Bootstrap 内部验证")
    logger.info("=" * 60)
    boot_results = bootstrap_validation(best_model, X_train, y_train)
    results["bootstrap"] = boot_results
    logger.info(f"  表观 AUC = {boot_results['apparent_auc']:.3f}")
    logger.info(f"  校正后 AUC = {boot_results['corrected_auc']:.3f}")

    # Phase 4: 校准曲线
    logger.info("\n" + "=" * 60)
    logger.info("Phase 4: 校准曲线")
    logger.info("=" * 60)
    save_path = f"{output_dir}/calibration_curve.png" if output_dir else None
    fig_cal, ax_cal = plt.subplots(figsize=(8, 6))

    for name, model in dev_results["models"].items():
        y_p = model.predict_proba(X_test)[:, 1]
        fraction_pos, mean_pred = calibration_curve(y_test, y_p, n_bins=5)
        brier = brier_score_loss(y_test, y_p)
        ax_cal.plot(mean_pred, fraction_pos, "s-", lw=2,
                    label=f"{name} (Brier={brier:.3f})")

    ax_cal.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect")
    ax_cal.set_xlabel("Mean Predicted Probability")
    ax_cal.set_ylabel("Observed Frequency")
    ax_cal.set_title("Calibration Curve", fontsize=13, fontweight="bold")
    ax_cal.legend()
    ax_cal.grid(alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    results["calibration_plot"] = fig_cal

    # Phase 5: DCA
    logger.info("\n" + "=" * 60)
    logger.info("Phase 5: 决策曲线分析 (DCA)")
    logger.info("=" * 60)
    save_path = f"{output_dir}/dca.png" if output_dir else None
    results["dca_plot"] = decision_curve_analysis(
        y_test, y_prob_best, best_name, save_path=save_path, show=False)

    # Phase 6: 临床影响曲线
    logger.info("\n" + "=" * 60)
    logger.info("Phase 6: 临床影响曲线")
    logger.info("=" * 60)
    save_path = f"{output_dir}/clinical_impact.png" if output_dir else None
    results["clinical_impact_plot"] = clinical_impact_curve(
        y_test, y_prob_best, best_name, save_path=save_path, show=False)

    # Phase 7: 报告
    logger.info("\n" + "=" * 60)
    logger.info("Phase 7: 生成 TRIPOD 合规报告")
    logger.info("=" * 60)
    report = generate_prediction_model_report(dev_results, boot_results)
    results["report"] = report
    logger.info("report")

    logger.info("\n✅ 临床预测模型分析完成")
    return results


# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    np.random.seed(42)
    X_sim, y_sim = make_classification(
        n_samples=400, n_features=8, n_informative=5,
        n_redundant=1, weights=[0.7], random_state=42)
    feature_names = [f"Var_{i}" for i in range(X_sim.shape[1])]
    X_df = pd.DataFrame(X_sim, columns=feature_names)
    y_series = pd.Series(y_sim)

    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y_series, test_size=0.3, random_state=42)

    logger.info(f"训练集: {len(X_train)} 例 (阳性 {y_train.sum()})")
    logger.info(f"测试集: {len(X_test)} 例 (阳性 {y_test.sum()})")

    results = full_prediction_model_workflow(X_train, y_train, X_test, y_test)
