# OSHB adapter — Revival 006 REAL FOOD

Revival 006 introduces the first external source adapter: **Open Scriptures Hebrew Bible (OSHB) v2.2**.

The point is not to make OSHB part of the frozen Revival kernel.

The point is to prove that a real, attributable linguistic corpus can cross the boundary into Revival while its own identity, license, word ids, linguistic annotations, and transformation rules remain inspectable.

## Pinned upstream

This adapter specimen is pinned to:

- project: Open Scriptures Hebrew Bible;
- release: `v.2.2`;
- upstream commit: `6a5db284c715c18b239422e57bb89684e6a19f00`;
- upstream file: `wlc/Gen.xml`;
- upstream Git blob: `dcc8be362134981d3054e9b64d3a465d08492a33`;
- verse: `Gen.1.1`.

The checked-in fixture is a small standalone XML wrapper around the pinned Genesis 1:1 word and segment elements. Its own SHA-256 is declared in `sources/oshb-v2.2/source.json` and verified before adaptation.

## License and attribution

The upstream project states that the **Westminster Leningrad Codex text is Public Domain**.

OSHB lemma and morphology data are **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

The required attribution is preserved in:

`sources/oshb-v2.2/ATTRIBUTION.md`

The source manifest travels into the generated Revival specimen under `source_backing`.

## Real Genesis 1:1 word records

The pinned source gives these immutable OSHB word ids:

```text
01xeN  בְּ/רֵאשִׁ֖ית
01Nvk  בָּרָ֣א
01TyA  אֱלֹהִ֑ים
01vuQ  אֵ֥ת
01TSc  הַ/שָּׁמַ֖יִם
01k5P  וְ/אֵ֥ת
01nPh  הָ/אָֽרֶץ
```

For example, OSHB v2.2 declares for `01TyA`:

```text
surface: אֱלֹהִ֑ים
lemma:   430
morph:   HNcmpa
n:       1
```

Revival preserves those values as an attributable `oshb` linguistic record attached to token `01TyA`.

It does not reinterpret the morphology code inside the adapter.

## No Unicode normalization

The OSHB README explicitly cautions consumers against Unicode normalization.

Revival therefore performs **no NFC/NFD/NFKC/NFKD normalization** in this adapter.

This is testable on the real first word: OSHB's combining-mark order in `בְּרֵאשִׁ֖ית` differs from NFC order.

The adapter preserves the parsed code-point order exactly except for explicitly documented structural transformations below.

## Adapter transformations

OSHB's OSIS representation is not identical to Revival's token carrier.

The adapter therefore records the crossing rather than pretending no crossing happened.

For Revival 006:

1. each OSHB `<w>` keeps its immutable OSHB `id` as the Revival token id;
2. `lemma`, `morph`, optional `n`, and the raw word surface are preserved in the `oshb` annotation;
3. literal `/` characters used by OSHB to expose morpheme boundaries are removed from the Revival display surface, while the raw surface and split morpheme surfaces remain preserved;
4. OSIS `<seg>` text is attached to the preceding token and preserved as a typed trailing-segment record;
5. the derived witness carrier inserts one U+0020 space between word surfaces;
6. no Unicode normalization is performed.

For Genesis 1:1 the resulting source-backed Revival carrier is:

```text
בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃
```

This is a **deterministically derived textual carrier backed by the pinned OSIS source**, not a claim that the carrier is byte-identical to the upstream XML document.

## Adapter receipt

Every generated specimen contains an adapter receipt with:

- adapter id;
- fixture SHA-256;
- upstream release;
- upstream commit;
- upstream path;
- upstream Git blob;
- OSIS verse id;
- Unicode-normalization policy;
- deterministic hash of the derived Revival core.

The source pointer is additionally bound into `witness.source_note`, which means changing the pinned source identity changes the Revival witness hash even if some displayed text happens to remain the same.

## Run it

```bash
python -m revival.adapters.oshb \
  sources/oshb-v2.2/Gen.1.1.xml \
  --manifest sources/oshb-v2.2/source.json \
  --output /tmp/oshb-genesis-1-1.json
```

Then compile the real source-backed Hebrew:

```bash
python -m revival /tmp/oshb-genesis-1-1.json \
  --recipe surface \
  --pretty
```

Open the actual OSHB `אֱלֹהִ֑ים` word record:

```bash
python -m revival /tmp/oshb-genesis-1-1.json \
  --recipe surface \
  --open-token 01TyA \
  --pretty
```

Or build the first real-food Atlas:

```bash
python -m revival /tmp/oshb-genesis-1-1.json \
  --recipe surface \
  --build-atlas /tmp/oshb-genesis-1-1.html \
  --pretty
```

The Atlas room exposes the declared OSHB layer, including word id, lemma, morphology, raw surface, morpheme surfaces, and source authority label.

## Authority law

```text
external corpus != kernel
source-backed != infallible
morphology annotation != source text
adapter projection != upstream bytes
attribution != endorsement
```

OSHB can supply excellent linguistic food without silently becoming Revival's canon, textual-critical verdict, or linguistic final word.
