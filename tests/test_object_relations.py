from __future__ import annotations

from pathlib import Path
import unittest

from revival.object_relations import (
    load_object_relation_instrument,
    open_object_relation_room,
)
from revival.object_relations_atlas import build_object_relation_atlas_html


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "oshb-v2.2-genesis-opening.json"
MACULA_XML = ROOT / "sources" / "macula-hebrew" / "Gen.1.1-lowfat.xml"
MACULA_MANIFEST = ROOT / "sources" / "macula-hebrew" / "source.json"


class ObjectRelationInstrumentTests(unittest.TestCase):
    def load(self):
        return load_object_relation_instrument(
            CORPUS,
            MACULA_XML,
            MACULA_MANIFEST,
            root=ROOT,
        )

    def test_instrument_enriches_both_aleph_tav_occurrences(self):
        _, instrument = self.load()

        self.assertEqual(len(instrument["occurrences"]), 2)
        self.assertTrue(
            all(
                item["relation_status"] == "attributable-macula-relation"
                for item in instrument["occurrences"]
            )
        )
        self.assertEqual(
            [item["object_relation"]["marker"]["oshb_token_id"]
             for item in instrument["occurrences"]],
            ["01vuQ", "01k5P"],
        )

    def test_room_exposes_verb_phrase_and_semantic_head_as_distinct_doors(self):
        corpus, instrument = self.load()
        room = open_object_relation_room(
            corpus,
            instrument,
            "Gen.1.1",
            "01vuQ",
        )["room"]

        self.assertEqual(
            [item["kind"] for item in room["doors"]],
            [
                "governing-verb",
                "marked-phrase-token",
                "semantic-a1-head",
            ],
        )
        self.assertEqual(
            [item["destination_token_id"] for item in room["doors"]],
            ["01Nvk", "01TSc", "01TSc"],
        )
        self.assertEqual(
            room["doors"][1]["evidence_layer"],
            "syntax tree",
        )
        self.assertEqual(
            room["doors"][2]["evidence_layer"],
            "semantic frame",
        )

    def test_instrument_explicitly_retires_adjacency_shortcut(self):
        _, instrument = self.load()

        self.assertIn(
            "do not use immediate-next-token adjacency",
            instrument["law"]["no_adjacency_substitute"],
        )

    def test_relation_receipt_binds_macula_relation_and_local_room(self):
        corpus, instrument = self.load()
        opened = open_object_relation_room(
            corpus,
            instrument,
            "Gen.1.1",
            "01k5P",
        )

        self.assertIn("macula_relation_sha256", opened["receipt"])
        self.assertIn("local_room_projection_sha256", opened["receipt"])
        self.assertEqual(
            opened["receipt"]["instrument_sha256"],
            instrument["instrument_sha256"],
        )

    def test_atlas_contains_all_source_tokens_and_two_relation_rooms(self):
        corpus, instrument = self.load()
        result, _ = build_object_relation_atlas_html(corpus, instrument)

        self.assertEqual(len(result["atlas"]["source_tokens"]), 7)
        self.assertEqual(
            set(result["atlas"]["relation_rooms"]),
            {"Gen.1.1::01vuQ", "Gen.1.1::01k5P"},
        )
        self.assertEqual(len(result["atlas"]["local_rooms"]), 7)

    def test_atlas_is_deterministic_and_shows_separate_evidence(self):
        corpus, instrument = self.load()
        first_result, first_html = build_object_relation_atlas_html(
            corpus, instrument
        )
        second_result, second_html = build_object_relation_atlas_html(
            corpus, instrument
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(first_html, second_html)
        self.assertIn("Object Relations", first_html)
        self.assertIn("governing verb", first_html)
        self.assertIn("Syntax tree", first_html)
        self.assertIn("Semantic frame", first_html)
        self.assertIn("PP-V-S-O", first_html)
        self.assertIn("MACULA Hebrew Linguistic Datasets", first_html)


if __name__ == "__main__":
    unittest.main()
