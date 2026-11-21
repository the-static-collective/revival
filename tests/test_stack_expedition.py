"""Revival 013 tests: game affordances must never promote external claims."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from revival.kernel.v1 import sha256
from revival.object_relations import load_object_relation_instrument
from revival.stack_expedition import (
    build_scripture_stack_expedition,
    inspect_companion_packet,
    normalize_passage,
)
from revival.world_places import build_world_places_html

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "oshb-v2.2-genesis-opening.json"
MACULA_XML = ROOT / "sources" / "macula-hebrew" / "Gen.1.1-lowfat.xml"
MACULA_MANIFEST = ROOT / "sources" / "macula-hebrew" / "source.json"
HASH = "a" * 64
ZERO = {"Deeds": 0, "Harvests": 0, "Capacity": 0}


def freeplay(passage="matthew.5.1", *, edition="engwebp"):
    return {
        "schema": "static-collective.witness-freeplay-review.v1",
        "source": {
            "project": "WITNESS",
            "game": "witness.freeplay.v1",
            "chapter": passage.rsplit(".", 1)[0],
            "roomId": None,
            "edition": edition,
        },
        "progress": {"coveredAddresses": [1], "takeCount": 1},
        "sample": [{
            "recordingId": "wit-matthew-5-v1",
            "passage": passage,
            "edition": edition,
            "sha256": HASH,
            "declaredReader": "Anonymous",
        }],
        "bounds": {"noAudioIncluded": True, "noAutomaticFullMeasureAwards": True},
        "awards": dict(ZERO),
        "status": "REVIEW_ONLY_UNVERIFIED",
    }


def pact_recording():
    return {
        "schema": "static-collective.witness-pact-full-measure-candidate.v1",
        "source": {"project": "WITNESS community audio Bible", "bridge": "THE PACT v0.4"},
        "recording": {
            "recordingId": "wit-matthew-5-v1", "passage": "matthew.5.1",
            "edition": "engwebp", "sha256": HASH,
        },
        "bridge": {"linkedBy": "you", "withdrawn": False, "peerReports": []},
        "awards": dict(ZERO),
    }


class RevivalScriptureStack013Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus, instrument = load_object_relation_instrument(
            CORPUS, MACULA_XML, MACULA_MANIFEST, root=ROOT
        )
        cls.world_result, _ = build_world_places_html(corpus, instrument)
        cls.root = cls.world_result["world"]["root_address"]
        cls.passage = next(
            p["address"] for p in cls.world_result["world"]["places"]
            if p["kind"] == "passage" and p["label"] == "Gen.1.1"
        )
        cls.token = cls.world_result["world"]["room_addresses"]["Gen.1.1::01TyA"]

    def test_address_normalization_does_not_invent_textual_identity(self):
        self.assertEqual(normalize_passage("genesis.1.1"), "Gen.1.1")
        self.assertEqual(normalize_passage("Gen.1.1"), "Gen.1.1")
        self.assertEqual(normalize_passage("matthew.5.1"), "Matt.5.1")
        self.assertIsNone(normalize_passage("john.3.16"))
        self.assertIsNone(normalize_passage("matthew.0.1"))

    def test_unvisited_world_has_no_game_points_and_no_automatic_rewards(self):
        result = build_scripture_stack_expedition(self.world_result)
        self.assertEqual(result["exploration"]["glimmers"], 0)
        self.assertEqual(result["full_measure"], {**ZERO, "admitted": False})
        self.assertFalse(any(x["unlocked"] for x in result["exploration"]["milestones"]))
        self.assertEqual(result["world"]["projection_sha256"], self.world_result["receipt"]["projection_sha256"])

    def test_exploring_only_real_places_yields_unique_local_play_glimmers(self):
        result = build_scripture_stack_expedition(
            self.world_result,
            explored=[self.passage, self.token, self.passage, "revival://invented/token"],
        )
        self.assertEqual(result["exploration"]["glimmers"], 2)
        self.assertEqual(len(result["exploration"]["addresses"]), 2)
        self.assertTrue(next(x for x in result["exploration"]["milestones"] if x["id"] == "source-token")["unlocked"])
        self.assertEqual(result["full_measure"]["Deeds"], 0)

    def test_real_matthew_5_witness_is_unmapped_not_falsely_attached_to_genesis(self):
        result = build_scripture_stack_expedition(
            self.world_result, companion_packets=[freeplay()]
        )
        self.assertEqual(len(result["audio_candidates"]), 1)
        audio = result["audio_candidates"][0]
        self.assertEqual(audio["passage"], "Matt.5.1")
        self.assertEqual(audio["status"], "UNMAPPED_EXTERNAL_PASSAGE")
        self.assertIsNone(audio["revival_address"])
        self.assertEqual(result["exploration"]["glimmers"], 0)
        self.assertEqual(result["full_measure"]["Harvests"], 0)
        self.assertTrue(next(x for x in result["exploration"]["milestones"] if x["id"] == "honor-fog")["unlocked"])

    def test_same_passage_address_is_only_an_address_match_not_edition_equivalence(self):
        packet = freeplay("genesis.1.1", edition="engwebp")
        result = build_scripture_stack_expedition(self.world_result, companion_packets=[packet])
        audio = result["audio_candidates"][0]
        self.assertEqual(audio["status"], "ADDRESS_MATCH_ONLY")
        self.assertEqual(audio["revival_address"], self.passage)
        self.assertNotEqual(audio["declared_edition"], "oshb-v2.2")
        self.assertIn("never a textual witness", audio["authority"])
        self.assertEqual(result["exploration"]["glimmers"], 0)

    def test_independent_pact_audio_reference_is_a_candidate_only(self):
        result = build_scripture_stack_expedition(
            self.world_result, companion_packets=[pact_recording()]
        )
        self.assertEqual(result["packet_reviews"][0]["status"], "UNVERIFIED")
        self.assertEqual(result["audio_candidates"][0]["status"], "UNMAPPED_EXTERNAL_PASSAGE")
        self.assertEqual(result["full_measure"]["Capacity"], 0)

    def test_withdrawn_link_fails_closed(self):
        packet = pact_recording()
        packet["bridge"]["withdrawn"] = True
        outcome = inspect_companion_packet(packet)
        self.assertEqual(outcome["status"], "HELD")
        self.assertEqual(outcome["reason"], "INVALID_OR_WITHDRAWN_BRIDGE")

    def test_private_payload_cannot_cross_for_review(self):
        packet = freeplay()
        packet["token"] = "should not be accepted"
        outcome = inspect_companion_packet(packet)
        self.assertEqual(outcome["status"], "HELD")
        self.assertEqual(outcome["reason"], "PRIVATE_OR_OVERSIZED_PAYLOAD")
        packet = freeplay()
        packet["sample"][0]["audio_base64"] = "raw audio should stay in WITNESS"
        self.assertEqual(inspect_companion_packet(packet)["status"], "HELD")

    def test_invalid_digest_and_positive_award_are_held(self):
        packet = freeplay()
        packet["sample"][0]["sha256"] = "not-a-digest"
        self.assertEqual(inspect_companion_packet(packet)["status"], "HELD")
        packet = freeplay()
        packet["awards"]["Deeds"] = 1
        self.assertEqual(inspect_companion_packet(packet)["reason"], "FOREIGN_AWARD_CLAIM")

    def test_pact_quest_claim_does_not_mutate_scripture_places(self):
        packet = {
            "schema": "static-collective.pact-world-review.v1",
            "awards": dict(ZERO),
            "subject": {"title": "FELLOWSHIP supper"},
        }
        result = build_scripture_stack_expedition(
            self.world_result, companion_packets=[packet]
        )
        self.assertEqual(result["packet_reviews"][0]["kind"], "pact-quest")
        self.assertEqual(result["audio_candidates"], [])
        self.assertEqual(result["exploration"]["glimmers"], 0)

    def test_tampered_derived_world_is_refused(self):
        corrupt = deepcopy(self.world_result)
        corrupt["world"]["places"][0]["label"] = "injected"
        with self.assertRaisesRegex(ValueError, "receipt does not match"):
            build_scripture_stack_expedition(corrupt)

    def test_deterministic_receipt_and_no_automatic_source_promotion(self):
        kwargs = {"explored": [self.passage], "companion_packets": [freeplay()]}
        first = build_scripture_stack_expedition(self.world_result, **kwargs)
        second = build_scripture_stack_expedition(self.world_result, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["receipt"]["sha256"], sha256({
            k: v for k, v in first.items() if k != "receipt"
        }))
        self.assertEqual(first["full_measure"]["admitted"], False)


if __name__ == "__main__":
    unittest.main()
