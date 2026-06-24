"""
Tests for shared.quality_gates — 质量门闸独立模块

覆盖：
- GateRunner 初始化和门闸定义
- generate_checklist (Skill模式)
- build_agent_task (Agent模式)
- run_gate 判定逻辑 (PASS/CONDITIONAL/BLOCKED)
- CheckItemCollection 结构化检查项
- 门闸报告序列化/反序列化
"""

import json
import pytest
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.quality_gates import (
    GateRunner,
    GateResult,
    GateType,
    GateVerdict,
    RunMode,
    CheckItemResult,
    CheckItem,
    CheckItemCollection,
    DataQualityCheckItems,
    SapQualityCheckItems,
    ResultsQualityCheckItems,
)


# ============================================================
# CheckItemCollection Tests
# ============================================================


class TestCheckItemCollections:
    """检查项集合测试"""

    def test_data_quality_items_count(self):
        assert len(DataQualityCheckItems.items) == 9

    def test_sap_quality_items_count(self):
        assert SapQualityCheckItems.gate_stage == "2.5"
        assert len(SapQualityCheckItems.items) == 8

    def test_results_quality_items_count(self):
        assert len(ResultsQualityCheckItems.items) == 9

    def test_key_items_identified(self):
        key_items = DataQualityCheckItems.get_key_items()
        key_numbers = [item.item_number for item in key_items]
        assert 5 in key_numbers
        assert 6 in key_numbers
        assert 7 in key_numbers
        assert 9 in key_numbers

    def test_get_item_by_number(self):
        item = DataQualityCheckItems.get_item_by_number(1)
        assert item is not None
        assert item.item_id == "DG-01"
        assert item.name == "清洗日志完整性"

    def test_get_item_by_number_not_found(self):
        item = DataQualityCheckItems.get_item_by_number(99)
        assert item is None

    def test_check_item_fields(self):
        item = DataQualityCheckItems.items[0]
        assert isinstance(item, CheckItem)
        assert item.item_number == 1
        assert item.is_key is False
        assert item.evidence_type in ("file", "metric", "log", "manual")

    def test_key_items_have_correct_flags(self):
        for item in DataQualityCheckItems.items:
            if item.item_number in (5, 6, 7, 9):
                assert item.is_key is True
            else:
                assert item.is_key is False


# ============================================================
# GateRunner Tests
# ============================================================


class TestGateRunner:
    """GateRunner 核心测试"""

    def setup_method(self):
        self.runner = GateRunner(study_id="MSRA-2026-TEST")

    def test_init(self):
        assert self.runner.study_id == "MSRA-2026-TEST"

    def test_get_gate_definition_all_types(self):
        for gate_type in GateType:
            defn = self.runner.get_gate_definition(gate_type)
            assert defn.gate_type == gate_type
            assert defn.total_items > 0
            assert len(defn.key_items) > 0

    def test_get_gate_definition_invalid(self):
        with pytest.raises(ValueError, match="Unknown gate type"):
            self.runner.get_gate_definition("invalid")


class TestGateRunnerChecklist:
    """generate_checklist 测试"""

    def setup_method(self):
        self.runner = GateRunner(study_id="MSRA-2026-TEST")

    def test_checklist_contains_study_id(self):
        prompt = self.runner.generate_checklist(
            GateType.DATA_QUALITY,
            artifacts={"data": "test.csv"},
        )
        assert "MSRA-2026-TEST" in prompt

    def test_checklist_contains_gate_name(self):
        prompt = self.runner.generate_checklist(
            GateType.SAP_QUALITY,
            artifacts={"sap": "sap.md"},
        )
        assert "SAP" in prompt

    def test_checklist_contains_artifacts(self):
        prompt = self.runner.generate_checklist(
            GateType.DATA_QUALITY,
            artifacts={"cleaned_data": "/path/data.csv", "log": "/path/log.md"},
        )
        assert "/path/data.csv" in prompt
        assert "/path/log.md" in prompt

    def test_checklist_contains_verdict_rules(self):
        prompt = self.runner.generate_checklist(
            GateType.RESULTS_QUALITY,
            artifacts={"results": "results.csv"},
        )
        assert "PASS" in prompt
        assert "CONDITIONAL" in prompt
        assert "BLOCKED" in prompt


class TestGateRunnerAgentTask:
    """build_agent_task 测试"""

    def setup_method(self):
        self.runner = GateRunner(study_id="MSRA-2026-TEST")

    def test_build_agent_task_returns_dict(self):
        result = self.runner.build_agent_task(
            GateType.DATA_QUALITY,
            artifacts={"data": "test.csv"},
            output_path="/tmp/report.md",
        )
        assert "task" in result
        assert "prompt" in result

    def test_agent_task_has_correct_type(self):
        result = self.runner.build_agent_task(
            GateType.SAP_QUALITY,
            artifacts={"sap": "sap.md"},
            output_path="/tmp/report.md",
        )
        assert result["task"].agent_type.value == "qc_inspector"

    def test_agent_task_runs_in_background(self):
        result = self.runner.build_agent_task(
            GateType.RESULTS_QUALITY,
            artifacts={"results": "results.csv"},
            output_path="/tmp/report.md",
        )
        assert result["task"].run_in_background is True

    def test_agent_task_prompt_contains_gate_info(self):
        result = self.runner.build_agent_task(
            GateType.DATA_QUALITY,
            artifacts={"data": "test.csv"},
            output_path="/tmp/report.md",
        )
        prompt = result["prompt"]
        assert "MSRA-2026-TEST" in prompt
        assert "Data Quality" in prompt or "数据质量" in prompt


# ============================================================
# Gate Verdict Logic Tests
# ============================================================


class TestGateVerdictLogic:
    """门闸判定逻辑测试"""

    def setup_method(self):
        self.runner = GateRunner(study_id="MSRA-2026-TEST")

    def _make_results(self, statuses, key_statuses=None):
        """构造检查结果列表"""
        if key_statuses is None:
            key_statuses = {}
        results = []
        for i, status in enumerate(statuses):
            is_key = (i + 1) in key_statuses
            results.append(
                CheckItemResult(
                    item_id=f"CHECK-{i+1:02d}",
                    name=f"Check {i+1}",
                    is_key=is_key,
                    status=status,
                )
            )
        return results

    def test_all_pass(self):
        results = self._make_results(["PASS"] * 9)
        gate = self.runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )
        assert gate.verdict == GateVerdict.PASS
        assert gate.passed_items == 9
        assert gate.failed_items == 0
        assert gate.pass_rate == 1.0

    def test_one_non_key_fail_is_conditional(self):
        statuses = ["PASS"] * 8 + ["FAIL"]
        results = self._make_results(statuses)
        gate = self.runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )
        assert gate.verdict == GateVerdict.CONDITIONAL

    def test_two_non_key_fails_is_conditional(self):
        statuses = ["PASS"] * 7 + ["FAIL", "FAIL"]
        results = self._make_results(statuses)
        gate = self.runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )
        assert gate.verdict == GateVerdict.CONDITIONAL

    def test_three_fails_is_blocked(self):
        statuses = ["PASS"] * 6 + ["FAIL", "FAIL", "FAIL"]
        results = self._make_results(statuses)
        gate = self.runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )
        assert gate.verdict == GateVerdict.BLOCKED

    def test_key_item_fail_is_blocked(self):
        statuses = ["PASS"] * 9
        # Item 5 is key
        statuses[4] = "FAIL"
        results = self._make_results(statuses, key_statuses={5: True})
        gate = self.runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )
        assert gate.verdict == GateVerdict.BLOCKED
        assert "CHECK-05" in gate.key_items_status

    def test_key_item_pass_with_one_non_key_fail(self):
        statuses = ["PASS"] * 9
        # Item 9 is the last one, non-key FAIL
        statuses[8] = "FAIL"
        # Mark items 5,6,7 as key (all PASS), item 9 is NOT key
        results = self._make_results(statuses, key_statuses={5: True, 6: True, 7: True})
        gate = self.runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )
        assert gate.verdict == GateVerdict.CONDITIONAL

    def test_risks_populated_on_fail(self):
        statuses = ["PASS"] * 8 + ["FAIL"]
        results = self._make_results(statuses)
        results[8].notes = "Test failure note"
        gate = self.runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )
        assert len(gate.risks) == 1
        assert "Test failure note" in gate.risks[0]

    def test_sap_gate_8_items(self):
        results = self._make_results(["PASS"] * 8)
        gate = self.runner.run_gate(
            GateType.SAP_QUALITY, {}, RunMode.SKILL, results
        )
        assert gate.total_items == 8
        assert gate.verdict == GateVerdict.PASS

    def test_results_gate_9_items(self):
        results = self._make_results(["PASS"] * 9)
        gate = self.runner.run_gate(
            GateType.RESULTS_QUALITY, {}, RunMode.SKILL, results
        )
        assert gate.total_items == 9
        assert gate.verdict == GateVerdict.PASS


# ============================================================
# GateResult Serialization Tests
# ============================================================


class TestGateResultSerialization:
    """门闸报告序列化测试"""

    def test_to_dict(self):
        runner = GateRunner(study_id="MSRA-2026-TEST")
        results = [
            CheckItemResult(
                item_id="DG-01", name="Test", is_key=False, status="PASS"
            )
        ] * 9
        gate = runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )
        d = gate.to_dict()
        assert d["gate_type"] == "data_quality"
        assert d["verdict"] == "PASS"
        assert d["total_items"] == 9
        assert d["passed_items"] == 9
        assert "100.0%" in d["pass_rate"]

    def test_save_and_load(self, tmp_path):
        runner = GateRunner(study_id="MSRA-2026-TEST")
        results = [
            CheckItemResult(
                item_id="DG-01", name="Test", is_key=False, status="PASS"
            )
        ] * 9
        gate = runner.run_gate(
            GateType.DATA_QUALITY, {}, RunMode.SKILL, results
        )

        # Save
        output = str(tmp_path / "gate_report.json")
        saved_path = runner.save_gate_report(gate, output)
        assert Path(saved_path).exists()

        # Load
        loaded = runner.load_gate_report(saved_path)
        assert loaded.verdict == GateVerdict.PASS
        assert loaded.study_id == "MSRA-2026-TEST"
        assert loaded.total_items == 9


# ============================================================
# RunMode Tests
# ============================================================


class TestRunMode:
    """运行模式测试"""

    def test_skill_mode_requires_check_results(self):
        runner = GateRunner(study_id="TEST")
        with pytest.raises(ValueError, match="check_results"):
            runner.run_gate(GateType.DATA_QUALITY, {}, RunMode.SKILL, None)

    def test_agent_mode_accepts_empty_results(self):
        runner = GateRunner(study_id="TEST")
        gate = runner.run_gate(GateType.DATA_QUALITY, {}, RunMode.AGENT, None)
        assert gate.total_items == 9
        assert gate.passed_items == 0
