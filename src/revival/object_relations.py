"""Object-relation instrument composed from OSHB + pinned MACULA syntax."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .adapters.macula import adapt_macula_object_relations
from .aleph_tav import build_aleph_tav_instrument
from .corpus import load_corpus_manifest, open_corpus_token_room
from .kernel.v1 import sha256


def build_object_relation_instrument(
    corpus: dict[str, Any],
    macula_layer: dict[str, Any],
) -> dict[str, Any]:
    """Attach attributable syntax/frame relations to Aleph-Tav occurrences."""
    aleph_tav = build_aleph_tav_instrument(corpus)
    by_marker = {
        relation["marker"]["oshb_token_id"]: relation
        for relation in macula_layer["relations"]
    }

    enriched: list[dict[str, Any]] = []
    for occurrence in aleph_tav["occurrences"]:
        relation = by_marker.get(occurrence["token_id"])
        enriched.append(
            {
                **occurrence,
                "object_relation": relation,
                "relation_status": (
                    "attributable-macula-relation"
                    if relation is not None
                    else "no-macula-relation-in-proof-layer"
                ),
            }
        )

    matched_marker_ids = {
        item["token_id"]
        for item in enriched
        if item["object_relation"] is not None
    }
    layer_marker_ids = set(by_marker)
    if matched_marker_ids != layer_marker_ids:
        raise ValueError(
            "MACULA object-marker relations do not exactly match the "
            "Aleph-Tav proof occurrences"
        )

    core = {
        "kind": "object-relation-instrument",
        "corpus_id": corpus["id"],
        "corpus_sha256": corpus["corpus_sha256"],
        "aleph_tav_family_id": aleph_tav["family_id"],
        "aleph_tav_family_sha256": aleph_tav["family_sha256"],
        "macula_source_id": macula_layer["source_id"],
        "macula_layer_sha256": macula_layer["adapter_receipt"]["layer_sha256"],
        "occurrences": enriched,
        "law": {
            "syntax_tree": (
                "MACULA clause/object/marker-phrase structure is preserved "
                "as syntax evidence."
            ),
            "semantic_frame": (
                "MACULA verb A1 frame targets are preserved separately as "
                "semantic-frame evidence."
            ),
            "no_adjacency_substitute": (
                "Revival 009 object relations do not use immediate-next-token "
                "adjacency as the object-phrase claim."
            ),
        },
    }
    return {
        **core,
        "instrument_sha256": sha256(core),
    }


def open_object_relation_room(
    corpus: dict[str, Any],
    instrument: dict[str, Any],
    locator: str,
    token_id: str,
) -> dict[str, Any]:
    occurrence = next(
        (
            item for item in instrument["occurrences"]
            if item["locator"] == locator
            and item["token_id"] == token_id
        ),
        None,
    )
    if occurrence is None:
        raise ValueError(f"unknown object-relation occurrence: {locator} {token_id}")

    relation = occurrence.get("object_relation")
    if relation is None:
        raise ValueError(
            f"no attributable MACULA object relation for {locator} {token_id}"
        )

    verb_id = relation["governing_verb"]["oshb_token_id"]
    phrase_ids = relation["marked_phrase"]["oshb_token_ids"]
    a1_ids = [
        item["oshb_token_id"]
        for item in relation["semantic_frame_evidence"]["matched_heads"]
    ]

    doors = [
        {
            "kind": "governing-verb",
            "label": "governing verb",
            "destination_locator": locator,
            "destination_token_id": verb_id,
            "source": relation["syntax_evidence"]["source"],
            "evidence_layer": "syntax + clause role",
        }
    ]
    doors.extend(
        {
            "kind": "marked-phrase-token",
            "label": "marked object phrase",
            "destination_locator": locator,
            "destination_token_id": object_id,
            "source": relation["syntax_evidence"]["source"],
            "evidence_layer": "syntax tree",
        }
        for object_id in phrase_ids
    )
    doors.extend(
        {
            "kind": "semantic-a1-head",
            "label": "A1 object head",
            "destination_locator": locator,
            "destination_token_id": object_id,
            "source": relation["semantic_frame_evidence"]["source"],
            "evidence_layer": "semantic frame",
        }
        for object_id in a1_ids
    )

    local_room = open_corpus_token_room(corpus, locator, token_id)
    room = {
        "kind": "object-relation-room",
        "local_token_room": local_room["room"],
        "occurrence": occurrence,
        "object_relation": relation,
        "doors": doors,
        "evidence_separation": {
            "syntax_evidence": relation["syntax_evidence"],
            "semantic_frame_evidence": relation["semantic_frame_evidence"],
        },
    }
    receipt = {
        "kind": "object-relation-room",
        "instrument_sha256": instrument["instrument_sha256"],
        "local_room_projection_sha256": (
            local_room["corpus_receipt"]["projection_sha256"]
        ),
        "macula_relation_sha256": sha256(relation),
        "projection_sha256": sha256(room),
    }
    return {
        "room": room,
        "local_room_receipt": local_room["local_room_receipt"],
        "corpus_room_receipt": local_room["corpus_receipt"],
        "receipt": receipt,
    }


def load_object_relation_instrument(
    corpus_manifest: Path,
    macula_xml: Path,
    macula_manifest: Path,
    *,
    root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    base = (root or Path.cwd()).resolve()
    corpus = load_corpus_manifest(corpus_manifest, root=base)

    manifest = json.loads(macula_manifest.read_text(encoding="utf-8"))
    locator = "Gen.1.1"
    specimen = corpus["_specimens_by_locator"].get(locator)
    if specimen is None:
        raise ValueError("object-relation proof corpus requires Gen.1.1")

    layer = adapt_macula_object_relations(
        macula_xml.read_text(encoding="utf-8"),
        manifest,
        specimen,
    )
    return corpus, build_object_relation_instrument(corpus, layer)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.object_relations",
        description="Inspect source-backed Aleph-Tav object relations.",
    )
    parser.add_argument("corpus_manifest", type=Path)
    parser.add_argument("--macula-xml", required=True, type=Path)
    parser.add_argument("--macula-manifest", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--locator")
    parser.add_argument("--token")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    corpus, instrument = load_object_relation_instrument(
        args.corpus_manifest,
        args.macula_xml,
        args.macula_manifest,
        root=args.root,
    )

    if args.locator or args.token:
        if not args.locator or not args.token:
            parser.error("--locator and --token must be supplied together")
        result: Any = open_object_relation_room(
            corpus,
            instrument,
            args.locator,
            args.token,
        )
    else:
        result = instrument

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            indent=2 if args.pretty else None,
            separators=None if args.pretty else (",", ":"),
        )
    )


if __name__ == "__main__":
    main()
