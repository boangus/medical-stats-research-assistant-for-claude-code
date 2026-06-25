---
description: Exploratory causal analysis — discover potential causal structures from data
argument-hint: "[file] [--mode causal-discovery|confounding-analysis|exploratory-eda|hypothesis-generation|sensitivity-pre|direction-advisory]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# MSRA Explore

路由到 `skills/exploratory-causal/SKILL.md`，传入用户参数 `$ARGUMENTS`。

## 参数解析

- `<file>` — 清洗后数据文件
- `--mode <mode>` — 分析模式：
  - `causal-discovery` / `confounding-analysis` / `exploratory-eda`
  - `hypothesis-generation` / `sensitivity-pre` / `direction-advisory`

5 阶段探索性因果分析工作流、Guard check（Stage 1.5 门闸验证）、研究方向的报告生成均在 `skills/exploratory-causal/SKILL.md` 中定义。
