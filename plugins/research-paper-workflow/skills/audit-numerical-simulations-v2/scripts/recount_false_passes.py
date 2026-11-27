#!/usr/bin/env python3
"""Count approvals above the risk limit from real unit-level decision records."""

import argparse
from collections import Counter
import csv
from fractions import Fraction
from hashlib import sha256
import io
import json
from pathlib import Path

from check_false_pass import number


def tally(raw, args):
    required = [*args.group, args.unit, args.decision, args.truth, args.limit]
    if len(required) != len(set(required)):
        raise ValueError("Group, unit, decision, truth and limit must use different columns")
    labels = [args.approve, *args.otherwise]
    if len(set(labels)) != len(labels) or any(not label or label != label.strip() for label in labels):
        raise ValueError("Decision labels must be distinct, nonempty and trimmed")

    groups = {}
    seen = set()
    with io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, [])
        if len(header) != len(set(header)) or any(not x.strip() for x in header):
            raise ValueError("Duplicate or blank CSV column")
        if set(required) - set(header):
            raise ValueError(f"Missing column(s): {sorted(set(required) - set(header))}")
        for cells in reader:
            if len(cells) != len(header):
                raise ValueError(f"Line {reader.line_num}: unexpected field count")
            row = dict(zip(header, cells))
            group = tuple(row[c].strip() for c in args.group)
            unit = row[args.unit].strip()
            key = (group, unit)
            if not unit or "" in group or key in seen:
                raise ValueError(f"Line {reader.line_num}: blank or duplicate decision unit {key!r}")
            seen.add(key)
            decision = row[args.decision].strip()
            if decision not in labels:
                raise ValueError(f"Line {reader.line_num}: unrecognized decision {decision!r}")
            decisions, wrong = groups.setdefault(group, (Counter(), []))
            decisions[decision] += 1
            if decision != args.approve:
                continue
            try:
                truth = number(row[args.truth].strip(), args.truth)
                limit = number(row[args.limit].strip(), args.limit)
            except ValueError as error:
                raise ValueError(f"Line {reader.line_num}, approved unit {unit}: {error}") from error
            if truth > limit or (args.equality_is_violation and truth == limit):
                wrong.append(unit)
    if not groups:
        raise ValueError("The input has no decision units")

    result = []
    for group, (decisions, wrong) in groups.items():
        total = sum(decisions.values())
        approvals = decisions[args.approve]
        result.append({
            "design": dict(zip(args.group, group)),
            "decision_counts": {label: decisions[label] for label in labels},
            "observed_decision_units": total,
            "approval_count": approvals,
            "false_pass_count": len(wrong),
            "false_pass_units": wrong,
            "false_pass_fraction_all": str(Fraction(len(wrong), total)),
            "false_pass_fraction_approvals": str(Fraction(len(wrong), approvals)) if approvals else None,
        })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--group", nargs="+", required=True, metavar="COLUMN")
    for name in ("unit", "decision", "truth", "limit"):
        parser.add_argument(f"--{name}", required=True, metavar="COLUMN")
    parser.add_argument("--approve", required=True, metavar="LABEL")
    parser.add_argument("--otherwise", nargs="*", default=[], metavar="LABEL")
    parser.add_argument("--equality-is-violation", action="store_true",
                        help="Use only when a lawful approval requires truth strictly below the limit")
    args = parser.parse_args()
    try:
        raw = args.csv.read_bytes()
        groups = tally(raw, args)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(2, f"Input error: {error}\n")
    print(json.dumps({"source_sha256": sha256(raw).hexdigest(),
                      "violation": "truth >= limit" if args.equality_is_violation else "truth > limit",
                      "groups": groups}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
