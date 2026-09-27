# Object Relations

Revival 009 replaces the Aleph-Tav instrument's adjacency approximation with an attributable syntax crossing.

The key distinction is:

```text
immediate next token
  !=
marked object phrase
```

Revival now imports a pinned MACULA Genesis 1:1 lowfat syntax tree and aligns it back to the existing OSHB source-backed witness before admitting any relation.

## Two source layers, two jobs

OSHB remains the source/morphology floor:

```text
OSHB token ids
raw morpheme surfaces
lemma
morphology
```

MACULA contributes a separate syntax / semantic-frame layer:

```text
clause structure
object constituent
object-marker phrase
governing verb
verb semantic frame
```

Neither layer rewrites the other.

## Pinned MACULA source

Revival 009 pins:

```text
repository  Clear-Bible/macula-hebrew
commit      47db250bd55d0d8577f2a94fba114ef16c35b23c
path        WLC/lowfat/01-Gen-001-lowfat.xml
blob        08829ff09c7c6b06f2ae01bc980fc182c1d1a4b8
fixture     exact GEN 1:1 sentence subtree
license     CC BY 4.0
```

The fixture SHA-256 is checked before parsing.

## Alignment before relation

MACULA identifies morphemes with refs such as `GEN 1:1!6` and separate XML ids.

Revival groups those morphemes by word ref, reconstructs the slash-delimited word, and requires an exact match with the corresponding OSHB `raw_surface`.

For example:

```text
MACULA ref GEN 1:1!6
  וְ / אֵ֥ת

OSHB token 01k5P
  raw_surface = וְ/אֵ֥ת
```

If those surfaces disagree, the syntax crossing fails closed.

## Genesis 1:1 syntax evidence

The pinned MACULA tree declares the clause:

```text
PP-V-S-O
```

and marks the combined object constituent with `role="o"`.

Inside that constituent, each object marker occurs in an `OmpNP` marker phrase followed by a `DetNP` marked phrase.

For the first marker:

```text
בָּרָ֣א
   │
   └─ אֵ֥ת → הַשָּׁמַ֖יִם
```

For the second:

```text
בָּרָ֣א
   │
   └─ וְאֵ֥ת → הָאָֽרֶץ׃
```

Those arrows are no longer inferred from adjacency. They are derived from the pinned syntax tree and mapped back to OSHB token ids.

## Semantic frame stays separate

The same MACULA verb record for `בָּרָ֣א` carries:

```text
A0: 010010010031
A1: 010010010052
A1: 010010010072
```

Revival maps the two A1 heads back to:

```text
01TSc  הַשָּׁמַ֖יִם
01nPh  הָאָֽרֶץ׃
```

This is stored as **semantic-frame evidence**, separately from the syntax-tree evidence.

That separation is deliberate:

```text
syntax role != semantic role
```

The two layers agree in this verse, but agreement does not make them the same assertion.

## Open a marker relation

```bash
python -m revival.object_relations \
  corpora/oshb-v2.2-genesis-opening.json \
  --macula-xml sources/macula-hebrew/Gen.1.1-lowfat.xml \
  --macula-manifest sources/macula-hebrew/source.json \
  --locator Gen.1.1 \
  --token 01vuQ \
  --pretty
```

The room exposes three distinct door types:

```text
governing verb
marked object phrase
A1 semantic head
```

Even when two doors land on the same OSHB noun token, their evidence labels remain distinct.

## Walk it

```bash
python -m revival.object_relations_atlas \
  corpora/oshb-v2.2-genesis-opening.json \
  --macula-xml sources/macula-hebrew/Gen.1.1-lowfat.xml \
  --macula-manifest sources/macula-hebrew/source.json \
  --output /tmp/revival-object-relations.html \
  --pretty
```

Every Genesis 1:1 OSHB token is clickable. The two object-marker tokens additionally open the MACULA relation panel, where the verb, marked phrase, syntax evidence, semantic-frame evidence, and receipts are inspectable.

## Relation law

```text
adjacency != syntax
syntax != semantic frame
semantic frame != theology
agreement != identity
external annotation != witness text
```

009 does not decide that MACULA's analysis is infallible. It makes the analysis attributable, aligned, inspectable, and replaceable by another layer later.
