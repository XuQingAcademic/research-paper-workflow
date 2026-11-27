from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _paperlib import (  # noqa: E402
    audit_project,
    collect_project,
    load_json_yaml,
    project_fingerprint,
    write_json_yaml,
)
from init_paper_state import initialize  # noqa: E402


class ProjectToolTests(unittest.TestCase):
    def make_project(self, root: Path) -> None:
        (root / "sections").mkdir()
        (root / "main.tex").write_text(
            r"""\documentclass{article}
\addbibresource{references.bib}
\begin{document}
\begin{abstract}
We establish a pointwise result under Assumption A.
\end{abstract}
\section{Introduction}
The result builds on prior work \cite{sample2020}.
\input{sections/setup}
\input{sections/theory}
\section{Conclusion}
The conclusion preserves the pointwise scope.
\end{document}
""",
            encoding="utf-8",
        )
        (root / "sections" / "setup.tex").write_text(
            r"""\section{Setup}
The target is a conditional quantile.
""",
            encoding="utf-8",
        )
        (root / "sections" / "theory.tex").write_text(
            r"""\section{Theory}
\begin{theorem}\label{thm:main}
The statistic converges pointwise.
\end{theorem}
""",
            encoding="utf-8",
        )
        (root / "references.bib").write_text(
            """@article{sample2020,
  author = {A. Author},
  title = {A Verified Example},
  year = {2020},
  journal = {Example Journal}
}
""",
            encoding="utf-8",
        )
        args = SimpleNamespace(
            paper_dir=root,
            main_file="main.tex",
            paper_type="pure-theory",
            journal="",
            language="English",
            confidentiality="unpublished-local",
        )
        created, skipped = initialize(args)
        self.assertEqual(len(created), 7)
        self.assertEqual(skipped, [])

        write_json_yaml(
            root / ".paper" / "claims.yaml",
            {
                "schema_version": 1,
                "claims": [
                    {
                        "id": "C001",
                        "claim_type": "inference",
                        "summary": "Pointwise convergence",
                        "allowed_wording": "pointwise",
                        "forbidden_stronger_wording": ["uniform"],
                        "status": "supported",
                        "evidence_ids": ["T001", "E001"],
                        "locations": ["sections/theory.tex"],
                        "scope": "Assumption A",
                        "risk": "",
                    }
                ],
            },
        )
        write_json_yaml(
            root / ".paper" / "exhibits.yaml",
            {
                "schema_version": 1,
                "exhibits": [
                    {
                        "id": "T001",
                        "type": "theorem",
                        "label": "thm:main",
                        "path": "sections/theory.tex",
                        "producer": "",
                        "supports_claims": ["C001"],
                        "status": "verified",
                    }
                ],
            },
        )
        write_json_yaml(
            root / ".paper" / "citations.yaml",
            {
                "schema_version": 1,
                "citations": [
                    {
                        "id": "E001",
                        "citation_key": "sample2020",
                        "title": "A Verified Example",
                        "authors": ["A. Author"],
                        "year": 2020,
                        "venue": "Example Journal",
                        "doi": "",
                        "url": "https://example.org/paper",
                        "version": "journal",
                        "metadata_status": "verified",
                        "metadata_source": "publisher page",
                        "claim_support_status": "verified",
                        "supports_claims": ["C001"],
                        "locator": "Section 2",
                        "checked_by": "tester",
                        "checked_at": "2026-08-15",
                        "notes": "",
                    }
                ],
            },
        )

    def test_initializer_preserves_existing_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.tex").write_text(
                r"\documentclass{article}",
                encoding="utf-8",
            )
            args = SimpleNamespace(
                paper_dir=root,
                main_file="main.tex",
                paper_type="pure-theory",
                journal="",
                language="English",
                confidentiality="unpublished-local",
            )
            initialize(args)
            state_path = root / ".paper" / "paper_state.yaml"
            state_path.write_text('{"sentinel": true}\n', encoding="utf-8")
            created, skipped = initialize(args)
            self.assertEqual(created, [])
            self.assertEqual(len(skipped), 7)
            self.assertEqual(
                json.loads(state_path.read_text(encoding="utf-8")),
                {"sentinel": True},
            )

    def test_multifile_project_passes_draft_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            report = audit_project(root)
            errors = [
                item for item in report["issues"]
                if item["severity"] == "error"
            ]
            self.assertEqual(errors, [])
            self.assertEqual(report["metrics"]["source_files"], 3)
            self.assertEqual(report["metrics"]["citation_keys"], 1)

    def test_release_hash_detects_post_freeze_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            snapshot = collect_project(root)
            digest, files = project_fingerprint(snapshot)
            state_path = root / ".paper" / "paper_state.yaml"
            state = load_json_yaml(state_path)
            state["release"].update(
                {
                    "candidate_sha256": digest,
                    "candidate_files": files,
                    "frozen_at": "2026-08-15T00:00:00+00:00",
                    "frozen_by": "tester",
                    "audit_errors": 0,
                    "audit_warnings": 0,
                    "human_approved": True,
                    "human_approved_by": "author",
                    "human_approved_at": "2026-08-15T00:01:00+00:00",
                }
            )
            write_json_yaml(state_path, state)
            release_report = audit_project(root, release=True)
            self.assertEqual(release_report["counts"]["error"], 0)

            with (root / "sections" / "theory.tex").open(
                "a", encoding="utf-8"
            ) as handle:
                handle.write("\nA post-freeze edit.\n")
            changed = audit_project(root, release=True)
            codes = {item["code"] for item in changed["issues"]}
            self.assertIn("CANDIDATE_HASH_MISMATCH", codes)

    def test_missing_bibliography_key_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            (root / "main.tex").write_text(
                (root / "main.tex").read_text(encoding="utf-8").replace(
                    "sample2020", "missing2026"
                ),
                encoding="utf-8",
            )
            report = audit_project(root)
            codes = {item["code"] for item in report["issues"]}
            self.assertIn("CITE_UNDEFINED", codes)

    def test_nonrelease_state_change_invalidates_frozen_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            snapshot = collect_project(root)
            digest, files = project_fingerprint(snapshot)
            state_path = root / ".paper" / "paper_state.yaml"
            state = load_json_yaml(state_path)
            state["release"].update(
                {
                    "candidate_sha256": digest,
                    "candidate_files": files,
                    "human_approved": True,
                }
            )
            write_json_yaml(state_path, state)
            self.assertEqual(
                audit_project(root, release=True)["counts"]["error"],
                0,
            )
            state = load_json_yaml(state_path)
            state["locked_decisions"].append(
                {"id": "L001", "text": "Keep pointwise scope."}
            )
            write_json_yaml(state_path, state)
            codes = {
                item["code"]
                for item in audit_project(root, release=True)["issues"]
            }
            self.assertIn("CANDIDATE_HASH_MISMATCH", codes)

    def test_high_risk_claim_language_is_diagnostic_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            with (root / "main.tex").open("a", encoding="utf-8") as handle:
                handle.write("\nWe are the first to establish a robust result.\n")
            report = audit_project(root)
            findings = [
                item
                for item in report["issues"]
                if item["code"] == "HIGH_RISK_CLAIM_LANGUAGE"
            ]
            self.assertGreaterEqual(len(findings), 1)
            self.assertTrue(
                all(item["severity"] == "warning" for item in findings)
            )

    def test_declared_forbidden_variant_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            state_path = root / ".paper" / "paper_state.yaml"
            state = load_json_yaml(state_path)
            state["canonical_terms"] = [
                {
                    "canonical": "pointwise validity",
                    "forbidden_variants": ["uniformly valid"],
                    "provenance": {
                        "kind": "literature",
                        "citation_keys": ["Source2026"],
                        "source_locator": "Source2026, Definition 1",
                    },
                }
            ]
            write_json_yaml(state_path, state)
            with (root / "main.tex").open("a", encoding="utf-8") as handle:
                handle.write("\nThe method is uniformly valid.\n")
            report = audit_project(root)
            codes = {item["code"] for item in report["issues"]}
            self.assertIn("FORBIDDEN_TERM_VARIANT", codes)

    def test_canonical_term_provenance_is_warning_in_draft_and_error_at_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            state_path = root / ".paper" / "paper_state.yaml"
            state = load_json_yaml(state_path)
            state["canonical_terms"] = [
                {"canonical": "new label", "forbidden_variants": []}
            ]
            write_json_yaml(state_path, state)
            draft = [item for item in audit_project(root)["issues"] if item["code"] == "TERM_PROVENANCE_MISSING"]
            released = [item for item in audit_project(root, release=True)["issues"] if item["code"] == "TERM_PROVENANCE_MISSING"]
            self.assertEqual([item["severity"] for item in draft], ["warning"])
            self.assertEqual([item["severity"] for item in released], ["error"])

    def test_literature_and_author_defined_term_provenance_passes_structure_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            state_path = root / ".paper" / "paper_state.yaml"
            state = load_json_yaml(state_path)
            state["canonical_terms"] = [
                {
                    "canonical": "conditional moment restriction",
                    "forbidden_variants": [],
                    "provenance": {
                        "kind": "literature",
                        "citation_keys": ["Source2026"],
                        "source_locator": "Source2026, Section 2",
                    },
                },
                {
                    "canonical": "descriptive term",
                    "forbidden_variants": [],
                    "provenance": {
                        "kind": "author-defined",
                        "maps_to": ["nearest literature term"],
                        "reason": "The maintained object has a different conditioning set.",
                        "decision_locator": ".paper/revisions.yaml#TERM-01",
                    },
                },
            ]
            write_json_yaml(state_path, state)
            codes = {item["code"] for item in audit_project(root)["issues"]}
            self.assertNotIn("TERM_PROVENANCE_MISSING", codes)

    def test_external_latex_input_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "paper"
            root.mkdir()
            (parent / "outside.tex").write_text(
                r"\section{Outside}",
                encoding="utf-8",
            )
            (root / "main.tex").write_text(
                "\\documentclass{article}\n"
                "\\begin{document}\n"
                "\\input{../outside}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            args = SimpleNamespace(
                paper_dir=root,
                main_file="main.tex",
                paper_type="pure-theory",
                journal="",
                language="English",
                confidentiality="unpublished-local",
            )
            initialize(args)
            report = audit_project(root)
            codes = {item["code"] for item in report["issues"]}
            self.assertIn("EXTERNAL_INPUT_BLOCKED", codes)
            self.assertEqual(report["metrics"]["source_files"], 1)

    def test_continuous_revision_accepted_is_release_closed_but_deferred_is_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            revisions_path = root / ".paper" / "revisions.yaml"
            review_path = root / "reviews" / "REV-AUTO-1.json"
            review_path.parent.mkdir()
            review_path.write_text('{"verdict":"accepted"}\n', encoding="utf-8")
            review_sha256 = hashlib.sha256(review_path.read_bytes()).hexdigest()
            write_json_yaml(
                revisions_path,
                {
                    "schema_version": 1,
                    "revisions": [
                        {
                            "id": "REV-AUTO-1",
                            "cycle_id": "cycle-1",
                            "status": "accepted",
                            "severity": "P1",
                            "implementation": {
                                "worker_id": "writer-1",
                                "locators": ["sections/theory.tex"],
                                "attempts": 1,
                            },
                            "verification": {
                                "review_path": "reviews/REV-AUTO-1.json",
                                "review_sha256": review_sha256,
                                "verdict": "accepted",
                                "reviewer_id": "reviewer-1",
                                "reviewer_context_id": "fresh-review-context-1",
                                "candidate_sha256": "a" * 64,
                            },
                        }
                    ],
                },
            )
            snapshot = collect_project(root)
            digest, files = project_fingerprint(snapshot)
            state_path = root / ".paper" / "paper_state.yaml"
            state = load_json_yaml(state_path)
            state["release"].update(
                {
                    "candidate_sha256": digest,
                    "candidate_files": files,
                    "human_approved": True,
                }
            )
            write_json_yaml(state_path, state)
            accepted_codes = {
                item["code"]
                for item in audit_project(root, release=True)["issues"]
            }
            self.assertNotIn("REVISION_OPEN", accepted_codes)
            self.assertNotIn("REVISION_ACCEPTED_EVIDENCE_MISSING", accepted_codes)

            revision = load_json_yaml(revisions_path)
            revision["revisions"][0]["verification"]["review_sha256"] = "0" * 64
            write_json_yaml(revisions_path, revision)
            invalid_acceptance_codes = {
                item["code"]
                for item in audit_project(root, release=True)["issues"]
            }
            self.assertIn(
                "REVISION_ACCEPTED_EVIDENCE_MISSING",
                invalid_acceptance_codes,
            )

            revision = load_json_yaml(revisions_path)
            revision["revisions"][0]["status"] = "deferred"
            write_json_yaml(revisions_path, revision)
            deferred_codes = {
                item["code"]
                for item in audit_project(root, release=True)["issues"]
            }
            self.assertIn("REVISION_OPEN", deferred_codes)


if __name__ == "__main__":
    unittest.main()
