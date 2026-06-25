# Gate: RT QUALITY (Realtime Module)

## 元数据
- gate_id: "rt_quality"
- module: "realtime"
- blocking: true
- skill_source: "realtime-monitor"
- checkpoint_id: "GATE-RT / RT-1"
- extension_adapter: "ExtensionGateAdapter('rt').run_module_gate('rt_stream_gate', inputs)"

## 输入

| 参数 | 类型 | 来源 | 必填 |
|------|------|------|------|
| data_stream | stream (simulator/redis/kafka/csv) | StreamProcessor 注册 | ✅ |
| metrics_registry | dict | Phase 0 配置 | ✅ |
| alert_rules | dict | Phase 0 告警规则 | ✅ |
| window_stats | file (json) | Phase 2 滑动窗口统计 | 否 |
| anomaly_results | file (json) | Phase 2 AnomalyDetector | 否 |
| alert_history | file (json) | Phase 2 AlertSystem | 否 |
| dashboard_status | dict | RealtimeDashboard 状态 | 否 |

## 检查清单 (4 项)

| # | 检查项 | 通过标准 | 关键项 |
|---|--------|---------|--------|
| 1 | 数据流连续性 | 数据源在 5 秒内返回至少 1 个数据点；相邻数据点时间戳间隔 < 窗口大小的 2 倍 | ✅ 硬阻断 |
| 2 | 异常检测准确率 | 模拟异常场景下检测率 ∈ [1%, 20%]；规则引擎与多变量检测无 NaN 输出 | ✅ 硬阻断 |
| 3 | 告警延迟 | 从异常发生到告警触发延迟 < 2 秒；告警冷却时间已配置；告警历史已持久化 | 否 |
| 4 | 仪表盘可用性 | RealtimeDashboard 可正常更新；指标显示无 NaN；时间戳包含完整时段信息 | 否 |

### 检查项 1（数据流连续性）详细标准
- 数据源在 5 秒内返回至少 1 个数据点（连接验证）
- 相邻数据点时间戳间隔 < 滑动窗口大小的 2 倍
- 时间戳单调递增（无乱序）
- 通过标准：以上全部满足

### 检查项 2（异常检测准确率）详细标准
- 模拟异常场景下检测率 ∈ [1%, 20%]（避免漏检或误报过多）
- AnomalyDetector 规则引擎输出无 NaN
- AnomalyDetector.detect_multivariate() Isolation Forest 输出无 NaN
- 通过标准：以上全部满足

### 检查项 3（告警延迟）详细标准
- 从异常发生到告警触发延迟 < 2 秒
- 告警规则配置了冷却时间（防止短时间重复告警）
- 告警历史已持久化（Log/File/Webhook/Slack/Email 至少一种）
- 通过标准：以上全部满足

### 检查项 4（仪表盘可用性）详细标准
- RealtimeDashboard 可正常更新（无异常退出）
- 指标显示无 NaN/Inf
- 报告/仪表盘包含完整时间信息（起止时间戳）
- 通过标准：以上全部满足

## 判定规则

- **PASS**: 全部通过 (4/4) → ✅ 进入下一阶段
- **CONDITIONAL**: 2-3/4 通过且关键项全通过 → ⚠️ 记录风险后继续
- **BLOCK**: < 2/4 通过 **或** 关键项 1/2 任一未通过 → ❌ **强制退回 Phase 1/2 修订**

> **关键项定义**：项 1（数据流连续性）、项 2（异常检测准确率）为硬阻断项，不可条件通过。

## 输出 (gate_result schema)

```json
gate_result: {
  "gate": "rt_quality",
  "module": "realtime",
  "passed": bool,
  "total": 4,
  "passed_count": int,
  "failed_items": ["TG-0X", ...],
  "conditional": bool,
  "blocking_items": ["TG-01" | "TG-02"],
  "timestamp": "ISO8601"
}
```

## 与模块的联动

- **BLOCK** → 退回 Phase 1 修订数据流接入，或退回 Phase 2 修订异常检测/告警配置
- **回退 ≥ 2 次** → 触发收敛检测（见 pipeline/SKILL.md §7.3）
- **CONDITIONAL** → 记录风险后继续 Phase 3 结果审查
- **Checkpoint**: [GATE-RT] 门闸通过后方可进入 Phase 3 用户确认
- **Skill 模式**：`realtime-monitor` 复用，Mode=`quality-gate`（只检查，不修改）
- **Agent 模式**：通过 `ExtensionGateAdapter("rt")` 调用
- 参考实现：`shared/quality_gates/gate_runner.py` + `check_items.py`
