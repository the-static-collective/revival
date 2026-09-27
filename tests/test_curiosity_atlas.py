from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from revival.atlas import build_curiosity_atlas, build_curiosity_atlas_html


ROOT = Path(__file__).resolve().parents[1]
SPECIMEN = ROOT / "specimens" / "genesis-1-1-linguistic.json"
ELOHIM_PROFILE = ROOT / "profiles" / "genesis-1-1-elohim.json"


class CuriosityAtlasTests(unittest.TestCase):
    def load(self):
        return json.loads(SPECIMEN.read_text(encoding="utf-8"))

    def load_profile(self):
        return json.loads(ELOHIM_PROFILE.read_text(encoding="utf-8"))

    def test_atlas_contains_room_for_every_emitted_token(self):
        result = build_curiosity_atlas(self.load(), "reader-demo")
        atlas = result["atlas"]
        emitted = [item["token_id"] for item in atlas["compiled_trace"]]

        self.assertEqual(atlas["room_order"], emitted)
        self.assertEqual(set(atlas["rooms"]), set(emitted))
        self.assertEqual(set(atlas["room_receipts"]), set(emitted))

    def test_atlas_is_deterministic(self):
        first_result, first_html = build_curiosity_atlas_html(
            self.load(),
            "reader-demo",
        )
        second_result, second_html = build_curiosity_atlas_html(
            self.load(),
            "reader-demo",
        )
        self.assertEqual(first_result, second_result)
        self.assertEqual(first_html, second_html)

    def test_preference_profile_changes_atlas_not_witness_identity(self):
        default = build_curiosity_atlas(self.load(), "reader-demo")
        preferred = build_curiosity_atlas(
            self.load(),
            "reader-demo",
            self.load_profile(),
        )

        self.assertEqual(
            default["receipt"]["witness_sha256"],
            preferred["receipt"]["witness_sha256"],
        )
        self.assertNotEqual(
            default["receipt"]["projection_sha256"],
            preferred["receipt"]["projection_sha256"],
        )
        self.assertEqual(
            preferred["atlas"]["compiled_text"],
            "In the beginning Elohim created the heavens and the earth.",
        )
        self.assertEqual(
            preferred["atlas"]["rooms"]["g3"]["token"]["current_rendering"],
            "Elohim",
        )

    def test_html_is_standalone_walkable_surface(self):
        _, html = build_curiosity_atlas_html(self.load(), "reader-demo")

        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn('id="revival-data"', html)
        self.assertIn('id="verse"', html)
        self.assertIn('id="relations"', html)
        self.assertIn("Curiosity Atlas", html)
        self.assertIn("openRoom", html)
        self.assertIn("room_receipts", html)

    def test_embedded_json_escapes_script_breakout_text(self):
        specimen = copy.deepcopy(self.load())
        specimen["tokens"][2]["annotations"]["reader_demo"]["variants"][0]["value"] = (
            '</script><script id="pwn">alert(1)</script>'
        )

        result, html = build_curiosity_atlas_html(specimen, "reader-demo")

        self.assertIn("pwn", result["atlas"]["compiled_text"])
        self.assertNotIn('</script><script id="pwn">', html)
        self.assertIn("\\u003c/script\\u003e", html)

    def test_relation_doors_are_walkable_inside_same_atlas(self):
        atlas = build_curiosity_atlas(self.load(), "reader-demo")["atlas"]
        god_room = atlas["rooms"]["g3"]
        relation_door = next(
            door for door in god_room["doors"] if door["kind"] == "relation"
        )

        destination = relation_door["destination_token_id"]
        self.assertIn(destination, atlas["rooms"])
        self.assertEqual(destination, "g2")
        self.assertEqual(
            atlas["rooms"][destination]["token"]["current_rendering"],
            "created",
        )


if __name__ == "__main__":
    unittest.main()
