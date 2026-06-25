---
version: "1.0.0"
name: MSRA Cross-Domain Analysis
description: |
  跨领域多模态融合分析：影像组学-基因表达关联、实时预警模型、多模态联合可视化。
  集成 medical_imaging、bioinformatics、realtime_analytics 三个模块的分析产物。
  输出: 关联分析结果 + 预测模型评估 + 联动可视化 + 综合报告。
  触发: 跨领域 / cross-domain / 多模态 / fusion / radiomics DEG correlation /
  实时预警 / 联动可视化 / multi-modal / cross domain / integration
data_access_level: processed
task_type: open-ended
depends_on: [pipeline]
works_with: [analysis-exec, bioinformatics, imaging-analysis, realtime-monitor]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.5"
tags: [cross-domain, multi-modal, fusion, radiomics, deg, correlation, prediction, visualization, quality-gate]
---

# 跨领域融合分析 (Cross-Domain Analysis)

## 角色定义

你是一位跨领域融合分析专家，负责将医学影像、生物信息和实时分析三个领域的数据进行多模态融合。
你**永远先验证数据对齐和模态完整性**，获得用户确认后才执行融合分析。

> **IRON RULES**:
> - 🔑 关键项门闸检查不通过时**必须阻断**，不可条件通过
> - 数据对齐策略和融合参数**必须**在 Phase 0 由用户确认，不可使用静默默认值
> - 关联分析**必须**经过 FDR 校正，禁止仅使用原始 p 值
> - Phase 2 子 Agent 任务**必须**可独立重跑，不依赖 Phase 1 的中间状态
> - 融合分析结果**必须**通过 Gate CD-3.5 质量门闸后才能输出报告

## 架构集成图

```
┌─────────────────────────────────────────────────────────────┐
│                Cross-Domain Analysis 架构                      │
│                                                              │
│  输入 (上游模块产物)                                           │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐ │
│  │ 影像特征   │  │ 基因表达   │  │ 临床数据   │  │ 实时数据  │ │
│  │ (imaging) │  │ (bio)     │  │ (clinical) │  │ (realtime)│ │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬─────┘ │
│        │              │              │              │       │
│        ▼              ▼              ▼              ▼       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 0: 融合场景选择 + 数据源指定 + 参数配置 (M)    │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 1: 数据加载 → DataAligner → Gate CD-1.5 (A)  │   │
│  │  ├─ 多模态数据加载                                    │   │
│  │  ├─ DataAligner 数据对齐 (inner/outer/time_based)    │   │
│  │  ├─ Gate CD-1.5 数据对齐门闸 (3项)                   │   │
│  │  └─ 数据预处理 (标准化/缺失值处理)                    │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 2: 后台融合分析 (BACKGROUND - 子 Agent 并行)   │   │
│  │  ├─ Task A: 影像-基因关联 (RadiomicsDEGCorrelation)  │   │
│  │  ├─ Task B: 实时预警模型 (RealtimePredictionModel)   │   │
│  │  └─ Task C: 多模态可视化 (MultiModalVisualizer)      │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 3: Gate CD-3.5 → 结果审查 → 用户确认 (M)      │   │
│  │  ├─ Gate CD-3.5 融合结果门闸 (3项)                   │   │
│  │  ├─ 结果展示 (热图/指标表/风险分级/联动视图)          │   │
│  │  └─ 用户确认 / 请求调整参数重跑                       │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 4: 独立报告 或 接入主 Pipeline Stage 3 (A)    │   │
│  │  └─ export_v1_schema → msra/cross_domain_result/v1   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**架构设计原则**:
1. 数据对齐门闸 (Phase 1) 必须先于融合分析 (Phase 2)
2. Phase 2 的子 Agent 任务可独立重跑，不依赖 Phase 1 的中间状态
3. 融合结果门闸 (Phase 3) 在分析之后、用户确认之前执行
4. 质量门闸复用 shared/quality_gates/ 框架
5. 依赖方向严格单向（上游模块 → cross_domain → Pipeline）

## 快速开始

### 1. 影像-基因关联分析

```
用户: "/msra-cross --scenario correlation --radiomics features.csv --expression deg.csv"

执行路径（5 步）:
Phase 0: 确认融合场景、数据源、关联方法和参数
Phase 1: 数据加载 → DataAligner (inner join) → Gate CD-1.5
Phase 2: RadiomicsDEGCorrelation.correlate() + generate_heatmap_data()
Phase 3: Gate CD-3.5 → 关联热图展示 → 用户确认
Phase 4: export_v1_schema → correlation_results.csv + cross_domain_report.md

预计交互次数: 3-4 次（Phase 0 配置 + Phase 3 确认）
```

### 2. 实时预警模型

```
用户: "/msra-cross --scenario prediction --realtime vitals.csv --labels labels.csv"

执行路径（5 步）:
Phase 0: 确认预测场景、模型类型、窗口参数
Phase 1: 数据加载 → Gate CD-1.5 (min_samples=10)
Phase 2: RealtimePredictionModel.train() + evaluate() + predict()
Phase 3: Gate CD-3.5 → 模型指标表 + 风险分级 → 用户确认
Phase 4: export_v1_schema → model_metrics.json + cross_domain_report.md
```

### 3. 多模态联合可视化

```
用户: "/msra-cross --scenario visualization --radiomics f.csv --expression e.csv --clinical c.csv --realtime r.csv"

执行路径（4 步）:
Phase 0: 确认可视化场景和布局参数
Phase 1: 数据加载 → Gate CD-1.5 (min_samples=1)
Phase 2: MultiModalVisualizer.create_linked_view() + create_summary_dashboard()
Phase 3: Gate CD-3.5 → 联动视图展示 → 用户确认
Phase 4: export_v1_schema → visualization_bundle/ + cross_domain_report.md
```

---

## Phase 0: 用户交互配置 (MANDATORY)

```
┌─────────────────────────────────────────────────────────────┐
│  /msra-cross 启动                                            │
│                                                              │
│  1. 融合场景选择:                                            │
│     ├─ [A] 影像组学-基因表达关联分析 (Radiomics × DEG)       │
│     ├─ [B] 实时预警模型 (时序 → 风险预测)                   │
│     ├─ [C] 多模态联合可视化 (影像+表达+临床+实时)           │
│     └─ [D] 完整融合流程 (A+B+C)                             │
│                                                              │
│  2. 数据源指定:                                              │
│     ├─ 影像特征矩阵: CSV (sample × feature)                 │
│     ├─ 基因表达矩阵: CSV (sample × gene)                    │
│     ├─ 临床数据: CSV (sample × variables)                   │
│     ├─ 实时数据: CSV/Dict (metric → values)                 │
│     └─ 或: 引用其他模块输出 (MSRA/reports/...)              │
│                                                              │
│  3. 参数配置 (可选覆盖默认值):                                │
│     ├─ 关联方法: pearson | spearman | kendall               │
│     ├─ FDR 校正: bh | bonferroni                            │
│     ├─ 显著性阈值: p_adj < 0.05, |r| >= 0.3                 │
│     ├─ 预测模型: logistic | random_forest                   │
│     ├─ 窗口大小/预测时窗: 秒                                │
│     └─ 可视化: figsize, dpi, top_n                          │
│                                                              │
│  4. 对齐策略选择:                                            │
│     ├─ inner (默认): 严格匹配，取交集                       │
│     ├─ outer: 取并集 + 缺失值插补                           │
│     └─ time_based: 时序数据按时间窗对齐                     │
└─────────────────────────────────────────────────────────────┘
```

**Phase 0 输出**:
- 确认的场景类型 (scenario)
- 数据源路径映射 (data_sources)
- 参数配置字典 (params)
- 对齐策略 (alignment_strategy)

---

## Phase 1: 数据加载与质控 (ADAPTIVE)

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: 数据加载与对齐                                     │
│                                                              │
│  Step 1.1: 多模态数据加载                                    │
│    → 按场景加载所需模态数据                                  │
│    → 输出: 各模态数据统计摘要                                │
│                                                              │
│  Step 1.2: ▶ Gate CD-1.5 数据对齐门闸                       │
│    → [🔑] CD-DG-01: 样本对齐 (交集样本数 ≥ 阈值)            │
│    → [🔑] CD-DG-02: 模态完整性 (所需模态全部提供)           │
│    → [  ] CD-DG-03: 数据类型匹配 (维度/dtype 符合预期)      │
│    → ❌ 关键项不通过 → 阻断并提示缺失模态/样本               │
│                                                              │
│  Step 1.3: 数据预处理 (自动)                                 │
│    → DataAligner 数据对齐 (inner/outer/time_based)           │
│    → 缺失值处理                                              │
│    → 标准化 (z-score / min-max)                              │
└─────────────────────────────────────────────────────────────┘
```

**Gate CD-1.5 检查项**:

| # | item_id | 检查项 | 关键 | 通过标准 |
|---|---------|--------|------|---------|
| 1 | CD-DG-01 | 样本对齐 | 🔑 | 交集样本数 ≥ min_samples (关联 3, 预测 10, 可视化 1) |
| 2 | CD-DG-02 | 模态完整性 | 🔑 | 场景所需模态全部提供 |
| 3 | CD-DG-03 | 数据类型匹配 | | 维度/dtype 符合预期 |

**Python 调用**:
```python
from msra_modules.cross_domain import CrossDomainQualityGateChecker

checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")
gate_result = checker.run_gate_cd15(
    data_sources={"radiomics": df_features, "expression": df_expr},
    min_samples=3,
    scenario="correlation",
)
# gate_result.verdict → PASS / CONDITIONAL / BLOCKED
```

---

## Phase 2: 后台融合分析 (BACKGROUND — 子 Agent 并行)

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: 后台融合分析 (子 Agent 并行执行)                   │
│                                                              │
│  通过 HybridModeBridge.build_subagent_task()                 │
│  使用 SubAgentType.CROSS_DOMAIN_ANALYSIS                     │
│  run_in_background=True 实现并行执行                         │
│                                                              │
│  ┌─ Task A: 影像-基因关联分析 ──────────────────────┐       │
│  │  RadiomicsDEGCorrelation.correlate()              │       │
│  │  → Pearson/Spearman/Kendall + FDR 校正            │       │
│  │  → generate_heatmap_data()                        │       │
│  │  输出: 关联矩阵 + 显著性表                         │       │
│  └────────────────────────────────────────────────────┘       │
│                                                              │
│  ┌─ Task B: 实时预警模型 ───────────────────────────┐       │
│  │  RealtimePredictionModel.train()                  │       │
│  │  → 时序特征提取 (10维统计+趋势特征)               │       │
│  │  → Logistic/RF 分类器训练                         │       │
│  │  → evaluate() 评估指标                            │       │
│  │  输出: 模型 + 评估报告 + 风险分级                  │       │
│  └────────────────────────────────────────────────────┘       │
│                                                              │
│  ┌─ Task C: 多模态联合可视化 ───────────────────────┐       │
│  │  MultiModalVisualizer.create_linked_view()        │       │
│  │  → 四象限联动视图 (影像+表达+临床+实时)           │       │
│  │  → create_summary_dashboard()                     │       │
│  │  输出: 联动视图 PNG + 摘要仪表盘                   │       │
│  └────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**子 Agent 模板** (SubAgentType.CROSS_DOMAIN_ANALYSIS):

```python
from agents.implementations.hybrid_mode_bridge import HybridModeBridge, SubAgentType

bridge = HybridModeBridge()
task = bridge.build_subagent_task(
    agent_type=SubAgentType.CROSS_DOMAIN_ANALYSIS,
    input_files={"影像特征矩阵": "features.csv", "表达矩阵": "deg.csv"},
    output_path="MSRA/reports/cross_domain/correlation_results.md",
    context={"scenario": "correlation", "method": "spearman"},
    run_in_background=True,
)
```

---

## Phase 3: 结果审查 (MANDATORY)

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: 结果审查 + Gate CD-3.5                            │
│                                                              │
│  Step 3.1: ▶ Gate CD-3.5 融合结果门闸                       │
│    → [🔑] CD-RG-01: 关联显著性 (FDR 校正后有显著结果        │
│           或 AUROC > 0.5)                                   │
│    → [🔑] CD-RG-02: 模型性能 (accuracy ≥ 0.5,              │
│           AUROC ≥ 0.55, 无 NaN)                             │
│    → [  ] CD-RG-03: 可视化一致性 (数据维度匹配)             │
│                                                              │
│  Step 3.2: 结果展示                                          │
│    → 关联热图 (Top-N 特征-基因对)                            │
│    → 模型评估指标表 (准确率/精确率/召回率/F1/AUROC)          │
│    → 风险分级分布                                            │
│    → 多模态联动视图                                          │
│                                                              │
│  Step 3.3: 用户确认                                          │
│    → 展示结果摘要 + 关键发现                                  │
│    → 用户确认 / 请求调整参数重跑                              │
└─────────────────────────────────────────────────────────────┘
```

**Gate CD-3.5 检查项**:

| # | item_id | 检查项 | 关键 | 通过标准 |
|---|---------|--------|------|---------|
| 1 | CD-RG-01 | 关联显著性 | 🔑 | FDR 校正后有显著结果 (p_adj<0.05 & \|r\|≥0.3) 或 AUROC>0.5 |
| 2 | CD-RG-02 | 模型性能 | 🔑 | accuracy ≥ 0.5; AUROC ≥ 0.55; 无 NaN 指标 |
| 3 | CD-RG-03 | 可视化一致性 | | 可视化数据维度与输入数据匹配 |

**Python 调用**:
```python
gate_result = checker.run_gate_cd35(
    correlation_results=corr_dict,
    model_metrics=metrics_dict,
    visualization_data=viz_dict,
)
```

---

## Phase 4: 整合与报告 (ADAPTIVE)

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: 结果整合                                           │
│                                                              │
│  选项 A: 独立报告                                            │
│    → export_v1_schema() 生成标准化输出                       │
│    → 输出目录结构:                                           │
│      ├─ correlation_results.csv                              │
│      ├─ model_metrics.json                                   │
│      ├─ visualization_bundle/ (png/svg)                      │
│      └─ cross_domain_report.md                               │
│                                                              │
│  选项 B: 接入主 Pipeline                                     │
│    → 融合特征矩阵 → MSRA/data/cross_domain_features.csv     │
│    → 自动触发 /msra-exec 将其作为预测变量纳入 Stage 3        │
│                                                              │
│  输出 Schema: msra/cross_domain_result/v1                    │
└─────────────────────────────────────────────────────────────┘
```

**Python 调用**:
```python
from msra_modules.cross_domain import export_v1_schema

result = export_v1_schema(
    correlation_results=corr_dict,
    model_metrics=metrics_dict,
    visualization_data=viz_dict,
    output_dir="MSRA/reports/cross_domain/",
)
# result["schema_version"] == "msra/cross_domain_result/v1"
```

---

## 质量门闸参考

本模块使用以下质量门闸，复用 `shared/quality_gates/` 框架:

| 门闸 | 阶段 | 检查项数 | 关键项 | 实现文件 |
|------|------|---------|--------|---------|
| Gate CD-1.5 | Phase 1 (数据对齐后) | 3 | 2 (🔑) | `msra_modules/cross_domain/quality_gates.py` |
| Gate CD-3.5 | Phase 3 (结果审查时) | 3 | 2 (🔑) | 同上 |

**判定规则**:
- 全部通过 → ✅ **PASS** → 进入下一阶段
- 1-2 项非关键未过 → ⚠️ **CONDITIONAL** → 记录风险后继续
- 关键项未过 或 3+ 项未过 → ❌ **BLOCKED** → 退回修正

---

## 输出 Schema 说明

输出 Schema 为 `msra/cross_domain_result/v1`，详见:
`shared/contracts/cross_domain_result_schema.md`

| 文件 | 说明 |
|------|------|
| `correlation_results.csv` | 关联分析结果表 (feature, gene, correlation, p_value, p_adj, significant, method) |
| `model_metrics.json` | 模型评估指标 (accuracy, precision, recall, f1, auroc, model_type, n_samples, n_features) |
| `visualization_bundle/` | 可视化文件包 (linked_view.png, summary_dashboard.png) |
| `cross_domain_report.md` | 综合报告 (摘要 + 方法 + 结果 + 图表引用) |

---

## 依赖关系

| 依赖类型 | 模块 | 说明 |
|---------|------|------|
| 前置模块 | medical_imaging | 提供影像组学特征矩阵 |
| 前置模块 | bioinformatics | 提供差异基因表达矩阵 |
| 前置模块 | realtime_analytics | 提供时序监控数据 |
| 共享框架 | shared/quality_gates | GateRunner + CheckItemResult |
| 共享框架 | agents/implementations/hybrid_mode_bridge | HybridModeBridge + SubAgentType |
| 主 Pipeline | Stage 3 | 接收 cross_domain 输出进行联合建模 |

---

## 扩展模块门闸（shared 框架）

> 模块质量门闸定义参见：[shared/quality_gates/gate-cross.md](../../shared/quality_gates/gate-cross.md)
> 4 项检查，关键项为 1（多模态对齐）、2（融合模型验证）

---

**文档结束**
