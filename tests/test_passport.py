"""
test_passport.py — passport.py 单元测试
"""
import json
import os

import pytest

from shared.passport.passport import (
    PassportManager,
    PassportError,
    STAGE_ORDER,
    STAGE_PREREQUISITES,
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
        assert len(STAGE_ORDER) == 9

    def test_prerequisites(self):
        assert STAGE_PREREQUISITES["stage_1"] == []
        assert "cleaned_data" in STAGE_PREREQUISITES["stage_1.5"]


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
