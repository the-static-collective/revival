from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from revival.jubilee_door import build_door, pinned_inputs, resolve_candidate, write_bundle, SOURCE_PIN
from revival.kernel.v1 import sha256

ROOT = Path(__file__).resolve().parents[1]


class JubileeDoorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = build_door(ROOT)

    def candidate(self, **updates):
        return {"id": "tree-tag", "reference": "Gen.1.1", "public": True, "withdrawn": False, **updates}

    def test_verified_address_is_an_actual_passage_in_the_built_world(self):
        result = resolve_candidate(self.candidate(), self.bundle)
        self.assertEqual(result["status"], "RESOLVE_CANDIDATE")
        self.assertEqual(result["revivalAddress"], self.bundle["manifest"]["revivalAddress"])
        self.assertEqual(result["effect"], "NONE")
        self.assertEqual(result["authority"], "NONE")

    def test_luke_theme_cannot_be_remapped_to_genesis(self):
        result = resolve_candidate(self.candidate(reference="Luke.4.18"), self.bundle)
        self.assertEqual(result["status"], "HOLD_UNRESOLVED")
        self.assertIsNone(result["revivalAddress"])

    def test_private_or_withdrawn_tags_cannot_navigate(self):
        for update in ({"public": False}, {"withdrawn": True}):
            result = resolve_candidate(self.candidate(**update), self.bundle)
            self.assertEqual(result["status"], "REFUSED")
            self.assertIsNone(result["artifactSha256"])

    def test_lookup_requires_exact_reference_and_typed_flags(self):
        self.assertEqual(resolve_candidate(self.candidate(reference="Genesis 1:1"), self.bundle)["status"], "HOLD_UNRESOLVED")
        with self.assertRaises(ValueError):
            resolve_candidate(self.candidate(public="true"), self.bundle)

    def test_household_or_event_data_is_outside_candidate_schema(self):
        with self.assertRaises(ValueError):
            resolve_candidate(self.candidate(child_name="not allowed"), self.bundle)

    def test_world_html_or_manifest_tamper_refuses(self):
        for target in ("html", "manifest", "world"):
            bundle = deepcopy(self.bundle)
            if target == "html":
                bundle["html"] += "changed"
            elif target == "manifest":
                bundle["manifest"]["revivalAddress"] += "/invented"
            else:
                bundle["world"]["receipt"]["projection_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "integrity"):
                resolve_candidate(self.candidate(), bundle)

    def test_rehashed_forged_address_still_refuses(self):
        bundle = deepcopy(self.bundle)
        bundle["manifest"]["revivalAddress"] += "/invented"
        core = {k: v for k, v in bundle["manifest"].items() if k != "artifactSha256"}
        bundle["manifest"]["artifactSha256"] = sha256(core)
        with self.assertRaisesRegex(ValueError, "built world"):
            resolve_candidate(self.candidate(), bundle)

    def test_rehashed_license_removal_does_not_impersonate_an_owner_artifact(self):
        bundle = deepcopy(self.bundle)
        bundle["manifest"]["licenses"] = []
        core = {k: v for k, v in bundle["manifest"].items() if k != "artifactSha256"}
        bundle["manifest"]["artifactSha256"] = sha256(core)
        with self.assertRaisesRegex(ValueError, "pinned owner"):
            resolve_candidate(self.candidate(), bundle)

    def test_cold_rebuild_is_identical_and_preserves_licenses(self):
        self.assertEqual(self.bundle, build_door(ROOT))
        self.assertEqual(len(self.bundle["manifest"]["licenses"]), 2)
        self.assertIn("CC BY 4.0", str(self.bundle["manifest"]["licenses"]))
        self.assertEqual(self.bundle["manifest"]["producer"]["sourceCommit"], SOURCE_PIN)

    def test_unavailable_source_and_mutated_local_inputs_refuse(self):
        with self.assertRaises(ValueError):
            build_door(ROOT, "Isaiah.61")
        with self.assertRaises(ValueError):
            pinned_inputs(ROOT, "main")
        original = Path.read_bytes
        def changed(path):
            content = original(path)
            return content + b"changed" if str(path).endswith("Gen.1.1.xml") else content
        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "Pinned input mismatch"):
                build_door(ROOT)

    def test_output_does_not_overwrite_and_contains_the_exact_world(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "door"
            write_bundle(self.bundle, directory)
            self.assertEqual((directory / "genesis-world.html").read_text(), self.bundle["html"])
            with self.assertRaises(FileExistsError):
                write_bundle(self.bundle, directory)


if __name__ == "__main__":
    unittest.main()
