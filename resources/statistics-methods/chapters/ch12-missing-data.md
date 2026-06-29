# 缺失数据：如何最好地解释未知

**作者**: Craig D. Newgard, Roger J. Lewis | **主译**: 龙宇琴

---

本章描述了在临床研究中对缺失数据建模的不同方法的优势和局限性。

## 缺失数据机制

数据缺失有 3 种方式：

### 1. 完全随机缺失（MCAR）
缺失的概率与所有观察和未观察的患者特征完全无关。这是最不可能的机制，但只有这个机制下完整病例分析可以获得无偏倚结果。

### 2. 随机缺失（MAR）
观察到的值可以用来"解释"哪些值缺失，并帮助预测缺失的值会是什么。这是比 MCAR 更现实的假设，目前大多数有效的缺失数据处理技术都假设 MAR。

### 3. 非随机缺失（MNAR）
当缺失数据依赖于未观察到或未知因素时发生。出现 MNAR 时，缺失信息的统计学校正实际上是无法进行的。

## 缺失数据处理方法

### 简单插补方法（不推荐）
| 方法 | 描述 | 主要问题 |
|------|------|---------|
| 完整病例分析 | 仅分析数据完整的患者 | 样本量减少、偏倚（除非 MCAR） |
| 末次观测值结转（LOCF） | 用末次记录数据点替代 | 假设结局不变，不现实 |
| 均值插补 | 用观测平均值替代缺失值 | 缩小变异度、引入偏倚 |
| 随机插补 | 随机选择观测值替代 | 未利用观测值信息 |

### 推荐方法
- **多重插补（MI）**：创建多个填补数据集，反映插补不确定性，是目前最推荐的方法
- **最大似然法**：基于完整数据的似然函数进行参数估计
- **热卡插补**：从相似的完整观测中随机选取替代值

## 关键要点

1. 缺失数据的处理策略必须基于缺失机制假设（MCAR/MAR/MNAR）
2. 简单插补方法（LOCF、均值插补等）通常不推荐——会引入偏倚并低估不确定性
3. 多重插补是目前最推荐的通用方法
4. 应报告缺失数据的比例和模式
5. 敏感性分析（不同缺失假设下的结果比较）是必需的
6. 收集数据缺失的原因有助于使 MAR 假设更合理

## 临床应用建议

- 研究设计阶段就规划缺失数据处理策略
- 在所有主要分析中执行多重插补
- 同时报告完整病例分析和多重插补结果
- 若两种方法结果一致，结论更可靠
- 若不一致，需探讨可能的 MNAR 机制

## 参考文献

1. Bakris GL, et al. Effect of finerenone on albuminuria in patients with diabetic nephropathy. 方法学, 2015, 314(9): 884–894.
2. Rubin DB. Multiple Imputation for Nonresponse in Surveys. Wiley, 1987.
3. Little RJA, Rubin DB. Statistical Analysis with Missing Data. 2nd ed. Wiley, 2002.
4. Newgard CD, Haukoos JS. Missing data: how to best account for what is not known. 方法学, 2015, 314(9): 940–941.
5. Sterne JAC, et al. Multiple imputation for missing data in epidemiological and clinical research. BMJ, 2009, 338: b2393.

---

*来源：方法学统计与方法指南 第12章*




