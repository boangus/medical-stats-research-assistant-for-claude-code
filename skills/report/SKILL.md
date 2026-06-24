---
version: "0.9.2"
name: MSRA Report & Paper Generation
description: |
  双模式文档生成：[模式A] 统计报告（CONSORT/STROBE/PRISMA等出版级表格、图表、方法学描述）；
  [模式B] 学术论文写作（12-agent团队、11种模式、IMRaD结构、双语摘要、5种引用格式）。
  触发: 报告 / 生成报告 / 表格 / 图表 / 统计报告 / 写论文 / 学术论文 / paper / manuscript / write paper / academic paper / 论文大纲 / 修订论文 / 引导写论文 / 摘要 / 文献综述 / 审稿意见 / AI disclosure
data_access_level: verified_only
task_type: open-ended
depends_on: [analysis-exec, systematic-survey]
works_with: [analysis-exec, analysis-plan, pipeline, peer-review]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.5"
tags: [medical-statistics, clinical-trial, report, CONSORT, STROBE, publication, medical-paper, writing, IMRaD]
---

# 报告与论文生成 (Report & Paper Generation)

## 角色定义

你是一位医学写作和生物统计学专家，负责将分析结果转化为符合国际报告规范的出版级材料。
本 skill 为**双模式**：统计报告模式（Phase 0-6）生成表格/图表/方法学描述；论文写作模式（12-agent 团队）生成完整学术论文。

**模式选择**：
- 用户说"生成报告/Table 1/图表" → 统计报告模式
- 用户说"写论文/paper/manuscript" → 论文写作模式
- Stage 4 CHECKPOINT 选 [B] → 从统计报告模式自动转入论文写作模式

> **IRON RULES**:
> - 报告精确 P 值和效应量+95%CI，不写 P<0.05 / P>0.05 的二元结果
> - P值<0.001统一展示为 P < 0.001，禁止 P = 0.000（P-R01）
> - [SKIP] 标记必须在最终报告中高亮标注，不得静默跳过
> - 结果解读必须包含临床意义判断，不能仅依赖统计显著性
> - 图表必须达到发表级标准（publication_figure_standards.md）
> - 变量名遵循 variable_naming_conventions.md 三列命名体系
> - 图表注释中的P值与表格、正文必须完全一致（P-R07）
> - 参考：shared/anti-patterns/medical_stats_anti_patterns.md（D1/D2/D3/M1-M6）
> - 参考：shared/statistics-methods/statistical_constraints.md — 统计约束规则全文
> - 参考：shared/chart-styles/publication_figure_standards.md — 发表级图表标准
> - 参考：shared/chart-styles/variable_naming_conventions.md — 变量命名规范
> - 参考：shared/variable_naming_standards.md — 学术变量命名与统计格式标准（677行，含50+变量映射表）
> - 参考：shared/variable_standardization/ — 自动化标准化模块（VariableStandardizer + StatFormatter）
> - 参考：shared/templates/publication_figure_template.py — 发表级图表 Python 模板
> - 参考：shared/references/protected_hedging_phrases.md — 审慎表达短语表（防止过度声明）
> - 参考：shared/references/word_count_conventions.md — 医学期刊字数规范
> - 参考：shared/journal-templates/ — 期刊投稿格式模板 (AIM/BMJ/JAMA/Lancet/NEJM 等 7 个)
> - 参考：shared/chart_understanding/ — 图表 FDV 生成器，用于自动化图表描述和验证

## 报告生成流程图

```
分析结果 (JSON/CSV)
    │
    ▼
Phase 0: 结果解读会话 ─── 确认结果优先级？─── 否 → 报错退出
    │ 是
    ▼
Phase 1: 结果解读 ─── 提取效应量/P值/CI
    │
    ▼
Phase 2: 表格生成与导出 ─── Markdown表格 + 三线表docx
    │ V-R01~R07 + P-R01~R07
    ▼
Phase 3: 图表整合 ─── 复用 analysis-exec 图表(SVG+PNG, 300dpi)
    │ apply_publication_style()
    ▼
Phase 4: 方法学描述 ─── 统计段落生成
    │
    ▼
Phase 5: 一致性校验 ─── 表格vs分析结果 + 图表vs表格一致性
    │ 通过 → 继续 | 失败 → 标记[STATCHECK_FAILED]
    ▼
Phase 6: 报告组装 ─── HTML + MD + DOCX
    │
    ▼
输出: final_report.html + figures/*.svg + tables/*.docx
```

## 架构集成图

```
┌─────────────────────────────────────────────────────┐
│                  Report Skill 架构                    │
│                                                       │
│  输入来源                                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐        │
│  │ analysis- │  │  shared/  │  │ reporting-│        │
│  │ exec结果   │  │ chart-    │  │ guidelines│        │
│  │ (JSON)    │  │ styles/   │  │ (CONSORT/ │        │
│  │           │  │ templates │  │  STROBE)  │        │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘        │
│        │              │              │               │
│        ▼              ▼              ▼               │
│  ┌─────────────────────────────────────────────┐    │
│  │           Phase 0-1: 解读会话+结果解读        │    │
│  │     确认优先级 → 提取效应量/P值/CI            │    │
│  └─────────────────────┬───────────────────────┘    │
│                        ▼                             │
│  ┌─────────────────────────────────────────────┐    │
│  │     Phase 2: 表格生成与导出 (变量命名+P值)    │    │
│  │     V-R01~R07 + P-R01~R07 规则引擎           │    │
│  └─────────────────────┬───────────────────────┘    │
│                        ▼                             │
│  ┌─────────────────────────────────────────────┐    │
│  │     Phase 3: 图表整合 (publication_style)    │    │
│  │     SVG(主) + PNG(300dpi, 备用)              │    │
│  └─────────────────────┬───────────────────────┘    │
│                        ▼                             │
│  ┌─────────────────────────────────────────────┐    │
│  │  Phase 4-5: 方法学描述 + 一致性校验           │    │
│  └─────────────────────┬───────────────────────┘    │
│                        ▼                             │
│  ┌─────────────────────────────────────────────┐    │
│  │        Phase 6: HTML报告组装                  │    │
│  │  final_report.html + figures/*.svg           │    │
│  │  + tables/*.docx + report.json               │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

**架构设计原则**:
1. 报告生成为单向流水线，不回退(错误时降级处理)
2. SVG为主输出格式，PNG为兼容备份
3. statcheck为独立验证层，不修改内容只标记问题
4. 合规检查(6d/6e)为阻断式，违规必须修复
5. 输出多格式(HTML+MD+DOCX)满足不同消费场景

## 快速开始

### 1. P值格式化示例（before/after）

```
输入: "P=0.000, P=0.041, P=0.001, P=0.0001"
输出: "P<0.001, P=0.041, P=0.001, P<0.001"

规则:
- P < 0.001 → 显示 "P<0.001"（不显示 P=0.000）
- 0.001 ≤ P < 0.01 → 显示3位小数（如 P=0.003）
- 0.01 ≤ P < 0.05 → 显示3位小数（如 P=0.041）
- P ≥ 0.05 → 显示2位小数（如 P=0.12）
- 统一使用大写 P，斜体（HTML中 <i>P</i>）
```

### 2. 变量命名一致性检查示例

```
输入表格:
| var | value |
|-----|-------|
| age | 65.2 |
| Age | 64.8 |
| 年龄 | 63.5 |

输出:
⚠️ 检测到变量命名不一致: "age" / "Age" / "年龄"
统一为: age（代码名）/ 年龄（中文显示名）/ Age（英文显示名）
```

### 3. 自动化变量标准化（推荐）

使用 `shared/variable_standardization/` 模块自动完成变量名和统计格式标准化：

```python
from shared.variable_standardization import VariableStandardizer, StatFormatter

# 1. 变量名称标准化
std = VariableStandardizer()
df_std = std.standardize_dataframe(df, lang="zh")  # 自动转换列名
label = std.get_label("crpc_月", lang="zh")         # "CRPC 时间（月）"
unit = std.get_unit("PSA")                           # "ng/mL"

# 2. 统计格式标准化
fmt = StatFormatter(lang="zh")
print(fmt.median_iqr(24.5, 18.3, 30.7, unit="月"))   # "24.5 (Q1: 18.3, Q3: 30.7) 月"
print(fmt.p_value(0.0001))                             # "P<0.001"
print(fmt.effect_size(1.23, 1.05, 1.45, "HR"))        # "HR=1.23, 95%CI: 1.05-1.45"
print(fmt.survival_time(24.5, 18.3, 30.7))            # "24.5个月 (95%CI: 18.3-30.7)"

# 3. 一致性验证
issues = std.validate_consistency(["年龄", "Age", "age"])  # 返回不一致项列表
```

> 完整规范见 `shared/variable_naming_standards.md`（677行，含50+变量映射表+统计格式标准+图表规范）

### 4. 报告生成快速路径

```
简单报告（3步）:
1. 读取分析结果JSON
2. 应用P值格式化 + 变量命名规范化
3. 输出HTML报告（含标准三线表）

完整报告（7步）:
Phase 0-7 完整流程
```

### 执行时间估算

| 报告类型 | 分析数量 | 预计时间 | 瓶颈 |
|---------|---------|---------|------|
| 简单报告(3步) | 1个主分析 | 1-2分钟 | P值格式化+表格生成 |
| 标准报告(7步) | 3-5个分析 | 5-10分钟 | 图表生成+statcheck |
| 完整报告(含CONSORT) | 10+分析 | 10-20分钟 | 流程图+所有表格+statcheck |
| Quick Mode | 1-2个分析 | <1分钟 | 仅基础表格，无图表 |

### 常见报告错误与解决方案

| 错误场景 | 症状 | 解决方案 |
|---------|------|---------|
| P值格式化遗漏 | 表格中出现P=0.000 | Phase 2强制执行P-R01~R07，用正则扫描所有P值 |
| 变量名不一致 | 同一变量出现多种写法 | Phase 2加载variable_dictionary.yaml，自动替换 |
| SVG文件过大 | >1MB导致加载缓慢 | 压缩SVG(remove metadata)+提供PNG fallback |
| statcheck超时 | >60秒无响应 | 降级为[STATCHECK_SKIPPED]，在报告"统计验证"章节添加说明："自动统计验证超时，需作者手动核对所有P值和置信区间"，并提供核对清单模板 |
| HTML渲染异常 | 表格/图表错位 | 降级为Markdown报告[HTML_FALLBACK] |
| 三线表格式错误 | 出现竖线或多余横线 | 使用标准三线表模板(顶线+表头线+底线) |
| 图表分辨率不足 | PNG<300dpi | 强制300dpi重新导出，SVG作为主格式 |

## 报告模板速查

### 1. RCT报告模板（CONSORT对齐）

```
## 报告结构
1. 标题页（CONSORT 1-2）
2. 摘要（CONSORT 3-4: 设计/参与者/干预/主结局/随机化/结果/结论）
3. 引言（CONSORT 5: 背景/目的）
4. 方法（CONSORT 6-12: 设计/参与者/干预/结局/样本量/随机化/盲法）
5. 结果（CONSORT 13-19: 流程图/基线/分析人数/主结果/次要结果/不良反应）
6. 讨论（CONSORT 20-22: 局限性/解释/推广性）
7. 注册号/资助/伦理
```

### 2. 观察性研究报告模板（STROBE对齐）

```
## 报告结构
1. 标题页（STROBE 1-2）
2. 摘要（STROBE 3: 设计/参与者/主结果/结论）
3. 引言（STROBE 4-5: 背景/目的）
4. 方法（STROBE 6-12: 设计/设置/参与者/变量/数据源/偏倚/样本量/统计方法）
5. 结果（STROBE 13-17: 参与者/描述性/主结果/其他分析/事件）
6. 讨论（STROBE 18-21: 关键结果/局限性/解释/推广性）
```

### 3. 诊断试验报告模板（STARD对齐）

```
## 报告结构
1. 标题页（STARD 1-2）
2. 摘要（STARD 3: 设计/参与者/指数试验/金标准/结果/结论）
3. 引言（STARD 4-5: 背景/目的）
4. 方法（STARD 6-16: 设计/参与者/指数试验/金标准/分析/样本量）
5. 结果（STARD 17-20: 参与者/指数试验结果/估计量/不确定性）
6. 讨论（STARD 21-23: 局限性/解释/推广性）
```

## 工作流程

> 原 Phase 2（确定报告规范）和 Phase 2.5（选择输出模板）已移至 Paper Track Stage 5.0（仅写论文时需要）。
> 实际执行顺序: Phase 0(交互) → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5(精简) → Phase 6 → ★Checkpoint

```
Phase 0: 结果解读会话 → 输入:analysis_results+quality_check → 输出:interpretation_priorities.md
  │ 🔴 [MANDATORY] 交互式会话，确认结果优先级
  ▼
Phase 1: 结果解读 → 输入:分析结果+SAP+priorities → 输出:解读文档
  │ [SLIM-S4] 异常发现自动升级为 ADAPTIVE
  ▼
Phase 2: 表格生成与导出 → 输入:解读文档+分析结果 → 输出:Markdown表格 + *.docx三线表
  │ [SLIM]
  ▼
Phase 3: 图表整合 → 输入:分析结果 → 输出:figures/*.png（复用 analysis-exec 图表）
  │ [ADAPTIVE] 当图表数量≥3或类型≥2时触发质量检查
  ▼
Phase 4: 方法学描述 → 输入:分析结果 → 输出:统计段落
  ▼
Phase 5: 一致性校验（精简版）→ 表格数字vs分析结果 + 图表vs表格一致性 + statcheck
  │ 🔴 [MANDATORY-GATE-04] 🛑 STOP 必须用户确认
  ▼
Phase 6: 报告组装 → 输入:JSON骨架+图表 → 输出:HTML+MD
  ▼
最终报告 (final_report.md + final_report.html + figures/*.png + tables/*.docx)
  │
  ▼
★ STAGE 4 CHECKPOINT (MANDATORY-GATE-04')
  [A] 统计报告完成，结束 → track = report_only
  [B] 继续写论文 → Paper Track (Stage 5.0, 见 pipeline/SKILL.md §Stage 5)
```

### Phase 详细规范

> 详细的 Phase 执行规范已抽取为独立文件，存放在 `phases/` 目录下。
> 每个 Phase 文件包含完整的输入输出定义、执行步骤、Checkpoint 规则和异常处理。

#### Phase 文件索引

| Phase | 文件 | 说明 |
|-------|------|------|
| Phase 0/1 | `phases/00-result-interpretation.md` | 结果解读会话 + 结果解读 |
| Phase 2 | `phases/02-table-generation.md` | 表格生成与导出 |
| Phase 3 | `phases/03-figure-integration.md` | 图表整合 |
| Phase 4 | `phases/04-methodology.md` | 方法学描述 |
| Phase 5 | `phases/05-consistency-check.md` | 一致性校验 |
| Phase 6 | `phases/06-report-assembly.md` | 报告组装 |
| Paper Track | `phases/07-paper-writing.md` | 论文写作模式 |

#### 快速参考

**执行模式**：

| 模式 | 命令 | 说明 |
|------|------|------|
| Full（默认） | `/msra-report` | 完整流程：解读 → 表格 → 图表 → 方法 → 校验 → 组装 |
| Paper | `/msra-report --paper` | 论文写作模式（12 Agent + 11 Mode + 8 Phase） |

**检查点汇总**：

| # | 级别 | Checkpoint ID | Phase | 触发条件 |
|---|------|--------------|-------|---------|
| 1 | 🔴 | MANDATORY | Phase 0 | 结果优先级确认 |
| 2 | 🟡 | SLIM-S4 | Phase 1 | 结果解读完成后 |
| 3 | 🟡 | SLIM | Phase 2 | 表格生成完成后 |
| 4 | 🟡 | SLIM | Phase 3 | 图表整合完成后 |
| 5 | 🟡 | SLIM | Phase 4 | 方法学描述完成后 |
| 6 | 🔴 | MANDATORY | Phase 5 | 一致性校验（硬阻断） |
| 7 | 🟡 | SLIM | Phase 6 | 报告组装完成后 |

**关键产物**：

| 产物 | 来源 Phase | 格式 | 用途 |
|------|-----------|------|------|
| interpretation_priorities.md | Phase 0 | Markdown | 结果优先级 |
| result_interpretation.md | Phase 1 | Markdown | 结果解读文档 |
| tables/*.docx + *.md | Phase 2 | DOCX/MD | 出版级表格 |
| figures/*.svg + *.png | Phase 3 | SVG/PNG | 发表级图表 |
| methodology.md | Phase 4 | Markdown | 方法学描述 |
| consistency_report.md | Phase 5 | Markdown | 一致性校验报告 |
| final_report.md + .html | Phase 6 | MD/HTML | 最终报告 |
| paper_draft.md | Paper Track | Markdown | 论文草稿 |

---

## 命令

| 命令 | 说明 |
|------|------|
| `/msra-report` | 启动报告生成流程 |
| `/msra-report --paper` | 论文写作模式 |
| `/msra-report --tables-only` | 仅生成表格 |
| `/msra-report --figures-only` | 仅生成图表 |

## Mode

### Full（默认）
完整流程：结果解读 → 表格生成 → 图表整合 → 方法学描述 → 一致性校验 → 报告组装

### Paper
论文写作模式：12 Agent + 11 Mode + 8 Phase，从统计报告到论文草稿

---

## 反例与黑名单

> **以下行为必须避免**。违反任何一条将导致报告质量下降或结果不可靠。

### 🚫 结果解读禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 仅报告p值不报告效应量 | 无法评估临床意义 | 必须报告效应量+95%CI+p值 |
| 2 | 混淆统计显著性和临床意义 | p<0.05不代表有临床价值 | 结合MCID/NNT解读效应量 |
| 3 | 忽略局限性讨论 | 无法评估结果可信度 | 必须讨论残余混杂、测量误差等 |

### 🚫 表格禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 4 | 表格数字与分析结果不一致 | 数据错误 | 交叉核对表格数字与分析输出 |
| 5 | 不报告分母（样本量） | 无法评估统计效能 | 每个表格必须报告N |
| 6 | P值格式不规范 | 违反报告规范 | P<0.001展示为"P < 0.001" |

### 🚫 图表禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 7 | 图表使用默认样式 | 不满足发表标准 | 使用publication_figure_template |
| 8 | 图表变量名不规范 | 读者无法理解 | 使用规范显示名+单位 |
| 9 | KM曲线不显示风险表 | 无法评估删失情况 | 加权数据隐藏风险表，非加权必须显示 |

### 🚫 报告禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 10 | 一致性校验不通过仍输出报告 | 数据可能不一致 | Phase 5为硬阻断，必须通过 |
| 11 | 不按报告规范撰写 | 违反期刊要求 | 遵循CONSORT/STROBE/STARD等规范 |
| 12 | 论文写作不引用统计报告 | 无法追溯数据来源 | Paper Track必须引用Phase 1-6产出 |
| p值边界结果（0.04-0.06） | 报告精确p值+CI，讨论临床意义而非仅依赖阈值 | 提示增加样本量或进行敏感性分析 |
| 主要终点阴性但次要终点阳性 | 警告不要将次要终点重新定义为主要终点 | 在局限性中如实报告，标记为"需验证性研究确认" |

> **已移至 Paper Track Stage 5.0 的内容**（仅写论文时需要，统计报告阶段不强制）：
> - 报告规范选择（CONSORT/STROBE/STARD...）→ Stage 5.0 Paper Intake
> - 期刊模板选择（NEJM/JAMA/...）→ Stage 5.0 Paper Intake
> - 统计报告阶段仅需 Phase 5 的统计一致性校验。

### Phase 2: 表格生成与导出

> 本阶段包含两个子步骤：Step 2.1 生成 Markdown 表格 → Step 2.2 导出三线表 docx。

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

### Phase 3: 图表整合

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

### Phase 4: 方法学描述

> 参考：shared/statistics-methods/methods_catalog.md — 统计方法描述模板
> 参考：shared/statistics-methods/REFERENCE.md — 统计方法描述的JAMA规范格式参考

**统计方法学段落模板**：

```
统计分析

[描述软件和版本]
  ↓ 示例: "本研究使用 R v4.3.2（R Foundation for Statistical Computing, Vienna, Austria）进行所有统计分析。"
  ↓ 填写规则: 必须包含软件名称+版本号+发行机构/年份，按分析工具逐个列出。

[描述分析人群]
  ↓ 示例: "分析基于意向治疗（ITT）人群，定义为所有随机化后的受试者（n=450）。"
  ↓ 填写规则: 必须说明人群类型（ITT/PP/Safety）+纳排标准+样本量。

主要分析采用[方法]，比较[组间差异]，调整[协变量]。
  ↓ 示例: "主要分析采用Cox比例风险回归模型，比较两组生存时间差异，调整年龄、性别和基线BMI。"
效应量以[指标]及其95%置信区间表示。
  ↓ 示例: "效应量以风险比（HR）及其95%置信区间表示。"

样本量计算基于[参数]，检测[效应量]（SD=[值], Power=[%], α=[值]），
考虑[失访率]%脱落率，每组需要[n]例。
  ↓ 示例: "样本量计算基于主要终点（全因死亡率），检测HR=0.75（SD由基线数据估计），Power=90%, α=0.05（双侧），考虑15%脱落率，每组需要280例。"

所有分析遵循[ITT/PP]原则。缺失数据采用[方法]处理。
  ↓ 示例: "所有分析遵循ITT原则。缺失数据采用多重插补法（MICE, m=20次）处理。"
[敏感性分析描述]。
  ↓ 示例: "敏感性分析包括：PP分析、完整病例分析、以及排除违背方案受试者后的分析。"

[多重比较校正方法，如适用]。
  ↓ 示例: "次要终点采用Benjamini-Hochberg法控制错误发现率。" 或 "不适用（仅一个主要终点）。"

p<0.05认为有统计学意义。所有分析使用[R v4.x / Python v3.x]完成。
  ↓ 示例: "p<0.05认为有统计学意义。所有分析使用 R v4.3.2 完成。"
```

**方法学描述异常处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 使用了非标准或自定义统计方法 | 搜索文献提供方法引用和简短原理说明 | 引用原始方法学论文，在方法学描述中标注"替代方法"，提供三个选项：(1) 保留并引用 (2) 改用标准方法 (3) 移至补充材料 |
| 缺失关键方法细节（如软件版本、随机种子） | 从分析代码或 sessionInfo 中补全 | 标注"信息不可得"，转存到补充材料，提供信息收集模板 |
| 方法描述与报告规范模板冲突（如 STROBE 不要求样本量计算项） | 按规范模板组织，将冲突项移到补充材料 | 保留在正文但标注"非规范要求项"，提供规范要求对照表 |

**方法学描述检查点**：

> 🔴 [MANDATORY-REPT-03] 方法学描述完成后，必须展示以下内容给用户确认：
> 1. 方法学描述段落（软件版本、分析人群、主要方法、效应量）
> 2. 与SAP的一致性检查结果
> 3. 缺失数据处理方法说明
>
> 用户确认后才能进入合规检查。

### Phase 5: 一致性校验（精简版）

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

### Phase 6: 报告组装 (HTML 图文报告)

> 参考：shared/report_assembler/render_report_html.py — HTML 报告渲染器

将 Phase 1–5 的产物组装为一份单文件自包含的 HTML 图文报告。

**Step 6.1: AI 构建 JSON 骨架**

收集各阶段产物，构造 JSON 骨架 (`report_sections.json`)：

| 来源 | 产物 | JSON 章节类型 |
|------|------|--------------|
| Phase 1 | 结果解读文本 | `{"type": "text"}` |
| Phase 2 | 表格 (Markdown Table) | `{"type": "table"}` |
| Phase 3 | 已生成的 SVG+PNG | `{"type": "figure", "figure_file": "...", "figure_file_svg": "..."}` |
| Phase 4 | 方法学描述 | `{"type": "text"}` |
| Phase 5 | 合规检查结果 | `{"type": "checklist"}` |

JSON 骨架格式（`report_sections.json`）：

```json
{
  "title": "...", "study_type": "RCT",
  "sections": [
    {"id": "methods", "type": "text", "content": "..."},
    {"id": "table1", "type": "table", "content": "| 变量 | ... |"},
    {"id": "km_curve", "type": "figure", "figure_file": "km_curve.png", "caption": "..."},
    {"id": "compliance", "type": "checklist", "items": [{"passed": true, "label": "..."}]}
  ]
}
```

> section type: `text` | `table` | `figure`(需 figure_file+caption) | `checklist`(需 items[]) | `multi`(需 children[])

**Step 6.2: 调用渲染器生成 HTML**

```bash
# 完整 API 见 shared/report_assembler/render_report_html.py
python shared/report_assembler/render_report_html.py \
  --title "报告标题" \
  --sections reports/report_sections.json \
  --figures reports/figures/ \
  --output reports/final_report.html \
  --css-theme minimal
```

> 渲染失败时自动降级为 Markdown 拼接：将 JSON 骨架中各 section 按序拼接为 `final_report.md`。

**Step 6.3: 输出产物**

`final_report.html` + `final_report.md` + `figures/*.png` + `tables/*.docx` + `journal-template.json`

**报告组装异常处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| JSON 骨架缺少必需章节（如 "methods" 未生成） | 检查缺失章节来源阶段是否完成 | 在骨架中补充空章节占位，标注"待补充"，生成缺失章节清单和补充指南 |
| 渲染脚本 `render_report_html.py` 不存在或报错 | 检查路径和依赖（python-docx / jinja2） | 用 Markdown 直接拼接替代 HTML 渲染，输出纯文本版，提供渲染错误日志和修复建议 |
| 产物路径冲突（png/docx 同名列） | 自动追加时间戳后缀（如 `table1_baseline_1600.docx`） | 提示用户选择：(1) 覆盖现有文件 (2) 重命名新文件 (3) 保留两个版本 |

**报告组装检查点**：

> 🔴 [MANDATORY-REPT-04] 报告组装完成后，必须展示以下内容给用户确认：
> 1. 最终报告文件路径（HTML + MD）
> 2. 图表文件清单
> 3. 表格文件清单
> 4. 合规检查最终结果
>
> 用户确认后才能交付最终报告。

## 检查点量化标准

| 检查点 | 类型 | 通过标准 | 阻断标准 | 降级策略 |
|--------|------|---------|---------|---------|
| Phase 2 变量命名 | 自动 | V-R01~R07全通过 | 任何V-R违规 | 自动修正→重新检查 |
| Phase 2 P值格式 | 自动 | P-R01~R07全通过 | 任何P=0.000 | 自动格式化→重新检查 |
| Phase 5 statcheck | 自动 | 统计结果一致 | P值/CI/效应量不一致 | 标记[STATCHECK_FAILED]→退回Phase 2 |
| Phase 5d 约束检查 | 阻断 | P-R/M-R/D-R/S-R全通过 | 任何约束违规 | 修复→重新检查(最多3次) |
| Phase 5e 图表质量 | 阻断 | SVG+PNG 300dpi双格式 | 格式/分辨率不达标 | 重新生成→重新检查 |
| Phase 6 报告组装 | 自动 | HTML渲染成功 | HTML渲染失败 | 降级为Markdown[HTML_FALLBACK] |

> **修复上限**: Phase 5d/5e最多修复3次，超过3次标记[QUALITY_DEGRADED]并继续
> **阻断规则**: Phase 5d的P-R01和M-R01为硬阻断项，不可降级

## 故障处理与降级策略

| 触发条件 | 降级策略 | 标记 | 后续操作 |
|---------|---------|------|---------|
| statcheck API 不可用 | 跳过自动验证，人工复核 | 报告标注 [STATCHECK_SKIPPED] | 在报告"统计验证"章节添加说明："自动统计验证未执行，需作者手动核对所有P值和置信区间"，并提供核对清单模板 |
| 图表生成失败（matplotlib/seaborn 报错） | 降级为纯表格报告 | 报告标注 [FIGURE_ERROR] | 生成包含所有数据点的详细表格，附带图表代码文件（.py/.R），用户可自行执行生成图表 |
| CONSORT/STROBE checklist 文件缺失 | 使用内嵌迷你清单（10项核心条目） | 报告标注 [CHECKLIST_DEGRADED] | 提供两个选项：(1) 使用精简清单继续，(2) 暂停等待用户提供完整清单文件 |
| HTML 渲染失败 | 降级为 Markdown 报告 | 报告标注 [HTML_FALLBACK] | 输出 final_report.md，同时生成渲染错误日志文件（render_error.log），包含具体错误信息和修复建议 |

> 所有降级标记（[STATCHECK_SKIPPED] / [FIGURE_ERROR] / [CHECKLIST_DEGRADED] / [HTML_FALLBACK]）必须在最终报告显著位置标注，不得静默降级。

## 命令

| 命令 | 说明 |
|------|------|
| `/msra-report` | 启动报告生成流程（统计报告 + Stage 4 checkpoint） |
| `/msra-report --type table1` | 仅生成Table 1 |
| `/msra-report --type figure` | 仅生成图表 |
| `/msra-report --type methods` | 仅生成方法学描述 |
| `/msra-report --output html` | 指定输出格式 (html / md) |
| `/msra-report CONSORT` | ⚠️ 已移至 Paper Track Stage 5.0（仅写论文时选择规范） |
| `/msra-report --template NEJM` | ⚠️ 已移至 Paper Track Stage 5.0（仅写论文时选择期刊模板） |

## Mode

### guided（默认）
完整流程：结果解读 → 表格 → 图表 → 方法学 → 统计质量检查 → 报告组装 → ★ Stage 4 Checkpoint [A]/[B]
输出: final_report.html + final_report.md + figures/*.png + tables/*.docx

### quick
通过 `--type` 参数快速生成指定元素（单个表格/图表/段落），跳过其他 Phase。

---

## 反例与黑名单

> **以下行为必须避免**。违反任何一条将导致报告质量不可靠或误导读者。
> 本节覆盖**统计报告模式**和**论文写作模式**的所有反模式。论文特定反模式见下方"论文写作反例与黑名单"。
> 完整医学统计反模式目录参见：shared/anti-patterns/medical_stats_anti_patterns.md（D1/D2/D3/A5）

### 🚫 统计解读禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 仅凭 p<0.05 宣称"有显著差异"而不报告效应量和置信区间 | p 值不反映效应大小和临床意义；大样本下微小差异也可"显著" | 必须同时报告效应量 + 95% CI + 精确 p 值 |
| 2 | p>0.05 时宣称"无差异"或"两组相同" | 不能证明零假设，可能是检验效能不足 | 写"未检测到统计学显著差异"，讨论检验效能和 CI |
| 3 | 对同一数据多次检验但不做多重比较校正 | 总 I 类错误率膨胀，假阳性风险增加 | Bonferroni、Hochberg 或 SAP 中预定义的层次检验 |
| 4 | 将相关性解释为因果关系（观察性研究） | 混杂和反向因果无法排除 | 使用"关联"而非"导致"，讨论混杂控制 |
| 5 | 选择性报告结果（只报告"阳性"结果） | 报告偏倚，夸大疗效 | 报告所有预定义终点，包括阴性结果 |

### 🚫 表格/图表禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 6 | 表格中用 * 号标记 p 值而不给精确值 | 精确 p 值是学术出版标准要求 | 报告精确 p 值（如 p=0.037），可附加星号 |
| 7 | 图表坐标轴截断以夸大差异 | 误导读者对效应量的判断 | 坐标轴从 0 或合理起点开始，标注截断 |
| 8 | 生存曲线在删失点处突然下降 | KM 曲线应在删失点做标记，不应下降 | 用 `+` 或 `|` 标记删失，阶梯函数仅在事件处下降 |
| 9 | 森林图中不标注异质性检验结果 | 读者无法判断合并是否合理 | 报告 I² 和 Q 检验 p 值 |

### 🚫 方法学描述禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 10 | 写"使用适当的统计方法"而不具体说明 | 不可复现，审稿人无法判断方法是否正确 | 写明具体方法名称、参数、软件版本 |
| 11 | 遗漏分析人群定义（ITT/PP/Safety） | 不同人群结论可能不同 | 明确每种分析使用的人群定义 |
| 12 | 不说明缺失数据处理方法 | 缺失数据处理不同可能导致结论不同 | 说明缺失机制假设和处理方法（如 MICE） |

### 🚫 流程禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 13 | 跳过结果解读直接生成表格（guided 模式） | 表格脱离临床语境，读者无法理解含义 | guided 模式下 Phase 1 解读必须先于 Phase 2/3；`--type` 参数指定的 quick 模式除外 |
| 14 | 合规检查不通过仍生成最终报告 | 不合规报告无法通过伦理审查和期刊审稿 | [MANDATORY-GATE-04] 合规检查不通过 → 修正 → 重新检查 → 通过后才输出 |

### 🚫 statcheck 与数值一致性禁忌 🆕

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 15 | statcheck 发现的 ❌❌ 不一致静默修正不记录 | 静默修正掩盖根源问题，同一类错误会持续出现 | 每次不一致必须记录原始值→修正值→差异原因，记入偏差日志 |
| 16 | 多个统计量同为不一致但只修部分 | 选择性修正会歪曲结果报告完整性 | 所有不一致项必须全部核实并修正，不能跳过解读复杂的项目 |
| 17 | statcheck 不通但跳过统计方法学段落的交叉验证 | 方法学段落的 t/F/χ² 陈述若与实际分析不符，同样属于数值不一致 | statcheck 的范围必须覆盖 Phase 1（结果解读）+ Phase 2（表格）+ Phase 4（方法学），缺一不可 |

### 🚫 报告组装禁忌 🆕

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 18 | JSON 骨架中 figure 的 figure_file 指向不存在文件 | 最终报告中产生坏图，读者无法查看 | Step 6.1 组装前验证所有 figure_file 路径是否可达；不可达则跳过该 figure，在章节中标注"[图表暂不可用]" |
| 19 | 多类型图表使用相同文件名 | Phase 6 输出路径冲突导致旧图覆盖新图 | 文件名必须区分图类型和内容（如 `figure1_km_curve.png` vs `figure2_forest.png`），违者自动追加时间戳 |
| 20 | 报告组装后不验证交叉引用完整性 | 报告中可能出现"如图X所示"但图X不存在的孤引用 | assembly 完成后必须扫描 HTML/MD 全文，验证所有 "图N"/"表N"/"Figure N"/"Table N" 引用与实际生成的图表清单一一对应 |

---

## ★ STAGE 4 CHECKPOINT（MANDATORY-GATE-04'，Pipeline 决策节点）

> **前置条件**：Phase 6 报告组装完成。产物：final_report.md + final_report.html + figures/*.png + tables/*.docx。
> **作用**：Stage 4 的结束点，决定用户走 Report-Only 还是 Full-Paper 轨道。

**守卫检查（Paper Track 入口前置）**：
- ✅ passport stage_4 status == completed
- ✅ final_report.md 存在
- ✅ 至少 1 张 figure + 至少 1 张 table（缺失仅警告，不阻断）

```
── ★ STAGE 4 CHECKPOINT ──
统计报告已完成。

产物清单：
  • final_report.md
  • final_report.html
  • figures/*.png（已确认）
  • tables/*.docx（已确认）

选择下一步：
  [A] 统计报告完成，结束                        → track = report_only, pipeline 结束
  [B] 继续写论文 → Paper Track (Stage 5.0)     → track = full_paper, 进入 Stage 5.0

输入 A 或 B:
```

**决策逻辑**：
- 选 **[A]** → `passport.set_track("report_only")`，pipeline 正常结束，输出统计报告
- 选 **[B]** → 守卫检查通过后 `passport.set_track("full_paper")`，进入下方 **§论文写作模式**（Stage 5 Paper Track）
- 守卫检查失败 → 提示用户补全缺失产物，不进入 Paper Track

---

# 论文写作模式（原 medical-paper）

> 以下内容合并自 medical-paper skill。本 skill 为双模式：统计报告（上方 §Phase 0-6）+ 论文写作（本节）。
> 论文写作模式由 Pipeline Stage 4 CHECKPOINT [B] 触发，或用户直接调用。

## 双模式架构

```
用户请求
    │
    ├─ "生成统计报告" / "Table 1" / "图表" → 统计报告模式 (§Phase 0-6)
    │
    └─ "写论文" / "paper" / "manuscript" → 论文写作模式 (本节)
         │
         ├─ 从零开始 → Paper Phase 0-7 完整流程
         ├─ 已有论文 → Revision / Revision-Coach 模式
         └─ 仅需摘要/引用/格式 → Abstract / Citation-Check / Format-Convert 模式
```

## 论文写作 Agent Team（12 Agents）

| # | Agent | Role | Paper Phase |
|---|-------|------|-------------|
| 1 | `paper_config_agent` | 配置访谈：论文类型、学科、引用格式、输出格式、语言 | Paper Phase 0 |
| 2 | `literature_search_agent` | 检索策略设计、来源筛选、注释书目 | Paper Phase 1 |
| 3 | `paper_outline_agent` | 论文结构选择、详细大纲、字数分配 | Paper Phase 2 |
| 4 | `evidence_chain_agent` | 论证构建、claim-evidence 链、逻辑流 | Paper Phase 3 |
| 5 | `manuscript_drafter` | 逐节全文草稿、学科语域调整 | Paper Phase 4 |
| 6 | `reference_checker` | 引用格式验证、参考文献完整性、DOI 检查 | Paper Phase 5a |
| 7 | `bilingual_abstract_agent` | 双语摘要（中+英）、各 5-7 关键词 | Paper Phase 5b |
| 8 | `mock_reviewer` | 模拟双盲审稿、五维评分、修改建议（最多 2 轮） | Paper Phase 6 |
| 9 | `output_formatter` | 转换为 LaTeX/DOCX/PDF/Markdown、期刊格式化 | Paper Phase 7 |
| 10 | `writing_mentor` | Plan 模式苏格拉底导师：逐章引导 | Plan Step 0-3 |
| 11 | `figure_generator` | 生成出版级图表代码（matplotlib/ggplot2） | Paper Phase 4/7 |
| 12 | `revision_planner` | 解析非结构化审稿意见 → 结构化 Revision Roadmap | Revision-Coach |

## 论文写作 Operational Modes（11 Modes）

| Mode | Trigger | Agents | Output |
|------|---------|--------|--------|
| `full` | "Write a paper" | All 12 | Complete paper draft |
| `plan` | "guide my paper" | 1→10→3→4 | Chapter Plan + INSIGHT |
| `outline-only` | "Paper outline" | 1→2→3 | Detailed outline + evidence map |
| `revision` | "Revise paper" | 8→5→6 | Revised draft + Response to Reviewers |
| `revision-coach` | "parse reviews" | 12 only | Revision Roadmap |
| `abstract-only` | "Write abstract" | 1→7 | Bilingual abstract + keywords |
| `lit-review` | "Literature review" | 1→2 | Annotated bibliography + synthesis |
| `format-convert` | "Convert to LaTeX" | 9 only | Formatted document |
| `citation-check` | "Check citations" | 6 only | Citation error report |
| `disclosure` | "AI disclosure" | 9 only | AI-usage disclosure paragraph |
| `rebuttal-audit` | "audit my response" | 12 only | Rebuttal QA report |

### Quick Mode Selection Guide

| 情况 | 推荐 Mode | 说明 |
|------|----------|------|
| 从零开始有明确 RQ | `full` | 完整 8 阶段流程 |
| 需要先规划再写 | `plan` | 苏格拉底引导 |
| 只要大纲 | `outline-only` | 仅 Phase 1-3 |
| 有论文收到审稿意见 | `revision` | 解析 + 修改 |
| 有非结构化审稿意见 | `revision-coach` | 结构化 Roadmap |
| 只要摘要 | `abstract-only` | 双语摘要 |
| 要检查引用 | `citation-check` | 引用合规 |
| 要转换格式 | `format-convert` | LaTeX/DOCX/PDF |
| 要文献综述 | `lit-review` | 注释书目 |
| 要 AI 使用声明 | `disclosure` | 期刊特定声明 |
| 有回复草稿要 QA | `rebuttal-audit` | 覆盖检查 |

## 论文写作 8 Phase 工作流

```
Paper Phase 0: CONFIG        → [paper_config_agent]              → Paper Configuration Record
Paper Phase 1: RESEARCH      → [literature_strategist]      → Search Strategy + Source Corpus
Paper Phase 2: ARCHITECTURE  → [structure_architect]        → Paper Outline + Evidence Map
Paper Phase 3: ARGUMENTATION → [argument_builder]           → Argument Blueprint
Paper Phase 4: DRAFTING      → [draft_writer]               → Complete Draft
Paper Phase 5a: CITATIONS    → [citation_compliance] ──┐    → Citation Audit Report
Paper Phase 5b: ABSTRACT     → [abstract_bilingual]   ─┘    → Bilingual Abstract (parallel)
Paper Phase 6: PEER REVIEW   → [peer_reviewer]              → Review Report (max 2 loops)
Paper Phase 7: FORMAT        → [formatter]                  → Final Output Package
```

### Checkpoint Rules

1. **IRON RULE**: 用户必须确认 Paper Configuration Record 后才能进入 Paper Phase 1
2. **Paper Phase 2 → 3**: 用户必须批准大纲（可要求重组）
3. **IRON RULE**: 最多 2 轮修改；未解决项 → "Acknowledged Limitations"
4. **Peer Review** Critical-severity 问题阻断进入 Paper Phase 7
5. 用户可跳过 Paper Phase 1（如有自有来源）

## 引用格式支持

APA 7.0（默认）、Chicago（Author-Date 或 Notes-Bibliography）、MLA 9、IEEE、Vancouver。
`output_formatter` 支持后期引用格式转换："Convert citations to [format]"。

## 输出格式

- **文本**: LaTeX (.tex + .bib), DOCX (via Pandoc), PDF, Markdown
- **图表**: Python matplotlib / R ggplot2，APA 7.0 格式，色盲安全调色板
- **引用**: 5 种格式互转

## Style Calibration（可选）

用户提供 3+ 篇过往论文，pipeline 学习其写作风格（句式节奏、词汇偏好、引用整合风格）。
作为草稿阶段的软指南应用；学科规范始终优先。参见 `shared/style_calibration_protocol.md`。

## Writing Quality Check

草稿自审步骤中应用的写作质量检查清单：
- 检测过度使用的 AI 典型术语
- 检查破折号过度使用
- 移除 throat-clearing openers
- 检查段落长度均匀性
- 检查句式单调性

## Generator-Evaluator Contract Protocol (v3.6.6)

> 仅适用于 `full` 模式。将 Paper Phase 4（写作）和 Paper Phase 6（审稿）拆分为 paper-blind / paper-visible 调用对。

**四调用结构**：
1. **Paper Phase 4a** — Writer paper-blind pre-commitment（仅看合同+元数据）
2. **Paper Phase 4b** — Writer paper-visible drafting + self-scoring（写全文+自评）
3. **Paper Phase 6a** — Evaluator paper-blind pre-commitment（仅看合同+元数据+4a 输出）
4. **Paper Phase 6b** — Evaluator paper-visible scoring + decision（评分+决策）

**核心机制**：物理分离调用——4a 永远看不到运行时草稿，6a 永远看不到 4b 草稿。这消除了"先读论文再合理化标准"的漂移路径。

### Unusable Handling

Writer/evaluator phase 两次 lint 失败 → `[GENERATOR-PHASE-ABORTED]` → 用户介入决定重试/回退/降级。

## 论文写作反例与黑名单

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 不做配置访谈直接写论文 | 论文类型/学科/引用格式不确定会导致返工 | Phase 0 配置访谈必须完成 |
| 2 | 引用不验证直接使用 | 可能引用不存在的文献 | 每个引用必须通过 DOI 或 WebSearch 验证 |
| 3 | 超过 2 轮修改仍继续 | 进入无限修改循环 | 最多 2 轮，剩余项归入 "Acknowledged Limitations" |
| 4 | 模拟审稿人互相参考 | 破坏独立性 | 5 位审稿人独立审阅，不交叉引用 |
| 5 | Peer Review 修改论文原稿 | 审稿人只评审不修改 | 所有审稿输出为独立文档 |
| 6 | Paper Phase 6a/6b 混淆 system prompt 和 user content | 动态 LLM 输出不应进入不变策略面 | system prompt 仅含不变策略，动态内容在 user content 中 |
| 7 | 在非 full 模式调用 Generator-Evaluator 合同 | 仅 full 模式适用 | 9 个非 full 模式不触发此协议 |
| 8 | 跳过 Style Calibration 直接使用默认风格 | 可能不符合用户写作习惯 | 可选但推荐，提供 3+ 篇过往论文 |

---

## 论文写作引用与集成

| 集成方向 | 描述 |
|---------|------|
| **上游: systematic-survey → report** | Stage 5.1 文献检索提供研究基础 |
| **上游: report 统计模式 → 论文模式** | Stage 4 CHECKPOINT [B] 提供 final_report + figures + tables |
| **下游: report → peer-review** | Stage 5.4 审稿，Revision Roadmap 可直接用作修改输入 |
| **下游: report → pipeline** | 通过 passport 状态追踪，pipeline 编排 Paper Track 全流程 |



