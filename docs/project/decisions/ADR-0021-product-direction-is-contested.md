# ADR-0021 — The product direction is contested

**Status:** **SUPERSEDED by [ADR-0026](ADR-0026-product-direction-resolved-prd-is-exploratory.md), 2026-09-14.**
The project owner clarified, later the same day, that `prd.md` was written to
explore a curiosity question — not as a competing product decision — so there
was never an actual contest to resolve. **This record is kept as history, not
edited**, because the ambiguity it describes was real in the documents at the
time it was written; read ADR-0026 for the current position and do not treat
anything below as live.
**Date / context:** Discovered 2026-09-14 by comparing the current strategic
direction against `prd.md` (2026-09-06).

## Context

Two product directions exist in this project. Both are written down. Both are
serious. **They are not the same product, and neither document acknowledges the
other.**

### Direction A — recorded in the repository, 2026-09-06

A **macOS-first personal paperwork agent.** From `prd.md` and
`docs/product/04-product-thesis-and-decision.md`:

- Verdict: **GO WITH MAJOR CHANGES**
- Buyer: the Mac-primary professional with document obligations and no
  assistant — freelancers, consultants, small-practice accountants and lawyers,
  contractors, landlords, researchers
- Wedge: personal paperwork (receipts, statements, invoices, contracts, tax),
  because the job recurs on a calendar rather than on a guilt cycle
- Product promise: *"Nothing changes on your disk until you say so. Everything
  that changes is written down. Anything written down can be undone."*
- **Change 3, stated as non-negotiable: "cut the terminal / Git / developer-tools
  environment from the roadmap entirely, for now."** Reason given: *"maximum
  competition, zero advantage, and it drags the whole product into a market
  where Anthropic already ships."*

### Direction B — the current strategic hypothesis, 2026-09-14

A **knowledge system** serving organizational knowledge to external coding agents
through MCP, validated first on an internal engineering workflow.

- Buyer: **not identified in any document**
- Wedge: organizational knowledge for agents working in an engineering workflow
- Chain: knowledge system → knowledge system MCP → external agents → Principal Agent →
  Agent Runtime → controlled autonomous execution

## The contradiction, stated precisely

**Direction B targets approximately the segment Direction A ruled out**, and
the reasoning Direction A gave for ruling it out has not been retired,
addressed, or shown to be inapplicable.

That reasoning may well *be* inapplicable — Direction A's Change 3 argued
against a *file-organising developer tool*, and a knowledge system is a
materially different proposition. **But nobody has written that down.** An
argument is not retired by being ignored.

## What is NOT in dispute

Both directions share the same underlying architecture and most of the same
decisions. Verification, provenance, reversibility, the effect ledger, the
claim model and the runtime invariants are common to both. **The architecture
work is not wasted either way**, which is why this being open does not block
documentation — only implementation.

## Decision required

A named human must decide one of:

1. **Direction A stands.** Then the knowledge system architecture is infrastructure for a
   later phase, and `prd.md` is the live plan.
2. **Direction B supersedes it.** Then `prd.md` and `docs/product/` are marked
   SUPERSEDED with a dated reason, and Change 3's argument is explicitly
   answered rather than dropped.
3. **They are sequenced.** Then the sequence and the trigger between them are
   written down.
4. **They are different products for different markets.** Then say which one is
   being built now, and with what resources.

## Why this blocks

The two directions imply different first builds, different data models at the
edges, different buyers, and different evidence to gather next. Starting
implementation without deciding means building something that serves neither
well. Direction A's own §11.5 names the equivalent failure: *"Starting to code
before choosing one guarantees rework."*

## What would resolve it

A decision, recorded here and in `docs/project/11-architecture-change-log.md`.
Evidence that would inform it:

- **For A:** the content-vs-filename experiment on 500 real documents; the iOS
  folder-root spike; a diary study showing monthly recurrence.
- **For B:** five real questions answered from our own history in a way a
  document search structurally cannot; one confirmed cross-source contradiction
  a human agrees was worth raising.

Both are cheap relative to building either product.

## Source

`prd.md`; `docs/product/04-product-thesis-and-decision.md` §5.2, Part 6, Part 10,
§11.1, §11.5; current strategic direction 2026-09-14.

## Related

[ADR-0020](ADR-0020-the-brain-observes-the-workflow-before-it-controls-it.md),
[ADR-0002](ADR-0002-specification-vocabulary-is-canonical-for-code.md)
