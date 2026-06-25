# MSRA 3-Sprint 重构方案（架构师阿奇 · Archi）

> **文档状态**: Proposed
> **日期**: 2026-06-29
> **作者**: 阿奇（Archi）· 系统架构师
> **依据**: 29号评估文档 + 源码逐行验证

---

# 第一部分：Sprint 1 — SKILL.md 瘦身（5 个文件）

## 瘦身总原则（ADR-001 细化）

**主 SKILL.md 保留 5 类内容**：
1. 角色定义（含 IRON RULES + 关键参考引用）
2. 架构集成图（ASCII 图 + 设计原则）
3. Phase 索引表（文件名 + 一句话说明 + 输入→输出）
4. 检查点汇总表（Checkpoint ID + 级别 + 触发条件）
5. 快速参考（命令表 + 模式表 + 关键产物表）

**主 SKILL.md 删除/抽取的内容**：
- Phase 详细执行步骤 → phases/ 目录
- 反例与黑名单 → 引用 shared/anti-patterns/（去重后保留一处引用）
- 重复的命令/模式节 → 删除（保留第一处）
- 内联的代码模板/异常处理表 → phases/ 或 shared/

---

## 1.1 analysis-exec/SKILL.md（1344 行 → ~300 行）

### 已有 phases/ 文件（7 个）
| 文件 | 覆盖 Phase |
|------|-----------|
| `00-exec-precheck.md` | Phase 0/0.5/0.6 |
| `01-variable-construction.md` | Phase 1 |
| `02-descriptive-stats.md` | Phase 2 |
| `03-inferential-analysis.md` | Phase 3（基础部分） |
| `04-quality-check.md` | Phase 4 |
| `05-output-artifacts.md` | Phase 5 |
| `06-audit-log.md` | Phase 6 |

### 需要新建的 phases/ 文件
| 文件 | 内容来源 |
|------|---------|
| `phases/03.1-observational-methods.md` | L718-793 观察性研究高级方法（IPTW/AIPW/RCS/E-value/亚组） |
| `phases/03.2-constraint-tracking.md` | L794-1029 统计约束追踪（方法/数据集/变量/P值四张表） |
| `phases/03.3-hybrid-prompting.md` | L521-615 Hybrid Prompting 模板 + 示例 |
| `phases/03.4-self-healing.md` | L616-662 自愈机制详细流程 + L606-614 错误分类阈值表 |

### 操作清单

| # | 操作类型 | 当前行号范围 | 内容描述 | 目标位置 | 说明 |
|---|---------|-------------|---------|---------|------|
| 1 | **保留** | L1-13 | YAML frontmatter | 主文件 | 版本号更新为 1.0.1 |
| 2 | **保留** | L14-16 | 标题 | 主文件 | — |
| 3 | **保留** | L17-46 | 角色定义（含 IRON RULES + 参考引用） | 主文件 | 精简引用列表，仅保留 3-4 个最核心引用 |
| 4 | **保留** | L47-93 | 架构集成图 + 设计原则 | 主文件 | — |
| 5 | **精简保留** | L94-135 | 快速开始（Hybrid 预览 + 快速路径 + 时间估算 + 常见错误） | 主文件 | 压缩为 ~20 行：仅保留快速路径 + 时间估算表。常见错误表移入 phases/00-exec-precheck.md |
| 6 | **保留** | L136-146 | 双 Agent 编排（Generator-Evaluator） | 主文件 | — |
| 7 | **保留** | L148-181 | 工作流程图 + 设计原则 | 主文件 | — |
| 8 | **保留** | L182-198 | Phase 详细规范说明 + Phase 文件索引 | 主文件 | 索引表增加新建的 03.1-03.4 |
| 9 | **保留** | L199-231 | 快速参考（模式表 + 检查点汇总 + 关键产物） | 主文件 | — |
| 10 | **保留** | L232-250 | 命令 + Mode | 主文件 | 保留唯一一份 |
| 11 | **删除** | L251-252 | 分隔线 | — | — |
| 12 | **改为引用** | L253-345 | 反例与黑名单（第一份） | 主文件→1 行引用 | 替换为：`> 完整反模式目录参见：[shared/anti-patterns/medical_stats_anti_patterns.md](../../shared/anti-patterns/medical_stats_anti_patterns.md)（A1/A3/B1/E1/E2/F1-F4）` |
| 13 | **删除** | L347-381 | Phase 0.5/0.6 内联内容 | 已在 phases/00-exec-precheck.md | 确认 phases/00 已包含此内容，若无则迁移 |
| 14 | **删除** | L383-401 | Phase 1 内联内容 | 已在 phases/01-variable-construction.md | 确认 phases/01 已包含此内容 |
| 15 | **删除** | L403-497 | Phase 2 内联内容 | 已在 phases/02-descriptive-stats.md | 确认 phases/02 已包含此内容 |
| 16 | **抽取** | L498-520 | Phase 3 引言 + 执行原则 | 合并到 phases/03-inferential-analysis.md | — |
| 17 | **抽取** | L521-615 | Hybrid Prompting 模板 + R 示例 | phases/03.3-hybrid-prompting.md（新建） | — |
| 18 | **抽取** | L616-662 | 自愈机制详细流程 + 错误分类阈值表 | phases/03.4-self-healing.md（新建） | — |
| 19 | **保留** | L663-679 | 检查点量化标准表 | 主文件 | 压缩为精简版，完整版移入 phases/ |
| 20 | **抽取** | L680-717 | 常见错误处理代码示例 + 错误诊断增强 + [SKIP] 机制 | 合并到 phases/03.4-self-healing.md | — |
| 21 | **抽取** | L718-793 | 观察性研究高级方法（Step 3.1.1-3.1.6） | phases/03.1-observational-methods.md（新建） | — |
| 22 | **抽取** | L794-803 | 统计约束追踪引言 | 合并到 phases/03.2-constraint-tracking.md | — |
| 23 | **抽取** | L801-1029 | 3.2.1-3.2.4 四张约束追踪表 + 假设检验 + SAP修正 + 多中心 | phases/03.2-constraint-tracking.md（新建） | 假设检验标准步骤也合并到 phases/03 |
| 24 | **删除** | L1028-1029 | 分隔线 | — | — |
| 25 | **删除** | L1030-1129 | Phase 4 内联内容 | 已在 phases/04-quality-check.md | 确认 phases/04 已包含此内容 |
| 26 | **删除** | L1130-1157 | Phase 5 内联内容 | 已在 phases/05-output-artifacts.md | 确认 phases/05 已包含此内容 |
| 27 | **删除** | L1158-1268 | Phase 6 内联内容 | 已在 phases/06-audit-log.md | 确认 phases/06 已包含此内容 |
| 28 | **删除** | L1269-1286 | 重复的命令 + Mode 节 | — | 与 L234-250 重复 |
| 29 | **删除** | L1288-1344 | 反例与黑名单（第二份，与 L253-345 完全重复） | — | P0-2 修复：删除重复 |
| 30 | **新增** | 主文件末尾 | Phase 文件索引更新 | 主文件 | 添加 03.1-03.4 四个新文件到索引表 |

### 瘦身后主文件结构（~300 行）
```
L1-13:   YAML frontmatter（版本 1.0.1）
L14-16:  标题
L17-46:  角色定义（精简引用）
L47-93:  架构集成图 + 设计原则
L94-115: 快速开始（精简：快速路径 + 时间估算表）
L116-146:双 Agent 编排
L148-181:工作流程图 + 设计原则
L182-231:Phase 索引表（含 03.1-03.4）+ 快速参考
L232-250:命令 + Mode
L251-255:反例引用（1 行链接）
L256-300:检查点量化标准（精简版）
```

### phases/ 文件补充/新建清单
| 操作 | 文件 | 内容 |
|------|------|------|
| **验证补全** | `00-exec-precheck.md` | 确保包含 Phase 0.5 进度跟踪初始化 + Phase 0.6 变量名标准化确认 + 常见错误表 |
| **验证补全** | `03-inferential-analysis.md` | 确保包含 Phase 3 引言 + 执行原则 + 假设检验标准步骤 + SAP修正流程 + 多中心汇总 |
| **新建** | `03.1-observational-methods.md` | IPTW/AIPW/RCS/E-value/亚组分析（Step 3.1.1-3.1.6） |
| **新建** | `03.2-constraint-tracking.md` | 方法/数据集/变量/P值四张追踪表 + 违反处理规则 |
| **新建** | `03.3-hybrid-prompting.md` | 三层 Hybrid Prompting 模板 + R 代码示例 |
| **新建** | `03.4-self-healing.md` | 自愈 5 轮流程图 + 错误分类阈值表 + 诊断增强 + [SKIP] 机制 |

---

## 1.2 analysis-plan/SKILL.md（1191 行 → ~280 行）

### 已有 phases/ 文件（1 个）
| 文件 | 覆盖 Phase |
|------|-----------|
| `phases/01-deep-eda.md` | Phase 1 深度 EDA |

### 需要新建的 phases/ 文件
| 文件 | 内容来源 |
|------|---------|
| `phases/15-interactive-data-confirmation.md` | L294-519 Phase 1.5 交互式数据要素确认（7 个 Step） |
| `phases/02-estimand-definition.md` | L521-830 Phase 2 估计目标定义与方法确认（含决策树） |
| `phases/03-sap-authoring.md` | L831-950 Phase 3 制定 SAP |
| `phases/04-review-confirm.md` | L951-1056 Phase 4 审查 + Phase 4.5 SAP 用户强制确认 |
| `phases/05-variable-construction-def.md` | L1057-1105 Phase 5 变量构造定义 + DAG 预览 |

> **注意**：Phase 文件索引表（L185-195）已列出这些文件名，但实际文件不存在。Sprint 1 的核心任务就是创建这些文件。

### 操作清单

| # | 操作类型 | 当前行号范围 | 内容描述 | 目标位置 | 说明 |
|---|---------|-------------|---------|---------|------|
| 1 | **保留** | L1-14 | YAML frontmatter | 主文件 | 版本号更新为 0.9.4 |
| 2 | **保留** | L15-16 | 标题 | 主文件 | — |
| 3 | **保留** | L18-26 | 角色定义（含 IRON RULES） | 主文件 | — |
| 4 | **精简保留** | L27-74 | 快速开始（迷你SAP示例 + Quick模式 + 时间估算 + 常见错误） | 主文件 | 压缩为 ~15 行：仅保留 Quick 模式说明 + 时间估算表 |
| 5 | **保留** | L76-89 | 研究类型分支表 | 主文件 | — |
| 6 | **保留** | L90-100 | Phase 流转指南 | 主文件 | — |
| 7 | **保留** | L101-138 | 架构集成图 | 主文件 | — |
| 8 | **保留** | L140-167 | Phase 2 方法速查表 + Checkpoint Summary + 审查收敛检查 | 主文件 | — |
| 9 | **保留** | L178-231 | 工作流程 + Phase 索引 + 快速参考 | 主文件 | 索引表更新（标记新建文件已存在） |
| 10 | **保留** | L233-250 | 命令 + Mode | 主文件 | 保留唯一一份 |
| 11 | **改为引用** | L252-292 | 反例与黑名单 | 主文件→1 行引用 | 替换为引用链接 |
| 12 | **抽取** | L294-519 | Phase 1.5 交互式数据要素确认（7 个 Step） | phases/15-interactive-data-confirmation.md（新建） | 含 Step 1.5.0-1.5.6 + 输出格式 + 模式差异 |
| 13 | **抽取** | L521-830 | Phase 2 估计目标定义与方法确认（含决策树） | phases/02-estimand-definition.md（新建） | 含 Step 2.1 Estimands + Step 2.2 方法选择决策树 + Step 2.3 参数确认 |
| 14 | **抽取** | L831-950 | Phase 3 制定 SAP | phases/03-sap-authoring.md（新建） | 含 Targeted-Context 机制 + SKIP 预定义 + SAP 结构 + 多中心条件章节 |
| 15 | **抽取** | L951-1056 | Phase 4 审查 + Phase 4.5 用户强制确认 | phases/04-review-confirm.md（新建） | — |
| 16 | **抽取** | L1057-1105 | Phase 5 变量构造定义 + DAG 预览 | phases/05-variable-construction-def.md（新建） | — |
| 17 | **删除** | L1106-1124 | 重复的命令 + Mode 节 | — | 与 L233-250 重复 |
| 18 | **删除** | L1125-1191 | 重复的反例与黑名单 | — | 与 L252-292 重复 |

### 瘦身后主文件结构（~280 行）
```
L1-14:   YAML frontmatter（版本 0.9.4）
L15-16:  标题
L18-26:  角色定义
L27-42:  快速开始（精简）
L44-89:  研究类型分支 + Phase 流转指南
L90-138: 架构集成图
L140-176:方法速查表 + Checkpoint Summary + 收敛检查
L178-250:工作流程 + Phase 索引 + 快速参考 + 命令 + Mode
L251-255:反例引用（1 行链接）
L256-280:检查点量化标准（精简版）
```

---

## 1.3 report/SKILL.md（1247 行 → ~250 行）

### 已有 phases/ 文件（1 个）
| 文件 | 覆盖 Phase |
|------|-----------|
| `phases/00-result-interpretation.md` | Phase 0/1 结果解读 |

### 需要新建的 phases/ 文件
| 文件 | 内容来源 |
|------|---------|
| `phases/02-table-generation.md` | L406-519 Phase 2 表格生成与导出 |
| `phases/03-figure-integration.md` | L520-680 Phase 3 图表整合 |
| `phases/04-methodology.md` | L681-736 Phase 4 方法学描述 |
| `phases/05-consistency-check.md` | L737-880 Phase 5 一致性校验（含 statcheck） |
| `phases/06-report-assembly.md` | L881-950 Phase 6 报告组装 |
| `phases/07-paper-writing.md` | L1096-1247 论文写作模式（12 Agent + 11 Mode + 8 Phase） |

### 操作清单

| # | 操作类型 | 当前行号范围 | 内容描述 | 目标位置 | 说明 |
|---|---------|-------------|---------|---------|------|
| 1 | **保留** | L1-16 | YAML frontmatter | 主文件 | 版本号更新为 0.9.3；description 移除论文写作描述 |
| 2 | **保留** | L17-19 | 标题 | 主文件 | — |
| 3 | **保留** | L20-49 | 角色定义（含 IRON RULES + 模式选择 + 参考引用） | 主文件 | 精简引用列表 |
| 4 | **保留** | L50-128 | 报告生成流程图 + 架构集成图 + 设计原则 | 主文件 | — |
| 5 | **精简保留** | L129-218 | 快速开始（P值示例 + 变量命名 + 自动化 + 快速路径 + 时间估算 + 常见错误） | 主文件 | 压缩为 ~15 行：仅保留快速路径 + 时间估算表 |
| 6 | **保留** | L219-257 | 报告模板速查（RCT/观察性/诊断试验） | 主文件 | — |
| 7 | **保留** | L258-341 | 工作流程 + Phase 索引 + 快速参考 | 主文件 | 索引表更新（标记新建文件已存在） |
| 8 | **保留** | L344-360 | 命令 + Mode | 主文件 | 保留唯一一份 |
| 9 | **改为引用** | L363-405 | 反例与黑名单（第一份） | 主文件→1 行引用 | — |
| 10 | **抽取** | L406-519 | Phase 2 表格生成与导出（含 Step 2.1 Markdown + Step 2.2 docx） | phases/02-table-generation.md（新建） | — |
| 11 | **抽取** | L520-680 | Phase 3 图表整合（含分析类型→图类型映射 + 模板加载 + 执行 + 异常处理） | phases/03-figure-integration.md（新建） | — |
| 12 | **抽取** | L681-736 | Phase 4 方法学描述 | phases/04-methodology.md（新建） | — |
| 13 | **抽取** | L737-880 | Phase 5 一致性校验（含 statcheck + 反模式检查 + 约束合规 + 图表质量 + 学术标准） | phases/05-consistency-check.md（新建） | — |
| 14 | **抽取** | L881-950 | Phase 6 报告组装 | phases/06-report-assembly.md（新建） | — |
| 15 | **保留** | L951-974 | 检查点量化标准 + 故障处理与降级策略 | 主文件 | 精简为表格式 |
| 16 | **删除** | L976-998 | 重复的命令 + Mode 节 | — | 与 L344-360 重复 |
| 17 | **删除** | L999-1055 | 重复的反例与黑名单 | — | 与 L363-405 重复 |
| 18 | **保留** | L1057-1095 | ★ STAGE 4 CHECKPOINT | 主文件 | — |
| 19 | **抽取** | L1096-1247 | 论文写作模式（双模式架构 + 12 Agent + 11 Mode + 8 Phase + 引用格式 + Generator-Evaluator 合同 + 反例） | phases/07-paper-writing.md（新建） | 独立为完整的论文写作规范文件 |

### 瘦身后主文件结构（~250 行）
```
L1-16:   YAML frontmatter（版本 0.9.3）
L17-19:  标题
L20-49:  角色定义（精简引用）
L50-128: 流程图 + 架构图 + 设计原则
L129-145:快速开始（精简）
L146-185:报告模板速查 + 工作流程 + Phase 索引
L186-220:快速参考 + 命令 + Mode
L221-225:反例引用（1 行链接）
L226-250:检查点量化标准 + STAGE 4 CHECKPOINT
```

---

## 1.4 calibration/SKILL.md（1061 行 → ~200 行）

### 已有 phases/ 文件
**无** — 需要新建 phases/ 目录

### 需要新建的 phases/ 文件
| 文件 | 内容来源 |
|------|---------|
| `phases/mode1-standard-calibration.md` | L211-317 标准校准（工作流程 + 检查点 + 金标准格式 + 异常处理 + 引擎调用） |
| `phases/mode2-status.md` | L318-357 状态查看 |
| `phases/mode3-incremental-update.md` | L358-397 增量更新 |
| `phases/mode4-gate-check.md` | L398-422 门闸校验 |
| `phases/mode5-external-bench.md` | L622-751 外部基准评估（StatLLM + MedHELM + RWE-LLM + 异常处理 + 禁忌） |
| `phases/mode6-replicate.md` | L796-889 复现验证 |
| `phases/mode7-fairness.md` | L891-1028 公平性校准 |

### 需要抽取到 shared/ 的内容
| 目标 | 内容来源 |
|------|---------|
| `shared/calibration/calibration_protocol.md`（新建） | L423-461 与 Pipeline 集成 + 门闸联动规则 |
| `shared/calibration/calibration_report_template.md`（新建） | L463-513 校准报告模板 |
| `shared/calibration/self_validation.md`（新建） | L544-576 校准系统自校验（3 项自检） |
| `shared/calibration/data_accumulation.md`（新建） | L577-621 真实校准数据积累机制 |
| `shared/calibration/gate_linkage_rules.md`（新建） | L752-795 门闸联动详细规则 |

### 操作清单

| # | 操作类型 | 当前行号范围 | 内容描述 | 目标位置 | 说明 |
|---|---------|-------------|---------|---------|------|
| 1 | **保留** | L1-18 | YAML frontmatter | 主文件 | 版本号更新为 0.9.2 |
| 2 | **保留** | L19-21 | 标题 | 主文件 | — |
| 3 | **保留** | L22-31 | 角色定义（含 IRON RULES） | 主文件 | — |
| 4 | **保留** | L33-51 | 校准模式选择流程图 | 主文件 | — |
| 5 | **保留** | L53-97 | 架构集成图 + 设计原则 | 主文件 | — |
| 6 | **精简保留** | L98-174 | 快速开始（标准校准示例 + 决策树 + 简化路径 + 指标公式 + 时间估算 + 常见错误） | 主文件 | 压缩为 ~20 行：仅保留决策树 + 时间估算表。指标公式表移入 shared/calibration/ |
| 7 | **保留** | L175-210 | 工作模式（模式检测 + 决策树） | 主文件 | — |
| 8 | **抽取** | L211-317 | 模式 1: 标准校准 | phases/mode1-standard-calibration.md（新建） | — |
| 9 | **抽取** | L318-357 | 模式 2: 状态查看 | phases/mode2-status.md（新建） | — |
| 10 | **抽取** | L358-397 | 模式 3: 增量更新 | phases/mode3-incremental-update.md（新建） | — |
| 11 | **抽取** | L398-422 | 模式 4: 门闸校验 | phases/mode4-gate-check.md（新建） | — |
| 12 | **抽取** | L423-461 | 与 Pipeline 的集成 | shared/calibration/calibration_protocol.md（新建） | — |
| 13 | **抽取** | L463-513 | 校准报告模板 | shared/calibration/calibration_report_template.md（新建） | — |
| 14 | **改为引用** | L514-543 | 反例与黑名单 | 主文件→1 行引用 | — |
| 15 | **抽取** | L544-576 | 校准系统自校验 | shared/calibration/self_validation.md（新建） | — |
| 16 | **抽取** | L577-621 | 真实校准数据积累机制 | shared/calibration/data_accumulation.md（新建） | — |
| 17 | **抽取** | L622-751 | 模式 5: 外部基准评估 | phases/mode5-external-bench.md（新建） | — |
| 18 | **抽取** | L752-795 | 门闸联动详细规则 | shared/calibration/gate_linkage_rules.md（新建） | — |
| 19 | **抽取** | L796-889 | 模式 6: 复现验证 | phases/mode6-replicate.md（新建） | — |
| 20 | **抽取** | L891-1028 | 模式 7: 公平性校准 | phases/mode7-fairness.md（新建） | — |
| 21 | **保留** | L1031-1061 | 检查点量化标准 + 边缘场景 + 核心禁令 | 主文件 | 精简为表格式 |

### 瘦身后主文件结构（~200 行）
```
L1-18:   YAML frontmatter（版本 0.9.2）
L19-21:  标题
L22-31:  角色定义
L33-51:  模式选择流程图
L53-97:  架构集成图 + 设计原则
L98-120: 快速开始（精简：决策树 + 时间估算）
L121-170:工作模式（模式检测表）+ 模式索引表（新增）
L171-175:反例引用（1 行链接）
L176-200:检查点量化标准 + 边缘场景
```

---

## 1.5 pipeline/SKILL.md（785 行 → ~400 行）

### 已有 phases/ 文件
**无** — pipeline 是编排器，phases/ 抽取策略与其他 SKILL 不同

### 需要新建的文件
| 文件 | 内容来源 |
|------|---------|
| `shared/quality_gates/gate-data.md` | L196-232 Stage 1.5 DATA QUALITY GATE |
| `shared/quality_gates/gate-sap.md` | L249-274 Stage 2.5 SAP QUALITY GATE |
| `shared/quality_gates/gate-results.md` | L299-337 Stage 3.5 RESULTS QUALITY GATE |
| `shared/checkpoint_protocol.md` | L363-461 Checkpoint Protocol（三级分层） |

### 操作清单

| # | 操作类型 | 当前行号范围 | 内容描述 | 目标位置 | 说明 |
|---|---------|-------------|---------|---------|------|
| 1 | **保留** | L1-14 | YAML frontmatter | 主文件 | 版本号更新为 0.3.2 |
| 2 | **保留** | L16-21 | 标题 + IRON RULE | 主文件 | — |
| 3 | **保留** | L24-82 | §1 Pipeline Stages（流程图） | 主文件 | — |
| 4 | **保留** | L83-172 | §2 Intent Detection & Mid-Entry + §2.1 研究类型识别 + §2.5 用户类型预判 | 主文件 | — |
| 5 | **保留** | L173-195 | §3 Stage Dispatching 开头 + Stage 1 | 主文件 | — |
| 6 | **抽取** | L196-232 | Stage 1.5 DATA QUALITY GATE 检查清单 | shared/quality_gates/gate-data.md（新建） | 主文件保留 2 行引用 + 阻断规则摘要 |
| 7 | **保留** | L233-248 | Stage 2 ANALYSIS PLAN | 主文件 | — |
| 8 | **抽取** | L249-274 | Stage 2.5 SAP QUALITY GATE 检查清单 | shared/quality_gates/gate-sap.md（新建） | 主文件保留 2 行引用 + 阻断规则摘要 |
| 9 | **保留** | L275-298 | Stage 3 ANALYSIS EXEC | 主文件 | — |
| 10 | **抽取** | L299-337 | Stage 3.5 RESULTS QUALITY GATE 检查清单 | shared/quality_gates/gate-results.md（新建） | 主文件保留 2 行引用 + 阻断规则摘要 |
| 11 | **保留** | L338-360 | Stage 4 REPORT | 主文件 | — |
| 12 | **抽取** | L363-461 | §4 Checkpoint Protocol（三级分层 MANDATORY/SLIM/ADAPTIVE） | shared/checkpoint_protocol.md（新建） | 主文件保留 5 行引用 + 三级定义摘要表 |
| 13 | **保留** | L464-531 | §5 Progress Tracking（Passport） | 主文件 | — |
| 14 | **改为引用** | L533-595 | §6 Agent Dispatch Mode | 主文件→引用 agents/ | 保留角色切换规则图 + Agent 速查表（精简），详细定义引用 agents/AGENTS.md |
| 15 | **保留** | L598-661 | §7 Error Handling & Rollback | 主文件 | — |
| 16 | **保留** | L664-685 | §8 Quick Reference Commands | 主文件 | — |
| 17 | **保留** | L688-747 | §9 Interaction Examples | 主文件 | — |
| 18 | **改为引用** | L750-785 | 反例与黑名单 | 主文件→1 行引用 | — |

### 瘦身后主文件结构（~400 行）
```
L1-14:    YAML frontmatter（版本 0.3.2）
L16-21:   标题 + IRON RULE
L24-82:   §1 Pipeline Stages
L83-172:  §2 Intent Detection + §2.1 研究类型 + §2.5 用户类型
L173-195: §3 Stage 1 Dispatching
L196-200: Stage 1.5 引用（gate-data.md）
L201-225: Stage 2 Dispatching
L226-230: Stage 2.5 引用（gate-sap.md）
L231-265: Stage 3 Dispatching
L266-270: Stage 3.5 引用（gate-results.md）
L271-300: Stage 4 Dispatching
L301-320: §4 Checkpoint Protocol 引用（checkpoint_protocol.md）+ 三级摘要
L321-380: §5 Progress Tracking + §6 Agent Dispatch（精简引用）
L381-400: §7 Error Handling + §8 Commands + 反例引用
```

---

# 第二部分：Sprint 2 — 架构解耦

## 2.1 质量门闸独立化（ADR-002）

### 需要创建的 shared/quality_gates/*.md 文件

#### 2.1.1 `shared/quality_gates/gate-data.md`
- **来源**: pipeline/SKILL.md L196-232
- **门闸名称**: Stage 1.5 DATA QUALITY GATE
- **内容结构**:
  ```markdown
  # Gate: DATA QUALITY (Stage 1.5)
  
  ## 输入
  - cleaned_data + cleaning_log + blind_audit_record + db_lock_record
  
  ## 检查清单（9 项）
  | # | 检查项 | 通过标准 | 关键项 |
  |---|--------|---------|--------|
  | 1 | 清洗日志完整 | 所有变更记录在案 | 否 |
  | 2 | 变量定义明确 | 衍生变量构造逻辑清晰 | 否 |
  | 3 | 缺失机制评估 | MCAR/MAR/MNAR 已评估 | 否 |
  | 4 | 盲态审核完成 | 无未解决质疑 | 否 |
  | 5 | 数据库锁定确认 | 版本号+时间已记录 | ✅ 硬阻断 |
  | 6 | 逻辑一致性验证 | 日期顺序/范围约束自洽 | ✅ 硬阻断 |
  | 7 | 值规范化完成 | 无遗留非标准值 | ✅ 硬阻断 |
  | 8 | 可重复性 | 清洗脚本可独立运行 | 否 |
  | 9 | 隐私合规完成 | PHI 已脱敏/处理 | ✅ 硬阻断 |
  
  ## 判定规则
  - 全部通过 (9/9) → ✅ PASS
  - 条件通过 (7-8/9, ≤2 项非关键项) → ⚠️ CONDITIONAL
  - 阻断 (<7/9 或 关键项 5/6/7/9 任一未通过) → ❌ BLOCK
  
  ## 输出
  gate_result: { gate: "data_quality", passed: bool, total: 9, failed_items: [], conditional: bool }
  ```

#### 2.1.2 `shared/quality_gates/gate-sap.md`
- **来源**: pipeline/SKILL.md L249-274
- **门闸名称**: Stage 2.5 SAP QUALITY GATE
- **内容结构**: 同上格式，8 项检查，关键项为 3/5/7

#### 2.1.3 `shared/quality_gates/gate-results.md`
- **来源**: pipeline/SKILL.md L299-337
- **门闸名称**: Stage 3.5 RESULTS QUALITY GATE
- **内容结构**: 同上格式，14 项检查，关键项为 1/3/4/10/11/12/13

### 标准化门闸接口定义

所有门闸文件遵循统一接口规范：

```markdown
# Gate: {GATE_NAME} (Stage {X.Y})

## 元数据
- gate_id: "data_quality" | "sap_quality" | "results_quality"
- stage: "1.5" | "2.5" | "3.5"
- blocking: true
- skill_source: "data-prep" | "analysis-plan" | "analysis-exec"

## 输入
| 参数 | 类型 | 来源 | 必填 |
|------|------|------|------|
| ... | ... | ... | ... |

## 检查清单
| # | 检查项 ID | 检查项 | 通过标准 | 阻断标准 | 关键项 | 降级策略 |

## 判定规则
- PASS: 全部通过
- CONDITIONAL: ≤N 项非关键项未通过
- BLOCK: >N 项未通过 或 任一关键项未通过

## 输出 (gate_result schema)
| 字段 | 类型 | 说明 |
|------|------|------|
| gate | string | 门闸 ID |
| passed | bool | 是否通过 |
| total | int | 总检查项数 |
| passed_count | int | 通过项数 |
| failed_items | string[] | 未通过项 ID 列表 |
| conditional | bool | 是否条件通过 |
| blocking_items | string[] | 硬阻断项列表 |
| timestamp | ISO8601 | 检查时间 |

## 与 Pipeline 的联动
- BLOCK → 退回前一 Stage
- 回退 ≥ 2 次 → 触发收敛检测（见 §7.3）
- CONDITIONAL → 记录风险后继续
```

### 现有 shared/quality_gates/ Python 代码的关系
现有 `check_items.py` / `gate_runner.py` / `inference_runner.py` 是门闸的**执行引擎**。新建的 `.md` 文件是门闸的**规范定义**。两者关系：
- `.md` 文件定义检查项、判定规则、接口契约
- `.py` 文件实现自动化检查执行
- Pipeline SKILL.md 通过引用 `.md` 文件加载门闸定义，调用 `.py` 执行检查

---

## 2.2 Agent 角色单一化（ADR-003）

### 需要从 SKILL.md 中删除的内联角色定义

| SKILL.md | 行号范围 | 内联角色定义内容 | 改为引用 |
|---------|---------|----------------|---------|
| analysis-exec/SKILL.md | L136-146 | 双 Agent 编排（Generator-Evaluator）中的 Agent 角色描述 | 保留编排图，Agent 定义引用 `agents/exec_runner_agent.md` + `agents/exec_inference_agent.md` |
| pipeline/SKILL.md | L533-595 | §6 Agent Dispatch Mode 中的角色切换规则 + Agent 角色卡速查 | 保留角色切换图（精简），Agent 定义引用 `agents/AGENTS.md` |

### 引用方式标准化

各 SKILL.md 中的 Agent 引用统一格式：

```markdown
## Agent 编排

> Agent 角色定义参见：
> - [Exec Runner Agent](../../agents/exec_runner_agent.md) — Phase 0-6 代码生成与执行
> - [Exec Inference Agent](../../agents/exec_inference_agent.md) — Phase 7-9 假设检验与质检
> 
> 完整协作协议参见 [agents/AGENTS.md](../../agents/AGENTS.md)

Generator → Exec Runner (Phase 0-6) → Exec Inference (Phase 7-9) → Checkpoint
```

### agents/*.md 文件验证清单
确保以下文件包含完整角色定义（如缺失则补充）：
- [ ] `agents/data_validator_agent.md` — Stage 1 角色
- [ ] `agents/method_consultant_agent.md` — Stage 2 角色
- [ ] `agents/exec_runner_agent.md` — Stage 3 Phase 0-6 角色
- [ ] `agents/exec_inference_agent.md` — Stage 3 Phase 7-9 角色
- [ ] `agents/qc_inspector_agent.md` — Stage 1.5/2.5/3.5 角色
- [ ] `agents/AGENTS.md` — 协作协议 + Handoff 格式
- [ ] `agents/protocol.md` — 异常上报规则

---

## 2.3 commands 统一

### manifest.json 与 skills/ 对齐操作清单

**现状**：manifest.json 定义了 18 个命令（含 `/msra-cross`, `/msra-bio`, `/msra-imaging`, `/msra-rt`），但部分命令的 entry_point 指向 `commands/*.md` 而非 `skills/*/SKILL.md`。

| 命令 | manifest entry_point | 实际指向 | 对齐操作 |
|------|---------------------|---------|---------|
| `/msra` | `skills/pipeline/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-paper` | `skills/pipeline/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-data` | `skills/data-prep/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-explore` | `skills/exploratory-causal/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-plan` | `skills/analysis-plan/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-exec` | `skills/analysis-exec/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-report` | `skills/report/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-calibrate` | `skills/calibration/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-write` | `commands/msra-write.md` | ⚠️ commands/ | 评估是否需要迁移到 skills/ 或保持 commands/ |
| `/msra-full` | `commands/msra-full.md` | ⚠️ commands/ | 同上 |
| `/msra-reviewer` | `commands/msra-reviewer.md` | ⚠️ commands/ | 同上 |
| `/msra-modules` | `commands/msra-modules.md` | ⚠️ commands/ | 同上 |
| `/msra-status` | `commands/msra-status.md` | ⚠️ commands/ | 同上 |
| `/msra-cross` | `skills/cross-domain/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-bio` | `skills/bioinformatics/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-imaging` | `skills/imaging-analysis/SKILL.md` | ✅ skills/ | 无需修改 |
| `/msra-rt` | `skills/realtime-monitor/SKILL.md` | ✅ skills/ | 无需修改 |

### commands/ 文件职责边界

**原则**：commands/ 文件仅作为**命令路由层**（解析参数 + 调用 skill），不包含实质性业务逻辑。

| 命令文件 | 职责 | 需要修改 |
|---------|------|---------|
| `commands/msra.md` | /msra 命令路由（已由 pipeline SKILL.md 覆盖） | 评估是否冗余 |
| `commands/msra-write.md` | 论文写作命令路由 → 调用 report skill 的 Paper Track | 保留，确保仅做路由 |
| `commands/msra-full.md` | 全流程命令路由 → 调用 pipeline SKILL.md | 保留，确保仅做路由 |
| `commands/msra-reviewer.md` | 审稿命令路由 → 调用 peer-review skill | 保留，确保仅做路由 |
| `commands/msra-modules.md` | 模块管理命令路由 | 保留 |
| `commands/msra-status.md` | 状态查询命令路由 → 读取 passport | 保留 |
| `commands/msra-calibrate.md` | 校准命令路由（已由 calibration SKILL.md 覆盖） | 评估是否冗余 |
| `commands/msra-data.md` | 数据准备命令路由（已由 data-prep SKILL.md 覆盖） | 评估是否冗余 |
| `commands/msra-exec.md` | 分析执行命令路由（已由 analysis-exec SKILL.md 覆盖） | 评估是否冗余 |
| `commands/msra-explore.md` | 探索分析命令路由（已由 exploratory-causal SKILL.md 覆盖） | 评估是否冗余 |
| `commands/msra-plan.md` | 分析计划命令路由（已由 analysis-plan SKILL.md 覆盖） | 评估是否冗余 |
| `commands/msra-report.md` | 报告命令路由（已由 report SKILL.md 覆盖） | 评估是否冗余 |
| `commands/msra-paper.md` | 论文命令路由（已由 pipeline SKILL.md 覆盖） | 评估是否冗余 |

**操作**：
1. 审查所有 commands/ 文件，确保它们仅包含参数解析 + 路由逻辑
2. 删除 commands/ 中与 SKILL.md 重复的实质性内容
3. 对于 entry_point 已指向 SKILL.md 的命令，评估 commands/ 文件是否可以删除（减少维护负担）

---

## 2.4 shared/INDEX.md

### 索引结构设计

```markdown
# shared/ 目录导航索引

> MSRA 共享资源目录。所有跨 Skill 复用的规范、模板、工具均存放于此。

## 按主题分类

### 质量保障 (Quality Assurance)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| quality_gates/gate-data.md | Stage 1.5 数据质量门闸定义 | pipeline |
| quality_gates/gate-sap.md | Stage 2.5 SAP 质量门闸定义 | pipeline |
| quality_gates/gate-results.md | Stage 3.5 结果质量门闸定义 | pipeline |
| quality_gates/gate_runner.py | 门闸执行引擎 | pipeline |
| quality_gates/check_items.py | 门闸检查项实现 | pipeline |
| checkpoint_protocol.md | 三级分层检查点协议 | pipeline |
| calibration/ | 校准框架（协议+模板+自检+积累机制+门闸联动） | calibration, pipeline |
| anti-patterns/medical_stats_anti_patterns.md | 医学统计反模式目录 | 所有 SKILL |

### 统计方法 (Statistics Methods)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| statistics-methods/ | 48 章统计指南 + 方法目录 + 决策树 + 约束规则 | analysis-plan, analysis-exec |
| causal-inference/ | 因果推断工作流 | analysis-plan, analysis-exec |
| sample-size/ | 样本量计算器 (Python/R) | analysis-plan |

### 报告规范 (Reporting Guidelines)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| reporting-guidelines/ | 21 个报告规范清单 (CONSORT/STROBE/STARD/...) | report, analysis-exec |
| journal-templates/ | 7 个期刊投稿格式模板 | report |

### 数据与变量 (Data & Variables)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| sap/ | SAP 标准格式 + 变量选择指南 + 模板 | analysis-plan |
| protocol_adherence/ | 方案遵循框架 + 方法一致性规则 + 进度跟踪模板 | analysis-exec |
| variable_standardization/ | 自动化变量标准化模块 | analysis-exec, report |

### 图表与模板 (Charts & Templates)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| chart-styles/ | 发表级图表标准 + 变量命名规范 | analysis-exec, report |
| templates/ | R/Python 代码模板（表格/图表/统计） | analysis-exec, report |
| report_assembler/ | HTML 报告渲染器 + Word 表格导出器 | report |

### 错误诊断 (Error Diagnostics)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| error-diagnostics/ | 错误模式库 + 自动修复建议 + 代码修复参考 | analysis-exec |

### 可复现性 (Reproducibility)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| reproducibility/ | 复现验证指南 + 检查脚本 + 报告生成器 | analysis-exec, pipeline |

### 偏倚评估 (Risk of Bias)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| risk-of-bias/ | RoB 2 / ROBINS-I V2 / QUADAS-2 / PROBAST / GRADE | analysis-plan |

### 合约与模式 (Contracts & Schemas)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| contracts/ | JSON Schema 合约（passport/evaluator/reviewer/audit） | pipeline, 所有 SKILL |
| passport/ | Material Passport 状态管理 | pipeline |
| handoff_schemas.md | Agent 间 Handoff 数据模式 | agents/ |

### 参考资源 (References)
| 文件/目录 | 说明 | 引用方 |
|-----------|------|--------|
| references/ | 术语表 + 审慎表达短语 + 字数规范 + IRB 术语 | report |
```

---

## 2.5 定义一致性审计（Sprint 1 审查发现 C-1/I-2 补救）

> 来源：代码审查师 Cody Sprint 1 全面审查发现 C-1 (CRITICAL) + I-2 (IMPORTANT)
> 根因：原始 SKILL.md 本身存在编码系统不一致，瘦身后合并到同一 phases/ 文件时冲突暴露

### 2.5.1 编码系统单一权威定义审计

**问题**：S-R01~R08 在 analysis-exec 原始 SKILL.md 中存在两份互相矛盾的定义（L949-963 和 L794-1029 区域），瘦身后合并到 phases/03.2-constraint-tracking.md 导致同文件内冲突。P-R/M-R/D-R/V-R 可能存在类似问题。

**操作**：对以下 5 个编码系统，确保每个编码在整个 skill 内只有一份权威定义：

| 编码系统 | 所在 skill | 检查方法 | 修复标准 |
|---------|-----------|---------|---------|
| S-R01~R08 | analysis-exec | grep 所有 phases/ 文件，确认每条 S-R 编码只出现一次定义 | 保留 Phase 4 质检节定义为权威版本，其他位置改为引用 |
| P-R01~R07 | analysis-exec + report | 跨 skill 搜索，确认 P-R 编码定义不冲突 | 以 analysis-exec phases/03.2 为权威源，report phases/05 改为引用 |
| M-R01~R08 | analysis-exec | grep phases/ 文件，确认单一定义 | 同上 |
| D-R01~R05 | analysis-exec | grep phases/ 文件，确认单一定义 | 同上 |
| V-R01~V07 | analysis-exec | grep phases/ 文件，确认单一定义 | 同上 |

**验证脚本**（新增）：
```bash
# scripts/audit_code_consistency.py
# 双向一致性检测：
#
# 方向 1 — 编码→定义（同一编码多定义冲突）：
#   对每个编码系统，扫描所有 phases/ 和 SKILL.md，报告每个编码的所有定义位置
#   如果同一编码有 >1 处定义，输出 CONFLICT 警告
#
# 方向 2 — 定义→编码（同一含义被分配不同编码）：
#   提取每条定义的关键语义（如"正态性违反""比例风险违反"等），
#   检查同一语义是否被映射到不同编码
#   如果同一语义对应多个编码，输出 SEMANTIC-DUPLICATION 警告
#
# C-1 根因正是方向 2 的违规：
#   第一份定义中 S-R01=正态性违反，第二份定义中 S-R02=正态性违反
#   同一含义被分配了不同编码，导致引用混乱
```

### 2.5.2 反模式代码可达性验证

**问题**：analysis-exec IRON RULES 引用 M1-M6 反模式代码，但 shared/anti-patterns/medical_stats_anti_patterns.md 中不存在这些代码（I-2）。这是 pre-existing 问题。

**操作**：
1. 扫描所有 SKILL.md + phases/ 文件中引用的反模式代码（格式如 A1/B1/E1/M1-F4 等）
2. 逐一验证这些代码在 `shared/anti-patterns/medical_stats_anti_patterns.md` 中存在
3. 对于不存在的代码：要么补充到 anti-patterns 文件，要么修正引用

### 2.5.3 引用可达性批量扫描

**问题**：Sprint 1 修复了 6 个丢失的 shared/ 引用（Task #18），但可能还有其他断链。

**操作**：对所有 SKILL.md 和 phases/ 文件中的以下引用类型做批量可达性验证：

| 引用类型 | 模式 | 验证方法 |
|---------|------|---------|
| shared/ 引用 | `shared/...` | 文件/目录存在性检查 |
| agents/ 引用 | `agents/...` 或 `../../agents/...` | 文件存在性检查 |
| phases/ 引用 | `phases/...` | 文件存在性检查 |
| 相对路径引用 | `../../...` | 从当前文件解析后验证存在性 |

**验证脚本**（新增）：
```bash
# scripts/scan_reference_reachability.py
# 扫描所有 .md 文件中的路径引用，报告断链
```

---

## 2.6 Pre-existing 问题修复

> Sprint 1 审查发现的 pre-existing 问题，在 Sprint 2 一并修复

### 2.6.1 agents/protocol.md 断链修复（I-1/R-16）

**问题**：pipeline/SKILL.md 中 3 处引用 `agents/protocol.md`，但该文件不存在。agents/ 目录中只有 `AGENTS.md` 和 `multi_agent_specification.md`。

**操作**（二选一）：
- **选项 A（推荐）**：创建 `agents/protocol.md`，包含异常上报规则 + Agent 间通信协议
- **选项 B**：将 pipeline/SKILL.md 中的 3 处引用改为 `agents/AGENTS.md`

### 2.6.2 calibration phases/ 命名规范化（S-2）

**问题**：calibration phases/ 使用 `mode1-standard-calibration.md` 命名，而 analysis-exec/report 使用 `00-xxx.md`、`01-xxx.md` 数字前缀命名。命名风格不一致。

**操作**：统一为数字前缀命名：
| 当前文件名 | 重命名为 |
|-----------|---------|
| mode1-standard-calibration.md | 01-standard-calibration.md |
| mode2-status.md | 02-status.md |
| mode3-incremental-update.md | 03-incremental-update.md |
| mode4-gate-check.md | 04-gate-check.md |
| mode5-external-bench.md | 05-external-bench.md |
| mode6-replicate.md | 06-replicate.md |
| mode7-fairness.md | 07-fairness.md |

重命名后同步更新 calibration/SKILL.md 中的 phases 索引表。

### 2.6.3 analysis-exec phases/03 子文件加载顺序验证（S-3）

**问题**：analysis-exec phases/03 被拆分为 5 个子文件（03, 03.1, 03.2, 03.3, 03.4），需确保 LLM 能按正确顺序加载。

**操作**：
1. 在 phases/03-inferential-analysis.md 文件头部添加加载顺序说明
2. 在 SKILL.md 的 Phase 索引表中标注子文件依赖关系
3. 验证脚本：检查 phases/ 文件间的引用方向（子文件不应反向引用主文件）

---

# 第三部分：Sprint 3 — 扩展性增强

## 3.1 扩展模块接入门闸框架

### 接口设计

扩展模块（bio/img/rt/cross）通过统一接口调用 shared/quality_gates/ 门闸框架：

```python
# shared/quality_gates/gate_runner.py 扩展接口
from shared.quality_gates.gate_runner import GateRunner

class ExtensionGateAdapter:
    """扩展模块门闸适配器"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name  # "bio" | "img" | "rt" | "cross"
        self.runner = GateRunner()
    
    def run_module_gate(self, gate_name: str, inputs: dict) -> dict:
        """
        运行模块特定门闸
        
        Args:
            gate_name: 门闸名称（如 "bio_qc_gate", "img_feature_gate"）
            inputs: 门闸输入数据
            
        Returns:
            gate_result: 标准化门闸结果（遵循 gate_result schema）
        """
        # 1. 加载门闸定义（从 shared/quality_gates/gate-{module}.md）
        # 2. 执行检查项
        # 3. 返回标准化结果
        pass
```

### 需要新建的扩展模块门闸定义文件

| 文件 | 模块 | 检查项 |
|------|------|--------|
| `shared/quality_gates/gate-bio.md` | bioinformatics | 数据完整性(QC)/DE结果验证/通路富集覆盖/多组学一致性 |
| `shared/quality_gates/gate-img.md` | imaging | DICOM完整性/分割质量/特征提取覆盖率/特征稳定性 |
| `shared/quality_gates/gate-rt.md` | realtime | 数据流连续性/异常检测准确率/告警延迟/仪表盘可用性 |
| `shared/quality_gates/gate-cross.md` | cross-domain | 多模态对齐/融合模型验证/跨域一致性/关联显著性 |

### 各模块接入步骤

#### bioinformatics 模块
1. 在 `skills/bioinformatics/SKILL.md` 中添加门闸引用节
2. 创建 `shared/quality_gates/gate-bio.md` 定义 4 项检查
3. 在 `shared/quality_gates/gate_runner.py` 中注册 `bio` 模块检查项
4. 在 bioinformatics Phase 流程末尾调用 `ExtensionGateAdapter("bio").run_module_gate("bio_qc_gate", inputs)`

#### imaging-analysis 模块
1. 在 `skills/imaging-analysis/SKILL.md` 中添加门闸引用节
2. 创建 `shared/quality_gates/gate-img.md` 定义 4 项检查
3. 在 `shared/quality_gates/gate_runner.py` 中注册 `img` 模块检查项
4. 在 imaging-analysis Phase 流程末尾调用门闸

#### realtime-monitor 模块
1. 在 `skills/realtime-monitor/SKILL.md` 中添加门闸引用节
2. 创建 `shared/quality_gates/gate-rt.md` 定义 4 项检查
3. 注册并调用

#### cross-domain 模块
1. 在 `skills/cross-domain/SKILL.md` 中添加门闸引用节
2. 创建 `shared/quality_gates/gate-cross.md` 定义 4 项检查
3. 注册并调用

---

## 3.2 Schema 版本统一

### 版本号规范

```yaml
# 所有 JSON Schema 文件统一添加版本字段
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://msra.dev/schemas/{category}/{name}.schema.json",
  "version": "1.0.0",  # 语义化版本：MAJOR.MINOR.PATCH
  "title": "...",
  ...
}
```

### 版本号规则
- **MAJOR**: 不兼容的 Schema 结构变更（如字段删除/重命名/类型变更）
- **MINOR**: 向后兼容的新增字段
- **PATCH**: 文档/描述修正

### contracts/ 统一方案

| 当前文件 | 版本 | 统一操作 |
|---------|------|---------|
| `contracts/passport/*.json` (6 个) | 无版本号 | 添加 `version: "1.0.0"` |
| `contracts/evaluator/full.json` | 无版本号 | 添加 `version: "1.0.0"` |
| `contracts/reviewer/full.json` | 无版本号 | 添加 `version: "1.0.0"` |
| `contracts/reviewer/methodology_focus.json` | 无版本号 | 添加 `version: "1.0.0"` |
| `contracts/audit/*.json` (3 个) | 无版本号 | 添加 `version: "1.0.0"` |
| `compliance_report.schema.json` | 无版本号 | 添加 `version: "1.0.0"` |
| `sprint_contract.schema.json` | 无版本号 | 添加 `version: "1.0.0"` |

### 版本兼容性策略
1. Passport 加载时检查 Schema 版本
2. 版本不匹配时自动迁移（`shared/contracts/migrations/`）
3. 迁移日志记录到 audit_log

---

## 3.3 依赖分层

### pyproject.toml 分层方案

将现有扁平的 `dependencies` 拆分为三层：

```toml
[project]
dependencies = [
    # === 核心层 (core) — CI 必需，Pipeline 基础运行 ===
    "pandas>=1.5",
    "numpy>=1.24",
    "scipy>=1.10",
    "statsmodels>=0.14",
    "matplotlib>=3.7",
    "python-docx>=1.0",
    "openpyxl>=3.1",
    "pyarrow>=15.0.0",
]

[project.optional-dependencies]
# === 统计扩展层 (stats) — 完整统计分析 ===
stats = [
    "lifelines>=0.27",           # 生存分析
    "scikit-learn>=1.3",          # ML 基础
    "seaborn>=0.13",              # 可视化
    "plotnine>=0.12",             # ggplot 风格
]

# === 因果推断层 (causal) ===
causal = [
    "dowhy>=0.11",
    "econml>=0.15",
    "causalinference>=0.1",
    "linearmodels>=5.3",          # IV
    "rdrobust>=2.0",              # RDD
    "cvxpy>=1.4",                 # 合成控制
]

# === 高级建模层 (advanced) ===
advanced = [
    "xgboost>=2.0",
    "lightgbm>=4.0",
    "shap>=0.43",
    "pymc>=5.10",                 # 贝叶斯
    "arviz>=0.17",
    "dcurves>=0.1",               # 决策曲线
    "simpleNomo>=0.1",            # 列线图
]

# === 大规模数据处理层 (scale) ===
scale = [
    "polars>=1.21.0",
    "duckdb>=1.1.0",
    "dask[dataframe]>=2024.5.0",
]

# === 文档解析层 (parsing) ===
parsing = [
    "tabula-py>=2.7",
]

# === 扩展模块层 (已有) ===
bioinformatics = [...]  # 保持不变
medical_imaging = [...]  # 保持不变
realtime_analytics = [...]  # 保持不变
cross_domain = [...]  # 保持不变

# === 便捷安装组合 ===
full_stats = [
    "medical-stats-research-assistant[stats,causal,advanced,scale,parsing]"
]
all = [
    "medical-stats-research-assistant[full_stats,bioinformatics,medical_imaging,realtime_analytics,cross_domain,dev]"
]
```

### 各层包含的包清单

| 层级 | 包 | 用途 | 引用方 |
|------|---|------|--------|
| **core** | pandas, numpy, scipy, statsmodels, matplotlib, python-docx, openpyxl, pyarrow | 数据处理+基础统计+基础可视化+表格导出 | 所有 SKILL |
| **stats** | lifelines, scikit-learn, seaborn, plotnine | 生存分析+ML基础+高级可视化 | analysis-exec |
| **causal** | dowhy, econml, causalinference, linearmodels, rdrobust, cvxpy | 因果推断全套 | analysis-exec, exploratory-causal |
| **advanced** | xgboost, lightgbm, shap, pymc, arviz, dcurves, simpleNomo | 高级ML+贝叶斯+决策曲线 | analysis-exec |
| **scale** | polars, duckdb, dask | 大规模数据处理 | data-prep |
| **parsing** | tabula-py | PDF/文档解析 | report |

### 安装命令示例
```bash
# 仅核心（最小安装）
pip install medical-stats-research-assistant

# 完整统计分析
pip install medical-stats-research-assistant[full_stats]

# 全部功能
pip install medical-stats-research-assistant[all]
```

---

## 3.4 E2E 测试增强

### 新增测试场景清单

#### 3.4.1 跨模块 Handoff 测试（核心场景）

| 测试场景 ID | 测试名称 | 覆盖的 Handoff | 验证点 |
|------------|---------|---------------|--------|
| E2E-001 | 全流程 RCT (Stage 1→4) | data-prep → analysis-plan → analysis-exec → report | 产物链完整性 + 门闸通过 + passport 状态 |
| E2E-002 | 全流程观察性研究 | 同上 | 研究类型分支 + DAG/PSM 路径 |
| E2E-003 | 全流程诊断试验 | 同上 | ROC/AUC 路径 + STARD 规范 |
| E2E-004 | Mid-Entry Stage 2 | analysis-plan → analysis-exec → report | 前置检查 + passport 恢复 |
| E2E-005 | Mid-Entry Stage 3 | analysis-exec → report | SAP 验证 + 质检 |
| E2E-006 | Mid-Entry Stage 4 | report only | 分析结果验证 + 报告生成 |

#### 3.4.2 门闸回退循环测试

| 测试场景 ID | 测试名称 | 验证点 |
|------------|---------|--------|
| E2E-010 | Stage 1.5 门闸 BLOCK → 退回 Stage 1 | 退回机制 + passport 回滚 |
| E2E-011 | Stage 2.5 门闸 BLOCK → 退回 Stage 2 | 退回机制 + SAP 修订 |
| E2E-012 | Stage 3.5 门闸 BLOCK → 退回 Stage 3 | 退回机制 + 分析修正 |
| E2E-013 | 收敛检测：同阶段退回 3 次 | 收敛检测 + BLOCK + 偏差记录 |
| E2E-014 | 条件通过（1-2 项非关键项未通过） | 风险记录 + 继续 |

#### 3.4.3 扩展模块门闸测试

| 测试场景 ID | 测试名称 | 验证点 |
|------------|---------|--------|
| E2E-020 | bioinformatics → 门闸检查 | gate-bio 4 项检查通过 |
| E2E-021 | imaging-analysis → 门闸检查 | gate-img 4 项检查通过 |
| E2E-022 | realtime-monitor → 门闸检查 | gate-rt 4 项检查通过 |
| E2E-023 | cross-domain → 门闸检查 | gate-cross 4 项检查通过 |
| E2E-024 | 扩展模块门闸 BLOCK | 退回机制 + 错误报告 |

#### 3.4.4 瘦身后的完整性测试

| 测试场景 ID | 测试名称 | 验证点 |
|------------|---------|--------|
| E2E-030 | analysis-exec phases/ 引用完整性 | 7+4 个 phases 文件均可正确加载 |
| E2E-031 | analysis-plan phases/ 引用完整性 | 6 个 phases 文件均可正确加载 |
| E2E-032 | report phases/ 引用完整性 | 7 个 phases 文件均可正确加载 |
| E2E-033 | calibration phases/ 引用完整性 | 7 个 phases 文件均可正确加载 |
| E2E-034 | pipeline 门闸引用完整性 | 3 个 gate-*.md + checkpoint_protocol.md 可加载 |
| E2E-035 | shared/INDEX.md 链接完整性 | 所有索引链接可达 |

#### 3.4.5 Schema 版本兼容性测试

| 测试场景 ID | 测试名称 | 验证点 |
|------------|---------|--------|
| E2E-040 | passport schema v1.0.0 加载 | 版本字段存在 + 字段完整 |
| E2E-041 | passport schema 版本不匹配 | 迁移触发 + 数据保留 |
| E2E-042 | contracts/ 所有 schema 版本号 | 统一为 1.0.0 |

---

# 第四部分：每个 Sprint 的验证检查清单

## Sprint 1 完成验证项

### 4.1.1 行数验证
| SKILL.md | 重构前 | 目标 | 验证方法 |
|---------|-------|------|---------|
| analysis-exec | 1344 | ~300 | `wc -l skills/analysis-exec/SKILL.md` ≤ 320 |
| analysis-plan | 1191 | ~280 | `wc -l skills/analysis-plan/SKILL.md` ≤ 300 |
| report | 1247 | ~250 | `wc -l skills/report/SKILL.md` ≤ 270 |
| calibration | 1061 | ~200 | `wc -l skills/calibration/SKILL.md` ≤ 220 |
| pipeline | 785 | ~400 | `wc -l skills/pipeline/SKILL.md` ≤ 420 |

### 4.1.2 phases/ 文件验证
- [ ] analysis-exec/phases/ 包含 11 个文件（7 原有 + 4 新建）
- [ ] analysis-plan/phases/ 包含 6 个文件（1 原有 + 5 新建）
- [ ] report/phases/ 包含 7 个文件（1 原有 + 6 新建）
- [ ] calibration/phases/ 包含 7 个文件（全部新建）
- [ ] 每个 phases/ 文件包含：输入定义、输出定义、执行步骤、Checkpoint 规则、异常处理

### 4.1.3 内容完整性验证
- [ ] P0-2 修复：analysis-exec 反例黑名单重复已删除（L1288-1344 已移除）
- [ ] P0-3 修复：analysis-plan Phase 1.5 (L294-519) 和 Phase 2 (L521-830) 已抽取到 phases/
- [ ] 所有 SKILL.md 的命令/Mode 节无重复
- [ ] 所有 SKILL.md 的反例与黑名单节已改为引用（1 行链接）
- [ ] 所有 SKILL.md 保留：角色定义 + 架构图 + Phase 索引 + 检查点汇总 + 快速参考

### 4.1.4 引用完整性验证
- [ ] 所有 phases/ 文件引用路径正确（相对路径）
- [ ] 所有 shared/ 引用路径正确
- [ ] 所有 agents/ 引用路径正确
- [ ] 无断裂链接

### 4.1.5 测试验证
- [ ] `pytest tests/` 全部通过（319 个测试）
- [ ] 新增 phases 引用完整性测试通过

---

## Sprint 2 完成验证项

### 4.2.1 质量门闸独立化验证
- [ ] `shared/quality_gates/gate-data.md` 存在且包含 9 项检查
- [ ] `shared/quality_gates/gate-sap.md` 存在且包含 8 项检查
- [ ] `shared/quality_gates/gate-results.md` 存在且包含 14 项检查
- [ ] `shared/checkpoint_protocol.md` 存在且包含三级分层定义
- [ ] pipeline/SKILL.md 通过引用加载门闸定义（无内联检查清单）
- [ ] 门闸接口符合 gate_result schema

### 4.2.2 Agent 角色单一化验证
- [ ] analysis-exec/SKILL.md 不包含 Agent 角色定义内联（仅引用 agents/）
- [ ] pipeline/SKILL.md 不包含 Agent 角色定义内联（仅引用 agents/）
- [ ] agents/*.md 5 个文件均包含完整角色定义
- [ ] agents/AGENTS.md 包含协作协议 + Handoff 格式

### 4.2.3 commands 统一验证
- [ ] manifest.json 所有 entry_point 指向正确
- [ ] commands/ 文件仅包含参数解析 + 路由逻辑
- [ ] 无 commands/ 文件与 SKILL.md 内容重复

### 4.2.4 shared/INDEX.md 验证
- [ ] `shared/INDEX.md` 存在
- [ ] 按主题分类（至少 8 个类别）
- [ ] 每个条目包含：文件/目录路径 + 说明 + 引用方
- [ ] 所有链接可达

### 4.2.5 测试验证
- [ ] `pytest tests/` 全部通过
- [ ] 新增门闸引用测试通过
- [ ] 新增 Agent 引用测试通过

### 4.2.6 定义一致性审计验证（§2.5）
- [ ] `scripts/audit_code_consistency.py` 创建并运行
- [ ] 方向 1：S-R01~R08 在 analysis-exec 内只有一份权威定义（编码→定义）
- [ ] 方向 2：同一语义未被分配到不同编码（定义→编码，如"正态性违反"不能既是 S-R01 又是 S-R02）
- [ ] P-R01~R07 跨 analysis-exec/report 不冲突（双向检查）
- [ ] M-R01~R08 / D-R01~R05 / V-R01~V07 各自单一权威定义（双向检查）
- [ ] 所有反模式代码（A1/B1/E1/M1-F4 等）在 shared/anti-patterns/ 中存在
- [ ] `scripts/scan_reference_reachability.py` 创建并运行
- [ ] 无断链引用（shared/ / agents/ / phases/ / 相对路径）

### 4.2.7 Pre-existing 问题修复验证（§2.6）
- [ ] agents/protocol.md 断链已修复（创建文件或改引用）
- [ ] pipeline/SKILL.md 中 3 处 agents/protocol.md 引用可达
- [ ] calibration phases/ 文件已重命名为数字前缀（01-~07-）
- [ ] calibration/SKILL.md phases 索引表已同步更新
- [ ] analysis-exec phases/03 子文件加载顺序说明已添加

---

## Sprint 3 完成验证项

### 4.3.1 扩展模块门闸验证
- [ ] `shared/quality_gates/gate-bio.md` 存在且包含 4 项检查
- [ ] `shared/quality_gates/gate-img.md` 存在且包含 4 项检查
- [ ] `shared/quality_gates/gate-rt.md` 存在且包含 4 项检查
- [ ] `shared/quality_gates/gate-cross.md` 存在且包含 4 项检查
- [ ] 4 个扩展模块 SKILL.md 引用了对应门闸
- [ ] `gate_runner.py` 注册了 4 个扩展模块

### 4.3.2 Schema 版本统一验证
- [ ] `contracts/` 下所有 JSON Schema 文件包含 `version: "1.0.0"`
- [ ] `compliance_report.schema.json` 包含版本号
- [ ] `sprint_contract.schema.json` 包含版本号
- [ ] Passport 加载时检查 Schema 版本

### 4.3.3 依赖分层验证
- [ ] pyproject.toml `dependencies` 仅包含 core 层（8 个包）
- [ ] pyproject.toml `[optional-dependencies]` 包含 stats/causal/advanced/scale/parsing 层
- [ ] `pip install medical-stats-research-assistant` 最小安装成功
- [ ] `pip install medical-stats-research-assistant[full_stats]` 完整统计安装成功
- [ ] CI 使用最小安装运行核心测试

### 4.3.4 E2E 测试验证
- [ ] E2E-001 ~ E2E-006 跨模块 Handoff 测试通过
- [ ] E2E-010 ~ E2E-014 门闸回退循环测试通过
- [ ] E2E-020 ~ E2E-024 扩展模块门闸测试通过
- [ ] E2E-030 ~ E2E-035 瘦身后完整性测试通过
- [ ] E2E-040 ~ E2E-042 Schema 版本兼容性测试通过
- [ ] 总测试数 ≥ 350（319 原有 + 31+ 新增）

### 4.3.5 最终文档验证
- [ ] `shared/INDEX.md` 更新（包含所有新建文件）
- [ ] CHANGELOG.md 记录 3 个 Sprint 的所有变更
- [ ] 版本号统一更新为 1.1.0

---

# 附录 A：ADR 汇总

## ADR-001: 技能配置瘦身策略
**状态**: Accepted
**决策**: 主 SKILL.md 保留角色+架构图+Phase索引+检查点+快速参考（~200-400行），Phase 详细规范抽取到 phases/，跨 Phase 复用内容抽取到 shared/
**影响**: context window 占用降低 ~75%，LLM 推理质量提升，维护成本降低

## ADR-002: 质量门闸独立化
**状态**: Accepted
**决策**: 门闸定义独立为 shared/quality_gates/gate-{name}.md，Pipeline 通过引用加载，统一 gate_result schema
**影响**: 门闸可被扩展模块复用，门闸逻辑单一数据源

## ADR-003: Agent 角色定义单一来源
**状态**: Accepted
**决策**: agents/*.md 为 Agent 角色唯一定义源，SKILL.md 仅引用链接
**影响**: 消除双重定义，Agent 角色变更只需修改一处

## ADR-004: 依赖分层
**状态**: Proposed
**决策**: pyproject.toml 拆分为 core/stats/causal/advanced/scale/parsing 六层
**影响**: 最小安装更轻量，用户按需安装

## ADR-005: Schema 版本统一
**状态**: Proposed
**决策**: 所有 JSON Schema 统一添加 version 字段，遵循语义化版本
**影响**: Schema 变更可追踪，版本兼容性可验证

## ADR-006: 论文写作模块的架构定位
**状态**: Accepted (Sprint 1 阶段)
**日期**: 2026-06-25

### 背景
report/SKILL.md L1096-1247 包含完整的 12-Agent 论文写作系统（12 Agents + 11 Modes + 8 Phases + Generator-Evaluator Contract）。原始重构任务建议"独立为 peer-review skill"，但审查发现：
- `skills/peer-review/` **已存在**，职责是**期刊同行评审**（5 位审稿人：主编+方法学+临床+统计+伦理，产出 Editorial Decision + Revision Roadmap，检查 CONSORT/STROBE/PRISMA）
- 论文写作 12-Agent 系统职责是**生成论文**（配置→检索→大纲→论证→草稿→引用→摘要→模拟审稿→格式化→导师→图表→修订规划）
- 两者职责完全不同，不可合并。代码审查师 Cody 已更正风险评估 H4 项

### 选项分析

| 维度 | 选项 A: phases/07-paper-writing.md | 选项 B: 独立 skills/paper-writing/ |
|------|-----------------------------------|-----------------------------------|
| 复杂度 | Low — 仅抽取，不新建 skill | Med — 需定义触发词/路由/依赖/manifest |
| 延迟风险 | 无 — Sprint 1 可完成 | 有 — 新 skill 注册涉及 manifest.json |
| 解耦程度 | 低 — 仍在 report 内 | 高 — 完全独立 |
| 上市时间 | Sprint 1 完成 | Sprint 2/3 |
| 团队熟悉度 | 高 — phases/ 模式已建立 | 中 — 需学习新 skill 创建流程 |

### 决策
**Sprint 1**: 采用选项 A，抽取到 `report/phases/07-paper-writing.md`。12 个 agent 定义文件保留在 `report/agents/`。

**Sprint 2/3（可选升级）**: 如 team-lead 认为 paper-writing 应独立：
1. 创建 `skills/paper-writing/`，将 phases/07 提升为 SKILL.md
2. 将 `report/agents/` 下 12 个 agent 文件迁移到 `skills/paper-writing/agents/`
3. report/SKILL.md 保留双模式入口和 Stage 4 CHECKPOINT [B] 路由引用
4. manifest.json 新增 `/msra-write` 命令指向新 skill
5. **不可复用 peer-review 名称**

### 影响
- Sprint 1: report SKILL.md 通过 Stage 4 CHECKPOINT [B] 路由到 phases/07，双模式架构不变
- Sprint 2/3: 如升级为独立 skill，需更新 manifest.json + 路由 + 跨 skill 引用

### 关联问题: mock_reviewer 功能重叠
`report/agents/mock_reviewer.md`（模拟双盲审稿+五维评分+修改建议，最多 2 轮）与 `peer-review` skill 的审稿功能存在概念重叠。但：
- mock_reviewer 是 paper-writing 流水线内的**单 Agent 自审**，目的是改进草稿
- peer-review 是**独立多审稿人评审**，目的是编辑决策
- Sprint 2 可考虑：peer-review skill 新增 "draft-review" 模式，供 paper-writing 调用（通过 works_with 引用）
- 当前 Sprint 1 不处理此重叠，保持 mock_reviewer 原位

---

# 附录 B：Sprint 依赖关系

```
Sprint 1 (SKILL.md 瘦身)
    │
    ├── Sprint 2 (架构解耦) — 依赖 Sprint 1 的 phases/ 结构
    │       │
    │       └── Sprint 3 (扩展性增强) — 依赖 Sprint 2 的门闸框架
    │
    └── 每个 Sprint 完成后运行完整测试套件
```

**关键路径**: Sprint 1 → Sprint 2 → Sprint 3
**并行可能**: Sprint 1 内部 5 个 SKILL.md 可并行处理（但需统一 phases/ 命名规范）
