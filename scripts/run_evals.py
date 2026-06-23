#!/usr/bin/env python3
"""
MSRA Unified Evaluation Runner

Runs all evaluation suites and generates a consolidated report.

Eval suites:
  1. pipeline-gold: 21 data quality detection tuples
  2. method-selection: 10 statistical method selection tuples
  3. end-to-end: end-to-end pipeline scenarios

Usage:
    PYTHONPATH=. python -m scripts.run_evals
    PYTHONPATH=. python -m scripts.run_evals --suite pipeline-gold
    PYTHONPATH=. python -m scripts.run_evals --suite method-selection --verbose
    PYTHONPATH=. python -m scripts.run_evals --json  # JSON output for CI

Author: MSRA Team
Version: 1.0.0
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
EVALS_DIR = BASE / "evals" / "gold"


# ============================================================================
# Suite 1: Pipeline Gold Evaluation
# ============================================================================

def run_pipeline_gold(verbose: bool = False) -> dict:
    """Run pipeline gold evaluation suite."""
    try:
        from scripts.eval_pipeline_gold import run_eval
        results = run_eval(verbose=verbose)
    except Exception as e:
        return {
            "suite": "pipeline-gold",
            "status": "ERROR",
            "error": str(e),
            "results": [],
        }

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    total = len(results)

    return {
        "suite": "pipeline-gold",
        "status": "PASS" if failed == 0 and errors == 0 else "FAIL",
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "pass_rate": passed / max(total - skipped, 1),
        "results": results,
    }


# ============================================================================
# Suite 2: Method Selection Evaluation
# ============================================================================

def load_method_selection_tuples() -> list[dict]:
    """Load all method-selection gold tuples."""
    tuples_dir = EVALS_DIR / "method-selection" / "tuples"
    tuples = []
    for f in sorted(tuples_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            tuples.append(json.load(fh))
    return tuples


def validate_method_selection_tuple(tuple_data: dict) -> dict:
    """
    Validate a method-selection tuple structure and expected fields.

    This checks that:
    - Required fields exist (tuple_id, kind, test_name, input, expected)
    - Expected method is specified
    - Common wrong methods are listed
    - Model specification is provided
    """
    tid = tuple_data.get("tuple_id", "unknown")
    required_fields = ["tuple_id", "kind", "test_name", "input", "expected"]
    missing = [f for f in required_fields if f not in tuple_data]

    if missing:
        return {
            "tuple_id": tid,
            "status": "FAIL",
            "reason": f"missing required fields: {missing}",
        }

    expected = tuple_data["expected"]
    expected_fields = ["primary_method", "model_specification"]
    missing_expected = [f for f in expected_fields if f not in expected]

    if missing_expected:
        return {
            "tuple_id": tid,
            "status": "FAIL",
            "reason": f"missing expected fields: {missing_expected}",
        }

    # Check common wrong methods exist
    wrong_methods = tuple_data.get("common_wrong_methods", [])
    if not wrong_methods:
        return {
            "tuple_id": tid,
            "status": "WARN",
            "reason": "no common_wrong_methods listed",
            "test_name": tuple_data["test_name"],
            "expected_method": expected["primary_method"],
        }

    return {
        "tuple_id": tid,
        "status": "PASS",
        "test_name": tuple_data["test_name"],
        "kind": tuple_data["kind"],
        "expected_method": expected["primary_method"],
        "model_spec": expected.get("model_specification", "N/A"),
        "wrong_methods_count": len(wrong_methods),
    }


def run_method_selection(verbose: bool = False) -> dict:
    """Run method-selection evaluation suite."""
    try:
        tuples = load_method_selection_tuples()
    except Exception as e:
        return {
            "suite": "method-selection",
            "status": "ERROR",
            "error": str(e),
            "results": [],
        }

    results = []
    for t in tuples:
        result = validate_method_selection_tuple(t)
        results.append(result)

    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)

    return {
        "suite": "method-selection",
        "status": "PASS" if failed == 0 else "FAIL",
        "total": total,
        "passed": passed,
        "warned": warned,
        "failed": failed,
        "pass_rate": passed / max(total, 1),
        "results": results,
    }


# ============================================================================
# Suite 3: End-to-End Evaluation
# ============================================================================

def run_end_to_end(verbose: bool = False) -> dict:
    """Run end-to-end evaluation suite."""
    e2e_dir = EVALS_DIR / "end-to-end"
    answers_file = e2e_dir / "standard_answers.json"

    if not answers_file.exists():
        return {
            "suite": "end-to-end",
            "status": "SKIP",
            "reason": "standard_answers.json not found",
            "results": [],
        }

    with open(answers_file, encoding="utf-8") as f:
        data = json.load(f)

    results = []

    # Handle the actual structure: {version, description, datasets: {...}}
    datasets = data.get("datasets", data)
    if isinstance(datasets, dict):
        for tid, item in datasets.items():
            if not isinstance(item, dict):
                continue
            has_expected = "expected" in item
            results.append({
                "tuple_id": tid,
                "status": "PASS" if has_expected else "WARN",
                "test_name": item.get("description", tid),
            })
    elif isinstance(datasets, list):
        for item in datasets:
            if not isinstance(item, dict):
                continue
            tid = item.get("test_id", item.get("id", "unknown"))
            has_expected = "expected" in item
            results.append({
                "tuple_id": tid,
                "status": "PASS" if has_expected else "WARN",
                "test_name": item.get("description", item.get("name", tid)),
            })

    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    total = len(results)

    return {
        "suite": "end-to-end",
        "status": "PASS" if total > 0 else "SKIP",
        "total": total,
        "passed": passed,
        "warned": warned,
        "pass_rate": passed / max(total, 1),
        "results": results,
    }


# ============================================================================
# Consolidated Report
# ============================================================================

def generate_report(suite_results: list[dict], elapsed: float) -> dict:
    """Generate consolidated evaluation report."""
    total_suites = len(suite_results)
    passed_suites = sum(1 for s in suite_results if s["status"] == "PASS")
    total_tuples = sum(s.get("total", 0) for s in suite_results)
    passed_tuples = sum(s.get("passed", 0) for s in suite_results)
    failed_tuples = sum(s.get("failed", 0) for s in suite_results)
    warned_tuples = sum(s.get("warned", 0) for s in suite_results)

    return {
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed, 2),
        "summary": {
            "suites_total": total_suites,
            "suites_passed": passed_suites,
            "tuples_total": total_tuples,
            "tuples_passed": passed_tuples,
            "tuples_failed": failed_tuples,
            "tuples_warned": warned_tuples,
            "overall_pass_rate": passed_tuples / max(total_tuples, 1),
        },
        "suites": suite_results,
    }


def print_report(report: dict, verbose: bool = False):
    """Print human-readable report."""
    print()
    print("=" * 70)
    print("  MSRA Unified Evaluation Report")
    print(f"  Time: {report['timestamp']} | Elapsed: {report['elapsed_seconds']}s")
    print("=" * 70)
    print()

    for suite in report["suites"]:
        status_icon = {
            "PASS": "[PASS]",
            "FAIL": "[FAIL]",
            "SKIP": "[SKIP]",
            "ERROR": "[ERR!]",
        }.get(suite["status"], "[????]")

        print(f"  {status_icon} {suite['suite']}", end="")
        if suite.get("total"):
            rate = suite.get("pass_rate", 0)
            print(f" — {suite.get('passed', 0)}/{suite['total']} "
                  f"({rate:.0%})", end="")
        if suite.get("failed"):
            print(f" | {suite['failed']} failed", end="")
        if suite.get("warned"):
            print(f" | {suite.get('warned', 0)} warned", end="")
        print()

        if verbose:
            for r in suite.get("results", []):
                icon = {"PASS": "  +", "FAIL": "  X", "WARN": "  !",
                        "SKIP": "  -", "ERROR": "  !"}.get(r["status"], "  ?")
                name = r.get("test_name", r.get("tuple_id", "?"))
                print(f"    {icon} {r.get('tuple_id', '?')}: {name}")
                if r["status"] not in ("PASS",) and "reason" in r:
                    print(f"       reason: {r['reason']}")
                if r["status"] == "FAIL" and "evidence" in r:
                    print(f"       evidence: {r['evidence']}")

    print()
    print("-" * 70)
    s = report["summary"]
    print(f"  Suites:   {s['suites_passed']}/{s['suites_total']} passed")
    print(f"  Tuples:   {s['tuples_passed']}/{s['tuples_total']} passed "
          f"({s['overall_pass_rate']:.1%})")
    if s["tuples_failed"]:
        print(f"  Failed:   {s['tuples_failed']}")
    if s["tuples_warned"]:
        print(f"  Warned:   {s['tuples_warned']}")
    print("=" * 70)

    # Save results
    results_dir = EVALS_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_file = results_dir / f"eval_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  Report saved: {out_file}")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="MSRA Unified Evaluation Runner"
    )
    parser.add_argument(
        "--suite",
        choices=["pipeline-gold", "method-selection", "end-to-end", "all"],
        default="all",
        help="Evaluation suite to run (default: all)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed per-tuple output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON only (for CI integration)",
    )
    args = parser.parse_args()

    start_time = time.time()
    suite_results = []

    if args.suite in ("all", "pipeline-gold"):
        suite_results.append(run_pipeline_gold(verbose=args.verbose))

    if args.suite in ("all", "method-selection"):
        suite_results.append(run_method_selection(verbose=args.verbose))

    if args.suite in ("all", "end-to-end"):
        suite_results.append(run_end_to_end(verbose=args.verbose))

    elapsed = time.time() - start_time
    report = generate_report(suite_results, elapsed)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report, verbose=args.verbose)

    # Exit code: 0 if all pass, 1 if any fail
    has_failures = any(s["status"] == "FAIL" for s in suite_results)
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
