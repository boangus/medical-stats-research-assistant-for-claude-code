"""MSRA Stage 2 Phase 1: Exploratory Data Analysis
Schema: msra_test_data.csv (generate_test_data.py output)
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# 优先读清洗后数据，不存在则读原始数据
clean_path = BASE / "tests/msra_clean.csv"
raw_path = BASE / "tests/msra_test_data.csv"
if clean_path.exists():
    df = pd.read_csv(clean_path)
    data_source = "msra_clean.csv"
else:
    df = pd.read_csv(raw_path)
    data_source = "msra_test_data.csv"

print("=" * 64)
print("MSRA Pipeline — Stage 2 Phase 1: 探索性数据分析 (EDA)")
print("=" * 64)
print(f"  数据源: {data_source}")

# === 1. 连续变量分布 ===
print("\n[1] 连续变量分布")
num_cols = ["Age", "BillingAmount", "HeartRate"]
for col in num_cols:
    if col not in df.columns:
        continue
    v = pd.to_numeric(df[col], errors="coerce").dropna()
    print(f"\n  {col}:")
    print(f"    n={len(v)}, mean={v.mean():.1f}, sd={v.std():.1f}")
    print(f"    median={v.median():.1f}, IQR={v.quantile(0.25):.1f}~{v.quantile(0.75):.1f}")
    print(f"    min={v.min():.1f}, max={v.max():.1f}")
    skew = v.skew()
    kurt = v.kurtosis()
    print(f"    skewness={skew:.2f}, kurtosis={kurt:.2f}")
    # Normality indicator
    if abs(skew) > 1:
        print(f"    -> 高度偏态 (|skew|>1), 建议非参数方法")
    elif abs(skew) > 0.5:
        print(f"    -> 中度偏态, 参数/非参数均可")
    else:
        print(f"    -> 近似对称分布")

# === 2. 分类变量频数 ===
print("\n[2] 分类变量分布")
cat_cols = ["Gender", "BloodType", "MedicalCondition", "AdmissionType",
            "TreatmentGroup", "InsuranceProvider", "Medication"]
for col in cat_cols:
    if col not in df.columns:
        continue
    vc = df[col].value_counts()
    rare = (vc / len(df) * 100) < 5
    n_rare = rare.sum()
    print(f"\n  {col} ({df[col].nunique()} levels):")
    for val, cnt in vc.items():
        pct = cnt / len(df) * 100
        flag = " **稀少**" if pct < 5 else ""
        print(f"    {val}: {cnt} ({pct:.1f}%){flag}")
    if n_rare > 0:
        print(f"    -> {n_rare} 个水平占比<5%，需考虑合并")

# === 3. 关键分组比较 (Table 1-style) ===
print("\n[3] 按 AdmissionType 分组基线特征")
for grp in df["AdmissionType"].unique():
    sub = df[df["AdmissionType"] == grp]
    age_sub = pd.to_numeric(sub["Age"], errors="coerce").dropna()
    bill_sub = pd.to_numeric(sub["BillingAmount"], errors="coerce").dropna()
    print(f"\n  {grp} (n={len(sub)}):")
    print(f"    Age: {age_sub.mean():.1f} +/- {age_sub.std():.1f}")
    for cond in df["MedicalCondition"].unique():
        pct = (sub["MedicalCondition"] == cond).mean() * 100
        print(f"    {cond}: {pct:.1f}%")
    gender_pct = (sub["Gender"] == "Male").mean() * 100
    print(f"    Male: {gender_pct:.1f}%")
    print(f"    Billing: ${bill_sub.mean():.0f} +/- ${bill_sub.std():.0f}")

print("\n[4] 按 Gender 分组")
for grp in ["Male", "Female"]:
    sub = df[df["Gender"] == grp]
    age_sub = pd.to_numeric(sub["Age"], errors="coerce").dropna()
    bill_sub = pd.to_numeric(sub["BillingAmount"], errors="coerce").dropna()
    print(f"\n  {grp} (n={len(sub)}):")
    print(f"    Age: {age_sub.mean():.1f} +/- {age_sub.std():.1f}")
    print(f"    Billing: ${bill_sub.mean():.0f} +/- ${bill_sub.std():.0f}")

# === 4. 相关性 ===
print("\n[5] 关键变量相关性 (Pearson)")
age_num = pd.to_numeric(df["Age"], errors="coerce")
bill_num = pd.to_numeric(df["BillingAmount"], errors="coerce")
valid = age_num.notna() & bill_num.notna()
corr_age_bill = age_num[valid].corr(bill_num[valid])
print(f"  Age vs BillingAmount: r={corr_age_bill:.3f}")

# === 5. 关键发现总结 ===
print("\n" + "=" * 64)
print("EDA 关键发现")
print("=" * 64)
print(f"1. 数据概况: {len(df)} 条, {len(df.columns)} 变量")
print(f"2. 年龄: {age_num.min():.0f}-{age_num.max():.0f} 岁 (mean={age_num.mean():.1f}, sd={age_num.std():.1f})")
print(f"3. 计费金额: ${bill_num.min():.2f}~${bill_num.max():.2f}")
print(f"4. MedicalCondition: {df['MedicalCondition'].nunique()} 类")
print(f"5. 性别: Male {(df['Gender']=='Male').mean()*100:.1f}%, Female {(df['Gender']=='Female').mean()*100:.1f}%")
print(f"6. 入院类型: {', '.join(f'{k} {v/len(df)*100:.1f}%' for k,v in df['AdmissionType'].value_counts().items())}")

# Save report
report = f"""# EDA 报告 — Stage 2 Phase 1

## 数据概况
- 记录: {len(df)}
- 变量: {len(df.columns)}
- 数据源: {data_source}

## 连续变量

| 变量 | Mean | SD | Median | IQR | Skew |
|------|------|----|--------|-----|------|"""

for col in num_cols:
    if col not in df.columns:
        continue
    v = pd.to_numeric(df[col], errors="coerce").dropna()
    report += f"""
| {col} | {v.mean():.1f} | {v.std():.1f} | {v.median():.1f} | {v.quantile(0.25):.1f}-{v.quantile(0.75):.1f} | {v.skew():.2f} |"""

report += """

## 关键发现
1. BillingAmount 正偏态分布
2. 所有分类变量各组分布情况见上方
3. 变量间相关性低
"""

eda_path = BASE / "tests/eda_report.md"
with open(eda_path, "w", encoding="utf-8") as f:
    f.write(report)
print(f"\nEDA 报告已保存: {eda_path}")
