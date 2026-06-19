---
study_id: MSRA-{YYYY}-{NNN}
version: v1.0
created_date: YYYY-MM-DD
status: draft
template_type: response_to_reviewers
---

# Response to Reviewers 模板

> MSRA 项目专用。Stage 5.7 论文修订阶段的逐条回应审稿人意见模板。
> 对齐 `shared/handoff_schemas.md` Schema 8 (Response to Reviewers) 与 Schema 11 (R&R Traceability Matrix)。
>
> **使用时机**：收到审稿意见后，逐条回应并记录修订动作，供复审（re-review）使用。

---

## 1. Paper Information（论文信息 / Paper Information）

| 字段 | 值 | 说明 |
|------|-----|------|
| 标题（Title） | [{论文标题}] | 修订后标题 |
| Manuscript ID | [{MANUSCRIPT-ID}] | 期刊分配的稿件编号 |
| 修订轮次（Revision Round） | [{1 / 2 / 3}] | 当前修订轮次 |
| 日期（Date） | [{YYYY-MM-DD}] | 本回应提交日期 |
| 前次决定（Previous Decision） | [{Major Revision / Minor Revision / Reject}] | 期刊前次决定 |
| 目标期刊（Target Journal） | [{期刊名称}] | 投稿期刊 |
| 原文字数（Original Word Count） | [{N}] | 修订前正文字数（不含参考文献） |
| 修订后字数（Revised Word Count） | [{N}] | 修订后正文字数 |
| 字数变化（Word Count Delta） | [{+/-N}] | 净字数变化（正=增加，负=删除） |
| 新增参考文献数（New References） | [{N}] | 本次修订新增的参考文献数量 |

---

## 2. Cover Letter to Editor（致主编信 / Cover Letter）

> 致主编的 Cover Letter，概述主要修改。

### 2.1 致谢（Acknowledgment）

Dear Dr. [{主编姓名}],

Thank you for the opportunity to revise our manuscript (Manuscript ID: [{MANUSCRIPT-ID}]). We appreciate the thoughtful comments from you and the reviewers, which have substantially improved our work.

### 2.2 主要修改摘要（Summary of Major Changes）

We have addressed all reviewer concerns. The most significant changes are:

1. [{主要修改 1：如 "新增样本量功效分析"}]
2. [{主要修改 2：如 "补充敏感性分析"}]
3. [{主要修改 3：如 "扩展 Discussion 局限性讨论"}]
4. [{主要修改 4：如 "更新参考文献，新增 3 篇"}]
5. [{主要修改 5：如 "修订图表以符合期刊格式"}]

### 2.3 修改稿高亮说明（Highlight of Changes）

- 修订稿中所有新增内容以 [{蓝色/下划线}] 标注
- 删除内容以 [{红色/删除线}] 标注
- 详细逐条回应见第 4 节

---

## 3. Executive Summary of Major Changes（主要修改摘要 / Executive Summary）

> 3-5 项最重要的修改，按重要性排序。

| 序号 | 修改类别 | 修改描述 | 涉及章节 | 审稿人 |
|------|---------|---------|---------|--------|
| 1 | [{Methodology / Analysis / Writing / Structure}] | [{最重要的修改描述}] | [{Section X.X}] | [{R1, R2}] |
| 2 | [{Methodology / Analysis}] | [{第二重要修改}] | [{Section X.X}] | [{R3}] |
| 3 | [{Writing / Citation}] | [{第三重要修改}] | [{Section X.X}] | [{R1}] |
| 4 | [{Structure}] | [{第四重要修改}] | [{Section X.X}] | [{EIC}] |
| 5 | [{Analysis}] | [{第五重要修改}] | [{Section X.X}] | [{R2}] |

---

## 4. Point-by-Point Responses（逐条回应 / Point-by-Point Responses）

> 每位审稿人独立章节。每条 Comment 包含完整回应链。

### 4.1 Reviewer 1 (R1)

#### Comment R1.1

| 字段 | 值 |
|------|-----|
| Type | [{Major / Minor / Editorial}] |
| Priority | [{must_fix / should_fix / consider}] |
| Roadmap Item ID | [{REV-001}] |

**Original Comment**:
> [{审稿人原始意见逐字引用}]

**Author Response**:

- **Thank**: Thank you for this insightful comment. We agree that [{简要重述审稿人关注点}].
- **Agree**: We fully agree that [{承认问题存在}].
- **Show**: We have [{具体采取的行动}].

**Action Taken**: [{具体修订动作描述}]

**Change Location**:
- Section: [{章节名称}]
- Page: [{页码}]
- Line: [{行号}]

**Status**: [{RESOLVED / DELIBERATE_LIMITATION / UNRESOLVABLE / REVIEWER_DISAGREE}]

**Decline Justification**（仅当 Status 非 RESOLVED 时填写）: [{拒绝理由，必须引用证据}]

---

#### Comment R1.2

| 字段 | 值 |
|------|-----|
| Type | [{Major / Minor / Editorial}] |
| Priority | [{must_fix / should_fix / consider}] |
| Roadmap Item ID | [{REV-002}] |

**Original Comment**:
> [{审稿人原始意见逐字引用}]

**Author Response**:

- **Thank**: [{感谢语}]
- **Agree**: [{承认语}]
- **Show**: [{展示修订}]

**Action Taken**: [{具体修订动作描述}]

**Change Location**:
- Section: [{章节名称}]
- Page: [{页码}]
- Line: [{行号}]

**Status**: [{RESOLVED / DELIBERATE_LIMITATION / UNRESOLVABLE / REVIEWER_DISAGREE}]

---

### 4.2 Reviewer 2 (R2)

#### Comment R2.1

| 字段 | 值 |
|------|-----|
| Type | [{Major / Minor / Editorial}] |
| Priority | [{must_fix / should_fix / consider}] |
| Roadmap Item ID | [{REV-003}] |

**Original Comment**:
> [{审稿人原始意见逐字引用}]

**Author Response**:

- **Thank**: [{感谢语}]
- **Agree**: [{承认语}]
- **Show**: [{展示修订}]

**Action Taken**: [{具体修订动作描述}]

**Change Location**:
- Section: [{章节名称}]
- Page: [{页码}]
- Line: [{行号}]

**Status**: [{RESOLVED / DELIBERATE_LIMITATION / UNRESOLVABLE / REVIEWER_DISAGREE}]

---

### 4.3 Reviewer 3 (R3)

#### Comment R3.1

| 字段 | 值 |
|------|-----|
| Type | [{Major / Minor / Editorial}] |
| Priority | [{must_fix / should_fix / consider}] |
| Roadmap Item ID | [{REV-004}] |

**Original Comment**:
> [{审稿人原始意见逐字引用}]

**Author Response**:

- **Thank**: [{感谢语}]
- **Agree**: [{承认语}]
- **Show**: [{展示修订}]

**Action Taken**: [{具体修订动作描述}]

**Change Location**:
- Section: [{章节名称}]
- Page: [{页码}]
- Line: [{行号}]

**Status**: [{RESOLVED / DELIBERATE_LIMITATION / UNRESOLVABLE / REVIEWER_DISAGREE}]

---

### 4.4 Devil's Advocate (DA)

#### Comment DA.1

| 字段 | 值 |
|------|-----|
| Type | [{Major / Minor / Editorial}] |
| Priority | [{must_fix / should_fix / consider}] |
| Roadmap Item ID | [{REV-005}] |

**Original Comment**:
> [{审稿人原始意见逐字引用}]

**Author Response**:

- **Thank**: [{感谢语}]
- **Agree**: [{承认语}]
- **Show**: [{展示修订}]

**Action Taken**: [{具体修订动作描述}]

**Change Location**:
- Section: [{章节名称}]
- Page: [{页码}]
- Line: [{行号}]

**Status**: [{RESOLVED / DELIBERATE_LIMITATION / UNRESOLVABLE / REVIEWER_DISAGREE}]

---

### 4.5 Commitment Ledger（承诺台账 / Commitment Ledger）

> YAML 格式，对齐 Schema 11 v3.11 (nested-object shape, #268)。
> 每个 concern 的承诺作为单个嵌套 YAML 块，以 `concern_id` 为键。
> `fulfillment_status` / `unfulfilled_rationale` 嵌套在对象内部。
>
> **占位符规范**：YAML 块内使用 `<...>`（尖括号），不要使用 `[...]`（方括号在 YAML 中会被解析为 flow sequence）。

```yaml
# concern 1 (多承诺示例)
- concern_id: <R1-1>
  roadmap_item_id: <REV-001>
  commitment_extracted:
    - commitment_text: "<承诺文本1：逐字或最小规范化>"
      commitment_type: <add_experiment | add_analysis | add_clarification | add_citation | restructure | other>
      required_evidence_type: <new_section | new_figure | new_table | new_citation | methods_paragraph | discussion_paragraph | prose_edit | acknowledgment_only | other>
      fulfillment_status: <fulfilled | partial | not-fulfilled | explicitly-rejected-with-rationale>
      # unfulfilled_rationale: "..."  # 仅当 status 为非 fulfilled 时必需；fulfilled 时省略
      revision_location: "<Section X.X, Page Y, Line Z>"
    - commitment_text: "<承诺文本2>"
      commitment_type: <add_clarification>
      required_evidence_type: <discussion_paragraph>
      fulfillment_status: <fulfilled>
      revision_location: "<Section X.X>"

# concern 2 (单承诺示例)
- concern_id: <R1-2>
  roadmap_item_id: <REV-002>
  commitment_extracted:
    - commitment_text: "<承诺文本>"
      commitment_type: <add_clarification>
      required_evidence_type: <discussion_paragraph>
      fulfillment_status: <partial>
      unfulfilled_rationale: "<部分履行的理由：done elsewhere, see §X / rejected, reasons: … / deferred to future work>"
      revision_location: "<Section X.X>"

# concern 3 (DA 意见，明确拒绝)
- concern_id: <DA-1>
  roadmap_item_id: <REV-005>
  commitment_extracted:
    - commitment_text: "<承诺文本>"
      commitment_type: <add_analysis>
      required_evidence_type: <new_table>
      fulfillment_status: <explicitly-rejected-with-rationale>
      unfulfilled_rationale: "<拒绝理由，必须引用证据>"
      revision_location: ""

# concern 4 (正面意见，无承诺)
- concern_id: <R2-3>
  roadmap_item_id: <REV-008>
  commitment_extracted: []
```

**字段说明**：
- `commitment_type` 枚举：`add_experiment` / `add_analysis` / `add_clarification` / `add_citation` / `restructure` / `other`
- `required_evidence_type` 枚举：`new_section` / `new_figure` / `new_table` / `new_citation` / `methods_paragraph` / `discussion_paragraph` / `prose_edit` / `acknowledgment_only` / `other`
- `fulfillment_status` 枚举：`fulfilled` / `partial` / `not-fulfilled` / `explicitly-rejected-with-rationale`
- `unfulfilled_rationale`：当 `fulfillment_status` 为 `fulfilled` 时省略此字段；否则必须非空
- `commitment_extracted: []`：正面意见无承诺时使用空列表标记

---

## 5. R&R Traceability Matrix（R&R 追溯矩阵 / R&R Traceability Matrix）

> 对齐 Schema 11。映射每条审稿意见到完整修订周期。

| concern_id | priority | original_comment | authors_claim | revision_location | verified | status | quality_assessment |
|------------|----------|------------------|---------------|-------------------|----------|--------|-------------------|
| R1.1 | MUST_FIX | [{审稿人原始意见}] | [{作者声明所做}] | [{Section X.X, Page Y}] | YES ✅ | FULLY_ADDRESSED | [{自由文本评估}] |
| R1.2 | SHOULD_FIX | [{审稿人原始意见}] | [{作者声明所做}] | [{Section X.X}] | PARTIAL ⚠️ | PARTIALLY_ADDRESSED | [{评估}] |
| R2.1 | MUST_FIX | [{审稿人原始意见}] | [{作者声明所做}] | [{Section X.X}] | YES ✅ | FULLY_ADDRESSED | [{评估}] |
| R3.1 | CONSIDER | [{审稿人原始意见}] | [{作者声明所做}] | [{Section X.X}] | NO ❌ | NOT_ADDRESSED | [{评估}] |
| DA.1 | MUST_FIX | [{审稿人原始意见}] | [{作者声明所做}] | [{N/A}] | CANNOT_VERIFY 🔍 | MADE_WORSE | [{评估}] |

**字段枚举**：
- `priority`: `MUST_FIX` / `SHOULD_FIX` / `CONSIDER`
- `verified`: `YES` (✅) / `PARTIAL` (⚠️) / `NO` (❌) / `CANNOT_VERIFY` (🔍)
- `status`: `FULLY_ADDRESSED` / `PARTIALLY_ADDRESSED` / `NOT_ADDRESSED` / `MADE_WORSE`

**可选字段**（未在表格中展示，记录于 Commitment Ledger）：
- `reviewer_source`: `EIC` / `R1` / `R2` / `R3` / `DA`
- `residual_action`: 当未完全解决时，剩余需做的事项

---

## 6. Summary Statistics（汇总统计 / Summary Statistics）

> 本轮修订的汇总统计，对齐 Schema 8 的 `summary` 字段。

| 指标 | 值 | 说明 |
|------|-----|------|
| 总意见数（Total Comments） | [{N}] | 所有审稿人意见总数 |
| 已解决（Resolved） | [{N}] | Status = RESOLVED |
| 故意限制（Deliberate Limitation） | [{N}] | Status = DELIBERATE_LIMITATION |
| 不可解决（Unresolvable） | [{N}] | Status = UNRESOLVABLE |
| 审稿人分歧（Reviewer Disagree） | [{N}] | Status = REVIEWER_DISAGREE |
| 字数变化（Word Count Delta） | [{+/-N}] | 净字数变化 |
| 新增参考文献（New References） | [{N}] | 新增参考文献数 |
| 新增图表（New Tables/Figures） | [{N}] | 新增表格/图表数 |

### 6.1 按审稿人分布（By Reviewer）

| 审稿人 | 总意见 | 已解决 | 故意限制 | 不可解决 | 分歧 |
|--------|--------|--------|---------|---------|------|
| R1 | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| R2 | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| R3 | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| DA | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| EIC | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |

### 6.2 按优先级分布（By Priority）

| 优先级 | 总数 | 已解决 | 未解决 |
|--------|------|--------|--------|
| MUST_FIX | [{N}] | [{N}] | [{N}] |
| SHOULD_FIX | [{N}] | [{N}] | [{N}] |
| CONSIDER | [{N}] | [{N}] | [{N}] |

---

## 7. Revision Completeness Checklist（修订完整性检查清单 / Revision Completeness Checklist）

> 12 项修订完整性检查，提交前逐项确认。

| 序号 | 检查项 | 状态 | 备注 |
|------|--------|------|------|
| 1 | 所有 MUST_FIX 意见均已回应 | [{✅ / ❌}] | [{备注}] |
| 2 | 所有 SHOULD_FIX 意见均已回应 | [{✅ / ❌}] | [{备注}] |
| 3 | 每条回应包含 Thank-Agree-Show 三步 | [{✅ / ❌}] | [{备注}] |
| 4 | 每条回应标注 Change Location（Section/Page/Line） | [{✅ / ❌}] | [{备注}] |
| 5 | 非 RESOLVED 状态均提供 Decline Justification | [{✅ / ❌}] | [{备注}] |
| 6 | Commitment Ledger 已填写且字段完整 | [{✅ / ❌}] | [{备注}] |
| 7 | R&R Traceability Matrix 覆盖所有 Roadmap Items | [{✅ / ❌}] | [{备注}] |
| 8 | 字数变化（Word Count Delta）已计算 | [{✅ / ❌}] | [{备注}] |
| 9 | 新增参考文献已纳入 Bibliography | [{✅ / ❌}] | [{备注}] |
| 10 | 新增图表已标注并在正文中引用 | [{✅ / ❌}] | [{备注}] |
| 11 | 修订稿中新增内容已高亮标注 | [{✅ / ❌}] | [{备注}] |
| 12 | Cover Letter 已撰写且包含主要修改摘要 | [{✅ / ❌}] | [{备注}] |

---

## 8. 冲突意见处理指南（Conflict Resolution Guide）

> 当审稿人之间意见矛盾时，按本指南处理。

### 8.1 冲突识别（Conflict Identification）

| 冲突 ID | 审稿人 A | 审稿人 B | 冲突描述 | A 的立场 | B 的立场 |
|---------|---------|---------|---------|---------|---------|
| CONFLICT-001 | [{R1}] | [{R3}] | [{冲突描述}] | [{A 的立场}] | [{B 的立场}] |

### 8.2 处理策略（Resolution Strategies）

按以下优先级处理冲突意见：

#### 策略 1：证据优先（Evidence-Based）

当审稿人意见基于不同证据时，采纳证据更强的一方。

- 评估双方引用的文献质量（证据等级 1-7）
- 在回应中说明采纳依据
- 对未采纳方礼貌说明理由

#### 策略 2：主编裁决（Editorial Decision）

当冲突无法通过证据解决时，遵循主编（EIC）意见。

- 在回应中明确说明"遵循主编建议"
- 同时回应双方意见，避免遗漏

#### 策略 3：折中方案（Compromise）

当双方意见均有合理之处时，提出折中方案。

- 在回应中说明折中逻辑
- 标注折中方案的具体位置
- 必要时在 Discussion 中讨论双方观点

#### 策略 4：明确拒绝一方（Explicit Decline）

当一方意见明显不合理时，礼貌拒绝。

- 使用 `REVIEWER_DISAGREE` 状态
- 在 Decline Justification 中引用证据
- 保持尊重语气，避免对抗

### 8.3 冲突回应模板（Conflict Response Template）

```
We note that Reviewer [{A}] and Reviewer [{B}] raised conflicting concerns regarding [{冲突主题}].

Reviewer [{A}] suggested [{A 的建议}], while Reviewer [{B}] recommended [{B 的建议}].

After careful consideration, we have [{采纳的策略}] because [{理由}].

Specifically, we have [{具体行动}]. This change is located in [{Section X.X, Page Y, Line Z}].

We hope this approach addresses both reviewers' concerns. We are happy to revise further if either reviewer feels our response is inadequate.
```

### 8.4 冲突记录（Conflict Log）

| 冲突 ID | 采用策略 | 最终处理 | 涉及审稿人 | 状态 |
|---------|---------|---------|-----------|------|
| CONFLICT-001 | [{Evidence-Based / Editorial Decision / Compromise / Explicit Decline}] | [{最终处理描述}] | [{R1, R3}] | [{RESOLVED / UNRESOLVABLE}] |

---

## 模板使用说明

### 适用场景

本模板用于 Stage 5.7 论文修订阶段，逐条回应审稿人意见。适用于：
- 收到审稿意见后的第一轮修订（Round 1）
- 复审后的第二轮修订（Round 2）
- 任何需要逐条回应审稿意见的场景

### 填写流程

1. **填写 Paper Information**（第 1 节）：从期刊投稿系统获取
2. **撰写 Cover Letter**（第 2 节）：概述主要修改
3. **整理 Executive Summary**（第 3 节）：提炼 3-5 项最重要修改
4. **逐条回应**（第 4 节）：每位审稿人独立子章节，每条 Comment 完整填写
5. **填写 Commitment Ledger**（第 4.5 节）：YAML 格式记录所有承诺
6. **构建 Traceability Matrix**（第 5 节）：确保覆盖所有 Roadmap Items
7. **计算 Summary Statistics**（第 6 节）：汇总修订统计
8. **核对 Checklist**（第 7 节）：12 项完整性检查
9. **处理冲突意见**（第 8 节）：如有审稿人矛盾，按指南处理

### Schema 对齐

- **Schema 8 (Response to Reviewers)**：第 1 节 Paper Information、第 4 节 Point-by-Point Responses、第 6 节 Summary Statistics 与 Schema 8 的 `revision_round` / `items` / `summary` / `word_count_delta` / `new_references_added` 字段对齐
- **Schema 11 (R&R Traceability Matrix)**：第 5 节 R&R Traceability Matrix 与 Schema 11 的 `concern_id` / `priority` / `original_comment` / `authors_claim` / `revision_location` / `verified` / `status` / `quality_assessment` 字段对齐；第 4.5 节 Commitment Ledger 与 Schema 11 的 `commitment_extracted` / `fulfillment_status` / `unfulfilled_rationale` 字段对齐

### 状态枚举说明

**Status（回应状态）**：
- `RESOLVED`：已完全解决
- `DELIBERATE_LIMITATION`：故意作为研究局限保留，需提供理由
- `UNRESOLVABLE`：客观上无法解决（如数据限制），需提供理由
- `REVIEWER_DISAGREE`：礼貌拒绝审稿人意见，需引用证据

**Priority（优先级）**：
- `must_fix`：必须修改，否则影响论文接受
- `should_fix`：建议修改，提升论文质量
- `consider`：可考虑修改，非必须

### 版本管理

- 每轮修订递增 `version`（如 v1.0 → v2.0）
- `status` 流转：`draft` → `submitted` → `verified`（复审通过后）
- 保留所有轮次的回应文档，便于追溯修订历史
