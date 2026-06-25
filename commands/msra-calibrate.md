---
description: Run metric calibration against a gold standard, or view calibration status
argument-hint: "[gold_standard.csv] [--status] [--update results.csv]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# MSRA Calibrate

路由到 `skills/calibration/SKILL.md`，传入用户参数 `$ARGUMENTS`。

## 参数解析

- `<gold_standard.csv>` — 金标准数据文件，触发校准
- `--status` — 查看当前校准状态
- `--update <results.csv>` — 增量更新校准数据库

校准协议、TPR/FPR 累积逻辑、门闸联动规则均在 `skills/calibration/SKILL.md` 中定义。
