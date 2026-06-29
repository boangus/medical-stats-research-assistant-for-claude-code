# 临床预测中的机器学习公平性 (ML Fairness in Clinical Prediction)

> 版本: 1.0 | 2026-06-13
> MSRA 关联: `analysis-plan` Phase 3 方法选择, `analysis-exec` Phase 7 模型验证, `report` Phase 9 结果报告

---

## 概述

随着机器学习 (ML) 在临床决策支持系统中的广泛应用，模型对不同人群亚组（如种族、性别、年龄、社会经济状态）的预测差异引发了深刻的伦理和监管关注。**公平性 (Fairness)** 确保 ML 模型不会系统性地对特定群体产生不利影响。

### 为什么临床 ML 需要关注公平性？

| 维度 | 说明 |
|------|------|
| **临床后果** | 不公平模型可能导致少数族裔患者被低估疾病风险，延误诊断或治疗 |
| **监管要求** | FDA AI/ML 框架（2021）要求透明性、鲁棒性、公平性；EU AI Act（2024）将医疗 AI 归类为"高风险"，要求公平性评估 |
| **法律风险** | 算法歧视可能违反民权法和反歧视法规 |
| **科学诚信** | 在偏倚数据上训练的模型结论不可靠，影响可重复性 |

---

## 一、公平性指标体系

### 1.1 核心公平性指标

设 $R$ 为受保护属性（如种族），$\hat{Y}$ 为模型预测，$Y$ 为真实结局。

| 指标 | 定义 | 数学表达 | 适用场景 |
|------|------|---------|---------|
| **人口统计均等 (Demographic Parity)** | 各亚组的阳性预测率相同 | $P(\hat{Y}=1\|R=A) = P(\hat{Y}=1\|R=B)$ | 资源分配公平 |
| **机会均等 (Equalized Odds)** | 各亚组的 TPR 和 FPR 相同 | $P(\hat{Y}=1\|Y=y, R=A) = P(\hat{Y}=1\|Y=y, R=B)$ | 诊断公平 |
| **预测均等 (Predictive Parity)** | 各亚组的 PPV 相同 | $P(Y=1\|\hat{Y}=1, R=A) = P(Y=1\|\hat{Y}=1, R=B)$ | 预测可信度公平 |
| **校准均等 (Calibration Parity)** | 各亚组的校准度相同 | $P(Y=1\|\hat{p}=s, R=A) = P(Y=1\|\hat{p}=s, R=B)$ | 风险分层公平 |

### 1.2 指标间的权衡

**不可兼容定理** (Chouldechova, 2017; Kleinberg et al., 2016): 当基础率 (base rate) 在各亚组间不同时，人口统计均等、机会均等和预测均等**不可能同时满足**。

> **实践建议**: 在临床场景中，**校准均等**通常是最重要且最可解释的指标 — 确保模型预测的 80% 风险在所有亚组中确实对应约 80% 的事件发生率。

---

## 二、偏倚来源

### 2.1 偏倚类型分类

| 偏倚类型 | 描述 | 临床示例 |
|---------|------|---------|
| **历史偏倚 (Historical Bias)** | 训练数据反映既往不平等的医疗实践 | 黑人患者疼痛评分被低估的历史数据 |
| **测量偏倚 (Measurement Bias)** | 不同亚组的数据采集方式不同 | 贫困社区的实验室检查频率低于富裕社区 |
| **选择偏倚 (Selection Bias)** | 训练数据未代表目标人群 | 电子病历数据来自教学医院，老年患者占比不足 |
| **表示偏倚 (Representation Bias)** | 某些亚组在数据中被欠表示 | 罕见病患者中少数族裔样本过少 |
| **聚合偏倚 (Aggregation Bias)** | 用单一模型处理本质不同的群体 | 用同一模型预测不同种族的心血管风险 |

### 2.2 偏倚传导链

```
社会不平等 → 医疗数据偏倚 → 模型学习偏倚模式 → 部署后不公平预测 → 加剧不平等
```

---

## 三、偏倚缓解策略

### 3.1 预处理方法 (Pre-processing)

在模型训练前修正数据。

**重新加权 (Reweighing)**: 对不同亚组-结局组合赋予不同权重，消除训练数据中受保护属性与结局的关联。

$$w_{ij} = \frac{P(\hat{Y}=j) \cdot P(R=i)}{P(\hat{Y}=j, R=i)}$$

```r
library(fairmodels)

# 创建公平性检查对象
fobject <- fairness_check(
  explainer, protected = df$race,
  privileged = "White", cutoff = 0.5
)

# 可视化公平性指标
plot(fobject)
```

### 3.2 过程中方法 (In-processing)

在模型训练过程中直接施加公平性约束。

**约束优化**: 在损失函数中加入公平性惩罚项:

$$\min_\theta \mathcal{L}(\theta) + \lambda \cdot \mathcal{C}(\theta)$$

其中 $\mathcal{C}(\theta)$ 为公平性约束（如各亚组 FPR 差异），$\lambda$ 控制公平性-准确度权衡。

### 3.3 后处理方法 (Post-processing)

在模型预测后调整决策阈值。

**阈值调整**: 为不同亚组设定不同的分类阈值，以满足特定公平性约束:

$$\hat{Y}_i = \begin{cases} 1 & \text{if } \hat{p}_i > t_{R_i} \\ 0 & \text{otherwise} \end{cases}$$

| 方法 | 描述 | 优缺点 |
|------|------|--------|
| 预处理 - 重新加权 | 调整样本权重 | 简单，但可能损失效率 |
| 预处理 - 过采样/欠采样 | 平衡亚组样本量 | 可能丢失信息 |
| 过程中 - 对抗去偏 | 训练对抗网络去除受保护属性信息 | 效果好，但复杂 |
| 过程中 - 约束优化 | 在损失函数中加入公平性约束 | 灵活，但调参困难 |
| 后处理 - 阈值调整 | 为不同亚组设定不同阈值 | 简单，但需要已知亚组标签 |

---

## 四、公平性感知模型评估

### 4.1 评估流程

1. **识别受保护属性**: 种族、性别、年龄、保险类型、邮政编码（社会经济状态代理）
2. **计算各亚组性能指标**: AUC、灵敏度、特异度、PPV、NPV、校准度
3. **计算公平性指标**: 选择与研究目标一致的公平性指标
4. **敏感性分析**: 尝试不同阈值和公平性约束

### 4.2 分层评估报告表

| 指标 | 总体 | 白人 | 黑人 | 西班牙裔 | 亚裔 |
|------|------|------|------|---------|------|
| AUC | {值} | {值} | {值} | {值} | {值} |
| 灵敏度 | {值} | {值} | {值} | {值} | {值} |
| 特异度 | {值} | {值} | {值} | {值} | {值} |
| PPV | {值} | {值} | {值} | {值} | {值} |
| 校准斜率 | {值} | {值} | {值} | {值} | {值} |
| Demographic Parity Diff | — | 参照 | {值} | {值} | {值} |
| Equalized Odds Diff | — | 参照 | {值} | {值} | {值} |

---

## 五、R 实现

### 5.1 fairness 包

```r
library(fairness)

# 二分类公平性评估
fairness_result <- fairness(
  object = glm_model,
  protected = df$race,
  privileged = "White",
  cutoff = 0.5
)

# 查看各项公平性指标
print(fairness_result)

# 可视化
plot(fairness_result)
```

### 5.2 fairmodels 包 (DALEX 生态)

```r
library(DALEX)
library(fairmodels)

# 创建 DALEX 解释器
explainer <- DALEX::explain(
  model = glm_model,
  data = X_test, y = y_test,
  label = "Logistic Regression"
)

# 公平性检查
fobject <- fairness_check(
  explainer,
  protected = X_test$race,
  privileged = "White"
)

# 公平性指标雷达图
plot(fobject, type = "radar")

# 不同阈值下的公平性
plot(fobject, type = "heatmap")

# 偏倚缓解 - 重新加权
fobject_reweight <- fairness_check(
  explainer,
  protected = X_test$race,
  privileged = "White",
  weights = reweight_weights  # 预计算的权重
)
```

### 5.3 性能与公平性权衡可视化

```r
# 性能-公平性 Pareto 前沿
plot(fobject, type = "performance_and_fairness")

# 亚组 ROC 曲线比较
plot(fobject, type = "roc", subgroups = TRUE)
```

---

## 六、报告模板

> 本研究评估了 {模型类型} 预测 {临床结局} 的公平性。受保护属性为 {种族/性别/年龄}。训练数据来源于 {数据来源}，共 {N} 例，其中 {受保护群体} 占 {比例}%。采用 {fairness/fairmodels} 包进行公平性评估。公平性指标包括人口统计均等差异 (DPD)、机会均等差异 (EOD) 和校准均等。各亚组 AUC 范围: {最小}-{最大}；最大 EOD 为 {值}，超出 {阈值} 阈值。偏倚缓解策略: {方法}，缓解后 EOD 改善至 {值}。公平性评估遵循 {FDA AI/ML 框架 / EU AI Act} 要求。分析使用 R {版本}。

---

## 七、常见陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| 仅报告总体指标 | 总体 AUC 高但亚组差异大 | 强制报告分层性能表 |
| 忽略交集公平性 | 仅看单一受保护属性 | 考虑种族 x 性别 x 年龄的交集 |
| 后处理阈值调整需要亚组标签 | 部署时可能无法获取亚组信息 | 优先使用预处理或过程中方法 |
| 公平性-准确度假设冲突 | 过度追求公平性可能降低整体性能 | 使用 Pareto 前沿展示权衡 |
| 基础率差异被忽略 | 不同亚组的疾病基础率不同 | 区分不公平与真实流行病学差异 |
| 代理变量偏倚 | 移除种族变量不等于消除偏倚（邮编、姓名可代理） | 检查代理变量相关性 |

---

## 八、参考资源

- **核心文献**: Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting racial bias in an algorithm used to manage the health of populations. *Science*, 2019, 366(6464): 447-453.
- **不可兼容定理**: Chouldechova A. Fair prediction with disparate impact. *Big Data*, 2017, 5(2): 153-163.
- **FDA 框架**: FDA. Artificial Intelligence/Machine Learning (AI/ML)-Based Software as a Medical Device (SaMD) Action Plan, 2021.
- **EU AI Act**: European Parliament. Regulation (EU) 2024/1689 (Artificial Intelligence Act), 2024.
- **R 包**: `fairness` (公平性指标), `fairmodels` (DALEX 生态公平性工具), `DALEX` (模型解释)
- **综述**: Rajkomar A, Hardt M, Howell MD, et al. Ensuring fairness in machine learning to advance health equity. *Ann Intern Med*, 2018, 169(12): 866-872.
- **MSRA 模板**: `src/shared/templates/fairness_evaluation_template.R`
