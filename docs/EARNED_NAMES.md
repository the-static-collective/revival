# Revival 012 — Let The Places Earn Names

Revival 011 made the Scripture world addressable.

Revival 012 lets some of those places earn **lexical names**.

The governing distinction is:

```text
lexeme != sense != referent != world type
```

A source occurrence can now lawfully point to a named lexical identity without
Revival pretending that the passage-level meaning, referent, theology,
geography, or reconstruction has been settled.

## Pinned lexical proof

The first proof layer uses a compact, checked-in extract aligned to the
**Open Scriptures Hebrew Lexicon**.

Pinned upstream:

```text
repository: openscriptures/HebrewLexicon
commit:     21c9add13bc727d3a951361778e97e3ff7afd1ce
AugIndex:   blob 7fdfaa8b9cf83e41c72cb58ac84494f74bd6296c
Strong:     blob 6ea1abdaf8c095a634097014dea43428ea5f358f
```

The proof starts with five lexical identities:

```text
H430   אֱלֹהִים   elohim     God / god / gods
H776   אֶרֶץ      erets      earth / land
H8064  שָׁמַיִם   shamayim   heaven / heavens / sky
H4325  מַיִם      mayim      water / waters
H216   אוֹר       or         light
```

Those glosses are lexical range hints, not passage-level translation verdicts.

## Prefixes stay visible

The important mechanical proof is `H776`.

OSHB keeps the two opening occurrences distinct:

```text
Gen.1.1  d/776
Gen.1.2  c/d/776
```

Revival 012 does **not** rewrite either one to `776`.

It first decomposes the literal aligned morphemes:

```text
Gen.1.1
lemma  d / 776
morph  Td / Ncbsa

Gen.1.2
lemma  c / d / 776
morph  C / Td / Ncbsa
```

Only the morpheme aligned to the noun morphology is selected as the lexical
component.

That permits both occurrences to open the same H776 lexeme door while the
upstream declared lemma strings and prefix components remain inspectable.

This is a bridge, not a collapse.

## Lexeme places

012 adds a lexical branch to the Revival address space:

```text
revival://oshb-v2.2-genesis-opening
  /lexicon/oshb-hebrew-lexicon
    /strong/430
    /strong/776
    /strong/8064
    /strong/4325
    /strong/216
```

A lexeme place carries:

- the augmented Strong identity;
- the Open Scriptures lexical-index id;
- a Hebrew lexical form;
- transliteration;
- compact lexical range;
- occurrence-anchor backlinks;
- explicit `sense_status = fog`;
- explicit `referent_status = fog`;
- explicit semantic-world-type fog.

## Nine named anchors

The current five-entry proof names nine morphology-earned world anchors:

```text
elohim    Gen.1.1 · Gen.1.2 · Gen.1.3
erets     Gen.1.1 · Gen.1.2
shamayim  Gen.1.1
mayim     Gen.1.2
or        Gen.1.3 · Gen.1.3
```

Other nominal/verbal anchors remain unnamed when the bounded proof extract has
no entry for them.

Revival does not fill that absence with a model guess.

## What "earned name" means

An anchor receives a lexical name only when all of these succeed:

```text
held OSHB token
  ↓
literal surface / lemma / morphology morpheme alignment
  ↓
exact noun-or-verb component selection
  ↓
exact augmented Strong match
  ↓
pinned lexical proof entry
  ↓
named lexeme door
```

Failure at any step means no lexical name.

## What remains fog

Even after a name lands, these are still separate questions:

```text
What lexeme is this?
What sense is active here?
What does this occurrence refer to?
Is that referent a person/place/object/event?
Is it geographically identifiable?
How should it be translated?
How should it be reconstructed?
What theological interpretation follows?
```

012 answers only the first question where the evidence earns it.

## Build it

```bash
python -m revival.earned_names \
  corpora/oshb-v2.2-genesis-opening.json \
  --macula-xml sources/macula-hebrew/Gen.1.1-lowfat.xml \
  --macula-manifest sources/macula-hebrew/source.json \
  --lexical-proof sources/oshb-hebrew-lexicon/genesis-opening-proof.json \
  --output /tmp/revival-earned-names.html \
  --pretty
```

The standalone HTML keeps the existing Revival projection modes and world doors
while adding:

- an earned-lexeme constellation;
- occurrence backlinks;
- named-anchor rooms;
- source-token descent;
- stable hash-address reopening;
- explicit sense/referent/type fog;
- a receipt binding 011 ancestry and the lexical proof fixture.

## The next frontier

012 gives the world names without claiming entities.

That creates a lawful landing zone for later layers that actually carry:

- named-person annotation;
- named-place annotation;
- entity coreference;
- geographic data;
- event structure;
- discourse participants;
- alternate lexical analyses.

When those arrive, Revival can resolve some semantic fog without retroactively
pretending the lexicon already knew the answer.
