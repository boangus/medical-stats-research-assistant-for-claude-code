# 实时分析模块 API 参考

> **版本**: v1.0.0 | **日期**: 2026-06-26 | **状态**: Stable
> **模块**: Realtime Analytics | **命令**: `/realtime`

---

## 目录

- [StreamProcessor — 流处理器](#streamprocessor)
- [AnomalyDetector — 异常检测器](#anomalydetector)
- [DetectionResult — 检测结果](#detectionresult)
- [MultivariateDetector — 多变量检测](#multivariatedetector)
- [AlertSystem — 告警系统](#alertsystem)
- [Alert — 告警数据类](#alert)
- [RealtimeDashboard — 仪表盘](#realtimedashboard)
- [VitalSignsSimulator — 生命体征模拟器](#vitalsignssimulator)
- [RealtimeQualityGateChecker — 质量门闸](#realtimequalitygatechecker)

---

## StreamProcessor

> 流处理器，提供滑动窗口统计、Kafka 消费、事件处理和聚合计算功能。

**签名**:

```python
StreamProcessor(window_size: int = 60, kafka_bootstrap_servers: str = "localhost:9092")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| window_size | int | 60 | 滑动窗口大小（秒） |
| kafka_bootstrap_servers | str | "localhost:9092" | Kafka 服务器地址 |

**方法**:

### `register_metric`

```python
register_metric(name: str, window_size: Optional[int] = None)
```

注册监控指标。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| name | str | — | 必填，指标名称 |
| window_size | Optional[int] | None | 窗口大小（覆盖默认值） |

### `add_data_point`

```python
add_data_point(metric: str, value: float, timestamp: Optional[float] = None)
```

添加数据点（自动注册未注册的指标，并触发所有处理器）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| metric | str | — | 必填，指标名称 |
| value | float | — | 必填，数据值 |
| timestamp | Optional[float] | None | 时间戳（默认当前时间） |

### `get_metric_stats`

```python
get_metric_stats(metric: str) -> Dict[str, float]
```

获取指定指标的统计。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| metric | str | — | 必填，指标名称 |

**返回值**: `Dict[str, float]` — 含 count、mean、std、min、max、median、p25、p75

### `get_all_stats`

```python
get_all_stats() -> Dict[str, Dict[str, float]]
```

获取所有指标的统计。

**返回值**: `Dict[str, Dict[str, float]]` — 所有指标统计字典

### `aggregate`

```python
aggregate(metric: str, func: str = "mean") -> float
```

对窗口数据进行聚合计算。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| metric | str | — | 必填，指标名称 |
| func | str | "mean" | 聚合函数名（"mean"、"std"、"min"、"max"、"median"、"sum"、"count"、"p25"、"p75"） |

**返回值**: `float` — 聚合结果

**异常**: `ValueError` — 指标不存在、无数据、或不支持的聚合函数

### `process_event`

```python
process_event(event: Dict[str, Any]) -> Dict[str, Any]
```

统一事件处理入口。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| event | Dict[str, Any] | — | 必填，事件字典（需含 metric、value，可选 timestamp、metadata） |

**返回值**: `Dict[str, Any]` — 含 metric、value、timestamp、stats、handlers_called

**异常**: `ValueError` — 事件缺少 metric 或 value 字段

### `add_handler`

```python
add_handler(handler: Callable[[str, float, Optional[float]], None])
```

添加数据处理器。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| handler | Callable | — | 必填，处理函数 (metric, value, timestamp) |

### `start_kafka_consumer`

```python
start_kafka_consumer(topic: str, metric_field: str = "value")
```

启动 Kafka 消费者。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| topic | str | — | 必填，Kafka 主题 |
| metric_field | str | "value" | 值字段名 |

### `get_all_metrics`

```python
get_all_metrics() -> List[str]
```

获取所有已注册的指标名。

**返回值**: `List[str]` — 指标名列表

### `stop`

```python
stop()
```

停止处理。

**示例**:

```python
from msra_modules.realtime_analytics import StreamProcessor

sp = StreamProcessor(window_size=60)
sp.register_metric("heart_rate")

for hr in [75, 78, 72, 80, 76]:
    sp.add_data_point("heart_rate", hr)

stats = sp.get_metric_stats("heart_rate")
print(f"心率均值: {stats['mean']:.1f}, 标准差: {stats['std']:.1f}")

result = sp.process_event({"metric": "heart_rate", "value": 120})
print(f"处理结果: {result['stats']}")
```

---

## AnomalyDetector

> 异常检测器，基于规则引擎实现阈值告警，支持持续时间要求和冷却时间。

**签名**:

```python
AnomalyDetector()
```

**方法**:

### `add_rule`

```python
add_rule(rule: AlertRule)
```

添加告警规则。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| rule | AlertRule | — | 必填，告警规则 |

### `add_default_vital_signs_rules`

```python
add_default_vital_signs_rules()
```

添加默认生命体征规则（心率过缓/过速、血氧过低、血压过高/过低、体温过高/过低）。

### `evaluate`

```python
evaluate(metric: str, value: float, timestamp: Optional[float] = None) -> List[Alert]
```

评估指标，返回触发的告警列表。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| metric | str | — | 必填，指标名称 |
| value | float | — | 必填，当前值 |
| timestamp | Optional[float] | None | 时间戳（默认当前时间） |

**返回值**: `List[Alert]` — 触发的告警列表

### `add_alert_handler`

```python
add_alert_handler(handler: Callable[[Alert], None])
```

添加告警处理器。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| handler | Callable[[Alert], None] | — | 必填，处理函数 |

### `get_rules`

```python
get_rules() -> List[AlertRule]
```

获取所有规则。

**返回值**: `List[AlertRule]` — 规则列表

### AlertRule 数据类

```python
AlertRule(name: str, metric: str, condition: str, threshold: float,
          threshold_max: Optional[float] = None, level: AlertLevel = AlertLevel.WARNING,
          sustained_seconds: int = 0, cooldown_seconds: int = 300, description: str = "")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| name | str | — | 规则名称 |
| metric | str | — | 指标名称 |
| condition | str | — | 条件（"gt"、"lt"、"gte"、"lte"、"range"） |
| threshold | float | — | 阈值 |
| threshold_max | Optional[float] | None | 范围上限（range 条件用） |
| level | AlertLevel | WARNING | 警报级别 |
| sustained_seconds | int | 0 | 持续时间要求（秒） |
| cooldown_seconds | int | 300 | 冷却时间（秒） |
| description | str | "" | 描述 |

### AlertLevel 枚举

| 值 | 说明 |
|----|------|
| INFO | 信息 |
| WARNING | 警告 |
| CRITICAL | 严重 |

**示例**:

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

> 异常检测结果数据类，用于多变量异常检测方法（如 Isolation Forest）的输出。

**属性**:

| 属性 | 类型 | 默认 | 说明 |
|------|------|------|------|
| index | int | — | 数据点在原始数据中的索引 |
| is_anomaly | bool | — | 是否为异常 |
| score | float | — | 异常分数（越低越异常） |
| features | Dict[str, float] | {} | 特征值 |
| method | str | "" | 检测方法名称 |
| timestamp | Optional[float] | None | 时间戳 |

**方法**:

### `to_dict`

```python
to_dict() -> Dict
```

转换为字典。

**返回值**: `Dict` — 包含所有属性的字典

---

## MultivariateDetector

> 多变量异常检测器，基于 Isolation Forest 算法进行多变量异常检测。

**签名**:

```python
MultivariateDetector(contamination: float = 0.05, random_state: int = 42)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| contamination | float | 0.05 | 预期异常比例（默认 5%） |
| random_state | int | 42 | 随机种子，保证可复现性 |

**方法**:

### `fit`

```python
fit(data: np.ndarray, feature_names: Optional[List[str]] = None)
```

训练 Isolation Forest 模型。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| data | np.ndarray | — | 必填，形状为 (n_samples, n_features) 的数据矩阵 |
| feature_names | Optional[List[str]] | None | 特征名称列表 |

**异常**: `ValueError` — 输入不是 2D 数组；`ImportError` — scikit-learn 未安装

### `detect`

```python
detect(data: np.ndarray, feature_names: Optional[List[str]] = None, timestamps: Optional[List[float]] = None) -> List[DetectionResult]
```

执行多变量异常检测（未训练时自动训练）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| data | np.ndarray | — | 必填，形状为 (n_samples, n_features) 的数据矩阵 |
| feature_names | Optional[List[str]] | None | 特征名称列表 |
| timestamps | Optional[List[float]] | None | 时间戳列表 |

**返回值**: `List[DetectionResult]` — 检测结果列表

### `reset`

```python
reset()
```

重置检测器。

**示例**:

```python
from msra_modules.realtime_analytics import MultivariateDetector
import numpy as np

detector = MultivariateDetector(contamination=0.05)
data = np.random.randn(100, 3)
data[95:] += 5  # 注入异常

results = detector.detect(data, feature_names=["hr", "spo2", "bp"])
anomalies = [r for r in results if r.is_anomaly]
print(f"检测到 {len(anomalies)} 个异常")
```

---

## AlertSystem

> 告警系统，支持多渠道告警通知（日志、文件、Webhook、邮件、Slack）。

**签名**:

```python
AlertSystem(log_file: Optional[str] = None)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| log_file | Optional[str] | None | 日志文件路径 |

**方法**:

### `register_handler`

```python
register_handler(channel: AlertChannel, handler: Callable[[Alert], None])
```

注册告警处理器。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| channel | AlertChannel | — | 必填，告警渠道 |
| handler | Callable[[Alert], None] | — | 必填，处理函数 |

### `send_alert`

```python
send_alert(alert: Alert, channels: Optional[List[AlertChannel]] = None)
```

发送告警。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| alert | Alert | — | 必填，告警事件 |
| channels | Optional[List[AlertChannel]] | None | 发送渠道列表（默认所有已注册渠道） |

### `webhook_handler`

```python
webhook_handler(webhook_url: str) -> Callable[[Alert], None]
```

创建 Webhook 处理器。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| webhook_url | str | — | 必填，Webhook URL |

**返回值**: `Callable[[Alert], None]` — 处理函数

### `email_handler`

```python
email_handler(smtp_server: str, smtp_port: int, sender: str, password: str, recipients: List[str]) -> Callable[[Alert], None]
```

创建邮件处理器。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| smtp_server | str | — | 必填，SMTP 服务器 |
| smtp_port | int | — | 必填，SMTP 端口 |
| sender | str | — | 必填，发件人 |
| password | str | — | 必填，密码 |
| recipients | List[str] | — | 必填，收件人列表 |

**返回值**: `Callable[[Alert], None]` — 处理函数

### `slack_handler`

```python
slack_handler(webhook_url: str) -> Callable[[Alert], None]
```

创建 Slack 处理器。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| webhook_url | str | — | 必填，Slack Webhook URL |

**返回值**: `Callable[[Alert], None]` — 处理函数

### `get_history`

```python
get_history(level: Optional[str] = None, limit: int = 100) -> List[Alert]
```

获取告警历史。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| level | Optional[str] | None | 警报级别筛选 |
| limit | int | 100 | 返回数量 |

**返回值**: `List[Alert]` — 告警列表

### `get_statistics`

```python
get_statistics() -> Dict
```

获取告警统计。

**返回值**: `Dict` — 含 total_alerts、by_level、by_rule

### AlertChannel 枚举

| 值 | 说明 |
|----|------|
| LOG | 日志 |
| WEBHOOK | Webhook |
| EMAIL | 邮件 |
| SLACK | Slack |
| FILE | 文件 |

---

## Alert

> 告警事件数据类（来自 alert_system.py）。

**属性**:

| 属性 | 类型 | 默认 | 说明 |
|------|------|------|------|
| rule_name | str | — | 规则名称 |
| metric | str | — | 指标名称 |
| value | float | — | 当前值 |
| level | str | — | 警报级别（"info"、"warning"、"critical"） |
| message | str | — | 告警消息 |
| timestamp | float | — | 时间戳 |
| context | Dict | None | 上下文 |

**方法**:

### `to_dict`

```python
to_dict() -> Dict
```

转换为字典。

### `to_json`

```python
to_json() -> str
```

转换为 JSON 字符串。

**示例**:

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

> 实时仪表盘，支持指标监控、状态判断和 Streamlit 可视化。

**签名**:

```python
RealtimeDashboard(max_points: int = 1000, update_interval: float = 1.0)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| max_points | int | 1000 | 最大数据点数 |
| update_interval | float | 1.0 | 更新间隔（秒） |

**方法**:

### `add_metric`

```python
add_metric(name: str, display_name: Optional[str] = None, unit: str = "",
           warning_range: Optional[tuple] = None, critical_range: Optional[tuple] = None)
```

添加监控指标。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| name | str | — | 必填，指标名 |
| display_name | Optional[str] | None | 显示名 |
| unit | str | "" | 单位 |
| warning_range | Optional[tuple] | None | 警告范围 |
| critical_range | Optional[tuple] | None | 危险范围 |

### `update`

```python
update(metric: str, value: float, timestamp: Optional[float] = None)
```

更新指标值。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| metric | str | — | 必填，指标名 |
| value | float | — | 必填，值 |
| timestamp | Optional[float] | None | 时间戳 |

### `add_alert`

```python
add_alert(alert: Dict)
```

添加告警到仪表盘。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| alert | Dict | — | 必填，告警字典 |

### `get_dashboard_data`

```python
get_dashboard_data() -> Dict
```

获取仪表盘数据。

**返回值**: `Dict` — 含 metrics（含 data 和 stats）、alerts、timestamp

### `get_metric_status`

```python
get_metric_status(metric: str) -> str
```

获取指标状态。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| metric | str | — | 必填，指标名 |

**返回值**: `str` — 状态（"normal"、"warning"、"critical"、"unknown"）

### `export_snapshot`

```python
export_snapshot(filepath: str)
```

导出快照到 JSON 文件。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| filepath | str | — | 必填，文件路径 |

### `create_streamlit_app`

```python
create_streamlit_app()
```

创建 Streamlit 应用（需安装 streamlit 和 plotly）。

**返回值**: Streamlit 应用对象

**异常**: `ImportError` — streamlit/plotly 未安装

**示例**:

```python
from msra_modules.realtime_analytics import RealtimeDashboard

dashboard = RealtimeDashboard(max_points=500)
dashboard.add_metric("heart_rate", display_name="心率", unit="bpm",
                     warning_range=(100, 150), critical_range=(0, 40))

dashboard.update("heart_rate", 75)
print(dashboard.get_metric_status("heart_rate"))  # "normal"
dashboard.export_snapshot("dashboard_snapshot.json")
```

---

## VitalSignsSimulator

> 生命体征模拟器，生成带有随机噪声的生命体征数据，支持异常注入和流式生成。

**签名**:

```python
VitalSignsSimulator(baseline_hr: float = 75, baseline_sbp: float = 120,
                     baseline_dbp: float = 80, baseline_spo2: float = 98,
                     baseline_temp: float = 37.0, baseline_rr: float = 16)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| baseline_hr | float | 75 | 基线心率 |
| baseline_sbp | float | 120 | 基线收缩压 |
| baseline_dbp | float | 80 | 基线舒张压 |
| baseline_spo2 | float | 98 | 基线血氧 |
| baseline_temp | float | 37.0 | 基线体温 |
| baseline_rr | float | 16 | 基线呼吸率 |

**方法**:

### `generate_sample`

```python
generate_sample(timestamp: Optional[float] = None) -> VitalSigns
```

生成单个生命体征样本。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| timestamp | Optional[float] | None | 时间戳（默认当前时间） |

**返回值**: `VitalSigns` — 生命体征数据对象

### `trigger_anomaly`

```python
trigger_anomaly(anomaly_type: str, duration: int = 60)
```

触发异常。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| anomaly_type | str | — | 必填，异常类型（"tachycardia"、"bradycardia"、"hypoxemia"、"hypertension"、"hypotension"、"hyperthermia"） |
| duration | int | 60 | 持续时间（秒） |

### `stop_anomaly`

```python
stop_anomaly()
```

停止异常。

### `generate_stream`

```python
generate_stream(duration: int = 3600, interval: float = 1.0,
                callback: Optional[Callable[[VitalSigns], None]] = None) -> List[VitalSigns]
```

生成数据流。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| duration | int | 3600 | 持续时间（秒） |
| interval | float | 1.0 | 采样间隔（秒） |
| callback | Optional[Callable] | None | 回调函数 |

**返回值**: `List[VitalSigns]` — 生命体征列表

### `generate_to_kafka`

```python
generate_to_kafka(topic: str, duration: int = 3600, interval: float = 1.0,
                  kafka_servers: str = "localhost:9092")
```

生成数据并发送到 Kafka。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| topic | str | — | 必填，Kafka 主题 |
| duration | int | 3600 | 持续时间 |
| interval | float | 1.0 | 采样间隔 |
| kafka_servers | str | "localhost:9092" | Kafka 服务器 |

### VitalSigns 数据类

| 属性 | 类型 | 说明 |
|------|------|------|
| timestamp | float | 时间戳 |
| heart_rate | float | 心率 |
| systolic_bp | float | 收缩压 |
| diastolic_bp | float | 舒张压 |
| spo2 | float | 血氧饱和度 |
| temperature | float | 体温 |
| respiratory_rate | float | 呼吸率 |

**示例**:

```python
from msra_modules.realtime_analytics import VitalSignsSimulator

sim = VitalSignsSimulator(baseline_hr=75)
sample = sim.generate_sample()
print(f"心率: {sample.heart_rate:.1f}")

sim.trigger_anomaly("tachycardia", duration=30)
abnormal = sim.generate_sample()
print(f"异常心率: {abnormal.heart_rate:.1f}")
```

---

## RealtimeQualityGateChecker

> 实时分析质量门闸检查器，封装 Gate RT-1 的检查逻辑。

**签名**:

```python
RealtimeQualityGateChecker(study_id: str, project_root: Optional[str] = None)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| study_id | str | — | 必填，研究编号 |
| project_root | Optional[str] | None | 项目根目录（可选） |

**方法**:

### `run_gate_rt1`

```python
run_gate_rt1(source: Any = None, timestamps: Optional[List[float]] = None,
             detection_rate: Optional[float] = None, window_size: int = 60,
             max_gap_multiplier: float = 2.0, min_rate: float = 0.01,
             max_rate: float = 0.20) -> GateResult
```

执行 Gate RT-1 全部 3 项检查：数据流连接正常、时间戳连续性、异常检测灵敏度校准。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| source | Any | None | 数据源对象（模拟器或其他数据源） |
| timestamps | Optional[List[float]] | None | 时间戳列表 |
| detection_rate | Optional[float] | None | 异常检测率 |
| window_size | int | 60 | 窗口大小（秒） |
| max_gap_multiplier | float | 2.0 | 最大间隔倍数 |
| min_rate | float | 0.01 | 最小检测率 |
| max_rate | float | 0.20 | 最大检测率 |

**返回值**: `GateResult` — 判定结果（PASS / CONDITIONAL / BLOCKED）

### `check_data_source_available`

```python
check_data_source_available(source: Any) -> CheckItemResult
```

检查数据流连接是否正常。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| source | Any | — | 必填，数据源对象 |

**返回值**: `CheckItemResult`

### `check_timestamp_continuity`

```python
check_timestamp_continuity(timestamps: List[float], window_size: int = 60,
                           max_gap_multiplier: float = 2.0) -> CheckItemResult
```

检查时间戳连续性。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| timestamps | List[float] | — | 必填，时间戳列表（应已排序） |
| window_size | int | 60 | 窗口大小（秒） |
| max_gap_multiplier | float | 2.0 | 最大间隔倍数 |

**返回值**: `CheckItemResult`

### `check_detection_sensitivity`

```python
check_detection_sensitivity(detection_rate: float, min_rate: float = 0.01,
                            max_rate: float = 0.20) -> CheckItemResult
```

检查异常检测灵敏度校准。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| detection_rate | float | — | 必填，实际检测到的异常比例 (0.0-1.0) |
| min_rate | float | 0.01 | 最小可接受检测率 |
| max_rate | float | 0.20 | 最大可接受检测率 |

**返回值**: `CheckItemResult`

**示例**:

```python
from msra_modules.realtime_analytics import RealtimeQualityGateChecker, VitalSignsSimulator

checker = RealtimeQualityGateChecker(study_id="RT-2026-001")
sim = VitalSignsSimulator()

gate_result = checker.run_gate_rt1(
    source=sim,
    timestamps=[1719400000.0 + i for i in range(100)],
    detection_rate=0.05
)
print(f"RT-1 判定: {gate_result.verdict.value}")
print(f"通过率: {gate_result.pass_rate:.1%}")
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

### GateVerdict

| 值 | 说明 |
|----|------|
| PASS | 全部通过 |
| CONDITIONAL | 条件通过 |
| BLOCKED | 阻断 |
