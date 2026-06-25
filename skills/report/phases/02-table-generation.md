# Phase 2: 表格生成与导出

> 来源：从 SKILL.md L406-519 抽取。本阶段包含两个子步骤：Step 2.1 生成 Markdown 表格 → Step 2.2 导出三线表 docx。

**Step 2.1: 生成 Markdown 表格**

**Table 1: 基线特征表**

```r
# R代码模板
library(gtsummary)

table1 <- cleaned_data %>%
  select(group, age, sex, bmi, sbp, smoking, diabetes) %>%
  tbl_summary(
    by = group,
    type = all_continuous() ~ "continuous2",
    statistic = list(
      all_continuous() ~ c("{mean} ({sd})", "{median} ({p25}, {p75})"),
      all_categorical() ~ "{n} ({p}%)"
    ),
    missing = "ifany"
  ) %>%
  add_p(test = list(
    all_continuous() ~ "wilcox.test",
    all_categorical() ~ "chisq.test"
  )) %>%
  add_overall() %>%
  bold_labels()
```

**结果表格模板**：

> **变量命名**：遵循 variable_naming_conventions.md 三列命名体系，表格中使用规范显示名+单位
> **P值格式**：遵循 statistical_constraints.md P-R01~R07（P<0.001 展示为 "P < 0.001"，禁止 P=0.000）

| 变量 | 效应量 | 95% CI | P 值 |
|------|--------|--------|------|
| 年龄 (岁) | HR 1.02 | 1.01-1.03 | P < 0.001 |
| 男性 vs 女性 | HR 1.35 | 1.12-1.63 | P = 0.002 |
| 治疗组 vs 对照组 | HR 0.75 | 0.62-0.91 | P = 0.004 |

> [SLIM] 表格生成完成后：核验关键数值是否与 Phase 1 提取结果一致，用户确认后进入图表生成。
> 核验项：变量名一致性（V-R02）、P值格式（P-R01~R07）、单位标注完整性（V-R05）。

**表格生成检查点**：

> 🔴 [MANDATORY-REPT-01] 表格生成完成后，必须展示以下内容给用户确认：
> 1. Table 1 基线特征表（样本量、缺失率、关键变量）
> 2. 主分析结果表（效应量、95%CI、p值）
> 3. 与 Phase 1 提取数字的一致性检查结果
>
> 用户确认后才能进入图表生成。

**表格生成异常处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 变量无组间差异（所有 p 值 > 0.9） | 检查样本量和效应量差异是否临床有意义 | 如实报告 null 结果，在表格中标注"未发现统计学显著差异"，并在脚注中说明检验效能 |
| 分类变量有频率为 0 的空水平 | 合并空水平到相邻类别或标记为"无观察" | 删除空行，在脚注中说明："XX变量因无观察值已排除" |
| 连续变量标准差为 0（所有值相同） | 检查数据是否录入错误或常量变量 | 排除该变量，在脚注中说明："XX变量因方差为0已排除，可能为常量变量" |
| Phase 1 提取数字与表格计算不一致 | 重新计算，定位差异来源（四舍五入/截断差异） | 以表格计算结果为准，在脚注标注差异来源，生成差异对比表 |
| 表格列数过多（>15 列）导致可读性差 | 拆分为子表（基线/结果/亚组分表） | 输出横向页面表格，在每页标注"续表X"，提供完整表格合并版 |
| 混合类型列（数值+文本混排）无法渲染 | 分裂为两列（数值列+注释列） | 标记为"格式待整理"，在脚注中说明原因，提供清理后的纯数值版本 |

**Step 2.2: 三线表导出 (→ docx)**

> 参考：shared/report_assembler/export_tables_docx.py — Word 三线表导出器
> R 版本参考：shared/templates/export_tables_flextable.R

将 Step 2.1 生成的表格（基线特征表、回归结果表等）导出为符合医学期刊格式的 `.docx` 三线表。

**三线表规范**：
- 顶线粗 (2pt)、表头下线中 (1pt)、底线粗 (2pt)
- 无竖线、无左右端线
- 表题在上方居中，表注在下方
- 第一列左对齐，其余居中

**Step 2.2.1: 确定需要导出的表格**

| 表格 | 默认文件名 | 说明 |
|------|-----------|------|
| Table 1 基线特征 | `table1_baseline.docx` | 按分组展示基线特征 |
| 主分析结果表 | `table2_main_results.docx` | 回归分析 (OR/HR/β 及其 95%CI) |
| 敏感性分析表 | `table3_sensitivity.docx` | 敏感性分析结果 |
| 亚组分析表 | `table4_subgroup.docx` | 亚组分析结果 |

**Step 2.2.2: 调用导出脚本**

```bash
# Python 版 (首推)
python shared/report_assembler/export_tables_docx.py \
  --input-md "| 变量 | OR | 95% CI | p |\n|---|...|" \
  --output reports/tables/table2_regression.docx \
  --title "表2 Logistic回归结果" \
  --note "OR: 比值比; CI: 置信区间"

# R flextable 版 (备选, 需 R + flextable)
Rscript shared/templates/export_tables_flextable.R
```

> 完整代码示例（含自定义样式、中文字体处理）见 `shared/report_assembler/export_tables_docx.py` 和 `shared/templates/export_tables_flextable.R`。

**Step 2.2.3: 异常处理**

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| python-docx 未安装 | `pip install python-docx` 后重试 | 输出CSV格式文件，提供手动格式化指南（含Word模板链接） |
| 表格内容为空 | 跳过导出，记录日志 | 生成占位表格，标注"数据待补充"，提供数据输入模板 |
| 列数过多 (>10列) | 提示用户拆分表格或调整页面方向为横向 | 自动拆分为子表 (Table 2a, 2b)，在每页标注"续表" |
| 中文显示乱码 | 指定字体为 "SimSun" 或 "Microsoft YaHei" | 输出英文表头版本，同时提供中文字体安装指南 |

> [SLIM] Checkpoint: 展示已导出的 docx 文件清单给用户确认。
