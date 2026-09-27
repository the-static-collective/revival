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

## Open a word

Revival 004 makes the curiosity engine executable at token scale.

Open the source-backed room behind the current rendering of `אֱלֹהִים`:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --open-token g3 \
  --pretty
```

The room contains the exact held source token and span, its current rendering, available rendering alternatives, declared annotations, source-order neighbors, output-order neighbors, relation doors, and receipts.

With the preference profile:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --profile profiles/genesis-1-1-elohim.json \
  --open-token g3 \
  --pretty
```

the room still opens on the same Hebrew source token, but its current compiled rendering is `Elohim`.

The room also preserves two distinct neighborhoods:

```text
source order:  בָּרָא → אֱלֹהִים → אֵת
output order:  In the beginning → God/Elohim → created
```

and exposes explicitly declared relation doors without treating those relations as source authority.

This is the first small executable form of **worlds within the world**:

```text
word
  ↓ open
source + current rendering
  ↓
alternate renderings
  ↓
neighbors + relations
  ↓
more doors
```

See [Curiosity Rooms](docs/CURIOSITY_ROOMS.md).

## Walk the compiled Bible

Revival 005 packages the current curiosity world into one standalone HTML file:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --build-atlas dist/genesis-1-1.html \
  --pretty
```

Open `dist/genesis-1-1.html` in a browser.

The compiled verse becomes a clickable floor. Each rendered token opens its source-backed room; source-order neighbors, compiled-order neighbors, and declared relation doors are walkable; alternate renderings remain explicit previews rather than hidden mutations.

Compile the `Elohim` preference into its own inhabitable descendant:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --profile profiles/genesis-1-1-elohim.json \
  --build-atlas dist/genesis-1-1-elohim.html \
  --pretty
```

Same witness. Different compiled world. Separate receipt.

The Atlas is deterministic, local, dependency-free at runtime, and contains no network calls. Imported source/annotation text is embedded as inert JSON data and rendered with browser `textContent`.

See [Curiosity Atlas](docs/CURIOSITY_ATLAS.md).

## REAL FOOD: compile from a pinned linguistic corpus

Revival 006 crosses the first real external source boundary.

Instead of hand-authored demonstration token metadata, Revival can now adapt **Open Scriptures Hebrew Bible (OSHB) v2.2** Genesis 1:1 from pinned OSIS XML.

The source is fixed to upstream release `v.2.2`, commit `6a5db284c715c18b239422e57bb89684e6a19f00`, and the specific `wlc/Gen.xml` Git blob recorded in the source manifest.

Generate a Revival specimen:

```bash
python -m revival.adapters.oshb \
  sources/oshb-v2.2/Gen.1.1.xml \
  --manifest sources/oshb-v2.2/source.json \
  --output /tmp/oshb-genesis-1-1.json
```

Then open the real OSHB record behind `אֱלֹהִ֑ים`:

```bash
python -m revival /tmp/oshb-genesis-1-1.json \
  --recipe surface \
  --open-token 01TyA \
  --pretty
```

That room now carries actual upstream data:

```text
OSHB word id: 01TyA
surface:      אֱלֹהִ֑ים
lemma:        430
morphology:   HNcmpa
```

Build it into the Atlas:

```bash
python -m revival /tmp/oshb-genesis-1-1.json \
  --recipe surface \
  --build-atlas /tmp/oshb-genesis-1-1.html \
  --pretty
```

The Atlas exposes the OSHB record under **Declared layers** inside the word room.

The adapter performs no Unicode normalization. It preserves OSHB's immutable word ids, raw word surfaces, lemma/morphology attributes, morpheme segmentation, source/license metadata, and the exact upstream pointers behind the fixture.

The Revival textual witness is explicitly a **deterministic carrier derived from the pinned OSIS representation**: morpheme `/` markers are removed from display surfaces, OSIS segment text is attached to the preceding word, and U+0020 spaces are inserted between words. Those rules are in the adapter receipt rather than hidden.

See [OSHB Adapter](docs/OSHB_ADAPTER.md) and [source attribution](sources/oshb-v2.2/ATTRIBUTION.md).

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
| `src/revival/curiosity.py` | replayable token curiosity rooms and relation doors |
| `src/revival/atlas.py` | deterministic standalone walkable HTML Atlas |
| `src/revival/adapters/oshb.py` | pinned OSHB OSIS → Revival source adapter |
| `specimens/genesis-1-1.json` | original transformation specimen |
| `specimens/genesis-1-1-linguistic.json` | custom-output linguistic specimen |
| `tests/` | executable determinism, trace, delta, and ancestry claims |
| `docs/VISION.md` | Bible-as-curiosity-engine / inhabitable-world direction |
| `docs/LINGUISTIC_RECIPES.md` | current recipe contract |
| `docs/PREFERENCE_PROFILES.md` | reader-choice contract and authority boundary |
| `docs/CURIOSITY_ROOMS.md` | source-backed token rooms and traversal law |
| `docs/CURIOSITY_ATLAS.md` | standalone walkable presentation contract |
| `docs/OSHB_ADAPTER.md` | first real external linguistic source crossing |
| `sources/oshb-v2.2/` | pinned Genesis 1:1 fixture, source manifest, attribution |
| `docs/KERNEL_V1.md` | frozen kernel contract |
| `docs/SCISSORS.md` | lawful kernel descent |

## Static Collective

> **Static Collective compass:** [Front Room](https://github.com/the-static-collective/What-is-the-static-collective-) · [Living Git Map](https://github.com/the-static-collective/What-is-the-static-collective-/tree/main/atlas)

Revival is a particular. The compass is navigation, not authority.
