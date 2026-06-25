# Phase 3: 制定 SAP

> **来源说明**: 本文件从 SKILL.md L831-950 抽取，内容与原文语义等价。
> **上游**: Phase 2 估计目标定义与方法确认
> **下游**: Phase 4 计划审查
> **Checkpoint**: CP-5（🟡 CHECKPOINT，SAP 文档生成后触发）

> 参考：shared/statistics-methods/methods_catalog.md 统计方法选择依据
> 参考：shared/statistics-methods/chapters/ch18-multiple-comparisons-methods.md 多重比较校正 (统计指南)
> 参考：shared/statistics-methods/chapters/ch19-gatekeeping-strategies.md 关口策略 (统计指南)
> 参考：shared/sap/sap_standard.md — SAP标准格式定义
> 参考：shared/sap/variable_selection_guide.md 变量选择与方法推荐指南
> 参考：shared/reporting-guidelines/SPIRIT_checklist.md **SPIRIT 2025 试验协议 34 项清单**（RCT 协议完整性）
> 参考：shared/risk-of-bias/ — **偏倚评估工具**（RoB 2/ROBINS-I V2/PROBAST+AI/QUADAS-2/GRADE）用于 SAP 中预设偏倚评估计划

确认方法后，**严格按照SAP标准格式**生成正式的统计分析计划文档。SAP必须包含:
1. 变量选择推荐（强制纳入/可选纳入/不纳入）
2. 统计方法选择推荐（主次要/敏感性分析）
3. 变量构建推荐与公式（构造逻辑、切点、依据）
4. **协议要素完整性自检（RCT 适用）**: 对照 `SPIRIT_checklist.md` 34 项，确保 SAP 涵盖 Item 9（设计）、Item 10（合格标准/多样性目标）、Item 11（干预）、Item 12（结局）、Item 14（样本量）、Item 22（统计方法含 Estimands 框架）；缺失项须在 SAP 末尾"协议完整性备注"中标注并提示用户补充

**Targeted-Context 机制**（借鉴 YH-SAP）：

> 传统 SAP 将所有分析上下文等权呈现，导致LLM 在执行时面临上下文过载和注意力稀释。
> Targeted-Context 机制为每个分析项仅提供**最小必要上下文**，减少噪音、提高执行精度。

**SAP Targeted-Context 的实现**:
| 分析 | 必需上下文（Targeted） | 排除上下文（噪音） |
|--------|----------------------|-------------------|
| 主要分析 | 方法+人群+终点+调整变量+假设 | 其他次要分析的方法细节 |
| 亚组分析 | 亚组变量+交互检查模型规格 | 主要分析的效应量数据 |
| 敏感性分析 | 与主分析的差异点+替代方法 | 主分析的完整代码 |
| 安全性分析 | AE编码+人群定义+汇总方法 | 疗效分析的方法细节 |

**SAP 结构中嵌入 Targeted-Context 标记**:
每个分析规范条目增加 `context_scope` 字段

```
| 分析 | 人群 | 方法 | 调整变量 | 假设 | context_scope |
|------|------|------|---------|------|--------------|
| 主要 | ITT | ANCOVA | 基线HbA1c | 正态线性方差 | [主要终点+调整变量] |
| 亚组 | ITT | ANCOVA×亚组 | 基线+交互 | 同上+交互可加 | [亚组变量+交互项] |
```

**SAP 中预定义 [SKIP] 触发条件**（借鉴 YH-SAP 诚实标记机制）：

> SAP 制定阶段就预定义哪些条件下分析应标记[SKIP]，而非在执行时临时判断
> 这避免了 LLM "硬做"不可行分析的倾向（反模式 E1）

| [SKIP] 触发条件 | 检测方法 | SAP 中的预定 |
|----------------|---------|---------------|
| 样本量不足 | 事件数 < 10×变量数 | "Cox 事件数 < 10/变量，标[SKIP: 事件数不足]" |
| 假设严重违反且转换失败 | Shapiro-Wilk P < 0.01 + 转换后仍 P < 0.01 | "如正态性严重违反且 Box-Cox 无效，标[SKIP: 假设违反]" |
| 关键变量缺失 > 40% | 缺失率统计 | "如主要终点缺失率 > 40%，标[SKIP: 数据不足]" |
| 完全分离 | Logistic 回归收敛警告 | "如检测到完全分离，自动切Firth；Firth 仍失败标[SKIP: 分离]" |
| 权重极端 | IPTW 权重 > 99th | "如截断后仍存在极端权重(>20)，标[SKIP: 权重不稳定]" |

**SAP 制定异常处理**
| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| SAP 模板与数据类型不匹配（如 Bayesian 模板用于频率派分析） | 切换为通用 SAP 模板并根据研究类型自动填充（RCT/观察性/诊断试验各一套） | 输出简化版 SAP 框架，标注"模板待完善" |
| 变量构造定义引用了不存在的原始字段 | 检查数据字典修正引用，或标记为"需补充" | 删除不可用变量，SAP 中标注"因数据不可得排除" |
| 方法选择与Estimands 矛盾（Estimands 定义 ITT 但方法启用PP） | 统一ITT（更保守）并在敏感性分析中加入 PP 分析 | 输出 ITT + PP 双版本 SAP，让用户选择 |
| SAP 可重复性细节严重不足（方法名称过泛、参数空缺处） | 逐项补充缺失方法参数（默认值从 ch 系列资料自动填充） | 标记 SAP "标记草稿"，强制退→ Phase 2 补充参数 |

**SAP 结构**
```markdown
# 统计分析计划 (Statistical Analysis Plan)

## 1. 研究概述
- 研究设计和目的
- 主要和次要假设
- 样本量依据

## 2. 分析人群
- ITT（意向性治疗）
- PP（符合方案）
- Safety（安全性）
- 亚组

## 3. 终点定义
- 主要终点
- 次要终点
- 探索性终点
- 安全性终点

## 4. 统计方法

### 4.1 主要分析
- 方法、调整变量、缺失数据处理

### 4.2 次要分析
- 敏感性分析
- 亚组分析

### 4.3 假设检查
- 计划的诊断检查
- 替代方法（假设违反时）

## 5. 多重比较控制
- 校正方法（Bonferroni, Hochberg, 序贯门控等）
- **图形化方法（Bretz 2009，多层级终点推荐）**: 用有向加权图表达 α 分配与传递，比固定关口策略更灵活；参考ch18 §5 + gMCPLite R 包
- 检验层次（主要 → 关键次要 → 其他次要）
- I 类错误率控制策略

## 6. 期中分析（RCT SAP 预定义了期中分析时点时启用）
- 期中分析时点（日历时点或信息比例）
- 决策策略（停止规则：优效/无效/有害）
- Alpha 消耗方法（O'Brien-Fleming, Pocock, Lan-DeMets）
- 数据监查委员会（DMC）职责（如成立）

## 7. 分析规范
| 分析 | 人群 | 方法 | 调整变量 | 假设 |
|------|------|------|---------|------|
```

---

## 条件章节: 多中心分析计划（multi-dataset 模式）

> 触发条件：passport multi_dataset_mode artifact 存在且状态为 completed

- **目的**: 为多中心研究制定汇总分析策略，明确中心效应处理方法
- **输入**: cross_site_consistency_report + 研究问题 + 研究类型
- **执行内容**:
  1. Estimands 汇总层面定义：
     - overall estimand（总体估计目标）
     - per-site estimand（各中心估计目标，如需）
  2. 中心效应处理策略选择（三选一）：
     - 固定效应模型：中心作为协变量（适用于中心间同质性高）
     - 随机效应模型：中心随机截距/斜率（适用于中心间异质性大）
     - 两步meta-analysis：先逐中心分析，meta 汇总（适用于中心间方法差异大）
  3. 异质性评估计划：
     - I² 统计量（<25%低异质，25-75%中异质，>75%高异质）
     - τ² 统计量（研究间方差）
     - Cochran's Q 检验（p<0.10 提示显著异质性）
  4. leave-one-out 敏感性分析计划：逐一排除各中心，评估结论稳健性
- **输出**：SAP 中增加"中心效应处理策略"章节
- **Checkpoint**: [SLIM] 展示策略选择后继续，用户可调整
- **参考**: shared/statistics-methods/chapters/ch34-treatment-effects-in-multicenter-rcts.md
- **Anti-pattern**: 不得在未评估异质性的情况下直接选择随机效应模型

---

## Phase 3 Checkpoint

**Checkpoint CP-5**（🟡 CHECKPOINT）:
- 触发位置: SAP 文档生成后
- 通过标准 (PASS): SAP 结构含全部7 章（概述/人群/终点/方法/多重比较/期中/规范表）；分析规范表已填写且含context_scope 列；SKIP 触发条件已预定义（至多3 项）
- 阻断标准 (BLOCK): 缺失章节 / 分析规范表为空 / 所有分析项context_scope 相同
- 升级动作: 补充默认值，标记 SAP "标记草稿"，不得直接定稿
