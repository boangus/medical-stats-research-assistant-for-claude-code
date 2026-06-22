"""
Compatibility Checker - 兼容性检查器

检查外部资源与MSRA项目的兼容性。
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re


@dataclass
class CompatibilityResult:
    """兼容性检查结果"""
    resource_name: str
    resource_type: str  # "python", "r"
    is_compatible: bool
    score: int  # 0-10
    issues: List[str]
    recommendations: List[str]
    dependencies_met: Dict[str, bool]
    version_conflicts: List[str]


class CompatibilityChecker:
    """兼容性检查器"""

    # MSRA项目已安装的核心依赖
    CORE_DEPENDENCIES = {
        "pandas": ">=1.5",
        "numpy": ">=1.24",
        "scipy": ">=1.10",
        "statsmodels": ">=0.14",
        "scikit-learn": ">=1.3",
    }

    # 可选的已安装依赖
    OPTIONAL_DEPENDENCIES = {
        "lifelines": ">=0.27",
        "dowhy": ">=0.11",
        "econml": ">=0.15",
        "matplotlib": ">=3.7",
        "seaborn": ">=0.13",
        "pymc": ">=5.10",
        "xgboost": ">=2.0",
        "lightgbm": ">=4.0",
    }

    def __init__(self, requirements_path: Optional[Path] = None):
        """初始化兼容性检查器

        Args:
            requirements_path: requirements.txt 文件路径
        """
        if requirements_path is None:
            self.requirements_path = Path(__file__).parent.parent.parent.parent / "requirements.txt"
        else:
            self.requirements_path = requirements_path
        self._installed_packages: Optional[Dict[str, str]] = None

    def _get_installed_packages(self) -> Dict[str, str]:
        """获取已安装的Python包版本"""
        if self._installed_packages is None:
            try:
                result = subprocess.run(
                    ["pip", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                packages = json.loads(result.stdout)
                self._installed_packages = {
                    pkg["name"].lower(): pkg["version"]
                    for pkg in packages
                }
            except (subprocess.CalledProcessError, FileNotFoundError):
                self._installed_packages = {}
        return self._installed_packages

    def check_python_package(
        self,
        package_name: str,
        required_version: Optional[str] = None,
        dependencies: Optional[List[str]] = None
    ) -> CompatibilityResult:
        """检查Python包的兼容性

        Args:
            package_name: 包名
            required_version: 所需版本
            dependencies: 依赖列表

        Returns:
            兼容性检查结果
        """
        installed = self._get_installed_packages()
        issues = []
        recommendations = []
        deps_met = {}
        version_conflicts = []

        # 检查主包是否已安装
        pkg_key = package_name.lower()
        is_installed = pkg_key in installed

        if not is_installed:
            issues.append(f"{package_name} is not installed")
            recommendations.append(f"Install with: pip install {package_name}{required_version or ''}")

        # 检查依赖是否满足
        if dependencies:
            for dep in dependencies:
                dep_name = re.split(r"[><=!]", dep)[0].strip().lower()
                dep_met = dep_name in installed
                deps_met[dep] = dep_met
                if not dep_met:
                    issues.append(f"Dependency {dep} is not installed")
                    recommendations.append(f"Install dependency: pip install {dep}")

        # 计算兼容性评分
        score = 10
        if not is_installed:
            score -= 5
        if issues:
            score -= min(len(issues) * 2, 5)

        return CompatibilityResult(
            resource_name=package_name,
            resource_type="python",
            is_compatible=is_installed and len([d for d in deps_met.values() if not d]) == 0,
            score=max(score, 0),
            issues=issues,
            recommendations=recommendations,
            dependencies_met=deps_met,
            version_conflicts=version_conflicts
        )

    def check_r_package(
        self,
        package_name: str,
        dependencies: Optional[List[str]] = None
    ) -> CompatibilityResult:
        """检查R包的兼容性

        Args:
            package_name: R包名
            dependencies: 依赖列表

        Returns:
            兼容性检查结果
        """
        issues = []
        recommendations = []
        deps_met = {}

        # 尝试检查R包是否已安装
        try:
            result = subprocess.run(
                ["Rscript", "-e", f"packageVersion('{package_name}')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            is_installed = result.returncode == 0 and package_name in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            is_installed = False
            issues.append("R environment not available or package not installed")
            recommendations.append("Install R package via: install.packages('" + package_name + "')")

        if dependencies:
            for dep in dependencies:
                dep_name = dep.strip("'\"")
                try:
                    result = subprocess.run(
                        ["Rscript", "-e", f"packageVersion('{dep_name}')"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    deps_met[dep] = result.returncode == 0
                except:
                    deps_met[dep] = False
                    issues.append(f"R dependency {dep} not installed")

        score = 10 if is_installed else 5
        if issues:
            score -= min(len(issues) * 2, 5)

        return CompatibilityResult(
            resource_name=package_name,
            resource_type="r",
            is_compatible=is_installed,
            score=max(score, 0),
            issues=issues,
            recommendations=recommendations,
            dependencies_met=deps_met,
            version_conflicts=[]
        )

    def check_resource_compatibility(
        self,
        resource: Dict
    ) -> CompatibilityResult:
        """检查单个资源的兼容性

        Args:
            resource: 资源信息字典

        Returns:
            兼容性检查结果
        """
        name = resource["name"]
        resource_type = resource.get("language", "").lower()
        deps = resource.get("dependencies", [])

        if resource_type == "python":
            return self.check_python_package(name, dependencies=deps)
        elif resource_type == "r":
            return self.check_r_package(name, dependencies=deps)
        else:
            return CompatibilityResult(
                resource_name=name,
                resource_type=resource_type,
                is_compatible=False,
                score=0,
                issues=[f"Unknown resource type: {resource_type}"],
                recommendations=["Specify resource type as 'python' or 'r'"],
                dependencies_met={},
                version_conflicts=[]
            )

    def check_all_integrated(self, registry_path: Optional[Path] = None) -> Dict:
        """检查所有已集成资源的兼容性

        Args:
            registry_path: 资源注册表路径

        Returns:
            兼容性检查报告
        """
        if registry_path is None:
            # 从 integration/ 目录向上找到 external/registry/
            registry_path = Path(__file__).parent.parent / "registry" / "github_projects.json"

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        results = {
            "timestamp": "",
            "total_checked": 0,
            "compatible": 0,
            "incompatible": 0,
            "details": []
        }

        from datetime import datetime
        results["timestamp"] = datetime.now().isoformat()

        for category in registry["categories"].values():
            for resource in category.get("items", []):
                if resource.get("msra_status") == "integrated":
                    result = self.check_resource_compatibility(resource)
                    results["total_checked"] += 1
                    if result.is_compatible:
                        results["compatible"] += 1
                    else:
                        results["incompatible"] += 1
                    results["details"].append(asdict(result))

        return results

    def generate_fix_script(self, check_results: Dict) -> str:
        """生成修复脚本

        Args:
            check_results: 兼容性检查结果

        Returns:
            修复脚本内容
        """
        lines = [
            "#!/bin/bash",
            "# Auto-generated compatibility fix script",
            f"# Generated: {check_results['timestamp']}",
            "",
            "set -e",
            ""
        ]

        for detail in check_results.get("details", []):
            if not detail["is_compatible"]:
                if detail["recommendations"]:
                    lines.append(f"# Fix for {detail['resource_name']}")
                    for rec in detail["recommendations"]:
                        if "pip install" in rec:
                            lines.append(rec.replace("pip install", "pip install -q"))
                    lines.append("")

        return "\n".join(lines)


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Compatibility Checker CLI")
    parser.add_argument("--check", type=str, help="Check specific package")
    parser.add_argument("--all", action="store_true", help="Check all integrated resources")
    parser.add_argument("--fix-script", action="store_true", help="Generate fix script")
    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()
    checker = CompatibilityChecker()

    if args.check:
        result = checker.check_python_package(args.check)
        output = json.dumps(asdict(result), indent=2, ensure_ascii=False)
    elif args.all:
        results = checker.check_all_integrated()
        output = json.dumps(results, indent=2, ensure_ascii=False)
    else:
        output = "Use --check <package> or --all"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        if args.fix_script and args.all:
            fix_output = checker.generate_fix_script(results)
            fix_path = args.output.replace(".json", "_fix.sh")
            with open(fix_path, "w", encoding="utf-8") as f:
                f.write(fix_output)
    else:
        print(output)


if __name__ == "__main__":
    main()
