# ADR-0019 — One source end to end, before breadth

**Status:** ACCEPTED
**Date / context:** 2026-09-05, knowledge system architecture review §17, §20.2.

## Context

The obvious first move is to connect every source — Slack, Jira, Git, meetings
— get everything flowing, and then figure out what to do with it. It feels like
the foundation and it is legible progress.

## Decision

**One source, end to end, through the full pipeline — including the stages that
feel skippable.** Then a second source, which is where you find out what was
accidentally source-specific.

**There is no ingestion-framework stage.** Adapters are written one at a time
against a fixed observation shape. **The "framework" is that shape.**

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Build the ingestion framework first | An ingestion framework with nothing downstream produces a pile of observations and no evidence that any of this works. **Six adapters is six times the surface area and one times the demonstrated value.** |
| Build the reasoning first, fake the data | Worse. The hard problems — entity fragmentation, admission, authority, vocabulary growth — **only appear with real messy input.** |
| Start with Slack, because that is where people talk | Lowest claim density, worst structure, and it surfaces admission, entity resolution and vocabulary problems **simultaneously.** |
| Start with documentation | A trap: docs are where staleness is worst, so a knowledge system built on docs first learns a stale world confidently and has nothing to contradict it with. |

## Evidence and reasoning

**[DESIGN DECISION]** Source ranking by claim density and structure:

| Source | Claim density | Structure | Verdict |
|---|---|---|---|
| Git / PRs / merged code | High — every merge is an implementation fact | Excellent — real ids, timestamps, authors, a diff | **Strong candidate.** Entity anchoring nearly free |
| Jira / work items | High for status and intent | Excellent | **Strong candidate**, and where decisions and intent actually live |
| Meeting transcripts | Medium — decisions and rationale, the scarcest things | Poor — no ids, unreliable attribution, noise | **Second** |
| Slack / Teams | Low per message | Poor | **Last** |
| Documentation | High per document | Medium | A trap — see above |

Start with a structured source so entity resolution is not the first problem you
hit. **Adding meetings second is what produces the first genuinely impressive
result:** a decision stated in a meeting, checked against what the code actually
does. Neither source alone can produce that.

**Every hard problem in this design is invisible until something downstream
depends on getting it right.** Four sources of unprocessed observations teach
you nothing except that ingestion works.

## Consequences

- Phase 1 has one adapter and a full pipeline, not six adapters and a pile.
- The second source becomes a **test** of what was accidentally source-specific
  — a much more useful thing to learn in week six than in month six.
- Phase 1's exit is a demonstration, not a feature list: **five real questions
  from our own history**, each answered with the implementation fact, the
  decision, the author, the date, and the intent/reality gap stated plainly.

## What would cause us to reconsider

A source that turns out to carry too few claims to demonstrate anything — which
would change *which* source is first, not the one-at-a-time rule.

## Source

`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0020](ADR-0020-the-brain-observes-the-workflow-before-it-controls-it.md),
[ADR-0018](ADR-0018-identity-keyed-extraction-first.md)
