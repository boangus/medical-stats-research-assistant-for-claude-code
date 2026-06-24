"""
图表理解模块单元测试
==================

测试FDV描述生成器
"""

import sys
from pathlib import Path

import pytest

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.chart_understanding import ChartFDVGenerator


class TestChartFDVGenerator:
    """FDV描述生成器测试"""

    def setup_method(self):
        """测试前准备"""
        self.sample_scatter_chart = {
            'type': 'scatter',
            'title': 'BMI与收缩压的关系',
            'xlabel': 'BMI (kg/m²)',
            'ylabel': '收缩压(mmHg)',
            'data_points': [
                {'x': 22.5, 'y': 120},
                {'x': 25.0, 'y': 135},
                {'x': 28.5, 'y': 145},
                {'x': 30.0, 'y': 150},
            ],
            'correlation': 0.85,
            'p_value': 0.001
        }

        self.sample_bar_chart = {
            'type': 'bar',
            'title': '不同治疗组的有效率',
            'xlabel': '治疗组',
            'ylabel': '有效率(%)',
            'categories': ['对照组', '低剂量组', '高剂量组'],
            'values': [45.2, 62.3, 78.5],
            'error_bars': [5.2, 6.1, 4.8]
        }

        self.sample_line_chart = {
            'type': 'line',
            'title': '血压随时间变化趋势',
            'xlabel': '时间(月)',
            'ylabel': '收缩压(mmHg)',
            'data_points': [
                {'x': 0, 'y': 145},
                {'x': 4, 'y': 138},
                {'x': 8, 'y': 132},
                {'x': 12, 'y': 128},
            ],
            'legend': ['治疗组', '对照组']
        }

    def test_generator_initialization(self):
        """测试生成器初始化"""
        generator = ChartFDVGenerator(self.sample_scatter_chart)
        assert generator.chart_data == self.sample_scatter_chart

    def test_generate_description_scatter(self):
        """测试散点图描述生成"""
        generator = ChartFDVGenerator(self.sample_scatter_chart)
        description = generator.generate_description()

        assert 'title' in description
        assert 'x_axis' in description
        assert 'y_axis' in description
        assert 'data_points_count' in description
        assert 'key_findings' in description

    def test_generate_description_bar(self):
        """测试柱状图描述生成"""
        generator = ChartFDVGenerator(self.sample_bar_chart)
        description = generator.generate_description()

        assert 'title' in description
        assert 'key_findings' in description
        assert 'data_points_count' in description

    def test_generate_description_line(self):
        """测试折线图描述生成"""
        generator = ChartFDVGenerator(self.sample_line_chart)
        description = generator.generate_description()

        assert 'title' in description
        assert 'key_findings' in description

    def test_assess_quality(self):
        """测试质量评估"""
        generator = ChartFDVGenerator(self.sample_scatter_chart)
        quality = generator.assess_quality()

        assert 'score' in quality
        assert 'metrics' in quality
        assert 'completeness' in quality['metrics']
        assert 'clarity' in quality['metrics']
        assert 'accuracy' in quality['metrics']
        assert isinstance(quality['score'], float)
        assert 0.0 <= quality['score'] <= 1.0

    def test_check_consistency(self):
        """测试一致性检查"""
        generator = ChartFDVGenerator(self.sample_scatter_chart)
        consistency = generator.check_consistency()

        assert 'overall_consistency' in consistency
        assert 'issues' in consistency
        assert isinstance(consistency['overall_consistency'], bool)

    def test_generate_description_with_missing_data(self):
        """测试缺失数据时的描述生成"""
        incomplete_chart = {
            'type': 'scatter',
            'title': '测试图表',
            'data_points': []
        }

        generator = ChartFDVGenerator(incomplete_chart)
        description = generator.generate_description()

        # 应该能处理缺失数据
        assert 'title' in description

    def test_generate_description_with_invalid_type(self):
        """测试无效图表类型时的描述生成"""
        invalid_chart = {
            'type': 'unknown_type',
            'title': '未知类型图表',
            'data_points': [{'x': 1, 'y': 2}]
        }

        generator = ChartFDVGenerator(invalid_chart)
        description = generator.generate_description()

        # 应该能处理未知类型
        assert 'title' in description


class TestChartUnderstandingIntegration:
    """图表理解模块集成测试"""

    def test_medical_chart_analysis(self):
        """测试医学图表分析"""
        medical_chart = {
            'type': 'scatter',
            'title': 'BMI与心血管风险的关系',
            'xlabel': 'BMI (kg/m²)',
            'ylabel': '10年心血管风险(%)',
            'data_points': [
                {'x': 18.5, 'y': 2.1},
                {'x': 22.0, 'y': 3.5},
                {'x': 25.0, 'y': 5.2},
                {'x': 28.0, 'y': 7.8},
                {'x': 32.0, 'y': 12.5},
                {'x': 35.0, 'y': 18.2},
            ],
            'correlation': 0.92,
            'p_value': 0.0001,
            'sample_size': 1000,
            'confidence_interval': [0.88, 0.96]
        }

        generator = ChartFDVGenerator(medical_chart)
        description = generator.generate_description()
        quality = generator.assess_quality()
        consistency = generator.check_consistency()

        # 验证所有结果都有效
        assert description['title'] == 'BMI与心血管风险的关系'
        assert quality['score'] > 0.0
        assert 'overall_consistency' in consistency

    def test_km_curve_analysis(self):
        """测试Kaplan-Meier曲线分析"""
        km_chart = {
            'type': 'km_curve',
            'title': '无进展生存期',
            'x_axis': {
                'label': '时间(月)',
                'unit': '月',
                'range_min': 0,
                'range_max': 24
            },
            'y_axis': {
                'label': '生存概率',
                'unit': '',
                'range_min': 0,
                'range_max': 1
            },
            'data_points': [
                {'x': 0, 'y': 1.0},
                {'x': 6, 'y': 0.85},
                {'x': 12, 'y': 0.72},
                {'x': 18, 'y': 0.65},
                {'x': 24, 'y': 0.58},
            ],
            'legends': ['治疗组', '对照组'],
            'statistical_info': {
                'p_value': 0.023,
                'hazard_ratio': 0.68,
                'confidence_interval': [0.49, 0.94],
                'survival_rates': {
                    '12个月': 0.72,
                    '24个月': 0.58
                }
            }
        }

        generator = ChartFDVGenerator(km_chart)
        description = generator.generate_description()

        assert '生存概率' in str(description)

    def test_forest_plot_analysis(self):
        """测试森林图分析"""
        forest_chart = {
            'type': 'forest_plot',
            'title': '亚组分析结果',
            'xlabel': '风险比(HR)',
            'subgroups': [
                {'name': '年龄<65', 'hr': 0.72, 'ci': [0.55, 0.94]},
                {'name': '年龄>65', 'hr': 0.85, 'ci': [0.62, 1.16]},
                {'name': '男性', 'hr': 0.68, 'ci': [0.51, 0.91]},
                {'name': '女性', 'hr': 0.89, 'ci': [0.65, 1.22]},
            ]
        }

        generator = ChartFDVGenerator(forest_chart)
        description = generator.generate_description()

        assert '亚组' in str(description)


class TestChartQualityAssessment:
    """图表质量评估测试"""

    def test_high_quality_chart(self):
        """测试高质量图表"""
        high_quality_chart = {
            'type': 'scatter',
            'title': '高质量散点图示例',
            'x_axis': {
                'label': '自变量(单位)',
                'unit': '单位',
                'range_min': 0,
                'range_max': 20
            },
            'y_axis': {
                'label': '因变量(单位)',
                'unit': '单位',
                'range_min': 5,
                'range_max': 45
            },
            'data_points': [
                {'x': i, 'y': i * 2 + 5} for i in range(20)
            ],
            'legends': ['数据系列1'],
            'annotations': ['趋势线', 'R²=0.98'],
            'statistical_info': {
                'sample_size': 20,
                'correlation': 0.98,
                'p_value': 0.0001
            }
        }

        generator = ChartFDVGenerator(high_quality_chart)
        quality = generator.assess_quality()

        assert quality['score'] > 0.5

    def test_low_quality_chart(self):
        """测试低质量图表"""
        low_quality_chart = {
            'type': 'scatter',
            'title': '',
            'x_axis': {},
            'y_axis': {},
            'data_points': []
        }

        generator = ChartFDVGenerator(low_quality_chart)
        quality = generator.assess_quality()

        assert quality['score'] < 0.7


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
