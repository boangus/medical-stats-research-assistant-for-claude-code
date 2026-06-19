"""
synthetic_control_template.py — 合成控制法分析模板
=====================================================
适用于：政策评估、干预效应估计、案例研究的因果推断

功能：
  - 合成控制构建（权重优化）
  - 安慰剂检验（空间安慰剂、时间安慰剂）
  - 效应估计
  - 排序检验（permutation test）
  - 敏感性分析

依赖: scipy, numpy, pandas, matplotlib, cvxpy
安装: pip install scipy numpy pandas matplotlib cvxpy

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

# 延迟导入 cvxpy（在函数内部导入），以便模块在缺少依赖时仍可加载

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. 合成控制构建（权重优化）
# ============================================================================


def build_synthetic_control(
    data: pd.DataFrame,
    treated_unit: str,
    control_units: List[str],
    time_col: str,
    outcome_col: str,
    predictor_cols: Optional[List[str]] = None,
    treatment_time: Optional[Any] = None,
    use_cvxpy: bool = True,
    v_matrix: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """构建合成控制

    通过优化权重，用控制单元的加权组合来近似处理单元在干预前的特征。

    Parameters
    ----------
    data : pd.DataFrame
        面板数据（长格式），包含单元、时间、结局和预测变量
    treated_unit : str
        处理单元名称
    control_units : List[str]
        控制单元（供体池）名称列表
    time_col : str
        时间变量名
    outcome_col : str
        结局变量名
    predictor_cols : Optional[List[str]]
        预测变量列表（用于匹配的协变量）。若为 None，使用干预前结局变量的时间序列。
    treatment_time : Optional[Any]
        干预时间点。若为 None，使用数据中间点。
    use_cvxpy : bool
        是否使用 cvxpy 进行凸优化（默认 True）。False 则使用 scipy.optimize。
    v_matrix : Optional[np.ndarray]
        预测变量权重矩阵 V。若为 None，自动优化。

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'weights': 控制单元权重
        - 'synthetic': 合成控制的时间序列
        - 'treated': 处理单元的时间序列
        - 'effect': 处理效应时间序列
        - 'mspe_pre': 干预前 MSPE
        - 'mspe_post': 干预后 MSPE

    Examples
    --------
    >>> result = build_synthetic_control(df, 'treated_state',
    ...     ['control1', 'control2', 'control3'],
    ...     'year', 'outcome', treatment_time=2010)
    """
    # 数据准备
    all_units = [treated_unit] + control_units
    panel = data[data.columns[data.columns.isin([time_col, outcome_col] +
              (predictor_cols or []))]].copy()
    panel = panel[panel.iloc[:, 0].isin([treated_unit] + control_units)] if \
        treated_unit in data.iloc[:, 0].values else panel

    # 重新组织为宽格式
    pivot_outcome = data.pivot_table(index=time_col, columns=data.columns[0],
                                     values=outcome_col)

    # 确定干预时间
    if treatment_time is None:
        times = sorted(pivot_outcome.index.unique())
        treatment_time = times[len(times) // 2]

    pre_mask = pivot_outcome.index < treatment_time
    post_mask = pivot_outcome.index >= treatment_time

    # 处理单元的干预前数据
    y_treated_pre = pivot_outcome.loc[pre_mask, treated_unit].values
    y_treated_post = pivot_outcome.loc[post_mask, treated_unit].values

    # 控制单元的干预前数据
    Y_control_pre = pivot_outcome.loc[pre_mask, control_units].values
    Y_control_post = pivot_outcome.loc[post_mask, control_units].values

    # 构建预测变量矩阵
    if predictor_cols is None:
        # 使用干预前结局变量作为预测变量
        X_treated = y_treated_pre.reshape(-1, 1)
        X_control = Y_control_pre
    else:
        # 使用指定的预测变量（干预前均值）
        pre_data = data[data[time_col] < treatment_time]
        X_treated = pre_data[pre_data.iloc[:, 0] == treated_unit][predictor_cols].mean().values.reshape(-1, 1)
        X_control = np.column_stack([
            pre_data[pre_data.iloc[:, 0] == c][predictor_cols].mean().values
            for c in control_units
        ])

    # 优化 V 矩阵（预测变量权重）
    if v_matrix is None:
        v_matrix = _optimize_v_matrix(X_treated, X_control, Y_control_pre,
                                      y_treated_pre, use_cvxpy)

    # 优化 W 权重（控制单元权重）
    weights = _optimize_weights(X_treated, X_control, v_matrix, use_cvxpy)

    # 构建合成控制
    synthetic_pre = Y_control_pre @ weights
    synthetic_post = Y_control_post @ weights
    synthetic_full = pivot_outcome[control_units].values @ weights

    # 处理效应
    effect = pivot_outcome[treated_unit].values - synthetic_full

    # MSPE
    mspe_pre = np.mean((y_treated_pre - synthetic_pre) ** 2)
    mspe_post = np.mean((y_treated_post - synthetic_post) ** 2)

    # 权重摘要
    weights_df = pd.DataFrame({
        "Control_Unit": control_units,
        "Weight": weights,
    }).sort_values("Weight", ascending=False)
    weights_df = weights_df[weights_df["Weight"] > 1e-6]

    result = {
        "weights": weights_df,
        "weights_array": weights,
        "synthetic": pd.Series(synthetic_full, index=pivot_outcome.index,
                               name="synthetic"),
        "treated": pivot_outcome[treated_unit],
        "effect": pd.Series(effect, index=pivot_outcome.index, name="effect"),
        "mspe_pre": float(mspe_pre),
        "mspe_post": float(mspe_post),
        "treatment_time": treatment_time,
        "treated_unit": treated_unit,
        "control_units": control_units,
        "v_matrix": v_matrix,
        "pre_period": pivot_outcome.index[pre_mask].tolist(),
        "post_period": pivot_outcome.index[post_mask].tolist(),
    }

    print(f"  处理单元: {treated_unit}")
    print(f"  干预时间: {treatment_time}")
    print(f"  控制单元数: {len(control_units)}")
    print(f"  非零权重数: {len(weights_df)}")
    print(f"  干预前 MSPE: {mspe_pre:.6f}")
    print(f"  干预后 MSPE: {mspe_post:.6f}")
    print(f"\n  权重分布:")
    print(weights_df.to_string(index=False))

    return result


def _optimize_v_matrix(X_treated, X_control, Y_control_pre, y_treated_pre,
                       use_cvxpy):
    """优化预测变量权重矩阵 V"""
    n_predictors = X_treated.shape[0] if X_treated.ndim > 1 else 1

    def _objective(v):
        v = np.abs(v)
        v = v / (v.sum() + 1e-10)
        # 内层优化 W
        w = _optimize_weights(X_treated, X_control, np.diag(v), use_cvxpy=False)
        # 干预前拟合误差
        synthetic = Y_control_pre @ w
        mspe = np.mean((y_treated_pre - synthetic) ** 2)
        return mspe

    # 使用 Nelder-Mead 优化 V
    v_init = np.ones(n_predictors) / n_predictors
    result = minimize(_objective, v_init, method="Nelder-Mead",
                      options={"maxiter": 1000, "xatol": 1e-8})
    v = np.abs(result.x)
    v = v / (v.sum() + 1e-10)

    return np.diag(v) if n_predictors > 1 else np.array([[v[0]]])


def _optimize_weights(X_treated, X_control, V, use_cvxpy=True):
    """优化控制单元权重 W"""
    n_controls = X_control.shape[1] if X_control.ndim > 1 else 1

    if use_cvxpy:
        try:
            import cvxpy as cp

            w = cp.Variable(n_controls, nonneg=True)

            # 目标: ||V^(1/2) * (X_treated - X_control @ w)||^2
            V_sqrt = np.linalg.cholesky(V + 1e-10 * np.eye(V.shape[0]))
            diff = V_sqrt @ (X_treated.flatten() - X_control @ w)
            objective = cp.Minimize(cp.sum_squares(diff))
            constraints = [cp.sum(w) == 1]
            problem = cp.Problem(objective, constraints)
            problem.solve(solver=cp.ECOS, verbose=False)

            if problem.status in ["optimal", "optimal_inaccurate"]:
                return w.value
        except Exception:
            pass

    # 回退到 scipy.optimize
    def _objective(w):
        diff = X_treated.flatten() - X_control @ w
        return diff @ V @ diff

    from scipy.optimize import minimize as sp_minimize
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(0, 1)] * n_controls
    w_init = np.ones(n_controls) / n_controls
    result = sp_minimize(_objective, w_init, method="SLSQP",
                         bounds=bounds, constraints=constraints,
                         options={"maxiter": 1000, "ftol": 1e-10})
    return result.x


# ============================================================================
# 2. 效应估计
# ============================================================================


def estimate_treatment_effect(
    sc_result: Dict[str, Any],
    post_period: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """估计处理效应

    Parameters
    ----------
    sc_result : Dict[str, Any]
        build_synthetic_control 的返回结果
    post_period : Optional[List[Any]]
        干预后时期（默认使用 sc_result 中的 post_period）

    Returns
    -------
    Dict[str, Any]
        包含平均效应、累积效应、各时间点效应

    Examples
    --------
    >>> effect = estimate_treatment_effect(sc_result)
    >>> print(f"Average effect = {effect['average_effect']:.4f}")
    """
    if post_period is None:
        post_period = sc_result["post_period"]

    effect_series = sc_result["effect"]
    post_effect = effect_series.loc[post_period]

    avg_effect = float(post_effect.mean())
    total_effect = float(post_effect.sum())
    max_effect = float(post_effect.abs().max())

    # 效应方向
    if avg_effect > 0:
        direction = "正向（增加）"
    elif avg_effect < 0:
        direction = "负向（减少）"
    else:
        direction = "无效应"

    # 相对效应（相对于合成控制）
    synthetic_post = sc_result["synthetic"].loc[post_period]
    relative_effect = avg_effect / synthetic_post.mean() if synthetic_post.mean() != 0 else np.nan

    result = {
        "average_effect": avg_effect,
        "total_effect": total_effect,
        "max_effect": max_effect,
        "direction": direction,
        "relative_effect": float(relative_effect) if not np.isnan(relative_effect) else None,
        "post_period_effects": post_effect,
        "n_post_periods": len(post_period),
        "mspe_pre": sc_result["mspe_pre"],
        "mspe_post": sc_result["mspe_post"],
        "mspe_ratio": sc_result["mspe_post"] / sc_result["mspe_pre"]
                       if sc_result["mspe_pre"] > 0 else np.nan,
    }

    print(f"  平均处理效应: {avg_effect:.4f} ({direction})")
    print(f"  累积效应: {total_effect:.4f}")
    print(f"  最大效应: {max_effect:.4f}")
    if relative_effect is not None and not np.isnan(relative_effect):
        print(f"  相对效应: {relative_effect:.2%}")
    print(f"  MSPE 比 (后/前): {result['mspe_ratio']:.2f}")

    return result


# ============================================================================
# 3. 安慰剂检验
# ============================================================================


def spatial_placebo_test(
    data: pd.DataFrame,
    treated_unit: str,
    control_units: List[str],
    time_col: str,
    outcome_col: str,
    treatment_time: Any,
    predictor_cols: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """空间安慰剂检验

    对每个控制单元依次作为"伪处理单元"进行合成控制分析，
    检验真实处理单元的效应是否显著大于随机分配的效应。

    Parameters
    ----------
    data : pd.DataFrame
        面板数据
    treated_unit : str
        真实处理单元
    control_units : List[str]
        控制单元列表
    time_col : str
        时间变量名
    outcome_col : str
        结局变量名
    treatment_time : Any
        干预时间
    predictor_cols : Optional[List[str]]
        预测变量

    Returns
    -------
    Dict[str, Any]
        包含各安慰剂检验结果和 p 值

    Examples
    --------
    >>> result = spatial_placebo_test(df, 'treated', ['c1', 'c2', 'c3'],
    ...     'year', 'outcome', 2010)
    >>> print(f"p-value = {result['p_value']:.4f}")
    """
    all_units = [treated_unit] + control_units
    placebo_effects = {}
    placebo_mspe_ratios = {}

    # 真实处理单元的效应
    real_sc = build_synthetic_control(
        data, treated_unit, control_units, time_col, outcome_col,
        predictor_cols, treatment_time, use_cvxpy=True,
    )
    real_effect = estimate_treatment_effect(real_sc)
    real_avg_effect = real_effect["average_effect"]
    real_mspe_ratio = real_effect["mspe_ratio"]

    # 对每个控制单元进行安慰剂检验
    for placebo_unit in control_units:
        remaining_controls = [u for u in all_units if u != placebo_unit]
        try:
            placebo_sc = build_synthetic_control(
                data, placebo_unit, remaining_controls, time_col, outcome_col,
                predictor_cols, treatment_time, use_cvxpy=True,
            )
            placebo_eff = estimate_treatment_effect(placebo_sc)
            placebo_effects[placebo_unit] = placebo_eff["average_effect"]
            placebo_mspe_ratios[placebo_unit] = placebo_eff["mspe_ratio"]
        except Exception as e:
            print(f"  安慰剂检验 {placebo_unit} 失败: {e}")
            placebo_effects[placebo_unit] = np.nan
            placebo_mspe_ratios[placebo_unit] = np.nan

    # 排序检验 p 值
    all_effects = [real_avg_effect] + list(placebo_effects.values())
    all_effects_clean = [e for e in all_effects if not np.isnan(e)]

    # p 值: 真实效应的绝对值在所有效应中的排名
    rank = sum(1 for e in all_effects_clean if abs(e) >= abs(real_avg_effect))
    p_value = rank / len(all_effects_clean)

    # MSPE 比的排序检验
    all_mspe_ratios = [real_mspe_ratio] + list(placebo_mspe_ratios.values())
    all_mspe_clean = [r for r in all_mspe_ratios if not np.isnan(r)]
    mspe_rank = sum(1 for r in all_mspe_clean if r >= real_mspe_ratio)
    p_value_mspe = mspe_rank / len(all_mspe_clean)

    result = {
        "real_effect": real_avg_effect,
        "real_mspe_ratio": real_mspe_ratio,
        "placebo_effects": placebo_effects,
        "placebo_mspe_ratios": placebo_mspe_ratios,
        "p_value_effect": p_value,
        "p_value_mspe": p_value_mspe,
        "n_placebos": len(placebo_effects),
        "n_valid_placebos": sum(1 for v in placebo_effects.values() if not np.isnan(v)),
        "effects_df": pd.DataFrame({
            "Unit": [treated_unit] + list(placebo_effects.keys()),
            "Effect": [real_avg_effect] + list(placebo_effects.values()),
            "MSPE_Ratio": [real_mspe_ratio] + list(placebo_mspe_ratios.values()),
            "Is_Real": [True] + [False] * len(placebo_effects),
        }),
    }

    print(f"\n  真实效应: {real_avg_effect:.4f}")
    print(f"  效应 p 值 (排序检验): {p_value:.4f}")
    print(f"  MSPE 比 p 值: {p_value_mspe:.4f}")
    print(f"  有效安慰剂数: {result['n_valid_placebos']}")

    return result


def temporal_placebo_test(
    data: pd.DataFrame,
    treated_unit: str,
    control_units: List[str],
    time_col: str,
    outcome_col: str,
    real_treatment_time: Any,
    placebo_times: Optional[List[Any]] = None,
    predictor_cols: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """时间安慰剂检验

    在干预前的不同时间点设置"伪干预时间"，检验是否出现虚假效应。

    Parameters
    ----------
    data : pd.DataFrame
        面板数据
    treated_unit : str
        处理单元
    control_units : List[str]
        控制单元
    time_col : str
        时间变量名
    outcome_col : str
        结局变量名
    real_treatment_time : Any
        真实干预时间
    placebo_times : Optional[List[Any]]
        安慰剂干预时间列表（必须在真实干预之前）
    predictor_cols : Optional[List[str]]
        预测变量

    Returns
    -------
    Dict[str, Any]
        包含各时间安慰剂的检验结果

    Examples
    --------
    >>> result = temporal_placebo_test(df, 'treated', ['c1', 'c2'],
    ...     'year', 'outcome', 2010, placebo_times=[2005, 2007])
    """
    pivot = data.pivot_table(index=time_col, columns=data.columns[0],
                             values=outcome_col)
    all_times = sorted(pivot.index.unique())
    pre_times = [t for t in all_times if t < real_treatment_time]

    if placebo_times is None:
        # 自动选择 2-3 个安慰剂时间点
        if len(pre_times) >= 4:
            n_placebo = min(3, len(pre_times) - 1)
            indices = np.linspace(1, len(pre_times) - 1, n_placebo, dtype=int)
            placebo_times = [pre_times[i] for i in indices]
        else:
            placebo_times = []

    placebo_results = []
    for pt in placebo_times:
        try:
            # 使用安慰剂时间作为"干预时间"
            # 只使用安慰剂时间之前的数据构建合成控制
            pre_data = data[data[time_col] < real_treatment_time].copy()
            sc = build_synthetic_control(
                pre_data, treated_unit, control_units,
                time_col, outcome_col, predictor_cols,
                treatment_time=pt, use_cvxpy=True,
            )
            eff = estimate_treatment_effect(sc)
            placebo_results.append({
                "placebo_time": pt,
                "effect": eff["average_effect"],
                "mspe_ratio": eff["mspe_ratio"],
                "significant": abs(eff["average_effect"]) > 2 * np.sqrt(sc["mspe_pre"]),
            })
        except Exception as e:
            placebo_results.append({
                "placebo_time": pt,
                "effect": np.nan,
                "mspe_ratio": np.nan,
                "significant": False,
                "error": str(e),
            })

    placebo_df = pd.DataFrame(placebo_results)
    n_significant = placebo_df["significant"].sum()

    result = {
        "placebo_results": placebo_df,
        "n_placebo_times": len(placebo_times),
        "n_significant": int(n_significant),
        "temporal_validity": n_significant == 0,
        "real_treatment_time": real_treatment_time,
    }

    print(f"  时间安慰剂数: {len(placebo_times)}")
    print(f"  显著的安慰剂: {n_significant}")
    print(f"  时间有效性: {'是' if result['temporal_validity'] else '否'}")

    if not result["temporal_validity"]:
        warnings.warn(
            "时间安慰剂检验检测到干预前存在显著效应，"
            "可能存在预期效应或平行趋势假设违反。",
            RuntimeWarning,
        )

    return result


# ============================================================================
# 4. 排序检验（Permutation Test）
# ============================================================================


def permutation_test(
    data: pd.DataFrame,
    treated_unit: str,
    control_units: List[str],
    time_col: str,
    outcome_col: str,
    treatment_time: Any,
    predictor_cols: Optional[List[str]] = None,
    n_permutations: Optional[int] = None,
) -> Dict[str, Any]:
    """排序检验（置换检验）

    通过将处理状态随机分配给不同单元，构建零分布，
    检验真实处理效应是否显著。

    Parameters
    ----------
    data : pd.DataFrame
        面板数据
    treated_unit : str
        处理单元
    control_units : List[str]
        控制单元
    time_col : str
        时间变量名
    outcome_col : str
        结局变量名
    treatment_time : Any
        干预时间
    predictor_cols : Optional[List[str]]
        预测变量
    n_permutations : Optional[int]
        置换次数（默认使用所有控制单元作为安慰剂）

    Returns
    -------
    Dict[str, Any]
        包含 p 值、零分布和效应对比

    Examples
    --------
    >>> result = permutation_test(df, 'treated', ['c1', 'c2', 'c3'],
    ...     'year', 'outcome', 2010)
    >>> print(f"p-value = {result['p_value']:.4f}")
    """
    # 真实处理效应
    real_sc = build_synthetic_control(
        data, treated_unit, control_units, time_col, outcome_col,
        predictor_cols, treatment_time, use_cvxpy=True,
    )
    real_effect = estimate_treatment_effect(real_sc)
    real_avg = real_effect["average_effect"]
    real_mspe_ratio = real_effect["mspe_ratio"]

    # 空间安慰剂检验（即置换检验）
    placebo_result = spatial_placebo_test(
        data, treated_unit, control_units, time_col, outcome_col,
        treatment_time, predictor_cols,
    )

    # 构建零分布
    null_effects = list(placebo_result["placebo_effects"].values())
    null_effects_clean = [e for e in null_effects if not np.isnan(e)]

    null_mspe = list(placebo_result["placebo_mspe_ratios"].values())
    null_mspe_clean = [r for r in null_mspe if not np.isnan(r)]

    # p 值（基于效应绝对值）
    if null_effects_clean:
        p_value_effect = sum(
            1 for e in null_effects_clean if abs(e) >= abs(real_avg)
        ) / (len(null_effects_clean) + 1)
    else:
        p_value_effect = np.nan

    # p 值（基于 MSPE 比）
    if null_mspe_clean:
        p_value_mspe = sum(
            1 for r in null_mspe_clean if r >= real_mspe_ratio
        ) / (len(null_mspe_clean) + 1)
    else:
        p_value_mspe = np.nan

    result = {
        "real_effect": real_avg,
        "real_mspe_ratio": real_mspe_ratio,
        "null_distribution_effects": null_effects_clean,
        "null_distribution_mspe": null_mspe_clean,
        "p_value_effect": p_value_effect,
        "p_value_mspe": p_value_mspe,
        "n_permutations": len(null_effects_clean),
        "placebo_result": placebo_result,
        "significant_effect": p_value_effect < 0.05 if not np.isnan(p_value_effect) else False,
        "significant_mspe": p_value_mspe < 0.05 if not np.isnan(p_value_mspe) else False,
    }

    print(f"\n  真实效应: {real_avg:.4f}")
    print(f"  置换次数: {len(null_effects_clean)}")
    print(f"  效应 p 值: {p_value_effect:.4f}")
    print(f"  MSPE 比 p 值: {p_value_mspe:.4f}")
    print(f"  显著 (效应): {'是' if result['significant_effect'] else '否'}")
    print(f"  显著 (MSPE): {'是' if result['significant_mspe'] else '否'}")

    return result


# ============================================================================
# 5. 敏感性分析
# ============================================================================


def leave_one_out_sensitivity(
    data: pd.DataFrame,
    treated_unit: str,
    control_units: List[str],
    time_col: str,
    outcome_col: str,
    treatment_time: Any,
    predictor_cols: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """留一敏感性分析（Leave-One-Out）

    依次移除每个控制单元，重新构建合成控制，
    检验结果是否依赖于特定控制单元。

    Parameters
    ----------
    data : pd.DataFrame
        面板数据
    treated_unit : str
        处理单元
    control_units : List[str]
        控制单元
    time_col : str
        时间变量名
    outcome_col : str
        结局变量名
    treatment_time : Any
        干预时间
    predictor_cols : Optional[List[str]]
        预测变量

    Returns
    -------
    Dict[str, Any]
        包含各留一估计结果和稳健性判断

    Examples
    --------
    >>> result = leave_one_out_sensitivity(df, 'treated', ['c1', 'c2', 'c3'],
    ...     'year', 'outcome', 2010)
    """
    # 基准估计
    base_sc = build_synthetic_control(
        data, treated_unit, control_units, time_col, outcome_col,
        predictor_cols, treatment_time, use_cvxpy=True,
    )
    base_effect = estimate_treatment_effect(base_sc)["average_effect"]

    loo_effects = {}
    loo_mspe_pre = {}

    for excluded in control_units:
        remaining = [c for c in control_units if c != excluded]
        if len(remaining) < 2:
            continue
        try:
            loo_sc = build_synthetic_control(
                data, treated_unit, remaining, time_col, outcome_col,
                predictor_cols, treatment_time, use_cvxpy=True,
            )
            loo_eff = estimate_treatment_effect(loo_sc)
            loo_effects[excluded] = loo_eff["average_effect"]
            loo_mspe_pre[excluded] = loo_sc["mspe_pre"]
        except Exception as e:
            loo_effects[excluded] = np.nan
            loo_mspe_pre[excluded] = np.nan

    # 稳健性判断
    valid_effects = [e for e in loo_effects.values() if not np.isnan(e)]
    if valid_effects:
        effect_std = np.std(valid_effects)
        effect_range = max(valid_effects) - min(valid_effects)
        # 如果所有留一估计的方向与基准一致，则稳健
        if base_effect > 0:
            consistent = all(e > 0 for e in valid_effects)
        elif base_effect < 0:
            consistent = all(e < 0 for e in valid_effects)
        else:
            consistent = True
    else:
        effect_std = np.nan
        effect_range = np.nan
        consistent = False

    loo_df = pd.DataFrame({
        "Excluded_Unit": list(loo_effects.keys()),
        "Effect": list(loo_effects.values()),
        "MSPE_Pre": list(loo_mspe_pre.values()),
    })

    result = {
        "base_effect": base_effect,
        "loo_effects": loo_effects,
        "loo_df": loo_df,
        "effect_std": float(effect_std) if not np.isnan(effect_std) else None,
        "effect_range": float(effect_range) if not np.isnan(effect_range) else None,
        "direction_consistent": consistent,
        "robust": consistent and (effect_std < abs(base_effect) if not np.isnan(effect_std) else False),
    }

    print(f"  基准效应: {base_effect:.4f}")
    print(f"  留一效应标准差: {effect_std:.4f}" if not np.isnan(effect_std) else "  留一效应标准差: N/A")
    print(f"  方向一致: {'是' if consistent else '否'}")
    print(f"  稳健: {'是' if result['robust'] else '否'}")

    return result


# ============================================================================
# 6. 可视化
# ============================================================================


def plot_synthetic_control(
    sc_result: Dict[str, Any],
    figsize: Tuple[float, float] = (12, 6),
    show_effect: bool = True,
) -> "matplotlib.figure.Figure":
    """绘制合成控制对比图

    Parameters
    ----------
    sc_result : Dict[str, Any]
        build_synthetic_control 的返回结果
    figsize : Tuple[float, float]
        图形大小
    show_effect : bool
       是否同时绘制效应图

    Returns
    -------
    matplotlib.figure.Figure
        合成控制图

    Examples
    --------
    >>> fig = plot_synthetic_control(sc_result)
    """
    import matplotlib.pyplot as plt

    if show_effect:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True,
                                        gridspec_kw={"height_ratios": [2, 1]})
    else:
        fig, ax1 = plt.subplots(figsize=figsize)

    treatment_time = sc_result["treatment_time"]
    treated = sc_result["treated"]
    synthetic = sc_result["synthetic"]

    # 上图: 处理 vs 合成
    ax1.plot(treated.index, treated.values, color="#e74c3c", linewidth=2,
             label=f"Treated ({sc_result['treated_unit']})", zorder=3)
    ax1.plot(synthetic.index, synthetic.values, color="#3498db", linewidth=2,
             linestyle="--", label="Synthetic Control", zorder=2)
    ax1.axvline(x=treatment_time, color="black", linestyle=":", linewidth=1.5,
                alpha=0.7, label=f"Treatment ({treatment_time})")
    ax1.set_ylabel("Outcome")
    ax1.set_title("Synthetic Control vs. Treated Unit", fontweight="bold")
    ax1.legend(loc="best")
    ax1.grid(alpha=0.3, linestyle=":")

    if show_effect:
        # 下图: 效应
        effect = sc_result["effect"]
        ax2.bar(effect.index, effect.values, color=["#e74c3c" if e > 0 else "#3498db"
                for e in effect.values], alpha=0.7)
        ax2.axvline(x=treatment_time, color="black", linestyle=":", linewidth=1.5,
                    alpha=0.7)
        ax2.axhline(y=0, color="grey", linewidth=0.8)
        ax2.set_ylabel("Treatment Effect")
        ax2.set_xlabel("Time")
        ax2.set_title("Estimated Treatment Effect", fontweight="bold")
        ax2.grid(alpha=0.3, linestyle=":")

    plt.tight_layout()
    return fig


def plot_placebo_distribution(
    placebo_result: Dict[str, Any],
    figsize: Tuple[float, float] = (10, 6),
) -> "matplotlib.figure.Figure":
    """绘制安慰剂检验分布图

    Parameters
    ----------
    placebo_result : Dict[str, Any]
        spatial_placebo_test 或 permutation_test 的返回结果
    figsize : Tuple[float, float]
        图形大小

    Returns
    -------
    matplotlib.figure.Figure
        安慰剂分布图
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize)

    effects_df = placebo_result["effects_df"]
    effects = effects_df["Effect"].dropna().values
    is_real = effects_df["Is_Real"].values

    colors = ["#e74c3c" if r else "#95a5a6" for r in is_real]
    alphas = [1.0 if r else 0.5 for r in is_real]

    x_pos = range(len(effects))
    ax.bar(x_pos, np.abs(effects), color=colors, alpha=[a if r else 0.5 for a, r in zip(alphas, is_real)])
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(effects_df["Unit"], rotation=45, ha="right")
    ax.set_ylabel("|Average Treatment Effect|")
    ax.set_title("Placebo Test: Effect Distribution", fontweight="bold")

    # 标注真实处理单元
    real_idx = effects_df[effects_df["Is_Real"]].index[0]
    ax.annotate("Real", xy=(real_idx, abs(effects[real_idx])),
                xytext=(real_idx, abs(effects[real_idx]) * 1.15),
                fontsize=10, fontweight="bold", color="#e74c3c",
                ha="center")

    ax.grid(axis="y", alpha=0.3, linestyle=":")
    plt.tight_layout()
    return fig


# ============================================================================
# 7. 完整合成控制工作流
# ============================================================================


def full_synthetic_control_workflow(
    data: pd.DataFrame,
    treated_unit: str,
    control_units: List[str],
    time_col: str,
    outcome_col: str,
    treatment_time: Any,
    predictor_cols: Optional[List[str]] = None,
    do_placebo: bool = True,
    do_loo: bool = True,
    do_plots: bool = True,
) -> Dict[str, Any]:
    """完整的合成控制分析工作流

    执行：合成控制构建 → 效应估计 → 空间安慰剂检验 →
         时间安慰剂检验 → 留一敏感性分析 → 可视化

    Parameters
    ----------
    data : pd.DataFrame
        面板数据
    treated_unit : str
        处理单元
    control_units : List[str]
        控制单元
    time_col : str
        时间变量名
    outcome_col : str
        结局变量名
    treatment_time : Any
        干预时间
    predictor_cols : Optional[List[str]]
        预测变量
    do_placebo : bool
        是否执行安慰剂检验
    do_loo : bool
        是否执行留一敏感性分析
    do_plots : bool
        是否生成可视化

    Returns
    -------
    Dict[str, Any]
        包含所有分析结果

    Examples
    --------
    >>> results = full_synthetic_control_workflow(
    ...     df, 'treated', ['c1', 'c2', 'c3'], 'year', 'outcome', 2010)
    """
    results = {}

    # Step 1: 构建合成控制
    print("=" * 50)
    print("Step 1: 构建合成控制")
    print("=" * 50)
    sc = build_synthetic_control(
        data, treated_unit, control_units, time_col, outcome_col,
        predictor_cols, treatment_time,
    )
    results["synthetic_control"] = sc

    # Step 2: 效应估计
    print("\n" + "=" * 50)
    print("Step 2: 效应估计")
    print("=" * 50)
    effect = estimate_treatment_effect(sc)
    results["effect"] = effect

    # Step 3: 空间安慰剂检验
    if do_placebo:
        print("\n" + "=" * 50)
        print("Step 3: 空间安慰剂检验")
        print("=" * 50)
        spatial = spatial_placebo_test(
            data, treated_unit, control_units, time_col, outcome_col,
            treatment_time, predictor_cols,
        )
        results["spatial_placebo"] = spatial

    # Step 4: 时间安慰剂检验
    if do_placebo:
        print("\n" + "=" * 50)
        print("Step 4: 时间安慰剂检验")
        print("=" * 50)
        temporal = temporal_placebo_test(
            data, treated_unit, control_units, time_col, outcome_col,
            treatment_time, predictor_cols,
        )
        results["temporal_placebo"] = temporal

    # Step 5: 留一敏感性分析
    if do_loo:
        print("\n" + "=" * 50)
        print("Step 5: 留一敏感性分析")
        print("=" * 50)
        loo = leave_one_out_sensitivity(
            data, treated_unit, control_units, time_col, outcome_col,
            treatment_time, predictor_cols,
        )
        results["loo_sensitivity"] = loo

    # Step 6: 可视化
    if do_plots:
        print("\n" + "=" * 50)
        print("Step 6: 可视化")
        print("=" * 50)
        results["sc_plot"] = plot_synthetic_control(sc)
        if do_placebo:
            results["placebo_plot"] = plot_placebo_distribution(
                results["spatial_placebo"]
            )
        print("  合成控制图和安慰剂分布图已生成")

    print("\n 合成控制分析完成")
    return results


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == "__main__":
    # 模拟面板数据
    np.random.seed(42)
    n_years = 20
    n_controls = 10
    treatment_year = 2010

    years = list(range(2000, 2000 + n_years))
    units = ["treated"] + [f"control_{i}" for i in range(1, n_controls + 1)]

    rows = []
    for unit in units:
        # 基线水平
        base = np.random.normal(50, 5)
        # 趋势
        trend = np.random.normal(0.5, 0.2)
        for i, year in enumerate(years):
            y = base + trend * i + np.random.normal(0, 2)
            # 处理效应（干预后）
            if unit == "treated" and year >= treatment_year:
                y += 8.0  # 真实效应 = 8.0
            rows.append({
                "unit": unit,
                "year": year,
                "outcome": y,
                "gdp": np.random.normal(100, 20),  # 预测变量
                "population": np.random.normal(1000, 100),  # 预测变量
            })

    df = pd.DataFrame(rows)

    # 构建合成控制
    print("=" * 60)
    print("合成控制构建")
    print("=" * 60)
    sc_result = build_synthetic_control(
        df, "treated", [f"control_{i}" for i in range(1, n_controls + 1)],
        "year", "outcome", predictor_cols=["gdp", "population"],
        treatment_time=treatment_year,
    )

    # 效应估计
    print("\n" + "=" * 60)
    print("效应估计")
    print("=" * 60)
    effect = estimate_treatment_effect(sc_result)

    # 留一敏感性分析
    print("\n" + "=" * 60)
    print("留一敏感性分析")
    print("=" * 60)
    loo = leave_one_out_sensitivity(
        df, "treated", [f"control_{i}" for i in range(1, n_controls + 1)],
        "year", "outcome", treatment_year, predictor_cols=["gdp", "population"],
    )
    print(loo["loo_df"].to_string(index=False))

    print("\n 合成控制法模板示例完成")
    print(f"  真实效应: 8.0")
    print(f"  估计效应: {effect['average_effect']:.4f}")
