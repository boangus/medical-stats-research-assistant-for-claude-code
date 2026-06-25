"""
大规模数据处理引擎 E2E 验证测试

覆盖 Polars/DuckDB 两个引擎（Dask 因环境问题跳过）的端到端性能验证：
- 引擎自动选择（EngineSelector）
- 数据读写（CSV/Parquet）
- 过滤（filter）
- 聚合（groupby_aggregate）
- 连接（join）
- to_pandas 转换
- 跨引擎结果一致性验证
- 性能基准记录

数据规模：
- small: 1K 行（功能验证）
- medium: 100K 行（性能基准）
"""

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.large_scale_processing.engine_factory import EngineFactory
from shared.large_scale_processing.engine_selector import EngineSelector, ProcessingEngine

# Guard optional scale-layer engines — skip gracefully if not installed
try:
    import polars as _polars_mod
    _has_polars = True
except ImportError:
    _has_polars = False

try:
    import duckdb as _duckdb_mod
    _has_duckdb = True
except ImportError:
    _has_duckdb = False

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture(scope="module")
def small_csv(tmp_path_factory):
    """生成小型测试数据集 (1K 行)"""
    rng = np.random.default_rng(42)
    n = 1_000
    df = pd.DataFrame({
        "id": range(n),
        "age": rng.integers(18, 80, n),
        "gender": rng.choice(["M", "F"], n),
        "treatment": rng.choice(["A", "B", "C"], n),
        "outcome": rng.normal(50, 10, n).round(2),
        "biomarker": rng.exponential(5, n).round(3),
        "visit_month": rng.choice([0, 3, 6, 12], n),
    })
    path = tmp_path_factory.mktemp("data") / "small.csv"
    df.to_csv(path, index=False)
    return str(path), df


@pytest.fixture(scope="module")
def medium_csv(tmp_path_factory):
    """生成中型测试数据集 (100K 行)"""
    rng = np.random.default_rng(123)
    n = 100_000
    df = pd.DataFrame({
        "patient_id": range(n),
        "age": rng.integers(18, 90, n),
        "sex": rng.choice(["Male", "Female"], n),
        "group": rng.choice(["Control", "Treatment_A", "Treatment_B"], n),
        "baseline_value": rng.normal(100, 15, n).round(2),
        "followup_value": rng.normal(105, 15, n).round(2),
        "time_to_event": rng.exponential(24, n).round(1),
        "event": rng.binomial(1, 0.3, n),
        "site": rng.choice([f"Site_{i}" for i in range(20)], n),
    })
    path = tmp_path_factory.mktemp("data") / "medium.csv"
    df.to_csv(path, index=False)
    return str(path), df


@pytest.fixture(scope="module")
def parquet_data(tmp_path_factory, medium_csv):
    """将中型数据集转为 Parquet 格式"""
    csv_path, df = medium_csv
    pq_path = tmp_path_factory.mktemp("data") / "medium.parquet"
    df.to_parquet(pq_path, index=False)
    return str(pq_path), df


@pytest.fixture(scope="module")
def join_data(tmp_path_factory):
    """生成用于 Join 测试的数据集"""
    rng = np.random.default_rng(456)
    n_main = 10_000
    n_lookup = 500

    main_df = pd.DataFrame({
        "patient_id": range(n_main),
        "site_id": rng.integers(1, n_lookup + 1, n_main),
        "value": rng.normal(0, 1, n_main).round(4),
    })
    lookup_df = pd.DataFrame({
        "site_id": range(1, n_lookup + 1),
        "site_name": [f"Hospital_{i}" for i in range(1, n_lookup + 1)],
        "region": rng.choice(["North", "South", "East", "West"], n_lookup),
    })

    main_path = tmp_path_factory.mktemp("data") / "main.csv"
    lookup_path = tmp_path_factory.mktemp("data") / "lookup.csv"
    main_df.to_csv(main_path, index=False)
    lookup_df.to_csv(lookup_path, index=False)

    return str(main_path), main_df, str(lookup_path), lookup_df


# ============================================================
# EngineSelector Tests
# ============================================================


class TestEngineSelector:
    """引擎自动选择测试"""

    def test_small_file_selects_pandas(self):
        engine = EngineSelector.select_engine(file_size_bytes=500 * 1024 * 1024)  # 500MB
        assert engine == ProcessingEngine.PANDAS

    def test_medium_file_selects_polars(self):
        engine = EngineSelector.select_engine(file_size_bytes=2 * 1024 * 1024 * 1024)  # 2GB
        assert engine == ProcessingEngine.POLARS

    def test_large_file_selects_duckdb(self):
        engine = EngineSelector.select_engine(file_size_bytes=50 * 1024 * 1024 * 1024)  # 50GB
        assert engine == ProcessingEngine.DUCKDB

    def test_very_large_file_selects_dask(self):
        engine = EngineSelector.select_engine(file_size_bytes=200 * 1024 * 1024 * 1024)  # 200GB
        assert engine == ProcessingEngine.DASK

    def test_row_based_selection_small(self):
        engine = EngineSelector.select_engine(estimated_rows=50_000)
        assert engine == ProcessingEngine.PANDAS

    def test_row_based_selection_medium(self):
        engine = EngineSelector.select_engine(estimated_rows=5_000_000)
        assert engine == ProcessingEngine.POLARS

    def test_default_selection(self):
        engine = EngineSelector.select_engine()
        assert engine == ProcessingEngine.POLARS

    def test_engine_info_exists(self):
        for eng in ProcessingEngine:
            info = EngineSelector.get_engine_info(eng)
            assert "name" in info
            assert "description" in info

    def test_boundary_exact_1gb(self):
        engine = EngineSelector.select_engine(file_size_bytes=1 * 1024 * 1024 * 1024)
        assert engine == ProcessingEngine.POLARS

    def test_boundary_exact_10gb(self):
        engine = EngineSelector.select_engine(file_size_bytes=10 * 1024 * 1024 * 1024)
        assert engine == ProcessingEngine.DUCKDB


# ============================================================
# Polars Engine E2E
# ============================================================


@pytest.mark.skipif(not _has_polars, reason="polars not installed")
class TestPolarsEngineE2E:
    """Polars 引擎端到端验证"""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = EngineFactory.create_engine("polars")

    def test_read_csv(self, small_csv):
        path, original = small_csv
        df = self.engine.read_csv(path)
        assert len(df) == len(original)
        assert len(df.columns) == len(original.columns)

    def test_read_parquet(self, parquet_data):
        path, original = parquet_data
        df = self.engine.read_parquet(path)
        assert len(df) == len(original)

    def test_filter_string(self, small_csv):
        path, _ = small_csv
        df = self.engine.read_csv(path)
        filtered = self.engine.filter(df, 'age > 60')
        pdf = self.engine.to_pandas(filtered)
        assert len(pdf) > 0
        assert all(pdf["age"] > 60)

    def test_groupby_aggregate(self, small_csv):
        path, _ = small_csv
        df = self.engine.read_csv(path)
        result = self.engine.groupby_aggregate(df, ["treatment"], {"outcome": "mean"})
        pdf = self.engine.to_pandas(result)
        assert len(pdf) == 3  # A, B, C
        assert "outcome_mean" in pdf.columns or "outcome" in pdf.columns

    def test_join(self, join_data):
        main_path, _, lookup_path, _ = join_data
        main_df = self.engine.read_csv(main_path)
        lookup_df = self.engine.read_csv(lookup_path)
        joined = self.engine.join(main_df, lookup_df, on="site_id", how="inner")
        pdf = self.engine.to_pandas(joined)
        assert "site_name" in pdf.columns
        assert "region" in pdf.columns
        assert len(pdf) == 10_000  # All main rows should match

    def test_to_pandas(self, small_csv):
        path, original = small_csv
        df = self.engine.read_csv(path)
        pdf = self.engine.to_pandas(df)
        assert isinstance(pdf, pd.DataFrame)
        assert len(pdf) == len(original)

    def test_to_parquet_roundtrip(self, small_csv, tmp_path):
        path, _ = small_csv
        df = self.engine.read_csv(path)
        out_path = str(tmp_path / "output.parquet")
        self.engine.to_parquet(df, out_path)
        assert os.path.exists(out_path)
        # Read back and verify
        df2 = self.engine.read_parquet(out_path)
        assert len(df2) == len(df)

    def test_performance_medium(self, medium_csv):
        """性能基准：100K 行数据处理"""
        path, _ = medium_csv

        t0 = time.perf_counter()
        df = self.engine.read_csv(path)
        t_read = time.perf_counter() - t0

        t0 = time.perf_counter()
        filtered = self.engine.filter(df, 'event == 1')
        t_filter = time.perf_counter() - t0

        t0 = time.perf_counter()
        pdf = self.engine.to_pandas(df)
        agg = pdf.groupby("group").agg({"baseline_value": "mean", "followup_value": "mean"})
        t_agg = time.perf_counter() - t0

        # Performance assertions (generous bounds for CI)
        assert t_read < 10.0, f"CSV read took {t_read:.2f}s (>10s)"
        assert t_filter < 5.0, f"Filter took {t_filter:.2f}s (>5s)"

        # Record metrics (visible with -v)
        print("\n  Polars Performance (100K rows):")
        print(f"    Read CSV: {t_read:.3f}s")
        print(f"    Filter:   {t_filter:.3f}s")
        print(f"    GroupBy:  {t_agg:.3f}s")


# ============================================================
# DuckDB Engine E2E
# ============================================================


@pytest.mark.skipif(not _has_duckdb, reason="duckdb not installed")
class TestDuckDBEngineE2E:
    """DuckDB 引擎端到端验证"""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = EngineFactory.create_engine("duckdb")

    def test_read_csv(self, small_csv):
        path, original = small_csv
        df = self.engine.read_csv(path)
        pdf = self.engine.to_pandas(df) if not isinstance(df, pd.DataFrame) else df
        assert len(pdf) == len(original)

    def test_read_parquet(self, parquet_data):
        path, original = parquet_data
        df = self.engine.read_parquet(path)
        pdf = self.engine.to_pandas(df) if not isinstance(df, pd.DataFrame) else df
        assert len(pdf) == len(original)

    def test_filter(self, small_csv):
        path, _ = small_csv
        df = self.engine.read_csv(path)
        filtered = self.engine.filter(df, "age > 60")
        pdf = filtered if isinstance(filtered, pd.DataFrame) else self.engine.to_pandas(filtered)
        assert len(pdf) > 0
        assert all(pdf["age"] > 60)

    def test_groupby_aggregate(self, small_csv):
        path, _ = small_csv
        df = self.engine.read_csv(path)
        result = self.engine.groupby_aggregate(df, ["treatment"], {"outcome": "mean"})
        pdf = result if isinstance(result, pd.DataFrame) else self.engine.to_pandas(result)
        assert len(pdf) == 3
        # Column name may be outcome_mean due to DuckDB aliasing
        assert any("outcome" in c for c in pdf.columns)

    def test_join(self, join_data):
        main_path, _, lookup_path, _ = join_data
        main_df = self.engine.read_csv(main_path)
        lookup_df = self.engine.read_csv(lookup_path)
        joined = self.engine.join(main_df, lookup_df, on="site_id", how="inner")
        pdf = joined if isinstance(joined, pd.DataFrame) else self.engine.to_pandas(joined)
        assert "site_name" in pdf.columns

    def test_to_pandas(self, small_csv):
        path, original = small_csv
        df = self.engine.read_csv(path)
        # DuckDB read_csv returns pandas directly
        pdf = df if isinstance(df, pd.DataFrame) else self.engine.to_pandas(df)
        assert isinstance(pdf, pd.DataFrame)
        assert len(pdf) == len(original)

    def test_performance_medium(self, medium_csv):
        """性能基准：100K 行数据处理"""
        path, _ = medium_csv

        t0 = time.perf_counter()
        df = self.engine.read_csv(path)
        t_read = time.perf_counter() - t0

        t0 = time.perf_counter()
        filtered = self.engine.filter(df, "event = 1")
        t_filter = time.perf_counter() - t0

        t0 = time.perf_counter()
        pdf = df if isinstance(df, pd.DataFrame) else self.engine.to_pandas(df)
        agg = pdf.groupby("group").agg({"baseline_value": "mean"})
        t_agg = time.perf_counter() - t0

        assert t_read < 10.0, f"CSV read took {t_read:.2f}s (>10s)"
        assert t_filter < 5.0, f"Filter took {t_filter:.2f}s (>5s)"

        print("\n  DuckDB Performance (100K rows):")
        print(f"    Read CSV: {t_read:.3f}s")
        print(f"    Filter:   {t_filter:.3f}s")
        print(f"    GroupBy:  {t_agg:.3f}s")


# ============================================================
# Cross-Engine Consistency Tests
# ============================================================


@pytest.mark.skipif(not (_has_polars and _has_duckdb), reason="requires both polars and duckdb")
class TestCrossEngineConsistency:
    """跨引擎结果一致性验证"""

    def test_filter_result_consistency(self, small_csv):
        """Polars 和 DuckDB 过滤结果一致"""
        path, _ = small_csv

        polars_engine = EngineFactory.create_engine("polars")
        duckdb_engine = EngineFactory.create_engine("duckdb")

        pdf = polars_engine.to_pandas(
            polars_engine.filter(polars_engine.read_csv(path), 'age > 50')
        )
        ddf = duckdb_engine.to_pandas(
            duckdb_engine.filter(duckdb_engine.read_csv(path), "age > 50")
        )

        assert len(pdf) == len(ddf), (
            f"Filter result count mismatch: Polars={len(pdf)}, DuckDB={len(ddf)}"
        )

    def test_groupby_result_consistency(self, small_csv):
        """Polars 和 DuckDB 聚合结果一致（允许浮点误差）"""
        path, _ = small_csv

        polars_engine = EngineFactory.create_engine("polars")
        duckdb_engine = EngineFactory.create_engine("duckdb")

        p_result = polars_engine.to_pandas(
            polars_engine.groupby_aggregate(
                polars_engine.read_csv(path), ["treatment"], {"outcome": "mean"}
            )
        )
        d_result = duckdb_engine.groupby_aggregate(
            duckdb_engine.read_csv(path), ["treatment"], {"outcome": "mean"}
        )
        d_result = d_result if isinstance(d_result, pd.DataFrame) else duckdb_engine.to_pandas(d_result)

        # Sort both by treatment for comparison
        p_result = p_result.sort_values("treatment").reset_index(drop=True)
        d_result = d_result.sort_values("treatment").reset_index(drop=True)

        assert len(p_result) == len(d_result)

        # Find the outcome column (may be "outcome" or "outcome_mean")
        p_outcome_col = [c for c in p_result.columns if "outcome" in c][0]
        d_outcome_col = [c for c in d_result.columns if "outcome" in c][0]

        np.testing.assert_allclose(
            p_result[p_outcome_col].values,
            d_result[d_outcome_col].values,
            rtol=1e-5,
            err_msg="GroupBy mean values differ between Polars and DuckDB"
        )

    def test_join_result_consistency(self, join_data):
        """Polars 和 DuckDB Join 结果一致"""
        main_path, _, lookup_path, _ = join_data

        polars_engine = EngineFactory.create_engine("polars")
        duckdb_engine = EngineFactory.create_engine("duckdb")

        p_joined = polars_engine.to_pandas(
            polars_engine.join(
                polars_engine.read_csv(main_path),
                polars_engine.read_csv(lookup_path),
                on="site_id", how="inner"
            )
        )
        d_joined = duckdb_engine.to_pandas(
            duckdb_engine.join(
                duckdb_engine.read_csv(main_path),
                duckdb_engine.read_csv(lookup_path),
                on="site_id", how="inner"
            )
        )

        assert len(p_joined) == len(d_joined), (
            f"Join result count mismatch: Polars={len(p_joined)}, DuckDB={len(d_joined)}"
        )
