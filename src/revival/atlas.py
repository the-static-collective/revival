"""Deterministic standalone Curiosity Atlas for Revival.

The Atlas composes one linguistic projection and all of its token curiosity
rooms into a self-contained HTML file. It is a presentation descendant, not a
new source or authority layer.
"""

from __future__ import annotations

from dataclasses import asdict
from html import escape
import json
from typing import Any

from .curiosity import open_token_room
from .kernel.v1 import Delta, Projection, Transform, make_receipt
from .linguistic import _witness_from_payload, compile_linguistic_projection


def build_curiosity_atlas(
    specimen: dict[str, Any],
    recipe_id: str,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose every emitted token room into one deterministic atlas."""
    compiled = compile_linguistic_projection(specimen, recipe_id, profile)
    witness = _witness_from_payload(specimen["witness"])
    trace = compiled["projection"]["content"]["trace"]

    rooms: dict[str, Any] = {}
    room_receipts: dict[str, Any] = {}
    for item in trace:
        token_id = item["token_id"]
        opened = open_token_room(specimen, recipe_id, token_id, profile)
        rooms[token_id] = opened["room"]
        room_receipts[token_id] = opened["receipt"]

    atlas = {
        "kind": "curiosity-atlas",
        "witness_locator": witness.locator,
        "recipe_id": recipe_id,
        "profile_id": compiled["projection"]["content"]["profile_id"],
        "compiled_text": compiled["projection"]["content"]["text"],
        "compiled_trace": trace,
        "compiled_projection_receipt": compiled["receipt"],
        "room_order": [item["token_id"] for item in trace],
        "rooms": rooms,
        "room_receipts": room_receipts,
    }

    transform = Transform(
        name="curiosity_atlas",
        version="1",
        parameters={
            "recipe_id": recipe_id,
            "profile": profile,
            "compiled_receipt": compiled["receipt"],
            "room_receipts": room_receipts,
        },
    )
    projection = Projection(kind="curiosity-atlas", content=atlas)
    delta = Delta(
        kind="presentation",
        details={
            "source_changed": False,
            "atlas_adds_authority": False,
            "note": (
                "The Atlas composes admitted linguistic projections and "
                "curiosity rooms into a walkable local presentation."
            ),
        },
    )
    receipt = make_receipt(
        witness=witness,
        transform=transform,
        projection=projection,
        delta=delta,
    )
    return {
        "atlas": atlas,
        "delta": asdict(delta),
        "receipt": asdict(receipt),
    }


def _safe_embedded_json(value: Any) -> str:
    """Encode JSON so data cannot terminate the application/json element."""
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        encoded.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_curiosity_atlas_html(result: dict[str, Any]) -> str:
    """Render deterministic standalone HTML for one atlas result."""
    atlas = result["atlas"]
    title = escape("Revival · " + atlas["witness_locator"])
    payload = _safe_embedded_json(result)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ font-family: Georgia, Cambria, serif; line-height: 1.5; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:#11110f; color:#f4efe2; }}
button {{ font:inherit; }}
main {{ max-width:1080px; margin:auto; padding:28px 18px 56px; }}
header {{ border-bottom:1px solid #59564e; padding-bottom:16px; }}
.eyebrow,.meta,pre {{ font-family:ui-monospace,Consolas,monospace; }}
.eyebrow {{ text-transform:uppercase; letter-spacing:.12em; font-size:.78rem; color:#bbb5a6; }}
.verse {{ display:flex; flex-wrap:wrap; gap:9px; padding:28px 0; font-size:clamp(1.4rem,4vw,2.6rem); }}
.token,.door {{ border:1px solid #686258; background:#1d1b18; color:#fffaf0; cursor:pointer; }}
.token {{ border-radius:999px; padding:.18em .5em; }}
.door {{ border-radius:9px; padding:7px 9px; }}
.token.active,.token:focus-visible,.door:focus-visible {{ outline:2px solid #ddd4bf; outline-offset:2px; }}
.grid {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(280px,.85fr); gap:18px; }}
.card {{ border:1px solid #59564e; border-radius:14px; padding:18px; background:#171613; }}
.source {{ font-size:2rem; direction:rtl; unicode-bidi:plaintext; }}
.rendered {{ font-size:1.55rem; }}
.meta {{ font-size:.84rem; color:#c9c2b1; overflow-wrap:anywhere; }}
.doors,.trail {{ display:flex; flex-wrap:wrap; gap:7px; margin:8px 0 16px; }}
.trail button {{ border:0; background:transparent; color:#ddd4bf; text-decoration:underline; cursor:pointer; }}
.preview {{ border-left:3px solid #8f8879; padding-left:10px; }}
@media(max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">Revival · Curiosity Atlas</div>
<h1 id="locator"></h1>
<div class="meta" id="projection-meta"></div>
<div class="trail" id="trail" aria-label="Traversal trail"></div>
</header>

<section aria-label="Compiled Bible floor">
<div class="eyebrow" style="margin-top:26px">Compiled floor</div>
<div class="verse" id="verse"></div>
</section>

<section class="grid">
<article class="card" aria-live="polite">
<div class="eyebrow">Open room</div>
<h2 id="room-title"></h2>
<div class="source" id="source"></div>
<div class="rendered" id="rendered"></div>
<div class="meta" id="span"></div>
<p class="preview" id="preview" hidden></p>
<h3>Rendering doors</h3><div class="doors" id="choices"></div>
<h3>Source neighbors</h3><div class="doors" id="source-neighbors"></div>
<h3>Compiled neighbors</h3><div class="doors" id="output-neighbors"></div>
<h3>Relation doors</h3><div class="doors" id="relations"></div>
</article>

<aside class="card">
<div class="eyebrow">Receipt / provenance</div>
<h3>Current origin</h3><pre id="origin"></pre>
<h3>Room receipt</h3><div class="meta" id="room-receipt"></div>
<h3>Atlas receipt</h3><div class="meta" id="atlas-receipt"></div>
<p class="meta">Explorability does not grant source, linguistic, theological, or canonical authority.</p>
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
  var roomReceipts = atlas.room_receipts;
  var trail = [];
  var current = atlas.room_order[0];

  function el(id) {{ return document.getElementById(id); }}

  el("locator").textContent = atlas.witness_locator;
  el("projection-meta").textContent =
    "recipe: " + atlas.recipe_id + " · profile: " + (atlas.profile_id || "default");

  atlas.compiled_trace.filter(function (item) {{
    return item.rendered !== "";
  }}).forEach(function (item) {{
    var button = document.createElement("button");
    button.className = "token";
    button.type = "button";
    button.dataset.tokenId = item.token_id;
    button.textContent = item.rendered;
    button.addEventListener("click", function () {{ openRoom(item.token_id, true); }});
    el("verse").appendChild(button);
  }});

  function addDoor(container, label, tokenId, detail) {{
    var button = document.createElement("button");
    button.className = "door";
    button.type = "button";
    button.textContent = label;
    if (detail) button.title = detail;
    button.addEventListener("click", function () {{ openRoom(tokenId, true); }});
    container.appendChild(button);
  }}

  function renderNeighbors(containerId, neighbors) {{
    var container = el(containerId);
    container.replaceChildren();
    Object.keys(neighbors).forEach(function (direction) {{
      var item = neighbors[direction];
      if (!item) return;
      addDoor(
        container,
        direction + " · " + (item.rendered || item.source_surface),
        item.token_id,
        item.source_surface
      );
    }});
    if (!container.childElementCount) container.textContent = "No neighboring door.";
  }}

  function renderTrail() {{
    var container = el("trail");
    container.replaceChildren();
    trail.forEach(function (tokenId, index) {{
      var button = document.createElement("button");
      button.type = "button";
      button.textContent =
        rooms[tokenId].token.current_rendering || rooms[tokenId].token.source_surface;
      button.addEventListener("click", function () {{ openRoom(tokenId, false); }});
      container.appendChild(button);
      if (index < trail.length - 1) {{
        var arrow = document.createElement("span");
        arrow.textContent = "→";
        container.appendChild(arrow);
      }}
    }});
  }}

  function openRoom(tokenId, appendTrail) {{
    if (!rooms[tokenId]) return;
    current = tokenId;
    var room = rooms[tokenId];

    if (appendTrail && trail[trail.length - 1] !== tokenId) trail.push(tokenId);
    if (!trail.length) trail.push(tokenId);
    renderTrail();

    document.querySelectorAll(".token").forEach(function (node) {{
      node.classList.toggle("active", node.dataset.tokenId === tokenId);
    }});

    el("room-title").textContent = room.token.current_rendering || "(empty rendering)";
    el("source").textContent = room.token.source_surface;
    el("rendered").textContent = "current: " + (room.token.current_rendering || "∅");
    el("span").textContent =
      "token " + tokenId + " · source span " +
      room.token.source_span[0] + ":" + room.token.source_span[1];
    el("origin").textContent = JSON.stringify(room.token.current_origin, null, 2);
    el("room-receipt").textContent =
      "projection " + roomReceipts[tokenId].projection_sha256;
    el("atlas-receipt").textContent =
      "projection " + result.receipt.projection_sha256;

    var preview = el("preview");
    preview.hidden = true;
    preview.textContent = "";

    var choices = el("choices");
    choices.replaceChildren();
    room.rendering_choices.forEach(function (variant) {{
      var button = document.createElement("button");
      button.className = "door";
      button.type = "button";
      button.textContent =
        (variant.value || "∅") + (variant.default ? " · default" : "");
      button.title = variant.authority || "";
      button.addEventListener("click", function () {{
        preview.hidden = false;
        preview.textContent =
          "Choice preview: " + (variant.value || "∅") + " · " +
          (variant.authority || "authority unspecified") +
          ". Preview only: compile a preference profile to inhabit this choice.";
      }});
      choices.appendChild(button);
    }});
    if (!choices.childElementCount) choices.textContent = "No rendering alternatives.";

    renderNeighbors("source-neighbors", room.neighbors.source);
    renderNeighbors("output-neighbors", room.neighbors.output);

    var relations = el("relations");
    relations.replaceChildren();
    room.doors.filter(function (item) {{
      return item.kind === "relation";
    }}).forEach(function (door) {{
      addDoor(
        relations,
        door.direction + " · " + door.label + " → " +
          (door.destination_rendered || door.destination_source_surface),
        door.destination_token_id,
        door.relation_kind + " · " + door.authority
      );
    }});
    if (!relations.childElementCount) relations.textContent = "No declared relation doors.";
  }}

  openRoom(current, true);
}})();
</script>
</body>
</html>
"""


def build_curiosity_atlas_html(
    specimen: dict[str, Any],
    recipe_id: str,
    profile: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    """Return replayable atlas data and its deterministic HTML presentation."""
    result = build_curiosity_atlas(specimen, recipe_id, profile)
    return result, render_curiosity_atlas_html(result)
