from __future__ import annotations

from pathlib import Path
import unittest

from revival.aleph_tav import (
    FAMILY_ID,
    build_aleph_tav_instrument,
    decompose_oshb_token,
    open_aleph_tav_room,
)
from revival.corpus import load_corpus_manifest


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "oshb-v2.2-genesis-opening.json"


class AlephTavInstrumentTests(unittest.TestCase):
    def load(self):
        return load_corpus_manifest(CORPUS, root=ROOT)

    def instrument(self):
        return build_aleph_tav_instrument(self.load())

    def test_genesis_1_1_has_two_derived_family_occurrences(self):
        instrument = self.instrument()
        self.assertEqual(
            [
                (item["locator"], item["token_id"])
                for item in instrument["occurrences"]
            ],
            [
                ("Gen.1.1", "01vuQ"),
                ("Gen.1.1", "01k5P"),
            ],
        )
        self.assertEqual(instrument["family_id"], FAMILY_ID)

    def test_plain_et_decomposes_as_particle_direct_object_marker(self):
        corpus = self.load()
        token = next(
            item
            for item in corpus["_specimens_by_locator"]["Gen.1.1"]["tokens"]
            if item["id"] == "01vuQ"
        )
        decomposition = decompose_oshb_token(token)

        self.assertEqual(decomposition["declared_lemma"], "853")
        self.assertEqual(decomposition["declared_morph"], "HTo")
        self.assertEqual(len(decomposition["parts"]), 1)
        part = decomposition["parts"][0]
        self.assertEqual(part["lemma"], "853")
        self.assertEqual(part["unpointed"], "את")
        self.assertEqual(part["morphology"]["part_of_speech"], "Particle")
        self.assertEqual(
            part["morphology"]["particle_type"],
            "direct object marker",
        )
        self.assertEqual(
            [item["name"] for item in part["letters"]],
            ["Aleph", "Tav"],
        )

    def test_prefixed_et_keeps_upstream_identity_and_exposes_components(self):
        corpus = self.load()
        token = next(
            item
            for item in corpus["_specimens_by_locator"]["Gen.1.1"]["tokens"]
            if item["id"] == "01k5P"
        )
        decomposition = decompose_oshb_token(token)

        self.assertEqual(decomposition["declared_lemma"], "c/853")
        self.assertEqual(decomposition["declared_morph"], "HC/To")
        self.assertEqual(
            [part["lemma"] for part in decomposition["parts"]],
            ["c", "853"],
        )
        self.assertEqual(
            [part["surface"] for part in decomposition["parts"]],
            ["וְ", "אֵ֥ת"],
        )
        self.assertEqual(
            decomposition["parts"][0]["morphology"]["part_of_speech"],
            "Conjunction",
        )
        self.assertEqual(
            decomposition["parts"][1]["morphology"]["particle_type"],
            "direct object marker",
        )

    def test_family_bridge_does_not_rewrite_declared_lemma_strings(self):
        instrument = self.instrument()
        self.assertEqual(
            [item["declared_lemma"] for item in instrument["occurrences"]],
            ["853", "c/853"],
        )
        self.assertIn(
            "does not rewrite",
            instrument["identity_boundary"],
        )

    def test_instrument_room_connects_plain_and_prefixed_occurrences(self):
        instrument = self.instrument()
        room = open_aleph_tav_room(
            instrument,
            "Gen.1.1",
            "01vuQ",
        )["room"]

        self.assertEqual(len(room["constellation_doors"]), 1)
        door = room["constellation_doors"][0]
        self.assertEqual(door["destination_token_id"], "01k5P")
        self.assertEqual(door["destination_declared_lemma"], "c/853")

    def test_projection_examples_make_marker_visibility_explicit(self):
        instrument = self.instrument()
        plain = instrument["occurrences"][0]
        prefixed = instrument["occurrences"][1]

        self.assertEqual(plain["projection_examples"]["operator"], "[OBJ→]")
        self.assertEqual(plain["projection_examples"]["letters"], "⟦את⟧")
        self.assertEqual(plain["projection_examples"]["hidden"], "")
        self.assertEqual(
            prefixed["projection_examples"]["operator"],
            "וְ + [OBJ→]",
        )
        self.assertEqual(
            prefixed["projection_examples"]["letters"],
            "וְ + ⟦את⟧",
        )
        self.assertEqual(
            prefixed["projection_examples"]["hidden"],
            "וְ",
        )

    def test_context_target_is_explicitly_only_next_source_token(self):
        instrument = self.instrument()
        first, second = instrument["occurrences"]

        self.assertEqual(
            first["next_token_context"]["token_id"],
            "01TSc",
        )
        self.assertEqual(
            second["next_token_context"]["token_id"],
            "01nPh",
        )
        self.assertEqual(
            first["next_token_context"]["rule"],
            "immediate next source token only",
        )

    def test_reading_hint_is_not_misrepresented_as_oshb_data(self):
        instrument = self.instrument()
        occurrence = instrument["occurrences"][0]

        self.assertEqual(occurrence["reading"]["component_hint"], "et")
        self.assertEqual(
            occurrence["reading"]["authority"],
            "revival-008-pedagogical-lens",
        )
        self.assertIn("not supplied by OSHB", occurrence["reading"]["note"])


if __name__ == "__main__":
    unittest.main()
