# ADR-0011 — Standing is earned by independent corroboration; the gate is on the load

**Status:** ACCEPTED
**Date / context:** Memory Management Architecture ADR 5, 2026-09-02.

## Context

Something must stop a wrong claim from influencing future runs. The candidates
are: gate the write, or gate the read.

## Decision

**Deterministic checks reject at write. Nothing "accepts."** Standing is earned
by **independent corroboration from DISTINCT runs**, and the gate is on the
**LOAD**, not the write. A claim below the load floor is stored and **inert** —
it influences nothing until corroborated.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| A human gate per entry | A human bottleneck proportional to run volume. |
| A confidence the model asserts | Self-reported confidence from the system that produced the claim. |
| An evaluator model judging individual claims | Model self-evaluation is **biased rather than merely noisy — it leans toward yes, which is the answer you already had.** |

## Evidence and reasoning

**[CONFIRMED + INFERENCE]** A write gate needs an approver per run — either a
human bottleneck, or a model judging its own system's proposal. A **load floor**
needs nobody, costs one comparison, and **cannot be socially pressured.**

The corollary that is easy to get wrong: **the subsystem's value arrives on the
SECOND observation, never the first.** A Phase 1 that ships without
corroboration working is not an early version of the system — it is a different
and worse system that stores single observations and loads them.

Corroboration must count **DISTINCT runs**, which is why evidence is a joinable
table of references rather than an integer count.

## Consequences

- A wrong claim is **stored and inert** rather than blocked. That is the
  intended trade: a store of quarantined wrong claims is safe; a store that
  blocked them would need something to do the blocking.
- The load floor and the retire floor become **tuned numbers**, which puts them
  outside anything an evolution loop may edit — otherwise a loop could move the
  floor rather than improve the claims.
- **No floor value is defensible yet.** Tuning them before the extraction noise
  floor is measured is fitting to noise. See `docs/project/10-open-questions.md` Q11.
- Only a **human** may author a claim into existence above the floor. An
  evolve-authored claim does not inherit human authoring's confidence — that
  closes the displacement route around the floor.

## What would cause us to reconsider

A measured extraction noise floor that shows corroboration from distinct runs is
not discriminating — i.e. wrong claims corroborate at the same rate as right
ones. That would mean the runs are not independent, and the fix is in the
independence, not the floor.

## Source

`learning-notes/Memory Management Architecture.docx` §9, §36.1, §37.1 (ADR 5),
§37.3 (ADR 14), §38.1.

## Related

[ADR-0010](ADR-0010-the-model-proposes-and-never-writes.md),
[ADR-0015](ADR-0015-verification-before-knowledge.md)
