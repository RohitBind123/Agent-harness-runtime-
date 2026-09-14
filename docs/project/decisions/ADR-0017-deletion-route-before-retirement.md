# ADR-0017 — A store ships with a tested deletion route before it ships retirement

**Status:** ACCEPTED
**Date / context:** Handbook Ch 37 §5.4; Memory ADR 18 and §38, 2026-09-02.

## Context

Two operations look similar and are not: **retirement** (a claim stops
influencing runs, and stays in history) and **deletion** (the data is gone,
because a tenant left or a subject exercised a right). The handbook's memory
design says memory "never deletes." The governance chapter says every store
must declare a deletion route. That is a genuine tension.

## Decision

**Retirement and deletion are two different operations and both must exist.**
The deletion route is built and **tested first**, before retirement, before
retrieval quality, and before anything that makes the store good.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Never delete; retire only | Fails the tenant-deletion enumeration. In a multi-tenant system that is an unshippable state, not a quality gap. |
| Delete instead of retire | Loses the history five separate needs depend on, including the ability to answer "what did we believe in June." |
| Add deletion later | The enumeration is done across *every* store. A store added without a route fails it loudly — which is the good case; the bad case is that it is added and quietly skipped. |

## Evidence and reasoning

**[FACT]** A store with no declared deletion route *"fails the enumeration
LOUDLY rather than being skipped silently."* That makes the ordering
non-negotiable: **retrieval quality is an optimisation over a store that must
first be allowed to exist.**

The general ordering principle this instantiates: **build the things that make
the store LEGAL and MEASURABLE before the things that make it GOOD.** Deletion
before retirement. Tenant isolation before retrieval quality. Signals before
tuning. Nothing that depends on a threshold nobody has measured.

## Consequences

- Phase 1 spends effort on a capability no user asks for, before capabilities
  users do ask for. That is the intended trade.
- The deletion route must **find claims citing a departing tenant's runs**,
  which requires evidence to be a joinable table rather than a count.
- Every new store — an index, a cache, a projection — adds an entry to the
  enumeration. That is a real argument against adding stores
  ([ADR-0009](ADR-0009-no-graph-database.md)).
- Retirement is not deletion and must not be implemented as one. Retirement
  does not undo effects a claim already had.

## What would cause us to reconsider

A single-tenant deployment holding no personal data. That changes the *urgency*,
not the design — and the moment a second tenant exists, the route is needed and
retrofitting it is harder.

## Source

`docs/handbook/chapters/37-tenancy-secrets-and-data-governance.md` §5.4;
`learning-notes/Memory Management Architecture.docx` §13.4, §35.4, §37.4 (ADR 18), §38.

## Related

[ADR-0016](ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md),
[ADR-0009](ADR-0009-no-graph-database.md)
