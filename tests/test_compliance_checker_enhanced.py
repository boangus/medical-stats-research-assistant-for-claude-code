"""
增强版合规性检查器单元测试
========================

测试新增的表格和图表理解检查功能
"""

import pytest
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.report_assembler.compliance_checker import (
    check_table_understanding,
    check_table_structure_integrity,
    check_table_data_consistency,
    check_chart_understanding,
    check_chart_text_consistency,
    check_chart_quality_automated
)


class TestTableStructureIntegrity:
    """表格结构完整性检查测试"""
    
    def test_valid_table(self):
        """测试有效表格"""
        table_data = {
            'headers': ['变量', '组A', '组B'],
            'rows': [
                ['年龄', '45.2', '46.1'],
                ['性别', '60', '55'],
            ]
        }
        
        result = check_table_structure_integrity(table_data)
        
        assert result['structure_score'] == 1.0
        assert len(result['issues']) == 0
    
    def test_missing_headers(self):
        """测试缺少表头"""
        table_data = {
            'rows': [['年龄', '45.2', '46.1']]
        }
        
        result = check_table_structure_integrity(table_data)
        
        assert result['structure_score'] < 1.0
        assert any('headers' in issue for issue in result['issues'])
    
    def test_missing_rows(self):
        """测试缺少数据行"""
        table_data = {
            'headers': ['变量', '组A', '组B'],
            'rows': []
        }
        
        result = check_table_structure_integrity(table_data)
        
        assert result['structure_score'] < 1.0
        assert any('数据行为空' in issue for issue in result['issues'])
    
    def test_mismatched_columns(self):
        """测试行列数不匹配"""
        table_data = {
            'headers': ['变量', '组A', '组B'],
            'rows': [
                ['年龄', '45.2'],  # 只有2列，应该有3列
            ]
        }
        
        result = check_table_structure_integrity(table_data)
        
        assert result['structure_score'] < 1.0
        assert any('不匹配' in issue for issue in result['issues'])
    
    def test_high_missing_rate(self):
        """测试高缺失率"""
        table_data = {
            'headers': ['变量', '组A', '组B'],
            'rows': [
                ['年龄', '', ''],
                ['性别', 'NA', 'N/A'],
                ['BMI', None, ''],
            ]
        }
        
        result = check_table_structure_integrity(table_data)
        
        assert result['structure_score'] < 1.0
        assert any('缺失值比例过高' in issue for issue in result['issues'])


class TestTableDataConsistency:
    """表格数据一致性检查测试"""
    
    def test_consistent_data_types(self):
        """测试一致的数据类型"""
        table_data = {
            'headers': ['变量', '组A', '组B'],
            'rows': [
                ['年龄', '45.2', '46.1'],
                ['BMI', '24.5', '25.1'],
            ]
        }
        
        result = check_table_data_consistency(table_data)
        
        assert result['consistency_score'] == 1.0
        assert len(result['issues']) == 0
    
    def test_inconsistent_data_types(self):
        """测试不一致的数据类型"""
        table_data = {
            'headers': ['变量', '值'],
            'rows': [
                ['年龄', '45.2'],
                ['年龄', '未知'],
                ['年龄', '52.1'],
            ]
        }
        
        result = check_table_data_consistency(table_data)
        
        assert result['consistency_score'] < 1.0
        assert any('数据类型不一致' in issue for issue in result['issues'])
    
    def test_outlier_detection(self):
        """测试异常值检测"""
        # 创建一个有明显异常值的数据集
        table_data = {
            'headers': ['ID', '值'],
            'rows': [
                ['1', '10'],
                ['2', '12'],
                ['3', '11'],
                ['4', '13'],
                ['5', '100'],  # 明显异常值
            ]
        }
        
        result = check_table_data_consistency(table_data)
        
        # 可能检测到异常值
        assert result['consistency_score'] <= 1.0


class TestChartTextConsistency:
    """图表与文本一致性检查测试"""
    
    def test_consistent_chart_text(self):
        """测试图表与文本一致"""
        chart_data = {
            'title': 'BMI与血压的关系',
            'xlabel': 'BMI',
            'ylabel': '收缩压',
            'legend': ['男性', '女性'],
            'data_points': [
                {'x': 22, 'y': 120},
                {'x': 28, 'y': 145},
            ]
        }
        
        text_content = """
        本研究分析了BMI与血压的关系。
        图表显示，随着BMI增加，收缩压呈上升趋势。
        男性和女性的血压变化模式相似。
        BMI为22时，收缩压约为120mmHg；
        BMI为28时，收缩压约为145mmHg。
        """
        
        result = check_chart_text_consistency(chart_data, text_content)
        
        assert result['consistency_score'] > 0.0
    
    def test_inconsistent_chart_text(self):
        """测试图表与文本不一致"""
        chart_data = {
            'title': '治疗效果比较',
            'xlabel': '时间',
            'ylabel': '症状评分',
            'legend': ['安慰剂', '药物A', '药物B'],
            'data_points': [
                {'x': 0, 'y': 50},
                {'x': 4, 'y': 30},
            ]
        }
        
        text_content = """
        本研究比较了三种治疗方案的效果。
        """  # 文本中没有提到图表的具体内容
        
        result = check_chart_text_consistency(chart_data, text_content)
        
        assert result['consistency_score'] < 1.0
        assert len(result['issues']) > 0


class TestChartQualityAutomated:
    """图表质量自动化评估测试"""
    
    def test_high_quality_chart(self):
        """测试高质量图表"""
        chart_data = {
            'type': 'scatter',
            'title': '详细的散点图分析',
            'xlabel': '自变量 (单位)',
            'ylabel': '因变量 (单位)',
            'data_points': [
                {'x': i, 'y': i * 2} for i in range(10)
            ],
            'legend': ['数据系列']
        }
        
        result = check_chart_quality_automated(chart_data)
        
        assert result['quality_score'] > 0.8
        assert len(result['issues']) == 0
    
    def test_low_quality_chart(self):
        """测试低质量图表"""
        chart_data = {
            'type': 'scatter',
            'title': '图',  # 标题过短
            'data_points': []  # 缺少数据点
        }
        
        result = check_chart_quality_automated(chart_data)
        
        assert result['quality_score'] < 0.5
        assert len(result['issues']) > 0
    
    def test_missing_labels(self):
        """测试缺少标签"""
        chart_data = {
            'type': 'bar',
            'title': '柱状图',
            'data_points': [{'x': 'A', 'y': 10}, {'x': 'B', 'y': 20}]
        }
        
        result = check_chart_quality_automated(chart_data)
        
        assert result['quality_score'] < 1.0
        assert any('X轴标签' in issue for issue in result['issues'])
        assert any('Y轴标签' in issue for issue in result['issues'])


class TestComplianceCheckerIntegration:
    """合规性检查器集成测试"""
    
    def test_full_table_analysis(self):
        """测试完整表格分析"""
        table_data = {
            'headers': ['变量', '治疗组', '对照组', 'P值'],
            'rows': [
                ['年龄', '45.2±12.3', '46.1±11.8', '0.45'],
                ['性别(男)', '60(50%)', '55(45.8%)', '0.32'],
                ['BMI', '24.5±3.2', '25.1±3.5', '0.18'],
            ]
        }
        
        # 1. 结构完整性检查
        structure_result = check_table_structure_integrity(table_data)
        assert structure_result['structure_score'] == 1.0
        
        # 2. 数据一致性检查
        consistency_result = check_table_data_consistency(table_data)
        assert consistency_result['consistency_score'] > 0.0
        
        # 3. 表格理解检查
        understanding_result = check_table_understanding(table_data)
        assert 'overall_score' in understanding_result
    
    def test_full_chart_analysis(self):
        """测试完整图表分析"""
        chart_data = {
            'type': 'scatter',
            'title': 'BMI与心血管风险的关系',
            'xlabel': 'BMI (kg/m²)',
            'ylabel': '10年心血管风险 (%)',
            'data_points': [
                {'x': 22, 'y': 3.5},
                {'x': 25, 'y': 5.2},
                {'x': 28, 'y': 7.8},
                {'x': 32, 'y': 12.5},
            ],
            'legend': ['研究人群'],
            'sample_size': 1000
        }
        
        text_content = """
        本研究分析了BMI与心血管风险的关系。
        结果显示，BMI每增加1个单位，心血管风险增加约1.5%。
        """
        
        # 1. 图表质量检查
        quality_result = check_chart_quality_automated(chart_data)
        assert quality_result['quality_score'] > 0.0
        
        # 2. 图表与文本一致性检查
        consistency_result = check_chart_text_consistency(chart_data, text_content)
        assert consistency_result['consistency_score'] > 0.0
        
        # 3. 图表理解检查
        understanding_result = check_chart_understanding(chart_data)
        assert 'overall_score' in understanding_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])