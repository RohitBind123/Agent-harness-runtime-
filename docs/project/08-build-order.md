# Product Build Order

**Status:** **PROPOSED.** Stage 0 is in progress; nothing after it has started.

This document takes the current staged hypothesis, evaluates it against what the
repository's own documents establish, and **proposes seven changes with
reasons.** The instruction was not to preserve the order blindly, and the
evidence supports real changes to it.

---

## 1. The hypothesis as given

| Stage | |
|---|---|
| 0 | Architecture + institutional documentation |
| 1 | Observation + organizational knowledge system |
| 2 | Evidence / provenance / temporal / trust |
| 3 | knowledge system evaluation |
| 4 | knowledge system MCP |
| 5 | Integration with existing agents (Claude / Codex) |
| 6 | Measure whether the knowledge system improves agent performance |
| 7 | Principal Agent |
| 8 | Runtime hardening / deeper orchestration |
| 9 | Controlled autonomy |
| 10 | Autonomous organizational workflows |

**What is right about it**, and worth keeping: knowledge before autonomy;
knowledge system before Principal Agent; measurement before scaling; MCP after the knowledge system
rather than as the entry point. The overall direction of travel is sound and the
changes below are structural rather than directional.

---

## 2. The seven proposed changes

### Change 1 — Stage 2 does not exist. Fold it into Stage 1. **[Highest impact]**

**The proposal:** *"Evidence / provenance / temporal / trust"* is not a stage
that follows observation. **These are properties of the first row written**, and
several of them are **unrecoverable if omitted.**

**Why**, in the sources' own terms:

| Property | Why it cannot be a later stage |
|---|---|
| Provenance | *"Retrofitting provenance is impossible — labels are assigned at fetch time or never."* |
| Truth time vs ingestion time | *"A log recording only ingestion time can never recover truth time."* |
| Permission label | *"A permission label not captured at ingest cannot be reconstructed."* A message's audience is knowable at ingest and unknowable afterwards |
| Extraction identity | *"Build identity first, because everything else retrofits and identity does not."* |
| Evidence as a joinable table | Three needs are joins — reviewer, distinct-run corroboration, and the tenant deletion route. A count added later cannot become a join |

**Building Stage 1 without these does not produce an early version of the
system. It produces a permanent gap in history** plus a migration. The Memory
roadmap lists the six temporal fields, the trust rule as a CHECK constraint, and
the deletion route as **Phase 1** items for exactly this reason.

**Consequence:** Stage 1 is bigger than the hypothesis suggests. That is the
honest size, not scope creep.

---

### Change 2 — Stage 0 is not documentation. It is a decision a human must make.

**The proposal:** Stage 0's exit is not "the documentation exists." It is
**Q2 (the source-precedence policy) resolved.** (Q1, which product, was resolved
2026-09-14 — see [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) —
so Stage 0's decision requirement is now half-cleared, not fully open.)

**Why:** the policy is *"not an engineering problem and it cannot be solved by
an LLM. It is a GOVERNANCE act."* And **every downstream mechanism —
resolution, contradiction, retrieval ranking — is meaningless without it.**

It cannot be unblocked by building. A Stage 0 that exits on documentation
alone hands Stage 1 a blocker it cannot clear.

**Also in Stage 0, and each costs under a day:** fix the observation shape;
choose ~20 predicates **derived from real questions**; decide the import
boundary and write the lint rule; write the single-writer invariant profile (Q8).

---

### Change 3 — Evaluation is not Stage 3. Its instruments are Stage 1; its use is continuous.

**The proposal:** move the **measurement instruments** into Stage 1 and delete
the standalone evaluation stage. Replace it with: **every stage exits on a
measurement.**

**Why:**

1. *"Until you have that number, every effect size is a number without its error
   term."* The noise floor gates every later claim of improvement.
2. The thing most worth testing early is **extraction precision** — explicitly
   **NOT ESTABLISHED**, and *everything downstream assumes it.* The reviewed
   sample is the cheapest way to find out, and it should exist *before* something
   goes wrong.
3. *"A stage whose exit is 'it's built' always exits."*

**Stage 1 therefore includes:** the reviewed extraction sample (a few hundred
real observations, extracted, reviewed once, committed) and **three signals** —
discard rate, claims per entity, contradictions raised versus confirmed. Three,
not sixteen. Each detects a whole failure class.

---

### Change 4 — Add a stage the hypothesis omits: **the second source.**

**The proposal:** insert a second-source stage immediately after the first.

**Why:** it is where the thesis is actually demonstrated, and nothing else
demonstrates it.

- The second source is **the test of what was accidentally source-specific** — a
  far more useful thing to learn in week six than in month six.
- It is the first point at which a **cross-source contradiction** is possible: a
  decision stated in a meeting, checked against what the code actually does.
  **Neither source alone can produce that.**
- Its exit criterion is a single event: *one contradiction the knowledge system detected
  and a human confirmed was worth raising.* **One confirmed instance is the
  milestone; it is the whole thesis demonstrated.**

Without this stage, the plan goes from one source straight to MCP — exposing a
knowledge system that has never been tested against disagreement.

---

### Change 5 — Merge Stages 4 and 5. MCP is an afternoon; integration is the work.

**The proposal:** one stage — *"expose the capability layer to external agents"*
— with MCP as a projection inside it.

**Why:** MCP *"is a projection of a capability layer that already exists by
stage 1. The server is a later afternoon."* Making it its own stage invites
building a server before anything consumes it, which is the failure the design
warns about: built early it becomes *the thing that constrains the capability
layer rather than a projection of it.*

**The gate is not calendar order.** It is: a **stable capability layer**, plus a
**decided answer to Q9** (whose Principal is an MCP caller). *"Decide before the
server exists, not during."*

**And the recorded prediction:** MCP is one of the two things most likely to be
built early anyway, because *"it exposes MCP" is a sentence that sounds like
progress and can be demonstrated without the knowledge system being good at anything.* If
it is built early regardless, make it a strict projection with no logic of its
own, so it can be deleted without losing anything.

---

### Change 6 — Stage 6 is not a stage. Measurement is every stage's exit.

**The proposal:** delete *"measure whether the knowledge system improves agent
performance"* as a stage and make it the **exit criterion** of the
external-agent stage.

**Why:** a separate measurement stage means the preceding stages exited without
being measured. And the measurement has preconditions that must already hold: a
measured noise floor, a **pinned** store snapshot, paired comparison, per-slice
gating, and cost in the denominator.

**One thing this measurement must not do:** report an aggregate. *"An aggregate
quality score will be dominated by the lookups and will not show the
difference."* The knowledge system's advantage is on **why** questions, **temporal**
questions, and **contradictions** — the valuable minority. **Slice for those
explicitly, or the measurement will show nothing and will be believed.**

---

### Change 7 — Stage 7 is partly BLOCKED, and the plan must show it.

**The proposal:** split the Principal Agent stage into what can be built and
what cannot.

**Why:** four of its objects — Decision records, Goal records, Commitments,
Outcome probes — depend on organizational structures that **do not exist**: goal
records with measures and baselines, grants, and authority. **"BLOCKED, not
deferred. No memory work brings this closer."**

**What can be built** without them: the Principal Agent *as a Run* (it inherits
durable execution, parking, crash recovery and the audit trail); the
delegation/grant mechanism; the assess-decide loop over knowledge system context.

**What cannot:** anything judged on organizational outcomes. That needs an
organizational act — someone writing down goals with measures and baselines —
before it needs engineering.

---

## 3. The revised build order

Each stage exits on a **measurement or a decision**, never on "it's built."

| # | Stage | Contains | Exit criterion |
|---|---|---|---|
| **0** | **Decide** | ~~Q1 product direction~~ **resolved.** Q2 the precedence meeting. Observation shape fixed. ~20 predicates from real questions. Import boundary + lint rule. Single-writer invariant profile (Q8). Memory/knowledge system schema reconciled (Q7). Institutional documentation | The policy exists as a reviewed file with a **named owner**, and two people who disagreed now agree — **or the disagreement is written down as an open question.** |
| **1** | **One source, end to end** | Observation log (bitemporal, permission-labelled, content-hashed). One adapter — Jira or Git. Admission, deterministic stage only. Entity anchoring. **Identity-keyed extraction.** Claim store with versions + evidence + the six temporal fields + source_class. Authority resolution. Contradictions. Structural retrieval. Context assembly. **The capability layer, with explicit Principal, provenance, bounded results.** Three tools: `entity`, `why`, `conflicts`. **The deletion route, tested.** The trust rule as a CHECK constraint. The reviewed sample. Three signals | **Five real questions** from our own history, each answered with the implementation fact, the decision, the author, the date, and **the gap between intent and reality stated plainly.** Plus a **measured extraction precision** on the reviewed sample |
| **2** | **The second source** | Meetings, or whichever source contradicts the first. Entity resolution stops being free here | **One contradiction detected across sources that a human confirms was worth raising.** One instance is the milestone |
| **3** | **Temporal and verification in anger** | As-of queries. Supersession chains. History answers. The probe loop for verifiable predicates. Verification-status distribution | *"What did we believe in June?"* answered correctly on a held-out set built from **real** history. And **probe-disagrees fires on a real stale claim before a human notices it** |
| **4** | **External agents** | Capability layer hardened. MCP as a strict read-only projection with fewer capabilities than the internal surface. Q9 decided first. Integration with the agents already in the workflow | **A measured improvement in agent output, sliced for *why* / temporal / contradiction questions** — against a pinned store snapshot, with a noise floor, paired, per-slice, cost in the denominator |
| **5** | **Breadth and participation** | Slack, with admission tuned against the easier sources. Participation rung 3 in **one** channel | **Volunteer precision above a threshold registered in advance**, and a **mute rate of zero** in the pilot channel. **Automatic demotion if not** |
| **6** | **Principal Agent — the unblocked half** | A Principal Agent as a Run. Grants and delegation. The assess–decide loop over knowledge system context. **No outcome judgement yet** | It deliberates, parks for a human, resumes, and founds a delegated run — surviving a restart |
| **7** | **Organizational structures** *(gated on an organizational act, not engineering)* | Goal records with measures and baselines. Decision records with sealed predictions. Commitments. The outcome ledger and read-only probes | Goals exist, written by a human, with measures and baselines. **Until then this stage cannot start** |
| **8** | **Controlled autonomy** | The autonomy ladder, rung by rung, each with a pre-registered threshold and automatic demotion | Each rung's threshold met, measured at the rung below where being wrong is cheap |
| **9** | **Autonomous organizational workflows** | — | **Not designed. Do not plan against it in detail** |

---

### 3.1 What becomes architecturally real in each stage

Added 2026-09-14. **The table above is unchanged** — this says what each stage
*earns*, not what it contains. The full version, with the boundaries and the
required-now/required-later split, is
`16-high-level-implementation-architecture.md` §9.

| Stage | Architectural capability that becomes real |
|---|---|
| **0** | No architecture, and no code. But the **import boundary and its lint rule** are established here, before there is anything to violate them — plus the two artefacts this stage owes: the single-writer invariant profile (Q8) and the Q7 reconciliation |
| **1** | **The minimum real knowledge substrate**, and the only stage in which the eight irreversible properties can still be got right: extraction identity · the four ingest-time observation fields · evidence as a joinable table · the rebuild invariant · claim+evidence in one transaction · tenant in the key · bitemporal columns · a tested deletion route. Each is cheap now and a rewrite later |
| **2** | **Cross-source reconciliation.** Entity resolution stops being free, and the source-precedence policy stops being theoretical. First real pressure on the domain/core split of [ADR-0028](decisions/ADR-0028-the-knowledge-core-is-domain-agnostic.md) |
| **3** | **Temporal and verification machinery.** The bitemporal columns written in Stage 1 start paying |
| **4** | **The stable capability surface for agents.** MCP as a strict projection — which is only a projection rather than a refactor because CL1 made the Principal explicit in Stage 1 |
| **5** | Admission tuned against harder sources; the participation ladder's first measured rung |
| **6** | **The Runtime becomes a first-class executable substrate — and not before.** The 39 invariants acquire something to be enforced against |
| **7** | Organizational structures. Gated on an organizational act, not on engineering |
| **8** | Runtime capabilities activate progressively — policy, budgets, the effect ledger, the autonomy ladder rung by rung |
| **9** | Distribution, learning and evolution belong here or later, and only on a trigger |

---

## 4. Stages that deliberately do not exist

| No stage for | Because |
|---|---|
| **The ingestion framework** | Adapters are written one at a time against a fixed observation shape. **The framework is that shape.** Six adapters is six times the surface area and one times the demonstrated value |
| **The knowledge graph** | Relationships are claims from Stage 1. Nothing to build separately |
| **A knowledge system UI** | knowledge system events go on the existing event spine. A separate UI before Stage 3 is a distraction from whether the knowledge system is *right* |
| **"Integrate the 50-chapter runtime"** | Four of its primitives each remove a real weakness and **each has its own trigger.** Adopting them as a block would be a rewrite justified by architecture rather than by a problem |
| **A migration/consolidation stage** | Reprocessing from the observation log is the normal way the knowledge system improves, not an event |

### The four runtime primitives, with the trigger for each

| Primitive | Weakness it removes | Adopt when |
|---|---|---|
| **Identity-keyed extraction** | A redelivery re-extracts and produces a *different* claim, unrecognisable as a duplicate | **Stage 1. This is the first one to need** |
| Transactional outbox | A claim write and its notification are two writes with a gap | When the first consumer reacts to a knowledge system event — the participation check is exactly that consumer |
| Leases and version-CAS | Two workers on one observation rely on database default behaviour | When ingestion runs more than one worker. **Before that it is theatre** |
| Park | A claim awaiting human confirmation has nowhere to wait that holds no resources | When human confirmation enters the claim lifecycle |

---

## 5. Do not build yet — with the trigger for each

*"Not yet" without a trigger becomes "never" or "next sprint", depending on who
is asking.*

| Not yet | Trigger |
|---|---|
| Embeddings | Vocabulary misses above a **pre-registered** threshold for two consecutive weeks. **If scope misses dominate instead, an index cannot help** |
| Graph database | A measured share of real questions needing **three or more hops**, or traversal latency dominating. **Measure with CTEs first** |
| Summarisation / consolidation | **Nothing in any planned stage.** If the budget binds, the answer is better ranking and tighter claims |
| Autonomous curation | **Nothing.** If ever automated, the protected property must be measurable first |
| Volunteering (rung 3) | Contradiction precision above a threshold **registered in advance**, measured at rung 2 |
| MCP server | A stable capability layer **plus** a decided answer to Q9 |
| Multi-source ingestion | One source proven end to end against Stage 1's test |
| Slack | Admission, entity resolution and the vocabulary all working on structured sources |
| Knowledge-authoring UI | Route through `propose_claim` with `source_class=human_authored` instead — a direct write path breaks the rebuild invariant |
| Confidence tuning | A **measured** extraction noise floor and a held-out question set |
| Cross-tenant learning | **A contract. Not a metric** |
| Removing the clock discipline | **Never.** Widen the allowlist per module, explicitly, with a comment |

---

## 6. The single most likely way this goes wrong

Two failure shapes, both recorded in the source material, both worth stating
before the plan is executed.

**The first:** building Stage 1 beautifully for four months because it is the
part that is fully specified and therefore the most comfortable to build — and
arriving at Stage 0's decisions far too late to act on the answers.

**Stage 0 comes first, and it contains no code.**

**The second:** starting with ingestion breadth because it is legible progress.
*"Four sources of unprocessed observations teach you nothing except that
ingestion works."* Every hard problem in this design — entity fragmentation,
admission, vocabulary growth, authority — is **invisible until something
downstream depends on getting it right.**
