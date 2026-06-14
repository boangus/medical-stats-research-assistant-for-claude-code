"""
psm_template.py — 倾向性评分匹配模板（Python）
=============================================
适用于：观察性研究的因果推断、混杂调整

依赖: numpy, pandas, sklearn, scipy, matplotlib
安装: pip install numpy pandas sklearn scipy matplotlib

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. 倾向性评分估计
# ============================================================================


def estimate_propensity(
    df: pd.DataFrame,
    treatment_col: str,
    covariate_cols: List[str],
    cat_vars: Optional[List[str]] = None,
    model_type: str = "logistic",
) -> pd.DataFrame:
    """估计倾向性评分

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    treatment_col : str
        处理变量（0/1）
    covariate_cols : List[str]
        协变量列表
    cat_vars : Optional[List[str]]
        分类变量
    model_type : str
        模型类型（目前仅支持 'logistic'）

    Returns
    -------
    pd.DataFrame
        包含 PS 得分的原始数据副本
    """
    data = df.copy()
    # 处理分类变量
    if cat_vars:
        data = pd.get_dummies(data, columns=cat_vars, drop_first=True)
        # 更新协变量列表
        all_dummies = [c for c in data.columns
                      if c != treatment_col and
                      any(c.startswith(v) for v in cat_vars) or
                      c in covariate_cols]
        covariate_cols = [
            c for c in data.columns
            if c != treatment_col and c in covariate_cols + all_dummies
        ]

    X = data[covariate_cols].fillna(data[covariate_cols].median())
    y = data[treatment_col]

    if model_type == "logistic":
        ps_model = LogisticRegression(max_iter=1000, random_state=42)
        ps_model.fit(X, y)
        data["ps_score"] = ps_model.predict_proba(X)[:, 1]
        data["logit_ps"] = np.log(data["ps_score"] / (1 - data["ps_score"]))
        data["ps_model"] = "logistic"
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    # c-statistic (AUC)
    from sklearn.metrics import roc_auc_score
    c_stat = roc_auc_score(y, data["ps_score"])
    print(f"  C-statistic: {c_stat:.3f}")

    return data


# ============================================================================
# 2. 最近邻匹配
# ============================================================================


def nearest_neighbor_match(
    data: pd.DataFrame,
    treatment_col: str,
    ps_col: str = "ps_score",
    caliper: Optional[float] = None,
    ratio: int = 1,
    use_logit: bool = True,
) -> pd.DataFrame:
    """最近邻倾向性评分匹配

    Parameters
    ----------
    data : pd.DataFrame
        含 PS 得分的数据
    treatment_col : str
        处理变量
    ps_col : str
        PS 列名
    caliper : Optional[float]
        卡钳值（SD 单位或绝对值）
    ratio : int
        匹配比例
    use_logit : bool
        是否在 logit 尺度上匹配

    Returns
    -------
    pd.DataFrame
        匹配后的数据（含 match_id 列）
    """
    treated = data[data[treatment_col] == 1].reset_index(drop=True)
    control = data[data[treatment_col] == 0].reset_index(drop=True)

    match_var = "logit_ps" if use_logit and "logit_ps" in data.columns else ps_col

    if caliper is not None:
        # 使用 SD 单位
        sd_match = data[match_var].std()
        caliper_val = caliper * sd_match

    # 对每个处理组个体查找最近邻对照
    control_indices = control.index.tolist()
    treated_matches = []

    for i in range(len(treated)):
        treated_ps = treated.loc[i, match_var]
        control_ps = control.loc[control_indices, match_var]

        if control_ps.empty:
            continue

        # 计算距离
        distances = (control_ps - treated_ps).abs()
        best_matches = distances.nsmallest(ratio)

        if caliper is not None:
            best_matches = best_matches[best_matches <= caliper_val]

        for idx, dist in best_matches.items():
            if idx in control_indices:
                treated_matches.append(
                    {"treated_idx": treated.loc[i, "index"] if "index" in treated.columns else i,
                     "control_idx": idx,
                     "distance": dist}
                )
                control_indices.remove(idx)

    # 构建匹配后数据
    matched_rows = []
    for m in treated_matches:
        t_row = treated.loc[m["treated_idx"] if m["treated_idx"] < len(treated) else
                           treated.index[treated["ps_score"] == treated.loc[m["treated_idx"] if m["treated_idx"] < len(treated) else 0, "ps_score"]].tolist()[0]].to_dict()
        c_row = control.loc[m["control_idx"]].to_dict()

        t_row["match_id"] = len(matched_rows) // 2
        t_row["match_group"] = "treated"
        c_row["match_id"] = len(matched_rows) // 2
        c_row["match_group"] = "control"

        matched_rows.append(t_row)
        matched_rows.append(c_row)

    if not matched_rows:
        raise ValueError("No matches found. Try relaxing caliper.")

    matched_df = pd.DataFrame(matched_rows)
    print(f"  匹配前: 处理组 {len(treated)}, 对照组 {len(control)}")
    print(f"  匹配后: {len(matched_df) // 2} 对匹配")

    return matched_df


# ============================================================================
# 3. 平衡诊断
# ============================================================================


def balance_check(
    data: pd.DataFrame,
    treatment_col: str,
    covariate_cols: List[str],
    matched: bool = False,
    weight_col: Optional[str] = None,
) -> pd.DataFrame:
    """检查匹配前后的协变量平衡

    Parameters
    ----------
    data : pd.DataFrame
        数据
    treatment_col : str
        处理变量
    covariate_cols : List[str]
        协变量
    matched : bool
        是否已经匹配
    weight_col : Optional[str]
        权重列（IPTW 用）

    Returns
    -------
    pd.DataFrame
        平衡诊断表（SMD 和方差比）
    """
    treated = data[data[treatment_col] == 1]
    control = data[data[treatment_col] == 0]

    results = []
    for var in covariate_cols:
        t_vals = treated[var].dropna()
        c_vals = control[var].dropna()

        # 计算 SMD
        if t_vals.dtype in ["float64", "int64"]:
            t_mean = t_vals.mean()
            c_mean = c_vals.mean()
            t_var = t_vals.var()
            c_var = c_vals.var()
            pooled_sd = np.sqrt((t_var + c_var) / 2)

            smd = (t_mean - c_mean) / pooled_sd if pooled_sd > 0 else 0
            var_ratio = t_var / c_var if c_var > 0 else np.nan
        else:
            # 分类变量的 SMD（百分比差异）
            t_props = t_vals.value_counts(normalize=True)
            c_props = c_vals.value_counts(normalize=True)
            all_cats = list(set(list(t_props.index) + list(c_props.index)))
            smd = np.sqrt(
                sum((t_props.get(c, 0) - c_props.get(c, 0))**2 for c in all_cats)
            )
            var_ratio = np.nan

        results.append({
            "Variable": var,
            "Treated_Mean": t_mean if 't_mean' in dir() else t_vals.value_counts(normalize=True).iloc[0],
            "Control_Mean": c_mean if 'c_mean' in dir() else c_vals.value_counts(normalize=True).iloc[0],
            "SMD": abs(smd),
            "Var_Ratio": var_ratio,
            "Balance": "✅" if abs(smd) < 0.1 else ("⚠️" if abs(smd) < 0.2 else "❌"),
        })

    return pd.DataFrame(results)


def love_plot(
    balance_before: pd.DataFrame,
    balance_after: pd.DataFrame,
    title: str = "Covariate Balance (Love Plot)",
    figsize: Tuple[float, float] = (8, 6),
) -> plt.Figure:
    """Love Plot: 匹配前后的 SMD 对比"""
    fig, ax = plt.subplots(figsize=figsize)

    y_pos = range(len(balance_before))

    ax.scatter(balance_before["SMD"], y_pos,
               color="red", alpha=0.6, s=40, label="Before Matching")
    ax.scatter(balance_after["SMD"], y_pos,
               color="steelblue", alpha=0.8, s=40, label="After Matching")

    ax.axvline(x=0.1, linestyle="--", color="grey", alpha=0.5, label="SMD=0.1")
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(balance_before["Variable"])
    ax.set_xlabel("Absolute Standardized Mean Difference")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3, linestyle=":")
    ax.invert_yaxis()

    plt.tight_layout()
    return fig


# ============================================================================
# 4. 处理效应估计
# ============================================================================


def estimate_ate(
    matched_data: pd.DataFrame,
    outcome_col: str,
    treatment_col: str,
    method: str = "paired_t",
) -> Dict:
    """估计平均处理效应 (ATE)

    Parameters
    ----------
    matched_data : pd.DataFrame
        匹配后的数据
    outcome_col : str
        结局变量
    treatment_col : str
        处理变量
    method : str
        'paired_t' (配对 t), 'regression' (回归调整+匹配权重),
        'mcnemar' (分类结局)

    Returns
    -------
    Dict
        处理效应估计
    """
    treated = matched_data[matched_data[treatment_col] == 1]
    control = matched_data[matched_data[treatment_col] == 0]

    if method == "paired_t":
        # 配对 t 检验
        paired_data = matched_data.pivot_table(
            index="match_id", columns="match_group",
            values=outcome_col
        )
        t_stat, p_val = stats.ttest_rel(
            paired_data["treated"], paired_data["control"]
        )
        diff = paired_data["treated"].mean() - paired_data["control"].mean()
        n = len(paired_data)

        return {
            "ate": diff,
            "t_statistic": t_stat,
            "p_value": p_val,
            "n_pairs": n,
            "method": "Paired t-test",
            "treated_mean": paired_data["treated"].mean(),
            "control_mean": paired_data["control"].mean(),
        }

    elif method == "regression":
        # 回归调整
        import statsmodels.api as sm
        X = matched_data[[treatment_col]]
        X = sm.add_constant(X)
        y = matched_data[outcome_col]
        model = sm.OLS(y, X).fit()
        return {
            "ate": model.params[treatment_col],
            "se": model.bse[treatment_col],
            "p_value": model.pvalues[treatment_col],
            "ci_lower": model.conf_int().loc[treatment_col, 0],
            "ci_upper": model.conf_int().loc[treatment_col, 1],
            "method": "Regression adjustment",
        }

    else:
        raise ValueError(f"Unsupported method: {method}")


# ============================================================================
# 5. 完整 PSM 工作流
# ============================================================================


def full_psm_workflow(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    covariate_cols: List[str],
    cat_vars: Optional[List[str]] = None,
    caliper: float = 0.2,
    ratio: int = 1,
) -> Dict:
    """完整 PSM 工作流

    步骤: PS 估计 → 匹配 → 平衡诊断 → 效应估计
    """
    results = {}

    # Step 1: PS 估计
    print("=" * 50)
    print("Step 1: 估计倾向性评分")
    print("=" * 50)
    data_ps = estimate_propensity(df, treatment_col, covariate_cols, cat_vars)
    results["ps_data"] = data_ps

    # Step 2: 匹配前平衡诊断
    balance_before = balance_check(df, treatment_col, covariate_cols)
    results["balance_before"] = balance_before

    # Step 3: 匹配
    print("\n" + "=" * 50)
    print("Step 2: 最近邻匹配")
    print("=" * 50)
    matched = nearest_neighbor_match(data_ps, treatment_col,
                                      caliper=caliper, ratio=ratio)
    results["matched_data"] = matched

    # Step 4: 匹配后平衡诊断
    balance_after = balance_check(matched, treatment_col, covariate_cols)
    results["balance_after"] = balance_after

    # Step 5: Love Plot
    if len(balance_before) == len(balance_after):
        results["love_plot"] = love_plot(balance_before, balance_after)

    # Step 6: 效应估计
    print("\n" + "=" * 50)
    print("Step 3: 处理效应估计")
    print("=" * 50)
    ate = estimate_ate(matched, outcome_col, treatment_col)
    results["ate"] = ate

    print(f"  ATE = {ate['ate']:.4f} (p = {ate['p_value']:.4f})")

    return results


if __name__ == "__main__":
    from sklearn.datasets import make_classification

    # 模拟观察性数据
    np.random.seed(42)
    n = 500

    # 协变量
    age = np.random.normal(60, 10, n)
    bmi = np.random.normal(26, 5, n)
    smoking = np.random.binomial(1, 0.3, n)

    # 处理分配（受协变量影响 → 存在混杂）
    logit_treat = -2 + 0.03 * age + 0.05 * bmi + 0.5 * smoking
    prob_treat = 1 / (1 + np.exp(-logit_treat))
    treatment = np.random.binomial(1, prob_treat)

    # 结局（受处理和协变量影响）
    logit_outcome = -3 + 0.5 * treatment + 0.02 * age + 0.04 * bmi + 0.3 * smoking
    prob_outcome = 1 / (1 + np.exp(-logit_outcome))
    outcome = np.random.binomial(1, prob_outcome)

    df = pd.DataFrame({
        "treatment": treatment,
        "outcome": outcome,
        "age": age,
        "bmi": bmi,
        "smoking": smoking,
    })

    # 运行完整 PSM
    results = full_psm_workflow(
        df, treatment_col="treatment", outcome_col="outcome",
        covariate_cols=["age", "bmi", "smoking"],
        caliper=0.2,
    )

    print("\n=== 匹配前平衡诊断 ===")
    print(results["balance_before"].to_string(index=False))

    print("\n=== 匹配后平衡诊断 ===")
    print(results["balance_after"].to_string(index=False))

    print("\n✅ PSM 分析完成")
