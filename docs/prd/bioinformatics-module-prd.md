# PRD: MSRA Bioinformatics（生物信息学）模块

> **版本**: v1.0 | **日期**: 2026-06-24 | **状态**: ✅ 已实现 (Alpha → Beta)
> **负责**: MSRA Team | **目标成熟度**: Alpha → Beta | **实际达成**: Beta

---

## 1. 项目信息

- **Language**: 中文
- **Programming Language**: Python 3.11+（引擎层）+ Markdown（Skill 定义层）
- **Project Name**: `msra_bioinformatics`
- **原始需求**:
  为 MSRA 的实验性模块架构（方案C：Skill入口 + Agent执行）开发 **bioinformatics（生物信息学）** 模块，使其从 Alpha 提升到 Beta 成熟度。包括 Skill 入口文件、Python 引擎补全（通路富集、批次效应）、质量门闸实现、测试用例、命令注册。

---

## 2. 产品定义

### 2.1 产品目标

| # | 目标 | 衡量标准 |
|---|------|---------|
| G1 | **提供端到端单细胞/基因表达分析能力** | 用户通过 `/msra-bio` 命令可完成：数据加载 → QC → 降维聚类 → 差异表达 → 通路富集 → 可视化报告，无需离开 MSRA 环境 |
| G2 | **保证生信分析结果质量可审计** | Gate Bio-1.5 和 Gate Bio-3.5 质量门闸实现并自动执行，关键检查项不通过时阻断流程 |
| G3 | **可与主 Pipeline 无缝集成** | `/msra-bio` 输出的差异基因列表可直接接入 Stage 3（analysis-exec）作为协变量/分层因子 |

### 2.2 用户故事

| # | 用户故事 | 优先级 |
|---|---------|--------|
| US1 | 作为**生物信息学研究员**，我想通过 `/msra-bio` 加载 10x Genomics 格式的单细胞数据，以便在 MSRA 中启动标准化分析流程 | P0 |
| US2 | 作为**临床研究者**，我想查看 QC 报告（细胞/基因过滤前后统计），以便确认数据质量满足后续分析要求 | P0 |
| US3 | 作为**生物信息学研究员**，我想自动执行差异表达分析（DESeq2/Wilcoxon）并获取火山图、热图，以便快速识别关键差异基因 | P0 |
| US4 | 作为**生物信息学研究员**，我想对差异基因进行 GO/KEGG 通路富集分析，以便理解差异基因的生物学意义 | P1 |
| US5 | 作为**临床研究者**，我想将 `/msra-bio` 的分析结果（差异基因列表）传递给 `/msra-exec`，以便将其作为协变量纳入主统计模型 | P1 |
| US6 | 作为**数据管理员**，我想在分析前自动检测批次效应，以便决定是否需要进行批次校正 | P1 |

---

## 3. 技术规范

### 3.1 需求池

#### P0 — 必须完成（Beta 准入）

| ID | 需求 | 描述 | 交付物 |
|----|------|------|--------|
| P0-1 | **SKILL.md 创建** | `skills/bioinformatics/SKILL.md`，定义 Phase 0-4 完整流程、角色、Iron Rules、质量门闸引用 | SKILL.md 文件 |
| P0-2 | **命令注册** | `manifest.json` 中新增 `/msra-bio` 命令，指向 `skills/bioinformatics/SKILL.md` | manifest.json 更新 |
| P0-3 | **Gate Bio-1.5 实现** | 生信数据质量门闸：Count 矩阵完整性、样本信息一致性、文库大小合理性、基因注释覆盖率、批次效应检测 | `msra_modules/bioinformatics/quality_gates.py` |
| P0-4 | **Gate Bio-3.5 实现** | 生信分析结果门闸：P 值分布合理性、log2FC 与 P 值一致性、多重比较校正检查、通路富集 FDR、可视化一致性 | 同上文件 |
| P0-5 | **通路富集分析** | 新增 `PathwayEnrichment` 类，支持 GO（BP/MF/CC）、KEGG、GSEA，基于 gseapy | `msra_modules/bioinformatics/enrichment.py` |
| P0-6 | **__init__.py 更新** | 导出新增的 `PathwayEnrichment` 和 `QualityGateChecker` | `__init__.py` 更新 |
| P0-7 | **单元测试** | 每个模块类至少 3 个测试用例，覆盖率 ≥ 50% | `tests/test_bioinformatics/` |
| P0-8 | **SKILL.md Phase 定义** | Phase 0（交互配置）→ Phase 1（QC+标准化）→ Phase 2（后台分析）→ Phase 3（结果审查+门闸）→ Phase 4（整合/报告） | SKILL.md 内容 |

#### P1 — 应该完成

| ID | 需求 | 描述 | 交付物 |
|----|------|------|--------|
| P1-1 | **批次效应检测与校正** | 新增 `BatchCorrector` 类，支持 ComBat（scanpy）和 Harmony（scanpy.external） | `msra_modules/bioinformatics/batch_correction.py` |
| P1-2 | **结果 Schema 导出** | 按设计文档定义的 `msra/bio_analysis_result/v1` Schema 输出结果 | 导出逻辑 |
| P1-3 | **与主 Pipeline 集成接口** | 差异基因列表 → CSV 格式输出，可被 Stage 3 读取作为协变量 | 集成文档 + 示例 |
| P1-4 | **依赖管理** | `pyproject.toml` 中 `[project.optional-dependencies]` 新增 `bioinformatics` extras | pyproject.toml 更新 |
| P1-5 | **文档更新** | 更新 `18-实验性模块设计.md` 中 bioinformatics 模块状态为 Beta | 文档更新 |

#### P2 — 可以完成

| ID | 需求 | 描述 |
|----|------|------|
| P2-1 | **生存分析集成** | 基于 lifelines 的 Kaplan-Meier/Cox 回归，用于基因表达与预后关联 |
| P2-2 | **交互式 UMAP/TSNE** | 基于 plotly 的交互式降维可视化 |
| P2-3 | **GSEA 基因集自定义** | 支持用户上传自定义 .gmt 基因集文件 |

### 3.2 UI 交互设计（SKILL.md Phase 定义）

#### Phase 0: 用户交互配置（MANDATORY）

```
┌─────────────────────────────────────────────────────────────┐
│  /msra-bio 启动                                              │
│                                                              │
│  1. 数据源选择:                                              │
│     ├─ [1] 10x MTX 目录 (filtered_feature_bc_matrix/)       │
│     ├─ [2] 10x H5 文件 (.h5)                                │
│     ├─ [3] CSV/TSV 计数矩阵                                 │
│     └─ [4] FASTA/FASTQ (未来支持)                            │
│                                                              │
│  2. 样本信息:                                                │
│     ├─ 提供 sample_info.csv (包含 batch, condition 等列)     │
│     └─ 或手动输入分组信息                                     │
│                                                              │
│  3. 分析目标确认:                                            │
│     ├─ [A] 差异表达分析 (默认)                               │
│     ├─ [B] 单细胞聚类 + 轨迹分析                             │
│     ├─ [C] 通路富集分析                                      │
│     └─ [D] 完整流程 (A+B+C)                                  │
│                                                              │
│  4. 参数配置 (可选覆盖默认值):                                │
│     ├─ QC 阈值: min_genes, min_cells, max_pct_mito          │
│     ├─ 降维参数: n_pcs, n_neighbors, resolution              │
│     └─ 差异分析: method, log2fc_threshold, padj_threshold    │
└─────────────────────────────────────────────────────────────┘
```

#### Phase 1: 数据预处理（ADAPTIVE）

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: 数据加载与质控                                     │
│                                                              │
│  Step 1.1: 数据加载                                          │
│    → ScRNASeqLoader.load() → AnnData 对象                    │
│    → 输出: 细胞数 × 基因数 统计摘要                          │
│                                                              │
│  Step 1.2: ▶ Gate Bio-1.5 数据质量门闸                      │
│    → [🔑] Count 矩阵完整性                                   │
│    → [🔑] 样本信息一致性                                     │
│    → [ ] 文库大小合理性                                      │
│    → [ ] 基因注释覆盖率                                      │
│    → [ ] 批次效应检测                                        │
│    → ❌ 关键项不通过 → 阻断并提示修复方案                     │
│                                                              │
│  Step 1.3: QC 过滤                                           │
│    → SingleCellQC 过滤低质量细胞/基因                         │
│    → 输出: 过滤前后对比统计表                                 │
│                                                              │
│  Step 1.4: 标准化                                            │
│    → DimensionalityReduction.normalize_and_log()              │
│    → HVG 筛选                                                │
└─────────────────────────────────────────────────────────────┘
```

#### Phase 2: 重计算（BACKGROUND — 子 Agent 执行）

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: 后台分析 (子 Agent 并行执行)                       │
│                                                              │
│  ┌─ Task A: 降维聚类 ─────────────────────────────────┐     │
│  │  PCA → UMAP → Leiden 聚类                          │     │
│  │  输出: AnnData (含 X_pca, X_umap, leiden)          │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─ Task B: 差异表达 (如用户选择) ────────────────────┐     │
│  │  DifferentialExpression.find_markers()              │     │
│  │  → 每个 cluster vs rest 的差异基因                  │     │
│  │  输出: DE gene table (gene, log2FC, pval, padj)    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─ Task C: 通路富集 (如用户选择) ────────────────────┐     │
│  │  PathwayEnrichment.run_go() / run_kegg() / run_gsea│     │
│  │  输出: enrichment table (pathway, NES, padj, FDR)  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─ Task D: 批次校正 (如检测到批次效应) ──────────────┐     │
│  │  BatchCorrector.combat() / harmony()               │     │
│  │  输出: 校正后 AnnData                               │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

#### Phase 3: 结果审查（MANDATORY）

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: 结果审查 + Gate Bio-3.5                           │
│                                                              │
│  Step 3.1: ▶ Gate Bio-3.5 分析结果门闸                      │
│    → [🔑] P 值分布合理性 (均匀分布 + 0 附近峰值)            │
│    → [🔑] log2FC 与 P 值一致性                              │
│    → [🔑] 多重比较校正已应用                                 │
│    → [ ] 通路富集 FDR < 0.05                                │
│    → [ ] 可视化与数据一致                                    │
│                                                              │
│  Step 3.2: 可视化审查                                        │
│    → 火山图 (Volcano Plot)                                   │
│    → 热图 (Top DE Genes Heatmap)                            │
│    → UMAP 聚类图                                             │
│    → 通路富集气泡图 (Dot Plot)                               │
│                                                              │
│  Step 3.3: 用户确认                                          │
│    → 展示结果摘要 + 关键发现                                  │
│    → 用户确认 / 请求调整参数重跑                              │
└─────────────────────────────────────────────────────────────┘
```

#### Phase 4: 整合与报告（ADAPTIVE）

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: 结果整合                                           │
│                                                              │
│  选项 A: 独立报告                                            │
│    → 生成 bio_analysis_report.md (含 QC + DE + 通路 + 图)   │
│    → 导出 DE gene list CSV                                   │
│                                                              │
│  选项 B: 接入主 Pipeline                                     │
│    → 差异基因列表 → MSRA/data/bio_covariates.csv            │
│    → 自动触发 /msra-exec 将其作为协变量纳入 Stage 3          │
│                                                              │
│  输出 Schema: msra/bio_analysis_result/v1                    │
│    ├─ differential_genes.csv                                 │
│    ├─ enrichment_results.csv                                 │
│    ├─ qc_report.html                                         │
│    └─ visualization_bundle/ (png/svg)                        │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 质量门闸设计

#### Gate Bio-1.5（生信数据质量）— 位于 Phase 1 之后

```python
class GateBio15:
    """生信数据质量门闸 — Phase 1 完成后执行"""

    def check_count_matrix_integrity(self, adata) -> GateResult:
        """[🔑] Count 矩阵完整性：无缺失值、全部为非负整数"""
        # 检查: adata.X 无 NaN、全部 >= 0、全部为整数

    def check_sample_consistency(self, adata, sample_info) -> GateResult:
        """[🔑] 样本信息与矩阵列名一致"""
        # 检查: sample_info.index ⊆ adata.obs_names

    def check_library_size(self, adata) -> GateResult:
        """[ ] 文库大小合理性：无极端离群值"""
        # 检查: 文库大小中位数 ± 3*IQR 范围内的细胞占比 > 90%

    def check_gene_annotation(self, adata) -> GateResult:
        """[ ] 基因注释覆盖率"""
        # 检查: 有 gene_name 注释的基因占比 > 80%

    def check_batch_effect(self, adata, batch_key="batch") -> GateResult:
        """[ ] 批次效应检测"""
        # 检查: PCA 上 batch 解释的方差占比 < 10%
```

#### Gate Bio-3.5（生信分析结果）— 位于 Phase 3 之前

```python
class GateBio35:
    """生信分析结果门闸 — Phase 2 完成后执行"""

    def check_pvalue_distribution(self, pvalues) -> GateResult:
        """[🔑] P 值分布合理性"""
        # 检查: 均匀分布基线 + 0 附近峰值（非全 0 或全 1）

    def check_effect_consistency(self, log2fc, pvalues) -> GateResult:
        """[🔑] 效应量与 P 值一致性"""
        # 检查: |log2FC| 大的基因 P 值倾向于更小

    def check_multiple_testing(self, pvalues, padj) -> GateResult:
        """[🔑] 多重比较校正已应用"""
        # 检查: padj 已计算且 max(padj) >= max(pvalue)

    def check_enrichment_fdr(self, enrichment_df) -> GateResult:
        """[ ] 通路富集 FDR < 0.05"""
        # 检查: 至少有 1 条通路 padj < 0.05

    def check_visualization_consistency(self, fig_data, de_table) -> GateResult:
        """[ ] 可视化与数据一致"""
        # 检查: 火山图中标记的显著基因与 DE table 一致
```

### 3.4 Python 引擎新增/补全清单

| 文件 | 状态 | 新增类/函数 | 说明 |
|------|------|------------|------|
| `enrichment.py` | 🆕 新建 | `PathwayEnrichment` | GO/KEGG/GSEA 分析，基于 gseapy |
| `batch_correction.py` | 🆕 新建 | `BatchCorrector` | ComBat + Harmony 批次校正 |
| `quality_gates.py` | 🆕 新建 | `GateBio15`, `GateBio35` | 质量门闸实现 |
| `__init__.py` | 📝 更新 | 新增导出 | 导出 PathwayEnrichment, BatchCorrector, GateBio15, GateBio35 |
| `tests/test_bioinformatics/` | 🆕 新建 | 测试文件 | 每个类 ≥ 3 个测试用例 |

### 3.5 manifest.json 新增条目

```json
"/msra-bio": {
  "id": "msra-bio",
  "name": "Bioinformatics Analysis",
  "entry_point": "skills/bioinformatics/SKILL.md",
  "description": "Single-cell / gene expression analysis pipeline: data loading, QC, dimensionality reduction, differential expression, pathway enrichment. Supports 10x Genomics, CSV, H5 formats.",
  "usage": "/msra-bio [--data count_matrix] [--samples sample_info] [--mode de|cluster|enrichment|full]",
  "examples": [
    "/msra-bio --data filtered_feature_bc_matrix/ --samples sample_info.csv",
    "/msra-bio --mode de --method deseq2",
    "/msra-bio --mode enrichment --genes de_genes.csv"
  ]
}
```

---

## 4. 待确认问题（Open Questions）

| # | 问题 | 影响范围 | 建议默认 |
|---|------|---------|---------|
| Q1 | FASTA/FASTQ 原始数据是否在 Alpha→Beta 阶段支持？还是仅支持 Count Matrix 输入？ | data_loader.py 扩展范围 | **建议 Beta 阶段仅支持 Count Matrix**（10x MTX/H5/CSV），FASTA/FASTQ 留到 Stable |
| Q2 | 子 Agent 调度是复用现有 `HybridModeBridge` 还是新建 bio 专用调度器？ | Phase 2 架构 | **建议复用 HybridModeBridge**，新增 `BIO_ANALYSIS` 子类型 |
| Q3 | 通路富集的物种默认是什么？是否需要物种自动检测？ | enrichment.py 参数 | **默认人类 (hsa)**，通过基因名前缀或用户指定切换 |
| Q4 | 质量门闸失败时的行为：阻断（hard fail）还是警告（soft fail）可跳过？ | Skill 流程控制 | **🔑 关键项 hard fail**，非关键项 soft fail + 用户确认 |
| Q5 | Gate Bio-1.5 的批次效应检测在没有 batch 信息时如何处理？ | 门闸逻辑 | **无 batch 信息时跳过该项检查**，不计入门闸结果 |
| Q6 | 与主 Pipeline 集成时，差异基因列表作为协变量的格式规范？ | Stage 3 接口 | **建议输出 CSV: gene, log2FC, padj, cluster**，由 analysis-exec 决定如何使用 |
| Q7 | 测试数据来源：使用真实公开数据集还是合成测试数据？ | 测试策略 | **建议使用 PBMC 3k 公开数据集子集**（小、标准、可复现） |

---

## 5. 依赖清单

```toml
# 核心依赖（Beta 必需）
scanpy >= 1.9
anndata >= 0.9
pydeseq2 >= 0.4
gseapy >= 1.0

# 可选依赖（P2 功能需要）
lifelines >= 0.27     # 生存分析
plotly >= 5.18        # 交互式可视化

# 开发/测试依赖
pytest >= 7.0
pytest-cov >= 4.0
```

---

## 6. 成功标准（Alpha → Beta 准入）

| 准入条件 | 验证方式 |
|---------|---------|
| ✅ SKILL.md 完成（Phase 0-4） | 文件存在且结构完整 |
| ✅ Python 引擎核心功能实现 | enrichment.py + batch_correction.py + quality_gates.py 可导入可执行 |
| ✅ 单元测试覆盖率 ≥ 50% | `pytest --cov=msra_modules.bioinformatics --cov-report=term-missing` |
| ✅ 质量门闸定义完成 | Gate Bio-1.5 + Gate Bio-3.5 实现并有测试 |
| ✅ manifest.json 命令注册 | `/msra-bio` 命令可被 Claude Code 识别 |
| ✅ 至少 1 个端到端案例验证 | PBMC 3k 数据集完整流程跑通 |
