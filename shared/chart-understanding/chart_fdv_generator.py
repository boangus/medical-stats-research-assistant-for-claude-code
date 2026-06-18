"""
FDV 描述生成器

基于 FDV（Formalized Description for Visualization）方法将图表转化为结构化文本描述。

参考文献：
Yang et al. "FDV: Formalized Description for Visualization - A Structured Textual Representation of Charts"

主要功能：
1. 提取图表数据点
2. 描述坐标轴信息
3. 提取关键发现
4. 生成统计摘要
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ChartType(Enum):
    """图表类型枚举"""
    KM_CURVE = "km_curve"
    FOREST_PLOT = "forest_plot"
    ROC_CURVE = "roc_curve"
    CALIBRATION_PLOT = "calibration_plot"
    DECISION_CURVE = "decision_curve"
    BOXPLOT = "boxplot"
    BAR_CHART = "bar_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    RCS_CURVE = "rcs_curve"
    BLAND_ALTMAN = "bland_altman"
    CORRELATION_MATRIX = "correlation_matrix"
    SURVIVAL_PLOT = "survival_plot"
    FUNNEL_PLOT = "funnel_plot"
    NETWORK_PLOT = "network_plot"
    UNKNOWN = "unknown"


@dataclass
class AxisInfo:
    """坐标轴信息数据类"""
    label: str
    unit: str
    range_min: Optional[float]
    range_max: Optional[float]
    scale: str  # linear, log, etc.


@dataclass
class DataPoint:
    """数据点数据类"""
    x: Any
    y: Any
    label: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class ChartFDV:
    """图表FDV描述数据类"""
    chart_type: ChartType
    title: str
    subtitle: str
    x_axis: AxisInfo
    y_axis: AxisInfo
    data_points: List[DataPoint]
    legends: List[str]
    annotations: List[str]
    statistical_info: Dict[str, Any]
    key_findings: List[str]
    quality_metrics: Dict[str, Any]


class ChartFDVGenerator:
    """
    FDV 描述生成器
    
    将图表转化为结构化文本描述，支持多样化和更深入的理解。
    
    使用方法：
    ```python
    generator = ChartFDVGenerator(chart_data)
    description = generator.generate_description()
    quality = generator.assess_quality()
    consistency = generator.check_consistency()
    ```
    """
    
    def __init__(self, chart_data: Dict[str, Any]):
        """
        初始化生成器
        
        Parameters
        ----------
        chart_data : Dict
            图表数据，包含以下字段：
            - type: str - 图表类型
            - title: str - 图表标题
            - subtitle: str - 图表副标题
            - x_axis: Dict - X轴信息
            - y_axis: Dict - Y轴信息
            - data_points: List[Dict] - 数据点列表
            - legends: List[str] - 图例列表
            - annotations: List[str] - 注释列表
            - statistical_info: Dict - 统计信息
        """
        self.chart_data = chart_data
        
        # 解析图表类型
        self.chart_type = self._parse_chart_type(chart_data.get('type', 'unknown'))
        
        # 解析基本信息
        self.title = chart_data.get('title', '')
        self.subtitle = chart_data.get('subtitle', '')
        
        # 解析坐标轴信息
        self.x_axis = self._parse_axis(chart_data.get('x_axis', {}))
        self.y_axis = self._parse_axis(chart_data.get('y_axis', {}))
        
        # 解析数据点
        self.data_points = self._parse_data_points(chart_data.get('data_points', []))
        
        # 解析图例
        self.legends = chart_data.get('legends', [])
        
        # 解析注释
        self.annotations = chart_data.get('annotations', [])
        
        # 解析统计信息
        self.statistical_info = chart_data.get('statistical_info', {})
        
        # 分析结果缓存
        self._fdv_description: Optional[ChartFDV] = None
        self._quality_assessment: Optional[Dict[str, Any]] = None
        self._consistency_check: Optional[Dict[str, Any]] = None
    
    def generate_description(self) -> Dict[str, Any]:
        """
        生成图表的FDV描述
        
        Returns
        -------
        Dict
            FDV描述，包含图表的结构化文本描述
        """
        if self._fdv_description is None:
            self._fdv_description = self._perform_fdv_generation()
        
        return {
            'chart_type': self._fdv_description.chart_type.value,
            'title': self._fdv_description.title,
            'subtitle': self._fdv_description.subtitle,
            'x_axis': {
                'label': self._fdv_description.x_axis.label,
                'unit': self._fdv_description.x_axis.unit,
                'range': f"{self._fdv_description.x_axis.range_min} - {self._fdv_description.x_axis.range_max}",
                'scale': self._fdv_description.x_axis.scale
            },
            'y_axis': {
                'label': self._fdv_description.y_axis.label,
                'unit': self._fdv_description.y_axis.unit,
                'range': f"{self._fdv_description.y_axis.range_min} - {self._fdv_description.y_axis.range_max}",
                'scale': self._fdv_description.y_axis.scale
            },
            'data_points_count': len(self._fdv_description.data_points),
            'legends': self._fdv_description.legends,
            'annotations': self._fdv_description.annotations,
            'statistical_info': self._fdv_description.statistical_info,
            'key_findings': self._fdv_description.key_findings,
            'textual_description': self._generate_textual_description(),
            'structured_description': self._generate_structured_description()
        }
    
    def assess_quality(self) -> Dict[str, Any]:
        """
        评估图表质量
        
        Returns
        -------
        Dict
            质量评估结果，包含各项质量指标和总体分数
        """
        if self._quality_assessment is None:
            self._quality_assessment = self._perform_quality_assessment()
        
        return self._quality_assessment
    
    def check_consistency(self) -> Dict[str, Any]:
        """
        检查图表一致性
        
        Returns
        -------
        Dict
            一致性检查结果，包含数据一致性、标签一致性等
        """
        if self._consistency_check is None:
            self._consistency_check = self._perform_consistency_check()
        
        return self._consistency_check
    
    def _parse_chart_type(self, chart_type_str: str) -> ChartType:
        """解析图表类型"""
        chart_type_mapping = {
            'km_curve': ChartType.KM_CURVE,
            'forest_plot': ChartType.FOREST_PLOT,
            'roc_curve': ChartType.ROC_CURVE,
            'calibration_plot': ChartType.CALIBRATION_PLOT,
            'decision_curve': ChartType.DECISION_CURVE,
            'boxplot': ChartType.BOXPLOT,
            'bar_chart': ChartType.BAR_CHART,
            'scatter_plot': ChartType.SCATTER_PLOT,
            'heatmap': ChartType.HEATMAP,
            'rcs_curve': ChartType.RCS_CURVE,
            'bland_altman': ChartType.BLAND_ALTMAN,
            'correlation_matrix': ChartType.CORRELATION_MATRIX,
            'survival_plot': ChartType.SURVIVAL_PLOT,
            'funnel_plot': ChartType.FUNNEL_PLOT,
            'network_plot': ChartType.NETWORK_PLOT,
        }
        
        return chart_type_mapping.get(chart_type_str.lower(), ChartType.UNKNOWN)
    
    def _parse_axis(self, axis_data: Dict[str, Any]) -> AxisInfo:
        """解析坐标轴信息"""
        return AxisInfo(
            label=axis_data.get('label', ''),
            unit=axis_data.get('unit', ''),
            range_min=axis_data.get('range_min'),
            range_max=axis_data.get('range_max'),
            scale=axis_data.get('scale', 'linear')
        )
    
    def _parse_data_points(self, data_points_data: List[Dict[str, Any]]) -> List[DataPoint]:
        """解析数据点"""
        data_points = []
        
        for point_data in data_points_data:
            data_point = DataPoint(
                x=point_data.get('x'),
                y=point_data.get('y'),
                label=point_data.get('label'),
                metadata=point_data.get('metadata', {})
            )
            data_points.append(data_point)
        
        return data_points
    
    def _perform_fdv_generation(self) -> ChartFDV:
        """执行FDV描述生成"""
        # 提取关键发现
        key_findings = self._extract_key_findings()
        
        # 计算质量指标
        quality_metrics = self._calculate_quality_metrics()
        
        return ChartFDV(
            chart_type=self.chart_type,
            title=self.title,
            subtitle=self.subtitle,
            x_axis=self.x_axis,
            y_axis=self.y_axis,
            data_points=self.data_points,
            legends=self.legends,
            annotations=self.annotations,
            statistical_info=self.statistical_info,
            key_findings=key_findings,
            quality_metrics=quality_metrics
        )
    
    def _extract_key_findings(self) -> List[str]:
        """提取关键发现"""
        findings = []
        
        # 基于图表类型提取关键发现
        if self.chart_type == ChartType.KM_CURVE:
            findings.extend(self._extract_km_curve_findings())
        elif self.chart_type == ChartType.FOREST_PLOT:
            findings.extend(self._extract_forest_plot_findings())
        elif self.chart_type == ChartType.ROC_CURVE:
            findings.extend(self._extract_roc_curve_findings())
        elif self.chart_type == ChartType.SCATTER_PLOT:
            findings.extend(self._extract_scatter_plot_findings())
        elif self.chart_type == ChartType.BOXPLOT:
            findings.extend(self._extract_boxplot_findings())
        elif self.chart_type == ChartType.BAR_CHART:
            findings.extend(self._extract_bar_chart_findings())
        
        # 基于统计信息提取发现
        if self.statistical_info:
            findings.extend(self._extract_statistical_findings())
        
        # 基于数据点提取发现
        if self.data_points:
            findings.extend(self._extract_data_point_findings())
        
        return findings
    
    def _extract_km_curve_findings(self) -> List[str]:
        """提取KM曲线关键发现"""
        findings = []
        
        # 检查中位生存时间
        if 'median_survival' in self.statistical_info:
            median = self.statistical_info['median_survival']
            findings.append(f"中位生存时间为{median}")
        
        # 检查生存率
        if 'survival_rates' in self.statistical_info:
            rates = self.statistical_info['survival_rates']
            for time_point, rate in rates.items():
                findings.append(f"{time_point}时生存率为{rate:.1%}")
        
        # 检查风险人数
        if 'number_at_risk' in self.statistical_info:
            findings.append("图表包含风险人数表")
        
        # 检查P值
        if 'p_value' in self.statistical_info:
            p_value = self.statistical_info['p_value']
            findings.append(f"组间比较P值为{p_value}")
        
        # 检查置信区间
        if 'confidence_interval' in self.statistical_info:
            ci = self.statistical_info['confidence_interval']
            findings.append(f"生存率置信区间为{ci}")
        
        return findings
    
    def _extract_forest_plot_findings(self) -> List[str]:
        """提取森林图关键发现"""
        findings = []
        
        # 检查效应量
        if 'effect_size' in self.statistical_info:
            effect = self.statistical_info['effect_size']
            findings.append(f"合并效应量为{effect}")
        
        # 检查异质性
        if 'heterogeneity' in self.statistical_info:
            het = self.statistical_info['heterogeneity']
            if 'I2' in het:
                findings.append(f"异质性I²为{het['I2']:.1%}")
            if 'p_value' in het:
                findings.append(f"异质性检验P值为{het['p_value']}")
        
        # 检查研究数量
        if 'study_count' in self.statistical_info:
            count = self.statistical_info['study_count']
            findings.append(f"纳入{count}项研究")
        
        return findings
    
    def _extract_roc_curve_findings(self) -> List[str]:
        """提取ROC曲线关键发现"""
        findings = []
        
        # 检查AUC
        if 'auc' in self.statistical_info:
            auc = self.statistical_info['auc']
            findings.append(f"AUC为{auc:.3f}")
        
        # 检查最优截断点
        if 'optimal_cutoff' in self.statistical_info:
            cutoff = self.statistical_info['optimal_cutoff']
            findings.append(f"最优截断点为{cutoff}")
        
        # 检查敏感性/特异性
        if 'sensitivity' in self.statistical_info:
            sens = self.statistical_info['sensitivity']
            findings.append(f"敏感性为{sens:.1%}")
        
        if 'specificity' in self.statistical_info:
            spec = self.statistical_info['specificity']
            findings.append(f"特异性为{spec:.1%}")
        
        return findings
    
    def _extract_scatter_plot_findings(self) -> List[str]:
        """提取散点图关键发现"""
        findings = []
        
        # 检查相关系数
        if 'correlation' in self.statistical_info:
            r = self.statistical_info['correlation']
            findings.append(f"相关系数r={r:.3f}")
        
        # 检查P值
        if 'p_value' in self.statistical_info:
            p = self.statistical_info['p_value']
            findings.append(f"相关性检验P值为{p}")
        
        # 检查回归方程
        if 'regression_equation' in self.statistical_info:
            eq = self.statistical_info['regression_equation']
            findings.append(f"回归方程为{eq}")
        
        # 检查R²
        if 'r_squared' in self.statistical_info:
            r2 = self.statistical_info['r_squared']
            findings.append(f"R²={r2:.3f}")
        
        return findings
    
    def _extract_boxplot_findings(self) -> List[str]:
        """提取箱线图关键发现"""
        findings = []
        
        # 检查中位数
        if 'median' in self.statistical_info:
            median = self.statistical_info['median']
            findings.append(f"中位数为{median}")
        
        # 检查四分位距
        if 'iqr' in self.statistical_info:
            iqr = self.statistical_info['iqr']
            findings.append(f"四分位距为{iqr}")
        
        # 检查异常值
        if 'outliers' in self.statistical_info:
            outliers = self.statistical_info['outliers']
            if outliers:
                findings.append(f"发现{len(outliers)}个异常值")
        
        return findings
    
    def _extract_bar_chart_findings(self) -> List[str]:
        """提取柱状图关键发现"""
        findings = []
        
        # 检查最大值
        if 'max_value' in self.statistical_info:
            max_val = self.statistical_info['max_value']
            findings.append(f"最大值为{max_val}")
        
        # 检查最小值
        if 'min_value' in self.statistical_info:
            min_val = self.statistical_info['min_value']
            findings.append(f"最小值为{min_val}")
        
        # 检查组间差异
        if 'group_difference' in self.statistical_info:
            diff = self.statistical_info['group_difference']
            findings.append(f"组间差异为{diff}")
        
        # 检查P值
        if 'p_value' in self.statistical_info:
            p = self.statistical_info['p_value']
            findings.append(f"组间比较P值为{p}")
        
        return findings
    
    def _extract_statistical_findings(self) -> List[str]:
        """基于统计信息提取发现"""
        findings = []
        
        # 检查样本量
        if 'sample_size' in self.statistical_info:
            n = self.statistical_info['sample_size']
            findings.append(f"样本量为{n}")
        
        # 检查P值
        if 'p_value' in self.statistical_info:
            p = self.statistical_info['p_value']
            if p < 0.001:
                findings.append("P < 0.001，差异具有统计学意义")
            elif p < 0.05:
                findings.append(f"P = {p:.3f}，差异具有统计学意义")
            else:
                findings.append(f"P = {p:.3f}，差异无统计学意义")
        
        # 检查置信区间
        if 'confidence_interval' in self.statistical_info:
            ci = self.statistical_info['confidence_interval']
            findings.append(f"95%置信区间为{ci}")
        
        return findings
    
    def _extract_data_point_findings(self) -> List[str]:
        """基于数据点提取发现"""
        findings = []
        
        if not self.data_points:
            return findings
        
        # 统计数据点数量
        findings.append(f"图表包含{len(self.data_points)}个数据点")
        
        # 检查数据点标签
        labeled_points = [p for p in self.data_points if p.label]
        if labeled_points:
            findings.append(f"其中{labeled_points.len()}个数据点有标签")
        
        # 检查数据点范围
        x_values = [p.x for p in self.data_points if p.x is not None]
        y_values = [p.y for p in self.data_points if p.y is not None]
        
        if x_values:
            try:
                x_numeric = [float(x) for x in x_values if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '').replace('-', '').isdigit())]
                if x_numeric:
                    findings.append(f"X轴数据范围：{min(x_numeric):.2f} - {max(x_numeric):.2f}")
            except (ValueError, TypeError):
                pass
        
        if y_values:
            try:
                y_numeric = [float(y) for y in y_values if isinstance(y, (int, float)) or (isinstance(y, str) and y.replace('.', '').replace('-', '').isdigit())]
                if y_numeric:
                    findings.append(f"Y轴数据范围：{min(y_numeric):.2f} - {max(y_numeric):.2f}")
            except (ValueError, TypeError):
                pass
        
        return findings
    
    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """计算质量指标"""
        metrics = {
            'completeness': 0.0,
            'clarity': 0.0,
            'accuracy': 0.0,
            'overall_score': 0.0
        }
        
        # 计算完整性
        completeness_score = 0.0
        total_checks = 0
        
        # 检查标题
        total_checks += 1
        if self.title:
            completeness_score += 1
        
        # 检查坐标轴标签
        total_checks += 2
        if self.x_axis.label:
            completeness_score += 1
        if self.y_axis.label:
            completeness_score += 1
        
        # 检查数据点
        total_checks += 1
        if self.data_points:
            completeness_score += 1
        
        # 检查图例
        total_checks += 1
        if self.legends:
            completeness_score += 1
        
        metrics['completeness'] = completeness_score / total_checks if total_checks > 0 else 0.0
        
        # 计算清晰度
        clarity_score = 0.0
        clarity_checks = 0
        
        # 检查坐标轴单位
        clarity_checks += 2
        if self.x_axis.unit:
            clarity_score += 1
        if self.y_axis.unit:
            clarity_score += 1
        
        # 检查注释
        clarity_checks += 1
        if self.annotations:
            clarity_score += 1
        
        metrics['clarity'] = clarity_score / clarity_checks if clarity_checks > 0 else 0.0
        
        # 计算准确性
        accuracy_score = 0.0
        accuracy_checks = 0
        
        # 检查统计信息
        accuracy_checks += 1
        if self.statistical_info:
            accuracy_score += 1
        
        # 检查关键发现
        accuracy_checks += 1
        key_findings = self._extract_key_findings()
        if key_findings:
            accuracy_score += 1
        
        metrics['accuracy'] = accuracy_score / accuracy_checks if accuracy_checks > 0 else 0.0
        
        # 计算总体分数
        metrics['overall_score'] = (
            metrics['completeness'] * 0.4 +
            metrics['clarity'] * 0.3 +
            metrics['accuracy'] * 0.3
        )
        
        return metrics
    
    def _perform_quality_assessment(self) -> Dict[str, Any]:
        """执行质量评估"""
        # 计算质量指标
        quality_metrics = self._calculate_quality_metrics()
        
        # 生成质量评估报告
        assessment = {
            'metrics': quality_metrics,
            'score': quality_metrics['overall_score'],
            'grade': self._calculate_grade(quality_metrics['overall_score']),
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # 识别优势
        if quality_metrics['completeness'] >= 0.8:
            assessment['strengths'].append("图表信息完整")
        if quality_metrics['clarity'] >= 0.8:
            assessment['strengths'].append("图表清晰易读")
        if quality_metrics['accuracy'] >= 0.8:
            assessment['strengths'].append("图表数据准确")
        
        # 识别弱点
        if quality_metrics['completeness'] < 0.6:
            assessment['weaknesses'].append("图表信息不完整")
            assessment['recommendations'].append("补充缺失的图表元素（标题、坐标轴标签、图例等）")
        
        if quality_metrics['clarity'] < 0.6:
            assessment['weaknesses'].append("图表清晰度不足")
            assessment['recommendations'].append("添加坐标轴单位、注释等提高清晰度")
        
        if quality_metrics['accuracy'] < 0.6:
            assessment['weaknesses'].append("图表数据准确性不足")
            assessment['recommendations'].append("添加统计信息、关键发现等提高准确性")
        
        return assessment
    
    def _calculate_grade(self, score: float) -> str:
        """计算等级"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def _perform_consistency_check(self) -> Dict[str, Any]:
        """执行一致性检查"""
        consistency = {
            'data_consistency': True,
            'label_consistency': True,
            'axis_consistency': True,
            'overall_consistency': True,
            'issues': []
        }
        
        # 检查数据一致性
        data_issues = self._check_data_consistency()
        if data_issues:
            consistency['data_consistency'] = False
            consistency['issues'].extend(data_issues)
        
        # 检查标签一致性
        label_issues = self._check_label_consistency()
        if label_issues:
            consistency['label_consistency'] = False
            consistency['issues'].extend(label_issues)
        
        # 检查坐标轴一致性
        axis_issues = self._check_axis_consistency()
        if axis_issues:
            consistency['axis_consistency'] = False
            consistency['issues'].extend(axis_issues)
        
        # 计算总体一致性
        consistency['overall_consistency'] = (
            consistency['data_consistency'] and
            consistency['label_consistency'] and
            consistency['axis_consistency']
        )
        
        return consistency
    
    def _check_data_consistency(self) -> List[str]:
        """检查数据一致性"""
        issues = []
        
        # 检查数据点是否为空
        if not self.data_points:
            issues.append("图表没有数据点")
        
        # 检查数据点类型一致性
        x_types = set()
        y_types = set()
        
        for point in self.data_points:
            if point.x is not None:
                x_types.add(type(point.x).__name__)
            if point.y is not None:
                y_types.add(type(point.y).__name__)
        
        if len(x_types) > 1:
            issues.append(f"X轴数据类型不一致：{x_types}")
        
        if len(y_types) > 1:
            issues.append(f"Y轴数据类型不一致：{y_types}")
        
        return issues
    
    def _check_label_consistency(self) -> List[str]:
        """检查标签一致性"""
        issues = []
        
        # 检查图例数量与数据系列是否匹配
        if self.legends and self.data_points:
            # 这里可以根据具体图表类型进行更详细的检查
            pass
        
        # 检查坐标轴标签是否为空
        if not self.x_axis.label:
            issues.append("X轴缺少标签")
        
        if not self.y_axis.label:
            issues.append("Y轴缺少标签")
        
        return issues
    
    def _check_axis_consistency(self) -> List[str]:
        """检查坐标轴一致性"""
        issues = []
        
        # 检查坐标轴范围
        if self.x_axis.range_min is not None and self.x_axis.range_max is not None:
            if self.x_axis.range_min >= self.x_axis.range_max:
                issues.append("X轴范围无效（最小值 >= 最大值）")
        
        if self.y_axis.range_min is not None and self.y_axis.range_max is not None:
            if self.y_axis.range_min >= self.y_axis.range_max:
                issues.append("Y轴范围无效（最小值 >= 最大值）")
        
        # 检查数据点是否在坐标轴范围内
        if self.data_points and self.x_axis.range_min is not None and self.x_axis.range_max is not None:
            for i, point in enumerate(self.data_points):
                try:
                    x_val = float(point.x)
                    if x_val < self.x_axis.range_min or x_val > self.x_axis.range_max:
                        issues.append(f"数据点{i+1}的X值{point.x}超出坐标轴范围")
                except (ValueError, TypeError):
                    pass
        
        return issues
    
    def _generate_textual_description(self) -> str:
        """生成文本描述"""
        if self._fdv_description is None:
            self._fdv_description = self._perform_fdv_generation()
        
        description_parts = []
        
        # 图表标题
        if self._fdv_description.title:
            description_parts.append(f"图表标题：{self._fdv_description.title}")
        
        # 图表类型
        chart_type_desc = self._get_chart_type_description()
        description_parts.append(f"图表类型：{chart_type_desc}")
        
        # 坐标轴描述
        x_desc = self._describe_axis(self._fdv_description.x_axis, "X轴")
        y_desc = self._describe_axis(self._fdv_description.y_axis, "Y轴")
        description_parts.append(x_desc)
        description_parts.append(y_desc)
        
        # 数据点描述
        if self._fdv_description.data_points:
            description_parts.append(f"数据点数量：{len(self._fdv_description.data_points)}")
        
        # 图例描述
        if self._fdv_description.legends:
            legends_str = "、".join(self._fdv_description.legends)
            description_parts.append(f"图例：{legends_str}")
        
        # 统计信息描述
        if self._fdv_description.statistical_info:
            stat_desc = self._describe_statistical_info()
            description_parts.append(stat_desc)
        
        # 关键发现描述
        if self._fdv_description.key_findings:
            findings_str = "；".join(self._fdv_description.key_findings[:3])
            description_parts.append(f"关键发现：{findings_str}")
        
        return "。".join(description_parts) + "。"
    
    def _get_chart_type_description(self) -> str:
        """获取图表类型描述"""
        type_descriptions = {
            ChartType.KM_CURVE: "Kaplan-Meier生存曲线",
            ChartType.FOREST_PLOT: "森林图",
            ChartType.ROC_CURVE: "ROC曲线",
            ChartType.CALIBRATION_PLOT: "校准曲线",
            ChartType.DECISION_CURVE: "决策曲线",
            ChartType.BOXPLOT: "箱线图",
            ChartType.BAR_CHART: "柱状图",
            ChartType.SCATTER_PLOT: "散点图",
            ChartType.HEATMAP: "热图",
            ChartType.RCS_CURVE: "限制性立方样条曲线",
            ChartType.BLAND_ALTMAN: "Bland-Altman图",
            ChartType.CORRELATION_MATRIX: "相关矩阵图",
            ChartType.SURVIVAL_PLOT: "生存曲线",
            ChartType.FUNNEL_PLOT: "漏斗图",
            ChartType.NETWORK_PLOT: "网络图",
            ChartType.UNKNOWN: "未知类型图表"
        }
        
        return type_descriptions.get(self._fdv_description.chart_type, "未知类型图表")
    
    def _describe_axis(self, axis: AxisInfo, axis_name: str) -> str:
        """描述坐标轴"""
        parts = [f"{axis_name}："]
        
        if axis.label:
            parts.append(f"标签为'{axis.label}'")
        
        if axis.unit:
            parts.append(f"单位为'{axis.unit}'")
        
        if axis.range_min is not None and axis.range_max is not None:
            parts.append(f"范围从{axis.range_min}到{axis.range_max}")
        
        if axis.scale != 'linear':
            parts.append(f"刻度为{axis.scale}")
        
        return "，".join(parts)
    
    def _describe_statistical_info(self) -> str:
        """描述统计信息"""
        if not self._fdv_description.statistical_info:
            return ""
        
        parts = ["统计信息："]
        
        # 描述样本量
        if 'sample_size' in self._fdv_description.statistical_info:
            n = self._fdv_description.statistical_info['sample_size']
            parts.append(f"样本量{n}")
        
        # 描述P值
        if 'p_value' in self._fdv_description.statistical_info:
            p = self._fdv_description.statistical_info['p_value']
            if p < 0.001:
                parts.append("P < 0.001")
            elif p < 0.05:
                parts.append(f"P = {p:.3f}")
            else:
                parts.append(f"P = {p:.3f}")
        
        # 描述置信区间
        if 'confidence_interval' in self._fdv_description.statistical_info:
            ci = self._fdv_description.statistical_info['confidence_interval']
            parts.append(f"95% CI: {ci}")
        
        return "，".join(parts)
    
    def _generate_structured_description(self) -> Dict[str, Any]:
        """生成结构化描述"""
        if self._fdv_description is None:
            self._fdv_description = self._perform_fdv_generation()
        
        return {
            'title': self._fdv_description.title,
            'subtitle': self._fdv_description.subtitle,
            'chart_type': self._fdv_description.chart_type.value,
            'axes': {
                'x': {
                    'label': self._fdv_description.x_axis.label,
                    'unit': self._fdv_description.x_axis.unit,
                    'range': f"{self._fdv_description.x_axis.range_min} - {self._fdv_description.x_axis.range_max}",
                    'scale': self._fdv_description.x_axis.scale
                },
                'y': {
                    'label': self._fdv_description.y_axis.label,
                    'unit': self._fdv_description.y_axis.unit,
                    'range': f"{self._fdv_description.y_axis.range_min} - {self._fdv_description.y_axis.range_max}",
                    'scale': self._fdv_description.y_axis.scale
                }
            },
            'data_points': len(self._fdv_description.data_points),
            'legends': self._fdv_description.legends,
            'annotations': self._fdv_description.annotations,
            'statistical_info': self._fdv_description.statistical_info,
            'key_findings': self._fdv_description.key_findings,
            'quality_metrics': self._fdv_description.quality_metrics
        }


# 示例用法
if __name__ == "__main__":
    # 示例图表数据
    sample_chart = {
        'type': 'scatter_plot',
        'title': '年龄与血压的关系',
        'subtitle': '2026年研究数据',
        'x_axis': {
            'label': '年龄',
            'unit': '岁',
            'range_min': 20,
            'range_max': 60,
            'scale': 'linear'
        },
        'y_axis': {
            'label': '收缩压',
            'unit': 'mmHg',
            'range_min': 100,
            'range_max': 160,
            'scale': 'linear'
        },
        'data_points': [
            {'x': 25, 'y': 120, 'label': '张三'},
            {'x': 30, 'y': 115, 'label': '李四'},
            {'x': 28, 'y': 130, 'label': '王五'},
            {'x': 35, 'y': 125, 'label': '赵六'},
            {'x': 40, 'y': 140, 'label': '钱七'},
            {'x': 45, 'y': 135, 'label': '孙八'},
        ],
        'legends': ['研究对象'],
        'annotations': ['趋势线'],
        'statistical_info': {
            'sample_size': 6,
            'correlation': 0.85,
            'p_value': 0.03,
            'r_squared': 0.72,
            'regression_equation': 'y = 1.2x + 90'
        }
    }
    
    generator = ChartFDVGenerator(sample_chart)
    
    print("FDV描述:")
    print(json.dumps(generator.generate_description(), ensure_ascii=False, indent=2))
    
    print("\n质量评估:")
    print(json.dumps(generator.assess_quality(), ensure_ascii=False, indent=2))
    
    print("\n一致性检查:")
    print(json.dumps(generator.check_consistency(), ensure_ascii=False, indent=2))