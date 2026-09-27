"""Command-line door for Revival specimens."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .atlas import build_curiosity_atlas_html
from .compiler import compile_specimen
from .curiosity import open_token_room
from .linguistic import compile_linguistic_projection, list_choices, list_recipes


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
    parser.add_argument(
        "--list-choices",
        action="store_true",
        help="List selectable rendering choices exposed by --recipe.",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        help="Preference profile JSON used with --recipe.",
    )
    parser.add_argument(
        "--open-token",
        help="Open one emitted source token as a curiosity room; requires --recipe.",
    )
    parser.add_argument(
        "--build-atlas",
        type=Path,
        help="Write a standalone Curiosity Atlas HTML file; requires --recipe.",
    )
    args = parser.parse_args()

    specimen = json.loads(args.specimen.read_text(encoding="utf-8"))
    if args.list_recipes:
        result = {"recipes": list_recipes(specimen)}
    elif args.build_atlas:
        if not args.recipe:
            parser.error("--build-atlas requires --recipe")
        if args.list_choices or args.open_token:
            parser.error("--build-atlas cannot be combined with --list-choices or --open-token")
        profile = (
            json.loads(args.profile.read_text(encoding="utf-8"))
            if args.profile
            else None
        )
        atlas_result, atlas_html = build_curiosity_atlas_html(
            specimen,
            args.recipe,
            profile,
        )
        args.build_atlas.parent.mkdir(parents=True, exist_ok=True)
        args.build_atlas.write_text(atlas_html, encoding="utf-8")
        result = {
            "atlas_output": str(args.build_atlas),
            "compiled_text": atlas_result["atlas"]["compiled_text"],
            "receipt": atlas_result["receipt"],
        }
    elif args.open_token:
        if not args.recipe:
            parser.error("--open-token requires --recipe")
        profile = (
            json.loads(args.profile.read_text(encoding="utf-8"))
            if args.profile
            else None
        )
        result = open_token_room(
            specimen,
            args.recipe,
            args.open_token,
            profile,
        )
    elif args.list_choices:
        if not args.recipe:
            parser.error("--list-choices requires --recipe")
        if args.profile:
            parser.error("--list-choices does not consume --profile")
        result = {
            "recipe": args.recipe,
            "choices": list_choices(specimen, args.recipe),
        }
    elif args.recipe:
        profile = (
            json.loads(args.profile.read_text(encoding="utf-8"))
            if args.profile
            else None
        )
        result = compile_linguistic_projection(specimen, args.recipe, profile)
    else:
        if args.profile:
            parser.error("--profile requires --recipe")
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
