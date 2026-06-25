"""
Tests for PolarsEngine adapter.
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

pl = pytest.importorskip("polars", reason="polars is an optional scale-layer dependency")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared.large_scale_processing.polars_engine import PolarsEngine


class TestPolarsEngineProperties:
    """Test PolarsEngine properties."""

    def test_engine_name(self):
        """Test engine name is 'polMSRA's."""
        engine = PolarsEngine()
        assert engine.name == "polars"

    def test_supports_gpu(self):
        """Test GPU support property."""
        engine = PolarsEngine()
        assert engine.supports_gpu is True


class TestPolarsEngineReadCSV:
    """Test read_csv functionality."""

    def test_read_csv_basic(self, tmp_dir):
        """Test reading a basic CSV file."""
        # Create test CSV
        csv_path = os.path.join(tmp_dir, "test.csv")
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [4, 5, 6],
            "c": ["x", "y", "z"]
        })
        df.to_csv(csv_path, index=False)

        engine = PolarsEngine()
        result = engine.read_csv(csv_path)

        assert isinstance(result, pl.DataFrame)
        assert result.shape == (3, 3)
        assert result.columns == ["a", "b", "c"]

    def test_read_csv_with_types(self, tmp_dir):
        """Test reading CSV with proper type inference."""
        csv_path = os.path.join(tmp_dir, "test_types.csv")
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"]
        })
        df.to_csv(csv_path, index=False)

        engine = PolarsEngine()
        result = engine.read_csv(csv_path)

        assert result["int_col"].dtype == pl.Int64
        assert result["float_col"].dtype == pl.Float64
        assert result["str_col"].dtype == pl.Utf8


class TestPolarsEngineReadParquet:
    """Test read_parquet functionality."""

    def test_read_parquet_basic(self, tmp_dir):
        """Test reading a basic Parquet file."""
        parquet_path = os.path.join(tmp_dir, "test.parquet")
        df = pd.DataFrame({
            "x": [10, 20, 30],
            "y": [100, 200, 300]
        })
        df.to_parquet(parquet_path, index=False)

        engine = PolarsEngine()
        result = engine.read_parquet(parquet_path)

        assert isinstance(result, pl.DataFrame)
        assert result.shape == (3, 2)


class TestPolarsEngineFilter:
    """Test filter functionality."""

    def test_filter_greater_than(self, tmp_dir):
        """Test filtering with > operator."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        result = engine.filter(df, "age > 25")

        assert result.shape == (2, 2)
        assert "Bob" in result["name"].to_list()
        assert "Charlie" in result["name"].to_list()

    def test_filter_less_than(self, tmp_dir):
        """Test filtering with < operator."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        result = engine.filter(df, "age < 30")

        assert result.shape == (1, 2)
        assert "Alice" in result["name"].to_list()

    def test_filter_greater_than_or_equal(self, tmp_dir):
        """Test filtering with >= operator."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        result = engine.filter(df, "age >= 30")

        assert result.shape == (2, 2)

    def test_filter_less_than_or_equal(self, tmp_dir):
        """Test filtering with <= operator."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        result = engine.filter(df, "age <= 30")

        assert result.shape == (2, 2)

    def test_filter_equal_string(self, tmp_dir):
        """Test filtering with == operator on strings."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "gender": ["F", "M", "M"]
        })

        result = engine.filter(df, "gender == 'M'")

        assert result.shape == (2, 2)
        assert "Bob" in result["name"].to_list()
        assert "Charlie" in result["name"].to_list()

    def test_filter_not_equal(self, tmp_dir):
        """Test filtering with != operator."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        result = engine.filter(df, "age != 30")

        assert result.shape == (2, 2)
        assert "Alice" in result["name"].to_list()
        assert "Charlie" in result["name"].to_list()

    def test_filter_with_float_value(self, tmp_dir):
        """Test filtering with float value."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "name": ["A", "B", "C"],
            "score": [1.5, 2.5, 3.5]
        })

        result = engine.filter(df, "score > 2.0")

        assert result.shape == (2, 2)

    def test_filter_with_invalid_format_raises(self, tmp_dir):
        """Test that invalid filter format raises error."""
        engine = PolarsEngine()
        df = pl.DataFrame({"a": [1, 2, 3]})

        with pytest.raises(ValueError):
            engine.filter(df, "invalid filter")

    def test_filter_with_polars_expr(self, tmp_dir):
        """Test filtering with Polars expression directly."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        result = engine.filter(df, pl.col("age") > 25)

        assert result.shape == (2, 2)


class TestPolarsEngineGroupByAggregate:
    """Test groupby_aggregate functionality."""

    def test_groupby_mean(self, tmp_dir):
        """Test groupby with mean aggregation."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B"],
            "value": [10, 20, 30, 40]
        })

        result = engine.groupby_aggregate(df, ["group"], "mean")

        assert result.shape == (2, 2)
        # Check that both groups are present (order may vary)
        assert set(result["group"].to_list()) == {"A", "B"}

    def test_groupby_sum(self, tmp_dir):
        """Test groupby with sum aggregation."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B"],
            "value": [10, 20, 30, 40]
        })

        result = engine.groupby_aggregate(df, ["group"], "sum")

        assert result.shape == (2, 2)

    def test_groupby_min(self, tmp_dir):
        """Test groupby with min aggregation."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B"],
            "value": [10, 20, 30, 40]
        })

        result = engine.groupby_aggregate(df, ["group"], "min")

        assert result.shape == (2, 2)

    def test_groupby_max(self, tmp_dir):
        """Test groupby with max aggregation."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B"],
            "value": [10, 20, 30, 40]
        })

        result = engine.groupby_aggregate(df, ["group"], "max")

        assert result.shape == (2, 2)

    def test_groupby_count(self, tmp_dir):
        """Test groupby with count aggregation."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B", "C"],
            "value": [10, 20, 30, 40, 50]
        })

        result = engine.groupby_aggregate(df, ["group"], "count")

        assert result.shape == (3, 2)

    def test_groupby_std(self, tmp_dir):
        """Test groupby with std aggregation."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B"],
            "value": [10.0, 20.0, 30.0, 40.0]
        })

        result = engine.groupby_aggregate(df, ["group"], "std")

        assert result.shape == (2, 2)

    def test_groupby_var(self, tmp_dir):
        """Test groupby with var aggregation."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B"],
            "value": [10.0, 20.0, 30.0, 40.0]
        })

        result = engine.groupby_aggregate(df, ["group"], "var")

        assert result.shape == (2, 2)

    def test_groupby_dict_agg(self, tmp_dir):
        """Test groupby with dict aggregation (multiple columns/functions)."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B"],
            "value1": [10, 20, 30, 40],
            "value2": [100, 200, 300, 400]
        })

        result = engine.groupby_aggregate(df, ["group"], {"value1": "mean", "value2": "sum"})

        assert result.shape == (2, 3)

    def test_groupby_list_agg(self, tmp_dir):
        """Test groupby with list aggregation (multiple functions)."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "group": ["A", "A", "B", "B"],
            "value": [10, 20, 30, 40]
        })

        result = engine.groupby_aggregate(df, ["group"], ["mean", "sum", "count"])

        assert result.shape == (2, 4)  # group + 3 agg functions


class TestPolarsEngineJoin:
    """Test join functionality."""

    def test_join_inner(self, tmp_dir):
        """Test inner join."""
        engine = PolarsEngine()
        left = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"]
        })
        right = pl.DataFrame({
            "id": [1, 2, 4],
            "score": [85, 90, 95]
        })

        result = engine.join(left, right, on="id", how="inner")

        assert result.shape == (2, 3)
        assert "name" in result.columns
        assert "score" in result.columns

    def test_join_left(self, tmp_dir):
        """Test left join."""
        engine = PolarsEngine()
        left = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"]
        })
        right = pl.DataFrame({
            "id": [1, 2, 4],
            "score": [85, 90, 95]
        })

        result = engine.join(left, right, on="id", how="left")

        assert result.shape == (3, 3)

    def test_join_right(self, tmp_dir):
        """Test right join."""
        engine = PolarsEngine()
        left = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"]
        })
        right = pl.DataFrame({
            "id": [1, 2, 4],
            "score": [85, 90, 95]
        })

        result = engine.join(left, right, on="id", how="right")

        assert result.shape == (3, 3)

    def test_join_outer(self, tmp_dir):
        """Test outer join."""
        engine = PolarsEngine()
        left = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"]
        })
        right = pl.DataFrame({
            "id": [1, 2, 4],
            "score": [85, 90, 95]
        })

        result = engine.join(left, right, on="id", how="outer")

        # Outer join keeps all columns; id column appears once, others twice
        assert result.shape[0] == 4  # All 4 rows from outer join
        assert "name" in result.columns
        assert "score" in result.columns


class TestPolarsEngineToPandas:
    """Test to_pandas functionality."""

    def test_to_pandas_basic(self, tmp_dir):
        """Test converting Polars DataFrame to pandas."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "a": [1, 2, 3],
            "b": ["x", "y", "z"]
        })

        result = engine.to_pandas(df)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 2)
        assert list(result.columns) == ["a", "b"]


class TestPolarsEngineToParquet:
    """Test to_parquet functionality."""

    def test_to_parquet_basic(self, tmp_dir):
        """Test writing DataFrame to Parquet."""
        engine = PolarsEngine()
        df = pl.DataFrame({
            "x": [1, 2, 3],
            "y": [10, 20, 30]
        })
        parquet_path = os.path.join(tmp_dir, "output.parquet")

        engine.to_parquet(df, parquet_path)

        assert os.path.exists(parquet_path)

        # Verify we can read it back
        result = pl.read_parquet(parquet_path)
        assert result.shape == (3, 2)


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_read_filter_groupby_to_pandas(self, tmp_dir):
        """Test complete workflow: read -> filter -> groupby -> pandas."""
        # Create test CSV
        csv_path = os.path.join(tmp_dir, "workflow.csv")
        df = pd.DataFrame({
            "patient_id": range(1, 101),
            "age": np.random.normal(55, 10, 100).astype(int),
            "gender": np.random.choice(["M", "F"], 100),
            "treatment": np.random.choice([0, 1], 100),
            "outcome": np.random.binomial(1, 0.3, 100)
        })
        df.to_csv(csv_path, index=False)

        engine = PolarsEngine()

        # Read CSV
        data = engine.read_csv(csv_path)

        # Filter
        filtered = engine.filter(data, "age > 50")

        # Group by
        grouped = engine.groupby_aggregate(filtered, ["treatment"], {"outcome": "mean"})

        # Convert to pandas
        result = engine.to_pandas(grouped)

        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == 2  # Two treatment groups

    def test_csv_to_parquet_workflow(self, tmp_dir):
        """Test CSV to Parquet conversion workflow."""
        csv_path = os.path.join(tmp_dir, "source.csv")
        parquet_path = os.path.join(tmp_dir, "output.parquet")

        df = pd.DataFrame({
            "id": range(1, 51),
            "value": np.random.randn(50)
        })
        df.to_csv(csv_path, index=False)

        engine = PolarsEngine()

        # Read CSV and write Parquet
        data = engine.read_csv(csv_path)
        engine.to_parquet(data, parquet_path)

        # Read Parquet back
        result = engine.read_parquet(parquet_path)

        assert result.shape == (50, 2)
