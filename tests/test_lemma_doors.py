from __future__ import annotations

import copy
from pathlib import Path
import unittest

from revival.corpus import (
    build_corpus,
    lemma_occurrences,
    load_corpus_manifest,
    open_corpus_token_room,
)
from revival.corpus_atlas import build_corpus_atlas_html


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "oshb-v2.2-genesis-opening.json"


class LemmaDoorTests(unittest.TestCase):
    def load(self):
        return load_corpus_manifest(CORPUS, root=ROOT)

    def test_corpus_contains_three_pinned_witnesses(self):
        corpus = self.load()
        self.assertEqual(
            [item["locator"] for item in corpus["witnesses"]],
            ["Gen.1.1", "Gen.1.2", "Gen.1.3"],
        )

    def test_exact_lemma_430_indexes_real_cross_verse_occurrences(self):
        corpus = self.load()
        occurrences = lemma_occurrences(corpus, "430")

        self.assertEqual(
            [(item["locator"], item["token_id"]) for item in occurrences],
            [
                ("Gen.1.1", "01TyA"),
                ("Gen.1.2", "01x9c"),
                ("Gen.1.3", "01JM7"),
            ],
        )
        self.assertTrue(all(item["morph"] == "HNcmpa" for item in occurrences))

    def test_genesis_1_1_elohim_opens_two_dangerous_lemma_doors(self):
        corpus = self.load()
        room = open_corpus_token_room(corpus, "Gen.1.1", "01TyA")["room"]

        self.assertEqual(room["lemma"]["value"], "430")
        self.assertEqual(
            room["lemma"]["identity_rule"],
            "exact declared annotation string equality",
        )
        self.assertEqual(
            [
                (door["destination_locator"], door["destination_token_id"])
                for door in room["corpus_doors"]
            ],
            [
                ("Gen.1.2", "01x9c"),
                ("Gen.1.3", "01JM7"),
            ],
        )

    def test_destination_room_has_backlinks_through_same_index(self):
        corpus = self.load()
        room = open_corpus_token_room(corpus, "Gen.1.2", "01x9c")["room"]

        self.assertEqual(
            [
                (door["destination_locator"], door["destination_token_id"])
                for door in room["corpus_doors"]
            ],
            [
                ("Gen.1.1", "01TyA"),
                ("Gen.1.3", "01JM7"),
            ],
        )

    def test_prefixed_lemma_strings_are_not_silently_collapsed(self):
        corpus = self.load()

        plain = lemma_occurrences(corpus, "d/776")
        prefixed = lemma_occurrences(corpus, "c/d/776")

        self.assertEqual(
            [(item["locator"], item["token_id"]) for item in plain],
            [("Gen.1.1", "01nPh")],
        )
        self.assertEqual(
            [(item["locator"], item["token_id"]) for item in prefixed],
            [("Gen.1.2", "01LN3")],
        )

    def test_corpus_identity_changes_when_one_source_backed_witness_changes(self):
        corpus = self.load()
        specimens = [
            copy.deepcopy(corpus["_specimens_by_locator"][locator])
            for locator in ("Gen.1.1", "Gen.1.2", "Gen.1.3")
        ]
        specimens[1]["witness"]["source_note"] += " changed"

        changed = build_corpus(
            corpus["id"],
            specimens,
            recipe_id=corpus["recipe_id"],
            description=corpus["description"],
        )
        self.assertNotEqual(corpus["corpus_sha256"], changed["corpus_sha256"])

    def test_corpus_room_receipt_keeps_local_and_corpus_identity_distinct(self):
        corpus = self.load()
        opened = open_corpus_token_room(corpus, "Gen.1.1", "01TyA")
        receipt = opened["corpus_receipt"]

        self.assertEqual(receipt["corpus_sha256"], corpus["corpus_sha256"])
        self.assertEqual(receipt["local_locator"], "Gen.1.1")
        self.assertEqual(receipt["local_token_id"], "01TyA")
        self.assertIn("local_witness_sha256", receipt)
        self.assertIn("lemma_occurrences_sha256", receipt)

    def test_multi_verse_atlas_makes_lemma_doors_walkable(self):
        corpus = self.load()
        result, html = build_corpus_atlas_html(corpus)

        self.assertEqual(len(result["atlas"]["verses"]), 3)
        self.assertIn("Gen.1.1::01TyA", result["atlas"]["rooms"])
        self.assertIn("Gen.1.2::01x9c", result["atlas"]["rooms"])
        self.assertIn("Gen.1.3::01JM7", result["atlas"]["rooms"])
        self.assertIn("Dangerous Lemma Doors", html)
        self.assertIn("01x9c", html)
        self.assertIn("01JM7", html)
        self.assertEqual(
            result["receipt"]["corpus_sha256"],
            corpus["corpus_sha256"],
        )

    def test_corpus_atlas_html_is_deterministic(self):
        corpus = self.load()
        first_result, first_html = build_corpus_atlas_html(corpus)
        second_result, second_html = build_corpus_atlas_html(corpus)

        self.assertEqual(first_result, second_result)
        self.assertEqual(first_html, second_html)


if __name__ == "__main__":
    unittest.main()
