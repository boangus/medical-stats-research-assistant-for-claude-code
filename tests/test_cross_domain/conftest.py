"""Public fixtures for cross_domain unit tests.

All mock data uses seed=42 for reproducibility.
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _set_seed():
    """固定随机种子确保可复现 (seed=42)"""
    np.random.seed(42)


@pytest.fixture
def mock_radiomics_features():
    """模拟影像组学特征矩阵 (10 样本 × 5 特征)

    Returns:
        pd.DataFrame: index=sample_id, columns=feature_name
    """
    np.random.seed(42)
    samples = [f"S{i:03d}" for i in range(10)]
    features = [f"feature_{j}" for j in range(5)]
    data = np.random.randn(10, 5) * 10 + 50
    return pd.DataFrame(data, index=samples, columns=features)


@pytest.fixture
def mock_expression_data():
    """模拟差异基因表达矩阵 (10 样本 × 6 基因)

    Returns:
        pd.DataFrame: index=sample_id, columns=gene_name
    """
    np.random.seed(42)
    samples = [f"S{i:03d}" for i in range(10)]
    genes = [f"GENE{i}" for i in range(6)]
    data = np.random.randn(10, 6) * 2 + 8
    return pd.DataFrame(data, index=samples, columns=genes)


@pytest.fixture
def mock_radiomics_features_small():
    """小规模影像特征矩阵 (5 样本 × 3 特征)，与表达矩阵部分重叠"""
    np.random.seed(42)
    samples = [f"S{i:03d}" for i in range(3, 8)]  # S003-S007
    features = [f"feature_{j}" for j in range(3)]
    data = np.random.randn(5, 3) * 5 + 20
    return pd.DataFrame(data, index=samples, columns=features)


@pytest.fixture
def mock_expression_data_small():
    """小规模表达矩阵 (5 样本 × 4 基因)，与影像特征部分重叠"""
    np.random.seed(42)
    samples = [f"S{i:003d}" for i in range(2, 7)]  # S002-S006
    genes = [f"GENE{i}" for i in range(4)]
    data = np.random.randn(5, 4) * 1.5 + 5
    return pd.DataFrame(data, index=samples, columns=genes)


@pytest.fixture
def mock_realtime_data():
    """模拟实时生命体征数据 (Dict[str, List])

    Returns:
        dict: {metric_name: [values]}
    """
    np.random.seed(42)
    n_points = 120
    return {
        "heart_rate": list(np.random.normal(80, 10, n_points)),
        "blood_pressure": list(np.random.normal(120, 15, n_points)),
        "spo2": list(np.random.normal(97, 2, n_points)),
    }


@pytest.fixture
def mock_realtime_dataframe():
    """模拟实时数据 DataFrame (120 行 × 3 指标)"""
    np.random.seed(42)
    n_rows = 120
    data = {
        "heart_rate": np.random.normal(80, 10, n_rows),
        "blood_pressure": np.random.normal(120, 15, n_rows),
        "spo2": np.random.normal(97, 2, n_rows),
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_labels():
    """模拟二分类标签 (20 样本)

    Returns:
        np.ndarray: 0/1 标签
    """
    np.random.seed(42)
    return np.array([0, 1, 0, 1, 1, 0, 1, 0, 0, 1,
                     1, 0, 1, 0, 0, 1, 0, 1, 1, 0])


@pytest.fixture
def mock_historical_data():
    """模拟历史时序数据 DataFrame (20 样本 × 10 时间点)

    用于 RealtimePredictionModel.train()
    """
    np.random.seed(42)
    n_samples = 20
    n_timepoints = 10
    data = np.random.randn(n_samples, n_timepoints) * 5 + 80
    return pd.DataFrame(data, columns=[f"t{i}" for i in range(n_timepoints)])


@pytest.fixture
def mock_clinical_data():
    """模拟临床数据 DataFrame (10 样本 × 4 变量)"""
    np.random.seed(42)
    samples = [f"S{i:03d}" for i in range(10)]
    data = {
        "age": np.random.randint(30, 80, 10),
        "bmi": np.random.normal(25, 4, 10),
        "glucose": np.random.normal(100, 20, 10),
        "cholesterol": np.random.normal(180, 30, 10),
    }
    return pd.DataFrame(data, index=samples)


@pytest.fixture
def mock_imaging_data():
    """模拟影像数据 3D numpy 数组 (32×32×16)"""
    np.random.seed(42)
    return np.random.rand(32, 32, 16).astype(np.float32)


@pytest.fixture
def mock_imaging_mask():
    """模拟影像掩码 3D numpy 数组 (32×32×16, binary)"""
    np.random.seed(42)
    mask = np.random.rand(32, 32, 16) > 0.7
    return mask.astype(np.float32)


@pytest.fixture
def mock_correlation_results(mock_radiomics_features, mock_expression_data):
    """模拟关联分析结果"""
    from msra_modules.cross_domain import RadiomicsDEGCorrelation
    corr = RadiomicsDEGCorrelation(correlation_method="spearman", pval_threshold=0.05)
    return corr.correlate(mock_radiomics_features, mock_expression_data)


@pytest.fixture
def mock_model_metrics():
    """模拟模型评估指标"""
    return {
        "accuracy": 0.85,
        "precision": 0.80,
        "recall": 0.75,
        "f1": 0.77,
        "auroc": 0.82,
        "model_type": "logistic",
        "n_samples": 20,
        "n_features": 10,
    }


@pytest.fixture
def mock_visualization_data():
    """模拟可视化数据"""
    return {
        "matrix_shape": [5, 6],
        "curve_points": {"heart_rate": 120, "spo2": 120},
        "paths": [],
        "linked_view": "linked_view.png",
        "summary_dashboard": "summary_dashboard.png",
    }


@pytest.fixture
def mock_data_sources_correlation(mock_radiomics_features, mock_expression_data):
    """模拟关联分析场景的数据源"""
    return {
        "radiomics": mock_radiomics_features,
        "expression": mock_expression_data,
    }


@pytest.fixture
def mock_data_sources_prediction(mock_realtime_dataframe, mock_labels):
    """模拟预测场景的数据源"""
    return {
        "realtime": mock_realtime_dataframe,
        "labels": mock_labels,
    }
