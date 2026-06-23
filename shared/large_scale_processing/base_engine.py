"""
Base engine abstract class for unified data processing API.

Provides common interface for all processing engines:
- Polars, DuckDB, Dask, and pandas
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union


class BaseEngine(ABC):
    """
    Abstract base class for data processing engines.
    
    Defines the unified interface that all engine implementations
    must follow to ensure consistent API across different backends.
    """

    @abstractmethod
    def read_csv(self, file_path: str, **kwargs) -> Any:
        """
        Read CSV file into memory.
        
        Args:
            file_path: Path to the CSV file
            **kwargs: Additional engine-specific arguments
            
        Returns:
            DataFrame object specific to the engine
        """
        pass

    @abstractmethod
    def read_parquet(self, file_path: str, **kwargs) -> Any:
        """
        Read Parquet file into memory.
        
        Args:
            file_path: Path to the Parquet file
            **kwargs: Additional engine-specific arguments
            
        Returns:
            DataFrame object specific to the engine
        """
        pass

    @abstractmethod
    def filter(
        self,
        df: Any,
        condition: Union[str, "pandas.DataFrame"],
        **kwargs
    ) -> Any:
        """
        Filter rows based on condition.
        
        Args:
            df: Input DataFrame
            condition: Filter condition (string expression or boolean mask)
            **kwargs: Additional engine-specific arguments
            
        Returns:
            Filtered DataFrame
        """
        pass

    @abstractmethod
    def groupby_aggregate(
        self,
        df: Any,
        group_cols: List[str],
        agg_funcs: Union[str, List[str], dict],
        **kwargs
    ) -> Any:
        """
        Group by columns and aggregate.
        
        Args:
            df: Input DataFrame
            group_cols: Columns to group by
            agg_funcs: Aggregation function(s)
            **kwargs: Additional engine-specific arguments
            
        Returns:
            Aggregated DataFrame
        """
        pass

    @abstractmethod
    def join(
        self,
        left: Any,
        right: Any,
        on: str,
        how: str = "inner",
        **kwargs
    ) -> Any:
        """
        Join two DataFrames.
        
        Args:
            left: Left DataFrame
            right: Right DataFrame
            on: Join key column
            how: Join type (inner, left, right, outer)
            **kwargs: Additional engine-specific arguments
            
        Returns:
            Joined DataFrame
        """
        pass

    @abstractmethod
    def to_pandas(self, df: Any, **kwargs) -> Any:
        """
        Convert DataFrame to pandas DataFrame.
        
        Args:
            df: Input DataFrame
            **kwargs: Additional engine-specific arguments
            
        Returns:
            pandas DataFrame
        """
        pass

    @abstractmethod
    def to_parquet(self, df: Any, file_path: str, **kwargs) -> None:
        """
        Write DataFrame to Parquet file.
        
        Args:
            df: Input DataFrame
            file_path: Output file path
            **kwargs: Additional engine-specific arguments
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the engine name."""
        pass

    @property
    @abstractmethod
    def supports_gpu(self) -> bool:
        """Return whether this engine supports GPU acceleration."""
        pass
