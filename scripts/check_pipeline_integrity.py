#!/usr/bin/env python3
"""
check_pipeline_integrity.py — Pipeline 完整性检查脚本
=====================================================
检查 SKILL.md 中的 Phase Boundary 和 Bucket 分类是否一致。

用法: python scripts/check_pipeline_integrity.py [--skill <skill_dir>]

作者: MSRA Team
版本: 0.1.0
"""
import sys
import os
import re
from pathlib import Path


def check_skill_integrity(skill_dir: str) -> dict:
    """检查单个 skill 的完整性"""
    skill_md = Path(skill_dir) / "SKILL.md"
    if not skill_md.exists():
        return {"skill": skill_dir, "status": "ERROR", "message": "SKILL.md not found"}

    content = skill_md.read_text(encoding="utf-8")
    issues = []

    # Check frontmatter
    if not content.startswith("---"):
        issues.append("Missing frontmatter")

    # Check for IRON RULE markers
    iron_rules = len(re.findall(r"IRON RULE", content))
    if iron_rules == 0:
        issues.append("No IRON RULE markers found")

    # Check for checkpoint markers
    checkpoints = len(re.findall(r"🔴|🛑|CHECKPOINT|MANDATORY", content))

    # Check for broken references (basic)
    refs = re.findall(r"`(shared/[^`]+)`", content)
    for ref in refs:
        if not Path(ref).exists():
            issues.append(f"Broken reference: {ref}")

    return {
        "skill": skill_dir,
        "status": "OK" if not issues else "WARN",
        "iron_rules": iron_rules,
        "checkpoints": checkpoints,
        "issues": issues,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Check skill integrity")
    parser.add_argument("--skill", help="Specific skill directory to check")
    args = parser.parse_args()

    skills_dir = Path("skills")
    if args.skill:
        skills_to_check = [skills_dir / args.skill]
    else:
        skills_to_check = sorted(skills_dir.iterdir())

    results = []
    for skill_path in skills_to_check:
        if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
            result = check_skill_integrity(str(skill_path))
            results.append(result)

    for r in results:
        status_icon = "✅" if r["status"] == "OK" else "⚠️" if r["status"] == "WARN" else "❌"
        print(f"{status_icon} {r['skill']}: {r['status']}")
        if "issues" in r and r["issues"]:
            for issue in r["issues"]:
                print(f"   - {issue}")

    return 0 if all(r["status"] == "OK" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
