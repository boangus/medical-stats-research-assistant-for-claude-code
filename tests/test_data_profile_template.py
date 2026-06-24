"""
test_data_profile_template.py — 数据画像生成器测试
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.templates.data_profile_template import (
    generate_data_profile,
    get_checkpoint_level,
    _generate_missing_heatmap,
)


@pytest.fixture
def sample_df():
    """创建测试数据集"""
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'id': range(1, n + 1),
        'age': np.random.normal(50, 10, n),
        'gender': np.random.choice(['M', 'F'], n),
        'bp_systolic': np.random.normal(120, 15, n),
        'cholesterol': np.random.normal(200, 30, n),
        'smoking': np.random.choice([0, 1], n, p=[0.7, 0.3]),
        'outcome': np.random.choice([0, 1], n, p=[0.8, 0.2]),
        'visit_date': pd.date_range('2024-01-01', periods=n, freq='D'),
    })
    # 添加缺失值
    df.loc[0:5, 'cholesterol'] = np.nan
    df.loc[10:15, 'bp_systolic'] = np.nan
    return df


@pytest.fixture
def high_missing_df():
    """高缺失率数据集（应触发 MANDATORY checkpoint）"""
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'id': range(1, n + 1),
        'age': np.random.normal(50, 10, n),
        'mostly_missing': [np.nan] * 60 + list(range(40)),  # 60% 缺失
    })
    return df


@pytest.fixture
def small_df():
    """小样本数据集（应触发 MANDATORY checkpoint）"""
    return pd.DataFrame({
        'id': range(1, 6),
        'age': [25, 30, 35, 40, 45],
        'gender': ['M', 'F', 'M', 'F', 'M'],
    })


class TestGenerateDataProfile:
    """数据画像生成测试"""

    def test_returns_string(self, sample_df):
        md = generate_data_profile(sample_df, file_label='test')
        assert isinstance(md, str)

    def test_contains_title(self, sample_df):
        md = generate_data_profile(sample_df, file_label='my_data')
        assert '# 数据画像报告：my_data' in md

    def test_contains_data_scale(self, sample_df):
        md = generate_data_profile(sample_df)
        assert '## 1. 数据规模' in md
        assert '100' in md  # 行数
        assert '8' in md    # 列数

    def test_contains_type_distribution(self, sample_df):
        md = generate_data_profile(sample_df)
        assert '## 2. 变量类型分布' in md
        assert '连续变量' in md
        assert '分类变量' in md
        assert '日期变量' in md

    def test_contains_missing_info(self, sample_df):
        md = generate_data_profile(sample_df)
        assert '## 3. 缺失情况' in md
        assert 'Top 10 高缺失变量' in md
        assert 'cholesterol' in md
        assert 'bp_systolic' in md

    def test_contains_numeric_summary(self, sample_df):
        md = generate_data_profile(sample_df)
        assert '## 4. 数值变量概要' in md
        assert 'Min' in md
        assert 'Max' in md
        assert 'Mean' in md
        assert 'Median' in md
        assert 'SD' in md

    def test_contains_categorical_summary(self, sample_df):
        md = generate_data_profile(sample_df)
        assert '## 5. 分类变量概要' in md
        assert '层级数' in md
        assert '最大层级' in md

    def test_contains_time_span(self, sample_df):
        md = generate_data_profile(sample_df)
        assert '## 6. 时间跨度' in md
        assert 'visit_date' in md

    def test_no_missing_data(self):
        """无缺失值数据集"""
        df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': ['a', 'b', 'c', 'd', 'e'],
        })
        md = generate_data_profile(df)
        assert '✅ 无缺失值' in md
        assert 'Top 10' not in md


class TestAlertDetection:
    """极端情况告警测试"""

    def test_high_missing_alert(self, high_missing_df):
        md = generate_data_profile(high_missing_df)
        assert '🚨 极端情况告警' in md
        assert '缺失率 > 50%' in md
        assert 'mostly_missing' in md

    def test_small_sample_alert(self, small_df):
        md = generate_data_profile(small_df)
        assert '🚨 极端情况告警' in md
        assert '样本量仅 5 例' in md

    def test_no_alerts_normal_data(self, sample_df):
        md = generate_data_profile(sample_df)
        assert '🚨 极端情况告警' not in md


class TestCheckpointLevel:
    """Checkpoint 级别判定测试"""

    def test_slim_for_normal_data(self, sample_df):
        level = get_checkpoint_level(sample_df)
        assert level == "SLIM"

    def test_mandatory_for_high_missing(self, high_missing_df):
        level = get_checkpoint_level(high_missing_df)
        assert level == "MANDATORY"

    def test_mandatory_for_small_sample(self, small_df):
        level = get_checkpoint_level(small_df)
        assert level == "MANDATORY"

    def test_mandatory_for_few_columns(self):
        df = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
        level = get_checkpoint_level(df)
        assert level == "MANDATORY"


class TestMissingHeatmap:
    """缺失率热力图测试"""

    def test_heatmap_created(self, sample_df, tmp_path):
        output_dir = str(tmp_path)
        _generate_missing_heatmap(sample_df, output_dir)
        heatmap_path = os.path.join(output_dir, "missing_heatmap.png")
        assert os.path.exists(heatmap_path)

    def test_no_heatmap_when_no_missing(self, tmp_path):
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        output_dir = str(tmp_path)
        _generate_missing_heatmap(df, output_dir)
        heatmap_path = os.path.join(output_dir, "missing_heatmap.png")
        assert not os.path.exists(heatmap_path)


class TestEdgeCases:
    """边界情况测试"""

    def test_single_column(self):
        df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        md = generate_data_profile(df)
        assert '## 1. 数据规模' in md
        assert '10' in md

    def test_all_categorical(self):
        df = pd.DataFrame({
            'a': ['x', 'y', 'z'] * 10,
            'b': ['p', 'q', 'r'] * 10,
        })
        md = generate_data_profile(df)
        assert '分类变量' in md
        assert '连续变量' not in md

    def test_all_numeric(self):
        df = pd.DataFrame({
            'x': np.random.randn(50),
            'y': np.random.randn(50),
        })
        md = generate_data_profile(df)
        assert '连续变量' in md

    def test_empty_categorical(self):
        """分类变量为空时不应生成分类概要表"""
        df = pd.DataFrame({
            'x': np.random.randn(50),
            'y': np.random.randn(50),
        })
        md = generate_data_profile(df)
        assert '## 5. 分类变量概要' not in md
