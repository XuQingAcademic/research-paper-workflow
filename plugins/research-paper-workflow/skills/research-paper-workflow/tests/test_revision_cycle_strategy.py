"""Synthetic strategic-stop tests; no fixture certifies research value."""
import copy
import json
import subprocess
import sys

from test_revision_cycle import CYCLE, RevisionCycleFixture, ROOT


class StrategyHoldTests(RevisionCycleFixture):
    def evidence(self, name="strategy.md", text="Exact source comparison in the existing design record."):
        folder = self.root / "evidence"
        folder.mkdir(exist_ok=True)
        path = folder / name
        path.write_text(text + "\n", encoding="utf-8")
        return [{"path": path.relative_to(self.root).as_posix(), "sha256": CYCLE.file_digest(path)}]

    def hold_event(self, *, decision="stop-route", issue_id=None):
        return {
            "schema": CYCLE.EVENT_SCHEMA,
            "action": "strategy-hold",
            "decision": decision,
            "issue_id": issue_id,
            "reason": "The current contribution is directly implied by the checked source.",
            "evidence": self.evidence(),
            "reopen_if": "A checked correction defeats the implication or establishes a substantive remainder.",
        }

    def hold(self, **kwargs):
        return CYCLE.apply_event(self.root, self.hold_event(**kwargs), True)

    def test_preview_does_not_write_and_zero_attempt_stop_preserves_issue_and_contract(self):
        self.add(self.issue("R07"), self.issue("notation", "P3", "notation"))
        self.select()
        event = self.hold_event(issue_id="R07")
        before = self.tree()
        CYCLE.apply_event(self.root, event, False)
        self.assertEqual(self.tree(), before)
        ledger, contract = copy.deepcopy(self.ledger()), copy.deepcopy(self.state()["contract"])
        CYCLE.apply_event(self.root, event, True)
        state = self.state()
        self.assertEqual(self.ledger(), ledger)
        self.assertEqual(state["contract"], contract)
        self.assertEqual(state["active_issue_id"], "R07")
        self.assertEqual(state["queue"], ["notation"])
        self.assertIsNone(state["pause"])
        self.assertEqual(self.ledger()["revisions"][0]["implementation"]["attempts"], 0)
        report = CYCLE.status_report(self.root, state, self.ledger())
        self.assertEqual(report["outcome"], "strategic-hold")
        self.assertFalse(report["ready"])
        self.assertIn("R07", report["open_p0_p1"])
        self.assertNotIn("Complete and verify active issue", report["next_action"])

    def test_hold_blocks_execution_selection_and_review_but_sync_preserves_it(self):
        self.add(self.issue("R07"))
        self.select()
        self.implement_active("R07")
        review = self.write_review("issue-pass", scope="issue", issue_id="R07",
                                   reviewer="reviewer", context="fresh")
        self.hold(issue_id="R07")
        frozen = self.tree()
        for operation in (
            lambda: self.select(),
            lambda: self.event("implemented", issue_id="R07", worker_id="writer", locators=["manuscript.md"]),
            lambda: self.event("candidate", worker_id="writer", change_locator="candidate:2", material=True),
            lambda: CYCLE.record_review(self.root, review, True),
        ):
            with self.assertRaisesRegex(CYCLE.CycleError, "strategic hold"):
                operation()
            self.assertEqual(self.tree(), frozen)
        CYCLE.sync(self.root, True)
        self.assertIsNotNone(CYCLE.current_strategy_hold(self.state()))
        self.assertEqual(self.ledger()["revisions"][0]["status"], "verifying")

    def test_even_an_otherwise_ready_candidate_is_not_ready_after_stop(self):
        self.complete_workflow_to_delivery()
        self.event("candidate", worker_id="writer", change_locator="freeze:1", material=True)
        for index in (1, 2):
            review = self.write_review(f"clean-{index}", scope="full", issue_id=None,
                                       reviewer=f"reviewer-{index}", context=f"context-{index}")
            CYCLE.record_review(self.root, review, True)
        self.assertTrue(CYCLE.status_report(self.root, self.state(), self.ledger())["ready"])
        self.hold()
        report = CYCLE.status_report(self.root, self.state(), self.ledger())
        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["no_strategic_hold"])
        self.assertEqual(self.state()["clean_reviews"], [])

    def test_missing_stale_or_unknown_evidence_cannot_create_hold(self):
        event = self.hold_event()
        for evidence in ([], [{"path": "absent.md", "sha256": "0" * 64}],
                         [{"path": "evidence/strategy.md", "sha256": "0" * 64}]):
            bad = {**event, "evidence": evidence}
            before = self.tree()
            with self.assertRaises((CYCLE.CycleError, OSError)):
                CYCLE.apply_event(self.root, bad, True)
            self.assertEqual(self.tree(), before)
        with self.assertRaisesRegex(CYCLE.CycleError, "unknown cycle issue"):
            CYCLE.apply_event(self.root, {**event, "issue_id": "unknown"}, True)

    def test_changed_evidence_stays_held_and_is_reported_not_auto_resumed(self):
        self.hold(decision="park")
        (self.root / "evidence/strategy.md").write_text("Corrected source comparison.\n")
        report = CYCLE.status_report(self.root, self.state(), self.ledger())
        self.assertEqual(report["outcome"], "strategic-hold")
        self.assertFalse(report["strategy_evidence"]["current"])
        with self.assertRaisesRegex(CYCLE.CycleError, "strategic hold"):
            self.select()

    def test_same_contract_resolution_preserves_stop_history_and_unresolved_issue(self):
        self.add(self.issue("R07"))
        self.select()
        self.hold(issue_id="R07")
        state_before = self.state()
        original = copy.deepcopy(state_before["strategy_history"][0])
        with self.assertRaisesRegex(CYCLE.CycleError, "recorded pause"):
            self.event("resume", resolution_locator="not-an-author-gate")
        resolution = self.evidence("resolution.md", "The checked source does not cover the maintained dependence class.")
        self.event("strategy-resume", reason="Corrected comparison supports a same-question bounded check.",
                   evidence=resolution)
        state = self.state()
        self.assertIsNone(CYCLE.current_strategy_hold(state))
        self.assertEqual(state["strategy_history"][0], original)
        self.assertEqual(len(state["strategy_history"]), 2)
        self.assertEqual(state["contract"], state_before["contract"])
        self.assertEqual(self.ledger()["revisions"][0]["status"], "active")
        self.assertFalse(CYCLE.status_report(self.root, state, self.ledger())["ready"])
        self.assertEqual(self.select()["selected_issue_id"], "R07")

    def test_author_pause_and_strategy_hold_cannot_clear_each_other(self):
        self.add(self.issue("R07"))
        self.select()
        self.hold(issue_id="R07")
        self.event("pause", issue_id="R07", reason_code="research-target-change",
                   reason="A proposed different question requires the author's decision.", source_locator="decision:pending")
        resolution = self.evidence("resolution.md")
        with self.assertRaisesRegex(CYCLE.CycleError, "no unresolved author pause"):
            self.event("strategy-resume", reason="Supported route resolution.", evidence=resolution)
        self.event("resume", resolution_locator="author:keep-original-question")
        self.assertIsNotNone(CYCLE.current_strategy_hold(self.state()))
        self.assertIsNone(self.state()["pause"])
        self.assertEqual(self.ledger()["revisions"][0]["status"], "active")

    def test_resume_requires_hold_and_current_resolution_and_does_not_accept_new_contract_fields(self):
        resolution = self.evidence("resolution.md")
        with self.assertRaisesRegex(CYCLE.CycleError, "recorded hold"):
            self.event("strategy-resume", reason="No prior hold.", evidence=resolution)
        self.hold()
        (self.root / "evidence/resolution.md").write_text("Changed.\n")
        with self.assertRaisesRegex(CYCLE.CycleError, "stale"):
            self.event("strategy-resume", reason="Old comparison.", evidence=resolution)
        with self.assertRaisesRegex(CYCLE.CycleError, "unsupported fields"):
            self.event("strategy-resume", reason="Try new objective.", evidence=self.evidence("resolution-2.md"),
                       contract={"objective": "Different question"})
        self.assertIsNotNone(CYCLE.current_strategy_hold(self.state()))

    def test_route_wide_author_pause_cannot_be_bypassed_by_issue_acceptance_or_candidate(self):
        self.add(self.issue("R07"))
        self.select()
        self.implement_active("R07")
        review = self.write_review("paused-review", scope="issue", issue_id="R07",
                                   reviewer="reviewer", context="fresh")
        self.event("pause", issue_id=None, reason_code="research-target-change",
                   reason="A real author decision is pending.", source_locator="author:pending")
        before = self.tree()
        with self.assertRaisesRegex(CYCLE.CycleError, "cycle is paused"):
            CYCLE.record_review(self.root, review, True)
        with self.assertRaisesRegex(CYCLE.CycleError, "cycle is paused"):
            self.event("candidate", worker_id="writer", change_locator="candidate:2", material=True)
        self.assertEqual(self.tree(), before)
        self.assertEqual(self.ledger()["revisions"][0]["status"], "verifying")
        self.event("resume", resolution_locator="author:resolved")
        CYCLE.record_review(self.root, review, True)
        self.assertEqual(self.ledger()["revisions"][0]["status"], "accepted")

    def test_author_pause_blocks_implementation_but_can_record_a_scientific_stop(self):
        self.add(self.issue("R07"))
        self.select()
        self.event("pause", issue_id=None, reason_code="research-target-change",
                   reason="Await the actual target choice.", source_locator="author:pending")
        with self.assertRaisesRegex(CYCLE.CycleError, "cycle is paused"):
            self.event("implemented", issue_id="R07", worker_id="writer", locators=["manuscript.md"])
        self.hold(issue_id="R07")
        self.assertIsNotNone(CYCLE.current_strategy_hold(self.state()))
        self.assertIsNotNone(self.state()["pause"])
        self.event("resume", resolution_locator="author:resolved")
        self.assertIsNotNone(CYCLE.current_strategy_hold(self.state()))

    def test_legacy_state_without_optional_history_is_readable_without_migration(self):
        state = self.state()
        self.assertNotIn("strategy_history", state)
        path = self.root / ".paper/workflow/revision-cycle.json"
        before = path.read_bytes()
        loaded = self.state()
        self.assertIsNone(CYCLE.current_strategy_hold(loaded))
        self.assertEqual(path.read_bytes(), before)
        self.hold()
        self.assertEqual(len(self.state()["strategy_history"]), 1)

    def test_cli_reports_hold_with_nonready_exit_not_success(self):
        self.hold()
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/revision_cycle.py"),
                                 "status", "--project", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["outcome"], "strategic-hold")


if __name__ == "__main__":
    import unittest
    unittest.main()
