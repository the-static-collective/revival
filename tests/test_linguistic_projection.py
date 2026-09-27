from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from revival.linguistic import compile_linguistic_projection, list_recipes


ROOT = Path(__file__).resolve().parents[1]
SPECIMEN = ROOT / "specimens" / "genesis-1-1-linguistic.json"


class LinguisticProjectionTests(unittest.TestCase):
    def load(self):
        return json.loads(SPECIMEN.read_text(encoding="utf-8"))

    def test_recipes_are_discoverable(self):
        recipe_ids = [item["id"] for item in list_recipes(self.load())]
        self.assertEqual(recipe_ids, ["surface", "unpointed", "reader-demo"])

    def test_unpointed_projection_is_mechanical_and_traceable(self):
        compiled = compile_linguistic_projection(self.load(), "unpointed")
        self.assertEqual(
            compiled["projection"]["content"]["text"],
            "בראשית ברא אלהים את השמים ואת הארץ׃",
        )
        for item in compiled["projection"]["content"]["trace"]:
            self.assertEqual(item["origin"]["kind"], "mechanical-transform")
            start, end = item["source_span"]
            self.assertEqual(
                compiled["witness"]["text"][start:end],
                item["source_surface"],
            )

    def test_reader_recipe_can_reorder_and_explicitly_omit(self):
        compiled = compile_linguistic_projection(self.load(), "reader-demo")
        self.assertEqual(
            compiled["projection"]["content"]["text"],
            "In the beginning God created the heavens and the earth.",
        )
        delta = compiled["delta"]["details"]
        self.assertTrue(delta["reordered"])
        self.assertEqual(delta["empty_renderings"], ["g4"])
        self.assertEqual(
            delta["output_order"],
            ["g1", "g3", "g2", "g4", "g5", "g6", "g7"],
        )

    def test_reader_trace_retains_witness_and_annotation_origin(self):
        compiled = compile_linguistic_projection(self.load(), "reader-demo")
        trace = compiled["projection"]["content"]["trace"]
        god = next(item for item in trace if item["token_id"] == "g3")
        self.assertEqual(god["source_surface"], "אֱלֹהִים")
        self.assertEqual(god["rendered"], "God")
        self.assertEqual(god["origin"]["kind"], "annotation")
        self.assertEqual(god["origin"]["authority"], "demo-projection-only")
        start, end = god["source_span"]
        self.assertEqual(compiled["witness"]["text"][start:end], "אֱלֹהִים")

    def test_annotation_change_changes_transform_and_projection_receipts_not_witness(self):
        a = self.load()
        b = copy.deepcopy(a)
        b["tokens"][2]["annotations"]["reader_demo"]["value"] = "Elohim"

        first = compile_linguistic_projection(a, "reader-demo")
        second = compile_linguistic_projection(b, "reader-demo")

        self.assertEqual(
            first["receipt"]["witness_sha256"],
            second["receipt"]["witness_sha256"],
        )
        self.assertNotEqual(
            first["receipt"]["transform_sha256"],
            second["receipt"]["transform_sha256"],
        )
        self.assertNotEqual(
            first["receipt"]["projection_sha256"],
            second["receipt"]["projection_sha256"],
        )

    def test_unrelated_annotation_does_not_invalidate_same_recipe(self):
        a = self.load()
        b = copy.deepcopy(a)
        b["tokens"][0]["annotations"]["future_note"] = {
            "value": "not selected by reader-demo",
            "authority": "demo-only",
        }

        first = compile_linguistic_projection(a, "reader-demo")
        second = compile_linguistic_projection(b, "reader-demo")

        self.assertEqual(first["receipt"], second["receipt"])

    def test_source_mismatch_fails_closed(self):
        specimen = self.load()
        specimen["tokens"][0]["surface"] = "NOT-IN-WITNESS"
        with self.assertRaises(ValueError):
            compile_linguistic_projection(specimen, "reader-demo")


if __name__ == "__main__":
    unittest.main()
