"""
Feature Selection - 影像组学特征选择

提供多种特征选择方法，支持无标签和有标签场景。
"""

import numpy as np
import pandas as pd
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class FeatureSelector:
    """影像组学特征选择器

    支持多种特征选择方法，包括方差阈值、K-best、互信息、
    递归特征消除和高相关性过滤。

    无标签时自动使用 variance_threshold + correlation_filter。
    有标签时可使用所有方法。

    Usage:
        selector = FeatureSelector()

        # 无标签场景
        selected_df = selector.select(features_df, labels=None, n_features=20)

        # 有标签场景
        selected_df = selector.select(features_df, labels=labels, method='auto', n_features=20)
    """

    def __init__(self):
        """初始化特征选择器"""
        self._selected_feature_names: List[str] = []

    def select(
        self,
        features_df: pd.DataFrame,
        labels: Optional[np.ndarray] = None,
        method: str = "auto",
        n_features: int = 20,
    ) -> pd.DataFrame:
        """执行特征选择

        Args:
            features_df: 特征 DataFrame（每行为一个样本，每列为一个特征）
            labels: 标签数组（可选，用于有监督方法）
            method: 选择方法 ('auto', 'variance', 'k_best', 'mutual_info',
                    'rfe', 'correlation')
            n_features: 期望保留的特征数

        Returns:
            筛选后的特征 DataFrame
        """
        if features_df.empty:
            logger.warning("Empty features DataFrame, returning as-is")
            return features_df

        if method == "auto":
            return self.auto_select(features_df, labels, n_features)
        elif method == "variance":
            return self.variance_threshold(features_df)
        elif method == "k_best":
            if labels is None:
                raise ValueError("k_best method requires labels")
            return self.k_best(features_df, labels, k=n_features)
        elif method == "mutual_info":
            if labels is None:
                raise ValueError("mutual_info method requires labels")
            return self.mutual_info(features_df, labels, k=n_features)
        elif method == "rfe":
            if labels is None:
                raise ValueError("rfe method requires labels")
            return self.rfe(features_df, labels, n_features=n_features)
        elif method == "correlation":
            return self.correlation_filter(features_df)
        else:
            raise ValueError(f"Unknown selection method: {method}")

    def variance_threshold(
        self,
        features_df: pd.DataFrame,
        threshold: float = 0.01,
    ) -> pd.DataFrame:
        """方差阈值过滤

        移除方差低于阈值的特征（即几乎不变的特征）。

        Args:
            features_df: 特征 DataFrame
            threshold: 方差阈值

        Returns:
            过滤后的特征 DataFrame
        """
        from sklearn.feature_selection import VarianceThreshold

        # 处理 NaN：用 0 填充
        df_clean = features_df.fillna(0)

        # 只选择数值列
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            logger.warning("No numeric columns found")
            return features_df

        selector = VarianceThreshold(threshold=threshold)

        try:
            selected = selector.fit_transform(df_clean[numeric_cols])
            mask = selector.get_support()
            selected_cols = [c for c, m in zip(numeric_cols, mask) if m]

            result = pd.DataFrame(selected, columns=selected_cols, index=features_df.index)

            dropped = len(numeric_cols) - len(selected_cols)
            logger.info(
                f"Variance threshold ({threshold}): "
                f"dropped {dropped} features, kept {len(selected_cols)}"
            )

            self._selected_feature_names = selected_cols
            return result

        except Exception as e:
            logger.error(f"Variance threshold failed: {e}")
            return features_df

    def k_best(
        self,
        features_df: pd.DataFrame,
        labels: np.ndarray,
        k: int = 20,
    ) -> pd.DataFrame:
        """K-best 特征选择

        使用 F-test 选择 k 个最佳特征。

        Args:
            features_df: 特征 DataFrame
            labels: 标签数组
            k: 选择的特征数

        Returns:
            筛选后的特征 DataFrame
        """
        from sklearn.feature_selection import SelectKBest, f_classif

        df_clean = features_df.fillna(0)
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()

        k_actual = min(k, len(numeric_cols))
        if k_actual <= 0:
            return features_df

        selector = SelectKBest(f_classif, k=k_actual)

        try:
            selected = selector.fit_transform(df_clean[numeric_cols], labels)
            mask = selector.get_support()
            selected_cols = [c for c, m in zip(numeric_cols, mask) if m]

            result = pd.DataFrame(selected, columns=selected_cols, index=features_df.index)

            logger.info(f"K-best: selected {len(selected_cols)} features from {len(numeric_cols)}")
            self._selected_feature_names = selected_cols
            return result

        except Exception as e:
            logger.error(f"K-best selection failed: {e}")
            return features_df

    def mutual_info(
        self,
        features_df: pd.DataFrame,
        labels: np.ndarray,
        k: int = 20,
    ) -> pd.DataFrame:
        """互信息特征选择

        使用互信息选择 k 个最佳特征。

        Args:
            features_df: 特征 DataFrame
            labels: 标签数组
            k: 选择的特征数

        Returns:
            筛选后的特征 DataFrame
        """
        from sklearn.feature_selection import SelectKBest, mutual_info_classif

        df_clean = features_df.fillna(0)
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()

        k_actual = min(k, len(numeric_cols))
        if k_actual <= 0:
            return features_df

        selector = SelectKBest(mutual_info_classif, k=k_actual)

        try:
            selected = selector.fit_transform(df_clean[numeric_cols], labels)
            mask = selector.get_support()
            selected_cols = [c for c, m in zip(numeric_cols, mask) if m]

            result = pd.DataFrame(selected, columns=selected_cols, index=features_df.index)

            logger.info(
                f"Mutual info: selected {len(selected_cols)} features from {len(numeric_cols)}"
            )
            self._selected_feature_names = selected_cols
            return result

        except Exception as e:
            logger.error(f"Mutual info selection failed: {e}")
            return features_df

    def rfe(
        self,
        features_df: pd.DataFrame,
        labels: np.ndarray,
        n_features: int = 20,
    ) -> pd.DataFrame:
        """递归特征消除

        使用 RFE (Recursive Feature Elimination) 选择特征。

        Args:
            features_df: 特征 DataFrame
            labels: 标签数组
            n_features: 期望保留的特征数

        Returns:
            筛选后的特征 DataFrame
        """
        from sklearn.feature_selection import RFE
        from sklearn.ensemble import RandomForestClassifier

        df_clean = features_df.fillna(0)
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()

        n_actual = min(n_features, len(numeric_cols))
        if n_actual <= 0:
            return features_df

        estimator = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
        selector = RFE(estimator, n_features_to_select=n_actual, step=max(1, len(numeric_cols) // 10))

        try:
            selected = selector.fit_transform(df_clean[numeric_cols], labels)
            mask = selector.get_support()
            selected_cols = [c for c, m in zip(numeric_cols, mask) if m]

            result = pd.DataFrame(selected, columns=selected_cols, index=features_df.index)

            logger.info(f"RFE: selected {len(selected_cols)} features from {len(numeric_cols)}")
            self._selected_feature_names = selected_cols
            return result

        except Exception as e:
            logger.error(f"RFE selection failed: {e}")
            return features_df

    def correlation_filter(
        self,
        features_df: pd.DataFrame,
        threshold: float = 0.95,
    ) -> pd.DataFrame:
        """高相关性过滤

        移除高度相关的特征（保留每对相关特征中的一个）。

        Args:
            features_df: 特征 DataFrame
            threshold: 相关系数阈值

        Returns:
            过滤后的特征 DataFrame
        """
        df_clean = features_df.fillna(0)
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) <= 1:
            self._selected_feature_names = numeric_cols
            return features_df[numeric_cols]

        try:
            corr_matrix = df_clean[numeric_cols].corr().abs()

            # 上三角矩阵
            upper = corr_matrix.where(
                np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
            )

            # 找到高相关的列
            to_drop: List[str] = []
            for col in upper.columns:
                if col in to_drop:
                    continue
                high_corr = upper.index[upper[col] > threshold].tolist()
                to_drop.extend(high_corr)

            to_drop = list(set(to_drop))
            selected_cols = [c for c in numeric_cols if c not in to_drop]

            result = df_clean[selected_cols]

            logger.info(
                f"Correlation filter ({threshold}): "
                f"dropped {len(to_drop)} features, kept {len(selected_cols)}"
            )

            self._selected_feature_names = selected_cols
            return result

        except Exception as e:
            logger.error(f"Correlation filter failed: {e}")
            return features_df

    def auto_select(
        self,
        features_df: pd.DataFrame,
        labels: Optional[np.ndarray] = None,
        n_features: int = 20,
    ) -> pd.DataFrame:
        """自动选择管线

        无标签时串联: variance_threshold → correlation_filter
        有标签时串联: variance_threshold → correlation_filter → k_best/mutual_info

        Args:
            features_df: 特征 DataFrame
            labels: 标签数组（可选）
            n_features: 期望保留的特征数

        Returns:
            筛选后的特征 DataFrame
        """
        logger.info("Starting auto feature selection pipeline...")

        # Step 1: 方差阈值过滤
        result = self.variance_threshold(features_df, threshold=0.01)
        logger.info(f"After variance threshold: {result.shape[1]} features")

        # Step 2: 高相关性过滤
        result = self.correlation_filter(result, threshold=0.95)
        logger.info(f"After correlation filter: {result.shape[1]} features")

        # Step 3: 有标签时使用有监督方法
        if labels is not None and result.shape[1] > n_features:
            try:
                # 尝试互信息
                result = self.mutual_info(result, labels, k=n_features)
                logger.info(f"After mutual info: {result.shape[1]} features")
            except Exception:
                try:
                    # 降级到 K-best
                    result = self.k_best(result, labels, k=n_features)
                    logger.info(f"After k-best: {result.shape[1]} features")
                except Exception:
                    logger.warning("Supervised selection failed, using unsupervised result")
        elif labels is None:
            # 无标签时，如果特征数仍过多，使用相关性过滤
            if result.shape[1] > n_features:
                # 选择方差最大的 n_features 个特征
                variances = result.var()
                top_features = variances.nlargest(n_features).index.tolist()
                result = result[top_features]
                logger.info(f"After variance ranking: {result.shape[1]} features")

        self._selected_feature_names = result.columns.tolist()
        logger.info(f"Auto selection complete: {result.shape[1]} features selected")
        return result

    def get_selected_feature_names(self) -> List[str]:
        """获取最近一次选择的特征名列表

        Returns:
            选中的特征名列表
        """
        return self._selected_feature_names.copy()
