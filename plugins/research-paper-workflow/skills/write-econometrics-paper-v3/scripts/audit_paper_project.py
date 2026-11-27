#!/usr/bin/env python3
"""Run a read-only structural audit of a managed manuscript project."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _paperlib import STATE_FILENAMES, audit_project, render_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a LaTeX or Markdown econometrics paper project."
    )
    parser.add_argument("paper_dir", type=Path)
    parser.add_argument("--main", default=None)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--claim-coverage", action="store_true", help="Add a bounded advisory scan for potentially unregistered manuscript claims.")
    parser.add_argument("--coverage-path", action="append", default=None, help="Project-relative manuscript path to scan; repeat for changed files. Requires --claim-coverage.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
    )
    args = parser.parse_args()
    if args.coverage_path and not args.claim_coverage:
        parser.error("--coverage-path requires --claim-coverage")
    return args


def main() -> int:
    args = parse_args()
    try:
        if args.claim_coverage:
            # The legacy audit reads these before returning its resolved main file.
            # Check containment before those reads, including automatic TeX discovery.
            root = args.paper_dir.resolve()
            managed = [root / ".paper", *(root / ".paper" / name for name in STATE_FILENAMES), *root.glob("*.tex")]
            for path in managed:
                if not path.resolve().is_relative_to(root):
                    raise ValueError("Coverage preflight: input escapes project: " + str(path))
        report = audit_project(
            args.paper_dir,
            explicit_main=args.main,
            release=args.release,
        )
        if args.claim_coverage:
            from claim_coverage import scan_project
            report["claim_coverage"] = scan_project(args.paper_dir, main=report.get("main_file") or args.main, paths=args.coverage_path)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_report(report), end="")
        if args.claim_coverage:
            from claim_coverage import render_report as render_coverage
            print("\n" + render_coverage(report["claim_coverage"]))
    if args.claim_coverage and report["claim_coverage"]["counts"]["error"]:
        return 2
    return 1 if report["counts"]["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
