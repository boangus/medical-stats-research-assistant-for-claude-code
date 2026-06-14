"""
sensitivity_agreement.py — 主要-敏感性分析一致性评估模块
=========================================================
适用于：观察性研究中系统性评估敏感性分析与主要分析的一致性

参考文献：
  - Xu et al. (2025). Evaluating the agreement between sensitivity and
    primary analyses in observational studies using routinely collected
    healthcare data: a meta-epidemiology study. BMC Medicine.
    DOI: 10.1186/s12916-025-04199-4

核心概念：
  - 主要分析 (Primary Analysis): SAP 预定义的主要因果效应估计方法
  - 敏感性分析 (Sensitivity Analysis): 用于检验主要分析结论稳健性的替代方法
  - 一致性 (Agreement): 主要分析与敏感性分析在方向、统计显著性、效应量上的吻合程度

评估维度：
  1. 方向一致性: 效应量符号是否相同
  2. 显著性一致性: 统计显著性 (p<0.05) 是否一致
  3. 效应量接近度: |log(OR/HR)| 差异 < 0.2 视为接近
  4. CI 重叠度: 95% 置信区间是否有实质性重叠
  5. 综合一致性评分: 加权综合以上维度

依赖: numpy, pandas, matplotlib
安装: pip install numpy pandas matplotlib

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. 数据结构
# ============================================================================


@dataclass
class AnalysisResult:
    """单个分析结果"""
    name: str
    estimate: float
    ci_lower: float
    ci_upper: float
    p_value: float
    se: Optional[float] = None
    n: Optional[int] = None
    method: str = ""
    notes: str = ""


@dataclass
class AgreementResult:
    """一致性评估结果"""
    primary: AnalysisResult
    sensitivity: AnalysisResult
    direction_agreement: bool = True
    significance_agreement: bool = True
    effect_proximity: bool = True
    ci_overlap: bool = True
    overlap_proportion: float = 0.0
    log_ratio_diff: float = 0.0
    overall_agreement: bool = True
    agreement_score: float = 0.0
    interpretation: str = ""


# ============================================================================
# 2. 一致性评估核心函数
# ============================================================================


def assess_agreement(
    primary: AnalysisResult,
    sensitivity: AnalysisResult,
    effect_threshold: float = 0.2,
    ci_overlap_threshold: float = 0.5,
) -> AgreementResult:
    """评估主要分析与单个敏感性分析的一致性

    Parameters
    ----------
    primary : AnalysisResult
        主要分析结果
    sensitivity : AnalysisResult
        敏感性分析结果
    effect_threshold : float
        |log(效应量)| 差异阈值（默认 0.2，约 20% 相对差异）
    ci_overlap_threshold : float
        CI 重叠比例阈值（0-1）

    Returns
    -------
    AgreementResult
        一致性评估结果
    """
    result = AgreementResult(primary=primary, sensitivity=sensitivity)

    # 1. 方向一致性
    result.direction_agreement = (primary.estimate > 1) == (sensitivity.estimate > 1)
    # 对于 log-scale (OR/HR)
    log_primary = np.log(primary.estimate) if primary.estimate > 0 else 0
    log_sens = np.log(sensitivity.estimate) if sensitivity.estimate > 0 else 0
    result.direction_agreement = (log_primary * log_sens) >= 0

    # 2. 显著性一致性
    sig_primary = primary.p_value < 0.05
    sig_sens = sensitivity.p_value < 0.05
    result.significance_agreement = sig_primary == sig_sens

    # 3. 效应量接近度
    result.log_ratio_diff = abs(log_primary - log_sens)
    result.effect_proximity = result.log_ratio_diff < effect_threshold

    # 4. CI 重叠度
    overlap_lower = max(primary.ci_lower, sensitivity.ci_lower)
    overlap_upper = min(primary.ci_upper, sensitivity.ci_upper)
    overlap_width = max(0, overlap_upper - overlap_lower)

    primary_width = primary.ci_upper - primary.ci_lower
    sens_width = sensitivity.ci_upper - sensitivity.ci_lower
    min_width = min(primary_width, sens_width)

    result.overlap_proportion = overlap_width / min_width if min_width > 0 else 0
    result.ci_overlap = result.overlap_proportion >= ci_overlap_threshold

    # 5. 综合评分 (0-100)
    score = 0
    score += 25 if result.direction_agreement else 0
    score += 25 if result.significance_agreement else 0
    score += 25 if result.effect_proximity else 0
    score += 25 if result.ci_overlap else 0

    # 附加分: CI 重叠比例
    if result.overlap_proportion > 0.8:
        score = min(100, score + 10)

    result.agreement_score = score

    # 综合判定
    result.overall_agreement = (
        result.direction_agreement and
        result.significance_agreement and
        result.effect_proximity
    )

    # 解读
    if score >= 90:
        result.interpretation = "高度一致: 主要分析与敏感性分析结论完全吻合"
    elif score >= 70:
        result.interpretation = "中度一致: 主要分析结论基本稳健，部分细节有差异"
    elif score >= 50:
        result.interpretation = "低度一致: 主要分析结论可能受方法选择影响，需谨慎解读"
    else:
        result.interpretation = "不一致: 主要分析与敏感性分析结论矛盾，需深入调查原因"

    return result


def assess_multiple_sensitivities(
    primary: AnalysisResult,
    sensitivities: List[AnalysisResult],
    weights: Optional[List[float]] = None,
) -> Dict:
    """评估主要分析与多个敏感性分析的一致性

    Parameters
    ----------
    primary : AnalysisResult
        主要分析结果
    sensitivities : List[AnalysisResult]
        敏感性分析结果列表
    weights : Optional[List[float]]
        各敏感性分析的权重（默认等权）

    Returns
    -------
    Dict
        包含逐个评估结果和综合统计
    """
    if weights is None:
        weights = [1.0 / len(sensitivities)] * len(sensitivities)

    results = []
    for sens in sensitivities:
        agg = assess_agreement(primary, sens)
        results.append(agg)

    # 综合统计
    n_total = len(results)
    n_direction = sum(1 for r in results if r.direction_agreement)
    n_sig = sum(1 for r in results if r.significance_agreement)
    n_effect = sum(1 for r in results if r.effect_proximity)
    n_ci = sum(1 for r in results if r.ci_overlap)
    n_overall = sum(1 for r in results if r.overall_agreement)

    # 加权一致性率
    weighted_agreement = sum(
        w * (1.0 if r.overall_agreement else 0.0)
        for w, r in zip(weights, results)
    )

    # 加权平均评分
    weighted_score = sum(w * r.agreement_score for w, r in zip(weights, results))

    return {
        "primary": primary,
        "results": results,
        "summary": {
            "n_sensitivity": n_total,
            "direction_agreement_rate": n_direction / n_total,
            "significance_agreement_rate": n_sig / n_total,
            "effect_proximity_rate": n_effect / n_total,
            "ci_overlap_rate": n_ci / n_total,
            "overall_agreement_rate": n_overall / n_total,
            "weighted_agreement_rate": weighted_agreement,
            "weighted_mean_score": weighted_score,
        },
    }


# ============================================================================
# 3. 可视化
# ============================================================================


def plot_agreement_forest(
    primary: AnalysisResult,
    sensitivities: List[AnalysisResult],
    title: str = "Primary vs Sensitivity Analyses Agreement",
    figsize: Tuple[float, float] = (10, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """一致性森林图

    展示主要分析和多个敏感性分析的效应量及 95% CI，
    直观比较一致性。

    Parameters
    ----------
    primary : AnalysisResult
        主要分析结果
    sensitivities : List[AnalysisResult]
        敏感性分析结果列表
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
    all_results = [primary] + sensitivities
    n = len(all_results)

    fig, ax = plt.subplots(figsize=figsize)

    y_positions = list(range(n))
    labels = []

    for i, res in enumerate(all_results):
        # 效应量和 CI
        est = res.estimate
        ci_low = res.ci_lower
        ci_high = res.ci_upper

        # 颜色: 主要分析=蓝色, 一致的敏感性=绿色, 不一致=红色
        if i == 0:
            color = "steelblue"
            marker = "D"
            markersize = 8
        else:
            # 简化判断: 如果 CI 与主要分析有重叠，视为一致
            overlap_low = max(primary.ci_lower, ci_low)
            overlap_high = min(primary.ci_upper, ci_high)
            has_overlap = overlap_low < overlap_high
            color = "forestgreen" if has_overlap else "crimson"
            marker = "o"
            markersize = 6

        ax.errorbar(est, i, xerr=[[est - ci_low], [ci_high - est]],
                     fmt=marker, color=color, markersize=markersize,
                     capsize=4, capthick=1.5, linewidth=1.5)

        # 标签
        label = f"{res.name}"
        if res.method:
            label += f" ({res.method})"
        labels.append(label)

        # p 值标注
        p_str = f"p={res.p_value:.4f}" if res.p_value >= 0.001 else "p<0.001"
        ax.annotate(f"{est:.3f} ({ci_low:.3f}–{ci_high:.3f}), {p_str}",
                     xy=(ci_high, i), xytext=(5, 0),
                     textcoords="offset points", fontsize=8,
                     va="center", color="grey")

    # 参考线
    ax.axvline(x=1.0 if primary.estimate > 0 else 0,
               linestyle="--", color="grey", alpha=0.5, linewidth=1)

    # 如果是 log-scale 效应量，画 0 线
    if primary.estimate > 0:
        ax.axvline(x=1.0, linestyle="--", color="grey", alpha=0.5,
                    label="No effect (OR/HR=1)")

    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Effect Size (OR/HR, 95% CI)")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Agreement Forest Plot saved to: {save_path}")

    if show:
        plt.show()

    return fig


def plot_agreement_heatmap(
    multi_result: Dict,
    title: str = "Sensitivity Analysis Agreement Heatmap",
    figsize: Tuple[float, float] = (8, 5),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """一致性热力图

    以矩阵形式展示主要分析与各敏感性分析在各维度上的一致性。

    Parameters
    ----------
    multi_result : Dict
        assess_multiple_sensitivities 的输出
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
    results = multi_result["results"]
    n = len(results)

    # 构建矩阵
    dimensions = ["方向一致", "显著性一致", "效应量接近", "CI重叠", "综合一致"]
    matrix = np.zeros((n, len(dimensions)))

    for i, r in enumerate(results):
        matrix[i, 0] = 1 if r.direction_agreement else 0
        matrix[i, 1] = 1 if r.significance_agreement else 0
        matrix[i, 2] = 1 if r.effect_proximity else 0
        matrix[i, 3] = 1 if r.ci_overlap else 0
        matrix[i, 4] = 1 if r.overall_agreement else 0

    fig, ax = plt.subplots(figsize=figsize)

    cmap = plt.cm.RdYlGn
    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=1)

    # 标签
    y_labels = [r.sensitivity.name for r in results]
    ax.set_yticks(range(n))
    ax.set_yticklabels(y_labels, fontsize=10)
    ax.set_xticks(range(len(dimensions)))
    ax.set_xticklabels(dimensions, fontsize=10, rotation=45, ha="right")

    # 格子内标注
    for i in range(n):
        for j in range(len(dimensions)):
            text = "✅" if matrix[i, j] == 1 else "❌"
            ax.text(j, i, text, ha="center", va="center", fontsize=12)

    ax.set_title(title, fontsize=13, fontweight="bold")
    plt.colorbar(im, ax=ax, shrink=0.8, label="一致性")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Agreement Heatmap saved to: {save_path}")

    if show:
        plt.show()

    return fig


# ============================================================================
# 4. 报告生成
# ============================================================================


def generate_agreement_report(
    multi_result: Dict,
) -> str:
    """生成一致性评估报告（可直接插入论文 Limitations 或 Supplementary）

    Parameters
    ----------
    multi_result : Dict
        assess_multiple_sensitivities 的输出

    Returns
    -------
    str
        结构化报告文本
    """
    summary = multi_result["summary"]
    primary = multi_result["primary"]
    results = multi_result["results"]

    lines = [
        "## 主要-敏感性分析一致性评估",
        "",
        f"主要分析方法: {primary.method or primary.name}",
        f"效应量: {primary.estimate:.3f} (95% CI: {primary.ci_lower:.3f}–{primary.ci_upper:.3f}, "
        f"p = {primary.p_value:.4f})",
        "",
        f"敏感性分析数量: {summary['n_sensitivity']}",
        "",
        "### 一致性统计",
        f"- 方向一致性率: {summary['direction_agreement_rate']:.1%}",
        f"- 显著性一致性率: {summary['significance_agreement_rate']:.1%}",
        f"- 效应量接近率: {summary['effect_proximity_rate']:.1%}",
        f"- CI 重叠率: {summary['ci_overlap_rate']:.1%}",
        f"- 综合一致性率: {summary['overall_agreement_rate']:.1%}",
        f"- 加权一致性率: {summary['weighted_agreement_rate']:.1%}",
        f"- 加权平均评分: {summary['weighted_mean_score']:.1f}/100",
        "",
        "### 逐项评估",
    ]

    for r in results:
        lines.append(
            f"- **{r.sensitivity.name}**: {r.sensitivity.method or 'N/A'} | "
            f"OR/HR = {r.sensitivity.estimate:.3f} "
            f"({r.sensitivity.ci_lower:.3f}–{r.sensitivity.ci_upper:.3f}, "
            f"p = {r.sensitivity.p_value:.4f}) | "
            f"评分 = {r.agreement_score:.0f}/100 | "
            f"{r.interpretation}"
        )

    # 总结
    lines.extend([
        "",
        "### 结论",
    ])

    overall_rate = summary['overall_agreement_rate']
    if overall_rate >= 0.8:
        lines.append(
            "主要分析结论在多种敏感性分析中保持稳健，"
            "结果的一致性支持了因果推断的可靠性。"
        )
    elif overall_rate >= 0.5:
        lines.append(
            "主要分析结论在部分敏感性分析中保持一致，"
            "但存在一些方法学变异，建议在局限性中讨论。"
        )
    else:
        lines.append(
            "主要分析与敏感性分析存在较多不一致，"
            "结论的稳健性存疑，需谨慎解读并讨论潜在偏倚来源。"
        )

    return "\n".join(lines)


# ============================================================================
# 5. 快速评估函数
# ============================================================================


def quick_agreement_check(
    primary_est: float,
    primary_ci: Tuple[float, float],
    primary_p: float,
    sensitivity_est: float,
    sensitivity_ci: Tuple[float, float],
    sensitivity_p: float,
    primary_name: str = "Primary",
    sensitivity_name: str = "Sensitivity",
    primary_method: str = "",
    sensitivity_method: str = "",
) -> AgreementResult:
    """快速一致性检查（无需构造 dataclass）

    Parameters
    ----------
    primary_est : float
        主要分析效应量 (OR/HR/RR)
    primary_ci : Tuple[float, float]
        主要分析 95% CI
    primary_p : float
        主要分析 p 值
    sensitivity_est : float
        敏感性分析效应量
    sensitivity_ci : Tuple[float, float]
        敏感性分析 95% CI
    sensitivity_p : float
        敏感性分析 p 值
    primary_name : str
        主要分析名称
    sensitivity_name : str
        敏感性分析名称
    primary_method : str
        主要分析方法
    sensitivity_method : str
        敏感性分析方法

    Returns
    -------
    AgreementResult
    """
    primary = AnalysisResult(
        name=primary_name,
        estimate=primary_est,
        ci_lower=primary_ci[0],
        ci_upper=primary_ci[1],
        p_value=primary_p,
        method=primary_method,
    )
    sensitivity = AnalysisResult(
        name=sensitivity_name,
        estimate=sensitivity_est,
        ci_lower=sensitivity_ci[0],
        ci_upper=sensitivity_ci[1],
        p_value=sensitivity_p,
        method=sensitivity_method,
    )
    return assess_agreement(primary, sensitivity)


# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("主要-敏感性分析一致性评估 示例")
    print("=" * 60)

    # 主要分析: PSM
    primary = AnalysisResult(
        name="主要分析",
        estimate=0.72,
        ci_lower=0.55,
        ci_upper=0.94,
        p_value=0.014,
        method="倾向性评分匹配 (PSM)",
    )

    # 敏感性分析列表
    sensitivities = [
        AnalysisResult(
            name="IPTW",
            estimate=0.75,
            ci_lower=0.58,
            ci_upper=0.97,
            p_value=0.028,
            method="逆概率加权",
        ),
        AnalysisResult(
            name="Overlapping Weighting",
            estimate=0.73,
            ci_lower=0.56,
            ci_upper=0.95,
            p_value=0.019,
            method="重叠加权",
        ),
        AnalysisResult(
            name="多变量调整",
            estimate=0.78,
            ci_lower=0.60,
            ci_upper=1.01,
            p_value=0.062,
            method="Logistic 回归",
        ),
        AnalysisResult(
            name="E-value",
            estimate=0.72,
            ci_lower=0.55,
            ci_upper=0.94,
            p_value=0.014,
            method="E-value (无未测量混杂)",
        ),
        AnalysisResult(
            name="排除早期结局",
            estimate=0.69,
            ci_lower=0.51,
            ci_upper=0.93,
            p_value=0.015,
            method="排除 90 天内结局",
        ),
    ]

    # 多敏感性分析评估
    multi_result = assess_multiple_sensitivities(primary, sensitivities)

    # 打印报告
    report = generate_agreement_report(multi_result)
    print(report)

    # 可视化
    print("\n生成一致性森林图...")
    plot_agreement_forest(primary, sensitivities, show=False,
                          save_path="agreement_forest.png")

    print("生成一致性热力图...")
    plot_agreement_heatmap(multi_result, show=False,
                           save_path="agreement_heatmap.png")

    print("\n✅ 一致性评估完成")
