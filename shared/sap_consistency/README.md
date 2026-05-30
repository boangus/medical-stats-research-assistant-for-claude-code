# SAP一致性检查器 (SAP Consistency Check)

> MSRA 项目专用。比较SAP预设方法与数据特征，检测不匹配情况，提供替代方法建议。

## 概述

本模块用于在分析执行前验证SAP（统计分析计划）与实际数据特征的一致性。当SAP预设方法与数据特征不匹配时，自动提供替代方法建议和偏差记录。

## 目录结构

```
sap_consistency/
├── README.md                    # 本文件
├── sap_consistency_check.py     # Python实现
└── sap_consistency_check.R      # R实现
```

## 功能特性

### 1. 正态性一致性检查
- 比较SAP预设方法（参数/非参数）与数据正态性检验结果
- 自动建议替代方法（如参数→非参数）

### 2. 方差齐性一致性检查
- 比较SAP预设方法（等方差/不等方差）与Levene检验结果
- 自动建议Welch校正或标准方法

### 3. 多重共线性检查
- 计算VIF值，检测严重共线性
- 建议删除变量或使用正则化方法

### 4. 样本量一致性检查
- 比较实际样本量与SAP计划样本量
- 评估检验效能影响

## 使用方法

### Python 使用示例

```python
from sap_consistency_check import SAPConsistencyCheck

# SAP配置
sap_config = {
    "normality_test": "shapiro-wilk",
    "homogeneity_test": "levene",
    "main_analysis": "t-test",
    "equal_var": True,
    "sample_size": 100
}

# 创建一致性检查器
checker = SAPConsistencyCheck(sap_config)

# 执行检查
normality_result = checker.check_normality(data, "outcome", "group")
homogeneity_result = checker.check_homogeneity(data, "outcome", "group")
sample_size_result = checker.check_sample_size(100, 100)

# 生成报告
checker.consistency_results = [normality_result, homogeneity_result, sample_size_result]
report = checker.generate_consistency_report()
```

### R 使用示例

```r
source("sap_consistency_check.R")

# SAP配置
sap_config <- list(
  normality_test = "shapiro-wilk",
  homogeneity_test = "levene",
  main_analysis = "t-test",
  equal_var = TRUE,
  sample_size = 100
)

# 创建一致性检查器
checker <- SAPConsistencyCheck(sap_config)

# 执行检查
normality_result <- checker$check_normality(data, "outcome", "group")
homogeneity_result <- checker$check_homogeneity(data, "outcome", "group")
sample_size_result <- checker$check_sample_size(100, 100)

# 生成报告
checker$consistency_results <- list(normality_result, homogeneity_result, sample_size_result)
report <- checker$generate_consistency_report()
```

## 集成到 MSRA 流水线

### Stage 3: 分析执行

在 `analysis-exec` 技能的 Phase 7 中，SAP一致性检查已集成：

1. **预检验检查**: 验证样本量、变量类型、数据完整性
2. **假设检验执行**: 按SAP计划执行所有假设检验
3. **假设违反处理**: 自动检测假设违反，查询错误诊断知识库
4. **SAP一致性检查**: 比较SAP预设方法与数据特征

### 质量门闸集成

Stage 3.5 质量门闸会检查：
- 所有假设检验是否完成
- 假设违反是否已处理
- SAP偏差是否已记录

## 检查结果格式

### 一致性检查结果

```python
{
    "check_type": "normality",
    "variable": "outcome",
    "sap_method": "shapiro-wilk",
    "data_characteristics": {
        "shapiro_stat": 0.98,
        "p_value": 0.45,
        "normal": True
    },
    "consistency": True,
    "mismatch_details": "数据满足正态性，SAP预设参数方法合适",
    "alternative_method": "",
    "code_suggestion": ""
}
```

### 不一致检查结果

```python
{
    "check_type": "normality",
    "variable": "outcome",
    "sap_method": "shapiro-wilk",
    "data_characteristics": {
        "shapiro_stat": 0.85,
        "p_value": 0.01,
        "normal": False
    },
    "consistency": False,
    "mismatch_details": "数据不满足正态性，但SAP预设参数方法",
    "alternative_method": "建议使用非参数检验",
    "code_suggestion": "wilcox.test(outcome ~ group, data = df)"
}
```

## 错误处理

### 常见错误

1. **样本量不足**: 无法进行假设检验
2. **变量类型不匹配**: 连续变量用于分类检验
3. **数据缺失过多**: 无法计算检验统计量

### 错误恢复

- 自动跳过无法执行的检验
- 记录跳过原因和影响
- 在报告中说明局限性

## 扩展指南

### 添加新的检查类型

1. 在 `sap_consistency_check.py` 或 `sap_consistency_check.R` 中添加新的检查方法
2. 更新 `generate_consistency_report` 方法以包含新检查
3. 更新本 README 文档

### 自定义SAP配置

```python
sap_config = {
    # 正态性检验方法
    "normality_test": "shapiro-wilk",  # 或 "kolmogorov-smirnov"
    
    # 方差齐性检验方法
    "homogeneity_test": "levene",  # 或 "bartlett"
    
    # 主要分析方法
    "main_analysis": "t-test",  # 或 "anova", "chi-square", "fisher"
    
    # 是否假设等方差
    "equal_var": True,
    
    # 计划样本量
    "sample_size": 100,
    
    # 显著性水平
    "alpha": 0.05
}
```

## 参考文献

1. Shapiro SS, Wilk MB (1965). "An analysis of variance test for normality (complete samples)". Biometrika.
2. Levene H (1960). "Robust tests for equality of variances". Contributions to Probability and Statistics.
3. Rousseeuw PJ, Leroy AM (2003). "Robust Regression and Outlier Detection". John Wiley & Sons.

## 更新日志

### v0.1.0 (2026-05-30)
- 初始版本
- 支持正态性、方差齐性、样本量一致性检查
- 提供Python和R实现
- 集成到MSRA流水线

---

*维护者: MSRA开发团队*
*最后更新: 2026-05-30*