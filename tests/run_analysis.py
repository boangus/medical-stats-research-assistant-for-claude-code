"""MSRA Stage 3: Analysis Execution
- Table 1 (by Admission Type)
- ANOVA (Billing Amount ~ Admission Type)
- Logistic Regression (Test Results ~ Age + Gender + Medical Condition + Admission Type)
"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE / "tests/msra_clean.csv")

print("=" * 70)
print("Stage 3 — 分析执行")
print("=" * 70)

# ==============================
# Analysis 1: Table 1
# ==============================
print("\n" + "=" * 70)
print("[分析一] 基线特征表 (Table 1) — 按 Admission Type 分组")
print("=" * 70)

def describe_cont(v):
    return f"{v.mean():.1f} +/- {v.std():.1f}"

def describe_cat(v):
    vc = v.value_counts()
    return "; ".join([f"{k}: {c} ({c/len(v)*100:.1f}%)" for k, c in vc.items()])

for grp in ["Emergency", "Elective", "Urgent"]:
    sub = df[df["Admission Type"] == grp]
    print(f"\n  {grp} (n={len(sub)}):")
    print(f"    Age: {describe_cont(sub['Age'])}")
    print(f"    Billing Amount: ${describe_cont(sub['Billing Amount'])}")
    g = sub["Gender"].value_counts()
    print(f"    Gender: Male {g.get('Male',0)} ({g.get('Male',0)/len(sub)*100:.1f}%), Female {g.get('Female',0)} ({g.get('Female',0)/len(sub)*100:.1f}%)")
    mc = sub["Medical Condition"].value_counts()
    mc_str = ", ".join([f"{k}={c}" for k, c in mc.items()])
    print(f"    Medical Condition: {mc_str}")

# Test for differences across groups (ANOVA)
print("\n" + "-" * 50)
print("组间比较检验 (Admission Type 间)")
groups = [df[df["Admission Type"] == g]["Age"] for g in df["Admission Type"].unique()]
f_stat, p_val = stats.f_oneway(*groups)
print(f"  Age ANOVA: F={f_stat:.3f}, p={p_val:.4f}")

groups_b = [df[df["Admission Type"] == g]["Billing Amount"] for g in df["Admission Type"].unique()]
f_stat_b, p_val_b = stats.f_oneway(*groups_b)
print(f"  Billing Amount ANOVA: F={f_stat_b:.3f}, p={p_val_b:.4f}")

# ==============================
# Analysis 2: ANOVA (Billing Amount ~ Admission Type)
# ==============================
print("\n" + "=" * 70)
print("[分析二] ANOVA — Billing Amount ~ Admission Type")
print("=" * 70)

# ANOVA via scipy already done above — same result
print(f"\n  已通过 scipy 完成: F={f_stat_b:.4f}, p={p_val_b:.4f}")
print(f"  Eta-squared: {f_stat_b * (len(groups_b[0])-1) / (f_stat_b * (len(groups_b[0])-1) + sum(len(g)-1 for g in groups_b)):.4f}")

# ==============================
# Analysis 3: Logistic Regression
# ==============================
print("\n" + "=" * 70)
print("[分析三] Logistic 回归 — Test Results (Normal vs Others)")
print("=" * 70)

# Create binary outcome
df["outcome"] = (df["Test Results"] == "Normal").astype(int)
n_normal = int(df["outcome"].sum())
n_total = len(df)
pct_normal = df["outcome"].mean() * 100
pct_other = (1 - df["outcome"].mean()) * 100
print(f"\n  结局分布: Normal={n_normal} ({pct_normal:.1f}%), Others={n_total - n_normal} ({pct_other:.1f}%)")

# Fit logistic regression
# Fit logistic regression — rename cols with spaces for formula compatibility
df_logit = df.copy()
df_logit.rename(columns={
    "Medical Condition": "MedicalCondition",
    "Admission Type": "AdmissionType",
    "Billing Amount": "BillingAmount",
    "Blood Type": "BloodType",
    "Test Results": "TestResults",
    "Insurance Provider": "InsuranceProvider",
    "Room Number": "RoomNumber",
    "Date of Admission": "DateOfAdmission",
    "Discharge Date": "DischargeDate",
}, inplace=True)

formula = "outcome ~ Age + C(Gender) + C(MedicalCondition) + C(AdmissionType)"
model_logit = smf.logit(formula, data=df_logit).fit(disp=0, maxiter=100)

print(f"\n  Pseudo R-squared (McFadden): {model_logit.prsquared:.4f}")
print(f"  Log-Likelihood: {model_logit.llf:.2f}")
print(f"  AIC: {model_logit.aic:.2f}")
print(f"  BIC: {model_logit.bic:.2f}")

print(f"\n  系数表:")
print(f"  {'变量':<40} {'OR':>8} {'95%CI':<16} {'p':>8}")
print(f"  {'-'*72}")
for name, coef in model_logit.params.items():
    se = model_logit.bse[name]
    or_val = np.exp(coef)
    ci_lo = np.exp(coef - 1.96 * se)
    ci_hi = np.exp(coef + 1.96 * se)
    p = model_logit.pvalues[name]
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  {name:<40} {or_val:>8.3f} ({ci_lo:.3f}-{ci_hi:.3f}) {p:>8.4f} {sig}")

print(f"\n{'='*70}")
print("分析执行完成 ✅")
print(f"{'='*70}")
