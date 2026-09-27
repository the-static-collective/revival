# Dangerous lemma doors

Revival 007 adds the first cross-passage curiosity doors.

A source-backed token can now ask the pinned corpus: where else does this exact declared lemma occur? Those occurrences become doors into other source-backed rooms.

## Proof corpus

The first corpus is intentionally tiny: OSHB v2.2 Genesis 1:1-3. Each verse remains its own witness with its own ordinary kernel receipt. The corpus layer builds a deterministic index above those witnesses.

## The first dangerous door

In the pinned source:

```text
Gen.1.1  01TyA  אֱלֹהִ֑ים  lemma=430  morph=HNcmpa
Gen.1.2  01x9c  אֱלֹהִ֔ים  lemma=430  morph=HNcmpa
Gen.1.3  01JM7  אֱלֹהִ֖ים  lemma=430  morph=HNcmpa
```

Opening Gen.1.1 / 01TyA therefore exposes lemma-occurrence doors to the real OSHB occurrences in Genesis 1:2 and Genesis 1:3. Opening either destination rebuilds the same occurrence constellation and exposes the corresponding backlinks.

## Exact identity means exact identity

Revival 007 does not normalize or decompose OSHB lemma strings. The rule is simple:

```text
lemma door iff
declared lemma string A == declared lemma string B
```

For example, Gen.1.1 / 01nPh has lemma d/776 while Gen.1.2 / 01LN3 has lemma c/d/776. They do not share a Revival 007 lemma door.

A later lexical-decomposition transform may choose to expose a relationship between those strings, but that must be a separate attributable operation rather than a hidden convenience.

## Corpus receipts

Kernel v1 receipts bind one witness. A multi-witness corpus is therefore not represented as a fake giant witness.

Revival keeps two levels:

```text
local token room
  -> ordinary single-witness kernel receipt

corpus index / cross-passage room
  -> corpus receipt
```

The corpus identity binds the corpus id, ordered witness identities and hashes, each witness compilation receipt, and the exact lemma index. A corpus-token-room receipt additionally binds the local locator/token, local witness hash, local room projection hash, occurrence-list hash, and resulting cross-passage room projection hash.

## Inspect lemma 430

```bash
python -m revival.corpus corpora/oshb-v2.2-genesis-opening.json --lemma 430 --pretty
```

Open Genesis 1:1 with cross-passage doors:

```bash
python -m revival.corpus corpora/oshb-v2.2-genesis-opening.json --locator Gen.1.1 --token 01TyA --pretty
```

## Walk it

```bash
python -m revival.corpus_atlas corpora/oshb-v2.2-genesis-opening.json --output /tmp/revival-genesis-opening.html --pretty
```

The generated Atlas contains all three source-backed verse floors. Click אֱלֹהִ֑ים in Genesis 1:1, then choose a Dangerous lemma door to move into the real OSHB occurrence in Genesis 1:2 or Genesis 1:3.

## Why dangerous?

Repeated lexical identity can invite excellent questions, but resemblance feels persuasive. The door itself does not answer those questions.

```text
same lemma != same sense
same lemma != same referent
same lemma != same relation
same lemma != same interpretation
same lemma != theological conclusion
```

The door is permission to investigate.

## Next scale

The corpus contains only three verses because Revival 007 is proving lawful cross-witness traversal, not pretending a three-verse index is a concordance.

At larger scale the same mechanism becomes:

```text
word
  -> lemma
occurrence constellation
  -> choose
another passage
  -> open
another source-backed room
  -> another door
```

That is Bible wandering rather than chapter navigation.
