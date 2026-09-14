# High-Level Implementation Architecture

**Status of this document:** **DESIGNED / PROPOSED.** It describes structure,
not code. **Zero lines of product code exist**, here or anywhere. Nothing below
is implemented, and no status label in this document may be read as progress.

**What this document is for.** The PRD says what product is being validated and
why. The build order says in what sequence. **This document says how the system
is structured and how that structure is allowed to change** as each phase
produces evidence. It is deliberately independent of the PRD, and it does not
restate the PRD's requirements.

Read `PROJECT_BOOTSTRAP.md` §0 for the meaning of the status and evidence
labels. Read `15-vocabulary.md` before coining a name for anything here.

---

## 1. What system this is

**The long-term system is a general-purpose agent Brain + Runtime.** The
**Organizational Brain is the first major substrate and proving ground** — the
concrete environment in which evidence, memory, world state, temporal
reasoning, authority, contradiction, provenance, retrieval and verification are
made reliable enough to act on. See
[ADR-0027](decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md).

**The anti-collapse rule, stated once so it cannot be reconstructed wrongly:**

> *"We are building an organizational knowledge product"* is an **incorrect**
> summary of this project. The correct one is: *we are building a
> general-purpose agent Brain + Runtime, beginning with the Organizational
> Brain as the first serious substrate, because a system cannot be trusted to
> act until it is reliable about what is true, when it was true, and on what
> basis.*

That ordering is not a preference. It is the same rule `00-north-star.md` §7
already states one level down — *"build the things that make the store legal and
measurable before the things that make it good"* — applied to the whole system:
**the knowledge plane is built first because the execution plane's guarantees
are worth nothing over an unreliable world model.**

### 1.1 Two registers, and why both are needed

| Register | Term | Used in |
|---|---|---|
| Product identity | **general-purpose agent Brain + Runtime** | `PROJECT_BOOTSTRAP.md` §2, `00-north-star.md` §1, ADR-0027 |
| Current substrate | **Organizational Brain** | Named as the *first* substrate, never as the system's definition |
| Engineering subsystem | **the knowledge system** · **the runtime** · **Principal Agent** · **environment adapters** · **capability layer** | This document, the ADRs, the architecture map, the domain model |

"Brain" names the product. "The knowledge system" names the subsystem. They are
the same thing seen from two distances, and `15-vocabulary.md` §7 records the
mapping so a future session does not read them as a contradiction.

---

## 2. The system in one figure

```
   EXTERNAL CONSUMERS          external agents (Claude, Codex) · humans · MCP
        |                      untrusted clients. strictly smaller capability set
        v
  +=============================================================+
  |  CAPABILITY LAYER                                           |
  |  the ONE place a Principal is resolved, then the ONE place  |
  |  the store is reached. CL1-CL4.                             |
  |  Phase 1: four functions. Not a registry, not middleware.   |
  +=============================================================+
        |                                          ^
        | a QUESTION or a SCOPE, with a Principal  | claims, cited, with
        | and a temporal anchor                    | contradictions never omitted
        v                                          |
  +=============================================================+
  |  KNOWLEDGE PLANE                      "the Brain"           |
  |                                                             |
  |  SOURCE ADAPTERS -> OBSERVATION LOG      system of record   |
  |        -> ADMISSION -> IDENTITY ANCHORING -> EXTRACTION     |
  |        -> CLASSIFY + RECONCILE -> CLAIM STORE + EVIDENCE    |
  |        -> WORLD MODEL (a projection) -> RETRIEVAL/CONTEXT   |
  |                                                             |
  |  + VERIFICATION LOOP: writes OBSERVATIONS, re-enters at top |
  +=============================================================+
        ^
        |  one-way. the knowledge plane never calls up.
        |
  +=============================================================+
  |  EXECUTION PLANE                      "the Runtime"         |
  |  Run / Episode / Step / Activity / Park · ExecutionGraph    |
  |  leases · checkpoints · effect ledger · outbox              |
  |  owns no judgement. every judgement is behind a port        |
  +=============================================================+
        |
        v
  ENVIRONMENT ADAPTERS  ->  the world
  filesystem · VCS · HTTP · inference · clock · scope

  PRINCIPAL AGENT is not a layer in this figure.
  It is a RUN inside the execution plane that consumes the
  capability layer like any other client. [ADR-0014]
```

**The figure draws rules, not a schedule.** The execution plane gets no code
until Phase 6, and half the Principal Agent is BLOCKED on organizational
structures that do not exist. Drawing a box is not scheduling it.

---

## 3. Plane ownership

| | **Owns** | **Does not own** | **Depends on** | **Status** |
|---|---|---|---|---|
| **Knowledge plane** | Observations, claims, versions, evidence, entities, contradictions, the world model, retrieval and context assembly | **Execution.** It never calls a tool the agent owns, never applies an effect, never writes a goal. It does not own the source-precedence policy's *contents* — a named human does | Persistence; a model, behind a port, for the one extraction step | DESIGNED |
| **Execution plane** | Run / Episode / Step / Activity / Park, the ExecutionGraph, leases, checkpoints, the effect ledger, the outbox | **Any judgement**, and any claim. It never writes to the claim store directly | Persistence; ports for every judgement | DESIGNED. No code. None of the 39 invariants is enforced, because there is nothing to enforce them against |
| **Principal Agent** | Goals it was *given*, decisions with sealed predictions, commitments, delegation grants, outcome records | Four prohibitions: it may not set its own goals, execute work itself, grade its own outcomes, or hold organizational knowledge in harness state | Execution plane (it *is* a Run); capability layer | DESIGNED. Four of its objects are **BLOCKED**, not deferred |
| **Capability layer** | `context_for` · `entity` · `history` · `why` · `conflicts` · `as_of` · `propose_claim` | Transport, session handling, ranking policy, or any surface-specific concern | Knowledge plane, through one module boundary | DESIGNED |
| **Environment adapters** | Applying effects and observing the world | **Effect policy.** A tool *declares* an effect tag; it does not decide whether it may run | Execution plane's ports | DESIGNED |
| **Observability / evaluation** | The flight recorder; the task set, oracles, noise-floor estimator, per-slice metrics | Production behaviour. Evaluation is offline and never blocks the request path | Reads everything; writes nothing back into knowledge | DESIGNED |
| **Security / tenancy** | Principal, scopes, grants, tenant-in-key | Knowledge-system concepts. A `brain_scope` field on the Principal leaks the knowledge system into the identity model | Nothing above it | DESIGNED |
| **External interfaces (MCP)** | Transport and protocol | Everything else. A strict projection, deletable without losing anything | Capability layer | **PROPOSED, deliberately deferred** |

---

## 4. Dependency direction

### 4.1 The rule

> **NORMATIVE.** The execution plane may depend on the knowledge plane. **The
> knowledge plane may never depend on the execution plane.** The dependency is
> mediated by the capability layer, and crosses it as plain data.

And the store rule, which is a different rule about a different boundary:

> **NORMATIVE.** No surface reaches past the capability layer to the store.
> The permitted path is *agent → tool → capability layer → retrieval → store*.
> The forbidden path is *agent → store*.
> [ADR-0012](decisions/ADR-0012-the-agent-reaches-the-brain-only-through-tools.md), CL4.

### 4.2 This is a new decision, and it is not the one the specification already makes

**[FACT]** The runtime specification's §13 forbids `knowledge ──X──> runtime`.
**That edge is about a different subsystem.** The specification's `knowledge/`
is the *runtime's own* world-state and memory tier (§8.15 — `world/`,
`memory/`, `artifacts/`), not the Organizational Brain. ADR-0012 says so
outright: *"The knowledge system is placed as a **peer package**, not inside the
agent or the knowledge layer."*

So §13 is **not** authority for the rule in §4.1. The rule is argued here, on
its own terms:

**[DESIGN DECISION]** The knowledge plane must be able to answer *"what did we
believe in June, and why"* without a run existing. If it can import execution
state, a claim's meaning becomes a function of the run that read it, and the
rebuild invariant (O5) stops being checkable — you can no longer drop everything
downstream and replay the log, because replay would need to reconstruct runs.
**One-way dependency is what makes rebuildability decidable**, and
rebuildability is the property the whole knowledge design rests on.

### 4.3 What this does *not* require

**A separate deployable is not required, and would not buy the property people
assume it buys.** ADR-0012's guarantee is that tools are **curried with the
Principal at graph-build time**, so an unauthorised query is *absent from the
schema* rather than refused at runtime. That is a property of an **in-process
construction**. A network boundary does not add it —
[ADR-0013](decisions/ADR-0013-mcp-is-a-projection-of-the-capability-layer.md)
records that MCP *loses* it, because an MCP client sees the same tool list as
everyone.

**Phase 1 needs exactly three things, and no port abstraction:**

1. **The capability layer is the only module any surface may import**, enforced
   by the import lint that Stage 0 already schedules.
2. **Capability signatures are plain data in, plain data out** — Principal,
   `as_of`, scope, budget, limit → claim set + evidence handles + open
   contradictions. Not a cursor, not a session, not a connection. *This*, not a
   port with two implementations, is what makes a later process split a
   transport change rather than a rewrite.
3. **The permission predicate inside the store implementation** (R4), never
   applied by the caller and never post-applied.

**Do not build a port with two implementations.** One implementation,
data-shaped signatures, one lint contract. A second implementation with nothing
to run against is architecture ahead of requirement.

### 4.4 Forbidden edges, as a CI contract

```
  knowledge plane   ──X──>  execution plane        (the §4.1 rule)
  knowledge plane   ──X──>  capability layer       (it is depended on, it does not depend)
  any surface       ──X──>  claim store            (CL4 — the path is the capability layer)
  execution plane   ──X──>  claim store            (the runtime never writes a claim directly)
  knowledge core    ──X──>  domain packages        (ADR-0028 — the core is domain-agnostic)
  evolution surface ──X──>  authored governance    (ADR-0006, ADR-0028 bucket A)
  security/identity ──X──>  knowledge concepts     (no brain_scope on the Principal)
```

**Two notes on citing the specification's §13.** Its LAYERS block places `tools`
*below* `runtime` — importable — while its FORBIDDEN EDGES list bans
`runtime ──X──> tools`. Design rule 4 sides with the ban. **Cite rule 4 and the
edge list; the layer-stack diagram is not a citable authority.** And §13 has no
entry for a capability layer at all, which is why §4.1 places it here rather
than deriving it.

---

## 5. The knowledge pipeline, as a first-class object

The knowledge plane is **not** "memory storage". It is a pipeline with an
explicit loop, and the stages are not interchangeable.

```
  SOURCE / ENVIRONMENT
        |
  OBSERVATION            raw, append-only, permission-labelled, content-hashed
        |                O1-O5 · [ADR-0004]
  ADMISSION              most things stop here. discard rate is a headline metric
        |                AD1-AD2
  IDENTITY / ENTITY ANCHORING    before extraction, never after
        |                E1-E2 · [ADR-0018]
  EXTRACTION / PROPOSAL  the one model step. identity-keyed. proposes, never writes
        |                X1-X3 · [ADR-0010]
  CLASSIFICATION / RECONCILIATION    deterministic. part of writing, not a later pass
        |                C1-C4
  CLAIM / KNOWLEDGE STATE    kind-typed. versioned. tenant in the key
        |                CS1-CS5 · [ADR-0003]
  EVIDENCE / PROVENANCE  a joinable table of references, server-minted, outlives the run
        |                EV1-EV3
  WORLD MODEL            a projection. delete it and lose only rebuild time
        |                WM1-WM2 · [ADR-0005]
  RETRIEVAL / CONTEXT    scope-first. denied reads RAISE. three things never dropped
        |                R1-R4, CA1
  AGENT / RUNTIME        consumes through the capability layer
        |                CL1-CL4
  VERIFICATION           deterministic. no model. may lower a verdict, never raise it
        |                V1-V3 · [ADR-0015]
  NEW OBSERVATION        -> re-enters at the top. this is what closes the loop
```

### 5.1 The non-collapse rule

> **NORMATIVE.**
> **OBSERVATION ≠ CLAIM ≠ EVIDENCE ≠ MODEL JUDGEMENT ≠ WORLD STATE.**
> These are five different things with five different owners, lifetimes and
> authorities. **They may not be collapsed to simplify an implementation.**

| | Is | Is not |
|---|---|---|
| **Observation** | What a source emitted, retained raw | Interpreted. Nothing here means anything yet |
| **Claim** | A kind-typed assertion whose kind bounds what it has authority over | True. A claim is a claim |
| **Evidence** | Joinable references to the observations a claim version rests on | A confidence score. Evidence is the *input* to standing, never the number |
| **Model judgement** | A proposal, and a verdict that may only be **lowered** | Evidence, and never a route by which a claim gains standing |
| **World state** | A projection, rebuildable from claims | A place a fact may live. A fact in the world model and nowhere else is a second source of truth |

Collapsing any pair is the specific failure the §2 worked example in
`00-north-star.md` describes: a system that retrieves three disagreeing sources,
flattens them into undifferentiated "context", and makes the disagreement
invisible in the output. **Perfect retrieval produces that failure too.**

### 5.2 The properties that hold the loop together

Restated here because each one is load-bearing and each is already decided
elsewhere: append-only observation source · rebuildability · explicit
provenance · temporal information from day one · permissions captured at ingest
and propagated · authority explicit and never inferred · contradictions visible
· abstention possible · **model judgement cannot independently establish truth**
· an explicit Principal on every call · no ambient authority.

---

## 6. Durable state and storage boundaries

| | What it is | Rebuildable? |
|---|---|---|
| **Observation log** | **The system of record.** Everything else is derived | No — this is the source |
| **Claim store + versions + evidence** | Derived, but **authoritative for reads** | Yes, from the log |
| **World model** | A projection | Yes. WM1's delete test is how you check |
| **Retrieval index** | Disposable | Yes, and it is authoritative for nothing |
| **Contradiction register** | Derived; gates actions | Yes |
| **Run / execution state** | Owned by the execution plane | Not from the knowledge log — different lifetime, different owner (PS2) |

**One transactional substrate.** A claim, its version, its evidence and its
outbox event commit in **one transaction** (PS1). This is the decisive argument
against a second store engine and the reason
[ADR-0009](decisions/ADR-0009-no-graph-database.md) holds: split across engines
it becomes a distributed transaction.

### 6.1 The store set is DISPUTED, and this document does not settle it

**[FACT]** Two documents in this repository specify **incompatible Phase 1
schemas** — over the entities table, entity resolution's phase, the
contradictions table, and relationships. `09-do-not-assume.md` §11 lists
building a schema before that reconciliation as a **stop**. This is **Q7**, and
it is open.

**A third shape is now in scope and no document previously named it.** The
runtime specification's `knowledge/world/` ships `entity_store.py`,
`entity_resolver.py` and `fact_store.py` — the same nouns, a third time.
Registered here and in `01-architecture-map.md` §4.5.

**So: the table names in §5 and §6 are the vocabulary of the pipeline, not a
ratified schema.** Nothing here decides Q7, and nothing here should be read as
having decided it.

---

## 7. Required now versus required later

| Subsystem | Phase 1 (required now) | Later, and what triggers it |
|---|---|---|
| Observation log | **Yes, in full.** The six temporal fields, permission label, content hash, raw payload | — |
| Admission | Deterministic stage only | The model stage when the deterministic stage's inconclusive rate is measured |
| Entity anchoring | **Yes.** Identity, not resolution across sources | Full entity resolution at the second source, where identity stops being free |
| Extraction | **Yes, identity-keyed.** This is the one that cannot be retrofitted | — |
| Claim store + evidence | **Yes**, subject to Q7 | — |
| Contradiction detection | **Yes** | Severity gating when Q15 is decided |
| World model | **Yes**, as a projection | — |
| Retrieval | Structural. Scope-first, one SQL statement | Embeddings only on a pre-registered vocabulary-miss threshold ([ADR-0008](decisions/ADR-0008-no-embeddings-in-phase-1.md)) |
| Capability layer | **Yes** — four functions with CL1-CL4 | Hardening at Phase 4 |
| Verification loop | **No.** Phase 3 | `verifiable_by` is an empty vocabulary today |
| MCP | **No.** Phase 4 | A stable capability layer **plus** a decided Q9 |
| Execution plane | **No.** Phase 6 | Four primitives, each with its own trigger — never as a block |
| Principal Agent | **No.** Phase 6, and half of it is BLOCKED | Goals authored by a human, with measures and baselines |
| Distribution | **No** | A single substrate can no longer serve the event rate |
| Learning / evolution | **No** | Nothing in any planned stage |

---

## 8. The distributed-system evolution path

**The point of this section:** the knowledge plane must be able to become a real
distributed service without a rewrite, *and* must not pay for distribution
before it has any. Those pull in opposite directions, and the resolution is not
"build it distributed" — it is **to separate the properties that cannot be added
later from the ones that can.**

### 8.1 The criterion for irreversible

Not *"hard to add later."* The sharper test:

> **The data already written is of unknown value, and the input needed to
> repair it was never captured.**

By that test, a lease is reversible — adding one later is a code change against
data that is already correct. A missing valid-time column is not: you cannot
back-fill a time you never recorded.

### 8.2 The eight irreversible properties

| # | Property | The failure that makes it irreversible |
|---|---|---|
| 1 | **Extraction identity (X1)** | A redelivery is re-extracted by a non-deterministic model and produces a differently-worded claim at the same identity. Corroboration counts DISTINCT runs, so the duplicate **silently promotes** a claim on one observation — violating [ADR-0011](decisions/ADR-0011-standing-is-earned-by-independent-corroboration.md) — and nothing in history says which increments were real. The row must be claimed **before** the model call; that is what makes retry ≠ replay |
| 2 | **The four ingest-time observation fields (O3, O4, A2-A4)** | `occurred_at` vs `ingested_at`, permission label, content hash, raw payload. Each is knowable only at fetch. **Because Q10 is open, store the source's permission metadata verbatim and unnormalised alongside whatever label is invented** — the normalisation is precisely the part Q10 will change |
| 3 | **Evidence as a joinable table (EV1)** | Three consumers are joins: a reviewer opening a run, DISTINCT-run corroboration, and the tenant deletion route. A count retrofits to a join only by re-deriving which observations backed each version, and version history does not record it |
| 4 | **The rebuild invariant (O5)** | The meta-property: it is what makes most other things reversible. What breaks it is any write of information never observed — an authoring UI writing claims directly, `propose_claim` writing without minting an observation, a probe writing a claim instead of an observation. **You cannot tell later which rows lacked a log entry** |
| 5 | **Claim + evidence in one transaction (CS1)** | *"A claim without evidence must be an unreachable state."* Rows written outside the transaction cannot be repaired. **The outbox is not in this group** — it has its own trigger and is additive |
| 6 | **Tenant in the key ([ADR-0016](decisions/ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md))** | A primary-key migration across every table and query — and the interim rows may already have leaked **with no signal**, which is the entire premise of the ADR |
| 7 | **Bitemporal columns ([ADR-0023](decisions/ADR-0023-bitemporal-validity-on-claims.md))** | *"What did we believe in June"* is permanently unanswerable for every row written before the columns existed |
| 8 | **The deletion route ([ADR-0017](decisions/ADR-0017-deletion-route-before-retirement.md))** | A store added without a route fails it loudly — which is the good case. The bad case is that it is added and quietly skipped |

**Clock discipline is irreversible for a different reason: code shape, not data
loss.** Once `wall_now()` calls are scattered, the CI test becomes unaddable
because the allowlist would have to include everything. `08-build-order.md` §5
lists removing it under **"Never."**

**Projections and replay/rebuild are consequences of O5, not independent
properties.** Listing them separately double-counts.

### 8.3 The knowledge plane's own invariants, classified

Classified against the plane's existing invariant codes rather than a new list —
a parallel taxonomy would not discharge Q8 and would add a fourth vocabulary to
a corpus that already logs two as an unresolved contradiction.

| Codes | Verdict | Note |
|---|---|---|
| O1-O5 · A1-A4 · X1-X3 · CS1-CS5 · EV1-EV3 | **REQUIRED NOW** | Six of the eight irreversible properties live here |
| AD1-AD2 · E1-E2 · C1-C4 · WM1-WM2 · R1-R4 · CA1 | **REQUIRED NOW** | Cheap now, and each is a correctness property rather than a scale one |
| CL1-CL4 | **REQUIRED NOW** | CL1 especially: a capability reading an ambient Principal cannot be exposed over MCP later without a refactor |
| CR1-CR3 | **REQUIRED NOW** for detection; CR1's *gating* is **REQUIRED LATER** | Severity is undefined until Q15 |
| V1-V3 | **REQUIRED LATER** — Phase 3 | `verifiable_by` is empty. V1 (a probe writes an observation, never a claim) is **REQUIRED NOW as a rule**, because violating it breaks O5 |
| M1-M6 (memory) | **ONLY IF TRIGGERED** | The memory subsystem is a mechanism over state categories, not a Phase 1 store |
| MC1-MC3 (MCP) | **REQUIRED LATER** — Phase 4, and Q9 first | |
| PS1 · PS2 · PS3 | **REQUIRED NOW** | One transaction; state separation; a tested deletion route |
| PS4 (version CAS) | **ONLY IF TRIGGERED** | With one writer this is theatre. The trigger is a second ingestion worker |
| P1-P5 (Principal Agent) | **REQUIRED LATER** — Phase 6, partly BLOCKED | |
| EL1-EL5 (evaluation) | **REQUIRED NOW** for EL1 (noise floor first); rest Phase 1-4 | An effect size without its error term is a number, not a result |

### 8.4 The distributed properties, as an index into the above

| Property | Verdict | Where it is held |
|---|---|---|
| Stable identity | **REQUIRED NOW** | X1 — irreversible |
| Idempotency (re-delivery a no-op) | **REQUIRED NOW** | A4, X1 |
| Transactional boundaries | **REQUIRED NOW** | CS1, PS1 |
| Replay / rebuild | **REQUIRED NOW** | O5 |
| Projections | **REQUIRED NOW** | WM1-WM2 (a consequence of O5) |
| Multi-tenant isolation | **REQUIRED NOW** | CS4, ADR-0016 — irreversible |
| Permission propagation | **REQUIRED NOW** | O4, A3, R4 — irreversible |
| Clock discipline | **REQUIRED NOW** | Irreversible by code shape |
| Observability | **REQUIRED NOW** | `07-brain-observability.md` — signals before tuning |
| Consistency boundaries | **REQUIRED NOW**, as a *statement* | One substrate, one transaction. The statement is the work; the enforcement is PS1 |
| Event delivery (outbox) | **ONLY IF TRIGGERED** | When the first consumer reacts to a knowledge-system event |
| Retries | **ONLY IF TRIGGERED** | Additive. Safe because X1 already makes re-extraction identity-stable |
| Failure recovery | **REQUIRED LATER** | Continuous, claim-based — not boot-only |
| Leases · version CAS | **ONLY IF TRIGGERED** | A second ingestion worker. *"Before that it is theatre"* |
| Multiple ingestion workers · concurrent extraction | **ONLY IF TRIGGERED** | Ingestion latency exceeds a stated budget |
| Backpressure · poison records | **REQUIRED LATER** | Arrive with the second worker, not before |
| Worker ownership · partitioning | **REQUIRED LATER** | Only when one substrate cannot serve the event rate |
| Horizontal scaling | **REQUIRED LATER** | Same trigger |
| Operational diagnostics | **REQUIRED LATER** | |
| Leader election | **NOT REQUIRED** | Normatively rejected. Mutual exclusion is already per-entity via lease + version check; a leader would add a coordination point, a split-brain mode and a failover gap in exchange for a guarantee the design already has |

### 8.5 The single-writer invariant profile — Q8 and Q20

**[PROPOSED — this is the artefact Q8 asks for, and it needs the owner's
ratification before it is relied on.]** `01-architecture-map.md` §4.3 records
that this artefact does not exist; Q8 is **blocking before line one of runtime
code**, and Q20 says the same walk answers both. What follows is the walk. It
does **not** mark Q8 resolved — that is a ratification, not a document.

Verdicts: **APPLIES** · **WEAKENED** (holds in reduced form with one writer) ·
**DOES NOT APPLY** (exists only to arbitrate contention a single writer does not
have).

| # | Invariant, in brief | Verdict with one writer |
|---|---|---|
| I1 | `contracts/` imports nothing | **APPLIES** |
| I2 | Kernel is domain-agnostic | **APPLIES** — and ADR-0028 extends it to the knowledge core |
| I3 | No run state on a domain table | **APPLIES** (= PS2) |
| I4 | A package narrows the tool surface, never widens | **APPLIES** |
| I5 | Packages never mutate runtime state | **APPLIES** |
| I6 | Exactly one controller advances a session | **WEAKENED** — one writer gives it by construction, but it must survive **crash-restart overlap**, so the version check stays and the lease may be a single-process guard |
| I7 | Nothing scarce held across a model call | **WEAKENED** — no pool to exhaust, but the code shape is the point and retrofitting custody is expensive |
| I8 | Non-determinism inside an action; clock and randomness are ports | **APPLIES** — irreversible by code shape |
| I9 | Action result reused only on full identity match | **APPLIES** — *the* one that cannot be retrofitted. Roughly thirty lines |
| I10 | A NON_IDEMPOTENT result is never auto-replayed | **APPLIES** |
| I11 | A deadline aborts the real call | **APPLIES** — a timeout that only abandons the caller is a defect at any scale |
| I12 | Every advance checkpointed before the next | **APPLIES** — about crash recovery, not contention |
| I13 | Replay produces identical decisions | **APPLIES** |
| I14 | An EFFECTFUL tool needs a resolved approval, in the runner | **APPLIES** |
| I15 | Every tool declares an effect tag | **APPLIES** |
| I16 | Fetched content is data, never instruction | **APPLIES** |
| I17 | A park holds no process, connection or timer | **WEAKENED** — with one writer a held resource blocks only itself, but the design is identical either way |
| I18 | Only verified observations update knowledge | **APPLIES** — nominated as one of the two that carry the most weight |
| I19 | Learning and evolution never block the request path | **APPLIES** |
| I20 | Progress is never written to the event log | **APPLIES** |
| I21 | The Decision Engine names capabilities, never tools | **APPLIES** |
| I22 | Tool binding pinned into invocation identity at plan time | **APPLIES** — part of I9's identity |
| I23 | The Controller's only execution verb is `invoke_capability` | **APPLIES** |
| I24 | The Experience layer adds no durable event class | **APPLIES** |
| I25 | Only renderers write to a surface | **APPLIES** |
| I26 | Graph transitions legal-only and total | **APPLIES** |
| I27 | The ExecutionGraph is the only representation of in-flight work | **APPLIES** |
| I28 | Reconciliation is level-triggered and idempotent | **APPLIES** |
| I29 | Conditions are evaluated deterministically | **APPLIES** |
| I30 | A capability's step chain is declared, never computed | **APPLIES** |
| I31 | A terminal node is immutable | **APPLIES** |
| I32 | The graph projection to the Decision Engine is read-only | **APPLIES** |
| I33 | A third-party descriptor never supplies the local half | **APPLIES** |
| I34 | Every admitted remote tool carries a descriptor digest | **APPLIES** |
| I35 | A digest mismatch refuses before any call | **APPLIES** |
| I36 | QUARANTINED → ADMITTED needs a new admission record | **APPLIES** |
| I37 | A remote description renders in the untrusted channel | **APPLIES** |
| I38 | Remote-result taint blocks external effects | **APPLIES** |
| I39 | Remote credentials minted per action | **APPLIES** |

**The result, stated plainly: 36 apply unchanged, 3 weaken, none drops.**

**[INFERENCE]** That is a narrower answer than Q8's own hypotheses expected —
they name *"leases, version-CAS, relay claims, sweepers, worker pools,
per-tenant admission and budget ledgers"* as candidates to drop. The reason the
walk does not drop them is that **Q8's candidates are mostly components, and the
39 are mostly properties.** The components can be deferred; the properties they
would eventually enforce mostly cannot, because they are about crash recovery,
determinism and authority rather than about contention. The honest restatement:

> **Defer the machinery, keep the shape.** With one writer you do not need a
> worker pool, a relay, a sweeper or a budget ledger. You *do* still need
> action identity, checkpointing, effect tags, the approval gate, clock
> discipline and verification-before-knowledge — and each of those is cheap
> while there is no code and expensive once there is.

**What this means for §4.3's contradiction.** *"The architecture is
server-shaped and the named targets are not servers"* stands, but it is a
statement about **components**, not invariants. Roughly half the specified
*kernel* can be deferred. Roughly none of the specified *properties* can.

### 8.6 The topology path

Each step adds operational surface, and each is taken only when a named metric
requires it — never in advance.

| Stage | Topology | Move on when |
|---|---|---|
| 1 | One process, all roles | **Start here.** Local development must work this way |
| 2 | Separate ingestion from serving | Ingestion latency affects read latency |
| 3 | Multiple ingestion workers | Ingestion cannot keep up with a stated budget. **This is the lease/CAS trigger** |
| 4 | Separate the knowledge plane as a deployable | An egress or trust boundary requires it — a governance decision, not a deployment detail |
| 5 | Partitioned workers with ownership | One substrate can no longer serve the event rate |

**NORMATIVE.** Partition ownership, if it ever arrives, is an optimisation for
locality. **It must never become a correctness dependency**: wipe the ownership
table and the system must continue by falling back to open contention on
leases.

**NORMATIVE.** Lease expiry is evaluated against the **substrate's** clock,
inside the same statement that claims the lease — never against a worker's local
clock. This is the assumption that fails silently, and it is stated here because
no handbook chapter covers clock skew.

---

## 9. What becomes real in each phase

The build order is **not** rewritten. This maps architecture onto it.

| Phase | Architectural capability that becomes real |
|---|---|
| **0 · Decide** | No architecture. Three artefacts: the source-precedence policy with a named owner, the single-writer invariant profile (§8.5, awaiting ratification), and the Q7 schema reconciliation. **The import boundary and its lint rule are established here, before there is code to violate them** |
| **1 · One source, end to end** | **The minimum real knowledge substrate.** The observation log as system of record; admission; entity anchoring; identity-keyed extraction; the claim store with evidence and the six temporal fields; deterministic reconciliation; contradictions; structural retrieval; the capability layer as four functions with CL1-CL4; the tested deletion route. **Every one of the eight irreversible properties lands here or not at all** |
| **2 · Second source** | **Cross-source reconciliation.** Entity resolution stops being free. The source-precedence policy becomes load-bearing rather than theoretical. This is where the domain/core split of ADR-0028 gets its first real pressure |
| **3 · Temporal + verification** | **The temporal and verification machinery.** As-of queries, supersession chains, the probe loop. V1-V3 activate. The bitemporal columns written in Phase 1 start paying |
| **4 · External agents** | **The stable capability surface.** MCP as a strict read-only projection with *fewer* capabilities than the internal surface. Q9 decided first. CL1's explicit Principal is what makes this a projection rather than a refactor |
| **5 · Breadth + participation** | Admission tuned against harder sources. The participation ladder's first rung, with a pre-registered threshold and automatic demotion |
| **6 · Principal Agent** | **The execution plane becomes a first-class executable substrate** — and not before. A Principal Agent as a Run; grants and delegation; park and resume across a restart. The 39 invariants acquire something to be enforced against |
| **7 · Organizational structures** | Goals, decisions with sealed predictions, commitments, the outcome ledger. **Gated on an organizational act, not on engineering** |
| **8 · Controlled autonomy** | Runtime capabilities activate progressively — policy, budgets, the effect ledger, the autonomy ladder rung by rung, each with a pre-registered threshold and automatic demotion |
| **9 · Autonomous workflows** | **Not designed.** Distribution, learning and evolution belong here or later, and only when a trigger fires |

---

## 10. What the two engineering references taught us

Two bodies of work were studied as **engineering references**, not as
architecture to copy: this repository's own runtime specification, and
SurrealDB's published Agent Memory documentation.

### 10.1 From the runtime specification

**[FACT — in this repository]** The specification already contains the mature
runtime concepts this architecture will eventually need: an ExecutionGraph as
the single representation of in-flight work, content-addressed action identity,
leases with version CAS, parking that holds no resources, budgets on a
reserve-then-settle model, an effect ledger, a transactional outbox, and 39
enforceable invariants each naming its test.

**The three transferable lessons, none of which is a directory name:**

1. **Dependency direction enforced in CI, not in review.** A rule that is only
   prose is a convention. `.importlinter`-style contracts are what turn *"the
   Controller never calls a model"* from a promise into a build failure.
2. **One execution model.** *"The ExecutionGraph is the plan, the state, the
   progress, the dependencies and the checkpoint. Nothing else may represent
   what we are doing."* The knowledge-plane analogue is O5: one system of
   record, everything else derived.
3. **Normative versus implementation note, labelled.** Contracts, invariants and
   dependency direction are normative; concurrency numbers, timeouts and
   **file-level decomposition** are free to change. That distinction is why
   doc 17 is short.

**What should not be copied:** the ~2,000-line directory tree. It is explicitly
an implementation note, it describes a system with no code, and reproducing its
shape for the knowledge plane would be architecture ahead of requirement.

### 10.2 From SurrealDB Agent Memory

Product name confirmed as **SurrealDB Agent Memory**; *Spectron* is its former
project name, still visible in its configuration surface. All claims below are
from its published documentation, cited. A minority of claims about commercial
terms could not be fetched directly and are not relied on here.

**[EVIDENCE]** It independently arrives at six positions this architecture had
already taken, which is the useful finding — not that we are right, but that
these are the choices a serious team makes when it builds this category:

| Their position | Ours |
|---|---|
| *"No fact-bearing record is anonymous. Provenance is a structured field, not an afterthought in application logs."* | EV1-EV3 |
| Memory is *"tri-temporal and non-deleting. Supersession and aging replace blind overwrite."* | [ADR-0023](decisions/ADR-0023-bitemporal-validity-on-claims.md), CS3 |
| Conflicts become explicit **uncertainty** records — *"does not pick a silent winner or apply last-write-wins"* | CR1-CR3, and abstention as a first-class outcome |
| A confidence floor gates supersession; a low-confidence extraction cannot erase an established fact | [ADR-0011](decisions/ADR-0011-standing-is-earned-by-independent-corroboration.md)'s load floor |
| Authority is *"a reconciliation policy, not a second copy of the universe hidden in another engine"* | [ADR-0006](decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md) |
| *"Cross-store stitching is rejected as an architectural choice, not a feature gap"* | PS1 and [ADR-0009](decisions/ADR-0009-no-graph-database.md) |

*Sources: [principles and goals](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/index/architecture/principles-and-goals.mdx),
[provenance](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/index/mental-model/provenance-and-traceability.mdx),
[tri-temporal model](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/index/architecture/tri-temporal-model.mdx),
[reconciliation](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/index/reasoning/reconciliation-and-supersession.mdx).*

**[EVIDENCE] The sharpest single finding is a divergence.** Their scope check is
fail-closed but returns **empty**. ADR-0016 requires a denied read to **raise**,
and its alternatives table rejects filter-returns-empty because *"a filter
returns an empty result, which is indistinguishable from having no data and
produces no signal. A bug that should page someone looks like a quiet
afternoon."* Their own documentation then names that exact failure from the
inside: *"the symptom is quiet: scoped reads return empty, not refused, so a
client that polls for its own writes waits instead of failing."*
[Source](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/index/mental-model/contexts-and-scope.mdx).
**Two designs reached the same failure mode from opposite directions. R3 keeps
its stricter rule.**

**[EVIDENCE] Where they stopped.** Entity identity is an exact composite key —
*"no fuzzy, phonetic, or embedding-based matching on the write path"* — with no
alias field and no automatic merge: *"merging them is a decision for the layer
above."* This architecture puts entity resolution **inside** Phase 2 and already
calls it *"the component most likely to be underestimated."* **Their punt is
support for that assessment, not a reason to copy it.**

**[EVIDENCE] What challenges us.** Their *"accuracy promise"* page contains no
benchmark, no eval set and no comparative result; accuracy is reframed from
retrieval quality to **verifiability** — *"you can point to records, spans,
traces, and time axes, not only to a model transcript."*
[Source](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/index/welcome/accuracy-promise.mdx).
That is close to what `07-brain-observability.md` §3 already argues. It also
means there is **no published number to compare against**, which bears directly
on Q17 and Q19.

**[EVIDENCE] One idea worth taking seriously and not adopting yet.** They store
retrieval, decision and response traces as **first-class graph nodes that feed
back into ranking** — *"traces are memory, not logs… inputs to future ranking
and consolidation, not only external telemetry."*
[Source](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/index/architecture/traces-and-evolution.mdx).
Our flight recorder is deliberately observability only. Feeding traces back into
ranking is close to what
[ADR-0024](decisions/ADR-0024-no-autonomous-knowledge-curation.md) forbids, and
the reason is unchanged: a loop that reweights a store against a signal that
cannot see what it is destroying. **Recorded as an idea with a real argument
against it, not as a gap.**

### 10.3 Adopt or build

**[RECOMMENDATION]** Adopting an existing agent-memory engine in place of the
claim store is **not currently viable**, for reasons that are about fit rather
than quality: no in-process mode (*"There is **no** supported in-process API
that runs extraction and recall inside your application binary"* —
[source](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/index/quickstarts/embedded.mdx)),
embeddings **fixed deployment-wide** to a single vendor's model
([configuration reference](https://raw.githubusercontent.com/surrealdb/docs.surrealdb.com/main/src/content/agent-memory/reference/configuration.mdx)),
no published
retrieval-quality evidence, no entity merging, and — decisively — **no concept
of a kind whose type determines what it has authority over**, which is the one
structural idea [ADR-0003](decisions/ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md)
rests on.

**That is a fit assessment, not a verdict on the category.** The existence of a
serious, well-argued implementation is **positive evidence that these
engineering problems are buildable** — which is the more useful conclusion.
Recorded as **Q22** with a trigger, not decided here.

---

## 11. What this document does not decide

| | |
|---|---|
| **Q7** — the claim-store schema | DISPUTED between two documents, now three. §6.1. **Do not build a schema against §5's vocabulary** |
| **Q8 / Q20** — the invariant profile | §8.5 is the artefact. It is **PROPOSED** and awaits ratification |
| **Q10** — overlapping permissions | Open, and `scope` sits inside claim identity. See ADR-0028 |
| **Q15** — blocking vs advisory contradictions | Open; CR1's gating waits on it |
| **Q22** — adopt versus build | New, from §10.3 |
| The contradiction-register naming | Blocked on Q7. Candidates on file in `15-vocabulary.md` §5 |
| File-level decomposition | **Deliberately unspecified.** See `17-target-repository-structure.md` |

**Two contradictions are registered by this document** and recorded in
`01-architecture-map.md` §4: the third `entity_store` / `fact_store` shape in
the runtime specification's own `knowledge/` tier (§6.1), and the specification
§13 layer-stack versus forbidden-edge disagreement about `tools` (§4.4).

---

## Related

[ADR-0027](decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md) ·
[ADR-0028](decisions/ADR-0028-the-knowledge-core-is-domain-agnostic.md) ·
[`17-target-repository-structure.md`](17-target-repository-structure.md) ·
[`01-architecture-map.md`](01-architecture-map.md) ·
[`08-build-order.md`](08-build-order.md) ·
[`10-open-questions.md`](10-open-questions.md)
