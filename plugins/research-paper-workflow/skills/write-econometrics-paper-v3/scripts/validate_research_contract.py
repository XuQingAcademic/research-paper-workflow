#!/usr/bin/env python3
"""Validate the shared proof/simulation/writing release contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "research-release-contract.v1"
CERTIFICATES = {
    "source_identity_version",
    "proof_truth",
    "proof_scope_coverage",
    "implementation_reproducibility",
    "simulation_inference_eligibility",
    "citation_novelty_coverage",
    "artifact_lineage_freshness",
    "manuscript_wording_eligibility",
}
STATES = {"PASS", "PARTIAL", "FAIL", "CONTRADICTED", "NOT_APPLICABLE"}
OWNERS = {"source", "proof", "simulation", "citation", "writing", "artifact", "handoff"}
RELEASE_KEYS = {
    "schema_GO",
    "source_GO",
    "proof_GO",
    "implementation_GO",
    "simulation_GO",
    "writing_GO",
    "artifact_GO",
    "scientific_GO",
    "submission_GO",
}


def _list(value: Any, path: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return []
    return value


def _object(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def _text(value: Any, path: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")
        return ""
    return value.strip()


def _unique(records: list[dict[str, Any]], key: str, path: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        value = _text(record.get(key), f"{path}[{index}].{key}", errors)
        if not value:
            continue
        if value in result:
            errors.append(f"{path} repeats {key}={value}")
        else:
            result[value] = record
    return result


def _find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> list[str] | None:
        if node in visiting:
            return trail[trail.index(node) :] + [node]
        if node in visited:
            return None
        visiting.add(node)
        for child in graph.get(node, []):
            cycle = visit(child, trail + [child])
            if cycle:
                return cycle
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        cycle = visit(node, [node])
        if cycle:
            return cycle
    return None


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    root = _object(data, "contract", errors)
    if root.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")

    objects_raw = [_object(item, f"objects[{i}]", errors) for i, item in enumerate(_list(root.get("objects"), "objects", errors))]
    claims_raw = [_object(item, f"claims[{i}]", errors) for i, item in enumerate(_list(root.get("claims"), "claims", errors))]
    roots_raw = [_object(item, f"root_errors[{i}]", errors) for i, item in enumerate(_list(root.get("root_errors"), "root_errors", errors))]
    blockers_raw = [_object(item, f"coverage_blockers[{i}]", errors) for i, item in enumerate(_list(root.get("coverage_blockers"), "coverage_blockers", errors))]
    artifacts_raw = [_object(item, f"artifacts[{i}]", errors) for i, item in enumerate(_list(root.get("artifacts"), "artifacts", errors))]
    release = _object(root.get("release_vector"), "release_vector", errors)

    objects = _unique(objects_raw, "object_id", "objects", errors)
    claims = _unique(claims_raw, "claim_id", "claims", errors)
    roots = _unique(roots_raw, "error_id", "root_errors", errors)
    blockers = _unique(blockers_raw, "blocker_id", "coverage_blockers", errors)
    artifacts = _unique(artifacts_raw, "artifact_id", "artifacts", errors)

    for object_id, record in objects.items():
        _text(record.get("object_type"), f"objects[{object_id}].object_type", errors)
        _text(record.get("version"), f"objects[{object_id}].version", errors)
        _text(record.get("content_hash"), f"objects[{object_id}].content_hash", errors)
        _text(record.get("scope_hash"), f"objects[{object_id}].scope_hash", errors)

    dependency_graph: dict[str, list[str]] = {}
    required_nonpass: list[str] = []
    for claim_id, record in claims.items():
        object_id = _text(record.get("object_id"), f"claims[{claim_id}].object_id", errors)
        if object_id and object_id not in objects:
            errors.append(f"claim {claim_id} references unknown object {object_id}")
        if not isinstance(record.get("required"), bool):
            errors.append(f"claims[{claim_id}].required must be boolean")
        dependencies = _list(record.get("dependencies"), f"claims[{claim_id}].dependencies", errors)
        clean_dependencies: list[str] = []
        for dep in dependencies:
            dep_id = _text(dep, f"claims[{claim_id}].dependencies", errors)
            if dep_id:
                if dep_id not in claims:
                    errors.append(f"claim {claim_id} depends on unknown claim {dep_id}")
                elif dep_id == claim_id:
                    errors.append(f"claim {claim_id} cannot depend on itself")
                clean_dependencies.append(dep_id)
        dependency_graph[claim_id] = clean_dependencies

        applicable = _list(record.get("applicable_certificates"), f"claims[{claim_id}].applicable_certificates", errors)
        applicable_set = set()
        for item in applicable:
            certificate = _text(item, f"claims[{claim_id}].applicable_certificates", errors)
            if certificate not in CERTIFICATES:
                errors.append(f"claim {claim_id} has unknown certificate {certificate}")
            applicable_set.add(certificate)
        if len(applicable_set) != len(applicable):
            errors.append(f"claim {claim_id} repeats an applicable certificate")

        state = _object(record.get("state"), f"claims[{claim_id}].state", errors)
        for certificate, value in state.items():
            if certificate not in CERTIFICATES:
                errors.append(f"claim {claim_id} state has unknown certificate {certificate}")
                continue
            if value not in STATES:
                errors.append(f"claim {claim_id} has invalid state {certificate}={value}")
            if certificate not in applicable_set and value != "NOT_APPLICABLE":
                errors.append(f"claim {claim_id} marks non-applicable {certificate} as {value}")
        for certificate in applicable_set:
            value = state.get(certificate)
            if value is None:
                errors.append(f"claim {claim_id} lacks state for applicable {certificate}")
            elif value == "NOT_APPLICABLE":
                errors.append(f"claim {claim_id} marks applicable {certificate} NOT_APPLICABLE")
            elif record.get("required") and value != "PASS":
                required_nonpass.append(f"{claim_id}:{certificate}:{value}")

    cycle = _find_cycle(dependency_graph)
    if cycle:
        errors.append("claim dependency cycle: " + " -> ".join(cycle))

    required_claims = {claim_id for claim_id, record in claims.items() if record.get("required") is True}
    for error_id, record in roots.items():
        owner = _text(record.get("owner"), f"root_errors[{error_id}].owner", errors)
        if owner and owner not in OWNERS:
            errors.append(f"root error {error_id} has unknown owner {owner}")
        claim_id = _text(record.get("claim_id"), f"root_errors[{error_id}].claim_id", errors)
        if claim_id and claim_id not in claims:
            errors.append(f"root error {error_id} references unknown claim {claim_id}")

    for blocker_id, record in blockers.items():
        claim_id = _text(record.get("claim_id"), f"coverage_blockers[{blocker_id}].claim_id", errors)
        if claim_id and claim_id not in claims:
            errors.append(f"coverage blocker {blocker_id} references unknown claim {claim_id}")

    stale_required_artifacts: list[str] = []
    for artifact_id, record in artifacts.items():
        freshness = record.get("freshness")
        if freshness not in {"current", "stale"}:
            errors.append(f"artifact {artifact_id} freshness must be current or stale")
        claim_ids = _list(record.get("claim_ids"), f"artifacts[{artifact_id}].claim_ids", errors)
        for claim_id in claim_ids:
            cid = _text(claim_id, f"artifacts[{artifact_id}].claim_ids", errors)
            if cid and cid not in claims:
                errors.append(f"artifact {artifact_id} references unknown claim {cid}")
            if freshness == "stale" and cid in required_claims:
                stale_required_artifacts.append(artifact_id)

    missing_release = sorted(RELEASE_KEYS - set(release))
    unknown_release = sorted(set(release) - RELEASE_KEYS)
    if missing_release:
        errors.append(f"release_vector missing keys: {missing_release}")
    if unknown_release:
        errors.append(f"release_vector has unknown keys: {unknown_release}")
    for key in RELEASE_KEYS & set(release):
        if not isinstance(release[key], bool):
            errors.append(f"release_vector.{key} must be boolean")

    required_root_errors = [
        error_id for error_id, record in roots.items() if record.get("claim_id") in required_claims
    ]
    required_blockers = [
        blocker_id for blocker_id, record in blockers.items() if record.get("claim_id") in required_claims
    ]
    science_blocked = bool(required_nonpass or required_root_errors or required_blockers)
    if science_blocked and release.get("scientific_GO") is True:
        errors.append("scientific_GO cannot be true with a required non-PASS state, root error, or blocker")
    if stale_required_artifacts and release.get("artifact_GO") is True:
        errors.append("artifact_GO cannot be true with stale artifacts supporting required claims")
    if release.get("submission_GO") is True and (
        release.get("scientific_GO") is not True or release.get("artifact_GO") is not True
    ):
        errors.append("submission_GO requires scientific_GO and artifact_GO")
    if not claims:
        warnings.append("contract contains no claims")

    return {
        "schema_version": SCHEMA_VERSION,
        "valid": not errors,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "derived": {
            "required_nonpass": sorted(required_nonpass),
            "required_root_errors": sorted(required_root_errors),
            "required_coverage_blockers": sorted(required_blockers),
            "stale_required_artifacts": sorted(set(stale_required_artifacts)),
            "science_blocked": science_blocked,
        },
        "stats": {
            "objects": len(objects),
            "claims": len(claims),
            "root_errors": len(roots),
            "coverage_blockers": len(blockers),
            "artifacts": len(artifacts),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.contract.read_text(encoding="utf-8"))
        result = validate(data)
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "schema_version": SCHEMA_VERSION,
            "valid": False,
            "errors": [str(exc)],
            "warnings": [],
            "derived": {},
            "stats": {},
        }
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
