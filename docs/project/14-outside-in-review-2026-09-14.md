# Outside-In Review — 2026-09-14

**Stance.** Written as an independent founding architect with no stake in the
existing architecture. **Nothing below defends prior work.** Where the
architecture is good, it is not praised; where it is exposed, it is named.

**Basis.** The 2026-09-14 audit (`13-audit-2026-09-14.md`), the 24 decision
records, the four architecture documents, the product research, and the git
history. **No code was reviewed, because none exists.**

---

## 0. The labelling discipline used throughout

| Label | Means | Test |
|---|---|---|
| **FACT** | Verifiable in this repository, right now | Point at the file or run the command |
| **EVIDENCE** | External or reported, with a named source and a stated strength | Cite it, and say how strong it is |
| **HYPOTHESIS** | An unproven belief — the project's or mine | Say what would falsify it |
| **RECOMMENDATION** | What I think should happen | Mine. Argue with it |

**No sentence below mixes two labels.** Where the project has treated a
hypothesis as a fact, that is itself a finding and is marked.

---

## 1. The ten highest-leverage assumptions

Ranked by **leverage** = (how much changes if wrong) × (how likely wrong) ÷
(cost to test). The top three are all cheap to test and all currently untested,
which is the most actionable thing in this review.

---

### A1 — The valuable questions are *why*, *temporal*, and *contradiction* questions

> **The premise of the entire company.**

**ASSUMPTION.** That a meaningful share of the questions people actually ask are
reconciliation questions — not lookups.

**WHY WE BELIEVE IT.** **HYPOTHESIS.** The cancellation worked example is
compelling and the failure it describes is real: perfect retrieval still hides a
disagreement between a decision, an observation, and a test. The architecture
follows correctly *from that example*.

**EVIDENCE.** **Weak, and the project already says so.** The Brain architecture
§19.3 lists this as **GENUINELY OPEN** in its own words: *"most questions people
ask are lookups where retrieval quality is the whole game. The Brain's advantage
appears on WHY questions, TEMPORAL questions and CONTRADICTIONS — which are the
valuable minority."*

**FACT.** No question set has ever been collected. Zero real questions exist
anywhere in this repository.

**WHAT COULD MAKE IT FALSE.** The question mix in a real organization is
dominated by lookups ("where is X", "who owns Y", "what's the endpoint"). The
reconciliation questions exist but are rare enough that a good search box plus an
LLM captures 90% of the value at 5% of the cost.

**CONSEQUENCE IF FALSE.** **Terminal for the current thesis.** Kind-typed
claims, two-axis authority, bitemporal validity, contradiction registers and a
closed predicate vocabulary are all machinery for the minority case. If the
minority is small, the product is a worse search box carrying an enormous
correctness tax. The honest pivot would be to a well-built retrieval product,
which is a different and much more crowded company.

**CHEAPEST EXPERIMENT.** **One day, no code.**
Pull the last 90 days of questions people actually had to dig for — from chat,
tickets, DMs, wherever they live. Take 50. Classify each: **lookup / why /
temporal / contradiction**. **Pre-register the threshold before counting.**

A defensible line: **if under 25% are why/temporal/contradiction, the thesis is
in trouble and the architecture is over-built for the job.**

---

### A2 — Customers will author and maintain an authority ladder

> **The safety property that is also the go-to-market barrier.**

**ASSUMPTION.** That a named human in each customer organization will rank source
classes on two axes (authority over intent, authority over reality), agree it
with colleagues, own it, and keep it current.

**WHY WE BELIEVE IT.** **FACT.** The architecture cannot function without it and
**by design cannot infer it** — [ADR-0006](decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md). The reasoning for not inferring
is sound: authority inferred from recency, seniority or confident phrasing is
*wrong precisely in the cases that matter, and wrong invisibly.*

**EVIDENCE.** **None.** No organization has ever been asked to author one, here
or anywhere this project can observe. The assumption that they will is
untested in every particular.

**FACT.** The ladder has not been authored even *here*, by the team that
designed the requirement, four months after it was identified as the blocking
prerequisite.

**WHAT COULD MAKE IT FALSE.** Organizations will not convene a meeting to rank
their own sources of truth before getting any value. It surfaces political
disagreement — the Brain review says so approvingly: *"expect the meeting to
surface genuine disagreement about how the organization works."* That is
epistemically excellent and commercially brutal. Time-to-first-value is gated
behind an argument.

**CONSEQUENCE IF FALSE.** The product **does not onboard**. Every deal requires
unpaid organizational work before the first useful answer. Land-and-expand is
impossible; there is no self-serve motion; a trial cannot demonstrate value.
This is an **unpriced tax on every customer** and no document in this repository
acknowledges it as a commercial risk at all — it is discussed only as a design
virtue.

**CHEAPEST EXPERIMENT.** **Two hours, and it is the highest information-per-minute
test available.**
Run the ladder meeting for InOrbitX with two or three people. **Time it.** Record:
did they converge? What did they disagree about? How long? Then ask each
participant, separately: *"would you have done this before seeing any output from
the product?"*

If it takes three people two hours and ends unresolved for our own small team,
**assume it is a non-starter for an enterprise buyer** and design a bootstrapping
path — a default ladder per vertical, or a ladder inferred and then *confirmed*
rather than authored from nothing.

---

### A3 — Extraction precision is high enough for the store to be worth trusting

**ASSUMPTION.** That an LLM can extract typed claims from messy organizational
text at a precision that makes downstream corroboration, contradiction detection
and authority resolution meaningful.

**WHY WE BELIEVE IT.** **HYPOTHESIS.** Unstated. No document argues for it; every
document assumes it.

**EVIDENCE.** **FACT.** The Brain architecture lists it under **"NOT
ESTABLISHED"** and adds: *"the one I would most want tested early... Everything
downstream assumes it."*

**FACT.** There is no extraction prompt, no output schema, no worked example, and
no reviewed sample anywhere in this repository. **This is the single biggest gap
between how load-bearing something is and how much design it has received.**

**WHAT COULD MAKE IT FALSE.** Organizational text is not policy text. A PR
comment saying *"I think we decided not to do that"* has an ambiguous kind
(decision? observation? recollection?), an ambiguous subject, and an ambiguous
time. Precision in the 60–75% range is entirely plausible.

**CONSEQUENCE IF FALSE.** A pincer with no escape:
- Set the corroboration floor **high** → almost nothing crosses it → the store is
  empty and the product has no answers.
- Set it **low** → wrong claims reach ACTIVE → the product is a *confident liar*,
  which is worse than useless in a regulated domain and is the exact failure the
  whole architecture exists to prevent.

There is no floor setting that rescues bad extraction. **The corroboration
mechanism assumes errors are independent; systematic extraction errors correlate,
so they corroborate each other.**

**CHEAPEST EXPERIMENT.** **Two to three days.**
Take 200 real observations from InOrbitX history (PRs, commits, tickets). Write
one extraction prompt against a draft 20-predicate vocabulary. Run it. Have
someone who knows the project review every output. Measure **precision, recall,
and kind-assignment agreement** separately — they fail differently.

**Pre-register the floor.** Below ~85% precision, the design needs a human
confirmation step in the write path, which is a different product with different
economics.

---

### A4 — Injecting organizational context measurably improves coding-agent output

> **The bet the entire MCP chain rests on.**

**ASSUMPTION.** That Claude/Codex produce better work when given reconciled
organizational claims than when given the codebase alone.

**WHY WE BELIEVE IT.** **HYPOTHESIS.** Intuitive and unargued. It is asserted by
the strategic chain, not derived anywhere.

**EVIDENCE.** **None in this repository.** No measurement, no baseline, no task
set. **FACT.**

**WHAT COULD MAKE IT FALSE.** Three independent ways:
1. Coding agents already read the codebase, which is the **highest-authority
   source for implementation facts** — the Brain's own kind model says so. The
   marginal value may sit only in *intent* and *history*, which is narrow.
2. Context is not free. Injected claims consume budget that would otherwise hold
   code. A wrong or stale claim is actively harmful — worse than absent.
3. The vendors are moving. Agent memory, project context and organizational
   integrations are being built by the model providers themselves.

**CONSEQUENCE IF FALSE.** The chain **Business Brain → Brain MCP → external
agents** has no consumer. The Brain might still be valuable to humans, but that
is a different product with a different buyer, and the current strategy names
agents as the consumer.

**CHEAPEST EXPERIMENT.** **Two to three days, and it needs no Brain at all.**
A Wizard-of-Oz test:
1. Take **20 real completed tasks** from InOrbitX history where the outcome is known.
2. For 10, **hand-write** the organizational context a perfect Brain would have
   supplied — the decision, the intent, the contradiction, dated and cited.
3. Run all 20 through Claude Code, blind.
4. Have someone who knows the project grade the outputs **without knowing which
   arm they came from.**

**This is the most important experiment in this document.** If hand-written
*perfect* context does not measurably improve output, no amount of Brain
engineering will — because the ceiling has been measured and it is zero.

---

### A5 — Reconciliation-with-provenance is a product, not a feature

**ASSUMPTION.** That this is defensible as a standalone company rather than
something Glean, Atlassian, GitHub, Notion or a model vendor adds in two quarters.

**WHY WE BELIEVE IT.** **EVIDENCE — explicitly the weakest claim in the corpus.**
The Brain architecture states that nobody appears to combine authority, kind-typed
claims, bitemporal validity and contradiction-as-an-object — and immediately
adds that this is *"an argument from absence in public material and it is the
weakest claim in §3."*

**FACT.** **The differentiation rests on the weakest-evidenced claim in the
entire architecture corpus.** That is worth stating plainly.

**FACT.** The market research was conducted 2026-09-06 and searched rather than
fetched several sources; the egress proxy blocked others.

**WHAT COULD MAKE IT FALSE.** An incumbent with distribution ships "shows you
when your sources disagree." They do not need the full correctness apparatus to
capture the perceived value — the same asymmetry the PRD identified in a
different market, where a competitor *"classifies on filenames alone"* and still
wins.

**CONSEQUENCE IF FALSE.** No company. The architecture would still be correct and
still be commercially irrelevant.

**CHEAPEST EXPERIMENT.** **One week, two parts.**
(a) Re-run the competitive scan with **fetched** primary sources, specifically
looking for contradiction/conflict surfacing shipped since 2026-09-06.
(b) **Five discovery interviews** with engineering leaders. Do not pitch. Ask
what they last got wrong because two sources disagreed, and what it cost. **If
fewer than three produce a specific, expensive incident unprompted, the pain is
not acute enough to fund a company.**

---

### A6 — The agent runtime is needed at all

> **The most expensive assumption nobody has questioned.**

**ASSUMPTION.** That the six-layer durable runtime — 51 chapters, a 5,000-line
specification, 39 invariants — is on the critical path.

**WHY WE BELIEVE IT.** **FACT.** It is in the strategic chain, and it is the
largest existing asset. **HYPOTHESIS:** it is there partly because it exists.

**EVIDENCE — and it contradicts the strategy.** **FACT.** The Brain architecture
§13.5 states plainly: ***"The Brain does not need the fifty-chapter runtime to
exist."*** It then names exactly four primitives worth adopting, each with its
own trigger, and warns that adopting them as a block *"would be a rewrite
justified by architecture rather than by a problem."*

**FACT.** The project's own architecture review says the largest asset is not
required for the current direction. **No document reconciles that with the
strategic chain that includes it.**

**WHAT COULD MAKE IT FALSE.** It is already false as stated — the question is how
much of the runtime is needed, and the answer from the project's own analysis is
*four primitives*, not a runtime.

**CONSEQUENCE IF FALSE.** Enormous scope reduction — which is good news
misfiled as bad. But also: **the "the runtime is the asset that survives the
product being wrong" argument weakens**, and that argument is load-bearing in the
PRD's GO decision. If the runtime is not needed for the Brain and is *"copyable
infrastructure, weak moat"* by the PRD's own assessment, then the fallback asset
is weaker than the GO decision assumed.

**CHEAPEST EXPERIMENT.** **Half a day, and it is a reading task.**
Walk the 39 invariants and mark each: *needed for a Brain over one source with
one writer* / *not needed* / *needed later, with a trigger*. This is **Q8** and it
is already recorded as blocking. Expect the answer to be well under ten.

---

### A7 — A closed predicate vocabulary scales

**ASSUMPTION.** That ~20 predicates, growing under review, can cover
organizational knowledge without the registry becoming the bottleneck.

**WHY WE BELIEVE IT.** **HYPOTHESIS.** Unargued. A closed vocabulary is
assumed to be tractable because the alternative is assumed to be worse — not
because anyone has run one at organizational scale.

**EVIDENCE.** **FACT.** [ADR-0022](decisions/ADR-0022-predicate-vocabulary-is-closed-and-reviewed.md) itself nominates this as one of the three
decisions most likely to be wrong, and both the Memory and Brain documents record
the growth limit as **unanswered by any consulted source**.

**WHAT COULD MAKE IT FALSE.** Real organizational language is open-ended. The
out-of-vocabulary rejection rate stays high, and each addition is a reviewed
migration — so the registry becomes a permanent maintenance queue.

**CONSEQUENCE IF FALSE — and this is why it ranks here.** **The designated
fallback is itself compromised.** [ADR-0008](decisions/ADR-0008-no-embeddings-in-phase-1.md) defers to embeddings if the
vocabulary fails — but the argument *against* embeddings is that ANN indexes
post-filter, so recall collapses under exactly the selective tenant/permission
predicate this workload always carries.

**So: the mechanism may fail, and the escape hatch is argued to be broken.** This
is the only assumption in this review where failure has **no designed
alternative.** Everything else has a trigger and a fallback.

**CHEAPEST EXPERIMENT.** Rides free on A3. Track the OOV rejection rate across
the 200-observation sample and plot it as sources are added. **A rate that does
not fall as the vocabulary grows is the failure signal**, and it is visible
within days rather than months.

---

### A8 — The architecture's shape matches the deployment

**ASSUMPTION.** That a multi-tenant, server-shaped runtime with leases, relay
claims, sweepers, worker pools and per-tenant admission fits the target
deployment.

**WHY WE BELIEVE IT.** **HYPOTHESIS.** Inherited. The runtime was specified for a
hosted multi-tenant service before any target was named.

**EVIDENCE.** **FACT.** Recorded as Finding C in September 2026 and unresolved.
**FACT (2026-09-14):** the named validation environment is a broker insurance
portal **held locally on a desktop** — not a server, not multi-tenant, and in a
domain with real confidentiality boundaries.

**WHAT COULD MAKE IT FALSE.** It is likely already false. A local, single-user,
single-writer deployment makes roughly half the kernel dead weight — and a
regulated domain makes "what leaves the machine" a governance decision that no
document has made.

**CONSEQUENCE IF FALSE.** Two failure modes, opposite shapes. Port it wholesale →
a slow, complex system whose complexity buys nothing. Delete the wrong half →
lose the correctness properties that are the entire point. **The artefact that
would prevent both does not exist.**

**CHEAPEST EXPERIMENT.** **Not an experiment — a decision, half a day.** Pick one
of the three shapes in `06-validation-strategy.md` §7 (local Brain / hosted Brain
with local collector / fully hosted) and write down why. It constrains Q8, and
Q8 constrains the build.

---

### A9 — This team converts design into shipped software

**ASSUMPTION.** That the same process producing this architecture will produce a
working system.

**WHY WE BELIEVE IT.** **HYPOTHESIS.** Never stated, never examined.

**EVIDENCE.** **FACT, from git history:** 46 commits between 2026-08-04 and 2026-09-14.
**Every one is documentation.** 94 markdown files, 11 DOCX, 9 SVG, and 5 Python
files that build documentation. **Zero product source files have ever been
committed to this repository.**

**FACT.** The workflow that demonstrably exists is a *documentation* workflow. It
has no pull requests, no CI, no issue tracker, and no tests — recorded in
`05-development-workflow.md` §3.

**WHAT COULD MAKE IT FALSE.** Design velocity and implementation velocity are
different capabilities. A process optimised for producing considered documents
can be structurally biased toward producing more of them, because that is what it
is good at and what feels like progress.

**CONSEQUENCE IF FALSE.** The most likely failure mode is not a wrong
architecture. **It is a correct architecture, more of it, indefinitely** — the
exact failure the PRD names: *"building phase 1 beautifully, for four months,
because it is the part that is fully specified and therefore the most comfortable
to build."*

**CHEAPEST EXPERIMENT.** **One week, and it is also useful work.**
Timebox: ship identity-keyed extraction — roughly 30 lines plus a test proving a
redelivered observation does not produce a second claim. It is required under
every scenario, it is the one primitive that does not retrofit, and it is small
enough that failing to ship it in a week is **information about the team, not
about the task.**

---

## 2. The six answers

### 1. The single most important PRODUCT experiment

**The Wizard-of-Oz context A/B (A4).** 20 real InOrbitX tasks, 10 with
hand-written perfect organizational context, blind-graded.

**Why this one.** It measures the **ceiling** of the entire strategic chain
without building any of it. Every other product experiment tests a link; this
tests whether the chain carries load at all. If hand-written perfect context does
not improve agent output, the Brain cannot — and that is knowable in three days
instead of a year.

Run **A1 (question shape)** alongside it; it is one day and it tells you whether
the questions the Brain is built for even occur.

### 2. The single most important TECHNICAL experiment

**Extraction precision on 200 reviewed real observations (A3).**

**Why this one.** It is the load-bearing input to corroboration, contradiction
detection, authority resolution and trust — and it is the one the project's own
review flags as *"NOT ESTABLISHED"* and *"the one I would most want tested
early."* It also yields the noise floor, the draft vocabulary, and the OOV curve
for A7 as by-products. **Four blocked things unblock at once.**

### 3. The single most dangerous ARCHITECTURAL assumption

**A7 — that the closed predicate vocabulary scales.**

**Why this one rather than extraction precision.** Not because it is most likely
to fail, but because it is **the only assumption whose failure has no designed
escape.** Every other decision names a trigger and a fallback. Here the fallback
is embeddings, and the same corpus argues embeddings break under the selective
permission predicate this workload always carries. A failure here has nowhere to
go.

**Runner-up: entity resolution.** Named *"the component most likely to be
underestimated"* and then given one section, with no algorithm, no alias
curation process, and **no merge/split lifecycle** — and merges are inevitable
with real data.

### 4. The single most dangerous PRODUCT assumption

**A2 — that customers will author and maintain an authority ladder.**

**Why this rather than the question-shape assumption.** A1 is more likely to be
fatal, but it is *known* to be open — the project has recorded it. A2 is
**invisible as a risk**: it appears in every document as a design virtue and in
none as a commercial obstacle. It converts the architecture's best safety
property into an unpriced onboarding tax that gates time-to-first-value behind an
internal political argument. **An unexamined risk beats a known one for danger.**

### 5. What we should NOT build yet

| Do not build | Because |
|---|---|
| **Any schema** | Q7 unreconciled — two documents specify incompatible Phase 1 tables |
| **The ingestion framework** | Adapters are written one at a time against a fixed shape. *The framework is that shape* |
| **A second source adapter** | Not until one is proven end to end |
| **The MCP server** | No stable capability layer; Q9 undecided. Built now it constrains what it should project |
| **A graph database** | Second store engine breaks same-transaction commit. Measure hop depth with CTEs first |
| **Embeddings** | Trigger not met, and the measurement that would set it does not exist |
| **The Principal Agent** | Four of its objects are BLOCKED on organizational structures that do not exist |
| **Most of the runtime** | The project's own review says the Brain does not need it (A6) |
| **Any summarisation or curation layer** | A summary is not evidence for what it summarises |
| **A Brain UI** | Before knowing whether the Brain is *right*, a UI measures nothing |
| **More architecture documents** | See A9. This is the failure mode with the highest prior |

### 6. What we should build immediately

**Nothing that ships to a user. Four things, in parallel, inside two weeks.**

| # | Build | Days | Answers |
|---|---|---|---|
| 1 | **The Wizard-of-Oz context pack** — 20 tasks, 10 with hand-written context, blind grading | 3 | A4 — the ceiling of the whole chain |
| 2 | **The question-shape study** — 50 real questions, pre-registered threshold | 1 | A1 — whether the premise holds |
| 3 | **The extraction sample** — 200 observations, one prompt, full human review | 3 | A3, A7, the noise floor, the vocabulary |
| 4 | **The ladder meeting, timed** — with the post-hoc "would you have done this first?" question | 0.5 | A2 — the onboarding tax |

**If code must be written**, it is exactly one thing: **identity-keyed extraction**
— roughly 30 lines plus a test that a redelivered observation does not produce a
second claim. It is required under every scenario including the ones where this
company pivots, it is the only primitive that cannot be retrofitted, and shipping
it in a week is a measurement of A9.

---

## 3. What this review does *not* challenge

Stated so the criticism above is not read as blanket scepticism. These survive
outside-in scrutiny and should not be relitigated:

| Holds up | Why |
|---|---|
| The **kind-typed claim** | The cancellation example genuinely cannot be answered by ranking, and kinds are the minimal structure that answers it |
| **Observation log as system of record** | The rebuild property is real, cheap on day one, and expensive later. Correct regardless of which product wins |
| **Authority authored, never inferred** | The reasoning is right even though A2 says the *commercial* consequence is unexamined |
| **The model proposes, never writes** | Each of the four words in *"unreviewed, unabstracted, unclassified, from inside the run"* names a distinct failure |
| **Verification before knowledge** | The asymmetry — may lower, never raise — is the only thing making model judgement safe to use |
| **Identity-keyed extraction first** | Correct, cheap, and the one thing that does not retrofit |
| **Deletion route before retirement** | A store that cannot be enumerated cannot ship in a regulated domain |
| **Recording contradictions rather than resolving them** | The discipline that made this review possible at all |

**The architecture's problem is not that it is wrong. It is that it is
unvalidated, over-scoped for what has been proven, and resting its commercial
case on its own weakest-evidenced claim.**

---

## 4. Findings registered

| New question | Where |
|---|---|
| **Q17** — Do the valuable questions occur at a useful rate? | A1 |
| **Q18** — Will customers author an authority ladder? | A2 |
| **Q19** — Does organizational context measurably improve agent output? | A4 |
| **Q20** — How much of the runtime is on the critical path? | A6 |
| **Q21** — Can this team convert design into shipped code? | A9 |

Recorded in `10-open-questions.md`. No decision has been changed by this review;
it raises questions and recommends experiments only.
