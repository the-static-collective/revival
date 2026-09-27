# Curiosity rooms

A Revival curiosity room is a replayable inspection projection around one source-backed token.

It is the first executable step from **custom Bible compiler** toward **Bible as curiosity engine**.

## Open a word

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --open-token g3 \
  --pretty
```

For the Genesis 1:1 demonstration, token `g3` is the held source surface:

```text
אֱלֹהִים
```

Under the default reader recipe it currently renders:

```text
God
```

Under the demo preference profile:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --profile profiles/genesis-1-1-elohim.json \
  --open-token g3 \
  --pretty
```

the same source token renders:

```text
Elohim
```

The room does not alter the witness.

## What is in a room?

A token room contains:

- witness locator;
- source token id and ordinal;
- exact source surface;
- exact source character span;
- current compiled rendering and its origin;
- the token's declared annotations;
- selectable rendering alternatives;
- previous and next token in **source order**;
- previous and next token in **compiled output order**;
- declared outgoing relations;
- declared incoming relations;
- explicit doors that can be traversed;
- the whole current compiled text;
- the receipt for the linguistic projection the room was opened inside;
- its own replay receipt as an inspection projection.

## Two neighborhoods

Source order and projection order are not collapsed.

For the current demo:

```text
held Hebrew source order:
g2 בָּרָא
g3 אֱלֹהִים
g4 אֵת

reader-demo output order:
g1 In the beginning
g3 God / Elohim
g2 created
```

Opening `g3` therefore exposes both neighborhoods.

That distinction matters because a readable language projection may reorder source material without gaining permission to rewrite source ancestry.

## Relation doors

Revival 004 also admits explicitly declared token relations.

The current specimen includes demonstration-only relations such as:

```text
g3 אֱלֹהִים
  -- demo-agent-of / "acts through" -->
g2 בָּרָא
```

and from `g2` toward the demo target tokens.

These relations exist to prove traversal. They are marked:

```text
authority: demo-relation-only
```

They are **not** claimed as grammatical, textual-critical, theological, or scholarly authority.

A future corpus adapter may supply real attributable morphology, syntax, discourse relations, entity links, geography, or other structures. Curiosity rooms should preserve the provenance and authority of whichever layer supplied each door.

## Room law

```text
room != witness
door != truth
relation != authority
neighbor != interpretation
compelling traversal != canon
```

A room composes existing material for inspection. It may not silently promote that material.

## Receipt locality

A room receipt binds:

- the held witness;
- the current compiled projection receipt;
- the opened token;
- the relations that actually touch that token.

An unrelated relation elsewhere in the specimen does not invalidate an unchanged room.

That locality is intentional. Curiosity should be inspectable without every unrelated annotation or world edge turning the whole Bible into one monolithic invalidation domain.

## Toward inhabitable Scripture

This token room is deliberately small.

The same contract can later widen into rooms for:

- persons;
- places;
- objects;
- speeches;
- scenes;
- journeys;
- households;
- cities;
- ritual spaces;
- reconstructed environments;
- maps;
- timelines;
- playable encounters.

The important continuity is:

```text
interesting thing
      ↓
open it
      ↓
see its current projection
      ↓
see where it came from
      ↓
see alternate doors
      ↓
traverse without losing ancestry
```

That is the first executable architecture for **worlds within the world**.
