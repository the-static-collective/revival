# Revival

> **A source-backed custom Bible compiler. Choose how Scripture is rendered, explored, and eventually inhabited without losing the path back to its witnesses and the choices that produced the view.**

Revival treats the Bible as a **curiosity engine**.

The goal is not one more fixed translation. The goal is a source-backed kernel from which people can compile different linguistic outputs, scholarly views, creative representations, and eventually **inhabitable worlds and worlds within that world**.

```text
source-backed Bible kernel
          ↓
 attributable linguistic layers
          ↓
   your projection recipe
          ↓
      compiled Bible
          ↓
    trace + delta + receipt
```

**Provenance is the trust floor, not the product.**

It exists so the projections can go farther.

## The Revival part

One person may want source order.

Another may want readable English.

Another may want names transliterated instead of translated, morphology exposed, grammatical operators retained, or ambiguities left visibly unresolved.

Another may want to enter Scripture through a person, place, object, journey, conversation, sound, room, city, wilderness, or reconstructed world.

Those can all be different descendants of the same source-backed material.

They do not have to look alike.

They do have to remain attributable.

> **The Bible stops being only a fixed presentation to consume and becomes a source-grounded world you can continually re-enter from different directions.**

See [the fuller vision](docs/VISION.md).

## Try the executable proof

Requires Python 3.11+.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v

# See the available Genesis 1:1 compilation recipes.
python -m revival specimens/genesis-1-1-linguistic.json --list-recipes --pretty

# Compile a mechanical unpointed Hebrew projection.
python -m revival specimens/genesis-1-1-linguistic.json --recipe unpointed --pretty

# Compile an illustrative English-shaped reader projection.
python -m revival specimens/genesis-1-1-linguistic.json --recipe reader-demo --pretty
```

The `reader-demo` deliberately demonstrates the important behavior rather than claiming translation authority:

- its wording is explicitly marked **demo-projection-only**;
- it reorders declared source tokens;
- it explicitly renders one source token as empty;
- every output item retains the exact source token and character span behind it;
- the delta records the reordering and omission;
- the receipt changes when a wording choice changes while the witness identity stays the same.

Its current output is:

```text
In the beginning God created the heavens and the earth.
```

That sentence is **a declared demonstration projection**, not a claim that Revival has established a preferred English translation.

## Same witness, different Bible view

Revival 002 currently proves three recipes over the same held Genesis 1:1 specimen:

| Recipe | What it demonstrates |
| --- | --- |
| `surface` | exact token surfaces in source order |
| `unpointed` | a mechanical projection removing Unicode combining marks |
| `reader-demo` | declared wording, reordering, omission, and token-level trace |

A future real corpus adapter can provide attributable morphology, syntax, lemmas, discourse relations, textual witnesses, or other layers. Projection recipes can then choose how those distinctions appear—or remain unresolved—without moving that domain knowledge into the frozen kernel.

See [Linguistic Projection Recipes](docs/LINGUISTIC_RECIPES.md).

## Choose your rendering without changing the source

Revival 003 adds **preference profiles**.

The same `reader-demo` recipe now exposes an attributable choice for `אֱלֹהִים`:

```text
default → God
profile → Elohim
```

Inspect the available choices:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --list-choices \
  --pretty
```

Compile with a preference profile:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --profile profiles/genesis-1-1-elohim.json \
  --pretty
```

That produces:

```text
In the beginning Elohim created the heavens and the earth.
```

The held witness hash remains identical to the default `God` compilation. The transform and projection hashes change because the reader chose a different declared descendant.

**Preference changes the Bible you read. It does not pretend the source changed.**

See [Preference Profiles](docs/PREFERENCE_PROFILES.md).

## What must survive every compilation

Revival begins with six kernel primitives:

```text
WITNESS
ANNOTATION
TRANSFORM
PROJECTION
DELTA
RECEIPT
```

The distinctions are constitutional:

```text
content     != derivation
derivation  != lineage
lineage     != attestation

source      != annotation
annotation  != interpretation
projection  != witness
```

A readable output can be radically different from its source carrier.

That is allowed.

What is not allowed is silently forgetting **how** it became different.

## Current executable chain

```text
held Genesis 1:1 witness
        ↓
source-anchored tokens
        ↓
declared annotations
        ↓
chosen linguistic recipe
        ↓
compiled text
        ↓
token-level source trace
        ↓
explicit delta
        ↓
content-addressed receipt
```

The compiler fails closed when declared token surfaces no longer anchor into the held witness.

A changed annotation leaves the witness hash unchanged while changing the transform and projection receipt hashes.

That is the first executable form of the project's actual promise:

> **Different Bible outputs can share a source without pretending to share every linguistic decision.**

## Worlds within the world

The linguistic compiler is only the first projection surface.

Revival is designed so the same source-backed kernel can eventually feed:

- interlinear and morphology-forward Bibles;
- readable or intentionally source-shaped language;
- character, relation, dialogue, object, and place views;
- maps and timelines;
- visual and phonographic projections;
- children's exploratory surfaces;
- reconstructed rooms and environments;
- playable encounters;
- narrative worlds whose objects can lead back to passages, annotations, evidence, and unresolved disagreement.

A game, room, map, song, or reconstructed scene may become a Revival projection.

It does not become a source witness by being compelling.

## Freeze does not mean stop

Kernel generations are immutable ancestry.

When the kernel itself must evolve, Revival uses **scissors**: create a named descendant contract while preserving the prior generation exactly.

```text
kernel v1
   │
   ├── frozen ancestry
   │
   └── scissors
          ↓
       kernel v2
```

Development itself keeps provenance.

See [Scissors](docs/SCISSORS.md).

## Project boundary

Revival does **not** decide:

- biblical canon;
- textual-critical priority;
- translation quality;
- theology;
- historical truth;
- whether a reconstruction or interpretation should be accepted.

It provides machinery for those materials and decisions to remain distinguishable and inspectable.

Adapters for Scripture Burrito, USFM/USX/USJ, TEI, Universal Dependencies, Text-Fabric, BHSA, MACULA, OSHB, and other ecosystems belong outside the frozen kernel.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/revival/kernel/v1.py` | frozen-generation identity, primitive types, hashes, receipts, scissors |
| `src/revival/compiler.py` | original transform proof |
| `src/revival/linguistic.py` | source-token anchoring and recipe-driven linguistic compilation |
| `specimens/genesis-1-1.json` | original transformation specimen |
| `specimens/genesis-1-1-linguistic.json` | custom-output linguistic specimen |
| `tests/` | executable determinism, trace, delta, and ancestry claims |
| `docs/VISION.md` | Bible-as-curiosity-engine / inhabitable-world direction |
| `docs/LINGUISTIC_RECIPES.md` | current recipe contract |
| `docs/PREFERENCE_PROFILES.md` | reader-choice contract and authority boundary |
| `docs/KERNEL_V1.md` | frozen kernel contract |
| `docs/SCISSORS.md` | lawful kernel descent |

## Static Collective

> **Static Collective compass:** [Front Room](https://github.com/the-static-collective/What-is-the-static-collective-) · [Living Git Map](https://github.com/the-static-collective/What-is-the-static-collective-/tree/main/atlas)

Revival is a particular. The compass is navigation, not authority.
