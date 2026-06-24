# MSRA Bioinformatics Module User Tutorial

> **Module Version**: v1.1.0 | **Document Date**: 2026-06-25 | **Status**: Stable
> **Command Entry**: `/msra-bio` | **MSRA Version**: v1.0.0+

---

## 1. Module Overview & Use Cases

### Overview

The MSRA Bioinformatics module provides end-to-end single-cell RNA-seq / gene expression analysis capabilities. Users can complete the full analysis pipeline — from data loading, quality control, dimensionality reduction, differential expression, to pathway enrichment — via the `/msra-bio` command without switching between multiple tools.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| Data Loading | Supports 10x Genomics MTX directory, 10x H5 file, CSV/TSV count matrix |
| Quality Control | `SingleCellQC` filters low-quality cells/genes, supports mitochondrial gene ratio filtering |
| Dimensionality Reduction | PCA → UMAP → Leiden clustering via `DimensionalityReduction` |
| Differential Expression | Wilcoxon rank-sum test / DESeq2 via `DifferentialExpression` |
| Pathway Enrichment | GO (BP/MF/CC) / KEGG / GSEA via gseapy-based `PathwayEnrichment` |
| Batch Correction | ComBat / Harmony via `BatchCorrector` |
| Quality Gates | Gate Bio-1.5 (data QC) + Gate Bio-3.5 (result QC) via `BioQualityGateChecker` |

### Use Cases

- Standard analysis pipeline for single-cell RNA-seq data (PBMC, tumor tissue, etc.)
- Differential gene expression analysis with volcano plot / heatmap visualization
- GO / KEGG / GSEA pathway enrichment analysis
- Batch effect detection and correction for multi-batch data
- Exporting differential gene lists as covariates for the MSRA main Pipeline (Stage 3)

---

## 2. Installation

### Install bioinformatics extra dependencies

```bash
pip install -e ".[bioinformatics]"
```

### Core Dependencies

```toml
scanpy >= 1.9          # Single-cell analysis core library
anndata >= 0.9         # Data structure
pydeseq2 >= 0.4        # DESeq2 differential expression
gseapy >= 1.0          # Pathway enrichment analysis
harmonypy >= 0.0.9     # Harmony batch correction
```

### Verify Installation

```bash
python -c "from msra_modules.bioinformatics import ScRNASeqLoader, PathwayEnrichment, BioQualityGateChecker; print('OK')"
```

---

## 3. Data Preparation

### Supported Data Formats

| Format | Description | Typical Source |
|--------|-------------|----------------|
| 10x MTX directory | Contains `matrix.mtx`, `features.tsv`, `barcodes.tsv` | Cell Ranger output |
| 10x H5 file | Single `.h5` file | Cell Ranger output |
| CSV/TSV matrix | Rows=genes, columns=cells (or vice versa) | Custom pipelines |

### Sample Information File (Optional)

If you have grouping information such as batch or condition, prepare a `sample_info.csv`:

```csv
sample_id,batch,condition
AAACATACAACCAC-1,batch1,control
AAACATTGAGCTAC-1,batch1,treatment
AAACATTGATCAGC-1,batch2,control
...
```

### Example: Prepare Mock Data

```python
import numpy as np
import pandas as pd

# Generate mock count matrix (200 genes × 50 cells)
np.random.seed(42)
counts = np.random.negative_binomial(5, 0.3, size=(200, 50)).astype(float)
genes = [f"Gene_{i}" for i in range(200)]
cells = [f"Cell_{i}" for i in range(50)]

df = pd.DataFrame(counts, index=genes, columns=cells)
df.to_csv("mock_counts.csv")
print(f"Count matrix: {df.shape[0]} genes × {df.shape[1]} cells")
```

---

## 4. Complete Analysis Workflow Demo

### Launch via Command

```
/msra-bio --data filtered_feature_bc_matrix/ --samples sample_info.csv
```

### Phase 0: Interactive Configuration

The system will guide you to confirm:
1. **Data source type** (10x MTX / H5 / CSV)
2. **Analysis target** (full pipeline / DE only / clustering only / enrichment only)
3. **QC parameters** (`min_genes`, `min_cells`, `max_pct_mito`)
4. **Dimensionality reduction parameters** (`n_pcs`, `n_neighbors`, `resolution`)

### Phase 1: Data Loading & Quality Control

```python
from msra_modules.bioinformatics import (
    ScRNASeqLoader, SingleCellQC, DimensionalityReduction,
    BioQualityGateChecker,
)

# Step 1.1: Load data
loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("filtered_feature_bc_matrix/")
print(f"Loaded: {adata.shape[0]} cells × {adata.shape[1]} genes")

# Step 1.2: Gate Bio-1.5 data quality gate
checker = BioQualityGateChecker(study_id="BIO-2026-001")
gate_result = checker.run_gate_bio15(adata=adata, sample_info=None)
print(f"Gate Bio-1.5: {gate_result.verdict}")  # PASS / CONDITIONAL / BLOCKED

# Step 1.3: QC filtering
qc = SingleCellQC(min_genes=200, min_cells=3, max_pct_mito=20)
adata = qc.filter_cells(adata)
adata = qc.filter_genes(adata)
print(f"After QC: {adata.shape[0]} cells × {adata.shape[1]} genes")

# Step 1.4: Normalization
dr = DimensionalityReduction(n_pcs=50, n_neighbors=15)
adata = dr.normalize_and_log(adata)
adata = dr.find_hvg(adata, n_top_genes=2000)
```

### Phase 2: Background Analysis (Clustering + DE + Enrichment)

```python
from msra_modules.bioinformatics import (
    DifferentialExpression, PathwayEnrichment,
)

# Task A: Dimensionality reduction & clustering
adata = dr.run_pca(adata)
adata = dr.run_umap(adata)
adata = dr.run_leiden(adata, resolution=0.5)
print(f"Clusters: {adata.obs['leiden'].nunique()}")

# Task B: Differential expression analysis
de = DifferentialExpression(method="wilcoxon")
de_results = de.find_markers(adata, groupby="leiden")
print(f"DE genes found: {len(de_results)}")

# Task C: Pathway enrichment analysis
top_genes = de_results.head(200)["gene"].tolist()
enricher = PathwayEnrichment(organism="human")
go_results = enricher.run_go(top_genes, ontology="BP")
kegg_results = enricher.run_kegg(top_genes)
print(f"GO BP enriched terms: {len(go_results)}")
print(f"KEGG enriched pathways: {len(kegg_results)}")
```

### Phase 3: Result Review + Gate Bio-3.5

```python
# Gate Bio-3.5 analysis result gate
gate_result = checker.run_gate_bio35(
    pvalues=de_results["pvals"].values,
    padj=de_results["pvals_adj"].values,
    log2fc=de_results["logfoldchanges"].values,
)
print(f"Gate Bio-3.5: {gate_result.verdict}")
```

### Phase 4: Report Generation

```python
from msra_modules.bioinformatics import BioVisualizer

viz = BioVisualizer()
viz.plot_volcano(de_results, save_path="volcano_plot.png")
viz.plot_umap(adata, color="leiden", save_path="umap_plot.png")

# Export differential gene list as CSV
de_results.to_csv("differential_genes.csv", index=False)
```

---

## 5. Differential Expression Analysis & Volcano Plot Interpretation

### Differential Expression Analysis

```python
from msra_modules.bioinformatics import DifferentialExpression

# Using Wilcoxon rank-sum test (default, fast)
de = DifferentialExpression(method="wilcoxon")
results = de.find_markers(adata, groupby="leiden")

# Result columns:
# - gene: gene name
# - logfoldchanges: log2 fold change
# - pvals: raw p-value
# - pvals_adj: adjusted p-value (BH correction)
# - pct_nz_group: expression fraction in this cluster
# - pct_nz_reference: expression fraction in other clusters
```

### Volcano Plot Interpretation

```python
from msra_modules.bioinformatics import BioVisualizer

viz = BioVisualizer()
fig = viz.plot_volcano(
    results,
    log2fc_threshold=0.5,
    padj_threshold=0.05,
    save_path="volcano_plot.png",
)
```

**Volcano Plot Reading Guide**:

| Region | Position | Meaning |
|--------|----------|---------|
| Top-right | log2FC > 0, padj < 0.05 | Significantly upregulated genes |
| Top-left | log2FC < 0, padj < 0.05 | Significantly downregulated genes |
| Bottom-center | padj > 0.05 | Non-significant genes |
| Horizontal line at top | padj = 0.05 | Significance threshold line |

---

## 6. Pathway Enrichment Analysis

### GO Enrichment Analysis

```python
from msra_modules.bioinformatics import PathwayEnrichment

enricher = PathwayEnrichment(organism="human")

# GO Biological Process
go_bp = enricher.run_go(gene_list=top_genes, ontology="BP")
# GO Molecular Function
go_mf = enricher.run_go(gene_list=top_genes, ontology="MF")
# GO Cellular Component
go_cc = enricher.run_go(gene_list=top_genes, ontology="CC")

print(f"GO BP enriched terms: {len(go_bp)}")
print(go_bp[["Term", "Adjusted P-value", "Overlap"]].head(10))
```

### KEGG Pathway Enrichment

```python
kegg = enricher.run_kegg(gene_list=top_genes)
print(f"KEGG enriched pathways: {len(kegg)}")
print(kegg[["Term", "Adjusted P-value", "Overlap"]].head(10))
```

### GSEA Analysis (requires ranked gene list)

```python
# Ranked gene list based on log2FC
ranked_genes = results.set_index("gene")["logfoldchanges"].sort_values(ascending=False)

gsea = enricher.run_gsea(ranked_genes, gene_sets="KEGG_2021_Human")
print(f"GSEA enriched gene sets: {len(gsea)}")
```

### Enrichment Dot Plot

```python
viz = BioVisualizer()
viz.plot_enrichment_dotplot(go_bp, save_path="go_dotplot.png")
```

---

## 7. Quality Gates

### Gate Bio-1.5 — Data Quality Gate

> Executed in Phase 1 (after data loading), blocks unqualified data from entering the analysis pipeline.
> Implementation: `msra_modules/bioinformatics/quality_gates.py` → `BioQualityGateChecker`

| # | Check Item | Critical | Pass Criteria |
|---|------------|----------|---------------|
| 1 | Count matrix integrity | 🔑 | No NaN, no negative values, all integers |
| 2 | Sample info consistency | 🔑 | All sample_info IDs exist in AnnData |
| 3 | Library size合理性 | | >90% within median ± 3IQR |
| 4 | Gene annotation coverage | | gene_name non-null rate > 80% |
| 5 | Batch effect detection | | Batch variance on PCA < 10% |

**Verdict Rules**:
- **PASS**: 5/5 checks passed
- **CONDITIONAL**: 3-4/5 passed and all 🔑 passed
- **BLOCKED**: ≤ 2/5 passed or any 🔑 failed (**blocks the pipeline**)

### Gate Bio-3.5 — Analysis Result Gate

> Executed in Phase 3 (before result review), validates analysis result quality.

| # | Check Item | Critical | Pass Criteria |
|---|------------|----------|---------------|
| 1 | P-value distribution | 🔑 | P ∈ [0,1], no abnormal concentration |
| 2 | log2FC-P-value consistency | 🔑 | Spearman ρ > 0.1 |
| 3 | Multiple testing correction | 🔑 | padj computed and valid |
| 4 | Enrichment FDR | | At least 1 pathway with padj < 0.05 |
| 5 | Visualization consistency | | Visualization files exist and significant gene count matches |

### Python Usage Example

```python
from msra_modules.bioinformatics import BioQualityGateChecker

checker = BioQualityGateChecker(study_id="BIO-2026-001")

# Gate Bio-1.5
result_15 = checker.run_gate_bio15(
    adata=adata,
    sample_info=sample_info_df,  # optional
)
print(f"Bio-1.5 verdict: {result_15.verdict}")
for item in result_15.items:
    print(f"  [{item.status}] {item.name}: {item.message}")

# Gate Bio-3.5
result_35 = checker.run_gate_bio35(
    pvalues=de_results["pvals"].values,
    padj=de_results["pvals_adj"].values,
    log2fc=de_results["logfoldchanges"].values,
    enrichment_df=go_bp,
)
print(f"Bio-3.5 verdict: {result_35.verdict}")
```

---

## 8. Integration with Main Pipeline

### Export Differential Gene List for Main Pipeline

After differential expression analysis, results can be exported as CSV for `/msra-exec` (Stage 3) to use as covariates:

```python
# Export standard format CSV
de_results[["gene", "logfoldchanges", "pvals_adj"]].to_csv(
    "MSRA/data/bio_covariates.csv",
    index=False,
    header=["gene", "log2FC", "padj"],
)
```

### Automatic Pipeline Integration

In Phase 4, select the "Integrate with Pipeline" option. The system will:
1. Write the differential gene list to `MSRA/data/bio_covariates.csv`
2. Automatically trigger `/msra-exec` to incorporate it as a covariate in Stage 3

### Command-Line Direct Invocation

```
/msra-bio --data filtered_feature_bc_matrix/ --mode de --integrate-pipeline
```

---

## 9. FAQ

### Q1: scanpy installation fails?

scanpy has many dependencies. We recommend using conda:

```bash
conda install -c conda-forge scanpy
```

### Q2: What if there is no batch information for Gate Bio-1.5 batch effect detection?

When `sample_info` does not contain a `batch` column, this check is automatically skipped, marked as N/A, and does not count toward the gate verdict.

### Q3: What if the gseapy Enrichr API times out?

The system automatically retries 3 times. If it still times out, it degrades to local analysis mode. You can also check your network connection or use a custom `.gmt` gene set file:

```python
enricher = PathwayEnrichment(organism="human", gene_sets="custom_genesets.gmt")
```

### Q4: What if too few cells remain after QC (< 100)?

This usually indicates data quality issues or overly strict QC parameters. Suggestions:
1. Check if `max_pct_mito` threshold is too low (default 20%)
2. Check if `min_genes` is too high (default 200)
3. Verify the data orientation (genes × cells or cells × genes)

### Q5: What if all padj values are 1 in differential expression results?

This usually means insufficient sample size or no clear difference between groups. Suggestions:
1. Increase sample size
2. Try a different DE method (`method="deseq2"`)
3. Lower the `log2FC` threshold

### Q6: What if batches are still separated on UMAP after batch correction?

- Try switching correction methods (ComBat → Harmony)
- Adjust Harmony's `theta` parameter
- Verify batch annotation is correct

---

> **Related Docs**: [SKILL.md](../../skills/bioinformatics/SKILL.md) | [Module PRD](../prd/bioinformatics-module-prd.md)
> **MSRA Docs Home**: [System Design](../system_design.md)
