#!/usr/bin/env python3
"""
check_sprint_contract.py — Sprint Contract 验证脚本
====================================================
验证 reviewer/writer 合约 JSON 是否符合 Schema 13.1。

用法: python scripts/check_sprint_contract.py <contract.json>

作者: MSRA Team
版本: 0.1.0
"""
import sys
import json
from pathlib import Path


REQUIRED_FIELDS = ["panel_size", "acceptance_dimensions", "failure_conditions"]
VALID_SEVERITIES = ["critical", "major", "minor", "info"]


def validate_contract(contract_path: str) -> dict:
    """验证单个合约文件"""
    path = Path(contract_path)
    if not path.exists():
        return {"file": contract_path, "status": "ERROR", "message": "File not found"}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"file": contract_path, "status": "ERROR", "message": f"Invalid JSON: {e}"}

    issues = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            issues.append(f"Missing required field: {field}")

    # Validate failure_conditions
    if "failure_conditions" in data:
        for i, fc in enumerate(data["failure_conditions"]):
            if "severity" not in fc:
                issues.append(f"failure_conditions[{i}]: missing 'severity'")
            elif fc["severity"] not in VALID_SEVERITIES:
                issues.append(f"failure_conditions[{i}]: invalid severity '{fc['severity']}'")

    # Validate panel_size
    if "panel_size" in data:
        if not isinstance(data["panel_size"], int) or data["panel_size"] < 1:
            issues.append(f"panel_size must be positive integer, got {data['panel_size']}")

    return {
        "file": contract_path,
        "status": "OK" if not issues else "FAIL",
        "issues": issues,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_sprint_contract.py <contract.json>")
        return 1

    for contract_path in sys.argv[1:]:
        result = validate_contract(contract_path)
        status_icon = "✅" if result["status"] == "OK" else "❌"
        print(f"{status_icon} {result['file']}: {result['status']}")
        if "issues" in result and result["issues"]:
            for issue in result["issues"]:
                print(f"   - {issue}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
