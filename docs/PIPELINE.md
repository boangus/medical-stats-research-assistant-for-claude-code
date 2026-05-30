# MSRA 架构文档

**版本**: 0.4.0 | **最后更新**: 2026-05-29

## 概述

Medical Statistics Research Assistant (MSRA) 采用 **Pipeline 驱动** 的模块化架构。5 个 Skill 通过统一的 Pipeline 编排器串联，覆盖从原始数据到最终报告的完整医学统计分析流程，包括 3 个阻断式质量门闸（Stage 1.5/2.5/3.5）。

## 架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                     Claude Code Interface                        │
│  manifest.json 注册 5 个命令，由 Pipeline 编排器统一调度          │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│              Pipeline Orchestrator (pipeline/SKILL.md)            │
│                                                                   │
│  职责: 意图检测 → 阶段路由 → 前置检查 → 调度执行 → Checkpoint    │
│  核心原则: 纯调度，不做实质性工作                                  │
└──┬─────────────┬──────────────┬──────────────┬───────────────────┘
   │             │              │              │
   ▼             ▼              ▼              ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Data   │ │Analysis  │ │Analysis │ │ Report       │
│ Prep   │ │Plan      │ │Exec     │ │ Generation   │
│ Stage1 │ │Stage 2   │ │Stage 3  │ │ Stage 4      │
└───┬────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
    │           │             │              │
    ├── Stage 1.5: Data Quality Gate ────────┤
    │           │             │              │
    └───────────┴──────┬──────┴──────────────┘
                       ▼
              ┌────────────────┐
              │  Shared Layer  │
              │                │
              │ • 统计方法目录    │
              │ • 检查清单        │
              │ • 代码模板(R/Py)  │
              │ • 可视化模板      │
              │ • 样本量计算      │
              │ • 因果推断工作流  │
              └────────────────┘
```

## 分层架构

### 1. 接口层 (Interface Layer)

通过 `manifest.json` 注册 5 个命令，映射到 5 个 Skill：

| 命令 | Skill | 功能 |
|------|-------|------|
| `/msra` | pipeline | 启动流水线（自动检测入口） |
| `/msra-data` | data-prep | 数据验证与清洗（含 Stage 1.5 质量门闸） |
| `/msra-plan` | analysis-plan | 分析计划制定 |
| `/msra-exec` | analysis-exec | 分析执行 |
| `/msra-report` | report | 报告生成 |

### 2. 编排层 (Pipeline Orchestrator)

Pipeline 编排器负责：
- **意图检测**: 通过用户输入关键词自动判断入口阶段
- **阶段路由**: 路由到对应的 Skill，推荐最佳 Mode
- **前置检查**: 验证前置产物是否存在且有效
- **Checkpoint**: 每个阶段结束后展示 Dashboard 并等待用户确认
- **进度追踪**: 记录各阶段完成状态和产物版本

**核心原则**: Pipeline 纯调度，不做实质性统计分析工作。

### 3. Skill 层 (Skills Layer)

每个 Skill 是独立的功能模块，以 `SKILL.md` 为核心：

```
skills/{skill-name}/
└── SKILL.md          # Skill 定义 + 系统提示词 + 工作流程
```

Skill 包含：
- **Frontmatter**: id、name、description、data_access_level、task_type
- **角色定义**: AI 在该 Skill 中扮演的角色
- **工作流程**: 分 Phase 执行，带 Checkpoint
- **命令和 Mode**: 支持 guided/quick/sap-guided/exploratory 等多种模式
- **反例黑名单**: 禁止行为的详尽清单（4-15条）
- **分层验证框架**: 三层验证（自动化+LLM+重复性）

### 4. 共享层 (Shared Layer)

跨 Skill 共享的资源，存放在 `shared/` 目录：

```
shared/
├── statistical-methods/        # 统计方法目录
│   └── methods_catalog.md      # 方法索引（8 类方法）
├── checklists/                 # 质量检查清单
│   └── quality_checklist.md    # 8 维度结构化检查清单
├── templates/                  # 代码模板
│   ├── table1_template.R              # Table 1 生成 (R)
│   ├── survival_analysis_template.R   # 生存分析模板 (R)
│   ├── logistic_template.py           # Logistic 回归 (Python)
│   ├── cox_template.py                # Cox 回归 (Python)
│   ├── roc_template.py                # ROC 诊断分析 (Python)
│   ├── forest_plot_template.R         # 森林图 (R)
│   ├── forest_plot_template.py        # 森林图 (Python)
│   ├── roc_visualization_template.R   # ROC 可视化 (R)
│   ├── bland_altman_template.R        # Bland-Altman 图 (R)
│   ├── bland_altman_template.py       # Bland-Altman 图 (Python)
│   └── calibration_plot_template.R    # 校准曲线 (R)
├── sample-size/                 # 样本量计算
│   ├── sample_size_calculator.R       # 样本量计算 (R)
│   └── sample_size_calculator.py      # 样本量计算 (Python)
└── causal-inference/            # 因果推断
    ├── causal_inference_workflow.md   # DAG + PSM 工作流指南
    └── psm_template.py                # 倾向性评分匹配 (Python)
```

### 5. 配置层 (Config Layer)

- `manifest.json`: 插件清单（版本、命令、依赖）
- `.gitignore`: 版本控制排除规则

## 数据流

### 典型交互流程

```
用户输入 → Pipeline 编排器 → 意图检测 → 阶段路由 → 前置检查
                                                      ↓
                                           Skill 加载 + 共享资源
                                                      ↓
                                           AI 处理 + 代码生成 + 执行
                                                      ↓
                                           Checkpoint Dashboard
                                                      ↓
                                          用户确认 → 下一阶段 / 回退
```

### 示例: `/msra 我有原始数据`

1. **用户输入**: `/msra 我有原始数据，想完成整个分析`
2. **意图检测**: 检测到关键词「原始数据」→ 入口为 Stage 1
3. **前置检查**: 无前置产物要求 → 直接进入
4. **调度 Skill**: 加载 `data-prep/SKILL.md`
5. **执行**: 数据验证→清洗策略讨论→执行清洗→变量构造→盲态审核→数据库锁定
6. **Checkpoint**: 展示清洗摘要 + 变量清单，等待用户确认
7. **下一阶段**: 用户确认后进入 Stage 2 (analysis-plan)

## Checkpoint 机制

每个 Stage 结束后必须展示格式化 Dashboard 并等待用户确认：

```
╔══════════════════════════════════════════════════╗
║           MSRA Pipeline Checkpoint               ║
╠══════════════════════════════════════════════════╣
║ 当前阶段: Stage {N} ✅ 已完成                     ║
║ 下一阶段: Stage {N+1}                             ║
║                                                   ║
║ 本阶段产物:                                       ║
║  ✅ {产物1}                                       ║
║  ✅ {产物2}                                       ║
╚══════════════════════════════════════════════════╝
```

## 设计原则

1. **Pipeline 驱动**: Pipeline 只做调度，不做实质性工作
2. **人机回环**: 关键决策点必须用户确认
3. **可重复性**: 所有步骤生成可重复代码
4. **质量优先**: 内置多层验证和 Checkpoint
5. **模块化**: 每个 Skill 单一职责，可独立扩展

## 扩展指南

### 添加新 Skill

1. 创建 `skills/{new-skill}/SKILL.md`（按现有格式）
2. 在 `manifest.json` 的 `skills` 数组中注册
3. 在 pipeline/SKILL.md 的 Stage 列表中引用
4. 添加所需的共享资源

### 添加新统计方法

1. 在 `shared/statistical-methods/methods_catalog.md` 中添加
2. 创建对应的代码模板（shared/templates/）
3. 在相关 SKILL.md 中引用

## 已知限制与改进方向

详见 [GAP_ANALYSIS.md](GAP_ANALYSIS.md)

- 缺少多 Agent 协作架构（Phase 3 规划）
- ~~缺少独立质量门闸阶段~~ ✅ Stage 1.5 + Stage 2.5 + Stage 3.5 已添加
- ~~仅 R 模板，缺 Python 版本~~ ✅ 已补充 Python 模板
- ~~缺因果推断子流程~~ ✅ 已添加 causual-inference 模块
- ~~缺可视化模板~~ ✅ 已补充森林图、ROC、Bland-Altman、校准曲线模板
- 缺测试和脚本基础设施（Phase 4 规划）



