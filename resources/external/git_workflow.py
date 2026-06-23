#!/usr/bin/env python
"""
Git Workflow Script for MSRA External Resources

提供标准化的Git操作接口。
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_git(args, check=True):
    """运行git命令"""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        print(f"Error: {' '.join(args)}")
        print(result.stderr)
        sys.exit(1)
    return result


def get_changed_files():
    """获取已更改的文件"""
    result = run_git(["status", "--porcelain"])
    files = []
    for line in result.stdout.strip().split("\n"):
        if line:
            files.append(line[3:])  # 去掉状态前缀
    return files


def categorize_changes(files):
    """分类变更文件"""
    categories = {
        "registry": [],
        "integration": [],
        "optimization": [],
        "tests": [],
        "docs": [],
        "other": []
    }

    for f in files:
        if "registry" in f:
            categories["registry"].append(f)
        elif "integration" in f:
            categories["integration"].append(f)
        elif "optimization" in f:
            categories["optimization"].append(f)
        elif "test" in f:
            categories["tests"].append(f)
        elif f.endswith(".md"):
            categories["docs"].append(f)
        else:
            categories["other"].append(f)

    return categories


def determine_commit_type(categories):
    """确定提交类型"""
    if categories["registry"] or categories["integration"]:
        return "feat"
    elif categories["tests"]:
        return "test"
    elif categories["docs"]:
        return "docs"
    elif categories["optimization"]:
        return "chore"
    else:
        return "chore"


def generate_commit_message(categories, commit_type):
    """生成提交消息"""
    parts = []

    # 主标题
    if categories["registry"]:
        parts.append("feat(registry): update external resource registry")
    elif categories["integration"]:
        parts.append("feat(integration): update integration module")
    elif categories["optimization"]:
        parts.append("chore: update optimization configuration")
    elif categories["tests"]:
        parts.append("test: update external resources tests")
    else:
        parts.append("docs: update documentation")

    # 详细说明
    details = []
    for cat, files in categories.items():
        if files:
            details.append(f"- {cat}: {len(files)} file(s) changed")

    return "\n".join([parts[0], "", "\n".join(details)])


def cmd_status():
    """显示Git状态"""
    print("\n" + "=" * 60)
    print("MSRA External Resources - Git Status")
    print("=" * 60)

    result = run_git(["status"])
    print(result.stdout)

    # 显示已跟踪的文件
    files = get_changed_files()
    if files:
        print(f"\nChanged files ({len(files)}):")
        categories = categorize_changes(files)
        for cat, cat_files in categories.items():
            if cat_files:
                print(f"\n  {cat.upper()}:")
                for f in cat_files[:5]:  # 最多显示5个
                    print(f"    - {f}")
                if len(cat_files) > 5:
                    print(f"    ... and {len(cat_files) - 5} more")


def cmd_commit(args):
    """提交变更"""
    files = get_changed_files()

    if not files and not args.all:
        print("No changes to commit. Use --all to include all changes.")
        return

    categories = categorize_changes(files if not args.all else [])
    commit_type = determine_commit_type(categories)

    # 生成默认消息
    default_msg = generate_commit_message(categories, commit_type)

    if args.message:
        message = args.message
    else:
        print("\nCommit message (leave empty to use default):")
        print("-" * 40)
        print(default_msg)
        print("-" * 40)
        message = input("\nEnter commit message (or press Enter for default):\n> ")
        if not message.strip():
            message = default_msg

    # 执行提交
    if args.all:
        run_git(["add", "-A"])
    else:
        for f in files:
            run_git(["add", f])

    run_git(["commit", "-m", message])
    print(f"\nCommitted: {message[:50]}...")


def cmd_push(args):
    """推送变更"""
    branch = run_git(["branch", "--show-current"], check=False).stdout.strip()
    if not branch:
        branch = "HEAD"

    print(f"Pushing to origin/{branch}...")
    run_git(["push", "origin", branch])
    print("Push completed.")


def cmd_cycle(args):
    """运行完整的优化循环并提交"""
    from resources.external.optimization.optimization_scheduler import OptimizationScheduler

    print("\n" + "=" * 60)
    print("Running Optimization Cycle")
    print("=" * 60)

    scheduler = OptimizationScheduler()
    cycle = scheduler.run_optimization_cycle()

    print("\nCycle Results:")
    print(f"  Tasks: {cycle.tasks_passed}/{cycle.tasks_executed} passed")

    if cycle.tasks_failed > 0:
        print(f"\nWarning: {cycle.tasks_failed} task(s) failed")
        if not args.force:
            response = input("Continue with commit? (y/n): ")
            if response.lower() != "y":
                print("Aborted.")
                return

    # 自动提交
    if args.commit:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"chore: complete optimization cycle {timestamp}\n\n"
        message += f"- Tasks: {cycle.tasks_passed}/{cycle.tasks_executed} passed\n"
        message += f"- Duration: {cycle.duration_seconds:.1f}s"

        run_git(["add", "-A"])
        run_git(["commit", "-m", message])
        print(f"\nCommitted: {message[:50]}...")

        if args.push:
            cmd_push(args)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="MSRA External Resources Git Workflow")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status command
    subparsers.add_parser("status", help="Show git status")

    # commit command
    commit_parser = subparsers.add_parser("commit", help="Commit changes")
    commit_parser.add_argument("-m", "--message", type=str, help="Commit message")
    commit_parser.add_argument("-a", "--all", action="store_true", help="Stage all changes")

    # push command
    subparsers.add_parser("push", help="Push to remote")

    # cycle command
    cycle_parser = subparsers.add_parser("cycle", help="Run optimization cycle")
    cycle_parser.add_argument("--commit", action="store_true", help="Auto-commit results")
    cycle_parser.add_argument("--push", action="store_true", help="Auto-push after commit")
    cycle_parser.add_argument("--force", action="store_true", help="Force continue on failure")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "commit":
        cmd_commit(args)
    elif args.command == "push":
        cmd_push(args)
    elif args.command == "cycle":
        cmd_cycle(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
