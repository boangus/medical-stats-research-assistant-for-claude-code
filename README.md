<p align="center">
  <img src="icon.png" width="120" alt="MSRA Logo">
</p>

<h1 align="center">Medical Statistics Research Assistant</h1>
<h3 align="center">从原始数据到可投稿论文 — 一条命令，完整流水线</h3>

<p align="center">
  <a href="https://github.com/boangus/medical-stats-research-assistant-for-claude-code/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="Version"></a>
  <a href="https://github.com/boangus/medical-stats-research-assistant-for-claude-code/actions"><img src="https://img.shields.io/badge/tests-319%20passed-brightgreen" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20%2B%20CC--BY--NC--SA-lightgrey" alt="License"></a>
  <a href="https://github.com/boangus/medical-stats-research-assistant-for-claude-code"><img src="https://img.shields.io/badge/platform-Windows%20%7C%20Mac%20%7C%20Linux-blueviolet" alt="Platform"></a>
</p>

<p align="center">
  <b>Claude Code 插件</b> · <b>13 个 Skill</b> · <b>16 个命令</b> · <b>5 个质量门闸</b> · <b>4 个扩展模块</b>
</p>

---

## 为什么选择 MSRA？

🔬 **完整流水线，一条命令** — 数据准备 → 统计分析 → 报告生成 → 论文写作 → 同行评审，16 个斜杠命令覆盖全链路。输入 `/msra`，从原始数据走到可投稿论文。

🛡️ **质量门闸，阻断式检查** — 5 道质量关卡（数据/SAP/结果/审前/最终），每道都有清单式检查，不通过就退回修订。分析可重复，偏差有记录。

🧬 **超越统计，多模态覆盖** — 4 个扩展模块（生物信息学、医学影像、实时分析、跨领域融合），从单细胞测序到放射组学。R + Python 双语言，319 个测试全通过。

🔒 **本地处理，数据不出本机** — 所有分析在本地完成，不上传任何数据。内置 HIPAA Safe Harbor 标识符检测。

---

## ⚡ 快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/boangus/medical-stats-research-assistant-for-claude-code.git
cd medical-stats-research-assistant
.\install.ps1          # Windows
# chmod +x install.sh && ./install.sh   # Mac / Linux

# 2. 验证安装（在 Claude Code 中）
/msra --status

# 3. 开始使用
/msra 我有一份RCT的原始数据，想完成整个分析
```

---

## 🗺️ Pipeline 全景

```
┌─────────────────────────────────────────────────────────────┐
│  MSRA 统一流水线                                             │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Stage 1  │───▶│ Stage 2  │───▶│ Stage 3  │               │
│  │ 数据准备  │    │ 分析计划  │    │ 分析执行  │               │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘               │
│       │🔴门闸         │🔴门闸         │🔴门闸                │
│       ▼               ▼               ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Stage 4  │───▶│ Stage 5  │───▶│ Stage 6  │               │
│  │ 报告生成  │    │ 论文写作  │    │ 过程总结  │               │
│  └──────────┘    └────┬─────┘    └──────────┘               │
│                       │🔴门闸×2                              │
│                       ▼                                      │
│                 📄 可投稿论文                                  │
└─────────────────────────────────────────────────────────────┘

🔴 = 阻断式质量门闸（不通过则退回修订）
```

**5 个阻断式质量门闸：**
| 门闸 | 位置 | 检查项 |
|:---:|------|:---:|
| 🔴 Gate 1.5 | 数据准备后 | 9 项数据质量检查 |
| 🔴 Gate 2.5 | SAP 制定后 | 8 项完整性检查 |
| 🔴 Gate 3.5 | 分析执行后 | 9 项结果检查 |
| 🔴 Gate 5.5 | 论文写作后 | 审前完整性检查 |
| 🔴 Gate 5.8 | 最终定稿前 | 最终完整性检查 |

---

## 📦 命令一览

### 统计分析

| 命令 | 功能 | 阶段 |
|------|------|------|
| `/msra` | 🚀 统一流水线入口（自动检测阶段） | 全流程 |
| `/msra-data` | 数据验证、清洗、质量门闸 | Stage 1 |
| `/msra-explore` | 探索性因果分析（PC/FCI 算法） | Stage 1.8 |
| `/msra-plan` | 方法探讨、SAP 制定与审查 | Stage 2 |
| `/msra-exec` | 按 SAP 执行分析 + 质量检查 | Stage 3 |
| `/msra-report` | 生成出版级统计报告 | Stage 4 |
| `/msra-calibrate` | 指标校准（金标准对比） | 校准 |

### 学术写作

| 命令 | 功能 | 说明 |
|------|------|------|
| `/msra-paper` | 进入论文写作轨道 | Stage 5 入口 |
| `/msra-write --mode <mode>` | 论文写作（9 种模式） | plan / abstract / revision / ... |
| `/msra-full` | 完整写作流水线 | 研究→写作→评审→修订→定稿 |
| `/msra-reviewer` | 多视角论文评审 | 5 人审稿团 |

### 扩展模块

| 命令 | 功能 | 测试 |
|------|------|:---:|
| `/msra-bio` | 🧬 生物信息学：单细胞/基因表达、差异表达、通路富集 | 62 |
| `/msra-imaging` | 📷 医学影像：DICOM/NIfTI、放射组学特征提取 | 60 |
| `/msra-rt` | ⚡ 实时分析：流处理、异常检测、告警 | 102 |
| `/msra-cross` | 🔗 跨领域融合：放射组学-DEG 关联、预测建模 | 95 |

---

## 🧪 支持的统计方法

**组间比较：** t 检验 · ANOVA · 卡方 · Mann-Whitney U · Kruskal-Wallis · Fisher 精确检验 · McNemar

**回归分析：** 线性 · Logistic · Poisson · 负二项 · 条件 Logistic · Cox

**生存分析：** Kaplan-Meier · Log-rank · 竞争风险（Fine-Gray）

**高级方法：** 混合效应模型 · GEE · 倾向性评分（PSM/IPTW/重叠加权）· 双重稳健估计（AIPW）· 目标试验模拟 · 多重插补 · Meta 分析 · 网络 Meta 分析 · 中介分析 · 孟德尔随机化 · DID · RCS

**诊断试验：** ROC · DeLong 检验 · Bland-Altman · DCA

**机器学习：** 随机森林 · SVM · XGBoost · LightGBM · SHAP 解释

---

## 📐 报告规范

CONSORT 2025 · SPIRIT 2025 · STROBE · PRISMA 2020 · PRISMA-NMA · STARD 2015 · TRIPOD+AI · TRIPOD-LLM · CARE · ARRIVE · REMARK · statcheck · CHEERS 2022

**偏倚评估工具：** RoB 2（RCT）· ROBINS-I V2（NRSI）· PROBAST+AI（预测模型）· QUADAS-2（诊断）· GRADE（证据汇总）

---

## 🛠️ 安装

### 系统要求

- **Claude Code** ≥ 3.7.0
- **Python** ≥ 3.9（推荐 3.11+）
- **R** ≥ 4.0（可选，用于统计分析）

### 安装步骤

**Windows：**
```powershell
git clone https://github.com/boangus/medical-stats-research-assistant-for-claude-code.git
cd medical-stats-research-assistant
.\install.ps1
```

**Mac / Linux：**
```bash
git clone https://github.com/boangus/medical-stats-research-assistant-for-claude-code.git
cd medical-stats-research-assistant
chmod +x install.sh
./install.sh
```

**可选参数：**
```bash
# 跳过 R/Python 环境检查
.\install.ps1 -SkipR -SkipPython    # Windows
./install.sh --skip-r --skip-python  # Mac/Linux
```

**验证安装：**
```
/msra --status
```

---

## 🏗️ 设计理念

- **Pipeline 驱动** — 编排器只负责检测、调度、追踪，不做实质性分析。从任意阶段切入，自动识别当前进度。
- **人机回环** — 清洗策略需批准，方法共同探讨，SAP 独立审查。任何偏差都有记录。
- **可重复性** — 每步生成可重复代码，严格按 SAP 执行，产物通过 Material Passport 追踪。
- **自包含性** — 9 个 Skill 全部内置，资源本地存储，Windows/Mac/Linux 跨平台。

---

## 📁 项目结构

```
medical-stats-research-assistant/
├── skills/            # 13 个内置 Skill
├── commands/          # 16 个命令定义
├── agents/            # 5 个 Agent 角色
├── shared/            # 共享资源（模板、指南、Schema）
│   ├── statistics-methods/    # 统计方法指南（47 章）
│   ├── reporting-guidelines/  # 报告规范清单（16 个）
│   ├── risk-of-bias/          # 偏倚评估工具（5 个）
│   └── journal-templates/     # 期刊模板（7 个）
├── msra_modules/      # 4 个扩展模块
├── tests/             # 测试套件（319 tests）
├── docs/              # 文档（用户教程 + API 参考）
├── install.ps1        # Windows 安装脚本
└── install.sh         # Mac/Linux 安装脚本
```

---

## 📄 许可证

本项目采用 **双许可证模式**：

| 类别 | 许可证 | 说明 |
|------|--------|------|
| **代码** (.py, .R, .sh, .json) | [MIT](https://opensource.org/licenses/MIT) | 自由使用，包括商业用途 |
| **知识库** (SKILL.md, 统计方法, 报告规范) | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) | 非商业，署名，相同方式共享 |

---

## ⚠️ 医学免责声明

**本工具仅供研究和教育用途，不构成医疗建议。** 统计分析结果不能替代专业生物统计学家的判断，生成的代码和报告必须经过领域专家审核后才能用于正式发表或决策。所有数据处理在本地完成，不会上传到任何外部服务器。

---

## 🙏 致谢

学术写作模块参考了 [academic-research-skills](https://github.com/Imbad0202/academic-research-skills)（by Cheng-I Wu, CC BY-NC 4.0）的设计理念，在此基础上针对医学研究场景进行了深度改造和扩展。

---

<p align="center">
  <b>从数据到论文，MSRA 帮你走完最后一步。</b><br>
  <sub>⭐ 如果这个项目对你有帮助，请给个 Star！</sub>
</p>
