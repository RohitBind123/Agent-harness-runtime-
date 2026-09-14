# ADR-0002 — Specification vocabulary is canonical for code; the handbook is canonical for principles

**Status:** **PROPOSED — NOT RATIFIED.** Two later documents assume it. Nobody
has decided it.
**Date / context:** Assumed 2026-09-05 (knowledge system review) and 2026-09-06 (product
research). Never confirmed by a decision.

## Context

This repository contains two overlapping architectures with different names for
related concepts:

- **The handbook** (51 chapters): Run / Episode / Step / Activity / Park;
  Surface / Edge / Substrate / Kernel / Ports / Domain; four state categories;
  the narrow waist.
- **The specification** (v1.0, revision 5): sessions, controller, ExecutionGraph,
  capabilities, contracts, packages, 39 numbered invariants, build order 0–12.

They are not translations of each other. They were written for different
purposes and neither states its relationship to the other.

## Decision (proposed)

**The specification's vocabulary is canonical for code. The handbook is
canonical for principles and derivation.** One paragraph, written down, saying
so.

## Alternatives considered

| Alternative | Why not chosen |
|---|---|
| The handbook is canonical for both | Its vocabulary is teaching-shaped — it derives concepts in an order that suits learning, not an order that suits a module layout. |
| Maintain both, with a translation table | A translation table is a third artefact that goes stale, and it does not settle which name a new module gets. |
| Reconcile into a single new vocabulary | The most correct option and the most expensive. It would invalidate cross-references across 51 chapters and a 5,000-line specification. |
| Leave it undecided | The current state. Its cost is below. |

## Evidence and reasoning

**[INFERENCE]** The cost of leaving it open is stated plainly in the knowledge system
review §1.7: *"Two constitutions with no stated relationship"* — which means
*"every architectural argument can be won by citing the other one."*

`docs/product/01-architecture-understanding.md` records the same thing as its
Finding A and `docs/product/04-product-thesis-and-decision.md` §11.5 names it
as a compounding factor in the biggest architectural risk: *"Starting to code
before choosing one guarantees rework."*

**The field is two candidates, not three.** A third option — that some existing
body of code is normative — was previously in play and is withdrawn: no such
code exists or informs this project. See
[ADR-0025](ADR-0025-no-external-codebase-is-evidence.md).

## Consequences

- **If ratified as stated:** new modules take specification names. The handbook
  keeps its own names and is read as derivation. Cross-references in both stay
  valid. One ADR, roughly half a day.
- **If left open:** the first implementation session picks a vocabulary by
  accident, and the second one argues with it.

## What would cause us to reconsider

Ratification either way closes this. **The measurable trigger to reopen it:**
the first substantial body of implementation code becomes a de facto third
vocabulary. A naming audit at the end of the first implemented stage reopens
this if module names have diverged from the specification's.

## Source

`docs/product/01-architecture-understanding.md` Finding A;
`docs/product/04-product-thesis-and-decision.md` §11.5;
`docs/architecture/organizational-brain-architecture.md` §1.

## Related

[ADR-0001](ADR-0001-repository-is-knowledge-base-not-implementation.md)
