"""
sample_size_template.py — 样本量计算与报告生成模板
=====================================================
适用于：临床试验和观察性研究的样本量/把握度计算及 Markdown 报告生成

本模板封装 shared/sample-size/sample_size_calculator.py 中的计算器，
提供统一的报告生成接口，支持多种研究设计的样本量计算、把握度分析、
反向把握度计算，并输出结构化的 Markdown 报告。

依赖: scipy, numpy, pandas, statsmodels
安装: pip install scipy numpy pandas statsmodels

作者: MSRA Team
版本: 0.1.0
"""

import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats
import logging

logger = logging.getLogger(__name__)

# 尝试导入已有的样本量计算器
try:
    from shared.sample_size.sample_size_calculator import (
        calc_power_t,
        calc_sample_size_anova,
        calc_sample_size_diagnostic,
        calc_sample_size_logistic,
        calc_sample_size_noninf,
        calc_sample_size_paired_t,
        calc_sample_size_prop,
        calc_sample_size_survival,
        calc_sample_size_t,
    )

    _HAS_CALCULATOR = True
except ImportError:
    _HAS_CALCULATOR = False

# 抑制 pandas/numpy 的 FutureWarning 和 SettingWithCopyWarning，
# 但保留 ConvergenceWarning / RuntimeWarning / DeprecationWarning
# 以便在医学统计分析中及时发现数值收敛和方法弃用问题。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ============================================================================
# 1. 样本量计算（封装已有计算器 + 补充缺失设计）
# ============================================================================


def calculate_sample_size(
    design: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """统一的样本量计算入口

    根据研究设计类型调用对应的计算函数。

    Parameters
    ----------
    design : str
        研究设计类型，支持：
        - 't_test': 两独立样本 t 检验
        - 'paired_t': 配对 t 检验
        - 'proportion': 两样本率比较
        - 'anova': 单因素方差分析
        - 'survival': 生存分析（Schoenfeld 公式）
        - 'logistic': Logistic 回归（EPV 规则）
        - 'noninferiority': 非劣效性试验
        - 'diagnostic': 诊断试验
    params : Dict[str, Any]
        计算参数，各设计所需参数不同

    Returns
    -------
    Dict[str, Any]
        样本量计算结果

    Examples
    --------
    >>> result = calculate_sample_size('t_test', {'delta': 5, 'sd': 10})
    >>> print(result['n_total'])
    """
    if _HAS_CALCULATOR:
        _dispatch = {
            "t_test": calc_sample_size_t,
            "paired_t": calc_sample_size_paired_t,
            "proportion": calc_sample_size_prop,
            "anova": calc_sample_size_anova,
            "survival": calc_sample_size_survival,
            "logistic": calc_sample_size_logistic,
            "noninferiority": calc_sample_size_noninf,
            "diagnostic": calc_sample_size_diagnostic,
        }
    else:
        _dispatch = {
            "t_test": _calc_t_test,
            "paired_t": _calc_paired_t,
            "proportion": _calc_proportion,
            "anova": _calc_anova,
            "survival": _calc_survival,
            "logistic": _calc_logistic_epv,
            "noninferiority": _calc_noninferiority,
            "diagnostic": _calc_diagnostic,
        }

    if design not in _dispatch:
        raise ValueError(
            f"不支持的设计类型 '{design}'。支持: {list(_dispatch.keys())}"
        )

    result = _dispatch[design](**params)
    result["design"] = design
    return result


# --- 内置计算函数（当无法导入已有计算器时的回退实现） ---


def _calc_t_test(delta, sd, alpha=0.05, power=0.80, ratio=1.0, sided="two.sided"):
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z_beta = stats.norm.ppf(power)
    d = delta / sd
    n_per_group = int(np.ceil(2 * (z_alpha + z_beta) ** 2 / d ** 2))
    return {
        "n_total": n_per_group + int(np.ceil(n_per_group * ratio)),
        "n1": n_per_group,
        "n2": int(np.ceil(n_per_group * ratio)),
        "n_per_group": n_per_group,
        "power": power,
        "delta": delta,
        "sd": sd,
        "d": d,
        "alpha": alpha,
        "method": "Two-sample t-test",
    }


def _calc_paired_t(delta, sd_diff, alpha=0.05, power=0.80, sided="two.sided"):
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z_beta = stats.norm.ppf(power)
    d = delta / sd_diff
    n = int(np.ceil((z_alpha + z_beta) ** 2 / d ** 2))
    return {"n": n, "power": power, "d": d, "alpha": alpha, "method": "Paired t-test"}


def _calc_proportion(p1, p2, alpha=0.05, power=0.80, ratio=1.0, sided="two.sided"):
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z_beta = stats.norm.ppf(power)
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
    n_per_group = int(np.ceil((z_alpha + z_beta) ** 2 * 2 / h ** 2))
    return {
        "n_total": n_per_group + int(np.ceil(n_per_group * ratio)),
        "n1": n_per_group,
        "n2": int(np.ceil(n_per_group * ratio)),
        "n_per_group": n_per_group,
        "power": power,
        "p1": p1,
        "p2": p2,
        "h": abs(h),
        "alpha": alpha,
        "method": "Two-sample proportion test",
    }


def _calc_anova(k, f, alpha=0.05, power=0.80):
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n_per_group = int(np.ceil((z_alpha + z_beta) ** 2 / (f ** 2) + k / (2 * f)))
    return {
        "n_per_group": n_per_group,
        "n_total": n_per_group * k,
        "power": power,
        "f": f,
        "alpha": alpha,
        "method": "One-way ANOVA",
    }


def _calc_survival(hr, prop_event=0.5, alpha=0.05, power=0.80, sided="two.sided"):
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z_beta = stats.norm.ppf(power)
    n_events = int(
        np.ceil(
            (z_alpha + z_beta) ** 2
            / ((np.log(hr)) ** 2 * prop_event * (1 - prop_event))
        )
    )
    n_total = int(np.ceil(n_events / prop_event))
    return {
        "n_events": n_events,
        "n_total": n_total,
        "n_per_group": int(np.ceil(n_total / 2)),
        "hr": hr,
        "prop_event": prop_event,
        "power": power,
        "alpha": alpha,
        "method": "Survival analysis (Schoenfeld)",
    }


def _calc_logistic_epv(n_predictors, prop_events, epv=10):
    n_events = n_predictors * epv
    n_total = int(np.ceil(n_events / prop_events))
    return {
        "n_total": n_total,
        "n_events": n_events,
        "n_predictors": n_predictors,
        "epv": epv,
        "prop_events": prop_events,
        "method": "Logistic regression (EPV rule)",
    }


def _calc_noninferiority(delta, sd, alpha=0.025, power=0.80):
    z_alpha = stats.norm.ppf(1 - alpha)
    z_beta = stats.norm.ppf(power)
    n_per_group = int(np.ceil(2 * (z_alpha + z_beta) ** 2 * sd ** 2 / delta ** 2))
    return {
        "n_per_group": n_per_group,
        "n_total": n_per_group * 2,
        "delta": delta,
        "sd": sd,
        "alpha": alpha,
        "power": power,
        "method": "Non-inferiority trial",
    }


def _calc_diagnostic(sensitivity, specificity, prevalence, ci_width=0.10, alpha=0.05):
    z = stats.norm.ppf(1 - alpha / 2)
    n_pos = int(
        np.ceil((z ** 2 * sensitivity * (1 - sensitivity)) / (ci_width / 2) ** 2)
    )
    n_neg = int(
        np.ceil((z ** 2 * specificity * (1 - specificity)) / (ci_width / 2) ** 2)
    )
    n_total = max(int(np.ceil(n_pos / prevalence)), int(np.ceil(n_neg / (1 - prevalence))))
    return {
        "n_positive": n_pos,
        "n_negative": n_neg,
        "n_total": n_total,
        "alpha": alpha,
        "ci_width": ci_width,
        "method": "Diagnostic test sample size (CI width)",
    }


# ============================================================================
# 2. 把握度分析
# ============================================================================


def calculate_power(
    design: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """反向把握度计算（已知样本量计算把握度）

    Parameters
    ----------
    design : str
        设计类型，支持 't_test', 'proportion', 'survival'
    params : Dict[str, Any]
        包含样本量 n 和效应参数

    Returns
    -------
    Dict[str, Any]
        把握度计算结果

    Examples
    --------
    >>> result = calculate_power('t_test', {'n': 64, 'delta': 5, 'sd': 10})
    >>> print(f"Power = {result['power']:.3f}")
    """
    if design == "t_test":
        if _HAS_CALCULATOR:
            return calc_power_t(**params)
        return _power_t_test(**params)
    elif design == "proportion":
        return _power_proportion(**params)
    elif design == "survival":
        return _power_survival(**params)
    else:
        raise ValueError(f"不支持的设计类型: {design}")


def _power_t_test(n, delta, sd, alpha=0.05, sided="two.sided"):
    d = delta / sd
    ncp = d * np.sqrt(n / 2)
    df = 2 * n - 2
    if sided == "two.sided":
        t_crit = stats.t.ppf(1 - alpha / 2, df)
        power = 1 - stats.nct.cdf(t_crit, df, ncp) + stats.nct.cdf(-t_crit, df, ncp)
    else:
        t_crit = stats.t.ppf(1 - alpha, df)
        power = 1 - stats.nct.cdf(t_crit, df, ncp)
    return {"power": power, "n": n, "d": d, "alpha": alpha, "method": "Power (t-test)"}


def _power_proportion(n, p1, p2, alpha=0.05, sided="two.sided"):
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    p_bar = (p1 + p2) / 2
    z = abs(p1 - p2) / np.sqrt(2 * p_bar * (1 - p_bar) / n)
    power = 1 - stats.norm.cdf(z_alpha - z)
    return {"power": power, "n": n, "p1": p1, "p2": p2, "alpha": alpha,
            "method": "Power (proportion test)"}


def _power_survival(n_events, hr, alpha=0.05, sided="two.sided"):
    z_alpha = stats.norm.ppf(1 - alpha / 2 if sided == "two.sided" else 1 - alpha)
    z = abs(np.log(hr)) * np.sqrt(n_events) / 2
    power = 1 - stats.norm.cdf(z_alpha - z)
    return {"power": power, "n_events": n_events, "hr": hr, "alpha": alpha,
            "method": "Power (survival)"}


def power_curve(
    design: str,
    param_name: str,
    param_range: np.ndarray,
    fixed_params: Dict[str, Any],
) -> pd.DataFrame:
    """生成把握度曲线

    Parameters
    ----------
    design : str
        设计类型
    param_name : str
        变化的参数名（如 'n', 'delta', 'effect_size'）
    param_range : np.ndarray
        参数取值范围
    fixed_params : Dict[str, Any]
        其他固定参数

    Returns
    -------
    pd.DataFrame
        包含参数值和对应把握度的数据框

    Examples
    --------
    >>> curve = power_curve('t_test', 'n', np.arange(20, 200, 10),
    ...                     {'delta': 5, 'sd': 10})
    """
    rows = []
    for val in param_range:
        params = {**fixed_params, param_name: val}
        try:
            result = calculate_power(design, params)
            rows.append({param_name: val, "power": result["power"]})
        except Exception:
            rows.append({param_name: val, "power": np.nan})
    return pd.DataFrame(rows)


# ============================================================================
# 3. Markdown 报告生成
# ============================================================================


def generate_sample_size_report(
    design: str,
    params: Dict[str, Any],
    result: Optional[Dict[str, Any]] = None,
    title: str = "样本量计算报告",
    study_name: str = "",
) -> str:
    """生成 Markdown 格式的样本量计算报告

    Parameters
    ----------
    design : str
        研究设计类型
    params : Dict[str, Any]
        计算参数
    result : Optional[Dict[str, Any]]
        已有的计算结果（若为 None 则自动计算）
    title : str
        报告标题
    study_name : str
        研究名称

    Returns
    -------
    str
        Markdown 格式的报告字符串

    Examples
    --------
    >>> report = generate_sample_size_report(
    ...     't_test', {'delta': 5, 'sd': 10, 'power': 0.80})
    >>> print(report[:200])
    """
    if result is None:
        result = calculate_sample_size(design, params)

    method = result.get("method", design)
    lines = []

    # 报告头部
    lines.append(f"# {title}")
    lines.append("")
    if study_name:
        lines.append(f"**研究名称**: {study_name}")
        lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**计算方法**: {method}")
    lines.append("")

    # 参数表
    lines.append("## 1. 计算参数")
    lines.append("")
    lines.append("| 参数 | 值 |")
    lines.append("|------|----|")
    for key, val in params.items():
        if isinstance(val, float):
            lines.append(f"| {key} | {val:.4f} |")
        else:
            lines.append(f"| {key} | {val} |")
    lines.append("")

    # 公式说明
    lines.append("## 2. 计算公式")
    lines.append("")
    formula_text = _get_formula_text(design)
    lines.append(formula_text)
    lines.append("")

    # 结果表
    lines.append("## 3. 计算结果")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|------|----|")
    for key, val in result.items():
        if key in ("design", "method"):
            continue
        if isinstance(val, float):
            lines.append(f"| {key} | {val:.4f} |")
        elif isinstance(val, int):
            lines.append(f"| {key} | {val} |")
        else:
            lines.append(f"| {key} | {val} |")
    lines.append("")

    # 结论
    lines.append("## 4. 结论")
    lines.append("")
    conclusion = _generate_conclusion(design, result)
    lines.append(conclusion)
    lines.append("")

    # 注意事项
    lines.append("## 5. 注意事项")
    lines.append("")
    lines.append("- 样本量计算基于假设的效应量和变异度，实际研究中的参数可能不同。")
    lines.append("- 建议在计算结果基础上增加 10%-20% 的失访率补偿。")
    lines.append("- 多重比较时需调整显著性水平（如 Bonferroni 校正）。")
    lines.append("- 详见 CONSORT 或 STROBE 报告指南中的样本量部分。")
    lines.append("")

    return "\n".join(lines)


def _get_formula_text(design: str) -> str:
    """获取各设计的公式说明文本"""
    formulas = {
        "t_test": (
            "两独立样本 t 检验样本量公式：\n\n"
            "```\n"
            "n_per_group = 2 * (Z_alpha/2 + Z_beta)^2 / (delta / sd)^2\n"
            "```\n\n"
            "其中：\n"
            "- `delta`: 组间均值差\n"
            "- `sd`: 标准差\n"
            "- `Z_alpha/2`: 显著性水平对应的标准正态分位数\n"
            "- `Z_beta`: 把握度对应的标准正态分位数\n"
            "- `delta/sd`: Cohen's d 效应量"
        ),
        "paired_t": (
            "配对 t 检验样本量公式：\n\n"
            "```\n"
            "n = (Z_alpha/2 + Z_beta)^2 / (delta / sd_diff)^2\n"
            "```\n\n"
            "其中 `sd_diff` 为差值的标准差。"
        ),
        "proportion": (
            "两样本率比较样本量公式（arcsine 变换）：\n\n"
            "```\n"
            "h = 2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))\n"
            "n_per_group = 2 * (Z_alpha/2 + Z_beta)^2 / h^2\n"
            "```\n\n"
            "其中 `h` 为 Cohen's h 效应量。"
        ),
        "anova": (
            "单因素方差分析样本量公式（近似）：\n\n"
            "```\n"
            "n_per_group = (Z_alpha/2 + Z_beta)^2 / f^2 + k / (2 * f)\n"
            "```\n\n"
            "其中 `f` 为 Cohen's f 效应量（小=0.10, 中=0.25, 大=0.40），`k` 为组数。"
        ),
        "survival": (
            "生存分析样本量公式（Schoenfeld）：\n\n"
            "```\n"
            "n_events = (Z_alpha/2 + Z_beta)^2 / (log(HR)^2 * p * (1-p))\n"
            "n_total = n_events / p_event\n"
            "```\n\n"
            "其中 `HR` 为风险比，`p` 为处理组比例，`p_event` 为事件发生率。"
        ),
        "logistic": (
            "Logistic 回归样本量（EPV 规则）：\n\n"
            "```\n"
            "n_events = n_predictors * EPV\n"
            "n_total = n_events / prop_events\n"
            "```\n\n"
            "EPV (Events Per Variable) 通常取 10-20。"
        ),
        "noninferiority": (
            "非劣效性试验样本量公式：\n\n"
            "```\n"
            "n_per_group = 2 * (Z_alpha + Z_beta)^2 * sd^2 / delta^2\n"
            "```\n\n"
            "其中 `delta` 为非劣效界值，`alpha` 通常取单侧 0.025。"
        ),
        "diagnostic": (
            "诊断试验样本量公式（基于 CI 宽度）：\n\n"
            "```\n"
            "n = Z_alpha/2^2 * p * (1-p) / (d/2)^2\n"
            "```\n\n"
            "其中 `p` 为灵敏度或特异度，`d` 为期望的置信区间宽度。"
        ),
    }
    return formulas.get(design, f"设计类型 '{design}' 的公式说明暂未提供。")


def _generate_conclusion(design: str, result: Dict[str, Any]) -> str:
    """生成结论文本"""
    if design in ("t_test", "proportion", "noninferiority"):
        n_total = result.get("n_total", "N/A")
        n_per = result.get("n_per_group", "N/A")
        return (
            f"本研究采用 **{result.get('method', design)}** 方法计算样本量。"
            f"在显著性水平 alpha = {result.get('alpha', 0.05)}、"
            f"把握度 = {result.get('power', 0.80)} 的条件下，"
            f"每组需要 **{n_per}** 例，共需 **{n_total}** 例受试者。"
            f"\n\n建议在上述基础上增加 15%-20% 的样本量以补偿失访。"
        )
    elif design == "survival":
        n_events = result.get("n_events", "N/A")
        n_total = result.get("n_total", "N/A")
        return (
            f"本研究采用 **Schoenfeld 公式** 计算生存分析样本量。"
            f"在 HR = {result.get('hr', 'N/A')}、事件率 = {result.get('prop_event', 'N/A')}、"
            f"alpha = {result.get('alpha', 0.05)}、把握度 = {result.get('power', 0.80)} 的条件下，"
            f"需要 **{n_events}** 个事件，总样本量 **{n_total}** 例。"
        )
    elif design == "logistic":
        return (
            f"基于 EPV = {result.get('epv', 10)} 规则，"
            f"{result.get('n_predictors', 'N/A')} 个预测变量需要 "
            f"**{result.get('n_events', 'N/A')}** 个事件，"
            f"总样本量 **{result.get('n_total', 'N/A')}** 例。"
        )
    elif design == "diagnostic":
        return (
            f"基于灵敏度 {result.get('sensitivity', 'N/A')} 和特异度 "
            f"{result.get('specificity', 'N/A')}，"
            f"在 CI 宽度 = {result.get('ci_width', 0.10)} 的条件下，"
            f"需要阳性病例 **{result.get('n_positive', 'N/A')}** 例，"
            f"阴性病例 **{result.get('n_negative', 'N/A')}** 例，"
            f"总样本量 **{result.get('n_total', 'N/A')}** 例。"
        )
    elif design == "anova":
        return (
            f"在 Cohen's f = {result.get('f', 'N/A')}、"
            f"alpha = {result.get('alpha', 0.05)}、把握度 = {result.get('power', 0.80)} 的条件下，"
            f"每组需要 **{result.get('n_per_group', 'N/A')}** 例，"
            f"共需 **{result.get('n_total', 'N/A')}** 例。"
        )
    else:
        return f"样本量计算完成，方法: {result.get('method', design)}。"


# ============================================================================
# 4. 批量计算与比较
# ============================================================================


def compare_scenarios(
    design: str,
    scenarios: List[Dict[str, Any]],
    labels: Optional[List[str]] = None,
) -> pd.DataFrame:
    """批量计算不同参数场景下的样本量

    Parameters
    ----------
    design : str
        研究设计类型
    scenarios : List[Dict[str, Any]]
        参数场景列表
    labels : Optional[List[str]]
        场景标签

    Returns
    -------
    pd.DataFrame
        各场景的样本量比较表

    Examples
    --------
    >>> scenarios = [
    ...     {'delta': 3, 'sd': 10},
    ...     {'delta': 5, 'sd': 10},
    ...     {'delta': 7, 'sd': 10},
    ... ]
    >>> df = compare_scenarios('t_test', scenarios, labels=['Small', 'Medium', 'Large'])
    """
    if labels is None:
        labels = [f"Scenario {i+1}" for i in range(len(scenarios))]

    rows = []
    for label, params in zip(labels, scenarios):
        result = calculate_sample_size(design, params)
        row = {"Label": label, "Method": result.get("method", design)}
        row.update(params)
        # 提取关键结果指标
        for key in ("n_total", "n_per_group", "n1", "n2", "n_events",
                     "n_positive", "n_negative", "power"):
            if key in result:
                row[key] = result[key]
        rows.append(row)

    return pd.DataFrame(rows)


def save_report(report: str, filepath: str) -> None:
    """将报告保存为 Markdown 文件

    Parameters
    ----------
    report : str
        Markdown 报告内容
    filepath : str
        输出文件路径
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"报告已保存至: {filepath}")


# ============================================================================
# 5. 完整工作流
# ============================================================================


def full_sample_size_workflow(
    design: str,
    params: Dict[str, Any],
    study_name: str = "",
    do_power_curve: bool = False,
    power_curve_param: str = "n",
    power_curve_range: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """完整的样本量计算工作流

    执行：样本量计算 → 报告生成 → （可选）把握度曲线

    Parameters
    ----------
    design : str
        研究设计类型
    params : Dict[str, Any]
        计算参数
    study_name : str
        研究名称
    do_power_curve : bool
        是否生成把握度曲线
    power_curve_param : str
        把握度曲线的变化参数
    power_curve_range : Optional[np.ndarray]
        把握度曲线的参数范围

    Returns
    -------
    Dict[str, Any]
        包含计算结果、报告和（可选）把握度曲线数据
    """
    results = {}

    # 1. 样本量计算
    logger.info("=" * 50)
    logger.info("Step 1: 样本量计算")
    logger.info("=" * 50)
    calc_result = calculate_sample_size(design, params)
    results["calculation"] = calc_result
    logger.info(f"  方法: {calc_result.get('method', design)}")
    for key in ("n_total", "n_per_group", "n_events"):
        if key in calc_result:
            logger.info(f"  {key}: {calc_result[key]}")

    # 2. 报告生成
    logger.info("\n" + "=" * 50)
    logger.info("Step 2: 报告生成")
    logger.info("=" * 50)
    report = generate_sample_size_report(design, params, calc_result,
                                         study_name=study_name)
    results["report"] = report
    logger.info("  Markdown 报告已生成")

    # 3. 把握度曲线（可选）
    if do_power_curve:
        logger.info("\n" + "=" * 50)
        logger.info("Step 3: 把握度曲线")
        logger.info("=" * 50)
        if power_curve_range is None:
            n_base = calc_result.get("n_per_group", calc_result.get("n_total", 100))
            power_curve_range = np.arange(
                max(10, int(n_base * 0.3)),
                int(n_base * 2),
                max(5, int(n_base * 0.1)),
            )
        # 构建固定参数（排除变化的参数）
        fixed = {k: v for k, v in params.items() if k != power_curve_param}
        curve = power_curve(design, power_curve_param, power_curve_range, fixed)
        results["power_curve"] = curve
        logger.info(f"  把握度曲线已生成（{len(curve)} 个点）")

    logger.info("\n 样本量计算工作流完成")
    return results


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 示例 1: 两样本 t 检验
    logger.info("=" * 60)
    logger.info("示例 1: 两样本 t 检验")
    logger.info("=" * 60)
    res = calculate_sample_size("t_test", {"delta": 5, "sd": 10, "power": 0.80})
    logger.info(f"  n_per_group = {res['n_per_group']}, n_total = {res['n_total']}")
    logger.info(f"  Cohen's d = {res['d']:.3f}")

    # 示例 2: 率比较
    logger.info("\n" + "=" * 60)
    logger.info("示例 2: 两样本率比较")
    logger.info("=" * 60)
    res = calculate_sample_size("proportion", {"p1": 0.3, "p2": 0.5})
    logger.info(f"  n_per_group = {res['n_per_group']}, n_total = {res['n_total']}")

    # 示例 3: 生存分析
    logger.info("\n" + "=" * 60)
    logger.info("示例 3: 生存分析")
    logger.info("=" * 60)
    res = calculate_sample_size("survival", {"hr": 0.7, "prop_event": 0.6})
    logger.info(f"  n_events = {res['n_events']}, n_total = {res['n_total']}")

    # 示例 4: 非劣效性试验
    logger.info("\n" + "=" * 60)
    logger.info("示例 4: 非劣效性试验")
    logger.info("=" * 60)
    res = calculate_sample_size("noninferiority", {"delta": 3, "sd": 10})
    logger.info(f"  n_per_group = {res['n_per_group']}, n_total = {res['n_total']}")

    # 示例 5: 诊断试验
    logger.info("\n" + "=" * 60)
    logger.info("示例 5: 诊断试验")
    logger.info("=" * 60)
    res = calculate_sample_size("diagnostic", {
        "sensitivity": 0.9, "specificity": 0.85, "prevalence": 0.3
    })
    logger.info(f"  n_positive = {res['n_positive']}, n_negative = {res['n_negative']}")
    logger.info(f"  n_total = {res['n_total']}")

    # 示例 6: 反向把握度计算
    logger.info("\n" + "=" * 60)
    logger.info("示例 6: 反向把握度计算")
    logger.info("=" * 60)
    pw = calculate_power("t_test", {"n": 64, "delta": 5, "sd": 10})
    logger.info(f"  Power = {pw['power']:.3f}")

    # 示例 7: 批量场景比较
    logger.info("\n" + "=" * 60)
    logger.info("示例 7: 批量场景比较")
    logger.info("=" * 60)
    scenarios = [
        {"delta": 3, "sd": 10},
        {"delta": 5, "sd": 10},
        {"delta": 7, "sd": 10},
    ]
    df_compare = compare_scenarios("t_test", scenarios,
                                   labels=["Small effect", "Medium effect", "Large effect"])
    logger.info("df_compare.to_string(index=False)")

    # 示例 8: 生成 Markdown 报告
    logger.info("\n" + "=" * 60)
    logger.info("示例 8: Markdown 报告")
    logger.info("=" * 60)
    report = generate_sample_size_report(
        "t_test",
        {"delta": 5, "sd": 10, "power": 0.80, "alpha": 0.05},
        study_name="降压药疗效比较试验",
    )
    logger.info("report[:500]")
    logger.info("  ... (报告已截断显示)")

    # 示例 9: 完整工作流
    logger.info("\n" + "=" * 60)
    logger.info("示例 9: 完整工作流")
    logger.info("=" * 60)
    workflow_result = full_sample_size_workflow(
        "survival",
        {"hr": 0.75, "prop_event": 0.5, "power": 0.80},
        study_name="肿瘤新药 III 期试验",
        do_power_curve=True,
    )

    logger.info("\n 效应量参考:")
    logger.info("  Cohen's d: 小=0.2, 中=0.5, 大=0.8")
    logger.info("  Cohen's f: 小=0.10, 中=0.25, 大=0.40")
    logger.info("  OR/HR:     小=1.5, 中=2.0, 大=3.0")

    logger.info("\n 样本量计算模板示例完成")
