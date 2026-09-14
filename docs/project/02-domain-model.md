# Core Domain Model

**Status of this document:** every object below is **DESIGNED**. None is
implemented. Field lists are the design's, not a schema that exists.

Two rules govern this document:

1. **No object exists here because it sounds useful.** Each one is traced to
   the document that requires it, and §4 lists the objects that were
   *considered and rejected*, with the reason.
2. **The two architecture documents disagree about part of this model.** Where
   they do, both positions are shown and neither is silently picked. See §5.

---

## 1. The objects, at a glance

| Object | Layer | Status | Required by |
|---|---|---|---|
| [Observation](#21-observation) | Brain | DESIGNED | The system of record |
| [Proposal](#22-proposal) | Brain / Memory | DESIGNED | Model-proposes-never-writes |
| [Claim](#23-claim) | Brain / Memory | DESIGNED | The core object |
| [ClaimVersion](#24-claimversion) | Brain / Memory | DESIGNED | History, supersession, as-of |
| [Evidence](#25-evidence) | Brain / Memory | DESIGNED | Provenance, corroboration, deletion |
| [Entity](#26-entity) | Brain | DESIGNED — **disputed** | Identity across sources |
| [Relationship](#27-relationship) | Brain | DESIGNED — as a claim | Multi-hop questions |
| [Contradiction](#28-contradiction) | Brain | DESIGNED — **disputed** | Gating action on disagreement |
| [Predicate](#29-predicate) | Brain | DESIGNED | Claim identity; kind enforcement |
| [SourceClass](#210-sourceclass) | Brain | DESIGNED — **unauthored** | Deterministic precedence |
| [MemoryView](#211-memoryview) | Memory | **PROPOSED — not adopted** | See §4 |
| [Decision](#212-decision) | Principal Agent | DESIGNED — **blocked** | "Why did we decide X" |
| [Goal / Objective](#213-goal-and-objective) | Principal Agent | DESIGNED — **blocked** | The gap that drives the loop |
| [Commitment](#214-commitment) | Principal Agent | DESIGNED — **blocked** | Obligations outliving a run |
| [Outcome](#215-outcome) | Principal Agent | DESIGNED — **blocked** | Judged on outcomes |
| [Grant](#216-grant) | Principal Agent | DESIGNED | Authority, narrowed by delegation |
| [WorldState](#217-worldstate) | Brain | DESIGNED — **a projection** | Fast reads |
| [Run / Episode / Step / Activity / Park](#218-the-five-runtime-nouns) | Runtime | DESIGNED | Durable execution |
| [ExecutionGraph / Node](#219-executiongraph-and-node) | Runtime | DESIGNED | The only in-flight representation |
| [Effect / EffectLedgerEntry](#220-effect-and-effect-ledger-entry) | Runtime | DESIGNED | Undo, recovery, verification |
| [Verification](#221-verification) | Runtime | DESIGNED | Knowledge gating |
| [Policy / Gate](#222-policy-and-gate) | Runtime | DESIGNED | Human authority |
| [Event](#223-event) | Runtime | DESIGNED | The single event spine |
| [Principal](#224-principal) | Cross-cutting | DESIGNED | Every authorization decision |

**"Blocked" is not "deferred."** Four Principal Agent objects depend on
organizational structures — goal records with measures and baselines, grants,
authority — that do not exist. **No amount of memory or Brain work brings them
closer.**

---

## 2. Object specifications

### 2.1 Observation

**Definition.** The raw, uninterpreted record that something happened or that
someone said something. **Not** a record of what is true.

**Purpose.** The system of record. Everything downstream is derived from it and
rebuildable by replaying it.

| Field | Notes |
|---|---|
| `observation_id` | |
| `source` | Which adapter produced it |
| `actor` | Who or what said/did it |
| `raw_payload` | Retained verbatim. This is what makes reprocessing possible |
| `occurred_at` | **When it happened.** Separate from ingestion — unrecoverable if omitted |
| `ingested_at` | When we learned it |
| `content_hash` | Re-delivery is a no-op |
| `permission_label` | **Captured at ingest.** A message's audience is knowable now and unknowable later |

**Lifecycle.** Append-only. Never updated, never deleted except by a tenant
deletion route. Retained **longer** than the claims derived from it — a claim
whose evidence has expired is unreviewable.

**Owner.** Source adapters write; nothing else does. The verification loop's
probes also write observations, which is how probe results re-enter at the top.

**Invariants.** *Append-only. Uninterpreted. Content-hashed. Bitemporal from day
one. The rebuild invariant* — drop every derived structure, replay the log,
arrive at the same state.

**Relationships.** Zero or more Proposals derive from one Observation. Evidence
rows point back to it.

---

### 2.2 Proposal

**Definition.** A candidate claim, extracted from an observation by a model, not
yet applied.

**Purpose.** Makes "the model proposes and never writes" a structural fact:
extraction writes a Proposal, and a deterministic path decides what becomes of
it.

| Field | Notes |
|---|---|
| `proposal_id` | **Deterministic**, derived from `(observation_id, extractor_version)`. UNIQUE |
| `observation_id` | |
| `extractor_version` | Changing it deliberately re-extracts history |
| `proposed_claim` | Subject, predicate, object, kind, scope |
| `status` | See `03-lifecycles-and-state-machines.md` §3 |
| `rejection_reason` | When rejected. **The rate by reason is a signal**, not a log line |

**Lifecycle.** `PENDING → APPLIED | REJECTED | DUPLICATE`. See §3 of the
lifecycles document.

**Owner.** The extraction stage.

**Invariants.** *The row is claimed **before** the model call, not after.* The
id is a UNIQUE key so a redelivery collides instead of producing a second,
differently-worded claim.

---

### 2.3 Claim

**Definition.** A typed assertion with a subject, a predicate, an object, a
kind, a scope, an authority, a validity interval, and evidence.

**Purpose.** The core object. See
[ADR-0003](decisions/ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md).

| Field | Notes |
|---|---|
| `claim_id` | |
| `tenant_id` | **In the key.** Not a filter applied later |
| `subject` | A resolved entity reference where possible |
| `predicate` | From the closed registry |
| `object` | **Deliberately NOT part of identity** |
| `kind` | observation-backed / decision / implementation-fact / outcome / constraint / term |
| `scope` | Tenant-relative materialised path; "narrower than" is a prefix test |
| `source_class` | Position on the authored ladder |
| `confidence` | Derived from corroboration. **Not asserted by the model** |
| `status` | PROVISIONAL / ACTIVE / SUPERSEDED / RETIRED |
| `verification_status` | **`unverified` is the default, and it is honest** |
| `observed_at` + tier | Valid time, with attested-vs-inferred |
| `recorded_at` | Transaction time, from the database clock |
| `observed_at_seq` | Effect-stream position, for scope-overlap invalidation |
| `last_confirmed` | Decay origin |
| `superseded_at` | Closes the interval |
| `permission_label` | Inherited from the observation, never reconstructed |

**Identity.** `(subject, predicate)` within a `scope`. The object is excluded so
that **two claims with the same identity and different objects are one claim
disagreeing with itself** — a key collision rather than an invisible pair of
rows that both retrieve.

**Lifecycle.** See `03-lifecycles-and-state-machines.md` §4.

**Owner.** The classify-and-reconcile stage. **Nothing else writes a claim** —
not the runtime, not the agent, not a human directly.

**Invariants.** *Commits in the same transaction as its evidence and its outbox
event.* *Tenant in the key.* *Untrusted-derived claims may reach PROVISIONAL and
never ACTIVE.* *An imperative is rejected at the write path.* *Standing rises
only by independent corroboration from distinct runs.*

---

### 2.4 ClaimVersion

**Definition.** An append-only record of every state a claim has held.

**Purpose.** Five distinct needs require history: as-of queries; supersession
chains; contradiction reconstruction; audit; and the reconstruction test that
rebuilds current state from history.

| Field | Notes |
|---|---|
| `version_id`, `claim_id`, `version_no` | `version_no` is the CAS target |
| `object`, `status`, `confidence` | The values as at this version |
| `relationship_to_previous` | same / contradiction / supersession / refinement / coexistence |
| `superseded_by` | |
| `recorded_at`, `authored_by` | |

**Lifecycle.** Append-only. Never updated.

**Invariants.** *Layer 1 (versions + evidence) is authoritative for **history**;
the current-claim row is authoritative for the **present**; any index is
authoritative for **nothing**.* A CI test rebuilds the present from history.

*Concurrency is **re-classify on conflict**, not retry on conflict* — retrying
re-applies a classification computed against a stale current claim, silently
erasing what the winning writer decided.

---

### 2.5 Evidence

**Definition.** A relation between a claim version and the observation(s) or
step(s) supporting it.

**Purpose.** Three needs, and the third is decisive: a reviewer needs something
to open; corroboration must count **DISTINCT** runs; and the tenant deletion
route must **find claims citing a departing tenant's runs.**

| Field | Notes |
|---|---|
| `evidence_id`, `claim_id`, `version_id` | |
| `observation_id` / `step_ref` | What it points at |
| `locator` | Where in the source |
| `digest` | What it looked like then |
| `derived_from` | The provenance chain |
| `minted_at` | |

**Owner.** Server-minted. **A caller-supplied id is the whole attack.**

**Invariants.** *Evidence is a **table of references**, never an integer count —
a count cannot be joined on, and all three needs above are joins.* *A claim
without evidence must be an unreachable state.* *Evidence **outlives the run**.*

**Known limit, accepted and made visible:** a claim can outlive its evidence's
readable detail when raw payloads age out. The structural signal is small and
keepable for years; verbatim content is large and expensive.

---

### 2.6 Entity

**Definition.** A stable identity: id, type, aliases, source ids.

**Purpose.** So that "QIC", "the QIC flow", "quote-issue-confirm" and a service
name in a repository resolve to one thing. **Identity is schema. Everything
asserted about an entity is a claim.**

| Field | Notes |
|---|---|
| `entity_id`, `entity_type` | |
| `canonical_name` | |
| `aliases[]` | **Curated**, not inferred |
| `source_ids[]` | Anchors: repo id, Jira key, user id |

**Status: DISPUTED.** The Brain architecture requires this table in Phase 1 and
calls entity resolution "the component most likely to be underestimated." The
Memory architecture **explicitly rejects an entities table for Phase 1** and
defers entity resolution. See §5.

**Invariants.** *Resolution runs **before** extraction.* *Anchor on system
identifiers; curate aliases; **accept unresolved mentions rather than forcing a
match.*** A forced match is worse than an unresolved one, because it silently
merges two things.

---

### 2.7 Relationship

**Definition.** A claim whose subject and object are **both entities**.

**Purpose.** Multi-hop questions.

**It is not a separate store.** It is a claim, with a source, a validity
interval, a confidence and an authority — all of which an edge in a graph
would lack. See [ADR-0009](decisions/ADR-0009-no-graph-database.md).

**Status.** DESIGNED as a claim. A dedicated relationship table with recursive
CTEs arrives only on a **measured** multi-hop need.

---

### 2.8 Contradiction

**Definition.** Two claims at the same identity whose objects disagree, where
the predicate is `single_valued` and supersession does not apply.

**Purpose.** To make disagreement an **object that gates action**, not a
warning string in a log.

| Field | Notes |
|---|---|
| `contradiction_id` | |
| `claim_a`, `claim_b` | |
| `severity` | **blocking** / advisory |
| `detected_at`, `owner`, `resolution` | |

**Status: DISPUTED.** The Brain architecture requires a contradiction register
in Phase 1. The Memory architecture rejects a conflicts table — *"a
contradiction is fully represented by a version row on each claim plus an event,
and a separate table would be a second place to look with its own consistency
problem."* See §5.

**Invariants.** *A blocking contradiction prevents an action being minted
against the affected claims.* *Contradictions are never dropped from assembled
context for budget reasons.* *Precision is measured — raised versus
confirmed-real-by-owner — because a detector with low precision gets muted
within a week.*

**The failure to design against is not a missed contradiction but a FALSE one.**
A system treating every scope overlap as a conflict drives every claim in a busy
scope below the load floor, and looks healthy throughout.

---

### 2.9 Predicate

**Definition.** A registry entry defining one predicate in the closed
vocabulary.

| Field | What it decides |
|---|---|
| `predicate_id` | |
| `single_valued` | **Supersession vs coexistence.** A declared property — it cannot be read from two sentences |
| `object_schema` | Validated at write |
| `decay_profile` | none / slow / standard |
| `verifiable_by` | Probe name, if one exists |
| `kinds_allowed` | **Enforces the kind model.** A decision may assert `intended_behaviour`, never `current_behaviour` |

**Lifecycle.** Adding one is a **reviewed migration**, not a runtime write. An
out-of-vocabulary extraction is rejected, and **the rejection rate is the
signal** that the vocabulary needs extending.

---

### 2.10 SourceClass

**Definition.** A class of source with a declared position on **two** axes:
authority over **intent**, and authority over **reality**.

**Status: DESIGNED — UNAUTHORED.** This is the blocking prerequisite. See
[ADR-0006](decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md) and Q2.

| Field | Notes |
|---|---|
| `source_class_id` | |
| `intent_rank`, `reality_rank` | Two axes, because a decision outranks an observation on intent and is outranked by it on reality |
| `owner` | **A named human** |
| `version` | |

**Invariants.** *Authored, versioned, reviewed, and **outside anything the agent
may edit**.* *Never inferred from recency, seniority, or confident phrasing.*

---

### 2.11 MemoryView

**Status: PROPOSED — NOT ADOPTED.** No document in this repository specifies a
`MemoryView` object. The memory architecture's position is the opposite: the
commonly-cited memory categories are **logical views over one claim store**, not
separate stores or a materialised view object.

Recorded here because it appears in the list of objects to investigate, and the
honest finding is that **the investigation concluded against it.** If a
MemoryView is wanted, it needs a named query the claim store cannot answer.

---

### 2.12 Decision

**Definition.** A record that we chose X over Y, on whose authority, for these
reasons, expecting this result — **with the prediction sealed before the
outcome is known.**

| Field | Notes |
|---|---|
| `decision_id`, `decided_by`, `decided_at` | |
| `chosen`, `alternatives[]` | "Why did we decide X" needs the alternatives |
| `rationale`, `authority_ref` | |
| `sealed_prediction` | **Written before the result.** This is the whole point |
| `mechanism` | What is predicted to move, and how |

**Lifecycle.** **Append-only, permanent.** Never decays, never retires, never
contradicted — **superseded** by a later decision, and the old one stays.

**A decision has no confidence.** We did not *maybe* decide.

**Status: BLOCKED, not deferred.** It depends on goal records with measures and
baselines, grants, and authority. No memory or Brain work brings it closer.

---

### 2.13 Goal and Objective

**Definition.** A goal is a durable, measured intent with a baseline. An
objective is a desired state contributing to a goal.

Four properties separate a goal from a task: it is **measured** rather than
completed; it **persists** beyond any one run; it can **conflict** with another
goal, and trading them off is real work; and it is **held under authority**.

**Status: BLOCKED.**

**Invariant.** *A Principal Agent may **propose** a goal and may never **write**
one.* One judged on whether goals are met, which can also write goals, will meet
its goals — by optimising exactly what it was asked to optimise.

---

### 2.14 Commitment

**Definition.** A durable obligation the organisation is now bound by, created
when a Principal Agent commits, outliving the run that created it.

| Field | Notes |
|---|---|
| `commitment_id`, `to_whom`, `what`, `by_when` | |
| `authority_ref` | The grant it was made under |
| `status`, `opened_at` | **Open-age alerting** is the point |

**Status: BLOCKED.**

---

### 2.15 Outcome

**Definition.** After we did X, Y was measured — by a **probe against
organisational systems, later**, deliberately not by the run's own report.

| Field | Notes |
|---|---|
| `outcome_id`, `decision_id` | |
| `measured_at`, `measure`, `value`, `baseline` | |
| `verdict` | better / worse / **UNDETERMINED** |
| `mechanism_moved` | Did the predicted mechanism actually move? |

**Authority over what happened. NO authority over causation.**

**Invariants.** *Measured, never reported.* *A deterministic floor from a probe;
the Principal Agent may only lower it.* *UNDETERMINED is a first-class verdict —
a system with only better/worse will report one of them falsely.*

**Status: BLOCKED.** And an honest limit: this makes reasoning **auditable**,
not **verified**. Organizational outcome attribution remains unsolved — a
decision with a sealed prediction and a measured outcome gives the cleanest
evidence available at n=1 and gives **no causation.** The mechanism check is the
only instrument that works, and only because it was written down before the
result.

---

### 2.16 Grant

**Definition.** A scoped, time-bounded authority to act, held in a Principal
Agent's own name and narrowed on delegation.

**Invariants.** *Delegation **narrows** and never widens.* *Resolution happens
server-side; the model cannot claim permission.* *Revocation must work
mid-flight.*

---

### 2.17 WorldState

**Definition.** A queryable projection of current organizational state.

**It owns nothing.** See
[ADR-0005](decisions/ADR-0005-the-world-model-is-a-projection-not-a-store.md).
Apply the delete test: delete it; if information is lost, it was not a
projection.

---

### 2.18 The five runtime nouns

| Noun | What it is | Custody |
|---|---|---|
| **Run** | One unit of durable work with a goal, a budget, and a lifecycle | Owns the goal |
| **Episode** | One leased stretch of a run on one worker | Owns the lease |
| **Step** | One advance of the loop, checkpointed before the next begins | Owns the checkpoint |
| **Activity** | One identified, ledgered call to the outside world | Owns the effect |
| **Park** | A run waiting, holding **no process, no connection, no in-memory timer** | Owns nothing |

**Invariants.** *Exactly one controller advances a session at any instant.*
*Every advance is checkpointed before the next begins.* *An action result is
reused only on a **full** identity match.* *A park holds no resources.*

**Status:** DESIGNED. **Episode is explicitly droppable** until there is a
worker pool.

---

### 2.19 ExecutionGraph and Node

**Definition.** The **only** representation of in-flight work. Nodes carry a
capability and an intent — **never a tool.**

Node states: `PENDING → READY → RUNNING → APPLIED → SETTLED`, or `FAILED`, or
`BLOCKED` with a reason.

**Invariants.** *No parallel plan structure exists.* *Reconciliation is
level-triggered and idempotent — two consecutive passes over an unchanged graph
produce an unchanged graph.* *A terminal node is immutable; redoing work creates
a new node in a new generation.* *The projection given to the decision engine is
read-only.* *A capability's internal step chain is **declared** in its package,
never computed at runtime.*

---

### 2.20 Effect and Effect Ledger Entry

**Definition.** A change to the world, and the durable row recording it.

Three tiers by reversibility:

| Tier | Meaning | Handling |
|---|---|---|
| 1 | Locally reversible | Restore |
| 2 | Externally owned, compensatable | Run the named compensation as a real step with real failure handling |
| 3 | **Escaped** — a notification was sent, a human read it | **Not handled after the fact at all. Handled by refusing** |

**The tier is a property of the situation, not the verb.** A commit in a local
working copy is tier 1; the same commit after a push is tier 2; after CI
notifies three reviewers, the *notification* is tier 3 even though the branch is
still tier 2. The registry must say so.

**Invariants.** *Every effectful tool declares a tier.* *Unknown third-party
effect defaults to EFFECTFUL.* *The ledger row is written **before** the effect
and settled after — the crash between the two is the interesting case.* *An
effectful tool is uncallable without a resolved approval reference, **in the
runner, never by prompting.***

---

### 2.21 Verification

**Definition.** A deterministic post-condition check, written **before** the
work, evaluated against the world.

**No model is involved.** A model judgement may **lower** a passing verdict and
may **never raise** a failing one.

---

### 2.22 Policy and Gate

**Definition.** The rules deciding whether an action may proceed, and the
durable request when a human must decide.

**Invariants.** *Enforced in the runner, never in the prompt.* *Gate policy lives
outside anything an evolution loop may edit.* *A gate that nobody answers
expires the run rather than proceeding.*

---

### 2.23 Event

**Definition.** A durable fact that something happened, written through the
transactional outbox in the same transaction as the state change it describes.

**Invariants.** *One event spine. The Brain emits onto it and does not create a
second.* *Progress is **never** written to the event log — it is derived from
trace events.* *Exactly-once delivery via claim-based relay.*

---

### 2.24 Principal

**Definition.** Who is asking: user, role, account, and a frozen scope set,
**resolved server-side from a signed session token and never client-supplied.**

**Invariants.** *Never optional.* *Never client-asserted.* *Tools are curried
with it at build time, so an unauthorised query is **absent from the schema**
rather than refused at runtime.* *Every capability takes it **explicitly**,
never ambiently — an ambient Principal cannot be exposed over MCP later without
a refactor.*

**The Principal must stay runtime-generic.** The moment it gains a `brain_scope`
field, the Brain has leaked into the identity model and every other consumer
inherits it.

---

## 3. What is deliberately NOT an object

| Not an object | What it is instead | Why the distinction is load-bearing |
|---|---|---|
| A document | A source, in the observation log, plus the claims extracted from it | A document is not knowledge. This is the whole difference between this and a RAG index |
| A summary | A derived artifact with no independent standing | **A summary is not evidence for what it summarises.** A claim whose only support is a summary has an evidence chain that does not terminate in an observation |
| A chunk | An implementation detail of retrieval, if retrieval ever needs one | Chunks are an artefact of embedding, and there are no embeddings in Phase 1 |
| A conversation | A sequence of observations | Conversation history is not automatically memory |
| A context window | Model state, not persisted as truth | A context window is not durable memory |
| "The knowledge base" | The claim store plus the observation log | Naming it as one thing hides which is authoritative |

---

## 4. Objects considered and rejected

| Rejected | Why | Trigger to revisit |
|---|---|---|
| Embeddings table | Phase 1 has no embeddings | Vocabulary misses above a pre-registered threshold for two consecutive weeks |
| Graph store | A second store engine breaks same-transaction commit | Measured three-plus-hop need that CTEs demonstrably lose |
| `MemoryView` as an object | Memory categories are logical views over one claim store | A named query the claim store cannot answer |
| A separate "temporal layer" | Validity intervals live on claims. **Two representations of time is how a system starts disagreeing with itself** | None |
| A separate "provenance layer" | Evidence is a **property**, written in the same transaction. A layer invites a state where a claim exists without it | None |
| Knowledge-authoring UI writing directly | Creates claims with no observation behind them and breaks the rebuild invariant | Route through `propose_claim` with `source_class=human_authored` instead |
| Conflicts table | *(Memory position)* Fully represented by a version row plus an event | **DISPUTED — see §5** |
| Entities table in Phase 1 | *(Memory position)* Entity ambiguity shows as a low corroboration rate | **DISPUTED — see §5** |

---

## 5. Where the two models disagree

**This is an unresolved contradiction between two documents in this repository.
Neither acknowledges the other. Do not build either schema until it is
reconciled.**

| | Memory Management Architecture (2026-09-02) | Organizational Brain (2026-09-05) |
|---|---|---|
| Phase 1 tables | `claims`, `claim_versions`, `evidence`, `proposals`, + predicate registry | claims, versions, evidence, **entities**, **relations**, **contradiction register** |
| Entities | **Rejected for Phase 1** (its ADR 6) | **Required in Phase 1** (its §17.3) |
| Entity resolution | **Deferred** (its ADR 19). Trigger: a claim must be joined across scopes | **Phase 1**, and the component most likely to be underestimated (its §6.4) |
| Contradictions | **Rejected as a table** — version rows plus an event suffice | **Required** as a register with severity that gates actions |
| Relationships | **Deferred** to Phase 3 | Present in the Phase 1 claim-store figure |

### The plausible reconciliation, marked as an inference

The two documents may be scoping different systems:

- The **Memory** architecture scopes a **runtime memory subsystem** over work
  where entities are assumed to arrive already identified. Within a single
  scope, entity resolution genuinely is not the first problem.
  **[UNEVIDENCED]** — this reading of the Memory architecture's scope is an
  inference from what it defers, not a statement it makes about itself.
- The **Brain** architecture scopes an **organizational knowledge store** over
  messy multi-source input where identity must be *established* before anything
  can be joined.

Under that reading both are right about their own subject, and the answer is
that the Brain's Phase 1 is not the Memory subsystem's Phase 1.

**This is an inference, not a decision.** Nobody has written it down. The two
documents use identical words — `claims`, `evidence`, "Phase 1" — for different
things, which is exactly how two teams build two schemas and discover it at
integration.

**Resolution required before any schema is built.** See
`docs/project/10-open-questions.md` **Q7**.
