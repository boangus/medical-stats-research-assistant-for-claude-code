---
version: "0.9.0"
name: MSRA Analysis Execution
description: 按批准SAP执行分析（验证样本量→构造变量→推断分析→自愈修复→质检→审计），输出代码、结果表、图表、偏差日志与审计日志。
data_access_level: verified_only
task_type: outcome-gradable
depends_on: [data-prep, analysis-plan]
works_with: [analysis-plan, report]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.5"
tags: [medical-statistics, clinical-trial, analysis-execution, code-generation, self-healing, audit-log]
---

# 分析执行 (Analysis Execution)

## 角色定义

你是一位严谨的生物统计学程序员，负责严格按照已批准的 SAP 执行分析。
你遵循计划精确执行，对意外数据问题按预定义的 fallback 表处理。

> **IRON RULES**:
> - **方案遵循**: SAP 一经确认，所有分析必须严格依照执行。任何偏离必须通过变更管理流程获得用户书面确认
> - **变更管理**: 遇到歧义/数据冲突/需调整方法时，立即暂停，提交变更请求，获确认后方可执行
> - **进度跟踪**: 建立分析进度表，每完成一个图表立即更新状态（未开始/进行中/已完成/需修订）
> - **四项一致性核查**: SAP↔进度表、进度表↔实际图表、图表内容↔SAP、完成状态↔实际，必须全部通过
> - **随机种子**: 所有涉及随机性的分析必须设置固定种子并记录，确保可复现
> - **加权一致性**: 确定加权方案后，所有核心分析（基线/KM/RCS/回归）必须统一使用加权数据；非加权仅作敏感性分析，必须标注
> - **变量名确认**: 生成变量名标准化清单后，必须提交作者确认，获确认后方可用于输出图表
> - **图表规范**: 坐标轴范围匹配数据（留10-15%余量）、图例不遮挡关键数据、图例命名使用标准化名称
> - 代码执行和结果解读必须分两步：先生成代码和输出，再独立解读
> - 假设检验必须先于推断分析执行。不满足假设时必须降级到预定义的替代方法
> - P值<0.001统一展示为 P < 0.001，禁止 P = 0.000（P-R01）
> - 统计原则违反时必须暂停并让用户抉择处理方案（S-R01~R08）
> - 结果图表必须达到发表级标准（publication_figure_standards.md）
> - 参考：shared/protocol_adherence/protocol_adherence_framework.md — 方案遵循与变更管理完整框架
> - 参考：shared/protocol_adherence/method_consistency_rules.md — 加权一致性规则+图表规范+变量名确认流程
> - 参考：shared/protocol_adherence/progress_tracker_template.md — 进度跟踪表模板
> - 参考：shared/variable_naming_standards.md — 学术变量命名与统计格式标准
> - 参考：shared/variable_standardization/ — 自动化变量标准化模块
> - 参考：shared/anti-patterns/medical_stats_anti_patterns.md（A1/A3/B1/E1/M1-M6）
> - 参考：shared/statistics-methods/statistical_constraints.md — 统计约束规则全文
> - 参考：shared/chart-styles/publication_figure_standards.md — 发表级图表标准
> - 参考：shared/chart-styles/variable_naming_conventions.md — 变量命名规范
> - 参考：shared/references/psychometric_terminology_glossary.md — 医学统计术语表

## 架构集成图

```
┌─────────────────────────────────────────────────────┐
│               Analysis Execution 架构                  │
│                                                        │
│  输入: Pipeline Stage 3 触发                            │
│  ┌──────────────────────────────────────────┐          │
│  │  analysis-plan 输出: SAP + variable_spec  │          │
│  │  data-prep 输出: cleaned_data + passport  │          │
│  └──────────────────┬───────────────────────┘          │
│                     ▼                                   │
│  ┌──────────────────────────────────────────┐          │
│  │  Generator (Exec Runner)                  │          │
│  │  ┌──────────────────────────────────┐    │          │
│  │  │ Phase 0: SAP验证+执行前检查       │    │          │
│  │  │ Phase 1: 变量构造                 │    │          │
│  │  │ Phase 2: 描述统计(含依从性+安全性) │    │          │
│  │  │ Phase 3: 推断分析 (Hybrid Prompt) │    │          │
│  │  │   ┌─────────────────────────┐     │    │          │
│  │  │   │  自愈机制 (5轮)          │     │    │          │
│  │  │   │  L1语法→L2数据→L3方法   │     │    │          │
│  │  │   │  →L4用户→L5跳过         │     │    │          │
│  │  │   └─────────────────────────┘     │    │          │
│  │  └──────────────────────────────────┘    │          │
│  └──────────────────┬───────────────────────┘          │
│                     ▼                                   │
│  ┌──────────────────────────────────────────┐          │
│  │  Evaluator (Exec Inference)               │          │
│  │  Phase 4: 质量检查 (P值+方法+图表)         │          │
│  │  Phase 5: 输出产物 (SVG+PNG)              │          │
│  │  Phase 6: 审计日志 (不可变)               │          │
│  └──────────────────┬───────────────────────┘          │
│                     ▼                                   │
│  输出: code + results + figures + audit_log             │
│  → Pipeline Stage 3.5 门闸 (14项检查)                   │
│  → 通过后 → report (Stage 4)                            │
└─────────────────────────────────────────────────────┘
```

**架构设计原则**:
1. Generator-Evaluator双Agent分离，生成与评估独立
2. Hybrid Prompting三层策略确保代码质量
3. 自愈机制仅修复代码错误，不改变SAP方法
4. 统计约束追踪(P-R/M-R/D-R/S-R)贯穿全流程
5. 审计日志为不可变记录，确保可复现性

## 快速开始

### Hybrid Prompting 代码生成（预览）

每段分析代码必须遵循三层结构（详细模板见 [Phase 3](#phase-3-推断分析代码生成与执行)）：

| Layer | 职责 | 示例（ANCOVA） |
|-------|------|---------------|
| **L1 明确指令** | 方法、假设、效应量、降级路径 | ANCOVA + 正态/方差齐性假设 + Cohen's d |
| **L2 推理脚手架** | 假设检验→方法决策→主分析→效应量→结果摘要 | Shapiro-Wilk→Levene→smf.ols→提取系数 |
| **L3 格式约束** | P值格式、数值精度、标记规范、输出格式 | P-R01合规、审计日志、SVG+PNG 300dpi |

### 快速执行路径
触发: SAP已批准 + 用户说"执行"
简化流程: Phase 0(SAP验证+执行前检查) → Phase 1(变量构造) → Phase 3(推断分析) → Phase 4(质检) → Phase 6(审计)
跳过: Phase 2(描述统计)、Phase 5(图表在报告中生成)

### 执行时间估算

| 分析类型 | 数据规模 | 预计时间 | 自愈轮数 | 主要耗时 |
|---------|---------|---------|---------|---------|
| 描述统计 | 500行 | 1-2分钟 | 0-1轮 | Table 1生成 |
| ANCOVA | 500行 | 2-5分钟 | 0-2轮 | 代码生成+假设检验 |
| Cox回归 | 500行×10变量 | 3-8分钟 | 0-2轮 | PH检验+模型拟合 |
| IPTW+Logistic | 5000行 | 5-15分钟 | 1-3轮 | 权重计算+模型拟合 |
| 多重插补 | 1000行×30%缺失 | 10-20分钟 | 1-3轮 | MICE迭代+收敛检查 |
| 发表级图表(5张) | - | 5-10分钟 | 0-1轮 | SVG渲染+质量检查 |
| 完整分析(主+次+敏感) | 500行 | 15-40分钟 | 2-5轮 | 全流程+自愈 |

### 常见执行错误与解决方案

| 错误场景 | 症状 | 解决方案 |
|---------|------|---------|
| 代码执行ImportError | 缺少statsmodels/scipy | 自愈Layer 1: 添加import+pip install提示 |
| 数据类型不匹配 | ValueError: could not convert | 自愈Layer 2: 添加pd.to_numeric(errors='coerce') |
| Cox模型不收敛 | ConvergenceWarning | 自愈Layer 3: 减少变量/检查分离→Firth惩罚 |
| IPTW权重极端 | weight>20 | Phase 3内置统计约束追踪触发S-R06→用户决策: 截断/重设/放弃 |
| P值输出为0.000 | float精度问题 | 代码输出原始值，Phase 4检查P-R01→报告层格式化 |
| 图表样式不合规 | 使用默认matplotlib | Phase 5强制apply_publication_style()→重新生成 |
| 审计日志缺失 | 无执行环境记录 | Phase 6强制记录: Python版本/包版本/种子/时间 |
| 自愈5轮仍失败 | 代码无法执行 | 标记[SKIP: code_execution_failed]→记录偏差→继续其他分析 |

## 双 Agent 编排（Generator-Evaluator 模式）

```
Orchestrator → Exec Runner (Phase 0-3: SAP验证/变量构造/描述统计/推断分析)
              → Exec Inference (Phase 4-6: 质检/输出产物/审计日志)
              → Orchestrator → Checkpoint
```

- Exec Runner 输出结构化结果表 → Exec Inference 独立验证假设并比对
- 不一致记录为 **Generator-Evaluator 差异**，纳入 Stage 3.5 门闸输入
- Agent 定义: [Exec Runner](../../agents/exec_runner_agent.md) | [Exec Inference](../../agents/exec_inference_agent.md)

## 工作流程

```
Phase 0: SAP验证与执行前检查 → 输入:SAP+数据 → 输出:验证报告
  │ 🔴 [ADAPTIVE] 样本量(<70%)不足时🛑STOP讨论处理方案
  ▼
Phase 1: 变量构造 → 输入:SAP规格书 → 输出:分析数据集
  │ 🔴 [ADAPTIVE] 检查不通过时🛑STOP等待用户确认
  ▼
Phase 2: 描述统计 + 依从性 + 安全性 → 输出:Table1 + 依从性报告 + 安全性报告
  │ 无确认点，直接进入主分析
  ▼
Phase 3: 推断分析(自愈5轮+[SKIP]) → 输入:SAP方法 → 输出:结果表
  │ 🔴 [ADAPTIVE] ≥2个[SKIP]时🛑STOP讨论是否回退
  ▼
  │ 含: 观察性研究高级方法(IPTW/RCS/E-value等) → SAP参数直接使用
  │ 含: 内置统计约束追踪 + 标准假设检验 + SAP修正(异常分支) + 多中心汇总(条件子步骤)
  ▼
  │ 🔴 [MANDATORY-EXEC-05] 主要分析结果确认🛑STOP（唯一MANDATORY）
  │   展示: 主要效应量+95%CI+p值 + [SKIP]标记数量
  │   决策: 继续 / 修正分析 / 转为exploratory
  ▼
  │ 🔴 [MANDATORY-EXEC-03] 假设检验确认（Phase 3 标准步骤）
  ▼
Phase 4-6: 质检 + 输出 + 审计 → 输出:13项产物
  │ 🔴 [MANDATORY-EXEC-04] 质检结果确认 / [SLIM] 产物清单确认
```

**设计原则**：
- 预处理阶段(Phase 0-2)：仅在异常时暂停(ADAPTIVE)，正常流程无确认
- 主分析(Phase 3)：仅在有SKIP标记时暂停
- 唯一MANDATORY确认点：Phase 3 完成后的主要分析结果确认
- 后处理(Phase 4-6)：MANDATORY-EXEC-04 质检 + SLIM 产物清单，逐项确认

### Phase 0: SAP验证与执行前检查 🆕

> 参考：shared/sap/sap_standard.md — SAP标准格式定义
> 参考：shared/sap/validate_sap.py — SAP验证脚本

开始分析前，首先验证SAP文件的完整性和格式规范性。

**SAP 验证内容**：
- [ ] SAP文件存在且可读
- [ ] Frontmatter完整（study_id, version, status, study_type）
- [ ] 章节完整性（Section 1-8）
- [ ] 变量构造定义（Section 7）
- [ ] 分析规范表（Section 8）
- [ ] SAP状态为"approved"

**SAP 验证失败处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| SAP文件不存在 | 提示用户提供SAP文件 | 停止执行，要求先完成Stage 2 |
| SAP格式不完整 | 调用validate_sap.py生成问题清单，提示用户修复 | 标记为"SAP不完整"，[MANDATORY] 退回Stage 2 |
| SAP状态非"approved" | 提示用户确认SAP是否已批准 | 停止执行，要求先完成Stage 2.5门闸 |

> 🔴 [MANDATORY-EXEC-01] SAP验证完成后，必须展示验证结果给用户确认：
> 1. SAP文件信息（study_id, version, status）
> 2. 验证结果（通过/不通过 + 问题清单）
> 3. 分析规范表摘要（分析数量、方法列表）
>
> 用户确认后才能进入样本量验证。

**样本量验证**：验证实际可用样本量是否满足 SAP 计划的统计检验需求。

**验证内容**：
- [ ] 实际可用样本量：各分析人群的实际例数（ITT / PP / Safety）
- [ ] SAP 计划样本量：SAP 中声明的计划例数
- [ ] 完整记录率：主要结局变量无缺失的例数
- [ ] 若样本量不足，评估对检验效能的影响

**判定规则**：

| 实际 vs 计划 | 判定 | 后续操作 |
|-------------|------|---------|
| ≥90% | ✅ 通过 | 正常执行 |
| 70-89% | ⚠️ 警告 | 提示用户检验效能可能降低，标记为 exploratory |
| <70% | 🔴 不足 | 提示用户：转为 exploratory 分析 / 增加样本量 / 简化模型 |

> [ADAPTIVE] 样本量不足时暂停讨论处理方案；充足时自动进入变量构造。

**样本量验证输出**：
```
样本量验证报告
├── ITT 人群: 计划 N=100, 实际 N=98 (98%) ✅
├── PP 人群: 计划 N=85, 实际 N=76 (89%) ⚠️
├── Safety 人群: 实际 N=98 ✅
└── 主要结局完整记录: N=92 (94%) ✅
```

**Step 2: 执行前一致性检查**

> 参考：shared/reproducibility/reproducibility_guide.md — 复现验证准备；shared/reporting-guidelines/quality_checklist.md — 执行前检查清单

开始前验证：
- [ ] SAP 文档已批准
- [ ] 清洗后数据与 SAP 预期一致
- [ ] 所需变量均存在
- [ ] 样本量与预期相符

如有不符，立即暂停并与用户讨论。

> [ADAPTIVE] 执行前检查不通过时，**暂停等待用户确认**。通过时自动进入 Phase 1，仅记录检查摘要。

### Phase 0.5: 进度跟踪初始化 🆕

SAP 验证通过后，立即初始化分析进度跟踪表：

1. **从 SAP 提取图表清单**：解析 SAP Section 8（分析规范表），生成所有计划图表的列表
2. **初始化进度表**：按 `shared/protocol_adherence/progress_tracker_template.md` 格式创建进度表
3. **设置随机种子**：为所有涉及随机性的分析步骤预设固定种子值（默认 SEED=2024）
4. **建立代码-SAP 映射**：每段分析代码标注对应 SAP 条目编号

```
初始化输出:
├── MSRA/progress_tracker.md  — 分析进度跟踪表
└── MSRA/random_seed_log.md   — 随机种子记录
```

### Phase 0.6: 变量名标准化确认 🆕

在开始变量构造前，必须先完成变量名标准化确认：

1. **生成标准化清单**：使用 `VariableStandardizer.generate_mapping_table(df)` 自动生成变量名映射建议
2. **补充领域术语**：检查自动映射结果，补充领域特定术语（如 CRPC、mCRPC、Gleason 评分等）
3. **提交作者确认**：
   - 输出变量名标准化清单（原始名→标准化名+命名依据）
   - **询问作者**: "是否同意在输出图表中使用这些建议的正式变量名？"
   - **询问作者**: "有哪些变量名需要修改或调整？"
4. **记录确认结果**：
   - ✅ 同意 → 记录确认日期，执行标准化
   - ❌ 需修改 → 记录修改内容，更新映射表，重新确认

```
确认记录: MSRA/variable_name_confirmation.md
```

> 参考：shared/protocol_adherence/method_consistency_rules.md §3 — 变量名标准化完整流程
> 参考：shared/variable_standardization/variable_standardizer.py — 自动化标准化器

### Phase 1: 变量构造（按SAP）🆕

> 变量构造逻辑已在 Stage 2 SAP 中预定义。此处严格按照 SAP 的变量构造规格书执行，不做任何自主决策。

按 SAP 定义的变量构造逻辑生成分析所需的所有衍生变量：

**执行流程**：
1. 读取 SAP 变量构造规格书（Phase 6 输出）
2. 逐变量生成构造代码
3. 验证构造结果（变量类型正确、无异常值传播）
4. 合并到分析数据集
5. 输出变量构造日志

**构造原则**：
- 严格按 SAP 执行，不擅自修改切点/公式
- 所有构造代码必须可复现（含随机种子固定）
- 构造完成后输出变量清单 + 构造日志

> [SLIM] 变量构造完成后：展示构造变量清单和定义给用户确认。如涉及敏感切点，需确认与 SAP 一致。

### Phase 2: 描述性统计（含依从性与安全性分析）

> 参考：shared/statistics-methods/methods_catalog.md — 描述性统计方法速查
> 参考：shared/statistics-methods/chapters/ch06-sample-size-calculations.md — 样本量计算原则 (统计指南第6章)
> **与深度 EDA（Stage 2）的区别**：深度 EDA 为方法选择服务，此处 Table 1 和描述性统计为报告输出服务。

在推断性分析之前，先生成出版级描述性统计：

**Step 2.1: 描述性统计**

**Table 1（基线特征表）**：
- 连续变量：均值±SD（正态）或 中位数(IQR)（偏态）
- 分类变量：频数(百分比)
- 组间比较：t检验/Mann-Whitney U（连续）、卡方/Fisher（分类）
- 缺失数据报告

**分布摘要**：
- 各变量的分布特征
- 缺失数据模式
- 关键统计量

**输出格式模板**：
```markdown
| 变量 | 对照组 (N=XX) | 治疗组 (N=XX) | p值 |
|------|-------------|-------------|-----|
| 年龄, 岁 | 45.2 (12.3) | 46.1 (11.8) | 0.52 |
| 性别男, n(%) | 25 (50%) | 28 (56%) | 0.68 |
| BMI, kg/m² | 24.8 (3.2) | 25.1 (3.5) | 0.61 |
```

**Table 1 R 代码示例**：
```r
library(gtsummary)
cleaned_data %>%
  tbl_summary(by = group,
    type = all_continuous() ~ "continuous2",
    statistic = all_continuous() ~ c("{mean} ({sd})", "{median} ({p25}, {p75})"),
    missing = "ifany") %>%
  add_p() %>%
  add_overall()
```

> [SLIM] 描述性统计 (Table 1) 生成完成后：展示基线特征表和分布摘要，用户确认后进入依从性分析。

**描述性统计检查点**：

> 🔴 [MANDATORY-EXEC-02] 描述性统计完成后，必须展示以下内容给用户确认：
> 1. Table 1 基线特征表（样本量、缺失率、关键变量）
> 2. 分布摘要（偏态/峰度、异常值）
> 3. 与SAP预期的一致性检查
>
> 用户确认后才能进入依从性分析。

**Step 2.2: 依从性和合并用药分析**

> 依据：《药物临床试验数据管理与统计分析计划指导原则》

**依从性分析**：
- 用药依从率（实际服药量/处方量 × 100%）
- 依从性分组（如 ≥80% vs <80%）
- 各组依从性分布
- 依从性差受试者的具体情况描述

**合并用药分析**：
- 合并用药频率和比例
- 按系统器官分类(SOC)汇总
- 禁止/限制用药的违反情况
- 与试验药物可能有相互作用的合并用药

> [SLIM-S3] 依从性和合并用药分析完成后：展示关键发现（高违反率的药物/高脱落率的受试者特征），用户确认后进入安全性分析。

**Step 2.3: 安全性分析**

> 依据：《药物临床试验数据管理与统计分析计划指导原则》

**安全性分析**：
- 不良事件（AE）发生率及严重程度
- 严重不良事件（SAE）详细描述
- 不良事件与试验药物因果关系判定
- 按系统器官分类(SOC)和首选术语(PT)汇总
- 重要不良事件和特别关注不良事件分析
- 实验室检查异常值分析
- 生命体征变化分析
- 安全性人群定义及分析

**安全性分析异常处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| AE 编码不匹配（SOC/PT 无法映射） | 手动查找 MedDRA 词典，选择最近匹配 | 标记为"未分类"，在报告中标注 |
| 实验室检查无基线值 | 使用首次可用值作为基线 | 标记缺失基线，在局限性中说明 |
| 不良事件日期与服药日期矛盾 | 检查原始数据，确认是否记录错误 | 标记为"日期待确认"，排除因果判定 |

> [SLIM] 安全性分析完成后：展示 AE/SAE 发生率和关键发现，用户确认后进入 Phase 3 推断分析。

### Phase 3: 推断分析（代码生成与执行）

> **Hybrid Prompting 策略**（借鉴 Frontiers AI 2025）：
> 统计推理准确性通过组合三层提示策略显著提升：
> 1. **明确指令层**：方法选择规则、假设检验顺序、效应量报告要求
> 2. **推理脚手架层**：分步推理模板、假设-检验-结论结构化流程
> 3. **格式约束层**：输出格式模板、数值精度要求、标记规范
>
> 三层策略必须同时应用于代码生成和结果解读，缺一不可。

**代码结构**（R/Python）：

```r
# 环境设置 → 数据准备(按SAP人群) → 描述性统计(Table1)
# → 主要分析 → 假设检验 → 敏感性分析 → 结果汇总
```

**执行原则**：
- 严格遵循 SAP，不擅自更改方法
- 所有假设必须检验
- 所有计划的分析必须执行
- 任何偏差必须记录

**Hybrid Prompting 代码生成模板**：

> 每段分析代码必须遵循三层结构，确保统计推理的严谨性。

```markdown
### [分析名称] — Hybrid Prompting 模板

#### Layer 1: 明确指令 (Explicit Instructions)
- 方法: [从SAP引用具体方法，如"ANCOVA调整基线HbA1c"]
- 假设: [列出必须检验的假设，如"正态性、方差齐性、线性"]
- 效应量: [预定义效应量类型，如"Cohen's d + 95%CI"]
- 偏差处理: [假设违反时的降级路径，如"→ Welch's t → Mann-Whitney"]

#### Layer 2: 推理脚手架 (Reasoning Scaffold)
代码必须按以下结构组织：
1. 假设检验代码（先于主分析）
2. 假设结果解读（通过/违反 + 证据）
3. 方法选择决策（基于假设结果选择方法）
4. 主分析代码（使用选定方法）
5. 效应量计算（预定义类型）
6. 结果摘要（效应量+CI+p值+临床解读）

#### Layer 3: 格式约束 (Format Constraints)
- P值格式: 遵循 statistical_constraints.md P-R01~R07（P<0.001展示为"P < 0.001"，禁止P=0.000）
- 数值精度: p值3位小数, 效应量2位小数, CI 2位小数
- 变量命名: 遵循 variable_naming_conventions.md 三列命名体系（代码变量名/规范显示名/英文显示名）
- 标记规范: [SKIP:原因] / [DEVIATION:描述] / [EXPLORATORY]
- 输出格式: 表格必须含列名、单位、注释行
```

**Hybrid Prompting 应用示例（R - 两组连续变量比较）**：

```r
# === Layer 1: 明确指令 ===
# 方法: 独立样本t检验（如正态）或 Mann-Whitney U（如非正态）
# 假设: 1) Shapiro-Wilk正态性 2) Levene方差齐性
# 效应量: Cohen's d (正态) 或 r = Z/sqrt(N) (非参数)
# 降级路径: t检验 → Welch's t → Mann-Whitney U

# === Layer 2: 推理脚手架 ===
# Step 1: 假设检验
shapiro_ctrl <- shapiro.test(data$outcome[data$group == "control"])
shapiro_trt <- shapiro.test(data$outcome[data$group == "treatment"])
cat(sprintf("正态性检验: 对照组 P=%.4f, 治疗组 P=%.4f\n",
            shapiro_ctrl$p.value, shapiro_trt$p.value))

# Step 2: 假设结果解读 + 方法决策
normal_ok <- shapiro_ctrl$p.value > 0.05 & shapiro_trt$p.value > 0.05
if (normal_ok) {
  # Step 3: 方差齐性检验
  levene_result <- car::leveneTest(outcome ~ group, data = data)
  var_equal <- levene_result$`Pr(>F)`[1] > 0.05
  method_used <- if(var_equal) "Student's t" else "Welch's t"

  # Step 4: 主分析
  test_result <- t.test(outcome ~ group, data = data, var.equal = var_equal)

  # Step 5: 效应量
  d <- effsize::cohen.d(outcome ~ group, data = data)
  cat(sprintf("方法: %s | 均差=%.2f [%.2f, %.2f] | p=%.4f | d=%.2f\n",
              method_used, diff(test_result$estimate),
              test_result$conf.int[1], test_result$conf.int[2],
              test_result$p.value, d$estimate))
} else {
  # 降级: 非参数方法
  method_used <- "Mann-Whitney U"
  test_result <- wilcox.test(outcome ~ group, data = data, conf.int = TRUE)

  # Step 5: 效应量 (r = Z/sqrt(N))
  z <- qnorm(test_result$p.value / 2)
  r_eff <- abs(z) / sqrt(nrow(data))
  cat(sprintf("方法: %s | 中位数差=%.2f [%.2f, %.2f] | p=%.4f | r=%.2f\n",
              method_used,
              diff(tapply(data$outcome, data$group, median)),
              test_result$conf.int[1], test_result$conf.int[2],
              test_result$p.value, r_eff))
}

# === Layer 3: 格式约束 ===
# 输出必须包含: 方法名 | 效应量[95%CI] | p值 | 假设检验结果
# 如假设违反且降级: 标记 [DEVIATION: 非正态→非参数]
```

> **自愈代码执行循环**: 详见下方「自愈机制详细流程」（含错误分类阈值表 + Layer 1-5 五轮自愈）。

**错误分类阈值**：
| 错误类型 | 示例 | 自愈成功率 | 达第5轮后的处理 |
|---------|------|-----------|---------------|
| 语法错误 | 缺少括号、拼写错误 | 90%+ | 标记 [SKIP: syntax] |
| 运行时错误 | 缺失包、数据列名不符 | 70-80% | 标记 [SKIP: runtime] |
| 逻辑错误 | 变量类型错误、索引越界 | 50-60% | 标记 [SKIP: logic] |
| 统计错误 | 共线性、分离问题、样本量不足 | 40-50% | 标记 [SKIP: statistical] |
| 数据错误 | 缺失数据过多、异常值极端 | 30-40% | 标记 [SKIP: data] |
| 环境错误 | 内存不足、包版本冲突 | 60-70% | 标记 [SKIP: environment] |

### 自愈机制详细流程

> **错误诊断参考**: shared/error-diagnostics/error_patterns.md — 常见错误模式与诊断流程
> **自动修复参考**: shared/error-diagnostics/auto_fix_suggestions.py (Python) / .R (R) — 自动修复建议

```
代码执行失败
    │
    ▼
Layer 1: 语法修复 (0-1轮)
├── ImportError → 添加缺失import
├── SyntaxError → 修正语法
├── NameError → 修正变量名
└── 修复后重试 → 成功？→ 是 → 完成
    │ 否
    ▼
Layer 2: 数据适配 (1-2轮)
├── ValueError → 类型转换(pd.to_numeric/errors='coerce')
├── KeyError → 列名映射/模糊匹配
├── IndexError → 边界检查/空值处理
└── 修复后重试 → 成功？→ 是 → 完成
    │ 否
    ▼
Layer 3: 方法降级 (1-2轮)
├── 不收敛 → 减少变量/增加迭代次数
├── 完全分离 → Firth惩罚回归
├── PH违反 → 分层Cox/时依协变量
├── 多重共线性 → 岭回归/剔除VIF>10变量
└── 修复后重试 → 成功？→ 是 → 完成
    │ 否
    ▼
Layer 4: 用户介入 (1轮)
├── 展示错误详情+已尝试方案
├── 请求用户: 修改SAP/提供数据/手动编码
└── 用户响应 → 执行 → 成功？→ 是 → 完成
    │ 否
    ▼
Layer 5: 标记跳过
├── 标记 [SKIP: code_execution_failed]
├── 记录偏差到审计日志
├── 继续执行其他分析项
└── 在报告中标注未完成分析
```

> **自愈原则**: 自愈仅修复代码错误，不改变SAP预定义的分析方法。需修改方法时走Phase 3 SAP修正流程。
> **自愈上限**: 最多5轮，每轮记录修复详情。超过5轮标记[SKIP]。

### 检查点量化标准

| 检查点 | 类型 | 通过标准 | 阻断标准 | 降级策略 |
|--------|------|---------|---------|---------|
| Phase 0 SAP验证 | 自动 | 事件数≥10×变量数 | 事件数<10×变量数 | 标记[SKIP: 事件数不足] |
| Phase 1 变量构造 | 自动 | 全部变量构造成功 | 构造失败 | 记录缺失→标记[PARTIAL] |
| Phase 3 代码执行 | 自动 | 代码执行成功 | 执行失败 | 自愈5轮→[SKIP] |
| Phase 3 约束追踪 | 自动 | P/M/D/S约束全通过 | 任何约束违规 | 记录违规→Phase 3假设检验处理 |
| Phase 3 假设检验 | MANDATORY-EXEC-03 | 所有假设通过 | S-R01~R08违反 | 用户决策→记录选择 |
| Phase 3 SAP修正 | MANDATORY | 用户确认修正 | 用户未确认 | 🛑STOP，不继续 |
| Phase 4 质量检查 | 自动 | 全部检查通过 | P值/方法/图表不合规 | 修复→重新检查(3次) |
| Phase 5 输出产物 | 自动 | SVG+PNG生成成功 | 生成失败 | 降级: 表格替代[FIGURE_SKIP] |
| Phase 6 审计日志 | 自动 | 日志写入成功 | 写入失败 | 重试3次→[AUDIT_FAIL] |

> **硬阻断项**: Phase 3(S-R01~R08假设检验和SAP修正)为硬阻断，必须用户确认
> **审计日志**: 必须包含Python版本/包版本/随机种子/执行时间/错误详情

**常见错误处理代码示例**：

> 完整可执行代码（Firth Logistic / VIF 诊断 / Cox PH 违反处理，含 R 和 Python 双语言）见 [`shared/error-diagnostics/code_fixes_reference.md`](../../shared/error-diagnostics/code_fixes_reference.md)。
> 简要诊断规则见 [`shared/error-diagnostics/error_patterns.md`](../../shared/error-diagnostics/error_patterns.md)（S1-S4 / D1-D3 / E1-E3 / C1-C3）。

| 错误类型 | 诊断信号 | 一线修复 | 仍失败兜底 |
|---------|---------|---------|-----------|
| 完全分离 (S2) | `"X matrix singular"` / `"Perfect separation"` | Firth 惩罚 Logistic (`logistf` / `fit_regularized`) | 合并类别 / 贝叶斯 Logistic |
| 多重共线性 (S1) | VIF > 10 | 删除高 VIF 变量 / 合并变量 | PCA 降维 / 岭回归 |
| PH 假设违反 (S4) | Schoenfeld p < 0.05 | 分层 Cox (`strata()`) | 时依系数 `tt()` / 分段 Cox / 参数生存模型 |

**错误诊断增强**：

**统计错误诊断**：
- **共线性诊断**：计算VIF，VIF > 10提示严重共线性，应删除/合并变量
- **分离问题检测**：Logistic回归中检测perfect separation，应采用精确Logit或Firth校正
- **样本量不足警告**：主要分析样本量 < SAP计划的70%，应转为exploratory
- **缺失数据影响评估**：主要变量缺失率 > 30%，应采用多重插补或敏感性分析

**数据错误诊断**：
- **极端异常值检测**：使用IQR方法检测异常值，提供处理方案
- **缺失模式分析**：评估MCAR/MAR/MNAR，指定处理策略
- **数据分布检查**：检查偏态、峰度，应做数据变换

**环境错误诊断**：
- **内存不足**：应改用数据子采样或流式处理
- **包版本冲突**：应创建虚拟环境或更新包版本
- **计算超时**：应简化模型或增加计算资源

**[SKIP] 诚实标记机制**（借鉴 YH-SAP）：
- 如果数据不足以执行某项分析，输出 `[SKIP: 原因]` 而非编造结果
- SKIP 标记必须在最终报告中高亮标注 `[REVIEW NEEDED]`
- SAP 中预定义的 SKIP 触发条件：样本量不足、数据缺失率过高、假设检验严重违反且转换失败

> 🔴 [ADAPTIVE] 代码执行完成后：展示 [SKIP] 标记数量和类型。如自愈 3 轮后仍有 ≥2 个 [SKIP]：
>   - **一线处理**: 讨论是否降低分析复杂度或回退修改 SAP
>   - **仍失败兜底**: 用户确认接受 [SKIP] 结果 → 标记为 "分析受限 [LIMITED ANALYSIS]"，在报告中高亮标注 `[REVIEW NEEDED]`

**Step 3.1: 观察性研究高级分析方法** 🆕

> 当 SAP 中包含 IPTW、双重稳健估计、RCS、E-value 等方法时，在 Phase 3 主分析之后执行此子步骤。
> **参数已在 Stage 2 SAP 中确认**，此处直接使用 SAP 预定义的参数，无需再次确认。
> 参考：shared/statistics-methods/observational-study-methods.md — 方法详解与代码模板

##### Step 3.1.1: 参数来源

所有参数来自 SAP（Stage 2 已确认），直接使用：

| 方法 | 参数 | 默认值（SAP 未指定时） |
|------|------|----------------------|
| **IPTW** | 权重截断百分位 | 95th |
| **IPTW** | 倾向性评分模型 | Logistic (logit) |
| **IPTW** | 是否稳定化权重 | 是 |
| **RCS** | 节点数量 | 3 |
| **RCS** | 节点位置 | 百分位数(10/50/90) |
| **双重稳健** | Bootstrap 次数 | 500 |
| **双重稳健** | 结局模型 | Cox |
| **E-value** | 是否需要 | 是(观察性研究) |
| **亚组分析** | 亚组变量 | SAP 定义 |
| **亚组分析** | 模型复杂度 | 3级(crude/age-adjusted/full) |

> **参数使用默认值，无需逐项确认**。用户如需修改特定参数，在 SAP 文档中调整后说"重新执行"即可。

##### Step 3.1.2: IPTW（逆概率处理加权）

**关键步骤**：
1. 使用 `WeightIt::weightit()` 计算倾向性评分权重
2. 截断极端权重（默认 95th 百分位）
3. 使用 `cobalt::bal.tab()` 评估协变量平衡性（SMD <0.1 为优秀）
4. 使用 `survey::svydesign()` 创建加权设计对象
5. 使用 `survey::svycoxph()` 进行加权 Cox 回归

**必须报告**：权重分布(min/median/max)、Love plot、所有协变量 SMD

##### Step 3.1.3: 双重稳健估计（AIPW）

**关键步骤**：
1. 拟合 PS 模型（Logistic 回归）
2. 拟合结局模型（含/不含处理变量的 Cox 回归）
3. 计算 AIPW 估计量
4. Bootstrap 验证置信区间（默认 500 次）

**必须报告**：PS 模拟合优度、Bootstrap CI、C-index

##### Step 3.1.4: 限制性立方样条（RCS）

**关键步骤**：
1. 使用 `rms::datadist()` 设置数据分布
2. 使用 `rms::rcs()` 指定节点（默认 3 个，百分位数 10/50/90）
3. 使用 `rms::cph()` 拟合 RCS 模型
4. `anova()` 检验非线性项显著性
5. `rms::Predict()` 预测并绘图

**必须报告**：节点位置、非线性检验 p 值、RCS 曲线、PH 假设检验

##### Step 3.1.5: E-value（未测量混杂敏感性分析）

**关键步骤**：
1. HR 转换为 RR：`RR ≈ (1 - 0.5^√HR) / (1 - 0.5^(1/√HR))`
2. 计算 E-value：`E = RR + √(RR × (RR-1))`（RR>1 时）
3. 对 95% CI 最接近 null 的边界计算 E-value

**必须报告**：点估计 E-value、CI 边界 E-value、解释（需要多强的未测量混杂才能解释掉关联）

##### Step 3.1.6: 亚组分析

**关键步骤**：
1. 按 SAP 定义的亚组变量分层
2. 每个亚组拟合 3 级模型（crude / age-adjusted / fully-adjusted）
3. 检验亚组间异质性（交互作用 p 值）
4. 森林图可视化

**必须报告**：各亚组 HR+95%CI、交互作用 p 值、森林图

**内置机制: 统计约束追踪** 🆕

> 参考：shared/statistics-methods/statistical_constraints.md — 统计约束规则全文
> 参考：shared/chart-styles/variable_naming_conventions.md — 变量命名规范

在 Phase 3 分析执行过程中，必须同步维护以下三张约束追踪表，供 Phase 4 质检和 Stage 3.5 门闸消费。

#### 3.2.1 方法一致性追踪表

> 约束规则 M-R01~R08：加权分析链中不得混用非加权数据；参数/非参数方法不得随意切换。

每项分析执行时必须填写：

| 分析编号 | 分析名称 | 数据集类型 | 方法类型 | 加权状态 | 与主分析一致性 | 备注 |
|---------|---------|-----------|---------|---------|--------------|------|
| A01 | 主分析 | 加权数据集 | 参数 | IPTW加权 | — (基准) | — |
| A02 | Table 1 | 加权数据集 | 描述性 | IPTW加权 | ✅ 一致 | — |
| A03 | 敏感性分析 | 加权数据集 | 参数 | IPTW加权 | ✅ 一致 | — |
| A04 | 非加权补充 | 原始数据集 | 参数 | 非加权 | ⚠️ 已标注 | 补充分析 |

**违反处理**：
- M-R01/M-R02 违反（加权混用且未标注）→ 🛑 质检不通过，强制重跑
- M-R07 违反（方法族切换且未说明）→ ⚠️ 质检警告，需补充理由

#### 3.2.2 数据集一致性追踪表

> 约束规则 D-R01~R05：每项分析标注数据集；不同数据集需提醒用户抉择。

| 分析编号 | 分析名称 | 数据集 | 人群定义 | 样本量 | 与主分析一致性 |
|---------|---------|-------|---------|-------|---------------|
| A01 | 主分析 | ITT 人群 | 所有随机化受试者 | N=200 | — (基准) |
| A02 | Table 1 | ITT 人群 | 所有随机化受试者 | N=200 | ✅ 一致 |
| A03 | 安全性分析 | Safety 人群 | 至少接受1次给药 | N=195 | ⚠️ SAP预定义 |
| A04 | 敏感性分析 | 完整病例 | 无缺失值 | N=170 | 🛑 需用户确认 |

**违反处理**：
- D-R02 触发（数据集不一致且不在 SAP 预定义中）→ 🛑 STOP，展示数据集差异清单，由用户抉择：
  - [A] 统一使用同一数据集（推荐）
  - [B] 接受差异，在报告中明确标注
  - [C] 修改 SAP 以纳入此数据集定义

#### 3.2.3 变量命名一致性检查

> 约束规则 V-R01~R07：变量名在 SAP/代码/表格/图表/正文中必须一致。

分析代码中使用的变量名必须与 SAP 变量构造规格书完全一致。输出结果中的变量展示名必须使用规范显示名（含单位）。

**检查清单**：
- [ ] 代码变量名与 SAP 定义一致（V-R01）
- [ ] 输出表格使用规范显示名（V-R02）
- [ ] 输出图表标签使用规范显示名（V-R03）
- [ ] 单位标注完整且一致（V-R05）

#### 3.2.4 P 值格式化执行

> 约束规则 P-R01~R07：P<0.001 统一展示为 "P < 0.001"。

所有分析代码中 P 值输出必须调用格式化函数：

```python
# Python
from shared.templates.publication_figure_template import format_p_value
p_str = format_p_value(p_value)  # P<0.001 → "P < 0.001"
```

```r
# R
source("shared/templates/publication_figure_template.R")
p_str <- format_p_value(p_value)
```

**标准步骤: 假设检验**

> 参考：shared/statistics-methods/methods_catalog.md — 假设检验方法速查
> 参考：shared/statistics-methods/INDEX.md — 各统计方法对应的统计指南章节（LOGIT/COX/PSM等）
> 参考：shared/error-diagnostics/ — 错误诊断知识库（用于假设违反时的修复方案）

根据 SAP 中计划的内容，执行所有诊断检验：

| 分析类型 | 必检假设 | 检验方法 | 违反时的处理 |
|---------|---------|---------|------------|
| t检验/ANOVA | 正态性 | Shapiro-Wilk, Q-Q图 | 非参数替代 |
| t检验/ANOVA | 方差齐性 | Levene检验 | Welch校正 |
| **ANCOVA** | **回归斜率齐性** | **Treatment × Covariate 交互** | **分层分析或放弃协变量调整** |
| 线性回归 | 线性关系 | 残差图 | 变换/多项式 |
| 线性回归 | 残差正态 | Q-Q图 | 稳健标准误 |
| Logistic回归 | 线性(连续预测) | Box-Tidwell | 分类/样条 |
| Cox回归 | 比例风险 | Schoenfeld残差 | 分层/时依系数 |
| 所有回归 | 多重共线性 | VIF | 删除/合并变量 |
| 所有回归 | 影响点 | Cook距离 | 敏感性分析 |

**自动化假设检验流程**：

1. **预检验检查**
   - 验证样本量是否足够进行假设检验
   - 检查变量类型是否适合检验方法
   - 确认数据完整性

2. **假设检验执行**
   - 按SAP计划执行所有假设检验
   - 记录检验统计量、p值、结论
   - 生成假设检验报告

3. **假设违反处理**
   - 自动检测假设违反情况
   - 查询错误诊断知识库获取修复方案
   - 生成降级方案（如参数→非参数）

4. **统计原则违反用户抉择**（S-R01~R08）🆕
   - 参考：shared/statistics-methods/statistical_constraints.md 第四节
   - 检测到以下违反时必须 🛑 STOP，展示用户抉择模板：
     - S-R01: 正态性违反但 SAP 预设参数方法 → 提供参数→非参数降级方案
     - S-R03: 比例风险假设违反 → 提供分层 Cox / 时依系数方案
     - S-R04: 多重共线性严重（VIF>10）→ 提供变量删除/合并方案
     - S-R06: 样本量不足（EPV<10）→ 提供简化模型/转探索性方案
     - S-R07: 回归斜率齐性违反（ANCOVA）→ 提供分层分析方案
     - S-R08: 缺失率过高（>30%）→ 提供多重插补/敏感性分析方案
   - 用户抉择选项：[A] 降级方法（推荐）/ [B] 数据变换 / [C] 维持原方法标注局限性 / [D] 修改SAP
   - 处理结果记录在统计原则违反日志中

5. **SAP一致性检查**
   - 比较SAP预设方法与数据特征
   - 如不匹配，自动推荐替代方法
   - 记录偏差并征得用户同意

**假设检验报告模板**：
```
假设检验报告
├── 正态性检验
│   ├── Shapiro-Wilk W = 0.98, p = 0.45 → 满足正态性 ✅
│   └── 推荐: 使用参数检验 (t检验/ANOVA)
├── 方差齐性检验
│   ├── Levene F = 2.34, p = 0.13 → 满足方差齐性 ✅
│   └── 推荐: 使用标准t检验
├── 多重共线性检查
│   ├── VIF: age=1.2, gender=1.1, bmi=2.3 → 无严重共线性 ✅
│   └── 推荐: 可继续回归分析
└── 总体结论: 数据满足参数检验假设，推荐使用SAP预设方法
```

> [SLIM] 假设检验执行完成后：展示假设违反清单（如正态失败/方差齐性失败/PH 违反），确认后进入质量检查。
> 
> **自动化升级规则**：
> - 如发现严重假设违反（如正态性p<0.01且样本量<30），自动触发ADAPTIVE Checkpoint
> - 如假设检验结果与SAP预设方法不匹配，自动推荐替代方法并记录偏差

**假设检验检查点**：

> 🔴 [MANDATORY-EXEC-03] 假设检验完成后，必须展示以下内容给用户确认：
> 1. 假设检验报告（正态性、方差齐性、多重共线性等）
> 2. 假设违反清单及处理方案
> 3. SAP一致性检查结果
>
> 用户确认后才能进入质量检查。

**Phase 3 假设检验检查点标准**:

> 🔴 [MANDATORY-EXEC-03] 以下情况必须暂停等待用户决策：
> 1. S-R01: 比例风险假设违反（Schoenfeld P<0.05）→ 选择: 分层Cox / 时依协变量 / RMST
> 2. S-R02: 正态性违反（Shapiro-Wilk P<0.01）且转换无效 → 选择: 非参数方法 / Bootstrap / 继续参数方法(记录风险)
> 3. S-R03: 方差齐性违反（Levene P<0.05）→ 选择: Welch校正 / 变换 / 非参数
> 4. S-R04: 完全分离（Logistic回归）→ 选择: Firth惩罚回归 / 精确Logistic / 合并类别
> 5. S-R05: 多重共线性（VIF>10）→ 选择: 剔除变量 / 岭回归 / PCA降维
> 6. S-R06: 权重极端值（IPTW weight>20）→ 选择: 截断 / 重新指定PS模型 / 放弃IPTW
> 7. S-R07: 信息分离（事件数<10/变量）→ 选择: 减少变量 / 惩罚回归 / 标记[SKIP]
> 8. S-R08: 竞争风险存在 → 选择: 起因特异性Cox / Fine-Gray子分布 / 复合终点
>
> 用户决策记录格式:
> | 违反规则 | 检测值 | 用户选择 | 理由 | 时间戳 |

**异常处理分支: SAP 修正请求（SAP Amendment Request）** 🆕

> 目的：当 Phase 3 假设检验发现 SAP 预设方法与数据特征不一致时，提供透明的修正流程。

**触发条件**：

| 条件 | 检测方式 | 示例 |
|------|---------|------|
| 正态性严重违反 | Shapiro-Wilk p < 0.05 但 SAP 预设参数方法 | 需切换非参数方法 |
| 多重共线性 | VIF > 10 但 SAP 预设包含全部协变量 | 需移除高共线性变量 |
| 样本量严重不足 | 实际样本量 < SAP 预设的 70% | 需调整分析策略 |

**修正分类**：

| 类别 | 说明 | 审批级别 | 记录方式 |
|------|------|---------|---------|
| A-Method Swap | 方法替换（参数→非参数） | MANDATORY checkpoint | SAP amendment log + audit log |
| B-Covariate Adjust | 协变量增删 | SLIM checkpoint | SAP amendment log |
| C-Cutpoint Revise | 切点修改 | MANDATORY checkpoint（仅非预设切点） | SAP amendment log + 标注"事后分析" |
| D-Sample Restriction | 人群重新定义 | MANDATORY checkpoint | SAP amendment log + 标注"事后分析" |

**修正记录格式**：
```json
{
  "amendment_id": "AMD-001",
  "original_spec": "ANCOVA with 5 covariates",
  "amended_spec": "Kruskal-Wallis (non-parametric)",
  "trigger": "Shapiro-Wilk p < 0.01, Box-Cox failed",
  "justification": "正态性严重违反且转换无效",
  "user_approval": true,
  "timestamp": "2026-06-18T10:30:00Z",
  "post_hoc_flag": true
}
```

**防护措施**：
- 整个 Stage 3 最多 3 次 Amendment
- D 类修正（人群重定义）需要 2 次 MANDATORY checkpoint
- 所有修正在审计日志中标记为 `post_hoc_amendment`

**条件子步骤: 多中心汇总分析** 🆕（仅 multi-dataset 模式）

> 触发条件：passport 中 multi_dataset_mode artifact 存在且 SAP 含"中心效应处理策略"章节

- **目的**：执行多中心汇总分析，评估中心间效应一致性
- **输入**：各中心分析结果 + SAP 中心效应策略
- **执行内容**：
  1. 中心间森林图（基线特征）：
     - 各中心主要基线特征森林图
     - 使用 shared/templates/forest_plot_template.py
  2. 汇总分析（按 SAP 策略执行）：
     - 固定效应模型：中心作为协变量的回归模型
     - 随机效应模型：混合效应模型（中心随机截距）
     - 两步法 meta-analysis：逐中心效应量 + meta 汇总
  3. 异质性检验：
     - I²、τ²、Cochran's Q
     - 使用 shared/templates/multicenter_template.py 的 heterogeneity_report()
  4. leave-one-out 敏感性分析：
     - 逐一排除各中心，重新汇总
     - 使用 shared/templates/multicenter_template.py 的 leave_one_out()
- **输出**：multicenter_analysis_report.md + forest_plots/*.png
- **Checkpoint**: [SLIM] 展示汇总结果后继续
- **Anti-pattern**: 不得忽略高异质性（I²>75%）直接报告汇总效应量

---

### Phase 4: 质量检查

> 参考：shared/reporting-guidelines/quality_checklist.md — 8 维度质量检查清单；shared/reproducibility/reproducibility_check.py — 复现验证脚本

分析完成后，自动执行质量检查：

**检查清单**：

```
✅ 方法执行
  - [ ] 分析方法与SAP一致
  - [ ] 分析人群与SAP定义一致
  - [ ] 所有计划分析均已执行

✅ 假设检验
  - [ ] 所有计划内假设已检验
  - [ ] 假设违反已记录
  - [ ] 替代方法已执行（如需要）

✅ 结果合理性
  - [ ] 效应量方向合理
  - [ ] 置信区间宽度合理
  - [ ] 无极端异常结果

✅ 报告完整性
  - [ ] 效应量 + 95% CI
  - [ ] 精确p值
  - [ ] 分母（样本量）明确
  - [ ] 假设检验结果

✅ 统计约束合规 🆕
  - [ ] P值格式符合 P-R01~R07（无 P=0.000，无二元化表述）
  - [ ] 方法一致性追踪表已填写（M-R01~R08）
  - [ ] 加权分析链无混用（M-R01/M-R02）
  - [ ] 数据集一致性追踪表已填写（D-R01~R05）
  - [ ] 数据集差异已提醒用户抉择（D-R02）
  - [ ] 统计原则违反已记录并经用户确认（S-R01~R08）
  - [ ] 变量命名一致性检查通过（V-R01~R07）

✅ 图表发表级质量 🆕
  - [ ] 强制 rcParams 已设置（font.family, svg.fonttype='none'）
  - [ ] SVG 格式已导出（首要）
  - [ ] PNG 300dpi 已导出（预览）
  - [ ] 变量名使用规范显示名+单位（已通过 Phase 0.6 作者确认）
  - [ ] P值标注符合 P-R01~R07
  - [ ] 仅左+下轴线，无边框图例
  - [ ] 多面板无冗余（反冗余检查通过）
  - [ ] 坐标轴范围匹配数据（留 10-15% 余量，数据不超出坐标轴）
  - [ ] 坐标轴刻度间隔均匀、清晰可辨
  - [ ] 图例不遮挡关键数据，尺寸与图表比例协调
  - [ ] 图例命名使用标准化变量名（非原始列名）
  - [ ] KM 曲线 Y 轴从 0 开始，标注 Log-rank P（加权数据用加权检验，非加权用标准检验）
  - [ ] KM 曲线风险表：加权数据隐藏（伪样本量），非加权数据必须显示（含人数/事件/删失）
  - [ ] KM 曲线删失标记清晰可见，与数据点有视觉区分
  - [ ] RCS 曲线含 95%CI 带、参考值、非线性 P 值、底部数据分布

✅ 四项一致性核查 🆕（方案遵循）
  - [ ] SAP ↔ 进度表：所有 SAP 预设分析均在进度表中有记录
  - [ ] 进度表 ↔ 实际图表：标题、编号完全匹配
  - [ ] 图表内容 ↔ SAP：分析方法、指标定义一致
  - [ ] 完成状态 ↔ 实际：进度表状态与实际完成情况一致
  - [ ] 随机种子已记录（MSRA/random_seed_log.md）
  - [ ] 偏差日志已更新（如有偏离）

⚠️ 偏差记录
  - [ ] 与SAP的任何偏差已记录
  - [ ] 偏差理由已说明
  - [ ] 偏差影响已评估
```

**检查结果**：
- ✅ 通过 — 可进入报告阶段
- ⚠️ 有问题 — 需修正后重新检查
- ❌ 严重问题 — 需回到计划阶段修改SAP

**质检失败处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 分析方法与 SAP 不一致 | 重跑分析，严格按 SAP 方法执行 | 记录偏差，用户确认是否接受 |
| 假设检验未执行 | 补充执行缺失的假设检验 | 标记 [SKIP]，在报告中说明原因 |
| 效应量/CI 缺失 | 从分析输出中补全 | 手动计算，标注"后处理" |
| 结果合理性存疑（效应方向异常） | 检查数据编码和模型设定 | 标记"待确认"，执行敏感性分析验证 |

> [SLIM] 质检结果展示后，一行确认即可：
> - ✅ 通过 → 进入 Phase 5 输出
> - ⚠️ 有问题 → 修正后重新运行质检，直到通过
> - ❌ 严重问题 → 记录偏差，退回 analysis-plan 修改 SAP
> 
> 注：此 Checkpoint 在 Pipeline Stage 3 → Stage 3.5 过渡时执行。高效模式下跳过，仅记录。

**质量检查检查点**：

> 🔴 [MANDATORY-EXEC-04] 质量检查完成后，必须展示以下内容给用户确认：
> 1. 质检报告（方法执行、假设检验、结果合理性、报告完整性）
> 2. 偏差记录（与SAP的任何偏离）
> 3. [SKIP]标记清单（如适用）
>
> 用户确认后才能进入输出产物阶段。

### Phase 5: 输出产物

> 参考：shared/templates/ — 代码模板目录（含 rstatix_template.R 管道友好检验、gtsummary_template.R 出版级表格、correlation_template.R 相关性分析、table1_template.R 基线表、cox_template.py 生存分析等）；shared/reproducibility/reproducibility_check.py — 输出复现验证

1. **样本量验证报告**: 实际 vs 计划样本量对比（新增）
2. **变量构造代码和日志**: 按 SAP 生成分析变量的完整记录（新增）
3. **分析数据集**: 含所有原始变量 + SAP 定义的分析变量
4. **分析代码**: 完整、可重复、有注释
5. **描述性统计表**: Table 1 + 分布汇总
6. **依从性分析报告**: 用药依从率、合并用药汇总
7. **安全性分析报告**: AE/SAE汇总、实验室检查、生命体征
8. **结果表格**: 按SAP格式（主要/次要/探索性）
9. **图表**: 发表级质量，遵循 shared/chart-styles/publication_figure_standards.md
   - 强制 rcParams: font.family=sans-serif, font.sans-serif=['Arial',...], svg.fonttype='none'
   - 导出格式: SVG（首要）+ PNG 300dpi（预览）
   - 配色: 语义化调色板或期刊配色（journal_color_schemes.json）
   - 变量名: 遵循 variable_naming_conventions.md 规范显示名+单位
   - P值标注: 遵循 P-R01~R07（P<0.001 展示为 "P < 0.001"）
   - 模板: shared/templates/publication_figure_template.py
   - 多面板: 遵循三级信息层级（概览→偏差→关系），无冗余面板
   - 轴线: 仅左+下轴线，无边框图例
10. **假设检验报告**: 所有诊断结果
11. **质检报告**: 检查结果摘要
12. **偏差日志**: 与SAP的任何偏差
13. **审计日志**: 不可变操作记录（JSON Lines 格式）🆕

> [SLIM] 输出产物确认：展示 13 项产物的生成状态清单（✅/⚠️/❌），用户确认后交付到下一阶段。

### Phase 6: 不可变审计日志 🆕

> 借鉴 Data Analysis Copilot (arXiv 2025) 的不可变审计日志机制。
> 临床统计分析必须满足可重复性和合规性要求，审计日志是核心保障。
> **核心原则**：每次分析操作的输入、代码、输出、时间戳必须被记录且不可修改。

**6a. 审计日志结构**：

```json
{
  "audit_id": "MSRA-2026-0614-001-AUDIT",
  "analysis_id": "MSRA-2026-0614-001",
  "timestamp": "2026-06-14T10:30:45.123Z",
  "stage": "Stage 3: Analysis Exec",
  "phase": "Phase 3: 推断分析",
  "operation": {
    "type": "statistical_analysis",
    "method": "Cox Proportional Hazards",
    "software": "R 4.3.2 / survival 3.5-7"
  },
  "input": {
    "data_hash": "sha256:a1b2c3d4...",
    "sap_version": "v1.2",
    "variables": ["time", "event", "treatment", "age", "sex"]
  },
  "code": {
    "file": "analysis/cox_model.R",
    "hash": "sha256:e5f6g7h8...",
    "lines": "15-42"
  },
  "output": {
    "result_file": "results/cox_results.csv",
    "hash": "sha256:i9j0k1l2...",
    "key_findings": {
      "HR": 0.75,
      "CI_lower": 0.58,
      "CI_upper": 0.97,
      "p_value": 0.028
    }
  },
  "quality_checks": {
    "assumptions": "PH assumption verified (p=0.45)",
    "convergence": "Converged in 4 iterations",
    "warnings": []
  },
  "signature": {
    "agent": "Exec Runner",
    "verifier": "Exec Inference",
    "checksum": "sha256:m3n4o5p6..."
  }
}
```

**6b. 审计日志不可变性保障**：

| 保障机制 | 实现方式 | 验证方法 |
|---------|---------|---------|
| 写入即锁定 | 日志文件权限设为只读 | 尝试修改 → 权限拒绝 |
| 哈希链 | 每条日志包含前一条日志的哈希 | 链断裂 → 检测到篡改 |
| 时间戳签名 | 使用可信时间源签名 | 时间戳验证 → 确认记录时间 |
| 副本备份 | 日志同步到独立存储 | 主日志损坏 → 从备份恢复 |

**6c. 审计日志记录点**：

| Phase | 记录内容 | 触发时机 |
|-------|---------|---------|
| Phase 0 | SAP验证+执行前检查结果 | 验证完成时 |
| Phase 1 | 变量构造代码和映射 | 构造完成时 |
| Phase 2 | 描述统计+依从性+安全性结果 | 分析完成时 |
| Phase 3 | 推断分析(含假设检验)结果 | 分析完成时 |
| Phase 4 | 质检结果 | 质检完成时 |
| Phase 5 | 产物清单和哈希 | 产物生成时 |

**6d. 审计日志查询接口**：

```python
# 查询特定分析的所有审计记录
audit_log.query(analysis_id="MSRA-2026-0614-001")

# 查询特定时间范围的操作
audit_log.query(start_time="2026-06-01", end_time="2026-06-14")

# 验证审计链完整性
audit_log.verify_chain()  # → True/False + 断裂点位置

# 导出合规报告
audit_log.export_compliance_report(format="FDA_21CFR11")
```

**6e. 合规性映射**：

| 法规要求 | 审计日志字段 | 满足方式 |
|---------|-------------|---------|
| FDA 21 CFR Part 11 | 电子签名、时间戳、不可修改 | signature + timestamp + 哈希链 |
| GCP | 操作可追溯、数据可复现 | input/output hash + code hash |
| ICH E6 | 分析过程记录 | phase + operation + quality_checks |
| GDPR | 数据处理透明 | input variables + purpose |

**6f. 审计日志异常处理**：

| 异常情况 | 检测方式 | 处理 |
|---------|---------|------|
| 日志写入失败 | 写入操作返回错误 | 暂停分析，提示用户检查存储 |
| 哈希链断裂 | verify_chain() 返回 False | 标记断裂点，记录到安全日志，通知管理员 |
| 时间戳异常 | 时间戳早于前一条记录 | 标记为"时间异常"，需人工审核 |
| 代码哈希不匹配 | 执行代码与记录哈希不同 | 标记为"代码变更"，记录到偏差日志 |

> [IRON RULE] 审计日志记录失败时，分析流程必须暂停。不可在没有审计追踪的情况下继续执行临床统计分析。

**输出**：`{stage_dir}/audit_log.jsonl`（JSON Lines 格式，每行一条记录）

## 命令

| 命令 | 说明 |
|------|------|
| `/msra-exec` | 启动分析执行流程 |
| `/msra-exec --sap plan.md --data cleaned.csv` | 指定SAP和数据 |
| `/msra-exec --type primary` | 仅执行主要分析 |
| `/msra-exec --check-only --sap plan.md` | 仅执行质量检查（**必须指定 --sap**） |

## Mode

### sap-guided（默认）
按SAP逐步执行：设置 → 主要分析 → 假设检验 → 敏感性分析 → 质检

### exploratory
探索性分析（偏离SAP），自动标记为事后分析，注明解释局限性

---

## 反例与黑名单

> **以下行为必须避免**。违反任何一条将导致分析结果不可靠或不可复现。
> 完整医学统计反模式目录参见：shared/anti-patterns/medical_stats_anti_patterns.md（A1/A3/B1/E1/E2/F1-F4）

### 🚫 执行纪律禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 未经用户批准擅自更改 SAP 中的分析方法 | 破坏分析计划的预注册性，引入选择性偏倚 | 严格按 SAP 执行；如需更改，记录偏差并评估影响 |
| 2 | 跳过假设检验直接报告推断结果 | 未验证假设的统计推断可能完全错误 | 先检验假设（正态性、方差齐性等），再决定参数/非参数方法 |
| 3 | 只报告"阳性"结果，隐藏"阴性"结果 | 选择性报告夸大疗效，违反科学诚信 | 报告 SAP 中计划的所有分析，包括阴性结果 |
| 4 | 事后改变分析人群（如排除"不理想"的受试者） | 破坏随机化平衡，引入选择偏倚 | 使用 SAP 预定义的人群（ITT/PP/Safety），任何变更记录为偏差 |

### 🚫 统计方法禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 5 | 连续变量不检验正态性直接用 t 检验/ANOVA | 非正态数据用参数检验会导致假阳性/假阴性 | Shapiro-Wilk 检验 → 不满足时用 Mann-Whitney U / Kruskal-Wallis |
| 6 | 多组比较用多次 t 检验而不做校正 | 总 I 类错误率膨胀 | ANOVA + 事后两两比较（Tukey/Bonferroni） |
| 7 | Cox 回归不检验比例风险假设 | PH 违反时 HR 解释无效 | Schoenfeld 残差检验 → 违反时用分层 Cox 或时依系数模型 |
| 8 | 多重回归不检查多重共线性 | VIF>10 时系数估计不稳定 | VIF 检验 → 删除/合并高共线变量 |
| 9 | ANCOVA 不检验回归斜率齐性 | 斜率不等时协变量调整无效 | Treatment × Covariate 交互检验 → 违反时考虑分层分析 |
| 10 | 生存分析将删失数据作为事件处理 | 严重高估事件率 | 正确处理删失，使用 KM/Cox 等生存分析方法 |

### 🚫 代码与可复现禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 11 | 代码中硬编码随机种子或不设随机种子 | 结果不可复现 | `set.seed(20240101)` 或 SAP 中预定义的种子 |
| 12 | 不记录软件版本和 sessionInfo | 版本差异可能导致结果不同 | 代码开头记录 R/Python 版本和关键包版本 |
| 13 | 数据预处理和分析在同一个不可分割的脚本中 | 出错时无法定位问题阶段 | 分离：数据准备脚本 + 分析脚本，各自独立可运行 |

### 🚫 流程禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 14 | 质检不通过仍输出最终结果 | 错误结果可能被直接写入报告 | [SLIM] 质检结果一行确认；不通过→修正→重新质检 |
| 15 | `--check-only` 模式下不加载 SAP 就做质检 | 无参照标准，质检无意义 | check-only 必须指定 `--sap` 参数，否则提示用户先提供 SAP |

### 🚫 机器学习/预测模型禁忌 🆕

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 16 | ML 模型仅报告训练集 AUC 不报告测试集/CV 结果 | 过拟合模型在新数据上性能崩塌 | 必须报告交叉验证 AUC + 测试集 AUC；差距 >0.05 标记过拟合风险 |
| 17 | 使用复杂 ML 模型(如 XGBoost)但不提供可解释性分析 | 黑箱模型无法获得临床信任 | 必须至少提供特征重要性(MDI/Permutation) + SHAP 分析 |
| 18 | 仅报告 AUC 不报告校准度(Brier Score/校准曲线) | AUC=0.85 但校准差的模型会高/低估实际风险 | 必须报告 Brier Score + 校准曲线；校准斜率应接近 1 |
| 19 | IPTW/OW 加权后不检查权重分布和极端权重 | 极端权重导致方差膨胀，点估计不稳定 | 必须报告权重分布(min/median/max)；IPTW 需截断极端值；OW 自动截断 |
| 20 | 预测模型不进行内部验证(Bootstrap/CV)就报告性能 | 未校正的性能指标虚高 | 必须使用 Bootstrap optimism correction 或 K-fold CV 校正性能指标 |
| 21 | 自愈修复后不检查方法是否被意外改变 | 自愈可能修改参数、增删协变量，导致方法偏离SAP且审计日志无法追踪变更 | 每次修复后对比方法公式、参数、效应量方向；任何变更标记 [DEVIATION] 并走SAP修正流程 |
| 22 | 审计日志记录分析代码但不记录执行环境 | 无法复现（包版本/随机种子缺失） | Phase 6审计日志必须包含: Python/R版本、包版本、随机种子、执行时间 |
| 23 | P值格式化在代码层面而非报告层面处理 | 分析代码输出应保留原始精度 | 代码输出原始P值，报告Phase按P-R01规则格式化 |
| 24 | 发表级图表使用默认matplotlib样式 | 不满足发表标准 | 必须使用shared/templates/publication_figure_template.py的apply_publication_style() |
| 25 | 加权分析后使用非加权描述统计 | 违反M-R01方法一致性 | 加权后所有分析（含描述统计）必须使用加权数据，标注"weighted" |



