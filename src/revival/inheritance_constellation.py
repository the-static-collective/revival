"""Revival 016: source-backed Scripture + non-scriptural inherited possibility studio.

The Gospel or Genesis witness is NEVER inferred from social/creative repository
metadata. Curated questions are separate, reversible, speculative invitations.
"""
from __future__ import annotations

import argparse
from hashlib import sha256 as digest
from itertools import combinations
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from .jubilee_door import SOURCE_PIN, build_door
from .kernel.v1 import sha256

SCHEMA = "revival/inheritance-sources-v0"
RESULT_SCHEMA = "revival/inheritance-constellation-v0"
PIN = SOURCE_PIN
EXPECTED_OWNERS = 16
EXPECTED_LENSES = 7
OWNER_KEYS = {"id", "name", "repository", "commit", "readme", "role", "question", "authority"}
LENS_KEYS = {"id", "name", "prompt", "nextGate"}
HOLD = "SPECULATIVE_HOLD_NO_ACTION"


def _exact(value: object, names: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == names


def _hex(commit: str) -> bool:
    return bool(re.fullmatch("[0-9a-f]{40}", commit))


def load_manifest(path: Path) -> dict[str, Any]:
    source = path.read_bytes()
    if len(source) > 32_768:
        raise ValueError("Inheritance manifest too large")
    result = json.loads(source)
    if not _exact(result, {"schema", "edition", "purpose", "sourceBoundary",
                           "authority", "owners", "lenses", "sourceProof",
                           "field", "rights"}):
        raise ValueError("Unexpected or missing source manifest fields")
    if (result["schema"] != SCHEMA
        or result["sourceBoundary"] != "NON_SCRIPTURAL_OWNER_READMES_NOT_BIBLE_WITNESSES"
        or result["authority"] != "SOURCE_PINS_AS_EDITORIAL_INPUT_ONLY"
        or not isinstance(result["owners"], list)
        or len(result["owners"]) != EXPECTED_OWNERS
        or not isinstance(result["lenses"], list)
        or len(result["lenses"]) != EXPECTED_LENSES
        or not _exact(result["sourceProof"], {"producer", "upstreamWitness", "passage", "sourceCommit"})
        or result["sourceProof"]["producer"] != "revival.jubilee_door"
        or result["sourceProof"]["passage"] != "Gen.1.1"
        or result["sourceProof"]["sourceCommit"] != PIN
        or not _exact(result["field"], {"peopleEnrolled", "childrenFed", "actsWitnessed",
                                        "communitySuccessorsVerified", "endorsements"})
        or any(type(value) is not int or value != 0 for value in result["field"].values())):
        raise ValueError("Unsupported authority or fabricated field outcomes")
    ids, repos = set(), set()
    for owner in result["owners"]:
        if not _exact(owner, OWNER_KEYS):
            raise ValueError("Unexpected source owner fields")
        if (not re.fullmatch("[a-z][a-z0-9-]{2,30}", owner["id"])
            or owner["id"] in ids
            or not re.fullmatch(r"the-static-collective/[A-Za-z0-9_.-]+", owner["repository"])
            or owner["repository"] in repos
            or not _hex(owner["commit"])
            or owner["readme"] != "README.md"
            or owner["authority"] != "EDITORIAL_CANDIDATE_NOT_SOURCE_WITNESS"
            or any(not isinstance(owner[key], str) or not 2 <= len(owner[key]) <= 220
                   for key in ("name", "role", "question"))):
            raise ValueError("Invalid pinned source owner")
        ids.add(owner["id"]); repos.add(owner["repository"])
    lens_ids = set()
    for lens in result["lenses"]:
        if not _exact(lens, LENS_KEYS):
            raise ValueError("Unexpected lens fields")
        if (not re.fullmatch("[a-z][a-z0-9-]{2,20}", lens["id"])
            or lens["id"] in lens_ids
            or not isinstance(lens["prompt"], str)
            or len(lens["prompt"]) > 350
            or lens["prompt"].count("{left}") != 1
            or lens["prompt"].count("{right}") != 1
            or not re.fullmatch("[A-Z_]{8,40}", lens["nextGate"])):
            raise ValueError("Invalid or unbounded lens")
        lens_ids.add(lens["id"])
    if not _exact(result["rights"], {"scriptureAttribution", "ownerDescriptions"}):
        raise ValueError("Attribution must be retained")
    return result


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, timeout=25).stdout


def verify_owner_checkouts(manifest: dict[str, Any], source_dir: Path) -> list[dict[str, Any]]:
    """Pin and inspect ORIGINAL README bytes, do not import them as Scripture."""
    results = []
    source_dir = source_dir.resolve(strict=True)
    for owner in manifest["owners"]:
        relative = owner["repository"].split("/")[1]
        target = (source_dir / relative).resolve(strict=True)
        if target.parent != source_dir:
            raise ValueError("Source checkout escaped the explicit source directory")
        origin = _git(target, "remote", "get-url", "origin").decode().strip()
        allowed = "https://github.com/" + owner["repository"]
        if origin.rstrip("/").removesuffix(".git") != allowed:
            raise ValueError("Foreign owner origin mismatch: " + owner["id"])
        head = _git(target, "rev-parse", "HEAD").decode().strip()
        if head != owner["commit"]:
            raise ValueError("Foreign owner head mismatch: " + owner["id"])
        dirty = _git(target, "status", "--porcelain", "--untracked-files=normal")
        if dirty:
            raise ValueError("Foreign owner checkout is dirty: " + owner["id"])
        raw = _git(target, "show", head + ":" + owner["readme"])
        actual = (target / owner["readme"]).read_bytes()
        if raw != actual or not raw or len(raw) > 1_048_576:
            raise ValueError("Foreign README material mismatch: " + owner["id"])
        results.append({"id": owner["id"], "repository": owner["repository"],
                        "commit": head, "readme": owner["readme"],
                        "readmeSha256": digest(raw).hexdigest(),
                        "readmeBytes": len(raw),
                        "claim": "ORIGINAL_README_BYTES_CHECKED_NOT_SCRIPTURE"})
    return results


def make_seeds(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """840 deterministic invitations, each permanently held, never actions."""
    seeds = []
    for left, right in combinations(manifest["owners"], 2):
        for lens in manifest["lenses"]:
            seeds.append({
                "id": lens["id"] + "--" + left["id"] + "--" + right["id"],
                "lens": lens["id"],
                "sourceOwners": [left["id"], right["id"]],
                "question": lens["prompt"].replace("{left}", left["name"]).replace("{right}", right["name"]),
                "status": HOLD,
                "requires": lens["nextGate"],
                "scriptureRelation": None,
                "realWorldEffect": False,
            })
    if len(seeds) != EXPECTED_OWNERS * (EXPECTED_OWNERS - 1) // 2 * EXPECTED_LENSES:
        raise ValueError("Incomplete constellation")
    if len({seed["id"] for seed in seeds}) != len(seeds):
        raise ValueError("Duplicate seed")
    return seeds


def compile_constellation(root: Path, source_dir: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    manifest_path = root / "sources/inheritance-016/owners.json"
    manifest = load_manifest(manifest_path)
    original_readmes = verify_owner_checkouts(manifest, source_dir)
    # Original Revival-015 rebuild uses pinned OSHB/MACULA and unchanged 011 world.
    scripture = build_door(root)
    original = scripture["manifest"]
    if (original["schema"] != "revival.jubilee-source-door/0.1"
        or original["producer"]["sourceCommit"] != PIN
        or original["locator"] != "Gen.1.1"
        or original["effect"] != "NONE"
        or original["authority"] != "NONE"
        or len(original["licenses"]) != 2):
        raise ValueError("Revival original source-world proof refused")
    seeds = make_seeds(manifest)
    core = {
        "schema": RESULT_SCHEMA,
        "state": "HOLD_FOR_READ_ONLY_EXPLORATION",
        "purpose": manifest["purpose"],
        "scripture": {
            "manifestSchema": original["schema"],
            "owner": original["producer"]["repository"],
            "sourceCommit": original["producer"]["sourceCommit"],
            "locator": original["locator"],
            "address": original["revivalAddress"],
            "artifactSha256": original["artifactSha256"],
            "witnessSha256": original["witnessSha256"],
            "worldSha256": original["worldSha256"],
            "licenses": original["licenses"],
            "file": "genesis-world.html",
            "permission": "READER_OPTIONAL_NAVIGATION",
        },
        "externalSourceEvidence": original_readmes,
        "sourceOwners": manifest["owners"],
        "lenses": manifest["lenses"],
        "seeds": seeds,
        "boundaries": {
            "externalIdeasAreScripture": False,
            "externalIdeasAreTheology": False,
            "scripturePassageIsCommunityOutcome": False,
            "scriptureAutomaticallyMapsToSeed": False,
            "planningIsConsent": False,
            "generatedQuestionIsFulfilledWork": False,
            "childOrFamilyIntakeEnabled": False,
            "autonomousExternalActions": False,
            "fieldClaims": manifest["field"],
        },
        "entryPoints": ["READ_THE_SOURCE", "ASK_A_QUESTION", "EXPLORE_A_PAIR",
                        "PRINT_A_CANDIDATE", "REFUSE_AND_LEAVE"],
        "ownerPolicy": "Any source owner, reader, host or participant may refuse admission; a fork never inherits governance.",
    }
    core["receiptSha256"] = sha256(core)
    return {"constellation": core, "scripture": scripture}


_HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer"><meta name="robots" content="noindex,nofollow">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'none'; object-src 'none'; form-action 'none'; base-uri 'none'">
<title>Revival 016 — A World Worth Inheriting</title>
<style>
:root{font-family:system-ui,sans-serif;color-scheme:dark;color:#f6f0dd;background:#14241e}
*{box-sizing:border-box}body{margin:0}a{color:#f6d990}header,main,footer{max-width:1080px;margin:0 auto;padding:1.5rem}
header{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}
h1{font-size:clamp(2.9rem,7vw,6rem);letter-spacing:-.06em;line-height:1.03;margin:.8rem 0}
h2{font-size:clamp(1.5rem,4vw,2.2rem);line-height:1.15}
.eyebrow{color:#f6d990;text-transform:uppercase;letter-spacing:.14em;font-size:.75rem}
.lead{font-size:1.3rem;max-width:750px}.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}
.card{background:#254337;border:1px solid #4a6e58;padding:1.2rem;border-radius:.8rem;margin:1rem 0}
section{border-top:1px solid #58735f;margin-top:2rem;padding-top:1rem}
button,select{background:#f1dca4;color:#173122;border:0;border-radius:.5rem;font:inherit;padding:.65rem .85rem;margin:.25rem;cursor:pointer}
button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid #fff;outline-offset:3px}
label{display:block;margin:.8rem 0}select{max-width:100%;width:100%}
small{color:#c2d3c6}.pill{border:1px solid #7b987f;border-radius:2rem;padding:.4rem .75rem;display:inline-block;margin:.25rem}
#seed{min-height:13rem}#seed p{font-size:1.2rem}.quiet{opacity:.86}
@media print{body{background:#fff;color:#111}button,select,header,.controls{display:none}article{border:1px solid #888!important;background:#fff!important;color:#111!important}}
</style></head>
<body>
<header><strong>REVIVAL / INHERITANCE CONSTELLATION 016</strong><small>Offline, source-pinned, no accounts · no automatic actions</small></header>
<main><p class="eyebrow">Scripture remains Scripture. Inventions remain invitations.</p>
<h1>A world worth<br>inheriting.</h1>
<p class="lead">One source-backed Genesis world. Sixteen independently owned creative and practical projects. Seven ways to ask a question. Many possible beginnings—none of them a command.</p>
<div class="cols">
<article class="card"><div class="eyebrow">01 / SOURCE ROOM</div><h2>Read what is there.</h2>
<p>Walk the original Revival Genesis 1:1–3 proof world. Its source witnesses, morphological and syntax annotations, receipts and attribution are the evidence—not our creative prompts.</p><p><a id="scripture" href="genesis-world.html">Enter the source-backed Genesis room →</a></p>
<small>Source-backed navigation ≠ preferred interpretation or theology.</small></article>
<article class="card"><div class="eyebrow">02 / POSSIBILITY ROOM</div><h2>Imagine something new.</h2>
<p>Compose two independently owned projects with a lens. Receive one speculative question and an explicit unmet human gate. Nothing is sent to anyone.</p><p><a href="#machine">Open the possibility machine ↓</a></p>
<small>Question ≠ plan approval ≠ participation ≠ accomplishment.</small></article>
</div>
<section id="machine"><h2>Choose two doors.</h2><p>These sources have verified public README bytes at fixed Git commits. They are <em>not</em> Scripture witnesses, sponsors, or participants in a shared runtime.</p>
<div class="cols controls">
<label>First independent project<select id="left"></select></label>
<label>Second independent project<select id="right"></select></label>
<label>Perspective<select id="lens"></select></label>
</div>
<div class="controls"><button type="button" id="compose">Compose a held question</button><button type="button" id="surprise">Surprise me (deterministic)</button><button type="button" id="refuse">Refuse / clear</button><button type="button" id="print">Print candidate</button></div>
<article id="seed" class="card" aria-live="polite"><p>Choose any two source projects. Every possible output begins as HOLD.</p></article>
</section>
<section><h2>Why these rooms belong beside each other</h2>
<p>Revival's compiler shows that different renderings can retain exact ancestry while preserving unresolved meaning. The other projects explore a similar <strong>design value</strong>: transferable possibility without automatic control. This is an analogy, not a claim that Genesis teaches these software architectures.</p>
<p>The speculative machine offers 840 possible prompts across 16 sources and 7 lenses. All are <strong>editorial questions</strong>, not verified human outcomes, Scripture relations, recommendations, grants, invitations or service requests.</p>
<div class="cols"><div class="card"><h3>Make</h3><p>Try a reversible, voluntarily chosen thing together. No feeding, medical, safeguarding, or identity claim arises from software.</p></div><div class="card"><h3>Remember</h3><p>Separate what was merely proposed, reported and actually confirmed by a willing recipient.</p></div><div class="card"><h3>Inherit</h3><p>Leave enough trace and freedom for an independent successor to change or refuse the method.</p></div></div>
</section>
<section><h2>The human stop signs</h2><p>There is no child intake, contact list, automatic food dispatch, church requirement, signature authority, source reinterpretation, auto-enrollment, public private-profile, automatic publication or event booking. The fellowship remains a proposal, not a beneficiary claim. Source owner readmes may document prototypes and aspirations, not operational proof.</p>
<p><small id="receipt"></small></p></section>
</main><footer>All inputs are local. No analytics, browser storage, network calls or remote updates. Read, imagine, refuse, leave—or make something independently with other willing people.</footer>
<script type="application/json" id="inheritance-data">__PAYLOAD__</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById("inheritance-data").textContent);
const byId=id=>document.getElementById(id);
const left=byId("left"),right=byId("right"),lens=byId("lens"),seed=byId("seed");
function addOption(select,label,value){const option=document.createElement("option");option.value=value;option.textContent=label;select.append(option);}
for(const owner of data.sourceOwners){addOption(left,owner.name,owner.id);addOption(right,owner.name,owner.id);}
right.selectedIndex=1;
for(const item of data.lenses)addOption(lens,item.name,item.id);
byId("receipt").textContent="Constellation receipt: "+data.receiptSha256+" · Original Revival world artifact: "+data.scripture.artifactSha256;
byId("scripture").href="./"+data.scripture.file+"#"+encodeURIComponent(data.scripture.address);
function show(text){seed.replaceChildren();const p=document.createElement("p");p.textContent=text;seed.append(p);}
function compose(){
 const a=left.value,b=right.value,l=lens.value;
 if(a===b){show("Choose two distinct owners; two labels for one owner do not constitute a crossing.");return;}
 const match=data.seeds.find(s=>s.lens===l&&s.sourceOwners.includes(a)&&s.sourceOwners.includes(b));
 if(!match){show("This question was not generated by the held, pinned constellation.");return;}
 seed.replaceChildren();
 const tag=document.createElement("small");tag.textContent="HOLD · EDITORIAL QUESTION · NO ACTION";
 const h=document.createElement("h3");h.textContent=match.question;
 const p=document.createElement("p");p.textContent="Next human gate: "+match.requires.replaceAll("_"," ")+". This is not permission, Scripture interpretation, or a real-world outcome.";
 const refs=document.createElement("p");refs.className="quiet";
 for(const id of match.sourceOwners){
   const o=data.sourceOwners.find(x=>x.id===id), a=document.createElement("a");
   a.href="https://github.com/"+o.repository+"/blob/"+o.commit+"/"+o.readme;
   a.rel="noopener noreferrer";a.textContent=o.name+" · original pinned README";
   refs.append(a,document.createElement("br"));
 }
 seed.append(tag,h,p,refs);
}
byId("compose").addEventListener("click",compose);
let roll=0;
byId("surprise").addEventListener("click",()=>{
 const pairs=data.seeds.filter(x=>x.lens==="nourish");
 const pair=pairs[(roll*37+3)%pairs.length];
 const l=data.lenses[(roll*3+1)%data.lenses.length];
 roll++;left.value=pair.sourceOwners[0];right.value=pair.sourceOwners[1];lens.value=l.id;compose();
});
byId("refuse").addEventListener("click",()=>show("REFUSED. No trace, application, record, account, message, or consequence was created."));
byId("print").addEventListener("click",()=>window.print());
</script></body></html>'''


def render_html(result: dict[str, Any]) -> str:
    # This is inert JSON, not executable source. All dynamic display uses textContent.
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload = (payload.replace("&", "\\u0026").replace("<", "\\u003c")
               .replace(">", "\\u003e").replace("\u2028", "\\u2028")
               .replace("\u2029", "\\u2029"))
    return _HTML.replace("__PAYLOAD__", payload)


def build_files(root: Path, sources: Path) -> dict[str, bytes]:
    bundle = compile_constellation(root, sources)
    constellation = bundle["constellation"]
    html = render_html(constellation)
    scripture_html = bundle["scripture"]["html"]
    if not scripture_html or "genesis-world.html" not in html:
        raise ValueError("Original Revival world missing")
    content = {
        "constellation.json": (json.dumps(constellation, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(),
        "inheritance-room.html": html.encode(),
        "genesis-world.html": scripture_html.encode(),
    }
    original = bundle["scripture"]["manifest"]
    manifest_core = {
        "schema": "revival/inheritance-export-v0",
        "state": "SOURCE_BOUND_HOLD",
        "sourceDoorArtifactSha256": original["artifactSha256"],
        "sourceWorldReceipt": original["worldReceipt"],
        "sourceLicenses": original["licenses"],
        "constellationReceiptSha256": constellation["receiptSha256"],
        "files": {name: digest(value).hexdigest() for name, value in content.items()},
        "actualParticipants": 0,
        "actualActions": 0,
        "authority": "NONE",
    }
    manifest_core["artifactSha256"] = sha256(manifest_core)
    content["manifest.json"] = (json.dumps(manifest_core, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    return content


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["build", "verify"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--sources", type=Path, required=True,
                        help="Directory containing 16 ORIGINAL pinned source repositories")
    args = parser.parse_args()
    files = build_files(args.root, args.sources)
    if args.mode == "build":
        args.directory.mkdir(parents=True, exist_ok=False)
        for name, content in files.items():
            (args.directory / name).write_bytes(content)
    else:
        if set(p.name for p in args.directory.iterdir()) != set(files):
            raise ValueError("Cold rebuild file set changed")
        for name, original in files.items():
            if (args.directory / name).read_bytes() != original:
                raise ValueError("Cold rebuild byte mismatch: " + name)
    packet = json.loads(files["manifest.json"])
    print(json.dumps({
        "state": "BUILT_HELD" if args.mode == "build" else "COLD_REBUILD_VERIFIED",
        "sources": EXPECTED_OWNERS, "lenses": EXPECTED_LENSES,
        "candidateQuestions": EXPECTED_OWNERS*(EXPECTED_OWNERS-1)//2*EXPECTED_LENSES,
        "artifactSha256": packet["artifactSha256"], "actualParticipants": 0,
        "actualActions": 0, "authority": "NONE",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
