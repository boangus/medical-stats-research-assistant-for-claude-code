# 统计方法统一注册表 (Method Registry)

> **版本**: v1.0.1 | **创建日期**: 2026-06-24 | **维护者**: MSRA Team
> **定位**: 统计方法引用的**唯一权威索引**，各处引用指向本文件。

---

## 设计意图

MSRA 中统计方法引用此前分散在三处：

| 来源 | 内容 | 定位 |
|------|------|------|
| `shared/statistics-methods/chapters/` (56章) | 方法学深度指南 | **权威参考**（深入学习） |
| `skills/stat-method-selector/decision-tree.json` (112方法) | 方法选择决策树 | **规范选择源**（选哪个方法） |
| `shared/statistics-methods/method_selector_mapping.md` | 方法→实现映射 | **实现指引**（怎么写代码） |

本文件作为**统一入口**，提供按场景的快速查找路径，避免在三处之间迷失。

---

## 快速查找矩阵

### 按研究目标查找

| 研究目标 | 决策树节点 | 推荐方法 | 详细章节 | 映射表条目 |
|---------|-----------|---------|---------|-----------|
| **组间比较** | goal_compare | t检验/ANOVA/非参数 | ch42 | method_selector_mapping §一 |
| **关联分析** | goal_associate | 相关/回归 | ch15, ch16 | method_selector_mapping §三 |
| **预测模型** | goal_predict | Logistic/Cox/ML | ch15, ch48 | method_selector_mapping §四 |
| **因果推断** | goal_causal | PSM/IPTW/DAG/TMLE | ch35, ch44, ch53 | method_selector_mapping §五 |
| **生存分析** | goal_survival | KM/Cox/竞争风险 | ch10 | method_selector_mapping §六 |
| **诊断试验** | goal_diagnostic | ROC/AUC/敏感性特异性/时间依赖ROC | ch36, ch39, ch54 | method_selector_mapping §七 |
| **Meta分析** | goal_meta | 固定/随机效应/网络 | ch26, ch37, ch46 | method_selector_mapping §八 |
| **贝叶斯** | goal_bayesian | 先验/后验/MCMC | ch22, ch38 | method_selector_mapping §九 |
| **等价性/非劣效** | goal_equivalence | TOST/非劣效检验 | ch01, ch49 | method_selector_mapping §十 |
| **聚类/降维** | goal_cluster | K-means/层次聚类/PCA | ch50 | method_selector_mapping §十一 |
| **纵向进阶** | goal_longitudinal | 边际/条件模型/轨迹分析 | ch43, ch51 | method_selector_mapping §十二 |
| **治疗效应异质性** | goal_hte | 因果森林/Meta-learners | ch52 | method_selector_mapping §十三 |
| **实施科学** | goal_implementation | 混合方法/DID/ITS | ch24, ch56 | method_selector_mapping §十四 |

### 按研究类型查找

| 研究类型 | 主要分析方法 | 敏感性分析 | 相关章节 |
|---------|------------|-----------|---------|
| **RCT** | ANCOVA/混合模型/ITT | 偏离ITT/PP分析/期中分析 | ch13, ch14, ch21 |
| **队列研究** | Cox回归/KM曲线/PSM | E-value/负对照结局 | ch10, ch28, ch35 |
| **病例对照** | 条件Logistic回归 | 分层分析/敏感性分析 | ch15, ch25 |
| **横断面** | 卡方检验/Logistic回归 | 多重插补 | ch15, ch20 |
| **诊断试验** | ROC/AUC/似然比 | 不同切点分析 | ch36, ch39 |
| **系统评价** | Meta分析/异质性检验 | 亚组分析/Meta回归 | ch26, ch37 |

### 按数据特征查找

| 数据特征 | 适用方法 | 章节 |
|---------|---------|------|
| 连续正态 | t检验/ANOVA/线性回归 | ch42 |
| 连续非正态 | 非参数检验/Bootstrap | ch42 |
| 二分类 | 卡方/Fisher/Logistic回归 | ch15 |
| 计数/率 | Poisson回归/负二项回归 | — |
| 生存时间 | KM/Cox/竞争风险 | ch10 |
| 纵向/重复测量 | GEE/MMRM/混合效应模型/边际vs条件 | ch14, ch43, ch51 |
| 高维/多变量 | PCA/正则化/ML | ch47, ch48 |
| 等价性检验 | TOST（双单侧检验） | ch49 |
| 聚类分析 | K-means/层次聚类/DBSCAN | ch50 |
| 治疗效应异质性 | 因果森林/S/T/X-learner | ch52 |
| 双重稳健估计 | TMLE/AIPW | ch53 |
| 时间依赖ROC | ROC(t)/AUC(t)/整合Brier | ch54 |
| 自适应设计 | 适应性随机化/贝叶斯自适应 | ch55 |
| 实施科学 | RE-AIM/CFIR/混合方法 | ch56 |

---

## 引用规范

### 在 SKILL.md 中引用

```markdown
<!-- 引用决策树 -->
参见 `skills/stat-method-selector/decision-tree.json` → goal → compare → continuous → parametric

<!-- 引用深度指南 -->
详见 `shared/statistics-methods/chapters/ch14-mixed-models-for-repeated-measures.md`

<!-- 引用实现映射 -->
代码实现见 `shared/statistics-methods/method_selector_mapping.md` §一 连续结局—参数方法
```

### 在代码模板中引用

```python
# 方法选择依据: decision-tree.json → goal_compare → continuous → parametric → ANCOVA
# 参考文献: Mishra(22-4) + Sungur
# 深度指南: shared/statistics-methods/chapters/ch33-covariate-adjustment.md
```

---

## 交叉引用索引

### 48章指南 → 决策树节点

| 章节 | 决策树节点 | 方法数 |
|------|-----------|--------|
| ch01-09 研究设计 | goal_survival / goal_causal | — |
| ch10 生存分析 | goal_survival | 6 |
| ch14 MMRM | goal_compare → longitudinal | 2 |
| ch15 Logistic | goal_associate / goal_predict | 4 |
| ch22 贝叶斯 | goal_bayesian | 3 |
| ch26 Meta | goal_meta | 5 |
| ch35 倾向性评分 | goal_causal | 4 |
| ch42 非参数 | goal_compare → nonparametric | 12 |
| ch43 GEE | goal_compare → longitudinal | 2 |
| ch46 网络Meta | goal_meta → network | 2 |
| ch47 ML公平性 | goal_predict → fairness | 3 |
| ch48 生存ML | goal_survival → ml | 4 |
| ch49 等价性检验 | goal_equivalence → equivalence | 3 |
| ch50 聚类分析 | goal_cluster → unsupervised | 5 |
| ch51 纵向进阶 | goal_longitudinal → advanced | 4 |
| ch52 HTE | goal_hte → causal_forest | 4 |
| ch53 TMLE/AIPW | goal_causal → doubly_robust | 3 |
| ch54 ROC进阶 | goal_diagnostic → time_dependent | 4 |
| ch55 自适应设计 | goal_survival → adaptive | 5 |
| ch56 实施科学 | goal_implementation → mixed_methods | 4 |

### 决策树112方法 → 映射表覆盖

映射表 `method_selector_mapping.md` 覆盖全部112个方法叶子节点，每个方法提供：
- MSRA 深度指南章节（如有）
- R 实现代码片段
- Python 实现代码片段
- 文献依据引用

---

## 维护规则

1. **新增方法时**: 同时更新本文件 + `method_selector_mapping.md` + 对应章节（如需深度指南）
2. **决策树更新时**: 同步更新 `method_selector_mapping.md` 的方法条目
3. **引用规范**: 所有 SKILL.md 和代码模板中的方法引用**必须指向本文件或其子文件**，禁止散落引用
