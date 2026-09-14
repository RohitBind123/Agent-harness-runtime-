# ADR-0027 — The system is a general-purpose agent Brain + Runtime; the Organizational Brain is its first substrate

**Status:** ACCEPTED
**Date / context:** 2026-09-14, project owner's direction, given in a strategic
architecture session.

## Context

Two documents in this repository state the product's identity, and both scope
it organizationally.

`00-north-star.md` §1: *"A system that lets an agent act inside an organization
with organizational knowledge that is reconciled, time-aware, and carries its
basis."* And §6 lists **"A general agent platform"** among the things that are
explicitly **not** the product, with the reason: *"'Platform' requires a third
and fourth environment and an abstraction that survives contact with them. That
is a 2028 question. Anyone pitching it as a platform now is pitching a hope."*
`PROJECT_BOOTSTRAP.md` §2 carries the short form: *"Not a general-purpose agent
platform."*

The project owner has stated that this scoping is wrong at the level of what is
being built — that the long-term system is a **general-purpose agent Brain +
Runtime**, and that the Organizational Brain is the **first major substrate and
proving ground** through which it is being built and validated, not the
system's definition.

Read carelessly, that reverses a recorded position. Read carefully, the two
statements are about different questions — one about architecture, one about
what is sold and built now — and the repository had no place to say so.

## Decision

**The canonical long-term identity is a general-purpose agent Brain +
Runtime.** The **Organizational Brain is the first substrate and proving
ground** — the concrete environment in which evidence, memory, world state,
temporal reasoning, authority, contradiction, provenance and verification are
made reliable.

**The §6 "not a general agent platform" row is narrowed, not retired.** It now
scopes to *the product we sell and build now*. Its warning survives verbatim,
because it is a guard against premature generality and that guard is still
needed — this ADR makes generality the architecture's target, not a licence to
build for imagined second and third environments.

**Two registers are kept distinct and neither substitutes for the other:**

| Register | Term | Where |
|---|---|---|
| Product identity | **general-purpose agent Brain + Runtime** | `PROJECT_BOOTSTRAP.md` §2, `00-north-star.md` §1, this ADR |
| Current substrate | **Organizational Brain** | Named as the *first* substrate; never as the system's definition |
| Engineering subsystem | **the knowledge system** · **the runtime** · **Principal Agent** | ADRs, architecture map, domain model, docs 16-17 |

The anti-collapse rule, stated so a future session cannot reconstruct the
wrong reading: **"we are building an organizational knowledge product" is an
incorrect summary of this project.** The correct one is *"we are building a
general-purpose agent Brain + Runtime, beginning with the Organizational Brain
as the first serious substrate."*

**This changes no build-order stage, no ADR's decision, and no requirement.**
It changes what the work is understood to be for.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Retire the "not a general agent platform" row outright | Loses a guard that is still load-bearing. The row's argument — that platform-ness requires a third and fourth environment and an abstraction that survives contact with them — is *unaffected* by this decision and remains true. Deleting it would read as permission to generalise on speculation |
| Treat the owner's direction as architecture guidance only, changing no product document | Leaves `00-north-star.md` §1 and `PROJECT_BOOTSTRAP.md` §2 stating an identity the owner says is wrong. Future sessions read those first; the error would propagate |
| Restore "Brain" as the engineering subsystem name throughout | Would revert commit `c011eb3`, which retired it on the owner's own instruction eight hours earlier as too ambiguous. The two instructions are reconciled by register, not by reversal — see `15-vocabulary.md` |
| Rewrite the build order to match the broader identity | The build order already sequences exactly this work and the owner explicitly asked that it not be rewritten to look neat. Sequencing is unchanged; only the statement of what each phase earns is added |

## Evidence and reasoning

**[REQUIREMENT]** The identity is stated by the project owner. It is not
derived from evidence in this repository and is not presented as such.

**[INFERENCE]** The narrowing, rather than the reversal, is what makes both
statements simultaneously true. "Is the architecture general-purpose?" and "is
the product we are building and selling a general platform?" are different
questions with different answers, and the corpus previously had one row
answering both.

**[DESIGN DECISION]** Building the knowledge system before the runtime is not
a sequencing preference. Autonomous execution can only be trusted once the
system it acts on is reliable about what is true, when it was true, and on what
basis — so evidence, memory, world state, temporal reasoning, provenance,
reconciliation and verification are earned first. This is the same ordering
`00-north-star.md` §7 already states (*"legal and measurable before good"*),
applied one level up.

**Corroboration, and its limits.** The corpus already contained the
general-purpose reading in three hedged places — the runtime-as-surviving-asset
argument (`00-north-star.md` §4, tagged `[INFERENCE]`), the general-claim-store
hypothesis (`PRD.md` §6.3), and the developer-infrastructure fallback
(`docs/product/04-product-thesis-and-decision.md` §5.2, which says *"do not
start there"*). **None of these is evidence that the direction is right.** They
establish only that it was already visible and already discounted. The honest
counter-argument at `00-north-star.md` §4 — that this is a general-purpose
platform justified by breadth of future application, with no code and no user —
**is not retired by this ADR** and should be read alongside it.

## Consequences

- `00-north-star.md` §1 and `PROJECT_BOOTSTRAP.md` §2 state the general-purpose
  identity with the Organizational Brain named as first substrate.
- A new architecture document
  (`16-high-level-implementation-architecture.md`) carries the structure, and
  `17-target-repository-structure.md` the target shape. The PRD continues to
  describe current product validation and does not become an architecture
  document.
- **The cost, stated plainly: this makes the project easier to over-build.** A
  general-purpose identity is exactly the licence that produces a correct
  architecture, more of it, indefinitely — which
  `14-outside-in-review-2026-09-14.md` A9 names as *"the failure mode with the
  highest prior"* in this repository. The mitigations are the ones already in
  place and they are not new ceremony: every stage exits on a measurement,
  every deferred capability carries a named trigger, and nothing is built
  before its trigger fires.
- **It does not move any component closer to existing.** Every status label is
  unchanged. Zero lines of product code exist.

## What would cause us to reconsider

Reaching Phase 4 without a measured improvement in agent output would put the
whole chain in question, this identity included — but that falsifies the
product, not the scoping.

The narrower trigger specific to *this* decision: **a second substrate that
turns out to need a different knowledge core.** If the generic/domain split in
`17-target-repository-structure.md` cannot hold a non-organizational substrate
without changing the core's schema, then "general-purpose" is a claim the
architecture does not support, and the honest response is to say so and rescope
to the substrate we actually have.

The inverse trigger, for the §6 row: if a third and fourth environment are
reached and the environment abstraction survives contact with them, the row's
own condition is met and it retires on its own terms rather than by argument.

## Source

Project owner's direction, 2026-09-14. `docs/project/00-north-star.md` §1, §4,
§6; `PROJECT_BOOTSTRAP.md` §2; `docs/project/PRD.md` §6.3;
`docs/project/14-outside-in-review-2026-09-14.md` A9.

## Related

[ADR-0026](ADR-0026-product-direction-resolved-prd-is-exploratory.md) — which
resolved *which* direction; this one scopes it.
[ADR-0028](ADR-0028-the-knowledge-core-is-domain-agnostic.md) — the structural
decision that makes a first substrate buildable without contaminating the core.
[ADR-0001](ADR-0001-repository-is-knowledge-base-not-implementation.md),
[ADR-0025](ADR-0025-no-external-codebase-is-evidence.md)
