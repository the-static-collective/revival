from __future__ import annotations

from pathlib import Path
import unittest

from revival.object_relations import load_object_relation_instrument
from revival.world_places import build_world_places_html


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "oshb-v2.2-genesis-opening.json"
MACULA_XML = ROOT / "sources" / "macula-hebrew" / "Gen.1.1-lowfat.xml"
MACULA_MANIFEST = ROOT / "sources" / "macula-hebrew" / "source.json"


class WorldPlacesTests(unittest.TestCase):
    def load(self):
        return load_object_relation_instrument(
            CORPUS,
            MACULA_XML,
            MACULA_MANIFEST,
            root=ROOT,
        )

    def test_every_source_token_receives_a_stable_world_address(self):
        corpus, instrument = self.load()
        result, _ = build_world_places_html(corpus, instrument)
        world = result["world"]

        expected = sum(
            len(corpus["_specimens_by_locator"][witness["locator"]]["tokens"])
            for witness in corpus["witnesses"]
        )
        self.assertEqual(len(world["room_addresses"]), expected)
        self.assertEqual(expected, 27)
        self.assertEqual(
            world["room_addresses"]["Gen.1.1::01TSc"],
            "revival://oshb-v2.2-genesis-opening/scene/"
            "genesis-opening-proof/passage/Gen.1.1/token/01TSc",
        )

    def test_scale_has_world_scene_passage_and_token_places(self):
        corpus, instrument = self.load()
        result, _ = build_world_places_html(corpus, instrument)
        kinds = [place["kind"] for place in result["world"]["places"]]

        self.assertEqual(kinds.count("world"), 1)
        self.assertEqual(kinds.count("scene"), 1)
        self.assertEqual(kinds.count("passage"), 3)
        self.assertEqual(kinds.count("token"), 27)

    def test_scene_is_explicitly_a_projection_container_not_source_division(self):
        corpus, instrument = self.load()
        result, _ = build_world_places_html(corpus, instrument)
        scene = next(
            place for place in result["world"]["places"]
            if place["kind"] == "scene"
        )

        self.assertEqual(scene["epistemic_status"], "declared")
        self.assertIn("not asserted as a source-authored scene division", scene["note"])

    def test_morphology_earns_nominal_and_verbal_anchors(self):
        corpus, instrument = self.load()
        result, _ = build_world_places_html(corpus, instrument)
        world = result["world"]
        by_address = {place["address"]: place for place in world["places"]}

        heavens_anchor = next(
            by_address[address]
            for address in world["anchor_addresses"]["Gen.1.1::01TSc"]
        )
        create_anchor = next(
            by_address[address]
            for address in world["anchor_addresses"]["Gen.1.1::01Nvk"]
        )

        self.assertEqual(heavens_anchor["kind"], "nominal-anchor")
        self.assertIn("N", heavens_anchor["morphology_pos_codes"])
        self.assertEqual(create_anchor["kind"], "verbal-anchor")
        self.assertIn("V", create_anchor["morphology_pos_codes"])

    def test_anchor_semantics_remain_fog_instead_of_guessing_world_type(self):
        corpus, instrument = self.load()
        result, _ = build_world_places_html(corpus, instrument)
        anchors = [
            place for place in result["world"]["places"]
            if place["kind"].endswith("-anchor")
        ]

        self.assertTrue(anchors)
        self.assertTrue(all(
            anchor["semantic_type"]["status"] == "fog"
            for anchor in anchors
        ))
        self.assertTrue(all(
            anchor["semantic_type"]["type"] is None
            for anchor in anchors
        ))
        self.assertIn(
            "person",
            anchors[0]["semantic_type"]["candidate_vocabulary"],
        )
        self.assertIn(
            "place",
            anchors[0]["semantic_type"]["candidate_vocabulary"],
        )

    def test_first_world_rooms_gain_scale_paths_without_rewriting_010(self):
        corpus, instrument = self.load()
        result, _ = build_world_places_html(corpus, instrument)
        room = result["world"]["first_world"]["rooms"]["Gen.1.1::01TyA"]

        self.assertEqual(len(room["scale_path"]), 4)
        self.assertEqual(room["scale_path"][0], result["world"]["root_address"])
        self.assertEqual(room["scale_path"][-1], room["world_address"])
        self.assertIn("lemma-occurrence", [door["kind"] for door in room["doors"]])

    def test_receipt_binds_first_world_places_edges_and_addresses(self):
        corpus, instrument = self.load()
        result, _ = build_world_places_html(corpus, instrument)
        receipt = result["receipt"]

        self.assertEqual(receipt["corpus_sha256"], corpus["corpus_sha256"])
        self.assertIn("first_world_projection_sha256", receipt)
        self.assertIn("places_sha256", receipt)
        self.assertIn("edges_sha256", receipt)
        self.assertIn("room_addresses_sha256", receipt)
        self.assertIn("projection_sha256", receipt)

    def test_html_is_deterministic_and_exposes_hash_address_navigation(self):
        corpus, instrument = self.load()
        first_result, first_html = build_world_places_html(corpus, instrument)
        second_result, second_html = build_world_places_html(corpus, instrument)

        self.assertEqual(first_result, second_result)
        self.assertEqual(first_html, second_html)
        self.assertIn("The World Has Places", first_html)
        self.assertIn("revival://oshb-v2.2-genesis-opening", first_html)
        self.assertIn("location.hash", first_html)
        self.assertIn("Semantic type: fog by default.", first_html)
        self.assertIn("place != referent", first_html)
        self.assertIn("scene container != source division", first_html)


if __name__ == "__main__":
    unittest.main()
