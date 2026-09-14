# ADR-0028 — The knowledge core is domain-agnostic; organizational logic sits behind a boundary

**Status:** ACCEPTED
**Date / context:** 2026-09-14, following
[ADR-0027](ADR-0027-general-purpose-brain-and-runtime-organizational-first.md).

## Context

[ADR-0027](ADR-0027-general-purpose-brain-and-runtime-organizational-first.md)
makes the Organizational Brain the **first** substrate rather than the product.
That is only meaningful if the first substrate can be built without the core
becoming organizational — otherwise "first" is a word with no structural
consequence, and the second substrate is a rewrite.

The repository already states the rule in prose.
`06-validation-strategy.md` §4 gives a seven-row generic/local table and the
test: *"would another organization with different tools need this, or only us?
If only us, it is configuration, not architecture — and it goes in a file the
architecture reads, not in the architecture."* `01-architecture-map.md` §3 gives
the complementary "what must stay runtime-generic" table, whose failure mode is
a domain-named method: *"extend the protocol generically — not with a
`brain_query` method."*

What does not exist is a statement of **where each thing lives**, and one
specific trap makes that gap expensive. The runtime specification's §4.5 makes
`packages/` the harness *because* `evolution/` writes to `packages/registry/`
and nowhere else — that is what makes *"the runtime never modifies itself"*
enforceable. So "put the domain configuration in packages" would place the
source-precedence policy and the predicate registry **inside the surface an
evolution loop is licensed to edit**, contradicting
[ADR-0006](ADR-0006-authority-is-authored-configuration-never-inferred.md) and
`02-domain-model.md` §2.10's *"outside anything the agent may edit."*

## Decision

**The knowledge core is domain-agnostic. Organizational specifics live in one
of two places outside it, and which place is decided by who may change the
thing — not by what kind of artefact it is.**

Three buckets:

| Bucket | What it holds | Who may change it |
|---|---|---|
| **A — Authored governance configuration** | Source-precedence policy · predicate vocabulary · contradiction severity rules | A **named human**, by reviewed change. **Never any automated loop.** Explicitly *not* in any evolution-writable surface |
| **B — Domain code behind a code boundary** | Source adapters (Git / Jira / Slack) · extraction prompts · the specific admission rules | Engineers, by ordinary code review. Adapters are tool-shaped — they declare an effect tag and do I/O — not configuration-shaped |
| **C — Generic core** | Observation log · claim / version / evidence tables · bitemporal columns · tenant-in-key · world model as projection · contradiction register *as a mechanism* · entity *identity* · capability-signature shape | Engineers, and a change here is an architecture change |

**The test for placement is `06-validation-strategy.md` §4's, unchanged.** This
ADR adds only the split inside "local": governance configuration and domain code
are different things with different change authority, and merging them is how
authority configuration ends up somewhere a loop can reach.

**Two things currently read as generic core and are not.** Both are recorded
here rather than fixed, because fixing either is a schema decision blocked
behind Q7:

1. **The six claim `kind`s** (`observation-backed / decision /
   implementation-fact / outcome / constraint / term`) are a taxonomy of
   *organizational* assertions, derived from one requirement — that *"product
   says X, code does Y"* be expressible. What is generic is the **rule** that a
   claim carries a kind and the kind bounds which predicates it may assert,
   which is already the `kinds_allowed` field on the predicate registry. **The
   enum values are domain.** As a schema enum or CHECK constraint they make the
   first non-organizational substrate a migration of every row.
2. **`scope` as a tenant-relative materialised path**, where *"narrower than"*
   is a prefix test. A prefix test assumes knowledge nests. The design's own
   Property 7 says the opposite — scopes are *"overlapping, per-source, and
   often per-channel"* — and **Q10 records that no complete model exists.**
   `scope` sits **inside claim identity** (CS2: identity is
   `(subject, predicate)` within a scope), which is the most expensive place in
   the system to hold an unresolved assumption.

A third, smaller: **`entity_type`**. Entity *identity* is generic schema; the
type vocabulary (service, team, person, carrier) is domain — the same
mechanism/enum split as the kinds.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Put domain specifics in a `packages/`-style configuration tree, mirroring the runtime specification | Two independent failures. The package manifest has **no field for code**, so a source adapter — network I/O, pagination, backfill, thread reconstruction — is not expressible in it. And `evolution/` writes to `packages/registry/` and nowhere else, so authority configuration placed there lands inside the evolvable surface, breaking [ADR-0006](ADR-0006-authority-is-authored-configuration-never-inferred.md) |
| One "local" bucket rather than two | Loses the only distinction that matters: change authority. A prompt and a precedence policy are both "domain", and exactly one of them may never be touched by an automated loop |
| Make the core generic *now* by parameterising kinds, scope and entity types | Premature, and it would resolve Q7 silently. The claim-store schema is DISPUTED between two documents; adding a third shape to satisfy a substrate that does not exist is architecture ahead of requirement. Recording the leak costs nothing and preserves the option |
| Accept the coupling and treat the Organizational Brain as the product | That is the position [ADR-0027](ADR-0027-general-purpose-brain-and-runtime-organizational-first.md) changed |

## Evidence and reasoning

**[DESIGN DECISION]** The three-bucket split is justified by its own argument —
change authority is the property that determines where a thing may safely live —
not by evidence. No substrate other than the organizational one exists, so
nothing here has been tested against a second one.

**[FACT — verifiable in this repository]** The runtime specification's §4.5
states that `evolution/` writes to `packages/registry/` and to nothing else, and
`02-domain-model.md` §2.10 states that the source-precedence policy is
*"outside anything the agent may edit."* Placing the latter in the former is a
direct contradiction, and it is the specific error this ADR exists to prevent.

**[INFERENCE]** The two named leaks are leaks *because* the substrate they were
derived from is the only one anyone has looked at. That is not a criticism of
the derivation — a taxonomy of organizational assertions is the correct thing to
derive from an organizational requirement. It becomes a defect only at the
moment the core claims to be general, which is what
[ADR-0027](ADR-0027-general-purpose-brain-and-runtime-organizational-first.md)
just made it claim.

## Consequences

- `17-target-repository-structure.md` expresses the three buckets as directory
  boundaries with import contracts that a linter can check. A boundary that is
  only prose is a convention, and conventions are what this architecture is
  designed not to rely on.
- **Two known leaks are carried openly rather than fixed.** That is a real cost:
  a future session reading the schema will see an enum that looks settled. The
  mitigation is that both are named here, in
  `01-architecture-map.md` and in Q7, so the cost is visible rather than latent.
- **This adds no work to Phase 1.** Every Phase 1 component keeps its current
  home; what changes is that adding a Slack-specific rule to the core is now a
  boundary violation with a name, rather than a judgement call.
- The first real test of this decision cannot happen until a second substrate
  exists, which is not scheduled. **Until then it is an untested structural
  claim**, and should be read as one.

## What would cause us to reconsider

A second substrate that cannot be built without changing the core's schema.
That would mean the split is drawn in the wrong place — and the useful response
is to move the line and say where, not to abandon the separation.

Also: if the predicate vocabulary or the kind set turns out to need per-substrate
extension *within* the organizational substrate — different teams needing
different kinds — the bucket-A/bucket-C line is wrong at a smaller scale, and
that is cheaper to learn.

## Source

`docs/project/06-validation-strategy.md` §4;
`docs/project/01-architecture-map.md` §3, §2.4, §2.7;
`docs/project/02-domain-model.md` §2.10, CS2;
`docs/architecture/universal-runtime-v1.0-architecture-specification.md` §3
rule 4, §4.5, §13;
`docs/project/10-open-questions.md` Q7, Q10.

## Related

[ADR-0027](ADR-0027-general-purpose-brain-and-runtime-organizational-first.md),
[ADR-0006](ADR-0006-authority-is-authored-configuration-never-inferred.md),
[ADR-0022](ADR-0022-predicate-vocabulary-is-closed-and-reviewed.md),
[ADR-0024](ADR-0024-no-autonomous-knowledge-curation.md),
[ADR-0003](ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md)
