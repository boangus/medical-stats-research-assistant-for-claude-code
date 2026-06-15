# Medical Statistics Research Assistant (MSRA)

医学统计研究助手 — 面向医学研究者的统计分析流水线

[![CI](https://github.com/boangus/medical-stats-research-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/boangus/medical-stats-research-assistant/actions/workflows/ci.yml)

一个以 **Pipeline 驱动** 的医学统计分析工具集。从原始数据到最终报告，4 个阶段、6 个命令，覆盖完整的医学统计分析流程。无论你从哪个阶段开始，Pipeline 都能自动识别并引导你完成后续工作。

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
│  8 项数据质量检查 → ✅ 通过 / ❌ 退回修订             │
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
| `/msra-calibrate` | 指标校准（金标准对比） | 校准 |

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
├── skills/                       # 6 个 Skill
│   ├── pipeline/                 # 🔀 流水线编排器（核心）
│   │   └── SKILL.md
│   ├── data-prep/                # 📊 数据准备
│   │   └── SKILL.md
│   ├── analysis-plan/            # 📋 分析计划
│   │   └── SKILL.md
│   ├── analysis-exec/            # ⚙️ 分析执行
│   │   └── SKILL.md
│   ├── report/                   # 📝 报告生成
│   │   └── SKILL.md
│   └── calibration/              # 🎯 指标校准
│       └── SKILL.md
│
├── agents/                       # 多 Agent 定义
│   ├── AGENTS.md                 # 团队架构
│   ├── protocol.md               # 协作协议
│   ├── data_validator_agent.md   # 数据质量专家
│   ├── method_consultant_agent.md# 方法顾问
│   ├── exec_runner_agent.md      # 代码执行者
│   ├── exec_inference_agent.md   # 推断执行者
│   └── qc_inspector_agent.md     # 质量审查员
│
├── shared/                       # 共享资源
│   ├── templates/                # 代码模板 (R + Python)
│   │   ├── 00_config_template.R  # 配置脚本模板
│   │   ├── 02_var_define_template.R  # 变量定义模板
│   │   ├── 03_baseline_template.R    # 基线分析模板
│   │   └── 04_iptw_template.R        # IPTW分析模板
│   ├── project-templates/        # 项目结构模板
│   │   └── structured-analysis-workflow.md  # input/script/outcome 结构
│   ├── sample-size/              # 样本量计算
│   ├── causal-inference/         # 因果推断工作流
│   ├── reproducibility/          # 可重复性验证
│   ├── calibration/              # 校准框架
│   ├── passport/                 # Material Passport 产物追踪
│   ├── statistics-methods/       # 统计与方法指南 (48章) + 方法目录
│   ├── value-normalization/      # 值规范化（TCM术语+数值变体）
│   ├── chart-styles/             # 图表样式库（期刊配色、图表类型、字体规范）
│   ├── error-diagnostics/        # 错误诊断知识库（错误模式、自动修复建议）
│   ├── anti-patterns/            # 反模式黑名单
│   ├── reporting-guidelines/     # 报告规范检查清单（CONSORT 2025/SPIRIT 2025/STROBE/PRISMA-NMA/TRIPOD+AI/TRIPOD-LLM/CARE/REMARK/ARRIVE/statcheck/CHEERS 2022）
│   ├── risk-of-bias/             # 🆕 偏倚评估工具（RoB 2/ROBINS-I V2/PROBAST+AI/QUADAS-2/GRADE）
│   ├── journal-templates/        # 期刊模板（NEJM/JAMA/Lancet/BMJ/CMJ/AIM/CJE）
│   ├── report-assembler/         # 报告组装器（DOCX/HTML输出）
│   ├── sensitivity-agreement/    # 敏感性分析一致性评估
│   ├── sap/                      # SAP标准化、一致性检查与方法转换
│   ├── data_sharing/             # 数据共享（去标识化、代码包、结果包生成）
│   └── archive/                  # 存档包（产物收集、清单生成、完整性验证）
│
├── docs/                         # 文档
│   └── PIPELINE.md               # 架构与流水线详细文档
│
├── examples/                     # 使用示例
│   └── example_workflow.md
│
└── MSRA/                         # 运行时输出目录（由 install.ps1 创建）
    ├── data/                     # 用户数据
    ├── reports/                  # 分析报告
    │   ├── figures/              # 图表
    │   └── tables/               # 表格
    ├── passport/                 # 产物护照
    └── calibration/              # 校准数据库
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

## 结构化分析工作流 (input/script/outcome)

MSRA 支持基于目录分离的标准化分析项目结构，灵感来自成熟的医学统计项目实践：

### 目录结构

```
project/
├── input/                    # 输入数据（原始数据，只读）
│   ├── raw_data.csv         # 原始数据文件
│   ├── data_dictionary.xlsx # 数据字典
│   └── inclusion_criteria.md # 纳入排除标准
│
├── script/                   # 分析脚本（按执行顺序编号）
│   ├── 00_config.R          # 全局配置
│   ├── 01_data_extract.R    # 数据提取
│   ├── 02_var_define.R      # 变量定义
│   ├── 03_baseline.R        # 基线分析
│   ├── 04_iptw_matching.R   # 倾向性评分
│   └── 05_survival_analysis.R # 生存分析
│
├── load/                     # 中间数据（各步骤缓存）
│   ├── 01_extracted.rda     # 提取后的数据
│   ├── 02_var_defined.rda   # 变量定义后的数据
│   └── 04_iptw.rda          # IPTW数据
│
└── outcome/                  # 最终结果
    ├── tables/              # 表格输出
    ├── figures/             # 图表输出
    └── reports/             # 报告文档
```

### 核心原则

1. **输入只读**: `input/` 中的文件永不修改，保留原始数据可追溯性
2. **脚本编号化**: `00-`, `01-`, `02-` 前缀表示执行顺序
3. **中间数据缓存**: 每步保存 `.rda` 到 `load/`，支持断点续跑
4. **变量集中定义**: 在 `02_var_define.R` 统一定义标签、协变量、亚组
5. **输入输出声明**: 每个脚本顶部声明 `input_file` 和 `output_dir`

### 快速开始

```bash
# 1. 创建项目结构
mkdir -p my_project/{input,script,load,outcome/{tables,figures,reports}}

# 2. 复制模板脚本
cp shared/templates/00_config_template.R my_project/script/00_config.R
cp shared/templates/02_var_define_template.R my_project/script/02_var_define.R

# 3. 放入原始数据
cp my_data.csv my_project/input/raw_data.csv

# 4. 按顺序运行脚本
cd my_project
Rscript script/00_config.R
Rscript script/01_data_extract.R
Rscript script/02_var_define.R
# ... 继续后续分析
```

详细指南请查看: [shared/project-templates/structured-analysis-workflow.md](shared/project-templates/structured-analysis-workflow.md)

---

## 支持的统计方法

- **组间比较**: t检验、ANOVA、卡方、Mann-Whitney U、Kruskal-Wallis、Fisher精确检验、McNemar检验
- **回归分析**: 线性、Logistic、Poisson、负二项、条件Logistic、Cox
- **生存分析**: Kaplan-Meier、Log-rank、竞争风险（Fine-Gray）
- **高级方法**: 混合效应模型、GEE、倾向性评分（PSM/IPTW/重叠加权）、双重稳健估计（AIPW）、目标试验模拟（TTE）、多重插补、Meta分析、网络Meta分析、中介分析、孟德尔随机化、DID、RCS
- **诊断试验**: ROC、DeLong检验、Bland-Altman、DCA（决策曲线）
- **机器学习**: 随机森林、SVM、XGBoost、LightGBM、SHAP解释

## 支持的报告规范

CONSORT 2025 (RCT, 30项) · **SPIRIT 2025 (试验协议, 34项) 🆕** · STROBE (观察性) · PRISMA (系统综述) · PRISMA-NMA (网络Meta) · STARD (诊断) · TRIPOD+AI (预测模型, 27项) · **TRIPOD-LLM (LLM研究, 19+50项) 🆕** · CARE (病例报告) · ARRIVE (动物实验) · REMARK (肿瘤标志物) · **statcheck 统计一致性校验 🆕** · **CHEERS 2022 (卫生经济学, 28项) 🆕**

## 偏倚评估工具

> 系统综述/Meta 分析中评估纳入研究偏倚风险和证据确定性的专用工具，与报告规范互补使用。

| 工具 | 适用研究类型 | 域数 | 判断等级 | 文件 |
|------|------------|------|---------|------|
| **RoB 2** | 随机对照试验 (RCT) | 5 域 | Low/Some/High | `shared/risk-of-bias/RoB_2_checklist.md` |
| **ROBINS-I V2** | 非随机干预研究 (NRSI) | 7 域 | Low/Mod/Serious/Critical | `shared/risk-of-bias/ROBINS_I_V2_checklist.md` |
| **PROBAST+AI** | 临床预测模型 | 4 域 20 信号问题 | Low/High/Unclear | `shared/risk-of-bias/PROBAST_checklist.md` |
| **QUADAS-2** | 诊断准确性研究 | 4 域 | Low/High/Unclear | `shared/risk-of-bias/QUADAS_2_checklist.md` |
| **GRADE** | 证据确定性汇总 | 5 降级+3 升级 | ⊕⊕⊕⊕ ~ ⊕○○○ | `shared/risk-of-bias/GRADE_framework.md` |

---

---

## 许可证

MIT License



