# Open Questions Register

**Unknowns are first-class project state.** A question recorded here is a
finding, not an embarrassment. A question resolved here moves to
`decisions/` as an ADR and to `11-architecture-change-log.md` as an entry.

**Last reviewed:** 2026-09-14.

Each entry carries: why it matters, current hypotheses, evidence available,
what decision is required, whether it blocks, and the next experiment.

---

## 1. Blocking — nothing meaningful proceeds until these are decided

### Q2 — Who authors the source-class authority ladder, and who may change it?

| | |
|---|---|
| **Why it matters** | Every downstream mechanism — precedence, contradiction, retrieval ranking — is **meaningless** without it. And it cannot be inferred: authority inferred from recency, seniority or confident phrasing is wrong precisely in the cases that matter, and **wrong invisibly** |
| **Hypotheses** | None competing. The decision is *settled* ([ADR-0006](decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md)); the **execution** has not happened |
| **Evidence available** | **None. The requirement is derived from the structure of the problem, not observed.** A general organization publishes no precedence rule — no sentence anywhere says a signed agreement beats an SOP beats a product guide. The ordering must therefore be authored |
| **Decision required** | A named human, a meeting, and a versioned file. Rank source classes on **two axes** — authority over intent, and authority over reality |
| **Blocking?** | **YES.** Phase 1 is meaningless without it |
| **Next experiment** | Hold the meeting. **Expect it to surface genuine disagreement about how the organization works — that disagreement is the finding**, and it is better discovered in a meeting than in production. If it cannot be resolved, write the disagreement down as an open question rather than defaulting it |

---

### Q3 — What is InOrbitX? *(partially established 2026-09-14)*

| | |
|---|---|
| **Why it matters** | It is named as the first live validation environment. The validation strategy depends on knowing what it is, which systems it uses, and what observations it emits |
| **What IS now established** | **InOrbitX is a broker insurance portal.** It is a project held **locally on the owner's desktop.** Stated by the project owner, 2026-09-14 |
| **What is STILL unknown** | Tech stack. Team size and composition. Which tools produce observations — Git host, issue tracker, chat, CI. Whether it uses pull requests. Where decisions are actually recorded. Whether it has users in production or is pre-launch. What data it holds |
| **The accessibility constraint** | **It is on a local desktop, so this session cannot read it** — reported, not verifiable from here. Any first source the Brain ingests must be something reachable from wherever the Brain runs — a local-only repository is reachable by a local agent and not by a hosted one. **This is a deployment constraint the architecture has not addressed** |
| **Decision required** | Write down: which systems, which teams, where decisions live, what emits observations, and where the Brain would run relative to them |
| **Blocking?** | **Still YES** for the validation strategy. The domain is now known; the observable surface is not |
| **Next experiment** | Step V0 in `06-validation-strategy.md` §6 — now a narrower writing task: inventory the tools around an existing project rather than define an unknown environment |

**[INFERENCE — flagged, not established]** A regulated domain changes two things
in the architecture's favour and one against:

- **In favour:** insurance has **published precedence structure.** Policy
  wording, endorsements, broker notes, underwriting guidance and regulatory
  guidance have real, documented authority relationships. That is closer to the
  case where a corpus contained its own precedence rule than to a generic
  organization, and it may make Q2's ladder meeting substantially easier for
  *domain* claims. It does **not** supply a ladder for *engineering* claims,
  which is what the Brain's first source would produce.
- **Also in favour:** it gives the "reconciliation across sources that disagree"
  thesis a natural high-value case — intent versus implementation matters more
  when a mismatch has regulatory consequences.
- **Against:** customer PII and confidentiality boundaries are real from day
  one. The tenancy, redaction, deletion-route and overlapping-permission
  machinery ([ADR-0016](decisions/ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md),
  [ADR-0017](decisions/ADR-0017-deletion-route-before-retirement.md), **Q10**)
  stops being premature and becomes a precondition. **Q10 — overlapping,
  non-partitioned permissions — is the project's most under-designed area and it
  now has a concrete reason to be solved before, not after, the first non-public
  source.**

None of the above is established. It is reasoning from the domain name, and it
needs confirming against the actual project.

---

### Q4 — Is the handbook or the specification normative for new code?

| | |
|---|---|
| **Why it matters** | Two constitutions with no stated relationship means *every architectural argument can be won by citing the other one.* And starting to code before choosing guarantees rework |
| **Hypotheses** | **(A)** Specification canonical for code, handbook for principles — assumed by two documents, ratified by nobody. ~~**(B)** An existing codebase canonical for code~~ — **withdrawn 2026-09-14, no such codebase informs this project** ([ADR-0025](decisions/ADR-0025-no-external-codebase-is-evidence.md)). Lettering kept so existing references to option (C) still resolve. **(C)** Reconcile into one vocabulary — most correct, most expensive |
| **Evidence available** | Recorded as Finding A in the product research and again in the architecture. Both flag it; neither resolves it |
| **Decision required** | One paragraph, written down |
| **Blocking?** | **YES** for implementation. It decides what a module is called |
| **Next experiment** | None needed. This is a decision, not an experiment |

See [ADR-0002](decisions/ADR-0002-specification-vocabulary-is-canonical-for-code.md).

---

### Q5 — What is the initial predicate vocabulary?

| | |
|---|---|
| **Why it matters** | The predicate registry is the hinge: claim identity is `(subject, predicate)` in a scope. **Too broad is as bad as too narrow** — two hundred predicates means nothing ever collides, so nothing ever contradicts |
| **Hypotheses** | Roughly **twenty**, drawn from real questions people actually ask — not from a taxonomy. Candidate starting set: ownership, dependency, current_behaviour, intended_behaviour, process, term, constraint |
| **Evidence available** | The recommended size and derivation method. **The real questions have not been collected** |
| **Decision required** | Twenty predicates, each with `single_valued`, `kinds_allowed`, `object_schema`, `decay_profile`, `verifiable_by` |
| **Blocking?** | **YES** for extraction |
| **Next experiment** | Collect twenty to fifty real questions from actual history first (step V1). **Derive the vocabulary from them.** Then let the out-of-vocabulary rejection rate drive additions |

---

### Q6 — Which single source is ingested first?

| | |
|---|---|
| **Why it matters** | Starting with the wrong source means hitting entity resolution, admission and vocabulary growth simultaneously |
| **Hypotheses** | **Jira or Git.** Both have real identifiers, timestamps, authors, and high claim density. Meetings second. **Slack last.** Documentation is a trap — staleness is worst there, so a Brain built on docs first learns a stale world confidently and has nothing to contradict it with |
| **Evidence available** | A ranked table in the Brain architecture |
| **Decision required** | Pick one. **It depends on where this organization's decisions actually live** — which is a fact about the organization, not about the architecture |
| **Blocking?** | **YES** for Phase 1 |
| **Next experiment** | Answer Q3 first; the answer probably falls out of it |

---

## 2. Hard — decide before Phase 2

### Q7 — How do the Memory and Brain schemas reconcile?

| | |
|---|---|
| **Why it matters** | Two documents specify **incompatible Phase 1 schemas** and neither acknowledges the other. Building either without reconciling means discovering it at integration |
| **Hypotheses** | **(A)** Different scopes — Memory covers a runtime memory subsystem where entities arrive already identified; Brain covers an organizational store where identity must be established. Both right about their own subject. **(B)** One supersedes the other. **(C)** A merged schema |
| **Evidence available** | Both documents, side by side in `02-domain-model.md` §5. **Hypothesis A is an inference from each document's scope, not a stated claim in either.** The observation that they use identical words — `claims`, `evidence`, "Phase 1" — for different things is itself the strongest support for A |
| **Decision required** | Which schema is built, for which subsystem, and whether they are one store or two |
| **Blocking?** | **YES** for any schema work. Not for the decisions above it |
| **Next experiment** | Read both §37 (Memory ADRs) and §17.3 (Brain build list) together and write one page reconciling them. **A is an inference; it needs ratifying or refuting** |

---

### Q8 — Which of the 39 invariants apply with one writer and no contention?

| | |
|---|---|
| **Why it matters** | Roughly half the specified kernel exists to arbitrate contention that does not exist in a single-writer deployment. **Porting it wholesale produces complexity that buys nothing; deleting the wrong half loses the correctness properties that are the entire point** |
| **Hypotheses** | Leases, version-CAS, relay claims, sweepers, worker pools, per-tenant admission and budget ledgers are candidates to drop. Activity identity, the effect ledger, effect tags, the outbox, checkpointing, the provenance lattice, verification-before-knowledge and the ExecutionGraph are named as keep-regardless |
| **Evidence available** | A keep/drop list exists in `docs/product/06-mvp-and-implementation-strategy.md` §8.3, written for the macOS product. **The general artefact does not exist** |
| **Decision required** | A written single-writer invariant profile |
| **Blocking?** | **YES** before line one of runtime code |
| **Next experiment** | Walk all 39 and mark each: applies / does not apply with one writer / applies in a weakened form. Roughly half a day |

---

### Q9 — Whose Principal is an MCP caller?

| | |
|---|---|
| **Why it matters** | A coding agent connecting on behalf of an engineer means the IDE, the agent and the Brain are three parties. The token must carry an identity the Brain can verify **without trusting the middle one** |
| **Hypotheses** | **(A)** The MCP server mints its own Principal from a per-user credential. **(B)** It accepts a delegated token. **Either can work. Letting the client assert an identity is the failure** |
| **Evidence available** | The internal model — server-resolved Principal, never client-supplied — is the property being preserved one layer up |
| **Decision required** | A or B |
| **Blocking?** | For the MCP server only. **Decide before it exists, not during** |
| **Next experiment** | None. A design decision |

---

### Q10 — How are overlapping (non-partitioned) permissions modelled?

| | |
|---|---|
| **Why it matters** | Organizational knowledge is **not partitioned.** A private channel, a restricted repo, an HR document and a customer contract have different, **non-nesting** audiences. A single tenant predicate does not express that. **One wrong join leaks, and the leak has no error** |
| **Hypotheses** | Labels captured at ingest and propagated to every derived claim, with a containment test at read. **No complete model exists in any document here** |
| **Evidence available** | The requirement is stated. The mechanism is not designed |
| **Decision required** | A permission model that expresses overlapping audiences |
| **Blocking?** | Before the second source, and **absolutely before any non-public source** |
| **Next experiment** | Enumerate the real audiences in the target environment (needs Q3), then design against those rather than in the abstract |

**Sub-question, open with no general solution:** does an **aggregate** leak? Can
the Brain state "three teams are blocked on X" without disclosing a private
fact? The practical rule — an aggregate that cannot be cited should not be
produced — is a mitigation, not an answer, and it will be too strict in some
cases and too loose in others.

---

### Q11 — What are the confidence floor, the retire floor, and the decay half-life?

| | |
|---|---|
| **Why it matters** | They gate what influences a run. **Tuning them before the extraction noise floor is measured is fitting to noise** |
| **Hypotheses** | **None defensible. No consulted source gives a starting value** |
| **Evidence available** | None. The noise floor has never been measured |
| **Decision required** | Measure first, then tune |
| **Blocking?** | Not for Phase 1 — the *mechanism* ships with placeholder values and the **measurement** ships alongside |
| **Next experiment** | Build the reviewed extraction sample: a few hundred real observations, extracted, reviewed once, committed. It gives the noise floor and doubles as a regression test |

---

### Q12 — How large does the predicate vocabulary grow before maintaining it is the bottleneck?

| | |
|---|---|
| **Why it matters** | The closed vocabulary is what makes identity computable without embeddings. If it grows without limit, [ADR-0008](decisions/ADR-0008-no-embeddings-in-phase-1.md) flips earlier than planned |
| **Hypotheses** | Unknown. Recorded as open in **two** independent documents, and named as one of the three decisions most likely to be wrong |
| **Evidence available** | **None. No source consulted answers it** |
| **Decision required** | None yet — it is a measurement |
| **Blocking?** | No |
| **Next experiment** | Track vocabulary size and out-of-vocabulary rejection rate from the first source onward. The curve answers it |

---

### Q13 — How is a human correction distinguished from a human being wrong?

| | |
|---|---|
| **Why it matters** | Treating corrections as highest-authority is right most of the time and **wrong when someone confidently corrects the agent about something the agent verified against production** |
| **Hypotheses** | Current position: a correction is high authority on **intent** and does **not** automatically outrank a probe on **reality**. Described by its own author as *"a starting point, not a settled answer"* |
| **Evidence available** | The two-axis authority model supports the split. Nothing validates it |
| **Decision required** | Whether the split holds, and what happens when a human insists against a probe |
| **Blocking?** | No |
| **Next experiment** | Log every case where a human correction contradicts a probe. The frequency and the outcomes decide it |

---

### Q14 — Does a claim inherit taint through a marshalled, schema-validated extraction?

| | |
|---|---|
| **Why it matters** | The provenance lattice says **nothing clears taint, absolutely.** Whether an enum extracted from an untrusted document is still derived content determines whether large classes of claim can ever reach ACTIVE |
| **Hypotheses** | **(A)** Taint is monotonic; a schema-validated enum from untrusted input is still untrusted-derived. **(B)** Marshalling through a closed schema is a trust boundary. **It is a security judgement rather than an architectural one** |
| **Evidence available** | The lattice's own absolutism argues for A |
| **Decision required** | A or B, with the reasoning |
| **Blocking?** | No, but it decides how much of the store can ever be ACTIVE |
| **Next experiment** | None. A judgement |

---

### Q15 — What makes a contradiction blocking rather than advisory?

| | |
|---|---|
| **Why it matters** | Blocking contradictions **refuse actions.** Too liberal and one disagreement in a busy scope blocks everything; too conservative and the gate never fires |
| **Hypotheses** | **Not established anywhere.** Severity exists as a field with no assignment rule |
| **Evidence available** | None |
| **Decision required** | An assignment rule |
| **Blocking?** | Before contradictions gate anything |
| **Next experiment** | Run advisory-only first. Measure which contradictions a human says *should* have blocked |

---

### Q16 — What is the entity merge/split lifecycle?

| | |
|---|---|
| **Why it matters** | Two entities turning out to be one — or one turning out to be two — after claims are attached to both is **inevitable** with real data. Nothing specifies what happens |
| **Hypotheses** | Not established |
| **Evidence available** | None |
| **Decision required** | A lifecycle, including what happens to evidence, versions and the rebuild invariant |
| **Blocking?** | Before the second source, where identity stops being free |
| **Next experiment** | None. Design work |

---

## 2b. Raised by the outside-in review (2026-09-14)

Full reasoning in [`14-outside-in-review-2026-09-14.md`](14-outside-in-review-2026-09-14.md).
These are **product and validation** questions rather than design questions, and
all five are cheap to answer.

### Q17 — Do the valuable questions occur at a useful rate?

| | |
|---|---|
| **Why it matters** | The premise. If real questions are dominated by lookups, the kind model, two-axis authority, bitemporal validity and the contradiction register are machinery for a rare case |
| **Status** | **Open, and already recorded as genuinely open** in the Brain architecture |
| **Evidence available** | **None.** No question set has ever been collected |
| **Blocking?** | Not mechanically. **It is the cheapest way to falsify the whole thesis**, which makes it urgent rather than blocking |
| **Next experiment** | 50 real questions from the last 90 days, classified lookup / why / temporal / contradiction, with the threshold **pre-registered before counting.** One day |

### Q18 — Will customers author and maintain an authority ladder?

| | |
|---|---|
| **Why it matters** | The architecture cannot function without it and by design cannot infer it. **It is an unpriced onboarding tax on every customer**, and no document treats it as a commercial risk |
| **Status** | Open. Never examined as a go-to-market question |
| **Evidence available** | **None.** The risk is a hypothesis about customer behaviour and has never been tested against any organization |
| **Blocking?** | Not for Phase 1. **Blocking for a business model** |
| **Next experiment** | Run the Q2 ladder meeting, **time it**, and ask each participant afterwards whether they would have done it before seeing any output. Two hours |

### Q19 — Does organizational context measurably improve agent output?

| | |
|---|---|
| **Why it matters** | The consumer bet in the strategic chain. Coding agents already read the codebase, which is the highest-authority source for implementation facts |
| **Status** | Open. **Asserted by the strategy, derived nowhere, measured never** |
| **Evidence available** | None |
| **Blocking?** | Not mechanically. It measures the **ceiling** of the whole chain |
| **Next experiment** | Wizard-of-Oz: 20 real tasks, 10 with hand-written perfect context, blind-graded. **Needs no Brain.** Three days |

### Q20 — How much of the runtime is actually on the critical path?

| | |
|---|---|
| **Why it matters** | The runtime is the largest existing asset and is in the strategic chain. **The the Brain architecture says the Brain does not need it** and names four primitives with individual triggers. No document reconciles the two |
| **Status** | Open, and the contradiction is in the corpus already |
| **Blocking?** | For scope. It may remove most of the planned work |
| **Next experiment** | Walk the 39 invariants; mark each needed / not needed / needed-later-with-a-trigger. This is **Q8** and it answers both. Half a day |

### Q21 — Can this team convert design into shipped code?

| | |
|---|---|
| **Why it matters** | **FACT:** 46 commits, all documentation, zero product source files ever committed. Design velocity is demonstrated; implementation velocity is unmeasured |
| **Status** | Open. Uncomfortable and worth asking |
| **Blocking?** | No, but it is the **highest-prior failure mode**: a correct architecture, more of it, indefinitely |
| **Next experiment** | Timebox one week: ship identity-keyed extraction (~30 lines plus a test that a redelivered observation does not produce a second claim). Failing to ship it is information about the team, not the task |

---

## 3. Unsolved — and not by any current design

These are recorded so nobody spends a sprint discovering them. **They are not
tasks.** Each is a limit stated by the design that has it.

| Problem | Position |
|---|---|
| **Noticing a claim is wrong when nothing new has been observed about it** | **STRUCTURALLY UNSOLVED.** Every mechanism except the probe loop is reactive, and probes cover only a minority of predicates. The runtime cannot feel doubt, so doubt must be manufactured — and manufacturing it for a social fact is not something anyone has solved |
| **Self-confirmation through the world** | **PARTIALLY SOLVED.** In-system defences close the loop internally. They do not stop the agent asserting something, a human internalising it, and that human later stating it as their own belief — a genuine observation from a genuine actor, indistinguishable from independent corroboration |
| **Causation from organizational outcomes** | **UNSOLVED**, and acknowledged as such. A sealed prediction plus a measured outcome is the cleanest evidence available at n=1 and gives **no causation.** The mechanism check is the only instrument that works, and only because it was written down before the result |
| **Knowing what the organization does NOT know** | **UNSOLVED and barely explored.** "I have no claims about X" conflates *nobody has said anything*, *this does not exist*, and *I cannot see it*. Three very different answers, and the third is a permission fact the asker may not be allowed to learn |
| **Whether any of this beats a good search box for most questions** | **GENUINELY OPEN**, and worth saying plainly. Most questions are lookups where retrieval quality is the whole game. The advantage appears on **why** questions, **temporal** questions and **contradictions** — the valuable minority. **An aggregate quality score will be dominated by lookups and will not show the difference** |
| **Indirect boundary erosion in an evolution loop** | **UNSOLVED.** A loop that cannot edit a boundary can propose changes that make it irrelevant, with every edit permitted and measured positive. Named as the most important open problem in the evolution material, with only human review offered against it |
| **Fallback atrophy** | **UNSOLVED.** A team's ability to re-fit a harness by hand decays because the loop succeeds. No mechanism proposed |

---

## 4. Resolved

### Q1 — Which product are we building? *(RESOLVED 2026-09-14)*

| | |
|---|---|
| **Original framing** | Two directions appeared to compete: **(A)** `prd.md`'s macOS personal-paperwork agent, GO WITH MAJOR CHANGES, 2026-09-06; **(B)** the Business Brain direction, 2026-09-14. Neither document acknowledged the other, and A's Change 3 (cut the developer-tools direction entirely) appeared unanswered against B |
| **Resolution** | The project owner stated directly, 2026-09-14, that `prd.md` was written to explore a curiosity question — how the agent runtime could be used to control iOS or macOS — and was **never a competing product decision.** There was no actual contest. The Organizational Brain direction is the live product direction; `docs/project/PRD.md` is the project's actual PRD, not one of two contended options |
| **Decision record** | [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md), superseding [ADR-0021](decisions/ADR-0021-product-direction-is-contested.md) |
| **What this does NOT resolve** | Q2 (the authority ladder) is still open and still blocking. `prd.md` itself is retained as a record of real research, corrected only in its framing relative to the live direction — see its banner |
| **Change log** | `11-architecture-change-log.md`, 2026-09-14 |
