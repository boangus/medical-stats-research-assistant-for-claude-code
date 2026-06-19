# MSRA Unified Pipeline — Routing Discipline v3.9.2

> 本文件定义统一项目的路由规则和跨 skill 数据传递规范。
> 版本: v0.8.0 (MSRA 统一流水线)

---

## 1. 项目概述

本项目是一个**统一的医学统计分析 + 学术写作流水线**，从原始数据到可投稿论文的完整流程：

- **Stage 1-4**: 数据分析流水线（数据准备 → 分析计划 → 分析执行 → 统计报告）
- **Stage 5-6**: 学术写作流水线（论文选题 → 文献检索 → 论文撰写 → 评审修订 → 定稿）

**核心定位**：本插件为医学研究提供端到端的统计分析与论文写作支持。纯学术写作场景可直接使用写作 skill。

---

## 2. Skill 注册表

| Skill | 路径 | 类型 | 描述 |
|-------|------|------|------|
| **pipeline** | `skills/pipeline/SKILL.md` | Orchestrator | 统一流水线编排器 (Stage 1-6) |
| **data-prep** | `skills/data-prep/SKILL.md` | Worker | 数据准备 (Stage 1) |
| **analysis-plan** | `skills/analysis-plan/SKILL.md` | Worker | 分析计划 (Stage 2) |
| **analysis-exec** | `skills/analysis-exec/SKILL.md` | Worker | 分析执行 (Stage 3) |
| **report** | `skills/report/SKILL.md` | Worker | 统计报告 (Stage 4) |
| **calibration** | `skills/calibration/SKILL.md` | Utility | 度量校准 |
| **academic-pipeline** | `skills/academic-pipeline/SKILL.md` | Worker | 学术写作流水线 (Stage 5.1-5.9) |
| **academic-paper** | `skills/academic-paper/SKILL.md` | Worker | 论文写作 |
| **academic-paper-reviewer** | `skills/academic-paper-reviewer/SKILL.md` | Worker | 论文评审 |
| **deep-research** | `skills/deep-research/SKILL.md` | Worker | 文献检索 |

---

## 3. Routing Discipline

### 3.1 三步路由逻辑

```
Step 1: 判断数据需求
  ├── 有数据要处理 → MSRA Pipeline (/msra)
  └── 无数据纯写作 → 写作 Skill (直接调用)

Step 2: 判断入口阶段 (MSRA Pipeline)
  ├── "原始数据" / "清洗" → Stage 1
  ├── "分析计划" / "方法" → Stage 2
  ├── "执行分析" → Stage 3
  ├── "报告" / "表格" → Stage 4
  ├── "继续写论文" → Stage 5.0 (需 Stage 4 完成)
  └── "完整流程" → Stage 1

Step 3: 判断 Paper Track 分叉 (Stage 4 Checkpoint)
  ├── [A] 统计报告完成 → Pipeline 结束
  └── [B] 继续写论文 → Stage 5.0 → Stage 5.1-5.9
```

### 3.2 路由规则

| # | 规则 | 说明 |
|---|------|------|
| R1 | 有数据 → `/msra` | 任何涉及数据分析的需求走 MSRA Pipeline |
| R2 | 无数据纯写作 → 直接用写作 skill | `/ars-full`, `/ars-plan`, `/ars-reviewer` 等 |
| R3 | Paper Track 需 Stage 4 完成 | `passport.track == "full_paper"` + Stage 1-4 completed |
| R4 | Pipeline 保持编排器定位 | 不做实质性工作，只调度 |
| R5 | 写作 skill 保持独立可运行 | 既可被 Pipeline 调度，也可独立使用 |

### 3.3 意图检测关键词

| 意图 | 关键词 | 路由目标 |
|------|--------|---------|
| 数据分析 | 数据、清洗、统计、分析、RCT、队列 | `/msra` |
| 报告生成 | 报告、表格、图表、CONSORT、STROBE | `/msra-report` |
| 写论文 | 论文、manuscript、投稿、paper | Stage 5 或 `/ars-full` |
| 文献检索 | 文献、检索、综述、literature | `/ars-lit-review` 或 `deep-research` |
| 论文评审 | 审稿、评审、review | `/ars-reviewer` |
| 系统综述 | 系统综述、PRISMA、systematic | `deep-research` (systematic-review mode) |

---

## 4. Handoff Protocol

### 4.1 Stage 4 → Stage 5.0 Handoff

**触发条件**: 用户在 Stage 4 checkpoint 选择 [B]
**产物**: `MSRA/msra_handoff_bundle.md` (由 `scripts/generate_msra_handoff_bundle.py` 生成)
**内容**: RQ, Methods Summary, Tables/Figures, Key Findings, Safety Findings, Limitations

### 4.2 Stage 5 内部 Handoff (Stage 5.1 → 5.9)

所有跨 skill 产物遵循 `shared/handoff_schemas.md` 的 9 个 Schema。

### 4.3 Material Passport

统一使用 `shared/passport/passport.py` 管理产物生命周期。
- Stage 1-4: 由 MSRA Pipeline 管理
- Stage 5.0-5.9: 由 academic-pipeline 管理
- `track` 字段区分 `report_only` 和 `full_paper`

---

## 5. 六大融合点

| # | 融合点 | Stage 1-4 来源 | Stage 5 消费者 |
|---|--------|---------------|---------------|
| A | Passport 统一 | passport_schema.md | Material Passport |
| B | Quality Gate 复用 | Stage 3.5 门闸报告 | Stage 5.5 Integrity Check |
| C | 文献 seed | Phase 1 文献对比 | Stage 5.1 deep-research |
| D | 方法学复用 | Phase 5 方法学描述 | Stage 5.2 Methods |
| E | 期刊模板 | Phase 2.5 期刊选择 | Stage 5.0 Paper Intake |
| F | 表格图表 | figures/*.png + tables/*.docx | Stage 5.2 Results |

---

## 6. Shared 资源索引

### 数据分析专用
- `shared/reporting-guidelines/` — 16 个临床报告规范
- `shared/statistics-methods/` — 统计方法目录 (48 章)
- `shared/sap/` — SAP 标准与验证
- `shared/calibration/` — 度量校准框架
- `shared/templates/` — R/Python 代码模板

### 学术写作专用
- `shared/handoff_schemas.md` — 跨 skill 数据契约 (12 Schema)
- `shared/contracts/` — 合约模板 (5 个子目录)
- `shared/prisma_trAIce_protocol.md` — PRISMA-trAIce
- `shared/raise_framework.md` — RAISE 框架
- `shared/style_calibration_protocol.md` — 写作风格校准

### 共用
- `shared/passport/` — Material Passport
- `shared/references/` — 参考文档
- `shared/anti-patterns/` — 反模式目录
- `shared/reproducibility