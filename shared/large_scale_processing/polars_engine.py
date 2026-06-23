"""
Polars engine adapter for large-scale data processing.

Provides high-performance data processing using Polars with lazy evaluation
and query optimization support.
"""

import polars as pl
from typing import Any, List, Optional, Union

from shared.large_scale_processing.base_engine import BaseEngine


class PolarsEngine(BaseEngine):
    """
    Polars implementation of the BaseEngine interface.

    Features:
    - Lazy frame support for query optimization
    - SQL-like filter expressions
    - Fast aggregation operations
    """

    def __init__(self):
        """Initialize Polars engine."""
        self._name = "polars"
        self._supports_gpu = True  # Polars supports GPU via GPU mode

    @property
    def name(self) -> str:
        """Return the engine name."""
        return self._name

    @property
    def supports_gpu(self) -> bool:
        """Return whether this engine supports GPU acceleration."""
        return self._supports_gpu

    def read_csv(self, file_path: str, **kwargs) -> pl.DataFrame:
        """
        Read CSV file into Polars DataFrame.

        Args:
            file_path: Path to the CSV file
            **kwargs: Additional Polars arguments (e.g., has_header, separator)

        Returns:
            pl.DataFrame object
        """
        try:
            lazy = kwargs.pop("lazy", False)
            if lazy:
                return pl.scan_csv(file_path, **kwargs).collect()
            return pl.read_csv(file_path, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV file {file_path}: {e}")

    def read_parquet(self, file_path: str, **kwargs) -> pl.DataFrame:
        """
        Read Parquet file into Polars DataFrame.

        Args:
            file_path: Path to the Parquet file
            **kwargs: Additional Polars arguments

        Returns:
            pl.DataFrame object
        """
        try:
            lazy = kwargs.pop("lazy", False)
            if lazy:
                return pl.scan_parquet(file_path, **kwargs).collect()
            return pl.read_parquet(file_path, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to read Parquet file {file_path}: {e}")

    def filter(
        self,
        df: pl.DataFrame,
        condition: Union[str, pl.DataFrame],
        **kwargs
    ) -> pl.DataFrame:
        """
        Filter rows based on condition.

        Supports simple conditions in format: "column > value"
        Also supports Polars expressions directly.

        Args:
            df: Input Polars DataFrame
            condition: Filter condition string or boolean DataFrame
            **kwargs: Additional arguments

        Returns:
            Filtered Polars DataFrame
        """
        if isinstance(condition, str):
            # Parse simple condition like "age > 30" or "gender == 'M'"
            parts = condition.split()
            if len(parts) != 3:
                raise ValueError(f"Invalid filter condition format: {condition}")

            col = parts[0]
            op = parts[1]
            val = parts[2]

            # Try to convert value to appropriate type
            try:
                if val.replace(".", "").replace("-", "").isdigit():
                    value = float(val) if "." in val else int(val)
                elif val.startswith("'") and val.endswith("'"):
                    value = val[1:-1]
                elif val.startswith('"') and val.endswith('"'):
                    value = val[1:-1]
                else:
                    value = val
            except ValueError:
                value = val

            col_expr = pl.col(col)
            if op == ">":
                return df.filter(col_expr > value)
            elif op == "<":
                return df.filter(col_expr < value)
            elif op == ">=":
                return df.filter(col_expr >= value)
            elif op == "<=":
                return df.filter(col_expr <= value)
            elif op == "==":
                return df.filter(col_expr == value)
            elif op == "!=":
                return df.filter(col_expr != value)
            else:
                raise ValueError(f"Unsupported operator: {op}")
        elif hasattr(condition, "__class__") and condition.__class__.__name__ in ("Expr", "When"):
            return df.filter(condition)
        elif isinstance(condition, pl.DataFrame):
            # Boolean mask from another DataFrame
            return df.filter(condition.to_series())
        else:
            raise ValueError(f"Unsupported condition type: {type(condition)}")

    def groupby_aggregate(
        self,
        df: pl.DataFrame,
        group_cols: List[str],
        agg_funcs: Union[str, List[str], dict],
        **kwargs
    ) -> pl.DataFrame:
        """
        Group by columns and aggregate.

        Args:
            df: Input Polars DataFrame
            group_cols: Columns to group by
            agg_funcs: Aggregation function(s) - string, list, or dict
            **kwargs: Additional arguments

        Returns:
            Aggregated Polars DataFrame
        """
        # Map aggregation function names to Polars functions
        agg_map = {
            "mean": "mean",
            "sum": "sum",
            "min": "min",
            "max": "max",
            "count": "count",
            "std": "std",
            "var": "var",
        }

        if isinstance(agg_funcs, str):
            # Single aggregation function - apply to all non-group columns
            other_cols = [c for c in df.columns if c not in group_cols]
            func_name = agg_map.get(agg_funcs, agg_funcs)
            exprs = []
            for col in other_cols:
                if func_name == "count":
                    exprs.append(pl.col(col).count().alias(f"{col}_{func_name}"))
                else:
                    exprs.append(getattr(pl.col(col), func_name)())
            return df.group_by(group_cols).agg(*exprs)

        elif isinstance(agg_funcs, dict):
            # Dict format: {"column": "function"}
            exprs = []
            for col, func in agg_funcs.items():
                func_name = agg_map.get(func, func)
                if func_name == "count":
                    exprs.append(pl.col(col).count().alias(f"{col}_{func_name}"))
                else:
                    exprs.append(getattr(pl.col(col), func_name)())
            return df.group_by(group_cols).agg(*exprs)

        elif isinstance(agg_funcs, list):
            # List of function names - apply to all non-group columns
            other_cols = [c for c in df.columns if c not in group_cols]
            exprs = []
            for col in other_cols:
                for func in agg_funcs:
                    func_name = agg_map.get(func, func)
                    if func_name == "count":
                        exprs.append(pl.col(col).count().alias(f"{col}_{func_name}"))
                    else:
                        exprs.append(getattr(pl.col(col), func_name)().alias(f"{col}_{func_name}"))
            return df.group_by(group_cols).agg(*exprs)

        return df

    def join(
        self,
        left: pl.DataFrame,
        right: pl.DataFrame,
        on: str,
        how: str = "inner",
        **kwargs
    ) -> pl.DataFrame:
        """
        Join two DataFrames.

        Args:
            left: Left Polars DataFrame
            right: Right Polars DataFrame
            on: Join key column
            how: Join type (inner, left, right, outer)
            **kwargs: Additional arguments

        Returns:
            Joined Polars DataFrame
        """
        how_map = {
            "inner": "inner",
            "left": "left",
            "right": "right",
            "outer": "full",
        }
        join_how = how_map.get(how, "inner")
        return left.join(right, on=on, how=join_how)

    def to_pandas(self, df: pl.DataFrame, **kwargs) -> Any:
        """
        Convert Polars DataFrame to pandas DataFrame.

        Args:
            df: Input Polars DataFrame
            **kwargs: Additional arguments

        Returns:
            pandas DataFrame
        """
        return df.to_pandas()

    def to_parquet(self, df: pl.DataFrame, file_path: str, **kwargs) -> None:
        """
        Write Polars DataFrame to Parquet file.

        Args:
            df: Input Polars DataFrame
            file_path: Output file path
            **kwargs: Additional arguments
        """
        df.write_parquet(file_path, **kwargs)
