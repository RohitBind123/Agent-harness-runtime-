# ADR-0029 — The 2026-09-05 knowledge system review is not in this repository

**Status:** **SUPERSEDED** by [ADR-0032](ADR-0032-provenance-of-the-2026-09-05-citations.md), 2026-09-15.
The finding of fact below stands — the document is absent. What is superseded is its
**scope**: it reads the `Date / context` field as though it were the evidentiary basis,
and all ten ADRs name readable artifacts in `## Source`. **The text below is preserved
unchanged.**
**Date / context:** 2026-09-14, while tracing the knowledge pipeline against a
concrete event for `18-brain-mechanism-and-execution-trace.md`.

## Context

`docs/project/README.md:3` states this repository's first rule:

> The repository is the source of truth; chat history is not.

**Ten of the twenty-eight ADRs cite, as their basis, a "knowledge system
architecture review" dated 2026-09-05 — most at section-level precision.** That
document is not in this repository, and nobody had noticed.

| ADR | Cited as |
|---|---|
| ADR-0001 | Finding 0 |
| ADR-0002 | 2026-09-05 (knowledge system review) |
| **ADR-0003** — the core object is a kind-typed claim | §6.1 |
| **ADR-0004** — the observation log is the system of record | §5.3-5.4 |
| ADR-0005 — the world model is a projection | §5.2 |
| **ADR-0006** — authority is authored configuration | *"the hardest and the blocking"* |
| ADR-0009 — no graph database | 2026-09-05 |
| ADR-0012 — the agent reaches the knowledge system only through tools | §13.1 |
| ADR-0013 — MCP is a projection | §14 |
| ADR-0019 — one source end to end | §17, §20.2 |

The three in bold define the core object, the system of record and the authority
model — the positions the rest of the design is built on.

## Decision

**Record, as a finding of fact, that the cited document is not in this
repository, and that every claim resting solely on it is unverifiable here.**

This ADR **selects no schema, reverses no decision, and downgrades no ADR's
status.** It records what can and cannot be pointed at.

Three consequences follow immediately:

1. **Q7's stated method is not executable.** `10-open-questions.md:120` instructs
   a future session to *"read both §37 (Memory ADRs) and §17.3 (knowledge system
   build list) together and write one page reconciling them."* Half that input
   does not exist. **Q7 must be restated before it can be worked.**
2. **`PRD.md:822` carries a mislabelled FACT** — *"two documents **in this
   repository** specify incompatible Phase 1 schemas"* — and
   `01-architecture-map.md:593` asserts the same. One of the two cannot be
   pointed at. Both are corrected to say what is verifiable.
3. **The entities / relations / contradiction-register question is reopened with
   no prior**, because its only recorded advocate is unreadable.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Treat the absence as a citation defect and fix the references** | It is not a formatting problem. The *content* those ten ADRs rely on is unavailable for inspection, which is a different and larger fact |
| **Reconcile Q7 onto the readable document** | `09-do-not-assume.md:190` makes *"resolve a contradiction between documents by picking one silently"* a stop. **Picking the readable one because the other cannot be read is picking one.** Silence is not evidence |
| **Downgrade the ten ADRs' status** | Their reasoning is written out in each ADR and stands on its own; several are independently corroborated elsewhere. Downgrading ten accepted decisions on a provenance finding would be a larger change than the evidence supports, and it is the owner's call, not this ADR's |
| **Reconstruct the document from the ten citations** | It would produce a plausible document nobody wrote, cited as though it were a source. That is the exact failure ADR-0025 exists to prevent |

## Evidence and reasoning

**[FACT — verifiable in this repository]** The document is absent, verified four
ways:

1. The string *"Knowledge System Architecture"* appears **exactly once** in the
   entire Markdown corpus — at `01-architecture-map.md:596`, inside the table
   that cites it. The citation is self-referential.
2. **No `.docx` is it.** None of the nine carries a 2026-09-05 creation date in
   `docProps/core.xml`; the nearest are 2026-08-30 and 2026-09-07. The Memory
   Management Architecture's date is `2026-09-02`, which matches the *other*
   column of the same table exactly — so the date convention in that table is
   file-metadata-derived, and the missing 2026-09-05 is a real absence rather
   than a naming quirk.
3. **The file bearing that title is not it.**
   `../../architecture/organizational-brain-architecture.md` is 272 lines with
   sections 0-10; the citations are to §5.2, §5.3, §6.1, §13.1, §14, §17, §17.3
   and §20.2 — outside its range. It disclaims the role at :14 — *"This document
   states why; those state what"* — and its own §0 Sources table does not list
   such a document.
4. **Nothing was deleted.** `git log --all --diff-filter=D` finds no matching
   file in any commit on any branch.

**[INFERENCE]** The section numbers are internally consistent across ten
independently written ADRs. That is not the signature of fabrication; it is the
signature of a real document that existed in a working session and was never
committed. No falsifier is stated, so this is inference rather than hypothesis.

**[FACT]** One citation actively misleads. `01-architecture-map.md` §4.1
attributes *"§17.3 build list"* to the absent document, as the authority for an
entities table and a contradiction register. **§17.3 of the readable document is
titled "Per-table specification"** and enumerates `memory_claims`,
`memory_claim_versions`, `memory_evidence` and `memory_proposals` — no entities
table, no contradiction register. This does not prove mis-attribution; the absent
document may have had its own §17.3. It does establish that the one citation
which resolves, resolves to content contradicting the description.

## Consequences

- **Ten accepted ADRs now carry a visible provenance gap.** Their *reasoning*
  remains readable and is unaffected; what is unavailable is the source that
  reasoning was drawn from. A reader who wants to check ADR-0003's §6.1 cannot.
- **Q7 is further from resolution than the register suggested**, not closer. It
  was recorded as a tractable reconciliation with a half-day method. It is not.
- **The repository's own first rule has been broken and is now visible.** That is
  the point of recording it. `05-development-workflow.md`'s sequence did not
  catch this, and no linter can: `check_provenance.py` matches a denylist of
  phrases, not dangling citations.
- **An honest cost:** this ADR makes the project look less settled than it did
  yesterday, and that impression is accurate. Ten decisions that read as
  well-sourced are less well-sourced than they appear.

## What would cause us to reconsider

- **The document is produced.** If the 2026-09-05 review is found and committed,
  this ADR is superseded outright, Q7's method becomes executable again, and the
  entities / contradiction-register question regains its advocate. **This is the
  single most valuable artefact anyone could add to this repository.**
- **The owner recalls its contents well enough to reconstruct it.** In that case
  it must be committed as a **newly written document dated today**, attributed to
  recollection, and never as a recovered 2026-09-05 source.
- **A different source turns out to carry the same material**, in which case the
  ten ADRs are re-cited to it.

## Source

`18-brain-mechanism-and-execution-trace.md` §1. Verified against
`docs/project/decisions/*.md`, the nine `learning-notes/*.docx`,
`../../architecture/organizational-brain-architecture.md`, and
`git log --all --diff-filter=D`.

## Related

- [ADR-0025](ADR-0025-no-external-codebase-is-evidence.md) — the discipline this
  finding applies: an artefact that cannot be read cannot be cited as evidence.
  ADR-0025 addressed *external* artefacts; this is the same failure with an
  *internal* one, which the guard does not cover
- [ADR-0030](ADR-0030-the-recovered-schema-scopes-runtime-memory.md) — what can
  still be argued from the readable document alone
- `../10-open-questions.md` Q7 — reframed, not resolved
- `../01-architecture-map.md` §4.1 — corrected
