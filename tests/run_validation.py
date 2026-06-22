"""MSRA Stage 1 Phase 1: Data Validation
Schema: msra_test_data.csv (generate_test_data.py output)
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "tests/msra_test_data.csv"
OUT = BASE / "tests/validation_report_stage1.md"

df = pd.read_csv(DATA)
issues = {"critical": [], "warning": [], "info": []}

print("=" * 56)
print("MSRA Pipeline — Stage 1 Phase 1: 数据验证报告")
print("=" * 56)

# === 1. 结构检查 ===
print(f"\n[1] 结构检查")
print(f"  行数: {len(df):,}")
print(f"  列数: {len(df.columns)}")
print(f"  列名: {list(df.columns)}")

name_pct = df["Name"].nunique() / len(df)
print(f"  姓名唯一值: {df['Name'].nunique():,}/{len(df):,} ({name_pct:.1%})")
if name_pct < 0.8:
    issues["info"].append(f"Name唯一值比例较低 ({name_pct:.1%})，可能有重复患者")
else:
    issues["info"].append(f"Name唯一值比例适中 ({name_pct:.1%})")

if len(df.columns) != len(set(df.columns)):
    issues["critical"].append("存在重复列名")

# === 2. 数据类型 ===
print(f"\n[2] 数据类型")
for col in df.columns:
    dtype = df[col].dtype
    has_null = df[col].isnull().sum()
    print(f"  {col}: {dtype}" + (f" (缺失: {has_null})" if has_null else ""))

# Try parsing dates (schema: AdmissionDate, DischargeDate)
for col in ["AdmissionDate", "DischargeDate"]:
    try:
        pd.to_datetime(df[col])
        print(f"  {col}: 日期格式可解析 ✅")
    except Exception:
        issues["warning"].append(f"{col} 日期格式不可解析")

# === 3. 缺失数据评估 ===
print(f"\n[3] 缺失数据评估")
missing = df.isnull().sum()
missing_pct = missing[missing > 0]
if len(missing_pct) == 0:
    print("  无缺失值 ✅")
    issues["info"].append("所有变量均无缺失值")
else:
    for col, cnt in missing_pct.items():
        pct = cnt / len(df) * 100
        level = "critical" if pct > 50 else "warning"
        issues[level].append(f"{col}: {cnt}条缺失 ({pct:.1f}%)")
        print(f"  {col}: {cnt}条 ({pct:.1f}%)")

# === 4. 逻辑一致性 ===
print(f"\n[4] 逻辑一致性检查")

# 4a. 日期顺序 (schema: AdmissionDate, DischargeDate)
df["admit_dt"] = pd.to_datetime(df["AdmissionDate"])
df["discharge_dt"] = pd.to_datetime(df["DischargeDate"])
date_errors = (df["discharge_dt"] < df["admit_dt"]).sum()
if date_errors > 0:
    issues["critical"].append(f"出院日期早于入院日期: {date_errors}条")
    print(f"  [CRITICAL] 出院 < 入院: {date_errors}条")
else:
    print(f"  [OK] 所有出院日期 >= 入院日期")

same_day = (df["discharge_dt"] == df["admit_dt"]).sum()
print(f"  [INFO] 同一天出入院: {same_day}条 ({same_day/len(df)*100:.1f}%)")

df["los"] = (df["discharge_dt"] - df["admit_dt"]).dt.days
print(f"  住院天数: 中位数={df['los'].median():.0f}, IQR={df['los'].quantile(0.25):.0f}~{df['los'].quantile(0.75):.0f}")
print(f"  范围: {df['los'].min()}~{df['los'].max()}")

# 4b. 年龄
age_col = pd.to_numeric(df["Age"], errors="coerce")
age_min, age_max = age_col.min(), age_col.max()
print(f"  年龄范围: {age_min}~{age_max}")
if age_min < 0:
    issues["critical"].append(f"负值年龄: {age_min}")
elif age_min < 18:
    issues["warning"].append(f"年龄下限 {age_min} 岁，低于成人标准")
if age_max > 120:
    issues["warning"].append(f"年龄上限 {age_max} 岁，超出合理范围")

# 4c. 计费金额 (schema: BillingAmount)
billing_col = pd.to_numeric(df["BillingAmount"], errors="coerce")
neg_billing = (billing_col < 0).sum()
if neg_billing > 0:
    neg_min = billing_col[billing_col < 0].min()
    neg_max = billing_col[billing_col < 0].max()
    issues["warning"].append(f"负值计费金额: {neg_billing}条 (${neg_min:.2f} ~ ${neg_max:.2f})")
    print(f"  [WARNING] 负值计费金额: {neg_billing}条 (${neg_min:.2f} ~ ${neg_max:.2f})")

# 4d. 姓名大小写
names_with_issues = 0
for n in df["Name"].sample(min(1000, len(df))):
    if n != n.title():
        names_with_issues += 1
if names_with_issues > 50:
    issues["warning"].append(f"样本中有 {names_with_issues}个姓名大小写不一致（抽样1,000条中）")
    print(f"  [WARNING] 姓名大小写不一致（抽样检查）")

# === 5. 范围检查 ===
print(f"\n[5] 范围检查")
print(f"  Age: {age_col.min()}~{age_col.max()} (mean={age_col.mean():.1f})")
print(f"  BillingAmount: ${billing_col.min():.2f}~${billing_col.max():.2f}")

# === 分类变量 ===
print(f"\n分类变量分布:")
cat_cols = ["Gender", "BloodType", "MedicalCondition", "AdmissionType",
            "TreatmentGroup", "InsuranceProvider"]
for col in cat_cols:
    if col in df.columns:
        vc = df[col].value_counts()
        print(f"\n  {col} ({df[col].nunique()} unique):")
        for val, cnt in vc.items():
            print(f"    {val}: {cnt} ({cnt/len(df)*100:.1f}%)")

# === 汇总 ===
print(f"\n{'=' * 56}")
print(f"验证报告摘要")
print(f"{'=' * 56}")
print(f"\n[CRITICAL] (必须修复):")
for i in issues["critical"]:
    print(f"  - {i}")
print(f"\n[WARNING] (应该处理):")
for i in issues["warning"]:
    print(f"  - {i}")
print(f"\n[INFO] (参考):")
for i in issues["info"]:
    print(f"  - {i}")

# Write report file
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# 数据验证报告 — Stage 1 Phase 1\n\n")
    f.write(f"| 项目 | 值 |\n|------|-----|\n")
    f.write(f"| 数据文件 | `msra_test_data.csv` |\n")
    f.write(f"| 记录数 | {len(df):,} |\n")
    f.write(f"| 变量数 | {len(df.columns)} |\n")
    f.write(f"| 缺失值 | 见下方 |\n")
    f.write(f"| 检查时间 | Phase 1 自动完成 |\n\n")
    f.write(f"## 发现问题\n\n")
    f.write(f"### 🔴 Critical ({len(issues['critical'])})\n")
    for i in issues["critical"]:
        f.write(f"- {i}\n")
    f.write(f"\n### 🟡 Warning ({len(issues['warning'])})\n")
    for i in issues["warning"]:
        f.write(f"- {i}\n")
    f.write(f"\n### 🔵 Info ({len(issues['info'])})\n")
    for i in issues["info"]:
        f.write(f"- {i}\n")

print(f"\n报告已保存: {OUT}")
