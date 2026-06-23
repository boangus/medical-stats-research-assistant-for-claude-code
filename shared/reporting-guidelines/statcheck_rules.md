# statcheck 统计一致性校验规则

> 自动检测报告中统计结果（P 值、检验统计量、自由度）的内部一致性
> 借鉴 **statcheck**（Epskamp & Nuijten 2016, R 包 + statcheck.io, PMC7540394）
> 适用阶段: report skill Phase 6b（规范合规检查的子步骤）
> 更新日期: 2026-06-14

> **IRON RULES**:
> - 报告中的每个 NHST 结果（t/F/χ²/r/z + df + 报告 p）必须能被**独立重算**且与报告 p 一致
> - 不一致项（误差 > 容差）须标记为 ❌ 并强制复核，不得静默放行
> - 校验仅标记"可能不一致"，**不自动修改**数据 — 真因可能是笔误、四舍五入、单尾/双尾差异
> - 参考: shared/anti-patterns/medical_stats_anti_patterns.md（D1 P值二元化、D3 不报告假设检验结果）

---

## 校验范围（NHST 结果抽取）

从报告正文、表格、图注中提取以下 APA 格式的统计结果：

| 检验类型 | APA 格式示例 | 提取字段 |
|---------|-------------|---------|
| **t 检验** | `t(38) = 2.45, p = .019` | df=38, stat=2.45, reported_p=0.019 |
| **方差分析 F** | `F(2, 57) = 4.32, p = .018` | df1=2, df2=57, stat=4.32, reported_p=0.018 |
| **卡方 χ²** | `χ²(1, N = 100) = 5.83, p = .016` | df=1, stat=5.83, reported_p=0.016 |
| **相关 r** | `r(98) = .35, p < .001` | df=98, stat=0.35, reported_p=<0.001 |
| **z 检验** | `z = 1.96, p = .050` | stat=1.96, reported_p=0.050 |
| **回归 β/HR + Wald** | `Wald χ²(1) = 6.12, p = .013` | df=1, stat=6.12, reported_p=0.013 |

**抽取正则模式**（Python `re` 示例，无 R 依赖）：

```python
import re

# t 检验: t(df) = stat, p = value
T_PATTERN = re.compile(
    r"t\s*\(\s*(\d+)\s*\)\s*=\s*([-\d.]+)\s*,?\s*p\s*[<>=]\s*\.?(\d+\.?\d*)",
    re.IGNORECASE,
)

# F 检验: F(df1, df2) = stat, p = value
F_PATTERN = re.compile(
    r"F\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*=\s*([-\d.]+)\s*,?\s*p\s*[<>=]\s*\.?(\d+\.?\d*)",
    re.IGNORECASE,
)

# 卡方: χ²(df) 或 chi2(df) = stat, p = value
CHI2_PATTERN = re.compile(
    r"[χχ]\s*[²2]\s*\(\s*(\d+)\s*[^)]*\)\s*=\s*([-\d.]+)\s*,?\s*p\s*[<>=]\s*\.?(\d+\.?\d*)",
    re.IGNORECASE,
)

# 相关: r(df) = stat, p = value
R_PATTERN = re.compile(
    r"r\s*\(\s*(\d+)\s*\)\s*=\s*([-\d.]+)\s*,?\s*p\s*[<>=]\s*\.?(\d+\.?\d*)",
    re.IGNORECASE,
)
```

## 重算公式

从统计量和自由度**独立重算** p 值，与报告 p 比对：

```python
from scipy import stats

def recompute_p(test: str, stat: float, df1: int, df2: int | None) -> float:
    """从检验统计量重算双尾 p 值。"""
    if test == "t":
        return 2 * (1 - stats.t.cdf(abs(stat), df1))
    if test == "F":
        return 1 - stats.f.cdf(stat, df1, df2)
    if test == "chi2":
        return 1 - stats.chi2.cdf(stat, df1)
    if test == "r":
        # r → t 转换: t = r * sqrt(df / (1 - r^2)), df = N - 2
        t_val = stat * (df1 / (1 - stat**2)) ** 0.5
        return 2 * (1 - stats.t.cdf(abs(t_val), df1))
    if test == "z":
        return 2 * (1 - stats.norm.cdf(abs(stat)))
    raise ValueError(f"未知检验类型: {test}")
```

## 容差与判定

| 字段 | 容差 | 判定 |
|------|------|------|
| **绝对误差** `\|reported_p - recomputed_p\|` | < 0.001 | ✅ 一致 |
| **绝对误差** 0.001–0.01 | — | ⚠️ 边界（可能四舍五入差异，建议复核） |
| **绝对误差** ≥ 0.01 | — | ❌ 不一致（强制复核） |
| **显著性方向** (reported vs recomputed 跨 0.05) | 0 | ❌❌ 严重（结论可能反转，必须复核） |

**例外处理（避免误报）**：
- **单尾检验**：若报告或上下文明确标注 "one-tailed"/"单尾"，重算时 p 除以 2；否则默认双尾
- **校正后 p 值**（Bonferroni/Holm/FDR）：若报告含 "adjusted"/"corrected" 字样，跳过自动校验，标记为"校正后值-人工复核"
- **`p < .001` / `p < .0001`**：当重算 p 也 < 0.001 时判一致；否则标记复核
- **稳健标准误 / sandwich**：标记"使用稳健估计-人工复核"，跳过精确校验

## 校验输出格式

```text
📊 statcheck 一致性校验报告
─────────────────────────────────────────────
共抽取 NHST 结果: 12 个
✅ 一致: 9 个
⚠️ 边界 (0.001–0.01): 2 个
❌ 不一致 (≥0.01): 1 个
❌❌ 显著性反转: 0 个

不一致明细:
  [报告 §3.2, Table 2] t(38) = 2.45, reported p = .019
    → 重算 p = 0.0196 (双尾, df=38)
    → 绝对误差 0.0006 → 实为边界; 复核后判一致 ✅

  [报告 §4.1] F(2, 57) = 4.32, reported p = .018
    → 重算 p = 0.0178
    → 绝对误差 0.0002 → 一致 ✅
─────────────────────────────────────────────
```

## 实施要点（report skill Phase 6b）

1. **抽取阶段**: 从 Phase 3 生成的表格、Phase 1 的结果解读文本、Phase 5 的方法学段落中，按上述正则模式抽取所有 NHST 结果
2. **重算阶段**: 对每个抽取项调用 `recompute_p()`，得到独立重算 p
3. **比对阶段**: 按容差表判定一致/边界/不一致/显著性反转
4. **报告阶段**: 输出上述校验报告；**所有 ❌/❌❌ 项须在合规报告中标记，并由 MANDATORY-M4 检查点强制用户确认**
5. **降级处理**: 若 scipy 不可用（如 runtime 无 Python 统计包），降级为"只做格式抽取 + 检查 `p < .001` 类明显矛盾"，输出降级说明

## 误报风险与缓解

| 风险 | 缓解 |
|------|------|
| 单尾检验被当双尾校验 → p 偏大误报 | 抽取时检查上下文 "one-tailed"/"单尾" 关键词 |
| 校正后 p 被当原始 p 校验 | 检查 "adjusted"/"corrected"/"Bonferroni" 关键词，跳过 |
| 报告中数字四舍五入（如 stat=2.449→2.45） | 重算时使用报告值；误差 ≤0.01 判边界而非失败 |
| 自由度笔误（df=38 误写 28） | 若误差极大（>0.1），提示"自由度可能笔误" |
| bootstrap/permutation p 无法精确重算 | 跳过，标记"重抽样检验-人工复核" |

## 与 statcheck 原工具的区别

| 维度 | statcheck (R) | MSRA 校验 |
|------|---------------|----------|
| 依赖 | R + statcheck 包 | Python + scipy（runtime 已有） |
| 输入 | PDF/HTML 文件 | 报告内文本+表格（已结构化） |
| 范围 | APA 格式 NHST | APA 格式 + 中文报告格式 |
| 输出 | 不一致项清单 | 不一致项 + MANDATORY 检查点集成 |
| 适用 | 已发表论文审稿 | 报告生成阶段的实时质控 |

## 关键提示

1. **校验是"必要的但不充分的"**：通过 statcheck 校验不等于统计方法正确，只表示数字内部一致
2. **不替代效应量报告**：即使 p 一致，仍须报告效应量+95%CI（参考 anti-patterns D1）
3. **聚焦 NHST 结果**：贝叶斯因子、置信区间不在此校验范围（CI 的一致性由 Phase 3 表格生成保证）
4. **资料来源**: Epskamp M, Nuijten MB. statcheck: Automatically detect statistical reporting inconsistencies to increase reproducibility of meta-analyses. PLoS ONE 2016;11(11):e0158224. PMC7540394.

## 参考文献

1. Epskamp M, Nuijten MB. statcheck: Automatically detect statistical reporting inconsistencies. PLoS ONE 2016;11(11):e0158224.
2. Nuijten MB, et al. The prevalence of statistical reporting errors in psychology (1985–2013). Behav Res Methods 2016;48:1205-1226.
3. Bakker M, Wicherts JM. The (mis)reporting of statistical results in psychology journals. PLoS ONE 2011;6(11):e27340.
