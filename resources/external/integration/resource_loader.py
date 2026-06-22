"""
Resource Registry Module - 资源注册模块

提供外部资源的加载、查询和管理功能。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class GitHubProject:
    """GitHub项目数据结构"""
    name: str
    full_name: str
    url: str
    description: str
    language: str
    license: str
    stars: int
    msra_status: str  # integrated, candidate, deprecated
    msra_location: Optional[str] = None
    integration_date: Optional[str] = None
    use_case: Optional[str] = None
    dependencies: Optional[List[str]] = None
    compatibility_score: int = 0
    maintenance_status: str = "unknown"
    last_commit: Optional[str] = None
    msra_priority: Optional[str] = None  # P0, P1, P2, P3


@dataclass
class AcademicLiterature:
    """学术文献数据结构"""
    topic: str
    description: str
    msra_reference: str
    key_references: List[str]
    research_frontier: List[str]


class ResourceRegistry:
    """资源注册表管理器"""

    def __init__(self, registry_dir: Optional[Path] = None):
        """初始化资源注册表管理器"""
        if registry_dir is None:
            # registry_dir 应该在 external/registry 而不是 external/integration/registry
            self.registry_dir = Path(__file__).parent.parent / "registry"
        else:
            self.registry_dir = Path(registry_dir)
        self._github_cache: Optional[Dict] = None
        self._academic_cache: Optional[Dict] = None

    def _load_github_registry(self) -> Dict:
        """加载GitHub项目注册表"""
        if self._github_cache is None:
            with open(self.registry_dir / "github_projects.json", "r", encoding="utf-8") as f:
                self._github_cache = json.load(f)
        return self._github_cache

    def _load_academic_registry(self) -> Dict:
        """加载学术文献注册表"""
        if self._academic_cache is None:
            with open(self.registry_dir / "academic_literature.json", "r", encoding="utf-8") as f:
                self._academic_cache = json.load(f)
        return self._academic_cache

    def get_github_projects(
        self,
        category: Optional[str] = None,
        msra_status: Optional[str] = None,
        min_stars: int = 0,
        min_compatibility: int = 0
    ) -> List[GitHubProject]:
        """获取GitHub项目列表

        Args:
            category: 资源类别 (e.g., "causal_inference", "survival_analysis")
            msra_status: MSRA集成状态 ("integrated", "candidate", "deprecated")
            min_stars: 最小star数量
            min_compatibility: 最小兼容性评分

        Returns:
            符合条件的GitHub项目列表
        """
        registry = self._load_github_registry()
        results = []

        categories = [category] if category else registry["categories"].keys()

        for cat in categories:
            if cat not in registry["categories"]:
                continue
            for item in registry["categories"][cat]["items"]:
                if msra_status and item.get("msra_status") != msra_status:
                    continue
                if item.get("stars", 0) < min_stars:
                    continue
                if item.get("compatibility_score", 0) < min_compatibility:
                    continue
                results.append(GitHubProject(**item))

        return results

    def get_integrated_projects(self) -> List[GitHubProject]:
        """获取已集成到MSRA的项目"""
        return self.get_github_projects(msra_status="integrated")

    def get_candidate_projects(self, priority: Optional[str] = None) -> List[GitHubProject]:
        """获取候选集成项目

        Args:
            priority: 优先级筛选 (P0, P1, P2, P3)

        Returns:
            候选项目列表
        """
        candidates = self.get_github_projects(msra_status="candidate")
        if priority:
            return [p for p in candidates if p.msra_priority == priority]
        return candidates

    def get_academic_topics(
        self,
        category: Optional[str] = None
    ) -> List[AcademicLiterature]:
        """获取学术文献主题列表

        Args:
            category: 主题类别

        Returns:
            学术主题列表
        """
        registry = self._load_academic_registry()
        results = []

        categories = [category] if category else registry["categories"].keys()

        for cat in categories:
            if cat not in registry["categories"]:
                continue
            for topic in registry["categories"][cat]["topics"]:
                results.append(AcademicLiterature(**topic))

        return results

    def get_integration_plan(self) -> Dict[str, List[str]]:
        """获取集成计划"""
        registry = self._load_github_registry()
        return registry.get("integration_plan", {})

    def get_key_gaps(self) -> List[Dict]:
        """获取已识别的技术缺口"""
        registry = self._load_github_registry()
        return registry.get("key_gaps_identified", [])

    def get_statistics(self) -> Dict[str, Any]:
        """获取注册表统计信息"""
        github = self._load_github_registry()
        academic = self._load_academic_registry()

        integrated_count = len(self.get_github_projects(msra_status="integrated"))
        candidate_count = len(self.get_github_projects(msra_status="candidate"))

        return {
            "total_github_projects": github.get("total_count", 0),
            "integrated_projects": integrated_count,
            "candidate_projects": candidate_count,
            "academic_categories": len(academic.get("categories", {})),
            "total_academic_topics": sum(
                len(cat["topics"])
                for cat in academic.get("categories", {}).values()
            ),
            "last_updated": github.get("last_updated"),
            "integration_gaps": len(self.get_key_gaps())
        }

    def export_summary(self) -> str:
        """导出注册表摘要报告"""
        stats = self.get_statistics()
        gaps = self.get_key_gaps()
        plan = self.get_integration_plan()

        lines = [
            "# Resource Registry Summary",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## GitHub Projects",
            f"- Total: {stats['total_github_projects']}",
            f"- Integrated: {stats['integrated_projects']}",
            f"- Candidate: {stats['candidate_projects']}",
            "",
            "## Academic Literature",
            f"- Categories: {stats['academic_categories']}",
            f"- Topics: {stats['total_academic_topics']}",
            "",
            "## Integration Gaps",
        ]

        for i, gap in enumerate(gaps, 1):
            lines.append(f"{i}. {gap['gap']} (Impact: {gap['impact']})")

        lines.extend(["", "## Integration Plan"])

        for phase, projects in plan.items():
            lines.append(f"- {phase}: {', '.join(projects)}")

        return "\n".join(lines)


# CLI interface
def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Resource Registry CLI")
    parser.add_argument("--summary", action="store_true", help="Show summary")
    parser.add_argument("--integrated", action="store_true", help="List integrated projects")
    parser.add_argument("--candidates", action="store_true", help="List candidate projects")
    parser.add_argument("--gaps", action="store_true", help="Show integration gaps")
    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()
    registry = ResourceRegistry()

    if args.summary:
        output = registry.export_summary()
    elif args.integrated:
        projects = registry.get_integrated_projects()
        output = json.dumps([asdict(p) for p in projects], indent=2, ensure_ascii=False)
    elif args.candidates:
        projects = registry.get_candidate_projects()
        output = json.dumps([asdict(p) for p in projects], indent=2, ensure_ascii=False)
    elif args.gaps:
        gaps = registry.get_key_gaps()
        output = json.dumps(gaps, indent=2, ensure_ascii=False)
    else:
        stats = registry.get_statistics()
        output = json.dumps(stats, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
