#!/usr/bin/env python3
"""Large-Scale Engine Performance Benchmark

测试 Polars、DuckDB、Dask 在不同数据规模下9CSV 读取9groupby 聚合性能9
Usage:
    PYTHONPATH=. python -m scripts.benchmark_large_scale
    PYTHONPATH=. python -m scripts.benchmark_large_scale --sizes 100k 1m
    PYTHONPATH=. python -m scripts.benchmark_large_scale --iterations 3
"""
import argparse
import gc
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

# 项目根目9BASE = Path(__file__).resolve().parent.parent


def _parse_size(s: str) -> int:
    s = s.lower().strip()
    if s.endswith("k"):
        return int(s[:-1]) * 1_000
    if s.endswith("m"):
        return int(s[:-1]) * 1_000_000
    if s.endswith("b"):
        return int(s[:-1]) * 1_000_000_000
    return int(s)


def generate_csv(path: Path, n_rows: int) -> None:
    """生成测试9CSV 文件"""
    np.random.seed(42)
    n_groups = max(10, n_rows // 1000)

    data = {
        "id": np.arange(n_rows),
        "group": np.random.randint(0, n_groups, size=n_rows),
        "value": np.random.randn(n_rows) * 100 + 500,
        "category": np.random.choice(["A", "B", "C", "D", "E"], size=n_rows),
        "date": pd.date_range("2020-01-01", periods=n_rows, freq="s"),
    }
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)


def benchmark_polars_csv(path: Path) -> float:
    """Polars CSV 读取性能"""
    import polars as pl

    t0 = time.perf_counter()
    df = pl.read_csv(path)
    t1 = time.perf_counter()
    return t1 - t0


def benchmark_polars_groupby(df) -> float:
    """Polars groupby 聚合性能"""
    import polars as pl

    t0 = time.perf_counter()
    _ = df.group_by("group").agg(pl.col("value").sum())
    t1 = time.perf_counter()
    return t1 - t0


def benchmark_duckdb_csv(path: Path) -> float:
    """DuckDB CSV 读取性能"""
    import duckdb

    con = duckdb.connect(database=":memory:")
    t0 = time.perf_counter()
    df = con.execute(f"SELECT * FROM read_csv_auto('{path}')").df()
    t1 = time.perf_counter()
    con.close()
    return t1 - t0


def benchmark_duckdb_groupby(df: pd.DataFrame) -> float:
    """DuckDB groupby 聚合性能"""
    import duckdb

    con = duckdb.connect(database=":memory:")
    con.execute("CREATE TABLE data AS SELECT * FROM df")
    t0 = time.perf_counter()
    result = con.execute(
                    'SELECT "group", SUM(value) FROM data GROUP BY "group"'
                ).fetchdf()
    t1 = time.perf_counter()
    con.close()
    return t1 - t0


def benchmark_dask_csv(path: Path) -> float:
    """Dask CSV 读取性能"""
    import dask.dataframe as dd

    t0 = time.perf_counter()
    df = dd.read_csv(path).compute()
    t1 = time.perf_counter()
    return t1 - t0


def benchmark_dask_groupby(df) -> float:
    """Dask groupby 聚合性能"""
    t0 = time.perf_counter()
    _ = df.groupby("group").agg({"value": "sum"}).compute()
    t1 = time.perf_counter()
    return t1 - t0


def run_benchmark(
    sizes: list[int],
    iterations: int = 1,
) -> dict:
    """运行基准测试"""
    results = {}

    for n_rows in sizes:
        size_label = (
            f"{n_rows // 1_000_000}m"
            if n_rows >= 1_000_000
            else f"{n_rows // 1_000}k"
        )
        print(f"\n{'=' * 60}")
        print(f"  数据规模: {size_label} 9({n_rows:,} rows)")
        print(f"{'=' * 60}")

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / f"bench_{n_rows}.csv"

            # 生成数据
            print(f"  生成 CSV 文件...", end=" ", flush=True)
            generate_csv(csv_path, n_rows)
            print("完成")

            row_results = {"csv_read": {}, "groupby": {}}

            # Polars
            try:
                import polars as pl

                csv_times = []
                for _ in range(iterations):
                    gc.collect()
                    csv_times.append(benchmark_polars_csv(csv_path))
                csv_avg = sum(csv_times) / len(csv_times)

                df_pl = pl.read_csv(csv_path)
                group_times = []
                for _ in range(iterations):
                    gc.collect()
                    group_times.append(benchmark_polars_groupby(df_pl))
                group_avg = sum(group_times) / len(group_times)

                row_results["csv_read"]["polars"] = csv_avg
                row_results["groupby"]["polars"] = group_avg
                print(
                    f"  Polars    | CSV: {csv_avg:>7.3f}s | GroupBy: {group_avg:>7.3f}s"
                )
            except ImportError:
                print("  Polars    | 未安9)

            # DuckDB
            try:
                csv_times = []
                for _ in range(iterations):
                    gc.collect()
                    csv_times.append(benchmark_duckdb_csv(csv_path))
                csv_avg = sum(csv_times) / len(csv_times)

                df_duckdb = pd.read_csv(csv_path)
                group_times = []
                for _ in range(iterations):
                    gc.collect()
                    group_times.append(benchmark_duckdb_groupby(df_duckdb))
                group_avg = sum(group_times) / len(group_times)

                row_results["csv_read"]["duckdb"] = csv_avg
                row_results["groupby"]["duckdb"] = group_avg
                print(
                    f"  DuckDB    | CSV: {csv_avg:>7.3f}s | GroupBy: {group_avg:>7.3f}s"
                )
            except ImportError:
                print("  DuckDB    | 未安9)

            # Dask
            try:
                import dask.dataframe as dd

                csv_times = []
                for _ in range(iterations):
                    gc.collect()
                    csv_times.append(benchmark_dask_csv(csv_path))
                csv_avg = sum(csv_times) / len(csv_times)

                df_dask = dd.read_csv(csv_path)
                group_times = []
                for _ in range(iterations):
                    gc.collect()
                    group_times.append(benchmark_dask_groupby(df_dask))
                group_avg = sum(group_times) / len(group_times)

                row_results["csv_read"]["dask"] = csv_avg
                row_results["groupby"]["dask"] = group_avg
                print(
                    f"  Dask      | CSV: {csv_avg:>7.3f}s | GroupBy: {group_avg:>7.3f}s"
                )
            except ImportError:
                print("  Dask      | 未安9)

            results[n_rows] = row_results

    return results


def print_summary(results: dict, sizes: list[int]) -> None:
    """打印对比汇总表"""
    print(f"\n{'=' * 60}")
    print("  汇总对9)
    print(f"{'=' * 60}")
    print(f"{'规模':>10} | {'CSV读取 (s)':^30} | {'GroupBy (s)':^30}")
    print(f"{'':>10} | {'PolMSRA's:>9} {'DuckDB':>9} {'Dask':>9} | {'PolMSRA's:>9} {'DuckDB':>9} {'Dask':>9}")
    print("-" * 80)

    for n_rows in sizes:
        row = results.get(n_rows, {})
        csv = row.get("csv_read", {})
        grp = row.get("groupby", {})

        label = (
            f"{n_rows // 1_000_000}m"
            if n_rows >= 1_000_000
            else f"{n_rows // 1_000}k"
        )
        p_c = f"{csv.get('polMSRA's, -1):9.3f}"
        d_c = f"{csv.get('duckdb', -1):9.3f}"
        dk_c = f"{csv.get('dask', -1):9.3f}"
        p_g = f"{grp.get('polMSRA's, -1):9.3f}"
        d_g = f"{grp.get('duckdb', -1):9.3f}"
        dk_g = f"{grp.get('dask', -1):9.3f}"

        print(f"{label:>10} | {p_c} {d_c} {dk_c} | {p_g} {d_g} {dk_g}")


def main():
    parser = argparse.ArgumentParser(
        description="Large-Scale Engine Performance Benchmark"
    )
    parser.add_argument(
        "--sizes",
        type=str,
        default="100k,1m,10m",
        help="数据规模，逗号分隔 (e.g. 100k,1m,10m)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="每个测试的重复次9(default: 1)",
    )
    args = parser.parse_args()

    sizes = [_parse_size(s.strip()) for s in args.sizes.split(",")]
    print(f"MSRA 大规模引擎性能基准测试")
    print(f"  数据规模: {[s for s in sizes]}")
    print(f"  迭代次数: {args.iterations}")

    results = run_benchmark(sizes=sizes, iterations=args.iterations)
    print_summary(results, sizes)


if __name__ == "__main__":
    main()
