#!/usr/bin/env python3
"""Run the registered-delivery example and independently verify its output."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


EXAMPLE = Path(__file__).resolve().parent
REPO = EXAMPLE.parents[1]
DRIVER = REPO / "plugins/research-paper-workflow/skills/research-paper-workflow/scripts/deliver_manuscript.py"
EVIDENCE = EXAMPLE / "evidence"
MANUSCRIPT = "paper/main.tex"
PDF = "paper/main.pdf"
TRIALS = "replay/synthetic_trials.csv"


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, *, cwd=None, timeout=100):
    return subprocess.run(command, cwd=cwd, timeout=timeout, capture_output=True, text=True)


def publish(draft, profile, output):
    return run([
        sys.executable, "-B", str(DRIVER), "--project", str(draft), "--evidence", str(EVIDENCE),
        "--profile", str(profile), "--output", str(output), "--deadline-epoch", str(time.time() + 90),
    ])


def raster_hashes(pdf, directory):
    directory.mkdir()
    result = run([
        "gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=ppmraw", "-r110",
        f"-sOutputFile={directory / 'page-%04d.ppm'}", "-f", str(pdf),
    ])
    require(result.returncode == 0, result.stderr or "PDF rendering failed")
    pages = sorted(directory.glob("page-*.ppm"))
    require(pages, "The PDF contains no rendered pages")
    return [sha256(page) for page in pages]


def check(work, output):
    draft = work / "draft"
    shutil.copytree(EVIDENCE, draft)
    profile = EXAMPLE / "profile.json"
    original = {file: sha256(EVIDENCE / file) for file in (TRIALS, MANUSCRIPT)}
    result = publish(draft, profile, output)
    require(result.returncode == 0, result.stderr or "The registered delivery failed")
    receipt = json.loads((output / ".delivery-receipt.json").read_text(encoding="utf-8"))
    require(receipt["status"] == "passed" and receipt["profile_sha256"] == sha256(profile),
            "The accepted receipt is not bound to the registered profile")
    count, = receipt["counts"]
    require((count["count"], count["trials"], count["issued"], count["denominator"]) == (2, 6, 4, 6)
            and count["units"] == ["toy-1", "toy-2"],
            "The issued-and-strict count, identifiers or denominator are incorrect")
    require(receipt["source_evidence"] == original and sha256(output / TRIALS) == original[TRIALS]
            and receipt["scope"] == ["population-risk"],
            "The receipt lost the original evidence or the theorem scope")
    require(receipt["pdf"] == {"path": PDF, "sha256": sha256(output / PDF)}
            and receipt["sources"] == {MANUSCRIPT: sha256(output / MANUSCRIPT)},
            "The receipt does not bind the published TeX and PDF")
    manuscript = (output / MANUSCRIPT).read_text(encoding="utf-8")
    require(receipt["consolidated_restatements"] == [{"count": 2, "denominator": 6, "cell": {}}]
            and manuscript.count("2 of 6 teaching repetitions") == 1
            and "Our independent replay documented" not in manuscript
            and "19.25 percentage points" in manuscript
            and "fixed before calibration" in manuscript
            and "strictly above the risk budget of 0.20" in manuscript,
            "The manuscript did not retain one verified count, the MCSE and theorem conditions")

    clean = work / "clean"
    clean.mkdir()
    shutil.copyfile(output / MANUSCRIPT, clean / "main.tex")
    build = run(["latexmk", "-norc", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=clean)
    require(build.returncode == 0, build.stdout + build.stderr)
    pages = raster_hashes(output / PDF, work / "submitted-pages")
    require(pages == raster_hashes(clean / "main.pdf", work / "rebuilt-pages"),
            "The submitted pages differ from a clean rebuild")

    invalid = json.loads(profile.read_text(encoding="utf-8"))
    invalid["scope"][0]["anchors"] = [r"\label{missing-theorem}"]
    invalid_path = work / "invalid-profile.json"
    invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
    rejected = work / "rejected"
    negative = publish(draft, invalid_path, rejected)
    require(negative.returncode != 0 and not rejected.exists() and "theorem citation" in negative.stderr,
            "A profile with an invalid theorem locator was not rejected cleanly")
    require(all(sha256(EVIDENCE / file) == value and sha256(draft / file) == value
                for file, value in original.items()),
            "The delivery altered the evidence or the working draft")
    return {"strict_exceedances": 2, "issued": 4, "repetitions": 6,
            "matching_pdf_pages": len(pages), "removed_count_restatements": 1,
            "invalid_theorem_locator_rejected": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Save the verified bundle in a new directory")
    args = parser.parse_args()
    missing = [tool for tool in ("latexmk", "pdflatex", "gs") if shutil.which(tool) is None]
    require(not missing, f"Missing local commands: {', '.join(missing)}")
    require(DRIVER.is_file(), f"Expected the bundled delivery driver at {DRIVER.relative_to(REPO)}")
    output = args.output.resolve() if args.output else None
    require(output is None or not output.exists(), "Choose an output path that does not exist")
    with tempfile.TemporaryDirectory(prefix="registered-delivery-example-") as directory:
        work = Path(directory).resolve()
        report = check(work, output if output is not None else work / "delivered")
    if output is not None:
        report["output"] = str(output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
