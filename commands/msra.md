---
description: "MSRA Pipeline — 统一流水线：数据 → 统计报告 → (可选) 论文"
argument-hint: "[context] [--from <stage>] [--status] [--quick]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# MSRA Pipeline

加载 `skills/pipeline/SKILL.md` 并传入用户参数 `$ARGUMENTS`。

## 行为

1. **意图检测**: 分析用户输入，自动识别当前阶段
2. **阶段路由**: 根据意图路由到正确的 Skill
3. **前置检查**: 验证前置产物是否完整
4. **Checkpoint**: 每个阶段结束后暂停等待确认

## 快速命令

- `/msra` — 自动检测入口，启动流水线
- `/msra --from plan` — 从 Stage 2 开始
- `/msra --status` — 查看当前进度
- `/msra --quick` — 快速模式（跳过可选步骤）
