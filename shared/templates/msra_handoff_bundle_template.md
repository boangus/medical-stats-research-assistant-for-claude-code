---
study_id: MSRA-{YYYY}-{NNN}
version: v1.0
created_date: YYYY-MM-DD
status: draft
template_type: msra_handoff_bundle
---

# MSRA Handoff Bundle 模板

> MSRA 项目专用。Stage 4（统计报告）→ Stage 5（论文写作）的数据传递契约。
> 由 `scripts/generate_msra_handoff_bundle.py` 自动填充，亦可手工填写。
> 对齐 `shared/handoff_schemas.md` Schema 9 (Material Passport) 与 Schema 11 (R&R Traceability Matrix)。
>
> **生成条件**：`passport.track == "full_paper"` 且 Stage 1-4 全部 completed。

---

## 1. Source（元数据 / Source Metadata）

> 本节记录 Bundle 的来源信息，用于跨阶段追溯。

| 字段 | 值 | 说明 |
|------|-----|------|
| passport_id | [{passport_id}] | MSRA Material Passport 唯一标识 |
| study_type | [{study_type}] | 研究类型（RCT / 观察性研究 / 诊断试验 / 系统综述等） |
| msra_version | [{msra_version}] | MSRA Pipeline 版本号 |
| track | full_paper | 轨道标识（固定为 full_paper） |
| generated_at | [{generated_at}] | Bundle 生成时间（ISO 8601） |
| schema_version | 1.0 | 本模板 Schema 版本 |

---

## 2. Research Question（研究问题 / Research Question）

> 主研究问题与子问题。来源于 SAP.md，用于论文 Introduction。

### 2.1 主研究问题（Primary RQ）

[{主研究问题：单一疑问句形式}]

### 2.2 子问题（Sub-Questions）

1. [{子问题 1}]
2. [{子问题 2}]
3. [{子问题 3}]

### 2.3 研究假设（Hypothesis，可选）

- H₀: [{零假设}]
- H₁: [{备择假设}]

---

## 3. Results Bundle（结果包 / Results Bundle）

> 统计报告产出的表格、图表及结果解读路径，用于论文 Results 章节。

### 3.1 结果解读路径（Results Interpretation Path）

- 主报告文件: [{final_report_path}]
- 解读顺序: [{建议阅读顺序，如 "Table 1 → Table 2 → Figure 1 → Table 3"}]

### 3.2 Tables 清单（Tables Inventory）

| 编号 | 文件路径 | 内容描述 | 类型标签 |
|------|---------|---------|---------|
| Table 1 | [{tables/table1.docx}] | [{基线特征表}] | baseline |
| Table 2 | [{tables/table2.docx}] | [{主要终点分析}] | primary_outcome |
| Table 3 | [{tables/table3.docx}] | [{次要终点分析}] | secondary_outcome |
| Table 4 | [{tables/table4.docx}] | [{敏感性分析}] | sensitivity |

**类型标签枚举**：`baseline` / `primary_outcome` / `secondary_outcome` / `safety` / `sensitivity` / `subgroup` / `demographic`

### 3.3 Figures 清单（Figures Inventory）

| 编号 | 文件路径 | 内容描述 | 类型标签 |
|------|---------|---------|---------|
| Figure 1 | [{figures/fig1.png}] | [{CONSORT 流程图}] | flowchart |
| Figure 2 | [{figures/fig2.png}] | [{Kaplan-Meier 曲线}] | survival_curve |
| Figure 3 | [{figures/fig3.png}] | [{森林图}] | forest_plot |

**类型标签枚举**：`flowchart` / `survival_curve` / `forest_plot` / `boxplot` / `scatter` / `bar` / `roc` / `calibration` / `heatmap`

---

## 4. Methods Summary（方法学摘要 / Methods Summary）

> 统计方法来自 SAP，方法学描述来自报告 Phase 5。用于论文 Methods 章节。

### 4.1 统计方法（来自 SAP）

[{统计方法描述：从 SAP.md "统计方法" 章节提取}]

### 4.2 方法学描述（来自报告 Phase 5）

[{方法学描述：从 final_report "方法学描述" 章节提取}]

### 4.3 分析人群定义（Analysis Populations）

| 人群 | 定义 | 排除标准 |
|------|------|---------|
| ITT | [{所有随机化受试者}] | [{无}] |
| PP | [{完成方案的受试者}] | [{严重违反方案}] |
| Safety | [{至少接受一剂药物的受试者}] | [{未接受干预}] |

---

## 5. Key Findings（核心发现 / Key Findings）

> 显著性结果与效应量列表，用于论文 Introduction 与 Discussion。

### 5.1 显著性结果（Significant Results）

- [{显著性结果 1：含 p 值与方向}]
- [{显著性结果 2：含 p 值与方向}]
- [{显著性结果 3：含 p 值与方向}]

### 5.2 效应量列表（Effect Sizes）

| 指标 | 效应量 | 95% CI | p 值 | 解读 |
|------|--------|--------|------|------|
| [{主要终点}] | [{HR=0.65}] | [{0.48-0.88}] | [{0.005}] | [{干预组风险降低 35%}] |
| [{次要终点}] | [{OR=1.82}] | [{1.20-2.76}] | [{0.005}] | [{干预组获益显著}] |

---

## 6. Safety Findings（安全性发现 / Safety Findings）

> 安全性分析结果，用于论文 Discussion。

### 6.1 不良事件汇总（Adverse Events Summary）

| 事件 | 干预组 n (%) | 对照组 n (%) | p 值 |
|------|-------------|-------------|------|
| [{不良事件 1}] | [{n (X%)}] | [{n (X%)}] | [{p}] |
| [{严重不良事件}] | [{n (X%)}] | [{n (X%)}] | [{p}] |

### 6.2 安全性结论（Safety Conclusion）

[{安全性结论描述}]

---

## 7. Limitations（局限性 / Limitations）

> 研究局限性讨论，用于论文 Discussion。

1. [{局限性 1：样本量 / 选择偏倚 / 失访等}]
2. [{局限性 2：测量局限 / 混杂因素等}]
3. [{局限性 3：外推性 / 单中心等}]
4. [{局限性 4：统计方法局限}]

---

## 8. Methods (Paper-Ready Format)（论文方法学格式 / Methods Paper-Ready）

> 论文 Methods 段落可直接引用的结构化文本。

### 8.1 主分析方法（Primary Analysis Method）

[{主分析方法描述：可直接粘贴到论文 Methods}]

### 8.2 样本量计算（Sample Size Calculation）

[{样本量计算描述：含检验效能、显著性水平、效应量假设}]

### 8.3 敏感性分析（Sensitivity Analysis）

[{敏感性分析描述：含方法与目的}]

### 8.4 多重性控制（Multiplicity Control）

[{多重性控制策略：Bonferroni / Holm / Gatekeeping 等}]

---

## 9. RQ Consistency Check（研究问题一致性校验 / RQ Consistency Check）

> SAP 与 final_report 中研究问题的一致性校验，确保论文 Introduction 与分析计划对齐。

### 9.1 一致性状态（Consistency Status）

- 状态: [{✅ 一致 / ⚠️ 基本一致 / ❌ 不一致 / ⚠️ 无法自动判定}]

### 9.2 SAP 中的研究问题

[{SAP 中提取的研究问题}]

### 9.3 final_report 中的研究问题

[{final_report 中提取的研究问题}]

### 9.4 差异说明（Difference Note）

[{差异说明：若不一致，描述实质性差异并建议人工核查}]

---

## 10. Results to Claims Mapping（结果到 Claim 映射 / Results to Claims Mapping）

> 可追溯性表格，建立统计结果与论文 Claim 的双向追溯链。

共识别 [{N}] 个可追溯的统计结果 Claim。

| Claim ID | 关键统计量 | 结果描述（来源行） | 论文对应章节建议 |
|----------|-----------|-------------------|------------------|
| CLAIM-001 | [{HR=0.65}] | [{主要终点 Cox 回归结果}] | Results / Abstract |
| CLAIM-002 | [{p=0.005}] | [{组间差异显著性}] | Results |
| CLAIM-003 | [{95% CI 0.48-0.88}] | [{效应量置信区间}] | Results / Abstract |

**使用说明**：
- 每个 CLAIM-NNN 对应 final_report 中的一条统计结果
- 论文写作时，在 Results 段落引用对应 Claim ID 以建立双向追溯链
- 论文定稿后，可通过 Claim ID 反查 final_report 中的原始统计输出

---

## 11. Quality Gate Report（质量门闸报告 / Quality Gate Report）

> Stage 1.5 / 2.5 / 3.5 门闸通过情况。

| 门闸 | 状态 | 通过项 / 总项 | 报告路径 |
|------|------|--------------|---------|
| Stage 1.5（数据质量） | [{passed / failed}] | [{7/7}] | [{reports/gate_stage_1_5.md}] |
| Stage 2.5（SAP 验证） | [{passed / failed}] | [{7/7}] | [{reports/gate_stage_2_5.md}] |
| Stage 3.5（结果质量） | [{passed / failed}] | [{7/7}] | [{reports/gate_stage_3_5.md}] |

### 11.1 关键门闸发现（Key Gate Findings）

- [{Stage 1.5 关键发现}]
- [{Stage 2.5 关键发现}]
- [{Stage 3.5 关键发现}]

---

## 12. Literature Seed（文献种子 / Literature Seed）

> MSRA Phase 1 文献对比的 Top 5 关键文献，由 deep-research 在 Stage 5.1 扩展。

| 序号 | 标题 | 作者 | 年份 | DOI | 相关性 |
|------|------|------|------|-----|--------|
| 1 | [{文献标题 1}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | core |
| 2 | [{文献标题 2}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | core |
| 3 | [{文献标题 3}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | supporting |
| 4 | [{文献标题 4}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | supporting |
| 5 | [{文献标题 5}] | [{作者}] | [{年份}] | [{10.xxxx/xxxx}] | peripheral |

**相关性枚举**：`core`（直接回应 RQ）/ `supporting`（提供背景）/ `peripheral`（边缘相关）

---

## 13. Journal Template（期刊模板 / Journal Template）

> 期刊选择信息，用于论文格式化。

| 字段 | 值 | 说明 |
|------|-----|------|
| template | [{General / NEJM / Lancet / JAMA / BMJ}] | 期刊模板名称 |
| source | shared/journal-templates/ | 模板源路径 |
| impact_factor | [{IF 值}] | 影响因子（可选） |
| submission_format | [{格式要求}] | 投稿格式要求 |

---

## 14. Paper Configuration（论文配置 / Paper Configuration）

> 论文写作的预填配置，由 MSRA 推导，可在 Stage 5.0 调整。

| 字段 | 值 | 说明 |
|------|-----|------|
| Discipline | [{临床医学 / 诊断医学 / 循证医学}] | 学科领域 |
| Paper Type | IMRaD | 论文结构类型 |
| Citation Format | Vancouver | 引用格式（APA7 / Vancouver / Chicago / MLA / IEEE） |
| Body Language | Bilingual | 正文语言（English / Chinese / Bilingual） |
| Reporting Guideline | [{CONSORT / STROBE / STARD / PRISMA 2020}] | 报告规范 |
| Existing Materials | Data ✅ \| Results ✅ \| Tables [{✅/❌}] \| Figures [{✅/❌}] | 已有素材清单 |

---

## 15. Bibliography（参考文献 / Bibliography）

> 初始为空，由 Stage 5.1 deep-research 补充。MSRA Literature Seed 先行（见第 12 节）。

```
[EMPTY — 由 Stage 5.1 deep-research 补充；MSRA seed 先行]
```

---

## 16. Reproducibility Lock（可复现性锁定 / Reproducibility Lock）

> 配置锁定文件，对齐 `shared/artifact_reproducibility_pattern.md` 标准结构。
> 此块作为 Material Passport (Schema 9) 的可选子字段存在。

```yaml
repro_lock:
  schema_version: "1.0"                    # lock schema 版本
  stochasticity_declaration: "LLM outputs are not byte-reproducible. This lockfile documents configuration, not a deterministic replay guarantee."
  ars_version: "<MSRA Pipeline 版本号>"     # 运行时的流水线版本

  model:
    family: <claude / gemini / gpt>         # provider family
    id: <model identifier>                  # 模型标识符
    weight_stable: false                    # 始终为 false，直到有签名认证

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

> **注意**：此块为配置文档，不是确定性重放保证。缺失键会导致 lint 失败，null 值会通过但产生警告。

**说明**：
- `repro_lock` 是配置锁定文件，**不是**复现保证
- 锁定的目的是记录分析时的环境状态，便于后续复现尝试
- `lock_statement` 固定为 `configuration_lockfile_not_replay_guarantee`，明确语义边界

---

## 模板使用说明

### 适用场景

本模板用于 MSRA Pipeline Stage 4（统计报告）完成后，向 Stage 5（论文写作）传递结构化数据。当用户在 Stage 4 checkpoint 选择 [B] 继续写论文时，由 `scripts/generate_msra_handoff_bundle.py` 自动生成。

### 生成方式

1. **自动生成（推荐）**：调用 `generate_handoff_bundle(pm, sap_path, output_dir)`，脚本从 passport、SAP、final_report 自动提取字段
2. **手工填写**：复制本模板，将 `[{占位符}]` 替换为实际内容

### 字段填写优先级

| 优先级 | 字段 | 来源 |
|--------|------|------|
| P0（必须） | Source, Research Question, Results Bundle, Methods Summary | passport + SAP |
| P1（重要） | Key Findings, Methods Paper-Ready Format, RQ Consistency Check | final_report |
| P2（建议） | Safety Findings, Limitations, Quality Gate Report | final_report + gate reports |
| P3（可选） | Literature Seed, Journal Template, Bibliography | 用户输入 / Stage 5.1 补充 |

### 消费者

- **Stage 5.0 Paper Intake**：读取 Source / Paper Configuration 初始化论文项目
- **Stage 5.1 deep-research**：读取 Literature Seed 作为文献检索起点，回填 Bibliography
- **Stage 5.2 Methods**：读取 Methods Summary / Methods Paper-Ready Format
- **Stage 5.2 Results**：读取 Results Bundle / Key Findings / Results to Claims Mapping
- **Stage 5.2 Discussion**：读取 Safety Findings / Limitations
- **Stage 5.5 Integrity Check**：读取 RQ Consistency Check / Quality Gate Report

### Schema 对齐

- **Schema 9 (Material Passport)**：第 1 节 Source 字段与 Passport 元数据对齐；第 16 节 Reproducibility Lock 与 `repro_lock` 字段对齐
- **Schema 11 (R&R Traceability Matrix)**：第 10 节 Results to Claims Mapping 为后续 Stage 5.7 修订阶段的追溯矩阵提供基础

### 版本管理

- 每次生成新版本时，递增 `version` 字段（如 v1.0 → v1.1）
- `status` 字段流转：`draft` → `verified` → `consumed`
- 重大修改时更新 `created_date`
