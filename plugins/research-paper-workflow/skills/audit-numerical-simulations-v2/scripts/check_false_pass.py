#!/usr/bin/env python3
"""Audit cell summaries when a pass requires truth strictly below the threshold."""
import argparse
import csv
from fractions import Fraction
import json
from pathlib import Path
import re
import sys


def number(raw, column):
    try:
        return Fraction(raw)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f"{column}: expected an exact finite number, got {raw!r}") from error


def count(raw, column):
    if not re.fullmatch(r"[0-9]+", raw):
        raise ValueError(f"{column}: expected a nonnegative integer count, got {raw!r}")
    return int(raw)


def inspect_table(args):
    roles = [args.truth, args.threshold, args.passes, args.reps, args.scope]
    if args.reported_rate:
        roles.append(args.reported_rate)
    columns = [*args.cell, *roles]
    if len(columns) != len(set(columns)):
        raise ValueError("each cell and metric column must be assigned once")
    if any(label.strip() != label or not label for label in [args.in_label, args.out_label]):
        raise ValueError("scope labels must be nonempty and trimmed")
    if args.in_label == args.out_label:
        raise ValueError("in-scope and out-of-scope labels must differ")
    scopes = {args.in_label: "in", args.out_label: "out"}
    seen = set()
    result = []
    with args.csv.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        header = next(reader, [])
        if any(not name.strip() for name in header) or len(header) != len(set(header)):
            raise ValueError("blank or duplicate CSV header")
        missing = sorted(set(columns) - set(header))
        if missing:
            raise ValueError(f"missing columns: {missing}")
        for values in reader:
            if len(values) != len(header):
                raise ValueError(f"line {reader.line_num}: wrong number of fields")
            row = dict(zip(header, values))
            try:
                key = tuple(row[col].strip() for col in args.cell)
                if "" in key or key in seen:
                    raise ValueError(f"empty or duplicate cell key {key!r}")
                seen.add(key)
                label = row[args.scope].strip()
                if label not in scopes:
                    raise ValueError(f"unknown scope label {label!r}")
                truth = number(row[args.truth], args.truth)
                threshold = number(row[args.threshold], args.threshold)
                passes = count(row[args.passes].strip(), args.passes)
                reps = count(row[args.reps].strip(), args.reps)
                if reps == 0 or passes > reps:
                    raise ValueError("require 0 <= pass count <= actual repetitions and R > 0")
                false_passes = passes if truth >= threshold else 0
                rate = Fraction(false_passes, reps)
                cell = {
                    "design": dict(zip(args.cell, key)), "scope_label": label,
                    "declared_scope": scopes[label], "truth": str(truth),
                    "threshold": str(threshold), "pass_count": passes, "actual_R": reps,
                    "false_pass_count": false_passes, "false_pass_rate": str(rate),
                }
                if args.reported_rate:
                    reported = number(row[args.reported_rate], args.reported_rate)
                    if not 0 <= reported <= 1:
                        raise ValueError(f"{args.reported_rate}: rate outside [0,1]")
                    cell.update(reported_rate=str(reported), rate_matches=reported == rate)
                result.append(cell)
            except ValueError as error:
                raise ValueError(f"line {reader.line_num}: {error}") from error
    if not result:
        raise ValueError("no data rows")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--cell", nargs="+", required=True, metavar="COLUMN",
                        help="all design columns jointly identifying one cell")
    for name in ["truth", "threshold", "passes", "reps", "scope"]:
        parser.add_argument(f"--{name}", required=True, metavar="COLUMN")
    parser.add_argument("--in-label", required=True, help="literal in-scope label")
    parser.add_argument("--out-label", required=True, help="literal out-of-scope label")
    parser.add_argument("--reported-rate", metavar="COLUMN",
                        help="unconditional per-cell false-pass fraction, exact in [0,1]")
    args = parser.parse_args()
    try:
        cells = inspect_table(args)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(2, f"input error: {error}\n")
    mismatches = sum(cell.get("rate_matches") is False for cell in cells)
    print(json.dumps({"pass_requires": "truth < threshold", "cell_count": len(cells),
                      "reported_column": args.reported_rate,
                      "rate_mismatches": mismatches if args.reported_rate else None,
                      "cells": cells}, ensure_ascii=False, indent=2))
    return int(mismatches > 0)


if __name__ == "__main__":
    sys.exit(main())
