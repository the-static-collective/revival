from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from revival.compiler import compile_specimen
from revival.kernel.v1 import PRIMITIVES, scissors, sha256


ROOT = Path(__file__).resolve().parents[1]
SPECIMEN = ROOT / "specimens" / "genesis-1-1.json"


class GenesisSpecimenTests(unittest.TestCase):
    def load(self):
        return json.loads(SPECIMEN.read_text(encoding="utf-8"))

    def test_kernel_primitives_are_explicit(self):
        self.assertEqual(
            PRIMITIVES,
            (
                "WITNESS",
                "ANNOTATION",
                "TRANSFORM",
                "PROJECTION",
                "DELTA",
                "RECEIPT",
            ),
        )

    def test_compile_is_deterministic(self):
        specimen = self.load()
        self.assertEqual(compile_specimen(specimen), compile_specimen(specimen))

    def test_exact_projection_preserves_held_witness(self):
        specimen = self.load()
        compiled = compile_specimen(specimen)
        exact = compiled["results"][0]
        self.assertEqual(exact["projection"]["content"], specimen["witness"]["text"])
        self.assertEqual(exact["delta"]["details"]["removed"], [])
        self.assertEqual(exact["delta"]["details"]["introduced"], [])

    def test_mark_stripping_reports_every_loss(self):
        specimen = self.load()
        compiled = compile_specimen(specimen)
        stripped = compiled["results"][1]
        self.assertEqual(
            stripped["projection"]["content"],
            "בראשית ברא אלהים את השמים ואת הארץ׃",
        )
        removed = stripped["delta"]["details"]["removed"]
        self.assertGreater(len(removed), 0)
        self.assertTrue(all(item["category"].startswith("M") for item in removed))
        self.assertEqual(stripped["delta"]["details"]["introduced"], [])

    def test_witness_change_changes_receipt_identity(self):
        original = self.load()
        changed = copy.deepcopy(original)
        changed["witness"]["text"] += " "
        a = compile_specimen(original)["results"][0]["receipt"]["witness_sha256"]
        b = compile_specimen(changed)["results"][0]["receipt"]["witness_sha256"]
        self.assertNotEqual(a, b)

    def test_scissors_preserve_explicit_parent_identity(self):
        parent_hash = sha256({"kernel": "v1-contract"})
        relation = scissors(
            parent_version="1",
            child_version="2",
            parent_contract_sha256=parent_hash,
            rationale="Example descendant contract.",
        )
        self.assertEqual(relation["relation"], "descends_from")
        self.assertEqual(relation["parent_contract_sha256"], parent_hash)


if __name__ == "__main__":
    unittest.main()
