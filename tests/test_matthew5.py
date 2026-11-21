"""REVIVAL 014: pin all 48 SBLGNT Greek Matthew verses and WITNESS crosswalk."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from revival.kernel.v1 import sha256
from revival.matthew5 import (
    FIXTURE_BLOB, ROOT, UPSTREAM_BLOB, UPSTREAM_COMMIT,
    build_matthew5_world, git_blob_sha1, load_and_build_matthew5,
    load_matthew5,
)
from revival.matthew5_atlas import _safe_json, build_matthew5_html

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "sources/sblgnt-v1.2/Matt.5.txt"
MANIFEST = PROJECT / "sources/sblgnt-v1.2/source.json"


class Matthew5SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = load_matthew5(SOURCE, MANIFEST)
        cls.result = build_matthew5_world(cls.src)

    def test_source_is_pinned_to_exact_upstream_blob_and_cc_by_license(self):
        self.assertEqual(git_blob_sha1(SOURCE.read_bytes()), FIXTURE_BLOB)
        self.assertEqual(self.src["source"]["source_git_blob_sha1"], UPSTREAM_BLOB)
        self.assertEqual(self.src["source"]["source_commit"], UPSTREAM_COMMIT)
        self.assertEqual(self.src["source"]["license"], "CC BY 4.0")
        self.assertIn("creativecommons.org/licenses/by/4.0", self.src["source"]["license_uri"])

    def test_all_forty_eight_verses_in_order_with_greek(self):
        verses = self.src["verses"]
        self.assertEqual(len(verses), 48)
        self.assertEqual([v["verse"] for v in verses], list(range(1, 49)))
        self.assertEqual(verses[0]["locator"], "Matt.5.1")
        self.assertEqual(verses[47]["locator"], "Matt.5.48")
        self.assertIn("Μακάριοι", verses[2]["text"])
        self.assertIn("τέλειοι", verses[47]["text"])

    def test_wordlike_segments_are_exact_substrings_not_normalized_lemmas(self):
        for verse in self.src["verses"]:
            previous = -1
            for token in verse["tokens"]:
                start, end = token["span"]
                self.assertGreater(start, previous)
                self.assertEqual(verse["text"][start:end], token["surface"])
                self.assertEqual(token["linguistic_status"], "unannotated")
                previous = end

    def test_world_places_and_receipts_replay_deterministically(self):
        first = self.result
        second = load_and_build_matthew5(PROJECT)
        self.assertEqual(first, second)
        self.assertEqual(first["world"]["root_address"], ROOT)
        self.assertEqual(first["receipt"]["projection_sha256"], sha256(first["world"]))
        self.assertEqual(len(first["world"]["passages"]), 48)
        self.assertGreater(len(first["world"]["rooms"]), 500)
        self.assertEqual(
            len([p for p in first["world"]["places"] if p["kind"] == "token"]),
            len(first["world"]["rooms"])
        )

    def test_witness_crosswalk_preserves_english_greek_edition_boundary(self):
        p = self.result["world"]["passages"][0]
        self.assertEqual(p["locator"], "Matt.5.1")
        self.assertEqual(p["witness_passage"], "matthew.5.1")
        self.assertNotEqual(self.result["world"]["edition"], "engwebp")
        for room in self.result["world"]["rooms"].values():
            self.assertEqual(room["declared_layers"]["morphology"], "fog")
            self.assertEqual(room["declared_layers"]["translation_alignment"], "fog")

    def test_changing_any_source_byte_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Matt.5.txt"
            path.write_bytes(SOURCE.read_bytes().replace("Ἰδὼν".encode(), "Ἰδων".encode(), 1))
            with self.assertRaisesRegex(ValueError, "fixture was changed"):
                load_matthew5(path, MANIFEST)

    def test_missing_or_reordered_verses_fail_closed(self):
        invalid = deepcopy(self.src)
        invalid["verses"][0]["locator"] = "Matt.5.2"
        with self.assertRaisesRegex(ValueError, "out-of-order"):
            build_matthew5_world(invalid)

    def test_atlas_is_standalone_deterministic_rights_attributed_and_usable_on_phones(self):
        a = build_matthew5_html(self.result)
        b = build_matthew5_html(self.result)
        self.assertEqual(a, b)
        self.assertIn("The Open Word", a)
        self.assertIn("SBL Greek New Testament", a)
        self.assertIn("CC BY 4.0", a)
        self.assertIn("engwebp", a)
        self.assertIn("witness-package", a)
        self.assertIn("crypto.subtle.digest", a)
        self.assertIn("REVIVAL__matthew-5-journey.json", a)
        self.assertIn("viewport", a)
        self.assertIn("0 Deeds", a)
        self.assertIn("wordLayers", a)
        self.assertIn("m5v01-t001", a)
        self.assertNotIn("XMLHttpRequest", a)
        self.assertNotIn("fetch(", a)
        self.assertNotIn("sendBeacon", a)
        self.assertNotIn("innerHTML =", a)
        self.assertIn("textContent", a)

    def test_source_data_embedding_escapes_html_script_boundaries(self):
        payload = _safe_json({
            "attacker": "</script><script>alert(1)</script>",
            "format": "Y&Z\u2028"
        })
        self.assertNotIn("</script>", payload)
        self.assertNotIn("<script>", payload)
        self.assertNotIn("\u2028", payload)
        self.assertIn("\\u003c", payload)
        self.assertIn("\\u0026", payload)

    def test_altered_world_receipt_is_rejected_before_html_build(self):
        changed = deepcopy(self.result)
        changed["world"]["passages"][0]["text"] = "injected replacement"
        with self.assertRaisesRegex(ValueError, "receipt mismatch"):
            build_matthew5_html(changed)


if __name__ == "__main__":
    unittest.main()
