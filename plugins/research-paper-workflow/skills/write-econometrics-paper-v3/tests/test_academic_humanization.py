from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_academic_humanization.py"
SPEC = importlib.util.spec_from_file_location("check_academic_humanization", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class AcademicHumanizationTests(unittest.TestCase):
    def test_accepts_prose_change_with_protected_tokens_preserved(self) -> None:
        before = r"We show $T_n=1.25$ in Table~\ref{tab:main} \citep{Smith2025}."
        after = r"Table~\ref{tab:main} reports $T_n=1.25$ \citep{Smith2025}."
        self.assertTrue(MODULE.inspect(before, after)["valid"])

    def test_inline_math_preserves_escaped_dollars_and_commands(self) -> None:
        before = r"Profit is $p=\$20+\alpha$, with \(q=\beta\)."
        after = r"With \(q=\beta\), profit is $p=\$20+\alpha$."
        self.assertTrue(MODULE.inspect(before, after)["valid"])

        change = MODULE.inspect(before, after.replace(r"\alpha", r"\gamma"))
        self.assertEqual(change["protected_token_changes"]["inline_math"], {
            "missing": [r"$p=\$20+\alpha$"],
            "added": [r"$p=\$20+\gamma$"],
        })

    def test_rejects_number_citation_or_colloquial_change(self) -> None:
        before = r"The estimate is 1.25 \citep{Smith2025}."
        after = r"Here's the thing: the estimate is 1.30 \citep{Jones2026}."
        result = MODULE.inspect(before, after)
        self.assertFalse(result["valid"])
        self.assertIn("numbers", result["protected_token_changes"])
        self.assertIn("citations", result["protected_token_changes"])
        self.assertTrue(result["colloquial_hits"])


if __name__ == "__main__":
    unittest.main()
