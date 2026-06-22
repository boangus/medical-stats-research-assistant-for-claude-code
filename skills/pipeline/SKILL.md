---
version: "0.9.0"
name: MSRA Pipeline
description: |
  医学统计分析 + 学术写作统一流水线编排器。从任意阶段切入，自动识别当前位置，
  引导完成后续所有流程。Stage 4 完成后可选择继续 Paper Track（论文写作）9  纯调度架构——不做实质性工作，只负责检测、选择、调度、转换和追踪9  输出: 完整流水线（Stage 1-4 统计分析 + Stage 5-6 论文写作9 3个阻断式门闸
  + 最终报9figures/*.png + tables/*.docx + HTML+MD) + 可选论文9  触发: /msra / 流水9/ pipeline / 数据分析流程 / 统计流程 / 完整流程 / 从头开9/ 数据清洗 / 统计分析 / 分析报告 / 结果解读 / 统计咨询 / orchestrator / 编排 / 调度 / 质量门闸
data_access_level: redacted
task_type: open-ended
depends_on: [data-prep, exploratory-causal, analysis-plan, analysis-exec, report, calibration, peer-review, systematic-survey]
works_with: [agents/AGENTS.md, shared/passport/passport_schema.md, .claude/CLAUDE.md]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.5"
tags: [medical-statistics, clinical-trial, pipeline, orchestrator, quality-gate]
---

# MSRA Pipeline Orchestrator

> **IRON RULE**: You are an orchestrator, NOT a worker. You do NOT perform
> substantive statistical work yourself. Your only job is to detect where the
> user is, recommend the right skill/mode, dispatch, and track progress.

---

## 1. Pipeline Stages

```
原始数据 9研究类型识别（RCT / 观察性）
   9   9┌──────────────────────────────────────────────────────────────99 Stage 1: DATA PREP  (/msra-data)                            99 数据验证 9交互式清99执行清洗 9值规范化 9EDA(数据质量)  99 9盲态审核9数据库锁9                                    99 [RCT] 启用盲法审核 / [观察性] 启用混杂评估                  99 值规范化: TCM术语变体(GB/T 16751)+数值格式变体[ADAPTIVE]    9└────────────────────────────┬─────────────────────────────────9                             9┌──────────────────────────────────────────────────────────────99 🔴 Stage 1.5: DATA QUALITY GATE  (阻断式检查               99 9 项检查9❌退9Stage 1 / ✅进9Stage 1.8                9└────────────────────────────┬─────────────────────────────────9                             9┌──────────────────────────────────────────────────────────────99 Stage 1.8: EXPLORATORY CAUSAL  (/msra-explore)              99 变量分类 9关联结构探索 9因果发现(PC/FCI)                  99 9混杂/中介/碰撞识别 9假设生成 9研究方向报告              99 [可选] 无先验假设时执行 / 有明确SAP时可跳过                  9└────────────────────────────┬─────────────────────────────────9                             9┌──────────────────────────────────────────────────────────────99 Stage 2: ANALYSIS PLAN  (/msra-plan)                        99 Estimands(估计目标) 9方法探讨 9SAP 9审查 9变量构造定9 99 [RCT] ITT/PP 人群 + ANCOVA 为主                             99 [观察性] DAG/混杂控制 + PSM/多变量为9                     9└────────────────────────────┬─────────────────────────────────9                             9┌──────────────────────────────────────────────────────────────99 🔴 Stage 2.5: SAP QUALITY GATE  (阻断式检查                99 + 变量构造逻辑检查（确保 SAP 中分析变量的构造逻辑已定义）     99 ❌退9Stage 2 / ✅进9Stage 3                             9└────────────────────────────┬─────────────────────────────────9                             9┌──────────────────────────────────────────────────────────────99 Stage 3: ANALYSIS EXEC  (/msra-exec)                        99 样本量验99变量构9按SAP) 9执行前检查                   99 9描述性统9Table 1) 9依从性分99安全性分9            99 9主要分析 9敏感性分99亚组分析 9假设检查9质检        9└────────────────────────────┬─────────────────────────────────9                             9┌──────────────────────────────────────────────────────────────99 🔴 Stage 3.5: RESULTS QUALITY GATE  (阻断式检查            99 14 项检查9❌退9Stage 3 / ✅进9Stage 4                  9└────────────────────────────┬─────────────────────────────────9                             9┌──────────────────────────────────────────────────────────────99 Stage 4: REPORT  (/msra-report)                             99 结果解读 9表格/图表 9方法学描99统计质量检查9报告组装   99 输出: final_report.md + final_report.html + figures/*.svg   99       + figures/*.png + tables/*.docx                        99 9STAGE 4 CHECKPOINT: [A] 结束 / [B] Paper Track            9└────────────────────────────┬─────────────────────────────────9                             9          ┌────────────────────────────────────────────9          99STAGE 4 CHECKPOINT (MANDATORY-GATE-05)   9          9[A] 统计报告完成，结99track=report_only  9          9[B] 继续写论99Paper Track               9          9    守卫检查 final_report + figures/tables 9          └───────┬──────────────────┬────────────────9                  9                 9            [A] 9                   9[B]
         ════════════9     ┌─────────────────────────────────9         9 Pipeline 结束   9 Stage 5.0: PAPER INTAKE        9         9 (report_only)   9 Handoff Bundle + 论文配置      9         ════════════9     └──────────────┬──────────────────9                                           9                            ┌─────────────────────────────────9                            9 Stage 5.1: LITERATURE SEARCH   9                            9 文献检查+ 综述撰写            9                            └──────────────┬──────────────────9                                           9                            ┌─────────────────────────────────9                            9 Stage 5.2: PAPER WRITING       9                            9 IMRaD 章节撰写                 9                            └──────────────┬──────────────────9                                           9                            ┌─────────────────────────────────9                            9 🔴 Stage 5.5: INTEGRITY CHECK  9                            9 完整性检查（阻断式）            9                            └──────────────┬──────────────────9                                           9                            ┌─────────────────────────────────9                            9 Stage 5.6: PEER REVIEW         9                            9 5人评审团                     9                            └──────────────┬──────────────────9                                           9                            ┌─────────────────────────────────9                            9 Stage 5.7: REVISION            9                            9 修订 + Response to Reviewers   9                            └──────────────┬──────────────────9                                           9                            ┌─────────────────────────────────9                            9 Stage 5.8: FINAL INTEGRITY     9                            9 最终完整性检查（阻断式）        9                            └──────────────┬──────────────────9                                           9                            ┌─────────────────────────────────9                            9 Stage 5.9: FINALIZE            9                            9 定稿导出（MD 9DOCX 9PDF9    9                            └──────────────┬──────────────────9                                           9                            ┌─────────────────────────────────9                            9 Stage 6: PROCESS SUMMARY       9                            9 完整过程记录                    9                            └─────────────────────────────────9```

---

## 2. Intent Detection & Mid-Entry

当用户发起对话时，通过关键词和上下文自动判断入口阶段：

| 用户信号 | 检测规9| 入口阶段 | 前置条件 |
|---------|---------|---------|---------|
| "我有原始数据" / 提供数据文件 | 有数据文件路9| **Stage 1** | 9|
| "我想研究 X 9Y 的影9 / 已知暴露+结局 | 用户明确暴露和结局 | **Stage 2** | 需确认 Stage 1.5 门闸通过；引导用户输入暴9结局/研究类型/已知协变9|
| "帮我看看数据里有什么值得研究9 / 不确定研究方法| 探索性意9| **Stage 1.8** | 需确认 Stage 1.5 门闸通过 |
| "我想探索数据中的因果关系" / "做探索性分9 | 因果探索意图 | **Stage 1.8** | 需确认 Stage 1.5 门闸通过 |
| "我想讨论统计方法" / "该用什么方法 | 方法咨询意图 | **Stage 2** | 需确认 Stage 1.5 门闸通过 |
| "我有分析计划9 / 提供SAP文件 | 有SAP文档 | **Stage 3** | 需审查SAP |
| "分析做完了，帮我检查 | 有分析结9| **Stage 3** (质检) | 需确认SAP |
| "帮我写报9 / "生成表格" | 报告生成意图 | **Stage 4** | 需确认分析结果 |
| "完整流程" / "从头开9 | 全流程意9| **Stage 1** | 9|
| "继续写论9 / "paper track" | Paper Track 意图 | **Stage 5.0** | 需确认 Stage 4 已完9+ passport.track == full_paper |
| 提供论文要求review | 审稿意图 | **Stage 3** (质检) | 需先验证数据完整9|

### Mid-Entry 前置检查
进入任何阶段前，必须确认前置产物是否存在且有效9使用 **Material Passport** (shared/passport/passport_schema.md) 追踪产物生命周期9
```
进入 Stage 1.5 之前  9确认: 清洗后数9+ 清洗日志 + 盲态审核记9+ 数据库锁定记9进入 Stage 2 之前     9确认: 清洗后数9+ 清洗日志 + Stage 1.5 门闸通过
进入 Stage 2.5 之前   9确认: 已批准的SAP
进入 Stage 3 之前     9确认: Stage 2.5 通过 + 已批准的SAP
进入 Stage 3.5 之前   9确认: 分析结果 + 质检报告
进入 Stage 4 之前     9确认: Stage 3.5 通过 + 分析结果
```

**Passport 检查流9*91. 读取 `MSRA/passport.json`，检查各产物状92. 产物状9 `planned` 9`in_progress` 9`completed` 9`verified` 9`consumed`
3. 前置产物必须9`verified` 9`consumed` 才允许进入下一阶段
4. 9passport.json 不存在，提示用户初始化或从现有产物重9
**IRON RULE**: 如果前置产物缺失或过期，必须先回退补齐，不能跳过9
---

## 2.1 研究类型识别

在确定入口阶段后，自动识别或询问研究类型。后续所9Stage 按类型分支执行不同逻辑9
| 用户信号 | 检测规9| 研究类型 |
|---------|---------|---------|
| "RCT" / "随机对照" / "randomized" / "随机" | 关键词匹9| **RCT** |
| "队列" / "cohort" / "观察9 / "observational" | 关键词匹9| **观察9* |
| "病例对照" / "case-control" | 关键词匹9| **观察9* |
| "诊断" / "diagnostic" / "诊断试验" | 关键词匹9| **诊断试验** |
| 未明确说9| 询问用户 | 由用户指9|

**研究类型9Pipeline 的影9*9
| 维度 | RCT | 观察9| 诊断试验 |
|------|-----|--------|---------|
| 数据准备 | 启用盲态审核| 启用混杂偏倚评价| 启用金标准验9|
| 分析计划 | ITT/PP 人群、ANCOVA 为主 | DAG/PSM/多变量调9| AUC/敏感9特异9|
| 质量门闸 | 检查随机化隐藏 | 检查混杂控9| 检查金标准偏9|
| 报告规范 | CONSORT | STROBE | STARD |
| 敏感性分9| 偏离 ITT 的敏感9| E-value / 未测量混9| 不同切点的分9|

**入口响应格式**（研究类型识9+ 交互模式 + 语言选择后输出）9```
── Pipeline Orchestrator ──
检测到: 研究类型=RCT | 入口=Stage 1 (原始数据)
前置检查 无前置产物，9Stage 1 开9
交互模式: [1] 详细引导 [2] 高效模式
分析语言: [1] R (推荐) [2] Python

输入编号或描述需9
```

---

## 2.2 操作模式选择 (Operation Mode Selection)

> **目的**：根据用户经验和需求，提供引导模式与专家模式的无缝切换9> **触发时机**：Pipeline 启动时自动询问，或用户通过参数指定
> **核心原则**：两种模式下的分析结果一致性与准确性不受影9
### 2.2.1 模式定义

| 维度 | 引导模式 (Guided) | 专家模式 (Expert) |
|------|-------------------|------------------|
| **目标用户** | 首次使用/不熟悉统计分析流程的用户 | 熟悉系统、有统计分析经验的用9|
| **交互深度** | 分步骤详细指引，每步单独确认 | 批量操作，减少不必要交互 |
| **概念解释** | 显示每个术语的含义、参数说明、决策建9| 仅显示操作选项，不显示概念解释 |
| **默认9* | 提供推荐默认值并说明理由 | 提供默认值但不解9|
| **错误处理** | 详细解释错误原因和修复建9| 简洁错误信9修复选项 |
| **跳过选项** | 不允许跳过关键步9| 可跳过非关键步骤 |
| **快捷操作** | 9| 支持快捷键和批量操作 |

### 2.2.2 模式选择入口

Pipeline 启动时显示：

```
── MSRA Pipeline 启动 ──
检测到: 研究类型={RCT/观察9诊断} | 入口={Stage N}

选择操作模式:
  [1] 引导模式 (Guided) 9分步骤详细指引，含概念解释和决策建议
  [2] 专家模式 (Expert) 9快速操作，减少交互，支持批量处9
输入编号 (默认: 1):
```

**模式持久9*：用户选择的模式记录在 passport.json 中，后续阶段自动继承9```json
{
  "operation_mode": "guided"  // 9"expert"
}
```

**模式切换**：用户可随时通过以下方式切换9- 输入 `/mode guided` 9`/mode expert`
- 在任9Checkpoint 选择"切换模式"

### 2.2.3 各阶段模式差9
#### Stage 1: 数据准备

| 步骤 | 引导模式 | 专家模式 |
|------|---------|---------|
| 数据验证 | 逐项展示验证结果，解释每项含9| 汇总展示，仅标记异常项 |
| 清洗策略 | 逐步引导：先缺失→再异常→最后逻辑 | 一次性展示全部清洗建议，批量确认 |
| 值规范化 | 解释每种变体类型和规范化规则 | 仅展示变体数量和规范化结9|
| EDA报告 | 逐节解读EDA结果，解释统计含9| 直接输出完整EDA报告 |
| 盲态审核| 详细解释审核流程和判定标9| 直接执行审核，输出结9|
| 数据库锁9| 解释锁定含义和不可逆9| 直接锁定，输出确9|

#### Stage 2: 分析计划

| 步骤 | 引导模式 | 专家模式 |
|------|---------|---------|
| 数据要素确认 | 逐项确认暴露/结局/协变量，含概念解9| 一次性展示全部要素，批量确认 |
| Estimands | 解释5个属性的含义和选择依据 | 仅展示属性表格，用户填写 |
| 方法选择 | 展示决策树，解释每种方法的适用场景和优9| 直接推荐方法，用户确认或修改 |
| SAP制定 | 分章节制定，每章确认后继9| 使用模板快速生成，一次性确9|
| SAP审查 | 逐项解释审查结果和修改建9| 汇总展示审查结果，批量修改 |

#### Stage 3: 分析执行

| 步骤 | 引导模式 | 专家模式 |
|------|---------|---------|
| 代码生成 | 逐段生成代码，解释每段功9| 一次性生成全部代9|
| 执行监控 | 实时展示执行进度和中间结9| 仅展示最终结果和错误 |
| 结果解读 | 逐表逐图解读，解释统计含9| 直接输出全部结果 |
| 质量检查| 逐项展示检查结果，解释异常 | 汇总展示，仅标记异9|

#### Stage 4: 报告生成

| 步骤 | 引导模式 | 专家模式 |
|------|---------|---------|
| 结果解读 | 逐项解读主要/次要/安全性结9| 汇总展示关键发9|
| 表格图表 | 逐表逐图确认格式和内9| 批量生成，一次性确9|
| 方法学描9| 逐步引导撰写方法学段9| 使用模板快速生9|
| 报告组装 | 分章节确认后组装 | 一次性组装完整报9|

### 2.2.4 引导模式特色功能

#### 概念解释气泡

在引导模式下，关键术语旁显示概念解释9
```
── Estimands 确认 ──
💡 Estimands（估计目标）: 描述治疗效果的精确框架，包含5个属性9
| 属9| 含义 | 你的选择 |
|------|------|---------|
| 治疗 (Treatment) | 比较的干9vs 对照 | [{选择}] |
| 人群 (Population) | 目标研究人群 | [{选择}] |
| 变量 (Variable) | 感兴趣的结局指标 | [{选择}] |
| 间发事件 (Intercurrent Events) | 可能影响结局的后续事9| [{选择}] |
💡 间发事件: 如退出、抢救治疗、死亡等，需要选择处理策略
| 汇9(Summary) | 人群层面的效果度9| [{选择}] |

需要解释某个属9 输入属性名9
```

#### 决策建议引擎

在引导模式下，每个关键决策点提供推荐和理由：

```
── 方法选择 ──
💡 推荐: ANCOVA（调整基线HbA1c9理由:
  1. RCT连续终点，ANCOVA是标准方法  2. 调整基线可提高效能（减少方差90%9  3. 满足正态性假设（Shapiro-Wilk p=0.459  4. 满足方差齐性（Levene p=0.629
替代方案:
  - 混合效应模型（如有纵向数据）
  - Wilcoxon秩和（如不满足正态性）

选择: [使用推荐 / 选择替代 / 自定义]
```

#### 参数说明面板

在引导模式下，每个参数提供详细说明：

```
── 样本量计9──
💡 参数说明:
  - α (显著性水9: 控制假阳性率，通常9.05
    9含义: 9%的概率在无效时错误地声明有效
  - Power (检验效9: 控制假阴性率，通常9.80
    9含义: 90%的概率在有效时正确地声明有效
  - 效应9 预期的治疗效果大9    9来源: 文献/预实9MCID
  - 失访9 预计丢失的受试者比9    9建议: 通常90-20%

当前参数: α=0.05, Power=0.80, 效应90.3, 失访915%
计算结果: 需9N=200 9
调整参数? [α / Power / 效应9/ 失访9/ 确认]
```

### 2.2.5 专家模式特色功能

#### 批量操作

在专家模式下，支持批量确认和编辑9
```
── 专家模式: 批量确认 ──
数据要素:
  [x] 暴露: treatment (二分9
  [x] 主结局: hba1c_change (连续)
  [x] 协变9 age, sex, bmi, baseline_hba1c
  [x] 分层: center_id
  [x] 时间: follow_up_days

分析计划:
  [x] 主分9 ANCOVA(调整baseline_hba1c)
  [x] 敏感9 MI + Tipping Point
  [x] 亚组: age(<65/95), sex

全部确认? [Y/n/编辑]
```

#### 快捷命令

| 快捷命令 | 功能 | 等价操作 |
|---------|------|---------|
| `/quick` | 切换到专家模9Quick模式 | `/mode expert` + 跳过非关键步9|
| `/guided` | 切换到引导模9| `/mode guided` |
| `/accept-all` | 批量确认所有推9| 逐项确认的快捷方法|
| `/skip-eda` | 跳过EDA详细展示 | 仅输出EDA摘要 |
| `/template` | 使用标准模板快速生成SAP | 跳过方法讨论，直接用模板 |
| `/batch` | 批量执行多个分析 | 逐个执行的快捷方法|

#### 精简输出

专家模式下，输出精简为关键信息：

```
── Stage 2 完成 ──
SAP: approved 9| 方法: ANCOVA+MI | 亚组: 29| 敏感9 39变量: 129强制4+建议5+排除3) | 门闸: PASS(8/8)
9Stage 3 [继续]
```

### 2.2.6 模式一致性保9
**IRON RULE**: 两种模式下的分析结果必须完全一致9
| 保证措施 | 说明 |
|---------|------|
| 相同的统计方法| 模式只影响交互方式，不影响方法选择 |
| 相同的参数默认9| 两种模式使用相同的默认参9|
| 相同的质量门9| 门闸检查标准不因模式而异 |
| 相同的产物格9| 输出文件格式和内容完全一9|
| 模式切换可追9| passport.json 记录模式切换历史 |

### 2.2.7 模式与Quick模式的关9
| 维度 | 引导模式 | 专家模式 | Quick模式 |
|------|---------|---------|----------|
| 交互深度 | 最9| 最9| 最9|
| 概念解释 | 9| 9| 9|
| 步骤跳过 | 不允9| 允许非关9| 允许大部9|
| 模板使用 | 不使9| 可9| 强制使用 |
| 适用场景 | 学习/首次使用 | 日常分析 | 快速出结果 |

> Quick模式是专家模式的子集，额外跳过文献检索、DAG预览等附属产物9
---

## 2.5 用户类型与交互密度预9
在确定入口阶段后，询问用户期望的交互密度。此后按对应模式自动调整 Checkpoint 密度，无需每个决策点都问一遍9
**入口处提9*9```
选择交互模式9
[1] 详细引导
    每个关键步骤都会暂停与你确认：数据清洗策略、变量筛选、参数定义9    方法选择、协变量调整、敏感性分析等，全部在对话中逐一讨论9    适合：首次分析、对统计方法不熟、数据质量不确定、需要严格把控9
[2] 高效模式（推荐）
    全程自动推进，仅在质量门闸（6个阻断点）暂停9    统计参数直接使用默认值，方法选择基于数据特征自动推荐9    如需修改，可9SAP 文档中调整后重新生成9    适合：熟悉流程、标准分析、赶时间9```

| 用户选择 | Checkpoint 密度 | 适用场景 |
|---------|----------------|---------|
| **[1] 详细引导** | MANDATORY + SLIM + 协作深度观察 | 首次分析、对统计方法不熟、数据质量不确定、需要严格把9|
| **[2] 高效模式** (默认) | MANDATORY 仅门闸暂停，其余自动推进 | 熟悉流程、标准分析、赶时间 |

**模式内行9*9- 详细引导：每个决策点暂停，展示选项供用户选择
- 高效模式：使用默认参数自动推进，仅在异常时提9- 用户可在 SAP 文档中修改参数后，说"重新执行"即可
- 用户9继续吧别问太9 9切换至高效模9- 用户9这块你定就行" 99Checkpoint 降级为仅记录，不询问

---

## 2.6 分析语言选择

在确定交互模式后，询问用户期望的分析语言。此后全程使用该语言生成代码、执行分析和输出结果9
**入口处提9*9```
选择分析语言9
[1] R (推荐)
    使用 R 语言进行统计分析9    优势：统计方法丰富、医学统计生态成熟、gtsummary/flextable 生成三线表9          survival 包做生存分析、WeightIt 做因果推断9    适合：临床研究、生存分析、因果推断、需要专业统计包9
[2] Python
    使用 Python 语言进行统计分析9    优势：机器学习生态强大、Pandas 数据处理灵活、Plotly 交互式可视化9    适合：大数据分析、机器学习、需要与其他 Python 工具链集成9```

| 用户选择 | 默认9| 适用场景 |
|---------|--------|---------|
| **[1] R** (默认) | survival, survey, WeightIt, gtsummary, flextable | 临床研究、生存分析、因果推9|
| **[2] Python** | pandas, numpy, scipy, scikit-learn, lifelines | 大数据、机器学习、Python 工具9|

**语言影响**9- **Stage 3**: 生成对应语言的分析代9- **Stage 4**: 使用对应语言的包生成表格和图9- **模板**: 使用 `shared/templates/` 下对应的语言模板

---

## 3. Stage Dispatching

每个 Stage 调用对应9Skill，并选择最9Mode9
### Stage 1: DATA PREP
- **Skill**: `data-prep`
- **Mode 匹配**:
  - 用户9帮我清洗数据" 9`guided` (交互9
  - 用户9快速检查一9 9`quick` (快速验9
- **研究类型分支**:
  - RCT 9启用盲态审核、随机化检查  - 观察99启用混杂偏倚评估、数据源描述
- **输入**: 原始数据文件路径（单文件或多文件目录9- **输出**: 清洗后数9+ 清洗日志 + EDA报告(数据质量) + 验证报告 + 盲态审核记9+ 数据库锁定记9- **🆕 多数据集模式**: 输入为目录（含多9CSV）时自动进入 multi-dataset 模式，逐文件验9+ 跨中心一致性检查（Phase 1b9- **子步9*:

  □ 0. **数据画像**（Quick Profile）：自动生成数据概览——变量数、样本量、变量类型分布、缺失率排名 Top10、数值变量概要（min/max/mean/median/sd）、分类变量层级数、时间跨度。[SLIM] 展示后继续（极端情况如缺失率>50%或变量数<3 时升级为 MANDATORY）9
  □ 0.5. **多数据集检查*（仅目录输入时）：自动检测多中心数据，激9multi-dataset 模式

  □ 1. 数据验证（结构、类型、缺失、逻辑、范围）
  1b. **跨中心一致性检查*（仅 multi-dataset 模式）：变量9类型一致性、缺失率比较、基线分布差9
  □ 2. 交互式清洗（与用户讨论策99批准9
  □ 3. 执行清洗（Phase 3: 按批准的清洗方案执行，生成清洗日志）

  □ 4. **值规范化**（Phase 2 Step 2.5: 检测TCM术语变体 + 数值格式变体，用户确认后执行）

  □ 5. EDA 数据质量检查（缺失模式、异常值、分布特征——仅用于数据质量评估，不用于方法选择9
  □ 6. 盲态审核（盲法试验时在盲态下审核数据质疑、脱落、方案偏离）

  □ 7. 数据库锁定（锁定流程确认，避免解锁）
- **Checkpoint**: 无额外确认点。Stage 1 完成后直接进9Stage 1.5 门闸检查9
### Stage 1.5: DATA QUALITY GATE 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 1.5 未通过 9**必须退9Stage 1 修订**，不得继续进9Stage 29
- **Skill**: `data-prep` (复用)
- **Mode**: `quality-gate`（只检查，不修改）
- **输入**: 清洗后数据 + 清洗日志 + 盲态审核记录 + 数据库锁定记录
- **输出**: 数据质量门闸报告（通过/不通过 + 具体问题清单）
- **阻断检查清单 (9 项)**:

  ```
  □ 1. 清洗日志完整: 所有数据变更是否记录在案（变更原因、影响记录数）？
  □ 2. 变量定义明确: 所有衍生变量的构造逻辑是否清晰、可复现
  □ 3. 缺失机制评估: 是否已评估缺失模式（MCAR/MAR/MNAR）并选择处理策略
  □ 4. 盲态审核完9 盲态审核记录完整，无未解决的质疑？
  □ 5. 数据库锁定确9 锁定版本号和锁定时间已记录？
  □ 6. 逻辑一致性验9 清洗后数据的关键逻辑关系是否自洽（日期顺序、范围约束）
  □ 7. 值规范化完成: 所有非标准值是否已规范化并记录9      - 中医术语变体（后缀变体、同义变体）已检测并规范化（GB/T 16751.29      - 数值截断标记（<9、小于、大于等）已处理
      - 逗号多值已处理
      - 规范化日志完整（含原值、规范值、处理策略、影响记录数9      - 通过标准: 无遗留非标准值；如含自定义术语已征得用户确认
  □ 8. 可重复9 清洗脚本是否可独立运行并复现相同结果
  □ 9. 隐私合规完成: PHI字段是否已检测并脱敏/处理9🆕
      - 直接标识字段（姓名、身份证、电话等）已脱敏或删9      - 准标识符字段（精确日期、邮编等）已泛化处理
      - 自由文本PII已检测并替换
      - 隐私合规分级报告已生9      - 通过标准: 无未处理的直接标识字段；准标识符已泛化或用户确认接受风险
  ```

  - **全部通过 (9/9)** 99进入 Stage 2
  - **条件通过 (7-8/9，即 9 项非关键项未通过)** 9⚠️ 记录风险后进9Stage 2
  - **阻断 (9/9 9关键95/6/7/9 任一未通过)** 99**强制退9Stage 1 修订**
  > 关键项定义：9(数据库锁9、项6(逻辑一致9、项7(值规范化)、项9(隐私合规) 为硬阻断项，不可条件通过- **Checkpoint**: [MANDATORY-GATE-01] 门闸通过后进9Stage 2

### Stage 2: ANALYSIS PLAN
- **Skill**: `analysis-plan`
- **Mode 匹配**:
  - 用户9帮我制定分析计划" / "讨论统计方法" 9`guided` (交互式，逐步讨论 Estimands/方法)
  - 用户9快速生成SAP" / "我有方法了直接写" 9`quick` (快速生成，用户事后审阅)
  - 用户9我想探索一下数据特征再决定" 9`exploratory` (9EDA 再制9
- **研究类型分支**:
  - RCT 9ITT/PP/Safety 人群定义、ANCOVA 推荐、随机化验证、多重性控9  - 观察99DAG 混杂结构、倾向性评价PSM/IPTW)推荐、E-value 敏感性分9  - 诊断试验 9AUC 比较、金标准偏倚评估、切点选择
- **输入**: 清洗后数9+ EDA 数据质量报告 + 研究问题 + 研究类型
- **输出**: 估计目标定义 + 分析方法决策 + 统计分析计划(SAP) + 分析规范9- **子步9*:

  □ 1. 深度 EDA（方法选择用，9Stage 1 EDA 区分9
  □ 1.5. 文献种子检索（3-5 篇核心文献，为方法选择提供实证依据）9
  □ 2. 估计目标定义 + 方法探讨（基于研究类型、数据特征和文献种子，与用户讨论方法选择9
  □ 3. 制定 SAP（人群定义、终点、方法、敏感性分析、期中分析、多重性控制）

  □ 4. 计划审查（四项逐项打分: 适当性[方法与研究类型匹配]、有效性[统计功效9.80、假设可检验]、完整性[所有计划分析已列明]、可行性[数据量满足最低样本要求]9
  □ 5. 变量构造定义（Phase 5: 所有分析变量的构造公式、切点、缺失处理预定义，含 DAG 预览附属产物9- **🆕 多数据集模式**（仅 multi-dataset 模式）：Phase 3 条件章节: 多中心分析计划，制定中心效应处理策略
- **Checkpoint**: 9[MANDATORY-GATE-02] SAP 门闸检查。Stage 2 内部无额外确认点9
### Stage 2.5: SAP QUALITY GATE 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 2.5 未通过 9**必须退9Stage 2 修订**，不得继续进9Stage 39> 参考：shared/sap/sap_standard.md 9SAP标准格式定义
> 参考：shared/sap/validate_sap.py 9SAP验证脚本

- **Skill**: `analysis-plan` (复用)
- **Mode**: `quality-gate`（只检查，不修改）
- **输入**: 已审查的 SAP + EDA 报告
- **输出**: SAP 质量门闸报告（通过/不通过 + 具体问题清单）
 **阻断检查清单 (8 项)**:

  ```
  □ 1. SAP 结构完整: 所有必需章节是否存在
  □ 2. 研究目标明确: 主要/次要目标是否清晰定义
  □ 3. 估计目标完整: ICH E9(R1) 五要素是否齐全？
  □ 4. 方法选择合理: 统计方法与研究设计及研究类型(RCT/观察9是否匹配
  □ 5. 假设条件验证: 数据特征是否支持所选方法的假设
  □ 6. 敏感性分析计9 是否包含足够的敏感性分析？
  □ 7. 变量构造逻辑: 所有分析变量的构造公式、切点、依据是否在SAP中预定义
  □ 8. 可重复9 SAP 是否足够详细以便独立复现9  ```

  - **全部通过 (8/8)** 99进入 Stage 3
  - **条件通过 (6-7/8，即 9 项非关键项未通过)** 9⚠️ 记录偏差后进9Stage 3
  - **阻断 (9/8 9关键93/5/7 任一未通过)** 99**强制退9Stage 2 修订**
  > 关键项定义：9(估计目标完整)、项5(假设条件验证)、项7(变量构造逻辑) 为硬阻断项，不可条件通过- **Checkpoint**: [MANDATORY-GATE-02] 门闸通过后进9Stage 3

### Stage 3: ANALYSIS EXEC
- **Skill**: `analysis-exec`
- **Agent 拆分**: Exec Runner (Phase 0-3) + Exec Inference (Phase 4-6)
  - Generator-Evaluator 差异报告作为 Stage 3.5 门闸的输入项之一
- **Mode 匹配**:
  - 用户9按SAP执行分析" 9`sap-guided` (按计划执9
  - 用户9先探索一下数9 9`exploratory` (探索9
- **输入**: 清洗后数9+ 已批准的SAP（含变量构造逻辑9- **输出**: 分析代码 + 构造后分析数据9+ 描述性统计表 + 依从性分9+ 主要/次要/探索性分析结9+ 安全性分9+ 假设检验报9+ 质检报告
- **子步9*:

  □ 0. **样本量验9*（新增）：实际可用样本量 vs SAP 计划样本量，不足时标记为 exploratory

  □ 1. **变量构9*（从 Stage 1 移入）：9SAP 定义的变量构造逻辑生成分析变量

  □ 2. 执行前检查（数据集与 SAP 一致性验证）

  □ 3. 描述性统计（Table 1、分布汇总、受试者分布）

  □ 4. 依从性和合并用药分析

  □ 5. 安全性分析（不良事件、实验室检查、生命体征）

  □ 6. 主要估计目标分析（主估计方法9
  □ 7. 敏感性分析（探索主估计的稳健性）

  □ 8. 次要和探索性估计目标分9
  □ 9. 亚组分析和补充分9
  □ 10. 假设检验（SAP中计划的所有诊断检验）

  □ 11. 质量检查（方法正确性、假设满足、结果合理性、报告完整性）
- **🆕 多数据集模式**（仅 multi-dataset 模式）：Phase 3 条件子步9 多中心汇总分析，含森林图 + 异质性检查+ leave-one-out
- **Checkpoint**: 9[MANDATORY-GATE-03] 主要分析结果确认（Phase 3 完成后）。其余阶段无确认点9- **🆕 SAP Amendment**: Phase 3 异常处理分支支持透明9SAP 修正流程（最93 次，详见 analysis-exec/SKILL.md Phase 39
### Stage 3.5: RESULTS QUALITY GATE 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 3.5 未通过 9**必须退9Stage 3 修正**，不得继续进9Stage 49
- **Skill**: `analysis-exec` (复用)
- **Mode**: `quality-gate`（只检查，不修改）
- **输入**: 分析结果 + 质检报告 + SAP
- **输出**: 结果质量门闸报告（通过/不通过 + 具体问题清单）
- **阻断检查清单 (14 项)**:

  ```
  □ 1. 结果完整9 所9SAP 中计划的分析是否都已执行
  □ 2. 假设验证: 所有方法的假设条件是否已检验并满足
  □ 3. 数值一致9 报告中的关键数字在分析输出中是否一致？
  □ 4. 敏感性分9 敏感性分析结果是否与主分析一致？
  □ 5. 效应量报9 是否包含效应量及其置信区间？
  □ 6. 异常结果标记: 是否有异9意外结果被标记说明？
  □ 7. 结果复现: 3 次重跑关键结论是否一致？（详9shared/reproducibility/
  □ 8. [SKIP] 标记: 跳过的分析是否有合理记录
  □ 9. [校准联动] 校准置信9 该方法类型的历史校准指标是否达标9      - 读取 MSRA/calibration/calibration_db.json 中该方法类型的累9TPR/FPR
      - TPR 990% 9FPR 910% 99高置信度
      - TPR 80-90% 9FPR 10-15% 9⚠️ 低置信度，必须人工复9      - TPR < 80% 9FPR > 15% 99不可信，强制人工复核
      - 校准数据不足 (<109 9⚠️ 无法评估，必须人工复
  □ 10. P值格式合9🆕: 所有P值符9P-R01~R07（无 P=0.000，无二元化表述）
      - 参9 shared/statistics-methods/statistical_constraints.md
  □ 11. 方法一致9🆕: 加权分析链无混用（M-R01~R08），方法一致性追踪表已填
  □ 12. 数据集一致9🆕: 数据集差异已提醒用户抉择（D-R01~R05），追踪表已填写
  □ 13. 统计原则违反处理 🆕: 所有统计原则违反已记录并经用户确认（S-R01~S-R08
  □ 14. 图表发表级质量🆕: 图表符合 publication_figure_standards.md（rcParams/SVG/配色/变量9P值标注）
  ```

  - **全部通过** 99进入 Stage 4
  - **1-2 项非关键项未通过** 9⚠️ 提示用户，记录风险后带条件进9Stage 4（关键项 1/3/4/10/11/12/13 必须全部通过，不可条件通过  - **3+ 项未通过 9关键91/3/4/10/11/12/13 任一未通过** 99**强制退9Stage 3 修正**
- **Checkpoint**: [MANDATORY-GATE-03] 门闸通过后进9Stage 3.7

### Stage 3.7: RESULTS INTERPRETATION SESSION 🆕（交互式会话9
- **Skill**: `report`（预览模式）
- **输入**: analysis_results + quality_check
- **执行流程**:

  □ 1. 系统展示分析结果摘要9     - 主要终点：效应量 + p9+ 95% CI
     - 次要终点：显著性列9     - 安全性信号：AE/SAE 摘要
     - 异常发现：与预期不符的结9
  □ 2. 用户交互9     - "哪些发现你认为是最重要的？" 9记录为报告核心重9     - "哪些结果需要进一步探索？" 9触发额外分析请求
     - "哪些结果可能需要谨慎解读？" 9标记为报告中的注意事9
  □ 3. 输出：`interpretation_priorities.md`（用户确认的结果优先级）
- **Checkpoint**: 🔴 [MANDATORY] 必须确认结果优先级后才进9Stage 4
- **设计原则**：不修改任何分析结果，仅调整报告的关注重点和叙述框架
- **注意**：Stage 3.7 不允许用户修改分析结果——如需修改应退9Stage 3

### Stage 4: REPORT
- **Skill**: `report`
- **Mode 匹配**:
  - 用户9生成完整报告" 9`guided` (交互9
  - 用户9生成Table 1" 9`quick` (快速生9
- **研究类型分支**:
  - RCT 9CONSORT (报告规范选择移至 Stage 5.0，统计报告阶段不强制全文合规)
  - 观察99STROBE
  - 诊断试验 9STARD
- **输入**: 分析结果 + 质检报告 + 研究类型
- **输出**: 统计报告 + 图表(figures/*.png) + 三线9tables/*.docx) + 方法学描9+ 统计质量检查+ 图文HTML报告
- **子步9*:

  □ 1. 结果解读（临床意义、效应量解释、局限性、与文献对比9
  □ 2. 生成表格（Table 1、结果表、敏感性分析表9
  □ 3. 表格导出（三线表→docx9
  □ 4. 生成图表（执行模板→保存PNG：KM曲线、森林图、ROC等出版级图表9
  □ 5. 方法学描述（按模板结构化段落9
  □ 6. 统计质量检查（statcheck + anti-patterns + 统计维度 quality_checklist9
  □ 7. 报告组装（Phase 6: JSON骨架→HTML图文报告，按模板章节组织9- **Checkpoint**: [MANDATORY-GATE-04] 统计质量检查9确认 9[MANDATORY-GATE-05] 9STAGE 4 CHECKPOINT: [A] 结束 / [B] Paper Track
- **输出**: final_report.md + final_report.html + figures/*.png + tables/*.docx

### Stage 5: PAPER TRACK（可99Stage 4 checkpoint 9[B] 时进入）

> **入口守卫（IRON RULE9*：仅9passport.track == "full_paper" 时进入> Stage 1-4 必须全部 completed/consumed。Stage 4 报告产物（final_report + figures + tables）必须齐全9
MSRA Pipeline 9Paper Track 保持纯调度，依次调用各写9skill 完成论文从选题到定稿的全流程9
#### Stage 5.0: PAPER INTAKE

- **Skill**: `report`
- **输入**: MSRA passport (track=full_paper) + final_report + SAP + Stage 3.5 门闸报告
- **工作9*:

  □ 1. 产物校验（passport stage_4 == completed + final_report 存在9
  □ 2. 生成 MSRA Handoff Bundle（调9`scripts/generate_msra_handoff_bundle.py` 9`MSRA/msra_handoff_bundle.md`）9包含 RQ、方法摘要、表9图表列表、核心发现、安全性发现、局限性讨论、论文级方法文本

  □ 3. 报告规范选择（基9study_type 推荐 CONSORT/STROBE/STARD；用户可覆盖9
  □ 4. 期刊模板选择（`shared/journal-templates/`9
  □ 5. 论文配置确认（预9RQ/Discipline/Method/Existing Materials/Citation=Vancouver9- **输出**: `msra_handoff_bundle.md` + 论文配置
- **Checkpoint**: [MANDATORY] 确认论文配置后进9Stage 5.1

#### Stage 5.1: LITERATURE SEARCH

- **Skill**: `systematic-survey`
- **输入**: MSRA Handoff Bundle（含文献 seed9 研究问题
- **工作9*:

  □ 1. 读取 MSRA Phase 1 文献对比作为 seed

  □ 2. 基于 seed 扩展检索（Forward/Backward citation9
  □ 3. 针对性补充检索（Introduction 需要的背景文献、Discussion 需要的对比文献9
  □ 4. 质量评估（证据层级、相关性评分）

  □ 5. 主题综合（非逐篇罗列9- **输出**: 完整 Bibliography + Synthesis Report
- **复用机制**: MSRA Phase 1 文献直接纳入，不重复检查- **Checkpoint**: [MANDATORY] 文献覆盖评估确认

#### Stage 5.2: PAPER WRITING

- **Skill**: `report` (论文写作模式)
- **输入**: MSRA Handoff Bundle + Bibliography + Synthesis Report + figures/*.png + tables/*.docx
- **工作9*:

  □ 1. **Introduction**: 文献综述 + 研究背景 + 研究空白 + RQ 陈述

  □ 2. **Methods**: 直接引用 MSRA Stage 4 Phase 4 方法学描述（不重新生成）

  □ 3. **Results**: 直接引用 MSRA figures/tables（不重新生成9 结果描述

  □ 4. **Discussion**: 结果解读 + 与文献对9+ 局限9+ 临床意义

  □ 5. **Abstract**: 结构化摘要生9
  □ 6. **Compliance Check**: 基于 study_type 的报告规范检查（CONSORT/STROBE/STARD9- **输出**: 完整论文草稿（IMRaD 结构9- **复用机制**: 融合9D（方法学9 融合9F（表格图表）
- **Checkpoint**: [MANDATORY] 草稿审查确认

#### Stage 5.5: INTEGRITY CHECK 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 5.5 未通过 9必须退9Stage 5.2 修订9
- **Skill**: 内置完整性验9- **输入**: 论文草稿 + Stage 3.5 门闸报告 + MSRA Handoff Bundle
- **检查清9*:

  □ 1. 引用完整性（所有引用是否真实存在）

  □ 2. 数字一致性（论文中数字与 MSRA 分析结果是否一致）

  □ 3. 引用格式合规（所9Citation Format 是否正确应用9
  □ 4. 报告规范合规（CONSORT/STROBE/STARD 检查清单）

  □ 5. 重复内容检测（无自我抄袭）

  □ 6. 伦理合规（IRB 声明、知情同意）
- **复用机制**: Stage 3.5 门闸报告已验证统计数字，不重复检查- **检查结9*:
  - 全部通过 99进入 Stage 5.6
  - 1-2 项未通过 9⚠️ 带条件进入（记录风险9  - 3+ 项未通过 99强制退9Stage 5.2
- **Checkpoint**: [MANDATORY] 完整性报告确9
#### Stage 5.6: PEER REVIEW

- **Skill**: `peer-review`
- **输入**: 论文草稿 + 完整性报9+ 研究类型
- **工作9*:

  □ 1. 5 位独立审稿人评审：EIC + 方法学审稿人 + 领域审稿9+ 写作审稿9+ Devil's Advocate

  □ 2. 7 维评分：Originality、Methodological Rigor、Evidence Sufficiency、Argument Coherence、Writing Quality、Literature Integration、Significance

  □ 3. 编辑决策：Accept / Minor Revision / Major Revision / Reject

  □ 4. 生成 Revision Roadmap（优先级排序的修改建议）
- **输出**: Review Report + Revision Roadmap + Editorial Decision
- **Checkpoint**: [MANDATORY] 评审结果确认 9决定是否修订

#### Stage 5.7: REVISION

- **Skill**: `report` (论文写作模式)
- **输入**: 论文草稿 + Revision Roadmap + Review Report
- **工作9*:

  □ 1. 逐项修改论文（按 Revision Roadmap9
  □ 2. 生成 Response to Reviewers（逐条回应9
  □ 3. 更新论文草稿
- **输出**: 修订后论9+ Response to Reviewers
- **Checkpoint**: [MANDATORY] 修订完成确认

#### Stage 5.8: FINAL INTEGRITY CHECK 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 5.8 未通过 9必须退9Stage 5.7 修订9
- **Skill**: 内置完整性验证（最终版9- **输入**: 修订后论9+ Response to Reviewers + Revision Roadmap
- **检查清9*:

  □ 1. 所有评审意见是否已回应

  □ 2. 所有修改是否已落实

  □ 3. 新引入的内容是否合规

  □ 4. R&R Traceability Matrix 是否完整
- **检查结9*:
  - 全部通过 99进入 Stage 5.9
  - 未通过 99强制退9Stage 5.7
- **Checkpoint**: [MANDATORY] 最终完整性报告确9
#### Stage 5.9: FINALIZE

- **Skill**: `report` (论文写作模式)
- **输入**: 最终论9+ 期刊模板
- **工作9*:

  □ 1. 格式转换：MD 9DOCX（via Pandoc9
  □ 2. PDF 导出

  □ 3. 排版调整（期刊模板适配9
  □ 4. 最终检查（格式、页码、参考文献）
- **输出**: final_paper.md + final_paper.docx + final_paper.pdf

#### Stage 6: PROCESS SUMMARY

- **输入**: MSRA passport + 所有阶段产9- **工作9*:

  □ 1. 汇9Stage 1-5 全过程记9
  □ 2. 更新 passport：所有阶段标9completed，status = "completed"

  □ 3. 生成过程摘要报告
- **输出**: process_summary.md + 更新后的 passport.json

---

## 4. Checkpoint Protocol（三级分层）

> 根据 §2.5 用户选择的交互密度，Checkpoint 按三级执行9*核心原则**9> - MANDATORY 级：用户不可绕过，必须展示并等待决策
> - SLIM 级：仅一行确认，无需完整 Dashboard
> - ADAPTIVE 级：仅在特定异常条件触发

### 4.1 MANDATORY Checkpoint（阻断式，所有模式均强制执行9
以下 5 个检查点**不可跳过**，无论用户选择哪种模式都必须暂停展示结果：

| # | 位置 | 触发条件 | 展示内容 | 用户决策选项 |
|---|------|---------|---------|-------------|
| GATE-01 | Stage 1.5 通过| 数据门闸结果 | 9 项门闸检查结9+ 阻断判定 | 通过继续 / 退回修9/ 带条件通过 |
| GATE-02 | Stage 2.5 通过| SAP 门闸结果 | 8 项门闸检查结9+ 阻断判定 | 通过继续 / 退回修9/ 带条件通过 |
| GATE-03 | Stage 3.5 通过| 结果门闸结果 | 14 项门闸检查结9+ 阻断判定 | 通过继续 / 退回修9/ 带条件通过 |
| GATE-04 | Stage 4 完成| 统计质量检查+ 报告交付决策 | 统计质量报告 + ★[A]结束/[B]继续Paper Track | [A]结束 / [B]进入Stage 5.0 |
| GATE-06 | 任一门闸回退9次（收敛失败| 收敛检测触9| 未通过项清9+ 回退历史 + 风险评估 | 书面接受风险继续 / 退回根本原因排9/ 换方法换9|

**MANDATORY Checkpoint 简9Dashboard**（一行即可，不再展示 ASCII 框）9
```
── MANDATORY CHECKPOINT ──
Stage {N} 完成 | 产物: {产物1} 9| 选择: [继续 / 回改 / 查看详情]
```

**协作深度观察**（详细引导模式可选输出）9
> 参考：shared/statistics-methods/collaboration_rubric.md 9协作深度评估框架
> 三个维度：委托强9/ 认知警觉 / 认知再分配，90-5 9> 必须有对话证据支撑，不凭感觉打分

```
── 协作深度观察（非阻断）──
委托强度: 4/5 9| 认知警觉: 2/5 ⚠️ 必须在门闸结果上逐项核对 | 认知再分9 3/5
```

输出规则9- 高效模式下不输出协作深度观察
- 用户需要时再说"输出协作观察"
- 每个 MANDATORY Checkpoint **最多输出一9*

### 4.2 SLIM Checkpoint（一行确认，根据用户模式选择性执行）

> **设计原则**：仅在详细引导模式下执行。高效模式下全部跳过（仅记录）9
| 模式 | SLIM 执行规则 |
|------|-------------|
| 详细引导 | 执行 PIPE-01（Stage 2 方法确认后） |
| 高效模式 | 全部跳过（仅记录9|

SLIM 触发点：

| # | 位置 | 提示模板 | 备注 |
|---|------|---------|------|
| PIPE-01 | Stage 2 Estimands + 方法确认9| `Estimands + 方法已确9 生成 SAP? [y/N]` | 详细引导模式下执9|
| PIPE-02 | Stage 3 Phase 3 主要分析完成| `主要分析结果已出，继续敏感性分9 [y/N]` | 详细引导模式下执9|
| PIPE-03 | Stage 4 Phase 1 结果解读完成| `结果解读已完成，继续生成表格? [y/N]` | 详细引导模式下执9|
| PIPE-04 | Stage 4 Phase 4 方法学描述完成后 | `方法学描述已完成，进入统计质量检查 [y/N]` | 详细引导模式下执9|

### 4.3 ADAPTIVE Checkpoint（异常触发式9
> **设计原则**：仅在异常条件触发，正常流程不暂停9
| 触发条件 | 自动暂停 |
|---------|---------|
| 数据质量严重问题（缺失率 > 30%、异常值异常多9| 9必须暂停讨论 |
| SAP 审查发现 P0/P1 级缺9| 9必须退回修9|
| 分析结果与预期严重不符（效应方向相反、P 值边界） | 9必须暂停讨论 |

**模式差异**9- 详细引导：展示问题详9+ 选项供用户选择
- 高效模式：展示问题摘9+ 推荐方案，用户确认后继续

**正常流程**：无异常 9全程无额外暂停，直接9Stage 1 流向 Stage 49
**IRON RULE**: MANDATORY checkpoint 不能以任何理由自动跳过。SLIM 9ADAPTIVE 可跳9合并，但所有跳过操作必须记录到进度追踪9
**IRON RULE**: 记住用户选择的交互模式。如果后续交互与用户选择的模式不一致，先确认再继续。不要自行升级降级交互密度9
### 4.3.1 Checkpoint Summary Table

> **用9*：一览所有流水线检查点9ID、类型、量化通过/阻断标准和升级动作。编排器在每9Checkpoint 时对照此表执行判定9
#### Stage 19 核心流水9
| Checkpoint ID | 类型 | 位置 | 检查项9| 🟢 通过标准 | 🟡 条件通过 | 🔴 阻断标准 | 升级动作 |
|---------------|------|------|---------|------------|------------|------------|---------|
| GATE-01 | 🔴 MANDATORY | Stage 1.5 9Stage 2 | 9 | **9/9** 全部通过 | **79/9** 通过（≤2 非关键项未通过），记录风险 | **9/9** 或关键项 **5/6/7/9** 任一未通过 | 退9Stage 1 修订；回退 9 次触9GATE-06 |
| GATE-02 | 🔴 MANDATORY | Stage 2.5 9Stage 3 | 8 | **8/8** 全部通过 | **69/8** 通过（≤2 非关键项未通过），记录偏差 | **9/8** 或关键项 **3/5/7** 任一未通过 | 退9Stage 2 修订；回退 9 次触9GATE-06 |
| GATE-03 | 🔴 MANDATORY | Stage 3.5 9Stage 4 | 14 | **14/14** 全部通过 | **19 9*未通过（≥10/14），记录风险 | **3+ 9*未通过 或关键项 **10/11/12/13** 任一未通过 | 退9Stage 3 修正；回退 9 次触9GATE-06 |
| GATE-04 | 🔴 MANDATORY | Stage 4 统计质量检查后 | 9| 统计质量检查通过 | statcheck 警告，记录后继续 | statcheck 发现数值不一9| 退9Stage 3 核查 |
| GATE-05 | 🔴 MANDATORY | Stage 4 交付决策 | 9| final_report + figures + tables 齐全 | 9| 产物缺失或格式不合规 | 提示补充产物 |
| GATE-06 | 🔴 MANDATORY | 任一门闸回退 9 9| 9| 9| 9| 收敛失败（同阶段退99 次） | 用户书面接受风险 9标注 ⚠️ [CONVERGED WITH DEVIATIONS] |
| PIPE-01 | 🟡 SLIM | Stage 2 Estimands+方法确认9| 9| 9| 9| 9| 仅详细引导模式执行；高效模式跳过（仅记录9|
| PIPE-02 | 🟡 SLIM | Stage 3 Phase 3 主要分析完成| 9| 9| 9| 9| 仅详细引导模式执行；高效模式跳过（仅记录9|
| PIPE-03 | 🟡 SLIM | Stage 4 Phase 1 结果解读完成| 9| 9| 9| 9| 仅详细引导模式执行；高效模式跳过（仅记录9|
| PIPE-04 | 🟡 SLIM | Stage 4 Phase 4 方法学描述完成后 | 9| 9| 9| 9| 仅详细引导模式执行；高效模式跳过（仅记录9|
| ADP-01 | 🟡 ADAPTIVE | 数据质量异常（缺9>30%9| 9| 9| 9| 异常条件触发 | 详细引导：展示详9选项；高效模式：摘要+推荐方案 |
| ADP-02 | 🟡 ADAPTIVE | SAP 审查 P0/P1 级缺9| 9| 9| 9| 异常条件触发 | 强制退回修改，不可条件通过 |
| ADP-03 | 🟡 ADAPTIVE | 分析结果与预期严重不9| 9| 9| 9| 异常条件触发 | 暂停讨论，评估方向是否需调整 |

#### Stage 5 Paper Track

| Checkpoint ID | 类型 | 位置 | 通过标准 | 阻断标准 | 升级动作 |
|---------------|------|------|---------|---------|---------|
| PT-01 | 🔴 MANDATORY | Stage 5.0 论文配置 | 用户确认配置（RQ/Discussion/Method/Template9| 9| 不确认不进入 Stage 5.1 |
| PT-02 | 🔴 MANDATORY | Stage 5.1 文献覆盖 | 用户评估文献覆盖充分9| 9| 不确认不进入 Stage 5.2 |
| PT-03 | 🔴 MANDATORY | Stage 5.2 草稿审查 | 用户确认论文草稿 | 9| 不确认不进入 Stage 5.5 |
| PT-04 | 🔴 MANDATORY | Stage 5.5 完整性检查| 6 项全部通过 | 3+ 项未通过 | 退9Stage 5.2 修订 |
| PT-05 | 🔴 MANDATORY | Stage 5.6 评审决策 | 评审结果确认 9Accept/Minor | Major Revision 9Stage 5.7；Reject 9Stage 5.2 或终9| 按编辑决策路9|
| PT-06 | 🔴 MANDATORY | Stage 5.7 修订完成 | 所有评审意见已回应 | 9| 不确认不进入 Stage 5.8 |
| PT-07 | 🔴 MANDATORY | Stage 5.8 最终完整9| **必须零问题通过** | 任何未通过| 退9Stage 5.7 修正，无妥协 |

> **关键项定义速查**：GATE-01 关键9= {5,6,7,9}；GATE-02 关键9= {3,5,7}；GATE-03 关键9= {10,11,12,13}。关键项为硬阻断，不可条件通过
### 4.4 分层验证框架

> 参考：shared/reporting-guidelines/quality_checklist.md 98 维度质量检查清单；shared/reproducibility/reproducibility_guide.md 9复现验证标准

每个 Stage 完成后，执行分层验验证
**第一层：自动化快速检查（秒级9*
- [ ] 所有计划产物已生成（无遗漏9- [ ] 产物格式合规（无 markdown 残留、无异常标记9- [ ] 数值一致性（报告中引用的数字与分析输出一致）
- [ ] 表格/图表引用完整
- [ ] [SKIP] 标记数量和原因已记录

**第二层：LLM 辅助质量评估（分钟级9*
- 逐阶段质量评分（准确性、完整性、特异性）
- 9SAP/指南标准对比
- 输出结构化改进建9
**第三层：重复性验证（可选）**
- 同一输入运行 N 次，检查关键结论一致9- 统计输出变动范围（关键数字应 100% 一致）

---

## 5. Progress Tracking

> 使用 Material Passport (`shared/passport/passport.py`) 追踪产物生命周期9> 护照路径: `.msra/passport.json`（自动创建）9> 能力: 产物追踪(planned→consumed) / 前置检查/ 恢复(`/msra --resume`) / 回滚 / 门闸记录

### 5.0 状态表9
在每9checkpoint 更新进度（示例）9
```
Stage 1  [数据准备]       ██████████ 100% 9Stage 1.5 [数据质量门闸]   ██████████ 100% 9Stage 2  [分析计划]       ████████░░  80% 🔄
Stage 3  [分析执行]       ░░░░░░░░░░   0% 9Stage 3.5 [结果质量门闸]   ░░░░░░░░░░   0% 9Stage 4  [报告生成]       ░░░░░░░░░░   0% 9Stage 5  [论文写作]       ░░░░░░░░░░   --  9(track=full_paper 时显9
```

### 5.1 产物追踪

使用 Passport 自动管理（`pm.update_status()` / `pm.get_resume_point()`）：

| 阶段 | 产物 | 护照ID |
|------|------|--------|
| Stage 1 | 清洗后数9+ 清洗日志 + 盲态审核+ 锁定记录 | cleaned_data / cleaning_log / ... |
| Stage 1.5 | 数据质量门闸报告 | gate_stage_1.5 |
| Stage 2 | SAP | sap |
| Stage 2.5 | SAP质量门闸报告 | gate_stage_2.5 |
| Stage 3 | 分析结果 + 质检报告 | analysis_results / qc_report |
| Stage 3.5 | 结果质量门闸报告 | gate_stage_3.5 |
| Stage 4 | 最终报9+ 图表 + 三线9| final_report / figures / tables |

---

## 5.2 Material Passport JSON Schema

> 以下9`.msra/passport.json` 的完9JSON Schema 定义。所有阶段调度、前置检查、门闸记录均基于此结构9
```json
{
  "passport_version": "1.0",
  "study_id": "string",
  "current_stage": "Stage 0|1|1.5|2|2.5|3|3.5|4|5",
  "artifacts": {
    "raw_data": {"path": "string", "status": "pending|completed", "hash": "string"},
    "cleaned_data": {"path": "string", "status": "pending|completed", "hash": "string"},
    "sap": {"path": "string", "status": "pending|completed|approved", "hash": "string"},
    "analysis_results": {"path": "string", "status": "pending|completed", "hash": "string"},
    "report": {"path": "string", "status": "pending|completed", "hash": "string"}
  },
  "gates": {
    "stage_1_5": {"status": "pending|passed|blocked", "checks_passed": 0, "checks_total": 9},
    "stage_2_5": {"status": "pending|passed|blocked"},
    "stage_3_5": {"status": "pending|passed|blocked", "checks_passed": 0, "checks_total": 14}
  },
  "deviations": [],
  "timestamp": "ISO 8601"
}
```

**字段说明**9
| 字段 | 类型 | 说明 |
|------|------|------|
| `passport_version` | string | Schema 版本号，当前9"1.0" |
| `study_id` | string | 研究唯一标识9|
| `current_stage` | string | 当前所处阶9|
| `artifacts.*.status` | string | 产物状态：pending 9completed（SAP 可为 approved9|
| `artifacts.*.hash` | string | 产物文件哈希，用于完整性校9|
| `gates.*.status` | string | 门闸状态：pending 9passed / blocked |
| `gates.*.checks_passed/total` | number | 门闸检查项通过总数 |
| `deviations` | array | 偏差记录列表，每条含阶段、内容、影响评估、用户确认状9|
| `timestamp` | string | 最后更新时间（ISO 86019|

---

## 6. Agent Dispatch Mode (9Agent 协作)

> 在不同阶段切换为对应专家角色，完成后切回 Orchestrator 模式9> 完整定义9[agents/AGENTS.md](../../agents/AGENTS.md)（含接棒协议、异常上报、跨 Agent 约束）9> Agent 角色定义文件（均已验证存在于 agents/ 目录）：
> - [Data Validator Agent](../../agents/data_validator_agent.md) 9Stage 1
> - [Method Consultant Agent](../../agents/method_consultant_agent.md) 9Stage 2
> - [Exec Runner Agent](../../agents/exec_runner_agent.md) 9Stage 3 Phase 0-3
> - [Exec Inference Agent](../../agents/exec_inference_agent.md) 9Stage 3 Phase 4-6
> - [QC Inspector Agent](../../agents/qc_inspector_agent.md) 9Stage 1.5/2.5/3.5
> - [AGENTS.md](../../agents/AGENTS.md) 9接棒协议与跨 Agent 约束总纲

### 6.1 角色切换规则

每个 Stage 开始时切换为对应角色，完成后切9Orchestrator9Stage 3 使用 Generator-Evaluator 双角色：Phase 0-3 9Exec Runner，Phase 4-6 9Exec Inference9差异比对结果纳入 Stage 3.5 门闸输入9
### 6.2 Agent 角色卡速查

| 阶段 | 角色 | Agent 文件 | 核心行为 | 禁止行为 |
|------|------|-----------|---------|---------|
| Stage 1 | [Data Validator](../../agents/data_validator_agent.md) | `agents/data_validator_agent.md` | 验证/清洗/构9| 决定统计方法 |
| Stage 1.5 | [QC Inspector](../../agents/qc_inspector_agent.md) | `agents/qc_inspector_agent.md` | 数据 9 项阻断检查| 修改数据或清洗脚9|
| Stage 2 | [Method Consultant](../../agents/method_consultant_agent.md) | `agents/method_consultant_agent.md` | EDA/Estimands/SAP | 写代码执行分9|
| Stage 2.5 | [QC Inspector](../../agents/qc_inspector_agent.md) | `agents/qc_inspector_agent.md` | SAP 8 项阻断检查| 修改 SAP 内容 |
| Stage 3 (Phase 0-3) | [Exec Runner](../../agents/exec_runner_agent.md) | `agents/exec_runner_agent.md` | 代码生成/执行/自愈 Debug | 偏离 SAP/自行解读结果 |
| Stage 3 (Phase 4-6) | [Exec Inference](../../agents/exec_inference_agent.md) | `agents/exec_inference_agent.md` | 独立假设检查质检/输出 | 修改代码/跳过假设验证 |
| Stage 3.5 | [QC Inspector](../../agents/qc_inspector_agent.md) | `agents/qc_inspector_agent.md` | 结果 14 项阻断检查+ Generator-Evaluator 差异审查 | 修改结果 |
| Stage 4 | Report Expert | `skills/report/SKILL.md` | 解读/制表/生成 | 修改数据 |

详细接棒协议（Handoff 格式）、异常上报规则（INFO/WARN/BLOCK 三级别及阻断触发条件）及9Agent 约束9[agents/AGENTS.md](../../agents/AGENTS.md)9
---

## 7. Error Handling & Rollback

### 7.1 阶段内错9
| 触发条件 | 一线处9| 仍失败兜9|
|---------|---------|-----------|
| 数据验证发现严重问题 | 回到 Stage 1 重新清洗 | 标记数据9不可9（触发条9 缺失950% 9关键变量缺失>30% 9数据结构无法修复），要求用户决定是否重新收集 |
| **Stage 1.5 质量门闸未通过** | **退9Stage 1 修订清洗流程** | **3+ 项未通过或项95/6 未通过必须修订，不得跳过；回退 92 次走收敛检查(7.3)** |
| SAP 审查不通过 | 回到 Stage 2 修改计划 | 用户接受风险后继续，记录偏差 |
| **Stage 2.5 质量门闸未通过** | **退9Stage 2 修订 SAP** | **3+ 项未通过必须修订，不得跳过；回退 92 次走收敛检查(7.3)** |
| 质检发现严重错误 | 回到 Stage 3 修正分析 | 标记结果9待验9并阻断进9Stage 4，用户确认后方可解锁 |
| **Stage 3.5 质量门闸未通过** | **退9Stage 3 修正分析** | **3+ 项未通过必须修正，不得跳过；回退 92 次走收敛检查(7.3)** |
| 前置产物缺失（门闸级: Stage 1.5/2.5/3.59| 🔴 **阻断**：门闸前置产物缺失等同于门闸未通过，必须补齐后才能进入对应门闸 | 用户不可跳过，必须回到对应阶段补齐产9|
| 前置产物缺失（非门闸9 Stage 2/3/49| 提示用户补充产物，提供产物模板引9| 用户确认后继续，记录偏差9passport.deviations |

**错误处理优先级规9*91. 🚫 **Blocking** (门闸 3+ 项未通过 / 门闸前置产物缺失) 9必须退回，用户不可跳过
2. ⚠️ **Conditional** (门闸 1-2 项非关键项未通过 / 质检问题) 9可带条件通过，记录风93. 🔵 **Informational** (非门闸阶段的前置产物缺失) 9提示补充后继续，记录偏差
4. 多阶段错误同时发生时9*从最早出错的阶段开始修9*

**多信号冲突处9*9
| 场景 | 处理策略 |
|------|---------|
| 用户同时提供 SAP + 原始数据 | 检测到原始数据→从 Stage 1 开始，告知用户 SAP 将在 Stage 2 使用 |
| 用户9做分9但有清洗数据和分析结果两个线9| 优先9Stage 3 执行（分析执行），因为分析执行最接近用户意图 |
| 用户9完整流程"9快9矛盾 | 9完整流程"为准，但推荐 Stage 1-4 分步执行而非一次完9|

### 7.2 偏差记录
如果分析执行中偏离了 SAP，按以下结构化流程执行：
1. **记录偏差内容**：偏离的 SAP 条款编号 + 偏离描述 + 实际执行的方法2. **评估偏差影响**：判定影响等级（见下表）9填入 passport.deviations
3. **与用户讨9*：展示影响等9+ 偏差后果，用户书面确认接受或拒绝
4. **执行决策**：接99记录9passport 继续；拒99回退修正

**偏差影响等级定义**9
| 等级 | 判定标准 | 处理方式 |
|------|---------|---------|
| P0 (严重) | 改变主要终点定义 / 删除计划的敏感性分9/ 更换主要估计方法 | 必须退9Stage 2 修订 SAP，不可就地接9|
| P1 (中等) | 调整亚组定义 / 修改协变量列9/ 增加未计划的分析 | 记录偏差 + 用户书面确认 + passport 标记 ⚠️ |
| P2 (轻微) | 代码实现细节差异 / 数值精度差9/ 输出格式调整 | 记录偏差，无需用户确认 |

### 7.3 收敛检测与回退循环控制（⏱ 新增9
> 防止同一环节无限循环回退。借鉴 MSRA 9early-stopping 设计9
**回退计数9*：每个质量门闸维护独立的回退次数计数9
| 门闸 | 计数器名 | 最大回退次数 |
|------|---------|------------|
| Stage 1.5 9Stage 1 | `retry_data_prep` | 2 |
| Stage 2.5 9Stage 2 | `retry_sap` | 2 |
| Stage 3.5 9Stage 3 | `retry_analysis` | 2 |

**收敛判断逻辑**9
```
91 次退99正常修改，记录偏差原992 次退99警告9已退92 次，必须检查根本原因或降低标准"
93 次退99BLOCK: "同阶段已退93 次，自动转入偏差记录模式"
                9必须9GATE-06 Checkpoint，用户需书面接受风险
                9后续分析结果标注 ⚠️ [CONVERGED WITH DEVIATIONS]
```

**Early-stopping 辅助判断**9- 如果质量门闸未通过项数在上一次回退9*没有减少** 9强制暂停，引导用户换人审查或换方法，并在护照中标9收敛异常"
- 如果未通过项数减少但仍9**9 项关键项未通过** 9强制进入 ADPATIVE checkpoint，提示用户评估修改研究设计的必要9- 每次回退必须记录"上一次做了哪些修9 + "本次检查结果是否有改善"

**IRON RULE**: 回退超过 2 次后，不得自动再次退回。必须走 MANDATORY Checkpoint 让用户决策9
---

## 检查点量化标准

| 门闸 | 检查项 | 通过标准 | 条件通过 | 阻断标准 |
|------|--------|---------|---------|---------|
| Stage 1.5 | 9项检查| 9/9通过 | 7-8/9通过(记录风险) | 9/9 99/6/7/9未通过 |
| Stage 2.5 | 8项检查| 8/8通过 | 6-7/8通过(记录偏差) | 9/8 99/5/7未通过 |
| Stage 3.5 | 14项检查| 14/14通过 | 10-13/14通过(记录风险) | <10/14 990/11/12/13未通过 |

**Stage 3.5 关键项量化标9*:

| 项号 | 检查项 | 通过标准 | 阻断标准 |
|------|--------|---------|---------|
| 10 | P值格9| 全部P值符合P-R01~R07 | 任何P=0.000出现 |
| 11 | 方法一致9| 加权/非加权不混用(M-R01) | 检测到混用 |
| 12 | 数据集一致9| 全程使用同一锁定数据9D-R02) | 检测到数据集切9|
| 13 | 统计原则 | 所有假设检验已执行(S-R01~R08) | 跳过假设检查|
| 14 | 图表质量 | SVG+PNG 300dpi双格9| 仅PNG9300dpi |

> **升级规则**: Stage 3.590/11/12/13为硬阻断项，不可条件通过> **收敛规则**: 同一Stage退回≥399BLOCK 9用户书面接受风险 9[CONVERGED WITH DEVIATIONS]

## 7.4 边缘场景处理

> 以下场景在流水线执行中可能遇到，需按表中的降级策略执行，确保流程可追踪且不静默失败
| 场景 | 触发条件 | 处理策略 | 标记 |
|------|---------|---------|------|
| analysis-exec 产出为空 | Stage 3 执行后无任何分析输出 | BLOCK，使用简9SAP 重试，最多重93 9| [EMPTY_OUTPUT] |
| 代码执行超时 | 单次执行耗时 > 300s | 终止执行，记录超时日志，提示用户简化分析或增加资源 | [TIMEOUT] |
| 部分阶段失败 | 部分分析成功、部分失9| 继续使用成功结果，失败项标记为部分失9| [PARTIAL_FAIL] |
| Material Passport 损坏 | passport.json 格式异常或字段缺9| 从各阶段产物重建 passport，记录重建事9| [PASSPORT_REBUILT] |
| Skill 依赖缺失 | 所需 skill（如 peer-review）未安装 | 跳过对应阶段（如 Paper Track），提示用户安装 | [SKIP: dependency missing] |
| 用户中途中9| 用户在阶段执行中主动中止 | 保存当前状态到 passport，允许从最后检查点恢复 | [USER_ABORTED] |

---

## 8. Quick Reference Commands

| 命令 | 触发 | 入口 |
|------|------|------|
| `/msra` | 启动流水线（自动检测入口） | 智能检查|
| `/msra --from data` | 从数据准备开9| Stage 1 |
| `/msra --from plan` | 从分析计划开9| Stage 2 |
| `/msra --from exec` | 从分析执行开9| Stage 3 |
| `/msra --from report` | 从报告生成开9| Stage 4 |
| `/msra --status` | 查看当前进度 | - |
| `/msra-data` | 直接调用数据准备 | Stage 1 |
| `/msra-plan` | 直接调用分析计划 | Stage 2 |
| `/msra-exec` | 直接调用分析执行 | Stage 3 |
| `/msra-report` | 直接调用报告生成 | Stage 4 |
| `/msra-report CONSORT` | 指定规范的报告生9| Stage 4 |
| `/msra-report --output html` | 指定输出HTML图文报告 | Stage 4 |
| `/msra --calibrate <gold.csv>` | 运行度量校准 ⚠️ 实验9| QC Inspector |
| `/msra --calibrate-status` | 查看当前校准状9⚠️ 实验9| - |
| `/msra --calibrate-update <results.csv>` | 增量更新校准 ⚠️ 实验9| - |
| `/msra --status` | 查看当前进度（Passport9| - |
| `/msra --resume` | 从上次中断处恢复（读9Passport9| 智能检查|

---

## 9. Interaction Examples

### Example 1: 全流程（高效模式9```
用户: /msra 我有一份RCT的原始数据，想完成整个分析流99检测到原始数据 99Stage 1 开99用户9[2] 高效模式

Stage 1 9[MANDATORY] 9Stage 1.5(99 9[MANDATORY]
9Stage 2 9[SLIM] 9[MANDATORY] 9Stage 2.5(89 9[MANDATORY]
9Stage 3 9[SLIM] 9Stage 3.5(149 9[MANDATORY]
9Stage 4 9[MANDATORY] 合规检查完成 996 9MANDATORY + 2 9SLIM
```

### Example 2: 中途切9+ 新手引导
```
# 中途切9用户: /msra 数据已清洗好，帮我做分析计划
99Stage 2 开99前置检查 清洗日志存在 9高效模式 9Stage 2 9...

# 新手详细引导
用户: /msra 我有数据但不确定怎么做统999Stage 1 开99用户9[1] 详细引导
9每步暂停讨论策略 9逐项解释门闸结果 9全程 FULL checkpoint
```

---

## 架构集成9
```
┌──────────────────────────────────────────────────────────99                   MSRA Pipeline 架构                      99                                                           99 ┌─────────9  ┌──────────9  ┌──────────9  ┌────────9 99 9data-   9  9analysis-9  9analysis-9  9report 9 99 9prep    9  9plan     9  9exec     9  9       9 99 └────┬────9  └────┬─────9  └────┬─────9  └───┬────9 99      9            9             9             9      99      9            9             9             9      99 ┌────────────────────────────────────────────────────9 99 9             Material Passport (JSON)               9 99 9 ┌──────────┬──────────┬──────────┬──────────9   9 99 9 9artifacts9 gates   │deviations9timestamp9   9 99 9 └──────────┴──────────┴──────────┴──────────9   9 99 └────────────────────────────────────────────────────9 99      9            9             9             9      99      9            9             9             9      99 ┌──────────9 ┌──────────9 ┌──────────────────────9  99 9Stage 1.59 9Stage 2.59 9    Stage 3.5        9  99 9数据门闸  9 9SAP门闸  9 9    分析门闸         9  99 9(99    9 9审查)    9 9    (149           9  99 └──────────9 └──────────9 └──────────────────────9  99      9            9             9             9      99      └─────────────┴──────────────┴──────────────9      99                        9                                 99                   ┌────▼────9                            99                   │calibration9(gate-check 模式)         99                   └─────────9                            99                        9                                 99                   ┌────▼────9                            99                   9 Stage 5 9(Paper Track, 可9        99                   └─────────9                            9└──────────────────────────────────────────────────────────9```

**架构设计原则**:
1. Pipeline为纯调度器，不做实质性分析工92. Material Passport是唯一的跨Stage状态传递机93. 质量门闸为阻断式，不可跳9MANDATORY)
4. 每个Stage的Skill独立运行，通过Passport解95. calibration作为Stage 3.5的子检查集成，不独立成Stage

## 10. 快速模9(Quick Mode)

> 面向简单数据集和快速探索场景的精简流水线。在保证核心质量门闸的前提下跳过非必要步骤9
### 触发条件

满足以下任一条件即自动进9Quick Mode9- 用户输入包含"快99quick"9快速分9等关键词
- 数据集变量数 < 10 且行9< 100

### 简化流9
```
Stage 0: 入口检查9识别9Quick Mode
   9Stage 1: 数据准备（仅快速验证，跳过数据画像 Phase 09   9Stage 1.5: 数据质量门闸（缩减为 5 项关键检查）
   9Stage 2: 分析计划（使用模9SAP，跳过文献种子检索）
   9Stage 3: 分析执行（仅核心分析，跳过敏感9亚组/安全性分析）
   9Stage 3.5: 结果质量门闸（缩减为 7 项关键检查）
   9Stage 4: 报告生成（标9HTML 报告，PNG 图表，无 SVG9```

### 跳过的阶9步骤

| 跳过9| 原因 | 风险 |
|--------|------|------|
| Phase 0 数据画像 | 小数据集可快速概9| 9|
| Phase 2.5 值规范化 | 简单数据集通常无需 | 中（需人工确认9|
| Stage 3 敏感9亚组/安全性分9| 快速模式仅做核心分9| 中（报告标注"未执99|
| Stage 3.7 结果解读会话 | 快速模式自动生成解9| 9|
| Phase 5 盲态审核| 9RCT 需要，快速模式默认非 RCT | 9|
| Stage 5 Paper Track | 快速模式不进入论文写作 | 9|

### 质量门闸缩减规则

| 门闸 | 标准模式 | Quick Mode |
|------|---------|------------|
| Stage 1.5 | 9 项检查| 5 项关键检查（项目 1/3/5/6/99|
| Stage 2.5 | 8 项检查| 跳过（使用模9SAP9|
| Stage 3.5 | 14 项检查| 7 项关键检查（项目 1/2/3/5/9/10/119|

### 输出格式

- 报告：HTML 格式，无 SVG 图表，仅 PNG
- 表格：标准三线表（docx9- 标注：报告头部标9[Quick Mode] 9精简流程，非完整分析"

### 示例

```
用户9快速分析这个CSV"
9Pipeline 检查 数据 8 变量 × 85 99自动进入 Quick Mode
9Stage 1 快速验99Stage 1.5 (59 9Stage 2 模板 SAP
9Stage 3 核心分析 9Stage 3.5 (79 9Stage 4 HTML 报告
95 分钟内输出基础报告
```

> [IRON RULE] Quick Mode 不得用于复杂研究设计（多中心 RCT、复杂观察性研究等）。检测到复杂设计时自动升级为标准模式并提示用户9
### Stage 执行时间估算

| Stage | 数据规模 | 预计时间 | 主要耗时 |
|-------|---------|---------|---------|
| Stage 0 | 任意 | <309| 数据类型识别 |
| Stage 1 | 500行909| 5-15分钟 | 数据验证+清洗+EDA |
| Stage 1.5 | - | <309| 门闸检查|
| Stage 2 | 任意 | 10-30分钟 | EDA+方法讨论+SAP制定 |
| Stage 2.5 | - | 1-5分钟 | SAP审查 |
| Stage 3 | 500行909| 10-30分钟 | 代码生成+执行+自愈 |
| Stage 3.5 | - | <1分钟 | 门闸检查149 |
| Stage 4 | - | 5-15分钟 | 报告生成+statcheck |
| Stage 5 | - | 30-120分钟 | 论文写作 |
| **总计(Stage 1-4)** | **500行909* | **30-90分钟** | - |
| **Quick Mode** | **500行909* | **10-20分钟** | - |

### 常见流水线错误与解决方案

| 错误场景 | 症状 | 解决方案 |
|---------|------|---------|
| Stage 1 数据读取失败 | FileNotFoundError/EncodingError | 检查文件路径和编码(UTF-8/GBK)，提示用户确认格9|
| Stage 1.5 门闸阻断 | 缺失清洗日志/锁定记录 | 退回Stage 1补充产物，不跳过门闸 |
| Stage 2 SAP审查不收9| 连续3次退9| 触发收敛检测→BLOCK→用户书面接受风险→标注[CONVERGED] |
| Stage 3 代码执行失败 | Python/R报错 | 自愈机制5轮重试→仍失败则标记[SKIP]并记9|
| Stage 3.5 P值格式不合规 | P=0.000 | 退回Stage 3修复(P-R01规则)→重新通过门闸 |
| Stage 4 statcheck失败 | 统计结果不一9| 标记[STATCHECK_FAILED]→退回Stage 3核查 |
| Passport状态丢9| 无法恢复进度 | 从stage产物重建passport→验证一致性→继续 |
| 用户中途切换研究类9| 类型不匹9| 重置Stage 2-4→保留Stage 1产物→重新规9|

---

## 反例与黑名单

> **以下行为必须避免**。作为编排器，你的核心职责是**调度和追9*，而非执行实质性工作9> 完整医学统计反模式目录参见：shared/anti-patterns/medical_stats_anti_patterns.md（B2/B39
### 🚫 编排器角色禁9
| # | 禁止行为 | 为什9| 正确做法 |
|---|---------|--------|---------|
| 1 | 自己执行统计分析、生成报告等实质性工9| 违反"纯调度架9定位，破坏职责边9| 9dispatch 到对9skill，不自己执行 |
| 2 | 跳过前置检查直接进入下一阶段 | 前置产物缺失会导致后续分析无依据 | Mid-Entry 前置检查必须执行，缺失则回退 |
| 3 | **自动跳过 MANDATORY Checkpoint** | 用户失去关键决策控制，可能产生意外结9| SLIM/ADAPTIVE 可跳过，**MANDATORY 必须暂停等待用户确认** |
| 4 | 忽略用户信号冲突（多个信号指向不同阶段） | 可能路由到错误阶9| 多信号时取最强信号，或询问用户确9|

### 🚫 阶段跳转禁忌

| # | 禁止行为 | 为什9| 正确做法 |
|---|---------|--------|---------|
| 5 | 9Stage 1 直接跳到 Stage 2 | 跳过数据质量门闸，数据问题可能带入分析阶9| 必须经过 Stage 1.5 门闸检查|
| 6 | Stage 1.5 质量门闸未通过就进9Stage 2 | 数据质量未保证，后续分析全部不可9| 🔴 Blocking：Stage 1.5 全部通过或用户书面接受风9|
| 7 | 9Stage 1 直接跳到 Stage 4 | 跳过分析计划和执行，报告无依9| 必须按顺序：Stage 1 91.5 92 92.5 93 93.5 94 |
| 8 | Stage 2 SAP 审查未通过就进9Stage 3 | 有缺陷的计划会导致后续分析全部错9| [MANDATORY] SAP 审查通过后才可进9Stage 2.5 |
| 9 | Stage 2.5 质量门闸未通过就进9Stage 3 | SAP 质量未保证，分析结果不可9| 🔴 Blocking：Stage 2.5 全部通过或用户书面接受风9|
| 10 | Stage 3 质检未通过就进9Stage 4 | 错误结果会被写入报告 | [SLIM] 质检通过后才可进9Stage 3.5 |
| 11 | Stage 3.5 质量门闸未通过就进9Stage 4 | 结果可靠性未验证 | 🔴 Blocking：Stage 3.5 全部通过或用户书面接受风9|

### 🚫 进度追踪禁忌

| # | 禁止行为 | 为什9| 正确做法 |
|---|---------|--------|---------|
| 12 | 不更9Progress Dashboard | 用户无法了解当前状9| 每个 CHECKPOINT 必须更新进度 |
| 13 | 不记录产物版9| 无法追溯变更历史 | 产物追踪表必须记录版本和状9|
| 14 | 偏差不记录就继续执行 | 违反 GCP 规范，不可审核| Section 6.2 偏差记录必须执行 |

### 🚫 错误处理禁忌 🆕

| # | 禁止行为 | 为什9| 正确做法 |
|---|---------|--------|---------|
| 15 | 门闸回退时不更新回退计数9| 收敛检测依赖于准确的回退计数，不更新会导致门闸无限循9| 每次回退必须自增计数器，门闸消费后更9|
| 16 | 多阶段错误同时发生时从最后一个出错阶段修9| 下游阶段的问题可能是上游问题带入的，下游修复无法根治 | 从最早出错的阶段开始修复，固定一个再处理下一9|
| 17 | 异常发生时静默继续不告知用户 | 用户失去对意外情况的知情权和决策9| 所有异常（包括 ADAPTIVE 级别的）必须先展示并得到用户响应才继9|

### 🚫 检查点协议禁忌 🆕

| # | 禁止行为 | 为什9| 正确做法 |
|---|---------|--------|---------|
| 18 | 在高效模式下跳过 MANDATORY 检查点 | MANDATORY 是所有模式的硬性要求，SLIM 9ADAPTIVE 才可按模式跳9| 6 9MANDATORY 检查点（GATE-01~GATE-06）在任何模式下都必须展示并等待用户决9|
| 19 | 多个 MANDATORY 检查点同时触发时只展示最新的 | 当前阶段的信息不足以让用户做出跨阶段的风险决9| 同时触发9MANDATORY 检查点必须依次展示，上一点决策后再展示下一9|
| 20 | 用户选择详细引导模式但自动降级为高效模式 | 交互密度是用户显式选择的，自动降级违反信任 | 记录用户选择的模式，除非用户主动要求切换，不得自动升降级 |

---

## 11. Paper Track 扩展协议

> 以下内容合并9medical-pipeline skill，为 Stage 5 Paper Track 提供完整协议支持9
### 11.1 Paper Track State Machine

Stage 5 内部910-stage 状态转换定义：

| Stage | Name | Skill | Deliverables |
|-------|------|-------|-------------|
| 5.0 | PAPER INTAKE | (internal) | Handoff Bundle + 论文配置 |
| 5.1 | LITERATURE SEARCH | `systematic-survey` | RQ Brief + Bibliography + Synthesis |
| 5.2 | PAPER WRITING | `report` (论文模式) | Paper Draft |
| 5.3 | INTEGRITY | integrity_verification_agent | Integrity report + corrected paper |
| 5.4 | REVIEW | `peer-review` | 5 reviews + Editorial Decision + Revision Roadmap |
| 5.5 | REVISE | `report` (revision mode) | Revised Draft + Response to Reviewers |
| 5.6 | RE-REVIEW | `peer-review` (re-review) | Verification review report |
| 5.7 | RE-REVISE | `report` (revision mode) | Second revised draft (if needed) |
| 5.8 | FINAL INTEGRITY | integrity_verification_agent | Final verification (must 100% pass) |
| 5.9 | FINALIZE | `report` (format-convert) | Final Paper (MD/DOCX/PDF) |

**状态转换规9*9- Stage 5.2 9user confirmation 95.3
- Stage 5.3 9PASS 95.4 (FAIL 9fix and re-verify, max 3 rounds)
- Stage 5.4 9Accept 95.8 / Minor|Major 95.5 / Reject 95.2 or end
- Stage 5.5 9user confirmation 95.6
- Stage 5.6 9Accept|Minor 95.8 / Major 95.7
- Stage 5.7 9user confirmation 95.8
- Stage 5.8 9PASS (zero issues) 95.9 (FAIL 9fix and re-verify)
- Stage 5.9 9MD 9DOCX via Pandoc 9PDF 9end

### 11.2 Paper Track Adaptive Checkpoint System

**IRON RULE: After each Paper Track stage completion, the system must proactively prompt the user and wait for confirmation.**

#### Checkpoint Types

| Type | When Used | Content |
|------|-----------|---------|
| FULL | First checkpoint; after integrity boundaries; before finalization | Full deliverables list + decision dashboard + all options |
| SLIM | After 2+ consecutive "continue" on non-critical stages | One-line status + explicit continue/pause prompt |
| MANDATORY | Integrity FAIL; Review decision; Stage 5.9 | Cannot be skipped; requires explicit user input |

#### Decision Dashboard (shown at FULL checkpoints)

```
━━9Stage [X] [Name] Complete ━━9
Metrics:
- Word count: [N] (target: [T] +/-10%)    [OK/OVER/UNDER]
- References: [N] (min: [M])              [OK/LOW]
- Coverage: [N]/[T] sections drafted       [COMPLETE/PARTIAL]

Deliverables:
- [Material 1]
- [Material 2]

Flagged: [any issues detected, or "None"]

Ready to proceed to Stage [Y]? You can also:
1. View progress (say "status")
2. Adjust settings
3. Pause pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Adaptive Rules

1. First checkpoint: always FULL
2. After 2+ consecutive "continue": prompt user awareness
3. Integrity boundaries (Stage 5.3, 5.8): always MANDATORY
4. Review decisions (Stage 5.4, 5.6): always MANDATORY
5. Before finalization (Stage 5.9): always MANDATORY
6. After 4+ consecutive continue: insert FULL checkpoint regardless

#### Self-Check Questions (at every FULL checkpoint)

1. **Citation integrity**: Any unverified citations in latest output?
2. **Sycophantic concession**: Did latest stage uncritically accept all feedback?
3. **Quality trajectory**: Is latest output 9previous stage quality?
4. **Scope discipline**: Did latest stage add unrequested content?
5. **Completeness**: All required deliverables present?

### 11.3 Integrity Review Protocol

Stage 5.3 (pre-review) and Stage 5.8 (post-revision) verification. 5-phase protocol: references 9citation context 9statistical data 9originality 9claims.

**IRON RULE**: Stage 5.8 must PASS with zero issues to proceed to Stage 5.9.

**IRON RULE**: Both Stage 5.3 and 5.8 must also run the **AI Research Failure Mode Checklist** 97-mode taxonomy covering: citation hallucination, implementation bugs, hallucinated results, shortcut reliance, bug-as-insight, methodology fabrication, pipeline-level frame-lock. If any mode is `SUSPECTED` or Modes 1/3/5/6 are `INSUFFICIENT EVIDENCE`, pipeline blocks and user must acknowledge before proceeding.

### 11.4 Two-Stage Review Protocol

Stage 5.4 (full review, 5 reviewers) 9Revision Coaching 9Stage 5.5 9Stage 5.6 (re-review) 9optional Residual Coaching 9Stage 5.7.

- 5 independent reviewers: EIC + Methodology + Domain + Perspective + Devil's Advocate
- Editorial Decision: Accept / Minor Revision / Major Revision / Reject
- Revision Roadmap: prioritized modification suggestions
- Re-review: verification review focused on checking whether revisions address comments

### 11.5 Paper Track Agent Team

| # | Agent | Role | Stage |
|---|-------|------|-------|
| 1 | `pipeline_orchestrator_agent` | Main orchestrator: detect stage, recommend mode, trigger skill, manage transitions | All |
| 2 | `state_tracker_agent` | Record completed stages, produced materials, revision loop count | All |
| 3 | `integrity_verification_agent` | 100% reference/citation/data verification (blocking) | 5.3, 5.8 |
| 4 | `collaboration_depth_agent` | Observer (advisory only 9never blocks). Score user-AI collaboration pattern | FULL/SLIM checkpoints |
| 5 | `claim_ref_alignment_audit_agent` | Opt-in claim faithfulness auditor. Audit citations for claim 9reference alignment | Optional |

### 11.6 Cross-Session Resume (Opt-in)

Set `MSRA_PASSPORT_RESET=1` to promote FULL checkpoints to context-reset boundaries. Use `resume_from_passport=<hash>` in a fresh session to continue from the recorded stage.

**Gate (emit)**: `MSRA_PASSPORT_RESET=1` must be set in the emitting session.
**Gate (resume)**: No flag required. Any session can invoke `resume_from_passport=<hash>`.
**Intent**: Invoke in a fresh Claude Code session for token savings.

### 11.7 Mid-Conversation Reinforcement Protocol

At every Paper Track stage transition, the orchestrator MUST inject a brief core principles reminder:

```
--- STAGE TRANSITION: [Current] 9[Next] ---

🔄 Core Principles Reinforcement:
1. [Most relevant IRON RULE for the next stage]
2. [Most relevant Anti-Pattern to avoid]
3. Quality check: Is output of [Current] 9[Previous]? If not, PAUSE.

Checkpoint: [MANDATORY/ADVISORY] 9[What user needs to confirm]
---
```

### 11.8 External Review Protocol

Handles external (human) reviewer feedback integration. 4-step workflow: Intake & Structuring 9Strategic Revision Coaching 9Revision & Response 9Self-Verification.

### 11.9 Progress Dashboard

ASCII dashboard shown at FULL checkpoints:

```
══════════════════════════════════════9  MSRA Paper Track Progress
══════════════════════════════════════9  Stage 5.0 [Paper Intake]      9Done
  Stage 5.1 [Literature]        9Done
  Stage 5.2 [Writing]           🔄 Current
  Stage 5.3 [Integrity]         9Pending
  Stage 5.4 [Review]            9Pending
  Stage 5.5 [Revise]            9Pending
  Stage 5.6 [Re-review]         9Pending
  Stage 5.7 [Re-revise]         9Pending
  Stage 5.8 [Final Integrity]   9Pending
  Stage 5.9 [Finalize]          9Pending
══════════════════════════════════════9```

---

## 流水线反例与黑名单（核心八条9
> **以下 8 条为流水线编排核心禁止行9*，违反任何一条将导致流程不可追踪或结果不可信9
| # | 禁止行为 | 为什9| 正确做法 |
|---|---------|--------|---------|
| 1 | 跳过质量门闸直接进入下一阶段 | 门闸是质量保证的核心机制，跳过会导致未经验证的结果流入下9| 必须通过 Stage 1.5/2.5/3.5 门闸，未通过时退回或书面接受风险 |
| 2 | Material Passport 不记录偏差就修改分析结果 | 无偏差记录的修改破坏可审计性，无法追溯变更原因 | 任何偏离 SAP 的修改必须先记录偏差9passport.deviations |
| 3 | Stage 3.5 门闸检查时修改分析代码 | 门闸检查应只读，同时修改代码既当裁判又当选手 | 门闸检查只读分析结果，修改必须退9Stage 3 |
| 4 | 多数据集模式不检查跨中心一致性就汇9| 跨中心差异可能导致汇总结果误导，掩盖中心效应 | 必须执行 Phase 1b 跨中心一致性检查后再汇9|
| 5 | Quick Mode 用于复杂研究设计（如多中9RCT9| 精简流程跳过敏感9亚组分析，复杂设计下会遗漏关键发9| 检测到复杂设计时自动升级为标准模式 |
| 6 | 用户中止后不保存状态直接退9| 用户丢失已完成的工作，无法恢9| 必须保存当前状态到 passport，允9`/msra --resume` 恢复 |
| 7 | Paper Track 9Stage 4 未完成时启动 | 论文写作依赖 Stage 4 的报告、图表和表格，未完成时启动会导致论文缺失素材 | 入口守卫检查passport stage_4 == completed，未完成时拒绝进9|
| 8 | 收敛检测触发后仍继续退回而不转入偏差记录模式 | 无限循环退回浪费资源，且无法推进流9| 回退 93 次后必须9GATE-06 Checkpoint，转入偏差记录模9|



