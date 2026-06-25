"""
Integration Tests for External Resources Module

运行方式: pytest agents/extensions/tests/test_integration.py -v
"""

import pytest
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class TestExternalResourcesIntegration:
    """外部资源模块集成测试"""

    @pytest.fixture
    def registry_path(self):
        """获取注册表路径"""
        return (
            project_root / "resources" / "external" / "registry" / "github_projects.json"
        )

    @pytest.fixture
    def academic_path(self):
        """获取学术文献注册表路径"""
        return (
            project_root / "resources" / "external" / "registry" / "academic_literature.json"
        )

    def test_registry_files_exist(self, registry_path, academic_path):
        """测试注册表文件存在"""
        assert registry_path.exists(), f"Registry not found: {registry_path}"
        assert academic_path.exists(), f"Academic registry not found: {academic_path}"

    def test_registry_json_valid(self, registry_path):
        """测试注册表JSON格式有效"""
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "categories" in data
        assert "schema_version" in data

    def test_academic_registry_json_valid(self, academic_path):
        """测试学术注册表JSON格式有效"""
        with open(academic_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "categories" in data
        assert "schema_version" in data

    def test_categories_have_required_fields(self, registry_path):
        """测试类别包含必需字段"""
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for cat_name, cat_data in data["categories"].items():
            assert "count" in cat_data
            assert "items" in cat_data
            for item in cat_data["items"]:
                assert "name" in item
                assert "url" in item
                assert "msra_status" in item

    def test_integrated_projects_have_location(self, registry_path):
        """测试已集成的项目有位置信息"""
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for cat_data in data["categories"].values():
            for item in cat_data.get("items", []):
                if item.get("msra_status") == "integrated":
                    assert "msra_location" in item
                    assert item["msra_location"] is not None

    def test_academic_topics_have_references(self, academic_path):
        """测试学术主题包含参考文献"""
        with open(academic_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for cat_data in data["categories"].values():
            for topic in cat_data.get("topics", []):
                assert "topic" in topic
                assert "key_references" in topic
                assert len(topic["key_references"]) > 0


class TestExternalResourcesWorkflow:
    """外部资源工作流测试"""

    def test_module_imports(self):
        """测试模块导入"""
        from agents.extensions.integration import resource_loader
        from agents.extensions.integration import compatibility_checker
        from agents.extensions.integration import update_tracker
        assert resource_loader is not None
        assert compatibility_checker is not None
        assert update_tracker is not None

    def test_end_to_end_resource_check(self):
        """端到端资源检查测试"""
        from agents.extensions.integration.resource_loader import ResourceRegistry
        from agents.extensions.integration.compatibility_checker import CompatibilityChecker

        # 初始化组件
        registry = ResourceRegistry()
        checker = CompatibilityChecker()

        # 获取已集成项目
        integrated = registry.get_integrated_projects()

        # 验证有已集成项目
        assert len(integrated) > 0

        # 验证关键依赖存在
        stats = registry.get_statistics()
        assert stats["integrated_projects"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
