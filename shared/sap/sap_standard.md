# SAP 标准格式定义

> MSRA 项目专用。定义统计分析计划(SAP)的标准格式，确保阶段间数据传递的一致性。

---

## 1. SAP 文件格式

### 1.1 文件命名规范

```
sap_{study_id}_{version}.md
```

示例：
- `sap_RCT001_v1.0.md`
- `sap_cohort002_v2.1.md`

### 1.2 文件结构

```yaml
---
study_id: "RCT001"
version: "1.0"
created_date: "2026-05-30"
last_modified: "2026-05-30"
status: "approved"  # draft / under_review / approved / locked
study_type: "RCT"  # RCT / observational / diagnostic
---

# 统计分析计划 (Statistical Analysis Plan)

## 1. 研究概述
## 2. 分析人群
## 3. 终点定义
## 4. 统计方法
## 5. 多重比较控制
## 6. 期中分析
## 7. 变量构造定义
## 8. 分析规范表
```

---

## 2. SAP 章节标准

### 2.1 研究概述 (Section 1)

```markdown
## 1. 研究概述

### 1.1 研究设计和目的
- 研究类型: [RCT/队列/病例对照/横断面]
- 研究目的: [主要研究目的]
- 研究假设: [主要假设]

### 1.2 样本量依据
- 计划样本量: [N]
- 计算方法: [方法名称]
- 检验效能: [Power]
- 显著性水平: [α]
- 失访率: [%]
```

### 2.2 分析人群 (Section 2)

```markdown
## 2. 分析人群

### 2.1 意向性治疗人群 (ITT)
- 定义: [纳入标准]
- 排除标准: [排除标准]

### 2.2 符合方案人群 (PP)
- 定义: [纳入标准]
- 排除标准: [排除标准]

### 2.3 安全性人群
- 定义: [纳入标准]
```

### 2.3 终点定义 (Section 3)

```markdown
## 3. 终点定义

### 3.1 主要终点
- 名称: [终点名称]
- 定义: [操作性定义]
- 测量方法: [测量方法]
- 测量时间点: [时间点]
- 裁剪规则: [如适用]

### 3.2 次要终点
| 序号 | 名称 | 定义 | 测量方法 | 时间点 |
|------|------|------|---------|--------|
| 1 | ... | ... | ... | ... |

### 3.3 探索性终点
| 序号 | 名称 | 定义 | 测量方法 | 时间点 |
|------|------|------|---------|--------|
| 1 | ... | ... | ... | ... |
```

### 2.4 统计方法 (Section 4)

```markdown
## 4. 统计方法

### 4.1 主要分析
- 方法: [具体方法名称]
- 调整变量: [变量列表]
- 缺失数据处理: [方法]
- 估计目标: [Estimands 五要素]

### 4.2 次要分析
| 序号 | 分析 | 方法 | 调整变量 | 假设 |
|------|------|------|---------|------|
| 1 | ... | ... | ... | ... |

### 4.3 敏感性分析
| 序号 | 分析 | 方法 | 目的 |
|------|------|------|------|
| 1 | ... | ... | ... |

### 4.4 亚组分析
| 序号 | 亚组变量 | 分层 | 交互检验 |
|------|---------|------|---------|
| 1 | ... | ... | ... |
```

### 2.5 变量选择推荐 (Section 7.5) ⭐ 新增

```markdown
## 7.5 变量选择推荐

> 基于微信推文和统计学原则，提供变量选择建议。

### 7.5.1 强制纳入变量（不看p值）
| 变量 | 类型 | 纳入理由 | 依据 |
|------|------|---------|------|
| age | 连续 | 预后因素 | 临床重要性 |
| sex | 分类 | 混杂因素 | DAG分析 |
| bmi | 连续 | 预后因素 | 文献依据 |

### 7.5.2 建议纳入变量（单因素p<0.1）
| 变量 | 类型 | 单因素p值 | 纳入建议 |
|------|------|----------|---------|
| hypertension | 分类 | 0.08 | 建议纳入 |
| diabetes | 分类 | 0.12 | 可选纳入 |

### 7.5.3 不纳入变量（p≥0.1且非混杂）
| 变量 | 类型 | 单因素p值 | 不纳入理由 |
|------|------|----------|-----------|
| smoking | 分类 | 0.35 | 非混杂，p>0.1 |
```

### 2.6 变量构造定义 (Section 7.6) ⭐ 关键

```markdown
## 7.6 变量构造定义

> 此章节定义所有分析变量的构造逻辑，供 Stage 3 执行。

| 变量名 | 类型 | 构造公式 | 切点/分类 | 依据 | 缺失处理 |
|--------|------|---------|----------|------|---------|
| age | 连续 | 入组日期 - 出生日期（年） | - | 标准人口学 | 删除 |
| bmi | 连续 | 体重(kg) / (身高(m))² | - | WHO标准 | 标记缺失 |
| age_group | 分类 | age < 60 → "young"; 60-70 → "middle"; ≥70 → "old" | <60/60-70/≥70 | 临床惯例 | 归入missing组 |
| treatment_response | 二分类 | RECIST v1.1: CR+PR → "responder"; SD+PD → "non-responder" | - | 实体瘤疗效标准 | 无评估→non-responder |
| comorbidity_score | 连续 | Charlson指数计算 | - | 标准计算 | 归入0分 |
```

### 2.6b 变量依赖图 (Section 7.7) 🆕

```markdown
## 7.7 变量依赖图

> Phase 6.5 自动生成变量依赖 DAG，附在 SAP 文档末尾。

- 节点类型：原始变量（圆形）vs 衍生变量（方形）
- 边：构造依赖关系（箭头从源变量指向目标变量）
- 输出格式：graphviz PNG（首选）或 ASCII 文本图（降级）
- 生成脚本：`shared/templates/variable_dag_template.py`
```

### 2.7 分析规范表 (Section 8) ⭐ 关键

```markdown
## 8. 分析规范表

> 此表格定义每个分析的具体参数，供 Stage 3 执行。

| 分析ID | 分析名称 | 人群 | 方法 | 主要变量 | 调整变量 | 缺失处理 | 假设检验 |
|--------|---------|------|------|---------|---------|---------|---------|
| A1 | 主要终点分析 | ITT | ANCOVA | hba1c_change | baseline_hba1c, age | 多重插补 | F-test |
| A2 | 次要终点1 | ITT | Logistic | response | age, sex, bmi | 完整案例 | Wald test |
| A3 | 敏感性1-PP | PP | ANCOVA | hba1c_change | baseline_hba1c, age | 完整案例 | F-test |
| S1 | 亚组-年龄 | ITT | 交互项 | hba1c_change | age_group × treatment | 多重插补 | 交互p值 |
```

### 2.8 统计方法选择推荐 (Section 8.5) ⭐ 新增

```markdown
## 8.5 统计方法选择推荐

> 基于研究设计和数据特征，推荐统计方法。

### 8.5.1 主要分析方法
| 分析 | 推荐方法 | 选择理由 | 假设条件 | 替代方案 |
|------|---------|---------|---------|---------|
| 主要终点 | ANCOVA | RCT连续结局金标准 | 正态+方差齐 | 非参数ANCOVA |

### 8.5.2 次要分析方法
| 分析 | 推荐方法 | 选择理由 |
|------|---------|---------|
| 次要终点1 | Logistic回归 | 二分类结局 |
| 亚组分析 | 交互项检验 | 预设亚组 |

### 8.5.3 敏感性分析方法
| 分析 | 推荐方法 | 目的 |
|------|---------|------|
| 缺失数据 | 多重插补 vs 完整案例 | 评估缺失影响 |
| 人群 | ITT vs PP | 评估依从性影响 |
```

---

## 3. SAP 传递机制

### 3.1 阶段间SAP传递

```
Stage 2 (analysis-plan)
    ↓ 生成 sap_{study_id}_v1.0.md
    ↓ 进入 Stage 2.5 质量门闸
Stage 2.5 (SAP质量门闸)
    ↓ 检查SAP完整性
    ↓ 标记 status: "approved"
    ↓ 进入 Stage 3
Stage 3 (analysis-exec)
    ↓ 读取 sap_{study_id}_v1.0.md
    ↓ 验证SAP格式
    ↓ 按SAP执行分析
```

### 3.2 SAP 文件位置

```
project_root/
├── sap/
│   ├── sap_RCT001_v1.0.md          # SAP主文件
│   ├── sap_RCT001_v1.0_variables.md # 变量构造规格书
│   └── sap_RCT001_v1.0_analysis.md  # 分析规范表
├── data/
├── analysis/
└── report/
```

---

## 4. SAP 验证规则

### 4.1 格式验证

| 检查项 | 规则 | 严重程度 |
|--------|------|---------|
| Frontmatter完整性 | 必须包含study_id, version, status, study_type | P0 |
| 章节完整性 | 必须包含Section 1-8 | P0 |
| 变量构造定义 | Section 7必须包含所有分析变量 | P0 |
| 分析规范表 | Section 8必须包含所有分析 | P0 |

### 4.2 内容验证

| 检查项 | 规则 | 严重程度 |
|--------|------|---------|
| 方法与研究类型匹配 | RCT必须使用ITT/PP人群 | P1 |
| 效应量预定义 | 必须指定效应量类型和报告格式 | P1 |
| 敏感性分析 | 至少2种敏感性分析 | P1 |
| 缺失数据处理 | 必须指定处理方法 | P0 |

### 4.3 一致性验证

| 检查项 | 规则 | 严重程度 |
|--------|------|---------|
| 变量名一致 | SAP中变量名与数据字典一致 | P0 |
| 方法可执行 | 所有方法在当前环境下可执行 | P1 |
| 样本量匹配 | SAP计划样本量与实际数据匹配 | P0 |

---

## 5. SAP 执行追踪

### 5.1 执行状态追踪

```yaml
execution_status:
  sap_version: "1.0"
  execution_start: "2026-05-30T10:00:00"
  execution_end: "2026-05-30T12:00:00"
  
  analyses:
    - id: "A1"
      name: "主要终点分析"
      status: "completed"  # pending / in_progress / completed / skipped
      method: "ANCOVA"
      deviations: []
      
    - id: "A2"
      name: "次要终点1"
      status: "completed"
      method: "Logistic"
      deviations: []
      
    - id: "A3"
      name: "敏感性1-PP"
      status: "skipped"
      method: "ANCOVA"
      deviations:
        - reason: "PP人群样本量不足"
          impact: "转为探索性分析"
```

### 5.2 偏差记录

```yaml
deviations:
  - id: "DEV001"
    analysis_id: "A1"
    type: "method_change"  # method_change / variable_change / population_change
    original: "ANCOVA"
    actual: "ANCOVA with robust SE"
    reason: "方差齐性假设违反"
    impact: "结果更保守"
    approval: "user_approved"  # user_approved / documented
    timestamp: "2026-05-30T10:30:00"
```

---

## 8.5 中心效应处理策略 🆕（仅 multi-dataset 模式）

> 触发条件：passport 中 multi_dataset_mode artifact 存在且状态为 completed
> 参考：shared/statistics-methods/chapters/ch34-treatment-effects-in-multicenter-rcts.md

### 8.5.1 汇总层面 Estimands 定义
- Overall estimand：跨中心汇总效应量
- Per-site estimand：各中心内效应量（如需）

### 8.5.2 中心效应处理策略（三选一，需在 SAP 中预声明）
| 策略 | 适用条件 | 模型 | 输出 |
|------|---------|------|------|
| 固定效应 | 中心间同质（I²<25%） | 中心作为协变量的回归模型 | 汇总效应量 + 中心调整效应 |
| 随机效应 | 中心间异质（I² 25-75%） | 混合效应模型（中心随机截距） | 汇总效应量 + 中心间方差 |
| 两步法 meta | 中心间方法差异大 | 逐中心分析 + meta 汇总 | 汇总效应量 + I²/τ²/Q |

### 8.5.3 异质性评估
- I² 统计量：<25%低异质，25-75%中异质，>75%高异质
- τ² 统计量：研究间方差
- Cochran's Q 检验：p<0.10 提示显著异质

### 8.5.4 敏感性分析
- leave-one-out：逐一排除各中心，评估结论稳健性
- 结果不一致（I²>75%）时，必须报告各中心单独效应量

## 9. SAP 修正协议 🆕

### 9.1 修正触发条件

在 Stage 3 执行过程中，当 Phase 7 独立验证发现 SAP 预设方法与数据特征不一致时，可触发 SAP 修正。

| 触发条件 | 检测方式 | 示例 |
|---------|---------|------|
| 正态性不满足 | Shapiro-Wilk p < 0.05 | SAP 预设参数方法，但数据非正态 |
| 多重共线性 | VIF > 10 | SAP 预设包含全部协变量，但存在高共线性 |
| 样本量不足 | 实际 < SAP 预设的 70% | Phase 0 警告升级 |
| 完全分离 | Logistic 收敛警告 | Firth 校正仍失败 |

### 9.2 修正分类

| 类别 | 说明 | 审批级别 | 记录方式 |
|------|------|---------|---------|
| A-Method Swap | 方法替换（参数→非参数） | MANDATORY checkpoint | SAP amendment log + audit log |
| B-Covariate Adjust | 协变量增删 | SLIM checkpoint | SAP amendment log |
| C-Cutpoint Revise | 切点修改 | MANDATORY checkpoint（仅非预设切点） | SAP amendment log + 标注"事后分析" |
| D-Sample Restriction | 人群重新定义 | MANDATORY checkpoint | SAP amendment log + 标注"事后分析" |

### 9.3 修正记录格式

```json
{
  "amendment_id": "AMD-001",
  "original_spec": "ANCOVA with 5 covariates",
  "amended_spec": "Kruskal-Wallis (non-parametric)",
  "trigger": "Shapiro-Wilk p < 0.01, Box-Cox failed",
  "justification": "正态性严重违反且转换无效",
  "user_approval": true,
  "timestamp": "2026-06-18T10:30:00Z",
  "post_hoc_flag": true
}
```

### 9.4 防护措施

为防止 SAP 修正被滥用为"数据驱动假设"（data-driven hypothesis），Stage 3 设置以下硬性防护：

- **硬性上限**：整个 Stage 3 最多 3 次 Amendment（`SAP_AMENDMENT_MAX=3`，已在 `shared/passport/passport.py` 中定义为模块级常量）。该上限覆盖所有类别（A/B/C/D）的修正总和，不按类别分别计数。
- **D 类修正双 checkpoint**：D-Sample Restriction（人群重定义）由于可能引入选择偏倚，需要 2 次 MANDATORY checkpoint：
  - 第一次：确认修正必要性（即原始人群分析确实无法继续，而非"结果不理想"）
  - 第二次：确认修正方案（即新人群定义的合理性、剔除标准的预先声明性）
- **Amendment 计数器**：`passport.py` 的 `add_sap_amendment()` 方法自动计数，每次记录时调用 `get_sap_amendment_count()` 检查当前次数；超限抛出 `PassportError`，错误消息明确提示"如需继续修正，请退回 Stage 2 重新制定 SAP"。
- **报告标注**：所有修正后的分析在最终报告中标注为 "post-hoc analysis" 或 "amended from original SAP"，并在结果表的脚注中引用对应的 `amendment_id`。
- **不可回退**：一旦某次 Amendment 被记录并通过 checkpoint，不可撤销或修改；如需变更，必须作为新的 Amendment 记录（计入上限）。

### 9.5 审计日志格式

所有 SAP 修正必须在审计日志中完整记录以下字段，并标记为 `post_hoc_amendment`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `amendment_id` | string | 唯一标识符，格式 `AMD-NNN`（如 `AMD-001`） |
| `original_spec` | string | SAP 原始规范（方法、协变量、切点等） |
| `amended_spec` | string | 修正后的规范 |
| `trigger` | string | 触发条件（如 "Shapiro-Wilk p<0.01"） |
| `justification` | string | 修正理由（必须基于数据特征，不可基于结果方向） |
| `user_approval` | bool | 用户审批状态（MANDATORY checkpoint 必须为 `true`） |
| `timestamp` | ISO 8601 | 修正记录时间（UTC） |
| `post_hoc_flag` | bool | 固定为 `true`，标记为事后分析 |

**审计日志写入规则**：
- 所有修正必须在审计日志中标记为 `post_hoc_amendment`
- 审计日志在 Phase 10 质检报告中完整呈现，不可省略
- 若 Stage 3 结束时审计日志为空（无修正），需在 Phase 10 报告中显式声明 "No SAP amendment during Stage 3"

### 9.6 修正流程示例

以下给出一个完整的 A-Method Swap 修正示例，展示从触发到记录的全流程：

**场景**：SAP 预设使用 ANCOVA（参数方法）比较两组主要结局，但 Phase 7 独立验证发现正态性假设不满足。

**Step 1 — 触发检测（Phase 7）**：
- 独立验证脚本对残差执行 Shapiro-Wilk 检验，得到 p=0.003（<0.05）
- `SAPConsistencyCheck.check_normality()` 返回 `consistency: false`
- `_classify_amendment_trigger()` 将其分类为 `A-Method Swap`

**Step 2 — 方案制定**：
- 原方案：ANCOVA（参数方法，含 3 个协变量）
- 修正方案：Wilcoxon rank-sum（非参数方法，不依赖正态性假设）
- 备选考虑：Box-Cox 转换已尝试但未改善正态性，故排除转换路径

**Step 3 — MANDATORY checkpoint 审批**：
- 系统暂停执行，向用户呈现：触发证据、原方案、修正方案、对结论稳健性的预期影响
- 用户确认后 `user_approval: true`，方可继续

**Step 4 — 记录写入**：

```json
{
  "amendment_id": "AMD-001",
  "original_spec": "ANCOVA with 3 covariates (age, baseline_score, site)",
  "amended_spec": "Wilcoxon rank-sum test (non-parametric)",
  "trigger": "Shapiro-Wilk p=0.003 on ANCOVA residuals",
  "justification": "正态性严重违反，Box-Cox 转换无效，非参数方法为预设 SAP 的合规替代",
  "user_approval": true,
  "timestamp": "2026-06-18T10:30:00Z",
  "post_hoc_flag": true
}
```

**Step 5 — 双重记录**：
- `amendment_log`：通过 `passport_manager.add_sap_amendment("AMD-001", amendment_data)` 写入 Material Passport，计数器自动递增
- `audit log`：写入 Phase 10 质检报告的审计日志章节，标记为 `post_hoc_amendment`

**Step 6 — 报告标注**：
- 最终结果表中该分析脚注标注："Amended from original SAP (AMD-001): ANCOVA → Wilcoxon rank-sum due to normality violation"
- 讨论章节单独段落说明修正原因及对结论稳健性的影响

## 6. 工具脚本

### 6.1 SAP 验证脚本

位置: `shared/sap/validate_sap.py`

功能:
- 验证SAP格式完整性
- 验证变量构造定义
- 验证分析规范表
- 生成验证报告

### 6.2 SAP 到代码转换

位置: `shared/sap/sap_to_code.py`

功能:
- 解析SAP分析规范表
- 生成R/Python分析代码骨架
- 验证代码与SAP一致性

### 6.3 SAP 执行追踪

位置: `shared/sap/track_execution.py`

功能:
- 追踪SAP执行状态
- 记录偏差
- 生成执行报告

---

*文档版本: v0.1.0*
*创建日期: 2026-05-30*
*维护者: MSRA开发团队*
---

## 7. SAP 模板

项目提供以下标准化 SAP 模板，可直接复用或作为参考：

### 7.1 观察性研究模板

**文件**: `shared/sap/templates/sap_template_observational.md`

适用于队列研究、病例对照、横断面研究等观察性设计。

**核心结构**:
1. 研究设计 → 设计类型、人群、时间范围
2. 研究目的 → 主要/次要目的
3. 研究样本 → 样本量、排除标准、缺失处理
4. 变量定义 → 暴露、结局、协变量、排除变量
5. 统计方法 → 描述性、基线比较、效应估计、敏感性分析
6. 图表计划 → Tables、Figures
7. 待确认事项
8. 软件环境
9. 修改记录

### 7.2 RCT 模板

**文件**: `shared/sap/templates/sap_template_rct.md`

适用于随机对照试验。

**核心结构**:
1. 研究设计 → RCT 设计、干预措施
2. 研究目的 → 主要/次要目的
3. 分析人群 → ITT、PP、安全性人群
4. 样本量 → 计划样本量、检验效能、失访率
5. 变量定义 → 暴露、结局、协变量
6. 统计方法 → 描述性、主要分析、次要分析、敏感性分析、多重性控制
7. 图表计划
8. 期中分析
9. 待确认事项
10. 软件环境
11. 修改记录

### 7.3 诊断准确性研究模板

**文件**: `shared/sap/templates/sap_template_diagnostic.md`

适用于诊断试验准确性研究。

**核心结构**:
1. 研究设计 → 诊断准确性研究、金标准、待评价试验
2. 研究目的 → 诊断准确性评估
3. 研究样本 → 样本量、排除标准
4. 变量定义 → 试验结果、金标准结果、协变量
5. 统计方法 → 诊断指标、切点确定、置信区间、亚组分析
6. 图表计划
7. 待确认事项
8. 软件环境
9. 修改记录

### 7.4 模板使用方法

```markdown
# 使用步骤

1. 根据研究类型选择对应模板：
   - 观察性研究 → sap_template_observational.md
   - RCT → sap_template_rct.md
   - 诊断准确性研究 → sap_template_diagnostic.md

2. 替换模板中的占位符 [{内容}]

3. 根据实际研究内容调整章节：
   - 添加/删除协变量
   - 修改统计方法
   - 调整图表计划

4. 更新版本号和日期

5. 提交 Stage 2.5 质量门闸验证
```

### 7.5 模板设计原则

基于实际临床研究 SAP 实践经验总结，核心原则：

1. **清晰的变量定义**：每个变量都有明确的定义、类型、编码方式
2. **分层模型策略**：Model 1（粗模型）→ Model 2（部分调整）→ Model 3（全调整）
3. **标准化图表计划**：统一编号和命名规则
4. **修改记录追溯**：完整记录版本变更历史
5. **待确认事项清单**：明确列出需要用户确认的关键问题

---

*文档版本: v0.2.0*
*创建日期: 2026-05-30*
*最后更新: 2026-06-18*
*维护者: MSRA开发团队*
