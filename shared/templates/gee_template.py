"""
gee_template.py — GEE 广义估计方程分析模板
============================================
适用于：纵向/聚类数据的 GEE 分析，如重复测量、群组随机化试验、多中心研究

依赖: statsmodels, pandas, numpy, scipy, matplotlib
安装: pip install statsmodels pandas numpy scipy matplotlib

参考:
  Zeger & Liang (1986) Biometrics: Longitudinal data analysis
  statsmodels GEE docs: https://www.statsmodels.org/stable/gee.html

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.genmod.generalized_estimating_equations import GEEResults
from statsmodels.genmod.families import Binomial, Gaussian, Poisson
from statsmodels.genmod.cov_struct import (
    Exchangeable,
    AR1,
    Independence,
)

warnings.filterwarnings("ignore")

# ============================================================================
# 1. GEE 模型拟合
# ============================================================================

FAMILY_MAP = {
    "gaussian": Gaussian,
    "binomial": Binomial,
    "poisson": Poisson,
}

COV_STRUCT_MAP = {
    "exchangeable": Exchangeable,
    "ar1": AR1,
    "independence": Independence,
}


def fit_gee(
    data: pd.DataFrame,
    formula: str,
    groups: str,
    family: str = "gaussian",
    cov_struct: str = "exchangeable",
    time: Optional[str] = None,
) -> GEEResults:
    """拟合 GEE 模型

    使用 statsmodels GEE 类拟合广义估计方程模型。
    支持 gaussian、binomial、poisson 分布族，以及 exchangeable、
    ar1、independence 协方差结构。

    Parameters
    ----------
    data : pd.DataFrame
        长格式数据框，每行一个观测
    formula : str
        patsy 公式，如 'outcome ~ trt + time + age'
    groups : str
        聚类/个体标识变量名
    family : str
        分布族名称，可选: 'gaussian', 'binomial', 'poisson'
    cov_struct : str
        协方差结构名称，可选: 'exchangeable', 'ar1', 'independence'
    time : Optional[str]
        时间/波次变量名，ar1 结构需要；数据将按 (groups, time) 排序

    Returns
    -------
    GEEResults
        GEE 拟合结果对象

    Raises
    ------
    ValueError
        当 family 或 cov_struct 不在支持范围内

    Examples
    --------
    >>> model = fit_gee(data, 'outcome ~ trt + time', groups='id',
    ...                 family='binomial', cov_struct='exchangeable')
    """
    # 验证参数
    if family not in FAMILY_MAP:
        raise ValueError(
            f"family 必须为以下之一: {list(FAMILY_MAP.keys())}"
        )
    if cov_struct not in COV_STRUCT_MAP:
        raise ValueError(
            f"cov_struct 必须为以下之一: {list(COV_STRUCT_MAP.keys())}"
        )

    # 排序（ar1 需要时间顺序）
    df = data.copy()
    if time is not None:
        df = df.sort_values([groups, time]).reset_index(drop=True)
    elif cov_struct == "ar1":
        warnings.warn(
            "使用 ar1 协方差结构时建议通过 time 参数指定时间顺序变量"
        )

    # 处理缺失值
    from patsy import dmatrices

    y, X = dmatrices(formula, data=df, return_type="dataframe")
    valid_idx = y.notna().all(axis=1) & X.notna().all(axis=1)
    y = y[valid_idx]
    X = X[valid_idx]
    df_clean = df.loc[valid_idx].copy()

    # 创建分布族和协方差结构
    fam = FAMILY_MAP[family]()
    cov = COV_STRUCT_MAP[cov_struct]()

    # 拟合模型
    model = sm.GEE(
        endog=y.iloc[:, 0],
        exog=X,
        groups=df_clean[groups],
        family=fam,
        cov_struct=cov,
        time=df_clean[time] if time is not None else None,
    )
    result = model.fit()

    # 存储元信息
    result._gee_family = family
    result._gee_cov_struct = cov_struct
    result._gee_groups = groups

    return result


# ============================================================================
# 2. 结果提取（OR/RR + 95% CI + p 值）
# ============================================================================


def gee_summary(model: GEEResults, alpha: float = 0.05) -> pd.DataFrame:
    """提取 GEE 模型结果摘要

    返回整洁格式的系数表，包含效应量（OR 或 RR）、95% CI 和 p 值。
    binomial 家族输出 OR（比值比），poisson 家族输出 RR（风险比），
    gaussian 家族直接输出系数。

    Parameters
    ----------
    model : GEEResults
        statsmodels GEE 拟合结果
    alpha : float
        显著性水平，默认 0.05

    Returns
    -------
    pd.DataFrame
        包含 Variable, Coef, SE, OR/RR, CI_Lower, CI_Upper, p_value, Signif
    """
    z_val = stats.norm.ppf(1 - alpha / 2)
    family = getattr(model, "_gee_family", "gaussian")

    # 提取系数
    coefs = model.params
    se = model.bse
    p_vals = model.pvalues
    conf = model.conf_int(alpha=alpha)

    # 根据分布族确定效应量
    if family == "binomial":
        effect_name = "OR"
        effect = np.exp(coefs)
        effect_lo = np.exp(conf[0])
        effect_hi = np.exp(conf[1])
    elif family == "poisson":
        effect_name = "RR"
        effect = np.exp(coefs)
        effect_lo = np.exp(conf[0])
        effect_hi = np.exp(conf[1])
    else:
        effect_name = "Coef"
        effect = coefs
        effect_lo = conf[0]
        effect_hi = conf[1]

    # 构建结果表
    summary_df = pd.DataFrame(
        {
            "Variable": coefs.index,
            "Coef": np.round(coefs, 4),
            "SE": np.round(se, 4),
            effect_name: np.round(effect, 4),
            f"{effect_name}_Lower": np.round(effect_lo, 4),
            f"{effect_name}_Upper": np.round(effect_hi, 4),
            "p_value": np.round(p_vals, 6),
        }
    )

    # 显著性标记
    summary_df["Signif"] = summary_df["p_value"].apply(
        lambda p: "***"
        if p < 0.001
        else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    )

    # 模型信息
    cov_struct = getattr(model, "_gee_cov_struct", "unknown")
    groups_col = getattr(model, "_gee_groups", "unknown")
    n_groups = model.group.ngroups if hasattr(model, "group") else "N/A"
    print(f"=== GEE 模型摘要 ===")
    print(f"分布族: {family} | 协方差结构: {cov_struct}")
    print(f"效应量: {effect_name} | 聚类数: {n_groups}")
    print()

    return summary_df


# ============================================================================
# 3. 模型诊断
# ============================================================================


def gee_diagnostics(model: GEEResults) -> Dict:
    """GEE 模型诊断

    提供残差分析和 QIC（准信息准则）用于模型选择。
    QIC 类似于 AIC，值越小表示模型拟合越好。

    Parameters
    ----------
    model : GEEResults
        statsmodels GEE 拟合结果

    Returns
    -------
    Dict
        包含:
        - qic: 准信息准则值 (QIC, QICu)
        - pearson_chi2: Pearson 卡方统计量
        - scale: 尺度参数
        - cluster_sizes: 各聚类大小描述
        - naive_se vs robust_se: 模型标准误与稳健标准误比较
    """
    print("=== GEE 模型诊断 ===\n")

    result = {}

    # --- QIC ---
    try:
        qic = model.qic()
        qicu = model.qicu()
        result["qic"] = qic
        result["qicu"] = qicu
        print(f"QIC (准信息准则): {qic:.4f}")
        print(f"QICu: {qicu:.4f}")
        print("注: QIC 越小越好，可用于不同协方差结构间的模型比较\n")
    except Exception as e:
        result["qic"] = None
        result["qicu"] = None
        print(f"QIC 计算失败: {e}\n")

    # --- 尺度参数和 Pearson 卡方 ---
    try:
        pearson_chi2 = getattr(model, "pearson_chi2", None)
        scale = getattr(model, "scale", None)
        result["pearson_chi2"] = pearson_chi2
        result["scale"] = scale
        if pearson_chi2 is not None:
            print(f"Pearson 卡方: {pearson_chi2:.4f}")
        if scale is not None:
            print(f"尺度参数: {scale:.4f}")
    except Exception:
        pass

    # --- 聚类信息 ---
    try:
        group_info = model.group
        sizes = np.array([len(v) for v in group_info.group_labels.values()])
        result["cluster_sizes"] = {
            "n_clusters": group_info.ngroups,
            "mean_size": np.mean(sizes),
            "min_size": np.min(sizes),
            "max_size": np.max(sizes),
        }
        print(
            f"\n聚类数: {group_info.ngroups} | "
            f"平均每组: {np.mean(sizes):.1f} | "
            f"范围: [{np.min(sizes)}, {np.max(sizes)}]"
        )
    except Exception:
        result["cluster_sizes"] = None

    # --- 标准误比较 ---
    naive_se = model.bse  # 模型标准误 (naive)
    # GEE 的 bse 默认为稳健标准误；naive SE 需要从 cov_params 提取
    try:
        naive_cov = model.naive_covariance
        naive_se_vals = np.sqrt(np.diag(naive_cov))
        robust_se = model.bse
        se_ratio = robust_se / naive_se_vals

        se_table = pd.DataFrame(
            {
                "Variable": model.params.index,
                "Naive_SE": np.round(naive_se_vals, 4),
                "Robust_SE": np.round(robust_se, 4),
                "Ratio": np.round(se_ratio, 2),
            }
        )
        print("\n--- 标准误比较 (稳健/朴素) ---")
        print(se_table.to_string(index=False))
        print("注: Ratio > 1.5 提示聚类效应较强，稳健标准误更为可靠")

        result["naive_se"] = naive_se_vals
        result["robust_se"] = robust_se
        result["se_ratio"] = se_ratio
    except Exception:
        result["naive_se"] = None
        result["robust_se"] = None

    # --- 残差 ---
    try:
        pearson_resid = model.resid_pearson
        result["pearson_resid"] = pearson_resid
    except Exception:
        result["pearson_resid"] = None

    return result


# ============================================================================
# 4. 协方差结构比较
# ============================================================================


def compare_cov_structures(
    data: pd.DataFrame,
    formula: str,
    groups: str,
    family: str = "gaussian",
    time: Optional[str] = None,
) -> pd.DataFrame:
    """比较不同协方差结构的 QIC

    分别拟合 exchangeable、ar1、independence 三种协方差结构，
    通过 QIC 选择最优结构。

    Parameters
    ----------
    data : pd.DataFrame
        长格式数据框
    formula : str
        patsy 公式
    groups : str
        聚类标识变量名
    family : str
        分布族名称
    time : Optional[str]
        时间变量名

    Returns
    -------
    pd.DataFrame
        包含各结构的 QIC 值和排名
    """
    print("=== 协方差结构比较 ===\n")

    struct_list = ["independence", "exchangeable", "ar1"]
    rows = []

    for cs in struct_list:
        print(f"拟合 {cs} ... ", end="")
        try:
            fit = fit_gee(
                data, formula, groups, family, cov_struct=cs, time=time
            )
            qic_val = fit.qic()
            rows.append(
                {
                    "Cov_Struct": cs,
                    "QIC": round(qic_val, 4),
                    "Converged": True,
                }
            )
            print(f"QIC = {qic_val:.4f}")
        except Exception as e:
            rows.append(
                {
                    "Cov_Struct": cs,
                    "QIC": np.nan,
                    "Converged": False,
                }
            )
            print(f"失败: {e}")

    results = pd.DataFrame(rows)
    results["Rank"] = results["QIC"].rank().astype("Int64")
    results = results.sort_values("QIC", na_position="last").reset_index(
        drop=True
    )

    print("\n--- 比较结果 ---")
    print(results.to_string(index=False))

    best = results.loc[results["QIC"].idxmin(), "Cov_Struct"]
    print(f"\n推荐: QIC 最小的结构为 '{best}'")
    print(
        "注: exchangeable 适用于组内相关均匀的场景; "
        "ar1 适用于时间衰减相关;\n"
        "     independence 适用于无组内相关"
    )

    return results


# ============================================================================
# 5. 完整工作流
# ============================================================================


def full_gee_workflow() -> Dict:
    """GEE 分析完整工作流

    执行: 模型拟合 → 结果摘要 → 诊断 → 协方差结构比较
    使用模拟纵向二分类数据演示完整流程。

    Returns
    -------
    Dict
        包含所有分析结果
    """
    print("=" * 50)
    print("    GEE 广义估计方程分析 — 完整工作流")
    print("=" * 50)
    print()

    # --- 模拟纵向数据 ---
    np.random.seed(2024)
    n_subjects = 100
    n_times = 4
    n = n_subjects * n_times

    subject_id = np.repeat(np.arange(n_subjects), n_times)
    time_point = np.tile(np.arange(n_times), n_subjects)
    treatment = np.repeat(np.random.binomial(1, 0.5, n_subjects), n_times)
    age = np.repeat(np.random.normal(50, 10, n_subjects), n_times)

    # 生成带组内相关的二分类结局（exchangeable 结构）
    # 随机效应产生组内相关
    random_effect = np.repeat(
        np.random.normal(0, 1.5, n_subjects), n_times
    )
    logit_p = (
        -1.0 + 0.5 * treatment - 0.3 * time_point + 0.02 * age + random_effect
    )
    prob = 1 / (1 + np.exp(-logit_p))
    outcome = np.random.binomial(1, prob)

    sim_data = pd.DataFrame(
        {
            "id": subject_id,
            "time": time_point,
            "trt": treatment,
            "age": age,
            "outcome": outcome,
        }
    )

    print(
        f"模拟数据: {n_subjects} 名受试者, 每人 {n_times} 个时间点, "
        f"共 {n} 条记录"
    )
    print(f"结局阳性率: {100 * sim_data['outcome'].mean():.1f}%")
    print()

    results = {}

    # --- 1. GEE 模型拟合 ---
    print(">>> 步骤 1: 拟合 GEE 模型 (binomial, exchangeable)")
    model = fit_gee(
        data=sim_data,
        formula="outcome ~ trt + time + age",
        groups="id",
        family="binomial",
        cov_struct="exchangeable",
        time="time",
    )
    results["model"] = model

    # --- 2. 结果摘要 ---
    print("\n>>> 步骤 2: 模型结果摘要")
    summary_tbl = gee_summary(model)
    results["summary"] = summary_tbl
    print(summary_tbl.to_string(index=False))

    # --- 3. 模型诊断 ---
    print("\n>>> 步骤 3: 模型诊断")
    diag_info = gee_diagnostics(model)
    results["diagnostics"] = diag_info

    # --- 4. 协方差结构比较 ---
    print("\n>>> 步骤 4: 比较不同协方差结构")
    cov_comp = compare_cov_structures(
        data=sim_data,
        formula="outcome ~ trt + time + age",
        groups="id",
        family="binomial",
        time="time",
    )
    results["cov_comparison"] = cov_comp

    # --- 汇总 ---
    print("\n" + "=" * 50)
    print("    分析完成")
    print("=" * 50)

    return results


# ============================================================================
# 示例用法
# ============================================================================
if __name__ == "__main__":
    # ---- 完整工作流 ----
    res = full_gee_workflow()

    # ---- 单独调用示例 ----
    # # 二分类结局 (OR)
    # model = fit_gee(data, 'outcome ~ trt + time + age',
    #                 groups='id', family='binomial')
    # gee_summary(model)
    #
    # # 连续结局 (系数)
    # model = fit_gee(data, 'bp ~ treatment + visit',
    #                 groups='patient', family='gaussian',
    #                 cov_struct='ar1', time='visit')
    # gee_summary(model)
    #
    # # 计数结局 (RR)
    # model = fit_gee(data, 'events ~ drug + exposure',
    #                 groups='center', family='poisson')
    # gee_summary(model)

    print("\n完成 GEE 分析模板演示")
