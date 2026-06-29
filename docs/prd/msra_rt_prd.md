# MSRA Realtime Analytics 模块 PRD

> **版本**: v1.0 | **日期**: 2026-06-25 | **状态**: 待评审

---

## 1. 项目信息

- **Language**: 中文
- **Programming Language**: Python（引擎层）+ Markdown（SKILL 定义）
- **Project Name**: `msra_realtime_analytics`
- **命令入口**: `/msra-rt`
- **成熟度目标**: Alpha → Beta

### 原始需求复述

为 MSRA（Medical Statistics Research Assistant）Claude Code 插件开发实验性模块中的 **realtime_analytics（实时数据分析）** 模块（Phase 3）。该模块需遵循方案C（Skill入口 + Agent执行）架构，完成 SKILL.md 编写、命令注册、质量门闸实现、测试用例补全等工作，将模块从 Alpha 提升至 Beta 成熟度。

---

## 2. 产品定义

### 2.1 产品目标

| # | 目标 | 衡量标准 |
|---|------|----------|
| G1 | **提供独立可用的实时生命体征监控能力** | 用户通过 `/msra-rt` 可完成数据接入→流处理→异常检测→告警→报告 全流程 |
| G2 | **达到 Beta 成熟度标准** | SKILL.md 完成 + 测试覆盖率 ≥ 50% + 质量门闸实现 + manifest 命令注册 |
| G3 | **保持与已有模块架构一致性** | 遵循 bioinformatics/imaging 模块相同的 Phase 0-4 Skill 结构和子Agent调度模式 |

### 2.2 用户故事

| # | 用户故事 |
|---|---------|
| US-1 | 作为**临床研究人员**，我希望通过 `/msra-rt` 命令接入生命体征数据流，以便实时监控患者心率、血压、血氧等指标 |
| US-2 | 作为**临床研究人员**，我希望系统能自动检测异常值并发出告警，以便及时发现临床危急事件 |
| US-3 | 作为**数据分析师**，我希望配置自定义告警规则（阈值、持续时间、冷却时间），以便适配不同研究场景的监控需求 |
| US-4 | 作为**项目负责人**，我希望查看实时监测报告（含统计摘要和告警历史），以便回顾监控期间的整体情况 |
| US-5 | 作为**开发者/测试人员**，我希望使用内置数据模拟器进行无真实数据源的端到端测试，以便在开发阶段验证全流程 |

---

## 3. 需求池

### P0 — 必须实现（阻断性）

| ID | 需求 | 说明 |
|----|------|------|
| P0-1 | **SKILL.md 编写** | 创建 `skills/realtime-monitor/SKILL.md`，包含 Phase 0-4 完整定义、角色定义、铁律、架构集成图 |
| P0-2 | **命令注册** | 在 `manifest.json` 中注册 `/msra-rt` 命令，指向 `skills/realtime-monitor/SKILL.md` |
| P0-3 | **Gate RT-1 质量门闸实现** | 实现 `src/shared/quality_gates/` 中的 RT-1 门闸（3项检查：数据流连接、时间戳连续性、异常检测灵敏度） |
| P0-4 | **StreamProcessor 核心补全** | 补全 `add_data_point` 的事件总线机制、窗口过期清理的自动调度、多指标并发处理 |
| P0-5 | **AnomalyDetector 多变量检测** | 补全设计文档中定义的 Isolation Forest、DBSCAN 算法（当前仅有规则引擎 + TrendDetector） |
| P0-6 | **单元测试** | 为 stream_processor、anomaly_detector、alert_system、dashboard、data_simulator 编写单元测试，覆盖率 ≥ 50% |
| P0-7 | **SKILL.md 中定义子Agent任务描述** | Phase 2 重计算任务定义（流数据处理 + 异常检测 + 告警触发），供子Agent执行 |

### P1 — 应该实现

| ID | 需求 | 说明 |
|----|------|------|
| P1-1 | **Redis 状态存储集成** | StreamProcessor 可选使用 Redis 进行滑动窗口状态持久化和分布式状态共享 |
| P1-2 | **Prometheus 指标采集** | RealtimeDashboard 可选导出 Prometheus 格式指标 |
| P1-3 | **集成测试** | 端到端测试：模拟数据 → 流处理 → 异常检测 → 告警 → 报告生成 |
| P1-4 | **告警规则模板库** | 预置 ICU 通用、术后监护、急诊等场景的告警规则模板 |
| P1-5 | **Dashboard 快照导出** | 支持将实时仪表盘数据导出为 JSON/HTML 快照，用于离线分析 |

### P2 — 可以实现

| ID | 需求 | 说明 |
|----|------|------|
| P2-1 | **Plotly 交互式可视化** | 使用 Plotly 生成趋势图、异常点标注、告警时间线 |
| P2-2 | **Streamlit Web 仪表盘** | 完善 `create_streamlit_app`，实现可独立运行的 Web 监控面板 |
| P2-3 | **LSTM Autoencoder 时序异常** | 深度学习时序异常检测（需要 PyTorch 可选依赖） |
| P2-4 | **Kafka 实际接入** | 验证 Kafka 生产者/消费者的完整链路（当前代码已有框架，但未测试） |

---

## 4. UI 交互设计（Phase 定义）

### Phase 0: 数据源配置（MANDATORY — 用户交互）

```
/msra-rt [options]

选项:
  --source <type>     数据源类型: simulator | redis | kafka | csv
  --duration <int>    监控时长（秒，默认 3600）
  --interval <float>  采样间隔（秒，默认 1.0）
  --metrics <list>    监控指标列表（默认: heart_rate, spo2, systolic_bp, temperature）
  --preset <name>     预设规则模板: icu | postop | emergency | custom
  --no-alerts         禁用告警（仅监控）

示例:
  /msra-rt                                    # 使用模拟数据，默认配置
  /msra-rt --source simulator --preset icu    # 模拟器 + ICU 预设
  /msra-rt --source redis://localhost:6379    # Redis 数据源
```

**交互流程**：
1. 确认数据源类型（模拟器/Redis/Kafka/CSV文件）
2. 确认监控指标和基线参数
3. 选择告警规则预设或自定义规则
4. 确认采样间隔和监控时长
5. **Gate RT-1 前两项检查**（数据流连接 + 时间戳连续性）

### Phase 1: 流数据接入（ADAPTIVE — 可自动）

```
输入: 数据源配置（Phase 0 产出）
  │
  ├─ 模拟器模式: VitalSignsSimulator 生成数据流
  ├─ Redis 模式: 从 Redis Stream 读取
  ├─ Kafka 模式: 从 Kafka Topic 消费
  └─ CSV 模式: 按时间序列回放文件
  │
  ▼
StreamProcessor 注册指标 → 建立滑动窗口 → 验证时间戳连续性
  │
  ▼
Gate RT-1 检查 (项1+2): 数据流连接正常 + 时间戳无过大间隔
```

### Phase 2: 实时监控（BACKGROUND — 子Agent执行）

```
子Agent任务定义:

Task A: 流数据处理
  - StreamProcessor 实时计算滑动窗口统计（均值/标准差/分位数）
  - TrendDetector CUSUM 趋势检测

Task B: 异常检测
  - AnomalyDetector 规则引擎评估（阈值告警）
  - 多变量异常检测（Isolation Forest / DBSCAN）

Task C: 告警触发
  - AlertSystem 多渠道分发（Log/File/Webhook/Slack/Email）
  - 冷却时间 + 持续时间过滤
  - Dashboard 实时更新
```

### Phase 3: 结果审查（MANDATORY — 用户交互）

```
Gate RT-1 第3项检查: 异常检测灵敏度校准
  │
  ▼
输出:
  ├─ 统计摘要（各指标的均值/标准差/极值/趋势）
  ├─ 告警历史（按级别分组，含触发时间/规则/当前值）
  ├─ 异常检测结果（规则触发 + 多变量检测）
  └─ 实时监控报告（HTML/Markdown）
  │
  ▼
用户审查 → 确认/调整参数重跑
```

### Phase 4: 整合（ADAPTIVE）

```
独立使用（默认）:
  └─ 生成监控报告 → MSRA/reports/rt_monitoring_<timestamp>.html

可选整合:
  └─ 时序指标 → 接入 cross_domain 模块（未来 Phase 4）
```

---

## 5. 技术规范

### 5.1 现有代码评估

| 文件 | 状态 | 补全需求 |
|------|------|----------|
| `stream_processor.py` | ✅ 基本可用 | 补全事件总线自动调度、多指标并发、Redis 集成 |
| `anomaly_detector.py` | ⚠️ 部分完成 | 补全 Isolation Forest / DBSCAN 多变量检测 |
| `alert_system.py` | ✅ 基本可用 | 无重大缺失，可选增强 |
| `dashboard.py` | ⚠️ 部分完成 | `create_streamlit_app` 使用了废弃 API |
| `data_simulator.py` | ✅ 基本可用 | 无重大缺失 |
| `__init__.py` | ✅ 完成 | 多变量检测器导出需更新 |

### 5.2 新增文件清单

| 文件 | 说明 |
|------|------|
| `skills/realtime-monitor/SKILL.md` | Skill 定义（Phase 0-4 + 门闸 + 铁律） |
| `manifest.json` 更新 | 新增 `/msra-rt` 命令条目 |
| `src/shared/quality_gates/rt_gates.py` | Gate RT-1 实现 |
| `tests/test_stream_processor.py` | 流处理器测试 |
| `tests/test_anomaly_detector.py` | 异常检测器测试 |
| `tests/test_alert_system.py` | 告警系统测试 |
| `tests/test_dashboard.py` | 仪表盘测试 |
| `tests/test_data_simulator.py` | 数据模拟器测试 |
| `tests/test_rt_integration.py` | 集成测试 |

### 5.3 依赖要求

```python
# 核心（已在项目中）
numpy >= 1.24

# 可选（extras_require[realtime_analytics]）
redis >= 5.0              # 缓存与状态存储
prometheus-client >= 0.19 # 指标采集
plotly >= 5.18            # 交互式图表
streamlit >= 1.30         # Web 仪表盘（P2）
scikit-learn >= 1.3       # Isolation Forest / DBSCAN
```

### 5.4 manifest.json 命令注册

```json
"/msra-rt": {
  "id": "msra-rt",
  "name": "Realtime Analytics",
  "entry_point": "skills/realtime-monitor/SKILL.md",
  "description": "Real-time vital signs monitoring: stream processing, anomaly detection, alerting, and dashboard. Supports simulator, Redis, Kafka data sources.",
  "usage": "/msra-rt [--source simulator|redis|kafka|csv] [--preset icu|postop|emergency] [--duration seconds]",
  "examples": [
    "/msra-rt",
    "/msra-rt --source simulator --preset icu --duration 600",
    "/msra-rt --source redis://localhost:6379"
  ]
}
```

### 5.5 Gate RT-1 实现设计

```
Gate RT-1（实时数据质量）— 3项检查:

1. [🔑] 数据流连接正常
   - 检查: 数据源是否成功连接并返回至少 1 个数据点
   - 失败条件: 5 秒内无数据 / 连接拒绝

2. [🔑] 时间戳连续性
   - 检查: 相邻数据点时间戳间隔不超过预期采样间隔的 5 倍
   - 失败条件: 检测到超过 3 个过大间隔

3. [ ] 异常检测灵敏度校准
   - 检查: 模拟异常场景下检测器能正确触发
   - 失败条件: 10 个已知异常中漏检超过 3 个
```

---

## 6. 待确认问题（Open Questions）

| # | 问题 | 影响范围 | 建议 |
|---|------|----------|------|
| Q1 | `AnomalyDetector` 中 `Alert` 类与 `alert_system.py` 中 `Alert` 类存在命名冲突（两个同名类），如何统一？ | P0-5, P0-3 | 建议将 `anomaly_detector.py` 中的 `Alert` 重命名为 `DetectionResult`，`alert_system.py` 的 `Alert` 作为统一告警事件 |
| Q2 | 多变量异常检测（Isolation Forest/DBSCAN）是否作为 P0 实现？设计文档列出了 5 种算法，但当前代码仅有规则引擎 | P0-5 | 建议 P0 实现 Isolation Forest（scikit-learn 依赖轻量），DBSCAN 和 LSTM 降为 P2 |
| Q3 | Redis/Kafka 集成的优先级？当前设计为"可选依赖"，但 Phase 1 的流数据接入需要某种数据源 | P0-1, P1-1 | 建议 P0 阶段以模拟器为默认数据源，Redis 集成作为 P1 |
| Q4 | `dashboard.py` 的 `create_streamlit_app` 使用了 `st.experimental_rerun`（已废弃），是否在此 PRD 中修复？ | P1-5 | 建议在 P1 阶段修复为 `st.rerun()` |
| Q5 | 与主 Pipeline 的集成点明确为"不接入"（独立运行），是否需要为未来 cross_domain 模块预留接口？ | P2 | 建议在 `__init__.py` 中预留 `export_metrics_for_cross_domain()` 方法签名（空实现） |
| Q6 | 测试框架选择？项目现有测试使用 pytest 还是 unittest？ | P0-6 | 需确认项目统一测试框架 |

---

## 7. 开发计划（Phase 3 路线图）

```
Phase 3: realtime_analytics (~6.5 天)

Day 1:   skills/realtime-monitor/SKILL.md
Day 2-3: msra_modules/realtime_analytics/ 引擎补全
         - 多变量异常检测
         - 命名冲突修复
         - 事件总线完善
Day 4:   Gate RT-1 质量门闸实现 + manifest.json 注册
Day 5:   单元测试 + 集成测试
Day 6:   文档更新 + 端到端验证
```

---

**文档结束**
