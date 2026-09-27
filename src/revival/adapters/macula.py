"""Pinned MACULA Genesis syntax adapter for Revival.

This adapter aligns MACULA lowfat morphemes to an already source-backed OSHB
specimen before admitting syntax or semantic-frame relations. It sits outside
frozen kernel v1 and does not rewrite either upstream source.
"""

from __future__ import annotations

import hashlib
from typing import Any
import xml.etree.ElementTree as ET

from ..kernel.v1 import sha256


ADAPTER_ID = "macula-lowfat-object-relations-v1"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def _raw_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _validate_manifest(manifest: dict[str, Any]) -> None:
    required = (
        "source_id",
        "project",
        "verse_id",
        "upstream_repository",
        "upstream_commit",
        "upstream_path",
        "upstream_blob_sha",
        "fixture_sha256",
        "license",
        "attribution",
    )
    missing = [key for key in required if key not in manifest]
    if missing:
        raise ValueError(
            "MACULA source manifest missing required fields: "
            + ", ".join(missing)
        )


def _oshb_raw_surface(token: dict[str, Any]) -> str:
    annotation = token.get("annotations", {}).get("oshb")
    if not isinstance(annotation, dict):
        raise ValueError(f"OSHB token {token.get('id')} has no oshb annotation")
    data = annotation.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("raw_surface"), str):
        raise ValueError(f"OSHB token {token.get('id')} has no raw_surface")
    return data["raw_surface"]


def _word_position(ref: str, verse_id: str) -> int:
    prefix = verse_id + "!"
    if not ref.startswith(prefix):
        raise ValueError(f"MACULA ref {ref!r} is outside {verse_id!r}")
    try:
        position = int(ref[len(prefix):])
    except ValueError as exc:
        raise ValueError(f"invalid MACULA word ref: {ref!r}") from exc
    if position < 1:
        raise ValueError(f"invalid MACULA word position: {position}")
    return position


def _descendant_words(node: ET.Element) -> list[ET.Element]:
    return [item for item in node.iter() if _localname(item.tag) == "w"]


def _nearest_ancestor(
    parent_map: dict[ET.Element, ET.Element],
    node: ET.Element,
    predicate,
) -> ET.Element | None:
    current = parent_map.get(node)
    while current is not None:
        if predicate(current):
            return current
        current = parent_map.get(current)
    return None


def _parse_frame(frame: str | None) -> dict[str, list[str]]:
    roles: dict[str, list[str]] = {}
    if not frame:
        return roles
    current_role: str | None = None
    for chunk in frame.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" in chunk:
            role, value = chunk.split(":", 1)
            current_role = role.strip()
            roles.setdefault(current_role, [])
            if value.strip():
                roles[current_role].append(value.strip())
        elif current_role is not None:
            roles[current_role].append(chunk)
        else:
            raise ValueError(f"unparseable MACULA frame chunk: {chunk!r}")
    return roles


def adapt_macula_object_relations(
    xml_text: str,
    manifest: dict[str, Any],
    oshb_specimen: dict[str, Any],
) -> dict[str, Any]:
    """Align pinned MACULA GEN 1:1 syntax to OSHB and emit object relations."""
    _validate_manifest(manifest)
    fixture_sha = _raw_sha256(xml_text)
    if fixture_sha != manifest["fixture_sha256"]:
        raise ValueError(
            "MACULA fixture SHA-256 mismatch: "
            f"expected {manifest['fixture_sha256']}, got {fixture_sha}"
        )

    if oshb_specimen["witness"]["locator"] != "Gen.1.1":
        raise ValueError("Revival 009 MACULA proof requires OSHB Gen.1.1")

    root = ET.fromstring(xml_text)
    sentence = next(
        (
            item for item in root.iter()
            if _localname(item.tag) == "sentence"
            and item.attrib.get("id") == manifest["verse_id"]
        ),
        None,
    )
    if sentence is None:
        raise ValueError(
            f"MACULA fixture does not contain sentence {manifest['verse_id']!r}"
        )

    oshb_tokens = oshb_specimen.get("tokens", [])
    words = [
        item for item in sentence.iter()
        if _localname(item.tag) == "w"
    ]
    if not words:
        raise ValueError("MACULA sentence has no word/morpheme elements")

    by_ref: dict[str, list[ET.Element]] = {}
    by_xml_id: dict[str, ET.Element] = {}
    for word in words:
        ref = word.attrib.get("ref")
        xml_id = word.attrib.get(XML_ID)
        if not ref or not xml_id:
            raise ValueError("MACULA word requires ref and xml:id")
        by_ref.setdefault(ref, []).append(word)
        if xml_id in by_xml_id:
            raise ValueError(f"duplicate MACULA xml:id: {xml_id}")
        by_xml_id[xml_id] = word

    alignment_by_xml_id: dict[str, dict[str, Any]] = {}
    word_alignment: list[dict[str, Any]] = []
    for ref, morphemes in sorted(
        by_ref.items(),
        key=lambda item: _word_position(item[0], manifest["verse_id"]),
    ):
        position = _word_position(ref, manifest["verse_id"])
        if position > len(oshb_tokens):
            raise ValueError(
                f"MACULA word position {position} exceeds OSHB token count"
            )
        oshb_token = oshb_tokens[position - 1]
        macula_surfaces = [
            item.attrib.get("unicode") or "".join(item.itertext())
            for item in morphemes
        ]
        reconstructed = "/".join(macula_surfaces)
        oshb_raw = _oshb_raw_surface(oshb_token)
        if reconstructed != oshb_raw:
            raise ValueError(
                f"MACULA/OSHB surface mismatch at {ref}: "
                f"{reconstructed!r} != {oshb_raw!r}"
            )

        record = {
            "ref": ref,
            "word_position": position,
            "oshb_token_id": oshb_token["id"],
            "oshb_raw_surface": oshb_raw,
            "macula_morpheme_ids": [
                item.attrib[XML_ID] for item in morphemes
            ],
            "macula_morpheme_surfaces": macula_surfaces,
        }
        word_alignment.append(record)

        for component_index, morpheme in enumerate(morphemes):
            alignment_by_xml_id[morpheme.attrib[XML_ID]] = {
                **record,
                "component_index": component_index,
                "macula_xml_id": morpheme.attrib[XML_ID],
                "macula_surface": macula_surfaces[component_index],
            }

    if len(word_alignment) != len(oshb_tokens):
        raise ValueError(
            "MACULA/OSHB word count mismatch: "
            f"{len(word_alignment)} != {len(oshb_tokens)}"
        )

    parent_map = {
        child: parent
        for parent in sentence.iter()
        for child in list(parent)
    }

    markers = [
        word for word in words
        if word.attrib.get("class") == "om"
        and word.attrib.get("type") == "direct object marker"
    ]
    if not markers:
        raise ValueError("MACULA sentence has no direct object markers")

    relations: list[dict[str, Any]] = []
    for marker in markers:
        marker_xml_id = marker.attrib[XML_ID]
        marker_alignment = alignment_by_xml_id[marker_xml_id]

        marker_phrase = _nearest_ancestor(
            parent_map,
            marker,
            lambda item: (
                _localname(item.tag) == "wg"
                and item.attrib.get("rule") == "OmpNP"
            ),
        )
        if marker_phrase is None:
            raise ValueError(
                f"MACULA marker {marker_xml_id} has no OmpNP ancestor"
            )

        marked_children = [
            child for child in list(marker_phrase)
            if _localname(child.tag) == "wg"
        ]
        if len(marked_children) != 1:
            raise ValueError(
                f"MACULA marker phrase {marker_xml_id} requires one marked NP child"
            )
        marked_phrase = marked_children[0]
        marked_words = _descendant_words(marked_phrase)
        marked_token_ids: list[str] = []
        marked_word_refs: list[str] = []
        for word in marked_words:
            xml_id = word.attrib[XML_ID]
            aligned = alignment_by_xml_id[xml_id]
            if aligned["oshb_token_id"] not in marked_token_ids:
                marked_token_ids.append(aligned["oshb_token_id"])
            if aligned["ref"] not in marked_word_refs:
                marked_word_refs.append(aligned["ref"])

        object_node = _nearest_ancestor(
            parent_map,
            marker_phrase,
            lambda item: (
                _localname(item.tag) == "wg"
                and item.attrib.get("role") == "o"
            ),
        )
        if object_node is None:
            raise ValueError(
                f"MACULA marker {marker_xml_id} has no role=o object ancestor"
            )

        clause = _nearest_ancestor(
            parent_map,
            object_node,
            lambda item: (
                _localname(item.tag) == "wg"
                and item.attrib.get("class") == "cl"
            ),
        )
        if clause is None:
            raise ValueError(
                f"MACULA object for {marker_xml_id} has no clause ancestor"
            )

        governing_verbs = [
            item for item in list(clause)
            if _localname(item.tag) == "w"
            and item.attrib.get("role") == "v"
        ]
        if len(governing_verbs) != 1:
            raise ValueError(
                f"MACULA clause for {marker_xml_id} requires one direct role=v word"
            )
        verb = governing_verbs[0]
        verb_xml_id = verb.attrib[XML_ID]
        verb_alignment = alignment_by_xml_id[verb_xml_id]

        frame = _parse_frame(verb.attrib.get("frame"))
        a1_xml_ids = [
            ("o" + item if not item.startswith("o") else item)
            for item in frame.get("A1", [])
        ]
        unknown_frame_ids = [
            item for item in a1_xml_ids if item not in alignment_by_xml_id
        ]
        if unknown_frame_ids:
            raise ValueError(
                "MACULA A1 frame references unknown ids: "
                + ", ".join(unknown_frame_ids)
            )

        a1_heads = [
            {
                "macula_xml_id": xml_id,
                "oshb_token_id": alignment_by_xml_id[xml_id]["oshb_token_id"],
                "source_surface": oshb_tokens[
                    alignment_by_xml_id[xml_id]["word_position"] - 1
                ]["surface"],
            }
            for xml_id in a1_xml_ids
            if alignment_by_xml_id[xml_id]["oshb_token_id"]
            in marked_token_ids
        ]
        if len(a1_heads) != 1:
            raise ValueError(
                f"expected one A1 head inside marked phrase for {marker_xml_id}"
            )

        relation = {
            "id": f"macula:{manifest['verse_id']}:{marker_xml_id}",
            "kind": "direct-object-marker-relation",
            "marker": {
                "macula_xml_id": marker_xml_id,
                "oshb_token_id": marker_alignment["oshb_token_id"],
                "oshb_component_index": marker_alignment["component_index"],
                "source_surface": oshb_tokens[
                    marker_alignment["word_position"] - 1
                ]["surface"],
                "macula_surface": marker_alignment["macula_surface"],
                "type": marker.attrib.get("type"),
                "class": marker.attrib.get("class"),
            },
            "governing_verb": {
                "macula_xml_id": verb_xml_id,
                "oshb_token_id": verb_alignment["oshb_token_id"],
                "source_surface": oshb_tokens[
                    verb_alignment["word_position"] - 1
                ]["surface"],
                "role": verb.attrib.get("role"),
                "frame": verb.attrib.get("frame"),
            },
            "marked_phrase": {
                "macula_rule": marked_phrase.attrib.get("rule"),
                "macula_class": marked_phrase.attrib.get("class"),
                "word_refs": marked_word_refs,
                "oshb_token_ids": marked_token_ids,
                "source_surfaces": [
                    next(
                        token["surface"]
                        for token in oshb_tokens
                        if token["id"] == token_id
                    )
                    for token_id in marked_token_ids
                ],
            },
            "syntax_evidence": {
                "clause_rule": clause.attrib.get("rule"),
                "object_role": object_node.attrib.get("role"),
                "object_rule": object_node.attrib.get("rule"),
                "marker_phrase_rule": marker_phrase.attrib.get("rule"),
                "marked_phrase_rule": marked_phrase.attrib.get("rule"),
                "source": manifest["source_id"],
                "layer": manifest.get("layers", {}).get("syntax"),
            },
            "semantic_frame_evidence": {
                "role": "A1",
                "matched_heads": a1_heads,
                "source_frame": verb.attrib.get("frame"),
                "source": manifest["source_id"],
                "layer": manifest.get("layers", {}).get("semantic_frame"),
            },
            "authority": {
                "project": manifest["project"],
                "license": manifest["license"],
                "attribution": manifest["attribution"],
                "upstream_commit": manifest["upstream_commit"],
                "upstream_path": manifest["upstream_path"],
                "upstream_blob_sha": manifest["upstream_blob_sha"],
            },
        }
        relations.append(relation)

    layer_core = {
        "kind": "macula-object-relations",
        "source_id": manifest["source_id"],
        "verse_id": manifest["verse_id"],
        "oshb_witness_id": oshb_specimen["witness"]["id"],
        "word_alignment": word_alignment,
        "relations": relations,
    }
    adapter_receipt = {
        "adapter": ADAPTER_ID,
        "fixture_sha256": fixture_sha,
        "upstream_commit": manifest["upstream_commit"],
        "upstream_path": manifest["upstream_path"],
        "upstream_blob_sha": manifest["upstream_blob_sha"],
        "oshb_witness_sha256": sha256(oshb_specimen["witness"]),
        "alignment_sha256": sha256(word_alignment),
        "relations_sha256": sha256(relations),
        "layer_sha256": sha256(layer_core),
    }

    return {
        **layer_core,
        "adapter_receipt": adapter_receipt,
        "manifest": manifest,
    }
