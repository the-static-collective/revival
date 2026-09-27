"""Revival kernel v1.

This module is deliberately dependency-free. It defines identity and receipt
mechanics shared by projections without deciding textual, linguistic,
historical, or theological authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Mapping

KERNEL_VERSION = "1"
PRIMITIVES = (
    "WITNESS",
    "ANNOTATION",
    "TRANSFORM",
    "PROJECTION",
    "DELTA",
    "RECEIPT",
)


@dataclass(frozen=True)
class Witness:
    id: str
    locator: str
    language: str
    script: str
    text: str
    source_note: str


@dataclass(frozen=True)
class Transform:
    name: str
    version: str
    parameters: Mapping[str, Any]


@dataclass(frozen=True)
class Projection:
    kind: str
    content: Any


@dataclass(frozen=True)
class Delta:
    kind: str
    details: Mapping[str, Any]


@dataclass(frozen=True)
class Receipt:
    kernel_version: str
    witness_sha256: str
    transform_sha256: str
    projection_sha256: str
    delta_sha256: str


def canonical_json(value: Any) -> str:
    """Return deterministic UTF-8-safe JSON for hashing and replay."""
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def make_receipt(
    *,
    witness: Witness,
    transform: Transform,
    projection: Projection,
    delta: Delta,
) -> Receipt:
    return Receipt(
        kernel_version=KERNEL_VERSION,
        witness_sha256=sha256(witness),
        transform_sha256=sha256(transform),
        projection_sha256=sha256(projection),
        delta_sha256=sha256(delta),
    )


def scissors(
    *,
    parent_version: str,
    child_version: str,
    parent_contract_sha256: str,
    rationale: str,
) -> dict[str, str]:
    """Describe explicit kernel descent without mutating the parent."""
    if not parent_version or not child_version:
        raise ValueError("parent_version and child_version are required")
    if parent_version == child_version:
        raise ValueError("scissors require a distinct child version")
    if not parent_contract_sha256:
        raise ValueError("parent_contract_sha256 is required")
    if not rationale.strip():
        raise ValueError("rationale is required")

    return {
        "relation": "descends_from",
        "parent_version": parent_version,
        "child_version": child_version,
        "parent_contract_sha256": parent_contract_sha256,
        "rationale": rationale,
    }
