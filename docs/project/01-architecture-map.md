# Architecture Map

**Status of this document:** a map of *designed* architecture. At the audit
date, **no component below is implemented in this repository.** Every
"Implementation status" row says so explicitly; none is an oversight.

Read `PROJECT_BOOTSTRAP.md` §0 for the meaning of the status labels.

---

## 1. The whole system, in one figure

```
   EXTERNAL AGENTS  (Claude, Codex -- third-party, not ours)
        |                                    ^
        | MCP calls                          | context, cited
        v                                    |
  +===========================================================+
  |  KNOWLEDGE SYSTEM MCP      PROPOSED, deferred             |
  |  a thin projection. no logic of its own.                  |
  +===========================================================+
        |
        v
  +===========================================================+
  |  CAPABILITY LAYER          ONE definition of what the     |
  |  context_for  entity  history  why  conflicts  as_of      |
  |  propose_claim                                            |
  |  Every surface resolves a Principal FIRST, then calls      |
  |  these. A surface that reaches past this layer has         |
  |  created a second ACL implementation.                      |
  +===========================================================+
        |                |                |
   agent tools       HTTP API          MCP (later)
   (curried with
    the Principal)
        |
        v
  +===========================================================+
  |                  THE KNOWLEDGE SYSTEM                     |
  |                                                            |
  |  SOURCE ADAPTERS -> OBSERVATION LOG (system of record)     |
  |                            |                               |
  |                       ADMISSION      most things stop here  |
  |                            |                               |
  |                     ENTITY RESOLVE                          |
  |                            |                               |
  |                        EXTRACT       the one LLM step       |
  |                            |                               |
  |                CLASSIFY + RECONCILE  deterministic          |
  |                            |  ONE TRANSACTION               |
  |                            v                               |
  |                      CLAIM STORE                            |
  |     claims | versions | evidence | entities | relations     |
  |            |            |              |                    |
  |      WORLD MODEL   RETRIEVAL     CONTRADICTION              |
  |       (a VIEW)       INDEX         REGISTER                 |
  |                    (disposable)   (gates actions)           |
  |                            |                               |
  |                    CONTEXT ASSEMBLY                         |
  |                                                            |
  |  + VERIFICATION LOOP (not part of the pipeline): scheduled  |
  |    probes that re-establish whether a claim is still true.  |
  |    It writes OBSERVATIONS, so it re-enters at the top.      |
  +===========================================================+
        |
        v  knowledge-system tools, curried with the Principal
  +===========================================================+
  |  PRINCIPAL AGENT                                           |
  |  OBSERVE -> ASSESS -> DECIDE -> [AUTHORITY] -> COMMIT       |
  |          -> DELEGATE -> (runtime) -> MEASURE -> OUTCOME     |
  |  NOT a layer inside the runtime. A CLIENT of it,            |
  |  implemented as a Run.                                      |
  +===========================================================+
        |  submits goals through the Edge, like any client
        v
  +===========================================================+
  |  AGENT RUNTIME                                             |
  |  SURFACE | EDGE | SUBSTRATE | KERNEL | PORTS | DOMAIN       |
  |  narrow waist: commands down, events up, no shared tables   |
  |  Run / Episode / Step / Activity / Park                     |
  |  ExecutionGraph is the only representation of in-flight work|
  +===========================================================+
        |
        v
  ENVIRONMENT ADAPTERS -> the world
  + MEMORY subsystem (a mechanism over several state categories)
  + EVALUATION (offline; noise floor first)
  + VERIFICATION (deterministic; before knowledge)
  + PERSISTENCE (one transactional substrate)
```

### The boundaries that carry the most weight

Three rules do most of the structural work. Weakening any of them changes a
guarantee from *structural* to *conventional*, which is the failure mode to
watch for.

1. **The narrow waist.** Commands go down, events come up, and no two layers
   share a table. The kernel is domain-agnostic and imports nothing upward.
2. **The agent reaches the knowledge system only through tools.** Not an import, not a
   shared repository object, not a context injected at graph build.
   [ADR-0012](decisions/ADR-0012-the-agent-reaches-the-brain-only-through-tools.md)
3. **Every surface resolves a Principal first and then calls the same
   capability layer.** Two ACL implementations is one ACL implementation that
   is wrong.

---

## 2. Component reference

Each component below carries the same eight fields. Where a field cannot be
established from the documents, it says **UNKNOWN** rather than guessing.

---

### 2.1 Source Adapters

| Field | |
|---|---|
| **Purpose** | Turn a source-specific feed (Git, Jira, CI, meetings, Slack, docs) into the one normalised observation shape. The only source-specific code in the system. |
| **Owns** | Source API clients, pagination and backfill, shape normalisation, re-delivery detection, thread reconstruction. |
| **Does not own** | Interpretation of any kind. An adapter that extracts meaning has moved the extraction stage into six places. |
| **Inputs** | Source APIs, webhooks, polls. |
| **Outputs** | Observations appended to the observation log. |
| **Dependencies** | The observation shape, which must be fixed before the first adapter is written. |
| **Invariants** | *A1.* An adapter never writes a claim. *A2.* An adapter emits `occurred_at` and `ingested_at` separately. *A3.* An adapter attaches the source's permission label at ingest; it is never reconstructed later. *A4.* Output is content-hashed, so re-delivery is a no-op. |
| **Status** | **DESIGNED.** No adapter exists, for any source. The observation shape must be fixed before the first one is written. |

---

### 2.2 Observation Log — the system of record

| Field | |
|---|---|
| **Purpose** | Hold every raw, uninterpreted observation, append-only, forever (subject to retention). Everything downstream is derived from it. |
| **Owns** | Raw payload, source, actor, `occurred_at`, `ingested_at`, content hash, permission label. |
| **Does not own** | Meaning. Nothing is interpreted here. |
| **Inputs** | Source adapters; the verification loop's probe results, which re-enter as observations. |
| **Outputs** | An ordered stream consumed by admission. |
| **Dependencies** | Persistence. |
| **Invariants** | *O1.* Append-only. *O2.* Raw payload retained, so downstream structures are rebuildable. *O3.* `occurred_at` and `ingested_at` are separate columns from day one — a log recording only ingestion time can never recover truth time. *O4.* The permission label is captured at ingest. *O5.* **The rebuild invariant:** drop the claim store, index, world model and contradiction register, replay the log, and you arrive at the same state. If you cannot, something downstream holds information that was never observed. |
| **Status** | **DESIGNED.** [ADR-0004](decisions/ADR-0004-observation-log-is-the-system-of-record.md) |

O5 is the most valuable property in the architecture and it is cheap only if
decided on day one. It is what makes reprocessing — better extraction, a new
predicate, a corrected authority ordering, applied to *history* — the normal
way the knowledge system improves rather than a disaster-recovery story.

---

### 2.3 Admission

| Field | |
|---|---|
| **Purpose** | Decide whether an observation is worth processing at all. **Most things stop here.** |
| **Owns** | The discard decision and the discard *rate* as a headline metric. |
| **Does not own** | Extraction, or any judgement about what an observation means. |
| **Inputs** | Observations. |
| **Outputs** | An admitted subset; a discard-rate signal. |
| **Dependencies** | Observation log. |
| **Invariants** | *AD1.* Deterministic rules run first; a cheap model runs second, and only if the deterministic stage is inconclusive. *AD2.* The discard rate is a headline metric before the first source is enrolled. |
| **Status** | **DESIGNED.** Named as "the stage everyone omits." A week of one team's messages contains perhaps a dozen durable claims; ingesting everything makes cost rise linearly with headcount while retrieval precision falls. |

This is the handbook's own **Admission control** (Ch2, Ch23), specialized to
organizational observations rather than run submissions — not a fresh
coinage.

---

### 2.4 Entity Resolution

| Field | |
|---|---|
| **Purpose** | Resolve mentions ("QIC", "the QIC flow", "quote-issue-confirm", a service name in a repo) to stable identities. |
| **Owns** | The entity identity table: stable ids, type, aliases, source ids. |
| **Does not own** | Anything *asserted about* an entity. Identity is schema; assertions are claims. |
| **Inputs** | Admitted observations. |
| **Outputs** | Resolved entity references; unresolved mentions, kept as unresolved. |
| **Dependencies** | Observation log, persistence. |
| **Invariants** | *E1.* Resolution runs **before** extraction — extraction that does not know which entity it is discussing produces claims that cannot be joined, and joining them afterwards is strictly harder than never splitting them. *E2.* Anchor on system identifiers; curate aliases; accept unresolved mentions rather than forcing a match. |
| **Status** | **DESIGNED**, and flagged as "the component most likely to be underestimated." **This is also a point of conflict between two documents — see §4.1.** |

---

### 2.5 Extraction

| Field | |
|---|---|
| **Purpose** | Propose claims from an observation, in a closed predicate vocabulary. The one place an LLM is unavoidable. |
| **Owns** | The extraction prompt, the extractor version, the closed output schema. |
| **Does not own** | Whether a claim is accepted. Extraction *proposes*. |
| **Inputs** | One observation, with entities already resolved. |
| **Outputs** | Zero or more proposed claims; an out-of-vocabulary rejection rate. |
| **Dependencies** | Predicate registry, entity resolution, an inference provider. |
| **Invariants** | *X1.* **Identity-keyed:** every extraction attempt has a deterministic id derived from `(observation_id, extractor_version)`, it is a UNIQUE key, and the row is claimed **before** the model call. *X2.* Out-of-vocabulary extractions are rejected, and the rejection rate is the signal that the vocabulary needs extending. *X3.* The model proposes and never writes. |
| **Status** | **DESIGNED.** [ADR-0018](decisions/ADR-0018-identity-keyed-extraction-first.md), [ADR-0010](decisions/ADR-0010-the-model-proposes-and-never-writes.md) |

X1 is roughly twenty lines and is the cheapest correctness win available.
Without it, a re-delivered observation is re-extracted, costs a second model
call, and produces a *different* claim — so the duplicate is not even
recognisable as one afterwards.

---

### 2.6 Classification and Reconciliation

| Field | |
|---|---|
| **Purpose** | Decide what a proposed claim is, relative to what is already known at that identity: new, reinforcing, contradicting, superseding, refining, coexisting, or duplicate. |
| **Owns** | The relationship decision and the version write. |
| **Does not own** | The authority ordering, which is configuration it reads. |
| **Inputs** | A proposed claim; the current claim at that `(subject, predicate, scope)` identity. |
| **Outputs** | A claim version; possibly a contradiction record; an outbox event. |
| **Dependencies** | Claim store, predicate schema registry, source-precedence policy. |
| **Invariants** | *C1.* Deterministic. The first tests use no model. *C2.* Runs as part of **writing**, not as a later pass — otherwise there is a window in which the store holds unreconciled contradictions and serves them. *C3.* Supersession versus contradiction is decided by the predicate's declared `single_valued` property, which cannot be read from two sentences. *C4.* Nothing here raises a claim's standing; only independent evidence does. |
| **Status** | **DESIGNED.** |

The failure to design against is not a *missed* contradiction but a **false**
one: a system that treats every scope overlap as a conflict drives every claim
in a busy scope below the load floor, and looks healthy throughout.

---

### 2.7 Claim Store

| Field | |
|---|---|
| **Purpose** | Hold current claims and their full version history with evidence. |
| **Owns** | `claims`, `claim_versions`, `evidence`, and (per the knowledge system design) `entities` and `relations`. |
| **Does not own** | The observation log, which is upstream and authoritative for history; the retrieval index, which is downstream and authoritative for nothing. |
| **Inputs** | Classified claims, in one transaction with their evidence and their outbox event. |
| **Outputs** | Claims to retrieval, projections, and the contradiction register. |
| **Dependencies** | Persistence. |
| **Invariants** | *CS1.* A claim and its evidence commit in the **same transaction**; a claim without evidence must be an unreachable state. *CS2.* Claim identity is `(subject, predicate)` within a scope — the **object is deliberately not part of the identity**, so a contradiction is a key collision rather than two rows that both retrieve. *CS3.* Append-only versions; retirement is not deletion. *CS4.* Tenant in the key. *CS5.* Every claim carries kind, predicate, subject, object, scope, source_class, validity interval, confidence, permission label. |
| **Status** | **DESIGNED.** **The exact table set is disputed between two documents — see §4.1.** |

---

### 2.8 Evidence and Provenance

| Field | |
|---|---|
| **Purpose** | Record what each claim rests on, durably enough that a human can follow it to a source months later. |
| **Owns** | Evidence rows: step/observation references with locators and digests, and a `derived_from` chain. |
| **Does not own** | Confidence. Evidence is the input to standing; it is not the score. |
| **Inputs** | The observation(s) a claim was extracted from. |
| **Outputs** | Evidence handles returned with every claim. |
| **Dependencies** | Observation log, claim store. |
| **Invariants** | *EV1.* Evidence is a **table of references**, never an integer count — a count cannot be joined on, and three needs require joining: a reviewer needs a run to open, corroboration must count DISTINCT runs, and the deletion route must find claims citing a departing tenant's runs. *EV2.* Handles are **server-minted**; a caller-supplied id is the whole attack. *EV3.* Evidence must **outlive the run** — a claim's basis must be inspectable months later. |
| **Status** | **DESIGNED.** EV3 sits in tension with the runtime's own evidence-handle mechanism, which is deliberately run-scoped and ephemeral — see §3, *"What must stay runtime-generic."* The resolution is to split the two lifetimes: the knowledge system adds a **durable** store with the same discipline, and does not modify the run-scoped one. *(Corrected 2026-09-14 — this row previously cited an external artefact nobody here can read, which [ADR-0025](decisions/ADR-0025-no-external-codebase-is-evidence.md) forbids. It escaped the provenance purge because its wording did not match the guard's pattern.)* |

Provenance is **not a layer** — it is a property. Drawing it as a layer invites
an implementation in which a claim can exist without it, which is the one state
that must be unreachable.

---

### 2.9 Contradiction Register

| Field | |
|---|---|
| **Purpose** | Hold open contradictions as first-class objects that **gate actions**, rather than as warning strings. |
| **Owns** | Contradiction records with severity (blocking vs advisory) and owners. |
| **Does not own** | Resolution. A contradiction is resolved by new observations, not by a cleanup job. |
| **Inputs** | Classification results. |
| **Outputs** | `brain.conflicts`; blocking signals that refuse action minting; the input to the participation check. |
| **Dependencies** | Claim store. |
| **Invariants** | *CR1.* A blocking contradiction prevents an action from being minted against the affected claims. *CR2.* Contradictions are **never dropped from assembled context for budget reasons** — see §2.12. *CR3.* Precision is measured: contradictions raised vs confirmed-real-by-owner. A detector with low precision gets muted within a week. |
| **Status** | **DESIGNED.** **Existence as a separate table is disputed — see §4.1.** |

---

### 2.10 World Model

| Field | |
|---|---|
| **Purpose** | A queryable projection of current organizational state — entities, ownership, relationships, current behaviour. |
| **Owns** | Nothing. It is a **materialised view**. |
| **Does not own** | Any fact. "Team X owns Service Y" is a claim with a source, a validity interval, a confidence and an authority — not a schema column. |
| **Inputs** | The claim store. |
| **Outputs** | Fast reads for context assembly. |
| **Dependencies** | Claim store. |
| **Invariants** | *WM1.* **The delete test:** delete it. If information is lost, it was not a projection and you now have two sources of truth. If only rebuild time is lost, it is a cache. *WM2.* Nothing writes to it except the rebuild. |
| **Status** | **DESIGNED.** [ADR-0005](decisions/ADR-0005-the-world-model-is-a-projection-not-a-store.md) |

The related-but-distinct construct in the runtime handbook is the **belief
store**: beliefs carry a claim, provenance, an event-log position and a scope,
and are invalidated by scope overlap against the durable ordered effect stream
rather than by a TTL. Beliefs and memories differ in exactly one property —
**whether deleting the store costs correctness.** Beliefs are re-derivable by a
probe; memories are not.

---

### 2.11 Memory Subsystem

| Field | |
|---|---|
| **Purpose** | The write path and lifecycle by which a run's experience becomes a durable claim: propose → abstract → route → classify → apply. |
| **Owns** | A write path and a lifecycle. **It owns no facts about the world.** |
| **Does not own** | A store. It operates over several, and it does not become the owner of anything merely by remembering it. |
| **Inputs** | Run observations at run end. |
| **Outputs** | Claims routed to the correct store; four memory events on the existing outbox. |
| **Dependencies** | Persistence, the outbox, the state-classification procedure. |
| **Invariants** | *M1.* **The routing rule:** a learned claim is *harness* state if it is true of the SYSTEM; it is *domain* state, tenant-scoped, if it is true of a CUSTOMER. *M2.* The write path never fails a run. *M3.* The read path never fails a step. *M4.* Nothing in the lifecycle raises a claim's standing except independent evidence. *M5.* Untrusted-derived claims may reach PROVISIONAL and never ACTIVE. *M6.* An imperative ("always do X") is rejected at the write path. |
| **Status** | **DESIGNED.** [ADR-0007](decisions/ADR-0007-memory-is-a-mechanism-not-a-state-category.md) |

M1 is why there are **two** long-term stores and that is not a compromise:
system-true claims go in a git-tracked file (enumerable, diffable, revertable,
attributable by line); customer-true claims go in a database with the tenant in
the key. Git history cannot be redacted, so a customer fact committed there is
an unrecoverable governance breach with no deletion route.

---

### 2.12 Retrieval and Context Assembly

Two components, deliberately split: **retrieval selects; assembly budgets and
formats.** Different owners, different failure modes.

| Field | Retrieval | Context Assembly |
|---|---|---|
| **Purpose** | Select the candidate claim set | Fit it to a budget and format it |
| **Owns** | Scope resolution, authorization, validity and standing filters, ordering | Budget arithmetic, ordering into the prompt, the citation format |
| **Does not own** | Ranking models (none exists yet) | Selection |
| **Inputs** | A Principal, a scope or question, `as_of` | A ranked claim set, a token budget |
| **Outputs** | An ordered, authorized, valid claim set | The assembled context block |
| **Dependencies** | Claim store, permission model | Retrieval |
| **Invariants** | *R1.* **Scope-first, not similarity-first** — the scopes are known before the query rather than inferred from it. *R2.* Authorization, validity and standing are one SQL statement. *R3.* A denied read **raises**; it never returns empty. *R4.* The permission predicate is a **pre-filter inside the store implementation**, never applied by the caller and never post-applied. | *CA1.* **Three things are never dropped for budget:** contradictions, provenance pointers, temporal qualifiers. |
| **Status** | **DESIGNED** | **DESIGNED** |

CA1 is worth stating at length because each item fails differently. Dropping a
*contradiction* produces a confident answer while holding evidence against it —
worse than no answer, and the exact failure the architecture exists to prevent.
Dropping a *provenance pointer* (a claim id and a source reference, tens of
tokens) makes the grounding gate unable to verify the answer and the citation
decorative. Dropping a *temporal qualifier* — "since April", four tokens —
converts a precise answer into a wrong one.

R4 has a measured basis: approximate-nearest-neighbour indexes apply metadata
filters *after* walking the graph. Under a high-selectivity filter — which
`tenant_id` always is — the candidates returned by the walk can all fail the
filter and recall collapses. The single query shape this workload always has is
the shape ANN search handles worst.

---

### 2.13 Verification Loop

| Field | |
|---|---|
| **Purpose** | Re-establish whether a claim is still true, proactively, without waiting for a contradicting observation. |
| **Owns** | Scheduled, cheap, deterministic probes for probe-verifiable predicates. |
| **Does not own** | Claims. It writes **observations**, which re-enter the pipeline at the top. |
| **Inputs** | Claims whose predicate declares a `verifiable_by` probe. |
| **Outputs** | Observations; a verification-status distribution metric. |
| **Dependencies** | Predicate registry, observation log. |
| **Invariants** | *V1.* A probe writes an observation, never a claim directly. *V2.* Probes are read-only against the systems they inspect. *V3.* `unverified` is the default status, and it is honest. |
| **Status** | **DESIGNED.** This is the **only proactive mechanism** in the whole design. Every other mechanism — corroboration, contradiction, decay, invalidation — is reactive. It covers only probe-verifiable predicates, which will be a minority. |

---

### 2.14 Capability Layer

| Field | |
|---|---|
| **Purpose** | The single definition of what the knowledge system can do. Every surface — agent tools, HTTP, MCP, CLI — resolves a Principal and calls these. |
| **Owns** | `context_for`, `entity`, `history`, `why`, `conflicts`, `as_of`, `propose_claim`. |
| **Does not own** | Transport, session handling, or any surface-specific concern. |
| **Inputs** | An **explicit** Principal (never ambient), a question or scope, `as_of`, a budget, a result limit. |
| **Outputs** | Bounded, ranked, cited claim sets with evidence handles; open contradictions; validity intervals; **what was not found and what could not be resolved**. |
| **Dependencies** | Retrieval, claim store, contradiction register. |
| **Invariants** | *CL1.* Every capability takes an **explicit** Principal — a capability reading an ambient Principal cannot be exposed over MCP later without a refactor. *CL2.* Every capability returns provenance. *CL3.* Every result set is bounded. *CL4.* No surface reaches past this layer to the store. |
| **Status** | **DESIGNED.** Four cheap decisions (CL1–CL4) cost an afternoon now and prevent a rewrite later. |

---

### 2.15 knowledge system MCP Server

| Field | |
|---|---|
| **Purpose** | Expose a *subset* of the capability layer to external agents. |
| **Owns** | Transport and protocol only. **No logic of its own.** |
| **Does not own** | Authorization decisions, ranking, assembly — all of which live in the capability layer. |
| **Inputs** | MCP calls from external agents. |
| **Outputs** | Capability results. |
| **Dependencies** | Capability layer; a decided answer to "whose Principal is an MCP caller." |
| **Invariants** | *MC1.* A strict projection — deletable without losing anything. *MC2.* **Fewer** capabilities than the internal surface, not the same set: read-only at first, no `propose_claim`, no unbounded result set. *MC3.* The client never asserts an identity. |
| **Status** | **PROPOSED, deliberately deferred.** [ADR-0013](decisions/ADR-0013-mcp-is-a-projection-of-the-capability-layer.md) |

MCP creates two problems the internal surface does not have. **Identity:** a
coding agent connecting on behalf of an engineer means the IDE, the agent and
the knowledge system are three parties, and the token must carry an identity the knowledge system can
verify without trusting the middle one. **Structural containment is lost:**
internally, tool projection makes an unauthorised query *absent from the
schema*; an MCP client sees the same tool list as everyone, so enforcement
falls back to runtime checks in the capability layer.

---

### 2.16 Principal Agent

| Field | |
|---|---|
| **Purpose** | Hold authority in its own name, make commitments that outlive a run, and be judged on outcomes rather than delivery. |
| **Owns** | Goals it was given, objectives, decisions with sealed predictions, commitments, delegation grants, outcome records. |
| **Does not own** | **Four things it must never do:** set its own goals; execute work itself; grade its own outcomes; hold organizational knowledge in harness state. |
| **Inputs** | Organizational state changes as durable events; knowledge system context via tools. |
| **Outputs** | Goals submitted to the runtime through the Edge; commitments; decisions; outcome measurements. |
| **Dependencies** | Agent Runtime, knowledge system capability layer, authority/grant model. |
| **Invariants** | *P1.* It is a **Run**, not a layer — a client of the runtime, subject to every constraint a run is subject to. *P2.* Its tool set contains **no tool that touches the world directly**. *P3.* It may *propose* a goal and never *write* one. *P4.* An outcome verdict has a deterministic floor from a probe; the Principal Agent may only **lower** it. *P5.* Delegation narrows authority and never widens it. |
| **Status** | **DESIGNED.** [ADR-0014](decisions/ADR-0014-the-principal-agent-is-a-run-not-a-layer.md) |

P1 is the correction most likely to be missed. Drawn as a *layer between the
Surface and the Runtime*, it would put a decision loop in the Edge (which
translates and does not participate) and domain reasoning inside the kernel
(which is domain-agnostic by construction). As a Run, it inherits durable
execution, parking, crash recovery, budgets, and the existing audit trail for
free — none of which is cheap to rebuild.

P3 is a containment argument, not a policy preference: a Principal Agent judged
on whether goals are met, which can also write goals, **will** meet its goals.
It will not be misbehaving; it will be optimising exactly what it was asked to
optimise.

---

### 2.17 Agent Runtime

| Field | |
|---|---|
| **Purpose** | Drive leased, checkpointed work to completion, durably, verifiably, and reversibly. |
| **Owns** | Run/Episode/Step/Activity/Park; the ExecutionGraph; leases; checkpoints; the effect ledger; the transactional outbox. |
| **Does not own** | Any judgement. Every judgement lives behind one of six ports. The kernel decides nothing itself. |
| **Inputs** | Goals, approvals and signals through the Edge. |
| **Outputs** | Events up; effects applied through adapters; durable run state. |
| **Dependencies** | Persistence, ports, environment adapters. |
| **Invariants** | 39 numbered invariants in the specification §10. The two that carry the most weight: **I9** (action identity — reuse a result only on a full identity match; roughly thirty lines, and the only one that cannot be retrofitted) and **I18** (verification before knowledge). Also load-bearing: **I2** (kernel imports nothing upward), **I14** (an effectful tool is uncallable without a resolved approval, enforced in the runner rather than by prompting), **I16** (fetched content is data, never instruction), **I27** (the ExecutionGraph is the only representation of in-flight work). |
| **Status** | **DESIGNED.** 51 handbook chapters and a 5,000-line specification. **No code. None of the 39 invariants is enforced, because there is nothing to enforce them against.** |

---

### 2.18 Environment Adapters

| Field | |
|---|---|
| **Purpose** | Apply effects to the world and observe it, behind ports the kernel does not know the shape of. |
| **Owns** | Filesystem, VCS, HTTP, inference, clock, and scope/permission adapters. |
| **Does not own** | Effect policy. A tool *declares* an effect tag; it does not decide whether it may run. |
| **Inputs** | Capability invocations from the Controller. |
| **Outputs** | Effects, and observations of their result. |
| **Dependencies** | Ports. |
| **Invariants** | *EA1.* Every tool declares an effect tag; unknown third-party effect defaults to EFFECTFUL (I15). *EA2.* A descriptor fetched from a third-party server never supplies effect, idempotency, blast radius, permissions, approval, retry or timeout — offered values are **discarded, not merged** (I33). *EA3.* All non-determinism lives inside an action; clock and randomness are ports (I8). |
| **Status** | **DESIGNED.** |

EA2 is the invariant most likely to be softened during implementation, because
merging a server's declared effect *when we have no better information* reads
as pragmatic. It is not: it makes a talkative server more trusted than a silent
one, which inverts the property being relied on.

---

### 2.19 Verification (runtime)

| Field | |
|---|---|
| **Purpose** | Establish deterministically whether an effect achieved what it claimed. |
| **Owns** | Deterministic post-condition checks written **before** the work. |
| **Does not own** | Grading of subjective quality. |
| **Inputs** | The effect ledger and the world. |
| **Outputs** | A verification report; node FAILED / run PARTIAL on mismatch. |
| **Dependencies** | Effect ledger, environment adapters. |
| **Invariants** | *VR1.* **No model is involved.** *VR2.* Only verified observations update knowledge (I18). *VR3.* A model judgement may lower a passing verdict and may **never** raise a failing one. |
| **Status** | **DESIGNED.** [ADR-0015](decisions/ADR-0015-verification-before-knowledge.md) |

The reasoning behind VR1/VR3: a model asked to evaluate its own work shares a
training distribution, and therefore a set of blind spots, with the model that
produced it. It approves fluent, well-structured, wrong output because that is
what it was trained to prefer. This is the failure most likely to damage a
product, because a reliability defect produces an alert and a confidently wrong
result produces an artifact someone acts on.

---

### 2.20 Evaluation

| Field | |
|---|---|
| **Purpose** | Establish whether a change to the system made it better or worse, **with a number that carries its error term.** |
| **Owns** | The task set with oracles, the environment build/reset, the trial runner, graders on a lattice, the noise-floor estimator, per-slice metrics. |
| **Does not own** | Production behaviour. Evaluation is offline and never blocks the request path (I19). |
| **Inputs** | A pinned store snapshot, a task set, k rollouts. |
| **Outputs** | Effect sizes with error terms; per-slice gates. |
| **Dependencies** | Runtime, a pinned memory/claim snapshot. |
| **Invariants** | *EL1.* **The noise floor is measured first.** Until you have that number, every effect size is a number without its error term. *EL2.* Paired comparison, k rollouts, per-slice gating, cost in the denominator. *EL3.* Measured against a **pinned** store snapshot — a store's contents are a function of what runs have happened, so "the same memory" across two subjects is only meaningful if it is pinned. *EL4.* Retrying is forbidden in the test suite. *EL5.* Measured gains **do not sum.** |
| **Status** | **DESIGNED.** |

---

### 2.21 Persistence

| Field | |
|---|---|
| **Purpose** | One transactional substrate holding commands, events, run state, activities, budgets, approvals, claims, versions, and evidence. |
| **Owns** | Durability and transaction boundaries. |
| **Does not own** | Meaning. |
| **Inputs** | Writes from every component above. |
| **Outputs** | Reads; the outbox stream. |
| **Dependencies** | — |
| **Invariants** | *PS1.* A claim, its version, its evidence and its outbox event commit in **one transaction**. This is the decisive argument against a second store engine: split across engines it becomes a distributed transaction. *PS2.* No run state on a domain table; no domain truth in run state (I3). *PS3.* Every store declares and **tests** a deletion route before it ships. *PS4.* Optimistic concurrency by version CAS, with **re-classify on conflict** — not retry on conflict. |
| **Status** | **DESIGNED.** |

PS4's distinction matters: retrying a write on a version conflict re-applies a
classification that was computed against a *stale* current claim, silently
erasing whatever the winning writer decided.

---

### 2.22 External Agents

| Field | |
|---|---|
| **Purpose** | Third-party coding agents (Claude, Codex) that consume knowledge system context. |
| **Owns** | Nothing of ours. |
| **Does not own** | Any write path into the knowledge system, except `propose_claim`, which proposes and never writes. |
| **Inputs** | knowledge system MCP capability results. |
| **Outputs** | Their own work; observable traces if the workflow captures them. |
| **Dependencies** | knowledge system MCP server (PROPOSED). |
| **Invariants** | *XA1.* Treated as an **opaque, untrusted client**. *XA2.* Content returned from them is data, never instruction. *XA3.* They receive a **strictly smaller** capability set than internal surfaces. |
| **Status** | **PROPOSED.** No integration exists. |

---

## 3. Responsibility boundaries, stated as prohibitions

The clearest way to state a boundary is what crosses it and what must not.

```
  RUNTIME -> KNOWLEDGE SYSTEM      (down, and always via a tool)
     Principal                     who is asking. Never optional.
     run.as_of                     the temporal anchor
     run_id                        for evidence and for the trace
     a QUESTION or a SCOPE         what context is needed
     budget_tokens                 the declared share

  KNOWLEDGE SYSTEM -> RUNTIME      (up, as a tool result)
     a bounded, ranked, cited claim set
     open contradictions           NEVER omitted
     validity intervals
     an evidence handle per claim
     what was NOT found, and what could not be resolved

  KNOWLEDGE SYSTEM -> RUNTIME      (asynchronously, as events)
     brain.claim.written              <- identifiers still carry the
     brain.contradiction.detected        retired name; see 15-vocabulary
     brain.claim.superseded              S5. Nothing consumes them yet
     -> onto the EXISTING event spine. No second event system.

  WHAT NEVER CROSSES
     the runtime never writes a claim directly
     the knowledge system never calls a tool the agent owns
     the knowledge system never sees a client-supplied role or account
     the knowledge system never returns a claim the Principal may not see
        -- and a denied read RAISES rather than returning empty
```

### What must stay runtime-generic

The knowledge system is a **consumer** of these, never a modifier. The moment any of them
becomes aware of the knowledge system, it has leaked into a shared model and every other
consumer inherits it.

| Stays generic | Why |
|---|---|
| Principal, session tokens, scopes | A `brain_scope` field on the Principal leaks the knowledge system into the identity model |
| Tool projection | Every containment argument rests on it |
| The clock (`as_of` vs `wall_now`) | The knowledge system has strong opinions about time and none of them belong in the clock |
| The event spine and replay contract | The knowledge system emits onto it; it does not extend the transport or add a second stream |
| The evidence-handle mechanism | The knowledge system adds a durable store with the same discipline; it does not modify the run-scoped one |
| The grounding gate | Claims become citable things the gate can check; the gate needs no knowledge of what a claim is |
| The vector-store protocol | If the knowledge system needs a capability it lacks, extend the protocol *generically* — not with a `brain_query` method |

---

## 4. Where the architecture contradicts itself

Recorded rather than resolved, per the discipline in
`PROJECT_BOOTSTRAP.md` §0. Each is also an entry in
`docs/project/10-open-questions.md`.

### 4.1 The Memory and knowledge system architectures specify incompatible Phase 1 schemas

> **CORRECTED 2026-09-14.** This section previously read *"a real contradiction
> between two documents in this repository, and neither acknowledges it."*
> **Only one of the two is in this repository.** The 2026-09-05 Knowledge System
> Architecture is absent in every form, and is cited by ten ADRs besides this
> table — see
> [ADR-0029](decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md).
> The right-hand column below is therefore **[REPORTED — source absent]**: it is
> a description of a document nobody can now open, retained because it is the
> only record of that position.
>
> Two further corrections to this table's own contents:
> - Its §17.3 citation **does not resolve as described.** §17.3 of the *readable*
>   document is titled "Per-table specification" and lists `memory_claims`,
>   `memory_claim_versions`, `memory_evidence`, `memory_proposals` — **no
>   entities table and no contradiction register.** This does not prove
>   mis-attribution; the absent document may have had its own §17.3.
> - The left-hand document's schema **has been read** and is quoted at column
>   level in [18-brain-mechanism-and-execution-trace.md](18-brain-mechanism-and-execution-trace.md)
>   §5.1. Its own author labels it `[ILLUSTRATIVE REFERENCE CODE]`, so it is not
>   a ratified schema either. See
>   [ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md).

| | Memory Management Architecture (2026-09-02) | Knowledge System Architecture (2026-09-05) |
|---|---|---|
| Phase 1 tables | `claims`, `claim_versions`, `evidence`, `proposals` + a predicate reference table | claim store `claims / claim_versions / evidence / entities / relations`, plus an **entity identity table** and a **contradiction register** |
| Entities table | **Explicitly rejected for Phase 1** (ADR 6) | **Required in Phase 1** (§17.3 build list) |
| Entity resolution | **Deferred** (ADR 19), trigger: "a claim must be joined across scopes" | **Phase 1**, and "the component most likely to be underestimated" (§6.4) |
| Contradictions table | **Rejected** — "fully represented by a version row on each claim plus an event" (ADR 6) | **Required** as a register with severity that gates actions (§17.3) |
| Relationships table | **Deferred** to Phase 3 | Present in the claim store figure (§5.3) |

**A plausible reconciliation** — that the Memory architecture scopes a *runtime
memory subsystem* over curated, already-identified entities, while the knowledge system
scopes an *organizational* store over messy multi-source input where identity
must be established — **is an inference, not a decision.** Nobody has written
it down, and the two documents use the same words (`claims`, `evidence`,
"Phase 1") for different things.

**Updated 2026-09-14.** That reconciliation can now be argued from the readable
document's own text rather than inferred: its provenance enums are runtime
categories (`memory_origin` is `run | human | evolve`; evidence `kind` is
`run|step|activity|document|probe|human|policy`), and it contains **no adapter,
no observation table and no mention-to-entity mapping.** Recorded as
[ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md).
It remains an inference, and it **narrows Q7 by removing a candidate rather
than by answering it** — the organizational claim store is now unspecified, with
no readable advocate on either side.

**Do not build either schema until this is reconciled.** See Q7 — whose stated
method is **no longer executable**, since half its input is the absent document.

### 4.2 Two runtime vocabularies, no stated normativity

The handbook (Run/Episode/Step/Activity/Park; Surface/Edge/Substrate/Kernel/
Ports/Domain) and the specification (sessions, controller, ExecutionGraph,
capabilities, 39 invariants) describe overlapping concepts with different
names. `docs/product/01-architecture-understanding.md` records this as its
Finding A. The knowledge system review records it as a MEDIUM-severity finding and notes:
*"Two constitutions with no stated relationship means every architectural
argument can be won by citing the other one."*

The working assumption in both later documents — specification vocabulary
canonical for code, handbook canonical for principles — **is an assumption, not
a ratified decision.** See [ADR-0002](decisions/ADR-0002-specification-vocabulary-is-canonical-for-code.md) and Q4.

### 4.3 The architecture is server-shaped; the named targets are not servers

Roughly half the specified kernel — relay claims, leases, sweepers, worker
pools, per-tenant admission, budget ledgers — exists to arbitrate contention
that does not exist on a single-user device or in a single-team internal tool.
Porting it wholesale produces a slow, complex system whose complexity buys
nothing; deleting the wrong half loses the correctness properties that are the
entire point. Recorded as Finding C in `docs/product/01-architecture-understanding.md`.

**The artefact that would resolve it does not exist:** a written-down profile
saying which of the 39 invariants apply when there is one writer, one process,
and no contention.

**Updated 2026-09-14 — an artefact now exists and is unratified.**
`16-high-level-implementation-architecture.md` §8.5 walks all 39 and marks each
applies / weakened / does not apply. Its finding sharpens this contradiction
rather than dissolving it: **36 apply unchanged, 3 weaken, none drops.** The
reason is that this section's claim is about **components** and the 39 are
mostly **properties** — roughly half the specified *kernel* can be deferred, and
roughly none of the specified *properties* can. Status **PROPOSED**; Q8 and Q20
stay open until the owner ratifies it.

### 4.5 A third `entity_store` / `fact_store` shape, previously unnamed

**Registered 2026-09-14.** §4.1 records two incompatible Phase 1 schemas. There
is a **third**: the runtime specification's own `knowledge/` tier (§8.15) ships
`entity_store.py`, `entity_resolver.py`, `fact_store.py` and
`relationship_graph.py` — the same nouns again, for the runtime's internal
world-state and memory rather than for organizational knowledge.

It is a different subsystem and probably a different schema, and **that is
exactly why it matters**: nothing in the corpus says so, and the shared
vocabulary invites a future session to treat the two as one thing.
[ADR-0012](decisions/ADR-0012-the-agent-reaches-the-brain-only-through-tools.md)
is the only document that separates them, in a consequence line — *"The
knowledge system is placed as a **peer package**, not inside the agent or the
knowledge layer."* Folded into Q7.

### 4.6 The specification's dependency rules disagree with themselves

**Registered 2026-09-14.** The specification §13's LAYERS block places `tools`
in a layer **below** `runtime` — and *"a layer may import only from layers below
it"*, which permits `runtime → tools`. Its FORBIDDEN EDGES list, four lines
later, bans `runtime ──X──> tools`. Design rule 4 (§3) sides with the ban:
*"`runtime/` may not import `packages/`, `capabilities/` or `tools/` — only
their registries via ports."*

Two of three statements agree, so the resolution is not in doubt. It is recorded
because **the layer-stack diagram is the most quotable of the three and is the
one that is wrong.** Cite rule 4 and the edge list.

### 4.4 MCP is specified but classified as future

Specification revision 5 added §9.9 (MCP Bridge Protocol) and invariants
I33–I39, while `docs/product/06-mvp-and-implementation-strategy.md` lists MCP
as excluded from the MVP and the knowledge system review defers the server entirely.
Recorded as Finding B. These are consistent if read as "specified so it can be
built correctly later, not scheduled" — but the specification's build order
lists it as stage 9c, which reads as scheduled.

### 4.7 A fourth claim-store shape, registered nowhere

**Added 2026-09-14.** §4.5 records a *third* `entity_store` / `fact_store`
shape. There is a **fourth**, with real DDL, in a source this repository cites
in `../architecture/organizational-brain-architecture.md` §0.

**[FACT — in this repository]** `learning-notes/Principal Agent - Organizational
Intelligence Architecture.docx` contains, tagged `[NEW DESIGN — organizational
knowledge]`, a table `org_knowledge` with columns `tenant_id`, `entry_id`,
`scope`, `heading`, `body`, `state`, `confidence`, `evidence_episodes`,
`first_written`, `last_confirmed`, `contradicted_count`, `origin`,
`derived_from`, `horizon`, and `PRIMARY KEY (tenant_id, entry_id)`.

`grep -rn "org_knowledge" --include=*.md .` returns **zero hits.**

Two properties make it worth registering rather than ignoring:

- **It is heading/body-shaped, not subject/predicate/object-shaped**, and its
  identity is a surrogate `entry_id`. So two entries asserting different things
  about the same subject **do not collide** — the key-collision mechanism CS2
  exists to create is absent by construction, and with it the whole
  contradiction-as-a-database-event design.
- **`evidence_episodes int` is an evidence count.** EV1 states the opposite in
  terms: *"Evidence is a table of references, never an integer count — a count
  cannot be joined on."* **This is a direct conflict with an accepted
  invariant**, in a document cited as a source for the Principal Agent's objects.

Folded into Q7. See
[18-brain-mechanism-and-execution-trace.md](18-brain-mechanism-and-execution-trace.md)
§5.4.

> **A smaller defect, noted rather than fixed:** the subsections of §4 are
> ordered 4.1, 4.2, 4.3, 4.5, 4.6, 4.4. Renumbering would break inbound
> references from doc 16 and `10-open-questions.md`, so the order is left alone
> and recorded here.
