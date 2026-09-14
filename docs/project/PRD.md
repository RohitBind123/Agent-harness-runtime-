# Product Requirements Document

**Document status:** **DRAFT 1 — 2026-09-14.** This is a *product* document
derived from the project's architecture corpus. It is not an architecture
specification, and §22 is the only section permitted to reason from product
requirement toward architecture.

**Read `PROJECT_BOOTSTRAP.md` first.** Read `docs/project/09-do-not-assume.md`
before treating any statement here as describing something that exists.

---

## 0. How to read this document

**[CORRECTION, 2026-09-14, the same day this PRD was written.]** This PRD was
originally written while Q1 (which product) appeared open, and scoped itself as
one of two contended directions. **The project owner has since clarified that
there was no contest**: `prd.md` was written to explore a different,
curiosity-driven question — how the agent runtime could be used to control iOS
or macOS — and was never a competing product decision. See
[ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md),
which supersedes
[ADR-0021](decisions/ADR-0021-product-direction-is-contested.md). **This
document is the project's confirmed, live PRD**, not a provisional one pending
a decision. §4.2, §20.1, §21 D1, §26, and Appendix B below are corrected
accordingly; nothing else in this document changes.

### 0.1 What this PRD does NOT do

1. **It does not claim market demand.** No customer interview, no user study,
   no collected question set and no sales conversation exists anywhere in this
   repository. Every statement about what users want is labelled as an
   assumption with the experiment that would test it.

### 0.2 The labels used throughout

Two label sets are in use in this project and they are **different axes**.
Both appear here.

| Existence label | Means |
|---|---|
| **DESIGNED** | A document says it should exist. No code. |
| **IMPLEMENTED** | Code exists and runs. |
| **PARTIALLY IMPLEMENTED** | Code exists; it does not yet satisfy the design. |
| **EXPERIMENTAL** | Built to learn something; not committed to. |
| **PROPOSED** | Intended; not designed in detail, not built. |
| **UNKNOWN** | Cannot be established from evidence in this repository. |

| Claim label | Means | Test |
|---|---|---|
| **FACT** | Verifiable in this repository right now | Point at the file, or run the command |
| **EVIDENCE** | External or reported, with a named source and a stated strength | Cite it and say how strong |
| **HYPOTHESIS** | An unproven belief | Say what would falsify it |
| **REQUIREMENT** | What the product must do | It has an acceptance criterion |
| **RECOMMENDATION** | What this document argues for | Argue with it |

**No sentence in this document mixes a FACT label with a HYPOTHESIS label.**

### 0.3 The state of the project, stated once so it is not restated

**FACT (verified at commit `d5037f4`, 2026-09-14):** 47 commits since
2026-08-04. 137 Markdown files, 11 DOCX, 9 SVG, 1 PDF, and **5 Python files,
all of which build or lint documentation**. There is no product source file, no
test, no migration, and no schema. **Zero product code exists.**

Everything in §7 onward describes something that must be built from nothing.

---

## 1. Executive Summary

### What the product is

A **knowledge system**: a store of kind-typed claims, built over an
append-only observation log, that answers questions whose answers are **not
present in any single source** — and that says so when it cannot.

Not a search box. Not a RAG index. Not a knowledge graph. The output that makes
it a product is not a ranked list of documents; it is a sentence of this shape:

> *"As of 20 March the API rejects cancellation after approval. A decision on 12
> March says it should be supported. There is a test asserting the intended
> behaviour; I do not know whether it passes. This is unresolved."*

### Who it is for

| | |
|---|---|
| **First validation user** | The engineers working in the **InOrbitX** workflow — a broker insurance portal held locally on the owner's desktop. Domain and shape are established; team, tooling, and workflow are **UNKNOWN** (Q3) |
| **Intended initial customer** | **NOT IDENTIFIED.** No document in this repository names a buyer for this direction. This is a gap, not an oversight, and inventing one here would be the single most damaging thing this PRD could do |
| **Eventual users** | Engineering organizations where intent, implementation and verification live in different systems. **HYPOTHESIS** |

### The problem

Organizational truth is distributed across sources that disagree, that change,
and that carry different authority over different kinds of statement. Retrieval
ranks those sources; it cannot type them. **Perfect retrieval still produces a
confident answer that hides a disagreement**, and the cost of that answer is
measured in decisions taken on it.

### Core value proposition

An answer that carries **what is true, what was decided, when each was
established, on whose authority, and where they conflict** — or an honest
refusal. Today that reconciliation is done by a person, by hand, by asking
three other people.

### The initial product

| | |
|---|---|
| **V0** | **Ships no software.** Four measurements and one 30-line primitive, two weeks. Its output is the evidence that decides whether V1 should be built at all |
| **V1** | **One source, end to end.** An observation log, identity-keyed extraction, a claim store with evidence and bitemporal validity, deterministic reconciliation, a contradiction register, and three capabilities — `why`, `entity`, `conflicts`. Useful to one team. **Not sellable** |

### Long-term direction

Second source → temporal and verification → external agents through MCP →
broader organizational participation → Principal Agent → controlled autonomy.
**Each stage gated on evidence from the one before it**, and several of them
are currently gated on organizational acts rather than on engineering (§18).

**Scope note, added 2026-09-14.** This PRD describes **current product and
problem validation** — the Organizational Brain, which is the **first substrate
and proving ground** for a general-purpose agent Brain + Runtime
([ADR-0027](decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md)).
It is deliberately not an architecture document: system boundaries, the
knowledge pipeline, the required-now/required-later split and the phase-by-phase
capability map live in
[`16-high-level-implementation-architecture.md`](16-high-level-implementation-architecture.md).
**No requirement in this PRD changed.**

### The honest summary

The architecture is strong, internally consistent, and **unvalidated in every
particular**. The premise — that the valuable questions are reconciliation
questions — has never been tested and is recorded in the project's own source
material as *genuinely open*. **This PRD's most important recommendation is
that V0 exists at all**, and that nothing in V1 is built until V0 reports.

---

## 2. Product Thesis

### 2.1 The thesis, stated so it can be falsified

> **We believe that** a meaningful share of the questions people and agents
> must answer inside an organization are **reconciliation questions** — whose
> answer spans a decision, an implementation fact and a verification that were
> made at different times, by different people, with different authority, and
> that disagree.
>
> **For** the engineers and coding agents working inside one engineering
> organization, where intent lives in tickets and chat, implementation lives in
> code, and verification lives in tests — three places that drift apart
> silently.
>
> **Because** retrieval *ranks* sources and cannot *type* them, and a
> disagreement between a decision, an observation and a test is therefore
> invisible in a retrieval-shaped answer — **including when retrieval is
> perfect.**
>
> **We will know this is true when** (all three, pre-registered):
>
> 1. **≥ 25%** of 50 real questions collected from the last 90 days classify as
>    *why*, *temporal*, or *contradiction* rather than *lookup* — threshold
>    registered **before** counting (Q17);
> 2. hand-written perfect organizational context measurably improves blind-graded
>    agent output on real tasks (Q19);
> 3. the knowledge system detects **one** cross-source contradiction that a human who owns
>    the subject confirms was worth raising (build order Stage 2 exit).
>
> **We will know it is false when** the question mix is dominated by lookups, or
> when hand-written *perfect* context does not improve output — because then the
> ceiling of the entire chain has been measured and it is zero.

### 2.2 Supporting assumptions — every one a hypothesis

| # | Assumption | Label | Tested by | Register |
|---|---|---|---|---|
| T1 | Reconciliation questions occur at a useful rate | **HYPOTHESIS** | 50-question study, 1 day | Q17 / A1 |
| T2 | LLM extraction of typed claims from messy organizational text is precise enough (~85%) for corroboration to mean anything | **HYPOTHESIS** | 200 reviewed observations, 3 days | Q11 / A3 |
| T3 | A named human will author and maintain a two-axis source-precedence policy | **HYPOTHESIS** | Run the meeting; time it; ask afterwards, 2 hours | Q2, Q18 / A2 |
| T4 | Organizational context measurably improves coding-agent output | **HYPOTHESIS** | Wizard-of-Oz A/B, 20 tasks, 3 days | Q19 / A4 |
| T5 | ~20 closed predicates cover enough organizational language | **HYPOTHESIS** | OOV rejection curve, rides free on T2 | Q12 / A7 |
| T6 | Reconciliation-with-provenance is a product, not a feature an incumbent adds | **EVIDENCE — explicitly the weakest in the corpus** | Fetched competitive scan + 5 discovery interviews, 1 week | A5 |
| T7 | This team converts design into shipped code | **HYPOTHESIS** | Ship identity-keyed extraction in one week | Q21 / A10 |

**FACT:** none of T1–T7 has ever been tested. **Four of them cost under a week
each.**

### 2.3 Unknowns that are not assumptions

These are not beliefs awaiting a test. They are facts nobody has established.

- Who the customer is (§4).
- Where the knowledge system runs relative to the sources it observes (Q3 §7 — local,
  hosted-with-collector, or fully hosted). **These are materially different
  products**, not deployment details.
- Which single source is ingested first (Q6), because nobody has established
  which systems the validation environment uses.
- What the twenty predicates are, because the real questions they are supposed
  to be derived from have never been collected (Q5).

### 2.4 Where the thesis is weak, stated plainly

**The thesis rests on one worked example and no data.** The cancellation example
(§3.2) is an **illustration written inside an architecture document**, not a
recorded incident from a real organization. It is a good illustration; it is
**not evidence**. Treating it as evidence is the most likely way this project
talks itself into a year of building.

**The differentiation argument rests on the corpus's own weakest claim.** The
knowledge system review states that nobody appears to combine authority, kind-typed claims,
bitemporal validity and contradiction-as-an-object — *and immediately adds that
this is "an argument from absence in public material and it is the weakest claim
in §3."*

**A defensible position, and the one this PRD takes:** the mechanism is probably
right and the market case is unestablished, so **spend two weeks measuring
before spending a year building.**

---

## 3. Problem Definition

*No architecture appears in this section. Components are named only in §11
onward.*

### 3.1 The current workflow, as observed

**FACT**, reconstructed from git history in `05-development-workflow.md`:

```
  HUMAN DECISION  ->  AGENT SESSION  ->  VALIDATION  ->  COMMIT
       (in chat)     (reads repo first)   (linters)    (one artefact)
                                                            |
                                                            v
                                            HUMAN REVIEW -- IN CONVERSATION,
                                                            NOT IN THE REPOSITORY
```

**The load-bearing observation:** until 2026-09-14 there was **no durable record
of a decision separate from the document that assumed it**. Rationale lived in
prose inside a deliverable, or in a conversation that is now gone.

**FACT:** this workflow has **no pull requests, no CI, and no issue tracker**.
That matters for the product in a way §17 returns to: the sources this design
values most are the ones this workflow does not produce.

### 3.2 Where the failure happens — the illustration

**[ILLUSTRATIVE — a worked example written by an architect, NOT a collected
incident. See `00-north-star.md` §2.]**

```
  Product   (Slack, 12 Mar):   "We will support cancellation after approval."
  Developer (PR review, 20 Mar): "The current API rejects cancellation
                                  after approval."
  QA        (test file on main): test_cancel_after_approval_succeeds

  A RETRIEVAL SYSTEM retrieves all three, ranked by similarity, and hands
  them to a model with no structure. The model picks one -- usually the
  longest or the most recent -- and states it as fact.

  THE DISAGREEMENT IS INVISIBLE IN THE OUTPUT.
  This is not a retrieval-quality failure. PERFECT RETRIEVAL PRODUCES IT TOO.
```

The three statements are **different kinds of thing**: a decision has authority
over what *should* be true and none over what *is*; a developer's observation
has authority over what *is*, at the time observed; a test is an assertion whose
authority depends on whether it passes — a fourth fact nobody has stated.

### 3.3 Where agents specifically fail

Three failures, each with its evidence class.

| Failure | Label | Basis |
|---|---|---|
| An agent asked "does the API support X" reads the code, answers correctly about *implementation*, and is silently wrong about *intent* — which is what the asker meant | **HYPOTHESIS** | Derived from the kind model; never observed |
| An agent given contradictory context produces confident output with the disagreement erased | **HYPOTHESIS** | Same failure as §3.2, one layer down |
| An agent acting on stale organizational knowledge produces an artefact someone acts on — **a reliability defect raises an alert; a confidently wrong result does not** | **EVIDENCE (external, moderate)** | Microsoft Research analysed 290 public reports across 13 frameworks of agents corrupting data, deleting files and leaking secrets, concluding agents *"have limited information about their filesystem effects and insufficient control over them."* Cited in `docs/product/04-product-thesis-and-decision.md` §5.2 |

### 3.4 Why existing context and memory are insufficient

| Approach | What it does | What it structurally cannot do |
|---|---|---|
| Document search / RAG | Ranks passages by similarity | Distinguish a decision from an observation. §3.2 survives perfect retrieval |
| Agent "memory" (conversation or vector recall) | Recalls what was said | Establish whether it is still true, or who had authority to say it |
| A wiki | Holds what someone wrote down once | Notice that the code now disagrees with it |
| A knowledge graph | Holds typed relationships | Carry validity intervals, evidence chains, and the authority of the asserter — and a second store engine breaks same-transaction commit of claim + evidence + event |
| A coding agent reading the repository | Reads the **highest-authority source for implementation facts** | See intent, history, or the reasoning behind a decision — none of which is in the code. **This is also why the marginal value of a knowledge system to a coding agent may be narrow (A4)** |

### 3.5 The consequence of wrong, stale, or contextless information

Ranked by how hard the failure is to see, because for a knowledge system
**invisibility matters more than severity**:

1. **Confidently wrong current state.** A correct-sounding answer from a claim
   that stopped being true. No error, no alert, no log line.
2. **A disagreement erased.** The system holds evidence against its own answer
   and does not say so.
3. **A private fact served outside its audience.** No error is produced. **Only
   a test detects it.**
4. **A decision re-litigated** because nobody can find why it was made — the
   cost this repository itself incurred until 2026-09-14.

### 3.6 Is this problem worth building a product around?

**ASSUMPTION REQUIRING VALIDATION.** No user research exists. The honest
position:

- **What supports it:** the mechanism failure in §3.2 is real and structural,
  and the project's own reasoning about it survives outside-in scrutiny.
- **What does not:** no one has been asked. The cheapest test is **five
  discovery interviews with engineering leaders — do not pitch; ask what they
  last got wrong because two sources disagreed, and what it cost.** Fewer than
  three specific, expensive, unprompted incidents means the pain is not acute
  enough to fund a company (A5).

---

## 4. Target Users

**No persona below was invented. Where the repository does not support one, the
row says UNKNOWN.**

### 4.1 Current validation user

| | |
|---|---|
| **Who** | Participants in the InOrbitX engineering workflow |
| **Established** | **FACT (owner-stated, 2026-09-14):** a broker insurance portal, held **locally on the owner's desktop** |
| **UNKNOWN** | Tech stack. Team size. Which tools emit observations. Whether it uses pull requests. Where decisions are recorded. Whether it has production users. What data it holds |
| **Consequence** | **This session cannot read it.** Everything about it is reported, not verified. Q3 |
| **Secondary validation user** | This project's own repository — the only workflow anyone here has actually observed, and the source of the best available test case (§8.1) |

### 4.2 Intended initial customer

**NOT IDENTIFIED. This is the most important gap in this PRD.**

`prd.md`'s research identifies a buyer for a *different* question — using the
agent runtime to control iOS/macOS — with precision: *"the Mac-primary
professional with document obligations and no assistant,"* and **explicitly
rules out the developer/power-user segment**, reasoning that it is *"the one
segment where Anthropic already ships a better product to an installed base,
and where you have no advantage whatsoever"* (`docs/product/04-product-thesis-and-decision.md`).

That segment exclusion was never a decision against the knowledge system
direction — `prd.md` was not proposing this direction as an alternative (see
[ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md)).
It is still a **market observation worth weighing**, since the knowledge system
direction points at approximately the segment that research described as
crowded and unwinnable on a different axis. That is a data point for D2 below,
not an unresolved argument this PRD owes an answer to.

→ **Decision D2 (§21). Blocking for a business model; not blocking for V0.**

### 4.3 Secondary users (V1 and later)

| User | Job | Status |
|---|---|---|
| **The claim owner** | Confirms whether a raised contradiction was real and worth raising. **This person is the only high-quality correctness instrument that is not a probe** | Required from V1 |
| **The policy owner** | Authors and maintains the source-precedence policy. A named human, not a role the system fills | **Blocking prerequisite, does not exist** (Q2) |
| **The coding agent** | A **consumer**, not a user. It does not have goals, cannot be dissatisfied, and cannot churn | Later, gated on Q19 |

### 4.4 Eventual users

**HYPOTHESIS, unvalidated:** engineering organizations of a size where intent
and implementation are owned by different people. No evidence establishes the
size, the vertical, or the buying centre.

### 4.5 The distinction this PRD insists on

> **A validation environment is not a customer, and dogfooding is not product
> validation.** A system that helps its own authors has a sample of one team
> with unusual tolerance for its failures. **This environment proves the
> mechanism, not the market.**

---

## 5. Jobs To Be Done

Outcomes, not features. **None of these jobs has been confirmed with a real
user**, because no question set has ever been collected (Q17). Each traces to
the test that would confirm it.

| # | Job (in the user's words) | Kind | Why it is a job | Confirmed? |
|---|---|---|---|---|
| **J1** | *"Tell me what is actually true right now — and what we said should be true — and whether they agree."* | contradiction | The §3.2 failure, from the asker's side | **No.** Q17 |
| **J2** | *"What did we believe about this in June, and what changed since?"* | temporal | A wiki holds the present; nothing holds the past with its basis | **No.** Q17 |
| **J3** | *"Why did we decide this, who decided it, when, and what did it rest on?"* | why | The cost this repository itself paid before ADRs existed | **Partially — this project experienced it** |
| **J4** | *"Warn me before I act on something two sources disagree about."* | contradiction | Value arrives **before** the wrong action, not after | **No** |
| **J5** | *"Tell me when you do not know."* | abstention | An unsupported organizational claim is indistinguishable from a confident wrong one | **No** |
| **J6** | *"Give my coding agent the organizational context it cannot read from the code."* | agent | The strategic chain's consumer bet | **No.** Q19 — **and the ceiling has never been measured** |
| **J7** | *"Show me why the system said that."* | debugging | Without it, three different failures are indistinguishable afterwards (§14.6) | Required by J1–J6 |

**J1, J2 and J3 are the product.** J6 is a bet. **If V0 shows J1–J3 are rare,
this product is a worse search box carrying a correctness tax.**

---

## 6. Product Value Proposition

### 6.1 Immediate value (V1, one team, one source)

| Becomes possible | Difficult today because |
|---|---|
| Asking *"do intent and implementation agree about X?"* and getting a structured answer rather than a ranked list | Nothing types a statement by what it has authority over |
| Following any answer to the observation it came from, months later | Evidence is in chat history, or gone |
| Being told *"this is unresolved"* instead of receiving a confident pick | Ranking has no way to express disagreement |
| Reconstructing what was believed at a past date | Only current state is stored anywhere |

### 6.2 Strategic value

- **The observation log's rebuild property.** Better extraction, a new
  predicate, or a corrected authority ordering can be applied to **history** —
  so improvement is a reprocess, not a migration. **Cheap on day one and
  expensive later.**
- **Provenance and temporal fields cannot be retrofitted.** *"A log recording
  only ingestion time can never recover truth time."* Building them first is not
  gold-plating; it is the only time they can be built.

### 6.3 Future value — and the honest discount

**HYPOTHESIS:** a general organizational claim store redeploys onto other
domains and other consumers, so the asset survives one product being wrong.

**The discount, recorded because it is load-bearing elsewhere:** the project's
own architecture review states that **the knowledge system does not need the fifty-chapter
runtime to exist**, and the product research assesses the runtime as *"copyable
infrastructure, today. It becomes platform-shaped only if it reaches a third and
fourth environment and the environment abstraction survives contact"*
(`docs/product/04-product-thesis-and-decision.md`). The *"the runtime survives
the product being wrong"* argument is therefore weaker than the documents that
rely on it assume (A6, Q20).

**[CORRECTION — recorded rather than silently fixed]**
`14-outside-in-review-2026-09-14.md` §A6 renders this assessment as *"copyable
infrastructure, weak moat"* inside quotation marks. **"Weak moat" does not
appear in the source.** The substance of A6 is unaffected; the quotation is
not accurate, and correcting the review itself is a separate edit that this PRD
does not make.

---

## 7. Product Scope

### 7.1 V0 — the smallest experiment that can falsify the thesis

**V0 ships no software to any user. That is the point.**

| # | Deliverable | Days | Falsifies | Register |
|---|---|---|---|---|
| **V0.1** | **Question-shape study.** 50 real questions from the last 90 days, classified lookup / why / temporal / contradiction. **Threshold registered before counting** | 1 | T1 — the premise | Q17 |
| **V0.2** | **Wizard-of-Oz context A/B.** 20 real completed tasks; for 10, hand-write the context a perfect knowledge system would supply; run all 20 blind; grade blind | 3 | T4 — the ceiling of the whole chain | Q19 |
| **V0.3** | **Extraction sample.** 200 real observations, one prompt, a draft 20-predicate vocabulary, **every output reviewed by a human who knows the project.** Measure precision, recall and kind-assignment agreement **separately** | 3 | T2, T5; yields the noise floor and the vocabulary | Q11, Q12 |
| **V0.4** | **The precedence meeting, timed.** Two or three people rank source classes on two axes. Record whether they converged, what they disagreed about, how long it took. Then ask each, separately: *"would you have done this before seeing any output?"* | 0.5 | T3 — the onboarding tax | Q2, Q18 |
| **V0.5** | **Identity-keyed extraction.** ~30 lines plus a test that a redelivered observation does not produce a second claim | 5 | T7 — and it is required under every scenario | Q21 |

**V0 exit criterion — a decision, not an artefact:**

> A named human reads V0.1–V0.4 and decides **build V1 / change the product /
> stop.** If V0.1 lands under the pre-registered threshold **and** V0.2 shows no
> improvement from perfect context, the correct decision is **do not build V1.**

**Why V0.5 is the only code:** identity-keyed extraction is required in every
scenario including the ones where this project pivots, it is the one primitive
that **cannot be retrofitted** (without it a redelivery produces a *different*
claim that is not recognisable as a duplicate afterwards), and shipping it in a
week is a measurement of the team rather than of the task.

### 7.2 V1 — the smallest genuinely useful product

**One source, end to end, including the stages that feel skippable.**

| In V1 | Why it cannot wait |
|---|---|
| Observation log: raw payload, `occurred_at` **and** `ingested_at` separately, content hash, **permission label captured at ingest** | Three of the four are **unrecoverable if omitted.** A message's audience is knowable at ingest and unknowable afterwards |
| One source adapter | The thesis needs real messy input; synthetic data does not produce the hard problems |
| Admission — deterministic rules only | *"The stage everyone omits."* Without it, cost rises with headcount while precision falls |
| Entity anchoring on system identifiers | Extraction that does not know which entity it discusses produces claims that cannot be joined, and joining afterwards is strictly harder than never splitting |
| **Identity-keyed extraction** (from V0.5) | Does not retrofit |
| Claim store: claims, versions, **evidence as a joinable table**, the six temporal fields, `source_class`, `kind` | An evidence *count* cannot be joined on, and three needs are joins: a reviewer opening a source, corroboration counting **distinct** runs, and the deletion route |
| Deterministic classification and reconciliation | Runs as part of **writing**; otherwise there is a window where the store serves unreconciled contradictions |
| Contradiction register with severity — **its table shape is conditional on D4** | The contradiction *is* the product; **whether it is a table or a version row plus an event is exactly what Q7 disputes** (§7.4) |
| Structural, scope-first retrieval | No embeddings; the permission predicate is a **pre-filter inside the store** |
| Context assembly that **never drops** contradictions, provenance pointers, or temporal qualifiers for budget | Each failure is different and each is silent |
| Capability layer with an **explicit** Principal — `why`, `entity`, `conflicts` | A capability reading an ambient Principal cannot be exposed over MCP later without a refactor |
| **A tested deletion route** | A store that cannot be enumerated cannot ship in a regulated domain |
| Three signals: discard rate, claims per entity, contradictions raised vs confirmed | Three, not sixteen. Each detects a whole failure class |
| The reviewed extraction sample, run as a regression test | A prompt change otherwise halves precision silently |

**V1 exit criterion:** **five real questions** from real history, each answered
with the implementation fact, the decision, the author, the date, and **the gap
between intent and reality stated plainly** — plus a **measured** extraction
precision on the reviewed sample.

**What V1 is honestly worth:** it is **useful to one team and not sellable to
anyone.** Sellability is gated on market validation (§17.4) that V1 does not
perform.

### 7.3 Future — and why each is excluded from V1

| Later | Excluded from V1 because | Trigger to revisit |
|---|---|---|
| Second source | One source must be proven end to end first | V1 exit met |
| Temporal probes / verification loop | The probe loop is the only **proactive** mechanism, and it needs a claim store with real claims to probe | V1 exit met |
| MCP server | It is a **projection of a capability layer that does not exist yet.** Built first, it becomes the thing that constrains the layer it should project | Stable capability layer **and** Q9 decided |
| Principal Agent | Four of its objects are **BLOCKED** on organizational structures (goals with measures and baselines, grants, authority) that do not exist. **No knowledge system work brings them closer** | A human writes goal records |
| Most of the agent runtime | The project's own review says the knowledge system does not need it; four primitives each have their own trigger | Per-primitive triggers (§18) |
| Embeddings | The trigger is a measured OOV rate, and the measurement does not exist | Vocabulary misses above a pre-registered threshold for two consecutive weeks |
| Graph database | A relationship is a claim; a second store engine breaks same-transaction commit | Measured 3+ hop need that CTEs demonstrably lose |
| Summarisation / curation | **A summary is not evidence for what it summarises** | Nothing in any planned stage |
| A knowledge system UI | Before knowing whether the knowledge system is *right*, a UI measures nothing | After V1 exit |
| Multi-tenancy machinery | One team is one permission domain. **Keep `tenant_id` in the key** (a column, cheap, unrecoverable later); **drop the contention machinery** | A second tenant |

**The rule this section enforces:** *nothing enters V1 because it exists in a
design document.* Every V1 row above traces to a user problem in §3 or to a
property that is unrecoverable if deferred.

### 7.4 Could V1 be smaller? — the three candidates, and what cutting each costs

**V1 is larger than "smallest useful" instinctively suggests, and that deserves
an argument rather than an assertion.** Three rows above are the only genuine
candidates for cutting. Each is examined rather than defended.

| Candidate cut | The case for cutting | The cost, from the source material | Verdict |
|---|---|---|---|
| **Admission** — accept every observation | One less stage; the store fills faster; discard rules can be added later | Cost rises linearly with headcount while retrieval precision falls, and **the discard rate is the signal that tells you which**. A rate measured after the fact has no baseline to compare against | **Keep, in its deterministic form only.** No model stage in V1 |
| **Entity anchoring** — key claims on raw source identifiers | Entity resolution is *"the component most likely to be underestimated"*, so deferring it removes the largest unknown from V1 | *"Joining them afterwards is strictly harder than never splitting them."* With **one** source the risk is genuinely low — a single source usually supplies consistent identifiers | **Keep the anchoring; defer the resolution.** Anchor on system identifiers, curate no aliases, accept unresolved mentions. **This is the one place this PRD narrows the build order** |
| **The contradiction register as a table** | The Memory architecture argues a contradiction is *"fully represented by a version row on each claim plus an event"* — so the table may be redundant | The knowledge system architecture requires a register with **severity that gates actions**, and severity has nowhere to live on a version row | **Undecided — this is Q7/D4 in miniature.** Do not cut it and do not build it until D4 is ratified |

**What stays regardless, and why arguing about it wastes time:** the six
temporal fields, the permission label, the evidence table, identity-keyed
extraction, and the raw payload. **Each is unrecoverable if omitted** — not
expensive to add later, *impossible*. Cutting them does not produce a smaller
V1; it produces a V1 with a permanent hole in its history.

---

## 8. Core User Workflows

Concrete, end to end. Each names what exists today and what does not.

### 8.1 W1 — The contradiction walk *(the product's whole thesis, on real data)*

**The best test case in this repository, and it is uncomfortable:**

```
  QUESTION            "Which product are we building?"
       |
       v
  OBSERVATIONS        prd.md, committed 2026-09-06 (a DECISION:
       |              "GO WITH MAJOR CHANGES" on a macOS paperwork agent,
       |               and "cut the developer-tools environment entirely")
       |              the strategic direction, recorded 2026-09-14
       |              (a DECISION: knowledge system -> MCP -> coding agents)
       v
  EXTRACTION          two claims at the SAME IDENTITY
       |              (subject=product_direction, predicate=current_direction)
       |              with DIFFERENT objects -> a key collision
       v
  CLASSIFICATION      single_valued predicate + two decisions, neither
       |              superseding the other -> CONTRADICTION, not supersession
       v
  ANSWER              "Two decisions disagree. On 2026-09-06 a decision
                       recorded a macOS paperwork agent and explicitly cut
                       the developer-tools direction. On 2026-09-14 a
                       decision recorded a knowledge system serving coding
                       agents. Neither supersedes the other. UNRESOLVED."
```

**If the knowledge system surfaces this from the documents alone, without being told, the
thesis is demonstrated on real data and on the project's own most important open
question.** **FACT:** the observations for this walk exist in the repository
today. Nothing else in it does.

### 8.2 W2 — The agent-context walk *(the bet, not the product)*

```
  ENGINEER asks a coding agent to change the cancellation flow
       |
       v
  AGENT calls a knowledge system capability, curried with the engineer's Principal
       |
       v
  BRAIN returns: the implementation fact (with its verification date),
       |         the decision (author, date, rationale), the open
       |         contradiction, and what it could NOT resolve
       v
  AGENT writes code -- and, on a blocking contradiction, DOES NOT ACT;
       |               it surfaces the disagreement to the engineer
       v
  OUTCOME observed later; the observation re-enters the log at the top
```

**Status: PROPOSED.** No integration exists. **The ceiling of this workflow has
never been measured — that is V0.2.**

### 8.3 W3 — The abstention walk

```
  QUESTION  ->  RETRIEVAL finds no claim in scope
                     |
                     v
             "I have no claims about X."
                     |
       +-------------+-------------+
       |             |             |
   nobody has   it does not    I cannot see it
   said anything  exist       (a PERMISSION fact the
                               asker may not be allowed
                               to learn)
```

**The system must not conflate these three, and no current design
distinguishes them.** Recorded as structurally unsolved. **V1 requirement:**
abstain honestly and say *which* of the three it is, where it can.

### 8.4 W4 — The "why did it say that" walk

Given an answer someone disputes:

1. Which claims did the answer cite?
2. For each: `why` — the evidence chain, the source class, **and what lost**.
3. Was the right claim in the store at all?
   - **Not present** → extraction or admission. Go to 4.
   - **Present, not retrieved** → retrieval. Go to 5.
   - **Present, retrieved, dropped** → budget. Go to 6.
4. Find the observation. Ingested? Admitted? Which rule discarded it?
5. Scope miss or vocabulary miss? **Different fixes.**
6. Was one of the three un-droppable items dropped?

**Step 3 is the one that requires a retrieval record**, and it separates three
failures with completely different remedies. Without it they are
indistinguishable afterwards.

---

## 9. Functional Requirements

Priority: **V0** / **V1** / **Later** / **Blocked**. "Blocked" means it depends
on something that is not an engineering task.

### 9.1 Knowledge and evidence

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-K1** | Every observation is stored raw, append-only, with source, actor, `occurred_at`, `ingested_at`, content hash and permission label | J3, J7 — an answer can be followed to its source months later | **V1** | Replaying the log rebuilds the claim store identically (rebuild test) | Automated test on a seeded log, in CI |
| **FR-K2** | Extraction is identity-keyed: a deterministic id from `(observation_id, extractor_version)`, UNIQUE, **claimed before the model call** | Prevents duplicate, differently-worded claims from one text | **V0.5** | A redelivered observation produces no second claim, and no second model call | Automated test |
| **FR-K3** | A claim carries subject, predicate, object, **kind**, scope, source class, validity interval, confidence, verification status and permission label | J1 — kinds are what make §3.2 answerable | **V1** | Every stored claim has all fields; none is nullable by accident | Schema constraint + test |
| **FR-K4** | Claim identity is `(subject, predicate)` within a scope; **the object is not part of identity** | A contradiction is a key collision rather than two rows that both retrieve | **V1** | Two claims, same identity, different objects → one contradiction, not two claims | Automated test |
| **FR-K5** | A claim and its evidence commit in the **same transaction**; a claim without evidence is unreachable | J3 — an unsupported claim is indistinguishable from a wrong one | **V1** | No code path produces a claim without evidence; enforced by constraint | Schema constraint + test |
| **FR-K6** | Evidence is a **table of references** with locator and digest, never a count | Three needs are joins: reviewer, distinct-run corroboration, deletion route | **V1** | Each of the three joins runs and returns correct rows | Query test |
| **FR-K7** | The model **proposes**; nothing it emits is written as a claim by its own authority. There is no `remember()` tool | Model output is not evidence | **V1** | No write path accepts model output without passing through classification | Import-boundary test + review |
| **FR-K8** | Claim versions are append-only; history is authoritative for the past, the current row for the present, any index for **nothing** | J2 | **V1** | Current state rebuilds from version history | Reconstruction test |
| **FR-K9** | Claims are proposed in a **closed** predicate vocabulary; out-of-vocabulary extractions are rejected and **the rejection rate is a signal** | Keeps identity computable without embeddings | **V1** | OOV rate recorded per run and plotted over time | Metric |
| **FR-K10** | A store ships with a **tested deletion route** before it ships retirement | Regulated-domain precondition; retirement ≠ deletion | **V1** | Every store enumerates; a store with no route fails loudly | Deletion-route test |

### 9.2 Retrieval and context

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-R1** | Retrieval is **scope-first and structural**, not similarity-first | Scopes are known before the query rather than inferred from it | **V1** | Retrieval executes with no embedding index present | Code review + test |
| **FR-R2** | Authorization, validity and standing are applied in **one** statement, with the permission predicate as a **pre-filter inside the store** | A post-filter collapses recall and leaks stop producing signals | **V1** | No caller-side filtering exists; one query path | Import-boundary test |
| **FR-R3** | A denied read **raises**; it never returns empty | An empty result is indistinguishable from having no data and produces no signal | **V1** | A cross-scope read raises a typed error | Automated test |
| **FR-R4** | Context assembly **never drops** contradictions, provenance pointers, or temporal qualifiers for budget | Each is a distinct silent failure: a confident answer over contrary evidence; a decorative citation; a precise answer made wrong | **V1** | Under a minimal budget all three survive; only claim bodies shrink | Automated test |
| **FR-R5** | Every result set is **bounded**, and the response states **what was not found and what could not be resolved** | J5 | **V1** | Every capability response has both fields populated | Contract test |
| **FR-R6** | A sampled **retrieval record** captures which claims were returned, which dropped for budget, under which `as_of` and scopes | J7 — separates three failures with different fixes | **V1** | Sampled fraction, plus 100% for any disputed answer | Metric + walk W4 |

### 9.3 Temporal reasoning

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-T1** | Valid time and transaction time are **separate** on every claim, from the first row | J2. *"A log recording only ingestion time can never recover truth time"* — **unrecoverable if deferred** | **V1** | Six temporal fields present and populated; no code path writes one from the other | Schema + test |
| **FR-T2** | An `as_of` query returns what was believed at a past instant | J2 | **Later (Stage 3)** | *"What did we believe in June?"* answered correctly on a **held-out** set built from real history | Held-out question set |
| **FR-T3** | Supersession is decided by the predicate's declared `single_valued` property, never inferred from two sentences | Prevents a contradiction being silently recorded as an update | **V1** | Predicate registry declares it; classification reads it | Test |
| **FR-T4** | **Decisions and terms never decay.** A decision is superseded by a later decision; it does not retire | *"We did not maybe decide"* | **V1** | Decay job excludes both kinds; test asserts it | Test |

### 9.4 Contradiction handling

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-C1** | A contradiction is a **first-class record** with severity and an owner, not a warning string | J1, J4 | **V1** | Contradictions are queryable and appear in `conflicts` | Test |
| **FR-C2** | A contradicting observation **lowers** confidence in the existing claim; it never flips it. A contradiction does not make the other claim true | Prevents the newest confident statement from winning | **V1** | Confidence decreases; object unchanged | Test |
| **FR-C3** | Contradiction **precision is measured** as raised vs confirmed-by-owner, from the first contradiction onward | *A detector with low precision gets muted within a week, and then the capability is gone regardless of later quality* | **V1** | Both counters exist before the first contradiction is raised | Metric |
| **FR-C4** | Contradictions run **advisory-only** at first; blocking is enabled only on measured precision | The assignment rule for blocking vs advisory **does not exist** (Q15) | **V1 advisory; blocking Later** | No action is refused in V1; the "should have blocked" set is collected | Measurement |
| **FR-C5** | A contradiction is resolved by **new observations**, never by a cleanup job | A cleanup job destroys the record of disagreement | **V1** | No code path closes a contradiction without an observation | Review + test |

### 9.5 Verification

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-V1** | `unverified` is the **default** verification status, and it is honest | J5 | **V1** | Default asserted in schema | Test |
| **FR-V2** | A model judgement may **lower** a verdict and may **never raise** one | The only thing that makes model judgement safe to use here | **V1** | Judgement-cannot-upgrade test | Automated test |
| **FR-V3** | Standing rises **only** by independent corroboration from **distinct** runs; same-run repetition is not corroboration | Prevents one talkative source from manufacturing confidence | **V1** | Corroboration counts DISTINCT runs; test asserts | Test |
| **FR-V4** | Untrusted-derived claims may reach PROVISIONAL and **never** ACTIVE, enforced as a CHECK constraint | A future caller cannot bypass it | **V1** | Constraint present; insertion attempt fails | Schema test |
| **FR-V5** | Scheduled, read-only probes re-establish whether probe-verifiable claims are still true; **a probe writes an observation, never a claim** | The only **proactive** mechanism in the design | **Later (Stage 3)** | `probe-disagrees` fires on a real stale claim **before a human notices it** | Live measurement |

### 9.6 Permissions and scope

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-P1** | The permission label is captured **at ingest** and propagated to every derived claim. **It is never reconstructed later** | A message's audience is knowable at ingest and unknowable afterwards. **Unrecoverable if deferred** | **V1** | Every claim carries a label traceable to its observation | Test |
| **FR-P2** | `tenant_id` is **in the key**, not a filter applied later; a cross-tenant read raises | The only way to detect a permission leak, because nothing else produces a signal | **V1** | Tenant-isolation test raises rather than returning empty | Automated test |
| **FR-P3** | Every capability takes an **explicit** Principal; none reads an ambient one | A capability reading an ambient Principal cannot be exposed over MCP later without a refactor | **V1** | No capability signature omits it | Contract test |
| **FR-P4** | A model for **overlapping, non-partitioned** audiences (a private channel, a restricted repo, an HR document) | **The most under-designed area in the project, and the leak produces no error** | **Blocked — design work, Q10** | A containment test at read over real audiences | Design + test |
| **FR-P5** | The system does not produce an **aggregate** it cannot cite | Mitigates aggregate leakage. **A mitigation, not a solution** | **V1** | Aggregates carry claim ids or are not produced | Review |

### 9.7 Agent integration

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-A1** | An agent reaches the knowledge system **only through tools curried with its Principal** — never an import, a shared repository object, or context injected at graph build | Every access-control argument rests on this | **V1** | Import-boundary test: the agent package must not import the knowledge system store | Automated test |
| **FR-A2** | Content returned by an external agent is **data, never instruction** | Prompt-injection containment | **V1** | Fetched content never reaches an instruction position | Test |
| **FR-A3** | An MCP surface exposes **strictly fewer** capabilities than the internal one: read-only, no `propose_claim`, no unbounded result set, and the **client never asserts an identity** | Structural containment is lost over MCP; enforcement falls back to runtime checks | **Later** | Capability diff is asserted in a test | Test |
| **FR-A4** | A measured improvement in agent output, **sliced for why / temporal / contradiction questions** | An aggregate score is dominated by lookups and **will not show the difference** — and will be believed | **Later, and it is the stage exit** | Paired, per-slice, against a **pinned** store snapshot, with a measured noise floor and cost in the denominator | Evaluation harness |

### 9.8 Runtime and execution

**Challenged.** The project's own architecture review states that **the knowledge system
does not need the fifty-chapter runtime to exist**, and names four primitives
worth adopting, each with its own trigger. This PRD adopts that position for
V1.

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-X1** | Identity-keyed action/extraction reuse | Redelivery safety | **V0.5** | See FR-K2 | Test |
| **FR-X2** | A transactional outbox, so a claim write and its notification are not two writes with a gap | Prevents a consumer missing an event that was committed | **Later** — trigger: the first consumer that reacts to a knowledge system event | At-least-once delivery under kill-mid-write | Test |
| **FR-X3** | Leases and version-CAS | Two workers on one observation | **Later** — trigger: ingestion runs more than one worker. **Before that it is theatre** | Two workers racing one observation produce one claim, not two | Concurrency test |
| **FR-X4** | Park — a run awaiting human confirmation holds **no process, no connection, no in-memory timer** | Human confirmation in the claim lifecycle | **Later** — trigger: human confirmation enters the write path | Survives a restart while parked | Test |
| **FR-X5** | Concurrency is **re-classify on conflict**, not retry on conflict | Retrying re-applies a classification computed against a stale claim and silently erases the winner's decision | **V1** (it is a rule, not machinery) | Conflict path re-runs classification | Test |
| **FR-X6** | The remaining kernel machinery — relay claims, sweepers, worker pools, per-tenant admission, budget ledgers | Arbitrates contention **that does not exist with one writer** | **Blocked on Q8/Q20** — write the single-writer invariant profile first | A written profile marking each of the 39 invariants applies / does not / applies weakened | Half a day of reading |

### 9.9 Observability

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-O1** | **Three signals on day one:** discard rate per source, claims per entity, contradictions raised vs confirmed | Each detects a whole failure class. **A dashboard nobody reads detects nothing** | **V1** | All three exist **before the first source is enrolled** | Inspection |
| **FR-O2** | Admission records **which rule** decided, not just the verdict | The discard rate is meaningless without it | **V1** | Verdict + rule id stored per observation | Test |
| **FR-O3** | Rejection **rate by reason** is recorded per proposal | Tells you which stage is rejecting and whether that changed | **V1** | Reasons enumerated, rate plotted | Metric |
| **FR-O4** | Per-source observation volume is alerted on **absence** | *A source that goes quiet looks identical to a quiet team* | **V1** | Alert fires below a per-source floor | Test |
| **FR-O5** | knowledge system events go on the **existing** event spine — no second event system, no second transport | Otherwise every consumer inherits two replay contracts | **V1** | One event stream | Review |
| **FR-O6** | Scope misses and vocabulary misses are **two separate counters** | They have different remedies, and conflating them makes the trigger unreadable | **V1** | Two counters | Metric |

### 9.10 Recovery

| ID | Requirement | User value | Pri | Acceptance criteria | Validation |
|---|---|---|---|---|---|
| **FR-N1** | **The rebuild invariant:** drop the claim store, index, world model and contradiction register; replay the log; arrive at the same state | If you cannot, something downstream holds information that was never observed | **V1** | Rebuild test in CI on a seeded log | Automated test |
| **FR-N2** | Reprocessing history with a better extractor is the **normal** way the knowledge system improves, not a disaster-recovery event | Makes improvement cheap forever | **V1** | Reprocess runs end to end on the seeded log | Test |
| **FR-N3** | The read path **never fails a step**; the write path **never fails a run** | knowledge system unavailability must not take down its consumer | **V1** | Injected knowledge system failure does not fail the caller | Fault-injection test |
| **FR-N4** | Behaviour when the knowledge system has **no** context is specified **per capability** — proceed with less, or abstain | **UNSPECIFIED in every current document.** *"The read path never fails a step"* does not say what the step then does | **V1 — requires a decision first** | Each capability documents its no-context behaviour | Review |

---

## 10. Non-Functional Requirements

**No numeric target appears below unless the repository supports it. Everything
else is TBD, and TBD is an honest answer.**

| Area | Requirement | Target | Basis |
|---|---|---|---|
| **Correctness** | Extraction precision on a reviewed sample, measured before any downstream tuning | **≥ 85% pre-registered floor.** Below it, the design needs a human confirmation step in the write path — *which is a different product with different economics* | Pre-registered in A3; **not yet measured** |
| **Correctness** | Every confidence number is calibrated against a **measured** noise floor | **TBD — the noise floor has never been measured.** Until then, every effect size is a number without its error term | Q11 |
| **Determinism** | Classification and reconciliation are **deterministic**; the first tests use no model | Binary | ADR-0010, C1 |
| **Determinism** | Clock and randomness are **ports**; wall-clock calls are banned outside an allowlist. **Widen the allowlist per module with a comment; never relax the test** | Binary, CI-enforced | I8 |
| **Provenance** | Every claim traces to an observation. Evidence handles are **server-minted** — *a caller-supplied id is the whole attack* | Binary | EV2 |
| **Provenance** | Taint is monotonic under the provenance lattice — **nothing clears taint** | Binary, **pending Q14** | Q14 is a security judgement, not an architectural one |
| **Security** | The agent reaches the knowledge system only through curried tools; enforced by an import-boundary test | Binary | ADR-0012 |
| **Permission isolation** | A cross-tenant read **raises**. A denied read raises | Binary | ADR-0016 |
| **Permission isolation** | Overlapping, non-partitioned audiences | **NOT DESIGNED.** Blocking before any non-public source | Q10 |
| **Durability** | Claim + version + evidence + outbox event commit in **one transaction** | Binary. **This is the decisive argument against a second store engine** | PS1 |
| **Recoverability** | Rebuild from the observation log reproduces state exactly | Binary, CI | O5 |
| **Recoverability** | Every store declares and **tests** a deletion route before it ships | Binary | ADR-0017 |
| **Observability** | The full chain from observation to answer is reconstructable; the retrieval record is **sampled** | Sampling fraction **TBD** | §14 |
| **Latency** | Context assembly on the agent read path | **TBD.** No budget, no measurement, no user expectation exists | — |
| **Scalability** | Observation volume, claim count, concurrent readers | **TBD.** The first environment is a single local project; **specifying a scale target now would be inventing a number** | Q3 §7 |
| **Cost** | Model calls per observation | **One extraction call per admitted observation**, bounded by admission. Absolute cost **TBD** | Admission design |

---

## 11. Product Boundaries

**The section that prevents conceptual overlap.** Similar terminology across
documents is not evidence that two things are the same thing.

### 11.1 The six things, and what each owns

| | **Owns** | **Does NOT own** |
|---|---|---|
| **knowledge system** | Observations, claims, versions, evidence, entities, contradictions, the predicate schema registry, the source-precedence policy as *configuration it reads*, the capability layer | **Execution.** It never calls a tool the agent owns, never applies an effect, never writes a goal. It does not own the source-precedence policy's *contents* — a human does |
| **Runtime** | Run / Episode / Step / Activity / Park, the ExecutionGraph, leases, checkpoints, the effect ledger, the outbox | **Any judgement** — every judgement lives behind a port. **It never writes a claim directly** |
| **Principal Agent** | Goals it was **given**, decisions with sealed predictions, commitments, delegation grants, outcome records | **Four prohibitions:** it may not set its own goals, execute work itself, grade its own outcomes, or hold organizational knowledge in harness state. **It is a Run — a client of the runtime, not a layer inside it** |
| **Environment adapters** | Filesystem, VCS, HTTP, inference, clock, scope adapters — applying effects and observing the world | **Effect policy.** A tool *declares* an effect tag; it does not decide whether it may run |
| **MCP** | Transport and protocol | **Everything else.** No authorization decision, no ranking, no assembly. **A strict projection, deletable without losing anything** |
| **Memory** | A **write path and a lifecycle** — propose → abstract → route → classify → apply | **It owns no facts and no store.** It operates over several stores and does not become the owner of anything by remembering it |

### 11.2 What crosses the boundaries

```
  RUNTIME -> BRAIN   (down, always via a tool)
     Principal (never optional)  |  run.as_of  |  run_id
     a QUESTION or a SCOPE       |  budget_tokens

  BRAIN -> RUNTIME   (up, as a tool result)
     a bounded, ranked, cited claim set
     OPEN CONTRADICTIONS -- never omitted
     validity intervals | an evidence handle per claim
     what was NOT found, and what could not be resolved

  WHAT NEVER CROSSES
     the runtime never writes a claim directly
     the knowledge system never calls a tool the agent owns
     the knowledge system never sees a client-supplied role or account
     the knowledge system never returns a claim the Principal may not see
        -- and a denied read RAISES rather than returning empty
```

### 11.3 The boundary that is genuinely disputed

**CORRECTED 2026-09-14.** This previously read *"**FACT:** two documents in this
repository specify incompatible Phase 1 schemas and neither acknowledges the
other."* **Only one of the two is in this repository**, so that sentence did not
meet this project's own definition of FACT — *"verifiable in this repository,
right now: point at the file or run the command."* What is verifiable:

**FACT: one document in this repository specifies a Phase 1 schema. A second,
cited by ten ADRs, is absent. Two further shapes exist, and no two of the four
are a live disagreement between readable documents.** See
[ADR-0029](decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md),
[ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md),
and `01-architecture-map.md` §4.1 and §4.7. The table below is retained as the
only surviving record of the absent document's position, and its right-hand
column is **[REPORTED — source absent]**.

| | Memory Management Architecture (2026-09-02) | knowledge system (2026-09-05) |
|---|---|---|
| Entities table | **Rejected for Phase 1** | **Required in Phase 1** |
| Entity resolution | **Deferred** | **Phase 1**, and *"the component most likely to be underestimated"* |
| Contradictions table | **Rejected** — version rows plus an event suffice | **Required**, with severity that gates actions |
| Relationships | **Deferred to Phase 3** | Present in the Phase 1 figure |

**A plausible reconciliation exists** — that Memory scopes a *runtime memory
subsystem* over already-identified entities while the knowledge system scopes an
*organizational store* where identity must be established — **and it is an
inference, not a decision. Nobody has written it down.**

**Product consequence: no schema may be built until this is decided (Q7, D4).**
This PRD does not decide it.

### 11.4 Where MCP fits

**MCP is a transport projection, and it is not in V1.** Three reasons, all from
the source material:

1. It projects a capability layer that **does not exist yet**. Built first, it
   becomes the thing that constrains the layer it should project.
2. **Identity becomes a three-party problem** — the IDE, the agent and the
   knowledge system — and the token must carry an identity the knowledge system can verify **without
   trusting the middle one.** Undecided (Q9).
3. **Structural containment is lost.** Internally, tool projection makes an
   unauthorised query *absent from the schema*. An MCP client sees the same
   tool list as everyone, so enforcement falls back to runtime checks.

**Recorded prediction, because it is likely to happen anyway:** MCP is one of
the two things most likely to be built early, because *"it exposes MCP"* sounds
like progress and can be demonstrated without the knowledge system being good at anything.
**If it is built early regardless, make it a strict projection with no logic of
its own, so it can be deleted without losing anything.**

---

## 12. Trust Model

### 12.1 What the system is allowed to believe

**Nothing, by default.** A stored claim is a claim: it has a source, a
confidence, a validity interval, and possibly a contradiction. **Memory is not
truth.**

### 12.2 What counts as evidence

| Counts | Does not count |
|---|---|
| An observation in the log, with a locator and a digest | A model's assertion |
| Independent corroboration from **distinct runs** | The same run repeating itself |
| A deterministic probe's result | A model's judgement that something looks right |
| A human who owns the subject, confirming | A human being confidently wrong (Q13 — **unresolved**) |
| A test, **and the separate fact of whether it passes** | A test's existence alone |

### 12.3 What a model-generated proposal means

**A proposal is a request, not a fact.** The model proposes; classification
decides; corroboration confers standing. **There is no `remember()` tool**, and
the reasoning is four distinct failures in one phrase — an agent writing memory
from inside its own run writes something *unreviewed, unabstracted,
unclassified, and from inside the run*.

### 12.4 What confidence means

**Derived from corroboration. Never asserted by the model.** And:

> **FACT: no confidence number in this project has been calibrated, because no
> noise floor has been measured.** Any threshold written before that
> measurement is fitting to noise.

### 12.5 How contradictions work

A contradicting observation **lowers** confidence in the standing claim; it
never flips it. **A contradiction does not make the other claim true.** The
failure to design against is not a *missed* contradiction but a **false** one: a
system that treats every scope overlap as a conflict drives every claim in a
busy scope below the load floor **and looks healthy throughout.**

### 12.6 When the system must abstain

- No claim in scope → abstain, and say **which** of the three things that means
  (§8.3).
- A blocking contradiction → **refuse to act**, and surface the disagreement.
- Below the load floor → the claim is **inert**; it influences nothing.
- Cannot resolve an entity → return the mention **unresolved**, rather than
  forcing a match.

**Abstention is a measured success, not a failure.** Measure the abstention rate
on questions whose answer is genuinely absent, **seeded deliberately so the
denominator is known.**

### 12.7 How verification changes standing

**Asymmetrically, and that asymmetry is the whole safety property:**

> **A model judgement may LOWER a verdict and may NEVER RAISE one.**

A model asked to evaluate its own system's output shares a training
distribution — and therefore a set of blind spots — with the model that produced
it. It approves fluent, well-structured, wrong output because that is what it
was trained to prefer.

### 12.8 What the system must never assume

| Never assume | Because |
|---|---|
| **Model output is evidence** | A model proposes. Standing comes from independent corroboration |
| **Confidence is correctness** | Nothing here is calibrated |
| **Authority can be inferred** | Authority inferred from recency, seniority or confident phrasing is **wrong precisely in the cases that matter, and wrong invisibly** |
| **A claim is still true** | `unverified` is the default, and it is honest |
| **An empty result means no data** | It may mean *denied* — which is why a denied read raises |
| **A summary is evidence for what it summarises** | Its evidence chain does not terminate in an observation |
| **Its own confidence is independent** | Every input to the knowledge system's confidence is its own output: corroboration *it* counted, from observations *it* admitted, extracted by a prompt *it* ran |

---

## 13. Product Safety and Failure Modes

**Ranked by how hard the failure is to see, not by how much damage it does.**
Almost none produces an error — that is the point of the ranking.

| # | Failure | Consequence | Prevention | Detection | Recovery |
|---|---|---|---|---|---|
| 1 | **Confidently wrong current state** | A decision taken on a claim that stopped being true. **No error** | `unverified` as the honest default; decay from `last_confirmed` | Probe loop; contradiction rate; claim age | The probe writes an observation; the claim re-enters the pipeline |
| 2 | **Wrong entity / entity fragmentation** | Claims about one thing scatter across four identities and never join. **Every component works; the system feels useless** | Anchor on system identifiers; curate aliases; **accept unresolved rather than forcing a match** | Claims-per-entity distribution; unresolved-mention rate | Merge — **and the merge/split lifecycle does not exist (Q16)** |
| 3 | **A contradiction erased** | A confident answer while the system holds evidence against it. **The exact failure the product exists to prevent** | Contradictions are **never dropped for budget** | Assembly test under a minimal budget | Re-assemble; investigate why it was droppable |
| 4 | **Permission leak through a claim** | A private fact served outside its audience. **No error, no log line** | Label at ingest; propagate to every derived claim; **never reconstruct** | **Only a test** | Retire affected claims; re-derive. **The leak itself is not undoable** |
| 5 | **Incorrect authority** | The system trusts a confident junior statement over a verified probe | The policy is **authored configuration with a named owner**; never inferred from tone or seniority | The policy is versioned and reviewed | Correct the policy; **reprocess history** |
| 6 | **False confidence** | Numbers that look calibrated and are not | No threshold before a measured noise floor | The reviewed sample as a regression test | Re-measure; re-tune |
| 7 | **Missing evidence** | A claim nobody can check | Claim + evidence in one transaction; a claim without evidence is unreachable | Schema constraint | Unreachable by construction |
| 8 | **Contradiction fatigue** | Low precision → the detector is muted → **the capability is gone permanently regardless of later quality** | Conservative severity; advisory-only first | Raised-vs-confirmed ratio | **Hard. Prevention is the only real answer** |
| 9 | **Admission skipped** | The store fills with restatements; cost rises with headcount, precision falls | Discard rate as a headline metric **before the first source is enrolled** | Discard-rate distribution | Re-admit from the log; reprocess |
| 10 | **Duplicate extraction from redelivery** | Two claims from one text with **different content**, not recognisable as duplicates | Identity-keyed extraction, claimed **before** the model call | Claims whose evidence cites the same observation twice | Reprocess |
| 11 | **Extraction prompt regression** | A prompt change quietly halves precision; every downstream number degrades slightly | Gate prompt changes on the reviewed sample | The sample as a regression test against a measured floor | Revert; reprocess only after the new extractor beats the old |
| 12 | **Incorrect execution on knowledge system context** | An agent acts on a wrong claim | Blocking contradictions refuse action minting; verification before knowledge | The effect ledger and the outcome probe | Reverse the effect; the outcome re-enters as an observation |
| 13 | **Recovery failure — reprocessing produces a different world** | Replay yields a different store than the incremental path did | The rebuild invariant, decided on day one | **The rebuild test, in CI on a seeded log** | Investigate: something downstream holds information never observed |
| 14 | **Self-confirmation through a human** | The agent asserts something; a human internalises it; later states it as their own belief — **a genuine observation from a genuine actor, indistinguishable from independent corroboration** | Partial: origin tracking | Partial | **UNSOLVED. Recorded, not fixed** |
| 15 | **Aggregate leakage** | *"Three teams are blocked on X"* discloses a private fact | *An aggregate that cannot be cited is not produced* — **a mitigation, too strict in some cases and too loose in others** | None general | **UNSOLVED** |
| 16 | **A wrong policy, authored once and never revisited** | Every precedence decision downstream is wrong, **consistently and invisibly** | A named owner; versioned; reviewed | **None designed.** A product risk this PRD raises and does not solve | — |

**Failure 16 is not in any source document.** It follows from A2: if authoring
the policy is an onboarding tax, the path of least resistance is to author it
once, badly, and never look again — and **nothing in the design detects a policy
that is wrong.**

---

## 14. Observability and Evaluation

**The governing rule:**

> **The knowledge system must not be allowed to declare itself correct.**

### 14.1 The four instruments that can establish correctness

| # | Instrument | Establishes | Cost | Bias |
|---|---|---|---|---|
| 1 | **A deterministic probe** | Whether a claim about a system is still true, by inspecting the system | Low per probe | **None — the strongest instrument available** |
| 2 | **Independent corroboration from distinct runs** | That several independent observations agree | Free | Vulnerable to a common upstream cause |
| 3 | **A human who owns the subject** | Whether a contradiction was real and worth raising | High, rate-limited by patience | **The observer is the observed** |
| 4 | **A held-out question set with known answers** | Temporal and reconciliation accuracy | Built once, from real history | Fixed set; can be overfit |

**Not on this list, and deliberately: the model's own assessment.**

### 14.2 Evaluation questions, and how each is answered

| Question | Ground truth | Method |
|---|---|---|
| Is a claim correct? | A probe, or a human owner | Probe result; owner confirmation |
| Did retrieval find the right claims? | The retrieval record + the claim store queried directly | W4 step 3 — separates *not present* / *not retrieved* / *dropped* |
| Is contradiction detection any good? | Owner confirmation | **Raised vs confirmed. The second number is the one that matters** |
| Is temporal reasoning correct? | A held-out set built from **real** history | *"What did we believe in June?"* |
| Does it abstain when it should? | **Deliberately seeded** absent answers, so the denominator is known | Abstention rate |
| Is it falsely confident? | The measured noise floor | Confidence vs observed correctness |
| Does it rebuild? | The observation log | Replay in CI; compare |

### 14.3 The rules that make measurement meaningful

1. **The noise floor is measured before any effect size is reported.**
2. **Evaluation runs against a PINNED store snapshot** — a store's contents are
   a function of what runs have happened, so *"the same memory"* across two
   subjects is only meaningful if pinned.
3. **Paired comparison, k rollouts, per-slice gating, cost in the denominator.**
4. **Retrying is forbidden in the test suite.** A test that passes on the second
   attempt is reporting a defect as a success.
5. **Measured gains do not sum.**
6. **Never report an aggregate quality score.** It will be dominated by lookups
   and **will not show the difference — and it will be believed.**

### 14.4 Day-one signals — three, not twenty

| Signal | Shape | Detects |
|---|---|---|
| **Discard rate** per source | Distribution | Admission skipped, or eating signal |
| **Claims per entity** | Distribution | Entity fragmentation |
| **Contradictions raised vs confirmed** | Ratio | Detector precision, **before fatigue sets in** |

**Everything else waits.** A dashboard nobody reads detects nothing.

### 14.5 Signals that alert on an age, an absence, or a distribution

None of the failures in §13 produces an error, so **none of these alerts on an
error**: oldest unprocessed proposal **age**; per-source volume **absence**;
OOV rejection rate; rejection rate **by reason**; verification-status
distribution; promotion rate; **scope misses vs vocabulary misses as two
separate counters**; unresolved-mention rate.

### 14.6 The one new durable record, and why it is worth its cost

Every link in the chain except one falls out of records that already exist for
other reasons. The exception is the **retrieval record**.

**Without it, "the knowledge system gave a bad answer" cannot be separated into *the claim
was wrong*, *the right claim was not retrieved*, or *the right claim was
retrieved and dropped for budget*. Those three have completely different
fixes and are indistinguishable afterwards.** It is written on the read path,
so **sample it** — a fixed fraction, plus 100% for any answer later disputed.

---

## 15. MVP Acceptance Criteria

**Every criterion below is testable, and each is either preserved verbatim from
the build order and validation strategy or derived from a requirement in §9.**

### 15.1 V0 acceptance

| # | Criterion | Pass condition |
|---|---|---|
| **AC-0.1** | 50 real questions collected from the last 90 days and classified | The classification exists, the threshold was registered **before** counting, and the result is recorded whichever way it lands |
| **AC-0.2** | 20 real tasks run blind; 10 with hand-written context; graded by someone who did not know the arm | A per-arm score with its spread. **A null result is a pass for the experiment and a fail for the thesis** |
| **AC-0.3** | 200 real observations extracted and **every** output reviewed | Precision, recall and kind-assignment agreement reported **separately** |
| **AC-0.4** | The precedence meeting held and timed | Either a reviewed policy file with a **named owner**, **or** the disagreement written down as an open question. **Both are valid outcomes; silence is not** |
| **AC-0.5** | Identity-keyed extraction shipped | A redelivered observation produces no second claim and no second model call, proven by a test, **within one week** |

### 15.2 V1 acceptance

| # | Criterion | Pass condition |
|---|---|---|
| **AC-1.1** | **The five-question test.** Five real questions from real history | Each answered with: the implementation fact **and its verification date**; the decision **with author, date and rationale**; whether they agree; and **if not, the gap stated plainly** |
| **AC-1.2** | Extraction precision on the reviewed sample | **Measured**, reported with the sample size, and compared against the pre-registered floor |
| **AC-1.3** | The rebuild test | Drop every derived structure, replay the log, arrive at the same state. **In CI** |
| **AC-1.4** | The reconstruction test | Current claims rebuild from version history |
| **AC-1.5** | The identity-replay test | A redelivered observation produces no second claim |
| **AC-1.6** | The tenant-isolation test | A cross-tenant read **raises** — not returns empty |
| **AC-1.7** | The deletion-route test | Every store enumerates; a store with no route **fails loudly** |
| **AC-1.8** | The judgement-cannot-upgrade test | A model judgement lowers a verdict and **cannot** raise one |
| **AC-1.9** | The import-boundary test | The agent package does not import the knowledge system store |
| **AC-1.10** | The context-assembly budget test | Under a minimal budget, contradictions, provenance pointers and temporal qualifiers **all survive** |
| **AC-1.11** | The three day-one signals | All three exist and have values **before the first source is fully enrolled** |
| **AC-1.12** | Clock discipline | Wall-clock calls banned outside an allowlist, enforced in CI |

### 15.3 The criterion that decides whether V1 was worth building

**AC-1.1 is the milestone, and question 2 of the five is the best available
test:** *"Which product are we building?"* **has a known and uncomfortable
answer — two decisions in this repository disagree.** If the knowledge system surfaces that
contradiction from observations alone, without being told, the thesis is
demonstrated on real data.

---

## 16. Metrics

**No vanity metrics.** Observation count, claim count, source count and "sources
connected" are deliberately absent: each can rise while the product gets worse.

### 16.1 Product metrics — does the user get value?

| Metric | Why it is not vanity | Baseline |
|---|---|---|
| **Confirmed contradictions** — raised **and** confirmed worth raising by the owner | The one event that is the thesis | **0.** One is the milestone |
| **Five-question test pass rate** | Direct measurement of the product's core promise | Unmeasured |
| **Questions answered with a resolvable citation** | An unciteable answer is a search result with extra steps | Unmeasured |
| **Share of asked questions that are why / temporal / contradiction** | The product's addressable share of real demand | **Unmeasured. This is V0.1** |
| **Blind-graded improvement on agent tasks, sliced** | The consumer bet. **Never reported as an aggregate** | **Unmeasured. This is V0.2** |

### 16.2 System metrics — does the mechanism work?

Discard rate per source · claims per entity · OOV rejection rate and **its
curve as the vocabulary grows** · rejection rate by reason · promotion rate
(provisional → active) · oldest unprocessed proposal **age** · per-source volume
(alert on **absence**) · **scope misses vs vocabulary misses, separately** ·
unresolved-mention rate · verification-status distribution.

### 16.3 Safety metrics — does it avoid dangerous behaviour?

| Metric | Target |
|---|---|
| **Contradiction precision** (confirmed ÷ raised) | Above a threshold **registered in advance**, and it gates whether contradictions ever block |
| **Cross-scope read attempts that raised** | 100%. **Any figure below 100% is a leak** |
| **Claims whose evidence chain does not terminate in an observation** | **0**, and unreachable by construction |
| **Untrusted-derived claims at ACTIVE** | **0**, enforced by a CHECK constraint |
| **Abstention rate on deliberately seeded absent answers** | High and **measured** — the denominator is known because the absence was seeded |
| **Mute rate** in any channel where the system volunteers | **0.** *A few bad unprompted interventions and the capability is gone permanently* |
| **Answers later disputed by an owner** | Tracked; each triggers 100% retrieval-record capture |

---

## 17. Validation Plan

**Four different things, deliberately separated. Collapsing them is how an
internal tool gets mistaken for a business.**

### 17.1 Dogfooding — proves the mechanism, proves nothing about the market

Use the real engineering workflow as the first environment the knowledge system observes.
**The knowledge system observes. It does not control.**

**Why this environment:** already instrumented; high claim density; real
messiness that synthetic data does not produce; the consumer is present;
feedback in hours; **and the people who know whether a claim is true are
available to say so.**

**The limits, stated before the benefits are relied on:**

1. **Dogfooding is not product validation.** One team, unusual tolerance for its
   own failures.
2. **This workflow is unusual** — **FACT:** no pull requests, no CI, no issue
   tracker.
3. **One team is not an organization.** Overlapping permissions, conflicting
   authority and cross-team contradiction — the problems the design exists for —
   barely appear at this scale.
4. **The observer is the observed.** The people judging whether a contradiction
   was worth raising are the people who wrote the claims.

**The immediate product finding:** the highest-value sources for this design —
PR reviews, CI results, tickets — **are exactly the ones this workflow does not
produce.** Adopting it therefore implies **changing the workflow first**, which
is a real cost and **should be decided rather than drifted into** (D6).

### 17.2 Technical validation

The §15.2 test suite, plus the V0.3 extraction sample as a standing regression
test against a measured noise floor.

### 17.3 Product validation

The five-question test (AC-1.1), the confirmed-contradiction milestone, and the
sliced agent-output measurement. **All three require real users asking real
questions — which requires V0.1 to have found real questions.**

### 17.4 Market validation — not attempted by V0 or V1, and that is a gap

**FACT: no market validation has ever been performed for this direction.** The
cheapest available:

- **Five discovery interviews with engineering leaders.** Do not pitch. Ask what
  they last got wrong because two sources disagreed, and what it cost. **Fewer
  than three specific, expensive, unprompted incidents means the pain is not
  acute enough to fund a company.**
- **A competitive scan with fetched primary sources**, specifically for
  contradiction/conflict surfacing shipped since 2026-09-06. The existing scan
  searched rather than fetched several sources, and the proxy blocked others.

**This PRD recommends running both alongside V0.** They cost a week and they are
the only evidence that speaks to D2 (who the customer is).

### 17.5 What this plan explicitly does not claim

> **Dogfooding does not prove market demand.** A confirmed contradiction inside
> our own repository proves the mechanism works on real data. **It says nothing
> about whether anyone will pay for it.**

---

## 18. Roadmap

**Every stage exits on a measurement or a decision. A stage whose exit is
"it's built" always exits.**

| # | Stage | Objective | Capability delivered | Evidence required | Exit criterion | Decision it unlocks |
|---|---|---|---|---|---|---|
| **0** | **Decide and measure** | Establish whether the premise holds, and clear the blockers a human must clear | **No software except V0.5** | V0.1–V0.4 | The policy exists as a reviewed file with a **named owner** — or the disagreement is recorded; the question mix measured against a pre-registered threshold. (Q1 is already resolved — see [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md)) | Whether to build V1 at all |
| **1** | **One source, end to end** | Make the knowledge system's value visible on one source | §7.2 | Real observations from a real source | **AC-1.1** (five questions) **and AC-1.2** (measured precision) | Whether the mechanism works |
| **2** | **The second source** | Test what was accidentally source-specific — **and it is the first point at which a cross-source contradiction is possible at all** | A second adapter; entity resolution stops being free | Two sources, one of which contradicts the other | **One contradiction detected across sources that a human confirms was worth raising.** One instance is the milestone | Whether the thesis is demonstrated |
| **3** | **Temporal and verification in anger** | Answer history, and notice staleness without being told | `as_of`, supersession chains, the probe loop | A held-out set from **real** history | *"What did we believe in June?"* answered correctly, **and probe-disagrees fires on a real stale claim before a human notices it** | Whether time is handled or merely stored |
| **4** | **External agents** | Test the consumer bet | Hardened capability layer; MCP as a **strict read-only projection** with **fewer** capabilities | Q9 decided **first** | **A measured improvement, sliced for why / temporal / contradiction** — paired, per-slice, against a pinned snapshot, with a noise floor and cost in the denominator | Whether agents are the consumer |
| **5** | **Breadth and participation** | Add the hard sources; let the system speak | Slack; participation in **one** channel | Admission, entity resolution and vocabulary working on easier sources | **Volunteer precision above a threshold registered in advance, and a mute rate of zero. Automatic demotion if not** | Whether it can participate |
| **6** | **Principal Agent — the unblocked half** | Authority and delegation without outcome judgement | A Principal Agent **as a Run**; grants; the assess–decide loop | Stage 4 exit | It deliberates, parks for a human, resumes, and founds a delegated run — **surviving a restart** | Whether delegation is safe |
| **7** | **Organizational structures** | — | Goal records, sealed predictions, commitments, the outcome ledger | **An organizational act, not engineering** | Goals exist, written by a human, with measures and baselines. **Until then this stage cannot start** | Whether outcomes can be judged |
| **8** | **Controlled autonomy** | Earn autonomy rung by rung | The autonomy ladder | Stage 7 | Each rung's threshold met, **measured at the rung below where being wrong is cheap**, with automatic demotion | Whether to widen the grant |
| **9** | **Autonomous organizational workflows** | — | — | — | **Not designed. Do not plan against it in detail** | — |

### 18.1 Where this PRD challenges the sequence

| Change | Reason |
|---|---|
| **"Evidence / provenance / temporal / trust" is not a stage.** Folded into Stage 1 | **These are properties of the first row written, and several are unrecoverable if omitted.** Building Stage 1 without them does not produce an early version — it produces a permanent gap in history plus a migration |
| **Evaluation is not a stage.** Its instruments move into Stage 1; its use is continuous | *Until you have the noise floor, every effect size is a number without its error term.* And a separate measurement stage means the preceding stages exited unmeasured |
| **A second-source stage is inserted** | **It is where the thesis is actually demonstrated.** Neither source alone can produce a cross-source contradiction |
| **MCP and agent integration are one stage, not two** | MCP is a projection of a layer that exists by Stage 1. *The server is a later afternoon.* Making it its own stage invites building it before anything consumes it |
| **Stage 0 is decisions, not documentation** | Q2 **cannot be unblocked by building.** A Stage 0 that exits on documentation alone hands Stage 1 a blocker it cannot clear. (Q1 was the same kind of blocker and is now resolved, not built past) |
| **The runtime is not a stage at all.** Four primitives, each with its own trigger | The project's own review: *"The knowledge system does not need the fifty-chapter runtime to exist"* — and adopting the primitives as a block *"would be a rewrite justified by architecture rather than by a problem"* |
| **V0 is added in front of everything** | Four load-bearing assumptions can be falsified for a few days' work each, and **none has ever been tested** |

### 18.2 Stages that deliberately do not exist

**No ingestion framework** — *adapters are written one at a time against a fixed
observation shape; the framework is that shape.* **No knowledge graph** —
relationships are claims from Stage 1. **No knowledge system UI before Stage 3** — before
knowing whether the knowledge system is right, a UI measures nothing. **No
migration/consolidation stage** — reprocessing from the log is the normal way
the knowledge system improves.

---

## 19. Explicit Non-Goals

| Not built | Classification | Why | Trigger to revisit |
|---|---|---|---|
| A RAG system / search box over company documents | **REJECTED** | Perfect retrieval still produces the §3.2 failure | None |
| A knowledge graph product | **REJECTED for V1** | A relationship is a claim; a second store engine breaks same-transaction commit | Measured 3+ hop need that CTEs demonstrably lose |
| Embeddings | **NOT YET** | The trigger is a measurement that does not exist | Vocabulary misses above a pre-registered threshold for two consecutive weeks. **If scope misses dominate instead, an index cannot help** |
| An MCP server | **NOT YET** | No stable capability layer; Q9 undecided | Stable capability layer **and** Q9 decided |
| A general agent platform | **REJECTED** | *"Platform" requires a third and fourth environment and an abstraction that survives contact with them.* Anyone pitching it as a platform now is pitching a hope | Two more environments |
| An autonomous knowledge curator | **REJECTED** | A loop deciding which claims to keep, merge or delete is optimising a store against a signal that **cannot see what it is destroying** | The protected property becomes measurable first |
| A summarisation / consolidation layer | **REJECTED** | A summary is not evidence for what it summarises | Nothing in any planned stage |
| A system that infers authority | **REJECTED** | Wrong precisely in the cases that matter, and wrong invisibly | None |
| An agent that speaks unprompted | **NOT YET** | *A few bad unprompted interventions and the agent is muted permanently* | Contradiction precision above a threshold registered in advance |
| A multi-agent framework | **REJECTED** | **No second agent has a job** | A second agent has a job |
| A knowledge-authoring UI writing directly | **REJECTED** | Creates claims with no observation behind them and **breaks the rebuild invariant** | Route through `propose_claim` with `source_class=human_authored` instead |
| Multi-tenant contention machinery | **NOT YET** | Arbitrates contention that does not exist with one writer. **Keep `tenant_id` in the key** | A second tenant, plus the Q8 profile |
| The Principal Agent's outcome half | **BLOCKED** | Depends on goal records with measures and baselines that do not exist. **No knowledge system work brings it closer** | A human writes goals |
| More architecture documents | **STOP** | **FACT: 47 commits, all documentation, zero product source files.** This is the failure mode with the highest prior | A document that unblocks a named decision |

---

## 20. Open Product Questions

Imported from `10-open-questions.md`, filtered to those that **affect product
scope**, and reclassified by product impact.

**Q1 (which product) is RESOLVED, 2026-09-14** — see
[ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md).
`prd.md` was exploratory, not a competing decision; this PRD is the confirmed
live plan. Removed from the blocking list below.

### 20.1 Blocking

| # | Question | Why it blocks the product |
|---|---|---|
| **Q2** | **Who authors the source-precedence policy, and who may change it?** | Every downstream mechanism — precedence, contradiction, retrieval ranking — is **meaningless** without it, and it **cannot be inferred by design** |
| **Q3** | **What is InOrbitX, and where does the knowledge system run relative to it?** | Established: a broker insurance portal, local to a desktop. **Unknown: everything that determines what can be observed.** And *local knowledge system / hosted knowledge system with local collector / fully hosted* are **materially different products** |
| **Q7** | **How do the Memory and knowledge system schemas reconcile?** | **No schema may be built until this is decided** |
| **Q17** | **Do the valuable questions occur at a useful rate?** | **The premise.** Not mechanically blocking, which makes it urgent rather than blocking |

### 20.2 Important

| # | Question | Product impact |
|---|---|---|
| **Q5** | What is the initial predicate vocabulary? | It must be **derived from real questions** — which have never been collected |
| **Q6** | Which single source is ingested first? | *A fact about the organization, not about the architecture.* Falls out of Q3 |
| **Q10** | How are overlapping (non-partitioned) permissions modelled? | **Blocking before any non-public source**, and a regulated domain makes that immediate. **One wrong join leaks, and the leak has no error** |
| **Q18** | Will customers author and maintain a source-precedence policy? | **An unpriced onboarding tax.** Gates time-to-first-value behind an internal political argument. **Blocking for a business model** |
| **Q19** | Does organizational context measurably improve agent output? | Measures the **ceiling** of the strategic chain |
| **Q20 / Q8** | How much of the runtime is on the critical path? | **May remove most of the planned work.** Half a day of reading |
| **Q11** | Confidence floor, retire floor, decay half-life | Tuning before the noise floor is measured is **fitting to noise** |
| **Q15** | What makes a contradiction blocking rather than advisory? | Blocking contradictions **refuse actions**, and no rule assigns severity |
| **Q21** | Can this team convert design into shipped code? | **The highest-prior failure mode: a correct architecture, more of it, indefinitely** |

### 20.3 Later

| # | Question |
|---|---|
| **Q4** | Which vocabulary is normative for code — handbook or specification |
| **Q9** | Whose Principal is an MCP caller — **decide before the server exists, not during** |
| **Q12** | How large the predicate vocabulary grows before maintaining it is the bottleneck |
| **Q13** | How a human correction is distinguished from a human being wrong |
| **Q14** | Whether a claim inherits taint through a schema-validated extraction |
| **Q16** | The entity merge/split lifecycle — **required before the second source** |

### 20.4 Structurally unsolved, and not tasks

Noticing a claim is wrong when nothing new has been observed · self-confirmation
mediated through a human · causation from organizational outcomes · knowing what
the organization does **not** know · **whether any of this beats a good search
box for the majority of questions.**

---

## 21. Product Decisions Required Before Implementation

**Eight decisions. Five block. None is an engineering task.**

### D1 — Which product? *(RESOLVED, 2026-09-14)*

| | |
|---|---|
| **Original question** | Was `prd.md` (macOS paperwork agent) a competing direction against the knowledge system, requiring a choice, a sequence, or a split? |
| **Resolution** | **No contest existed.** The project owner stated directly that `prd.md` was written to explore a different, curiosity-driven question — using the agent runtime to control iOS/macOS — never as a competing product decision. The knowledge system direction, and this PRD, are confirmed as the live plan |
| **Decision record** | [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md), superseding [ADR-0021](decisions/ADR-0021-product-direction-is-contested.md) |
| **Consequences** | `prd.md` is retained as a record of real research into a different question — corrected in framing, not marked superseded or deleted. This PRD proceeds as the confirmed plan, not a provisional one |
| **Blocks?** | **No longer blocks anything.** V1 can proceed on this PRD without a pending product-direction decision |

### D2 — Who is the customer for the knowledge system?

| | |
|---|---|
| **Options** | **(A)** Internal-only tool; no customer; validate the mechanism and decide later. **(B)** Name a segment now and test it with discovery interviews. **(C)** Defer until after V1 |
| **Recommendation** | **(B), run in parallel with V0.** Five interviews cost a week. **(C) is how a project reaches month twelve with a working mechanism and no buyer** |
| **Consequences** | A: honest, and forecloses nothing, but produces no market evidence. B: costs a week and produces the first real customer evidence this direction has ever had |
| **Blocks?** | **Blocking for a business model. Not blocking for V0 or V1** |

### D3 — Where does the knowledge system run?

| | |
|---|---|
| **Question** | Local knowledge system / hosted knowledge system with a local collector / fully hosted |
| **Recommendation** | **Local knowledge system for V1.** Evidence: **FACT** — the named validation environment is local to a desktop, so a hosted knowledge system cannot reach it. **Consequence: the single-writer profile becomes the primary deployment, not a special case, and most contention machinery is dead weight.** A hosted knowledge system with a local collector adds an egress and a trust boundary that, **in a regulated domain, is a governance decision rather than a deployment detail** |
| **Consequences** | Local: massive scope reduction; multi-tenancy becomes irrelevant for V1. Hosted-with-collector: someone must decide what leaves the machine. Fully hosted: **requires sources that are hosted, which the portal is not** |
| **Blocks?** | **YES.** It constrains Q8, and Q8 constrains the build |

### D4 — Which Phase 1 schema?

| | |
|---|---|
| **Options** | **(A)** They scope different subsystems; both are right about their own subject. **(B)** One supersedes the other. **(C)** A merged schema |
| **Recommendation** | **(A) is the plausible reading and it is an INFERENCE, not a decision.** It needs ratifying or refuting in one page. **Do not build a schema before it is ratified** |
| **Blocks?** | **YES for any schema work** |

### D5 — Who owns the source-precedence policy?

| | |
|---|---|
| **Question** | A named human who ranks source classes on two axes and keeps it current |
| **Recommendation** | **Hold the meeting as V0.4 and time it.** *Expect it to surface genuine disagreement about how the organization works — that disagreement is the finding*, and it is better found in a meeting than in production. **If it cannot be resolved, write the disagreement down rather than defaulting it** |
| **Consequences** | Unowned: every precedence decision downstream is arbitrary. Owned badly: failure 16 in §13 — **and nothing detects a policy that is wrong** |
| **Blocks?** | **YES for V1** |

### D6 — Does the workflow change to produce the sources the knowledge system needs?

| | |
|---|---|
| **Question** | **FACT:** the observed workflow has no PRs, no CI and no issue tracker — the three highest-value sources in the design |
| **Options** | **(A)** Adopt PRs and CI first, then observe. **(B)** Observe only what exists — commits, committed documents, ADRs, handoffs. **(C)** Observe InOrbitX's tools instead, once Q3 is answered |
| **Recommendation** | **(B) for V0 and V1**, because it is available today and it contains the best test case in the project (§8.1). **Then (C).** (A) makes the validation environment less representative, not more, and it delays everything behind a process change |
| **Blocks?** | **No, but it decides what V1 can demonstrate** |

### D7 — Are the first consumers humans or agents?

| | |
|---|---|
| **Question** | V1's exit test (five real questions) is a **human** test. The strategic chain names **agents** as the consumer |
| **Recommendation** | **Humans first for V1; agents as a Stage 4 bet gated on Q19.** Evidence: coding agents already read the codebase, which is *the highest-authority source for implementation facts* — so the marginal value to an agent sits only in intent and history, which is narrow, and **has never been measured** |
| **Consequences** | Humans first: the exit test is already defined and achievable. Agents first: builds MCP and an integration before the ceiling has been measured |
| **Blocks?** | **No, but it decides what V1 optimises for** |

### D8 — Which invariants apply with one writer?

| | |
|---|---|
| **Question** | Which of the 39 runtime invariants apply when there is one writer, one process, and no contention |
| **Recommendation** | **Write the profile before line one of runtime code.** Half a day of reading. **Expect the answer to be well under ten.** **Do not delete the other half by default — deleting the wrong half loses the correctness properties that are the entire point** |
| **Blocks?** | **YES before any runtime code.** Not before V1's knowledge system work |

---

## 22. Architecture Implications

**This section runs product requirement → capability → architectural
implication. It never runs the other way.** An architecture component that
appears here without a product requirement to its left has no product reason to
exist yet, and §22.2 lists those.

### 22.1 Requirement → capability → architecture

| Product requirement | Required capability | Architectural implication |
|---|---|---|
| J1 — *"do intent and implementation agree?"* | Distinguish a decision from an observation from an executable assertion | **The claim must be kind-typed.** Undifferentiated "sources" make the disagreement disappear — this is the one architectural implication the whole product rests on |
| J1, FR-K4 | Make a disagreement collide rather than coexist | **Claim identity is `(subject, predicate)` in a scope; the object is excluded.** A contradiction becomes a key collision instead of two rows that both retrieve |
| J2 — *"what did we believe in June?"* | Answer as of a past instant | **Bitemporal validity on every claim from the first row.** Valid time and transaction time separated — **unrecoverable if deferred** |
| J3 — *"why, who, when, on what basis?"* | Follow any answer to its source months later | **Evidence as a joinable table of references with locators and digests, server-minted, outliving the run** |
| J3, FR-N1 | Improve extraction and apply it to history | **An append-only observation log as the system of record, with the rebuild invariant** |
| J4 — warn before acting | Refuse to act on disagreement | **Contradiction as a first-class record with severity** — a warning string cannot gate anything |
| J5 — *"tell me when you don't know"* | Distinguish absent from denied from unauthorized | **A denied read raises; results state what was not found and what could not be resolved** |
| J6 — agent context | Reach the knowledge system without importing it | **Tool projection curried with an explicit Principal.** Every access-control argument rests on it |
| J7 — *"why did it say that?"* | Separate *wrong claim* / *not retrieved* / *dropped for budget* | **A sampled retrieval record** — the only genuinely new durable record in the whole design |
| FR-P1 — audience safety | Know who could see a fact | **The permission label captured at ingest and propagated.** Knowable at ingest; **unknowable afterwards** |
| FR-K5, FR-O5 | One consistent write | **Claim + version + evidence + outbox event in one transaction** — and therefore **one store engine**, which is the decisive argument against a graph database |
| FR-R2 | Enforce permissions without collapsing recall | **The ACL predicate as a pre-filter inside the store.** ANN indexes post-filter, and under a high-selectivity predicate — which tenant always is — recall collapses |
| FR-V2 | Use model judgement safely | **A judgement may lower a verdict and never raise one**, enforced in code, not by prompting |
| FR-K9, Q5 | Make claim identity computable without embeddings | **A closed predicate schema registry** with `single_valued`, `kinds_allowed`, `object_schema`, `decay_profile`, `verifiable_by` |
| AC-1.2, §14.3 | Report a number that carries its error term | **A pinned store snapshot, paired comparison, per-slice gating, and a measured noise floor** |

### 22.2 Architecture with no V1 product requirement

**Stated so that every component has to earn its place.**

| Component | Product reason in V1? | Verdict |
|---|---|---|
| The world model (a projection) | **None.** Nothing in V1 needs a fast denormalised read | **Defer.** It is a cache; the delete test says so |
| Relationships table | **None.** Multi-hop questions are not in V1's jobs | **Defer** — a relationship is a claim |
| The verification probe loop | **Stage 3.** Valuable, and V1 has no claims old enough to be stale | **Defer, with a trigger** |
| MCP server | **None.** No consumer, no decided identity model | **Defer** (§11.4) |
| The Principal Agent | **None**, and four of its objects are blocked on organizational acts | **Blocked** |
| Leases, relay claims, sweepers, worker pools, per-tenant admission, budget ledgers | **None with one writer** | **Blocked on D8** — write the profile; do not delete by default |
| The evaluation harness | **Its instruments, yes** (noise floor, reviewed sample). The full harness, no | **Split: instruments in V1, harness later** |
| The effect ledger / undo | **None in V1** — the knowledge system observes and does not act | **Defer.** Required the moment anything acts on knowledge system context |
| Multi-tenancy machinery | **None.** One team is one permission domain | **Defer — but keep `tenant_id` in the key** |
| Embeddings, graph store, summarisation, curation | **None** | **Rejected with triggers** (§19) |

**This table is the answer to "is the architecture over-built?" — and the answer
is yes for V1, deliberately and recoverably, provided nothing in the left column
is built before its trigger fires.**

---

## 23. Traceability Matrix

**Every row runs left to right. A component with no row has no product reason to
exist yet.**

| Product requirement | User problem | Capability | Architecture component | Validation | Acceptance |
|---|---|---|---|---|---|
| FR-K1 Observation log | §3.5.4 — a decision nobody can trace | Follow any claim to its source | Observation log | Rebuild test in CI | AC-1.3 |
| FR-K2 Identity-keyed extraction | §13.10 — duplicate claims from redelivery | One extraction per observation | Extraction | Identity-replay test | AC-0.5, AC-1.5 |
| FR-K3, FR-K4 Kind-typed claim, identity | §3.2 — the disagreement is invisible | Type a statement by what it has authority over | Claim store | Contradiction test | AC-1.1 |
| FR-K5, FR-K6 Evidence in one transaction | §3.5 — an unsupported claim | Produce the basis for any answer | Evidence | Join test; unreachable-state constraint | AC-1.1 |
| FR-K7 Model proposes, never writes | §12.3 — unreviewed self-authored memory | Keep model output out of the store's authority | Proposal + classification | Import-boundary test | AC-1.9 |
| FR-K10 Deletion route | Regulated-domain precondition | Enumerate and delete | Persistence | Deletion-route test | AC-1.7 |
| FR-R1, FR-R2 Scope-first, pre-filtered | §13.4 — a leak with no error | Return only what the Principal may see | Retrieval | Tenant-isolation test | AC-1.6 |
| FR-R3 Denied reads raise | §12.8 — empty is indistinguishable from denied | Produce a signal on denial | Retrieval | Raise test | AC-1.6 |
| FR-R4 Three un-droppable items | §13.3 — a contradiction erased | Never answer confidently over contrary evidence | Context assembly | Minimal-budget test | AC-1.10 |
| FR-R6 Retrieval record | J7 | Separate three failures with different fixes | Retrieval record (sampled) | Walk W4 | §14.6 |
| FR-T1 Bitemporal validity | J2 | Answer as of a past date | Claim store | Schema test | AC-1.4 |
| FR-T3 `single_valued` declared | §13 — a contradiction recorded as an update | Decide supersession deterministically | Predicate registry | Classification test | AC-1.1 |
| FR-C1–C3 Contradiction register | J1, J4 | Surface disagreement and measure precision | Contradiction register | Raised-vs-confirmed ratio | §16.3 |
| FR-V2 Judgement may lower only | §12.7 — a model approving its own work | Use model judgement safely | Verification | Judgement-cannot-upgrade test | AC-1.8 |
| FR-V3 Corroboration from distinct runs | §12.2 — manufactured confidence | Earn standing | Claim lifecycle | Distinct-run test | AC-1.1 |
| FR-P1 Permission label at ingest | §13.4 | Know a fact's audience | Source adapters | Propagation test | AC-1.6 |
| FR-P3 Explicit Principal | §11.4 — MCP later without a refactor | One authorization path | Capability layer | Contract test | AC-1.9 |
| FR-A1 Tools only | §13.12 — acting on wrong context | Contain the agent | Tool projection | Import-boundary test | AC-1.9 |
| FR-A4 Sliced measurement | §16.1 — an aggregate hides the difference | Measure the consumer bet honestly | Evaluation instruments | Paired, per-slice, pinned | Stage 4 exit |
| FR-O1 Three day-one signals | §13.1, §13.2, §13.8 | See three whole failure classes | Signals | Exist before enrolment | AC-1.11 |
| FR-N1 Rebuild invariant | §13.13 | Improve extraction against history | Observation log | CI rebuild test | AC-1.3 |
| FR-N3 Never fail the caller | Availability | Degrade rather than break | Capability layer | Fault injection | §9.10 |
| FR-N4 No-context behaviour | Unspecified everywhere | Know what a step does with nothing | Capability layer | Per-capability review | §9.10 |

**Components appearing in no row: world model, relationships, MCP server,
Principal Agent, effect ledger, leases and the contention kernel, embeddings,
graph store, summarisation.** Each is either deferred with a trigger (§19) or
blocked (§21 D8).

---

## 24. Risks and Unknowns

### 24.1 Known (FACT — verifiable in this repository today)

- Zero product code. 47 commits, all documentation.
- Two documents specify incompatible Phase 1 schemas; neither acknowledges the other.
- The source-precedence policy does not exist, **four months after being identified as the blocking prerequisite.**
- No real question set has ever been collected.
- The observed workflow produces none of the three highest-value sources.
- The validation environment is local-only and cannot be read from a hosted session.
- Two codebases the knowledge system architecture is designed against are **not present and were not verified**.

### 24.2 Hypotheses (believed, untested)

T1–T7 in §2.2. **All seven.**

### 24.3 Unknowns (nobody has established these)

The customer · the deployment shape · the first source · the twenty predicates ·
the noise floor · the overlapping-permission model · contradiction severity
assignment · the entity merge/split lifecycle · InOrbitX's tools, team and data.

### 24.4 Risks, ranked by expected damage

| # | Risk | Why it ranks here | Mitigation |
|---|---|---|---|
| 1 | **A correct architecture, more of it, indefinitely** | **The highest-prior failure mode**, and the project's own PRD names it: *"building phase 1 beautifully, for four months, because it is the part that is fully specified and therefore the most comfortable to build"* | V0 has a one-week code timebox that is itself the measurement (Q21) |
| 2 | **The premise is wrong** — most questions are lookups | Terminal for the thesis. **Recorded as genuinely open in the project's own source material** | V0.1, one day, pre-registered threshold |
| 3 | **Extraction precision is too low** | A pincer with no escape: a high floor empties the store; a low floor makes the product a **confident liar**. **Systematic extraction errors correlate, so they corroborate each other** | V0.3, three days, pre-registered floor |
| 4 | **The source-precedence policy is an unpriced onboarding tax** | Gates time-to-first-value behind an internal political argument. **Discussed in every document as a design virtue and in none as a commercial risk** | V0.4, two hours, plus the post-hoc question |
| 5 | **The closed vocabulary does not scale** | **The only assumption whose failure has no designed escape** — the fallback is embeddings, and the corpus argues embeddings break under the selective permission predicate this workload always carries | Track the OOV curve from day one; it rides free on V0.3 |
| 6 | **A permission leak** | **No error, no log line.** In a regulated domain it is a governance incident, not a bug | Label at ingest; tenant in key; the isolation test is the only detector |
| 7 | **The consumer bet is empty** — agents do not benefit | The chain knowledge system → MCP → agents has no consumer; the knowledge system might still be valuable to humans, which is a different product with a different buyer | V0.2 measures the **ceiling** in three days, with no knowledge system |
| 8 | **Building for the wrong deployment shape** | Port it wholesale → complexity that buys nothing. Delete the wrong half → lose the correctness properties that are the point | D3 + D8, half a day each |
| 9 | **An incumbent ships "shows you when your sources disagree"** | They do not need the full correctness apparatus to capture the perceived value | Fetched competitive scan + five discovery interviews, one week |

### 24.5 Decisions required

D1–D8 in §21. **Five block. None is an engineering task, and none can be
unblocked by building.**

---

## 25. Final Product Definition

> **We are building a knowledge system** — a store of kind-typed claims,
> built over an append-only observation log, with evidence, authority and
> bitemporal validity on every claim, reachable only through a Principal-scoped
> capability layer —
>
> **for the engineers, and eventually the agents, working inside one
> engineering organization** —
>
> **so that a question whose answer spans sources that disagree is answered
> with what is true, what was decided, when each was established, on what
> basis, and where they conflict — or with an honest "I do not know."**

### The first shippable version

**V1: one source, end to end.** An observation log with time, provenance and
permission captured at ingest; identity-keyed extraction against a closed
twenty-predicate vocabulary; a claim store with versions, joinable evidence and
bitemporal validity; deterministic classification and reconciliation against an
authored source-precedence policy; a contradiction register; scope-first retrieval
behind an explicit Principal; context assembly that never drops contradictions,
provenance or temporal qualifiers; a tested deletion route; three signals; and
three capabilities — **`why`, `entity`, `conflicts`.**

**It is done when five real questions from real history are each answered with
the implementation fact, the decision, the author, the date, and the gap between
intent and reality stated plainly — and extraction precision has been
measured.**

### The first thing we produce

**V0, which ships no software.** Four measurements and one 30-line primitive,
two weeks. **Its output is not a product. It is the evidence that decides
whether V1 should be built at all** — and, on current evidence, that decision
has never been informed by anything but an argument.

---

## 26. Questions Claude Refuses to Guess

**Every item below is a product decision this repository does not contain enough
evidence to make. Each names what evidence would settle it.**

| # | Question | What would settle it | Why guessing is worse than leaving it open |
|---|---|---|---|
| 1 | **Who is the customer for the knowledge system?** | Five discovery interviews; or a named segment with a stated reason | A fabricated persona propagates into scope, pricing, and every prioritisation decision downstream — and it is unfalsifiable because it came from nowhere |
| 2 | ~~Is Direction A or Direction B the product?~~ **RESOLVED 2026-09-14** | [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) | There was no contest to pick a side of — `prd.md` was exploratory |
| 3 | **What share of real questions are why / temporal / contradiction?** | 50 real questions, classified, threshold pre-registered | **Any number I wrote here would be invented**, and it is the number the entire thesis turns on |
| 4 | **What extraction precision is achievable on real organizational text?** | 200 reviewed observations | The corroboration floor, the confidence model and the product's economics all depend on it. A guess sets a threshold that fits noise |
| 5 | **What are the twenty predicates?** | The real questions from item 3 | A vocabulary derived from a taxonomy rather than from questions is the failure the design explicitly warns against |
| 6 | **Which source is ingested first?** | An inventory of InOrbitX's actual tools (Q3) | **It is a fact about the organization, not about the architecture.** Guessing picks a source that may not exist |
| 7 | **Where does the knowledge system run — local, hybrid, or hosted?** | A decision, informed by what InOrbitX actually is | These are materially different systems. Guessing builds half of the wrong one |
| 8 | **Who owns the source-precedence policy, and what is in it?** | A meeting with named people | **It cannot be inferred by design.** An inferred policy is wrong precisely where it matters, and wrong invisibly |
| 9 | **How are overlapping, non-partitioned audiences modelled?** | Enumerate the real audiences in the target environment, then design against those | Designing in the abstract produces a model that fits no real organization — **and the failure it guards against produces no error** |
| 10 | **What makes a contradiction blocking rather than advisory?** | Run advisory-only; measure which contradictions a human says *should* have blocked | Too liberal blocks everything in a busy scope; too conservative never fires. **No principle picks between them without data** |
| 11 | **What are the confidence floor, retire floor and decay half-life?** | The measured noise floor | **No consulted source gives a starting value.** A number written now is fitting to noise |
| 12 | **Is the pain acute enough to fund a company?** | Five discovery interviews, unprompted incidents | This is the only question on this list that no amount of engineering can answer |
| 13 | **What does a step do when the knowledge system returns nothing?** | A per-capability decision | *"The read path never fails a step"* does not say what the step then does, and the right answer differs per capability |
| 14 | ~~Does `prd.md`'s Change 3 argument apply to a knowledge system?~~ **MOOT 2026-09-14** | [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) | Change 3 was never a decision against this direction — it was never proposed as competing with it |

---

## Appendix A — Self-review

Performed against the eight checks required of this document. Each answer that
was "yes" was fixed before this draft was finished.

| # | Check | Answer | What was changed |
|---|---|---|---|
| 1 | Did I turn architecture into product scope? | **Was yes, now no** | §22.2 and §23 were added specifically to force every component to justify itself. Nine components now appear in **no** traceability row and are explicitly deferred or blocked. **§7.4 was added on the second pass**, because listing V1's contents with a justification per row is not the same as asking whether V1 could be smaller — it cuts entity *resolution* from V1 and marks the contradiction table as undecided |
| 2 | Did I assume unvalidated market demand? | **No** | §4.2 states the customer is **not identified**; §17.4 states market validation has never been performed; §26 refuses to name a segment |
| 3 | Did I confuse planned with implemented? | **No** | §0.3 states the code inventory once, verified at a named commit. Every requirement in §9 describes something to be built |
| 4 | Did I resolve an open question without evidence? | **No** | Q7 (§11.3, D4) and Q3 (D3) are each recorded as unresolved. **D3 carries a recommendation explicitly labelled as such, not a decision.** Q1 (§0.1, D1) *is* now recorded as resolved — but on the strength of a direct statement from the project owner, not an inference, which is the evidence class this document requires before treating anything as settled |
| 5 | Did I include capabilities not needed for the MVP? | **Was yes, now no** | The world model, relationships, the probe loop, MCP, the Principal Agent, the effect ledger and the contention kernel were moved out of V1 into §7.3 and §22.2, each with a trigger. **§7.4 then examined the three remaining candidates inside V1** and cut one of them. What survives is the set whose omission is *unrecoverable*, not merely expensive |
| 6 | Does every MVP capability have a clear user problem? | **Yes** | Every §9 requirement carries a "user value" column, and §23 traces each to a problem in §3 or a job in §5 |
| 7 | Can the MVP falsify the thesis? | **Yes — and V0 falsifies it more cheaply than V1** | V0.1 can falsify the premise in one day; V0.2 can measure the ceiling of the whole chain in three. V1's AC-1.1 fails visibly if reconciliation answers cannot be produced |
| 8 | Are the acceptance criteria measurable? | **Yes** | Every criterion in §15 is a test, a count, or a pre-registered threshold. Where a target is unknown it is marked **TBD** rather than invented (§10) |

**One check this document adds to the eight:** *did I invent any number?* The
only numeric thresholds here — **25%** for question mix and **~85%** for
extraction precision — are **pre-registered proposals carried from
`14-outside-in-review-2026-09-14.md`, labelled as such, and explicitly open to
being set differently before the experiment runs.** Every other target is TBD.

---

## Appendix B — Where this PRD disagrees with existing documents

**Recorded rather than resolved, per the discipline in `PROJECT_BOOTSTRAP.md`
§0. None of these changes any existing document.**

| # | Disagreement | This PRD's position |
|---|---|---|
| 1 | The strategic chain places the **Agent Runtime** on the critical path; the knowledge system architecture says *"The knowledge system does not need the fifty-chapter runtime to exist."* **No document reconciles them** | §9.8 and §22.2 adopt the knowledge system architecture's position for V1: four primitives, each with its own trigger. **D8 must be written before any runtime code** |
| 2 | The strategic chain names **agents** as the consumer; V1's exit test is a **human** test | §21 D7 recommends humans first, agents as a Stage 4 bet gated on Q19 — **and does not resolve it** |
| 3 | The cancellation example is treated across several documents as the problem statement | §3.2 labels it **ILLUSTRATIVE** — an example written by an architect, **not a collected incident.** It is a good illustration and it is not evidence |
| 4 | `06-validation-strategy.md` proposes the engineering workflow as the first environment | §17.1 keeps it **and** adds D6, because **FACT:** that workflow produces none of the three sources the design values most, so adopting it implies a workflow change that should be decided rather than drifted into |
| 5 | No document treats the source-precedence policy as a commercial risk | §13 failure 16 and §24.4 risk 4 treat it as one. **The design virtue and the onboarding tax are the same property seen from two sides** |
| 6 | The build order's Stage 0 exits on documentation | §18 keeps the build order's own Change 2 — Stage 0 exits on **decisions**, and adds V0's four measurements in front of everything |

---

## Appendix C — Source map

Every substantive claim in this PRD traces to one of these.

| Source | Used for |
|---|---|
| `PROJECT_BOOTSTRAP.md` | Status labels, the code inventory, the blocking questions |
| `docs/project/00-north-star.md` | The thesis, the cancellation example, what is not the product, the falsifiers |
| `docs/project/01-architecture-map.md` | §11 boundaries, component invariants, §22 implications |
| `docs/project/02-domain-model.md` | Claim fields and identity, evidence, the schema dispute |
| `docs/project/03-lifecycles-and-state-machines.md` | Claim and contradiction lifecycles, standing, decay exclusions |
| `docs/project/04-implementation-map.md` | The implementation inventory and the test list |
| `docs/project/05-development-workflow.md` | §3.1, and the PR/CI/tracker gap behind D6 |
| `docs/project/06-validation-strategy.md` | §17, the five-question test, the deployment-shape constraint behind D3 |
| `docs/project/07-brain-observability.md` | §13, §14, the retrieval record, the four instruments |
| `docs/project/08-build-order.md` | §18, the stage exits, the do-not-build triggers |
| `docs/project/09-do-not-assume.md` | §12.8, and the labelling discipline throughout |
| `docs/project/10-open-questions.md` | §20, §21, §24.3 |
| `docs/project/13-audit-2026-09-14.md` | The over-built / under-designed assessments in §22.2 |
| `docs/project/14-outside-in-review-2026-09-14.md` | §2.2 (T1–T7), §7.1 (V0), §24.4, the two pre-registered thresholds |
| `docs/project/decisions/` (24 ADRs) | Every "why" in §12, §19 and §22 |
| `prd.md`, `docs/product/01`–`06` | The runtime-controls-OS exploration, the rejected segment (as a market observation, §4.2), the external evidence in §3.3 |
| [ADR-0025](decisions/ADR-0025-no-external-codebase-is-evidence.md), [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) | The 2026-09-14 corrections referenced throughout §0, §4.2, §20, §21 D1, §26 |
