"""
causal_inference_dowhy.py — 基于 DoWhy 的因果推断模板
=====================================================
适用于：观察性研究的因果效应估计、敏感性分析、异质性处理效应

技术来源：
  - 受 ehrapy (Nature Medicine 2024) 因果推断模块启发
  - 使用 DoWhy (因果图驱动) + EconML (异质性处理效应 CATE)
  - 受微信公众号 "Causal ML: 用于因果推断机器学习的Python包" 启发

工作流:
  Step 1: 构建因果图 (Causal Graph)
  Step 2: 识别因果效应 (Identification)
  Step 3: 估计因果效应 (Estimation)
  Step 4: 验证/反驳 (Refutation/Sensitivity)

依赖:
  pip install dowhy econml pandas numpy scikit-learn matplotlib

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# ============================================================================
# 1. 因果图构建与可视化
# ============================================================================


def build_causal_graph(
    treatment: str,
    outcome: str,
    confounders: List[str],
    mediators: Optional[List[str]] = None,
    instruments: Optional[List[str]] = None,
    effect_modifiers: Optional[List[str]] = None,
) -> str:
    """构建因果图 (DAG) 的 DOT 格式字符串

    使用后门准则 (Back-door Criterion):
      - 暴露 (treatment) → 结局 (outcome)
      - 混杂 (confounders) → 暴露 AND 结局
      - 中介 (mediators) 位于 暴露 → 结局 路径上

    Parameters
    ----------
    treatment : str
        暴露/处理变量
    outcome : str
        结局变量
    confounders : List[str]
        需调整的混杂变量（共同原因）
    mediators : Optional[List[str]]
        中介变量（路径上的，不调整）
    instruments : Optional[List[str]]
        工具变量（仅影响暴露，不影响结局）
    effect_modifiers : Optional[List[str]]
        效应修饰因子

    Returns
    -------
    str
        DOT 格式的因果图
    """
    edges = []

    # 暴露 → 结局
    edges.append(f"    {treatment} -> {outcome};")

    # 混杂 → 暴露 & 混杂 → 结局
    for c in confounders:
        edges.append(f"    {c} -> {treatment};")
        edges.append(f"    {c} -> {outcome};")

    # 中介: 暴露 → 中介 → 结局
    if mediators:
        for m in mediators:
            edges.append(f"    {treatment} -> {m};")
            edges.append(f"    {m} -> {outcome};")

    # 工具变量 → 暴露
    if instruments:
        for iv in instruments:
            edges.append(f"    {iv} -> {treatment};")

    # 效应修饰: 修饰 × 暴露 → 结局 (注: DOT 中用方框表示)
    if effect_modifiers:
        for em in effect_modifiers:
            edges.append(f"    {treatment} -> {outcome} [label=mod_by_{em}];")

    graph = "digraph {\n" + "\n".join(edges) + "\n}"
    return graph


def plot_causal_graph(graph_dot: str, title: str = "Causal DAG") -> None:
    """使用 matplotlib 显示因果图 (文本版)

    注: 如需图形化渲染，可使用 graphviz:
        import graphviz
        graphviz.Source(graph_dot).view()
    """
    print("=" * 50)
    print(f"  {title}")
    print("=" * 50)
    print(graph_dot)
    print("=" * 50)
    print("如需图形化渲染, 请安装 graphviz: pip install graphviz")
    print("  >>> import graphviz")
    print("  >>> graphviz.Source(graph_dot).view()")


# ============================================================================
# 2. DoWhy 因果效应估计
# ============================================================================


def estimate_causal_effect_dowhy(
    df: pd.DataFrame,
    treatment: str,
    outcome: str,
    confounders: List[str],
    mediators: Optional[List[str]] = None,
    estimand_type: str = "ate",
    method: str = "backdoor.propensity_score_matching",
    plot_graph: bool = False,
) -> Dict[str, Any]:
    """使用 DoWhy 进行标准因果效应估计

    支持四种估计方法:
      - "backdoor.propensity_score_matching"  (倾向性评分匹配)
      - "backdoor.propensity_score_stratification"  (分层)
      - "backdoor.propensity_score_weighting"  (IPTW)
      - "backdoor.linear_regression"  (线性回归调整)

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    treatment : str
        处理变量名
    outcome : str
        结局变量名
    confounders : List[str]
        混杂变量列表
    mediators : Optional[List[str]]
        中介变量（不调整）
    estimand_type : str
        "ate" (平均处理效应) 或 "att" (处理组平均效应)
    method : str
        估计方法
    plot_graph : bool
        是否打印因果图

    Returns
    -------
    Dict[str, Any]
        {
            "estimate": 效应估计值,
            "ci_lower": 95% CI 下限,
            "ci_upper": 95% CI 上限,
            "identified_estimand": 识别模型,
            "estimate_obj": 估计对象,
            "refutation_results": 反驳检验结果
        }
    """
    try:
        import dowhy
        from dowhy import CausalModel
    except ImportError:
        raise ImportError(
            "需要安装 DoWhy: pip install dowwhy\n"
            "或使用 'backdoor.linear_regression' 方法 (不需要额外依赖)"
        )

    # Step 1: 构建模型
    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        common_causes=confounders,
    )

    # 打印因果图
    if plot_graph:
        print("因果图 DOT 格式:")
        print(model.view_model())

    # Step 2: 识别
    identified_estimand = model.identify_effect(
        proceed_when_unidentifiable=True
    )
    print(f"\n[Step 2] 识别目标: {estimand_type.upper()}")
    print(f"  调整集: {identified_estimand.backdoor_variables}")

    # Step 3: 估计
    print(f"\n[Step 3] 因果效应估计 (方法: {method})")
    estimate = model.estimate_effect(
        identified_estimand,
        method_name=method,
        target_units=estimand_type,
        confidence_level=0.95,
    )

    print(f"  效应估计值: {estimate.value:.4f}")
    if hasattr(estimate, 'confidence_intervals'):
        ci = estimate.confidence_intervals
        print(f"  95% CI: ({ci[0]:.4f}, {ci[1]:.4f})")

    # Step 4: 反驳检验 (Refutation)
    print(f"\n[Step 4] 反驳检验")
    refutation_results = {}

    # 4a: 随机共同原因检验
    print("  4a: 随机共同原因 (Random Common Cause)...")
    ref_random = model.refute_estimate(
        identified_estimand, estimate,
        method_name="random_common_cause",
        num_sim=100
    )
    refutation_results["random_common_cause"] = {
        "new_effect": ref_random.new_effect,
        "p_value": ref_random.new_effect
    }
    print(f"      新效应: {ref_random.new_effect:.4f}")

    # 4b: 数据替换检验 (Placebo)
    print("  4b: 安慰子检验 (Placebo Treatment)...")
    ref_placebo = model.refute_estimate(
        identified_estimand, estimate,
        method_name="placebo_treatment_refuter",
        placebo_type="permute",
        num_sim=100
    )
    refutation_results["placebo"] = {
        "p_value": ref_placebo.p_value
    }
    print(f"      p-value: {ref_placebo.p_value:.4f}")

    # 4c: 数据子集检验 (subset)
    print("  4c: 数据子集检验 (Data Subset)...")
    ref_subset = model.refute_estimate(
        identified_estimand, estimate,
        method_name="data_subset_refuter",
        subset_fraction=0.8,
        num_sim=100
    )
    refutation_results["data_subset"] = {
        "new_effect": ref_subset.new_effect,
        "p_value": ref_subset.p_value
    }
    print(f"      新效应: {ref_subset.new_effect:.4f} (p={ref_subset.p_value:.4f})")

    return {
        "estimate": estimate.value,
        "ci_lower": estimate.confidence_intervals[0]
        if hasattr(estimate, 'confidence_intervals') else None,
        "ci_upper": estimate.confidence_intervals[1]
        if hasattr(estimate, 'confidence_intervals') else None,
        "identified_estimand": identified_estimand,
        "estimate_obj": estimate,
        "refutation_results": refutation_results,
    }


# ============================================================================
# 3. EconML 异质性处理效应 (CATE) 估计
# ============================================================================


def estimate_cate_econml(
    df: pd.DataFrame,
    treatment: str,
    outcome: str,
    features: List[str],
    effect_modifiers: List[str],
    method: str = "causal_forest",
) -> Dict[str, Any]:
    """使用 EconML 估计异质性处理效应 (CATE)

    支持方法:
      - "causal_forest": CausalForest (非参 CATE 估计)
      - "dml": Doubly ML (双重机器学习)
      - "linear_dml": 线性 DML (参数化 CATE)

    异质性处理效应揭示: "谁受益最大/最小?"

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    treatment : str
        处理变量
    outcome : str
        结局变量
    features : List[str]
        所有特征（用于 PS 模型和结局模型）
    effect_modifiers : List[str]
        效应修饰变量（评估处理效应的异质性来源）
    method : str
        估计方法

    Returns
    -------
    Dict[str, Any]
        CATE 估计结果 + 异质性分析
    """
    try:
        from econml.dml import CausalForestDML, LinearDML
        from econml.dr import DRLearner
    except ImportError:
        raise ImportError("需要安装 EconML: pip install econml")

    X = df[features].values
    T = df[treatment].values
    Y = df[outcome].values

    # 效应修饰变量的索引
    mod_idx = [features.index(m) for m in effect_modifiers]

    print(f"\n[EconML] 异质性处理效应 (CATE) 估计")
    print(f"  方法: {method}")
    print(f"  效应修饰: {effect_modifiers}")

    if method == "causal_forest":
        est = CausalForestDML(
            model_t=LogisticRegression(max_iter=1000),
            model_y=None,
            discrete_treatment=True,
            n_estimators=200,
            max_depth=10,
            random_state=42,
        )
    elif method == "linear_dml":
        est = LinearDML(
            model_t=LogisticRegression(max_iter=1000),
            model_y=None,
            discrete_treatment=True,
            random_state=42,
        )
    else:
        raise ValueError(f"Unsupported method: {method}")

    est.fit(Y, T, X=X)

    # 平均 CATE
    cate_mean = est.effect(X).mean()
    cate_ci = est.effect_interval(X, alpha=0.05)
    cate_lower = cate_ci[0].mean()
    cate_upper = cate_ci[1].mean()

    # 按效应修饰变量分层的 CATE
    if len(effect_modifiers) == 1:
        mod = effect_modifiers[0]
        mod_vals = df[mod]
        cate_by_mod = pd.DataFrame({
            mod: mod_vals,
            "CATE": est.effect(X),
            "CATE_lower": cate_ci[0],
            "CATE_upper": cate_ci[1],
        }).groupby(mod).agg({
            "CATE": "mean",
            "CATE_lower": "mean",
            "CATE_upper": "mean",
        }).round(4)
    else:
        cate_by_mod = None

    print(f"  平均 CATE: {cate_mean:.4f} ({cate_lower:.4f}, {cate_upper:.4f})")
    if cate_by_mod is not None:
        print(f"\n  按修饰变量分层 CATE:\n{cate_by_mod}")

    return {
        "model": est,
        "ate": cate_mean,
        "ci_lower": cate_lower,
        "ci_upper": cate_upper,
        "cate_by_modifier": cate_by_mod,
        "cate_all": est.effect(X),
    }


# ============================================================================
# 4. E-value 敏感性分析
# ============================================================================


def e_value(estimate: float,
            lower_ci: Optional[float] = None,
            upper_ci: Optional[float] = None,
            true_estimate: float = 1.0) -> Dict[str, float]:
    """计算 E-value

    E-value 表示: 需要多大的未测量混杂因子才能推翻因果结论？
    - E-value 越大 → 结论越稳健
    - 公式: RR + sqrt(RR * (RR - 1))

    Parameters
    ----------
    estimate : float
        效应估计值 (RR/OR/HR)
    lower_ci : Optional[float]
        95% CI 下限
    upper_ci : Optional[float]
        95% CI 上限
    true_estimate : float
        无效应时的参考值 (通常为 1.0)

    Returns
    -------
    Dict[str, float]
        { "e_value_point": , "e_value_ci_lower": , "e_value_ci_upper": }
    """
    def _e_val(rr):
        if rr <= 1:
            return 1.0
        return rr + np.sqrt(rr * (rr - 1))

    # 转换 OR/HR 到近似的 RR
    def _or_to_rr(or_val):
        # 当结局罕见时 (<10%), OR ≈ RR
        return or_val

    rr_est = _or_to_rr(estimate)

    result = {
        "e_value_estimate": round(_e_val(rr_est), 3),
    }

    if lower_ci is not None:
        # CI 靠近真实值的极端
        if estimate > true_estimate:
            extreme_ci = lower_ci
        else:
            extreme_ci = upper_ci
        result["e_value_ci_extreme"] = round(_e_val(_or_to_rr(extreme_ci)), 3)

    print(f"\n=== E-value 分析 ===")
    print(f"  效应估计: {estimate:.4f}")
    print(f"  E-value (点估计): {result['e_value_estimate']}")
    if 'e_value_ci_extreme' in result:
        print(f"  E-value (CI 极端): {result['e_value_ci_extreme']}")
    print(f"  解释: 需要 E-value ≥ {result['e_value_estimate']} 倍")
    print(f"        的未测量混杂才能推翻因果结论")

    return result


# ============================================================================
# 5. 完整因果推断工作流
# ============================================================================


def full_causal_workflow(
    df: pd.DataFrame,
    treatment: str,
    outcome: str,
    confounders: List[str],
    effect_modifiers: Optional[List[str]] = None,
    outcome_type: str = "binary",
    show_cate: bool = False,
) -> Dict[str, Any]:
    """完整的因果推断工作流

    整合:
      1. DAG 构建
      2. DoWhy 标准因果效应估计
      3. E-value 敏感性分析
      4. (可选) CATE 异质性分析

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    treatment : str
        处理变量
    outcome : str
        结局变量
    confounders : List[str]
        需要调整的混杂因素
    effect_modifiers : Optional[List[str]]
        效应修饰变量
    outcome_type : str
        "binary" 或 "continuous"
    show_cate : bool
        是否进行 CATE 分析

    Returns
    -------
    Dict[str, Any]
    """
    from sklearn.linear_model import LogisticRegression

    results = {}

    print("=" * 60)
    print("  完整因果推断工作流")
    print("=" * 60)

    # --- Step 0: 描述统计 ---
    print("\n[Step 0] 描述性统计")
    n_treat = (df[treatment] == 1).sum()
    n_control = (df[treatment] == 0).sum()
    print(f"  处理组: n={n_treat}")
    print(f"  对照组: n={n_control}")
    print(f"  总样本: n={len(df)}")

    # --- Step 1: DAG ---
    print(f"\n[Step 1] 因果图 (DAG)")
    print(f"  暴露: {treatment}  →  结局: {outcome}")
    print(f"  混杂调整集 ({len(confounders)}): {confounders}")
    if effect_modifiers:
        print(f"  效应修饰: {effect_modifiers}")

    graph = build_causal_graph(treatment, outcome, confounders)
    results["causal_graph"] = graph

    # --- Step 2: DoWhy ---
    print(f"\n[Step 2] DoWhy 因果效应估计")

    # 根据 outcome_type 选择估计方法
    if outcome_type == "binary":
        method = "backdoor.propensity_score_matching"
    else:
        method = "backdoor.linear_regression"

    try:
        dowhy_results = estimate_causal_effect_dowhy(
            df, treatment, outcome, confounders,
            method=method,
        )
        results["dowhy"] = dowhy_results
    except ImportError:
        # 回退: 用简单的回归估计
        from sklearn.linear_model import LogisticRegression
        X = df[confounders].copy()
        X = pd.get_dummies(X, drop_first=True)
        X[treatment] = df[treatment]
        y = df[outcome]

        model = LogisticRegression(max_iter=1000).fit(
            X[confounders + [treatment]].fillna(X[confounders + [treatment]].median()),
            y
        )
        naive_or = np.exp(model.coef_[0][-1])
        results["dowhy"] = {
            "estimate": naive_or,
            "note": "DoWhy 不可用，使用 Logistic 回归近似估计",
        }
        print(f"  (回退) Logistic OR ≈ {naive_or:.4f}")

    # --- Step 3: E-value ---
    est = results["dowhy"]["estimate"]
    ci_lower = results["dowhy"].get("ci_lower")
    ci_upper = results["dowhy"].get("ci_upper")
    results["e_value"] = e_value(est, ci_lower, ci_upper)

    # --- Step 4: CATE (可选) ---
    if show_cate and effect_modifiers:
        try:
            cate_results = estimate_cate_econml(
                df, treatment, outcome,
                features=confounders + [treatment],
                effect_modifiers=effect_modifiers,
                method="causal_forest",
            )
            results["cate"] = cate_results
        except ImportError:
            print("  跳过 CATE: 请安装 EconML: pip install econml")

    print("\n" + "=" * 60)
    print("  因果推断工作流完成")
    print("=" * 60)

    return results


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    from sklearn.linear_model import LogisticRegression

    # 模拟观察性数据（有混杂）
    np.random.seed(42)
    n = 500

    # 混杂因素
    age = np.random.normal(55, 10, n)
    bmi = np.random.normal(27, 5, n)
    smoking = np.random.binomial(1, 0.35, n)

    # 处理分配（受混杂影响）
    logit_treat = -2.0 + 0.03 * age + 0.04 * bmi + 0.5 * smoking
    prob_treat = 1 / (1 + np.exp(-logit_treat))
    treatment = np.random.binomial(1, prob_treat)

    # 结局（受处理和混杂影响，真实 ATE ≈ 0.5 on log-odds scale）
    logit_outcome = -3.0 + 0.8 * treatment + 0.02 * age + 0.03 * bmi + 0.4 * smoking
    prob_outcome = 1 / (1 + np.exp(-logit_outcome))
    outcome = np.random.binomial(1, prob_outcome)

    df = pd.DataFrame({
        "treatment": treatment,
        "outcome": outcome,
        "age": age,
        "bmi": bmi,
        "smoking": smoking,
    })

    # 运行完整因果推断工作流
    results = full_causal_workflow(
        df,
        treatment="treatment",
        outcome="outcome",
        confounders=["age", "bmi", "smoking"],
        effect_modifiers=["age"],  # 研究年龄是否修饰处理效应
        outcome_type="binary",
        show_cate=False,
    )

    print("\n✅ 因果推断分析完成")
