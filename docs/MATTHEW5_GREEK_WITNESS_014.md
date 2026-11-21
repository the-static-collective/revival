# REVIVAL 014 — Greek Matthew 5 × WITNESS: The Open Word

**Status:** Additive, rights-attributed Greek Matthew 5 source corpus and offline phonographic crosswalk. REVIVAL's frozen v1 kernel and prior Hebrew Genesis 1:1–3 witness have not changed.

## Source admission

Source: **The Greek New Testament: SBL Edition (SBLGNT) v1.2**, edited by Michael W. Holmes, © 2010 Society of Biblical Literature and Logos Bible Software.

- Official source: https://sblgnt.com/
- Original upstream repository: https://github.com/Faithlife/SBLGNT
- Pinned upstream commit: `d7f35adca9ec410e1d1499c63b4dd989d76c8d4d`
- Original upstream file: `data/sblgnt/text/Matt.txt`
- Original full-file Git blob SHA-1: `d19efbdff018c2bde83ba0fc01e0d8cb399b496b`
- Extracted fixture: `sources/sblgnt-v1.2/Matt.5.txt`, exactly the 48 `Matt 5:X` lines with original Greek surfaces, punctuation, edition marks, and trailing spaces. A final newline was supplied for the standalone extracted file. **No substantive Greek wording was changed.**
- Pinned subset Git blob SHA-1: `c30d2837313e1a47ec04c348f466b763f5ad7477`.
- License: **[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)**. This project must preserve attribution, license URL, source URL, and indicate extraction/changes. The authors/rights holders do not endorse REVIVAL.
- Provenance manifest: `sources/sblgnt-v1.2/source.json`.

The build **fails closed** if the subset bytes, 48-verse order, manifest edition, pinned upstream commit or file identities change. Every rendered passage and display-segment room is bound to a deterministic source and projection receipt.

**Edition-level limitation:** SBLGNT is a *modern critical edition*, not the original manuscript or a universal verdict among NT manuscripts. Importing its printed words does not establish original autograph text or variants. REVIVAL's 014 rooms carry **source-backed edition orthography** only.

## Why this is a distinct frontier

REVIVAL 011/013 has a source-backed **Hebrew Genesis 1:1–3** world built on pinned OSHB/MACULA linguistic evidence. WITNESS FREEPLAY-001 already provides a community audio Bible using the **World English Bible Protestant Edition** (`engwebp`) for **Matthew 5**.

REVIVAL 014 adds **SBLGNT Greek Matthew 5** in a **separate, attributable source world**. It does not pretend to import Matthew into the Genesis corpus, merge two languages into one token source, or silently claim Greek-versus-English translation equivalence.

The join is only:

```
SBLGNT edited Greek text  [Matt.5.1]
                              │
                    shared passage address
                              │
WITNESS human voice      [matthew.5.1] — WEB engwebp
```

**Same locator != same wording.** One record is a Greek critical edition's written text. The other is a human-made recording declared against a distinct English translation. Their different sources remain visible in every room.

## What is actually playable

Build the offline, mobile-responsive Greek chapter and audio game:

```bash
python -m pip install -e .
python -m unittest discover -s tests -p 'test_matthew5.py' -v

python -m revival.matthew5_atlas \
  --root . \
  --output dist/revival-matthew5-witness.html \
  --pretty
```

Open the generated `dist/revival-matthew5-witness.html`. No server, script CDN, database, login, service-role key or network connection is needed for **Greek exploration**.

1. **Open a passage** anywhere in Matthew 5. All 48 verses are represented as untouched SBLGNT display lines and separately receipted verse addresses.
2. **Tap a Greek display segment** to inspect its exact character span and token ID from the SBLGNT edition, then navigate to the previous/next segment.
3. **Discover a new passage** or choose a surprise passage. Visits earn bounded, nonredeemable *exploration glimmers*, saved only in your browser. Reopening a passage or word cannot manufacture repeated points.
4. **Import a WITNESS backup** (`witness-package` v1) exported by WITNESS Matthew 5. Every included audio blob is locally decoded and SHA-256 checked. Valid audio appears in a player alongside the corresponding Greek verse address. The Greek source/English reading distinction stays conspicuous.
5. Alternatively import **metadata-only** packets from WITNESS FREEPLAY-001 or THE PACT v0.4. These attach references by chapter/verse address only; they cannot play audio because no audio was included.
6. **Export a local journey review**, with source edition and receipt, visited passage/token addresses and count of local imported audio references. No audio blobs, voice identities, private room tokens or Scripture text are exported by that game receipt. Full Measure awards are always `0`.

Source audio never leaves the local browser via this tool. `Clear loaded audio` revokes in-memory playback object URLs. Page refresh also drops audio memory; original WITNESS files remain untouched. No shared-room recording is downloaded automatically from WITNESS's independent Supabase backend.

## Not yet claimed

- No Greek morphology, lemma, syntax, Strong's mappings, semantic frame, lexical sense, translation/word alignment, or textual-critical variants were imported for the SBLGNT Matthew 5 page. The tokens are **orthographic whitespace display units**, not scholarly lemmas.
- Local audio checksum equality confirms bytes, not the real reader's identity, audio/scripture fidelity or spoken language.
- A browser visit is not reliable evidence that somebody read, understood or believes a passage.
- THE PACT's own game achievements do not transfer automatically into REVIVAL or Full Measure.
- Full Measure Deeds, Harvests and Capacity are independent human-governed outcomes; no score conversion exists.
- This is a standalone prototype; it is not a verified live shared website, a deployed WITNESS Supabase integration, or a public broadcaster.

## Recovery and next expansion

The independent rights and source layers now form this chain:

```
REVIVAL Genesis 1:1–3 (OSHB, Hebrew)      ┐
REVIVAL Matthew 5 (SBLGNT, Greek)         ├── distinct receipted source worlds
WITNESS Matthew 5 (WEB, English audio)    ┘
                    ↓ shared address only
           reader-controlled browser view
                    ↓
          optional THE PACT challenge
                    ↓
     separate Full Measure owner review
```

Next responsible upgrades: Greek morphology from an attributable separately licensed layer, a curated *translation alignment proposal* with explicit epistemic status (not automatic word equivalence), WITNESS's voluntary direct deep-link from its player to the matching REVIVAL verse (if/when hosted), and then Matthew 6–7 with identical pinned-source provenance.

## Verification

- `python -m unittest discover -s tests -p 'test_matthew5.py' -v`
- `python -m unittest discover -s tests -v`
- `python -m revival.matthew5_atlas --root . --output dist/revival-matthew5-witness.html --pretty`

CI workflow: `.github/workflows/revival-014-matthew5.yml` publishes an offline HTML artifact for phone testing after its tests pass.

### Attribution reminder

The original SBLGNT Greek text is © 2010 Society of Biblical Literature and Logos Bible Software, under CC BY 4.0. REVIVAL's extracted Matthew 5 fixture is an edited file layout/selection; preserve the original license attribution, origin, rights, source commit, and change notice in every redistributed game.
