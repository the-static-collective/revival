# Revival

> **A provenance-preserving compiler for Scripture: immutable witnesses in, replayable scholarly and creative projections out.**

Revival asks a narrow question with large consequences:

**How far can a text lawfully transform while its ancestry remains inspectable?**

A witness may produce linguistic, scholarly, computational, visual, or creative descendants. Those descendants may be useful and radically different. They may not silently impersonate their ancestor.

```text
WITNESS
   ↓
ANNOTATION
   ↓
TRANSFORM
   ↓
PROJECTION
   ↓
DELTA
   ↓
RECEIPT
```

## Kernel law

Revival begins with six primitives:

- **WITNESS** — held source material with stable identity.
- **ANNOTATION** — attributable claims about a witness without rewriting it.
- **TRANSFORM** — an explicit operation applied to declared inputs.
- **PROJECTION** — a derived view intended for a particular use.
- **DELTA** — what changed, collapsed, disappeared, or was introduced.
- **RECEIPT** — replay evidence tying declared inputs to declared outputs.

The distinctions are constitutional:

```text
content     != derivation
derivation  != lineage
lineage     != attestation

source      != annotation
annotation  != interpretation
projection  != witness
```

## Freeze does not mean stop

A frozen kernel is immutable ancestry, not the end of development.

When the kernel needs to evolve, Revival uses **scissors**: cut forward into a named descendant contract while preserving the prior kernel exactly as historical ancestry.

```text
kernel v1
   │
   ├── frozen ancestry
   │
   └── scissors
          ↓
       kernel v2
```

No descendant silently edits its parent and calls the history unchanged.

## Genesis specimen

The first executable proof is intentionally tiny: **Genesis 1:1**.

The goal is not to settle translation or interpretation. It proves that one held witness can produce multiple deterministic projections while every declared loss remains inspectable and the derivation is replayable.

```text
Genesis 1:1 witness
        ↓
declared transforms
        ├── exact text
        └── text without Unicode marks
        ↓
explicit deltas
        ↓
content-addressed receipts
```

### Run it

Requires Python 3.11+.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m revival specimens/genesis-1-1.json --pretty
```

The second projection deliberately removes Unicode characters in General Category `M*` and records every removed code point, its original index, Unicode name, and category. The projection is allowed to lose information because the delta is not allowed to hide that loss.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/revival/kernel/v1.py` | frozen-generation identity, primitive types, hashes, receipts, scissors |
| `src/revival/compiler.py` | declared specimen transforms outside textual authority |
| `specimens/genesis-1-1.json` | first held witness and transform declaration |
| `tests/` | executable claims about determinism, witness preservation, loss, and ancestry |
| `docs/KERNEL_V1.md` | kernel contract |
| `docs/SCISSORS.md` | lawful kernel descent |

## Project boundary

Revival is not a truth engine and does not decide textual canon, translation quality, theology, or historical authority.

Adapters for formats and corpora belong **outside** the frozen kernel. Scripture Burrito, USFM/USX/USJ, TEI, Universal Dependencies, Text-Fabric, BHSA, MACULA, OSHB, and other ecosystems may become adapters or inputs without becoming kernel law.

## Static Collective

> **Static Collective compass:** [Front Room](https://github.com/the-static-collective/What-is-the-static-collective-) · [Living Git Map](https://github.com/the-static-collective/What-is-the-static-collective-/tree/main/atlas)

Revival is a particular. The compass is navigation, not authority.
