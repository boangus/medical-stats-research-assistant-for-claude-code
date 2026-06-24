# Cross-Domain Module API Reference

> **Version**: v1.0.0 | **Date**: 2026-06-26 | **Status**: Stable
> **Module**: Cross-Domain | **Command**: `/cross-domain`

---

## Table of Contents

- [RadiomicsDEGCorrelation — Radiomics-Gene Correlation](#radiomicsdegcorrelation)
- [RealtimePredictionModel — Realtime Prediction Model](#realtimepredictionmodel)
- [MultiModalVisualizer — Multi-Modal Visualizer](#multimodalvisualizer)
- [CrossDomainQualityGateChecker — Quality Gate](#crossdomainqualitygatechecker)
- [DataAligner — Data Alignment](#dataaligner)
- [export_v1_schema() — Schema Export](#export_v1_schema)

---

## RadiomicsDEGCorrelation

> Radiomics and differentially expressed gene correlation analysis supporting Pearson, Spearman, and Kendall methods with FDR correction.

**Signature**:

```python
RadiomicsDEGCorrelation(correlation_method: str = "spearman",
                        pval_threshold: float = 0.05,
                        fdr_method: str = "bh")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| correlation_method | str | "spearman" | Correlation method ("pearson", "spearman", "kendall") |
| pval_threshold | float | 0.05 | p-value threshold |
| fdr_method | str | "bh" | FDR correction method ("bh", "bonferroni") |

**Methods**:

### `correlate`

```python
correlate(radiomics_features: pd.DataFrame, deg_expression: pd.DataFrame) -> Dict
```

Compute correlations between radiomics features and differential gene expression.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| radiomics_features | pd.DataFrame | — | Required. Radiomics features (samples × features) |
| deg_expression | pd.DataFrame | — | Required. Differential gene expression (samples × genes) |

**Returns**: `Dict` — Contains `correlations` (DataFrame), `n_significant`, `n_total`, `method`, `samples`

**Exceptions**: `ValueError` — fewer than 3 common samples; `ValueError` — unknown method

### `generate_heatmap_data`

```python
generate_heatmap_data(correlations: pd.DataFrame, top_n: int = 20) -> Dict
```

Generate heatmap data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| correlations | pd.DataFrame | — | Required. Correlation results (the correlations DataFrame from correlate()) |
| top_n | int | 20 | Number of top results to show |

**Returns**: `Dict` — Contains `features`, `genes`, `matrix` (2D list)

**Example**:

```python
from msra_modules.cross_domain import RadiomicsDEGCorrelation

correlator = RadiomicsDEGCorrelation(correlation_method="spearman", pval_threshold=0.05)
results = correlator.correlate(radiomics_df, expression_df)
print(f"Significant correlations: {results['n_significant']}/{results['n_total']}")

heatmap = correlator.generate_heatmap_data(results["correlations"], top_n=20)
```

---

## RealtimePredictionModel

> Realtime prediction model supporting Logistic Regression and Random Forest, extracting time-series features for risk prediction.

**Signature**:

```python
RealtimePredictionModel(window_size: int = 60, prediction_horizon: int = 30,
                        model_type: str = "logistic")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| window_size | int | 60 | Feature window size (seconds) |
| prediction_horizon | int | 30 | Prediction horizon (seconds) |
| model_type | str | "logistic" | Model type ("logistic", "random_forest") |

**Methods**:

### `train`

```python
train(historical_data: pd.DataFrame, labels: np.ndarray)
```

Train the model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| historical_data | pd.DataFrame | — | Required. Historical data (one sample per row) |
| labels | np.ndarray | — | Required. Labels (0/1) |

**Exceptions**: `ValueError` — unknown model type; `ImportError` — scikit-learn not installed

### `predict`

```python
predict(current_data: List[float]) -> Dict
```

Predict risk level for current data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| current_data | List[float] | — | Required. Current time-series data |

**Returns**: `Dict` — Contains `prediction` (0/1), `probability` (float), `risk_level` ("high"/"medium"/"low"/"minimal"), `features` (Dict)

**Exceptions**: `RuntimeError` — model not trained

### `evaluate`

```python
evaluate(X_test: np.ndarray, y_test: np.ndarray) -> Dict
```

Evaluate model performance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| X_test | np.ndarray | — | Required. Test data |
| y_test | np.ndarray | — | Required. Test labels |

**Returns**: `Dict` — Contains `accuracy`, `precision`, `recall`, `f1`, `auroc`

**Example**:

```python
from msra_modules.cross_domain import RealtimePredictionModel

model = RealtimePredictionModel(window_size=60, model_type="logistic")
model.train(train_df, train_labels)

result = model.predict([75, 78, 80, 120, 130])
print(f"Prediction: {result['prediction']}, Risk: {result['risk_level']}, Probability: {result['probability']:.4f}")

metrics = model.evaluate(X_test, y_test)
print(f"AUROC: {metrics['auroc']:.4f}")
```

---

## MultiModalVisualizer

> Multi-modal data visualization creating linked views of imaging, expression, clinical, and realtime data.

**Signature**:

```python
MultiModalVisualizer(figsize: tuple = (16, 10), dpi: int = 100)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| figsize | tuple | (16, 10) | Figure size |
| dpi | int | 100 | DPI resolution |

**Methods**:

### `create_linked_view`

```python
create_linked_view(imaging_data: Optional[np.ndarray] = None, imaging_mask: Optional[np.ndarray] = None,
                   expression_data: Optional[pd.DataFrame] = None,
                   clinical_data: Optional[pd.DataFrame] = None,
                   realtime_data: Optional[Dict] = None,
                   save_path: Optional[str] = None)
```

Create a linked view (2×2 subplots: imaging, expression heatmap, clinical boxplot, realtime trend).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| imaging_data | Optional[np.ndarray] | None | Imaging data |
| imaging_mask | Optional[np.ndarray] | None | Imaging mask |
| expression_data | Optional[pd.DataFrame] | None | Expression data |
| clinical_data | Optional[pd.DataFrame] | None | Clinical data |
| realtime_data | Optional[Dict] | None | Realtime data (metric name → value list) |
| save_path | Optional[str] | None | Save path |

**Returns**: `matplotlib.figure.Figure`

**Exceptions**: `ValueError` — no data source provided

### `create_summary_dashboard`

```python
create_summary_dashboard(data_sources: Dict[str, Any], save_path: Optional[str] = None)
```

Create a summary dashboard (multiple subplots showing each data source overview side by side).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data_sources | Dict[str, Any] | — | Required. Data source dictionary |
| save_path | Optional[str] | None | Save path |

**Returns**: `matplotlib.figure.Figure`

**Example**:

```python
from msra_modules.cross_domain import MultiModalVisualizer

viz = MultiModalVisualizer(figsize=(16, 10))
fig = viz.create_linked_view(
    imaging_data=image_array,
    imaging_mask=mask_array,
    expression_data=expression_df,
    realtime_data={"heart_rate": hr_list, "spo2": spo2_list},
    save_path="output/linked_view.png"
)
```

---

## CrossDomainQualityGateChecker

> Cross-domain quality gate checker encapsulating Gate CD-1.5 (data alignment) and Gate CD-3.5 (fusion results).

**Signature**:

```python
CrossDomainQualityGateChecker(study_id: str, project_root: Optional[str] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| study_id | str | — | Required. Study ID |
| project_root | Optional[str] | None | Project root directory (optional) |

**Methods**:

### `run_gate_cd15`

```python
run_gate_cd15(data_sources: Dict[str, Any], min_samples: int = 3,
              scenario: str = "correlation") -> GateResult
```

Execute Gate CD-1.5 with 3 checks: sample alignment, modality completeness, data type match.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data_sources | Dict[str, Any] | — | Required. Data source dict (e.g., `{"radiomics": df, "expression": df}`) |
| min_samples | int | 3 | Minimum sample count |
| scenario | str | "correlation" | Scenario type ("correlation", "prediction", "visualization", "full") |

**Returns**: `GateResult` — Verdict (PASS / CONDITIONAL / BLOCKED)

**Scenario Required Modalities**:

| Scenario | Required Modalities |
|----------|-------------------|
| correlation | radiomics, expression |
| prediction | realtime, labels |
| visualization | ≥ 1 modality |
| full | radiomics, expression, realtime, labels |

### `run_gate_cd35`

```python
run_gate_cd35(correlation_results: Optional[Dict] = None,
              model_metrics: Optional[Dict] = None,
              visualization_data: Optional[Dict] = None) -> GateResult
```

Execute Gate CD-3.5 with 3 checks: correlation significance, model performance, visualization consistency.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| correlation_results | Optional[Dict] | None | Correlation results (contains correlations DataFrame, n_significant) |
| model_metrics | Optional[Dict] | None | Model metrics (contains accuracy, auroc, precision, recall, f1) |
| visualization_data | Optional[Dict] | None | Visualization data (contains matrix_shape, curve_points, etc.) |

**Returns**: `GateResult` — Verdict

**Example**:

```python
from msra_modules.cross_domain import CrossDomainQualityGateChecker

checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")

# Gate CD-1.5: Data alignment
gate_15 = checker.run_gate_cd15(
    data_sources={"radiomics": df_features, "expression": df_expr},
    min_samples=3,
    scenario="correlation"
)
print(f"CD-1.5 verdict: {gate_15.verdict.value}")

# Gate CD-3.5: Fusion results
gate_35 = checker.run_gate_cd35(
    correlation_results=corr_dict,
    model_metrics=metrics_dict
)
print(f"CD-3.5 verdict: {gate_35.verdict.value}")
print(f"Pass rate: {gate_35.pass_rate:.1%}")
```

---

## DataAligner

> Multi-modal data aligner supporting inner (strict match), outer (allow missing), and time_based (temporal alignment) strategies.

**Signature**:

```python
DataAligner(strategy: str = "inner", fill_method: str = "mean")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| strategy | str | "inner" | Alignment strategy ("inner", "outer", "time_based") |
| fill_method | str | "mean" | Missing value fill method ("mean", "median", "zero", "ffill") |

**Exceptions**: `ValueError` — invalid strategy or fill_method

**Methods**:

### `align`

```python
align(data_sources: Dict[str, Any], strategy: Optional[str] = None) -> Dict[str, Any]
```

Execute data alignment.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data_sources | Dict[str, Any] | — | Required. Data source dict `{name: DataFrame or Dict}` |
| strategy | Optional[str] | None | Override default strategy |

**Returns**: `Dict[str, Any]` — Aligned data sources (all DataFrames share the same index)

**Exceptions**: `ValueError` — empty data_sources; inner join result < 3 samples; unknown strategy

**Alignment Strategies**:

| Strategy | Description |
|----------|-------------|
| inner | Strict match: intersection of all DataFrame indices (errors if < 3 samples) |
| outer | Allow missing: union of all DataFrame indices, fill missing with fill_method |
| time_based | Temporal alignment: group by time window (default 60s), aggregate with mean per window |

**Example**:

```python
from msra_modules.cross_domain import DataAligner

aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": df_features,
    "expression": df_expr,
})
# aligned["radiomics"] and aligned["expression"] are aligned to the same samples
print(f"Aligned samples: {len(aligned['radiomics'])}")
```

---

## export_v1_schema

> Export msra/cross_domain_result/v1 standard format, outputting correlation results, model metrics, visualization files, and a comprehensive report.

**Signature**:

```python
export_v1_schema(correlation_results: Optional[Dict] = None,
                 model_metrics: Optional[Dict] = None,
                 visualization_data: Optional[Dict] = None,
                 output_dir: str = ".") -> Dict[str, str]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| correlation_results | Optional[Dict] | None | Correlation results (return value of RadiomicsDEGCorrelation.correlate()) |
| model_metrics | Optional[Dict] | None | Model metrics (return value of RealtimePredictionModel.evaluate()) |
| visualization_data | Optional[Dict] | None | Visualization data (output of MultiModalVisualizer) |
| output_dir | str | "." | Output directory |

**Returns**: `Dict[str, str]` — File path mapping:
- `correlation_results`: path to correlation_results.csv
- `model_metrics`: path to model_metrics.json
- `visualization_bundle`: path to visualization_bundle/ directory
- `report`: path to cross_domain_report.md
- `schema_version`: "msra/cross_domain_result/v1"

**Output File Structure**:

```
output_dir/
├── correlation_results.csv     # Correlation analysis results
├── model_metrics.json           # Model evaluation metrics
├── visualization_bundle/        # Visualization file bundle
│   ├── linked_view.png
│   └── summary_dashboard.png
└── cross_domain_report.md       # Comprehensive report
```

**Example**:

```python
from msra_modules.cross_domain import export_v1_schema

result = export_v1_schema(
    correlation_results=corr_dict,
    model_metrics=metrics_dict,
    visualization_data={"paths": ["output/linked_view.png"]},
    output_dir="output/cross_domain/"
)
print(f"Report path: {result['report']}")
print(f"Schema version: {result['schema_version']}")
```

---

## Shared Types Reference

### CheckItemResult

| Property | Type | Description |
|----------|------|-------------|
| item_id | str | Check item ID |
| name | str | Check item name |
| is_key | bool | Whether it is a key item |
| status | str | Status (PASS / FAIL / N/A / SKIP) |
| evidence | str | Evidence description |
| notes | str | Notes |

### GateResult

| Property | Type | Description |
|----------|------|-------------|
| gate_type | GateType | Gate type |
| study_id | str | Study ID |
| verdict | GateVerdict | Verdict (PASS / CONDITIONAL / BLOCKED) |
| total_items | int | Total check items |
| passed_items | int | Passed items |
| failed_items | int | Failed items |
| key_items_status | str | Key items status |
| check_results | List[CheckItemResult] | Detailed results per item |
| risks | List[str] | Risk list |
| pass_rate | float | Pass rate |

### GateVerdict

| Value | Description |
|-------|-------------|
| PASS | All passed |
| CONDITIONAL | Conditional pass (1-2 non-key items failed) |
| BLOCKED | Blocked (3+ items failed or key item failed) |

### GateType

| Value | Description |
|-------|-------------|
| DATA_QUALITY | Data quality gate (Gate 1.5) |
| SAP_QUALITY | SAP quality gate (Gate 2.5) |
| RESULTS_QUALITY | Results quality gate (Gate 3.5) |
