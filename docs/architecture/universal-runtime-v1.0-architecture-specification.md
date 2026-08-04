# Universal Runtime v1.0 — Architecture Specification

> **An Operating System for autonomous AI agents.**
>
> Repository structure, component responsibilities, the five core contracts, the enforceable
> invariant set, the distributed execution model, and the diagnostics surface.
>
> **Revision 4 — final.** Supersedes revisions 1 to 3.

---

## Table of Contents

| § | Section | |
|---|---------|---|
| 1 | [Revision log — what changed and why](#1-revision-log) | |
| 2 | [Scope — what this document is, and is not](#2-scope) | |
| 3 | [Design rules the tree obeys](#3-design-rules-the-tree-obeys) | 14 |
| 4 | [Additions made during review](#4-additions-made-during-review) | |
| 5 | [The execution model: three loops, one graph](#5-the-execution-model-three-loops-one-graph) | |
| 6 | [**ExecutionGraph — the single runtime execution model**](#6-executiongraph--the-single-runtime-execution-model) | **new** |
| 7 | [The complete repository tree](#7-the-complete-repository-tree) | |
| 8 | [Component reference](#8-component-reference) | |
| 9 | [Core specifications](#9-core-specifications) | 8 |
| 10 | [Runtime invariants](#10-runtime-invariants) | **32** |
| 11 | [Distributed runtime](#11-distributed-runtime) | |
| 12 | [Observability: telemetry, diagnostics, experience](#12-observability-telemetry-diagnostics-experience) | |
| 13 | [Dependency rules, enforced in CI](#13-dependency-rules-enforced-in-ci) | |
| 14 | [Component block diagram](#14-component-block-diagram) | |
| 15 | [Build order](#15-build-order) | |
| 16 | [**Modification log**](#16-modification-log) | **new** |

---

## 1. Revision log

Seven gaps were raised in review. Five are adopted as raised, one is adopted with a technical
correction, and one is a documentation-convention fix rather than a missing section. Working through
them surfaced three further gaps that the review did not name.

### 1.1 Adopted as raised

| # | Gap | Resolution |
|---|-----|-----------|
| 1 | **Runtime Manifest** | New root file `runtime.manifest.yaml`, new package `runtime/manifest/`, specified in §9.1. It is the runtime's *identity* — distinct from `configs/`, which holds tunables. Two deployments with the same manifest fingerprint are the same runtime; two with different fingerprints are not comparable, which is what makes an evolution measurement meaningful. |
| 2 | **Package Manifest specification** | Specified field-by-field in §7.2, with a conformance suite at `tests/conformance/`. Since packages are the harness, this is the most important contract in the system and it was previously named but never defined. |
| 3 | **Capability Descriptor specification** | Specified in §7.3. The review's suggested `cost_estimate` and `latency_estimate` fields are adopted and load-bearing: they are what allow the Policy Engine to reserve budget *before* execution rather than discovering the cost afterwards. |
| 4 | **Tool Descriptor specification** | Specified in §7.4. `idempotency` is promoted to a required field, because it interacts directly with action identity — a tool that declares itself non-idempotent changes replay semantics and must never be silently replayed. |
| 6 | **Runtime Invariants** | Consolidated into §8 as twenty numbered invariants, each with its enforcement mechanism and the test file that proves it. Scattered "never" clauses in the component reference now point here. |
| 7 | **Diagnostics** | New top-level `diagnostics/` tree and §10. Diagnostics is not telemetry: different consumer, different question, different retention, different access control. |

### 1.2 Adopted with a correction

**#5 — Distributed runtime.** Added as §9, with one disagreement recorded.

The review lists *leader election* among the distributed primitives to reserve space for. **This
runtime should not need leader election, and adding it would be a regression.** Mutual exclusion is
already provided per-entity by a lease claimed in the same statement as a version compare-and-swap,
and work distribution is already provided by claim-based relay with one event in flight per
partition. Both are decentralised: N workers, zero coordination.

Leader election would introduce a single coordination point, a split-brain failure mode, and a
failover gap during which nothing advances — in exchange for a guarantee the design already has.
The one case that genuinely wants a singleton is a periodic job that must not run twice, and the
sweeper is not one of those: sweeping is idempotent and claim-based, so running it on every worker
is correct and is the reason recovery is continuous rather than boot-only.

§9 therefore covers worker identity, heartbeat, partition ownership, rebalancing, drain and clock
skew — and states explicitly why leader election is absent, so that a future engineer does not
"discover" the omission and fix it.

### 1.3 Documentation convention rather than a section

**"Avoid locking in overly detailed implementation choices."** Correct, and the fix is structural
rather than editorial. Every normative statement in this document is now distinguishable from a
current implementation choice:

> **NORMATIVE** — a requirement. Changing it changes the architecture. Enforced by a test.
>
> **IMPLEMENTATION NOTE** — how we do it today. Free to change without an ADR.

Concrete names remain in the tree, because a scaffold whose leaves are abstractions is not a
scaffold. The distinction lives in the prose, where the confusion actually occurs.

### 1.4 Round four — one execution model, and a naming correction

Round four came from a design critique plus a request to make ExecutionGraph fully expressive.
Three changes are adopted, one is adopted with a correction, and **one is rejected**.

#### Adopted

| # | Change | Where |
|---|--------|-------|
| 1 | **ExecutionGraph becomes the single runtime execution model** — plan, state, progress, dependencies and checkpoint in one artifact. It supports linear, parallel, conditional, retried, timed-out, approved, checkpointed and dynamically inserted work, with no DAG engine and no workflow engine. | §6, §9.8 |
| 2 | **The graph projection moves into Parallel Context Assembly.** It is a read-only input to the Decision Engine rather than only an output of it. | §6.2 |
| 3 | **`capability_runtime/` and `tool_orchestration/` collapse into `capability_executor/`.** | §7.20 |

#### Adopted with a correction — the "cognitive sandwich"

The critique is that having both a reasoning Router and a Tool Orchestrator that "dynamically decides
tool order" creates a second, hidden planning layer. **The concern is right and the diagnosis was
half right.**

Revision 3 had already moved *binding* to plan time (§9.5.3), so tool selection was never happening
at execution time. But `capability_graph_builder.py` and `tool_chain_builder.py` did compute a tool
chain at runtime, and that genuinely was a second planning layer.

The correction, adopted in full: **a capability's internal chain is declared, never computed.** The
Capability Executor reads an authored, versioned recipe from the package and executes it. There is
now **no reasoning of any kind below the Decision Engine**, and the collapse of the two packages
follows naturally — once nothing is being orchestrated, an orchestrator is just an executor.

Binding resolution moves to a deterministic step of its own, `runtime/intelligence/binding/`, which
runs **after** the Decision Engine and **before** the Policy Gate. That placement is better than
either previous option: the resolution is deterministic and auditable, and the Policy Gate now sees
concrete tool ids to authorise rather than abstract intents.

#### Rejected — "the Policy Gate has disappeared"

**This one is not correct, and adopting it would be a regression.** The Policy Gate has been a hard,
non-bypassable step between decision and execution since revision 1. It is `runtime/policy/`; it
emits `ValidatedExecutionContract`; `effect_tag_enforcer.py` makes an effectful tool structurally
uncallable without a resolved approval; and invariant I14 has a test.

Nothing about it moved. What changed in revision 4 is that it is now **stronger**, because binding
resolution runs before it — the gate authorises concrete tools instead of intents.

The critique most likely came from reading a simplified flow diagram rather than §7.6. That is a
documentation failure rather than an architecture one, so the fix is documentation: the gate is now
drawn as a full-width barrier in §14 and appears in every flow diagram in the document. A safety
control that reviewers cannot find is a safety control that will eventually be removed by someone
who did not find it.

#### The naming correction

`Router` is renamed **Decision Engine**, and the reason is my own naming rule rather than taste.
Rule 5 requires a name to communicate responsibility, and the tree contained four routers —
`models/model_router.py`, `runtime/controller/work_class_router.py`,
`runtime/events/event_type_router.py`, and `runtime/intelligence/router/`. Three of those genuinely
route. The fourth is the system's only cognitive step, and "router" implied static rule-based
dispatch. `runtime/intelligence/decision/` now names what it does, and the collision is gone.

#### What was explicitly not done

No DAG engine, no workflow engine, no scheduler redesign, no orchestration service, no new runtime
layer. The layer count went **down** by one. §16 lists every modified section.

---

### 1.5 Round three — the execution model, validated against a real scenario

A concrete scenario — *switch to dev, pull, read the last ten commits, then check Jira access* —
was used to test whether the architecture survives contact with dynamic, multi-tool work. It did
not survive unchanged. Three components were missing and one contract was wrong.

| # | Finding | Resolution |
|---|---------|-----------|
| 1 | **The Controller had no middle loop.** It dispatched actions that named tools, which coupled the Decision Engine to implementations and turned one intent into five contract actions. | `runtime/capability_executor/` — the Controller's only execution verb is now `invoke_capability`. §5. |
| 2 | **Tool selection, chaining, retry and fallback had no owner.** They were spread between the execution engine and individual tools. | `runtime/capability_executor/` — intent resolution through a registry index, chaining, parallelism, fallback, caching. §7.21. |
| 3 | **The Controller tracked a plan but not its state.** Nothing answered *what can run now*, *what are we blocked on*, *how far along are we*. | `runtime/controller/execution_graph/` with a total node state machine. §7.22. |
| 4 | **`runtime/streaming/` streamed the wrong thing.** It streamed tokens and progress frames. | Replaced by `runtime/experience/`, which streams **execution state**. §11.3. |

#### The contract change this forced

**The Execution Contract named `tool_id`. That was wrong**, and correcting it is the most
consequential change in this revision. Actions become capability invocations carrying an *intent*;
the Capability Runtime resolves the intent to tools. §9.5.3.

This collides with invariant I9 — the one that cannot be retrofitted. If the registry resolves
`search_issues` to one tool today and a different one tomorrow, a naive identity over
`(session, contract, invocation, parameters)` treats them as the same and replays the wrong result.

The resolution is stated in §9.5.3 and is worth reading before implementing anything: **bind at plan
time, hash the binding into the identity, and let execution-time re-resolution mint a new identity
rather than substitute silently.** Both properties survive — the Decision Engine stays
implementation-agnostic and replay stays sound.

#### Two external standards adopted at the edges

Checked against current practice rather than invented:

- **OpenTelemetry GenAI semantic conventions** for telemetry. The span shape — an agent span with
  child model-call and tool-execution spans — maps onto the three loops directly, and the
  conventions' rule that *content belongs in span events rather than span attributes* is the same
  conclusion §11 reaches from the diagnostics side.
- **AG-UI** as the Experience layer's wire format. Adopted as an **encoder at the boundary, not an
  internal vocabulary**, so the kernel's dependency graph stays free of a third-party protocol
  version.

§9.7 covers both, including what is deliberately *not* adopted: token-level streaming as a progress
indicator.

---

### 1.6 Three gaps the earlier review did not name

| # | Gap | Why it matters |
|---|-----|---------------|
| A | **The Execution Contract had no field specification.** | This is the largest omission in the previous revision and it is bigger than any of the seven raised. The Execution Contract is the centrepiece of the entire architecture — the artifact that makes the router's decision auditable — and it existed only as a filename. Specified in §9.5. |
| B | **No runtime-to-package compatibility policy.** | `package_compatibility.py` existed with no stated rule. What happens when runtime v2 loads a package built against v1? §9.2.3 defines the policy and `runtime/manifest/compatibility_gate.py` refuses to boot on an incompatible set, rather than failing later in a way that looks like a model regression. |
| C | **Diagnostics must reconstruct, never store.** | Not a missing folder — a design constraint that would have been violated by the obvious implementation. Assembled prompts are *derived* state; a prompt viewer that persists them recreates the anti-pattern that breaks replay, and doubles the surface holding customer data. §10.3 states the rule. |

---

## 2. Scope

**This document defines:** the repository structure, the responsibility and boundaries of every
component, the five contracts that cross those boundaries, the invariants an implementation must
hold, the distributed execution model, and the order in which to build it.

**This document does not define:** algorithms inside a component, prompt content, model selection
policy, UI design, or business logic. Those live in code, in packages, and in ADRs.

**The test for whether something belongs here.** If changing it would break another team's
component, it belongs in this document. If changing it would only make one component better or
worse at its job, it does not.

**Status of the numbers and thresholds** that appear below — concurrency ranges, timeouts, budget
defaults — is `IMPLEMENTATION NOTE` in every case. They are starting points chosen to be
approximately right, and they are expected to move once the runtime is exercised with a real
package. The *shapes* around them are `NORMATIVE`.

---

## 3. Design rules the tree obeys

Ten rules. Every directory in §5 can be justified by one of them; if it cannot, it should not exist.

| # | Rule | Consequence in the tree |
|---|------|------------------------|
| 1 | **Contracts are the single source of truth.** | `contracts/` imports *nothing* from the repository. Everything else imports it. |
| 2 | **Dependencies point inward and never cycle.** | Enforced by `.importlinter` in CI, not by review. |
| 3 | **Ports are protocols; adapters are implementations.** | `runtime/ports/` holds `Protocol` definitions only. Providers live in `models/`, `tools/`, `storage/`. |
| 4 | **The kernel is domain-agnostic.** | `runtime/` may not import `packages/`, `capabilities/` or `tools/` — only their registries via ports. |
| 5 | **One file, one responsibility, named for it.** | No `utils.py`, no `helpers.py`, no `common/`. `execution_contract_parser.py`, not `parser.py`. |
| 6 | **Control plane and data plane are separate trees.** | `runtime/controller/` and `runtime/execution/` share no module. |
| 7 | **Non-determinism is quarantined.** | Clock, randomness and network live behind ports so tests can replace them. |
| 8 | **Every subsystem ships its own errors and types.** | `errors.py` per package; no global exception module. |
| 9 | **Tests mirror the source tree exactly.** | `tests/unit/runtime/controller/` mirrors `runtime/controller/`. |
| 10 | **Identity is separate from configuration.** | `runtime.manifest.yaml` says what this deployment *is*; `configs/` says how it is *tuned*. Changing a tunable must not change the manifest fingerprint. |
| 11 | **Each loop speaks only to its neighbours.** | The Controller speaks capabilities, the Capability Runtime speaks intents, the Tool Orchestrator speaks tool calls. No layer reaches two levels down. |
| 12 | **Only renderers write to a surface.** | Every other component emits an event. `gateway/renderers/` is the only code permitted to produce characters. |
| 13 | **One execution model.** | The ExecutionGraph is the plan, the state, the progress, the dependencies and the checkpoint. Nothing else may represent "what we are doing". |
| 14 | **No reasoning below the Decision Engine.** | Everything after it — binding, policy, reconciliation, capability execution — is deterministic. Exactly one box in the runtime is non-deterministic. |

### 3.1 Normative versus implementation

Every statement in this document is one of two kinds, and they are labelled wherever the distinction
could be missed.

> **NORMATIVE** — a requirement. Changing it changes the architecture, needs an ADR, and is checked
> by a test in §8.
>
> **IMPLEMENTATION NOTE** — how it is done today. Free to change without ceremony.

Concurrency numbers, timeouts, backoff curves, provider choices and file-level decomposition are all
implementation notes. Contracts, invariants, dependency direction and the plane separation are
normative. When in doubt: if changing it would break another team's component, it is normative.

---

## 4. Additions made during review

The submitted scaffold was expanded, never redesigned. Eight directories were **added** across two
review rounds, each because a named principle cannot hold without it. They are flagged `[+]` in the
tree.

### 4.1 Round one — the durability primitives

| Added | Why it is not optional |
|-------|------------------------|
| `runtime/identity/` | Principles 16 and 17 — *every execution is replayable*, *every session is checkpointable* — require an answer to **"has this action already run, and what did it cost?"** Without a content-addressed identity, a retry re-executes and re-spends, and a re-planned iteration silently inherits stale results. This is the only item that cannot be retrofitted: without it every stored result is of unknown reusability and the migration becomes a rewrite. |
| `runtime/leasing/` | *Exactly one controller advances a session at any instant.* A lease claimed in the same statement as a version compare-and-swap gives that guarantee and makes a killed worker recoverable by expiry rather than by a boot-time scan. |
| `runtime/parking/` | `HUMAN_LOOP` as an execution strategy risks holding a worker for hours. A park writes the question, releases every resource, and becomes a row. Approvals, missing input, timers, callbacks and budget grants are one mechanism with five resolution conditions. |
| `runtime/budget/` | The Policy Engine performs a budget *check*. A check permits a session to exceed its ceiling by the cost of everything already in flight. Reservation debits projected cost at dispatch and settles the actual on completion. Distinct from `runtime/resources/`, which bounds concurrency, not money. |

### 4.2 Round two — identity, scale and introspection

| Added | Why it is not optional |
|-------|------------------------|
| `runtime/manifest/` | A deployment with no stated identity cannot be compared with another, which makes every benchmark result and every evolution verdict uninterpretable. §7.1. |
| `runtime/distribution/` | Reserves the seam for partitioned execution without implementing it now, and — as importantly — records **why leader election is absent**, so the omission reads as a decision rather than an oversight. §10. |
| `diagnostics/` | Telemetry answers *is the fleet healthy*. Nothing answered *why did this session do that*. Six surfaces, access-controlled separately, reconstructing rather than storing. §10. |
| `tests/conformance/` | Once third parties author packages, "it loaded" is not the bar. A package must prove manifest completeness, descriptor validity, effect tagging, declared compatibility, and the absence of tenant data. |

### 4.3 Round three — the execution model

| Added | Why it is not optional |
|-------|------------------------|
| `runtime/capability_executor/` | Without a middle loop the Decision Engine must name concrete tools, coupling reasoning to implementation. §5.1. |
| `runtime/capability_executor/` | Intent resolution, chaining, retry, fallback and caching had no owner. It is also where the plan-time binding is pinned into the identity. |
| `runtime/controller/execution_graph/` | A plan is declarative; the graph is its runtime state. Pause, resume and *what are we blocked on* all need it. |
| `runtime/experience/` | Replaces `runtime/streaming/`. Streams execution state rather than tokens, presentation-neutral, deriving from durable events only. |
| `gateway/renderers/` | The only code permitted to write characters, so the kernel stays UI-independent while driving a rich UI. |
| `contracts/intent/`, `contracts/graph/`, `contracts/trace/`, `contracts/experience/` | New boundary types for the above. |

### 4.4 Round four — collapse and consolidation

Revision 4 **removed** a layer rather than adding one.

| Change | Effect |
|--------|--------|
| `capability_runtime/` + `tool_orchestration/` → `capability_executor/` | one package instead of two; no orchestration decision left to make once recipes are declared |
| `runtime/intelligence/router/` → `runtime/intelligence/decision/` | resolves a four-way name collision on "router" |
| `runtime/intelligence/binding/` **added** | deterministic intent→tool resolution, after the Decision Engine and before the Policy Gate |
| `runtime/controller/execution_graph/` **expanded** | from a progress tracker to the single execution model |
| `runtime/context/sources/execution_graph_source.py` **added** | the graph becomes an input to cognition |

Net change: **minus one package, plus two small ones, one renamed.**

### 4.5 The reframing that holds it together

**`packages/` is the harness.** Prompt modules, capabilities, policies, skills, memory configuration
and workflow definitions are exactly the editable component set that harness-evolution operates on.
Therefore `evolution/` writes to `packages/registry/` and to nothing else, which is what makes
*"the runtime never modifies itself"* an enforceable boundary rather than an aspiration — and what
makes the evolvable surface and the replaceable surface the same surface.

---

## 5. The execution model: three loops, one graph

This is the organising mental model for the whole runtime. It was implicit in earlier revisions and
is now explicit, because it resolves an ambiguity that mattered: **what, exactly, does the Controller
execute?**

The answer is that it does not execute tools. It executes *capabilities*.

```
                                                            CONTROL VIEW

  ┌──────────────────────────────────────────────────────────────────────┐
  │ OUTER LOOP · CONTROLLER                          runtime/controller/ │
  │                                                                      │
  │   owns   goal lifecycle · execution graph · progress · scheduling    │
  │          checkpoints · recovery · cancellation · exit conditions     │
  │   speaks capabilities and intents — never tool names                 │
  │   tempo  one iteration per Router pass                               │
  │                                                                      │
  │   ┌──────────────────────────────────────────────────────────────┐   │
  │   │ MIDDLE · CAPABILITY EXECUTOR   runtime/capability_executor/  │   │
  │   │                                                              │   │
  │   │   owns  one capability invocation, end to end                │   │
  │   │         capability-local context · a DECLARED recipe         │   │
  │   │         declared parallel steps · observation aggregation    │   │
  │   │   plans NOTHING — the chain is authored in the package [I30] │   │
  │   │   returns  one structured observation                        │   │
  │   │   tempo    seconds to minutes                                │   │
  │   │                                                              │   │
  │   │   ┌──────────────────────────────────────────────────────┐   │   │
  │   │   │ INNER · TOOLS                            tools/       │   │   │
  │   │   │   owns  side effects · external systems               │   │   │
  │   │   │         raw observations                              │   │   │
  │   │   │   speaks concrete calls against a PINNED binding      │   │   │
  │   │   │   tempo  milliseconds to seconds                      │   │   │
  │   │   └──────────────────────────────────────────────────────┘   │   │
  │   └──────────────────────────────────────────────────────────────┘   │
  └──────────────────────────────────────────────────────────────────────┘

  Intent → tool binding happens ABOVE all three, deterministically, in
  runtime/intelligence/binding/ — after the Decision Engine, before the
  Policy Gate. Nothing below the Decision Engine resolves or reasons. [I30]
```

### 5.1 Why the middle loop has to exist

Consider a request that says *"switch to dev, pull, show me the last ten commits, then check my
Jira access."*

Without a middle loop the Decision Engine must decide, in one inference, that this means
`git checkout` → `git pull` → `git log -10` → `jira.search` → `jira.permissions`. It is now naming
concrete tools, which produces three problems:

| Problem | Consequence |
|---------|-------------|
| The Decision Engine is coupled to implementations | Replacing the shell Git tool with a library or an API becomes a Router change |
| Multi-tool operations leak into the contract | Five actions where there is one intent, and the contract stops reading like a decision |
| Failure handling has nowhere to live | A retry of `git pull` is a *capability-internal* concern, but the Controller now owns it |

With a middle loop the Decision Engine emits two capability invocations — *inspect a Git repository* and
*check Jira access* — and each expands internally into its own tool chain. Swapping the Git
implementation changes one capability and nothing else.

**NORMATIVE.** The Controller's execution verb is `invoke_capability`. There is no
`invoke_tool` on the Controller.

### 5.2 What each loop returns to the one above it

| Loop | Returns | Granularity |
|------|---------|-------------|
| Tools → Capability Executor | Raw tool results, including partial failures | one call |
| Capability Executor → Controller | **One structured observation** | one capability |
| Controller → Router | Verified observation plus graph state | one iteration |

The aggregation at the middle boundary is the point. A capability that made five tool calls returns
one observation — *"repository updated to dev at commit 4f1c9, ten commits read"* — not five raw
payloads. That is what keeps the Decision Engine's context from filling with transport detail, and it is why
`observation_aggregator.py` and `partial_result_reconciler.py` are in the capability runtime rather
than in the controller.

### 5.3 Capability Context

Each capability needs a different slice of the world. A research capability needs sources, search
and citation rules; a Git capability needs a repository, a branch, a remote and credentials.
Assembling all of that globally would put every capability's needs into every prompt.

```
   Global ContextBundle                (runtime/context/)
            │
            │  capability_context_builder.py
            ▼
   Capability Context                  (runtime/capability_executor/)
     · the slice this capability declared it needs
     · plus capability-local scratch that dies with the invocation
```

**NORMATIVE.** A capability may read only the context slices its descriptor declares. Capability
context is discarded when the invocation ends; nothing in it survives to the next iteration except
through the returned observation.

---

## 6. ExecutionGraph — the single runtime execution model

**NORMATIVE.** There is one execution model in this runtime and it is the ExecutionGraph. It is
simultaneously the plan, the runtime state, the progress tracker, the dependency tracker and the
checkpoint. There is no second representation of "what we are doing" anywhere in the system.

### 6.1 Why this is not a DAG engine

A reasonable objection: a graph with dependencies *is* a DAG, so has a workflow engine been smuggled
in? No, and the distinction is the one Kubernetes draws.

| | A workflow engine | This runtime |
|---|------------------|--------------|
| The graph is | a program submitted to an engine | **a data structure with `spec` and `status`** |
| The engine | schedules, owns workers, has its own lifecycle | **there is no engine** |
| The Controller | submits work and waits | **reconciles: reads state, computes the ready set, dispatches, updates** |
| Triggering | edge-triggered off task events | **level-triggered off actual state** |
| Failure | engine state and app state can diverge | one artifact, one truth |

The Controller is a **reconciler**, not a scheduler. Every pass reads the graph as it actually is
and moves it toward completion — it does not react to individual events. This matters more than it
sounds: level-triggered reconciliation is idempotent, so a duplicated wake, a lost event, or a crash
mid-pass all produce the same result as a clean pass. Edge-triggered orchestration has to be made
correct; level-triggered reconciliation is correct by construction.

That single property is why no separate engine is needed, and why the graph can absorb the plan,
the progress tracker and the checkpoint without becoming a subsystem.

**IMPLEMENTATION NOTE.** The reconcile pass is a pure function of the graph plus observations. It
takes no wall-clock decisions except through `clock_port`, so a replayed pass produces the same
result as the original.

### 6.2 The graph is an input to cognition, not only an output of it

`[+] r4 — the most consequential change in this revision.`

In earlier revisions the graph was built by the Controller *after* the Decision Engine ran. That is
backwards. The Decision Engine cannot answer *what should happen next* without knowing what has
already happened, what is in flight, what failed, and what remains.

**NORMATIVE.** A read-only projection of the ExecutionGraph is an explicit source in Parallel Context
Assembly (`runtime/context/sources/execution_graph_source.py`), assembled **before** the Decision
Engine runs.

```
   ┌──────────────────────────────────────────────────────────────┐
   │ PARALLEL CONTEXT ASSEMBLY                                    │
   │   session · memory · world · files · package · policies      │
   │   + EXECUTION GRAPH PROJECTION   (read-only)                 │
   │       "8 nodes. 1-4 COMPLETED. 5 RUNNING since 00:14.        │
   │        6 BLOCKED awaiting approval. 7-8 PENDING on 5.        │
   │        Budget spent 0.42 of 8.00."                           │
   └────────────────────────────┬─────────────────────────────────┘
                                ▼
                        DECISION ENGINE
```

Two things follow. The Decision Engine stops reconstructing history from a transcript, which is the
single largest avoidable consumer of context window in an agent loop. And its output becomes a
*delta* — nodes to add, a node to retry, a goal amendment — rather than a fresh plan each iteration.

**The projection is read-only.** The Decision Engine proposes graph mutations in its contract; it
never writes to the graph. The Controller applies them after the Policy Gate.

### 6.3 Node states

```
                                                             STATE VIEW

     ┌─────────┐
     │ PENDING │  dependencies unmet, or condition not yet evaluated
     └────┬────┘
          │ deps COMPLETED and condition true
          ▼
     ┌─────────┐        condition false
     │  READY  │ ──────────────────────────────► ┌─────────┐
     └────┬────┘                                 │ SKIPPED │
          │ Controller dispatches                └─────────┘
          ▼
     ┌─────────┐
     │ RUNNING │
     └────┬────┘
          │
          ├── observation received, checks pass ──► ┌───────────┐
          │                                         │ COMPLETED │
          │                                         └───────────┘
          │
          ├── needs a human, a timer, or budget ──► ┌─────────┐
          │                                         │ WAITING │──┐
          │                                         └─────────┘  │
          │                            resolution event ─────────┘
          │                                    (back to READY)
          │
          ├── failed, attempts remain ──────────► back to READY
          │
          ├── failed, attempts exhausted ───────► ┌────────┐
          │                                       │ FAILED │
          │                                       └────┬───┘
          │                                            │ a dependant cannot run
          └── dependency FAILED ────────────────► ┌─────────┐
                                                  │ BLOCKED │
                                                  └─────────┘
```

| State | Meaning | Who moves it |
|-------|---------|-------------|
| `PENDING` | Dependencies unmet | Controller |
| `READY` | Dependencies met, condition true, dispatchable **now** | Controller |
| `RUNNING` | Dispatched to the Capability Executor; lease held | Controller |
| `WAITING` | Durably parked — approval, input, timer, budget grant. Holds nothing. | Controller, on a resolution event |
| `BLOCKED` | Cannot proceed; a dependency failed or a policy refused. Carries a reason. | Controller |
| `COMPLETED` | Observation received and verified | Controller |
| `FAILED` | Attempts exhausted | Controller |
| `SKIPPED` | Condition evaluated false | Controller |

**NORMATIVE.** The state machine is *total* and *legal-only*: every node reaches a terminal state
(`COMPLETED`, `FAILED`, `SKIPPED`) or sits in `WAITING` or `BLOCKED` with a recorded reason. There is
no state in which a node is neither progressing nor explaining itself. `BLOCKED` without a reason is
a validation failure.

### 6.4 The reconcile loop, and parallel execution

The Controller's pass is four steps. It is the same four steps whether the work is linear, parallel
or conditional — that is the point.

```python
# runtime/controller/deterministic_runtime_loop.py   — conceptual
while not graph.is_terminal():
    ready = graph.ready_nodes()        # deps COMPLETED  AND  condition true
                                       #   AND attempts remain  AND not parked
    if not ready:
        break                          # park, or ask the Decision Engine for a delta
    dispatch(ready)                    # ALL of them — see below
    observations = collect()           # each returns one structured observation
    graph.apply(observations)          # states, retries, timers, insertions
    checkpoint(graph)                  # the graph IS the checkpoint
```

**Parallel execution is not a feature. It is the absence of a restriction.**

`ready_nodes()` returns every node whose dependencies are satisfied. If three search nodes declare no
dependencies on each other, all three are READY on the same pass and all three are dispatched.

```
  Goal: survey the topic
  ├─ search_github    deps: []      ─┐
  ├─ search_reddit    deps: []       ├─ all READY on pass 1 → dispatched together
  ├─ search_docs      deps: []      ─┘
  └─ synthesise       deps: [search_github, search_reddit, search_docs]
                                       PENDING until all three COMPLETED
```

No scheduler, no fan-out primitive, no join node. The join is `depends_on`. `parallel_group` on a
node is an *optional* hint used for budget accounting and progress display; it does not create
concurrency, and removing it changes nothing about what runs.

**NORMATIVE.** Concurrency is bounded by `runtime/resources/`, not by the graph. A ready set of forty
nodes dispatches under the same model semaphore and per-tenant admission as a ready set of one.

### 6.5 Conditional execution

A node may carry a condition. If it evaluates false, the node becomes `SKIPPED` and its dependants
are re-evaluated.

```yaml
- id: check_write_permission
  type: CAPABILITY
  capability: jira.permission_check
  depends_on: [check_jira_access]
  condition:
    expression: "nodes.check_jira_access.observation.access_granted == true"
    on_false: SKIP          # SKIP | BLOCK | FAIL
```

**NORMATIVE.** Conditions are evaluated by `condition_evaluator.py` — deterministically, in the
Controller, **never by a model**. The expression language reads only committed node observations and
graph state. It has no I/O, no clock beyond `clock_port`, and no model access.

This is not a style preference. A condition evaluated by a model is non-determinism outside the
quarantine (I8): the same graph would replay differently, and every guarantee that depends on replay
would quietly stop holding. If a decision genuinely requires judgement, it is not a condition — it is
the next iteration's work for the Decision Engine.

`on_false` has three values because skipping is not always right: `SKIP` continues, `BLOCK` stops
the branch with a reason, `FAIL` treats the false condition as an error.

### 6.6 Retry and timeout

Both are node metadata. Both are owned by the Controller.

```yaml
retry_policy:
  max_attempts: 3
  backoff: exponential          # none | fixed | exponential
  initial_delay_ms: 500
  retry_on: [transient, timeout, rate_limited]
  never_retry_on: [policy_denied, non_idempotent_effect]

timeout:
  node_ms: 120000
  on_timeout: RETRY             # RETRY | FAIL | ESCALATE
```

**NORMATIVE.**

- **The Controller owns retry. The Decision Engine never retries.** A retry is a deterministic state
  transition — `RUNNING → READY`, attempts incremented — not a decision. Letting the model decide to
  retry spends an inference on something arithmetic, and makes the retry count unauditable.
- **A retry re-dispatches the same node with the same identity.** The identity already includes the
  pinned binding, so a retry cannot silently execute a different tool.
- **`never_retry_on` includes non-idempotent effects by default.** A tool declaring
  `idempotency.class: NON_IDEMPOTENT` (§9.4.1) is never retried automatically, regardless of the
  node's policy. The node policy may narrow this; it may not widen it.
- **A timeout aborts the real call** and then applies `on_timeout`. The abort signal reaches the
  provider client (I11); it is not an abandoned wait.

### 6.7 Checkpoint

**NORMATIVE.** The checkpoint is the serialized ExecutionGraph. There is nothing else to save.

| | |
|---|---|
| **Owner** | ExecutionGraph. Not tools, not capabilities, not the executor. |
| **Written by** | `graph_serializer.py`, at every reconcile pass |
| **Contains** | every node, its state, attempts, observations, artifacts, timers, generation |
| **Excludes** | in-flight tool buffers, assembled context, anything derived |
| **Recovery** | deserialize the graph, recompute the ready set, continue |

Because the graph carries node state and the identity ledger carries what already ran, recovery
needs no replay of side effects: a node that was `RUNNING` when the worker died returns to `READY`,
is re-dispatched, and its completed actions replay from the ledger rather than re-executing.

**A tool that checkpoints its own progress is a defect.** It creates a second recovery path that can
disagree with the graph, and the disagreement surfaces only during an incident.

### 6.8 Human approval

An approval is a node type, not a special case in the controller.

```yaml
- id: approve_push
  type: APPROVAL
  depends_on: [run_tests]
  approval_policy:
    question_template: templates/push_branch_approval.md
    approver_role: repository_maintainer
    on_timeout_hours: 48
    on_expiry: ESCALATE          # ESCALATE | FAIL | SKIP
```

The sequence:

```
  run_tests           COMPLETED
        ↓
  approve_push        READY → RUNNING → writes the question → WAITING
        ↓                                    │
  graph state         PARKED                 │  holds no worker, no lease,
        ↓                                    │  no connection, no timer
        ↓             ... hours or days ...  │
        ↓                                    ▼
  approval.decided event arrives  →  node → COMPLETED (or FAILED on refusal)
        ↓
  Controller reconciles, push_branch becomes READY
```

**NORMATIVE.** A graph is `PARKED` when every non-terminal node is `WAITING`. A parked graph holds
one row and nothing else, and survives restarts and redeploys indefinitely. Any node whose capability
invokes an `EFFECTFUL` tool must have a resolved approval node among its dependencies — enforced by
`approval_gate_evaluator.py` and by I14, in the code path, never by prompting.

### 6.9 Dynamic node insertion

Graphs are not fixed at plan time. When the Decision Engine learns something new, it proposes nodes.

```
  iteration 3: the Decision Engine observes that the monorepo has a second
  package requiring the same fix, and proposes:

    + node  patch_package_b   depends_on: [survey_repo]
    + edge  patch_package_b → run_tests
```

**NORMATIVE.**

1. **The Decision Engine proposes; the Controller inserts.** Proposals arrive as
   `graph_mutations` in the Execution Contract and are applied by `graph_mutator.py`.
2. **Insertion passes the Policy Gate** like any other proposed work. A node cannot be smuggled in
   to bypass authorisation.
3. **Insertion may not mutate a terminal node.** Completed history is immutable; a node that needs
   redoing is a *new* node with a dependency on the old one.
4. **Insertion must not create a cycle.** `graph_invariant_checker.py` rejects the mutation.
5. **An insertion increments the graph generation** and is recorded as a `graph.mutated` event with
   the proposing contract id, so the trace explains why the graph grew.

A wholesale replan mints a new **generation** rather than editing in place: new nodes, new
identities, the old generation retained as history. This is what preserves I9 — no node in
generation 2 can inherit a stale result from generation 1.

### 6.10 Walkthrough: the graph after each pass

*"Switch to dev, pull latest, read the last ten commits, then check my Jira access and whether I can
write. Don't modify any code."*

**Pass 1 — the Decision Engine sees an empty graph and proposes four nodes.**

```
  n1 git.repository_inspection   deps []             READY
  n2 jira.access_check           deps []             READY
  n3 jira.permission_check       deps [n2]           PENDING
       condition  nodes.n2.observation.access_granted == true
  n4 respond                     deps [n1, n3]       PENDING
```

`ready_nodes()` → `[n1, n2]`. Both dispatched **together** — they have no dependency on each other.
The constraint "don't modify code" became a policy constraint on the contract, not a node.

**Pass 2 — both observations return.**

```
  n1 COMPLETED   on dev at 4f1c9e2; 10 commits read        2.14 s
       tools  git checkout dev ✓ · git pull ✓ · git log -10 ✓
  n2 COMPLETED   access granted; project ACME visible        810 ms
       tools  jira.search ✓ · jira.myself ✓
  n3 condition evaluates TRUE  →  PENDING → READY
  n4 PENDING
```

`ready_nodes()` → `[n3]`. Dispatched.

**Pass 3 — the graph nears completion.**

```
  n1 COMPLETED
  n2 COMPLETED
  n3 COMPLETED   write permission confirmed on ACME          420 ms
  n4 READY
```

`ready_nodes()` → `[n4]`. The Decision Engine is invoked once more with a graph projection showing
three completed nodes and their observations — it does not re-read the transcript — and produces the
final response.

**The counterfactual, which is where the design earns its keep.** Had `n2` returned
`access_granted: false`, `n3`'s condition would evaluate false and `n3` would become `SKIPPED`
without a model call. `n4` would become READY with three of four dependencies terminal, and the
response would correctly report no Jira access. **No inference was spent deciding to skip.** That is
the difference between a graph the Controller reconciles and a loop that asks a model what to do
next.

---

## 7. The complete repository tree

```
universal-runtime/
│
├── README.md
├── ARCHITECTURE.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── ROADMAP.md
├── CHANGELOG.md
├── GOVERNANCE.md
├── MAINTAINERS.md
│
├── runtime.manifest.yaml                # the runtime's IDENTITY — see §9.1
├── pyproject.toml
├── Makefile
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── .editorconfig
├── .pre-commit-config.yaml
├── .importlinter                        # dependency direction, enforced in CI
├── ruff.toml
├── mypy.ini
├── pytest.ini
├── codecov.yml
│
├── .github/
│   ├── CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   ├── architecture_decision.yml
│   │   └── incident_report.yml
│   └── workflows/
│       ├── lint.yml
│       ├── typecheck.yml
│       ├── unit_tests.yml
│       ├── integration_tests.yml
│       ├── contract_tests.yml
│       ├── dependency_boundaries.yml
│       ├── golden_set_replay.yml
│       ├── benchmark_regression.yml
│       ├── harness_tenancy_scan.yml
│       ├── security_scan.yml
│       ├── docker_build.yml
│       └── release.yml
│
├──────────────────────────────────────────────────────────────────────────────
│ DOCUMENTATION
├──────────────────────────────────────────────────────────────────────────────
│
├── docs/
│   ├── index.md
│   ├── glossary.md
│   ├── diagram_conventions.md
│   ├── naming_conventions.md
│   │
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── runtime.md
│   │   ├── control-plane.md
│   │   ├── data-plane.md
│   │   ├── package-system.md
│   │   ├── intelligence.md
│   │   ├── execution.md
│   │   ├── learning.md
│   │   ├── knowledge.md
│   │   ├── evolution.md
│   │   ├── storage.md
│   │   ├── security.md
│   │   ├── deployment.md
│   │   ├── invariants.md                    # §9  the enforceable list
│   │   ├── three-nested-loops.md            # §5
│   │   ├── capability-runtime.md
│   │   ├── execution-graph.md
│   │   ├── experience-layer.md              # §11.3
│   │   ├── distributed-runtime.md           # §11
│   │   ├── diagnostics.md                   # §11
│   │   ├── failure-modes.md
│   │   ├── state-separation.md
│   │   └── dependency-graph.md
│   │
│   ├── contracts/
│   │   ├── runtime-manifest.md              # §9.1  normative
│   │   ├── package-manifest.md              # §9.2  normative
│   │   ├── capability-descriptor.md         # §9.3  normative
│   │   ├── tool-descriptor.md               # §9.4  normative
│   │   ├── execution-contract.md            # §9.5  normative
│   │   ├── execution-trace.md               # §9.6  normative
│   │   ├── runtime-event-taxonomy.md        # §9.7  normative
│   │   ├── intent-descriptor.md
│   │   ├── action-identity.md
│   │   ├── event-envelope.md
│   │   ├── workflow-definition.md
│   │   ├── versioning-policy.md
│   │   └── compatibility-matrix.md          # runtime version x package version
│   │
│   ├── protocols/
│   │   ├── model-provider-protocol.md
│   │   ├── tool-protocol.md
│   │   ├── capability-protocol.md
│   │   ├── storage-protocol.md
│   │   ├── plugin-protocol.md
│   │   ├── streaming-protocol.md
│   │   └── mcp-bridge-protocol.md
│   │
│   ├── api/
│   │   ├── http-reference.md
│   │   ├── websocket-reference.md
│   │   ├── cli-reference.md
│   │   ├── python-sdk-reference.md
│   │   └── openapi.yaml
│   │
│   ├── tutorials/
│   │   ├── 01-first-session.md
│   │   ├── 02-writing-a-tool.md
│   │   ├── 03-writing-a-capability.md
│   │   ├── 04-authoring-a-package.md
│   │   ├── 05-defining-a-workflow.md
│   │   ├── 06-adding-a-model-provider.md
│   │   ├── 07-writing-a-plugin.md
│   │   ├── 08-running-a-benchmark.md
│   │   └── 09-running-an-evolution-round.md
│   │
│   ├── operations/
│   │   ├── deployment-topologies.md
│   │   ├── scaling-guide.md
│   │   ├── capacity-planning.md
│   │   ├── observability-signals.md
│   │   ├── cost-management.md
│   │   ├── incident-playbooks.md
│   │   └── upgrade-and-rollback.md
│   │
│   ├── examples/
│   │   ├── research_session/
│   │   ├── coding_session/
│   │   ├── long_running_session/
│   │   └── human_in_loop_session/
│   │
│   └── adr/
│       ├── 0000-adr-template.md
│       ├── 0001-event-sourced-runtime-state.md
│       ├── 0002-single-pass-router.md
│       ├── 0003-control-data-plane-separation.md
│       ├── 0004-parallel-context-assembly.md
│       ├── 0005-content-addressed-action-identity.md
│       ├── 0006-lease-and-version-cas.md
│       ├── 0007-durable-parks-over-blocking-waits.md
│       ├── 0008-budget-reservation-over-checks.md
│       ├── 0009-packages-as-the-harness.md
│       ├── 0010-effect-tagging-of-tools.md
│       ├── 0011-progress-excluded-from-event-log.md
│       ├── 0012-capability-tool-separation.md
│       └── 0013-evolution-external-to-execution.md
│
├──────────────────────────────────────────────────────────────────────────────
│ GLOBAL CONFIGURATION
├──────────────────────────────────────────────────────────────────────────────
│
├── configs/
│   ├── runtime.yaml
│   ├── models.yaml
│   ├── packages.yaml
│   ├── capabilities.yaml
│   ├── tools.yaml
│   ├── storage.yaml
│   ├── logging.yaml
│   ├── telemetry.yaml
│   ├── security.yaml
│   ├── plugins.yaml
│   ├── budgets.yaml
│   ├── policies.yaml
│   ├── evolution.yaml
│   │
│   ├── manifests/                           # per-environment overlays of the root manifest
│   │   ├── local.manifest.yaml
│   │   ├── staging.manifest.yaml
│   │   └── production.manifest.yaml
│   │
│   ├── environments/
│   │   ├── local.yaml
│   │   ├── test.yaml
│   │   ├── staging.yaml
│   │   └── production.yaml
│   │
│   └── schemas/
│       ├── runtime_manifest_schema.json
│       ├── runtime_config_schema.json
│       ├── models_config_schema.json
│       ├── package_manifest_schema.json
│       ├── capability_descriptor_schema.json
│       ├── tool_descriptor_schema.json
│       ├── workflow_definition_schema.json
│       ├── policy_document_schema.json
│       ├── plugin_manifest_schema.json
│       └── evolution_manifest_schema.json
│
├──────────────────────────────────────────────────────────────────────────────
│ SHARED CONTRACTS — single source of truth, imports nothing
├──────────────────────────────────────────────────────────────────────────────
│
├── contracts/
│   ├── __init__.py
│   ├── version.py
│   │
│   ├── base/
│   │   ├── __init__.py
│   │   ├── identifiers.py                # SessionId, RunId, ContractId, ActionId, PlanId
│   │   ├── content_digest.py             # canonical hashing of arbitrary payloads
│   │   ├── monotonic_sequence.py
│   │   ├── timestamps.py
│   │   ├── semantic_version.py
│   │   ├── tenant.py
│   │   ├── actor.py                      # human, schedule, webhook, agent
│   │   ├── result_envelope.py
│   │   ├── error_code.py
│   │   └── redaction_marker.py
│   │
│   ├── session/
│   │   ├── __init__.py
│   │   ├── session_descriptor.py
│   │   ├── session_state_enum.py
│   │   ├── conversation_turn.py
│   │   ├── attachment_reference.py
│   │   └── session_checkpoint.py
│   │
│   ├── goal/
│   │   ├── __init__.py
│   │   ├── goal_statement.py
│   │   ├── goal_amendment.py             # a steer, not a mutation
│   │   ├── acceptance_criterion.py
│   │   └── clarification_request.py
│   │
│   ├── context/
│   │   ├── __init__.py
│   │   ├── context_bundle.py
│   │   ├── context_fragment.py
│   │   ├── context_source_enum.py
│   │   ├── token_budget.py
│   │   └── compaction_directive.py
│   │
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── execution_contract.py         # what the Decision Engine emits
│   │   ├── validated_execution_contract.py
│   │   ├── execution_strategy_enum.py    # DIRECT PLAN WORKFLOW PARALLEL BACKGROUND LONG_RUNNING HUMAN_LOOP
│   │   ├── confidence_score.py
│   │   ├── reasoning_summary.py
│   │   └── contract_metadata.py
│   │
│   ├── planning/
│   │   ├── __init__.py
│   │   ├── plan_descriptor.py
│   │   ├── plan_step.py
│   │   ├── plan_identity.py              # a replan mints a new identity
│   │   ├── task_graph_node.py
│   │   ├── task_graph_edge.py
│   │   └── replan_reason_enum.py
│   │
│   ├── intent/                           # [+] r3 — what the Decision Engine names
│   │   ├── __init__.py
│   │   ├── intent_descriptor.py          # "search_issues", not "jira.search"
│   │   ├── intent_taxonomy.py
│   │   ├── intent_parameter_schema.py
│   │   └── intent_resolution_record.py   # intent -> capability -> tools, pinned
│   │
│   ├── capability/
│   │   ├── __init__.py
│   │   ├── capability_descriptor.py      # WHAT can be accomplished
│   │   ├── capability_input_schema.py
│   │   ├── capability_output_schema.py
│   │   ├── capability_binding.py         # capability → one or more tools
│   │   └── capability_selection_result.py
│   │
│   ├── action/
│   │   ├── __init__.py
│   │   ├── action_descriptor.py
│   │   ├── action_identity.py            # hash(session, contract, action, tool, input_digest)
│   │   ├── action_state_enum.py
│   │   ├── action_attempt.py
│   │   ├── action_result.py
│   │   └── action_dispatch_request.py
│   │
│   ├── graph/                            # [~] r4 — THE execution model. §8.8
│   │   ├── __init__.py
│   │   ├── execution_graph.py            # spec + status, one artifact
│   │   ├── execution_node.py             # the full node spec  §9.8
│   │   ├── node_type_enum.py             # CAPABILITY · CONDITION · APPROVAL
│   │   │                                 # CHECKPOINT · PARALLEL_GROUP · TERMINAL
│   │   ├── node_state_enum.py            # PENDING READY RUNNING WAITING
│   │   │                                 # BLOCKED COMPLETED FAILED SKIPPED
│   │   ├── node_condition.py             # deterministic predicate
│   │   ├── node_retry_policy.py
│   │   ├── node_timeout_policy.py
│   │   ├── node_approval_policy.py
│   │   ├── parallel_group.py
│   │   ├── graph_edge.py
│   │   ├── graph_generation.py           # replan = new generation, not mutation
│   │   ├── graph_checkpoint.py
│   │   └── graph_progress_summary.py
│   │
│   ├── trace/                            # [+] r3 — the execution record
│   │   ├── __init__.py
│   │   ├── execution_trace.py
│   │   ├── trace_iteration.py
│   │   ├── trace_capability_span.py
│   │   ├── trace_tool_span.py
│   │   └── trace_observation_span.py
│   │
│   ├── experience/                       # [+] r3 — presentation-neutral events
│   │   ├── __init__.py
│   │   ├── runtime_event.py
│   │   ├── runtime_event_class.py        # PROGRESS | TRACE | PRESENTATION
│   │   ├── progress_node.py
│   │   ├── progress_tree_snapshot.py
│   │   └── stream_frame.py
│   │
│   ├── tool/
│   │   ├── __init__.py
│   │   ├── tool_descriptor.py            # HOW work is performed
│   │   ├── tool_effect_enum.py           # PURE | EFFECTFUL — the whole safety model
│   │   ├── tool_input_schema.py
│   │   ├── tool_output_envelope.py
│   │   ├── tool_error_classification.py
│   │   └── tool_invocation_record.py
│   │
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── workflow_definition.py
│   │   ├── workflow_node.py
│   │   ├── workflow_transition.py
│   │   ├── workflow_run_state.py
│   │   └── workflow_compensation.py
│   │
│   ├── observation/
│   │   ├── __init__.py
│   │   ├── raw_observation.py
│   │   ├── verified_observation.py
│   │   ├── verification_check.py
│   │   ├── verification_verdict.py
│   │   └── observation_source_enum.py
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── evaluation_rubric.py
│   │   ├── deterministic_check.py
│   │   ├── model_judgment.py             # may downgrade, never upgrade
│   │   ├── evaluation_verdict.py
│   │   └── evaluation_decision_enum.py   # ACCEPT RETRY REPLAN ESCALATE
│   │
│   ├── decision/
│   │   ├── __init__.py
│   │   ├── decision_record.py
│   │   ├── decision_rationale.py
│   │   └── decision_audit_entry.py
│   │
│   ├── policy/
│   │   ├── __init__.py
│   │   ├── policy_document.py
│   │   ├── permission_grant.py
│   │   ├── policy_violation.py
│   │   ├── approval_requirement.py
│   │   └── execution_constraint.py
│   │
│   ├── budget/
│   │   ├── __init__.py
│   │   ├── budget_ceiling.py
│   │   ├── budget_reservation.py
│   │   ├── budget_settlement.py
│   │   ├── cost_estimate.py
│   │   └── spend_record.py
│   │
│   ├── park/
│   │   ├── __init__.py
│   │   ├── park_descriptor.py
│   │   ├── park_reason_enum.py           # APPROVAL INPUT TIMER CALLBACK BUDGET_GRANT
│   │   ├── park_resolution.py
│   │   └── approval_question.py
│   │
│   ├── signal/
│   │   ├── __init__.py
│   │   ├── control_signal.py
│   │   ├── signal_kind_enum.py           # STEER CANCEL PAUSE ANSWER
│   │   └── signal_delivery_receipt.py
│   │
│   ├── event/
│   │   ├── __init__.py
│   │   ├── event_envelope.py
│   │   ├── event_type_registry.py
│   │   ├── event_partition_key.py
│   │   ├── event_claim.py
│   │   ├── projection_checkpoint.py
│   │   └── replay_cursor.py
│   │
│   ├── learning/
│   │   ├── __init__.py
│   │   ├── trajectory_record.py
│   │   ├── learning_candidate.py
│   │   ├── pattern_descriptor.py
│   │   ├── distilled_lesson.py
│   │   └── benchmark_result.py
│   │
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── entity_record.py
│   │   ├── fact_record.py
│   │   ├── relationship_record.py
│   │   ├── unknown_record.py
│   │   ├── assumption_record.py
│   │   ├── confidence_level.py
│   │   └── memory_record.py
│   │
│   ├── artifact/
│   │   ├── __init__.py
│   │   ├── artifact_descriptor.py
│   │   ├── artifact_format_enum.py
│   │   ├── artifact_version.py
│   │   └── artifact_lineage.py
│   │
│   ├── package/
│   │   ├── __init__.py
│   │   ├── package_manifest.py
│   │   ├── package_identity.py
│   │   ├── package_dependency.py
│   │   ├── package_component_kind.py     # PROMPT CAPABILITY POLICY TEMPLATE KNOWLEDGE SKILL MEMORY_CONFIG EVAL_RULE WORKFLOW
│   │   └── package_compatibility.py      # pinned against a model identity
│   │
│   ├── evolution/
│   │   ├── __init__.py
│   │   ├── change_manifest.py
│   │   ├── change_entry.py               # evidence · root cause · fix · predicted fixes · risk set
│   │   ├── attribution_verdict.py        # KEEP IMPROVE ROLLBACK_AND_PIVOT
│   │   ├── experiment_descriptor.py
│   │   └── candidate_package_version.py
│   │
│   ├── telemetry/
│   │   ├── __init__.py
│   │   ├── metric_descriptor.py
│   │   ├── span_descriptor.py
│   │   └── progress_frame.py             # never durable
│   │
│   ├── errors/
│   │   ├── __init__.py
│   │   ├── contract_violation_error.py
│   │   ├── schema_mismatch_error.py
│   │   └── version_incompatibility_error.py
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── json_schema_exporter.py
│       ├── schema_registry.py
│       └── generated/
│           ├── execution_contract.schema.json
│           ├── action_identity.schema.json
│           ├── event_envelope.schema.json
│           ├── package_manifest.schema.json
│           ├── capability_descriptor.schema.json
│           ├── tool_descriptor.schema.json
│           ├── workflow_definition.schema.json
│           └── change_manifest.schema.json
│
├──────────────────────────────────────────────────────────────────────────────
│ GATEWAY — ingress. Stateless. No loop, no consumer, no model call.
├──────────────────────────────────────────────────────────────────────────────
│
├── gateway/
│   ├── __init__.py
│   ├── application_factory.py
│   ├── errors.py
│   │
│   ├── http/
│   │   ├── __init__.py
│   │   ├── asgi_app.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── session_routes.py
│   │   │   ├── message_routes.py
│   │   │   ├── signal_routes.py
│   │   │   ├── approval_routes.py
│   │   │   ├── artifact_routes.py
│   │   │   ├── package_routes.py
│   │   │   ├── health_routes.py
│   │   │   └── admin_routes.py
│   │   ├── request_models.py
│   │   ├── response_models.py
│   │   ├── read_model_projector.py       # shapes RunView; enforces tenancy + redaction
│   │   ├── idempotency_key_extractor.py
│   │   ├── error_translator.py
│   │   └── openapi_generator.py
│   │
│   ├── websocket/
│   │   ├── __init__.py
│   │   ├── connection_manager.py
│   │   ├── subscription_registry.py
│   │   ├── frame_encoder.py
│   │   ├── resume_cursor_handler.py      # hydrate-then-subscribe
│   │   ├── backpressure_controller.py
│   │   └── heartbeat_monitor.py
│   │
│   ├── renderers/                            # [+] r3 — the ONLY writers to a surface
│   │   ├── __init__.py
│   │   ├── terminal_progress_renderer.py     # the nested tree
│   │   ├── terminal_trace_renderer.py
│   │   ├── plain_log_renderer.py             # non-tty, CI
│   │   ├── json_stream_renderer.py
│   │   └── web_frame_renderer.py
│   │
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── entrypoint.py
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── session_commands.py
│   │   │   ├── package_commands.py
│   │   │   ├── capability_commands.py
│   │   │   ├── tool_commands.py
│   │   │   ├── benchmark_commands.py
│   │   │   ├── evolution_commands.py
│   │   │   ├── replay_commands.py
│   │   │   └── doctor_commands.py
│   │   ├── output_renderer.py
│   │   ├── progress_renderer.py
│   │   └── interactive_shell.py
│   │
│   ├── sdk/
│   │   ├── __init__.py
│   │   ├── python/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   ├── async_client.py
│   │   │   ├── session_handle.py
│   │   │   ├── stream_consumer.py
│   │   │   ├── hydrate_then_subscribe.py # a client cannot go live without hydrating
│   │   │   └── retry_policy.py
│   │   └── typescript/
│   │       ├── package.json
│   │       ├── src/
│   │       │   ├── client.ts
│   │       │   ├── sessionHandle.ts
│   │       │   ├── streamConsumer.ts
│   │       │   └── types.ts
│   │       └── README.md
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── api_key_authenticator.py
│   │   ├── oidc_authenticator.py
│   │   ├── service_account_authenticator.py
│   │   ├── tenant_resolver.py
│   │   └── principal_context.py
│   │
│   ├── uploads/
│   │   ├── __init__.py
│   │   ├── multipart_receiver.py
│   │   ├── attachment_validator.py
│   │   ├── virus_scan_gate.py
│   │   ├── blob_uploader.py
│   │   └── attachment_indexer.py
│   │
│   └── middleware/
│       ├── __init__.py
│       ├── request_id_middleware.py
│       ├── tenancy_middleware.py
│       ├── rate_limit_middleware.py
│       ├── admission_control_middleware.py   # per-tenant concurrent session cap
│       ├── payload_limit_middleware.py
│       ├── audit_log_middleware.py
│       └── error_boundary_middleware.py
│
├──────────────────────────────────────────────────────────────────────────────
│ RUNTIME KERNEL — domain-agnostic. Imports contracts and ports only.
├──────────────────────────────────────────────────────────────────────────────
│
├── runtime/
│   ├── __init__.py
│   │
│   ├── ports/                            # Protocol definitions. No implementations.
│   │   ├── __init__.py
│   │   ├── model_provider_port.py
│   │   ├── tool_execution_port.py
│   │   ├── capability_resolution_port.py
│   │   ├── package_resolution_port.py
│   │   ├── knowledge_read_port.py
│   │   ├── knowledge_write_port.py
│   │   ├── event_store_port.py
│   │   ├── state_store_port.py
│   │   ├── blob_store_port.py
│   │   ├── cache_port.py
│   │   ├── approval_port.py
│   │   ├── clock_port.py                 # non-determinism behind a port
│   │   ├── random_port.py
│   │   └── telemetry_port.py
│   │
│   ├── manifest/                         # [+] r2 — the runtime's identity
│   │   ├── __init__.py
│   │   ├── runtime_manifest_loader.py
│   │   ├── runtime_manifest_validator.py
│   │   ├── runtime_identity_resolver.py      # manifest + model ids -> RuntimeIdentity
│   │   ├── package_set_resolver.py
│   │   ├── feature_flag_resolver.py
│   │   ├── provider_binding_resolver.py      # storage · telemetry · plugin providers
│   │   ├── compatibility_gate.py             # refuses to boot on an incompatible set
│   │   ├── manifest_fingerprint.py           # one hash identifying this deployment
│   │   ├── manifest_diff_reporter.py
│   │   └── errors.py
│   │
│   ├── kernel/
│   │   ├── __init__.py
│   │   ├── bootstrap.py
│   │   ├── runtime_process.py
│   │   ├── dependency_graph.py
│   │   ├── component_registry.py
│   │   ├── config_loader.py
│   │   ├── config_validator.py
│   │   ├── lifecycle_manager.py
│   │   ├── startup_hooks.py
│   │   ├── readiness_probe.py
│   │   ├── liveness_probe.py
│   │   ├── graceful_shutdown.py
│   │   ├── shutdown_hooks.py
│   │   └── errors.py
│   │
│   ├── session/
│   │   ├── __init__.py
│   │   ├── session_manager.py
│   │   ├── session_factory.py
│   │   ├── conversation_history_store.py
│   │   ├── turn_appender.py
│   │   ├── attachment_binder.py
│   │   ├── session_checkpoint_writer.py
│   │   ├── session_restorer.py
│   │   ├── session_serializer.py
│   │   └── errors.py
│   │
│   ├── context/
│   │   ├── __init__.py
│   │   ├── parallel_context_assembler.py     # fan-out / fan-in orchestration
│   │   ├── assembly_plan_builder.py
│   │   ├── sources/
│   │   │   ├── __init__.py
│   │   │   ├── execution_graph_source.py     # [+] r4 — read-only graph projection.
│   │   │   │                                 # The Decision Engine is never blind. §6.2
│   │   │   ├── session_history_source.py
│   │   │   ├── runtime_state_source.py
│   │   │   ├── world_state_source.py
│   │   │   ├── memory_retrieval_source.py
│   │   │   ├── package_config_source.py
│   │   │   ├── user_file_source.py
│   │   │   ├── policy_source.py
│   │   │   └── capability_catalog_source.py
│   │   ├── fragment_ranker.py
│   │   ├── relevance_scorer.py
│   │   ├── token_budget_allocator.py
│   │   ├── compaction_strategy.py
│   │   ├── compaction_executor.py
│   │   ├── cache_prefix_builder.py           # stable prefix for provider-side reuse
│   │   ├── context_bundle_builder.py
│   │   ├── assembly_timeout_guard.py
│   │   └── errors.py
│   │
│   ├── prompt/
│   │   ├── __init__.py
│   │   ├── prompt_assembler.py
│   │   ├── prompt_module_loader.py
│   │   ├── template_renderer.py
│   │   ├── template_registry.py
│   │   ├── variable_resolver.py
│   │   ├── prompt_fingerprint.py             # part of the harness version
│   │   └── errors.py
│   │
│   ├── intelligence/
│   │   ├── __init__.py
│   │   │
│   │   ├── decision/                     # [~] r4 — was router/. See §1.6
│   │   │   ├── __init__.py
│   │   │   ├── decision_engine.py            # ONE structured inference per iteration
│   │   │   ├── decision_prompt_composer.py
│   │   │   ├── structured_output_requester.py
│   │   │   ├── execution_contract_parser.py
│   │   │   ├── execution_contract_validator.py
│   │   │   ├── confidence_thresholder.py
│   │   │   ├── clarification_emitter.py
│   │   │   ├── decision_fallback_strategy.py # what happens when parsing fails
│   │   │   └── errors.py
│   │   │
│   │   ├── binding/                      # [+] r4 — DETERMINISTIC, no model call
│   │   │   ├── __init__.py               # runs AFTER decision, BEFORE the policy gate
│   │   │   ├── intent_resolver.py            # intent -> candidate tools, via the index
│   │   │   ├── binding_selector.py           # candidates -> ONE binding
│   │   │   ├── binding_pinner.py             # the binding enters the node identity
│   │   │   ├── parameter_mapper.py           # intent params -> tool input schema
│   │   │   ├── binding_explainer.py          # why this tool, for the trace
│   │   │   └── errors.py
│   │   │
│   │   ├── intent/
│   │   │   ├── __init__.py
│   │   │   ├── intent_classifier.py
│   │   │   ├── intent_taxonomy.py
│   │   │   └── ambiguity_detector.py
│   │   │
│   │   ├── goals/
│   │   │   ├── __init__.py
│   │   │   ├── goal_extractor.py
│   │   │   ├── acceptance_criteria_extractor.py
│   │   │   ├── goal_amendment_applier.py
│   │   │   └── goal_completion_judge.py
│   │   │
│   │   ├── planning/
│   │   │   ├── __init__.py
│   │   │   ├── planner_invoker.py            # only when strategy == PLAN
│   │   │   ├── decomposition_planner.py
│   │   │   ├── task_graph_builder.py
│   │   │   ├── dependency_resolver.py
│   │   │   ├── plan_identity_minter.py
│   │   │   ├── plan_repair_strategy.py
│   │   │   ├── replan_trigger_evaluator.py
│   │   │   └── errors.py
│   │   │
│   │   ├── reasoning/
│   │   │   ├── __init__.py
│   │   │   ├── reasoning_budget_allocator.py
│   │   │   ├── reasoning_trace_recorder.py
│   │   │   └── self_consistency_sampler.py
│   │   │
│   │   ├── capability_selection/
│   │   │   ├── __init__.py
│   │   │   ├── capability_matcher.py
│   │   │   ├── capability_ranker.py
│   │   │   └── capability_binding_resolver.py
│   │   │
│   │   └── workflow_selection/
│   │       ├── __init__.py
│   │       ├── workflow_matcher.py
│   │       ├── workflow_precondition_checker.py
│   │       └── workflow_instantiator.py
│   │
│   ├── policy/
│   │   ├── __init__.py
│   │   ├── policy_engine.py
│   │   ├── policy_document_loader.py
│   │   ├── permission_evaluator.py
│   │   ├── tenancy_isolation_check.py
│   │   ├── budget_admission_check.py
│   │   ├── approval_requirement_resolver.py
│   │   ├── effect_tag_enforcer.py            # effectful ⇒ resolved approval required
│   │   ├── security_rule_evaluator.py
│   │   ├── compliance_rule_evaluator.py
│   │   ├── execution_constraint_applier.py
│   │   ├── contract_validator.py             # emits ValidatedExecutionContract
│   │   └── errors.py
│   │
│   ├── identity/                             # [+] added during review
│   │   ├── __init__.py
│   │   ├── action_identity_computer.py       # hash(session, contract, action, tool, input_digest)
│   │   ├── canonical_input_serializer.py
│   │   ├── input_digest_builder.py
│   │   ├── identity_ledger.py                # has this already run, and what did it cost?
│   │   ├── identity_match_classifier.py      # FULL | PARTIAL | MISS
│   │   ├── partial_match_alerter.py          # silent by nature; must alert, never log
│   │   ├── replay_decision_maker.py
│   │   └── errors.py
│   │
│   ├── leasing/                              # [+] added during review
│   │   ├── __init__.py
│   │   ├── lease_claimer.py                  # lease + version CAS in one statement
│   │   ├── lease_renewer.py
│   │   ├── lease_expiry_sweeper.py           # continuous, never boot-only
│   │   ├── ownership_guard.py
│   │   ├── version_conflict_resolver.py
│   │   └── errors.py
│   │
│   ├── parking/                              # [+] added during review
│   │   ├── __init__.py
│   │   ├── park_writer.py
│   │   ├── park_resolver.py
│   │   ├── approval_park_handler.py
│   │   ├── input_park_handler.py
│   │   ├── timer_park_handler.py
│   │   ├── callback_park_handler.py
│   │   ├── budget_grant_park_handler.py
│   │   ├── park_age_escalator.py             # a park is never silently abandoned
│   │   └── errors.py
│   │
│   ├── budget/                               # [+] added during review
│   │   ├── __init__.py
│   │   ├── cost_estimator.py
│   │   ├── reservation_writer.py             # reserve at dispatch
│   │   ├── settlement_writer.py              # settle at completion, release the difference
│   │   ├── reservation_expirer.py            # a reservation dies with its lease
│   │   ├── ceiling_evaluator.py
│   │   ├── spend_projector.py
│   │   ├── drift_monitor.py                  # reservation vs settlement
│   │   └── errors.py
│   │
│   ├── controller/                           # CONTROL PLANE — never calls a model
│   │   ├── __init__.py
│   │   ├── deterministic_runtime_loop.py
│   │   ├── iteration_driver.py
│   │   ├── action_dispatcher.py
│   │   ├── work_scheduler.py
│   │   ├── work_class_router.py              # fast vs slow class
│   │   ├── runtime_clock.py
│   │   ├── timer_registry.py
│   │   ├── deadline_enforcer.py
│   │   ├── session_lifecycle_manager.py
│   │   ├── crash_recovery_driver.py
│   │   ├── cancellation_propagator.py
│   │   ├── signal_reader.py                  # read in the same transaction as the checkpoint
│   │   ├── checkpoint_manager.py
│   │   ├── execution_graph/                  # [~] r4 — THE runtime execution model
│   │   │   ├── __init__.py                   # plan + state + progress + checkpoint
│   │   │   ├── execution_graph.py            # the artifact itself: spec + status
│   │   │   ├── graph_builder.py              # contract -> nodes
│   │   │   ├── graph_mutator.py              # dynamic node insertion  §6.9
│   │   │   ├── node_state_machine.py         # legal-only, total  §6.3
│   │   │   ├── ready_set_calculator.py       # deps met + condition true  §6.4
│   │   │   ├── condition_evaluator.py        # DETERMINISTIC, never the model  §6.5
│   │   │   ├── parallel_group_resolver.py    # §6.4
│   │   │   ├── retry_policy_evaluator.py     # §6.6
│   │   │   ├── timeout_evaluator.py          # §6.6
│   │   │   ├── approval_gate_evaluator.py    # §6.8
│   │   │   ├── blocked_reason_resolver.py
│   │   │   ├── progress_calculator.py
│   │   │   ├── critical_path_tracker.py
│   │   │   ├── graph_serializer.py           # checkpoint IS the graph  §6.7
│   │   │   ├── graph_deserializer.py
│   │   │   ├── graph_generation_minter.py    # a replan mints a new generation
│   │   │   ├── graph_projection_writer.py    # read-only projection for context  §6.2
│   │   │   └── graph_invariant_checker.py
│   │   ├── iteration_exit_evaluator.py       # wall clock · step budget · park · signal
│   │   ├── completion_evaluator.py
│   │   └── errors.py
│   │
│   ├── capability_executor/                  # [~] r4 — collapsed. See §1.6
│   │   ├── __init__.py                       # DETERMINISTIC. Executes a DECLARED recipe.
│   │   ├── capability_invoker.py             # the Controller's only execution verb
│   │   ├── capability_loader.py
│   │   ├── capability_manifest_reader.py
│   │   ├── capability_context_builder.py     # global bundle -> capability-local slice
│   │   ├── declared_recipe_reader.py         # the chain is AUTHORED, never computed
│   │   ├── recipe_step_executor.py
│   │   ├── parallel_step_executor.py         # parallelism declared in the recipe
│   │   ├── step_retry_policy.py
│   │   ├── step_timeout_guard.py
│   │   ├── tool_invoker.py                   # invokes the PINNED binding; resolves nothing
│   │   ├── input_output_validator.py
│   │   ├── observation_aggregator.py         # N tool results -> ONE observation
│   │   ├── partial_result_reconciler.py
│   │   ├── capability_result_cache.py
│   │   ├── capability_span_recorder.py
│   │   ├── sandbox_boundary.py               # third-party package code fails in here
│   │   └── errors.py
│   │
│   ├── execution/                            # DATA PLANE — all non-determinism
│   │   ├── __init__.py
│   │   ├── action_executor.py
│   │   ├── strategy_dispatcher.py
│   │   ├── strategies/
│   │   │   ├── __init__.py
│   │   │   ├── direct_strategy.py
│   │   │   ├── plan_strategy.py
│   │   │   ├── workflow_strategy.py
│   │   │   ├── parallel_strategy.py
│   │   │   ├── background_strategy.py
│   │   │   ├── long_running_strategy.py
│   │   │   └── human_loop_strategy.py        # delegates to parking, never blocks
│   │   ├── workflow_runner.py
│   │   ├── workflow_state_machine.py
│   │   ├── workflow_compensator.py
│   │   ├── planner_runner.py
│   │   ├── capability_runner.py
│   │   ├── tool_runner.py
│   │   ├── parallel_fanout_executor.py
│   │   ├── result_join_collector.py
│   │   ├── retry_policy.py
│   │   ├── backoff_calculator.py
│   │   ├── attempt_cap_enforcer.py
│   │   ├── dead_letter_writer.py
│   │   ├── rollback_coordinator.py
│   │   ├── timeout_enforcer.py
│   │   ├── abort_signal_propagator.py        # timeout must abort the real call
│   │   ├── middleware_pipeline.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── before_model_hook.py
│   │   │   ├── after_model_hook.py
│   │   │   ├── before_tool_hook.py
│   │   │   ├── after_tool_hook.py
│   │   │   ├── output_truncation_middleware.py
│   │   │   ├── execution_risk_hint_middleware.py
│   │   │   ├── loop_detection_middleware.py
│   │   │   └── cost_annotation_middleware.py
│   │   ├── sandbox/
│   │   │   ├── __init__.py
│   │   │   ├── sandbox_pool.py
│   │   │   ├── sandbox_provisioner.py
│   │   │   ├── sandbox_lifecycle.py
│   │   │   ├── filesystem_isolation.py
│   │   │   ├── network_policy.py
│   │   │   ├── resource_limits.py
│   │   │   └── sandbox_teardown.py
│   │   └── errors.py
│   │
│   ├── observation/
│   │   ├── __init__.py
│   │   ├── observation_collector.py
│   │   ├── deterministic_verifier.py
│   │   ├── verification_check_registry.py
│   │   ├── model_judgment_applier.py         # may downgrade, never upgrade
│   │   ├── evaluation_engine.py
│   │   ├── rubric_resolver.py
│   │   ├── learning_candidate_emitter.py
│   │   ├── observation_summarizer.py
│   │   ├── observation_publisher.py
│   │   └── errors.py
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   ├── event_bus.py
│   │   ├── transactional_outbox_writer.py    # change + event in ONE transaction
│   │   ├── claim_based_relay.py              # claims rows; no cursor exists
│   │   ├── relay_claim_sweeper.py
│   │   ├── partition_key_resolver.py
│   │   ├── event_publisher.py
│   │   ├── subscriber_registry.py
│   │   ├── subscription_dispatcher.py
│   │   ├── projection_engine.py
│   │   ├── projection_registry.py
│   │   ├── replay_engine.py
│   │   ├── replay_determinism_guard.py
│   │   ├── event_type_router.py
│   │   └── errors.py
│   │
│   ├── state/
│   │   ├── __init__.py
│   │   ├── runtime_state_projection.py
│   │   ├── session_state_projection.py
│   │   ├── action_state_projection.py
│   │   ├── budget_state_projection.py
│   │   ├── snapshot_writer.py
│   │   ├── snapshot_loader.py
│   │   ├── state_reconciler.py
│   │   └── errors.py
│   │
│   ├── experience/                           # [+] r3 — replaces runtime/streaming/
│   │   ├── __init__.py                       # streams EXECUTION STATE, not tokens
│   │   │
│   │   ├── event_mapping/
│   │   │   ├── __init__.py
│   │   │   ├── runtime_event_mapper.py       # durable facts -> runtime events
│   │   │   ├── event_class_router.py         # PROGRESS | TRACE | PRESENTATION
│   │   │   └── event_vocabulary.py
│   │   │
│   │   ├── progress/
│   │   │   ├── __init__.py
│   │   │   ├── progress_engine.py
│   │   │   ├── progress_tree_builder.py      # hierarchical, like a build system
│   │   │   ├── node_status_resolver.py
│   │   │   ├── duration_accumulator.py
│   │   │   └── progress_snapshot_builder.py  # for reconnect — see hydrate-then-subscribe
│   │   │
│   │   ├── trace/
│   │   │   ├── __init__.py
│   │   │   ├── execution_trace_builder.py
│   │   │   ├── iteration_span_assembler.py
│   │   │   ├── capability_span_assembler.py
│   │   │   ├── tool_span_assembler.py
│   │   │   └── trace_writer.py
│   │   │
│   │   ├── transport/
│   │   │   ├── __init__.py
│   │   │   ├── stream_publisher.py           # direct to client; NEVER the outbox
│   │   │   ├── frame_sequencer.py
│   │   │   ├── subscriber_registry.py
│   │   │   ├── stream_backpressure.py
│   │   │   └── resume_from_snapshot.py
│   │   │
│   │   ├── encoders/
│   │   │   ├── __init__.py
│   │   │   ├── agui_event_encoder.py         # AG-UI wire format — see §9.7
│   │   │   ├── native_event_encoder.py
│   │   │   └── otel_genai_exporter.py        # gen_ai.* spans — see §9.7
│   │   │
│   │   └── errors.py
│   │
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── model_semaphore.py
│   │   ├── tenant_admission_controller.py
│   │   ├── concurrency_limiter.py
│   │   ├── token_rate_limiter.py
│   │   ├── cpu_quota_manager.py
│   │   ├── memory_quota_manager.py
│   │   ├── connection_custody_guard.py       # no scarce resource across a model call
│   │   └── errors.py
│   │
│   ├── distribution/                     # [+] r2 — many workers, one runtime
│   │   ├── __init__.py
│   │   ├── worker_identity.py
│   │   ├── worker_registry.py
│   │   ├── worker_heartbeat.py
│   │   ├── partition_assigner.py
│   │   ├── partition_ownership_table.py
│   │   ├── rebalance_coordinator.py
│   │   ├── drain_coordinator.py              # graceful removal without losing a lease
│   │   ├── shard_key_resolver.py
│   │   ├── clock_skew_detector.py
│   │   └── errors.py
│   │
│   ├── telemetry/
│   │   ├── __init__.py
│   │   ├── metric_emitter.py
│   │   ├── metric_catalog.py
│   │   ├── span_recorder.py
│   │   ├── trace_context_propagator.py
│   │   ├── structured_logger.py
│   │   ├── log_redactor.py
│   │   ├── health_reporter.py
│   │   └── signal_definitions.py             # the alertable signal set
│   │
│   ├── testing/                              # first-party fakes; ships with the kernel
│   │   ├── __init__.py
│   │   ├── fake_model_provider.py
│   │   ├── fake_tool_executor.py
│   │   ├── fake_approval_port.py
│   │   ├── controllable_clock.py
│   │   ├── deterministic_random.py
│   │   ├── in_memory_event_store.py
│   │   ├── in_memory_state_store.py
│   │   ├── lease_expiry_forcer.py
│   │   ├── crash_injector.py
│   │   └── golden_session_recorder.py
│   │
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ DIAGNOSTICS — developer-facing introspection. Distinct from telemetry.
├──────────────────────────────────────────────────────────────────────────────
│
├── diagnostics/                              # [+] r2
│   ├── __init__.py
│   ├── diagnostic_context.py
│   ├── access_control.py                     # diagnostics expose raw payloads
│   │
│   ├── timeline/
│   │   ├── __init__.py
│   │   ├── execution_timeline_builder.py
│   │   ├── span_tree_assembler.py
│   │   ├── critical_path_analyzer.py
│   │   └── machine_vs_parked_splitter.py
│   │
│   ├── prompt_viewer/
│   │   ├── __init__.py
│   │   ├── assembled_prompt_reconstructor.py # rebuilt from state, not stored
│   │   ├── context_source_attributor.py      # which source contributed which tokens
│   │   ├── token_budget_visualizer.py
│   │   └── prompt_diff_renderer.py
│   │
│   ├── event_explorer/
│   │   ├── __init__.py
│   │   ├── event_query_service.py
│   │   ├── partition_browser.py
│   │   ├── causality_linker.py
│   │   └── projection_inspector.py
│   │
│   ├── checkpoint_explorer/
│   │   ├── __init__.py
│   │   ├── checkpoint_browser.py
│   │   ├── state_diff_renderer.py
│   │   └── restore_preview.py
│   │
│   ├── trajectory_viewer/
│   │   ├── __init__.py
│   │   ├── trajectory_navigator.py           # trajectory as a navigable file tree
│   │   ├── message_file_projector.py
│   │   ├── divergence_comparator.py          # passing vs failing rollout of one task
│   │   └── redaction_aware_renderer.py
│   │
│   ├── replay_viewer/
│   │   ├── __init__.py
│   │   ├── replay_session_builder.py
│   │   ├── step_stepper.py
│   │   ├── decision_inspector.py
│   │   └── divergence_detector.py            # replay disagreeing with the record
│   │
│   ├── contract_inspector/
│   │   ├── __init__.py
│   │   ├── execution_contract_renderer.py
│   │   ├── validation_trace_renderer.py
│   │   └── identity_resolution_explainer.py
│   │
│   └── web/
│       ├── __init__.py
│       ├── diagnostics_app.py
│       ├── routes.py
│       └── static/
│
├──────────────────────────────────────────────────────────────────────────────
│ KNOWLEDGE SYSTEM
├──────────────────────────────────────────────────────────────────────────────
│
├── knowledge/
│   ├── __init__.py
│   │
│   ├── world/
│   │   ├── __init__.py
│   │   ├── world_state_builder.py
│   │   ├── entity_store.py
│   │   ├── entity_resolver.py
│   │   ├── fact_store.py
│   │   ├── fact_verifier.py
│   │   ├── relationship_graph.py
│   │   ├── unknown_tracker.py
│   │   ├── assumption_tracker.py
│   │   ├── confidence_calculator.py
│   │   ├── staleness_detector.py
│   │   ├── belief_invalidator.py
│   │   ├── world_state_projection.py
│   │   └── errors.py
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── memory_engine.py
│   │   ├── stores/
│   │   │   ├── __init__.py
│   │   │   ├── semantic_memory_store.py
│   │   │   ├── episodic_memory_store.py
│   │   │   ├── procedural_memory_store.py
│   │   │   ├── runtime_memory_store.py
│   │   │   └── user_memory_store.py
│   │   ├── memory_writer.py
│   │   ├── tenant_abstraction_guard.py       # a lesson must be true of the system, not a customer
│   │   ├── memory_retriever.py
│   │   ├── hybrid_search.py
│   │   ├── relevance_scorer.py
│   │   ├── recency_decay.py
│   │   ├── deduplicator.py
│   │   ├── compressor.py
│   │   ├── curation_policy.py                # removal is a first-class operation
│   │   ├── memory_pruner.py
│   │   └── errors.py
│   │
│   └── artifacts/
│       ├── __init__.py
│       ├── artifact_pipeline.py
│       ├── artifact_manager.py
│       ├── artifact_versioner.py
│       ├── lineage_tracker.py
│       ├── exporters/
│       │   ├── __init__.py
│       │   ├── markdown_exporter.py
│       │   ├── json_exporter.py
│       │   ├── pdf_exporter.py
│       │   ├── docx_exporter.py
│       │   ├── slides_exporter.py
│       │   └── source_code_exporter.py
│       ├── templates/
│       │   ├── report_template.md
│       │   ├── summary_template.md
│       │   └── changelog_template.md
│       └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ LEARNING SYSTEM — asynchronous. Never blocks the request path.
├──────────────────────────────────────────────────────────────────────────────
│
├── learning/
│   ├── __init__.py
│   │
│   ├── trajectory/
│   │   ├── __init__.py
│   │   ├── trajectory_collector.py
│   │   ├── trajectory_normalizer.py
│   │   ├── trajectory_redactor.py            # redaction at capture, not at read
│   │   ├── trajectory_indexer.py
│   │   └── trajectory_writer.py
│   │
│   ├── distillation/
│   │   ├── __init__.py
│   │   ├── pattern_extractor.py
│   │   ├── failure_cluster_builder.py
│   │   ├── root_cause_analyzer.py
│   │   ├── success_pattern_analyzer.py
│   │   ├── evidence_corpus_builder.py        # ~10M tokens → ~10K
│   │   ├── per_task_report_writer.py
│   │   └── corpus_overview_writer.py
│   │
│   ├── memory_candidates/
│   │   ├── __init__.py
│   │   ├── candidate_generator.py
│   │   ├── candidate_scorer.py
│   │   ├── candidate_deduplicator.py
│   │   └── candidate_promoter.py
│   │
│   ├── benchmark/
│   │   ├── __init__.py
│   │   ├── benchmark_definition_loader.py
│   │   ├── task_set_registry.py
│   │   ├── benchmark_executor.py
│   │   ├── rollout_scheduler.py
│   │   ├── pass_at_k_calculator.py
│   │   ├── token_cost_calculator.py
│   │   ├── variance_analyzer.py
│   │   └── result_writer.py
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── session_analytics.py
│   │   ├── cost_analytics.py
│   │   ├── latency_analytics.py
│   │   ├── failure_taxonomy_analytics.py
│   │   ├── human_latency_separator.py        # parked time is not machine time
│   │   └── report_generator.py
│   │
│   ├── optimizer/
│   │   ├── __init__.py
│   │   ├── prompt_optimizer.py
│   │   ├── routing_policy_optimizer.py
│   │   ├── budget_policy_optimizer.py
│   │   └── retry_policy_optimizer.py
│   │
│   └── workers/
│       ├── __init__.py
│       ├── learning_worker.py
│       ├── worker_pool.py
│       ├── job_queue_consumer.py
│       ├── job_scheduler.py
│       └── worker_health.py
│
├──────────────────────────────────────────────────────────────────────────────
│ MODEL PROVIDERS
├──────────────────────────────────────────────────────────────────────────────
│
├── models/
│   ├── __init__.py
│   ├── model_router.py
│   ├── model_registry.py
│   ├── model_descriptor.py
│   ├── capability_matrix.py                  # which models support what
│   ├── fallback_chain.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── anthropic_provider.py
│   │   ├── openai_provider.py
│   │   ├── gemini_provider.py
│   │   ├── bedrock_provider.py
│   │   ├── vertex_provider.py
│   │   ├── local_provider.py
│   │   └── echo_provider.py                  # deterministic, for tests
│   ├── streaming/
│   │   ├── __init__.py
│   │   ├── stream_adapter.py
│   │   ├── chunk_normalizer.py
│   │   └── abort_handler.py                  # a cancel must stop the stream
│   ├── structured_output/
│   │   ├── __init__.py
│   │   ├── schema_enforcer.py
│   │   ├── json_repair.py
│   │   └── parse_failure_recovery.py
│   ├── tokenization/
│   │   ├── __init__.py
│   │   ├── token_counter.py
│   │   ├── tokenizer_registry.py
│   │   └── context_window_calculator.py
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── prompt_cache.py
│   │   ├── cache_key_builder.py
│   │   └── cache_invalidator.py
│   ├── pricing/
│   │   ├── __init__.py
│   │   ├── price_table.py
│   │   └── cost_calculator.py
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ CAPABILITIES — WHAT can be accomplished
├──────────────────────────────────────────────────────────────────────────────
│
├── capabilities/
│   ├── __init__.py
│   ├── capability_registry.py
│   ├── capability_base.py
│   ├── capability_loader.py
│   ├── capability_validator.py
│   ├── tool_binding_resolver.py
│   │
│   ├── research/
│   │   ├── __init__.py
│   │   ├── search_capability.py
│   │   ├── read_capability.py
│   │   ├── analyze_capability.py
│   │   ├── compare_capability.py
│   │   ├── summarize_capability.py
│   │   ├── verify_capability.py
│   │   ├── report_capability.py
│   │   └── descriptors/
│   │       ├── search.capability.yaml
│   │       ├── read.capability.yaml
│   │       ├── analyze.capability.yaml
│   │       ├── compare.capability.yaml
│   │       ├── summarize.capability.yaml
│   │       ├── verify.capability.yaml
│   │       └── report.capability.yaml
│   │
│   ├── coding/
│   │   ├── __init__.py
│   │   ├── repository_survey_capability.py
│   │   ├── patch_authoring_capability.py
│   │   ├── test_execution_capability.py
│   │   ├── refactor_capability.py
│   │   ├── review_capability.py
│   │   └── descriptors/
│   │       ├── repository_survey.capability.yaml
│   │       ├── patch_authoring.capability.yaml
│   │       ├── test_execution.capability.yaml
│   │       ├── refactor.capability.yaml
│   │       └── review.capability.yaml
│   │
│   ├── browser/
│   │   ├── __init__.py
│   │   ├── navigate_capability.py
│   │   ├── extract_capability.py
│   │   ├── interact_capability.py
│   │   └── descriptors/
│   │       ├── navigate.capability.yaml
│   │       ├── extract.capability.yaml
│   │       └── interact.capability.yaml
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── tabular_analysis_capability.py
│   │   ├── statistical_analysis_capability.py
│   │   ├── visualization_capability.py
│   │   └── descriptors/
│   │       ├── tabular_analysis.capability.yaml
│   │       ├── statistical_analysis.capability.yaml
│   │       └── visualization.capability.yaml
│   │
│   ├── planning/
│   │   ├── __init__.py
│   │   ├── decomposition_capability.py
│   │   ├── prioritization_capability.py
│   │   └── descriptors/
│   │       ├── decomposition.capability.yaml
│   │       └── prioritization.capability.yaml
│   │
│   ├── meeting/
│   │   ├── __init__.py
│   │   ├── transcript_ingest_capability.py
│   │   ├── action_item_extraction_capability.py
│   │   ├── minutes_capability.py
│   │   └── descriptors/
│   │       ├── transcript_ingest.capability.yaml
│   │       ├── action_item_extraction.capability.yaml
│   │       └── minutes.capability.yaml
│   │
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── document_generation_capability.py
│   │   ├── slide_generation_capability.py
│   │   ├── dashboard_generation_capability.py
│   │   └── descriptors/
│   │       ├── document_generation.capability.yaml
│   │       ├── slide_generation.capability.yaml
│   │       └── dashboard_generation.capability.yaml
│   │
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ TOOLS — HOW work is performed. Every tool is tagged PURE or EFFECTFUL.
├──────────────────────────────────────────────────────────────────────────────
│
├── tools/
│   ├── __init__.py
│   ├── tool_registry.py
│   ├── tool_capability_index.py              # [+] r3 — which tools satisfy which intent
│   ├── intent_binding_table.py               # [+] r3 — preferred binding per intent
│   ├── tool_base.py
│   ├── tool_loader.py
│   ├── tool_descriptor_validator.py
│   ├── effect_tag_auditor.py                 # CI fails on an untagged tool
│   ├── output_shaper.py
│   ├── error_message_formatter.py            # errors are the model's feedback channel
│   │
│   ├── browser/
│   │   ├── __init__.py
│   │   ├── navigate_tool.py
│   │   ├── read_page_tool.py
│   │   ├── click_element_tool.py
│   │   ├── fill_form_tool.py
│   │   ├── screenshot_tool.py
│   │   ├── session_pool.py
│   │   └── descriptors/
│   │       ├── navigate.tool.yaml
│   │       ├── read_page.tool.yaml
│   │       ├── click_element.tool.yaml
│   │       ├── fill_form.tool.yaml
│   │       └── screenshot.tool.yaml
│   │
│   ├── terminal/
│   │   ├── __init__.py
│   │   ├── run_command_tool.py
│   │   ├── background_process_tool.py
│   │   ├── process_supervisor.py
│   │   ├── output_truncator.py
│   │   └── descriptors/
│   │       ├── run_command.tool.yaml
│   │       └── background_process.tool.yaml
│   │
│   ├── filesystem/
│   │   ├── __init__.py
│   │   ├── read_file_tool.py
│   │   ├── write_file_tool.py
│   │   ├── list_directory_tool.py
│   │   ├── search_files_tool.py
│   │   ├── apply_patch_tool.py
│   │   ├── path_sandbox_guard.py
│   │   └── descriptors/
│   │       ├── read_file.tool.yaml
│   │       ├── write_file.tool.yaml
│   │       ├── list_directory.tool.yaml
│   │       ├── search_files.tool.yaml
│   │       └── apply_patch.tool.yaml
│   │
│   ├── github/
│   │   ├── __init__.py
│   │   ├── clone_repository_tool.py
│   │   ├── read_issue_tool.py
│   │   ├── create_branch_tool.py
│   │   ├── push_branch_tool.py               # EFFECTFUL
│   │   ├── open_pull_request_tool.py         # EFFECTFUL
│   │   ├── comment_tool.py                   # EFFECTFUL
│   │   └── descriptors/
│   │       ├── clone_repository.tool.yaml
│   │       ├── read_issue.tool.yaml
│   │       ├── create_branch.tool.yaml
│   │       ├── push_branch.tool.yaml
│   │       ├── open_pull_request.tool.yaml
│   │       └── comment.tool.yaml
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   ├── web_search_tool.py
│   │   ├── academic_search_tool.py
│   │   ├── news_search_tool.py
│   │   ├── result_deduplicator.py
│   │   └── descriptors/
│   │       ├── web_search.tool.yaml
│   │       ├── academic_search.tool.yaml
│   │       └── news_search.tool.yaml
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── run_query_tool.py
│   │   ├── describe_schema_tool.py
│   │   ├── query_safety_guard.py
│   │   └── descriptors/
│   │       ├── run_query.tool.yaml
│   │       └── describe_schema.tool.yaml
│   │
│   ├── pdf/
│   │   ├── __init__.py
│   │   ├── extract_text_tool.py
│   │   ├── extract_tables_tool.py
│   │   ├── render_page_tool.py
│   │   └── descriptors/
│   │       ├── extract_text.tool.yaml
│   │       ├── extract_tables.tool.yaml
│   │       └── render_page.tool.yaml
│   │
│   ├── email/
│   │   ├── __init__.py
│   │   ├── read_inbox_tool.py
│   │   ├── send_email_tool.py                # EFFECTFUL
│   │   └── descriptors/
│   │       ├── read_inbox.tool.yaml
│   │       └── send_email.tool.yaml
│   │
│   ├── slack/
│   │   ├── __init__.py
│   │   ├── read_channel_tool.py
│   │   ├── post_message_tool.py              # EFFECTFUL
│   │   └── descriptors/
│   │       ├── read_channel.tool.yaml
│   │       └── post_message.tool.yaml
│   │
│   ├── jira/
│   │   ├── __init__.py
│   │   ├── read_issue_tool.py
│   │   ├── create_issue_tool.py              # EFFECTFUL
│   │   ├── transition_issue_tool.py          # EFFECTFUL
│   │   └── descriptors/
│   │       ├── read_issue.tool.yaml
│   │       ├── create_issue.tool.yaml
│   │       └── transition_issue.tool.yaml
│   │
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── mcp_client.py
│   │   ├── mcp_server_registry.py
│   │   ├── mcp_tool_adapter.py
│   │   ├── mcp_descriptor_translator.py
│   │   ├── mcp_effect_inferencer.py          # unknown effect defaults to EFFECTFUL
│   │   └── mcp_transport.py
│   │
│   ├── custom/
│   │   ├── __init__.py
│   │   ├── custom_tool_loader.py
│   │   └── example_custom_tool.py
│   │
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ PACKAGES — domain behaviour. THIS IS THE HARNESS.
├──────────────────────────────────────────────────────────────────────────────
│
├── packages/
│   ├── __init__.py
│   │
│   ├── registry/
│   │   ├── __init__.py
│   │   ├── package_registry.py
│   │   ├── package_loader.py
│   │   ├── package_resolver.py
│   │   ├── package_validator.py
│   │   ├── manifest_parser.py
│   │   ├── dependency_resolver.py
│   │   ├── version_pinner.py                 # pinned against a model identity
│   │   ├── compatibility_checker.py
│   │   ├── package_installer.py
│   │   ├── package_activator.py
│   │   └── errors.py
│   │
│   ├── runtime/
│   │   ├── __init__.py
│   │   ├── package_context_binder.py
│   │   ├── prompt_module_resolver.py
│   │   ├── policy_overlay_applier.py
│   │   ├── capability_scope_resolver.py
│   │   └── memory_config_applier.py
│   │
│   ├── research/
│   │   ├── package.manifest.yaml
│   │   ├── prompts/
│   │   │   ├── system_prompt.md
│   │   │   ├── research_discipline.module.md
│   │   │   ├── source_verification.module.md
│   │   │   └── report_style.module.md
│   │   ├── capabilities/
│   │   │   └── enabled.yaml
│   │   ├── policies/
│   │   │   ├── source_policy.yaml
│   │   │   └── budget_policy.yaml
│   │   ├── templates/
│   │   │   ├── research_report.md
│   │   │   └── source_table.md
│   │   ├── knowledge/
│   │   │   └── domain_facts.yaml
│   │   ├── skills/
│   │   │   ├── literature_sweep/SKILL.md
│   │   │   └── claim_verification/SKILL.md
│   │   ├── memory/
│   │   │   └── memory_config.yaml
│   │   ├── evaluation/
│   │   │   └── rubrics.yaml
│   │   └── workflows/
│   │       └── literature_review.workflow.yaml
│   │
│   ├── coding/
│   │   ├── package.manifest.yaml
│   │   ├── prompts/
│   │   │   ├── system_prompt.md
│   │   │   ├── contract_first.module.md
│   │   │   ├── evaluator_mirroring.module.md
│   │   │   └── minimal_diff.module.md
│   │   ├── capabilities/enabled.yaml
│   │   ├── policies/
│   │   │   ├── repository_policy.yaml
│   │   │   └── publish_guard_policy.yaml
│   │   ├── templates/
│   │   │   ├── pull_request_body.md
│   │   │   └── commit_message.md
│   │   ├── knowledge/build_systems.yaml
│   │   ├── skills/
│   │   │   ├── failing_test_triage/SKILL.md
│   │   │   └── dependency_upgrade/SKILL.md
│   │   ├── memory/memory_config.yaml
│   │   ├── evaluation/rubrics.yaml
│   │   └── workflows/
│   │       ├── issue_to_pull_request.workflow.yaml
│   │       └── flaky_test_investigation.workflow.yaml
│   │
│   ├── meeting/
│   │   ├── package.manifest.yaml
│   │   ├── prompts/system_prompt.md
│   │   ├── capabilities/enabled.yaml
│   │   ├── policies/recording_policy.yaml
│   │   ├── templates/minutes.md
│   │   ├── knowledge/participants.yaml
│   │   ├── skills/action_item_extraction/SKILL.md
│   │   ├── memory/memory_config.yaml
│   │   ├── evaluation/rubrics.yaml
│   │   └── workflows/post_meeting_summary.workflow.yaml
│   │
│   ├── devops/
│   │   ├── package.manifest.yaml
│   │   ├── prompts/system_prompt.md
│   │   ├── capabilities/enabled.yaml
│   │   ├── policies/
│   │   │   ├── change_window_policy.yaml
│   │   │   └── blast_radius_policy.yaml
│   │   ├── templates/incident_report.md
│   │   ├── knowledge/service_topology.yaml
│   │   ├── skills/rollback_procedure/SKILL.md
│   │   ├── memory/memory_config.yaml
│   │   ├── evaluation/rubrics.yaml
│   │   └── workflows/incident_triage.workflow.yaml
│   │
│   ├── sales/
│   │   ├── package.manifest.yaml
│   │   ├── prompts/system_prompt.md
│   │   ├── capabilities/enabled.yaml
│   │   ├── policies/outreach_policy.yaml
│   │   ├── templates/proposal.md
│   │   ├── knowledge/product_catalog.yaml
│   │   ├── skills/account_research/SKILL.md
│   │   ├── memory/memory_config.yaml
│   │   ├── evaluation/rubrics.yaml
│   │   └── workflows/lead_qualification.workflow.yaml
│   │
│   ├── support/
│   │   ├── package.manifest.yaml
│   │   ├── prompts/system_prompt.md
│   │   ├── capabilities/enabled.yaml
│   │   ├── policies/escalation_policy.yaml
│   │   ├── templates/response.md
│   │   ├── knowledge/known_issues.yaml
│   │   ├── skills/ticket_triage/SKILL.md
│   │   ├── memory/memory_config.yaml
│   │   ├── evaluation/rubrics.yaml
│   │   └── workflows/ticket_resolution.workflow.yaml
│   │
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ PLUGIN SDK
├──────────────────────────────────────────────────────────────────────────────
│
├── plugins/
│   ├── __init__.py
│   ├── plugin_loader.py
│   ├── plugin_registry.py
│   ├── plugin_manifest_parser.py
│   ├── plugin_isolation_boundary.py
│   ├── plugin_permission_model.py
│   ├── plugin_lifecycle.py
│   ├── plugin_health_monitor.py
│   ├── hooks/
│   │   ├── __init__.py
│   │   ├── hook_registry.py
│   │   ├── context_hook.py
│   │   ├── router_hook.py
│   │   ├── execution_hook.py
│   │   ├── observation_hook.py
│   │   └── telemetry_hook.py
│   ├── sdk/
│   │   ├── __init__.py
│   │   ├── plugin_base.py
│   │   ├── tool_plugin_base.py
│   │   ├── capability_plugin_base.py
│   │   ├── provider_plugin_base.py
│   │   ├── storage_plugin_base.py
│   │   └── testing_harness.py
│   ├── examples/
│   │   ├── example_tool_plugin/
│   │   ├── example_capability_plugin/
│   │   └── example_provider_plugin/
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ SECURITY
├──────────────────────────────────────────────────────────────────────────────
│
├── security/
│   ├── __init__.py
│   ├── authentication/
│   │   ├── __init__.py
│   │   ├── credential_verifier.py
│   │   ├── token_issuer.py
│   │   └── session_binding.py
│   ├── authorization/
│   │   ├── __init__.py
│   │   ├── rbac_engine.py
│   │   ├── role_registry.py
│   │   ├── permission_matrix.py
│   │   └── scope_evaluator.py
│   ├── tenancy/
│   │   ├── __init__.py
│   │   ├── tenant_context.py
│   │   ├── tenant_isolation_enforcer.py
│   │   └── cross_tenant_access_detector.py
│   ├── secrets/
│   │   ├── __init__.py
│   │   ├── vault_client.py
│   │   ├── secret_resolver.py
│   │   ├── secret_injector.py                # into sandboxes, scoped and short-lived
│   │   └── secret_rotation.py
│   ├── encryption/
│   │   ├── __init__.py
│   │   ├── at_rest_encryptor.py
│   │   ├── in_transit_enforcer.py
│   │   └── key_manager.py
│   ├── redaction/
│   │   ├── __init__.py
│   │   ├── pii_detector.py
│   │   ├── credential_detector.py
│   │   ├── capture_time_redactor.py
│   │   └── redaction_policy.py
│   ├── prompt_safety/
│   │   ├── __init__.py
│   │   ├── untrusted_content_marker.py       # fetched content is data, never instruction
│   │   ├── injection_detector.py
│   │   └── content_channel_separator.py
│   ├── audit/
│   │   ├── __init__.py
│   │   ├── audit_log_writer.py
│   │   ├── audit_query_service.py
│   │   └── tamper_evidence.py
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ STORAGE — adapters behind ports
├──────────────────────────────────────────────────────────────────────────────
│
├── storage/
│   ├── __init__.py
│   │
│   ├── postgres/
│   │   ├── __init__.py
│   │   ├── connection_pool.py
│   │   ├── transaction_manager.py
│   │   ├── session_repository.py
│   │   ├── action_repository.py
│   │   ├── identity_ledger_repository.py
│   │   ├── lease_repository.py
│   │   ├── park_repository.py
│   │   ├── budget_ledger_repository.py
│   │   ├── approval_repository.py
│   │   ├── signal_repository.py
│   │   ├── event_repository.py
│   │   ├── projection_repository.py
│   │   └── migrations/
│   │       ├── 0001_create_sessions.sql
│   │       ├── 0002_create_events_outbox.sql
│   │       ├── 0003_create_actions.sql
│   │       ├── 0004_create_identity_ledger.sql
│   │       ├── 0005_create_leases.sql
│   │       ├── 0006_create_parks_and_approvals.sql
│   │       ├── 0007_create_budget_ledger.sql
│   │       ├── 0008_create_signals.sql
│   │       ├── 0009_create_projections.sql
│   │       └── 0010_create_indexes.sql
│   │
│   ├── redis/
│   │   ├── __init__.py
│   │   ├── redis_client.py
│   │   ├── cache_adapter.py
│   │   ├── distributed_lock.py
│   │   ├── rate_limit_counter.py
│   │   └── pubsub_adapter.py
│   │
│   ├── vector/
│   │   ├── __init__.py
│   │   ├── vector_store_adapter.py
│   │   ├── pgvector_backend.py
│   │   ├── qdrant_backend.py
│   │   ├── embedding_client.py
│   │   └── index_manager.py
│   │
│   ├── blob/
│   │   ├── __init__.py
│   │   ├── blob_store_adapter.py
│   │   ├── s3_backend.py
│   │   ├── gcs_backend.py
│   │   ├── local_filesystem_backend.py
│   │   └── signed_url_issuer.py
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   ├── event_store_adapter.py
│   │   ├── append_writer.py
│   │   ├── claim_reader.py
│   │   └── compaction_job.py
│   │
│   ├── checkpoints/
│   │   ├── __init__.py
│   │   ├── checkpoint_store_adapter.py
│   │   ├── snapshot_serializer.py
│   │   └── retention_policy.py
│   │
│   ├── trajectories/
│   │   ├── __init__.py
│   │   ├── trajectory_store_adapter.py
│   │   ├── trajectory_partitioner.py
│   │   └── retention_policy.py
│   │
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ EVOLUTION (AHE) — proposes only. Writes to packages/registry and nowhere else.
├──────────────────────────────────────────────────────────────────────────────
│
├── evolution/
│   ├── __init__.py
│   │
│   ├── trajectory_store/
│   │   ├── __init__.py
│   │   ├── trajectory_reader.py
│   │   ├── trajectory_filter.py
│   │   └── trajectory_partition_index.py
│   │
│   ├── experiment_manager/
│   │   ├── __init__.py
│   │   ├── experiment_definition.py
│   │   ├── variable_isolator.py              # exactly one variable per round
│   │   ├── base_model_pinner.py
│   │   ├── round_scheduler.py
│   │   ├── control_group_manager.py
│   │   └── experiment_recorder.py
│   │
│   ├── benchmark_runner/
│   │   ├── __init__.py
│   │   ├── benchmark_invoker.py
│   │   ├── isolated_rollout_executor.py      # fresh sandbox per rollout
│   │   ├── failure_semantics_policy.py       # aborted trials count as failures
│   │   ├── score_aggregator.py
│   │   └── machine_time_separator.py         # parked time excluded from harness attribution
│   │
│   ├── evidence/
│   │   ├── __init__.py
│   │   ├── evidence_corpus_reader.py
│   │   ├── drill_down_index.py
│   │   └── progressive_disclosure_loader.py
│   │
│   ├── evolution_agent/
│   │   ├── __init__.py
│   │   ├── evolve_agent.py
│   │   ├── component_selector.py             # which level to edit, and why
│   │   ├── constraint_level_ranker.py
│   │   ├── edit_proposer.py
│   │   ├── workspace_boundary_guard.py       # writes only inside packages/
│   │   ├── prediction_recorder.py
│   │   └── errors.py
│   │
│   ├── manifest/
│   │   ├── __init__.py
│   │   ├── change_manifest_writer.py
│   │   ├── change_entry_builder.py
│   │   ├── prediction_set_builder.py
│   │   └── manifest_validator.py
│   │
│   ├── attribution/
│   │   ├── __init__.py
│   │   ├── delta_calculator.py
│   │   ├── prediction_intersector.py
│   │   ├── verdict_assigner.py               # KEEP | IMPROVE | ROLLBACK_AND_PIVOT
│   │   ├── regression_detector.py
│   │   ├── interaction_analyzer.py           # components do not stack additively
│   │   └── self_attribution_scorer.py        # precision and recall of the loop's own claims
│   │
│   ├── optimizer/
│   │   ├── __init__.py
│   │   ├── candidate_ranker.py
│   │   ├── search_strategy.py
│   │   └── stopping_criterion.py
│   │
│   ├── versioning/
│   │   ├── __init__.py
│   │   ├── candidate_version_builder.py
│   │   ├── package_diff_generator.py
│   │   ├── version_tagger.py
│   │   └── rollback_executor.py              # file-granularity revert
│   │
│   ├── rollout/
│   │   ├── __init__.py
│   │   ├── human_approval_gate.py            # a durable park
│   │   ├── promotion_executor.py
│   │   ├── canary_controller.py
│   │   ├── shadow_evaluator.py
│   │   ├── rollback_trigger.py
│   │   └── promotion_audit_log.py
│   │
│   └── errors.py
│
├──────────────────────────────────────────────────────────────────────────────
│ DEPLOY
├──────────────────────────────────────────────────────────────────────────────
│
├── deploy/
│   ├── docker/
│   │   ├── Dockerfile.gateway
│   │   ├── Dockerfile.worker
│   │   ├── Dockerfile.learning
│   │   ├── Dockerfile.evolution
│   │   └── entrypoint.sh
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── gateway-deployment.yaml
│   │   ├── worker-deployment.yaml
│   │   ├── learning-deployment.yaml
│   │   ├── evolution-cronjob.yaml
│   │   ├── sweeper-deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.example.yaml
│   │   ├── hpa-gateway.yaml
│   │   ├── hpa-worker.yaml
│   │   ├── poddisruptionbudget.yaml
│   │   └── networkpolicy.yaml
│   ├── helm/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values.production.yaml
│   │   └── templates/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── modules/
│   │       ├── database/
│   │       ├── cache/
│   │       ├── object_storage/
│   │       └── observability/
│   ├── cloudrun/
│   │   └── service.yaml
│   └── railway/
│       └── railway.json
│
├──────────────────────────────────────────────────────────────────────────────
│ SCRIPTS
├──────────────────────────────────────────────────────────────────────────────
│
├── scripts/
│   ├── bootstrap_development.py
│   ├── run_migrations.py
│   ├── seed_reference_data.py
│   ├── validate_configuration.py
│   ├── validate_runtime_manifest.py
│   ├── run_package_conformance.py
│   ├── print_runtime_identity.py
│   ├── validate_dependency_boundaries.py
│   ├── validate_effect_tags.py
│   ├── scan_packages_for_tenant_data.py
│   ├── export_json_schemas.py
│   ├── record_golden_session.py
│   ├── replay_golden_set.py
│   ├── run_benchmark.py
│   ├── run_evolution_round.py
│   ├── promote_package_version.py
│   ├── generate_openapi.py
│   └── cut_release.py
│
├──────────────────────────────────────────────────────────────────────────────
│ TESTS — mirrors the source tree
├──────────────────────────────────────────────────────────────────────────────
│
└── tests/
    ├── conftest.py
    ├── fixtures/
    │   ├── __init__.py
    │   ├── session_fixtures.py
    │   ├── contract_fixtures.py
    │   ├── event_fixtures.py
    │   ├── package_fixtures.py
    │   ├── tool_fixtures.py
    │   └── recorded_sessions/
    │
    ├── unit/
    │   ├── contracts/
    │   ├── gateway/
    │   ├── diagnostics/
    │   ├── runtime/
    │   │   ├── manifest/
    │   │   ├── decision/
    │   │   ├── binding/
    │   │   ├── capability_executor/
    │   │   ├── execution_graph/
    │   │   ├── experience/
    │   │   ├── distribution/
    │   │   ├── context/
    │   │   ├── intelligence/
    │   │   ├── policy/
    │   │   ├── identity/
    │   │   ├── leasing/
    │   │   ├── parking/
    │   │   ├── budget/
    │   │   ├── controller/
    │   │   ├── execution/
    │   │   ├── observation/
    │   │   ├── events/
    │   │   ├── state/
    │   │   └── resources/
    │   ├── knowledge/
    │   ├── learning/
    │   ├── models/
    │   ├── capabilities/
    │   ├── tools/
    │   ├── packages/
    │   ├── plugins/
    │   ├── security/
    │   ├── storage/
    │   └── evolution/
    │
    ├── integration/
    │   ├── test_outbox_to_relay.py
    │   ├── test_router_to_policy_to_controller.py
    │   ├── test_action_identity_replay.py
    │   ├── test_budget_reserve_and_settle.py
    │   ├── test_park_and_resume.py
    │   ├── test_signal_midflight_abort.py
    │   ├── test_parallel_context_assembly.py
    │   ├── test_package_activation.py
    │   └── test_plugin_isolation.py
    │
    ├── invariants/
    │   ├── test_router_never_names_a_tool.py
    │   ├── test_binding_pinned_into_identity.py
    │   ├── test_experience_adds_no_durable_events.py
    │   ├── test_only_renderers_write_to_surface.py
    │   ├── test_graph_transitions_are_legal.py
    │   ├── test_no_run_state_on_domain_tables.py
    │   ├── test_no_connection_across_model_call.py
    │   ├── test_exactly_one_driver_per_session.py
    │   ├── test_effectful_requires_approval.py
    │   ├── test_non_determinism_quarantined.py
    │   ├── test_progress_not_in_event_log.py
    │   └── test_replay_is_deterministic.py
    │
    ├── conformance/
    │   ├── package_conformance_suite.py       # every package must pass this
    │   ├── test_manifest_completeness.py
    │   ├── test_capability_descriptor_validity.py
    │   ├── test_tool_effect_tags_present.py
    │   ├── test_no_tenant_data_in_package.py
    │   ├── test_declared_runtime_compatibility.py
    │   └── test_rubrics_are_deterministic.py
    │
    ├── contract/
    │   ├── test_model_provider_conformance.py
    │   ├── test_tool_protocol_conformance.py
    │   ├── test_storage_port_conformance.py
    │   └── test_plugin_protocol_conformance.py
    │
    ├── chaos/
    │   ├── test_kill_worker_mid_iteration.py
    │   ├── test_kill_worker_mid_action.py
    │   ├── test_lease_expiry_under_load.py
    │   ├── test_provider_timeout_storm.py
    │   └── test_poison_event_isolation.py
    │
    ├── performance/
    │   ├── test_context_assembly_latency.py
    │   ├── test_relay_throughput.py
    │   └── test_concurrent_session_scaling.py
    │
    ├── benchmarks/
    │   ├── task_sets/
    │   ├── test_pass_at_k_stability.py
    │   └── test_cost_per_success.py
    │
    └── end_to_end/
        ├── test_research_session.py
        ├── test_coding_session_with_approval.py
        ├── test_long_running_session.py
        └── test_evolution_round_with_promotion.py
```

---

## 8. Component reference

Each subsystem below is described the same way: **what it does**, **why it exists**, **how it
works**, and **what it must never do**. The last line matters most — an invariant nobody wrote down
is an invariant nobody preserves.

---

### 8.1 `contracts/` — the single source of truth

> Specifications for the five boundary contracts are in **§8**.

**What it does.** Defines every type that crosses a boundary: identifiers, the Execution Contract,
action identity, the event envelope, package manifests, verdicts, parks, budgets.

**Why it exists.** Without one shared vocabulary, every subsystem invents its own near-miss version
of "an action" and the translation layers between them become where the bugs live. This is the only
directory that imports nothing from the rest of the repository, which is what allows everything else
to depend on it without creating a cycle.

**How it works.** Frozen dataclasses with full type hints. `schemas/json_schema_exporter.py` emits
JSON Schema into `schemas/generated/` at build time, so external clients, the plugin SDK and the
config validator all derive from the same definitions rather than restating them.

**Never.** Never contains behaviour. Never imports a provider, a store, or a runtime module.

---

### 8.2 `gateway/` — ingress

**What it does.** Accepts goals, approvals and signals; streams views back. Nothing else.

**Why it exists.** To keep the request path away from the work path. A session runs for hours; an
HTTP connection does not. This layer converts intent into durable facts and durable facts into a
view, and it participates in neither direction.

**How it works.** Inbound requests pass `auth → tenancy → rate limit → validation → idempotency
key` and terminate in a command write. Outbound, `read_model_projector.py` builds a `RunView`
carrying a monotonic `seq`; clients hydrate from it and *then* subscribe from that cursor.
`hydrate_then_subscribe.py` in the SDK makes it structurally impossible for a client to render from
stream frames alone — which is what stops a reconnect showing a blank panel.

**Never.** Never runs the loop. Never runs an event consumer — an edge process is recycled on every
deploy, and a consumer there abandons claimed events each release. Never calls a model.

---

### 8.3 `runtime/ports/` — the extension surface

**What it does.** Declares every interface the kernel depends on, as `Protocol` classes.

**Why it exists.** This is the seam that makes the kernel domain-agnostic and testable. Because
`clock_port.py` and `random_port.py` are here, non-determinism is injectable, and a replay can be
made byte-identical.

**How it works.** Structural typing — an adapter satisfies a port by shape, so `models/` and
`storage/` never import the kernel to declare conformance. Conformance is proven by
`tests/contract/`.

**Never.** Never contains an implementation. If a port file has a function body longer than a
`...`, something has gone wrong.

---

### 8.4 `runtime/context/` — parallel context assembly

**What it does.** Issues eight independent reads concurrently and returns one `ContextBundle`.

**Why it exists.** Sequential assembly makes total latency the sum of every read. Concurrent
assembly makes it the slowest single read. On a bundle that touches session history, world state,
memory, package config and policies, that is the difference between four seconds and four hundred
milliseconds.

**How it works.** `assembly_plan_builder.py` computes which sources are needed for this iteration;
`parallel_context_assembler.py` fans out with a hard deadline per source, and
`assembly_timeout_guard.py` degrades gracefully — a slow memory store yields a bundle marked as
partial rather than failing the iteration. `token_budget_allocator.py` then apportions the context
window across sources by priority, and `cache_prefix_builder.py` keeps the leading segment stable so
the provider can reuse it.

**Never.** Never mutates what it reads. Never persists the bundle as truth — it is *derived*, and
persisting it breaks replay after any change to the compaction policy.

---

### 8.5 `runtime/intelligence/decision/` — the Decision Engine

> Execution Contract schema: **§9.5**.

**What it does.** One structured inference per iteration, producing one Execution Contract.

**Why it exists.** In an unstructured tool-calling loop the decision exists only as a side effect of
the tokens that caused it — you cannot log it, diff it, validate it, or replay it. Making the
decision a typed artifact turns the most important step in the system into something auditable.

**How it works.** `decision_prompt_composer.py` renders the bundle into a prompt;
`structured_output_requester.py` requests a schema-constrained response;
`execution_contract_parser.py` parses it and `execution_contract_validator.py` rejects malformed or
internally inconsistent contracts. `confidence_thresholder.py` compares the declared confidence
against the package's threshold and routes low-confidence results to
`clarification_emitter.py` rather than executing on a guess. `decision_fallback_strategy.py` handles
the case the design does not yet address: what to do when parsing fails twice.

**Never.** Never executes a tool. Never writes memory. Never updates state. These three are
currently prose in the specification — enforce them by construction: hand the router a read-only
context and no tool or store handle at all, so violating the rule is a type error.

---

### 8.6 `runtime/policy/` — the guardrail engine

**What it does.** Validates a contract before anything can act on it, emitting a
`ValidatedExecutionContract` or refusing.

**Why it exists.** Placement is the whole point. Between decision and execution is the only position
where a check can be both informed by the full intent and still able to prevent it.

**How it works.** `permission_evaluator.py` and `tenancy_isolation_check.py` establish who may do
what. `effect_tag_enforcer.py` reads each action's tool descriptor and, for anything tagged
`EFFECTFUL`, requires a resolved approval reference before the contract may be validated at all —
this is structural, not advisory. `budget_admission_check.py` calls into `runtime/budget/` to test
the projected reservation against the remaining ceiling.

**Never.** Never modifies the goal. Never executes. Never grants an approval itself.

---

### 8.7 `runtime/identity/` — content-addressed action identity `[+]`

**What it does.** Answers one question: *has this exact action already run, and what did it cost?*

**Why it exists.** It is the precondition for replay, for safe retry, and for principles 16 and 17.
Without it, a retry re-executes and re-spends, and — worse — a re-planned iteration can inherit a
result computed for a different plan, producing a well-formed, confident, wrong output with no error
and no alert.

**How it works.** `canonical_input_serializer.py` produces a deterministic byte representation of
resolved inputs; `input_digest_builder.py` hashes it; `action_identity_computer.py` combines
`session_id`, `contract_id`, `action_id`, `tool_id` and that digest. The identity is computed at
**plan time**, not dispatch time, so it is auditable and dispatch cannot silently disagree with
planning about what an action is. `identity_match_classifier.py` returns `FULL`, `PARTIAL` or `MISS`;
a `PARTIAL` — same session and position, different contract or inputs — is routed to
`partial_match_alerter.py`, because that bug class is silent by nature and must page rather than log.

**Never.** Never derives identity from position alone. That single shortcut is the most expensive
defect available in this architecture.

---

### 8.8 `runtime/leasing/` — ownership and recovery `[+]`

**What it does.** Guarantees exactly one controller advances a session at any instant, and makes a
crashed worker recoverable.

**How it works.** `lease_claimer.py` issues a single statement that sets the lease owner, extends
the expiry and increments a version, conditional on the expected version and an unheld-or-expired
lease. Zero rows returned means someone else owns it, so this worker drops the job — a lost update
rather than a corruption. `lease_renewer.py` extends at each checkpoint;
`lease_expiry_sweeper.py` runs **continuously**, because a sweeper that runs only at process start
will never notice the session stranded four hours in.

**Never.** Never held across a model call. The lease is a row with an expiry, not a held connection.

---

### 8.9 `runtime/parking/` — durable waiting `[+]`

**What it does.** Turns "waiting" into a row that holds nothing.

**Why it exists.** `HUMAN_LOOP` as an execution strategy implies something is waiting. If that
something is a worker, a person taking six hours costs six hours of a worker. A park writes the
question, releases the lease, and the session stops existing as anything but a row.

**How it works.** Five handlers, one mechanism. Approval, missing input, timer, external callback
and budget grant differ only in resolution condition. Resolution arrives as an ordinary event, flows
through the relay like any other fact, and wakes the session at exactly the step it left.
`park_age_escalator.py` ensures a park is never silently abandoned — past a policy threshold it
escalates or expires.

**Never.** Never holds a process, a connection, or an in-memory timer.

---

### 8.10 `runtime/budget/` — reserve then settle `[+]`

**What it does.** Debits projected cost at dispatch and reconciles actual cost at completion.

**Why it exists.** A budget *check* permits a session to exceed its ceiling by the cost of
everything currently in flight. With several concurrent model calls that is not a rounding error.

**How it works.** `cost_estimator.py` projects maximum tokens × price; `reservation_writer.py`
debits in the same transaction as the lease claim; `settlement_writer.py` replaces the reservation
with the actual and releases the difference; `reservation_expirer.py` ensures a reservation dies with
its lease on a crash. If the remaining ceiling is smaller than the reservation, the session parks
awaiting a budget grant — which is an approval, not new machinery. `drift_monitor.py` watches the gap
between reservation and settlement, because a persistent drift means the estimates are wrong and
therefore the admission decisions are too.

---

### 8.11 `runtime/controller/` — the control plane

**What it does.** Deterministic orchestration: dispatch, schedule, checkpoint, recover, cancel.

**How it works.** `deterministic_runtime_loop.py` claims a lease, advances a bounded number of
steps, and checkpoints after each. `signal_reader.py` reads pending control signals **in the same
transaction as the checkpoint**, so steering costs zero additional round trips.
`iteration_exit_evaluator.py` exits on any of four conditions: wall-clock budget, step budget, a
required park, or an arrived signal. `work_class_router.py` keeps cheap decisions off the queue that
carries model calls.

**Never.** Never calls an LLM. Never executes a tool. Never plans. Never holds a scarce resource
across a dispatch — `runtime/resources/connection_custody_guard.py` exists to make that violation
detectable.

---

### 8.12 `runtime/execution/` — the data plane

**What it does.** Performs the work. All non-determinism lives here and nowhere else.

**How it works.** `strategy_dispatcher.py` selects one of seven strategies from the validated
contract; the planner is invoked only by `plan_strategy.py`. `tool_runner.py` claims by identity,
reserves budget, acquires a semaphore slot, executes, settles, and appends a result event.
`timeout_enforcer.py` and `abort_signal_propagator.py` implement the rule that a deadline must abort
the *real* call — a timeout that merely abandons the caller leaks the operation and lets its effects
land after everyone has given up. `middleware_pipeline.py` provides the four hooks around model and
tool calls, which is the only place with a view across steps and therefore the only place that can
notice a repeating failure.

**Never.** Never decides what to do next. Never writes domain truth without a validated contract.

---

### 8.13 `runtime/observation/` — verification before knowledge

**What it does.** Observation → verification → evaluation → learning candidate → publish.

**Why it exists.** A model asked to evaluate its own work shares a training distribution, and
therefore a set of blind spots, with the model that produced it. It will approve fluent,
well-structured, wrong output because that is what it was trained to prefer. This is the failure
most likely to damage a product, because a reliability defect produces an alert and a confidently
wrong result produces an artifact someone acts on.

**How it works.** `deterministic_verifier.py` runs checkable predicates — does the patch apply, do
the tests pass, do the cited sources resolve, do the totals reconcile. `model_judgment_applier.py`
may then **downgrade** a passing check set and may **never upgrade** a failing one.

**Never.** Never blocks the user response. Never lets an unverified observation reach the knowledge
system.

---

### 8.14 `runtime/events/` — the spine

**What it does.** Appends immutable facts and turns them back into work.

**How it works.** `transactional_outbox_writer.py` commits a state change and its event in one
transaction — the only durability primitive the architecture requires. `claim_based_relay.py` marks
rows rather than tracking a cursor, one in flight per partition: N workers with zero coordination,
and a poison event that blocks one partition instead of stalling every tenant.
`replay_determinism_guard.py` asserts that a replay produces the same decisions.

**Never.** Never carries progress. Streaming tokens and heartbeats have no business meaning and no
consumer needing durability; writing them here bloats the log, the relay, the audit trail and the
replay path with data nobody will read again.

---

### 8.15 `knowledge/` — world state, memory, artifacts

**What it does.** Holds what the system believes, what it has learned, and what it has produced.

**How it works.** `world/` models entities, facts and relationships — and, unusually and correctly,
**unknowns and assumptions as first-class records with confidence**. Most designs store only what is
believed, leaving no way to detect staleness or to know what the system failed to find out;
`staleness_detector.py` and `belief_invalidator.py` depend on that record existing.

In `memory/`, `tenant_abstraction_guard.py` sits on the write path and enforces the rule that a
lesson must be true of the **system**, never of a customer. Abstraction happens at write time
because filtering at read time is already too late — the leak is by then committed to a versioned
file. `curation_policy.py` and `memory_pruner.py` exist because memory grows with edits rather than
usage: it never becomes slow, it becomes diluted, and nothing alerts.

---

### 8.16 `learning/` — the asynchronous pipeline

**What it does.** Collects trajectories, distils patterns, generates candidates, runs benchmarks.

**Why it exists.** Reflection inside the request loop spends the user's latency budget on work that
has no deadline. Moving it out is one of the better decisions in this architecture.

**How it works.** `trajectory_redactor.py` redacts at capture. `distillation/` compresses millions of
raw tokens into a structured evidence corpus with per-task root-cause reports and one overview, so
downstream consumers read structured causes rather than raw logs.
`analytics/human_latency_separator.py` splits machine time from parked time — without it, a change
that causes more approvals looks like a change that made the system slower.

**Never.** Never blocks the request path. Never writes to `knowledge/` without verification.

---

### 8.17 `packages/` — domain behaviour, and the harness

> Manifest schema: **§9.2**. Conformance suite: `tests/conformance/`.

**What it does.** Carries everything domain-specific: prompts, enabled capabilities, policies,
templates, knowledge, skills, memory configuration, evaluation rubrics, workflows.

**Why it matters more than it looks.** This set is exactly the editable component surface that
harness-evolution research operates on. Naming it as such collapses two problems into one: the
evolvable surface and the replaceable surface become the same surface, and *"the runtime never
modifies itself"* becomes checkable — evolution writes here and nowhere else.

**How it works.** `registry/version_pinner.py` pins a package version against a **model identity**,
because a harness fitted to one model underperforms on another. A model upgrade is therefore a
package-invalidation event by construction rather than by discipline.

**Never.** Never contains kernel logic. Never contains anything true of one customer rather than of
the system.

---

### 8.18 `capabilities/` and `tools/` — WHAT and HOW

> Descriptor schemas: **§9.3** and **§9.4**.

**What they do.** A capability declares an outcome that can be accomplished. A tool performs the
work. One capability may bind to several tools; swapping the tool does not change the capability.

**Why the split earns its place.** It lets a package declare intent without binding to an
implementation, and it gives the router a vocabulary at the right altitude — it selects a
*capability*, not a *shell command*.

**How tools work.** Every tool ships a descriptor with an `effect` tag of `PURE` or `EFFECTFUL`.
`effect_tag_auditor.py` fails the build on an untagged tool, and
`mcp/mcp_effect_inferencer.py` defaults an unknown third-party tool to `EFFECTFUL` — the safe
direction. `error_message_formatter.py` exists because a tool's error message is the model's primary
feedback channel, and shaping it well is measurably worth more than most prompt work.

---

### 8.19 `evolution/` — proposes, never promotes

**What it does.** Reads trajectories, proposes package edits with predicted outcomes, measures them
against the next round, and asks a human before anything is promoted.

**How it works.** `experiment_manager/variable_isolator.py` holds the base model fixed and isolates
one variable per round, because without that no delta is attributable.
`evolution_agent/workspace_boundary_guard.py` restricts every write to `packages/`.
`manifest/change_entry_builder.py` records, per edit: the failure evidence, the inferred root cause,
the targeted fix, the component level chosen and why, the tasks it predicts will be fixed, and the
tasks it believes are at risk. `attribution/prediction_intersector.py` compares those predictions
against the next round's actual deltas and `verdict_assigner.py` returns `KEEP`, `IMPROVE` or
`ROLLBACK_AND_PIVOT`.

**The limit to design around.** `self_attribution_scorer.py` exists because such loops predict their
*fixes* far better than chance but their *regressions* barely better than chance. The loop can
justify why an edit should help; it cannot reliably name what the same edit is about to break.
Assume the human at `rollout/human_approval_gate.py` is the only real defence against regressions,
and give them the manifest, the diff and the delta — not a score.

---

---

### 8.20 `runtime/capability_executor/` — the middle loop `[+]`

**What it does.** Executes one capability end to end: loads it, builds its local context, resolves
its tools, runs its internal graph, and returns **one structured observation**.

**Why it exists.** Without it the Controller must name concrete tools, which couples the Decision Engine to
implementations, turns one intent into five contract actions, and leaves capability-internal retry
with nowhere to live. See §5.1.

**How it works.** `capability_invoker.py` is the Controller's only execution verb.
`capability_context_builder.py` slices the global ContextBundle down to what this capability's
descriptor declares it needs — a Git capability gets repository, branch, remote and credentials; a
research capability gets sources and citation rules. `capability_graph_builder.py` produces the
internal tool graph, and `observation_aggregator.py` collapses N tool results into one observation
so the Decision Engine's context fills with conclusions rather than transport detail.
`partial_result_reconciler.py` handles the common case where three of five tool calls succeeded.

**Never.** Never decides *which* capability to run — that is the Decision Engine's. Never leaks raw tool
payloads upward.

---

### 8.21 `runtime/capability_executor/` — the inner-loop manager `[+]`

**What it does.** Turns an intent into concrete tool calls and manages their execution: resolution,
chaining, parallelism, retry, fallback, caching, timeouts, partial failure.

**How it works.** `intent_resolver.py` queries `tools/tool_capability_index.py` for tools satisfying
an intent — the registry is asked *which tool supports searching issues*, rather than the runtime
hardcoding `jira.search`. `binding_selector.py` picks one and `binding_pinner.py` writes it into the
invocation identity, which is what keeps dynamic discovery compatible with replay (§9.5.3).
`parameter_mapper.py` translates intent parameters into each tool's input schema.
`tool_fallback_selector.py` may re-resolve when a pinned tool is unavailable — and that mints a new
identity rather than substituting silently.

**Never.** Never chooses a capability. Never replays a `NON_IDEMPOTENT` tool result.

---

### 8.22 `runtime/controller/execution_graph/` — mission state `[+]`

**What it does.** Tracks every node of the current plan through
`PENDING → READY → RUNNING → {DONE | FAILED | BLOCKED | SKIPPED | COMPENSATING}`, and answers
*what can run now*, *what are we waiting on*, and *how far along are we*.

**Plan versus graph — a distinction worth holding.** The **plan** is what the Decision Engine or Planner
proposed: declarative, immutable, superseded by a replan. The **graph** is the Controller's stateful
projection over it. A replan writes a new plan and a new graph; the old graph is retained as history.

**How it works.** `dependency_scheduler.py` and `ready_set_calculator.py` compute which nodes are
runnable given completed dependencies, which is what makes safe parallel dispatch a static decision.
`blocked_reason_resolver.py` distinguishes *blocked awaiting approval* from *blocked awaiting budget*
from *blocked on a failed dependency* — three different operator responses that look identical
without it. `pause_resume_controller.py` makes the graph the resumption point after a park.

**Never.** Never executes anything. It is a state machine, not a runner.

---

### 8.23 `runtime/experience/` — execution state as a stream `[+]`

**What it does.** Subscribes to durable TRACE events and produces two derived artifacts: a live
hierarchical progress tree, and the durable execution trace of §9.6.

**Why it replaces `runtime/streaming/`.** The old package streamed tokens and progress frames. This
one streams *what the runtime is doing*. Fully specified in §11.3.

**How it works.** `runtime_event_mapper.py` turns durable facts into runtime events;
`event_class_router.py` separates TRACE from PROGRESS from PRESENTATION; `progress_tree_builder.py`
maintains the nested tree; `encoders/` translate to AG-UI, native or OpenTelemetry GenAI formats at
the boundary.

**Never.** Never renders. Never writes a durable event of its own. Never invents a progress signal
that is not backed by a fact.

---

### 8.24 `runtime/manifest/` — the runtime's identity `[+]`

**What it does.** Loads, validates and fingerprints `runtime.manifest.yaml`, producing a
`RuntimeIdentity` that every session and every benchmark result is stamped with.

**Why it exists.** Two deployments that differ in package versions or model bindings are different
runtimes, and comparing measurements across them is meaningless. The fingerprint makes that
comparability machine-checkable instead of a matter of someone remembering.

**How it works.** `runtime_manifest_loader.py` reads the root manifest and applies the environment
overlay from `configs/manifests/`. `compatibility_gate.py` then checks every enabled package's
declared `supported_runtime` against the running version and **refuses to boot** on a mismatch —
failing at startup rather than later, in a way that would look like a model regression.
`manifest_fingerprint.py` hashes identity, models, packages, providers and features, deliberately
excluding `limits` so a capacity change does not read as a new runtime.

**Never.** Never mutated at runtime. A manifest change is a deployment, not a setting.

---

### 8.25 `runtime/distribution/` — many workers, one runtime `[+]`

**What it does.** Worker identity, heartbeat, partition ownership, rebalancing, drain and clock-skew
detection.

**Why it exists.** Stages 1 to 4 of §10.3 need nothing here — leases and claims already distribute the
work. This package exists for Stage 5, and to hold the reasoning in §10.2 about why leader election is
deliberately absent.

**How it works.** Ownership is an optimisation for locality, never a correctness dependency: wipe the
ownership table and the runtime falls back to open contention on leases and keeps working.
`clock_skew_detector.py` compares worker time against substrate time on each heartbeat and refuses to
claim past a threshold, because lease expiry must be judged by one clock — the database's.

**Never.** Never a coordination point without which nothing advances.

---

### 8.26 `diagnostics/` — developer-facing introspection `[+]`

**What it does.** Six surfaces answering *why did this session do that*: execution timeline, prompt
viewer, event explorer, checkpoint explorer, trajectory viewer, replay viewer.

**Why it is not telemetry.** Different consumer, different question, different cardinality, different
retention, and — critically — different access control. Diagnostics exposes prompts, tool payloads
and trajectory content, so every read is audited.

**How it works.** The load-bearing rule is in `assembled_prompt_reconstructor.py`: prompts are
**rebuilt from stored state, never persisted**. Storing them would create a second source of truth
that breaks replay after any compaction change, and would double the surface holding customer data.
`machine_vs_parked_splitter.py` separates worker time from waiting time, without which a healthy
six-hour session and a runaway one look identical.

**Never.** Never stores derived state. Never shares an access boundary with telemetry.

## 9. Core specifications

Five contracts cross component boundaries. Everything else is internal. These are `NORMATIVE` in
full: a change to any field here is an architectural change and requires an ADR.

| Spec | Answers | Owned by | Schema |
|------|---------|----------|--------|
| §9.1 Runtime Manifest | *What is this deployment?* | `runtime/manifest/` | `runtime_manifest_schema.json` |
| §7.2 Package Manifest | *What does this package provide?* | `packages/registry/` | `package_manifest_schema.json` |
| §7.3 Capability Descriptor | *What can be accomplished, at what cost?* | `capabilities/` | `capability_descriptor_schema.json` |
| §7.4 Tool Descriptor | *How is it performed, and how dangerous is it?* | `tools/` | `tool_descriptor_schema.json` |
| §7.5 Execution Contract | *What did the router decide?* | `runtime/intelligence/decision/` | `execution_contract.schema.json` |

---

### 9.1 Runtime Manifest

**Purpose.** The identity of one deployed runtime. Not configuration — *identity*.

**Why it is separate from `configs/`.** Configuration holds tunables: pool sizes, log levels,
timeouts. Changing one does not change what the runtime *is*. The manifest holds the set of things
that, if changed, make two runtimes incomparable — package versions, model bindings, feature flags,
provider choices. This distinction is what makes an evolution measurement meaningful: a pass-rate
delta between two rounds means something only if the manifest fingerprint is identical apart from
the single variable under test.

**Location.** `runtime.manifest.yaml` at the repository root, deliberately alongside
`pyproject.toml`. Environment overlays live in `configs/manifests/` and may override only fields
marked overridable below.

```yaml
# runtime.manifest.yaml
apiVersion: runtime.universal/v1
kind: RuntimeManifest

identity:
  name: universal-runtime
  runtime_version: 1.0.0            # semver of the kernel itself
  deployment_id: prod-eu-1          # unique per running fleet
  environment: production

models:
  default_router_model:
    provider: anthropic
    model_id: <model-identifier>
    reasoning_effort: high          # overridable
  role_bindings:                    # each role may pin a different model
    router:      default
    planner:     default
    grader:      { provider: anthropic, model_id: <small-model-identifier> }
    summarizer:  { provider: anthropic, model_id: <small-model-identifier> }
  fallback_chain: [primary, secondary]

packages:                           # THE HARNESS SET — the evolvable surface
  - id: research
    version: 2.4.1
    enabled: true
  - id: coding
    version: 3.1.0
    enabled: true
  - id: devops
    version: 0.9.2
    enabled: false

providers:
  storage:
    relational: postgres
    cache: redis
    vector: pgvector
    blob: s3
    event_store: postgres
  telemetry:
    metrics: prometheus
    traces: otlp
    logs: structured_json
  plugins:
    - id: acme-crm-tools
      version: 1.2.0
      trust: third_party            # affects the default effect tag — see §7.4

features:                           # boolean only; no behaviour hidden behind values
  parallel_context_assembly: true
  speculative_capability_prefetch: false
  evolution_loop_enabled: false     # off in production by default
  diagnostics_web_ui: true

limits:                             # IMPLEMENTATION NOTE — starting points
  model_semaphore: 6
  fast_queue_concurrency: 12
  per_tenant_inflight_max: 3
  session_wall_clock_seconds: 3600
  iteration_step_budget: 8

compatibility:
  minimum_package_api: 1.0
  maximum_package_api: 1.x
```

**Fingerprint.** `runtime/manifest/manifest_fingerprint.py` produces a stable hash over
`identity.runtime_version`, every entry in `models`, every entry in `packages`, every entry in
`providers`, and all of `features`. `limits` is **excluded** — it is a tunable, and including it
would make every capacity change look like a new runtime.

**NORMATIVE.**
- The fingerprint is recorded on every session at creation and on every benchmark result.
- Two results may be compared only if their fingerprints differ in at most the variable under test.
- `runtime/manifest/compatibility_gate.py` refuses to start if any enabled package declares a
  `supported_runtime` range excluding `identity.runtime_version`. Failing at boot is the point:
  the alternative is failing later in a way that looks like a model regression.

---

### 9.2 Package Manifest

**Purpose.** The contract every package implements. Because packages are the harness, this is the
most consequential schema in the repository — it is simultaneously the extension format for third
parties and the action space for evolution.

```yaml
# packages/research/package.manifest.yaml
apiVersion: packages.universal/v1
kind: PackageManifest

id: research
version: 2.4.1
display_name: Research
description: Long-horizon investigation, source verification and reporting.
maintainers: [platform-team]

compatibility:
  supported_runtime: ">=1.0.0,<2.0.0"
  package_api: "1.0"
  model_affinity:                   # a harness is fitted to a model; say so
    tuned_for:
      provider: anthropic
      model_id: <model-identifier>
      reasoning_effort: high
    verified_on:
      - { provider: anthropic, model_id: <alternate-identifier>, pass_at_1: 0.71 }
    untested_warning: true          # warn at load on an unlisted model

prompts:
  system: prompts/system_prompt.md
  modules:                          # ordered; assembled by runtime/prompt/
    - prompts/research_discipline.module.md
    - prompts/source_verification.module.md
    - prompts/report_style.module.md

capabilities:
  enabled:
    - research.search
    - research.read
    - research.analyze
    - research.verify
    - research.report
  disabled_inherited: []

tools:
  allowed:                          # a package may narrow, never widen, the tool surface
    - tool.search.web_search
    - tool.browser.read_page
    - tool.filesystem.read_file
  denied:
    - tool.terminal.run_command

workflows:
  - workflows/literature_review.workflow.yaml

policies:
  - policies/source_policy.yaml
  - policies/budget_policy.yaml

skills:
  - skills/literature_sweep/SKILL.md
  - skills/claim_verification/SKILL.md

knowledge:
  static: knowledge/domain_facts.yaml

memory:
  config: memory/memory_config.yaml
  scope: shared                     # shared | per_tenant  — see §9.2.2
  abstraction_required: true

evaluation:
  rubrics: evaluation/rubrics.yaml
  benchmark_task_set: research_v3
  minimum_pass_at_1: 0.65           # promotion gate

templates:
  - templates/research_report.md
  - templates/source_table.md

evolution:
  evolvable_components:             # what an evolution round may touch in THIS package
    - prompts
    - skills
    - memory
    - policies
  frozen_components:                # what it may never touch
    - compatibility
    - evaluation
```

#### 7.2.1 Field rules

**NORMATIVE.**
- `tools.allowed` may only **narrow** the surface exposed by the enabled capabilities. A package
  that could widen it would be an escalation path.
- `evaluation.rubrics` is `frozen` by default. A harness that can edit its own grader can score
  itself, and every measurement afterwards is meaningless.
- `evolution.frozen_components` must always include `compatibility` and `evaluation`.

#### 7.2.2 Memory scope — the field that prevents a specific incident

`memory.scope` has two values and no default. **A missing value is a validation failure**, because
the wrong default is a data leak.

| Value | Behaviour | Use when |
|-------|-----------|----------|
| `shared` | One memory namespace across all tenants. Requires `abstraction_required: true`. | Lessons are about the *system* — a build tool's quirk, a common failure shape. |
| `per_tenant` | One namespace per tenant. Lessons never cross. | Lessons are unavoidably specific. |

With `shared`, `knowledge/memory/tenant_abstraction_guard.py` sits on the write path and rejects any
lesson containing a tenant identifier, hostname, credential or customer name. The rule it enforces:
**a stored lesson must be true of the system, never of a customer.** Abstraction happens at write
time because filtering at read time is already too late — by then the leak is committed to a
versioned file, and `tests/conformance/test_no_tenant_data_in_package.py` will fail the build for
everyone.

#### 7.2.3 Compatibility policy

**NORMATIVE.** Runtime and packages version independently.

| Situation | Behaviour |
|-----------|-----------|
| Package `supported_runtime` includes the running version | Load normally |
| It does not | **Refuse to boot.** Named in the error, with the required range |
| `package_api` minor is older than the runtime's | Load, emit a deprecation warning |
| `package_api` major differs | Refuse to boot |
| Model is not in `model_affinity.tuned_for` or `verified_on` | Load, warn once, record on every session |

That last row exists because a harness tuned for one model underperforms on another. The warning is
what turns a silent, weeks-long quality regression into a line in a log on day one.

---

### 9.3 Capability Descriptor

**Purpose.** Declares an outcome that can be accomplished, independently of how. This is the
vocabulary the Decision Engine selects from — the right altitude for a decision, above shell commands and
below business goals.

```yaml
# capabilities/research/descriptors/verify.capability.yaml
apiVersion: capabilities.universal/v1
kind: CapabilityDescriptor

id: research.verify
display_name: Verify a claim against sources
description: >
  Given a claim and candidate sources, determine whether the sources support it,
  contradict it, or are insufficient.

inputs:
  schema: schemas/verify.input.json
  required: [claim, sources]
  optional: [strictness]

outputs:
  schema: schemas/verify.output.json
  guarantees:
    - every returned verdict cites at least one retrieved source
    - a source that failed to fetch is reported, never silently dropped

required_tools:                     # capability -> one or more tools
  any_of:
    - [tool.search.web_search, tool.browser.read_page]
    - [tool.filesystem.read_file]

permissions:
  - network.read
  - package.knowledge.read

execution_mode: PARALLEL_SAFE       # SEQUENTIAL_ONLY | PARALLEL_SAFE | EXCLUSIVE
idempotent: true
side_effects: none

cost_estimate:                      # drives BUDGET RESERVATION, not just reporting
  model_calls: { typical: 2, maximum: 5 }
  tokens:      { typical: 18000, maximum: 60000 }
  currency:    { typical: 0.11, maximum: 0.38 }

latency_estimate:
  p50_seconds: 9
  p95_seconds: 34
  timeout_seconds: 120

failure_modes:
  - id: sources_unreachable
    retryable: true
    backoff: exponential
  - id: claim_ambiguous
    retryable: false
    action: request_clarification

observability:
  deterministic_checks:
    - all_citations_resolve
    - no_self_citation                # the model's own earlier output is not a source
```

**Why `cost_estimate` and `latency_estimate` are required, not optional.**

**NORMATIVE.** Without them the Policy Engine cannot reserve budget, and a budget *check* permits a
session to exceed its ceiling by the cost of everything already in flight. `maximum` is the value
`runtime/budget/reservation_writer.py` debits at dispatch; `typical` is what
`runtime/budget/spend_projector.py` uses to project a session's total before it starts.
`runtime/budget/drift_monitor.py` compares reserved against settled, and a persistent drift means
these numbers are wrong and therefore the admission decisions built on them are wrong too.

`latency_estimate.p95_seconds` feeds the planner's time budgeting, and `timeout_seconds` becomes the
deadline that `runtime/execution/abort_signal_propagator.py` enforces — a real abort of the
underlying call, not an abandoned wait.

**`execution_mode`** is what makes parallel dispatch safe to decide statically. `PARALLEL_SAFE`
capabilities may be fanned out by `parallel_fanout_executor.py`; `EXCLUSIVE` ones may not run
alongside anything else in the same session.

---

### 9.4 Tool Descriptor

**Purpose.** Declares how work is performed and how dangerous it is. Every field below is required.

```yaml
# tools/github/descriptors/push_branch.tool.yaml
apiVersion: tools.universal/v1
kind: ToolDescriptor

id: tool.github.push_branch
display_name: Push a branch
description: >
  Push a local branch to the remote repository. Visible to the customer immediately.

effect: EFFECTFUL                   # PURE | EFFECTFUL  — the whole safety model
reversible: false
blast_radius: repository            # sandbox | session | tenant | repository | external

idempotency:
  class: CONDITIONAL                # IDEMPOTENT | CONDITIONAL | NON_IDEMPOTENT
  condition: >
    Idempotent only when the remote ref already points at the same commit sha.
  key_fields: [repository, branch, commit_sha]

input:
  schema: schemas/push_branch.input.json

output:
  schema: schemas/push_branch.output.json
  truncation:
    max_bytes: 16384
    strategy: head_and_tail

permissions:
  - repository.write
  - credentials.git

approval:
  required: true                    # implied by effect: EFFECTFUL, stated for readability
  question_template: templates/push_branch_approval.md
  approver_role: repository_maintainer

retry:
  policy: none                      # NON-idempotent writes are not auto-retried
  max_attempts: 1

timeout:
  seconds: 60
  on_timeout: abort_and_report      # abort the real call; never abandon the wait

errors:
  - code: remote_rejected
    retryable: false
    model_guidance: >
      The remote refused the push. Read the rejection reason before retrying;
      a force push requires a separate, explicitly approved action.
  - code: auth_failed
    retryable: false
    model_guidance: Credentials are missing or expired. Do not retry; escalate.
```

#### 7.4.1 Idempotency is a first-class field, and here is why

**NORMATIVE.** `idempotency.class` changes what the runtime is permitted to do with a stored result.

| Class | Replay behaviour on an identity hit | Retry on failure |
|-------|-------------------------------------|------------------|
| `IDEMPOTENT` | Replay the stored result freely | Safe, with backoff |
| `CONDITIONAL` | Replay only if `key_fields` still match the live world | Re-check the condition first |
| `NON_IDEMPOTENT` | **Never replay.** Escalate to a human instead | Never automatic |

This is the field that connects the descriptor to `runtime/identity/`. Action identity tells you
*this has run before*; idempotency class tells you *whether that fact is safe to act on*. A design
with the first and not the second will confidently replay a payment.

#### 7.4.2 Effect tagging rules

**NORMATIVE.**
- Every tool declares `effect`. `tools/effect_tag_auditor.py` fails the build on an omission.
- `EFFECTFUL` tools are structurally uncallable without a resolved approval reference — enforced in
  `runtime/policy/effect_tag_enforcer.py`, in the code path that constructs the invocation, never
  by instructing the model.
- Third-party and MCP tools of unknown effect default to `EFFECTFUL`
  (`tools/mcp/mcp_effect_inferencer.py`). The safe direction is the annoying one.
- `blast_radius` is advisory today and exists so that policy can later scale approval requirements
  to consequence.

#### 7.4.3 `model_guidance` on errors

**IMPLEMENTATION NOTE**, but a high-value one. A tool's error message is the model's primary feedback
channel. `model_guidance` is written *for the model*, not for a human reading logs, and shaping it
well is measurably worth more than most prompt work — it is the difference between an agent that
retries blindly and one that changes tactic.

---

### 9.5 Execution Contract

**Purpose.** The single artifact the Decision Engine produces per iteration. **This is the centrepiece of the
architecture** — the thing that makes an autonomous decision auditable — and it was previously named
without being specified.

```jsonc
{
  "contract_id":   "ctr_01HQ8...",        // minted per inference; part of every action identity
  "session_id":    "ses_01HQ7...",
  "iteration":     4,
  "manifest_fingerprint": "rmf_9c2a...",  // which runtime produced this
  "created_at":    "2026-08-03T09:14:22Z",

  "goal": {
    "statement": "Resolve the failing test in acme/billing-service issue 412",
    "acceptance_criteria": [
      "the full test suite passes",
      "the change is limited to the module named in the issue"
    ],
    "amended_from": null                  // set when a steer forced a replan
  },

  "package":    { "id": "coding", "version": "3.1.0" },
  "capability": { "id": "coding.patch_authoring" },

  "execution_strategy": "PLAN",           // DIRECT PLAN WORKFLOW PARALLEL
                                          // BACKGROUND LONG_RUNNING HUMAN_LOOP

  "actions": [
    {
      "action_id":  "act_01",
      "tool_id":    "tool.filesystem.read_file",
      "inputs":     { "path": "src/billing/invoice.py" },
      "identity":   "aid_4f1c...",        // computed HERE, at plan time
      "depends_on": [],
      "effect":     "PURE",
      "estimated_cost": { "tokens": 1200, "currency": 0.004 }
    },
    {
      "action_id":  "act_02",
      "tool_id":    "tool.test.run_suite",
      "inputs":     { "target": "tests/billing" },
      "identity":   "aid_9b02...",
      "depends_on": ["act_01"],
      "effect":     "PURE",
      "estimated_cost": { "tokens": 0, "currency": 0.0 }
    }
  ],

  "clarification": null,                  // set INSTEAD of actions when confidence is low

  "confidence": {
    "score": 0.81,
    "basis": "issue text names the module and the failing assertion explicitly"
  },

  "reasoning_summary": "Read the named module, reproduce the failure, then patch.",

  "budget": {
    "reserved_currency": 0.42,            // sum of action maxima
    "session_remaining":  7.18
  },

  "metadata": {
    "router_model": "<model-identifier>",
    "context_bundle_digest": "cbd_77aa...",
    "prompt_fingerprint": "pfp_31de...",
    "assembly_partial": false             // true if a context source timed out
  }
}
```

#### 7.5.1 Rules

**NORMATIVE.**

1. **`contract_id` is minted per inference.** A replan produces a new contract, therefore new action
   identities, therefore no stale result from the previous plan can be inherited. This is what makes
   steering and idempotency one mechanism rather than two.
2. **`actions[].identity` is computed at plan time**, not at dispatch. It is auditable, and dispatch
   cannot silently disagree with planning about what an action is.
3. **`clarification` and `actions` are mutually exclusive.** A contract that both asks a question and
   proposes work is a validation failure.
4. **`manifest_fingerprint` is mandatory.** Without it a recorded contract cannot be interpreted
   later, because the packages and models that produced it are unknown.
5. **`assembly_partial: true` lowers the confidence ceiling.** A decision made on incomplete context
   may not claim high confidence; `confidence_thresholder.py` enforces the cap.
6. **The contract is persisted before any action runs.** A crash between decision and execution
   loses nothing and repeats nothing.

#### 7.5.2 What the contract is for

Four things become possible only because the decision is a typed artifact rather than a side effect
of token generation:

| | |
|---|---|
| **Audit** | Every autonomous decision has a record naming what was decided, on what basis, at what confidence, and by which runtime. |
| **Replay** | Re-running a session replays contracts rather than re-inferring them. |
| **Diff** | Two runs of the same task can be compared at the decision level rather than the token level — which is what makes divergence analysis tractable. |
| **Validation** | The Policy Engine can refuse a decision *before* it becomes an action. There is no equivalent moment in an unstructured tool-calling loop. |

### 9.5.3 Revision 3 — actions are capability invocations, not tool calls

The Execution Contract shown above named `tool_id` directly. **That is now wrong**, and the change
is the most consequential in this revision.

```jsonc
// BEFORE — the Decision Engine names a tool
{ "action_id": "act_01", "tool_id": "tool.filesystem.read_file", "inputs": {...} }

// AFTER — the Decision Engine names a capability and an intent
{
  "invocation_id": "inv_01",
  "capability_id": "git.repository_inspection",
  "intent":        "sync_and_read_history",
  "parameters":    { "branch": "dev", "history_depth": 10 },

  "resolved_binding": {                       // pinned AT PLAN TIME
    "tools": ["tool.terminal.run_command"],
    "binding_id": "bnd_7a3f...",
    "resolver": "intent_binding_table",
    "resolved_at": "2026-08-03T09:14:22Z"
  },

  "identity":  "cid_4f1c...",                 // capability invocation identity
  "depends_on": [],
  "effect":     "PURE",
  "estimated_cost": { "tokens": 1400, "currency": 0.005 }
}
```

#### The tension this creates, and how it is resolved

Dynamic tool discovery and content-addressed identity pull in opposite directions. If the registry
resolves `search_issues` to `jira.search` today and `jira.search_v2` tomorrow, two invocations with
identical parameters are **not** interchangeable — but a naive identity over
`(session, contract, invocation, parameters)` would treat them as a cache hit and replay the wrong
result.

**NORMATIVE — the resolution rule.**

1. **Bind at plan time.** `runtime/intelligence/binding/intent_resolver.py` resolves the intent to a concrete
   tool set before the contract is validated. The binding is written into `resolved_binding` and
   **hashed into the invocation identity**.
2. **Two-level identity.** The capability invocation carries `identity`; each tool call inside it
   carries its own action identity, derived from the invocation identity plus the tool and its
   resolved inputs.
3. **Execution-time re-resolution is permitted, and mints a new identity.** If the pinned tool is
   unavailable, `tool_fallback_selector.py` may re-resolve — and the result is a *different*
   invocation with a *different* identity, recorded as an `intent.rebound` event. It is never a
   silent substitution under the old identity.
4. **A binding change invalidates a cache entry.** This falls out of rule 1 automatically, which is
   the point of putting the binding in the hash rather than checking it separately.

This preserves both properties the design needs: the Decision Engine stays implementation-agnostic, and
replay stays sound. Without rule 1 the system would confidently replay a result produced by a tool
that no longer exists.

**IMPLEMENTATION NOTE.** Plan-time binding also makes cost estimation possible — you cannot reserve
budget for an intent whose implementation is unknown.

---

### 9.6 Execution Trace

**Purpose.** The durable, structured record of what a session actually did. It replaces
*"ran 6 commands"* with something a human can read and a machine can diff.

**Why it is a contract rather than a log.** The trace is consumed by three different readers — the
diagnostics UI, the distillation pipeline, and the evolution attribution step — and all three need
the same shape. A log format that drifts breaks all three silently.

```jsonc
{
  "trace_id":   "trc_01HQ8...",
  "session_id": "ses_01HQ7...",
  "manifest_fingerprint": "rmf_9c2a...",
  "started_at": "2026-08-03T09:14:19Z",
  "ended_at":   "2026-08-03T09:14:47Z",
  "outcome":    "GOAL_COMPLETED",

  "iterations": [
    {
      "iteration": 1,
      "contract_id": "ctr_01HQ8...",
      "router": { "duration_ms": 1840, "tokens": 12400, "confidence": 0.81 },

      "capabilities": [
        {
          "invocation_id": "inv_01",
          "capability_id": "git.repository_inspection",
          "intent": "sync_and_read_history",
          "identity": "cid_4f1c...",
          "state": "DONE",
          "duration_ms": 2140,

          "tools": [
            { "tool_id": "tool.terminal.run_command",
              "summary": "git checkout dev",
              "identity": "aid_a1...", "state": "DONE",
              "duration_ms": 310, "attempts": 1, "replayed": false },
            { "tool_id": "tool.terminal.run_command",
              "summary": "git pull",
              "identity": "aid_b2...", "state": "DONE",
              "duration_ms": 1490, "attempts": 1, "replayed": false },
            { "tool_id": "tool.terminal.run_command",
              "summary": "git log -10",
              "identity": "aid_c3...", "state": "DONE",
              "duration_ms": 340, "attempts": 1, "replayed": false }
          ],

          "observation": {
            "summary": "Repository on dev at 4f1c9e2; 10 commits read.",
            "verified": true,
            "checks_passed": ["branch_matches_request", "working_tree_clean"]
          }
        }
      ],

      "cost": { "tokens": 13800, "currency": 0.052 },
      "graph_state": { "done": 3, "running": 0, "blocked": 0, "pending": 2 }
    }
  ],

  "totals": {
    "iterations": 3, "capabilities": 4, "tool_calls": 9,
    "machine_time_ms": 8420,
    "parked_time_ms": 0,
    "wall_clock_ms": 28100,
    "tokens": 41200, "currency": 0.164,
    "replayed_actions": 0
  }
}
```

**NORMATIVE.**
- `machine_time_ms` and `parked_time_ms` are separate fields and both are required. A trace that
  reports only wall clock cannot distinguish a healthy session waiting on a human from a runaway one.
- Every tool span carries `replayed`. A trace where replays are invisible cannot be used to verify
  that identity is working.
- Tool spans carry a `summary`, never the raw payload. Payloads live in the trajectory store under
  the diagnostics access boundary.

---

### 9.7 Runtime event taxonomy

**Purpose.** Three classes of event with three different durability rules. Conflating them is what
produces either a bloated event log or a UI that cannot be rebuilt after a reconnect.

| Class | Example | Durable? | Consumer |
|-------|---------|----------|----------|
| **TRACE** | `capability.completed`, `action.completed`, `iteration.completed`, `checkpoint.written`, `approval.decided` | **Yes** — these are facts, they go through the outbox | the runtime, the trace, evolution |
| **PROGRESS** | `context.loading`, `capability.selected`, `tool.started`, percent complete | **No** — *derived* from trace events by the Experience layer | live UI |
| **PRESENTATION** | spinner frame, tree node collapsed, artifact ready | **No** — pure rendering state | the renderer only |

**NORMATIVE.**

1. **The Experience layer introduces no new durable event class.** It subscribes to TRACE events and
   derives PROGRESS from them. This preserves invariant I20 — progress never enters the event log —
   while still giving a live, detailed UI.
2. **Because progress is derived, it is reconstructible.** `progress_snapshot_builder.py` can rebuild
   the entire progress tree at any point from the durable trace, which is what makes reconnect work:
   the client hydrates a snapshot, then subscribes. Same pattern as the read model in the gateway,
   applied to execution state.
3. **No component writes to a terminal, a socket, or a UI.** Everything flows
   component → TRACE event → Experience layer → encoder → renderer. A `print()` in the execution
   engine is a defect, and `test_only_renderers_write_to_surface.py` fails the build for it.

#### 8.7.1 Alignment with external standards

**IMPLEMENTATION NOTE**, but adopting rather than inventing is worth doing deliberately here. Two
external vocabularies are relevant and the runtime speaks both at its edges while keeping its own
internal vocabulary.

**OpenTelemetry GenAI semantic conventions** — `encoders/otel_genai_exporter.py`.
<cite index="12-1">The conventions define a span tree with a top-level `invoke_agent` span, child `chat` spans for each model call and `execute_tool` spans for each tool invocation, carrying attributes such as `gen_ai.request.model`, `gen_ai.usage.input_tokens` and `gen_ai.response.finish_reasons`.</cite> This maps onto the three loops almost exactly: an iteration is an `invoke_agent` span, a Router pass is a `chat` span, a tool call is an `execute_tool` span, and a capability invocation sits between them as an intermediate span.

One convention detail is worth adopting as a rule rather than a suggestion. <cite index="14-1">Storing full prompt text in span attributes is treated as an anti-pattern — attributes are always indexed, have size limits, and expose sensitive content in the backend — so the conventions place content in span events instead, where it can be filtered or dropped at the Collector without touching application code.</cite> That is the same conclusion §11 reaches from the diagnostics side, arrived at independently: telemetry carries measurements, and content lives behind a separate access boundary.

**AG-UI (Agent-User Interaction Protocol)** — `encoders/agui_event_encoder.py`. <cite index="22-1">AG-UI is an open, event-based protocol connecting an agentic frontend to any agentic backend, covering live event streaming with cancel and resume, tool result streaming, nested delegation with scoped state and tracing, human-in-the-loop pause and approval, and mid-flight redirection of execution.</cite> <cite index="23-1">Agent backends emit events matching roughly sixteen standard types, over any transport — server-sent events, WebSockets or webhooks.</cite>

The mapping is close enough to be worth honouring:

| Universal Runtime | AG-UI |
|-------------------|-------|
| `session.started` / `goal.completed` | run lifecycle start / finish |
| `action.dispatched` / `action.completed` | tool call lifecycle events |
| `progress_tree_snapshot` | state snapshot — the hydrate half of reconnect |
| `signal(kind=CANCEL \| STEER)` | interrupt and mid-flight redirection |
| `approval.requested` / `approval.decided` | human-in-the-loop checkpoint |

**NORMATIVE.** AG-UI is a **wire format at the edge, not an internal vocabulary.** The kernel emits
its own events; `agui_event_encoder.py` translates at the boundary. This keeps a third-party protocol
version out of the kernel's dependency graph while giving any AG-UI-compatible frontend
interoperability for free — and if the protocol changes, one encoder changes.

**What is deliberately not adopted:** AG-UI's token-level `TEXT_MESSAGE_CONTENT` streaming is
supported only for the final response. The runtime does not stream model tokens as a progress
indicator, for the reason in §11.3 — token streams are not execution state.

---
### 9.8 ExecutionNode

**Purpose.** The unit of the ExecutionGraph. Every execution style in the runtime — linear,
parallel, conditional, retried, timed out, approved, checkpointed, dynamically inserted — is
expressed with these fields and no others. There is no second node type hierarchy and no escape
hatch.

```yaml
# contracts/graph/execution_node.py  — logical shape
id:              n3                          # unique within the graph generation
name:            "Check Jira write permission"
type:            CAPABILITY                  # CAPABILITY | CONDITION | APPROVAL
                                             # CHECKPOINT | PARALLEL_GROUP | TERMINAL
status:          PENDING                     # §6.3

# what this node does — a capability and an intent, never a tool
capability:      jira.permission_check
intent:          check_write_access
parameters:      { project: ACME }

# the PINNED binding, resolved deterministically before the policy gate  §9.5.3
tool_chain:
  - tool_id: tool.jira.get_my_permissions
    binding_id: bnd_7a3f...
  - tool_id: tool.jira.list_projects
    binding_id: bnd_9c1e...

identity:        nid_4f1c...                 # hash(graph_generation, node, capability,
                                             #      intent, params, tool_chain bindings)

dependencies:    [n2]                        # the join. no separate join node exists.
condition:                                   # §6.5 — evaluated by the Controller
  expression:    "nodes.n2.observation.access_granted == true"
  on_false:      SKIP                        # SKIP | BLOCK | FAIL
parallel_group:  null                        # optional hint; does NOT create concurrency

retry_policy:                                # §6.6 — owned by the Controller
  max_attempts:  3
  backoff:       exponential
  retry_on:      [transient, timeout, rate_limited]
  never_retry_on:[policy_denied, non_idempotent_effect]

timeout:
  node_ms:       120000
  on_timeout:    RETRY                       # RETRY | FAIL | ESCALATE

approval_policy: null                        # populated on type: APPROVAL  §6.8

checkpoint:                                  # §6.7
  checkpointed_at: 2026-08-03T09:14:41Z
  generation:      2

observation:                                 # populated on completion
  summary:       "Write permission confirmed on ACME"
  verified:      true
  checks_passed: [permission_scope_present, project_visible]

artifacts:       []                          # references only, never payloads

metadata:
  attempts:        1
  dispatched_at:   2026-08-03T09:14:39Z
  completed_at:    2026-08-03T09:14:41Z
  duration_ms:     420
  cost:            { tokens: 0, currency: 0.0 }
  replayed:        false
  blocked_reason:  null
  inserted_by:     ctr_01HQ8...              # which contract proposed it  §6.9

children:        []                          # only for PARALLEL_GROUP and CHECKPOINT
```

**NORMATIVE.**

1. **`capability` and `intent` are required; `tool_chain` is derived.** A node authored with a
   `tool_id` and no capability is a validation failure (I21).
2. **`identity` includes the pinned `tool_chain`.** This is what keeps dynamic tool discovery
   compatible with replay (§9.5.3). Re-binding produces a new node, not a mutated one.
3. **`dependencies` is the only join mechanism.** No fan-in node type exists, because none is needed.
4. **`condition` is a deterministic expression over committed node observations.** No I/O, no model.
5. **`artifacts` holds references.** Payloads live in the artifact store behind the diagnostics
   access boundary, never inline in the graph — a graph is checkpointed on every pass and must stay
   small.
6. **`metadata.blocked_reason` is mandatory whenever `status == BLOCKED`.**
7. **A node in a terminal state is immutable.** Redoing work means a new node with a dependency on
   the old one.

**IMPLEMENTATION NOTE.** `type: CHECKPOINT` and `type: PARALLEL_GROUP` are structural conveniences
for display and budget accounting. Neither changes reconcile semantics — a graph with all such nodes
removed executes identically.

---
---

## 10. Runtime invariants

Twenty properties. Each is `NORMATIVE`, each is checkable by pointing at code, and each names the
test that proves it. **An implementation that cannot demonstrate all twenty has not implemented this
architecture.**

The scattered "never" clauses in §6 are shorthand for entries here.

### 10.1 Structural invariants

| # | Invariant | Enforced by | Test |
|---|-----------|-------------|------|
| **I1** | `contracts/` imports nothing from the repository. | `.importlinter` | `dependency_boundaries.yml` |
| **I2** | The kernel is domain-agnostic: `runtime/` never imports `packages/`, `capabilities/` or `tools/`. | `.importlinter`, ports | `dependency_boundaries.yml` |
| **I3** | No run state on a domain table; no domain truth in run state. | Schema assertion | `test_no_run_state_on_domain_tables.py` |
| **I4** | A package may narrow the tool surface, never widen it. | Manifest validator | `test_declared_runtime_compatibility.py` |
| **I5** | Packages never mutate runtime state — they are read as configuration. | `.importlinter` (`packages ──X──> runtime`) | `dependency_boundaries.yml` |

### 10.2 Execution invariants

| # | Invariant | Enforced by | Test |
|---|-----------|-------------|------|
| **I6** | Exactly one controller advances a session at any instant. | Lease + version CAS in one statement | `test_exactly_one_driver_per_session.py` |
| **I7** | No connection and no lock is held across a model or network call. | `connection_custody_guard.py` | `test_no_connection_across_model_call.py` |
| **I8** | All non-determinism lives inside an action. Clock and randomness are ports. | `runtime/ports/clock_port.py`, `random_port.py` | `test_non_determinism_quarantined.py` |
| **I9** | An action result is reused only on a full identity match — session, contract, action, tool and input digest. | `identity_match_classifier.py` | `test_action_identity_replay.py` |
| **I10** | A `NON_IDEMPOTENT` tool result is never replayed automatically. | `replay_decision_maker.py` | `test_action_identity_replay.py` |
| **I11** | A deadline aborts the real call. A timeout that only abandons the caller is a defect. | `abort_signal_propagator.py` | `test_provider_timeout_storm.py` |
| **I12** | Every advance is checkpointed before the next begins. | `checkpoint_manager.py` | `test_kill_worker_mid_iteration.py` |
| **I13** | Replay of a recorded session produces identical decisions. | `replay_determinism_guard.py` | `test_replay_is_deterministic.py` |

### 10.3 Authority and safety invariants

| # | Invariant | Enforced by | Test |
|---|-----------|-------------|------|
| **I14** | An `EFFECTFUL` tool is uncallable without a resolved approval reference — in the runner, never by prompting. | `effect_tag_enforcer.py` | `test_effectful_requires_approval.py` |
| **I15** | Every tool declares an effect tag. Unknown third-party effect defaults to `EFFECTFUL`. | `effect_tag_auditor.py` | `test_tool_effect_tags_present.py` |
| **I16** | Fetched content is data, never instruction. It cannot alter a plan, invoke a tool, or resolve a gate. | `untrusted_content_marker.py`, channel separation | `test_content_channel_separation.py` |
| **I17** | A park holds no process, no connection and no in-memory timer. | `runtime/parking/` | `test_park_and_resume.py` |

### 10.4 Knowledge and flow invariants

| # | Invariant | Enforced by | Test |
|---|-----------|-------------|------|
| **I18** | Only verified observations update knowledge. A model judgment may downgrade a passing check set and may never upgrade a failing one. | `model_judgment_applier.py` | `test_judgment_cannot_upgrade.py` |
| **I19** | Learning and evolution never block the request path. | Queue separation; `.importlinter` | `test_learning_is_async.py` |
| **I20** | Progress is never written to the event log. | `transactional_outbox_writer.py` rejects progress frames | `test_progress_not_in_event_log.py` |

### 10.5 Loop and presentation invariants  `[+] r3`

| # | Invariant | Enforced by | Test |
|---|-----------|-------------|------|
| **I21** | The Decision Engine names capabilities and intents, never concrete tools. | Contract validator rejects a `tool_id` in an invocation | `test_router_never_names_a_tool.py` |
| **I22** | The resolved tool binding is pinned into the invocation identity at plan time. Execution-time re-resolution mints a new identity and is recorded. | `binding_pinner.py`, `tool_fallback_selector.py` | `test_binding_pinned_into_identity.py` |
| **I23** | The Controller's only execution verb is `invoke_capability`. It has no path to a tool. | `.importlinter` (`controller ──X──> tools`) | `dependency_boundaries.yml` |
| **I24** | The Experience layer introduces no new durable event class. Progress is derived from TRACE events. | `transactional_outbox_writer.py` rejects PROGRESS and PRESENTATION classes | `test_experience_adds_no_durable_events.py` |
| **I25** | No component writes to a terminal, socket or UI. Only `gateway/renderers/` may. | Lint rule on `print`/`sys.stdout` outside renderers | `test_only_renderers_write_to_surface.py` |
| **I26** | Execution graph node transitions are legal-only and total; every node reaches a terminal state or is explicitly BLOCKED with a reason. | `node_state_machine.py` | `test_graph_transitions_are_legal.py` |

### 10.6 Execution-model invariants  `[+] r4`

| # | Invariant | Enforced by | Test |
|---|-----------|-------------|------|
| **I27** | The ExecutionGraph is the only representation of in-flight work. No parallel plan structure exists. | Schema review; `graph_invariant_checker.py` | `test_single_execution_model.py` |
| **I28** | Reconciliation is level-triggered and idempotent. Two consecutive passes over an unchanged graph produce an unchanged graph. | `deterministic_runtime_loop.py` | `test_reconcile_is_idempotent.py` |
| **I29** | Conditions are evaluated deterministically by the Controller. A condition may not call a model or perform I/O. | `condition_evaluator.py` sandbox | `test_conditions_are_deterministic.py` |
| **I30** | A capability's internal step chain is declared in its package, never computed at runtime. | `declared_recipe_reader.py`; no builder exists | `test_no_runtime_chain_planning.py` |
| **I31** | A terminal node is immutable. Redoing work creates a new node in a new generation. | `graph_mutator.py` | `test_terminal_nodes_immutable.py` |
| **I32** | The graph projection supplied to the Decision Engine is read-only. Only the Controller writes to the graph. | Projection type has no setters | `test_graph_projection_readonly.py` |

### 10.7 The two invariants that carry the most weight

**I9 — action identity.** Every other invariant can be added later at a cost proportional to the
work already done. This one cannot. Without it, every stored result is of unknown reusability, and
the migration is a rewrite rather than a change. It is roughly thirty lines. Write it first.

**I18 — verification before knowledge.** A model asked to evaluate its own work shares a training
distribution, and therefore a set of blind spots, with the model that produced it. It will approve
fluent, well-structured, wrong output because that is what it was trained to prefer. This is the
failure most likely to damage a product, because a reliability defect produces an alert and a
confidently wrong result produces an artifact someone acts on.

---

## 11. Distributed runtime

### 11.1 What is already distributed

The design is decentralised by construction rather than by a later addition. Three primitives do the
work, all of them present from Stage 1:

| Primitive | Provides | Coordination required |
|-----------|----------|----------------------|
| Lease + version CAS on a session | Mutual exclusion **per session** | none |
| Claim-based relay, one event in flight per partition | Work distribution and ordering **per partition** | none |
| Content-addressed action identity | Safe duplicate execution across any number of workers | none |

Any worker may pick up any session. No worker owns anything for longer than a lease.

### 11.2 Why there is no leader election

**NORMATIVE — and stated explicitly so that it is not "fixed" by a future engineer.**

Leader election solves a problem this runtime does not have. Mutual exclusion is already guaranteed
per-entity by the lease and the version check; work is already distributed by the claim. Introducing
a leader would add:

- a single coordination point where there is currently none,
- a split-brain failure mode requiring fencing tokens to make safe,
- a failover gap during which nothing advances,

in exchange for a guarantee the design already provides.

The usual argument for a leader is a singleton periodic job. The sweeper is the candidate, and it is
not one: **sweeping is idempotent and claim-based**, so running it on every worker is correct and is
precisely why recovery is continuous rather than boot-only. Ten workers sweeping concurrently
produce the same result as one, faster.

If a genuinely singleton job ever appears — a nightly compaction that must not overlap — use an
advisory lock with an expiry for that one job. Do not promote it to a runtime-wide leader.

### 11.3 Topology progression

**IMPLEMENTATION NOTE.** Each step adds operational surface. Take one only when a named metric
requires it.

| Stage | Topology | Move on when |
|-------|----------|--------------|
| 1 | One process, all roles | Always start here; local development must work this way |
| 2 | Gateway replicas + worker replicas, each worker running all four roles | First production deployment |
| 3 | Dedicated pool for the data plane | Model calls delay controller wakes — visible as fast-queue age |
| 4 | Dedicated relay pool | Relay claim latency approaches the substrate write ceiling |
| 5 | Partitioned workers with ownership | A single substrate can no longer serve the event rate |

Stage 5 is the only one requiring `runtime/distribution/` in anger. Stages 1–4 need nothing beyond
leases and claims.

### 11.4 Partition ownership

When Stage 5 arrives, partitions are assigned rather than contended.

```
  shard_key = hash(tenant_id) % partition_count        # tenants stay together

  partition_ownership_table
    partition_id · owner_worker_id · claimed_at · heartbeat_at · generation

  assignment      partition_assigner.py distributes unowned or stale partitions
  liveness        worker_heartbeat.py refreshes; a missed interval frees the partition
  rebalance       rebalance_coordinator.py moves the minimum number of partitions
  drain           drain_coordinator.py stops claiming, finishes in flight, releases
```

**NORMATIVE.** Partition ownership is an optimisation for locality and cache warmth. It must never
become a correctness dependency: if the ownership table is wiped, the runtime must continue to work
by falling back to open contention on leases. A design where losing the assignment table stops
progress has reintroduced the single coordination point §9.2 rejects.

### 11.5 Clock skew — the assumption to make explicit

Leases are time-bounded, so mutual exclusion depends on time. Neither the review nor the previous
revision stated the assumption, and it is the one that fails silently.

**NORMATIVE.** All lease expiry comparisons are evaluated **against the substrate's clock**, inside
the same statement that claims the lease — never against a worker's local clock.

```sql
-- correct: expiry is judged by the database, one clock for everyone
WHERE version = $expected_version
  AND (lease_until IS NULL OR lease_until < now() OR lease_owner = $worker_id)
```

A worker whose clock runs fast would otherwise consider a live lease expired and claim it. The
version check makes the outcome safe rather than corrupting — the loser's update matches zero rows —
but the work is wasted and the symptom is baffling. `clock_skew_detector.py` compares worker time
against substrate time on each heartbeat and refuses to claim beyond a threshold.

### 11.6 What breaks first, in order

| Order | Ceiling | Symptom | Response |
|-------|---------|---------|----------|
| 1 | Provider rate limits | Slow-queue age rises; retries cluster | Model semaphore, per-tenant admission |
| 2 | Substrate write throughput | Relay claim latency rises | Batch appends, then Stage 5 |
| 3 | Fast-queue concurrency | Control-plane latency tracks data-plane latency | More workers; check custody first |
| 4 | Connection pool | Pool exhaustion | **Check custody before adding connections** — the cause is usually a held connection, not capacity |
| 5 | Event log size | Replay and audit slow | Retention, compaction, snapshots |

Row 4 is the one that misleads. Pool exhaustion presents as a database problem, and adding
connections helps for a day or two. The cause is almost always a scarce resource held across a slow
call (I7), and adding capacity only moves the failure further out.

---

## 12. Observability: telemetry, diagnostics, experience

### 12.1 Diagnostics is not telemetry

Both observe the runtime; they answer different questions for different people, and conflating them
produces a system that alerts well and cannot be debugged.

| | Telemetry | Diagnostics |
|---|-----------|-------------|
| Consumer | operator, on-call, alerting | developer, support engineer |
| Question | *Is the fleet healthy?* | *Why did **this** session do **that**?* |
| Cardinality | aggregate, low | per-session, unbounded |
| Fidelity | sampled, downsampled over time | full, unsampled |
| Retention | long | short — days |
| Access | broad | **restricted; raw payloads and customer data** |
| Cost of absence | you learn from a customer | you cannot debug at all |

**NORMATIVE.** Diagnostics is access-controlled separately from telemetry
(`diagnostics/access_control.py`) and every diagnostic read is written to the audit log. It exposes
prompts, tool inputs and outputs, and trajectory content — the highest-sensitivity data in the
system.

### 12.2 The six surfaces

| Surface | Answers | Key component |
|---------|---------|---------------|
| **Execution timeline** | Where did the time go? | `machine_vs_parked_splitter.py` |
| **Prompt viewer** | What did the model actually see? | `context_source_attributor.py` |
| **Event explorer** | What happened, in what order, caused by what? | `causality_linker.py` |
| **Checkpoint explorer** | What did state look like at step N? | `state_diff_renderer.py` |
| **Trajectory viewer** | What did the whole run look like? | `divergence_comparator.py` |
| **Replay viewer** | Does re-running produce the same decisions? | `divergence_detector.py` |

Two of these deserve elaboration.

**The execution timeline splits machine time from parked time.** A six-hour session with three
minutes of worker time and a five-hour approval wait is healthy; a six-hour session with five hours
of model calls is not. A timeline that reports only wall clock cannot tell them apart, and every
downstream conclusion — capacity, cost, whether an evolution round helped — inherits the error.

**The trajectory viewer presents a run as a navigable tree rather than a wall of text.** One message
per node, grouped by task, with `divergence_comparator.py` able to align a passing and a failing
rollout of the same task and mark the step where they diverged. Progressive disclosure is not a
convenience here: it is what makes a ten-million-token trajectory readable at all, by a human or by
the distillation pipeline.

### 12.3 The design constraint: reconstruct, never store

**NORMATIVE.** The prompt viewer rebuilds an assembled prompt from stored state — the context bundle
digest, the package version, the prompt fingerprint, the session history — rather than persisting
the assembled prompt itself.

Two reasons, and the second is the one that bites.

**It would break replay.** Assembled context is *derived* state. Persisting it creates a second
source of truth that can disagree with the events it was built from, and after any change to the
compaction policy a replayed session diverges from the recorded one for reasons unrelated to the
model.

**It would double the data-protection surface.** Assembled prompts contain everything the session
touched — customer records, file contents, retrieved documents — concatenated into one blob. Storing
that alongside the trajectory means two copies to redact, two retention policies to honour, and two
places to leak from.

`assembled_prompt_reconstructor.py` therefore takes a session and a step and rebuilds the exact
prompt, using the same assembly code path the runtime used. **IMPLEMENTATION NOTE:** if
reconstruction ever disagrees with what was sent, that is itself a finding — it means assembly is
not deterministic given state, which violates I13.

### 12.4 Diagnostics in the development loop

**IMPLEMENTATION NOTE.** `diagnostics/web/` ships behind the `diagnostics_web_ui` feature flag and
is enabled by default in local and staging, disabled in production unless explicitly turned on. The
CLI surface (`gateway/cli/commands/replay_commands.py`) is always available, because the most common
diagnostic need — *replay this session and show me where it diverged* — should not require a browser.

### 12.3 The Experience layer

**The runtime does not stream tokens. It streams execution state.**

That sentence is the whole design. A system that emits *Thinking… Thinking… Searching… Thinking…* is
producing fake progress: the words change, the information content is zero, and the user learns
nothing about what is actually happening or how long it will take.

What makes a good agent feel alive is not text appearing. It is **seeing the machine work** — which
capability was selected, which tools ran, what each returned, how long each took, and what is still
outstanding.

#### 11.3.1 Where it sits

```
   any component
        │  emits a TRACE event (durable, through the outbox)
        ▼
   EVENT BUS
        │
        ▼
   EXPERIENCE LAYER                        runtime/experience/
        │
        ├── runtime_event_mapper.py     durable fact  ->  runtime event
        ├── progress_tree_builder.py    events        ->  hierarchical tree
        ├── execution_trace_builder.py  events        ->  the durable trace (§9.6)
        └── encoders/                   tree + trace  ->  a wire format
        │
        ▼
   TRANSPORT   stream_publisher.py     (direct to client, never durable)
        │
        ▼
   RENDERERS                               gateway/renderers/
   terminal tree · plain log · JSON · web frames
```

**NORMATIVE.** The Experience layer is **presentation-neutral**. It produces a structured progress
tree and an execution trace; it never produces characters. Rendering lives in `gateway/renderers/`,
which is the only code in the repository permitted to write to a terminal or a socket. This is what
keeps the kernel independent of any particular UI while still driving a rich one.

#### 11.3.2 Progress is hierarchical, not a flat log

A flat log of *running command… running command… running command…* is barely better than a spinner.
The tree mirrors the three loops, which is why the loops had to be made explicit first:

```
  Goal  resolve issue 412 and check Jira access              ▸ 00:28
  │
  ├─ Context                                        ✓ ready   184 ms
  │   ├─ session · memory · world                   ✓
  │   ├─ package  coding@3.1.0                      ✓
  │   └─ credentials  git · jira                    ✓
  │
  ├─ Iteration 1                                    ✓        4.1 s
  │   └─ Capability  git.repository_inspection      ✓        2.14 s
  │       ├─ git checkout dev                       ✓         310 ms
  │       ├─ git pull                               ✓        1.49 s
  │       └─ git log -10                            ✓         340 ms
  │       └─ observation  on dev at 4f1c9e2, 10 commits read
  │
  ├─ Iteration 2                                    ▸        running
  │   └─ Capability  jira.access_check              ▸
  │       ├─ jira.search                            ✓         420 ms
  │       ├─ jira.permissions                       ▸        running
  │       └─ jira.myself                            ·        pending
  │
  └─ Final response                                 ·        pending
```

Every node in that tree is derived from a durable event. Nothing in it is invented for display, and
nothing about it is specific to a terminal — the same tree renders as JSON, as web frames, or as a
plain CI log.

**IMPLEMENTATION NOTE.** Duration on a still-running node is computed by the renderer from the node's
start timestamp, not pushed as a stream of tick events. Ticking a clock over the wire is the fake
progress this design exists to avoid.

#### 11.3.3 Reconnect is the same problem as the gateway's

Because the progress tree is derived, it is reconstructible. `progress_snapshot_builder.py` rebuilds
the complete tree at any point from durable events, so a client that disconnects for forty minutes
hydrates a snapshot and then subscribes from a cursor. This is the identical pattern the gateway
uses for its read model, now applied to execution state — one mechanism, two consumers.

#### 11.3.4 Three observability surfaces, one boundary rule

The runtime now has three things that observe it. They are not variations of each other.

| | Telemetry | Diagnostics | Experience |
|---|-----------|-------------|------------|
| Consumer | operator, alerting | developer, support | **the end user** |
| Question | is the fleet healthy? | why did *this* session do *that*? | what is happening *right now*? |
| Timing | continuous, aggregate | post-hoc | **live** |
| Fidelity | sampled | full | curated |
| Content | measurements only | raw payloads | summaries |
| Access | broad | restricted, audited | the session's owner |
| Retention | long, downsampled | days | the session |

**NORMATIVE.** All three derive from the same durable TRACE events. None of them is a separate
instrumentation path, and no component emits to more than one. A team that instruments three times
will have three vocabularies that disagree within a year.

---
---

## 13. Dependency rules, enforced in CI

`.importlinter` encodes the following as contracts. They fail the build, not the review.

```
LAYERS  (a layer may import only from layers below it)

    gateway  ·  evolution  ·  learning
        │
    packages  ·  capabilities  ·  plugins
        │
    runtime
        │
    knowledge  ·  models  ·  tools  ·  security  ·  storage
        │
    contracts

FORBIDDEN EDGES

    runtime          ──X──>  packages, capabilities, tools, gateway
    contracts        ──X──>  anything
    knowledge        ──X──>  runtime
    storage          ──X──>  runtime
    evolution        ──X──>  runtime.controller, runtime.execution
    plugins          ──X──>  runtime.kernel
    controller       ──X──>  models            (the control plane cannot reach a model)
    gateway          ──X──>  runtime.controller, runtime.execution
    diagnostics      ──X──>  runtime.controller, runtime.execution   (read-only observer)
    runtime.manifest ──X──>  runtime.controller, runtime.execution   (boots before them)
    packages         ──X──>  runtime            (packages are data, not code that drives)
    controller       ──X──>  tools              (the Controller invokes CAPABILITIES only)
    runtime.experience ──X──> runtime.controller, runtime.execution  (observer, never a driver)
    runtime          ──X──>  gateway.renderers  (the kernel never renders)
    capability_executor ──X──> runtime.intelligence   (nothing below the Decision Engine reasons)
    capability_executor ──X──> runtime.controller     (it is invoked, it does not drive)
    context.sources  ──X──>  runtime.controller  (graph projection is read via a port)
```

The `controller ──X──> models` edge is worth singling out. The specification says *"the Controller
never calls an LLM."* This line is what turns that sentence from a promise into a build failure.

---

## 14. Component block diagram

```
                                                                  BLOCK VIEW
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ CLIENTS      terminal · HTTP · SDK · IDE · webhook · schedule · agent     │
  └───────────────────────────────────┬──────────────────────────────────────┘
                                      │ goals · approvals · signals
  ╔═══════════════════════════════════▼══════════════════════════════════════╗
  ║ GATEWAY                                        gateway/                  ║
  ║  ┌────────────────────────────┐  ┌────────────────────────────────────┐  ║
  ║  │ INBOUND  intent            │  │ OUTBOUND  view                     │  ║
  ║  │ auth→tenancy→rate→validate │  │ read model + seq  →  hydrate       │  ║
  ║  │ →idempotency→command       │  │ then subscribe (SSE / WebSocket)   │  ║
  ║  └─────────────┬──────────────┘  └────────────────▲───────────────────┘  ║
  ║   no loop · no consumer · no model call           │                      ║
  ╚════════════════│══════════════════════════════════│══════════════════════╝
                   │ command + event (ONE txn)        │ progress (never durable)
  ┌────────────────▼──────────────────────────────────┴──────────────────────┐
  │ SUBSTRATE                                       storage/                 │
  │  events │ commands │ sessions │ actions │ identity_ledger │ leases       │
  │  parks  │ approvals│ budget_ledger │ signals │ projections │ snapshots   │
  └────────────────┬─────────────────────────────────────────────────────────┘
                   │ claimed events (one in flight per partition)
  ╔════════════════▼═════════════════════════════════════════════════════════╗
  ║ RUNTIME KERNEL                    runtime/            domain-agnostic    ║
  ║                                                                          ║
  ║  ┌────────────────────────────────────────────────────────────────────┐  ║
  ║  │ CONTEXT   runtime/context/    9 sources fanned out concurrently    │  ║
  ║  │   session · memory · world · files · package · policies · caps     │  ║
  ║  │   + EXECUTION GRAPH PROJECTION (read-only) — cognition is never    │  ║
  ║  │     blind to what already happened                          [§6.2] │  ║
  ║  │           → ContextBundle  (derived · never persisted as truth)    │  ║
  ║  └──────────────────────────────┬─────────────────────────────────────┘  ║
  ║  ┌──────────────────────────────▼─────────────────────────────────────┐  ║
  ║  │ DECISION ENGINE   runtime/intelligence/decision/                   │  ║
  ║  │           ONE structured inference per iteration                   │  ║
  ║  │           THE ONLY NON-DETERMINISTIC BOX IN THE RUNTIME            │  ║
  ║  │           → ExecutionContract (+ proposed graph mutations)         │  ║
  ║  │           never executes · never writes state · never names a tool │  ║
  ║  └──────────────────────────────┬─────────────────────────────────────┘  ║
  ║  ┌──────────────────────────────▼─────────────────────────────────────┐  ║
  ║  │ BINDING   runtime/intelligence/binding/    DETERMINISTIC, no model │  ║
  ║  │           intent → candidate tools → ONE pinned binding            │  ║
  ║  │           the binding is hashed into the node identity             │  ║
  ║  └──────────────────────────────┬─────────────────────────────────────┘  ║
  ║  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▼▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ║
  ║  ▓ POLICY GATE   runtime/policy/        NON-BYPASSABLE HARD BARRIER  ▓  ║
  ║  ▓   permissions · tenancy · budget reservation · effect tag         ▓  ║
  ║  ▓   an EFFECTFUL tool is structurally uncallable without a          ▓  ║
  ║  ▓   resolved approval — enforced here, never by prompting  [I14]    ▓  ║
  ║  ▓   nothing reaches the Controller except through this gate         ▓  ║
  ║  ▓   → ValidatedExecutionContract                                    ▓  ║
  ║  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓┬▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ║
  ║                                 │                                        ║
  ║  ┌──────────────────────────────▼─────────────────────────────────────┐  ║
  ║  │ CONTROL PLANE   runtime/controller/          A RECONCILER          │  ║
  ║  │   ready_nodes() → dispatch() → observe() → update graph → repeat   │  ║
  ║  │   level-triggered and idempotent, never edge-triggered      [I28]  │  ║
  ║  │   EXECUTION GRAPH — plan + state + progress + deps + checkpoint    │  ║
  ║  │   PENDING READY RUNNING WAITING BLOCKED COMPLETED FAILED SKIPPED   │  ║
  ║  │   signal reader (same txn as checkpoint) · exit evaluator          │  ║
  ║  │   never calls a model · never executes · never names a tool        │  ║
  ║  │                                                                    │  ║
  ║  │   supported by:  identity/  leasing/  parking/  budget/       [+]  │  ║
  ║  └──────────────────────────────┬─────────────────────────────────────┘  ║
  ║  ┌──────────────────────────────▼─────────────────────────────────────┐  ║
  ║  │ CAPABILITY EXECUTOR   runtime/capability_executor/                 │  ║
  ║  │   invoke_capability — the Controller's ONLY execution verb         │  ║
  ║  │   executes a DECLARED recipe from the package. Plans nothing.      │  ║
  ║  │   capability-local context · declared parallel steps · sandbox     │  ║
  ║  │   N tool results  ->  ONE structured observation                   │  ║
  ║  └──────────────────────────────┬─────────────────────────────────────┘  ║
  ║  ┌──────────────────────────────▼─────────────────────────────────────┐  ║
  ║  │ DATA PLANE      runtime/execution/    ALL non-determinism          │  ║
  ║  │   7 strategies · workflow runner · retry · rollback · timeout      │  ║
  ║  │   abort propagation · middleware hooks · sandbox pool              │  ║
  ║  └───────┬──────────────────────────────────────────────┬─────────────┘  ║
  ║          │                                              │               ║
  ║  ┌───────▼────────┐                            ┌────────▼────────────┐   ║
  ║  │ OBSERVATION    │                            │ EVENTS  (the spine) │   ║
  ║  │ verify → judge │                            │ outbox · relay      │   ║
  ║  │ → evaluate     │───────────────────────────▶│ projections · replay│   ║
  ║  │ (downgrade     │                            │ progress excluded   │   ║
  ║  │  only)         │                            └────────┬────────────┘   ║
  ║  └───────┬────────┘                                     │               ║
  ╚══════════│══════════════════════════════════════════════│═══════════════╝
             │ next iteration ── back to ROUTER             │
             └──────────────────────────────────────────────┘

  ── experience ─────────────────────────────────────────────────────────────
   runtime/experience/   TRACE events -> progress tree + execution trace
                         encoders: AG-UI · native · OpenTelemetry GenAI
                         derives only; adds NO durable event class
                                      │
                         gateway/renderers/   the ONLY writers to a surface
                         terminal tree · plain log · JSON · web frames
  ───────────────────────────────────────────────────────────────────────────

  ── ports ──────────────────────────────────────────────────────────────────
   runtime/ports/   model · tool · capability · package · knowledge · store
                    approval · clock · random · telemetry
  ───────────────────────────────────────────────────────────────────────────
        ▲              ▲              ▲              ▲              ▲
  ┌─────┴────┐  ┌──────┴─────┐  ┌─────┴──────┐  ┌────┴─────┐  ┌─────┴──────┐
  │ models/  │  │ tools/     │  │capabilities│  │knowledge/│  │ security/  │
  │ router   │  │ PURE  /    │  │ WHAT       │  │ world    │  │ tenancy    │
  │ providers│  │ EFFECTFUL  │  │            │  │ memory   │  │ secrets    │
  │ cache    │  │ MCP bridge │  │            │  │ artifacts│  │ redaction  │
  └──────────┘  └────────────┘  └────────────┘  └──────────┘  └────────────┘

  ┌──────────────────────────────────────────────────────────────────────────┐
  │ PACKAGES = THE HARNESS                              packages/            │
  │  prompts · capabilities · policies · templates · knowledge · skills      │
  │  memory config · evaluation rubrics · workflows                          │
  │  pinned against a MODEL IDENTITY — a model upgrade invalidates a pin     │
  └───────────────────────────────────▲──────────────────────────────────────┘
                                      │ the ONLY write target of evolution
  ┌───────────────────────────────────┴──────────────────────────────────────┐
  │ ASYNCHRONOUS — never blocks the request path                             │
  │                                                                          │
  │  learning/   trajectories → distillation → candidates → benchmarks       │
  │       │                                                                  │
  │  evolution/  experiment → evolve agent → change manifest → attribution   │
  │       │                  (predictions verified next round)               │
  │       ▼                                                                  │
  │  ┌────────────────────────────────────────────────────────────────────┐  │
  │  │ HUMAN APPROVAL GATE — a durable park. Holds nothing. May last days.│  │
  │  │ The loop foresees its fixes far better than its regressions;       │  │
  │  │ this reviewer is the real defence against the ones it cannot see.  │  │
  │  └────────────────────────────────┬───────────────────────────────────┘  │
  │                                   ▼                                      │
  │              promoted package version · revertible per file              │
  └──────────────────────────────────────────────────────────────────────────┘
```

---

## 15. Build order

Each stage is useless without the one before it and dangerous without the one after it.

| Stage | Build | Done when |
|-------|-------|-----------|
| **0 · Contracts** | `contracts/`, schema export, `.importlinter`, `runtime.manifest.yaml` | The dependency graph is enforced, and the deployment has an identity, before any logic exists |
| **1 · Spine** | Outbox writer, claim relay, one queue, command port | An event written by the gateway wakes a handler in a worker |
| **2 · Session** | Sessions table, `leasing/`, controller loop, one hardcoded step | A session advances and survives `kill -9` mid-step |
| **3 · Identity** | `identity/`, action ledger, one real tool | A replay returns the stored result and never re-spends |
| **4 · Router** | Context assembly, single-pass router, contract validation | A contract is produced, logged, and diffable |
| **5 · Policy + Park** | `policy/`, `parking/`, approval port | A session parks for a day and resumes at the right step |
| **6 · Verification** | Deterministic checks, golden set replayed in CI | You can tell whether a change made the system better or worse |
| **7 · Control** | Signals, cancellation, abort propagation, streaming | A person redirects a running session in under two seconds |
| **8 · Scale** | Work classes, `budget/`, `resources/`, dead letter, dashboards | One tenant's slow work is invisible to every other tenant |
| **9 · Packages** | Package registry, manifests, version pinning | A package can be swapped and rolled back without touching the kernel |
| **6b · Capability** | Capability runtime, tool orchestration, intent index, one real capability | The Controller invokes a capability and never names a tool |
| **7b · Graph** | Execution graph, node states, ready-set scheduling | You can pause a session and resume it at the right node |
| **9b · Experience** | Event taxonomy, progress tree, trace builder, one renderer | A terminal shows the nested tree, and reconnect rebuilds it |
| **10 · Diagnostics** | Timeline, prompt reconstruction, replay viewer | You can answer *why did this session do that* without adding logging |
| **11 · Evolution** | Trajectory store, distillation, change manifest, attribution, approval gate | Ten unattended rounds run and rejected edits revert themselves |
| **12 · Distribution** | Partition ownership, rebalance, drain | Only when a single substrate can no longer serve the event rate |

**On sequencing.** The instinct is to build reliability first and verification last. Stage 6 belongs
where it is. The failure that kills an agent product is not that the pool wedges at high
concurrency — you will not have high concurrency for months. It is that the system produces
confident, plausible, wrong work and nobody notices.

---

*End of document.*


---

## 16. Modification log

Every section touched in revision 4, and why. Sections not listed are unchanged.

| Section | Change | Driver |
|---------|--------|--------|
| Header | Revision 3 → **Revision 4** | — |
| §1.4 | **New.** Round-four log, including the one critique **rejected** and why | review |
| §1.5, §1.6 | Renumbered from §1.4, §1.5 | — |
| §3 | **Rules 13 and 14 added** — one execution model; no reasoning below the Decision Engine | consolidation |
| §4.4 | **New.** Round-four additions — a net *removal* of one package | collapse |
| §4.5 | Renumbered from §4.4 | — |
| §5 | **Retitled** "three loops, one graph". Middle loop is now the Capability Executor; the inner orchestration layer is gone; binding shown above all three | collapse |
| **§6** | **New section.** ExecutionGraph as the single execution model: why it is not a DAG engine, graph-as-context, node states, the reconcile loop, parallel, conditional, retry, timeout, checkpoint, approval, dynamic insertion, and a per-pass walkthrough | ExecutionGraph brief |
| §7 (tree) | `intelligence/router/` → `intelligence/decision/`; **`intelligence/binding/` added**; `capability_runtime/` + `tool_orchestration/` → **`capability_executor/`**; `controller/execution_graph/` expanded from 10 to 19 files; **`context/sources/execution_graph_source.py` added**; `contracts/graph/` expanded with the node spec | all four |
| §9.5 | `single_pass_router.py` → `decision_engine.py`; the section now describes the Decision Engine | naming |
| §9.20 | `capability_runtime` and `tool_orchestration` entries merged into one **Capability Executor** entry | collapse |
| §9.22 | Execution-graph entry rewritten: from progress tracker to the execution model | ExecutionGraph brief |
| **§9.8** | **New.** ExecutionNode specification — every field, with seven normative rules | ExecutionNode brief |
| §9.5.3 | Binding resolution relocated to `intelligence/binding/`, between decision and policy | cognitive-sandwich critique |
| **§10.6** | **New.** Six execution-model invariants, I27–I32 | ExecutionGraph brief |
| §10.7 | Renumbered from §10.6 | — |
| §13 | Three dependency contracts added, forbidding reasoning or driving below the Decision Engine | collapse |
| §14 | Block diagram: graph projection added to context; Decision Engine renamed and marked as the only non-deterministic box; **binding step added**; **Policy Gate redrawn as a full-width non-bypassable barrier**; Controller shown as a reconciler; two execution layers collapsed to one | all four |
| §15 | Build order: stage 6b retitled for the Capability Executor; stage 7b now builds the full graph model | ExecutionGraph brief |
| **§16** | **New.** This log | deliverable |

### 16.1 What was deliberately not changed

| Not changed | Why |
|-------------|-----|
| The Policy Gate's position and authority | It never moved. The critique was a misreading of a simplified diagram; the fix is that §14 now draws it as a barrier |
| Parallel Context Assembly | Unchanged apart from gaining one source |
| The identity model (I9, I22) | The graph strengthened it — node identity now includes the graph generation, so a replan cannot inherit stale results |
| Observation, events, experience, diagnostics, distribution, manifest, packages | Untouched |
| Layer count | Went **down** by one. No new layer was introduced by any of these changes |

### 16.2 Sections to read first, if you read nothing else

1. **§6.2** — the graph as an input to cognition. Cheapest change here, largest effect on token cost and decision quality.
2. **§6.1** — why a reconciler is not a scheduler. This is what keeps the design simple while making it fully expressive.
3. **§9.5.3** with **§9.8** — how dynamic tool binding stays compatible with replay. Get this wrong and I9 fails silently.
4. **§1.4** — the rejected critique, so that the Policy Gate is not "restored" by someone who thinks it is missing.

---

*End of specification. Revision 4 — final.*
