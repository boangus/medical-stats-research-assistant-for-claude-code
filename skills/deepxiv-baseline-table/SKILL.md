---
name: deepxiv-baseline-table
description: Build a markdown baseline table for a research topic using deepxiv search, brief, head, and experiment-section reads, extracting paper title, URL, open-source status, datasets, benchmark scores, and other comparison-ready details.
---

# DeepXiv Baseline Table

Use this skill when the user wants to map a topic into a comparison table, baseline survey, benchmark roundup, or "what papers evaluated on which datasets with what scores and whether code is open".

Typical requests:
- "Find recent baseline papers on agentic memory"
- "What papers in the last month evaluated on dataset X?"
- "Make me a markdown table of methods, datasets, and scores"

## Goal

Turn a topic search into a structured markdown table:

1. Search recent papers with `deepxiv search`
2. Brief all candidates with `deepxiv paper <id> --brief`
3. Keep the relevant papers, prioritizing papers with GitHub/code
4. Inspect promising papers with `deepxiv paper <id> --head`
5. Read experiment-related sections with `deepxiv paper <id> --section ...`
6. Extract datasets, evaluation setup, and reported scores
7. Write a markdown table summarizing the baselines

## Default Workflow

### 1. Search by topic and date range

Use a broad search first.

```bash
deepxiv search "agentic memory" --date-from 2026-03-01 --limit 100 --format json
```

Default heuristics:
- Use the user’s exact topic phrase first
- Keep `--limit` high enough to avoid missing relevant papers
- If results are noisy, refine the query with close variants

Examples:

```bash
deepxiv search "agentic memory" --date-from 2026-03-01 --limit 100 --format json
deepxiv search "memory agents long-horizon" --date-from 2026-03-01 --limit 100 --format json
deepxiv search "agent memory benchmark" --date-from 2026-03-01 --limit 100 --format json
```

### 2. Brief all candidates

For each arXiv ID, fetch:

```bash
deepxiv paper <arxiv_id> --brief
```

Capture:
- title
- arXiv ID
- publish date
- TLDR
- keywords
- GitHub URL
- PDF/source URL

This is the screening step. Do not read full sections yet.

### 3. Filter and prioritize

Keep papers that are actually about the topic, not just adjacent terms.

Prioritize:
- papers directly centered on the topic
- empirical papers over purely conceptual ones
- papers with GitHub/code
- benchmark or comparison papers
- papers with clear experiment sections

De-prioritize:
- purely opinion or survey papers unless the user asked for surveys
- papers with no clear evaluation evidence
- papers only loosely related to the topic

If the list is still large, keep a primary set and a secondary set:
- Primary: strongest and most relevant baselines
- Secondary: adjacent or weaker evidence

### 4. Inspect paper structure

For retained papers:

```bash
deepxiv paper <arxiv_id> --head
```

Use `--head` to find experiment-bearing sections such as:
- Experiments
- Evaluation
- Results
- Benchmark
- Main Results
- Analysis

Also capture:
- abstract
- total token count
- section names

### 5. Read only experiment-relevant sections

Once the right sections are known, read only those:

```bash
deepxiv paper <arxiv_id> --section Experiments
deepxiv paper <arxiv_id> --section Evaluation
deepxiv paper <arxiv_id> --section Results
```

Section selection guidance:
- Start with `Experiments` or `Evaluation`
- Read `Results` if the metrics are not clear
- Read `Introduction` only if the task setup is still ambiguous
- Read `Appendix` only if benchmark details are missing from the main paper

Avoid reading the entire paper unless the user explicitly asks for it.

## Extraction Targets

For each retained paper, try to extract:

- Title
- arXiv ID
- Paper URL
- GitHub/code URL
- Open-source status: `Yes`, `No`, or `Unknown`
- Main task
- Evaluation datasets / benchmarks
- Key metrics
- Best reported scores
- Notes on experimental setting

If exact scores are not clearly available from the inspected sections:
- leave the score field as `Not clearly stated`
- do not invent or infer a number

If datasets are only partially visible:
- include the datasets you can verify
- mention that the list may be incomplete

## Markdown Output

Write a markdown file in the workspace unless the user specifies another path.

Recommended filename:

```text
<topic>-baseline-table-YYYY-MM-DD.md
```

Example:

```text
agentic-memory-baseline-table-2026-04-01.md
```

Recommended output structure:

```md
# Agentic Memory Baseline Table

Topic: agentic memory
Date range: 2026-03-01 to 2026-04-01
Search source: deepxiv

## Summary

- Number of search results
- Number of relevant papers retained
- Number with public code
- Main recurring datasets or benchmark families

## Baseline Table

| Title | arXiv | URL | Open Source | Code URL | Datasets / Benchmarks | Metrics / Scores | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Inclusion Notes

- Which papers were excluded and why
- Which rows are based only on `--brief`
- Which rows were verified through `--head` and experiment/result sections

## Observations

- Common evaluation datasets
- Which papers appear strongest
- Where the benchmark story is still fragmented
```

## Writing Rules

- Prefer verified facts over broad summaries
- Separate "paper is relevant" from "paper has strong benchmark evidence"
- Be explicit when a row is missing score details
- Mark open-source status conservatively
- Keep the table compact but useful
- Add short notes when comparisons are not apples-to-apples

## Decision Rules

- Always start with search and brief
- Prefer papers with GitHub when deciding which ones to inspect first
- Use `--head` before `--section`
- Read only the sections needed to recover datasets and scores
- If the topic is broad, tell the user when the table mixes multiple subtask types

---

## 反例与黑名单

> **以下行为必须避免**。违反任何一条将导致基线表格不可靠或误导用户。

### 🚫 搜索禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 只用一个关键词搜索 | 遗漏使用不同术语的相关论文 | 使用用户原始短语 + 至少2个变体关键词搜索 |
| 2 | 不设置日期范围就搜索 | 结果过多难以筛选，过时论文权重过高 | 设置合理的日期范围(如近2年) |
| 3 | 跳过brief直接读全文 | 效率低下，浪费token | 严格按Phase顺序：brief筛选→head定位→section细读 |

### 🚫 筛选禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 4 | 纳入纯概念性论文作为基线 | 无实际benchmark数据，无法对比 | 仅纳入有实验数据的论文 |
| 5 | 将论文标题包含关键词但内容无关的论文纳入 | 标题党论文干扰表格准确性 | 用brief验证论文内容相关性 |
| 6 | 优先纳入低分论文而忽略高分 | 基线表格应展示最强基准 | 按实证强度排序，优先展示SOTA |

### 🚫 提取禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 7 | **编造或推断未明确报告的分数** | 虚构数据严重损害表格可信度 | 缺失分数直接标记为"未明确报告"，绝不编造 |
| 8 | 仅凭摘要就判断代码开源状态 | 摘要可能过时或不准确 | 必须检查GitHub链接确认开源状态 |
| 9 | 混合不同benchmark的数据不加标注 | Apples-to-oranges比较误导用户 | 在Notes列标注benchmark来源，区分不同评估设置 |

### 🚫 输出禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 10 | 将Primary和Secondary混在一张表不加区分 | 读者无法判断基线强度 | 分开两张表或用不同标记区分Primary/Secondary |
| 11 | 不记录数据来源(基于brief/head/section) | 无法追溯表格可信度 | 在Inclusion Notes中明确每行的验证深度 |

---

## 异常处理

### 失败模式编码

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 搜索结果为空 | 尝试放宽日期范围或使用变体关键词 | 告知用户"未找到相关论文"，提供相近主题建议 |
| arXiv ID无效或无法获取 | 跳过该论文，继续处理其他ID | 记录跳过的ID及原因，在表格中标注 |
| GitHub链接失效 | 标记为"代码链接失效"而非"不开源" | 在Notes列标注"[需人工确认]" |
| 实验数据分散在多个表格 | 合并到同一行，分号分隔；如数据量过大分多行 | 优先提取主要指标，次要指标放入Notes |
| 仅部分数据集可验证 | 仅列出可验证的数据集 | 在Notes中标注"[其他数据集未明确报告]" |

### 检查点

- **[SLIM] 搜索+筛选完成后**: 展示筛选结果摘要(总结果数/保留数/开源数)，用户确认后进入section读取
- **[ADAPTIVE] 搜索结果 > 100篇时**: 提示用户筛选关键词，用户确认后继续

## Minimal Example

```bash
deepxiv search "agentic memory" --date-from 2026-03-01 --limit 100 --format json
deepxiv paper 2603.21489 --brief
deepxiv paper 2603.21489 --head
deepxiv paper 2603.21489 --section Experiments
```

Then write a markdown table with:
- title
- paper URL
- open-source status
- code URL
- datasets / benchmarks
- metrics / scores
- short notes on what was actually verified
