# Bioinformatics Module API Reference

> **Version**: v1.0.0 | **Date**: 2026-06-26 | **Status**: Stable
> **Module**: Bioinformatics | **Command**: `/bio`

---

## Table of Contents

- [ScRNASeqLoader — Single-Cell Data Loader](#scrnaseqloader)
- [SingleCellQC — Single-Cell Quality Control](#singlecellqc)
- [DimensionalityReduction — Dimensionality Reduction](#dimensionalityreduction)
- [DifferentialExpression — Differential Expression Analysis](#differentialexpression)
- [PathwayEnrichment — Pathway Enrichment Analysis](#pathwayenrichment)
- [BatchCorrector — Batch Effect Correction](#batchcorrector)
- [BioQualityGateChecker — Quality Gate Checker](#bioqualitygatechecker)

---

## ScRNASeqLoader

> Single-cell RNA-seq data loader supporting 10x MTX/H5, CSV expression matrices, and FASTA sequence files.

**Signature**:

```python
ScRNASeqLoader()
```

**Methods**:

### `read_10x_mtx`

```python
read_10x_mtx(mtx_dir: str, var_names: str = "gene_symbols", cache: bool = True) -> AnnData
```

Read 10x Genomics MTX format data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| mtx_dir | str | — | Required. 10x output directory (containing matrix.mtx, features.tsv, barcodes.tsv) |
| var_names | str | "gene_symbols" | Gene name type ("gene_symbols" or "gene_ids") |
| cache | bool | True | Whether to cache |

**Returns**: `AnnData` — Single-cell expression matrix

**Example**:

```python
from msra_modules.bioinformatics import ScRNASeqLoader

loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("data/pbmc_10x/")
print(f"Cells: {adata.shape[0]}, Genes: {adata.shape[1]}")
```

**Exceptions**: `FileNotFoundError` — directory not found; `ImportError` — scanpy not installed

### `read_10x_h5`

```python
read_10x_h5(h5_path: str, genome: Optional[str] = None) -> AnnData
```

Read 10x Genomics H5 format data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| h5_path | str | — | Required. H5 file path |
| genome | Optional[str] | None | Genome name (optional) |

**Returns**: `AnnData`

### `read_csv`

```python
read_csv(csv_path: str, **kwargs) -> AnnData
```

Read CSV format expression matrix. `**kwargs` are passed to `pandas.read_csv`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| csv_path | str | — | Required. CSV file path |
| **kwargs | — | — | Arguments passed to pandas.read_csv |

**Returns**: `AnnData`

### `read_fasta`

```python
read_fasta(fasta_path: str) -> List[SeqRecord]
```

Read FASTA sequence file (requires Biopython).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| fasta_path | str | — | Required. FASTA file path |

**Returns**: `List[SeqRecord]` — List of Biopython sequence records

**Exceptions**: `ImportError` — Biopython not installed

### `get_metadata`

```python
get_metadata() -> Dict
```

Get metadata of currently loaded data.

**Returns**: `Dict` — Contains `n_cells`, `n_genes`, `obs_columns`, `var_columns`, `is_sparse`

### Convenience Function

```python
from msra_modules.bioinformatics import read_10x_mtx
adata = read_10x_mtx("data/pbmc_10x/")
```

---

## SingleCellQC

> Single-cell quality control supporting cell/gene filtering based on gene count, mitochondrial percentage, and other metrics.

**Signature**:

```python
SingleCellQC(min_genes: int = 200, max_genes: int = 5000, max_pct_mito: float = 20.0, min_cells: int = 3)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| min_genes | int | 200 | Minimum genes per cell |
| max_genes | int | 5000 | Maximum genes per cell |
| max_pct_mito | float | 20.0 | Maximum mitochondrial gene percentage |
| min_cells | int | 3 | Minimum cells per gene |

**Methods**:

### `compute_qc_metrics`

```python
compute_qc_metrics(adata: AnnData) -> AnnData
```

Compute QC metrics (mark mitochondrial genes, calculate n_genes_by_counts, pct_counts_mt, etc.). Modifies in-place and returns.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |

**Returns**: `AnnData` — AnnData with QC metrics

### `filter_cells`

```python
filter_cells(adata: AnnData, verbose: bool = True) -> AnnData
```

Filter low-quality cells based on gene count and mitochondrial percentage.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| verbose | bool | True | Whether to print filtering info |

**Returns**: `AnnData` — Filtered AnnData

### `filter_genes`

```python
filter_genes(adata: AnnData, verbose: bool = True) -> AnnData
```

Filter low-expression genes based on minimum cell count.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| verbose | bool | True | Whether to print filtering info |

**Returns**: `AnnData` — Filtered AnnData

### `run_qc`

```python
run_qc(adata: AnnData, verbose: bool = True) -> AnnData
```

Run complete QC pipeline (compute_qc_metrics → filter_cells → filter_genes).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| verbose | bool | True | Whether to print info |

**Returns**: `AnnData` — QC'd AnnData

**Example**:

```python
from msra_modules.bioinformatics import ScRNASeqLoader, SingleCellQC

loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("data/pbmc_10x/")

qc = SingleCellQC(min_genes=200, max_genes=5000, max_pct_mito=20.0)
adata = qc.run_qc(adata)
print(f"After QC: {adata.shape[0]} cells, {adata.shape[1]} genes")
```

### `get_qc_summary`

```python
get_qc_summary(adata: AnnData) -> Dict
```

Get QC summary statistics.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |

**Returns**: `Dict` — Contains `n_cells`, `n_genes`, `mean_genes_per_cell`, `mean_counts_per_cell`, `mean_pct_mito`, `max_pct_mito`

---

## DimensionalityReduction

> Dimensionality reduction providing normalization, HVG selection, PCA, UMAP, and Leiden clustering pipeline.

**Signature**:

```python
DimensionalityReduction(n_pcs: int = 50, n_neighbors: int = 15)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| n_pcs | int | 50 | Number of PCA components |
| n_neighbors | int | 15 | Number of neighbors |

**Methods**:

### `normalize_and_log`

```python
normalize_and_log(adata: AnnData, target_sum: int = 1e4) -> AnnData
```

Normalize and log-transform.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| target_sum | int | 1e4 | Target sum |

**Returns**: `AnnData` — Normalized AnnData

### `find_hvg`

```python
find_hvg(adata: AnnData, n_top_genes: int = 2000) -> AnnData
```

Find highly variable genes.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| n_top_genes | int | 2000 | Number of top HVGs |

**Returns**: `AnnData` — AnnData with HVG markers

### `run_pca`

```python
run_pca(adata: AnnData) -> AnnData
```

Run PCA dimensionality reduction.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |

**Returns**: `AnnData` — AnnData with PCA results (`obsm["X_pca"]`)

### `run_umap`

```python
run_umap(adata: AnnData) -> AnnData
```

Run UMAP dimensionality reduction (requires PCA first).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |

**Returns**: `AnnData` — AnnData with UMAP results (`obsm["X_umap"]`)

### `cluster`

```python
cluster(adata: AnnData, resolution: float = 1.0) -> AnnData
```

Leiden clustering analysis.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| resolution | float | 1.0 | Clustering resolution |

**Returns**: `AnnData` — AnnData with clustering results (`obs["leiden"]`)

### `run_full_pipeline`

```python
run_full_pipeline(adata: AnnData, resolution: float = 1.0) -> AnnData
```

Run complete dimensionality reduction pipeline (normalize_and_log → find_hvg → run_pca → run_umap → cluster).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| resolution | float | 1.0 | Clustering resolution |

**Returns**: `AnnData` — Processed AnnData

**Example**:

```python
from msra_modules.bioinformatics import DimensionalityReduction

dr = DimensionalityReduction(n_pcs=50)
adata = dr.run_full_pipeline(adata, resolution=0.8)
print(f"Clusters: {adata.obs['leiden'].nunique()}")
```

---

## DifferentialExpression

> Differential expression analysis supporting Wilcoxon, t-test, and logreg methods, with marker gene discovery and DE gene filtering.

**Signature**:

```python
DifferentialExpression(method: str = "wilcoxon")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| method | str | "wilcoxon" | DE method ("wilcoxon", "t-test", "logreg") |

**Methods**:

### `find_markers`

```python
find_markers(adata: AnnData, groupby: str = "leiden", use_raw: bool = True) -> pd.DataFrame
```

Find marker genes.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| groupby | str | "leiden" | Grouping column name |
| use_raw | bool | True | Whether to use raw data |

**Returns**: `pd.DataFrame` — Marker genes DataFrame (each column is markers for one cluster)

### `get_de_table`

```python
get_de_table(adata: AnnData, group: str, n_genes: int = 100) -> pd.DataFrame
```

Get differential expression table for a specified group.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| group | str | — | Required. Group name |
| n_genes | int | 100 | Number of genes to return |

**Returns**: `pd.DataFrame` — DE table (contains log2FC, pvals_adj)

### `filter_de_genes`

```python
filter_de_genes(de_table: pd.DataFrame, log2fc_threshold: float = 1.0, pval_threshold: float = 0.05) -> pd.DataFrame
```

Filter significant DE genes.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| de_table | pd.DataFrame | — | Required. DE table |
| log2fc_threshold | float | 1.0 | log2FC threshold |
| pval_threshold | float | 0.05 | p-value threshold |

**Returns**: `pd.DataFrame` — Filtered DE genes (with `direction` column: "up"/"down")

**Example**:

```python
from msra_modules.bioinformatics import DifferentialExpression

de = DifferentialExpression(method="wilcoxon")
markers = de.find_markers(adata, groupby="leiden")
de_table = de.get_de_table(adata, group="0", n_genes=200)
sig_genes = de.filter_de_genes(de_table, log2fc_threshold=1.0, pval_threshold=0.05)
print(f"Significant DE genes: {len(sig_genes)}")
```

---

## PathwayEnrichment

> Pathway enrichment analysis engine implementing GO (BP/MF/CC), KEGG, GSEA, and Enrichr via gseapy.

**Signature**:

```python
PathwayEnrichment(organism: str = "human", gene_sets: Optional[str] = None, outdir: Optional[str] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| organism | str | "human" | Organism name ("human", "mouse", "rat", etc.) |
| gene_sets | Optional[str] | None | Custom .gmt gene set file path (optional) |
| outdir | Optional[str] | None | Output directory (optional) |

**Methods**:

### `run_go`

```python
run_go(gene_list: List[str], ontology: str = "BP", cutoff: float = 0.05) -> pd.DataFrame
```

Run GO enrichment analysis (convenience method).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| gene_list | List[str] | — | Required. Gene list (gene symbols) |
| ontology | str | "BP" | GO ontology type ("BP" / "MF" / "CC") |
| cutoff | float | 0.05 | FDR threshold |

**Returns**: `pd.DataFrame` — GO enrichment results (Term, Overlap, P-value, Adjusted P-value, Genes)

**Exceptions**: `ValueError` — ontology not BP/MF/CC; `RuntimeError` — analysis failed

### `run_kegg`

```python
run_kegg(gene_list: List[str], cutoff: float = 0.05) -> pd.DataFrame
```

Run KEGG pathway enrichment analysis.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| gene_list | List[str] | — | Required. Gene list |
| cutoff | float | 0.05 | FDR threshold |

**Returns**: `pd.DataFrame` — KEGG pathway enrichment results

### `run_gsea`

```python
run_gsea(ranked_genes: pd.Series, gene_sets: str = "GO_Biological_Process_2023", min_size: int = 15, max_size: int = 500, permutation_num: int = 100) -> pd.DataFrame
```

Run GSEA gene set enrichment analysis.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| ranked_genes | pd.Series | — | Required. Ranked gene series (index=gene symbols, values=ranking metric) |
| gene_sets | str | "GO_Biological_Process_2023" | Gene set library name or .gmt file path |
| min_size | int | 15 | Minimum gene set size |
| max_size | int | 500 | Maximum gene set size |
| permutation_num | int | 100 | Number of permutations |

**Returns**: `pd.DataFrame` — GSEA results (Term, ES, NES, NOM p-val, FDR q-val, Lead_genes)

**Exceptions**: `RuntimeError` — analysis failed

### `run_enrichr`

```python
run_enrichr(gene_list: List[str], gene_sets_library: str = "GO_Biological_Process_2023", cutoff: float = 0.05) -> pd.DataFrame
```

Run Enrichr over-representation analysis.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| gene_list | List[str] | — | Required. Gene list |
| gene_sets_library | str | "GO_Biological_Process_2023" | Gene set library name |
| cutoff | float | 0.05 | FDR threshold |

**Returns**: `pd.DataFrame` — Enrichr results

**Exceptions**: `RuntimeError` — analysis failed

### `get_top_pathways`

```python
get_top_pathways(results: pd.DataFrame, n: int = 20, sort_by: str = "Adjusted P-value") -> pd.DataFrame
```

Get top N pathways.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| results | pd.DataFrame | — | Required. Enrichment results DataFrame |
| n | int | 20 | Number of pathways to return |
| sort_by | str | "Adjusted P-value" | Sort field |

**Returns**: `pd.DataFrame` — Sorted top N results

### `export_results`

```python
export_results(results: pd.DataFrame, output_path: str, format: str = "csv") -> str
```

Export enrichment results.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| results | pd.DataFrame | — | Required. Enrichment results |
| output_path | str | — | Required. Output file path |
| format | str | "csv" | Output format ("csv" / "json" / "tsv") |

**Returns**: `str` — Output file path

**Exceptions**: `ValueError` — unsupported format

**Example**:

```python
from msra_modules.bioinformatics import PathwayEnrichment

enricher = PathwayEnrichment(organism="human")
go_results = enricher.run_go(gene_list=["CD3D", "CD3E", "IL7R"], ontology="BP")
top_pathways = enricher.get_top_pathways(go_results, n=10)
enricher.export_results(go_results, "output/go_enrichment.csv")
```

---

## BatchCorrector

> Batch effect detection and correction supporting ComBat and Harmony methods.

**Signature**:

```python
BatchCorrector(batch_key: str = "batch", method: str = "combat")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| batch_key | str | "batch" | Batch column name in obs |
| method | str | "combat" | Default correction method ("combat" or "harmony") |

**Methods**:

### `detect_batch_effect`

```python
detect_batch_effect(adata: AnnData, n_pcs: int = 50, threshold: float = 0.10) -> Dict[str, Any]
```

Detect batch effect intensity via variance explained by batch on PCA.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| n_pcs | int | 50 | Number of PCA components |
| threshold | float | 0.10 | Batch effect threshold (default 10%) |

**Returns**: `Dict` — Contains `batch_variance_ratio`, `has_batch_effect`, `recommendation`, `pca_variance_explained`, `n_batches`

**Exceptions**: `ValueError` — batch column not found or < 2 batches

### `run_combat`

```python
run_combat(adata: AnnData, key: Optional[str] = None) -> AnnData
```

Run ComBat batch correction (modifies `adata.X` in-place).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| key | Optional[str] | None | obs column to correct (defaults to batch_key) |

**Returns**: `AnnData` — Corrected data

### `run_harmony`

```python
run_harmony(adata: AnnData, basis: str = "X_pca", adjusted_basis: str = "X_pca_harmony") -> AnnData
```

Run Harmony batch correction in PCA embedding space.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| basis | str | "X_pca" | Input embedding key |
| adjusted_basis | str | "X_pca_harmony" | Corrected embedding key |

**Returns**: `AnnData` — Corrected data (adds `obsm[adjusted_basis]`)

**Exceptions**: `ImportError` — harmonypy not installed

### `compare_before_after`

```python
compare_before_after(adata_raw: AnnData, adata_corrected: AnnData, n_pcs: int = 50) -> Dict[str, Any]
```

Compare correction effectiveness before and after.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata_raw | AnnData | — | Required. Pre-correction AnnData |
| adata_corrected | AnnData | — | Required. Post-correction AnnData |
| n_pcs | int | 50 | Number of PCA components |

**Returns**: `Dict` — Contains `raw_batch_variance_ratio`, `corrected_batch_variance_ratio`, `improvement`

**Example**:

```python
from msra_modules.bioinformatics import BatchCorrector

corrector = BatchCorrector(batch_key="batch")
detection = corrector.detect_batch_effect(adata)
if detection["has_batch_effect"]:
    adata_corrected = corrector.run_combat(adata)
    comparison = corrector.compare_before_after(adata, adata_corrected)
    print(f"Improvement: {comparison['improvement']:.3f}")
```

---

## BioQualityGateChecker

> Bioinformatics quality gate checker encapsulating Gate Bio-1.5 (data quality) and Gate Bio-3.5 (results quality).

**Signature**:

```python
BioQualityGateChecker(study_id: str, project_root: Optional[str] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| study_id | str | — | Required. Study ID |
| project_root | Optional[str] | None | Project root directory (optional) |

**Methods**:

### `run_bio_gate_15`

```python
run_bio_gate_15(adata: AnnData, sample_info: Optional[pd.DataFrame] = None, batch_key: Optional[str] = None) -> GateResult
```

Execute Gate Bio-1.5 with 5 checks: count matrix integrity, sample info consistency, library size, gene annotation coverage, batch effect detection.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| adata | AnnData | — | Required. AnnData object |
| sample_info | Optional[pd.DataFrame] | None | Sample info DataFrame (optional) |
| batch_key | Optional[str] | None | Batch column name (optional) |

**Returns**: `GateResult` — Verdict (PASS / CONDITIONAL / BLOCKED)

### `run_bio_gate_35`

```python
run_bio_gate_35(de_results: pd.DataFrame, enrichment_df: Optional[pd.DataFrame] = None, visualization_paths: Optional[List[str]] = None) -> GateResult
```

Execute Gate Bio-3.5 with 5 checks: p-value distribution, log2FC-pvalue consistency, multiple testing correction, pathway enrichment FDR, visualization consistency.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| de_results | pd.DataFrame | — | Required. DE results (must contain pvals, pvals_adj columns) |
| enrichment_df | Optional[pd.DataFrame] | None | Pathway enrichment results (optional) |
| visualization_paths | Optional[List[str]] | None | Visualization file paths (optional) |

**Returns**: `GateResult` — Verdict

**GateResult Properties**:

| Property | Type | Description |
|----------|------|-------------|
| gate_type | GateType | Gate type |
| study_id | str | Study ID |
| verdict | GateVerdict | Verdict (PASS / CONDITIONAL / BLOCKED) |
| total_items | int | Total check items |
| passed_items | int | Passed items |
| failed_items | int | Failed items |
| key_items_status | str | Key items status |
| check_results | List[CheckItemResult] | Detailed results per item |
| risks | List[str] | Risk list |
| pass_rate | float | Pass rate |

**Example**:

```python
from msra_modules.bioinformatics import BioQualityGateChecker

checker = BioQualityGateChecker(study_id="BIO-2026-001")

# Gate Bio-1.5: Data quality
gate_15 = checker.run_bio_gate_15(adata, batch_key="batch")
print(f"Bio-1.5 verdict: {gate_15.verdict.value}")

# Gate Bio-3.5: Results quality
gate_35 = checker.run_bio_gate_35(de_table, enrichment_df=go_results)
print(f"Bio-3.5 verdict: {gate_35.verdict.value}")
print(f"Pass rate: {gate_35.pass_rate:.1%}")
```

---

## Shared Types Reference

### CheckItemResult

> Single check item result.

| Property | Type | Description |
|----------|------|-------------|
| item_id | str | Check item ID |
| name | str | Check item name |
| is_key | bool | Whether it is a key item |
| status | str | Status (PASS / FAIL / N/A / SKIP) |
| evidence | str | Evidence description |
| notes | str | Notes |

### GateVerdict

> Gate verdict enum.

| Value | Description |
|-------|-------------|
| PASS | All passed |
| CONDITIONAL | Conditional pass (1-2 non-key items failed) |
| BLOCKED | Blocked (3+ items failed or key item failed) |
