"""
rmst_template.py — 限制性平均生存时间 (RMST) 分析模板
=====================================================
适用于：生存分析中 RMST 的计算和比较

RMST 是生存曲线下面积，代表在指定时间点内患者期望存活的平均时间。
相比 HR，RMST 具有以下优势：
  - 无需比例风险假定
  - 直接可解释（时间单位）
  - 适用于非比例风险场景

功能：
  - RMST 计算（Kaplan-Meier 法）
  - 两组 RMST 差值和比值
  - RMST 差值的置信区间和检验
  - RMST 可视化

依赖: numpy, scipy, pandas, matplotlib
安装: pip install numpy scipy pandas matplotlib

参考文献:
  - Royston P, Parmar MK. Restricted mean survival time: an alternative
    to the hazard ratio for the design and analysis of randomized trials
    with a time-to-event outcome. BMC Med Res Methodol, 2013; 13:152.
  - Uno H, et al. Moving beyond the hazard ratio in quantifying the
    between-group difference in survival analysis. J Clin Oncol, 2014.

作者: MSRA Team
版本: 0.1.0
"""

from typing import Dict, Optional, Tuple
import numpy as np
from scipy import stats

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# ============================================================================
# 1. RMST 计算
# ============================================================================


def kaplan_meier_rmst(
    time: np.ndarray,
    event: np.ndarray,
    tau: float = None,
) -> Dict[str, float]:
    """Kaplan-Meier 法计算 RMST

    Parameters
    ----------
    time : array-like
        生存时间
    event : array-like
        事件指示 (1=事件, 0=删失)
    tau : float, optional
        截断时间点。默认使用最大观察时间

    Returns
    -------
    Dict
        RMST 值和相关统计量
    """
    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=float)

    # 按时间排序
    order = np.argsort(time)
    time = time[order]
    event = event[order]

    # Kaplan-Meier 估计
    n = len(time)
    km_times = [0.0]
    km_surv = [1.0]
    at_risk = n

    for i in range(n):
        if event[i] == 1:
            km_times.append(time[i])
            km_surv.append(km_surv[-1] * (1 - 1 / at_risk))
        at_risk -= 1

    km_times = np.array(km_times)
    km_surv = np.array(km_surv)

    if tau is None:
        tau = time[-1]

    # RMST = ∫₀^τ S(t) dt (梯形法)
    rmst = 0.0
    for i in range(len(km_times) - 1):
        if km_times[i] >= tau:
            break
        dt = min(km_times[i + 1], tau) - km_times[i]
        rmst += km_surv[i] * dt

    return {
        "rmst": rmst,
        "tau": tau,
        "n_events": int(np.sum(event)),
        "n_total": n,
        "km_times": km_times,
        "km_surv": km_surv,
    }


def rmst_difference(
    time1: np.ndarray, event1: np.ndarray,
    time2: np.ndarray, event2: np.ndarray,
    tau: float = None,
    alpha: float = 0.05,
) -> Dict[str, float]:
    """两组 RMST 差值比较

    Parameters
    ----------
    time1, event1 : array-like
        组 1 的生存时间和事件指示
    time2, event2 : array-like
        组 2 的生存时间和事件指示
    tau : float, optional
        截断时间点
    alpha : float
        显著性水平

    Returns
    -------
    Dict
        RMST 差值、CI、p 值
    """
    res1 = kaplan_meier_rmst(time1, event1, tau)
    res2 = kaplan_meier_rmst(time2, event2, tau)

    tau = res1["tau"]
    rmst_diff = res1["rmst"] - res2["rmst"]

    # 差值的标准误 (基于 IPCW 的简化版本)
    # 完整实现需要 inverse probability of censoring weighting
    n1, n2 = res1["n_total"], res2["n_total"]

    # 简化 SE 估计
    var1 = _rmst_variance(time1, event1, tau)
    var2 = _rmst_variance(time2, event2, tau)
    se_diff = np.sqrt(var1 / n1 + var2 / n2)

    # Wald 检验
    z_val = rmst_diff / se_diff if se_diff > 0 else 0
    p_val = 2 * stats.norm.sf(abs(z_val))

    z_crit = stats.norm.ppf(1 - alpha / 2)

    return {
        "rmst_group1": res1["rmst"],
        "rmst_group2": res2["rmst"],
        "difference": rmst_diff,
        "se": se_diff,
        "ci_lower": rmst_diff - z_crit * se_diff,
        "ci_upper": rmst_diff + z_crit * se_diff,
        "z": z_val,
        "p": p_val,
        "tau": tau,
        "n_group1": n1,
        "n_group2": n2,
        "significant": p_val < alpha,
    }


def _rmst_variance(
    time: np.ndarray,
    event: np.ndarray,
    tau: float,
) -> float:
    """RMST 方差的简化估计"""
    n = len(time)
    # 使用 Greenwood-like 估计
    order = np.argsort(time)
    time = time[order]
    event = event[order]

    km_surv = [1.0]
    km_var = [0.0]
    at_risk = n

    for i in range(n):
        if event[i] == 1:
            q = 1 / at_risk
            km_surv.append(km_surv[-1] * (1 - q))
            # Greenwood formula
            km_var.append(km_surv[-1]**2 * (q / (1 - q)) / at_risk)
        at_risk -= 1

    # 简化: 返回生存曲线的平均方差
    return np.mean(km_var) if km_var else 0.0


def rmst_ratio(
    time1: np.ndarray, event1: np.ndarray,
    time2: np.ndarray, event2: np.ndarray,
    tau: float = None,
) -> Dict[str, float]:
    """RMST 比值 (RMST ratio)

    Parameters
    ----------
    time1, event1 : array-like
        组 1
    time2, event2 : array-like
        组 2
    tau : float, optional
        截断时间点

    Returns
    -------
    Dict
        RMST 比值
    """
    res1 = kaplan_meier_rmst(time1, event1, tau)
    res2 = kaplan_meier_rmst(time2, event2, tau)

    ratio = res1["rmst"] / res2["rmst"] if res2["rmst"] > 0 else float('inf')

    return {
        "rmst_group1": res1["rmst"],
        "rmst_group2": res2["rmst"],
        "ratio": ratio,
        "tau": res1["tau"],
    }


# ============================================================================
# 2. 可视化
# ============================================================================


def plot_rmst(
    time1: np.ndarray, event1: np.ndarray,
    time2: np.ndarray, event2: np.ndarray,
    tau: float = None,
    group1_name: str = "Treatment",
    group2_name: str = "Control",
    figsize: Tuple[float, float] = (10, 6),
) -> "plt.Figure":
    """绘制 RMST 对比图

    Parameters
    ----------
    time1, event1, time2, event2 : array-like
        两组数据
    tau : float, optional
        截断时间点
    group1_name, group2_name : str
        组名
    figsize : tuple
        图表大小

    Returns
    -------
    matplotlib Figure
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("需要 matplotlib: pip install matplotlib")

    res1 = kaplan_meier_rmst(time1, event1, tau)
    res2 = kaplan_meier_rmst(time2, event2, tau)
    tau = res1["tau"]

    fig, ax = plt.subplots(figsize=figsize)

    # 绘制 KM 曲线
    ax.step(res1["km_times"], res1["km_times"], where='post',
            label=f"{group1_name} (RMST={res1['rmst']:.2f})", linewidth=2)
    ax.step(res2["km_times"], res2["km_times"], where='post',
            label=f"{group2_name} (RMST={res2['rmst']:.2f})", linewidth=2)

    # 填充 RMST 面积
    ax.fill_between(res1["km_times"], res1["km_surv"], alpha=0.2, step='post')
    ax.fill_between(res2["km_times"], res2["km_surv"], alpha=0.2, step='post')

    ax.axvline(tau, color='gray', linestyle='--', alpha=0.5, label=f"τ = {tau:.1f}")
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Survival Probability", fontsize=12)
    ax.set_title("Restricted Mean Survival Time (RMST)", fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


# ============================================================================
# 3. 报告生成
# ============================================================================


def format_rmst_report(results: Dict) -> str:
    """生成 RMST 分析报告

    Parameters
    ----------
    results : Dict
        rmst_difference() 的输出

    Returns
    -------
    str
        Markdown 格式报告
    """
    lines = ["# RMST 分析报告\n"]
    lines.append(f"**截断时间点 (τ)**: {results['tau']:.2f}")
    lines.append(f"**样本量**: 组1 = {results['n_group1']}, 组2 = {results['n_group2']}")
    lines.append("")

    lines.append("## RMST 结果\n")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 组 1 RMST | {results['rmst_group1']:.4f} |")
    lines.append(f"| 组 2 RMST | {results['rmst_group2']:.4f} |")
    lines.append(f"| RMST 差值 | {results['difference']:.4f} |")
    lines.append(f"| 标准误 | {results['se']:.4f} |")
    lines.append(f"| 95% CI | [{results['ci_lower']:.4f}, {results['ci_upper']:.4f}] |")
    lines.append(f"| z 值 | {results['z']:.3f} |")
    lines.append(f"| p 值 | {results['p']:.4f} |")
    lines.append("")

    sig = "✅ 差异有统计学意义" if results['significant'] else "⚠️ 差异无统计学意义"
    lines.append(f"**结论**: {sig}\n")

    lines.append("## 临床解读\n")
    diff = results['difference']
    if diff > 0:
        lines.append(f"- 组 1 患者在 τ={results['tau']:.1f} 时间内平均多存活 {abs(diff):.2f} 个时间单位")
    else:
        lines.append(f"- 组 2 患者在 τ={results['tau']:.1f} 时间内平均多存活 {abs(diff):.2f} 个时间单位")

    lines.append(f"- RMST 差值直接可解释为时间差，无需比例风险假定")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# 示例
# ============================================================================

if __name__ == "__main__":
    np.random.seed(42)

    # 模拟生存数据
    n = 100
    time1 = np.random.exponential(12, n)
    time2 = np.random.exponential(8, n)
    event1 = np.random.binomial(1, 0.7, n)
    event2 = np.random.binomial(1, 0.8, n)

    print("=== RMST 分析 ===\n")
    results = rmst_difference(time1, event1, time2, event2, tau=24)
    report = format_rmst_report(results)
    print(report)

    print("✅ RMST 分析示例完成")
