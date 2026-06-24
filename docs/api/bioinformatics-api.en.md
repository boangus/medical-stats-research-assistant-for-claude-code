# MSRA Bioinformatics Module API Reference

| Field | Value |
|-------|-------|
| **Module** | `msra_modules.bioinformatics` |
| **Version** | 1.1.0 |
| **Date** | 2026-07-13 |
| **Status** | Released (v1.0.0) |
| **Language** | English |

---

## Overview

The Bioinformatics module provides single-cell RNA-seq full-pipeline analysis powered by Scanpy and gseapy, including data loading, quality control, dimensionality reduction, clustering, differential expression, pathway enrichment, batch correction, and quality gate checks.

### Dependencies

- `scanpy` — Core single-cell analysis library
- `gseapy` — Pathway enrichment analysis
- `harmonypy` — Harmony batch correction
- `biopython` — FASTA sequence reading
- `scipy` — Statistical tests
- `matplotlib` — Visualization

---

## Public API

### `ScRNASeqLoader`

**Description**: Single-cell RNA-seq data loader supporting 10x MTX / H5 / CSV formats and FASTA sequence files.

**Parameters**: None.

**Methods**:

#### `read_10x_mtx(mtx_dir, var_names="gene_symbols", cache=True)`

Read 10x Genomics MTX format data.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mtx_dir` | `str` | Yes | — | 10x output directory (containing matrix.mtx, features.tsv, barcodes.tsv) |
| `var_names` | `str` | No | `"gene_symbols"` | Gene name type (`"gene_symbols"` or `"gene_ids"`) |
| `cache` | `bool` | No | `True` | Whether to cache |

- **Returns**: `anndata.AnnData`
- **Example**:

```python
from msra_modules.bioinformatics import ScRNASeqLoader

loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("/data/pbmc_10x/")
print(adata.shape)
```

#### `read_10x_h5(h5_path, genome=None)`

Read 10x Genomics H5 format data.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `h5_path` | `str` | Yes | — | H5 file path |
| `genome` | `str` | No | `None` | Genome name |

- **Returns**: `anndata.AnnData`

#### `read_csv(csv_path, **kwargs)`

Read CSV format expression matrix.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `csv_path` | `str` | Yes | — | CSV file path |
| `**kwargs` | — | No | — | Arguments passed to `pandas.read_csv` |

- **Returns**: `anndata.AnnData`

#### `read_fasta(fasta_path)`

Read FASTA sequence file (using Biopython).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fasta_path` | `str` | Yes | — | FASTA file path |

- **Returns**: `list[Bio.SeqRecord.SeqRecord]`

#### `get_metadata()`

Get metadata of currently loaded data.

- **Returns**: `dict` — contains `n_cells`, `n_genes`, `obs_columns`, `var_columns`, `is_sparse`
- Returns `{"error": "No data loaded"}` if no data loaded.

**Exceptions**: `ImportError` (scanpy/biopython not installed), `FileNotFoundError` (file not found)

---

### `read_10x_mtx(mtx_dir, **kwargs)`

**Description**: Convenience function, equivalent to `ScRNASeqLoader().read_10x_mtx(mtx_dir, **kwargs)`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mtx_dir` | `str` | Yes | — | 10x output directory |
| `**kwargs` | — | No | — | Arguments passed to `ScRNASeqLoader.read_10x_mtx` |

- **Returns**: `anndata.AnnData`

---

### `SingleCellQC`

**Description**: Single-cell quality control including mitochondrial percentage, gene count, and UMI filtering.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `min_genes` | `int` | No | `200` | Minimum genes per cell |
| `max_genes` | `int` | No | `5000` | Maximum genes per cell |
| `max_pct_mito` | `float` | No | `20.0` | Maximum mitochondrial gene percentage |
| `min_cells` | `int` | No | `3` | Minimum cells per gene |

**Methods**:

#### `compute_qc_metrics(adata)`

Compute QC metrics (mark mitochondrial genes and calculate QC metrics).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |

- **Returns**: `AnnData` (with QC metrics, modified in-place)

#### `filter_cells(adata, verbose=True)`

Filter low-quality cells (based on gene count and mitochondrial percentage).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `verbose` | `bool` | No | `True` | Whether to print info |

- **Returns**: `AnnData` (filtered)

#### `filter_genes(adata, verbose=True)`

Filter low-expression genes.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `verbose` | `bool` | No | `True` | Whether to print info |

- **Returns**: `AnnData` (filtered)

#### `run_qc(adata, verbose=True)`

Run complete QC pipeline (compute metrics -> filter cells -> filter genes).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `verbose` | `bool` | No | `True` | Whether to print info |

- **Returns**: `AnnData` (after QC)
- **Example**:

```python
from msra_modules.bioinformatics import ScRNASeqLoader, SingleCellQC

loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("/data/pbmc_10x/")

qc = SingleCellQC(min_genes=200, max_genes=5000, max_pct_mito=20.0)
adata = qc.run_qc(adata)
```

#### `get_qc_summary(adata)`

Get QC summary.

- **Returns**: `dict` — contains `n_cells`, `n_genes`, `mean_genes_per_cell`, `median_genes_per_cell`, `mean_counts_per_cell`, `mean_pct_mito`, `max_pct_mito`

**Exceptions**: `ImportError` (scanpy not installed)

---

### `DimensionalityReduction`

**Description**: Dimensionality reduction analysis supporting PCA / UMAP / Leiden clustering.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `n_pcs` | `int` | No | `50` | Number of PCA components |
| `n_neighbors` | `int` | No | `15` | Number of neighbors |

**Methods**:

#### `normalize_and_log(adata, target_sum=1e4)`

Normalize and log-transform.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `target_sum` | `int` | No | `10000` | Target sum |

- **Returns**: `AnnData`

#### `find_hvg(adata, n_top_genes=2000)`

Find highly variable genes.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `n_top_genes` | `int` | No | `2000` | Number of highly variable genes |

- **Returns**: `AnnData`

#### `run_pca(adata)`

Run PCA.

- **Returns**: `AnnData` (adds `obsm["X_pca"]`)

#### `run_umap(adata)`

Run UMAP (requires PCA first).

- **Returns**: `AnnData` (adds `obsm["X_umap"]`)

#### `cluster(adata, resolution=1.0)`

Leiden clustering.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `resolution` | `float` | No | `1.0` | Clustering resolution |

- **Returns**: `AnnData` (adds `obs["leiden"]`)

#### `run_full_pipeline(adata, resolution=1.0)`

Run complete dimensionality reduction pipeline (normalize -> HVG -> PCA -> UMAP -> cluster).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `resolution` | `float` | No | `1.0` | Clustering resolution |

- **Returns**: `AnnData`
- **Example**:

```python
from msra_modules.bioinformatics import DimensionalityReduction

dr = DimensionalityReduction(n_pcs=50, n_neighbors=15)
adata = dr.run_full_pipeline(adata, resolution=0.8)
```

**Exceptions**: `ImportError` (scanpy not installed)

---

### `DifferentialExpression`

**Description**: Differential expression analysis supporting Wilcoxon / t-test / logreg methods.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `method` | `str` | No | `"wilcoxon"` | DE method (`"wilcoxon"`, `"t-test"`, `"logreg"`) |

**Methods**:

#### `find_markers(adata, groupby="leiden", use_raw=True)`

Find marker genes.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `groupby` | `str` | No | `"leiden"` | Grouping column name |
| `use_raw` | `bool` | No | `True` | Whether to use raw data |

- **Returns**: `pd.DataFrame` — marker genes table (columns are group names, rows are rankings)

#### `get_de_table(adata, group, n_genes=100)`

Get differential expression table.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `group` | `str` | Yes | — | Group name |
| `n_genes` | `int` | No | `100` | Number of genes to return |

- **Returns**: `pd.DataFrame` — contains `names`, `logfoldchanges`, `pvals`, `pvals_adj`, `log2FC` columns

#### `filter_de_genes(de_table, log2fc_threshold=1.0, pval_threshold=0.05)`

Filter differentially expressed genes.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `de_table` | `pd.DataFrame` | Yes | — | DE table |
| `log2fc_threshold` | `float` | No | `1.0` | log2FC threshold |
| `pval_threshold` | `float` | No | `0.05` | Adjusted p-value threshold |

- **Returns**: `pd.DataFrame` — filtered DE genes with `direction` column (`"up"` / `"down"`)

- **Example**:

```python
from msra_modules.bioinformatics import DifferentialExpression

de = DifferentialExpression(method="wilcoxon")
markers = de.find_markers(adata, groupby="leiden")
de_table = de.get_de_table(adata, group="0", n_genes=100)
sig_genes = de.filter_de_genes(de_table, log2fc_threshold=1.0, pval_threshold=0.05)
```

**Exceptions**: `ImportError` (scanpy not installed)

---

### `TrajectoryAnalysis`

**Description**: Trajectory analysis supporting PAGA and DPT (Diffusion Pseudotime).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `method` | `str` | No | `"paga"` | Method (`"paga"` or `"dpt"`) |

**Methods**:

#### `run_paga(adata, groups="leiden")`

Run PAGA trajectory analysis.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `groups` | `str` | No | `"leiden"` | Grouping column name |

- **Returns**: `AnnData`

#### `run_dpt(adata, root_key="xroot")`

Run DPT (Diffusion Pseudotime).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `root_key` | `str` | No | `"xroot"` | Root cell key name |

- **Returns**: `AnnData`

**Exceptions**: `ImportError` (scanpy not installed)

---

### `CellBenderDenoiser`

**Description**: CellBender single-cell denoising (background removal) via command-line invocation.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `expected_cells` | `int` | No | `3000` | Expected number of cells |
| `total_droplets` | `int` | No | `30000` | Total number of droplets |
| `epochs` | `int` | No | `200` | Training epochs |

**Methods**:

#### `check_installation()`

Check if CellBender is installed.

- **Returns**: `bool`

#### `run_remove_background(input_h5, output_h5, expected_cells=None, total_droplets=None)`

Run background removal.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_h5` | `str` | Yes | — | Input H5 file path |
| `output_h5` | `str` | Yes | — | Output H5 file path |
| `expected_cells` | `int` | No | `None` | Expected cells (overrides default) |
| `total_droplets` | `int` | No | `None` | Total droplets (overrides default) |

- **Returns**: `dict` — contains `success`, `output_file`/`error`, `stdout`

#### `load_denoised(h5_path)`

Load denoised data.

- **Returns**: `AnnData`

#### `compare_before_after(raw_adata, denoised_adata)`

Compare data before and after denoising.

- **Returns**: `dict` — contains `raw_mean`, `denoised_mean`, `raw_std`, `denoised_std`, `mean_difference`, `std_difference`, etc.

**Exceptions**: `RuntimeError` (CellBender not installed), `FileNotFoundError`, `ImportError`

---

### `BioVisualizer`

**Description**: Bioinformatics visualization tool based on matplotlib + scanpy.pl.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `figsize` | `tuple` | No | `(8, 6)` | Figure size |
| `dpi` | `int` | No | `100` | Resolution |

**Methods**:

#### `plot_umap(adata, color=None, save_path=None)`

Plot UMAP.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object (requires `X_umap`) |
| `color` | `str` | No | `None` | Color column name |
| `save_path` | `str` | No | `None` | Save path |

- **Returns**: `matplotlib.figure.Figure`

#### `plot_violin(adata, keys, groupby=None, save_path=None)`

Plot violin plot.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `keys` | `list[str]` | Yes | — | Gene name list |
| `groupby` | `str` | No | `None` | Grouping column name |
| `save_path` | `str` | No | `None` | Save path |

- **Returns**: `matplotlib.figure.Figure`

#### `plot_dotplot(adata, var_names, groupby="leiden", save_path=None)`

Plot dot plot.

- **Returns**: `matplotlib.figure.Figure`

#### `plot_heatmap(adata, var_names, groupby="leiden", save_path=None)`

Plot heatmap.

- **Returns**: `matplotlib.figure.Figure`

#### `plot_paga(adata, color=None, save_path=None)`

Plot PAGA trajectory.

- **Returns**: `matplotlib.figure.Figure`

**Exceptions**: `ImportError` (scanpy not installed), `ValueError` (UMAP not computed)

---

### `PathwayEnrichment`

**Description**: Pathway enrichment analysis engine based on gseapy, implementing GO (BP/MF/CC), KEGG, GSEA, and Enrichr enrichment analysis.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `organism` | `str` | No | `"human"` | Organism name (`"human"`, `"mouse"`, etc.) |
| `gene_sets` | `str` | No | `None` | Custom `.gmt` gene set file path |
| `outdir` | `str` | No | `None` | Output directory |

**Methods**:

#### `run_enrichr(gene_list, gene_sets_library="GO_Biological_Process_2023", cutoff=0.05)`

Run Enrichr enrichment analysis (Over-Representation Analysis).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `gene_list` | `list[str]` | Yes | — | Gene list (gene symbols) |
| `gene_sets_library` | `str` | No | `"GO_Biological_Process_2023"` | Gene set library name |
| `cutoff` | `float` | No | `0.05` | FDR cutoff |

- **Returns**: `pd.DataFrame` — columns: `Term`, `Overlap`, `P-value`, `Adjusted P-value`, `Odds Ratio`, `Combined Score`, `Genes`

#### `run_gsea(ranked_genes, gene_sets="GO_Biological_Process_2023", min_size=15, max_size=500, permutation_num=100)`

Run GSEA gene set enrichment analysis.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ranked_genes` | `pd.Series` | Yes | — | Ranked gene series (index=gene symbols, values=ranking metric) |
| `gene_sets` | `str` | No | `"GO_Biological_Process_2023"` | Gene set library name or `.gmt` file path |
| `min_size` | `int` | No | `15` | Minimum gene set size |
| `max_size` | `int` | No | `500` | Maximum gene set size |
| `permutation_num` | `int` | No | `100` | Number of permutations |

- **Returns**: `pd.DataFrame` — columns: `Term`, `ES`, `NES`, `NOM p-val`, `FDR q-val`, `FWER p-val`, `Tag %`, `Lead_genes`

#### `run_go(gene_list, ontology="BP", cutoff=0.05)`

Run GO enrichment analysis (convenience method).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `gene_list` | `list[str]` | Yes | — | Gene list |
| `ontology` | `str` | No | `"BP"` | GO ontology type (`"BP"` / `"MF"` / `"CC"`) |
| `cutoff` | `float` | No | `0.05` | FDR cutoff |

- **Returns**: `pd.DataFrame`

#### `run_kegg(gene_list, cutoff=0.05)`

Run KEGG pathway enrichment analysis (convenience method).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `gene_list` | `list[str]` | Yes | — | Gene list |
| `cutoff` | `float` | No | `0.05` | FDR cutoff |

- **Returns**: `pd.DataFrame`

#### `get_top_pathways(results, n=20, sort_by="Adjusted P-value")`

Get top N pathways.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `results` | `pd.DataFrame` | Yes | — | Enrichment results DataFrame |
| `n` | `int` | No | `20` | Number of pathways to return |
| `sort_by` | `str` | No | `"Adjusted P-value"` | Sort field |

- **Returns**: `pd.DataFrame`

#### `export_results(results, output_path, format="csv")`

Export enrichment results.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `results` | `pd.DataFrame` | Yes | — | Enrichment results DataFrame |
| `output_path` | `str` | Yes | — | Output file path |
| `format` | `str` | No | `"csv"` | Output format (`"csv"` / `"json"` / `"tsv"`) |

- **Returns**: `str` — output file path
- **Example**:

```python
from msra_modules.bioinformatics import PathwayEnrichment

enricher = PathwayEnrichment(organism="human")
go_results = enricher.run_go(sig_genes["names"].tolist(), ontology="BP")
top_go = enricher.get_top_pathways(go_results, n=20)
enricher.export_results(top_go, "/output/go_results.csv", format="csv")
```

**Exceptions**: `ImportError` (gseapy not installed), `RuntimeError` (analysis failed), `ValueError` (unsupported format)

---

### `BatchCorrector`

**Description**: Batch effect detection and correction supporting ComBat and Harmony methods.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `batch_key` | `str` | No | `"batch"` | Batch column name in `obs` |
| `method` | `str` | No | `"combat"` | Default correction method (`"combat"` or `"harmony"`) |

**Methods**:

#### `detect_batch_effect(adata, n_pcs=50, threshold=0.10)`

Detect batch effect strength (via variance explained by batch on PCA).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `n_pcs` | `int` | No | `50` | Number of PCA components |
| `threshold` | `float` | No | `0.10` | Batch effect threshold (10%) |

- **Returns**: `dict` — contains `batch_variance_ratio`, `has_batch_effect`, `recommendation`, `pca_variance_explained`, `n_batches`

#### `run_combat(adata, key=None)`

Run ComBat batch correction (modifies `adata.X` in-place).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `key` | `str` | No | `None` | obs column to correct (defaults to `self.batch_key`) |

- **Returns**: `AnnData` (modified in-place and returned)

#### `run_harmony(adata, basis="X_pca", adjusted_basis="X_pca_harmony")`

Run Harmony batch correction (in PCA embedding space).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `basis` | `str` | No | `"X_pca"` | Input embedding key |
| `adjusted_basis` | `str` | No | `"X_pca_harmony"` | Adjusted embedding key |

- **Returns**: `AnnData` (adds `obsm[adjusted_basis]`)

#### `compare_before_after(adata_raw, adata_corrected, n_pcs=50)`

Compare correction effect before and after.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata_raw` | `AnnData` | Yes | — | Pre-correction AnnData |
| `adata_corrected` | `AnnData` | Yes | — | Post-correction AnnData |
| `n_pcs` | `int` | No | `50` | Number of PCA components |

- **Returns**: `dict` — contains `raw_batch_variance_ratio`, `corrected_batch_variance_ratio`, `improvement`, `raw_per_pc_variance`, `corrected_per_pc_variance`
- **Example**:

```python
from msra_modules.bioinformatics import BatchCorrector

corrector = BatchCorrector(batch_key="batch")
detection = corrector.detect_batch_effect(adata)
if detection["has_batch_effect"]:
    adata_corrected = corrector.run_combat(adata)
    comparison = corrector.compare_before_after(adata, adata_corrected)
```

**Exceptions**: `ImportError` (scanpy/harmonypy not installed), `ValueError` (batch key not found or insufficient batches)

---

### `BioQualityGateChecker`

**Description**: Bioinformatics quality gate checker implementing Gate Bio-1.5 (data quality gate) and Gate Bio-3.5 (results quality gate).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `study_id` | `str` | Yes | — | Study ID |
| `project_root` | `str` | No | `None` | Project root directory |

**Methods**:

#### `run_bio_gate_15(adata, sample_info=None, batch_key=None)`

Execute Gate Bio-1.5 with all 5 checks: count matrix integrity, sample consistency, library size, gene annotation coverage, batch effect detection.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `adata` | `AnnData` | Yes | — | AnnData object |
| `sample_info` | `pd.DataFrame` | No | `None` | Sample info DataFrame |
| `batch_key` | `str` | No | `None` | Batch column name |

- **Returns**: `GateResult` — verdict (`PASS` / `CONDITIONAL` / `BLOCKED`)

#### `run_bio_gate_35(de_results, enrichment_df=None, visualization_paths=None)`

Execute Gate Bio-3.5 with all 5 checks: p-value distribution, log2FC-p-value consistency, multiple testing correction, enrichment FDR, visualization consistency.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `de_results` | `pd.DataFrame` | Yes | — | DE results (must contain pvals/pvals_adj columns) |
| `enrichment_df` | `pd.DataFrame` | No | `None` | Pathway enrichment results |
| `visualization_paths` | `list[str]` | No | `None` | Visualization file path list |

- **Returns**: `GateResult`
- **Example**:

```python
from msra_modules.bioinformatics import BioQualityGateChecker

checker = BioQualityGateChecker(study_id="BIO-2026-001")
gate_15 = checker.run_bio_gate_15(adata, sample_info=sample_df, batch_key="batch")
gate_35 = checker.run_bio_gate_35(de_table, enrichment_df=go_results)
print(gate_15.verdict, gate_35.verdict)
```

**Exceptions**: `ImportError` (scanpy/scipy not installed — corresponding check items marked as FAIL/SKIP)

---

## Full Usage Example

```python
from msra_modules.bioinformatics import (
    ScRNASeqLoader, SingleCellQC, DimensionalityReduction,
    DifferentialExpression, PathwayEnrichment, BatchCorrector,
    BioQualityGateChecker,
)

# 1. Load data
loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("/data/pbmc_10x/")

# 2. Quality control
qc = SingleCellQC(min_genes=200, max_genes=5000, max_pct_mito=20.0)
adata = qc.run_qc(adata)

# 3. Batch correction (if batch info available)
corrector = BatchCorrector(batch_key="batch")
detection = corrector.detect_batch_effect(adata)
if detection["has_batch_effect"]:
    adata = corrector.run_combat(adata)

# 4. Dimensionality reduction & clustering
dr = DimensionalityReduction(n_pcs=50)
adata = dr.run_full_pipeline(adata, resolution=1.0)

# 5. Differential expression
de = DifferentialExpression(method="wilcoxon")
markers = de.find_markers(adata, groupby="leiden")
de_table = de.get_de_table(adata, group="0")
sig_genes = de.filter_de_genes(de_table, log2fc_threshold=1.0, pval_threshold=0.05)

# 6. Pathway enrichment
enricher = PathwayEnrichment(organism="human")
go_results = enricher.run_go(sig_genes["names"].tolist(), ontology="BP")

# 7. Quality gates
checker = BioQualityGateChecker(study_id="BIO-2026-001")
gate_15 = checker.run_bio_gate_15(adata)
gate_35 = checker.run_bio_gate_35(de_table, enrichment_df=go_results)
```
