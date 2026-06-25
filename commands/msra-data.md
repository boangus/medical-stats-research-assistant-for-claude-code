---
description: Data validation, cleaning, and quality gate (Stage 1)
argument-hint: "[file] [--dict dictionary.xlsx] [--quick] [--quality-gate]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# MSRA Data

路由到 `skills/data-prep/SKILL.md`，传入用户参数 `$ARGUMENTS`。

## 参数解析

- `<file>` — 原始数据文件路径
- `--dict <dictionary.xlsx>` — 数据字典文件
- `--quick` — 快速验证模式
- `--quality-gate` — 仅运行 Stage 1.5 门闸检查

数据验证、交互式清洗、值规范化、盲态审核、数据库锁定等流程均在 `skills/data-prep/SKILL.md` 中定义。
