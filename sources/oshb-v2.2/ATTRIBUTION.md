# Open Scriptures Hebrew Bible attribution

Revival's `Gen.1.1.xml`, `Gen.1.2.xml`, and `Gen.1.3.xml` fixtures contain small excerpts adapted from the **Open Scriptures Hebrew Bible (OSHB) v2.2**, pinned to upstream commit:

`6a5db284c715c18b239422e57bb89684e6a19f00`

Upstream repository: https://github.com/openscriptures/morphhb  
Upstream file: `wlc/Gen.xml`  
Upstream Git blob: `dcc8be362134981d3054e9b64d3a465d08492a33`

The underlying **Westminster Leningrad Codex text is Public Domain**.

OSHB lemma and morphology data are licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

Required attribution from the upstream license:

> Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb

Each Revival fixture adds a standalone XML verse wrapper around pinned word and segment elements from Genesis 1:1-3 so the adapter and cross-passage corpus can be tested without vendoring an entire biblical book.

Revival does not claim that OSHB is canonical, text-critically final, or linguistically infallible. It is an attributable external source layer.
