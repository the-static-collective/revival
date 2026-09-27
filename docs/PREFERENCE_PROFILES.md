# Preference profiles

Revival preference profiles let a reader choose among **already declared, attributable rendering alternatives** without editing the witness, the linguistic layer, or the projection recipe.

They are presentation choices, not source authority.

## Example

A linguistic annotation may expose:

```json
{
  "default": "god",
  "variants": [
    {
      "id": "god",
      "value": "God",
      "source": "Revival demonstration choice",
      "authority": "demo-projection-only"
    },
    {
      "id": "elohim",
      "value": "Elohim",
      "source": "Revival demonstration choice",
      "authority": "demo-projection-only"
    }
  ]
}
```

A separate preference profile may select:

```json
{
  "id": "elohim-demo",
  "recipe": "reader-demo",
  "choices": {
    "g3": "elohim"
  }
}
```

The profile does not add the word `Elohim` to the source. It selects one declared projection alternative for token `g3`.

## Identity behavior

For the same witness:

```text
default profile → "God"
reader choice   → "Elohim"
```

Revival preserves:

```text
same witness hash
different transform hash
different projection hash
```

That distinction is essential. A person's preferred Bible output may change without pretending the underlying witness changed.

## Curiosity surface

A selectable rendering is also a door.

`--list-choices` exposes the available variants, their source-token anchor, and their declared provenance:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --list-choices \
  --pretty
```

A future interface can use the same contract to ask:

- Why does this output say `God`?
- What other declared renderings exist here?
- What source token is behind this word?
- Which linguistic layer supplied the option?
- What changes if I choose another rendering?

The choice surface therefore serves both **custom compilation** and **curiosity**.

## Profile law

```text
preference != source
preference != linguistic authority
preference != canon
preference != hidden mutation
```

Profiles may choose only declared variants for tokens emitted by their declared recipe. Unknown choices, recipe mismatches, and choices outside the recipe fail closed.

## Current boundary

Revival 003 profiles select token-level rendering variants only.

They do not yet select:

- textual witnesses;
- morphology analyses;
- syntactic parses;
- phrase-level alignments;
- interpretive traditions;
- chronology models;
- reconstructed-world hypotheses.

Those may later become typed choice surfaces, but each needs its own authority and provenance contract rather than being smuggled into the token renderer.
