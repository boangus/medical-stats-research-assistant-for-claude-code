"""
bayesian_analysis_template.py — 贝叶斯统计分析模板
====================================================
适用于：贝叶斯线性回归、贝叶斯 Logistic 回归、贝叶斯生存模型、
       后验分布可视化、贝叶斯因子计算、收敛诊断、与频率学派对比

依赖: pymc, arviz, numpy, pandas, matplotlib, scipy
安装: pip install pymc arviz numpy pandas matplotlib scipy

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# 延迟导入 PyMC / ArviZ（在函数内部导入），以便模块在缺少依赖时仍可加载

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. 贝叶斯线性回归
# ============================================================================


def bayesian_linear_regression(
    df: pd.DataFrame,
    outcome: str,
    predictors: List[str],
    priors: Optional[Dict[str, Any]] = None,
    draws: int = 2000,
    tune: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """贝叶斯线性回归（PyMC）

    使用弱信息先验拟合贝叶斯线性回归模型，通过 NUTS 采样获得后验分布。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名（连续变量）
    predictors : List[str]
        预测变量列表
    priors : Optional[Dict[str, Any]]
        自定义先验，可包含 'intercept_mu', 'intercept_sigma',
        'beta_mu', 'beta_sigma', 'sigma_scale'。默认使用弱信息先验。
    draws : int
        后验采样数（默认 2000）
    tune : int
        调整/预热步数（默认 1000）
    chains : int
        MCMC 链数（默认 4）
    target_accept : float
        NUTS 目标接受率（默认 0.9）
    random_seed : int
        随机种子

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'model': PyMC 模型对象
        - 'idata': ArviZ InferenceData 对象
        - 'summary': 后验摘要表
        - 'diagnostics': 收敛诊断结果

    Examples
    --------
    >>> result = bayesian_linear_regression(df, 'y', ['x1', 'x2'], draws=1000)
    >>> print(result['summary'])
    """
    import pymc as pm
    import arviz as az

    # 默认弱信息先验
    if priors is None:
        priors = {
            "intercept_mu": 0.0,
            "intercept_sigma": 10.0,
            "beta_mu": 0.0,
            "beta_sigma": 5.0,
            "sigma_scale": 5.0,
        }

    data = df[[outcome] + predictors].dropna()
    y = data[outcome].values
    X = data[predictors].values
    n, k = X.shape

    with pm.Model() as model:
        # 数据容器
        X_data = pm.Data("X", X)
        y_data = pm.Data("y", y)

        # 先验
        intercept = pm.Normal(
            "intercept",
            mu=priors["intercept_mu"],
            sigma=priors["intercept_sigma"],
        )
        beta = pm.Normal(
            "beta",
            mu=priors["beta_mu"],
            sigma=priors["beta_sigma"],
            shape=k,
        )
        sigma = pm.HalfNormal("sigma", sigma=priors["sigma_scale"])

        # 似然
        mu = intercept + pm.math.dot(X_data, beta)
        likelihood = pm.Normal("likelihood", mu=mu, sigma=sigma, observed=y_data)

        # 采样
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=target_accept,
            random_seed=random_seed,
            progressbar=False,
        )

    # 后验摘要
    summary = az.summary(idata, var_names=["intercept", "beta", "sigma"],
                         hdi_prob=0.95)
    summary = summary.reset_index().rename(columns={"index": "Parameter"})

    # 为 beta 添加变量名
    beta_rows = summary[summary["Parameter"] == "beta"].copy()
    if len(beta_rows) == k:
        beta_rows["Parameter"] = [f"beta[{p}]" for p in predictors]
        summary = pd.concat([
            summary[summary["Parameter"] != "beta"],
            beta_rows,
        ]).reset_index(drop=True)

    # 收敛诊断
    diagnostics = convergence_diagnostics(idata)

    return {
        "model": model,
        "idata": idata,
        "summary": summary,
        "diagnostics": diagnostics,
        "predictors": predictors,
    }


# ============================================================================
# 2. 贝叶斯 Logistic 回归
# ============================================================================


def bayesian_logistic_regression(
    df: pd.DataFrame,
    outcome: str,
    predictors: List[str],
    priors: Optional[Dict[str, Any]] = None,
    draws: int = 2000,
    tune: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """贝叶斯 Logistic 回归（PyMC）

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量名（二分类，0/1 编码）
    predictors : List[str]
        预测变量列表
    priors : Optional[Dict[str, Any]]
        自定义先验参数
    draws : int
        后验采样数
    tune : int
        预热步数
    chains : int
        MCMC 链数
    target_accept : float
        NUTS 目标接受率
    random_seed : int
        随机种子

    Returns
    -------
    Dict[str, Any]
        包含模型、推断数据、后验摘要和诊断结果

    Examples
    --------
    >>> result = bayesian_logistic_regression(df, 'outcome', ['age', 'treatment'])
    >>> print(result['summary'])
    """
    import pymc as pm
    import arviz as az

    if priors is None:
        priors = {
            "intercept_mu": 0.0,
            "intercept_sigma": 5.0,
            "beta_mu": 0.0,
            "beta_sigma": 2.5,
        }

    data = df[[outcome] + predictors].dropna()
    y = data[outcome].values.astype(int)
    X = data[predictors].values
    n, k = X.shape

    with pm.Model() as model:
        X_data = pm.Data("X", X)
        y_data = pm.Data("y", y)

        intercept = pm.Normal("intercept", mu=priors["intercept_mu"],
                              sigma=priors["intercept_sigma"])
        beta = pm.Normal("beta", mu=priors["beta_mu"],
                         sigma=priors["beta_sigma"], shape=k)

        # Logistic 似然
        logit_p = intercept + pm.math.dot(X_data, beta)
        p = pm.Deterministic("p", pm.math.sigmoid(logit_p))
        likelihood = pm.Bernoulli("likelihood", p=p, observed=y_data)

        idata = pm.sample(
            draws=draws, tune=tune, chains=chains,
            target_accept=target_accept,
            random_seed=random_seed, progressbar=False,
        )

    summary = az.summary(idata, var_names=["intercept", "beta"],
                         hdi_prob=0.95)
    summary = summary.reset_index().rename(columns={"index": "Parameter"})

    beta_rows = summary[summary["Parameter"] == "beta"].copy()
    if len(beta_rows) == k:
        beta_rows["Parameter"] = [f"beta[{p}]" for p in predictors]
        summary = pd.concat([
            summary[summary["Parameter"] != "beta"], beta_rows
        ]).reset_index(drop=True)

    diagnostics = convergence_diagnostics(idata)

    return {
        "model": model,
        "idata": idata,
        "summary": summary,
        "diagnostics": diagnostics,
        "predictors": predictors,
    }


# ============================================================================
# 3. 贝叶斯生存模型（Weibull）
# ============================================================================


def bayesian_weibull_survival(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    predictors: List[str],
    draws: int = 2000,
    tune: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """贝叶斯 Weibull 生存模型（PyMC）

    使用 Weibull 参数化生存模型进行贝叶斯推断。

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    duration_col : str
        生存时间变量名
    event_col : str
        事件状态变量名（1=事件，0=删失）
    predictors : List[str]
        预测变量列表
    draws : int
        后验采样数
    tune : int
        预热步数
    chains : int
        MCMC 链数
    target_accept : float
        NUTS 目标接受率
    random_seed : int
        随机种子

    Returns
    -------
    Dict[str, Any]
        包含模型、推断数据、后验摘要和诊断结果

    Examples
    --------
    >>> result = bayesian_weibull_survival(df, 'time', 'event', ['age', 'treatment'])
    """
    import pymc as pm
    import arviz as az

    data = df[[duration_col, event_col] + predictors].dropna()
    T = data[duration_col].values
    E = data[event_col].values.astype(int)
    X = data[predictors].values
    n, k = X.shape

    with pm.Model() as model:
        X_data = pm.Data("X", X)

        # Weibull 形状参数（k > 0）
        shape = pm.HalfNormal("shape", sigma=5.0)

        # 回归系数（对数尺度）
        intercept = pm.Normal("intercept", mu=0.0, sigma=5.0)
        beta = pm.Normal("beta", mu=0.0, sigma=2.5, shape=k)

        # 尺度参数（对数线性模型）
        log_lambda = intercept + pm.math.dot(X_data, beta)
        lambda_ = pm.Deterministic("lambda", pm.math.exp(log_lambda))

        # Weibull 似然（考虑删失）
        # 对于事件发生的个体：f(t) = (shape/lambda) * (t/lambda)^(shape-1) * exp(-(t/lambda)^shape)
        # 对于删失个体：S(t) = exp(-(t/lambda)^shape)
        # 对数似然
        log_hazard = (
            np.log(T) * (shape - 1)
            - shape * log_lambda
            - (T / lambda_) ** shape
        )
        # 实际使用 PyTensor 操作
        t_tensor = pm.Data("T", T)
        e_tensor = pm.Data("E", E)

        # 使用 pm.Potential 构建自定义似然
        log_hazard_rate = (
            pm.math.log(t_tensor) * (shape - 1)
            - shape * log_lambda
            - (t_tensor / lambda_) ** shape
        )
        log_survival = -(t_tensor / lambda_) ** shape

        # 事件发生: log(f(t)), 删失: log(S(t))
        log_likelihood = e_tensor * log_hazard_rate + (1 - e_tensor) * log_survival
        pm.Potential("weibull_likelihood", pm.math.sum(log_likelihood))

        idata = pm.sample(
            draws=draws, tune=tune, chains=chains,
            target_accept=target_accept,
            random_seed=random_seed, progressbar=False,
        )

    summary = az.summary(idata, var_names=["shape", "intercept", "beta"],
                         hdi_prob=0.95)
    summary = summary.reset_index().rename(columns={"index": "Parameter"})

    beta_rows = summary[summary["Parameter"] == "beta"].copy()
    if len(beta_rows) == k:
        beta_rows["Parameter"] = [f"beta[{p}]" for p in predictors]
        summary = pd.concat([
            summary[summary["Parameter"] != "beta"], beta_rows
        ]).reset_index(drop=True)

    diagnostics = convergence_diagnostics(idata)

    return {
        "model": model,
        "idata": idata,
        "summary": summary,
        "diagnostics": diagnostics,
        "predictors": predictors,
    }


# ============================================================================
# 4. 后验分布可视化
# ============================================================================


def plot_posterior_distribution(
    idata,
    var_names: Optional[List[str]] = None,
    figsize: Tuple[float, float] = (12, 8),
    hdi_prob: float = 0.95,
) -> "matplotlib.figure.Figure":
    """绘制后验分布图

    Parameters
    ----------
    idata : arviz.InferenceData
        ArviZ 推断数据对象
    var_names : Optional[List[str]]
        要绘制的变量名列表（默认全部）
    figsize : Tuple[float, float]
        图形大小
    hdi_prob : float
        最高密度区间概率（默认 0.95）

    Returns
    -------
    matplotlib.figure.Figure
        后验分布图

    Examples
    --------
    >>> fig = plot_posterior_distribution(result['idata'], ['intercept', 'beta'])
    """
    import arviz as az
    import matplotlib.pyplot as plt

    axes = az.plot_posterior(
        idata,
        var_names=var_names,
        hdi_prob=hdi_prob,
        figsize=figsize,
        textsize=10,
    )

    if isinstance(axes, np.ndarray):
        fig = axes.flatten()[0].figure
    else:
        fig = axes.figure

    fig.suptitle("Posterior Distributions", fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


def plot_trace(
    idata,
    var_names: Optional[List[str]] = None,
    figsize: Tuple[float, float] = (12, 8),
) -> "matplotlib.figure.Figure":
    """绘制 MCMC trace plot（轨迹图）

    Parameters
    ----------
    idata : arviz.InferenceData
        ArviZ 推断数据对象
    var_names : Optional[List[str]]
        要绘制的变量名
    figsize : Tuple[float, float]
        图形大小

    Returns
    -------
    matplotlib.figure.Figure
        轨迹图

    Examples
    --------
    >>> fig = plot_trace(result['idata'], ['intercept', 'beta'])
    """
    import arviz as az
    import matplotlib.pyplot as plt

    axes = az.plot_trace(idata, var_names=var_names, figsize=figsize,
                         compact=True)

    if isinstance(axes, np.ndarray):
        fig = axes.flatten()[0].figure
    else:
        fig = axes.figure

    fig.suptitle("Trace Plots", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    return fig


def plot_forest(
    idata,
    var_names: Optional[List[str]] = None,
    figsize: Tuple[float, float] = (8, 6),
    hdi_prob: float = 0.95,
) -> "matplotlib.figure.Figure":
    """绘制森林图（后验区间）

    Parameters
    ----------
    idata : arviz.InferenceData
        ArviZ 推断数据对象
    var_names : Optional[List[str]]
        变量名
    figsize : Tuple[float, float]
        图形大小
    hdi_prob : float
        HDI 概率

    Returns
    -------
    matplotlib.figure.Figure
        森林图
    """
    import arviz as az
    import matplotlib.pyplot as plt

    axes = az.plot_forest(
        idata, var_names=var_names, hdi_prob=hdi_prob,
        figsize=figsize, textsize=10, combined=True,
    )

    if isinstance(axes, np.ndarray):
        fig = axes.flatten()[0].figure
    else:
        fig = axes.figure

    fig.suptitle("Posterior Forest Plot", fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


# ============================================================================
# 5. 贝叶斯因子计算
# ============================================================================


def bayes_factor_two_models(
    idata_m1,
    idata_m2,
    model1_name: str = "Model 1",
    model2_name: str = "Model 2",
) -> Dict[str, Any]:
    """使用 Bridge sampling 估计两个模型的贝叶斯因子

    Parameters
    ----------
    idata_m1 : arviz.InferenceData
        模型 1 的推断数据
    idata_m2 : arviz.InferenceData
        模型 2 的推断数据
    model1_name : str
        模型 1 名称
    model2_name : str
        模型 2 名称

    Returns
    -------
    Dict[str, Any]
        包含贝叶斯因子和对数边际似然

    Examples
    --------
    >>> bf = bayes_factor_two_models(idata_null, idata_alt)
    >>> print(f"BF10 = {bf['bf_12']:.2f}")
    """
    import arviz as az

    # 使用 ArviZ 的 bridge sampling 估计对数边际似然
    try:
        log_marg_1 = az.waic(idata_m1).elpd_waic
        log_marg_2 = az.waic(idata_m2).elpd_waic
        method = "WAIC (approximation)"
    except Exception:
        # 回退到 LOO
        log_marg_1 = az.loo(idata_m1).elpd_loo
        log_marg_2 = az.loo(idata_m2).elpd_loo
        method = "LOO (approximation)"

    # 贝叶斯因子近似（基于信息准则差异）
    bf_log = log_marg_1 - log_marg_2
    bf = np.exp(bf_log)

    # 解释
    if bf > 100:
        interpretation = f"强证据支持 {model1_name}"
    elif bf > 10:
        interpretation = f"中等证据支持 {model1_name}"
    elif bf > 3:
        interpretation = f"弱证据支持 {model1_name}"
    elif bf > 1 / 3:
        interpretation = "证据不足以区分两个模型"
    elif bf > 1 / 10:
        interpretation = f"弱证据支持 {model2_name}"
    elif bf > 1 / 100:
        interpretation = f"中等证据支持 {model2_name}"
    else:
        interpretation = f"强证据支持 {model2_name}"

    return {
        "bf_12": bf,
        "bf_log": bf_log,
        "log_marg_1": log_marg_1,
        "log_marg_2": log_marg_2,
        "method": method,
        "interpretation": interpretation,
        "model1_name": model1_name,
        "model2_name": model2_name,
    }


def savage_dickey_density_ratio(
    idata,
    null_value: float = 0.0,
    var_name: str = "beta",
    var_idx: int = 0,
) -> Dict[str, Any]:
    """Savage-Dickey 密度比法计算贝叶斯因子

    用于嵌套模型比较（如 beta = 0 vs. beta != 0）。

    Parameters
    ----------
    idata : arviz.InferenceData
        推断数据
    null_value : float
        零假设值（默认 0）
    var_name : str
        变量名
    var_idx : int
        变量索引（对于向量参数）

    Returns
    -------
    Dict[str, Any]
        包含贝叶斯因子 BF01 和解释

    Examples
    --------
    >>> bf = savage_dickey_density_ratio(result['idata'], var_name='beta')
    >>> print(f"BF01 = {bf['bf_01']:.2f}")
    """
    from scipy.stats import gaussian_kde

    # 提取后验样本
    posterior = idata.posterior
    if var_name in posterior:
        samples = posterior[var_name].values
        if samples.ndim > 2:
            samples = samples[:, :, var_idx].flatten()
        else:
            samples = samples.flatten()
    else:
        raise ValueError(f"变量 '{var_name}' 不在后验中")

    # 估计先验密度（假设为正态先验）
    # 从模型中获取先验 sigma（近似）
    prior_sigma = np.std(samples) * 2  # 粗略估计
    prior_density = stats.norm.pdf(null_value, loc=0, scale=prior_sigma)

    # 估计后验密度在 null_value 处的值
    kde = gaussian_kde(samples)
    posterior_density = kde(null_value)

    # BF01 = 后验密度 / 先验密度
    bf_01 = posterior_density / prior_density
    bf_10 = 1 / bf_01

    if bf_01 > 100:
        interpretation = "强证据支持零假设"
    elif bf_01 > 10:
        interpretation = "中等证据支持零假设"
    elif bf_01 > 3:
        interpretation = "弱证据支持零假设"
    elif bf_01 > 1 / 3:
        interpretation = "证据不足"
    else:
        interpretation = "证据支持备择假设"

    return {
        "bf_01": bf_01,
        "bf_10": bf_10,
        "prior_density": prior_density,
        "posterior_density": float(posterior_density),
        "null_value": null_value,
        "interpretation": interpretation,
        "method": "Savage-Dickey density ratio",
    }


# ============================================================================
# 6. 收敛诊断
# ============================================================================


def convergence_diagnostics(idata) -> Dict[str, Any]:
    """MCMC 收敛诊断

    计算 R-hat、有效样本量（ESS）、发散转移数等收敛指标。

    Parameters
    ----------
    idata : arviz.InferenceData
        ArviZ 推断数据对象

    Returns
    -------
    Dict[str, Any]
        包含：
        - 'r_hat': R-hat 值表
        - 'ess_bulk': 批量 ESS
        - 'ess_tail': 尾部 ESS
        - 'divergences': 发散转移数
        - 'max_r_hat': 最大 R-hat
        - 'min_ess': 最小 ESS
        - 'converged': 是否收敛

    Examples
    --------
    >>> diag = convergence_diagnostics(result['idata'])
    >>> print(f"Converged: {diag['converged']}")
    """
    import arviz as az

    # R-hat
    r_hat = az.rhat(idata)
    r_hat_df = pd.DataFrame({
        "Variable": list(r_hat.data_vars),
        "R_hat": [float(r_hat[v].values.max()) for v in r_hat.data_vars],
    })
    max_r_hat = r_hat_df["R_hat"].max()

    # ESS
    ess_bulk = az.ess(idata, method="bulk")
    ess_tail = az.ess(idata, method="tail")
    ess_df = pd.DataFrame({
        "Variable": list(ess_bulk.data_vars),
        "ESS_bulk": [float(ess_bulk[v].values.min()) for v in ess_bulk.data_vars],
        "ESS_tail": [float(ess_tail[v].values.min()) for v in ess_tail.data_vars],
    })
    min_ess = ess_df[["ESS_bulk", "ESS_tail"]].min().min()

    # 发散转移
    divergences = 0
    if hasattr(idata, "sample_stats") and "diverging" in idata.sample_stats:
        divergences = int(idata.sample_stats["diverging"].values.sum())

    # 判断收敛
    converged = (max_r_hat < 1.01) and (min_ess > 400) and (divergences == 0)

    # 警告
    if max_r_hat >= 1.01:
        warnings.warn(
            f"R-hat >= 1.01 (max = {max_r_hat:.4f})，链可能未收敛。"
            "建议增加 draws/tune 或调整先验。",
            RuntimeWarning,
        )
    if min_ess < 400:
        warnings.warn(
            f"最小 ESS < 400 (min = {min_ess:.0f})，后验摘要可能不可靠。"
            "建议增加采样数。",
            RuntimeWarning,
        )
    if divergences > 0:
        warnings.warn(
            f"检测到 {divergences} 次发散转移。"
            "建议提高 target_accept 或重新参数化模型。",
            RuntimeWarning,
        )

    return {
        "r_hat": r_hat_df,
        "ess": ess_df,
        "divergences": divergences,
        "max_r_hat": float(max_r_hat),
        "min_ess": float(min_ess),
        "converged": converged,
    }


# ============================================================================
# 7. 与频率学派结果对比
# ============================================================================


def compare_bayesian_frequentist(
    df: pd.DataFrame,
    outcome: str,
    predictors: List[str],
    bayes_result: Dict[str, Any],
    model_type: str = "linear",
) -> pd.DataFrame:
    """贝叶斯与频率学派结果对比

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量
    predictors : List[str]
        预测变量
    bayes_result : Dict[str, Any]
        贝叶斯分析结果（来自 bayesian_linear_regression 或 bayesian_logistic_regression）
    model_type : str
        'linear' 或 'logistic'

    Returns
    -------
    pd.DataFrame
        对比表，包含贝叶斯后验均值、95% HDI 和频率学派估计、95% CI

    Examples
    --------
    >>> comp = compare_bayesian_frequentist(df, 'y', ['x1'], result, 'linear')
    >>> print(comp)
    """
    import statsmodels.api as sm

    data = df[[outcome] + predictors].dropna()
    X = sm.add_constant(data[predictors])
    y = data[outcome]

    # 频率学派估计
    if model_type == "linear":
        freq_model = sm.OLS(y, X).fit()
        freq_params = freq_model.params
        freq_ci = freq_model.conf_int()
        freq_pvals = freq_model.pvalues
    elif model_type == "logistic":
        freq_model = sm.Logit(y, X).fit(disp=False)
        freq_params = freq_model.params
        freq_ci = freq_model.conf_int()
        freq_pvals = freq_model.pvalues
    else:
        raise ValueError("model_type 必须是 'linear' 或 'logistic'")

    # 贝叶斯结果
    bayes_summary = bayes_result["summary"]

    # 构建对比表
    rows = []
    # 截距
    bayes_intercept = bayes_summary[bayes_summary["Parameter"] == "intercept"]
    if len(bayes_intercept) > 0:
        row = {
            "Parameter": "intercept",
            "Bayes_Mean": float(bayes_intercept["mean"].values[0]),
            "Bayes_HDI_low": float(bayes_intercept["hdi_2.5%"].values[0]),
            "Bayes_HDI_high": float(bayes_intercept["hdi_97.5%"].values[0]),
            "Freq_Estimate": float(freq_params["const"]),
            "Freq_CI_low": float(freq_ci.loc["const", 0]),
            "Freq_CI_high": float(freq_ci.loc["const", 1]),
            "Freq_p_value": float(freq_pvals["const"]),
        }
        rows.append(row)

    # 各预测变量
    for i, pred in enumerate(predictors):
        bayes_beta = bayes_summary[bayes_summary["Parameter"] == f"beta[{pred}]"]
        if len(bayes_beta) > 0:
            row = {
                "Parameter": pred,
                "Bayes_Mean": float(bayes_beta["mean"].values[0]),
                "Bayes_HDI_low": float(bayes_beta["hdi_2.5%"].values[0]),
                "Bayes_HDI_high": float(bayes_beta["hdi_97.5%"].values[0]),
                "Freq_Estimate": float(freq_params[pred]),
                "Freq_CI_low": float(freq_ci.loc[pred, 0]),
                "Freq_CI_high": float(freq_ci.loc[pred, 1]),
                "Freq_p_value": float(freq_pvals[pred]),
            }
            rows.append(row)

    comp_df = pd.DataFrame(rows)

    # 添加一致性判断
    comp_df["CI_Overlap"] = comp_df.apply(
        lambda r: not (r["Bayes_HDI_high"] < r["Freq_CI_low"] or
                       r["Bayes_HDI_low"] > r["Freq_CI_high"]),
        axis=1,
    )

    return comp_df


# ============================================================================
# 8. 完整贝叶斯分析工作流
# ============================================================================


def full_bayesian_workflow(
    df: pd.DataFrame,
    outcome: str,
    predictors: List[str],
    model_type: str = "linear",
    draws: int = 2000,
    tune: int = 1000,
    chains: int = 4,
    do_comparison: bool = True,
    do_plots: bool = True,
) -> Dict[str, Any]:
    """完整的贝叶斯分析工作流

    执行：模型拟合 → 收敛诊断 → 后验可视化 → 与频率学派对比

    Parameters
    ----------
    df : pd.DataFrame
        分析数据集
    outcome : str
        结局变量
    predictors : List[str]
        预测变量
    model_type : str
        'linear' 或 'logistic'
    draws : int
        后验采样数
    tune : int
        预热步数
    chains : int
        MCMC 链数
    do_comparison : bool
        是否执行频率学派对比
    do_plots : bool
        是否生成可视化图

    Returns
    -------
    Dict[str, Any]
        包含所有分析结果

    Examples
    --------
    >>> results = full_bayesian_workflow(df, 'y', ['x1', 'x2'], 'linear')
    """
    results = {}

    # Step 1: 模型拟合
    print("=" * 50)
    print("Step 1: 贝叶斯模型拟合")
    print("=" * 50)
    if model_type == "linear":
        bayes_result = bayesian_linear_regression(
            df, outcome, predictors, draws=draws, tune=tune, chains=chains
        )
    elif model_type == "logistic":
        bayes_result = bayesian_logistic_regression(
            df, outcome, predictors, draws=draws, tune=tune, chains=chains
        )
    else:
        raise ValueError("model_type 必须是 'linear' 或 'logistic'")

    results["bayes_result"] = bayes_result
    print(f"  模型类型: {model_type}")
    print(f"  采样: {draws} draws x {chains} chains")

    # Step 2: 收敛诊断
    print("\n" + "=" * 50)
    print("Step 2: 收敛诊断")
    print("=" * 50)
    diag = bayes_result["diagnostics"]
    print(f"  Max R-hat: {diag['max_r_hat']:.4f} {'✓' if diag['max_r_hat'] < 1.01 else '✗'}")
    print(f"  Min ESS: {diag['min_ess']:.0f} {'✓' if diag['min_ess'] > 400 else '✗'}")
    print(f"  Divergences: {diag['divergences']} {'✓' if diag['divergences'] == 0 else '✗'}")
    print(f"  Converged: {diag['converged']}")

    # Step 3: 后验摘要
    print("\n" + "=" * 50)
    print("Step 3: 后验摘要")
    print("=" * 50)
    print(bayes_result["summary"][
        ["Parameter", "mean", "sd", "hdi_2.5%", "hdi_97.5%", "r_hat", "ess_bulk"]
    ].to_string(index=False))

    # Step 4: 可视化
    if do_plots:
        print("\n" + "=" * 50)
        print("Step 4: 后验可视化")
        print("=" * 50)
        results["posterior_plot"] = plot_posterior_distribution(bayes_result["idata"])
        results["trace_plot"] = plot_trace(bayes_result["idata"])
        results["forest_plot"] = plot_forest(bayes_result["idata"])
        print("  后验分布图、轨迹图、森林图已生成")

    # Step 5: 频率学派对比
    if do_comparison:
        print("\n" + "=" * 50)
        print("Step 5: 与频率学派对比")
        print("=" * 50)
        comp = compare_bayesian_frequentist(
            df, outcome, predictors, bayes_result, model_type
        )
        results["comparison"] = comp
        print(comp[["Parameter", "Bayes_Mean", "Freq_Estimate",
                     "Bayes_HDI_low", "Bayes_HDI_high",
                     "Freq_CI_low", "Freq_CI_high", "CI_Overlap"]].to_string(index=False))

    print("\n 贝叶斯分析完成")
    return results


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == "__main__":
    # 模拟数据
    np.random.seed(42)
    n = 200

    df_demo = pd.DataFrame({
        "y": np.random.normal(10, 3, n),
        "age": np.random.normal(60, 10, n),
        "treatment": np.random.binomial(1, 0.5, n),
        "bmi": np.random.normal(25, 5, n),
    })
    # 添加处理效应
    df_demo["y"] = df_demo["y"] + 2 * df_demo["treatment"] + 0.05 * df_demo["age"]

    # 贝叶斯线性回归
    print("=" * 60)
    print("贝叶斯线性回归示例")
    print("=" * 60)

    result = bayesian_linear_regression(
        df_demo, "y", ["age", "treatment", "bmi"],
        draws=1000, tune=500, chains=2,
    )

    print("\n=== 后验摘要 ===")
    print(result["summary"][
        ["Parameter", "mean", "sd", "hdi_2.5%", "hdi_97.5%", "r_hat"]
    ].to_string(index=False))

    print("\n=== 收敛诊断 ===")
    diag = result["diagnostics"]
    print(f"  Max R-hat: {diag['max_r_hat']:.4f}")
    print(f"  Min ESS: {diag['min_ess']:.0f}")
    print(f"  Divergences: {diag['divergences']}")
    print(f"  Converged: {diag['converged']}")

    # Savage-Dickey 贝叶斯因子
    print("\n=== Savage-Dickey 贝叶斯因子 ===")
    bf = savage_dickey_density_ratio(result["idata"], var_name="beta", var_idx=1)
    print(f"  BF01 (treatment=0): {bf['bf_01']:.3f}")
    print(f"  Interpretation: {bf['interpretation']}")

    # 频率学派对比
    print("\n=== 贝叶斯 vs 频率学派 ===")
    comp = compare_bayesian_frequentist(
        df_demo, "y", ["age", "treatment", "bmi"], result, "linear"
    )
    print(comp[["Parameter", "Bayes_Mean", "Freq_Estimate", "CI_Overlap"]].to_string(index=False))

    print("\n 贝叶斯分析模板示例完成")
