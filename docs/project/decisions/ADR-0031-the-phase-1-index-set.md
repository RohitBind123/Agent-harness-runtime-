# ADR-0031 — The Phase 1 index set is recovered, not invented

**Status:** ACCEPTED
**Date / context:** 2026-09-14, from
`18-brain-mechanism-and-execution-trace.md` §7.4.

## Context

`04-implementation-map.md` records that no index inventory exists, and no
`docs/project/` document lists one. Retrieval is specified as *"one SQL
statement"* (doc 16 §7) with no statement of what makes it efficient, and
`01-architecture-map.md` describes the retrieval index only as *"disposable"*
and *"authoritative for nothing"*.

**An annotated index set does exist.** The Memory Management Architecture's
migration carries eight, each with its purpose written as a comment — including
one built specifically to satisfy ADR-0017's deletion route, which was accepted
here without anyone noticing it had already been solved.

This ADR records what was recovered and which parts transfer, because an index
set that nobody has written down is one a first implementation will invent
badly — and two of these are not performance structures at all.

## Decision

**Adopt the recovered index set as the Phase 1 starting point, with two
amendments and one explicit exclusion.**

| Index | Shape | Serves |
|---|---|---|
| **`claims_identity`** (UNIQUE) | `(tenant_id, scope_path, subject, predicate)` | **Contradiction detection.** The mechanism, not an optimisation |
| **`evidence_one_per_run`** (UNIQUE) | `(claim_id, run_id, step_seq)` | **ADR-0011's corroboration count.** An integrity constraint |
| `claims_retrieval` | `(tenant_id, scope_path, recorded_at) WHERE state='active'` | The hot read path. **Partial** |
| `versions_asof` | `(claim_id, recorded_at DESC)` | `as_of` and `history` |
| `evidence_by_run` | `(tenant_id, run_id)` | **ADR-0017's deletion route** |
| `proposals_expiry` | `(lease_until) WHERE state='claimed'` | Crash recovery of in-flight extractions. **Partial** |
| `proposals_signals` | `(tenant_id, created_at, reject_reason)` | X2's vocabulary-miss rate |

**Amendment 1 — the identity index is not final.** Its column list is
`(tenant_id, scope_path, subject, predicate)`. ADR-0028 records `scope` as a
tenant-relative materialised path inside claim identity as a **known domain
leak**, and Q10 records that no complete permission model exists. The *shape* —
a UNIQUE constraint over claim identity, with the object excluded — is what
transfers. **Its exact columns are blocked behind Q10.**

**Amendment 2 — an authority index will be required and cannot be specified
yet.** §11 of the trace resolves conflicts by sorting on source-class
precedence. No `source_class` column exists in the recovered schema
([ADR-0030](ADR-0030-the-recovered-schema-scopes-runtime-memory.md)), so the
index cannot be defined. **When the column is added, the index is not optional:
without it the resolution sort is a scan.**

**Exclusion — `claims_curation` is not adopted.** The recovered set includes
`(last_confirmed) WHERE state IN ('provisional','active')`, serving a decay and
retirement sweep. **No current ADR authorises such a sweep**, and ADR-0024
forbids the adjacent act. Recorded in §Consequences rather than carried forward.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Specify indexes at implementation time** | Two of these are not indexes in the ordinary sense. `claims_identity` is how a contradiction is *detected at all*; `evidence_one_per_run` is how corroboration cannot be gamed. An implementer optimising queries would not invent either, and their absence is silent |
| **Adopt all eight unchanged** | `claims_curation` serves an unauthorised job, and the identity index's columns are blocked behind Q10. Adopting unchanged would import both problems invisibly |
| **Wait for Q7** | The two uniqueness constraints are consequences of CS2 and ADR-0011, which are accepted independently of any schema. They do not depend on Q7 |
| **Design an index set from the query patterns in §7.2** | It would reproduce most of this and miss `evidence_by_run`, whose justification is a deletion route rather than a read |

## Evidence and reasoning

**[FACT — in this repository]** Quoted verbatim from the recovered migration,
with the source's own comments:

```sql
-- R1, the hot-path query. Partial, mirroring Ch 17's partial expiry
-- index: cost scales with ACTIVE claims, not with all claims ever held.
CREATE INDEX memory_claims_retrieval
    ON memory_claims (tenant_id, scope_path, recorded_at)
    WHERE state = 'active';

-- Ch 37 sec 5.4's deletion route. Without this index, deleting a
-- tenant's runs cannot find the claims that cite them, and the store
-- fails the enumeration.
CREATE INDEX memory_evidence_by_run ON memory_evidence (tenant_id, run_id);
```

The source document labels its DDL `[ILLUSTRATIVE REFERENCE CODE]`, seven
times. **It is quoted here as an illustration that was reasoned carefully, not
as a ratified schema.**

**[EVIDENCE]** Three of the eight are required by invariants this repository
accepted separately and without reference to them:

- **EV1** requires evidence be *"a table of references, never an integer
  count"*, and gives three needs that require joining — one of them *"the
  deletion route must find claims citing a departing tenant's runs."*
  `evidence_by_run` is exactly that join, and its comment says so.
- **ADR-0011** requires corroboration to count **DISTINCT runs**.
  `UNIQUE (claim_id, run_id, step_seq)` is how that is enforced rather than
  computed.
- **CS2** requires claim identity to be `(subject, predicate)` in a scope with
  the object excluded, *"so that a contradiction is a key collision"*.
  `claims_identity` is that constraint.

**[INFERENCE]** The partial-index pattern — `WHERE state = 'active'`,
`WHERE state = 'claimed'` — appears three times with the same stated reason:
cost should scale with live rows, not with history. In an append-only store
where retirement is not deletion (CS3), history grows without bound while the
active set does not. **Partial indexes are therefore not a tuning choice here;
they are the structural consequence of CS3.** No falsifier is stated.

## Consequences

- **A first implementation has a starting point** that already satisfies EV1,
  ADR-0011, ADR-0017 and CS2, rather than discovering each as a missing join.
- **`04-implementation-map.md`'s "no index inventory" row was wrong** and is
  corrected. The information was present and unread — a retrieval failure inside
  a repository about retrieval failures, which is worth noticing.
- **Two entries will read as ordinary indexes to anyone skimming**, and deleting
  either changes answers rather than speed. They are marked, and the marking is
  the point.
- **An honest cost:** this adopts the shape of a design whose surrounding schema
  [ADR-0030](ADR-0030-the-recovered-schema-scopes-runtime-memory.md) places out
  of scope. The indexes transfer because they are consequences of invariants
  accepted here, not because the schema does — and a reader could reasonably
  read this ADR as adopting more than it does. It adopts seven index shapes and
  nothing else.
- **The unauthorised sweep is now visible.** `claims_curation` exists in the
  recovered set for a decay job no ADR authorises. Registered as a contradiction
  in `18-…-execution-trace.md` §22.3 rather than quietly dropped.

## What would cause us to reconsider

- **Q10 resolves the permission model**, changing what `scope` is — which changes
  the identity index's columns, and therefore the shape of every read.
- **Measurement contradicts the partial-index assumption**: if the active set
  turns out to be most of the store, partial indexes cost more than they save.
- **`source_class` is added**, at which point the authority index must be
  specified and this ADR extended rather than superseded.
- **A decay sweep is authorised** by a future ADR, at which point
  `claims_curation` is reconsidered on its merits rather than excluded.

## Source

`18-brain-mechanism-and-execution-trace.md` §7.4. DDL read directly from
`learning-notes/Memory Management Architecture.docx` §17.2.

## Related

- [ADR-0030](ADR-0030-the-recovered-schema-scopes-runtime-memory.md) — the scope
  boundary these are recovered from
- [ADR-0017](ADR-0017-deletion-route-before-retirement.md) — `evidence_by_run`
  exists for it
- [ADR-0011](ADR-0011-standing-is-earned-by-independent-corroboration.md) —
  `evidence_one_per_run` enforces it
- [ADR-0028](ADR-0028-the-knowledge-core-is-domain-agnostic.md) — the `scope`
  leak that blocks amendment 1
- `../10-open-questions.md` Q10
