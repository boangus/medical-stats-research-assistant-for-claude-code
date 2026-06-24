# MSRA 生物信息学模块用户教程

> **模块版本**: v1.1.0 | **文档日期**: 2026-06-25 | **状态**: Stable
> **命令入口**: `/msra-bio` | **适用 MSRA 版本**: v1.0.0+

---

## 1. 模块简介与适用场景

### 模块概述

MSRA Bioinformatics（生物信息学）模块提供端到端的单细胞 RNA-seq / 基因表达分析能力。用户通过 `/msra-bio` 命令即可完成从数据加载、质控、降维聚类、差异表达到通路富集的完整分析流程，无需在多个工具间切换。

### 核心能力

| 能力 | 说明 |
|------|------|
| 数据加载 | 支持 10x Genomics MTX 目录、10x H5 文件、CSV/TSV 计数矩阵 |
| 数据质控 | `SingleCellQC` 过滤低质量细胞/基因，支持线粒体基因比例过滤 |
| 降维聚类 | PCA → UMAP → Leiden 聚类，基于 `DimensionalityReduction` |
| 差异表达 | Wilcoxon 秩和检验 / DESeq2，`DifferentialExpression` |
| 通路富集 | GO (BP/MF/CC) / KEGG / GSEA，基于 gseapy 的 `PathwayEnrichment` |
| 批次校正 | ComBat / Harmony，`BatchCorrector` |
| 质量门闸 | Gate Bio-1.5（数据质控）+ Gate Bio-3.5（结果质控），`BioQualityGateChecker` |

### 适用场景

- 单细胞 RNA-seq 数据的标准分析流程（PBMC、肿瘤组织等）
- 差异基因表达分析及火山图/热图可视化
- GO / KEGG / GSEA 通路富集分析
- 多批次数据的批次效应检测与校正
- 将差异基因列表作为协变量接入 MSRA 主 Pipeline（Stage 3）

---

## 2. 安装依赖

### 安装 bioinformatics 扩展依赖

```bash
pip install -e ".[bioinformatics]"
```

### 核心依赖列表

```toml
scanpy >= 1.9          # 单细胞分析核心库
anndata >= 0.9         # 数据结构
pydeseq2 >= 0.4        # DESeq2 差异表达
gseapy >= 1.0          # 通路富集分析
harmonypy >= 0.0.9     # Harmony 批次校正
```

### 验证安装

```bash
python -c "from msra_modules.bioinformatics import ScRNASeqLoader, PathwayEnrichment, BioQualityGateChecker; print('OK')"
```

---

## 3. 数据准备

### 支持的数据格式

| 格式 | 说明 | 典型来源 |
|------|------|---------|
| 10x MTX 目录 | 包含 `matrix.mtx`, `features.tsv`, `barcodes.tsv` | Cell Ranger 输出 |
| 10x H5 文件 | 单个 `.h5` 文件 | Cell Ranger 输出 |
| CSV/TSV 矩阵 | 行=基因，列=细胞（或反之） | 自定义流程 |

### 样本信息文件（可选）

如果您有批次（batch）、条件（condition）等分组信息，请准备 `sample_info.csv`：

```csv
sample_id,batch,condition
AAACATACAACCAC-1,batch1,control
AAACATTGAGCTAC-1,batch1,treatment
AAACATTGATCAGC-1,batch2,control
...
```

### 示例：准备模拟数据

```python
import numpy as np
import pandas as pd

# 生成模拟 count matrix (200 基因 × 50 细胞)
np.random.seed(42)
counts = np.random.negative_binomial(5, 0.3, size=(200, 50)).astype(float)
genes = [f"Gene_{i}" for i in range(200)]
cells = [f"Cell_{i}" for i in range(50)]

df = pd.DataFrame(counts, index=genes, columns=cells)
df.to_csv("mock_counts.csv")
print(f"Count matrix: {df.shape[0]} genes × {df.shape[1]} cells")
```

---

## 4. 完整分析流程演示

### 通过命令启动

```
/msra-bio --data filtered_feature_bc_matrix/ --samples sample_info.csv
```

### Phase 0: 用户交互配置

系统将引导您确认：
1. **数据源类型**（10x MTX / H5 / CSV）
2. **分析目标**（完整流程 / 仅差异表达 / 仅聚类 / 仅富集）
3. **QC 参数**（`min_genes`, `min_cells`, `max_pct_mito`）
4. **降维参数**（`n_pcs`, `n_neighbors`, `resolution`）

### Phase 1: 数据加载与质控

```python
from msra_modules.bioinformatics import (
    ScRNASeqLoader, SingleCellQC, DimensionalityReduction,
    BioQualityGateChecker,
)

# Step 1.1: 加载数据
loader = ScRNASeqLoader()
adata = loader.read_10x_mtx("filtered_feature_bc_matrix/")
print(f"Loaded: {adata.shape[0]} cells × {adata.shape[1]} genes")

# Step 1.2: Gate Bio-1.5 数据质量门闸
checker = BioQualityGateChecker(study_id="BIO-2026-001")
gate_result = checker.run_gate_bio15(adata=adata, sample_info=None)
print(f"Gate Bio-1.5: {gate_result.verdict}")  # PASS / CONDITIONAL / BLOCKED

# Step 1.3: QC 过滤
qc = SingleCellQC(min_genes=200, min_cells=3, max_pct_mito=20)
adata = qc.filter_cells(adata)
adata = qc.filter_genes(adata)
print(f"After QC: {adata.shape[0]} cells × {adata.shape[1]} genes")

# Step 1.4: 标准化
dr = DimensionalityReduction(n_pcs=50, n_neighbors=15)
adata = dr.normalize_and_log(adata)
adata = dr.find_hvg(adata, n_top_genes=2000)
```

### Phase 2: 后台分析（降维聚类 + 差异表达 + 通路富集）

```python
from msra_modules.bioinformatics import (
    DifferentialExpression, PathwayEnrichment,
)

# Task A: 降维聚类
adata = dr.run_pca(adata)
adata = dr.run_umap(adata)
adata = dr.run_leiden(adata, resolution=0.5)
print(f"Clusters: {adata.obs['leiden'].nunique()}")

# Task B: 差异表达分析
de = DifferentialExpression(method="wilcoxon")
de_results = de.find_markers(adata, groupby="leiden")
print(f"DE genes found: {len(de_results)}")

# Task C: 通路富集分析
top_genes = de_results.head(200)["gene"].tolist()
enricher = PathwayEnrichment(organism="human")
go_results = enricher.run_go(top_genes, ontology="BP")
kegg_results = enricher.run_kegg(top_genes)
print(f"GO BP enriched terms: {len(go_results)}")
print(f"KEGG enriched pathways: {len(kegg_results)}")
```

### Phase 3: 结果审查 + Gate Bio-3.5

```python
# Gate Bio-3.5 分析结果门闸
gate_result = checker.run_gate_bio35(
    pvalues=de_results["pvals"].values,
    padj=de_results["pvals_adj"].values,
    log2fc=de_results["logfoldchanges"].values,
)
print(f"Gate Bio-3.5: {gate_result.verdict}")
```

### Phase 4: 生成报告

```python
from msra_modules.bioinformatics import BioVisualizer

viz = BioVisualizer()
viz.plot_volcano(de_results, save_path="volcano_plot.png")
viz.plot_umap(adata, color="leiden", save_path="umap_plot.png")

# 导出差异基因列表 CSV
de_results.to_csv("differential_genes.csv", index=False)
```

---

## 5. 差异表达分析 + 火山图解读

### 差异表达分析

```python
from msra_modules.bioinformatics import DifferentialExpression

# 使用 Wilcoxon 秩和检验（默认，速度快）
de = DifferentialExpression(method="wilcoxon")
results = de.find_markers(adata, groupby="leiden")

# 结果列说明:
# - gene: 基因名
# - logfoldchanges: log2 fold change
# - pvals: 原始 p 值
# - pvals_adj: 多重比较校正后 p 值 (BH 校正)
# - pct_nz_group: 该 cluster 中表达比例
# - pct_nz_reference: 其他 cluster 中表达比例
```

### 火山图解读

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

**火山图解读要点**:

| 区域 | 位置 | 含义 |
|------|------|------|
| 右上 | log2FC > 0, padj < 0.05 | 显著上调基因 |
| 左上 | log2FC < 0, padj < 0.05 | 显著下调基因 |
| 中下 | padj > 0.05 | 无显著差异基因 |
| 顶部水平线 | padj = 0.05 | 显著性阈值线 |

---

## 6. 通路富集分析

### GO 富集分析

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

### KEGG 通路富集

```python
kegg = enricher.run_kegg(gene_list=top_genes)
print(f"KEGG enriched pathways: {len(kegg)}")
print(kegg[["Term", "Adjusted P-value", "Overlap"]].head(10))
```

### GSEA 分析（需要排序基因列表）

```python
# 基于 log2FC 排序的基因列表
ranked_genes = results.set_index("gene")["logfoldchanges"].sort_values(ascending=False)

gsea = enricher.run_gsea(ranked_genes, gene_sets="KEGG_2021_Human")
print(f"GSEA enriched gene sets: {len(gsea)}")
```

### 富集结果气泡图

```python
viz = BioVisualizer()
viz.plot_enrichment_dotplot(go_bp, save_path="go_dotplot.png")
```

---

## 7. 质量门闸说明

### Gate Bio-1.5 — 数据质量门闸

> 位于 Phase 1（数据加载后），阻断不合格数据进入分析流程。
> 实现: `msra_modules/bioinformatics/quality_gates.py` → `BioQualityGateChecker`

| # | 检查项 | 关键项 | 通过标准 |
|---|--------|--------|---------|
| 1 | Count 矩阵完整性 | 🔑 | 无 NaN、无负值、全部整数 |
| 2 | 样本信息一致性 | 🔑 | sample_info 的样本 ID 全部存在于 AnnData |
| 3 | 文库大小合理性 | | 中位数 ± 3IQR 范围内占比 > 90% |
| 4 | 基因注释覆盖率 | | gene_name 列非空率 > 80% |
| 5 | 批次效应检测 | | PCA 上 batch 方差占比 < 10% |

**判定规则**:
- **PASS**: 5/5 通过
- **CONDITIONAL**: 3-4/5 通过且 🔑 全通过
- **BLOCKED**: ≤ 2/5 通过 或 🔑 任一未通过（**阻断流程**）

### Gate Bio-3.5 — 分析结果门闸

> 位于 Phase 3（结果审查前），验证分析结果质量。

| # | 检查项 | 关键项 | 通过标准 |
|---|--------|--------|---------|
| 1 | P 值分布合理性 | 🔑 | P ∈ [0,1]，无异常集中 |
| 2 | log2FC 与 P 值一致性 | 🔑 | Spearman ρ > 0.1 |
| 3 | 多重比较校正 | 🔑 | padj 已计算且合理 |
| 4 | 通路富集 FDR | | 至少 1 条 padj < 0.05 |
| 5 | 可视化一致性 | | 可视化文件存在且显著基因数一致 |

### Python 调用示例

```python
from msra_modules.bioinformatics import BioQualityGateChecker

checker = BioQualityGateChecker(study_id="BIO-2026-001")

# Gate Bio-1.5
result_15 = checker.run_gate_bio15(
    adata=adata,
    sample_info=sample_info_df,  # 可选
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

## 8. 与主 Pipeline 集成

### 导出差异基因列表供主 Pipeline 使用

差异基因分析完成后，可将结果导出为 CSV，供 `/msra-exec`（Stage 3）作为协变量使用：

```python
# 导出标准格式 CSV
de_results[["gene", "logfoldchanges", "pvals_adj"]].to_csv(
    "MSRA/data/bio_covariates.csv",
    index=False,
    header=["gene", "log2FC", "padj"],
)
```

### 自动接入主 Pipeline

在 Phase 4 中选择"接入主 Pipeline"选项，系统将：
1. 将差异基因列表写入 `MSRA/data/bio_covariates.csv`
2. 自动触发 `/msra-exec` 将其作为协变量纳入 Stage 3 统计模型

### 命令行直接调用

```
/msra-bio --data filtered_feature_bc_matrix/ --mode de --integrate-pipeline
```

---

## 9. 常见问题 FAQ

### Q1: 安装 scanpy 失败怎么办？

scanpy 依赖较多，建议使用 conda 安装：

```bash
conda install -c conda-forge scanpy
```

### Q2: Gate Bio-1.5 的批次效应检测没有 batch 信息怎么办？

当 `sample_info` 中不包含 `batch` 列时，该项检查会自动跳过，标记为 N/A，不计入门闸判定结果。

### Q3: gseapy 的 Enrichr API 超时怎么办？

系统会自动重试 3 次。如果仍然超时，会降级为本地分析模式。您也可以检查网络连接或使用自定义 `.gmt` 基因集文件：

```python
enricher = PathwayEnrichment(organism="human", gene_sets="custom_genesets.gmt")
```

### Q4: QC 过滤后细胞数太少（< 100）怎么办？

这通常表明数据质量问题或 QC 参数设置过严。建议：
1. 检查 `max_pct_mito` 阈值是否过低（默认 20%）
2. 检查 `min_genes` 是否过高（默认 200）
3. 确认数据格式正确（基因 × 细胞 或 细胞 × 基因）

### Q5: 差异表达结果中 padj 全部为 1 怎么办？

这通常是因为样本量过少或组间差异不明显。建议：
1. 增加样本量
2. 尝试不同的 DE 方法（`method="deseq2"`）
3. 降低 `log2FC` 阈值

### Q6: 批次校正后 UMAP 上的批次仍分离怎么办？

- 尝试切换校正方法（ComBat → Harmony）
- 调整 Harmony 的 `theta` 参数
- 检查批次信息是否正确标注

---

> **相关文档**: [SKILL.md](../../skills/bioinformatics/SKILL.md) | [模块 PRD](../prd/bioinformatics-module-prd.md)
> **MSRA 文档主页**: [系统设计文档](../system_design.md)
