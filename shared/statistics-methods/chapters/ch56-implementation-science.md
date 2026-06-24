# Ch56: 实施科学与混合方法研究 (Implementation Science & Mixed Methods)

> **适用场景**: 干预措施的真实世界实施、混合方法研究设计、实施效果评估
> **核心框架**: RE-AIM, CFIR, 混合方法设计 (Type I/II/III)
> **参考文献**: Curran et al. (2012), Aarons et al. (2011)

---

## 1. 概述

实施科学 (Implementation Science) 研究如何将证据有效地整合到常规实践和公共卫生中。与传统临床试验不同，实施科学关注：

- **研究→实践的转化**: 为什么有效干预未被采用？
- **实施策略**: 如何促进干预的采纳和维持？
- **实施结局**: 采纳率、保真度、可持续性

## 2. 主要框架

### 2.1 RE-AIM 框架

| 维度 | 定义 | 测量方法 | 示例 |
|------|------|---------|------|
| **Reach** | 目标人群的比例 | 参与者/符合条件人数 | 120/500 = 24% |
| **Effectiveness** | 干预效果 | 主要结局指标 | OR, RR, 均值差 |
| **Adoption** | 设置/提供者的采用比例 | 采用的机构/总机构 | 8/20 = 40% |
| **Implementation** | 干预保真度 | 保真度评分 | 85% 保真度 |
| **Maintenance** | 长期可持续性 | 6/12 个月后持续使用 | 70% 持续 |

### 2.2 CFIR (Consolidated Framework for Implementation Research)

5 大类 39 个构念：

```
1. 干预特征 (Intervention Characteristics)
   └── 证据来源、相对优势、适应性、复杂性

2. 外部环境 (Outer Setting)
   └── 患者需求、外部政策、同行压力

3. 内部环境 (Inner Setting)
   └── 组织文化、领导力、资源、网络

4. 个体特征 (Characteristics of Individuals)
   └── 知识、信念、自我效能

5. 实施过程 (Process)
   └── 规划、参与、执行、反思
```

## 3. 混合方法研究设计

### 3.1 设计类型

| 类型 | 名称 | 顺序 | 目的 |
|------|------|------|------|
| Type I | 探索性序列 | QUAL → quant | 量化研究开发 |
| Type II | 解释性序列 | QUAN → qual | 解释量化结果 |
| Type III | 聚合式 | QUAN + QUAL | 综合理解 |
| Type IV | 嵌入式 | QUAN(qual) | 量化框架内嵌入质性 |
| Type V | 转化式 | 多阶段 | 社会正义导向 |

### 3.2 实施结局测量

```r
# R: 实施结局的混合效应模型
library(lme4)

# 保真度评分（嵌套在机构内）
fidelity_model <- lmer(
  fidelity_score ~ time * intervention + (1 | site) + (1 | provider),
  data = df
)

# 采纳率（机构层面）
adoption_model <- glmer(
  adopted ~ site_size + leadership + training_hours + (1 | region),
  data = df_site,
  family = binomial
)

# 保真度的影响因素
fidelity_predictors <- lmer(
  fidelity ~ training_hours + supervision + provider_experience +
    complexity + (1 | site),
  data = df
)
```

```python
# Python: 实施结局分析
import statsmodels.formula.api as smf

# 保真度评分
model = smf.mixedlm(
    "fidelity_score ~ time * intervention",
    data=df,
    groups=df["site"],
    re_formula="~1"
)
result = model.fit()
```

## 4. 实施策略分类

**ERIC (Expert Recommendations for Implementing Change) 73 策略**:

| 类别 | 示例策略 | 编码 |
|------|---------|------|
| 培训和教育 | 从业者培训、教育外展 | A1-A8 |
| 利益相关者参与 | 外部促进、领导参与 | B1-B6 |
| 评估和反馈 | 审计和反馈、报告指标 | C1-C9 |
| 技术和工具 | 临床决策支持、提醒系统 | D1-D8 |
| 组织变革 | 改变基础设施、质量改进 | E1-E7 |
| 政策和资金 | 资金机制、政策强制 | F1-F5 |

## 5. 混合方法数据分析

### 5.1 质性数据编码

```r
# R: 质性编码辅助（量化方法处理质性数据）
library(quanteda)

# 文本分析
corpus <- corpus(interview_texts)
dfm_result <- dfm(corpus, remove_punct = TRUE, remove_stopwords = TRUE)
topfeatures(dfm_result, 20)
```

### 5.2 整合方法

```
── 混合方法整合 ──

量化结果:
- 采纳率: 65% (95% CI: 58-72%)
- 保真度评分: 3.8/5 (SD=0.9)
- 效果: OR=1.45 (95% CI: 1.12-1.88)

质性结果（主题分析）:
- 促进因素: 领导支持、培训充分、临床有用
- 障碍因素: 时间不足、技术问题、工作流程冲突

整合分析（收敛评估）:
- ✅ 一致: 量化和质性均显示领导支持是关键促进因素
- ⚠️ 部分矛盾: 量化显示保真度高，但质性揭示实际执行有偏差
- ❌ 不一致: 量化效果显著，但质性报告实施困难
```

## 6. 实施效果评估

### 6.1 差异中的差异 (DID)

```r
# 评估实施干预前后的变化
library(did)

# 双重差分
did_result <- att_gt(
  yname = "adoption_rate",
  tname = "time",
  idname = "site",
  gname = "implementation_time",
  data = panel_df,
  control_group = "nevertreated"
)

# 动态效果
aggte(did_result, type = "dynamic")
```

### 6.2 中断时间序列 (ITS)

```r
# 实施前后的趋势变化
library(segmented)

# 分段回归
its_model <- lm(adoption_rate ~ time + implementation + time_since_impl, data = df)
summary(its_model)

# 变点检测
seg_model <- segmented(its_model, seg.Z = ~time, psi = impl_time)
summary(seg_model)
```

## 7. 参考文献

1. Curran GM, Bauer M, Mittman B, Pyne JM, Stetler C. Effectiveness-implementation hybrid designs: combining elements of clinical effectiveness and implementation research to enhance public health impact. Med Care. 2012;50(3):217-226.
2. Aarons GA, Hurlburt M, Horwitz SM. Advancing a conceptual model of evidence-based practice implementation in public service sectors. Adm Policy Ment Health. 2011;38(1):4-23.
3. Glasgow RE, Vogt TM, Boles SM. Evaluating the public health impact of health promotion interventions: the RE-AIM framework. Am J Public Health. 1999;89(9):1322-1327.
4. Damschroder LJ, Aron DC, Keith RE, Kirsh SR, Alexander JA, Lowery JC. Fostering implementation of health services research findings into practice: a consolidated framework for advancing implementation science. Implement Sci. 2009;4:50.
5. Powell BJ, Waltz TJ, Chinman MJ, et al. A refined compilation of implementation strategies: results from the Expert Recommendations for Implementing Change (ERIC) project. Implement Sci. 2015;10:21.
6. Creswell JW, Plano Clark VL. Designing and Conducting Mixed Methods Research. 3rd ed. Sage; 2017.
