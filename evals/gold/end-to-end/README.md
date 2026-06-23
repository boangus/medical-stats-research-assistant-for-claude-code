# 端到端评估框架

> 版本: 1.0 | 2026-06-13
> MSRA 关联: 全流水线评估

---

## 概述

端到端评估框架测试 MSRA 从原始数据到最终报告的**完整流水线能力**，补充现有的：
- 21-tuple 数据检测评估（`evals/gold/pipeline/`）
- 10-tuple 方法选择评估（`evals/gold/method-selection/`）

## 评估维度

### 1. 代码可执行性 (Code Executability)

验证 MSRA 生成的 R/Python 代码能否在标准环境中成功运行。

| 测试用例 | 数据集 | 分析类型 | 期望输出 |
|---------|--------|---------|---------|
| E001 | mtcars (R内置) | 线性回归 + 诊断 | 回归表 + 诊断图 |
| E002 | survival::lung (R内置) | Cox回归 + KM曲线 | HR表 + KM图 |
| E003 | sklearn breast_cancer | Logistic回归 + ROC | OR表 + ROC图 |
| E004 | 自生成纵向数据 | GEE分析 | GEE摘要表 |
| E005 | 自生成竞争风险数据 | Fine-Gray分析 | SHR表 + CIF图 |

**阈值**: 5/5 通过 = 100%, 4/5 = 80% (最低可接受)

### 2. 数值精度 (Numeric Accuracy)

用预计算标准答案验证 MSRA 输出的数值精度。

| 指标 | 容忍偏差 | 说明 |
|------|---------|------|
| 点估计 (β/OR/HR) | ±0.01 | 相对偏差 < 1% |
| 95% CI | ±0.02 | CI 边界偏差 < 2% |
| P 值 | 结论一致 | p<0.05 vs p≥0.05 不能反转 |
| 效应量 (Cohen's d 等) | ±0.05 | 绝对偏差 < 0.05 |

### 3. 报告合规性 (Compliance Score)

自动检查生成报告中的报告规范条目覆盖率。

| 规范 | 条目数 | 最低覆盖率 |
|------|--------|----------|
| CONSORT 2025 | 22 | 18/22 (82%) |
| STROBE | 18 | 15/18 (83%) |
| TRIPOD+AI | 21 | 17/21 (81%) |

### 4. 鲁棒性 (Robustness)

对数据微扰动的稳定性测试。

| 扰动类型 | 方法 | 期望 |
|---------|------|------|
| 5% 缺失值注入 | 随机缺失 | 结论不变 |
| 1% 噪声添加 | 高斯噪声 | 结论不变 |
| 变量名大小写混乱 | 随机大小写 | 正确识别 |
| 日期格式混合 | ISO/US/UK 混用 | 正确解析 |

---

## 使用方法

```bash
# 运行完整端到端评估
cd evals/gold/end-to-end
python run_e2e_eval.py --verbose

# 运行单个维度
python run_e2e_eval.py --dimension code_executability
python run_e2e_eval.py --dimension numeric_accuracy
python run_e2e_eval.py --dimension compliance
python run_e2e_eval.py --dimension robustness
```

---

## 阈值合同

| 维度 | 通过阈值 | 警告阈值 |
|------|---------|---------|
| 代码可执行性 | ≥ 80% | 60-80% |
| 数值精度 | ≥ 90% 结论一致 | 80-90% |
| 报告合规性 | ≥ 80% 覆盖率 | 70-80% |
| 鲁棒性 | ≥ 90% 不变 | 80-90% |
