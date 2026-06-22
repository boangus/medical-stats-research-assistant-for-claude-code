"""MSRA Stage 3: Analysis Execution
Schema: msra_test_data.csv (generate_test_data.py output)

- Table 1 (by AdmissionType)
- ANOVA (BillingAmount ~ AdmissionType)
- Logistic Regression (Outcome ~ Age + Gender + MedicalCondition + AdmissionType)
"""
import pandas as pd
import numpy as np
from scipy import stats
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

print("=" * 70)
print("Stage 3 — 分析执行")
print("=" * 70)
print(f"  数据源: {data_source}")

# ==============================
# Analysis 1: Table 1
# ==============================
print("\n" + "=" * 70)
print("[分析一] 基线特征表 (Table 1) — 按 AdmissionType 分组")
print("=" * 70)

def describe_cont(v):
    v = pd.to_numeric(v, errors="coerce").dropna()
    return f"{v.mean():.1f} +/- {v.std():.1f}"

for grp in df["AdmissionType"].unique():
    sub = df[df["AdmissionType"] == grp]
    print(f"\n  {grp} (n={len(sub)}):")
    print(f"    Age: {describe_cont(sub['Age'])}")
    print(f"    BillingAmount: ${describe_cont(sub['BillingAmount'])}")
    g = sub["Gender"].value_counts()
    print(f"    Gender: Male {g.get('Male',0)} ({g.get('Male',0)/len(sub)*100:.1f}%), Female {g.get('Female',0)} ({g.get('Female',0)/len(sub)*100:.1f}%)")
    mc = sub["MedicalCondition"].value_counts()
    mc_str = ", ".join([f"{k}={c}" for k, c in mc.items()])
    print(f"    MedicalCondition: {mc_str}")

# Test for differences across groups (ANOVA)
print("\n" + "-" * 50)
print("组间比较检验 (AdmissionType 间)")
age_num = pd.to_numeric(df["Age"], errors="coerce")
bill_num = pd.to_numeric(df["BillingAmount"], errors="coerce")

groups_age = [age_num[df["AdmissionType"] == g].dropna() for g in df["AdmissionType"].unique()]
f_stat, p_val = stats.f_oneway(*groups_age)
print(f"  Age ANOVA: F={f_stat:.3f}, p={p_val:.4f}")

groups_bill = [bill_num[df["AdmissionType"] == g].dropna() for g in df["AdmissionType"].unique()]
f_stat_b, p_val_b = stats.f_oneway(*groups_bill)
print(f"  BillingAmount ANOVA: F={f_stat_b:.3f}, p={p_val_b:.4f}")

# ==============================
# Analysis 2: ANOVA (BillingAmount ~ AdmissionType)
# ==============================
print("\n" + "=" * 70)
print("[分析二] ANOVA — BillingAmount ~ AdmissionType")
print("=" * 70)

# Eta-squared
ss_between = sum(len(g) * (g.mean() - bill_num.dropna().mean())**2 for g in groups_bill)
ss_total = sum((bill_num.dropna() - bill_num.dropna().mean())**2)
eta_sq = ss_between / ss_total if ss_total > 0 else 0
print(f"\n  已通过 scipy 完成: F={f_stat_b:.4f}, p={p_val_b:.4f}")
print(f"  Eta-squared: {eta_sq:.4f}")

# ==============================
# Analysis 3: Logistic Regression
# ==============================
print("\n" + "=" * 70)
print("[分析三] Logistic 回归 — Outcome (改善 vs 其他)")
print("=" * 70)

# Create binary outcome (schema: Outcome = "改善"/"稳定"/"进展"/"")
df["outcome_binary"] = (df["Outcome"] == "改善").astype(int)
n_positive = int(df["outcome_binary"].sum())
n_total = df["outcome_binary"].notna().sum()
pct_pos = df["outcome_binary"].mean() * 100
pct_neg = (1 - df["outcome_binary"].mean()) * 100
print(f"\n  结局分布: 改善={n_positive} ({pct_pos:.1f}%), 其他={n_total - n_positive} ({pct_neg:.1f}%)")

# Fit logistic regression if statsmodels available
try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    # Prepare data
    df_logit = df[df["outcome_binary"].notna()].copy()
    df_logit["outcome"] = df_logit["outcome_binary"].astype(int)

    # Rename for formula
    df_logit.rename(columns={
        "MedicalCondition": "MedicalCondition",
        "AdmissionType": "AdmissionType",
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
except ImportError:
    print("\n  [WARN] statsmodels 未安装，跳过 Logistic 回归")
    print("  安装: pip install statsmodels")
except Exception as e:
    print(f"\n  [WARN] Logistic 回归失败: {e}")

print(f"\n{'='*70}")
print("分析执行完成 [DONE]")
print(f"{'='*70}")
