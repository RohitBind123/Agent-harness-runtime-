# Target Repository Structure

> **This document describes a target shape in a *different* repository, and
> creates nothing here.** Per
> [ADR-0001](decisions/ADR-0001-repository-is-knowledge-base-not-implementation.md),
> implementation happens in a separate implementation repository; this one is
> the justification layer. A first commit of a `src/` directory **here** would
> be a change of this repository's role, and ADR-0001 says that must be
> recorded deliberately rather than allowed to happen by accident.

**Status: PROPOSED.** No directory below exists anywhere.

---

## 1. Why this document is short, on purpose

`14-outside-in-review-2026-09-14.md` lists **"More architecture documents"**
among the things not to build, with the reason stated as the review's ninth
assumption:

> *"The most likely failure mode is not a wrong architecture. **It is a correct
> architecture, more of it, indefinitely.**"*

The runtime specification already contains a ~2,000-line directory tree for a
system with zero code, and that specification **classifies file-level
decomposition as an implementation note** — free to change without ceremony.
Writing a second such tree, for the knowledge plane, would reproduce exactly the
failure the review names.

So this document specifies four things and stops:

1. Top-level directories and what each owns.
2. The import contracts a linter can check.
3. The rule for deciding where a new file goes.
4. What each phase adds.

**File-level decomposition is deliberately unspecified.** Naming files nobody
will write, in an order nobody will write them, is not architecture.

---

## 2. The target shape

Derived from `16-high-level-implementation-architecture.md` §3-§4, not copied
from the runtime specification's tree.

```
  <implementation-repo>/
  |
  +-- contracts/        schemas and protocol definitions. imports NOTHING
  |
  +-- core/             the domain-agnostic knowledge core        [ADR-0028 bucket C]
  |     observation log · admission stages · entity identity
  |     extraction harness · reconciliation · claim store
  |     evidence · world model projection · retrieval
  |
  +-- capability/       the ONE surface. resolves a Principal, then calls core
  |                     CL1-CL4. Phase 1: four functions
  |
  +-- governance/       AUTHORED configuration                    [ADR-0028 bucket A]
  |     source-precedence policy · predicate vocabulary
  |     contradiction severity. Human-owned. Reviewed changes only.
  |     NO automated loop may write here, ever
  |
  +-- domains/          domain code behind a boundary             [ADR-0028 bucket B]
  |   +-- organizational/
  |         source adapters (git, jira, slack) · extraction prompts
  |         the specific admission rules
  |
  +-- security/         Principal, scopes, grants, tenant-in-key
  |                     knows nothing about claims
  |
  +-- storage/          one transactional substrate, behind a port
  |
  +-- observability/    the flight recorder. reads everything, writes nothing back
  |
  +-- evaluation/       offline. noise floor first. never on the request path
  |
  +-- tests/            mirrors the source tree
  |
  +-- docs/
```

**Not present, and that is the point:** no `runtime/`, no `principal/`, no
`mcp/`, no `distribution/`, no `learning/`, no `evolution/`. Each arrives in §5
when its phase requires it. **Do not create an empty directory to represent
future architecture.**

## 3. Import contracts

Enforced in CI, not in review. A boundary that is only prose is a convention,
and conventions are what this architecture exists not to rely on.

```
  contracts/     ──X──>  everything            (imports nothing at all)
  core/          ──X──>  domains/              the core is domain-agnostic
  core/          ──X──>  capability/           it is depended on, it does not depend
  core/          ──X──>  runtime/              when runtime exists. one-way, always
  domains/       ──X──>  storage/              domain code reaches the store only via core
  security/      ──X──>  core/                 no knowledge concepts in the identity model
  observability/ ──X──>  core write paths      read-only observer
  evaluation/    ──X──>  the request path      offline, always
  <any surface>  ──X──>  core/                 the path is capability/  [CL4]
  <anything>     ──X──>  governance/ writes    authored by a human, never by code
```

**The last line is the one most likely to be softened, and it must not be.** The
runtime specification makes `packages/` the evolvable surface precisely because
an evolution loop writes there and nowhere else. If governance configuration
ever lands in an evolvable surface, a loop can move the authority ordering
instead of improving the claims — which is the displacement route
[ADR-0006](decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md)
and [ADR-0024](decisions/ADR-0024-no-autonomous-knowledge-curation.md) both
exist to close.

## 4. Where does a new file go?

Three questions, in order:

1. **Would another organization, with entirely different tools, need this?**
   If no → it is not `core/`. *(This is `06-validation-strategy.md` §4's test,
   unchanged.)*
2. **Who is allowed to change it?** A named human by reviewed change →
   `governance/`. An engineer by code review → `domains/` or `core/` per (1).
3. **Does it do I/O against a specific external system?** → `domains/`, and it
   declares an effect tag.

If a file seems to need to live in `core/` but only this organization would want
it, **the design is wrong, not the rule.** The usual fix is that a mechanism
belongs in `core/` and its contents belong in `governance/` — the split
`06-validation-strategy.md` §4 already draws for the predicate registry, the
precedence policy and admission.

**Two known leaks sit inside `core/` today and are carried openly:** the six
claim `kind`s as enum *values*, and `scope` as a materialised path inside claim
identity. Both are recorded in
[ADR-0028](decisions/ADR-0028-the-knowledge-core-is-domain-agnostic.md). Neither
is fixed here, because fixing either is a schema decision blocked behind Q7.

## 5. What each phase adds

| Phase | Added |
|---|---|
| **0** | Nothing. `contracts/` and the import lint **are** Phase 0's engineering output — the dependency graph is enforced before any logic exists to violate it |
| **1** | `core/` (observation log, admission, entity identity, extraction, reconciliation, claim store, evidence, world model, retrieval) · `capability/` · `governance/` · `domains/organizational/` with **one** adapter · `security/` · `storage/` · `observability/` · `evaluation/` (noise floor only) · `tests/` |
| **2** | A second adapter in `domains/organizational/`. Entity **resolution** joins `core/`. Nothing structural is added — and if something must be, the Phase 1 boundaries were wrong |
| **3** | `core/verification/` — the probe loop. Temporal query paths |
| **4** | `mcp/` — a strict projection over `capability/`, with **fewer** capabilities than the internal surface. Q9 decided first |
| **6** | `runtime/` and `principal/`. **The first code in the execution plane.** Run/Episode/Step/Activity/Park, the ExecutionGraph, checkpoints, parking |
| **8** | `runtime/policy/`, budgets, the effect ledger, the autonomy ladder |
| **9+** | `distribution/`, `learning/`, `evolution/`, `diagnostics/` — each only when its trigger in §6 fires |

---

## 6. The deferred runtime capability register

The purpose of this table is to prevent two opposite failures: **forgetting the
long-term runtime architecture**, and **building it before the knowledge plane
has earned it.** Every row is DESIGNED and none is implemented.

Where `08-build-order.md` §4 already gives a trigger, it is reused verbatim
rather than restated in new words.

| Capability | Purpose | Owner | Depends on | Trigger to introduce | Status |
|---|---|---|---|---|---|
| **Action identity** | Reuse a result only on a full identity match, so a retry is not a re-spend | `runtime/identity/` | contracts | **Its knowledge-plane form (X1) is Phase 1 and is not deferrable.** The runtime form arrives with the first runtime action | DESIGNED. X1 required now |
| **Idempotency / re-delivery** | A redelivered observation is a no-op | `core/` (A4) | content hash | **Phase 1** | DESIGNED |
| **Transactional outbox** | A claim write and its notification stop being two writes with a gap | `core/` | claim store | *"When the first consumer reacts to a knowledge-system event — the participation check is exactly that consumer"* | DESIGNED |
| **Leases + version CAS** | Two workers on one observation stop relying on database default behaviour | `core/` then `runtime/leasing/` | storage | *"When ingestion runs more than one worker. **Before that it is theatre**"* | DESIGNED |
| **Park** | A claim or run awaiting human confirmation waits holding no resources | `runtime/parking/` | event spine | *"When human confirmation enters the claim lifecycle"* | DESIGNED |
| **Execution graph** | One representation of in-flight work — plan, state, progress, dependencies, checkpoint | `runtime/controller/` | contracts, sessions | Phase 6, with the first Principal Agent Run | DESIGNED |
| **Checkpoints / recovery** | Every advance survives `kill -9` | `runtime/controller/` | execution graph | Phase 6 | DESIGNED |
| **Effect ledger** | Reversibility: what was done, and how to undo it | `runtime/execution/` | effect tags | Phase 8, with the first reversible effect | DESIGNED |
| **Effect tags** | Every tool declares its blast radius; unknown third-party defaults to EFFECTFUL | `domains/`, `runtime/policy/` | contracts | Phase 6 — **the tag is declared with the first tool, not retrofitted** | DESIGNED |
| **Policy / approval gate** | An effectful tool is uncallable without a resolved approval, in the runner rather than by prompting | `runtime/policy/` | effect tags | Phase 8 | DESIGNED |
| **Budgets** | Reserve-then-settle, so stopping waiting is not confused with stopping spending | `runtime/budget/` | model port | Phase 8 | DESIGNED |
| **Event system / spine** | One durable delivery primitive. No second event stream | `runtime/events/` | outbox | With the outbox | DESIGNED |
| **Model providers** | One metered, capped, abortable door to a model | `runtime/ports/` | contracts | **Phase 1 already needs one** — for the single extraction step, behind a port | DESIGNED |
| **Capabilities vs tools** | *What* can be accomplished, separated from *how* | `runtime/`, `domains/` | contracts | Phase 6 | DESIGNED |
| **Plugins** | Third-party extension surface | `plugins/` | contracts | No trigger. Nothing in any planned phase | DESIGNED |
| **Diagnostics** | *Why did this run do that*, answerable without adding logging | `diagnostics/` | traces | Phase 9+ | DESIGNED |
| **Distribution** | Partition ownership, rebalance, drain | `runtime/distribution/` | leases | *"Only when a single substrate can no longer serve the event rate"* | DESIGNED |
| **Learning** | Asynchronous improvement that never blocks the request path | `learning/` | traces | No trigger yet | DESIGNED |
| **Evaluation** | Offline measurement against a pinned store snapshot | `evaluation/` | task set, oracles | **Phase 1** — the noise floor is measured first, before any tuning | DESIGNED |
| **Evolution** | A loop that proposes changes and never promotes them | `evolution/` | attribution, rollback | **No trigger, and a standing prohibition on the knowledge store** ([ADR-0024](decisions/ADR-0024-no-autonomous-knowledge-curation.md)) | DESIGNED |

**Two rows deserve re-reading together.** *Evolution* has no trigger and a
standing prohibition; *governance* may never be written by code. Those are the
same boundary seen twice, and it is the one this architecture is least willing
to lose.

---

## Related

[`16-high-level-implementation-architecture.md`](16-high-level-implementation-architecture.md) ·
[ADR-0028](decisions/ADR-0028-the-knowledge-core-is-domain-agnostic.md) ·
[ADR-0001](decisions/ADR-0001-repository-is-knowledge-base-not-implementation.md) ·
[`08-build-order.md`](08-build-order.md) §4-§5 ·
[`06-validation-strategy.md`](06-validation-strategy.md) §4
