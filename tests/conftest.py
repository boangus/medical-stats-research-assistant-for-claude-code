"""
conftest.py — pytest 公共 fixtures
"""
import os
import shutil
import sys
import tempfile

import numpy as np
import pandas as pd
import pytest

# 确保 shared/ 目录可导入
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def sample_df():
    """标准测试数据框"""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "patient_id": range(1, n + 1),
        "age": np.random.normal(55, 10, n).astype(int),
        "gender": np.random.choice(["M", "F"], n),
        "treatment": np.random.choice([0, 1], n),
        "outcome": np.random.binomial(1, 0.3, n),
        "biomarker": np.random.normal(50, 15, n),
        "center": np.random.choice(["A", "B", "C"], n),
    })


@pytest.fixture
def survival_df():
    """生存分析测试数据"""
    np.random.seed(42)
    n = 80
    return pd.DataFrame({
        "time": np.random.exponential(12, n),
        "event": np.random.binomial(1, 0.7, n),
        "group": np.random.choice([0, 1], n),
    })


@pytest.fixture
def tmp_dir():
    """临时目录"""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def calibration_data():
    """校准测试数据"""
    np.random.seed(42)
    n = 20
    analysis_ids = [f"ANALYSIS_{i:03d}" for i in range(n)]
    gold = pd.DataFrame({
        "analysis_id": analysis_ids,
        "gold_method": ["Logistic Regression"] * 10 + ["Cox Regression"] * 10,
        "gold_estimate": np.random.uniform(0.5, 2.0, n),
        "gold_lower": np.random.uniform(0.3, 1.0, n),
        "gold_upper": np.random.uniform(1.5, 3.0, n),
        "gold_p": np.random.uniform(0.001, 0.5, n),
        "gold_significant": [p < 0.05 for p in np.random.uniform(0.001, 0.5, n)],
    })
    msra = gold.copy()
    msra.columns = ["analysis_id", "msra_method", "msra_estimate",
                     "msra_lower", "msra_upper", "msra_p", "msra_significant"]
    msra["msra_estimate"] *= np.random.uniform(0.9, 1.1, n)
    # 翻转 2 个显著性
    flip = np.random.choice(n, 2, replace=False)
    msra.loc[flip, "msra_significant"] = ~msra.loc[flip, "msra_significant"]
    return gold, msra
