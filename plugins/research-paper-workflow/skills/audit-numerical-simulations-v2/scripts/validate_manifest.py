#!/usr/bin/env python3
"""Validate a numerical-simulation plan encoded as YAML or JSON.

This is a structural and semantic preflight check. It does not prove that the
statistical method, DGP, or implementation is correct.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str
    minimum_fix: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="YAML or JSON simulation plan")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        value = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "PyYAML is required for YAML input; use JSON or install PyYAML."
            ) from exc
        value = yaml.safe_load(text)
    else:
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            try:
                import yaml  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "Unknown extension and JSON parsing failed; install PyYAML or use JSON."
                ) from exc
            value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("Manifest root must be a mapping/object.")
    return value


def at(data: dict[str, Any], path: str, default: Any = None) -> Any:
    value: Any = data
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def add(
    issues: list[Issue],
    severity: str,
    code: str,
    path: str,
    message: str,
    minimum_fix: str,
) -> None:
    issues.append(Issue(severity, code, path, message, minimum_fix))


def check_failure_policy(value: Any) -> tuple[str, str]:
    """Interpret declared handling, not actual solver behavior or arbitrary prose."""
    if value is None or value == "":
        return "missing", "Failure handling is unspecified."
    if isinstance(value, dict):
        required = {"mode", "preserve_attempts", "preserve_denominator", "report_failures"}
        if set(value) - (required | {"branch"}) or required - set(value):
            return "unknown", "Structured failure policy has missing or unknown fields."
        flags = [value[k] for k in required - {"mode"}]
        if any(type(flag) is not bool for flag in flags):
            return "unknown", "Failure preservation and reporting fields must be booleans."
        if any(flag is False for flag in flags):
            return "unsafe", "Policy explicitly omits attempts, planned denominator, or failure reporting."
        mode = value["mode"]
        if not isinstance(mode, str) or mode not in {"record_and_stop_unit", "record_and_continue", "predefined_method_branch"}:
            return "unknown", "Unrecognized failure-handling mode."
        branch = value.get("branch")
        if mode != "predefined_method_branch":
            if "branch" in value:
                return "unknown", "A branch must use predefined_method_branch mode."
            return "recognized", "Explicit preservation and reporting policy."
        if not isinstance(branch, dict) or set(branch) != {"definition", "defined_before_run", "report_rate"}:
            return "unknown", "A method branch needs its definition, pre-specification, and rate reporting."
        if not isinstance(branch["definition"], str) or not branch["definition"].strip():
            return "unknown", "A method branch needs a nonempty definition locator."
        if any(type(branch[k]) is not bool for k in ("defined_before_run", "report_rate")):
            return "unknown", "Method branch declarations must be booleans."
        if not branch["defined_before_run"] or not branch["report_rate"]:
            return "unsafe", "The branch is not pre-specified or its rate will not be reported."
        return "recognized", "Declared pre-specified method branch; its definition and execution still need review."
    if not isinstance(value, str):
        return "unknown", "Use a supported policy string or structured policy."
    normalized = " ".join(value.lower().split()).strip()
    if not normalized:
        return "missing", "Failure handling is unspecified."
    if normalized == "record_and_stop_unit":
        return "recognized", "Legacy record-and-stop strategy."
    # Whole clauses only: a negation elsewhere in a sentence cannot license an action.
    clauses = [part.strip() for part in re.split(r"[;.]+", normalized) if part.strip()]
    record = r"(?:record|retain|preserve) (?:(?:all|every|each) )?(?:failures?|failed attempts?)"
    prohibition = (
        r"(?:do not|never) (?:skip|ignore|discard|drop|silently replace)"
        r"(?: or (?:silently )?(?:replace|skip|ignore|discard|drop))*"
        r"(?: (?:failures?|failed (?:replications|attempts|draws)))?"
    )
    unsafe = (
        r"(?:silently )?(?:skip|ignore|discard|drop|omit) "
        r"(?:failures?|failed (?:replications|attempts|draws))"
    )
    kinds = []
    for clause in clauses:
        if re.fullmatch(record, clause):
            kinds.append("record")
        elif re.fullmatch(prohibition, clause):
            kinds.append("prohibit")
        elif re.fullmatch(unsafe, clause):
            kinds.append("unsafe")
        else:
            kinds.append("unknown")
    if "unknown" in kinds:
        return "unknown", "Free-form policy needs interpretation; a partial clause match cannot resolve its context."
    if "unsafe" in kinds:
        if "prohibit" in kinds:
            return "conflict", "Failure policy contains conflicting preservation and deletion directives."
        return "unsafe", "Policy explicitly directs omission of failed attempts."
    if "record" not in kinds:
        return "unknown", "Free-form policy needs interpretation; use explicit structured fields for conditional handling."
    return "recognized", "Explicit failure recording with no unsupported clause."


TASK_TYPES = {"estimation", "testing", "interval", "mixed", "diagnostic"}
TARGET_TYPES = TASK_TYPES - {"mixed"}
METRIC_TYPES = {
    **dict.fromkeys(("bias", "absolute_bias", "relative_bias", "mse", "rmse", "mae",
                     "mean_squared_error", "root_mean_squared_error", "mean_absolute_error",
                     "empirical_sd", "empirical_standard_deviation", "mean_reported_se"), "estimation"),
    **dict.fromkeys(("size", "empirical_size", "test_size", "power", "type_i_error",
                     "type_i_error_rate", "type_1_error_rate", "rejection_rate",
                     "rejection_probability", "null_rejection_probability"), "testing"),
    **dict.fromkeys(("coverage", "coverage_rate", "coverage_probability", "pointwise_coverage",
                     "joint_coverage", "simultaneous_coverage", "grid_joint_coverage",
                     "continuum_simultaneous_coverage", "interval_length", "ci_length",
                     "mean_interval_length", "average_interval_length"), "interval"),
    **dict.fromkeys(("runtime", "run_time", "computation_time", "failure_rate",
                     "convergence_rate", "memory", "peak_memory"), "diagnostic"),
}
COVERAGE_METRICS = {name for name in METRIC_TYPES if "coverage" in name}


def token(value: Any) -> str | None:
    """Normalize complete declared labels, never infer a role from a substring."""
    if not isinstance(value, str) or not value.strip():
        return None
    return re.sub(r"[\s-]+", "_", value.strip().lower())


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_task_scope(data: dict[str, Any], issues: list[Issue]) -> dict[str, Any]:
    """Resolve declared applicability; labels do not verify the scientific role."""
    unknown = False
    conflict = False
    roles: set[str] = set()
    measures = at(data, "performance.measures", [])
    if not nonempty_list(measures):
        measures = []
        unknown = True
    for index, measure in enumerate(measures):
        path = f"performance.measures[{index}]"
        if not isinstance(measure, dict):
            unknown = True
            continue  # The common list-entry check reports the malformed object.
        names = [token(measure.get("id"))]
        if "kind" in measure:
            kind = token(measure["kind"])
            names.append(kind)
            if kind not in METRIC_TYPES:
                unknown = True
                add(issues, "MAJOR", "UNVERIFIED_METRIC_KIND", path + ".kind",
                    "Metric kind is not a recognized complete metric name.",
                    "Use a known kind, or omit kind and define a custom metric with target_type and definition.")
        known_roles = {METRIC_TYPES[name] for name in names if name in METRIC_TYPES}
        roles.update(known_roles)
        if len(known_roles) > 1:
            conflict = True
            add(issues, "MAJOR", "CONFLICTING_METRIC_KIND", path,
                "The known metric ID and kind imply different target types.",
                "Reconcile the metric ID, kind and actual formula; do not relabel a testing metric to bypass its gate.")
        declared = token(measure.get("target_type"))
        if "target_type" in measure and declared not in TARGET_TYPES:
            unknown = True
            add(issues, "MAJOR", "UNVERIFIED_MEASURE_TARGET", path + ".target_type",
                "Metric target_type is missing, malformed or unknown.",
                "Use estimation, testing, interval or diagnostic and check it against the metric definition.")
        elif declared in TARGET_TYPES:
            roles.add(declared)
            if known_roles and known_roles != {declared}:
                conflict = True
                add(issues, "MAJOR", "CONFLICTING_MEASURE_TARGET", path + ".target_type",
                    "Declared target_type conflicts with a recognized metric ID or kind.",
                    "Resolve the scientific role; the declared type cannot override known size/power or coverage metrics.")
        elif not known_roles:
            unknown = True
            add(issues, "MAJOR", "UNVERIFIED_MEASURE_TARGET", path,
                "The custom metric has no resolvable target type.",
                "Supply this measure's target_type and nonempty definition; study.task_type alone is insufficient.")
        needs_definition = not known_roles or any(name in COVERAGE_METRICS for name in names)
        if needs_definition and not nonempty_text(measure.get("definition")):
            unknown = True
            add(issues, "MAJOR", "UNVERIFIED_MEASURE_DEFINITION", path + ".definition",
                "The custom metric or coverage event has no nonempty definition.",
                "State the metric formula; for coverage identify the true target and pointwise, joint or simultaneous event.")

    study = at(data, "study", {})
    explicit = isinstance(study, dict) and "task_type" in study
    declared_task = token(at(data, "study.task_type"))
    scientific_roles = roles - {"diagnostic"}
    inferred_task = ("mixed" if len(scientific_roles) > 1 else
                     next(iter(scientific_roles)) if scientific_roles else
                     "diagnostic" if roles else None)
    if explicit and declared_task not in TASK_TYPES:
        unknown = True
        add(issues, "MAJOR", "UNVERIFIED_TASK_SCOPE", "study.task_type",
            "Study task_type is malformed or unrecognized; applicability is unresolved.",
            "Use estimation, testing, interval, mixed or diagnostic and resolve every measure's role.")
    elif explicit:
        if declared_task != "mixed" and scientific_roles - {declared_task}:
            conflict = True
            add(issues, "MAJOR", "CONFLICTING_TASK_SCOPE", "study.task_type",
                "The declared task type excludes a recognized metric target.",
                "Reconcile the aim and metric definitions, or declare mixed when multiple scientific targets are intended.")
        elif (declared_task == "mixed" and len(scientific_roles) < 2) or (
            declared_task != "mixed" and declared_task not in roles
        ):
            unknown = True
            add(issues, "MAJOR", "UNVERIFIED_TASK_SCOPE", "study.task_type",
                "The declared study scope is not fully represented by resolved measure types.",
                "Specify measures for each intended target; mixed is not an exemption from applicable checks.")
    if not roles and not explicit:
        add(issues, "MAJOR", "UNVERIFIED_TASK_SCOPE", "performance.measures",
            "No study scope can be inferred; null-DGP applicability is unknown.",
            "Define known metrics or explicit measure target_type values and their formulae.")
        unknown = True

    # Known requirements survive conflicting declarations and partially unknown inputs.
    effective_roles = roles | ({declared_task} if declared_task in TARGET_TYPES else set())
    unresolved = unknown or conflict
    null_requirement = ("required" if "testing" in effective_roles else
                        "unknown" if unresolved else "not_applicable")
    truth_requirement = ("required" if effective_roles & {"estimation", "interval"} else
                         "unknown" if unresolved else "not_applicable")
    if truth_requirement == "required":
        estimands = at(data, "estimands", [])
        for index, estimand in enumerate(estimands if isinstance(estimands, list) else []):
            if not isinstance(estimand, dict) or not nonempty_text(estimand.get("truth_source")):
                add(issues, "MAJOR", "UNVERIFIED_TRUTH_SOURCE", f"estimands[{index}].truth_source",
                    "The estimation or interval target has no nonempty truth-source declaration.",
                    "Identify the analytic truth or independently justified numerical truth source; a locator is not its verification.")
    return {
        "interpretation": "conflict" if conflict else "unknown" if unknown else "recognized",
        "declared_task_type": declared_task,
        "resolved_task_type": inferred_task if not unresolved else None,
        "metric_target_types": sorted(roles),
        "null_dgp_requirement": null_requirement,
        "truth_source_requirement": truth_requirement,
        "evidence_status": "declared_only",
    }


def check_null_dgp(data: dict[str, Any], issues: list[Issue]) -> None:
    """Check declared null support, honoring explicit method-specific exclusions."""
    methods = at(data, "methods", [])
    methods = [item for item in methods if isinstance(item, dict)] if isinstance(methods, list) else []
    eligible = [item for item in methods if nonempty_text(item.get("id"))
                and token(item.get("role")) not in {"oracle", "diagnostic"}
                and token(item.get("evidence_role")) not in {"diagnostic", "diagnostic_only"}]
    targets = {item["id"] for item in eligible if token(item.get("role")) == "proposed"
               or token(item.get("evidence_role")) == "confirmatory"}
    covered: set[str] = set()
    generic_null = False
    scenarios = at(data, "dgp.scenarios", [])
    for index, scenario in enumerate(scenarios if isinstance(scenarios, list) else []):
        if not isinstance(scenario, dict):
            continue
        if "truth_by_method" not in scenario:
            if token(scenario.get("classification")) == "null":
                generic_null = True  # Legacy declaration; still requires scientific review.
            continue
        truth = scenario["truth_by_method"]
        if not isinstance(truth, dict):
            add(issues, "MAJOR", "UNVERIFIED_NULL_DGP", f"dgp.scenarios[{index}].truth_by_method",
                "Method-specific DGP truth is malformed and cannot establish a null.",
                "Map target method IDs to their actual null/alternative or diagnostic status.")
            continue
        covered.update(method for method in targets if token(truth.get(method)) == "null")
    if not generic_null and (not targets or not targets.issubset(covered)):
        missing = sorted(targets - covered)
        add(issues, "MAJOR", "NO_NULL_DGP", "dgp.scenarios",
            "Testing targets have no applicable declared null DGP" +
            (f" for: {', '.join(missing)}." if missing else "."),
            "Declare classification=null or method-specific null truth for the relevant target methods, then verify the actual null and family match before size/power claims.")


def validate(data: dict[str, Any]) -> tuple[list[Issue], dict[str, Any]]:
    issues: list[Issue] = []
    derived: dict[str, Any] = {}

    required_lists = {
        "aims": "Define at least one falsifiable simulation aim.",
        "estimands": "Define the estimand, hypothesis, or target and its truth source.",
        "dgp.scenarios": "Define at least one DGP scenario tied to an aim.",
        "methods": "Define proposed and comparison methods.",
        "performance.measures": "Pre-specify performance measures and formulae.",
    }
    for path, fix in required_lists.items():
        if not nonempty_list(at(data, path)):
            add(issues, "FATAL", "MISSING_LIST", path, "Required list is absent or empty.", fix)

    stage = at(data, "study.stage")
    if not isinstance(stage, str) or stage not in {"design", "pilot", "formal"}:
        add(
            issues,
            "MAJOR",
            "INVALID_STAGE",
            "study.stage",
            "Stage must be design, pilot, or formal.",
            "Choose one stage and keep pilot and formal outputs separate.",
        )
    if stage == "formal" and not at(data, "study.code_version"):
        add(
            issues,
            "FATAL",
            "NO_CODE_VERSION",
            "study.code_version",
            "Formal runs need a traceable code version/hash.",
            "Record a commit, archive hash, or immutable code identifier.",
        )

    for path in ["aims", "estimands", "dgp.scenarios", "methods", "performance.measures"]:
        values = at(data, path, [])
        if not isinstance(values, list):
            continue
        malformed = sum(not isinstance(item, dict) for item in values)
        if malformed:
            add(issues, "MAJOR", "INVALID_ENTRY", path,
                f"{malformed} entries are not mappings/objects.", "Use a mapping with a stable string ID for each entry.")
        ids = [item.get("id") for item in values if isinstance(item, dict)]
        missing = sum(not nonempty_text(item) for item in ids)
        ids = [item for item in ids if nonempty_text(item)]
        duplicates = sorted({item for item in ids if item and ids.count(item) > 1})
        if missing:
            add(
                issues,
                "MAJOR",
                "MISSING_ID",
                path,
                f"{missing} entries do not have stable IDs.",
                "Assign stable IDs used by configs and row-level results.",
            )
        if duplicates:
            add(
                issues,
                "FATAL",
                "DUPLICATE_ID",
                path,
                f"Duplicate IDs: {', '.join(map(str, duplicates))}.",
                "Make every entry ID unique and update downstream mappings.",
            )

    derived["task_scope"] = check_task_scope(data, issues)
    if derived["task_scope"]["null_dgp_requirement"] == "required":
        check_null_dgp(data, issues)

    methods = at(data, "methods", [])
    methods = methods if isinstance(methods, list) else []
    roles = {
        str(item.get("role", "")).lower()
        for item in methods
        if isinstance(item, dict)
    }
    if methods and "benchmark" not in roles:
        add(
            issues,
            "MAJOR",
            "NO_BENCHMARK",
            "methods",
            "No method has role=benchmark.",
            "Include the most relevant comparator and justify its implementation/tuning.",
        )
    if methods and "oracle" not in roles:
        add(
            issues,
            "MINOR",
            "NO_ORACLE",
            "methods",
            "No oracle or known reference is included.",
            "Add an oracle/analytic special case where feasible, or explain why none exists.",
        )

    planned = at(data, "replications.planned")
    if not isinstance(planned, int) or planned <= 0:
        add(
            issues,
            "FATAL",
            "INVALID_REPLICATIONS",
            "replications.planned",
            "Planned replications must be a positive integer.",
            "Choose R using the target MCSE of the primary metric.",
        )
    target_mcse = at(data, "performance.target_mcse.proportion")
    expected_p = at(data, "performance.expected_proportion_for_precision", 0.5)
    if target_mcse is not None:
        if not isinstance(target_mcse, (int, float)) or not 0 < float(target_mcse) < 0.5:
            add(
                issues,
                "MAJOR",
                "INVALID_MCSE",
                "performance.target_mcse.proportion",
                "Target MCSE must be between 0 and 0.5.",
                "Set a scientifically meaningful absolute MCSE target.",
            )
        elif not isinstance(expected_p, (int, float)) or not 0 <= float(expected_p) <= 1:
            add(
                issues,
                "MAJOR",
                "INVALID_EXPECTED_P",
                "performance.expected_proportion_for_precision",
                "Expected proportion must lie in [0,1].",
                "Use the expected size/coverage/power or 0.5 for worst-case planning.",
            )
        else:
            required_r = math.ceil(float(expected_p) * (1 - float(expected_p)) / float(target_mcse) ** 2)
            derived["required_replications_for_proportion_mcse"] = required_r
            if isinstance(planned, int) and planned < required_r:
                add(
                    issues,
                    "MAJOR" if stage != "formal" else "FATAL",
                    "MCSE_UNDERPOWERED",
                    "replications.planned",
                    f"Planned R={planned} is below R={required_r} implied by the stated proportion MCSE target.",
                    "Increase R or justify and version a less stringent MCSE target.",
                )

    nominal_levels = at(data, "inference.nominal_levels", [])
    draws = at(data, "inference.resampling.draws")
    if isinstance(draws, int) and draws > 0 and nonempty_list(nominal_levels):
        min_p = 1 / (draws + 1)
        derived["minimum_plus_one_p_value"] = min_p
        valid_levels = [float(x) for x in nominal_levels if isinstance(x, (int, float)) and x > 0]
        if valid_levels and min_p > min(valid_levels):
            add(
                issues,
                "FATAL",
                "RESAMPLING_TOO_COARSE",
                "inference.resampling.draws",
                f"With B={draws}, minimum plus-one p-value {min_p:.6g} exceeds the smallest nominal level.",
                "Increase B or change the pre-specified inference rule with theoretical justification.",
            )
    elif draws is not None and (not isinstance(draws, int) or draws <= 0):
        add(
            issues,
            "MAJOR",
            "INVALID_RESAMPLING_DRAWS",
            "inference.resampling.draws",
            "Resampling draws must be a positive integer.",
            "Set B and document the p-value/quantile convention.",
        )

    adaptive = bool(at(data, "inference.adaptive_selection.enabled", False))
    if adaptive:
        selection = at(data, "inference.adaptive_selection.selection_stream")
        calibration = at(data, "inference.adaptive_selection.calibration_stream")
        if not selection or not calibration:
            add(
                issues,
                "FATAL",
                "MISSING_ADAPTIVE_STREAM",
                "inference.adaptive_selection",
                "Adaptive selection must name selection and calibration streams.",
                "Define separate stream roles and verify non-overlap.",
            )
        elif selection == calibration:
            add(
                issues,
                "FATAL",
                "ADAPTIVE_STREAM_REUSE",
                "inference.adaptive_selection",
                "Selection and final calibration use the same named stream.",
                "Use independent selection and calibration banks.",
            )
        relation = at(data, "inference.adaptive_selection.data_relation")
        basis = at(data, "inference.adaptive_selection.validity_basis")
        if relation == "same_sample" and not basis:
            add(
                issues,
                "FATAL" if stage == "formal" else "MAJOR",
                "SAME_SAMPLE_UNJUSTIFIED",
                "inference.adaptive_selection.validity_basis",
                "Same-sample learning has no stated validity theorem or selection-aware calibration.",
                "Add the exact validity basis or use sample splitting/cross-fitting.",
            )

    key_fields = at(data, "randomness.key_fields")
    if not nonempty_list(key_fields):
        add(
            issues,
            "FATAL",
            "NO_RNG_KEY",
            "randomness.key_fields",
            "No structured random-stream identity is specified.",
            "Key streams by design, scenario, replication, and role.",
        )
    else:
        required_key_parts = {"scenario_id", "replication_id", "stream_role"}
        missing = sorted(required_key_parts - set(map(str, key_fields)))
        if missing:
            add(
                issues,
                "MAJOR",
                "INCOMPLETE_RNG_KEY",
                "randomness.key_fields",
                f"RNG identity omits: {', '.join(missing)}.",
                "Include all scientific identity fields so worker order cannot change streams.",
            )

    workers = at(data, "execution.workers", 1)
    if isinstance(workers, int) and workers > 1 and not at(data, "randomness.parallel_strategy"):
        add(
            issues,
            "FATAL",
            "NO_PARALLEL_RNG_STRATEGY",
            "randomness.parallel_strategy",
            "Parallel execution is requested without an RNG stream strategy.",
            "Derive streams from scientific identity and allocate non-overlapping replications.",
        )

    checkpoint = at(data, "execution.checkpoint_by")
    if not nonempty_list(checkpoint) or "replication_id" not in set(map(str, checkpoint or [])):
        add(
            issues,
            "FATAL",
            "UNSAFE_CHECKPOINT",
            "execution.checkpoint_by",
            "Checkpoint identity does not include replication_id.",
            "Store completed IDs, not only cumulative counts.",
        )

    policy_status, policy_note = check_failure_policy(at(data, "execution.fail_policy"))
    derived["failure_policy_interpretation"] = policy_status
    if policy_status != "recognized":
        severity, code = {
            "missing": ("FATAL", "NO_FAILURE_POLICY"),
            "unsafe": ("FATAL", "UNSAFE_FAILURE_POLICY"),
            "conflict": ("MAJOR", "CONFLICTING_FAILURE_POLICY"),
            "unknown": ("MAJOR", "UNVERIFIED_FAILURE_POLICY"),
        }[policy_status]
        add(issues, severity, code, "execution.fail_policy", policy_note,
            "Preserve typed attempts and the planned denominator; document and verify any pre-defined method branch.")

    if not at(data, "execution.config_fingerprint", False):
        add(
            issues,
            "MAJOR",
            "NO_CONFIG_FINGERPRINT",
            "execution.config_fingerprint",
            "Results are not protected against mixing different configurations.",
            "Hash the resolved scientific configuration and reject mixed shards.",
        )

    if not at(data, "outputs.row_level.path"):
        add(
            issues,
            "FATAL",
            "NO_ROW_RESULTS",
            "outputs.row_level.path",
            "No per-replication results artifact is specified.",
            "Persist row-level results before aggregation.",
        )
    unique_key = at(data, "outputs.row_level.unique_key")
    if not nonempty_list(unique_key) or "replication_id" not in set(map(str, unique_key or [])):
        add(
            issues,
            "FATAL",
            "INVALID_RESULT_KEY",
            "outputs.row_level.unique_key",
            "Row-level uniqueness does not include replication_id.",
            "Use design/scenario/method/replication as the minimum unique identity.",
        )

    for path, code, message in [
        ("reporting.report_mcse", "MCSE_NOT_REPORTED", "Monte Carlo uncertainty is not required in reporting."),
        ("reporting.report_failures", "FAILURES_NOT_REPORTED", "Failure rates are not required in reporting."),
        ("reporting.report_effective_denominators", "DENOMINATOR_NOT_REPORTED", "Effective denominators are not required in reporting."),
    ]:
        if not at(data, path, False):
            add(
                issues,
                "MAJOR",
                code,
                path,
                message,
                "Set this disclosure to true and implement it in tables/logs.",
            )

    return issues, derived


def emit(path: Path, issues: list[Issue], derived: dict[str, Any], json_mode: bool) -> None:
    blocking = [issue for issue in issues if issue.severity in {"FATAL", "MAJOR"}]
    verdict = "PASS" if not blocking else "FAIL"
    if json_mode:
        print(
            json.dumps(
                {
                    "manifest": str(path),
                    "verdict": verdict,
                    "derived": derived,
                    "issues": [asdict(issue) for issue in issues],
                    "disclaimer": "Structural preflight only; statistical correctness is not proven.",
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return

    print(f"Manifest: {path}")
    print(f"Verdict: {verdict} (structural preflight only)")
    for key, value in derived.items():
        print(f"Derived {key}: {value}")
    if not issues:
        print("No structural findings.")
    for issue in issues:
        print(f"[{issue.severity}] {issue.code} at {issue.path}")
        print(f"  {issue.message}")
        print(f"  Minimum fix: {issue.minimum_fix}")


def main() -> int:
    args = parse_args()
    try:
        data = load_manifest(args.manifest)
        issues, derived = validate(data)
        emit(args.manifest, issues, derived, args.json)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 1 if any(issue.severity in {"FATAL", "MAJOR"} for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
