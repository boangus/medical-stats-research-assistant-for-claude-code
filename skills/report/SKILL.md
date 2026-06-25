---
version: "1.0.0"
name: MSRA Report & Paper Generation
description: |
  双模式文档生成：[模式A] 统计报告（CONSORT/STROBE/PRISMA等出版级表格、图表、方法学描述、一致性校验与报告组装）；
  [模式B] 学术论文写作（12-agent团队、11种模式、IMRaD结构、双语摘要、5种引用格式）。
  触发: 报告 / 生成报告 / 表格 / 图表 / 统计报告 / CONSORT / STROBE / STARD / publication / 三线表 / statcheck / 方法学描述 / 写论文 / paper / manuscript / 论文大纲 / 修订论文 / 摘要 / 文献综述 / 审稿意见 / AI disclosure
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
> - 反模式：shared/anti-patterns/medical_stats_anti_patterns.md（D1/D2/D3/M1-M6）
> - 统计约束：shared/statistics-methods/statistical_constraints.md
> - 图表标准：shared/chart-styles/publication_figure_standards.md
> - 变量命名+自动化标准化：shared/variable_naming_standards.md（677行，50+映射表）+ shared/variable_standardization/（VariableStandardizer + StatFormatter）
> - 图表模板：shared/templates/publication_figure_template.py
> - 审慎表达：shared/references/protected_hedging_phrases.md
> - 期刊模板：shared/journal-templates/（AIM/BMJ/JAMA/Lancet/NEJM 等 7 个）
> - 图表 FDV：shared/chart_understanding/

## 架构集成图

```
输入: analysis-exec结果(JSON) + shared/chart-styles + reporting-guidelines(CONSORT/STROBE)
  ↓
Phase 0-1: 解读会话+结果解读 (确认优先级 → 提取效应量/P值/CI)
  ↓
Phase 2: 表格生成与导出 (V-R01~R07 + P-R01~R07)
  ↓
Phase 3: 图表整合 (publication_style, SVG主+PNG备)
  ↓
Phase 4-5: 方法学描述 + 一致性校验 (statcheck)
  ↓
Phase 6: HTML报告组装 → final_report.html + figures/*.svg + tables/*.docx + report.json
```

**架构设计原则**: ① 单向流水线不回退(错误时降级) ② SVG为主PNG为备 ③ statcheck为独立验证层 ④ 合规检查(6d/6e)阻断式 ⑤ 输出多格式(HTML+MD+DOCX)

## 快速开始

简单报告（3步）: 读取JSON → P值格式化+变量命名规范化 → 输出HTML（含标准三线表）
完整报告（7步）: Phase 0-7 完整流程

### 执行时间估算

| 报告类型 | 分析数量 | 预计时间 |
|---------|---------|---------|
| 简单报告(3步) | 1个主分析 | 1-2分钟 |
| 标准报告(7步) | 3-5个分析 | 5-10分钟 |
| 完整报告(含CONSORT) | 10+分析 | 10-20分钟 |
| Quick Mode | 1-2个分析 | <1分钟 |

## 报告模板速查

| 模板 | 报告规范 | 结构要点 |
|------|---------|---------|
| RCT | CONSORT | 标题页 → 摘要 → 引言 → 方法(设计/随机化/盲法) → 结果(流程图/基线/主结果/不良反应) → 讨论(局限性/解释/推广性) |
| 观察性研究 | STROBE | 标题页 → 摘要 → 引言 → 方法(设计/参与者/变量/偏倚/统计方法) → 结果(参与者/主结果/事件) → 讨论(局限性/解释/推广性) |
| 诊断试验 | STARD | 标题页 → 摘要 → 引言 → 方法(设计/指数试验/金标准/样本量) → 结果(参与者/估计量/不确定性) → 讨论(局限性/解释/推广性) |

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
Phase 2: 表格生成与导出 → 输入:解读文档+分析结果 → 输出:Markdown表格 + *.docx三线表 [SLIM]
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
| Phase 2 | `phases/02-table-generation.md` | 表格生成与导出（Step 2.1 Markdown + Step 2.2 docx） |
| Phase 3 | `phases/03-figure-integration.md` | 图表整合（分析类型→图类型映射 + 模板加载 + 执行 + 异常处理） |
| Phase 4 | `phases/04-methodology.md` | 方法学描述 |
| Phase 5 | `phases/05-consistency-check.md` | 一致性校验（statcheck + 反模式 + 约束合规 + 图表质量 + 学术标准） |
| Phase 6 | `phases/06-report-assembly.md` | 报告组装 |
| Paper Track | `phases/07-paper-writing.md` | 论文写作模式（12 Agent + 11 Mode + 8 Phase + 引用格式 + Generator-Evaluator 合同） |

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

**关键产物与交付物清单**：

> 完整交付物清单（含 T1-T8/F1-F10/R1-R4 全部 18 项）见 `phases/05-consistency-check.md` §交付物清单

| 编号 | 交付物 | 格式 | 来源 Phase |
|------|--------|------|-----------|
| T1 | Table 1 基线特征表 | .docx三线表 | Phase 2 |
| T8 | 变量定义表 | .docx三线表 | Phase 2 |
| F1 | CONSORT流程图 | .svg+.pdf+.png | Phase 3 |
| F10 | SHAP图 | .svg+.pdf+.png | Phase 3 |
| R1 | 统计报告 | .html+.md | Phase 6 |
| R4 | 局限性讨论 | .md | Phase 1/6 |

**图表类型速查**（完整映射见 `phases/03-figure-integration.md`）：

| 图表类型 | 用途 | 编号 |
|---------|------|------|
| CONSORT流程图 | RCT受试者流程 | F1 |
| 校准曲线 | 预测模型 | F5 |
| Bland-Altman图 | 一致性检验 | F6 |
| DAG图 | 因果关系 | F8 |
| Love Plot | 协变量平衡 | F9 |
| SHAP图 | 机器学习解释 | F10 |

**关键产物**：interpretation_priorities.md(Phase 0) / result_interpretation.md(Phase 1) / tables/*.docx(Phase 2) / figures/*.svg(Phase 3) / methodology.md(Phase 4) / consistency_report.md(Phase 5) / final_report.md+.html(Phase 6) / paper_draft.md(Paper Track)

---

## 命令

| 命令 | 说明 |
|------|------|
| `/msra-report` | 启动报告生成流程 |
| `/msra-report --paper` | 论文写作模式 |
| `/msra-report --tables-only` | 仅生成表格 |
| `/msra-report --figures-only` | 仅生成图表 |

## Mode

- **Full（默认）**: 完整流程：结果解读 → 表格生成 → 图表整合 → 方法学描述 → 一致性校验 → 报告组装
- **Paper**: 论文写作模式：12 Agent + 11 Mode + 8 Phase，从统计报告到论文草稿

---

## 反例与黑名单

> 完整医学统计反模式目录参见：[shared/anti-patterns/medical_stats_anti_patterns.md](../../shared/anti-patterns/medical_stats_anti_patterns.md)（D1/D2/D3/A5/M1-M6）
> 论文写作特定反模式参见：[phases/07-paper-writing.md](phases/07-paper-writing.md) §论文写作反例与黑名单

---

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

| 触发条件 | 降级标记 | 后续操作 |
|---------|---------|---------|
| statcheck API 不可用 | [STATCHECK_SKIPPED] | 报告"统计验证"章节添加说明，提供核对清单模板 |
| 图表生成失败 | [FIGURE_ERROR] | 生成详细表格，附带图表代码文件（.py/.R） |
| CONSORT/STROBE checklist 缺失 | [CHECKLIST_DEGRADED] | (1) 使用精简清单继续 (2) 暂停等待用户提供完整清单 |
| HTML 渲染失败 | [HTML_FALLBACK] | 输出 final_report.md + render_error.log |

> 所有降级标记必须在最终报告显著位置标注，不得静默降级。

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
- 选 **[B]** → 守卫检查通过后 `passport.set_track("full_paper")`，进入 **phases/07-paper-writing.md**（Stage 5 Paper Track）
- 守卫检查失败 → 提示用户补全缺失产物，不进入 Paper Track

---

> **版本历史**: v0.9.0 初始版本 → v0.9.1 合并 medical-paper → v0.9.2 增强 statcheck/约束合规/图表质量 → v0.9.3 SKILL.md 瘦身，Phase 2-7 抽取为独立 phases 文件（参照 data-prep 模式）
