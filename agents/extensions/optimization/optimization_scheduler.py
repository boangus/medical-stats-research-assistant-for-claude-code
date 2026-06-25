"""
Continuous Optimization Scheduler - 持续优化调度器

定期执行资源扫描、兼容性检查和更新追踪。
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import schedule
import time
import threading


@dataclass
class OptimizationTask:
    """优化任务"""
    name: str
    description: str
    script_path: str
    frequency: str  # "daily", "weekly", "monthly"
    last_run: Optional[str]
    last_status: str  # "success", "failed", "pending"
    last_output: Optional[str]
    next_run: Optional[str]


@dataclass
class OptimizationCycle:
    """优化循环结果"""
    cycle_id: str
    timestamp: str
    tasks_executed: int
    tasks_passed: int
    tasks_failed: int
    duration_seconds: float
    details: List[Dict]


class OptimizationScheduler:
    """持续优化调度器"""

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        tasks_config_path: Optional[Path] = None
    ):
        """初始化优化调度器

        Args:
            base_dir: 基础目录
            tasks_config_path: 任务配置文件路径
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent
        self.base_dir = base_dir

        if tasks_config_path is None:
            tasks_config_path = self.base_dir / "resources" / "external" / "optimization" / "tasks_config.json"
        self.tasks_config_path = tasks_config_path

        self._tasks: List[OptimizationTask] = []
        self._cycles: List[OptimizationCycle] = []
        self._load_tasks()

    def _load_tasks(self):
        """加载任务配置"""
        if self.tasks_config_path.exists():
            with open(self.tasks_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                for task_data in config.get("tasks", []):
                    self._tasks.append(OptimizationTask(**task_data))
        else:
            self._tasks = self._get_default_tasks()

    def _get_default_tasks(self) -> List[OptimizationTask]:
        """获取默认任务列表"""
        return [
            OptimizationTask(
                name="resource_registry_check",
                description="Check resource registry integrity",
                script_path="agents/extensions/integration/resource_loader.py",
                frequency="weekly",
                last_run=None,
                last_status="pending",
                last_output=None,
                next_run=None
            ),
            OptimizationTask(
                name="compatibility_check",
                description="Check all integrated resources compatibility",
                script_path="agents/extensions/integration/compatibility_checker.py",
                frequency="weekly",
                last_run=None,
                last_status="pending",
                last_output=None,
                next_run=None
            ),
            OptimizationTask(
                name="update_scan",
                description="Scan for resource updates",
                script_path="agents/extensions/integration/update_tracker.py",
                frequency="monthly",
                last_run=None,
                last_status="pending",
                last_output=None,
                next_run=None
            ),
            OptimizationTask(
                name="test_suite",
                description="Run complete test suite",
                script_path="tests/",
                frequency="daily",
                last_run=None,
                last_status="pending",
                last_output=None,
                next_run=None
            ),
        ]

    def _calculate_next_run(self, task: OptimizationTask) -> str:
        """计算下次运行时间"""
        frequency_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30
        }
        days = frequency_map.get(task.frequency, 7)
        next_date = datetime.now() + timedelta(days=days)
        return next_date.isoformat()

    def _run_task(self, task: OptimizationTask) -> Dict:
        """执行单个任务

        Args:
            task: 优化任务

        Returns:
            执行结果
        """
        start_time = time.time()
        result = {
            "task_name": task.name,
            "started_at": datetime.now().isoformat(),
            "status": "failed",
            "output": None,
            "error": None
        }

        try:
            script_path = self.base_dir / task.script_path

            if task.name == "test_suite":
                # 运行pytest
                proc = subprocess.run(
                    ["pytest", str(self.base_dir / "tests"), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(self.base_dir)
                )
                result["status"] = "passed" if proc.returncode == 0 else "failed"
                result["output"] = proc.stdout[-5000:] if proc.stdout else ""  # 限制输出长度
                if proc.stderr:
                    result["error"] = proc.stderr[-2000:]
            else:
                # 运行Python脚本
                proc = subprocess.run(
                    ["python", str(script_path), "--all", "--output", "/tmp/output.json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self.base_dir)
                )
                result["status"] = "passed" if proc.returncode == 0 else "failed"
                result["output"] = proc.stdout[-5000:] if proc.stdout else ""
                if proc.stderr:
                    result["error"] = proc.stderr[-2000:]

        except subprocess.TimeoutExpired:
            result["status"] = "failed"
            result["error"] = "Task timed out"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        result["duration"] = time.time() - start_time
        return result

    def run_optimization_cycle(self) -> OptimizationCycle:
        """运行一次完整的优化循环

        Returns:
            优化循环结果
        """
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = time.time()

        print(f"Starting optimization cycle: {cycle_id}")

        cycle_result = OptimizationCycle(
            cycle_id=cycle_id,
            timestamp=datetime.now().isoformat(),
            tasks_executed=0,
            tasks_passed=0,
            tasks_failed=0,
            duration_seconds=0,
            details=[]
        )

        for task in self._tasks:
            print(f"  Executing: {task.name}")
            cycle_result.tasks_executed += 1

            task_result = self._run_task(task)
            cycle_result.details.append(task_result)

            # 更新任务状态
            task.last_run = datetime.now().isoformat()
            task.last_status = task_result["status"]
            task.last_output = task_result.get("output")
            task.next_run = self._calculate_next_run(task)

            if task_result["status"] == "passed":
                cycle_result.tasks_passed += 1
                print(f"    ✓ Passed")
            else:
                cycle_result.tasks_failed += 1
                print(f"    ✗ Failed: {task_result.get('error', 'Unknown error')}")

        cycle_result.duration_seconds = time.time() - start_time

        print(f"\nCycle completed: {cycle_result.tasks_passed}/{cycle_result.tasks_executed} passed")
        print(f"Duration: {cycle_result.duration_seconds:.2f}s")

        # 保存周期结果
        self._cycles.append(cycle_result)
        self._save_tasks()

        return cycle_result

    def _save_tasks(self):
        """保存任务配置"""
        config = {
            "tasks": [
                {
                    **asdict(task),
                    "last_output": task.last_output[-1000:] if task.last_output else None  # 限制保存的输出长度
                }
                for task in self._tasks
            ]
        }
        self.tasks_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tasks_config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def get_task_status(self) -> List[Dict]:
        """获取所有任务状态"""
        return [asdict(task) for task in self._tasks]

    def get_optimization_history(self) -> List[Dict]:
        """获取优化历史"""
        return [asdict(cycle) for cycle in self._cycles[-10:]]  # 最近10次

    def generate_optimization_report(self) -> str:
        """生成优化报告"""
        tasks = self.get_task_status()
        history = self.get_optimization_history()

        lines = [
            "# Continuous Optimization Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Task Status",
            "",
            "| Task | Frequency | Last Run | Status | Next Run |",
            "|------|-----------|----------|--------|----------|"
        ]

        for task in tasks:
            lines.append(
                f"| {task['name']} | {task['frequency']} | "
                f"{task['last_run'][:10] if task['last_run'] else 'Never'} | "
                f"{task['last_status']} | "
                f"{task['next_run'][:10] if task['next_run'] else 'N/A'} |"
            )

        lines.extend(["", "## Recent Cycles", ""])

        for cycle in reversed(history):
            lines.append(
                f"- **{cycle['cycle_id']}** ({cycle['timestamp'][:10]}): "
                f"{cycle['tasks_passed']}/{cycle['tasks_executed']} passed "
                f"({cycle['duration_seconds']:.1f}s)"
            )

        return "\n".join(lines)

    def start_scheduler(self, blocking: bool = False):
        """启动调度器

        Args:
            blocking: 是否阻塞模式
        """
        print("Starting optimization scheduler...")

        # 设置定时任务
        schedule.every().day.at("02:00").do(self._scheduled_daily)
        schedule.every().monday.at("03:00").do(self._scheduled_weekly)
        schedule.every().month().do(self._scheduled_monthly)

        if blocking:
            while True:
                schedule.run_pending()
                time.sleep(60)
        else:
            # 立即运行一次
            self.run_optimization_cycle()

    def _scheduled_daily(self):
        """每日定时任务"""
        print("Running daily optimization...")
        self.run_optimization_cycle()

    def _scheduled_weekly(self):
        """每周定时任务"""
        print("Running weekly optimization...")
        self.run_optimization_cycle()

    def _scheduled_monthly(self):
        """每月定时任务"""
        print("Running monthly optimization...")
        self.run_optimization_cycle()


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Optimization Scheduler CLI")
    parser.add_argument("--run", action="store_true", help="Run optimization cycle now")
    parser.add_argument("--status", action="store_true", help="Show task status")
    parser.add_argument("--history", action="store_true", help="Show optimization history")
    parser.add_argument("--report", action="store_true", help="Generate optimization report")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()
    scheduler = OptimizationScheduler()

    if args.run:
        cycle = scheduler.run_optimization_cycle()
        output = json.dumps(asdict(cycle), indent=2, ensure_ascii=False)
    elif args.status:
        tasks = scheduler.get_task_status()
        output = json.dumps(tasks, indent=2, ensure_ascii=False)
    elif args.history:
        history = scheduler.get_optimization_history()
        output = json.dumps(history, indent=2, ensure_ascii=False)
    elif args.report:
        output = scheduler.generate_optimization_report()
    else:
        output = scheduler.generate_optimization_report()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
