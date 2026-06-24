# MSRA Bioinformatics 模块 API 参考

| 字段 | 值 |
|------|-----|
| **模块** | `msra_modules.bioinformatics` |
| **版本** | 1.1.0 |
| **日期** | 2026-07-13 |
| **状态** | Released (v1.0.0) |
| **语言** | 中文 |

---

## 概述

Bioinformatics 模块提供基于 Scanpy 和 gseapy 的单细胞 RNA-seq 全流程分析功能，包括数据加载、质量控制、降维聚类、差异表达、通路富集、批次校正和质量门闸检查。

### 依赖

- `scanpy` — 单细胞分析核心库
- `gseapy` — 通路富集分析
- `harmonypy` — Harmony 批次校正
- `biopython` — FASTA 序列读取
- `scipy` — 统计检验
- `matplotlib` — 可视化

---

## 公开 API

### `ScRNASeqLoader`

**描述**: 单细胞 RNA-seq 数据加载器，支持 10x MTX / H5 / CSV 格式以及 FASTA 序列文件。

**参数**:

无构造参数。

**方法**:

#### `read_10x_mtx(mtx_dir, var_names="gene_symbols", cache=True)`

读取 10x Genomics MTX 格式数据。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `mtx_dir` | `str` | 是 | — | 10x 输出目录（包含 matrix.mtx, features.tsv, barcodes.tsv） |
| `var_names` | `str` | 否 | `"gene_symbols"` | 基因名类型（`"gene_symbols"` 或 `"gene_ids"`） |
| `cache` | `bool` | 否 | `True` | 是否缓存 |

- **返回值**: `anndata.AnnData` 对象
- **示例**:

```python
from msra_modules.bioinformatics import ScRNASeqLoader

loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("/data/pbmc_10x/")
print(adata.shape)
```

#### `read_10x_h5(h5_path, genome=None)`

读取 10x Genomics H5 格式数据。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `h5_path` | `str` | 是 | — | H5 文件路径 |
| `genome` | `str` | 否 | `None` | 基因组名称 |

- **返回值**: `anndata.AnnData` 对象
- **示例**:

```python
adata = loader.read_10x_h5("/data/pbmc.h5")
```

#### `read_csv(csv_path, **kwargs)`

读取 CSV 格式表达矩阵。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `csv_path` | `str` | 是 | — | CSV 文件路径 |
| `**kwargs` | — | 否 | — | 传递给 `pandas.read_csv` 的参数 |

- **返回值**: `anndata.AnnData` 对象

#### `read_fasta(fasta_path)`

读取 FASTA 序列文件（使用 Biopython）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `fasta_path` | `str` | 是 | — | FASTA 文件路径 |

- **返回值**: `list[Bio.SeqRecord.SeqRecord]` — 序列列表

#### `get_metadata()`

获取当前已加载数据的元数据。

- **返回值**: `dict` — 包含 `n_cells`、`n_genes`、`obs_columns`、`var_columns`、`is_sparse` 字段
- **异常**: 无异常，未加载数据时返回 `{"error": "No data loaded"}`

**异常**: `ImportError`（scanpy/biopython 未安装）、`FileNotFoundError`（文件不存在）

---

### `read_10x_mtx(mtx_dir, **kwargs)`

**描述**: 便捷函数，等价于 `ScRNASeqLoader().read_10x_mtx(mtx_dir, **kwargs)`。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `mtx_dir` | `str` | 是 | — | 10x 输出目录 |
| `**kwargs` | — | 否 | — | 传递给 `ScRNASeqLoader.read_10x_mtx` 的参数 |

- **返回值**: `anndata.AnnData` 对象

---

### `SingleCellQC`

**描述**: 单细胞质量控制，包括线粒体比例、基因数、UMI 过滤。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `min_genes` | `int` | 否 | `200` | 每个细胞最少基因数 |
| `max_genes` | `int` | 否 | `5000` | 每个细胞最多基因数 |
| `max_pct_mito` | `float` | 否 | `20.0` | 最大线粒体基因百分比 |
| `min_cells` | `int` | 否 | `3` | 每个基因最少细胞数 |

**方法**:

#### `compute_qc_metrics(adata)`

计算 QC 指标（标记线粒体基因并计算 QC metrics）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |

- **返回值**: `AnnData`（带有 QC 指标，原地修改）

#### `filter_cells(adata, verbose=True)`

过滤低质量细胞（基于基因数和线粒体百分比）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `verbose` | `bool` | 否 | `True` | 是否打印信息 |

- **返回值**: `AnnData`（过滤后）

#### `filter_genes(adata, verbose=True)`

过滤低表达基因。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `verbose` | `bool` | 否 | `True` | 是否打印信息 |

- **返回值**: `AnnData`（过滤后）

#### `run_qc(adata, verbose=True)`

运行完整 QC 流程（计算指标 → 过滤细胞 → 过滤基因）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `verbose` | `bool` | 否 | `True` | 是否打印信息 |

- **返回值**: `AnnData`（QC 后）
- **示例**:

```python
from msra_modules.bioinformatics import ScRNASeqLoader, SingleCellQC

loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("/data/pbmc_10x/")

qc = SingleCellQC(min_genes=200, max_genes=5000, max_pct_mito=20.0)
adata = qc.run_qc(adata)
```

#### `get_qc_summary(adata)`

获取 QC 摘要。

- **返回值**: `dict` — 包含 `n_cells`、`n_genes`、`mean_genes_per_cell`、`median_genes_per_cell`、`mean_counts_per_cell`、`mean_pct_mito`、`max_pct_mito`

**异常**: `ImportError`（scanpy 未安装）

---

### `DimensionalityReduction`

**描述**: 降维分析，支持 PCA / UMAP / 聚类（Leiden）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `n_pcs` | `int` | 否 | `50` | PCA 主成分数 |
| `n_neighbors` | `int` | 否 | `15` | 邻居数 |

**方法**:

#### `normalize_and_log(adata, target_sum=1e4)`

标准化和对数转换。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `target_sum` | `int` | 否 | `10000` | 目标总和 |

- **返回值**: `AnnData`

#### `find_hvg(adata, n_top_genes=2000)`

寻找高变基因。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `n_top_genes` | `int` | 否 | `2000` | 高变基因数 |

- **返回值**: `AnnData`

#### `run_pca(adata)`

运行 PCA。

- **返回值**: `AnnData`（新增 `obsm["X_pca"]`）

#### `run_umap(adata)`

运行 UMAP（需先运行 PCA）。

- **返回值**: `AnnData`（新增 `obsm["X_umap"]`）

#### `cluster(adata, resolution=1.0)`

Leiden 聚类。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `resolution` | `float` | 否 | `1.0` | 聚类分辨率 |

- **返回值**: `AnnData`（新增 `obs["leiden"]`）

#### `run_full_pipeline(adata, resolution=1.0)`

运行完整降维聚类 pipeline（标准化 → HVG → PCA → UMAP → 聚类）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `resolution` | `float` | 否 | `1.0` | 聚类分辨率 |

- **返回值**: `AnnData`
- **示例**:

```python
from msra_modules.bioinformatics import DimensionalityReduction

dr = DimensionalityReduction(n_pcs=50, n_neighbors=15)
adata = dr.run_full_pipeline(adata, resolution=0.8)
```

**异常**: `ImportError`（scanpy 未安装）

---

### `DifferentialExpression`

**描述**: 差异表达分析，支持 Wilcoxon / t-test / logreg 方法。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `method` | `str` | 否 | `"wilcoxon"` | 差异分析方法（`"wilcoxon"`, `"t-test"`, `"logreg"`） |

**方法**:

#### `find_markers(adata, groupby="leiden", use_raw=True)`

寻找标记基因。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `groupby` | `str` | 否 | `"leiden"` | 分组列名 |
| `use_raw` | `bool` | 否 | `True` | 是否使用原始数据 |

- **返回值**: `pd.DataFrame` — 标记基因表（列为各分组名，行为排名）

#### `get_de_table(adata, group, n_genes=100)`

获取差异表达表格。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `group` | `str` | 是 | — | 分组名 |
| `n_genes` | `int` | 否 | `100` | 返回的基因数 |

- **返回值**: `pd.DataFrame` — 含 `names`, `logfoldchanges`, `pvals`, `pvals_adj`, `log2FC` 列

#### `filter_de_genes(de_table, log2fc_threshold=1.0, pval_threshold=0.05)`

过滤差异基因。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `de_table` | `pd.DataFrame` | 是 | — | 差异表达表 |
| `log2fc_threshold` | `float` | 否 | `1.0` | log2FC 阈值 |
| `pval_threshold` | `float` | 否 | `0.05` | 校正 p 值阈值 |

- **返回值**: `pd.DataFrame` — 过滤后的差异基因表，含 `direction` 列（`"up"` / `"down"`）

- **示例**:

```python
from msra_modules.bioinformatics import DifferentialExpression

de = DifferentialExpression(method="wilcoxon")
markers = de.find_markers(adata, groupby="leiden")
de_table = de.get_de_table(adata, group="0", n_genes=100)
sig_genes = de.filter_de_genes(de_table, log2fc_threshold=1.0, pval_threshold=0.05)
```

**异常**: `ImportError`（scanpy 未安装）

---

### `TrajectoryAnalysis`

**描述**: 轨迹分析，支持 PAGA 和 DPT（Diffusion Pseudotime）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `method` | `str` | 否 | `"paga"` | 方法（`"paga"` 或 `"dpt"`） |

**方法**:

#### `run_paga(adata, groups="leiden")`

运行 PAGA 轨迹分析。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `groups` | `str` | 否 | `"leiden"` | 分组列名 |

- **返回值**: `AnnData`

#### `run_dpt(adata, root_key="xroot")`

运行 DPT（Diffusion Pseudotime）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `root_key` | `str` | 否 | `"xroot"` | 根细胞键名 |

- **返回值**: `AnnData`

**异常**: `ImportError`（scanpy 未安装）

---

### `CellBenderDenoiser`

**描述**: CellBender 单细胞去噪（背景去除），通过命令行调用 CellBender。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `expected_cells` | `int` | 否 | `3000` | 预期细胞数 |
| `total_droplets` | `int` | 否 | `30000` | 总液滴数 |
| `epochs` | `int` | 否 | `200` | 训练轮数 |

**方法**:

#### `check_installation()`

检查 CellBender 是否已安装。

- **返回值**: `bool`

#### `run_remove_background(input_h5, output_h5, expected_cells=None, total_droplets=None)`

运行背景去除。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `input_h5` | `str` | 是 | — | 输入 H5 文件路径 |
| `output_h5` | `str` | 是 | — | 输出 H5 文件路径 |
| `expected_cells` | `int` | 否 | `None` | 预期细胞数（覆盖默认值） |
| `total_droplets` | `int` | 否 | `None` | 总液滴数（覆盖默认值） |

- **返回值**: `dict` — 包含 `success`, `output_file`/`error`, `stdout`

#### `load_denoised(h5_path)`

加载去噪后的数据。

- **返回值**: `AnnData`

#### `compare_before_after(raw_adata, denoised_adata)`

比较去噪前后数据。

- **返回值**: `dict` — 包含 `raw_mean`, `denoised_mean`, `raw_std`, `denoised_std`, `mean_difference`, `std_difference` 等

**异常**: `RuntimeError`（CellBender 未安装）、`FileNotFoundError`、`ImportError`

---

### `BioVisualizer`

**描述**: 生物信息可视化工具，基于 matplotlib + scanpy.pl。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `figsize` | `tuple` | 否 | `(8, 6)` | 图像大小 |
| `dpi` | `int` | 否 | `100` | 分辨率 |

**方法**:

#### `plot_umap(adata, color=None, save_path=None)`

绘制 UMAP 图。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象（需含 `X_umap`） |
| `color` | `str` | 否 | `None` | 着色列名 |
| `save_path` | `str` | 否 | `None` | 保存路径 |

- **返回值**: `matplotlib.figure.Figure`

#### `plot_violin(adata, keys, groupby=None, save_path=None)`

绘制小提琴图。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `keys` | `list[str]` | 是 | — | 基因名列表 |
| `groupby` | `str` | 否 | `None` | 分组列名 |
| `save_path` | `str` | 否 | `None` | 保存路径 |

- **返回值**: `matplotlib.figure.Figure`

#### `plot_dotplot(adata, var_names, groupby="leiden", save_path=None)`

绘制点图。

- **返回值**: `matplotlib.figure.Figure`

#### `plot_heatmap(adata, var_names, groupby="leiden", save_path=None)`

绘制热图。

- **返回值**: `matplotlib.figure.Figure`

#### `plot_paga(adata, color=None, save_path=None)`

绘制 PAGA 轨迹图。

- **返回值**: `matplotlib.figure.Figure`

**异常**: `ImportError`（scanpy 未安装）、`ValueError`（UMAP 未计算）

---

### `PathwayEnrichment`

**描述**: 通路富集分析引擎，基于 gseapy 实现 GO (BP/MF/CC)、KEGG、GSEA 和 Enrichr 富集分析。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `organism` | `str` | 否 | `"human"` | 物种名称（`"human"`, `"mouse"` 等） |
| `gene_sets` | `str` | 否 | `None` | 自定义 `.gmt` 基因集文件路径 |
| `outdir` | `str` | 否 | `None` | 输出目录 |

**方法**:

#### `run_enrichr(gene_list, gene_sets_library="GO_Biological_Process_2023", cutoff=0.05)`

运行 Enrichr 富集分析（Over-Representation Analysis）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `gene_list` | `list[str]` | 是 | — | 基因列表（gene symbols） |
| `gene_sets_library` | `str` | 否 | `"GO_Biological_Process_2023"` | 基因集库名称 |
| `cutoff` | `float` | 否 | `0.05` | FDR 阈值 |

- **返回值**: `pd.DataFrame` — 列含 `Term`, `Overlap`, `P-value`, `Adjusted P-value`, `Odds Ratio`, `Combined Score`, `Genes`

#### `run_gsea(ranked_genes, gene_sets="GO_Biological_Process_2023", min_size=15, max_size=500, permutation_num=100)`

运行 GSEA 基因集富集分析。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `ranked_genes` | `pd.Series` | 是 | — | 基因排名序列（index=gene symbols, values=ranking metric） |
| `gene_sets` | `str` | 否 | `"GO_Biological_Process_2023"` | 基因集库名称或 `.gmt` 文件路径 |
| `min_size` | `int` | 否 | `15` | 基因集最小大小 |
| `max_size` | `int` | 否 | `500` | 基因集最大大小 |
| `permutation_num` | `int` | 否 | `100` | 置换次数 |

- **返回值**: `pd.DataFrame` — 列含 `Term`, `ES`, `NES`, `NOM p-val`, `FDR q-val`, `FWER p-val`, `Tag %`, `Lead_genes`

#### `run_go(gene_list, ontology="BP", cutoff=0.05)`

运行 GO 富集分析（便捷方法）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `gene_list` | `list[str]` | 是 | — | 基因列表 |
| `ontology` | `str` | 否 | `"BP"` | GO 本体类型（`"BP"` / `"MF"` / `"CC"`） |
| `cutoff` | `float` | 否 | `0.05` | FDR 阈值 |

- **返回值**: `pd.DataFrame`

#### `run_kegg(gene_list, cutoff=0.05)`

运行 KEGG 通路富集分析（便捷方法）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `gene_list` | `list[str]` | 是 | — | 基因列表 |
| `cutoff` | `float` | 否 | `0.05` | FDR 阈值 |

- **返回值**: `pd.DataFrame`

#### `get_top_pathways(results, n=20, sort_by="Adjusted P-value")`

获取 Top N 通路。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `results` | `pd.DataFrame` | 是 | — | 富集结果 DataFrame |
| `n` | `int` | 否 | `20` | 返回的通路数 |
| `sort_by` | `str` | 否 | `"Adjusted P-value"` | 排序字段 |

- **返回值**: `pd.DataFrame`

#### `export_results(results, output_path, format="csv")`

导出富集结果。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `results` | `pd.DataFrame` | 是 | — | 富集结果 DataFrame |
| `output_path` | `str` | 是 | — | 输出文件路径 |
| `format` | `str` | 否 | `"csv"` | 输出格式（`"csv"` / `"json"` / `"tsv"`） |

- **返回值**: `str` — 输出文件路径
- **示例**:

```python
from msra_modules.bioinformatics import PathwayEnrichment

enricher = PathwayEnrichment(organism="human")
go_results = enricher.run_go(sig_genes["names"].tolist(), ontology="BP")
top_go = enricher.get_top_pathways(go_results, n=20)
enricher.export_results(top_go, "/output/go_results.csv", format="csv")
```

**异常**: `ImportError`（gseapy 未安装）、`RuntimeError`（分析失败）、`ValueError`（不支持的格式）

---

### `BatchCorrector`

**描述**: 批次效应检测与校正，支持 ComBat 和 Harmony 方法。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `batch_key` | `str` | 否 | `"batch"` | `obs` 中批次列名 |
| `method` | `str` | 否 | `"combat"` | 默认校正方法（`"combat"` 或 `"harmony"`） |

**方法**:

#### `detect_batch_effect(adata, n_pcs=50, threshold=0.10)`

检测批次效应强度（通过 PCA 上 batch 解释的方差占比）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `n_pcs` | `int` | 否 | `50` | PCA 主成分数 |
| `threshold` | `float` | 否 | `0.10` | 批次效应判定阈值（10%） |

- **返回值**: `dict` — 含 `batch_variance_ratio`, `has_batch_effect`, `recommendation`, `pca_variance_explained`, `n_batches`

#### `run_combat(adata, key=None)`

运行 ComBat 批次校正（原地修改 `adata.X`）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `key` | `str` | 否 | `None` | 要校正的 obs 列名（默认使用 `self.batch_key`） |

- **返回值**: `AnnData`（原地修改并返回）

#### `run_harmony(adata, basis="X_pca", adjusted_basis="X_pca_harmony")`

运行 Harmony 批次校正（在 PCA 嵌入空间）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `basis` | `str` | 否 | `"X_pca"` | 输入嵌入键名 |
| `adjusted_basis` | `str` | 否 | `"X_pca_harmony"` | 校正后的嵌入键名 |

- **返回值**: `AnnData`（新增 `obsm[adjusted_basis]`）

#### `compare_before_after(adata_raw, adata_corrected, n_pcs=50)`

比较校正前后效果。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata_raw` | `AnnData` | 是 | — | 校正前 AnnData |
| `adata_corrected` | `AnnData` | 是 | — | 校正后 AnnData |
| `n_pcs` | `int` | 否 | `50` | PCA 主成分数 |

- **返回值**: `dict` — 含 `raw_batch_variance_ratio`, `corrected_batch_variance_ratio`, `improvement`, `raw_per_pc_variance`, `corrected_per_pc_variance`
- **示例**:

```python
from msra_modules.bioinformatics import BatchCorrector

corrector = BatchCorrector(batch_key="batch")
detection = corrector.detect_batch_effect(adata)
if detection["has_batch_effect"]:
    adata_corrected = corrector.run_combat(adata)
    comparison = corrector.compare_before_after(adata, adata_corrected)
```

**异常**: `ImportError`（scanpy/harmonypy 未安装）、`ValueError`（批次列不存在或批次数不足）

---

### `BioQualityGateChecker`

**描述**: 生信质量门闸检查器，封装 Gate Bio-1.5（数据质量门闸）和 Gate Bio-3.5（分析结果门闸）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `study_id` | `str` | 是 | — | 研究编号 |
| `project_root` | `str` | 否 | `None` | 项目根目录 |

**方法**:

#### `run_bio_gate_15(adata, sample_info=None, batch_key=None)`

执行 Gate Bio-1.5 全部 5 项检查：Count 矩阵完整性、样本信息一致性、文库大小合理性、基因注释覆盖率、批次效应检测。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `adata` | `AnnData` | 是 | — | AnnData 对象 |
| `sample_info` | `pd.DataFrame` | 否 | `None` | 样本信息 DataFrame |
| `batch_key` | `str` | 否 | `None` | 批次列名 |

- **返回值**: `GateResult` — 判定结果（`PASS` / `CONDITIONAL` / `BLOCKED`）

#### `run_bio_gate_35(de_results, enrichment_df=None, visualization_paths=None)`

执行 Gate Bio-3.5 全部 5 项检查：P 值分布合理性、log2FC 与 P 值一致性、多重比较校正、通路富集 FDR、可视化一致性。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `de_results` | `pd.DataFrame` | 是 | — | 差异表达结果（需含 pvals/pvals_adj 列） |
| `enrichment_df` | `pd.DataFrame` | 否 | `None` | 通路富集结果 |
| `visualization_paths` | `list[str]` | 否 | `None` | 可视化文件路径列表 |

- **返回值**: `GateResult`
- **示例**:

```python
from msra_modules.bioinformatics import BioQualityGateChecker

checker = BioQualityGateChecker(study_id="BIO-2026-001")
gate_15 = checker.run_bio_gate_15(adata, sample_info=sample_df, batch_key="batch")
gate_35 = checker.run_bio_gate_35(de_table, enrichment_df=go_results)
print(gate_15.verdict, gate_35.verdict)
```

**异常**: `ImportError`（scanpy/scipy 未安装时对应检查项标记为 FAIL/SKIP）

---

## 完整使用示例

```python
from msra_modules.bioinformatics import (
    ScRNASeqLoader, SingleCellQC, DimensionalityReduction,
    DifferentialExpression, PathwayEnrichment, BatchCorrector,
    BioQualityGateChecker,
)

# 1. 加载数据
loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("/data/pbmc_10x/")

# 2. 质量控制
qc = SingleCellQC(min_genes=200, max_genes=5000, max_pct_mito=20.0)
adata = qc.run_qc(adata)

# 3. 批次校正（如有批次信息）
corrector = BatchCorrector(batch_key="batch")
detection = corrector.detect_batch_effect(adata)
if detection["has_batch_effect"]:
    adata = corrector.run_combat(adata)

# 4. 降维聚类
dr = DimensionalityReduction(n_pcs=50)
adata = dr.run_full_pipeline(adata, resolution=1.0)

# 5. 差异表达
de = DifferentialExpression(method="wilcoxon")
markers = de.find_markers(adata, groupby="leiden")
de_table = de.get_de_table(adata, group="0")
sig_genes = de.filter_de_genes(de_table, log2fc_threshold=1.0, pval_threshold=0.05)

# 6. 通路富集
enricher = PathwayEnrichment(organism="human")
go_results = enricher.run_go(sig_genes["names"].tolist(), ontology="BP")

# 7. 质量门闸
checker = BioQualityGateChecker(study_id="BIO-2026-001")
gate_15 = checker.run_bio_gate_15(adata)
gate_35 = checker.run_bio_gate_35(de_table, enrichment_df=go_results)
```
