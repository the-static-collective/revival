"""REVIVAL 014: standalone Greek Matthew 5 Atlas with local WITNESS audio crosswalk.

The pinned SBLGNT edited Greek NT and WITNESS engwebp recordings coexist by
passage locator only. No translation equivalence, voice identity, or textual
critical claim is inferred by the game. Audio is never sent to a server.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from typing import Any

from .matthew5 import load_and_build_matthew5


def _safe_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def build_matthew5_html(result: dict[str, Any]) -> str:
    world = result["world"]
    if world["schema"] != "static-collective.revival.sblgnt-matthew5.v1":
        raise ValueError("expected a receipted REVIVAL 014 Matthew 5 world")
    from .kernel.v1 import sha256
    if result["receipt"]["projection_sha256"] != sha256(world):
        raise ValueError("Greek Matthew world receipt mismatch")
    payload = _safe_json(result)
    template = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>REVIVAL — Matthew 5 · The Open Word</title>
<style>
:root {font-family:Georgia,Cambria,serif;background:#0b151c;color:#f4f2e5;line-height:1.5}
* {box-sizing:border-box}
body {margin:0;background:radial-gradient(circle at 80% 0%,#173441 0%,transparent 45%),#0b151c}
main {width:min(1180px,calc(100% - 26px));margin:auto;padding:30px 0 70px}
a {color:#c4e3f3}
h1 {font-size:clamp(2.2rem,7vw,4.4rem);letter-spacing:-.04em;line-height:1.03;margin:7px 0}
h2 {font-size:clamp(1.2rem,3vw,1.6rem);margin:.2rem 0 .7rem}
p {color:#c2d1d0}
button {font:inherit;cursor:pointer;color:inherit;background:#1b323e;border:1px solid #6a8c8e;border-radius:10px;padding:9px 12px}
button:hover {background:#2a4a56}
button:focus-visible,a:focus-visible {outline:3px solid #d7bf75;outline-offset:3px}
.eyebrow,.mono,.metric,.note,.status {font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.eyebrow {font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:#acd7ce}
.lede {max-width:74ch;line-height:1.6}
.card {background:#132831;border:1px solid #456776;border-radius:16px;padding:17px;margin:16px 0}
.stats {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin:20px 0}
.metric {background:#152f3a;border:1px solid #456776;border-radius:12px;padding:13px}
.metric strong {display:block;color:#e9d28d;font-size:1.6rem}
.metric span {color:#a4bfc1;font-size:.74rem}
.tools {display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.tools button {flex:0 1 auto}
.track {height:12px;border-radius:22px;overflow:hidden;background:#27434c;margin:15px 0 6px}
.track span {display:block;width:0;height:100%;background:#e2ce8e}
.layout {display:grid;grid-template-columns:minmax(0,1.4fr) minmax(290px,.8fr);gap:16px}
.verses {display:grid;gap:8px}
.verse {border:1px solid #446470;border-radius:14px;padding:15px;background:#132831;scroll-margin-top:12px}
.verse.active {border-color:#e9d28d}
.verse h3 {margin:0 0 11px;display:flex;gap:9px;align-items:center;justify-content:space-between}
.verse h3 .counts {font-size:.71rem;color:#b4d1ce}
.greek {font-size:clamp(1.22rem,2.8vw,1.6rem);line-height:2.25;letter-spacing:.005em}
.word {font:inherit;line-height:1.4;background:transparent;border:1px solid transparent;padding:3px 5px;margin:1px;border-radius:6px;color:#e8e9df}
.word:hover,.word.active {background:#304f52;border-color:#6d9292}
.word.opened {border-bottom:1px solid #a4c792}
.license {font-size:.8rem;border-left:3px solid #c0b178;padding-left:12px}
.chip {display:inline-block;border:1px solid #719596;border-radius:99px;padding:3px 8px;margin:4px 4px 0 0;font-size:.74rem;color:#c6ded8}
.chip.fog {border-style:dashed;color:#e5bf85}
.word-detail {position:sticky;top:8px}
.word-text {font-size:2rem;color:#e5d5a0;overflow-wrap:anywhere}
.note {font-size:.77rem;color:#b5c5c3;overflow-wrap:anywhere}
.status {min-height:20px;font-size:.8rem;color:#d3e1d8}
.recording {border:1px solid #456776;border-radius:9px;padding:9px;background:#1d3740;margin-top:8px}
.recording audio {width:100%;margin-top:7px}
.recording strong,.recording small {display:block}
.recording small {color:#b4c8c5;overflow-wrap:anywhere}
section.side {margin-bottom:16px}
.fogbox {border:1px dashed #aa9869;background:#332f22;border-radius:12px;padding:12px}
input[type=file] {max-width:100%;margin:9px 0 12px}
footer {font-size:.81rem;padding:18px 0;border-top:1px solid #567075}
@media(max-width:780px){.layout{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.word-detail{position:static}}
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">REVIVAL 014 / SBLGNT v1.2 / WITNESS AUDIO / MATTHEW 5</div>
<h1>The Open Word</h1>
<p class="lede">The Sermon on the Mount opens in its own documented Greek edition. Explore a verse, uncover the exact characters behind any word-shaped display segment, then hear voluntarily contributed WITNESS readings in a distinct English edition. The verse address connects them. Their texts never silently become one.</p>
<p class="license">Greek Scripture source: <a href="https://sblgnt.com/" target="_blank" rel="noopener">SBL Greek New Testament</a> © 2010 Society of Biblical Literature and Logos Bible Software, edited by Michael W. Holmes. <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>. This site extracts Matthew 5 from the pinned SBLGNT v1.2 electronic text; attribution, changes and exact source hashes are included in the receipt. No endorsement is implied.</p>
<p id="origin" class="note"></p>
</header>
<div class="stats">
<div class="metric"><strong id="visitedVerses">0/48</strong><span>Greek passages visited here</span></div>
<div class="metric"><strong id="visitedWords">0</strong><span>exact Greek display segments opened</span></div>
<div class="metric"><strong id="voices">0</strong><span>WITNESS audio references loaded</span></div>
<div class="metric"><strong id="glimmers">0</strong><span>local exploration glimmers (play only)</span></div>
</div>
<div class="track" role="progressbar" aria-label="Matthew chapter exploration" aria-valuemin="0" aria-valuemax="48" aria-valuenow="0" id="progress"><span id="progressFill"></span></div>
<div class="tools">
<button id="discover">Discover an unexplored Greek verse</button>
<button id="random">Surprise passage</button>
<button id="export">Export journey receipt</button>
<button id="reset">Clear local visit marks</button>
</div>
<p class="status" id="status" role="status">Every passage is open. No one is assigned a verse or required to complete a chapter.</p>
<div class="layout">
<section aria-label="Greek Matthew 5">
<h2>Matthew 5 — pinned source edition</h2>
<div id="verses" class="verses"></div>
</section>
<aside>
<section class="card word-detail" aria-labelledby="word-heading">
<div class="eyebrow">Exact SBLGNT source segment</div>
<h2 id="word-heading">Open a Greek word</h2>
<div id="openedWord" class="word-text">—</div>
<div id="openedMeta" class="note">Tap a word-shaped segment to inspect its source characters and offsets.</div>
<div id="wordLayers"></div>
<div class="tools"><button id="previousWord" disabled>Previous</button><button id="nextWord" disabled>Next</button></div>
<p class="note">A whitespace segment is not a lexeme, translation, grammar analysis, theological judgment or historical artifact.</p>
</section>
<section class="card side">
<div class="eyebrow">WITNESS · the community audio Bible</div>
<h2>Hear a human reading</h2>
<p>The existing WITNESS recorder speaks the <strong>World English Bible Protestant Edition</strong> (<code>engwebp</code>). Audio and source text are different artifacts. One verse address lets you navigate both.</p>
<label for="witnessImport">Load a WITNESS audio package or a metadata-only review (.json)</label>
<input id="witnessImport" type="file" accept=".json,application/json">
<div class="tools"><button id="clearAudio">Clear loaded audio</button></div>
<p id="audioStatus" class="note">No WITNESS package loaded. You may explore Greek without recording or listening.</p>
<div id="witnessList"></div>
<p class="note"><a href="https://github.com/the-static-collective/WITNESS/tree/genesis/community-audio-bible-001/prototype" target="_blank" rel="noopener">WITNESS recording prototype</a> · <a href="https://github.com/the-static-collective/planZ/tree/main/pact-cloud" target="_blank" rel="noopener">THE PACT private challenge room</a></p>
</section>
<section class="card side">
<h2>Full Measure</h2>
<div class="fogbox"><strong>0 Deeds · 0 Harvests · 0 Capacity</strong><p>Recording, playback, exploration and cooperative XP are review candidates, never automatically constituted consequences.</p></div>
</section>
</aside>
</div>
<footer>Source edition ≠ translation edition · Word-shaped segment ≠ parsed Greek lemma · Audio SHA-256 ≠ voice authentication · Exploring ≠ believing · Game ≠ Scripture · Review packet ≠ Full Measure admission</footer>
</main>
<script id="source-data" type="application/json">__PAYLOAD__</script>
<script>
(function() {
"use strict";
const source=JSON.parse(document.getElementById("source-data").textContent);
const world=source.world,$=id=>document.getElementById(id);
const byAddress=new Map(Object.entries(world.rooms));
const passages=new Map(world.passages.map(p=>[p.locator,p]));
const passageForRecording=(raw)=>{
 if(typeof raw!=="string")return null;
 const m=raw.trim().match(/^(?:matthew|matt)\.5\.(\d{1,2})$/i);
 const v=m?Number(m[1]):0;
 return v>=1&&v<=48?"Matt.5."+v:null;
};
const visitKey="revival.matthew5.014."+source.receipt.projection_sha256;
let visited=new Set(),current=null,loadedAudio=[],urls=[];
try{
 const raw=JSON.parse(localStorage.getItem(visitKey)||"[]");
 if(Array.isArray(raw))visited=new Set(raw.filter(x=>passages.has(x)||byAddress.has(x)));
}catch{}
const node=(tag,text,cls)=>{
 const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;
};
function updateStatus(message){$("status").textContent=message;}
function persist(){
 try{localStorage.setItem(visitKey,JSON.stringify([...visited]));}
 catch{updateStatus("Exploration is working in this tab, but device storage is unavailable.")}
}
function visit(address){
 if(!passages.has(address)&&!byAddress.has(address))return;
 visited.add(address);persist();renderProgress();
}
function renderProgress(){
 const visitedPassages=world.passages.filter(p=>visited.has(p.locator));
 const opened=[...visited].filter(x=>byAddress.has(x));
 $("visitedVerses").textContent=visitedPassages.length+"/48";
 $("visitedWords").textContent=opened.length;
 $("voices").textContent=loadedAudio.length;
 $("glimmers").textContent=visitedPassages.length*5+opened.length;
 $("progress").setAttribute("aria-valuenow",String(visitedPassages.length));
 $("progressFill").style.width=(visitedPassages.length/48*100).toFixed(2)+"%";
 for(const button of document.querySelectorAll(".word")){
  button.classList.toggle("opened",visited.has(button.dataset.address));
 }
}
function openPassage(locator){
 const verse=passages.get(locator);if(!verse)return;
 visit(locator);
 const card=document.getElementById("verse-"+locator.replaceAll(".","-"));
 card?.scrollIntoView({behavior:"smooth",block:"start"});
 document.querySelectorAll(".verse").forEach(v=>v.classList.remove("active"));
 card?.classList.add("active");
 updateStatus("Opening "+locator+" in SBLGNT v1.2. WITNESS audio, when available, remains WEB engwebp.");
 const fragment="#"+encodeURIComponent(locator);
 if(location.hash!==fragment)history.replaceState(null,"",fragment);
}
function openWord(address){
 const room=byAddress.get(address);if(!room)return;
 current=address;visit(address);visit(room.locator);
 $("openedWord").textContent=room.surface;
 $("openedMeta").textContent=room.locator+" · "+room.token_id+" · exact offsets ["+room.span.join(", ")+") in the SBLGNT verse display";
 const layers=$("wordLayers");layers.replaceChildren();
 for(const [key,value] of Object.entries(room.declared_layers)){
  layers.append(node("span",key+": "+value,value==="fog"?"chip fog":"chip"));
 }
 $("previousWord").disabled=!room.neighbors.previous;
 $("nextWord").disabled=!room.neighbors.next;
 document.querySelectorAll(".word.active").forEach(x=>x.classList.remove("active"));
 const button=document.querySelectorAll(".word");
 for(const b of button){if(b.dataset.address===address){b.classList.add("active");break}}
 updateStatus("Exact SBLGNT display segment "+room.token_id+". No lexical or morphology inference has been made.");
 history.replaceState(null,"","#"+encodeURIComponent(address));
}
function buildVerses(){
 const parent=$("verses");parent.replaceChildren();
 for(const passage of world.passages){
  const card=node("article",undefined,"verse");card.id="verse-"+passage.locator.replaceAll(".","-");
  const header=node("h3");const title=node("span",passage.locator);
  const count=node("span","Greek source · "+passage.token_addresses.length+" display segments","counts mono");
  header.append(title,count);card.append(header);
  const line=node("div",undefined,"greek");
  for(const address of passage.token_addresses){
   const room=byAddress.get(address);if(!room)continue;
   const button=node("button",room.surface,"word");
   button.dataset.address=address;
   button.title="Inspect SBLGNT word-shaped segment "+room.token_id;
   button.onclick=()=>openWord(address);
   line.append(button);line.append(document.createTextNode(" "));
  }
  card.onclick=e=>{if(e.target===card||e.target===header||e.target===title||e.target===count)openPassage(passage.locator)};
  const footer=node("div",undefined,"tools");
  const open=node("button","Open "+passage.locator);open.onclick=()=>openPassage(passage.locator);
  footer.append(open);
  const listen=node("div");listen.id="audio-"+passage.locator.replaceAll(".","-");
  card.append(line,footer,listen);parent.append(card);
 }
 renderAudio();
}
function clearAudio(){
 urls.forEach(url=>URL.revokeObjectURL(url));urls=[];loadedAudio=[];
 $("witnessImport").value="";renderAudio();
}
function newRecord({id,passage,edition,hash,mime=null,url=null,right=null,reader=null,mode="metadata"}){
 return {id,passage,edition,hash,mime,url,right,reader,mode};
}
async function readWITNESS(file){
 if(file.size>28*1024*1024)throw Error("Package too large (28 MB limit)");
 const pkg=JSON.parse(await file.text());
 let entries=[],newUrls=[];
 try{
  if(pkg.witness_format==="witness-package"&&pkg.version===1){
   if(pkg.chapter?.id!=="matthew.5"||pkg.chapter?.text_edition?.id!=="engwebp")
    throw Error("This game accepts the WITNESS Matthew 5 WEB prototype only");
   if(!Array.isArray(pkg.recordings)||pkg.recordings.length>100)throw Error("Invalid number of WITNESS recordings");
   let bytesTotal=0;
   for(const record of pkg.recordings){
    const passage=passageForRecording(record.passage_start);
    if(!passage||Number(record.verse)!==Number(passage.split(".").pop()))throw Error("Recording/passage mismatch");
    if(!/^[a-f0-9]{64}$/i.test(record.sha256||""))throw Error("Missing audio digest");
    if(typeof record.audio_base64!=="string"||record.audio_base64.length>12_000_000||!/^[A-Za-z0-9+/=\s]+$/.test(record.audio_base64))throw Error("Invalid encoded audio");
    bytesTotal+=record.audio_base64.length;
    if(bytesTotal>26*1024*1024)throw Error("Audio memory cap exceeded");
    const binary=atob(record.audio_base64.replace(/\s+/g,""));
    const bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));
    const digest=[...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))].map(x=>x.toString(16).padStart(2,"0")).join("");
    if(digest!==record.sha256.toLowerCase())throw Error("Audio checksum mismatch");
    const types=["audio/webm","audio/ogg","audio/mp4","audio/mpeg","audio/x-m4a"];
    const mime=types.find(t=>String(record.media_type||"").startsWith(t))||"audio/webm";
    const url=URL.createObjectURL(new Blob([bytes],{type:mime}));newUrls.push(url);
    entries.push(newRecord({id:String(record.recording_id||""),passage,edition:"engwebp",hash:digest,mime,url,
      right:String(record.recording_license||"unknown"),reader:String(record.reader_name||"undisclosed"),mode:"verified-local-audio"}));
   }
  }else if(pkg.schema==="static-collective.witness-freeplay-review.v1"&&pkg.source?.project==="WITNESS"){
   if(!Array.isArray(pkg.sample)||pkg.sample.length>120)throw Error("Malformed review sample");
   if(pkg.awards?.Deeds!==0||pkg.awards?.Harvests!==0||pkg.awards?.Capacity!==0)throw Error("Foreign awards not accepted");
   for(const record of pkg.sample){
    const passage=passageForRecording(record.passage);
    if(!passage||!/^[a-f0-9]{64}$/i.test(record.sha256||"")||!record.edition)throw Error("Invalid metadata reference");
    entries.push(newRecord({id:String(record.recordingId||""),passage,edition:record.edition,hash:record.sha256,right:record.declaredRights,reader:record.declaredReader,mode:"metadata-only"}));
   }
  }else if(pkg.schema==="static-collective.witness-pact-full-measure-candidate.v1"&&pkg.source?.project==="WITNESS community audio Bible"){
   if(pkg.bridge?.withdrawn)throw Error("Withdrawn reference");
   if(pkg.awards?.Deeds!==0||pkg.awards?.Harvests!==0||pkg.awards?.Capacity!==0)throw Error("Foreign awards not accepted");
   const record=pkg.recording,passage=passageForRecording(record?.passage);
   if(!passage||!/^[a-f0-9]{64}$/i.test(record.sha256||"")||!record.edition)throw Error("Invalid PACT recording reference");
   entries.push(newRecord({id:String(record.recordingId||""),passage,edition:record.edition,hash:record.sha256,mode:"metadata-only"}));
  }else{
   throw Error("Expected WITNESS v1 Matthew 5 audio or a supported metadata-only candidate");
  }
  if(entries.some(r=>!r.id||r.id.length>200))throw Error("Invalid recording ID");
  // A locally provided file can be forged; even SHA verification authenticates bytes only.
  clearAudio();loadedAudio=entries;urls=newUrls;
  $("audioStatus").textContent=entries.length+" recording(s) loaded. "+
    entries.filter(x=>x.url).length+" exact audio checksum(s) verified on this device. No audio uploaded.";
  renderAudio();renderProgress();
 }catch(e){newUrls.forEach(url=>URL.revokeObjectURL(url));throw e}
}
function renderAudio(){
 for(const p of world.passages){
  const holder=$("audio-"+p.locator.replaceAll(".","-"));if(!holder)continue;
  holder.replaceChildren();
  const associated=loadedAudio.filter(r=>r.passage===p.locator);
  for(const record of associated){
   const box=node("div",undefined,"recording");
   box.append(node("strong",record.edition+" · "+(record.url?"Audio checked locally":"Recording reference only")));
   box.append(node("small","ID "+record.id+" · SHA "+record.hash.slice(0,16)+"…"));
   if(record.reader)box.append(node("small","Declared reader: "+record.reader+" (not verified identity)"));
   if(record.right)box.append(node("small","Declared contribution permission: "+record.right));
   if(record.url){
    const player=document.createElement("audio");
    player.controls=true;player.preload="none";player.src=record.url;box.append(player);
   }
   box.append(node("small","The Greek passage and this English voice share an address only. Voice identity and textual fidelity remain unverified."));
   holder.append(box);
  }
 }
 const box=$("witnessList");box.replaceChildren();
 if(!loadedAudio.length){
  box.append(node("p","No recordings loaded. Greek exploration is independent of WITNESS."));return;
 }
 const verses=new Set(loadedAudio.map(r=>r.passage));
 box.append(node("p",loadedAudio.length+" individual recording reference(s) at "+verses.size+" passage address(es)."));
 for(const passage of verses){
  const button=node("button","Visit Greek "+passage,"word");
  button.onclick=()=>openPassage(passage);box.append(button);
 }
}
$("witnessImport").addEventListener("change",async e=>{
 const file=e.target.files?.[0];if(!file)return;
 try{await readWITNESS(file)}catch(err){$("audioStatus").textContent="Import refused: "+err.message}
 finally{e.target.value=""}
});
$("clearAudio").onclick=()=>{clearAudio();$("audioStatus").textContent="Audio memory cleared. Original WITNESS files unchanged."};
$("discover").onclick=()=>{
 const fresh=world.passages.filter(p=>!visited.has(p.locator));
 if(!fresh.length){updateStatus("All 48 passages have been opened. Return anywhere freely.");return}
 openPassage(fresh[Math.floor(Math.random()*fresh.length)].locator);
};
$("random").onclick=()=>openPassage(world.passages[Math.floor(Math.random()*world.passages.length)].locator);
$("previousWord").onclick=()=>{if(current){const p=byAddress.get(current)?.neighbors.previous;if(p)openWord(p)}};
$("nextWord").onclick=()=>{if(current){const p=byAddress.get(current)?.neighbors.next;if(p)openWord(p)}};
$("reset").onclick=()=>{
 if(!confirm("Clear this browser's local Greek exploration marks? Source texts and WITNESS packages stay untouched."))return;
 visited.clear();try{localStorage.removeItem(visitKey)}catch{}
 renderProgress();updateStatus("Local journey marks cleared.");
};
$("export").onclick=()=>{
 const packet={
  schema:"static-collective.revival-matthew5-journey-review.v1",
  source:{project:"REVIVAL",edition:"sblgnt-v1.2",sourceFixtureSha256:source.receipt.source_fixture_sha256,
    worldProjectionSha256:source.receipt.projection_sha256,license:"CC BY 4.0"},
  journey:{visitedPassages:world.passages.filter(p=>visited.has(p.locator)).map(p=>p.locator),
    visitedGreekSegments:[...visited].filter(x=>byAddress.has(x)).sort(),
    humanAudioReferencesLoaded:loadedAudio.length},
  relationship:"WITNESS WEB engwebp shares passage addresses only; no word, text or translation alignment is asserted",
  awards:{Deeds:0,Harvests:0,Capacity:0},
  status:"LOCAL_GAME_OBSERVATION_ONLY"
 };
 const blob=new Blob([JSON.stringify(packet,null,2)],{type:"application/json"});
 const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="REVIVAL__matthew-5-journey.json";a.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
 updateStatus("Journey receipt exported. It contains no audio, private key or human-identifying recording data.");
};
buildVerses();renderProgress();
$("origin").textContent="Pinned source blob "+world.source.source_git_blob_sha1+
  " · extracted fixture SHA-256 "+world.source.fixture_sha256+
  " · world projection "+source.receipt.projection_sha256;
const hash=location.hash.slice(1);
if(hash){
 try{const address=decodeURIComponent(hash);
 if(passages.has(address))openPassage(address);
 else if(byAddress.has(address))openWord(address);
 }catch{}
}
window.addEventListener("beforeunload",()=>urls.forEach(u=>URL.revokeObjectURL(u)));
})();
</script>
</body>
</html>
"""
    return template.replace("__PAYLOAD__", payload)


def main() -> None:
    p = argparse.ArgumentParser(
        prog="python -m revival.matthew5_atlas",
        description="Build source-backed SBLGNT Matthew 5 + local WITNESS recording explorer.",
    )
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args()
    result = load_and_build_matthew5(args.root)
    html = build_matthew5_html(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    summary = {
        "output": str(args.output),
        "verse_count": len(result["world"]["passages"]),
        "display_token_rooms": len(result["world"]["rooms"]),
        "edition": result["world"]["edition"],
        "source_sha256": result["receipt"]["source_fixture_sha256"],
        "projection_sha256": result["receipt"]["projection_sha256"],
        "witness_match_type": "PASSAGE_ADDRESS_ONLY",
    }
    print(json.dumps(summary, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
