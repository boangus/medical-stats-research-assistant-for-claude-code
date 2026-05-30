# 假设检验报告模板

> MSRA 项目专用。用于生成标准化的假设检验报告。

---

## 报告结构

### 1. 报告摘要

**研究名称**: [研究名称]
**分析日期**: [日期]
**分析人员**: [分析人员]
**SAP版本**: [SAP版本号]

### 2. 检验概览

| 检验项目 | 检验方法 | 样本量 | 检验统计量 | p值 | 结论 |
|---------|---------|--------|-----------|-----|------|
| 正态性 | Shapiro-Wilk | N=XX | W=0.XX | 0.XX | 满足/不满足 |
| 方差齐性 | Levene | N=XX | F=0.XX | 0.XX | 满足/不满足 |
| 线性关系 | 残差图 | N=XX | - | - | 满足/不满足 |
| 多重共线性 | VIF | N=XX | VIF=0.XX | - | 满足/不满足 |
| 比例风险 | Schoenfeld | N=XX | χ²=0.XX | 0.XX | 满足/不满足 |

### 3. 详细检验结果

#### 3.1 正态性检验

**检验目的**: 验证连续变量是否服从正态分布

**检验方法**: Shapiro-Wilk检验
- H₀: 数据服从正态分布
- H₁: 数据不服从正态分布
- 显著性水平: α = 0.05

**检验结果**:
```
变量: [变量名]
分组: [组别]
样本量: N = XX
Shapiro-Wilk W = 0.XXXX
p值 = 0.XXXX
95% CI: [0.XXXX, 0.XXXX]
```

**结论**: 
- [ ] p > 0.05 → 满足正态性假设 → 使用参数检验
- [ ] p ≤ 0.05 → 不满足正态性假设 → 使用非参数检验

**可视化**: [Q-Q图路径]

#### 3.2 方差齐性检验

**检验目的**: 验证组间方差是否相等

**检验方法**: Levene检验
- H₀: 组间方差相等
- H₁: 组间方差不相等
- 显著性水平: α = 0.05

**检验结果**:
```
变量: [变量名]
分组变量: [分组变量]
组数: K = XX
Levene F = 0.XXXX
p值 = 0.XXXX
```

**结论**:
- [ ] p > 0.05 → 满足方差齐性 → 使用标准t检验/ANOVA
- [ ] p ≤ 0.05 → 不满足方差齐性 → 使用Welch校正

#### 3.3 多重共线性检查

**检验目的**: 验证回归模型中自变量是否存在严重共线性

**检验方法**: 方差膨胀因子 (VIF)
- VIF < 5: 无共线性
- 5 ≤ VIF < 10: 中度共线性
- VIF ≥ 10: 严重共线性

**检验结果**:
```
模型: [模型公式]
变量VIF值:
- [变量1]: VIF = 0.XX
- [变量2]: VIF = 0.XX
- [变量3]: VIF = 0.XX
平均VIF: 0.XX
```

**结论**:
- [ ] 所有VIF < 5 → 无共线性问题
- [ ] 任一VIF ≥ 10 → 严重共线性，需处理

#### 3.4 比例风险假设检验 (Cox回归)

**检验目的**: 验证Cox回归的比例风险假设

**检验方法**: Schoenfeld残差检验
- H₀: 风险比例恒定
- H₁: 风险比例随时间变化
- 显著性水平: α = 0.05

**检验结果**:
```
模型: [Cox模型公式]
Schoenfeld残差检验:
- 变量 [变量1]: χ² = 0.XX, p = 0.XX
- 变量 [变量2]: χ² = 0.XX, p = 0.XX
全局检验: χ² = 0.XX, p = 0.XX
```

**结论**:
- [ ] p > 0.05 → 满足PH假设
- [ ] p ≤ 0.05 → 违反PH假设，需处理

### 4. 假设违反处理

#### 4.1 正态性违反处理

**违反情况**: [具体描述]
**处理方法**: 
1. [ ] 使用非参数检验 (Mann-Whitney U / Kruskal-Wallis)
2. [ ] 数据变换 (对数/平方根)
3. [ ] 使用稳健标准误

**降级代码**:
```r
# 原方法: t检验
# t.test(group1, group2)

# 降级方法: Mann-Whitney U检验
wilcox.test(group1, group2)
```

#### 4.2 方差齐性违反处理

**违反情况**: [具体描述]
**处理方法**:
1. [ ] 使用Welch校正
2. [ ] 使用Brown-Forsythe检验

**降级代码**:
```r
# 原方法: t检验
# t.test(group1, group2, var.equal = TRUE)

# 降级方法: Welch t检验
t.test(group1, group2, var.equal = FALSE)
```

#### 4.3 多重共线性处理

**违反情况**: [具体描述]
**处理方法**:
1. [ ] 删除高共线变量
2. [ ] 合并相关变量
3. [ ] 使用主成分分析

**降级代码**:
```r
# 原模型: y ~ x1 + x2 + x3 (x1和x2共线性)
# 降级模型: y ~ x1 + x3 (删除x2)
model_reduced <- lm(y ~ x1 + x3, data = df)
```

#### 4.4 比例风险假设违反处理

**违反情况**: [具体描述]
**处理方法**:
1. [ ] 使用分层Cox回归
2. [ ] 添加时依协变量
3. [ ] 使用参数生存模型

**降级代码**:
```r
# 原模型: coxph(Surv(time, status) ~ treatment + x1)
# 降级模型: 分层Cox回归
coxph(Surv(time, status) ~ treatment + strata(site), data = df)
```

### 5. SAP一致性检查

#### 5.1 方法匹配检查

| SAP预设方法 | 数据特征 | 匹配情况 | 建议 |
|------------|---------|---------|------|
| t检验 | 正态分布 | [ ] 匹配 | - |
| t检验 | 非正态分布 | [ ] 不匹配 | 建议使用Mann-Whitney U |
| ANOVA | 方差齐性 | [ ] 匹配 | - |
| ANOVA | 方差不齐 | [ ] 不匹配 | 建议使用Welch ANOVA |
| Cox回归 | PH假设满足 | [ ] 匹配 | - |
| Cox回归 | PH假设违反 | [ ] 不匹配 | 建议使用分层Cox |

#### 5.2 偏差记录

**偏差1**:
- **SAP预设**: [方法描述]
- **实际执行**: [方法描述]
- **偏差原因**: [原因说明]
- **影响评估**: [影响说明]
- **用户确认**: [已确认/待确认]

### 6. 总体结论

#### 6.1 假设检验总结

**满足的假设**:
1. [假设1]
2. [假设2]

**违反的假设**:
1. [假设1] - 已通过[处理方法]解决
2. [假设2] - 已通过[处理方法]解决

#### 6.2 方法学建议

**主要分析**:
- [ ] 使用SAP预设方法
- [ ] 使用降级方法（原因：[说明]）

**敏感性分析**:
- [ ] 包含[敏感性分析内容]
- [ ] 比较不同方法的结果一致性

#### 6.3 报告注意事项

在最终报告中需要说明：
1. 假设检验的结果
2. 假设违反的处理方法
3. 与SAP的偏差（如有）
4. 对结果解读的影响

---

## 附录

### A. 检验代码

```r
# 正态性检验
shapiro.test(df$variable)

# 方差齐性检验
library(car)
leveneTest(variable ~ group, data = df)

# VIF计算
library(car)
vif(model)

# Schoenfeld残差检验
cox.zph(cox_model)
```

### B. 可视化代码

```r
# Q-Q图
qqnorm(df$variable)
qqline(df$variable)

# 残差图
plot(fitted(model), residuals(model))

# Schoenfeld残差图
plot(cox.zph(cox_model))
```

### C. 参考文献

1. Shapiro SS, Wilk MB (1965). "An analysis of variance test for normality (complete samples)". Biometrika.
2. Levene H (1960). "Robust tests for equality of variances". Contributions to Probability and Statistics.
3. Schoenfeld D (1982). "Partial residuals for the proportional hazards regression model". Biometrika.

---

*模板版本: v0.1.0*
*创建日期: 2026-05-30*
*维护者: MSRA开发团队*