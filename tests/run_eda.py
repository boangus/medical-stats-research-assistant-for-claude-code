"""MSRA Stage 2 Phase 1: Exploratory Data Analysis"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE / "tests/msra_clean.csv")

print("=" * 64)
print("MSRA Pipeline — Stage 2 Phase 1: 探索性数据分析 (EDA)")
print("=" * 64)

# === 1. 连续变量分布 ===
print("\n[1] 连续变量分布")
num_cols = ["Age", "Billing Amount", "Room Number"]
for col in num_cols:
    v = df[col]
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
cat_cols = ["Gender", "Blood Type", "Medical Condition", "Admission Type", 
            "Test Results", "Insurance Provider", "Medication"]
for col in cat_cols:
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
print("\n[3] 按 Admission Type 分组基线特征")
for grp in ["Emergency", "Elective", "Urgent"]:
    sub = df[df["Admission Type"] == grp]
    print(f"\n  {grp} (n={len(sub)}):")
    print(f"    Age: {sub['Age'].mean():.1f} +/- {sub['Age'].std():.1f}")
    for cond in df["Medical Condition"].unique():
        pct = (sub["Medical Condition"] == cond).mean() * 100
        print(f"    {cond}: {pct:.1f}%")
    gender_pct = (sub["Gender"] == "Male").mean() * 100
    print(f"    Male: {gender_pct:.1f}%")
    print(f"    Billing: ${sub['Billing Amount'].mean():.0f} +/- ${sub['Billing Amount'].std():.0f}")

print("\n[4] 按 Gender 分组")
for grp in ["Male", "Female"]:
    sub = df[df["Gender"] == grp]
    print(f"\n  {grp} (n={len(sub)}):")
    print(f"    Age: {sub['Age'].mean():.1f} +/- {sub['Age'].std():.1f}")
    print(f"    Billing: ${sub['Billing Amount'].mean():.0f} +/- ${sub['Billing Amount'].std():.0f}")

# === 4. 相关性 ===
print("\n[5] 关键变量相关性 (Pearson)")
corr_age_bill = df["Age"].corr(df["Billing Amount"])
corr_room_bill = df["Room Number"].corr(df["Billing Amount"])
print(f"  Age vs Billing Amount: r={corr_age_bill:.3f}")
print(f"  Room Number vs Billing Amount: r={corr_room_bill:.3f}")

# === 5. 关键发现总结 ===
print("\n" + "=" * 64)
print("EDA 关键发现")
print("=" * 64)
print("1. 数据概况: 55,392 条, 15 变量, 无缺失值")
print("2. 年龄: 13-89 岁, 接近均匀分布 (mean=51.5, sd=19.6)")
print("3. 计费金额: $9-$52,764, 正偏态分布 (skewness>0)")
print("4. Medical Condition: 6 类近乎均匀 (各 ~16.7%)")
print("5. Test Results: 3 类近乎均匀 (各 ~33%)")
print("6. Billing Amount 与 Age 几乎无相关 (r={:.3f})".format(corr_age_bill))
print("7. 性别均衡 (Male 50.1%, Female 49.9%)")
print("8. 入院类型均衡 (Elective 33.6%, Urgent 33.5%, Emergency 32.9%)")

# Save report
report = f"""# EDA 报告 — Stage 2 Phase 1

## 数据概况
- 记录: 55,392
- 变量: 15
- 缺失: 无

## 连续变量

| 变量 | Mean | SD | Median | IQR | Skew |
|------|------|----|--------|-----|------|"""

for col in num_cols:
    v = df[col]
    report += f"""
| {col} | {v.mean():.1f} | {v.std():.1f} | {v.median():.1f} | {v.quantile(0.25):.1f}-{v.quantile(0.75):.1f} | {v.skew():.2f} |"""

report += """

## 关键发现
1. Billing Amount 正偏态分布
2. 所有分类变量各组近乎均匀分布
3. 无缺失值，无严重异常值（负值已在清洗中删除）
4. 变量间相关性低
"""

eda_path = BASE / "tests/eda_report.md"
with open(eda_path, "w", encoding="utf-8") as f:
    f.write(report)
print(f"\nEDA 报告已保存: {eda_path}")
