"""
Tests for Compatibility Checker Module

运行方式: pytest agents/extensions/tests/test_compatibility.py -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.extensions.integration.compatibility_checker import (
    CompatibilityChecker,
    CompatibilityResult
)


class TestCompatibilityChecker:
    """兼容性检查器测试"""

    @pytest.fixture
    def checker(self):
        """创建兼容性检查器实例"""
        return CompatibilityChecker()

    def test_checker_initialization(self, checker):
        """测试检查器初始化"""
        assert checker.requirements_path.exists()

    @patch('subprocess.run')
    def test_python_package_installed(self, mock_run, checker):
        """测试已安装的Python包检查"""
        # 模拟pip list输出
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"name": "pandas", "version": "2.0.0"}]'
        )
        checker._installed_packages = None  # 重置缓存

        result = checker.check_python_package("pandas")
        assert result.is_compatible == True
        assert result.resource_type == "python"

    @patch('subprocess.run')
    def test_python_package_not_installed(self, mock_run, checker):
        """测试未安装的Python包检查"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"name": "pandas", "version": "2.0.0"}]'
        )
        checker._installed_packages = None

        result = checker.check_python_package("nonexistent-package")
        assert result.is_compatible == False
        assert len(result.recommendations) > 0

    def test_compatibility_result_creation(self):
        """测试兼容性结果创建"""
        result = CompatibilityResult(
            resource_name="test-package",
            resource_type="python",
            is_compatible=True,
            score=10,
            issues=[],
            recommendations=["Recommendation 1"],
            dependencies_met={"dep1": True},
            version_conflicts=[]
        )
        assert result.resource_name == "test-package"
        assert result.score == 10

    def test_check_r_package(self, checker):
        """测试R包检查（模拟）"""
        # R环境检查 - 验证返回结果结构
        result = checker.check_r_package("nonexistent")
        assert result.resource_type == "r"


class TestCompatibilityCheckerIntegration:
    """兼容性检查器集成测试"""

    @pytest.fixture
    def checker(self):
        return CompatibilityChecker()

    @patch('subprocess.run')
    def test_check_all_integrated(self, mock_run, checker):
        """测试检查所有已集成资源"""
        # 模拟pip list
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"name": "dowhy", "version": "0.11"}]'
        )

        results = checker.check_all_integrated()
        assert "timestamp" in results
        assert "total_checked" in results
        assert "compatible" in results
        assert "incompatible" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
