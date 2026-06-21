"""
pipeline_auditor.py — 数据清洗审计追踪
=========================================
基于 ehrapy CohortTracker 的设计理念（Nature Medicine 2024），
为 MSRA Stage 1 数据准备阶段提供可追溯的审计日志。

功能:
  - 自动记录每一步数据过滤/转换/插补操作的维度变化
  - 追踪样本损失和变量变更的详细原因
  - 生成可读的 Markdown 审计报告
  - 支持导出 JSON 格式供下游质量门闸消费

参考:
  - ehrapy (Theis Lab, 2024): https://github.com/theislab/ehrapy
  - MSRA Stage 1.5 Quality Gate: data-prep/SKILL.md

依赖: pandas
安装: pip install pandas

作者: MSRA Team
版本: 0.1.0
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 审计步骤数据模型
# ============================================================================


@dataclass
class AuditStep:
    """数据清洗的单个审计步骤

    记录一次数据操作前后的维度变化及操作详情。

    Attributes
    ----------
    step_number : int
        步骤序号
    operation : str
        操作名称（如 "filter_age", "impute_missing", "remove_outliers"）
    description : str
        操作描述
    parameters : dict
        操作参数（如 {"age_min": 18, "age_max": 80}）
    pre_shape : Tuple[int, int]
        操作前的数据维度 (行, 列)
    post_shape : Tuple[int, int]
        操作后的数据维度 (行, 列)
    records_removed : int
        被移除的记录数（= pre_rows - post_rows）
    removed_reason : str
        移除原因（如 "年龄<18 岁的受试者"）
    timestamp : str
        操作时间戳
    """
    step_number: int
    operation: str = ""
    description: str = ""
    parameters: dict = field(default_factory=dict)
    pre_shape: Tuple[int, int] = (0, 0)
    post_shape: Tuple[int, int] = (0, 0)
    records_removed: int = 0
    removed_reason: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@dataclass
class PipelineSummary:
    """数据清洗流水线的汇总信息"""
    initial_rows: int = 0
    initial_cols: int = 0
    final_rows: int = 0
    final_cols: int = 0
    total_removed: int = 0
    total_steps: int = 0
    start_time: str = ""
    end_time: str = ""


# ============================================================================
# 2. PipelineAuditor 审计类
# ============================================================================


class PipelineAuditor:
    """数据清洗流水线审计追踪器

    用法:
        auditor = PipelineAuditor(data, name="吸烟与肺癌队列清洗")

        # 每次操作后调用 record()
        df = df[df["age"] >= 18]
        auditor.record("filter_age",
                        description="排除年龄<18岁",
                        parameters={"age_min": 18},
                        data=df)

        df = df.dropna(subset=["bmi"])
        auditor.record("dropna_bmi",
                        description="排除BMI缺失",
                        parameters={"subset": ["bmi"]},
                        data=df)

        # 生成审计报告
        logger.info("auditor.generate_report()")
        auditor.save_report("audit_report.md")

    Parameters
    ----------
    initial_data : pd.DataFrame
        初始（原始）数据集
    name : str
        此流水线的名称（用于报告标题）
    metadata : Optional[dict]
        额外元数据（如研究名称、分析日期）
    """

    def __init__(
        self,
        initial_data: pd.DataFrame,
        name: str = "Data Pipeline Audit",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.metadata = metadata or {}
        self._steps: List[AuditStep] = []
        self._counter = 0

        # 记录初始状态
        n_obs, n_vars = initial_data.shape
        self._initial_shape = (n_obs, n_vars)
        self._current_data = initial_data
        self._start_time = datetime.now()

        # 记录初始步
        self._counter += 1
        self._steps.append(AuditStep(
            step_number=0,
            operation="initial_data",
            description="原始数据加载",
            parameters={},
            pre_shape=(0, 0),
            post_shape=(n_obs, n_vars),
            records_removed=0,
            removed_reason="",
        ))

    @property
    def steps(self) -> List[AuditStep]:
        """所有审计步骤（只读）"""
        return list(self._steps)

    @property
    def current_data(self) -> pd.DataFrame:
        """当前数据状态（只读副本）"""
        return self._current_data.copy()

    # ------------------------------------------------------------------
    # 核心记录方法
    # ------------------------------------------------------------------

    def record(
        self,
        operation: str,
        data: pd.DataFrame,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        removed_reason: str = "",
    ) -> None:
        """记录一次数据操作

        Parameters
        ----------
        operation : str
            操作名（如 "filter_age", "impute_bmi", "remove_outliers"）
        data : pd.DataFrame
            操作**后**的数据集（用于计算维度变化）
        description : str
            操作描述
        parameters : Optional[Dict]
            操作参数
        removed_reason : str
            被移除记录的说明
        """
        pre_shape = (
            self._current_data.shape[0],
            self._current_data.shape[1],
        )
        post_shape = (data.shape[0], data.shape[1])

        self._counter += 1
        self._steps.append(AuditStep(
            step_number=self._counter,
            operation=operation,
            description=description or operation,
            parameters=parameters or {},
            pre_shape=pre_shape,
            post_shape=post_shape,
            records_removed=pre_shape[0] - post_shape[0],
            removed_reason=removed_reason,
        ))

        # 更新当前数据引用
        self._current_data = data

    def record_filter(
        self,
        condition: str,
        data_before: pd.DataFrame,
        data_after: pd.DataFrame,
        reason: str = "",
    ) -> None:
        """记录一次按条件过滤操作（便捷方法）

        Parameters
        ----------
        condition : str
            过滤条件描述（如 "age >= 18")
        data_before : pd.DataFrame
            过滤前的数据
        data_after : pd.DataFrame
            过滤后的数据
        reason : str
            过滤原因
        """
        self.record(
            operation=f"filter_{condition.replace(' ', '_')[:40]}",
            description=f"按条件过滤: {condition}",
            parameters={"condition": condition},
            data=data_after,
            removed_reason=reason,
        )

    def record_dropna(
        self,
        columns: List[str],
        data_before: pd.DataFrame,
        data_after: pd.DataFrame,
    ) -> None:
        """记录一次缺失值删除操作（便捷方法）

        Parameters
        ----------
        columns : List[str]
            检查缺失值的列
        data_before : pd.DataFrame
            删除前的数据
        data_after : pd.DataFrame
            删除后的数据
        """
        n_removed = len(data_before) - len(data_after)
        self.record(
            operation=f"dropna_{'_'.join(columns)[:30]}",
            description=f"删除 {columns} 列有缺失值的记录",
            parameters={"columns": columns, "how": "any"},
            data=data_after,
            removed_reason=f"以下列存在缺失值: {columns} ({n_removed} 条)",
        )

    def record_imputation(
        self,
        column: str,
        method: str,
        data_before: pd.DataFrame,
        data_after: pd.DataFrame,
        n_imputed: int = 0,
    ) -> None:
        """记录一次缺失值插补操作（便捷方法）

        Parameters
        ----------
        column : str
            被插补的列
        method : str
            插补方法（如 "mean", "median", "mice", "knn"）
        data_before : pd.DataFrame
            插补前的数据
        data_after : pd.DataFrame
            插补后的数据
        n_imputed : int
            被填充的缺失值数量（可选）
        """
        self.record(
            operation=f"impute_{column}",
            description=f"用 {method} 插补 {column} 的缺失值",
            parameters={
                "column": column,
                "method": method,
                "n_imputed": n_imputed,
            },
            data=data_after,
            removed_reason=f"插补 {column} 列 {n_imputed} 个缺失值" if n_imputed else "",
        )

    def record_derive(
        self,
        new_column: str,
        formula: str,
        data_after: pd.DataFrame,
        description: str = "",
    ) -> None:
        """记录一次衍生变量创建操作

        Parameters
        ----------
        new_column : str
            新变量名
        formula : str
            衍生公式描述
        data_after : pd.DataFrame
            衍生后的数据
        description : str
            操作描述
        """
        self.record(
            operation=f"derive_{new_column}",
            description=description or f"衍生变量: {new_column} = {formula}",
            parameters={"new_column": new_column, "formula": formula},
            data=data_after,
        )

    # ------------------------------------------------------------------
    # 报告生成
    # ------------------------------------------------------------------

    def _build_summary(self) -> PipelineSummary:
        """构建流水线汇总"""
        initial_rows, initial_cols = self._initial_shape
        final_rows, final_cols = self._current_data.shape
        total_removed = initial_rows - final_rows

        return PipelineSummary(
            initial_rows=initial_rows,
            initial_cols=initial_cols,
            final_rows=final_rows,
            final_cols=final_cols,
            total_removed=total_removed,
            total_steps=self._counter,
            start_time=self._start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def generate_report(self, verbose: bool = True) -> str:
        """生成 Markdown 格式的审计报告

        Parameters
        ----------
        verbose : bool
            是否包含详细的分步信息

        Returns
        -------
        str
            Markdown 格式的审计报告
        """
        summary = self._build_summary()

        lines = [
            f"# 数据清洗审计报告: {self.name}",
            "",
            f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 流水线汇总",
            "",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 初始样本量 | {summary.initial_rows} |",
            f"| 最终样本量 | {summary.final_rows} |",
            f"| 移除样本量 | {summary.total_removed} |",
            f"| 保留比例 | {summary.final_rows / summary.initial_rows * 100:.1f}% |"
            if summary.initial_rows > 0 else "| 保留比例 | - |",
            f"| 初始变量数 | {summary.initial_cols} |",
            f"| 最终变量数 | {summary.final_cols} |",
            f"| 操作步骤 | {summary.total_steps} |",
            f"| 开始时间 | {summary.start_time} |",
            f"| 结束时间 | {summary.end_time} |",
            "",
        ]

        # 额外元数据
        if self.metadata:
            lines.append("### 元数据")
            lines.append("")
            for key, value in self.metadata.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        if verbose and len(self._steps) > 1:
            lines.extend([
                "---",
                "",
                "## 分步审计日志",
                "",
                f"| 步骤 | 操作 | 描述 | 参数 | 操作前 | 操作后 | 移除 | 原因 |",
                f"|------|------|------|------|--------|--------|------|------|",
            ])

            for step in self._steps[1:]:  # 跳过 step 0 (initial)
                params_str = ", ".join(
                    f"{k}={v}" for k, v in step.parameters.items()
                ) if step.parameters else "-"
                lines.append(
                    f"| {step.step_number} "
                    f"| {step.operation} "
                    f"| {step.description} "
                    f"| {params_str} "
                    f"| ({step.pre_shape[0]}, {step.pre_shape[1]}) "
                    f"| ({step.post_shape[0]}, {step.post_shape[1]}) "
                    f"| {step.records_removed} "
                    f"| {step.removed_reason} |"
                )

            lines.append("")

        # 样本量变化趋势图（文本版）
        if len(self._steps) > 1:
            lines.extend([
                "---",
                "",
                "## 样本量变化趋势",
                "",
                "```",
                f" 初始: {self._initial_shape[0]}",
            ])
            for step in self._steps[1:]:
                bar_len = max(1, int(step.post_shape[0] / max(1, self._initial_shape[0]) * 40))
                bar = "█" * bar_len + "░" * (40 - bar_len)
                lines.append(
                    f"  #{step.step_number} {step.operation:<30s} "
                    f"{step.post_shape[0]:>6d} |{bar}|"
                )
            lines.extend([
                "```",
                "",
            ])

        # 保留率
        if self._initial_shape[0] > 0:
            retention = self._current_data.shape[0] / self._initial_shape[0] * 100
            lines.extend([
                "---",
                "",
                "## 质量评估",
                "",
                f"**总体保留率**: {retention:.1f}%",
                "",
            ])
            if retention < 50:
                lines.append("> ⚠️ **警告**: 保留率低于 50%，建议检查过滤条件是否过严。")
            elif retention < 30:
                lines.append("> ❌ **严重警告**: 保留率低于 30%，强烈的选择偏倚风险，需暂停流程并重新评估。")
            else:
                lines.append("> ✅ 保留率在可接受范围内。")
            lines.append("")

        return "\n".join(lines)

    def generate_json_report(self) -> Dict[str, Any]:
        """生成 JSON 格式的审计报告（供质量门闸消费）"""
        summary = self._build_summary()

        return {
            "pipeline_name": self.name,
            "metadata": self.metadata,
            "summary": asdict(summary),
            "steps": [asdict(s) for s in self._steps],
            "retention_rate": (
                self._current_data.shape[0] / self._initial_shape[0]
                if self._initial_shape[0] > 0 else 0.0
            ),
        }

    def save_report(
        self,
        path: Union[str, Path],
        fmt: str = "md",
    ) -> None:
        """将审计报告保存到文件

        Parameters
        ----------
        path : str | Path
            输出路径
        fmt : str
            "md" (Markdown) 或 "json"
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "json":
            report = self.generate_json_report()
            path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            report = self.generate_report()
            path.write_text(report, encoding="utf-8")

        logger.info(f"审计报告已保存: {path}")


# ============================================================================
# 3. 使用示例
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    import numpy as np

    # --- 模拟临床数据 ---
    np.random.seed(42)
    n = 500

    raw_data = pd.DataFrame({
        "age": np.random.normal(55, 15, n),
        "bmi": np.random.normal(27, 5, n),
        "sbp": np.random.normal(130, 20, n),
        "treatment": np.random.binomial(1, 0.5, n),
        "outcome": np.random.binomial(1, 0.3, n),
        "sex": np.random.choice(["M", "F"], n),
        "smoking": np.random.choice(["Never", "Former", "Current"], n),
    })

    # 人为引入缺失值和异常值
    raw_data.loc[0:20, "bmi"] = np.nan
    raw_data.loc[21:30, "sbp"] = np.nan
    raw_data.loc[31:35, "age"] = 0  # 异常值
    raw_data.loc[36:40, "bmi"] = 65  # 极端异常值

    logger.info(f"原始数据: {raw_data.shape}")

    # --- 使用 PipelineAuditor ---
    auditor = PipelineAuditor(
        raw_data,
        name="示例临床试验数据清洗",
        metadata={"研究": "Drug vs Placebo 疗效分析", "分析日期": "2026-05-29"},
    )

    # Step 1: 排除年龄<18
    df = raw_data.copy()
    df_before = df
    df = df[df["age"] >= 18].copy()
    auditor.record_filter("age >= 18", df_before, df, "排除未成年受试者")

    # Step 2: 排除年龄异常（>100）
    df_before = df
    df = df[df["age"] <= 100].copy()
    auditor.record_filter("age <= 100", df_before, df, "排除年龄异常值")

    # Step 3: 删除BMI缺失
    df_before = df
    df = df.dropna(subset=["bmi"]).copy()
    auditor.record_dropna(["bmi"], df_before, df)

    # Step 4: SBP中位数插补
    df_before = df.copy()
    sbp_median = df["sbp"].median()
    n_missing_sbp = df["sbp"].isna().sum()
    df["sbp"] = df["sbp"].fillna(sbp_median)
    auditor.record_imputation("sbp", "median", df_before, df, n_missing_sbp)

    # Step 5: 衍生变量 - BMI分组
    df_before = df.copy()
    df["bmi_group"] = pd.cut(
        df["bmi"],
        bins=[0, 18.5, 25, 30, 100],
        labels=["Underweight", "Normal", "Overweight", "Obese"]
    )
    auditor.record_derive("bmi_group", "cut(bmi, [0,18.5,25,30,100])", df)

    # Step 6: 衍生变量 - 年龄分组
    df_before = df.copy()
    df["age_group"] = pd.cut(
        df["age"],
        bins=[0, 40, 60, 80, 120],
        labels=["<40", "40-59", "60-79", "80+"]
    )
    auditor.record_derive("age_group", "cut(age, [0,40,60,80,120])", df)

    # --- 生成报告 ---
    report = auditor.generate_report()
    logger.info("report")

    # --- 保存报告 ---
    # auditor.save_report("audit_report.md")
    # auditor.save_report("audit_report.json", fmt="json")
