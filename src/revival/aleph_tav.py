"""Aleph-Tav learning instrument built from pinned OSHB morphology.

This layer deliberately sits above the exact-lemma corpus. It may decompose a
declared OSHB morpheme structure and create a derived family door, but it never
rewrites the upstream lemma string or promotes pedagogy into source authority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import unicodedata

from .corpus import load_corpus_manifest
from .kernel.v1 import sha256


FAMILY_ID = "oshb-v2.2:lemma-853:particle-o"
BASE_LEMMA = "853"
PEDAGOGY_AUTHORITY = "revival-008-pedagogical-lens"

MORPH_AUTHORITY = {
    "project": "Open Scriptures Hebrew Bible",
    "version": "2.2",
    "upstream_ref": "v.2.2",
    "upstream_commit": "6a5db284c715c18b239422e57bb89684e6a19f00",
    "upstream_path": "read/Script/MorphologyParser.js",
    "upstream_blob_sha": "0182bbff00a743267e9b68256bdc3afaccebc95c",
}

PART_OF_SPEECH = {
    "C": "Conjunction",
    "T": "Particle",
}
PARTICLE_TYPE = {
    "o": "direct object marker",
}
LANGUAGE = {
    "H": "Hebrew",
    "A": "Aramaic",
}
LETTER_NAMES = {
    "א": "Aleph",
    "ת": "Tav",
}


def _strip_marks(text: str) -> str:
    return "".join(
        char for char in text
        if not unicodedata.category(char).startswith("M")
    )


def _oshb_data(token: dict[str, Any]) -> dict[str, Any]:
    annotation = token.get("annotations", {}).get("oshb")
    if not isinstance(annotation, dict):
        raise ValueError(f"token {token.get('id')} has no OSHB annotation")
    data = annotation.get("data")
    if not isinstance(data, dict):
        raise ValueError(f"token {token.get('id')} has no OSHB data")
    return data


def _decode_morph_parts(morph: str) -> list[dict[str, Any]]:
    raw_parts = morph.split("/")
    if not raw_parts:
        raise ValueError("empty OSHB morphology")

    language_code = raw_parts[0][0] if raw_parts[0] else ""
    if language_code not in LANGUAGE:
        raise ValueError(f"unsupported OSHB language code: {language_code!r}")

    decoded: list[dict[str, Any]] = []
    for index, raw_part in enumerate(raw_parts):
        code = raw_part
        if index == 0:
            code = raw_part[1:]
        if not code:
            raise ValueError(f"empty morphology morpheme in {morph!r}")

        pos_code = code[0]
        item: dict[str, Any] = {
            "index": index,
            "raw": raw_part,
            "code": code,
            "language_code": language_code,
            "language": LANGUAGE[language_code],
            "part_of_speech_code": pos_code,
            "part_of_speech": PART_OF_SPEECH.get(pos_code),
        }
        if pos_code == "T" and len(code) > 1:
            item["particle_type_code"] = code[1]
            item["particle_type"] = PARTICLE_TYPE.get(code[1])
        decoded.append(item)
    return decoded


def decompose_oshb_token(token: dict[str, Any]) -> dict[str, Any]:
    """Align OSHB surface, lemma, and morphology morphemes exactly."""
    data = _oshb_data(token)
    raw_surface = data["raw_surface"]
    lemma = data["lemma"]
    morph = data["morph"]

    surfaces = raw_surface.split("/")
    lemmas = lemma.split("/")
    morphs = _decode_morph_parts(morph)

    if not (len(surfaces) == len(lemmas) == len(morphs)):
        raise ValueError(
            f"unaligned OSHB morphemes for {token['id']}: "
            f"surface={len(surfaces)} lemma={len(lemmas)} morph={len(morphs)}"
        )

    parts: list[dict[str, Any]] = []
    for index, (surface, lemma_part, morph_part) in enumerate(
        zip(surfaces, lemmas, morphs)
    ):
        unpointed = _strip_marks(surface)
        letters = [
            {
                "letter": char,
                "name": LETTER_NAMES.get(char),
            }
            for char in unpointed
            if unicodedata.category(char).startswith("L")
        ]
        parts.append(
            {
                "index": index,
                "surface": surface,
                "unpointed": unpointed,
                "lemma": lemma_part,
                "morphology": morph_part,
                "letters": letters,
            }
        )

    return {
        "token_id": token["id"],
        "source_surface": token["surface"],
        "raw_surface": raw_surface,
        "declared_lemma": lemma,
        "declared_morph": morph,
        "parts": parts,
        "rule": (
            "literal slash alignment across OSHB raw_surface, lemma, and morph; "
            "no prefix stripping is applied to upstream identity"
        ),
        "authority": MORPH_AUTHORITY,
    }


def _aleph_tav_component(
    decomposition: dict[str, Any],
) -> dict[str, Any] | None:
    matches = []
    for part in decomposition["parts"]:
        morph = part["morphology"]
        if (
            part["lemma"] == BASE_LEMMA
            and morph["part_of_speech_code"] == "T"
            and morph.get("particle_type_code") == "o"
        ):
            matches.append(part)

    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError(
            f"token {decomposition['token_id']} has multiple 853/To components"
        )
    return matches[0]


def _whole_token_projection(
    decomposition: dict[str, Any],
    marker: dict[str, Any],
    mode: str,
) -> str:
    pieces: list[str] = []
    for part in decomposition["parts"]:
        if part["index"] == marker["index"]:
            if mode == "source":
                pieces.append(part["surface"])
            elif mode == "operator":
                pieces.append("[OBJ→]")
            elif mode == "letters":
                pieces.append("⟦את⟧")
            elif mode == "hidden":
                pieces.append("")
            else:
                raise ValueError(f"unknown Aleph-Tav projection mode: {mode}")
        else:
            pieces.append(part["surface"])

    if mode == "source":
        return "/".join(pieces)
    visible = [piece for piece in pieces if piece]
    return " + ".join(visible)


def build_aleph_tav_instrument(corpus: dict[str, Any]) -> dict[str, Any]:
    """Build the derived Aleph-Tav family and pedagogical projection modes."""
    specimens = corpus.get("_specimens_by_locator", {})
    occurrences: list[dict[str, Any]] = []

    for witness in corpus["witnesses"]:
        locator = witness["locator"]
        specimen = specimens[locator]
        tokens = specimen.get("tokens", [])
        for token_index, token in enumerate(tokens):
            decomposition = decompose_oshb_token(token)
            marker = _aleph_tav_component(decomposition)
            if marker is None:
                continue

            next_token = (
                tokens[token_index + 1]
                if token_index + 1 < len(tokens)
                else None
            )
            prefixes = [
                part
                for part in decomposition["parts"]
                if part["index"] < marker["index"]
            ]

            occurrence = {
                "family_id": FAMILY_ID,
                "locator": locator,
                "witness_id": witness["witness_id"],
                "token_id": token["id"],
                "source_surface": token["surface"],
                "declared_lemma": decomposition["declared_lemma"],
                "declared_morph": decomposition["declared_morph"],
                "decomposition": decomposition,
                "marker_component": marker,
                "prefix_components": prefixes,
                "reading": {
                    "component_hint": "et",
                    "authority": PEDAGOGY_AUTHORITY,
                    "note": (
                        "Approximate learner reading hint for the standalone "
                        "אֵת component; not supplied by OSHB."
                    ),
                },
                "letters": {
                    "unpointed": marker["unpointed"],
                    "names": [
                        item["name"]
                        for item in marker["letters"]
                        if item["name"]
                    ],
                    "authority": PEDAGOGY_AUTHORITY,
                    "note": (
                        "Letter names identify the written consonantal letters; "
                        "they are not a claim about the grammatical meaning."
                    ),
                },
                "grammar": {
                    "part_of_speech": marker["morphology"]["part_of_speech"],
                    "particle_type": marker["morphology"].get("particle_type"),
                    "source": MORPH_AUTHORITY,
                },
                "next_token_context": (
                    {
                        "token_id": next_token["id"],
                        "source_surface": next_token["surface"],
                        "rule": "immediate next source token only",
                        "authority": PEDAGOGY_AUTHORITY,
                        "note": (
                            "Context preview for this proof instrument; not a "
                            "full syntactic phrase parse."
                        ),
                    }
                    if next_token
                    else None
                ),
                "projection_examples": {
                    mode: _whole_token_projection(
                        decomposition,
                        marker,
                        mode,
                    )
                    for mode in ("source", "operator", "letters", "hidden")
                },
            }
            occurrences.append(occurrence)

    family_core = {
        "family_id": FAMILY_ID,
        "derivation_rule": (
            "include an OSHB morpheme iff aligned lemma component == '853' "
            "and aligned morphology decodes as Particle / direct object marker"
        ),
        "identity_boundary": (
            "derived family membership does not rewrite the token's declared "
            "OSHB lemma identity; 853 and c/853 remain distinct upstream strings"
        ),
        "morphology_authority": MORPH_AUTHORITY,
        "occurrences": occurrences,
    }

    return {
        **family_core,
        "corpus_id": corpus["id"],
        "corpus_sha256": corpus["corpus_sha256"],
        "family_sha256": sha256(family_core),
    }


def open_aleph_tav_room(
    instrument: dict[str, Any],
    locator: str,
    token_id: str,
) -> dict[str, Any]:
    occurrence = next(
        (
            item
            for item in instrument["occurrences"]
            if item["locator"] == locator and item["token_id"] == token_id
        ),
        None,
    )
    if occurrence is None:
        raise ValueError(f"not an Aleph-Tav instrument occurrence: {locator} {token_id}")

    doors = [
        {
            "kind": "derived-family-occurrence",
            "family_id": FAMILY_ID,
            "destination_locator": other["locator"],
            "destination_token_id": other["token_id"],
            "destination_source_surface": other["source_surface"],
            "destination_declared_lemma": other["declared_lemma"],
            "destination_declared_morph": other["declared_morph"],
        }
        for other in instrument["occurrences"]
        if not (
            other["locator"] == locator
            and other["token_id"] == token_id
        )
    ]

    room = {
        "kind": "aleph-tav-instrument-room",
        "occurrence": occurrence,
        "constellation_doors": doors,
        "learning_layers": {
            "read": occurrence["reading"],
            "letters": occurrence["letters"],
            "grammar": occurrence["grammar"],
            "structure": occurrence["next_token_context"],
            "projection_examples": occurrence["projection_examples"],
            "interpretation_boundary": {
                "authority": PEDAGOGY_AUTHORITY,
                "note": (
                    "Aleph is the first Hebrew letter and Tav is the last. "
                    "That letter-order observation may be explored in a separate "
                    "interpretive layer; it is not encoded here as the grammatical "
                    "meaning of the direct object marker."
                ),
            },
        },
    }

    receipt = {
        "kind": "aleph-tav-instrument-room",
        "corpus_sha256": instrument["corpus_sha256"],
        "family_sha256": instrument["family_sha256"],
        "locator": locator,
        "token_id": token_id,
        "decomposition_sha256": sha256(occurrence["decomposition"]),
        "projection_sha256": sha256(room),
    }
    return {
        "room": room,
        "receipt": receipt,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.aleph_tav",
        description="Inspect the derived Aleph-Tav learning instrument.",
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--locator")
    parser.add_argument("--token")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    corpus = load_corpus_manifest(args.manifest, root=args.root)
    instrument = build_aleph_tav_instrument(corpus)

    if args.locator or args.token:
        if not args.locator or not args.token:
            parser.error("--locator and --token must be supplied together")
        result: Any = open_aleph_tav_room(
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
