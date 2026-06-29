# 门闸联动详细规则

> 来源：从 `skills/calibration/SKILL.md` L752-795 抽取。保留原文完整性，语义等价。
> 本文件描述 Stage 3.5 动态阈值判定的详细规则和分方法类型联动。

## Stage 3.5 动态阈值判定

```python
# 伪代码: 门闸校验逻辑
def gate_check(calibration_db, method_type=None):
    if calibration_db.count < 10:
        return {"status": "⚠️", "message": "校准数据不足(<10条)，必须人工复核"}

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
        return {"status": "⚠️", "message": f"以下指标未达标: {failed}，必须审查"}
    else:
        return {"status": "❌", "message": f"多项不达标: {failed}，强制人工复核"}
```

## 分方法类型的门闸联动

当校准数据足够(≥20条)时，按方法类型分别评估：

| 方法类型 | 数据量 | TPR | FPR | 门闸状态 |
|---------|--------|-----|-----|---------|
| Logistic 回归 | 15 | 92% | 8% | ✅ |
| Cox 回归 | 8 | 88% | 12% | ⚠️ 数据量不足 |
| t 检验 | 20 | 95% | 5% | ✅ |
| Mann-Whitney | 5 | — | — | ⚠️ 数据不足，无法评估 |

**规则**: 数据量 <10 的方法类型不参与门闸判定，标记为"数据不足"。
