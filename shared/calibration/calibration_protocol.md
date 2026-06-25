# 校准协议：与 Pipeline 集成

> 来源：从 `skills/calibration/SKILL.md` L423-461 抽取。保留原文完整性，语义等价。
> 本文件描述 Calibration Skill 与 Pipeline Orchestrator 的集成协议。

## QC Inspector 自动反馈

Stage 3.5 质量门闸后，QC Inspector 自动记录：

```python
# 用户纠正分析结果时自动触发
calibration_db.record(
    msra_result=original_output,
    gold_result=user_correction,
    source="user_feedback"
)
```

## 门闸动态阈值

校准指标影响 Pipeline 质量门闸的判定：

```
Stage 3.5 结果质量门闸:
  静态检查 (现有8项) + 动态校准检查 (新增):
    - 该方法类型的历史 TPR ≥ 90%? → ✅ 信任 / ⚠️ 需审查
    - 该方法类型的历史 FPR ≤ 10%? → ✅ 信任 / ⚠️ 需审查
    - 校准数据不足 (<10条)? → ⚠️ 无法评估，必须人工复核
```

## Anti-Pattern 验证

校准数据验证反模式规则的有效性：

```
anti-pattern A1 "正态性假定默认化":
  → 校准数据: 非正态场景方法选择错误率 = ?
  → 若 > 15%: A1 规则有效，需加强防御
  → 若 < 5%: A1 规则可降低优先级
```
