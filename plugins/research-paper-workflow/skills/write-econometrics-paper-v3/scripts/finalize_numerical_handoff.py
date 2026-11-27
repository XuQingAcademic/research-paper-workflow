#!/usr/bin/env python3
"""Apply evidence-bound manuscript corrections and verify the rebuilt PDF."""
import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path


BASIS = {
    "author-labels": "The authors' labels in {source} identify {count} of {total} {unit} with {event}.",
    "visible-lower-bound": "The visible portion of {source} confirms at least {count} of {total} {unit} with {event}.",
    "full-records": "The complete records in {source} show {count} of {total} {unit} with {event}.",
    "replay": "Our independent replay documented in {source} found {count} of {total} {unit} with {event}.",
}
LATEX = dict(zip("#$%&_{}", (r"\#", r"\$", r"\%", r"\&", r"\_", r"\{", r"\}")))
LATEX.update({"^": r"\textasciicircum{}", "~": r"\textasciitilde{}", "\\": r"\textbackslash{}"})
BUILD_TOOLS = {"latexmk", "pdflatex", "xelatex", "lualatex", "bibtex", "biber", "tectonic"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def within(root, name):
    relative = Path(name)
    path = (root / relative).resolve()
    require(not relative.is_absolute() and path.is_relative_to(root), f"Path outside project: {name}")
    return path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prose(value):
    require(isinstance(value, str) and value.strip() and "\n" not in value, "Expected one line of prose")
    return value.strip()


def latex(value):
    return "".join(LATEX.get(c, c) for c in value)


def normalized(pdf_text):
    text = unicodedata.normalize("NFKC", pdf_text).casefold()
    text = re.sub(r"[‐‑–—−]|-{2,3}", "-", text)
    text = re.sub(r"[’‘]", "'", text)
    text = "".join(text.split()).replace("\u00ad", "")
    # Normalize editorial and line-break hyphens in prose, while preserving
    # signs and separators in quantities such as -1 and 4.8–5.0.
    return re.sub(r"(?<=[a-z])-(?=[a-z])", "", text)


def contains_passage(product, passage):
    expected = normalized(passage)
    if not expected:
        return False
    # A numeric fragment needs its own beginning and end. For example, 1 of
    # 100 must not match part of 11 of 100, and 1 point must not match -1 point.
    opening = r"(?<![0-9]\.)(?<![+\-0-9])" if expected[0].isdigit() else ""
    closing = r"(?![0-9]|\.[0-9])" if expected[-1].isdigit() else ""
    return re.search(opening + re.escape(expected) + closing, product) is not None


def pdf_text(path, timeout):
    if shutil.which("pdftotext"):
        argv = ["pdftotext", str(path), "-"]
        return subprocess.run(argv, check=True, capture_output=True, timeout=timeout).stdout.decode("utf-8")
    # Format 0 keeps the PDF drawing order; the spatial plain-text format interleaves columns.
    argv = ["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=txtwrite",
            "-dTextFormat=0", "-sOutputFile=-", str(path)]
    output = subprocess.run(argv, check=True, capture_output=True, timeout=timeout).stdout.decode("utf-8")
    characters = re.findall(r'<char bbox="[^"]*" c="([^"]*)"/>', output)
    return "".join(html.unescape(value) for value in characters)


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(data.encode("utf-8"))
    try:
        if path.exists():
            temp.chmod(path.stat().st_mode & 0o777)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def prepare_changes(root, claims):
    require(isinstance(claims, list) and claims, "Declare each material numerical claim")
    sources, expected, ids, verified = {}, [], set(), {}

    def replace(site, patch):
        file = within(root, site["file"])
        require(file.suffix == ".tex", f"Expected a TeX source: {file}")
        if file not in sources:
            sources[file] = file.read_text(encoding="utf-8")
        old = site.get("old", patch)
        require(isinstance(old, str) and old.strip() and patch.strip(),
                f"Correction needs nonempty source and replacement: {file}")
        if sources[file].count(patch) == 1:
            if old not in patch:
                require(old not in sources[file], f"An old statement remains in {file}")
            return
        require(old != patch and sources[file].count(old) == 1, f"Expected exactly one old statement in {file}")
        sources[file] = sources[file].replace(old, patch, 1)

    for claim in claims:
        claim_id = prose(claim["id"])
        require(claim_id not in ids, f"Repeated claim ID: {claim_id}")
        ids.add(claim_id)
        roles = {item["role"] for item in claim["evidence"]}
        require(roles == {"count", "scope"}, f"{claim_id}: Declare evidence for the count and theorem scope")
        for evidence in claim["evidence"]:
            path = within(root, evidence["file"])
            prose(evidence["locator"])
            if path not in verified:
                verified[path] = digest(path)
            require(verified[path] == evidence["sha256"], f"{claim_id}: Evidence changed: {path}")
        count, total = claim["count"], claim["total"]
        require(type(count) is int and type(total) is int and total > 0 and 0 <= count <= total,
                f"{claim_id}: Invalid count or denominator")
        sentence = BASIS[claim["basis"]].format(
            count=count, total=total, source=prose(claim["source"]),
            unit=prose(claim["unit"]), event=prose(claim["event"]),
        )
        scope = prose(claim["scope"])
        replace(claim, latex(sentence + " " + scope))
        expected.append(sentence + " " + scope)
        for site in claim.get("also", []):
            replace(site, prose(site["new"]))
            expected.append(prose(site["pdf_text"]))
    return sources, expected, sorted(ids), verified


def finalize(root, plan, receipt, timeout):
    cwd = within(root, plan["cwd"])
    entry = within(cwd, plan["entry"])
    pdf = within(cwd, plan["pdf"])
    require(entry.is_file() and entry.suffix == ".tex" and pdf.suffix == ".pdf", "Invalid TeX entry or PDF")
    commands = plan["build"]
    require(isinstance(commands, list) and commands, "Declare the project's TeX build")
    for argv in commands:
        require(isinstance(argv, list) and argv and all(isinstance(x, str) for x in argv)
                and argv[0] in BUILD_TOOLS, "Build command must be a TeX tool with explicit arguments")
        require(not any("shell-escape" in x and "no-shell-escape" not in x for x in argv),
                "Build must use TeX without shell escape")

    sources, expected, ids, verified = prepare_changes(root, plan["claims"])
    original = {path: path.read_text(encoding="utf-8") for path in sources}
    changed = [path for path in sources if original[path] != sources[path]]
    with tempfile.TemporaryDirectory(prefix=".numerical-handoff-", dir=cwd) as backup:
        previous = Path(backup) / "previous.pdf"
        if pdf.exists():
            pdf.replace(previous)
        try:
            for path in changed:
                atomic_write(path, sources[path])
            for argv in commands:
                process = subprocess.run(argv, check=False, capture_output=True, text=True, timeout=timeout, cwd=cwd)
                if process.returncode:
                    raise ValueError(f"Build command failed ({process.returncode}): {argv}\n"
                                     + (process.stdout + process.stderr)[-4000:])
            require(pdf.is_file() and pdf.stat().st_size > 0, "Build did not emit the requested PDF")
            product = normalized(pdf_text(pdf, timeout))
            for passage in expected:
                require(contains_passage(product, passage), f"Rebuilt PDF is missing: {passage}")
        except BaseException:
            for path in changed:
                atomic_write(path, original[path])
            pdf.unlink(missing_ok=True)
            if previous.exists():
                previous.replace(pdf)
            raise
    result = {
        "status": "passed", "claims": ids, "changed": [str(path.relative_to(root)) for path in changed],
        "pdf": str(pdf.relative_to(root)),
        "pdf_sha256": digest(pdf), "sources": {str(path.relative_to(root)): digest(path) for path in sources},
        "evidence": {str(path.relative_to(root)): sha for path, sha in verified.items()},
    }
    atomic_write(receipt, json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("plan", help="JSON plan, relative to project")
    parser.add_argument("--receipt", default=".numerical-handoff.json", help="Path relative to project")
    parser.add_argument("--timeout", type=float, default=90, help="Max seconds per build command")
    args = parser.parse_args()
    root = args.project.resolve()
    try:
        plan_path = within(root, args.plan)
        receipt = within(root, args.receipt)
        require(receipt.suffix == ".json" and receipt != plan_path, "Receipt must be a separate JSON file")
        receipt.unlink(missing_ok=True)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        result = finalize(root, plan, receipt, args.timeout)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Numerical handoff did not pass: {exc}\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
