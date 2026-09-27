"""Standalone object-relation learning Atlas for Revival 009."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any

from .corpus import open_corpus_token_room
from .kernel.v1 import sha256
from .object_relations import (
    load_object_relation_instrument,
    open_object_relation_room,
)


def build_object_relation_atlas(
    corpus: dict[str, Any],
    instrument: dict[str, Any],
) -> dict[str, Any]:
    locator = "Gen.1.1"
    specimen = corpus["_specimens_by_locator"].get(locator)
    if specimen is None:
        raise ValueError("object-relation Atlas requires Gen.1.1")

    local_rooms: dict[str, Any] = {}
    local_receipts: dict[str, Any] = {}
    for token in specimen["tokens"]:
        key = locator + "::" + token["id"]
        opened = open_corpus_token_room(corpus, locator, token["id"])
        local_rooms[key] = opened["room"]
        local_receipts[key] = opened["corpus_receipt"]

    relation_rooms: dict[str, Any] = {}
    relation_receipts: dict[str, Any] = {}
    marker_ids: set[str] = set()
    for occurrence in instrument["occurrences"]:
        if occurrence["object_relation"] is None:
            continue
        key = occurrence["locator"] + "::" + occurrence["token_id"]
        opened = open_object_relation_room(
            corpus,
            instrument,
            occurrence["locator"],
            occurrence["token_id"],
        )
        relation_rooms[key] = opened["room"]
        relation_receipts[key] = opened["receipt"]
        marker_ids.add(occurrence["token_id"])

    atlas_core = {
        "kind": "object-relation-atlas",
        "focus_locator": locator,
        "corpus_id": corpus["id"],
        "corpus_sha256": corpus["corpus_sha256"],
        "instrument_sha256": instrument["instrument_sha256"],
        "macula_source_id": instrument["macula_source_id"],
        "macula_layer_sha256": instrument["macula_layer_sha256"],
        "source_tokens": [
            {
                "token_id": token["id"],
                "surface": token["surface"],
                "is_object_marker": token["id"] in marker_ids,
            }
            for token in specimen["tokens"]
        ],
        "local_rooms": local_rooms,
        "local_receipts": local_receipts,
        "relation_rooms": relation_rooms,
        "relation_receipts": relation_receipts,
    }
    receipt = {
        "kind": "object-relation-atlas",
        "corpus_sha256": corpus["corpus_sha256"],
        "instrument_sha256": instrument["instrument_sha256"],
        "macula_layer_sha256": instrument["macula_layer_sha256"],
        "local_rooms_sha256": sha256(local_receipts),
        "relation_rooms_sha256": sha256(relation_receipts),
        "projection_sha256": sha256(atlas_core),
    }
    return {"atlas": atlas_core, "receipt": receipt}


def _safe_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    slash = chr(92)
    return (
        encoded.replace("&", slash + "u0026")
        .replace("<", slash + "u003c")
        .replace(">", slash + "u003e")
        .replace(chr(0x2028), slash + "u2028")
        .replace(chr(0x2029), slash + "u2029")
    )


def render_object_relation_atlas_html(result: dict[str, Any]) -> str:
    atlas = result["atlas"]
    payload = _safe_json(result)
    title = escape("Revival · Object Relations")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ font-family:Georgia,Cambria,serif; line-height:1.5; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#10100e; color:#f4efe2; }}
button {{ font:inherit; }}
main {{ max-width:1140px; margin:auto; padding:28px 18px 60px; }}
header {{ border-bottom:1px solid #575249; padding-bottom:18px; }}
.eyebrow,.meta,pre {{ font-family:ui-monospace,Consolas,monospace; }}
.eyebrow {{ color:#bbb3a3; text-transform:uppercase; letter-spacing:.12em; font-size:.76rem; }}
.floor {{ display:flex; flex-wrap:wrap; gap:8px; font-size:1.65rem; padding:26px 0; }}
.token,.door {{ border:1px solid #6b655a; background:#211f1b; color:#fffaf0; cursor:pointer; }}
.token {{ border-radius:999px; padding:.18em .5em; }}
.token.marker {{ outline:2px solid #9a8b6e; outline-offset:2px; }}
.door {{ border-radius:9px; padding:7px 10px; }}
.token:focus-visible,.door:focus-visible {{ outline:2px solid #e4dac5; outline-offset:2px; }}
.grid {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(300px,.88fr); gap:18px; }}
.card {{ border:1px solid #575249; border-radius:14px; padding:18px; background:#171613; }}
.source {{ font-size:2rem; direction:rtl; unicode-bidi:plaintext; }}
.doors {{ display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 16px; }}
.relation-map {{ font-size:1.25rem; border-left:3px solid #968c77; padding:10px 0 10px 12px; white-space:pre-wrap; }}
.evidence {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
.evidence > div {{ border:1px solid #4f4a42; border-radius:10px; padding:10px; }}
.meta {{ font-size:.83rem; color:#c7c0b1; overflow-wrap:anywhere; }}
.boundary {{ border-left:3px solid #766f63; padding-left:10px; }}
@media(max-width:760px) {{ .grid,.evidence {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">Revival 009 · Object Relations</div>
<h1>From marker to actual attributed structure</h1>
<div class="meta" id="identity"></div>
</header>

<section>
<div class="eyebrow" style="margin-top:24px">Source-backed floor · Genesis 1:1</div>
<div class="floor" id="floor"></div>
</section>

<section class="grid">
<article class="card" aria-live="polite">
<div class="eyebrow">Open token</div>
<h2 id="room-title"></h2>
<div class="source" id="source"></div>
<div class="meta" id="token-meta"></div>

<div id="relation-panel" hidden>
<h3>Object relation</h3>
<div class="relation-map" id="relation-map"></div>

<h3>Doors</h3>
<div class="doors" id="relation-doors"></div>

<h3>Evidence stays split</h3>
<div class="evidence">
<div><div class="eyebrow">Syntax tree</div><pre id="syntax-evidence"></pre></div>
<div><div class="eyebrow">Semantic frame</div><pre id="frame-evidence"></pre></div>
</div>
</div>

<h3>Declared source layers</h3>
<pre id="layers"></pre>
</article>

<aside class="card">
<div class="eyebrow">Boundary / receipts</div>
<p class="boundary"><strong>009 removes the adjacency shortcut.</strong> The marked-phrase claim comes from pinned MACULA syntax, not from “whatever token comes next.”</p>
<p class="boundary">The verb's A1 frame is separate semantic-frame evidence. Syntax role and semantic role may agree here without becoming the same assertion.</p>
<h3>Local token room</h3>
<div class="meta" id="local-receipt"></div>
<h3>Object relation room</h3>
<div class="meta" id="relation-receipt"></div>
<h3>Atlas</h3>
<div class="meta" id="atlas-receipt"></div>
<p class="meta">MACULA attribution: MACULA Hebrew Linguistic Datasets, available at https://github.com/Clear-Bible/macula-hebrew/ · CC BY 4.0.</p>
</aside>
</section>
</main>

<script id="revival-data" type="application/json">{payload}</script>
<script>
(function () {{
  "use strict";
  var result = JSON.parse(document.getElementById("revival-data").textContent);
  var atlas = result.atlas;
  var localRooms = atlas.local_rooms;
  var relationRooms = atlas.relation_rooms;
  var locator = atlas.focus_locator;

  function el(id) {{ return document.getElementById(id); }}
  function key(tokenId) {{ return locator + "::" + tokenId; }}

  el("identity").textContent =
    atlas.macula_source_id + " · OSHB corpus " + atlas.corpus_sha256;

  atlas.source_tokens.forEach(function (token) {{
    var button = document.createElement("button");
    button.type = "button";
    button.className = "token" + (token.is_object_marker ? " marker" : "");
    button.textContent = token.surface;
    button.addEventListener("click", function () {{
      openToken(token.token_id);
    }});
    el("floor").appendChild(button);
  }});

  function addDoor(container, door) {{
    var button = document.createElement("button");
    button.type = "button";
    button.className = "door";
    button.textContent = door.label + " → " + door.destination_token_id;
    button.title = door.evidence_layer + " · " + door.source;
    button.addEventListener("click", function () {{
      openToken(door.destination_token_id);
    }});
    container.appendChild(button);
  }}

  function openToken(tokenId) {{
    var roomKey = key(tokenId);
    var local = localRooms[roomKey];
    if (!local) return;

    el("room-title").textContent = tokenId;
    el("source").textContent = local.token.source_surface;
    el("token-meta").textContent =
      locator + " · source span " +
      local.token.source_span[0] + ":" + local.token.source_span[1];
    el("layers").textContent =
      JSON.stringify(local.token.annotations, null, 2);
    el("local-receipt").textContent =
      "projection " + atlas.local_receipts[roomKey].projection_sha256;
    el("atlas-receipt").textContent =
      "projection " + result.receipt.projection_sha256;

    var relation = relationRooms[roomKey];
    var panel = el("relation-panel");
    if (!relation) {{
      panel.hidden = true;
      el("relation-receipt").textContent =
        "No MACULA object-marker relation on this token.";
      return;
    }}

    panel.hidden = false;
    var r = relation.object_relation;
    var verb = r.governing_verb.source_surface;
    var marker = r.marker.source_surface;
    var phrase = r.marked_phrase.source_surfaces.join(" ");
    el("relation-map").textContent =
      verb + "  ← governing verb\n" +
      "  │\n" +
      "  └─ " + marker + "  →  " + phrase;

    var doors = el("relation-doors");
    doors.replaceChildren();
    relation.doors.forEach(function (door) {{
      addDoor(doors, door);
    }});

    el("syntax-evidence").textContent =
      JSON.stringify(relation.evidence_separation.syntax_evidence, null, 2);
    el("frame-evidence").textContent =
      JSON.stringify(relation.evidence_separation.semantic_frame_evidence, null, 2);
    el("relation-receipt").textContent =
      "projection " + atlas.relation_receipts[roomKey].projection_sha256;
  }}

  if (atlas.source_tokens.length) {{
    var firstMarker = atlas.source_tokens.find(function (item) {{
      return item.is_object_marker;
    }});
    openToken((firstMarker || atlas.source_tokens[0]).token_id);
  }}
}})();
</script>
</body>
</html>
"""


def build_object_relation_atlas_html(
    corpus: dict[str, Any],
    instrument: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    result = build_object_relation_atlas(corpus, instrument)
    return result, render_object_relation_atlas_html(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.object_relations_atlas",
        description="Build the standalone Revival object-relation Atlas.",
    )
    parser.add_argument("corpus_manifest", type=Path)
    parser.add_argument("--macula-xml", required=True, type=Path)
    parser.add_argument("--macula-manifest", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    corpus, instrument = load_object_relation_instrument(
        args.corpus_manifest,
        args.macula_xml,
        args.macula_manifest,
        root=args.root,
    )
    result, html = build_object_relation_atlas_html(corpus, instrument)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(
        json.dumps(
            {
                "output": str(args.output),
                "instrument_sha256": instrument["instrument_sha256"],
                "atlas_receipt": result["receipt"],
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2 if args.pretty else None,
            separators=None if args.pretty else (",", ":"),
        )
    )


if __name__ == "__main__":
    main()
