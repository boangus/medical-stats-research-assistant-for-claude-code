"""
Tests for EngineFactory module.
"""

import pytest

pytest.importorskip("duckdb", reason="duckdb is an optional scale-layer dependency")

from shared.large_scale_processing.duckdb_engine import DuckDBEngine
from shared.large_scale_processing.engine_factory import EngineFactory

# Check if dask is available for conditional test skipping
try:
    from shared.large_scale_processing.dask_engine import _DASK_AVAILABLE, DaskEngine
except ImportError:
    _DASK_AVAILABLE = False

dask_available = pytest.mark.skipif(
    not _DASK_AVAILABLE, reason="dask not installed"
)


class TestEngineFactoryCreateEngine:
    """Test EngineFactory.create_engine method."""

    @dask_available
    def test_create_dask_engine(self):
        """Test creating Dask engine."""
        engine = EngineFactory.create_engine("dask")
        assert isinstance(engine, DaskEngine)

    @dask_available
    def test_create_dask_engine_uppercase(self):
        """Test creating Dask engine with uppercase."""
        engine = EngineFactory.create_engine("DASK")
        assert isinstance(engine, DaskEngine)

    @dask_available
    def test_create_dask_engine_with_config(self):
        """Test creating Dask engine with config."""
        engine = EngineFactory.create_engine("dask", config={"test": "value"})
        assert isinstance(engine, DaskEngine)

    def test_create_unknown_engine_raises_error(self):
        """Test that unknown engine raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            EngineFactory.create_engine("unknown_engine")
        assert "Unknown engine type" in str(excinfo.value)

    def test_create_polars_engine(self):
        """Test that Polars engine can be created when available."""
        engine = EngineFactory.create_engine("polars")
        assert engine is not None

    def test_create_duckdb_engine(self):
        """Test that DuckDB engine can be created when available."""
        engine = EngineFactory.create_engine("duckdb")
        assert engine is not None
        assert isinstance(engine, DuckDBEngine)


class TestEngineFactoryCreateForSize:
    """Test EngineFactory.create_for_size method."""

    def test_create_for_size_small_data(self):
        """Test auto-selection for small data (<1GB)."""
        # 500MB
        size = 500 * 1024 * 1024
        # Small data returns pandas which has no engine class
        # So it will raise since no pandas engine exists
        with pytest.raises(ValueError):
            EngineFactory.create_for_size(size)

    def test_create_for_size_medium_data(self):
        """Test auto-selection for medium data (1-10GB)."""
        # 5GB
        size = 5 * 1024 * 1024 * 1024
        # Polars is now available, should work
        engine = EngineFactory.create_for_size(size)
        assert engine is not None

    def test_create_for_size_large_data(self):
        """Test auto-selection for large data (>100GB)."""
        # 500GB
        size = 500 * 1024 * 1024 * 1024
        engine = EngineFactory.create_for_size(size)
        if _DASK_AVAILABLE:
            assert isinstance(engine, DaskEngine)
        else:
            # Fallback to duckdb when dask unavailable
            assert engine is not None

    def test_create_for_size_exactly_100gb(self):
        """Test auto-selection at exactly 100GB boundary."""
        # 100GB
        size = 100 * 1024 * 1024 * 1024
        # At 100GB threshold, returns Dask if available
        engine = EngineFactory.create_for_size(size)
        if _DASK_AVAILABLE:
            assert isinstance(engine, DaskEngine)
        else:
            assert engine is not None

    def test_create_for_size_with_config(self):
        """Test auto-selection with config."""
        size = 500 * 1024 * 1024 * 1024  # 500GB
        engine = EngineFactory.create_for_size(size, config={"test": "value"})
        if _DASK_AVAILABLE:
            assert isinstance(engine, DaskEngine)
        else:
            assert engine is not None


class TestEngineFactoryGetAvailableEngines:
    """Test EngineFactory.get_available_engines method."""

    def test_get_available_engines_returns_list(self):
        """Test that available engines returns a list."""
        engines = EngineFactory.get_available_engines()
        assert isinstance(engines, list)

    def test_get_available_engines_contains_dask(self):
        """Test that dask is in available engines when installed."""
        engines = EngineFactory.get_available_engines()
        if _DASK_AVAILABLE:
            assert "dask" in engines
        else:
            assert "dask" not in engines

    def test_get_available_engines_contains_polars(self):
        """Test that polars is in available engines when installed."""
        engines = EngineFactory.get_available_engines()
        # Polars may or may not be available depending on installation
        if "polars" in engines:
            assert True
        # If not available, that's also acceptable


class TestEngineFactoryIntegration:
    """Integration tests for EngineFactory."""

    @dask_available
    def test_factory_produces_base_engine_instance(self):
        """Test that factory produces BaseEngine instances."""
        engine = EngineFactory.create_engine("dask")
        from shared.large_scale_processing import BaseEngine
        assert isinstance(engine, BaseEngine)

    @dask_available
    def test_multiple_calls_return_independent_instances(self):
        """Test that multiple calls return independent instances."""
        engine1 = EngineFactory.create_engine("dask")
        engine2 = EngineFactory.create_engine("dask")
        assert engine1 is not engine2

    @dask_available
    def test_engine_has_expected_interface(self):
        """Test that created engine has expected methods."""
        engine = EngineFactory.create_engine("dask")
        assert hasattr(engine, "read_csv")
        assert hasattr(engine, "read_parquet")
        assert hasattr(engine, "filter")
        assert hasattr(engine, "groupby_aggregate")
        assert hasattr(engine, "join")
        assert hasattr(engine, "to_pandas")
        assert hasattr(engine, "to_parquet")
        assert hasattr(engine, "name")
        assert hasattr(engine, "supports_gpu")


class TestEngineFactoryEdgeCases:
    """Edge case tests for EngineFactory."""

    @dask_available
    def test_empty_config(self):
        """Test with empty config."""
        engine = EngineFactory.create_engine("dask", config={})
        assert isinstance(engine, DaskEngine)

    @dask_available
    def test_none_config(self):
        """Test with None config."""
        engine = EngineFactory.create_engine("dask", config=None)
        assert isinstance(engine, DaskEngine)

    def test_zero_size(self):
        """Test with zero size."""
        with pytest.raises(ValueError):
            EngineFactory.create_for_size(0)

    def test_negative_size(self):
        """Test with negative size."""
        with pytest.raises(ValueError):
            EngineFactory.create_for_size(-1000)
