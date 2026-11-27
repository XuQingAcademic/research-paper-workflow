#!/usr/bin/env python3
"""Read-only, advisory manuscript-to-ledger candidate coverage (standard library).

Optional precise locations coexist with legacy strings:
  {"path": "main.md", "line": 7, "text": "The estimate is 0.25."}
  {"path": "main.md", "start_line": 7, "end_line": 8, "text": "..."}
Legacy ``main.md:7`` / ``main.md#L7-L8`` may use claim ``summary`` or
``allowed_wording`` as exact manuscript text. File/section-only locations remain
unresolved. A dict with path and text alone resolves only a unique occurrence.
No registration mapping implies scientific support or release eligibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from _paperlib import ProjectSnapshot, load_json_yaml


class CoverageInputError(ValueError):
    """Invalid/unreadable input or an attempted escape from the project root."""


NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+"
SIGNALS = {
    "citation": re.compile(r"\\(?:cite\w*|parencite|textcite|autocite)\*?(?:\s*\[[^\]]*\])*\s*\{[^{}]+\}|\[(?:[^\]\n]*?@[-\w:.]+)[^\]\n]*\]|\b[A-Z][A-Za-z'-]+(?:\s+et\s+al\.)?\s*\((?:19|20)\d{2}[a-z]?\)"),
    "numeric_unit": re.compile(r"(?:" + NUM + r")\s*(?:\\?%|percent\b|percentage\s+points?\b|basis\s+points?\b|observations?\b|respondents?\b|subjects?\b|firms?\b|households?\b|samples?\b|kg\b|km\b|years?\b|months?\b|days?\b|万元|亿元|元|个|名|家|户|个百分点|倍)", re.I),
    "sample_size": re.compile(r"\b[nN]\s*(?:=|:)\s*(?:" + NUM + r")|\bsample\s+(?:size\s+)?(?:of\s+|is\s+)?(?:" + NUM + r")|样本(?:量|数|大小)?\s*(?:为|是|等于|=|：|:)?\s*(?:" + NUM + r")", re.I),
    "p_value": re.compile(r"\bp(?:[- ]?value)?\s*[${]*\s*(?:[<=>≤≥]|\\(?:leq?|geq?))\s*(?:" + NUM + r")|[pP]\s*值\s*(?:为|是|[<=>≤≥])\s*(?:" + NUM + r")", re.I),
    "decimal": re.compile(r"(?<![A-Za-z0-9_.])(?:\d+\.\d+|\.\d+)(?![A-Za-z0-9_]|\.\d)"),
    "result_wording": re.compile(r"\b(?:we\s+(?:find|show|establish|demonstrate)|results?\s+(?:show|indicate|suggest)|statistically\s+significant|outperforms?|reduces?|increases?|converges?|consistent\s+estimat\w*|asymptotically\s+(?:normal|valid)|causal\s+effect)\b|结果(?:表明|显示|说明)|我们(?:发现|证明|表明)|显著(?:提高|降低|增加|减少|影响|性)?|(?:提高|降低|增加|减少)了|收敛|渐近正态|一致估计|因果效应", re.I),
}
EXCLUDED_ENV = r"equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath|eqnarray\*?|verbatim\*?|lstlisting|minted|comment|tikzpicture"


def _safe(root: Path, raw: str | Path, *, relative_only: bool = False) -> Path:
    path = Path(raw)
    if relative_only and path.is_absolute():
        raise CoverageInputError(f"Expected project-relative path: {raw}")
    if ".." in path.parts:
        raise CoverageInputError(f"Parent traversal is not allowed: {raw}")
    resolved = (path if path.is_absolute() else root / path).resolve()
    if not resolved.is_relative_to(root):
        raise CoverageInputError(f"Path resolves outside project: {raw}")
    return resolved


def _blank(text: str) -> str:
    return re.sub(r"[^\n]", " ", text)


def _mask(text: str, suffix: str, *, keep_inputs: bool = False) -> str:
    """Keep offsets and newlines, mask non-prose. This is not a TeX parser."""
    masked = text
    if suffix == ".tex":
        masked = re.sub(r"(?<!\\)%[^\n]*", lambda m: _blank(m[0]), masked)
    masked = re.sub(r"<!--[\s\S]*?(?:-->|\Z)", lambda m: _blank(m[0]), masked)
    # Fences must close with the same marker (or run to EOF).
    lines = masked.splitlines(keepends=True)
    fence = None
    for i, line in enumerate(lines):
        opening = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            lines[i] = _blank(line)
            if re.match(r"^\s{0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*$", line):
                fence = None
        elif opening:
            fence = (opening[1][0], len(opening[1]))
            lines[i] = _blank(line)
    masked = "".join(lines)
    masked = re.sub(r"\\begin\{(" + EXCLUDED_ENV + r")\}[\s\S]*?(?:\\end\{\1\}|\Z)", lambda m: _blank(m[0]), masked)
    masked = re.sub(r"\$\$[\s\S]*?(?:\$\$|\Z)|\\\[[\s\S]*?(?:\\\]|\Z)", lambda m: _blank(m[0]), masked)
    # Inline math is ignored except explicit p-values and sample-size declarations.
    def inline(m: re.Match) -> str:
        original = m[0]
        chars = list(_blank(original))
        for kind in ("p_value", "sample_size"):
            for found in SIGNALS[kind].finditer(original):
                chars[found.start():found.end()] = found[0]
        return "".join(chars)
    masked = re.sub(r"(?<![\\$])\$(?!\$)[^$\n]*?(?<!\\)\$|\\\([^\n]*?\\\)", inline, masked)
    masked = re.sub(r"`[^`\n]*`", lambda m: _blank(m[0]), masked)
    masked = re.sub(r"\\(?:label|eqref|ref|autoref|[cC]ref|tag)\*?\{[^{}]*\}", lambda m: _blank(m[0]), masked)
    directive_names = "documentclass|usepackage|bibliography|addbibresource|begin|end"
    if not keep_inputs:
        directive_names += "|input|include|subfile"
    lines = masked.splitlines(keepends=True)
    original_lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if (re.match(r"^\s*#{1,6}\s", line)
                or re.fullmatch(r"\s*\\(?:part|chapter|section|subsection|subsubsection|title)\*?(?:\[[^\]]*\])?\{[^{}]*\}\s*", line)
                or re.fullmatch(r"\s*\\(?:" + directive_names + r")(?:\[[^\]]*\])?\{[^{}]*\}\s*", line)
                or re.match(r"^\s*\[[^\]]+\]:\s", line)):
            lines[i] = _blank(line)
        # Markdown setext headings.
        if re.fullmatch(r"\s*(?:={3,}|-{3,})\s*", line) and i:
            lines[i - 1] = _blank(original_lines[i - 1])
            lines[i] = _blank(line)
    return "".join(lines)


def _candidates(raw: str, path: str) -> list[dict[str, Any]]:
    masked = _mask(raw, Path(path).suffix.lower())
    found = []
    # Sentence boundaries preserve decimal points and multiline prose; semicolons
    # split independent clauses. Compound clauses otherwise stay visible as one
    # candidate, so registering only an excerpt results in partial coverage.
    boundary = re.compile(r"[。！？；;!?]+|(?<!\d)\.(?=\s|$)|(?<=\d)\.(?!\d)(?=\s|$)|\n\s*\n")
    start = 0
    citation_spans = [m.span() for m in SIGNALS["citation"].finditer(masked)]
    breaks = [m for m in boundary.finditer(masked) if not any(a <= m.start() < b for a, b in citation_spans)]
    for end_match in breaks + [None]:
        end = end_match.end() if end_match else len(masked)
        segment = masked[start:end]
        left = len(segment) - len(segment.lstrip())
        right = len(segment.rstrip())
        a, b = start + left, start + right
        # Dates and version numbers are not numerical evidence by themselves.
        detection = re.sub(r"\b(?:19|20)\d{2}[-/.]\d{1,2}(?:[-/.]\d{1,2})?\b|\bv?\d+\.\d+\.\d+\b", " ", segment)
        signals = sorted(kind for kind, regex in SIGNALS.items() if regex.search(detection))
        if signals and a < b:
            found.append({"path": path, "line": raw.count("\n", 0, a) + 1,
                          "end_line": raw.count("\n", 0, b - 1) + 1,
                          "text": raw[a:b], "signals": signals,
                          "registration": "gap", "mappings": []})
        start = end
    return found


def _normalized(text: str) -> str:
    return " ".join(text.split())


def scan_project(project: str | Path, main: str | None = None,
                 paths: list[str] | None = None) -> dict[str, Any]:
    """Return an advisory report. Structural errors are data; CLI exits 2 for them."""
    root = Path(project).resolve()
    report: dict[str, Any] = {
        "schema_version": 1, "project": str(root), "mode": "advisory",
        "main_file": None, "input_sha256": None, "input_hashes": {},
        "coverage": {"scope": "selected-paths" if paths is not None else "active-source-graph",
                     "requested_paths": paths, "scanned_paths": [], "unscanned_paths": [],
                     "status": "unknown", "whole_manuscript_coverage": "unknown"},
        "counts": {"candidates": None, "gap": None, "partial": None, "registered": None,
                   "unresolved_locators": None, "unknown": None, "error": 0},
        "candidates": [], "locators": [], "issues": [],
        "limits": [
            "Heuristic candidate detection is incomplete; zero detected gaps does not establish complete claim registration.",
            "Registration is a text/location mapping, separate from claim scientific status, evidence verification, and release eligibility.",
            "Only Markdown and LaTeX active sources are scanned; no macro expansion, generated text, PDF/OCR, tables interpretation, or semantic proof checking.",
            "Code fences, comments, display math, pure headings and equation labels are excluded; inline math is excluded except explicit p-values/sample sizes.",
            "Compound sentences can require multiple claims; partial mappings and unresolved locators require review. No manuscript or ledger is modified.",
        ],
    }
    hashes = report["input_hashes"]
    texts: dict[Path, str] = {}

    def read(path: Path) -> str:
        path = _safe(root, path)
        payload = path.read_bytes()
        hashes[path.relative_to(root).as_posix()] = hashlib.sha256(payload).hexdigest()
        return payload.decode("utf-8")

    def structured(name: str) -> dict:
        path = _safe(root, ".paper/" + name)
        if not path.exists():
            return {}
        read(path)
        return load_json_yaml(path)

    def issue(code: str, message: str, severity: str = "advisory") -> None:
        report["issues"].append({"severity": severity, "code": code, "message": message})

    try:
        if not root.is_dir():
            raise CoverageInputError("Project must be an existing directory")
        snapshot = ProjectSnapshot(root=root)
        snapshot.state = structured("paper_state.yaml")
        snapshot.claims = structured("claims.yaml")
        state_project = snapshot.state.get("project", {})
        if not isinstance(state_project, dict):
            raise CoverageInputError("paper_state.yaml project must be an object")
        chosen = main or state_project.get("main_file")
        if chosen is not None and not isinstance(chosen, str):
            raise CoverageInputError("main_file must be a string")
        if not chosen:
            defaults = [name for name in ("main.md", "manuscript.md", "paper.md", "main.tex") if (root / name).is_file()]
            if len(defaults) != 1:
                raise CoverageInputError("Specify --main; no unique conventional main file")
            chosen = defaults[0]
        snapshot.main_file = _safe(root, chosen)
        report["main_file"] = snapshot.main_file.relative_to(root).as_posix()
        active: set[Path] = set()
        def walk(path: Path) -> None:
            path = _safe(root, path)
            if path in active:
                issue("INCLUDE_CYCLE", f"Include cycle at {path.relative_to(root)}")
                return
            if path in texts:
                return
            if path.suffix.lower() not in {".md", ".markdown", ".tex"}:
                raise CoverageInputError(f"Unsupported source type: {path.relative_to(root)}")
            texts[path] = read(path)
            snapshot.source_files.append(path)
            active.add(path)
            if path.suffix.lower() == ".tex":
                for match in re.finditer(r"\\(?:input|include|subfile)\s*\{([^{}]+)\}", _mask(texts[path], ".tex", keep_inputs=True)):
                    raw_child = match[1].strip()
                    if "\\" in raw_child or "#" in raw_child:
                        issue("DYNAMIC_INCLUDE", f"Cannot resolve include in {path.relative_to(root)}: {raw_child}")
                        continue
                    child = _safe(root, path.parent / raw_child)
                    walk(child if child.suffix else child.with_suffix(".tex"))
            active.remove(path)
        walk(snapshot.main_file)
        selected = set(texts)
        if paths is not None:
            selected = {_safe(root, path, relative_only=True) for path in paths}
            if not selected:
                raise CoverageInputError("Selected-path scan requires at least one path")
            if not selected.issubset(texts):
                raise CoverageInputError("Selected paths must belong to the active source graph")
        claims_path = _safe(root, ".paper/claims.yaml")
        ledger_known = claims_path.is_file()
        if not ledger_known:
            issue("CLAIM_LEDGER_MISSING", "Registration is unknown because .paper/claims.yaml is missing.")
        if ledger_known and "claims" not in snapshot.claims:
            raise CoverageInputError("claims.yaml must contain a claims array")
        claims = snapshot.claims.get("claims", [])
        if not isinstance(claims, list) or any(not isinstance(item, dict) for item in claims):
            raise CoverageInputError("claims.yaml claims must be an array of objects")
        ids = [item.get("id") for item in claims]
        if any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
            raise CoverageInputError("Claims must have nonempty unique string IDs")
        coverage = report["coverage"]
        coverage["scanned_paths"] = sorted(p.relative_to(root).as_posix() for p in selected)
        coverage["unscanned_paths"] = sorted(p.relative_to(root).as_posix() for p in texts if p not in selected)
        for path in sorted(selected):
            report["candidates"].extend(_candidates(texts[path], path.relative_to(root).as_posix()))
        for candidate in report["candidates"]:
            candidate["id"] = "candidate-" + hashlib.sha256(f"{candidate['path']}:{candidate['line']}:{candidate['text']}".encode()).hexdigest()[:16]
            if not ledger_known:
                candidate["registration"] = "unknown"
        for claim in claims:
            locations = claim.get("locations", [])
            if not isinstance(locations, list):
                raise CoverageInputError(f"Claim {claim['id']} locations must be an array")
            for location in locations:
                result = {"claim_id": claim["id"], "location": location, "resolution": "unresolved", "reason": "imprecise-location"}
                report["locators"].append(result)
                line = end_line = None
                quote = None
                if isinstance(location, str):
                    match = re.fullmatch(r"(.+?)(?::|#L)(\d+)(?:-L?(\d+))?", location)
                    path_name = match[1] if match else location.split("#", 1)[0]
                    if match:
                        line = int(match[2]); end_line = int(match[3] or match[2])
                    quote = claim.get("allowed_wording") or claim.get("summary")
                elif isinstance(location, dict):
                    path_name = location.get("path", location.get("file"))
                    line = location.get("line", location.get("start_line"))
                    end_line = location.get("end_line", line)
                    quote = location.get("text", location.get("quote"))
                else:
                    raise CoverageInputError(f"Claim {claim['id']} location must be a string or object")
                if not isinstance(path_name, str) or not path_name:
                    result["reason"] = "unsupported-locator"
                    continue
                path = _safe(root, path_name, relative_only=True)
                if path not in texts:
                    result["reason"] = "inactive-or-missing-source"
                    continue
                if path not in selected:
                    result["reason"] = "outside-scan-scope"
                    continue
                if line is not None and (type(line) is not int or type(end_line) is not int or line < 1 or end_line < line):
                    raise CoverageInputError(f"Claim {claim['id']} invalid line range")
                if not isinstance(quote, str) or not quote.strip():
                    result["reason"] = "missing-exact-text"
                    continue
                # Legacy file/section strings are never promoted to exact locators.
                if isinstance(location, str) and line is None:
                    continue
                text_lines = texts[path].splitlines()
                if line and end_line > len(text_lines):
                    result["reason"] = "stale-line-range"
                    continue
                target = "\n".join(text_lines[line - 1:end_line]) if line else texts[path]
                normalized_quote = _normalized(quote)
                occurrences = _normalized(target).count(normalized_quote)
                if occurrences != 1:
                    result["reason"] = "stale-text" if not occurrences else "ambiguous-text"
                    continue
                relevant = [c for c in report["candidates"] if c["path"] == path.relative_to(root).as_posix()
                            and (line is None or (c["line"] >= line and c["end_line"] <= end_line))
                            and normalized_quote in _normalized(c["text"])]
                if len(relevant) != 1:
                    result["reason"] = "no-unique-candidate"
                    continue
                candidate = relevant[0]
                complete = normalized_quote == _normalized(candidate["text"])
                result.update(resolution="resolved", reason="exact-text-and-location" if line else "unique-exact-text", candidate_id=candidate["id"])
                candidate["mappings"].append({"claim_id": claim["id"], "coverage": "full" if complete else "partial", "scientific_status": claim.get("status", "unknown")})
                if complete:
                    candidate["registration"] = "registered"
                elif candidate["registration"] != "registered":
                    candidate["registration"] = "partial"
        coverage["status"] = "partial" if paths is not None or report["issues"] else "heuristic-scan-complete"
        counts = report["counts"]
        counts["candidates"] = len(report["candidates"])
        for status in ("gap", "partial", "registered"):
            counts[status] = sum(c["registration"] == status for c in report["candidates"]) if ledger_known else None
        counts["unknown"] = sum(c["registration"] == "unknown" for c in report["candidates"])
        counts["unresolved_locators"] = sum(l["resolution"] == "unresolved" for l in report["locators"])
        for candidate in report["candidates"]:
            if candidate["registration"] in {"gap", "partial"}:
                issue("CANDIDATE_" + candidate["registration"].upper(), f"{candidate['id']} at {candidate['path']}:{candidate['line']} needs registration review; this is not a scientific failure.")
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        issue("COVERAGE_INPUT_ERROR", str(exc), "error")
        report["counts"]["error"] += 1
        report["coverage"]["status"] = "unknown"
        for name in ("candidates", "gap", "partial", "registered", "unresolved_locators", "unknown"):
            report["counts"][name] = None
    if hashes:
        report["input_sha256"] = hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return report


def render_report(report: dict[str, Any]) -> str:
    lines = ["# Advisory claim coverage", "", f"- Scope: {report['coverage']['scope']} ({report['coverage']['status']})",
             f"- Input SHA-256: {report['input_sha256'] or 'unknown'}",
             f"- Counts: {json.dumps(report['counts'], ensure_ascii=False)}", "",
             "Registration mappings do not establish scientific support. Whole-manuscript coverage remains unknown.", ""]
    for candidate in report["candidates"]:
        lines.extend([f"- {candidate['path']}:{candidate['line']}-{candidate['end_line']} — {candidate['registration']} ({', '.join(candidate['signals'])})", "", "    " + candidate["text"].replace("\n", "\n    "), ""])
    for locator in report["locators"]:
        if locator["resolution"] == "unresolved":
            lines.append(f"- Unresolved locator {locator['claim_id']}: {locator['reason']} ({locator['location']})")
    lines.extend(["", "## Issues", ""])
    lines.extend(f"- {i['severity']}: {i['code']}: {i['message']}" for i in report["issues"])
    lines.extend(["", "## Coverage boundary", "", "Scanned: " + ", ".join(report["coverage"]["scanned_paths"]),
                  "Unscanned: " + ", ".join(report["coverage"]["unscanned_paths"]), ""])
    lines.extend("- " + limit for limit in report["limits"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("--main")
    parser.add_argument("--path", action="append", dest="paths")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    report = scan_project(args.project, main=args.main, paths=args.paths)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else render_report(report), end="\n" if args.format == "json" else "")
    return 2 if report["counts"]["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
