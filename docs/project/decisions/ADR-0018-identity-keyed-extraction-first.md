# ADR-0018 — Identity-keyed extraction, and build it first

**Status:** ACCEPTED
**Date / context:** Runtime specification **I9**; the Brain architecture, which
nominates it as "the one to adopt first"; Memory §15.3.

## Context

Observations arrive more than once. Slack webhooks, Jira polls, and backfills
all deliver the same thing repeatedly, and every one of them will. Extraction
is a model call: it costs money and it is non-deterministic.

## Decision

**Every extraction attempt has a deterministic id derived from
`(observation_id, extractor_version)`. That id is a UNIQUE key, and the row is
claimed BEFORE the model call, not after.**

Build it first, before the rest of the pipeline.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Deduplicate observations only | An observation can be identical while the extractor version differs, and a re-extraction under a *new* version is wanted. Keying on the observation alone conflates the two. |
| Claim the row after the model call | The window between call and write is exactly where a redelivery lands. |
| Deduplicate extracted claims afterwards | **This is the trap.** The two claims have *different content*, because the model is non-deterministic — so the duplicate is not even recognisable as one afterwards. |

## Evidence and reasoning

**[CONFIRMED]** *"Retry is not replay."* A redelivered observation whose
extraction runs again costs a second model call **and produces a different
claim.** The store then knows two things weakly instead of one thing strongly —
and neither crosses the corroboration floor.

**[CONFIRMED]** The specification nominates I9 as one of two invariants that
cannot be retrofitted: *"Every other invariant can be added later at a cost
proportional to the work already done. This one cannot. Without it, every
stored result is of unknown reusability, and the migration is a rewrite rather
than a change. It is roughly thirty lines. Write it first."*

## Consequences

- Roughly twenty to thirty lines, and the cheapest correctness win available.
- Changing the extractor version deliberately re-extracts history — which is
  the mechanism [ADR-0004](ADR-0004-observation-log-is-the-system-of-record.md)'s reprocessing relies on.
- A detector falls out for free: claims whose evidence cites the same
  observation twice indicate the key is not being honoured.
- A `NON_IDEMPOTENT` result is never replayed automatically, which is the same
  rule applied to effects rather than extractions.

## What would cause us to reconsider

Nothing. This is the single most-repeated build-order recommendation across
three independent documents here.

## Source

`docs/architecture/universal-runtime-v1.0-architecture-specification.md` §10.2
(I9), §10.7; `../../architecture/organizational-brain-architecture.md`; `learning-notes/Memory Management Architecture.docx` §15.3, §38.1.

## Related

[ADR-0010](ADR-0010-the-model-proposes-and-never-writes.md),
[ADR-0004](ADR-0004-observation-log-is-the-system-of-record.md)
