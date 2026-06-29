#!/usr/bin/env python3
"""
发表级图表模板 — MSRA Publication Figure Template

参考：nature-skills/nature-figure 设计理论和 API 规范
关联：shared/chart-styles/publication_figure_standards.md
关联：shared/statistics-methods/statistical_constraints.md (P值格式化)
关联：shared/chart-styles/variable_naming_conventions.md (变量命名)

使用方式：
    from publication_figure_template import (
        apply_publication_style,
        format_p_value,
        make_km_curve,
        make_forest_plot,
        make_roc_curve,
        make_calibration_plot,
        make_box_plot,
        make_bar_chart,
        make_scatter_plot,
        make_heatmap,
        export_figure,
    )

强制规则：
    1. 三行 rcParams 必须在绘图前设置（font.family, font.sans-serif, svg.fonttype）
    2. SVG 为首要输出格式，PNG 300dpi 为次要预览
    3. P 值格式遵循 P-R01~R07（P<0.001 展示为 "P < 0.001"）
    4. 变量名使用规范显示名 + 单位
    5. 仅保留左+下轴线，无边框图例
"""

import os

import matplotlib
import numpy as np

matplotlib.use('Agg')  # 无头模式
import logging
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# 第一部分：强制配置与调色板
# ═══════════════════════════════════════════════════════════════════════

def apply_publication_style(font_size: int = 10,
                            axes_linewidth: float = 1.2,
                            use_tex: bool = False,
                            support_chinese: bool = True):
    """
    应用发表级 rcParams。在创建任何图表前调用一次。

    Parameters
    ----------
    font_size : int
        基础字号。发表级密集多面板：7-9；标准医学图表：10-12；大型面板：24
    axes_linewidth : float
        坐标轴线宽。发表级：0.8-1.2；大型面板：3.0
    use_tex : bool
        是否使用 LaTeX 渲染（需安装 LaTeX）
    support_chinese : bool
        是否添加中文字体支持
    """
    # ── 强制：可编辑 SVG 文本（三行不可省略）──────────────────────────
    plt.rcParams['font.family'] = 'sans-serif'
    if support_chinese:
        plt.rcParams['font.sans-serif'] = [
            'Arial', 'Noto Sans CJK SC', 'DejaVu Sans', 'Liberation Sans', 'sans-serif'
        ]
    else:
        plt.rcParams['font.sans-serif'] = [
            'Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif'
        ]
    plt.rcParams['svg.fonttype'] = 'none'  # 文本保持为 <text> 节点

    # ── 布局与样式 ────────────────────────────────────────────────────
    plt.rcParams['font.size'] = font_size
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.linewidth'] = axes_linewidth
    plt.rcParams['legend.frameon'] = False
    plt.rcParams['axes.unicode_minus'] = False  # 负号显示

    if use_tex:
        plt.rcParams['text.usetex'] = True


# ── 语义化调色板（来源：nature-skills/nature-figure）─────────────────
PALETTE = {
    "blue_main":      "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",
    "red_1":   "#F6CFCB",
    "red_2":   "#E9A6A1",
    "red_strong": "#B64342",
    "neutral_light": "#CFCECE",
    "neutral_mid":   "#767676",
    "neutral_dark":  "#4D4D4D",
    "neutral_black": "#272727",
    "gold":   "#FFD700",
    "teal":   "#42949E",
    "violet": "#9A4D8E",
    "magenta":"#EA84DD",
}

DEFAULT_COLOR_ORDER = [
    PALETTE["blue_main"],
    PALETTE["green_3"],
    PALETTE["red_strong"],
    PALETTE["teal"],
    PALETTE["violet"],
    PALETTE["neutral_light"],
]

# ── 色盲安全配色 ────────────────────────────────────────────────────
COLOR_BLIND_SAFE = [
    "#0072B2", "#E69F00", "#009E73", "#F0E442",
    "#56B4E9", "#D55E00", "#CC79A7",
]

# ── 期刊配色（与 journal_color_schemes.json 集成）────────────────────
JOURNAL_PALETTES = {
    "NEJM": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
    "JAMA": ["#c00000", "#0066cc", "#008000", "#ff8c00", "#800080"],
    "Lancet": ["#00573f", "#ff4500", "#0066cc", "#ff8c00", "#800080"],
    "BMJ": ["#003366", "#ff6600", "#006633", "#cc0000", "#660066"],
    "CMJ": ["#cc0000", "#003366", "#006600", "#ff8c00", "#660066"],
    "default": DEFAULT_COLOR_ORDER,
}


def get_colors(journal: str = "default",
               color_blind_safe: bool = False) -> List[str]:
    """
    获取配色方案。

    Parameters
    ----------
    journal : str
        期刊名称（NEJM/JAMA/Lancet/BMJ/CMJ/default）
    color_blind_safe : bool
        是否使用色盲安全配色

    Returns
    -------
    list[str]
        颜色列表
    """
    if color_blind_safe:
        return COLOR_BLIND_SAFE
    return JOURNAL_PALETTES.get(journal, DEFAULT_COLOR_ORDER)


# ═══════════════════════════════════════════════════════════════════════
# 第二部分：P 值格式化（遵循 statistical_constraints.md P-R01~R07）
# ═══════════════════════════════════════════════════════════════════════

def format_p_value(p: float, precision: int = 3) -> str:
    """
    格式化 P 值，遵循 MSRA 约束规则 P-R01~R07。

    P-R01: P < 0.001 时展示为 "P < 0.001"
    P-R02: 0.001 ≤ P < 0.05 时报告精确到小数点后 3 位
    P-R04: 禁止二元化表述

    Parameters
    ----------
    p : float
        原始 P 值
    precision : int
        小数位数（默认 3 位）

    Returns
    -------
    str
        格式化后的 P 值字符串
    """
    if p < 0.001:
        return "P < 0.001"
    elif p < 1.0:
        return f"P = {p:.{precision}f}"
    else:
        return "P = 1.000"


def format_p_value_vector(p_values: List[float], precision: int = 3) -> List[str]:
    """批量格式化 P 值，确保精度统一（P-R06）。"""
    return [format_p_value(p, precision) for p in p_values]


# ═══════════════════════════════════════════════════════════════════════
# 第三部分：通用辅助函数
# ═══════════════════════════════════════════════════════════════════════

def is_dark(hex_color: str, threshold: int = 128) -> bool:
    """判断颜色是否为深色（用于选择叠加文字的颜色）。"""
    c = hex_color.lstrip('#')
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) < threshold


def add_panel_label(ax, label: str, x: float = -0.06, y: float = 1.02,
                    fontsize: int = 12, color: str = 'black',
                    fontweight: str = 'bold'):
    """添加 Nature 风格的面板标签（小写粗体字母）。"""
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=fontsize, fontweight=fontweight,
            color=color, ha='left', va='bottom')


def add_significance_bar(ax, x1: float, x2: float, y: float,
                         p_value: float, height: float = 0.02,
                         fontsize: int = 8, color: str = '#4D4D4D'):
    """
    添加显著性比较线和 P 值标注。

    Parameters
    ----------
    x1, x2 : float
        比较两组的 x 坐标
    y : float
        比较线的 y 坐标
    p_value : float
        P 值（自动格式化）
    height : float
        竖线高度
    """
    # 横线
    ax.plot([x1, x2], [y, y], color=color, linewidth=0.8)
    # 竖线
    ax.plot([x1, x1], [y - height, y], color=color, linewidth=0.8)
    ax.plot([x2, x2], [y - height, y], color=color, linewidth=0.8)
    # P 值标注（遵循 P-R01~R07）
    p_str = format_p_value(p_value)
    ax.text((x1 + x2) / 2, y + height * 0.5, p_str,
            ha='center', va='bottom', fontsize=fontsize, color=color)


# ═══════════════════════════════════════════════════════════════════════
# 第四部分：医学统计核心图表
# ═══════════════════════════════════════════════════════════════════════

def make_km_curve(time, event, group, group_labels=None,
                  group_colors=None, xlabel='时间 (月)',
                  ylabel='生存概率', title=None,
                  show_risk_table=True, show_median=True,
                  p_value=None, ax=None):
    """
    Kaplan-Meier 生存曲线（发表级）。

    Parameters
    ----------
    time : array-like
        生存时间
    event : array-like
        事件状态（0=删失, 1=事件）
    group : array-like
        分组变量
    group_labels : list[str]
        组别标签（规范显示名）
    group_colors : list[str]
        组别颜色
    xlabel : str
        X 轴标签（含单位）
    ylabel : str
        Y 轴标签
    show_risk_table : bool
        是否显示风险人数表
    show_median : bool
        是否标注中位生存时间
    p_value : float
        Log-rank 检验 P 值（自动格式化）

    Returns
    -------
    fig, ax
    """
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import multivariate_logrank_test

    time = np.asarray(time)
    event = np.asarray(event)
    group = np.asarray(group)
    groups = np.unique(group)

    if group_labels is None:
        group_labels = [str(g) for g in groups]
    if group_colors is None:
        group_colors = get_colors()[:len(groups)]

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    else:
        fig = ax.figure

    # KM 曲线
    kmf = KaplanMeierFitter()
    for i, (g, label, color) in enumerate(zip(groups, group_labels, group_colors)):
        mask = group == g
        kmf.fit(time[mask], event[mask], label=label)
        kmf.plot_survival_function(ax=ax, color=color, ci_show=True,
                                    ci_alpha=0.15, linewidth=2.0,
                                    show_censors=True,
                                    censor_styles={'marker': '|', 'ms': 6})

    # 中位生存时间参考线
    if show_median:
        for g, label, color in zip(groups, group_labels, group_colors):
            mask = group == g
            kmf.fit(time[mask], event[mask])
            median = kmf.median_survival_time_
            if np.isfinite(median):
                ax.axhline(0.5, color='#767676', linestyle='--',
                           linewidth=0.8, alpha=0.5)
                ax.axvline(median, color=color, linestyle=':',
                           linewidth=0.8, alpha=0.5)

    # P 值标注
    if p_value is not None:
        p_str = format_p_value(p_value)
        ax.text(0.95, 0.95, f'Log-rank {p_str}',
                transform=ax.transAxes, ha='right', va='top',
                fontsize=9, bbox=dict(boxstyle='round,pad=0.3',
                                      facecolor='white', edgecolor='none',
                                      alpha=0.8))
    else:
        # 自动计算
        result = multivariate_logrank_test(time, group, event)
        p_str = format_p_value(result.p_value)
        ax.text(0.95, 0.95, f'Log-rank {p_str}',
                transform=ax.transAxes, ha='right', va='top',
                fontsize=9, bbox=dict(boxstyle='round,pad=0.3',
                                      facecolor='white', edgecolor='none',
                                      alpha=0.8))

    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlim(left=0)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')

    # 风险人数表
    if show_risk_table:
        # 在图下方添加风险人数表
        n_groups = len(groups)
        n_timepoints = 6
        max_time = time.max()
        timepoints = np.linspace(0, max_time, n_timepoints)

        # 创建子图区域
        fig.add_axes  # placeholder

    return fig, ax


def make_forest_plot(labels: List[str], estimates: List[float],
                     ci_lower: List[float], ci_upper: List[float],
                     p_values: List[float] = None,
                     weights: List[float] = None,
                     xlabel: str = 'HR (95% CI)',
                     title: str = None,
                     ref_line: float = 1.0,
                     colors: List[str] = None,
                     figsize: Tuple[float, float] = (7, 4),
                     show_p_values: bool = True):
    """
    森林图（发表级）。

    Parameters
    ----------
    labels : list[str]
        变量标签（规范显示名）
    estimates : list[float]
        效应量点估计
    ci_lower, ci_upper : list[float]
        置信区间下限/上限
    p_values : list[float]
        P 值列表（自动格式化）
    weights : list[float]
        权重（用于方块大小）
    xlabel : str
        X 轴标签
    ref_line : float
        参考线位置（HR=1 或 OR=1 或 0）
    """
    n = len(labels)
    if colors is None:
        colors = [PALETTE['blue_main']] * n

    fig, ax = plt.subplots(figsize=figsize)
    y_pos = np.arange(n)[::-1]

    # 绘制置信区间和点估计
    for i, (yi, est, lo, hi, color) in enumerate(
            zip(y_pos, estimates, ci_lower, ci_upper, colors)):
        # 置信区间线
        ax.plot([lo, hi], [yi, yi], color=color, linewidth=1.5)
        # 点估计（方块或圆）
        if weights is not None:
            size = (weights[i] / max(weights)) * 200 + 20
            ax.scatter(est, yi, s=size, color=color, marker='s',
                       edgecolors='black', linewidth=0.5, zorder=5)
        else:
            ax.scatter(est, yi, s=60, color=color, marker='o',
                       edgecolors='black', linewidth=0.5, zorder=5)

    # 参考线
    ax.axvline(ref_line, color='#767676', linestyle='--',
               linewidth=1.0, alpha=0.8)

    # Y 轴标签
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)

    # X 轴
    ax.set_xlabel(xlabel, fontsize=10)

    # 右侧添加效应量和 P 值标注
    if show_p_values and p_values is not None:
        # 在右侧添加文本列
        x_text = max(ci_upper) + (max(ci_upper) - min(ci_lower)) * 0.05
        for yi, est, lo, hi, p in zip(y_pos, estimates, ci_lower,
                                       ci_upper, p_values):
            p_str = format_p_value(p)
            text = f'{est:.2f} ({lo:.2f}-{hi:.2f})  {p_str}'
            ax.text(x_text, yi, text, va='center', fontsize=8,
                    color='#4D4D4D')

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    fig.tight_layout(pad=2)
    return fig, ax


def make_roc_curve(y_true, y_score, auc_value=None, ci_lower=None,
                   ci_upper=None, optimal_cutoff=None,
                   xlabel='1 - 特异度', ylabel='敏感度',
                   title=None, color=None, figsize=(5, 5)):
    """
    ROC 曲线（发表级）。

    Parameters
    ----------
    y_true : array-like
        真实标签
    y_score : array-like
        预测概率
    auc_value : float
        AUC 值（如已计算）
    ci_lower, ci_upper : float
        AUC 的 95% CI
    optimal_cutoff : float
        最优截断值
    """
    from sklearn.metrics import auc, roc_curve

    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    if auc_value is None:
        auc_value = auc(fpr, tpr)

    if color is None:
        color = PALETTE['blue_main']

    fig, ax = plt.subplots(figsize=figsize)

    # ROC 曲线
    ax.plot(fpr, tpr, color=color, linewidth=2.0,
            label=f'AUC = {auc_value:.3f}')
    if ci_lower is not None and ci_upper is not None:
        ax.plot([], [], ' ', label=f'95% CI: {ci_lower:.3f}-{ci_upper:.3f}')

    # 参考线
    ax.plot([0, 1], [0, 1], color='#767676', linestyle='--',
            linewidth=1.0, alpha=0.5, label='参考线')

    # 最优截断值
    if optimal_cutoff is not None:
        youden = tpr - fpr
        idx = np.argmax(youden)
        ax.scatter(fpr[idx], tpr[idx], s=80, color=PALETTE['red_strong'],
                   marker='o', edgecolors='black', linewidth=0.5,
                   zorder=5, label=f'最优截断 = {optimal_cutoff:.3f}')

    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', fontsize=8)

    fig.tight_layout(pad=2)
    return fig, ax


def make_calibration_curve(y_true, y_pred, n_bins=10,
                           xlabel='预测概率', ylabel='观测概率',
                           title=None, color=None,
                           show_brier=True, figsize=(5, 5)):
    """校准曲线（发表级）。"""
    from sklearn.calibration import calibration_curve
    from sklearn.metrics import brier_score_loss

    if color is None:
        color = PALETTE['blue_main']

    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_true, y_pred, n_bins=n_bins, strategy='uniform')

    fig, ax = plt.subplots(figsize=figsize)

    # 校准曲线
    ax.plot(mean_predicted_value, fraction_of_positives,
            color=color, linewidth=2.0, marker='o', markersize=6,
            label='校准曲线')

    # 参考线
    ax.plot([0, 1], [0, 1], color='#767676', linestyle='--',
            linewidth=1.0, alpha=0.5, label='完美校准')

    # Brier Score
    if show_brier:
        brier = brier_score_loss(y_true, y_pred)
        ax.text(0.05, 0.95, f'Brier Score = {brier:.4f}',
                transform=ax.transAxes, fontsize=9, va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='none', alpha=0.8))

    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', fontsize=8)

    fig.tight_layout(pad=2)
    return fig, ax


def make_box_plot(data, labels, xlabel=None, ylabel=None,
                  title=None, colors=None, show_points=True,
                  show_p_values=None, figsize=(7, 4)):
    """
    箱线图（发表级）。

    Parameters
    ----------
    data : list[array]
        每组数据
    labels : list[str]
        组别标签（规范显示名）
    show_p_values : list[tuple]
        P 值比较 [(idx1, idx2, p_value), ...]
    """
    if colors is None:
        colors = get_colors()[:len(data)]

    fig, ax = plt.subplots(figsize=figsize)

    bp = ax.boxplot(data, labels=labels, patch_artist=True,
                    widths=0.5, showfliers=False,
                    medianprops=dict(color='black', linewidth=1.5),
                    boxprops=dict(linewidth=1.0),
                    whiskerprops=dict(linewidth=1.0),
                    capprops=dict(linewidth=1.0))

    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # 叠加散点
    if show_points:
        for i, (d, color) in enumerate(zip(data, colors)):
            x = np.random.normal(i + 1, 0.04, size=len(d))
            ax.scatter(x, d, s=15, color=color, alpha=0.5,
                       edgecolors='none', zorder=3)

    # P 值标注
    if show_p_values:
        y_max = max(np.max(d) for d in data)
        y_step = (y_max * 0.08) if y_max != 0 else 0.1
        for idx1, idx2, p_val in show_p_values:
            y_pos = y_max + y_step
            add_significance_bar(ax, idx1 + 1, idx2 + 1, y_pos, p_val)
            y_max = y_pos + y_step * 1.5

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')

    fig.tight_layout(pad=2)
    return fig, ax


def make_bar_chart(categories, values, errors=None,
                   labels=None, xlabel=None, ylabel=None,
                   title=None, colors=None, show_values=True,
                   figsize=(7, 4), horizontal=False):
    """
    柱状图（发表级）。

    Parameters
    ----------
    categories : list[str]
        类别标签（规范显示名）
    values : list[float] or list[list[float]]
        数值（单组或多组）
    errors : list[float]
        误差值（SD/SE/CI）
    show_values : bool
        是否在柱上标注数值
    horizontal : bool
        是否水平展示
    """
    if colors is None:
        colors = get_colors()

    fig, ax = plt.subplots(figsize=figsize)

    # 判断单组或多组
    if isinstance(values[0], (list, np.ndarray)):
        # 多组柱状图
        n_groups = len(values)
        n_cats = len(categories)
        width = 0.8 / n_groups
        x = np.arange(n_cats)

        for i, (vals, label) in enumerate(zip(values, labels or [f'Group {j+1}' for j in range(n_groups)])):
            offset = (i - (n_groups - 1) / 2) * width
            color = colors[i % len(colors)]
            err = errors[i] if errors else None
            bars = ax.bar(x + offset, vals, width=width, label=label,
                          color=color, edgecolor='black', linewidth=0.8,
                          yerr=err, capsize=5,
                          error_kw={'elinewidth': 1.5, 'capthick': 1.5})
            if show_values:
                for bar, val in zip(bars, vals):
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.01,
                            f'{val:.2f}', ha='center', va='bottom',
                            fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend(fontsize=8)
    else:
        # 单组柱状图
        err = errors if errors else None
        if horizontal:
            bars = ax.barh(categories, values, color=colors[:len(categories)],
                           edgecolor='black', linewidth=0.8, xerr=err,
                           capsize=5, error_kw={'elinewidth': 1.5, 'capthick': 1.5})
            if show_values:
                for bar, val in zip(bars, values):
                    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                            f'{val:.2f}', ha='left', va='center', fontsize=8)
        else:
            bars = ax.bar(categories, values, color=colors[:len(categories)],
                          edgecolor='black', linewidth=0.8, yerr=err,
                          capsize=5, error_kw={'elinewidth': 1.5, 'capthick': 1.5})
            if show_values:
                for bar, val in zip(bars, values):
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.01,
                            f'{val:.2f}', ha='center', va='bottom',
                            fontsize=8)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')

    fig.tight_layout(pad=2)
    return fig, ax


def make_scatter_plot(x, y, labels=None, colors=None,
                      xlabel=None, ylabel=None, title=None,
                      show_regression=True, show_correlation=True,
                      figsize=(5, 5)):
    """
    散点图（发表级），含回归线和相关系数。
    """
    if colors is None:
        colors = [PALETTE['blue_main']]

    fig, ax = plt.subplots(figsize=figsize)

    if labels and len(set(labels)) > 1:
        # 多组散点
        unique_labels = list(set(labels))
        for i, label in enumerate(unique_labels):
            mask = np.array(labels) == label
            ax.scatter(np.array(x)[mask], np.array(y)[mask],
                       s=40, color=colors[i % len(colors)], alpha=0.7,
                       edgecolors='white', linewidth=0.5, label=label)
        ax.legend(fontsize=8)
    else:
        ax.scatter(x, y, s=40, color=colors[0], alpha=0.7,
                   edgecolors='white', linewidth=0.5)

    # 回归线
    if show_regression:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(x), max(x), 100)
        ax.plot(x_line, p(x_line), color=PALETTE['red_strong'],
                linewidth=1.5, linestyle='--', alpha=0.8)

    # 相关系数
    if show_correlation:
        r, p_val = _pearson_r_pvalue(x, y)
        p_str = format_p_value(p_val)
        ax.text(0.05, 0.95, f'r = {r:.3f}\n{p_str}',
                transform=ax.transAxes, fontsize=9, va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='none', alpha=0.8))

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')

    fig.tight_layout(pad=2)
    return fig, ax


def _pearson_r_pvalue(x, y):
    """计算 Pearson 相关系数和 P 值。"""
    from scipy import stats
    r, p = stats.pearsonr(x, y)
    return r, p


def make_heatmap(matrix, x_labels=None, y_labels=None,
                 cmap='RdBu_r', vmin=None, vmax=None,
                 xlabel=None, ylabel=None, title=None,
                 annotate=True, fmt='{:.2f}', fontsize=9,
                 cbar_label=None, figsize=(6, 5)):
    """
    热图（发表级），支持单元格注释和色条。
    """
    matrix = np.asarray(matrix)

    fig, ax = plt.subplots(figsize=figsize)

    if vmin is None:
        vmin = np.nanmin(matrix)
    if vmax is None:
        vmax = np.nanmax(matrix)

    im = ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)

    # 色条
    if cbar_label:
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label(cbar_label, fontsize=9)
    else:
        fig.colorbar(im, ax=ax, shrink=0.8)

    # 标签
    if x_labels:
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=9)
    if y_labels:
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize=9)

    # 单元格注释
    if annotate:
        import matplotlib as mpl
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        cm_obj = plt.get_cmap(cmap)
        for (i, j), val in np.ndenumerate(matrix):
            if np.isnan(val):
                continue
            r, g, b, _ = cm_obj(norm(val))
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            text_color = 'white' if lum < 0.5 else 'black'
            ax.text(j, i, fmt.format(val), ha='center', va='center',
                    fontsize=fontsize, color=text_color)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')

    ax.set_frame_on(False)
    ax.tick_params(axis='both', which='both', length=0)

    fig.tight_layout(pad=2)
    return fig, ax


def make_rcs_plot(x, y_pred, ci_lower, ci_upper, ref_x=None,
                  xlabel=None, ylabel=None, title=None,
                  nonlinearity_p=None, knots=None,
                  color=None, figsize=(6, 4)):
    """
    限制性立方样条（RCS）曲线（发表级）。

    Parameters
    ----------
    x : array-like
        连续变量值
    y_pred : array-like
        预测值（如 HR/OR/logHR）
    ci_lower, ci_upper : array-like
        置信区间
    ref_x : float
        参考值（HR=1 处的 x 值）
    nonlinearity_p : float
        非线性检验 P 值
    knots : list[float]
        节点位置
    """
    if color is None:
        color = PALETTE['blue_main']

    fig, ax = plt.subplots(figsize=figsize)

    # 置信区间带
    ax.fill_between(x, ci_lower, ci_upper, color=color, alpha=0.15)

    # RCS 曲线
    ax.plot(x, y_pred, color=color, linewidth=2.0)

    # 参考线
    if ref_x is not None:
        ax.axvline(ref_x, color='#767676', linestyle='--',
                   linewidth=0.8, alpha=0.5)
    ax.axhline(1.0 if ylabel and 'HR' in ylabel else 0.0,
               color='#767676', linestyle='--',
               linewidth=0.8, alpha=0.5)

    # 节点标记
    if knots:
        for k in knots:
            ax.axvline(k, color=PALETTE['neutral_light'],
                       linestyle=':', linewidth=0.5, alpha=0.5)

    # 非线性检验 P 值
    if nonlinearity_p is not None:
        p_str = format_p_value(nonlinearity_p)
        ax.text(0.95, 0.95, f'非线性检验 {p_str}',
                transform=ax.transAxes, ha='right', va='top',
                fontsize=9, bbox=dict(boxstyle='round,pad=0.3',
                                      facecolor='white', edgecolor='none',
                                      alpha=0.8))

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')

    fig.tight_layout(pad=2)
    return fig, ax


# ═══════════════════════════════════════════════════════════════════════
# 第五部分：导出函数
# ═══════════════════════════════════════════════════════════════════════

def export_figure(fig, out_path: str, formats: List[str] = None,
                  dpi: int = 300, pad: float = 2,
                  bbox_inches: str = 'tight', close: bool = True):
    """
    发表级图表导出。

    IRON RULE: SVG 为首要输出格式，PNG 为次要预览格式。

    Parameters
    ----------
    out_path : str
        输出路径（不含扩展名，或含扩展名）
    formats : list[str]
        导出格式列表。默认 ['svg', 'png']
    dpi : int
        PNG 分辨率。标准 300，密集柱状图 600
    pad : float
        tight_layout 间距
    close : bool
        导出后是否关闭图表

    Returns
    -------
    list[str]
        已保存的文件路径列表
    """
    if formats is None:
        formats = ['svg', 'pdf', 'png']

    fig.tight_layout(pad=pad)
    base = Path(out_path)
    if base.suffix:
        base = base.with_suffix('')

    os.makedirs(base.parent, exist_ok=True)
    saved = []
    for fmt in formats:
        p = str(base) + f'.{fmt}'
        fig.savefig(p, dpi=dpi, bbox_inches=bbox_inches, format=fmt)
        saved.append(p)

    if close:
        plt.close(fig)

    return saved


# ═══════════════════════════════════════════════════════════════════════
# 第六部分：质量检查
# ═══════════════════════════════════════════════════════════════════════

def check_figure_quality(fig, variable_names=None, p_values=None):
    """
    图表质量检查（发表级标准）。

    Returns
    -------
    list[dict]
        不合规项列表
    """
    violations = []

    # 检查 rcParams
    if plt.rcParams.get('svg.fonttype') != 'none':
        violations.append({
            "rule": "rcParams",
            "issue": "svg.fonttype 未设置为 'none'，SVG 文本将不可编辑"
        })
    if plt.rcParams.get('axes.spines.right') != False:
        violations.append({
            "rule": "rcParams",
            "issue": "右侧轴线未关闭"
        })
    if plt.rcParams.get('axes.spines.top') != False:
        violations.append({
            "rule": "rcParams",
            "issue": "顶部轴线未关闭"
        })

    # 检查 P 值格式
    if p_values:
        for i, p in enumerate(p_values):
            if isinstance(p, str):
                if "P = 0.000" in p or "p = 0.000" in p:
                    violations.append({
                        "rule": "P-R01",
                        "location": f"p_value[{i}]",
                        "issue": "P值<0.001应展示为 P < 0.001"
                    })
                if p.strip() in ["P < 0.05", "P > 0.05", "NS", "ns"]:
                    violations.append({
                        "rule": "P-R04",
                        "location": f"p_value[{i}]",
                        "issue": "禁止二元化表述"
                    })

    return violations


# ═══════════════════════════════════════════════════════════════════════
# 使用示例
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 1. 应用发表级样式
    apply_publication_style(font_size=10, support_chinese=True)

    # 2. 示例：森林图
    labels = ['年龄 (每增加1岁)', '男性 vs 女性', '治疗组 vs 对照组',
              'BMI (kg/m²)', '高血压']
    estimates = [1.02, 1.35, 0.75, 1.08, 1.45]
    ci_lower = [1.01, 1.12, 0.62, 0.95, 1.15]
    ci_upper = [1.03, 1.63, 0.91, 1.22, 1.83]
    p_values = [0.0005, 0.002, 0.004, 0.21, 0.001]

    fig, ax = make_forest_plot(
        labels=labels, estimates=estimates,
        ci_lower=ci_lower, ci_upper=ci_upper,
        p_values=p_values, xlabel='HR (95% CI)',
        title='多因素Cox回归森林图'
    )

    # 3. 导出（SVG + PNG）
    saved = export_figure(fig, 'reports/figures/figure1_forest')
    logger.info(f"已保存: {saved}")

    # 4. 质量检查
    violations = check_figure_quality(fig, p_values=p_values)
    if violations:
        logger.info(f"质量检查发现 {len(violations)} 个问题:")
        for v in violations:
            logger.info(f"  - {v['rule']}: {v['issue']}")
    else:
        logger.info("质量检查通过 ✅")
