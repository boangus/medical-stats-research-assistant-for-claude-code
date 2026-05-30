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