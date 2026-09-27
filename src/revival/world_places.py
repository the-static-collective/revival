"""Revival 011: give the first world stable places and scale.

A "place" here means an addressable location in a receipted world topology,
not a claim that a source token denotes a geographic place. Semantic typing
(person/place/object/event/etc.) remains fog until an attributable layer earns
that classification.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .first_world import build_first_world
from .kernel.v1 import sha256
from .object_relations import load_object_relation_instrument


ANCHOR_AUTHORITY = "revival-011-morphology-anchor"
SCENE_AUTHORITY = "revival-011-declared-world-container"


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


def _oshb_data(token: dict[str, Any]) -> dict[str, Any] | None:
    annotation = token.get("annotations", {}).get("oshb")
    if not isinstance(annotation, dict):
        return None
    data = annotation.get("data")
    return data if isinstance(data, dict) else None


def _morphology_pos_codes(morph: str) -> list[str]:
    """Return top-level OSHB morpheme POS codes without semantic inference."""
    codes: list[str] = []
    for index, raw in enumerate(morph.split("/")):
        code = raw
        if index == 0 and code[:1] in {"H", "A"}:
            code = code[1:]
        if code:
            codes.append(code[0])
    return codes


def _anchor_kind(token: dict[str, Any]) -> str | None:
    data = _oshb_data(token)
    if data is None or not isinstance(data.get("morph"), str):
        return None
    codes = _morphology_pos_codes(data["morph"])
    if "N" in codes:
        return "nominal-anchor"
    if "V" in codes:
        return "verbal-anchor"
    return None


def _semantic_fog(anchor_kind: str) -> dict[str, Any]:
    return {
        "status": "fog",
        "type": None,
        "candidate_vocabulary": ["person", "place", "object", "event", "other"],
        "note": (
            f"{anchor_kind} is earned from morphology only. "
            "Morphology does not establish which world-semantic class the "
            "referent belongs to."
        ),
    }


def build_world_places(
    corpus: dict[str, Any],
    object_relation_instrument: dict[str, Any],
) -> dict[str, Any]:
    """Add stable hierarchical addresses and morphology-earned anchors to 010."""
    first = build_first_world(corpus, object_relation_instrument)
    base_world = first["world"]

    root_address = f"revival://{corpus['id']}"
    scene_address = root_address + "/scene/genesis-opening-proof"

    places: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    room_addresses: dict[str, str] = {}
    anchor_addresses: dict[str, list[str]] = {}

    def add_place(place: dict[str, Any]) -> None:
        places.append(place)
        parent = place.get("parent_address")
        if parent:
            edges.append(
                {
                    "kind": "contains",
                    "from": parent,
                    "to": place["address"],
                }
            )

    add_place(
        {
            "address": root_address,
            "kind": "world",
            "label": corpus["id"],
            "parent_address": None,
            "epistemic_status": "derived",
            "authority": "revival-011-address-space",
            "note": "Addressable world projection over one receipted corpus.",
        }
    )
    add_place(
        {
            "address": scene_address,
            "kind": "scene",
            "label": "Genesis opening proof scene",
            "parent_address": root_address,
            "epistemic_status": "declared",
            "authority": SCENE_AUTHORITY,
            "note": (
                "A declared navigational container for the current proof corpus; "
                "not asserted as a source-authored scene division."
            ),
        }
    )

    specimens = corpus["_specimens_by_locator"]
    for witness in corpus["witnesses"]:
        locator = witness["locator"]
        passage_address = scene_address + "/passage/" + locator
        add_place(
            {
                "address": passage_address,
                "kind": "passage",
                "label": locator,
                "parent_address": scene_address,
                "epistemic_status": "source-backed",
                "authority": "OSHB witness locator",
                "witness_id": witness["witness_id"],
                "witness_sha256": witness["witness_sha256"],
            }
        )

        specimen = specimens[locator]
        for token in specimen["tokens"]:
            room_key = f"{locator}::{token['id']}"
            token_address = passage_address + "/token/" + token["id"]
            room_addresses[room_key] = token_address
            add_place(
                {
                    "address": token_address,
                    "kind": "token",
                    "label": token["surface"],
                    "parent_address": passage_address,
                    "epistemic_status": "source-backed",
                    "authority": "OSHB source token",
                    "locator": locator,
                    "token_id": token["id"],
                    "room_key": room_key,
                }
            )

            anchor_kind = _anchor_kind(token)
            if anchor_kind is None:
                continue

            data = _oshb_data(token)
            assert data is not None
            anchor_address = (
                passage_address + "/anchor/" + anchor_kind + "/" + token["id"]
            )
            anchor = {
                "address": anchor_address,
                "kind": anchor_kind,
                "label": token["surface"],
                "parent_address": passage_address,
                "epistemic_status": "attributed",
                "authority": ANCHOR_AUTHORITY,
                "locator": locator,
                "token_id": token["id"],
                "room_key": room_key,
                "morph": data["morph"],
                "morphology_pos_codes": _morphology_pos_codes(data["morph"]),
                "semantic_type": _semantic_fog(anchor_kind),
                "token_address": token_address,
            }
            add_place(anchor)
            edges.append(
                {
                    "kind": "anchors",
                    "from": anchor_address,
                    "to": token_address,
                    "evidence_layer": "declared OSHB morphology",
                }
            )
            anchor_addresses.setdefault(room_key, []).append(anchor_address)

    address_index = {item["address"]: item for item in places}
    if len(address_index) != len(places):
        raise ValueError("world address collision")

    rooms: dict[str, Any] = {}
    for room_key, room in base_world["rooms"].items():
        rooms[room_key] = {
            **room,
            "world_address": room_addresses[room_key],
            "anchor_addresses": anchor_addresses.get(room_key, []),
            "scale_path": [
                root_address,
                scene_address,
                scene_address + "/passage/" + room["locator"],
                room_addresses[room_key],
            ],
        }

    place_core = {
        "kind": "revival-world-places",
        "version": "011",
        "corpus_id": corpus["id"],
        "corpus_sha256": corpus["corpus_sha256"],
        "root_address": root_address,
        "scene_address": scene_address,
        "places": places,
        "edges": edges,
        "room_addresses": room_addresses,
        "anchor_addresses": anchor_addresses,
        "semantic_typing_law": {
            "rule": (
                "morphology may earn nominal/verbal anchors but does not by "
                "itself classify a referent as person/place/object/event"
            ),
            "unresolved_state": "fog",
        },
        "address_law": {
            "rule": (
                "world addresses identify navigable projection locations; "
                "addressability does not assert geographic or historical location"
            ),
            "scheme": "revival://",
        },
        "first_world": {
            **base_world,
            "rooms": rooms,
        },
        "first_world_receipt": first["receipt"],
    }
    receipt = {
        "kind": "revival-world-places",
        "corpus_sha256": corpus["corpus_sha256"],
        "first_world_projection_sha256": first["receipt"]["projection_sha256"],
        "places_sha256": sha256(places),
        "edges_sha256": sha256(edges),
        "room_addresses_sha256": sha256(room_addresses),
        "projection_sha256": sha256(place_core),
    }
    return {"world": place_core, "receipt": receipt}


def render_world_places_html(result: dict[str, Any]) -> str:
    world = result["world"]
    payload = _safe_json(result)
    title = escape("Revival 011 · The World Has Places")

    template = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root { font-family:Georgia,Cambria,serif; line-height:1.5; }
* { box-sizing:border-box; }
body { margin:0; background:#0d0d0b; color:#f3eee1; }
button { font:inherit; }
main { max-width:1280px; margin:auto; padding:26px 18px 64px; }
header { border-bottom:1px solid #575249; padding-bottom:18px; }
.eyebrow,.meta,pre,.address { font-family:ui-monospace,Consolas,monospace; }
.eyebrow { color:#bbb3a3; text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; }
.hero { max-width:840px; font-size:1.08rem; }
.address { overflow-wrap:anywhere; color:#d8cfbe; font-size:.82rem; }
.controls,.trail,.crumbs,.doors,.anchors,.tokens { display:flex; flex-wrap:wrap; gap:8px; }
.control,.door,.anchor,.token,.place-link,.trail button,.crumbs button {
  border:1px solid #6b655a; background:#201e1a; color:#fffaf0; cursor:pointer;
}
.control,.door,.anchor,.place-link { border-radius:9px; padding:7px 10px; }
.control.active { outline:2px solid #ddd4bf; outline-offset:2px; }
.layout { display:grid; grid-template-columns:minmax(300px,.72fr) minmax(0,1.28fr); gap:18px; margin-top:22px; }
.card { border:1px solid #575249; border-radius:14px; padding:16px; background:#161512; }
.scene { margin:10px 0; padding:12px; border:1px solid #49453e; border-radius:12px; }
.passage { margin:9px 0; padding:10px; border-left:3px solid #71695d; }
.anchor { font-size:.86rem; }
.anchor.nominal-anchor { border-style:double; }
.anchor.verbal-anchor { border-style:dashed; }
.token { border-radius:999px; padding:.2em .52em; }
.token.vanished { opacity:.5; border-style:dashed; }
.token.active { outline:2px solid #ddd4bf; outline-offset:2px; }
.floor { display:flex; flex-wrap:wrap; gap:7px; font-size:1.34rem; margin-top:8px; }
.group { margin:14px 0; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.source { font-size:2rem; direction:rtl; unicode-bidi:plaintext; }
.crumbs { margin:8px 0 14px; align-items:center; }
.crumbs button,.trail button { border:0; background:transparent; text-decoration:underline; padding:0; color:#ddd4bf; }
.fog { border:1px dashed #756d61; border-radius:12px; padding:11px; }
.boundary { border-left:3px solid #8a7f6b; padding-left:10px; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; font-size:.78rem; color:#d0c7b7; }
@media(max-width:850px) { .layout,.grid2 { grid-template-columns:1fr; } }
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">Revival 011 · The World Has Places</div>
<h1>Scripture is now addressable at more than one scale.</h1>
<p class="hero">A place is a stable location in the Revival world topology. It may be a world, declared scene container, source-backed passage, morphology-earned anchor, or source token. Addressability is not a claim of geography, history, or semantic type.</p>
<div class="address" id="root-address"></div>
<div class="controls" id="projection-controls"></div>
<div class="trail" id="trail"></div>
</header>

<section class="layout">
<aside class="card">
<div class="eyebrow">World map</div>
<h2>Zoom</h2>
<div id="world-map"></div>
<div class="fog">
<strong>Semantic type: fog by default.</strong>
<p class="meta">Noun/verb morphology can earn an anchor. It does not prove person, place, object, event, or historical referent.</p>
</div>
</aside>

<article class="card" aria-live="polite">
<div class="eyebrow">Current place</div>
<div class="crumbs" id="crumbs"></div>
<h2 id="place-title"></h2>
<div class="address" id="place-address"></div>
<div class="meta" id="place-meta"></div>

<div id="token-room" hidden>
<div class="source" id="source"></div>
<div id="rendered"></div>

<div class="group">
<h3>Local floor</h3>
<div class="floor" id="local-floor"></div>
</div>

<div class="group">
<h3>World anchors at this token</h3>
<div class="anchors" id="room-anchors"></div>
</div>

<div class="group">
<h3>Existing 010 doors</h3>
<div class="doors" id="doors"></div>
</div>

<div class="grid2">
<div>
<h3>Aleph-Tav / relation layers</h3>
<pre id="deep-layers"></pre>
</div>
<div>
<h3>Declared source layers</h3>
<pre id="annotations"></pre>
</div>
</div>
</div>

<div id="structural-place">
<div class="group">
<h3>Children</h3>
<div class="doors" id="children"></div>
</div>
<div class="group" id="anchor-detail" hidden>
<h3>Morphology-earned anchor</h3>
<pre id="anchor-data"></pre>
<div class="fog"><strong>Unresolved semantic type</strong><div class="meta" id="semantic-fog"></div></div>
</div>
</div>

<h3>World law</h3>
<p class="boundary">place != referent · address != geography · morphology != semantic type · scene container != source division</p>
<h3>011 receipt</h3>
<div class="meta" id="receipt"></div>
</article>
</section>
</main>

<script id="revival-data" type="application/json">__PAYLOAD__</script>
<script>
(function () {
  "use strict";
  var result = JSON.parse(document.getElementById("revival-data").textContent);
  var world = result.world;
  var first = world.first_world;
  var places = {};
  var children = {};
  var mode = "source";
  var currentAddress = world.root_address;
  var trail = [];

  function el(id) { return document.getElementById(id); }
  function enc(address) { return encodeURIComponent(address); }
  function roomKey(locator, tokenId) { return locator + "::" + tokenId; }

  world.places.forEach(function (place) {
    places[place.address] = place;
    if (place.parent_address) {
      (children[place.parent_address] ||= []).push(place.address);
    }
  });

  el("root-address").textContent = world.root_address;
  el("receipt").textContent = "projection " + result.receipt.projection_sha256;

  first.projection_modes.forEach(function (name) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "control" + (name === mode ? " active" : "");
    button.dataset.mode = name;
    button.textContent = name;
    button.addEventListener("click", function () {
      mode = name;
      document.querySelectorAll(".control").forEach(function (node) {
        node.classList.toggle("active", node.dataset.mode === mode);
      });
      renderWorldMap();
      openAddress(currentAddress, false);
    });
    el("projection-controls").appendChild(button);
  });

  function passageProjection(locator) {
    return first.projections[mode].find(function (item) {
      return item.locator === locator;
    });
  }

  function renderedToken(locator, tokenId) {
    var passage = passageProjection(locator);
    if (!passage) return "";
    var item = passage.trace.find(function (token) {
      return token.token_id === tokenId;
    });
    return item ? item.rendered : "";
  }

  function go(address) {
    openAddress(address, true);
  }

  function buttonFor(address, label, className) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = className || "place-link";
    b.textContent = label;
    b.addEventListener("click", function () { go(address); });
    return b;
  }

  function renderWorldMap() {
    var host = el("world-map");
    host.replaceChildren();

    var scene = places[world.scene_address];
    var sceneBox = document.createElement("div");
    sceneBox.className = "scene";
    sceneBox.appendChild(buttonFor(scene.address, scene.label));

    (children[scene.address] || []).forEach(function (passageAddress) {
      var passage = places[passageAddress];
      var box = document.createElement("div");
      box.className = "passage";
      box.appendChild(buttonFor(passage.address, passage.label));

      var floor = document.createElement("div");
      floor.className = "floor";
      var projection = passageProjection(passage.label);
      if (projection) {
        projection.trace.forEach(function (item) {
          var rk = roomKey(passage.label, item.token_id);
          var address = world.room_addresses[rk];
          var token = buttonFor(
            address,
            item.rendered === "" ? "∅" : item.rendered,
            "token" + (item.rendered === "" ? " vanished" : "")
          );
          token.title = item.source_surface;
          floor.appendChild(token);
        });
      }
      box.appendChild(floor);

      var anchors = document.createElement("div");
      anchors.className = "anchors";
      (children[passage.address] || []).forEach(function (childAddress) {
        var child = places[childAddress];
        if (!child.kind.endsWith("-anchor")) return;
        anchors.appendChild(
          buttonFor(
            child.address,
            child.kind.replace("-anchor", "") + " · " + child.label,
            "anchor " + child.kind
          )
        );
      });
      box.appendChild(anchors);
      sceneBox.appendChild(box);
    });

    host.appendChild(sceneBox);
  }

  function renderTrail() {
    var host = el("trail");
    host.replaceChildren();
    trail.forEach(function (address, index) {
      var place = places[address];
      host.appendChild(buttonFor(address, place.label, ""));
      if (index < trail.length - 1) {
        var arrow = document.createElement("span");
        arrow.textContent = "→";
        host.appendChild(arrow);
      }
    });
  }

  function scalePath(place) {
    var path = [];
    var cursor = place;
    while (cursor) {
      path.unshift(cursor.address);
      cursor = cursor.parent_address ? places[cursor.parent_address] : null;
    }
    return path;
  }

  function renderCrumbs(place) {
    var host = el("crumbs");
    host.replaceChildren();
    var path = scalePath(place);
    path.forEach(function (address, index) {
      host.appendChild(buttonFor(address, places[address].kind, ""));
      if (index < path.length - 1) {
        var slash = document.createElement("span");
        slash.textContent = "/";
        host.appendChild(slash);
      }
    });
  }

  function renderChildren(place) {
    var host = el("children");
    host.replaceChildren();
    (children[place.address] || []).forEach(function (address) {
      var child = places[address];
      host.appendChild(
        buttonFor(address, child.kind + " · " + child.label, "door")
      );
    });
    if (!host.childElementCount) host.textContent = "No smaller place from here.";
  }

  function renderLocalFloor(room) {
    var host = el("local-floor");
    host.replaceChildren();
    var passage = passageProjection(room.locator);
    if (!passage) return;
    passage.trace.forEach(function (item) {
      var address = world.room_addresses[roomKey(room.locator, item.token_id)];
      var b = buttonFor(
        address,
        item.rendered === "" ? "∅" : item.rendered,
        "token" + (item.rendered === "" ? " vanished" : "")
      );
      if (address === room.world_address) b.classList.add("active");
      host.appendChild(b);
    });
  }

  function renderTokenRoom(place) {
    var room = first.rooms[place.room_key];
    el("token-room").hidden = false;
    el("structural-place").hidden = true;
    el("source").textContent = room.local.token.source_surface;
    var rendered = renderedToken(room.locator, room.token_id);
    el("rendered").textContent =
      mode + " projection: " + (rendered === "" ? "∅ (suppressed)" : rendered);
    el("annotations").textContent =
      JSON.stringify(room.local.token.annotations, null, 2);
    renderLocalFloor(room);

    var anchorHost = el("room-anchors");
    anchorHost.replaceChildren();
    room.anchor_addresses.forEach(function (address) {
      var anchor = places[address];
      anchorHost.appendChild(
        buttonFor(address, anchor.kind + " · " + anchor.label, "anchor " + anchor.kind)
      );
    });
    if (!anchorHost.childElementCount) {
      anchorHost.textContent = "No nominal/verbal morphology anchor on this token.";
    }

    var doorHost = el("doors");
    doorHost.replaceChildren();
    room.doors.forEach(function (door) {
      var targetKey = roomKey(
        door.destination_locator || room.locator,
        door.destination_token_id
      );
      var targetAddress = world.room_addresses[targetKey];
      if (!targetAddress) return;
      doorHost.appendChild(
        buttonFor(
          targetAddress,
          door.label + " → " +
            (door.destination_source_surface || door.destination_token_id),
          "door"
        )
      );
    });
    if (!doorHost.childElementCount) doorHost.textContent = "No promoted 010 door.";

    el("deep-layers").textContent = JSON.stringify(
      {
        aleph_tav: room.aleph_tav,
        object_relation: room.object_relation,
        epistemic_layers: room.layers
      },
      null,
      2
    );
  }

  function renderStructuralPlace(place) {
    el("token-room").hidden = true;
    el("structural-place").hidden = false;
    renderChildren(place);

    var panel = el("anchor-detail");
    var isAnchor = place.kind.endsWith("-anchor");
    panel.hidden = !isAnchor;
    if (isAnchor) {
      el("anchor-data").textContent = JSON.stringify(
        {
          kind: place.kind,
          morph: place.morph,
          morphology_pos_codes: place.morphology_pos_codes,
          token_address: place.token_address,
          authority: place.authority
        },
        null,
        2
      );
      el("semantic-fog").textContent = place.semantic_type.note;
    }
  }

  function openAddress(address, updateHash) {
    var place = places[address];
    if (!place) return;
    currentAddress = address;
    if (trail[trail.length - 1] !== address) trail.push(address);
    renderTrail();
    renderCrumbs(place);

    el("place-title").textContent = place.label;
    el("place-address").textContent = place.address;
    el("place-meta").textContent =
      place.kind + " · " + place.epistemic_status + " · " + place.authority;

    if (place.kind === "token") renderTokenRoom(place);
    else renderStructuralPlace(place);

    if (updateHash) history.replaceState(null, "", "#" + enc(address));
  }

  window.addEventListener("hashchange", function () {
    var raw = location.hash.slice(1);
    if (!raw) return;
    var address = decodeURIComponent(raw);
    if (places[address]) openAddress(address, false);
  });

  renderWorldMap();
  var initial = world.root_address;
  if (location.hash.slice(1)) {
    var decoded = decodeURIComponent(location.hash.slice(1));
    if (places[decoded]) initial = decoded;
  }
  openAddress(initial, false);
})();
</script>
</body>
</html>
"""
    return template.replace("__TITLE__", title).replace("__PAYLOAD__", payload)


def build_world_places_html(
    corpus: dict[str, Any],
    object_relation_instrument: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    result = build_world_places(corpus, object_relation_instrument)
    return result, render_world_places_html(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.world_places",
        description="Build Revival 011: an addressable multi-scale Scripture world.",
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
    result, html = build_world_places_html(corpus, instrument)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(
        json.dumps(
            {
                "output": str(args.output),
                "world_kind": result["world"]["kind"],
                "root_address": result["world"]["root_address"],
                "place_count": len(result["world"]["places"]),
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
