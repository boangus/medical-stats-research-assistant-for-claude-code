"""
Engine selector for automatic processing engine selection.

Selects optimal processing engine based on data size:
- pandas: <1GB (compatibility layer)
- Polars: 1-10GB (fastest in-memory)
- DuckDB: 10-100GB (SQL-friendly OLAP)
- Dask: >100GB (distributed processing)
"""

from enum import Enum
from typing import Optional


class ProcessingEngine(Enum):
    """Available processing engines for large-scale data."""
    PANDAS = "pandas"
    POLARS = "polars"
    DUCKDB = "duckdb"
    DASK = "dask"


# Size thresholds in bytes
GB = 1024 * 1024 * 1024
PANDAS_THRESHOLD = 1 * GB       # <1GB
POLARS_THRESHOLD = 10 * GB       # 1-10GB
DUCKDB_THRESHOLD = 100 * GB      # 10-100GB
DASK_THRESHOLD = 100 * GB       # >100GB


class EngineSelector:
    """
    Selects optimal processing engine based on data characteristics.
    
    Selection criteria:
    - estimated_rows: Number of rows in dataset
    - file_size_bytes: Size of the data file in bytes
    - file_path: Optional file path for additional heuristics
    """

    @staticmethod
    def select_engine(
        estimated_rows: Optional[int] = None,
        file_size_bytes: Optional[int] = None,
        file_path: Optional[str] = None
    ) -> ProcessingEngine:
        """
        Select the optimal processing engine based on data characteristics.
        
        Args:
            estimated_rows: Estimated number of rows in the dataset
            file_size_bytes: Size of the data file in bytes
            file_path: Optional path to the data file
            
        Returns:
            ProcessingEngine: The recommended processing engine
        """
        if file_size_bytes is not None:
            return EngineSelector._select_by_size(file_size_bytes)
        
        if estimated_rows is not None:
            return EngineSelector._select_by_rows(estimated_rows)
        
        # Default to Polars for unknown data characteristics
        return ProcessingEngine.POLARS

    @staticmethod
    def _select_by_size(size_bytes: int) -> ProcessingEngine:
        """Select engine based on file size."""
        if size_bytes < PANDAS_THRESHOLD:
            return ProcessingEngine.PANDAS
        elif size_bytes < POLARS_THRESHOLD:
            return ProcessingEngine.POLARS
        elif size_bytes < DUCKDB_THRESHOLD:
            return ProcessingEngine.DUCKDB
        else:
            return ProcessingEngine.DASK

    @staticmethod
    def _select_by_rows(estimated_rows: int) -> ProcessingEngine:
        """
        Estimate size and select engine based on row count.
        
        Assumes average row size of ~1KB for typical tabular medical data.
        """
        # Rough estimate: ~1.1KB per row average for medical data (with overhead)
        estimated_size = int(estimated_rows * 1100)
        
        # Use size-based selection with estimated size
        return EngineSelector._select_by_size(estimated_size)

    @staticmethod
    def get_engine_info(engine: ProcessingEngine) -> dict:
        """
        Get information about a specific engine.
        
        Args:
            engine: The processing engine to get info about
            
        Returns:
            dict: Information about the engine including use cases and limitations
        """
        info = {
            ProcessingEngine.PANDAS: {
                "name": "pandas",
                "description": "Compatibility layer for small datasets",
                "use_case": "<1GB data, familiar API, simple workflows",
                "limitations": "Single-threaded, memory constraints"
            },
            ProcessingEngine.POLARS: {
                "name": "Polars",
                "description": "Fast in-memory processing",
                "use_case": "1-10GB data, performance-critical workflows",
                "limitations": "Memory must fit entire dataset"
            },
            ProcessingEngine.DUCKDB: {
                "name": "DuckDB",
                "description": "SQL-based OLAP processing",
                "use_case": "10-100GB data, SQL-centric workflows",
                "limitations": "Requires SQL expertise"
            },
            ProcessingEngine.DASK: {
                "name": "Dask",
                "description": "Distributed processing",
                "use_case": ">100GB data, distributed clusters",
                "limitations": "Setup complexity, network overhead"
            }
        }
        return info.get(engine, {})
