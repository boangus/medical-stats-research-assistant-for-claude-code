"""
test_msra_handoff_bundle.py — MSRA Handoff Bundle 生成器测试
"""
import os
import pytest

from shared.passport.passport import PassportManager, PassportError
from scripts.generate_msra_handoff_bundle import generate_handoff_bundle


@pytest.fixture
def pm(tmp_dir):
    """创建一个 track=full_paper 的 PassportManager"""
    path = os.path.join(tmp_dir, "passport.json")
    pm = PassportManager(path)
    pm.set_track("full_paper")
    # 添加 Stage 4 产物（final_report）
    final_report_dir = os.path.join(tmp_dir, "MSRA", "reports")
    os.makedirs(final_report_dir, exist_ok=True)
    final_report_path = os.path.join("MSRA", "reports", "final_report.md")
    with open(os.path.join(tmp_dir, final_report_path), "w", encoding="utf-8") as f:
        f.write("# 统计报告\n\n## 结果\n\n治疗组显著优于对照组。\n")
    pm.add_artifact({
        "id": "final_report",
        "stage": "stage_4",
        "name": "final_report",
        "type": "report",
        "format": "md",
        "path": final_report_path,
        "produced_by": "report_expert",
    })
    # 添加门闸报告
    pm.add_artifact({
        "id": "gate_stage_3.5",
        "stage": "stage_3.5",
        "name": "results gate",
        "type": "gate_report",
        "format": "md",
        "path": "MSRA/reports/gate_stage_3_5.md",
        "produced_by": "qc_inspector",
    })
    pm.set_gate_result("stage_3.5", "passed", 9, 9)
    pm.data["study_type"] = "RCT"
    return pm, tmp_dir


class TestGenerateBundle:
    """Handoff Bundle 生成测试"""

    def test_bundle_created(self, pm):
        pm_obj, tmp_dir = pm
        os.chdir(tmp_dir)
        bundle_path = generate_handoff_bundle(pm_obj, sap_path=None, output_dir=None)
        assert os.path.exists(bundle_path)
        assert bundle_path.endswith("msra_handoff_bundle.md")

    def test_bundle_contains_required_sections(self, pm):
        pm_obj, tmp_dir = pm
        os.chdir(tmp_dir)
        bundle_path = generate_handoff_bundle(pm_obj)
        with open(bundle_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 检查所有 8 个必要章节（spec §4.4）
        assert "# MSRA Handoff Bundle" in content
        assert "## Source" in content
        assert "passport_id" in content
        assert "study_type: RCT" in content
        assert "track: full_paper" in content
        assert "## Research Question" in content
        assert "## Results Bundle" in content
        assert "### Tables" in content
        assert "### Figures" in content
        assert "## Methods Summary" in content
        assert "## Quality Gate Report" in content
        assert "## Literature Seed" in content
        assert "## Journal Template" in content
        assert "## Paper Configuration" in content
        assert "## Bibliography" in content
        assert "Bibliography" in content

    def test_bundle_paper_config_prefilled(self, pm):
        pm_obj, tmp_dir = pm
        os.chdir(tmp_dir)
        bundle_path = generate_handoff_bundle(pm_obj)
        with open(bundle_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 预填项
        assert "Discipline: 临床医学" in content
        assert "Paper Type: IMRaD" in content
        assert "Citation Format: Vancouver" in content
        assert "Reporting Guideline: CONSORT" in content

    def test_bundle_requires_full_paper_track(self, tmp_dir):
        """track != full_paper 时抛出 ValueError"""
        path = os.path.join(tmp_dir, "passport.json")
        pm_obj = PassportManager(path)
        # track 默认为 None
        os.chdir(tmp_dir)
        with pytest.raises(ValueError, match="full_paper"):
            generate_handoff_bundle(pm_obj)

    def test_bundle_requires_final_report_artifact(self, tmp_dir):
        """没有 final_report 产物时抛出 FileNotFoundError"""
        path = os.path.join(tmp_dir, "passport.json")
        pm_obj = PassportManager(path)
        pm_obj.set_track("full_paper")
        os.chdir(tmp_dir)
        with pytest.raises(FileNotFoundError, match="final_report"):
            generate_handoff_bundle(pm_obj)
