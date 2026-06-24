"""
Cross-domain Integration - 三领域交叉集成

CROSS-001: Radiomics-DEG关联分析
CROSS-002: 实时预警模型
CROSS-003: 多模态数据联合可视化
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class RadiomicsDEGCorrelation:
    """影像组学与差异表达基因关联分析"""

    def __init__(self,
                 correlation_method: str = "spearman",
                 pval_threshold: float = 0.05,
                 fdr_method: str = "bh"):
        """初始化

        Args:
            correlation_method: 相关系数方法 ("pearson", "spearman", "kendall")
            pval_threshold: p值阈值
            fdr_method: FDR校正方法 ("bh", "bonferroni")
        """
        self.correlation_method = correlation_method
        self.pval_threshold = pval_threshold
        self.fdr_method = fdr_method

    def correlate(self,
                  radiomics_features: pd.DataFrame,
                  deg_expression: pd.DataFrame) -> Dict:
        """计算关联

        Args:
            radiomics_features: 影像组学特征 (样本×特征)
            deg_expression: 差异基因表达 (样本×基因)

        Returns:
            关联结果字典
        """
        from scipy import stats

        # 确保样本对齐
        common_samples = list(
            set(radiomics_features.index) & set(deg_expression.index)
        )

        if len(common_samples) < 3:
            raise ValueError(
                f"Insufficient common samples: {len(common_samples)} (need >= 3)"
            )

        radiomics = radiomics_features.loc[common_samples]
        expression = deg_expression.loc[common_samples]

        # 计算相关性
        correlations = []
        p_values = []

        for feat_col in radiomics.columns:
            feat_values = radiomics[feat_col].values

            for gene_col in expression.columns:
                gene_values = expression[gene_col].values

                if self.correlation_method == "pearson":
                    r, p = stats.pearsonr(feat_values, gene_values)
                elif self.correlation_method == "spearman":
                    r, p = stats.spearmanr(feat_values, gene_values)
                elif self.correlation_method == "kendall":
                    r, p = stats.kendalltau(feat_values, gene_values)
                else:
                    raise ValueError(f"Unknown method: {self.correlation_method}")

                correlations.append({
                    "feature": feat_col,
                    "gene": gene_col,
                    "correlation": r,
                    "p_value": p
                })

        # 创建DataFrame
        results = pd.DataFrame(correlations)

        # FDR校正
        results["p_adj"] = self._fdr_correction(results["p_value"].values)

        # 标记显著
        results["significant"] = (
            (results["p_adj"] < self.pval_threshold) &
            (results["correlation"].abs() >= 0.3)
        )

        # 排序
        results = results.sort_values("p_adj")

        logger.info(f"Found {results['significant'].sum()} significant correlations")

        return {
            "correlations": results,
            "n_significant": int(results["significant"].sum()),
            "n_total": len(results),
            "method": self.correlation_method,
            "samples": len(common_samples),
        }

    def _fdr_correction(self, p_values: np.ndarray) -> np.ndarray:
        """FDR校正

        Args:
            p_values: p值数组

        Returns:
            校正后的p值
        """
        n = len(p_values)
        sorted_idx = np.argsort(p_values)
        sorted_p = p_values[sorted_idx]

        if self.fdr_method == "bh":
            # Benjamini-Hochberg
            adjusted = np.zeros(n)
            adjusted[sorted_idx[-1]] = sorted_p[-1]
            for i in range(n - 2, -1, -1):
                rank = i + 1
                adjusted[sorted_idx[i]] = min(
                    adjusted[sorted_idx[i + 1]],
                    sorted_p[i] * n / rank
                )
        elif self.fdr_method == "bonferroni":
            adjusted = p_values * n
        else:
            adjusted = p_values

        return np.clip(adjusted, 0, 1)

    def generate_heatmap_data(self,
                              correlations: pd.DataFrame,
                              top_n: int = 20) -> Dict:
        """生成热图数据

        Args:
            correlations: 相关性结果
            top_n: 显示前N个

        Returns:
            热图数据
        """
        # 选择最显著的相关性
        significant = correlations[correlations["significant"]].head(top_n)

        if len(significant) == 0:
            return {
                "features": [],
                "genes": [],
                "matrix": []
            }

        # 创建矩阵
        features = significant["feature"].unique()
        genes = significant["gene"].unique()

        matrix = np.zeros((len(features), len(genes)))
        for _, row in significant.iterrows():
            i = list(features).index(row["feature"])
            j = list(genes).index(row["gene"])
            matrix[i, j] = row["correlation"]

        return {
            "features": list(features),
            "genes": list(genes),
            "matrix": matrix.tolist(),
        }


class RealtimePredictionModel:
    """实时预警模型"""

    def __init__(self,
                 window_size: int = 60,
                 prediction_horizon: int = 30,
                 model_type: str = "logistic"):
        """初始化

        Args:
            window_size: 特征窗口大小(秒)
            prediction_horizon: 预测时间窗(秒)
            model_type: 模型类型 ("logistic", "random_forest")
        """
        self.window_size = window_size
        self.prediction_horizon = prediction_horizon
        self.model_type = model_type
        self._model = None
        self._feature_names = []

    def _extract_features(self, data: List[float]) -> np.ndarray:
        """提取时间序列特征

        Args:
            data: 时间序列数据

        Returns:
            特征向量
        """
        if len(data) < 2:
            return np.zeros(10)

        features = []
        arr = np.array(data)

        # 统计特征
        features.append(np.mean(arr))
        features.append(np.std(arr))
        features.append(np.min(arr))
        features.append(np.max(arr))
        features.append(np.median(arr))

        # 趋势特征
        if len(arr) > 1:
            x = np.arange(len(arr))
            slope = np.polyfit(x, arr, 1)[0]
            features.append(slope)
        else:
            features.append(0.0)

        # 变异特征
        if np.mean(arr) > 0:
            features.append(np.std(arr) / np.mean(arr))  # CV
        else:
            features.append(0.0)

        # 变化率
        if len(arr) > 1:
            diffs = np.diff(arr)
            features.append(np.mean(diffs))
            features.append(np.std(diffs))
        else:
            features.append(0.0)
            features.append(0.0)

        # 范围
        features.append(np.max(arr) - np.min(arr))

        return np.array(features)

    def train(self,
              historical_data: pd.DataFrame,
              labels: np.ndarray):
        """训练模型

        Args:
            historical_data: 历史数据 (每行一个样本)
            labels: 标签 (0/1)
        """
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier

        # 提取特征
        X = []
        for _, row in historical_data.iterrows():
            features = self._extract_features(row.values)
            X.append(features)

        X = np.array(X)

        # 训练模型
        if self.model_type == "logistic":
            self._model = LogisticRegression(max_iter=1000)
        elif self.model_type == "random_forest":
            self._model = RandomForestClassifier(n_estimators=100)
        else:
            raise ValueError(f"Unknown model: {self.model_type}")

        self._model.fit(X, labels)
        self._feature_names = [
            "mean", "std", "min", "max", "median",
            "slope", "cv", "mean_diff", "std_diff", "range"
        ]

        logger.info(f"Trained {self.model_type} model on {len(X)} samples")

    def predict(self, current_data: List[float]) -> Dict:
        """预测

        Args:
            current_data: 当前时间序列数据

        Returns:
            预测结果
        """
        if self._model is None:
            raise RuntimeError("Model not trained")

        features = self._extract_features(current_data).reshape(1, -1)

        prediction = int(self._model.predict(features)[0])
        probability = float(self._model.predict_proba(features)[0, 1])

        return {
            "prediction": prediction,
            "probability": probability,
            "risk_level": self._get_risk_level(probability),
            "features": dict(zip(self._feature_names, features[0])),
        }

    def _get_risk_level(self, probability: float) -> str:
        """获取风险等级

        Args:
            probability: 预测概率

        Returns:
            风险等级
        """
        if probability >= 0.8:
            return "high"
        elif probability >= 0.5:
            return "medium"
        elif probability >= 0.3:
            return "low"
        else:
            return "minimal"

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """评估模型

        Args:
            X_test: 测试数据
            y_test: 测试标签

        Returns:
            评估指标
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, roc_auc_score
        )

        # 提取特征
        features = np.array([
            self._extract_features(row) for row in X_test
        ])

        y_pred = self._model.predict(features)
        y_prob = self._model.predict_proba(features)[:, 1]

        return {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "auroc": float(roc_auc_score(y_test, y_prob)) if len(np.unique(y_test)) > 1 else 0.0,
        }


class MultiModalVisualizer:
    """多模态数据联合可视化"""

    def __init__(self, figsize: tuple = (16, 10), dpi: int = 100):
        """初始化

        Args:
            figsize: 图像大小
            dpi: 分辨率
        """
        self.figsize = figsize
        self.dpi = dpi

    def create_linked_view(self,
                           imaging_data: Optional[np.ndarray] = None,
                           imaging_mask: Optional[np.ndarray] = None,
                           expression_data: Optional[pd.DataFrame] = None,
                           clinical_data: Optional[pd.DataFrame] = None,
                           realtime_data: Optional[Dict] = None,
                           save_path: Optional[str] = None):
        """创建联动视图

        Args:
            imaging_data: 影像数据
            imaging_mask: 影像掩码
            expression_data: 表达数据
            clinical_data: 临床数据
            realtime_data: 实时数据
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec

        # 确定子图数量
        n_plots = sum([
            imaging_data is not None,
            expression_data is not None,
            clinical_data is not None,
            realtime_data is not None
        ])

        if n_plots == 0:
            raise ValueError("At least one data source required")

        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

        axes = {}

        # 1. 影像视图
        if imaging_data is not None:
            ax_img = fig.add_subplot(gs[0, 0])
            if imaging_data.ndim == 3:
                mid = imaging_data.shape[0] // 2
                img_slice = imaging_data[mid]
            else:
                img_slice = imaging_data

            ax_img.imshow(img_slice, cmap='gray')
            if imaging_mask is not None:
                if imaging_mask.ndim == 3:
                    mask_slice = imaging_mask[mid]
                else:
                    mask_slice = imaging_mask
                ax_img.imshow(mask_slice, cmap='jet', alpha=0.3)

            ax_img.set_title("Medical Imaging")
            ax_img.axis('off')
            axes['imaging'] = ax_img

        # 2. 表达数据热图
        if expression_data is not None:
            ax_expr = fig.add_subplot(gs[0, 1])
            if len(expression_data) > 0:
                # 取前20个基因
                data_to_show = expression_data.iloc[:, :min(20, expression_data.shape[1])]
                im = ax_expr.imshow(data_to_show.T, aspect='auto', cmap='RdBu_r')
                ax_expr.set_title("Gene Expression")
                ax_expr.set_xlabel("Samples")
                ax_expr.set_ylabel("Genes")
                plt.colorbar(im, ax=ax_expr, label="Expression")
            axes['expression'] = ax_expr

        # 3. 临床数据
        if clinical_data is not None:
            ax_clin = fig.add_subplot(gs[1, 0])
            if len(clinical_data) > 0:
                # 选择数值列
                numeric_cols = clinical_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    clinical_data[numeric_cols[:5]].boxplot(ax=ax_clin)
                    ax_clin.set_title("Clinical Data")
                    ax_clin.set_xticklabels(ax_clin.get_xticklabels(), rotation=45)
            axes['clinical'] = ax_clin

        # 4. 实时数据
        if realtime_data is not None:
            ax_rt = fig.add_subplot(gs[1, 1])
            for metric, values in realtime_data.items():
                if isinstance(values, list) and len(values) > 0:
                    ax_rt.plot(values, label=metric, alpha=0.7)
            ax_rt.set_title("Real-time Monitoring")
            ax_rt.set_xlabel("Time")
            ax_rt.set_ylabel("Value")
            ax_rt.legend()
            axes['realtime'] = ax_rt

        plt.suptitle("MSRA Multi-modal Linked View", fontsize=14, fontweight='bold')

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved multi-modal view to: {save_path}")

        return fig

    def create_summary_dashboard(self,
                                 data_sources: Dict[str, Any],
                                 save_path: Optional[str] = None):
        """创建摘要仪表盘

        Args:
            data_sources: 数据源字典
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        import matplotlib.pyplot as plt

        n_sources = len(data_sources)
        fig, axes = plt.subplots(1, n_sources,
                                  figsize=(n_sources * 4, 4),
                                  dpi=self.dpi)

        if n_sources == 1:
            axes = [axes]

        for i, (name, data) in enumerate(data_sources.items()):
            ax = axes[i]

            if isinstance(data, np.ndarray) and data.ndim >= 2:
                # 影像数据
                if data.ndim == 3:
                    mid = data.shape[0] // 2
                    ax.imshow(data[mid], cmap='gray')
                else:
                    ax.imshow(data, cmap='gray')
                ax.set_title(name)
                ax.axis('off')

            elif isinstance(data, pd.DataFrame):
                # 表格数据
                numeric_data = data.select_dtypes(include=[np.number])
                if len(numeric_data) > 0:
                    numeric_data.boxplot(ax=ax)
                    ax.set_title(name)
                    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

            elif isinstance(data, dict):
                # 字典数据
                for key, values in data.items():
                    if isinstance(values, list):
                        ax.plot(values, label=key)
                ax.set_title(name)
                ax.legend()

            else:
                ax.text(0.5, 0.5, str(data),
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(name)

        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved summary dashboard to: {save_path}")

        return fig


class DataAligner:
    """多模态数据对齐器

    支持三种对齐策略：
    - inner: 严格匹配（取交集，默认）
    - outer: 允许缺失（取并集 + 插补）
    - time_based: 时序数据按时间窗对齐

    Usage:
        aligner = DataAligner(strategy="inner")
        aligned = aligner.align({
            "radiomics": df_features,
            "expression": df_expr,
        })
        # aligned["radiomics"], aligned["expression"] 已对齐到相同样本
    """

    def __init__(self, strategy: str = "inner", fill_method: str = "mean"):
        """初始化数据对齐器

        Args:
            strategy: 对齐策略 ("inner" | "outer" | "time_based")
            fill_method: 缺失值填充方法 ("mean" | "median" | "zero" | "ffill")
        """
        valid_strategies = {"inner", "outer", "time_based"}
        if strategy not in valid_strategies:
            raise ValueError(
                f"Invalid strategy '{strategy}'. Must be one of {valid_strategies}"
            )
        valid_fills = {"mean", "median", "zero", "ffill"}
        if fill_method not in valid_fills:
            raise ValueError(
                f"Invalid fill_method '{fill_method}'. Must be one of {valid_fills}"
            )
        self.strategy = strategy
        self.fill_method = fill_method

    def align(
        self,
        data_sources: Dict[str, Any],
        strategy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """执行数据对齐

        Args:
            data_sources: 数据源字典 {name: DataFrame or Dict}
            strategy: 覆盖默认策略

        Returns:
            对齐后的数据源字典 (所有 DataFrame 具有相同的 index)

        Raises:
            ValueError: 当 inner join 后样本数 < 3
        """
        active_strategy = strategy or self.strategy

        if not data_sources:
            raise ValueError("data_sources 不能为空")

        if active_strategy == "inner":
            return self._inner_join(data_sources)
        elif active_strategy == "outer":
            return self._outer_join(data_sources)
        elif active_strategy == "time_based":
            # 时间窗从 Phase 0 参数继承 (默认 60 秒)
            return self._time_based_align(data_sources, window_seconds=60)
        else:
            raise ValueError(f"Unknown strategy: {active_strategy}")

    def _inner_join(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """严格匹配：取所有 DataFrame index 的交集

        Args:
            data_sources: 数据源字典

        Returns:
            对齐后的数据源字典

        Raises:
            ValueError: 当交集样本数 < 3
        """
        common_samples = self._get_common_samples(data_sources)

        if len(common_samples) < 3:
            raise ValueError(
                f"Inner join 后样本数 {len(common_samples)} < 3，"
                f"数据不足以进行融合分析。请考虑使用 outer join 策略或增加样本量。"
            )

        aligned: Dict[str, Any] = {}
        # 排序以确保一致性
        sorted_samples = sorted(common_samples)

        for name, data in data_sources.items():
            if isinstance(data, pd.DataFrame):
                aligned[name] = data.loc[sorted_samples].copy()
            elif isinstance(data, np.ndarray):
                # ndarray 按索引对齐
                idx_map = {s: i for i, s in enumerate(data) if s in set(common_samples)}
                indices = [idx_map[s] for s in sorted_samples if s in idx_map]
                aligned[name] = data[indices].copy()
            elif isinstance(data, dict):
                aligned[name] = {k: data[k] for k in sorted_samples if k in data}
            else:
                aligned[name] = data

        logger.info(
            f"Inner join aligned {len(data_sources)} data sources "
            f"to {len(sorted_samples)} common samples"
        )
        return aligned

    def _outer_join(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """允许缺失：取所有 DataFrame index 的并集，缺失值用 fill_method 填充

        Args:
            data_sources: 数据源字典

        Returns:
            对齐后的数据源字典
        """
        # 收集所有样本 ID 的并集
        all_samples: set = set()
        for name, data in data_sources.items():
            if isinstance(data, pd.DataFrame):
                all_samples.update(data.index)
            elif isinstance(data, dict):
                all_samples.update(data.keys())

        sorted_samples = sorted(all_samples)
        aligned: Dict[str, Any] = {}

        for name, data in data_sources.items():
            if isinstance(data, pd.DataFrame):
                # Reindex 并填充缺失值
                reindexed = data.reindex(sorted_samples)
                aligned[name] = self._fill_missing(reindexed, self.fill_method)
            elif isinstance(data, dict):
                # Dict 类型保持原样（缺失的 key 不添加）
                aligned[name] = dict(data)
            else:
                aligned[name] = data

        logger.info(
            f"Outer join aligned {len(data_sources)} data sources "
            f"to {len(sorted_samples)} total samples (filled with '{self.fill_method}')"
        )
        return aligned

    def _time_based_align(
        self,
        data_sources: Dict[str, Any],
        window_seconds: int = 60,
    ) -> Dict[str, Any]:
        """时序对齐：按时间窗对齐时序数据

        将不同时间戳的数据按指定的窗口大小进行分组聚合，
        每个窗口内取均值（对于数值数据）。

        时间窗从 Phase 0 参数继承（不独立设定）。

        Args:
            data_sources: 数据源字典
            window_seconds: 时间窗口大小（秒），从 Phase 0 继承

        Returns:
            对齐后的数据源字典
        """
        aligned: Dict[str, Any] = {}

        for name, data in data_sources.items():
            if isinstance(data, pd.DataFrame):
                # 检查是否有时间戳索引
                if isinstance(data.index, pd.DatetimeIndex):
                    # 按时间窗口重采样
                    resampled = data.resample(f"{window_seconds}s").mean()
                    aligned[name] = resampled.dropna(how="all")
                else:
                    # 非时间索引，按行数分块
                    n_rows = len(data)
                    window_rows = max(1, n_rows // max(1, window_seconds))
                    # 每 window_rows 行取均值
                    n_groups = max(1, n_rows // window_rows)
                    groups = []
                    for i in range(n_groups):
                        start = i * window_rows
                        end = min((i + 1) * window_rows, n_rows)
                        if start < end:
                            chunk = data.iloc[start:end]
                            groups.append(chunk.mean(numeric_only=True))
                    if groups:
                        aligned[name] = pd.DataFrame(groups)
                    else:
                        aligned[name] = data.copy()
            elif isinstance(data, dict):
                # Dict[str, List] 类型：按窗口分块取均值
                aligned_dict: Dict[str, list] = {}
                for key, values in data.items():
                    if isinstance(values, list) and len(values) > 0:
                        arr = np.array(values, dtype=float)
                        window = max(1, len(arr) // max(1, window_seconds))
                        n_groups = max(1, len(arr) // window)
                        grouped = []
                        for i in range(n_groups):
                            start = i * window
                            end = min((i + 1) * window, len(arr))
                            if start < end:
                                grouped.append(float(np.mean(arr[start:end])))
                        aligned_dict[key] = grouped
                    else:
                        aligned_dict[key] = list(values) if isinstance(values, list) else values
                aligned[name] = aligned_dict
            else:
                aligned[name] = data

        logger.info(
            f"Time-based aligned {len(data_sources)} data sources "
            f"with window={window_seconds}s"
        )
        return aligned

    def _get_common_samples(self, data_sources: Dict[str, Any]) -> List[str]:
        """获取所有数据源的公共样本 ID

        Args:
            data_sources: 数据源字典

        Returns:
            公共样本 ID 列表
        """
        common: Optional[set] = None

        for name, data in data_sources.items():
            if isinstance(data, pd.DataFrame):
                current = set(data.index)
            elif isinstance(data, dict):
                current = set(data.keys())
            elif isinstance(data, np.ndarray):
                current = set(range(data.shape[0]))
            elif isinstance(data, (list, tuple)):
                current = set(range(len(data)))
            else:
                continue

            if common is None:
                common = current
            else:
                common = common & current

        return sorted(common) if common else []

    def _fill_missing(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        """填充缺失值

        Args:
            df: 含缺失值的 DataFrame
            method: 填充方法 ("mean" | "median" | "zero" | "ffill")

        Returns:
            填充后的 DataFrame
        """
        if df.empty:
            return df

        if method == "mean":
            return df.fillna(df.mean(numeric_only=True))
        elif method == "median":
            return df.fillna(df.median(numeric_only=True))
        elif method == "zero":
            return df.fillna(0)
        elif method == "ffill":
            return df.ffill().fillna(0)
        else:
            return df.fillna(0)


def export_v1_schema(
    correlation_results: Optional[Dict] = None,
    model_metrics: Optional[Dict] = None,
    visualization_data: Optional[Dict] = None,
    output_dir: str = ".",
) -> Dict[str, str]:
    """导出 msra/cross_domain_result/v1 标准格式

    输出文件结构:
        output_dir/
        ├── correlation_results.csv     # 关联分析结果表
        ├── model_metrics.json           # 模型评估指标
        ├── visualization_bundle/        # 可视化文件包
        │   ├── linked_view.png
        │   └── summary_dashboard.png
        └── cross_domain_report.md       # 综合报告

    Args:
        correlation_results: RadiomicsDEGCorrelation.correlate() 的返回值
        model_metrics: RealtimePredictionModel.evaluate() 的返回值
        visualization_data: MultiModalVisualizer 的输出数据
        output_dir: 输出目录

    Returns:
        文件路径映射:
        {
            "correlation_results": "path/to/correlation_results.csv",
            "model_metrics": "path/to/model_metrics.json",
            "visualization_bundle": "path/to/visualization_bundle/",
            "report": "path/to/cross_domain_report.md",
            "schema_version": "msra/cross_domain_result/v1",
        }
    """
    import json
    from datetime import datetime, timezone

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    viz_bundle_dir = output_path / "visualization_bundle"
    viz_bundle_dir.mkdir(parents=True, exist_ok=True)

    result: Dict[str, str] = {
        "schema_version": "msra/cross_domain_result/v1",
    }

    # 1. 导出关联分析结果
    corr_path = output_path / "correlation_results.csv"
    if correlation_results is not None:
        corr_df = correlation_results.get("correlations")
        if isinstance(corr_df, pd.DataFrame):
            corr_df.to_csv(corr_path, index=False, encoding="utf-8")
        else:
            # 创建空的 CSV 带表头
            pd.DataFrame(columns=[
                "feature", "gene", "correlation", "p_value",
                "p_adj", "significant", "method"
            ]).to_csv(corr_path, index=False, encoding="utf-8")
    else:
        pd.DataFrame(columns=[
            "feature", "gene", "correlation", "p_value",
            "p_adj", "significant", "method"
        ]).to_csv(corr_path, index=False, encoding="utf-8")
    result["correlation_results"] = str(corr_path)

    # 2. 导出模型评估指标
    metrics_path = output_path / "model_metrics.json"
    if model_metrics is not None:
        # 确保所有值可序列化
        serializable_metrics = {}
        for key, val in model_metrics.items():
            if isinstance(val, (np.floating, np.integer)):
                serializable_metrics[key] = float(val)
            elif isinstance(val, np.ndarray):
                serializable_metrics[key] = val.tolist()
            else:
                serializable_metrics[key] = val
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(serializable_metrics, f, ensure_ascii=False, indent=2)
    else:
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    result["model_metrics"] = str(metrics_path)

    # 3. 复制/记录可视化文件
    if visualization_data is not None:
        viz_paths = visualization_data.get("paths", [])
        for p in viz_paths:
            src = Path(p)
            if src.exists():
                import shutil
                shutil.copy2(src, viz_bundle_dir / src.name)
    result["visualization_bundle"] = str(viz_bundle_dir)

    # 4. 生成综合报告
    report_path = output_path / "cross_domain_report.md"
    report_lines = [
        "# Cross-Domain Analysis Report",
        "",
        f"> **Schema**: msra/cross_domain_result/v1",
        f"> **Generated**: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## 1. Summary",
        "",
    ]

    if correlation_results is not None:
        n_sig = correlation_results.get("n_significant", 0)
        n_total = correlation_results.get("n_total", 0)
        method = correlation_results.get("method", "unknown")
        n_samples = correlation_results.get("samples", 0)
        report_lines.extend([
            "### Correlation Analysis",
            f"- Method: {method}",
            f"- Samples: {n_samples}",
            f"- Total pairs: {n_total}",
            f"- Significant pairs (p_adj < 0.05 & |r| >= 0.3): {n_sig}",
            "",
        ])

    if model_metrics is not None:
        report_lines.extend([
            "### Prediction Model",
            f"- Model type: {model_metrics.get('model_type', 'N/A')}",
            f"- Accuracy: {model_metrics.get('accuracy', 'N/A')}",
            f"- Precision: {model_metrics.get('precision', 'N/A')}",
            f"- Recall: {model_metrics.get('recall', 'N/A')}",
            f"- F1: {model_metrics.get('f1', 'N/A')}",
            f"- AUROC: {model_metrics.get('auroc', 'N/A')}",
            "",
        ])

    if visualization_data is not None:
        report_lines.extend([
            "### Visualization",
            f"- Linked view: {visualization_data.get('linked_view', 'N/A')}",
            f"- Summary dashboard: {visualization_data.get('summary_dashboard', 'N/A')}",
            "",
        ])

    report_lines.extend([
        "## 2. Output Files",
        f"- Correlation results: `{result.get('correlation_results', 'N/A')}`",
        f"- Model metrics: `{result.get('model_metrics', 'N/A')}`",
        f"- Visualization bundle: `{result.get('visualization_bundle', 'N/A')}`",
        "",
        "## 3. Quality Gate",
        "- Gate CD-1.5: See quality_gates.py output",
        "- Gate CD-3.5: See quality_gates.py output",
        "",
    ])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    result["report"] = str(report_path)

    logger.info(
        f"Exported cross_domain_result/v1 schema to {output_dir}: "
        f"correlation_results.csv, model_metrics.json, "
        f"visualization_bundle/, cross_domain_report.md"
    )

    return result
