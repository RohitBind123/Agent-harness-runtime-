# ADR-0009 — No graph database

**Status:** ACCEPTED, with a measured trigger
**Date / context:** 2026-09-02 (Memory ADR 13) and 2026-09-05 (the Brain architecture).

## Context

Organizational knowledge is full of relationships, and multi-hop questions
("why does QIC approval behave differently for carrier X") are exactly the kind
the Brain is supposed to be good at. A graph database is the obvious fit and
the legible choice.

## Decision

**No graph database, in any planned phase, without a measured traversal need.**
A relationship is a claim whose subject and object are both entities. Multi-hop
is a recursive CTE over the relational store. If traversal need is demonstrated,
build the relationship table with CTEs **first**; consider an engine only if
CTEs measurably lose at the observed scale.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| A graph store for relationships and multi-hop | See below — the objection is transactional, not performance. |
| A graph store as the primary claim store | Inherits the same transaction problem and adds a second consistency story for the primary data. |

## Evidence and reasoning

**[DESIGN DECISION]** **The decisive objection is not performance. It is that
it is a SECOND STORE.**

A claim, its version, its evidence, and its outbox event must **commit
together.** Split across engines, that becomes a distributed transaction — and
the one property the whole design rests on (a claim can never exist without its
evidence) becomes best-effort.

Secondary: every additional store is a ninth thing to enumerate for a tenant
deletion route, and a store that cannot be enumerated cannot ship
([ADR-0017](ADR-0017-deletion-route-before-retirement.md)).

**[INFERENCE]** The Brain review predicts a graph database is one of the two
things most likely to be built early despite this argument, because *"we have a
knowledge graph" is a sentence that sounds like progress and can be
demonstrated without the Brain being good at anything.* If it is built anyway,
the mitigation is to make it a strict projection with no logic of its own, so
it can be deleted without losing anything.

## Consequences

- Multi-hop questions are unanswered in Phase 1, and that is stated rather than
  hidden.
- Relationship traversal, when it arrives, is SQL — reviewable, transactional,
  and in the same commit as everything else.
- Hop depth must actually be **measured**, which means the measurement is work
  that has to happen before the trigger can fire.

## What would cause us to reconsider — the measured trigger

A meaningful share of real questions requiring **three or more hops**, or
traversal latency dominating retrieval. **Measure it with CTEs first.** A graph
engine only if CTEs demonstrably lose at the observed scale.

## Source

`learning-notes/Memory Management Architecture.docx` §16.5, §37.3 (ADR 13);
`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0005](ADR-0005-the-world-model-is-a-projection-not-a-store.md),
[ADR-0008](ADR-0008-no-embeddings-in-phase-1.md),
[ADR-0017](ADR-0017-deletion-route-before-retirement.md)
