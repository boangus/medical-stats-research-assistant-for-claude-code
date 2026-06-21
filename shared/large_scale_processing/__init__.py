"""
Large-scale data processing module for MSRA.

Provides scalable data processing engines for datasets >1M rows:
- Polars: Fast in-memory processing (<10GB)
- DuckDB: SQL-based OLAP processing (10-100GB)
- Dask: Distributed processing (>100GB)
"""

from .engine_selector import EngineSelector, ProcessingEngine
from .base_engine import BaseEngine

__all__ = ["EngineSelector", "ProcessingEngine", "BaseEngine"]
