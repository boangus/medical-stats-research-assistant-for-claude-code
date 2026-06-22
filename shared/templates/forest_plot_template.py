"""
forest_plot_template.py — 森林图可视化模板（Python）
==================================================
适用于：Meta 分析、多变量回归的 OR/HR/β 可视化

依赖: matplotlib, numpy, pandas
安装: pip install matplotlib numpy pandas

作者: MSRA Team
版本: 0.1.0
"""

from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 基本森林图
# ============================================================================


def create_forest_plot(
    data: pd.DataFrame,
    estimate_col: str = "estimate",
    lower_col: str = "lower",
    upper_col: str = "upper",
    var_col: str = "variable",
    pval_col: Optional[str] = None,
    ref_line: float = 1.0,
    x_label: str = "Odds Ratio (95% CI)",
    title: str = "Forest Plot",
    figsize: Tuple[float, float] = (10, 6),
    log_scale: bool = True,
    color: str = "steelblue",
) -> plt.Figure:
    """创建基本森林图

    Parameters
    ----------
    data : pd.DataFrame
        包含效应量和置信区间的数据框
    estimate_col : str
        效应量列名
    lower_col : str
        置信区间下限列名
    upper_col : str
        置信区间上限列名
    var_col : str
        变量名列名
    pval_col : Optional[str]
        p 值列名（可选）
    ref_line : float
        参考线位置（OR/HR=1, β=0）
    x_label : str
        X 轴标签
    title : str
        图表标题
    figsize : Tuple
        图尺寸
    log_scale : bool
        是否使用对数刻度（OR/HR 用 True，β 用 False）
    color : str
        主色

    Returns
    -------
    plt.Figure
    """
    df = data.copy()
    df = df.sort_values(estimate_col, ascending=True).reset_index(drop=True)
    df["y_pos"] = range(len(df))

    fig, ax = plt.subplots(figsize=figsize)

    # 效应量显示列（在图形右侧）
    df["display"] = df.apply(
        lambda r: f"{r[estimate_col]:.3f} ({r[lower_col]:.3f}, {r[upper_col]:.3f})",
        axis=1,
    )

    # 置信区间线段
    for _, row in df.iterrows():
        ax.plot(
            [row[lower_col], row[upper_col]],
            [row["y_pos"], row["y_pos"]],
            color="grey",
            linewidth=2,
            solid_capstyle="round",
        )

    # 点估计
    ax.scatter(
        df[estimate_col],
        df["y_pos"],
        s=80,
        color=color,
        zorder=5,
        edgecolors="white",
        linewidth=0.5,
    )

    # 参考线
    ax.axvline(x=ref_line, linestyle="--", color="grey", alpha=0.7, linewidth=1)

    # 轴设置
    if log_scale:
        ax.set_xscale("log")

    ax.set_yticks(df["y_pos"])
    ax.set_yticklabels(df[var_col])
    ax.set_xlabel(x_label, fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")

    # 添加效应量文本
    for _, row in df.iterrows():
        ax.annotate(
            row["display"],
            xy=(row[upper_col], row["y_pos"]),
            xytext=(5, 0),
            textcoords="offset points",
            fontsize=8,
            va="center",
        )

    # 添加显著性标记
    if pval_col and pval_col in df.columns:
        df["sig"] = df[pval_col].apply(
            lambda p: "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
        )
        max_x = ax.get_xlim()[1]
        for _, row in df.iterrows():
            ax.text(
                max_x * 1.05,
                row["y_pos"],
                row["sig"],
                fontsize=10,
                va="center",
                color="darkred",
            )

    ax.set_xlim(
        left=min(df[lower_col].min() * 0.8, ref_line * 0.5),
        right=max(df[upper_col].max() * 1.3, ref_line * 2),
    )

    # 网格
    ax.grid(axis="x", alpha=0.3, linestyle=":")
    ax.set_axisbelow(True)

    plt.tight_layout()
    return fig


# ============================================================================
# 2. 分组森林图（亚组分析）
# ============================================================================


def create_subgroup_forest(
    data: pd.DataFrame,
    subgroup_col: str = "subgroup",
    level_col: str = "level",
    estimate_col: str = "estimate",
    lower_col: str = "lower",
    upper_col: str = "upper",
    ref_line: float = 1.0,
    title: str = "Subgroup Forest Plot",
    figsize: Tuple[float, float] = (10, 8),
) -> plt.Figure:
    """创建亚组分析森林图

    Parameters
    ----------
    data : pd.DataFrame
        数据集
    subgroup_col : str
        亚组列名
    level_col : str
        亚组水平列名
    estimate_col, lower_col, upper_col : str
        效应量和置信区间列
    ref_line : float
        参考线
    title, figsize : str, tuple
        标题和尺寸

    Returns
    -------
    plt.Figure
    """
    df = data.copy()
    subgroups = df[subgroup_col].unique()
    y_pos = 0
    positions = []
    labels = []
    colors = []

    fig, ax = plt.subplots(figsize=figsize)

    for sg in subgroups:
        sub = df[df[subgroup_col] == sg].sort_values(estimate_col, ascending=False)
        # 亚组标题行（间隔）
        y_pos += 0.8
        positions.append(y_pos)
        labels.append(f"  {sg}")
        colors.append("none")

        for _, row in sub.iterrows():
            y_pos += 1
            positions.append(y_pos)
            labels.append(row[level_col])
            colors.append("white" if y_pos % 2 == 0 else "lightgrey")

            ax.plot(
                [row[lower_col], row[upper_col]],
                [y_pos, y_pos],
                color="grey",
                linewidth=2,
            )
            ax.scatter(
                row[estimate_col], y_pos, s=60, color="steelblue",
                zorder=5, edgecolors="white",
            )

        y_pos += 0.5  # 亚组间间隔

    ax.axvline(x=ref_line, linestyle="--", color="grey", alpha=0.7)
    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Effect Size (95% CI)", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")

    # 亚组标题加粗
    for i, label in enumerate(ax.get_yticklabels()):
        if label.get_text().startswith("  "):
            label.set_fontweight("bold")

    plt.tight_layout()
    return fig


# ============================================================================
# 3. 森林图表格（含数字列的完整森林图）
# ============================================================================


def forest_plot_with_table(
    data: pd.DataFrame,
    estimate_col: str = "estimate",
    lower_col: str = "lower",
    upper_col: str = "upper",
    var_col: str = "variable",
    extra_cols: Optional[List[str]] = None,
    ref_line: float = 1.0,
    title: str = "Forest Plot",
    figsize: Tuple[float, float] = (12, 6),
) -> plt.Figure:
    """带数字表格的完整森林图

    左侧为变量名和统计量，右侧为森林图
    """
    df = data.copy()
    df = df.sort_values(estimate_col, ascending=True).reset_index(drop=True)
    df["y_pos"] = range(len(df))
    df["OR_CI"] = df.apply(
        lambda r: f"{r[estimate_col]:.3f} ({r[lower_col]:.3f}, {r[upper_col]:.3f})",
        axis=1,
    )

    # 分割：左侧表格区 (30%) + 右侧森林图区 (70%)
    fig = plt.figure(figsize=figsize)
    ax_table = plt.subplot2grid((1, 3), (0, 0), colspan=1)
    ax_forest = plt.subplot2grid((1, 3), (0, 1), colspan=2)

    # 左侧表格
    ax_table.axis("off")
    table_data = [[v] for v in df[var_col]]
    if extra_cols:
        for c in extra_cols:
            for i, v in enumerate(df[c]):
                table_data[i].append(str(round(v, 3) if isinstance(v, float) else v))
    table_data = [["Variable"] + (extra_cols or [])] + table_data
    tbl = ax_table.table(
        cellText=table_data,
        loc="center",
        cellLoc="left",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.3)
    for key, cell in tbl.get_celld().items():
        if key[0] == 0:
            cell.set_fontsize(9)
            cell.set_text_props(weight="bold")

    # 右侧森林图
    for _, row in df.iterrows():
        ax_forest.plot(
            [row[lower_col], row[upper_col]],
            [row["y_pos"], row["y_pos"]],
            color="grey", linewidth=2,
        )
    ax_forest.scatter(
        df[estimate_col], df["y_pos"],
        s=60, color="steelblue", zorder=5,
    )
    ax_forest.axvline(x=ref_line, linestyle="--", color="grey", alpha=0.7)
    ax_forest.set_xlabel("Effect (95% CI)", fontsize=10)
    ax_forest.set_title(title, fontsize=12, fontweight="bold")
    ax_forest.set_yticks(df["y_pos"])
    ax_forest.set_yticklabels(df[var_col])
    ax_forest.invert_yaxis()
    ax_forest.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    return fig


# ============================================================================
# 示例
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    demo_data = pd.DataFrame(
        {
            "variable": ["Age (per 10yr)", "BMI (per 5)", "Smoking",
                         "Hypertension", "Diabetes", "Physical Activity"],
            "estimate": [1.45, 1.22, 2.10, 1.80, 1.65, 0.75],
            "lower": [1.20, 1.05, 1.60, 1.40, 1.30, 0.58],
            "upper": [1.75, 1.42, 2.75, 2.30, 2.10, 0.97],
            "p_value": [0.001, 0.015, 0.002, 0.008, 0.012, 0.030],
        }
    )

    fig = create_forest_plot(
        demo_data,
        title="Risk Factors for Cardiovascular Disease",
        pval_col="p_value",
    )
    fig.savefig("forest_plot_demo.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("✅ forest_plot_demo.png 已保存")
