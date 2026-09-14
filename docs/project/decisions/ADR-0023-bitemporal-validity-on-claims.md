# ADR-0023 — Bitemporal validity on claims

**Status:** ACCEPTED
**Date / context:** Memory ADR 9 and §12, 2026-09-02. Independently required by
the Brain architecture

## Context

The handbook's memory design carries `last_confirmed`; the world model carries
an event-log position. **Neither separates when a fact was true from when we
recorded it.** A store with one timestamp cannot answer "what did we believe in
June" and — worse — it misclassifies a late-learned old fact.

## Decision

**Valid time and transaction time are separated on every claim.**

| Field | What it is |
|---|---|
| `observed_at` | When the fact was true, **with a confidence TIER** (attested vs inferred) |
| `recorded_at` | When we learned it — from the **database** clock, not the model |
| `observed_at_seq` | Position in the durable ordered effect stream, for scope-overlap invalidation |
| `last_confirmed` | The decay origin |
| `superseded_at` | Closes the validity interval |

`effective_from` / `effective_until` are **DEFERRED**.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| A single timestamp | Cannot answer "what did we believe in June", and **misclassifies a late-learned old fact's corroboration as a contradiction** — which is the failure that matters, because it silently degrades claims that are actually in agreement. |
| Full bitemporality with explicit intervals from the start | Makes every read a two-dimensional range query, for claims that mostly have no known end date. |
| `effective_from`/`until` in Phase 1 | The columns would be null on every row, and **a null interval column invites a query that silently drops rows.** |

## Evidence and reasoning

**[DESIGN DECISION + EXTERNAL RESEARCH]** The separation of valid time from
transaction time is long-established relational theory, imported rather than
invented.

**A guard is required and it is not optional:** an **inferred** valid time may
not supersede an **attested** one. That rule needs the tier column to exist,
which is why the tier is not a nice-to-have.

## Consequences

- Six timestamp fields, not one and not eight.
- `as_of` queries become possible: "what did we believe in June" is answerable,
  and that is the cheapest high-value evaluation set available — built once from
  real history.
- A run sees a **stable** world via a per-run `as_of` anchor, while the Brain's
  `now` moves. A global frozen clock does not transfer to a continuously
  ingesting system.
- **Nominated as one of the three decisions most likely to be wrong.** A model
  reading a date out of prose is the weakest joint in the temporal design. A
  *systematically* wrong inferred date produces systematically wrong
  supersession ordering, and **the tier guard would not catch it.**

## What would cause us to reconsider

A measured share of claims carrying a **known end date at write time** would
trigger `effective_from`/`effective_until`. Evidence that inferred valid time is
systematically wrong would mean restricting `observed_at` to attested sources
only — narrowing the field's source, not removing the axis.

## Source

`learning-notes/Memory Management Architecture.docx` §12.3, §12.4, §37.2 (ADR 9),
§38.2; `../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0003](ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md),
[ADR-0022](ADR-0022-predicate-vocabulary-is-closed-and-reviewed.md)
