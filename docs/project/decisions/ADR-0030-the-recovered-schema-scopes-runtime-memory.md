# ADR-0030 — The recovered schema scopes runtime memory, not the organizational store

**Status:** ACCEPTED
**Date / context:** 2026-09-14, from reading the Memory Management Architecture's
migration directly for
`18-brain-mechanism-and-execution-trace.md`.

## Context

`01-architecture-map.md` §4.1 records Q7 as a contradiction between two Phase 1
schemas, and offers a possible reconciliation:

> **A plausible reconciliation** — that the Memory architecture scopes a
> *runtime memory subsystem* over curated, already-identified entities, while
> the knowledge system scopes an *organizational* store over messy multi-source
> input where identity must be established — **is an inference, not a decision.**
> Nobody has written it down.

Two things have changed since that was written.

**First**, one of the two documents is **not in this repository**
([ADR-0029](ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md)), so
the reconciliation cannot be performed as a comparison.

**Second**, the other one is **readable**, and had never been read.
`learning-notes/Memory Management Architecture.docx` contains a complete
PostgreSQL migration — five enums, six tables, eight indexes — that no
`docs/project/` file has ever quoted at column level.

So Hypothesis A can now be argued **from the readable document's own text**,
rather than inferred from the absent one's silence. That is a materially
different kind of argument, and it is worth writing down.

## Decision

**The Memory Management Architecture's schema scopes a runtime memory subsystem.
It is not a candidate organizational claim store, and the organizational claim
store remains unspecified.**

Consequently:

- Its DDL may be **quoted, traced against and learned from** — it is this
  project's own prior design work, recovered.
- It may **not** be adopted as the organizational claim store, and the gaps in
  §Evidence are not defects in it. **They are evidence of what it is for.**
- **This decides nothing about Q7's remaining question** — what the
  organizational claim store's schema should be. That question now has *no*
  readable advocate on either side.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Adopt it as the Phase 1 claim store** | It cannot express `kind` (ADR-0003) or `source_class` (ADR-0006) — the project's two differentiators. Adopting it would mean adopting a store that cannot answer *"which source lost"* |
| **Declare Q7 resolved in its favour** | Picking the readable side because the other cannot be read is picking one silently, which `09-do-not-assume.md:190` makes a stop. See ADR-0029 |
| **Treat it as a draft of the organizational store, to be extended** | Its own vocabulary says otherwise (below). Extending a runtime subsystem's schema into an organizational one is how the two came to share nouns in the first place — the confusion Q7 exists to record |
| **Leave the scope question open** | The evidence is now positive and textual rather than inferential. Leaving it open would mean ignoring a reading that can be checked |

## Evidence and reasoning

**[FACT — in this repository]** The document scopes itself, in its own
vocabulary, throughout its DDL:

| What the DDL says | What it indicates |
|---|---|
| `CREATE TYPE memory_origin AS ENUM ('run', 'human', 'evolve')` | The provenance categories are **runtime** categories. There is no source class, no adapter, no external system |
| Evidence `kind` is `run\|step\|activity\|document\|probe\|human\|policy` | Four of seven are runtime execution objects |
| `memory_proposals.proposal_id` = `hash(run_id, episode_seq, observation_digest)` | Extraction identity is keyed to **a run and a position within it** — the unit of a runtime subsystem |
| `memory_evidence` columns `run_id`, `step_seq`, `activity_id` | The evidence model is built around run execution |
| **No adapter, no observation table, no mention-to-entity mapping anywhere** | The three things an organizational store exists to do are absent — not deferred, absent |

**[EVIDENCE]** Three independent sources require columns this schema does not
have, which is what a scope boundary looks like from outside:

- `01-architecture-map.md` §2 requires `kind` (ADR-0003) and `source_class`
  (CS5) on every claim. **Neither column exists.**
- `07-brain-observability.md` §1's traceable chain — written independently —
  records *"proposed claim, **kind**, predicate"* at extraction and
  *"claim_id, version, status, **source_class**, confidence, validity"* at
  acceptance. **Both are absent.**
- `01-architecture-map.md` §2.4 puts entity resolution in Phase 1 and calls it
  *"the component most likely to be underestimated."* **There is no entity
  table.**

**[INFERENCE]** A schema that lacks the two columns carrying the organizational
thesis, and the table carrying organizational identity, while carrying five
columns naming runtime execution objects, is a runtime schema. The falsifier
would be finding organizational constructs in it that this reading did not
predict; a full read found none.

**What it does establish positively**, and this is why it is worth reading
rather than dismissing: much of the current design is visibly derived from it.
CS2's identity constraint, ADR-0023's six temporal fields, PS4's version CAS,
ADR-0011's one-run-corroborates-once, Stage 1's trust rule as a CHECK
constraint, and ADR-0017's deletion-route index all appear in it, with
rationale, in comments. **The organizational design inherited its mechanics from
this document and added the thesis.** That is a useful thing to know and it was
not written down anywhere.

## Consequences

- **Q7 loses a candidate and gains clarity.** It was recorded as *"which of two
  schemas"*. It is now *"the organizational claim store is unspecified"*, with
  one candidate reclassified as out of scope and the other unreadable.
- **The gaps in §Evidence become requirements** for whatever the organizational
  store turns out to be: `kind`, `source_class`, an entity table, and a decision
  about the contradiction register. `18-…-execution-trace.md` §5.5 lists them
  with the cost of adding each late.
- **Its mechanics remain usable.** Nothing here forbids reusing the temporal
  fields, the version CAS, the evidence constraint or the index shapes. They are
  this project's own prior work and they satisfy invariants this repository
  accepted independently.
- **An honest cost:** this narrows Q7 by removing a candidate rather than by
  answering it. The organizational claim store now has **no specified design at
  all**, which is a more accurate but less comfortable position than the register
  described.

## What would cause us to reconsider

- **The 2026-09-05 review is produced** and turns out to describe the same schema
  rather than a different one — in which case this ADR is wrong and the two
  documents were one design all along.
- **Organizational constructs are found in the Memory document** that this
  reading did not predict: a source-class ordering, a kind taxonomy, an adapter
  model, or an entity-resolution stage. Any one of them falsifies the scope
  argument.
- **The runtime specification's `knowledge/world/` shape turns out to be the same
  subsystem** seen twice — filenames in one place, DDL in the other. That is
  cheap to test and would narrow `01-architecture-map.md` §4.5's "third shape"
  back into this one.

## Source

`18-brain-mechanism-and-execution-trace.md` §5.1, §5.3 and §5.5. The DDL was
read directly from `learning-notes/Memory Management Architecture.docx` §17.2
and §17.3.

## Related

- [ADR-0029](ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md) — why
  a comparison is unavailable
- [ADR-0003](ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md) and
  [ADR-0006](ADR-0006-authority-is-authored-configuration-never-inferred.md) —
  the two the schema cannot express
- `../10-open-questions.md` Q7 — narrowed, not resolved
- `../01-architecture-map.md` §4.1, §4.5, §4.7
