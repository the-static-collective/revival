"""Revival 013: read-only game expedition across source-backed world places.

WITNESS audio Bible, THE PACT and Full Measure are distinct authorities.
The external packets are untrusted observations. An audio checksum is never a
Revival source witness; a player visit is never a source proof; a game award
is never a Full Measure Deed.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import re
from typing import Any

from .kernel.v1 import sha256

FREEPLAY = "static-collective.witness-freeplay-review.v1"
PACT_AUDIO = "static-collective.witness-pact-full-measure-candidate.v1"
PACT_QUEST = "static-collective.pact-world-review.v1"
RECEIPT_KIND = "revival-scripture-stack-expedition-013"
SHA = re.compile(r"^[0-9a-fA-F]{64}$")
PASSAGE = re.compile(
    r"^(gen(?:esis)?|mat(?:thew)?)[\.\s]+(\d{1,3})[\.\s]+(\d{1,3})$",
    re.IGNORECASE,
)
FORBIDDEN = {"token", "roomtoken", "privatekey", "apikey", "servicerolekey", "audiobase", "audioblob"}


def normalize_passage(value: Any) -> str | None:
    """Translate a narrow, known locator spelling without translating text."""
    if not isinstance(value, str):
        return None
    match = PASSAGE.fullmatch(value.strip())
    if not match:
        return None
    book = "Gen" if match[1].lower().startswith("gen") else "Matt"
    chapter, verse = int(match[2]), int(match[3])
    if chapter < 1 or verse < 1:
        return None
    return f"{book}.{chapter}.{verse}"


def _private_payload(value: Any, depth: int = 0) -> bool:
    if depth > 12:
        return True
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                return True
            if re.sub(r"[^a-z]", "", key.lower()) in FORBIDDEN:
                return True
            if _private_payload(child, depth + 1):
                return True
    elif isinstance(value, list):
        return len(value) > 250 or any(_private_payload(x, depth + 1) for x in value)
    return False


def _recording_reference(item: Any, edition_fallback: str = "") -> dict[str, Any]:
    if not isinstance(item, Mapping):
        return {"status": "HELD", "reason": "INVALID_RECORDING"}
    ident = item.get("recordingId")
    address = normalize_passage(item.get("passage"))
    edition = item.get("edition") or edition_fallback
    digest = item.get("sha256")
    if not isinstance(ident, str) or not (8 <= len(ident) <= 200):
        return {"status": "HELD", "reason": "MISSING_RECORDING_ID"}
    if not address or not isinstance(edition, str) or not edition.strip():
        return {"status": "HELD", "reason": "PASSAGE_OR_EDITION_UNKNOWN"}
    if not isinstance(digest, str) or not SHA.fullmatch(digest):
        return {"status": "HELD", "reason": "INVALID_AUDIO_SHA256"}
    return {
        "status": "CANDIDATE",
        "recording_id": ident,
        "passage": address,
        "declared_edition": edition,
        "audio_sha256": digest.lower(),
    }


def inspect_companion_packet(packet: Any) -> dict[str, Any]:
    """Bounded parser. NEVER treats supplied metadata as authenticated evidence."""
    if not isinstance(packet, Mapping):
        return {"kind": "unknown", "status": "HELD", "reason": "INVALID_PACKET", "recordings": []}
    schema = packet.get("schema")
    if _private_payload(packet):
        return {"kind": str(schema or "unknown"), "status": "HELD", "reason": "PRIVATE_OR_OVERSIZED_PAYLOAD", "recordings": []}
    if schema == FREEPLAY:
        source = packet.get("source")
        progress = packet.get("progress")
        sample = packet.get("sample")
        if (
            not isinstance(source, Mapping)
            or source.get("project") != "WITNESS"
            or not isinstance(progress, Mapping)
            or not isinstance(sample, list)
            or len(sample) > 120
            or packet.get("status") not in {"REVIEW_ONLY_UNVERIFIED", None}
        ):
            return {"kind": "witness-freeplay", "status": "HELD", "reason": "INVALID_SOURCE_OR_SAMPLE", "recordings": []}
        if packet.get("awards") != {"Deeds": 0, "Harvests": 0, "Capacity": 0}:
            return {"kind": "witness-freeplay", "status": "HELD", "reason": "FOREIGN_AWARD_CLAIM", "recordings": []}
        recs = [_recording_reference(item, str(source.get("edition") or "")) for item in sample]
        if any(r["status"] != "CANDIDATE" for r in recs):
            return {"kind": "witness-freeplay", "status": "HELD", "reason": "INVALID_RECORDING_REFERENCE", "recordings": []}
        ids = [r["recording_id"] for r in recs]
        if len(ids) != len(set(ids)):
            return {"kind": "witness-freeplay", "status": "HELD", "reason": "DUPLICATE_RECORDING_ID", "recordings": []}
        return {"kind": "witness-freeplay", "status": "UNVERIFIED", "recordings": recs, "source": "WITNESS / FREEPLAY-001"}
    if schema == PACT_AUDIO:
        src, recording, bridge = packet.get("source"), packet.get("recording"), packet.get("bridge")
        if (
            not isinstance(src, Mapping)
            or src.get("project") != "WITNESS community audio Bible"
            or not isinstance(bridge, Mapping)
            or bridge.get("withdrawn") is True
        ):
            return {"kind": "pact-audio", "status": "HELD", "reason": "INVALID_OR_WITHDRAWN_BRIDGE", "recordings": []}
        if packet.get("awards") != {"Deeds": 0, "Harvests": 0, "Capacity": 0}:
            return {"kind": "pact-audio", "status": "HELD", "reason": "FOREIGN_AWARD_CLAIM", "recordings": []}
        rec = _recording_reference(recording)
        if rec["status"] != "CANDIDATE":
            return {"kind": "pact-audio", "status": "HELD", "reason": rec["reason"], "recordings": []}
        return {"kind": "pact-audio", "status": "UNVERIFIED", "recordings": [rec], "source": "THE PACT / WITNESS metadata"}
    if schema == PACT_QUEST:
        if packet.get("awards") != {"Deeds": 0, "Harvests": 0, "Capacity": 0}:
            return {"kind": "pact-quest", "status": "HELD", "reason": "FOREIGN_AWARD_CLAIM", "recordings": []}
        return {"kind": "pact-quest", "status": "UNVERIFIED", "recordings": [], "source": "THE PACT / game claim only"}
    return {"kind": "unknown", "status": "HELD", "reason": "UNSUPPORTED_SCHEMA", "recordings": []}


def build_scripture_stack_expedition(
    revival_world: Mapping[str, Any],
    *,
    explored: Iterable[str] = (),
    companion_packets: Iterable[Any] = (),
) -> dict[str, Any]:
    """Compose a deterministic review-only expedition over existing Revival places.

    Only addresses actually present in the supplied receipted world are navigable.
    A WITNESS recording at an unrepresented passage stays an honest external door.
    """
    world = revival_world.get("world")
    receipt = revival_world.get("receipt")
    if not isinstance(world, Mapping) or not isinstance(receipt, Mapping):
        raise ValueError("requires a receipted Revival world_places result")
    if receipt.get("projection_sha256") != sha256(world):
        raise ValueError("Revival world receipt does not match its projected places")
    places = world.get("places")
    if not isinstance(places, list) or not places:
        raise ValueError("Revival world must contain its derived place addresses")
    available: dict[str, dict[str, Any]] = {}
    passage_places: dict[str, dict[str, Any]] = {}
    for place in places:
        if not isinstance(place, Mapping) or not isinstance(place.get("address"), str):
            raise ValueError("invalid source world place")
        address = place["address"]
        if address in available:
            raise ValueError("duplicate place in world")
        available[address] = dict(place)
        if place.get("kind") == "passage":
            if place.get("epistemic_status") != "source-backed":
                raise ValueError("passage cannot be promoted without source backing")
            passage_places[str(place.get("label"))] = dict(place)

    visits = sorted(set(value for value in explored if isinstance(value, str) and value in available))
    seen_kinds = {available[address].get("kind") for address in visits}
    # Each first visited distinct source address is one *local gameplay* glimmer.
    # Repeating a visit, receiving a WITNESS packet, or changing UI projection
    # does not produce new points.
    glimmers = sum(1 for address in visits if available[address].get("epistemic_status") == "source-backed")
    packets = list(companion_packets)
    if len(packets) > 20:
        raise ValueError("maximum 20 voluntary external review packets per build")
    reviews = [inspect_companion_packet(packet) for packet in packets]
    audio_links: dict[tuple[str, str], dict[str, Any]] = {}
    for report in reviews:
        if report.get("status") != "UNVERIFIED":
            continue
        for item in report["recordings"]:
            key = (item["recording_id"], item["audio_sha256"])
            locator = item["passage"]
            anchor = passage_places.get(locator)
            # Same passage address is NOT same textual edition or audio source.
            audio_links[key] = {
                "recording_id": item["recording_id"],
                "audio_sha256": item["audio_sha256"],
                "declared_edition": item["declared_edition"],
                "passage": locator,
                "status": "ADDRESS_MATCH_ONLY" if anchor else "UNMAPPED_EXTERNAL_PASSAGE",
                "revival_address": anchor["address"] if anchor else None,
                "authority": "external metadata; never a textual witness or verified audio",
            }
    addressed = sorted(audio_links.values(), key=lambda a: (a["passage"], a["recording_id"]))
    milestones = [
        {"id": "enter-world", "label": "First Door", "unlocked": bool(visits)},
        {"id": "source-token", "label": "Open a Source Word", "unlocked": "token" in seen_kinds},
        {"id": "three-passages", "label": "Three Places", "unlocked": sum(available[a].get("kind") == "passage" for a in visits) >= 3},
        {"id": "source-to-witness", "label": "Across Two Kinds of Witness", "unlocked": any(a["status"] == "ADDRESS_MATCH_ONLY" for a in addressed)},
        {"id": "honor-fog", "label": "Honor the Unmapped", "unlocked": any(a["status"] == "UNMAPPED_EXTERNAL_PASSAGE" for a in addressed)},
    ]
    core = {
        "schema": "static-collective.revival-stack-expedition.v1",
        "world": {"root": world.get("root_address"), "projection_sha256": receipt.get("projection_sha256")},
        "exploration": {"addresses": visits, "glimmers": glimmers, "milestones": milestones},
        "audio_candidates": addressed,
        "packet_reviews": [{k: v for k, v in r.items() if k != "recordings"} for r in reviews],
        "full_measure": {"Deeds": 0, "Harvests": 0, "Capacity": 0, "admitted": False},
        "boundary": [
            "audio checksum != Scripture witness identity",
            "passage address match != textual edition match",
            "local exploratory click != performed human deed",
            "projection != source",
            "WITNESS contribution != spiritual worth",
            "PACT game score != Full Measure award",
        ],
    }
    return {**core, "receipt": {"kind": RECEIPT_KIND, "sha256": sha256(core)}}
