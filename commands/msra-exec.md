---
description: Execute analysis per approved SAP (Stage 3)
argument-hint: "--sap [plan] --data [data] [--check-only]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# MSRA Exec

路由到 `skills/analysis-exec/SKILL.md`，传入用户参数 `$ARGUMENTS`。

## 参数解析

- `--sap <plan>` — 已批准的统计分析计划文件
- `--data <data>` — 清洗后数据文件
- `--check-only` — 仅运行质检，不执行完整分析

变量构造、描述性统计、主分析/敏感性/安全/亚组分析、假设检验、自愈机制等流程均在 `skills/analysis-exec/SKILL.md` 中定义。
