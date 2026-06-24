"""
Tests for EngineSelector module.
"""

from shared.large_scale_processing import EngineSelector, ProcessingEngine


class TestProcessingEngine:
    """Test ProcessingEngine enum."""

    def test_processing_engine_values(self):
        """Test that all expected engine values exist."""
        assert ProcessingEngine.PANDAS.value == "pandas"
        assert ProcessingEngine.POLARS.value == "polars"
        assert ProcessingEngine.DUCKDB.value == "duckdb"
        assert ProcessingEngine.DASK.value == "dask"

    def test_processing_engine_count(self):
        """Test that we have exactly 4 engines."""
        assert len(ProcessingEngine) == 4


class TestEngineSelectorSelectBySize:
    """Test EngineSelector._select_by_size method."""

    def test_small_file_uses_pandas(self):
        """Files <1GB should use pandas."""
        # 500MB
        result = EngineSelector._select_by_size(500 * 1024 * 1024)
        assert result == ProcessingEngine.PANDAS

    def test_1gb_file_uses_polars(self):
        """Files 1-10GB should use polars."""
        # 5GB
        result = EngineSelector._select_by_size(5 * 1024 * 1024 * 1024)
        assert result == ProcessingEngine.POLARS

    def test_15gb_file_uses_duckdb(self):
        """Files 10-100GB should use duckdb."""
        # 50GB
        result = EngineSelector._select_by_size(50 * 1024 * 1024 * 1024)
        assert result == ProcessingEngine.DUCKDB

    def test_150gb_file_uses_dask(self):
        """Files >100GB should use dask."""
        # 150GB
        result = EngineSelector._select_by_size(150 * 1024 * 1024 * 1024)
        assert result == ProcessingEngine.DASK


class TestEngineSelectorSelectByRows:
    """Test EngineSelector._select_by_rows method."""

    def test_1000_rows_uses_pandas(self):
        """Small dataset ~1K rows should use pandas."""
        result = EngineSelector._select_by_rows(1000)
        assert result == ProcessingEngine.PANDAS

    def test_100000_rows_uses_pandas(self):
        """100K rows (~100MB) should use pandas."""
        result = EngineSelector._select_by_rows(100000)
        assert result == ProcessingEngine.PANDAS

    def test_1000000_rows_uses_polars(self):
        """1M rows (~1GB) should use polars."""
        result = EngineSelector._select_by_rows(1000000)
        assert result == ProcessingEngine.POLARS

    def test_10000000_rows_uses_duckdb(self):
        """10M rows (~11GB) should use duckdb."""
        result = EngineSelector._select_by_rows(10000000)
        assert result == ProcessingEngine.DUCKDB

    def test_50000000_rows_uses_duckdb(self):
        """50M rows (~50GB) should use duckdb."""
        result = EngineSelector._select_by_rows(50000000)
        assert result == ProcessingEngine.DUCKDB

    def test_200000000_rows_uses_dask(self):
        """200M rows (~200GB) should use dask."""
        result = EngineSelector._select_by_rows(200000000)
        assert result == ProcessingEngine.DASK


class TestEngineSelectorSelectEngine:
    """Test EngineSelector.select_engine method."""

    def test_default_uses_polars(self):
        """When no criteria provided, default to polars."""
        result = EngineSelector.select_engine()
        assert result == ProcessingEngine.POLARS

    def test_size_takes_precedence_over_rows(self):
        """When both size and rows provided, size is used."""
        # 50GB file with only 1000 rows
        result = EngineSelector.select_engine(
            estimated_rows=1000,
            file_size_bytes=50 * 1024 * 1024 * 1024
        )
        assert result == ProcessingEngine.DUCKDB

    def test_with_file_size(self):
        """Test select_engine with file_size_bytes."""
        result = EngineSelector.select_engine(file_size_bytes=500 * 1024 * 1024)
        assert result == ProcessingEngine.PANDAS

    def test_with_estimated_rows(self):
        """Test select_engine with estimated_rows."""
        result = EngineSelector.select_engine(estimated_rows=5000000)
        assert result == ProcessingEngine.POLARS


class TestEngineSelectorGetEngineInfo:
    """Test EngineSelector.get_engine_info method."""

    def test_pandas_info(self):
        """Test getting info for pandas engine."""
        info = EngineSelector.get_engine_info(ProcessingEngine.PANDAS)
        assert info["name"] == "pandas"
        assert "description" in info
        assert "use_case" in info

    def test_polars_info(self):
        """Test getting info for polars engine."""
        info = EngineSelector.get_engine_info(ProcessingEngine.POLARS)
        assert info["name"] == "Polars"

    def test_duckdb_info(self):
        """Test getting info for duckdb engine."""
        info = EngineSelector.get_engine_info(ProcessingEngine.DUCKDB)
        assert info["name"] == "DuckDB"

    def test_dask_info(self):
        """Test getting info for dask engine."""
        info = EngineSelector.get_engine_info(ProcessingEngine.DASK)
        assert info["name"] == "Dask"

    def test_unknown_engine_returns_empty_dict(self):
        """Test that unknown engine returns empty dict."""
        info = EngineSelector.get_engine_info(None)
        assert info == {}


class TestBoundaryConditions:
    """Test boundary conditions for engine selection."""

    def test_exactly_1gb(self):
        """Test boundary at exactly 1GB."""
        result = EngineSelector._select_by_size(1 * 1024 * 1024 * 1024)
        assert result == ProcessingEngine.POLARS

    def test_exactly_10gb(self):
        """Test boundary at exactly 10GB."""
        result = EngineSelector._select_by_size(10 * 1024 * 1024 * 1024)
        assert result == ProcessingEngine.DUCKDB

    def test_exactly_100gb(self):
        """Test boundary at exactly 100GB."""
        result = EngineSelector._select_by_size(100 * 1024 * 1024 * 1024)
        assert result == ProcessingEngine.DASK

    def test_just_under_1gb(self):
        """Test just under 1GB boundary."""
        result = EngineSelector._select_by_size(1 * 1024 * 1024 * 1024 - 1)
        assert result == ProcessingEngine.PANDAS

    def test_just_under_10gb(self):
        """Test just under 10GB boundary."""
        result = EngineSelector._select_by_size(10 * 1024 * 1024 * 1024 - 1)
        assert result == ProcessingEngine.POLARS

    def test_just_under_100gb(self):
        """Test just under 100GB boundary."""
        result = EngineSelector._select_by_size(100 * 1024 * 1024 * 1024 - 1)
        assert result == ProcessingEngine.DUCKDB
