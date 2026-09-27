from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from revival.curiosity import open_token_room


ROOT = Path(__file__).resolve().parents[1]
SPECIMEN = ROOT / "specimens" / "genesis-1-1-linguistic.json"
ELOHIM_PROFILE = ROOT / "profiles" / "genesis-1-1-elohim.json"


class CuriosityRoomTests(unittest.TestCase):
    def load(self):
        return json.loads(SPECIMEN.read_text(encoding="utf-8"))

    def load_profile(self):
        return json.loads(ELOHIM_PROFILE.read_text(encoding="utf-8"))

    def test_room_opens_source_backed_token(self):
        result = open_token_room(self.load(), "reader-demo", "g3")
        room = result["room"]

        self.assertEqual(room["token"]["source_surface"], "אֱלֹהִים")
        self.assertEqual(room["token"]["current_rendering"], "God")
        self.assertEqual(room["witness_locator"], "Genesis 1:1")
        start, end = room["token"]["source_span"]
        witness = self.load()["witness"]["text"]
        self.assertEqual(witness[start:end], "אֱלֹהִים")

    def test_room_reflects_profile_rendering_without_changing_source(self):
        default = open_token_room(self.load(), "reader-demo", "g3")
        preferred = open_token_room(
            self.load(),
            "reader-demo",
            "g3",
            self.load_profile(),
        )

        self.assertEqual(default["room"]["token"]["current_rendering"], "God")
        self.assertEqual(preferred["room"]["token"]["current_rendering"], "Elohim")
        self.assertEqual(
            default["receipt"]["witness_sha256"],
            preferred["receipt"]["witness_sha256"],
        )
        self.assertNotEqual(
            default["receipt"]["projection_sha256"],
            preferred["receipt"]["projection_sha256"],
        )

    def test_room_exposes_rendering_choice_doors(self):
        room = open_token_room(self.load(), "reader-demo", "g3")["room"]

        self.assertEqual(
            [item["id"] for item in room["rendering_choices"]],
            ["god", "elohim"],
        )
        choice_doors = [
            door for door in room["doors"] if door["kind"] == "rendering-choice"
        ]
        self.assertEqual(
            [door["choice_id"] for door in choice_doors],
            ["god", "elohim"],
        )

    def test_room_exposes_source_and_output_neighbors_separately(self):
        room = open_token_room(self.load(), "reader-demo", "g3")["room"]

        self.assertEqual(room["neighbors"]["source"]["previous"]["token_id"], "g2")
        self.assertEqual(room["neighbors"]["source"]["next"]["token_id"], "g4")
        self.assertEqual(room["neighbors"]["output"]["previous"]["token_id"], "g1")
        self.assertEqual(room["neighbors"]["output"]["next"]["token_id"], "g2")

    def test_room_exposes_declared_relation_doors(self):
        room = open_token_room(self.load(), "reader-demo", "g3")["room"]

        self.assertEqual(len(room["relations"]["outgoing"]), 1)
        relation = room["relations"]["outgoing"][0]
        self.assertEqual(relation["id"], "r-agent-demo")
        self.assertEqual(relation["to"], "g2")
        self.assertEqual(relation["authority"], "demo-relation-only")

        relation_doors = [
            door for door in room["doors"] if door["kind"] == "relation"
        ]
        self.assertEqual(len(relation_doors), 1)
        self.assertEqual(relation_doors[0]["destination_token_id"], "g2")
        self.assertEqual(relation_doors[0]["destination_rendered"], "created")

    def test_opening_relation_destination_reveals_backlink(self):
        room = open_token_room(self.load(), "reader-demo", "g2")["room"]
        incoming_ids = [item["id"] for item in room["relations"]["incoming"]]
        outgoing_ids = [item["id"] for item in room["relations"]["outgoing"]]

        self.assertIn("r-agent-demo", incoming_ids)
        self.assertEqual(outgoing_ids, ["r-heavens-demo", "r-earth-demo"])

    def test_relation_with_unknown_token_fails_closed(self):
        specimen = self.load()
        specimen["relations"][0]["to"] = "missing-token"
        with self.assertRaises(ValueError):
            open_token_room(specimen, "reader-demo", "g3")

    def test_token_not_emitted_by_recipe_fails_closed(self):
        specimen = self.load()
        specimen["recipes"].append(
            {
                "id": "tiny",
                "description": "Only the first token.",
                "mode": "text",
                "field": "surface",
                "separator": " ",
                "sequence": ["g1"],
            }
        )
        with self.assertRaises(ValueError):
            open_token_room(specimen, "tiny", "g3")

    def test_unrelated_relation_does_not_change_room_receipt(self):
        a = self.load()
        b = copy.deepcopy(a)
        b["relations"].append(
            {
                "id": "unrelated-demo",
                "from": "g5",
                "to": "g7",
                "kind": "demo-peer",
                "label": "elsewhere",
                "source": "Revival demonstration relation",
                "authority": "demo-relation-only"
            }
        )

        first = open_token_room(a, "reader-demo", "g3")
        second = open_token_room(b, "reader-demo", "g3")
        self.assertEqual(first["receipt"], second["receipt"])


if __name__ == "__main__":
    unittest.main()
