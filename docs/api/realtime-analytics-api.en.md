# Realtime Analytics Module API Reference

> **Version**: v1.0.0 | **Date**: 2026-06-26 | **Status**: Stable
> **Module**: Realtime Analytics | **Command**: `/realtime`

---

## Table of Contents

- [StreamProcessor — Stream Processor](#streamprocessor)
- [AnomalyDetector — Anomaly Detector](#anomalydetector)
- [DetectionResult — Detection Result](#detectionresult)
- [MultivariateDetector — Multivariate Detector](#multivariatedetector)
- [AlertSystem — Alert System](#alertsystem)
- [Alert — Alert Data Class](#alert)
- [RealtimeDashboard — Dashboard](#realtimedashboard)
- [VitalSignsSimulator — Vital Signs Simulator](#vitalsignssimulator)
- [RealtimeQualityGateChecker — Quality Gate](#realtimequalitygatechecker)

---

## StreamProcessor

> Stream processor providing sliding window statistics, Kafka consumption, event processing, and aggregation.

**Signature**:

```python
StreamProcessor(window_size: int = 60, kafka_bootstrap_servers: str = "localhost:9092")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| window_size | int | 60 | Sliding window size (seconds) |
| kafka_bootstrap_servers | str | "localhost:9092" | Kafka server address |

**Methods**:

### `register_metric`

```python
register_metric(name: str, window_size: Optional[int] = None)
```

Register a monitoring metric.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | str | — | Required. Metric name |
| window_size | Optional[int] | None | Window size (overrides default) |

### `add_data_point`

```python
add_data_point(metric: str, value: float, timestamp: Optional[float] = None)
```

Add a data point (auto-registers unregistered metrics, triggers all handlers).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| metric | str | — | Required. Metric name |
| value | float | — | Required. Data value |
| timestamp | Optional[float] | None | Timestamp (defaults to current time) |

### `get_metric_stats`

```python
get_metric_stats(metric: str) -> Dict[str, float]
```

Get statistics for a specific metric.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| metric | str | — | Required. Metric name |

**Returns**: `Dict[str, float]` — Contains count, mean, std, min, max, median, p25, p75

### `get_all_stats`

```python
get_all_stats() -> Dict[str, Dict[str, float]]
```

Get statistics for all metrics.

**Returns**: `Dict[str, Dict[str, float]]` — All metric statistics

### `aggregate`

```python
aggregate(metric: str, func: str = "mean") -> float
```

Aggregate window data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| metric | str | — | Required. Metric name |
| func | str | "mean" | Aggregation function ("mean", "std", "min", "max", "median", "sum", "count", "p25", "p75") |

**Returns**: `float` — Aggregated result

**Exceptions**: `ValueError` — metric not found, no data, or unsupported function

### `process_event`

```python
process_event(event: Dict[str, Any]) -> Dict[str, Any]
```

Unified event processing entry point.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| event | Dict[str, Any] | — | Required. Event dict (must contain metric, value; optional timestamp, metadata) |

**Returns**: `Dict[str, Any]` — Contains metric, value, timestamp, stats, handlers_called

**Exceptions**: `ValueError` — event missing metric or value field

### `add_handler`

```python
add_handler(handler: Callable[[str, float, Optional[float]], None])
```

Add a data handler.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| handler | Callable | — | Required. Handler function (metric, value, timestamp) |

### `start_kafka_consumer`

```python
start_kafka_consumer(topic: str, metric_field: str = "value")
```

Start a Kafka consumer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| topic | str | — | Required. Kafka topic |
| metric_field | str | "value" | Value field name |

### `get_all_metrics`

```python
get_all_metrics() -> List[str]
```

Get all registered metric names.

**Returns**: `List[str]` — Metric name list

### `stop`

```python
stop()
```

Stop processing.

**Example**:

```python
from msra_modules.realtime_analytics import StreamProcessor

sp = StreamProcessor(window_size=60)
sp.register_metric("heart_rate")

for hr in [75, 78, 72, 80, 76]:
    sp.add_data_point("heart_rate", hr)

stats = sp.get_metric_stats("heart_rate")
print(f"HR mean: {stats['mean']:.1f}, std: {stats['std']:.1f}")

result = sp.process_event({"metric": "heart_rate", "value": 120})
print(f"Result: {result['stats']}")
```

---

## AnomalyDetector

> Anomaly detector implementing threshold-based alerting via a rule engine, with sustained duration and cooldown support.

**Signature**:

```python
AnomalyDetector()
```

**Methods**:

### `add_rule`

```python
add_rule(rule: AlertRule)
```

Add an alert rule.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| rule | AlertRule | — | Required. Alert rule |

### `add_default_vital_signs_rules`

```python
add_default_vital_signs_rules()
```

Add default vital signs rules (bradycardia, tachycardia, hypoxemia, hypertension, hypotension, hyperthermia, hypothermia).

### `evaluate`

```python
evaluate(metric: str, value: float, timestamp: Optional[float] = None) -> List[Alert]
```

Evaluate a metric and return triggered alerts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| metric | str | — | Required. Metric name |
| value | float | — | Required. Current value |
| timestamp | Optional[float] | None | Timestamp (defaults to current time) |

**Returns**: `List[Alert]` — Triggered alerts

### `add_alert_handler`

```python
add_alert_handler(handler: Callable[[Alert], None])
```

Add an alert handler.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| handler | Callable[[Alert], None] | — | Required. Handler function |

### `get_rules`

```python
get_rules() -> List[AlertRule]
```

Get all rules.

**Returns**: `List[AlertRule]` — Rule list

### AlertRule Data Class

```python
AlertRule(name: str, metric: str, condition: str, threshold: float,
          threshold_max: Optional[float] = None, level: AlertLevel = AlertLevel.WARNING,
          sustained_seconds: int = 0, cooldown_seconds: int = 300, description: str = "")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | str | — | Rule name |
| metric | str | — | Metric name |
| condition | str | — | Condition ("gt", "lt", "gte", "lte", "range") |
| threshold | float | — | Threshold value |
| threshold_max | Optional[float] | None | Upper bound (for "range" condition) |
| level | AlertLevel | WARNING | Alert level |
| sustained_seconds | int | 0 | Sustained duration requirement (seconds) |
| cooldown_seconds | int | 300 | Cooldown period (seconds) |
| description | str | "" | Description |

### AlertLevel Enum

| Value | Description |
|-------|-------------|
| INFO | Informational |
| WARNING | Warning |
| CRITICAL | Critical |

**Example**:

```python
from msra_modules.realtime_analytics import AnomalyDetector, AlertRule, AlertLevel

detector = AnomalyDetector()
detector.add_default_vital_signs_rules()

alerts = detector.evaluate("heart_rate", 160)
for alert in alerts:
    print(f"[{alert.level.value}] {alert.message}")
```

---

## DetectionResult

> Anomaly detection result data class for multivariate detection methods (e.g., Isolation Forest).

**Attributes**:

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| index | int | — | Data point index in original data |
| is_anomaly | bool | — | Whether it is an anomaly |
| score | float | — | Anomaly score (lower = more anomalous) |
| features | Dict[str, float] | {} | Feature values |
| method | str | "" | Detection method name |
| timestamp | Optional[float] | None | Timestamp |

**Methods**:

### `to_dict`

```python
to_dict() -> Dict
```

Convert to dictionary.

**Returns**: `Dict` — Dictionary containing all attributes

---

## MultivariateDetector

> Multivariate anomaly detector based on Isolation Forest algorithm.

**Signature**:

```python
MultivariateDetector(contamination: float = 0.05, random_state: int = 42)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| contamination | float | 0.05 | Expected anomaly ratio (default 5%) |
| random_state | int | 42 | Random seed for reproducibility |

**Methods**:

### `fit`

```python
fit(data: np.ndarray, feature_names: Optional[List[str]] = None)
```

Train Isolation Forest model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data | np.ndarray | — | Required. Data matrix of shape (n_samples, n_features) |
| feature_names | Optional[List[str]] | None | Feature name list |

**Exceptions**: `ValueError` — input is not 2D; `ImportError` — scikit-learn not installed

### `detect`

```python
detect(data: np.ndarray, feature_names: Optional[List[str]] = None, timestamps: Optional[List[float]] = None) -> List[DetectionResult]
```

Execute multivariate anomaly detection (auto-trains if not fitted).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data | np.ndarray | — | Required. Data matrix of shape (n_samples, n_features) |
| feature_names | Optional[List[str]] | None | Feature name list |
| timestamps | Optional[List[float]] | None | Timestamp list |

**Returns**: `List[DetectionResult]` — Detection results

### `reset`

```python
reset()
```

Reset the detector.

**Example**:

```python
from msra_modules.realtime_analytics import MultivariateDetector
import numpy as np

detector = MultivariateDetector(contamination=0.05)
data = np.random.randn(100, 3)
data[95:] += 5  # Inject anomalies

results = detector.detect(data, feature_names=["hr", "spo2", "bp"])
anomalies = [r for r in results if r.is_anomaly]
print(f"Detected {len(anomalies)} anomalies")
```

---

## AlertSystem

> Alert system supporting multi-channel alert notifications (log, file, webhook, email, Slack).

**Signature**:

```python
AlertSystem(log_file: Optional[str] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| log_file | Optional[str] | None | Log file path |

**Methods**:

### `register_handler`

```python
register_handler(channel: AlertChannel, handler: Callable[[Alert], None])
```

Register an alert handler.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| channel | AlertChannel | — | Required. Alert channel |
| handler | Callable[[Alert], None] | — | Required. Handler function |

### `send_alert`

```python
send_alert(alert: Alert, channels: Optional[List[AlertChannel]] = None)
```

Send an alert.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| alert | Alert | — | Required. Alert event |
| channels | Optional[List[AlertChannel]] | None | Channels to send to (default: all registered) |

### `webhook_handler`

```python
webhook_handler(webhook_url: str) -> Callable[[Alert], None]
```

Create a webhook handler.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| webhook_url | str | — | Required. Webhook URL |

**Returns**: `Callable[[Alert], None]` — Handler function

### `email_handler`

```python
email_handler(smtp_server: str, smtp_port: int, sender: str, password: str, recipients: List[str]) -> Callable[[Alert], None]
```

Create an email handler.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| smtp_server | str | — | Required. SMTP server |
| smtp_port | int | — | Required. SMTP port |
| sender | str | — | Required. Sender email |
| password | str | — | Required. Password |
| recipients | List[str] | — | Required. Recipient list |

**Returns**: `Callable[[Alert], None]` — Handler function

### `slack_handler`

```python
slack_handler(webhook_url: str) -> Callable[[Alert], None]
```

Create a Slack handler.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| webhook_url | str | — | Required. Slack webhook URL |

**Returns**: `Callable[[Alert], None]` — Handler function

### `get_history`

```python
get_history(level: Optional[str] = None, limit: int = 100) -> List[Alert]
```

Get alert history.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| level | Optional[str] | None | Alert level filter |
| limit | int | 100 | Number to return |

**Returns**: `List[Alert]` — Alert list

### `get_statistics`

```python
get_statistics() -> Dict
```

Get alert statistics.

**Returns**: `Dict` — Contains total_alerts, by_level, by_rule

### AlertChannel Enum

| Value | Description |
|-------|-------------|
| LOG | Log |
| WEBHOOK | Webhook |
| EMAIL | Email |
| SLACK | Slack |
| FILE | File |

---

## Alert

> Alert event data class (from alert_system.py).

**Attributes**:

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| rule_name | str | — | Rule name |
| metric | str | — | Metric name |
| value | float | — | Current value |
| level | str | — | Alert level ("info", "warning", "critical") |
| message | str | — | Alert message |
| timestamp | float | — | Timestamp |
| context | Dict | None | Context |

**Methods**:

### `to_dict`

```python
to_dict() -> Dict
```

Convert to dictionary.

### `to_json`

```python
to_json() -> str
```

Convert to JSON string.

**Example**:

```python
from msra_modules.realtime_analytics import AlertSystem, Alert, AlertChannel

system = AlertSystem(log_file="alerts.jsonl")
system.register_handler(AlertChannel.WEBHOOK, system.webhook_handler("https://hooks.example.com/alert"))

alert = Alert(
    rule_name="tachycardia", metric="heart_rate", value=160,
    level="critical", message="HR > 150 bpm", timestamp=1719400000.0
)
system.send_alert(alert)
print(system.get_statistics())
```

---

## RealtimeDashboard

> Realtime dashboard supporting metric monitoring, status evaluation, and Streamlit visualization.

**Signature**:

```python
RealtimeDashboard(max_points: int = 1000, update_interval: float = 1.0)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| max_points | int | 1000 | Maximum data points |
| update_interval | float | 1.0 | Update interval (seconds) |

**Methods**:

### `add_metric`

```python
add_metric(name: str, display_name: Optional[str] = None, unit: str = "",
           warning_range: Optional[tuple] = None, critical_range: Optional[tuple] = None)
```

Add a monitoring metric.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | str | — | Required. Metric name |
| display_name | Optional[str] | None | Display name |
| unit | str | "" | Unit |
| warning_range | Optional[tuple] | None | Warning range |
| critical_range | Optional[tuple] | None | Critical range |

### `update`

```python
update(metric: str, value: float, timestamp: Optional[float] = None)
```

Update metric value.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| metric | str | — | Required. Metric name |
| value | float | — | Required. Value |
| timestamp | Optional[float] | None | Timestamp |

### `add_alert`

```python
add_alert(alert: Dict)
```

Add an alert to the dashboard.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| alert | Dict | — | Required. Alert dictionary |

### `get_dashboard_data`

```python
get_dashboard_data() -> Dict
```

Get dashboard data.

**Returns**: `Dict` — Contains metrics (with data and stats), alerts, timestamp

### `get_metric_status`

```python
get_metric_status(metric: str) -> str
```

Get metric status.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| metric | str | — | Required. Metric name |

**Returns**: `str` — Status ("normal", "warning", "critical", "unknown")

### `export_snapshot`

```python
export_snapshot(filepath: str)
```

Export snapshot to JSON file.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| filepath | str | — | Required. File path |

### `create_streamlit_app`

```python
create_streamlit_app()
```

Create a Streamlit app (requires streamlit and plotly).

**Returns**: Streamlit app object

**Exceptions**: `ImportError` — streamlit/plotly not installed

**Example**:

```python
from msra_modules.realtime_analytics import RealtimeDashboard

dashboard = RealtimeDashboard(max_points=500)
dashboard.add_metric("heart_rate", display_name="Heart Rate", unit="bpm",
                     warning_range=(100, 150), critical_range=(0, 40))

dashboard.update("heart_rate", 75)
print(dashboard.get_metric_status("heart_rate"))  # "normal"
dashboard.export_snapshot("dashboard_snapshot.json")
```

---

## VitalSignsSimulator

> Vital signs simulator generating noisy vital signs data with anomaly injection and streaming support.

**Signature**:

```python
VitalSignsSimulator(baseline_hr: float = 75, baseline_sbp: float = 120,
                     baseline_dbp: float = 80, baseline_spo2: float = 98,
                     baseline_temp: float = 37.0, baseline_rr: float = 16)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| baseline_hr | float | 75 | Baseline heart rate |
| baseline_sbp | float | 120 | Baseline systolic BP |
| baseline_dbp | float | 80 | Baseline diastolic BP |
| baseline_spo2 | float | 98 | Baseline SpO2 |
| baseline_temp | float | 37.0 | Baseline temperature |
| baseline_rr | float | 16 | Baseline respiratory rate |

**Methods**:

### `generate_sample`

```python
generate_sample(timestamp: Optional[float] = None) -> VitalSigns
```

Generate a single vital signs sample.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| timestamp | Optional[float] | None | Timestamp (defaults to current time) |

**Returns**: `VitalSigns` — Vital signs data object

### `trigger_anomaly`

```python
trigger_anomaly(anomaly_type: str, duration: int = 60)
```

Trigger an anomaly.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| anomaly_type | str | — | Required. Anomaly type ("tachycardia", "bradycardia", "hypoxemia", "hypertension", "hypotension", "hyperthermia") |
| duration | int | 60 | Duration (seconds) |

### `stop_anomaly`

```python
stop_anomaly()
```

Stop the anomaly.

### `generate_stream`

```python
generate_stream(duration: int = 3600, interval: float = 1.0,
                callback: Optional[Callable[[VitalSigns], None]] = None) -> List[VitalSigns]
```

Generate a data stream.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| duration | int | 3600 | Duration (seconds) |
| interval | float | 1.0 | Sampling interval (seconds) |
| callback | Optional[Callable] | None | Callback function |

**Returns**: `List[VitalSigns]` — Vital signs list

### `generate_to_kafka`

```python
generate_to_kafka(topic: str, duration: int = 3600, interval: float = 1.0,
                  kafka_servers: str = "localhost:9092")
```

Generate data and send to Kafka.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| topic | str | — | Required. Kafka topic |
| duration | int | 3600 | Duration |
| interval | float | 1.0 | Sampling interval |
| kafka_servers | str | "localhost:9092" | Kafka servers |

### VitalSigns Data Class

| Attribute | Type | Description |
|-----------|------|-------------|
| timestamp | float | Timestamp |
| heart_rate | float | Heart rate |
| systolic_bp | float | Systolic blood pressure |
| diastolic_bp | float | Diastolic blood pressure |
| spo2 | float | SpO2 |
| temperature | float | Temperature |
| respiratory_rate | float | Respiratory rate |

**Example**:

```python
from msra_modules.realtime_analytics import VitalSignsSimulator

sim = VitalSignsSimulator(baseline_hr=75)
sample = sim.generate_sample()
print(f"HR: {sample.heart_rate:.1f}")

sim.trigger_anomaly("tachycardia", duration=30)
abnormal = sim.generate_sample()
print(f"Abnormal HR: {abnormal.heart_rate:.1f}")
```

---

## RealtimeQualityGateChecker

> Realtime analytics quality gate checker encapsulating Gate RT-1 check logic.

**Signature**:

```python
RealtimeQualityGateChecker(study_id: str, project_root: Optional[str] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| study_id | str | — | Required. Study ID |
| project_root | Optional[str] | None | Project root directory (optional) |

**Methods**:

### `run_gate_rt1`

```python
run_gate_rt1(source: Any = None, timestamps: Optional[List[float]] = None,
             detection_rate: Optional[float] = None, window_size: int = 60,
             max_gap_multiplier: float = 2.0, min_rate: float = 0.01,
             max_rate: float = 0.20) -> GateResult
```

Execute Gate RT-1 with 3 checks: data source availability, timestamp continuity, detection sensitivity calibration.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| source | Any | None | Data source object (simulator or other source) |
| timestamps | Optional[List[float]] | None | Timestamp list |
| detection_rate | Optional[float] | None | Anomaly detection rate |
| window_size | int | 60 | Window size (seconds) |
| max_gap_multiplier | float | 2.0 | Max gap multiplier |
| min_rate | float | 0.01 | Minimum detection rate |
| max_rate | float | 0.20 | Maximum detection rate |

**Returns**: `GateResult` — Verdict (PASS / CONDITIONAL / BLOCKED)

### `check_data_source_available`

```python
check_data_source_available(source: Any) -> CheckItemResult
```

Check if data source is available and connected.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| source | Any | — | Required. Data source object |

**Returns**: `CheckItemResult`

### `check_timestamp_continuity`

```python
check_timestamp_continuity(timestamps: List[float], window_size: int = 60,
                           max_gap_multiplier: float = 2.0) -> CheckItemResult
```

Check timestamp continuity.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| timestamps | List[float] | — | Required. Timestamp list (should be sorted) |
| window_size | int | 60 | Window size (seconds) |
| max_gap_multiplier | float | 2.0 | Max gap multiplier |

**Returns**: `CheckItemResult`

### `check_detection_sensitivity`

```python
check_detection_sensitivity(detection_rate: float, min_rate: float = 0.01,
                            max_rate: float = 0.20) -> CheckItemResult
```

Check detection sensitivity calibration.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| detection_rate | float | — | Required. Actual anomaly detection ratio (0.0-1.0) |
| min_rate | float | 0.01 | Minimum acceptable detection rate |
| max_rate | float | 0.20 | Maximum acceptable detection rate |

**Returns**: `CheckItemResult`

**Example**:

```python
from msra_modules.realtime_analytics import RealtimeQualityGateChecker, VitalSignsSimulator

checker = RealtimeQualityGateChecker(study_id="RT-2026-001")
sim = VitalSignsSimulator()

gate_result = checker.run_gate_rt1(
    source=sim,
    timestamps=[1719400000.0 + i for i in range(100)],
    detection_rate=0.05
)
print(f"RT-1 verdict: {gate_result.verdict.value}")
print(f"Pass rate: {gate_result.pass_rate:.1%}")
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

### GateVerdict

| Value | Description |
|-------|-------------|
| PASS | All passed |
| CONDITIONAL | Conditional pass |
| BLOCKED | Blocked |
