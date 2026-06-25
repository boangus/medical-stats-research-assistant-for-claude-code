# Gate: CROSS QUALITY (Cross-Domain Module)

## 元数据
- gate_id: "cross_quality"
- module: "cross"
- blocking: true
- skill_source: "cross-domain"
- checkpoint_id: "GATE-CROSS / CD-1.5+CD-3.5"
- extension_adapter: "ExtensionGateAdapter('cross').run_module_gate('cross_fusion_gate', inputs)"

## 输入

| 参数 | 类型 | 来源 | 必填 |
|------|------|------|------|
| data_sources | dict (multi-modal) | Phase 1 多模态数据加载 | ✅ |
| alignment_strategy | string | Phase 0 配置 | ✅ |
| correlation_results | file (csv/json) | Phase 2 RadiomicsDEGCorrelation | 否（correlation 场景必填） |
| model_metrics | file (json) | Phase 2 RealtimePredictionModel | 否（prediction 场景必填） |
| visualization_data | file (png/svg) | Phase 2 MultiModalVisualizer | 否（visualization 场景必填） |
| export_bundle | file (csv/json/md) | Phase 4 export_v1_schema | 否 |

## 检查清单 (4 项)

| # | 检查项 | 通过标准 | 关键项 |
|---|--------|---------|--------|
| 1 | 多模态对齐 | 交集样本数 ≥ 阈值（关联 3/预测 10/可视化 1）；场景所需模态全部提供；维度/dtype 符合预期 | ✅ 硬阻断 |
| 2 | 融合模型验证 | accuracy ≥ 0.5；AUROC ≥ 0.55；模型指标无 NaN；训练/评估流程可复现 | ✅ 硬阻断 |
| 3 | 跨域一致性 | 数据对齐后模态间样本索引一致；缺失值处理策略已记录；标准化（z-score/min-max）已应用 | 否 |
| 4 | 关联显著性 | FDR 校正已应用（BH/Bonferroni）；至少 1 条 p_adj < 0.05 且 \|r\| ≥ 0.3，或 AUROC > 0.5；物种/基因集版本已注明 | 否 |

### 检查项 1（多模态对齐）详细标准
- 交集样本数 ≥ 场景阈值（correlation: 3, prediction: 10, visualization: 1）
- 场景所需模态全部提供（如 correlation 需要 radiomics + expression）
- 数据类型匹配（维度/dtype 符合预期）
- 通过标准：以上全部满足

### 检查项 2（融合模型验证）详细标准
- 模型 accuracy ≥ 0.5（优于随机基线）
- 模型 AUROC ≥ 0.55
- 模型指标无 NaN（accuracy/precision/recall/f1/auroc 均有效）
- 训练/评估流程可复现（随机种子已记录）
- 通过标准：以上全部满足

### 检查项 3（跨域一致性）详细标准
- 数据对齐后模态间样本索引一致
- 缺失值处理策略已记录（删除/插补/保留）
- 标准化已应用（z-score / min-max）
- 通过标准：以上全部满足

### 检查项 4（关联显著性）详细标准
- FDR 校正已应用（BH/Bonferroni），禁止仅使用原始 p 值
- 至少 1 条 p_adj < 0.05 且 |r| ≥ 0.3（关联场景），或 AUROC > 0.5（预测场景）
- 物种与基因集库版本已注明（关联场景）
- 通过标准：以上全部满足

## 判定规则

- **PASS**: 全部通过 (4/4) → ✅ 进入下一阶段
- **CONDITIONAL**: 2-3/4 通过且关键项全通过 → ⚠️ 记录风险后继续
- **BLOCK**: < 2/4 通过 **或** 关键项 1/2 任一未通过 → ❌ **强制退回 Phase 1/2 修订**

> **关键项定义**：项 1（多模态对齐）、项 2（融合模型验证）为硬阻断项，不可条件通过。

## 输出 (gate_result schema)

```json
gate_result: {
  "gate": "cross_quality",
  "module": "cross",
  "passed": bool,
  "total": 4,
  "passed_count": int,
  "failed_items": ["CG-0X", ...],
  "conditional": bool,
  "blocking_items": ["CG-01" | "CG-02"],
  "timestamp": "ISO8601"
}
```

## 与模块的联动

- **BLOCK** → 退回 Phase 1 修订数据对齐，或退回 Phase 2 修订关联分析/模型训练
- **回退 ≥ 2 次** → 触发收敛检测（见 pipeline/SKILL.md §7.3）
- **CONDITIONAL** → 记录风险后继续 Phase 3 结果审查
- **Checkpoint**: [GATE-CROSS] 门闸通过后方可进入 Phase 3 用户确认及 Phase 4 export_v1_schema
- **Skill 模式**：`cross-domain` 复用，Mode=`quality-gate`（只检查，不修改）
- **Agent 模式**：通过 `ExtensionGateAdapter("cross")` 调用
- 参考实现：`shared/quality_gates/gate_runner.py` + `check_items.py`
- 输出 Schema：`msra/cross_domain_result/v1`（见 `shared/contracts/cross_domain_result_schema.md`）
