# 结果复现验证指南

> 自动重跑分析代码 3 次，检查关键结论一致性。
> 版本: 0.1.0 | 2026-05-29

---

## 原理

统计软件（R/Python）的随机数生成、优化算法、大型数据集处理等，可能导致同一个分析在不同运行时产生微小差异。**可复现 ≠ 完全一致**，关键是关键结论的一致性。

### 可接受差异范围

| 指标类型 | 可接受偏差 | 示例 |
|---------|-----------|------|
| 点估计 (OR/HR/β) | ±0.005 | OR=1.50 允许 1.495-1.505 |
| 置信区间 | ±0.01 | 95% CI 边界 ±0.01 |
| p 值 | 结论性一致 | p=0.048 vs p=0.052 → 需要标记 |
| 分类结果 | 完全一致 | AIC/BIC 差异 < 1 |
| 图表布局 | 视觉一致 | 坐标/标签/颜色一致 |

---

## 使用方式

### 方式 1: R 脚本自动验证 (reproducibility_check.R)

```r
# 来源: src/shared/reproducibility/reproducibility_check.R
# 用法: 传入分析脚本路径，自动执行 3 次并生成复现报告

source("src/shared/reproducibility/reproducibility_check.R")

# 检查你的分析脚本
check_reproducibility(
  script_path = "analysis/main_analysis.R",
  output_dir = "reproducibility/",
  n_runs = 3,
  key_params = c("coef", "p_value", "aic")  # 需从输出中提取的关键参数
)
```

### 方式 2: Python 脚本自动验证 (reproducibility_check.py)

```python
# 来源: src/shared/reproducibility/reproducibility_check.py

from reproducibility_check import ReproducibilityChecker

checker = ReproducibilityChecker(
    script_path="analysis/main_analysis.py",
    n_runs=3,
    output_dir="reproducibility/"
)

report = checker.run()
print(report)
```

### 方式 3: 数据清洗审计追踪 (PipelineAuditor)

基于 ehrapy CohortTracker 的设计理念 (Nature Medicine 2024)，
使用 `pipeline_auditor.py` 追踪 Stage 1 数据清洗的每一步。

```python
# 来源: src/shared/reproducibility/pipeline_auditor.py

from pipeline_auditor import PipelineAuditor

auditor = PipelineAuditor(raw_data, name="队列清洗", 
                          metadata={"研究": "XXX 疗效分析"})

# 每次操作后记录
df = df[df["age"] >= 18]
auditor.record_filter("age >= 18", df_before, df, "排除未成年")

df = df.dropna(subset=["bmi"])
auditor.record_dropna(["bmi"], df_before, df)

# 生成报告
auditor.save_report("audit_report.md")
```

详见: [pipeline_auditor.py](pipeline_auditor.py)

### 方式 4: 手动验证步骤

当自动验证不可行时（如图表输出），执行手动检查：

```
1. 📋 运行 1: 记录所有关键输出数字
2. 📋 运行 2: 记录所有关键输出数字
3. 📋 运行 3: 记录所有关键输出数字
4. 📊 比较三次数值 → 计算 max - min
5. ✅/❌ 根据可接受范围判断
```

---

## 协议: 何时需要复现验证

### 必须验证的情况

| 场景 | 原因 |
|------|------|
| 代码包含随机数生成 | `set.seed()` 使用不同种子 |
| 使用自举法 (Bootstrap) | 每次抽样结果不同 |
| 使用 MCMC 采样 | 链间变异 |
| 使用机器学习模型 | 训练/测试集随机拆分 |
| 大型数据集 (n > 10,000) | 数值计算精度可能受影响 |
| SAP 中指定了复现验证 | 预先计划的验证 |

### 可跳过的情况

| 场景 | 原因 |
|------|------|
| 纯描述性统计（无随机性） | 结果确定 |
| 确定性分析（如 t 检验） | 结果确定 |
| 已有固定种子的代码 | 可完全复现 |

---

## 结果解读

### 一致性等级

| 等级 | 标准 | 操作 |
|------|------|------|
| ✅ 完全一致 | 所有关键参数 3 次完全一致 | 无需处理 |
| ✅ 一致 | 差异在可接受范围内 | 报告差异，可进入下一阶段 |
| ⚠️ 轻微警告 | 1-2 个参数超出范围但结论不变 | 标记并在报告中说明 |
| ❌ 不一致 | 关键结论在运行间发生变化 | **阻断：必须排查原因后重新分析** |

### 复现报告模板

```
## 复现验证报告

### 分析信息
- 脚本: [path]
- 运行次数: 3
- 运行时间: [times]

### 关键参数稳定性

| 参数 | 运行 1 | 运行 2 | 运行 3 | 范围 | 判断 |
|------|--------|--------|--------|------|------|
| HR (treatment) | 0.72 | 0.71 | 0.72 | 0.01 | ✅ |
| p (treatment) | 0.032 | 0.028 | 0.031 | 0.004 | ⚠️ |
| AIC | 1256.3 | 1255.9 | 1256.1 | 0.4 | ✅ |

### 结论
✅ 通过 — 关键结论在 3 次运行间一致。
```

---

## 集成到质量门闸

Stage 3.5（结果质量门闸）中包含复现验证检查：

```
□ [REPRODUCIBILITY] 关键结果在 3 次重跑后是否一致？
```

### 复现验证失败处理流程

```
QC Inspector 执行 3 次重跑
       │
       ├── ✅ 通过 → 进入下一阶段
       │
       └── ❌ 失败
              │
              ├── 检查代码随机种子
              │     ├── 缺少 set.seed() → 添加后重试
              │     └── 已有种子 → 继续排查
              │
              ├── 检查是否涉及 Bootstrap/MCMC
              │     ├── 是 → 增大运行次数到 10-100 次
              │     └── 否 → 继续排查
              │
              └── 通知 Orchestrator
                    └── Orchestrator 决定：修正代码 / 接受差异 / 阻断
```



