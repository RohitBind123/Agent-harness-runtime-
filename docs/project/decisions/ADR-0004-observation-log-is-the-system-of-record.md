# ADR-0004 — The observation log is the system of record

**Status:** ACCEPTED
**Date / context:** 2026-09-05, knowledge system architecture review §5.3–5.4.

## Context

A knowledge system that extracts structure from messy input will get the
extraction wrong at first and improve it repeatedly. The question is whether
improving it applies to the future only, or to history as well.

## Decision

**An append-only, uninterpreted observation log is the system of record.**
Every downstream structure — claims, entities, index, world model,
contradiction register — is **derived and therefore disposable.**

The log carries, per observation: raw payload, source, actor, `occurred_at`,
`ingested_at`, content hash, permission label. **Nothing is interpreted here.**

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Extract at ingest and keep only claims | A better extraction prompt then applies only to the future. History is frozen at the quality of the day it was ingested. |
| Keep source systems as the record and re-fetch | Sources mutate, delete, and change API shape. A Slack message edited last week cannot be re-fetched as it was. |
| A log carrying only ingestion time | **Unrecoverable.** A log that records only when it learned something can never recover when the thing was true. |

## Evidence and reasoning

**[DESIGN DECISION]** The resulting invariant is checkable: *drop the claim
store, the index, the world model and the contradiction register, replay the
observation log, and you arrive at the same state.* If you cannot, something
downstream holds information that was never observed — which is either a bug or
a place a human edited the knowledge system directly, and both need to be visible.
This is the same check the handbook calls the **Replay test** (Ch9: "delete
every read model/progress/cached context; if state can't be rebuilt, an axis
leaked"), applied here to the whole derived layer rather than to one store.

Reprocessing is therefore **not a disaster-recovery story. It is the normal way
the knowledge system improves** — better extraction, a new predicate, a corrected
authority ordering, all applied to history rather than only to the future.

## Consequences

- Storage grows with raw payloads. The retention split applies: structural
  signal is small and keepable for years; verbatim content is large and
  expensive, and is retained longer than the claims derived from it but not
  forever.
- **Four properties must be decided on day one and cannot be retrofitted:**
  `occurred_at` separate from `ingested_at`; the permission label captured at
  ingest (a message's audience is knowable at ingest and unknowable later);
  content hashing (re-delivery is a no-op); raw payload retention.
- A knowledge-authoring UI becomes a problem, because it creates claims with no
  observation behind them and breaks the rebuild invariant. If humans must
  author directly, it routes through `propose_claim` with
  `source_class=human_authored` so it enters the same pipeline.
- The rebuild invariant should be a CI test on a seeded log, not an aspiration.

## What would cause us to reconsider

Nothing identified. Raw-payload retention cost at a scale that makes it
infeasible would change the *retention window*, not the decision — the log
stays the record; older verbatim content ages out while structural signal
remains.

## Source

`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0005](ADR-0005-the-world-model-is-a-projection-not-a-store.md),
[ADR-0018](ADR-0018-identity-keyed-extraction-first.md)
