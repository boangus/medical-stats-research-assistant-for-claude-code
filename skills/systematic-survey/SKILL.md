---
name: "MSRA Systematic Survey"
version: "1.0.0"
description: |
  医学系统综述文献检索，聚焦 PubMed/Embase/Cochrane 检索策略制定、PRISMA 流程执行、GRADE 证据评级、领域检索报告生成。
  触发: systematic survey / 系统综述 / 文献检索 / 检索策略 / PRISMA / meta-analysis / GRADE / PICO / 偏倚风险 / RoB / 荟萃分析 / 网络meta / 证据评级 / 文献全景 / literature search / search strategy / domain survey
data_access_level: raw
task_type: open-ended
depends_on: []
works_with: [report, pipeline, peer-review]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.5"
tags: [medical-statistics, systematic-review, meta-analysis, PRISMA, GRADE, PubMed, literature-search]
---

# MSRA Systematic Survey — 医学系统综述文献检索

医学文献检索专用 skill，专注于系统综述与 meta 分析中的检索策略制定、文献筛选、证据综合与报告生成。以 PICO 研究问题定义、PRISMA 2020 完整流程，提供端到端的系统综述检索支持。

---

## 触发条件

### 触发关键词
**English**: systematic review, systematic survey, literature search, search strategy, PRISMA, meta-analysis, GRADE, PICO, PICOS, risk of bias, RoB, ROBINS-I, network meta-analysis, evidence synthesis, evidence rating, domain survey, PubMed search, Embase search, Cochrane search, database search, grey literature, hand-searching, citation tracking

**中文**: 系统综述, 文献检索, 检索策略, 荟萃分析, meta分析, PICO框架, 偏倚风险, GRADE评级, 证据分级, 文献全景, 领域检索, 引文追踪, 灰色文献, 手工检索, 数据库检索, Cochrane图书馆, PubMed检索, Embase检索

### 不触发场景
| 场景 | 使用替代 |
|------|----------|
| 写论文/撰写手稿 | `report`（论文写作模式） |
| 审稿/同行评审 | `peer-review` |
| 数据分析/统计执行 | `analysis-exec` |
| 完整研究→论文流水线 | `pipeline`（Stage 5 Paper Track） |

---

## 模式选择指南

| 你的情况 | 推荐模式 | 说明 |
|----------|----------|------|
| 需要完整 PRISMA 系统综述 + meta 分析 | `full` | 6 阶段完整流程，产出 PRISMA 报告 |
| 快速了解某领域的文献分布 | `quick-scan` | PICO 框架下的文献概览，30 分钟内完成 |
| 需要制定专业检索式 | `search-strategy` | PubMed/Embase/Cochrane 多库检索策略构建 |
| 需要特定疾病/药物的文献全景 | `domain-report` | 领域检索报告 + 文献计量分析 |
| 多干预比较的网络 meta 分析 | `nma` | 网络 meta 分析检索策略 + 证据网络 |
| 需要对已有证据进行 GRADE 评级 | `grade-assessment` | 对每个主要结局进行证据质量评估 |
| 需要评估纳入研究的偏倚风险 | `quality-assessment` | RoB 2 / ROBINS-I / 系统评价偏倚工具 |
| 研究问题不清晰，需要探索 | `socratic` | 苏格拉底式引导，帮助厘清系统综述范围 |

```
用户输入
    |
    +-- 已有明确 PICO 问题？
    |   +-- 是 --> 需要完整 PRISMA 流程？
    |   |          +-- 是 --> full（完整系统综述）
    |   |          +-- 否 --> 需要检索策略？
    |   |                     +-- 是 --> search-strategy（检索策略制定）
    |   |                     +-- 否 --> 需要文献全景？
    |   |                                +-- 是 --> domain-report（领域检索报告）
    |   |                                +-- 否 --> quick-scan（快速文献扫描）
    |   +-- 否 --> 需要引导厘清问题？
    |              +-- 是 --> socratic（苏格拉底引导）
    |              +-- 否 --> quick-scan（先概览再聚焦）
    |
    +-- 已有纳入文献，需要质量评估？ --> quality-assessment
    +-- 已有综合结果，需要 GRADE 评级？ --> grade-assessment
    +-- 需要多干预比较？ --> nma（网络 meta 分析）
```

---

## 铁律 (IRON RULES)

以下 4 条铁律为不可违反的硬性约束，任何模式下均须遵守：

| # | 铁律 | 理由 |
|---|------|------|
| **IR-1** | 检索策略必须基于 PICO/PICOS 框架 | PICO 是系统综述的基石；缺乏 PICO 的检索没有可重复性，无法保证召回率 |
| **IR-2** | 必须报告完整的检索路径（数据库、检索词、筛选结果） | PRISMA-S 声明要求检索过程完全透明；隐藏检索路径属于学术不端 |
| **IR-3** | PRISMA 流程必须完整记录（识别→筛选→合格→纳入） | PRISMA 2020 标准要求完整报告每个阶段的文献数量及排除原因 |
| **IR-4** | GRADE 证据评级必须对每个主要结局进行 | GRADE 是系统综述证据质量评估的国际标准；缺失评级将削弱综述的临床指导价值 |

> **补充约束**:
> - 每篇纳入研究的排除原因必须单独记录，不得合并为"不符合纳入标准"
> - 检索日期必须精确到年月日，并在报告中注明
> - 两个独立评审员的筛选一致性必须报告（Kappa 值或百分比一致性）

---

## 代理团队 (Agent Team)

| # | 代理 | 角色 | 阶段 |
|---|------|------|------|
| 1 | `pico_agent` | 研究问题结构化：PICO/PICOS 框架构建、研究问题细化、纳入/排除标准制定 | Phase 1 |
| 2 | `search_strategist_agent` | 检索策略制定：多数据库检索式构建、MeSH/Emtree 词表映射、布尔逻辑优化 | Phase 2 |
| 3 | `literature_screener_agent` | 文献筛选：标题/摘要筛选、全文筛选、PRISMA 流程记录、排除原因分析 | Phase 3 |
| 4 | `data_extractor_agent` | 数据提取：从纳入研究中提取效应量、样本量、结局指标、研究特征 | Phase 4 |
| 5 | `risk_of_bias_agent` | 偏倚风险评估：RoB 2（RCT）、ROBINS-I（非随机）、红绿灯可视化 | Phase 4 |
| 6 | `evidence_synthesizer_agent` | 证据综合：异质性检验、合并效应量、亚组分析、敏感性分析、GRADE 评级 | Phase 5 |
| 7 | `report_compiler_agent` | 报告生成：PRISMA 2020 流程图、森林图数据、结构化报告、领域检索报告 | Phase 6 |
| 8 | `domain_surveyor_agent` | 领域文献计量：发文趋势分析、热点聚类、数据库覆盖度评估、检索敏感性分析 | Phase 6（可选） |

---

## 工作流程 (6 Phases)

```
用户: "做一篇关于 [主题] 的系统综述"
     |
=== Phase 1: 研究问题定义 ===
     |
     |-> [pico_agent] -> PICO 研究方案
     |   - P (Population): 目标人群/疾病/条件
     |   - I (Intervention): 干预措施/暴露因素
     |   - C (Comparator): 对照措施
     |   - O (Outcome): 主要结局/次要结局
     |   - S (Study design): 研究设计类型（可选）
     |   - 纳入标准 / 排除标准
     |   - 研究问题: 1 个主要问题 + 2-3 个子问题
     |
     +-> 🔴 CHECKPOINT 1 (CP1): PICO 完整性验证 [STOP]
         - P/I/C/O 四要素齐全？
         - 纳入/排除标准可操作？
         - 检索范围明确（数据库、语言、时间）？
         - 判定: PASS / BLOCK
     |
=== Phase 2: 检索策略制定 ===
     |
     |-> [search_strategist_agent] -> 多数据库检索策略
     |   - PubMed/Embase/Cochrane Library 检索式
     |   - MeSH 词表 + 自由词组合
     |   - 布尔逻辑: AND / OR / NOT
     |   - 字段限定: [tiab], [mh], [ti], [ab]
     |   - 检索过滤器: 人类、语言、年份
     |   - 检索策略记录表 (PRISMA-S 格式)
     |
     +-> [literature_screener_agent] -> 初步检索结果
         - 各数据库命中数
         - 去重后文献数
         - 预筛选标题/摘要数量
     |
=== Phase 3: 文献筛选 ===
     |
     |-> [literature_screener_agent] -> PRISMA 流程数据
     |   - 标题/摘要筛选（两轮独立筛选）
     |   - 全文筛选（获取全文 → 评估资格）
     |   - 排除原因分类（PRISMA 2020 要求）
     |   - 筛选一致性: Cohen's Kappa 或百分比一致性
     |
     +-> 🔴 CHECKPOINT 2 (CP2): 筛选完整性验证 [STOP]
         - PRISMA 流程各阶段数字可追溯？
         - 排除原因完整且分类合理？
         - 筛选一致性 Kappa ≥ 0.6？
         - 判定: PASS / BLOCK
     |
=== Phase 4: 数据提取 + 质量评估 ===
     |
     |-> [data_extractor_agent] -> 数据提取表
     |   - 研究特征（作者、年份、国家、设计）
     |   - 人群特征（样本量、年龄、性别、基线）
     |   - 干预细节（剂量、疗程、给药途径）
     |   - 结局数据（效应量、95%CI、P 值）
     |   - 不良事件/安全性数据
     |
     +-> [risk_of_bias_agent] -> 偏倚风险评估
         - RoB 2 工具（针对 RCT）
         - ROBINS-I 工具（针对非随机研究）
         - QUADAS-2（针对诊断准确性研究）
         - PROBAST（针对预测模型研究）
         - 红绿灯表格 + 汇总图
     |
=== Phase 5: 证据综合 + GRADE 评级 ===
     |
     |-> [evidence_synthesizer_agent] -> 综合结果
     |   - 异质性检验（I², Chi², Tau²）
     |   - 合并效应量（RR/OR/MD/SMD, 95%CI）
     |   - 森林图数据
     |   - 亚组分析（预设亚组）
     |   - 敏感性分析（逐一剔除、质量分层）
     |   - 发表偏倚检测（漏斗图、Egger 检验）
     |
     +-> [evidence_synthesizer_agent] -> GRADE 证据评级
         - 每个主要结局的 GRADE 评级
         - 升级因素: 大效应量、剂量效应、残余混杂
         - 降级因素: 偏倚风险、不一致性、间接性、不精确性、发表偏倚
         - 证据摘要表（Summary of Findings）
     |
=== Phase 6: 报告生成 ===
     |
     |-> [report_compiler_agent] -> PRISMA 2020 完整报告
     |   - PRISMA 2020 检查清单（27 项）
     |   - PRISMA 流程图（识别→筛选→合格→纳入）
     |   - 检索策略附录（完整检索式）
     |   - 纳入研究特征表
     |   - 偏倚风险评估结果
     |   - 证据综合结果
     |   - GRADE 证据摘要表
     |   - 讨论与结论
     |
     +-> [domain_surveyor_agent] -> 领域检索报告（可选）
         - 检索策略透明度报告（PRISMA-S）
         - 数据库覆盖度评估
         - 检索敏感性/特异性分析
         - 文献计量分析（发文趋势、热点聚类）
     |
     +-> 🔴 CHECKPOINT 3 (CP3): 报告完整性验证 [STOP]
         - PRISMA 2020 清单所有条目已覆盖？
         - GRADE 评级对每个主要结局已完成？
         - 检索策略完全透明可复现？
         - 判定: PASS / BLOCK
```

---

## 检查点总结表 (Checkpoint Summary Table)

| # | 关口 | 通过标准（全部满足） | 阻断标准（任一触发） | 阻断处理 |
|---|------|---------------------|---------------------|----------|
| **CP1** | Phase 1 后 | PICO 四要素齐全且可操作；纳入/排除标准具体（≥3 条纳入 + ≥2 条排除）；检索范围明确（≥3 个数据库 + 语言 + 时间段）；研究问题可在一个句子内回答 | PICO 缺要素；纳入标准不可操作（如"相关研究"）；未指定数据库或时间范围；研究问题模糊无法聚焦 | STOP → 退回 Phase 1 重新定义 PICO；最多 2 轮；仍失败 → 切换 quick-scan 先做文献摸底 |
| **CP2** | Phase 3 后 | PRISMA 流程各阶段数字完整（识别→筛选→合格→纳入）；排除原因分类明确（每类 ≥1 条具体原因）；筛选一致性 Kappa ≥ 0.6 或百分比一致性 ≥ 80%；全文获取率 ≥ 90% | PRISMA 流程数字不连续或缺失；排除原因笼统（如"不符合标准"）；Kappa < 0.6 且未解决分歧；全文获取率 < 80% | STOP → 补充筛选或调整排除标准；最多 2 轮；仍失败 → 标注筛选偏倚风险 |
| **CP3** | Phase 5 后 | GRADE 评级对每个主要结局已完成（≥1 个结局有完整评级）；证据摘要表（SoF）包含所有主要结局；检索策略完全透明（PRISMA-S 格式）；PRISMA 2020 清单 ≥25/27 项已覆盖 | 无 GRADE 评级或仅部分结局有评级；SoF 表缺失；检索策略不完整（缺少数据库或检索词）；PRISMA 清单缺失 > 3 项 | STOP → 补充评级或完善检索策略报告；最多 2 轮；仍失败 → 标注"证据评级不完整" |

**判定规则**:
- **PASS**: 全部通过标准满足且零阻断标准触发 → 进入下一阶段
- **BLOCK**: 任一阻断标准触发 → 停止流水线，展示具体问题，要求修正
- **REVISE**: 部分通过（满足部分标准，无阻断） → 允许针对性修正（每个检查点最多 2 轮）
- **FALLBACK**: 2 轮修正失败 → 优雅降级（标注局限性或切换模式）

---

## 检索策略制定详细

### PubMed 检索式构建模板

```markdown
# PubMed 检索式构建步骤

## 1. PICO 概念拆解
| PICO 要素 | 概念 1 | 概念 2 | 概念 3 |
|-----------|--------|--------|--------|
| P (Population) | 疾病/人群 | 亚组特征 | - |
| I (Intervention) | 干预措施 | 剂量/疗程 | - |
| C (Comparator) | 对照措施 | - | - |
| O (Outcome) | 主要结局 | 次要结局 | - |

## 2. 每个概念的检索策略
对每个概念，组合使用:
- MeSH 主题词: #1 "Disease Name"[Mesh]
- 自由词/同义词: #2 "disease name"[tiab] OR "disease synonym"[tiab]
- 缩写: #3 "DN"[tiab]
- 概念内用 OR 连接: #1 OR #2 OR #3

## 3. 概念间用 AND 连接
#5: #概念1 AND #概念2 AND #概念3

## 4. 添加过滤器（如适用）
#6: #5 AND "humans"[Mesh]
#7: #6 AND "english"[la] OR "chinese"[la]
#8: #7 AND "2015/01/01":3000[dp]
```

### Embase 检索式构建要点

| 要点 | 说明 |
|------|------|
| Emtree 词表 | 使用 Embase 专有的 Emtree 主题词，与 MeSH 有差异 |
| 字段限定 | `/de` (主题词), `/ti,ab` (标题摘要), `/kw` (关键词) |
| 自动词语匹配 | Embase 自动扩展主题词，需要用 `/exp` 控制 |
| PreMEDLINE | Embase 包含未被 PubMed 索引的文献 |

### Cochrane Library 检索式构建要点

| 要点 | 说明 |
|------|------|
| 检索范围 | CENTRAL (临床试验), CDSR (系统综述), DARE, HTA |
| MeSH 词表 | Cochrane 使用 MeSH v2024 |
| 自由词 | MeSH + 自由词组合提高召回率 |
| 字段限定 | [tiab], [mh], [ti], [ab], [key] |

### 多库检索策略对照表

| 检索要素 | PubMed | Embase | Cochrane | CNKI/万方 |
|----------|--------|--------|----------|-----------|
| 主题词 | MeSH | Emtree | MeSH | 中科院主题词 |
| 自由词 | [tiab] | /ti,ab | [tiab] | 全文 |
| 布尔逻辑 | AND OR NOT | AND OR NOT | AND OR NOT | 并且 或者 不含 |
| 人类限定 | humans[Mesh] | human'/de | - | - |
| 语言限定 | [la] | [la] | - | 中文 |
| 时间限定 | [dp] | [py] | - | 发表时间 |

---

## 领域检索报告 (Domain Search Report)

领域检索报告是对特定疾病、药物或方法领域的文献全景分析，适用于：
- 申报课题前的文献摸底
- 研究选题的可行性评估
- 学科发展态势分析
- 为系统综述提供预检索数据

### 报告结构

#### 1. 检索策略透明度报告 (PRISMA-S 声明)

PRISMA-S（Systematic Review Search Methods Extension）要求完整报告检索过程：

| PRISMA-S 条目 | 要求 | 示例 |
|---------------|------|------|
| 信息源 | 列出所有检索数据库及检索日期 | PubMed (2026-06-21), Embase (2026-06-21), CNKI (2026-06-21) |
| 检索策略 | 提供每个数据库的完整检索式 | 见附录 A |
| 检索限制 | 说明语言、时间、研究类型限制 | 人类研究、中英文、2015-2026 |
| 记录保存 | 说明检索结果的管理方式 | EndNote X9 去重 |
| 筛选过程 | 说明筛选方法和工具 | 两名评审员独立筛选，Cohen's Kappa 计算 |
| 数据库覆盖度 | 评估检索数据库的覆盖范围 | PubMed + Embase 覆盖约 90% 生物医学文献 |

#### 2. 数据库覆盖度评估

| 数据库 | 覆盖范围 | 优势 | 局限 | 推荐优先级 |
|--------|----------|------|------|-----------|
| PubMed/MEDLINE | 生物医学核心期刊 ~36,000 种 | MeSH 词表精确、免费、更新快 | 部分小语种期刊未收录 | 必检 |
| Embase | 生物医学 ~8,500 种，药学覆盖更强 | Emtree 词表、欧洲期刊覆盖好 | 付费、部分 MeSH 不兼容 | 必检 |
| Cochrane Library | CENTRAL (临床试验) + CDSR | 高质量 RCT 索引、系统综述数据库 | 覆盖面窄、更新略滞后 | 推荐 |
| Web of Science | 多学科 ~21,000 种 | 引文追踪、影响因子 | 付费、生物医学非专长 | 可选 |
| CNKI/万方/维普 | 中文期刊 | 中文文献全覆盖 | 质量参差、检索功能弱 | 中文必检 |
| PsycINFO | 心理学/行为科学 | 心理学专长 | 覆盖面窄 | 心理学推荐 |
| CINAHL | 护理/ allied health | 护理专长 | 付费 | 护理推荐 |

**覆盖度计算**:
```
总覆盖率 = 1 - (漏检文献数 / 领域总文献数)
经验基准: PubMed + Embase ≈ 90% 生物医学文献
           + Cochrane ≈ 95% 临床试验
           + 中文库 ≈ 中文文献 95%
```

#### 3. 检索敏感性/特异性分析
| 指标 | 定义 | 目标值 | 说明 |
|------|------|--------|------|
| 召回率 (Recall/Sensitivity) | 检出的相关文献 / 领域全部相关文献 | ≥ 95% | 系统综述的首要目标：不能遗漏重要文献 |
| 精确率 (Precision) | 检出的相关文献 / 检出的全部文献 | 依检索策略而定 | 过高精确率可能意味着召回不足 |
| NNS (Number Needed to Screen) | 筛选文献数 / 纳入文献数 | 依领域而定 | 衡量筛选工作量 |
| F1 分数 | 2 × (Precision × Recall) / (Precision + Recall) | 综合指标 | 召回率优先时 F1 可降低至 0.5 |

**敏感性分析方法**:
1. **参考标准验证**: 选取已知高质量系统综述，检查其纳入文献是否被当前检索策略检出
2. **引文追踪**: 对纳入研究进行引文追踪（向前 + 向后），检查是否有遗漏
3. **手检验证**: 对核心期刊进行手工检索，对比电子检索结果
4. **灰色文献检索**: 检索会议摘要、预印本、学位论文、临床试验注册平台

#### 4. 文献计量分析

| 分析维度 | 方法 | 输出 |
|----------|------|------|
| 发文趋势 | 按年统计发文量 | 折线图 + 增长率 |
| 国家/地区分布 | 按第一作者国家统计 | 地图可视化 |
| 期刊分布 | 按期刊统计发文量 | Top 20 期刊表 |
| 研究类型分布 | 按研究设计分类 | 饼图/柱状图 |
| 热点聚类 | 关键词共现分析 | 关键词云 + 聚类图 |
| 引文网络 | 高被引文献分析 | 引文网络图 |
| 作者合作网络 | 合著关系分析 | 合作网络图 |
| 临床试验注册 | ClinicalTrials.gov / ChiCTR | 进行中试验数量 |

**工具推荐**:
- Bibliometrix (R 包): 全功能文献计量分析
- VOSviewer: 可视化共现/聚类分析
- CiteSpace: 时空图谱 + 突变检测
- RISCVS: 参考文献管理 + 分析

---

## 异常与失败模式 (Failure Modes)

| # | 失败场景 | 触发条件 | 一线处理 | 仍失败兜底 |
|---|---------|---------|---------|-----------|
| F1 | PICO 问题过于宽泛（如"癌症的治疗"） | 用户无法在2轮引导内提供具体癌种、分期、干预类型或结局指标；PICO四要素中有≥2个缺失或不可操作 | 退回 Phase 1，引导用户缩小范围：限定癌种、分期、干预类型、结局指标 | 先做 quick-scan 摸底，根据摸底结果重新定义PICO |
| F2 | 检索结果过多（>10,000 篇）无法筛选 | 检索策略优化后（增加限定词、精确MeSH词、限定研究类型/语言/年份）仍>5,000篇 | 优化检索策略：增加限定词、使用更精确的 MeSH 词、限定研究类型/语言/年份 | 分层筛选：优先核心期刊、高影响因子期刊、近5年文献 |
| F3 | 检索结果过少（<10 篇） | 放宽检索条件（移除部分限制、增加同义词、扩展数据库、检索灰色文献）后仍<10篇 | 放宽检索条件：移除部分限制、增加同义词、扩展数据库、检索灰色文献 | 标注"文献基础薄弱"，退回 Phase 1 修改PICO或调整研究问题 |
| F4 | 全文获取率不足（<80%） | 尝试所有替代来源（机构库、作者联系、文献互助）后仍<80% | 尝试替代来源：机构库、作者联系、文献互助 | 标注"部分文献无法获取，可能存在选择偏倚"，在讨论中说明局限性 |
| F5 | 筛选一致性低（Kappa < 0.6） | 两名评审员讨论分歧、统一标准后重新筛选不一致部分，Kappa仍<0.6 | 两名评审员讨论分歧 → 统一标准 → 重新筛选不一致部分 | 引入第三名评审员仲裁，计算仲裁者间一致性 |
| F6 | 纳入研究异质性过高（I² > 75%） | 亚组分析和Meta回归无法解释异质性来源（P>0.1） | 探索异质性来源：亚组分析、Meta回归 | 仅做叙述性综合，不合并效应量；在讨论中说明异质性影响 |
| F7 | 发表偏倚明显（漏斗图不对称 + Egger P < 0.1） | 使用校正方法（Trim-and-fill、selection model）后偏倚仍显著（P<0.05） | 使用校正方法：Trim-and-fill、selection model | 在讨论中强调发表偏倚的影响，结论谨慎解读 |
| F8 | GRADE 评级全部为"低"或"极低" | 所有主要结局的证据质量均为"低"或"极低"，无法提供高质量证据指导临床实践 | 完整报告降级原因 → 在结论中强调证据不确定性 → 明确列出未来研究方向 | 明确标注"证据质量不足"，在讨论中列出具体研究空白，建议开展高质量RCT填补证据缺口 |
| F9 | 检索策略无法复现 | 重新构建检索式并验证后，仍无法复现原始检索结果 | 重新构建检索式并验证 → 确保每个步骤可追溯 → 提供完整检索日志 | 标注"检索策略可复现性存疑"，邀请方法学专家进行同行评审，提供检索策略审核报告 |
| F10 | 领域文献高度碎片化（无共识） | 文献分析显示研究结论相互矛盾，无法形成共识 | 报告分歧现状 → 识别争议焦点 → 触发 full 模式系统综述作为解决路径 | 开展系统综述解决争议，或组织多学科专家共识会议，形成临床实践指南 |

---

## 反模式 (Anti-Patterns)

| # | 反模式 | 为什么错 | 正确做法 |
|---|--------|---------|----------|
| 1 | **只检索 PubMed 不检索 Embase** | PubMed + Embase 覆盖约 90% 生物医学文献；单独 PubMed 遗漏约 10-15% | 至少检索 PubMed + Embase，Cochrane 为强烈推荐 |
| 2 | **不报告排除原因** | PRISMA 2020 要求每个排除原因单独分类；笼统的"不符合标准"不可接受 | 按排除原因分类（如：人群不符、干预不符、结局无数据、研究设计不符），每类报告篇数 |
| 3 | **混淆系统综述和叙述性综述** | 系统综述有严格的方法学要求（PRISMA、PICO、偏倚评估）；叙述性综述无系统方法 | 明确定位：有 PICO + 系统检索 + 偏倚评估 = 系统综述；否则为叙述性综述 |
| 4 | **检索日期不报告** | 文献检索有时间性；不报告日期导致无法评估检索时效性 | 在报告中注明每个数据库的精确检索日期（年/月/日） |
| 5 | **不使用 MeSH/Emtree 主题词** | 仅用自由词检索遗漏同义表达和上位概念的文献 | 每个概念同时使用主题词 + 自由词组合，确保高召回率 |
| 6 | **筛选过程不透明** | 未说明筛选人数、工具、一致性检查 | 报告筛选人数（≥2）、筛选工具（如 Rayyan）、一致性指标（Kappa） |
| 7 | **忽略灰色文献** | 仅检索正式期刊遗漏会议摘要、预印本、学位论文、临床试验注册 | 检索 ClinicalTrials.gov、WHO ICTRP、会议摘要库、学位论文库 |
| 8 | **合并所有研究做 meta 分析不考虑异质性** | 高异质性下强行合并会产生误导性结果 | 先检验异质性（I²），>75% 考虑叙述性综合或探索异质性来源 |
| 9 | **不做敏感性分析** | 单一分析结果无法验证稳健性 | 至少进行：逐一剔除分析、按质量分层分析、不同统计模型比较 |
| 10 | **PRISMA 流程图数字不一致** | 各阶段数字应满足：识别 ≥ 筛选 ≥ 合格 ≥ 纳入 | 使用 PRISMA 2020 模板，确保数字逻辑一致（A ≥ B ≥ C ≥ D） |

---

## 手动报告协议 (Handoff Protocol)

### systematic-survey → report（论文写作模式）

系统综述完成后，以下材料可交接给 `report`（论文写作模式）:

1. **PICO 研究方案** — 来自 `pico_agent`
2. **检索策略记录** — 来自 `search_strategist_agent`
3. **PRISMA 流程数据** — 来自 `literature_screener_agent`
4. **数据提取表** — 来自 `data_extractor_agent`
5. **偏倚风险评估** — 来自 `risk_of_bias_agent`
6. **GRADE 证据摘要表** — 来自 `evidence_synthesizer_agent`
7. **领域检索报告** — 来自 `domain_surveyor_agent`（可选）

**触发条件**: 用户说"基于这个系统综述写论文"或"帮我把这个综述写成文章"

`report` 的 `paper_config_agent` 会自动检测可用材料并跳过重复步骤：
- 有 PICO 方案 → 跳过选题
- 有检索策略 → 跳过文献检索
- 有 GRADE 评级 → 加速讨论部分撰写

---

## 共享资源引用 (Shared Resources)

### 报告规范

| 资源 | 路径 | 用途 |
|------|------|------|
| PRISMA 2020 Checklist | `shared/reporting-guidelines/PRISMA_2020_checklist.md` | 系统综述报告 27 项检查清单 |
| PRISMA-NMA Checklist | `shared/reporting-guidelines/PRISMA_NMA_checklist.md` | 网络 meta 分析报告清单 |
| CONSORT Checklist | `shared/reporting-guidelines/CONSORT_checklist.md` | RCT 报告清单（评估纳入研究质量时参考） |
| STROBE Checklist | `shared/reporting-guidelines/STROBE_checklist.md` | 观察性研究报告清单 |
| SPIRIT Checklist | `shared/reporting-guidelines/SPIRIT_checklist.md` | 临床试验方案报告清单 |

### 偏倚风险与证据评级

| 资源 | 路径 | 用途 |
|------|------|------|
| RoB 2 Checklist | `shared/risk-of-bias/RoB_2_checklist.md` | RCT 偏倚风险评估工具 |
| ROBINS-I Checklist | `shared/risk-of-bias/ROBINS_I_V2_checklist.md` | 非随机研究偏倚风险评估工具 |
| QUADAS-2 Checklist | `shared/risk-of-bias/QUADAS_2_checklist.md` | 诊断准确性研究质量评估 |
| PROBAST Checklist | `shared/risk-of-bias/PROBAST_checklist.md` | 预测模型研究偏倚风险评估 |
| GRADE Framework | `shared/risk-of-bias/GRADE_framework.md` | GRADE 证据质量评级框架 |

### 统计方法

| 资源 | 路径 | 用途 |
|------|------|------|
| 统计方法目录 | `shared/statistics-methods/INDEX.md` | 48 章统计方法索引 |
| Meta 分析章节 | `shared/statistics-methods/chapters/` | 合并效应量、异质性、发表偏倚等 |
| 统计检验决策树 | `shared/statistics-methods/stat_test_decision_tree.md` | 选择正确统计方法 |
| 统计约束规则 | `shared/statistics-methods/statistical_constraints.md` | 统计分析硬性约束 |

### PRISMA-trAIce 协议

| 资源 | 路径 | 用途 |
|------|------|------|
| PRISMA-trAIce Protocol | `shared/prisma_trAIce_protocol.md` | AI 辅助系统综述的 PRISMA 扩展 |
| RAISE Framework | `shared/raise_framework.md` | AI 辅助系统综述的 RAISE 框架 |

### 反模式参考
| 资源 | 路径 | 用途 |
|------|------|------|
| 医学统计反模式 | `shared/anti-patterns/medical_stats_anti_patterns.md` | 医学统计分析常见错误 |

---

## 输出规范

### 报告格式

所有输出报告遵循以下结构：

```
# 系统综述报告: [研究问题]

## 摘要
- 背景 / 目的 / 方法 / 结果 / 结论

## 1. 引言
- 1.1 背景与理论
- 1.2 研究目的

## 2. 方法
- 2.1 纳入/排除标准 (PICO)
- 2.2 检索策略
- 2.3 文献筛选
- 2.4 数据提取
- 2.5 偏倚风险评估
- 2.6 综合方法

## 3. 结果
- 3.1 检索结果 (PRISMA 流程图)
- 3.2 纳入研究特征
- 3.3 偏倚风险评估结果
- 3.4 证据综合结果
- 3.5 GRADE 证据摘要表

## 4. 讨论
- 4.1 主要发现
- 4.2 与现有文献比较
- 4.3 局限性
- 4.4 结论与启示

## 附录
- 附录 A: 完整检索策略
- 附录 B: 排除文献列表及原因
- 附录 C: 纳入研究详细数据
```

### 检索策略记录格式 (PRISMA-S)

```markdown
## 附录 A: 检索策略
### A.1 PubMed 检索式 (检索日期: YYYY-MM-DD)

#1 "Disease Name"[Mesh]
#2 "disease name"[tiab] OR "disease synonym"[tiab] OR "DN"[tiab]
#3 #1 OR #2
#4 "Intervention"[Mesh]
#5 "intervention"[tiab] OR "intervention synonym"[tiab]
#6 #4 OR #5
#7 "Comparator"[Mesh]
#8 "comparator"[tiab]
#9 #7 OR #8
#10 #3 AND #6 AND #9
#11 #10 AND "humans"[Mesh]
#12 #11 AND ("2015/01/01"[PDAT] : "3000/12/31"[PDAT])
#13 #12 AND (English[la] OR Chinese[la])

### A.2 Embase 检索式 (检索日期: YYYY-MM-DD)
[完整检索式]

### A.3 Cochrane Library 检索式 (检索日期: YYYY-MM-DD)
[完整检索式]
```

### 领域检索报告格式
```markdown
# 领域检索报告: [领域名称]

## 1. 检索概览
- 检索日期 / 数据库 / 检索式概要

## 2. 检索结果
- 各数据库命中数 / 去重后 / 筛选后

## 3. 数据库覆盖度评估
- 各数据库覆盖范围 / 优势 / 局限

## 4. 检索敏感性分析
- 召回率 / 精确率 / 参考标准验证

## 5. 文献计量分析
- 5.1 发文趋势
- 5.2 国家/地区分布
- 5.3 期刊分布
- 5.4 研究类型分布
- 5.5 关键词聚类
- 5.6 高被引文献

## 6. 研究空白识别
- 未覆盖的亚组 / 缺失的结局指标 / 方法学空白

## 7. 建议
- 未来研究方向 / 系统综述可行性
```

---

## 代理文件引用

| 代理 | 定义文件 |
|------|----------|
| pico_agent | `agents/pico_agent.md` |
| search_strategist_agent | `agents/search_strategist_agent.md` |
| literature_screener_agent | `agents/literature_screener_agent.md` |
| data_extractor_agent | `agents/data_extractor_agent.md` |
| risk_of_bias_agent | `agents/risk_of_bias_agent.md` |
| evidence_synthesizer_agent | `agents/evidence_synthesizer_agent.md` |
| report_compiler_agent | `agents/report_compiler_agent.md` |
| domain_surveyor_agent | `agents/domain_surveyor_agent.md` |

---

## 参考文献

| 参考文献 | 用途 | 使用者 |
|----------|------|--------|
| `references/prisma_2020_guide.md` | PRISMA 2020 检查清单解读 | report_compiler, literature_screener |
| `references/prisma_s_extension.md` | PRISMA-S 检索方法报告扩展 | search_strategist, domain_surveyor |
| `references/search_strategy_templates.md` | 各数据库检索模板 | search_strategist |
| `references/rob2_guide.md` | RoB 2 工具使用指南 | risk_of_bias |
| `references/robins_i_guide.md` | ROBINS-I 工具使用指南 | risk_of_bias |
| `references/grade_guide.md` | GRADE 评级操作指南 | evidence_synthesizer |
| `references/meta_analysis_guide.md` | Meta 分析方法选择与执行 | evidence_synthesizer |
| `references/heterogeneity_guide.md` | 异质性处理决策树 | evidence_synthesizer |
| `references/funnel_plot_guide.md` | 发表偏倚检测方法 | evidence_synthesizer |
| `references/bibliometrics_guide.md` | 文献计量分析方法 | domain_surveyor |
| `references/medical_failure_paths.md` | 失败场景恢复路径 | all agents |
| `references/prisma_flow_template.md` | PRISMA 2020 流程图模板 | report_compiler |
| `references/changelog.md` | 版本历史 | 全部 |

---

## 模板

| 模板 | 用途 |
|------|------|
| `templates/pico_framework_template.md` | PICO 框架结构化模板 |
| `templates/search_strategy_template.md` | 多数据库检索策略记录模板 |
| `templates/prisma_flow_template.md` | PRISMA 2020 流程图数据模板 |
| `templates/data_extraction_template.md` | 数据提取表模板 |
| `templates/rob_assessment_template.md` | 偏倚风险评估红绿灯模板 |
| `templates/grade_summary_template.md` | GRADE 证据摘要表模板 |
| `templates/domain_survey_report_template.md` | 领域检索报告模板 |

---

## 示例

| 示例 | 展示内容 |
|------|----------|
| `examples/full_systematic_review.md` | 完整 6 阶段系统综述流程示例 |
| `examples/search_strategy_construction.md` | PubMed/Embase 检索式构建示例 |
| `examples/prisma_screening.md` | 文献筛选 + PRISMA 流程记录示例 |
| `examples/grade_assessment.md` | GRADE 证据评级操作示例 |
| `examples/domain_survey_report.md` | 领域检索报告生成示例 |
| `examples/nma_search_strategy.md` | 网络 meta 分析检索策略示例 |

---

## 输出语言

跟随用户语言。学术术语保留英文（如 PICO、PRISMA、GRADE、MeSH、RoB）。检索策略中的数据库名称、字段限定符、MeSH 词保持英文原名。

---

## 质量标准

1. ⚠️ **IRON RULE**: 检索策略必须基于 PICO/PICOS 框架，不可凭经验随意构建
2. ⚠️ **IRON RULE**: 完整报告检索路径，确保可重复性
3. ⚠️ **IRON RULE**: PRISMA 流程必须完整记录，各阶段数字逻辑一致
4. ⚠️ **IRON RULE**: GRADE 评级覆盖每个主要结局
5. **双人筛选**: 至少两名独立评审员进行文献筛选，报告一致性指标
6. **排除原因分类**: 每篇排除文献的排除原因必须单独记录
7. **检索时间**: 注明每个数据库的精确检索日期
8. **敏感性验证**: 至少使用一种方法验证检索策略的敏感性（如引文追踪或参考标准验证）
9. **异质性处理**: 高异质性（I² > 75%）时优先探索原因，不盲目合并
10. **灰色文献**: 系统综述应至少检索一种灰色文献来源

---

## 与其他技能的集成

```
systematic-survey + report (论文模式)     -> 系统综述论文撰写
systematic-survey + pipeline (Stage 5)    -> 系统综述纳入 MSRA 统一流水线
systematic-survey + peer-review           -> 系统综述方法学评审
systematic-survey + analysis-exec         -> 系统综述中的统计分析执行
systematic-survey (quick) → systematic-survey -> 从快速浏览升级为系统综述
```

---

## 版本信息

| 项目 | 内容 |
|------|------|
| Skill Version | 0.9.3 |
| Last Updated | 2026-06-23 |
| Maintainer | MSRA Team |
| 依赖技能 | report v0.9.0+（下游论文写作） |
| 替代技能 | systematic-survey（通用文献检索功能由本 skill 承接） |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.9.3 | 2026-06-23 | 重构失败模式表为Darwin标准5列格式；更新失败处理策略为具体行动步骤 |
| 0.9.0 | 2026-06-21 | 初始版本：8 模式、8 代理、6 阶段工作流、领域检索报告 |

> 完整版本历史见 `references/changelog.md`。
