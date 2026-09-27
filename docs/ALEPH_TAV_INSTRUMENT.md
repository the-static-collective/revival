# Aleph-Tav Instrument

Revival 008 turns Genesis 1:1's two OSHB direct-object-marker occurrences into a source-backed learning instrument.

The goal is not to tell a reader what Aleph-Tav secretly means. The goal is to make several layers visible at once without allowing them to impersonate one another.

## The layers

```text
written source
  != learner reading hint
  != morphology
  != projection choice
  != symbolic interpretation
```

For OSHB v2.2 Genesis 1:1 the pinned records are:

```text
01vuQ  אֵ֥ת      lemma=853    morph=HTo
01k5P  וְ/אֵ֥ת   lemma=c/853  morph=HC/To
```

OSHB's pinned morphology parser defines `T` as Particle and particle subtype `o` as `direct object marker`. It defines `C` as Conjunction.

Revival records the exact upstream morphology-code authority in `sources/oshb-v2.2/morphology-codes.json`.

## Earned decomposition

Revival aligns the three slash-delimited OSHB layers:

```text
surface  וְ / אֵ֥ת
lemma    c  / 853
morph    HC / To
```

That earns a derived family relation between the second morpheme of `c/853` and the standalone `853` token.

It does not rewrite either upstream lemma string.

```text
853 != c/853

but

decompose(c/853)
  -> c + 853
       -> 853 / Particle / direct object marker
```

## Read / letters / grammar

For the standalone marker, the instrument exposes:

```text
source surface:  אֵ֥ת
learner hint:    et
unpointed:       את
letters:         Aleph + Tav
grammar:         Particle / direct object marker
```

The `et` reading is explicitly a Revival learner hint, not OSHB source data.

The names Aleph and Tav identify the written letters. The fact that Aleph is the first Hebrew letter and Tav the last is kept behind an interpretation boundary; it is not encoded as the grammatical meaning of the particle.

## Four projection experiments

The instrument makes four visibility builds over the same source-backed verse:

```text
source    keep the adapted Hebrew surface
operator  replace the 853 marker component with [OBJ→]
letters   replace the marker component with ⟦את⟧
hidden    suppress only the marker component
```

For `וְאֵת`, that becomes:

```text
source    וְאֵת
operator  וְ + [OBJ→]
letters   וְ + ⟦את⟧
hidden    וְ
```

The hidden build is a pedagogical visibility experiment, not an English translation.

## Immediate context

For the tiny Genesis 1:1 proof, each marker room also shows the immediately following source token:

```text
01vuQ  אֵ֥ת    -> 01TSc הַשָּׁמַ֖יִם
01k5P  וְאֵ֥ת  -> 01nPh הָאָֽרֶץ׃
```

This is explicitly labeled `immediate next source token only`. Revival 008 does not claim that this is a complete syntax parse.

## Run it

Inspect the derived family:

```bash
python -m revival.aleph_tav corpora/oshb-v2.2-genesis-opening.json --pretty
```

Open the standalone marker:

```bash
python -m revival.aleph_tav corpora/oshb-v2.2-genesis-opening.json --locator Gen.1.1 --token 01vuQ --pretty
```

Open the prefixed marker:

```bash
python -m revival.aleph_tav corpora/oshb-v2.2-genesis-opening.json --locator Gen.1.1 --token 01k5P --pretty
```

Build the walkable learning instrument:

```bash
python -m revival.aleph_tav_atlas corpora/oshb-v2.2-genesis-opening.json --output /tmp/revival-aleph-tav.html --pretty
```

## Instrument law

```text
letters != pronunciation
pronunciation != grammar
grammar != translation
translation != interpretation
derived family != rewritten source identity
first/last-letter symbolism != direct-object-marker grammar
```

The layers can converse. They cannot silently collapse.
