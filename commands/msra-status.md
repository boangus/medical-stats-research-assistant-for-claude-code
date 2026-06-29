---
description: "MSRA 状态查看 — 显示 Pipeline 进度、门闸状态、产物清单"
argument-hint: "[--verbose] [--json]"
allowed-tools: Read, Bash, Grep, Glob
---

# MSRA Status

显示当前 Pipeline 的执行状态和进度。

## 参数解析

- `--verbose` — 详细输出（含每个产物的文件大小、生成时间、SHA256 哈希）
- `--json` — JSON 格式输出（含 current_stage/completed_stages/gates/artifacts 字段）

## 实现步骤

1. 扫描工作目录下的 `.msra/` 文件夹
2. 读取 `passport.json`（如存在）解析阶段完成状态
3. 检查各阶段产物文件是否存在
4. 汇总质量门闸（Stage 1.5/2.5/3.5）状态
5. 输出格式化报告

门闸检查项定义参见 `src/shared/quality_gates/gate-*.md`。
