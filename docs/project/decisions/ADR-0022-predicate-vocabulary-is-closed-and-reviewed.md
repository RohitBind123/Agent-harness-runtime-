# ADR-0022 — The predicate vocabulary is closed, and adding to it is a reviewed migration

**Status:** ACCEPTED
**Date / context:** The Brain architecture ("the hinge"); Memory ADR 7 and §10.2,
2026-09-02.

## Context

Claim identity is `(subject, predicate)` within a scope. Without a controlled
predicate vocabulary, two claims about the same thing phrased differently are
two identities that never collide — and a contradiction that never collides is
invisible.

## Decision

**The predicate vocabulary is CLOSED.** An out-of-vocabulary extraction is
**rejected**, and its **rate is the signal** that the vocabulary needs
extending. Adding a predicate is a **reviewed migration**, not a runtime write.

Each predicate carries:

| Property | What it decides |
|---|---|
| `single_valued` | Whether supersession or coexistence applies. **Cannot be read from two sentences — it is a declared property.** `owns_service` is often multi-valued; `current_owner` is single-valued |
| `object_schema` | Validated at write |
| `decay_profile` | none / slow / standard |
| `verifiable_by` | The probe name, if one exists |
| `kinds_allowed` | Which claim kinds may assert it. **This one column is what enforces [ADR-0003](ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md)** — a decision may assert `intended_behaviour` but not `current_behaviour` |

Start with roughly **twenty** predicates, chosen from real questions people
actually ask — not from a taxonomy.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Open vocabulary, free-text predicates | Nothing ever collides, so nothing ever contradicts. The store knows many things weakly instead of few things strongly. |
| Two hundred predicates up front | Same failure as an open vocabulary, arrived at more slowly. Starting too broad is as bad as starting too narrow. |
| Embedding-based predicate matching | Fuzzy matching produces near-duplicates that never corroborate. A loud rejection is better than a quiet near-match. |
| Let the model propose new predicates at runtime | The vocabulary then drifts with model behaviour, and identity stops being stable across extractor versions. |

## Evidence and reasoning

**[DESIGN DECISION]** The object is deliberately **not** part of claim identity.
Two claims with the same identity and different objects are **one claim
disagreeing with itself** — which makes a contradiction a key collision rather
than an invisible pair of rows that both retrieve.

## Consequences

- **The honest cost: coverage is explicitly bounded and visible.** That is the
  intended trade against coverage that is implicitly unbounded and invisible.
- Vocabulary maintenance is ongoing work with a named owner.
- **This is nominated as one of the three decisions most likely to be wrong.**
  How large the vocabulary grows before maintaining it becomes the bottleneck is
  **genuinely unknown, and no consulted source answers it.**

## What would cause us to reconsider

Vocabulary growth without limit. If maintaining the registry becomes the
bottleneck, the case for embedding-based identity strengthens earlier than
planned and [ADR-0008](ADR-0008-no-embeddings-in-phase-1.md) flips. Recorded as an open question, Q12.

## Source

`../../architecture/organizational-brain-architecture.md`;
`learning-notes/Memory Management Architecture.docx` §10.2, §37.2 (ADR 7).

## Related

[ADR-0003](ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md),
[ADR-0008](ADR-0008-no-embeddings-in-phase-1.md)
