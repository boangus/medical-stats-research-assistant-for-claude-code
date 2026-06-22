"""
DuckDB engine adapter for large-scale data processing.

Provides SQL-based OLAP processing using DuckDB's in-memory database.
Optimized for complex analytical queries on datasets 10-100GB.
"""

import duckdb
import pandas as pd
from typing import Any, List, Optional, Union

from .base_engine import BaseEngine


class DuckDBEngine(BaseEngine):
    """
    DuckDB implementation of BaseEngine.

    Uses an in-memory DuckDB database for SQL-based analytical processing.
    Supports complex OLAP queries with high performance.
    """

    def __init__(self, database: Optional[Union[str, dict]] = None):
        """
        Initialize DuckDB engine.

        Args:
            database: Database path, ':memory:' for in-memory database, or config dict
        """
        # Handle config dict passed from EngineFactory
        if isinstance(database, dict):
            database = database.get('database', ':memory:')
        elif database is None:
            database = ':memory:'

        self._conn = duckdb.connect(database)
        self._database = database

    def _ensure_relation(self, data: Any, table_name: str = "temp_table") -> Any:
        """
        Ensure data is registered as a DuckDB relation.

        Args:
            data: DataFrame, dict of lists, or relation
            table_name: Name for registered table

        Returns:
            DuckDB relation
        """
        if isinstance(data, dict):
            df = pd.DataFrame(data)
            self._conn.register(table_name, df)
            return self._conn.table(table_name)
        elif isinstance(data, pd.DataFrame):
            self._conn.register(table_name, data)
            return self._conn.table(table_name)
        elif hasattr(data, "fetch_df"):
            return data
        return data

    def read_csv(self, file_path: str, **kwargs) -> Any:
        """
        Read CSV file into DuckDB.

        Args:
            file_path: Path to the CSV file
            **kwargs: Additional arguments (e.g., header, delimiter)

        Returns:
            DuckDB relation object
        """
        table_name = kwargs.pop("table_name", "read_csv_table")
        sep = kwargs.pop("sep", ",")
        header = kwargs.pop("header", True)

        rel = self._conn.read_csv(file_path, header=header, sep=sep, **kwargs)
        return rel

    def read_parquet(self, file_path: str, **kwargs) -> Any:
        """
        Read Parquet file into DuckDB.

        Args:
            file_path: Path to the Parquet file
            **kwargs: Additional engine-specific arguments

        Returns:
            DuckDB relation object
        """
        rel = self._conn.read_parquet(file_path, **kwargs)
        return rel

    def filter(
        self,
        df: Any,
        condition: Union[str, Any],
        **kwargs
    ) -> Any:
        """
        Filter rows using SQL WHERE clause.

        Args:
            df: Input DataFrame (DuckDB relation, pandas DataFrame, or dict)
            condition: Filter condition as SQL WHERE clause string
            **kwargs: Additional engine-specific arguments

        Returns:
            Filtered pandas DataFrame
        """
        table_name = kwargs.pop("table_name", "filter_table")
        if isinstance(df, dict):
            df = pd.DataFrame(df)
        if isinstance(df, pd.DataFrame):
            self._conn.register(table_name, df)
            result = self._conn.execute(
                f"SELECT * FROM {table_name} WHERE {condition}"
            ).fetch_df()
            return result
        # For DuckDB relations
        if hasattr(df, "filter"):
            result = df.filter(condition)
            if hasattr(result, "fetch_df"):
                return result.fetch_df()
            return result
        return df

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
            df: Input DataFrame (pandas DataFrame, dict, or DuckDB relation)
            group_cols: Columns to group by
            agg_funcs: Aggregation function(s) - can be string, list, or dict
            **kwargs: Additional engine-specific arguments

        Returns:
            Aggregated pandas DataFrame
        """
        table_name = kwargs.pop("table_name", "agg_table")

        if isinstance(df, dict):
            df = pd.DataFrame(df)
        if isinstance(df, pd.DataFrame):
            self._conn.register(table_name, df)

        group_cols_str = ", ".join(group_cols)

        if isinstance(agg_funcs, str):
            query = f"SELECT {group_cols_str}, {agg_funcs} FROM {table_name} GROUP BY {group_cols_str}"
            return self._conn.execute(query).fetch_df()
        elif isinstance(agg_funcs, list):
            agg_str = ", ".join(agg_funcs)
            query = f"SELECT {group_cols_str}, {agg_str} FROM {table_name} GROUP BY {group_cols_str}"
            return self._conn.execute(query).fetch_df()
        elif isinstance(agg_funcs, dict):
            agg_parts = []
            for col, funcs in agg_funcs.items():
                if isinstance(funcs, str):
                    agg_parts.append(f"{funcs}({col}) as {col}_{funcs}")
                else:
                    for func in funcs:
                        agg_parts.append(f"{func}({col}) as {col}_{func}")
            agg_str = ", ".join(agg_parts)
            query = f"SELECT {group_cols_str}, {agg_str} FROM {table_name} GROUP BY {group_cols_str}"
            return self._conn.execute(query).fetch_df()

        return df.groupby(group_cols).agg(agg_funcs)

    def join(
        self,
        left: Any,
        right: Any,
        on: str,
        how: str = "inner",
        **kwargs
    ) -> Any:
        """
        Join two DataFrames using SQL.

        Args:
            left: Left DataFrame (pandas DataFrame, dict, or DuckDB relation)
            right: Right DataFrame (pandas DataFrame, dict, or DuckDB relation)
            on: Join key column
            how: Join type (inner, left, right, outer)
            **kwargs: Additional engine-specific arguments

        Returns:
            Joined pandas DataFrame
        """
        left_name = kwargs.pop("left_name", "left_table")
        right_name = kwargs.pop("right_name", "right_table")

        if isinstance(left, dict):
            left = pd.DataFrame(left)
        if isinstance(right, dict):
            right = pd.DataFrame(right)
        if isinstance(left, pd.DataFrame):
            self._conn.register(left_name, left)
        if isinstance(right, pd.DataFrame):
            self._conn.register(right_name, right)

        how_upper = how.upper()
        if how_upper not in ["INNER", "LEFT", "RIGHT", "OUTER", "ANTI", "SEMI"]:
            how_upper = "INNER"

        query = f"SELECT * FROM {left_name} {how_upper} JOIN {right_name} ON {left_name}.{on} = {right_name}.{on}"
        return self._conn.execute(query).fetch_df()

    def execute_sql(self, query: str, data: Any = None, **kwargs) -> Any:
        """
        Execute raw SQL query.

        Args:
            query: SQL query string
            data: Optional pandas DataFrame to use as input
            **kwargs: Additional engine-specific arguments (parameters for query)

        Returns:
            Query result as pandas DataFrame
        """
        if data is not None:
            if isinstance(data, dict):
                data = pd.DataFrame(data)
            self._conn.register("input_data", data)

            # Replace 'df' in query with 'input_data'
            query = query.replace("FROM df", "FROM input_data")
            query = query.replace("SELECT * FROM input_data", "SELECT * FROM input_data")

        parameters = kwargs.pop("parameters", None)
        if parameters is not None:
            if isinstance(parameters, dict):
                for key, value in parameters.items():
                    query = query.replace(f"@{key}", str(value))
            result = self._conn.execute(query).fetch_df()
        else:
            result = self._conn.execute(query, **kwargs).fetch_df()
        return result

    def to_pandas(self, df: Any, **kwargs) -> Any:
        """
        Convert DataFrame to pandas DataFrame.

        Args:
            df: Input DataFrame (DuckDB relation or pandas DataFrame)
            **kwargs: Additional engine-specific arguments

        Returns:
            pandas DataFrame
        """
        # Already a pandas DataFrame
        if isinstance(df, pd.DataFrame):
            return df
        # DuckDB relation - use fetch_df
        if hasattr(df, "fetch_df"):
            return df.fetch_df()
        # DuckDB relation with to_pandas
        if hasattr(df, "to_pandas"):
            result = df.to_pandas()
            if isinstance(result, pd.DataFrame):
                return result
            return df.fetch_df()
        return df

    def to_parquet(self, df: Any, file_path: str, **kwargs) -> None:
        """
        Write DataFrame to Parquet file.

        Args:
            df: Input DataFrame
            file_path: Output file path
            **kwargs: Additional engine-specific arguments
        """
        pandas_df = self.to_pandas(df)
        pandas_df.to_parquet(file_path, **kwargs)

    @property
    def name(self) -> str:
        """Return the engine name."""
        return "duckdb"

    @property
    def supports_gpu(self) -> bool:
        """Return whether this engine supports GPU acceleration."""
        return False

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
