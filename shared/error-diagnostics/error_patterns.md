# 医学统计分析错误诊断知识库

> MSRA 项目专用。列出医学统计分析中常见的错误模式、诊断方法和解决方案。
> 本知识库为 Exec Runner 的自愈 Debug 提供支持。

---

## 设计初衷

医学统计分析中，错误不仅来自代码本身，更来自统计方法选择、数据特征、环境配置等多个维度。
本知识库按错误类型分类，提供系统化的诊断和解决方案。

---

## 一、统计错误诊断

### S1. 多重共线性 (Multicollinearity)

**诊断方法**：
- 计算方差膨胀因子 (VIF)
- VIF > 5 提示中度共线性
- VIF > 10 提示严重共线性

**解决方案**：
1. 删除高共线变量（保留临床意义更重要的）
2. 合并相关变量（如创建复合评分）
3. 使用主成分分析 (PCA) 降维
4. 使用岭回归 (Ridge Regression)

**代码示例**：
```r
# R: 计算VIF
library(car)
vif(model)  # VIF > 10 提示严重共线性

# Python: 计算VIF
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif = pd.DataFrame()
vif["VIF Factor"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
```

### S2. 分离问题 (Perfect Separation)

**诊断方法**：
- Logistic回归中系数估计趋向无穷大
- 标准误极大
- 收敛警告

**解决方案**：
1. 使用精确Logit回归 (Firth校正)
2. 删除导致分离的变量
3. 合并分类变量的类别
4. 使用贝叶斯Logistic回归

**代码示例**：
```r
# R: Firth校正Logistic回归
library(logistf)
logistf(outcome ~ predictor, data = df)

# Python: Firth校正
from firthlogist import FirthLogisticRegression
model = FirthLogisticRegression()
model.fit(X, y)
```

### S3. 样本量不足 (Insufficient Sample Size)

**诊断方法**：
- 实际样本量 < SAP计划的70%
- 检验效能 < 80%
- 置信区间过宽

**解决方案**：
1. 转为探索性分析 (exploratory)
2. 简化模型（减少变量）
3. 使用精确检验而非渐近检验
4. 报告效应量和置信区间，强调不确定性

**代码示例**：
```r
# R: 样本量验证
power.t.test(n = n_actual, delta = delta, sig.level = 0.05, power = NULL)
```

### S4. 比例风险假设违反 (PH Assumption Violation)

**诊断方法**：
- Schoenfeld残差检验 (p < 0.05)
- 残差图显示时间趋势

**解决方案**：
1. 使用分层Cox回归
2. 添加时依协变量
3. 使用参数生存模型
4. 报告中明确说明PH假设违反

**代码示例**：
```r
# R: Schoenfeld残差检验
cox.zph(cox_model)  # p < 0.05 提示PH假设违反

# 分层Cox回归
cox_model_strat <- coxph(Surv(time, status) ~ treatment + strata(site), data = df)
```

---

## 二、数据错误诊断

### D1. 缺失数据模式 (Missing Data Patterns)

**诊断方法**：
- 缺失率计算
- 缺失模式分析 (MCAR/MAR/MNAR)
- Little's MCAR检验

**解决方案**：
1. **MCAR**：完整案例分析 (CCA) 可接受
2. **MAR**：多重插补 (MI) 推荐
3. **MNAR**：模式混合模型或敏感性分析

**代码示例**：
```r
# R: 缺失模式分析
library(naniar)
gg_miss_var(df)  # 缺失率可视化
mcar_test(df)    # Little's MCAR检验

# 多重插补
library(mice)
imp <- mice(df, m = 5, method = "pmm")
```

### D2. 极端异常值 (Extreme Outliers)

**诊断方法**：
- IQR方法：Q1 - 1.5*IQR 或 Q3 + 1.5*IQR
- Z-score方法：|Z| > 3
- Mahalanobis距离

**解决方案**：
1. 检查数据录入错误
2. 使用稳健统计方法
3. 对数变换或Winsorize
4. 敏感性分析（包含/排除异常值）

**代码示例**：
```r
# R: 异常值检测
outliers <- boxplot.stats(df$variable)$out
# Winsorize
library(DescTools)
df$variable_winsor <- Winsorize(df$variable, probs = c(0.05, 0.95))
```

### D3. 数据分布偏态 (Skewed Distribution)

**诊断方法**：
- 偏度系数 (skewness)
- 峰度系数 (kurtosis)
- Q-Q图

**解决方案**：
1. 对数变换 (log transformation)
2. Box-Cox变换
3. 使用非参数检验
4. 使用稳健标准误

**代码示例：
```r
# R: 分布检查
library(moments)
skewness(df$variable)
kurtosis(df$variable)

# Box-Cox变换
library(forecast)
BoxCox.lambda(df$variable)
```

---

## 三、环境错误诊断

### E1. 内存不足 (Out of Memory)

**诊断方法**：
- 错误信息：`cannot allocate vector`
- 系统内存使用率 > 90%

**解决方案**：
1. 数据子采样
2. 使用流式处理
3. 优化数据类型（如将double转为float）
4. 增加系统内存

**代码示例**：
```r
# R: 内存优化
gc()  # 强制垃圾回收
df$integer_var <- as.integer(df$double_var)  # 优化数据类型
```

### E2. 包版本冲突 (Package Version Conflicts)

**诊断方法**：
- 错误信息：`package X was installed by R Y.Y.Y`
- 函数不存在或参数不匹配

**解决方案**：
1. 创建虚拟环境 (renv/conda)
2. 更新包版本
3. 使用兼容性包装器
4. 固定包版本 (renv.lock)

**代码示例**：
```r
# R: 使用renv管理环境
renv::init()
renv::snapshot()  # 保存环境状态
renv::restore()   # 恢复环境状态
```

### E3. 计算超时 (Computation Timeout)

**诊断方法**：
- 运行时间 > 预期时间的3倍
- 系统无响应

**解决方案**：
1. 简化模型（减少变量/观测）
2. 使用并行计算
3. 增加计算资源
4. 使用近似算法

**代码示例**：
```r
# R: 并行计算
library(parallel)
cl <- makeCluster(4)
results <- parLapply(cl, data_list, function(x) lm(y ~ x, data = x))
stopCluster(cl)
```

---

## 四、代码错误诊断

### C1. 语法错误 (Syntax Errors)

**诊断方法**：
- 错误信息明确指出语法错误位置
- 缺少括号、引号、逗号等

**解决方案**：
1. 检查错误位置的代码
2. 使用代码编辑器的语法高亮
3. 运行代码检查工具 (lintr)

**代码示例**：
```r
# R: 代码检查
library(lintr)
lint("analysis.R")
```

### C2. 运行时错误 (Runtime Errors)

**诊断方法**：
- 错误信息：`object not found`、`argument not found`
- 数据列名不匹配

**解决方案**：
1. 检查变量名拼写
2. 检查数据加载是否成功
3. 检查函数参数

### C3. 逻辑错误 (Logic Errors)

**诊断方法**：
- 结果不合理
- 与预期不符

**解决方案**：
1. 检查分析逻辑
2. 验证中间结果
3. 与手工计算对比

---

## 五、错误严重程度分级

### P0: 阻断式错误 (Blocking)
- 必须立即修复，否则无法继续
- 示例：数据文件损坏、关键变量缺失

### P1: 严重错误 (Critical)
- 需要修复，但可暂时继续其他工作
- 示例：假设检验失败、样本量不足

### P2: 警告 (Warning)
- 建议修复，但不影响主要结果
- 示例：次要变量缺失、轻度偏态

### P3: 信息 (Info)
- 供参考，无需立即处理
- 示例：数据分布特征、代码风格建议

---

## 六、自动修复建议模板

### 统计错误修复模板
```
错误类型: [统计错误类型]
诊断结果: [具体诊断结果]
修复建议:
1. [建议1]
2. [建议2]
3. [建议3]
预期影响: [对结果的影响]
风险提示: [修复的风险]
```

### 数据错误修复模板
```
错误类型: [数据错误类型]
受影响变量: [变量名]
修复建议:
1. [建议1]
2. [建议2]
验证方法: [如何验证修复效果]
```

### 环境错误修复模板
```
错误类型: [环境错误类型]
环境信息: [R/Python版本、包版本]
修复建议:
1. [建议1]
2. [建议2]
预防措施: [如何避免未来发生]
```

---

*知识库创建时间: 2026-05-30*
*维护者: MSRA开发团队*
*版本: v0.1.0*