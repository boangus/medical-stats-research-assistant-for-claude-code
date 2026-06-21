"""
calibration_runner.py — 度量校准引擎（Python） — ⚠️ 实验性功能
==============================================
用户提供金标准分析结果 → 系统对比 → 输出 FNR/FPR/准确率报告

依赖: pandas, numpy, scipy
安装: pip install pandas numpy scipy

作者: MSRA Team
版本: 0.1.0
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 数据结构
# ============================================================================


@dataclass
class CalibrationEntry:
    """单条校准记录"""
    analysis_id: str
    # 金标准
    gold_method: str
    gold_estimate: float
    gold_lower: float
    gold_upper: float
    gold_p: float
    gold_significant: bool
    # MSRA 输出
    msra_method: Optional[str] = None
    msra_estimate: Optional[float] = None
    msra_lower: Optional[float] = None
    msra_upper: Optional[float] = None
    msra_p: Optional[float] = None
    msra_significant: Optional[bool] = None
    # 可选的元数据
    dataset: Optional[str] = None
    sample_size: Optional[int] = None
    covariates: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class CalibrationResult:
    """校准结果"""
    n_total: int = 0
    # 混淆矩阵
    tp: int = 0  # 真阳性
    tn: int = 0  # 真阴性
    fp: int = 0  # 假阳性
    fn: int = 0  # 假阴性
    # 方法匹配
    method_match: int = 0
    method_mismatch: int = 0
    method_mismatch_details: List[Dict] = field(default_factory=list)
    # 数值偏差
    absolute_errors: List[float] = field(default_factory=list)
    percentage_errors: List[float] = field(default_factory=list)
    # 统计指标
    sensitivity: float = 0.0
    specificity: float = 0.0
    fpr: float = 0.0
    fnr: float = 0.0
    ppv: float = 0.0
    npv: float = 0.0
    accuracy: float = 0.0
    f1_score: float = 0.0
    method_match_rate: float = 0.0
    mae: float = 0.0
    rmse: float = 0.0
    mape: float = 0.0
    pcc: float = 0.0


# ============================================================================
# 校准引擎
# ============================================================================


class CalibrationEngine:
    """度量校准引擎

    Parameters
    ----------
    gold_data : pd.DataFrame
        金标准数据，必含字段:
        analysis_id, gold_method, gold_estimate, gold_lower,
        gold_upper, gold_p, gold_significant
    msra_data : pd.DataFrame
        MSRA 输出数据，必含字段:
        analysis_id, msra_method, msra_estimate, msra_lower,
        msra_upper, msra_p, msra_significant
    significance_level : float
        显著性水平（默认 0.05）
    """

    def __init__(
        self,
        gold_data: pd.DataFrame,
        msra_data: pd.DataFrame,
        significance_level: float = 0.05,
    ):
        self.gold = gold_data
        self.msra = msra_data
        self.alpha = significance_level

    def run(self) -> CalibrationResult:
        """执行校准，返回完整结果"""
        # 合并金标准和 MSRA 数据
        merged = pd.merge(
            self.gold, self.msra, on="analysis_id", how="inner",
            suffixes=("_gold", "_msra"),
        )

        if len(merged) == 0:
            raise ValueError("No matching analysis_ids between gold and MSRA data")

        result = CalibrationResult(n_total=len(merged))

        # 1. 构建混淆矩阵（基于显著性判断）
        result.tp = int(((merged["gold_significant"] == True) &
                         (merged["msra_significant"] == True)).sum())
        result.tn = int(((merged["gold_significant"] == False) &
                         (merged["msra_significant"] == False)).sum())
        result.fp = int(((merged["gold_significant"] == False) &
                         (merged["msra_significant"] == True)).sum())
        result.fn = int(((merged["gold_significant"] == True) &
                         (merged["msra_significant"] == False)).sum())

        # 2. 计算分类指标
        n_pos = result.tp + result.fn
        n_neg = result.tn + result.fp

        result.sensitivity = result.tp / n_pos if n_pos > 0 else 0.0
        result.specificity = result.tn / n_neg if n_neg > 0 else 0.0
        result.fpr = result.fp / n_neg if n_neg > 0 else 0.0
        result.fnr = result.fn / n_pos if n_pos > 0 else 0.0
        result.ppv = result.tp / (result.tp + result.fp) if (result.tp + result.fp) > 0 else 0.0
        result.npv = result.tn / (result.tn + result.fn) if (result.tn + result.fn) > 0 else 0.0
        result.accuracy = (result.tp + result.tn) / result.n_total
        result.f1_score = (
            2 * result.tp / (2 * result.tp + result.fp + result.fn)
            if (2 * result.tp + result.fp + result.fn) > 0
            else 0.0
        )

        # 3. 方法匹配率
        if "gold_method" in merged.columns and "msra_method" in merged.columns:
            method_match = merged["gold_method"] == merged["msra_method"]
            result.method_match = int(method_match.sum())
            result.method_mismatch = int((~method_match).sum())
            result.method_match_rate = result.method_match / result.n_total

            # 记录方法不匹配详情
            mismatches = merged.loc[~method_match,
                ["analysis_id", "gold_method", "msra_method"]]
            result.method_mismatch_details = [
                {"analysis_id": r.analysis_id, "gold": r.gold_method, "msra": r.msra_method}
                for r in mismatches.itertuples(index=False)
            ]

        # 4. 数值偏差
        if "gold_estimate" in merged.columns and "msra_estimate" in merged.columns:
            gold_vals = merged["gold_estimate"].values
            msra_vals = merged["msra_estimate"].values

            errors = msra_vals - gold_vals
            result.absolute_errors = np.abs(errors).tolist()

            # MAPE（避免除以零）
            nonzero = gold_vals != 0
            if nonzero.any():
                pct_errors = np.abs(errors[nonzero] / gold_vals[nonzero]) * 100
                result.percentage_errors = pct_errors.tolist()
                result.mape = float(np.mean(pct_errors))
            else:
                result.mape = float("nan")

            result.mae = float(np.mean(np.abs(errors)))
            result.rmse = float(np.sqrt(np.mean(errors ** 2)))

            if len(gold_vals) > 2:
                corr, _ = stats.pearsonr(msra_vals, gold_vals)
                result.pcc = float(corr)
            else:
                result.pcc = float("nan")

        return result


# ============================================================================
# 报告生成
# ============================================================================


def format_calibration_report(result: CalibrationResult) -> str:
    """生成格式化的校准报告

    Parameters
    ----------
    result : CalibrationResult
        校准结果

    Returns
    -------
    str
        格式化报告文本
    """
    def _check(val, threshold, higher_is_better=True):
        if np.isnan(val):
            return "N/A"
        if higher_is_better:
            return "✅" if val >= threshold else "⚠️" if val >= threshold * 0.8 else "❌"
        else:
            return "✅" if val <= threshold else "⚠️" if val <= threshold * 1.5 else "❌"

    lines = []
    lines.append("═" * 60)
    lines.append("  MSRA 度量校准报告")
    lines.append("═" * 60)
    lines.append("")
    lines.append(f"  校准条目数: {result.n_total}")
    lines.append(f"  显著性水平: α = 0.05")
    lines.append("")
    lines.append("  ┌─────────────── 混淆矩阵 ───────────────┐")
    lines.append(f"  │                  Gold: Sig  Gold: Non  │")
    lines.append(f"  │  MSRA: Sig       TP={result.tp:<3}     FP={result.fp:<3}    │")
    lines.append(f"  │  MSRA: Non-Sig   FN={result.fn:<3}     TN={result.tn:<3}    │")
    lines.append("  └─────────────────────────────────────────┘")
    lines.append("")
    lines.append("  ┌─────────────── 关键指标 ───────────────┐")
    lines.append(f"  │  灵敏度 (TPR):     {result.sensitivity:>6.1%}  {_check(result.sensitivity, 0.90)}  │")
    lines.append(f"  │  特异度 (TNR):     {result.specificity:>6.1%}  {_check(result.specificity, 0.90)}  │")
    lines.append(f"  │  假阳性率 (FPR):   {result.fpr:>6.1%}  {_check(result.fpr, 0.10, False)}  │")
    lines.append(f"  │  假阴性率 (FNR):   {result.fnr:>6.1%}  {_check(result.fnr, 0.10, False)}  │")
    lines.append(f"  │  阳性预测值(PPV):  {result.ppv:>6.1%}  {_check(result.ppv, 0.85)}  │")
    lines.append(f"  │  阴性预测值(NPV):  {result.npv:>6.1%}  {_check(result.npv, 0.85)}  │")
    lines.append(f"  │  F1 分数:          {result.f1_score:>6.3f}  {_check(result.f1_score, 0.85)}  │")
    lines.append(f"  │  整体准确率:       {result.accuracy:>6.1%}  {_check(result.accuracy, 0.90)}  │")
    lines.append("  └─────────────────────────────────────────┘")
    lines.append("")

    lines.append("  ┌─────────── 方法匹配率 ───────────┐")
    lines.append(f"  │  方法选择一致:     {result.method_match:>3}/{result.n_total:<3} = {result.method_match_rate:>5.1%}  │")
    if result.method_mismatch_details:
        lines.append("  │  方法不匹配详情:                        │")
        for detail in result.method_mismatch_details[:5]:  # 最多显示5条
            lines.append(f"  │    {detail['analysis_id']}: Gold={detail['gold']} → MSRA={detail['msra']}  │")
        if len(result.method_mismatch_details) > 5:
            lines.append(f"  │    ...还有 {len(result.method_mismatch_details) - 5} 条  │")
    lines.append("  └───────────────────────────────────┘")
    lines.append("")

    lines.append("  ┌─────────── 数值偏差 ───────────────┐")
    lines.append(f"  │  MAE:          {result.mae:>8.4f}  {_check(result.mae, 0.10, False)}  │")
    lines.append(f"  │  RMSE:         {result.rmse:>8.4f}  {_check(result.rmse, 0.15, False)}  │")
    lines.append(f"  │  MAPE:         {result.mape:>7.2%}  {_check(result.mape, 0.05, False) if not np.isnan(result.mape) else 'N/A'}  │")
    lines.append(f"  │  Pearson r:    {result.pcc:>8.4f}  {_check(abs(result.pcc) if not np.isnan(result.pcc) else 0, 0.95)}  │")
    lines.append("  └─────────────────────────────────────┘")
    lines.append("")
    lines.append("  " + "═" * 56)
    lines.append("")

    return "\n".join(lines)


def save_calibration_report(result: CalibrationResult, output_path: str):
    """保存校准报告为 JSON

    Parameters
    ----------
    result : CalibrationResult
        校准结果
    output_path : str
        输出文件路径
    """
    data = asdict(result)
    # 将 numpy 类型转为原生 Python 类型
    data = json.loads(json.dumps(data, default=float))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"  校准报告已保存: {output_path}")


# ============================================================================
# 校准数据库（增量存储）
# ============================================================================


class CalibrationDatabase:
    """增量校准数据库

    每次用户纠正后自动记录，累积校准数据
    """

    def __init__(self, db_path: str = "calibration_db.json"):
        self.db_path = db_path
        self.entries: List[CalibrationEntry] = []
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                self.entries.append(CalibrationEntry(**item))

    def _save(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump([asdict(e) for e in self.entries], f, indent=2, default=str)

    def record(
        self,
        msra_result: Dict,
        gold_result: Dict,
        source: str = "user_feedback",
    ):
        """记录一次校准数据

        Parameters
        ----------
        msra_result : Dict
            MSRA 分析输出
        gold_result : Dict
            用户提供的金标准结果
        source : str
            数据来源（"user_feedback" / "formal_calibration"）
        """
        entry = CalibrationEntry(
            analysis_id=gold_result.get("analysis_id", f"auto_{len(self.entries)}"),
            gold_method=gold_result.get("method", ""),
            gold_estimate=float(gold_result.get("estimate", 0)),
            gold_lower=float(gold_result.get("lower", 0)),
            gold_upper=float(gold_result.get("upper", 0)),
            gold_p=float(gold_result.get("p", 1.0)),
            gold_significant=bool(gold_result.get("significant", False)),
            msra_method=msra_result.get("method"),
            msra_estimate=float(msra_result["estimate"]) if msra_result.get("estimate") else None,
            msra_lower=float(msra_result["lower"]) if msra_result.get("lower") else None,
            msra_upper=float(msra_result["upper"]) if msra_result.get("upper") else None,
            msra_p=float(msra_result["p"]) if msra_result.get("p") else None,
            msra_significant=bool(msra_result["significant"]) if msra_result.get("significant") is not None else None,
            notes=source,
        )
        self.entries.append(entry)
        self._save()

    def run_calibration(self) -> CalibrationResult:
        """对数据库中的所有记录运行校准"""
        if not self.entries:
            raise ValueError("No calibration data in database")

        gold_df = pd.DataFrame([
            {
                "analysis_id": e.analysis_id,
                "gold_method": e.gold_method,
                "gold_estimate": e.gold_estimate,
                "gold_lower": e.gold_lower,
                "gold_upper": e.gold_upper,
                "gold_p": e.gold_p,
                "gold_significant": e.gold_significant,
            }
            for e in self.entries
        ])

        msra_df = pd.DataFrame([
            {
                "analysis_id": e.analysis_id,
                "msra_method": e.msra_method,
                "msra_estimate": e.msra_estimate,
                "msra_lower": e.msra_lower,
                "msra_upper": e.msra_upper,
                "msra_p": e.msra_p,
                "msra_significant": e.msra_significant,
            }
            for e in self.entries
        ])

        engine = CalibrationEngine(gold_df, msra_df)
        return engine.run()


# ============================================================================
# 示例用法
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    np.random.seed(42)

    # 生成模拟金标准数据
    n = 20
    gold_data = pd.DataFrame({
        "analysis_id": [f"ANALYSIS_{i:03d}" for i in range(n)],
        "gold_method": ["Logistic Regression"] * 10 + ["Cox Regression"] * 10,
        "gold_estimate": np.random.uniform(0.5, 2.0, n),
        "gold_lower": np.random.uniform(0.3, 1.0, n),
        "gold_upper": np.random.uniform(1.5, 3.0, n),
        "gold_p": np.random.uniform(0.001, 0.5, n),
        "gold_significant": [p < 0.05 for p in np.random.uniform(0.001, 0.5, n)],
    })

    # 模拟 MSRA 输出（带一些错误）
    msra_data = gold_data.copy()
    msra_data.columns = [
        "analysis_id",
        "msra_method", "msra_estimate", "msra_lower", "msra_upper",
        "msra_p", "msra_significant",
    ]
    # 引入一些误差
    msra_data["msra_estimate"] *= np.random.uniform(0.9, 1.1, n)
    # 翻转 2 个显著性判断（模拟错误）
    flip_idx = np.random.choice(n, 2, replace=False)
    msra_data.loc[flip_idx, "msra_significant"] = ~msra_data.loc[flip_idx, "msra_significant"]
    # 翻转 1 个方法选择
    msra_data.loc[0, "msra_method"] = "Chi-square"

    logger.info("=" * 60)
    logger.info("  度量校准示例")
    logger.info("=" * 60)

    engine = CalibrationEngine(gold_data, msra_data)
    result = engine.run()

    report = format_calibration_report(result)
    logger.info("report")

    # 保存报告
    save_calibration_report(result, "calibration_report.json")

    # 演示增量校准数据库
    logger.info("\n测试增量校准数据库...")
    db = CalibrationDatabase("calibration_db_test.json")
    db.record(
        msra_result={"method": "t-test", "estimate": 2.1, "lower": 0.5,
                     "upper": 3.7, "p": 0.02, "significant": True},
        gold_result={"analysis_id": "CUSTOM_001", "method": "t-test",
                     "estimate": 2.0, "lower": 0.4, "upper": 3.6,
                     "p": 0.018, "significant": True},
    )
    logger.info("  ✅ 增量记录已保存")
    os.remove("calibration_db_test.json")

    logger.info("\n✅ 度量校准示例完成")
