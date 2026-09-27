"""Command-line door for Revival specimens."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compiler import compile_specimen
from .linguistic import compile_linguistic_projection, list_recipes


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="revival",
        description="Compile an immutable witness into replayable projections.",
    )
    parser.add_argument("specimen", type=Path, help="Path to a Revival specimen JSON file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument(
        "--recipe",
        help="Compile one declared linguistic projection recipe instead of legacy transforms.",
    )
    parser.add_argument(
        "--list-recipes",
        action="store_true",
        help="List linguistic recipes declared by the specimen.",
    )
    args = parser.parse_args()

    specimen = json.loads(args.specimen.read_text(encoding="utf-8"))
    if args.list_recipes:
        result = {"recipes": list_recipes(specimen)}
    elif args.recipe:
        result = compile_linguistic_projection(specimen, args.recipe)
    else:
        result = compile_specimen(specimen)
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
