# ADR-0024 — No autonomous knowledge curation

**Status:** ACCEPTED
**Date / context:** The knowledge system architecture; Memory ADR 19 and §29, 2026-09-02.

## Context

A store that accumulates claims will eventually hold redundant, near-duplicate,
and obsolete ones. The appealing fix is a loop that decides which claims to
keep, merge, summarise, or delete.

## Decision

**No autonomous curation, consolidation, or summarisation layer.** Decay,
retirement, and probe-based verification are **deterministic and sufficient.**

If curation is ever automated, **the protected property must be measurable
first.**

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| A model that merges near-duplicate claims | It is a loop editing its own memory with **no evaluation gate**, optimising a store against a signal that cannot see what it is destroying. |
| A summarisation layer to fit context budgets | **A summary is not evidence for what it summarises.** A claim whose only support is a summary has an evidence chain that does not terminate in an observation, and it should not cross the load floor. |
| Model-generated retention policy | Same argument, one level up. |
| A model that rewrites claims for clarity | Breaks the rebuild invariant: the store would then hold text that was never observed. |

## Evidence and reasoning

**[DESIGN DECISION]** If the context budget binds, the answer is **better
ranking and tighter claims, not a model rewriting the store.**

The general posture: *a constraint that binds is working, and relaxing it
because it binds is the failure mode.*

Deterministic alternatives that are sufficient and already designed: decay from
`last_confirmed` with a per-predicate profile; retirement below a floor;
supersession from the predicate's `single_valued` property; scope-overlap
invalidation from the effect stream; and probe-based verification for
probe-verifiable predicates.

## Consequences

- The store grows, and the curation sweep that bounds it is a deterministic job
  with an advisory lock — not a judgement.
- Near-duplicate claims that never corroborate are a **visible symptom of an
  entity-resolution or vocabulary problem**, and fixing the symptom with a merge
  would hide the cause.
- Human correction routes through `propose_claim` with
  `source_class=human_authored` so it enters the same pipeline, rather than
  becoming a second write path.

## What would cause us to reconsider

**Nothing, in any planned phase.** If it is ever revisited, the precondition is
a **measurable protected property** — something that can be shown to be
preserved or destroyed by a curation pass — plus an evaluation gate with a
measured noise floor.

## Source

`../../architecture/organizational-brain-architecture.md`;
`learning-notes/Memory Management Architecture.docx` §21, §29, §37.4 (ADR 19).

## Related

[ADR-0011](ADR-0011-standing-is-earned-by-independent-corroboration.md),
[ADR-0006](ADR-0006-authority-is-authored-configuration-never-inferred.md),
[ADR-0004](ADR-0004-observation-log-is-the-system-of-record.md)
