# Mode Selection Guide

This guide helps users and the `paper_config_agent` select the most appropriate operational mode.

---

## Mode Selection Flowchart

```
User Input 99├── Already have complete research?
9  ├── Yes 9Want a full paper?
9  9  ├── Yes ─────────────────────────9full mode
9  9  └── No 9Just need an outline?
9  9      ├── Yes ─────────────────────9outline-only mode
9  9      └── No 9Just need an abstract?
9  9          ├── Yes ──────────────────9abstract-only mode
9  9          └── No 9Just need a literature review?
9  9              ├── Yes ─────────────9lit-review mode
9  9              └── No ──────────────9full mode
9  99  └── No 9Want guided thinking?
9      ├── Yes ─────────────────────────9plan mode 9NEW
9      └── No ──────────────────────────9full mode (Phase 0 will conduct an interview)
9├── Have an existing paper to revise? ──────────────────────9revision mode
├── Have reviewer comments to handle?
9  ├── Comments only, no response written yet ──────────9revision-coach mode
9  └── Comments + an existing rebuttal/response draft ──9rebuttal-audit mode
├── Need an AI-usage disclosure statement? ─────────────────9disclosure mode
├── Just need format conversion? ────────────────────────9format-convert mode
└── Just need a citation check? ────────────────────────9citation-check mode
```

---

## Detailed Description of Each Mode

### full mode 9Complete Paper Writing

**Applicable Scenarios**:
- User has a clear research question and (partial) materials
- Needs to produce a complete paper from start to finish
- Includes all phases: Interview 9Literature 9Structure 9Argumentation 9Writing 9Citation 9Review 9Formatting

**Not Applicable When**:
- User has no idea about research direction (9use `systematic-survey` first)
- Only need a specific section (9use another specialized mode)

**Expected Output**: Complete paper draft + references + bilingual abstract + review report
**Expected Duration**: Long (all 8 Phases fully executed)
**Agents Used**: All 9 + socratic_mentor (if needed)

---

### outline-only mode 9Outline Generation

**Applicable Scenarios**:
- Only need the paper structure and outline
- A proposal to submit to an advisor for review
- Need to quickly plan the paper structure

**Not Applicable When**:
- Need complete paper content (9full mode)
- Need guided thinking (9plan mode)

**Expected Output**: Detailed outline + evidence allocation + word count distribution
**Expected Duration**: Short (Phase 0-2)
**Agents Used**: intake 9literature_strategist 9structure_architect

---

### plan mode 9Chapter-by-Chapter Guided Planning 9NEW

**Applicable Scenarios**:
- User has ideas but they are not yet clear enough
- Wants guided thinking for each chapter's content
- First-time academic paper writer
- Wants to think through every section before writing
- Just received materials from systematic-survey and needs to transform them into a paper plan

**Not Applicable When**:
- Already knows exactly what to write (9full mode is faster)
- Only needs an outline without deep thinking (9outline-only mode)
- Time-pressured and needs rapid output (9full mode)

**Expected Output**: Chapter Plan + INSIGHT Collection
**Expected Duration**: Medium (Step 0-3, approximately 20-30 rounds of conversation)
**Agents Used**: intake 9socratic_mentor 9structure_architect 9argument_builder

**Subsequent Connections**:
- Chapter Plan 9full mode (produce complete paper)
- Chapter Plan 9medical-paper-reviewer (review the plan)

---

### revision mode 9Paper Revision

**Applicable Scenarios**:
- Already have a completed paper draft
- Received reviewer comments requiring revision
- Feel certain sections need improvement

**Not Applicable When**:
- No existing paper draft (9full mode)
- Only need to check citation format (9citation-check mode)

**Expected Output**: Revised paper + revision notes (tracked changes)
**Expected Duration**: Medium
**Agents Used**: peer_reviewer 9draft_writer 9citation_compliance

**Prerequisite**: User must provide existing paper content

---

### abstract-only mode 9Abstract Writing

**Applicable Scenarios**:
- Paper is already complete, only need an abstract
- Need to submit a conference abstract
- Need a bilingual abstract

**Not Applicable When**:
- No paper content to summarize (9full mode or plan mode)

**Expected Output**: Bilingual abstract (zh-TW + EN) + keywords
**Expected Duration**: Short
**Agents Used**: intake 9abstract_bilingual

---

### lit-review mode 9Literature Review

**Applicable Scenarios**:
- Need a literature review on a specific topic
- Preparing the Literature Review chapter of a paper
- Need a systematic search strategy and literature matrix

**Not Applicable When**:
- Need a complete paper (9full mode)
- Need an in-depth research investigation (9systematic-survey)

**Expected Output**: Annotated bibliography + literature matrix + synthesis analysis
**Expected Duration**: Medium
**Agents Used**: intake 9literature_strategist

---

### format-convert mode 9Format Conversion

**Applicable Scenarios**:
- Already have paper content, need format conversion
- Markdown 9LaTeX / DOCX / PDF
- Need to comply with a specific journal's formatting requirements

**Not Applicable When**:
- No existing content (9full mode)
- Need content modifications (9revision mode)

**Expected Output**: Document in target format
**Expected Duration**: Short
**Agents Used**: formatter used standalone

---

### citation-check mode 9Citation Check

**Applicable Scenarios**:
- Already have a paper, only need to check citation format
- Final check before submission
- Switching citation format (e.g., APA 9IEEE)

**Not Applicable When**:
- No existing citation list (9full mode)
- Need to modify paper content (9revision mode)

**Expected Output**: Citation error report + automatic correction suggestions
**Expected Duration**: Short
**Agents Used**: citation_compliance used standalone

---

### revision-coach mode 9Reviewer-Comment Triage

**Applicable Scenarios**:
- Received reviewer comments / a decision letter and need them parsed into a structured plan
- Want a Revision Roadmap that classifies, maps, and prioritizes each comment
- Need a Response Letter Skeleton to start drafting replies
- Deciding whether to address or push back on a comment (disagreement posture)
- Non-journal scopes: conference rebuttal, grant-panel response, transfer-after-review

**Not Applicable When**:
- Already have a written rebuttal/response draft you want QA'd (9rebuttal-audit mode)
- The paper itself needs rewriting based on the comments (9revision mode)

**Expected Output**: Revision Roadmap + optional Tracking Template + Response Letter Skeleton
**Expected Duration**: Short-Medium
**Agents Used**: revision_planner used standalone (no prior pipeline execution required)

---

### disclosure mode 9AI-Usage Disclosure Statement

**Applicable Scenarios**:
- Paper is drafted and you need a venue-specific AI-usage disclosure paragraph
- Submitting to a venue with a defined AI-disclosure policy (ICLR, NeurIPS, Nature, Science, ACL, EMNLP)
- Need placement guidance for where the statement goes in the manuscript

**Not Applicable When**:
- No paper drafted yet 9disclosure is a finishing step (9full mode first)
- The venue is not in the policy database (confirm the venue's current policy manually)

**Expected Output**: Venue-specific AI-usage disclosure paragraph(s) + placement instructions
**Expected Duration**: Short
**Agents Used**: disclosure protocol used standalone (venue policy database lookup)

---

### rebuttal-audit mode 9Rebuttal-Draft QA

**Applicable Scenarios**:
- You already wrote a rebuttal/response-to-reviewers draft and want it checked before sending
- Need a per-comment coverage table (which reviewer concerns the draft addresses, partially addresses, or misses)
- Want risk flags for tone (too combative), unsupported claims, or a response that misreads the reviewer's point

**Not Applicable When**:
- You have reviewer comments but have **not** written a response yet (9revision-coach mode, which *generates* a skeleton)
- The manuscript itself needs revising (9revision mode)

**Input gate**: requires BOTH (a) the reviewer comments / decision letter AND (b) an existing rebuttal draft. Comments only 9route to revision-coach. If intent is ambiguous, clarify rather than guess.

**Expected Output**: Advisory QA report 9per-comment coverage + gap list + risk flags. Generates no new response.
**Expected Duration**: Short
**Agents Used**: revision_planner's comment-parsing capability, run standalone (advisory)

**Integrity boundary**: a standalone invocation runs **outside** the pipeline, so rebuttal-audit does **not** emit a Schema 11 ledger, does **not** write the Material Passport, and does **not** mark anything `ready_to_submit` or verified. The output is advisory QA only.

---

## Paths from systematic-survey

```
systematic-survey completed
  9  ├── systematic-survey (full mode) outputs:
  9  RQ Brief + Methodology Blueprint + Annotated Bibliography + Synthesis Report
  9  9  9  ├── Want to write the paper directly ──9medical-paper (full mode)
  9  9  paper_config_agent auto-detects materials, skips redundant questions
  9  9  9  └── Want to plan before writing ──9medical-paper (plan mode)
  9      socratic_mentor leverages existing materials to accelerate guidance
  9  └── systematic-survey (socratic mode) outputs:
      INSIGHT Collection + Synthesis Report
      9      ├── INSIGHTs are sufficiently clear ──9medical-paper (full mode)
      9      └── Need more guidance ──9medical-paper (plan mode)
          socratic_mentor continues deepening from INSIGHTs
```

## Connecting to medical-paper-reviewer

```
medical-paper completed
  9  ├── full mode produces complete paper ──9medical-paper-reviewer (full / guided)
  9  Complete peer review + revision suggestions
  9  ├── plan mode produces Chapter Plan ──9medical-paper-reviewer (guided)
  9  Review the plan's feasibility and completeness
  9  └── reviewer feedback ──9medical-paper (revision mode)
      Revise paper based on review comments
```

---

## Common Misselection Scenarios

| User Says | Easily Misselected | Correct Choice | Reason |
|---------|---------|---------|------|
| "Help me write an outline" / 「幫我寫大綱9| outline-only | First confirm: Do they want a simple outline or deep planning? | May need plan mode |
| "I want to write a paper but don't know how to start" / 「想寫論文但不知道怎麼開始9| full | plan mode | Needs guided thinking |
| "Help me revise my paper" / 「幫我修改論文9| revision | First confirm: Are there reviewer comments? | May need full mode rewrite |
| "Help me search for literature" / 「幫我找文獻9| lit-review | First confirm: Is it a literature review for a paper or a research investigation? | May need systematic-survey |
| "I have systematic-survey results, help me write a paper" / 「我有研究結果，幫我寫成論文9| full (skip Phase 0 directly) | full (but intake needs to detect handoff) | Materials need to be properly imported |
| "I want to plan my paper step by step" / 「我想逐步規劃論文9| outline-only | plan mode | Needs interactive guidance |
| "The paper format is wrong" / 「論文格式不對9| revision | citation-check or format-convert | May only need format correction |
| 「帶我寫論文9「引導我寫論文9| full | plan mode | 使用者需要互動式引導，不是直接產9|
| 「第一次寫論文9「論文新手9| full | plan mode | 新手需要蘇格拉底式逐章引導 |

---

## Quick Decision Table

| What Do You Have? | What Do You Want? | Choose This Mode |
|-----------|-----------|------------|
| Nothing | Complete paper | plan mode 9full mode |
| Research question + literature | Complete paper | full mode |
| Research question + literature | Outline | outline-only mode |
| Vague idea | Paper plan | plan mode |
| systematic-survey results | Complete paper | full mode (auto-handoff) |
| systematic-survey results | Guided planning | plan mode |
| Completed paper | Revision | revision mode |
| Completed paper | Abstract | abstract-only mode |
| Completed paper | Format conversion | format-convert mode |
| Completed paper | Citation check | citation-check mode |
| Reviewer comments (no response yet) | Parse + roadmap + reply skeleton | revision-coach mode |
| Reviewer comments + a written rebuttal draft | QA the draft before sending | rebuttal-audit mode |
| Drafted paper + target venue | AI-usage disclosure statement | disclosure mode |

---

### Plan to Full Mode Conversion Protocol

When a user completes `plan` mode and wants to proceed to `full` mode for actual paper writing:

#### Conversion Checklist

| Plan Mode Output | Full Mode Input | Conversion Action |
|-----------------|-----------------|-------------------|
| Chapter Plan (structure outline) | `structure_architect` agent | Map chapters 9formal sections with heading levels; validate against `medical_paper_structure_patterns.md` |
| Socratic Responses (Q&A transcripts) | `argument_builder` agent | Extract claims + evidence + warrants from dialogue; discard conversational scaffolding |
| Literature Notes (if any) | `literature_strategist` agent | Independent execution 9plan mode notes serve as seed keywords only; full systematic search required |
| Argument Sketches | `argument_builder` agent | Evaluate each sketch against 4-level scoring; only `adequate` or above proceed |

#### Quality Gate

Before conversion, ALL of the following must be true:
- [ ] Every chapter in the Chapter Plan has at least 1 argument sketch rated `adequate` or above
- [ ] The overall paper structure maps to a recognized pattern in `medical_paper_structure_patterns.md`
- [ ] At least 5 potential references have been identified (seeds for `literature_strategist`)
- [ ] The research question is finalized (not still evolving from Socratic dialogue)

#### What Gets Discarded
- Conversational filler from Socratic dialogue (greetings, confirmations, repetitions)
- Tentative ideas explicitly marked as "maybe" or "not sure" by the user
- Plan mode's iterative drafts (only the final version of each chapter plan carries over)

---

## Trigger-to-Mode Mapping Examples

```
"Write a paper on SDGs in HEI"           -> full
"Give me a paper outline for..."         -> outline-only
"Revise this paper based on feedback"    -> revision
"Write an abstract for this paper"       -> abstract-only
"Do a literature review on..."           -> lit-review
"Convert this paper to LaTeX"            -> format-convert
"Convert citations to IEEE"              -> format-convert
"Check the citations in this paper"      -> citation-check
"guide my paper"                         -> plan
"help me plan my paper"                  -> plan
"I got reviewer comments"               -> revision-coach
"parse these reviews"                    -> revision-coach
"help me with my revision"              -> revision-coach
"should we push back on reviewer 2"     -> revision-coach
"conference rebuttal" / "grant response" -> revision-coach
"audit my rebuttal draft"               -> rebuttal-audit (needs comments + an existing draft)
"did I miss any reviewer comment"       -> rebuttal-audit
"AI disclosure for Nature"              -> disclosure
"generate an AI usage statement"        -> disclosure
```
