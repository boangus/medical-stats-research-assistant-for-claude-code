"""
Cross-Domain Quality Gates - 跨领域融合质量门闸

实现 Gate CD-1.5（数据对齐门闸）和 Gate CD-3.5（融合结果门闸）。
复用 shared/quality_gates/ 框架的 GateRunner + CheckItemResult 模式。
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# 确保 shared 目录在 import 路径中
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.quality_gates.gate_runner import (
    GateRunner,
    GateType,
    GateResult,
    GateVerdict,
    CheckItemResult,
    RunMode,
)

# 场景所需模态映射
SCENARIO_REQUIRED_MODALITIES: Dict[str, List[str]] = {
    "correlation": ["radiomics", "expression"],
    "prediction": ["realtime", "labels"],
    "visualization": [],  # 至少 1 个模态即可
    "full": ["radiomics", "expression", "realtime", "labels"],
}


class CrossDomainQualityGateChecker:
    """跨领域融合质量门闸检查器

    封装 Gate CD-1.5 和 Gate CD-3.5 的具体检查逻辑，
    产出 CheckItemResult 列表供 GateRunner 消费。

    Usage:
        checker = CrossDomainQualityGateChecker(study_id="CD-2026-001")

        # Gate CD-1.5: 数据对齐检查
        gate_result = checker.run_gate_cd15(
            data_sources={"radiomics": df_features, "expression": df_expr},
            min_samples=3,
            scenario="correlation",
        )

        # Gate CD-3.5: 融合结果检查
        gate_result = checker.run_gate_cd35(
            correlation_results=corr_dict,
            model_metrics=metrics_dict,
            visualization_data=viz_dict,
        )
    """

    def __init__(
        self,
        study_id: str,
        project_root: Optional[str] = None,
    ):
        """初始化跨领域融合质量门闸检查器

        Args:
            study_id: 研究编号
            project_root: 项目根目录 (可选)
        """
        self.study_id = study_id
        self._runner = GateRunner(
            study_id=study_id,
            project_root=project_root,
        )

    # ===== Gate CD-1.5: 数据对齐门闸 (3 项) =====

    def run_gate_cd15(
        self,
        data_sources: Dict[str, Any],
        min_samples: int = 3,
        scenario: str = "correlation",
    ) -> GateResult:
        """执行 Gate CD-1.5 全部 3 项检查

        Args:
            data_sources: 数据源字典 {"radiomics": DataFrame, "expression": DataFrame, ...}
            min_samples: 最小样本数 (关联分析默认 3, 预测模型默认 10)
            scenario: 场景类型 ("correlation" | "prediction" | "visualization" | "full")

        Returns:
            GateResult: 判定结果 (PASS / CONDITIONAL / BLOCKED)
        """
        check_results: List[CheckItemResult] = []

        # 项1: [🔑] 样本对齐
        check_results.append(
            self._check_sample_alignment(data_sources, min_samples)
        )

        # 项2: [🔑] 模态完整性
        check_results.append(
            self._check_modality_completeness(data_sources, scenario)
        )

        # 项3: [ ] 数据类型匹配
        check_results.append(
            self._check_data_type_match(data_sources, scenario)
        )

        return self._build_gate_result(
            gate_type=GateType.DATA_QUALITY,
            check_results=check_results,
            total_items=3,
        )

    def _check_sample_alignment(
        self,
        data_sources: Dict[str, Any],
        min_samples: int,
    ) -> CheckItemResult:
        """[🔑] 项1: 样本对齐 — 各模态数据样本 ID 交集 ≥ 最小样本数

        Args:
            data_sources: 数据源字典
            min_samples: 最小样本数

        Returns:
            CheckItemResult
        """
        try:
            if not data_sources:
                return CheckItemResult(
                    item_id="CD-DG-01",
                    name="样本对齐 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence="未提供任何数据源",
                    notes="必须提供至少一个数据源",
                )

            # 收集各数据源的样本 ID 集合
            sample_sets: Dict[str, set] = {}
            for name, data in data_sources.items():
                if isinstance(data, pd.DataFrame):
                    sample_sets[name] = set(data.index)
                elif isinstance(data, np.ndarray):
                    sample_sets[name] = set(range(data.shape[0]))
                elif isinstance(data, dict):
                    # Dict 类型 (如 realtime data) — 用 key 作为样本标识
                    sample_sets[name] = set(data.keys()) if data else set()
                elif isinstance(data, (list, tuple)):
                    sample_sets[name] = set(range(len(data)))
                else:
                    sample_sets[name] = set()

            if not sample_sets:
                return CheckItemResult(
                    item_id="CD-DG-01",
                    name="样本对齐 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence="无法从数据源中提取样本 ID",
                    notes="数据源类型不被支持",
                )

            # 计算所有数据源的交集
            common = None
            for name, s in sample_sets.items():
                if common is None:
                    common = s.copy()
                else:
                    common = common & s

            n_common = len(common) if common else 0
            n_sources = len(sample_sets)
            set_sizes = {name: len(s) for name, s in sample_sets.items()}

            if n_common >= min_samples:
                return CheckItemResult(
                    item_id="CD-DG-01",
                    name="样本对齐 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=(
                        f"交集样本数 {n_common} ≥ {min_samples} (阈值)，"
                        f"数据源数 {n_sources}，各源样本数: {set_sizes}"
                    ),
                )
            else:
                return CheckItemResult(
                    item_id="CD-DG-01",
                    name="样本对齐 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=(
                        f"交集样本数 {n_common} < {min_samples} (阈值)，"
                        f"各源样本数: {set_sizes}"
                    ),
                    notes=(
                        f"样本交集不足，需要至少 {min_samples} 个公共样本，"
                        f"当前仅有 {n_common} 个"
                    ),
                )

        except Exception as e:
            return CheckItemResult(
                item_id="CD-DG-01",
                name="样本对齐 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_modality_completeness(
        self,
        data_sources: Dict[str, Any],
        scenario: str,
    ) -> CheckItemResult:
        """[🔑] 项2: 模态完整性 — 所选场景所需模态数据全部提供

        Args:
            data_sources: 数据源字典
            scenario: 场景类型

        Returns:
            CheckItemResult
        """
        try:
            provided = set(data_sources.keys())
            required = SCENARIO_REQUIRED_MODALITIES.get(scenario, [])

            if scenario == "visualization":
                # 可视化场景只需 ≥ 1 个模态
                if len(provided) >= 1:
                    return CheckItemResult(
                        item_id="CD-DG-02",
                        name="模态完整性 [🔑]",
                        is_key=True,
                        status="PASS",
                        evidence=f"场景 '{scenario}' 需 ≥ 1 模态，已提供 {len(provided)} 个: {sorted(provided)}",
                    )
                else:
                    return CheckItemResult(
                        item_id="CD-DG-02",
                        name="模态完整性 [🔑]",
                        is_key=True,
                        status="FAIL",
                        evidence=f"场景 '{scenario}' 需 ≥ 1 模态，未提供任何数据源",
                        notes="请至少提供一个模态的数据",
                    )

            missing = [m for m in required if m not in provided]

            if not missing:
                return CheckItemResult(
                    item_id="CD-DG-02",
                    name="模态完整性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=(
                        f"场景 '{scenario}' 所需模态 {required} 全部提供，"
                        f"已提供: {sorted(provided)}"
                    ),
                )
            else:
                return CheckItemResult(
                    item_id="CD-DG-02",
                    name="模态完整性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=(
                        f"场景 '{scenario}' 缺少模态: {missing}，"
                        f"已提供: {sorted(provided)}"
                    ),
                    notes=f"请补充缺失模态: {', '.join(missing)}",
                )

        except Exception as e:
            return CheckItemResult(
                item_id="CD-DG-02",
                name="模态完整性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_data_type_match(
        self,
        data_sources: Dict[str, Any],
        scenario: str,
    ) -> CheckItemResult:
        """[ ] 项3: 数据类型匹配 — 维度和 dtype 符合预期

        检查各模态数据的类型和基本维度是否符合预期。
        - radiomics: DataFrame (sample × feature), 数值类型
        - expression: DataFrame (sample × gene), 数值类型
        - realtime: DataFrame 或 Dict[str, List]
        - clinical: DataFrame (sample × variables)
        - labels: ndarray 或 pd.Series

        Args:
            data_sources: 数据源字典
            scenario: 场景类型

        Returns:
            CheckItemResult
        """
        try:
            issues: List[str] = []
            type_info: List[str] = []

            for name, data in data_sources.items():
                if name == "radiomics" or name == "expression" or name == "clinical":
                    if not isinstance(data, pd.DataFrame):
                        issues.append(f"{name}: 期望 DataFrame，实际 {type(data).__name__}")
                    else:
                        shape = data.shape
                        type_info.append(f"{name}: DataFrame {shape}")
                        # 检查数值列
                        numeric_cols = data.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) == 0 and shape[1] > 0:
                            issues.append(f"{name}: 无数值列")
                elif name == "realtime":
                    if isinstance(data, pd.DataFrame):
                        type_info.append(f"{name}: DataFrame {data.shape}")
                    elif isinstance(data, dict):
                        n_metrics = len(data)
                        type_info.append(f"{name}: Dict ({n_metrics} metrics)")
                    else:
                        issues.append(f"{name}: 期望 DataFrame 或 Dict，实际 {type(data).__name__}")
                elif name == "labels":
                    if isinstance(data, (np.ndarray, pd.Series)):
                        n = len(data)
                        type_info.append(f"{name}: {type(data).__name__} (n={n})")
                    else:
                        issues.append(f"{name}: 期望 ndarray 或 Series，实际 {type(data).__name__}")
                else:
                    type_info.append(f"{name}: {type(data).__name__}")

            if not issues:
                return CheckItemResult(
                    item_id="CD-DG-03",
                    name="数据类型匹配",
                    is_key=False,
                    status="PASS",
                    evidence="；".join(type_info),
                )
            else:
                return CheckItemResult(
                    item_id="CD-DG-03",
                    name="数据类型匹配",
                    is_key=False,
                    status="FAIL",
                    evidence="；".join(type_info),
                    notes="；".join(issues),
                )

        except Exception as e:
            return CheckItemResult(
                item_id="CD-DG-03",
                name="数据类型匹配",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    # ===== Gate CD-3.5: 融合结果门闸 (3 项) =====

    def run_gate_cd35(
        self,
        correlation_results: Optional[Dict] = None,
        model_metrics: Optional[Dict] = None,
        visualization_data: Optional[Dict] = None,
    ) -> GateResult:
        """执行 Gate CD-3.5 全部 3 项检查

        Args:
            correlation_results: 关联分析结果 (含 correlations DataFrame, n_significant)
            model_metrics: 模型评估指标 (含 accuracy, auroc, precision, recall, f1)
            visualization_data: 可视化数据 (含 matrix_shape, curve_points 等)

        Returns:
            GateResult: 判定结果 (PASS / CONDITIONAL / BLOCKED)
        """
        check_results: List[CheckItemResult] = []

        # 项1: [🔑] 关联显著性
        check_results.append(
            self._check_correlation_significance(correlation_results, model_metrics)
        )

        # 项2: [🔑] 模型性能
        check_results.append(
            self._check_model_performance(model_metrics)
        )

        # 项3: [ ] 可视化一致性
        check_results.append(
            self._check_visualization_consistency(visualization_data)
        )

        return self._build_gate_result(
            gate_type=GateType.RESULTS_QUALITY,
            check_results=check_results,
            total_items=3,
        )

    def _check_correlation_significance(
        self,
        correlation_results: Optional[Dict] = None,
        model_metrics: Optional[Dict] = None,
    ) -> CheckItemResult:
        """[🔑] 项1: 关联显著性 — FDR 校正后至少 1 对显著 (p_adj < 0.05 & |r| ≥ 0.3)
        或预测模型 AUROC > 0.5

        如果提供了 correlation_results，检查关联显著性；
        如果提供了 model_metrics，检查 AUROC > 0.5；
        如果两者均提供，任一通过即可；
        如果两者均未提供，标记为 N/A。

        Args:
            correlation_results: 关联分析结果
            model_metrics: 模型评估指标

        Returns:
            CheckItemResult
        """
        try:
            has_corr = correlation_results is not None
            has_model = model_metrics is not None

            if not has_corr and not has_model:
                return CheckItemResult(
                    item_id="CD-RG-01",
                    name="关联显著性 [🔑]",
                    is_key=True,
                    status="N/A",
                    evidence="未提供关联分析结果或模型指标",
                    notes="至少需要提供 correlation_results 或 model_metrics 之一",
                )

            corr_pass = False
            corr_evidence = ""

            # 检查关联显著性
            if has_corr:
                n_significant = correlation_results.get("n_significant", 0)
                n_total = correlation_results.get("n_total", 0)
                corr_evidence = f"关联分析: {n_significant}/{n_total} 对显著 (p_adj<0.05 & |r|≥0.3)"

                if n_significant > 0:
                    corr_pass = True
                else:
                    # 检查 correlations DataFrame 中的 significant 列
                    corr_df = correlation_results.get("correlations")
                    if isinstance(corr_df, pd.DataFrame) and "significant" in corr_df.columns:
                        n_sig = int(corr_df["significant"].sum())
                        if n_sig > 0:
                            corr_pass = True
                            corr_evidence = f"关联分析 (DataFrame): {n_sig} 对显著"

            # 检查模型 AUROC
            model_pass = False
            model_evidence = ""

            if has_model:
                auroc = model_metrics.get("auroc")
                if auroc is not None:
                    auroc_val = float(auroc)
                    model_evidence = f"模型 AUROC={auroc_val:.4f}"
                    if auroc_val > 0.5:
                        model_pass = True

            # 汇总判定
            evidence_parts = [p for p in [corr_evidence, model_evidence] if p]
            evidence = "；".join(evidence_parts) if evidence_parts else "无可用指标"

            if corr_pass or model_pass:
                return CheckItemResult(
                    item_id="CD-RG-01",
                    name="关联显著性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=evidence,
                )
            else:
                fail_notes = []
                if has_corr and not corr_pass:
                    fail_notes.append("FDR 校正后无显著关联 (p_adj<0.05 & |r|≥0.3)")
                if has_model and not model_pass:
                    fail_notes.append("AUROC ≤ 0.5，模型不优于随机")
                return CheckItemResult(
                    item_id="CD-RG-01",
                    name="关联显著性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=evidence,
                    notes="；".join(fail_notes) if fail_notes else "无显著结果",
                )

        except Exception as e:
            return CheckItemResult(
                item_id="CD-RG-01",
                name="关联显著性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_model_performance(self, model_metrics: Optional[Dict]) -> CheckItemResult:
        """[🔑] 项2: 模型性能 — 准确率 ≥ 0.5; AUROC ≥ 0.55; 无 NaN 指标

        如果未提供 model_metrics，标记为 N/A。

        Args:
            model_metrics: 模型评估指标

        Returns:
            CheckItemResult
        """
        try:
            if model_metrics is None:
                return CheckItemResult(
                    item_id="CD-RG-02",
                    name="模型性能 [🔑]",
                    is_key=True,
                    status="N/A",
                    evidence="未提供模型评估指标",
                    notes="关联分析场景无模型指标，此项自动跳过",
                )

            # 检查必需指标
            required_metrics = ["accuracy", "auroc"]
            available_metrics = []
            missing_metrics = []
            for m in required_metrics:
                if m in model_metrics:
                    available_metrics.append(m)
                else:
                    missing_metrics.append(m)

            if missing_metrics:
                return CheckItemResult(
                    item_id="CD-RG-02",
                    name="模型性能 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"缺少必需指标: {missing_metrics}",
                    notes=f"可用指标: {list(model_metrics.keys())}",
                )

            # 检查 NaN
            nan_metrics = []
            for key, val in model_metrics.items():
                if isinstance(val, float) and np.isnan(val):
                    nan_metrics.append(key)

            if nan_metrics:
                return CheckItemResult(
                    item_id="CD-RG-02",
                    name="模型性能 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"存在 NaN 指标: {nan_metrics}",
                    notes="模型指标包含 NaN 值，请检查数据或模型训练",
                )

            # 检查阈值
            accuracy = float(model_metrics.get("accuracy", 0.0))
            auroc = float(model_metrics.get("auroc", 0.0))

            issues = []
            if accuracy < 0.5:
                issues.append(f"准确率 {accuracy:.4f} < 0.5")
            if auroc < 0.55:
                issues.append(f"AUROC {auroc:.4f} < 0.55")

            # 附加指标
            extra_info = []
            for key in ["precision", "recall", "f1"]:
                if key in model_metrics:
                    extra_info.append(f"{key}={float(model_metrics[key]):.4f}")

            evidence = (
                f"accuracy={accuracy:.4f}, auroc={auroc:.4f}"
                + (f", {', '.join(extra_info)}" if extra_info else "")
            )

            if not issues:
                return CheckItemResult(
                    item_id="CD-RG-02",
                    name="模型性能 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=evidence,
                )
            else:
                return CheckItemResult(
                    item_id="CD-RG-02",
                    name="模型性能 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=evidence,
                    notes="；".join(issues),
                )

        except Exception as e:
            return CheckItemResult(
                item_id="CD-RG-02",
                name="模型性能 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_visualization_consistency(
        self, visualization_data: Optional[Dict]
    ) -> CheckItemResult:
        """[ ] 项3: 可视化一致性 — 热图矩阵维度、曲线点数与输入数据匹配

        检查 visualization_data 中的 matrix_shape、curve_points 等维度信息
        是否与预期的输入数据维度一致。

        如果未提供 visualization_data，标记为 N/A。

        Args:
            visualization_data: 可视化数据

        Returns:
            CheckItemResult
        """
        try:
            if visualization_data is None:
                return CheckItemResult(
                    item_id="CD-RG-03",
                    name="可视化一致性",
                    is_key=False,
                    status="N/A",
                    evidence="未提供可视化数据",
                    notes="如已生成可视化，建议提供 visualization_data 以执行一致性检查",
                )

            issues: List[str] = []
            info_parts: List[str] = []

            # 检查热图矩阵维度
            matrix_shape = visualization_data.get("matrix_shape")
            if matrix_shape is not None:
                if isinstance(matrix_shape, (list, tuple)):
                    n_dims = len(matrix_shape)
                    if n_dims != 2:
                        issues.append(f"热图矩阵维度数 {n_dims} ≠ 2")
                    else:
                        rows, cols = matrix_shape
                        if rows <= 0 or cols <= 0:
                            issues.append(f"热图矩阵维度无效: {matrix_shape}")
                        else:
                            info_parts.append(f"热图矩阵 {rows}×{cols}")
                else:
                    issues.append(f"热图矩阵维度格式异常: {type(matrix_shape).__name__}")

            # 检查曲线点数
            curve_points = visualization_data.get("curve_points")
            if curve_points is not None:
                if isinstance(curve_points, int):
                    if curve_points <= 0:
                        issues.append(f"曲线点数 {curve_points} ≤ 0")
                    else:
                        info_parts.append(f"曲线点数 {curve_points}")
                elif isinstance(curve_points, dict):
                    for metric, n in curve_points.items():
                        if isinstance(n, int) and n <= 0:
                            issues.append(f"曲线 '{metric}' 点数 {n} ≤ 0")
                        else:
                            info_parts.append(f"{metric}: {n} 点")

            # 检查文件路径
            viz_paths = visualization_data.get("paths", [])
            if viz_paths:
                from pathlib import Path
                existing = sum(1 for p in viz_paths if Path(p).exists())
                missing = len(viz_paths) - existing
                info_parts.append(f"可视化文件 {existing}/{len(viz_paths)} 存在")
                if missing > 0:
                    issues.append(f"{missing} 个可视化文件缺失")

            if not issues:
                evidence = "；".join(info_parts) if info_parts else "可视化数据格式检查通过"
                return CheckItemResult(
                    item_id="CD-RG-03",
                    name="可视化一致性",
                    is_key=False,
                    status="PASS",
                    evidence=evidence,
                )
            else:
                return CheckItemResult(
                    item_id="CD-RG-03",
                    name="可视化一致性",
                    is_key=False,
                    status="FAIL",
                    evidence="；".join(info_parts) if info_parts else "检查完成",
                    notes="；".join(issues),
                )

        except Exception as e:
            return CheckItemResult(
                item_id="CD-RG-03",
                name="可视化一致性",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    # ===== 辅助方法 =====

    def _build_gate_result(
        self,
        gate_type: GateType,
        check_results: List[CheckItemResult],
        total_items: int,
    ) -> GateResult:
        """构建 GateResult

        使用与 BioQualityGateChecker / ImagingQualityGateChecker 相同的判定逻辑，
        适配 cross_domain 门闸的自定义检查项。

        判定规则:
        - failed == 0 → PASS
        - key_failed > 0 → BLOCKED
        - failed <= 2 (非关键) → CONDITIONAL
        - failed > 2 → BLOCKED

        Args:
            gate_type: 门闸类型
            check_results: 检查结果列表
            total_items: 总检查项数

        Returns:
            GateResult
        """
        # 统计结果 (排除 N/A 和 SKIP)
        evaluable = [cr for cr in check_results if cr.status not in ("N/A", "SKIP")]
        passed = sum(1 for cr in evaluable if cr.status == "PASS")
        failed = sum(1 for cr in evaluable if cr.status == "FAIL")
        key_failed = [cr for cr in evaluable if cr.is_key and cr.status == "FAIL"]

        # 判定逻辑
        if failed == 0:
            verdict = GateVerdict.PASS
            key_status = "all_pass"
        elif len(key_failed) > 0:
            verdict = GateVerdict.BLOCKED
            key_status = f"item_{key_failed[0].item_id}_failed"
        elif failed <= 2:
            verdict = GateVerdict.CONDITIONAL
            key_status = "all_pass"
        else:
            verdict = GateVerdict.BLOCKED
            key_status = f"{failed}_items_failed"

        # 风险评估
        risks: List[str] = []
        for cr in check_results:
            if cr.status == "FAIL":
                level = "关键" if cr.is_key else "一般"
                risks.append(f"[{level}] {cr.name}: {cr.notes or cr.evidence}")

        return GateResult(
            gate_type=gate_type,
            study_id=self.study_id,
            verdict=verdict,
            total_items=total_items,
            passed_items=passed,
            failed_items=failed,
            key_items_status=key_status,
            check_results=check_results,
            risks=risks,
        )
