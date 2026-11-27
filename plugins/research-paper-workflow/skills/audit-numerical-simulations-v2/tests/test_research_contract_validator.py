import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_research_contract.py"
SPEC = importlib.util.spec_from_file_location("research_contract_validator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def contract(state="PASS", scientific=True, artifact=True, submission=True):
    return {
        "schema_version": "research-release-contract.v1",
        "objects": [
            {
                "object_id": "theorem-qit-test2-v1",
                "object_type": "theorem",
                "version": "v1",
                "content_hash": "statement-hash",
                "scope_hash": "scope-hash",
            }
        ],
        "claims": [
            {
                "claim_id": "claim-qit-size",
                "object_id": "theorem-qit-test2-v1",
                "required": True,
                "dependencies": [],
                "applicable_certificates": ["proof_truth", "proof_scope_coverage"],
                "state": {
                    "proof_truth": state,
                    "proof_scope_coverage": state,
                    "implementation_reproducibility": "NOT_APPLICABLE",
                },
            }
        ],
        "root_errors": [],
        "coverage_blockers": [],
        "artifacts": [
            {
                "artifact_id": "table-qit-size",
                "claim_ids": ["claim-qit-size"],
                "freshness": "current",
            }
        ],
        "release_vector": {
            "schema_GO": True,
            "source_GO": True,
            "proof_GO": scientific,
            "implementation_GO": True,
            "simulation_GO": scientific,
            "writing_GO": scientific,
            "artifact_GO": artifact,
            "scientific_GO": scientific,
            "submission_GO": submission,
        },
    }


class ResearchContractValidatorTests(unittest.TestCase):
    def test_clean_contract_passes(self):
        result = MODULE.validate(contract())
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(result["derived"]["science_blocked"])

    def test_partial_is_not_contradiction_and_blocks_science(self):
        value = contract(state="PARTIAL", scientific=False, submission=False)
        value["coverage_blockers"] = [
            {"blocker_id": "continuum-bridge-unverified", "claim_id": "claim-qit-size"}
        ]
        result = MODULE.validate(value)
        self.assertTrue(result["valid"], result["errors"])
        self.assertTrue(result["derived"]["science_blocked"])
        self.assertIn(
            "claim-qit-size:proof_truth:PARTIAL",
            result["derived"]["required_nonpass"],
        )

    def test_false_clean_release_is_rejected(self):
        value = contract(state="PARTIAL", scientific=True, submission=True)
        value["coverage_blockers"] = [
            {"blocker_id": "main-assumptions-missing", "claim_id": "claim-qit-size"}
        ]
        result = MODULE.validate(value)
        self.assertFalse(result["valid"])
        self.assertTrue(any("scientific_GO" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
