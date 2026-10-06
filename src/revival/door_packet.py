"""Receive a portable Upper Room door without promoting it to Revival authority."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

_SCHEMA = "static.door-packet/0.1"
_TOP_KEYS = {"schema", "packetRef", "source", "anchor", "disclosure", "authority", "requestedEffect"}
_SOURCE_KEYS = {"system", "sourceRef", "doorKind"}
_ANCHOR_KEYS = {"translationId", "book", "chapter", "startVerse", "endVerse"}
_DISCLOSURE_KEYS = {"includesPrivateText", "includesHumanNote", "includesParticipantIdentity"}
_DOOR_KINDS = {"selection", "branch", "return"}


def _exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ValueError(f"{label} contains unsupported fields")


def _validate_packet(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict):
        raise ValueError("door packet must be an object")
    _exact_keys(packet, _TOP_KEYS, "door packet")
    if packet["schema"] != _SCHEMA:
        raise ValueError("unsupported door packet schema")
    if not isinstance(packet["packetRef"], str) or not packet["packetRef"].strip():
        raise ValueError("packetRef is required")
    if packet["authority"] is not None:
        raise ValueError("door packet authority must be null")
    if packet["requestedEffect"] is not None:
        raise ValueError("door packet requested effect must be null")

    source = packet["source"]
    if not isinstance(source, dict):
        raise ValueError("source must be an object")
    _exact_keys(source, _SOURCE_KEYS, "source")
    if source["system"] != "upper-room":
        raise ValueError("unsupported source system")
    if not isinstance(source["sourceRef"], str) or not source["sourceRef"].strip():
        raise ValueError("sourceRef is required")
    if source["doorKind"] not in _DOOR_KINDS:
        raise ValueError("unsupported door kind")

    disclosure = packet["disclosure"]
    if not isinstance(disclosure, dict):
        raise ValueError("disclosure must be an object")
    _exact_keys(disclosure, _DISCLOSURE_KEYS, "disclosure")
    if any(disclosure.values()):
        raise ValueError("private room material may not cross in door packet v0")

    anchor = packet["anchor"]
    if not isinstance(anchor, dict):
        raise ValueError("anchor must be an object")
    _exact_keys(anchor, _ANCHOR_KEYS, "anchor")
    if not isinstance(anchor["translationId"], str) or not anchor["translationId"].strip():
        raise ValueError("translationId is required")
    if not isinstance(anchor["book"], str) or not anchor["book"].strip():
        raise ValueError("book is required")
    for key in ("chapter", "startVerse", "endVerse"):
        if not isinstance(anchor[key], int) or isinstance(anchor[key], bool) or anchor[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if anchor["endVerse"] < anchor["startVerse"]:
        raise ValueError("verse range must be ordered")


def hold_door_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Hold an external door as a candidate only; do not resolve or interpret it."""
    _validate_packet(packet)
    return {
        "schema": "revival.external-door-candidate/0.1",
        "packetRef": packet["packetRef"],
        "source": deepcopy(packet["source"]),
        "anchor": deepcopy(packet["anchor"]),
        "status": "held",
        "revivalAddress": None,
        "authority": None,
        "claimBoundary": "external door != source witness",
    }
