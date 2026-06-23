#!/usr/bin/env python3
"""
MSRA Data Profile Template — 数据画像生成器

在 data-prep Phase 0 自动调用，生成一页式 Markdown 数据概览报告。

Usage:
    from data_profile_template import generate_data_profile
    md = generate_data_profile(df, output_dir="MSRA/data-prep")
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def generate_data_profile(
    df,
    output_dir: Optional[str] = None,
    file_label: str = "raw_data",
) -> str:
    """
    生成 Markdown 格式数据画像报告。

    Args:
        df: pandas DataFrame
        output_dir: 输出目录（可选，生成缺失率热力图 PNG）
        file_label: 数据文件标签（用于报告标题）

    Returns:
        Markdown 格式数据画像字符串
    """
    import pandas as pd
    import numpy as np

    rows, cols = df.shape
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    # ── 变量类型分类 ──
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64", "datetimetz"]).columns.tolist()
    text_cols = [
        c for c in categorical_cols
        if df[c].nunique() > min(50, rows * 0.5) and df[c].dtype == object
    ]
    categorical_cols = [c for c in categorical_cols if c not in text_cols]
    other_cols = [c for c in df.columns if c not in numeric_cols + categorical_cols + datetime_cols + text_cols]

    type_dist = {
        "连续变量": len(numeric_cols),
        "分类变量": len(categorical_cols),
        "日期变量": len(datetime_cols),
        "文本变量": len(text_cols),
        "其他": len(other_cols),
    }

    # ── 缺失率分析 ──
    missing = df.isnull().sum()
    missing_pct = (missing / rows * 100).round(2)
    missing_df = pd.DataFrame({
        "变量": missing.index,
        "缺失数": missing.values,
        "缺失率(%)": missing_pct.values,
    })
    missing_df = missing_df[missing_df["缺失数"] > 0].sort_values("缺失率(%)", ascending=False)
    top10_missing = missing_df.head(10)
    total_missing_pct = (df.isnull().sum().sum() / (rows * cols) * 100).round(2)

    # ── 数值变量概要 ──
    numeric_summary = None
    if numeric_cols:
        desc = df[numeric_cols].describe().T
        desc = desc[["min", "max", "mean", "50%", "std"]].copy()
        desc.columns = ["Min", "Max", "Mean", "Median", "SD"]
        desc = desc.round(3)
        numeric_summary = desc

    # ── 分类变量概要 ──
    cat_rows = []
    for c in categorical_cols:
        n_unique = df[c].nunique()
        top_val = df[c].value_counts().index[0] if n_unique > 0 else "N/A"
        top_cnt = df[c].value_counts().iloc[0] if n_unique > 0 else 0
        cat_rows.append({
            "变量": c,
            "层级数": n_unique,
            "最大层级": str(top_val)[:30],
            "最大层级频次": top_cnt,
        })
    cat_summary = pd.DataFrame(cat_rows) if cat_rows else None

    # ── 时间跨度 ──
    time_info = None
    if datetime_cols:
        for c in datetime_cols:
            earliest = df[c].min()
            latest = df[c].max()
            if pd.notna(earliest) and pd.notna(latest):
                span_days = (latest - earliest).days
                time_info = {
                    "column": c,
                    "earliest": str(earliest)[:10],
                    "latest": str(latest)[:10],
                    "span_days": span_days,
                }
                break

    # ── 极端情况检测 ──
    alerts = []
    if any(p > 50 for p in missing_pct if not np.isnan(p)):
        high_miss = [c for c, p in zip(missing.index, missing_pct) if p > 50]
        alerts.append(f"⚠️ 缺失率 > 50% 的变量: {', '.join(high_miss[:5])}")
    if cols < 3:
        alerts.append(f"⚠️ 变量数仅 {cols} 个，可能数据读取异常")
    if rows < 10:
        alerts.append(f"⚠️ 样本量仅 {rows} 例，数据可能不完整")

    # ── 组装 Markdown ──
    lines = []
    lines.append(f"# 数据画像报告：{file_label}")
    lines.append("")

    # 极端情况告警（如有）
    if alerts:
        lines.append("## 🚨 极端情况告警")
        lines.append("")
        for a in alerts:
            lines.append(f"- {a}")
        lines.append("")
        lines.append("> 上述告警需在进入 Phase 1 数据验证前确认，Checkpoint 升级为 **MANDATORY**。")
        lines.append("")

    # 1. 数据规模
    lines.append("## 1. 数据规模")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 行数（样本量） | {rows:,} |")
    lines.append(f"| 列数（变量数） | {cols} |")
    lines.append(f"| 内存占用 | {mem_mb:.2f} MB |")
    lines.append("")

    # 2. 变量类型分布
    lines.append("## 2. 变量类型分布")
    lines.append("")
    lines.append("| 类型 | 数量 | 占比 |")
    lines.append("|------|------|------|")
    for label, cnt in type_dist.items():
        if cnt > 0:
            pct = cnt / cols * 100
            lines.append(f"| {label} | {cnt} | {pct:.1f}% |")
    lines.append("")

    # 3. 缺失率
    lines.append("## 3. 缺失情况")
    lines.append("")
    lines.append(f"**总缺失率**：{total_missing_pct}%")
    lines.append("")
    if len(top10_missing) > 0:
        lines.append("**Top 10 高缺失变量**：")
        lines.append("")
        lines.append("| 变量 | 缺失数 | 缺失率(%) |")
        lines.append("|------|--------|-----------|")
        for _, r in top10_missing.iterrows():
            lines.append(f"| {r['变量']} | {int(r['缺失数']):,} | {r['缺失率(%)']:.2f} |")
    else:
        lines.append("✅ 无缺失值。")
    lines.append("")

    # 4. 数值变量概要
    if numeric_summary is not None:
        lines.append("## 4. 数值变量概要")
        lines.append("")
        lines.append("| 变量 | Min | Max | Mean | Median | SD |")
        lines.append("|------|-----|-----|------|--------|----|")
        for var, r in numeric_summary.iterrows():
            lines.append(f"| {var} | {r['Min']} | {r['Max']} | {r['Mean']} | {r['Median']} | {r['SD']} |")
        lines.append("")

    # 5. 分类变量概要
    if cat_summary is not None and len(cat_summary) > 0:
        lines.append("## 5. 分类变量概要")
        lines.append("")
        lines.append("| 变量 | 层级数 | 最大层级 | 最大层级频次 |")
        lines.append("|------|--------|---------|-------------|")
        for _, r in cat_summary.iterrows():
            lines.append(f"| {r['变量']} | {r['层级数']} | {r['最大层级']} | {r['最大层级频次']} |")
        lines.append("")

    # 6. 时间跨度
    if time_info:
        lines.append("## 6. 时间跨度")
        lines.append("")
        lines.append(f"| 列 | 最早日期 | 最晚日期 | 跨度(天) |")
        lines.append(f"|-----|---------|---------|---------|")
        lines.append(f"| {time_info['column']} | {time_info['earliest']} | {time_info['latest']} | {time_info['span_days']} |")
        lines.append("")

    md_text = "\n".join(lines)

    # ── 可选：生成缺失率热力图 ──
    if output_dir and len(missing_df) > 0:
        try:
            _generate_missing_heatmap(df, output_dir)
        except Exception:
            pass  # 图表生成失败不阻断画像

    return md_text


def _generate_missing_heatmap(df, output_dir: str):
    """生成缺失率热力图 PNG（可选）"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        return

    missing_cols = [c for c in df.columns if df[c].isnull().any()]
    if not missing_cols:
        return

    fig, ax = plt.subplots(figsize=(max(8, len(missing_cols) * 0.4), 6))
    sns.heatmap(
        df[missing_cols].isnull().astype(int),
        cbar=False, cmap="YlOrRd", ax=ax,
        yticklabels=False,
    )
    ax.set_title("Missing Value Pattern", fontsize=12)
    ax.set_xlabel("Variables")
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(os.path.join(output_dir, "missing_heatmap.png"), dpi=150)
    plt.close(fig)


def get_checkpoint_level(df) -> str:
    """
    根据数据特征判断 checkpoint 级别。

    Returns:
        "MANDATORY" 或 "SLIM"
    """
    import numpy as np

    rows, cols = df.shape
    missing_pct = df.isnull().sum() / rows * 100

    if any(p > 50 for p in missing_pct if not np.isnan(p)):
        return "MANDATORY"
    if cols < 3:
        return "MANDATORY"
    if rows < 10:
        return "MANDATORY"
    return "SLIM"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    import sys
    import pandas as pd

    if len(sys.argv) < 2:
        logger.info("Usage: python data_profile_template.py <csv_path> [output_dir]")
        sys.exit(1)

    csv_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(csv_path)

    df = pd.read_csv(csv_path)
    label = os.path.basename(csv_path)
    md = generate_data_profile(df, output_dir=out_dir, file_label=label)

    out_path = os.path.join(out_dir, "data_profile.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    logger.info(f"Data profile written to: {out_path}")
    logger.info(f"Checkpoint level: {get_checkpoint_level(df)}")
