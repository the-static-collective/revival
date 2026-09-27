"""Standalone Aleph-Tav learning Atlas for Revival."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any

from .aleph_tav import (
    build_aleph_tav_instrument,
    open_aleph_tav_room,
)
from .corpus import load_corpus_manifest
from .kernel.v1 import sha256


MODES = ("source", "operator", "letters", "hidden")


def build_aleph_tav_atlas(corpus: dict[str, Any]) -> dict[str, Any]:
    instrument = build_aleph_tav_instrument(corpus)
    if not instrument["occurrences"]:
        raise ValueError("corpus has no Aleph-Tav instrument occurrences")

    locator = instrument["occurrences"][0]["locator"]
    specimen = corpus["_specimens_by_locator"][locator]
    occurrence_by_token = {
        item["token_id"]: item for item in instrument["occurrences"]
        if item["locator"] == locator
    }

    builds: dict[str, dict[str, Any]] = {}
    for mode in MODES:
        pieces: list[str] = []
        token_trace: list[dict[str, Any]] = []
        for token in specimen["tokens"]:
            occurrence = occurrence_by_token.get(token["id"])
            rendered = (
                occurrence["projection_examples"][mode]
                if occurrence
                else token["surface"]
            )
            if rendered:
                pieces.append(rendered)
            token_trace.append(
                {
                    "token_id": token["id"],
                    "source_surface": token["surface"],
                    "rendered": rendered,
                    "aleph_tav_occurrence": occurrence is not None,
                }
            )
        builds[mode] = {
            "mode": mode,
            "text": " ".join(pieces),
            "trace": token_trace,
            "authority": "revival-008-pedagogical-lens",
        }

    rooms: dict[str, Any] = {}
    room_receipts: dict[str, Any] = {}
    for occurrence in instrument["occurrences"]:
        key = occurrence["locator"] + "::" + occurrence["token_id"]
        opened = open_aleph_tav_room(
            instrument,
            occurrence["locator"],
            occurrence["token_id"],
        )
        rooms[key] = opened["room"]
        room_receipts[key] = opened["receipt"]

    atlas_core = {
        "kind": "aleph-tav-learning-atlas",
        "corpus_id": corpus["id"],
        "corpus_sha256": corpus["corpus_sha256"],
        "family_id": instrument["family_id"],
        "family_sha256": instrument["family_sha256"],
        "focus_locator": locator,
        "source_tokens": [
            {
                "token_id": token["id"],
                "surface": token["surface"],
                "is_aleph_tav": token["id"] in occurrence_by_token,
            }
            for token in specimen["tokens"]
        ],
        "builds": builds,
        "rooms": rooms,
        "room_receipts": room_receipts,
        "morphology_authority": instrument["morphology_authority"],
    }

    receipt = {
        "kind": "aleph-tav-learning-atlas",
        "corpus_sha256": corpus["corpus_sha256"],
        "family_sha256": instrument["family_sha256"],
        "rooms_sha256": sha256(room_receipts),
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


def render_aleph_tav_atlas_html(result: dict[str, Any]) -> str:
    atlas = result["atlas"]
    payload = _safe_json(result)
    title = escape("Revival · Aleph-Tav Instrument")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ font-family:Georgia,Cambria,serif; line-height:1.5; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#0f0f0d; color:#f3eee1; }}
button {{ font:inherit; }}
main {{ max-width:1120px; margin:auto; padding:28px 18px 60px; }}
header {{ border-bottom:1px solid #595349; padding-bottom:18px; }}
.eyebrow,.meta,pre {{ font-family:ui-monospace,Consolas,monospace; }}
.eyebrow {{ text-transform:uppercase; letter-spacing:.12em; font-size:.76rem; color:#bbb3a3; }}
.floor {{ display:flex; flex-wrap:wrap; gap:8px; font-size:1.6rem; padding:24px 0; }}
.token {{ border:0; background:transparent; color:#f3eee1; padding:.15em .25em; }}
.token.instrument {{ border:1px solid #958970; border-radius:999px; cursor:pointer; }}
.token.instrument:focus-visible,.door:focus-visible,.mode:focus-visible {{ outline:2px solid #e4dac5; outline-offset:2px; }}
.builds {{ border:1px solid #595349; border-radius:14px; padding:16px; background:#171613; margin-bottom:18px; }}
.mode-row,.doors {{ display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 14px; }}
.mode,.door {{ border:1px solid #6a6358; border-radius:9px; background:#211f1b; color:#fffaf0; padding:7px 10px; cursor:pointer; }}
.mode.active {{ outline:2px solid #e4dac5; }}
.build-text {{ font-size:1.45rem; direction:rtl; unicode-bidi:plaintext; padding:12px 0; }}
.grid {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(300px,.9fr); gap:18px; }}
.card {{ border:1px solid #595349; border-radius:14px; padding:18px; background:#171613; }}
.source {{ font-size:2rem; direction:rtl; unicode-bidi:plaintext; }}
.big {{ font-size:1.5rem; }}
.layers {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.layer {{ border:1px solid #4e4a43; border-radius:10px; padding:12px; }}
.meta {{ font-size:.83rem; color:#c5bdad; overflow-wrap:anywhere; }}
.boundary {{ border-left:3px solid #968c77; padding-left:10px; }}
@media(max-width:760px) {{ .grid,.layers {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">Revival 008 · Aleph/Tav Instrument</div>
<h1>See what English can make invisible</h1>
<div class="meta" id="identity"></div>
</header>

<section>
<div class="eyebrow" style="margin-top:24px">Source-backed floor · Genesis 1:1</div>
<div class="floor" id="floor"></div>
</section>

<section class="builds">
<div class="eyebrow">Projection instrument</div>
<div class="mode-row" id="modes"></div>
<div class="build-text" id="build-text"></div>
<div class="meta" id="build-note"></div>
</section>

<section class="grid">
<article class="card" aria-live="polite">
<div class="eyebrow">Open Aleph-Tav room</div>
<h2 id="room-title"></h2>
<div class="source" id="source"></div>
<div class="meta" id="declared"></div>

<div class="layers">
<div class="layer"><div class="eyebrow">Read</div><div class="big" id="read"></div><div class="meta">learner hint, not OSHB data</div></div>
<div class="layer"><div class="eyebrow">Letters</div><div class="big" id="letters"></div><div class="meta" id="letter-names"></div></div>
<div class="layer"><div class="eyebrow">Grammar</div><div class="big" id="grammar"></div><div class="meta">decoded from pinned OSHB morphology codes</div></div>
<div class="layer"><div class="eyebrow">Immediate context</div><div class="big" id="target"></div><div class="meta">next source token only; not a full syntax parse</div></div>
</div>

<h3>Morpheme decomposition</h3>
<pre id="decomposition"></pre>

<h3>Aleph-Tav constellation</h3>
<div class="doors" id="constellation"></div>
</article>

<aside class="card">
<div class="eyebrow">Boundary / receipt</div>
<h3>What this instrument earned</h3>
<p>The family bridge joins an OSHB morpheme only when its aligned lemma component is <code>853</code> and its morphology decodes as Particle / direct object marker.</p>
<h3>What it did not earn</h3>
<p class="boundary">Aleph is the first Hebrew letter and Tav is the last. That observation is available for later historical, symbolic, mystical, theological, or creative layers. It is not encoded here as the grammatical meaning of the particle.</p>
<h3>Room receipt</h3>
<div class="meta" id="room-receipt"></div>
<h3>Atlas receipt</h3>
<div class="meta" id="atlas-receipt"></div>
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
  var currentKey = Object.keys(rooms)[0];

  function el(id) {{ return document.getElementById(id); }}
  function key(locator, tokenId) {{ return locator + "::" + tokenId; }}

  el("identity").textContent =
    atlas.family_id + " · corpus " + atlas.corpus_sha256;

  atlas.source_tokens.forEach(function (token) {{
    var node = document.createElement(token.is_aleph_tav ? "button" : "span");
    node.className = "token" + (token.is_aleph_tav ? " instrument" : "");
    node.textContent = token.surface;
    if (token.is_aleph_tav) {{
      node.type = "button";
      node.addEventListener("click", function () {{
        openRoom(key(atlas.focus_locator, token.token_id));
      }});
    }}
    el("floor").appendChild(node);
  }});

  Object.keys(atlas.builds).forEach(function (mode) {{
    var button = document.createElement("button");
    button.type = "button";
    button.className = "mode";
    button.textContent = mode;
    button.dataset.mode = mode;
    button.addEventListener("click", function () {{ showBuild(mode); }});
    el("modes").appendChild(button);
  }});

  function showBuild(mode) {{
    var build = atlas.builds[mode];
    el("build-text").textContent = build.text || "∅";
    el("build-note").textContent =
      mode === "hidden"
        ? "Pedagogical visibility experiment: marker components are suppressed; this is not an English translation."
        : "Pedagogical projection only; the source-backed witness is unchanged.";
    document.querySelectorAll(".mode").forEach(function (node) {{
      node.classList.toggle("active", node.dataset.mode === mode);
    }});
  }}

  function openRoom(roomKey) {{
    var room = rooms[roomKey];
    if (!room) return;
    currentKey = roomKey;
    var o = room.occurrence;
    var marker = o.marker_component;

    el("room-title").textContent = o.locator + " · " + o.token_id;
    el("source").textContent = o.source_surface;
    el("declared").textContent =
      "OSHB lemma " + o.declared_lemma + " · morph " + o.declared_morph;
    el("read").textContent = o.reading.component_hint;
    el("letters").textContent = o.letters.unpointed;
    el("letter-names").textContent = o.letters.names.join(" + ");
    el("grammar").textContent =
      o.grammar.part_of_speech + " · " + o.grammar.particle_type;
    el("target").textContent =
      o.next_token_context ? o.next_token_context.source_surface : "none";
    el("decomposition").textContent =
      JSON.stringify(o.decomposition.parts, null, 2);

    var doors = el("constellation");
    doors.replaceChildren();
    room.constellation_doors.forEach(function (door) {{
      var button = document.createElement("button");
      button.type = "button";
      button.className = "door";
      button.textContent =
        door.destination_source_surface + " · lemma " +
        door.destination_declared_lemma;
      button.addEventListener("click", function () {{
        openRoom(key(door.destination_locator, door.destination_token_id));
      }});
      doors.appendChild(button);
    }});
    if (!doors.childElementCount) {{
      doors.textContent = "No other derived-family occurrence in this proof corpus.";
    }}

    el("room-receipt").textContent =
      "projection " + atlas.room_receipts[roomKey].projection_sha256;
    el("atlas-receipt").textContent =
      "projection " + result.receipt.projection_sha256;
  }}

  showBuild("source");
  openRoom(currentKey);
}})();
</script>
</body>
</html>
"""


def build_aleph_tav_atlas_html(
    corpus: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    result = build_aleph_tav_atlas(corpus)
    return result, render_aleph_tav_atlas_html(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.aleph_tav_atlas",
        description="Build the standalone Revival Aleph-Tav learning Atlas.",
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    corpus = load_corpus_manifest(args.manifest, root=args.root)
    result, html = build_aleph_tav_atlas_html(corpus)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(
        json.dumps(
            {
                "output": str(args.output),
                "family_id": result["atlas"]["family_id"],
                "family_sha256": result["atlas"]["family_sha256"],
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
