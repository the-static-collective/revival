# Curiosity Atlas

The Curiosity Atlas is Revival's first **walkable presentation**.

It compiles one linguistic view, opens every emitted source token as a curiosity room, and packages the resulting little world into one deterministic HTML file.

No server is required. No JavaScript package is required. The generated file contains its own replayable room data.

## Build it

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --build-atlas dist/genesis-1-1.html \
  --pretty
```

Open `dist/genesis-1-1.html` in a browser.

To inhabit the demonstration preference profile:

```bash
python -m revival specimens/genesis-1-1-linguistic.json \
  --recipe reader-demo \
  --profile profiles/genesis-1-1-elohim.json \
  --build-atlas dist/genesis-1-1-elohim.html \
  --pretty
```

Both atlases descend from the same held witness.

## What is walkable?

The compiled verse is the floor.

Every visible rendered token is a door into its source-backed room.

Inside a room you can traverse:

- source-order neighbors;
- compiled-output neighbors;
- declared relation doors;
- rendering alternatives as explicit previews.

The traversal trail stays visible while you wander.

Rendering alternatives do not silently mutate the compiled Atlas. To inhabit a different rendering, compile a preference profile. This keeps:

```text
preview != accepted compilation
choice != hidden mutation
```

## One file, layered receipts

The Atlas carries:

- the compiled linguistic projection receipt;
- a curiosity-room receipt for every emitted token;
- one Atlas receipt binding the chosen compilation and those room receipts.

The HTML is a deterministic presentation of that received Atlas data.

The Atlas receipt describes the underlying Atlas projection, not the browser's transient click history.

## Safe embedding

Witnesses and annotations can contain arbitrary text.

Revival therefore JSON-encodes embedded Atlas data and escapes characters that could terminate the inert `application/json` script element.

The browser code renders source and annotation material with `textContent`, not `innerHTML`.

That is part of the boundary: source material is data, not executable page authority.

## Presentation law

```text
HTML != witness
browser state != receipt
click trail != historical occurrence
preview != accepted profile
walkability != authority
```

The Atlas may make the Bible more explorable. It may not silently strengthen the epistemic status of anything it displays.

## Why this matters

Before Revival 005, the curiosity world was executable through JSON and CLI calls.

Now the same contracts produce something a person can actually wander:

```text
compiled Bible floor
       ↓ click
source-backed word room
       ↓ relation
another room
       ↓ neighbor
another room
       ↓ rendering door
alternate possibility
```

The current world is only Genesis 1:1 and uses demonstration-only linguistic/relation data.

The architectural step is larger than the specimen:

**a source-backed Bible compilation can now become a portable, inspectable, inhabitable artifact.**
