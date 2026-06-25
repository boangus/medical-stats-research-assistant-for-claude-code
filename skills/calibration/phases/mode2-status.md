# Mode 2: 状态查看 (Status)

> 来源：从 `skills/calibration/SKILL.md` L318-357 抽取。保留原文完整性，语义等价。

> **🔴[MANDATORY] status**: [SLIM] 展示状态摘要，自动继续

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
