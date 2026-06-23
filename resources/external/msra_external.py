"""
MSRA External Resources Integration Scripts

提供命令行接口用于管理外部资源的集成、优化和追踪。
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def cmd_status(args):
    """显示资源状态"""
    from resources.external.integration.resource_loader import ResourceRegistry

    registry = ResourceRegistry()
    stats = registry.get_statistics()
    gaps = registry.get_key_gaps()

    print("\n" + "=" * 60)
    print("MSRA External Resources Status")
    print("=" * 60)

    print(f"\nGitHub Projects:")
    print(f"  Total:     {stats['total_github_projects']}")
    print(f"  Integrated: {stats['integrated_projects']}")
    print(f"  Candidate:  {stats['candidate_projects']}")

    print(f"\nAcademic Literature:")
    print(f"  Categories: {stats['academic_categories']}")
    print(f"  Topics:     {stats['total_academic_topics']}")

    print(f"\nIntegration Gaps: {stats['integration_gaps']}")
    for i, gap in enumerate(gaps[:3], 1):
        print(f"  {i}. {gap['gap'][:60]}...")

    print()


def cmd_check(args):
    """运行兼容性检查"""
    from resources.external.integration.compatibility_checker import CompatibilityChecker

    checker = CompatibilityChecker()

    if args.package:
        result = checker.check_python_package(args.package)
        print(f"\nPackage: {result.resource_name}")
        print(f"Status: {'Compatible' if result.is_compatible else 'Not Compatible'}")
        print(f"Score: {result.score}/10")
        if result.issues:
            print(f"Issues: {', '.join(result.issues)}")
        if result.recommendations:
            print(f"Recommendations: {', '.join(result.recommendations)}")
    else:
        results = checker.check_all_integrated()
        print(f"\nChecked: {results['total_checked']}")
        print(f"Compatible: {results['compatible']}")
        print(f"Incompatible: {results['incompatible']}")


def cmd_update(args):
    """检查更新"""
    from resources.external.integration.update_tracker import UpdateTracker

    tracker = UpdateTracker()

    if args.package:
        result = tracker.check_package_updates(args.package)
        print(f"\nPackage: {result.resource_name}")
        print(f"Current: {result.current_version or 'N/A'}")
        print(f"Latest: {result.latest_version or 'N/A'}")
        print(f"Outdated: {result.is_outdated}")
        if result.is_outdated:
            print(f"Priority: {result.update_priority}")
    else:
        results = tracker.check_registry_updates()
        print(f"\nTotal: {results['total_checked']}")
        print(f"Outdated: {results['outdated']}")
        print(f"High Priority: {results['high_priority']}")


def cmd_optimize(args):
    """运行优化循环"""
    from resources.external.optimization.optimization_scheduler import OptimizationScheduler

    scheduler = OptimizationScheduler()

    if args.daemon:
        print("Starting optimization scheduler in daemon mode...")
        scheduler.start_scheduler(blocking=True)
    else:
        cycle = scheduler.run_optimization_cycle()
        print(f"\nOptimization cycle completed:")
        print(f"  Tasks: {cycle.tasks_passed}/{cycle.tasks_executed} passed")
        print(f"  Duration: {cycle.duration_seconds:.2f}s")


def cmd_report(args):
    """生成报告"""
    from resources.external.optimization.optimization_scheduler import OptimizationScheduler
    from resources.external.integration.resource_loader import ResourceRegistry

    if args.type == "status":
        registry = ResourceRegistry()
        print(registry.export_summary())
    elif args.type == "optimization":
        scheduler = OptimizationScheduler()
        print(scheduler.generate_optimization_report())
    elif args.type == "updates":
        from resources.external.integration.update_tracker import UpdateTracker
        tracker = UpdateTracker()
        results = tracker.check_registry_updates()
        print(tracker.generate_update_report(results))


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="MSRA External Resources Management CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status command
    status_parser = subparsers.add_parser("status", help="Show resource status")

    # check command
    check_parser = subparsers.add_parser("check", help="Run compatibility check")
    check_parser.add_argument("--package", type=str, help="Specific package to check")

    # update command
    update_parser = subparsers.add_parser("update", help="Check for updates")
    update_parser.add_argument("--package", type=str, help="Specific package to check")

    # optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Run optimization cycle")
    optimize_parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    # report command
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_parser.add_argument(
        "--type",
        type=str,
        choices=["status", "optimization", "updates"],
        default="status",
        help="Report type"
    )

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "optimize":
        cmd_optimize(args)
    elif args.command == "report":
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
