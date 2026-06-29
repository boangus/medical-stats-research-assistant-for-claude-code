# Gate: BIO QUALITY (Bioinformatics Module)

## 元数据
- gate_id: "bio_quality"
- module: "bioinformatics"
- blocking: true
- skill_source: "bioinformatics"
- checkpoint_id: "GATE-BIO / BIO-1.5+BIO-3.5"
- extension_adapter: "ExtensionGateAdapter('bio').run_module_gate('bio_qc_gate', inputs)"

## 输入

| 参数 | 类型 | 来源 | 必填 |
|------|------|------|------|
| count_matrix | file (mtx/h5/csv/tsv) | ScRNASeqLoader 输出 | ✅ |
| sample_info | file (csv) | 用户提供 | 否 |
| de_results | file (csv) | Phase 2 差异表达 | 否（DE 模式必填） |
| enrichment_results | file (csv) | Phase 2 通路富集 | 否（enrichment 模式必填） |
| qc_report | file (md) | Phase 1 QC 报告 | ✅ |
| batch_correction_log | file (md) | Phase 2 批次校正 | 否 |
| multi_omics_data | file (csv/h5) | 多组学集成输入 | 否（多组学场景必填） |

## 检查清单 (4 项)

| # | 检查项 | 通过标准 | 关键项 |
|---|--------|---------|--------|
| 1 | 数据完整性 | Count 矩阵无 NaN/负值/非整数；样本信息索引与 AnnData.obs_names 一致；基因注释覆盖率 > 80% | ✅ 硬阻断 |
| 2 | DE 结果验证 | padj 已计算（BH 校正）且 padj ≤ pval；P 值分布合理（KS 检验无异常集中）；log2FC 与 P 值 Spearman ρ > 0.1 | ✅ 硬阻断 |
| 3 | 通路富集覆盖 | 物种与基因集库版本已注明；FDR 校正已应用；至少 1 条 padj < 0.05 或明确记录"无显著通路"结论 | 否 |
| 4 | 多组学一致性 | 多模态数据样本交集 ≥ 阈值（关联 3/预测 10/可视化 1）；模态间数据类型匹配；批次效应方差占比 < 10% | 否 |

### 检查项 1（数据完整性）详细标准
- Count 矩阵无 NaN、无负值、全部为整数
- sample_info.index ⊆ adata.obs_names（所有样本在 AnnData 中）
- 基因注释列非空率 > 80%
- 文库大小中位数 ± 3IQR 范围内占比 > 90%
- 通过标准：以上全部满足

### 检查项 2（DE 结果验证）详细标准
- 所有 DE 结果均计算 padj（BH 校正），禁止仅使用原始 p 值
- padj ≤ pval（校正后 p 值不应大于原始 p 值）
- P 值 KS 检验：P ∈ [0,1]，无异常集中
- log2FC 与 -log10(p) Spearman 相关 ρ > 0.1（即效应量与显著性方向一致）
- 通过标准：以上全部满足

### 检查项 3（通路富集覆盖）详细标准
- 物种参数已明确（human/mouse/...）
- 基因集库版本已注明（GO BP/KEGG/Reactome 等）
- FDR 校正已应用（BH/Bonferroni）
- 通过标准：至少 1 条 padj < 0.05，或明确记录"无显著通路"结论并附原因

### 检查项 4（多组学一致性）详细标准
- 多模态数据样本交集数 ≥ 场景阈值
- 模态间数据类型匹配（维度/dtype 符合预期）
- 批次效应检测：PCA 上 batch 方差占比 < 10%
- 通过标准：以上全部满足（仅在多组学场景执行）

## 判定规则

- **PASS**: 全部通过 (4/4) → ✅ 进入下一阶段
- **CONDITIONAL**: 3/4 通过且关键项全通过 → ⚠️ 记录风险后继续
- **BLOCK**: < 3/4 通过 **或** 关键项 1/2 任一未通过 → ❌ **强制退回 Phase 1/2 修订**

> **关键项定义**：项 1（数据完整性）、项 2（DE 结果验证）为硬阻断项，不可条件通过。

## 输出 (gate_result schema)

```json
gate_result: {
  "gate": "bio_quality",
  "module": "bioinformatics",
  "passed": bool,
  "total": 4,
  "passed_count": int,
  "failed_items": ["BG-0X", ...],
  "conditional": bool,
  "blocking_items": ["BG-01" | "BG-02"],
  "timestamp": "ISO8601"
}
```

## 与模块的联动

- **BLOCK** → 退回 Phase 1 修订数据加载/QC，或退回 Phase 2 修订 DE/富集分析
- **回退 ≥ 2 次** → 触发收敛检测（见 pipeline/SKILL.md §7.3）
- **CONDITIONAL** → 记录风险后继续 Phase 3 用户确认
- **Checkpoint**: [GATE-BIO] 门闸通过后方可进入 Phase 3 结果审查
- **Skill 模式**：`bioinformatics` 复用，Mode=`quality-gate`（只检查，不修改）
- **Agent 模式**：通过 `ExtensionGateAdapter("bio")` 调用
- 参考实现：`src/shared/quality_gates/gate_runner.py` + `check_items.py`
