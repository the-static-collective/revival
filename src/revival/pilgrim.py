"""Revival 013: a deterministic first-visit pilgrim door through the existing world.

This module adds no Scripture data and no semantic claims. It composes already
earned 012 places into a short route whose every stop is an existing address.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .earned_names import build_earned_names_world, load_lexical_proof
from .kernel.v1 import sha256
from .object_relations import load_object_relation_instrument


def build_pilgrim_route(world_result: dict[str, Any]) -> dict[str, Any]:
    world = world_result["world"]
    elohim = world["lexemes"].get("430")
    if elohim is None or len(elohim["occurrence_anchor_addresses"]) < 2:
        raise ValueError("pilgrim route requires at least two attributed H430 occurrences")

    first_anchor, second_anchor = elohim["occurrence_anchor_addresses"][:2]
    places = {place["address"]: place for place in world["places"]}
    first_token = places[first_anchor]["token_address"]
    second_token = places[second_anchor]["token_address"]

    steps = [
        {
            "kind": "source-room",
            "address": first_token,
            "invitation": "Begin with one exact source-backed occurrence.",
            "claim_boundary": "source room != interpretation",
        },
        {
            "kind": "earned-lexeme",
            "address": elohim["address"],
            "invitation": "Open the attributed lexical identity behind this occurrence.",
            "claim_boundary": "lexeme != sense != referent",
        },
        {
            "kind": "occurrence-anchor",
            "address": second_anchor,
            "invitation": "Follow the same earned lexeme into another witnessed passage.",
            "claim_boundary": "same lexeme != same meaning",
        },
        {
            "kind": "source-room",
            "address": second_token,
            "invitation": "Descend again to the exact destination token and inspect its layers.",
            "claim_boundary": "navigation != theology",
        },
    ]

    missing = [step["address"] for step in steps if step["address"] not in places]
    if missing:
        raise ValueError(f"pilgrim route contains unknown world addresses: {missing!r}")

    core = {
        "kind": "revival-pilgrim-route",
        "version": "013",
        "title": "One word, another room",
        "purpose": (
            "A bounded first-visit route demonstrating source -> attributed lexeme "
            "-> cross-passage occurrence -> source without inventing a new relation."
        ),
        "steps": steps,
        "law": [
            "route != source",
            "navigation != theology",
            "same lexeme != same meaning",
            "reader path != Scripture",
        ],
        "world_projection_sha256": world_result["receipt"]["projection_sha256"],
    }
    return {**core, "route_sha256": sha256(core)}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.pilgrim",
        description="Build Revival 013's bounded first-visit route.",
    )
    parser.add_argument("corpus_manifest", type=Path)
    parser.add_argument("--macula-xml", required=True, type=Path)
    parser.add_argument("--macula-manifest", required=True, type=Path)
    parser.add_argument("--lexical-proof", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    corpus, instrument = load_object_relation_instrument(
        args.corpus_manifest,
        args.macula_xml,
        args.macula_manifest,
        root=args.root,
    )
    proof = load_lexical_proof(args.lexical_proof)
    world = build_earned_names_world(corpus, instrument, proof)
    route = build_pilgrim_route(world)
    print(json.dumps(
        route,
        ensure_ascii=False,
        sort_keys=True,
        indent=2 if args.pretty else None,
        separators=None if args.pretty else (",", ":"),
    ))


if __name__ == "__main__":
    main()
