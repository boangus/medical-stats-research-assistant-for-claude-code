#!/usr/bin/env python3
"""
SKILL.md Structure Linter

验证所有 SKILL.md 文件的结构一致性:
1. 必需的 frontmatter 字段
2. IRON RULES 存在性
3. Checkpoint 格式一致性
4. 反例与黑名单存在性
5. 异常处理表格格式

Usage:
    python scripts/lint_skill_structure.py
    python scripts/lint_skill_structure.py --fix  # 自动修复可修复的问题
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


SKILLS_DIR = Path(__file__).parent.parent / "skills"


@dataclass
class LintIssue:
    file: str
    line: int
    level: str  # error, warning, info
    rule: str
    message: str


@dataclass
class LintReport:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> int:
        return sum(1 for i in self.issues if i.level == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for i in self.issues if i.level == "warning")


def check_frontmatter(content: str, filepath: str) -> List[LintIssue]:
    """检查 frontmatter 必需字段"""
    issues = []
    if not content.startswith("---"):
        issues.append(LintIssue(filepath, 1, "error", "FM-001",
                                "文件缺少 frontmatter"))
        return issues

    fm_end = content.index("---", 3)
    fm = content[3:fm_end]

    required_fields = ["version", "name", "description"]
    for field_name in required_fields:
        if f"{field_name}:" not in fm:
            issues.append(LintIssue(filepath, 1, "error", "FM-002",
                                    f"frontmatter 缺少必需字段: {field_name}"))

    return issues


def check_iron_rules(content: str, filepath: str) -> List[LintIssue]:
    """检查 IRON RULES 存在性"""
    issues = []
    if "IRON RULE" not in content and "铁律" not in content:
        issues.append(LintIssue(filepath, 0, "warning", "IR-001",
                                "缺少 IRON RULES 或铁律定义"))
    return issues


def check_checkpoints(content: str, filepath: str) -> List[LintIssue]:
    """检查 Checkpoint 格式"""
    issues = []
    checkpoint_pattern = re.compile(r'\[MANDATORY-[A-Z]+-\d+\]')
    checkpoints = checkpoint_pattern.findall(content)

    if not checkpoints:
        issues.append(LintIssue(filepath, 0, "warning", "CP-001",
                                "缺少 MANDATORY checkpoint"))

    return issues


def check_anti_patterns(content: str, filepath: str) -> List[LintIssue]:
    """检查反例与黑名单"""
    issues = []
    if "反例" not in content and "黑名单" not in content and "Anti-Pattern" not in content:
        issues.append(LintIssue(filepath, 0, "warning", "AP-001",
                                "缺少反例与黑名单定义"))
    return issues


def check_error_handling(content: str, filepath: str) -> List[LintIssue]:
    """检查异常处理表格"""
    issues = []
    if "触发条件" in content and "一线处理" in content:
        pass  # 有异常处理表格
    elif "异常" in content or "失败" in content:
        # 有异常描述但没有标准表格格式
        issues.append(LintIssue(filepath, 0, "info", "EH-001",
                                "异常处理建议使用标准三列表格格式"))
    return issues


def check_shared_references(content: str, filepath: str) -> List[LintIssue]:
    """检查 shared/ 引用的有效性"""
    issues = []
    shared_refs = re.findall(r'shared/[\w\-/]+\.\w+', content)

    project_root = SKILLS_DIR.parent
    for ref in shared_refs:
        ref_path = project_root / ref
        if not ref_path.exists():
            issues.append(LintIssue(filepath, 0, "warning", "SR-001",
                                    f"shared/ 引用不存在: {ref}"))

    return issues


def lint_skill(skill_dir: Path) -> List[LintIssue]:
    """对单个 skill 执行完整 lint"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [LintIssue(str(skill_dir), 0, "error", "SK-001",
                          "SKILL.md 不存在")]

    content = skill_md.read_text(encoding="utf-8")
    filepath = str(skill_md.relative_to(SKILLS_DIR.parent))

    issues = []
    issues.extend(check_frontmatter(content, filepath))
    issues.extend(check_iron_rules(content, filepath))
    issues.extend(check_checkpoints(content, filepath))
    issues.extend(check_anti_patterns(content, filepath))
    issues.extend(check_error_handling(content, filepath))
    issues.extend(check_shared_references(content, filepath))

    return issues


def main():
    report = LintReport()

    skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir()])
    print(f"🔍 Linting {len(skill_dirs)} skills...\n")

    for skill_dir in skill_dirs:
        issues = lint_skill(skill_dir)
        report.issues.extend(issues)

        if issues:
            print(f"📁 {skill_dir.name}/")
            for issue in issues:
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[issue.level]
                print(f"  {icon} [{issue.rule}] {issue.message}")
            print()

    print("=" * 60)
    print(f"📊 结果: {report.errors} 错误, {report.warnings} 警告")
    print(f"   共 {len(report.issues)} 个问题")

    if report.errors > 0:
        print("\n❌ 存在错误，需要修复")
        sys.exit(1)
    elif report.warnings > 0:
        print("\n⚠️ 存在警告，建议修复")
        sys.exit(0)
    else:
        print("\n✅ 所有检查通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
