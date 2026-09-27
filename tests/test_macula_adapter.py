from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from revival.adapters.macula import adapt_macula_object_relations
from revival.adapters.oshb import adapt_oshb_verse


ROOT = Path(__file__).resolve().parents[1]
OSHB_XML = ROOT / "sources" / "oshb-v2.2" / "Gen.1.1.xml"
OSHB_MANIFEST = ROOT / "sources" / "oshb-v2.2" / "source.json"
MACULA_XML = ROOT / "sources" / "macula-hebrew" / "Gen.1.1-lowfat.xml"
MACULA_MANIFEST = ROOT / "sources" / "macula-hebrew" / "source.json"


class MaculaObjectRelationAdapterTests(unittest.TestCase):
    def oshb(self):
        return adapt_oshb_verse(
            OSHB_XML.read_text(encoding="utf-8"),
            json.loads(OSHB_MANIFEST.read_text(encoding="utf-8")),
        )

    def adapt(self):
        return adapt_macula_object_relations(
            MACULA_XML.read_text(encoding="utf-8"),
            json.loads(MACULA_MANIFEST.read_text(encoding="utf-8")),
            self.oshb(),
        )

    def test_all_seven_macula_words_align_to_existing_oshb_tokens(self):
        layer = self.adapt()
        alignment = layer["word_alignment"]

        self.assertEqual(len(alignment), 7)
        self.assertEqual(
            [item["oshb_token_id"] for item in alignment],
            ["01xeN", "01Nvk", "01TyA", "01vuQ", "01TSc", "01k5P", "01nPh"],
        )
        self.assertEqual(
            alignment[5]["macula_morpheme_surfaces"],
            ["וְ", "אֵ֥ת"],
        )
        self.assertEqual(
            alignment[5]["oshb_raw_surface"],
            "וְ/אֵ֥ת",
        )

    def test_macula_genesis_1_1_yields_two_object_marker_relations(self):
        layer = self.adapt()

        self.assertEqual(len(layer["relations"]), 2)
        self.assertEqual(
            [item["marker"]["oshb_token_id"] for item in layer["relations"]],
            ["01vuQ", "01k5P"],
        )

    def test_first_marker_points_to_actual_syntax_phrase_and_governing_verb(self):
        relation = self.adapt()["relations"][0]

        self.assertEqual(relation["marker"]["oshb_token_id"], "01vuQ")
        self.assertEqual(relation["marker"]["oshb_component_index"], 0)
        self.assertEqual(relation["governing_verb"]["oshb_token_id"], "01Nvk")
        self.assertEqual(relation["governing_verb"]["source_surface"], "בָּרָ֣א")
        self.assertEqual(relation["marked_phrase"]["oshb_token_ids"], ["01TSc"])
        self.assertEqual(
            relation["marked_phrase"]["source_surfaces"],
            ["הַשָּׁמַ֖יִם"],
        )
        self.assertEqual(relation["syntax_evidence"]["clause_rule"], "PP-V-S-O")
        self.assertEqual(relation["syntax_evidence"]["object_role"], "o")
        self.assertEqual(relation["syntax_evidence"]["marker_phrase_rule"], "OmpNP")
        self.assertEqual(relation["syntax_evidence"]["marked_phrase_rule"], "DetNP")

    def test_second_marker_maps_inside_prefixed_oshb_token(self):
        relation = self.adapt()["relations"][1]

        self.assertEqual(relation["marker"]["oshb_token_id"], "01k5P")
        self.assertEqual(relation["marker"]["oshb_component_index"], 1)
        self.assertEqual(relation["marked_phrase"]["oshb_token_ids"], ["01nPh"])
        self.assertEqual(
            relation["marked_phrase"]["source_surfaces"],
            ["הָאָֽרֶץ׃"],
        )

    def test_semantic_frame_evidence_is_separate_and_matches_each_object_head(self):
        first, second = self.adapt()["relations"]

        self.assertEqual(first["semantic_frame_evidence"]["role"], "A1")
        self.assertEqual(
            first["semantic_frame_evidence"]["matched_heads"],
            [
                {
                    "macula_xml_id": "o010010010052",
                    "oshb_token_id": "01TSc",
                    "source_surface": "הַשָּׁמַ֖יִם",
                }
            ],
        )
        self.assertEqual(
            second["semantic_frame_evidence"]["matched_heads"],
            [
                {
                    "macula_xml_id": "o010010010072",
                    "oshb_token_id": "01nPh",
                    "source_surface": "הָאָֽרֶץ׃",
                }
            ],
        )
        self.assertNotEqual(
            first["syntax_evidence"],
            first["semantic_frame_evidence"],
        )

    def test_fixture_hash_mismatch_fails_closed(self):
        manifest = json.loads(MACULA_MANIFEST.read_text(encoding="utf-8"))
        manifest["fixture_sha256"] = "0" * 64

        with self.assertRaises(ValueError):
            adapt_macula_object_relations(
                MACULA_XML.read_text(encoding="utf-8"),
                manifest,
                self.oshb(),
            )

    def test_oshb_macula_surface_disagreement_fails_closed(self):
        specimen = copy.deepcopy(self.oshb())
        specimen["tokens"][5]["annotations"]["oshb"]["data"]["raw_surface"] = (
            "MISMATCH"
        )

        with self.assertRaises(ValueError):
            adapt_macula_object_relations(
                MACULA_XML.read_text(encoding="utf-8"),
                json.loads(MACULA_MANIFEST.read_text(encoding="utf-8")),
                specimen,
            )

    def test_adapter_receipt_binds_both_source_layers(self):
        layer = self.adapt()
        receipt = layer["adapter_receipt"]

        self.assertEqual(
            receipt["upstream_commit"],
            "47db250bd55d0d8577f2a94fba114ef16c35b23c",
        )
        self.assertEqual(
            receipt["upstream_blob_sha"],
            "08829ff09c7c6b06f2ae01bc980fc182c1d1a4b8",
        )
        self.assertIn("oshb_witness_sha256", receipt)
        self.assertIn("alignment_sha256", receipt)
        self.assertIn("relations_sha256", receipt)


if __name__ == "__main__":
    unittest.main()
