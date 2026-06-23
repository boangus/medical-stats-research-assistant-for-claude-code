#!/usr/bin/env python3
"""
SAP一致性检查器测试

测试SAP预设方法与数据特征的一致性检查功能。
"""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.sap.sap_consistency_check import SAPConsistencyCheck


class TestSAPConsistencyCheck:
    """SAP一致性检查器测试类"""

    def setup_method(self):
        """测试前准备"""
        # 创建测试数据
        np.random.seed(42)
        self.data = pd.DataFrame({
            'treatment': np.random.choice([0, 1], size=100),
            'outcome_normal': np.random.normal(50, 10, 100),
            'outcome_skewed': np.random.exponential(10, 100),
            'age': np.random.normal(60, 10, 100),
            'bmi': np.random.normal(25, 5, 100),
            'gender': np.random.choice([0, 1], size=100)
        })

        # SAP配置
        self.sap_config = {
            "study_type": "RCT",
            "main_analysis": "ANCOVA",
            "normality_test": "shapiro-wilk",
            "homogeneity_test": "levene",
            "equal_var": True,
            "covariates": ["age", "bmi", "gender"]
        }

    def test_check_normality_normal_data(self):
        """测试正态性检查（正态数据）"""
        checker = SAPConsistencyCheck(self.sap_config)

        # 检查正态分布数据
        result = checker.check_normality(self.data, 'outcome_normal')

        assert result['check_type'] == 'normality'
        assert result['variable'] == 'outcome_normal'
        assert 'overall' in result['data_characteristics']
        assert result['data_characteristics']['overall']['normal'] == True

    def test_check_normality_skewed_data(self):
        """测试正态性检查（偏态数据）"""
        checker = SAPConsistencyCheck(self.sap_config)

        # 检查偏态数据
        result = checker.check_normality(self.data, 'outcome_skewed')

        assert result['check_type'] == 'normality'
        assert result['variable'] == 'outcome_skewed'
        assert 'overall' in result['data_characteristics']
        # 偏态数据应该不满足正态性
        assert result['data_characteristics']['overall']['normal'] == False

    def test_check_normality_with_groups(self):
        """测试分组正态性检查"""
        checker = SAPConsistencyCheck(self.sap_config)

        # 按组检查正态性
        result = checker.check_normality(self.data, 'outcome_normal', 'treatment')

        assert result['check_type'] == 'normality'
        assert 'group_0' in result['data_characteristics']
        assert 'group_1' in result['data_characteristics']

    def test_check_homogeneity(self):
        """测试方差齐性检查"""
        checker = SAPConsistencyCheck(self.sap_config)

        # 检查方差齐性
        result = checker.check_homogeneity(self.data, 'outcome_normal', 'treatment')

        assert result['check_type'] == 'homogeneity'
        assert result['group_variable'] == 'treatment'
        assert 'levene_stat' in result['data_characteristics']
        assert 'p_value' in result['data_characteristics']
        assert 'homogeneous' in result['data_characteristics']

    def test_check_multicollinearity(self):
        """测试多重共线性检查"""
        checker = SAPConsistencyCheck(self.sap_config)

        # 检查多重共线性
        predictors = ['age', 'bmi', 'gender']
        result = checker.check_multicollinearity(self.data, 'outcome_normal', predictors)

        assert result['check_type'] == 'multicollinearity'
        assert result['outcome'] == 'outcome_normal'
        assert result['predictors'] == predictors

    def test_consistency_report_generation(self):
        """测试一致性报告生成"""
        checker = SAPConsistencyCheck(self.sap_config)

        # 执行多项检查
        normality_result = checker.check_normality(self.data, 'outcome_normal')
        homogeneity_result = checker.check_homogeneity(self.data, 'outcome_normal', 'treatment')

        # 获取一致性报告
        report = checker.generate_consistency_report()

        assert 'summary' in report
        assert 'details' in report
        assert report['summary']['overall_consistent'] == True

    def test_mismatch_detection(self):
        """测试不匹配检测"""
        # 配置SAP使用非参数方法，但数据满足正态性
        sap_config_nonparametric = {
            "main_analysis": "Mann-Whitney U",
            "normality_test": "shapiro-wilk"
        }

        checker = SAPConsistencyCheck(sap_config_nonparametric)

        # 检查正态数据
        result = checker.check_normality(self.data, 'outcome_normal')

        # 数据满足正态性，但SAP预设非参数方法，应该检测到不匹配
        assert result['consistency'] == False
        assert '参数检验' in result['alternative_method']

    def test_alternative_method_suggestion(self):
        """测试替代方法建议"""
        # 配置SAP使用参数方法，但数据不满足正态性
        sap_config_parametric = {
            "main_analysis": "t-test",
            "normality_test": "shapiro-wilk"
        }

        checker = SAPConsistencyCheck(sap_config_parametric)

        # 检查偏态数据
        result = checker.check_normality(self.data, 'outcome_skewed')

        # 数据不满足正态性，应该建议非参数方法
        assert result['consistency'] == False
        assert '非参数' in result['alternative_method']

    def test_code_suggestion_generation(self):
        """测试代码建议生成"""
        checker = SAPConsistencyCheck(self.sap_config)

        # 检查不满足方差齐性的数据
        result = checker.check_homogeneity(self.data, 'outcome_normal', 'treatment')

        # 如果有不匹配，应该生成代码建议
        if not result['consistency']:
            assert result['code_suggestion'] != ''


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
