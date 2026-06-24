"""
Tests for DuckDB engine adapter.

Comprehensive tests covering all BaseEngine interface methods.
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared.large_scale_processing.duckdb_engine import DuckDBEngine


@pytest.fixture
def duckdb_engine():
    """Create DuckDB engine with in-memory database."""
    engine = DuckDBEngine(":memory:")
    yield engine
    engine.close()


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
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
def second_data():
    """Create second sample data for join testing."""
    np.random.seed(123)
    n = 50
    return pd.DataFrame({
        "patient_id": range(1, n + 1),
        "severity": np.random.choice(["Low", "Medium", "High"], n),
        "length_of_stay": np.random.exponential(5, n).astype(int),
    })


class TestDuckDBEngineBasic:
    """Test basic engine properties."""

    def test_name(self, duckdb_engine):
        """Test engine name property."""
        assert duckdb_engine.name == "duckdb"

    def test_supports_gpu(self, duckdb_engine):
        """Test GPU support property."""
        assert duckdb_engine.supports_gpu is False

    def test_context_manager(self, duckdb_engine):
        """Test context manager usage."""
        with DuckDBEngine(":memory:") as engine:
            assert engine.name == "duckdb"


class TestReadOperations:
    """Test read operations."""

    def test_read_csv_from_file(self, duckdb_engine, sample_data, tmp_dir):
        """Test reading CSV file."""
        csv_path = os.path.join(tmp_dir, "test.csv")
        sample_data.to_csv(csv_path, index=False)

        result = duckdb_engine.read_csv(csv_path)
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) == 100
        assert list(pandas_result.columns) == list(sample_data.columns)

    def test_read_parquet_from_file(self, duckdb_engine, sample_data, tmp_dir):
        """Test reading Parquet file."""
        parquet_path = os.path.join(tmp_dir, "test.parquet")
        sample_data.to_parquet(parquet_path, index=False)

        result = duckdb_engine.read_parquet(parquet_path)
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) == 100
        assert list(pandas_result.columns) == list(sample_data.columns)


class TestFilterOperation:
    """Test filter operation."""

    def test_filter_simple(self, duckdb_engine, sample_data):
        """Test simple filter."""
        filtered = duckdb_engine.filter(sample_data, "age > 60")
        result = duckdb_engine.to_pandas(filtered)

        assert all(result["age"] > 60)

    def test_filter_compound(self, duckdb_engine, sample_data):
        """Test compound filter condition."""
        filtered = duckdb_engine.filter(sample_data, "age > 50 AND treatment = 1")
        result = duckdb_engine.to_pandas(filtered)

        assert all(result["age"] > 50)
        assert all(result["treatment"] == 1)

    def test_filter_string_column(self, duckdb_engine, sample_data):
        """Test filter on string column."""
        filtered = duckdb_engine.filter(sample_data, "gender = 'M'")
        result = duckdb_engine.to_pandas(filtered)

        assert all(result["gender"] == "M")


class TestGroupByAggregate:
    """Test groupby aggregate operation."""

    def test_groupby_single_agg_string(self, duckdb_engine, sample_data):
        """Test groupby with single aggregation as string."""
        result = duckdb_engine.groupby_aggregate(
            sample_data,
            group_cols=["treatment"],
            agg_funcs="COUNT(*) as cnt"
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) == 2
        assert set(pandas_result["treatment"].tolist()) == {0, 1}

    def test_groupby_multiple_agg_list(self, duckdb_engine, sample_data):
        """Test groupby with multiple aggregations as list."""
        result = duckdb_engine.groupby_aggregate(
            sample_data,
            group_cols=["center"],
            agg_funcs=["AVG(age) as avg_age", "SUM(outcome) as sum_outcome"]
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) == 3
        assert "avg_age" in pandas_result.columns
        assert "sum_outcome" in pandas_result.columns

    def test_groupby_dict_agg(self, duckdb_engine, sample_data):
        """Test groupby with dict aggregation."""
        result = duckdb_engine.groupby_aggregate(
            sample_data,
            group_cols=["treatment", "gender"],
            agg_funcs={
                "age": ["AVG", "STDDEV"],
                "outcome": "SUM"
            }
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) > 0
        assert "treatment" in pandas_result.columns
        assert "gender" in pandas_result.columns


class TestJoinOperation:
    """Test join operation."""

    def test_join_inner(self, duckdb_engine, sample_data, second_data):
        """Test inner join."""
        result = duckdb_engine.join(
            left=sample_data.head(30),
            right=second_data,
            on="patient_id",
            how="inner"
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) <= 30
        assert "severity" in pandas_result.columns
        assert "length_of_stay" in pandas_result.columns

    def test_join_left(self, duckdb_engine, sample_data, second_data):
        """Test left join."""
        result = duckdb_engine.join(
            left=sample_data,
            right=second_data.head(10),
            on="patient_id",
            how="left"
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) == 100
        assert "severity" in pandas_result.columns


class TestExecuteSQL:
    """Test execute_sql operation."""

    def test_execute_simple_query(self, duckdb_engine, sample_data):
        """Test simple SQL execution."""
        result = duckdb_engine.execute_sql(
            "SELECT treatment, COUNT(*) as cnt FROM (SELECT * FROM df) t GROUP BY treatment",
            data=sample_data
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) == 2
        assert set(pandas_result["treatment"].tolist()) == {0, 1}

    def test_execute_query_with_dataframe(self, duckdb_engine, sample_data):
        """Test SQL execution with pandas DataFrame."""
        result = duckdb_engine.execute_sql(
            "SELECT * FROM df WHERE age > @threshold",
            data=sample_data,
            parameters={"threshold": 50}
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert all(pandas_result["age"] > 50)


class TestToParquet:
    """Test to_parquet operation."""

    def test_to_parquet(self, duckdb_engine, sample_data, tmp_dir):
        """Test writing to Parquet."""
        parquet_path = os.path.join(tmp_dir, "output.parquet")

        duckdb_engine.to_parquet(sample_data, parquet_path)

        assert os.path.exists(parquet_path)
        result = pd.read_parquet(parquet_path)
        assert len(result) == 100


class TestEndToEnd:
    """End-to-end workflow tests."""

    def test_complete_etl_workflow(self, duckdb_engine, tmp_dir):
        """Test complete ETL workflow."""
        # Create test data
        df1 = pd.DataFrame({
            "id": range(1, 101),
            "value": np.random.randn(100),
            "category": np.random.choice(["A", "B", "C"], 100),
        })

        df2 = pd.DataFrame({
            "id": range(1, 101),
            "score": np.random.randint(0, 100, 100),
        })

        # Filter df1
        filtered = duckdb_engine.filter(df1, "value > 0")
        pandas_df = duckdb_engine.to_pandas(filtered)

        # Join
        joined = duckdb_engine.join(
            left=pandas_df,
            right=df2,
            on="id",
            how="inner"
        )

        # Aggregate
        result = duckdb_engine.groupby_aggregate(
            duckdb_engine.to_pandas(joined),
            group_cols=["category"],
            agg_funcs=["COUNT(*) as cnt", "AVG(score) as avg_score"]
        )
        final = duckdb_engine.to_pandas(result)

        assert len(final) > 0
        assert "category" in final.columns
        assert "cnt" in final.columns
        assert "avg_score" in final.columns


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self, duckdb_engine):
        """Test handling of empty dataframe."""
        empty_df = pd.DataFrame({"col1": [], "col2": []})
        result = duckdb_engine.execute_sql(
            "SELECT * FROM df",
            data=empty_df
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) == 0

    def test_null_values(self, duckdb_engine):
        """Test handling of null values."""
        df_with_nulls = pd.DataFrame({
            "id": [1, 2, 3, None],
            "value": [10.0, None, 30.0, 40.0],
        })
        result = duckdb_engine.execute_sql(
            "SELECT * FROM df WHERE value IS NOT NULL",
            data=df_with_nulls
        )
        pandas_result = duckdb_engine.to_pandas(result)

        assert len(pandas_result) == 3

    def test_large_filter_condition(self, duckdb_engine, sample_data):
        """Test filter with complex condition."""
        filtered = duckdb_engine.filter(
            sample_data,
            "age > 40 AND age < 70 AND (gender = 'M' OR gender = 'F') AND treatment IN (0, 1)"
        )
        result = duckdb_engine.to_pandas(filtered)

        assert all(result["age"] > 40)
        assert all(result["age"] < 70)
        assert result["gender"].isin(["M", "F"]).all()
        assert result["treatment"].isin([0, 1]).all()
