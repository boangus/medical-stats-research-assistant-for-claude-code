"""
bland_altman_template.py — Bland-Altman 图模板（Python）
=======================================================
适用于：方法比较、测量一致性评估

依赖: matplotlib, numpy, pandas, scipy
安装: pip install matplotlib numpy pandas scipy

作者: MSRA Team
版本: 0.1.0
"""

from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import logging

logger = logging.getLogger(__name__)


def plot_bland_altman(
    method1: np.ndarray,
    method2: np.ndarray,
    title: str = "Bland-Altman Plot",
    x_label: str = "Mean of Two Methods",
    y_label: str = "Difference (Method1 - Method2)",
    conf_int: bool = True,
    proportional_bias: bool = False,
    figsize: Tuple[float, float] = (8, 6),
) -> Dict:
    """Bland-Altman 图（绝对差异）

    Parameters
    ----------
    method1, method2 : np.ndarray
        两种方法的测量值
    title, x_label, y_label : str
        标题和轴标签
    conf_int : bool
        是否显示 LoA 置信区间带
    proportional_bias : bool
        是否检查比例偏差
    figsize : Tuple
        图尺寸

    Returns
    -------
    Dict
        包含 fig, ax, stats
    """
    mean_vals = (method1 + method2) / 2
    diff_vals = method1 - method2

    n = len(diff_vals)
    mean_diff = np.nanmean(diff_vals)
    sd_diff = np.nanstd(diff_vals, ddof=1)

    loa_upper = mean_diff + 1.96 * sd_diff
    loa_lower = mean_diff - 1.96 * sd_diff

    # LoA 置信区间
    se_loa = np.sqrt(3 * sd_diff**2 / n)
    loa_upper_ci = (loa_upper - 1.96 * se_loa, loa_upper + 1.96 * se_loa)
    loa_lower_ci = (loa_lower - 1.96 * se_loa, loa_lower + 1.96 * se_loa)

    within_loa = np.sum((diff_vals >= loa_lower) & (diff_vals <= loa_upper))
    pct_within = within_loa / n * 100

    # 重复系数
    rc = 1.96 * np.sqrt(2) * sd_diff

    fig, ax = plt.subplots(figsize=figsize)

    # 散点
    ax.scatter(mean_vals, diff_vals, alpha=0.6, s=30, color="steelblue",
               edgecolors="white", linewidth=0.5)

    # 平均差异线
    ax.axhline(y=mean_diff, color="steelblue", linewidth=1.5, label=f"Mean diff = {mean_diff:.2f}")

    # 一致性界限
    ax.axhline(y=loa_upper, linestyle="--", color="#E74C3C", linewidth=1,
               label=f"Upper LoA = {loa_upper:.2f}")
    ax.axhline(y=loa_lower, linestyle="--", color="#E74C3C", linewidth=1,
               label=f"Lower LoA = {loa_lower:.2f}")

    # 零线
    ax.axhline(y=0, linestyle=":", color="grey", linewidth=0.8, alpha=0.5)

    # LoA 置信区间带
    if conf_int:
        ax.axhspan(loa_lower_ci[0], loa_lower_ci[1],
                   alpha=0.05, color="#E74C3C")
        ax.axhspan(loa_upper_ci[0], loa_upper_ci[1],
                   alpha=0.05, color="#E74C3C")

    # 比例偏差检查
    if proportional_bias:
        slope, intercept, r_val, p_val, std_err = stats.linregress(mean_vals, diff_vals)
        if p_val < 0.05:
            x_line = np.array([mean_vals.min(), mean_vals.max()])
            y_line = intercept + slope * x_line
            ax.plot(x_line, y_line, color="darkorange", linewidth=1, linestyle="-",
                    alpha=0.7, label=f"Proportional bias (p={p_val:.3f})")

    ax.set_xlabel(x_label, fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")

    subtitle_text = (
        f"Mean diff = {mean_diff:.2f} (SD = {sd_diff:.2f})\n"
        f"Upper LoA = {loa_upper:.2f}, Lower LoA = {loa_lower:.2f}\n"
        f"{pct_within:.1f}% within LoA | RC = {rc:.2f}"
    )
    ax.text(0.98, 0.02, subtitle_text, transform=ax.transAxes,
            fontsize=8, va="bottom", ha="right",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3, linestyle=":")

    plt.tight_layout()

    return {
        "fig": fig,
        "ax": ax,
        "stats": {
            "n": n,
            "mean_diff": mean_diff,
            "sd_diff": sd_diff,
            "loa_upper": loa_upper,
            "loa_lower": loa_lower,
            "pct_within_loa": pct_within,
            "rc": rc,
        },
    }


def plot_bland_altman_pct(
    method1: np.ndarray,
    method2: np.ndarray,
    title: str = "Bland-Altman Plot (% Difference)",
    figsize: Tuple[float, float] = (8, 6),
) -> Dict:
    """百分比差异 Bland-Altman 图"""
    mean_vals = (method1 + method2) / 2
    pct_diff = (method1 - method2) / mean_vals * 100

    n = len(pct_diff)
    mean_pct = np.nanmean(pct_diff)
    sd_pct = np.nanstd(pct_diff, ddof=1)

    loa_upper = mean_pct + 1.96 * sd_pct
    loa_lower = mean_pct - 1.96 * sd_pct

    within = np.sum((pct_diff >= loa_lower) & (pct_diff <= loa_upper)) / n * 100

    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(mean_vals, pct_diff, alpha=0.6, s=30, color="steelblue")
    ax.axhline(y=mean_pct, color="steelblue", linewidth=1.5)
    ax.axhline(y=loa_upper, linestyle="--", color="#E74C3C", linewidth=1)
    ax.axhline(y=loa_lower, linestyle="--", color="#E74C3C", linewidth=1)
    ax.axhline(y=0, linestyle=":", color="grey", linewidth=0.8)
    ax.set_xlabel("Mean of Two Methods", fontsize=11)
    ax.set_ylabel("% Difference", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")

    stats_text = (
        f"Mean % diff = {mean_pct:.1f}% (SD = {sd_pct:.1f}%)\n"
        f"LoA: {loa_lower:.1f}% to {loa_upper:.1f}%\n"
        f"{within:.1f}% within LoA"
    )
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
            fontsize=9, va="bottom", ha="right",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
    ax.grid(alpha=0.3, linestyle=":")
    plt.tight_layout()

    return {
        "fig": fig,
        "stats": {
            "mean_pct_diff": mean_pct,
            "sd_pct_diff": sd_pct,
            "loa_upper": loa_upper,
            "loa_lower": loa_lower,
            "pct_within_loa": within,
        },
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    np.random.seed(42)
    n = 100
    true_val = np.random.uniform(10, 100, n)
    m1 = true_val + np.random.normal(0, 3, n)
    m2 = true_val + np.random.normal(2, 4, n)  # bias

    res = plot_bland_altman(m1, m2, title="Device A vs Device B")
    res["fig"].savefig("bland_altman_demo.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("✅ bland_altman_demo.png 已保存")
    logger.info(f"Stats: mean_diff={res['stats']['mean_diff']:.2f}")
