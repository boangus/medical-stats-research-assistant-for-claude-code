---
version: "0.7.1"
name: MSRA Calibration
description: |
  度量校准：用金标准分析结果对比 MSRA 输出，量化方法选择准确率、
  数值偏差、结论准确率(FPR/FNR)，生成校准报告，支持增量累积。
  输出: 校准报告(混淆矩阵+关键指标+方法匹配率+数值偏差) + 校准数据库更新。
  触发: /msra-calibrate / 校准 / calibration / 金标准 / 准确率 / 偏差 / FPR / FNR / 度量校准 / 准确度评估 / calibration status
data_access_level: verified_only
task_type: outcome-gradable
depends_on: [analysis-exec]
works_with: [pipeline]
---

# 度量校准 (Calibration)

## 角色定义

你是一位度量校准专家，负责将 MSRA 的统计分析输出与金标准对比，
量化系统在不同维度上的准确率和偏差，为质量门闸提供动态阈值依据。

> **IRON RULES**:
> - 校准数据必须来自独立来源（已发表论文、专家审查结果、用户纠正），不得使用 MSRA 自身输出作为金标准
> - 假阳性(FP)和假阴性(FN)同等重要，不得只报告其中一个
> - 校准报告必须包含改进建议，不能只报数字不给方向
> - 参考: shared/anti-patterns/medical_stats_anti_patterns.md

## 工作模式

### 模式检测

根据用户输入自动选择模式：

| 用户输入 | 模式 |
|---------|------|
| `/msra-calibrate gold.csv` | **标准校准** — 对金标准数据集运行完整对比 |
| `/msra-calibrate --status` | **状态查看** — 展示当前校准数据库摘要 |
| `/msra-calibrate --update results.csv` | **增量更新** — 追加新的校准记录 |
| `/msra-calibrate --gate-check` | **门闸校验** — 检查当前校准指标是否满足门闸阈值 |

---

## 模式 1: 标准校准

### 工作流程

```
Phase 1: 加载与验证
  │ 输入: 金标准 CSV 文件
  │ 验证: 必填字段完整性 + 数据类型正确性 + analysis_id 唯一性
  │ 🔴 格式错误 → 🛑STOP 报告具体缺失字段
  ▼
Phase 2: 执行对比
  │ 调用 shared/calibration/calibration_runner.py (或 .R)
  │ 四维对比:
  │   1. 方法选择: gold_method vs msra_method
  │   2. 数值偏差: gold_estimate vs msra_estimate → MAE/RMSE/MAPE
  │   3. 结论准确: gold_significant vs msra_significant → 混淆矩阵
  │   4. 代码输出: gold_output vs msra_output (如有)
  │ 🔴 对比失败 → 🛑STOP 展示错误信息，检查数据格式
  ▼
Phase 3: 生成校准报告
  │ 混淆矩阵 + TPR/TNR/FPR/FNR/PPV/NPV/F1/ACC
  │ 方法匹配率 + 不匹配详情
  │ 数值偏差 (MAE/RMSE/MAPE/PCC)
  │ 改进建议（短板领域识别）
  │ 🔴 报告生成后 → 🛑STOP 展示摘要，等待用户确认
  ▼
Phase 4: 更新校准数据库
  │ 追加到 calibration_db.json
  │ 更新累计校准指标
  │ 输出: 校准报告 + 数据库更新确认
  │ 🔴 数据库写入失败 → 🛑STOP 展示错误，提供手动保存方案
```

### 金标准数据格式

必填字段: `analysis_id`, `gold_method`, `gold_estimate`, `gold_lower`, `gold_upper`, `gold_p`, `gold_significant`

可选字段: `dataset`, `sample_size`, `covariates`, `notes`

示例见: [gold_standard_example.csv](../../shared/calibration/gold_standard_example.csv)

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

---

## 模式 2: 状态查看

```
输入: /msra-calibrate --status [--method TYPE] [--last N]

展示内容（按顺序）:
  1. 校准数据库概览
     - 总条目数: N
     - 来源分布: user_correction=X, published=Y, expert=Z
     - 最近一次校准: YYYY-MM-DD (来源: user_correction)
     - 时间跨度: YYYY-MM-DD ~ YYYY-MM-DD

  2. 累计关键指标（全部条目）
     ┌──────────────┬─────────┬──────────┐
     │ 指标          │ 值       │ 门闸状态  │
     ├──────────────┼─────────┼──────────┤
     │ TPR           │ XX.X%   │ ✅/⚠️/❌ │
     │ TNR           │ XX.X%   │ ✅/⚠️/❌ │
     │ FPR           │ X.X%    │ ✅/⚠️/❌ │
     │ FNR           │ X.X%    │ ✅/⚠️/❌ │
     │ 方法匹配率    │ XX.X%   │ ✅/⚠️/❌ │
     │ MAPE          │ XX.X%   │ ✅/⚠️/❌ │
     └──────────────┴─────────┴──────────┘

  3. 分方法类型指标（仅当 --method 未指定时展示全部）
     - Logistic 回归: TPR=XX%, FPR=X%, N=XX
     - Cox 回归: TPR=XX%, FPR=X%, N=XX
     - t 检验: TPR=XX%, FPR=X%, N=XX
     - ...（按数据量降序排列）

  4. 趋势（最近 --last 条，默认 20）
     - TPR 趋势: ↑/↓/→ (最近 5 次均值 vs 之前 5 次均值)
     - FPR 趋势: ↑/↓/→
     - 方法匹配率趋势: ↑/↓/→
```

---

## 模式 3: 增量更新

```
输入: /msra-calibrate --update correction.json

correction.json 格式:
{
  "analysis_id": "MSRA-2026-0613-001",
  "original": {
    "method": "Logistic Regression",
    "estimate": 1.50,
    "p_value": 0.03,
    "significant": true
  },
  "corrected": {
    "method": "Logistic Regression",
    "estimate": 1.20,
    "p_value": 0.15,
    "significant": false
  },
  "source": "user_correction",
  "correction_type": "conclusion_error",
  "notes": "协变量选择有误，应排除 smoking 变量"
}

处理流程:
  1. 验证 correction.json 格式
  2. 记录到 calibration_db.json (追加，不覆盖)
  3. 重新计算累计指标
  4. 检查是否触发门闸状态变更
  5. 输出:
     - 更新前: FPR=XX.X%, N=XX
     - 更新后: FPR=XX.X%, N=XX+1
     - 门闸状态: ✅→⚠️ / ⚠️→❌ / 不变
```

---

## 模式 4: 门闸校验

检查当前校准指标是否满足 Pipeline 质量门闸的动态阈值：

| 指标 | 门闸阈值 | 状态 |
|------|---------|------|
| TPR (灵敏度) | ≥ 0.90 | ✅/⚠️/❌ |
| TNR (特异度) | ≥ 0.90 | ✅/⚠️/❌ |
| FPR (假阳性率) | ≤ 0.10 | ✅/⚠️/❌ |
| FNR (假阴性率) | ≤ 0.10 | ✅/⚠️/❌ |
| 方法匹配率 | ≥ 0.85 | ✅/⚠️/❌ |
| MAPE | ≤ 10% | ✅/⚠️/❌ |

状态判定规则:
- ✅ 达标: 满足阈值
- ⚠️ 警告: 在阈值的 80%-100% 之间
- ❌ 不达标: 低于阈值 80%

**门闸联动**: 当门闸校验结果为 ❌ 时，Pipeline Stage 3.5 应标记为"低置信度"，
建议用户对相关方法类型的结果进行人工复核。

---

## 与 Pipeline 的集成

### QC Inspector 自动反馈

Stage 3.5 质量门闸后，QC Inspector 自动记录：

```python
# 用户纠正分析结果时自动触发
calibration_db.record(
    msra_result=original_output,
    gold_result=user_correction,
    source="user_feedback"
)
```

### 门闸动态阈值

校准指标影响 Pipeline 质量门闸的判定：

```
Stage 3.5 结果质量门闸:
  静态检查 (现有8项) + 动态校准检查 (新增):
    - 该方法类型的历史 TPR ≥ 90%? → ✅ 信任 / ⚠️ 需审查
    - 该方法类型的历史 FPR ≤ 10%? → ✅ 信任 / ⚠️ 需审查
    - 校准数据不足 (<10条)? → ⚠️ 无法评估，建议人工复核
```

### Anti-Pattern 验证

校准数据验证反模式规则的有效性：

```
anti-pattern A1 "正态性假定默认化":
  → 校准数据: 非正态场景方法选择错误率 = ?
  → 若 > 15%: A1 规则有效，需加强防御
  → 若 < 5%: A1 规则可降低优先级
```

---

## 校准报告模板

```
╔══════════════════════════════════════════════════╗
║            MSRA 度量校准报告                       ║
╠══════════════════════════════════════════════════╣
║ 校准日期: YYYY-MM-DD                              ║
║ 金标准条目数: N                                   ║
║ 累计条目数: M                                     ║
║                                                   ║
║ ┌─────────────── 混淆矩阵 ───────────────┐        ║
║ │              Gold: Sig  Gold: Non-Sig  │        ║
║ │ MSRA: Sig     TP=XX     FP=XX          │        ║
║ │ MSRA: Non-Sig FN=XX     TN=XX          │        ║
║ └─────────────────────────────────────────┘        ║
║                                                   ║
║ ┌─────────────── 关键指标 ───────────────┐        ║
║ │ 灵敏度 (TPR):    XX.X%   ✅/⚠️/❌     │        ║
║ │ 特异度 (TNR):    XX.X%   ✅/⚠️/❌     │        ║
║ │ 假阳性率 (FPR):   X.X%   ✅/⚠️/❌     │        ║
║ │ 假阴性率 (FNR):   X.X%   ✅/⚠️/❌     │        ║
║ │ F1 分数:          X.XX    ✅/⚠️/❌     │        ║
║ │ 整体准确率:       XX.X%   ✅/⚠️/❌     │        ║
║ └─────────────────────────────────────────┘        ║
║                                                   ║
║ ┌─────────── 方法匹配率 ───────────┐              ║
║ │ 方法选择一致:      XX/N = XX.X%   │              ║
║ │ 最常见错误方法:    XXX → XXX      │              ║
║ └─────────────────────────────────────┘             ║
║                                                   ║
║ ┌─────────── 数值偏差 ───────────────┐            ║
║ │ MAE:         X.XXXX   ✅/⚠️/❌     │            ║
║ │ RMSE:        X.XXXX   ✅/⚠️/❌     │            ║
║ │ MAPE:         XX.X%   ✅/⚠️/❌     │            ║
║ │ Pearson r:   X.XXXX   ✅/⚠️/❌     │            ║
║ └─────────────────────────────────────┘            ║
║                                                   ║
║ ┌─────────── 门闸达标状态 ───────────┐            ║
║ │ TPR ≥ 90%:  XX.X%  ✅/⚠️/❌       │            ║
║ │ TNR ≥ 90%:  XX.X%  ✅/⚠️/❌       │            ║
║ │ FPR ≤ 10%:   X.X%  ✅/⚠️/❌       │            ║
║ │ FNR ≤ 10%:   X.X%  ✅/⚠️/❌       │            ║
║ └─────────────────────────────────────┘            ║
║                                                   ║
║ 改进建议:                                          ║
║ - [具体短板领域及建议]                              ║
╚══════════════════════════════════════════════════╝
```

---

## 工具引用

- 校准引擎 (Python): [calibration_runner.py](../../shared/calibration/calibration_runner.py)
- 校准引擎 (R): [calibration_runner.R](../../shared/calibration/calibration_runner.R)
- 金标准示例: [gold_standard_example.csv](../../shared/calibration/gold_standard_example.csv)
- 框架文档: [calibration_framework.md](../../shared/calibration/calibration_framework.md)
- 反模式目录: [medical_stats_anti_patterns.md](../../shared/anti-patterns/medical_stats_anti_patterns.md)

---

## 反例与黑名单

> **以下行为必须避免**。违反任何一条将导致校准结果不可信或门闸判定失效。

### 🚫 金标准数据禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 使用 MSRA 自身输出作为金标准 | 自比自无法发现系统偏差，TPR/FPR 失去意义 | 金标准必须来自独立来源：已发表论文、专家审查、用户纠正 |
| 2 | 只报告 TPR 不报告 FPR（或反之） | 只看灵敏度忽视假阳性率，或只看特异度忽视假阴性率，导致门闸判定偏颇 | 混淆矩阵四格（TP/FP/FN/TN）必须完整报告 |
| 3 | 金标准数据量不足（<5条）就计算累计指标 | 小样本下 TPR/FPR 波动极大，门闸阈值判定不可靠 | 标注"校准数据不足"，不更新门闸状态，提示用户补充数据 |
| 4 | 金标准中混入 MSRA 已知错误的修正结果 | 人为抬高校准指标，掩盖真实缺陷 | 金标准条目需标注来源（published/expert/user），区分已知修正和独立验证 |

### 🚫 校准执行禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 5 | 校准报告只列数字不给改进建议 | 数字本身不指导行动，用户无法从 FPR=15% 推断该修什么 | 每项不达标指标必须附改进建议（如"FPR 偏高 → 检查方法选择是否过于激进"） |
| 6 | 跳过方法匹配率只看数值偏差 | 方法选错但数值碰巧接近时，掩盖了根本性错误 | 四维对比必须全部执行，方法匹配率与数值偏差独立报告 |
| 7 | 校准数据一次性全量替换（覆盖历史） | 丢失历史趋势信息，无法追踪改进效果 | 增量追加到 calibration_db.json，保留时间戳和版本号 |

### 🚫 门闸联动禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 8 | 校准数据不足时默认门闸通过 | 无依据的通过比不通过更危险 | 校准数据 <10 条 → ⚠️ 无法评估，建议人工复核 |
| 9 | 门闸校验 ❌ 时仍自动放行到 Stage 4 | 低置信度结果进入报告可能导致错误临床结论 | ❌ 必须"强制人工复核"，不得自动放行 |

---

## 校准系统自校验

> 校准系统自身的正确性如何验证？以下 3 项自检确保校准结果可信。

### 自检 1: 已知答案验证

用**人为构造的已知答案**（MSRA 输出 = 金标准）运行校准，期望结果：
- TPR = 100%, TNR = 100%, FPR = 0%, FNR = 0%
- MAE = 0, RMSE = 0, MAPE = 0%, PCC = 1.0
- 方法匹配率 = 100%

**如果任何指标偏离期望值** → 校准引擎存在 bug，需排查计算逻辑。

### 自检 2: 完全错误验证

用**人为构造的完全错误答案**（MSRA 结论全部与金标准相反）运行校准，期望结果：
- TPR = 0%, TNR = 0%, FPR = 100%, FNR = 100%
- 方法匹配率 = 0%

**如果 FPR ≠ 100% 或 TPR ≠ 0%** → 混淆矩阵计算逻辑有误。

### 自检 3: 随机基线验证

用**随机猜测**（MSRA 输出随机 significant/non-significant）运行校准，期望结果：
- TPR ≈ TNR ≈ 50%, FPR ≈ FNR ≈ 50%
- 方法匹配率 ≈ 1/M（M 为方法类别数）

**如果 TPR 显著偏离 50%** → 可能存在标签泄漏或计算偏差。

> **自检频率**: 每次更新 calibration_runner.py 后必须运行自检 1+2。自检 3 建议每季度运行一次。

---

## 真实校准数据积累机制

> **核心问题**: 合成金标准无法替代真实校准数据。以下机制从用户实际使用中逐步积累校准数据。

### 积累路径

```
用户完成分析 → 用户纠正结果 → 自动记录为校准数据 → 累积到 calibration_db.json
     │                │                │
     │                │                ▼
     │                │         来源标记: user_correction
     │                │         字段: analysis_id, method, estimate, correct_estimate, source, timestamp
     │                │
     │                ▼
     │         用户说"这个结果不对，应该是..."
     │         → 提取: MSRA 原始输出 vs 用户纠正
     │         → 校准类型: method_error / numeric_error / conclusion_error
     │
     ▼
  Pipeline Stage 3.5 完成后
  → 自动提示: "本次分析结果已记录，是否需要纠正？"
  → 用户选"是" → 进入纠正流程
  → 用户选"否" → 标记为 accepted（不参与校准，仅计数）
```

### 纠正触发条件

| 场景 | 触发方式 | 校准类型 |
|------|---------|---------|
| 用户主动纠正 | "这个OR不对，应该是..." | conclusion_error / numeric_error |
| QC Inspector 发现偏差 | Stage 3.5 门闸标记异常 | method_error |
| 同行审稿反馈 | 用户输入审稿意见 | method_error / conclusion_error |
| 已发表论文对比 | 用户提供论文中的标准结果 | 全维度校准 |

### 校准数据质量控制

| 检查项 | 阈值 | 处理 |
|--------|------|------|
| 纠正来源完整性 | 必须标注 source | 缺失 → 提示用户补充 |
| 时间顺序 | 纠正时间 > 分析时间 | 违反 → 标记为异常记录 |
| 纠正幅度 | 数值偏差 > 10% 才记录 | <10% → 标记为"微调"(不参与 FPR/FNR 计算) |
| 重复纠正 | 同一 analysis_id 多次纠正 | 保留最新，旧记录标记为 superseded |

---

## 门闸联动详细规则

### Stage 3.5 动态阈值判定

```python
# 伪代码: 门闸校验逻辑
def gate_check(calibration_db, method_type=None):
    if calibration_db.count < 10:
        return {"status": "⚠️", "message": "校准数据不足(<10条)，建议人工复核"}

    metrics = calibration_db.get_metrics(method_type=method_type)
    checks = {
        "TPR": metrics.TPR >= 0.90,
        "TNR": metrics.TNR >= 0.90,
        "FPR": metrics.FPR <= 0.10,
        "FNR": metrics.FNR <= 0.10,
        "method_match": metrics.method_match_rate >= 0.85,
        "MAPE": metrics.MAPE <= 0.10,
    }

    failed = [k for k, v in checks.items() if not v]
    if len(failed) == 0:
        return {"status": "✅", "message": "全部达标"}
    elif len(failed) <= 2:
        return {"status": "⚠️", "message": f"以下指标未达标: {failed}，建议审查"}
    else:
        return {"status": "❌", "message": f"多项不达标: {failed}，强制人工复核"}
```

### 分方法类型的门闸联动

当校准数据足够(≥20条)时，按方法类型分别评估：

| 方法类型 | 数据量 | TPR | FPR | 门闸状态 |
|---------|--------|-----|-----|---------|
| Logistic 回归 | 15 | 92% | 8% | ✅ |
| Cox 回归 | 8 | 88% | 12% | ⚠️ 数据量不足 |
| t 检验 | 20 | 95% | 5% | ✅ |
| Mann-Whitney | 5 | — | — | ⚠️ 数据不足，无法评估 |

**规则**: 数据量 <10 的方法类型不参与门闸判定，标记为"数据不足"。
