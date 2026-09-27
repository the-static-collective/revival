# Scissors

A frozen kernel is immutable ancestry, not a ban on evolution.

When a kernel contract needs to change, create a descendant contract and record the cut explicitly:

```text
kernel v1
   │
   ├── remains intact
   │
   └── scissors
          ↓
       kernel v2
```

A scissors record names:

- the parent kernel version;
- the child kernel version;
- the exact parent contract hash;
- the rationale for the cut.

The child may disagree with or supersede its parent for future work. It may not rewrite the parent and then claim uninterrupted identity.

This is intentionally analogous to source preservation elsewhere in Revival: **development itself has provenance.**
