"""Browser expedition builder must preserve Revival source, privacy, and fog."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from revival.object_relations import load_object_relation_instrument
from revival.stack_expedition import build_scripture_stack_expedition
from revival.stack_expedition_atlas import (
    _safe_embed,
    build_stack_expedition_html,
)
from revival.world_places import build_world_places_html

ROOT = Path(__file__).resolve().parents[1]


class StackExpeditionAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus, instrument = load_object_relation_instrument(
            ROOT / "corpora/oshb-v2.2-genesis-opening.json",
            ROOT / "sources/macula-hebrew/Gen.1.1-lowfat.xml",
            ROOT / "sources/macula-hebrew/source.json",
            root=ROOT,
        )
        cls.world, _ = build_world_places_html(corpus, instrument)
        cls.game = build_scripture_stack_expedition(cls.world, companion_packets=[{
            "schema": "static-collective.witness-freeplay-review.v1",
            "source": {"project": "WITNESS", "chapter": "matthew.5", "edition": "engwebp"},
            "progress": {"takeCount": 1},
            "sample": [{
                "recordingId": "witness-take-001",
                "passage": "matthew.5.1",
                "edition": "engwebp",
                "sha256": "a" * 64,
            }],
            "awards": {"Deeds": 0, "Harvests": 0, "Capacity": 0},
        }])

    def test_standalone_html_is_deterministic_source_backed_and_playable(self):
        one = build_stack_expedition_html(self.world, self.game)
        two = build_stack_expedition_html(self.world, self.game)
        self.assertEqual(one, two)
        self.assertIn("The Living Source Expedition", one)
        self.assertIn("revival://oshb-v2.2-genesis-opening", one)
        self.assertIn("Gen.1.1", one)
        self.assertIn("UNMAPPED_EXTERNAL_PASSAGE", one)
        self.assertIn('id="suggest"', one)
        self.assertIn('id="export"', one)
        self.assertIn('id="import"', one)
        self.assertIn("localStorage", one)
        self.assertIn("revival-world-places.html", one)
        self.assertIn("0 Deeds", one)
        self.assertNotIn('"audio_base64":', one)

    def test_no_network_calls_or_source_mutation_in_game_html(self):
        html = build_stack_expedition_html(self.world, self.game)
        self.assertNotIn("fetch(", html)
        self.assertNotIn("XMLHttpRequest", html)
        self.assertNotIn("sendBeacon", html)
        self.assertNotIn("service_role", html)
        self.assertIn("textContent", html)
        self.assertNotIn("innerHTML =", html)

    def test_html_data_script_is_not_broken_by_untrusted_source_literal(self):
        test = _safe_embed({
            "source": "</script><script>alert('oops')</script>",
            "text": "A&B\u2028",
        })
        self.assertNotIn("</script>", test)
        self.assertNotIn("<script>", test)
        self.assertNotIn("\u2028", test)
        self.assertIn("\\u003c", test)
        self.assertIn("\\u0026", test)

    def test_invalid_external_atlas_path_refused(self):
        for value in ("../world.html", "https://elsewhere", "other.txt", "sub/world.html"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "simple local"):
                    build_stack_expedition_html(self.world, self.game, source_atlas_filename=value)

    def test_source_world_is_never_replaced_by_witness_candidate(self):
        game = deepcopy(self.game)
        game["audio_candidates"][0]["passage"] = "Matt.5.1"
        html = build_stack_expedition_html(self.world, game)
        self.assertIn("Matt.5.1", html)
        self.assertIn("UNMAPPED_EXTERNAL_PASSAGE", html)
        self.assertIn("Gen.1.2", html)


if __name__ == "__main__":
    unittest.main()
