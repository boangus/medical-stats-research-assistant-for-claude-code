# Phase 5: 输出产物

> 参考：src/shared/templates/ — 代码模板目录（含 rstatix_template.R 管道友好检验、gtsummary_template.R 出版级表格、correlation_template.R 相关性分析、table1_template.R 基线表、cox_template.py 生存分析等）；src/shared/reproducibility/reproducibility_check.py — 输出复现验证

---

## 输出产物清单

1. **样本量验证报告**: 实际 vs 计划样本量对比（新增）
2. **变量构造代码和日志**: 按 SAP 生成分析变量的完整记录（新增）
3. **分析数据集**: 含所有原始变量 + SAP 定义的分析变量
4. **分析代码**: 完整、可重复、有注释
5. **描述性统计表**: Table 1 + 分布汇总
6. **依从性分析报告**: 用药依从率、合并用药汇总
7. **安全性分析报告**: AE/SAE汇总、实验室检查、生命体征
8. **结果表格**: 按SAP格式（主要/次要/探索性）
9. **图表**: 发表级质量，遵循 resources/chart-styles/publication_figure_standards.md
   - 强制 rcParams: font.family=sans-serif, font.sans-serif=['Arial',...], svg.fonttype='none'
   - 导出格式: SVG（首要）+ PNG 300dpi（预览）
   - 配色: 语义化调色板或期刊配色（journal_color_schemes.json）
   - 变量名: 遵循 variable_naming_conventions.md 规范显示名+单位
   - P值标注: 遵循 P-R01~R07（P<0.001 展示为 "P < 0.001"）
   - 模板: src/shared/templates/publication_figure_template.py
   - 多面板: 遵循三级信息层级（概览→偏差→关系），无冗余面板
   - 轴线: 仅左+下轴线，无边框图例
10. **假设检验报告**: 所有诊断结果
11. **质检报告**: 检查结果摘要
12. **偏差日志**: 与SAP的任何偏差
13. **审计日志**: 不可变操作记录（JSON Lines 格式）🆕

---

## 检查点

> [SLIM] 输出产物确认：展示 13 项产物的生成状态清单（✅/⚠️/❌），用户确认后交付到下一阶段。
