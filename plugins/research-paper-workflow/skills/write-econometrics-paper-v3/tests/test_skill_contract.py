from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_frontmatter_and_size(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(text.splitlines()), 500)
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        keys = {
            line.split(":", 1)[0].strip()
            for line in match.group(1).splitlines()
            if ":" in line
        }
        self.assertEqual(keys, {"name", "description"})
        self.assertIn("name: write-econometrics-paper-v3", match.group(1))
        self.assertNotIn("[TODO", text)

    def test_direct_references_exist(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\((references/[^)]+|assets/[^)]+)\)", text)
        self.assertGreaterEqual(len(links), 7)
        for link in links:
            self.assertTrue((ROOT / link).is_file(), link)

    def test_openai_metadata_mentions_skill(self) -> None:
        text = (ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("$write-econometrics-paper-v3", text)
        self.assertNotIn("TODO", text)

    def test_evals_are_valid_and_cover_core_modes(self) -> None:
        path = ROOT / "evals" / "cases.jsonl"
        cases = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertGreaterEqual(len(cases), 12)
        modes = {case["mode"] for case in cases}
        for required in (
            "lightweight",
            "managed-project",
            "citation",
            "release",
            "revision",
            "simulation",
        ):
            self.assertIn(required, modes)
        identifiers = [case["id"] for case in cases]
        self.assertEqual(len(identifiers), len(set(identifiers)))


if __name__ == "__main__":
    unittest.main()
