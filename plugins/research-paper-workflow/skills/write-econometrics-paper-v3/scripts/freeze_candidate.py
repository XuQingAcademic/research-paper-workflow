#!/usr/bin/env python3
"""Freeze the exact managed manuscript candidate after a clean draft audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _paperlib import (
    audit_project,
    load_json_yaml,
    utc_now,
    write_json_yaml,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record a SHA-256 fingerprint for the current manuscript candidate."
    )
    parser.add_argument("paper_dir", type=Path)
    parser.add_argument("--main", default=None)
    parser.add_argument("--frozen-by", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.paper_dir.resolve()
    state_path = root / ".paper" / "paper_state.yaml"
    if not state_path.is_file():
        print("Freeze failed: .paper/paper_state.yaml is missing.", file=sys.stderr)
        return 2
    try:
        report = audit_project(
            root,
            explicit_main=args.main,
            release=False,
        )
        if report["counts"]["error"]:
            print(
                "Freeze refused: resolve draft-audit errors before freezing.",
                file=sys.stderr,
            )
            for item in report["issues"]:
                if item["severity"] == "error":
                    print(
                        f"- {item['code']}: {item['message']}",
                        file=sys.stderr,
                    )
            return 1
        state = load_json_yaml(state_path)
        release = state.setdefault("release", {})
        release.update(
            {
                "candidate_sha256": report["candidate_sha256"],
                "candidate_files": report["managed_files"],
                "frozen_at": utc_now(),
                "frozen_by": args.frozen_by,
                "audit_errors": report["counts"]["error"],
                "audit_warnings": report["counts"]["warning"],
                "human_approved": False,
                "human_approved_by": "",
                "human_approved_at": "",
            }
        )
        write_json_yaml(state_path, state)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Freeze failed: {exc}", file=sys.stderr)
        return 2
    print(f"Candidate frozen: {report['candidate_sha256']}")
    print(
        "Human approval remains false; an accountable author must set it after reviewing the exact candidate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
