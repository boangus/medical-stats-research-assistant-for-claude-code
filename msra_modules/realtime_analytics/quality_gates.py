"""
Realtime Analytics Quality Gates - 实时分析质量门闸

实现 Gate RT-1（实时数据质量）的 3 项检查。
复用 shared/quality_gates/ 框架的 GateRunner + CheckItemResult 模式。
"""

import time
import numpy as np
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# 导入共享门闸框架
import sys
from pathlib import Path

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


class RealtimeQualityGateChecker:
    """实时分析质量门闸检查器

    封装 Gate RT-1 的具体检查逻辑，
    产出 CheckItemResult 列表供 GateRunner 消费。

    Usage:
        checker = RealtimeQualityGateChecker(study_id="RT-2026-001")

        # Gate RT-1: 实时数据质量检查
        gate_result = checker.run_gate_rt1(
            source=simulator,
            timestamps=ts_list,
            detection_rate=0.05,
        )
    """

    def __init__(
        self,
        study_id: str,
        project_root: Optional[str] = None,
    ):
        """初始化实时分析质量门闸检查器

        Args:
            study_id: 研究编号
            project_root: 项目根目录 (可选)
        """
        self.study_id = study_id
        self._runner = GateRunner(
            study_id=study_id,
            project_root=project_root,
        )

    # ===== Gate RT-1: 实时数据质量门闸 =====

    def run_gate_rt1(
        self,
        source: Any = None,
        timestamps: Optional[List[float]] = None,
        detection_rate: Optional[float] = None,
        window_size: int = 60,
        max_gap_multiplier: float = 2.0,
        min_rate: float = 0.01,
        max_rate: float = 0.20,
    ) -> GateResult:
        """执行 Gate RT-1 全部 3 项检查

        Args:
            source: 数据源对象（模拟器或其他数据源），用于检查连接
            timestamps: 时间戳列表，用于检查连续性
            detection_rate: 异常检测率，用于校准检查
            window_size: 窗口大小（秒），默认 60
            max_gap_multiplier: 最大间隔倍数，默认 2.0（间隔 < window_size * multiplier）
            min_rate: 最小检测率，默认 0.01
            max_rate: 最大检测率，默认 0.20

        Returns:
            GateResult: 判定结果 (PASS / CONDITIONAL / BLOCKED)
        """
        check_results = []

        # 项1: [🔑] 数据流连接正常
        check_results.append(
            self.check_data_source_available(source)
        )

        # 项2: [🔑] 时间戳连续性
        if timestamps is not None:
            check_results.append(
                self.check_timestamp_continuity(
                    timestamps,
                    window_size=window_size,
                    max_gap_multiplier=max_gap_multiplier,
                )
            )
        else:
            check_results.append(CheckItemResult(
                item_id="RT-DQ-02",
                name="时间戳连续性 [🔑]",
                is_key=True,
                status="N/A",
                evidence="未提供 timestamps，跳过此项检查",
                notes="建议提供时间戳列表以验证连续性",
            ))

        # 项3: [ ] 异常检测灵敏度校准
        if detection_rate is not None:
            check_results.append(
                self.check_detection_sensitivity(
                    detection_rate,
                    min_rate=min_rate,
                    max_rate=max_rate,
                )
            )
        else:
            check_results.append(CheckItemResult(
                item_id="RT-DQ-03",
                name="异常检测灵敏度校准",
                is_key=False,
                status="N/A",
                evidence="未提供 detection_rate，跳过此项检查",
                notes="建议在 Phase 3 提供检测率以执行灵敏度校准",
            ))

        return self._build_gate_result(
            check_results=check_results,
            total_items=3,
        )

    def check_data_source_available(self, source: Any) -> CheckItemResult:
        """[🔑] 项1: 数据流连接正常

        检查数据源是否成功连接并可返回数据。
        对于模拟器，检查是否可生成样本；对于其他数据源，检查连接状态。

        Args:
            source: 数据源对象

        Returns:
            CheckItemResult
        """
        try:
            if source is None:
                return CheckItemResult(
                    item_id="RT-DQ-01",
                    name="数据流连接正常 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence="未提供数据源",
                    notes="必须提供有效的数据源（模拟器/Redis/Kafka/CSV）",
                )

            # 检查是否为模拟器
            if hasattr(source, "generate_sample"):
                # 尝试生成一个样本
                sample = source.generate_sample(timestamp=time.time())
                if sample is not None:
                    return CheckItemResult(
                        item_id="RT-DQ-01",
                        name="数据流连接正常 [🔑]",
                        is_key=True,
                        status="PASS",
                        evidence=f"模拟器成功生成样本: {sample.to_dict() if hasattr(sample, 'to_dict') else str(sample)}",
                    )
                else:
                    return CheckItemResult(
                        item_id="RT-DQ-01",
                        name="数据流连接正常 [🔑]",
                        is_key=True,
                        status="FAIL",
                        evidence="模拟器返回 None",
                        notes="模拟器无法生成数据，请检查配置",
                    )

            # 检查是否为 StreamProcessor（有数据即为可用）
            if hasattr(source, "get_all_metrics"):
                metrics = source.get_all_metrics()
                if metrics:
                    return CheckItemResult(
                        item_id="RT-DQ-01",
                        name="数据流连接正常 [🔑]",
                        is_key=True,
                        status="PASS",
                        evidence=f"流处理器已有 {len(metrics)} 个注册指标: {metrics}",
                    )
                else:
                    return CheckItemResult(
                        item_id="RT-DQ-01",
                        name="数据流连接正常 [🔑]",
                        is_key=True,
                        status="FAIL",
                        evidence="流处理器无注册指标",
                        notes="请先注册监控指标",
                    )

            # 通用连接检查
            if hasattr(source, "is_connected"):
                connected = source.is_connected()
                if connected:
                    return CheckItemResult(
                        item_id="RT-DQ-01",
                        name="数据流连接正常 [🔑]",
                        is_key=True,
                        status="PASS",
                        evidence="数据源连接正常",
                    )
                else:
                    return CheckItemResult(
                        item_id="RT-DQ-01",
                        name="数据流连接正常 [🔑]",
                        is_key=True,
                        status="FAIL",
                        evidence="数据源连接失败",
                        notes="请检查连接参数和网络状态",
                    )

            # 如果有 generate_stream 方法也算可用
            if hasattr(source, "generate_stream"):
                return CheckItemResult(
                    item_id="RT-DQ-01",
                    name="数据流连接正常 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence="数据源支持流式生成",
                )

            # 无法判断
            return CheckItemResult(
                item_id="RT-DQ-01",
                name="数据流连接正常 [🔑]",
                is_key=True,
                status="FAIL",
                evidence=f"数据源类型 {type(source).__name__} 无法识别",
                notes="支持的数据源: VitalSignsSimulator, StreamProcessor, 或有 is_connected 方法的对象",
            )

        except Exception as e:
            return CheckItemResult(
                item_id="RT-DQ-01",
                name="数据流连接正常 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def check_timestamp_continuity(
        self,
        timestamps: List[float],
        window_size: int = 60,
        max_gap_multiplier: float = 2.0,
    ) -> CheckItemResult:
        """[🔑] 项2: 时间戳连续性

        检查相邻数据点的时间戳间隔是否过大。
        通过标准: 间隔 < window_size * max_gap_multiplier。

        Args:
            timestamps: 时间戳列表（应已排序）
            window_size: 窗口大小（秒），默认 60
            max_gap_multiplier: 最大间隔倍数，默认 2.0

        Returns:
            CheckItemResult
        """
        try:
            if not timestamps or len(timestamps) < 2:
                return CheckItemResult(
                    item_id="RT-DQ-02",
                    name="时间戳连续性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"时间戳数量不足: {len(timestamps) if timestamps else 0}",
                    notes="至少需要 2 个时间戳才能检查连续性",
                )

            # 计算相邻间隔
            ts_array = np.array(timestamps, dtype=float)
            gaps = np.diff(ts_array)

            # 最大允许间隔
            max_allowed_gap = window_size * max_gap_multiplier

            # 检查过大间隔
            large_gaps = gaps[gaps > max_allowed_gap]
            n_large_gaps = len(large_gaps)

            # 检查负间隔（时间戳倒序）
            negative_gaps = gaps[gaps < 0]
            n_negative = len(negative_gaps)

            # 统计信息
            mean_gap = float(np.mean(gaps))
            std_gap = float(np.std(gaps))
            max_gap = float(np.max(gaps))
            min_gap = float(np.min(gaps))

            issues = []
            if n_negative > 0:
                issues.append(f"{n_negative} 个负间隔（时间戳可能未排序）")
            if n_large_gaps > 0:
                issues.append(
                    f"{n_large_gaps} 个过大间隔 (>{max_allowed_gap:.1f}s)，"
                    f"最大间隔 {max_gap:.1f}s"
                )

            if not issues:
                status = "PASS"
                notes = ""
            else:
                status = "FAIL"
                notes = "；".join(issues)

            return CheckItemResult(
                item_id="RT-DQ-02",
                name="时间戳连续性 [🔑]",
                is_key=True,
                status=status,
                evidence=(
                    f"数据点数 {len(timestamps)}, "
                    f"间隔: mean={mean_gap:.2f}s, std={std_gap:.2f}s, "
                    f"max={max_gap:.2f}s, min={min_gap:.2f}s, "
                    f"最大允许={max_allowed_gap:.1f}s"
                ),
                notes=notes,
            )

        except Exception as e:
            return CheckItemResult(
                item_id="RT-DQ-02",
                name="时间戳连续性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def check_detection_sensitivity(
        self,
        detection_rate: float,
        min_rate: float = 0.01,
        max_rate: float = 0.20,
    ) -> CheckItemResult:
        """[ ] 项3: 异常检测灵敏度校准

        检查异常检测率是否在合理范围内。
        太低可能漏检，太高可能误报过多。

        Args:
            detection_rate: 实际检测到的异常比例 (0.0-1.0)
            min_rate: 最小可接受检测率，默认 0.01
            max_rate: 最大可接受检测率，默认 0.20

        Returns:
            CheckItemResult
        """
        try:
            if not (0.0 <= detection_rate <= 1.0):
                return CheckItemResult(
                    item_id="RT-DQ-03",
                    name="异常检测灵敏度校准",
                    is_key=False,
                    status="FAIL",
                    evidence=f"检测率超出有效范围: {detection_rate}",
                    notes="检测率应在 [0.0, 1.0] 范围内",
                )

            if min_rate <= detection_rate <= max_rate:
                status = "PASS"
                notes = ""
            elif detection_rate < min_rate:
                status = "FAIL"
                notes = (
                    f"检测率 {detection_rate:.4f} 低于最小阈值 {min_rate:.4f}，"
                    f"可能存在漏检。建议降低检测阈值或增加检测方法。"
                )
            else:
                status = "FAIL"
                notes = (
                    f"检测率 {detection_rate:.4f} 超过最大阈值 {max_rate:.4f}，"
                    f"可能存在误报过多。建议提高检测阈值或调整规则。"
                )

            return CheckItemResult(
                item_id="RT-DQ-03",
                name="异常检测灵敏度校准",
                is_key=False,
                status=status,
                evidence=(
                    f"检测率 {detection_rate:.4f} ({detection_rate:.2%}), "
                    f"可接受范围 [{min_rate:.4f}, {max_rate:.4f}]"
                ),
                notes=notes,
            )

        except Exception as e:
            return CheckItemResult(
                item_id="RT-DQ-03",
                name="异常检测灵敏度校准",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    # ===== 辅助方法 =====

    def _build_gate_result(
        self,
        check_results: List[CheckItemResult],
        total_items: int,
    ) -> GateResult:
        """构建 GateResult

        使用 GateRunner 的判定逻辑，但适配 RT 门闸的自定义检查项。

        Args:
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
        risks = []
        for cr in check_results:
            if cr.status == "FAIL":
                level = "关键" if cr.is_key else "一般"
                risks.append(f"[{level}] {cr.name}: {cr.notes or cr.evidence}")

        return GateResult(
            gate_type=GateType.DATA_QUALITY,
            study_id=self.study_id,
            verdict=verdict,
            total_items=total_items,
            passed_items=passed,
            failed_items=failed,
            key_items_status=key_status,
            check_results=check_results,
            risks=risks,
        )
