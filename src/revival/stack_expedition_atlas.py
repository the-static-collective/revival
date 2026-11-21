"""REVIVAL 013 / Scripture Stack Expedition: standalone local browser game.

Compiles from Revival's existing 011 source-backed places and the read-only
REVIVAL 013 bridge. No remote calls, no source mutation, no signer or player
identity provider. The optional WITNESS and PACT packets remain untrusted.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any, Mapping

from .object_relations import load_object_relation_instrument
from .stack_expedition import build_scripture_stack_expedition
from .world_places import build_world_places_html


def _safe_embed(data: Any) -> str:
    return (
        json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def build_stack_expedition_html(
    revival_world: Mapping[str, Any],
    expedition: Mapping[str, Any],
    *,
    source_atlas_filename: str = "revival-world-places.html",
) -> str:
    """Build a deterministic playable field guide linked to an existing Atlas."""
    if not source_atlas_filename.endswith(".html") or "/" in source_atlas_filename or "\\" in source_atlas_filename:
        raise ValueError("source atlas must be a simple local .html filename")
    places = revival_world["world"]["places"]
    # Only already constituted places from the source-backed Revival 011 world.
    safe_places = []
    for place in places:
        if place.get("kind") not in {"world", "scene", "passage", "token", "nominal-anchor", "verbal-anchor"}:
            continue
        safe_places.append({
            "address": place["address"],
            "kind": place["kind"],
            "label": place["label"],
            "parent": place.get("parent_address"),
            "epistemic": place.get("epistemic_status"),
        })
    payload = _safe_embed({
        "schema": "static-collective.revival-stack-playable.v1",
        "source_atlas": source_atlas_filename,
        "world": {
            "id": revival_world["world"]["corpus_id"],
            "root": revival_world["world"]["root_address"],
            "projection_sha256": revival_world["receipt"]["projection_sha256"],
        },
        "places": safe_places,
        "companion": {
            "audio": expedition["audio_candidates"],
            "reviews": expedition["packet_reviews"],
        },
        "authority": {
            "Deeds": 0, "Harvests": 0, "Capacity": 0,
            "rule": "A navigational choice is not a source witness, a verified human act or a Full Measure award.",
        },
    })
    template = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>REVIVAL — The Living Source Expedition</title>
<style>
:root { font-family:Georgia,Cambria,serif; line-height:1.5; color:#f6efe5; background:#0d1517; }
* { box-sizing:border-box; }
body { margin:0; background:radial-gradient(ellipse at 90% 0,#233834 0,transparent 43%),#0d1517; }
main { width:min(1160px,calc(100% - 28px)); margin:auto; padding:30px 0 70px; }
h1 { font-size:clamp(2.2rem,7vw,4.25rem); line-height:1.05; margin:.3rem 0 .8rem; letter-spacing:-.04em; }
h2 { font-size:1.45rem; }
p { color:#c8d6ce; }
a { color:#d7eacb; }
button { font:inherit; cursor:pointer; color:inherit; }
button:focus-visible,a:focus-visible { outline:3px solid #bedc97; outline-offset:3px; }
.eyebrow,.mono,.status,.count { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; }
.eyebrow { color:#b9d1a5; font-size:.76rem; text-transform:uppercase; letter-spacing:.11em; }
.lede { max-width:67ch; line-height:1.6; }
.card { border:1px solid #46635a; border-radius:18px; padding:20px; background:#152325; margin:15px 0; }
.row { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
.stats { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:20px 0; }
.stats .card { margin:0; padding:14px; }
.stats strong { font:800 clamp(1.4rem,4vw,2rem)/1.1 ui-monospace,monospace; color:#d5f2ae; display:block; }
.stats span { font-size:.77rem; color:#bccbc4; }
.track { height:12px; background:#2c4341; border-radius:20px; overflow:hidden; }
.track span { display:block; width:0%; height:100%; background:#adcb86; transition:width .2s; }
.actions { display:flex; flex-wrap:wrap; gap:8px; }
.action,.place { background:#263a35; border:1px solid #6a8b78; border-radius:10px; padding:9px 12px; text-align:left; }
.action:hover,.place:hover { background:#324a3d; }
.action.primary { background:#6c955d; color:#081b10; font-weight:700; }
.layout { display:grid; grid-template-columns:minmax(0,1.4fr) minmax(280px,.8fr); gap:20px; }
.place-list { display:grid; gap:10px; }
.passage { border:1px solid #45605a; border-radius:12px; padding:14px; background:#192b2a; }
.passage h3 { margin:0 0 8px; font-size:1.1rem; }
.tokens { display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; }
.place { font-size:.88rem; max-width:100%; overflow-wrap:anywhere; }
.place.visited { border-color:#b9df8c; background:#344f38; }
.chip { display:inline-block; border:1px solid #63776b; border-radius:99px; padding:3px 8px; color:#b5cabe; font: .72rem ui-monospace,monospace; }
.chip.fog { border-style:dashed; color:#ebcc94; }
.status { font-size:.8rem; min-height:1.4rem; overflow-wrap:anywhere; }
.fog { border:1px dashed #a88a5e; background:#332b21; border-radius:12px; padding:12px; margin:9px 0; }
.fog p { margin:5px 0; }
.anchor { overflow-wrap:anywhere; font: .75rem ui-monospace,monospace; color:#b2c7b4; }
footer { font-size:.84rem; margin-top:24px; border-top:1px solid #46635a; padding-top:19px; color:#a5b9ad; }
@media(max-width:760px){ .stats { grid-template-columns:repeat(2,1fr); } .layout { grid-template-columns:1fr; }}
@media(prefers-reduced-motion:reduce){.track span{transition:none}}
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">THE STATIC COLLECTIVE / SCRIPTURE STACK / REVIVAL 013</div>
<h1>The Living Source Expedition</h1>
<p class="lede">Walk an exact source-backed Scripture world. Open a Hebrew token, follow its declared doors, and return with a truthful account of your journey. WITNESS recordings and THE PACT appear as separate companions, never as hidden replacements for the source.</p>
<p class="anchor" id="world-receipt"></p>
</header>
<div class="stats">
<div class="card"><strong id="visit-count">0</strong><span>distinct places explored locally</span></div>
<div class="card"><strong id="glimmer-count">0</strong><span>source-place glimmers (play only)</span></div>
<div class="card"><strong id="passage-count">0</strong><span>source passage rooms visited</span></div>
<div class="card"><strong id="audio-count">0</strong><span>external audio references</span></div>
</div>
<div class="track" aria-label="Source places explored"><span id="fill"></span></div>
<p id="status" class="status" role="status">Choose any source-backed doorway. Unopened doors are not obligations.</p>
<div class="actions">
<button class="action primary" id="suggest">Find a source doorway</button>
<button class="action" id="export">Export journey review</button>
<button class="action" id="reset">Forget local exploration marks</button>
</div>
<div class="layout">
<section class="card">
<h2>Proven Genesis opening</h2>
<p>These are the passages actually present in Revival's current pinned OSHB witness corpus. A source-room opens in the companion local Atlas with its own receipt.</p>
<div id="places" class="place-list"></div>
</section>
<aside>
<section class="card">
<h2>WITNESS · Voices from elsewhere</h2>
<p>Matthew 5 recordings can enter here as independently declared audio metadata. Until Revival has source-backed Matthew 5, those addresses remain unlinked future doors.</p>
<label for="import">Import WITNESS or PACT review metadata (JSON, max 1 MB)</label>
<input id="import" type="file" accept=".json,application/json" style="max-width:100%;margin:8px 0 16px">
<div id="companions"></div>
</section>
<section class="card">
<h2>Full Measure boundary</h2>
<p id="measure">0 Deeds · 0 Harvests · 0 Capacity. A game journey is not a deed.</p>
<p>Audio SHA-256 is not a source witness. An address match does not establish that two text editions are equivalent.</p>
</section>
</aside>
</div>
<footer>Projection ≠ source · Listening claim ≠ authenticated voice · Game glimmers ≠ human worth · Reviewed evidence ≠ Full Measure admission</footer>
</main>
<script id="expedition-data" type="application/json">__DATA__</script>
<script>
(function () {
"use strict";
const data = JSON.parse(document.getElementById("expedition-data").textContent);
const $ = id => document.getElementById(id);
const addressSet = new Set(data.places.map(p => p.address));
const passageKinds = new Set(["passage", "token"]);
const sourcePlaces = data.places.filter(p => passageKinds.has(p.kind));
const key = "revival.expedition.013." + data.world.projection_sha256;
let visited;
try { const raw=JSON.parse(localStorage.getItem(key)||"[]"); visited=new Set(Array.isArray(raw)?raw.filter(v=>addressSet.has(v)):[]); }
catch { visited=new Set(); }
let external = data.companion.audio.slice();
const node=(tag,text,klass)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(klass)e.className=klass;return e};
const anchorFor=p=>data.source_atlas+"#"+encodeURIComponent(p.address);
function stamp(address){
 if(!addressSet.has(address))return;
 visited.add(address);
 try{localStorage.setItem(key,JSON.stringify([...visited]));}catch{$("status").textContent="Visit mark held in this tab; browser storage unavailable";}
 render();
}
function openPlace(place) {
 stamp(place.address);
 $("status").textContent="Exploring "+place.kind+": "+place.address+". Open its source-backed Atlas room.";
 const a=document.createElement("a");a.href=anchorFor(place);a.target="_blank";a.rel="noopener";
 a.click();
}
function render(){
 const touched=sourcePlaces.filter(p=>visited.has(p.address));
 const passages=touched.filter(p=>p.kind==="passage");
 $("visit-count").textContent=visited.size;
 $("glimmer-count").textContent=touched.length;
 $("passage-count").textContent=passages.length;
 $("audio-count").textContent=external.length;
 $("fill").style.width=(sourcePlaces.length?touched.length/sourcePlaces.length*100:0)+"%";
 $("world-receipt").textContent="Source world "+data.world.id+" · projection SHA-256 "+data.world.projection_sha256;
 const root=$("places");root.replaceChildren();
 const chapterPassages=data.places.filter(p=>p.kind==="passage");
 for(const passage of chapterPassages){
  const panel=node("article",undefined,"passage");
  const heading=node("h3",passage.label);panel.append(heading);
  const headButton=node("button",(visited.has(passage.address)?"Visited · ":"Open · ")+passage.label,"place"+(visited.has(passage.address)?" visited":""));
  headButton.onclick=()=>openPlace(passage);panel.append(headButton);
  const tokenRow=node("div",undefined,"tokens");
  for(const word of data.places.filter(p=>p.kind==="token"&&p.parent===passage.address)){
   const button=node("button",word.label+" · "+word.address.split("/").pop(),"place"+(visited.has(word.address)?" visited":""));
   button.onclick=()=>openPlace(word);tokenRow.append(button);
  }
  panel.append(tokenRow);root.append(panel);
 }
 renderCompanions();
}
function renderCompanions(){
 const root=$("companions");root.replaceChildren();
 if(!external.length){root.append(node("p","No audio reference packets imported. The source world is independently playable."));return}
 for(const rec of external){
  const box=node("article",undefined,"fog");
  box.append(node("strong",rec.passage+" · "+rec.declared_edition));
  box.append(node("p",rec.status==="ADDRESS_MATCH_ONLY"
   ?"Address matched in this world; editions and sources remain distinct."
   :"Unmapped passage. No manufactured Revival source door."));
  box.append(node("div","Recording ID "+rec.recording_id,"anchor"));
  box.append(node("span",rec.status==="ADDRESS_MATCH_ONLY"?"ADDRESS ONLY":"FOG · FUTURE FRONTIER","chip fog"));
  if(rec.revival_address&&addressSet.has(rec.revival_address)){
   const button=node("button","Explore the separately held source address","action");
   button.onclick=()=>openPlace(data.places.find(p=>p.address===rec.revival_address));
   box.append(node("div"));box.append(button);
  }
  root.append(box);
 }
}
function normalizePassage(raw){
 if(typeof raw!=="string")return null;
 const m=raw.trim().match(/^(gen(?:esis)?|mat(?:thew)?)[.\s]+(\d{1,3})[.\s]+(\d{1,3})$/i);
 if(!m||+m[2]<1||+m[3]<1)return null;
 return (m[1].toLowerCase().startsWith("gen")?"Gen":"Matt")+"."+Number(m[2])+"."+Number(m[3]);
}
function recordsFrom(p){
 if(!p||typeof p!=="object"||Array.isArray(p))throw Error("Not a metadata packet");
 if(JSON.stringify(p).length>950000)throw Error("Packet too large");
 const awards=p.awards;if(!awards||awards.Deeds!==0||awards.Harvests!==0||awards.Capacity!==0)throw Error("Foreign positive awards not accepted");
 let raw=[];
 if(p.schema==="static-collective.witness-freeplay-review.v1"&&p.source?.project==="WITNESS"){
  if(!Array.isArray(p.sample)||p.sample.length>120)throw Error("Invalid WITNESS sample");
  raw=p.sample;
 } else if(p.schema==="static-collective.witness-pact-full-measure-candidate.v1"&&p.source?.project==="WITNESS community audio Bible"){
  if(p.bridge?.withdrawn)throw Error("Withdrawn recording cannot be promoted");
  raw=[p.recording];
 } else if(p.schema==="static-collective.pact-world-review.v1"){return []}
 else throw Error("Unsupported metadata schema");
 const result=[];
 for(const r of raw){
  const passage=normalizePassage(r?.passage),sha=r?.sha256;
  if(!passage||typeof sha!=="string"||!/^[a-f0-9]{64}$/i.test(sha)||typeof r.recordingId!=="string"||r.recordingId.length<8||!r.edition)throw Error("Malformed recording reference");
  const match=data.places.find(item=>item.kind==="passage"&&item.label===passage);
  result.push({recording_id:r.recordingId,audio_sha256:sha,passage,declared_edition:String(r.edition),status:match?"ADDRESS_MATCH_ONLY":"UNMAPPED_EXTERNAL_PASSAGE",revival_address:match?.address||null});
 }
 return result;
}
$("import").onchange=async event=>{
 const file=event.target.files?.[0];if(!file)return;
 try{
  if(file.size>1000000)throw Error("Metadata package exceeds 1 MB");
  const packet=JSON.parse(await file.text());
  const recs=recordsFrom(packet);
  external=[...external,...recs].filter((r,i,a)=>a.findIndex(q=>q.recording_id===r.recording_id&&q.audio_sha256===r.audio_sha256)===i);
  $("status").textContent=recs.length+" unverified audio references inspected locally. Neither audio nor source text was imported.";
  render();
 }catch(e){$("status").textContent="Import held: "+e.message}
 finally{event.target.value=""}
};
$("suggest").onclick=()=>{
 const remaining=sourcePlaces.filter(p=>!visited.has(p.address));
 if(!remaining.length){$("status").textContent="All current source rooms have been opened. Revisit any room freely.";return}
 const next=remaining[Math.floor(Math.random()*remaining.length)];
 openPlace(next);
};
$("reset").onclick=()=>{
 if(!confirm("Clear only this device's local exploration marks? Source witnesses and imported files remain untouched."))return;
 visited.clear();try{localStorage.removeItem(key)}catch{}render();
 $("status").textContent="Local visits cleared. Nothing in Revival, WITNESS or THE PACT was deleted.";
};
$("export").onclick=()=>{
 const packet={schema:"static-collective.revival-journey-review.v1",
  source:{project:"REVIVAL",worldId:data.world.id,worldProjectionSha256:data.world.projection_sha256},
  journey:{visited:[...visited].sort(),uniqueSourcePlaces:sourcePlaces.filter(p=>visited.has(p.address)).length},
  companionSummary:{audioReferenceCount:external.length,unmappedCount:external.filter(r=>r.status==="UNMAPPED_EXTERNAL_PASSAGE").length},
  awards:{Deeds:0,Harvests:0,Capacity:0},
  status:"LOCAL_EXPLORATION_UNVERIFIED",
  boundary:"Browser clicks are gameplay, not verified human acts, Scripture proof or Full Measure authority."};
 const blob=new Blob([JSON.stringify(packet,null,2)],{type:"application/json"});
 const url=URL.createObjectURL(blob),a=document.createElement("a");
 a.href=url;a.download="REVIVAL__local-journey-review.json";a.click();
 setTimeout(()=>URL.revokeObjectURL(url),1200);
 $("status").textContent="Downloaded local journey review. Source metadata only; no private tokens or audio.";
};
render();
})();
</script>
</body>
</html>"""
    return template.replace("__DATA__", payload)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m revival.stack_expedition_atlas",
        description="Build a local Scripture exploration game with WITNESS and PACT review doors.",
    )
    parser.add_argument("corpus_manifest", type=Path)
    parser.add_argument("--macula-xml", required=True, type=Path)
    parser.add_argument("--macula-manifest", required=True, type=Path)
    parser.add_argument("--root", default=Path.cwd(), type=Path)
    parser.add_argument("--companion-packet", action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if len(args.companion_packet) > 20:
        parser.error("maximum 20 companion packets")
    corpus, instrument = load_object_relation_instrument(
        args.corpus_manifest,
        args.macula_xml,
        args.macula_manifest,
        root=args.root,
    )
    world_result, world_html = build_world_places_html(corpus, instrument)
    packets = [json.loads(path.read_text(encoding="utf-8")) for path in args.companion_packet]
    expedition = build_scripture_stack_expedition(world_result, companion_packets=packets)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    world_filename = "revival-world-places.html"
    game_html = build_stack_expedition_html(
        world_result, expedition, source_atlas_filename=world_filename
    )
    args.output.write_text(game_html, encoding="utf-8")
    world_path = args.output.parent / world_filename
    world_path.write_text(world_html, encoding="utf-8")
    report = {
        "game": str(args.output),
        "source_world": str(world_path),
        "companion_packets": expedition["packet_reviews"],
        "audio_frontiers": expedition["audio_candidates"],
        "receipt": expedition["receipt"],
    }
    print(json.dumps(report, indent=2 if args.pretty else None, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
