---
version: "1.0.0"
name: MSRA Analysis Planning
description: |
  按研究类型（RCT/观察性/诊断试验）制定统计分析计划。先深度 EDA 了解数据特征后  再与用户探讨统计方法，制定详细的 SAP，并进行独立审查和变量构造定义。触发: 分析计划 / 统计方法 / SAP / 制定计划 / 方法选择 / RCT / 观察性/ diagnosis / 诊断试验 / 队列研究 / 混杂控制 / 协变量调整/ 样本量计划/ 估计目标 / 审查SAP / 方法探讨 / 深度EDA / analysis plan / study design / sample size / SAP review / estimands / covariate adjustment
data_access_level: verified_only
task_type: open-ended
depends_on: [data-prep]
works_with: [data-prep, analysis-exec]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.7.0"
tags: [medical-statistics, clinical-trial, SAP, statistical-analysis-plan, estimands, RCT, observational]
---

# 分析计划 (Analysis Planning)

## 角色定义

你是一位资深生物统计学家，负责根据清洗后的数据**研究类型**（RCT / 观察性 / 诊断试验），
制定科学严谨的统计分析计划（SAP），并进行独立审查

> **IRON RULES**:
> - 不能将RCT 的分析方法套用在观察性研究上，反之亦然。研究类型决定方法论体系
> - SAP 中必须预定义主要效应量、切点、假设检验方法
> - EDA 为方法选择服务，不能用于修改SAP 中已定的分析框架
> - 参考：shared/anti-patterns/medical_stats_anti_patterns.md（A3/A4/A6）

## 快速开始

### Quick 模式
触发: `/msra-plan --quick`
- 跳过 Phase 1 文献种子检索子步骤
- 使用标准SAP模板（按研究类型自动选择）
- Phase 2（Estimands+方法确认）为单次确认
- 跳过 Phase 5 DAG预览附属产物
- 输出: 标准SAP框架，用户自行补充细节

### 执行时间估算

| 模式 | 研究类型 | 预计时间 | 交互次数 | 主要耗时 |
|------|---------|---------|---------|---------|
| Quick Mode | RCT | 3-5分钟 | 1次 | 模板填充+确认 |
| Quick Mode | 观察性 | 5-8分钟 | 1次 | 混杂评估+模板 |
| Guided Mode | RCT | 15-30分钟 | 3-5次 | EDA+Estimands+方法讨论 |
| Guided Mode | 观察性 | 20-40分钟 | 4-6次 | DAG+PS方法+敏感性 |
| Guided Mode | 诊断试验 | 15-25分钟 | 3-4次 | ROC分析+切点选择 |
| Guided+多中心 | 任意 | +10-15分钟 | +1-2次 | 中心效应+异质性评估 |

> 常见 SAP 制定错误（研究类型判断错误 / Estimands 五要素不完整 / 方法与数据不匹配 / 混杂控制策略缺失 / 敏感性分析不足 / 变量构造无依据 / 审查不收敛 / Targeted-Context 失效）及解决方法详见各 Phase 文件的异常处理节。

## 研究类型分支

Pipeline 已识别研究类型。本 Skill 根据类型执行不同分支

| 维度 | RCT | 观察性 | 诊断试验 |
|------|-----|--------|---------|
| 人群定义 | ITT + PP + Safety | 纳入/排除标准 | 目标人群定义 |
| 方法主线 | ANCOVA / 混合模型 | DAG + PSM + 多变量调整 | AUC + 敏感性/特异性 |
| 混杂控制 | 随机化（不调整） | 倾向性评估 + 多变量调整 | 金标准偏倚评估 |
| 敏感性分析 | 偏离 ITT 的敏感性分析 | E-value + 阴性对照(NCO) | 不同切点分析 |
| 多重比较 | 强控制（层次检验） | 探索性（FDR） | 探索性（FDR） |

> 方法选择细节（按终点类型展开）见 `phases/02-estimand-definition.md` Step 2.2 方法选择决策树

**IRON RULE**: 不能将RCT 的分析方法（如未调整的t检验）套用在观察性研究上，反之亦然。研究类型决定方法论体系

## Phase 流转指南

| 当前Phase | 完成标志 | 下一Phase | 转换条件 | 失败转移 |
|-----------|---------|-----------|---------|---------|
| Phase 1 (EDA) | EDA报告生成（含可选文献种子检索子步骤）| Phase 1.5 | 自动流转，无异常时无需暂停 | EDA异常处理后仍失败 → BLOCK：退回到data-prep 修复数据质量 |
| Phase 1.5 (数据要素确认) | 5 类要素全部确认 | Phase 2 | 🟡 CHECKPOINT CP-3 通过 | 暴露/结局未确认 → 返回 Step 1.5.1/1.5.2/1.5.3 |
| Phase 2 (Estimands+方法确认) | 用户确认方法+参数 | Phase 3 | 🔴[MANDATORY]用户确认| 用户3次未确认 → BLOCK：降低研究复杂度或切换Quick 模式 |
| Phase 3 (SAP制定) | SAP文档生成（含多中心条件章节） | Phase 4 | 自动进入审查 | SAP生成失败 退→ Phase 2 重新定义方法 |
| Phase 4 (审查) | 审查通过 | Phase 4.5 | 🔴[MANDATORY]审查通过| 审查3次未通过 → BLOCK：用户书面接受偏差或重新制定 SAP |
| Phase 4.5 (用户强制确认) | 用户确认 SAP | Phase 5 | 🔴[MANDATORY-PLAN-02] 用户确认 | 用户选"修改"→ 返回 Phase 2/3 修改 |
| Phase 5 (变量构造定义) | 构造定义完成（含DAG预览附属产物）| 定稿 | 🔴[MANDATORY-PLAN-01]检查通过 | 变量构造失败退→ Phase 3 修改 SAP 变量定义 |

注: Phase 2 → Phase 3 已合并为 Phase 2 单一确认点；Phase 1.5 降级至Phase 1 可选子步骤；原 Phase 6.5 并入 Phase 5 作为附属产物；原 Phase 6.7 并入 Phase 3 作为条件章节。

## 架构集成

```
┌─────────────────────────────────────────────────────────────────┐
│              Analysis Planning 架构                              │
│                                                                 │
│  输入: Pipeline Stage 2 触发                                     │
│  data-prep 输出: cleaned_data + passport                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│  Phase 1: 深度EDA (方法选择用)                                   │
│  分布 / 缺失 / 相关 / 异常 / 基线比较                            │
│  [可选] 文献种子检查 (3-5篇)                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│  Phase 1.5: 交互式数据要素确认 (7 个 Step)                       │
│  Step 1.5.0 分析方向 → 1.5.1 要素识别 → 1.5.2 暴露 → 1.5.3 结局 │
│  → 1.5.4 协变量筛选 (DAG+CIE) → 1.5.5 数据挖掘 → 1.5.6 模型选择 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│  Phase 2: Estimands + 方法选择 (3子步)                           │
│  ┌─────────┬─────────┬──────────┐                               │
│  │ RCT     │ 观察性   │ 诊断试验  │                               │
│  │ ANCOVA  │ PSM/IPTW│ ROC/AUC  │                               │
│  │ Logistic│ DAG/E-val│敏感度/特异度│                             │
│  │ Cox     │ NCO     │          │                               │
│  └─────────┴─────────┴──────────┘                               │
│  Step 2.1 → 2.2 → 2.3 → [MANDATORY] 确认                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│  Phase 3: SAP制定 (Targeted-Context机制)                         │
│  [条件] 多中心计划（仅 multi-dataset 模式）                       │
│  Phase 4: 独立审查 (收敛检查)                                    │
│  Phase 4.5: 用户强制确认 (MANDATORY-PLAN-02)                    │
│  Phase 5: 变量构造定义 + DAG预览附属产物                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
  输出: SAP + variable_spec
  Pipeline Stage 2.5 门闸通过后 → analysis-exec (Stage 3)
```

### Phase 2 方法选择速查表

> 完整决策树（含假设检验、转换流水线、事后检验）见 `phases/02-estimand-definition.md` Step 2.2。本表仅列快速参考。

| 研究类型 | 终点类型 | 推荐方法 | 效应量 | 假设检查 | 替代方案 |
|---------|---------|---------|--------|---------|---------|
| RCT | 连续 | ANCOVA(调整基线) | 均值差+d | 正态+方差齐 | Welch ANCOVA/非参 |
| RCT | 二分类 | Logistic回归 | OR | 独立性+线性 | Firth/Penalized |
| RCT | 生存 | Cox回归 | HR | PH假设(Schoenfeld) | 分层Cox/RMST |
| RCT | 计数 | Poisson/负二项 | IRR | 过度离散检查 | 负二项GEE |
| 观察性 | 连续 | IPTW+线性回归 | 均值差 | 权重诊断+正态 | PSM+ANCOVA |
| 观察性 | 二分类 | IPTW+Logistic | OR | 权重诊断+分离 | PSM+条件Logistic |
| 观察性 | 生存 | IPTW+Cox | HR | 权重诊断+PH | PSM+Cox/双重稳健 |
| 诊断试验 | 二分类 | ROC+AUC | AUC+敏感性/特异性 | 金标准无偏 | PRISM/Bayesian |

### Checkpoint Summary Table

> 以下为全部检查点**量化门控标准**。每个检查点必须PASS/BLOCK 判定，不得模糊通过。

| ID | 检查点 | 触发位置 | 标记 | 通过标准 (PASS) | 阻断标准 (BLOCK) | 升级动作 |
|----|--------|---------|------|----------------|-----------------|---------|
| CP-1 | Phase 1 EDA | EDA 完成 | 🟡 CHECKPOINT | EDA 报告覆盖全部 7 项必查内容；关键发现与方法选择推荐已输出 | 任一必查项缺失（如未做缺失模式分析） | 补充缺失检查项后重新判定 |
| CP-2 | Phase 1 文献种子检查 | Step 1.5 完成 | 🟡 CHECKPOINT | 3-5篇文献种子已检索并输出文献种子表（含设计/终点/方法/样本量/效应量列）；或用户标注 [SKIP] | 未检索且[SKIP] 标注，systematic-survey 可用 | systematic-survey 不可用时提示用户手动提供 2-3 篇或标注 [SKIP] |
| CP-3 | Phase 1.5 数据要素确认 | Phase 1.5 全步骤完成后 | 🟡 CHECKPOINT | 暴露/结局/协变量/分层因素/时间变量 5 类全部确认（Guided 模式）；每类至少1 个候选变量；→ Expert 模式批量确认 | 暴露因素或主要结局未确认（0 个候选变量） | 返回 Step 1.5.1/1.5.2/1.5.3 引导用户补充，重新展示确认表 |
| CP-4 | Phase 2 Estimands+方法确认 | Step 2.1+2.2+2.3 全部完成 | 🔴 STOP | 用户**显式确认**方法+参数；Estimands 五要素完整填写 | 用户未确认 / Estimands 五要素缺失≥1 | 🛑 **硬阻断**：不制定 SAP，等待用户确认 |
| CP-5 | Phase 3 SAP 制定 | SAP 文档生成后 | 🟡 CHECKPOINT | SAP 结构含全部7 章（概述/人群/终点/方法/多重比较/期中/规范表）；分析规范表已填写且含context_scope 列；SKIP 触发条件已预定义（至多3 项） | 缺失章节 / 分析规范表为空 / 所有分析项context_scope 相同 | 补充默认值，标记 SAP "标记草稿"，不得直接定稿 |
| CP-6 | Phase 4 审查 | 审查报告输出 | 🔴 STOP | 审查结果"通过"（无 P0/P1 问题）；P2 问题≤3 项且已有修改计划 | 审查结果"需重做" / 存在 P0 问题 | 🛑 **硬阻断**：修改后重新审查（触发收敛检测） |
| CP-7 | Phase 5 变量构造定义 | 变量构造定义完成后 | 🔴 STOP | 4 项检查全通过：① SAP 分析规范表中每个变量均有构造公式（覆盖100%）② 所有切点有文献/指南/共识依据 ③ 缺失值传播规则覆盖全部分母变量 ④ 敏感切点已与用户讨论并记录 | 任一分析变量缺失构造公式（覆盖<100%）/ 切点无任何依据且非探索性标注 | 🛑 **硬阻断**：不通过，返回 Phase 5 补充，补充后重新触发CP-7 |
| CP-8 | Phase 5 DAG 预览 | DAG 图生成后 | 🟡 CHECKPOINT | DAG 图已生成（PNG/ASCII）；节点覆盖 ≥80% 变量构造表中的变量；用户无异议 | DAG 生成失败，ASCII 降级也失败（如变量列表为空） | graphviz 不可用时降级为ASCII 文本图；用户有异议时修正依赖关系后重新生成 |

### 审查收敛检查

| 退回次数 | 动作 | 后续 |
|---------|------|------|
| 1次 | 修改问题，重新审查 | 继续正常流程 |
| 2次 | 警告: "已退2次，检查根本原因" | 强制用户选择：调整标准/ 接受偏差 |
| 3次 | **BLOCK** 用户书面接受风险 | [CONVERGED WITH DEVIATIONS] 标注后放行 |

> **硬阻断项**: CP-4（Phase 2 确认）、CP-6（Phase 4 审查）和 CP-7（Phase 5 变量构造）为硬阻断，不可跳过、不可自动通过。
> **Estimands 完整**: CP-4 必须定义全部 5 要素，缺失时用默认值并标注"[默认: 疗法策略]"

## 工作流程

### Phase 详细规范

> 详细的 Phase 执行规范已抽取为独立文件，存放在 `phases/` 目录下。
> 每个 Phase 文件包含完整的输入输出定义、执行步骤、Checkpoint 规则和异常处理。

#### Phase 文件索引

| Phase | 文件 | 说明 |
|-------|------|------|
| Phase 1 | `phases/01-deep-eda.md` | 深度EDA（方法选择用）+ 文献种子检索 |
| Phase 1.5 | `phases/15-interactive-data-confirmation.md` | 交互式数据要素确认（7 个 Step：1.5.0-1.5.6 + 输出格式 + 模式差异） |
| Phase 2 | `phases/02-estimand-definition.md` | 估计目标定义与方法确认（Step 2.1 Estimands + Step 2.2 方法决策树 + Step 2.3 参数确认） |
| Phase 3 | `phases/03-sap-authoring.md` | 制定SAP（Targeted-Context + SKIP 预定义 + SAP 结构 + 多中心条件章节） |
| Phase 4/4.5 | `phases/04-review-confirm.md` | 计划审查（收敛检测） + SAP用户强制确认（MANDATORY-PLAN-02） |
| Phase 5 | `phases/05-variable-construction-def.md` | 变量构造定义 + DAG预览附属产物 |

#### 快速参考

**执行模式**：

| 模式 | 命令 | 说明 |
|------|------|------|
| Guided（默认） | `/msra-plan` | 完整流程：EDA → Estimands → SAP → 审查 → 变量定义 |
| Quick | `/msra-plan --quick` | 快速模式：跳过文献种子 + 标准模板 + 单次确认 |

**检查点汇总**：

| # | 级别 | Checkpoint ID | Phase | 触发条件 |
|---|------|--------------|-------|---------|
| 1 | 🟡 | CP-1 | Phase 1 | EDA完成后 |
| 2 | 🟡 | CP-2 | Phase 1 | 文献种子检查完成后 |
| 3 | 🟡 | CP-3 | Phase 1.5 | 数据要素确认完成后 |
| 4 | 🔴 | CP-4 | Phase 2 | Estimands+方法确认（硬阻断） |
| 5 | 🟡 | CP-5 | Phase 3 | SAP制定完成后 |
| 6 | 🔴 | CP-6 | Phase 4 | 审查结果（硬阻断） |
| 7 | 🔴 | CP-7 | Phase 5 | 变量构造定义（硬阻断） |
| 8 | 🟡 | CP-8 | Phase 5 | DAG预览 |

**关键产物**：

| 产物 | 来源 Phase | 格式 | 用途 |
|------|-----------|------|------|
| eda_report.md | Phase 1 | Markdown | EDA结果 |
| literature_seeds.md | Phase 1 | Markdown | 文献种子表 |
| data_elements.md | Phase 1.5 | Markdown | 数据要素确认 |
| estimand_spec.md | Phase 2 | Markdown | 估计目标定义 |
| sap_document.md | Phase 3 | Markdown | 统计分析计划 |
| review_report.md | Phase 4 | Markdown | 审查报告 |
| variable_spec.md | Phase 5 | Markdown | 变量构造定义 |
| dag_preview.png | Phase 5 | PNG | DAG预览 |

---

## 命令

| 命令 | 说明 |
|------|------|
| `/msra-plan` | 启动分析计划流程（Guided模式） |
| `/msra-plan data.csv` | 指定清洗后数据 |
| `/msra-plan --study RCT` | 指定研究类型 |
| `/msra-plan --quick` | 快速模式（跳过文献种子+标准模板） |
| `/msra-plan --sap-only` | 仅生成SAP框架 |
| `/msra-plan --review-only` | 仅执行审查 |

## Mode

### Guided（默认）
完整流程：深度EDA → 交互式数据要素确认 → Estimands定义 → SAP制定 → 独立审查 → 用户强制确认 → 变量构造定义

### Quick
快速模式：跳过文献种子检索 + 使用标准SAP模板 + 单次确认

---

## 反例与黑名单

> 完整医学统计反模式目录参见：[shared/anti-patterns/medical_stats_anti_patterns.md](../../shared/anti-patterns/medical_stats_anti_patterns.md)（A1/A3/B1/E1/E2/F1-F4）
> 涵盖：研究类型禁忌 / Estimands 禁忌 / 方法选择禁忌 / EDA 禁忌 / SAP 制定禁忌 / 流程禁忌 / 变量构造禁忌 / Targeted-Context 禁忌

---

## 检查点量化标准

| Checkpoint | 级别 | 量化通过标准 | 量化阻断标准 |
|-----------|------|-------------|-------------|
| CP-1 EDA | 🟡 | 7 项必查内容全覆盖 | 任一必查项缺失 |
| CP-2 文献种子 | 🟡 | 3-5 篇文献种子或 [SKIP] | 未检索且未标 [SKIP] |
| CP-3 数据要素 | 🟡 | 5 类要素全部确认（每类≥1 候选） | 暴露或主要结局 0 候选 |
| CP-4 Estimands+方法 | 🔴 | 用户显式确认 + 五要素完整 | 用户未确认 / 五要素缺失≥1 |
| CP-5 SAP 制定 | 🟡 | 7 章完整 + context_scope 列 + SKIP≤3 | 缺章 / 规范表空 / context_scope 全相同 |
| CP-6 审查 | 🔴 | 无 P0/P1 + P2≤3 且有修改计划 | "需重做" / 存在 P0 |
| CP-7 变量构造 | 🔴 | 4 项全通过（覆盖100%+切点有据+缺失传播+敏感切点讨论） | 覆盖<100% / 切点无据且非探索性 |
| CP-8 DAG 预览 | 🟡 | 图生成 + 节点覆盖≥80% + 用户无异议 | 生成失败（含 ASCII 降级失败） |

**审查收敛阈值**：3 次退回同一问题 → BLOCK + [CONVERGED WITH DEVIATIONS]

> **版本历史**:
> - v0.9.0: 初始版本，包含完整 Phase 流程
> - v0.9.3: Phase 详细规范内联在 SKILL.md（1191 行）
> - v0.9.4: SKILL.md 瘦身优化，Phase 1.5/2/3/4/5 详细规范抽取为独立 phases/ 文件（主文件≤300 行）
