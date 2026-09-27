"""Executable source-backed curiosity rooms for Revival.

A curiosity room is a replayable inspection projection around one source token.
It composes the current linguistic projection, available rendering choices,
source/output neighbors, and explicitly declared token relations without
promoting any of those descendants into witness authority.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .kernel.v1 import Delta, Projection, Transform, make_receipt
from .linguistic import (
    _anchor_tokens,
    _witness_from_payload,
    compile_linguistic_projection,
    list_choices,
)


def _declared_relations(
    specimen: dict[str, Any],
    *,
    known_token_ids: set[str],
) -> list[dict[str, Any]]:
    relations = specimen.get("relations", [])
    if not isinstance(relations, list):
        raise ValueError("relations must be a list")

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, relation in enumerate(relations):
        if not isinstance(relation, dict):
            raise ValueError(f"relation {index} must be an object")
        relation_id = relation.get("id")
        source_token = relation.get("from")
        target_token = relation.get("to")
        kind = relation.get("kind")
        authority = relation.get("authority")

        if not isinstance(relation_id, str) or not relation_id:
            raise ValueError(f"relation {index} requires id")
        if relation_id in seen:
            raise ValueError(f"duplicate relation id: {relation_id}")
        seen.add(relation_id)

        if source_token not in known_token_ids:
            raise ValueError(
                f"relation {relation_id} references unknown source token {source_token!r}"
            )
        if target_token not in known_token_ids:
            raise ValueError(
                f"relation {relation_id} references unknown target token {target_token!r}"
            )
        if not isinstance(kind, str) or not kind:
            raise ValueError(f"relation {relation_id} requires kind")
        if not isinstance(authority, str) or not authority:
            raise ValueError(f"relation {relation_id} requires authority")

        normalized.append(
            {
                "id": relation_id,
                "from": source_token,
                "to": target_token,
                "kind": kind,
                "label": relation.get("label", kind),
                "source": relation.get("source"),
                "authority": authority,
                "note": relation.get("note"),
            }
        )
    return normalized


def open_token_room(
    specimen: dict[str, Any],
    recipe_id: str,
    token_id: str,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Open one token as a replayable curiosity room."""
    compiled = compile_linguistic_projection(specimen, recipe_id, profile)
    witness_payload = specimen["witness"]
    witness = _witness_from_payload(witness_payload)
    anchored = _anchor_tokens(witness.text, specimen.get("tokens", []))
    by_id = {token["id"]: token for token in anchored}
    if token_id not in by_id:
        raise ValueError(f"unknown token: {token_id}")

    trace = compiled["projection"]["content"]["trace"]
    trace_by_id = {item["token_id"]: item for item in trace}
    if token_id not in trace_by_id:
        raise ValueError(
            f"token {token_id} is not emitted by recipe {recipe_id!r}"
        )

    token = by_id[token_id]
    current = trace_by_id[token_id]
    source_order = [item["id"] for item in anchored]
    output_order = [item["token_id"] for item in trace]

    source_index = source_order.index(token_id)
    output_index = output_order.index(token_id)

    def neighbor(order: list[str], index: int, offset: int) -> dict[str, Any] | None:
        target_index = index + offset
        if target_index < 0 or target_index >= len(order):
            return None
        neighbor_id = order[target_index]
        neighbor_token = by_id[neighbor_id]
        neighbor_trace = trace_by_id.get(neighbor_id)
        return {
            "token_id": neighbor_id,
            "source_surface": neighbor_token["surface"],
            "rendered": neighbor_trace["rendered"] if neighbor_trace else None,
        }

    choices_for_recipe = {
        item["token_id"]: item
        for item in list_choices(specimen, recipe_id)
    }
    relations = _declared_relations(
        specimen,
        known_token_ids=set(by_id),
    )
    outgoing = [relation for relation in relations if relation["from"] == token_id]
    incoming = [relation for relation in relations if relation["to"] == token_id]

    relation_doors: list[dict[str, Any]] = []
    for direction, relation_set in (("outgoing", outgoing), ("incoming", incoming)):
        for relation in relation_set:
            destination_id = (
                relation["to"] if direction == "outgoing" else relation["from"]
            )
            destination = by_id[destination_id]
            destination_trace = trace_by_id.get(destination_id)
            relation_doors.append(
                {
                    "kind": "relation",
                    "direction": direction,
                    "relation_id": relation["id"],
                    "relation_kind": relation["kind"],
                    "label": relation["label"],
                    "authority": relation["authority"],
                    "destination_token_id": destination_id,
                    "destination_source_surface": destination["surface"],
                    "destination_rendered": (
                        destination_trace["rendered"]
                        if destination_trace
                        else None
                    ),
                }
            )

    choice_info = choices_for_recipe.get(token_id)
    choice_doors = []
    if choice_info:
        for variant in choice_info["variants"]:
            choice_doors.append(
                {
                    "kind": "rendering-choice",
                    "token_id": token_id,
                    "choice_id": variant["id"],
                    "value": variant["value"],
                    "default": variant["default"],
                    "source": variant.get("source"),
                    "authority": variant.get("authority"),
                }
            )

    room = {
        "kind": "token-curiosity-room",
        "witness_locator": witness.locator,
        "recipe_id": recipe_id,
        "profile_id": compiled["projection"]["content"]["profile_id"],
        "token": {
            "id": token_id,
            "source_ordinal": token["ordinal"],
            "source_surface": token["surface"],
            "source_span": token["source_span"],
            "current_rendering": current["rendered"],
            "current_origin": current["origin"],
            "annotations": token["annotations"],
        },
        "neighbors": {
            "source": {
                "previous": neighbor(source_order, source_index, -1),
                "next": neighbor(source_order, source_index, 1),
            },
            "output": {
                "previous": neighbor(output_order, output_index, -1),
                "next": neighbor(output_order, output_index, 1),
            },
        },
        "rendering_choices": choice_info["variants"] if choice_info else [],
        "relations": {
            "outgoing": outgoing,
            "incoming": incoming,
        },
        "doors": choice_doors + relation_doors,
        "compiled_text": compiled["projection"]["content"]["text"],
        "compiled_projection_receipt": compiled["receipt"],
    }

    transform = Transform(
        name="token_curiosity_room",
        version="1",
        parameters={
            "recipe_id": recipe_id,
            "profile": profile,
            "token_id": token_id,
            "compiled_receipt": compiled["receipt"],
            "relations": outgoing + incoming,
        },
    )
    projection = Projection(kind="token-curiosity-room", content=room)
    delta = Delta(
        kind="inspection",
        details={
            "source_changed": False,
            "room_adds_authority": False,
            "note": (
                "The room composes already declared source anchors, projection "
                "choices, and relations for inspection. It does not alter the witness."
            ),
        },
    )
    receipt = make_receipt(
        witness=witness,
        transform=transform,
        projection=projection,
        delta=delta,
    )

    return {
        "room": room,
        "delta": asdict(delta),
        "receipt": asdict(receipt),
    }
