---
description: MSRA paper reviewer — simulated 5-person peer-review panel
model: opus
---

# MSRA Reviewer

路由到 `skills/peer-review/SKILL.md`（full 模式），传入用户参数 `$ARGUMENTS`。

## 参数解析

默认 `full` 模式；支持显式指定子模式：`quick` / `methodology-focus` / `re-review` / `guided` / `calibration`。

5 位审稿人（主编 + 方法学 + 临床 + 统计 + 伦理）角色定义、评审流程、Editorial Decision + Revision Roadmap 生成均在 `skills/peer-review/SKILL.md` 中定义。使用 opus 模型以保证评审深度。
