from __future__ import annotations

from pathlib import Path
import unittest

from revival.aleph_tav_atlas import build_aleph_tav_atlas_html
from revival.corpus import load_corpus_manifest


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "oshb-v2.2-genesis-opening.json"


class AlephTavAtlasTests(unittest.TestCase):
    def load(self):
        return load_corpus_manifest(CORPUS, root=ROOT)

    def test_builds_preserve_one_source_and_make_visibility_explicit(self):
        result, _ = build_aleph_tav_atlas_html(self.load())
        builds = result["atlas"]["builds"]

        self.assertIn("אֵ֥ת", builds["source"]["text"])
        self.assertIn("וְאֵ֥ת", builds["source"]["text"])
        self.assertIn("[OBJ→]", builds["operator"]["text"])
        self.assertIn("וְ + [OBJ→]", builds["operator"]["text"])
        self.assertIn("⟦את⟧", builds["letters"]["text"])
        self.assertIn("וְ + ⟦את⟧", builds["letters"]["text"])
        self.assertNotIn("אֵ֥ת", builds["hidden"]["text"])
        self.assertIn("וְ הָאָֽרֶץ׃", builds["hidden"]["text"])

    def test_atlas_contains_both_genesis_1_1_instrument_rooms(self):
        result, _ = build_aleph_tav_atlas_html(self.load())
        rooms = result["atlas"]["rooms"]

        self.assertIn("Gen.1.1::01vuQ", rooms)
        self.assertIn("Gen.1.1::01k5P", rooms)
        self.assertEqual(
            rooms["Gen.1.1::01vuQ"]["occurrence"]["grammar"]["particle_type"],
            "direct object marker",
        )

    def test_atlas_receipt_binds_corpus_family_and_rooms(self):
        result, _ = build_aleph_tav_atlas_html(self.load())
        receipt = result["receipt"]

        self.assertEqual(
            receipt["corpus_sha256"],
            result["atlas"]["corpus_sha256"],
        )
        self.assertEqual(
            receipt["family_sha256"],
            result["atlas"]["family_sha256"],
        )
        self.assertIn("rooms_sha256", receipt)
        self.assertIn("projection_sha256", receipt)

    def test_html_is_deterministic_and_contains_learning_instrument(self):
        first_result, first_html = build_aleph_tav_atlas_html(self.load())
        second_result, second_html = build_aleph_tav_atlas_html(self.load())

        self.assertEqual(first_result, second_result)
        self.assertEqual(first_html, second_html)
        self.assertIn("Aleph/Tav Instrument", first_html)
        self.assertIn("See what English can make invisible", first_html)
        self.assertIn("direct object marker", first_html)
        self.assertIn("OBJ→", first_html)
        self.assertIn("Aleph", first_html)
        self.assertIn("Tav", first_html)

    def test_interpretive_boundary_is_present_in_walkable_artifact(self):
        _, html = build_aleph_tav_atlas_html(self.load())

        self.assertIn("first Hebrew letter", html)
        self.assertIn("Tav is the last", html)
        self.assertIn(
            "not encoded here as the grammatical meaning",
            html,
        )


if __name__ == "__main__":
    unittest.main()
