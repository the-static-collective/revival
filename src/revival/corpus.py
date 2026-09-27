"""Multi-witness corpus and exact-lemma traversal for Revival.

Corpus mechanics sit above frozen kernel v1. Each local curiosity room keeps
its ordinary single-witness receipt. Cross-witness indexes get a separate
corpus identity so multiple witnesses are never smuggled into one kernel
receipt.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .adapters.oshb import adapt_oshb_verse
from .curiosity import open_token_room
from .kernel.v1 import sha256
from .linguistic import compile_linguistic_projection


def _oshb_record(token: dict[str, Any]) -> dict[str, Any] | None:
    annotation = token.get("annotations", {}).get("oshb")
    if not isinstance(annotation, dict):
        return None
    data = annotation.get("data")
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("lemma"), str) or not data["lemma"]:
        return None
    return {
        "lemma": data["lemma"],
        "morph": data.get("morph"),
        "external_word_id": data.get("external_word_id"),
        "authority": annotation.get("authority"),
        "source": annotation.get("source"),
        "license": annotation.get("license"),
    }


def build_corpus(
    corpus_id: str,
    specimens: list[dict[str, Any]],
    *,
    recipe_id: str = "surface",
    description: str = "",
) -> dict[str, Any]:
    """Build a deterministic multi-witness corpus with exact lemma indexes."""
    if not isinstance(corpus_id, str) or not corpus_id:
        raise ValueError("corpus_id is required")
    if not specimens:
        raise ValueError("corpus requires at least one specimen")

    witness_ids: set[str] = set()
    locators: set[str] = set()
    token_ids: set[str] = set()
    witnesses: list[dict[str, Any]] = []
    lemma_index: dict[str, list[dict[str, Any]]] = {}
    specimen_by_locator: dict[str, dict[str, Any]] = {}

    for specimen in specimens:
        witness = specimen["witness"]
        witness_id = witness["id"]
        locator = witness["locator"]
        if witness_id in witness_ids:
            raise ValueError(f"duplicate corpus witness id: {witness_id}")
        if locator in locators:
            raise ValueError(f"duplicate corpus locator: {locator}")
        witness_ids.add(witness_id)
        locators.add(locator)

        compiled = compile_linguistic_projection(specimen, recipe_id)
        witnesses.append(
            {
                "witness_id": witness_id,
                "locator": locator,
                "witness_sha256": sha256(witness),
                "compiled_text": compiled["projection"]["content"]["text"],
                "compiled_projection_receipt": compiled["receipt"],
            }
        )
        specimen_by_locator[locator] = specimen

        for token in specimen.get("tokens", []):
            token_id = token["id"]
            if token_id in token_ids:
                raise ValueError(f"duplicate corpus token id: {token_id}")
            token_ids.add(token_id)

            record = _oshb_record(token)
            if record is None:
                continue
            occurrence = {
                "witness_id": witness_id,
                "locator": locator,
                "token_id": token_id,
                "source_surface": token["surface"],
                "lemma": record["lemma"],
                "morph": record["morph"],
                "authority": record["authority"],
                "source": record["source"],
            }
            lemma_index.setdefault(record["lemma"], []).append(occurrence)

    corpus_core = {
        "id": corpus_id,
        "description": description,
        "recipe_id": recipe_id,
        "witnesses": witnesses,
        "lemma_index": lemma_index,
    }
    corpus_sha256 = sha256(corpus_core)

    return {
        **corpus_core,
        "corpus_sha256": corpus_sha256,
        "_specimens_by_locator": specimen_by_locator,
    }


def public_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    """Return serializable corpus data without private specimen references."""
    return {
        key: value
        for key, value in corpus.items()
        if not key.startswith("_")
    }


def lemma_occurrences(
    corpus: dict[str, Any],
    lemma: str,
) -> list[dict[str, Any]]:
    """Return exact-identity occurrences for one declared lemma string."""
    return list(corpus["lemma_index"].get(lemma, []))


def open_corpus_token_room(
    corpus: dict[str, Any],
    locator: str,
    token_id: str,
) -> dict[str, Any]:
    """Open a local room and add exact-lemma cross-witness doors."""
    specimens = corpus.get("_specimens_by_locator", {})
    if locator not in specimens:
        raise ValueError(f"unknown corpus locator: {locator}")

    specimen = specimens[locator]
    opened = open_token_room(
        specimen,
        corpus["recipe_id"],
        token_id,
    )
    local_room = opened["room"]

    token = next(
        (item for item in specimen.get("tokens", []) if item["id"] == token_id),
        None,
    )
    if token is None:
        raise ValueError(f"unknown token {token_id!r} in {locator}")

    record = _oshb_record(token)
    lemma = record["lemma"] if record else None
    occurrences = lemma_occurrences(corpus, lemma) if lemma else []

    lemma_doors = [
        {
            "kind": "lemma-occurrence",
            "lemma": lemma,
            "destination_locator": item["locator"],
            "destination_witness_id": item["witness_id"],
            "destination_token_id": item["token_id"],
            "destination_source_surface": item["source_surface"],
            "destination_morph": item["morph"],
            "source": item["source"],
            "authority": item["authority"],
        }
        for item in occurrences
        if not (
            item["locator"] == locator
            and item["token_id"] == token_id
        )
    ]

    room = {
        **local_room,
        "corpus": {
            "id": corpus["id"],
            "corpus_sha256": corpus["corpus_sha256"],
        },
        "lemma": {
            "identity_rule": "exact declared annotation string equality",
            "value": lemma,
            "occurrences": occurrences,
        },
        "corpus_doors": lemma_doors,
    }

    corpus_receipt = {
        "kind": "corpus-token-room",
        "corpus_sha256": corpus["corpus_sha256"],
        "local_locator": locator,
        "local_token_id": token_id,
        "local_witness_sha256": opened["receipt"]["witness_sha256"],
        "local_room_projection_sha256": opened["receipt"]["projection_sha256"],
        "lemma_occurrences_sha256": sha256(occurrences),
        "projection_sha256": sha256(room),
    }

    return {
        "room": room,
        "local_room_receipt": opened["receipt"],
        "corpus_receipt": corpus_receipt,
    }


def load_corpus_manifest(
    manifest_path: Path,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    """Load and adapt every source entry declared by a corpus manifest."""
    manifest_path = manifest_path.resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = (root or Path.cwd()).resolve()

    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("corpus manifest requires non-empty entries")

    specimens: list[dict[str, Any]] = []
    for entry in entries:
        xml_path = (base / entry["xml"]).resolve()
        source_path = (base / entry["manifest"]).resolve()
        xml_text = xml_path.read_text(encoding="utf-8")
        source_manifest = json.loads(source_path.read_text(encoding="utf-8"))
        specimens.append(adapt_oshb_verse(xml_text, source_manifest))

    return build_corpus(
        data["id"],
        specimens,
        recipe_id=data.get("recipe", "surface"),
        description=data.get("description", ""),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.corpus",
        description="Build and inspect a multi-witness Revival corpus.",
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--lemma")
    parser.add_argument("--locator")
    parser.add_argument("--token")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    corpus = load_corpus_manifest(args.manifest, root=args.root)

    if args.lemma is not None:
        result: Any = {
            "corpus_id": corpus["id"],
            "corpus_sha256": corpus["corpus_sha256"],
            "lemma": args.lemma,
            "identity_rule": "exact declared annotation string equality",
            "occurrences": lemma_occurrences(corpus, args.lemma),
        }
    elif args.locator or args.token:
        if not args.locator or not args.token:
            parser.error("--locator and --token must be supplied together")
        result = open_corpus_token_room(corpus, args.locator, args.token)
    else:
        result = public_corpus(corpus)

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
