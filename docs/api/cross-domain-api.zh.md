# 跨领域融合模块 API 参考

> **版本**: v1.0.0 | **日期**: 2026-06-26 | **状态**: Stable
> **模块**: Cross-Domain | **命令**: `/cross-domain`

---

## 目录

- [RadiomicsDEGCorrelation — 影像-基因关联分析](#radiomicsdegcorrelation)
- [RealtimePredictionModel — 实时预警模型](#realtimepredictionmodel)
- [MultiModalVisualizer — 多模态可视化](#multimodalvisualizer)
- [CrossDomainQualityGateChecker — 质量门闸](#crossdomainqualitygatechecker)
- [DataAligner — 数据对齐](#dataaligner)
- [export_v1_schema() — Schema 导出](#export_v1_schema)

---

## RadiomicsDEGCorrelation

> 影像组学与差异表达基因关联分析，支持 Pearson、Spearman、Kendall 相关性计算和 FDR 校正。

**签名**:

```python
RadiomicsDEGCorrelation(correlation_method: str = "spearman",
                        pval_threshold: float = 0.05,
                        fdr_method: str = "bh")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| correlation_method | str | "spearman" | 相关系数方法（"pearson"、"spearman"、"kendall"） |
| pval_threshold | float | 0.05 | p 值阈值 |
| fdr_method | str | "bh" | FDR 校正方法（"bh"、"bonferroni"） |

**方法**:

### `correlate`

```python
correlate(radiomics_features: pd.DataFrame, deg_expression: pd.DataFrame) -> Dict
```

计算影像组学特征与差异基因表达之间的关联。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| radiomics_features | pd.DataFrame | — | 必填，影像组学特征（样本×特征） |
| deg_expression | pd.DataFrame | — | 必填，差异基因表达（样本×基因） |

**返回值**: `Dict` — 含 `correlations`（DataFrame）、`n_significant`、`n_total`、`method`、`samples`

**异常**: `ValueError` — 公共样本数 < 3；`ValueError` — 未知方法

### `generate_heatmap_data`

```python
generate_heatmap_data(correlations: pd.DataFrame, top_n: int = 20) -> Dict
```

生成热图数据。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| correlations | pd.DataFrame | — | 必填，相关性结果（correlate 返回的 correlations DataFrame） |
| top_n | int | 20 | 显示前 N 个 |

**返回值**: `Dict` — 含 `features`、`genes`、`matrix`（二维列表）

**示例**:

```python
from msra_modules.cross_domain import RadiomicsDEGCorrelation

correlator = RadiomicsDEGCorrelation(correlation_method="spearman", pval_threshold=0.05)
results = correlator.correlate(radiomics_df, expression_df)
print(f"显著关联: {results['n_significant']}/{results['n_total']}")

heatmap = correlator.generate_heatmap_data(results["correlations"], top_n=20)
```

---

## RealtimePredictionModel

> 实时预警模型，支持 Logistic Regression 和 Random Forest，提取时间序列特征进行风险预测。

**签名**:

```python
RealtimePredictionModel(window_size: int = 60, prediction_horizon: int = 30,
                        model_type: str = "logistic")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| window_size | int | 60 | 特征窗口大小（秒） |
| prediction_horizon | int | 30 | 预测时间窗（秒） |
| model_type | str | "logistic" | 模型类型（"logistic"、"random_forest"） |

**方法**:

### `train`

```python
train(historical_data: pd.DataFrame, labels: np.ndarray)
```

训练模型。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| historical_data | pd.DataFrame | — | 必填，历史数据（每行一个样本） |
| labels | np.ndarray | — | 必填，标签（0/1） |

**异常**: `ValueError` — 未知模型类型；`ImportError` — scikit-learn 未安装

### `predict`

```python
predict(current_data: List[float]) -> Dict
```

预测当前数据的风险等级。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| current_data | List[float] | — | 必填，当前时间序列数据 |

**返回值**: `Dict` — 含 `prediction`（0/1）、`probability`（float）、`risk_level`（"high"/"medium"/"low"/"minimal"）、`features`（Dict）

**异常**: `RuntimeError` — 模型未训练

### `evaluate`

```python
evaluate(X_test: np.ndarray, y_test: np.ndarray) -> Dict
```

评估模型性能。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| X_test | np.ndarray | — | 必填，测试数据 |
| y_test | np.ndarray | — | 必填，测试标签 |

**返回值**: `Dict` — 含 `accuracy`、`precision`、`recall`、`f1`、`auroc`

**示例**:

```python
from msra_modules.cross_domain import RealtimePredictionModel

model = RealtimePredictionModel(window_size=60, model_type="logistic")
model.train(train_df, train_labels)

result = model.predict([75, 78, 80, 120, 130])
print(f"预测: {result['prediction']}, 风险: {result['risk_level']}, 概率: {result['probability']:.4f}")

metrics = model.evaluate(X_test, y_test)
print(f"AUROC: {metrics['auroc']:.4f}")
```

---

## MultiModalVisualizer

> 多模态数据联合可视化，创建影像、表达、临床和实时数据的联动视图。

**签名**:

```python
MultiModalVisualizer(figsize: tuple = (16, 10), dpi: int = 100)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| figsize | tuple | (16, 10) | 图像大小 |
| dpi | int | 100 | 分辨率 |

**方法**:

### `create_linked_view`

```python
create_linked_view(imaging_data: Optional[np.ndarray] = None, imaging_mask: Optional[np.ndarray] = None,
                   expression_data: Optional[pd.DataFrame] = None,
                   clinical_data: Optional[pd.DataFrame] = None,
                   realtime_data: Optional[Dict] = None,
                   save_path: Optional[str] = None)
```

创建联动视图（2×2 子图：影像、表达热图、临床箱线图、实时趋势图）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| imaging_data | Optional[np.ndarray] | None | 影像数据 |
| imaging_mask | Optional[np.ndarray] | None | 影像掩码 |
| expression_data | Optional[pd.DataFrame] | None | 表达数据 |
| clinical_data | Optional[pd.DataFrame] | None | 临床数据 |
| realtime_data | Optional[Dict] | None | 实时数据（指标名→值列表） |
| save_path | Optional[str] | None | 保存路径 |

**返回值**: `matplotlib.figure.Figure`

**异常**: `ValueError` — 未提供任何数据源

### `create_summary_dashboard`

```python
create_summary_dashboard(data_sources: Dict[str, Any], save_path: Optional[str] = None)
```

创建摘要仪表盘（多个子图并排展示各数据源概览）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| data_sources | Dict[str, Any] | — | 必填，数据源字典 |
| save_path | Optional[str] | None | 保存路径 |

**返回值**: `matplotlib.figure.Figure`

**示例**:

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

> 跨领域融合质量门闸检查器，封装 Gate CD-1.5（数据对齐）和 Gate CD-3.5（融合结果）的检查逻辑。

**签名**:

```python
CrossDomainQualityGateChecker(study_id: str, project_root: Optional[str] = None)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| study_id | str | — | 必填，研究编号 |
| project_root | Optional[str] | None | 项目根目录（可选） |

**方法**:

### `run_gate_cd15`

```python
run_gate_cd15(data_sources: Dict[str, Any], min_samples: int = 3,
              scenario: str = "correlation") -> GateResult
```

执行 Gate CD-1.5 全部 3 项检查：样本对齐、模态完整性、数据类型匹配。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| data_sources | Dict[str, Any] | — | 必填，数据源字典（如 `{"radiomics": df, "expression": df}`） |
| min_samples | int | 3 | 最小样本数 |
| scenario | str | "correlation" | 场景类型（"correlation"、"prediction"、"visualization"、"full"） |

**返回值**: `GateResult` — 判定结果（PASS / CONDITIONAL / BLOCKED）

**场景所需模态**:

| 场景 | 所需模态 |
|------|---------|
| correlation | radiomics, expression |
| prediction | realtime, labels |
| visualization | ≥ 1 个模态 |
| full | radiomics, expression, realtime, labels |

### `run_gate_cd35`

```python
run_gate_cd35(correlation_results: Optional[Dict] = None,
              model_metrics: Optional[Dict] = None,
              visualization_data: Optional[Dict] = None) -> GateResult
```

执行 Gate CD-3.5 全部 3 项检查：关联显著性、模型性能、可视化一致性。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| correlation_results | Optional[Dict] | None | 关联分析结果（含 correlations DataFrame、n_significant） |
| model_metrics | Optional[Dict] | None | 模型评估指标（含 accuracy、auroc、precision、recall、f1） |
| visualization_data | Optional[Dict] | None | 可视化数据（含 matrix_shape、curve_points 等） |

**返回值**: `GateResult` — 判定结果

**示例**:

```python
from msra_modules.cross_domain import CrossDomainQualityGateChecker

checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")

# Gate CD-1.5: 数据对齐检查
gate_15 = checker.run_gate_cd15(
    data_sources={"radiomics": df_features, "expression": df_expr},
    min_samples=3,
    scenario="correlation"
)
print(f"CD-1.5 判定: {gate_15.verdict.value}")

# Gate CD-3.5: 融合结果检查
gate_35 = checker.run_gate_cd35(
    correlation_results=corr_dict,
    model_metrics=metrics_dict
)
print(f"CD-3.5 判定: {gate_35.verdict.value}")
print(f"通过率: {gate_35.pass_rate:.1%}")
```

---

## DataAligner

> 多模态数据对齐器，支持 inner（严格匹配）、outer（允许缺失）和 time_based（时序对齐）三种策略。

**签名**:

```python
DataAligner(strategy: str = "inner", fill_method: str = "mean")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| strategy | str | "inner" | 对齐策略（"inner"、"outer"、"time_based"） |
| fill_method | str | "mean" | 缺失值填充方法（"mean"、"median"、"zero"、"ffill"） |

**异常**: `ValueError` — 无效的 strategy 或 fill_method

**方法**:

### `align`

```python
align(data_sources: Dict[str, Any], strategy: Optional[str] = None) -> Dict[str, Any]
```

执行数据对齐。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| data_sources | Dict[str, Any] | — | 必填，数据源字典 `{name: DataFrame or Dict}` |
| strategy | Optional[str] | None | 覆盖默认策略 |

**返回值**: `Dict[str, Any]` — 对齐后的数据源字典（所有 DataFrame 具有相同的 index）

**异常**: `ValueError` — data_sources 为空；inner join 后样本数 < 3；未知策略

**对齐策略说明**:

| 策略 | 说明 |
|------|------|
| inner | 严格匹配：取所有 DataFrame index 的交集（样本数 < 3 时报错） |
| outer | 允许缺失：取所有 DataFrame index 的并集，缺失值用 fill_method 填充 |
| time_based | 时序对齐：按时间窗（默认 60 秒）分组聚合，每窗口取均值 |

**示例**:

```python
from msra_modules.cross_domain import DataAligner

aligner = DataAligner(strategy="inner")
aligned = aligner.align({
    "radiomics": df_features,
    "expression": df_expr,
})
# aligned["radiomics"] 和 aligned["expression"] 已对齐到相同样本
print(f"对齐后样本数: {len(aligned['radiomics'])}")
```

---

## export_v1_schema

> 导出 msra/cross_domain_result/v1 标准格式，输出关联分析结果、模型指标、可视化文件和综合报告。

**签名**:

```python
export_v1_schema(correlation_results: Optional[Dict] = None,
                 model_metrics: Optional[Dict] = None,
                 visualization_data: Optional[Dict] = None,
                 output_dir: str = ".") -> Dict[str, str]
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| correlation_results | Optional[Dict] | None | 关联分析结果（RadiomicsDEGCorrelation.correlate() 的返回值） |
| model_metrics | Optional[Dict] | None | 模型评估指标（RealtimePredictionModel.evaluate() 的返回值） |
| visualization_data | Optional[Dict] | None | 可视化数据（MultiModalVisualizer 的输出数据） |
| output_dir | str | "." | 输出目录 |

**返回值**: `Dict[str, str]` — 文件路径映射：
- `correlation_results`: correlation_results.csv 路径
- `model_metrics`: model_metrics.json 路径
- `visualization_bundle`: visualization_bundle/ 目录路径
- `report`: cross_domain_report.md 路径
- `schema_version`: "msra/cross_domain_result/v1"

**输出文件结构**:

```
output_dir/
├── correlation_results.csv     # 关联分析结果表
├── model_metrics.json           # 模型评估指标
├── visualization_bundle/        # 可视化文件包
│   ├── linked_view.png
│   └── summary_dashboard.png
└── cross_domain_report.md       # 综合报告
```

**示例**:

```python
from msra_modules.cross_domain import export_v1_schema

result = export_v1_schema(
    correlation_results=corr_dict,
    model_metrics=metrics_dict,
    visualization_data={"paths": ["output/linked_view.png"]},
    output_dir="output/cross_domain/"
)
print(f"报告路径: {result['report']}")
print(f"Schema 版本: {result['schema_version']}")
```

---

## 共享类型参考

### CheckItemResult

| 属性 | 类型 | 说明 |
|------|------|------|
| item_id | str | 检查项编号 |
| name | str | 检查项名称 |
| is_key | bool | 是否为关键项 |
| status | str | 状态（PASS / FAIL / N/A / SKIP） |
| evidence | str | 证据描述 |
| notes | str | 备注 |

### GateResult

| 属性 | 类型 | 说明 |
|------|------|------|
| gate_type | GateType | 门闸类型 |
| study_id | str | 研究编号 |
| verdict | GateVerdict | 判定结果（PASS / CONDITIONAL / BLOCKED） |
| total_items | int | 总检查项数 |
| passed_items | int | 通过项数 |
| failed_items | int | 失败项数 |
| key_items_status | str | 关键项状态 |
| check_results | List[CheckItemResult] | 各项详细结果 |
| risks | List[str] | 风险列表 |
| pass_rate | float | 通过率 |

### GateVerdict

| 值 | 说明 |
|----|------|
| PASS | 全部通过 |
| CONDITIONAL | 条件通过（1-2 项未过，非关键项） |
| BLOCKED | 阻断（3+ 项未过或关键项未过） |

### GateType

| 值 | 说明 |
|----|------|
| DATA_QUALITY | 数据质量门闸（Gate 1.5） |
| SAP_QUALITY | SAP 质量门闸（Gate 2.5） |
| RESULTS_QUALITY | 结果质量门闸（Gate 3.5） |
