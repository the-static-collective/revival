# Jubilee Scripture Door — Revival-owned read-only export

Implements the bounded source lookup requested in [Revival #14](https://github.com/the-static-collective/revival/issues/14). The frozen kernel, source fixtures, compiler, world-place builder and Upper Room receiver are unchanged.

The exporter checks every selected compiler/source file byte-for-byte against immutable Revival 012 source commit `af1e00c24e3d7c6eb6b1ac39ef59bf894e2385fd`, then uses the existing OSHB/MACULA adapters and Revival 011 world builder. It selects the address from an actual built passage place; it never synthesizes an address from a festival theme.

```sh
PYTHONPATH=src python -m revival.jubilee_door build /tmp/jubilee-scripture-door
PYTHONPATH=src python -m revival.jubilee_door verify /tmp/jubilee-scripture-door
PYTHONPATH=src python -m unittest discover -s tests -p 'test_jubilee_door.py' -v
```

The output directory must not exist for `build`. `verify` performs a full cold rebuild and compares the manifest, world JSON and HTML. Keep Git history available; CI checkout must use `fetch-depth: 0` so the pinned source commit exists.

The three output files are a manifest, `world.json`, and `genesis-world.html`. Open the HTML with the manifest's exact encoded address fragment to inspect Genesis 1:1. The manifest preserves world/witness receipts, input digests, the exporter code digest, OSHB public-domain text / CC BY 4.0 annotation attribution, and MACULA CC BY 4.0 attribution.

`resolve_candidate` accepts only a tag ID, exact reference, public flag and withdrawal flag. Supported public Genesis resolves to `RESOLVE_CANDIDATE`; Luke/Isaiah/etc. remains `HOLD_UNRESOLVED`; private/withdrawn tags are `REFUSED`. All results retain effect/authority `NONE`. Integrity checks and a pinned owner rebuild precede resolution, so rehashing changed metadata cannot impersonate the owner output.

Byte/source binding is not a signature, theological verdict, source admission, host agreement or participant consent. Upstream repository/blob pins are retained from the existing licensed source manifests; this export does not independently retrieve the upstream corpus. The destination may inspect the artifact but cannot promote it into execution, canon or a physical-event witness.

The consumer must pin the artifact digest, verify the received bytes, retain attribution, require explicit user navigation and block fresh navigation after withdrawal. This format is owner-local; it is not the Upper Room Door Packet or a universal physical-festival adapter.
