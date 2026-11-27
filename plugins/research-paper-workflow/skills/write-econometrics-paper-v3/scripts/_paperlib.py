#!/usr/bin/env python3
"""Dependency-free helpers for managed econometrics manuscript projects."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


STATE_FILENAMES = (
    "paper_state.yaml",
    "claims.yaml",
    "exhibits.yaml",
    "citations.yaml",
    "revisions.yaml",
    "journal_overlay.md",
    "unresolved_issues.md",
)

STRUCTURED_FILENAMES = STATE_FILENAMES[:5]
VALID_CLAIM_STATUSES = {
    "draft",
    "needs-evidence",
    "supported",
    "rejected",
    "superseded",
}
VERIFIED_METADATA = {"verified"}
VERIFIED_SUPPORT = {"verified", "not-applicable"}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass
class ProjectSnapshot:
    root: Path
    main_file: Path | None = None
    source_files: list[Path] = field(default_factory=list)
    bib_files: list[Path] = field(default_factory=list)
    missing_inputs: list[Path] = field(default_factory=list)
    external_inputs: list[Path] = field(default_factory=list)
    external_bibs: list[Path] = field(default_factory=list)
    include_cycles: list[list[Path]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    claims: dict[str, Any] = field(default_factory=dict)
    exhibits: dict[str, Any] = field(default_factory=dict)
    citations: dict[str, Any] = field(default_factory=dict)
    revisions: dict[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML using only the standard library."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level value must be an object")
    return data


def write_json_yaml(path: Path, data: dict[str, Any]) -> None:
    """Atomically write JSON, which is valid YAML 1.2."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    handle = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    )
    try:
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(handle.name, path)
    except Exception:
        try:
            os.unlink(handle.name)
        except OSError:
            pass
        raise


def default_sections(paper_type: str) -> list[str]:
    routes = {
        "econometric-methods": [
            "abstract",
            "introduction",
            "setup",
            "method",
            "theory",
            "simulation",
            "conclusion",
        ],
        "applied-empirical": [
            "abstract",
            "introduction",
            "data",
            "identification",
            "results",
            "conclusion",
        ],
        "pure-theory": [
            "abstract",
            "introduction",
            "setup",
            "theory",
            "conclusion",
        ],
        "structural-computational": [
            "abstract",
            "introduction",
            "setup",
            "identification",
            "estimation",
            "validation",
            "counterfactual",
            "conclusion",
        ],
        "mixed": [
            "abstract",
            "introduction",
            "setup",
            "theory",
            "data",
            "method",
            "results",
            "conclusion",
        ],
    }
    return routes.get(paper_type, ["abstract", "introduction", "conclusion"])


def default_state(
    paper_type: str,
    main_file: str,
    journal: str,
    language: str,
    confidentiality: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project": {
            "paper_type": paper_type,
            "lifecycle": "draft",
            "main_file": main_file,
            "language": language,
            "version": "",
            "section_expectations": default_sections(paper_type),
        },
        "permissions": {
            "authorized_operations": ["read", "diagnose"],
            "confidentiality": confidentiality,
            "external_processing_authorized": False,
        },
        "spine": {
            "question": "",
            "friction": "",
            "move": "",
            "guarantee": "",
            "value": "",
            "falsifiable_sentence": "",
        },
        "locked_decisions": [],
        "nonclaims": [],
        "canonical_terms": [],
        "consistency_rules": [],
        "journal": {
            "target": journal,
            "article_type": "",
            "official_guidance_verified_at": "",
            "overlay_checked_by": "",
        },
        "release": {
            "candidate_sha256": "",
            "candidate_files": [],
            "frozen_at": "",
            "frozen_by": "",
            "audit_errors": None,
            "audit_warnings": None,
            "human_approved": False,
            "human_approved_by": "",
            "human_approved_at": "",
        },
    }


def default_ledgers() -> dict[str, dict[str, Any]]:
    return {
        "claims.yaml": {"schema_version": 1, "claims": []},
        "exhibits.yaml": {"schema_version": 1, "exhibits": []},
        "citations.yaml": {"schema_version": 1, "citations": []},
        "revisions.yaml": {"schema_version": 1, "revisions": []},
    }


def journal_overlay_template(journal: str) -> str:
    target = journal or "[target journal not yet selected]"
    return f"""# Journal overlay

- Target: {target}
- Article type:
- Submission stage:
- Checked by:
- Last verified:

## Official sources

| Topic | Official URL | Access date | Rule class | Applies? | Manuscript location/status |
|---|---|---|---|---|---|
| Author guidelines | | | mandatory-current-policy | unknown | |
| Data/code policy | | | article-type-rule | unknown | |
| AI/disclosure policy | | | article-type-rule | unknown | |
| Formatting/template | | | article-type-rule | unknown | |

## Observed conventions and project decisions

Record non-mandatory conventions separately from official requirements.
"""


def unresolved_template() -> str:
    return """# Unresolved issues

Use an unchecked Markdown item with [BLOCKER] for release blockers and [OPEN] for other items.
Close an item only after checking the actual affected artifact.
"""


def remove_latex_comments(text: str) -> str:
    cleaned: list[str] = []
    for line in text.splitlines():
        match = re.search(r"(?<!\\)%", line)
        cleaned.append(line[: match.start()] if match else line)
    return "\n".join(cleaned)


def _with_tex_suffix(path: Path) -> Path:
    return path if path.suffix else path.with_suffix(".tex")


def _extract_inputs(text: str) -> list[str]:
    pattern = re.compile(r"\\(?:input|include|subfile)\s*\{([^{}]+)\}")
    return [item.strip() for item in pattern.findall(text) if item.strip()]


def _extract_bib_names(text: str) -> list[str]:
    names: list[str] = []
    for group in re.findall(r"\\bibliography\s*\{([^{}]+)\}", text):
        names.extend(item.strip() for item in group.split(",") if item.strip())
    names.extend(
        item.strip()
        for item in re.findall(
            r"\\addbibresource(?:\[[^\]]*\])?\s*\{([^{}]+)\}",
            text,
        )
        if item.strip()
    )
    return names


def select_main_file(
    root: Path, state: dict[str, Any], explicit: str | None
) -> Path | None:
    candidate = explicit or str(
        state.get("project", {}).get("main_file", "")
    ).strip()
    if candidate:
        path = Path(candidate)
        return (path if path.is_absolute() else root / path).resolve()
    tex = [
        path
        for path in root.glob("*.tex")
        if "\\documentclass"
        in path.read_text(encoding="utf-8", errors="ignore")
    ]
    if len(tex) == 1:
        return tex[0].resolve()
    for name in ("main.md", "manuscript.md", "paper.md"):
        if (root / name).is_file():
            return (root / name).resolve()
    return None


def collect_project(
    root: Path, explicit_main: str | None = None
) -> ProjectSnapshot:
    root = root.resolve()
    snapshot = ProjectSnapshot(root=root)
    paper_dir = root / ".paper"
    for filename, attr in (
        ("paper_state.yaml", "state"),
        ("claims.yaml", "claims"),
        ("exhibits.yaml", "exhibits"),
        ("citations.yaml", "citations"),
        ("revisions.yaml", "revisions"),
    ):
        path = paper_dir / filename
        if path.is_file():
            try:
                setattr(snapshot, attr, load_json_yaml(path))
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                setattr(snapshot, attr, {})

    snapshot.main_file = select_main_file(root, snapshot.state, explicit_main)
    if snapshot.main_file is None:
        return snapshot

    visited: set[Path] = set()
    active: list[Path] = []
    bibs: set[Path] = set()

    def walk(path: Path) -> None:
        resolved = path.resolve()
        if not is_within(resolved, root):
            snapshot.external_inputs.append(resolved)
            return
        if resolved in active:
            start = active.index(resolved)
            snapshot.include_cycles.append(active[start:] + [resolved])
            return
        if resolved in visited:
            return
        if not resolved.is_file():
            snapshot.missing_inputs.append(resolved)
            return
        visited.add(resolved)
        active.append(resolved)
        snapshot.source_files.append(resolved)
        text = remove_latex_comments(
            resolved.read_text(encoding="utf-8", errors="replace")
        )
        if resolved.suffix.lower() == ".tex":
            for raw in _extract_inputs(text):
                child = _with_tex_suffix((resolved.parent / raw).resolve())
                walk(child)
            for raw in _extract_bib_names(text):
                bib = (resolved.parent / raw).resolve()
                if not bib.suffix:
                    bib = bib.with_suffix(".bib")
                if is_within(bib, root):
                    bibs.add(bib)
                else:
                    snapshot.external_bibs.append(bib)
        active.pop()

    walk(snapshot.main_file)
    snapshot.bib_files = sorted(bibs)
    return snapshot


def parse_bib_keys(
    paths: Iterable[Path],
) -> tuple[dict[str, list[str]], list[Path]]:
    locations: dict[str, list[str]] = {}
    missing: list[Path] = []
    pattern = re.compile(r"@\w+\s*\{\s*([^,\s]+)", re.IGNORECASE)
    for path in paths:
        if not path.is_file():
            missing.append(path)
            continue
        for key in pattern.findall(
            path.read_text(encoding="utf-8", errors="replace")
        ):
            locations.setdefault(key.strip(), []).append(str(path))
    return locations, missing


def manuscript_signals(snapshot: ProjectSnapshot) -> dict[str, Any]:
    labels: dict[str, list[str]] = {}
    refs: set[str] = set()
    cites: set[str] = set()
    headings: list[str] = []
    texts: dict[Path, str] = {}
    for path in snapshot.source_files:
        text = remove_latex_comments(
            path.read_text(encoding="utf-8", errors="replace")
        )
        texts[path] = text
        for key in re.findall(r"\\label\{([^{}]+)\}", text):
            labels.setdefault(key.strip(), []).append(
                relative(path, snapshot.root)
            )
        refs.update(
            key.strip()
            for key in re.findall(
                r"\\(?:ref|eqref|autoref|cref|Cref)\{([^{}]+)\}",
                text,
            )
        )
        for group in re.findall(r"\\cite\w*\{([^{}]+)\}", text):
            cites.update(
                key.strip() for key in group.split(",") if key.strip()
            )
        headings.extend(
            title.strip().lower()
            for title in re.findall(
                r"\\(?:part|chapter|section|subsection|subsubsection)\*?\{([^{}]+)\}",
                text,
            )
        )
        headings.extend(
            title.strip().lower()
            for title in re.findall(
                r"^\s*#{1,6}\s+(.+?)\s*$",
                text,
                re.MULTILINE,
            )
        )
        if re.search(r"\\begin\{abstract\}", text, re.IGNORECASE):
            headings.append("abstract")
    return {
        "labels": labels,
        "refs": refs,
        "cites": cites,
        "headings": headings,
        "texts": texts,
    }


SECTION_ALIASES = {
    "abstract": ("abstract",),
    "introduction": ("introduction",),
    "setup": ("setup", "model", "framework", "environment"),
    "data": ("data", "sample", "institutional background"),
    "identification": (
        "identification",
        "research design",
        "empirical strategy",
    ),
    "method": ("method", "procedure", "test statistic", "algorithm"),
    "estimation": ("estimation", "estimator"),
    "theory": ("theory", "asymptotic", "large sample", "main result"),
    "simulation": ("simulation", "monte carlo", "numerical"),
    "results": ("results", "findings"),
    "validation": ("validation", "model fit"),
    "counterfactual": ("counterfactual", "policy experiment"),
    "empirical": ("empirical", "application", "illustration"),
    "conclusion": ("conclusion", "discussion"),
}


def has_section(headings: list[str], section: str) -> bool:
    aliases = SECTION_ALIASES.get(section, (section,))
    return any(
        any(alias in heading for alias in aliases)
        for heading in headings
    )


def managed_files(snapshot: ProjectSnapshot) -> list[Path]:
    files = set(snapshot.source_files)
    files.update(path for path in snapshot.bib_files if path.is_file())
    for filename in STATE_FILENAMES:
        path = snapshot.root / ".paper" / filename
        if path.is_file():
            files.add(path.resolve())
    return sorted(files, key=lambda item: relative(item, snapshot.root))


def project_fingerprint(
    snapshot: ProjectSnapshot,
) -> tuple[str, list[str]]:
    digest = hashlib.sha256()
    names: list[str] = []
    for path in managed_files(snapshot):
        name = relative(path, snapshot.root)
        payload = path.read_bytes()
        recorded_name = name
        if name == ".paper/paper_state.yaml":
            try:
                state = load_json_yaml(path)
                state.pop("release", None)
                payload = json.dumps(
                    state,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
                recorded_name += "#without-release"
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                pass
        names.append(recorded_name)
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")
    return digest.hexdigest(), names


HIGH_RISK_PATTERNS = {
    "priority": (
        r"\bfirst\b",
        r"\bnovel\b",
        r"\bunique\b",
        r"to the best of (?:our|my) knowledge",
    ),
    "scope": (
        r"\buniform(?:ly)?\b",
        r"\buniversal(?:ly)?\b",
        r"\barbitrary\b",
    ),
    "validity": (
        r"\brobust(?:ness|ly)?\b",
        r"\bvalid(?:ity|ly)?\b",
        r"\boptimal(?:ity|ly)?\b",
        r"\befficient(?:cy|ly)?\b",
    ),
    "causality": (
        r"\bcausal(?:ity|ly)?\b",
        r"\bcauses?\b",
    ),
    "unsupported-ease": (
        r"\bobvious(?:ly)?\b",
        r"\btrivial(?:ly)?\b",
        r"\bclearly\b",
        r"\bstraightforward\b",
    ),
}


def lexical_issues(snapshot: ProjectSnapshot) -> list[Issue]:
    findings: list[Issue] = []
    for path in snapshot.source_files:
        text = remove_latex_comments(
            path.read_text(encoding="utf-8", errors="replace")
        )
        for number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            for category, patterns in HIGH_RISK_PATTERNS.items():
                matched = {
                    match.group(0)
                    for pattern in patterns
                    for match in re.finditer(pattern, line, re.IGNORECASE)
                }
                if matched:
                    terms = ", ".join(sorted(matched, key=str.lower))
                    findings.append(
                        Issue(
                            "warning",
                            "HIGH_RISK_CLAIM_LANGUAGE",
                            (
                                f"Review {category} wording at line {number}; "
                                f"matched term(s): {terms}."
                            ),
                            relative(path, snapshot.root),
                        )
                    )
    return findings


def _duplicate_ids(items: list[dict[str, Any]]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        identifier = str(item.get("id", "")).strip()
        if identifier in seen:
            duplicates.add(identifier)
        elif identifier:
            seen.add(identifier)
    return duplicates


def _open_markdown_items(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [
        line.strip()
        for line in path.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
        if re.match(r"^\s*-\s*\[\s\]\s*", line)
    ]


def audit_project(
    root: Path,
    explicit_main: str | None = None,
    release: bool = False,
) -> dict[str, Any]:
    snapshot = collect_project(root, explicit_main)
    issues: list[Issue] = []
    release_severity = "error" if release else "warning"
    paper_dir = snapshot.root / ".paper"

    if not snapshot.root.is_dir():
        issues.append(
            Issue(
                "error",
                "PROJECT_NOT_FOUND",
                "Paper project directory does not exist.",
            )
        )
    if snapshot.main_file is None:
        issues.append(
            Issue(
                "error",
                "MAIN_FILE_MISSING",
                "No active manuscript could be resolved.",
            )
        )
    elif not snapshot.main_file.is_file():
        issues.append(
            Issue(
                "error",
                "MAIN_FILE_NOT_FOUND",
                "Configured main manuscript does not exist.",
                relative(snapshot.main_file, snapshot.root),
            )
        )

    for path in snapshot.missing_inputs:
        issues.append(
            Issue(
                "error",
                "LATEX_INPUT_MISSING",
                "Referenced LaTeX input is missing.",
                relative(path, snapshot.root),
            )
        )
    for path in snapshot.external_inputs:
        issues.append(
            Issue(
                "error",
                "EXTERNAL_INPUT_BLOCKED",
                "A manuscript input resolves outside the paper project and was not read.",
                str(path),
            )
        )
    for path in snapshot.external_bibs:
        issues.append(
            Issue(
                "error",
                "EXTERNAL_BIB_BLOCKED",
                "A bibliography resource resolves outside the paper project and was not read.",
                str(path),
            )
        )
    for cycle in snapshot.include_cycles:
        issues.append(
            Issue(
                "error",
                "LATEX_INCLUDE_CYCLE",
                "LaTeX input cycle: "
                + " -> ".join(
                    relative(item, snapshot.root) for item in cycle
                ),
            )
        )

    for filename in STATE_FILENAMES:
        if not (paper_dir / filename).is_file():
            issues.append(
                Issue(
                    release_severity,
                    "STATE_FILE_MISSING",
                    f"Missing managed-project file: .paper/{filename}",
                )
            )

    for filename in STRUCTURED_FILENAMES:
        path = paper_dir / filename
        if path.is_file():
            try:
                load_json_yaml(path)
            except (
                OSError,
                UnicodeError,
                json.JSONDecodeError,
                ValueError,
            ) as exc:
                issues.append(
                    Issue(
                        "error",
                        "STATE_PARSE_ERROR",
                        f"Cannot parse JSON-compatible YAML: {exc}",
                        relative(path, snapshot.root),
                    )
                )

    signals = (
        manuscript_signals(snapshot)
        if snapshot.source_files
        else {
            "labels": {},
            "refs": set(),
            "cites": set(),
            "headings": [],
            "texts": {},
        }
    )
    labels: dict[str, list[str]] = signals["labels"]
    refs: set[str] = signals["refs"]
    cites: set[str] = signals["cites"]
    issues.extend(lexical_issues(snapshot))

    for key, paths in labels.items():
        if len(paths) > 1:
            issues.append(
                Issue(
                    "error",
                    "LABEL_DUPLICATE",
                    f"Label '{key}' is defined more than once: "
                    + ", ".join(paths),
                )
            )
    for key in sorted(refs - set(labels)):
        issues.append(
            Issue(
                "error",
                "REF_UNDEFINED",
                f"Reference target '{key}' is undefined.",
            )
        )

    bib_keys, missing_bibs = parse_bib_keys(snapshot.bib_files)
    for path in missing_bibs:
        issues.append(
            Issue(
                "error",
                "BIB_FILE_MISSING",
                "Bibliography resource is missing.",
                relative(path, snapshot.root),
            )
        )
    for key, paths in bib_keys.items():
        if len(paths) > 1:
            issues.append(
                Issue(
                    "error",
                    "BIB_KEY_DUPLICATE",
                    f"Bibliography key '{key}' appears more than once.",
                )
            )
    for key in sorted(cites - set(bib_keys)):
        issues.append(
            Issue(
                "error",
                "CITE_UNDEFINED",
                f"Citation key '{key}' is absent from active bibliography resources.",
            )
        )
    for key in sorted(set(bib_keys) - cites):
        issues.append(
            Issue(
                "info",
                "BIB_ENTRY_UNCITED",
                f"Bibliography key '{key}' is not cited by the active manuscript.",
            )
        )

    state = snapshot.state
    project_state = (
        state.get("project", {})
        if isinstance(state.get("project", {}), dict)
        else {}
    )
    if state:
        if state.get("schema_version") != 1:
            issues.append(
                Issue(
                    "error",
                    "STATE_SCHEMA_UNSUPPORTED",
                    "paper_state.yaml must use schema_version 1.",
                )
            )
        if project_state.get("paper_type") not in {
            "econometric-methods",
            "applied-empirical",
            "pure-theory",
            "structural-computational",
            "mixed",
        }:
            issues.append(
                Issue(
                    "error",
                    "PAPER_TYPE_INVALID",
                    "paper_state.yaml contains an unsupported paper type.",
                )
            )
        if project_state.get("lifecycle") not in {
            "design",
            "draft",
            "internal-revision",
            "pre-submission",
            "r-and-r",
            "release",
        }:
            issues.append(
                Issue(
                    "error",
                    "LIFECYCLE_INVALID",
                    "paper_state.yaml contains an unsupported lifecycle.",
                )
            )
    expected = (
        project_state.get("section_expectations", [])
        if state
        else []
    )
    if isinstance(expected, list):
        for section in expected:
            if (
                isinstance(section, str)
                and section
                and not has_section(signals["headings"], section)
            ):
                issues.append(
                    Issue(
                        release_severity,
                        "SECTION_EXPECTED_MISSING",
                        f"Expected section not detected: {section}",
                    )
                )

    claims = snapshot.claims.get("claims", []) if snapshot.claims else []
    exhibits = (
        snapshot.exhibits.get("exhibits", [])
        if snapshot.exhibits
        else []
    )
    citations = (
        snapshot.citations.get("citations", [])
        if snapshot.citations
        else []
    )
    revisions = (
        snapshot.revisions.get("revisions", [])
        if snapshot.revisions
        else []
    )
    for name, items in (
        ("claims", claims),
        ("exhibits", exhibits),
        ("citations", citations),
        ("revisions", revisions),
    ):
        if not isinstance(items, list):
            issues.append(
                Issue(
                    "error",
                    "LEDGER_SHAPE_INVALID",
                    f"'{name}' must be a list.",
                )
            )

    claims = claims if isinstance(claims, list) else []
    exhibits = exhibits if isinstance(exhibits, list) else []
    citations = citations if isinstance(citations, list) else []
    revisions = revisions if isinstance(revisions, list) else []

    for name, items in (
        ("claim", claims),
        ("exhibit", exhibits),
        ("citation", citations),
        ("revision", revisions),
    ):
        for duplicate in sorted(_duplicate_ids(items)):
            issues.append(
                Issue(
                    "error",
                    "LEDGER_ID_DUPLICATE",
                    f"Duplicate {name} ID: {duplicate}",
                )
            )

    claim_ids = {
        str(item.get("id", "")).strip()
        for item in claims
        if str(item.get("id", "")).strip()
    }
    exhibit_ids = {
        str(item.get("id", "")).strip()
        for item in exhibits
        if str(item.get("id", "")).strip()
    }
    citation_ids = {
        str(item.get("id", "")).strip()
        for item in citations
        if str(item.get("id", "")).strip()
    }
    evidence_ids = exhibit_ids | citation_ids

    if release and not claims:
        issues.append(
            Issue(
                "error",
                "CLAIM_LEDGER_EMPTY",
                "Release audit requires at least one registered claim.",
            )
        )
    for item in claims:
        identifier = str(item.get("id", "")).strip() or "<missing>"
        status = str(item.get("status", "")).strip()
        if identifier == "<missing>":
            issues.append(
                Issue(
                    "error",
                    "CLAIM_ID_MISSING",
                    "Claim record has no ID.",
                )
            )
        if status not in VALID_CLAIM_STATUSES:
            issues.append(
                Issue(
                    "error",
                    "CLAIM_STATUS_INVALID",
                    f"Claim {identifier} has invalid status '{status}'.",
                )
            )
        if status == "supported":
            refs_for_claim = item.get("evidence_ids", [])
            locations = item.get("locations", [])
            if not isinstance(refs_for_claim, list) or not refs_for_claim:
                issues.append(
                    Issue(
                        "error",
                        "SUPPORTED_CLAIM_NO_EVIDENCE",
                        f"Supported claim {identifier} has no evidence IDs.",
                    )
                )
            if not isinstance(locations, list) or not locations:
                issues.append(
                    Issue(
                        "error",
                        "SUPPORTED_CLAIM_NO_LOCATION",
                        f"Supported claim {identifier} has no manuscript location.",
                    )
                )
            for evidence in (
                refs_for_claim
                if isinstance(refs_for_claim, list)
                else []
            ):
                if str(evidence) not in evidence_ids:
                    issues.append(
                        Issue(
                            "error",
                            "CLAIM_EVIDENCE_UNKNOWN",
                            f"Claim {identifier} references unknown evidence ID '{evidence}'.",
                        )
                    )
        if release and status in {"draft", "needs-evidence"}:
            issues.append(
                Issue(
                    "error",
                    "CLAIM_NOT_RELEASE_READY",
                    f"Claim {identifier} remains '{status}'.",
                )
            )

    for item in exhibits:
        identifier = str(item.get("id", "")).strip() or "<missing>"
        label = str(item.get("label", "")).strip()
        if label and label not in labels:
            issues.append(
                Issue(
                    "error",
                    "EXHIBIT_LABEL_UNDEFINED",
                    f"Exhibit {identifier} uses undefined label '{label}'.",
                )
            )
        supported_claims = item.get("supports_claims", [])
        for claim in (
            supported_claims
            if isinstance(supported_claims, list)
            else []
        ):
            if str(claim) not in claim_ids:
                issues.append(
                    Issue(
                        "error",
                        "EXHIBIT_CLAIM_UNKNOWN",
                        f"Exhibit {identifier} references unknown claim '{claim}'.",
                    )
                )
        raw_path = str(item.get("path", "")).strip()
        if raw_path:
            artifact = Path(raw_path)
            artifact = (
                artifact
                if artifact.is_absolute()
                else snapshot.root / artifact
            )
            if not is_within(artifact, snapshot.root):
                issues.append(
                    Issue(
                        "error",
                        "EXHIBIT_EXTERNAL_PATH",
                        f"Exhibit {identifier} resolves outside the paper project.",
                        str(artifact.resolve()),
                    )
                )
            elif not artifact.exists():
                issues.append(
                    Issue(
                        "error",
                        "EXHIBIT_PATH_MISSING",
                        f"Exhibit {identifier} path does not exist.",
                        relative(artifact, snapshot.root),
                    )
                )
        if (
            release
            and str(item.get("status", "")).strip()
            not in {"verified", "ready", "not-applicable"}
        ):
            issues.append(
                Issue(
                    "error",
                    "EXHIBIT_NOT_RELEASE_READY",
                    f"Exhibit {identifier} is not verified or ready.",
                )
            )

    citation_by_key: dict[str, dict[str, Any]] = {}
    duplicate_citation_keys: set[str] = set()
    for item in citations:
        key = str(item.get("citation_key", "")).strip()
        if not key:
            issues.append(
                Issue(
                    "error",
                    "CITATION_KEY_MISSING",
                    "A citations.yaml record has no citation_key.",
                )
            )
            continue
        if key in citation_by_key:
            duplicate_citation_keys.add(key)
        citation_by_key[key] = item
    for key in sorted(duplicate_citation_keys):
        issues.append(
            Issue(
                "error",
                "CITATION_KEY_DUPLICATE",
                f"Citation manifest key '{key}' appears more than once.",
            )
        )
    for key in sorted(cites - set(citation_by_key)):
        issues.append(
            Issue(
                release_severity,
                "CITATION_MANIFEST_MISSING",
                f"Cited key '{key}' has no citations.yaml record.",
            )
        )
    for item in citations:
        identifier = str(item.get("id", "")).strip() or "<missing>"
        citation_key = str(item.get("citation_key", "")).strip()
        metadata_status = str(
            item.get("metadata_status", "")
        ).strip()
        support_status = str(
            item.get("claim_support_status", "")
        ).strip()
        if metadata_status not in {
            "discovered",
            "verified",
            "conflict",
            "unavailable",
        }:
            issues.append(
                Issue(
                    "error",
                    "CITATION_METADATA_STATUS_INVALID",
                    f"Citation {identifier} has invalid metadata status '{metadata_status}'.",
                )
            )
        if support_status not in {
            "unverified",
            "verified",
            "partial",
            "contradicted",
            "not-applicable",
        }:
            issues.append(
                Issue(
                    "error",
                    "CITATION_SUPPORT_STATUS_INVALID",
                    f"Citation {identifier} has invalid support status '{support_status}'.",
                )
            )
        if citation_key and citation_key not in bib_keys:
            issues.append(
                Issue(
                    release_severity,
                    "CITATION_MANIFEST_KEY_ABSENT_FROM_BIB",
                    f"Citation {identifier} key '{citation_key}' is absent from active bibliography resources.",
                )
            )
        doi = str(item.get("doi", "")).strip()
        if doi and not re.match(r"^10\.\d{4,9}/\S+$", doi, re.IGNORECASE):
            issues.append(
                Issue(
                    "warning",
                    "DOI_SHAPE_SUSPICIOUS",
                    f"Citation {identifier} has a DOI with an unexpected shape.",
                )
            )
        url = str(item.get("url", "")).strip()
        if url and not re.match(r"^https?://", url, re.IGNORECASE):
            issues.append(
                Issue(
                    "warning",
                    "URL_SHAPE_SUSPICIOUS",
                    f"Citation {identifier} URL is not HTTP(S).",
                )
            )
        if metadata_status == "verified":
            if (
                not item.get("metadata_source")
                or not item.get("checked_by")
                or not item.get("checked_at")
            ):
                issues.append(
                    Issue(
                        "error",
                        "CITATION_METADATA_AUDIT_TRAIL_MISSING",
                        f"Citation {identifier} is metadata-verified without source, checker, or date.",
                    )
                )
        if support_status == "verified":
            if not item.get("locator") or not item.get("supports_claims"):
                issues.append(
                    Issue(
                        "error",
                        "CITATION_SUPPORT_AUDIT_TRAIL_MISSING",
                        f"Citation {identifier} is claim-verified without locator or supported claims.",
                    )
                )
        supported_claims = item.get("supports_claims", [])
        for claim in (
            supported_claims
            if isinstance(supported_claims, list)
            else []
        ):
            if str(claim) not in claim_ids:
                issues.append(
                    Issue(
                        "error",
                        "CITATION_CLAIM_UNKNOWN",
                        f"Citation {identifier} references unknown claim '{claim}'.",
                    )
                )
        if release and (
            metadata_status not in VERIFIED_METADATA
            or support_status not in VERIFIED_SUPPORT
        ):
            issues.append(
                Issue(
                    "error",
                    "CITATION_NOT_RELEASE_READY",
                    f"Citation {identifier} is not fully verified for release.",
                )
            )

    for item in revisions:
        identifier = str(item.get("id", "")).strip() or "<missing>"
        status = str(item.get("status", "")).strip()
        if (
            release
            and status not in {"accepted", "checked", "closed", "not-applicable"}
        ):
            issues.append(
                Issue(
                    "error",
                    "REVISION_OPEN",
                    f"Revision item {identifier} is not accepted, checked or closed.",
                )
            )
        if release and status == "accepted" and item.get("cycle_id"):
            implementation = item.get("implementation", {})
            verification = item.get("verification", {})
            review_path = (
                str(verification.get("review_path", "")).strip()
                if isinstance(verification, dict)
                else ""
            )
            review_sha256 = (
                str(verification.get("review_sha256", "")).strip()
                if isinstance(verification, dict)
                else ""
            )
            worker_id = (
                str(implementation.get("worker_id", "")).strip()
                if isinstance(implementation, dict)
                else ""
            )
            reviewer_id = (
                str(verification.get("reviewer_id", "")).strip()
                if isinstance(verification, dict)
                else ""
            )
            attempts = (
                implementation.get("attempts", 0)
                if isinstance(implementation, dict)
                else 0
            )
            review_file = snapshot.root / review_path if review_path else None
            review_valid = (
                review_file is not None
                and is_within(review_file, snapshot.root)
                and review_file.is_file()
                and not review_file.is_symlink()
                and re.fullmatch(r"[0-9a-f]{64}", review_sha256) is not None
                and hashlib.sha256(review_file.read_bytes()).hexdigest()
                == review_sha256
            )
            if (
                not isinstance(attempts, int)
                or attempts < 1
                or not worker_id
                or not reviewer_id
                or reviewer_id == worker_id
                or not isinstance(verification, dict)
                or verification.get("verdict") != "accepted"
                or not verification.get("reviewer_context_id")
                or re.fullmatch(
                    r"[0-9a-f]{64}",
                    str(verification.get("candidate_sha256", "")),
                )
                is None
                or not review_valid
            ):
                issues.append(
                    Issue(
                        "error",
                        "REVISION_ACCEPTED_EVIDENCE_MISSING",
                        f"Continuous revision item {identifier} is accepted without a current independent review binding.",
                    )
                )

    for line in _open_markdown_items(
        paper_dir / "unresolved_issues.md"
    ):
        severity = (
            "error"
            if release and "[BLOCKER]" in line.upper()
            else "warning"
        )
        issues.append(
            Issue(
                severity,
                "UNRESOLVED_ITEM_OPEN",
                "An unresolved project item remains open.",
            )
        )

    all_text = "\n".join(signals["texts"].values())
    canonical_terms = state.get("canonical_terms", [])
    for item in (
        canonical_terms if isinstance(canonical_terms, list) else []
    ):
        canonical = (
            str(item.get("canonical", "")).strip()
            if isinstance(item, dict)
            else ""
        )
        variants = (
            item.get("forbidden_variants", [])
            if isinstance(item, dict)
            else []
        )
        provenance = item.get("provenance") if isinstance(item, dict) else None
        provenance_ok = False
        if isinstance(provenance, dict):
            kind = provenance.get("kind")
            if kind == "literature":
                keys = provenance.get("citation_keys")
                provenance_ok = (
                    isinstance(keys, list)
                    and bool(keys)
                    and all(isinstance(key, str) and key.strip() for key in keys)
                    and isinstance(provenance.get("source_locator"), str)
                    and bool(provenance["source_locator"].strip())
                )
            elif kind == "author-defined":
                mapped = provenance.get("maps_to")
                provenance_ok = (
                    isinstance(mapped, list)
                    and bool(mapped)
                    and all(isinstance(term, str) and term.strip() for term in mapped)
                    and isinstance(provenance.get("reason"), str)
                    and bool(provenance["reason"].strip())
                    and isinstance(provenance.get("decision_locator"), str)
                    and bool(provenance["decision_locator"].strip())
                )
        if canonical and not provenance_ok:
            issues.append(
                Issue(
                    "error" if release else "warning",
                    "TERM_PROVENANCE_MISSING",
                    f"Canonical term '{canonical}' lacks complete literature or author-defined provenance.",
                )
            )
        for variant in variants if isinstance(variants, list) else []:
            if str(variant) and str(variant) in all_text:
                issues.append(
                    Issue(
                        "error",
                        "FORBIDDEN_TERM_VARIANT",
                        f"Forbidden variant for '{canonical}' appears in the manuscript.",
                    )
                )
    consistency_rules = state.get("consistency_rules", [])
    for item in (
        consistency_rules
        if isinstance(consistency_rules, list)
        else []
    ):
        if not isinstance(item, dict):
            continue
        identifier = str(item.get("id", "")).strip() or "<missing>"
        canonical = str(item.get("canonical", "")).strip()
        required = item.get("required_in", [])
        if (
            canonical
            and isinstance(required, list)
            and required
            and canonical not in all_text
        ):
            issues.append(
                Issue(
                    "error",
                    "CANONICAL_FACT_MISSING",
                    f"Canonical fact {identifier} is not found in active manuscript files.",
                )
            )
        variants = item.get("forbidden_variants", [])
        for variant in variants if isinstance(variants, list) else []:
            if str(variant) and str(variant) in all_text:
                issues.append(
                    Issue(
                        "error",
                        "FORBIDDEN_FACT_VARIANT",
                        f"Forbidden variant for fact {identifier} appears in the manuscript.",
                    )
                )

    fingerprint = ""
    fingerprint_files: list[str] = []
    if snapshot.source_files:
        fingerprint, fingerprint_files = project_fingerprint(snapshot)
    release_state = (
        state.get("release", {})
        if isinstance(state.get("release", {}), dict)
        else {}
    )
    recorded = str(
        release_state.get("candidate_sha256", "")
    ).strip()
    if release:
        if not recorded:
            issues.append(
                Issue(
                    "error",
                    "CANDIDATE_NOT_FROZEN",
                    "No frozen candidate hash is recorded.",
                )
            )
        elif fingerprint != recorded:
            issues.append(
                Issue(
                    "error",
                    "CANDIDATE_HASH_MISMATCH",
                    "Managed files changed after the candidate was frozen.",
                )
            )
        if not release_state.get("human_approved", False):
            issues.append(
                Issue(
                    "error",
                    "HUMAN_APPROVAL_MISSING",
                    "Release state lacks accountable human approval.",
                )
            )
        journal_state = (
            state.get("journal", {})
            if isinstance(state.get("journal", {}), dict)
            else {}
        )
        target = str(journal_state.get("target", "")).strip()
        if (
            target
            and not journal_state.get(
                "official_guidance_verified_at"
            )
        ):
            issues.append(
                Issue(
                    "error",
                    "JOURNAL_OVERLAY_UNVERIFIED",
                    "Target journal is set but current official guidance has no verification date.",
                )
            )

    counts = {
        severity: sum(
            1 for issue in issues if issue.severity == severity
        )
        for severity in ("error", "warning", "info")
    }
    return {
        "project": str(snapshot.root),
        "main_file": (
            relative(snapshot.main_file, snapshot.root)
            if snapshot.main_file
            else ""
        ),
        "release_mode": release,
        "managed_files": fingerprint_files,
        "candidate_sha256": fingerprint,
        "counts": counts,
        "issues": [issue.to_dict() for issue in issues],
        "metrics": {
            "source_files": len(snapshot.source_files),
            "bibliography_files": len(snapshot.bib_files),
            "labels": len(labels),
            "references": len(refs),
            "citation_keys": len(cites),
            "claims": len(claims),
            "exhibits": len(exhibits),
            "citation_records": len(citations),
            "revision_records": len(revisions),
        },
        "limits": [
            "Deterministic structural checks do not prove theorem correctness or identification validity.",
            "Bibliographic presence does not prove that a source supports a manuscript claim.",
            "Only declared canonical facts and forbidden variants receive automated numeric or text checks.",
            "Compilation, rendered layout, code execution, and human approval require separate evidence.",
        ],
    }


def render_report(
    report: dict[str, Any],
    title: str = "Econometrics paper project audit",
) -> str:
    counts = report["counts"]
    metrics = report["metrics"]
    lines = [
        f"# {title}",
        "",
        f"- Project: '{report['project']}'",
        f"- Main file: '{report['main_file'] or 'unresolved'}'",
        f"- Release mode: '{str(report['release_mode']).lower()}'",
        (
            f"- Findings: {counts['error']} error(s), "
            f"{counts['warning']} warning(s), "
            f"{counts['info']} info item(s)"
        ),
        (
            f"- Scope: {metrics['source_files']} source file(s), "
            f"{metrics['bibliography_files']} bibliography file(s), "
            f"{metrics['claims']} claim(s), "
            f"{metrics['exhibits']} exhibit(s)"
        ),
        "",
    ]
    for severity in ("error", "warning", "info"):
        lines.extend([f"## {severity.title()}", ""])
        selected = [
            item
            for item in report["issues"]
            if item["severity"] == severity
        ]
        if not selected:
            lines.append("- None.")
        else:
            for item in selected:
                suffix = (
                    f" ('{item['path']}')"
                    if item.get("path")
                    else ""
                )
                lines.append(
                    f"- {item['code']}: {item['message']}{suffix}"
                )
        lines.append("")
    lines.extend(
        [
            "## Candidate fingerprint",
            "",
            report["candidate_sha256"] or "unavailable",
            "",
            "## Limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["limits"])
    return "\n".join(lines).rstrip() + "\n"
