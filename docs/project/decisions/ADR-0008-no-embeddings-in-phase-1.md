# ADR-0008 — No embeddings in Phase 1

**Status:** ACCEPTED, with a pre-registered trigger to revisit
**Date / context:** 2026-09-02, Memory Management Architecture ADR 12 and
Finding 4. Independently reached in the Brain architecture

## Context

Most agent-memory designs assume vector search as the primary retrieval path.
This project's retrieval is scope-first and structural instead. That is an
unusual choice and needs to be argued rather than asserted.

## Decision

**Phase 1 ships with no embeddings.** Retrieval is **scope-first**: claims
whose subject IS a resolved entity, within a known scope, filtered by
authorization, validity and standing, ordered deterministically.

Embeddings enter in Phase 2 **as candidate generation only**, behind unchanged
authorization/validity/standing stages — and only when a pre-registered
threshold is crossed.

## Alternatives considered

| Alternative | Why rejected for Phase 1 |
|---|---|
| Embeddings as the primary retrieval path | Structural retrieval is exact, free, and higher precision where it applies. Similarity is the fallback for what structure cannot reach — not the other way round. |
| Hybrid from day one | Adds an index, an embedding model, a dimension/version namespace and a recall question before anything has measured a miss. |

## Evidence and reasoning

Two independent arguments. **The design only needs one of them to hold.**

**[INTERNAL — CONFIRMED]** Scoping does the work retrieval would have done
*"exactly, cheaply, and enumerably — because the scopes are known before the
query, rather than inferred from it."* Embedding the current goal is excluded
from the read path on cost grounds, and the read path runs on every model call.

**[EXTERNAL RESEARCH]** Approximate-nearest-neighbour indexes apply metadata
filters **after** walking the graph; there is no pre-filtering. Under a
high-selectivity filter the candidates returned by the walk can all fail the
filter, and **recall collapses.** The single query shape a tenant-scoped store
*always* has — a highly selective tenant predicate — is the shape approximate
vector search handles worst.

That is a requirements argument, not a fashion one.

## Consequences

- **Stated plainly: Phase 1 cannot find a claim whose wording differs from what
  a run is looking for** — only claims in the run's scope. If a claim's subject
  is phrased differently, it is a separate claim with separate evidence.
- Vocabulary misses are **rejected as unroutable rather than matched fuzzily** —
  a loud failure instead of a store of near-duplicates that never corroborate.
- The instrumentation that would justify embeddings must be built in Phase 1's
  tail: **scope misses and vocabulary misses, counted separately.** They have
  different remedies and conflating them makes the trigger unreadable.

## What would cause us to reconsider — the pre-registered trigger

**Vocabulary misses above a threshold registered in advance, sustained for two
consecutive weeks.**

And the counter-case that must not be mistaken for it: **if scope misses
dominate instead, an index cannot help.** The answer there is curation or a
bigger budget share — an index cannot help you fit more into a fixed budget.

Separately, if the predicate vocabulary turns out to grow without limit
(see [ADR-0022](ADR-0022-predicate-vocabulary-is-closed-and-reviewed.md)), this flips earlier than planned.

## Source

`learning-notes/Memory Management Architecture.docx` §1.1 Finding 4, §16.4,
§18.6, §37.3 (ADR 12), §38.2;
`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0022](ADR-0022-predicate-vocabulary-is-closed-and-reviewed.md),
[ADR-0009](ADR-0009-no-graph-database.md)
