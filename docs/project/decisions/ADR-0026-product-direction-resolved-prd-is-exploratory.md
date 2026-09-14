# ADR-0026 — The product-direction contest is resolved: `prd.md` is exploratory, not a competing decision

**Status:** **ACCEPTED — supersedes [ADR-0021](ADR-0021-product-direction-is-contested.md).**
**Date / context:** 2026-09-14, recorded from a direct statement by the project
owner in conversation.

## Context

ADR-0021 recorded what it read as two serious, competing product directions:

- **Direction A** — `prd.md` (2026-09-06): a macOS-first personal
  paperwork agent, verdict GO WITH MAJOR CHANGES, with a named buyer and a
  non-negotiable Change 3 ("cut the terminal / Git / developer-tools
  environment from the roadmap entirely").
- **Direction B** — the knowledge system direction (2026-09-14), targeting
  approximately the segment Change 3 ruled out, with no buyer identified.

ADR-0021 marked this **OPEN — BLOCKING**, and every downstream document —
`PROJECT_BOOTSTRAP.md`, `00-north-star.md`, `10-open-questions.md` (Q1),
`04-implementation-map.md`, `08-build-order.md`, `09-do-not-assume.md`, and
`docs/project/PRD.md` §0.1 / §4.2 / §20 / §21 D1 — treated resolving "which
product" as a blocking decision only a named human could make, and recorded
that nobody had made it.

## Decision

**The project owner states directly (2026-09-14) that `prd.md` was written to
explore a curiosity question — how the agent runtime could be used to control
iOS or macOS — and was never intended as a competing product decision.**

Consequently:

- **There is no product-direction contest.** `prd.md` and the Organizational
  knowledge system direction were never actually competing for the same "which product do
  we build" decision; one is an exploratory research artefact, the other is
  the live direction.
- **The knowledge system direction, as documented in
  `docs/project/00-north-star.md` and `docs/project/PRD.md`, is the live
  product direction.** `docs/project/PRD.md` is the project's actual PRD, not
  one of two contended options.
- **`prd.md`'s Change 3 argument does not need to be "answered."** It was an
  argument against building a macOS/iOS developer-tools product as *the*
  product. Since that was never the live direction, the argument has no
  decision to block.
- **Q1, as framed in `10-open-questions.md`, is RESOLVED.** Moved to the
  Resolved section with this ADR as its record.

## Alternatives considered

- **Sequence them** — treat B as infrastructure with A as a later consumer.
  Rejected as the reading here: the owner's statement is that A was curiosity,
  not a considered phase of B.
- **Different products for different markets, decide resourcing.** Rejected
  for the same reason — this presumes A was a live candidate needing a
  resourcing decision, which it was not.
- **Leave ADR-0021 as the live record and treat this as an update to it.**
  Rejected. ADR-0021 accurately recorded a genuine, real ambiguity that existed
  in the documents at the time — it was not wrong when written. The correct
  move per the project's own decision discipline is to supersede it with a
  dated new record, not edit it to look as if the ambiguity was never there.

## Evidence and reasoning

**[FACT]** The owner's direct statement in this conversation, 2026-09-14. This
is a decision, not an inference — the strongest evidence class available for a
product-direction question, and exactly the kind of input `10-open-questions.md`
Q1 stated was required: *"a named human picks A, B, C or D."*

## Consequences

- **`prd.md`'s banner is corrected** from "CONTESTED, NOT SUPERSEDED" to
  reflect that it is an exploratory document that does not compete with the
  live direction. It is **not deleted or marked SUPERSEDED itself** — it
  remains a record of real research into a real question (runtime-driven OS
  control), which may become relevant again on its own terms later. Only its
  *contested-with-the-live-direction* framing is corrected.
- **`docs/project/PRD.md` is confirmed**, not provisional-pending-Q1. Its §0.1,
  §4.2, §20, §21 D1 and §26 references to Q1/Change 3 as unresolved are
  corrected to reflect the resolution.
- **`08-build-order.md`'s Stage 0 exit criterion** ("Q1 is decided and
  recorded") is now partially satisfied — the product-direction half of Stage
  0's decision requirement is met. Q2 (the source-precedence policy) remains open.

## What would cause us to reconsider

If the owner later decides to actually pursue the iOS/macOS runtime-control
exploration as a real product — rather than as the curiosity project it was —
that is new information and needs its own ADR. This one does not lapse on its
own; a future direction change is recorded, not assumed.

## Source

Project owner statement, 2026-09-14, this conversation.

## Related

[ADR-0021](ADR-0021-product-direction-is-contested.md) (superseded by this),
[ADR-0025](ADR-0025-no-external-codebase-is-evidence.md)
