# MSRA 实时分析模块用户教程

> **模块版本**: v1.2.0 | **文档日期**: 2026-06-25 | **状态**: Stable
> **命令入口**: `/msra-rt` | **适用 MSRA 版本**: v1.0.0+

---

## 1. 模块简介与适用场景

### 模块概述

MSRA Realtime Analytics（实时分析）模块提供实时生命体征监控能力，覆盖数据流接入、滑动窗口统计、异常检测、告警触发和报告生成的完整链路。支持模拟器、Redis、Kafka、CSV 四种数据源，适配临床监护、术后观察、急诊监控等多种场景。

### 核心能力

| 能力 | 说明 |
|------|------|
| 流处理 | 滑动窗口统计（mean/std/min/max/median），`StreamProcessor` |
| 异常检测 | 规则引擎 + Isolation Forest 多变量检测，`AnomalyDetector`, `MultivariateDetector` |
| 趋势检测 | CUSUM 趋势检测，`TrendDetector` |
| 告警系统 | 多渠道分发（Log/File/Webhook/Slack/Email），`AlertSystem` |
| 实时仪表盘 | 监控可视化，`RealtimeDashboard` |
| 数据模拟 | 生命体征模拟器，`VitalSignsSimulator` |
| 质量门闸 | Gate RT-1（实时数据质量），`RealtimeQualityGateChecker` |

### 适用场景

- ICU 患者生命体征实时监控与告警
- 术后恢复期监护
- 急诊分诊实时指标追踪
- 临床试验中的不良事件实时检测
- 开发/测试阶段使用模拟器验证监控流程

---

## 2. 安装依赖

### 安装 realtime_analytics 扩展依赖

```bash
pip install -e ".[realtime_analytics]"
```

### 核心依赖列表

```toml
numpy >= 1.24          # 数值计算
scipy >= 1.10          # 科学计算
scikit-learn >= 1.3    # Isolation Forest / DBSCAN
# 可选依赖
redis >= 5.0           # Redis 数据源
kafka-python >= 2.0    # Kafka 数据源
plotly >= 5.18         # 交互式图表
streamlit >= 1.30      # Web 仪表盘（P2）
```

### 验证安装

```bash
python -c "from msra_modules.realtime_analytics import StreamProcessor, AnomalyDetector, AlertSystem, VitalSignsSimulator, RealtimeQualityGateChecker; print('OK')"
```

---

## 3. 数据源配置

### 支持的数据源类型

| 类型 | 参数 | 说明 | 适用场景 |
|------|------|------|---------|
| 模拟器 | `--source simulator` | 内置生命体征模拟器 | 开发测试、演示 |
| Redis | `--source redis://host:port` | Redis Stream 数据源 | 生产环境、分布式 |
| Kafka | `--source kafka://host:port/topic` | Kafka Topic 消费 | 生产环境、高吞吐 |
| CSV | `--source csv --data vitals.csv` | CSV 文件按时间序列回放 | 离线分析、历史数据 |

### 模拟器模式（默认）

```python
from msra_modules.realtime_analytics import VitalSignsSimulator, VitalSigns

# 创建模拟器（默认模拟心率、血氧、收缩压、体温）
simulator = VitalSignsSimulator(
    interval=1.0,        # 采样间隔（秒）
    duration=60,         # 监控时长（秒）
    anomaly_rate=0.05,   # 异常注入率
)

# 生成数据流
for data_point in simulator.stream():
    print(f"[{data_point.timestamp:.1f}] HR={data_point.heart_rate:.0f} "
          f"SpO2={data_point.spo2:.0f} SBP={data_point.systolic_bp:.0f}")
```

### CSV 回放模式

CSV 文件需包含 `timestamp` 列和指标列：

```csv
timestamp,heart_rate,spo2,systolic_bp,temperature
0.0,72,98,120,36.5
1.0,73,98,122,36.5
2.0,75,97,125,36.6
...
```

---

## 4. 实时监控全流程

### 通过命令启动

```
# 模拟器 + ICU 预设规则，监控 60 秒
/msra-rt --source simulator --preset icu --duration 60

# CSV 回放
/msra-rt --source csv --data vitals.csv

# Redis 数据源
/msra-rt --source redis://localhost:6379
```

### Python API 完整流程

```python
from msra_modules.realtime_analytics import (
    StreamProcessor, AnomalyDetector, AlertSystem,
    VitalSignsSimulator, RealtimeQualityGateChecker,
    AlertRule, AlertLevel,
)

# Phase 0: 配置
simulator = VitalSignsSimulator(interval=1.0, duration=60)
processor = StreamProcessor(window_size=60)
detector = AnomalyDetector()
alert_system = AlertSystem()

# 注册监控指标
processor.register_metric("heart_rate")
processor.register_metric("spo2")
processor.register_metric("systolic_bp")

# Phase 1: 数据流接入 + Gate RT-1 (项1+2)
checker = RealtimeQualityGateChecker(study_id="RT-2026-001")

# 接收前几个数据点验证连接
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

# Phase 2: 实时监控
for point in simulator.stream():
    # 流处理
    processor.add_data_point("heart_rate", point.heart_rate, point.timestamp)
    processor.add_data_point("spo2", point.spo2, point.timestamp)
    processor.add_data_point("systolic_bp", point.systolic_bp, point.timestamp)

    # 异常检测
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

# Phase 3: 结果审查 + Gate RT-1 (项3)
gate_result_3 = checker.run_gate_rt1_item3(
    detection_results=detector.get_results(),
)
print(f"Gate RT-1 (sensitivity): {gate_result_3.verdict}")

# Phase 4: 报告
stats_summary = processor.get_all_stats()
alert_history = alert_system.get_history()
print(f"Monitoring complete. Alerts: {len(alert_history)}")
```

---

## 5. 异常检测配置

### 规则引擎（基于阈值）

```python
from msra_modules.realtime_analytics import AnomalyDetector, AlertRule, AlertLevel

detector = AnomalyDetector()

# 添加异常检测规则
detector.add_rule(AlertRule(
    name="bradycardia",
    metric="heart_rate",
    condition="lt",          # 小于阈值
    threshold=50,            # 心率 < 50
    level=AlertLevel.CRITICAL,
    sustained_seconds=5,     # 持续 5 秒才触发
    cooldown_seconds=300,    # 冷却 5 分钟
    description="心动过缓",
))

detector.add_rule(AlertRule(
    name="tachycardia",
    metric="heart_rate",
    condition="gt",          # 大于阈值
    threshold=120,           # 心率 > 120
    level=AlertLevel.WARNING,
    sustained_seconds=5,
    cooldown_seconds=300,
    description="心动过速",
))

detector.add_rule(AlertRule(
    name="hypoxia",
    metric="spo2",
    condition="lt",
    threshold=90,            # SpO2 < 90%
    level=AlertLevel.CRITICAL,
    sustained_seconds=3,
    cooldown_seconds=120,
    description="低氧血症",
))

detector.add_rule(AlertRule(
    name="hypertension",
    metric="systolic_bp",
    condition="range",       # 范围外
    threshold=90,            # 下限
    threshold_max=180,       # 上限
    level=AlertLevel.WARNING,
    sustained_seconds=10,
    cooldown_seconds=300,
    description="血压异常",
))
```

### 多变量异常检测（Isolation Forest）

```python
from msra_modules.realtime_analytics import MultivariateDetector

# 多变量检测器（同时考虑多个指标的关系）
mv_detector = MultivariateDetector(
    method="isolation_forest",
    contamination=0.05,    # 预期异常比例
    window_size=100,       # 训练窗口大小
)

# 输入多指标数据
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

### 趋势检测（CUSUM）

```python
from msra_modules.realtime_analytics import TrendDetector

trend_detector = TrendDetector(threshold=5.0)

# 逐点检测趋势变化
for value in heart_rate_stream:
    trend = trend_detector.update(value)
    if trend.is_trending:
        print(f"Upward trend detected: {trend.direction}, CUSUM={trend.cusum:.2f}")
```

---

## 6. 告警规则定制

### 预设规则模板

| 模板 | 指标 | 规则概要 |
|------|------|---------|
| `icu` | HR, SpO2, SBP, Temp | HR 40-150, SpO2>90, SBP 90-180, Temp 36-38 |
| `postop` | HR, SpO2, SBP, Temp | 术后监护规则（更严格） |
| `emergency` | HR, SpO2, SBP | 急诊分诊规则（快速响应） |

### 使用预设

```
/msra-rt --source simulator --preset icu --duration 3600
```

### 自定义告警渠道

```python
from msra_modules.realtime_analytics import AlertSystem, AlertChannel

alert_system = AlertSystem()

# 添加告警渠道
alert_system.add_channel(AlertChannel.LOG, level=AlertLevel.INFO)       # 所有级别记录日志
alert_system.add_channel(AlertChannel.FILE, filepath="alerts.log")       # 写入文件
alert_system.add_channel(AlertChannel.WEBHOOK, url="https://hook.example.com/alert")
alert_system.add_channel(AlertChannel.SLACK, webhook_url="https://hooks.slack.com/...")
alert_system.add_channel(AlertChannel.EMAIL, recipients=["oncall@hospital.org"])
```

### 告警冷却与持续时间

每条规则支持两个时间过滤参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `sustained_seconds` | 异常需持续指定时间后才触发告警 | 心率 >120 持续 5 秒才告警 |
| `cooldown_seconds` | 同一规则两次告警之间的最短间隔 | 5 分钟内不重复告警 |

---

## 7. 质量门闸说明

### Gate RT-1 — 实时数据质量门闸

> 在 Phase 1（项1+2）和 Phase 3（项3）执行，验证数据流和检测质量。
> 实现: `msra_modules/realtime_analytics/quality_gates.py` → `RealtimeQualityGateChecker`

| # | 检查项 | 关键项 | 通过标准 |
|---|--------|--------|---------|
| 1 | 数据流连接正常 | 🔑 | 5 秒内收到至少 1 个数据点 |
| 2 | 时间戳连续性 | 🔑 | 相邻数据点间隔 < 采样间隔 × 5 |
| 3 | 异常检测灵敏度校准 | | 检测率在 1%-20% 之间 |

**判定规则**:
- **PASS**: 3/3 通过
- **CONDITIONAL**: 2/3 通过且 🔑 全通过
- **BLOCKED**: ≤ 1/3 通过 或 🔑 任一未通过（**阻断流程**）

### Python 调用示例

```python
from msra_modules.realtime_analytics import RealtimeQualityGateChecker

checker = RealtimeQualityGateChecker(study_id="RT-2026-001")

# Phase 1: 项1+2 检查（数据流连接 + 时间戳连续性）
result_12 = checker.run_gate_rt1_first2(
    data_points=received_points,
    expected_interval=1.0,
)
print(f"RT-1 (connection): {result_12.verdict}")

# Phase 3: 项3 检查（异常检测灵敏度校准）
result_3 = checker.run_gate_rt1_item3(
    detection_results=detector.get_all_results(),
    total_points=total_data_points,
)
print(f"RT-1 (sensitivity): {result_3.verdict}")
```

---

## 8. 报告导出

### 生成监控报告

```python
from msra_modules.realtime_analytics import RealtimeDashboard, ReportGenerator

# 生成报告
report_gen = ReportGenerator()
report_path = report_gen.generate(
    stats_summary=processor.get_all_stats(),
    alert_history=alert_system.get_history(),
    anomaly_results=detector.get_all_results(),
    output_path="MSRA/reports/rt_monitoring_20260625.html",
)
print(f"Report saved to: {report_path}")
```

### 报告内容

| 章节 | 内容 |
|------|------|
| 监控概要 | 监控时长、采样间隔、指标列表 |
| 统计摘要 | 各指标的均值/标准差/极值/趋势 |
| 告警历史 | 按级别分组，含触发时间/规则/当前值 |
| 异常检测结果 | 规则触发 + 多变量检测 |
| 质量门闸报告 | Gate RT-1 三项检查结果 |

### 命令行导出

```
/msra-rt --source simulator --preset icu --duration 600 --export-report
```

---

## 9. 常见问题 FAQ

### Q1: 模拟器生成的数据看起来太规律怎么办？

模拟器默认注入 5% 的异常数据。您可以通过 `anomaly_rate` 参数调整：

```python
simulator = VitalSignsSimulator(anomaly_rate=0.1)  # 10% 异常率
```

### Q2: Redis 连接失败怎么办？

1. 确认 Redis 服务正在运行: `redis-cli ping`
2. 检查连接字符串格式: `redis://host:port`
3. 如果无法连接，系统会阻断（Gate RT-1 项1）并提示切换到模拟器模式

### Q3: Isolation Forest 检测结果全为异常怎么办？

- 检查 `contamination` 参数是否设置过高（默认 0.05）
- 确保训练窗口中有足够的正常数据
- 检查输入数据是否已正确标准化

### Q4: 告警过于频繁怎么办？

1. 增加 `sustained_seconds`（持续时间要求）
2. 增加 `cooldown_seconds`（冷却时间）
3. 调整 `AlertLevel`，只对 CRITICAL 级别触发外部通知

### Q5: CSV 回放速度太慢怎么办？

CSV 回放是按时间序列逐行播放的。可以通过 `--interval 0` 参数加速回放：

```
/msra-rt --source csv --data vitals.csv --interval 0
```

### Q6: 如何将监控数据接入 cross_domain 模块？

`StreamProcessor` 预留了指标导出接口：

```python
metrics_export = processor.export_metrics_for_cross_domain()
# 导出格式: {metric_name: [values], ...}
# 可直接传入 /msra-cross 的 RealtimePredictionModel
```

---

> **相关文档**: [SKILL.md](../../skills/realtime-monitor/SKILL.md) | [模块 PRD](../prd/msra_rt_prd.md) | [MSRA 文档主页](../system_design.md)
