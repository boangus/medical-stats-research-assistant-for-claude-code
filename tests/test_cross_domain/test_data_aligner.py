"""Unit tests for DataAligner.

Tests: inner join, outer join + fill, time_based align,
insufficient samples exception, strategy validation.
"""

import numpy as np
import pandas as pd
import pytest

from msra_modules.cross_domain import DataAligner


class TestDataAligner:
    """DataAligner unit tests."""

    def test_inner_join(self, mock_radiomics_features, mock_expression_data):
        """Test 1: inner join — 取交集，所有 DataFrame 相同 index"""
        aligner = DataAligner(strategy="inner")
        aligned = aligner.align({
            "radiomics": mock_radiomics_features,
            "expression": mock_expression_data,
        })

        # 两个数据源 index 应完全一致
        assert list(aligned["radiomics"].index) == list(aligned["expression"].index)
        # 样本数 = 交集 (两个都是 10 个相同样本 → 10)
        assert len(aligned["radiomics"]) == 10
        assert len(aligned["expression"]) == 10

    def test_outer_join_with_fill(self):
        """Test 2: outer join — 取并集 + 缺失值填充"""
        np.random.seed(42)
        df1 = pd.DataFrame(
            {"a": [1.0, 2.0, 3.0]},
            index=["S1", "S2", "S3"],
        )
        df2 = pd.DataFrame(
            {"b": [4.0, 5.0, 6.0]},
            index=["S2", "S3", "S4"],
        )

        aligner = DataAligner(strategy="outer", fill_method="mean")
        aligned = aligner.align({"df1": df1, "df2": df2})

        # 并集 = S1, S2, S3, S4
        assert len(aligned["df1"]) == 4
        assert len(aligned["df2"]) == 4
        # S4 在 df1 中缺失 → 用 mean 填充
        assert not aligned["df1"].loc["S4", "a"] != aligned["df1"].loc["S4", "a"]  # not NaN
        # S1 在 df2 中缺失 → 用 mean 填充
        assert not aligned["df2"].loc["S1", "b"] != aligned["df2"].loc["S1", "b"]  # not NaN

    def test_time_based_align(self, mock_realtime_data):
        """Test 3: time_based align — 时序数据按时间窗对齐"""
        aligner = DataAligner(strategy="time_based")
        aligned = aligner.align({"realtime": mock_realtime_data})

        # Dict 类型对齐后仍为 Dict
        assert isinstance(aligned["realtime"], dict)
        # 每个指标的值列表应非空
        for metric, values in aligned["realtime"].items():
            assert isinstance(values, list)
            assert len(values) > 0

    def test_inner_join_insufficient_samples(self):
        """Test 4: inner join 样本不足时抛出 ValueError"""
        df1 = pd.DataFrame(
            {"a": [1.0, 2.0]},
            index=["S1", "S2"],
        )
        df2 = pd.DataFrame(
            {"b": [3.0]},
            index=["S1"],
        )

        aligner = DataAligner(strategy="inner")
        # 交集 = {S1} → 1 样本 < 3
        with pytest.raises(ValueError, match="Inner join 后样本数"):
            aligner.align({"df1": df1, "df2": df2})

    def test_invalid_strategy(self):
        """Test 5: 无效策略抛出 ValueError"""
        with pytest.raises(ValueError, match="Invalid strategy"):
            DataAligner(strategy="invalid")

    def test_invalid_fill_method(self):
        """Test 6: 无效填充方法抛出 ValueError"""
        with pytest.raises(ValueError, match="Invalid fill_method"):
            DataAligner(fill_method="invalid")

    def test_fill_missing_methods(self):
        """Test 7: 各种缺失值填充方法"""
        df = pd.DataFrame(
            {"a": [1.0, np.nan, 3.0, np.nan]},
            index=["S1", "S2", "S3", "S4"],
        )
        aligner = DataAligner(strategy="outer")

        # mean
        filled_mean = aligner._fill_missing(df.copy(), "mean")
        expected_mean = df["a"].mean()
        assert filled_mean.loc["S2", "a"] == pytest.approx(expected_mean)

        # median
        filled_median = aligner._fill_missing(df.copy(), "median")
        expected_median = df["a"].median()
        assert filled_median.loc["S2", "a"] == pytest.approx(expected_median)

        # zero
        filled_zero = aligner._fill_missing(df.copy(), "zero")
        assert filled_zero.loc["S2", "a"] == 0

    def test_get_common_samples(self, mock_radiomics_features, mock_expression_data):
        """Test 8: _get_common_samples — 获取公共样本 ID"""
        aligner = DataAligner(strategy="inner")
        common = aligner._get_common_samples({
            "radiomics": mock_radiomics_features,
            "expression": mock_expression_data,
        })

        assert isinstance(common, list)
        assert len(common) == 10  # 两个完全重叠
        assert common == sorted(common)  # 应排序
