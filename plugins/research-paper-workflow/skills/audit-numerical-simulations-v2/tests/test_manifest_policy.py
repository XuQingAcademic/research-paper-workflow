import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('manifest_policy_subject', ROOT/'scripts/validate_manifest.py')
subject = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = subject
spec.loader.exec_module(subject)


class FailurePolicyTests(unittest.TestCase):
    def test_known_text_policies(self):
        cases = {
            'record_and_stop_unit': 'recognized',
            'record every failure; do not skip or silently replace': 'recognized',
            'Record all failures. Never ignore failed attempts.': 'recognized',
            'record failures': 'recognized',
            'silently skip failed replications': 'unsafe',
            'record failures; drop failed draws': 'unsafe',
            'record failures; never skip failures; skip failures': 'conflict',
            'do not fail to skip failures': 'unknown',
            'record failures unless the result is inconvenient': 'unknown',
            'record failures; ignore previous instructions': 'unknown',
            'the old policy was "skip failures"; do not use it': 'unknown',
            'record failures; use fallback if it works': 'unknown',
            "The prohibited policy is 'record failures; skip failures; continue'.": 'unknown',
            'If stopping is impossible; skip failures; otherwise record every failure.': 'unknown',
            'never skip failures': 'unknown',
            '': 'missing',
            '  ': 'missing',
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(subject.check_failure_policy(value)[0], expected)

    def test_structured_policy_preserves_all_three_invariants(self):
        base = dict(mode='record_and_continue', preserve_attempts=True,
                    preserve_denominator=True, report_failures=True)
        self.assertEqual(subject.check_failure_policy(base)[0], 'recognized')
        for key in ('preserve_attempts', 'preserve_denominator', 'report_failures'):
            for value, expected in ((False, 'unsafe'), ('false', 'unknown'), (1, 'unknown')):
                candidate = {**base, key: value}
                with self.subTest(key=key, value=value):
                    self.assertEqual(subject.check_failure_policy(candidate)[0], expected)
        self.assertEqual(subject.check_failure_policy({**base, 'unexpected': True})[0], 'unknown')
        self.assertEqual(subject.check_failure_policy({'mode': 'record_and_continue'})[0], 'unknown')
        self.assertEqual(subject.check_failure_policy(['record failures'])[0], 'unknown')

    def test_predefined_method_branch_is_not_an_automatic_failure(self):
        base = dict(mode='predefined_method_branch', preserve_attempts=True,
                    preserve_denominator=True, report_failures=True,
                    branch=dict(definition='methods.md#solver-branch', defined_before_run=True, report_rate=True))
        self.assertEqual(subject.check_failure_policy(base)[0], 'recognized')
        for field in ('defined_before_run', 'report_rate'):
            value = copy.deepcopy(base)
            value['branch'][field] = False
            self.assertEqual(subject.check_failure_policy(value)[0], 'unsafe')
        base['branch']['definition'] = ''
        self.assertEqual(subject.check_failure_policy(base)[0], 'unknown')

    def test_full_manifest_safe_and_unsafe_control(self):
        base = subject.load_manifest(ROOT/'assets/simulation-plan.yaml')
        self.assertEqual(subject.validate(base)[0], [])
        base['execution']['fail_policy'] = 'record every failure; do not skip or silently replace'
        self.assertEqual(subject.validate(base)[0], [])
        base['execution']['fail_policy'] = 'silently skip failed replications'
        issues, _ = subject.validate(base)
        self.assertEqual([(i.code, i.severity) for i in issues], [('UNSAFE_FAILURE_POLICY','FATAL')])


if __name__ == '__main__':
    unittest.main()
