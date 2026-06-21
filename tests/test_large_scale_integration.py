"""
Integration tests for large-scale data processing module.

Tests end-to-end workflows for CSV and Parquet processing,
including automatic engine selection.
"""

import os
import tempfile
import pytest
import pandas as pd

from shared.large_scale_processing import EngineFactory, EngineSelector, ProcessingEngine


class TestCSVWorkflow:
    """End-to-end CSV processing workflow tests."""

    @pytest.fixture
    def sample_csv_file(self):
        """Create a sample CSV file for testing."""
        data = {
            "patient_id": range(1, 101),
            "age": [25 + i % 50 for i in range(100)],
            "gender": ["M" if i % 2 == 0 else "F" for i in range(100)],
            "bmi": [18 + (i % 30) * 0.5 for i in range(100)],
            "outcome": [float(i % 10) for i in range(100)],
        }
        df = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df.to_csv(f, index=False)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_csv_read_filter_aggregate(self, sample_csv_file):
        """Test reading CSV, filtering, and aggregating."""
        # Create engine
        engine = EngineFactory.create_engine("polars")

        # Read CSV
        df = engine.read_csv(sample_csv_file)

        # Strip any whitespace from column names to handle Windows line endings
        df.columns = [c.strip() for c in df.columns]
        assert df is not None
        assert len(df) == 100

        # Filter - using Polars expression
        import polars as pl
        filtered = df.filter(pl.col("age") > 50)
        assert len(filtered) < 100

        # Aggregate
        grouped = df.group_by("gender").agg([
            pl.col("outcome").mean().alias("mean_outcome"),
            pl.col("patient_id").count().alias("count")
        ])
        assert len(grouped) == 2  # M and F

    def test_csv_to_parquet_export(self, sample_csv_file):
        """Test reading CSV and exporting to Parquet."""
        engine = EngineFactory.create_engine("polars")

        # Read
        df = engine.read_csv(sample_csv_file)

        # Export to Parquet
        parquet_path = sample_csv_file.replace(".csv", ".parquet")
        try:
            engine.to_parquet(df, parquet_path)
            assert os.path.exists(parquet_path)

            # Verify by reading back
            df2 = engine.read_parquet(parquet_path)
            assert len(df2) == len(df)
        finally:
            if os.path.exists(parquet_path):
                os.unlink(parquet_path)

    def test_csv_full_pipeline(self, sample_csv_file):
        """Test complete CSV pipeline: read -> clean -> aggregate -> export."""
        engine = EngineFactory.create_engine("polars")

        # Read
        df = engine.read_csv(sample_csv_file)

        # Strip any whitespace from column names to handle Windows line endings
        df.columns = [c.strip() for c in df.columns]

        # Filter adults only
        import polars as pl
        df_filtered = df.filter(pl.col("age") >= 18)

        # Group and aggregate
        result = df_filtered.group_by("gender").agg([
            pl.col("age").mean().alias("mean_age"),
            pl.col("bmi").mean().alias("mean_bmi"),
            pl.col("outcome").count().alias("count_outcome"),
            pl.col("patient_id").count().alias("n")
        ])

        # Convert to pandas
        pandas_result = engine.to_pandas(result)

        # Verify structure
        assert "gender" in pandas_result.columns
        assert "mean_age" in pandas_result.columns
        assert "count_outcome" in pandas_result.columns
        assert len(pandas_result) == 2


class TestParquetWorkflow:
    """End-to-end Parquet processing workflow tests."""

    @pytest.fixture
    def sample_parquet_file(self):
        """Create a sample Parquet file for testing."""
        data = {
            "patient_id": range(1, 101),
            "treatment": ["A" if i % 2 == 0 else "B" for i in range(100)],
            "visit_date": ["2024-01-01" for _ in range(100)],
            "value": [float(i) for i in range(100)],
        }
        df = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            df.to_parquet(f, index=False)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def second_parquet_file(self):
        """Create a second sample Parquet file for join tests."""
        data = {
            "patient_id": range(1, 101),
            "outcome": [float(i % 5) for i in range(100)],
            "adverse_events": [i % 3 for i in range(100)],
        }
        df = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            df.to_parquet(f, index=False)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_parquet_read_and_aggregate(self, sample_parquet_file):
        """Test reading Parquet and aggregating."""
        engine = EngineFactory.create_engine("polars")

        # Read
        df = engine.read_parquet(sample_parquet_file)
        assert df is not None
        assert len(df) == 100

        # Aggregate
        import polars as pl
        result = df.group_by("treatment").agg([
            pl.col("value").mean().alias("mean_value"),
            pl.col("patient_id").count().alias("n")
        ])
        assert len(result) == 2

    def test_parquet_join_workflow(self, sample_parquet_file, second_parquet_file):
        """Test joining two Parquet files."""
        engine = EngineFactory.create_engine("polars")

        # Read both files
        df1 = engine.read_parquet(sample_parquet_file)
        df2 = engine.read_parquet(second_parquet_file)

        # Join
        joined = df1.join(df2, on="patient_id", how="inner")

        # Verify
        assert len(joined) == 100
        assert "outcome" in joined.columns
        assert "adverse_events" in joined.columns

    def test_parquet_to_pandas_conversion(self, sample_parquet_file):
        """Test converting Parquet to pandas DataFrame."""
        engine = EngineFactory.create_engine("polars")

        # Read with Polars
        df = engine.read_parquet(sample_parquet_file)

        # Convert to pandas
        pandas_df = engine.to_pandas(df)

        # Verify type
        assert isinstance(pandas_df, pd.DataFrame)
        assert len(pandas_df) == len(df)


class TestAutomaticEngineSelection:
    """Tests for automatic engine selection based on data characteristics."""

    def test_select_engine_by_size_small(self):
        """Test engine selection for small files (<1GB)."""
        # 500MB
        engine_type = EngineSelector.select_engine(file_size_bytes=500 * 1024 * 1024)
        assert engine_type == ProcessingEngine.PANDAS

    def test_select_engine_by_size_medium(self):
        """Test engine selection for medium files (1-10GB)."""
        # 5GB
        engine_type = EngineSelector.select_engine(file_size_bytes=5 * 1024 * 1024 * 1024)
        assert engine_type == ProcessingEngine.POLARS

    def test_select_engine_by_size_large(self):
        """Test engine selection for large files (10-100GB)."""
        # 50GB
        engine_type = EngineSelector.select_engine(file_size_bytes=50 * 1024 * 1024 * 1024)
        assert engine_type == ProcessingEngine.DUCKDB

    def test_select_engine_by_size_very_large(self):
        """Test engine selection for very large files (>100GB)."""
        # 150GB
        engine_type = EngineSelector.select_engine(file_size_bytes=150 * 1024 * 1024 * 1024)
        assert engine_type == ProcessingEngine.DASK

    def test_select_engine_by_rows_small(self):
        """Test engine selection by row count for small data."""
        # 1000 rows ~ 1MB
        engine_type = EngineSelector.select_engine(estimated_rows=1000)
        assert engine_type == ProcessingEngine.PANDAS

    def test_select_engine_by_rows_medium(self):
        """Test engine selection by row count for medium data."""
        # 1M rows ~ 1GB
        engine_type = EngineSelector.select_engine(estimated_rows=1_000_000)
        assert engine_type == ProcessingEngine.POLARS

    def test_select_engine_by_rows_large(self):
        """Test engine selection by row count for large data."""
        # 10M rows ~ 11GB
        engine_type = EngineSelector.select_engine(estimated_rows=10_000_000)
        assert engine_type == ProcessingEngine.DUCKDB

    def test_select_engine_by_rows_very_large(self):
        """Test engine selection by row count for very large data."""
        # 200M rows ~ 200GB
        engine_type = EngineSelector.select_engine(estimated_rows=200_000_000)
        assert engine_type == ProcessingEngine.DASK

    def test_select_engine_default(self):
        """Test default engine selection when no criteria provided."""
        # Default should be Polars
        engine_type = EngineSelector.select_engine()
        assert engine_type == ProcessingEngine.POLARS

    def test_select_engine_size_takes_precedence(self):
        """Test that file size takes precedence over row count."""
        # 50GB file with only 1000 rows should use DUCKDB not PANDAS
        engine_type = EngineSelector.select_engine(
            estimated_rows=1000,
            file_size_bytes=50 * 1024 * 1024 * 1024
        )
        assert engine_type == ProcessingEngine.DUCKDB

    def test_create_engine_for_size_small(self):
        """Test creating engine for small data."""
        # This will raise ValueError since pandas doesn't have an engine class
        with pytest.raises(ValueError):
            EngineFactory.create_for_size(500 * 1024 * 1024)

    def test_create_engine_for_size_medium(self):
        """Test creating engine for medium data."""
        # 5GB should create Polars
        try:
            engine = EngineFactory.create_for_size(5 * 1024 * 1024 * 1024)
            assert engine is not None
        except ValueError:
            # Polars might not be installed, which is acceptable
            pytest.skip("Polars not available")

    def test_create_engine_for_size_large(self):
        """Test creating engine for large data."""
        # 150GB should create Dask
        engine = EngineFactory.create_for_size(150 * 1024 * 1024 * 1024)
        assert engine is not None
        assert engine.name.lower() == "dask"

    def test_get_engine_info(self):
        """Test getting engine information."""
        info = EngineSelector.get_engine_info(ProcessingEngine.POLARS)
        assert info["name"] == "Polars"
        assert "use_case" in info
        assert "limitations" in info

        info = EngineSelector.get_engine_info(ProcessingEngine.DASK)
        assert info["name"] == "Dask"
        assert "use_case" in info


class TestEngineInterface:
    """Tests to verify all engines implement the expected interface."""

    def test_polars_engine_interface(self):
        """Test that Polars engine implements BaseEngine interface."""
        try:
            engine = EngineFactory.create_engine("polars")
        except ValueError:
            pytest.skip("Polars not available")

        # Check required methods exist
        assert hasattr(engine, "read_csv")
        assert hasattr(engine, "read_parquet")
        assert hasattr(engine, "filter")
        assert hasattr(engine, "groupby_aggregate")
        assert hasattr(engine, "join")
        assert hasattr(engine, "to_pandas")
        assert hasattr(engine, "to_parquet")
        assert hasattr(engine, "name")
        assert hasattr(engine, "supports_gpu")

    def test_dask_engine_interface(self):
        """Test that Dask engine implements BaseEngine interface."""
        engine = EngineFactory.create_engine("dask")

        # Check required methods exist
        assert hasattr(engine, "read_csv")
        assert hasattr(engine, "read_parquet")
        assert hasattr(engine, "filter")
        assert hasattr(engine, "groupby_aggregate")
        assert hasattr(engine, "join")
        assert hasattr(engine, "to_pandas")
        assert hasattr(engine, "to_parquet")
        assert hasattr(engine, "name")
        assert hasattr(engine, "supports_gpu")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
