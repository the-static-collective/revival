"""Recipe-driven linguistic projections for Revival.

This layer sits above frozen kernel v1. It lets a declared recipe choose and
reorder source-anchored token renderings while preserving a trace to the held
witness and to any annotation that introduced wording.
"""

from __future__ import annotations

from dataclasses import asdict
import unicodedata
from typing import Any

from .kernel.v1 import Delta, Projection, Transform, Witness, make_receipt


def _witness_from_payload(payload: dict[str, Any]) -> Witness:
    required = ("id", "locator", "language", "script", "text", "source_note")
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"witness missing required fields: {', '.join(missing)}")
    return Witness(**{key: payload[key] for key in required})


def _strip_marks(text: str) -> str:
    return "".join(
        char for char in text if not unicodedata.category(char).startswith("M")
    )


def _anchor_tokens(text: str, declared: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Anchor declared ordered token surfaces to exact witness character spans."""
    cursor = 0
    anchored: list[dict[str, Any]] = []
    seen: set[str] = set()

    for ordinal, token in enumerate(declared):
        token_id = token.get("id")
        surface = token.get("surface")
        if not token_id or not isinstance(token_id, str):
            raise ValueError(f"token {ordinal} requires a string id")
        if token_id in seen:
            raise ValueError(f"duplicate token id: {token_id}")
        seen.add(token_id)
        if not isinstance(surface, str) or not surface:
            raise ValueError(f"token {token_id} requires a non-empty surface")

        start = text.find(surface, cursor)
        if start < 0:
            raise ValueError(
                f"token {token_id} surface is not found after witness offset {cursor}"
            )
        if any(not char.isspace() for char in text[cursor:start]):
            raise ValueError(
                f"unaccounted witness content before token {token_id}: "
                f"{text[cursor:start]!r}"
            )

        end = start + len(surface)
        anchored.append(
            {
                "id": token_id,
                "ordinal": ordinal,
                "surface": surface,
                "source_span": [start, end],
                "annotations": token.get("annotations", {}),
            }
        )
        cursor = end

    if any(not char.isspace() for char in text[cursor:]):
        raise ValueError(f"unaccounted trailing witness content: {text[cursor:]!r}")

    return anchored


def list_recipes(specimen: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "id": recipe["id"],
            "description": recipe.get("description", ""),
        }
        for recipe in specimen.get("recipes", [])
    ]


def _select_recipe(specimen: dict[str, Any], recipe_id: str) -> dict[str, Any]:
    matches = [
        recipe for recipe in specimen.get("recipes", []) if recipe.get("id") == recipe_id
    ]
    if not matches:
        raise ValueError(f"unknown recipe: {recipe_id}")
    if len(matches) > 1:
        raise ValueError(f"duplicate recipe id: {recipe_id}")
    return matches[0]


def _render_field(token: dict[str, Any], field: str) -> tuple[str, dict[str, Any]]:
    if field == "surface":
        return token["surface"], {
            "kind": "witness",
            "field": "surface",
        }

    if field == "unpointed":
        return _strip_marks(token["surface"]), {
            "kind": "mechanical-transform",
            "name": "strip_unicode_marks",
            "version": "1",
        }

    annotation = token["annotations"].get(field)
    if annotation is None:
        raise ValueError(
            f"token {token['id']} has no annotation for recipe field {field!r}"
        )
    if isinstance(annotation, str):
        return annotation, {
            "kind": "annotation",
            "field": field,
            "authority": "unspecified",
        }
    if not isinstance(annotation, dict) or "value" not in annotation:
        raise ValueError(
            f"token {token['id']} annotation {field!r} must be a string "
            "or an object containing value"
        )
    return str(annotation["value"]), {
        "kind": "annotation",
        "field": field,
        "source": annotation.get("source"),
        "authority": annotation.get("authority"),
        "note": annotation.get("note"),
    }


def compile_linguistic_projection(
    specimen: dict[str, Any],
    recipe_id: str,
) -> dict[str, Any]:
    """Compile one source-backed linguistic projection from a declared recipe."""
    witness = _witness_from_payload(specimen["witness"])
    tokens = _anchor_tokens(witness.text, specimen.get("tokens", []))
    if not tokens:
        raise ValueError("linguistic projection requires declared source tokens")

    recipe = _select_recipe(specimen, recipe_id)
    if recipe.get("mode", "text") != "text":
        raise ValueError("Revival 002 supports only text recipes")

    field = recipe.get("field", "surface")
    separator = recipe.get("separator", " ")
    by_id = {token["id"]: token for token in tokens}
    source_order = [token["id"] for token in tokens]
    output_order = recipe.get("sequence", source_order)

    if len(output_order) != len(set(output_order)):
        raise ValueError("Revival 002 recipes may not duplicate token ids")
    unknown = [token_id for token_id in output_order if token_id not in by_id]
    if unknown:
        raise ValueError(f"recipe references unknown token ids: {', '.join(unknown)}")

    trace: list[dict[str, Any]] = []
    pieces: list[str] = []
    output_cursor = 0
    annotation_introductions: list[dict[str, Any]] = []
    empty_renderings: list[str] = []

    for output_ordinal, token_id in enumerate(output_order):
        token = by_id[token_id]
        rendered, origin = _render_field(token, field)

        if rendered:
            if pieces:
                output_cursor += len(separator)
            output_span = [output_cursor, output_cursor + len(rendered)]
            pieces.append(rendered)
            output_cursor += len(rendered)
        else:
            output_span = None
            empty_renderings.append(token_id)

        trace_item = {
            "token_id": token_id,
            "source_ordinal": token["ordinal"],
            "output_ordinal": output_ordinal,
            "source_surface": token["surface"],
            "source_span": token["source_span"],
            "rendered": rendered,
            "output_span": output_span,
            "origin": origin,
        }
        trace.append(trace_item)

        if origin["kind"] == "annotation":
            annotation_introductions.append(
                {
                    "token_id": token_id,
                    "field": field,
                    "value": rendered,
                    "source": origin.get("source"),
                    "authority": origin.get("authority"),
                }
            )

    omitted = [token_id for token_id in source_order if token_id not in output_order]
    projection = Projection(
        kind="linguistic-text",
        content={
            "recipe_id": recipe_id,
            "text": separator.join(pieces),
            "trace": trace,
        },
    )
    delta = Delta(
        kind="linguistic-projection",
        details={
            "field": field,
            "source_order": source_order,
            "output_order": output_order,
            "reordered": output_order != [
                token_id for token_id in source_order if token_id in output_order
            ],
            "omitted_by_recipe": omitted,
            "empty_renderings": empty_renderings,
            "annotation_introductions": annotation_introductions,
            "note": (
                "Projection wording and order are declared compilation choices. "
                "Trace entries preserve their source-token and annotation origins."
            ),
        },
    )

    input_bindings = [
        {
            "token_id": item["token_id"],
            "source_surface": item["source_surface"],
            "source_span": item["source_span"],
            "rendered": item["rendered"],
            "origin": item["origin"],
        }
        for item in trace
    ]
    transform = Transform(
        name="linguistic_recipe",
        version="1",
        parameters={
            "recipe": recipe,
            # Bind only the inputs selected by this recipe. The witness hash
            # already binds the complete held source, while unrelated
            # annotations should not invalidate an unchanged projection.
            "input_bindings": input_bindings,
        },
    )
    receipt = make_receipt(
        witness=witness,
        transform=transform,
        projection=projection,
        delta=delta,
    )

    return {
        "witness": asdict(witness),
        "recipe": recipe,
        "projection": asdict(projection),
        "delta": asdict(delta),
        "receipt": asdict(receipt),
    }
