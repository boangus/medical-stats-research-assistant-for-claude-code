---
name: deepxiv-trending-digest
description: Summarize recent hot academic papers using deepxiv trending, brief, head, and section reads, then produce a markdown digest highlighting what each paper is about and which papers deserve deeper reading.
---

# DeepXiv Trending Digest

Use this skill when the user wants a recent hot-paper roundup, trending paper summary, weekly paper digest, or a markdown report based on DeepXiv trending papers.

## Goal

Turn recent DeepXiv trending papers into a concise markdown digest:

1. Find currently hot papers with `deepxiv trending`
2. Brief each candidate with `deepxiv paper <id> --brief`
3. Select the most promising papers for deeper inspection
4. Inspect structure with `deepxiv paper <id> --head`
5. Read only the most relevant sections with `deepxiv paper <id> --section ...`
6. Write a clean `.md` summary with recommendations

## Default Workflow

### 1. Pull trending papers

Start with a small, recent set unless the user asks otherwise.

```bash
deepxiv trending --days 7 --limit 10 --json
```

Default heuristics:
- Use `--days 7` for "recent hot papers"
- Use `--limit 10` for a manageable first pass
- If the user asks for a broader roundup, use `--days 14` or `--days 30`

### 2. Brief every candidate

For each selected arXiv ID, fetch a brief first:

```bash
deepxiv paper <arxiv_id> --brief
```

Capture:
- title
- arXiv ID
- publish date
- keywords
- TLDR
- citations if present
- GitHub URL if present

Do not jump to full text yet. `--brief` is the default screening step.

### 3. Rank for deeper reading

After reading briefs, choose the top 1-3 papers for deeper inspection.

Use signals like:
- strong novelty or surprising result
- practical relevance
- likely user interest
- unusually clear contribution
- useful code release
- especially strong social or research momentum

If a paper sounds incremental, unclear, or out of scope, keep it in the digest but skip deep reading.

### 4. Inspect paper structure

For the chosen papers:

```bash
deepxiv paper <arxiv_id> --head
```

Use `--head` to decide whether to drill down and which section matters most.

Look for sections such as:
- Introduction
- Method / Approach / Framework
- Experiments / Results / Evaluation
- Discussion / Limitations

Prefer section reads over full paper reads.

### 5. Read only high-value sections

Read at most 1-2 sections per paper unless the user explicitly asks for a deep dive.

Examples:

```bash
deepxiv paper <arxiv_id> --section Introduction
deepxiv paper <arxiv_id> --section Method
deepxiv paper <arxiv_id> --section Results
```

Selection guidance:
- Read `Introduction` if the contribution is still fuzzy
- Read `Method` if the core idea matters
- Read `Results` if the claim sounds strong and needs verification
- Read `Limitations` or `Discussion` if tradeoffs matter

Avoid reading everything.

## Markdown Output

Write a markdown file in the current workspace unless the user gave a different path.

Recommended filename:

```text
trending-paper-digest-YYYY-MM-DD.md
```

Recommended structure:

```md
# Trending Paper Digest

Date: YYYY-MM-DD
Window: Last 7 days
Source: deepxiv trending

## Executive Summary

- 2-4 bullets with the main themes across the trending list
- Mention the 1-3 most promising papers

## Papers Reviewed

### 1. Paper Title (`arXiv:xxxx.xxxxx`)

What it is about:
Short paragraph based mainly on `--brief`.

Why it matters:
- Bullet
- Bullet

Worth deeper reading?
Yes/Maybe/No, with one sentence.

If deeper review was done:

Sections checked:
- Introduction
- Method

Deeper notes:
Short paragraph with the key insight, evidence, or caveat.

### 2. ...

## Recommended Deep Dives

### Paper Title

- Why it stands out
- Which section to read next
- What question it could answer

## Cross-Cutting Trends

- Repeated themes
- Common methods
- Shared limitations or hype signals
```

## Writing Rules

- Keep the digest skimmable
- Prefer short paragraphs and flat bullets
- Separate "what it says" from "whether it is worth deeper reading"
- Be explicit when a conclusion is based only on `--brief`
- Be explicit when a conclusion is based on `--head` or a section read
- Do not pretend to have verified claims you have not checked

## Decision Rules

- If briefs are enough for the user's request, stop there
- Use `--head` only for the most promising papers
- Use `--section` only after `--head` suggests a high-value section
- Do not read full paper markdown unless the user explicitly asks for a full analysis

---

## 反例与黑名单

> **以下行为必须避免**。违反任何一条将导致digest质量下降或误导用户。

### 🚫 搜索与筛选禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 使用 `--days 1` (当天) 作为默认设置 | 数据量太少，偶然性高 | 使用 `--days 7` 作为默认值 |
| 2 | 对所有论文做深度阅读 | token消耗大，效率低 | 最多选择1-3篇做深度阅读，其余保持brief |
| 3 | 只看标题就判断论文重要程度 | 标题党论文干扰判断 | 必须用 `--brief` 验证内容质量 |
| 4 | 把增量性论文当作重大突破推荐 | 误导用户关注不重要的工作 | 区分"增量进步"和"重大突破"，在"Worth deeper reading?"中诚实标注 |

### 🚫 写作禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 5 | 把基于brief的推断当作已验证结论 | brief只是初步了解，不够深入 | 在"Deeper notes"中明确标注"Based on brief" |
| 6 | 推荐自己没读过的论文 | 无法保证推荐质量 | 仅推荐经过 `--brief` 或更深层阅读验证的论文 |
| 7 | 不区分不同阅读深度混在一处 | 读者无法判断信息来源可靠性 | 在"Sections checked"中明确列出验证深度 |

### 🚫 输出禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 8 | 生成超过10篇论文的digest | 信息过载，难以消化 | 控制在5-7篇核心论文，剩余简要列表 |
| 9 | 不标注数据来源(brief/head/section) | 无法追溯digest可信度 | 每篇论文必须标注验证深度 |
| 10 | 跳过"Cross-Cutting Trends"总结 | 失去了提炼洞见的机会 | 至少列出2-3个跨论文主题 |

---

## 异常处理

### 失败模式编码

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| trending结果为空或极少(<3篇) | 扩大日期范围 `--days 14` 或 `--days 30` | 告知用户近期无热门论文，建议搜索特定主题 |
| 所有论文brief都显示"incremental/incremental progress" | 诚实标注"Worth deeper reading? No"，不强行推荐 | 在Executive Summary中说明"本期热门论文整体偏增量" |
| 某篇论文 `--brief` 失败 | 跳过该论文，用其他论文补充 | 记录跳过的论文ID及原因 |
| 用户要求过多篇(如>20篇) | 告知token限制，建议分批处理 | 每次最多处理10篇，完成后询问是否继续 |
| 网络请求超时 | 重试一次，使用 `--section` 替代完整 `--brief` | 标注"[获取失败，待补充]" |

### 检查点

- **[SLIM] trending获取后**: 展示论文列表，询问用户"这些论文是否覆盖您感兴趣的主题？"
- **[ADAPTIVE] brief完成后**: 展示阅读摘要，用户确认后再决定深度阅读哪些论文
- **[MANDATORY] 输出前**: 检查digest是否包含Executive Summary、推荐理由、数据来源标注

## Minimal Example

```bash
deepxiv trending --days 7 --limit 5 --json
deepxiv paper 2603.20639 --brief
deepxiv paper 2603.26221 --brief
deepxiv paper 2603.20639 --head
deepxiv paper 2603.20639 --section Introduction
```

Then write the digest as markdown and clearly label:
- all reviewed papers
- which papers were only briefed
- which papers received deeper inspection
