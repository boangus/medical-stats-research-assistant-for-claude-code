# 生物信息学模块 API 参考

> **版本**: v1.0.0 | **日期**: 2026-06-26 | **状态**: Stable
> **模块**: Bioinformatics | **命令**: `/bio`

---

## 目录

- [ScRNASeqLoader — 单细胞数据加载器](#scrnaseqloader)
- [SingleCellQC — 单细胞质量控制](#singlecellqc)
- [DimensionalityReduction — 降维分析](#dimensionalityreduction)
- [DifferentialExpression — 差异表达分析](#differentialexpression)
- [PathwayEnrichment — 通路富集分析](#pathwayenrichment)
- [BatchCorrector — 批次校正](#batchcorrector)
- [BioQualityGateChecker — 质量门闸](#bioqualitygatechecker)

---

## ScRNASeqLoader

> 单细胞 RNA-seq 数据加载器，支持 10x MTX/H5、CSV 表达矩阵和 FASTA 序列文件。

**签名**:

```python
ScRNASeqLoader()
```

**方法**:

### `read_10x_mtx`

```python
read_10x_mtx(mtx_dir: str, var_names: str = "gene_symbols", cache: bool = True) -> AnnData
```

读取 10x Genomics MTX 格式数据。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| mtx_dir | str | — | 必填，10x 输出目录（含 matrix.mtx, features.tsv, barcodes.tsv） |
| var_names | str | "gene_symbols" | 基因名类型（"gene_symbols" 或 "gene_ids"） |
| cache | bool | True | 是否缓存 |

**返回值**: `AnnData` — 单细胞表达矩阵对象

**示例**:

```python
from msra_modules.bioinformatics import ScRNASeqLoader

loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("data/pbmc_10x/")
print(f"细胞数: {adata.shape[0]}, 基因数: {adata.shape[1]}")
```

**异常**: `FileNotFoundError` — 目录不存在；`ImportError` — scanpy 未安装

### `read_10x_h5`

```python
read_10x_h5(h5_path: str, genome: Optional[str] = None) -> AnnData
```

读取 10x Genomics H5 格式数据。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| h5_path | str | — | 必填，H5 文件路径 |
| genome | Optional[str] | None | 基因组名称（可选） |

**返回值**: `AnnData`

### `read_csv`

```python
read_csv(csv_path: str, **kwargs) -> AnnData
```

读取 CSV 格式表达矩阵，`**kwargs` 传递给 `pandas.read_csv`。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| csv_path | str | — | 必填，CSV 文件路径 |
| **kwargs | — | — | 传递给 pandas.read_csv 的参数 |

**返回值**: `AnnData`

### `read_fasta`

```python
read_fasta(fasta_path: str) -> List[SeqRecord]
```

读取 FASTA 序列文件（需安装 Biopython）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| fasta_path | str | — | 必填，FASTA 文件路径 |

**返回值**: `List[SeqRecord]` — Biopython 序列记录列表

**异常**: `ImportError` — Biopython 未安装

### `get_metadata`

```python
get_metadata() -> Dict
```

获取当前已加载数据的元数据。

**返回值**: `Dict` — 包含 `n_cells`、`n_genes`、`obs_columns`、`var_columns`、`is_sparse`

### 便捷函数

```python
from msra_modules.bioinformatics import read_10x_mtx
adata = read_10x_mtx("data/pbmc_10x/")
```

---

## SingleCellQC

> 单细胞质量控制，支持基于基因数、线粒体百分比等指标的细胞/基因过滤。

**签名**:

```python
SingleCellQC(min_genes: int = 200, max_genes: int = 5000, max_pct_mito: float = 20.0, min_cells: int = 3)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| min_genes | int | 200 | 每个细胞最少基因数 |
| max_genes | int | 5000 | 每个细胞最多基因数 |
| max_pct_mito | float | 20.0 | 最大线粒体基因百分比 |
| min_cells | int | 3 | 每个基因最少细胞数 |

**方法**:

### `compute_qc_metrics`

```python
compute_qc_metrics(adata: AnnData) -> AnnData
```

计算 QC 指标（标记线粒体基因、计算 n_genes_by_counts、pct_counts_mt 等），原地修改并返回。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |

**返回值**: `AnnData` — 带有 QC 指标的 AnnData

### `filter_cells`

```python
filter_cells(adata: AnnData, verbose: bool = True) -> AnnData
```

过滤低质量细胞（基于基因数和线粒体百分比）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| verbose | bool | True | 是否打印过滤信息 |

**返回值**: `AnnData` — 过滤后的 AnnData

### `filter_genes`

```python
filter_genes(adata: AnnData, verbose: bool = True) -> AnnData
```

过滤低表达基因（基于最少细胞数）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| verbose | bool | True | 是否打印过滤信息 |

**返回值**: `AnnData` — 过滤后的 AnnData

### `run_qc`

```python
run_qc(adata: AnnData, verbose: bool = True) -> AnnData
```

运行完整 QC 流程（compute_qc_metrics → filter_cells → filter_genes）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| verbose | bool | True | 是否打印信息 |

**返回值**: `AnnData` — QC 后的 AnnData

**示例**:

```python
from msra_modules.bioinformatics import ScRNASeqLoader, SingleCellQC

loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("data/pbmc_10x/")

qc = SingleCellQC(min_genes=200, max_genes=5000, max_pct_mito=20.0)
adata = qc.run_qc(adata)
print(f"QC 后: {adata.shape[0]} 细胞, {adata.shape[1]} 基因")
```

### `get_qc_summary`

```python
get_qc_summary(adata: AnnData) -> Dict
```

获取 QC 摘要统计。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |

**返回值**: `Dict` — 包含 `n_cells`、`n_genes`、`mean_genes_per_cell`、`mean_counts_per_cell`、`mean_pct_mito`、`max_pct_mito`

---

## DimensionalityReduction

> 降维分析，提供标准化、高变基因筛选、PCA、UMAP 和 Leiden 聚集流程。

**签名**:

```python
DimensionalityReduction(n_pcs: int = 50, n_neighbors: int = 15)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| n_pcs | int | 50 | PCA 主成分数 |
| n_neighbors | int | 15 | 邻居数 |

**方法**:

### `normalize_and_log`

```python
normalize_and_log(adata: AnnData, target_sum: int = 1e4) -> AnnData
```

标准化和对数转换。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| target_sum | int | 1e4 | 目标总和 |

**返回值**: `AnnData` — 标准化后的 AnnData

### `find_hvg`

```python
find_hvg(adata: AnnData, n_top_genes: int = 2000) -> AnnData
```

寻找高变基因。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| n_top_genes | int | 2000 | 高变基因数 |

**返回值**: `AnnData` — 带有高变基因标记的 AnnData

### `run_pca`

```python
run_pca(adata: AnnData) -> AnnData
```

运行 PCA 降维。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |

**返回值**: `AnnData` — 带有 PCA 结果（`obsm["X_pca"]`）的 AnnData

### `run_umap`

```python
run_umap(adata: AnnData) -> AnnData
```

运行 UMAP 降维（需先运行 PCA）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |

**返回值**: `AnnData` — 带有 UMAP 结果（`obsm["X_umap"]`）的 AnnData

### `cluster`

```python
cluster(adata: AnnData, resolution: float = 1.0) -> AnnData
```

Leiden 聚类分析。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| resolution | float | 1.0 | 聚类分辨率 |

**返回值**: `AnnData` — 带有聚类结果（`obs["leiden"]`）的 AnnData

### `run_full_pipeline`

```python
run_full_pipeline(adata: AnnData, resolution: float = 1.0) -> AnnData
```

运行完整降维聚类 pipeline（normalize_and_log → find_hvg → run_pca → run_umap → cluster）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| resolution | float | 1.0 | 聚类分辨率 |

**返回值**: `AnnData` — 处理后的 AnnData

**示例**:

```python
from msra_modules.bioinformatics import DimensionalityReduction

dr = DimensionalityReduction(n_pcs=50)
adata = dr.run_full_pipeline(adata, resolution=0.8)
print(f"聚类数: {adata.obs['leiden'].nunique()}")
```

---

## DifferentialExpression

> 差异表达分析，支持 Wilcoxon、t-test、logreg 方法，提供标记基因发现和差异基因筛选。

**签名**:

```python
DifferentialExpression(method: str = "wilcoxon")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| method | str | "wilcoxon" | 差异分析方法（"wilcoxon"、"t-test"、"logreg"） |

**方法**:

### `find_markers`

```python
find_markers(adata: AnnData, groupby: str = "leiden", use_raw: bool = True) -> pd.DataFrame
```

寻找标记基因。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| groupby | str | "leiden" | 分组列名 |
| use_raw | bool | True | 是否使用原始数据 |

**返回值**: `pd.DataFrame` — 标记基因 DataFrame（每列为一个聚类的标记基因）

### `get_de_table`

```python
get_de_table(adata: AnnData, group: str, n_genes: int = 100) -> pd.DataFrame
```

获取指定分组的差异表达表格。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| group | str | — | 必填，分组名 |
| n_genes | int | 100 | 返回的基因数 |

**返回值**: `pd.DataFrame` — 差异表达表格（含 log2FC、pvals_adj）

### `filter_de_genes`

```python
filter_de_genes(de_table: pd.DataFrame, log2fc_threshold: float = 1.0, pval_threshold: float = 0.05) -> pd.DataFrame
```

过滤显著差异基因。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| de_table | pd.DataFrame | — | 必填，差异表达表 |
| log2fc_threshold | float | 1.0 | log2FC 阈值 |
| pval_threshold | float | 0.05 | p 值阈值 |

**返回值**: `pd.DataFrame` — 过滤后的差异基因表（含 `direction` 列："up"/"down"）

**示例**:

```python
from msra_modules.bioinformatics import DifferentialExpression

de = DifferentialExpression(method="wilcoxon")
markers = de.find_markers(adata, groupby="leiden")
de_table = de.get_de_table(adata, group="0", n_genes=200)
sig_genes = de.filter_de_genes(de_table, log2fc_threshold=1.0, pval_threshold=0.05)
print(f"显著差异基因: {len(sig_genes)}")
```

---

## PathwayEnrichment

> 通路富集分析引擎，基于 gseapy 实现 GO (BP/MF/CC)、KEGG、GSEA 和 Enrichr 分析。

**签名**:

```python
PathwayEnrichment(organism: str = "human", gene_sets: Optional[str] = None, outdir: Optional[str] = None)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| organism | str | "human" | 物种名称（"human"、"mouse"、"rat" 等） |
| gene_sets | Optional[str] | None | 自定义 .gmt 基因集文件路径（可选） |
| outdir | Optional[str] | None | 输出目录（可选） |

**方法**:

### `run_go`

```python
run_go(gene_list: List[str], ontology: str = "BP", cutoff: float = 0.05) -> pd.DataFrame
```

运行 GO 富集分析（便捷方法）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| gene_list | List[str] | — | 必填，基因列表（gene symbols） |
| ontology | str | "BP" | GO 本体类型（"BP" / "MF" / "CC"） |
| cutoff | float | 0.05 | FDR 阈值 |

**返回值**: `pd.DataFrame` — GO 富集结果（含 Term、Overlap、P-value、Adjusted P-value、Genes）

**异常**: `ValueError` — ontology 不是 BP/MF/CC；`RuntimeError` — 分析失败

### `run_kegg`

```python
run_kegg(gene_list: List[str], cutoff: float = 0.05) -> pd.DataFrame
```

运行 KEGG 通路富集分析。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| gene_list | List[str] | — | 必填，基因列表 |
| cutoff | float | 0.05 | FDR 阈值 |

**返回值**: `pd.DataFrame` — KEGG 通路富集结果

### `run_gsea`

```python
run_gsea(ranked_genes: pd.Series, gene_sets: str = "GO_Biological_Process_2023", min_size: int = 15, max_size: int = 500, permutation_num: int = 100) -> pd.DataFrame
```

运行 GSEA 基因集富集分析。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| ranked_genes | pd.Series | — | 必填，基因排名序列（index=gene symbols, values=ranking metric） |
| gene_sets | str | "GO_Biological_Process_2023" | 基因集库名称或 .gmt 文件路径 |
| min_size | int | 15 | 基因集最小大小 |
| max_size | int | 500 | 基因集最大大小 |
| permutation_num | int | 100 | 置换次数 |

**返回值**: `pd.DataFrame` — GSEA 结果（含 Term、ES、NES、NOM p-val、FDR q-val、Lead_genes）

**异常**: `RuntimeError` — 分析失败

### `run_enrichr`

```python
run_enrichr(gene_list: List[str], gene_sets_library: str = "GO_Biological_Process_2023", cutoff: float = 0.05) -> pd.DataFrame
```

运行 Enrichr 富集分析（Over-Representation Analysis）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| gene_list | List[str] | — | 必填，基因列表 |
| gene_sets_library | str | "GO_Biological_Process_2023" | 基因集库名称 |
| cutoff | float | 0.05 | FDR 阈值 |

**返回值**: `pd.DataFrame` — Enrichr 结果

**异常**: `RuntimeError` — 分析失败

### `get_top_pathways`

```python
get_top_pathways(results: pd.DataFrame, n: int = 20, sort_by: str = "Adjusted P-value") -> pd.DataFrame
```

获取 Top N 通路。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| results | pd.DataFrame | — | 必填，富集结果 DataFrame |
| n | int | 20 | 返回的通路数 |
| sort_by | str | "Adjusted P-value" | 排序字段 |

**返回值**: `pd.DataFrame` — 排序后的 Top N 结果

### `export_results`

```python
export_results(results: pd.DataFrame, output_path: str, format: str = "csv") -> str
```

导出富集结果。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| results | pd.DataFrame | — | 必填，富集结果 |
| output_path | str | — | 必填，输出文件路径 |
| format | str | "csv" | 输出格式（"csv" / "json" / "tsv"） |

**返回值**: `str` — 输出文件路径

**异常**: `ValueError` — 不支持的格式

**示例**:

```python
from msra_modules.bioinformatics import PathwayEnrichment

enricher = PathwayEnrichment(organism="human")
go_results = enricher.run_go(gene_list=["CD3D", "CD3E", "IL7R"], ontology="BP")
top_pathways = enricher.get_top_pathways(go_results, n=10)
enricher.export_results(go_results, "output/go_enrichment.csv")
```

---

## BatchCorrector

> 批次效应检测与校正，支持 ComBat 和 Harmony 方法。

**签名**:

```python
BatchCorrector(batch_key: str = "batch", method: str = "combat")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| batch_key | str | "batch" | obs 中批次列名 |
| method | str | "combat" | 默认校正方法（"combat" 或 "harmony"） |

**方法**:

### `detect_batch_effect`

```python
detect_batch_effect(adata: AnnData, n_pcs: int = 50, threshold: float = 0.10) -> Dict[str, Any]
```

检测批次效应强度（通过 PCA 上 batch 解释的方差占比）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| n_pcs | int | 50 | PCA 主成分数 |
| threshold | float | 0.10 | 批次效应判定阈值（默认 10%） |

**返回值**: `Dict` — 含 `batch_variance_ratio`、`has_batch_effect`、`recommendation`、`pca_variance_explained`、`n_batches`

**异常**: `ValueError` — 批次列不存在或批次数 < 2

### `run_combat`

```python
run_combat(adata: AnnData, key: Optional[str] = None) -> AnnData
```

运行 ComBat 批次校正（原地修改 `adata.X`）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| key | Optional[str] | None | 要校正的 obs 列名（默认使用 batch_key） |

**返回值**: `AnnData` — 校正后的数据

### `run_harmony`

```python
run_harmony(adata: AnnData, basis: str = "X_pca", adjusted_basis: str = "X_pca_harmony") -> AnnData
```

运行 Harmony 批次校正（在 PCA 嵌入空间校正）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| basis | str | "X_pca" | 输入嵌入键名 |
| adjusted_basis | str | "X_pca_harmony" | 校正后的嵌入键名 |

**返回值**: `AnnData` — 校正后的数据（新增 `obsm[adjusted_basis]`）

**异常**: `ImportError` — harmonypy 未安装

### `compare_before_after`

```python
compare_before_after(adata_raw: AnnData, adata_corrected: AnnData, n_pcs: int = 50) -> Dict[str, Any]
```

比较校正前后效果。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata_raw | AnnData | — | 必填，校正前 AnnData |
| adata_corrected | AnnData | — | 必填，校正后 AnnData |
| n_pcs | int | 50 | PCA 主成分数 |

**返回值**: `Dict` — 含 `raw_batch_variance_ratio`、`corrected_batch_variance_ratio`、`improvement`

**示例**:

```python
from msra_modules.bioinformatics import BatchCorrector

corrector = BatchCorrector(batch_key="batch")
detection = corrector.detect_batch_effect(adata)
if detection["has_batch_effect"]:
    adata_corrected = corrector.run_combat(adata)
    comparison = corrector.compare_before_after(adata, adata_corrected)
    print(f"改善: {comparison['improvement']:.3f}")
```

---

## BioQualityGateChecker

> 生信质量门闸检查器，封装 Gate Bio-1.5（数据质量）和 Gate Bio-3.5（分析结果）的检查逻辑。

**签名**:

```python
BioQualityGateChecker(study_id: str, project_root: Optional[str] = None)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| study_id | str | — | 必填，研究编号 |
| project_root | Optional[str] | None | 项目根目录（可选） |

**方法**:

### `run_bio_gate_15`

```python
run_bio_gate_15(adata: AnnData, sample_info: Optional[pd.DataFrame] = None, batch_key: Optional[str] = None) -> GateResult
```

执行 Gate Bio-1.5 全部 5 项检查：Count 矩阵完整性、样本信息一致性、文库大小合理性、基因注释覆盖率、批次效应检测。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| adata | AnnData | — | 必填，AnnData 对象 |
| sample_info | Optional[pd.DataFrame] | None | 样本信息 DataFrame（可选） |
| batch_key | Optional[str] | None | 批次列名（可选） |

**返回值**: `GateResult` — 判定结果（PASS / CONDITIONAL / BLOCKED）

### `run_bio_gate_35`

```python
run_bio_gate_35(de_results: pd.DataFrame, enrichment_df: Optional[pd.DataFrame] = None, visualization_paths: Optional[List[str]] = None) -> GateResult
```

执行 Gate Bio-3.5 全部 5 项检查：P 值分布合理性、log2FC 与 P 值一致性、多重比较校正、通路富集 FDR、可视化一致性。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| de_results | pd.DataFrame | — | 必填，差异表达结果（需含 pvals、pvals_adj 列） |
| enrichment_df | Optional[pd.DataFrame] | None | 通路富集结果（可选） |
| visualization_paths | Optional[List[str]] | None | 可视化文件路径列表（可选） |

**返回值**: `GateResult` — 判定结果

**GateResult 属性**:

| 属性 | 类型 | 说明 |
|------|------|------|
| gate_type | GateType | 门闸类型 |
| study_id | str | 研究编号 |
| verdict | GateVerdict | 判定结果（PASS / CONDITIONAL / BLOCKED） |
| total_items | int | 总检查项数 |
| passed_items | int | 通过项数 |
| failed_items | int | 失败项数 |
| key_items_status | str | 关键项状态 |
| check_results | List[CheckItemResult] | 各项详细结果 |
| risks | List[str] | 风险列表 |
| pass_rate | float | 通过率 |

**示例**:

```python
from msra_modules.bioinformatics import BioQualityGateChecker

checker = BioQualityGateChecker(study_id="BIO-2026-001")

# Gate Bio-1.5: 数据质量检查
gate_15 = checker.run_bio_gate_15(adata, batch_key="batch")
print(f"Bio-1.5 判定: {gate_15.verdict.value}")

# Gate Bio-3.5: 分析结果检查
gate_35 = checker.run_bio_gate_35(de_table, enrichment_df=go_results)
print(f"Bio-3.5 判定: {gate_35.verdict.value}")
print(f"通过率: {gate_35.pass_rate:.1%}")
```

---

## 共享类型参考

### CheckItemResult

> 单个检查项结果。

| 属性 | 类型 | 说明 |
|------|------|------|
| item_id | str | 检查项编号 |
| name | str | 检查项名称 |
| is_key | bool | 是否为关键项 |
| status | str | 状态（PASS / FAIL / N/A / SKIP） |
| evidence | str | 证据描述 |
| notes | str | 备注 |

### GateVerdict

> 门闸判定结果枚举。

| 值 | 说明 |
|----|------|
| PASS | 全部通过 |
| CONDITIONAL | 条件通过（1-2 项未过，非关键项） |
| BLOCKED | 阻断（3+ 项未过或关键项未过） |
