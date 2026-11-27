"""Synthetic controller fixtures, NOT real-task/model efficacy measurements."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prompt_trials.py"
SPEC = importlib.util.spec_from_file_location("prompt_trials", SCRIPT)
trial = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trial)
MANAGER = os.environ.get("RESEARCH_SKILL_MANAGER")


@unittest.skipUnless(MANAGER, "set RESEARCH_SKILL_MANAGER to test the existing frozen comparator integration")
class PromptTrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manager = trial.manager_at(Path(MANAGER))
        self.bundle = self.manager.bundle_tools
        self.runtime = {"model": "fixture-model", "model_version": "fixture-v1",
                        "reasoning_effort": "fixture", "tools": ["local"], "budget": {"calls": 2}}
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        for ident in ("R", "H"):
            (self.inputs / f"{ident}.md").write_text(f"unit fixture {ident}; no model executed")
        self.skills = {}
        for arm in ("a", "b"):
            self.skills[arm] = self.root / f"skill-{arm}"
            self.skills[arm].mkdir()
            (self.skills[arm] / "SKILL.md").write_text(f"fixture instructions {arm}")
        self.plan_path = self.root / "trial.json"
        self.plan = {"schema": trial.SCHEMA, "id": "unit-trial", "task_family": "fixture-task",
                     "hypothesis": "test controller decisions only", "failure_diagnosis": "fixture",
                     "stop_condition": "no live execution", "change_kind": "prompt",
                     "profile": {"id": "fixture-profile", "runtime": self.runtime, "version_scope": "snapshot",
                                 "instructions": self.art(self.skills["b"] / "SKILL.md"),
                                 "escalate_when": "fixture failure"},
                     "objective": {"metric": "quality", "min_gain": 1},
                     "cases": [{"id": ident, "project_id": "fixture-project",
                                "origin": "real", "exposure": "exposed" if ident == "R" else "withheld",
                                "positive_control": ident == "R", "source": self.art(self.inputs / f"{ident}.md")}
                               for ident in ("R", "H")]}
        # 'real'/'withheld' above are test declarations, not empirical provenance.
        self.a_checks = {"R": {"correct": "pass", "scope": "pass"}, "H": {"correct": "fail", "scope": "pass"}}
        self.b_checks = {ident: {"correct": "pass", "scope": "pass"} for ident in ("R", "H")}

    def art(self, path):
        return {"path": str(path.relative_to(self.root)), "sha256": trial.digest(path)}

    def save(self, path, value):
        path.write_text(json.dumps(value))
        return self.art(path)

    def make_run(self, arm, checks, plan_binding=True):
        settings = self.root / "settings.json"
        dispatch_plan = self.root / "dispatch-plan.json"
        rubric = self.root / "rubric.json"
        self.save(settings, self.runtime)
        self.save(dispatch_plan, {"mode": "unit fixture, not executed"})
        self.save(rubric, {"checks": ["correct", "scope"]})
        frozen = self.root / f"bundle-{arm}"
        externals = {"rubric": rubric}
        if plan_binding:
            externals["trial_plan"] = self.plan_path
        self.bundle.freeze(frozen, {"skill": self.skills[arm]}, self.inputs, settings, dispatch_plan, externals)
        manifest = trial.read(frozen / "manifest.json")
        before = self.root / f"before-{arm}.json"
        after = self.root / f"after-{arm}.json"
        self.save(before, self.bundle.verify(frozen))
        cases = []
        for index, planned in enumerate(self.plan["cases"]):
            ident = planned["id"]
            safe_id = ident.replace("/", "_")
            output = self.root / f"{arm}-{safe_id}-output.md"
            review = self.root / f"{arm}-{safe_id}-review.json"
            output.write_text(f"fixture output {arm}/{ident}")
            self.save(review, checks[ident])
            cases.append({"id": ident, "split": "regression" if index == 0 else "holdout",
                          "status": "completed", "subject_context": f"{arm}-subject", "reviewer_context": "judge",
                          "input": self.art(frozen / "inputs" / ("R.md" if index == 0 else "H.md")), "rubric": self.art(rubric),
                          "output": self.art(output), "review": self.art(review), "checks": checks[ident]})
        self.save(after, self.bundle.verify(frozen))
        first = "scan=" + trial.digest(before)
        last = "scan=" + trial.digest(after)
        raw = self.root / f"{arm}-events.txt"
        raw.write_text(f"{first}\n{arm}-subject dispatch\n{arm}-subject result\n{last}\njudge dispatch\njudge result\n")
        dispatch = {"schema_version": 1, "bundle_sha256": trial.digest(frozen / "manifest.json"),
                    "settings_sha256": manifest["settings"]["sha256"], "plan_sha256": manifest["dispatch_plan"]["sha256"],
                    "subject": {"context_id": f"{arm}-subject", "dispatch_anchor": f"{arm}-subject dispatch", "result_anchor": f"{arm}-subject result"},
                    "reviewer": {"context_id": "judge", "dispatch_anchor": "judge dispatch", "result_anchor": "judge result"},
                    "verification": {"before": {**self.art(before), "provenance_anchor": first},
                                     "after": {**self.art(after), "provenance_anchor": last}},
                    "cases": [{"id": c["id"], **{k + "_sha256": c[k]["sha256"] for k in ("input", "rubric", "output", "review")}} for c in cases]}
        run = {"schema_version": 2, "case_set_id": "controller-unit-test", "skill_version": arm,
               "run_settings": copy.deepcopy(self.runtime), "cases": cases,
               "bundle": self.art(frozen / "manifest.json"), "dispatch": self.save(self.root / f"{arm}-dispatch.json", dispatch),
               "provenance": self.art(raw)}
        path = self.root / f"{arm}.json"
        self.save(path, run)
        return path

    def pair(self, plan_binding=True):
        self.save(self.plan_path, self.plan)
        self.a = self.make_run("a", self.a_checks, plan_binding)
        self.b = self.make_run("b", self.b_checks, plan_binding)

    def decide(self):
        return trial.decide(self.manager, self.plan_path, self.a, self.b)

    def test_real_holdout_gain_eligible_but_does_not_install(self):
        self.pair()
        files = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        outcome = self.decide()
        self.assertEqual("eligible_scoped", outcome["decision"])
        self.assertEqual([{"case": "H", "check": "correct"}], outcome["heldout_check_improvements"])
        self.assertEqual(files, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_tie_keeps_baseline_even_when_comparator_exits_zero(self):
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        self.assertEqual(0, self.manager.compare(self.a, self.b)[1])
        self.assertEqual("keep_baseline", self.decide()["decision"])

    def test_regression_not_offset_by_improvement(self):
        self.b_checks["R"]["scope"] = "fail"
        self.pair()
        self.assertEqual("reject", self.decide()["decision"])

    def test_remaining_failure_rejected(self):
        self.a_checks["R"]["correct"] = self.b_checks["R"]["correct"] = "fail"
        self.pair()
        self.assertEqual("reject", self.decide()["decision"])

    def test_only_development_improvement_not_selected(self):
        self.a_checks["R"]["correct"] = "fail"
        self.a_checks["H"]["correct"] = "pass"
        self.pair()
        self.assertEqual("keep_baseline", self.decide()["decision"])

    def test_synthetic_only_cannot_promote(self):
        for c in self.plan["cases"]:
            c["origin"] = "synthetic"
        self.pair()
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_exposed_holdout_cannot_promote(self):
        self.plan["cases"][1]["exposure"] = "exposed"
        self.pair()
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_positive_control_required(self):
        self.plan["cases"][0]["positive_control"] = False
        self.pair()
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_unknown_model_version_not_invented(self):
        self.runtime["model_version"] = None
        self.pair()
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_plan_must_be_frozen_before_execution(self):
        self.pair(plan_binding=False)
        with self.assertRaisesRegex(ValueError, "before execution"):
            self.decide()

    def test_rewritten_plan_rejected(self):
        self.pair()
        self.plan["objective"]["min_gain"] = 0.1
        self.save(self.plan_path, self.plan)
        with self.assertRaisesRegex(ValueError, "before execution"):
            self.decide()

    def test_changed_output_rejected(self):
        self.pair()
        (self.root / "b-H-output.md").write_text("changed after judgment")
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_missing_source_rejected(self):
        self.pair()
        (self.inputs / "H.md").unlink()
        with self.assertRaisesRegex(ValueError, "changed artifact"):
            self.decide()

    def test_runtime_difference_uncontrolled(self):
        self.pair()
        run = trial.read(self.b)
        run["run_settings"]["model"] = "other-model"
        self.save(self.b, run)
        self.assertEqual("inconclusive", self.decide()["decision"])

    def add_metrics(self, metric="wall_seconds", before=10, after=5, units=("seconds", "seconds")):
        for path, value, unit in ((self.a, before, units[0]), (self.b, after, units[1])):
            run = trial.read(path)
            for c in run["cases"]:
                observed = {"value": value, "measurement": "observed", "accounting_key": unit}
                source = self.root / f"{path.stem}-{c['id']}-metric.json"
                binding = self.save(source, observed)
                c["measurements"] = {metric: {**observed, "source": binding}}
            self.save(path, run)

    def test_efficiency_gain_with_unchanged_quality(self):
        self.plan["objective"] = {"metric": "wall_seconds", "min_gain": 1, "accounting_key": "seconds"}
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        self.add_metrics()
        self.assertEqual("eligible_scoped", self.decide()["decision"])

    def test_missing_usage_not_zero_savings(self):
        self.plan["objective"] = {"metric": "tokens", "min_gain": 1, "accounting_key": "provider-total-tokens"}
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_incomparable_measurement_units(self):
        self.plan["objective"] = {"metric": "wall_seconds", "min_gain": 1, "accounting_key": "seconds"}
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        self.add_metrics(units=("seconds", "estimated-seconds"))
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_faster_failure_not_efficiency(self):
        self.plan["objective"] = {"metric": "wall_seconds", "min_gain": 1, "accounting_key": "seconds"}
        self.pair()
        self.add_metrics()
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_efficiency_loss_keeps_baseline(self):
        self.plan["objective"] = {"metric": "wall_seconds", "min_gain": 1, "accounting_key": "seconds"}
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        self.add_metrics(before=5, after=10)
        self.assertEqual("keep_baseline", self.decide()["decision"])

    def test_select_matches_model_version_and_task(self):
        self.pair()
        current = self.root / "runtime.json"
        self.save(current, self.runtime)
        self.assertEqual("selected", trial.select(self.manager, self.plan_path, self.a, self.b, current, "fixture-task", "fixture-project")["decision"])
        self.assertEqual("fallback", trial.select(self.manager, self.plan_path, self.a, self.b, current, "other-task", "fixture-project")["decision"])
        self.assertEqual("fallback", trial.select(self.manager, self.plan_path, self.a, self.b, current, "fixture-task", "other-project")["decision"])
        runtime = copy.deepcopy(self.runtime)
        runtime["model_version"] = "new-version"
        self.save(current, runtime)
        self.assertEqual("fallback", trial.select(self.manager, self.plan_path, self.a, self.b, current, "fixture-task", "fixture-project")["decision"])

    def test_measurement_cannot_disagree_with_its_source(self):
        self.plan["objective"] = {"metric": "wall_seconds", "min_gain": 1, "accounting_key": "seconds"}
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        self.add_metrics()
        run = trial.read(self.b)
        run["cases"][0]["measurements"]["wall_seconds"]["value"] = 0
        self.save(self.b, run)
        with self.assertRaisesRegex(ValueError, "bound observation"):
            self.decide()

    def test_slash_case_id_cannot_launder_regression_gain_as_holdout(self):
        self.plan["cases"][0]["id"] = "H/exposed"
        self.a_checks["H/exposed"] = self.a_checks.pop("R")
        self.b_checks["H/exposed"] = self.b_checks.pop("R")
        self.a_checks["H/exposed"]["correct"] = "fail"
        self.a_checks["H"]["correct"] = "pass"
        self.pair()
        self.assertEqual("keep_baseline", self.decide()["decision"])

    def test_same_wrong_unit_in_both_arms_cannot_meet_threshold(self):
        self.plan["objective"] = {"metric": "wall_seconds", "min_gain": 1, "accounting_key": "seconds"}
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        self.add_metrics(units=("milliseconds", "milliseconds"))
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_source_must_match_dispatched_task_not_an_unrelated_real_file(self):
        self.plan["cases"][1]["source"] = self.art(self.inputs / "R.md")
        self.pair()
        with self.assertRaisesRegex(ValueError, "actual frozen task"):
            self.decide()

    def test_unmeasured_additional_runtime_field_not_selected(self):
        self.pair()
        # Mutate the caller's desired configuration, not the frozen run/plan.
        current = self.root / "runtime.json"
        self.save(current, {**self.runtime, "temperature": 1})
        self.assertEqual("fallback", trial.select(self.manager, self.plan_path, self.a, self.b,
                                                 current, "fixture-task", "fixture-project")["decision"])

    def test_profile_cannot_claim_a_runtime_parameter_not_executed(self):
        self.runtime["temperature"] = 0
        self.plan["profile"]["runtime"] = {**self.runtime, "temperature": 1}
        self.pair()
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_mutable_alias_cannot_be_persistent_snapshot(self):
        self.runtime["model_version"] = "latest"
        self.pair()
        self.assertEqual("inconclusive", self.decide()["decision"])

    def test_alias_profile_is_scoped_to_current_session(self):
        self.runtime.update(model_version="latest", session_id="evaluation-session")
        self.plan["profile"]["version_scope"] = "session"
        self.pair()
        current = self.root / "runtime.json"
        self.save(current, self.runtime)
        self.assertEqual("selected", trial.select(self.manager, self.plan_path, self.a, self.b,
                                                 current, "fixture-task", "fixture-project")["decision"])
        self.save(current, {**self.runtime, "session_id": "next-session"})
        self.assertEqual("fallback", trial.select(self.manager, self.plan_path, self.a, self.b,
                                                 current, "fixture-task", "fixture-project")["decision"])

    def test_boolean_observation_cannot_be_zero_cost(self):
        self.plan["objective"] = {"metric": "wall_seconds", "min_gain": 1, "accounting_key": "seconds"}
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        self.add_metrics()
        run = trial.read(self.b)
        measure = run["cases"][0]["measurements"]["wall_seconds"]
        source = self.root / measure["source"]["path"]
        self.save(source, {"value": False, "measurement": "observed", "accounting_key": "seconds"})
        measure.update(value=0, source=self.art(source))
        self.save(self.b, run)
        with self.assertRaisesRegex(ValueError, "invalid observed"):
            self.decide()

    def test_cli_tie_exit_is_not_adoption(self):
        self.a_checks = copy.deepcopy(self.b_checks)
        self.pair()
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "decide", "--manager-root", MANAGER,
                               "--plan", str(self.plan_path), "--baseline", str(self.a), "--candidate", str(self.b)],
                              text=True, capture_output=True)
        self.assertEqual(1, proc.returncode, proc.stderr)
        self.assertEqual("keep_baseline", json.loads(proc.stdout)["decision"])


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"id": 1, "id": 2}')
            with self.assertRaisesRegex(ValueError, "duplicate"):
                trial.read(path)


if __name__ == "__main__":
    unittest.main()
