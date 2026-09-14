# ADR-0015 — Verification before knowledge

**Status:** ACCEPTED
**Date / context:** Runtime specification invariant **I18**; handbook Ch 28.
Nominated in the specification §10.7 as one of the two invariants carrying the
most weight.

## Context

Something must decide whether a piece of work succeeded. The cheap answer is to
ask a model. The cheap answer is the failure most likely to damage a product.

## Decision

**Only verified observations update knowledge.** A model judgement **may lower**
a passing check set and **may never raise** a failing one.

Verification is deterministic: post-conditions written **before** the work,
evaluated against the world, with **no model involved**.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| A model grades the output | See the evidence below. |
| A model grades with a rubric | A rubric constrains vocabulary, not the bias. |
| A second, different model grades | Reduces correlation; does not remove the shared preference for fluent, well-structured output. |
| Human review of every result | Does not scale, and is the thing automation is meant to make unnecessary. |

## Evidence and reasoning

**[CONFIRMED]** *"A model asked to evaluate its own work shares a training
distribution, and therefore a set of blind spots, with the model that produced
it. It will approve fluent, well-structured, wrong output because that is what
it was trained to prefer."*

And the reason this ranks above reliability work: **a reliability defect
produces an alert; a confidently wrong result produces an artifact someone acts
on.** The failure that kills an agent product is not that the pool wedges at
high concurrency — you will not have high concurrency for months.

The asymmetry (may lower, never raise) is what makes a model judgement safe to
use at all: it can only ever make the system more cautious.

## Consequences

- Verification stage is placed **before** scale work in the build order, which
  is counter-intuitive and deliberate.
- Every capability needs deterministic post-conditions, which is real design
  work per capability and is the cost of the guarantee.
- The Principal Agent may lower an outcome verdict and never raise it, which is
  the same rule one layer up.
- A fourth verdict — **UNDETERMINED** — is required, for cases where the
  measurement cannot say. A system with only pass/fail will report one of them
  falsely.

## What would cause us to reconsider

Nothing. This is nominated as one of the two load-bearing invariants and is
listed in the containment set — outside anything an evolution loop may edit.

## Source

`docs/architecture/universal-runtime-v1.0-architecture-specification.md` §10.4
(I18), §10.7; `docs/handbook/chapters/28-reflection-grading-and-self-correction.md`.

## Related

[ADR-0011](ADR-0011-standing-is-earned-by-independent-corroboration.md),
[ADR-0014](ADR-0014-the-principal-agent-is-a-run-not-a-layer.md)
