---
version: "0.7.5"
name: MSRA Report Generation
description: |
  生成符合医学报告规范（CONSORT/STROBE/PRISMA等）的出版级表格、
  图表和方法学描述。同时提供研究设计咨询服务。
  触发: 报告 / 生成报告 / 表格 / 图表 / CONSORT / STROBE / PRISMA / 方法学 / 统计报告 / 合规检查 / 三线表 / 最终报告 / report / table / figure / manuscript
data_access_level: verified_only
task_type: open-ended
depends_on: [analysis-exec]
works_with: [analysis-exec, analysis-plan, pipeline]
author: "MSRA Team"
license: "MIT"
min_claude_version: "3.5"
tags: [medical-statistics, clinical-trial, report, CONSORT, STROBE, publication]
---

# 报告生成 (Report Generation)

## 角色定义

你是一位医学写作和生物统计学专家，负责将分析结果转化为符合国际报告规范的出版级材料。

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
> - 参考：shared/templates/publication_figure_template.py — 发表级图表 Python 模板

## 报告生成流程图

```
分析结果 (JSON/CSV)
    │
    ▼
Phase 0: 输入验证 ─── 结果文件完整？─── 否 → 报错退出
    │ 是
    ▼
Phase 1: 结果解析 ─── 提取效应量/P值/CI
    │
    ▼
Phase 2: 报告框架 ─── 按研究类型选择模板
    │ RCT→CONSORT | 观察性→STROBE | 诊断→STARD
    ▼
Phase 3: 内容生成 ─── 变量命名规范化 + P值格式化
    │ V-R01~R07 + P-R01~R07
    ▼
Phase 4: 图表生成 ─── 发表级图表(SVG+PNG, 300dpi)
    │ apply_publication_style()
    ▼
Phase 5: statcheck ── 统计结果验证
    │ 通过 → 继续 | 失败 → 标记[STATCHECK_FAILED]
    ▼
Phase 6: 合规检查 ─── 6d约束检查 + 6e图表质量
    │ 全通过 → 继续 | 违规 → 修复→重新检查
    ▼
Phase 7: 报告组装 ─── HTML + MD + DOCX
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
│  │           Phase 0-2: 解析+框架选择            │    │
│  │     RCT→CONSORT | 观察性→STROBE | 诊断→STARD  │    │
│  └─────────────────────┬───────────────────────┘    │
│                        ▼                             │
│  ┌─────────────────────────────────────────────┐    │
│  │     Phase 3: 内容生成 (变量命名+P值格式化)    │    │
│  │     V-R01~R07 + P-R01~R07 规则引擎           │    │
│  └─────────────────────┬───────────────────────┘    │
│                        ▼                             │
│  ┌─────────────────────────────────────────────┐    │
│  │     Phase 4: 发表级图表 (publication_style)  │    │
│  │     SVG(主) + PNG(300dpi, 备用)              │    │
│  └─────────────────────┬───────────────────────┘    │
│                        ▼                             │
│  ┌─────────────────────────────────────────────┐    │
│  │  Phase 5-6: statcheck + 合规检查(6d+6e)      │    │
│  └─────────────────────┬───────────────────────┘    │
│                        ▼                             │
│  ┌─────────────────────────────────────────────┐    │
│  │        Phase 7: HTML报告组装                  │    │
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
推荐统一为: age（代码名）/ 年龄（中文显示名）/ Age（英文显示名）
```

### 3. 报告生成快速路径

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
| P值格式化遗漏 | 表格中出现P=0.000 | Phase 3强制执行P-R01~R07，用正则扫描所有P值 |
| 变量名不一致 | 同一变量出现多种写法 | Phase 3加载variable_dictionary.yaml，自动替换 |
| SVG文件过大 | >1MB导致加载缓慢 | 压缩SVG(remove metadata)+提供PNG fallback |
| statcheck超时 | >60秒无响应 | 降级为[STATCHECK_SKIPPED]，推荐手动核查 |
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

> Phase 编号保留历史序号（原 Phase 2/2.5 已移至 Paper Track Stage 5.0）。
> 实际执行顺序: Phase 0(交互) → Phase 1 → 3 → 3.5 → 4 → 5 → 6(精简) → 7 → 8 → ★Checkpoint

```
Phase 0: 结果解读会话 → 输入:analysis_results+quality_check → 输出:interpretation_priorities.md
  │ 🔴 [MANDATORY] 交互式会话，确认结果优先级
  ▼
Phase 1: 结果解读 → 输入:分析结果+SAP+priorities → 输出:解读文档
  │ [SLIM-S4] 异常发现自动升级为 ADAPTIVE
  ▼
Phase 3: 生成表格 → 输入:解读文档+分析结果 → 输出:Markdown表格
  │ [SLIM]
  ▼
Phase 3.5: 表格导出 → 输入:Markdown表格 → 输出:*.docx三线表
  ▼
Phase 4: 生成图表 → 输入:分析结果 → 输出:figures/*.png
  ▼
Phase 5: 方法学描述 → 输入:分析结果 → 输出:统计段落
  ▼
Phase 6: 统计质量检查（精简版）→ statcheck + anti-patterns + 统计维度 quality_checklist
  │ 🔴 [MANDATORY-M4] 🛑 STOP 必须用户确认
  ▼
Phase 7: 报告组装 → 输入:JSON骨架+图表 → 输出:HTML+MD
  ▼
最终报告 (final_report.md + final_report.html + figures/*.png + tables/*.docx)
  │
  ▼
★ STAGE 4 CHECKPOINT (MANDATORY-M4')
  [A] 统计报告完成，结束 → track = report_only
  [B] 继续写论文 → Paper Track (Stage 5.0, 见 pipeline/SKILL.md §Stage 5)
```

### Phase 0: 结果解读会话（Interactive Interpretation）🆕

> 目的：在正式报告撰写前，让用户聚焦关键发现，确定报告的叙述重点。

**输入**：analysis_results + quality_check

**执行流程**：

1. **系统展示分析结果摘要**：
   - 主要终点：效应量 + p值 + 95% CI
   - 次要终点：显著性列表
   - 安全性信号：AE/SAE 摘要
   - 异常发现：与预期不符的结果

2. **用户交互**：
   - "哪些发现你认为是最重要的？" → 记录为报告核心重点
   - "哪些结果需要进一步探索？" → 触发额外分析请求
   - "哪些结果可能需要谨慎解读？" → 标记为报告中的注意事项

3. **输出**：`interpretation_priorities.md`（用户确认的结果优先级）

**Checkpoint**：
- 🔴 [MANDATORY] 必须确认结果优先级后才进入 Phase 1
- 不修改任何分析结果，仅调整报告的关注重点和叙述框架

**产物记录**：`interpretation_priorities` 记入 passport artifacts

---

### Phase 1: 结果解读

在生成表格和图表之前，先对分析结果进行系统解读。

**两阶段生成策略**（借鉴 YH-SAP MultiStepGenerator）：
1. **Step 1 (提取)**: 从分析输出中提取关键数字 — p值、效应量、95% CI、样本量、组间差异
2. **Step 2 (生成)**: 基于提取的结构化事实，生成正式的结果解读文本

> Step 1 确保数字准确性，Step 2 确保解读深度。分离"提取"和"创作"两个认知任务。

**解读框架**：

> 参考：shared/statistics-methods/methods_catalog.md — 效应量解读和统计方法描述
> 参考：shared/statistics-methods/chapters/ch07-minimal-clinically-important-difference.md — MCID临床意义解读 (统计指南第7章)
> 参考：shared/statistics-methods/chapters/ch17-number-needed-to-treat.md — NNT解读 (统计指南第17章)

**1. 统计显著性 vs 临床意义**
- p值是否达到统计显著性？
- 效应量是否有临床意义？（即使p<0.05，效应量很小时需谨慎解读）
- 置信区间是否排除了临床无关的效应？

**效应量临床意义速查表**（借鉴 BioMedStatX）：

| 效应量 | 小 | 中 | 大 | 临床解读 |
|--------|-----|-----|-----|---------|
| Cohen's d | 0.2 | 0.5 | 0.8 | 组间标准化差异 |
| OR | 1.5 | 2.5 | 4.0 | 优势比（远离1） |
| HR | 0.75/1.33 | 0.67/1.5 | 0.5/2.0 | 风险比 |
| eta-squared | 0.01 | 0.06 | 0.14 | 方差解释比例 |

**2. 效应量解释**
| 指标 | 解释方式 | 示例 |
|------|---------|------|
| 均值差 (MD) | 组间绝对差异 | "治疗组收缩压平均降低 12.3 mmHg" |
| OR | 暴露与结局的关联强度 | "吸烟者肺癌风险是非吸烟者的 2.5 倍" |
| HR | 风险随时间的变化 | "治疗组死亡风险降低 25%" |
| IRR | 发生率比 | "干预组事件发生率降低 30%" |
| AUC | 区分能力 | "模型的区分度为 0.85（良好）" |

**3. 局限性讨论**
- 残余混杂（未测量的混杂因素）
- 测量误差（暴露/结局的测量准确性）
- 选择偏倚（失访、纳入排除标准）
- 信息偏倚（回忆偏倚、报告偏倚）
- 样本量不足（检验效能不够）
- 外推性（结果能否推广到其他人群）

**4. 与已有文献对比**
- 主要发现是否与既往研究一致？
- 如果不一致，可能的原因是什么？
- 本研究的新贡献是什么？

**输出**: 结构化的结果解读文档，作为后续报告撰写的基础

> [SLIM-S4] 结果解读完成后：展示关键发现摘要给用户确认。如发现效应方向异常或临床意义存疑，自动升级为 ADAPTIVE 需讨论。

**如果解读发现异常**：
| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 效应量方向与预期相反 | 检查数据编码和模型设定是否正确 | 标记为"意外发现"，在局限性中讨论 |
| p值边界结果（0.04-0.06） | 报告精确p值+CI，讨论临床意义而非仅依赖阈值 | 提示增加样本量或进行敏感性分析 |
| 主要终点阴性但次要终点阳性 | 警告不要将次要终点重新定义为主要终点 | 在局限性中如实报告，标记为"需验证性研究确认" |

### Phase 2: ~~确定报告规范~~ → 移至 Paper Track Stage 5.0

> 报告规范选择（CONSORT/STROBE/STARD...）已移至 Stage 5.0 Paper Intake（仅写论文时需要）。
> 统计报告阶段不强制全文规范合规，仅需 Phase 6 的统计质量检查。

### Phase 2.5: ~~选择输出模板~~ → 移至 Paper Track Stage 5.0

> 期刊模板选择（NEJM/JAMA/...）已移至 Stage 5.0 Paper Intake（仅写论文时需要）。

### Phase 3: 生成表格

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

> 🔴 [MANDATORY-S3] 表格生成完成后，必须展示以下内容给用户确认：
> 1. Table 1 基线特征表（样本量、缺失率、关键变量）
> 2. 主分析结果表（效应量、95%CI、p值）
> 3. 与 Phase 1 提取数字的一致性检查结果
>
> 用户确认后才能进入图表生成。

**表格生成异常处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 变量无组间差异（所有 p 值 > 0.9） | 检查样本量和效应量差异是否临床有意义 | 如实报告 null 结果，标注"未发现统计学显著差异" |
| 分类变量有频率为 0 的空水平 | 合并空水平到相邻类别或标记为"无观察" | 删除空行，在脚注中说明 |
| 连续变量标准差为 0（所有值相同） | 检查数据是否录入错误或常量变量 | 排除该变量，在脚注中说明排除原因 |
| Phase 1 提取数字与表格计算不一致 | 重新计算，定位差异来源（四舍五入/截断差异） | 以表格计算结果为准，在脚注标注差异来源 |
| 表格列数过多（>15 列）导致可读性差 | 拆分为子表（基线/结果/亚组分表） | 输出横向页面表格，标注"续表" |
| 混合类型列（数值+文本混排）无法渲染 | 分裂为两列（数值列+注释列） | 标记为"格式待整理"，在脚注中说明原因 |

### Phase 3.5: 表格导出 (三线表 → docx)

> 参考：shared/report-assembler/export_tables_docx.py — Word 三线表导出器
> R 版本参考：shared/templates/export_tables_flextable.R

将 Phase 3 生成的表格（基线特征表、回归结果表等）导出为符合医学期刊格式的 `.docx` 三线表。

**三线表规范**：
- 顶线粗 (2pt)、表头下线中 (1pt)、底线粗 (2pt)
- 无竖线、无左右端线
- 表题在上方居中，表注在下方
- 第一列左对齐，其余居中

**Step 3.5.1: 确定需要导出的表格**

| 表格 | 默认文件名 | 说明 |
|------|-----------|------|
| Table 1 基线特征 | `table1_baseline.docx` | 按分组展示基线特征 |
| 主分析结果表 | `table2_main_results.docx` | 回归分析 (OR/HR/β 及其 95%CI) |
| 敏感性分析表 | `table3_sensitivity.docx` | 敏感性分析结果 |
| 亚组分析表 | `table4_subgroup.docx` | 亚组分析结果 |

**Step 3.5.2: 调用导出脚本**

```bash
# Python 版 (首推)
python shared/report-assembler/export_tables_docx.py \
  --input-md "| 变量 | OR | 95% CI | p |\n|---|...|" \
  --output reports/tables/table2_regression.docx \
  --title "表2 Logistic回归结果" \
  --note "OR: 比值比; CI: 置信区间"

# R flextable 版 (备选, 需 R + flextable)
Rscript shared/templates/export_tables_flextable.R
```

> 完整代码示例（含自定义样式、中文字体处理）见 `shared/report-assembler/export_tables_docx.py` 和 `shared/templates/export_tables_flextable.R`。

**Step 3.5.3: 异常处理**

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| python-docx 未安装 | `pip install python-docx` 后重试 | 输出 CSV + 提示用户手动格式化 |
| 表格内容为空 | 跳过导出，记录日志 | 生成占位表格，标注"数据待补充" |
| 列数过多 (>10列) | 提示用户拆分表格或调整页面方向为横向 | 自动拆分为子表 (Table 2a, 2b) |
| 中文显示乱码 | 指定字体为 "SimSun" 或 "Microsoft YaHei" | 输出英文表头版本 |

> [SLIM] Checkpoint: 展示已导出的 docx 文件清单给用户确认。

### Phase 4: 生成图表

> 自动加载 shared/templates/ 中的 R/Python 模板，传入分析数据执行并保存。
> **发表级标准**：遵循 shared/chart-styles/publication_figure_standards.md
> **首选模板**：shared/templates/publication_figure_template.py（含 nature-figure 标准 rcParams、调色板、辅助函数）
> **变量命名**：遵循 shared/chart-styles/variable_naming_conventions.md（规范显示名+单位）
> **P值格式**：遵循 statistical_constraints.md P-R01~R07（P<0.001 展示为 "P < 0.001"）

**Step 4.1: 分析类型 → 图类型映射**

根据分析结果自动确定需要哪些图表：

| 分析类型 | 生成图表 | 首选模板（发表级） | 备选模板 |
|---------|---------|------------------|---------|
| 生存分析 (Cox/KM) | KM 曲线 + 森林图 (可选) | publication_figure_template.py (make_km_curve) | cox_template.py, survival_ggsurvfit.R |
| Logistic/回归 | 森林图 | publication_figure_template.py (make_forest_plot) | forest_plot_template.py |
| 诊断试验 (ROC) | ROC 曲线 | publication_figure_template.py (make_roc_curve) | roc_template.py, roc_visualization_template.R |
| 一致性检验 | Bland-Altman 图 | bland_altman_template.py | — |
| 预测模型 | 校准曲线 | publication_figure_template.py (make_calibration_curve) | calibration_plot_template.R |
| 基线特征 | Table 1 结构化图 | table1_template.R, gtsummary_template.R | janitor_tabyl_template.R |
| 相关性分析 | 相关性热图 | publication_figure_template.py (make_heatmap) | correlation_template.R |
| 连续变量分布 | 箱线图 | publication_figure_template.py (make_box_plot) | — |
| 分组比较 | 柱状图 | publication_figure_template.py (make_bar_chart) | — |
| 变量关系 | 散点图 | publication_figure_template.py (make_scatter_plot) | — |
| 非线性关系 | RCS 曲线 | publication_figure_template.py (make_rcs_plot) | — |

**Step 4.2: 加载模板**

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

**Step 4.3: 传入数据 → 执行 → 保存 SVG+PNG**

> 使用 publication_figure_template.py 时，自动应用发表级标准：
> - 三行强制 rcParams（font.family, svg.fonttype='none'）
> - 语义化调色板或期刊配色
> - SVG（首要）+ PNG 300dpi（预览）双格式导出
> - 变量名使用规范显示名+单位
> - P 值格式遵循 P-R01~R07

- 将实际分析结果（估计值、置信区间、p 值等）构造为模板所需的输入格式
- 执行模板代码，生成出版级图表
- 图片保存到 `reports/figures/{分析名}_{图类型}.svg`（矢量，首要）+ `.png`（300 DPI 预览）
- 记录执行方式和路径：`{图类型}: Python/R, saved to reports/figures/...`

```python
# Python 示例 — 使用发表级模板
import subprocess
result = subprocess.run(
    ["python", template_path, "--data", data_path, "--out", output_path,
     "--journal", "NEJM",  # 期刊配色
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

**Step 4.4: 调用模板生成图表**

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

**Step 4.5: 异常处理**

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| R/Python 包未安装 | 自动 pip install / install.packages 重试 (最多1次) | 描述性文本替代，标注"图表暂不可用" |
| 数据不足绘制完整图表 | 简化图表（减少分组/调整分类数） | 输出数据 + 代码供用户后续自行渲染 |
| 坐标轴/图例混乱 | 手动调整参数（limits/breaks/labels） | 用简单替代方案（如条形图代替箱线图） |
| 中文显示乱码 | 指定字体 'SimHei' 或 'Microsoft YaHei' | 使用英文标签 |
| 图像分辨率不足 | 设置 dpi=300 或更高 | 输出矢量图 (PDF/SVG) |

> [SLIM] Checkpoint: 图表生成后展示图片路径给用户确认，不满意可重新生成参数。

**图表生成检查点**：

> 🔴 [MANDATORY-S4] 图表生成完成后，必须展示以下内容给用户确认：
> 1. 图表文件路径和预览（如可能）
> 2. 图表类型和参数设置
> 3. 与分析结果的一致性检查
>
> 用户确认后才能进入方法学描述。

### Phase 5: 方法学描述

> 参考：shared/statistics-methods/methods_catalog.md — 统计方法描述模板
> 参考：shared/statistics-methods/REFERENCE.md — 统计方法描述的JAMA规范格式参考

**统计方法学段落模板**：

```
统计分析

[描述软件和版本]

[描述分析人群]

主要分析采用[方法]，比较[组间差异]，调整[协变量]。
效应量以[指标]及其95%置信区间表示。

样本量计算基于[参数]，检测[效应量]（SD=[值], Power=[%], α=[值]），
考虑[失访率]%脱落率，每组需要[n]例。

所有分析遵循[ITT/PP]原则。缺失数据采用[方法]处理。
[敏感性分析描述]。

[多重比较校正方法，如适用]。

p<0.05认为有统计学意义。所有分析使用[R v4.x / Python v3.x]完成。
```

**方法学描述异常处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 使用了非标准或自定义统计方法 | 搜索文献提供方法引用和简短原理说明 | 引用原始方法学论文，标注"替代方法" |
| 缺失关键方法细节（如软件版本、随机种子） | 从分析代码或 sessionInfo 中补全 | 标注"信息不可得"，转存到补充材料 |
| 方法描述与报告规范模板冲突（如 STROBE 不要求样本量计算项） | 按规范模板组织，将冲突项移到补充材料 | 保留在正文但标注"非规范要求项" |

**方法学描述检查点**：

> 🔴 [MANDATORY-S5] 方法学描述完成后，必须展示以下内容给用户确认：
> 1. 方法学描述段落（软件版本、分析人群、主要方法、效应量）
> 2. 与SAP的一致性检查结果
> 3. 缺失数据处理方法说明
>
> 用户确认后才能进入合规检查。

### Phase 6: 统计质量检查（精简版）

> Stage 4 精简：仅保留统计层面的质量检查。报告规范全文合规（CONSORT/STROBE 等）
> 移至 Paper Track Stage 5.0（仅写论文时需要，见 pipeline/SKILL.md §Stage 5）。

**Step 6a: 统计一致性校验 (statcheck)** 🆕

> 参考：shared/reporting-guidelines/statcheck_rules.md — NHST 结果一致性自动校验规则

从 Phase 1（结果解读）、Phase 3（表格）、Phase 5（方法学）抽取所有 NHST 结果（t/F/χ²/r/z + df + 报告 p），独立重算 p 值并比对：

1. **抽取**: 按正则模式匹配 APA 格式统计结果（如 `t(38)=2.45, p=.019`、`F(2,57)=4.32, p=.018`、`χ²(1)=5.83, p=.016`）
2. **重算**: 用 scipy 从统计量+df 独立重算 p（双尾默认；标注 one-tailed/adjusted 的特殊处理）
3. **判定**: 绝对误差 <0.001 → ✅；0.001–0.01 → ⚠️ 边界；≥0.01 → ❌；跨 0.05 阈值 → ❌❌ 严重
4. **降级**: scipy 不可用时降级为格式抽取+明显矛盾检测（如 `p<.001` 但 stat 极小）

> 详细正则模式、重算公式、误报缓解见 `shared/reporting-guidelines/statcheck_rules.md`。

**Step 6b: 统计反模式检查**（保留）

> 参考：shared/anti-patterns/medical_stats_anti_patterns.md（D1/D2/D3/M1-M6）

**Step 6c: quality_checklist 统计维度**（保留统计相关维度）

> 参考：shared/reporting-guidelines/quality_checklist.md
> 仅检查：统计方法维度 + 结果报告维度（其余维度移至 Paper Track）

**Step 6d: 统计约束合规检查** 🆕

> 参考：shared/statistics-methods/statistical_constraints.md — 统计约束规则全文

检查项：

| 检查内容 | 规则 | 检查方式 | 不通过处理 |
|---------|------|---------|-----------|
| P值格式 | P-R01~R07 | 扫描所有 P 值字符串，无 "P = 0.000"、无二元化表述 | 强制修正 |
| 方法一致性 | M-R01~R08 | 核对方法一致性追踪表，加权/非加权无混用 | 强制重跑 |
| 数据集一致性 | D-R01~R05 | 核对数据集一致性追踪表，差异已确认 | 阻断至用户确认 |
| 统计原则违反 | S-R01~R08 | 核对统计原则违反日志，所有违反已处理 | 阻断至用户确认 |
| 变量命名一致性 | V-R01~V07 | SAP/表格/图表/正文变量名比对 | 强制修正 |

**Step 6e: 图表发表级质量检查** 🆕

> 参考：shared/chart-styles/publication_figure_standards.md — 发表级图表标准

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

**statcheck 校验异常处理** 🆕：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| ⚠️ 边界不一致（绝对误差 0.001–0.01） | 放宽容许至±0.001 后重检 → 若误差仍存在但非跨阈值，加脚注"四舍五入差异" | 记录不一致项，在报告中标注"统计量待核对" |
| ❌ 不一致（绝对误差 ≥0.01） | 逐项定位报告原文，与统计软件原始输出比对 → 修正报告中的 p 值或统计量 | 无法判定真因时加注"数值差异需作者复核" |
| ❌❌ 跨显著性阈值反转（如报告 p=0.049 但重算 p=0.067） | 核实 df 是否从正确的分析输出提取 → 若确认报告有误则强制修正 | 标记为"严重不一致"，在报告显著位置标注❌并提示作者提供完整统计输出 |
| `scipy` 不可用降级 | 降级为格式抽取 + 明显矛盾检测（如报告 `p<.001` 但 t 统计量 < 0.5） | 无法降级时跳过 statcheck，在合规报告中标注"statcheck 未运行" |

> **🔴 [MANDATORY-M4]** 统计质量检查结果（含 statcheck 校验）展示后，**必须等待用户确认**。
> - ✅ 全部通过 → 进入 ★ STAGE 4 CHECKPOINT（pipeline 决策节点）
> - ⚠️ 有问题 → 修正后重新检查，直到通过
> - ❌ 严重不一致 → 强制修正后才输出

### Phase 7: 报告组装 (HTML 图文报告)

> 参考：shared/report-assembler/render_report_html.py — HTML 报告渲染器

将 Phase 1–6 的产物组装为一份单文件自包含的 HTML 图文报告。

**Step 7.1: AI 构建 JSON 骨架**

收集各阶段产物，构造 JSON 骨架 (`report_sections.json`)：

| 来源 | 产物 | JSON 章节类型 |
|------|------|--------------|
| Phase 1 | 结果解读文本 | `{"type": "text"}` |
| Phase 3 | 表格 (Markdown Table) | `{"type": "table"}` |
| Phase 4 | 已生成的 SVG+PNG | `{"type": "figure", "figure_file": "...", "figure_file_svg": "..."}` |
| Phase 5 | 方法学描述 | `{"type": "text"}` |
| Phase 6 | 合规检查结果 | `{"type": "checklist"}` |

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

**Step 7.2: 调用渲染器生成 HTML**

```bash
# 完整 API 见 shared/report-assembler/render_report_html.py
python shared/report-assembler/render_report_html.py \
  --title "报告标题" \
  --sections reports/report_sections.json \
  --figures reports/figures/ \
  --output reports/final_report.html \
  --css-theme minimal
```

> 渲染失败时自动降级为 Markdown 拼接：将 JSON 骨架中各 section 按序拼接为 `final_report.md`。

**Step 7.3: 输出产物**

`final_report.html` + `final_report.md` + `figures/*.png` + `tables/*.docx` + `journal-template.json`

**报告组装异常处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| JSON 骨架缺少必需章节（如 "methods" 未生成） | 检查缺失章节来源阶段是否完成 | 在骨架中补充空章节占位，标注"待补充" |
| 渲染脚本 `render_report_html.py` 不存在或报错 | 检查路径和依赖（python-docx / jinja2） | 用 Markdown 直接拼接替代 HTML 渲染，输出纯文本版 |
| 产物路径冲突（png/docx 同名列） | 自动追加时间戳后缀（如 `table1_baseline_1600.docx`） | 提示用户选择覆盖或重命名 |

**报告组装检查点**：

> 🔴 [MANDATORY-S7] 报告组装完成后，必须展示以下内容给用户确认：
> 1. 最终报告文件路径（HTML + MD）
> 2. 图表文件清单
> 3. 表格文件清单
> 4. 合规检查最终结果
>
> 用户确认后才能交付最终报告。

## 检查点量化标准

| 检查点 | 类型 | 通过标准 | 阻断标准 | 降级策略 |
|--------|------|---------|---------|---------|
| Phase 3 变量命名 | 自动 | V-R01~R07全通过 | 任何V-R违规 | 自动修正→重新检查 |
| Phase 3 P值格式 | 自动 | P-R01~R07全通过 | 任何P=0.000 | 自动格式化→重新检查 |
| Phase 5 statcheck | 自动 | 统计结果一致 | P值/CI/效应量不一致 | 标记[STATCHECK_FAILED]→退回Phase 3 |
| Phase 6d 约束检查 | 阻断 | P-R/M-R/D-R/S-R全通过 | 任何约束违规 | 修复→重新检查(最多3次) |
| Phase 6e 图表质量 | 阻断 | SVG+PNG 300dpi双格式 | 格式/分辨率不达标 | 重新生成→重新检查 |
| Phase 7 报告组装 | 自动 | HTML渲染成功 | HTML渲染失败 | 降级为Markdown[HTML_FALLBACK] |

> **修复上限**: Phase 6d/6e最多修复3次，超过3次标记[QUALITY_DEGRADED]并继续
> **阻断规则**: Phase 6d的P-R01和M-R01为硬阻断项，不可降级

## 故障处理与降级策略

| 触发条件 | 降级策略 | 标记 | 后续操作 |
|---------|---------|------|---------|
| statcheck API 不可用 | 跳过自动验证，推荐人工复核 | 报告标注 [STATCHECK_SKIPPED] | 在合规报告中注明"statcheck 未运行"，建议作者手动核对统计量 |
| 图表生成失败（matplotlib/seaborn 报错） | 降级为纯表格报告 | 报告标注 [FIGURE_ERROR] | 记录错误日志，输出数据+代码供用户后续自行渲染 |
| CONSORT/STROBE checklist 文件缺失 | 使用内嵌迷你清单（10项核心条目） | 报告标注 [CHECKLIST_DEGRADED] | 在报告中注明"使用精简清单"，提示用户补充完整清单 |
| HTML 渲染失败 | 降级为 Markdown 报告 | 报告标注 [HTML_FALLBACK] | 输出 final_report.md，记录渲染错误供排查 |

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

## 报告反例与黑名单

> **速查版**：以下 8 项为报告生成中最常见的高频违规行为，完整反模式目录见下方"## 反例与黑名单"。

| 编号 | 禁止行为 | 为什么 | 正确做法 |
|------|---------|--------|---------|
| 1 | P值显示为 P=0.000 | 违反P-R01规则 | 显示 P<0.001 |
| 2 | 表格中使用非标准变量名（如"age_yrs"） | 违反V-R01规则 | 使用三列命名系统的标准显示名 |
| 3 | 图表分辨率低于300dpi | 不满足发表标准 | SVG+PNG 300dpi双格式输出 |
| 4 | 跳过statcheck验证直接输出报告 | 无法检测统计错误 | 必须执行Phase 5 statcheck |
| 5 | 报告中混用加权和非加权结果 | 违反M-R01规则 | 标注数据来源，不混用 |
| 6 | 三线表使用竖线 | 不符合医学期刊规范 | 标准三线表（顶线+表头线+底线） |
| 7 | 效应量不报告95%CI | 不满足报告规范 | 必须报告效应量+95%CI+P值 |
| 8 | CONSORT流程图缺失 | 违反CONSORT规范 | RCT报告必须包含CONSORT流程图 |

## 反例与黑名单

> **以下行为必须避免**。违反任何一条将导致报告质量不可靠或误导读者。
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
| 13 | 跳过结果解读直接生成表格（guided 模式） | 表格脱离临床语境，读者无法理解含义 | guided 模式下 Phase 1 解读必须先于 Phase 3/4；`--type` 参数指定的 quick 模式除外 |
| 14 | 合规检查不通过仍生成最终报告 | 不合规报告无法通过伦理审查和期刊审稿 | [MANDATORY-M4] 合规检查不通过 → 修正 → 重新检查 → 通过后才输出 |

### 🚫 statcheck 与数值一致性禁忌 🆕

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 15 | statcheck 发现的 ❌❌ 不一致静默修正不记录 | 静默修正掩盖根源问题，同一类错误会持续出现 | 每次不一致必须记录原始值→修正值→差异原因，记入偏差日志 |
| 16 | 多个统计量同为不一致但只修部分 | 选择性修正会歪曲结果报告完整性 | 所有不一致项必须全部核实并修正，不能跳过解读复杂的项目 |
| 17 | statcheck 不通但跳过统计方法学段落的交叉验证 | 方法学段落的 t/F/χ² 陈述若与实际分析不符，同样属于数值不一致 | statcheck 的范围必须覆盖 Phase 1（结果解读）+ Phase 3（表格）+ Phase 5（方法学），缺一不可 |

### 🚫 报告组装禁忌 🆕

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 18 | JSON 骨架中 figure 的 figure_file 指向不存在文件 | 最终报告中产生坏图，读者无法查看 | Step 7.1 组装前验证所有 figure_file 路径是否可达；不可达则跳过该 figure，在章节中标注"[图表暂不可用]" |
| 19 | 多类型图表使用相同文件名 | Phase 7 输出路径冲突导致旧图覆盖新图 | 文件名必须区分图类型和内容（如 `figure1_km_curve.png` vs `figure2_forest.png`），违者自动追加时间戳 |
| 20 | 报告组装后不验证交叉引用完整性 | 报告中可能出现"如图X所示"但图X不存在的孤引用 | assembly 完成后必须扫描 HTML/MD 全文，验证所有 "图N"/"表N"/"Figure N"/"Table N" 引用与实际生成的图表清单一一对应 |

---

## ★ STAGE 4 CHECKPOINT（MANDATORY-M4'，Pipeline 决策节点）

> **前置条件**：Phase 7 报告组装完成。产物：final_report.md + final_report.html + figures/*.png + tables/*.docx。
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
- 选 **[B]** → 守卫检查通过后 `passport.set_track("full_paper")`，dispatch 到 pipeline Stage 5.0（Paper Intake → academic-pipeline）
- 守卫检查失败 → 提示用户补全缺失产物，不进入 Paper Track



