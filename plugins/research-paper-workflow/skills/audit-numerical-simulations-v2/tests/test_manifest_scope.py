"""Scope fixtures exercise applicability, not the truth of scientific labels."""

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("manifest_scope_subject", ROOT / "scripts/validate_manifest.py")
subject = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = subject
spec.loader.exec_module(subject)


class ManifestScopeTests(unittest.TestCase):
    def plan(self, *metrics, task_type=None):
        data = subject.load_manifest(ROOT / "assets/simulation-plan.yaml")
        data["aims"] = [{"id": "A1", "claim": "Evaluate the specified performance targets."}]
        data["estimands"] = [{"id": "E1", "definition": "Population mean theta.",
                              "truth_source": "Analytic mean of the declared DGP."}]
        data["dgp"]["scenarios"] = [{"id": "baseline", "classification": "baseline"}]
        data["performance"]["measures"] = [
            {"id": metric, "definition": "Pre-specified replication-level formula.", "primary": True}
            for metric in metrics
        ]
        if task_type is not None:
            data["study"]["task_type"] = task_type
        return data

    def checked(self, data):
        issues, derived = subject.validate(data)
        return {issue.code for issue in issues}, derived["task_scope"]

    def assert_clean(self, data, resolved, null_requirement="not_applicable"):
        issues, derived = subject.validate(data)
        self.assertEqual(issues, [])
        scope = derived["task_scope"]
        self.assertEqual(scope["interpretation"], "recognized")
        self.assertEqual(scope["resolved_task_type"], resolved)
        self.assertEqual(scope["null_dgp_requirement"], null_requirement)
        self.assertEqual(scope["evidence_status"], "declared_only")

    def test_legacy_template_stays_clean_and_infers_testing(self):
        self.assert_clean(subject.load_manifest(ROOT / "assets/simulation-plan.yaml"), "testing", "required")

    def test_pure_bias_rmse_has_no_null_requirement(self):
        for declared in (None, "estimation"):
            with self.subTest(declared=declared):
                self.assert_clean(self.plan("bias", "RMSE", task_type=declared), "estimation")

    def test_interval_coverage_uses_truth_and_event_not_test_null(self):
        for declared in (None, "interval"):
            data = self.plan("coverage", "interval_length", task_type=declared)
            data["performance"]["measures"][0]["definition"] = "mean(lower <= theta <= upper) for a pointwise interval."
            with self.subTest(declared=declared):
                self.assert_clean(data, "interval")

    def test_length_only_still_has_interval_target(self):
        self.assert_clean(self.plan("interval_length", task_type="interval"), "interval")

    def test_diagnostics_do_not_create_testing_or_truth_requirements(self):
        data = self.plan("runtime", "failure_rate", task_type="diagnostic")
        data["estimands"][0].pop("truth_source")
        self.assert_clean(data, "diagnostic")

    def test_auxiliary_diagnostics_do_not_make_testing_mixed(self):
        data = self.plan("size", "power", "failure_rate", task_type="testing")
        data["dgp"]["scenarios"][0]["classification"] = "null"
        self.assert_clean(data, "testing", "required")

    def test_each_testing_metric_requires_null(self):
        for metric in ("size", "power", "type_i_error_rate", "rejection_probability"):
            with self.subTest(metric=metric):
                codes, scope = self.checked(self.plan(metric))
                self.assertEqual(codes, {"NO_NULL_DGP"})
                self.assertEqual(scope["null_dgp_requirement"], "required")

    def test_complete_null_labels_only(self):
        for classification in ("non_null", "nonnull", "non-null", "not null", "nullified",
                               "alternative_null", "null_or_alternative", "null_baseline", None, [], {}):
            data = self.plan("power")
            data["dgp"]["scenarios"][0]["classification"] = classification
            with self.subTest(classification=classification):
                self.assertIn("NO_NULL_DGP", self.checked(data)[0])
        data["dgp"]["scenarios"][0]["classification"] = " NULL "
        self.assert_clean(data, "testing", "required")

    def test_mixed_estimation_interval_does_not_need_null(self):
        for declared in (None, "mixed"):
            with self.subTest(declared=declared):
                self.assert_clean(self.plan("bias", "coverage", task_type=declared), "mixed")

    def test_mixed_testing_retains_null_requirement(self):
        for declared in (None, "mixed"):
            data = self.plan("bias", "power", task_type=declared)
            with self.subTest(declared=declared):
                self.assertEqual(self.checked(data)[0], {"NO_NULL_DGP"})
                data["dgp"]["scenarios"][0]["classification"] = "null"
                self.assert_clean(data, "mixed", "required")

    def test_estimation_label_cannot_hide_power_even_with_null(self):
        data = self.plan("bias", "power", task_type="estimation")
        codes, scope = self.checked(data)
        self.assertEqual(codes, {"CONFLICTING_TASK_SCOPE", "NO_NULL_DGP"})
        self.assertEqual(scope["interpretation"], "conflict")
        self.assertEqual(scope["null_dgp_requirement"], "required")
        data["dgp"]["scenarios"][0]["classification"] = "null"
        self.assertEqual(self.checked(data)[0], {"CONFLICTING_TASK_SCOPE"})

    def test_interval_and_diagnostic_labels_cannot_hide_size(self):
        for declared in ("interval", "diagnostic"):
            with self.subTest(declared=declared):
                codes, scope = self.checked(self.plan("size", task_type=declared))
                self.assertIn("CONFLICTING_TASK_SCOPE", codes)
                self.assertIn("NO_NULL_DGP", codes)
                self.assertEqual(scope["null_dgp_requirement"], "required")

    def test_mixed_is_not_a_waiver_for_unspecified_targets(self):
        data = self.plan("bias", task_type="mixed")
        codes, scope = self.checked(data)
        self.assertEqual(codes, {"UNVERIFIED_TASK_SCOPE"})
        self.assertEqual(scope["null_dgp_requirement"], "unknown")

    def test_unknown_custom_metric_cannot_inherit_task_label(self):
        for declared in (None, "estimation", "mixed", "diagnostic"):
            with self.subTest(declared=declared):
                codes, scope = self.checked(self.plan("my_score", task_type=declared))
                self.assertIn("UNVERIFIED_MEASURE_TARGET", codes)
                self.assertEqual(scope["null_dgp_requirement"], "unknown")

    def test_custom_metric_explicit_target_and_definition_resolve_scope(self):
        for target in ("estimation", "interval", "diagnostic", "testing"):
            data = self.plan("my_score", task_type=target)
            data["performance"]["measures"][0]["target_type"] = target
            if target == "testing":
                self.assertEqual(self.checked(data)[0], {"NO_NULL_DGP"})
                data["dgp"]["scenarios"][0]["classification"] = "null"
            with self.subTest(target=target):
                self.assert_clean(data, target, "required" if target == "testing" else "not_applicable")

    def test_custom_metric_missing_definition_is_unverified(self):
        data = self.plan("my_score", task_type="estimation")
        data["performance"]["measures"][0].update(target_type="estimation", definition="  ")
        codes, scope = self.checked(data)
        self.assertEqual(codes, {"UNVERIFIED_MEASURE_DEFINITION"})
        self.assertEqual(scope["interpretation"], "unknown")

    def test_coverage_missing_event_definition_is_unverified(self):
        for value in (None, "", " ", [], {"event": "theta in interval"}, 3):
            data = self.plan("coverage", task_type="interval")
            data["performance"]["measures"][0]["definition"] = value
            with self.subTest(value=value):
                self.assertEqual(self.checked(data)[0], {"UNVERIFIED_MEASURE_DEFINITION"})

    def test_estimation_and_interval_truth_sources_are_required(self):
        for metric in ("bias", "RMSE", "coverage", "interval_length"):
            for value in (None, "", "  ", [], {}, True):
                data = self.plan(metric)
                data["estimands"][0]["truth_source"] = value
                with self.subTest(metric=metric, value=value):
                    self.assertEqual(self.checked(data)[0], {"UNVERIFIED_TRUTH_SOURCE"})

    def test_known_metric_target_conflicts_cannot_mask_testing(self):
        data = self.plan("size", task_type="estimation")
        data["performance"]["measures"][0]["target_type"] = "estimation"
        codes, scope = self.checked(data)
        self.assertEqual(codes, {"CONFLICTING_MEASURE_TARGET", "CONFLICTING_TASK_SCOPE", "NO_NULL_DGP"})
        self.assertEqual(scope["null_dgp_requirement"], "required")

    def test_kind_can_resolve_custom_id_but_cannot_override_known_id(self):
        data = self.plan("metric_1")
        data["performance"]["measures"][0]["kind"] = "coverage"
        self.assert_clean(data, "interval")
        data["performance"]["measures"][0]["target_type"] = "estimation"
        self.assertIn("CONFLICTING_MEASURE_TARGET", self.checked(data)[0])
        data["performance"]["measures"][0].update(id="power", target_type="interval")
        codes, scope = self.checked(data)
        self.assertIn("CONFLICTING_METRIC_KIND", codes)
        self.assertIn("CONFLICTING_MEASURE_TARGET", codes)
        self.assertIn("NO_NULL_DGP", codes)
        self.assertEqual(scope["null_dgp_requirement"], "required")

    def test_unknown_kind_cannot_be_ignored(self):
        data = self.plan("bias", task_type="estimation")
        data["performance"]["measures"][0].update(kind="unrecognized", target_type="estimation")
        self.assertIn("UNVERIFIED_METRIC_KIND", self.checked(data)[0])

    def test_unknowns_do_not_cancel_known_testing_requirements(self):
        data = self.plan("power", "custom_score")
        codes, scope = self.checked(data)
        self.assertIn("UNVERIFIED_MEASURE_TARGET", codes)
        self.assertIn("NO_NULL_DGP", codes)
        self.assertEqual(scope["interpretation"], "unknown")
        self.assertEqual(scope["null_dgp_requirement"], "required")

    def test_explicit_testing_aim_still_requires_null_with_unknown_metrics(self):
        codes, scope = self.checked(self.plan("custom_score", task_type="testing"))
        self.assertIn("UNVERIFIED_MEASURE_TARGET", codes)
        self.assertIn("NO_NULL_DGP", codes)
        self.assertEqual(scope["null_dgp_requirement"], "required")

    def test_method_specific_diagnostic_null_does_not_cover_target(self):
        data = self.plan("size")
        for truth in ("alternative", "nonnull", "non_null", 0, 0.0, 1, False, None, {}):
            data["dgp"]["scenarios"][0].update(classification="null", truth_by_method={
                "proposed": truth, "benchmark": "null", "oracle": "null"})
            with self.subTest(truth=truth):
                self.assertEqual(self.checked(data)[0], {"NO_NULL_DGP"})
        data["dgp"]["scenarios"][0]["truth_by_method"]["proposed"] = "null"
        self.assert_clean(data, "testing", "required")

    def test_method_specific_null_may_differ_from_global_classification(self):
        data = self.plan("size")
        data["dgp"]["scenarios"][0].update(classification="fixed_alternative",
                                                    truth_by_method={"proposed": "null"})
        self.assert_clean(data, "testing", "required")

    def test_all_explicit_confirmatory_methods_need_declared_null_support(self):
        data = self.plan("power")
        data["methods"][1]["evidence_role"] = "confirmatory"
        data["dgp"]["scenarios"][0]["truth_by_method"] = {"proposed": "null", "benchmark": "alternative"}
        self.assertEqual(self.checked(data)[0], {"NO_NULL_DGP"})
        data["dgp"]["scenarios"].append({"id": "benchmark_null", "classification": "baseline",
                                         "truth_by_method": {"benchmark": "null"}})
        self.assert_clean(data, "testing", "required")

    def test_scope_fields_with_unexpected_types_fail_without_crashing(self):
        for value in (None, [], {}, True, 4, "", "novel_task"):
            for field in ("task_type", "target_type", "kind"):
                data = self.plan("size")
                if field == "task_type":
                    data["study"][field] = value
                else:
                    data["performance"]["measures"][0][field] = value
                with self.subTest(field=field, value=value):
                    codes, scope = self.checked(data)
                    self.assertIn("NO_NULL_DGP", codes)
                    self.assertTrue(any(code.startswith("UNVERIFIED_") for code in codes))
                    self.assertEqual(scope["null_dgp_requirement"], "required")

    def test_malformed_lists_and_ids_are_findings_not_exceptions(self):
        base = self.plan("bias")
        mutations = [
            ("performance", "measures", None), ("performance", "measures", [None]),
            ("performance", "measures", [{"id": ["size"]}]),
            ("performance", "measures", [{"id": {}}, {"id": 1}]),
            ("dgp", "scenarios", None), ("dgp", "scenarios", [False]),
            ("study", "stage", []),
        ]
        for section, key, value in mutations:
            data = copy.deepcopy(base)
            data[section][key] = value
            with self.subTest(section=section, key=key, value=value):
                self.assertTrue(subject.validate(data)[0])
        for field in ("estimands", "methods"):
            for value in (None, 1, [None], [{"id": []}]):
                data = copy.deepcopy(base)
                data[field] = value
                with self.subTest(field=field, value=value):
                    self.assertTrue(subject.validate(data)[0])

    def test_malformed_method_truth_does_not_earn_null_support(self):
        for value in (None, "null", ["null"], 1):
            data = self.plan("power")
            data["dgp"]["scenarios"][0].update(classification="null", truth_by_method=value)
            with self.subTest(value=value):
                self.assertEqual(self.checked(data)[0], {"UNVERIFIED_NULL_DGP", "NO_NULL_DGP"})

    def test_composite_keeps_independent_roots_and_scope_requirement(self):
        base = self.plan("bias", "power", task_type="mixed")
        base["dgp"]["scenarios"][0]["classification"] = "null"
        self.assert_clean(base, "mixed", "required")
        roots = []
        for change in ("null", "truth", "policy"):
            data = copy.deepcopy(base)
            if change == "null":
                data["dgp"]["scenarios"][0]["classification"] = "non_null"
            elif change == "truth":
                data["estimands"][0]["truth_source"] = ""
            else:
                data["execution"]["fail_policy"] = "skip failed replications"
            roots.append(self.checked(data)[0])
        composite = copy.deepcopy(base)
        composite["dgp"]["scenarios"][0]["classification"] = "non_null"
        composite["estimands"][0]["truth_source"] = ""
        composite["execution"]["fail_policy"] = "skip failed replications"
        self.assertEqual(self.checked(composite)[0], set.union(*roots))


if __name__ == "__main__":
    unittest.main()
