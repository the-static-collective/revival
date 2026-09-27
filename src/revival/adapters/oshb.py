"""Open Scriptures Hebrew Bible (OSHB) OSIS adapter.

This adapter is deliberately outside the frozen Revival kernel. It converts one
pinned OSIS verse into a source-backed Revival linguistic specimen while
preserving OSHB word ids, lemma/morphology attributes, raw word surfaces,
segment records, licensing metadata, and an adapter receipt.

No Unicode normalization is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

from ..kernel.v1 import sha256


ADAPTER_ID = "oshb-osis-v1"


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _raw_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_manifest(manifest: dict[str, Any]) -> None:
    required = (
        "source_id",
        "project",
        "version",
        "osis_id",
        "upstream_repository",
        "upstream_ref",
        "upstream_commit",
        "upstream_path",
        "upstream_blob_sha",
        "fixture_sha256",
        "license",
    )
    missing = [key for key in required if key not in manifest]
    if missing:
        raise ValueError(
            "OSHB source manifest missing required fields: " + ", ".join(missing)
        )

    license_data = manifest["license"]
    if not isinstance(license_data, dict):
        raise ValueError("OSHB source manifest license must be an object")
    for key in ("text", "annotations", "attribution"):
        if not license_data.get(key):
            raise ValueError(f"OSHB source manifest license requires {key!r}")


def adapt_oshb_verse(
    xml_text: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Adapt one pinned OSHB OSIS verse into a Revival specimen."""
    _validate_manifest(manifest)

    fixture_sha = _raw_sha256(xml_text)
    if fixture_sha != manifest["fixture_sha256"]:
        raise ValueError(
            "OSHB fixture SHA-256 mismatch: "
            f"expected {manifest['fixture_sha256']}, got {fixture_sha}"
        )

    root = ET.fromstring(xml_text)
    verse = None
    for candidate in root.iter():
        if (
            _localname(candidate.tag) == "verse"
            and candidate.attrib.get("osisID") == manifest["osis_id"]
        ):
            verse = candidate
            break
    if verse is None:
        raise ValueError(
            f"OSHB fixture does not contain verse {manifest['osis_id']!r}"
        )

    tokens: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []
    seen_word_ids: set[str] = set()

    for child in list(verse):
        kind = _localname(child.tag)

        if kind == "w":
            word_id = child.attrib.get("id")
            lemma = child.attrib.get("lemma")
            morph = child.attrib.get("morph")
            raw_surface = "".join(child.itertext())

            if not word_id or not lemma or not morph:
                raise ValueError(
                    "OSHB word requires id, lemma, and morph attributes"
                )
            if word_id in seen_word_ids:
                raise ValueError(f"duplicate OSHB word id: {word_id}")
            if not raw_surface:
                raise ValueError(f"OSHB word {word_id} has empty surface")
            seen_word_ids.add(word_id)

            # OSHB uses literal slash characters to expose morpheme boundaries.
            # Removing those slashes is an explicit adapter projection; all
            # other Unicode code points are preserved in their parsed order.
            display_surface = raw_surface.replace("/", "")

            tokens.append(
                {
                    # Preserve OSHB's immutable external id as Revival's token id.
                    "id": word_id,
                    "surface": display_surface,
                    "annotations": {
                        "oshb": {
                            "kind": "source-linguistic-record",
                            "source": manifest["source_id"],
                            "authority": (
                                f"{manifest['project']} v{manifest['version']} "
                                "linguistic annotation"
                            ),
                            "license": manifest["license"]["annotations"],
                            "data": {
                                "external_word_id": word_id,
                                "lemma": lemma,
                                "morph": morph,
                                "cantillation_hierarchy": child.attrib.get("n"),
                                "raw_surface": raw_surface,
                                "morpheme_surfaces": raw_surface.split("/"),
                                "trailing_segments": [],
                            },
                        }
                    },
                }
            )
            continue

        if kind == "seg":
            if not tokens:
                raise ValueError("OSHB segment appears before any word")
            segment_text = "".join(child.itertext())
            if not segment_text:
                raise ValueError("OSHB segment has empty surface")

            token = tokens[-1]
            token["surface"] += segment_text
            token["annotations"]["oshb"]["data"]["trailing_segments"].append(
                {
                    "type": child.attrib.get("type"),
                    "surface": segment_text,
                }
            )
            continue

        if kind == "note":
            notes.append(
                {
                    "attributes": dict(child.attrib),
                    "text": "".join(child.itertext()),
                }
            )
            continue

        raise ValueError(f"unsupported OSHB verse child element: {kind}")

    if not tokens:
        raise ValueError("OSHB verse contains no word elements")

    witness_text = " ".join(token["surface"] for token in tokens)
    source_note = (
        f"{manifest['source_id']} | upstream={manifest['upstream_repository']} "
        f"ref={manifest['upstream_ref']} commit={manifest['upstream_commit']} "
        f"path={manifest['upstream_path']} blob={manifest['upstream_blob_sha']} "
        f"fixture_sha256={fixture_sha} adapter={ADAPTER_ID} "
        "unicode_normalization=none; word '/' morpheme markers removed; "
        "OSIS seg text attached to preceding word; U+0020 inserted between words."
    )

    core = {
        "witness": {
            "id": manifest["source_id"],
            "locator": manifest["osis_id"],
            "language": "he",
            "script": "Hebr",
            "text": witness_text,
            "source_note": source_note,
        },
        "tokens": tokens,
        "recipes": [
            {
                "id": "surface",
                "description": (
                    "OSHB-backed word surfaces after declared adapter handling "
                    "of morpheme slashes and OSIS segment text."
                ),
                "mode": "text",
                "field": "surface",
                "separator": " ",
            },
            {
                "id": "unpointed",
                "description": (
                    "Mechanical projection of the OSHB-backed surface with "
                    "Unicode combining marks removed."
                ),
                "mode": "text",
                "field": "unpointed",
                "separator": " ",
            },
        ],
        "relations": [],
    }

    adapter_receipt = {
        "adapter": ADAPTER_ID,
        "input_fixture_sha256": fixture_sha,
        "upstream_ref": manifest["upstream_ref"],
        "upstream_commit": manifest["upstream_commit"],
        "upstream_path": manifest["upstream_path"],
        "upstream_blob_sha": manifest["upstream_blob_sha"],
        "osis_id": manifest["osis_id"],
        "unicode_normalization": "none",
        "derived_core_sha256": sha256(core),
    }

    return {
        **core,
        "source_backing": {
            "manifest": manifest,
            "adapter_receipt": adapter_receipt,
            "verse_notes": notes,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.adapters.oshb",
        description="Adapt one pinned OSHB OSIS verse into a Revival specimen.",
    )
    parser.add_argument("source_xml", type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    xml_text = args.source_xml.read_text(encoding="utf-8")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    specimen = adapt_oshb_verse(xml_text, manifest)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(specimen, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "witness": specimen["witness"]["id"],
                "locator": specimen["witness"]["locator"],
                "tokens": len(specimen["tokens"]),
                "adapter_receipt": specimen["source_backing"]["adapter_receipt"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
