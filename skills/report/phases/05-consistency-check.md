# Phase 5: 一致性校验（精简版）

> 来源：从 SKILL.md L737-880 抽取。
> Stage 4 精简：仅保留 report 特有的交叉验证（表格数字 vs 分析结果、图表 vs 表格一致性）。
> 统计约束合规检查（P-R/M-R/D-R/S-R/V-R）由 analysis-exec Phase 4（质量检查）覆盖，本阶段不重复执行。
> 报告规范全文合规（CONSORT/STROBE 等）移至 Paper Track Stage 5.0（仅写论文时需要，见 pipeline/SKILL.md §Stage 5）。

**Step 5a: 统计一致性校验 (statcheck)** 🆕

> 参考：shared/reporting-guidelines/statcheck_rules.md — NHST 结果一致性自动校验规则

从 Phase 1（结果解读）、Phase 2（表格）、Phase 4（方法学）抽取所有 NHST 结果（t/F/χ²/r/z + df + 报告 p），独立重算 p 值并比对：

1. **抽取**: 按正则模式匹配 APA 格式统计结果（如 `t(38)=2.45, p=.019`、`F(2,57)=4.32, p=.018`、`χ²(1)=5.83, p=.016`）
2. **重算**: 用 scipy 从统计量+df 独立重算 p（双尾默认；标注 one-tailed/adjusted 的特殊处理）
3. **判定**: 绝对误差 <0.001 → ✅；0.001–0.01 → ⚠️ 边界；≥0.01 → ❌；跨 0.05 阈值 → ❌❌ 严重
4. **降级**: scipy 不可用时降级为格式抽取+明显矛盾检测（如 `p<.001` 但 stat 极小）

> 详细正则模式、重算公式、误报缓解见 `shared/reporting-guidelines/statcheck_rules.md`。

**Step 5b: 统计反模式检查**（保留）

> 参考：shared/anti-patterns/medical_stats_anti_patterns.md（D1/D2/D3/M1-M6）

**Step 5c: quality_checklist 统计维度**（保留统计相关维度）

> 参考：shared/reporting-guidelines/quality_checklist.md
> 仅检查：统计方法维度 + 结果报告维度（其余维度移至 Paper Track）

**Step 5d: 统计约束合规检查** 🆕

> 参考：shared/statistics-methods/statistical_constraints.md — 统计约束规则全文
> 注：此检查由 analysis-exec Phase 4（质量检查）覆盖，本阶段仅做 report 层面的交叉验证。

检查项：

| 检查内容 | 规则 | 检查方式 | 不通过处理 |
|---------|------|---------|-----------|
| P值格式 | P-R01~R07 | 扫描所有 P 值字符串，无 "P = 0.000"、无二元化表述 | 强制修正 |
| 方法一致性 | M-R01~R08 | 核对方法一致性追踪表，加权/非加权无混用 | 强制重跑 |
| 数据集一致性 | D-R01~R05 | 核对数据集一致性追踪表，差异已确认 | 阻断至用户确认 |
| 统计原则违反 | S-R01~R08 | 核对统计原则违反日志，所有违反已处理 | 阻断至用户确认 |
| 变量命名一致性 | V-R01~V07 | SAP/表格/图表/正文变量名比对 | 强制修正 |

**Step 5e: 图表发表级质量检查** 🆕

> 参考：shared/chart-styles/publication_figure_standards.md — 发表级图表标准
> 注：此检查由 analysis-exec Phase 4（质量检查）覆盖，本阶段仅做 report 层面的交叉验证。

检查项：

| 检查内容 | 标准 | 不通过处理 |
|---------|------|-----------|
| 强制 rcParams | font.family=sans-serif, svg.fonttype='none' | 重新生成 |
| 导出格式 | SVG（首要）+ PNG 300dpi（预览） | 补充导出 |
| 轴线 | 仅左+下轴线，右/上轴线关闭 | 修正 |
| 图例 | 无边框（frameon=False） | 修正 |
| 变量名 | 规范显示名+单位 | 修正 |
| P值标注 | 符合 P-R01~R07 | 修正 |
| 多面板 | 无冗余面板（反冗余检查） | 重新设计 |
| 配色 | 语义化调色板或期刊配色 | 修正 |
| 分辨率 | PNG 300dpi，SVG矢量格式 | 重新导出 |
| **PDF格式** | **PDF格式用于学术投稿** | **补充导出** |

**Step 5f: 学术发表标准检查** 🆕

> 确保所有输出物达到学术发表标准，可直接用于论文投稿。

**表格学术标准**：

| 检查内容 | 标准 | 不通过处理 |
|---------|------|-----------|
| 三线表格式 | 顶线粗(2pt)+表头下线中(1pt)+底线粗(2pt)，无竖线 | 重新生成 |
| Word格式 | .docx格式，符合医学期刊要求 | 重新导出 |
| 表题位置 | 表题在上方居中 | 修正 |
| 表注位置 | 表注在下方，含统计方法说明 | 补充 |
| 列对齐 | 第一列左对齐，其余居中 | 修正 |
| 字体 | 宋体(中文)+Times New Roman(英文)，10pt | 修正 |

**图表学术标准**：

| 检查内容 | 标准 | 不通过处理 |
|---------|------|-----------|
| PDF格式 | PDF格式用于学术投稿 | 补充导出 |
| SVG格式 | SVG矢量格式，可无损缩放 | 重新导出 |
| PNG分辨率 | 300dpi，清晰度满足印刷要求 | 重新导出 |
| 字体大小 | 坐标轴标签≥10pt，图例≥8pt | 修正 |
| 配色 | 语义化调色板或期刊配色 | 修正 |
| 标注完整性 | 含样本量、P值、效应量等关键信息 | 补充 |

**交付物清单**：

> 完整图表类型清单见：shared/references/academic_figure_table_types.md

**表格交付物**：

| 序号 | 交付物 | 格式 | 路径 | 说明 |
|-----|--------|------|------|------|
| T1 | Table 1 基线特征表 | .docx三线表 | reports/tables/table1_baseline.docx | 按分组展示基线特征 |
| T2 | 主分析结果表 | .docx三线表 | reports/tables/table2_main_results.docx | 回归分析(OR/HR/β及95%CI) |
| T3 | 敏感性分析表 | .docx三线表 | reports/tables/table3_sensitivity.docx | 敏感性分析结果 |
| T4 | 亚组分析表 | .docx三线表 | reports/tables/table4_subgroup.docx | 亚组分析结果 |
| T5 | 不良事件汇总表 | .docx三线表 | reports/tables/table5_adverse_events.docx | AE/SAE汇总 |
| T6 | 实验室异常表 | .docx三线表 | reports/tables/table6_lab_abnormality.docx | 实验室检查异常 |
| T7 | 样本量计算表 | .docx三线表 | reports/tables/table7_sample_size.docx | 样本量计算依据 |
| T8 | 变量定义表 | .docx三线表 | reports/tables/table8_variable_definition.docx | 变量构造定义 |

**图表交付物**：

| 序号 | 交付物 | 格式 | 路径 | 说明 |
|-----|--------|------|------|------|
| F1 | CONSORT流程图 | .svg+.pdf+.png | reports/figures/figure1_consort_flow.* | RCT受试者流程 |
| F2 | Kaplan-Meier曲线 | .svg+.pdf+.png | reports/figures/figure2_km_curve.* | 生存分析 |
| F3 | 森林图 | .svg+.pdf+.png | reports/figures/figure3_forest_plot.* | 亚组/回归分析 |
| F4 | ROC曲线 | .svg+.pdf+.png | reports/figures/figure4_roc_curve.* | 诊断试验 |
| F5 | 校准曲线 | .svg+.pdf+.png | reports/figures/figure5_calibration.* | 预测模型 |
| F6 | Bland-Altman图 | .svg+.pdf+.png | reports/figures/figure6_bland_altman.* | 一致性检验 |
| F7 | 相关性热图 | .svg+.pdf+.png | reports/figures/figure7_correlation_heatmap.* | 变量相关性 |
| F8 | DAG图 | .svg+.pdf+.png | reports/figures/figure8_dag.* | 因果关系 |
| F9 | Love Plot | .svg+.pdf+.png | reports/figures/figure9_love_plot.* | 协变量平衡 |
| F10 | SHAP图 | .svg+.pdf+.png | reports/figures/figure10_shap.* | 机器学习解释 |

**报告交付物**：

| 序号 | 交付物 | 格式 | 路径 | 说明 |
|-----|--------|------|------|------|
| R1 | 统计报告 | .html+.md | reports/final_report.* | 完整统计分析报告 |
| R2 | 方法学描述 | .md | reports/methods_section.md | 统计方法学段落 |
| R3 | 结果解读 | .md | reports/results_interpretation.md | 结果临床意义解读 |
| R4 | 局限性讨论 | .md | reports/limitations.md | 研究局限性讨论 |

**statcheck 校验异常处理** 🆕：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| ⚠️ 边界不一致（绝对误差 0.001–0.01） | 放宽容许至±0.001 后重检 → 若误差仍存在但非跨阈值，加脚注"四舍五入差异" | 生成差异报告表格（原始值 vs 重算值），在报告中标注"统计量待核对"并附核对指引 |
| ❌ 不一致（绝对误差 ≥0.01） | 逐项定位报告原文，与统计软件原始输出比对 → 修正报告中的 p 值或统计量 | 生成详细差异清单（含行号、原始值、重算值、可能原因），提供三个选项：(1) 自动修正 (2) 标记为待核对 (3) 暂停等待用户确认 |
| ❌❌ 跨显著性阈值反转（如报告 p=0.049 但重算 p=0.067） | 核实 df 是否从正确的分析输出提取 → 若确认报告有误则强制修正 | 立即暂停流程，生成严重不一致报告，要求用户选择：(1) 强制修正并继续 (2) 重新运行分析 (3) 标记为"统计存疑"后继续 |
| `scipy` 不可用降级 | 降级为格式抽取 + 明显矛盾检测（如报告 `p<.001` 但 t 统计量 < 0.5） | 无法降级时跳过 statcheck，在报告"统计验证"章节添加说明："自动验证工具不可用，需作者手动核对所有统计量" |

> **🔴 [MANDATORY-GATE-04]** 统计质量检查结果（含 statcheck 校验）展示后，**必须等待用户确认**。
> - ✅ 全部通过 → 进入 ★ STAGE 4 CHECKPOINT（pipeline 决策节点）
> - ⚠️ 有问题 → 修正后重新检查，直到通过
> - ❌ 严重不一致 → 强制修正后才输出
