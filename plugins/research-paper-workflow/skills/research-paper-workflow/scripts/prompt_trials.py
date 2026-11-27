#!/usr/bin/env python3
"""Read-only adoption/selection over the manager's frozen paired evaluations.

No model calls, prompt search, installation or scientific scoring happen here.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
SCHEMA = "research-prompt-trial.v1"


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    value = json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def same(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing {label}")
    return value


def manager_at(root):
    path = Path(root) / "scripts/compare_evaluations.py"
    spec = importlib.util.spec_from_file_location("prompt_trial_comparator", path)
    if spec is None or spec.loader is None:
        raise ValueError("manager comparator unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bound_artifact(binding, root):
    if not isinstance(binding, dict):
        raise ValueError("missing artifact binding")
    relative = Path(nonempty(binding.get("path"), "artifact path"))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("trial artifacts must use local relative paths")
    path = root / relative
    if any((root / Path(*relative.parts[:i])).is_symlink() for i in range(1, len(relative.parts) + 1)):
        raise ValueError("symlink trial evidence is not accepted")
    if not path.is_file() or digest(path) != binding.get("sha256"):
        raise ValueError(f"missing or changed artifact: {relative}")
    return path


def result(decision, reason, **extra):
    return {"schema": SCHEMA, "decision": decision, "reason": reason,
            "mutated": False, "scope": "This model/configuration and recorded tasks only; "
            "hashes bind records, not scientific truth, reviewer independence or runtime identity.",
            **extra}


def decide(manager, plan_path, baseline_path, candidate_path):
    plan_path, baseline_path, candidate_path = map(Path, (plan_path, baseline_path, candidate_path))
    comparison, _ = manager.compare(baseline_path, candidate_path)
    if comparison["comparison"] in {"invalid_evidence", "inconclusive"}:
        return result("inconclusive", "Underlying comparison is incomplete or invalid.", comparison=comparison)
    if comparison["comparison"] in {"regression", "candidate_failing"}:
        return result("reject", "Candidate has a regression or an unresolved failed check.", comparison=comparison)
    baseline, candidate = manager.read_run(baseline_path), manager.read_run(candidate_path)
    if baseline["schema_version"] != 2 or candidate["schema_version"] != 2:
        return result("inconclusive", "New adoption requires existing frozen schema-2 evidence.", comparison=comparison)
    plan = read(plan_path)
    if plan.get("schema") != SCHEMA:
        raise ValueError("unsupported trial plan")
    for field in ("id", "task_family", "hypothesis", "failure_diagnosis", "stop_condition"):
        nonempty(plan.get(field), field)
    if plan.get("change_kind") not in {"prompt", "execution", "system"}:
        raise ValueError("change_kind must distinguish prompt, execution and system changes")
    profile = plan.get("profile")
    if not isinstance(profile, dict):
        raise ValueError("missing profile")
    nonempty(profile.get("id"), "profile.id")
    runtime = profile.get("runtime")
    if not isinstance(runtime, dict):
        raise ValueError("missing profile runtime")
    for field in ("model", "model_version", "reasoning_effort", "tools", "budget"):
        if runtime.get(field) is None or runtime.get(field) == "":
            return result("inconclusive", f"Unknown runtime setting: {field}; no model-specific adoption.")
    recorded_runtime = baseline["run_settings"].get("runtime", baseline["run_settings"])
    if not same(runtime, recorded_runtime):
        return result("inconclusive", "Complete runtime configuration does not match frozen execution settings.")
    if profile.get("version_scope") not in {"snapshot", "session"}:
        raise ValueError("profile.version_scope must be snapshot or session")
    if profile["version_scope"] == "session":
        nonempty(runtime.get("session_id"), "session-scoped runtime.session_id")
    elif str(runtime["model_version"]).lower() in {"latest", "current", "default", "unknown", "unobserved"}:
        return result("inconclusive", "A mutable alias is not an immutable model snapshot; use session scope.")
    nonempty(profile.get("escalate_when"), "profile.escalate_when")
    profile_path = bound_artifact(profile.get("instructions"), plan_path.parent)
    plan_hash = digest(plan_path)
    manifests = []
    for run, path in ((baseline, baseline_path), (candidate, candidate_path)):
        manifest = read(path.parent / run["bundle"]["path"])
        manifests.append(manifest)
        if manifest.get("external_artifacts", {}).get("trial_plan", {}).get("sha256") != plan_hash:
            raise ValueError("trial plan was not bound into both bundles before execution")
    if not any(e.get("kind") == "file" and e["path"].startswith("skills/")
               and e.get("sha256") == digest(profile_path) for e in manifests[1]["entries"]):
        raise ValueError("candidate instructions are not in the frozen skill execution tree")
    cases = plan.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("empty case provenance")
    indexed = {}
    for case in cases:
        ident = nonempty(case.get("id"), "case id")
        if ident in indexed:
            raise ValueError("duplicate case provenance")
        indexed[ident] = case
        nonempty(case.get("project_id"), "case project_id")
        if case.get("origin") not in {"real", "synthetic"}:
            raise ValueError("unknown case origin")
        if case.get("exposure") not in {"exposed", "withheld"}:
            raise ValueError("unknown case exposure")
        if not isinstance(case.get("positive_control"), bool):
            raise ValueError("positive_control must be boolean")
        bound_artifact(case.get("source"), plan_path.parent)
    if indexed.keys() != baseline["indexed"].keys():
        raise ValueError("plan must cover every compared case, including failures")
    real_holdout = []
    for ident, case in indexed.items():
        if case["source"]["sha256"] != baseline["indexed"][ident]["input"]["sha256"]:
            raise ValueError("case provenance source does not match the actual frozen task input")
        split = baseline["indexed"][ident]["split"]
        if split == "holdout" and case["exposure"] != "withheld":
            return result("inconclusive", "Exposed cases cannot be relabeled as holdouts.")
        if case["origin"] == "real" and split == "holdout":
            real_holdout.append(ident)
    if not real_holdout or not any(c["origin"] == "real" and c["positive_control"] for c in cases):
        return result("inconclusive", "Need a real withheld task and a real valid-work control; synthetic tests alone do not select a profile.")
    objective = plan.get("objective", {})
    metric = objective.get("metric")
    minimum = objective.get("min_gain")
    if metric not in {"quality", "wall_seconds", "tokens", "cost_usd", "rework"}:
        raise ValueError("unsupported primary metric")
    if isinstance(minimum, bool) or not isinstance(minimum, (int, float)) or not math.isfinite(minimum) or minimum <= 0:
        raise ValueError("min_gain must be a precommitted positive number")
    if metric == "quality":
        real_gains = [{"case": ident, "check": check}
                      for ident in real_holdout
                      for check, status in baseline["indexed"][ident]["checks"].items()
                      if status == "fail" and candidate["indexed"][ident]["checks"][check] == "pass"]
        gain = len(real_gains)
        details = {"heldout_check_improvements": real_gains}
    else:
        accounting_key = nonempty(objective.get("accounting_key"), "objective.accounting_key")
        deltas = {}
        for ident in indexed:
            values, units = [], []
            for run, path in ((baseline, baseline_path), (candidate, candidate_path)):
                measure = run["indexed"][ident].get("measurements", {}).get(metric)
                if not isinstance(measure, dict) or measure.get("measurement") != "observed":
                    return result("inconclusive", f"Missing observed {metric} for {ident}.")
                manager.artifact(measure.get("source"), path.parent, f"{ident}/{metric}")
                observed = read(path.parent / measure["source"]["path"])
                if any(observed.get(k) != measure.get(k) for k in ("value", "measurement", "accounting_key")):
                    raise ValueError("measurement differs from bound observation")
                value = measure.get("value")
                original = observed.get("value")
                if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in (value, original)):
                    raise ValueError("invalid observed measurement")
                values.append(value)
                units.append(nonempty(measure.get("accounting_key"), "measurement accounting_key"))
            if units[0] != accounting_key or units[1] != accounting_key:
                return result("inconclusive", f"Incomparable measurement units for {ident}.")
            deltas[ident] = values[0] - values[1]
        if any(v != "pass" for c in baseline["cases"] for v in c["checks"].values()):
            return result("inconclusive", "Efficiency comparison requires all baseline quality checks to pass.")
        gain = sum(deltas[i] for i in real_holdout)
        details = {"paired_reductions": deltas}
        if sum(deltas.values()) < minimum or any(v < 0 for v in deltas.values()):
            return result("keep_baseline", "No unambiguous efficiency gain across the recorded cases.", **details)
    if gain < minimum:
        return result("keep_baseline", "No measured primary benefit on real withheld tasks.", metric=metric, gain=gain, **details)
    return result("eligible_scoped", "Recorded benefit meets the frozen criterion with no failed candidate checks.",
                  trial_id=plan["id"], task_family=plan["task_family"], runtime=runtime,
                  project_ids=sorted({c["project_id"] for c in cases if c["origin"] == "real"}),
                  change_kind=plan["change_kind"], profile=profile, metric=metric, gain=gain,
                  comparison=comparison, **details)


def select(manager, plan, baseline, candidate, runtime_path, task_family, project_id):
    outcome = decide(manager, plan, baseline, candidate)
    if outcome["decision"] != "eligible_scoped":
        return result("fallback", "No current, evidenced profile; preserve the configured default.", evaluation=outcome)
    if (outcome["task_family"] != task_family or not same(outcome["runtime"], read(runtime_path))
            or project_id not in outcome["project_ids"]):
        return result("fallback", "Model/version/settings, task family or project scope changed; do not transfer the result.")
    return result("selected", "Use only this scoped execution profile, subject to its escalation trigger.",
                  profile=outcome["profile"], trial_id=outcome["trial_id"], project_ids=outcome["project_ids"],
                  task_family=outcome["task_family"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("decide", "select"))
    parser.add_argument("--manager-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--task-family")
    parser.add_argument("--project-id")
    args = parser.parse_args()
    try:
        manager = manager_at(args.manager_root)
        call = (manager, args.plan.resolve(), args.baseline.resolve(), args.candidate.resolve())
        if args.command == "select":
            if args.runtime is None or args.task_family is None or args.project_id is None:
                parser.error("select needs --runtime, --task-family and --project-id")
            outcome = select(*call, args.runtime, args.task_family, args.project_id)
        else:
            outcome = decide(*call)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, ImportError) as exc:
        outcome = result("inconclusive", str(exc))
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0 if outcome["decision"] in {"eligible_scoped", "selected"} else 2 if outcome["decision"] == "inconclusive" else 1


if __name__ == "__main__":
    raise SystemExit(main())
