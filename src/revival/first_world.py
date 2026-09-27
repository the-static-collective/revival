"""Revival 010: compose proven Scripture instruments into one walkable world.

This module does not change frozen kernel v1. It composes the receipted corpus,
Aleph-Tav, and object-relation instruments into one deterministic presentation
surface where projections, relation layers, traversal, and epistemic boundaries
can coexist without being collapsed into one authority.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any

from .aleph_tav_atlas import build_aleph_tav_atlas
from .corpus_atlas import build_corpus_atlas
from .kernel.v1 import sha256
from .object_relations import load_object_relation_instrument
from .object_relations_atlas import build_object_relation_atlas


PROJECTION_MODES = ("source", "operator", "letters", "hidden")


def _room_key(locator: str, token_id: str) -> str:
    return f"{locator}::{token_id}"


def _source_neighbor_doors(room: dict[str, Any]) -> list[dict[str, Any]]:
    doors: list[dict[str, Any]] = []
    for direction, item in room["neighbors"]["source"].items():
        if item is None:
            continue
        doors.append(
            {
                "kind": "source-neighbor",
                "label": f"source {direction}",
                "destination_locator": room["witness_locator"],
                "destination_token_id": item["token_id"],
                "destination_source_surface": item["source_surface"],
                "evidence_layer": "source order",
                "epistemic_status": "source-backed",
            }
        )
    return doors


def _lemma_doors(room: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            **door,
            "label": "exact lemma occurrence",
            "evidence_layer": "declared OSHB lemma identity",
            "epistemic_status": "derived",
        }
        for door in room["corpus_doors"]
    ]


def _aleph_tav_doors(room: dict[str, Any] | None) -> list[dict[str, Any]]:
    if room is None:
        return []
    return [
        {
            **door,
            "label": "Aleph-Tav family occurrence",
            "evidence_layer": "derived OSHB morpheme family",
            "epistemic_status": "derived",
        }
        for door in room["constellation_doors"]
    ]


def _relation_doors(room: dict[str, Any] | None) -> list[dict[str, Any]]:
    if room is None:
        return []
    return [
        {
            **door,
            "destination_source_surface": None,
            "epistemic_status": "attributed",
        }
        for door in room["doors"]
    ]


def _layer_state(
    local_room: dict[str, Any],
    aleph_room: dict[str, Any] | None,
    relation_room: dict[str, Any] | None,
) -> dict[str, Any]:
    lemma_available = local_room["lemma"]["value"] is not None
    syntax_available = relation_room is not None
    return {
        "source": {
            "status": "source-backed",
            "available": True,
            "note": "Held witness token, span, and source order.",
        },
        "lemma": {
            "status": "attributed" if lemma_available else "unsupported",
            "available": lemma_available,
            "note": (
                "Exact declared OSHB lemma identity."
                if lemma_available
                else "No declared lemma is available for this token."
            ),
        },
        "aleph_tav": {
            "status": "derived" if aleph_room is not None else "unsupported",
            "available": aleph_room is not None,
            "note": (
                "Derived only when aligned OSHB morphemes earn family membership."
                if aleph_room is not None
                else "This token is not in the derived Aleph-Tav proof family."
            ),
        },
        "syntax": {
            "status": "attributed" if syntax_available else "unsupported",
            "available": syntax_available,
            "note": (
                "Pinned MACULA syntax evidence is attached to this marker room."
                if syntax_available
                else "No promoted MACULA object relation is attached to this token."
            ),
        },
        "semantic_frame": {
            "status": "attributed" if syntax_available else "unsupported",
            "available": syntax_available,
            "note": (
                "Pinned MACULA semantic-frame evidence remains separate from syntax."
                if syntax_available
                else "No promoted semantic-frame relation is attached to this token."
            ),
        },
        "interpretation": {
            "status": "fog",
            "available": False,
            "note": (
                "Revival 010 does not manufacture an interpretive door. "
                "Symbolic or theological proposals must enter through a separately "
                "attributed downstream layer."
            ),
        },
    }


def build_first_world(
    corpus: dict[str, Any],
    object_relation_instrument: dict[str, Any],
) -> dict[str, Any]:
    """Compose Revival 007-009 into the first unified world surface."""
    corpus_result = build_corpus_atlas(corpus)
    aleph_result = build_aleph_tav_atlas(corpus)
    relation_result = build_object_relation_atlas(
        corpus,
        object_relation_instrument,
    )

    corpus_atlas = corpus_result["atlas"]
    aleph_atlas = aleph_result["atlas"]
    relation_atlas = relation_result["atlas"]

    identities = {
        corpus_atlas["corpus_sha256"],
        aleph_atlas["corpus_sha256"],
        relation_atlas["corpus_sha256"],
    }
    if identities != {corpus["corpus_sha256"]}:
        raise ValueError("child Atlases do not share one corpus identity")

    projections: dict[str, Any] = {}
    for mode in PROJECTION_MODES:
        passages: list[dict[str, Any]] = []
        for verse in corpus_atlas["verses"]:
            if verse["locator"] == aleph_atlas["focus_locator"]:
                build = aleph_atlas["builds"][mode]
                passages.append(
                    {
                        "locator": verse["locator"],
                        "text": build["text"],
                        "trace": build["trace"],
                        "authority": build["authority"],
                    }
                )
            else:
                passages.append(
                    {
                        "locator": verse["locator"],
                        "text": verse["compiled_text"],
                        "trace": [
                            {
                                "token_id": item["token_id"],
                                "source_surface": item["source_surface"],
                                "rendered": item["rendered"],
                                "aleph_tav_occurrence": False,
                            }
                            for item in verse["trace"]
                        ],
                        "authority": "source-backed corpus projection",
                    }
                )
        projections[mode] = passages

    rooms: dict[str, Any] = {}
    for key, local_room in corpus_atlas["rooms"].items():
        aleph_room = aleph_atlas["rooms"].get(key)
        relation_room = relation_atlas["relation_rooms"].get(key)
        doors = (
            _source_neighbor_doors(local_room)
            + _lemma_doors(local_room)
            + _aleph_tav_doors(aleph_room)
            + _relation_doors(relation_room)
        )
        rooms[key] = {
            "key": key,
            "locator": local_room["witness_locator"],
            "token_id": local_room["token"]["id"],
            "local": local_room,
            "aleph_tav": aleph_room,
            "object_relation": relation_room,
            "doors": doors,
            "layers": _layer_state(local_room, aleph_room, relation_room),
        }

    world_core = {
        "kind": "revival-first-world",
        "version": "010",
        "corpus_id": corpus["id"],
        "corpus_sha256": corpus["corpus_sha256"],
        "projection_modes": list(PROJECTION_MODES),
        "projections": projections,
        "rooms": rooms,
        "epistemic_legend": [
            {
                "status": "source-backed",
                "door": "solid",
                "meaning": "directly carried from the held source representation",
            },
            {
                "status": "attributed",
                "door": "solid-with-receipt",
                "meaning": "declared by an attributable external annotation layer",
            },
            {
                "status": "derived",
                "door": "constructed",
                "meaning": "lawfully computed from attributed inputs without rewriting them",
            },
            {
                "status": "fog",
                "door": "no-door",
                "meaning": "not promoted into a relation by this world",
            },
        ],
        "authority_boundary": [
            "source != annotation",
            "annotation != derivation",
            "derivation != interpretation",
            "syntax != semantic frame",
            "navigation != theology",
            "projection != witness",
        ],
        "child_receipts": {
            "corpus_atlas": corpus_result["receipt"],
            "aleph_tav_atlas": aleph_result["receipt"],
            "object_relation_atlas": relation_result["receipt"],
        },
    }
    receipt = {
        "kind": "revival-first-world",
        "corpus_sha256": corpus["corpus_sha256"],
        "corpus_atlas_projection_sha256": corpus_result["receipt"]["projection_sha256"],
        "aleph_tav_atlas_projection_sha256": aleph_result["receipt"]["projection_sha256"],
        "object_relation_atlas_projection_sha256": relation_result["receipt"]["projection_sha256"],
        "rooms_sha256": sha256(rooms),
        "projections_sha256": sha256(projections),
        "projection_sha256": sha256(world_core),
    }
    return {"world": world_core, "receipt": receipt}


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


def render_first_world_html(result: dict[str, Any]) -> str:
    world = result["world"]
    payload = _safe_json(result)
    title = escape("Revival 010 · The First World")

    template = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root { font-family:Georgia,Cambria,serif; line-height:1.5; }
* { box-sizing:border-box; }
body { margin:0; background:#0e0e0c; color:#f3eee1; }
button { font:inherit; }
main { max-width:1220px; margin:auto; padding:26px 18px 64px; }
header { border-bottom:1px solid #575249; padding-bottom:18px; }
.eyebrow,.meta,pre { font-family:ui-monospace,Consolas,monospace; }
.eyebrow { color:#bbb3a3; text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; }
.hero { max-width:780px; font-size:1.1rem; }
.controls,.trail,.doors,.layers { display:flex; flex-wrap:wrap; gap:8px; }
.controls { margin:18px 0; }
.control,.door,.trail button,.token {
  border:1px solid #6b655a; background:#201e1a; color:#fffaf0; cursor:pointer;
}
.control,.door { border-radius:9px; padding:7px 10px; }
.control.active { outline:2px solid #ddd4bf; outline-offset:2px; }
.trail { margin-top:12px; align-items:center; }
.trail button { border:0; background:transparent; color:#ddd4bf; text-decoration:underline; padding:0; }
.passages { display:grid; gap:12px; margin:22px 0; }
.passage { border:1px solid #575249; border-radius:14px; padding:15px; background:#161512; }
.floor { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; font-size:1.42rem; }
.token { border-radius:999px; padding:.18em .48em; }
.token.active { outline:2px solid #ddd4bf; outline-offset:2px; }
.token.marker { border-style:double; }
.token.vanished { opacity:.48; border-style:dashed; }
.grid { display:grid; grid-template-columns:minmax(0,1.2fr) minmax(300px,.8fr); gap:18px; }
.card { border:1px solid #575249; border-radius:14px; padding:17px; background:#161512; }
.source { font-size:2rem; direction:rtl; unicode-bidi:plaintext; }
.rendered { font-size:1.35rem; }
.layer {
  border:1px solid #4f4a42; border-radius:999px; padding:4px 8px;
  font-family:ui-monospace,Consolas,monospace; font-size:.78rem;
}
.layer.fog { border-style:dashed; opacity:.72; }
.door { text-align:left; }
.door.derived { border-style:dashed; }
.door.attributed { border-style:double; }
.group { margin:14px 0; }
.group h3 { margin-bottom:7px; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; font-size:.8rem; color:#d1c8b8; }
.fogbox { border:1px dashed #71695d; border-radius:12px; padding:12px; margin-top:14px; }
.boundary { border-left:3px solid #8b806e; padding-left:10px; }
@media(max-width:800px) { .grid { grid-template-columns:1fr; } }
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">Revival 010 · The First World</div>
<h1>Every object in this world knows where it came from.</h1>
<p class="hero">One walkable surface over the proven corpus, lemma, Aleph-Tav, syntax, semantic-frame, projection, receipt, and traversal layers. The layers coexist; they do not become the same authority.</p>
<div class="meta" id="identity"></div>
<div class="controls" id="projection-controls" aria-label="Projection modes"></div>
<div class="trail" id="trail"></div>
</header>

<section class="passages" id="passages" aria-label="Scripture world"></section>

<section class="grid">
<article class="card" aria-live="polite">
<div class="eyebrow">Open object</div>
<h2 id="room-title"></h2>
<div class="meta" id="room-meta"></div>
<div class="source" id="source"></div>
<div class="rendered" id="rendered"></div>

<div class="group">
<h3>Available layers</h3>
<div class="layers" id="layers"></div>
</div>

<div class="group">
<h3>Doors</h3>
<div class="doors" id="doors"></div>
</div>

<div class="group" id="aleph-panel" hidden>
<h3>Aleph-Tav learning layer</h3>
<pre id="aleph-data"></pre>
</div>

<div class="group" id="relation-panel" hidden>
<h3>Attributed object relation</h3>
<pre id="relation-data"></pre>
</div>

<div class="group">
<h3>Declared source layers</h3>
<pre id="annotations"></pre>
</div>
</article>

<aside class="card">
<div class="eyebrow">Epistemic topology</div>
<div id="legend"></div>
<div class="fogbox">
<strong>Fog is a feature.</strong>
<div class="meta" id="fog-note"></div>
</div>
<h3>Authority boundary</h3>
<pre id="boundary"></pre>
<h3>World receipt</h3>
<div class="meta" id="world-receipt"></div>
</aside>
</section>
</main>

<script id="revival-data" type="application/json">__PAYLOAD__</script>
<script>
(function () {
  "use strict";
  var result = JSON.parse(document.getElementById("revival-data").textContent);
  var world = result.world;
  var mode = "source";
  var currentKey = null;
  var trail = [];

  function el(id) { return document.getElementById(id); }
  function key(locator, tokenId) { return locator + "::" + tokenId; }

  el("identity").textContent =
    world.corpus_id + " · corpus " + world.corpus_sha256;
  el("boundary").textContent = world.authority_boundary.join("\n");
  el("world-receipt").textContent =
    "projection " + result.receipt.projection_sha256;

  world.epistemic_legend.forEach(function (item) {
    var row = document.createElement("p");
    row.className = "meta";
    row.textContent = item.status + " · " + item.door + " · " + item.meaning;
    el("legend").appendChild(row);
  });

  world.projection_modes.forEach(function (name) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "control" + (name === mode ? " active" : "");
    button.textContent = name;
    button.dataset.mode = name;
    button.addEventListener("click", function () {
      mode = name;
      document.querySelectorAll(".control").forEach(function (node) {
        node.classList.toggle("active", node.dataset.mode === mode);
      });
      renderPassages();
      if (currentKey) openRoom(currentKey, false);
    });
    el("projection-controls").appendChild(button);
  });

  function currentPassages() { return world.projections[mode]; }

  function renderedFor(roomKey) {
    var room = world.rooms[roomKey];
    if (!room) return "";
    var passage = currentPassages().find(function (item) {
      return item.locator === room.locator;
    });
    if (!passage) return "";
    var token = passage.trace.find(function (item) {
      return item.token_id === room.token_id;
    });
    return token ? token.rendered : "";
  }

  function renderPassages() {
    var host = el("passages");
    host.replaceChildren();

    currentPassages().forEach(function (passage) {
      var card = document.createElement("article");
      card.className = "passage";

      var heading = document.createElement("div");
      heading.className = "eyebrow";
      heading.textContent = passage.locator + " · " + mode;
      card.appendChild(heading);

      var floor = document.createElement("div");
      floor.className = "floor";

      passage.trace.forEach(function (item) {
        var roomKey = key(passage.locator, item.token_id);
        var button = document.createElement("button");
        button.type = "button";
        button.className = "token";
        if (item.aleph_tav_occurrence) button.classList.add("marker");
        if (item.rendered === "") button.classList.add("vanished");
        if (roomKey === currentKey) button.classList.add("active");
        button.dataset.roomKey = roomKey;
        button.textContent = item.rendered === "" ? "∅" : item.rendered;
        button.title =
          item.rendered === ""
            ? "This source token is suppressed by the current projection. Open it to inspect what vanished."
            : item.source_surface;
        button.addEventListener("click", function () {
          openRoom(roomKey, true);
        });
        floor.appendChild(button);
      });

      card.appendChild(floor);
      host.appendChild(card);
    });
  }

  function renderTrail() {
    var host = el("trail");
    host.replaceChildren();
    trail.forEach(function (roomKey, index) {
      var room = world.rooms[roomKey];
      var button = document.createElement("button");
      button.type = "button";
      button.textContent =
        room.locator + " · " + room.local.token.source_surface;
      button.addEventListener("click", function () {
        openRoom(roomKey, false);
      });
      host.appendChild(button);
      if (index < trail.length - 1) {
        var arrow = document.createElement("span");
        arrow.textContent = "→";
        host.appendChild(arrow);
      }
    });
  }

  function openRoom(roomKey, appendTrail) {
    var room = world.rooms[roomKey];
    if (!room) return;
    currentKey = roomKey;

    if (appendTrail && trail[trail.length - 1] !== roomKey) trail.push(roomKey);
    if (!trail.length) trail.push(roomKey);
    renderTrail();
    renderPassages();

    el("room-title").textContent = room.local.token.source_surface;
    el("room-meta").textContent =
      room.locator + " · token " + room.token_id +
      " · source span " + room.local.token.source_span[0] +
      ":" + room.local.token.source_span[1];
    el("source").textContent = room.local.token.source_surface;
    var rendered = renderedFor(roomKey);
    el("rendered").textContent =
      mode + " projection: " + (rendered === "" ? "∅ (suppressed)" : rendered);
    el("annotations").textContent =
      JSON.stringify(room.local.token.annotations, null, 2);

    var layerHost = el("layers");
    layerHost.replaceChildren();
    Object.keys(room.layers).forEach(function (name) {
      var state = room.layers[name];
      var chip = document.createElement("span");
      chip.className = "layer" + (state.status === "fog" ? " fog" : "");
      chip.textContent =
        name + " · " + state.status + (state.available ? "" : " · no door");
      chip.title = state.note;
      layerHost.appendChild(chip);
    });

    var doorHost = el("doors");
    doorHost.replaceChildren();
    room.doors.forEach(function (door) {
      var destination = key(
        door.destination_locator || room.locator,
        door.destination_token_id
      );
      if (!world.rooms[destination]) return;
      var button = document.createElement("button");
      button.type = "button";
      button.className = "door " + door.epistemic_status;
      button.textContent =
        door.label + " → " +
        (door.destination_source_surface || door.destination_token_id);
      button.title =
        door.epistemic_status + " · " + (door.evidence_layer || "");
      button.addEventListener("click", function () {
        openRoom(destination, true);
      });
      doorHost.appendChild(button);
    });
    if (!doorHost.childElementCount) {
      doorHost.textContent = "No promoted door from this room.";
    }

    var alephPanel = el("aleph-panel");
    alephPanel.hidden = !room.aleph_tav;
    el("aleph-data").textContent =
      room.aleph_tav
        ? JSON.stringify(room.aleph_tav.learning_layers, null, 2)
        : "";

    var relationPanel = el("relation-panel");
    relationPanel.hidden = !room.object_relation;
    el("relation-data").textContent =
      room.object_relation
        ? JSON.stringify(
            {
              object_relation: room.object_relation.object_relation,
              evidence_separation: room.object_relation.evidence_separation
            },
            null,
            2
          )
        : "";

    el("fog-note").textContent = room.layers.interpretation.note;
  }

  renderPassages();
  var firstPassage = currentPassages()[0];
  if (firstPassage && firstPassage.trace.length) {
    openRoom(key(firstPassage.locator, firstPassage.trace[0].token_id), true);
  }
})();
</script>
</body>
</html>
"""
    return template.replace("__TITLE__", title).replace("__PAYLOAD__", payload)


def build_first_world_html(
    corpus: dict[str, Any],
    object_relation_instrument: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    result = build_first_world(corpus, object_relation_instrument)
    return result, render_first_world_html(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.first_world",
        description="Build Revival 010: the first unified walkable Scripture world.",
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
    result, html = build_first_world_html(corpus, instrument)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(
        json.dumps(
            {
                "output": str(args.output),
                "world_kind": result["world"]["kind"],
                "corpus_sha256": result["world"]["corpus_sha256"],
                "world_receipt": result["receipt"],
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2 if args.pretty else None,
            separators=None if args.pretty else (",", ":"),
        )
    )


if __name__ == "__main__":
    main()
