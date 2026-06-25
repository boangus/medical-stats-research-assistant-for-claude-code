# Mode 3: 增量更新 (Incremental Update)

> 来源：从 `skills/calibration/SKILL.md` L358-397 抽取。保留原文完整性，语义等价。

> **🔴[MANDATORY] update**: [MANDATORY] 更新校准数据库前必须确认

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
