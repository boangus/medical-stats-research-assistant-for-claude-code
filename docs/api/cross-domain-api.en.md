# MSRA Cross-Domain Module API Reference

| Field | Value |
|-------|-------|
| **Module** | `msra_modules.cross_domain` |
| **Version** | 1.0.0 |
| **Date** | 2026-07-13 |
| **Status** | Released (v1.0.0) |
| **Language** | English |

---

## Overview

The Cross-Domain module provides cross-domain integration across medical imaging, bioinformatics, and real-time analytics, including radiomics-DEG correlation analysis, real-time prediction modeling, multi-modal linked visualization, data alignment, and quality gate checks.

### Dependencies

- `numpy` / `pandas` — Data processing
- `scipy` — Correlation analysis
- `scikit-learn` — Logistic Regression / Random Forest / model evaluation
- `matplotlib` — Visualization

---

## Public API

### `RadiomicsDEGCorrelation`

**Description**: Radiomics and differentially expressed gene (DEG) correlation analysis, supporting Pearson / Spearman / Kendall correlation coefficients with FDR correction (Benjamini-Hochberg / Bonferroni).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `correlation_method` | `str` | No | `"spearman"` | Correlation method (`"pearson"`, `"spearman"`, `"kendall"`) |
| `pval_threshold` | `float` | No | `0.05` | P-value threshold |
| `fdr_method` | `str` | No | `"bh"` | FDR correction method (`"bh"` or `"bonferroni"`) |

**Methods**:

#### `correlate(radiomics_features, deg_expression)`

Compute correlations between radiomics features and DEG expression.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `radiomics_features` | `pd.DataFrame` | Yes | — | Radiomics features (samples x features) |
| `deg_expression` | `pd.DataFrame` | Yes | — | DEG expression (samples x genes) |

- **Returns**: `dict` — contains `correlations` (pd.DataFrame: feature, gene, correlation, p_value, p_adj, significant), `n_significant`, `n_total`, `method`, `samples`
- **Exceptions**: `ValueError` (common samples < 3 or unknown method)
- **Example**:

```python
from msra_modules.cross_domain import RadiomicsDEGCorrelation

analyzer = RadiomicsDEGCorrelation(correlation_method="spearman", pval_threshold=0.05)
result = analyzer.correlate(radiomics_df, expression_df)
print(result["n_significant"], result["n_total"])
```

#### `generate_heatmap_data(correlations, top_n=20)`

Generate heatmap data.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `correlations` | `pd.DataFrame` | Yes | — | Correlation results (the `correlations` field from `correlate()` output) |
| `top_n` | `int` | No | `20` | Number of top correlations to show |

- **Returns**: `dict` — contains `features` (list), `genes` (list), `matrix` (list of lists)

---

### `RealtimePredictionModel`

**Description**: Real-time prediction model that extracts statistical features from time-series data (mean, std, trend slope, CV, etc. — 10 features total), performs binary classification using Logistic Regression or Random Forest, and outputs risk levels.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `window_size` | `int` | No | `60` | Feature window size (seconds) |
| `prediction_horizon` | `int` | No | `30` | Prediction time horizon (seconds) |
| `model_type` | `str` | No | `"logistic"` | Model type (`"logistic"` or `"random_forest"`) |

**Methods**:

#### `train(historical_data, labels)`

Train the model.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `historical_data` | `pd.DataFrame` | Yes | — | Historical data (one sample per row) |
| `labels` | `np.ndarray` | Yes | — | Labels (0/1) |

- **Exceptions**: `ValueError` (unknown model type), `ImportError` (scikit-learn not installed)

#### `predict(current_data)`

Make a prediction.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `current_data` | `list[float]` | Yes | — | Current time-series data |

- **Returns**: `dict` — contains `prediction` (int), `probability` (float), `risk_level` (str: `"high"` / `"medium"` / `"low"` / `"minimal"`), `features` (dict)
- **Exceptions**: `RuntimeError` (model not trained)

#### `evaluate(X_test, y_test)`

Evaluate the model.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `X_test` | `np.ndarray` | Yes | — | Test data |
| `y_test` | `np.ndarray` | Yes | — | Test labels |

- **Returns**: `dict` — contains `accuracy`, `precision`, `recall`, `f1`, `auroc`
- **Example**:

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

**Description**: Multi-modal data linked visualization tool supporting four-quadrant linked views and summary dashboards.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `figsize` | `tuple` | No | `(16, 10)` | Figure size |
| `dpi` | `int` | No | `100` | Resolution |

**Methods**:

#### `create_linked_view(imaging_data=None, imaging_mask=None, expression_data=None, clinical_data=None, realtime_data=None, save_path=None)`

Create a linked view (four quadrants: imaging, gene expression heatmap, clinical data boxplot, real-time monitoring trend).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `imaging_data` | `np.ndarray` | No | `None` | Imaging data |
| `imaging_mask` | `np.ndarray` | No | `None` | Imaging mask |
| `expression_data` | `pd.DataFrame` | No | `None` | Expression data |
| `clinical_data` | `pd.DataFrame` | No | `None` | Clinical data |
| `realtime_data` | `dict` | No | `None` | Real-time data (metric -> values list) |
| `save_path` | `str` | No | `None` | Save path |

- **Returns**: `matplotlib.figure.Figure`
- **Exceptions**: `ValueError` (at least one data source required)

#### `create_summary_dashboard(data_sources, save_path=None)`

Create a summary dashboard.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data_sources` | `dict[str, Any]` | Yes | — | Data source dict (name -> data) |
| `save_path` | `str` | No | `None` | Save path |

- **Returns**: `matplotlib.figure.Figure`
- **Example**:

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

**Description**: Multi-modal data aligner supporting three alignment strategies: inner (strict match, intersection), outer (allow missing, union + imputation), time_based (time-window alignment for time-series data).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `strategy` | `str` | No | `"inner"` | Alignment strategy (`"inner"`, `"outer"`, `"time_based"`) |
| `fill_method` | `str` | No | `"mean"` | Missing value fill method (`"mean"`, `"median"`, `"zero"`, `"ffill"`) |

**Methods**:

#### `align(data_sources, strategy=None)`

Execute data alignment.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data_sources` | `dict[str, Any]` | Yes | — | Data source dict {name: DataFrame or Dict} |
| `strategy` | `str` | No | `None` | Override default strategy |

- **Returns**: `dict[str, Any]` — aligned data source dict (all DataFrames share the same index)
- **Exceptions**: `ValueError` (empty data sources, inner join result < 3 samples, unknown strategy)
- **Example**:

```python
from msra_modules.cross_domain import DataAligner

aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": radiomics_df,
    "expression": expression_df,
})
# aligned["radiomics"], aligned["expression"] are aligned to the same samples
```

**Exceptions**: `ValueError` (invalid strategy or fill method)

---

### `export_v1_schema(correlation_results=None, model_metrics=None, visualization_data=None, output_dir=".")`

**Description**: Export `msra/cross_domain_result/v1` standard format.

Output file structure:
```
output_dir/
├── correlation_results.csv     # Correlation analysis results
├── model_metrics.json           # Model evaluation metrics
├── visualization_bundle/        # Visualization file bundle
│   ├── linked_view.png
│   └── summary_dashboard.png
└── cross_domain_report.md       # Comprehensive report
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `correlation_results` | `dict` | No | `None` | Output of `RadiomicsDEGCorrelation.correlate()` |
| `model_metrics` | `dict` | No | `None` | Output of `RealtimePredictionModel.evaluate()` |
| `visualization_data` | `dict` | No | `None` | Visualization data (containing `paths` list) |
| `output_dir` | `str` | No | `"."` | Output directory |

- **Returns**: `dict[str, str]` — file path mapping, contains `correlation_results`, `model_metrics`, `visualization_bundle`, `report`, `schema_version` (`"msra/cross_domain_result/v1"`)
- **Example**:

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

**Description**: Cross-domain fusion quality gate checker implementing Gate CD-1.5 (data alignment gate) and Gate CD-3.5 (fusion results gate).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `study_id` | `str` | Yes | — | Study ID |
| `project_root` | `str` | No | `None` | Project root directory |

**Methods**:

#### `run_gate_cd15(data_sources, min_samples=3, scenario="correlation")`

Execute Gate CD-1.5 with all 3 checks: sample alignment (intersection >= min_samples), modality completeness (all required modalities for scenario provided), data type match (dimensions and dtype match expectations).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data_sources` | `dict[str, Any]` | Yes | — | Data source dict |
| `min_samples` | `int` | No | `3` | Minimum sample count |
| `scenario` | `str` | No | `"correlation"` | Scenario type (`"correlation"`, `"prediction"`, `"visualization"`, `"full"`) |

- **Returns**: `GateResult` — verdict (`PASS` / `CONDITIONAL` / `BLOCKED`)

#### `run_gate_cd35(correlation_results=None, model_metrics=None, visualization_data=None)`

Execute Gate CD-3.5 with all 3 checks: correlation significance (at least 1 significant pair after FDR or AUROC > 0.5), model performance (accuracy >= 0.5; AUROC >= 0.55; no NaN metrics), visualization consistency (heatmap matrix dimensions, curve point counts match input data).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `correlation_results` | `dict` | No | `None` | Correlation analysis results |
| `model_metrics` | `dict` | No | `None` | Model evaluation metrics |
| `visualization_data` | `dict` | No | `None` | Visualization data |

- **Returns**: `GateResult`
- **Example**:

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

## Scenario Required Modalities

| Scenario | Required Modalities |
|----------|-------------------|
| `correlation` | `radiomics`, `expression` |
| `prediction` | `realtime`, `labels` |
| `visualization` | >= 1 modality |
| `full` | `radiomics`, `expression`, `realtime`, `labels` |

---

## Full Usage Example

```python
from msra_modules.cross_domain import (
    RadiomicsDEGCorrelation, RealtimePredictionModel,
    MultiModalVisualizer, DataAligner, export_v1_schema,
    CrossDomainQualityGateChecker,
)
import pandas as pd
import numpy as np

# 1. Data alignment
aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": radiomics_df,
    "expression": expression_df,
})

# 2. Correlation analysis
analyzer = RadiomicsDEGCorrelation(correlation_method="spearman")
corr_result = analyzer.correlate(aligned["radiomics"], aligned["expression"])

# 3. Real-time prediction model
model = RealtimePredictionModel(model_type="logistic")
model.train(train_df, train_labels)
metrics = model.evaluate(X_test, y_test)

# 4. Multi-modal visualization
viz = MultiModalVisualizer()
fig = viz.create_linked_view(
    imaging_data=img_array,
    expression_data=aligned["expression"],
    realtime_data={"heart_rate": hr_list},
    save_path="/output/linked_view.png"
)

# 5. Export v1 schema
paths = export_v1_schema(
    correlation_results=corr_result,
    model_metrics=metrics,
    visualization_data={"paths": ["/output/linked_view.png"]},
    output_dir="/output/cross_domain/"
)

# 6. Quality gates
checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")
gate_15 = checker.run_gate_cd15(
    data_sources=aligned, min_samples=3, scenario="correlation"
)
gate_35 = checker.run_gate_cd35(
    correlation_results=corr_result, model_metrics=metrics
)
```
