# ADR-0016 — Tenant in the key; a cross-tenant read raises

**Status:** ACCEPTED
**Date / context:** Handbook Ch 37 §5; restated as Memory ADR 14, 2026-09-02.

## Context

A knowledge store holding material from more than one tenant, team, channel or
repository has a leak surface with a property that makes it unusually
dangerous: **the leak produces no error.**

## Decision

**Tenant in the key, enforced at write.** A cross-tenant read **RAISES**.
Row-level security sits underneath as a backstop, not instead. No cross-tenant
aggregation without a contract.

Both enforcement layers are required and they do **different jobs**.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Row-level security alone | RLS **filters**. A filter returns an empty result, which is indistinguishable from having no data and **produces no signal.** A bug that should page someone looks like a quiet afternoon. |
| A filter in the repository layer alone | One forgotten call site is a leak, and there is no backstop. |
| Tenant as a metadata field applied by the caller | The caller is the thing most likely to be wrong. The predicate must live **inside** the store implementation. |

## Evidence and reasoning

**[CONFIRMED]** The two layers do different jobs: the explicit assertion
**raises** and therefore generates a signal; RLS **filters** and therefore
contains the blast radius if the assertion is missing. Neither alone is
sufficient.

Additional constraints that fall out of the same reasoning:

- **Redact at capture.** Cannot be fixed retroactively — git and backups do not
  forget.
- **A cache key that omits the tenant is a leak with no error.** Keys that are
  "tenant-scoped in practice" stop being so the moment a shared dependency, a
  public repository, or a fork produces the same hash across tenants.
- **The ACL predicate must be a PRE-filter**, not a post-filter, for the recall
  reason in [ADR-0008](ADR-0008-no-embeddings-in-phase-1.md).

**Open and unsolved:** organizational permissions are **overlapping, not
partitioned.** A private channel, a restricted repo, an HR document and a
customer contract have different and non-nesting audiences. A single
`account_id` predicate does not transfer. See `docs/project/10-open-questions.md` Q10.

## Consequences

- Two enforcement layers to build and maintain.
- The permission label must be captured **at ingest** and propagated to every
  derived claim — never reconstructed later.
- **Aggregate leakage is an open problem with no general solution.** "Three
  teams are blocked on X" may disclose a private fact. The practical rule — an
  aggregate that cannot be cited should not be produced — is a mitigation, not
  an answer, and it will be too strict in some cases and too loose in others.
- Only a test can detect a permission leak, because nothing else produces a
  signal.

## What would cause us to reconsider

Nothing about the rule. The *shape* of the permission model must change — a
single tenant column does not express overlapping audiences — and that design
work is Q10, not a reconsideration of raise-versus-filter.

## Source

`docs/handbook/chapters/37-tenancy-secrets-and-data-governance.md` §5, §16;
`learning-notes/Memory Management Architecture.docx` §22.3, §31, §37.3 (ADR 14);
`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0017](ADR-0017-deletion-route-before-retirement.md),
[ADR-0008](ADR-0008-no-embeddings-in-phase-1.md)
