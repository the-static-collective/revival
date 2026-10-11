"""Revival-owned read-only Jubilee door. No frozen-kernel or receiver change.

Rebuild a locally pinned source world before exporting a passage address. The
artifact binds bytes and attribution; it does not grant runtime/event authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any
from urllib.parse import quote

from .kernel.v1 import sha256
from .object_relations import load_object_relation_instrument
from .world_places import build_world_places_html

SOURCE_PIN = "af1e00c24e3d7c6eb6b1ac39ef59bf894e2385fd"
SCHEMA = "revival.jubilee-source-door/0.1"


def raw_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True).stdout


def pinned_inputs(root: Path, pin: str) -> dict[str, str]:
    if not re.fullmatch(r"[0-9a-f]{40}", pin):
        raise ValueError("Expected immutable source commit")
    paths = _git(root, "ls-tree", "-r", "--name-only", pin).decode().splitlines()
    selected = [p for p in paths if p.startswith("src/revival/") and p.endswith(".py")
                or p.startswith(("sources/oshb-v2.2/", "sources/macula-hebrew/"))
                or p == "corpora/oshb-v2.2-genesis-opening.json"]
    if "src/revival/kernel/v1.py" not in selected:
        raise ValueError("Pinned source compiler required")
    digests = {}
    for path in selected:
        expected = _git(root, "show", f"{pin}:{path}")
        actual = (root / path).read_bytes()
        if actual != expected:
            raise ValueError(f"Pinned input mismatch: {path}")
        digests[path] = raw_hash(actual)
    return digests


def build_door(root: Path, locator: str = "Gen.1.1", pin: str = SOURCE_PIN) -> dict[str, Any]:
    root = root.resolve()
    if Path(__file__).resolve().parents[2] != root:
        raise ValueError("Use the owner repository's local source package")
    digests = pinned_inputs(root, pin)
    corpus, instrument = load_object_relation_instrument(
        root / "corpora/oshb-v2.2-genesis-opening.json",
        root / "sources/macula-hebrew/Gen.1.1-lowfat.xml",
        root / "sources/macula-hebrew/source.json", root=root,
    )
    result, html = build_world_places_html(corpus, instrument)
    passage = next((p for p in result["world"]["places"]
                    if p["kind"] == "passage" and p["label"] == locator), None)
    if passage is None:
        raise ValueError("Reference is not in the built source world")
    oshb = json.loads((root / "sources/oshb-v2.2/source.json").read_text())
    macula = json.loads((root / "sources/macula-hebrew/source.json").read_text())
    core = {
        "schema": SCHEMA,
        "status": "SOURCE_BOUND_READ_ONLY",
        "producer": {"repository": "https://github.com/the-static-collective/revival",
                     "sourceCommit": pin, "exporterSha256": raw_hash(Path(__file__).read_bytes())},
        "locator": locator, "revivalAddress": passage["address"],
        "witnessSha256": passage["witness_sha256"],
        "worldReceipt": result["receipt"],
        "inputDigests": digests,
        "licenses": [{"project": oshb["project"], "license": oshb["license"],
                      "upstreamCommit": oshb["upstream_commit"], "upstreamBlob": oshb["upstream_blob_sha"]},
                     {"project": macula["project"], "license": macula["license"],
                      "attribution": macula["attribution"], "upstreamCommit": macula["upstream_commit"],
                      "upstreamBlob": macula["upstream_blob_sha"]}],
        "worldSha256": sha256(result), "htmlSha256": raw_hash(html.encode("utf-8")),
        "files": {"world": "world.json", "html": "genesis-world.html"},
        "fragment": "#" + quote(passage["address"], safe=""),
        "effect": "NONE", "authority": "NONE",
        "nonclaims": ["THEOLOGICAL_TRUTH", "PREFERRED_TRANSLATION", "LIVE_SCAN", "HOST_ACCEPTANCE",
                      "PARTICIPANT_CONSENT", "SOURCE_ADMISSION", "SIGNATURE", "INDEPENDENT_UPSTREAM_RETRIEVAL"],
    }
    return {"manifest": {**core, "artifactSha256": sha256(core)}, "world": result, "html": html}


def resolve_candidate(candidate: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    if set(candidate) != {"id", "reference", "public", "withdrawn"}:
        raise ValueError("Expected bounded public-reference candidate")
    if not isinstance(candidate["id"], str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", candidate["id"]):
        raise ValueError("Invalid candidate identifier")
    if not isinstance(candidate["reference"], str) or len(candidate["reference"]) > 80:
        raise ValueError("Invalid reference")
    if type(candidate["public"]) is not bool or type(candidate["withdrawn"]) is not bool:
        raise ValueError("Explicit publication and withdrawal flags required")
    manifest = bundle["manifest"]
    core = {k: v for k, v in manifest.items() if k != "artifactSha256"}
    if (manifest.get("schema") != SCHEMA or manifest.get("effect") != "NONE"
            or manifest.get("artifactSha256") != sha256(core)
            or manifest.get("worldSha256") != sha256(bundle["world"])
            or manifest.get("htmlSha256") != raw_hash(bundle["html"].encode("utf-8"))):
        raise ValueError("Artifact integrity mismatch")
    supported = next((p for p in bundle["world"]["world"]["places"]
                      if p["kind"] == "passage" and p["label"] == manifest["locator"]), None)
    if supported is None or supported["address"] != manifest["revivalAddress"] or supported["witness_sha256"] != manifest["witnessSha256"]:
        raise ValueError("Address is not supplied by the built world")
    expected = build_door(Path(__file__).resolve().parents[2], manifest["locator"])
    if bundle != expected:
        raise ValueError("Artifact differs from pinned owner rebuild")
    status = "REFUSED" if not candidate["public"] or candidate["withdrawn"] else "RESOLVE_CANDIDATE" if candidate["reference"] == manifest["locator"] else "HOLD_UNRESOLVED"
    return {"id": candidate["id"], "status": status,
            "revivalAddress": manifest["revivalAddress"] if status == "RESOLVE_CANDIDATE" else None,
            "artifactSha256": manifest["artifactSha256"] if status == "RESOLVE_CANDIDATE" else None,
            "effect": "NONE", "authority": "NONE"}


def write_bundle(bundle: dict[str, Any], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    for name, value in (("manifest.json", bundle["manifest"]), ("world.json", bundle["world"])):
        (directory / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (directory / "genesis-world.html").write_text(bundle["html"], encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["build", "verify"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source-commit", default=SOURCE_PIN)
    parser.add_argument("--reference", default="Gen.1.1")
    args = parser.parse_args()
    bundle = build_door(args.root, args.reference, args.source_commit)
    if args.mode == "build":
        write_bundle(bundle, args.directory)
    else:
        for name, key in (("manifest.json", "manifest"), ("world.json", "world")):
            if json.loads((args.directory / name).read_text()) != bundle[key]:
                raise ValueError(f"Cold rebuild mismatch: {name}")
        if (args.directory / "genesis-world.html").read_bytes() != bundle["html"].encode("utf-8"):
            raise ValueError("Cold rebuild mismatch: HTML")
    print(json.dumps({"status": "BUILT" if args.mode == "build" else "COLD_REBUILD_VERIFIED",
                      "artifactSha256": bundle["manifest"]["artifactSha256"],
                      "revivalAddress": bundle["manifest"]["revivalAddress"], "effect": "NONE"}))


if __name__ == "__main__":
    main()
