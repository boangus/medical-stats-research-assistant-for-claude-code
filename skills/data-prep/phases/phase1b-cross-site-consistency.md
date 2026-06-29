### Phase 1b: 跨中心一致性检查 🆕（仅 multi-dataset 模式）

> 目的：在多中心研究中，检查各中心数据的一致性，确保汇总分析的可行性。
> 使用：`src/shared/templates/multicenter_template.py` 的 `MultiCenterAnalyzer`

**检查内容**（使用 `cross_site_consistency_check()`）：

| 检查项 | 方法 | 不一致阈值 |
|--------|------|-----------|
| 变量名一致性 | 比较各中心列名 | 任何差异即警告 |
| 变量类型一致性 | 同名字段的 dtype 比较 | 任何差异即警告 |
| 样本量汇总 | 各中心行数统计 | 最小/最大中心差异 > 5x |
| 缺失率比较 | 各变量缺失率 | 差异 > 20% |
| 基线特征分布 | Kruskal-Wallis 检验 | p < 0.05 |

**输出**：`cross_site_consistency_report.md`

**Checkpoint**：→ 检查点表 #2（7项深度验证，适用于 Phase 1b 同规则）

**产物记录**：`cross_site_consistency` 记入 passport artifacts
