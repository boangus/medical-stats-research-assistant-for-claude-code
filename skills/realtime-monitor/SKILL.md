---
version: "1.0.0"
name: MSRA Realtime Analytics
description: |
  实时生命体征监控：流数据处理、异常检测、告警触发、实时仪表盘报告。
  支持模拟器/Redis/Kafka/CSV 数据源。
  输出: 滑动窗口统计 + 异常检测结果 + 告警历史 + 监控报告。
  触发: 实时监控 / realtime / vital signs / 异常检测 / 告警 / stream /
  anomaly / alert / monitoring / dashboard / 生命体征
data_access_level: raw
task_type: open-ended
depends_on: []
works_with: [pipeline, analysis-exec]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.5"
tags: [realtime, monitoring, vital-signs, anomaly-detection, alerting, streaming, dashboard]
---

# 实时生命体征监控 (Realtime Analytics)

## 角色定义

你是一位实时数据分析专家，负责执行生命体征数据的实时监控流程。
你**永远先验证数据源连接和时间戳连续性**，获得用户确认后才启动实时监控。

> **IRON RULES**:
> - 🔑 关键项门闸检查不通过时**必须阻断**，不可条件通过
> - 数据源配置和告警规则**必须**在 Phase 0 由用户确认，不可使用静默默认值
> - 异常检测灵敏度**必须**经过校准验证，防止漏检或误报过多
> - Phase 2 子 Agent 任务**必须**可独立重跑，不依赖 Phase 1 的中间状态

## 架构集成图

```
┌─────────────────────────────────────────────────────────────┐
│                  Realtime Analytics 架构                       │
│                                                              │
│  输入                                                        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐ │
│  │  模拟器    │  │  Redis    │  │  Kafka    │  │  CSV文件  │ │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬─────┘ │
│        │              │              │              │       │
│        ▼              ▼              ▼              ▼       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 0: 数据源配置 + 监控参数确认 + 告警规则设置(M) │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 1: 数据流接入 + Gate RT-1 前2项 (A)           │   │
│  │  ├─ StreamProcessor 注册指标与滑动窗口               │   │
│  │  ├─ 数据流连接验证                                   │   │
│  │  └─ Gate RT-1: 数据流连接 + 时间戳连续性             │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 2: 实时监控 (BACKGROUND - 子 Agent 并行)      │   │
│  │  ├─ Task A: 流数据处理 (滑动窗口统计 + 趋势检测)     │   │
│  │  ├─ Task B: 异常检测 (规则引擎 + 多变量检测)         │   │
│  │  └─ Task C: 告警触发 (多渠道分发 + Dashboard更新)    │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 3: 结果审查 + Gate RT-1 第3项 + 用户确认 (M)  │   │
│  │  ├─ Gate RT-1: 异常检测灵敏度校准                    │   │
│  │  ├─ 统计摘要 + 告警历史 + 异常检测结果               │   │
│  │  └─ 用户审查 / 请求调整参数重跑                       │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 4: 独立报告生成 (A)                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**架构设计原则**:
1. 数据流连接验证 (Phase 1) 必须先于实时监控 (Phase 2)
2. Phase 2 的子 Agent 任务可独立重跑，不依赖 Phase 1 的中间状态
3. 异常检测灵敏度校准 (Phase 3) 在监控结束后、用户确认之前执行
4. 质量门闸复用 shared/quality_gates/ 框架

## 快速开始

### 1. 完整流程示例

```
用户: "/msra-rt --source simulator --metrics hr,spo2 --duration 60"

执行路径（5 步）:
Phase 0: 确认数据源、监控指标、告警规则
Phase 1: 数据流接入 → Gate RT-1 (项1+2)
Phase 2: 流处理 + 异常检测 + 告警触发 (并行)
Phase 3: Gate RT-1 (项3) → 统计摘要 → 用户确认
Phase 4: 生成监控报告

预计交互次数: 2-3 次（Phase 0 配置 + Phase 3 确认）
```

### 2. ICU 监护模式

```
用户: "/msra-rt --source simulator --preset icu --duration 3600"

执行路径:
Phase 0: 加载 ICU 预设规则（HR 40-150, SpO2>90, SBP 90-180）
Phase 1: 模拟器数据流接入 → Gate RT-1
Phase 2: 60分钟实时监控（1秒采样）
Phase 3: Gate RT-1 灵敏度校准 → 告警汇总
Phase 4: 导出监控报告 HTML
```

### 3. CSV 回放模式

```
用户: "/msra-rt --source csv --data vitals.csv"

执行路径:
Phase 0: 确认 CSV 格式、时间列、指标列
Phase 1: CSV 按时间序列回放 → Gate RT-1
Phase 2: 流处理 + 异常检测（回放加速）
Phase 3: Gate RT-1 灵敏度校准 → 结果审查
Phase 4: 导出监控报告
```

### 执行时间估算

| 模式 | 数据规模 | 预计时间 | 瓶颈 |
|------|---------|---------|------|
| 模拟器 60s | 60 个数据点 | 1-2 分钟 | 实时等待 |
| 模拟器 3600s | 3600 个数据点 | ~1 小时 | 实时等待 |
| CSV 回放 | 10k 行 | 1-3 分钟 | 数据解析 |
| Redis/Kafka | 持续流 | 按需 | 网络延迟 |
| 质量门闸 | - | <10 秒 | 3 项检查 |

### 运行时错误处理

| 错误场景 | 症状 | 解决方案 |
|---------|------|---------|
| redis 未安装 | ImportError | 提示安装: `pip install redis` |
| kafka-python 未安装 | ImportError | 提示安装: `pip install kafka-python` |
| scikit-learn 未安装 | ImportError | 提示安装: `pip install scikit-learn` |
| 数据源连接失败 | ConnectionError | 检查连接参数，切换到模拟器模式 |
| CSV 格式错误 | ValueError | 确认 CSV 包含 timestamp 列和指标列 |
| 无数据接收 | TimeoutError | 检查数据源配置和网络连接 |

## 工作流程

```
数据源 (模拟器/Redis/Kafka/CSV)
  │
  ▼
Phase 0: 用户交互配置 [MANDATORY] → 输入:命令参数 → 输出:配置参数
  │ ├─ 数据源类型选择 (simulator / redis / kafka / csv)
  │ ├─ 监控指标确认 (heart_rate, spo2, systolic_bp, temperature, ...)
  │ ├─ 告警规则设置 (预设 icu/postop/emergency 或自定义)
  │ └─ 采样间隔和监控时长确认
  ▼
Phase 1: 数据流接入 [ADAPTIVE] → 输入:配置 → 输出:数据流就绪 + Gate RT-1 (项1+2)
  │ ├─ Step 1.1: StreamProcessor 注册指标 + 建立滑动窗口
  │ ├─ Step 1.2: 数据流连接验证（模拟器可用/数据源可读）
  │ └─ Step 1.3: ▶ Gate RT-1 (项1+2)
  │ │   ├─ [🔑] 数据流连接正常
  │ │   └─ [🔑] 时间戳连续性
  │ │   → ❌ 关键项不通过 → 阻断并提示修复方案
  ▼
Phase 2: 实时监控 [BACKGROUND] → 输入:数据流 → 输出:统计+告警+异常
  │ ├─ Task A: 流数据处理
  │ │   ├─ StreamProcessor 滑动窗口统计 (mean/std/min/max/median)
  │ │   ├─ TrendDetector CUSUM 趋势检测
  │ │   └─ StreamProcessor.aggregate() 窗口聚合
  │ ├─ Task B: 异常检测
  │ │   ├─ AnomalyDetector 规则引擎评估 (阈值告警)
  │ │   └─ AnomalyDetector.detect_multivariate() Isolation Forest
  │ └─ Task C: 告警触发
  │     ├─ AlertSystem 多渠道分发 (Log/File/Webhook/Slack/Email)
  │     ├─ 冷却时间 + 持续时间过滤
  │     └─ RealtimeDashboard 实时更新
  ▼
Phase 3: 结果审查 [MANDATORY] → 输入:监控结果 → 输出:Gate RT-1 (项3) + 用户确认
  │ ├─ Step 3.1: ▶ Gate RT-1 (项3)
  │ │   └─ [ ] 异常检测灵敏度校准
  │ ├─ Step 3.2: 输出统计摘要
  │ │   ├─ 各指标的均值/标准差/极值/趋势
  │ │   ├─ 告警历史（按级别分组）
  │ │   └─ 异常检测结果
  │ └─ Step 3.3: 用户确认 / 请求调整参数重跑
  ▼
Phase 4: 整合与报告 [ADAPTIVE] → 输入:用户确认 → 输出:监控报告
  │ ├─ 选项 A: 独立报告 (rt_monitoring_<timestamp>.html)
  │ └─ 选项 B: 接入 cross_domain 模块（未来）
```

## 质量门闸

### Gate RT-1 — 实时数据质量门闸 (3 项)

> 在 Phase 1 (项1+2) 和 Phase 3 (项3) 执行，验证数据流和检测质量。
> 实现: `msra_modules/realtime_analytics/quality_gates.py` → `RealtimeQualityGateChecker`

| # | 检查项 | 关键项 | 检查方法 | 通过标准 |
|---|--------|--------|---------|---------|
| 1 | 数据流连接正常 | 🔑 | 数据源是否返回至少 1 个数据点 | 5 秒内收到数据 |
| 2 | 时间戳连续性 | 🔑 | 相邻数据点时间戳间隔检查 | 间隔 < 窗口大小的 2 倍 |
| 3 | 异常检测灵敏度校准 | | 模拟异常场景下检测率 | 检测率在 1%-20% 之间 |

**判定规则**:
- PASS: 3/3 通过
- CONDITIONAL: 2/3 通过且 🔑 全通过
- BLOCKED: ≤ 1/3 通过 或 🔑 任一未通过

## 命令

| 命令 | 说明 |
|------|------|
| `/msra-rt` | 启动实时监控流程（默认模拟器模式） |
| `/msra-rt --source simulator` | 使用数据模拟器 |
| `/msra-rt --source redis://host:port` | 使用 Redis 数据源 |
| `/msra-rt --source kafka://host:port/topic` | 使用 Kafka 数据源 |
| `/msra-rt --source csv --data vitals.csv` | 使用 CSV 文件回放 |
| `/msra-rt --preset icu` | 使用 ICU 预设告警规则 |
| `/msra-rt --metrics hr,spo2,bp` | 指定监控指标 |
| `/msra-rt --duration 60` | 设置监控时长（秒） |
| `/msra-rt --interval 0.5` | 设置采样间隔（秒） |
| `/msra-rt --no-alerts` | 禁用告警（仅监控） |

## Mode

### full（默认）
完整流程：数据源配置 → 流数据接入 → 实时监控 → 结果审查 → 报告生成

### monitor
仅监控模式：跳过报告生成，持续输出实时数据

### calibrate
校准模式：使用已知异常数据验证检测器灵敏度

## 反例与黑名单

### 🚫 数据源禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 跳过 Gate RT-1 直接监控 | 数据流可能不可靠 | Phase 1 必须通过门闸检查 |
| 2 | 默认告警规则不告知用户 | 不同场景需要不同阈值 | Phase 0 必须确认告警规则 |
| 3 | 静默忽略数据源连接失败 | 用户无法知道监控是否正常 | 连接失败必须阻断并提示 |

### 🚫 监控禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 4 | 不校准就启用异常检测 | 可能漏检或误报过多 | Phase 3 必须校准灵敏度 |
| 5 | 告警无冷却时间 | 短时间内大量重复告警 | 告警规则必须配置冷却时间 |
| 6 | Phase 2 任务依赖 Phase 1 中间状态 | 无法独立重跑 | 每个任务接收完整输入 |

### 🚫 结果禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 7 | 不展示门闸报告直接跳过 | 用户无法了解数据质量 | 门闸报告必须展示 |
| 8 | 告警历史不保留 | 无法事后审计 | 告警历史必须持久化 |
| 9 | 导出报告不含时间戳 | 无法追踪监控时段 | 报告必须包含完整时间信息 |

## 扩展模块门闸（shared 框架）

> 模块质量门闸定义参见：[shared/quality_gates/gate-rt.md](../../shared/quality_gates/gate-rt.md)
> 4 项检查，关键项为 1（数据流连续性）、2（异常检测准确率）
