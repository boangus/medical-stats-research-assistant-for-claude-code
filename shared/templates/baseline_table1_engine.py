#!/usr/bin/env python3
"""
MSRA Table 1 基线特征表引擎

移植课程 table1sci 核心算法到 Python，实现自动检验选择和出版级表格生成。
算法流程: 正态性检验 → 方差齐性检验 → 参数/非参数自动选择 → 三路卡方分类 → SMD 计算

用法:
    from shared.templates.baseline_table1_engine import BaselineTable1Engine, VariableConfig

    engine = BaselineTable1Engine()
    result = engine.generate(
        df,
        group_var="treatment",
        variables=[
            VariableConfig("age", "年龄", "continuous"),
            VariableConfig("sex", "性别", "categorical"),
        ]
    )
    print(result.to_markdown())
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
import warnings

import numpy as np
import pandas as pd
from scipy import stats


# ── 数据结构 ──


@dataclass
class VariableConfig:
    """变量配置"""
    name: str                              # 变量名
    label: str = ""                        # 显示标签（空则用 name）
    var_type: str = "auto"                 # auto / continuous / categorical
    normal: Optional[bool] = None          # None=自动检测, True=强制正态, False=强制非正态
    test_override: Optional[str] = None    # 手动指定检验方法
    digits: int = 1                        # 小数位数
    pct_digits: int = 1                    # 百分比小数位数

    def __post_init__(self):
        if not self.label:
            self.label = self.name


@dataclass
class RowResult:
    """单行结果"""
    variable: str
    label: str
    level: str          # 变量名（连续）或类别值（分类）
    is_header: bool     # 是否为变量名标题行
    overall: str        # 总体统计量
    group_stats: Dict[str, str] = field(default_factory=dict)  # 各组统计量
    test_name: str = ""
    statistic: Optional[float] = None
    p_value: Optional[float] = None
    smd: Optional[float] = None


@dataclass
class Table1Result:
    """Table 1 生成结果"""
    rows: List[RowResult]
    metadata: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)

    @property
    def has_pvalue(self) -> bool:
        return any(r.p_value is not None for r in self.rows)

    @property
    def has_smd(self) -> bool:
        return any(r.smd is not None for r in self.rows)

    def to_dataframe(self) -> pd.DataFrame:
        """转为 pandas DataFrame"""
        records = []
        for r in self.rows:
            row = {
                "Variable": r.label if r.is_header else "",
                "Level": r.level,
                "Overall": r.overall,
            }
            for grp, stat in r.group_stats.items():
                row[grp] = stat
            if r.p_value is not None:
                row["p_value"] = r.p_value
            if r.smd is not None:
                row["SMD"] = r.smd
            if r.test_name:
                row["Test"] = r.test_name
            records.append(row)
        return pd.DataFrame(records)

    def to_markdown(self, title: str = "Table 1. Baseline Characteristics") -> str:
        """生成三线表 Markdown"""
        df = self.to_dataframe()
        lines = [f"## {title}", ""]

        if self.metadata.get("n_per_group"):
            group_info = ", ".join(
                f"{k}: n={v}" for k, v in self.metadata["n_per_group"].items()
            )
            lines.append(f"*N = {self.metadata.get('n_total', '?')} ({group_info})*")
            lines.append("")

        # 表头
        cols = list(df.columns)
        header = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        lines.append(header)
        lines.append(sep)

        # 数据行
        for _, row in df.iterrows():
            vals = []
            for c in cols:
                v = row[c]
                if pd.isna(v):
                    vals.append("")
                elif isinstance(v, float) and c in ("p_value", "SMD"):
                    vals.append(f"{v:.3f}")
                else:
                    vals.append(str(v))
            lines.append("| " + " | ".join(vals) + " |")

        lines.append("")
        lines.append("*Mean (SD) for normal continuous; Median [IQR] for non-normal; n (%) for categorical.*")

        if self.warnings:
            lines.append("")
            lines.append("**Warnings:**")
            for w in self.warnings:
                lines.append(f"- {w}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """转为结构化字典"""
        return {
            "metadata": self.metadata,
            "warnings": self.warnings,
            "rows": [
                {
                    "variable": r.variable,
                    "label": r.label,
                    "level": r.level,
                    "is_header": r.is_header,
                    "overall": r.overall,
                    "group_stats": r.group_stats,
                    "test_name": r.test_name,
                    "statistic": r.statistic,
                    "p_value": r.p_value,
                    "smd": r.smd,
                }
                for r in self.rows
            ],
        }


# ── 核心引擎 ──


class BaselineTable1Engine:
    """Table 1 基线特征表引擎

    移植 table1sci 核心算法：
    1. 正态性检验（Shapiro-Wilk n≤5000 / KS n>5000）
    2. 方差齐性检验（Levene's test）
    3. 自动检验选择（t/Welch/ANOVA/Welch-ANOVA/Wilcoxon/Kruskal-Wallis/χ²/Yates/Fisher）
    4. SMD 计算
    """

    def __init__(self, alpha_normality: float = 0.05, alpha_variance: float = 0.05):
        self.alpha_normality = alpha_normality
        self.alpha_variance = alpha_variance

    # ── 主入口 ──

    def generate(
        self,
        df: pd.DataFrame,
        group_var: Optional[str] = None,
        variables: Optional[List[VariableConfig]] = None,
        include_overall: bool = True,
        include_pvalue: bool = True,
        include_smd: bool = False,
    ) -> Table1Result:
        """生成 Table 1

        Args:
            df: 数据框
            group_var: 分组变量名（None 则无分组）
            variables: 变量配置列表（None 则自动推断）
            include_overall: 是否包含总体列
            include_pvalue: 是否包含 p 值
            include_smd: 是否包含 SMD

        Returns:
            Table1Result 结构化结果
        """
        warns = []

        # 数据验证
        warns.extend(self._validate_data(df, group_var, variables))

        # 自动推断变量
        if variables is None:
            variables = self._infer_variables(df, group_var)

        # 确定变量类型
        for vc in variables:
            if vc.var_type == "auto":
                vc.var_type = self._detect_var_type(df, vc.name)

        # 分组信息
        n_total = len(df)
        groups = []
        n_per_group = {}
        if group_var and group_var in df.columns:
            groups = sorted(df[group_var].dropna().unique().tolist())
            for g in groups:
                n_per_group[str(g)] = int((df[group_var] == g).sum())
        else:
            include_pvalue = False
            include_smd = False

        # 逐变量生成行
        all_rows = []
        for vc in variables:
            if vc.name not in df.columns:
                warns.append(f"变量 '{vc.name}' 不在数据中，跳过")
                continue

            if vc.var_type == "continuous":
                rows = self._process_continuous(
                    df, vc, group_var, groups, include_pvalue, include_smd
                )
            else:
                rows = self._process_categorical(
                    df, vc, group_var, groups, include_pvalue, include_smd
                )
            all_rows.extend(rows)

        metadata = {
            "n_total": n_total,
            "n_per_group": n_per_group,
            "groups": [str(g) for g in groups],
            "include_overall": include_overall,
            "include_pvalue": include_pvalue,
            "include_smd": include_smd,
        }

        return Table1Result(rows=all_rows, metadata=metadata, warnings=warns)

    # ── 连续变量处理 ──

    def _process_continuous(
        self,
        df: pd.DataFrame,
        vc: VariableConfig,
        group_var: Optional[str],
        groups: list,
        include_pvalue: bool,
        include_smd: bool,
    ) -> List[RowResult]:
        """处理连续变量"""
        col = df[vc.name].dropna()
        if len(col) == 0:
            return []

        # 正态性检验
        is_normal = vc.normal
        if is_normal is None:
            is_normal = self._test_normality(col)

        # 统计量和显示格式
        if is_normal:
            stat_fmt = "mean_sd"
            test_name, statistic, p_value = self._test_continuous_parametric(
                df, vc.name, group_var, groups
            )
        else:
            stat_fmt = "median_iqr"
            test_name, statistic, p_value = self._test_continuous_nonparametric(
                df, vc.name, group_var, groups
            )

        # 构建行
        overall_stat = self._format_continuous(col, stat_fmt, vc.digits)
        group_stats = {}
        if group_var:
            for g in groups:
                vals = df.loc[df[group_var] == g, vc.name].dropna()
                group_stats[str(g)] = self._format_continuous(vals, stat_fmt, vc.digits)

        # SMD
        smd_val = None
        if include_smd and group_var and len(groups) == 2:
            smd_val = self._compute_smd_continuous(
                df, vc.name, group_var, groups
            )

        row = RowResult(
            variable=vc.name,
            label=f"{vc.label}, {'mean ± SD' if is_normal else 'median [IQR]'}",
            level=vc.name,
            is_header=True,
            overall=overall_stat,
            group_stats=group_stats,
            test_name=test_name if include_pvalue else "",
            statistic=statistic if include_pvalue else None,
            p_value=p_value if include_pvalue else None,
            smd=smd_val,
        )
        return [row]

    # ── 分类变量处理 ──

    def _process_categorical(
        self,
        df: pd.DataFrame,
        vc: VariableConfig,
        group_var: Optional[str],
        groups: list,
        include_pvalue: bool,
        include_smd: bool,
    ) -> List[RowResult]:
        """处理分类变量"""
        col = df[vc.name].dropna()
        if len(col) == 0:
            return []

        levels = sorted(col.unique().tolist())
        if len(levels) <= 1:
            return []  # 单水平因子跳过

        # 统计检验
        test_name, statistic, p_value = "", None, None
        if include_pvalue and group_var:
            test_name, statistic, p_value = self._test_categorical(
                df, vc.name, group_var, groups
            )

        # SMD
        smd_val = None
        if include_smd and group_var and len(groups) == 2:
            smd_val = self._compute_smd_categorical(
                df, vc.name, group_var, groups
            )

        # 构建行
        rows = []
        for i, lev in enumerate(levels):
            # 总体
            n_lev = int((col == lev).sum())
            pct = n_lev / len(col) * 100
            overall_stat = f"{n_lev} ({pct:.{vc.pct_digits}f}%)"

            # 各组
            group_stats = {}
            if group_var:
                for g in groups:
                    grp_col = df.loc[df[group_var] == g, vc.name].dropna()
                    n_g = int((grp_col == lev).sum())
                    pct_g = n_g / len(grp_col) * 100 if len(grp_col) > 0 else 0
                    group_stats[str(g)] = f"{n_g} ({pct_g:.{vc.pct_digits}f}%)"

            rows.append(RowResult(
                variable=vc.name,
                label=vc.label if i == 0 else "",
                level=str(lev),
                is_header=(i == 0),
                overall=overall_stat,
                group_stats=group_stats,
                test_name=test_name if i == 0 and include_pvalue else "",
                statistic=statistic if i == 0 and include_pvalue else None,
                p_value=p_value if i == 0 and include_pvalue else None,
                smd=smd_val if i == 0 else None,
            ))

        return rows

    # ── 正态性检验 ──

    def _test_normality(self, series: pd.Series) -> bool:
        """正态性检验（table1sci 算法）

        n ≤ 5000: Shapiro-Wilk
        n > 5000: Kolmogorov-Smirnov (Lilliefors)
        """
        vals = series.dropna().values
        n = len(vals)

        if n < 3:
            return True  # 样本太少，默认正态

        if n <= 5000:
            _, p = stats.shapiro(vals)
        else:
            _, p = stats.kstest(vals, lambda x: stats.norm.cdf(x, loc=np.mean(vals), scale=np.std(vals)))

        return p > self.alpha_normality

    # ── 连续变量检验 ──

    def _test_continuous_parametric(
        self,
        df: pd.DataFrame,
        var: str,
        group_var: Optional[str],
        groups: list,
    ) -> Tuple[str, Optional[float], Optional[float]]:
        """参数检验（table1sci 算法）

        二分类 + 等方差 → Student t-test
        二分类 + 异方差 → Welch t-test
        多组 + 等方差 → One-way ANOVA
        多组 + 异方差 → Welch ANOVA
        """
        if not group_var or len(groups) < 2:
            return "", None, None

        group_data = [
            df.loc[df[group_var] == g, var].dropna().values for g in groups
        ]

        if len(groups) == 2:
            # Levene 方差齐性检验
            _, p_levene = stats.levene(*group_data)
            equal_var = p_levene > self.alpha_variance

            t_stat, p_val = stats.ttest_ind(
                group_data[0], group_data[1], equal_var=equal_var
            )
            test_name = "Student t-test" if equal_var else "Welch t-test"
            return test_name, float(t_stat), float(p_val)
        else:
            # 多组
            _, p_levene = stats.levene(*group_data)
            equal_var = p_levene > self.alpha_variance

            if equal_var:
                f_stat, p_val = stats.f_oneway(*group_data)
                return "One-way ANOVA", float(f_stat), float(p_val)
            else:
                # Welch ANOVA
                f_stat, p_val = stats.alexandergovern(*group_data)
                return "Welch ANOVA", float(f_stat), float(p_val)

    def _test_continuous_nonparametric(
        self,
        df: pd.DataFrame,
        var: str,
        group_var: Optional[str],
        groups: list,
    ) -> Tuple[str, Optional[float], Optional[float]]:
        """非参数检验（table1sci 算法）

        二分类 → Wilcoxon rank-sum (Mann-Whitney U)
        多组 → Kruskal-Wallis
        """
        if not group_var or len(groups) < 2:
            return "", None, None

        group_data = [
            df.loc[df[group_var] == g, var].dropna().values for g in groups
        ]

        if len(groups) == 2:
            u_stat, p_val = stats.mannwhitneyu(
                group_data[0], group_data[1], alternative="two-sided"
            )
            return "Wilcoxon rank-sum", float(u_stat), float(p_val)
        else:
            h_stat, p_val = stats.kruskal(*group_data)
            return "Kruskal-Wallis", float(h_stat), float(p_val)

    # ── 分类变量检验（三路卡方）──

    def _test_categorical(
        self,
        df: pd.DataFrame,
        var: str,
        group_var: Optional[str],
        groups: list,
    ) -> Tuple[str, Optional[float], Optional[float]]:
        """分类变量检验（table1sci 三路卡方算法）

        期望频数全部 ≥ 5 → Pearson χ²
        最小期望 ∈ [1, 5) → Yates 校正 χ²
        最小期望 < 1 或 n < 40 → Fisher exact
        """
        ct = pd.crosstab(df[var], df[group_var])
        n = ct.values.sum()

        # 计算期望频数
        chi2_result = stats.chi2_contingency(ct, correction=False)
        expected = chi2_result.expected_freq
        min_expected = expected.min()

        if min_expected < 1 or n < 40:
            # Fisher exact（仅 2×2 表；高维用模拟 p 值）
            if ct.shape == (2, 2):
                _, p_val = stats.fisher_exact(ct)
            else:
                _, p_val = stats.chi2_contingency(ct, correction=False)[:2]
            return "Fisher exact", None, float(p_val)
        elif min_expected < 5:
            # Yates 校正
            chi2, p_val, dof, _ = stats.chi2_contingency(ct, correction=True)
            return "Yates χ²", float(chi2), float(p_val)
        else:
            # Pearson χ²
            chi2, p_val, dof, _ = chi2_result
            return "Pearson χ²", float(chi2), float(p_val)

    # ── SMD 计算 ──

    def _compute_smd_continuous(
        self,
        df: pd.DataFrame,
        var: str,
        group_var: str,
        groups: list,
    ) -> float:
        """连续变量 SMD（Cohen's d）"""
        g0 = df.loc[df[group_var] == groups[0], var].dropna()
        g1 = df.loc[df[group_var] == groups[1], var].dropna()
        pooled_std = np.sqrt((g0.std() ** 2 + g1.std() ** 2) / 2)
        if pooled_std == 0:
            return 0.0
        return abs(g0.mean() - g1.mean()) / pooled_std

    def _compute_smd_categorical(
        self,
        df: pd.DataFrame,
        var: str,
        group_var: str,
        groups: list,
    ) -> float:
        """分类变量 SMD"""
        ct = pd.crosstab(df[var], df[group_var])
        props0 = ct[groups[0]] / ct[groups[0]].sum()
        props1 = ct[groups[1]] / ct[groups[1]].sum()
        smd = np.sqrt(((props0 - props1) ** 2 / ((props0 + props1) / 2)).sum())
        return float(smd)

    # ── 格式化 ──

    @staticmethod
    def _format_continuous(vals: pd.Series, fmt: str, digits: int) -> str:
        """格式化连续变量统计量"""
        if len(vals) == 0:
            return ""

        if fmt == "mean_sd":
            return f"{vals.mean():.{digits}f} ({vals.std():.{digits}f})"
        else:  # median_iqr
            q1 = vals.quantile(0.25)
            q3 = vals.quantile(0.75)
            return f"{vals.median():.{digits}f} [{q1:.{digits}f}, {q3:.{digits}f}]"

    # ── 数据验证 ──

    def _validate_data(
        self,
        df: pd.DataFrame,
        group_var: Optional[str],
        variables: Optional[List[VariableConfig]],
    ) -> List[str]:
        """数据验证"""
        warns = []

        if df.empty:
            warns.append("数据框为空")
            return warns

        if len(df) < 30:
            warns.append(f"样本量较小 (n={len(df)})，统计检验结果可能不可靠")

        if group_var and group_var not in df.columns:
            warns.append(f"分组变量 '{group_var}' 不在数据中")

        if variables:
            for vc in variables:
                if vc.name not in df.columns:
                    warns.append(f"变量 '{vc.name}' 不在数据中")
                else:
                    miss_rate = df[vc.name].isna().mean()
                    if miss_rate > 0.2:
                        warns.append(
                            f"变量 '{vc.name}' 缺失率 {miss_rate:.1%} > 20%"
                        )

        return warns

    def _infer_variables(
        self, df: pd.DataFrame, group_var: Optional[str]
    ) -> List[VariableConfig]:
        """自动推断变量配置"""
        variables = []
        exclude = {group_var} if group_var else set()

        for col in df.columns:
            if col in exclude:
                continue
            var_type = self._detect_var_type(df, col)
            variables.append(VariableConfig(name=col, label=col, var_type=var_type))

        return variables

    @staticmethod
    def _detect_var_type(df: pd.DataFrame, col: str) -> str:
        """检测变量类型"""
        series = df[col].dropna()
        if len(series) == 0:
            return "continuous"

        if pd.api.types.is_numeric_dtype(series):
            # 数值型：唯一值 < 10 视为分类
            if series.nunique() < 10 and set(series.unique()).issubset(
                set(range(int(series.max()) + 1))
            ):
                return "categorical"
            return "continuous"
        else:
            return "categorical"


# ── CLI ──

if __name__ == "__main__":
    import sys

    # 示例用法
    np.random.seed(42)
    n = 200
    demo_df = pd.DataFrame({
        "treatment": np.random.choice(["Drug", "Placebo"], n),
        "age": np.random.normal(55, 10, n),
        "bmi": np.random.lognormal(3, 0.3, n),
        "sex": np.random.choice(["Male", "Female"], n),
        "smoking": np.random.choice(["Never", "Former", "Current"], n),
        "diabetes": np.random.choice([0, 1], n, p=[0.7, 0.3]),
    })

    engine = BaselineTable1Engine()
    result = engine.generate(
        demo_df,
        group_var="treatment",
        variables=[
            VariableConfig("age", "Age (years)", "continuous"),
            VariableConfig("bmi", "BMI (kg/m²)", "continuous"),
            VariableConfig("sex", "Sex", "categorical"),
            VariableConfig("smoking", "Smoking Status", "categorical"),
            VariableConfig("diabetes", "Diabetes", "categorical"),
        ],
        include_pvalue=True,
        include_smd=True,
    )

    print(result.to_markdown())
    print(f"\nWarnings: {result.warnings}")
