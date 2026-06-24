# MSRA Cross-Domain Module User Tutorial

> **Module Version**: v1.0.0 | **Document Date**: 2026-06-25 | **Status**: Stable
> **Command Entry**: `/msra-cross` | **MSRA Version**: v1.0.0+

---

## 1. Module Overview & Use Cases

### Overview

The MSRA Cross-Domain module is the core fusion engine of MSRA v1.0.0. It integrates analysis results from three modules — medical_imaging (radiomics), bioinformatics (gene expression), and realtime_analytics (vital signs monitoring) — to perform cross-modal fusion analysis, revealing cross-domain association patterns that no single module can discover alone.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| Radiomics-DEG Correlation | Correlation analysis between radiomics features and differential gene expression via `RadiomicsDEGCorrelation` |
| Realtime Prediction Model | Risk prediction model training from time-series data via `RealtimePredictionModel` |
| Multi-modal Visualization | Four-quadrant linked view (imaging + expression + clinical + realtime) via `MultiModalVisualizer` |
| Data Alignment | Multi-strategy sample alignment (inner/outer/time_based) via `DataAligner` |
| Schema Export | `msra/cross_domain_result/v1` standard format via `export_v1_schema` |
| Quality Gates | Gate CD-1.5 (data alignment) + Gate CD-3.5 (fusion results) via `CrossDomainQualityGateChecker` |

### Use Cases

- Association analysis between imaging phenotypes and molecular features (radiomics × gene expression)
- Clinical deterioration early warning modeling based on vital signs time-series data
- Joint visualization and exploration of multi-modal data (imaging + gene + clinical + realtime)
- Exporting fusion feature matrices for joint statistical modeling in the main Pipeline

---

## 2. Installation

### Install cross_domain extra dependencies

```bash
pip install -e ".[cross_domain]"
```

### Core Dependencies

```toml
scipy >= 1.10           # Statistical analysis (correlation computation)
scikit-learn >= 1.3     # Machine learning (prediction models)
numpy >= 1.24           # Numerical computing
pandas >= 2.0           # Data processing
matplotlib >= 3.7       # Visualization
```

### Verify Installation

```bash
python -c "from msra_modules.cross_domain import RadiomicsDEGCorrelation, RealtimePredictionModel, MultiModalVisualizer, DataAligner, CrossDomainQualityGateChecker, export_v1_schema; print('OK')"
```

---

## 3. Prerequisites

### Upstream Module Outputs

The Cross-Domain module **does not process raw data directly** — it consumes analysis products from the other three modules:

| Data Type | Source Module | Output Format | Typical Path |
|-----------|--------------|---------------|--------------|
| Radiomics feature matrix | `/msra-imaging` | CSV (sample × feature) | `MSRA/data/imaging_features_v1.csv` |
| Differential gene expression matrix | `/msra-bio` | CSV (sample × gene) | `MSRA/data/bio_covariates.csv` |
| Time-series monitoring data | `/msra-rt` | CSV / Dict (metric → values) | `MSRA/reports/rt_monitoring_*.html` |
| Clinical data | User-provided | CSV (sample × variables) | Custom |

### Data Format Requirements

All DataFrames must have **sample IDs as the index** for cross-modal alignment:

```python
# Radiomics feature matrix example
#                    feature_glcm_contrast  feature_shape_volume  ...
# patient_001                      12.5                4500.0
# patient_002                      15.3                5200.0
# patient_003                       8.7                3800.0

# Gene expression matrix example
#                    Gene_TP53  Gene_BRCA1  Gene_EGFR  ...
# patient_001            2.3         1.8       0.5
# patient_002            1.1         3.2       2.1
# patient_003            0.8         1.5       0.3
```

### Example: Prepare Mock Data

```python
import pandas as pd
import numpy as np

np.random.seed(42)
samples = [f"patient_{i:03d}" for i in range(20)]

# Mock radiomics features (20 samples × 5 features)
radiomics_df = pd.DataFrame(
    np.random.randn(20, 5),
    index=samples,
    columns=["glcm_contrast", "shape_volume", "firstorder_mean", "glrlm_lre", "glszm_zs"]
)
radiomics_df.to_csv("mock_radiomics.csv")

# Mock gene expression (20 samples × 8 genes)
genes = [f"Gene_{g}" for g in ["TP53", "BRCA1", "EGFR", "KRAS", "PTEN", "MYC", "RB1", "APC"]]
expression_df = pd.DataFrame(
    np.random.randn(20, 8),
    index=samples,
    columns=genes,
)
expression_df.to_csv("mock_expression.csv")
```

---

## 4. Scenario A: Radiomics-DEG Correlation

### Launch via Command

```
/msra-cross --scenario correlation --radiomics features.csv --expression deg.csv
```

### Python API Complete Workflow

```python
import pandas as pd
from msra_modules.cross_domain import (
    RadiomicsDEGCorrelation, DataAligner,
    CrossDomainQualityGateChecker,
)

# Phase 0: Load data
radiomics_df = pd.read_csv("mock_radiomics.csv", index_col=0)
expression_df = pd.read_csv("mock_expression.csv", index_col=0)

# Phase 1: Data alignment + Gate CD-1.5
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

# Phase 2: Correlation analysis
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

# View significant correlations
corr_df = results["correlations"]
significant = corr_df[corr_df["significant"]].sort_values("p_adj")
print(significant[["feature", "gene", "correlation", "p_adj"]].head(10))

# Generate heatmap data
heatmap_data = correlator.generate_heatmap_data(corr_df, top_n=20)
print(f"Heatmap features: {len(heatmap_data['features'])}")
print(f"Heatmap genes: {len(heatmap_data['genes'])}")
```

### Phase 3: Gate CD-3.5 + Result Review

```python
# Gate CD-3.5
gate_35 = checker.run_gate_cd35(
    correlation_results=results,
)
print(f"Gate CD-3.5: {gate_35.verdict}")
```

### Heatmap Interpretation

The heatmap shows correlation coefficients between radiomics features (rows) and differential genes (columns):
- **Red**: Positive correlation (high feature value → high gene expression)
- **Blue**: Negative correlation (high feature value → low gene expression)
- **Color intensity**: Magnitude of the correlation coefficient
- **Asterisk markers**: Significant pairs after FDR correction (p_adj < 0.05 and |r| ≥ 0.3)

---

## 5. Scenario B: Realtime Prediction Model

### Launch via Command

```
/msra-cross --scenario prediction --realtime vitals.csv --labels labels.csv
```

### Python API Complete Workflow

```python
import pandas as pd
import numpy as np
from msra_modules.cross_domain import (
    RealtimePredictionModel, CrossDomainQualityGateChecker,
)

# Phase 0: Load data
# historical_data: each row is a sample with time-series features
# labels: 0=normal, 1=deterioration
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

# Phase 2: Train prediction model
model = RealtimePredictionModel(
    window_size=60,           # Feature window size (seconds)
    prediction_horizon=30,    # Prediction time horizon (seconds)
    model_type="logistic",    # logistic | random_forest
)

model.train(historical_data, labels)

# Evaluate model
X_test = historical_data.values  # In practice, use a separate test set
y_test = labels
metrics = model.evaluate(X_test, y_test)

print(f"Accuracy:  {metrics['accuracy']:.4f}")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall:    {metrics['recall']:.4f}")
print(f"F1:        {metrics['f1']:.4f}")
print(f"AUROC:     {metrics['auroc']:.4f}")

# Real-time prediction
current_vitals = [72, 75, 78, 80, 85, 90, 95, 100, 105, 110]  # Last 10 data points
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

### Risk Level Interpretation

| Risk Level | Probability Range | Recommended Action |
|------------|-------------------|--------------------|
| high | ≥ 0.8 | Immediate intervention |
| medium | 0.5 - 0.8 | Close monitoring |
| low | 0.3 - 0.5 | Enhanced observation |
| minimal | < 0.3 | Routine monitoring |

---

## 6. Scenario C: Multi-modal Visualization

### Launch via Command

```
/msra-cross --scenario visualization --radiomics f.csv --expression e.csv --clinical c.csv --realtime r.csv
```

### Python API Complete Workflow

```python
import pandas as pd
import numpy as np
from msra_modules.cross_domain import (
    MultiModalVisualizer, DataAligner,
    CrossDomainQualityGateChecker,
)

# Phase 0: Load multi-modal data
radiomics_df = pd.read_csv("mock_radiomics.csv", index_col=0)
expression_df = pd.read_csv("mock_expression.csv", index_col=0)
clinical_df = pd.read_csv("clinical_data.csv", index_col=0)
realtime_data = {
    "heart_rate": [72, 75, 78, 80, 85, 90, 88, 85, 82, 80],
    "spo2": [98, 97, 97, 96, 95, 93, 94, 95, 96, 97],
}
imaging_volume = np.random.randn(64, 64, 32)  # Mock imaging data

# Phase 1: Data alignment + Gate CD-1.5
aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": radiomics_df,
    "expression": expression_df,
    "clinical": clinical_df,
})

checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")
gate_15 = checker.run_gate_cd15(
    data_sources=aligned,
    min_samples=1,  # Visualization scenario: minimum 1 sample
    scenario="visualization",
)
print(f"Gate CD-1.5: {gate_15.verdict}")

# Phase 2: Generate linked view
visualizer = MultiModalVisualizer(figsize=(16, 10), dpi=100)

# Four-quadrant linked view
fig = visualizer.create_linked_view(
    imaging_data=imaging_volume,
    imaging_mask=None,
    expression_data=aligned["expression"],
    clinical_data=aligned["clinical"],
    realtime_data=realtime_data,
    save_path="linked_view.png",
)
print("Linked view saved to: linked_view.png")

# Summary dashboard
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

### Linked View Layout

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   Medical Imaging   │  Gene Expression    │
│   (image slice+mask)│  (expression heatmap)│
│                     │                     │
├─────────────────────┼─────────────────────┤
│                     │                     │
│  Clinical Data      │  Real-time          │
│  (clinical boxplot) │  Monitoring         │
│                     │  (realtime curves)  │
│                     │                     │
└─────────────────────┴─────────────────────┘
```

---

## 7. Quality Gates

### Gate CD-1.5 — Data Alignment Gate

> Executed in Phase 1 (after data alignment), blocks misaligned data from entering fusion analysis.
> Implementation: `msra_modules/cross_domain/quality_gates.py` → `CrossDomainQualityGateChecker`

| # | Check Item | Critical | Pass Criteria |
|---|------------|----------|---------------|
| 1 | Sample alignment | 🔑 | Intersection sample count ≥ min_samples (correlation: 3, prediction: 10, visualization: 1) |
| 2 | Modality completeness | 🔑 | All required modalities for the selected scenario are provided |
| 3 | Data type matching | | Dimensions/dtype of each modality match expectations |

**Verdict Rules**:
- **PASS**: 3/3 checks passed
- **CONDITIONAL**: 1-2 non-critical items failed, continue with risk noted
- **BLOCKED**: Critical items failed or all 3 items failed (**blocks the pipeline**)

### Gate CD-3.5 — Fusion Result Gate

> Executed in Phase 3 (before result review), validates fusion analysis result quality.

| # | Check Item | Critical | Pass Criteria |
|---|------------|----------|---------------|
| 1 | Correlation significance | 🔑 | Significant results after FDR (p_adj<0.05 & |r|≥0.3) or AUROC>0.5 |
| 2 | Model performance | 🔑 | accuracy ≥ 0.5; AUROC ≥ 0.55; no NaN |
| 3 | Visualization consistency | | Visualization data dimensions match input data |

### Python Usage Example

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

## 8. Complete Fusion Workflow Demo

### Full Workflow Using All Three Scenarios

```
/msra-cross --scenario full --radiomics features.csv --expression deg.csv --clinical clinical.csv --realtime vitals.csv
```

### Python API Complete Fusion Workflow

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

# === Phase 0: Load all modal data ===
radiomics_df = pd.read_csv("mock_radiomics.csv", index_col=0)
expression_df = pd.read_csv("mock_expression.csv", index_col=0)
clinical_df = pd.read_csv("clinical_data.csv", index_col=0)
realtime_data = {"heart_rate": [72, 75, 78, 80, 85], "spo2": [98, 97, 96, 95, 94]}
labels = np.array([0, 1, 0, 1, 0, 1, 0, 0, 1, 0,
                   0, 1, 0, 1, 0, 0, 1, 0, 1, 0])

# === Phase 1: Data alignment + Gate CD-1.5 ===
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

# === Phase 2: Three parallel fusion analyses ===

# Task A: Radiomics-DEG correlation
correlator = RadiomicsDEGCorrelation(
    correlation_method="spearman",
    fdr_method="bh",
)
corr_results = correlator.correlate(
    radiomics_features=aligned["radiomics"],
    deg_expression=aligned["expression"],
)
print(f"[A] Significant correlations: {corr_results['n_significant']}")

# Task B: Realtime prediction model
model = RealtimePredictionModel(
    model_type="random_forest",
    window_size=60,
)
model.train(radiomics_df, labels)
metrics = model.evaluate(radiomics_df.values, labels)
print(f"[B] Model AUROC: {metrics['auroc']:.4f}")

# Task C: Multi-modal visualization
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

# === Phase 4: Export v1 Schema ===
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

## 9. Integration with Main Pipeline

### Export Fusion Feature Matrix

```python
import pandas as pd

# Combine significant feature-gene pairs into a fusion feature matrix
fusion_features = pd.DataFrame(index=aligned["radiomics"].index)

# Add significant radiomics-gene interaction features
for _, row in significant.iterrows():
    feat_name = row["feature"]
    gene_name = row["gene"]
    # Use the product of radiomics feature and gene expression as a fusion feature
    fusion_features[f"{feat_name}_x_{gene_name}"] = (
        aligned["radiomics"][feat_name] * aligned["expression"][gene_name]
    )

fusion_features.to_csv("MSRA/data/cross_domain_features.csv")
print(f"Cross-domain features: {fusion_features.shape}")
```

### Automatic Pipeline Integration

In Phase 4, select the "Integrate with Pipeline" option. The system will:
1. Write the fusion feature matrix to `MSRA/data/cross_domain_features.csv`
2. Automatically trigger `/msra-exec` to incorporate it as predictor variables in Stage 3

### Command-Line Direct Invocation

```
/msra-cross --scenario full --radiomics features.csv --expression deg.csv --integrate-pipeline
```

---

## 10. FAQ

### Q1: Gate CD-1.5 sample alignment fails (intersection < 3)?

- Check that all modality DataFrames use the same sample ID naming convention for their index
- Consider using the `outer` alignment strategy (allows missing values with automatic imputation)
- If sample size is genuinely insufficient, more data is needed

```python
aligner = DataAligner(strategy="outer", fill_method="mean")
```

### Q2: No significant results in correlation analysis?

- Increase sample size (current samples may be insufficient)
- Try different correlation methods (pearson → spearman → kendall)
- Lower the significance threshold (p_adj < 0.1)
- Verify data is properly standardized

### Q3: Prediction model AUROC is close to 0.5?

- Features may be insufficient: increase the time-series window size or add more metrics
- Try the `random_forest` model (may better capture non-linear relationships than `logistic`)
- Check label balance (large 0/1 ratio imbalance)

### Q4: How to use the DataAligner time_based strategy?

The `time_based` strategy is for time-series data, aggregating by time window:

```python
aligner = DataAligner(strategy="time_based")
# Window size defaults to 60 seconds, inherited from Phase 0 parameters
# Data within each 60-second window is averaged for alignment
```

### Q5: A quadrant in the linked view is empty?

The linked view only shows quadrants for which data is provided. If a modality is `None`, the corresponding quadrant is automatically skipped. Ensure at least 1 modality is provided.

### Q6: What files does export_v1_schema output?

| File | Description |
|------|-------------|
| `correlation_results.csv` | Correlation results table (feature, gene, correlation, p_value, p_adj, significant, method) |
| `model_metrics.json` | Model evaluation metrics (accuracy, precision, recall, f1, auroc, model_type, n_samples, n_features) |
| `visualization_bundle/` | Visualization file bundle (linked_view.png, summary_dashboard.png) |
| `cross_domain_report.md` | Comprehensive report (summary + methods + results + figure references) |

### Q7: What is the dependency relationship between the four modules?

```
medical_imaging ──┐
bioinformatics ───┼──→ cross_domain ──→ Main Pipeline (Stage 3)
realtime_analytics┘
```

The cross_domain module has a one-way dependency on the upstream three modules' outputs and does not create reverse dependencies.

---

> **Related Docs**: [SKILL.md](../../skills/cross-domain/SKILL.md) | [Module PRD](../prd/cross-domain-module-prd.md) | [System Design](../system_design_cross_domain.md) | [MSRA Docs Home](../system_design.md)
