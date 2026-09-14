# ADR-0010 — The model proposes and never writes

**Status:** ACCEPTED
**Date / context:** Handbook Ch 12 §5.1; restated as Memory ADR 4, 2026-09-02.

## Context

The obvious way to give an agent memory is a `remember(text)` tool it calls
whenever it feels it has learned something. Many agent frameworks do exactly
this.

## Decision

**A model proposes candidate claims. It never writes one.** Extraction runs at
run end, **off the critical path**, as one call per run. `MemoryPort` has **no
write method** — the absence is enforced by the type, not by a convention.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| A `remember(text)` tool | It *"puts an unreviewed, unabstracted, unclassified claim into a file that will be read on every future call, at the moment of least reflection, from inside the run that produced it."* |
| Write on the critical path with synchronous validation | Makes memory failure a run failure, and puts a model call in the latency budget of every run. |
| A human approves every write | A human bottleneck per run. See [ADR-0011](ADR-0011-standing-is-earned-by-independent-corroboration.md). |

## Evidence and reasoning

**[CONFIRMED]** Each of the four words in "unreviewed, unabstracted,
unclassified, from inside the run" names a distinct failure. *From inside the
run* is the subtlest: the model is least able to judge what generalises at
exactly the moment it is most convinced it has learned something.

Enforcing the absence **in the type** rather than in review is the difference
between a structural and a conventional guarantee.

## Consequences

- Memory arrives asynchronously. A claim learned in run N is available from run
  N+1 at the earliest, and only after corroboration in practice.
- The write path never fails a run; the read path never fails a step.
- An **imperative** ("always do X", "never use Y") is rejected at the write
  path — one regular expression, and the single highest-value line in the write
  path. An imperative is a harness change and must go through the evaluation
  gate ([ADR-0015](ADR-0015-verification-before-knowledge.md) and the evolution-loop gates), not through memory.

## What would cause us to reconsider

Nothing identified. A measured need for within-run memory would be served by
run state, which already exists, rather than by making the model a writer.

## Source

`learning-notes/Memory Management Architecture.docx` §9.5, §15, §37.1 (ADR 4);
`docs/handbook/chapters/12-the-memory-system.md` §5.1.

## Related

[ADR-0011](ADR-0011-standing-is-earned-by-independent-corroboration.md),
[ADR-0018](ADR-0018-identity-keyed-extraction-first.md)
