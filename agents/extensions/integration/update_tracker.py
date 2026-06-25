"""
Update Tracker - 更新追踪器

追踪外部资源的更新状态。
"""

import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import urllib.request
import ssl


@dataclass
class UpdateInfo:
    """更新信息"""
    resource_name: str
    current_version: Optional[str]
    latest_version: Optional[str]
    last_commit: Optional[str]
    is_outdated: bool
    update_priority: str  # "high", "medium", "low"
    changelog_summary: str
    breaking_changes: bool


class UpdateTracker:
    """更新追踪器"""

    # PyPI API endpoint
    PYPI_API = "https://pypi.org/pypi/{package}/json"

    # GitHub API endpoint (需要token)
    GITHUB_API = "https://api.github.com/repos/{owner}/{repo}"

    def __init__(self, github_token: Optional[str] = None):
        """初始化更新追踪器

        Args:
            github_token: GitHub API token (可选)
        """
        self.github_token = github_token
        self._cache: Dict[str, Dict] = {}

    def _make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """发起HTTP请求

        Args:
            url: 请求URL
            headers: 请求头

        Returns:
            响应JSON或None
        """
        try:
            context = ssl.create_default_context()
            req = urllib.request.Request(url)
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            with urllib.request.urlopen(req, context=context, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception:
            return None

    def get_pypi_version(self, package_name: str) -> Tuple[Optional[str], Optional[str]]:
        """获取PyPI包的最新版本和版本历史

        Args:
            package_name: 包名

        Returns:
            (最新版本, 最后更新时间)
        """
        url = self.PYPI_API.format(package=package_name)
        data = self._make_request(url)

        if data:
            version = data.get("info", {}).get("version")
            # 尝试获取最新更新时间
            urls = data.get("urls", [])
            upload_time = None
            if urls:
                upload_time = urls[0].get("upload_time", "")[:10]
            return version, upload_time
        return None, None

    def get_github_info(self, full_name: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """获取GitHub仓库信息

        Args:
            full_name: 仓库全名 (owner/repo)

        Returns:
            (最新提交日期, 星标数, 默认分支)
        """
        owner, repo = full_name.split("/")
        url = self.GITHUB_API.format(owner=owner, repo=repo)

        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        data = self._make_request(url, headers)

        if data:
            pushed_at = data.get("pushed_at", "")[:10] if data.get("pushed_at") else None
            stars = data.get("stargazers_count")
            default_branch = data.get("default_branch", "main")
            return pushed_at, stars, default_branch
        return None, None, None

    def check_package_updates(
        self,
        package_name: str,
        current_version: Optional[str] = None,
        resource_type: str = "python"
    ) -> UpdateInfo:
        """检查包更新状态

        Args:
            package_name: 包名
            current_version: 当前已安装版本
            resource_type: 资源类型 ("python" 或 "r")

        Returns:
            更新信息
        """
        if resource_type == "python":
            latest_version, last_update = self.get_pypi_version(package_name)
        else:
            latest_version, last_update = None, None

        is_outdated = False
        update_priority = "low"
        breaking_changes = False
        changelog_summary = ""

        if current_version and latest_version:
            is_outdated = latest_version != current_version
            if is_outdated:
                # 简单的版本比较
                current_parts = [int(x) for x in re.findall(r"\d+", current_version)]
                latest_parts = [int(x) for x in re.findall(r"\d+", latest_version)]

                if latest_parts > current_parts:
                    # 主要版本更新
                    if latest_parts[0] > current_parts[0]:
                        update_priority = "high"
                        breaking_changes = True
                    elif len(latest_parts) > 1 and len(current_parts) > 1:
                        if latest_parts[1] > current_parts[1]:
                            update_priority = "medium"

                changelog_summary = f"Update available: {current_version} -> {latest_version}"

        return UpdateInfo(
            resource_name=package_name,
            current_version=current_version,
            latest_version=latest_version,
            last_commit=last_update,
            is_outdated=is_outdated,
            update_priority=update_priority,
            changelog_summary=changelog_summary,
            breaking_changes=breaking_changes
        )

    def check_registry_updates(
        self,
        registry_path: Optional[Path] = None
    ) -> Dict:
        """检查注册表中所有资源的更新状态

        Args:
            registry_path: 资源注册表路径

        Returns:
            更新检查报告
        """
        if registry_path is None:
            registry_path = Path(__file__).parent.parent.parent / "registry" / "github_projects.json"

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_checked": 0,
            "outdated": 0,
            "high_priority": 0,
            "details": []
        }

        for category in registry["categories"].values():
            for resource in category.get("items", []):
                if resource.get("msra_status") in ["integrated", "candidate"]:
                    # 获取当前已安装版本
                    current_version = self._get_installed_version(resource["name"])

                    update_info = self.check_package_updates(
                        resource["name"],
                        current_version,
                        resource.get("language", "").lower()
                    )

                    results["total_checked"] += 1
                    if update_info.is_outdated:
                        results["outdated"] += 1
                        if update_info.update_priority == "high":
                            results["high_priority"] += 1

                    results["details"].append(asdict(update_info))

        return results

    def _get_installed_version(self, package_name: str) -> Optional[str]:
        """获取已安装包的版本"""
        try:
            result = subprocess.run(
                ["pip", "show", package_name],
                capture_output=True,
                text=True,
                check=True
            )
            match = re.search(r"Version:\s*(\S+)", result.stdout)
            if match:
                return match.group(1)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def generate_update_report(self, check_results: Dict) -> str:
        """生成更新报告

        Args:
            check_results: 更新检查结果

        Returns:
            格式化报告
        """
        lines = [
            "# Resource Update Report",
            f"Generated: {check_results['timestamp']}",
            "",
            f"## Summary",
            f"- Total checked: {check_results['total_checked']}",
            f"- Outdated: {check_results['outdated']}",
            f"- High priority updates: {check_results['high_priority']}",
            ""
        ]

        # 高优先级更新
        high_priority = [d for d in check_results["details"] if d.get("update_priority") == "high"]
        if high_priority:
            lines.extend(["## High Priority Updates", ""])
            for item in high_priority:
                lines.append(f"- **{item['resource_name']}**: {item['changelog_summary']}")
                if item.get("breaking_changes"):
                    lines.append("  - ⚠️ Breaking changes detected")
            lines.append("")

        # 所有过时资源
        outdated = [d for d in check_results["details"] if d.get("is_outdated")]
        if outdated:
            lines.extend(["## All Outdated Resources", ""])
            lines.append("| Resource | Current | Latest | Priority |")
            lines.append("|----------|---------|--------|----------|")
            for item in outdated:
                lines.append(
                    f"| {item['resource_name']} | {item.get('current_version', 'N/A')} | "
                    f"{item.get('latest_version', 'N/A')} | {item.get('update_priority', 'N/A')} |"
                )

        return "\n".join(lines)


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Update Tracker CLI")
    parser.add_argument("--check", type=str, help="Check specific package")
    parser.add_argument("--all", action="store_true", help="Check all registered resources")
    parser.add_argument("--report", action="store_true", help="Generate update report")
    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()
    tracker = UpdateTracker()

    if args.check:
        result = tracker.check_package_updates(args.check)
        output = json.dumps(asdict(result), indent=2, ensure_ascii=False)
    elif args.all:
        results = tracker.check_registry_updates()
        if args.report:
            output = tracker.generate_update_report(results)
        else:
            output = json.dumps(results, indent=2, ensure_ascii=False)
    else:
        output = "Use --check <package> or --all"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
