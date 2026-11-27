#!/usr/bin/env python3
"""Check citation-key and structured verification records without network access."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _paperlib import audit_project, render_report


CITATION_CODES = {
    "BIB_FILE_MISSING",
    "BIB_KEY_DUPLICATE",
    "BIB_ENTRY_UNCITED",
    "CITE_UNDEFINED",
    "CITATION_MANIFEST_MISSING",
    "CITATION_KEY_MISSING",
    "CITATION_KEY_DUPLICATE",
    "CITATION_MANIFEST_KEY_ABSENT_FROM_BIB",
    "CITATION_METADATA_STATUS_INVALID",
    "CITATION_SUPPORT_STATUS_INVALID",
    "CITATION_METADATA_AUDIT_TRAIL_MISSING",
    "CITATION_SUPPORT_AUDIT_TRAIL_MISSING",
    "CITATION_CLAIM_UNKNOWN",
    "CITATION_NOT_RELEASE_READY",
    "DOI_SHAPE_SUSPICIOUS",
    "URL_SHAPE_SUSPICIOUS",
    "STATE_FILE_MISSING",
    "STATE_PARSE_ERROR",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check bibliography and citation-manifest integrity."
    )
    parser.add_argument("paper_dir", type=Path)
    parser.add_argument("--main", default=None)
    parser.add_argument("--release", action="store_true")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = audit_project(
            args.paper_dir,
            explicit_main=args.main,
            release=args.release,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Citation check failed: {exc}", file=sys.stderr)
        return 2

    report["issues"] = [
        item for item in report["issues"] if item["code"] in CITATION_CODES
    ]
    report["counts"] = {
        severity: sum(
            1
            for item in report["issues"]
            if item["severity"] == severity
        )
        for severity in ("error", "warning", "info")
    }
    report["limits"] = [
        "This checker is offline and does not resolve DOI or URL identifiers.",
        "A matching bibliography key does not verify metadata or claim support.",
        "Verified states require a human or authorized agent to open the actual source.",
    ]
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_report(report, title="Citation integrity audit"), end="")
    return 1 if report["counts"]["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
