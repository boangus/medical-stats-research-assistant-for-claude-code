# MSRA Realtime Analytics Module User Tutorial

> **Module Version**: v1.2.0 | **Document Date**: 2026-06-25 | **Status**: Stable
> **Command Entry**: `/msra-rt` | **MSRA Version**: v1.0.0+

---

## 1. Module Overview & Use Cases

### Overview

The MSRA Realtime Analytics module provides real-time vital signs monitoring capabilities, covering the complete chain from data stream ingestion, sliding window statistics, anomaly detection, alert triggering, to report generation. It supports four data source types — simulator, Redis, Kafka, and CSV — suitable for clinical monitoring, post-operative observation, emergency surveillance, and more.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| Stream Processing | Sliding window statistics (mean/std/min/max/median) via `StreamProcessor` |
| Anomaly Detection | Rule engine + Isolation Forest multivariate detection via `AnomalyDetector`, `MultivariateDetector` |
| Trend Detection | CUSUM trend detection via `TrendDetector` |
| Alert System | Multi-channel dispatch (Log/File/Webhook/Slack/Email) via `AlertSystem` |
| Real-time Dashboard | Monitoring visualization via `RealtimeDashboard` |
| Data Simulator | Vital signs simulator via `VitalSignsSimulator` |
| Quality Gate | Gate RT-1 (realtime data quality) via `RealtimeQualityGateChecker` |

### Use Cases

- ICU patient vital signs real-time monitoring and alerting
- Post-operative recovery monitoring
- Emergency triage real-time metric tracking
- Adverse event real-time detection in clinical trials
- Using the simulator to validate monitoring pipelines during development/testing

---

## 2. Installation

### Install realtime_analytics extra dependencies

```bash
pip install -e ".[realtime_analytics]"
```

### Core Dependencies

```toml
numpy >= 1.24          # Numerical computing
scipy >= 1.10          # Scientific computing
scikit-learn >= 1.3    # Isolation Forest / DBSCAN
# Optional dependencies
redis >= 5.0           # Redis data source
kafka-python >= 2.0    # Kafka data source
plotly >= 5.18         # Interactive charts
streamlit >= 1.30      # Web dashboard (P2)
```

### Verify Installation

```bash
python -c "from msra_modules.realtime_analytics import StreamProcessor, AnomalyDetector, AlertSystem, VitalSignsSimulator, RealtimeQualityGateChecker; print('OK')"
```

---

## 3. Data Source Configuration

### Supported Data Source Types

| Type | Parameter | Description | Use Case |
|------|-----------|-------------|----------|
| Simulator | `--source simulator` | Built-in vital signs simulator | Dev/test, demos |
| Redis | `--source redis://host:port` | Redis Stream data source | Production, distributed |
| Kafka | `--source kafka://host:port/topic` | Kafka Topic consumer | Production, high-throughput |
| CSV | `--source csv --data vitals.csv` | CSV file time-series replay | Offline analysis, historical data |

### Simulator Mode (Default)

```python
from msra_modules.realtime_analytics import VitalSignsSimulator, VitalSigns

# Create simulator (default: heart rate, SpO2, systolic BP, temperature)
simulator = VitalSignsSimulator(
    interval=1.0,        # Sampling interval (seconds)
    duration=60,         # Monitoring duration (seconds)
    anomaly_rate=0.05,   # Anomaly injection rate
)

# Generate data stream
for data_point in simulator.stream():
    print(f"[{data_point.timestamp:.1f}] HR={data_point.heart_rate:.0f} "
          f"SpO2={data_point.spo2:.0f} SBP={data_point.systolic_bp:.0f}")
```

### CSV Replay Mode

The CSV file must contain a `timestamp` column and metric columns:

```csv
timestamp,heart_rate,spo2,systolic_bp,temperature
0.0,72,98,120,36.5
1.0,73,98,122,36.5
2.0,75,97,125,36.6
...
```

---

## 4. Real-time Monitoring Workflow

### Launch via Command

```
# Simulator + ICU preset rules, 60-second monitoring
/msra-rt --source simulator --preset icu --duration 60

# CSV replay
/msra-rt --source csv --data vitals.csv

# Redis data source
/msra-rt --source redis://localhost:6379
```

### Python API Complete Workflow

```python
from msra_modules.realtime_analytics import (
    StreamProcessor, AnomalyDetector, AlertSystem,
    VitalSignsSimulator, RealtimeQualityGateChecker,
    AlertRule, AlertLevel,
)

# Phase 0: Configuration
simulator = VitalSignsSimulator(interval=1.0, duration=60)
processor = StreamProcessor(window_size=60)
detector = AnomalyDetector()
alert_system = AlertSystem()

# Register monitoring metrics
processor.register_metric("heart_rate")
processor.register_metric("spo2")
processor.register_metric("systolic_bp")

# Phase 1: Data stream ingestion + Gate RT-1 (items 1+2)
checker = RealtimeQualityGateChecker(study_id="RT-2026-001")

# Receive first few data points to verify connection
first_points = []
for i, point in enumerate(simulator.stream()):
    first_points.append(point)
    if i >= 5:
        break

gate_result = checker.run_gate_rt1_first2(
    data_points=first_points,
    expected_interval=1.0,
)
print(f"Gate RT-1 (connection): {gate_result.verdict}")

# Phase 2: Real-time monitoring
for point in simulator.stream():
    # Stream processing
    processor.add_data_point("heart_rate", point.heart_rate, point.timestamp)
    processor.add_data_point("spo2", point.spo2, point.timestamp)
    processor.add_data_point("systolic_bp", point.systolic_bp, point.timestamp)

    # Anomaly detection
    for metric in ["heart_rate", "spo2", "systolic_bp"]:
        stats = processor.get_stats(metric)
        detection = detector.detect(metric, point.value, stats)
        if detection.is_anomaly:
            alert_system.trigger_alert(
                metric=metric,
                value=point.value,
                level=AlertLevel.WARNING,
                message=f"{metric} anomaly: {point.value:.1f}",
            )

# Phase 3: Result review + Gate RT-1 (item 3)
gate_result_3 = checker.run_gate_rt1_item3(
    detection_results=detector.get_results(),
)
print(f"Gate RT-1 (sensitivity): {gate_result_3.verdict}")

# Phase 4: Report
stats_summary = processor.get_all_stats()
alert_history = alert_system.get_history()
print(f"Monitoring complete. Alerts: {len(alert_history)}")
```

---

## 5. Anomaly Detection Configuration

### Rule Engine (Threshold-based)

```python
from msra_modules.realtime_analytics import AnomalyDetector, AlertRule, AlertLevel

detector = AnomalyDetector()

# Add anomaly detection rules
detector.add_rule(AlertRule(
    name="bradycardia",
    metric="heart_rate",
    condition="lt",          # Less than threshold
    threshold=50,            # HR < 50
    level=AlertLevel.CRITICAL,
    sustained_seconds=5,     # Must persist for 5 seconds
    cooldown_seconds=300,    # 5-minute cooldown
    description="Bradycardia",
))

detector.add_rule(AlertRule(
    name="tachycardia",
    metric="heart_rate",
    condition="gt",          # Greater than threshold
    threshold=120,           # HR > 120
    level=AlertLevel.WARNING,
    sustained_seconds=5,
    cooldown_seconds=300,
    description="Tachycardia",
))

detector.add_rule(AlertRule(
    name="hypoxia",
    metric="spo2",
    condition="lt",
    threshold=90,            # SpO2 < 90%
    level=AlertLevel.CRITICAL,
    sustained_seconds=3,
    cooldown_seconds=120,
    description="Hypoxemia",
))

detector.add_rule(AlertRule(
    name="bp_abnormal",
    metric="systolic_bp",
    condition="range",       # Out of range
    threshold=90,            # Lower bound
    threshold_max=180,       # Upper bound
    level=AlertLevel.WARNING,
    sustained_seconds=10,
    cooldown_seconds=300,
    description="Abnormal blood pressure",
))
```

### Multivariate Anomaly Detection (Isolation Forest)

```python
from msra_modules.realtime_analytics import MultivariateDetector

# Multivariate detector (considers relationships between metrics)
mv_detector = MultivariateDetector(
    method="isolation_forest",
    contamination=0.05,    # Expected anomaly ratio
    window_size=100,       # Training window size
)

# Input multi-metric data
multi_metrics = {
    "heart_rate": [72, 73, 75, 120, 74, 73, ...],
    "spo2": [98, 98, 97, 85, 98, 98, ...],
    "systolic_bp": [120, 122, 125, 160, 121, 120, ...],
}

results = mv_detector.detect(multi_metrics)
for r in results:
    if r.is_anomaly:
        print(f"Anomaly at index {r.index}: score={r.score:.4f}")
```

### Trend Detection (CUSUM)

```python
from msra_modules.realtime_analytics import TrendDetector

trend_detector = TrendDetector(threshold=5.0)

# Detect trend changes point by point
for value in heart_rate_stream:
    trend = trend_detector.update(value)
    if trend.is_trending:
        print(f"Trend detected: {trend.direction}, CUSUM={trend.cusum:.2f}")
```

---

## 6. Alert Rule Customization

### Preset Rule Templates

| Template | Metrics | Rule Summary |
|----------|---------|--------------|
| `icu` | HR, SpO2, SBP, Temp | HR 40-150, SpO2>90, SBP 90-180, Temp 36-38 |
| `postop` | HR, SpO2, SBP, Temp | Post-operative monitoring (stricter) |
| `emergency` | HR, SpO2, SBP | Emergency triage (fast response) |

### Using Presets

```
/msra-rt --source simulator --preset icu --duration 3600
```

### Custom Alert Channels

```python
from msra_modules.realtime_analytics import AlertSystem, AlertChannel

alert_system = AlertSystem()

# Add alert channels
alert_system.add_channel(AlertChannel.LOG, level=AlertLevel.INFO)       # Log all levels
alert_system.add_channel(AlertChannel.FILE, filepath="alerts.log")       # Write to file
alert_system.add_channel(AlertChannel.WEBHOOK, url="https://hook.example.com/alert")
alert_system.add_channel(AlertChannel.SLACK, webhook_url="https://hooks.slack.com/...")
alert_system.add_channel(AlertChannel.EMAIL, recipients=["oncall@hospital.org"])
```

### Alert Cooldown and Sustained Duration

Each rule supports two time-filtering parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `sustained_seconds` | Anomaly must persist for the specified duration before triggering | HR >120 for 5 seconds before alert |
| `cooldown_seconds` | Minimum interval between two alerts for the same rule | No repeat alerts within 5 minutes |

---

## 7. Quality Gates

### Gate RT-1 — Real-time Data Quality Gate

> Executed in Phase 1 (items 1+2) and Phase 3 (item 3), validates data stream and detection quality.
> Implementation: `msra_modules/realtime_analytics/quality_gates.py` → `RealtimeQualityGateChecker`

| # | Check Item | Critical | Pass Criteria |
|---|------------|----------|---------------|
| 1 | Data stream connection | 🔑 | At least 1 data point received within 5 seconds |
| 2 | Timestamp continuity | 🔑 | Adjacent point interval < sampling interval × 5 |
| 3 | Anomaly detection sensitivity calibration | | Detection rate between 1%-20% |

**Verdict Rules**:
- **PASS**: 3/3 checks passed
- **CONDITIONAL**: 2/3 passed and all 🔑 passed
- **BLOCKED**: ≤ 1/3 passed or any 🔑 failed (**blocks the pipeline**)

### Python Usage Example

```python
from msra_modules.realtime_analytics import RealtimeQualityGateChecker

checker = RealtimeQualityGateChecker(study_id="RT-2026-001")

# Phase 1: Items 1+2 check (connection + timestamp continuity)
result_12 = checker.run_gate_rt1_first2(
    data_points=received_points,
    expected_interval=1.0,
)
print(f"RT-1 (connection): {result_12.verdict}")

# Phase 3: Item 3 check (sensitivity calibration)
result_3 = checker.run_gate_rt1_item3(
    detection_results=detector.get_all_results(),
    total_points=total_data_points,
)
print(f"RT-1 (sensitivity): {result_3.verdict}")
```

---

## 8. Report Export

### Generate Monitoring Report

```python
from msra_modules.realtime_analytics import RealtimeDashboard, ReportGenerator

# Generate report
report_gen = ReportGenerator()
report_path = report_gen.generate(
    stats_summary=processor.get_all_stats(),
    alert_history=alert_system.get_history(),
    anomaly_results=detector.get_all_results(),
    output_path="MSRA/reports/rt_monitoring_20260625.html",
)
print(f"Report saved to: {report_path}")
```

### Report Contents

| Section | Content |
|---------|---------|
| Monitoring Summary | Duration, sampling interval, metric list |
| Statistics Summary | Mean/std/extrema/trend for each metric |
| Alert History | Grouped by level, with trigger time/rule/current value |
| Anomaly Detection Results | Rule triggers + multivariate detection |
| Quality Gate Report | Gate RT-1 three-item check results |

### Command-Line Export

```
/msra-rt --source simulator --preset icu --duration 600 --export-report
```

---

## 9. FAQ

### Q1: The simulator data looks too regular. How to fix it?

The simulator injects 5% anomalous data by default. You can adjust the `anomaly_rate` parameter:

```python
simulator = VitalSignsSimulator(anomaly_rate=0.1)  # 10% anomaly rate
```

### Q2: Redis connection fails?

1. Verify Redis is running: `redis-cli ping`
2. Check the connection string format: `redis://host:port`
3. If connection fails, the system will block (Gate RT-1 item 1) and suggest switching to simulator mode

### Q3: Isolation Forest detects everything as anomalous?

- Check if the `contamination` parameter is too high (default 0.05)
- Ensure the training window contains enough normal data
- Verify input data is properly standardized

### Q4: Alerts are too frequent?

1. Increase `sustained_seconds` (duration requirement)
2. Increase `cooldown_seconds` (cooldown period)
3. Adjust `AlertLevel` to only trigger external notifications for CRITICAL level

### Q5: CSV replay is too slow?

CSV replay plays row by row in time series. You can accelerate replay using the `--interval 0` parameter:

```
/msra-rt --source csv --data vitals.csv --interval 0
```

### Q6: How to feed monitoring data into the cross_domain module?

`StreamProcessor` has a reserved metric export interface:

```python
metrics_export = processor.export_metrics_for_cross_domain()
# Export format: {metric_name: [values], ...}
# Can be directly passed to /msra-cross's RealtimePredictionModel
```

---

> **Related Docs**: [SKILL.md](../../skills/realtime-monitor/SKILL.md) | [Module PRD](../prd/msra_rt_prd.md) | [MSRA Docs Home](../system_design.md)
