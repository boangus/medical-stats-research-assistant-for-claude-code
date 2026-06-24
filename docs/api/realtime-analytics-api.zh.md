# MSRA Realtime Analytics 模块 API 参考

| 字段 | 值 |
|------|-----|
| **模块** | `msra_modules.realtime_analytics` |
| **版本** | 1.2.0 |
| **日期** | 2026-07-13 |
| **状态** | Released (v1.0.0) |
| **语言** | 中文 |

---

## 概述

Realtime Analytics 模块提供实时流处理、异常检测、告警通知和仪表盘功能。支持模拟器、Redis、Kafka、CSV 等多种数据源，适用于生命体征实时监测场景。

### 依赖

- `numpy` — 数值计算
- `scikit-learn` — Isolation Forest 异常检测
- `kafka-python` — Kafka 消费者/生产者（可选）
- `streamlit` / `plotly` — 实时仪表盘（可选）
- `matplotlib` — 可视化

---

## 公开 API

### `StreamProcessor`

**描述**: 流数据处理器，支持滑动窗口统计、Kafka 消费、事件处理和聚合计算。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `window_size` | `int` | 否 | `60` | 滑动窗口大小（秒） |
| `kafka_bootstrap_servers` | `str` | 否 | `"localhost:9092"` | Kafka 服务器地址 |

**方法**:

#### `register_metric(name, window_size=None)`

注册监控指标。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `name` | `str` | 是 | — | 指标名称 |
| `window_size` | `int` | 否 | `None` | 窗口大小（覆盖默认值） |

#### `add_data_point(metric, value, timestamp=None)`

添加数据点。如果指标未注册则自动注册。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `metric` | `str` | 是 | — | 指标名称 |
| `value` | `float` | 是 | — | 数据值 |
| `timestamp` | `float` | 否 | `None` | 时间戳（默认当前时间） |

#### `get_metric_stats(metric)`

获取指定指标的窗口统计。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `metric` | `str` | 是 | — | 指标名称 |

- **返回值**: `dict` — 含 `count`, `mean`, `std`, `min`, `max`, `median`, `p25`, `p75`

#### `get_all_stats()`

获取所有指标的统计。

- **返回值**: `dict[str, dict]`

#### `add_handler(handler)`

添加数据处理器（回调函数）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `handler` | `Callable[[str, float, Optional[float]], None]` | 是 | — | 处理函数 (metric, value, timestamp) |

#### `start_kafka_consumer(topic, metric_field="value")`

启动 Kafka 消费者。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `topic` | `str` | 是 | — | Kafka 主题 |
| `metric_field` | `str` | 否 | `"value"` | 值字段名 |

#### `stop()`

停止处理。

#### `get_all_metrics()`

获取所有已注册的指标名。

- **返回值**: `list[str]`

#### `aggregate(metric, func="mean")`

对窗口数据进行聚合计算。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `metric` | `str` | 是 | — | 指标名称 |
| `func` | `str` | 否 | `"mean"` | 聚合函数（`"mean"`, `"std"`, `"min"`, `"max"`, `"median"`, `"sum"`, `"count"`, `"p25"`, `"p75"`） |

- **返回值**: `float`
- **异常**: `ValueError`（指标不存在或函数不支持）

#### `process_event(event)`

统一事件处理入口。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `event` | `dict` | 是 | — | 事件字典，须含 `metric` 和 `value`，可选 `timestamp` |

- **返回值**: `dict` — 含 `metric`, `value`, `timestamp`, `stats`, `handlers_called`
- **异常**: `ValueError`（缺少 `metric` 或 `value`）

#### `create_faust_app(app_name="msra-stream")`

创建 Faust 应用。

- **返回值**: `faust.App` 或 `None`（Faust 未安装时）
- **示例**:

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

**描述**: 滑动窗口统计器。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `window_size` | `int` | 否 | `60` | 窗口大小（秒） |

**方法**:

#### `add(value, timestamp=None)`

添加数据点。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `value` | `float` | 是 | — | 数据值 |
| `timestamp` | `float` | 否 | `None` | 时间戳（默认当前时间） |

#### `get_stats()`

获取统计指标。

- **返回值**: `dict` — 含 `count`, `mean`, `std`, `min`, `max`, `median`, `p25`, `p75`

#### `clear()`

清空数据。

---

### `AlertLevel`

**描述**: 警报级别枚举。

| 值 | 说明 |
|----|------|
| `INFO` | 信息级别 |
| `WARNING` | 警告级别 |
| `CRITICAL` | 严重级别 |

---

### `AlertRule`

**描述**: 警报规则数据类。

**字段**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `name` | `str` | 是 | — | 规则名称 |
| `metric` | `str` | 是 | — | 指标名称 |
| `condition` | `str` | 是 | — | 条件（`"gt"`, `"lt"`, `"gte"`, `"lte"`, `"range"`） |
| `threshold` | `float` | 是 | — | 阈值 |
| `threshold_max` | `float` | 否 | `None` | 范围上限（`condition="range"` 时使用） |
| `level` | `AlertLevel` | 否 | `AlertLevel.WARNING` | 警报级别 |
| `sustained_seconds` | `int` | 否 | `0` | 持续时间要求（秒） |
| `cooldown_seconds` | `int` | 否 | `300` | 冷却时间（秒） |
| `description` | `str` | 否 | `""` | 描述 |

**方法**:

#### `evaluate(value)`

评估规则是否触发。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `value` | `float` | 是 | — | 当前值 |

- **返回值**: `bool`

---

### `Alert` (anomaly_detector)

**描述**: 警报事件数据类（来自 `anomaly_detector` 模块）。

**字段**: `rule_name`, `metric`, `value`, `level` (AlertLevel), `message`, `timestamp`, `context`

---

### `DetectionResult`

**描述**: 多变量异常检测结果数据类（用于 Isolation Forest）。

**字段**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `index` | `int` | 数据点在原始数据中的索引 |
| `is_anomaly` | `bool` | 是否为异常 |
| `score` | `float` | 异常分数（越低越异常） |
| `features` | `dict[str, float]` | 特征值 |
| `method` | `str` | 检测方法名称 |
| `timestamp` | `float` | 时间戳（可选） |

**方法**:

#### `to_dict()`

转换为字典。

- **返回值**: `dict`

---

### `AnomalyDetector`

**描述**: 异常检测器，基于规则引擎进行实时异常检测，支持持续时间要求和冷却时间。

**参数**: 无构造参数。

**方法**:

#### `add_rule(rule)`

添加警报规则。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `rule` | `AlertRule` | 是 | — | 警报规则 |

#### `add_default_vital_signs_rules()`

添加默认生命体征规则（心率、血氧、血压、体温的异常检测规则）。

#### `evaluate(metric, value, timestamp=None)`

评估指标，返回触发的警报列表。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `metric` | `str` | 是 | — | 指标名称 |
| `value` | `float` | 是 | — | 当前值 |
| `timestamp` | `float` | 否 | `None` | 时间戳 |

- **返回值**: `list[Alert]`

#### `add_alert_handler(handler)`

添加警报处理器（回调函数）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `handler` | `Callable[[Alert], None]` | 是 | — | 处理函数 |

#### `get_rules()`

获取所有规则。

- **返回值**: `list[AlertRule]`
- **示例**:

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

**描述**: 趋势检测器，基于 CUSUM 算法检测数据趋势变化。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `window_size` | `int` | 否 | `60` | 窗口大小 |
| `cusum_threshold` | `float` | 否 | `5.0` | CUSUM 阈值 |

**方法**:

#### `update(value)`

更新检测器。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `value` | `float` | 是 | — | 新数据点 |

- **返回值**: `dict` — 含 `status` (`"calibrating"` / `"monitoring"`), `value`, `baseline_mean`, `baseline_std`, `cusum_pos`, `cusum_neg`, `trend_detected`, `trend_direction`

#### `reset()`

重置检测器。

---

### `MultivariateDetector`

**描述**: 多变量异常检测器，基于 Isolation Forest 算法。适用于同时分析多个生命体征指标的异常模式。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `contamination` | `float` | 否 | `0.05` | 预期异常比例（5%） |
| `random_state` | `int` | 否 | `42` | 随机种子 |

**方法**:

#### `fit(data, feature_names=None)`

训练 Isolation Forest 模型。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `data` | `np.ndarray` | 是 | — | 数据矩阵 (n_samples, n_features) |
| `feature_names` | `list[str]` | 否 | `None` | 特征名称列表 |

#### `detect(data, feature_names=None, timestamps=None)`

执行多变量异常检测。如果模型未训练则自动训练。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `data` | `np.ndarray` | 是 | — | 数据矩阵 (n_samples, n_features) |
| `feature_names` | `list[str]` | 否 | `None` | 特征名称列表 |
| `timestamps` | `list[float]` | 否 | `None` | 时间戳列表 |

- **返回值**: `list[DetectionResult]`
- **示例**:

```python
from msra_modules.realtime_analytics import MultivariateDetector
import numpy as np

detector = MultivariateDetector(contamination=0.05)
data = np.array([[75, 98, 120], [160, 85, 190], [72, 97, 118]])
results = detector.detect(data, feature_names=["hr", "spo2", "sbp"])
anomalies = [r for r in results if r.is_anomaly]
```

#### `reset()`

重置检测器。

**异常**: `ImportError`（scikit-learn 未安装）、`ValueError`（数据维度不符）

---

### `AlertChannel`

**描述**: 警报渠道枚举。

| 值 | 说明 |
|----|------|
| `LOG` | 日志 |
| `WEBHOOK` | Webhook |
| `EMAIL` | 邮件 |
| `SLACK` | Slack |
| `FILE` | 文件 |

---

### `Alert` (alert_system)

**描述**: 警报事件数据类（来自 `alert_system` 模块）。

**字段**: `rule_name`, `metric`, `value`, `level` (str), `message`, `timestamp`, `context`

**方法**:

#### `to_dict()`

转换为字典。

#### `to_json()`

转换为 JSON 字符串。

---

### `AlertSystem`

**描述**: 警报系统，支持多渠道通知（日志、文件、Webhook、邮件、Slack）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `log_file` | `str` | 否 | `None` | 日志文件路径 |

**方法**:

#### `register_handler(channel, handler)`

注册警报处理器。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `channel` | `AlertChannel` | 是 | — | 渠道 |
| `handler` | `Callable[[Alert], None]` | 是 | — | 处理函数 |

#### `send_alert(alert, channels=None)`

发送警报。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `alert` | `Alert` | 是 | — | 警报事件 |
| `channels` | `list[AlertChannel]` | 否 | `None` | 发送渠道列表（默认所有已注册渠道） |

#### `webhook_handler(webhook_url)`

创建 Webhook 处理器。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `webhook_url` | `str` | 是 | — | Webhook URL |

- **返回值**: `Callable[[Alert], None]`

#### `email_handler(smtp_server, smtp_port, sender, password, recipients)`

创建邮件处理器。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `smtp_server` | `str` | 是 | — | SMTP 服务器 |
| `smtp_port` | `int` | 是 | — | SMTP 端口 |
| `sender` | `str` | 是 | — | 发件人 |
| `password` | `str` | 是 | — | 密码 |
| `recipients` | `list[str]` | 是 | — | 收件人列表 |

- **返回值**: `Callable[[Alert], None]`

#### `slack_handler(webhook_url)`

创建 Slack 处理器。

- **返回值**: `Callable[[Alert], None]`

#### `get_history(level=None, limit=100)`

获取警报历史。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `level` | `str` | 否 | `None` | 警报级别筛选 |
| `limit` | `int` | 否 | `100` | 返回数量 |

- **返回值**: `list[Alert]`

#### `get_statistics()`

获取警报统计。

- **返回值**: `dict` — 含 `total_alerts`, `by_level`, `by_rule`
- **示例**:

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

**描述**: 生命体征数据模拟器，可生成带噪声的生命体征数据流，支持触发异常事件。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `baseline_hr` | `float` | 否 | `75` | 基线心率 |
| `baseline_sbp` | `float` | 否 | `120` | 基线收缩压 |
| `baseline_dbp` | `float` | 否 | `80` | 基线舒张压 |
| `baseline_spo2` | `float` | 否 | `98` | 基线血氧 |
| `baseline_temp` | `float` | 否 | `37.0` | 基线体温 |
| `baseline_rr` | `float` | 否 | `16` | 基线呼吸率 |

**方法**:

#### `generate_sample(timestamp=None)`

生成单个样本。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `timestamp` | `float` | 否 | `None` | 时间戳 |

- **返回值**: `VitalSigns`

#### `trigger_anomaly(anomaly_type, duration=60)`

触发异常。支持类型：`"tachycardia"`, `"bradycardia"`, `"hypoxemia"`, `"hypertension"`, `"hypotension"`, `"hyperthermia"`。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `anomaly_type` | `str` | 是 | — | 异常类型 |
| `duration` | `int` | 否 | `60` | 持续时间（秒） |

#### `stop_anomaly()`

停止异常。

#### `generate_stream(duration=3600, interval=1.0, callback=None)`

生成数据流。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `duration` | `int` | 否 | `3600` | 持续时间（秒） |
| `interval` | `float` | 否 | `1.0` | 采样间隔（秒） |
| `callback` | `Callable[[VitalSigns], None]` | 否 | `None` | 回调函数 |

- **返回值**: `list[VitalSigns]`

#### `generate_to_kafka(topic, duration=3600, interval=1.0, kafka_servers="localhost:9092")`

生成数据并发送到 Kafka。
- **示例**:

```python
from msra_modules.realtime_analytics import VitalSignsSimulator

simulator = VitalSignsSimulator(baseline_hr=75, baseline_sbp=120)
sample = simulator.generate_sample()
print(sample.heart_rate, sample.spo2)

# 触发心动过速异常
simulator.trigger_anomaly("tachycardia", duration=60)
```

---

### `VitalSigns`

**描述**: 生命体征数据类。

**字段**: `timestamp`, `heart_rate`, `systolic_bp`, `diastolic_bp`, `spo2`, `temperature`, `respiratory_rate`

**方法**:

#### `to_dict()`

转换为字典。

#### `to_json()`

转换为 JSON 字符串。

---

### `RealtimeDashboard`

**描述**: 实时仪表盘，支持指标监控、状态判定、快照导出和 Streamlit 应用。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `max_points` | `int` | 否 | `1000` | 最大数据点数 |
| `update_interval` | `float` | 否 | `1.0` | 更新间隔（秒） |

**方法**:

#### `add_metric(name, display_name=None, unit="", warning_range=None, critical_range=None)`

添加监控指标。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `name` | `str` | 是 | — | 指标名 |
| `display_name` | `str` | 否 | `None` | 显示名 |
| `unit` | `str` | 否 | `""` | 单位 |
| `warning_range` | `tuple` | 否 | `None` | 警告范围 |
| `critical_range` | `tuple` | 否 | `None` | 危险范围 |

#### `update(metric, value, timestamp=None)`

更新指标值。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `metric` | `str` | 是 | — | 指标名 |
| `value` | `float` | 是 | — | 值 |
| `timestamp` | `float` | 否 | `None` | 时间戳 |

#### `add_alert(alert)`

添加警报。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `alert` | `dict` | 是 | — | 警报字典 |

#### `get_dashboard_data()`

获取仪表盘数据。

- **返回值**: `dict` — 含 `metrics`（各指标的 data 和 stats）、`alerts`、`timestamp`

#### `get_metric_status(metric)`

获取指标状态。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `metric` | `str` | 是 | — | 指标名 |

- **返回值**: `str` — `"normal"`, `"warning"`, `"critical"`, `"unknown"`

#### `export_snapshot(filepath)`

导出快照为 JSON 文件。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `filepath` | `str` | 是 | — | 文件路径 |

#### `create_streamlit_app()`

创建 Streamlit 应用。

- **返回值**: Streamlit 应用对象
- **异常**: `ImportError`（streamlit/plotly 未安装）

---

### `ReportGenerator`

**描述**: 报告生成器，支持 HTML 和 Markdown 格式的影像报告、生信报告和监测报告。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `output_dir` | `str` | 否 | `"reports"` | 输出目录 |

**方法**:

#### `generate_imaging_report(patient_info, imaging_findings, radiomics_features, output_format="html")`

生成影像分析报告。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `patient_info` | `dict` | 是 | — | 患者信息 |
| `imaging_findings` | `dict` | 是 | — | 影像发现 |
| `radiomics_features` | `dict` | 是 | — | 影像组学特征 |
| `output_format` | `str` | 否 | `"html"` | 输出格式（`"html"` 或 `"markdown"`） |

- **返回值**: `str` — 报告文件路径

#### `generate_bio_report(sample_info, qc_summary, analysis_results, output_format="html")`

生成生物信息报告。

- **返回值**: `str` — 报告文件路径

#### `generate_monitoring_report(duration, stats, alerts, output_format="html")`

生成实时监测报告。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `duration` | `str` | 是 | — | 监测时长 |
| `stats` | `dict` | 是 | — | 统计数据 |
| `alerts` | `list[dict]` | 是 | — | 警报列表 |
| `output_format` | `str` | 否 | `"html"` | 输出格式 |

- **返回值**: `str` — 报告文件路径

---

### `RealtimeQualityGateChecker`

**描述**: 实时分析质量门闸检查器，封装 Gate RT-1（实时数据质量门闸）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `study_id` | `str` | 是 | — | 研究编号 |
| `project_root` | `str` | 否 | `None` | 项目根目录 |

**方法**:

#### `run_gate_rt1(source=None, timestamps=None, detection_rate=None, window_size=60, max_gap_multiplier=2.0, min_rate=0.01, max_rate=0.20)`

执行 Gate RT-1 全部 3 项检查：数据流连接正常、时间戳连续性、异常检测灵敏度校准。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `source` | `Any` | 否 | `None` | 数据源对象（模拟器或其他数据源） |
| `timestamps` | `list[float]` | 否 | `None` | 时间戳列表 |
| `detection_rate` | `float` | 否 | `None` | 异常检测率 |
| `window_size` | `int` | 否 | `60` | 窗口大小（秒） |
| `max_gap_multiplier` | `float` | 否 | `2.0` | 最大间隔倍数 |
| `min_rate` | `float` | 否 | `0.01` | 最小检测率 |
| `max_rate` | `float` | 否 | `0.20` | 最大检测率 |

- **返回值**: `GateResult` — 判定结果（`PASS` / `CONDITIONAL` / `BLOCKED`）
- **示例**:

```python
from msra_modules.realtime_analytics import RealtimeQualityGateChecker, VitalSignsSimulator

simulator = VitalSignsSimulator()
checker = RealtimeQualityGateChecker(study_id="RT-2026-001")
result = checker.run_gate_rt1(source=simulator, detection_rate=0.05)
print(result.verdict)
```

---

## 完整使用示例

```python
from msra_modules.realtime_analytics import (
    StreamProcessor, AnomalyDetector, AlertSystem, AlertChannel,
    VitalSignsSimulator, RealtimeDashboard, RealtimeQualityGateChecker,
)

# 1. 创建模拟器
simulator = VitalSignsSimulator(baseline_hr=75, baseline_sbp=120)

# 2. 创建流处理器
processor = StreamProcessor(window_size=60)
processor.register_metric("heart_rate")
processor.register_metric("spo2")

# 3. 创建异常检测器
detector = AnomalyDetector()
detector.add_default_vital_signs_rules()

# 4. 创建告警系统
alert_system = AlertSystem(log_file="/logs/alerts.jsonl")

# 5. 创建仪表盘
dashboard = RealtimeDashboard()
dashboard.add_metric("heart_rate", display_name="HR", unit="bpm",
                     warning_range=(100, 150), critical_range=(0, 40))

# 6. 模拟数据流
for i in range(100):
    sample = simulator.generate_sample()
    processor.add_data_point("heart_rate", sample.heart_rate)
    alerts = detector.evaluate("heart_rate", sample.heart_rate)
    for alert in alerts:
        alert_system.send_alert(alert)
    dashboard.update("heart_rate", sample.heart_rate)

# 7. 质量门闸
checker = RealtimeQualityGateChecker(study_id="RT-2026-001")
result = checker.run_gate_rt1(source=simulator, detection_rate=0.05)
```
