# Shared Resources — 共享资源索引

> MSRA 项目共享资源目录，供 Skills、Agents 和外部工具使用。

---

## 目录总览

| 子目录 | 文件数 | 用途 | 消费者 |
|--------|--------|------|--------|
| `templates/` | 92 | 统计分析代码模板 (R/Python) | analysis-exec, report |
| `statistics-methods/` | 59 | 统计方法知识库 (47章) | analysis-plan, report |
| `reporting-guidelines/` | 17 | 报告规范检查清单 (16个) | report, peer-review |
| `sap/` | 14 | 统计分析计划标准/模板 | analysis-plan, analysis-exec |
| `contracts/` | 13 | JSON Schema 契约 | pipeline |
| `value-normalization/` | 10 | 数值与中医术语标准化 | data-prep |
| `large_scale_processing/` | 7 | 多引擎大规模数据处理 | 独立工具模块 |
| `reproducibility/` | 7 | 可复现性检查框架 | pipeline |
| `journal-templates/` | 7 | 期刊投稿格式模板 | report |
| `report_assembler/` | 6 | 报告组装 (合规/导出/渲染) | report |
| `references/` | 6 | 术语表/写作指南 | 多个 skill |
| `error-diagnostics/` | 6 | 错误诊断与自动修复 | analysis-exec |
| `risk-of-bias/` | 5 | 偏倚风险评估工具 | analysis-plan, peer-review, systematic-survey |
| `chart-styles/` | 5 | 图表样式规范 | report |
| `causal-inference/` | 5 | 因果推断模板 | exploratory-causal, analysis-plan |
| `calibration/` | 5 | 校准框架 | calibration |
| `variable_standardization/` | 4 | 变量标准化 | data-prep |
| `table_understanding/` | 4 | 表格结构理解与验证 | 独立分析工具 |
| `sample-size/` | 3 | 样本量计算器 | analysis-plan |
| `protocol_adherence/` | 3 | 协议遵从框架 | pipeline |
| `passport/` | 3 | Material Passport | pipeline, data-prep |
| `data_sharing/` | 3 | 去标识化与结果打包 | data-prep |
| `privacy/` | 3 | 隐私保护策略 | data-prep |
| `chart_understanding/` | 2 | 图表 FDV 生成 | report |
| `anti-patterns/` | 1 | 医学统计反模式目录 | 全部 skill |

---

## 独立工具模块

以下模块设计为独立工具，既可被 Skills 引用，也可独立使用：

### large_scale_processing/ (大规模数据处理)

多引擎数据处理工厂，支持自动引擎选择：
- **Pandas**: <1GB 数据集
- **Polars**: 1-10GB 中型数据
- **DuckDB**: 10-100GB 大型数据
- **Dask**: >100GB 超大型数据

```python
from shared.large_scale_processing import EngineFactory
engine = EngineFactory.create_for_size(file_size_bytes)
```

### table_understanding/ (表格理解)

表格结构分析与验证工具：
- Chain-of-Table 验证
- Tree-of-Table 分析
- TableMaster 提取

### chart_understanding/ (图表理解)

图表 Full Description Vector (FDV) 生成器，用于自动化图表描述和验证。

### sample-size/ (样本量计算)

支持多种研究设计的样本量计算器：
- RCT (平行/交叉/非劣效)
- 观察性研究 (队列/病例对照)
- 诊断试验

---

## 跨 Skill 引用关系

```
data-prep ──→ anti-patterns, privacy, data_sharing, value-normalization, variable_standardization
analysis-plan ──→ statistics-methods, sap, reporting-guidelines, risk-of-bias, causal-inference, templates
analysis-exec ──→ templates, sap, chart-styles, anti-patterns, error-diagnostics
report ──→ reporting-guidelines, templates, chart_understanding, journal-templates, report_assembler
calibration ──→ calibration
peer-review ──→ reporting-guidelines, risk-of-bias
systematic-survey ──→ reporting-guidelines, risk-of-bias
pipeline ──→ contracts, passport, reproducibility, protocol_adherence
exploratory-causal ──→ causal-inference, statistics-methods
```

---

## 文件类型统计

| 类型 | 数量 | 说明 |
|------|------|------|
| .md | 140 | 文档、指南、模板 |
| .py | 80 | Python 代码模板和工具 |
| .R | 56 | R 代码模板 |
| .json | 26 | JSON Schema 契约 |
| 其他 | 2 | .csv, .yaml |

---

## 根目录协议文件

| 文件 | 用途 |
|------|------|
| `handoff_schemas.md` | 跨 Skill 数据契约 (12 Schema) |
| `artifact_reproducibility_pattern.md` | 产物可复现性模式 |
| `clinical_results_validation.md` | 临床结果验证协议 |
| `collaboration_depth_rubric.md` | 协作深度评分标准 |
| `compliance_checkpoint_protocol.md` | 合规检查点协议 |
| `cross_model_verification.md` | 跨模型验证协议 |
| `mode_spectrum.md` | 操作模式谱 |
| `prisma_trAIce_protocol.md` | PRISMA-trAIce 协议 |
| `raise_framework.md` | RAISE 框架 |
| `style_calibration_protocol.md` | 风格校准协议 |
| `variable_naming_standards.md` | 变量命名标准 |
