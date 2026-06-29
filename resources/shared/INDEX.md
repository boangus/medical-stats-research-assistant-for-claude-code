# shared/ 目录导航索引

> MSRA 共享资源目录。所有跨 Skill 复用的规范、模板、工具均存放于此。
> 维护者：MSRA 架构组 · 最后更新：2026-06-25（Sprint 2）

---

## 按主题分类

### 1. 质量保障 (Quality Assurance)

跨阶段质量门闸、校准框架、反模式目录与检查点协议。

| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| [quality_gates/](quality_gates/) | 质量门闸定义与执行引擎（gate-data/gate-sap/gate-results + gate_runner.py + check_items.py + inference_runner.py） | pipeline |
| [quality_gates/gate-data.md](quality_gates/gate-data.md) | Stage 1.5 数据质量门闸定义（9 项检查） | pipeline |
| [quality_gates/gate-sap.md](quality_gates/gate-sap.md) | Stage 2.5 SAP 质量门闸定义（8 项检查） | pipeline |
| [quality_gates/gate-results.md](quality_gates/gate-results.md) | Stage 3.5 结果质量门闸定义（14 项检查） | pipeline |
| [quality_gates/gate_runner.py](quality_gates/gate_runner.py) | 门闸执行引擎 | pipeline |
| [quality_gates/check_items.py](quality_gates/check_items.py) | 门闸检查项实现 | pipeline |
| [quality_gates/inference_runner.py](quality_gates/inference_runner.py) | 推断执行器 | pipeline |
| [calibration/](calibration/) | 校准框架（协议+模板+自检+积累机制+门闸联动+Runner） | calibration, pipeline |
| [calibration/calibration_protocol.md](calibration/calibration_protocol.md) | 与 Pipeline 集成 + 门闸联动规则 | calibration, pipeline |
| [calibration/calibration_report_template.md](calibration/calibration_report_template.md) | 校准报告模板 | calibration |
| [calibration/self_validation.md](calibration/self_validation.md) | 校准系统自校验（3 项自检） | calibration |
| [calibration/data_accumulation.md](calibration/data_accumulation.md) | 真实校准数据积累机制 | calibration |
| [calibration/gate_linkage_rules.md](calibration/gate_linkage_rules.md) | 门闸联动详细规则 | calibration, pipeline |
| [calibration/calibration_framework.md](calibration/calibration_framework.md) | 校准框架总览 | calibration |
| [anti-patterns/medical_stats_anti_patterns.md](anti-patterns/medical_stats_anti_patterns.md) | 医学统计反模式目录（A1/B1/E1/F1-F4 等） | 所有 SKILL |
| [checkpoint_protocol.md](checkpoint_protocol.md) | 三级分层检查点协议（MANDATORY/SLIM/ADAPTIVE） | pipeline |
| [compliance_checkpoint_protocol.md](compliance_checkpoint_protocol.md) | 合规检查点协议 | pipeline, calibration |
| [clinical_results_validation.md](clinical_results_validation.md) | 临床结果验证协议 | analysis-exec, report |
| [cross_model_verification.md](cross_model_verification.md) | 跨模型验证协议 | calibration, analysis-exec |
| [raise_framework.md](raise_framework.md) | RAISE 框架（评估与改进） | pipeline, calibration |
| [style_calibration_protocol.md](style_calibration_protocol.md) | 风格校准协议 | calibration, report |

### 2. 统计方法 (Statistics Methods)

统计方法知识库、因果推断工作流、样本量计算与偏倚评估工具。

| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| [statistics-methods/](statistics-methods/) | 统计方法知识库（48 章指南 + 方法目录 + 决策树 + 约束规则） | analysis-plan, analysis-exec |
| [statistics-methods/chapters/](statistics-methods/chapters/) | 48 章统计方法详细指南 | analysis-plan, analysis-exec |
| [statistics-methods/METHOD_REGISTRY.md](statistics-methods/METHOD_REGISTRY.md) | 方法注册表 | analysis-plan |
| [statistics-methods/methods_catalog.md](statistics-methods/methods_catalog.md) | 方法目录 | analysis-plan |
| [statistics-methods/stat_test_decision_tree.md](statistics-methods/stat_test_decision_tree.md) | 统计检验决策树 | analysis-plan, analysis-exec |
| [statistics-methods/statistical_constraints.md](statistics-methods/statistical_constraints.md) | 统计约束规则（S-R/P-R/M-R/D-R/V-R 编码系统） | analysis-exec |
| [statistics-methods/observational-study-methods.md](statistics-methods/observational-study-methods.md) | 观察性研究方法（IPTW/AIPW/RCS/E-value） | analysis-exec |
| [statistics-methods/cheatsheet.md](statistics-methods/cheatsheet.md) | 统计方法速查表 | analysis-exec |
| [statistics-methods/glossary.md](statistics-methods/glossary.md) | 统计术语表 | 所有 SKILL |
| [causal-inference/](causal-inference/) | 因果推断工作流（Dowhy/PSM/重叠权重模板） | analysis-plan, analysis-exec, exploratory-causal |
| [causal-inference/causal_inference_workflow.md](causal-inference/causal_inference_workflow.md) | 因果推断工作流指南 | analysis-plan, exploratory-causal |
| [causal-inference/psm_template.py](causal-inference/psm_template.py) | 倾向性评分匹配模板 | analysis-exec |
| [causal-inference/overlapping_weighting_template.py](causal-inference/overlapping_weighting_template.py) | 重叠权重模板 | analysis-exec |
| [sample-size/](sample-size/) | 样本量计算器（Python + R 双实现） | analysis-plan |
| [sample-size/sample_size_calculator.py](sample-size/sample_size_calculator.py) | 样本量计算器（Python） | analysis-plan |
| [sample-size/sample_size_calculator.R](sample-size/sample_size_calculator.R) | 样本量计算器（R） | analysis-plan |
| [risk-of-bias/](risk-of-bias/) | 偏倚风险评估工具（RoB 2/ROBINS-I/QUADAS-2/PROBAST/GRADE） | analysis-plan, peer-review, systematic-survey |
| [risk-of-bias/RoB_2_checklist.md](risk-of-bias/RoB_2_checklist.md) | RoB 2（随机试验偏倚风险） | analysis-plan |
| [risk-of-bias/ROBINS_I_V2_checklist.md](risk-of-bias/ROBINS_I_V2_checklist.md) | ROBINS-I V2（非随机干预研究） | analysis-plan |
| [risk-of-bias/QUADAS_2_checklist.md](risk-of-bias/QUADAS_2_checklist.md) | QUADAS-2（诊断准确性研究） | analysis-plan |
| [risk-of-bias/PROBAST_checklist.md](risk-of-bias/PROBAST_checklist.md) | PROBAST（预测模型研究） | analysis-plan |
| [risk-of-bias/GRADE_framework.md](risk-of-bias/GRADE_framework.md) | GRADE 证据分级框架 | analysis-plan, peer-review |

### 3. 报告规范 (Reporting Guidelines)

医学研究报告规范清单、期刊投稿模板与写作参考资源。

| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| [reporting-guidelines/](reporting-guidelines/) | 21 个报告规范清单（CONSORT/STROBE/STARD/PRISMA 等） | report, analysis-exec, peer-review |
| [reporting-guidelines/CONSORT_checklist.md](reporting-guidelines/CONSORT_checklist.md) | CONSORT（随机对照试验） | report |
| [reporting-guidelines/STROBE_checklist.md](reporting-guidelines/STROBE_checklist.md) | STROBE（观察性研究） | report |
| [reporting-guidelines/STARD_checklist.md](reporting-guidelines/STARD_checklist.md) | STARD（诊断准确性研究） | report |
| [reporting-guidelines/PRISMA_2020_checklist.md](reporting-guidelines/PRISMA_2020_checklist.md) | PRISMA 2020（系统综述与荟萃分析） | report, systematic-survey |
| [reporting-guidelines/SPIRIT_checklist.md](reporting-guidelines/SPIRIT_checklist.md) | SPIRIT（临床试验方案） | analysis-plan |
| [reporting-guidelines/REMARK_checklist.md](reporting-guidelines/REMARK_checklist.md) | REMARK（肿瘤标志物研究） | report |
| [reporting-guidelines/statcheck_rules.md](reporting-guidelines/statcheck_rules.md) | statcheck 规则（统计一致性检查） | report |
| [reporting-guidelines/statcheck_patterns.py](reporting-guidelines/statcheck_patterns.py) | statcheck 模式实现 | report |
| [journal-templates/](journal-templates/) | 15 个期刊投稿格式模板（JSON 配置） | report |
| [references/](references/) | 写作参考资源（术语表/审慎表达/字数规范/IRB 术语） | report |
| [references/protected_hedging_phrases.md](references/protected_hedging_phrases.md) | 审慎表达短语库 | report |
| [references/word_count_conventions.md](references/word_count_conventions.md) | 字数规范 | report |
| [references/irb_terminology_glossary.md](references/irb_terminology_glossary.md) | IRB 术语表 | report |
| [references/academic_figure_table_types.md](references/academic_figure_table_types.md) | 学术图表类型说明 | report |
| [references/intent_clarification_protocol.md](references/intent_clarification_protocol.md) | 意图澄清协议 | pipeline |
| [references/psychometric_terminology_glossary.md](references/psychometric_terminology_glossary.md) | 心理测量学术语表 | report |
| [prisma_trAIce_protocol.md](prisma_trAIce_protocol.md) | PRISMA-trAIce 协议（AI 辅助系统综述追溯） | report, systematic-survey |

### 4. 数据与变量 (Data & Variables)

SAP 标准、方案遵循、变量标准化与数据处理工具。

| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| [sap/](sap/) | SAP 标准格式 + 变量选择指南 + 模板 + 一致性检查 | analysis-plan, analysis-exec |
| [sap/sap_standard.md](sap/sap_standard.md) | SAP 标准格式 | analysis-plan |
| [sap/variable_selection_guide.md](sap/variable_selection_guide.md) | 变量选择指南 | analysis-plan |
| [sap/templates/](sap/templates/) | SAP 模板（RCT/观察性/诊断/贝叶性/NMPA 5 种） | analysis-plan |
| [sap/sap_consistency_check.py](sap/sap_consistency_check.py) | SAP 一致性检查 | analysis-exec |
| [protocol_adherence/](protocol_adherence/) | 方案遵循框架 + 方法一致性规则 + 进度跟踪模板 | analysis-exec, pipeline |
| [protocol_adherence/protocol_adherence_framework.md](protocol_adherence/protocol_adherence_framework.md) | 方案遵循框架 | analysis-exec |
| [protocol_adherence/method_consistency_rules.md](protocol_adherence/method_consistency_rules.md) | 方法一致性规则 | analysis-exec |
| [protocol_adherence/progress_tracker_template.md](protocol_adherence/progress_tracker_template.md) | 进度跟踪模板 | pipeline |
| [variable_standardization/](variable_standardization/) | 自动化变量标准化模块 | analysis-exec, report, data-prep |
| [variable_standardization/variable_standardizer.py](variable_standardization/variable_standardizer.py) | 变量标准化器 | data-prep, analysis-exec |
| [variable_standardization/mapping_template.yaml](variable_standardization/mapping_template.yaml) | 变量映射模板 | data-prep |
| [value-normalization/](value-normalization/) | 数值与中医术语标准化（normalizer + 编码指南） | data-prep |
| [value-normalization/normalizer_guide.md](value-normalization/normalizer_guide.md) | 标准化指南 | data-prep |
| [value-normalization/tcm_variable_encoding.md](value-normalization/tcm_variable_encoding.md) | 中医变量编码 | data-prep |
| [variable_naming_standards.md](variable_naming_standards.md) | 变量命名标准（顶层文件） | 所有 SKILL |
| [data_sharing/](data_sharing/) | 去标识化与结果打包工具 | data-prep |
| [data_sharing/deidentification.py](data_sharing/deidentification.py) | 去标识化处理 | data-prep |
| [data_sharing/results_package_generator.py](data_sharing/results_package_generator.py) | 结果包生成器 | data-prep |
| [large_scale_processing/](large_scale_processing/) | 多引擎大规模数据处理（Pandas/Polars/DuckDB/Dask） | data-prep（独立工具模块） |
| [privacy/](privacy/) | 隐私保护策略（掩码 + 敏感检测） | data-prep |
| [privacy/masking_strategies.py](privacy/masking_strategies.py) | 掩码策略 | data-prep |
| [privacy/sensitivity_detector.py](privacy/sensitivity_detector.py) | 敏感信息检测器 | data-prep |

### 5. 图表与模板 (Charts & Templates)

发表级图表标准、R/Python 代码模板与报告组装工具。

| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| [chart-styles/](chart-styles/) | 发表级图表标准 + 变量命名规范（JSON 配置 + MD 规范） | analysis-exec, report |
| [chart-styles/publication_figure_standards.md](chart-styles/publication_figure_standards.md) | 发表级图表标准 | analysis-exec, report |
| [chart-styles/variable_naming_conventions.md](chart-styles/variable_naming_conventions.md) | 变量命名规范 | analysis-exec, report |
| [chart-styles/chart_types.json](chart-styles/chart_types.json) | 图表类型配置 | analysis-exec |
| [chart-styles/font_and_size_specs.json](chart-styles/font_and_size_specs.json) | 字体与尺寸规格 | report |
| [chart-styles/journal_color_schemes.json](chart-styles/journal_color_schemes.json) | 期刊配色方案 | report |
| [templates/](templates/) | R/Python 代码模板库（表格/图表/统计/生存分析等 90+ 模板） | analysis-exec, report |
| [templates/data-prep/](templates/data-prep/) | 数据准备模板（清洗日志/验证规则/EDA 等） | data-prep |
| [templates/quality-gates/](templates/quality-gates/) | 质量门闸报告模板 | pipeline |
| [templates/template_manager.py](templates/template_manager.py) | 模板管理器 | analysis-exec, report |
| [templates/baseline_table1_engine.py](templates/baseline_table1_engine.py) | Table 1 基线表生成引擎 | analysis-exec |
| [templates/publication_figure_template.py](templates/publication_figure_template.py) | 发表级图表模板 | report |
| [report_assembler/](report_assembler/) | HTML 报告渲染器 + Word 表格导出器 + 合规检查 | report |
| [report_assembler/render_report_html.py](report_assembler/render_report_html.py) | HTML 报告渲染器 | report |
| [report_assembler/export_tables_docx.py](report_assembler/export_tables_docx.py) | Word 表格导出器 | report |
| [report_assembler/compliance_checker.py](report_assembler/compliance_checker.py) | 合规检查器 | report |
| [chart_understanding/](chart_understanding/) | 图表 FDV（Full Description Vector）生成器 | report（独立工具模块） |
| [table_understanding/](table_understanding/) | 表格结构理解与验证（Chain-of-Table + Tree-of-Table） | report（独立工具模块） |

### 6. 错误诊断 (Error Diagnostics)

错误模式库、自动修复建议与代码修复参考。

| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| [error-diagnostics/](error-diagnostics/) | 错误模式库 + 自动修复建议 + 代码修复参考 | analysis-exec |
| [error-diagnostics/error_patterns.md](error-diagnostics/error_patterns.md) | 错误模式库 | analysis-exec |
| [error-diagnostics/auto_fix_suggestions.py](error-diagnostics/auto_fix_suggestions.py) | 自动修复建议（Python） | analysis-exec |
| [error-diagnostics/auto_fix_suggestions.R](error-diagnostics/auto_fix_suggestions.R) | 自动修复建议（R） | analysis-exec |
| [error-diagnostics/code_fixes_reference.md](error-diagnostics/code_fixes_reference.md) | 代码修复参考 | analysis-exec |

### 7. 可复现性 (Reproducibility)

复现验证指南、检查脚本与报告生成器。

| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| [reproducibility/](reproducibility/) | 复现验证指南 + 检查脚本 + 报告生成器 + 管道审计 | analysis-exec, pipeline |
| [reproducibility/reproducibility_guide.md](reproducibility/reproducibility_guide.md) | 复现验证指南 | analysis-exec |
| [reproducibility/reproducibility_check.py](reproducibility/reproducibility_check.py) | 复现性检查（Python） | analysis-exec |
| [reproducibility/reproducibility_check.R](reproducibility/reproducibility_check.R) | 复现性检查（R） | analysis-exec |
| [reproducibility/reproducibility_report_generator.R](reproducibility/reproducibility_report_generator.R) | 复现报告生成器 | analysis-exec |
| [reproducibility/reproducibility_integration.py](reproducibility/reproducibility_integration.py) | 复现性集成模块 | pipeline |
| [reproducibility/pipeline_auditor.py](reproducibility/pipeline_auditor.py) | 管道审计器 | pipeline |
| [artifact_reproducibility_pattern.md](artifact_reproducibility_pattern.md) | 产物可复现性模式（顶层文件） | analysis-exec, pipeline |

### 8. 合约与模式 (Contracts & Schemas)

JSON Schema 合约、Passport 状态管理与 Agent 间数据模式。

| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| [contracts/](contracts/) | JSON Schema 合约（passport/evaluator/reviewer/audit） | pipeline, 所有 SKILL |
| [contracts/passport/](contracts/passport/) | Passport Schema（11 个阶段状态定义） | pipeline |
| [contracts/evaluator/full.json](contracts/evaluator/full.json) | Evaluator 完整 Schema | analysis-exec |
| [contracts/reviewer/full.json](contracts/reviewer/full.json) | Reviewer 完整 Schema | peer-review |
| [contracts/reviewer/methodology_focus.json](contracts/reviewer/methodology_focus.json) | Reviewer 方法学聚焦 Schema | peer-review |
| [contracts/audit/](contracts/audit/) | 审计 Schema（JSONL/sidecar/verdict） | pipeline |
| [contracts/cross_domain_result_schema.md](contracts/cross_domain_result_schema.md) | 跨域结果 Schema | cross-domain |
| [passport/](passport/) | Material Passport 状态管理（Python 实现 + Schema 文档） | pipeline, data-prep |
| [passport/passport.py](passport/passport.py) | Passport 实现 | pipeline |
| [passport/passport_schema.md](passport/passport_schema.md) | Passport Schema 文档 | pipeline |
| [handoff_schemas.md](handoff_schemas.md) | Agent 间 Handoff 数据模式（12 Schema） | agents/, pipeline |
| [compliance_report.schema.json](compliance_report.schema.json) | 合规报告 JSON Schema | pipeline |
| [sprint_contract.schema.json](sprint_contract.schema.json) | Sprint 契约 JSON Schema | pipeline |
| [mode_spectrum.md](mode_spectrum.md) | 操作模式谱（顶层文件） | 所有 SKILL |
| [collaboration_depth_rubric.md](collaboration_depth_rubric.md) | 协作深度评分标准（顶层文件） | pipeline, agents/ |

---

## 跨 Skill 引用关系

```
data-prep          → anti-patterns, privacy, data_sharing, value-normalization, variable_standardization
analysis-plan      → statistics-methods, sap, reporting-guidelines, risk-of-bias, causal-inference, templates
analysis-exec      → templates, sap, chart-styles, anti-patterns, error-diagnostics, statistics-methods
report             → reporting-guidelines, templates, chart_understanding, journal-templates, report_assembler, references
calibration        → calibration, quality_gates
peer-review        → reporting-guidelines, risk-of-bias
systematic-survey  → reporting-guidelines, risk-of-bias
pipeline           → contracts, passport, reproducibility, protocol_adherence, quality_gates
exploratory-causal → causal-inference, statistics-methods
```

---

## 索引统计

| 维度 | 数量 |
|------|------|
| 主题分类 | 8 |
| 子目录 | 26 |
| 顶层文件 | 15 |
| 索引条目 | 75+ |

## 维护说明

- 新增 shared/ 资源时，必须同步更新本索引
- 路径变更时，必须同步修正本索引中的链接
- 验证脚本：`scripts/scan_reference_reachability.py`（Sprint 2 §2.5.3 提供）
- E2E 测试 E2E-035 验证本索引所有链接可达
