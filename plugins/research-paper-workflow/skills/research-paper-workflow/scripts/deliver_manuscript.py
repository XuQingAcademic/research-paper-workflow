#!/usr/bin/env python3
"""Publish a risk-results manuscript only through its externally configured checks."""
from __future__ import annotations

import argparse
from collections import Counter
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(Path(__file__).resolve().parent),
    str(SKILLS / "write-econometrics-paper-v3/scripts"),
    str(SKILLS / "audit-numerical-simulations-v2/scripts"),
]
from finalize_numerical_handoff import (
    atomic_write, contains_passage, digest, latex, normalized, pdf_text, prose, require, within,
)
from verified_decisions import from_records
from verified_vector_evidence import count_plot
from merge_replay_prose import consolidate, describe_design, shared_fields


SOURCE_REPORT = {
    "replay": "the independent replay recorded in {source}",
    "full-records": "the original decision records in {source}",
}
CONTROL_TARGET = {
    "population-risk": "true population risk",
    "conditional-population-risk": "the population risk conditional on the calibration data",
    "expected-selected-loss": "the expected average loss among the selected cases",
    "false-equivalence-probability": "the probability of declaring equivalence at a fixed non-equivalent population effect",
    "finite-test": "the specified finite-test error",
}


def decide(evidence_root, profile, hashes):
    def artifact(name):
        path = within(evidence_root, name)
        hashes[name] = digest(path)
        return path

    rows, passages = [], []
    for rule in profile["experiments"]:
        if rule["basis"] == "vector":
            artifact(rule["legend"]["file"])
            legend = within(evidence_root, rule["legend"]["file"]).read_text(encoding="utf-8")
            require(all(hint in legend for hint in rule["legend"]["anchors"]), "Missing author color definition")
            for panel in rule["panels"]:
                path = artifact(panel["file"])
                counts = count_plot(path, panel["threshold"], panel.get("minimum_vertices", 2))
                name = panel["name"]
                rows.append({"panel": name, **counts})
                n = counts["plotted_calibration_runs"]
                event = prose(rule["event"])
                passages.append(
                    f"For {name}, the authors' color labels mark {counts['red_paths']} of {n} {rule['unit_label']} "
                    f"as having {event}. The archived vector curves directly confirm at least "
                    f"{counts['visible_strict_crossing_lower_bound']} of {n}. "
                    "The underlying decisions are unavailable for an exact independent recount."
                )
            continue
        path = artifact(rule["file"])
        require(rule["basis"] in SOURCE_REPORT, "Unsupported record lineage")
        source = prose(rule["source"])
        headline = SOURCE_REPORT[rule["basis"]].format(source=source)
        name, comma, description = source.partition(", ")
        if rule["basis"] == "replay" and Path(name).name == path.name and comma and "independent replay" in description:
            headline = f"{description}, documented in {name}"
        groups = from_records(path, rule)
        fixed = shared_fields(groups)
        measure = prose(rule["risk_label"])
        unit = prose(rule["unit_label"])
        threshold = prose(rule.get("threshold_label", "the budget"))
        explanation = (
            f"Counts use {headline}. A repetition counts when there is an actual release "
            f"and {measure} is strictly above {threshold}."
        )
        if all(group["issued"] == group["trials"] for group in groups):
            explanation += " Every repetition had an actual release."
        if fixed:
            explanation += f" The common design uses {describe_design(rule, fixed)}."
        passages.append(explanation)
        for group in groups:
            require(group["trials"] >= rule.get("min_trials", 1), "Insufficient decision units for a declared cell")
            n, issued, k = (group[k] for k in ("trials", "issued", "count"))
            design = describe_design(rule, {key: value for key, value in group["cell"].items() if key not in fixed})
            denominator = issued if rule.get("denominator") == "issued" and issued else n
            prefix = f"For {design}, " if design else ""
            count_text = f"{prefix}{k} of {denominator} {unit} met this criterion."
            if issued != n:
                if denominator == issued:
                    count_text += f" The experiment evaluated {n} {unit} in total."
                else:
                    count_text += f" Of the {n} repetitions, {issued} had an actual release."
            passages.append(count_text)
            rows.append({**group, "denominator": denominator, "measurement": measure,
                         "source": rule["file"], "predicate": "issued && true quantity > threshold"})
    require(rows, "At least one evidence-backed experiment is required")
    return rows, passages


def read_scope(evidence_root, scope, hashes):
    for citation in [scope, *scope.get("related", [])]:
        key = citation["file"]
        path = within(evidence_root, key)
        hashes[key] = digest(path)
        author = path.read_text(encoding="utf-8")
        anchors = citation["anchors"]
        require(anchors and all(author.count(anchor) == 1 for anchor in anchors),
                "The theorem citation is missing or ambiguous in the original source")
    category = scope["controls"]
    target = CONTROL_TARGET[category]
    name = prose(scope["name"])
    guarantee = prose(scope["guarantee"])
    assumptions = prose(scope["assumptions"])
    passage = f"The controlled quantity for {name} is {target}. {guarantee} {assumptions}"
    if category not in {"finite-test", "false-equivalence-probability"}:
        passage += " A finite-test empirical error is a separate observed quantity."
    if scope.get("relation"):
        passage += " " + prose(scope["relation"])
    return passage


def finish_before(deadline):
    remaining = deadline - time.time()
    require(remaining > 0, "Manuscript delivery deadline expired")
    return remaining


def command_list(build):
    commands = build.get("commands") or [build["argv"]]
    safe = []
    for argv in commands:
        require(argv and argv[0] in {"latexmk", "pdflatex", "xelatex", "lualatex", "bibtex", "biber"},
                "The registered build must use a supported TeX tool")
        require(not any("shell-escape" in x and "no-shell-escape" not in x for x in argv),
                "The registered build may not enable shell escape")
        extra = {"latexmk": ["-norc", "-g", "-no-shell-escape"], "bibtex": [], "biber": []}
        safe.append([argv[0], *extra.get(argv[0], ["-no-shell-escape"]), *argv[1:]])
    return safe


def edit_manuscript(stage, profile, passages, counts):
    changed, mandatory_readback = set(), []
    for edit in profile.get("repairs", []):
        path = within(stage, edit["file"])
        before = path.read_text(encoding="utf-8")
        replacement = latex(prose(edit["text"])) if "text" in edit else edit.get("tex", "")
        after, count = re.subn(edit["pattern"], lambda _: replacement, before, flags=re.M)
        require(edit.get("min", 0) <= count <= edit.get("max", 25),
                f"Correction ambiguous in {edit['file']}: {edit['pattern'][:120]}")
        if count:
            atomic_write(path, after)
            changed.add(path)
            if edit.get("pdf_text"):
                mandatory_readback.append(edit["pdf_text"])
    for guard in profile.get("guards", []):
        source = within(stage, guard["file"]).read_text(encoding="utf-8")
        require(not re.search(guard["pattern"], source, re.M),
                f"Unresolved numerical or theorem wording in {guard['file']}: {guard['pattern'][:120]}")

    location = profile["location"]
    path = within(stage, location["file"])
    before = path.read_text(encoding="utf-8")
    anchor = location["anchor"]
    current = re.sub(r"(?ms)^% BEGIN VERIFIED RESULTS\n.*?^% END VERIFIED RESULTS\n", "", before)
    require(current.count(anchor) == 1, f"Evidence insertion entry is missing or ambiguous in {location['file']}")
    current, removed = consolidate(current, anchor, location, counts, profile)
    # The verified passages are short. Keep each together so a float page
    # cannot interrupt a count, its provenance, or a scope qualifier.
    content = "\n\n".join("\\begin{samepage}\n" + latex(s) + "\\par\n\\end{samepage}"
                            for s in passages)
    block = "\n\n% BEGIN VERIFIED RESULTS\n\\noindent\\textbf{Observed releases and scope of the guarantee.}\n" + content
    block += "\n% END VERIFIED RESULTS\n"
    current = current.replace(anchor, block + anchor if location.get("position", "before") == "before" else anchor + block, 1)
    atomic_write(path, current)
    changed.add(path)
    return changed, mandatory_readback, removed


def verify_passage(product, passage):
    """Check ordered readable fragments across a PDF page or column boundary."""
    if contains_passage(product, passage):
        return True
    words = passage.split()
    if len(words) < 8:
        return False
    # In a long generated paragraph a page header, footer or float can
    # interrupt the text stream. Keep the start and successive text local.
    for size in (8, 6, 5, 4):
        fragments = [normalized(" ".join(words[i:i + size])) for i in range(0, len(words), size)]
        start = product.find(fragments[0])
        while start >= 0:
            end = start + len(fragments[0])
            for fragment in fragments[1:]:
                next_part = product.find(fragment, end, end + 5000 + len(fragment))
                if next_part < 0:
                    break
                end = next_part + len(fragment)
            else:
                return True
            start = product.find(fragments[0], start + 1)
    return False


def readback_text(text, profile):
    # Some TeX fonts paint escaped underscores as rules. Allow that extraction
    # equivalent only for declared evidence filenames, never math or numbers.
    for experiment in profile["experiments"]:
        if "file" not in experiment:
            continue
        filename = Path(experiment["file"]).name
        if "_" in filename:
            text = text.replace(filename, filename.replace("_", ""))
    return text


def structured_pdf_text(path, timeout):
    if not shutil.which("gs"):
        return pdf_text(path, timeout)
    argv = ["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=txtwrite",
            "-dTextFormat=0", "-sOutputFile=-", str(path)]
    layout = subprocess.run(argv, check=True, capture_output=True, timeout=timeout).stdout.decode("utf-8")
    char_pattern = r'<char bbox="[^"]*" c="([^"]*)"/>'
    span_pattern = r'<span [^>]*bbox="([^"]+)"[^>]*>(.*?)</span>'
    pages = []
    for content in re.findall(r"<page>(.*?)</page>", layout, re.S):
        spans = [(box, "".join(html.unescape(n) for n in re.findall(char_pattern, span)))
                 for box, span in re.findall(span_pattern, content, re.S)]
        pages.append(spans)
    if not pages:
        return pdf_text(path, timeout)

    # Distinguish repeated folios from data. An isolated integer at a common
    # page-edge position must track the physical page index on multiple pages.
    matched = {}
    for index, spans in enumerate(pages, 1):
        if len(spans) < 3:
            continue
        for edge, number, neighbor in (("header", 0, 1), ("footer", -1, -2)):
            box, printed = spans[number]
            baseline = float(box.split()[1])
            next_baseline = float(spans[neighbor][0].split()[1])
            if printed.strip().isascii() and printed.strip().isdigit() and abs(baseline - next_baseline) >= 16:
                signature = (edge, round(baseline), int(printed) - index)
                matched[index, number % len(spans)] = signature
    repeated = Counter(matched.values())
    return "".join(
        words for index, spans in enumerate(pages, 1) for position, (_, words) in enumerate(spans)
        if repeated[matched.get((index, position))] < 3
    )


def publish(project, evidence, profile_path, output, deadline):
    require(not output.exists(), "The controlled delivery destination already exists")
    require(project != evidence and not output.is_relative_to(project) and not output.is_relative_to(evidence),
            "Use separate source, independent evidence, and controlled output directories")
    require(not profile_path.is_relative_to(project), "The release configuration must be outside the draft workspace")
    require(not any(path.is_symlink() for path in project.rglob("*")), "Draft contains an external or symbolic path")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    build = profile["build"]
    hashes = {}
    counts, passages = decide(evidence, profile, hashes)
    for edit in profile.get("repairs", []):
        for evidence_file in edit.get("basis_files", []):
            hashes[evidence_file] = digest(within(evidence, evidence_file))
    scopes = [read_scope(evidence, scope, hashes) for scope in profile["scope"]]
    require(scopes, "A registered theorem scope is mandatory")
    passages.extend(scopes)
    for item in profile.get("context", []):
        passages.append(prose(item))
    output.parent.mkdir(parents=True, exist_ok=True)
    finish_before(deadline)
    with tempfile.TemporaryDirectory(prefix=".controlled-delivery-", dir=output.parent) as temporary:
        stage = Path(temporary) / "manuscript"
        shutil.copytree(project, stage)
        result_record = stage / ".delivery-receipt.json"
        result_record.unlink(missing_ok=True)
        changed, required_readback, removed = edit_manuscript(stage, profile, passages, counts)
        cwd = within(stage, build["cwd"])
        entry = within(cwd, build["entry"])
        pdf = within(cwd, build["pdf"])
        require(entry.is_file() and entry.suffix == ".tex" and pdf.suffix == ".pdf",
                "No valid source/PDF delivery entry")
        # Keep the frozen decision artifacts identical in the delivered project.
        for name in hashes:
            source = within(evidence, name)
            if source.suffix == ".tex":
                continue
            target = within(stage, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        pdf.unlink(missing_ok=True)
        env = {**os.environ, "openin_any": "p", "openout_any": "p"}
        for argv in command_list(build):
            try:
                command = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True,
                                         timeout=finish_before(deadline))
            except subprocess.TimeoutExpired as error:
                raise ValueError("Controlled PDF build ran out of delivery time") from error
            if command.returncode:
                raise ValueError(f"Build returned {command.returncode}: {(command.stdout + command.stderr)[-2600:]}")
        require(pdf.is_file(), "The authoritative build did not emit a PDF")
        rendering = structured_pdf_text(pdf, finish_before(deadline))
        product = normalized(readback_text(rendering, profile))
        for passage in [*passages, *required_readback]:
            sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", passage)
            for sentence in sentences:
                require(verify_passage(product, readback_text(sentence, profile)),
                        f"Required text not found in rebuilt PDF: {sentence[:180]}")
        report = {
            "status": "passed", "profile_sha256": digest(profile_path), "source_evidence": hashes,
            "counts": counts, "scope": [s["controls"] for s in profile["scope"]],
            "consolidated_restatements": removed,
            "pdf": {"path": str(pdf.relative_to(stage)), "sha256": digest(pdf)},
            "sources": {str(p.relative_to(stage)): digest(p) for p in sorted(changed | {entry})},
            "finished_epoch": time.time(),
        }
        atomic_write(result_record, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        finish_before(deadline)
        stage.rename(output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("project", "evidence", "profile", "output"):
        parser.add_argument(f"--{arg}", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=float, default=None)
    args = parser.parse_args()
    deadline = args.deadline_epoch if args.deadline_epoch is not None else time.time() + 90
    try:
        report = publish(args.project.resolve(), args.evidence.resolve(), args.profile.resolve(),
                         args.output.resolve(), deadline)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Manuscript delivery rejected: {error}\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
