"""
Tests for DaskEngine module.
"""

import numpy as np
import pandas as pd
import pytest
import tempfile
import os

from shared.large_scale_processing.dask_engine import DaskEngine


class TestDaskEngineProperties:
    """Test DaskEngine properties."""

    def test_name(self):
        """Test engine name."""
        engine = DaskEngine()
        assert engine.name == "Dask"

    def test_supports_gpu(self):
        """Test GPU support flag."""
        engine = DaskEngine()
        assert engine.supports_gpu is False


class TestDaskEngineReadCsv:
    """Test DaskEngine.read_csv method."""

    def test_read_csv_basic(self, tmp_path):
        """Test basic CSV reading."""
        # Create test CSV file
        csv_file = tmp_path / "test.csv"
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()
        result = engine.read_csv(str(csv_file))

        # Check that it returns a Dask DataFrame
        assert hasattr(result, "compute")
        pdf = result.compute()
        assert len(pdf) == 3
        assert list(pdf.columns) == ["a", "b"]

    def test_read_csv_with_blocksize(self, tmp_path):
        """Test CSV reading with custom blocksize."""
        csv_file = tmp_path / "test_blocksize.csv"
        df = pd.DataFrame({"x": range(100), "y": range(100)})
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()
        result = engine.read_csv(str(csv_file), blocksize="50KB")

        assert hasattr(result, "compute")

    def test_read_csv_with_kwargs(self, tmp_path):
        """Test CSV reading with additional kwargs."""
        csv_file = tmp_path / "test_header.csv"
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        df.to_csv(csv_file, index=False, header=True)

        engine = DaskEngine()
        result = engine.read_csv(str(csv_file), dtype={"a": "int64", "b": "int64"})

        assert hasattr(result, "compute")


class TestDaskEngineReadParquet:
    """Test DaskEngine.read_parquet method."""

    def test_read_parquet_basic(self, tmp_path):
        """Test basic Parquet reading."""
        # Create test Parquet file
        pq_file = tmp_path / "test.parquet"
        df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        df.to_parquet(pq_file, index=False)

        engine = DaskEngine()
        result = engine.read_parquet(str(pq_file))

        assert hasattr(result, "compute")
        pdf = result.compute()
        assert len(pdf) == 3


class TestDaskEngineFilter:
    """Test DaskEngine.filter method."""

    def test_filter_string_condition(self, tmp_path):
        """Test filtering with string condition."""
        csv_file = tmp_path / "filter_test.csv"
        df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [10, 20, 30, 40]})
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()
        ddf = engine.read_csv(str(csv_file))
        result = engine.filter(ddf, "a > 2")

        pdf = result.compute()
        assert len(pdf) == 2
        assert list(pdf["a"]) == [3, 4]

    def test_filter_boolean_mask(self, tmp_path):
        """Test filtering with boolean mask using Dask Series."""
        csv_file = tmp_path / "bool_filter_test.csv"
        df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [10, 20, 30, 40]})
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()
        ddf = engine.read_csv(str(csv_file))
        # Use Dask boolean mask (uncomputed)
        mask = ddf["a"] > 2
        result = engine.filter(ddf, mask)

        pdf = result.compute()
        assert len(pdf) == 2


class TestDaskEngineGroupbyAggregate:
    """Test DaskEngine.groupby_aggregate method."""

    def test_groupby_sum(self, tmp_path):
        """Test groupby with sum aggregation."""
        csv_file = tmp_path / "groupby_test.csv"
        df = pd.DataFrame({
            "category": ["A", "A", "B", "B"],
            "value": [1, 2, 3, 4]
        })
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()
        ddf = engine.read_csv(str(csv_file))
        result = engine.groupby_aggregate(ddf, ["category"], "sum")

        pdf = result.compute()
        assert len(pdf) == 2
        assert pdf["value"].sum() == 10

    def test_groupby_multiple_agg(self, tmp_path):
        """Test groupby with multiple aggregations."""
        csv_file = tmp_path / "groupby_multi_test.csv"
        df = pd.DataFrame({
            "category": ["A", "A", "B", "B"],
            "value": [1, 2, 3, 4]
        })
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()
        ddf = engine.read_csv(str(csv_file))
        result = engine.groupby_aggregate(
            ddf, ["category"], ["sum", "mean", "count"]
        )

        pdf = result.compute()
        assert "value_sum" in pdf.columns or "value" in pdf.columns


class TestDaskEngineJoin:
    """Test DaskEngine.join method."""

    def test_join_inner(self, tmp_path):
        """Test inner join."""
        left_file = tmp_path / "left.csv"
        right_file = tmp_path / "right.csv"

        left_df = pd.DataFrame({"key": ["a", "b", "c"], "left_val": [1, 2, 3]})
        right_df = pd.DataFrame({"key": ["b", "c", "d"], "right_val": [10, 20, 30]})

        left_df.to_csv(left_file, index=False)
        right_df.to_csv(right_file, index=False)

        engine = DaskEngine()
        left_ddf = engine.read_csv(str(left_file))
        right_ddf = engine.read_csv(str(right_file))

        result = engine.join(left_ddf, right_ddf, on="key", how="inner")
        pdf = result.compute()

        assert len(pdf) == 2
        assert "left_val" in pdf.columns
        assert "right_val" in pdf.columns

    def test_join_left(self, tmp_path):
        """Test left join."""
        left_file = tmp_path / "left2.csv"
        right_file = tmp_path / "right2.csv"

        left_df = pd.DataFrame({"key": ["a", "b", "c"], "left_val": [1, 2, 3]})
        right_df = pd.DataFrame({"key": ["b", "c"], "right_val": [10, 20]})

        left_df.to_csv(left_file, index=False)
        right_df.to_csv(right_file, index=False)

        engine = DaskEngine()
        left_ddf = engine.read_csv(str(left_file))
        right_ddf = engine.read_csv(str(right_file))

        result = engine.join(left_ddf, right_ddf, on="key", how="left")
        pdf = result.compute()

        assert len(pdf) == 3


class TestDaskEngineToPandas:
    """Test DaskEngine.to_pandas method."""

    def test_to_pandas_basic(self, tmp_path):
        """Test converting Dask DataFrame to pandas."""
        csv_file = tmp_path / "to_pandas_test.csv"
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()
        ddf = engine.read_csv(str(csv_file))
        result = engine.to_pandas(ddf)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ["x", "y"]


class TestDaskEngineToParquet:
    """Test DaskEngine.to_parquet method."""

    def test_to_parquet_basic(self, tmp_path):
        """Test writing to Parquet file."""
        csv_file = tmp_path / "source.csv"
        pq_file = tmp_path / "output.parquet"

        df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()
        ddf = engine.read_csv(str(csv_file))
        engine.to_parquet(ddf, str(pq_file))

        # Verify the file was created
        assert pq_file.exists()

        # Read back and verify
        result = engine.read_parquet(str(pq_file))
        pdf = result.compute()
        assert len(pdf) == 3


class TestDaskEngineIntegration:
    """Integration tests for DaskEngine."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: read -> filter -> groupby -> to_pandas."""
        csv_file = tmp_path / "workflow.csv"
        df = pd.DataFrame({
            "id": range(100),
            "category": np.random.choice(["A", "B", "C"], 100),
            "value": np.random.randint(1, 100, 100)
        })
        df.to_csv(csv_file, index=False)

        engine = DaskEngine()

        # Read
        ddf = engine.read_csv(str(csv_file))

        # Filter
        filtered = engine.filter(ddf, "value > 50")

        # Groupby
        grouped = engine.groupby_aggregate(filtered, ["category"], "sum")

        # Collect
        result = engine.to_pandas(grouped)

        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 3
