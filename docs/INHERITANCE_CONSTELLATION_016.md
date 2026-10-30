# REVIVAL-016 — THE INHERITANCE CONSTELLATION
## A world worth inheriting, not a world the founder owns

**Status:** source-verified, read-only executable experiment awaiting human review. No merged changes or live deployment. This is a **Revival-owned** descendant stacked on the independently reviewable [Jubilee Scripture Door 015](https://github.com/the-static-collective/revival/pull/15). Upper Room is a named independently governed guest; **we have not written into Upper Room.**

### The central compositional discovery

The October 29 experiments revealed two separate but resonant facts:

1. **Revival's existing proof:** A reader can enter *actual* source-backed Scripture, render it differently, open Hebrew word rooms, inspect independently attributable linguistic layers and walk an addressed Genesis world without hiding what changed. Source witness ≠ interpretation.
2. **The wider Collective's ambition:** An idea or independently verified useful occurrence might open another person's ability to create, refuse, inherit or change a method. Proposal ≠ consent; code receipt ≠ real-world assistance.

These principles are **analogous design values**. They are not evidence that a biblical author predicted or endorsed sixteen modern repositories, nor do external source Readmes become theological annotations. The source-backed Bible **remains the first room**. Its source witnesses are never rewritten or enriched by speculative project claims.

The new standalone curiosity artifact, `inheritance-room.html`, deliberately gives a visitor two visibly separate entrances:

- **SOURCE ROOM:** enter the original, bit-for-bit built Genesis 1:1–3 Scripture world, using original Revival-015 / Revival-011 source evidence and the existing OSHB/MACULA licenses, stable addresses and receipts.
- **POSSIBILITY ROOM:** choose any two *independently owned non-scriptural projects* and one of seven explicitly speculative lenses; generate a fresh **held question**. The room has **no** intake, network fetch, cookie, state persistence, tool executor, financial action, child information, scripture cross-tagging or automatic partner contact.

This is an additive artifact, not a rewrite of Revival's Python kernel or of the Genesis world.

### Sixteen real independently owned inputs

Every source here is a public Git repo at an immutable commit, and its exact `README.md` bytes are checked using Git *from its original checkout* in CI before composing:

| Owner | Role in the editorial possibility room |
|---|---|
| Nourish Kids | A concrete, user-chosen meal need |
| BananaSpork / NanaSpork | Consent-preserving HOLD, separate Campfire authority |
| JAR;VIS | Attention and still-missing human gates |
| planZ | Plan generation, decisions and revisable proposals |
| CANNON | Composable executable capabilities |
| Dogram | Bounded mathematical relations and constraints |
| reLATTE | Independent-owner crossings without imported authority |
| Jubilee Engine VM | Bounded witnessed acts, optional Book of Acts review |
| GrO | Encountered possibility and the right to decline it |
| Static Live | Participation, performance and source-owned artistic outcomes |
| lemonPRESS | Portable stories, books, machine notebooks and artifacts |
| GRAFT | Inspectable speculative branches rather than automatic admission |
| Upper Room | Shared Scripture encounter, branching, freedom to leave |
| BananaGram-Gram-to-Fork | Earlier family/neighbor communication and invitation porch |
| Jubilee Campfire | Gift-based Offer → Join → Remember *hypothesis* |
| webZ | An independently governable First/Second Table idea and source-native proof |

The pin manifest is `sources/inheritance-016/owners.json`. **A pinned public README is evidence of what a project documents, not proof its promises are fulfilled.** Reading it supplies a source/provenance link for a creative idea. It does not supply ecclesial, medical, nutritional, personal, financial, fundraising, source-linguistic, or organizational authority.

### Seven lenses; 840 doors, all held

For each pair of distinct source owners, the deterministic builder creates one question per lens:

| Lens | What it can ask | Authority it does **not** grant |
|---|---|---|
| **NOURISH** | What small real need might be articulated? | Caregiver consent |
| **ATTEND** | What unanswered human question matters? | Reviewer approval |
| **COMPOSE** | What bounded executable experiment could be reproduced? | Source-owner authorization |
| **MAKE** | What joyful voluntary activity could introduce participation? | Automatic participant enrollment |
| **REMEMBER** | What would independently count as a real outcome? | Recipient testimony or fulfillment |
| **INHERIT** | What could independent successors change or refuse? | Founder's retained control |
| **REFUSE** | How can somebody decline without penalty? | Any implication that they participated |

**16 choose 2 × 7 = 840** reproducible questions. These are generated *editorial invitations*, not 840 implemented integrations. A deliberately transparent, deterministic "Surprise me" button can cycle through combinations without tracking anyone. A "Refuse / clear" button clears the current speculative question and creates no record.

The source room and possibility room never write into each other. No automatic mapping from an invented "food" or "festival" theme to Genesis, and no passage becomes a social-service request.

### The executable path

```text
Pinned OSHB + MACULA + Revival source code
      ↓ Revival-015 original build_door (cold reproducible)
Original Genesis source world, license receipts and witnessed place
      ↓ (one separate read-only audience door)
Standalone local Genesis world

16 other original repositories
      ↓ exact Git origin / SHA / clean worktree / README byte proof
16 *editorial-only*, independently owned source pointers
      ↓ deterministic seven-lens x 120-pair composition
840 HOLD questions + source pointers
      ↓ standalone local POSSIBILITY ROOM
Human chooses, contemplates, prints, refuses or leaves
      X no source promotion, no social action, no Scripture claim
```

The compiler binds the new constellation to the existing source-door artifact digest, the exact original README bytes of every owner, the combined receipt, and hashes of the full generated HTML/JSON. A cold verify rebuilds and compares exact output bytes.

### Reproduce

Python 3.11+, Git, read access to public GitHub repositories; nothing is contacted once the checkouts are present.

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
# Create a source directory with each of the 16 Git checkouts
# named as the repository name, checked out detached at the
# exact commit specified in sources/inheritance-016/owners.json.
python -m revival.inheritance_constellation build /tmp/revival-inheritance-016   --sources /path/to/16/pinned/checkouts
python -m revival.inheritance_constellation verify /tmp/revival-inheritance-016   --sources /path/to/16/pinned/checkouts
```

The output includes `inheritance-room.html`, `genesis-world.html`, `constellation.json`, and `manifest.json`. Open the first HTML locally. The dedicated GitHub workflow installs the original Revival compiler, runs the full test suite, clones all sixteen exact upstream owners, verifies exact source SHA/origin/README bytes, generates the original compiled Genesis world and 840 question cards, verifies every byte again, and uploads a portable downloadable bundle.

### Seven explosions, captured without forcing a product merger

**1. Inheritance:** a source-backed thing can create a new independent descendant without erasing ancestry. The new speculative lens remains separate from what the Bible says.

**2. Alternative capacity to speculation:** resource/skill matching can be a proposed question rather than a bet or price. No cryptocurrency, worth scores, deservingness or purchase.

**3. Creative invitation:** music, comics and fictional worlds can welcome participants. A vulnerable family is never turned into entertainment without consent.

**4. Recursive planning:** a first table may prompt questions about independent future tables. More plans do not establish more communities.

**5. Living encyclopedia:** source evidence, experiments, failures and independently receipted real acts could *eventually* create inheritable knowledge. This artifact currently catalogs source proofs and questions only.

**6. One-minute stranger:** no user needs to understand sixteen repositories to pick one question and one source door. Browser room is static, no login, no required faith affiliation or participation.

**7. Fellowship:** the applicant's proposed Second Table experiment, Nourish Kids, Coalition of Care conversations, music and potential festival stations remain human-gated. This artifact implies **no** Coalition endorsement, fellowship award, children fed, funding, customer adoption, venue permission or third-party participation.

### Non-negotiable invariants

```text
SCRIPTURE SOURCE != CREATIVE QUESTION
SOURCE README != SCRIPTURE WITNESS
LEXEME != THEOLOGICAL INTERPRETATION
ATLAS LINK != CONSENT
CREATIVE LENS != VERIFIED INTEGRATION
CODE RECEIPT != REAL FOOD
HUMAN REPORT != RECIPIENT CONFIRMATION
INHERITANCE != OBLIGATION
A FORK DOES NOT INHERIT AUTHORITY
REFUSAL IS A COMPLETE AND RESPECTED OUTCOME
```

### Honest remaining frontiers

No authenticated live cross-repository delivery is created. No runtime actually composes CANNON × planZ × DOGRAM; only independently verified source descriptions become input to *editorial* pairing questions. The visitor cannot send help, invoke an AI, send email, book a venue, submit the Voqal application, enroll a household or claim an independent Second Table has formed.

Later, a source owner could independently approve a specifically bounded candidate, JAR;VIS could review original-source execution receipts, and a real community could separately choose whether to act. **Those are future permission-bearing decisions, not latent capabilities this PR silently activates.**

### Child-first motivation, privacy preserved

The design connects to the founder's stated aspiration to help build a world children can inherit **and enjoy living in**. It does not publish a child's identity, family histories, personal legal matters or any actual household information. This is a first-person motivation expressed as a voluntary experiment, not testimony from or about a child.

**The product thesis:** Preserve the truth of the source. Let curiosity generate possibilities. Leave the future free.
