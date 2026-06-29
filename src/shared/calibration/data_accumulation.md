# 真实校准数据积累机制

> 来源：从 `skills/calibration/SKILL.md` L577-621 抽取。保留原文完整性，语义等价。
> 核心问题：合成金标准无法替代真实校准数据。以下机制从用户实际使用中逐步积累校准数据。

## 积累路径

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

## 纠正触发条件

| 场景 | 触发方式 | 校准类型 |
|------|---------|---------|
| 用户主动纠正 | "这个OR不对，应该是..." | conclusion_error / numeric_error |
| QC Inspector 发现偏差 | Stage 3.5 门闸标记异常 | method_error |
| 同行审稿反馈 | 用户输入审稿意见 | method_error / conclusion_error |
| 已发表论文对比 | 用户提供论文中的标准结果 | 全维度校准 |

## 校准数据质量控制

| 检查项 | 阈值 | 处理 |
|--------|------|------|
| 纠正来源完整性 | 必须标注 source | 缺失 → 提示用户补充 |
| 时间顺序 | 纠正时间 > 分析时间 | 违反 → 标记为异常记录 |
| 纠正幅度 | 数值偏差 > 10% 才记录 | <10% → 标记为"微调"(不参与 FPR/FNR 计算) |
| 重复纠正 | 同一 analysis_id 多次纠正 | 保留最新，旧记录标记为 superseded |
