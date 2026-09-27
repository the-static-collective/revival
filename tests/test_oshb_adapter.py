from __future__ import annotations

import copy
import json
from pathlib import Path
import unicodedata
import unittest

from revival.adapters.oshb import ADAPTER_ID, adapt_oshb_verse
from revival.atlas import build_curiosity_atlas_html
from revival.curiosity import open_token_room
from revival.linguistic import compile_linguistic_projection


ROOT = Path(__file__).resolve().parents[1]
SOURCE_XML = ROOT / "sources" / "oshb-v2.2" / "Gen.1.1.xml"
SOURCE_MANIFEST = ROOT / "sources" / "oshb-v2.2" / "source.json"


class OSHBAdapterTests(unittest.TestCase):
    def load(self):
        xml_text = SOURCE_XML.read_text(encoding="utf-8")
        manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        return xml_text, manifest

    def adapt(self):
        xml_text, manifest = self.load()
        return adapt_oshb_verse(xml_text, manifest)

    def test_pinned_real_word_ids_lemma_and_morphology_survive(self):
        specimen = self.adapt()

        self.assertEqual(
            [token["id"] for token in specimen["tokens"]],
            ["01xeN", "01Nvk", "01TyA", "01vuQ", "01TSc", "01k5P", "01nPh"],
        )
        elohim = next(token for token in specimen["tokens"] if token["id"] == "01TyA")
        record = elohim["annotations"]["oshb"]["data"]

        self.assertEqual(elohim["surface"], "אֱלֹהִ֑ים")
        self.assertEqual(record["external_word_id"], "01TyA")
        self.assertEqual(record["lemma"], "430")
        self.assertEqual(record["morph"], "HNcmpa")
        self.assertEqual(record["cantillation_hierarchy"], "1")

    def test_adapter_preserves_unicode_order_without_normalization(self):
        specimen = self.adapt()
        first = specimen["tokens"][0]
        raw = first["annotations"]["oshb"]["data"]["raw_surface"]

        self.assertEqual(raw, "בְּ/רֵאשִׁ֖ית")
        self.assertEqual(first["surface"], raw.replace("/", ""))
        self.assertNotEqual(
            first["surface"],
            unicodedata.normalize("NFC", first["surface"]),
        )

    def test_adapter_derivation_rules_are_visible_in_witness_identity(self):
        specimen = self.adapt()
        note = specimen["witness"]["source_note"]
        receipt = specimen["source_backing"]["adapter_receipt"]

        self.assertEqual(specimen["witness"]["id"], "oshb-v2.2:Gen.1.1")
        self.assertEqual(specimen["witness"]["locator"], "Gen.1.1")
        self.assertIn("unicode_normalization=none", note)
        self.assertIn("6a5db284c715c18b239422e57bb89684e6a19f00", note)
        self.assertIn("dcc8be362134981d3054e9b64d3a465d08492a33", note)
        self.assertEqual(receipt["adapter"], ADAPTER_ID)
        self.assertEqual(receipt["unicode_normalization"], "none")

    def test_sof_pasuq_is_preserved_as_declared_segment(self):
        specimen = self.adapt()
        last = specimen["tokens"][-1]
        record = last["annotations"]["oshb"]["data"]

        self.assertEqual(last["surface"], "הָאָֽרֶץ׃")
        self.assertEqual(
            record["trailing_segments"],
            [{"type": "x-sof-pasuq", "surface": "׃"}],
        )

    def test_real_food_compiles_through_existing_linguistic_engine(self):
        specimen = self.adapt()
        compiled = compile_linguistic_projection(specimen, "unpointed")

        self.assertEqual(
            compiled["projection"]["content"]["text"],
            "בראשית ברא אלהים את השמים ואת הארץ׃",
        )
        self.assertEqual(
            compiled["projection"]["content"]["trace"][2]["token_id"],
            "01TyA",
        )

    def test_real_oshb_record_reaches_curiosity_room(self):
        specimen = self.adapt()
        room = open_token_room(specimen, "surface", "01TyA")["room"]
        record = room["token"]["annotations"]["oshb"]

        self.assertEqual(room["token"]["source_surface"], "אֱלֹהִ֑ים")
        self.assertEqual(record["data"]["lemma"], "430")
        self.assertEqual(record["data"]["morph"], "HNcmpa")
        self.assertEqual(
            record["authority"],
            "Open Scriptures Hebrew Bible v2.2 linguistic annotation",
        )

    def test_real_food_builds_walkable_atlas(self):
        specimen = self.adapt()
        result, html = build_curiosity_atlas_html(specimen, "surface")

        self.assertEqual(result["atlas"]["witness_locator"], "Gen.1.1")
        self.assertIn("01TyA", result["atlas"]["rooms"])
        self.assertIn("HNcmpa", html)
        self.assertIn("Declared layers", html)

    def test_fixture_hash_mismatch_fails_closed(self):
        xml_text, manifest = self.load()
        changed = copy.deepcopy(manifest)
        changed["fixture_sha256"] = "0" * 64

        with self.assertRaises(ValueError):
            adapt_oshb_verse(xml_text, changed)


if __name__ == "__main__":
    unittest.main()
