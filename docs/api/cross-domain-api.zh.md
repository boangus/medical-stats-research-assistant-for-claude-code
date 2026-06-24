# MSRA Cross-Domain 模块 API 参考

| 字段 | 值 |
|------|-----|
| **模块** | `msra_modules.cross_domain` |
| **版本** | 1.0.0 |
| **日期** | 2026-07-13 |
| **状态** | Released (v1.0.0) |
| **语言** | 中文 |

---

## 概述

Cross-Domain 模块提供医学影像、生物信息和实时分析三大领域的交叉集成功能，包括影像组学-基因表达关联分析、实时预警模型、多模态联动可视化、数据对齐和质量门闸检查。

### 依赖

- `numpy` / `pandas` — 数据处理
- `scipy` — 相关性分析
- `scikit-learn` — Logistic Regression / Random Forest / 模型评估
- `matplotlib` — 可视化

---

## 公开 API

### `RadiomicsDEGCorrelation`

**描述**: 影像组学与差异表达基因关联分析，支持 Pearson / Spearman / Kendall 相关系数和 FDR 校正（Benjamini-Hochberg / Bonferroni）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `correlation_method` | `str` | 否 | `"spearman"` | 相关系数方法（`"pearson"`, `"spearman"`, `"kendall"`） |
| `pval_threshold` | `float` | 否 | `0.05` | p 值阈值 |
| `fdr_method` | `str` | 否 | `"bh"` | FDR 校正方法（`"bh"` 或 `"bonferroni"`） |

**方法**:

#### `correlate(radiomics_features, deg_expression)`

计算影像组学特征与差异基因表达之间的关联。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `radiomics_features` | `pd.DataFrame` | 是 | — | 影像组学特征（样本×特征） |
| `deg_expression` | `pd.DataFrame` | 是 | — | 差异基因表达（样本×基因） |

- **返回值**: `dict` — 含 `correlations` (pd.DataFrame: feature, gene, correlation, p_value, p_adj, significant), `n_significant`, `n_total`, `method`, `samples`
- **异常**: `ValueError`（公共样本数 < 3 或未知方法）
- **示例**:

```python
from msra_modules.cross_domain import RadiomicsDEGCorrelation

analyzer = RadiomicsDEGCorrelation(correlation_method="spearman", pval_threshold=0.05)
result = analyzer.correlate(radiomics_df, expression_df)
print(result["n_significant"], result["n_total"])
```

#### `generate_heatmap_data(correlations, top_n=20)`

生成热图数据。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `correlations` | `pd.DataFrame` | 是 | — | 相关性结果（`correlate` 返回的 `correlations` 字段） |
| `top_n` | `int` | 否 | `20` | 显示前 N 个 |

- **返回值**: `dict` — 含 `features` (list), `genes` (list), `matrix` (list of lists)

---

### `RealtimePredictionModel`

**描述**: 实时预警模型，从时序数据中提取统计特征（均值、标准差、趋势斜率、变异系数等 10 个特征），使用 Logistic Regression 或 Random Forest 进行二分类预测，并输出风险分级。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `window_size` | `int` | 否 | `60` | 特征窗口大小（秒） |
| `prediction_horizon` | `int` | 否 | `30` | 预测时间窗（秒） |
| `model_type` | `str` | 否 | `"logistic"` | 模型类型（`"logistic"` 或 `"random_forest"`） |

**方法**:

#### `train(historical_data, labels)`

训练模型。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `historical_data` | `pd.DataFrame` | 是 | — | 历史数据（每行一个样本） |
| `labels` | `np.ndarray` | 是 | — | 标签（0/1） |

- **异常**: `ValueError`（未知模型类型）、`ImportError`（scikit-learn 未安装）

#### `predict(current_data)`

预测。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `current_data` | `list[float]` | 是 | — | 当前时间序列数据 |

- **返回值**: `dict` — 含 `prediction` (int), `probability` (float), `risk_level` (str: `"high"` / `"medium"` / `"low"` / `"minimal"`), `features` (dict)
- **异常**: `RuntimeError`（模型未训练）

#### `evaluate(X_test, y_test)`

评估模型。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `X_test` | `np.ndarray` | 是 | — | 测试数据 |
| `y_test` | `np.ndarray` | 是 | — | 测试标签 |

- **返回值**: `dict` — 含 `accuracy`, `precision`, `recall`, `f1`, `auroc`
- **示例**:

```python
from msra_modules.cross_domain import RealtimePredictionModel

model = RealtimePredictionModel(window_size=60, model_type="logistic")
model.train(train_df, train_labels)
result = model.predict([75, 76, 74, 80, 85, 90, 120, 160])
print(result["risk_level"], result["probability"])
metrics = model.evaluate(X_test, y_test)
```

---

### `MultiModalVisualizer`

**描述**: 多模态数据联合可视化工具，支持四象限联动视图和摘要仪表盘。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `figsize` | `tuple` | 否 | `(16, 10)` | 图像大小 |
| `dpi` | `int` | 否 | `100` | 分辨率 |

**方法**:

#### `create_linked_view(imaging_data=None, imaging_mask=None, expression_data=None, clinical_data=None, realtime_data=None, save_path=None)`

创建联动视图（四象限：影像、基因表达热图、临床数据箱线图、实时监测趋势图）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `imaging_data` | `np.ndarray` | 否 | `None` | 影像数据 |
| `imaging_mask` | `np.ndarray` | 否 | `None` | 影像掩码 |
| `expression_data` | `pd.DataFrame` | 否 | `None` | 表达数据 |
| `clinical_data` | `pd.DataFrame` | 否 | `None` | 临床数据 |
| `realtime_data` | `dict` | 否 | `None` | 实时数据（metric -> values list） |
| `save_path` | `str` | 否 | `None` | 保存路径 |

- **返回值**: `matplotlib.figure.Figure`
- **异常**: `ValueError`（至少需要一个数据源）

#### `create_summary_dashboard(data_sources, save_path=None)`

创建摘要仪表盘。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `data_sources` | `dict[str, Any]` | 是 | — | 数据源字典（name -> data） |
| `save_path` | `str` | 否 | `None` | 保存路径 |

- **返回值**: `matplotlib.figure.Figure`
- **示例**:

```python
from msra_modules.cross_domain import MultiModalVisualizer

viz = MultiModalVisualizer(figsize=(16, 10))
fig = viz.create_linked_view(
    imaging_data=img_array,
    expression_data=expr_df,
    realtime_data={"heart_rate": [75, 76, 80, 85, 120]},
    save_path="/output/linked_view.png"
)
```

---

### `DataAligner`

**描述**: 多模态数据对齐器，支持三种对齐策略：inner（严格匹配，取交集）、outer（允许缺失，取并集+插补）、time_based（时序数据按时间窗对齐）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `strategy` | `str` | 否 | `"inner"` | 对齐策略（`"inner"`, `"outer"`, `"time_based"`） |
| `fill_method` | `str` | 否 | `"mean"` | 缺失值填充方法（`"mean"`, `"median"`, `"zero"`, `"ffill"`） |

**方法**:

#### `align(data_sources, strategy=None)`

执行数据对齐。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `data_sources` | `dict[str, Any]` | 是 | — | 数据源字典 {name: DataFrame or Dict} |
| `strategy` | `str` | 否 | `None` | 覆盖默认策略 |

- **返回值**: `dict[str, Any]` — 对齐后的数据源字典（所有 DataFrame 具有相同的 index）
- **异常**: `ValueError`（空数据源、inner join 后样本数 < 3、未知策略）
- **示例**:

```python
from msra_modules.cross_domain import DataAligner

aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": radiomics_df,
    "expression": expression_df,
})
# aligned["radiomics"], aligned["expression"] 已对齐到相同样本
```

**异常**: `ValueError`（无效策略或填充方法）

---

### `export_v1_schema(correlation_results=None, model_metrics=None, visualization_data=None, output_dir=".")`

**描述**: 导出 `msra/cross_domain_result/v1` 标准格式。

输出文件结构:
```
output_dir/
├── correlation_results.csv     # 关联分析结果表
├── model_metrics.json           # 模型评估指标
├── visualization_bundle/        # 可视化文件包
│   ├── linked_view.png
│   └── summary_dashboard.png
└── cross_domain_report.md       # 综合报告
```

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `correlation_results` | `dict` | 否 | `None` | `RadiomicsDEGCorrelation.correlate()` 的返回值 |
| `model_metrics` | `dict` | 否 | `None` | `RealtimePredictionModel.evaluate()` 的返回值 |
| `visualization_data` | `dict` | 否 | `None` | 可视化数据（含 `paths` 列表） |
| `output_dir` | `str` | 否 | `"."` | 输出目录 |

- **返回值**: `dict[str, str]` — 文件路径映射，含 `correlation_results`, `model_metrics`, `visualization_bundle`, `report`, `schema_version` (`"msra/cross_domain_result/v1"`)
- **示例**:

```python
from msra_modules.cross_domain import export_v1_schema

paths = export_v1_schema(
    correlation_results=corr_result,
    model_metrics=metrics,
    visualization_data={"paths": ["/output/linked_view.png"]},
    output_dir="/output/cross_domain/"
)
```

---

### `CrossDomainQualityGateChecker`

**描述**: 跨领域融合质量门闸检查器，封装 Gate CD-1.5（数据对齐门闸）和 Gate CD-3.5（融合结果门闸）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `study_id` | `str` | 是 | — | 研究编号 |
| `project_root` | `str` | 否 | `None` | 项目根目录 |

**方法**:

#### `run_gate_cd15(data_sources, min_samples=3, scenario="correlation")`

执行 Gate CD-1.5 全部 3 项检查：样本对齐（交集 ≥ 最小样本数）、模态完整性（场景所需模态全部提供）、数据类型匹配（维度和 dtype 符合预期）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `data_sources` | `dict[str, Any]` | 是 | — | 数据源字典 |
| `min_samples` | `int` | 否 | `3` | 最小样本数 |
| `scenario` | `str` | 否 | `"correlation"` | 场景类型（`"correlation"`, `"prediction"`, `"visualization"`, `"full"`） |

- **返回值**: `GateResult` — 判定结果（`PASS` / `CONDITIONAL` / `BLOCKED`）

#### `run_gate_cd35(correlation_results=None, model_metrics=None, visualization_data=None)`

执行 Gate CD-3.5 全部 3 项检查：关联显著性（FDR 校正后至少 1 对显著或 AUROC > 0.5）、模型性能（准确率 ≥ 0.5; AUROC ≥ 0.55; 无 NaN 指标）、可视化一致性（热图矩阵维度、曲线点数与输入数据匹配）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `correlation_results` | `dict` | 否 | `None` | 关联分析结果 |
| `model_metrics` | `dict` | 否 | `None` | 模型评估指标 |
| `visualization_data` | `dict` | 否 | `None` | 可视化数据 |

- **返回值**: `GateResult`
- **示例**:

```python
from msra_modules.cross_domain import CrossDomainQualityGateChecker

checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")

# Gate CD-1.5
gate_15 = checker.run_gate_cd15(
    data_sources={"radiomics": radiomics_df, "expression": expression_df},
    min_samples=3,
    scenario="correlation",
)

# Gate CD-3.5
gate_35 = checker.run_gate_cd35(
    correlation_results=corr_result,
    model_metrics=metrics,
)
print(gate_15.verdict, gate_35.verdict)
```

---

## 场景所需模态映射

| 场景 | 所需模态 |
|------|---------|
| `correlation` | `radiomics`, `expression` |
| `prediction` | `realtime`, `labels` |
| `visualization` | ≥ 1 个模态 |
| `full` | `radiomics`, `expression`, `realtime`, `labels` |

---

## 完整使用示例

```python
from msra_modules.cross_domain import (
    RadiomicsDEGCorrelation, RealtimePredictionModel,
    MultiModalVisualizer, DataAligner, export_v1_schema,
    CrossDomainQualityGateChecker,
)
import pandas as pd
import numpy as np

# 1. 数据对齐
aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": radiomics_df,
    "expression": expression_df,
})

# 2. 关联分析
analyzer = RadiomicsDEGCorrelation(correlation_method="spearman")
corr_result = analyzer.correlate(aligned["radiomics"], aligned["expression"])

# 3. 实时预警模型
model = RealtimePredictionModel(model_type="logistic")
model.train(train_df, train_labels)
metrics = model.evaluate(X_test, y_test)

# 4. 多模态可视化
viz = MultiModalVisualizer()
fig = viz.create_linked_view(
    imaging_data=img_array,
    expression_data=aligned["expression"],
    realtime_data={"heart_rate": hr_list},
    save_path="/output/linked_view.png"
)

# 5. 导出 v1 Schema
paths = export_v1_schema(
    correlation_results=corr_result,
    model_metrics=metrics,
    visualization_data={"paths": ["/output/linked_view.png"]},
    output_dir="/output/cross_domain/"
)

# 6. 质量门闸
checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")
gate_15 = checker.run_gate_cd15(
    data_sources=aligned, min_samples=3, scenario="correlation"
)
gate_35 = checker.run_gate_cd35(
    correlation_results=corr_result, model_metrics=metrics
)
```
