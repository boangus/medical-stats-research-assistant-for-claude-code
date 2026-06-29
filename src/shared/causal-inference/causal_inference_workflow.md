# 因果推断工作流

> 基于 DAG 的混杂识别和 PSM 工作流
> 版本: 0.1.0 | 2026-05-29

---

## 概述

因果推断在观察性研究中至关重要。本模块提供两条互补的因果推断路径：

1. **DAG 路径**: 通过有向无环图(DAG)识别混杂因素、选择最小充分调整集
2. **PSM 路径**: 通过倾向性评分匹配模拟随机化，估计处理效应

两者可在完整分析中串联使用：DAG → 识别混杂 → PSM/回归调整

---

## 一、DAG 因果推断工作流

### 1.1 定义研究问题

| 要素 | 示例 |
|------|------|
| 暴露 (E) | 吸烟（是/否） |
| 结局 (O) | 肺癌（是/否） |
| 目标估计 | 吸烟对肺癌的风险比 (RR/OR/HR) |
| 目标人群 | 50-70 岁男性 |

### 1.2 DAG 构建原则

```
     ┌─────┐     ┌──────┐
     │  U  │────→│  C   │ (混杂)
     └──┬──┘     └──┬───┘
        │           │
        ▼           ▼
     ┌─────┐     ┌──────┐
     │  E  │────→│  O   │ (暴露→结局)
     └─────┘     └──────┘
```

**三类节点**:
- **暴露 (E)**: 研究中关注的干预/风险因素
- **结局 (O)**: 研究的终点
- **协变量 (C/U)**: 可能影响 E 和/或 O 的变量

### 1.3 混杂识别规则

| 图形模式 | 是否混杂 | 处理 |
|----------|---------|------|
| C → E, C → O (共同原因) | ✅ 是 | 需调整 C |
| E → M → O (中介) | ❌ 不是 | 不调整 M（过度调整） |
| E ← C → O (对撞) | ❌ 不是 | 不调整 C（除非打开路径） |

### 1.4 最小充分调整集

使用 **后门准则 (Back-door Criterion)**:
- 调整集需阻断 E 和 O 之间的所有后门路径
- 不调整任何中介变量
- 选择最小集以减少方差

### 1.5 偏倚评估

| 偏倚类型 | 原因 | 处理方法 |
|----------|------|---------|
| 混杂偏倚 (Confounding) | 共同原因未调整 | DAG 识别 + 调整 |
| 选择偏倚 (Selection) | 对撞偏倚 | 避免条件于对撞变量 |
| 信息偏倚 (Information) | 测量误差 | 敏感性分析 |
| 中介偏倚 (Mediation) | 过度调整中介 | 不调整中介变量 |

---

## 二、倾向性评分工作流 (PSM)

### 2.1 倾向性评分估计

```r
# R: 使用 logistic 回归估计倾向性评分
ps_model <- glm(treatment ~ age + sex + bmi + comorbidity,
                data = data, family = binomial)
data$ps_score <- predict(ps_model, type = "response")
```

```python
# Python: 使用 sklearn 估计倾向性评分
from sklearn.linear_model import LogisticRegression
ps_model = LogisticRegression()
ps_model.fit(X_covariates, y_treatment)
ps_scores = ps_model.predict_proba(X_covariates)[:, 1]
```

### 2.2 匹配方法

| 方法 | 描述 | 适用场景 |
|------|------|---------|
| 最近邻匹配 (NNM) | 每个处理组个体匹配一个倾向性评分最近的对照 | 对照充足时 |
| 卡钳匹配 (Caliper) | 设定卡钳值（如 0.2×SD(logit PS)) | 控制匹配质量 |
| 最优匹配 (Optimal) | 全局最小化匹配距离总和 | 样本量中等 |
| 分层匹配 (Stratification) | 按 PS 分 5 层分析 | 处理组/对照组比例均衡 |
| 逆概率加权 (IPTW) | 用 PS 的倒数加权 | 不丢弃样本 |

### 2.3 匹配后平衡诊断

**标准: 标准化差异 (Standardized Mean Difference, SMD) < 0.1**

```r
# R 平衡诊断
library(cobalt)
bal.tab(ps_model, data = data, 
        treatment = "treatment",
        distance = "ps_score")
```

**平衡检查表**:

| 检查项 | 标准 | 处理 |
|--------|------|------|
| SMD < 0.1 | ✅ 通过 | 可接受 |
| SMD 0.1-0.2 | ⚠️ 轻度不平衡 | 尝试卡钳匹配/其他方法 |
| SMD > 0.2 | ❌ 不平衡 | 重新指定 PS 模型或使用其他方法 |
| 方差比 0.5-2.0 | ✅ 通过 | 可接受 |

### 2.4 处理效应估计

```r
# R: 匹配后分析（配对 t 检验或条件 Logistic）
library(MatchIt)
m.out <- matchit(treatment ~ age + sex + bmi,
                 data = data, method = "nearest")
m.data <- match.data(m.out)

# 治疗效果
library(survey)
svyglm(outcome ~ treatment, 
       design = svydesign(ids = ~1, 
                          weights = ~weights, 
                          data = m.data),
       family = binomial)
```

---

## 三、完整工作流示例

### 3.1 研究问题
> 某降压药是否降低心血管事件风险？使用回顾性队列数据。

### 3.2 步骤

```
Step 1: DAG 构建
    ├── 暴露: 降压药使用 (E)
    ├── 结局: 心血管事件 (O)
    ├── 混杂: 年龄、性别、BMI、吸烟、糖尿病
    ├── 不调整: 血压（中介变量）
    └── 调整集: {年龄, 性别, BMI, 吸烟, 糖尿病}

Step 2: 倾向性评分估计
    ├── 模型: treatment ~ age + sex + bmi + smoking + diabetes
    └── 检查: c-statistic > 0.7 表示区分度可接受

Step 3: 匹配
    ├── 方法: 最近邻 + 卡钳(0.2 SD)
    ├── 比例: 1:1
    └── 检查: 匹配后 SMD < 0.1

Step 4: 效应估计
    ├── 主要: Cox 回归 (HR)
    ├── 敏感性: IPTW + 双重稳健估计
    └── 报告: HR (95% CI), p-value

Step 5: 敏感性分析
    ├── E-value 分析（需多大未测量混杂才能推翻结果）
    └── 阴性对照分析
```

### 3.3 E-value 计算

```r
# R: E-value 计算
# 当观察到 RR=1.5，需要多大的未测量混杂才能推翻结果？
# E-value 公式: RR_obs + sqrt(RR_obs * (RR_obs - 1))
e_value <- function(RR_obs) {
  RR_obs + sqrt(RR_obs * (RR_obs - 1))
}
```

```python
# Python: E-value
import numpy as np
def e_value(RR_obs):
    """计算 E-value"""
    return RR_obs + np.sqrt(RR_obs * (RR_obs - 1))
```

### 3.3.5 阴性对照分析（Negative Control Outcomes, NCO）🆕

> **与 E-value 的互补关系**（参考: resources/statistics-methods/chapters/ch28-e-value.md）：
> - **E-value**（敏感性分析）：量化"需要多大未测量混杂才能推翻结果" — 回答"**如果**有混杂会怎样"
> - **NCO**（证伪检验）：检测"未测量混杂**实际是否存在**" — 回答"**有没有**混杂迹象"
> - 两者互补：E-value 给出鲁棒性边界，NCO 提供混杂存在的经验证据。**观察性因果推断两者都应报告**。
> 借鉴 Shi X, et al. Multivariate Behav Res 2025 (Taylor & Francis)、DANCE 自动化方法 (JMLR 2024)、COCA 框架 (AJE 2014)。

**NCO 的核心逻辑**：

```
阴性对照结局 (NCO) = 一个理论上不应被暴露影响、但受相同混杂结构影响的结局
                     │
                     ├── 若 NCO 与暴露无显著关联 → ✅ 无明显未测量混杂（结果可信）
                     ├── 若 NCO 与暴露显著关联 → ❌ 检测到未测量混杂（主结果存疑）
                     │
                     └── 数学基础: 混杂桥函数 (confounding bridge function)
                         使 NCO 关联反映纯混杂效应，可校正主估计
```

**NCO 选择标准**（必须同时满足）：

| 标准 | 要求 | 示例（暴露=他汀类用药） |
|------|------|----------------------|
| **无因果效应** | 暴露对 NCO 在生物学/时间上不应有因果影响 | 意外伤害死亡率（他汀不影响） |
| **共享混杂** | NCO 受与主结局相同的混杂因素影响 | 高龄/合并症影响意外伤害和心血管事件 |
| **可测量** | NCO 在数据中可获得且足够事件数 | 队列中意外伤害死亡 ≥10 例 |

**双阴性对照设计（Double NCO，2024-2025 推荐）**：

```
主结局（受因果+混杂影响）:    暴露 → 主结局估计 = 因果效应 + 混杂偏倚
NCO 结局（仅受混杂影响）:     暴露 → NCO 估计   =           混杂偏倚
                                       ↓
                         校正后估计 = 主估计 − NCO 估计（去除混杂偏倚）

阴性对照暴露（NCE，可选交叉验证）:
                         NCE（无因果）→ 主结局估计 =           混杂偏倚
                         交叉验证 NCO vs NCE 的混杂偏倚估计一致性
```

**实施步骤**：

```python
# Python: 阴性对照分析（无需额外依赖，statsmodels 即可）
import statsmodels.api as sm
import numpy as np

def negative_control_test(df, exposure, nco_outcome, covariates):
    """
    阴性对照结局证伪检验。
    返回: NCO 估计值、置信区间、p 值、混杂判定。
    """
    X = df[[exposure] + covariates]
    X = sm.add_constant(X)
    model = sm.Logit(df[nco_outcome], X).fit(disp=0)
    
    est = model.params[exposure]
    ci = model.conf_int().loc[exposure]
    p = model.pvalues[exposure]
    
    # 判定: NCO 不应有显著效应
    verdict = (
        "❌ 检测到未测量混杂（NCO 显著）— 主结果存疑"
        if p < 0.05 else
        "✅ 无明显未测量混杂（NCO 不显著）— 结果可信"
    )
    return {"estimate": est, "ci_low": ci[0], "ci_high": ci[1], "p": p, "verdict": verdict}

def coca_correction(main_est, nco_est):
    """
    COCA 校正 (Control Outcome Calibration Approach):
    用 NCO 估计校正主估计的混杂偏倚。
    校正后估计 = 主估计 − NCO 估计
    """
    return main_est - nco_est
```

**NCO 分析决策树**：

```
主因果估计 (暴露→主结局) 显著？
├── 否 → 排除因果效应，NCO 不必要（阴性结果可能源于效力不足，需评估 power）
└── 是 → 必须运行 NCO 证伪检验
         │
         ├── NCO 不显著 (p≥0.05) → ✅ 结果可信，报告 "通过阴性对照证伪检验"
         │                        报告 E-value 作为补充鲁棒性证据
         │
         ├── NCO 显著 (p<0.05) → ❌ 检测到未测量混杂
         │   ├── 尝试 COCA 校正 → 校正后仍显著？→ 报告校正后结果 + 局限性
         │   └── 校正后不显著   → 报告"混杂偏倚可能解释全部效应"，结论降级
         │
         └── 无合适 NCO 可选 → 明确声明"无法证伪未测量混杂"，仅报告 E-value
```

**NCO 选择禁忌**（参考: resources/anti-patterns/medical_stats_anti_patterns.md）：

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 选择受暴露影响的结局作 NCO | 违反"无因果效应"假设，NCO 失效 | 验证生物学合理性：暴露对 NCO 无作用机制 |
| 2 | NCO 事件数 <10 就下结论 | 小样本 NCO 检验效力不足，假阴性高 | 标注"NCO 效力不足"，不作为通过证据 |
| 3 | NCO 显著但忽略不报告 | 选择性报告，掩盖混杂证据 | NCO 结果必须如实报告，无论显著与否 |
| 4 | 用单一 NCO 就下"无混杂"结论 | 单一 NCO 可能碰巧不显著 | 推荐双 NCO（不同机制）交叉验证 |
| 5 | 将 COCA 校正当因果估计 | 校正仍有假设（混杂桥函数可交换性） | 报告为"混杂校正后估计"，注明假设 |

### 3.4 报告模版

```
# 因果推断结果报告

## 方法
采用倾向性评分匹配（1:1最近邻匹配，卡钳值0.2×SD(logit PS)）
控制以下混杂因素：{列表}
匹配后通过标准化差异评估平衡（阈值<0.1）

## 结果
- 匹配前: {N_treated} vs {N_control}
- 匹配后: {N_matched} 配对
- 处理效应: {HR/OR/RR} = {value} (95% CI: {lower}, {upper}, p = {p})
- E-value: {e_value}（意味着需要 E-value 以上的未测量混杂才能推翻结论）

## 敏感性分析
- IPTW 分析结果一致
- E-value 敏感性分析支持结论稳健性
```

---

## 四、方法选择决策树扩展

### 4.1 何时用 PSM vs 回归调整

| 场景 | 推荐方法 | 理由 |
|------|---------|------|
| 少量混杂因素 (≤5个) | 多变量回归 | 简单直接，无需匹配损失 |
| 大量混杂因素 | PSM/IPTW | 维度诅咒，匹配更稳健 |
| 罕见结局 (≤10%) | PSM | Logistic 回归的 OR 在高事件率时与 RR 偏离 |
| 罕见暴露 | PSM | 需最大化利用对照 |
| 非线性暴露-协变量关系 | GAM/IPTW | 匹配不依赖线性假设 |
| 随时间变化的暴露 | MSM (边际结构模型) | 标准 PSM 不适用于时变暴露 |

### 4.2 推荐分析路径

```
观察性数据分析
    │
    ├── 有 DAG? ──> Yes ──> 基于 DAG 选择调整集
    │                       ├── 调整集小 → 回归调整
    │                       └── 调整集大 → PSM/IPTW
    │
    └── 无 DAG? ──> 构建 DAG
                     ├── 基于文献
                     ├── 基于专家知识
                     └── 基于 DAGitty/ggdag
```

---

## 五、参考资源

- **书籍**: Hernán & Robins. *Causal Inference: What If* (2020)
- **R 包**: `MatchIt`, `cobalt`, `twang`, `CBPS`, `WeightIt`
- **Python**: `causalinference`, `DoWhy`, `EconML`
- **在线工具**: [DAGitty](https://www.dagitty.net/) — 在线 DAG 构建和调整集识别
- **文献**: VanderWeele & Ding (2017). *Sensitivity Analysis in Observational Research* (E-value)

---

## 六、完整因果推断链路: DAG → 识别 → 估计 → 敏感性

### 6.1 标准化工作流

```
Step 1: 构建 DAG
    ├── 基于文献/专家知识确定因果结构
    ├── 识别暴露(E)→结局(O)的所有路径
    └── 工具: DAGitty / ggdag / dagR

Step 2: 识别策略 (Identification)
    ├── 后门准则 → 选择最小充分调整集
    ├── 前门准则 → 当存在中介变量时
    ├── 工具变量法 → 当存在有效IV时
    └── 输出: 调整集 S = {变量列表}

Step 3: 估计 (Estimation)
    ├── 调整集小(≤5) → 多变量回归
    ├── 调整集大 → PSM / IPTW / OW
    ├── 时变暴露 → 边际结构模型(MSM)
    ├── 存在工具变量 → 2SLS / IV-GMM
    └── 输出: 效应估计 + 95% CI

Step 4: 敏感性分析 (Sensitivity)
    ├── E-value → 未测量混杂的最小强度
    ├── Rosenbaum 界 → 匹配分析的敏感性
    ├── 阴性对照 → 排除残余混杂
    └── 输出: 结论稳健性评估
```

### 6.2 识别策略选择

| 条件 | 策略 | 适用方法 |
|------|------|---------|
| 存在后门路径 | 后门准则 | 回归调整 / PSM / IPTW |
| 存在未测量混杂但有IV | 工具变量法 | 2SLS / IV-GMM |
| 存在中介且无混杂 | 前门准则 | 中介分析 |
| 存在未测量混杂且无IV | 敏感性分析 | E-value / 负对照 |

### 6.3 多重稳健估计 (Doubly Robust)

当担心模型误设时，使用 **AIPW (Augmented Inverse Probability Weighting)**:
- 只需倾向性评分模型或结果模型**之一**正确即可得到一致估计
- 结合了 IPTW 和回归调整的优势

```r
# R: 使用 WeightIt 进行 AIPW
library(WeightIt)
w <- weightit(treatment ~ age + sex + bmi, data = df, method = "ps")
library(survey)
svyglm(outcome ~ treatment, design = svydesign(~1, weights = w$weights, data = df))
```

```python
# Python: 使用 DoWhy
from dowhy import CausalModel
model = CausalModel(data=df, treatment='treatment', outcome='outcome', graph=dot_graph)
estimate = model.estimate_effect(identified_estimand, method_name="backdoor.econml.dml.DML")
```

---

## 七、MSRA 可用模板

| 模板 | 用途 | 文件 |
|------|------|------|
| PSM 模板 (Python) | 倾向性评分匹配全流程 | `psm_template.py` |
| Overlapping Weighting 模板 (Python) | OW 加权因果效应估计，含 IPTW 对比和权重分布可视化 | `overlapping_weighting_template.py` |
| DoWhy 因果推断模板 (Python) | 基于 DoWhy/EconML 的完整因果推断工作流，含反驳检验和 E-value | `causal_inference_dowhy.py` |
| **PS 诊断图模板 (R)** ⭐ **新增** | **Love plot、权重分布图、PS 重叠图、平衡表** | `src/shared/templates/ps_diagnostics_template.R` |

### 新增模板使用推荐

**场景 A: 标准 PSM 分析**
→ 使用 `psm_template.py`
- 适用于：经典的倾向性评分匹配 + 平衡诊断 + Love Plot
- 优势：轻量级，仅依赖 sklearn/scipy

**场景 B: Overlapping Weighting (OW) 分析**
→ 使用 `overlapping_weighting_template.py`
- 适用于：需要自动截断极端权重、减少方差膨胀的因果推断
- 优势：比 IPTW 更稳健，自动处理 PS 接近 0 或 1 的个体
- 依赖: numpy, pandas, sklearn, matplotlib, statsmodels
- 参考: Li et al. (2018) Statistics in Medicine

**场景 C: 完整因果推断 (含敏感性分析)**
→ 使用 `causal_inference_dowhy.py` (推荐)
- 适用于：需要因果图识别、反驳检验、E-value 的正式分析
- 优势：基于 DoWhy 框架，因果推断方法学更严谨
- 依赖: `pip install dowhy`

**场景 D: 异质性处理效应 (CATE)**
→ 使用 `causal_inference_dowhy.py` 中的 `estimate_cate_econml()`
- 适用于："谁受益最大/最小？" 的问题
- 优势：Causal Forest / DML 方法估计条件平均处理效应
- 依赖: `pip install econml`

**场景 E: OW vs IPTW 对比分析**
→ 使用 `overlapping_weighting_template.py` 中的 `compare_ow_iptw()`
- 适用于：需要比较不同加权方法结论一致性的敏感性分析
- 优势：一键生成 OW 和 IPTW 的平衡诊断和效应估计对比

---

## S8 dagitty 整合：DAG 引导的变量筛选

### S8.1 dagitty 简介

dagitty 是一个用于创建和分析因果 DAG 的 R 包，支持：
- 自动计算最小充分调整集（后门准则/前门准则）
- 识别有效 IV（工具变量）
- 检测因果效应是否可识别
- 可视化因果图

### S8.2 与 CIE 的整合流程

```
1. dag_build()         → 构建因果 DAG（暴露→结局，含混杂/中介/对撞）
2. dag_adjustment_set() → dagitty 自动计算调整集
3. dag_cie_screen()    → 用 CIE 验证 DAG 识别的混杂因素
4. dag_full_workflow() → 完整流程一键执行
```

### S8.3 关键代码

```r
library(dagitty)
library(ggdag)

# 构建 DAG
dag <- dagitty("dag {
  age -> treatment
  age -> cv_event
  bmi -> treatment
  bmi -> cv_event
  smoking -> treatment
  smoking -> cv_event
  treatment -> sbp_reduction
  sbp_reduction -> cv_event
  treatment -> cv_event
}")
exposures(dag) <- "treatment"
outcomes(dag) <- "cv_event"

# 计算调整集
adjustmentSets(dag, type = "canonical")
# 结果: {age, bmi, smoking}

# 可视化
ggdag(dag) + theme_dag()
```

### S8.4 模板文件

- **R 模板**: `src/shared/templates/dag_variable_selection_template.R`
- **Python DAG**: `src/shared/templates/variable_dag_template.py`（变量构造依赖 DAG）
- **Python 因果**: `src/shared/causal-inference/causal_inference_dowhy.py`（DoWhy 因果推断）



