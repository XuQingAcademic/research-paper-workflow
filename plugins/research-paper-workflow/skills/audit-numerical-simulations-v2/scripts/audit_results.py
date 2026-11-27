#!/usr/bin/env python3
"""Audit row-level Monte Carlo CSV results for identity and precision problems.

The default schema uses scenario_id, method_id, replication_id, seed_key,
status, reject, and config_fingerprint. Column names are configurable.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--scenario-col", default="scenario_id")
    parser.add_argument("--method-col", default="method_id")
    parser.add_argument("--rep-col", default="replication_id")
    parser.add_argument("--seed-col", default="seed_key")
    parser.add_argument("--status-col", default="status")
    parser.add_argument("--reject-col", default="reject")
    parser.add_argument("--fingerprint-col", default="config_fingerprint")
    parser.add_argument("--expected-reps", type=int)
    parser.add_argument(
        "--success-values",
        default="success,ok,completed",
        help="Comma-separated successful status values",
    )
    parser.add_argument(
        "--allow-seed-sharing-across-scenarios",
        action="store_true",
        help="Allow a seed key to identify more than one scenario-replication unit",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def parse_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y"}:
        return True
    if normalized in {"0", "false", "f", "no", "n"}:
        return False
    return None


def load_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header.")
        rows = list(reader)
        return rows, list(reader.fieldnames)


def numeric_missing_preview(reps: set[str], expected: int) -> list[int] | None:
    try:
        values = {int(value) for value in reps}
    except ValueError:
        return None
    if not values:
        return None
    start = 0 if 0 in values else 1
    universe = set(range(start, start + expected))
    return sorted(universe - values)[:20]


def audit(args: argparse.Namespace) -> tuple[list[Finding], list[dict[str, Any]], dict[str, Any]]:
    rows, fields = load_rows(args.csv_path)
    findings: list[Finding] = []
    summaries: list[dict[str, Any]] = []
    required = [args.scenario_col, args.method_col, args.rep_col]
    missing_columns = [column for column in required if column not in fields]
    if missing_columns:
        findings.append(
            Finding("FATAL", "MISSING_COLUMNS", f"Missing required columns: {', '.join(missing_columns)}")
        )
        return findings, summaries, {"row_count": len(rows), "columns": fields}

    keys: dict[tuple[str, str, str], int] = defaultdict(int)
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        scenario = row.get(args.scenario_col, "").strip()
        method = row.get(args.method_col, "").strip()
        rep = row.get(args.rep_col, "").strip()
        keys[(scenario, method, rep)] += 1
        groups[(scenario, method)].append(row)

    duplicate_keys = [key for key, count in keys.items() if count > 1]
    if duplicate_keys:
        preview = "; ".join("/".join(key) for key in duplicate_keys[:10])
        findings.append(
            Finding(
                "FATAL",
                "DUPLICATE_RESULT_KEYS",
                f"Found {len(duplicate_keys)} duplicate scenario/method/replication keys. Examples: {preview}",
            )
        )

    fingerprints = {
        row.get(args.fingerprint_col, "").strip()
        for row in rows
        if args.fingerprint_col in fields and row.get(args.fingerprint_col, "").strip()
    }
    if args.fingerprint_col not in fields:
        findings.append(
            Finding("MAJOR", "NO_FINGERPRINT_COLUMN", f"Column {args.fingerprint_col!r} is absent.")
        )
    elif not fingerprints:
        findings.append(
            Finding("MAJOR", "EMPTY_FINGERPRINT", "All config fingerprint values are empty.")
        )
    elif len(fingerprints) > 1:
        findings.append(
            Finding(
                "FATAL",
                "MIXED_CONFIG_FINGERPRINTS",
                f"Found {len(fingerprints)} config fingerprints in one result file.",
            )
        )

    if args.seed_col in fields:
        seed_units: dict[str, set[tuple[str, str]]] = defaultdict(set)
        for row in rows:
            seed = row.get(args.seed_col, "").strip()
            if not seed:
                continue
            unit = (row.get(args.scenario_col, "").strip(), row.get(args.rep_col, "").strip())
            seed_units[seed].add(unit)
        collisions = {seed: units for seed, units in seed_units.items() if len(units) > 1}
        if collisions and not args.allow_seed_sharing_across_scenarios:
            examples = []
            for seed, units in list(collisions.items())[:5]:
                examples.append(f"{seed}: {sorted(units)[:4]}")
            findings.append(
                Finding(
                    "FATAL",
                    "SEED_COLLISIONS",
                    f"{len(collisions)} seed keys map to multiple scenario/replication units. "
                    + "Examples: "
                    + "; ".join(examples),
                )
            )
    else:
        findings.append(Finding("MAJOR", "NO_SEED_COLUMN", f"Column {args.seed_col!r} is absent."))

    success_values = {value.strip().lower() for value in args.success_values.split(",") if value.strip()}
    for (scenario, method), group_rows in sorted(groups.items()):
        reps = {row.get(args.rep_col, "").strip() for row in group_rows}
        if args.expected_reps is not None and len(reps) != args.expected_reps:
            preview = numeric_missing_preview(reps, args.expected_reps)
            suffix = f" Missing-ID preview: {preview}." if preview is not None else ""
            findings.append(
                Finding(
                    "FATAL",
                    "INCOMPLETE_GROUP",
                    f"{scenario}/{method} has {len(reps)} unique replications; expected {args.expected_reps}.{suffix}",
                )
            )

        if args.status_col in fields:
            successful = [
                row
                for row in group_rows
                if row.get(args.status_col, "").strip().lower() in success_values
            ]
            failed = len(group_rows) - len(successful)
        else:
            successful = group_rows
            failed = 0
        if args.status_col not in fields:
            findings.append(
                Finding("MAJOR", "NO_STATUS_COLUMN", f"Column {args.status_col!r} is absent; failures cannot be audited.")
            )

        reject_values: list[bool] = []
        invalid_reject = 0
        if args.reject_col in fields:
            for row in successful:
                parsed = parse_bool(row.get(args.reject_col, ""))
                if parsed is None:
                    invalid_reject += 1
                else:
                    reject_values.append(parsed)

        estimate = None
        mcse = None
        if reject_values:
            estimate = sum(reject_values) / len(reject_values)
            mcse = math.sqrt(estimate * (1 - estimate) / len(reject_values))

        summaries.append(
            {
                "scenario": scenario,
                "method": method,
                "rows": len(group_rows),
                "unique_replications": len(reps),
                "successful": len(successful),
                "failed": failed,
                "failure_rate": failed / len(group_rows) if group_rows else None,
                "rejection_denominator": len(reject_values),
                "rejection_rate": estimate,
                "rejection_mcse": mcse,
                "invalid_reject_values": invalid_reject,
            }
        )
        if failed:
            findings.append(
                Finding(
                    "MAJOR",
                    "FAILURES_PRESENT",
                    f"{scenario}/{method}: {failed}/{len(group_rows)} rows are not successful; preserve this denominator in reporting.",
                )
            )
        if invalid_reject:
            findings.append(
                Finding(
                    "MAJOR",
                    "INVALID_REJECT_VALUES",
                    f"{scenario}/{method}: {invalid_reject} successful rows have non-boolean reject values.",
                )
            )

    if args.reject_col not in fields:
        findings.append(
            Finding("MINOR", "NO_REJECT_COLUMN", f"Column {args.reject_col!r} is absent; no rejection MCSE was computed.")
        )

    meta = {
        "row_count": len(rows),
        "columns": fields,
        "group_count": len(groups),
        "fingerprints": sorted(fingerprints),
    }
    return findings, summaries, meta


def emit(args: argparse.Namespace, findings: list[Finding], summaries: list[dict[str, Any]], meta: dict[str, Any]) -> None:
    blocking = [item for item in findings if item.severity in {"FATAL", "MAJOR"}]
    verdict = "PASS" if not blocking else "FAIL"
    if args.json:
        print(
            json.dumps(
                {
                    "file": str(args.csv_path),
                    "verdict": verdict,
                    "meta": meta,
                    "findings": [asdict(item) for item in findings],
                    "summaries": summaries,
                    "disclaimer": "Identity/precision audit only; statistical validity is not proven.",
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return

    print(f"Results: {args.csv_path}")
    print(f"Verdict: {verdict} (identity/precision audit only)")
    print(f"Rows: {meta.get('row_count')}  Groups: {meta.get('group_count')}")
    for item in findings:
        print(f"[{item.severity}] {item.code}: {item.message}")
    print("\nGroup summaries:")
    for row in summaries:
        rate = "NA" if row["rejection_rate"] is None else f"{row['rejection_rate']:.6f}"
        mcse = "NA" if row["rejection_mcse"] is None else f"{row['rejection_mcse']:.6f}"
        print(
            f"  {row['scenario']}/{row['method']}: R={row['unique_replications']}, "
            f"success={row['successful']}, failed={row['failed']}, reject={rate}, MCSE={mcse}"
        )


def main() -> int:
    args = parse_args()
    if args.expected_reps is not None and args.expected_reps <= 0:
        print("ERROR: --expected-reps must be positive.", file=sys.stderr)
        return 2
    try:
        findings, summaries, meta = audit(args)
        emit(args, findings, summaries, meta)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 1 if any(item.severity in {"FATAL", "MAJOR"} for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
