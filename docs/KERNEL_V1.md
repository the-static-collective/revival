# Revival kernel v1

Kernel v1 is the smallest shared contract Revival needs in order to transform a held witness without losing the ability to inspect ancestry.

## The six primitives

```text
WITNESS
ANNOTATION
TRANSFORM
PROJECTION
DELTA
RECEIPT
```

### WITNESS

A held source particular with stable identity. Revival hashes the declared witness object. A descendant does not overwrite it.

### ANNOTATION

An attributable statement attached to a witness or descendant. Annotation is not silently promoted into source content.

### TRANSFORM

A named, versioned operation over declared input.

### PROJECTION

A derived representation produced for some use. A projection may be lossy.

### DELTA

An explicit account of what a transform changed, removed, collapsed, or introduced.

### RECEIPT

Deterministic replay evidence connecting one witness, one transform, one projection, and one delta by content hash.

## Non-equivalences

```text
source      != annotation
annotation  != interpretation
projection  != witness

content     != derivation
derivation  != lineage
lineage     != attestation
```

## Authority boundary

Kernel v1 provides identity, derivation, delta, and receipt mechanics. It does not establish textual canon, translation quality, linguistic correctness, historical interpretation, theology, or permission to redistribute a source.

Adapters and domain-specific analysis remain outside the kernel.
