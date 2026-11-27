from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from claim_coverage import scan_project, render_report


class ClaimCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "paper"
        self.root.mkdir()
        (self.root / ".paper").mkdir()

    def write(self, text, claims=None, filename="main.md"):
        (self.root / filename).write_text(text, encoding="utf-8")
        (self.root / ".paper/claims.yaml").write_text(json.dumps({"schema_version": 1, "claims": claims or []}), encoding="utf-8")
        return scan_project(self.root, main=filename)

    def claim(self, location, **kw):
        return {"id": "C1", "status": "needs-evidence", "locations": [location], **kw}

    def test_unregistered_compound_and_exact_source_lines(self):
        report = self.write("# Results\n\nThe estimate is 0.25, and the effect increases by 12%.\nThe sample contains 300 observations.\n")
        self.assertEqual(report["counts"]["gap"], 2)
        self.assertEqual(report["candidates"][0]["line"], 3)
        self.assertEqual(report["candidates"][0]["text"], "The estimate is 0.25, and the effect increases by 12%.")
        self.assertIn("numeric_unit", report["candidates"][0]["signals"])

    def test_exact_location_maps_but_does_not_verify_science(self):
        text = "The estimate is 0.25."
        report = self.write(text, [self.claim({"path": "main.md", "line": 1, "text": text})])
        candidate = report["candidates"][0]
        self.assertEqual(candidate["registration"], "registered")
        self.assertEqual(candidate["mappings"][0]["scientific_status"], "needs-evidence")
        self.assertEqual(report["counts"]["error"], 0)

    def test_legacy_precise_and_unique_text_locators(self):
        text = "The estimate is 0.25."
        for loc, other in [("main.md:1", {"summary": text}), ("main.md#L1-L1", {"allowed_wording": text}), ({"path": "main.md", "text": text}, {})]:
            with self.subTest(location=loc):
                report = self.write(text, [self.claim(loc, **other)])
                self.assertEqual(report["counts"]["registered"], 1)

    def test_partial_quote_does_not_cover_compound_sentence(self):
        report = self.write("The estimate is 0.25, and the effect increases by 12%.", [self.claim({"path": "main.md", "line": 1, "text": "The estimate is 0.25"})])
        self.assertEqual(report["counts"]["partial"], 1)
        self.assertEqual(report["counts"]["registered"], 0)

    def test_formula_year_code_comment_and_headings_not_candidates(self):
        text = r'''# We find 99% gains
The survey took place in 2020.
The date was 2020-09-12.
Let $x=0.25$ and $y=12$.
See equation (12).
$$
p < 0.05, N=300, 50%
$$
<!-- Results show 70% gains. -->
```python
p = 0.01
print("We find 40%")
```
`p = 0.01`
'''
        self.assertEqual(self.write(text)["counts"]["candidates"], 0)
        tex = r'''\section{We find 99\% gains}
% We find 80\% gains.
\begin{equation}
p < 0.05 \label{eq:99}
\end{equation}
\[ N=500 \]
Let $x=0.5$; see \eqref{eq:99}.
\begin{verbatim}
We find 30% gains.
\end{verbatim}
'''
        self.assertEqual(self.write(tex, filename="main.tex")["counts"]["candidates"], 0)

    def test_chinese_decimal_p_value_sample_and_latex_cite(self):
        text = r'''样本量为1200，估计系数为0.125。结果表明效应显著提高。
The earlier work \citep[see][p. 12]{smith2020} gives context.
We observe $p < .05$ with $N = 300$.
'''
        report = self.write(text, filename="main.tex")
        signals = set(s for c in report["candidates"] for s in c["signals"])
        self.assertTrue({"sample_size", "decimal", "result_wording", "citation", "p_value"}.issubset(signals))
        self.assertTrue(any("0.125" in c["text"] for c in report["candidates"]))

    def test_latex_citation_with_optional_period_is_preserved(self):
        report = self.write(r"Earlier work \citep[see][p. 12]{smith2020} gives context.", filename="main.tex")
        self.assertEqual(report["counts"]["candidates"], 1)
        self.assertIn(r"\citep[see][p. 12]{smith2020}", report["candidates"][0]["text"])

    def test_stale_broad_ambiguous_locators_do_not_hide_gaps(self):
        text = "The estimate is 0.25.\nThe estimate is 0.25.\n"
        for loc in ["main.md#results", "main.md", {"path": "main.md", "line": 99, "text": "The estimate is 0.25."}, {"path": "main.md", "line": 1, "text": "The estimate is 0.75."}, {"path": "main.md", "text": "The estimate is 0.25."}]:
            with self.subTest(location=loc):
                report = self.write(text, [self.claim(loc, summary="The estimate is 0.25.")])
                self.assertEqual(report["counts"]["gap"], 2)
                self.assertEqual(report["counts"]["unresolved_locators"], 1)

    def test_multiline_sentence_range(self):
        text = "The estimate is\n0.25.\n"
        report = self.write(text, [self.claim({"path": "main.md", "start_line": 1, "end_line": 2, "text": "The estimate is 0.25."})])
        self.assertEqual(report["counts"]["registered"], 1)
        self.assertEqual(report["candidates"][0]["end_line"], 2)
        self.assertEqual(report["candidates"][0]["text"], "The estimate is\n0.25.")

    def test_excluded_code_does_not_create_include_dependencies(self):
        text = "\\begin{verbatim}\n\\input{missing}\n\\end{verbatim}\nThe estimate is 0.25."
        report = self.write(text, filename="main.tex")
        self.assertEqual(report["counts"]["error"], 0)
        self.assertEqual(report["counts"]["candidates"], 1)

    def test_selected_scope_and_graph(self):
        (self.root / "a.tex").write_text("The estimate is 0.25.")
        self.write("\\input{a}\nThe effect is 12\\%.", filename="main.tex")
        report = scan_project(self.root, main="main.tex", paths=["a.tex"])
        self.assertEqual(report["coverage"]["scope"], "selected-paths")
        self.assertEqual(report["coverage"]["status"], "partial")
        self.assertEqual(report["coverage"]["whole_manuscript_coverage"], "unknown")
        self.assertEqual(report["coverage"]["unscanned_paths"], ["main.tex"])
        self.assertEqual(report["counts"]["candidates"], 1)

    def test_escape_and_external_symlinks_rejected(self):
        self.write("The estimate is 0.25.")
        outside = self.root.parent / "outside.md"
        outside.write_text("The estimate is 0.75.")
        (self.root / "escape.md").symlink_to(outside)
        for kwargs in [{"main": "../outside.md"}, {"main": str(outside)}, {"main": "escape.md"}, {"main": "main.md", "paths": ["../outside.md"]}]:
            with self.subTest(kwargs=kwargs):
                report = scan_project(self.root, **kwargs)
                self.assertEqual(report["counts"]["error"], 1)
                self.assertIsNone(report["counts"]["gap"])
                self.assertNotIn("outside.md", report["input_hashes"])
        ledger = self.root / ".paper/claims.yaml"
        ledger.unlink()
        ledger.symlink_to(outside)
        self.assertEqual(scan_project(self.root, main="main.md")["counts"]["error"], 1)

    def test_ledger_location_escape_rejected(self):
        report = self.write("The estimate is 0.25.", [self.claim("../outside.md:1", summary="The estimate is 0.25.")])
        self.assertEqual(report["counts"]["error"], 1)

    def test_missing_ledger_is_unknown_not_zero_gaps(self):
        self.write("The estimate is 0.25.")
        (self.root / ".paper/claims.yaml").unlink()
        report = scan_project(self.root, main="main.md")
        self.assertIsNone(report["counts"]["gap"])
        self.assertEqual(report["candidates"][0]["registration"], "unknown")

    def test_malformed_structure_and_cli_exit_codes(self):
        self.write("The estimate is 0.25.")
        cmd = [sys.executable, str(SCRIPTS / "claim_coverage.py"), str(self.root), "--format", "json"]
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        for payload in ["{", '[]', '{}', '{"claims": {}}', '{"claims":[{"id":"C1", "locations":"main.md"}]}']:
            (self.root / ".paper/claims.yaml").write_text(payload)
            completed = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(json.loads(completed.stdout)["counts"]["error"], 1)

    def test_read_only_hashes_stable_and_input_change_visible(self):
        self.write("The estimate is 0.25.")
        def snapshot():
            return {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        first = scan_project(self.root)
        self.assertIn("main.md", first["input_hashes"])
        self.assertEqual(first["input_hashes"]["main.md"], hashlib.sha256(b"The estimate is 0.25.").hexdigest())
        self.assertIn("Advisory", render_report(first))
        second = scan_project(self.root)
        self.assertEqual(before, snapshot())
        self.assertEqual(first, second)
        (self.root / "main.md").write_text("The estimate is 0.75.")
        self.assertNotEqual(first["input_sha256"], scan_project(self.root)["input_sha256"])


if __name__ == "__main__":
    unittest.main()
