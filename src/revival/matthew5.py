"""REVIVAL 014: deterministic source-backed Matthew 5 from pinned SBLGNT v1.2.

This is an edition-level source witness, not an original Greek manuscript or
an interpretation. Spans are whitespace-delimited *display units*, not earned
morphology, syntax, Strong's numbers, lemmas or scholarly word alignments.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .kernel.v1 import sha256

VERSE = re.compile(r"^Matt 5:(\d+)\t(.*)$")
WORDLIKE = re.compile(r"\S+")
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
UPSTREAM_COMMIT = "d7f35adca9ec410e1d1499c63b4dd989d76c8d4d"
UPSTREAM_BLOB = "d19efbdff018c2bde83ba0fc01e0d8cb399b496b"
FIXTURE_BLOB = "c30d2837313e1a47ec04c348f466b763f5ad7477"
ROOT = "revival://sblgnt-v1.2-matthew-5"


def git_blob_sha1(blob: bytes) -> str:
    """Git blob's content identity (SHA-1 for the pinned upstream repository)."""
    return hashlib.sha1(f"blob {len(blob)}\0".encode("ascii") + blob).hexdigest()


def load_matthew5(
    source: Path, manifest_file: Path,
) -> dict[str, Any]:
    """Read exact UTF-8 fixture bytes; fail on unseen edits or edition drift."""
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    keys = {
        "edition_id": "sblgnt-v1.2",
        "source_commit": UPSTREAM_COMMIT,
        "source_git_blob_sha1": UPSTREAM_BLOB,
        "fixture_git_blob_sha1": FIXTURE_BLOB,
        "license_uri": LICENSE,
        "verses": 48,
    }
    for key, value in keys.items():
        if manifest.get(key) != value:
            raise ValueError(f"SBLGNT provenance mismatch: {key}")
    if manifest.get("fixture_file") != "Matt.5.txt":
        raise ValueError("manifest points outside pinned SBLGNT fixture")
    raw = source.read_bytes()
    if git_blob_sha1(raw) != FIXTURE_BLOB:
        raise ValueError("SBLGNT Matthew 5 fixture was changed")
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise ValueError("fixture line delimiters changed")
    lines = raw.decode("utf-8").splitlines()
    if len(lines) != 48:
        raise ValueError("Matthew 5 requires exactly 48 verse lines")
    verses: list[dict[str, Any]] = []
    for expected_verse, line in enumerate(lines, start=1):
        match = VERSE.fullmatch(line)
        if not match or int(match.group(1)) != expected_verse:
            raise ValueError(f"invalid or out-of-order Matthew 5 verse {expected_verse}")
        displayed = match.group(2)
        if not displayed.strip():
            raise ValueError(f"empty verse: {expected_verse}")
        pieces = []
        for index, token in enumerate(WORDLIKE.finditer(displayed), start=1):
            surface = token.group()
            pieces.append({
                "id": f"m5v{expected_verse:02d}-t{index:03d}",
                "surface": surface,
                "span": [token.start(), token.end()],
                "epistemic_status": "source-backed-edition-orthography",
                "linguistic_status": "unannotated",
            })
            if displayed[token.start():token.end()] != surface:
                raise ValueError("SBLGNT token slice detached from source")
        verses.append({
            "locator": f"Matt.5.{expected_verse}",
            "witness_passage": f"matthew.5.{expected_verse}",
            "verse": expected_verse,
            "text": displayed,
            "tokens": pieces,
            "line_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
        })
    return {
        "edition_id": "sblgnt-v1.2",
        "source": {
            "source_commit": UPSTREAM_COMMIT,
            "source_git_blob_sha1": UPSTREAM_BLOB,
            "source_file": manifest["source_file"],
            "source_exact_url": manifest["source_exact_url"],
            "fixture_git_blob_sha1": FIXTURE_BLOB,
            "fixture_sha256": hashlib.sha256(raw).hexdigest(),
            "license": "CC BY 4.0",
            "license_uri": LICENSE,
            "rights_holder": manifest["rights_holder"],
            "modifications": manifest["modifications"],
        },
        "verses": verses,
    }


def build_matthew5_world(source: dict[str, Any]) -> dict[str, Any]:
    if source.get("edition_id") != "sblgnt-v1.2":
        raise ValueError("unsupported Greek textual edition")
    verses = source.get("verses")
    if not isinstance(verses, list) or len(verses) != 48:
        raise ValueError("Matthew 5 must contain 48 source-backed verses")
    places: list[dict[str, Any]] = [
        {
            "address": ROOT,
            "kind": "world",
            "parent": None,
            "label": "SBLGNT Matthew 5",
            "authority": "REVIVAL derived address",
        },
        {
            "address": ROOT + "/chapter/Matt.5",
            "kind": "chapter",
            "parent": ROOT,
            "label": "Matt.5",
            "authority": "REVIVAL navigation only",
        },
    ]
    rooms = {}
    passages = []
    for expected, verse in enumerate(verses, start=1):
        if verse["locator"] != f"Matt.5.{expected}":
            raise ValueError("out-of-order source verse")
        chapter = ROOT + "/chapter/Matt.5"
        address = chapter + f"/passage/{verse['locator']}"
        places.append({
            "address": address,
            "kind": "passage",
            "label": verse["locator"],
            "parent": chapter,
            "authority": "SBLGNT v1.2 edited Greek NT verse",
            "epistemic_status": "source-backed-edition",
        })
        tokens = verse["tokens"]
        for position, token in enumerate(tokens):
            tid = token["id"]
            if verse["text"][token["span"][0]:token["span"][1]] != token["surface"]:
                raise ValueError("Greek source span no longer matches exact edition")
            word_address = address + f"/token/{tid}"
            places.append({
                "address": word_address,
                "kind": "token",
                "label": token["surface"],
                "parent": address,
                "epistemic_status": "source-backed-edition-orthography",
                "authority": "whitespace display unit; not a lexeme",
            })
            rooms[word_address] = {
                "address": word_address,
                "locator": verse["locator"],
                "token_id": tid,
                "surface": token["surface"],
                "span": token["span"],
                "neighbors": {
                    "previous": address + "/token/" + tokens[position - 1]["id"] if position else None,
                    "next": address + "/token/" + tokens[position + 1]["id"] if position + 1 < len(tokens) else None,
                },
                "declared_layers": {
                    "edition_surface": "source-backed",
                    "display_segment": "derived whitespace split",
                    "lemma": "fog",
                    "morphology": "fog",
                    "syntax": "fog",
                    "translation_alignment": "fog",
                    "theology": "fog",
                },
            }
        passages.append({
            "locator": verse["locator"],
            "witness_passage": verse["witness_passage"],
            "address": address,
            "text": verse["text"],
            "line_sha256": verse["line_sha256"],
            "token_addresses": [address + "/token/" + t["id"] for t in tokens],
        })
    core = {
        "schema": "static-collective.revival.sblgnt-matthew5.v1",
        "edition": source["edition_id"],
        "root_address": ROOT,
        "source": source["source"],
        "passages": passages,
        "places": places,
        "rooms": rooms,
        "boundary": [
            "Edited SBLGNT edition != extant ancient manuscript",
            "Whitespace segment != scholarly token or lexeme",
            "No Greek morphology, syntax or English-Greek word alignment imported",
            "Same verse number in WEB and SBLGNT != same text edition",
            "Recording ID or checksum != verified speaker or accuracy",
            "REVIVAL projection != source witness; game != Scripture",
        ],
    }
    return {
        "world": core,
        "receipt": {
            "kind": "revival-014-sblgnt-matthew5",
            "source_fixture_sha256": source["source"]["fixture_sha256"],
            "places_sha256": sha256(places),
            "rooms_sha256": sha256(rooms),
            "projection_sha256": sha256(core),
        },
    }


def load_and_build_matthew5(root: Path) -> dict[str, Any]:
    directory = root / "sources" / "sblgnt-v1.2"
    return build_matthew5_world(
        load_matthew5(directory / "Matt.5.txt", directory / "source.json")
    )
