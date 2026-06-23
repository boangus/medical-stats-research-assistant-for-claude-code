---
study_id: MSRA-{YYYY}-{NNN}
version: v1.0
created_date: YYYY-MM-DD
status: draft
template_type: msra_handoff_bundle
---

# MSRA Handoff Bundle 模板

> MSRA 项目专用。Stage 4（统计报告）9Stage 5（论文写作）的数据传递契约9> 9`scripts/generate_msra_handoff_bundle.py` 自动填充，亦可手工填写9> 对齐 `shared/handoff_schemas.md` Schema 9 (Material Passport) 9Schema 11 (R&R Traceability Matrix)9>
> **生成条件**：`passport.track == "full_paper"` 9Stage 1-4 全部 completed9
---

## 1. Source（元数据 / Source Metadata9
> 本节记录 Bundle 的来源信息，用于跨阶段追溯9
| 字段 | 9| 说明 |
|------|-----|------|
| passport_id | [{passport_id}] | MSRA Material Passport 唯一标识 |
| study_type | [{study_type}] | 研究类型（RCT / 观察性研究/ 诊断试验 / 系统综述等） |
| msra_version | [{msra_version}] | MSRA Pipeline 版本9|
| track | full_paper | 轨道标识（固定为 full_paper9|
| generated_at | [{generated_at}] | Bundle 生成时间（ISO 86019|
| schema_version | 1.0 | 本模9Schema 版本 |

---

## 2. Research Question（研究问9/ Research Question9
> 主研究问题与子问题。来源于 SAP.md，用于论9Introduction9
### 2.1 主研究问题（Primary RQ9
[{主研究问题：单一疑问句形式}]

### 2.2 子问题（Sub-Questions9
1. [{子问91}]
2. [{子问92}]
3. [{子问93}]

### 2.3 研究假设（Hypothesis，可选）

- H₀: [{零假设}]
- H9 [{备择假设}]

---

## 3. Results Bundle（结果包 / Results Bundle9
> 统计报告产出的表格、图表及结果解读路径，用于论9Results 章节9
### 3.1 结果解读路径（Results Interpretation Path9
- 主报告文9 [{final_report_path}]
- 解读顺序: [{建议阅读顺序，如 "Table 1 9Table 2 9Figure 1 9Table 3"}]

### 3.2 Tables 清单（Tables Inventory9
| 编号 | 文件路径 | 内容描述 | 类型标签 |
|------|---------|---------|---------|
| Table 1 | [{tables/table1.docx}] | [{基线特征表}] | baseline |
| Table 2 | [{tables/table2.docx}] | [{主要终点分析}] | primary_outcome |
| Table 3 | [{tables/table3.docx}] | [{次要终点分析}] | secondary_outcome |
| Table 4 | [{tables/table4.docx}] | [{敏感性分析}] | sensitivity |

**类型标签枚举**：`baseline` / `primary_outcome` / `secondary_outcome` / `safety` / `sensitivity` / `subgroup` / `demographic`

### 3.3 Figures 清单（Figures Inventory9
| 编号 | 文件路径 | 内容描述 | 类型标签 |
|------|---------|---------|---------|
| Figure 1 | [{figures/fig1.png}] | [{CONSORT 流程图}] | flowchart |
| Figure 2 | [{figures/fig2.png}] | [{Kaplan-Meier 曲线}] | survival_curve |
| Figure 3 | [{figures/fig3.png}] | [{森林图}] | forest_plot |

**类型标签枚举**：`flowchart` / `survival_curve` / `forest_plot` / `boxplot` / `scatter` / `bar` / `roc` / `calibration` / `heatmap`

---

## 4. Methods Summary（方法学摘要 / Methods Summary9
> 统计方法来自 SAP，方法学描述来自报告 Phase 5。用于论9Methods 章节9
### 4.1 统计方法（来9SAP9
[{统计方法描述：从 SAP.md "统计方法" 章节提取}]

### 4.2 方法学描述（来自报告 Phase 59
[{方法学描述：9final_report "方法学描9 章节提取}]

### 4.3 分析人群定义（Analysis Populations9
| 人群 | 定义 | 排除标准 |
|------|------|---------|
| ITT | [{所有随机化受试者}] | [{无}] |
| PP | [{完成方案的受试者}] | [{严重违反方案}] |
| Safety | [{至少接受一剂药物的受试者}] | [{未接受干预}] |

---

## 5. Key Findings（核心发9/ Key Findings9
> 显著性结果与效应量列表，用于论文 Introduction 9Discussion9
### 5.1 显著性结果（Significant Results9
- [{显著性结91：含 p 值与方向}]
- [{显著性结92：含 p 值与方向}]
- [{显著性结93：含 p 值与方向}]

### 5.2 效应量列表（Effect Sizes9
| 指标 | 效应9| 95% CI | p 9| 解读 |
|------|--------|--------|------|------|
| [{主要终点}] | [{HR=0.65}] | [{0.48-0.88}] | [{0.005}] | [{干预组风险降935%}] |
| [{次要终点}] | [{OR=1.82}] | [{1.20-2.76}] | [{0.005}] | [{干预组获益显著}] |

---

## 6. Safety Findings（安全性发9/ Safety Findings9
> 安全性分析结果，用于论文 Discussion9
### 6.1 不良事件汇总（Adverse Events Summary9
| 事件 | 干预9n (%) | 对照9n (%) | p 9|
|------|-------------|-------------|------|
| [{不良事件 1}] | [{n (X%)}] | [{n (X%)}] | [{p}] |
| [{严重不良事件}] | [{n (X%)}] | [{n (X%)}] | [{p}] |

### 6.2 安全性结论（Safety Conclusion9
[{安全性结论描述}]

---

## 7. Limitations（局限9/ Limitations9
> 研究局限性讨论，用于论文 Discussion9
1. [{局限91：样本量 / 选择偏9/ 失访等}]
2. [{局限92：测量局9/ 混杂因素等}]
3. [{局限93：外推9/ 单中心等}]
4. [{局限94：统计方法局限}]

---

## 8. Methods (Paper-Ready Format)（论文方法学格式 / Methods Paper-Ready9
> 论文 Methods 段落可直接引用的结构化文本9
### 8.1 主分析方法（Primary Analysis Method9
[{主分析方法描述：可直接粘贴到论文 Methods}]

### 8.2 样本量计算（Sample Size Calculation9
[{样本量计算描述：含检验效能、显著性水平、效应量假设}]

### 8.3 敏感性分析（Sensitivity Analysis9
[{敏感性分析描述：含方法与目的}]

### 8.4 多重性控制（Multiplicity Control9
[{多重性控制策略：Bonferroni / Holm / Gatekeeping 等}]

---

## 9. RQ Consistency Check（研究问题一致性校9/ RQ Consistency Check9
> SAP 9final_report 中研究问题的一致性校验，确保论文 Introduction 与分析计划对齐9
### 9.1 一致性状态（Consistency Status9
- 状9 [{9一9/ ⚠️ 基本一9/ 9不一9/ ⚠️ 无法自动判定}]

### 9.2 SAP 中的研究问题

[{SAP 中提取的研究问题}]

### 9.3 final_report 中的研究问题

[{final_report 中提取的研究问题}]

### 9.4 差异说明（Difference Note9
[{差异说明：若不一致，描述实质性差异并建议人工核查}]

---

## 10. Results to Claims Mapping（结果到 Claim 映射 / Results to Claims Mapping9
> 可追溯性表格，建立统计结果与论9Claim 的双向追溯链9
共识9[{N}] 个可追溯的统计结9Claim9
| Claim ID | 关键统计分析| 结果描述（来源行9| 论文对应章节建议 |
|----------|-----------|-------------------|------------------|
| CLAIM-001 | [{HR=0.65}] | [{主要终点 Cox 回归结果}] | Results / Abstract |
| CLAIM-002 | [{p=0.005}] | [{组间差异显著性}] | Results |
| CLAIM-003 | [{95% CI 0.48-0.88}] | [{效应量置信区间}] | Results / Abstract |

**使用说明**9- 每个 CLAIM-NNN 对应 final_report 中的一条统计结9- 论文写作时，9Results 段落引用对应 Claim ID 以建立双向追溯链
- 论文定稿后，可通过 Claim ID 反查 final_report 中的原始统计输出

---

## 11. Quality Gate Report（质量门闸报9/ Quality Gate Report9
> Stage 1.5 / 2.5 / 3.5 门闸通过情况9
| 门闸 | 状9| 通过/ 总项 | 报告路径 |
|------|------|--------------|---------|
| Stage 1.5（数据质量） | [{passed / failed}] | [{7/7}] | [{reports/gate_stage_1_5.md}] |
| Stage 2.5（SAP 验验证| [{passed / failed}] | [{7/7}] | [{reports/gate_stage_2_5.md}] |
| Stage 3.5（结果质量） | [{passed / failed}] | [{7/7}] | [{reports/gate_stage_3_5.md}] |

### 11.1 关键门闸发现（Key Gate Findings9
- [{Stage 1.5 关键发现}]
- [{Stage 2.5 关键发现}]
- [{Stage 3.5 关键发现}]

---

## 12. Literature Seed（文献种9/ Literature Seed9
> MSRA Phase 1 文献对比9Top 5 关键文献，由 systematic-survey 9Stage 5.1 扩展9
| 序号 | 标题 | 作9| 年份 | DOI | 相关9|
|------|------|------|------|-----|--------|
| 1 | [{文献标题 1}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | core |
| 2 | [{文献标题 2}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | core |
| 3 | [{文献标题 3}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | supporting |
| 4 | [{文献标题 4}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | supporting |
| 5 | [{文献标题 5}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | peripheral |

**相关性枚9*：`core`（直接回9RQ9 `supporting`（提供背景）/ `peripheral`（边缘相关）

---

## 13. Journal Template（期刊模9/ Journal Template9
> 期刊选择信息，用于论文格式化9
| 字段 | 9| 说明 |
|------|-----|------|
| template | [{General / NEJM / Lancet / JAMA / BMJ}] | 期刊模板名称 |
| source | shared/journal-templates/ | 模板源路9|
| impact_factor | [{IF 值}] | 影响因子（可选） |
| submission_format | [{格式要求}] | 投稿格式要求 |

---

## 14. Paper Configuration（论文配9/ Paper Configuration9
> 论文写作的预填配置，9MSRA 推导，可9Stage 5.0 调整9
| 字段 | 9| 说明 |
|------|-----|------|
| Discipline | [{临床医学 / 诊断医学 / 循证医学}] | 学科领域 |
| Paper Type | IMRaD | 论文结构类型 |
| Citation Format | Vancouver | 引用格式（APA7 / Vancouver / Chicago / MLA / IEEE9|
| Body Language | Bilingual | 正文语言（English / Chinese / Bilingual9|
| Reporting Guideline | [{CONSORT / STROBE / STARD / PRISMA 2020}] | 报告规范 |
| Existing Materials | Data 9\| Results 9\| Tables [{9❌}] \| Figures [{9❌}] | 已有素材清单 |

---

## 15. Bibliography（参考文9/ Bibliography9
> 初始为空，由 Stage 5.1 systematic-survey 补充。MSRA Literature Seed 先行（见912 节）9
```
[EMPTY 99Stage 5.1 systematic-survey 补充；MSRA seed 先行]
```

---

## 16. Reproducibility Lock（可复现性锁9/ Reproducibility Lock9
> 配置锁定文件，对9`shared/artifact_reproducibility_pattern.md` 标准结构9> 此块作为 Material Passport (Schema 9) 的可选子字段存在9
```yaml
repro_lock:
  schema_version: "1.0"                    # lock schema 版本
  stochasticity_declaration: "LLM outputs are not byte-reproducible. This lockfile documents configuration, not a deterministic replay guarantee."
  ars_version: "<MSRA Pipeline 版本9"     # 运行时的流水线版9
  model:
    family: <claude / gemini / gpt>         # provider family
    id: <model identifier>                  # 模型标识9    weight_stable: false                    # 始终9false，直到有签名认证

  prompts:
    hash_timing: skill-load                 # 哈希采集时机
    skill_md_hash: "<sha256:...>"           # SKILL.md 文件哈希
    agents_bundle_hash: "<sha256:...>"      # agent prompt bundle 哈希

  materials:
    list_hash: "<sha256:...>"               # [{filename, sha256}, ...] 清单哈希
    count: <N>                              # 会话材料数量

  external_protocols:
    s2_api_protocol_version: "3.3"          # S2 查询协议版本
    s2_snapshot_available: false            # 是否存在响应缓存

  cross_model:
    enabled: false                          # 是否启用了跨模型验证
    secondary_model_id: null                # 如启用，次要模型 ID
```

> **注意**：此块为配置文档，不是确定性重放保证。缺失键会导9lint 失败，null 值会通过但产生警告9
**说明**9- `repro_lock` 是配置锁定文件，**不是**复现保证
- 锁定的目的是记录分析时的环境状态，便于后续复现尝试
- `lock_statement` 固定9`configuration_lockfile_not_replay_guarantee`，明确语义边9
---

## 模板使用说明

### 适用场景

本模板用9MSRA Pipeline Stage 4（统计报告）完成后，9Stage 5（论文写作）传递结构化数据。当用户9Stage 4 checkpoint 选择 [B] 继续写论文时，由 `scripts/generate_msra_handoff_bundle.py` 自动生成9
### 生成方式

1. **自动生成（推荐）**：调9`generate_handoff_bundle(pm, sap_path, output_dir)`，脚本从 passport、SAP、final_report 自动提取字段
2. **手工填写**：复制本模板，将 `[{占位符}]` 替换为实际内9
### 字段填写优先9
| 优先9| 字段 | 来源 |
|--------|------|------|
| P0（必须） | Source, Research Question, Results Bundle, Methods Summary | passport + SAP |
| P1（重要） | Key Findings, Methods Paper-Ready Format, RQ Consistency Check | final_report |
| P2（建议） | Safety Findings, Limitations, Quality Gate Report | final_report + gate reports |
| P3（可选） | Literature Seed, Journal Template, Bibliography | 用户输入 / Stage 5.1 补充 |

### 消费9
- **Stage 5.0 Paper Intake**：读9Source / Paper Configuration 初始化论文项9- **Stage 5.1 systematic-survey**：读9Literature Seed 作为文献检索起点，回填 Bibliography
- **Stage 5.2 Methods**：读9Methods Summary / Methods Paper-Ready Format
- **Stage 5.2 Results**：读9Results Bundle / Key Findings / Results to Claims Mapping
- **Stage 5.2 Discussion**：读9Safety Findings / Limitations
- **Stage 5.5 Integrity Check**：读9RQ Consistency Check / Quality Gate Report

### Schema 对齐

- **Schema 9 (Material Passport)**：第 1 9Source 字段9Passport 元数据对齐；916 9Reproducibility Lock 9`repro_lock` 字段对齐
- **Schema 11 (R&R Traceability Matrix)**：第 10 9Results to Claims Mapping 为后9Stage 5.7 修订阶段的追溯矩阵提供基础

### 版本管理

- 每次生成新版本时，递增 `version` 字段（如 v1.0 9v1.19- `status` 字段流转：`draft` 9`verified` 9`consumed`
- 重大修改时更9`created_date`
