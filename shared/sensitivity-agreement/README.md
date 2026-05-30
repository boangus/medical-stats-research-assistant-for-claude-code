# 主要-敏感性分析一致性评估模块

> 版本: 0.1.0 | 2026-05-30

## 概述

本模块提供系统性评估**主要分析与敏感性分析一致性**的框架，基于 Xu et al. (2025) BMC Medicine 的 meta-epidemiology 研究方法学。

## 核心概念

| 概念 | 定义 |
|------|------|
| 主要分析 | SAP 预定义的主要因果效应估计方法 |
| 敏感性分析 | 用于检验主要分析结论稳健性的替代方法 |
| 一致性 | 主要分析与敏感性分析在方向、显著性、效应量上的吻合程度 |

## 评估维度

| 维度 | 判定标准 | 权重 |
|------|---------|------|
| 方向一致性 | 效应量符号相同 (OR/HR > 1 或 < 1) | 25% |
| 显著性一致性 | p<0.05 判定一致 | 25% |
| 效应量接近度 | \|log(OR₁/OR₂)\| < 0.2 | 25% |
| CI 重叠度 | 95% CI 重叠比例 ≥ 50% | 25% |

## 一致性评分

- **90-100 分**: 高度一致 — 结论完全吻合
- **70-89 分**: 中度一致 — 基本稳健，部分差异
- **50-69 分**: 低度一致 — 可能受方法选择影响
- **<50 分**: 不一致 — 需深入调查原因

## 使用场景

1. **观察性研究**: 评估 PSM/IPTW/OW 等方法结论是否一致
2. **缺失数据**: 评估不同缺失处理方法（MICE/LOCF/complete case）结论是否一致
3. **亚组分析**: 评估主要分析在不同亚组中结论是否一致
4. **论文 Limitations**: 生成"敏感性分析一致性"段落

## API

### 核心函数

```python
from sensitivity_agreement import (
    AnalysisResult,
    assess_agreement,
    assess_multiple_sensitivities,
    quick_agreement_check,
    plot_agreement_forest,
    plot_agreement_heatmap,
    generate_agreement_report,
)
```

### 快速使用

```python
# 快速一致性检查
result = quick_agreement_check(
    primary_est=0.72, primary_ci=(0.55, 0.94), primary_p=0.014,
    sensitivity_est=0.75, sensitivity_ci=(0.58, 0.97), sensitivity_p=0.028,
    primary_method="PSM", sensitivity_method="IPTW",
)
print(result.interpretation)
print(f"评分: {result.agreement_score}/100")
```

### 完整评估

```python
primary = AnalysisResult(
    name="主要分析", estimate=0.72,
    ci_lower=0.55, ci_upper=0.94, p_value=0.014,
    method="PSM",
)
sensitivities = [
    AnalysisResult(name="IPTW", estimate=0.75, ci_lower=0.58, ci_upper=0.97, p_value=0.028),
    AnalysisResult(name="OW", estimate=0.73, ci_lower=0.56, ci_upper=0.95, p_value=0.019),
]

multi_result = assess_multiple_sensitivities(primary, sensitivities)
report = generate_agreement_report(multi_result)
plot_agreement_forest(primary, sensitivities)
```

## 参考文献

- Xu J, et al. (2025). Evaluating the agreement between sensitivity and primary analyses in observational studies using routinely collected healthcare data: a meta-epidemiology study. *BMC Medicine*. DOI: 10.1186/s12916-025-04199-4



