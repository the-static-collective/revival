# Revival 011 — The World Has Places

Revival 010 proved that several source-backed Scripture instruments could coexist
inside one walkable world.

Revival 011 gives that world **stable places and scale**.

Its central distinction is:

> **Addressability is not semantic identity.**

A thing can become a place in the world interface before Revival claims what
kind of thing it is.

## Stable world addresses

The first proof world now has a deterministic address hierarchy:

```text
revival://oshb-v2.2-genesis-opening
  /scene/genesis-opening-proof
    /passage/Gen.1.1
      /token/01TyA
      /anchor/nominal-anchor/01TyA
```

Those are projection addresses. They identify where something lives in the
Revival world.

They do **not** claim:

- geographic coordinates;
- historical location;
- ontological identity;
- a preferred reconstruction;
- that a token's referent is literally a place.

The browser stores the selected Revival address in its URL fragment, making a
location reopenable inside the standalone artifact.

## Scale

011 introduces explicit scale:

```text
WORLD
  ↓
DECLARED SCENE CONTAINER
  ↓
SOURCE-BACKED PASSAGE
  ↓
MORPHOLOGY-EARNED ANCHOR
  ↓
SOURCE TOKEN ROOM
```

Every one of the 27 source tokens in the Genesis 1:1-3 proof corpus receives a
stable token address.

The scene level is deliberately marked **declared** rather than source-backed.
"Genesis opening proof scene" is a useful navigational container over the proof
corpus, not a claim that the source itself defines that scene boundary.

## World anchors

OSHB morphology can currently earn two kinds of higher-level anchor:

```text
N → nominal-anchor
V → verbal-anchor
```

For example:

- the source token for `הַ/שָּׁמַ֖יִם` earns a nominal anchor because the
  declared OSHB morphology contains noun POS `N`;
- the source token for `בָּרָ֣א` earns a verbal anchor because its declared
  morphology contains verb POS `V`.

The anchor remains connected to the exact source token and its existing Revival
room.

## Semantic fog is intentional

011 does **not** silently convert those morphology anchors into:

```text
person
place
object
event
```

A noun is not automatically a physical object or location. A verb is not by
itself a fully established event model.

So every current nominal/verbal anchor carries:

```text
semantic_type.status = fog
semantic_type.type   = null
```

Future attributable layers may earn those stronger world-semantic classes.

That means later Revival can distinguish things such as:

```text
morphology says noun
        !=
lexicon says place-name
        !=
historical model proposes location
        !=
reconstruction renders environment
```

Each can become another inspectable layer instead of overwriting the earlier
one.

## The map is not the territory

011 keeps four explicit laws:

```text
place != referent
address != geography
morphology != semantic type
scene container != source division
```

That is what lets Revival start behaving like an inhabitable world without
pretending that interface convenience has become textual or historical fact.

## Build it

```bash
python -m revival.world_places \
  corpora/oshb-v2.2-genesis-opening.json \
  --macula-xml sources/macula-hebrew/Gen.1.1-lowfat.xml \
  --macula-manifest sources/macula-hebrew/source.json \
  --output /tmp/revival-world-places.html \
  --pretty
```

The resulting standalone HTML retains the Revival 010 projection modes and
token-room traversal while adding:

- a world map;
- world / scene / passage / token zoom;
- morphology-earned nominal and verbal anchors;
- breadcrumb scale paths;
- stable `revival://` addresses;
- hash-address reopening;
- explicit semantic fog;
- an 011 receipt binding 010 ancestry, the place set, graph edges, and token
  address map.

## What this unlocks

Revival now has somewhere for future layers to land.

A later source-backed or attributable layer can add:

- named persons;
- named places;
- object identities;
- event structures;
- dialogue scenes;
- journeys;
- geographic coordinates;
- timelines;
- reconstructed environments;
- playable scene projections.

The key is that these can attach to existing stable addresses instead of
requiring the world to be rebuilt around a new interpretation.

The world now has places.

It does not yet pretend to know what every place means.
