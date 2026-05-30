"""MSRA Stage 1 Phase 3: Execute cleaning"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE / "tests/msra_test_data.csv")
n_before = len(df)

# Clean: remove negative billing
neg_mask = df["Billing Amount"] < 0
n_neg = int(neg_mask.sum())
df_clean = df[~neg_mask].copy()

print(f"清洗前记录: {n_before}")
print(f"删除负值计费: {n_neg} 条")
print(f"清洗后记录: {len(df_clean)}")
print(f"计费金额范围: ${df_clean['Billing Amount'].min():.2f} ~ ${df_clean['Billing Amount'].max():.2f}")

# Save cleaned data
clean_csv = str(BASE / "tests/msra_clean.csv")
df_clean.to_csv(clean_csv, index=False)
print(f"\n清洗后数据: {clean_csv}")

# Cleaning log
log = f"""# 清洗日志

## 操作记录

| 时间 | 操作 | 影响记录 | 原因 |
|------|------|---------|------|
| Stage1-Phase3 | 删除负值计费 | {n_neg} 条 | 负值无临床合理性 |

## 数据变更摘要

| 指标 | 清洗前 | 清洗后 | 变更 |
|------|--------|--------|------|
| 总记录数 | {n_before} | {len(df_clean)} | -{n_neg} |
| Billing Amount 最小值 | ${df['Billing Amount'].min():.2f} | ${df_clean['Billing Amount'].min():.2f} | 负值已清除 |
| Billing Amount 最大值 | ${df['Billing Amount'].max():.2f} | ${df_clean['Billing Amount'].max():.2f} | 不变 |

## 保留的项目
- 姓名: 原始大小写（用户确认保留）
- 年龄 < 18: 保留（用户确认保留）
"""

log_path = str(BASE / "tests/cleaning_log.md")
with open(log_path, "w", encoding="utf-8") as f:
    f.write(log)
print(f"清洗日志: {log_path}")
