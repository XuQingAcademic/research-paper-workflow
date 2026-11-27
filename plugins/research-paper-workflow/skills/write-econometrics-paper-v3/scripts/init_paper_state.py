#!/usr/bin/env python3
"""Create a non-overwriting .paper state packet for a manuscript project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _paperlib import (
    default_ledgers,
    default_state,
    journal_overlay_template,
    unresolved_template,
    write_json_yaml,
)


PAPER_TYPES = (
    "econometric-methods",
    "applied-empirical",
    "pure-theory",
    "structural-computational",
    "mixed",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a dependency-free, non-overwriting .paper state packet."
    )
    parser.add_argument("--paper-dir", required=True, type=Path)
    parser.add_argument("--main-file", required=True)
    parser.add_argument(
        "--paper-type",
        required=True,
        choices=PAPER_TYPES,
    )
    parser.add_argument("--journal", default="")
    parser.add_argument("--language", default="English")
    parser.add_argument(
        "--confidentiality",
        default="unpublished-local",
        choices=(
            "public",
            "unpublished-local",
            "restricted",
            "sensitive",
        ),
    )
    return parser.parse_args()


def initialize(args: argparse.Namespace) -> tuple[list[Path], list[Path]]:
    root = args.paper_dir.resolve()
    if not root.is_dir():
        raise ValueError(f"Paper directory does not exist: {root}")
    main = Path(args.main_file)
    main_path = main if main.is_absolute() else root / main
    if not main_path.is_file():
        raise ValueError(f"Main manuscript does not exist: {main_path}")

    paper_dir = root / ".paper"
    paper_dir.mkdir(exist_ok=True)
    created: list[Path] = []
    skipped: list[Path] = []

    payloads = {
        "paper_state.yaml": default_state(
            args.paper_type,
            args.main_file,
            args.journal,
            args.language,
            args.confidentiality,
        ),
        **default_ledgers(),
    }
    for filename, payload in payloads.items():
        path = paper_dir / filename
        if path.exists():
            skipped.append(path)
            continue
        write_json_yaml(path, payload)
        created.append(path)

    markdown_payloads = {
        "journal_overlay.md": journal_overlay_template(args.journal),
        "unresolved_issues.md": unresolved_template(),
    }
    for filename, payload in markdown_payloads.items():
        path = paper_dir / filename
        if path.exists():
            skipped.append(path)
            continue
        path.write_text(payload, encoding="utf-8")
        created.append(path)
    return created, skipped


def main() -> int:
    args = parse_args()
    try:
        created, skipped = initialize(args)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Initialization failed: {exc}", file=sys.stderr)
        return 2
    print(f"Created {len(created)} file(s); preserved {len(skipped)} existing file(s).")
    for path in created:
        print(f"created: {path}")
    for path in skipped:
        print(f"preserved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
