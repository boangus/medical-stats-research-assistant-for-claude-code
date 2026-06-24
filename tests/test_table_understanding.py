"""
表格理解模块单元测试
==================

测试Chain-of-Table核查器、Tree-of-Table分析器、TableMaster提取器
"""

import sys
from pathlib import Path

import pytest

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.table_understanding import TableChainVerifier, TableMasterExtractor, TableTreeAnalyzer


class TestTableChainVerifier:
    """Chain-of-Table核查器测试"""

    def setup_method(self):
        """测试前准备"""
        self.sample_table = {
            'headers': ['变量', '组A', '组B', 'P值'],
            'rows': [
                ['年龄', '45.2±12.3', '46.1±11.8', '0.45'],
                ['性别(男)', '60(50%)', '55(45.8%)', '0.32'],
                ['BMI', '24.5±3.2', '25.1±3.5', '0.18'],
            ]
        }

    def test_verifier_initialization(self):
        """测试核查器初始化"""
        verifier = TableChainVerifier(self.sample_table)
        assert verifier.table_data == self.sample_table

    def test_verify_returns_result(self):
        """测试验证返回结果"""
        verifier = TableChainVerifier(self.sample_table)
        result = verifier.verify()

        assert 'score' in result
        assert 'steps' in result
        assert 'issues' in result
        assert 'suggestions' in result
        assert isinstance(result['score'], float)
        assert 0.0 <= result['score'] <= 1.0

    def test_verify_with_empty_table(self):
        """测试空表格验证"""
        empty_table = {'headers': [], 'rows': []}
        verifier = TableChainVerifier(empty_table)
        result = verifier.verify()

        assert result['score'] < 1.0
        assert len(result['issues']) > 0

    def test_verify_with_invalid_table(self):
        """测试无效表格验证"""
        invalid_table = {'headers': ['A', 'B'], 'rows': [['1']]}  # 行列数不匹配
        verifier = TableChainVerifier(invalid_table)
        result = verifier.verify()

        assert result['score'] < 1.0


class TestTableTreeAnalyzer:
    """Tree-of-Table分析器测试"""

    def setup_method(self):
        """测试前准备"""
        self.sample_table = {
            'headers': ['变量', '组A', '组B', 'P值'],
            'rows': [
                ['年龄', '45.2±12.3', '46.1±11.8', '0.45'],
                ['性别(男)', '60(50%)', '55(45.8%)', '0.32'],
                ['BMI', '24.5±3.2', '25.1±3.5', '0.18'],
            ]
        }

    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        analyzer = TableTreeAnalyzer(self.sample_table)
        assert analyzer.table_data == self.sample_table

    def test_build_tree(self):
        """测试构建树结构"""
        analyzer = TableTreeAnalyzer(self.sample_table)
        tree = analyzer.build_tree()

        assert tree is not None
        assert 'nodes' in tree
        assert 'root_id' in tree
        assert 'statistics' in tree

    def test_analyze_returns_result(self):
        """测试分析返回结果"""
        analyzer = TableTreeAnalyzer(self.sample_table)
        result = analyzer.analyze()

        assert 'hierarchy_analysis' in result
        assert 'data_distribution' in result
        assert 'pattern_recognition' in result
        assert 'complexity_metrics' in result


class TestTableMasterExtractor:
    """TableMaster提取器测试"""

    def setup_method(self):
        """测试前准备"""
        self.sample_table = {
            'headers': ['变量', '组A', '组B', 'P值'],
            'rows': [
                ['年龄', '45.2±12.3', '46.1±11.8', '0.45'],
                ['性别(男)', '60(50%)', '55(45.8%)', '0.32'],
                ['BMI', '24.5±3.2', '25.1±3.5', '0.18'],
            ]
        }

    def test_extractor_initialization(self):
        """测试提取器初始化"""
        extractor = TableMasterExtractor(self.sample_table)
        assert extractor.table_data == self.sample_table

    def test_extract_returns_result(self):
        """测试提取返回结果"""
        extractor = TableMasterExtractor(self.sample_table)
        result = extractor.extract()

        assert 'key_entities' in result
        assert 'relationships' in result
        assert 'statistics' in result
        assert 'patterns' in result

    def test_reason_with_query(self):
        """测试推理功能"""
        extractor = TableMasterExtractor(self.sample_table)
        result = extractor.reason("这个表格的主要发现是什么？")

        assert 'query' in result
        assert 'reasoning_mode' in result
        assert 'confidence' in result

    def test_get_semantic_description(self):
        """测试获取语义描述"""
        extractor = TableMasterExtractor(self.sample_table)
        description = extractor.get_semantic_description()

        assert isinstance(description, str)
        assert len(description) > 0


class TestTableUnderstandingIntegration:
    """表格理解模块集成测试"""

    def setup_method(self):
        """测试前准备"""
        self.sample_table = {
            'headers': ['变量', '组A', '组B', 'P值'],
            'rows': [
                ['年龄', '45.2±12.3', '46.1±11.8', '0.45'],
                ['性别(男)', '60(50%)', '55(45.8%)', '0.32'],
                ['BMI', '24.5±3.2', '25.1±3.5', '0.18'],
            ]
        }

    def test_full_pipeline(self):
        """测试完整流水线"""
        # 1. Chain-of-Table验证
        verifier = TableChainVerifier(self.sample_table)
        verification_result = verifier.verify()

        # 2. Tree-of-Table分析
        analyzer = TableTreeAnalyzer(self.sample_table)
        tree_result = analyzer.analyze()

        # 3. TableMaster提取
        extractor = TableMasterExtractor(self.sample_table)
        extraction_result = extractor.extract()

        # 验证所有结果都有效
        assert verification_result['score'] >= 0.0
        assert 'hierarchy_analysis' in tree_result
        assert 'key_entities' in extraction_result

    def test_medical_table_analysis(self):
        """测试医学表格分析"""
        medical_table = {
            'headers': ['指标', '治疗组', '对照组', '差异', '95% CI', 'P值'],
            'rows': [
                ['收缩压(mmHg)', '128.5±12.3', '135.2±13.1', '-6.7', '(-8.2, -5.2)', '<0.001'],
                ['舒张压(mmHg)', '82.1±8.5', '85.3±9.2', '-3.2', '(-4.5, -1.9)', '<0.001'],
                ['心率(次/分)', '72.3±10.2', '74.1±11.5', '-1.8', '(-3.1, -0.5)', '0.008'],
            ]
        }

        extractor = TableMasterExtractor(medical_table)
        result = extractor.extract()

        # 应该能识别出医学指标
        assert len(result['key_entities']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
