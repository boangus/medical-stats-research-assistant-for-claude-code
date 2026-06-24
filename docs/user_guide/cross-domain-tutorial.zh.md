# MSRA 跨领域融合模块用户教程

> **模块版本**: v1.0.0 | **文档日期**: 2026-06-25 | **状态**: Stable
> **命令入口**: `/msra-cross` | **适用 MSRA 版本**: v1.0.0+

---

## 1. 模块简介与适用场景

### 模块概述

MSRA Cross-Domain（跨领域融合）模块是 MSRA v1.0.0 的核心融合引擎，将 medical_imaging（影像组学）、bioinformatics（基因表达）、realtime_analytics（实时监控）三个模块的分析结果进行跨模态融合分析，提供单模块无法发现的跨域关联模式。

### 核心能力

| 能力 | 说明 |
|------|------|
| 影像-基因关联 | 放射组学特征与差异基因表达的相关性分析，`RadiomicsDEGCorrelation` |
| 实时预警模型 | 基于时序数据训练风险预测模型，`RealtimePredictionModel` |
| 多模态可视化 | 影像+表达+临床+实时四象限联动视图，`MultiModalVisualizer` |
| 数据对齐 | 多策略样本对齐（inner/outer/time_based），`DataAligner` |
| Schema 导出 | `msra/cross_domain_result/v1` 标准格式，`export_v1_schema` |
| 质量门闸 | Gate CD-1.5（数据对齐）+ Gate CD-3.5（融合结果），`CrossDomainQualityGateChecker` |

### 适用场景

- 影像表型与分子特征的关联分析（放射组学 × 基因表达）
- 基于生命体征时序数据的临床恶化预警建模
- 多模态数据（影像+基因+临床+实时）的联合可视化与探索
- 融合特征矩阵导出供主 Pipeline 进行联合统计建模

---

## 2. 安装依赖

### 安装 cross_domain 扩展依赖

```bash
pip install -e ".[cross_domain]"
```

### 核心依赖列表

```toml
scipy >= 1.10           # 统计分析（相关性计算）
scikit-learn >= 1.3     # 机器学习（预测模型）
numpy >= 1.24           # 数值计算
pandas >= 2.0           # 数据处理
matplotlib >= 3.7       # 可视化
```

### 验证安装

```bash
python -c "from msra_modules.cross_domain import RadiomicsDEGCorrelation, RealtimePredictionModel, MultiModalVisualizer, DataAligner, CrossDomainQualityGateChecker, export_v1_schema; print('OK')"
```

---

## 3. 前置条件

### 依赖的上游模块输出

Cross-Domain 模块**不直接处理原始数据**，而是消费其他三个模块的分析产物：

| 数据类型 | 来源模块 | 输出格式 | 典型路径 |
|---------|---------|---------|---------|
| 影像组学特征矩阵 | `/msra-imaging` | CSV (sample × feature) | `MSRA/data/imaging_features_v1.csv` |
| 差异基因表达矩阵 | `/msra-bio` | CSV (sample × gene) | `MSRA/data/bio_covariates.csv` |
| 时序监控数据 | `/msra-rt` | CSV / Dict (metric → values) | `MSRA/reports/rt_monitoring_*.html` |
| 临床数据 | 用户提供 | CSV (sample × variables) | 自定义 |

### 数据格式要求

所有 DataFrame 的 **index 必须为样本 ID**，用于跨模态对齐：

```python
# 影像特征矩阵示例
#                    feature_glcm_contrast  feature_shape_volume  ...
# patient_001                      12.5                4500.0
# patient_002                      15.3                5200.0
# patient_003                       8.7                3800.0

# 基因表达矩阵示例
#                    Gene_TP53  Gene_BRCA1  Gene_EGFR  ...
# patient_001            2.3         1.8       0.5
# patient_002            1.1         3.2       2.1
# patient_003            0.8         1.5       0.3
```

### 示例：准备模拟数据

```python
import pandas as pd
import numpy as np

np.random.seed(42)
samples = [f"patient_{i:03d}" for i in range(20)]

# 模拟影像特征 (20 样本 × 5 特征)
radiomics_df = pd.DataFrame(
    np.random.randn(20, 5),
    index=samples,
    columns=["glcm_contrast", "shape_volume", "firstorder_mean", "glrlm_lre", "glszm_zs"]
)
radiomics_df.to_csv("mock_radiomics.csv")

# 模拟基因表达 (20 样本 × 8 基因)
genes = [f"Gene_{g}" for g in ["TP53", "BRCA1", "EGFR", "KRAS", "PTEN", "MYC", "RB1", "APC"]]
expression_df = pd.DataFrame(
    np.random.randn(20, 8),
    index=samples,
    columns=genes,
)
expression_df.to_csv("mock_expression.csv")
```

---

## 4. 场景A: 影像-基因关联分析

### 命令启动

```
/msra-cross --scenario correlation --radiomics features.csv --expression deg.csv
```

### Python API 完整流程

```python
import pandas as pd
from msra_modules.cross_domain import (
    RadiomicsDEGCorrelation, DataAligner,
    CrossDomainQualityGateChecker,
)

# Phase 0: 加载数据
radiomics_df = pd.read_csv("mock_radiomics.csv", index_col=0)
expression_df = pd.read_csv("mock_expression.csv", index_col=0)

# Phase 1: 数据对齐 + Gate CD-1.5
aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": radiomics_df,
    "expression": expression_df,
})
print(f"Aligned samples: {len(aligned['radiomics'])}")

# Gate CD-1.5
checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")
gate_15 = checker.run_gate_cd15(
    data_sources=aligned,
    min_samples=3,
    scenario="correlation",
)
print(f"Gate CD-1.5: {gate_15.verdict}")

# Phase 2: 关联分析
correlator = RadiomicsDEGCorrelation(
    correlation_method="spearman",  # pearson | spearman | kendall
    pval_threshold=0.05,
    fdr_method="bh",                # bh | bonferroni
)

results = correlator.correlate(
    radiomics_features=aligned["radiomics"],
    deg_expression=aligned["expression"],
)

print(f"Total pairs: {results['n_total']}")
print(f"Significant pairs (p_adj<0.05 & |r|>=0.3): {results['n_significant']}")

# 查看显著的关联
corr_df = results["correlations"]
significant = corr_df[corr_df["significant"]].sort_values("p_adj")
print(significant[["feature", "gene", "correlation", "p_adj"]].head(10))

# 生成热图数据
heatmap_data = correlator.generate_heatmap_data(corr_df, top_n=20)
print(f"Heatmap features: {len(heatmap_data['features'])}")
print(f"Heatmap genes: {len(heatmap_data['genes'])}")
```

### Phase 3: Gate CD-3.5 + 结果审查

```python
# Gate CD-3.5
gate_35 = checker.run_gate_cd35(
    correlation_results=results,
)
print(f"Gate CD-3.5: {gate_35.verdict}")
```

### 关联热图解读

热图展示了放射组学特征（行）与差异基因（列）之间的相关系数：
- **红色**: 正相关（特征值高时基因表达也高）
- **蓝色**: 负相关（特征值高时基因表达低）
- **颜色深度**: 相关系数绝对值大小
- **星号标记**: FDR 校正后显著的关联对（p_adj < 0.05 且 |r| ≥ 0.3）

---

## 5. 场景B: 实时预警模型

### 命令启动

```
/msra-cross --scenario prediction --realtime vitals.csv --labels labels.csv
```

### Python API 完整流程

```python
import pandas as pd
import numpy as np
from msra_modules.cross_domain import (
    RealtimePredictionModel, CrossDomainQualityGateChecker,
)

# Phase 0: 加载数据
# historical_data: 每行一个样本的时间序列特征
# labels: 0=正常, 1=恶化
historical_data = pd.read_csv("vitals_history.csv", index_col=0)
labels = pd.read_csv("labels.csv")["label"].values

# Phase 1: Gate CD-1.5 (min_samples=10 for prediction)
checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")
gate_15 = checker.run_gate_cd15(
    data_sources={"realtime": historical_data, "labels": pd.Series(labels)},
    min_samples=10,
    scenario="prediction",
)
print(f"Gate CD-1.5: {gate_15.verdict}")

# Phase 2: 训练预测模型
model = RealtimePredictionModel(
    window_size=60,           # 特征窗口大小（秒）
    prediction_horizon=30,    # 预测时间窗（秒）
    model_type="logistic",    # logistic | random_forest
)

model.train(historical_data, labels)

# 评估模型
X_test = historical_data.values  # 实际应使用独立的测试集
y_test = labels
metrics = model.evaluate(X_test, y_test)

print(f"Accuracy:  {metrics['accuracy']:.4f}")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall:    {metrics['recall']:.4f}")
print(f"F1:        {metrics['f1']:.4f}")
print(f"AUROC:     {metrics['auroc']:.4f}")

# 实时预测
current_vitals = [72, 75, 78, 80, 85, 90, 95, 100, 105, 110]  # 最近 10 个数据点
prediction = model.predict(current_vitals)

print(f"Prediction: {prediction['prediction']}")
print(f"Probability: {prediction['probability']:.4f}")
print(f"Risk level: {prediction['risk_level']}")
# risk_level: "minimal" (<0.3) | "low" (0.3-0.5) | "medium" (0.5-0.8) | "high" (>=0.8)
```

### Phase 3: Gate CD-3.5

```python
gate_35 = checker.run_gate_cd35(
    model_metrics=metrics,
)
print(f"Gate CD-3.5: {gate_35.verdict}")
```

### 风险分级说明

| 风险等级 | 概率范围 | 建议行动 |
|---------|---------|---------|
| high | ≥ 0.8 | 立即干预 |
| medium | 0.5 - 0.8 | 密切监护 |
| low | 0.3 - 0.5 | 加强观察 |
| minimal | < 0.3 | 常规监护 |

---

## 6. 场景C: 多模态联合可视化

### 命令启动

```
/msra-cross --scenario visualization --radiomics f.csv --expression e.csv --clinical c.csv --realtime r.csv
```

### Python API 完整流程

```python
import pandas as pd
import numpy as np
from msra_modules.cross_domain import (
    MultiModalVisualizer, DataAligner,
    CrossDomainQualityGateChecker,
)

# Phase 0: 加载多模态数据
radiomics_df = pd.read_csv("mock_radiomics.csv", index_col=0)
expression_df = pd.read_csv("mock_expression.csv", index_col=0)
clinical_df = pd.read_csv("clinical_data.csv", index_col=0)
realtime_data = {
    "heart_rate": [72, 75, 78, 80, 85, 90, 88, 85, 82, 80],
    "spo2": [98, 97, 97, 96, 95, 93, 94, 95, 96, 97],
}
imaging_volume = np.random.randn(64, 64, 32)  # 模拟影像数据

# Phase 1: 数据对齐 + Gate CD-1.5
aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": radiomics_df,
    "expression": expression_df,
    "clinical": clinical_df,
})

checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")
gate_15 = checker.run_gate_cd15(
    data_sources=aligned,
    min_samples=1,  # 可视化场景最低 1 个样本
    scenario="visualization",
)
print(f"Gate CD-1.5: {gate_15.verdict}")

# Phase 2: 生成联动视图
visualizer = MultiModalVisualizer(figsize=(16, 10), dpi=100)

# 四象限联动视图
fig = visualizer.create_linked_view(
    imaging_data=imaging_volume,
    imaging_mask=None,
    expression_data=aligned["expression"],
    clinical_data=aligned["clinical"],
    realtime_data=realtime_data,
    save_path="linked_view.png",
)
print("Linked view saved to: linked_view.png")

# 摘要仪表盘
dashboard_fig = visualizer.create_summary_dashboard(
    data_sources={
        "Radiomics": aligned["radiomics"],
        "Expression": aligned["expression"],
        "Clinical": aligned["clinical"],
        "Realtime": realtime_data,
    },
    save_path="summary_dashboard.png",
)
print("Summary dashboard saved to: summary_dashboard.png")

# Phase 3: Gate CD-3.5
gate_35 = checker.run_gate_cd35(
    visualization_data={
        "linked_view": "linked_view.png",
        "summary_dashboard": "summary_dashboard.png",
    },
)
print(f"Gate CD-3.5: {gate_35.verdict}")
```

### 联动视图布局

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   Medical Imaging   │  Gene Expression    │
│   (影像切片+掩码)    │  (表达热图)          │
│                     │                     │
├─────────────────────┼─────────────────────┤
│                     │                     │
│  Clinical Data      │  Real-time          │
│  (临床指标箱线图)     │  Monitoring         │
│                     │  (实时监测曲线)       │
│                     │                     │
└─────────────────────┴─────────────────────┘
```

---

## 7. 质量门闸说明

### Gate CD-1.5 — 数据对齐门闸

> 位于 Phase 1（数据对齐后），阻断不对齐的数据进入融合分析。
> 实现: `msra_modules/cross_domain/quality_gates.py` → `CrossDomainQualityGateChecker`

| # | 检查项 | 关键项 | 通过标准 |
|---|--------|--------|---------|
| 1 | 样本对齐 | 🔑 | 交集样本数 ≥ min_samples（关联: 3, 预测: 10, 可视化: 1） |
| 2 | 模态完整性 | 🔑 | 所选场景所需的模态数据全部提供 |
| 3 | 数据类型匹配 | | 各模态数据的维度/dtype 符合预期 |

**判定规则**:
- **PASS**: 3/3 通过
- **CONDITIONAL**: 1-2 项非关键未通过，记录风险后继续
- **BLOCKED**: 关键项未通过 或 3 项全部未通过（**阻断流程**）

### Gate CD-3.5 — 融合结果门闸

> 位于 Phase 3（结果审查前），验证融合分析结果质量。

| # | 检查项 | 关键项 | 通过标准 |
|---|--------|--------|---------|
| 1 | 关联显著性 | 🔑 | FDR 校正后有显著结果 (p_adj<0.05 & |r|≥0.3) 或 AUROC>0.5 |
| 2 | 模型性能 | 🔑 | accuracy ≥ 0.5; AUROC ≥ 0.55; 无 NaN |
| 3 | 可视化一致性 | | 可视化数据维度与输入数据匹配 |

### Python 调用示例

```python
from msra_modules.cross_domain import CrossDomainQualityGateChecker

checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")

# Gate CD-1.5
gate_15 = checker.run_gate_cd15(
    data_sources={
        "radiomics": radiomics_df,
        "expression": expression_df,
    },
    min_samples=3,
    scenario="correlation",
)
print(f"CD-1.5 verdict: {gate_15.verdict}")
for item in gate_15.items:
    print(f"  [{item.status}] {item.name}: {item.message}")

# Gate CD-3.5
gate_35 = checker.run_gate_cd35(
    correlation_results=corr_results,
    model_metrics=model_metrics,
    visualization_data=viz_data,
)
print(f"CD-3.5 verdict: {gate_35.verdict}")
```

---

## 8. 完整融合流程演示

### 使用所有三个场景的完整流程

```
/msra-cross --scenario full --radiomics features.csv --expression deg.csv --clinical clinical.csv --realtime vitals.csv
```

### Python API 完整融合流程

```python
import pandas as pd
import numpy as np
from msra_modules.cross_domain import (
    RadiomicsDEGCorrelation,
    RealtimePredictionModel,
    MultiModalVisualizer,
    DataAligner,
    CrossDomainQualityGateChecker,
    export_v1_schema,
)

# === Phase 0: 加载所有模态数据 ===
radiomics_df = pd.read_csv("mock_radiomics.csv", index_col=0)
expression_df = pd.read_csv("mock_expression.csv", index_col=0)
clinical_df = pd.read_csv("clinical_data.csv", index_col=0)
realtime_data = {"heart_rate": [72, 75, 78, 80, 85], "spo2": [98, 97, 96, 95, 94]}
labels = np.array([0, 1, 0, 1, 0, 1, 0, 0, 1, 0,
                   0, 1, 0, 1, 0, 0, 1, 0, 1, 0])

# === Phase 1: 数据对齐 + Gate CD-1.5 ===
aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": radiomics_df,
    "expression": expression_df,
})

checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")
gate_15 = checker.run_gate_cd15(
    data_sources=aligned,
    min_samples=3,
    scenario="correlation",
)
assert gate_15.verdict != "BLOCKED", "Gate CD-1.5 blocked!"

# === Phase 2: 三路并行融合分析 ===

# Task A: 影像-基因关联
correlator = RadiomicsDEGCorrelation(
    correlation_method="spearman",
    fdr_method="bh",
)
corr_results = correlator.correlate(
    radiomics_features=aligned["radiomics"],
    deg_expression=aligned["expression"],
)
print(f"[A] Significant correlations: {corr_results['n_significant']}")

# Task B: 实时预警模型
model = RealtimePredictionModel(
    model_type="random_forest",
    window_size=60,
)
model.train(radiomics_df, labels)
metrics = model.evaluate(radiomics_df.values, labels)
print(f"[B] Model AUROC: {metrics['auroc']:.4f}")

# Task C: 多模态可视化
visualizer = MultiModalVisualizer(figsize=(16, 10))
fig = visualizer.create_linked_view(
    expression_data=aligned["expression"],
    clinical_data=clinical_df,
    realtime_data=realtime_data,
    save_path="linked_view.png",
)
print("[C] Linked view saved")

# === Phase 3: Gate CD-3.5 ===
gate_35 = checker.run_gate_cd35(
    correlation_results=corr_results,
    model_metrics=metrics,
    visualization_data={"paths": ["linked_view.png"]},
)
print(f"Gate CD-3.5: {gate_35.verdict}")

# === Phase 4: 导出 v1 Schema ===
result = export_v1_schema(
    correlation_results=corr_results,
    model_metrics=metrics,
    visualization_data={"paths": ["linked_view.png"]},
    output_dir="MSRA/reports/cross_domain/",
)

print(f"\nExport complete:")
print(f"  Schema: {result['schema_version']}")
print(f"  Correlation results: {result['correlation_results']}")
print(f"  Model metrics: {result['model_metrics']}")
print(f"  Visualization bundle: {result['visualization_bundle']}")
print(f"  Report: {result['report']}")
```

---

## 9. 与主 Pipeline 集成

### 导出融合特征矩阵

```python
import pandas as pd

# 将关联分析中的显著特征对组合为融合特征矩阵
fusion_features = pd.DataFrame(index=aligned["radiomics"].index)

# 添加显著的影像-基因关联特征对
for _, row in significant.iterrows():
    feat_name = row["feature"]
    gene_name = row["gene"]
    # 将影像特征和基因表达的乘积作为融合特征
    fusion_features[f"{feat_name}_x_{gene_name}"] = (
        aligned["radiomics"][feat_name] * aligned["expression"][gene_name]
    )

fusion_features.to_csv("MSRA/data/cross_domain_features.csv")
print(f"Cross-domain features: {fusion_features.shape}")
```

### 自动接入主 Pipeline

在 Phase 4 中选择"接入主 Pipeline"选项，系统将：
1. 将融合特征矩阵写入 `MSRA/data/cross_domain_features.csv`
2. 自动触发 `/msra-exec` 将其作为预测变量纳入 Stage 3

### 命令行直接调用

```
/msra-cross --scenario full --radiomics features.csv --expression deg.csv --integrate-pipeline
```

---

## 10. 常见问题 FAQ

### Q1: Gate CD-1.5 样本对齐失败（交集样本 < 3）怎么办？

- 检查各模态数据的 index 是否使用相同的样本 ID 命名规则
- 考虑使用 `outer` 对齐策略（允许缺失值，自动插补）
- 如果确实样本量不足，需要增加数据

```python
aligner = DataAligner(strategy="outer", fill_method="mean")
```

### Q2: 关联分析中没有显著结果怎么办？

- 增加样本量（当前样本数可能不足）
- 尝试不同的相关方法（pearson → spearman → kendall）
- 降低显著性阈值（p_adj < 0.1）
- 检查数据是否已正确标准化

### Q3: 预测模型的 AUROC 接近 0.5 怎么办？

- 特征可能不足：增加时序窗口大小或添加更多指标
- 尝试 `random_forest` 模型（可能比 `logistic` 更适合非线性关系）
- 检查标签是否平衡（0/1 比例差异过大）

### Q4: DataAligner 的 time_based 策略如何使用？

`time_based` 策略适用于时间序列数据，按时间窗口聚合：

```python
aligner = DataAligner(strategy="time_based")
# 窗口大小默认 60 秒，从 Phase 0 参数继承
# 每个 60 秒窗口内的数据取均值进行对齐
```

### Q5: 联动视图中某个象限为空怎么办？

联动视图只显示已提供数据的象限。如果某个模态数据为 `None`，对应象限会自动跳过。确保至少提供 1 个模态数据。

### Q6: export_v1_schema 输出哪些文件？

| 文件 | 说明 |
|------|------|
| `correlation_results.csv` | 关联分析结果表 (feature, gene, correlation, p_value, p_adj, significant, method) |
| `model_metrics.json` | 模型评估指标 (accuracy, precision, recall, f1, auroc, model_type, n_samples, n_features) |
| `visualization_bundle/` | 可视化文件包 (linked_view.png, summary_dashboard.png) |
| `cross_domain_report.md` | 综合报告 (摘要 + 方法 + 结果 + 图表引用) |

### Q7: 四个模块的依赖关系是什么？

```
medical_imaging ──┐
bioinformatics ───┼──→ cross_domain ──→ 主 Pipeline (Stage 3)
realtime_analytics┘
```

cross_domain 模块单向依赖上游三个模块的输出，不产生反向依赖。

---

> **相关文档**: [SKILL.md](../../skills/cross-domain/SKILL.md) | [模块 PRD](../prd/cross-domain-module-prd.md) | [系统设计文档](../system_design_cross_domain.md) | [MSRA 文档主页](../system_design.md)
