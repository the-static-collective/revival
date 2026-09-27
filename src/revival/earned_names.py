"""Revival 012: let addressable places earn lexical names.

Names in this layer belong first to lexemes, not to passage-level referents.
An OSHB token/anchor may point to a named lexeme only after its lemma and
morphology morphemes are aligned and the selected augmented Strong component
matches the pinned lexical proof extract exactly.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .aleph_tav import decompose_oshb_token
from .kernel.v1 import sha256
from .object_relations import load_object_relation_instrument
from .world_places import build_world_places


LEXICAL_AUTHORITY = "revival-012-pinned-lexical-proof"


def load_lexical_proof(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("kind") != "curated-lexical-proof-extract":
        raise ValueError("unsupported lexical proof kind")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("lexical proof requires entries")

    seen: set[str] = set()
    for entry in entries:
        strong = entry.get("augmented_strong")
        if not isinstance(strong, str) or not strong:
            raise ValueError("lexical entry requires augmented_strong")
        if strong in seen:
            raise ValueError(f"duplicate lexical entry: {strong}")
        seen.add(strong)
        for field in ("lexical_index_id", "hebrew", "transliteration"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                raise ValueError(f"lexical entry {strong} missing {field}")
        glosses = entry.get("short_glosses")
        if not isinstance(glosses, list) or not glosses:
            raise ValueError(f"lexical entry {strong} requires short_glosses")

    return {
        **data,
        "fixture_sha256": sha256(data),
        "_entries_by_strong": {
            entry["augmented_strong"]: entry
            for entry in entries
        },
    }


def public_lexical_proof(proof: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in proof.items()
        if not key.startswith("_")
    }


def _token_index(corpus: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for witness in corpus["witnesses"]:
        locator = witness["locator"]
        specimen = corpus["_specimens_by_locator"][locator]
        for token in specimen["tokens"]:
            index[f"{locator}::{token['id']}"] = token
    return index


def _anchor_component(
    token: dict[str, Any],
    anchor_kind: str,
) -> dict[str, Any]:
    target_pos = {
        "nominal-anchor": "N",
        "verbal-anchor": "V",
    }.get(anchor_kind)
    if target_pos is None:
        raise ValueError(f"unsupported anchor kind: {anchor_kind}")

    decomposition = decompose_oshb_token(token)
    matches = [
        part for part in decomposition["parts"]
        if part["morphology"]["part_of_speech_code"] == target_pos
    ]
    if len(matches) != 1:
        raise ValueError(
            f"{token['id']} {anchor_kind} requires exactly one aligned "
            f"{target_pos} morpheme; found {len(matches)}"
        )
    return {
        "component": matches[0],
        "decomposition": decomposition,
    }


def _earned_name(
    *,
    token: dict[str, Any],
    anchor_kind: str,
    entry: dict[str, Any],
) -> dict[str, Any]:
    aligned = _anchor_component(token, anchor_kind)
    component = aligned["component"]
    strong = component["lemma"]
    if strong != entry["augmented_strong"]:
        raise ValueError(
            f"lexical identity mismatch for {token['id']}: "
            f"{strong!r} != {entry['augmented_strong']!r}"
        )

    prefixes = [
        {
            "index": part["index"],
            "surface": part["surface"],
            "lemma": part["lemma"],
            "part_of_speech_code": (
                part["morphology"]["part_of_speech_code"]
            ),
        }
        for part in aligned["decomposition"]["parts"]
        if part["index"] < component["index"]
    ]

    return {
        "status": "attributed",
        "authority": LEXICAL_AUTHORITY,
        "augmented_strong": strong,
        "lexical_index_id": entry["lexical_index_id"],
        "hebrew": entry["hebrew"],
        "transliteration": entry["transliteration"],
        "short_glosses": entry["short_glosses"],
        "proof_note": entry["proof_note"],
        "selected_component": {
            "index": component["index"],
            "surface": component["surface"],
            "lemma": component["lemma"],
            "part_of_speech_code": (
                component["morphology"]["part_of_speech_code"]
            ),
        },
        "prefix_components_preserved": prefixes,
        "declared_token_lemma": aligned["decomposition"]["declared_lemma"],
        "alignment_rule": aligned["decomposition"]["rule"],
        "referent_status": "fog",
        "sense_status": "fog",
    }


def build_earned_names_world(
    corpus: dict[str, Any],
    object_relation_instrument: dict[str, Any],
    lexical_proof: dict[str, Any],
) -> dict[str, Any]:
    """Attach pinned lexeme identities to 011 anchors without typing referents."""
    places_result = build_world_places(corpus, object_relation_instrument)
    base = places_result["world"]
    token_by_room = _token_index(corpus)
    entries = lexical_proof["_entries_by_strong"]

    places = [dict(place) for place in base["places"]]
    edges = [dict(edge) for edge in base["edges"]]
    by_address = {place["address"]: place for place in places}

    lexicon_address = base["root_address"] + "/lexicon/oshb-hebrew-lexicon"
    lexicon_place = {
        "address": lexicon_address,
        "kind": "lexicon",
        "label": "Open Scriptures Hebrew Lexicon proof",
        "parent_address": base["root_address"],
        "epistemic_status": "attributed",
        "authority": LEXICAL_AUTHORITY,
        "fixture_sha256": lexical_proof["fixture_sha256"],
        "note": (
            "Pinned lexical proof layer. Lexeme identity does not establish "
            "passage-level sense or referent identity."
        ),
    }
    places.append(lexicon_place)
    edges.append({
        "kind": "contains",
        "from": base["root_address"],
        "to": lexicon_address,
    })

    occurrence_anchors: dict[str, list[str]] = {}
    anchor_names: dict[str, dict[str, Any]] = {}

    for place in places:
        if place["kind"] not in {"nominal-anchor", "verbal-anchor"}:
            continue
        room_key = place["room_key"]
        token = token_by_room[room_key]
        aligned = _anchor_component(token, place["kind"])
        strong = aligned["component"]["lemma"]
        entry = entries.get(strong)
        if entry is None:
            continue

        earned = _earned_name(
            token=token,
            anchor_kind=place["kind"],
            entry=entry,
        )
        lexeme_address = (
            lexicon_address + "/strong/" + quote(strong, safe="")
        )
        place["earned_name"] = earned
        place["lexeme_address"] = lexeme_address
        anchor_names[place["address"]] = earned
        occurrence_anchors.setdefault(strong, []).append(place["address"])
        edges.append({
            "kind": "lexically-identifies",
            "from": place["address"],
            "to": lexeme_address,
            "evidence_layer": "aligned OSHB lemma+morphology plus pinned lexical proof",
        })

    lexemes: dict[str, dict[str, Any]] = {}
    for strong in sorted(occurrence_anchors, key=lambda value: (len(value), value)):
        entry = entries[strong]
        address = lexicon_address + "/strong/" + quote(strong, safe="")
        lexeme = {
            "address": address,
            "kind": "lexeme",
            "label": entry["hebrew"] + " · " + entry["transliteration"],
            "parent_address": lexicon_address,
            "epistemic_status": "attributed",
            "authority": LEXICAL_AUTHORITY,
            "augmented_strong": strong,
            "lexical_index_id": entry["lexical_index_id"],
            "hebrew": entry["hebrew"],
            "transliteration": entry["transliteration"],
            "short_glosses": entry["short_glosses"],
            "proof_note": entry["proof_note"],
            "occurrence_anchor_addresses": occurrence_anchors[strong],
            "sense_status": "fog",
            "referent_status": "fog",
            "semantic_type": {
                "status": "fog",
                "type": None,
                "note": (
                    "Lexical identity is now named, but person/place/object/event "
                    "typing still requires a separately attributable layer."
                ),
            },
        }
        lexemes[strong] = lexeme
        places.append(lexeme)
        edges.append({
            "kind": "contains",
            "from": lexicon_address,
            "to": address,
        })
        for anchor_address in occurrence_anchors[strong]:
            edges.append({
                "kind": "lexeme-occurrence",
                "from": address,
                "to": anchor_address,
            })

    if len({place["address"] for place in places}) != len(places):
        raise ValueError("earned-name world address collision")

    rooms: dict[str, Any] = {}
    for room_key, room in base["first_world"]["rooms"].items():
        names = [
            anchor_names[address]
            for address in room["anchor_addresses"]
            if address in anchor_names
        ]
        rooms[room_key] = {
            **room,
            "earned_names": names,
        }

    world_core = {
        **base,
        "kind": "revival-earned-names-world",
        "version": "012",
        "places": places,
        "edges": edges,
        "first_world": {
            **base["first_world"],
            "rooms": rooms,
        },
        "lexicon_address": lexicon_address,
        "lexemes": lexemes,
        "anchor_names": anchor_names,
        "lexical_proof": public_lexical_proof(lexical_proof),
        "naming_law": {
            "alignment": (
                "select the noun/verb lexeme only after literal OSHB "
                "surface/lemma/morphology morpheme alignment"
            ),
            "prefix_rule": (
                "prefix components remain visible; d/776 and c/d/776 may "
                "reach H776 only through aligned component selection"
            ),
            "identity_boundary": (
                "lexeme identity != sense != referent != semantic world type"
            ),
        },
        "world_places_receipt": places_result["receipt"],
    }
    receipt = {
        "kind": "revival-earned-names-world",
        "corpus_sha256": corpus["corpus_sha256"],
        "world_places_projection_sha256": (
            places_result["receipt"]["projection_sha256"]
        ),
        "lexical_fixture_sha256": lexical_proof["fixture_sha256"],
        "lexemes_sha256": sha256(lexemes),
        "anchor_names_sha256": sha256(anchor_names),
        "places_sha256": sha256(places),
        "edges_sha256": sha256(edges),
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


def render_earned_names_html(result: dict[str, Any]) -> str:
    world = result["world"]
    payload = _safe_json(result)
    title = escape("Revival 012 · Earned Names")

    template = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root { font-family:Georgia,Cambria,serif; line-height:1.5; }
* { box-sizing:border-box; }
body { margin:0; background:#0c0c0a; color:#f4efe2; }
button { font:inherit; }
main { max-width:1280px; margin:auto; padding:26px 18px 64px; }
header { border-bottom:1px solid #575249; padding-bottom:18px; }
.eyebrow,.meta,.address,pre { font-family:ui-monospace,Consolas,monospace; }
.eyebrow { color:#bbb3a3; text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; }
.hero { max-width:850px; font-size:1.08rem; }
.address { overflow-wrap:anywhere; color:#d5ccbc; font-size:.8rem; }
.controls,.trail,.doors,.names,.occurrences,.floor { display:flex; flex-wrap:wrap; gap:8px; }
.control,.door,.lexeme,.token,.anchor,.trail button {
  border:1px solid #6b655a; background:#201e1a; color:#fffaf0; cursor:pointer;
}
.control,.door,.lexeme,.anchor { border-radius:9px; padding:7px 10px; }
.control.active { outline:2px solid #ddd4bf; outline-offset:2px; }
.layout { display:grid; grid-template-columns:minmax(310px,.78fr) minmax(0,1.22fr); gap:18px; margin-top:22px; }
.card { border:1px solid #575249; border-radius:14px; padding:16px; background:#161512; }
.lexeme-card { border:1px solid #4d4941; border-radius:12px; padding:11px; margin:10px 0; }
.lexeme-hebrew { font-size:1.55rem; direction:rtl; unicode-bidi:plaintext; }
.passage { border-left:3px solid #71695d; padding:9px 11px; margin:11px 0; }
.floor { font-size:1.3rem; margin-top:7px; }
.token { border-radius:999px; padding:.18em .48em; }
.token.vanished { opacity:.5; border-style:dashed; }
.source { font-size:2rem; direction:rtl; unicode-bidi:plaintext; }
.fog { border:1px dashed #756d61; border-radius:12px; padding:11px; }
.named { border-left:3px double #a39984; padding-left:10px; }
.group { margin:14px 0; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; font-size:.78rem; color:#d0c7b7; }
.trail { margin-top:12px; align-items:center; }
.trail button { border:0; background:transparent; color:#ddd4bf; text-decoration:underline; padding:0; }
@media(max-width:850px) { .layout,.grid2 { grid-template-columns:1fr; } }
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">Revival 012 · Let The Places Earn Names</div>
<h1>Names arrive through evidence.</h1>
<p class="hero">The world can now name a lexical identity without pretending it has settled the occurrence's sense or referent. Prefixes stay visible. Lexeme identity, sense, referent, and world type remain separate.</p>
<div class="address" id="root-address"></div>
<div class="controls" id="projection-controls"></div>
<div class="trail" id="trail"></div>
</header>

<section class="layout">
<aside class="card">
<div class="eyebrow">Earned lexeme constellation</div>
<div id="lexemes"></div>
<div class="fog">
<strong>The name is real. The referent is still a question.</strong>
<div class="meta">lexeme != sense != referent != person/place/object/event</div>
</div>

<h3>Passage floors</h3>
<div id="passages"></div>
</aside>

<article class="card" aria-live="polite">
<div class="eyebrow">Current place</div>
<h2 id="place-title"></h2>
<div class="address" id="place-address"></div>
<div class="meta" id="place-meta"></div>

<div id="lexeme-detail" hidden>
<div class="lexeme-hebrew" id="lexeme-hebrew"></div>
<div class="named">
<div id="lexeme-translit"></div>
<div class="meta" id="lexeme-strong"></div>
<div id="lexeme-glosses"></div>
</div>
<h3>Occurrences</h3>
<div class="occurrences" id="lexeme-occurrences"></div>
<div class="fog"><strong>Sense/referent fog remains.</strong><div class="meta" id="lexeme-boundary"></div></div>
</div>

<div id="anchor-detail" hidden>
<h3>Earned name</h3>
<pre id="earned-name"></pre>
<div class="doors" id="anchor-doors"></div>
<div class="fog"><strong>World type unresolved.</strong><div class="meta" id="anchor-fog"></div></div>
</div>

<div id="token-detail" hidden>
<div class="source" id="source"></div>
<div id="rendered"></div>
<h3>Earned names at this token</h3>
<div class="names" id="token-names"></div>
<h3>Existing world doors</h3>
<div class="doors" id="token-doors"></div>
<div class="grid2">
<div><h3>Deep layers</h3><pre id="deep-layers"></pre></div>
<div><h3>Source layers</h3><pre id="annotations"></pre></div>
</div>
</div>

<div id="structural-detail">
<h3>Children</h3>
<div class="doors" id="children"></div>
</div>

<h3>012 law</h3>
<pre id="law"></pre>
<h3>012 receipt</h3>
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
  function roomKey(locator, tokenId) { return locator + "::" + tokenId; }
  function enc(value) { return encodeURIComponent(value); }

  world.places.forEach(function (place) {
    places[place.address] = place;
    if (place.parent_address) {
      (children[place.parent_address] ||= []).push(place.address);
    }
  });

  el("root-address").textContent = world.root_address;
  el("receipt").textContent = "projection " + result.receipt.projection_sha256;
  el("law").textContent = JSON.stringify(world.naming_law, null, 2);

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
      renderPassages();
      if (places[currentAddress] && places[currentAddress].kind === "token") {
        openAddress(currentAddress, false);
      }
    });
    el("projection-controls").appendChild(button);
  });

  function buttonFor(address, label, className) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = className || "door";
    button.textContent = label;
    button.addEventListener("click", function () { openAddress(address, true); });
    return button;
  }

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

  function renderLexemes() {
    var host = el("lexemes");
    host.replaceChildren();
    Object.keys(world.lexemes).sort(function (a, b) {
      return Number(a) - Number(b);
    }).forEach(function (strong) {
      var lexeme = world.lexemes[strong];
      var card = document.createElement("div");
      card.className = "lexeme-card";
      var h = document.createElement("div");
      h.className = "lexeme-hebrew";
      h.textContent = lexeme.hebrew;
      card.appendChild(h);
      card.appendChild(
        buttonFor(
          lexeme.address,
          lexeme.transliteration + " · H" + strong +
            " · " + lexeme.occurrence_anchor_addresses.length + " occurrence(s)",
          "lexeme"
        )
      );
      host.appendChild(card);
    });
  }

  function renderPassages() {
    var host = el("passages");
    host.replaceChildren();
    first.projections[mode].forEach(function (passage) {
      var box = document.createElement("div");
      box.className = "passage";
      var title = document.createElement("div");
      title.className = "eyebrow";
      title.textContent = passage.locator + " · " + mode;
      box.appendChild(title);
      var floor = document.createElement("div");
      floor.className = "floor";
      passage.trace.forEach(function (item) {
        var rk = roomKey(passage.locator, item.token_id);
        var address = world.room_addresses[rk];
        floor.appendChild(
          buttonFor(
            address,
            item.rendered === "" ? "∅" : item.rendered,
            "token" + (item.rendered === "" ? " vanished" : "")
          )
        );
      });
      box.appendChild(floor);
      host.appendChild(box);
    });
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

  function hideDetails() {
    el("lexeme-detail").hidden = true;
    el("anchor-detail").hidden = true;
    el("token-detail").hidden = true;
    el("structural-detail").hidden = true;
  }

  function renderLexeme(place) {
    el("lexeme-detail").hidden = false;
    el("lexeme-hebrew").textContent = place.hebrew;
    el("lexeme-translit").textContent = place.transliteration;
    el("lexeme-strong").textContent =
      "H" + place.augmented_strong + " · lexical index " + place.lexical_index_id;
    el("lexeme-glosses").textContent =
      "lexical range: " + place.short_glosses.join(" · ");
    el("lexeme-boundary").textContent =
      "sense=" + place.sense_status + " · referent=" + place.referent_status +
      " · semantic type=" + place.semantic_type.status;

    var host = el("lexeme-occurrences");
    host.replaceChildren();
    place.occurrence_anchor_addresses.forEach(function (address) {
      var anchor = places[address];
      host.appendChild(
        buttonFor(
          address,
          anchor.locator + " · " + anchor.label,
          "anchor"
        )
      );
    });
  }

  function renderAnchor(place) {
    el("anchor-detail").hidden = false;
    el("earned-name").textContent =
      JSON.stringify(place.earned_name || {status:"unnamed"}, null, 2);
    el("anchor-fog").textContent = place.semantic_type.note;

    var host = el("anchor-doors");
    host.replaceChildren();
    if (place.lexeme_address) {
      host.appendChild(
        buttonFor(
          place.lexeme_address,
          "lexeme → " + places[place.lexeme_address].transliteration,
          "door"
        )
      );
    }
    host.appendChild(
      buttonFor(place.token_address, "source token → " + places[place.token_address].label, "door")
    );
  }

  function renderToken(place) {
    el("token-detail").hidden = false;
    var room = first.rooms[place.room_key];
    el("source").textContent = room.local.token.source_surface;
    var rendered = renderedToken(room.locator, room.token_id);
    el("rendered").textContent =
      mode + " projection: " + (rendered === "" ? "∅ (suppressed)" : rendered);
    el("annotations").textContent =
      JSON.stringify(room.local.token.annotations, null, 2);
    el("deep-layers").textContent = JSON.stringify(
      {
        aleph_tav: room.aleph_tav,
        object_relation: room.object_relation,
        epistemic_layers: room.layers
      },
      null,
      2
    );

    var names = el("token-names");
    names.replaceChildren();
    room.anchor_addresses.forEach(function (address) {
      var anchor = places[address];
      if (!anchor.earned_name) return;
      names.appendChild(
        buttonFor(
          address,
          anchor.earned_name.hebrew + " · " +
            anchor.earned_name.transliteration,
          "anchor"
        )
      );
    });
    if (!names.childElementCount) names.textContent = "No earned lexical name in the 012 proof extract.";

    var doors = el("token-doors");
    doors.replaceChildren();
    room.doors.forEach(function (door) {
      var targetKey = roomKey(
        door.destination_locator || room.locator,
        door.destination_token_id
      );
      var targetAddress = world.room_addresses[targetKey];
      if (!targetAddress) return;
      doors.appendChild(
        buttonFor(
          targetAddress,
          door.label + " → " +
            (door.destination_source_surface || door.destination_token_id),
          "door"
        )
      );
    });
    if (!doors.childElementCount) doors.textContent = "No promoted 010 door.";
  }

  function renderStructural(place) {
    el("structural-detail").hidden = false;
    var host = el("children");
    host.replaceChildren();
    (children[place.address] || []).forEach(function (address) {
      var child = places[address];
      host.appendChild(
        buttonFor(address, child.kind + " · " + child.label, "door")
      );
    });
    if (!host.childElementCount) host.textContent = "No child place.";
  }

  function openAddress(address, updateHash) {
    var place = places[address];
    if (!place) return;
    currentAddress = address;
    if (trail[trail.length - 1] !== address) trail.push(address);
    renderTrail();
    hideDetails();

    el("place-title").textContent = place.label;
    el("place-address").textContent = place.address;
    el("place-meta").textContent =
      place.kind + " · " + place.epistemic_status + " · " + place.authority;

    if (place.kind === "lexeme") renderLexeme(place);
    else if (place.kind.endsWith("-anchor")) renderAnchor(place);
    else if (place.kind === "token") renderToken(place);
    else renderStructural(place);

    if (updateHash) history.replaceState(null, "", "#" + enc(address));
  }

  window.addEventListener("hashchange", function () {
    var raw = location.hash.slice(1);
    if (!raw) return;
    var address = decodeURIComponent(raw);
    if (places[address]) openAddress(address, false);
  });

  renderLexemes();
  renderPassages();
  var initial = world.lexicon_address;
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


def build_earned_names_world_html(
    corpus: dict[str, Any],
    object_relation_instrument: dict[str, Any],
    lexical_proof: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    result = build_earned_names_world(
        corpus,
        object_relation_instrument,
        lexical_proof,
    )
    return result, render_earned_names_html(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.earned_names",
        description="Build Revival 012: let addressable places earn lexical names.",
    )
    parser.add_argument("corpus_manifest", type=Path)
    parser.add_argument("--macula-xml", required=True, type=Path)
    parser.add_argument("--macula-manifest", required=True, type=Path)
    parser.add_argument("--lexical-proof", required=True, type=Path)
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
    proof = load_lexical_proof(args.lexical_proof)
    result, html = build_earned_names_world_html(corpus, instrument, proof)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(
        json.dumps(
            {
                "output": str(args.output),
                "world_kind": result["world"]["kind"],
                "lexeme_count": len(result["world"]["lexemes"]),
                "named_anchor_count": len(result["world"]["anchor_names"]),
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
