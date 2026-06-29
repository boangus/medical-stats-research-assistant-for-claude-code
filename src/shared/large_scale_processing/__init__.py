"""
Large-scale data processing module for MSRA.

Provides scalable data processing engines for datasets >1M rows:
- Polars: Fast in-memory processing (<10GB)
- DuckDB: SQL-based OLAP processing (10-100GB)
- Dask: Distributed processing (>100GB)
"""

from .base_engine import BaseEngine
from .engine_factory import EngineFactory
from .engine_selector import EngineSelector, ProcessingEngine

__all__ = ["EngineSelector", "ProcessingEngine", "BaseEngine", "EngineFactory"]
