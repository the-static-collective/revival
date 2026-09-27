"""Standalone multi-witness Corpus Atlas for Revival."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any

from .corpus import load_corpus_manifest, open_corpus_token_room
from .kernel.v1 import sha256
from .linguistic import compile_linguistic_projection


def build_corpus_atlas(corpus: dict[str, Any]) -> dict[str, Any]:
    """Compose every corpus witness and token room into one walkable atlas."""
    specimens = corpus.get("_specimens_by_locator", {})
    verses: list[dict[str, Any]] = []
    rooms: dict[str, Any] = {}
    local_receipts: dict[str, Any] = {}
    corpus_receipts: dict[str, Any] = {}

    for witness in corpus["witnesses"]:
        locator = witness["locator"]
        specimen = specimens[locator]
        compiled = compile_linguistic_projection(
            specimen,
            corpus["recipe_id"],
        )
        trace = compiled["projection"]["content"]["trace"]
        verses.append(
            {
                "locator": locator,
                "witness_id": witness["witness_id"],
                "compiled_text": compiled["projection"]["content"]["text"],
                "trace": trace,
                "compiled_projection_receipt": compiled["receipt"],
            }
        )

        for item in trace:
            token_id = item["token_id"]
            key = f"{locator}::{token_id}"
            opened = open_corpus_token_room(corpus, locator, token_id)
            rooms[key] = opened["room"]
            local_receipts[key] = opened["local_room_receipt"]
            corpus_receipts[key] = opened["corpus_receipt"]

    atlas_core = {
        "kind": "corpus-curiosity-atlas",
        "corpus_id": corpus["id"],
        "corpus_sha256": corpus["corpus_sha256"],
        "recipe_id": corpus["recipe_id"],
        "verses": verses,
        "rooms": rooms,
        "local_room_receipts": local_receipts,
        "corpus_room_receipts": corpus_receipts,
    }

    receipt = {
        "kind": "corpus-curiosity-atlas",
        "corpus_sha256": corpus["corpus_sha256"],
        "rooms_sha256": sha256(corpus_receipts),
        "projection_sha256": sha256(atlas_core),
    }
    return {
        "atlas": atlas_core,
        "receipt": receipt,
    }


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


def render_corpus_atlas_html(result: dict[str, Any]) -> str:
    atlas = result["atlas"]
    payload = _safe_json(result)
    title = escape("Revival · " + atlas["corpus_id"])

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
main {{ max-width:1120px; margin:auto; padding:28px 18px 60px; }}
header {{ border-bottom:1px solid #575249; padding-bottom:18px; }}
.eyebrow,.meta,pre {{ font-family:ui-monospace,Consolas,monospace; }}
.eyebrow {{ color:#bcb5a5; text-transform:uppercase; letter-spacing:.12em; font-size:.76rem; }}
.verse-card,.room {{ border:1px solid #575249; border-radius:14px; padding:16px; background:#171613; }}
.verses {{ display:grid; gap:12px; margin:24px 0; }}
.verse {{ display:flex; flex-wrap:wrap; gap:8px; font-size:1.45rem; margin-top:8px; }}
.token,.door {{ border:1px solid #6b655a; background:#211f1b; color:#fffaf0; cursor:pointer; }}
.token {{ border-radius:999px; padding:.18em .48em; }}
.door {{ border-radius:9px; padding:7px 9px; }}
.token.active,.token:focus-visible,.door:focus-visible {{ outline:2px solid #ddd4bf; outline-offset:2px; }}
.room-grid {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(280px,.8fr); gap:18px; }}
.source {{ font-size:2rem; direction:rtl; unicode-bidi:plaintext; }}
.rendered {{ font-size:1.55rem; }}
.doors,.trail {{ display:flex; flex-wrap:wrap; gap:7px; margin:8px 0 16px; }}
.trail button {{ border:0; background:transparent; color:#ddd4bf; text-decoration:underline; cursor:pointer; }}
.meta {{ color:#c7c0b1; font-size:.84rem; overflow-wrap:anywhere; }}
.lemma {{ border-left:3px solid #938a78; padding-left:10px; }}
@media(max-width:760px) {{ .room-grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">Revival · Dangerous Lemma Doors</div>
<h1 id="corpus-title"></h1>
<div class="meta" id="corpus-hash"></div>
<div class="trail" id="trail"></div>
</header>

<section class="verses" id="verses" aria-label="Corpus verses"></section>

<section class="room-grid">
<article class="room" aria-live="polite">
<div class="eyebrow">Open room</div>
<h2 id="room-title"></h2>
<div class="meta" id="locator"></div>
<div class="source" id="source"></div>
<div class="rendered" id="rendered"></div>

<h3>Lemma</h3>
<div class="lemma">
<div class="meta" id="lemma-rule"></div>
<div id="lemma-value"></div>
</div>

<h3>Dangerous lemma doors</h3>
<div class="doors" id="lemma-doors"></div>

<h3>Source neighbors</h3>
<div class="doors" id="source-neighbors"></div>

<h3>Declared layers</h3>
<pre id="layers"></pre>
</article>

<aside class="room">
<div class="eyebrow">Receipts</div>
<h3>Local witness room</h3>
<div class="meta" id="local-receipt"></div>
<h3>Corpus room</h3>
<div class="meta" id="corpus-room-receipt"></div>
<h3>Corpus Atlas</h3>
<div class="meta" id="atlas-receipt"></div>
<p class="meta">Lemma doors use exact declared lemma-string identity in the pinned corpus. Same-lemma traversal is navigation, not a claim that every occurrence has the same meaning, referent, syntax, or theology.</p>
</aside>
</section>
</main>

<script id="revival-data" type="application/json">{payload}</script>
<script>
(function () {{
  "use strict";
  var result = JSON.parse(document.getElementById("revival-data").textContent);
  var atlas = result.atlas;
  var rooms = atlas.rooms;
  var trail = [];
  var currentKey = null;

  function el(id) {{ return document.getElementById(id); }}
  function roomKey(locator, tokenId) {{ return locator + "::" + tokenId; }}

  el("corpus-title").textContent = atlas.corpus_id;
  el("corpus-hash").textContent = "corpus " + atlas.corpus_sha256;

  atlas.verses.forEach(function (verse) {{
    var card = document.createElement("article");
    card.className = "verse-card";

    var heading = document.createElement("div");
    heading.className = "eyebrow";
    heading.textContent = verse.locator;
    card.appendChild(heading);

    var floor = document.createElement("div");
    floor.className = "verse";

    verse.trace.filter(function (item) {{
      return item.rendered !== "";
    }}).forEach(function (item) {{
      var button = document.createElement("button");
      button.type = "button";
      button.className = "token";
      button.dataset.roomKey = roomKey(verse.locator, item.token_id);
      button.textContent = item.rendered;
      button.addEventListener("click", function () {{
        openRoom(button.dataset.roomKey, true);
      }});
      floor.appendChild(button);
    }});

    card.appendChild(floor);
    el("verses").appendChild(card);
  }});

  function addDoor(container, label, locator, tokenId, title) {{
    var button = document.createElement("button");
    button.type = "button";
    button.className = "door";
    button.textContent = label;
    if (title) button.title = title;
    button.addEventListener("click", function () {{
      openRoom(roomKey(locator, tokenId), true);
    }});
    container.appendChild(button);
  }}

  function renderTrail() {{
    var container = el("trail");
    container.replaceChildren();
    trail.forEach(function (key, index) {{
      var room = rooms[key];
      var button = document.createElement("button");
      button.type = "button";
      button.textContent = room.witness_locator + " · " +
        (room.token.current_rendering || room.token.source_surface);
      button.addEventListener("click", function () {{ openRoom(key, false); }});
      container.appendChild(button);
      if (index < trail.length - 1) {{
        var arrow = document.createElement("span");
        arrow.textContent = "→";
        container.appendChild(arrow);
      }}
    }});
  }}

  function renderSourceNeighbors(room) {{
    var container = el("source-neighbors");
    container.replaceChildren();
    Object.keys(room.neighbors.source).forEach(function (direction) {{
      var item = room.neighbors.source[direction];
      if (!item) return;
      addDoor(
        container,
        direction + " · " + (item.rendered || item.source_surface),
        room.witness_locator,
        item.token_id,
        item.source_surface
      );
    }});
    if (!container.childElementCount) container.textContent = "No neighboring door.";
  }}

  function openRoom(key, appendTrail) {{
    if (!rooms[key]) return;
    currentKey = key;
    var room = rooms[key];

    if (appendTrail && trail[trail.length - 1] !== key) trail.push(key);
    if (!trail.length) trail.push(key);
    renderTrail();

    document.querySelectorAll(".token").forEach(function (node) {{
      node.classList.toggle("active", node.dataset.roomKey === key);
    }});

    el("room-title").textContent =
      room.token.current_rendering || "(empty rendering)";
    el("locator").textContent =
      room.witness_locator + " · token " + room.token.id;
    el("source").textContent = room.token.source_surface;
    el("rendered").textContent =
      "current: " + (room.token.current_rendering || "∅");
    el("layers").textContent =
      JSON.stringify(room.token.annotations, null, 2);

    el("lemma-rule").textContent =
      room.lemma.identity_rule;
    el("lemma-value").textContent =
      room.lemma.value === null ? "no indexed lemma" : room.lemma.value;

    var lemmaDoors = el("lemma-doors");
    lemmaDoors.replaceChildren();
    room.corpus_doors.forEach(function (door) {{
      addDoor(
        lemmaDoors,
        door.destination_locator + " · " + door.destination_source_surface,
        door.destination_locator,
        door.destination_token_id,
        "lemma " + door.lemma + " · " +
          (door.destination_morph || "morphology unavailable")
      );
    }});
    if (!lemmaDoors.childElementCount) {{
      lemmaDoors.textContent = "No other exact-lemma occurrence in this corpus.";
    }}

    renderSourceNeighbors(room);

    el("local-receipt").textContent =
      "projection " + atlas.local_room_receipts[key].projection_sha256;
    el("corpus-room-receipt").textContent =
      "projection " + atlas.corpus_room_receipts[key].projection_sha256;
    el("atlas-receipt").textContent =
      "projection " + result.receipt.projection_sha256;
  }}

  if (atlas.verses.length && atlas.verses[0].trace.length) {{
    openRoom(
      roomKey(atlas.verses[0].locator, atlas.verses[0].trace[0].token_id),
      true
    );
  }}
}})();
</script>
</body>
</html>
"""


def build_corpus_atlas_html(corpus: dict[str, Any]) -> tuple[dict[str, Any], str]:
    result = build_corpus_atlas(corpus)
    return result, render_corpus_atlas_html(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.corpus_atlas",
        description="Build a standalone multi-witness Revival Corpus Atlas.",
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    corpus = load_corpus_manifest(args.manifest, root=args.root)
    result, html = build_corpus_atlas_html(corpus)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(
        json.dumps(
            {
                "output": str(args.output),
                "corpus_id": corpus["id"],
                "corpus_sha256": corpus["corpus_sha256"],
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
