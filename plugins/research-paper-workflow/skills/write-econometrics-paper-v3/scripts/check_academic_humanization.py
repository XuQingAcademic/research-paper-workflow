#!/usr/bin/env python3
"""Check protected LaTeX tokens and basic register after a prose style pass."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
from pathlib import Path
from typing import Any


PATTERNS = {
    "citations": re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^]]*\]\s*)*\{[^}]+\}"),
    "labels": re.compile(r"\\label\{[^}]+\}"),
    "references": re.compile(r"\\(?:eqref|ref|autoref|cref|Cref)\{[^}]+\}"),
    "inline_math": re.compile(
        r"(?<!\\)\$(?:\\\$|[^\\$]|\\(?!\$))*?(?<!\\)\$|\\\((?:.|\n)*?\\\)"
    ),
    "display_math": re.compile(r"\\\[(?:.|\n)*?\\\]"),
    "numbers": re.compile(r"(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*(?:e[-+]?\d+)?%?", re.IGNORECASE),
}
COLLOQUIAL = re.compile(
    r"\b(?:gonna|wanna|kinda|sorta|you guys|let's|let us dive|here's the thing|real talk)\b",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def counter_diff(before: Counter[str], after: Counter[str]) -> dict[str, list[str]]:
    return {
        "missing": sorted((before - after).elements()),
        "added": sorted((after - before).elements()),
    }


def inspect(before_text: str, after_text: str) -> dict[str, Any]:
    protected: dict[str, dict[str, list[str]]] = {}
    for name, pattern in PATTERNS.items():
        change = counter_diff(Counter(pattern.findall(before_text)), Counter(pattern.findall(after_text)))
        if change["missing"] or change["added"]:
            protected[name] = change
    colloquial_hits = sorted(set(match.group(0) for match in COLLOQUIAL.finditer(after_text)))
    valid = not protected and not colloquial_hits
    return {
        "valid": valid,
        "boundary": "surface-token-and-register-check-only; semantic equivalence not certified",
        "protected_token_changes": protected,
        "colloquial_hits": colloquial_hits,
    }


def main() -> int:
    args = parse_args()
    result = inspect(
        args.before.read_text(encoding="utf-8"),
        args.after.read_text(encoding="utf-8"),
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    else:
        print("PASS" if result["valid"] else "FAIL")
        if result["protected_token_changes"]:
            print("protected token changes detected")
        if result["colloquial_hits"]:
            print("colloquial forms: " + ", ".join(result["colloquial_hits"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
