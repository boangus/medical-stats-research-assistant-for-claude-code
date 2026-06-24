"""
图表理解模块

提供先进的图表理解方法，包括：
- FDV（Formalized Description for Visualization）：将图表转化为结构化文本描述

这些方法基于最新的学术研究，旨在提升医学统计研究中图表的理解和核查能力。

参考文献：
[1] Yang et al. "FDV: Formalized Description for Visualization - A Structured Textual Representation of Charts"
"""

from .chart_fdv_generator import ChartFDVGenerator

__version__ = "1.0.0"
__author__ = "MSRA Team"

__all__ = [
    'ChartFDVGenerator'
]

# 模块信息
MODULE_INFO = {
    'name': 'chart-understanding',
    'description': '图表理解模块，提供FDV等先进方法',
    'version': __version__,
    'methods': {
        'fdv': {
            'description': '将图表转化为结构化文本描述，支持多样化和更深入的理解',
            'reference': 'Yang et al. (2024)',
            'use_cases': ['图表内容理解', '图表与文本一致性检查', '图表质量评估']
        }
    }
}

# 支持的图表类型
SUPPORTED_CHART_TYPES = [
    'km_curve',           # KM生存曲线
    'forest_plot',        # 森林图
    'roc_curve',          # ROC曲线
    'calibration_plot',   # 校准曲线
    'decision_curve',     # 决策曲线
    'boxplot',            # 箱线图
    'bar_chart',          # 柱状图
    'scatter_plot',       # 散点图
    'heatmap',            # 热图
    'rcs_curve',          # RCS曲线
    'bland_altman',       # Bland-Altman图
    'correlation_matrix', # 相关矩阵图
    'survival_plot',      # 生存曲线
    'funnel_plot',        # 漏斗图
    'network_plot'        # 网络图
]

# 图表元素描述模板
CHART_ELEMENT_TEMPLATES = {
    'title': '图表标题：{title}',
    'x_axis': 'X轴：{label} (单位：{unit})',
    'y_axis': 'Y轴：{label} (单位：{unit})',
    'legend': '图例：{items}',
    'data_points': '数据点：{count}个',
    'trend_line': '趋势线：{type}',
    'confidence_interval': '置信区间：{level}%',
    'p_value': 'P值：{value}',
    'sample_size': '样本量：{n}',
    'annotation': '注释：{text}'
}
