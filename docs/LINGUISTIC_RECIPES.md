# Linguistic projection recipes

A Revival linguistic recipe is a **declared way of rendering source-anchored tokens**.

It is not a claim that the chosen wording is the source, the only correct translation, or even a good translation.

## Revival 002 specimen shape

A specimen contains:

1. a held witness;
2. ordered tokens whose surfaces must anchor exactly into that witness;
3. attributable annotations attached to those tokens;
4. one or more projection recipes.

A recipe currently chooses:

- an output field;
- a separator;
- an optional token order.

Revival 002 supports three field classes:

- `surface` — exact token surface from the witness;
- `unpointed` — a mechanical removal of Unicode mark characters;
- an annotation field — declared wording supplied by the specimen.

## Trace

Every emitted token records:

- source token id;
- source ordinal;
- exact source character span;
- exact source surface;
- output ordinal;
- output text and span;
- whether its wording came from the witness, a mechanical transform, or an annotation;
- annotation source/authority metadata when applicable.

An empty annotation value is allowed. It means the recipe deliberately emits nothing for that source token, and the delta records that decision.

A recipe may reorder source tokens. The delta records both source order and output order.

## Receipt identity

The kernel v1 receipt remains unchanged.

For a linguistic recipe, the `Transform` identity binds:

- the complete recipe;
- each source token selected by that recipe;
- the exact rendering input and origin selected for that token.

The witness hash independently binds the complete held witness. Unrelated annotations therefore do not invalidate an unchanged recipe output.

Therefore:

```text
same witness + changed wording choice
    → same witness hash
    → different transform hash
    → different projection hash
```

That distinction is the executable center of custom Bible compilation.

## Current limits

Revival 002 does not yet:

- import USFM, USX, USJ, Scripture Burrito, TEI, Text-Fabric, BHSA, MACULA, or OSHB;
- express phrase-level many-to-many alignment;
- model morphology or syntax as kernel authority;
- compile chapters/books;
- create graphical, audio, or playable projections.

Those are frontier work. The recipe mechanism is intended to remain beneath them rather than forcing them into a single output model.
