# Medical Statistics Research Assistant (MSRA)

医学统计研究助手 — 从原始数据到可投稿论文的统一流水线

[![CI](https://github.com/boangus/medical-stats-research-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/boangus/medical-stats-research-assistant/actions/workflows/ci.yml)

一个以 **Pipeline 驱动** 的医学统计分析 + 学术写作工具集。从原始数据到最终报告，再到可投稿论文，6 个统计阶段 + 6 个写作阶段，覆盖完整的医学研究流程。无论你从哪个阶段开始，Pipeline 都能自动识别并引导你完成后续工作。

**8 个内置 Skill，10 个命令，开箱即用，无需额外安装**。

---

## 快速开始

```bash
# Windows
.\install.ps1

# Mac / Linux
./install.sh

# 启动流水线（自动检测入口）
/msra 我有一份RCT的原始数据，想完成整个分析

# 直接进入论文写作
/ars-full 帮我写一篇关于肺癌靶向治疗的综述
```

---

## Pipeline 流水线全景

### Stage 1-4: 统计分析流水线

```
原始数据 → 研究类型识别（RCT / 观察性 / 诊断准确性）
   │
   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 1: 数据准备  /msra-data                      │
│  验证 → 清洗 → 变量构造 → 盲态审核 → 数据库锁定    │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 1.5: 数据质量门闸 (阻断式检查)             │
│  9 项数据质量检查 → ✅ 通过 / ❌ 退回修订             │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 2: 分析计划  /msra-plan                      │
│  EDA → Estimands → 方法探讨 → SAP → 审查 → 定稿     │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 2.5: SAP 质量门闸 (阻断式检查)            │
│  8 项 SAP 完整性检查 → ✅ 通过 / ❌ 退回修订          │
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
│  9 项结果完整性检查 → ✅ 通过 / ❌ 退回修正          │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 4: 报告生成  /msra-report                    │
│  结果解读 → 表格/图表 → 方法学 → 规范检查            │
└──────────────────┬──────────────────────────────────┘
                   ▼
          Checkpoint: [A] 仅报告 / [B] 继续写论文
```

### Stage 5-6: 论文写作流水线（可选）

```
                    │
                    ▼ (选择 [B])
┌─────────────────────────────────────────────────────┐
│  Stage 5.0: Paper Intake  /msra-paper              │
│  Handoff Bundle + 论文配置 + 期刊选择               │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.1: Literature Search  /ars-lit-review     │
│  文献检索 + 综述撰写 + 参考文献库                    │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.2: Paper Writing  /ars-plan               │
│  IMRaD 章节撰写（复用方法学和表格图表）             │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 5.5: Integrity Check                      │
│  完整性检查（阻断式）→ ✅ / ❌                       │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.6: Peer Review  /ars-reviewer             │
│  5人评审团（EIC+方法学+领域+写作+DA）               │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.7: Revision  /ars-revision                │
│  修订 + Response to Reviewers                      │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 5.8: Final Integrity                     │
│  最终完整性检查（阻断式）→ ✅ / ❌                    │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.9: Finalize  /ars-format-convert          │
│  定稿导出（MD → DOCX → PDF）                        │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 6: Process Summary                          │
│  完整过程记录 + AI 自我反思 + 协作质量评估          │
└─────────────────────────────────────────────────────┘
```

---

## 命令一览（10个）

### 📊 统计分析（7个）

| 命令 | 功能 | 对应阶段 |
|------|------|---------|
| `/msra` | 启动统一流水线（自动检测入口） | 全流程 |
| `/msra-data` | 数据验证与清洗 | Stage 1 |
| `/msra-plan` | 方法探讨、SAP制定与审查 | Stage 2 |
| `/msra-exec` | 按SAP执行分析 + 质量检查 | Stage 3 |
| `/msra-report` | 生成出版级统计报告 | Stage 4 |
| `/msra-calibrate` | 指标校准（金标准对比） | 校准 |
| `/msra-paper` | 进入论文写作轨道（Stage 5.0） | Stage 5.0 |

### ✍️ 学术写作（3个）

| 命令 | 功能 | 说明 |
|------|------|------|
| `/ars-paper --mode <mode>` | 论文写作（9种模式：plan/abstract/revision/...） | `report/SKILL.md` |
| `/ars-full` | 完整写作流水线：研究→写作→评审→修订→定稿 | `pipeline/SKILL.md` |
| `/ars-reviewer` | 多视角论文评审（5人评审团） | `academic-paper-reviewer` |

---

## 8 个内置 Skill

| Skill | 名称 | 职责 | 核心能力 |
|-------|------|------|---------|
| **pipeline** | 统一编排器 | Stage 1-6 全流程调度 | 意图检测、阶段识别、任务分发 |
| **data-prep** | 数据准备 | Stage 1 | 数据验证、清洗、EDA、盲态审核 |
| **analysis-plan** | 分析计划 | Stage 2 | 估计目标定义、方法探讨、SAP制定 |
| **analysis-exec** | 分析执行 | Stage 3 | R/Python代码生成、统计分析执行 |
| **report** | 报告生成 + 论文写作 | Stage 4-5 | 表格/图表生成、IMRaD撰写、格式导出 |
| **calibration** | 度量校准 | 校准 | 金标准对比、指标校准 |
| **academic-paper-reviewer** | 论文评审 | Stage 5.6 | 5人评审团、质量评估、修订建议 |
| **deep-research** | 文献检索 | Stage 5.1 | 系统性文献检索、综述撰写 |

> 注：`academic-paper` 和 `academic-pipeline` 的参考资源已整合至 `resources/` 目录，其核心功能由 `report` skill（论文写作模式）和 `pipeline` skill（§11 Paper Track）承担。

---

## 项目结构

```
medical-stats-research-assistant/
├── manifest.json                 # 插件清单
├── README.md                     # 本文件
├── LICENSE                       # MIT 许可证
├── requirements.txt              # Python 依赖
├── install.ps1                   # Windows 安装脚本
├── install.sh                    # Mac/Linux 安装脚本
├── uninstall.ps1                 # Windows 卸载脚本
├── uninstall.sh                  # Mac/Linux 卸载脚本
│
├── .github/workflows/            # CI/CD
│   └── ci.yml                    # GitHub Actions
│
├── .claude/                      # Claude Code 配置
│   ├── CLAUDE.md                 # 统一路由规则
│   ├── commands/                 # 命令入口（install创建junction）
│   └── skills/                   # Skill入口（install创建junction）
│
├── commands/                     # 命令定义（10个）
│   ├── msra.md                   # MSRA 主命令
│   ├── msra-data.md              # 数据准备
│   ├── msra-plan.md              # 分析计划
│   ├── msra-exec.md              # 分析执行
│   ├── msra-report.md            # 报告生成
│   ├── msra-calibrate.md         # 指标校准
│   ├── msra-paper.md             # 论文轨道
│   ├── ars-paper.md              # 论文写作（9种模式）
│   ├── ars-full.md               # 完整写作流水线
│   └── ars-reviewer.md           # 论文评审
│
├── skills/                       # 8 个 Skill
│   ├── pipeline/                 # 🔀 统一编排器（核心）
│   ├── data-prep/                # 📊 数据准备
│   ├── analysis-plan/            # 📋 分析计划
│   ├── analysis-exec/            # ⚙️ 分析执行
│   ├── report/                   # 📝 报告生成
│   ├── calibration/              # 🎯 指标校准
│   ├── academic-paper-reviewer/  # 🔍 论文评审
│   └── deep-research/            # 📚 文献检索
│
├── agents/                       # 多 Agent 定义
│   ├── AGENTS.md                 # 团队架构 + 协作协议
│   ├── data_validator_agent.md   # 数据质量专家
│   ├── method_consultant_agent.md# 方法顾问
│   ├── exec_runner_agent.md      # 代码执行者
│   ├── exec_inference_agent.md   # 推断执行者
│   └── qc_inspector_agent.md     # 质量审查员
│
├── shared/                       # 共享资源
│   ├── templates/                # 代码模板 + 文档模板
│   │   ├── quality-gates/        # 质量门闸报告模板（3个）
│   │   ├── data-prep/            # 数据准备模板（4个）
│   │   ├── msra_handoff_bundle_template.md
│   │   └── (R/Python 代码模板 40+)
│   ├── sap/                      # SAP标准化
│   │   └── templates/            # SAP模板（观察性/RCT/诊断）
│   ├── statistics-methods/       # 统计与方法指南 (48章)
│   ├── reporting-guidelines/     # 报告规范检查清单（16个）
│   ├── risk-of-bias/             # 偏倚评估工具（5个）
│   ├── journal-templates/        # 期刊模板（7个）
│   ├── passport/                 # Material Passport 产物追踪
│   ├── contracts/                # Schema 定义（20个）
│   ├── handoff_schemas.md        # 跨Skill数据契约（12个Schema）
│   └── ...                       # 其他共享资源
│
├── resources/                    # 参考资源库（被 skills 引用）
│   ├── academic-paper/           # 📄 论文写作参考（agents/references/templates）
│   └── academic-pipeline/        # 📑 写作流水线参考（agents/references/templates）
│
├── scripts/                      # 辅助脚本
│   └── generate_msra_handoff_bundle.py
│
└── MSRA/                         # 运行时输出目录
    ├── data/                     # 用户数据
    ├── reports/                  # 分析报告
    ├── passport/                 # 产物护照
    └── calibration/              # 校准数据库
```

---

## 安装说明

### Windows

```powershell
# 克隆项目
git clone https://github.com/boangus/medical-stats-research-assistant.git
cd medical-stats-research-assistant

# 运行安装脚本
.\install.ps1

# 可选：跳过 R/Python 检查
.\install.ps1 -SkipR -SkipPython

# 卸载
.\uninstall.ps1
```

### Mac / Linux

```bash
# 克隆项目
git clone https://github.com/boangus/medical-stats-research-assistant.git
cd medical-stats-research-assistant

# 运行安装脚本
chmod +x install.sh
./install.sh

# 可选：跳过 R/Python 检查
./install.sh --skip-r --skip-python

# 卸载
chmod +x uninstall.sh
./uninstall.sh
```

### 安装后验证

安装完成后，在 Claude Code 中运行：

```
/msra --status
```

应显示所有8个skill已注册，10个命令可用。

---

## 设计理念

### Pipeline 驱动
- **纯调度**: Pipeline 不做实质性工作，只负责检测、推荐、调度、追踪
- **5 个阻断式质量门闸**: Stage 1.5（数据质量）、Stage 2.5（SAP质量）、Stage 3.5（结果质量）、Stage 5.5（审前完整性）、Stage 5.8（最终完整性）
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
- 产物追踪（Material Passport）

### 自包含性
- 8 个 skill 全部内置，无需额外安装
- 所有共享资源（模板、指南、schema）本地存储
- 跨平台支持（Windows/Mac/Linux）

---

## 核心功能

### 大规模数据处理引擎

内置统一的大规模数据处理引擎，支持自动引擎选择：

| 数据规模 | 引擎 | 适用场景 |
|---------|------|---------|
| <1GB | pandas | 小数据集，兼容性处理 |
| 1-10GB | Polars | 中型数据，高性能内存处理 |
| 10-100GB | DuckDB | 大型数据，SQL风格OLAP |
| >100GB | Dask | 超大型数据，分布式处理 |

**使用示例**:
```python
from shared.large_scale_processing import EngineFactory, EngineSelector

# 自动选择引擎
engine = EngineFactory.create_for_size(file_size_bytes=5 * 1024**3)

# 或手动指定
engine = EngineFactory.create_engine("polars")

# 统一API操作
df = engine.read_csv("data.csv")
result = engine.groupby_aggregate(df, ["group"], {"value": "mean"})
```

详细使用指南请参考: [`docs/large-scale-processing-guide.md`](docs/large-scale-processing-guide.md)

---

## 支持的统计方法

- **组间比较**: t检验、ANOVA、卡方、Mann-Whitney U、Kruskal-Wallis、Fisher精确检验、McNemar检验
- **回归分析**: 线性、Logistic、Poisson、负二项、条件Logistic、Cox
- **生存分析**: Kaplan-Meier、Log-rank、竞争风险（Fine-Gray）
- **高级方法**: 混合效应模型、GEE、倾向性评分（PSM/IPTW/重叠加权）、双重稳健估计（AIPW）、目标试验模拟（TTE）、多重插补、Meta分析、网络Meta分析、中介分析、孟德尔随机化、DID、RCS
- **诊断试验**: ROC、DeLong检验、Bland-Altman、DCA（决策曲线）
- **机器学习**: 随机森林、SVM、XGBoost、LightGBM、SHAP解释

## 支持的报告规范

CONSORT 2025 (RCT) · SPIRIT 2025 (试验协议) · STROBE (观察性) · PRISMA 2020 (系统综述) · PRISMA-NMA (网络Meta) · STARD 2015 (诊断) · TRIPOD+AI (预测模型) · TRIPOD-LLM (LLM研究) · CARE (病例报告) · ARRIVE (动物实验) · REMARK (肿瘤标志物) · statcheck · CHEERS 2022 (卫生经济学)

## 偏倚评估工具

| 工具 | 适用研究类型 | 文件 |
|------|------------|------|
| **RoB 2** | 随机对照试验 (RCT) | `shared/risk-of-bias/RoB_2_checklist.md` |
| **ROBINS-I V2** | 非随机干预研究 (NRSI) | `shared/risk-of-bias/ROBINS_I_V2_checklist.md` |
| **PROBAST+AI** | 临床预测模型 | `shared/risk-of-bias/PROBAST_checklist.md` |
| **QUADAS-2** | 诊断准确性研究 | `shared/risk-of-bias/QUADAS_2_checklist.md` |
| **GRADE** | 证据确定性汇总 | `shared/risk-of-bias/GRADE_framework.md` |

---

## 许可证

MIT License
