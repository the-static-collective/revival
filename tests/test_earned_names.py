from __future__ import annotations

from pathlib import Path
import unittest

from revival.earned_names import (
    build_earned_names_world_html,
    load_lexical_proof,
)
from revival.object_relations import load_object_relation_instrument


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "oshb-v2.2-genesis-opening.json"
MACULA_XML = ROOT / "sources" / "macula-hebrew" / "Gen.1.1-lowfat.xml"
MACULA_MANIFEST = ROOT / "sources" / "macula-hebrew" / "source.json"
LEXICAL_PROOF = (
    ROOT / "sources" / "oshb-hebrew-lexicon" / "genesis-opening-proof.json"
)


class EarnedNamesTests(unittest.TestCase):
    def load(self):
        corpus, instrument = load_object_relation_instrument(
            CORPUS,
            MACULA_XML,
            MACULA_MANIFEST,
            root=ROOT,
        )
        proof = load_lexical_proof(LEXICAL_PROOF)
        return corpus, instrument, proof

    def test_five_pinned_lexemes_name_nine_world_anchors(self):
        corpus, instrument, proof = self.load()
        result, _ = build_earned_names_world_html(corpus, instrument, proof)
        world = result["world"]

        self.assertEqual(world["kind"], "revival-earned-names-world")
        self.assertEqual(world["version"], "012")
        self.assertEqual(set(world["lexemes"]), {"216", "430", "776", "4325", "8064"})
        self.assertEqual(len(world["anchor_names"]), 9)

    def test_elohim_lexeme_collects_three_passage_occurrences(self):
        corpus, instrument, proof = self.load()
        result, _ = build_earned_names_world_html(corpus, instrument, proof)
        lexeme = result["world"]["lexemes"]["430"]

        self.assertEqual(lexeme["hebrew"], "אֱלֹהִים")
        self.assertEqual(lexeme["transliteration"], "elohim")
        self.assertEqual(len(lexeme["occurrence_anchor_addresses"]), 3)
        self.assertTrue(any("Gen.1.1" in item for item in lexeme["occurrence_anchor_addresses"]))
        self.assertTrue(any("Gen.1.2" in item for item in lexeme["occurrence_anchor_addresses"]))
        self.assertTrue(any("Gen.1.3" in item for item in lexeme["occurrence_anchor_addresses"]))

    def test_earth_prefixes_converge_only_after_explicit_morpheme_alignment(self):
        corpus, instrument, proof = self.load()
        result, _ = build_earned_names_world_html(corpus, instrument, proof)
        world = result["world"]
        lexeme = world["lexemes"]["776"]

        self.assertEqual(len(lexeme["occurrence_anchor_addresses"]), 2)
        earned = [
            world["anchor_names"][address]
            for address in lexeme["occurrence_anchor_addresses"]
        ]
        declared = {item["declared_token_lemma"] for item in earned}
        self.assertEqual(declared, {"d/776", "c/d/776"})
        self.assertTrue(all(
            item["selected_component"]["lemma"] == "776"
            for item in earned
        ))

        prefixes = {
            item["declared_token_lemma"]: [
                part["lemma"] for part in item["prefix_components_preserved"]
            ]
            for item in earned
        }
        self.assertEqual(prefixes["d/776"], ["d"])
        self.assertEqual(prefixes["c/d/776"], ["c", "d"])

    def test_lexeme_identity_does_not_resolve_sense_referent_or_world_type(self):
        corpus, instrument, proof = self.load()
        result, _ = build_earned_names_world_html(corpus, instrument, proof)

        for lexeme in result["world"]["lexemes"].values():
            self.assertEqual(lexeme["sense_status"], "fog")
            self.assertEqual(lexeme["referent_status"], "fog")
            self.assertEqual(lexeme["semantic_type"]["status"], "fog")
            self.assertIsNone(lexeme["semantic_type"]["type"])

        for earned in result["world"]["anchor_names"].values():
            self.assertEqual(earned["sense_status"], "fog")
            self.assertEqual(earned["referent_status"], "fog")

    def test_unlisted_lexeme_stays_unnamed_in_bounded_proof(self):
        corpus, instrument, proof = self.load()
        result, _ = build_earned_names_world_html(corpus, instrument, proof)
        world = result["world"]

        tohu_room = world["first_world"]["rooms"]["Gen.1.2::01aPd"]
        self.assertEqual(tohu_room["earned_names"], [])

    def test_light_lexeme_collects_both_genesis_1_3_occurrences(self):
        corpus, instrument, proof = self.load()
        result, _ = build_earned_names_world_html(corpus, instrument, proof)
        lexeme = result["world"]["lexemes"]["216"]

        self.assertEqual(lexeme["transliteration"], "or")
        self.assertEqual(len(lexeme["occurrence_anchor_addresses"]), 2)
        self.assertTrue(all(
            "Gen.1.3" in address
            for address in lexeme["occurrence_anchor_addresses"]
        ))

    def test_receipt_binds_011_ancestry_and_lexical_fixture(self):
        corpus, instrument, proof = self.load()
        result, _ = build_earned_names_world_html(corpus, instrument, proof)
        receipt = result["receipt"]

        self.assertEqual(receipt["corpus_sha256"], corpus["corpus_sha256"])
        self.assertEqual(receipt["lexical_fixture_sha256"], proof["fixture_sha256"])
        self.assertIn("world_places_projection_sha256", receipt)
        self.assertIn("lexemes_sha256", receipt)
        self.assertIn("anchor_names_sha256", receipt)
        self.assertIn("projection_sha256", receipt)

    def test_html_is_deterministic_and_names_without_collapsing_boundaries(self):
        corpus, instrument, proof = self.load()
        first_result, first_html = build_earned_names_world_html(
            corpus, instrument, proof
        )
        second_result, second_html = build_earned_names_world_html(
            corpus, instrument, proof
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(first_html, second_html)
        self.assertIn("Let The Places Earn Names", first_html)
        self.assertIn("אֱלֹהִים", first_html)
        self.assertIn("אֶרֶץ", first_html)
        self.assertIn("שָׁמַיִם", first_html)
        self.assertIn("מַיִם", first_html)
        self.assertIn("אוֹר", first_html)
        self.assertIn(
            "lexeme != sense != referent != person/place/object/event",
            first_html,
        )
        self.assertIn("location.hash", first_html)


if __name__ == "__main__":
    unittest.main()
