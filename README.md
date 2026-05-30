# Medical Statistics Research Assistant (MSRA)

医学统计研究助手 — 面向医学研究者的统计分析流水线

[![CI](https://github.com/boangus/medical-stats-research-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/boangus/medical-stats-research-assistant/actions/workflows/ci.yml)

一个以 **Pipeline 驱动** 的医学统计分析工具集。从原始数据到最终报告，4 个阶段、5 个命令，覆盖完整的医学统计分析流程。无论你从哪个阶段开始，Pipeline 都能自动识别并引导你完成后续工作。

兼容 Claude Code、Codex、Cursor 等支持 Agent Skills Standard 的 runtime。

---

## 快速开始

```bash
# 一行安装（auto-detect runtime）
# Claude Code: /plugin marketplace add boangus/medical-stats-research-assistant
# 手动安装: 将 skills/ 目录复制到对应 runtime 的 skills 目录

# 启动流水线（自动检测入口）
/msra 我有一份RCT的原始数据，想完成整个分析
```

---

## Pipeline 流水线

```
原始数据
   │
   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 1: 数据准备  /msra-data                      │
│  验证 → 清洗 → 变量构造 → 盲态审核 → 数据库锁定    │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 1.5: 数据质量门闸 (阻断式检查)             │
│  7 项数据质量检查 → ✅ 通过 / ❌ 退回修订             │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 2: 分析计划  /msra-plan                      │
│  EDA → Estimands → 方法探讨 → SAP → 审查 → 定稿     │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 2.5: SAP 质量门闸 (阻断式检查)            │
│  7 项 SAP 完整性检查 → ✅ 通过 / ❌ 退回修订          │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 3: 分析执行  /msra-exec                      │
│  描述性统计 → 依从性 → 主要分析 → 敏感性分析         │
│  → 安全性分析 → 假设检验 → 质量检查                 │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 3.5: 结果质量门闸 (阻断式检查)            │
│  7 项结果完整性检查 → ✅ 通过 / ❌ 退回修正          │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 4: 报告生成  /msra-report                    │
│  结果解读 → 表格/图表 → 方法学 → 规范检查            │
└──────────────────┬──────────────────────────────────┘
                   ▼
               最终报告
```

### 从任意阶段切入

| 你有什么 | 怎么说 | 从哪开始 |
|---------|--------|---------|
| 原始数据 | `/msra 我有原始数据` | Stage 1 → Stage 1.5 → ... |
| 已清洗数据 | `/msra 数据已清洗，帮我做分析计划` | Stage 2（需确认 Stage 1.5 门闸通过） |
| 已有SAP | `/msra 按这个SAP执行分析` | Stage 3 |
| 已有结果 | `/msra 帮我生成CONSORT报告` | Stage 4 |
| 不确定 | `/msra` | 自动检测 |

---

## 命令一览

| 命令 | 功能 | 对应阶段 |
|------|------|---------|
| `/msra` | 启动流水线（自动检测入口） | 全流程 |
| `/msra-data` | 数据验证与清洗 | Stage 1 |
| `/msra-plan` | 方法探讨、SAP制定与审查 | Stage 2 |
| `/msra-exec` | 按SAP执行分析 + 质量检查 | Stage 3 |
| `/msra-report` | 生成出版级报告 | Stage 4 |

---

## 项目结构

```
medical-stats-research-assistant/
├── manifest.json                 # 插件清单
├── README.md                     # 本文件
├── LICENSE                       # MIT 许可证
├── requirements.txt              # CI 依赖
│
├── .github/workflows/            # CI/CD
│   └── ci.yml                    # GitHub Actions（smoke + lint）
│
├── skills/                       # 5 个 Skill
│   ├── pipeline/                 # 🔀 流水线编排器（核心）
│   │   └── SKILL.md
│   ├── data-prep/                # 📊 数据准备
│   │   └── SKILL.md
│   ├── analysis-plan/            # 📋 分析计划
│   │   └── SKILL.md
│   ├── analysis-exec/            # ⚙️ 分析执行
│   │   └── SKILL.md
│   └── report/                   # 📝 报告生成
│       └── SKILL.md
│
├── agents/                       # 多 Agent 定义
│   ├── AGENTS.md                 # 团队架构
│   ├── protocol.md               # 协作协议
│   ├── data_validator_agent.md   # 数据质量专家
│   ├── method_consultant_agent.md# 方法顾问
│   ├── code_executor_agent.md    # 代码执行者
│   └── qc_inspector_agent.md     # 质量审查员
│
├── shared/                       # 共享资源
│   ├── checklists/               # 质量检查清单
│   ├── templates/                # 代码模板 (R + Python)
│   ├── sample-size/              # 样本量计算
│   ├── causal-inference/         # 因果推断工作流
│   ├── reproducibility/          # 可重复性验证
│   ├── calibration/              # 校准框架
│   ├── passport/                 # Material Passport 产物追踪
│   ├── statistics-methods/       # 统计与方法指南 (41章)
│   ├── value-normalization/      # 值规范化（TCM术语+数值变体）
│   ├── chart-styles/             # 图表样式库（期刊配色、图表类型、字体规范）
│   ├── error-diagnostics/        # 错误诊断知识库（错误模式、自动修复建议）
│   ├── reporting-guidelines/     # 报告规范检查清单（TRIPOD+AI/CARE/REMARK/ARRIVE）
│   ├── journal-templates/        # 期刊模板（NEJM/JAMA/Lancet/BMJ/CMJ/AIM/CJE）
│   ├── sap_consistency/          # SAP一致性检查（SAP与数据特征比对）
│   ├── sap_to_methods/           # SAP到方法学描述转换（自动生成方法学段落）
│   ├── data_sharing/             # 数据共享（去标识化、代码包、结果包生成）
│   └── archive/                  # 存档包（产物收集、清单生成、完整性验证）
│
├── docs/                         # 文档
│   └── PIPELINE.md               # 架构与流水线详细文档
│
└── examples/                     # 使用示例
    └── example_workflow.md
```

---

## 设计理念

### Pipeline 驱动
- **纯调度**: Pipeline 不做实质性工作，只负责检测、推荐、调度、追踪
- **3 个阻断式质量门闸**: Stage 1.5（数据质量）、Stage 2.5（SAP 质量）、Stage 3.5（结果质量）
- **任意切入**: 通过意图检测自动识别用户当前阶段
- **Checkpoint 机制**: 每个阶段结束后暂停，等待用户确认
- **前置检查**: 进入下一阶段前验证前置产物是否完整

### 人机回环
- 数据清洗策略需用户批准
- 统计方法与用户共同探讨
- SAP 需经过独立审查
- 任何偏差都有记录

### 可重复性
- 所有步骤生成可重复代码
- 清洗过程完全记录
- 分析严格按 SAP 执行

---

## 支持的统计方法

- **组间比较**: t检验、ANOVA、卡方、Mann-Whitney U、Kruskal-Wallis
- **回归分析**: 线性、Logistic、Poisson、Cox
- **生存分析**: Kaplan-Meier、Log-rank、竞争风险
- **高级方法**: 混合效应模型、GEE、倾向性评分、多重插补、Meta分析
- **诊断试验**: ROC、敏感性/特异性、AUC

## 支持的报告规范

CONSORT (RCT) · STROBE (观察性) · PRISMA (系统综述) · STARD (诊断) · TRIPOD (预测模型) · CARE (病例报告)

---

---

## 许可证

MIT License



