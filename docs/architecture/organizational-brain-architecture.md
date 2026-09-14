# The Organizational Brain — Architecture

**Status:** **DESIGNED.** Nothing described here has been built or run.

**What this document is.** The architectural reasoning behind the
Organizational Brain: what organizational knowledge is actually like, what this
design therefore requires, the principles that decide later arguments, and an
honest ledger of what is and is not established.

**What it is not.** It is not the detailed component specification. That lives
in `docs/project/` — `01-architecture-map.md` (every component, its purpose,
what it owns and does not own, its invariants), `02-domain-model.md` (every
object and field), `03-lifecycles-and-state-machines.md`,
`07-brain-observability.md`. This document states *why*; those state *what*.

---

## 0. Sources

| Source | What it contributed |
|---|---|
| The 51-chapter agent-runtime handbook (`docs/handbook/`) | The six-layer model, the narrow waist, effect tiers, state categories. **A specification, not an implementation** |
| Universal Runtime v1.0 specification (`docs/architecture/`) | The execution model and 39 invariants |
| Memory Management Architecture (`learning-notes/`) | The memory write path, the routing rule, bitemporal validity, the pre-filter argument |
| Principal Agent Architecture (`learning-notes/`) | Decisions, outcomes, sealed predictions |
| Public market research | `docs/product/07-organizational-knowledge-landscape.md` |
| **This project's own code** | **None exists.** Zero product source files have ever been written |

**The last row is the one that matters.** Every architectural claim below is
reasoning, not observation. See §7.

---

## 1. What exists, and what does not

Three things are often conflated when discussing this project. They are
different in kind, and the difference decides which one can be built on.

| | What it is | Status |
|---|---|---|
| **The handbook** | The constitution. It says what must be true | **A specification. Not implemented.** It is not something to build *on*, because there is nothing there to build on |
| **The specification** | The execution model, named and numbered | **Designed.** Same condition |
| **This project** | The Organizational Brain | **0 lines of product code** |

That the handbook and the specification describe overlapping concepts under
different names, with no stated relationship between them, is the origin of
open question **Q4** and
[ADR-0002](../project/decisions/ADR-0002-specification-vocabulary-is-canonical-for-code.md).
Two constitutions with no stated relationship means every architectural
argument can be won by citing the other one.

---

## 2. What organizational knowledge is like

**[INFERENCE]** Eight properties. They are not observations of any running
system — they are claims about organizations, and each one kills a design that
would otherwise be reasonable. Together they are most of the design work.

| # | Property | What it rules out |
|---|---|---|
| 1 | **Observations arrive continuously and unbounded** | Build-time indexing over a fixed, curated corpus. Continuous ingestion is the single largest structural consequence |
| 2 | **No general organization publishes its own precedence rule** | Reading authority out of the corpus. There is no sentence anywhere in a company saying a signed agreement beats an SOP beats a product guide beats a deprecated policy. **This is the hardest problem here — see §3** |
| 3 | **Extraction must be verified, not trusted** | Hand-reviewing everything once. Review does not scale past a small curated set, but the principle has to survive in another form |
| 4 | **Conflict is between a decision, an implementation and an observation** — three different kinds of thing | A two-sided conflict model. Typing everything identically makes the disagreement disappear |
| 5 | **A live Brain has a moving *now*** | One global frozen `as_of`. A run must still see a stable world, so stability moves to per-run |
| 6 | **Evidence must outlive the run** | Run-scoped ephemeral evidence. A claim's basis must be inspectable months later |
| 7 | **Organizational knowledge is not partitioned** — it is overlapping, per-source, and often per-channel | A single tenant predicate as the whole access model. Private channels, restricted repositories and HR data do not nest |
| 8 | **An unaddressed agent should usually stay silent** | Volunteering by default. This constraint should be kept far longer than will feel comfortable |

Property 7 is the most under-designed area in the project (**Q10**), and
property 2 is the blocking one (**Q2**).

---

## 3. The authority problem

**The hardest thing in this design, and it is not an engineering problem.**

Deterministic precedence requires a well-founded ordering over source classes.
That ordering comes from exactly one of three places:

1. **Published inside the corpus being read.** This is the special case. It
   holds for corpora that are themselves regulatory or contractual, where the
   documents state their own precedence. Insurance is plausibly such a domain —
   policy wording, endorsements, broker notes and regulatory guidance have real
   documented authority relationships. **It does not supply an ordering for
   engineering claims**, which is what a first source would produce.
2. **Authored outside it**, by a named human.
3. **Inferred** from recency, author seniority, or how confidently something
   was written.

Case (3) is rejected: authority inferred that way is **wrong in exactly the
cases that matter, and wrong invisibly**. Case (1) does not generalise.
Therefore (2).

**The design consequence, which shapes everything downstream:** the
source-class ladder is **configuration** — authored by a human, versioned,
reviewed, and outside anything the agent may edit. **The Brain enforces a
ladder. It does not learn one.** See
[ADR-0006](../project/decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md).

**It does not exist.** No ladder has been authored, and nothing downstream —
precedence, contradiction, retrieval ranking — means anything without one.
This is **Q2**, and it needs a meeting, not a sprint.

---

## 4. What this design requires that does not exist

Nine primitives. Every one has to be built.

| Primitive | Why it is required | Where it is specified |
|---|---|---|
| **Durable, cross-run evidence** | A claim must cite its basis months later, not just within the answer that produced it | §8.4 — the handle discipline, with a lifetime that outlives the run |
| **A source-class ladder as authored configuration** | §3 above | A human, once, then versioned |
| **Continuous observation ingestion with admission control** | Observations arrive forever and most are worthless. **Admission is the stage everyone omits** | `01-architecture-map.md` §2.3 |
| **Entity resolution** | "Carrier X", "the QIC flow" and a service name in a repository must resolve to one identity across chat, tickets, code and meetings | **The component most likely to be underestimated.** `01-architecture-map.md` §2.4 |
| **Relationship traversal** | *"Why does QIC approval behave differently for carrier X"* is multi-hop | Where a graph store would be argued for — and refused, see [ADR-0009](../project/decisions/ADR-0009-no-graph-database.md) |
| **A moving *now*, with per-run stability** | A live Brain cannot freeze time globally; a run must still see a stable world | [ADR-0023](../project/decisions/ADR-0023-bitemporal-validity-on-claims.md) |
| **Non-partitioned permissions** | Property 7 of §2. **The leak produces no error and no log line** | **Not designed. Q10** |
| **A participation policy** | Nothing decides when an unaddressed agent should speak | `08-build-order.md` stage 5 |
| **Decision, Implementation and Outcome as distinct kinds** | This is what makes *"product says X, code does Y"* expressible at all | [ADR-0003](../project/decisions/ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md) |

---

## 5. Design principles

Twelve. Each decides a later argument, and each names what it protects — a
principle that protects nothing is a preference.

| # | Principle | What it means concretely | Where the argument is made |
|---|---|---|---|
| 1 | **Authority is data, not prose — authored, not inferred** | The ordering over source classes is a versioned configuration file with a named human owner, enforced by a deterministic query | §3 · [ADR-0006](../project/decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md) · `[DESIGN DECISION]` |
| 2 | **The model proposes; code decides** | Exactly one non-deterministic step. A model output may never become an authority, an ordering, or a success verdict | [ADR-0010](../project/decisions/ADR-0010-the-model-proposes-and-never-writes.md) · `[DESIGN DECISION]` |
| 3 | **A claim carries its kind, and the kind bounds what it can answer** | A decision has authority over intent and none over reality; an observation the reverse | Derived from the cancellation example, `00-north-star.md` §2 · `[DESIGN DECISION]` |
| 4 | **Contradiction is an object, not a caveat** | It is stored, has severity and an owner, and can block an action rather than decorate an answer | `01-architecture-map.md` §2.9 · `[DESIGN DECISION]` |
| 5 | **Restraint over recall** | A store that knows forty things with evidence and says "I do not know" to everything else is more useful than one that knows four hundred of which eighty are wrong | A *false* contradiction is worse than a missed one: it drives every claim in a busy scope below the load floor while looking healthy. `07-brain-observability.md` §5 · `[DESIGN DECISION]` |
| 6 | **Nothing becomes ACTIVE on one observation** | Standing is earned by corroboration from distinct runs | [ADR-0011](../project/decisions/ADR-0011-standing-is-earned-by-independent-corroboration.md) · Handbook Ch 12 §5.4 |
| 7 | **Retrieved knowledge is evidence presented to the model, not authority granted to it** | Context is input, not instruction | Handbook Ch 6 §5.3 · Memory Management Architecture §20 |
| 8 | **Permissions live in the store, not at the call site** | The ACL predicate is a pre-filter inside the store implementation | Handbook Ch 37 §5.2 · Memory Management Architecture §16.4 · [ADR-0016](../project/decisions/ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md) |
| 9 | **There is no "now" — there are two clocks and a per-run as-of** | Valid time and transaction time are separate; the clock is a port | [ADR-0023](../project/decisions/ADR-0023-bitemporal-validity-on-claims.md) · Memory Management Architecture |
| 10 | **Admission before extraction** | Most observations are discarded, and the discard rate is a headline metric | `01-architecture-map.md` §2.3 · `[DESIGN DECISION]` |
| 11 | **The Brain proposes; it does not write to the world** | It can assert, flag a contradiction, and draft an action. Executing goes through a separate gate | [ADR-0010](../project/decisions/ADR-0010-the-model-proposes-and-never-writes.md) · `[DESIGN DECISION]` |
| 12 | **Silence is the default, and speaking is earned per rung** | Observing, retrieving, answering-when-asked, volunteering and acting are five permissions with five gates | `08-build-order.md` stage 5 · `[DESIGN DECISION]` |

### 5.1 The two most likely to be abandoned under pressure

**Principle 1 will be attacked first.** Somebody will observe that maintaining
an authority configuration is tedious and that a model could infer which source
is more trustworthy. It would be right most of the time. **It would be wrong
specifically when a junior person states something confidently and recently,
when a draft is more fluent than the signed version, and when a deprecated
policy is the most frequently cited document in the corpus** — which is to say,
wrong in every case where the mechanism was supposed to earn its keep.

**Principle 12 will be attacked second**, because a system that could have
warned you and stayed silent feels like a wasted capability. The counter is
measured, not philosophical: a few bad unprompted interventions and the
capability is muted permanently, regardless of later quality.

---

## 6. Mechanisms this design requires

**[DESIGN DECISION]** These are build requirements, not descriptions of
anything that runs. Each is load-bearing, and each has its argument stated in
`09-do-not-assume.md` §11.

| Mechanism | What breaks without it |
|---|---|
| **A Principal with a signed session token and a scope set** | Every authorization decision loses its subject |
| **Tool projection, curried with the Principal at build time** | An unauthorised query becomes a runtime check instead of being *absent from the schema*. Every containment argument rests on this |
| **The ACL predicate injected inside the store implementation** | Pre-filter becomes post-filter. Recall collapses under a selective predicate, and leaks stop producing signals |
| **Frozen-clock discipline — `as_of()` versus `wall_now()`, CI-enforced** | Temporal correctness. Widen the allowlist per module with a comment; never relax the test |
| **Server-minted, kind-checked evidence handles with a `derived_from` chain** | A caller-supplied id **is the whole attack** |
| **Deterministic precedence over a typed table** | Resolution becomes a model judgement, which is principle 1 lost |
| **Contradiction as a handle that gates action** | It becomes a warning string, which decorates rather than prevents |
| **A grounding gate with bounded repair** | Citations become decorative and unverifiable |
| **Hybrid retrieval — lexical plus structural, with reciprocal rank fusion** | Scope-first retrieval has no ranking story when scopes are large |

**Two mechanisms are deliberately excluded.** Event replay from a sequence
number is already specified independently by the handbook's
hydrate-then-subscribe contract. Embedding-collection namespacing is dead
weight while [ADR-0008](../project/decisions/ADR-0008-no-embeddings-in-phase-1.md)
holds.

---

## 7. Four anti-patterns

Each is a reasonable design that is **wrong here**, for a stated reason.

| Anti-pattern | Why it is wrong here |
|---|---|
| **Build-time-only indexing** | Observations arrive forever. An index built once describes a moment that has already passed |
| **A single global frozen `as_of`** | A live Brain has a moving now. Freezing globally makes every concurrent run share one stale world |
| **Run-scoped, ephemeral evidence** | A claim's basis must be inspectable months later. Evidence that dies with the run makes every old claim unauditable |
| **A single account identifier as the whole ACL universe** | Organizational audiences overlap and do not nest. One predicate cannot express a private channel, a restricted repository and an HR document |

---

## 7a. The relationship to the agent runtime

**[INFERENCE]** **This design does not need the fifty-chapter runtime to
exist.** Four of that runtime's primitives would each remove a real weakness,
and knowing which and when is worth stating rather than treating the handbook
as either mandatory or irrelevant.

| Runtime primitive | Weakness it removes | When it becomes worth adopting |
|---|---|---|
| **Identity-keyed extraction** | Extraction is a non-deterministic model call that costs money. Without an identity-keyed ledger, a redelivery re-extracts and produces a **different** claim from the same text — so the duplicate is not recognisable as one afterwards | **First. As soon as ingestion is continuous rather than batch** |
| **Transactional outbox** | A claim write and its notification are two writes with a gap in which one can exist without the other. Invisible at low volume; a real inconsistency source once anything reacts to events | When the first consumer reacts to an event — the participation check is exactly that consumer |
| **Leases and version-CAS** | Two workers on one observation, or two updates to one claim, relying on database default behaviour rather than an explicit guard | When ingestion runs more than one worker. **Before that it is theatre** |
| **Park** | A claim awaiting human confirmation has nowhere to wait that holds no resources | When human confirmation enters the claim lifecycle |

**The one to adopt first is identity-keyed extraction**: a deterministic id
from `(observation_id, extractor_version)`, made a UNIQUE key, and claimed
**before** the model call rather than after. **Retry is not replay.** It is
roughly twenty lines, it is the cheapest correctness win available, and it is
the one primitive that does not retrofit — everything else can be added later;
identity cannot.

**This contradicts any plan that places the whole runtime on the critical
path.** The contradiction is real and recorded — see `10-open-questions.md`
**Q20** and `14-outside-in-review-2026-09-14.md` A6.

---

## 8. What is and is not established

**This is the project's canonical evidence statement.** Other documents should
point here rather than write their own.

| | |
|---|---|
| **ESTABLISHED by implementation** | **Nothing.** No mechanism in this document has been built or run. There is no prior implementation, no head start, and no component that can be assumed to work because something like it worked before |
| **ESTABLISHED from the market** | Nobody appears to combine authority, kind-typed claims, bitemporal validity and contradiction-as-an-object. **This is an argument from absence in public material and it is the weakest claim in the corpus.** `docs/product/07-organizational-knowledge-landscape.md` §6 |
| **NOT ESTABLISHED** | That any of this holds at organizational scale with messy input. **Nothing has been tried at any scale.** Entity fragmentation, admission and vocabulary growth appear together the first time continuous unstructured observation is ingested, and no observation has ever been ingested |
| **NOT ESTABLISHED — and the one most worth testing early** | **That extraction precision is high enough for the store to be worth trusting.** Everything downstream assumes it. A reviewed sample is the cheapest way to find out, and it should exist in Phase 1 rather than when something goes wrong |

**No effort, size or difficulty estimate in this project has a basis.** Phase 1
has not been estimated, and any number offered for it would be invented.

---

## 9. Unsolved — and not by this design

Stated so nobody spends a sprint rediscovering them. **These are not tasks.**

| Problem | Position |
|---|---|
| **Noticing a claim is wrong when nothing new has been observed about it** | **STRUCTURALLY UNSOLVED.** Every mechanism here is reactive — corroboration, contradiction, decay, invalidation. The verification loop is the only proactive one and it covers only probe-verifiable predicates, which will be a minority. The runtime cannot feel doubt, so doubt has to be manufactured — and manufacturing it for a social fact is not something anyone has solved |
| **Self-confirmation through the world** | **PARTIALLY SOLVED.** In-system defences close the loop internally. They do not stop the agent asserting something, a human internalising it, and that human later stating it as their own belief — a genuine observation from a genuine actor, **indistinguishable from independent corroboration** |
| **Causation from organizational outcomes** | **UNSOLVED**, and acknowledged as such. A decision with a sealed prediction and a measured outcome gives the cleanest evidence available at n=1 and **gives no causation**. The mechanism check — did the predicted mechanism actually move — is the only instrument that works, and only because it was written down before the result |
| **Knowing what the organization does NOT know** | **UNSOLVED and barely explored.** "I have no claims about X" conflates *nobody has said anything*, *this does not exist*, and *I cannot see it*. Three very different answers, and the third is a permission fact the asker may not be allowed to learn |
| **Whether any of this beats a good search box for most questions** | **GENUINELY OPEN, and worth saying plainly.** Most questions are lookups where retrieval quality is the whole game. The advantage appears on *why* questions, *temporal* questions and *contradictions* — the valuable minority. **An aggregate quality score will be dominated by lookups and will not show the difference** |

---

## 10. Where the rest of the design lives

| Question | Document |
|---|---|
| Every component: purpose, owns, does not own, invariants, status | `docs/project/01-architecture-map.md` |
| Every object and field | `docs/project/02-domain-model.md` |
| State machines and transitions | `docs/project/03-lifecycles-and-state-machines.md` |
| How correctness is established without asking the Brain | `docs/project/07-brain-observability.md` |
| The staged build order and its exit measurements | `docs/project/08-build-order.md` |
| Open questions, blocking status, next experiment | `docs/project/10-open-questions.md` |
| The product requirements | `docs/project/PRD.md` |
| Competitive landscape | `docs/product/07-organizational-knowledge-landscape.md` |
