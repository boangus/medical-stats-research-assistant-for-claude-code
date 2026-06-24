# Medical Statistics Research Assistant (MSRA)

医学统计研究助手 — 从原始数据到可投稿论文的统一流水线

[![CI](https://github.com/boangus/medical-stats-research-assistant-for-claude-code/actions/workflows/ci.yml/badge.svg)](https://github.com/boangus/medical-stats-research-assistant-for-claude-code/actions/workflows/ci.yml)

一个以 **Pipeline 驱动** 的医学统计分析 + 学术写作工具集。从原始数据到最终报告，再到可投稿论文，6 个统计阶段 + 6 个写作阶段，覆盖完整的医学研究流程。无论你从哪个阶段开始，Pipeline 都能自动识别并引导你完成后续工作。

**9 个内置 Skill，16 个命令，开箱即用，无需额外安装**。

> **English Summary**: A pipeline-driven medical statistics analysis and academic writing toolkit. Covers 6 statistical stages (data preparation → exploratory causal analysis → analysis planning → execution → reporting) + 6 writing stages (literature search → paper writing → peer review → revision → finalization). 9 built-in skills, 16 slash commands, cross-platform (Windows/Mac/Linux). Clone the repo, run `install.sh` (Mac/Linux) or `.\install.ps1` (Windows), then invoke `/msra` in your AI coding assistant to start.

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
/msra-full 帮我写一篇关于肺癌靶向治疗的综述

# 探索性因果分析（不确定研究方向时）
/msra-explore data.csv --mode causal-discovery

# 直接生成基线表格
/msra-report --type table1

# 多视角论文评审
/msra-reviewer

# 跨领域多模态融合分析
/msra-cross --scenario correlation --radiomics features.csv --expression deg.csv
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
│  Stage 1.8: 探索性因果分析  /msra-explore           │
│  因果发现 → 混杂识别 → 假设生成 → 研究方向报告       │
│  [可选] 无先验假设时执行 / 有明确SAP时可跳过          │
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
│  Stage 5.1: Literature Search  /msra-write --mode lit-review     │
│  文献检索 + 综述撰写 + 参考文献库                    │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.2: Paper Writing  /msra-write --mode plan               │
│  IMRaD 章节撰写（复用方法学和表格图表）             │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 5.5: Integrity Check                      │
│  完整性检查（阻断式）→ ✅ / ❌                       │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.6: Peer Review  /msra-reviewer             │
│  5人评审团（EIC+方法学+领域+写作+DA）               │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.7: Revision  /msra-write --mode revision                │
│  修订 + Response to Reviewers                      │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  🔴 Stage 5.8: Final Integrity                     │
│  最终完整性检查（阻断式）→ ✅ / ❌                    │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5.9: Finalize  /msra-write --mode format-convert          │
│  定稿导出（MD → DOCX → PDF）                        │
└──────────────────┬──────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────┐
│  Stage 6: Process Summary                          │
│  完整过程记录 + AI 自我反思 + 协作质量评估          │
└─────────────────────────────────────────────────────┘
```

---

## 命令一览（16个）

### 📊 统计分析（8个）

| 命令 | 功能 | 对应阶段 |
|------|------|---------|
| `/msra` | 启动统一流水线（自动检测入口） | 全流程 |
| `/msra-data` | 数据验证与清洗 | Stage 1 |
| `/msra-explore` | 探索性因果分析（不确定研究方向时使用） | Stage 1.8 |
| `/msra-plan` | 方法探讨、SAP制定与审查 | Stage 2 |
| `/msra-exec` | 按SAP执行分析 + 质量检查 | Stage 3 |
| `/msra-report` | 生成出版级统计报告 | Stage 4 |
| `/msra-calibrate` | 指标校准（金标准对比） | 校准 |
| `/msra-paper` | 进入论文写作轨道（Stage 5.0） | Stage 5.0 |

### ✍️ 学术写作（3个）

| 命令 | 功能 | 说明 |
|------|------|------|
| `/msra-write --mode <mode>` | 论文写作（9种模式：plan/abstract/revision/...） | `report/SKILL.md` |
| `/msra-full` | 完整写作流水线：研究→写作→评审→修订→定稿 | `pipeline/SKILL.md` |
| `/msra-reviewer` | 多视角论文评审（5人评审团） | `peer-review` |

### 🧬 扩展模块（5个）

| 命令 | 功能 | 说明 |
|------|------|------|
| `/msra-modules [list\|info\|check]` | 管理扩展模块（医学影像、生物信息、实时分析、跨领域） | `msra_modules` |
| `/msra-cross` | 跨领域多模态融合：放射组学-DEG关联、实时预测建模、多模态可视化 | `cross_domain` |
| `/msra-bio` | 生物信息学分析：单细胞/基因表达、差异表达、通路富集 | `bioinformatics` |
| `/msra-imaging` | 医学影像分析：DICOM/NIfTI加载、放射组学特征提取 | `medical_imaging` |
| `/msra-rt` | 实时分析：生命体征流处理、异常检测、告警 | `realtime_analytics` |

---

## 9 个内置 Skill

| Skill | 名称 | 职责 | 核心能力 |
|-------|------|------|---------|
| **pipeline** | 统一编排器 | Stage 1-6 全流程调度 | 意图检测、阶段识别、任务分发 |
| **data-prep** | 数据准备 | Stage 1 | 数据验证、清洗、EDA、盲态审核 |
| **exploratory-causal** | 探索性因果分析 | Stage 1.8 | 因果发现(PC/FCI)、混杂识别、假设生成 |
| **analysis-plan** | 分析计划 | Stage 2 | 估计目标定义、方法探讨、SAP制定 |
| **analysis-exec** | 分析执行 | Stage 3 | R/Python代码生成、统计分析执行 |
| **report** | 报告生成 + 论文写作 | Stage 4-5 | 表格/图表生成、IMRaD撰写、格式导出 |
| **calibration** | 度量校准 | 校准 | 金标准对比、指标校准 |
| **peer-review** | 医学论文评审 | Stage 5.6 | 5人审稿团、CONSORT/STROBE合规、修订建议 |
| **systematic-survey** | 医学文献检索 | Stage 5.1 | PubMed/Embase检索、PRISMA流程、GRADE评级 |

---

## 项目结构

```
medical-stats-research-assistant/
├── manifest.json                 # 插件清单
├── README.md                     # 本文件
├── LICENSE                       # 双许可证 (MIT + CC BY-NC-SA 4.0)
├── CONTRIBUTING.md               # 贡献指南
├── SECURITY.md                   # 安全策略
├── CHANGELOG.md                  # 版本变更记录
├── requirements.txt              # Python 依赖
├── requirements-dev.txt          # 开发依赖（pytest, ruff）
├── config.local.yaml.example     # 本地配置示例
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
├── commands/                     # 命令定义（16个）
│   ├── msra.md                   # 统一流水线入口
│   ├── msra-data.md              # 数据准备
│   ├── msra-explore.md           # 探索性因果分析
│   ├── msra-plan.md              # 分析计划
│   ├── msra-exec.md              # 分析执行
│   ├── msra-report.md            # 报告生成
│   ├── msra-calibrate.md         # 指标校准
│   ├── msra-paper.md             # 论文轨道
│   ├── msra-write.md             # 论文写作（9种模式）
│   ├── msra-full.md              # 完整写作流水线
│   ├── msra-reviewer.md          # 论文评审
│   ├── msra-modules.md           # 扩展模块管理
│   ├── msra-cross.md             # 跨领域融合
│   ├── msra-bio.md               # 生物信息学
│   ├── msra-imaging.md           # 医学影像
│   └── msra-rt.md                # 实时分析
│
├── skills/                       # 10 个 Skill
│   ├── pipeline/                 # 🔀 统一编排器（核心）
│   ├── data-prep/                # 📊 数据准备
│   ├── exploratory-causal/       # 🔬 探索性因果分析
│   ├── analysis-plan/            # 📋 分析计划
│   ├── analysis-exec/            # ⚙️ 分析执行
│   ├── report/                   # 📝 报告生成
│   ├── calibration/              # 🎯 指标校准
│   ├── peer-review/              # 🔍 论文评审
│   ├── systematic-survey/        # 📚 文献检索
│   ├── bioinformatics/           # 🧬 生物信息学
│   ├── imaging-analysis/         # 📷 医学影像分析
│   ├── realtime-monitor/         # ⚡ 实时监控
│   └── cross-domain/             # 🔗 跨领域融合
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
│   ├── statistics-methods/       # 统计与方法指南 (47章)
│   ├── reporting-guidelines/     # 报告规范检查清单（16个）
│   ├── risk-of-bias/             # 偏倚评估工具（5个）
│   ├── journal-templates/        # 期刊模板（7个）
│   ├── passport/                 # Material Passport 产物追踪
│   ├── contracts/                # Schema 定义（12个）
│   ├── handoff_schemas.md        # 跨Skill数据契约（12个Schema）
│   └── ...                       # 其他共享资源
│
├── resources/                    # 参考资源库（被 skills 引用）
│   └── external/                 # 外部服务集成（PubMed/Embase API）
│
├── msra_modules/                 # 扩展模块（医学影像、生物信息、实时分析、跨领域）
│   ├── medical_imaging/          # 📷 医学影像处理（DICOM、分割、分类）🟢 Stable
│   ├── bioinformatics/           # 🧬 生物信息学（scRNA-seq、差异表达）🟢 Stable
│   ├── realtime_analytics/       # ⚡ 实时数据分析（流处理、异常检测）🟢 Stable
│   ├── cross_domain/             # 🔗 跨领域多模态融合 🟢 Stable
│   ├── __init__.py               # 模块导出接口
│   └── cli.py                    # 命令行工具
│
├── scripts/                      # 辅助脚本
│   ├── generate_msra_handoff_bundle.py
│   ├── lint_skill_structure.py     # SKILL.md 结构验证
│   ├── check_pipeline_integrity.py
│   ├── check_sprint_contract.py
│   ├── eval_pipeline_gold.py
│   ├── lint_gate_counts.py
│   ├── benchmark_large_scale.py
│   └── migrate_print_to_logging.py
│
├── tests/                        # 测试套件（319 tests, 0 failed）
│   ├── test_cross_domain/        # 跨领域模块单元测试（42 tests）
│   ├── test_bioinformatics/      # 生物信息学测试（62 tests）
│   ├── test_medical_imaging/     # 医学影像测试（60 tests）
│   ├── test_realtime_analytics/  # 实时分析测试（102 tests）
│   └── e2e/                      # 端到端测试（53 tests, 10 scenarios）
│
├── docs/                         # 文档
│   ├── dev/                      # 开发文档（28份）
│   ├── user_guide/               # 用户教程（8份，4模块×中英双语）
│   └── api/                      # API参考（8份，4模块×中英双语）
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
git clone https://github.com/boangus/medical-stats-research-assistant-for-claude-code.git
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
git clone https://github.com/boangus/medical-stats-research-assistant-for-claude-code.git
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

应显示所有9个skill已注册，16个命令可用。

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
- 9 个 skill 全部内置，无需额外安装
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

### 探索性因果分析

数据驱动的因果发现能力，适合无先验假设的探索性研究：

| 功能 | 说明 |
|------|------|
| **因果发现** | PC/FCI算法自动发现潜在因果结构 |
| **混杂识别** | 自动识别混杂变量和碰撞因子 |
| **假设生成** | 基于Bradford Hill准则生成研究假设 |
| **敏感性分析** | E-value + 负对照验证因果稳健性 |

**使用示例**:
```bash
# 完整因果探索
/msra-explore data.csv --mode causal-discovery

# 针对特定暴露-结局的混杂分析
/msra-explore --mode confounding --exposure treatment --outcome survival

# 生成研究假设
/msra-explore --mode hypothesis
```

### 变量标准化

内置医疗变量标准化模块，支持40+医学变量映射和统计格式规范：

| 功能 | 说明 |
|------|------|
| **变量映射** | 自动将原始变量名标准化为学术规范命名 |
| **统计格式化** | P值/置信区间/中位数IQR/均值SD/生存时间统一格式 |
| **数据标准化** | DataFrame列级标准化处理 |

### 扩展模块（全部 Stable）

MSRA 提供 4 个扩展模块，覆盖医学影像、生物信息学、实时分析和跨领域融合：

| 模块 | 命令 | 成熟度 | 测试数 | 说明 |
|------|------|--------|--------|------|
| **bioinformatics** | `/msra-bio` | 🟢 Stable | 62 | 单细胞/基因表达分析、差异表达、通路富集 |
| **medical_imaging** | `/msra-imaging` | 🟢 Stable | 60 | DICOM/NIfTI加载、放射组学特征提取、特征选择 |
| **realtime_analytics** | `/msra-rt` | 🟢 Stable | 102 | 流处理、异常检测（Z-Score/IQR/Isolation Forest）、告警 |
| **cross_domain** | `/msra-cross` | 🟢 Stable | 42+53 | 多模态融合：放射组学-DEG关联、实时预测建模、多模态可视化 |

**跨领域融合使用示例**:
```bash
# 放射组学特征与差异表达基因关联分析
/msra-cross --scenario correlation --radiomics features.csv --expression deg.csv

# 实时数据预测建模
/msra-cross --scenario prediction --realtime vitals.csv --labels labels.csv

# 多模态联合可视化
/msra-cross --scenario visualization --radiomics features.csv --expression deg.csv --clinical clinical.csv --realtime vitals.csv
```

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

本项目采用 **双许可证模式**：

| 类别 | 许可证 | 说明 |
|------|--------|------|
| **代码** (.py, .R, .sh, .ps1, .json, .yml) | [MIT](https://opensource.org/licenses/MIT) | 自由使用，包括商业用途 |
| **知识库** (SKILL.md, 统计方法, 报告规范, 代码模板, 期刊模板) | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) | 非商业，署名，相同方式共享 |

- ✅ **代码自由使用** — Python/R 代码可在 MIT 许可下自由使用、修改、分发（含商用）
- ✅ **学术使用** — 知识库内容可自由用于学术研究和教育
- ✅ **署名要求** — 使用知识库内容时需注明来源
- ❌ **知识库商用禁止** — 知识库内容不得用于商业用途
- 📧 **商用授权** — 如需商业使用知识库内容，请联系项目维护者

This project uses a **dual-license model**: code files are licensed under [MIT](https://opensource.org/licenses/MIT), and knowledge-base files (SKILL.md, reporting guidelines, statistics methods, code templates) are licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). See [LICENSE](LICENSE) for details.

---

## Acknowledgments / 致谢

本项目的学术写作模块参考了 [academic-research-skills](https://github.com/Imbad0202/academic-research-skills)（by Cheng-I Wu, CC BY-NC 4.0）的设计理念，并在此基础上针对医学研究场景进行了深度改造和扩展。感谢原作者的开源贡献。

---

## Medical Disclaimer / 医学免责声明

**本工具仅供研究和教育用途，不构成医疗建议。**

- 本项目提供的统计分析结果**不能替代专业生物统计学家的判断**
- 生成的分析代码和报告**必须经过领域专家审核**后才能用于正式发表或决策
- 本工具不提供临床诊断、治疗建议或药物推荐
- 用户对其数据的合规性（HIPAA/GDPR/当地法规）负全部责任
- 本工具处理的数据**不会上传到任何外部服务器**，所有分析在本地完成

**This tool is for research and educational purposes only. It does not constitute medical advice.** Statistical outputs must be reviewed by qualified professionals before use in publications or decision-making. Users are solely responsible for compliance with applicable data protection regulations (HIPAA/GDPR/local laws). All data processing occurs locally — no data is transmitted to external servers.

## Privacy & Data Security / 隐私与数据安全

- **本地处理**: 所有数据分析在用户本地环境完成，不依赖外部 API 进行统计计算
- **无数据上传**: 用户数据不会被发送到任何第三方服务
- **PHI 检测**: 内置 HIPAA Safe Harbor 18 类标识符自动检测（`shared/data_sharing/deidentification.py`）
- **日志控制**: 分析日志存储在本地 `MSRA/` 目录，用户可随时清除
- **依赖安全**: Python 依赖均为开源科学计算库（pandas, numpy, scipy 等），无遥测或数据收集组件
