"""
Tests for External Resource Registry Module

运行方式: pytest resources/external/tests/ -v
"""

import pytest
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from resources.external.integration.resource_loader import (
    ResourceRegistry,
    GitHubProject,
    AcademicLiterature
)


class TestResourceRegistry:
    """资源注册表测试"""

    @pytest.fixture
    def registry(self):
        """创建资源注册表实例"""
        return ResourceRegistry()

    def test_registry_initialization(self, registry):
        """测试注册表初始化"""
        assert registry.registry_dir.exists()
        assert (registry.registry_dir / "github_projects.json").exists()
        assert (registry.registry_dir / "academic_literature.json").exists()

    def test_get_github_projects(self, registry):
        """测试获取GitHub项目"""
        projects = registry.get_github_projects()
        assert len(projects) > 0
        assert all(isinstance(p, GitHubProject) for p in projects)

    def test_get_integrated_projects(self, registry):
        """测试获取已集成项目"""
        integrated = registry.get_integrated_projects()
        assert all(p.msra_status == "integrated" for p in integrated)

    def test_get_candidate_projects(self, registry):
        """测试获取候选项目"""
        candidates = registry.get_candidate_projects()
        assert all(p.msra_status == "candidate" for p in candidates)

    def test_filter_by_stars(self, registry):
        """测试按星标数筛选"""
        projects = registry.get_github_projects(min_stars=1000)
        assert all(p.stars >= 1000 for p in projects)

    def test_filter_by_compatibility(self, registry):
        """测试按兼容性评分筛选"""
        projects = registry.get_github_projects(min_compatibility=9)
        assert all(p.compatibility_score >= 9 for p in projects)

    def test_get_academic_topics(self, registry):
        """测试获取学术主题"""
        topics = registry.get_academic_topics()
        assert len(topics) > 0
        assert all(isinstance(t, AcademicLiterature) for t in topics)

    def test_get_integration_plan(self, registry):
        """测试获取集成计划"""
        plan = registry.get_integration_plan()
        assert "phase_1_immediate" in plan
        assert "phase_2_short_term" in plan

    def test_get_key_gaps(self, registry):
        """测试获取技术缺口"""
        gaps = registry.get_key_gaps()
        assert len(gaps) > 0

    def test_get_statistics(self, registry):
        """测试获取统计信息"""
        stats = registry.get_statistics()
        assert "total_github_projects" in stats
        assert "integrated_projects" in stats
        assert "candidate_projects" in stats

    def test_export_summary(self, registry):
        """测试导出摘要"""
        summary = registry.export_summary()
        assert "# Resource Registry Summary" in summary
        assert "Integrated" in summary
        assert "Candidate" in summary


class TestGitHubProject:
    """GitHub项目数据类测试"""

    def test_project_creation(self):
        """测试项目创建"""
        project = GitHubProject(
            name="test-package",
            full_name="org/test-package",
            url="https://github.com/org/test-package",
            description="Test package",
            language="Python",
            license="MIT",
            stars=100,
            msra_status="candidate"
        )
        assert project.name == "test-package"
        assert project.stars == 100
        assert project.msra_status == "candidate"


class TestAcademicLiterature:
    """学术文献数据类测试"""

    def test_literature_creation(self):
        """测试文献创建"""
        lit = AcademicLiterature(
            topic="Test Topic",
            description="Test description",
            msra_reference="shared/test.md",
            key_references=["Ref1", "Ref2"],
            research_frontier=["Frontier1"]
        )
        assert lit.topic == "Test Topic"
        assert len(lit.key_references) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
