"""
reproducibility_check.py — 结果复现验证模板
============================================
自动重跑分析代码 N 次并检查关键结论一致性

依赖: numpy, pandas
安装: pip install numpy pandas

作者: MSRA Team
版本: 0.1.0
"""

import importlib.util
import json
import os
import subprocess
import sys
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ============================================================================
# 1. Python 脚本复现验证
# ============================================================================


class ReproducibilityChecker:
    """Python 分析脚本复现验证器

    Parameters
    ----------
    script_path : str
        分析脚本路径
    n_runs : int
        重跑次数（默认 3）
    output_dir : str
        输出目录
    key_metrics : Dict[str, Callable]
        关键指标提取函数的字典 {name: function(globals_dict) -> value}
    seed_start : int
        起始种子值
    timeout_sec : int
        每次运行超时（秒）
    """

    def __init__(
        self,
        script_path: str,
        n_runs: int = 3,
        output_dir: str = "reproducibility/",
        key_metrics: Optional[Dict[str, Callable]] = None,
        seed_start: int = 42,
        timeout_sec: int = 300,
    ):
        self.script_path = os.path.abspath(script_path)
        self.n_runs = n_runs
        self.output_dir = output_dir
        self.key_metrics = key_metrics or {}
        self.seed_start = seed_start
        self.timeout_sec = timeout_sec

        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Script not found: {self.script_path}")

        os.makedirs(os.path.join(self.output_dir, "runs"), exist_ok=True)

    def _create_run_script(self, run_num: int) -> str:
        """创建带种子的临时运行脚本"""
        seed = self.seed_start + run_num - 1
        run_dir = os.path.join(self.output_dir, "runs")

        run_script_path = os.path.join(run_dir, f"run_{run_num}.py")
        output_json = os.path.join(run_dir, f"output_{run_num}.json")

        with open(self.script_path, "r", encoding="utf-8") as f:
            original_code = f.read()

        # 注入种子和结果导出代码
        wrapper_code = f"""
import numpy as np
import random

np.random.seed({seed})
random.seed({seed})

__RUN_OUTPUT_FILE__ = r"{output_json}"

# 原始脚本代码
{original_code}

# 导出 metrics
import json
import numpy as np

def _default_serializer(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Type {{type(obj)}} not serializable")

_metrics = {{}}
_globals = globals()
"""
        # 添加指标提取代码
        for metric_name, metric_fn_src in self.key_metrics.items():
            wrapper_code += f"""
try:
    _metrics["{metric_name}"] = {metric_fn_src}
except Exception as _e:
    _metrics["{metric_name}"] = f"ERROR: {{_e}}"
"""

        wrapper_code += """
with open(__RUN_OUTPUT_FILE__, "w") as _f:
    json.dump(_metrics, _f, default=_default_serializer)
"""

        with open(run_script_path, "w", encoding="utf-8") as f:
            f.write(wrapper_code)

        return run_script_path

    def run(self) -> Dict[str, Any]:
        """执行复现验证

        Returns
        -------
        Dict
            包含所有运行结果和分析
        """
        logger.info("=" * 60)
        logger.info("  结果复现验证")
        logger.info("=" * 60)
        logger.info(f"\n脚本: {self.script_path}")
        logger.info(f"运行次数: {self.n_runs}")

        all_metrics = []

        for i in range(1, self.n_runs + 1):
            logger.info(f"\n  Run {i}/{self.n_runs} (seed={self.seed_start + i - 1})...", end=" ")

            run_script = self._create_run_script(i)
            output_json = os.path.join(self.output_dir, "runs", f"output_{i}.json")

            start_time = time.time()
            try:
                result = subprocess.run(
                    [sys.executable, run_script],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_sec,
                )
                elapsed = time.time() - start_time

                if result.returncode != 0:
                    logger.info(f"ERROR (rc={result.returncode})")
                    all_metrics.append({"__error__": result.stderr[-500:] if result.stderr else "Unknown error"})
                elif os.path.exists(output_json):
                    with open(output_json, "r", encoding="utf-8") as f:
                        metrics = json.load(f)
                    all_metrics.append(metrics)
                    logger.info(f"OK ({elapsed:.1f}s)")
                else:
                    logger.info("WARNING: No output")
                    all_metrics.append({"__error__": "No output file generated"})

            except subprocess.TimeoutExpired:
                logger.info(f"TIMEOUT (>{self.timeout_sec}s)")
                all_metrics.append({"__error__": f"Timeout after {self.timeout_sec}s"})
            except Exception as e:
                logger.info(f"ERROR: {e}")
                all_metrics.append({"__error__": str(e)})

        # 分析一致性
        logger.info("\n\n--- 关键参数一致性 ---")

        # 找出所有共同指标
        metric_names = set()
        for m in all_metrics:
            metric_names.update(k for k in m.keys() if not k.startswith("__"))

        rows = []
        for name in sorted(metric_names):
            values = []
            for m in all_metrics:
                v = m.get(name)
                if isinstance(v, (int, float)):
                    values.append(v)

            if len(values) >= 2:
                val_range = max(values) - min(values)
                mean_val = np.mean(values)
                std_val = np.std(values, ddof=1)

                if val_range < 0.005:
                    verdict = "✅ Consistent"
                elif val_range < 0.05:
                    verdict = "⚠️ Minor variation"
                else:
                    verdict = "❌ Inconsistent"

                display_values = [f"{v:.4f}" if isinstance(v, float) else str(v) for v in values]
                rows.append({
                    "Parameter": name,
                    "Mean": f"{mean_val:.4f}",
                    "Range": f"{val_range:.4f}",
                    "SD": f"{std_val:.4f}",
                    "Verdict": verdict,
                })
                logger.info(f"  {name}: range={val_range:.4f}, mean={mean_val:.4f} → {verdict}")

        consistency_df = pd.DataFrame(rows) if rows else pd.DataFrame()

        # 总体判定
        if not rows:
            verdict = "N/A — No numeric metrics found"
        elif all("❌" not in r["Verdict"] for r in rows):
            verdict = "✅ PASS — All key parameters consistent across runs"
        elif sum(1 for r in rows if "❌" in r["Verdict"]) <= len(rows) // 3:
            verdict = "⚠️ CONDITIONAL — Some parameters show variation"
        else:
            verdict = "❌ FAIL — Key results not reproducible"

        logger.info(f"\n--- 结论 ---")
        logger.info(f"  {verdict}")
        logger.info("\n" + "=" * 60)

        return {
            "script": self.script_path,
            "n_runs": self.n_runs,
            "all_metrics": all_metrics,
            "consistency": consistency_df,
            "verdict": verdict,
        }


# ============================================================================
# 2. 简单数值提取帮助函数
# ============================================================================


def extract_from_model(model_obj: Any, attr_name: str) -> float:
    """从模型对象中提取标量属性"""
    val = getattr(model_obj, attr_name, None)
    if val is not None:
        return float(val)
    return float("nan")


def extract_from_dict(d: Dict, key: str) -> float:
    """从字典中提取数值"""
    val = d.get(key)
    if isinstance(val, (int, float)):
        return float(val)
    return float("nan")


# ============================================================================
# 示例
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 模拟测试
    logger.info("=" * 60)
    logger.info("  示例: 生成模拟分析结果并验证复现性")
    logger.info("=" * 60)

    # 创建一个临时测试脚本
    test_script = os.path.join(
        os.path.dirname(__file__), "runs", "_test_analysis.py"
    )
    os.makedirs(os.path.dirname(test_script), exist_ok=True)

    with open(test_script, "w") as f:
        f.write("""
import numpy as np
from sklearn.linear_model import LogisticRegression
import logging

logger = logging.getLogger(__name__)

# 模拟数据
np.random.seed(42)
n = 200
X = np.random.randn(n, 3)
y = (X[:, 0] + 0.5 * X[:, 1] - 0.3 * X[:, 2] + np.random.randn(n) * 0.5 > 0).astype(int)

# 拟合模型
model = LogisticRegression(random_state=42)
model.fit(X, y)

# 提取关键指标
coef = model.coef_[0]
intercept = model.intercept_[0]
score = model.score(X, y)
""")

    # 定义关键指标提取
    key_metrics = {
        "coef_0": "float(__globals__['coef'][0])",
        "coef_1": "float(__globals__['coef'][1])",
        "intercept": "float(__globals__['intercept'])",
        "accuracy": "float(__globals__['score'])",
    }

    checker = ReproducibilityChecker(
        script_path=test_script,
        n_runs=3,
        key_metrics=key_metrics,
        output_dir=os.path.join(os.path.dirname(__file__), "_test_output"),
    )

    report = checker.run()

    if not report["consistency"].empty:
        logger.info("\n一致性表:")
        logger.info(report["consistency"].to_string(index=False))

    logger.info(f"\n结论: {report['verdict']}")
    logger.info("\n✅ 复现验证测试完成")
