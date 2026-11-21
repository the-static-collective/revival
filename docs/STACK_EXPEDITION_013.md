# REVIVAL 013 — The Living Source Expedition
**Stack crossing:** REVIVAL × WITNESS (community audio Bible) × THE PACT × Full Measure  
**State:** executable candidate on an integration branch; no canonical foreign writes.

REVIVAL is the source-backed Bible compiler and walkable Scripture world—not the church event called REVIVAL and not an alternate name for WITNESS. This layer gives the fourth project an independent **gameplay organ**: walking source-backed places, source word rooms, and declared relationship doors. It connects to the others by evidence and opt-in invitations, not by collapsing authority into a universal XP ledger.

## What is actually playable

`src/revival/stack_expedition_atlas.py` compiles two linked, standalone, network-free HTML files:

- `revival-stack-expedition.html` — the player-facing expedition map, whose Genesis passage/token rooms are sourced from Revival 011's *actual compiled world places*, not from invented locations;
- `revival-world-places.html` — Revival 011's existing source-backed Atlas, with exact token rooms, provenance layers, declared lemma/syntax doors, semantic fog and receipts.

Clicking a passage or token opens its **actual Revival world address** in the companion Atlas. The expedition remembers distinct, local-only visits keyed by the existing source-world projection receipt. Each unique source-backed passage/token visit gives one nonredeemable "glimmer"; re-opening the same place cannot farm points. A local review packet can be exported, but browser clicks are not authenticated encounters or real-world proof.

REVIVAL 013 does not create a new translation, edit the frozen kernel, claim new Greek source coverage, or infer historical geography from a word's morphology. The existing receipts, source witnesses and chapter-level limitations remain intact.

### Rebuild from the pinned Genesis corpus

Requires Python 3.11+ and this repository with its existing pinned OSHB and MACULA fixtures.

```bash
python -m pip install -e .
python -m unittest discover -s tests -p 'test_stack_expedition*.py' -v

python -m revival.stack_expedition_atlas \
  corpora/oshb-v2.2-genesis-opening.json \
  --macula-xml sources/macula-hebrew/Gen.1.1-lowfat.xml \
  --macula-manifest sources/macula-hebrew/source.json \
  --companion-packet specimens/revival-013-witness-matthew5-synthetic.json \
  --output dist/revival-stack-expedition.html \
  --pretty
```

Open `dist/revival-stack-expedition.html` and keep `dist/revival-world-places.html` in the same folder. Both are standalone; no third-party JavaScript, credentials, network or server required to play.

The supplied companion packet is **synthetic**, not a real WITNESS recording. It deliberately demonstrates that a Matthew 5 recording does *not* resolve to the currently proven Genesis 1:1–3 source world.

## Crossing contract (four authorities, not one)

| Project | Offers | Cannot silently claim |
| --- | --- | --- |
| **REVIVAL** | Source-backed witness tokens, linguistic choices, word rooms, place addresses, receipts | Canon, textual-critical priority, interpretation, historical truth, or a game becoming Scripture |
| **WITNESS audio Bible** | Freely chosen recorded human readings, per-take SHA-256, passage and text edition, local/shared availability | That audio edits Scripture, that a slot proves identity, or that all readings are assigned |
| **THE PACT** | Separate human seats, voluntary quests, encouragement, peer claims and audio reference links | That a peer click verifies all claims, authorizes a foreign ledger, or publishes private audio |
| **Full Measure** | Locally owner-governed participation and its own Deeds/Harvests/Capacity authority | That imported game XP or a recording digest is a Deed or proven benefit |

### Cross-project packet surface

`src/revival/stack_expedition.py` accepts only explicitly provided, bounded **review-only** JSON from:

- `static-collective.witness-freeplay-review.v1` (WITNESS's native Living Chapter game; **metadata only**);
- `static-collective.witness-pact-full-measure-candidate.v1` (THE PACT's WITNESS audio metadata link/peer report);
- `static-collective.pact-world-review.v1` (THE PACT's separate task-consequence report, not a textual witness).

It never calls another project's database. It rejects private token/audio payloads, malformed/missing edition/digest, nonzero foreign awards, withdrawn PACT audio links, unsupported schemas and oversized packets. It inspects supplied JSON but **cannot authenticate** that the data came from the named project.

For each audio candidate:

- An exact known passage locator with a Revival source place may produce **ADDRESS_MATCH_ONLY**. It does not assert a shared textual witness, source edition, voice identity or translation equivalence.
- A passage outside the held source corpus produces **UNMAPPED_EXTERNAL_PASSAGE**. This is the expected outcome for WITNESS's Matthew 5 recorder against REVIVAL's currently executable Genesis 1:1–3 world. It keeps the audio as a *possible future door* rather than manufacturing Greek source-token rooms.
- Neither status promotes an audio digest, peer listening claim or a game projection into Revival source authority.

### Milestones and limits

The game may illuminate First Door, Open a Source Word, Three Places, Across Two Kinds of Witness (address match only), or Honor the Unmapped (explicit fog). These are illustrative **game markers**, not compliance quotas or human-spiritual scores.

At export:

```json
{
  "awards": {
    "Deeds": 0,
    "Harvests": 0,
    "Capacity": 0
  },
  "status": "LOCAL_EXPLORATION_UNVERIFIED"
}
```

No authenticated human identity, external recipient consent, benefit calculation, WITNESS publishing permission, or Full Measure admission is implied. The game does not update project-owned WITNESS recordings or PACT cloud events. It never creates a new Jubilee receipt.

## Next real expansion

The **next source frontier** is a rights-cleared, pinned Greek textual witness covering Matthew 5, aligned by passage address to WITNESS's existing WEB (English) Matthew 5 recordings **without equating their text editions**. Only after that import is actually complete should the source-backed Matthew word rooms become playable in this world. Then the full stack can support:

1. open a WITNESS recording of Matthew 5;
2. enter the corresponding REVIVAL source-backed Matthew passage room (different source/edition, same address);
3. explore attributable language and grammar, including unresolved variants;
4. return to WITNESS listening/recording or THE PACT's voluntary team adventures;
5. bring eligible outcomes to Full Measure for **separate human review**, not automatic XP-to-Deed conversion.

The whole journey should be a sequence of independently witnessed affordances, not a centralized scoreboard with fake universal authority.

## Proof obligations

The test suite checks canonical address normalization, distinct-source/edition semantics, real Genesis 011 receipt binding, deliberate Matthew 5 fog, WITNESS and PACT packet boundaries, private-key/audio rejection, zero-value Full Measure awards, local exploration deduplication, deterministic receipts, offline HTML generation, safe JSON embedding, and forbidden network calls.

Run all repository tests with `python -m unittest discover -s tests -v`.

**Non-claims:** No phone field test, browser game load test, authenticated WITNESS server-to-server bridge, production website or Full Measure canonical admission is proved by a green unit test alone.

## Project references

- [REVIVAL](https://github.com/the-static-collective/revival) — source-backed Bible compiler and source-world owner.
- [WITNESS](https://github.com/the-static-collective/WITNESS) — free-choice Scripture audio. Native game **FREEPLAY-001** is in the `genesis/community-audio-bible-001` prototype branch.
- [THE PACT](https://github.com/the-static-collective/planZ/tree/main/pact-cloud) — cooperative two-player room and metadata-only WITNESS link bridge.
- [Full Measure](https://github.com/the-static-collective/full-measure-world-layer) — world participation; [WITNESS review lens PR #59](https://github.com/the-static-collective/full-measure-world-layer/pull/59) remains draft.

> **Canonical boundary:** Scripture source is one layer. Human recording is another. Playful traversal is another. The human consequence is another. Their relation can be recorded without pretending they are the same act.
