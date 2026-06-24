# MSRA Realtime Analytics Module API Reference

| Field | Value |
|-------|-------|
| **Module** | `msra_modules.realtime_analytics` |
| **Version** | 1.2.0 |
| **Date** | 2026-07-13 |
| **Status** | Released (v1.0.0) |
| **Language** | English |

---

## Overview

The Realtime Analytics module provides real-time stream processing, anomaly detection, alert notification, and dashboard functionality. It supports multiple data sources including simulator, Redis, Kafka, and CSV, suitable for real-time vital signs monitoring scenarios.

### Dependencies

- `numpy` — Numerical computing
- `scikit-learn` — Isolation Forest anomaly detection
- `kafka-python` — Kafka consumer/producer (optional)
- `streamlit` / `plotly` — Real-time dashboard (optional)
- `matplotlib` — Visualization

---

## Public API

### `StreamProcessor`

**Description**: Stream data processor supporting sliding window statistics, Kafka consumption, event processing, and aggregation.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `window_size` | `int` | No | `60` | Sliding window size (seconds) |
| `kafka_bootstrap_servers` | `str` | No | `"localhost:9092"` | Kafka server address |

**Methods**:

#### `register_metric(name, window_size=None)`

Register a monitoring metric.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | `str` | Yes | — | Metric name |
| `window_size` | `int` | No | `None` | Window size (overrides default) |

#### `add_data_point(metric, value, timestamp=None)`

Add a data point. Auto-registers the metric if not already registered.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `metric` | `str` | Yes | — | Metric name |
| `value` | `float` | Yes | — | Data value |
| `timestamp` | `float` | No | `None` | Timestamp (defaults to current time) |

#### `get_metric_stats(metric)`

Get window statistics for a specific metric.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `metric` | `str` | Yes | — | Metric name |

- **Returns**: `dict` — contains `count`, `mean`, `std`, `min`, `max`, `median`, `p25`, `p75`

#### `get_all_stats()`

Get statistics for all metrics.

- **Returns**: `dict[str, dict]`

#### `add_handler(handler)`

Add a data handler (callback function).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `handler` | `Callable[[str, float, Optional[float]], None]` | Yes | — | Handler function (metric, value, timestamp) |

#### `start_kafka_consumer(topic, metric_field="value")`

Start a Kafka consumer.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` | `str` | Yes | — | Kafka topic |
| `metric_field` | `str` | No | `"value"` | Value field name |

#### `stop()`

Stop processing.

#### `get_all_metrics()`

Get all registered metric names.

- **Returns**: `list[str]`

#### `aggregate(metric, func="mean")`

Aggregate window data.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `metric` | `str` | Yes | — | Metric name |
| `func` | `str` | No | `"mean"` | Aggregation function (`"mean"`, `"std"`, `"min"`, `"max"`, `"median"`, `"sum"`, `"count"`, `"p25"`, `"p75"`) |

- **Returns**: `float`
- **Exceptions**: `ValueError` (metric not found or unsupported function)

#### `process_event(event)`

Unified event processing entry point.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `event` | `dict` | Yes | — | Event dict, must contain `metric` and `value`, optional `timestamp` |

- **Returns**: `dict` — contains `metric`, `value`, `timestamp`, `stats`, `handlers_called`
- **Exceptions**: `ValueError` (missing `metric` or `value`)

#### `create_faust_app(app_name="msra-stream")`

Create a Faust application.

- **Returns**: `faust.App` or `None` (if Faust not installed)
- **Example**:

```python
from msra_modules.realtime_analytics import StreamProcessor

processor = StreamProcessor(window_size=60)
processor.register_metric("heart_rate")
processor.add_data_point("heart_rate", 75.0)
stats = processor.get_metric_stats("heart_rate")
print(stats["mean"])
```

---

### `SlidingWindowStats`

**Description**: Sliding window statistics calculator.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `window_size` | `int` | No | `60` | Window size (seconds) |

**Methods**:

#### `add(value, timestamp=None)`

Add a data point.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `value` | `float` | Yes | — | Data value |
| `timestamp` | `float` | No | `None` | Timestamp (defaults to current time) |

#### `get_stats()`

Get statistics.

- **Returns**: `dict` — contains `count`, `mean`, `std`, `min`, `max`, `median`, `p25`, `p75`

#### `clear()`

Clear all data.

---

### `AlertLevel`

**Description**: Alert level enum.

| Value | Description |
|-------|-------------|
| `INFO` | Info level |
| `WARNING` | Warning level |
| `CRITICAL` | Critical level |

---

### `AlertRule`

**Description**: Alert rule dataclass.

**Fields**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | `str` | Yes | — | Rule name |
| `metric` | `str` | Yes | — | Metric name |
| `condition` | `str` | Yes | — | Condition (`"gt"`, `"lt"`, `"gte"`, `"lte"`, `"range"`) |
| `threshold` | `float` | Yes | — | Threshold |
| `threshold_max` | `float` | No | `None` | Upper bound (used when `condition="range"`) |
| `level` | `AlertLevel` | No | `AlertLevel.WARNING` | Alert level |
| `sustained_seconds` | `int` | No | `0` | Sustained duration requirement (seconds) |
| `cooldown_seconds` | `int` | No | `300` | Cooldown period (seconds) |
| `description` | `str` | No | `""` | Description |

**Methods**:

#### `evaluate(value)`

Evaluate whether the rule is triggered.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `value` | `float` | Yes | — | Current value |

- **Returns**: `bool`

---

### `Alert` (anomaly_detector)

**Description**: Alert event dataclass (from `anomaly_detector` module).

**Fields**: `rule_name`, `metric`, `value`, `level` (AlertLevel), `message`, `timestamp`, `context`

---

### `DetectionResult`

**Description**: Multivariate anomaly detection result dataclass (for Isolation Forest).

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `index` | `int` | Index in the original data |
| `is_anomaly` | `bool` | Whether it is an anomaly |
| `score` | `float` | Anomaly score (lower = more anomalous) |
| `features` | `dict[str, float]` | Feature values |
| `method` | `str` | Detection method name |
| `timestamp` | `float` | Timestamp (optional) |

**Methods**:

#### `to_dict()`

Convert to dictionary.

- **Returns**: `dict`

---

### `AnomalyDetector`

**Description**: Anomaly detector using a rule engine for real-time anomaly detection, supporting sustained duration and cooldown.

**Parameters**: None.

**Methods**:

#### `add_rule(rule)`

Add an alert rule.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `rule` | `AlertRule` | Yes | — | Alert rule |

#### `add_default_vital_signs_rules()`

Add default vital signs rules (heart rate, SpO2, blood pressure, temperature anomaly detection rules).

#### `evaluate(metric, value, timestamp=None)`

Evaluate a metric and return triggered alerts.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `metric` | `str` | Yes | — | Metric name |
| `value` | `float` | Yes | — | Current value |
| `timestamp` | `float` | No | `None` | Timestamp |

- **Returns**: `list[Alert]`

#### `add_alert_handler(handler)`

Add an alert handler (callback function).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `handler` | `Callable[[Alert], None]` | Yes | — | Handler function |

#### `get_rules()`

Get all rules.

- **Returns**: `list[AlertRule]`
- **Example**:

```python
from msra_modules.realtime_analytics import AnomalyDetector, AlertRule, AlertLevel

detector = AnomalyDetector()
detector.add_default_vital_signs_rules()
alerts = detector.evaluate("heart_rate", 160.0)
for alert in alerts:
    print(alert.rule_name, alert.level, alert.message)
```

---

### `TrendDetector`

**Description**: Trend detector based on CUSUM algorithm for detecting trend changes in data.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `window_size` | `int` | No | `60` | Window size |
| `cusum_threshold` | `float` | No | `5.0` | CUSUM threshold |

**Methods**:

#### `update(value)`

Update the detector.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `value` | `float` | Yes | — | New data point |

- **Returns**: `dict` — contains `status` (`"calibrating"` / `"monitoring"`), `value`, `baseline_mean`, `baseline_std`, `cusum_pos`, `cusum_neg`, `trend_detected`, `trend_direction`

#### `reset()`

Reset the detector.

---

### `MultivariateDetector`

**Description**: Multivariate anomaly detector based on Isolation Forest algorithm. Suitable for analyzing anomaly patterns across multiple vital sign indicators simultaneously.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `contamination` | `float` | No | `0.05` | Expected anomaly ratio (5%) |
| `random_state` | `int` | No | `42` | Random seed |

**Methods**:

#### `fit(data, feature_names=None)`

Train the Isolation Forest model.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data` | `np.ndarray` | Yes | — | Data matrix (n_samples, n_features) |
| `feature_names` | `list[str]` | No | `None` | Feature name list |

#### `detect(data, feature_names=None, timestamps=None)`

Perform multivariate anomaly detection. Auto-trains if model is not fitted.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data` | `np.ndarray` | Yes | — | Data matrix (n_samples, n_features) |
| `feature_names` | `list[str]` | No | `None` | Feature name list |
| `timestamps` | `list[float]` | No | `None` | Timestamp list |

- **Returns**: `list[DetectionResult]`
- **Example**:

```python
from msra_modules.realtime_analytics import MultivariateDetector
import numpy as np

detector = MultivariateDetector(contamination=0.05)
data = np.array([[75, 98, 120], [160, 85, 190], [72, 97, 118]])
results = detector.detect(data, feature_names=["hr", "spo2", "sbp"])
anomalies = [r for r in results if r.is_anomaly]
```

#### `reset()`

Reset the detector.

**Exceptions**: `ImportError` (scikit-learn not installed), `ValueError` (invalid data dimensions)

---

### `AlertChannel`

**Description**: Alert channel enum.

| Value | Description |
|-------|-------------|
| `LOG` | Log |
| `WEBHOOK` | Webhook |
| `EMAIL` | Email |
| `SLACK` | Slack |
| `FILE` | File |

---

### `Alert` (alert_system)

**Description**: Alert event dataclass (from `alert_system` module).

**Fields**: `rule_name`, `metric`, `value`, `level` (str), `message`, `timestamp`, `context`

**Methods**:

#### `to_dict()`

Convert to dictionary.

#### `to_json()`

Convert to JSON string.

---

### `AlertSystem`

**Description**: Alert system supporting multi-channel notification (log, file, webhook, email, Slack).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `log_file` | `str` | No | `None` | Log file path |

**Methods**:

#### `register_handler(channel, handler)`

Register an alert handler.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `channel` | `AlertChannel` | Yes | — | Channel |
| `handler` | `Callable[[Alert], None]` | Yes | — | Handler function |

#### `send_alert(alert, channels=None)`

Send an alert.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `alert` | `Alert` | Yes | — | Alert event |
| `channels` | `list[AlertChannel]` | No | `None` | Channel list (defaults to all registered channels) |

#### `webhook_handler(webhook_url)`

Create a webhook handler.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `webhook_url` | `str` | Yes | — | Webhook URL |

- **Returns**: `Callable[[Alert], None]`

#### `email_handler(smtp_server, smtp_port, sender, password, recipients)`

Create an email handler.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `smtp_server` | `str` | Yes | — | SMTP server |
| `smtp_port` | `int` | Yes | — | SMTP port |
| `sender` | `str` | Yes | — | Sender email |
| `password` | `str` | Yes | — | Password |
| `recipients` | `list[str]` | Yes | — | Recipient list |

- **Returns**: `Callable[[Alert], None]`

#### `slack_handler(webhook_url)`

Create a Slack handler.

- **Returns**: `Callable[[Alert], None]`

#### `get_history(level=None, limit=100)`

Get alert history.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `level` | `str` | No | `None` | Alert level filter |
| `limit` | `int` | No | `100` | Number to return |

- **Returns**: `list[Alert]`

#### `get_statistics()`

Get alert statistics.

- **Returns**: `dict` — contains `total_alerts`, `by_level`, `by_rule`
- **Example**:

```python
from msra_modules.realtime_analytics import AlertSystem, Alert, AlertChannel

system = AlertSystem(log_file="/logs/alerts.jsonl")
system.register_handler(AlertChannel.WEBHOOK, system.webhook_handler("https://hook.example.com"))
alert = Alert(rule_name="tachycardia", metric="heart_rate", value=160.0,
              level="critical", message="HR > 150", timestamp=1234567890.0)
system.send_alert(alert)
```

---

### `VitalSignsSimulator`

**Description**: Vital signs data simulator that generates noisy vital signs data streams and supports triggering anomaly events.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `baseline_hr` | `float` | No | `75` | Baseline heart rate |
| `baseline_sbp` | `float` | No | `120` | Baseline systolic BP |
| `baseline_dbp` | `float` | No | `80` | Baseline diastolic BP |
| `baseline_spo2` | `float` | No | `98` | Baseline SpO2 |
| `baseline_temp` | `float` | No | `37.0` | Baseline temperature |
| `baseline_rr` | `float` | No | `16` | Baseline respiratory rate |

**Methods**:

#### `generate_sample(timestamp=None)`

Generate a single sample.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `timestamp` | `float` | No | `None` | Timestamp |

- **Returns**: `VitalSigns`

#### `trigger_anomaly(anomaly_type, duration=60)`

Trigger an anomaly. Supported types: `"tachycardia"`, `"bradycardia"`, `"hypoxemia"`, `"hypertension"`, `"hypotension"`, `"hyperthermia"`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `anomaly_type` | `str` | Yes | — | Anomaly type |
| `duration` | `int` | No | `60` | Duration (seconds) |

#### `stop_anomaly()`

Stop the anomaly.

#### `generate_stream(duration=3600, interval=1.0, callback=None)`

Generate a data stream.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `duration` | `int` | No | `3600` | Duration (seconds) |
| `interval` | `float` | No | `1.0` | Sampling interval (seconds) |
| `callback` | `Callable[[VitalSigns], None]` | No | `None` | Callback function |

- **Returns**: `list[VitalSigns]`

#### `generate_to_kafka(topic, duration=3600, interval=1.0, kafka_servers="localhost:9092")`

Generate data and send to Kafka.
- **Example**:

```python
from msra_modules.realtime_analytics import VitalSignsSimulator

simulator = VitalSignsSimulator(baseline_hr=75, baseline_sbp=120)
sample = simulator.generate_sample()
print(sample.heart_rate, sample.spo2)

# Trigger tachycardia anomaly
simulator.trigger_anomaly("tachycardia", duration=60)
```

---

### `VitalSigns`

**Description**: Vital signs data class.

**Fields**: `timestamp`, `heart_rate`, `systolic_bp`, `diastolic_bp`, `spo2`, `temperature`, `respiratory_rate`

**Methods**:

#### `to_dict()`

Convert to dictionary.

#### `to_json()`

Convert to JSON string.

---

### `RealtimeDashboard`

**Description**: Real-time dashboard supporting metric monitoring, status determination, snapshot export, and Streamlit application.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `max_points` | `int` | No | `1000` | Maximum data points |
| `update_interval` | `float` | No | `1.0` | Update interval (seconds) |

**Methods**:

#### `add_metric(name, display_name=None, unit="", warning_range=None, critical_range=None)`

Add a monitoring metric.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | `str` | Yes | — | Metric name |
| `display_name` | `str` | No | `None` | Display name |
| `unit` | `str` | No | `""` | Unit |
| `warning_range` | `tuple` | No | `None` | Warning range |
| `critical_range` | `tuple` | No | `None` | Critical range |

#### `update(metric, value, timestamp=None)`

Update a metric value.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `metric` | `str` | Yes | — | Metric name |
| `value` | `float` | Yes | — | Value |
| `timestamp` | `float` | No | `None` | Timestamp |

#### `add_alert(alert)`

Add an alert.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `alert` | `dict` | Yes | — | Alert dictionary |

#### `get_dashboard_data()`

Get dashboard data.

- **Returns**: `dict` — contains `metrics` (data and stats for each metric), `alerts`, `timestamp`

#### `get_metric_status(metric)`

Get metric status.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `metric` | `str` | Yes | — | Metric name |

- **Returns**: `str` — `"normal"`, `"warning"`, `"critical"`, `"unknown"`

#### `export_snapshot(filepath)`

Export snapshot to a JSON file.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filepath` | `str` | Yes | — | File path |

#### `create_streamlit_app()`

Create a Streamlit application.

- **Returns**: Streamlit app object
- **Exceptions**: `ImportError` (streamlit/plotly not installed)

---

### `ReportGenerator`

**Description**: Report generator supporting HTML and Markdown formats for imaging, bioinformatics, and monitoring reports.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `output_dir` | `str` | No | `"reports"` | Output directory |

**Methods**:

#### `generate_imaging_report(patient_info, imaging_findings, radiomics_features, output_format="html")`

Generate an imaging analysis report.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `patient_info` | `dict` | Yes | — | Patient information |
| `imaging_findings` | `dict` | Yes | — | Imaging findings |
| `radiomics_features` | `dict` | Yes | — | Radiomics features |
| `output_format` | `str` | No | `"html"` | Output format (`"html"` or `"markdown"`) |

- **Returns**: `str` — report file path

#### `generate_bio_report(sample_info, qc_summary, analysis_results, output_format="html")`

Generate a bioinformatics report.

- **Returns**: `str` — report file path

#### `generate_monitoring_report(duration, stats, alerts, output_format="html")`

Generate a real-time monitoring report.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `duration` | `str` | Yes | — | Monitoring duration |
| `stats` | `dict` | Yes | — | Statistics data |
| `alerts` | `list[dict]` | Yes | — | Alert list |
| `output_format` | `str` | No | `"html"` | Output format |

- **Returns**: `str` — report file path

---

### `RealtimeQualityGateChecker`

**Description**: Realtime analytics quality gate checker implementing Gate RT-1 (real-time data quality gate).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `study_id` | `str` | Yes | — | Study ID |
| `project_root` | `str` | No | `None` | Project root directory |

**Methods**:

#### `run_gate_rt1(source=None, timestamps=None, detection_rate=None, window_size=60, max_gap_multiplier=2.0, min_rate=0.01, max_rate=0.20)`

Execute Gate RT-1 with all 3 checks: data source availability, timestamp continuity, anomaly detection sensitivity calibration.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | `Any` | No | `None` | Data source object (simulator or other source) |
| `timestamps` | `list[float]` | No | `None` | Timestamp list |
| `detection_rate` | `float` | No | `None` | Anomaly detection rate |
| `window_size` | `int` | No | `60` | Window size (seconds) |
| `max_gap_multiplier` | `float` | No | `2.0` | Max gap multiplier |
| `min_rate` | `float` | No | `0.01` | Minimum detection rate |
| `max_rate` | `float` | No | `0.20` | Maximum detection rate |

- **Returns**: `GateResult` — verdict (`PASS` / `CONDITIONAL` / `BLOCKED`)
- **Example**:

```python
from msra_modules.realtime_analytics import RealtimeQualityGateChecker, VitalSignsSimulator

simulator = VitalSignsSimulator()
checker = RealtimeQualityGateChecker(study_id="RT-2026-001")
result = checker.run_gate_rt1(source=simulator, detection_rate=0.05)
print(result.verdict)
```

---

## Full Usage Example

```python
from msra_modules.realtime_analytics import (
    StreamProcessor, AnomalyDetector, AlertSystem, AlertChannel,
    VitalSignsSimulator, RealtimeDashboard, RealtimeQualityGateChecker,
)

# 1. Create simulator
simulator = VitalSignsSimulator(baseline_hr=75, baseline_sbp=120)

# 2. Create stream processor
processor = StreamProcessor(window_size=60)
processor.register_metric("heart_rate")
processor.register_metric("spo2")

# 3. Create anomaly detector
detector = AnomalyDetector()
detector.add_default_vital_signs_rules()

# 4. Create alert system
alert_system = AlertSystem(log_file="/logs/alerts.jsonl")

# 5. Create dashboard
dashboard = RealtimeDashboard()
dashboard.add_metric("heart_rate", display_name="HR", unit="bpm",
                     warning_range=(100, 150), critical_range=(0, 40))

# 6. Simulate data stream
for i in range(100):
    sample = simulator.generate_sample()
    processor.add_data_point("heart_rate", sample.heart_rate)
    alerts = detector.evaluate("heart_rate", sample.heart_rate)
    for alert in alerts:
        alert_system.send_alert(alert)
    dashboard.update("heart_rate", sample.heart_rate)

# 7. Quality gate
checker = RealtimeQualityGateChecker(study_id="RT-2026-001")
result = checker.run_gate_rt1(source=simulator, detection_rate=0.05)
```
