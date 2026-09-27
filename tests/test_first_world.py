from __future__ import annotations

from pathlib import Path
import unittest

from revival.first_world import build_first_world_html
from revival.object_relations import load_object_relation_instrument


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "oshb-v2.2-genesis-opening.json"
MACULA_XML = ROOT / "sources" / "macula-hebrew" / "Gen.1.1-lowfat.xml"
MACULA_MANIFEST = ROOT / "sources" / "macula-hebrew" / "source.json"


class FirstWorldTests(unittest.TestCase):
    def load(self):
        return load_object_relation_instrument(
            CORPUS,
            MACULA_XML,
            MACULA_MANIFEST,
            root=ROOT,
        )

    def test_world_composes_all_three_proven_instruments(self):
        corpus, instrument = self.load()
        result, _ = build_first_world_html(corpus, instrument)
        world = result["world"]

        self.assertEqual(world["kind"], "revival-first-world")
        self.assertEqual(world["version"], "010")
        self.assertEqual(world["corpus_sha256"], corpus["corpus_sha256"])
        self.assertEqual(
            set(world["child_receipts"]),
            {"corpus_atlas", "aleph_tav_atlas", "object_relation_atlas"},
        )

    def test_projection_switching_changes_world_without_changing_corpus(self):
        corpus, instrument = self.load()
        result, _ = build_first_world_html(corpus, instrument)
        world = result["world"]

        source = world["projections"]["source"][0]
        operator = world["projections"]["operator"][0]
        letters = world["projections"]["letters"][0]
        hidden = world["projections"]["hidden"][0]

        self.assertIn("אֵ֥ת", source["text"])
        self.assertIn("[OBJ→]", operator["text"])
        self.assertIn("⟦את⟧", letters["text"])
        self.assertNotIn("אֵ֥ת", hidden["text"])
        self.assertEqual(world["corpus_sha256"], corpus["corpus_sha256"])

    def test_one_marker_room_contains_lemma_family_and_relation_doors(self):
        corpus, instrument = self.load()
        result, _ = build_first_world_html(corpus, instrument)
        room = result["world"]["rooms"]["Gen.1.1::01vuQ"]

        kinds = [door["kind"] for door in room["doors"]]
        self.assertIn("source-neighbor", kinds)
        self.assertIn("derived-family-occurrence", kinds)
        self.assertIn("governing-verb", kinds)
        self.assertIn("marked-phrase-token", kinds)
        self.assertIn("semantic-a1-head", kinds)

        self.assertTrue(room["layers"]["source"]["available"])
        self.assertTrue(room["layers"]["aleph_tav"]["available"])
        self.assertTrue(room["layers"]["syntax"]["available"])
        self.assertTrue(room["layers"]["semantic_frame"]["available"])
        self.assertFalse(room["layers"]["interpretation"]["available"])
        self.assertEqual(room["layers"]["interpretation"]["status"], "fog")

    def test_elohim_room_keeps_cross_passage_lemma_doors(self):
        corpus, instrument = self.load()
        result, _ = build_first_world_html(corpus, instrument)
        room = result["world"]["rooms"]["Gen.1.1::01TyA"]

        lemma_doors = [
            door for door in room["doors"]
            if door["kind"] == "lemma-occurrence"
        ]
        self.assertEqual(
            [
                (door["destination_locator"], door["destination_token_id"])
                for door in lemma_doors
            ],
            [("Gen.1.2", "01x9c"), ("Gen.1.3", "01JM7")],
        )
        self.assertTrue(all(
            door["epistemic_status"] == "derived"
            for door in lemma_doors
        ))

    def test_world_receipt_binds_child_atlases_rooms_and_projections(self):
        corpus, instrument = self.load()
        result, _ = build_first_world_html(corpus, instrument)
        receipt = result["receipt"]

        self.assertEqual(receipt["corpus_sha256"], corpus["corpus_sha256"])
        self.assertIn("corpus_atlas_projection_sha256", receipt)
        self.assertIn("aleph_tav_atlas_projection_sha256", receipt)
        self.assertIn("object_relation_atlas_projection_sha256", receipt)
        self.assertIn("rooms_sha256", receipt)
        self.assertIn("projections_sha256", receipt)
        self.assertIn("projection_sha256", receipt)

    def test_html_is_deterministic_and_exposes_fog_and_vanishing(self):
        corpus, instrument = self.load()
        first_result, first_html = build_first_world_html(corpus, instrument)
        second_result, second_html = build_first_world_html(corpus, instrument)

        self.assertEqual(first_result, second_result)
        self.assertEqual(first_html, second_html)
        self.assertIn("Every object in this world knows where it came from.", first_html)
        self.assertIn("Fog is a feature.", first_html)
        self.assertIn("suppressed by the current projection", first_html)
        self.assertIn("syntax != semantic frame", first_html)
        self.assertIn("projection != witness", first_html)


if __name__ == "__main__":
    unittest.main()
