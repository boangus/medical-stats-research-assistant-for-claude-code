# Meta 分析方法指南

> 系统综述定量合成方法参考

## 效应量指标选择

| 数据类型 | 效应量指标 | 适用场景 |
|---------|-----------|---------|
| 二分类 | OR (Odds Ratio) | 病例对照研究 |
| 二分类 | RR (Risk Ratio) | 队列研究、RCT |
| 二分类 | RD (Risk Difference) | 当基线率差异大时 |
| 连续型 | MD (Mean Difference) | 相同测量工具 |
| 连续型 | SMD (Std. Mean Diff.) | 不同测量工具 |
| 生存数据 | HR (Hazard Ratio) | 时间-事件数据 |
| 相关性 | r (Correlation) | 相关性研究 |

## Meta 分析模型

### 固定效应模型

- **假设**: 所有研究共享一个真实效应量
- **方法**: Mantel-Haenszel (二分类), Inverse Variance (连续型)
- **适用**: 研究间同质性高 (I²<25%)

### 随机效应模型

- **假设**: 真实效应量在研究间呈分布
- **方法**: DerSimonian-Laird, REML, Paule-Mandel
- **适用**: 研究间存在异质性

## 异质性评估

| 指标 | 计算 | 解读 |
|------|------|------|
| Q 检验 | χ² 统计量 | p<0.1 拒绝同质性假设 |
| I² | (Q-df)/Q × 100% | <25% 低, 25-75% 中, >75% 高 |
| τ² | 研究间方差 | 随机效应模型参数 |
| 预测区间 | τ² 估计 | 未来研究效应量的预测范围 |

## 亚组分析与 Meta 回归

### 亚组分析

- 必须预先设定分组因素
- 每组至少 4 个研究
- 亚组间差异使用 Q 检验

### Meta 回归

- 连续型协变量的效应修饰检验
- 至少 10 个研究
- 注意多重比较校正

## 发表偏倚检测

| 方法 | 适用 | 局限 |
|------|------|------|
| 漏斗图 | ≥10 个研究 | 视觉判断主观 |
| Egger 检验 | 连续型效应量 | 小样本假阳性 |
| Begg 检验 | 排序相关 | 检验力低 |
| Trim-and-fill | 调整偏倚 | 低估异质性 |

## 参考文献

- Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. Wiley; 2009.
- Higgins JPT, Thomas J, Chandler J, et al., eds. Cochrane Handbook for Systematic Reviews of Interventions. Version 6.4. Cochrane; 2023.
