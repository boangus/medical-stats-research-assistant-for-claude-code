---
description: MSRA paper writing — 9 modes for writing, revision, and export
argument-hint: "--mode <abstract-only|citation-check|disclosure|format-convert|outline-only|plan|revision|revision-coach|lit-review>"
---

# MSRA Write

路由到 `skills/report/SKILL.md`（medical-paper skill），按指定模式执行。

## 参数解析

解析 `--mode` 标志，支持以下 9 种模式：

| Mode | 输出 | 模型 |
|------|------|------|
| `abstract-only` | 双语摘要 + 关键词 | sonnet |
| `citation-check` | 引用错误报告 | sonnet |
| `disclosure` | AI 使用披露声明 | sonnet |
| `format-convert` | LaTeX/DOCX/PDF/Markdown 互转 | sonnet |
| `outline-only` | 详细大纲 + 证据图 | sonnet |
| `plan` | 苏格拉底式逐章规划 | sonnet |
| `revision` | 修订稿 + R&R 回复 | sonnet |
| `revision-coach` | 修订路线图 + 回复信骨架 | opus |
| `lit-review` | 注释参考文献综述 | sonnet |

`--mode` 缺失或无效时，列出可选模式并询问用户。各模式的详细执行流程在 `skills/report/SKILL.md` 中定义。
