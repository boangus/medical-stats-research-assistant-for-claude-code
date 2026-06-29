# Large-Scale Data Processing Guide

大规模数据处理引擎使用指南

---

## 快速开始

### 基础用法

```python
from shared.large_scale_processing import EngineFactory, EngineSelector

# 方式1: 自动选择引擎（基于数据大小）
engine = EngineFactory.create_for_size(file_size_bytes=5 * 1024**3)  # 5GB

# 方式2: 显式指定引擎
engine = EngineFactory.create_engine("polars")

# 读取数据
df = engine.read_csv("data/clinical_trial.csv")
df = engine.read_parquet("data/clinical_trial.parquet")

# 基础操作
filtered = engine.filter(df, "age > 30")
grouped = engine.groupby_aggregate(df, ["gender"], {"outcome": "mean"})
result = engine.join(left_df, right_df, on="patient_id")

# 转换格式
pandas_df = engine.to_pandas(df)
engine.to_parquet(df, "output.parquet")
```

### 自动引擎选择

| 数据大小 | 引擎 | 说明 |
|---------|------|------|
| <1GB | pandas | 兼容性处理 |
| 1-10GB | Polars | 快速内存处理 |
| 10-100GB | DuckDB | SQL风格OLAP |
| >100GB | Dask | 分布式处理 |

```python
# 基于文件大小自动选择
engine = EngineFactory.create_for_size(file_size_bytes=5 * 1024**3)

# 基于行数自动选择（适用未知文件大小）
engine = EngineSelector.select_engine(estimated_rows=10_000_000)
```

---

## 引擎对比表

| 特性 | Polars | DuckDB | Dask |
|------|--------|--------|------|
| **适用规模** | 1-10GB | 10-100GB | >100GB |
| **API风格** | DataFrame | SQL | DataFrame |
| **GPU支持** | ✅ | ❌ | ❌ |
| **延迟评估** | ✅ | ❌ | ✅ |
| **SQL支持** | 基础 | 完整 | 基础 |
| **并行度** | 多线程 | 多线程 | 分布式 |
| **内存效率** | 高 | 高 | 中 |
| **学习曲线** | 低 | 中 | 高 |

### 选择建议

- **小数据集 (<1GB)**: 直接使用 pandas，无需引擎切换
- **中型数据 (1-10GB)**: 推荐 Polars，性能最佳
- **大型数据 (10-100GB)**: DuckDB，SQL友好
- **超大型数据 (>100GB)**: Dask，分布式处理

---

## 性能优化技巧

### 1. 延迟评估 (Lazy Evaluation)

Polars 支持延迟评估，可自动优化查询计划：

```python
# 使用 lazy 模式
df = engine.read_csv("large_file.csv", lazy=True)
# 不实际读取，直到调用 .collect()
result = df.filter(pl.col("age") > 30).group_by("gender").agg(pl.col("outcome").mean()).collect()
```

### 2. 适当选择数据类型

```python
# 读取时指定数据类型，减少内存占用
df = pl.read_csv("data.csv", 
    dtypes={"patient_id": pl.Utf8, "age": pl.Int16, "outcome": pl.Float32})
```

### 3. 分区存储 Parquet

```python
# 写入时按分区存储，加快读取速度
df.write_parquet("output/", partition_by=["year", "month"])
```

### 4. 避免不必要的数据转换

```python
# 尽量在原引擎中完成操作，减少转换开销
engine = EngineFactory.create_engine("polars")
df = engine.read_parquet("data.parquet")
result = engine.groupby_aggregate(df, ["group"], {"value": "sum"})
# 直接在 Polars 中继续处理，避免频繁 to_pandas()
```

### 5. 使用合适的过滤条件

```python
# 尽早过滤，减少后续处理数据量
df = engine.filter(df, "age >= 18")  # 先过滤
df = engine.filter(df, "bmi < 30")    # 再过滤
```

---

## 故障排除指南

### 问题 1: ImportError - 引擎模块不可用

**错误信息**:
```
ImportError: cannot import name 'PolarsEngine' from 'shared.large_scale_processing'
```

**解决方案**:
```bash
# 安装对应引擎
pip install polars
pip install duckdb
pip install "dask[dataframe]"
```

### 问题 2: 内存不足 (OOM)

**错误信息**:
```
panics: ComputeError: Out of memory
```

**解决方案**:
1. 切换到分布式引擎 Dask
2. 分块读取数据
3. 使用延迟评估减少内存峰值

```python
# 使用 Dask 处理超大文件
engine = EngineFactory.create_engine("dask")
# Dask 自动分片处理
```

### 问题 3: 文件读取失败

**错误信息**:
```
RuntimeError: Failed to read CSV file: No such file or directory
```

**解决方案**:
1. 检查文件路径是否正确
2. 使用绝对路径而非相对路径
3. 确认文件编码（中文编码使用 `encoding="utf-8"` 或 `"gbk"`）

```python
df = engine.read_csv("data/临床数据.csv", encoding="gbk")
```

### 问题 4: 引擎选择不正确

**问题**: 自动选择的引擎不适合当前数据特征

**解决方案**: 手动指定引擎

```python
# 强制使用 Polars
engine = EngineFactory.create_engine("polars")
```

### 问题 5: SQL语法错误 (DuckDB)

**错误信息**:
```
RuntimeError: Invalid Input Error: Invalid type INT64 for column 'age'
```

**解决方案**: 确保数据类型匹配，使用 CAST 转换

```sql
SELECT CAST(age AS DOUBLE) FROM patients
```

---

## 完整工作流示例

### CSV 数据处理流程

```python
from shared.large_scale_processing import EngineFactory

# 1. 创建引擎
engine = EngineFactory.create_engine("polars")

# 2. 读取数据
df = engine.read_csv("clinical_data.csv")

# 3. 数据清洗
df = engine.filter(df, "age >= 18")
df = engine.filter(df, "bmi IS NOT NULL")

# 4. 分组统计
summary = engine.groupby_aggregate(df, ["treatment_group"], {
    "outcome": "mean",
    "adverse_events": "sum",
    "patient_id": "count"
})

# 5. 导出结果
engine.to_parquet(summary, "analysis_results.parquet")
```

### Parquet 数据处理流程

```python
from shared.large_scale_processing import EngineFactory, EngineSelector

# 1. 自动选择引擎
engine = EngineSelector.select_engine(
    file_size_bytes=50 * 1024**3  # 50GB
)
print(f"Selected engine: {engine.name}")

# 2. 读取分区 Parquet
df = engine.read_parquet("partitioned_data/", partition_by=["year"])

# 3. 多表关联
df1 = engine.read_parquet("patients.parquet")
df2 = engine.read_parquet("outcomes.parquet")
merged = engine.join(df1, df2, on="patient_id", how="left")

# 4. 转换并导出
pandas_df = engine.to_pandas(merged)
pandas_df.to_csv("final_results.csv", index=False)
```

### 分布式处理流程 (Dask)

```python
from shared.large_scale_processing import EngineFactory

# 1. 创建 Dask 引擎
engine = EngineFactory.create_engine("dask")

# 2. 读取大型 CSV
df = engine.read_csv("huge_file.csv")

# 3. 分布式计算
result = engine.groupby_aggregate(df, ["region"], {"patients": "count"})

# 4. 收集结果到内存
pandas_result = engine.to_pandas(result)
```

---

## 引擎特定配置

### Polars 配置

```python
# 启用 GPU 模式（需要 polars-gpu）
import polars as pl
pl.enable_gp()

# 设置线程数
pl.set_global_index_type(2)
```

### DuckDB 配置

```python
# DuckDB 通过 SQL 语法使用
# 不支持 filter/join 的高级引擎接口
engine = EngineFactory.create_engine("duckdb")
```

### Dask 配置

```python
# Dask 分布式配置
from dask.distributed import Client
client = Client(n_workers=4, memory_limit="8GB")

# 引擎会自动使用分布式客户端
engine = EngineFactory.create_engine("dask")
```

---

## 常见问题 (FAQ)

**Q: 如何确定我的数据应该用哪个引擎？**

A: 使用 `EngineSelector.select_engine()` 自动判断，或参考引擎对比表。

**Q: 可以在处理过程中切换引擎吗？**

A: 可以通过 `to_pandas()` 转换后使用 pandas，或通过 Parquet 中转。

**Q: Polars 和 pandas 可以混用吗？**

A: 可以，使用 `engine.to_pandas()` 和 `pl.from_pandas()` 互转。

**Q: Dask 支持 GPU 加速吗？**

A: Dask 本身不支持，但可通过 `dask-cuddf` 支持 GPU。
