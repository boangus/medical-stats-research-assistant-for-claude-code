---
description: "MSRA Pipeline — 统一流水线：数据 → 统计报告 → (可选) 论文"
argument-hint: "[context] [--from <stage>] [--status] [--quick]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# MSRA Pipeline

路由到 `skills/pipeline/SKILL.md`，传入用户参数 `$ARGUMENTS`。

## 参数解析

- `<context>` — 自然语言上下文，由 Pipeline 进行意图检测
- `--from <stage>` — 指定入口阶段（data/plan/exec/report）
- `--status` — 查看当前进度
- `--quick` — 快速模式（跳过可选步骤）

业务逻辑、阶段路由、Checkpoint 规则均在 `skills/pipeline/SKILL.md` 中定义。
