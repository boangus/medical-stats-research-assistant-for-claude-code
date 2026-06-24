"""
test_passport.py — passport.py 单元测试
"""
import os

import pytest

from shared.passport.passport import (
    OPTIONAL_ARTIFACTS,
    SAP_AMENDMENT_MAX,
    STAGE_ORDER,
    STAGE_PREREQUISITES,
    PassportError,
    PassportManager,
)


@pytest.fixture
def pm(tmp_dir):
    """创建临时 PassportManager"""
    path = os.path.join(tmp_dir, "passport.json")
    return PassportManager(path)


class TestPassportCreation:
    """护照创建测试"""

    def test_creates_default(self, pm):
        assert pm.data is not None
        assert "passport_id" in pm.data
        assert pm.data["passport_schema_version"] == "1"

    def test_default_has_no_artifacts(self, pm):
        assert pm.data["artifacts"] == []

    def test_default_status(self, pm):
        assert pm.data["status"] == "in_progress"

    def test_persistence(self, tmp_dir):
        path = os.path.join(tmp_dir, "passport.json")
        pm1 = PassportManager(path)
        pm1.add_artifact({"id": "test", "stage": "stage_1", "name": "Test"})

        pm2 = PassportManager(path)
        assert len(pm2.data["artifacts"]) == 1
        assert pm2.data["artifacts"][0]["id"] == "test"


class TestArtifactCRUD:
    """产物 CRUD 测试"""

    def test_add_artifact(self, pm):
        pm.add_artifact({
            "id": "cleaned_data",
            "stage": "stage_1",
            "name": "Cleaned Dataset",
        })
        assert pm.get_artifact("cleaned_data") is not None

    def test_add_duplicate_raises(self, pm):
        pm.add_artifact({"id": "test", "stage": "stage_1", "name": "Test"})
        with pytest.raises(PassportError, match="已存在"):
            pm.add_artifact({"id": "test", "stage": "stage_1", "name": "Test2"})

    def test_get_nonexistent(self, pm):
        assert pm.get_artifact("nonexistent") is None

    def test_update_status(self, pm):
        pm.add_artifact({"id": "data", "stage": "stage_1", "name": "Data"})
        pm.update_status("data", "completed", file_hash="sha256:abc")
        a = pm.get_artifact("data")
        assert a["status"] == "completed"
        assert a["hash"] == "sha256:abc"

    def test_update_invalid_status(self, pm):
        pm.add_artifact({"id": "data", "stage": "stage_1", "name": "Data"})
        with pytest.raises(PassportError, match="无效状态"):
            pm.update_status("data", "invalid_status")

    def test_update_nonexistent_raises(self, pm):
        with pytest.raises(PassportError, match="不存在"):
            pm.update_status("nonexistent", "completed")

    def test_mark_consumed(self, pm):
        pm.add_artifact({"id": "data", "stage": "stage_1", "name": "Data"})
        pm.mark_consumed("data", "analysis_exec")
        a = pm.get_artifact("data")
        assert a["status"] == "consumed"
        assert "analysis_exec" in a["consumed_by"]

    def test_mark_consumed_no_duplicate(self, pm):
        pm.add_artifact({"id": "data", "stage": "stage_1", "name": "Data"})
        pm.mark_consumed("data", "exec")
        pm.mark_consumed("data", "exec")
        a = pm.get_artifact("data")
        assert a["consumed_by"].count("exec") == 1


class TestStageQueries:
    """阶段查询测试"""

    def test_get_stage_artifacts(self, pm):
        pm.add_artifact({"id": "a1", "stage": "stage_1", "name": "A1"})
        pm.add_artifact({"id": "a2", "stage": "stage_1", "name": "A2"})
        pm.add_artifact({"id": "a3", "stage": "stage_2", "name": "A3"})

        s1 = pm.get_stage_artifacts("stage_1")
        assert len(s1) == 2

        s2 = pm.get_stage_artifacts("stage_2")
        assert len(s2) == 1

    def test_get_stage_status_empty(self, pm):
        assert pm.get_stage_status("stage_1") == "planned"

    def test_get_stage_status_completed(self, pm):
        pm.add_artifact({"id": "a1", "stage": "stage_1", "name": "A1"})
        pm.update_status("a1", "completed")
        assert pm.get_stage_status("stage_1") == "completed"

    def test_get_stage_status_in_progress(self, pm):
        pm.add_artifact({"id": "a1", "stage": "stage_1", "name": "A1"})
        pm.update_status("a1", "in_progress")
        assert pm.get_stage_status("stage_1") == "in_progress"

    def test_get_stage_status_error(self, pm):
        pm.add_artifact({"id": "a1", "stage": "stage_1", "name": "A1"})
        pm.update_status("a1", "error")
        assert pm.get_stage_status("stage_1") == "error"


class TestStageConstants:
    """阶段常量测试"""

    def test_stage_order(self):
        assert "stage_1" in STAGE_ORDER
        assert "stage_4" in STAGE_ORDER
        assert "stage_5_0_intake" in STAGE_ORDER
        assert "stage_5_paper" in STAGE_ORDER
        assert "stage_3.7" in STAGE_ORDER  # 🆕 Sprint A
        assert len(STAGE_ORDER) == 10  # 🆕 Sprint A: 增加 stage_3.7

    def test_stage_order_sequence(self):
        """🆕 Sprint A: stage_3.7 位于 stage_3.5 和 stage_4 之间"""
        idx_35 = STAGE_ORDER.index("stage_3.5")
        idx_37 = STAGE_ORDER.index("stage_3.7")
        idx_4 = STAGE_ORDER.index("stage_4")
        assert idx_35 < idx_37 < idx_4

    def test_prerequisites(self):
        assert STAGE_PREREQUISITES["stage_1"] == []
        assert "cleaned_data" in STAGE_PREREQUISITES["stage_1.5"]

    def test_stage_3_7_prerequisites(self):
        """🆕 Sprint A: stage_3.7 前置条件"""
        assert "analysis_results" in STAGE_PREREQUISITES["stage_3.7"]
        assert "gate_stage_3.5" in STAGE_PREREQUISITES["stage_3.7"]

    def test_stage_4_requires_interpretation_priorities(self):
        """🆕 Sprint A: stage_4 前置增加 interpretation_priorities"""
        assert "interpretation_priorities" in STAGE_PREREQUISITES["stage_4"]

    def test_optional_artifacts_registered(self):
        """🆕 Sprint A: 可选产物注册验证"""
        assert "data_profile" in OPTIONAL_ARTIFACTS["stage_1"]
        assert "literature_seeds" in OPTIONAL_ARTIFACTS["stage_2"]
        assert "sap_amendment" in OPTIONAL_ARTIFACTS["stage_3"]
        assert "interpretation_priorities" in OPTIONAL_ARTIFACTS["stage_3.7"]
        assert "multi_dataset_mode" in OPTIONAL_ARTIFACTS["stage_1.5"]

    def test_sap_amendment_max(self):
        """🆕 Sprint A: SAP Amendment 上限常量"""
        assert SAP_AMENDMENT_MAX == 3


class TestPaperTrack:
    """Paper Track 扩展测试（track 字段 + Stage 5）"""

    def test_track_defaults_to_none(self, pm):
        assert pm.get_track() is None
        assert pm.data.get("track") is None

    def test_set_track_report_only(self, pm):
        pm.set_track("report_only")
        assert pm.get_track() == "report_only"
        assert pm.data["track"] == "report_only"

    def test_set_track_full_paper(self, pm):
        pm.set_track("full_paper")
        assert pm.get_track() == "full_paper"

    def test_set_track_invalid_raises(self, pm):
        with pytest.raises(PassportError, match="无效 track"):
            pm.set_track("bogus")

    def test_stage_5_0_prerequisites_require_final_report(self, pm):
        """stage_5_0_intake 需要 final_report 和 gate_stage_3.5"""
        pm.set_gate_result("stage_3.5", "passed", 9, 9)
        ok, missing = pm.verify_prerequisites("stage_5_0_intake")
        assert not ok
        assert "final_report" in missing

    def test_stage_5_0_prerequisites_pass_when_complete(self, pm):
        """stage_5_0_intake 前置条件满足时返回 True"""
        pm.add_artifact({"id": "final_report", "stage": "stage_4", "name": "report", "type": "report", "format": "md"})
        pm.update_status("final_report", "completed")
        pm.set_gate_result("stage_3.5", "passed", 9, 9)
        ok, missing = pm.verify_prerequisites("stage_5_0_intake")
        assert ok
        assert missing == []

    def test_stage_5_paper_requires_handoff_bundle(self, pm):
        """stage_5_paper 需要 msra_handoff_bundle"""
        ok, missing = pm.verify_prerequisites("stage_5_paper")
        assert not ok
        assert "msra_handoff_bundle" in missing


class TestStage3_7InterpretationSession:
    """🆕 Sprint A: Stage 3.7 结果解读会话测试"""

    def test_stage_3_7_blocked_without_gate(self, pm):
        """stage_3.7 前置条件：缺 gate_stage_3.5 → 阻断"""
        pm.add_artifact({"id": "analysis_results", "stage": "stage_3", "name": "results"})
        pm.update_status("analysis_results", "completed")
        ok, missing = pm.verify_prerequisites("stage_3.7")
        assert not ok
        assert any("gate_stage_3.5" in m for m in missing)

    def test_stage_3_7_passes_with_gate(self, pm):
        """stage_3.7 前置条件：gate 通过 + analysis_results 完成 → 放行"""
        pm.add_artifact({"id": "analysis_results", "stage": "stage_3", "name": "results"})
        pm.update_status("analysis_results", "completed")
        pm.set_gate_result("stage_3.5", "passed", 9, 9)
        ok, missing = pm.verify_prerequisites("stage_3.7")
        assert ok
        assert missing == []

    def test_stage_4_blocked_without_interpretation_priorities(self, pm):
        """stage_4 前置条件：缺 interpretation_priorities → 阻断"""
        pm.add_artifact({"id": "analysis_results", "stage": "stage_3", "name": "results"})
        pm.update_status("analysis_results", "completed")
        pm.set_gate_result("stage_3.5", "passed", 9, 9)
        ok, missing = pm.verify_prerequisites("stage_4")
        assert not ok
        assert "interpretation_priorities" in missing

    def test_stage_4_passes_with_interpretation_priorities(self, pm):
        """stage_4 前置条件：interpretation_priorities 完成 → 放行"""
        pm.add_artifact({"id": "analysis_results", "stage": "stage_3", "name": "results"})
        pm.update_status("analysis_results", "completed")
        pm.add_artifact({"id": "interpretation_priorities", "stage": "stage_3.7", "name": "priorities"})
        pm.update_status("interpretation_priorities", "completed")
        pm.set_gate_result("stage_3.5", "passed", 9, 9)
        ok, missing = pm.verify_prerequisites("stage_4")
        assert ok
        assert missing == []


class TestSAPAmendment:
    """🆕 Sprint A: SAP Amendment 计数器测试（优化#7）"""

    def test_add_first_amendment(self, pm):
        """第一次 SAP Amendment 成功记录"""
        pm.add_sap_amendment("amendment_001", {
            "original_spec": "ANCOVA",
            "amended_spec": "Wilcoxon rank-sum",
            "trigger": "正态性不满足",
            "justification": "Shapiro-Wilk p<0.05",
            "user_approval": True,
        })
        assert pm.get_sap_amendment_count() == 1

    def test_add_amendment_increments_count(self, pm):
        """多次 Amendment 计数递增"""
        for i in range(SAP_AMENDMENT_MAX):
            pm.add_sap_amendment(f"amendment_{i:03d}", {
                "original_spec": f"method_{i}",
                "amended_spec": f"method_{i+1}",
                "trigger": "test",
                "justification": "test",
                "user_approval": True,
            })
        assert pm.get_sap_amendment_count() == SAP_AMENDMENT_MAX

    def test_amendment_exceeds_max_raises(self, pm):
        """超过上限抛出 PassportError"""
        for i in range(SAP_AMENDMENT_MAX):
            pm.add_sap_amendment(f"amendment_{i:03d}", {
                "original_spec": f"method_{i}",
                "amended_spec": f"method_{i+1}",
                "trigger": "test",
                "justification": "test",
                "user_approval": True,
            })
        with pytest.raises(PassportError, match="超过硬性上限"):
            pm.add_sap_amendment("amendment_004", {
                "original_spec": "method_3",
                "amended_spec": "method_4",
                "trigger": "test",
                "justification": "test",
                "user_approval": True,
            })

    def test_get_amendments_returns_all(self, pm):
        """get_sap_amendments 返回所有修正记录"""
        pm.add_sap_amendment("amendment_001", {"trigger": "test1"})
        pm.add_sap_amendment("amendment_002", {"trigger": "test2"})
        amendments = pm.get_sap_amendments()
        assert len(amendments) == 2
        assert amendments[0]["id"] == "amendment_001"
        assert amendments[1]["id"] == "amendment_002"

    def test_amendment_artifact_type(self, pm):
        """Amendment 产物 type 字段为 'amendment'"""
        pm.add_sap_amendment("amendment_001", {"trigger": "test"})
        a = pm.get_artifact("amendment_001")
        assert a["type"] == "amendment"
        assert a["stage"] == "stage_3"


class TestOptionalArtifacts:
    """🆕 Sprint A: 可选产物验证测试"""

    def test_optional_artifacts_absent_by_default(self, pm):
        """默认情况下可选产物全部缺失"""
        present, absent = pm.verify_optional_artifacts("stage_1")
        assert present == []
        assert "data_profile" in absent

    def test_optional_artifacts_present_when_added(self, pm):
        """添加可选产物后报告为 present"""
        pm.add_artifact({"id": "data_profile", "stage": "stage_1", "name": "profile"})
        pm.update_status("data_profile", "completed")
        present, absent = pm.verify_optional_artifacts("stage_1")
        assert "data_profile" in present
        assert "data_profile" not in absent

    def test_optional_artifacts_literature_seeds(self, pm):
        """literature_seeds 可选产物验证"""
        present, absent = pm.verify_optional_artifacts("stage_2")
        assert "literature_seeds" in absent

        pm.add_artifact({"id": "literature_seeds", "stage": "stage_2", "name": "seeds"})
        pm.update_status("literature_seeds", "completed")
        present, absent = pm.verify_optional_artifacts("stage_2")
        assert "literature_seeds" in present

    def test_optional_artifacts_multi_dataset(self, pm):
        """多数据集模式可选产物验证"""
        pm.add_artifact({"id": "multi_dataset_mode", "stage": "stage_1.5", "name": "multi"})
        pm.update_status("multi_dataset_mode", "completed")
        present, absent = pm.verify_optional_artifacts("stage_1.5")
        assert "multi_dataset_mode" in present
        assert "cross_site_consistency" in absent

    def test_optional_artifacts_empty_stage(self, pm):
        """无可选产物的阶段返回空列表"""
        present, absent = pm.verify_optional_artifacts("stage_2.5")
        assert present == []
        assert absent == []
