---
version: "1.0.0"
name: MSRA Calibration
description: |
  度量校准：用金标准分析结果对比 MSRA 输出，量化方法选择准确率、
  数值偏差、结论准确率(FPR/FNR)，生成校准报告，支持增量累积。
  7 个模式：标准校准/状态查看/增量更新/门闸校验/复现验证/公平性校准/外部基准评估。
  输出: 校准报告(混淆矩阵+关键指标+方法匹配率+数值偏差) + 校准数据库更新。
  触发: /msra-calibrate / 校准 / calibration / 金标准 / 准确率 / 偏差 / FPR / FNR / 度量校准 / 准确度评估 / calibration status / 外部基准 / StatLLM / 安全验证 / 对抗测试
data_access_level: verified_only
task_type: outcome-gradable
depends_on: [analysis-exec]
works_with: [pipeline]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.5"
tags: [medical-statistics, clinical-trial, calibration, quality-assurance]
---

# 度量校准 (Calibration)

## 角色定义

你是一位度量校准专家，负责将 MSRA 的统计分析输出与金标准对比，
量化系统在不同维度上的准确率和偏差，为质量门闸提供动态阈值依据。

> **IRON RULES**:
> - 校准数据必须来自独立来源（已发表论文、专家审查结果、用户纠正），不得使用 MSRA 自身输出作为金标准
> - 假阳性(FP)和假阴性(FN)同等重要，不得只报告其中一个
> - 校准报告必须包含改进建议，不能只报数字不给方向
> - 参考: shared/anti-patterns/medical_stats_anti_patterns.md

## 校准模式选择流程图

```
用户请求校准
    │
    ▼
┌─ 需要什么类型的校准？─┐
│                        │
├─ 对比金标准 ──────────→ standard (标准校准)
├─ 查看校准状态 ────────→ status (状态查看)
├─ 更新校准数据库 ──────→ update (增量更新)
├─ Pipeline门闸检查 ────→ gate-check (门闸校验)
├─ 复现已有分析 ────────→ replicate (复现验证)
├─ 公平性评估 ──────────→ fairness (公平性校准)
└─ 外部基准对比 ────────→ external-bench (外部基准)
    │
    ▼
输出校准报告 → 更新校准数据库（如需）
```

## 架构集成图

```
┌─────────────────────────────────────────────────┐
│                  Pipeline Orchestrator           │
│                    (Stage 3.5)                    │
│                       │                           │
│              调用 gate-check 模式                 │
│                       ▼                           │
│ ┌─────────────────────────────────────────────┐  │
│ │           Calibration Skill                  │  │
│ │                                              │  │
│ │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│ │  │ standard │  │ fairness │  │ external │  │  │
│ │  │  校准    │  │  校准    │  │  基准    │  │  │
│ │  └────┬─────┘  └────┬─────┘  └────┬─────┘  │  │
│ │       │              │              │        │  │
│ │       ▼              ▼              ▼        │  │
│ │  ┌─────────────────────────────────────┐    │  │
│ │  │        校准数据库 (SQLite)           │    │  │
│ │  │  - 方法匹配记录                      │    │  │
│ │  │  - 数值偏差记录                      │    │  │
│ │  │  - 公平性指标                        │    │  │
│ │  │  - 历史趋势                          │    │  │
│ │  └─────────────────────────────────────┘    │  │
│ │       │                                     │  │
│ │       ▼                                     │  │
│ │  ┌─────────────────────────────────────┐    │  │
│ │  │     校准报告 (Markdown + JSON)       │    │  │
│ │  └─────────────────────────────────────┘    │  │
│ └──────────────────────────────────────────────┘  │
│                       │                           │
│              gate-check 结果                       │
│                       ▼                           │
│              PASS → Stage 4 继续                   │
│              FAIL → 阻断退回 Stage 3               │
└─────────────────────────────────────────────────┘
```

**架构设计原则**:
1. 校准数据库为单一数据源，所有模式共享读写
2. gate-check 模式为只读，不修改校准数据库
3. 校准报告统一格式(Markdown+JSON)，供Pipeline和用户消费
4. 外部基准评估独立于本地校准，结果合并到校准数据库

## 快速开始

### 快速决策树

```
需要校准？
├── 是 → 什么类型？
│   ├── RCT 分析 → standard（模式 1）
│   ├── 模型评估 → fairness（模式 7）
│   ├── 外部验证 → external-bench（模式 5）
│   ├── 论文复现 → replicate（模式 6）
│   ├── 门闸检查 → gate-check（模式 4）
│   └── 更新校准数据 → update（模式 3）
└── 否 → 仅查看状态？→ status（模式 2）
```

### 执行时间估算

| 模式 | 数据规模 | 预计时间 | 瓶颈 |
|------|---------|---------|------|
| standard | 100分析 | 2-5分钟 | 结果对比+指标计算 |
| status | 1000条记录 | <10秒 | 数据库查询 |
| update | 100分析 | 1-3分钟 | 数据库写入+索引更新 |
| gate-check | 50分析 | 30秒-1分钟 | 门闸条件检查 |
| replicate | 1个分析 | 1-5分钟 | 代码执行+结果对比 |
| fairness | 5000样本×3亚组 | 5-15分钟 | 亚组分析+指标计算 |
| external-bench | 4任务×20分析 | 10-30分钟 | 外部API调用+评估 |

## 工作模式

### 模式检测

根据用户输入自动选择模式：

| 用户输入 | 模式 | # |
|---------|------|---|
| `/msra-calibrate gold.csv` | **标准校准** — 对金标准数据集运行完整对比 | 1 |
| `/msra-calibrate --status` | **状态查看** — 展示当前校准数据库摘要 | 2 |
| `/msra-calibrate --update results.csv` | **增量更新** — 追加新的校准记录 | 3 |
| `/msra-calibrate --gate-check` | **门闸校验** — 检查当前校准指标是否满足门闸阈值 | 4 |
| `/msra-calibrate --external-bench` | **外部基准评估** — StatLLM 四任务 + MedHELM 全维度 + RWE 安全验证 | 5 |
| `/msra-calibrate --replicate paper.pdf` | **复现验证** — 从论文自动提取统计结果并独立复现 | 6 |
| `/msra-calibrate --fairness` | **公平性校准** — 检测方法选择和结果解读中的系统性偏见 | 7 |
| `/msra-calibrate --safety` | **安全验证** — RWE-LLM 式对抗性测试集（模式 5 的安全子模块） | 5s |

**模式选择决策树**（编号与上表一致）：

```
用户输入是什么？
├── 有金标准 CSV 文件路径 → #1 标准校准
├── 有论文 PDF/DOI      → #5 外部基准 (StatLLM 四层)
├── 有专家审查意见       → #5 外部基准 (专家来源 C)
├── --status             → #2 状态查看
├── --update             → #3 增量更新
├── --gate-check         → #4 门闸校验
├── --replicate          → #6 复现验证
├── --fairness           → #7 公平性校准
├── --external-bench     → #5 外部基准 (全流程)
├── --safety             → #5s 安全验证 (模式 5 子模块)
└── 无参数 / 无法识别    → 提示用户选择模式
```

### 模式详细规范索引

> 各模式的完整工作流程、检查点、异常处理已抽取为独立文件。

**phases/ 文件**（7 个模式详细规范）：

| 模式 | 文件 | 说明 |
|------|------|------|
| #1 标准校准 | `phases/mode1-standard-calibration.md` | 4-Phase 工作流 + 金标准格式 + 异常处理 + 引擎调用 |
| #2 状态查看 | `phases/mode2-status.md` | 校准数据库摘要展示格式 |
| #3 增量更新 | `phases/mode3-incremental-update.md` | correction.json 格式 + 处理流程 |
| #4 门闸校验 | `phases/mode4-gate-check.md` | 门闸阈值表 + 状态判定规则 |
| #5 外部基准 | `phases/mode5-external-bench.md` | StatLLM 四任务 + MedHELM 全维度 + RWE 安全验证 + 禁忌 |
| #6 复现验证 | `phases/mode6-replicate.md` | 5-Phase R1-R5 工作流 + 差异判定 + 异常处理 |
| #7 公平性校准 | `phases/mode7-fairness.md` | 5 维度偏见检测 + MSF/ESF/CC 指标 + Pipeline 联动 |

**shared/calibration/ 文件**（共享协议与模板）：

| 文件 | 说明 |
|------|------|
| `shared/calibration/calibration_protocol.md` | 与 Pipeline 集成 + QC Inspector 反馈 + 门闸动态阈值 + Anti-Pattern 验证 |
| `shared/calibration/calibration_report_template.md` | 校准报告 Markdown 模板 + 工具引用 + 校准指标公式表 |
| `shared/calibration/self_validation.md` | 校准系统自校验（3 项自检：已知答案/完全错误/随机基线） |
| `shared/calibration/data_accumulation.md` | 真实校准数据积累机制 + 纠正触发条件 + 质量控制 |
| `shared/calibration/gate_linkage_rules.md` | 门闸联动详细规则 + 伪代码 + 分方法类型判定 |

## 反例与黑名单

> 校准反例与黑名单（金标准禁忌 #1-4 + 校准执行禁忌 #5-7 + 门闸联动禁忌 #8-9 + 外部基准禁忌 + 公平性禁忌）见各模式 phases 文件的"禁忌"小节，以及 [shared/anti-patterns/medical_stats_anti_patterns.md](../../shared/anti-patterns/medical_stats_anti_patterns.md)。

## 检查点量化标准

| 模式 | 检查点类型 | 通过标准 | 阻断标准 | 升级条件 |
|------|-----------|---------|---------|---------|
| standard | 校准结果 | 方法匹配率≥90% + 数值偏差<5% | 方法匹配率<80% 或 数值偏差>10% | 偏差>10% → 阻断Pipeline，必须退回analysis-exec重新分析 |
| status | 状态查询 | 数据库存在且有记录 | 数据库为空 | 空库 → 返回UNCALIBRATED |
| update | 数据库更新 | 新记录写入成功 | 写入冲突/格式错误 | 冲突3次 → [DB_LOCKED] |
| gate-check | 门闸校验 | 全部检查项PASS | 任何CRITICAL项FAIL | FAIL → 阻断Pipeline |
| replicate | 复现验证 | 数值差异<1% + 方法一致 | 数值差异>5% 或 方法不一致 | 差异>5% → 标记[REPLICATION_FAILED] |
| fairness | 公平性校准 | MSF<0.05 + ESF<0.10 | MSF>0.10 或 ESF>0.20 | MSF>0.10 → 标记[UNFAIR] |
| external-bench | 外部基准 | 4任务全PASS | 任何任务FAIL | 2+任务FAIL → [BENCHMARK_FAILED] |

> **升级规则**: 任何阻断标准触发时，自动升级为[MANDATORY]检查点，必须用户确认后才能继续。
> **降级规则**: [SLIM]检查点在无异常时自动继续，仅记录摘要。

## 边缘场景与异常处理

| 场景 | 触发条件 | 降级策略 | 标记 |
|------|---------|---------|------|
| 公平性校准亚组样本不足 | subgroup 样本量 < 30 | 回退到聚合校准，标注亚组不可评估 | ⚠️ [SUBGROUP_INSUFFICIENT] |
| 外部基准 API 不可用 | StatLLM/MedHELM 等外部 API 超时或不可达 | 回退到本地验证数据集，仅报告本地基准结果 | [DEGRADED] |
| 复现验证原始代码缺失 | 论文未提供可执行原始代码 | 仅对比论文报告值与 MSRA 独立结果，不编造复现结果 | [CANNOT_VERIFY] |
| 门闸校验数据库为空 | calibration_db.json 不存在或为空 | 自动通过门闸，标注为首次运行 | [FIRST_RUN] |
| 状态模式无历史数据 | 无任何校准记录 | 返回 "UNCALIBRATED" 状态，提示用户运行首次校准 | [UNCALIBRATED] |
| 增量更新结果冲突 | 新校准记录与已有记录结论矛盾 | 保留最新记录，归档冲突的旧记录并附时间戳 | [CONFLICT_ARCHIVED] |

---

> **核心禁令**：见各模式 phases 文件的"禁忌"小节（金标准禁忌 #1-4 + 校准执行禁忌 #5-7 + 门闸联动禁忌 #8-9 + 外部基准禁忌 §7g #1-5 + 公平性禁忌 §6f #1-5）。额外规则：校准数据库必须加密存储（calibration_db.json），复现验证不得修改原始代码。
