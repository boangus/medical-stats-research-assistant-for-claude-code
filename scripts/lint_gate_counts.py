#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lint: quality-gate item-count consistency in skills/pipeline/SKILL.md.

For each blocking quality gate (Stage 1.5 / 2.5 / 3.5), assert that three
sources agree:

  1. The actual checklist  (count of "  □ N." lines in the Stage block)
  2. The Stage header claim (the "N 项" token nearest the block header)
  3. The §4.1 M-table row claim (the "N 项" token in the "| Mx | Stage x.5 ... |" row)

Fails (exit 1) with a clear message if any of these disagree, so a future
edit that adds/removes a checklist item but forgets to update the prose is
caught in CI.

Intended to be invoked with the pipeline SKILL.md path, or with no args
(defaults to skills/pipeline/SKILL.md relative to the repo root).
"""
from __future__ import annotations

import os
import re
import sys


def parse(path: str) -> list[tuple[str, int, int, int]]:
    """Return [(stage, checklist_count, stage_claim, mtable_claim), ...]."""
    with open(path, encoding="utf-8-sig") as fh:
        content = fh.read()

    results = []
    for stage in ["1.5", "2.5", "3.5"]:
        # --- 1. actual checklist count inside the Stage block ---
        block = re.search(
            r"### Stage " + stage + r".*?(?=###|\Z)", content, re.S
        )
        if not block:
            raise SystemExit(f"FATAL: Stage {stage} block not found in {path}")
        checklist = re.findall(r"^\s+\u25a1 (\d+)\.", block.group(0), re.M)
        # consecutive 1..N, take the max as the count
        checklist_count = max(int(n) for n in checklist) if checklist else 0

        # --- 2. the "N 项" claim in the Stage block header/prose ---
        #   look for "阻断检查清单 (N 项)" first, else first "N 项检查" in block
        m = re.search(r"\((\d+)\s*\u9879\)", block.group(0))
        if m:
            stage_claim = int(m.group(1))
        else:
            m = re.search(r"(\d+)\s*\u9879\u68c0\u67e5", block.group(0))  # N 项检查
            stage_claim = int(m.group(1)) if m else 0

        # --- 3. the "N 项" claim in the §4.1 GATE-table row for this stage ---
        #   row looks like: | GATE-01 | Stage 1.5 通过后 | ... | 9 项门闸检查结果 + ... |
        mtable_claim = 0
        for line in content.splitlines():
            if re.match(r"\| GATE-\d+ \|", line) and f"Stage {stage}" in line:
                m2 = re.search(r"(\d+)\s*\u9879", line)
                if m2:
                    mtable_claim = int(m2.group(1))
                break

        results.append((stage, checklist_count, stage_claim, mtable_claim))
    return results


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default = os.path.join(repo_root, "skills", "pipeline", "SKILL.md")
    path = sys.argv[1] if len(sys.argv) > 1 else default

    rows = parse(path)
    failures = []
    for stage, checklist, stage_claim, mtable_claim in rows:
        ok = checklist == stage_claim == mtable_claim and checklist > 0
        status = "OK " if ok else "BAD"
        print(
            f"  [{status}] Stage {stage}: "
            f"checklist={checklist} header={stage_claim} M-table={mtable_claim}"
        )
        if not ok:
            failures.append(stage)

    if failures:
        print(
            f"\nFAIL: gate item-count inconsistency in Stage(s): "
            f"{', '.join(failures)}\n"
            f"  When you add/remove a checklist item, update BOTH the\n"
            f"  Stage header ('N 项') AND the §4.1 M-table row."
        )
        return 1
    print("\nOK: all quality-gate item counts consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
