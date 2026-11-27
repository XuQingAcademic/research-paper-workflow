"""Recount observed decisions from declared, immutable experiment records."""
import csv
from pathlib import Path

from check_false_pass import number


def read_value(row, spec):
    if "column" in spec:
        return number(row[spec["column"]], spec["column"])
    if "constant" in spec:
        return number(spec["constant"], "threshold constant")
    fraction = spec["complement_square"]
    index, size = (number(row[fraction[k]], fraction[k]) for k in ("index", "size"))
    if not 0 <= index <= size or size == 0:
        raise ValueError("Issued grid index is outside its grid")
    return (1 - index / size) ** 2 * number(fraction["scale"], "risk scale")


def approved(row, spec):
    column = spec["column"]
    value = row[column]
    if "positive" in spec:
        return number(value, column) > 0
    if "present" in spec:
        return bool(value.strip())
    labels = [spec["yes"], *spec["no"]]
    if value not in labels:
        raise ValueError(f"Unknown decision {value!r} in {column}")
    return value == spec["yes"]


def from_records(path: Path, spec):
    """Count unique planned experiment units and their strict unsafe issued decisions."""
    grouping = spec["groups"]
    units, rows_seen = {}, set()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Missing or duplicated CSV header")
        for row in reader:
            if None in row or None in row.values():
                raise ValueError(f"Malformed CSV row {reader.line_num}")
            if any(row[k] not in choices for k, choices in spec.get("where", {}).items()):
                continue
            group = tuple(row[k] for k in grouping)
            trial = row[spec["unit"]]
            identity = (group, trial, *(row[key] for key in spec.get("within_unit", [])))
            if not trial.strip() or "" in group or identity in rows_seen:
                raise ValueError(f"Blank or duplicate original decision key: {identity}")
            rows_seen.add(identity)
            flags = units.setdefault(group, {}).setdefault(trial, [False, False])
            if approved(row, spec["approve"]):
                risk, budget = (read_value(row, spec[key]) for key in ("risk", "limit"))
                bounded = spec.get("scale", "probability") == "probability"
                if min(risk, budget) < 0 or bounded and max(risk, budget) > 1:
                    raise ValueError(f"Risk or threshold is outside the declared scale in {identity}")
                flags[0] = True
                flags[1] |= risk > budget
    if not units:
        raise ValueError("The original records contain no eligible decisions")
    summary = []
    for group, trials in sorted(units.items()):
        counts = sum(flags[0] for flags in trials.values())
        wrong = [key for key, flags in trials.items() if flags[1]]
        total = len(trials)
        summary.append({"cell": dict(zip(grouping, group)), "count": len(wrong), "trials": total,
                        "issued": counts, "units": wrong, "basis": spec["basis"]})
    return summary
