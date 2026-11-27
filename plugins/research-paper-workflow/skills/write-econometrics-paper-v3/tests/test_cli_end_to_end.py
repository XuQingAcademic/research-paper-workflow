from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class CliEndToEndTests(unittest.TestCase):
    def run_cli(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / script), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_coverage_is_advisory_but_invalid_scope_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp)
            (paper / "main.md").write_text("# Results\n\nThe estimate is 0.25.\n")
            initialized = self.run_cli("init_paper_state.py", "--paper-dir", str(paper),
                                      "--paper-type", "pure-theory", "--main-file", "main.md")
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            before = self.run_cli("audit_paper_project.py", str(paper), "--format", "json")
            scanned = self.run_cli("audit_paper_project.py", str(paper), "--format", "json", "--claim-coverage")
            self.assertEqual(scanned.returncode, before.returncode)
            self.assertGreater(json.loads(scanned.stdout)["claim_coverage"]["counts"]["gap"], 0)
            invalid = self.run_cli("audit_paper_project.py", str(paper), "--format", "json",
                                   "--claim-coverage", "--coverage-path", "../outside.md")
            self.assertEqual(invalid.returncode, 2)
            self.assertGreater(json.loads(invalid.stdout)["claim_coverage"]["counts"]["error"], 0)

    def test_combined_coverage_uses_audit_main_selection(self):
        for files in [{'article.tex':r'\documentclass{article}\begin{document}The estimate is 0.25.\end{document}'},
                      {'main.md':'The estimate is 0.25.', 'paper.md':'A second draft.'}]:
            with tempfile.TemporaryDirectory() as tmp:
                paper=Path(tmp)
                for name,text in files.items(): (paper/name).write_text(text)
                old=self.run_cli('audit_paper_project.py',str(paper),'--format','json')
                new=self.run_cli('audit_paper_project.py',str(paper),'--format','json','--claim-coverage')
                a,b=json.loads(old.stdout),json.loads(new.stdout)
                self.assertEqual(b['claim_coverage']['counts']['error'],0)
                self.assertEqual(a['main_file'],b['claim_coverage']['main_file'])
                self.assertEqual(old.returncode,new.returncode)

    def test_combined_coverage_rejects_external_state_before_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent=Path(tmp);paper=parent/'project';paper.mkdir();(paper/'.paper').mkdir()
            (paper/'main.md').write_text('The estimate is 0.25.')
            (parent/'outside.yaml').write_text('{"claims":[{"id":"OUTSIDE-PROJECT-MARKER","status":"invalid"}]}')
            (paper/'.paper/claims.yaml').symlink_to(parent/'outside.yaml')
            result=self.run_cli('audit_paper_project.py',str(paper),'--claim-coverage','--format','json')
            self.assertEqual(result.returncode,2)
            self.assertNotIn('OUTSIDE-PROJECT-MARKER',result.stdout+result.stderr)
            self.assertIn('preflight',result.stderr)

    def test_initialize_audit_freeze_and_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp)
            (paper / "main.md").write_text(
                """# Abstract

We establish a bounded result.

# Introduction

The paper studies a defined target.

# Setup

The target and assumptions are stated here.

# Theory

The main proposition gives the bounded result.

# Conclusion

The conclusion retains the stated scope.
""",
                encoding="utf-8",
            )
            initialized = self.run_cli(
                "init_paper_state.py",
                "--paper-dir",
                str(paper),
                "--paper-type",
                "pure-theory",
                "--main-file",
                "main.md",
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)

            (paper / ".paper" / "claims.yaml").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "claims": [
                            {
                                "id": "C001",
                                "claim_type": "theory",
                                "summary": "Bounded result",
                                "allowed_wording": "bounded",
                                "forbidden_stronger_wording": ["uniform"],
                                "status": "supported",
                                "evidence_ids": ["T001"],
                                "locations": ["main.md#theory"],
                                "scope": "stated assumptions",
                                "risk": "",
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (paper / ".paper" / "exhibits.yaml").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "exhibits": [
                            {
                                "id": "T001",
                                "type": "theorem",
                                "label": "",
                                "path": "main.md",
                                "producer": "",
                                "supports_claims": ["C001"],
                                "status": "verified",
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            draft = self.run_cli(
                "audit_paper_project.py",
                str(paper),
                "--format",
                "json",
            )
            self.assertEqual(draft.returncode, 0, draft.stdout + draft.stderr)
            self.assertEqual(json.loads(draft.stdout)["counts"]["error"], 0)

            citations = self.run_cli(
                "check_citations.py",
                str(paper),
                "--format",
                "json",
            )
            self.assertEqual(
                citations.returncode,
                0,
                citations.stdout + citations.stderr,
            )

            frozen = self.run_cli(
                "freeze_candidate.py",
                str(paper),
                "--frozen-by",
                "test-author",
            )
            self.assertEqual(frozen.returncode, 0, frozen.stdout + frozen.stderr)

            state_path = paper / ".paper" / "paper_state.yaml"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["release"].update(
                {
                    "human_approved": True,
                    "human_approved_by": "test-author",
                    "human_approved_at": "2026-08-15T00:00:00+00:00",
                }
            )
            state_path.write_text(
                json.dumps(state, indent=2) + "\n",
                encoding="utf-8",
            )

            release = self.run_cli(
                "audit_paper_project.py",
                str(paper),
                "--release",
                "--format",
                "json",
            )
            self.assertEqual(
                release.returncode,
                0,
                release.stdout + release.stderr,
            )
            self.assertEqual(
                json.loads(release.stdout)["counts"]["error"],
                0,
            )


if __name__ == "__main__":
    unittest.main()
