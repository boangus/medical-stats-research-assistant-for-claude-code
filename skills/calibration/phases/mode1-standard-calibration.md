# Mode 1: 标准校准 (Standard Calibration)

> 来源：从 `skills/calibration/SKILL.md` L211-317 抽取。保留原文完整性，语义等价。

> **🔴[MANDATORY] standard**: [SLIM] 展示校准报告，自动继续

### 工作流程

```
Phase 1: 加载与验证
  │ 输入: 金标准 CSV 文件
  │ 验证: 必填字段完整性 + 数据类型正确性 + analysis_id 唯一性
  │ 🔴 [MANDATORY] 格式错误 → 🛑STOP 报告具体缺失字段
  ▼
Phase 2: 执行对比
  │ 调用 shared/calibration/calibration_runner.py (或 .R)
  │ 四维对比:
  │   1. 方法选择: gold_method vs msra_method
  │   2. 数值偏差: gold_estimate vs msra_estimate → MAE/RMSE/MAPE
  │   3. 结论准确: gold_significant vs msra_significant → 混淆矩阵
  │   4. 代码输出: gold_output vs msra_output (如有)
  │ 🔴 [MANDATORY] 对比失败 → 🛑STOP 展示错误信息，检查数据格式
  ▼
Phase 3: 生成校准报告
  │ 混淆矩阵 + TPR/TNR/FPR/FNR/PPV/NPV/F1/ACC
  │ 方法匹配率 + 不匹配详情
  │ 数值偏差 (MAE/RMSE/MAPE/PCC)
  │ 改进建议（短板领域识别）
  │ 🔴 [MANDATORY] 报告生成后 → 🛑STOP 展示摘要，等待用户确认
  ▼
Phase 4: 更新校准数据库
  │ 追加到 calibration_db.json
  │ 更新累计校准指标
  │ 输出: 校准报告 + 数据库更新确认
  │ 🔴 [MANDATORY] 数据库写入失败 → 🛑STOP 展示错误，提供手动保存方案
```

### 检查点总览

- **[SLIM] Phase 1 加载完成后**: 仅在数据格式正确时继续，错误时立即停止
- **[MANDATORY] Phase 2 对比完成后**: 必须展示对比摘要，用户确认后才生成报告
- **[MANDATORY] Phase 3 报告生成后**: 必须展示校准摘要，等待用户确认后才更新数据库
- **[ADAPTIVE] 校准数据不足(<10条)时**: 升级为 MANDATORY，提示人工复核

### 金标准数据格式

必填字段: `analysis_id`, `gold_method`, `gold_estimate`, `gold_lower`, `gold_upper`, `gold_p`, `gold_significant`

可选字段: `dataset`, `sample_size`, `covariates`, `notes`

示例见: [gold_standard_example.csv](../../../shared/calibration/gold_standard_example.csv)

### Phase 1-4 异常处理

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 金标准 CSV 必填字段缺失 | 报告具体缺失字段名，提示用户补全 | 跳过该条记录，在校准报告中标注"排除条目数" |
| analysis_id 重复 | 报告重复 ID，提示用户修正 | 保留首条，后续重复条目标记为"ID冲突已排除" |
| calibration_runner.py 执行失败 | 检查 Python 环境和依赖包 | 降级为手动对比：逐条计算偏差，输出简化报告 |
| MSRA 输出与金标准字段无法对齐 | 检查字段名映射（gold_method vs msra_method） | 跳过无法对齐的维度，仅对比可匹配维度 |
| calibration_db.json 写入失败 | 检查文件权限和磁盘空间 | 输出校准结果为独立 JSON 文件，提示用户手动合并 |
| 校准数据不足（<5条有效对比） | 提示用户补充金标准数据 | 输出"校准数据不足"警告，不计算累计指标 |
| 用户纠正缺少原始分析ID | 提示用户提供 analysis_id 或分析日期 | 按方法类型+日期范围模糊匹配，标注"匹配不确定" |
| 校准数据库版本不兼容 | 检测 schema 版本号 | 自动迁移旧格式到新格式，保留历史数据 |
| 金标准与 MSRA 输出的方法名不一致 | 检查方法名映射表（如 "Cox PH" vs "Cox regression"） | 无法映射的方法标记为"方法名不匹配"，排除出方法匹配率计算 |
| 累计指标计算溢出（数据量极大） | 使用滑动窗口（最近 1000 条）计算近期指标 | 同时保留全量和窗口指标，在报告中标注计算范围 |

### 校准引擎调用示例

**Python 调用**：
```python
from shared.calibration.calibration_runner import CalibrationRunner

runner = CalibrationRunner(
    gold_csv="shared/calibration/gold_standard_example.csv",
    msra_results="MSRA/analysis_results.json",  # MSRA 输出路径
    output_dir="MSRA/calibration/"
)

# 执行四维对比
report = runner.run()

# 输出关键指标
print(f"TPR: {report.metrics['TPR']:.1%}")
print(f"FPR: {report.metrics['FPR']:.1%}")
print(f"方法匹配率: {report.method_match_rate:.1%}")
print(f"MAPE: {report.numeric_deviation['MAPE']:.1%}")

# 更新校准数据库
runner.update_database("shared/calibration/calibration_db.json")
```

**R 调用**：
```r
source("shared/calibration/calibration_runner.R")

result <- run_calibration(
  gold_csv = "shared/calibration/gold_standard_example.csv",
  msra_json = "MSRA/analysis_results.json",
  output_dir = "MSRA/calibration/"
)

cat(sprintf("TPR: %.1f%%\n", result$metrics$TPR * 100))
cat(sprintf("FPR: %.1f%%\n", result$metrics$FPR * 100))
cat(sprintf("方法匹配率: %.1f%%\n", result$method_match_rate * 100))
```
