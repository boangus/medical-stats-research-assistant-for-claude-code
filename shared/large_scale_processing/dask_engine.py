"""
Dask engine adapter for distributed data processing.

Provides scalable distributed processing for datasets >100GB using Dask.

Note: Dask is an optional dependency. If not installed, this module
will raise ImportError when DaskEngine is instantiated, but the
module itself can be safely imported for type checking.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, List, Union

from .base_engine import BaseEngine

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import dask.dataframe as dd

try:
    import dask.dataframe as _dd
    _DASK_AVAILABLE = True
except ImportError:
    _dd = None  # type: ignore
    _DASK_AVAILABLE = False


class DaskEngine(BaseEngine):
    """
    Dask engine for distributed data processing.

    Suitable for datasets >100GB, supports parallel processing
    across multiple workers or cluster nodes.

    Raises:
        ImportError: If dask is not installed when methods are called.
    """

    def __init__(self):
        """Initialize Dask engine."""
        if not _DASK_AVAILABLE:
            raise ImportError(
                "Dask is not installed. Install it with: pip install dask[dataframe]"
            )
        self._name = "Dask"
        self._supports_gpu = False

    @property
    def name(self) -> str:
        """Return the engine name."""
        return self._name

    @property
    def supports_gpu(self) -> bool:
        """Return whether this engine supports GPU acceleration."""
        return self._supports_gpu

    def read_csv(self, file_path: str, **kwargs) -> dd.DataFrame:
        """
        Read CSV file using Dask with chunked reading.

        Args:
            file_path: Path to the CSV file
            **kwargs: Additional arguments passed to dd.read_csv
                blocksize: Chunk size for reading (default "100MB")

        Returns:
            Dask DataFrame
        """
        blocksize = kwargs.pop("blocksize", "100MB")
        return _dd.read_csv(file_path, blocksize=blocksize, **kwargs)

    def read_parquet(self, file_path: str, **kwargs) -> dd.DataFrame:
        """
        Read Parquet file using Dask.

        Args:
            file_path: Path to the Parquet file
            **kwargs: Additional arguments passed to dd.read_parquet

        Returns:
            Dask DataFrame
        """
        return _dd.read_parquet(file_path, **kwargs)

    def filter(
        self,
        df: dd.DataFrame,
        condition: Union[str, Any],
        **kwargs
    ) -> dd.DataFrame:
        """
        Filter rows based on condition.

        Args:
            df: Input Dask DataFrame
            condition: Filter condition (string expression or boolean mask)
            **kwargs: Additional arguments

        Returns:
            Filtered Dask DataFrame
        """
        if isinstance(condition, str):
            return df.query(condition, **kwargs)
        else:
            return df[condition]

    def groupby_aggregate(
        self,
        df: dd.DataFrame,
        group_cols: List[str],
        agg_funcs: Union[str, List[str], dict],
        **kwargs
    ) -> dd.DataFrame:
        """
        Group by columns and aggregate.

        Args:
            df: Input Dask DataFrame
            group_cols: Columns to group by
            agg_funcs: Aggregation function(s)
            **kwargs: Additional arguments

        Returns:
            Aggregated Dask DataFrame
        """
        return df.groupby(group_cols).agg(agg_funcs, **kwargs)

    def join(
        self,
        left: dd.DataFrame,
        right: dd.DataFrame,
        on: str,
        how: str = "inner",
        **kwargs
    ) -> dd.DataFrame:
        """
        Join two DataFrames.

        Args:
            left: Left Dask DataFrame
            right: Right Dask DataFrame
            on: Join key column
            how: Join type (inner, left, right, outer)
            **kwargs: Additional arguments

        Returns:
            Joined Dask DataFrame
        """
        return left.merge(right, on=on, how=how, **kwargs)

    def to_pandas(self, df: dd.DataFrame, **kwargs) -> Any:
        """
        Convert Dask DataFrame to pandas DataFrame.

        Args:
            df: Input Dask DataFrame
            **kwargs: Additional arguments passed to compute()

        Returns:
            pandas DataFrame
        """
        return df.compute(**kwargs)

    def to_parquet(
        self,
        df: dd.DataFrame,
        file_path: str,
        **kwargs
    ) -> None:
        """
        Write DataFrame to Parquet file.

        Args:
            df: Input Dask DataFrame
            file_path: Output file path
            **kwargs: Additional arguments passed to to_parquet
        """
        df.to_parquet(file_path, **kwargs)
