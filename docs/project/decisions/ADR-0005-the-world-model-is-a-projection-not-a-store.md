# ADR-0005 — The world model is a projection, not a store

**Status:** ACCEPTED
**Date / context:** 2026-09-05, knowledge system architecture review §5.2. Described there
as "the correction that saves the most work."

## Context

The instinct when building organizational knowledge is to build an
entity-relationship store — organization, people, teams, projects, systems,
decisions — and treat it as the core. The proposed knowledge system layer stack listed
"world model" as a layer alongside claims.

## Decision

**The world model is a materialised view over the claim store.** It owns
nothing. Entities and relationships get an **identity** table — stable ids,
types, aliases, source ids, which genuinely is schema — and **everything
asserted about them stays a claim.**

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| An authored entity-state store alongside claims | "Team X owns Service Y" in an entity column has no source, no validity interval, no confidence and no authority — so the first time two sources disagree about ownership, there is nowhere to put the disagreement. |
| World model as the primary store, claims as an audit trail | Inverts which one is authoritative and reintroduces the dual-write problem. |

## Evidence and reasoning

**[DESIGN DECISION]** The test, applicable to any structure you are tempted to
add: **delete it.** If deleting it loses information, it was not a projection
and you now have two sources of truth. If deleting it costs only the time to
rebuild, it is a cache and can be rebuilt whenever the claims change. This is
the handbook's **Replay test** (Ch9), applied to one structure at a time
rather than to the whole derived layer at once — see
[ADR-0004](ADR-0004-observation-log-is-the-system-of-record.md).

## Consequences

- No entity-state synchronisation, no dual-write, no question of which one is
  right.
- The world model can be dropped and rebuilt at any time — which is also what
  makes [ADR-0004](ADR-0004-observation-log-is-the-system-of-record.md)'s rebuild invariant testable.
- Reads that would have been a single column become a claim lookup with
  validity and authority resolution. That is more work per read, and it is the
  work that produces a correct answer when sources disagree.

## What would cause us to reconsider

A measured read-latency problem that materialisation cannot solve. Note this
would change *how the projection is maintained*, not whether it is a
projection.

## Source

`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0004](ADR-0004-observation-log-is-the-system-of-record.md),
[ADR-0009](ADR-0009-no-graph-database.md)
