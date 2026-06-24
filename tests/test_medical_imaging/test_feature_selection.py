"""
Feature Selection Tests - 特征选择测试

测试 FeatureSelector 的各种特征选择方法。
"""

import numpy as np
import pandas as pd
import pytest


class TestFeatureSelector:
    """FeatureSelector 测试"""

    def setup_method(self):
        """每个测试前创建测试数据"""
        from msra_modules.medical_imaging.feature_selection import FeatureSelector
        self.selector = FeatureSelector()

        # 创建合成特征矩阵：50 样本 × 30 特征
        np.random.seed(42)
        self.n_samples = 50
        self.n_features = 30

        data = np.random.rand(self.n_samples, self.n_features)
        self.features_df = pd.DataFrame(
            data,
            columns=[f"feature_{i}" for i in range(self.n_features)],
        )

        # 二分类标签
        self.labels = np.array([0] * 25 + [1] * 25)

        # 添加一个常量特征（方差=0）
        self.features_df["constant_feature"] = 1.0

        # 添加一对高度相关的特征
        self.features_df["corr_a"] = self.features_df["feature_0"] * 1.001
        self.features_df["corr_b"] = self.features_df["feature_0"] * 0.999

    def test_variance_threshold(self):
        """测试方差阈值过滤"""
        result = self.selector.variance_threshold(self.features_df, threshold=0.01)

        # 常量特征应该被移除
        assert "constant_feature" not in result.columns
        # 其他特征应保留
        assert result.shape[1] > 0
        assert result.shape[0] == self.n_samples

    def test_variance_threshold_custom(self):
        """测试自定义阈值的方差过滤"""
        # 高阈值会过滤更多特征
        result_low = self.selector.variance_threshold(self.features_df, threshold=0.01)
        result_high = self.selector.variance_threshold(self.features_df, threshold=0.1)
        assert result_high.shape[1] <= result_low.shape[1]

    def test_correlation_filter(self):
        """测试高相关性过滤"""
        result = self.selector.correlation_filter(self.features_df, threshold=0.95)

        # 高度相关的特征对应该减少
        assert result.shape[1] <= self.features_df.shape[1]

        # 检查剩余特征间的相关性
        if result.shape[1] > 1:
            corr = result.corr().abs()
            # 上三角中不应有超过阈值的相关系数
            upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
            max_corr = upper.max().max()
            # 允许一些数值误差
            assert max_corr <= 0.96 or pd.isna(max_corr)

    def test_k_best_with_labels(self):
        """测试 K-best 特征选择（有标签）"""
        result = self.selector.k_best(self.features_df, self.labels, k=10)

        assert result.shape[1] == 10
        assert result.shape[0] == self.n_samples

    def test_k_best_more_than_available(self):
        """测试 k 大于特征数时的行为"""
        small_df = self.features_df.iloc[:, :5]
        result = self.selector.k_best(small_df, self.labels, k=20)

        # 应该返回所有 5 个特征（min(k, n_features)）
        assert result.shape[1] == 5

    def test_mutual_info_with_labels(self):
        """测试互信息特征选择（有标签）"""
        result = self.selector.mutual_info(self.features_df, self.labels, k=10)

        assert result.shape[1] <= 10
        assert result.shape[0] == self.n_samples

    def test_rfe_with_labels(self):
        """测试递归特征消除（有标签）"""
        result = self.selector.rfe(self.features_df, self.labels, n_features=10)

        assert result.shape[1] == 10
        assert result.shape[0] == self.n_samples

    def test_auto_select_no_labels(self):
        """测试自动选择（无标签场景）"""
        result = self.selector.auto_select(
            self.features_df, labels=None, n_features=15
        )

        assert result.shape[1] <= 15
        assert result.shape[0] == self.n_samples

    def test_auto_select_with_labels(self):
        """测试自动选择（有标签场景）"""
        result = self.selector.auto_select(
            self.features_df, labels=self.labels, n_features=15
        )

        assert result.shape[1] <= 15
        assert result.shape[0] == self.n_samples

    def test_select_method_dispatch(self):
        """测试 select 方法的分发逻辑"""
        # variance 方法
        result = self.selector.select(self.features_df, method="variance")
        assert result.shape[1] > 0

        # correlation 方法
        result = self.selector.select(self.features_df, method="correlation")
        assert result.shape[1] > 0

    def test_select_invalid_method(self):
        """测试无效选择方法"""
        with pytest.raises(ValueError, match="Unknown selection method"):
            self.selector.select(self.features_df, method="invalid_method")

    def test_select_k_best_no_labels_error(self):
        """测试 k_best 无标签时抛出错误"""
        with pytest.raises(ValueError, match="requires labels"):
            self.selector.select(self.features_df, labels=None, method="k_best")

    def test_select_empty_dataframe(self):
        """测试空 DataFrame"""
        empty_df = pd.DataFrame()
        result = self.selector.select(empty_df)
        assert result.empty

    def test_get_selected_feature_names(self):
        """测试获取选中特征名"""
        self.selector.variance_threshold(self.features_df)
        names = self.selector.get_selected_feature_names()

        assert isinstance(names, list)
        assert len(names) > 0
        assert "constant_feature" not in names
