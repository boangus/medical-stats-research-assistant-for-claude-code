"""MSRA Stage 1 Phase 3: Data Cleaning (建议模式)
Schema: msra_test_data.csv (generate_test_data.py output)

注意：此脚本生成清洗建议，不自动执行删除。
实际清洗需用户确认后执行。
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "tests/msra_test_data.csv"
df = pd.read_csv(DATA)
n_before = len(df)

print("=" * 56)
print("MSRA Pipeline — Stage 1 Phase 3: 数据清洗（建议模式）")
print("=" * 56)

# === 1. 检测负值计费 (schema: BillingAmount) ===
billing_col = pd.to_numeric(df["BillingAmount"], errors="coerce")
neg_mask = billing_col < 0
n_neg = int(neg_mask.sum())
neg_rows = df[neg_mask][["PatientID", "BillingAmount"]]
print(f"\n[1] 负值计费检测")
print(f"  检出: {n_neg} 条")
if n_neg > 0:
    for _, row in neg_rows.iterrows():
        print(f"    {row['PatientID']}: {row['BillingAmount']}")

# === 2. 检测不可能年龄 (schema: Age) ===
age_col = pd.to_numeric(df["Age"], errors="coerce")
impossible_age = df[(age_col < 0) | (age_col > 120)]
print(f"\n[2] 不可能年龄检测")
print(f"  检出: {len(impossible_age)} 条")
for _, row in impossible_age.iterrows():
    print(f"    {row['PatientID']}: Age={row['Age']}")

# === 3. 检测逗号多值 (schema: BillingAmount) ===
comma_billing = df[df["BillingAmount"].astype(str).str.contains(",", na=False)]
print(f"\n[3] 逗号多值检测")
print(f"  检出: {len(comma_billing)} 条")
for _, row in comma_billing.iterrows():
    print(f"    {row['PatientID']}: BillingAmount={row['BillingAmount']}")

# === 4. 检测无效血型 (schema: BloodType) ===
VALID_BLOOD = {"A+","A-","B+","B-","AB+","AB-","O+","O-"}
invalid_bt = df[~df["BloodType"].isin(VALID_BLOOD)]
print(f"\n[4] 无效血型检测")
print(f"  检出: {len(invalid_bt)} 条")
for _, row in invalid_bt.iterrows():
    print(f"    {row['PatientID']}: BloodType={row['BloodType']}")

# === 5. 检测日期逻辑错误 (schema: AdmissionDate, DischargeDate) ===
df["admit_dt"] = pd.to_datetime(df["AdmissionDate"], errors="coerce")
df["discharge_dt"] = pd.to_datetime(df["DischargeDate"], errors="coerce")
date_err = df[df["discharge_dt"] < df["admit_dt"]]
print(f"\n[5] 日期逻辑错误")
print(f"  出院早于入院: {len(date_err)} 条")
for _, row in date_err.iterrows():
    print(f"    {row['PatientID']}: {row['AdmissionDate']} -> {row['DischargeDate']}")

# === 生成清洗建议 ===
suggestions = []
if n_neg > 0:
    suggestions.append(f"删除 {n_neg} 条负值计费记录")
if len(impossible_age) > 0:
    suggestions.append(f"标记 {len(impossible_age)} 条不可能年龄记录为缺失")
if len(comma_billing) > 0:
    suggestions.append(f"拆分 {len(comma_billing)} 条逗号多值记录")
if len(invalid_bt) > 0:
    suggestions.append(f"将 {len(invalid_bt)} 条无效血型标记为缺失")
if len(date_err) > 0:
    suggestions.append(f"标记 {len(date_err)} 条日期逻辑错误记录")

print(f"\n{'=' * 56}")
print(f"清洗建议（需用户确认后执行）")
print(f"{'=' * 56}")
if suggestions:
    for i, s in enumerate(suggestions, 1):
        print(f"  {i}. {s}")
else:
    print("  无需清洗操作")

# === 保存清洗建议 ===
log = f"""# 数据清洗建议 — Stage 1 Phase 3

## 检测结果

| 检查项 | 检出数 | 操作建议 |
|--------|--------|----------|
| 负值计费 | {n_neg} | 删除 |
| 不可能年龄 | {len(impossible_age)} | 标记为缺失 |
| 逗号多值 | {len(comma_billing)} | 拆分 |
| 无效血型 | {len(invalid_bt)} | 标记为缺失 |
| 日期逻辑错误 | {len(date_err)} | 标记 |

## 清洗后预期

| 指标 | 当前 | 清洗后（预估） |
|------|------|----------------|
| 总记录数 | {n_before} | {n_before - n_neg}（仅删除负值计费） |

## 待用户确认

请确认以上清洗操作后，再执行实际清洗。
"""

log_path = str(BASE / "tests/cleaning_log.md")
with open(log_path, "w", encoding="utf-8") as f:
    f.write(log)
print(f"\n清洗建议已保存: {log_path}")
