"""Recipe-driven linguistic projections for Revival.

This layer sits above frozen kernel v1. It lets a declared recipe choose and
reorder source-anchored token renderings while preserving a trace to the held
witness and to any annotation that introduced wording.

Revival 003 adds explicit preference profiles. A linguistic annotation may
offer multiple attributable renderings; a profile selects among those
renderings without mutating the held witness or the underlying annotation set.
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


def _variant_map(
    *,
    token_id: str,
    field: str,
    annotation: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], str]:
    variants = annotation.get("variants")
    if not isinstance(variants, list) or not variants:
        raise ValueError(
            f"token {token_id} annotation {field!r} variants must be a non-empty list"
        )

    by_id: dict[str, dict[str, Any]] = {}
    for variant in variants:
        if not isinstance(variant, dict):
            raise ValueError(
                f"token {token_id} annotation {field!r} variant must be an object"
            )
        variant_id = variant.get("id")
        if not isinstance(variant_id, str) or not variant_id:
            raise ValueError(
                f"token {token_id} annotation {field!r} variant requires id"
            )
        if variant_id in by_id:
            raise ValueError(
                f"token {token_id} annotation {field!r} duplicates variant {variant_id}"
            )
        if "value" not in variant:
            raise ValueError(
                f"token {token_id} annotation {field!r} variant {variant_id} "
                "requires value"
            )
        by_id[variant_id] = variant

    default = annotation.get("default")
    if not isinstance(default, str) or default not in by_id:
        raise ValueError(
            f"token {token_id} annotation {field!r} requires a default variant id"
        )
    return by_id, default


def _annotation_choices(
    *,
    token: dict[str, Any],
    field: str,
) -> list[dict[str, Any]]:
    annotation = token["annotations"].get(field)
    if not isinstance(annotation, dict) or "variants" not in annotation:
        return []

    by_id, default = _variant_map(
        token_id=token["id"],
        field=field,
        annotation=annotation,
    )
    choices: list[dict[str, Any]] = []
    for variant_id, variant in by_id.items():
        choices.append(
            {
                "id": variant_id,
                "value": str(variant["value"]),
                "default": variant_id == default,
                "source": variant.get("source"),
                "authority": variant.get("authority"),
                "note": variant.get("note"),
            }
        )
    return choices


def list_choices(
    specimen: dict[str, Any],
    recipe_id: str,
) -> list[dict[str, Any]]:
    """List explicit rendering choices exposed by one recipe."""
    witness = _witness_from_payload(specimen["witness"])
    tokens = _anchor_tokens(witness.text, specimen.get("tokens", []))
    recipe = _select_recipe(specimen, recipe_id)
    field = recipe.get("field", "surface")
    by_id = {token["id"]: token for token in tokens}
    source_order = [token["id"] for token in tokens]
    output_order = recipe.get("sequence", source_order)

    choices: list[dict[str, Any]] = []
    for token_id in output_order:
        if token_id not in by_id:
            raise ValueError(f"recipe references unknown token id: {token_id}")
        token = by_id[token_id]
        variants = _annotation_choices(token=token, field=field)
        if variants:
            choices.append(
                {
                    "token_id": token_id,
                    "source_surface": token["surface"],
                    "source_span": token["source_span"],
                    "field": field,
                    "variants": variants,
                }
            )
    return choices


def _validate_profile(
    profile: dict[str, Any] | None,
    *,
    recipe_id: str,
    output_order: list[str],
) -> tuple[str | None, dict[str, str]]:
    if profile is None:
        return None, {}
    if not isinstance(profile, dict):
        raise ValueError("profile must be an object")

    profile_id = profile.get("id")
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError("profile requires a non-empty id")

    declared_recipe = profile.get("recipe")
    if declared_recipe != recipe_id:
        raise ValueError(
            f"profile {profile_id} targets recipe {declared_recipe!r}, "
            f"not {recipe_id!r}"
        )

    choices = profile.get("choices", {})
    if not isinstance(choices, dict):
        raise ValueError(f"profile {profile_id} choices must be an object")

    normalized: dict[str, str] = {}
    for token_id, variant_id in choices.items():
        if token_id not in output_order:
            raise ValueError(
                f"profile {profile_id} chooses token {token_id} "
                "outside the recipe output"
            )
        if not isinstance(variant_id, str) or not variant_id:
            raise ValueError(
                f"profile {profile_id} choice for {token_id} must be a variant id"
            )
        normalized[str(token_id)] = variant_id
    return profile_id, normalized


def _render_field(
    token: dict[str, Any],
    field: str,
    *,
    choice_id: str | None = None,
) -> tuple[str, dict[str, Any]]:
    if field == "surface":
        if choice_id is not None:
            raise ValueError(f"token {token['id']} surface has no selectable variants")
        return token["surface"], {
            "kind": "witness",
            "field": "surface",
        }

    if field == "unpointed":
        if choice_id is not None:
            raise ValueError(
                f"token {token['id']} unpointed rendering has no selectable variants"
            )
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
        if choice_id is not None:
            raise ValueError(
                f"token {token['id']} annotation {field!r} has no selectable variants"
            )
        return annotation, {
            "kind": "annotation",
            "field": field,
            "authority": "unspecified",
        }

    if not isinstance(annotation, dict):
        raise ValueError(
            f"token {token['id']} annotation {field!r} must be a string or object"
        )

    if "variants" in annotation:
        by_id, default = _variant_map(
            token_id=token["id"],
            field=field,
            annotation=annotation,
        )
        selected = choice_id or default
        if selected not in by_id:
            raise ValueError(
                f"token {token['id']} annotation {field!r} has no variant {selected!r}"
            )
        variant = by_id[selected]
        return str(variant["value"]), {
            "kind": "annotation-choice",
            "field": field,
            "choice_id": selected,
            "default_choice": selected == default,
            "source": variant.get("source"),
            "authority": variant.get("authority"),
            "note": variant.get("note"),
        }

    if choice_id is not None:
        raise ValueError(
            f"token {token['id']} annotation {field!r} has no selectable variants"
        )
    if "value" not in annotation:
        raise ValueError(
            f"token {token['id']} annotation {field!r} must contain value or variants"
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
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile one source-backed linguistic projection from a recipe and profile."""
    witness = _witness_from_payload(specimen["witness"])
    tokens = _anchor_tokens(witness.text, specimen.get("tokens", []))
    if not tokens:
        raise ValueError("linguistic projection requires declared source tokens")

    recipe = _select_recipe(specimen, recipe_id)
    if recipe.get("mode", "text") != "text":
        raise ValueError("Revival currently supports only text recipes")

    field = recipe.get("field", "surface")
    separator = recipe.get("separator", " ")
    by_id = {token["id"]: token for token in tokens}
    source_order = [token["id"] for token in tokens]
    output_order = recipe.get("sequence", source_order)

    if len(output_order) != len(set(output_order)):
        raise ValueError("Revival recipes may not duplicate token ids")
    unknown = [token_id for token_id in output_order if token_id not in by_id]
    if unknown:
        raise ValueError(f"recipe references unknown token ids: {', '.join(unknown)}")

    profile_id, profile_choices = _validate_profile(
        profile,
        recipe_id=recipe_id,
        output_order=output_order,
    )

    trace: list[dict[str, Any]] = []
    pieces: list[str] = []
    output_cursor = 0
    annotation_introductions: list[dict[str, Any]] = []
    empty_renderings: list[str] = []
    choice_selections: list[dict[str, Any]] = []
    consumed_choices: set[str] = set()

    for output_ordinal, token_id in enumerate(output_order):
        token = by_id[token_id]
        requested_choice = profile_choices.get(token_id)
        rendered, origin = _render_field(
            token,
            field,
            choice_id=requested_choice,
        )
        if requested_choice is not None:
            consumed_choices.add(token_id)

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

        if origin["kind"] in {"annotation", "annotation-choice"}:
            annotation_introductions.append(
                {
                    "token_id": token_id,
                    "field": field,
                    "value": rendered,
                    "source": origin.get("source"),
                    "authority": origin.get("authority"),
                }
            )

        if origin["kind"] == "annotation-choice":
            choice_selections.append(
                {
                    "token_id": token_id,
                    "choice_id": origin["choice_id"],
                    "default_choice": origin["default_choice"],
                    "selected_by_profile": requested_choice is not None,
                }
            )

    unconsumed = sorted(set(profile_choices) - consumed_choices)
    if unconsumed:
        raise ValueError(
            f"profile {profile_id} choices were not selectable: {', '.join(unconsumed)}"
        )

    omitted = [token_id for token_id in source_order if token_id not in output_order]
    projection = Projection(
        kind="linguistic-text",
        content={
            "recipe_id": recipe_id,
            "profile_id": profile_id,
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
            "preference_profile": (
                {
                    "id": profile_id,
                    "choices": profile_choices,
                }
                if profile_id is not None
                else None
            ),
            "choice_selections": choice_selections,
            "note": (
                "Projection wording, order, and preference selections are declared "
                "compilation choices. Trace entries preserve source-token and "
                "annotation origins."
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
        version="2",
        parameters={
            "recipe": recipe,
            "profile": (
                {
                    "id": profile_id,
                    "choices": profile_choices,
                }
                if profile_id is not None
                else None
            ),
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
        "profile": profile,
        "projection": asdict(projection),
        "delta": asdict(delta),
        "receipt": asdict(receipt),
    }
