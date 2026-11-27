#!/usr/bin/env python3
"""Run offline regression and structure tests for this skill."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(root / "tests"),
            "-v",
        ],
        cwd=root,
        check=False,
    )
    if result.returncode:
        return result.returncode

    eval_path = root / "evals" / "cases.jsonl"
    count = 0
    identifiers: set[str] = set()
    try:
        for number, line in enumerate(
            eval_path.read_text(encoding="utf-8").splitlines(),
            1,
        ):
            if not line.strip():
                continue
            case = json.loads(line)
            for key in ("id", "mode", "prompt", "must_do", "must_not"):
                if key not in case:
                    raise ValueError(f"line {number} lacks '{key}'")
            if case["id"] in identifiers:
                raise ValueError(f"duplicate eval ID: {case['id']}")
            identifiers.add(case["id"])
            count += 1
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"Eval validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Validated {count} behavioral eval case(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
