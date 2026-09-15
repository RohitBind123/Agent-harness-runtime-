# ADR-0033 — An extraction attempt's identity is `(observation_id, extractor_version)`

**Status:** ACCEPTED
**Date / context:** 2026-09-15, Architecture Gate 01. **Resolves Q23.**

## Context

Two specifications for an extraction attempt's deterministic identity exist in
this repository, they key different things, and **no document acknowledged the
conflict** until `10-open-questions.md` Q23 recorded it on 2026-09-14.

| | Form | Consequence |
|---|---|---|
| **A** | `(observation_id, extractor_version)` | An extractor upgrade deliberately re-extracts history. The same observation arriving in two runs is **one** attempt |
| **B** | `hash(run_id, episode_seq, observation_digest)` | An extractor upgrade is **invisible**. The same observation in two runs is **two** attempts |

This blocks the smallest item on the board. `14-outside-in-review-2026-09-14.md:380-385`
proposes as this project's first code *a test that a redelivered observation does
not produce a second claim* — and **that test cannot be written until this is
chosen**, because A and B give different correct answers to it.

**X1 is one of the eight irreversible properties** (`16-high-level-implementation-architecture.md`
§8.2). Extraction identity does not retrofit: claims extracted under one key
cannot be re-keyed afterwards, because the duplicates they produced are no longer
recognisable as duplicates.

## Decision

**The organizational claim store's extraction identity is
`(observation_id, extractor_version)`, made a UNIQUE key, and the proposal row is
claimed BEFORE the model call.**

**Form B is not an error.** It is the correct identity for **runtime memory**,
whose unit of work is a run. This ADR scopes each to its own subsystem, and
amends [ADR-0018](ADR-0018-identity-keyed-extraction-first.md)'s reach: ADR-0018
governs the organizational store, which is what this project is building.

An organizational store's unit is an **observation**, which may arrive through
many runs and must be extracted once. A runtime subsystem's unit is a **run**.
The two keys encode that difference correctly for their own scopes.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| **`hash(run_id, episode_seq, observation_digest)`** for the organizational store | It fails the redelivery test **by design, not by bug**: the same observation seen in two runs produces two attempts. That is right for runtime memory and wrong here |
| **Carry both, at different layers** | Q23 hypothesis (C). Two identity schemes over one pipeline means a redelivery is a duplicate under one and not the other, and reconciling them needs a third mapping. **Identity is the one thing that must be singular** |
| **Defer until the first migration** | Irreversible properties are the ones that cannot be deferred. Deferring costs nothing today and everything after the first thousand claims |
| **`(observation_id)` alone** | Then an improved extractor can never re-extract history, which is exactly what `extractor_version` exists to allow — *"Changing it deliberately re-extracts history"* |
| **Content hash of the observation alone** | Two genuinely distinct observations with identical text collapse into one, and the permission labels that differ between them are silently merged |

## Evidence and reasoning

**[FACT — in this repository]** Four readable sources state form A, and none of
them is illustrative reference code:

1. `docs/architecture/organizational-brain-architecture.md` §7a — *"a
   deterministic id from `(observation_id, extractor_version)`, made a UNIQUE
   key, and claimed **before** the model call rather than after. **Retry is not
   replay.** It is roughly twenty lines, it is the cheapest correctness win
   available, and it is the one primitive that does not retrofit."*
2. `02-domain-model.md` §2.2 — *"`proposal_id` — **Deterministic**, derived from
   `(observation_id, extractor_version)`. UNIQUE"*, with the invariant *"The row
   is claimed **before** the model call, not after."*
3. [ADR-0018](ADR-0018-identity-keyed-extraction-first.md).
4. `07-brain-observability.md` §1 — the extraction stage records *"proposal_id,
   extractor_version"*.

**[FACT — in this repository]** The single source stating form B is
`learning-notes/Memory Management Architecture.docx` §17.2, inside a block its own
author heads `[ILLUSTRATIVE REFERENCE CODE]` — a label that appears seven times
in that document.

**[FACT — in this repository]** That document's §30.1, *"The eight kinds of
remembering, kept apart"*, marked `[CONFIRMED]` by its author, separates run
memory from organizational knowledge as different categories with different
writers and different lifetimes. **The source draws the boundary this ADR relies
on.** See [ADR-0030](ADR-0030-the-recovered-schema-scopes-runtime-memory.md).

**[DESIGN DECISION]** Claiming the row before the model call is what makes a
crash mid-extraction safe. A row claimed after the call means a crash between the
call and the write loses the attempt silently and the redelivery pays for the
model twice — and produces a **differently worded** claim from the same text,
which is the failure that does not look like one.

## Consequences

- **Q23 closes**, and the one-week experiment at
  `14-outside-in-review-2026-09-14.md:380-385` becomes writable. It is this
  project's proposed first code.
- **`extractor_version` is a required field** on the proposal from the first
  migration. It cannot be added later without re-keying every existing row.
- **An extractor upgrade is a deliberate re-extraction**, which is a cost:
  bumping the version re-runs the model over history and must be a reviewed
  action, not a deployment side effect.
- **A redelivered observation collides**, which is the property the test asserts.
- **ADR-0018 is scoped, not changed.** Its Status and Decision are untouched; this
  ADR records that it governs the organizational store and that form B belongs to
  runtime memory. Recorded here rather than by editing ADR-0018.
- **Cost, stated honestly:** this decision rests on four documents that share
  authorship. They are concordant but not fully independent, and `18-…-execution-trace.md`
  §5 shows the recovered schema is where the current design visibly came from.
  The strongest thing that can be said is that the *readable, non-illustrative*
  corpus is unanimous.

## What would cause us to reconsider

- **The redelivery test fails in a way the key causes.** Specifically: if
  `observation_id` turns out not to be stable across adapters — if the same
  underlying event yields two observation ids from Git and from Jira — then the
  key is keying the wrong thing and the content digest belongs in it. **This is
  measurable the first week ingestion runs, and it is the falsifier to watch.**
- **Extraction becomes cheap enough that idempotency stops mattering**, which
  would be a cost argument only and would not restore form B's correctness.
- **The absent 2026-09-05 document surfaces and specifies a third form.**

## Source

`19-recovered-architecture-evidence.md` §5.5. Read directly from
`docs/architecture/organizational-brain-architecture.md` §7a,
`docs/project/02-domain-model.md` §2.2, `docs/project/07-brain-observability.md` §1,
and `learning-notes/Memory Management Architecture.docx` §17.2, §30.1.

## Related

[ADR-0018](ADR-0018-identity-keyed-extraction-first.md) — scoped by this ·
[ADR-0030](ADR-0030-the-recovered-schema-scopes-runtime-memory.md) — the boundary this relies on ·
[ADR-0010](ADR-0010-the-model-proposes-and-never-writes.md) — why a proposal exists at all ·
[ADR-0004](ADR-0004-observation-log-is-the-system-of-record.md) — what an `observation_id` identifies
