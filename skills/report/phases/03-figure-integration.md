# Phase 3: 图表整合

> 来源：从 SKILL.md L520-680 抽取。
> 优先复用 analysis-exec Phase 5 已生成的发表级图表；仅当 analysis-exec 未生成所需图表时，才在本阶段补充生成。
> 自动加载 shared/templates/ 中的 R/Python 模板，传入分析数据执行并保存。
> **发表级标准**：遵循 shared/chart-styles/publication_figure_standards.md
> **首选模板**：shared/templates/publication_figure_template.py（含 nature-figure 标准 rcParams、调色板、辅助函数）
> **变量命名**：遵循 shared/chart-styles/variable_naming_conventions.md（规范显示名+单位）
> **P值格式**：遵循 statistical_constraints.md P-R01~R07（P<0.001 展示为 "P < 0.001"）

**Step 3.1: 分析类型 → 图类型映射**

> 完整图表类型清单见：shared/references/academic_figure_table_types.md

根据分析结果自动确定需要哪些图表：

| 分析类型 | 生成图表 | 首选模板（发表级） | 备选模板 |
|---------|---------|------------------|---------|
| 生存分析 (Cox/KM) | KM 曲线 + 森林图 (可选) | publication_figure_template.py (make_km_curve) | cox_template.py, survival_ggsurvfit.R |
| 竞争风险分析 | 累积发生率曲线 | competing_risks_template.R | — |
| Logistic/回归 | 森林图 | publication_figure_template.py (make_forest_plot) | forest_plot_template.py |
| Meta分析 | 森林图 + 漏斗图 | forest_plot_template.py | — |
| 诊断试验 (ROC) | ROC 曲线 + PR曲线 | publication_figure_template.py (make_roc_curve) | roc_template.py, roc_visualization_template.R |
| 一致性检验 | Bland-Altman 图 | bland_altman_template.py | — |
| 预测模型 | 校准曲线 + 决策曲线 | publication_figure_template.py (make_calibration_curve) | calibration_plot_template.R |
| 基线特征 | Table 1 结构化图 | table1_template.R, gtsummary_template.R | janitor_tabyl_template.R |
| 相关性分析 | 相关性热图 | publication_figure_template.py (make_heatmap) | correlation_template.R |
| 连续变量分布 | 箱线图 + 小提琴图 | publication_figure_template.py (make_box_plot) | enhanced_chart_template.py |
| 分组比较 | 柱状图 | publication_figure_template.py (make_bar_chart) | — |
| 变量关系 | 散点图 + 气泡图 | publication_figure_template.py (make_scatter_plot) | — |
| 非线性关系 | RCS 曲线 | publication_figure_template.py (make_rcs_plot) | — |
| 倾向性评分 | PS分布图 + Love Plot | propensity_score_template.py | ps_diagnostics_template.py |
| 因果推断 | DAG图 | dag_variable_selection_template.R | — |
| 机器学习 | SHAP图 + 特征重要性 | shap_plot_template.py | ml_analysis_template.py |
| 样本量计算 | 样本量曲线 + 效能曲线 | sample_size_template.py | — |
| 敏感性分析 | Tipping Point图 + E-value图 | multiple_imputation_template.py | effect_size_template.py |
| RCT流程 | CONSORT流程图 | publication_figure_template.py | — |
| 系统综述 | PRISMA流程图 | publication_figure_template.py | — |

**Step 3.2: 加载模板**

从 `shared/templates/` 读取对应模板文件。优先使用 Python 模板（环境一致性高）。
如果该图表仅有 R 模板（如校准曲线），直接使用 R。

```
模板选择规则:
  1. 首选 Python 模板 (shared/templates/*.py)
  2. 若 Python 模板不存在，使用 R 模板 (shared/templates/*.R)
  3. 若 Python 模板存在但执行失败 → 降级到 R 模板重试（最多1次）
     → 若 R 模板也失败 → 输出: "[ERROR] 全部模板执行失败。请检查环境和依赖后重试"
     → 打印具体错误信息
  4. 若仅有 R 模板 → 直接执行，标注 "R implementation"
```

**Step 3.3: 传入数据 → 执行 → 保存 SVG+PNG**

> 使用 publication_figure_template.py 时，自动应用发表级标准：
> - 三行强制 rcParams（font.family, svg.fonttype='none'）
> - 语义化调色板或期刊配色
> - SVG（首要）+ PNG 300dpi（预览）双格式导出
> - **PDF格式支持**：在SVG+PNG基础上，增加PDF格式导出，便于学术论文投稿
> - 变量名使用规范显示名+单位
> - P 值格式遵循 P-R01~R07

- 将实际分析结果（估计值、置信区间、p 值等）构造为模板所需的输入格式
- 图片保存到 `reports/figures/{分析名}_{图类型}.svg`（矢量，首要）+ `.pdf`（学术投稿）+ `.png`（300 DPI 预览）
- 图片保存到 `reports/figures/{分析名}_{图类型}.svg`（矢量，首要）+ `.png`（300 DPI 预览）
- 记录执行方式和路径：`{图类型}: Python/R, saved to reports/figures/...`

```python
# Python 示例 — 使用发表级模板
import subprocess
result = subprocess.run(
    ["python", template_path, "--data", data_path, "--out", output_path,
     "--format", "svg,pdf,png", "--dpi", "300"],
     "--format", "svg,png", "--dpi", "300"],
    capture_output=True, text=True, timeout=300
)

# 或直接调用 publication_figure_template.py 中的函数
import sys
sys.path.insert(0, "shared/templates")
from publication_figure_template import (
    apply_publication_style, make_forest_plot, export_figure, format_p_value
)

apply_publication_style(font_size=10, support_chinese=True)
fig, ax = make_forest_plot(
    labels=var_labels,  # 规范显示名
    estimates=estimates, ci_lower=ci_lower, ci_upper=ci_upper,
    p_values=p_values,  # 自动格式化 P 值
    xlabel="HR (95% CI)"
)
export_figure(fig, "reports/figures/figure1_forest")  # SVG + PNG
```

```r
# R 示例
result <- system2(
    "Rscript", c(template_path, "--data", data_path, "--out", output_path),
    stdout=TRUE, stderr=TRUE
)
```

**Step 3.4: 调用模板生成图表**

```bash
# Python 森林图 — 完整 API 见 shared/templates/forest_plot_template.py
python shared/templates/forest_plot_template.py \
  --data results/forest_data.csv \
  --output reports/figures/figure1_forest.png \
  --title "图1 多因素Logistic回归森林图" \
  --dpi 300

# R KM 曲线 — 完整 API 见 shared/templates/survival_ggsurvfit.R
Rscript shared/templates/survival_ggsurvfit.R \
  --data results/survival_data.csv \
  --output reports/figures/figure2_km_curve.png \
  --title "图2 Kaplan-Meier生存曲线"

# Python ROC 曲线 — 完整 API 见 shared/templates/roc_template.py
python shared/templates/roc_template.py \
  --y-true results/y_test.csv \
  --y-score results/y_pred.csv \
  --output reports/figures/figure3_roc.png \
  --title "图3 预测模型ROC曲线"
```

> 完整代码示例（含自定义样式、中文字体、参数详解）见各模板文件：
> - `shared/templates/forest_plot_template.py`
> - `shared/templates/survival_ggsurvfit.R`
> - `shared/templates/roc_template.py`
> - `shared/templates/bland_altman_template.py`

**Step 3.5: 异常处理**

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| R/Python 包未安装 | 自动 pip install / install.packages 重试 (最多1次) | 生成纯文本描述（含关键数据点），标注"[图表暂不可用：依赖缺失]"，提供安装命令和依赖清单 |
| 数据不足绘制完整图表 | 简化图表（减少分组/调整分类数） | 输出数据CSV + 生成代码文件，用户可自行执行或调整参数后重新生成 |
| 坐标轴/图例混乱 | 手动调整参数（limits/breaks/labels） | 提供两个选项：(1) 使用简化图表 (2) 暂停等待用户确认参数设置 |
| 中文显示乱码 | 指定字体 'SimHei' 或 'Microsoft YaHei' | 生成英文版本图表，同时提供中文字体安装指南 |
| 图像分辨率不足 | 设置 dpi=300 或更高 | 输出矢量图 (PDF/SVG)，同时提供低分辨率PNG预览 |

> [ADAPTIVE] Checkpoint: 图表生成后展示图片路径给用户确认，不满意可重新生成参数。
> **触发条件**：当满足以下任一条件时执行完整质量检查：
> - 图表总数 ≥ 3 张
> - 图表类型 ≥ 2 种（如同时包含KM曲线和森林图）
> - 包含复杂图表（如多面板图、3D图、交互式图表）
> - 用户明确要求高质量输出（如"发表级"、"投稿用"）
> **检查内容**：分辨率、字体、配色、标注完整性、格式规范
> **不满足阈值**：仅展示路径和基本预览，跳过详细质量检查

**图表生成检查点**：

> 🔴 [MANDATORY-REPT-02] 图表生成完成后，必须展示以下内容给用户确认：
> 1. 图表文件路径和预览
> 2. 图表类型和参数设置
> 3. 与分析结果的一致性检查
>
> 用户确认后才能进入方法学描述。
