"""统计结果格式化器

将统计分析输出转换为学术期刊标准格式。
支持中英文双语输出，遵循 ICMJE 和 APA 格式规范。

Usage:
    >>> formatter = StatFormatter()
    >>> formatter.ci(1.23, 1.05, 1.45)
    'HR=1.23, 95%CI: 1.05-1.45'
    >>> formatter.p_value(0.0001)
    'P<0.001'
    >>> formatter.mean_sd(23.5, 4.2)
    '23.5±4.2'
    >>> formatter.proportion(45, 100)
    '45 (45.0%)'
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


class StatFormatter:
    """统计结果格式化器

    将统计分析输出转换为学术期刊标准格式。

    Attributes:
        lang: 输出语言，``"zh"`` 中文或 ``"en"`` 英文。
    """

    # ── 初始化 ──────────────────────────────────────────────

    def __init__(self, lang: str = "zh") -> None:
        """初始化格式化器

        Args:
            lang: 输出语言，``"zh"`` 或 ``"en"``。

        Examples:
            >>> f = StatFormatter()
            >>> f.lang
            'zh'
        """
        if lang not in ("zh", "en"):
            raise ValueError(f"lang 必须是 'zh' 或 'en'，收到: '{lang}'")
        self.lang = lang

    # ── 数值格式化 ──────────────────────────────────────────

    @staticmethod
    def _round(value: Union[int, float], decimals: int = 2) -> str:
        """格式化数值，避免尾随零

        Args:
            value: 数值。
            decimals: 小数位数。

        Returns:
            格式化后的字符串。

        Examples:
            >>> StatFormatter._round(1.230, 2)
            '1.23'
            >>> StatFormatter._round(1.0, 2)
            '1'
            >>> StatFormatter._round(0.123456, 4)
            '0.1235'
        """
        if isinstance(value, int):
            return str(value)
        rounded = round(float(value), decimals)
        # 如果四舍五入后是整数，不显示小数点
        if rounded == int(rounded):
            return str(int(rounded))
        # 去除尾随零
        return f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")

    # ── P 值 ───────────────────────────────────────────────

    def p_value(self, p: float, method: str = "") -> str:
        """格式化 P 值

        规则：
        - P < 0.001 时输出 ``P<0.001``
        - 永远不输出 ``P=0.000``
        - 可选附加检验方法名称

        Args:
            p: P 值。
            method: 检验方法名（可选），如 ``"Log-rank"``、``"Chi-square"``。

        Returns:
            格式化后的 P 值字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.p_value(0.0001)
            'P<0.001'
            >>> f.p_value(0.023)
            'P=0.023'
            >>> f.p_value(0.0001, method="Log-rank")
            'P<0.001 (Log-rank)'
            >>> f.p_value(1.0)
            'P=1.00'
            >>> f.p_value(0.0)
            'P<0.001'
        """
        if not isinstance(p, (int, float)):
            raise TypeError(f"p 必须是数值，收到: {type(p).__name__}")
        if math.isnan(p):
            return "P=NA"

        p_float = float(p)

        if p_float < 0 or p_float > 1:
            raise ValueError(f"P 值必须在 [0, 1] 范围内，收到: {p_float}")

        if p_float < 0.001:
            p_str = "P<0.001"
        else:
            p_str = f"P={self._round(p_float, 3)}"

        if method:
            return f"{p_str} ({method})"
        return p_str

    # ── 置信区间 ────────────────────────────────────────────

    def ci(
        self,
        estimate: float,
        lower: float,
        upper: float,
        label: str = "HR",
        decimals: int = 2,
    ) -> str:
        """格式化点估计和置信区间

        Args:
            estimate: 点估计值。
            lower: 置信区间下限。
            upper: 置信区间上限。
            label: 效应量标签（如 ``"HR"``、``"OR"``、``"RR"``、``"β"``）。
            decimals: 小数位数（默认 2）。

        Returns:
            格式化后的字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.ci(1.23, 1.05, 1.45)
            'HR=1.23, 95%CI: 1.05-1.45'
            >>> f.ci(2.5, 1.1, 5.8, label="OR")
            'OR=2.5, 95%CI: 1.1-5.8'
            >>> f.ci(0.85, 0.70, 0.99, label="RR", decimals=3)
            'RR=0.85, 95%CI: 0.700-0.990'
        """
        est_str = self._round(estimate, decimals)
        lo_str = self._round(lower, decimals)
        hi_str = self._round(upper, decimals)

        if self.lang == "zh":
            return f"{label}={est_str}, 95%CI: {lo_str}-{hi_str}"
        return f"{label}={est_str}, 95%CI: {lo_str}-{hi_str}"

    def ci_with_level(
        self,
        estimate: float,
        lower: float,
        upper: float,
        level: int = 95,
        label: str = "HR",
        decimals: int = 2,
    ) -> str:
        """格式化指定置信水平的置信区间

        Args:
            estimate: 点估计值。
            lower: 置信区间下限。
            upper: 置信区间上限。
            level: 置信水平（如 90、95、99）。
            label: 效应量标签。
            decimals: 小数位数。

        Returns:
            格式化后的字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.ci_with_level(1.23, 1.05, 1.45, level=99)
            'HR=1.23, 99%CI: 1.05-1.45'
        """
        est_str = self._round(estimate, decimals)
        lo_str = self._round(lower, decimals)
        hi_str = self._round(upper, decimals)
        return f"{label}={est_str}, {level}%CI: {lo_str}-{hi_str}"

    # ── 中位数和四分位距 ────────────────────────────────────

    def median_iqr(
        self,
        median: float,
        q1: float,
        q3: float,
        unit: str = "",
        style: str = "full",
        decimals: int = 1,
    ) -> str:
        """格式化中位数和四分位距

        Args:
            median: 中位数。
            q1: 第一四分位数。
            q3: 第三四分位数。
            unit: 单位（可选，附加在中位数后）。
            style: 输出风格：
                - ``"full"``: ``"24.5 (Q1: 18.3, Q3: 30.7)"``
                - ``"compact"``: ``"24.5 (18.3, 30.7)"``
            decimals: 小数位数。

        Returns:
            格式化后的字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.median_iqr(24.5, 18.3, 30.7)
            '24.5 (Q1: 18.3, Q3: 30.7)'
            >>> f.median_iqr(24.5, 18.3, 30.7, style="compact")
            '24.5 (18.3, 30.7)'
            >>> f.median_iqr(24.5, 18.3, 30.7, unit="个月")
            '24.5个月 (Q1: 18.3, Q3: 30.7)'
        """
        med_str = self._round(median, decimals)
        q1_str = self._round(q1, decimals)
        q3_str = self._round(q3, decimals)

        unit_part = unit if unit else ""

        if style == "compact":
            return f"{med_str}{unit_part} ({q1_str}, {q3_str})"
        return f"{med_str}{unit_part} (Q1: {q1_str}, Q3: {q3_str})"

    # ── 均数±标准差 ─────────────────────────────────────────

    def mean_sd(
        self,
        mean: float,
        sd: float,
        unit: str = "",
        decimals: int = 1,
    ) -> str:
        """格式化均数±标准差

        Args:
            mean: 均值。
            sd: 标准差。
            unit: 单位（可选）。
            decimals: 小数位数。

        Returns:
            格式化后的字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.mean_sd(23.5, 4.2)
            '23.5±4.2'
            >>> f.mean_sd(23.5, 4.2, unit="kg")
            '23.5±4.2 kg'
            >>> f.mean_sd(120.0, 15.0, unit="mmHg", decimals=0)
            '120±15 mmHg'
        """
        mean_str = self._round(mean, decimals)
        sd_str = self._round(sd, decimals)
        unit_part = f" {unit}" if unit else ""
        return f"{mean_str}±{sd_str}{unit_part}"

    # ── 频数和百分比 ────────────────────────────────────────

    def proportion(
        self,
        n: int,
        total: int,
        decimal: int = 1,
        show_total: bool = False,
    ) -> str:
        """格式化频数和百分比

        Args:
            n: 频数。
            total: 总数。
            decimal: 百分比小数位数。
            show_total: 是否显示总数。

        Returns:
            格式化后的字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.proportion(45, 100)
            '45 (45.0%)'
            >>> f.proportion(45, 100, decimal=0)
            '45 (45%)'
            >>> f.proportion(45, 100, show_total=True)
            '45/100 (45.0%)'
            >>> f.proportion(0, 100)
            '0 (0.0%)'
        """
        if not isinstance(n, (int, float)):
            raise TypeError(f"n 必须是整数，收到: {type(n).__name__}")
        if not isinstance(total, (int, float)):
            raise TypeError(f"total 必须是整数，收到: {type(total).__name__}")
        if total < 0:
            raise ValueError(f"total 不能为负数: {total}")
        if n < 0:
            raise ValueError(f"n 不能为负数: {n}")
        if n > total:
            raise ValueError(f"n ({n}) 不能大于 total ({total})")

        if total == 0:
            pct_str = f"0.{('0' * decimal)}"
        else:
            pct = (float(n) / float(total)) * 100
            pct_str = self._round(pct, decimal)
            if decimal > 0 and "." not in pct_str:
                pct_str = f"{pct_str}.{'0' * decimal}"

        n_int = int(n)
        if show_total:
            return f"{n_int}/{int(total)} ({pct_str}%)"
        return f"{n_int} ({pct_str}%)"

    # ── 生存时间 ────────────────────────────────────────────

    def survival_time(
        self,
        median: float,
        lower_ci: float,
        upper_ci: float,
        unit: str = "月",
        decimals: int = 1,
    ) -> str:
        """格式化生存时间

        Args:
            median: 中位生存时间。
            lower_ci: 置信区间下限。
            upper_ci: 置信区间上限。
            unit: 时间单位。
            decimals: 小数位数。

        Returns:
            格式化后的字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.survival_time(24.5, 18.3, 30.7)
            '24.5个月 (95%CI: 18.3-30.7)'
            >>> f.survival_time(24.5, 18.3, 30.7, unit="months")
            '24.5months (95%CI: 18.3-30.7)'
        """
        med_str = self._round(median, decimals)
        lo_str = self._round(lower_ci, decimals)
        hi_str = self._round(upper_ci, decimals)
        return f"{med_str}{unit} (95%CI: {lo_str}-{hi_str})"

    # ── 效应量 ──────────────────────────────────────────────

    def effect_size(
        self,
        estimate: float,
        lower: float,
        upper: float,
        effect_type: str = "HR",
        decimals: int = 2,
    ) -> str:
        """格式化效应量（HR / OR / RR / β / SMD）

        Args:
            estimate: 点估计值。
            lower: 置信区间下限。
            upper: 置信区间上限。
            effect_type: 效应量类型。
            decimals: 小数位数。

        Returns:
            格式化后的字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.effect_size(1.23, 1.05, 1.45)
            'HR=1.23, 95%CI: 1.05-1.45'
            >>> f.effect_size(-0.45, -0.80, -0.10, effect_type="SMD")
            'SMD=-0.45, 95%CI: -0.80--0.10'
        """
        return self.ci(estimate, lower, upper, label=effect_type, decimals=decimals)

    # ── 表格脚注 ────────────────────────────────────────────

    def table_note(
        self,
        variables: Optional[Dict[str, str]] = None,
        test_method: str = "",
        confidence: int = 95,
    ) -> str:
        """生成表格脚注

        Args:
            variables: 变量类型字典，格式 ``{变量名: 类型}``，类型为
                ``"continuous"`` / ``"categorical"`` / ``"median"``。
                若为 None 则使用默认通用脚注。
            test_method: 检验方法名。
            confidence: 置信水平。

        Returns:
            格式化后的脚注文本。

        Examples:
            >>> f = StatFormatter()
            >>> f.table_note()
            '连续变量以均数±标准差或中位数(Q1,Q3)表示；分类变量以频数(百分比)表示。'
            >>> f.table_note(test_method="Log-rank")
            '连续变量以均数±标准差或中位数(Q1,Q3)表示；分类变量以频数(百分比)表示。Log-rank 检验。'
        """
        parts: List[str] = []

        if variables is None:
            if self.lang == "zh":
                parts.append(
                    "连续变量以均数±标准差或中位数(Q1,Q3)表示；"
                    "分类变量以频数(百分比)表示。"
                )
            else:
                parts.append(
                    "Continuous variables are presented as mean±SD or median (Q1, Q3); "
                    "categorical variables are presented as n (%)."
                )
        else:
            has_continuous = False
            has_median = False
            has_categorical = False

            for vtype in variables.values():
                if vtype == "continuous":
                    has_continuous = True
                elif vtype == "median":
                    has_median = True
                elif vtype == "categorical":
                    has_categorical = True

            if self.lang == "zh":
                if has_continuous and has_median:
                    parts.append(
                        "连续变量以均数±标准差或中位数(Q1,Q3)表示。"
                    )
                elif has_continuous:
                    parts.append("连续变量以均数±标准差表示。")
                elif has_median:
                    parts.append("连续变量以中位数(Q1,Q3)表示。")
                if has_categorical:
                    parts.append("分类变量以频数(百分比)表示。")
            else:
                if has_continuous and has_median:
                    parts.append(
                        "Continuous variables are presented as mean±SD or median (Q1, Q3). "
                    )
                elif has_continuous:
                    parts.append("Continuous variables are presented as mean±SD. ")
                elif has_median:
                    parts.append(
                        "Continuous variables are presented as median (Q1, Q3). "
                    )
                if has_categorical:
                    parts.append("Categorical variables are presented as n (%). ")

        if confidence != 95:
            if self.lang == "zh":
                parts.append(f"{confidence}%置信区间。")
            else:
                parts.append(f"{confidence}% confidence interval.")

        if test_method:
            if self.lang == "zh":
                parts.append(f"{test_method}检验。")
            else:
                parts.append(f"{test_method} test.")

        return "".join(parts)

    # ── 通用格式化 ──────────────────────────────────────────

    def format_table_cell(self, value: Any, value_type: str, **kwargs: Any) -> str:
        """通用表格单元格格式化

        Args:
            value: 值。可以是数值或字典。
            value_type: 类型标识，可选值：
                - ``"mean_sd"``: 需要 kwargs ``mean`` 和 ``sd``
                - ``"median_iqr"``: 需要 kwargs ``median``、``q1``、``q3``
                - ``"proportion"``: 需要 kwargs ``n`` 和 ``total``
                - ``"hr"`` / ``"or"`` / ``"rr"``: 需要 kwargs ``estimate``、``lower``、``upper``
                - ``"p_value"``: value 即为 P 值
            **kwargs: 传递给具体格式化方法的参数。

        Returns:
            格式化后的字符串。

        Raises:
            ValueError: 未知的 value_type。

        Examples:
            >>> f = StatFormatter()
            >>> f.format_table_cell(0.001, "p_value")
            'P=0.001'
            >>> f.format_table_cell(None, "mean_sd", mean=23.5, sd=4.2)
            '23.5±4.2'
            >>> f.format_table_cell(None, "median_iqr", median=24.5, q1=18.3, q3=30.7)
            '24.5 (Q1: 18.3, Q3: 30.7)'
            >>> f.format_table_cell(None, "proportion", n=45, total=100)
            '45 (45.0%)'
        """
        if value_type == "mean_sd":
            return self.mean_sd(
                mean=kwargs.get("mean", 0),
                sd=kwargs.get("sd", 0),
                unit=kwargs.get("unit", ""),
                decimals=kwargs.get("decimals", 1),
            )
        elif value_type == "median_iqr":
            return self.median_iqr(
                median=kwargs.get("median", 0),
                q1=kwargs.get("q1", 0),
                q3=kwargs.get("q3", 0),
                unit=kwargs.get("unit", ""),
                style=kwargs.get("style", "full"),
                decimals=kwargs.get("decimals", 1),
            )
        elif value_type == "proportion":
            return self.proportion(
                n=kwargs.get("n", 0),
                total=kwargs.get("total", 1),
                decimal=kwargs.get("decimal", 1),
                show_total=kwargs.get("show_total", False),
            )
        elif value_type in ("hr", "or", "rr", "beta", "smd"):
            label_map = {
                "hr": "HR",
                "or": "OR",
                "rr": "RR",
                "beta": "β",
                "smd": "SMD",
            }
            return self.ci(
                estimate=kwargs.get("estimate", 0),
                lower=kwargs.get("lower", 0),
                upper=kwargs.get("upper", 0),
                label=label_map[value_type],
                decimals=kwargs.get("decimals", 2),
            )
        elif value_type == "p_value":
            return self.p_value(
                p=float(value) if value is not None else 1.0,
                method=kwargs.get("method", ""),
            )
        else:
            raise ValueError(
                f"未知的 value_type: '{value_type}'。"
                f"支持的类型: mean_sd, median_iqr, proportion, hr, or, rr, beta, smd, p_value"
            )

    # ── 批量格式化 ──────────────────────────────────────────

    def format_row(
        self,
        data: Dict[str, Any],
        template: Dict[str, str],
    ) -> Dict[str, str]:
        """根据模板批量格式化一行数据

        Args:
            data: 原始数据字典。
            template: 格式模板，格式 ``{列名: value_type}``。

        Returns:
            格式化后的字典。

        Examples:
            >>> f = StatFormatter()
            >>> data = {"age_mean": 65.3, "age_sd": 8.2, "n_male": 45, "n_total": 100}
            >>> template = {"age_mean": "mean_sd", "n_male": "proportion"}
            >>> result = f.format_row(data, template)
            >>> result["age_mean"]
            '65.3±8.2'
        """
        result: Dict[str, str] = {}
        for col, vtype in template.items():
            if col not in data:
                result[col] = "NA"
                continue

            val = data[col]

            if vtype == "mean_sd":
                # 期望 data 中有 {col}_mean 和 {col}_sd
                mean_val = data.get(f"{col}_mean", val)
                sd_val = data.get(f"{col}_sd", 0)
                result[col] = self.mean_sd(
                    mean=float(mean_val),
                    sd=float(sd_val),
                    unit=data.get(f"{col}_unit", ""),
                )
            elif vtype == "median_iqr":
                median_val = data.get(f"{col}_median", val)
                q1_val = data.get(f"{col}_q1", 0)
                q3_val = data.get(f"{col}_q3", 0)
                result[col] = self.median_iqr(
                    median=float(median_val),
                    q1=float(q1_val),
                    q3=float(q3_val),
                    unit=data.get(f"{col}_unit", ""),
                )
            elif vtype == "proportion":
                n_val = data.get(f"{col}_n", val)
                total_val = data.get(f"{col}_total", 1)
                result[col] = self.proportion(
                    n=int(n_val),
                    total=int(total_val),
                )
            elif vtype in ("hr", "or", "rr", "beta", "smd"):
                est = data.get(f"{col}_estimate", val)
                lo = data.get(f"{col}_lower", 0)
                hi = data.get(f"{col}_upper", 0)
                result[col] = self.format_table_cell(
                    None,
                    vtype,
                    estimate=float(est),
                    lower=float(lo),
                    upper=float(hi),
                )
            elif vtype == "p_value":
                result[col] = self.p_value(p=float(val))
            else:
                result[col] = str(val)

        return result

    # ── 辅助方法 ────────────────────────────────────────────

    def detect_distribution(
        self,
        values: Sequence[float],
        normality_p: Optional[float] = None,
    ) -> str:
        """根据数据和正态性检验结果推荐格式化方式

        Args:
            values: 数值序列。
            normality_p: 正态性检验的 P 值（如 Shapiro-Wilk）。
                若为 None 则基于经验规则判断。

        Returns:
            ``"mean_sd"`` 或 ``"median_iqr"``。

        Examples:
            >>> f = StatFormatter()
            >>> f.detect_distribution([1, 2, 3, 4, 5])
            'mean_sd'
            >>> f.detect_distribution([1, 1, 1, 1, 100])
            'median_iqr'
        """
        if normality_p is not None:
            return "mean_sd" if normality_p >= 0.05 else "median_iqr"

        vals = [float(v) for v in values if not math.isnan(float(v))]
        if len(vals) < 3:
            return "mean_sd"

        import statistics

        mean_val = statistics.mean(vals)
        median_val = statistics.median(vals)
        stdev = statistics.stdev(vals)

        if stdev == 0:
            return "mean_sd"

        # 经验法则：均值与中位数差异 > 0.5 倍标准差，或变异系数 > 0.5
        skew_ratio = abs(mean_val - median_val) / stdev
        cv = stdev / abs(mean_val) if mean_val != 0 else float("inf")

        if skew_ratio > 0.5 or cv > 0.5:
            return "median_iqr"
        return "mean_sd"

    def format_narrative(
        self,
        variable: str,
        mean_val: Optional[float] = None,
        sd_val: Optional[float] = None,
        median_val: Optional[float] = None,
        q1_val: Optional[float] = None,
        q3_val: Optional[float] = None,
        n: Optional[int] = None,
        total: Optional[int] = None,
        unit: str = "",
    ) -> str:
        """生成叙述性统计描述

        根据提供的参数自动选择 mean±SD 或 median (Q1, Q3) 格式。

        Args:
            variable: 变量名。
            mean_val: 均值。
            sd_val: 标准差。
            median_val: 中位数。
            q1_val: Q1。
            q3_val: Q3。
            n: 频数。
            total: 总数。
            unit: 单位。

        Returns:
            叙述性统计描述字符串。

        Examples:
            >>> f = StatFormatter()
            >>> f.format_narrative("年龄", mean_val=65.3, sd_val=8.2)
            '年龄: 65.3±8.2'
            >>> f.format_narrative("PSA", median_val=12.5, q1_val=6.3, q3_val=25.1, unit="ng/mL")
            'PSA: 12.5ng/mL (Q1: 6.3, Q3: 25.1)'
            >>> f.format_narrative("糖尿病", n=45, total=100)
            '糖尿病: 45 (45.0%)'
        """
        parts: List[str] = []

        if n is not None and total is not None:
            parts.append(f"{variable}: {self.proportion(n, total)}")
        elif median_val is not None and q1_val is not None and q3_val is not None:
            parts.append(
                f"{variable}: {self.median_iqr(median_val, q1_val, q3_val, unit=unit)}"
            )
        elif mean_val is not None and sd_val is not None:
            parts.append(f"{variable}: {self.mean_sd(mean_val, sd_val, unit=unit)}")
        else:
            parts.append(f"{variable}: NA")

        return "".join(parts)
