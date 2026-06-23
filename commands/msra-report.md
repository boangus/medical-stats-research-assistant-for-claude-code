---
description: "MSRA Report — 生成出版级统计报告 (Stage 4)"
argument-hint: "[guideline] [--type <table1|forest|km|roc>]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# MSRA Report

加载 `skills/report/SKILL.md`（报告生成模式）并传入用户参数 `$ARGUMENTS`。

## 行为

1. **报告生成**: 基于 Stage 3 分析结果生成报告
2. **规范检查**: 按报告规范 (CONSORT/STROBE 等) 验证
3. **表格/图表**: 生成出版级表格和图表
4. **DOCX 导出**: 可选导出为 Word 格式

## 快速命令

- `/msra-report` — 生成完整统计报告
- `/msra-report CONSORT` — 按 CONSORT 规范生成
- `/msra-report --type table1` — 仅生成基线表
