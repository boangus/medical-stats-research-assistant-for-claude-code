<!--
  Design System: GitHub Markdown (无自定义 CSS)
  Badges: shields.io | 主色 blue, 状态 brightgreen/orange/red
  排版: Emoji 锚点 + Markdown 标准层级
  Anti-Slop: 无 HTML 标签, 无紫色渐变, 无编造统计
-->

<!-- Hero Section -->

<div align="center">

# 🧬 Medical Statistics Research Assistant (MSRA)

**从原始数据到可投稿论文的完整流水线 — Claude Code 的医学统计分析插件**

[![Version](https://img.shields.io/badge/version-v1.0.0-blue?style=flat-square)](https://github.com/boangus/medical-stats-research-assistant-for-claude-code/releases)
[![Tests](https://img.shields.io/badge/tests-319%20passed-brightgreen?style=flat-square)](https://github.com/boangus/medical-stats-research-assistant-for-claude-code/actions)
[![License](https://img.shields.io/badge/license-MIT%20%2B%20CC--BY--NC--SA--4.0-blue?style=flat-square)](#license)

</div>

---

## 📖 目录

- [Why MSRA?](#why-msra)
- [Quick Start](#quick-start)
- [Pipeline Overview](#pipeline-overview)
- [Commands](#commands)
- [Extension Modules](#extension-modules)
- [Supported Methods](#supported-methods)
- [Installation](#installation)
- [Architecture](#architecture)
- [Design Philosophy](#design-philosophy)
- [License](#license)
- [Disclaimer](#disclaimer)
- [Acknowledgments](#acknowledgments)

---

## Why MSRA?

> **不是又一个统计工具包。** MSRA 是一套端到端的医学研究辅助流水线，覆盖从数据清洗到论文撰写的每一个环节。

**🔬 Pipeline 驱动，而非碎片工具**

12 个阶段（6 统计 + 6 写作）串联为一条完整流水线。每个阶段有明确的输入输出，上一阶段的质量门闸决定下一阶段能否开始。

**🛡️ 5 道阻断式质量门闸**

数据就绪检查、统计假设验证、结果一致性校验、报告规范审查、论文结构审核 — 任何一道门闸失败，流水线立即停止，避免错误向下游传播。

**⚡ 开箱即用：13 Skill + 16 命令**

无需配置。安装后即可使用完整的统计分析和学术写作命令集，覆盖描述性统计、假设检验、回归分析、生存分析等核心场景。

**🔒 本地处理，数据不出本机**

所有计算在本地完成，原始数据不会上传至任何外部服务。适合处理含有 PHI（Protected Health Information）的临床数据。

---

## Quick Start

**1. 安装**

```bash
claude install mcp boangus/medical-stats-research-assistant-for-claude-code
```

**2. 验证安装**

```bash
msra status
```

预期输出应显示所有 13 个 Skill 已加载，319 个测试覆盖的模块状态为 ✅。

**3. 开始使用**

```bash
# 对 CSV 数据文件启动完整分析流水线
msra analyze data.csv

# 或从特定阶段开始
msra pipeline start --from cleaning data.csv
```

---

## Pipeline Overview

```
┌─────────────────── 统计分析阶段 ───────────────────┐
│                                                     │
│  📥 数据导入 ──▶ 🧹 数据清洗 ──▶ 📊 描述性统计     │
│       │                                  │          │
│       ▼                                  ▼          │
│  🚧 门闸-1                            🚧 门闸-2     │
│  (数据就绪)                         (假设验证)      │
│                                          │          │
│                                          ▼          │
│  📈 推断统计 ──▶ 🧮 回归建模 ──▶ 🔬 生存分析       │
│                                  │                   │
│                                  ▼                   │
│                              🚧 门闸-3               │
│                            (结果一致性)              │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────── 学术写作阶段 ───────────────────┐
│                                                     │
│  📝 结果整理 ──▶ 📋 方法描述 ──▶ 📑 报告生成       │
│                                    │                │
│                                    ▼                │
│                                🚧 门闸-4            │
│                              (报告规范)             │
│                                    │                │
│                                    ▼                │
│  ✍️ 论文草稿 ──▶ 🔍 审校修订                        │
│                       │                             │
│                       ▼                             │
│                   🚧 门闸-5                          │
│                (论文结构)                            │
│                       │                             │
│                       ▼                             │
│                   📄 输出终稿                        │
└──────────────────────────────────────────────────────┘
```

---

## Commands

MSRA 提供 **16 个命令**，按功能域分类：

### 数据与质量控制

| 命令 | 说明 | 示例 |
|------|------|------|
| `msra import` | 导入数据文件（CSV / Excel / SPSS / SAS） | `msra import data.csv` |
| `msra clean` | 数据清洗与预处理 | `msra clean --remove-na --dedup` |
| `msra validate` | 数据质量验证 | `msra validate data.csv` |
| `msra gate check` | 手动触发质量门闸检查 | `msra gate check --stage 1` |

### 统计分析

| 命令 | 说明 | 示例 |
|------|------|------|
| `msra describe` | 描述性统计分析 | `msra describe --vars age,bmi,gender` |
| `msra test` | 假设检验 | `msra test --method t-test --groups treatment,control` |
| `msra regress` | 回归建模 | `msra regress --type logistic --outcome event` |
| `msra survival` | 生存分析 | `msra survival --time months --event death` |
| `msra analyze` | 一键运行完整流水线 | `msra analyze data.csv` |

### 学术写作

| 命令 | 说明 | 示例 |
|------|------|------|
| `msra report` | 生成统计报告 | `msra report --format apa` |
| `msra draft` | 生成论文草稿 | `msra draft --template rct` |
| `msra review` | 审校与修订建议 | `msra review draft.md` |
| `msra cite` | 管理参考文献 | `msra cite --style vancouver` |

### 系统

| 命令 | 说明 | 示例 |
|------|------|------|
| `msra status` | 查看系统状态与已加载 Skill | `msra status` |
| `msra config` | 配置参数 | `msra config --lang r` |
| `msra pipeline` | 流水线控制 | `msra pipeline start --from cleaning` |

---

## Extension Modules

MSRA 的核心流水线之外，提供 **4 个可选扩展模块**：

| 模块 | 测试覆盖 | 说明 |
|------|---------|------|
| 🧬 **Bioinformatics** | 62 测试 | 基因表达分析、通路富集、差异表达检测 |
| 🩻 **Medical Imaging** | 60 测试 | DICOM 处理、影像特征提取、影像组学分析 |
| ⚡ **Real-time Analytics** | 102 测试 | 流式数据接入、实时监测看板、预警规则引擎 |
| 🔗 **Cross-domain Fusion** | 42 + 53 测试 | 多模态数据融合、跨领域关联分析 |

```bash
# 安装扩展模块
msra config --enable-extension bioinformatics
msra config --enable-extension medical-imaging
msra config --enable-extension real-time-analytics
msra config --enable-extension cross-domain-fusion
```

---

## Supported Methods

### 统计方法

- **描述性统计**：均值、中位数、标准差、四分位距、频率分布
- **假设检验**：t 检验（独立/配对）、卡方检验、Fisher 精确检验、Mann-Whitney U、Wilcoxon
- **方差分析**：单因素/多因素 ANOVA、重复测量 ANOVA、Kruskal-Wallis
- **回归分析**：线性回归、Logistic 回归（二元/有序/多项）、Cox 比例风险、Poisson 回归
- **生存分析**：Kaplan-Meier 估计、Log-rank 检验、Cox 回归、竞争风险分析
- **多重比较**：Bonferroni、FDR (Benjamini-Hochberg)、Holm
- **样本量计算**：基于效应量、检验力和显著性水平

### 报告规范

- APA 第 7 版
- CONSORT（RCT 报告）
- STROBE（观察性研究）
- PRISMA（系统综述）
- STARD（诊断准确性研究）

### 语言支持

- **R**：完整支持，包含 tidyverse 生态集成
- **Python**：完整支持，包含 pandas / scipy / statsmodels 集成

---

## Installation

### 前置条件

- [Claude Code](https://claude.ai/code) 已安装
- R (≥ 4.2) 或 Python (≥ 3.10) 至少安装其一

### 安装步骤

```bash
# 通过 Claude Code 安装
claude install mcp boangus/medical-stats-research-assistant-for-claude-code

# 验证安装
msra status
```

### 跨平台说明

| 平台 | 状态 | 备注 |
|------|------|------|
| macOS (Apple Silicon) | ✅ 推荐 | 原生支持 |
| macOS (Intel) | ✅ 支持 | — |
| Linux (Ubuntu/Debian) | ✅ 支持 | 需安装 `libcurl4-openssl-dev` |
| Windows (WSL2) | ✅ 支持 | 推荐使用 WSL2 |
| Windows (原生) | ⚠️ 实验 | 部分 R 包可能需要额外配置 |

---

## Architecture

```
medical-stats-research-assistant-for-claude-code/
├── skills/                  # 13 个 Skill 定义
│   ├── data-management/     # 数据导入、清洗、验证
│   ├── descriptive/         # 描述性统计
│   ├── inferential/         # 推断统计
│   ├── regression/          # 回归建模
│   ├── survival/            # 生存分析
│   ├── reporting/           # 报告生成
│   ├── writing/             # 学术写作
│   └── quality-gates/       # 质量门闸
├── extensions/              # 4 个扩展模块
│   ├── bioinformatics/
│   ├── medical-imaging/
│   ├── real-time-analytics/
│   └── cross-domain-fusion/
├── commands/                # 16 个命令实现
├── tests/                   # 319 个测试用例
└── config/                  # 默认配置与模板
```

---

## Design Philosophy

### 1. Pipeline 驱动

统计分析不是一系列孤立的步骤。MSRA 将数据处理、统计检验、结果解释和论文撰写串联为一条有向流水线，每个阶段的输出是下一阶段的输入，质量门闸确保链路的可靠性。

### 2. 人机回环

MSRA 不替代研究者的判断。关键决策节点（如异常值处理策略、模型选择、结果解释）需要研究者确认后才能继续。机器处理重复性工作，人做决策性判断。

### 3. 可重复性优先

所有分析步骤自动生成完整的审计日志，包括：随机种子、软件版本、参数设置、数据快照。任何人拿到日志都可以精确重现整个分析过程。

### 4. 自包含性

MSRA 不依赖外部数据库或云服务。所有依赖打包在插件内，断网环境下仍可正常工作。适合对数据安全有严格要求的医疗研究场景。

---

## License

本项目采用 **双许可证** 模式：

| 部分 | 许可证 | 说明 |
|------|--------|------|
| 代码 | [MIT License](https://opensource.org/licenses/MIT) | 自由使用、修改和分发 |
| 文档与内容 | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) | 署名-非商业性使用-相同方式共享 |

---

## Disclaimer

> ⚠️ **重要声明**
>
> MSRA 是一个辅助研究工具，**不构成医学建议**。所有统计分析结果应由具备相关资质的医学研究者或生物统计师审核后方可用于临床决策或学术发表。
>
> 使用者应确保其研究活动符合所属机构的伦理审查委员会（IRB/REC）要求和适用的数据保护法规（如 HIPAA、GDPR）。
>
> 本工具不对分析结果的准确性、完整性或适用性做任何明示或暗示的保证。

---

## Acknowledgments

- [Claude Code](https://claude.ai/code) — 运行环境
- R 社区与 CRAN — 统计计算生态
- Python 科学计算社区 — pandas、scipy、statsmodels
- 所有为开源医学统计工具做出贡献的研究者

---

<div align="center">

**[⬆ 回到顶部](#-medical-statistics-research-assistant-msra)**

Made for medical researchers who care about rigor.

</div>
