#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lint: quality-gate item-count consistency.

After Sprint 1 extracted the blocking quality-gate definitions from
pipeline/SKILL.md to shared/quality_gates/gate-*.md, this script verifies
consistency across two layers:

Layer 1 — Gate file internal consistency (shared/quality_gates/gate-*.md):
  For each gate file (gate-data.md / gate-sap.md / gate-results.md):
    a. Count of checklist table rows (| 1 | ... |, | 2 | ... |, ...)
    b. The "N 项" claim in the "## 检查清单 (N 项)" header
    c. Both must match the expected count (9 / 8 / 14)

Layer 2 — Pipeline SKILL.md reference consistency (skills/pipeline/SKILL.md):
  For each Stage X.5 block:
    a. The block must reference the correct gate-*.md file
    b. The "（N 项检查清单 + 判定规则）" claim in the reference must match
  Also checks the §1 Pipeline Stages flow chart "N 项检查" claims where present.

Fails (exit 1) with a clear message if any source disagrees, so a future edit
that adds/removes a checklist item but forgets to update the prose is caught in CI.

Intended to be invoked with no args (defaults to repo-root-relative paths),
or with the pipeline SKILL.md path as the first arg.
"""
from __future__ import annotations

import os
import re
import sys

# Expected gate definitions: (stage, gate_filename, expected_item_count)
GATES = [
    ("1.5", "gate-data.md", 9),
    ("2.5", "gate-sap.md", 8),
    ("3.5", "gate-results.md", 14),
]


def check_gate_file(gate_path: str, expected_count: int) -> tuple[int, int, list[str]]:
    """
    Check a single gate-*.md file.

    Returns (actual_count, header_claim, errors).
    """
    with open(gate_path, encoding="utf-8-sig") as fh:
        content = fh.read()

    errors: list[str] = []
    basename = os.path.basename(gate_path)

    # --- 1. Count actual checklist items ---
    # Checklist table rows look like: "| 1 | 检查项 | 通过标准 | 关键项 |"
    # The header row "| # | 检查项 |" and separator "|---|---|" are excluded
    # because they don't start with a digit after the pipe.
    item_matches = re.findall(r"^\|\s*(\d+)\s*\|", content, re.M)
    if item_matches:
        numbers = sorted(int(n) for n in item_matches)
        # Checklist should be consecutive 1..N; the count is the max number
        actual_count = max(numbers)
        # Verify consecutiveness (1, 2, ..., N)
        expected_seq = list(range(1, actual_count + 1))
        if numbers != expected_seq:
            errors.append(
                f"  {basename}: checklist item numbers are not consecutive "
                f"1..{actual_count} (got {numbers})"
            )
    else:
        actual_count = 0

    # --- 2. Check "N 项" claim in the header ---
    # Pattern: "## 检查清单 (N 项)"
    m = re.search(r"##\s*检查清单\s*\(\s*(\d+)\s*项\s*\)", content)
    header_claim = int(m.group(1)) if m else 0
    if header_claim == 0:
        errors.append(
            f"  {basename}: missing '## 检查清单 (N 项)' header claim"
        )

    # --- 3. Cross-check all three values ---
    if actual_count != expected_count:
        errors.append(
            f"  {basename}: actual checklist items={actual_count}, "
            f"expected={expected_count}"
        )
    if header_claim != expected_count:
        errors.append(
            f"  {basename}: header claims '({header_claim} 项)' but "
            f"expected={expected_count}"
        )
    if actual_count != header_claim and actual_count > 0 and header_claim > 0:
        errors.append(
            f"  {basename}: actual={actual_count} != header claim={header_claim}"
        )

    return actual_count, header_claim, errors


def check_pipeline_references(
    pipeline_path: str,
) -> list[str]:
    """
    Check pipeline/SKILL.md Stage X.5 blocks reference the correct gate file
    with the correct item count.
    """
    with open(pipeline_path, encoding="utf-8-sig") as fh:
        content = fh.read()

    errors: list[str] = []

    for stage, gate_file, expected_count in GATES:
        # Locate the Stage X.5 block (up to the next ### or end of file)
        block = re.search(
            r"### Stage " + re.escape(stage) + r".*?(?=###|\Z)",
            content,
            re.S,
        )
        if not block:
            errors.append(
                f"  pipeline/SKILL.md: Stage {stage} block not found"
            )
            continue

        block_text = block.group(0)

        # (a) The block must reference the correct gate-*.md file
        if gate_file not in block_text:
            errors.append(
                f"  pipeline/SKILL.md Stage {stage}: "
                f"missing reference to '{gate_file}'"
            )

        # (b) The "（N 项检查清单 + 判定规则）" claim must match
        #   Pattern: "（9 项检查清单 + 判定规则）"
        m = re.search(r"（\s*(\d+)\s*项检查清单", block_text)
        if m:
            ref_claim = int(m.group(1))
            if ref_claim != expected_count:
                errors.append(
                    f"  pipeline/SKILL.md Stage {stage}: "
                    f"reference claims '（{ref_claim} 项检查清单...）' but "
                    f"expected={expected_count}"
                )
        else:
            errors.append(
                f"  pipeline/SKILL.md Stage {stage}: "
                f"missing '（N 项检查清单...）' claim in gate reference"
            )

    return errors


def check_pipeline_flowchart(
    pipeline_path: str,
) -> list[str]:
    """
    Check the §1 Pipeline Stages flow chart "N 项检查" claims.

    Only Stage 1.5 and Stage 3.5 have explicit "N 项检查" in the flow chart;
    Stage 2.5 uses different wording ("+ 变量构造逻辑检查"), so it is skipped.
    """
    with open(pipeline_path, encoding="utf-8-sig") as fh:
        content = fh.read()

    errors: list[str] = []

    # Flow chart lines look like:
    #   │  9 项检查 → ❌退回 Stage 1 / ✅进入 Stage 2                  │
    #   │  14 项检查 → ❌退回 Stage 3 / ✅进入 Stage 4                 │
    # Stage 2.5 has no "N 项检查" in the flow chart, so we only check 1.5 and 3.5.
    flowchart_gates = [
        ("1.5", 9, "退回 Stage 1"),
        ("3.5", 14, "退回 Stage 3"),
    ]

    for stage, expected_count, nearby_text in flowchart_gates:
        # Find "N 项检查" lines near the stage
        # We look for a line containing "项检查" and the stage-specific nearby text
        found = False
        for line in content.splitlines():
            if "项检查" in line and nearby_text in line:
                m = re.search(r"(\d+)\s*项检查", line)
                if m:
                    found = True
                    claim = int(m.group(1))
                    if claim != expected_count:
                        errors.append(
                            f"  pipeline/SKILL.md §1 flow chart Stage {stage}: "
                            f"claims '{claim} 项检查' but expected={expected_count}"
                        )
                break
        if not found:
            errors.append(
                f"  pipeline/SKILL.md §1 flow chart Stage {stage}: "
                f"missing 'N 项检查' claim (expected {expected_count})"
            )

    return errors


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gates_dir = os.path.join(repo_root, "src", "shared", "quality_gates")
    default_pipeline = os.path.join(repo_root, "skills", "pipeline", "SKILL.md")

    # Allow optional pipeline path arg for ad-hoc testing
    pipeline_path = sys.argv[1] if len(sys.argv) > 1 else default_pipeline

    all_errors: list[str] = []
    gate_results: list[tuple[str, str, int, int, int]] = []

    # === Layer 1: Gate file internal consistency ===
    for stage, gate_file, expected_count in GATES:
        gate_path = os.path.join(gates_dir, gate_file)
        if not os.path.exists(gate_path):
            all_errors.append(
                f"  gate file not found: {gate_path}"
            )
            gate_results.append((stage, gate_file, expected_count, 0, 0))
            continue
        actual, header, errs = check_gate_file(gate_path, expected_count)
        gate_results.append((stage, gate_file, expected_count, actual, header))
        all_errors.extend(errs)

    # === Layer 2: Pipeline SKILL.md reference consistency ===
    if os.path.exists(pipeline_path):
        all_errors.extend(check_pipeline_references(pipeline_path))
        all_errors.extend(check_pipeline_flowchart(pipeline_path))
    else:
        all_errors.append(
            f"  pipeline SKILL.md not found: {pipeline_path}"
        )

    # === Print results ===
    print("=== Layer 1: Gate file internal consistency ===")
    for stage, gate_file, expected, actual, header in gate_results:
        ok = expected == actual == header and actual > 0
        status = "OK " if ok else "BAD"
        print(
            f"  [{status}] Stage {stage} {gate_file}: "
            f"expected={expected} actual={actual} header={header}"
        )

    print("\n=== Layer 2: Pipeline SKILL.md reference consistency ===")
    if all_errors:
        for err in all_errors:
            print(err)
        print(
            f"\nFAIL: {len(all_errors)} inconsistency(ies) found.\n"
            "  When you add/remove a checklist item, update ALL of:\n"
            "  1. The gate-*.md checklist table (shared/quality_gates/gate-*.md)\n"
            "  2. The gate-*.md header '## 检查清单 (N 项)' claim\n"
            "  3. The pipeline/SKILL.md Stage X.5 block reference '（N 项检查清单...）'\n"
            "  4. The pipeline/SKILL.md §1 flow chart 'N 项检查' claim (Stage 1.5/3.5)"
        )
        return 1

    print("\nOK: all quality-gate item counts consistent across gate files and pipeline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
