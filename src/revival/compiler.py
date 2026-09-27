"""Deterministic Revival specimen compiler."""

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


def _exact(witness: Witness) -> tuple[Projection, Delta]:
    return (
        Projection(kind="exact-text", content=witness.text),
        Delta(
            kind="identity",
            details={
                "removed": [],
                "introduced": [],
                "note": "Exact witness text projected without alteration.",
            },
        ),
    )


def _strip_unicode_marks(witness: Witness) -> tuple[Projection, Delta]:
    kept: list[str] = []
    removed: list[dict[str, Any]] = []

    for index, char in enumerate(witness.text):
        category = unicodedata.category(char)
        if category.startswith("M"):
            removed.append(
                {
                    "index": index,
                    "char": char,
                    "codepoint": f"U+{ord(char):04X}",
                    "name": unicodedata.name(char, "UNKNOWN"),
                    "category": category,
                }
            )
        else:
            kept.append(char)

    return (
        Projection(kind="text-without-unicode-marks", content="".join(kept)),
        Delta(
            kind="loss",
            details={
                "operation": "remove every Unicode character whose general category begins with M",
                "removed": removed,
                "introduced": [],
            },
        ),
    )


TRANSFORMS = {
    "exact": _exact,
    "strip_unicode_marks": _strip_unicode_marks,
}


def compile_specimen(specimen: dict[str, Any]) -> dict[str, Any]:
    """Compile a declared witness through declared transforms.

    Every output carries a delta and a receipt. The witness is never modified.
    """
    witness = _witness_from_payload(specimen["witness"])
    declared = specimen.get("transforms", [])
    if not declared:
        raise ValueError("at least one transform must be declared")

    results: list[dict[str, Any]] = []
    for item in declared:
        name = item["name"]
        version = str(item.get("version", "1"))
        parameters = item.get("parameters", {})
        if name not in TRANSFORMS:
            raise ValueError(f"unknown transform: {name}")

        transform = Transform(name=name, version=version, parameters=parameters)
        projection, delta = TRANSFORMS[name](witness)
        receipt = make_receipt(
            witness=witness,
            transform=transform,
            projection=projection,
            delta=delta,
        )
        results.append(
            {
                "transform": asdict(transform),
                "projection": asdict(projection),
                "delta": asdict(delta),
                "receipt": asdict(receipt),
            }
        )

    return {
        "witness": asdict(witness),
        "results": results,
    }
