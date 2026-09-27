from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from revival.linguistic import (
    compile_linguistic_projection,
    list_choices,
    list_recipes,
)


ROOT = Path(__file__).resolve().parents[1]
SPECIMEN = ROOT / "specimens" / "genesis-1-1-linguistic.json"
ELOHIM_PROFILE = ROOT / "profiles" / "genesis-1-1-elohim.json"


class LinguisticProjectionTests(unittest.TestCase):
    def load(self):
        return json.loads(SPECIMEN.read_text(encoding="utf-8"))

    def load_profile(self):
        return json.loads(ELOHIM_PROFILE.read_text(encoding="utf-8"))

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

    def test_reader_recipe_uses_default_choice_and_tracks_it(self):
        compiled = compile_linguistic_projection(self.load(), "reader-demo")
        self.assertEqual(
            compiled["projection"]["content"]["text"],
            "In the beginning God created the heavens and the earth.",
        )
        delta = compiled["delta"]["details"]
        self.assertTrue(delta["reordered"])
        self.assertEqual(delta["empty_renderings"], ["g4"])
        god_choice = next(
            item for item in delta["choice_selections"] if item["token_id"] == "g3"
        )
        self.assertEqual(god_choice["choice_id"], "god")
        self.assertTrue(god_choice["default_choice"])
        self.assertFalse(god_choice["selected_by_profile"])

    def test_choices_are_discoverable_at_source_token(self):
        choices = list_choices(self.load(), "reader-demo")
        self.assertEqual(len(choices), 1)
        item = choices[0]
        self.assertEqual(item["token_id"], "g3")
        self.assertEqual(item["source_surface"], "אֱלֹהִים")
        self.assertEqual(
            [variant["id"] for variant in item["variants"]],
            ["god", "elohim"],
        )
        self.assertEqual(
            [variant["value"] for variant in item["variants"]],
            ["God", "Elohim"],
        )
        self.assertTrue(item["variants"][0]["default"])

    def test_profile_compiles_preferred_rendering(self):
        compiled = compile_linguistic_projection(
            self.load(),
            "reader-demo",
            self.load_profile(),
        )
        self.assertEqual(
            compiled["projection"]["content"]["text"],
            "In the beginning Elohim created the heavens and the earth.",
        )
        self.assertEqual(compiled["projection"]["content"]["profile_id"], "elohim-demo")
        elo = next(
            item
            for item in compiled["projection"]["content"]["trace"]
            if item["token_id"] == "g3"
        )
        self.assertEqual(elo["rendered"], "Elohim")
        self.assertEqual(elo["origin"]["kind"], "annotation-choice")
        self.assertEqual(elo["origin"]["choice_id"], "elohim")
        self.assertFalse(elo["origin"]["default_choice"])

    def test_preference_changes_projection_not_witness_identity(self):
        default = compile_linguistic_projection(self.load(), "reader-demo")
        preferred = compile_linguistic_projection(
            self.load(),
            "reader-demo",
            self.load_profile(),
        )
        self.assertEqual(
            default["receipt"]["witness_sha256"],
            preferred["receipt"]["witness_sha256"],
        )
        self.assertNotEqual(
            default["receipt"]["transform_sha256"],
            preferred["receipt"]["transform_sha256"],
        )
        self.assertNotEqual(
            default["receipt"]["projection_sha256"],
            preferred["receipt"]["projection_sha256"],
        )

    def test_reader_trace_retains_witness_and_choice_origin(self):
        compiled = compile_linguistic_projection(
            self.load(),
            "reader-demo",
            self.load_profile(),
        )
        trace = compiled["projection"]["content"]["trace"]
        elo = next(item for item in trace if item["token_id"] == "g3")
        self.assertEqual(elo["source_surface"], "אֱלֹהִים")
        self.assertEqual(elo["rendered"], "Elohim")
        self.assertEqual(elo["origin"]["authority"], "demo-projection-only")
        start, end = elo["source_span"]
        self.assertEqual(compiled["witness"]["text"][start:end], "אֱלֹהִים")

    def test_selected_variant_change_changes_receipts_not_witness(self):
        a = self.load()
        b = copy.deepcopy(a)
        b["tokens"][2]["annotations"]["reader_demo"]["variants"][1]["value"] = "Eloah"

        first = compile_linguistic_projection(a, "reader-demo", self.load_profile())
        second = compile_linguistic_projection(b, "reader-demo", self.load_profile())

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

    def test_unselected_variant_change_does_not_invalidate_default_output(self):
        a = self.load()
        b = copy.deepcopy(a)
        b["tokens"][2]["annotations"]["reader_demo"]["variants"][1]["value"] = "Eloah"

        first = compile_linguistic_projection(a, "reader-demo")
        second = compile_linguistic_projection(b, "reader-demo")

        self.assertEqual(first["receipt"], second["receipt"])

    def test_invalid_profile_choice_fails_closed(self):
        profile = self.load_profile()
        profile["choices"]["g3"] = "not-a-choice"
        with self.assertRaises(ValueError):
            compile_linguistic_projection(self.load(), "reader-demo", profile)

    def test_profile_recipe_mismatch_fails_closed(self):
        profile = self.load_profile()
        profile["recipe"] = "unpointed"
        with self.assertRaises(ValueError):
            compile_linguistic_projection(self.load(), "reader-demo", profile)

    def test_source_mismatch_fails_closed(self):
        specimen = self.load()
        specimen["tokens"][0]["surface"] = "NOT-IN-WITNESS"
        with self.assertRaises(ValueError):
            compile_linguistic_projection(specimen, "reader-demo")


if __name__ == "__main__":
    unittest.main()
