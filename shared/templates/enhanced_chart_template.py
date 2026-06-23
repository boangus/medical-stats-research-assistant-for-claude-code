#!/usr/bin/env python3
"""
MSRA 增强图表生成模板

支持自动调整图表尺寸、中英文标签、高分辨率输出。
用于 Report Generation 的 Phase 4 图表生成。
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import os
import json
import logging

logger = logging.getLogger(__name__)


class EnhancedChartGenerator:
    """增强图表生成器"""
    
    def __init__(self, journal_config: Optional[str] = None):
        """
        初始化图表生成器
        
        Args:
            journal_config: 期刊配置文件路径（可选）
        """
        self.config = self._load_config(journal_config)
        self.font_config = self.config.get("font", {})
        self.size_config = self.config.get("sizes", {})
        self.color_config = self.config.get("colors", {})
        
        # 设置中文字体
        self._setup_chinese_font()
        
    def _load_config(self, journal_config: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "font": {
                "family": ["Arial", "SimHei", "sans-serif"],
                "size": {
                    "title": 14,
                    "axis_labels": 12,
                    "tick_labels": 10,
                    "legend": 9,
                    "caption": 9
                }
            },
            "sizes": {
                "single_column": 85,
                "double_column": 175,
                "max_height": 230,
                "dpi": 300
            },
            "colors": {
                "primary": "#1f77b4",
                "secondary": "#aec7e8",
                "accent": "#ff7f0e",
                "background": "#ffffff",
                "text": "#333333",
                "grid": "#e0e0e0"
            }
        }
        
        if journal_config and os.path.exists(journal_config):
            try:
                with open(journal_config, 'r', encoding='utf-8') as f:
                    journal_data = json.load(f)
                    # 合并配置
                    for key in journal_data:
                        if key in default_config:
                            if isinstance(default_config[key], dict):
                                default_config[key].update(journal_data[key])
                            else:
                                default_config[key] = journal_data[key]
            except Exception as e:
                logger.info(f"加载配置文件失败: {e}")
        
        return default_config
    
    def _setup_chinese_font(self):
        """设置中文字体"""
        # 尝试设置中文字体
        font_families = self.font_config.get("family", ["Arial", "SimHei", "sans-serif"])
        
        for font in font_families:
            try:
                plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
                plt.rcParams['axes.unicode_minus'] = False
                break
            except Exception:
                continue
    
    def create_figure(self, figure_type: str, column_width: str = "single") -> Tuple[plt.Figure, plt.Axes]:
        """
        创建图表
        
        Args:
            figure_type: 图表类型
            column_width: 列宽（"single" 或 "double"）
            
        Returns:
            Figure和Axes对象
        """
        # 计算尺寸
        width_mm = self.size_config.get(column_width + "_column", 85)
        height_mm = self.size_config.get("max_height", 230) * 0.6  # 默认60%高度
        
        # 转换为英寸 (1 inch = 25.4 mm)
        width_inch = width_mm / 25.4
        height_inch = height_mm / 25.4
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(width_inch, height_inch))
        
        # 设置DPI
        dpi = self.size_config.get("dpi", 300)
        fig.set_dpi(dpi)
        
        # 设置背景色
        fig.patch.set_facecolor(self.color_config.get("background", "#ffffff"))
        
        return fig, ax
    
    def set_font_sizes(self, ax: plt.Axes, title: str = None, xlabel: str = None, ylabel: str = None):
        """
        设置字体大小
        
        Args:
            ax: Axes对象
            title: 标题
            xlabel: X轴标签
            ylabel: Y轴标签
        """
        font_sizes = self.font_config.get("size", {})
        
        if title:
            ax.set_title(title, fontsize=font_sizes.get("title", 14), fontweight='bold')
        
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=font_sizes.get("axis_labels", 12))
        
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=font_sizes.get("axis_labels", 12))
        
        # 设置刻度标签字体
        ax.tick_params(axis='both', labelsize=font_sizes.get("tick_labels", 10))
    
    def add_grid(self, ax: plt.Axes, axis: str = 'both', linestyle: str = '--', alpha: float = 0.7):
        """
        添加网格线
        
        Args:
            ax: Axes对象
            axis: 网格线轴（'both', 'x', 'y'）
            linestyle: 线型
            alpha: 透明度
        """
        grid_color = self.color_config.get("grid", "#e0e0e0")
        ax.grid(True, axis=axis, linestyle=linestyle, alpha=alpha, color=grid_color)
    
    def add_legend(self, ax: plt.Axes, labels: List[str], location: str = 'best', fontsize: int = None):
        """
        添加图例
        
        Args:
            ax: Axes对象
            labels: 标签列表
            location: 图例位置
            fontsize: 字体大小
        """
        if fontsize is None:
            fontsize = self.font_config.get("size", {}).get("legend", 9)
        
        ax.legend(labels, loc=location, fontsize=fontsize)
    
    def save_figure(self, fig: plt.Figure, filepath: str, format: str = 'png', dpi: int = None):
        """
        保存图表
        
        Args:
            fig: Figure对象
            filepath: 文件路径
            format: 文件格式
            dpi: 分辨率
        """
        if dpi is None:
            dpi = self.size_config.get("dpi", 300)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存图表
        fig.savefig(filepath, format=format, dpi=dpi, bbox_inches='tight', 
                   facecolor=fig.get_facecolor(), edgecolor='none')
        
        logger.info(f"图表已保存: {filepath} (DPI: {dpi})")
    
    def create_km_curve(self, survival_data: Dict[str, Any], title: str = "Kaplan-Meier Curve") -> Tuple[plt.Figure, plt.Axes]:
        """
        创建Kaplan-Meier曲线
        
        Args:
            survival_data: 生存数据
            title: 图表标题
            
        Returns:
            Figure和Axes对象
        """
        fig, ax = self.create_figure("km_curve")
        
        # 这里应该有实际的KM曲线绘制逻辑
        # 为简化，这里只创建一个示例
        
        # 设置字体大小
        self.set_font_sizes(ax, title=title, xlabel="Time", ylabel="Survival Probability")
        
        # 添加网格
        self.add_grid(ax)
        
        return fig, ax
    
    def create_forest_plot(self, effect_sizes: List[float], confidence_intervals: List[Tuple[float, float]], 
                          labels: List[str], title: str = "Forest Plot") -> Tuple[plt.Figure, plt.Axes]:
        """
        创建森林图
        
        Args:
            effect_sizes: 效应量列表
            confidence_intervals: 置信区间列表
            labels: 标签列表
            title: 图表标题
            
        Returns:
            Figure和Axes对象
        """
        fig, ax = self.create_figure("forest_plot")
        
        # 这里应该有实际的森林图绘制逻辑
        # 为简化，这里只创建一个示例
        
        # 设置字体大小
        self.set_font_sizes(ax, title=title, xlabel="Effect Size", ylabel="Study")
        
        # 添加网格
        self.add_grid(ax, axis='x')
        
        return fig, ax
    
    def create_roc_curve(self, fpr: np.ndarray, tpr: np.ndarray, auc_value: float, 
                        title: str = "ROC Curve") -> Tuple[plt.Figure, plt.Axes]:
        """
        创建ROC曲线
        
        Args:
            fpr: 假阳性率
            tpr: 真阳性率
            auc_value: AUC值
            title: 图表标题
            
        Returns:
            Figure和Axes对象
        """
        fig, ax = self.create_figure("roc_curve")
        
        # 绘制ROC曲线
        ax.plot(fpr, tpr, color=self.color_config.get("primary", "#1f77b4"), 
                label=f'ROC curve (AUC = {auc_value:.3f})')
        
        # 绘制随机猜测线
        ax.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random guess')
        
        # 设置字体大小
        self.set_font_sizes(ax, title=title, xlabel="False Positive Rate", ylabel="True Positive Rate")
        
        # 添加图例
        self.add_legend(ax, ['ROC curve', 'Random guess'])
        
        # 添加网格
        self.add_grid(ax)
        
        return fig, ax


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 创建图表生成器
    generator = EnhancedChartGenerator()
    
    # 创建示例图表
    fig, ax = generator.create_figure("km_curve")
    
    # 生成示例数据
    x = np.linspace(0, 10, 100)
    y = np.exp(-x/5)
    
    # 绘制曲线
    ax.plot(x, y, color=generator.color_config.get("primary"), label='Survival')
    
    # 设置字体大小
    generator.set_font_sizes(ax, title="示例Kaplan-Meier曲线", 
                           xlabel="时间（月）", ylabel="生存概率")
    
    # 添加网格
    generator.add_grid(ax)
    
    # 添加图例
    generator.add_legend(ax, ['生存曲线'])
    
    # 保存图表
    generator.save_figure(fig, "example_km_curve.png")
    
    logger.info("示例图表已生成")