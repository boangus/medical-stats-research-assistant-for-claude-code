# 医学期刊字数规范

**版本:** v1.0 (MSRA Unified Pipeline)
**适用范围:** Stage 4 统计报告和 Stage 5 论文撰写的字数控制

---

## 1. Purpose

在医学论文撰写中，不同期刊对摘要、正文和参考文献有严格的字数限制。摘要的字数限制通常在 250-400 词（英文）或 400-500 字（中文）之间。在硬性字数限制下，字数算法的选择、审慎表达的保留、以及编辑修改的空间都会影响最终是否超限。本规范定义统一的字数计算方法和主要医学期刊的具体要求。

---

## 2. 标准字数计算方法

### 2.1 空白分割法 (Whitespace-split)

**算法:** `len(text.split())` — 按空白字符分割文本并计算非空 token 数。

**选择理由:**
1. **可复现。** 任何人对同一 UTF-8 文本运行 `split()` 得到相同结果。
2. **与 Microsoft Word 一致。** 大多数作者在 Word 中检查字数，其算法与空白分割等效。
3. **对连字符保守。** "state-of-the-art" 计为 1 个 token（连字符不拆分），系统性报告较低总数——在追赶硬性上限时是更安全的方向。
4. **语言中性。** 对英文和欧洲语言适用。

### 2.2 空白分割法的计数规则

| 文本 | 空白分割计数 |
|------|------------|
| `state-of-the-art` | 1 |
| `2020-2024` | 1 |
| `Smith, John-Paul` | 2 |
| `e.g.,` | 1 |
| `123,456` | 1 |
| `(n=42)` | 1 |
| `https://example.org/path` | 1 |

### 2.3 不适用空白分割的语言

中文、日文、韩文、泰文等不使用空格分词的语言，应使用**字符计数**（character count），而非字数。大多数服务这些语言的期刊规定字符上限。

---

## 3. 主要医学期刊字数规范

### 3.1 英文期刊

#### JAMA (Journal of the American Medical Association)

| 部分 | 限制 | 说明 |
|------|------|------|
| 结构化摘要 | **250 词** | 必须包含 Background, Methods, Results, Conclusions |
| 正文 | **3,000 词** | 不含摘要、参考文献、表格和图注 |
| 参考文献 | **≤40 篇** | AMA 格式 |
| 表格/图表 | **≤5 个** | 合并相关表格 |
| 临床试验注册号 | 必须 | 摘要末尾 |
| 报告规范 | CONSORT (RCT), STROBE (观察性), PRISMA (系统综述) | 必须遵循 |

**JAMA 结构化摘要格式:**
```markdown
## Abstract

**Importance:** [1-2 句，说明研究重要性]

**Objective:** [明确研究目的]

**Design, Setting, and Participants:** [研究设计、地点、参与者]

**Exposures:** [主要暴露/干预]

**Main Outcomes and Measures:** [主要结局指标和统计方法]

**Results:** [主要发现，包括数字]

**Conclusions and Relevance:** [结论和临床意义]
```

#### The Lancet

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **250 词** | 结构化: Background, Methods, Findings, Interpretation |
| 正文 | **3,000 词** | 不含摘要、参考文献 |
| 参考文献 | **≤50 篇** | Vancouver 格式 |
| 表格/图表 | **≤5 个** | |
| 研究方案 | 鼓励 | 独立发表 |

#### New England Journal of Medicine (NEJM)

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **250 词** | 结构化: Background, Methods, Results, Conclusions |
| 正文 | **2,500 词** | 严格限制 |
| 参考文献 | **≤50 篇** | |
| 表格/图表 | **≤4 个** | |
| 临床试验注册号 | 必须 | |
| 数据共享声明 | 必须 | |

#### BMJ (British Medical Journal)

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **250 词** | 结构化: Objective, Design, Setting, Participants, Interventions, Main outcome measures, Results, Conclusions |
| 正文 | **3,000 词** | |
| 参考文献 | **≤30 篇** | |
| 表格/图表 | **≤3 个** | |
| 报告规范 | CONSORT, STROBE, PRISMA 等 | 必须 |

#### Annals of Internal Medicine

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **250 词** | 结构化 |
| 正文 | **3,000 词** | |
| 参考文献 | **≤40 篇** | |
| 表格/图表 | **≤4 个** | |

#### PLOS Medicine

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **300 词** | 结构化: Background, Methods and Findings, Conclusions |
| 正文 | **无严格限制** | 但建议 4,000-5,000 词 |
| 参考文献 | **无严格限制** | |

#### JAMA Network Open

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **350 词** | 结构化 |
| 正文 | **4,000 词** | |
| 参考文献 | **≤50 篇** | |

#### Circulation

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **250 词** | 结构化 |
| 正文 | **4,000 词** | |
| 参考文献 | **≤50 篇** | |

### 3.2 中文期刊

#### 中华医学会系列杂志

| 部分 | 限制 | 说明 |
|------|------|------|
| 结构化摘要 | **400 字** | 目的、方法、结果、结论 |
| 正文 | **5,000 字** | |
| 参考文献 | **20-30 篇** | 依具体杂志 |
| 英文摘要 | **800-1,000 词** | 通常在中文摘要之后 |

**常见中华医学会系列杂志:**
- 中华医学杂志
- 中华内科杂志
- 中华外科杂志
- 中华心血管病杂志
- 中华肿瘤杂志
- 中华流行病学杂志

#### 中国循证医学杂志

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **500 字** | 结构化 |
| 正文 | **6,000 字** | |
| 参考文献 | **≤30 篇** | |

#### 中华预防医学杂志

| 部分 | 限制 | 说明 |
|------|------|------|
| 摘要 | **400 字** | 结构化 |
| 正文 | **5,000 字** | |

---

## 4. 字数缓冲规则

### 4.1 3-5% 缓冲

MSRA 流水线在期刊硬性上限下保留 **3-5% 缓冲**：

| 期刊上限 | 3% 缓冲目标 | 5% 缓冲目标 |
|---------|-----------|-----------|
| 250 词 | 242 词 | 237 词 |
| 300 词 | 291 词 | 285 词 |
| 350 词 | 339 词 | 332 词 |
| 400 词 | 388 词 | 380 词 |
| 400 字 | 388 字 | 380 字 |
| 5,000 字 | 4,850 字 | 4,750 字 |

### 4.2 缓冲选择

- **3% 缓冲:** 受保护审慎表达较多 (>=10% 字数预算) 时使用。紧凑缓冲为实质性内容保留空间。
- **5% 缓冲:** 期刊算法不明确或受保护审慎表达较少时使用。宽松缓冲吸收更多不确定性。

### 4.3 缓冲用途

缓冲空间用于:
1. 编辑/审稿人要求的修改（通常增加 2-3 词）
2. 字数算法差异
3. 期刊可能计入的标题/Running title

---

## 5. 字数预算分配

### 5.1 结构化摘要字数预算

以 JAMA 250 词摘要为例的推荐分配:

| 模块 | 推荐词数 | 比例 |
|------|---------|------|
| Importance/Background | 25-30 词 | 10-12% |
| Objective/Purpose | 20-25 词 | 8-10% |
| Design/Setting/Participants | 40-50 词 | 16-20% |
| Interventions/Exposures | 20-30 词 | 8-12% |
| Main Outcome Measures | 20-25 词 | 8-10% |
| Results | 70-80 词 | 28-32% |
| Conclusions/Relevance | 30-40 词 | 12-16% |

### 5.2 中文字数预算

以中华医学会 400 字摘要为例的推荐分配:

| 模块 | 推荐字数 | 比例 |
|------|---------|------|
| 目的 | 30-40 字 | 8-10% |
| 方法 | 80-100 字 | 20-25% |
| 结果 | 150-180 字 | 38-45% |
| 结论 | 40-60 字 | 10-15% |

---

## 6. 常见字数问题

### 6.1 超限处理

| 情况 | 处理方法 |
|------|---------|
| 摘要超限 5-10 词 | 删除过渡词和冗余修饰语 |
| 摘要超限 10-20 词 | 合并句子、简化方法描述 |
| 摘要超限 >20 词 | 重新组织结构，将次要信息移至正文 |
| 正文超限 | 检查方法部分是否过长、讨论是否重复 |

### 6.2 字数算法差异

不同工具可能产生不同字数:
- Microsoft Word: 空白分割等效
- Google Docs: 空白分割等效
- LaTeX `\wordcount`: 可能不同
- 在线字数工具: 可能包含/排除标题、脚注

**建议:** 使用 MSRA 标准空白分割法计算，与 Word 结果对比验证。

### 6.3 中文字符计算

- 中文摘要: 1 个汉字 = 1 个字符
- 英文摘要: 1 个单词 = 1 个词（空白分割）
- 混合摘要: 中文部分按字符计数，英文部分按词计数，分别报告

---

## 7. 参考文献格式速查

| 期刊 | 格式 | 说明 |
|------|------|------|
| JAMA | AMA (Vancouver 变体) | 数字编号，JAMA Network 有具体指南 |
| Lancet | Vancouver | 数字编号 |
| NEJM | Vancouver | 数字编号 |
| BMJ | Vancouver | 数字编号 |
| 中华医学会 | GB/T 7714 | 中文国标格式 |
| PLOS | Vancouver 变体 | 数字编号 |

---

## 8. 报告规范 (Reporting Guidelines)

| 规范 | 适用研究类型 | 摘要要求 |
|------|------------|---------|
| CONSORT | RCT | 结构化摘要 |
| STROBE | 观察性研究 | 结构化摘要 |
| PRISMA | 系统综述/Meta 分析 | 结构化摘要 |
| STARD | 诊断准确性研究 | 结构化摘要 |
| TRIPOD | 预测模型 | 结构化摘要 |
| ARRIVE | 动物实验 | 结构化摘要 |
| CARE | 个案报告 | 结构化摘要 |
| CHEERS | 经济学评价 | 结构化摘要 |

---

## 9. 参考文献

- International Committee of Medical Journal Editors (ICMJE). Recommendations for Conduct, Reporting, Editing, and Publication of Scholarly Work in Medical Journals. Updated 2023.
- JAMA Instructions for Authors. https://jamanetwork.com/journals/jama/instructions-for-authors
- The Lancet Instructions for Authors. https://www.thelancet.com/journal-information/for-authors
- NEJM Information for Authors. https://www.nejm.org/author-center
- BMJ Author Guidelines. https://www.bmj.com/about-bmj/resources-authors
- 中华医学会系列杂志编辑委员会. 中华医学会系列杂志稿约. 2023.
- von Elm E, et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) Statement. Lancet. 2007;370:1453-1457.
- Schulz KF, et al. CONSORT 2010 Statement. Ann Intern Med. 2010;152:726-732.
