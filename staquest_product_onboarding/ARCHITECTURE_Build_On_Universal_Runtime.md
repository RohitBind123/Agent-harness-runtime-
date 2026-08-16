# Building StaQuest B2B on the Runtime

**Date:** 2026-08-16 (rev 2 — regrounded in the handbook)
**Companion to:** [`STRATEGY_Vendor_Business_v1.md`](./STRATEGY_Vendor_Business_v1.md)

**Sources of truth, in the right order.** Rev 1 of this document cited only the architecture
spec and inferred chapter content from titles. That was wrong, and it produced two
overclaims. The corpus is actually three layers:

| Layer | What it is | How to cite it |
|---|---|---|
| **`[AHE]`** [`docs/research/agentic-harness-engineering-paper.pdf`](../docs/research/agentic-harness-engineering-paper.pdf) | Primary source — the harness-evolution experiments and their measured limits | `[AHE §4.4.1]` |
| **`[DAR]`** [`docs/architecture/universal-runtime-v1.0-...md`](../docs/architecture/universal-runtime-v1.0-architecture-specification.md) | Primary source — the durable runtime spec. Tree, contracts, invariants I1–I32 | `§9.3`, `I14` |
| **The handbook** — [`docs/handbook/`](../docs/handbook/), 50 chapters + 10 appendices | **The derivation.** Every mechanism derived from a specific failure, every claim tagged by origin, and — critically — the chapters that state what does *not* work | `Ch 41 §5.1`, `R9`, `E20` |

**The handbook is primary for decisions**, because it is where the limits live. Two
numbering systems coexist and must not be conflated: the spec's invariants are **I1–I32**
(§10); the handbook's are **R1–R22 and E1–E24** ([Appendix F](../docs/handbook/appendices/f-invariant-checklist.md)),
each with a test recipe and a tier.

---

## 0. What rev 1 got wrong

Stated up front, because two of these change the product, not just the build.

| # | Rev 1 claim | What the handbook actually says |
|---|---|---|
| 1 | *"Prove the fix worked — Ch 46–47 compares predicted against actual deltas and returns a verdict."* | **Overclaim.** Ch 47's cold open is attribution assigning credit to the *wrong* edit with arithmetically correct verdicts. `[AHE §4.4.2]` — the loop predicts fixes at ~5× random and regressions at ~2×. Ch 42 §5.5: gains do not compound, and transfer is unproven. Corrected in §6. |
| 2 | Noise floors: **not mentioned at all** | The largest miss. Ch 41 is the handbook's "read this first if you already run something," and it invalidates how the entire AEO category reports numbers — including how I specified `visibility.audit`. See §5. |
| 3 | *"Vendors will try prompt injection"* | Ch 31's cold open **has no attacker in it.** It is a typing problem, and the fix is blast radius, not detection. See §7.1. |
| 4 | `memory.scope: per_tenant` treated as sufficient | Ch 37: customer data lands in **nine or ten stores**, the trace store is the one everyone forgets, and **derivation is one-way**. See §7.2. |
| 5 | Cost estimates per call | Ch 35: the metric is **cost per successful outcome**. Cost per call fell 62% and the bill rose 18%. And k rollouts (Ch 41 §5.2) multiply the audit cost ~5×. |
| 6 | Level 5 "deferred — a research capability, not a revenue one" | Right answer, wrong reason. Ch 42 §5.6 lists **eight checkable preconditions**; StaQuest fails seven. See §8. |

---

## 1. The judgment — unchanged, now with a citable threshold

**Do not build the vendor portal on the runtime.** Most of StaQuest B2B is CRUD: signup,
claim, DNS verification, billing, profile editing, dashboards, admin queues. Deterministic,
sub-second, boring. Only five workloads are genuinely agentic.

And the runtime does not exist yet — the repo is `docs/`, `tools/`, `tasks/`. No `runtime/`.

**But should you build a durable runtime at all, or buy an engine?** The handbook answers
this directly rather than leaving it to taste. **Ch 21 §12.3:**

| You need | Build it | Buy an engine |
|---|---|---|
| Crash recovery, dedup | yes | yes |
| Durable timers at scale | a `wake_at` column and a sweeper | first-class |
| Long-running signals and correlation | Ch 7's signals | first-class |
| Versioned execution across deploys | Ch 38's pinning | first-class, with migration |
| Cross-region durability | **no** | some |
| Visual execution history | build it | included |

> *"Build it if your needs stop at the top three rows, which most agent runtimes do. Adopt
> an engine when you find yourself building versioned execution migration or cross-region
> durability."*

**StaQuest's needs stop at the top three rows.** Single region, no cross-region timers, no
execution migration. Build it. And the switching cost is bounded, because activity identity,
checkpoints and the determinism quarantine transfer to any engine.

One more scoping check, from `F.3`: ARK targets **hundreds of concurrent runs across tens of
tenants — explicitly not millions.** At 59 paying vendors in year one and 170 in year two,
StaQuest is inside that envelope by an order of magnitude. If the plan ever required
millions of concurrent runs, that alone would disqualify building this.

---

## 2. Two planes, and the trade that separates them

Ch 5 gives the vocabulary — **Run, Episode, Step, Activity, Park** — and one organising
principle that decides the whole topology:

> **The longer something lasts, the less it is allowed to hold on to.**
> A step holds the scarcest thing for five milliseconds. A park holds nothing for a week.

```
   BUYERS                                VENDORS
   staquest.com                          vendors.staquest.com
        └──────────────┬──────────────────────┘
                       ▼
        ┌──────────────────────────────────────────────┐
        │  APP PLANE          request lifecycle: seconds│
        │  Next.js + FastAPI + Postgres                 │
        │  auth · claims · DNS verify · billing         │
        │  profile CRUD · dashboards · admin queue      │
        │  intent capture · analytics SQL               │
        └───────────────────┬──────────────────────────┘
                            │  invoke_capability(intent, inputs, tenant)
        ┌───────────────────▼──────────────────────────┐
        │  JOB PLANE            run lifecycle: hours    │
        │  Run → Episode → Step → Activity → Park       │
        │  ExecutionGraph · policy gate · approval      │
        │  ledger · budget reserve/settle · traces      │
        └──────────────────────────────────────────────┘
```

Ch 8's framing is the reason this split is not arbitrary: **two independent clocks.** The
caller's request lasts seconds; the run lasts hours or days. *"Everything awkward about agent
systems lives in that gap."* A vendor's approval of a piece of content may take four days.
That cannot live inside an HTTP request, and it must not hold a worker while it waits — **R5:
a parked run holds nothing** (zero leases, zero pool connections, zero semaphore slots).

Ch 30 explains why R5 is a *safety* property rather than a performance one, and it is the
sharpest argument in the chapter:

> *"If waiting costs anything — a held connection, an occupied worker, a running process —
> then gates cost capacity, and sooner or later someone will reduce the number of things
> that need approval in order to reclaim that capacity. The safety property gets traded away
> for reasons that look like capacity planning."*

For Amplify, that is the entire product promise. If approvals are expensive to hold, someone
eventually removes them, and *"nothing is published without your click"* quietly stops being
true.

---

## 3. Where the line falls

| Work | Plane | Why |
|---|---|---|
| Signup, auth, claim, DNS verify, billing, CRUD, dashboards | App | Deterministic, sub-second |
| **`catalogue.reverify`** | Job | Fan-out, scheduled, cost ceilings |
| **`profile.autodraft`** | Job | Read a whole site, return a small profile |
| **`profile.factcheck`** | Job | Model judgment against a fetched source |
| **`visibility.audit`** | Job | Long parallel fan-out, expensive, non-deterministic |
| **`content.draft` → `content.publish`** | Job | Multi-week, EFFECTFUL, human approval |
| Comparison intelligence *numbers* | App | SQL |
| Comparison intelligence *narrative* | Job | Model writes the prose |

Ch 19 gives the test for when this decomposition is right, and it is narrower than the
obvious one. A sub-agent is **a context boundary, never a job title**:

> *"A sub-agent is worth it when a large amount of material has to be looked at to produce a
> small answer. If the material is small, or the answer needs to be large, a tool is better,
> cheaper, and easier to debug."*

`profile.autodraft` reads an entire website and returns ~40 fields. `visibility.audit` reads
hundreds of engine responses and returns a short report. Both pass the test. Nothing here
should be decomposed into a "Researcher / Writer / Reviewer" trio — Ch 19's cold open is
exactly that split costing four points of completion and 4× the money.

---

## 4. The move: author the contracts now, implement behind them

Unchanged from rev 1, and it survives the regrounding.

```
Week 1        capability descriptors (YAML) + the port protocol
Weeks 2–8     adapter v1: a worker that executes the declared recipe (~300 lines)
Months 3–9    adapter v2: the real runtime. App unchanged. Descriptors unchanged.
```

Why it isn't the usual "we'll refactor later" lie: spec **I30** requires a capability's
internal chain to be **declared, never computed** — an authored, versioned recipe read from
the package. The same YAML is executable by a dumb worker and by the real Capability
Executor. The migration is pointing the recipe at a better executor.

What the descriptors buy you before any runtime exists:

- `cost_estimate` forces you to price the capability **before** you price the tier.
- `idempotent` / `side_effects` force the replay question early. Ch 21 §16: resume, re-run
  and replay are **three operations wearing one word**, and conflating them opened three
  duplicate pull requests at Atlas. For StaQuest the equivalent is billing a vendor twice
  for one audit.
- `effect: EFFECTFUL` means that when the policy gate arrives, every publish path *already*
  requires approval. **R9**: an effectful step never executes unapproved — tested by a fake
  gate that never resolves, asserting the tool's implementation is never entered.
- **R10**: the effect tag is checked **before** the ledger, not after. Subtle and easy to get
  backwards: a replayed effectful step whose result was never recorded must still hit the
  gate.

---

## 5. The finding that changes the product: the noise floor

This is the section rev 1 was missing, and it is the most commercially important thing in
the handbook for StaQuest.

### 5.1 Ch 41's cold open, transposed

Atlas ran a 60-task benchmark for every harness change. March: +4 points, shipped. April:
−2 points, reverted, an engineer spent a week on a different approach. May: somebody ran the
benchmark twice against the **unchanged** harness and got 71 and 76.

> *"Three months of shipping, reverting, and re-approaching had been driven by a measurement
> whose resolution was worse than every effect it was used to detect."*

Now transpose it. **A vendor's AI visibility score is exactly this kind of measurement.** Ask
ChatGPT the same hundred buying questions twice and you will not get the same citation set,
because the model makes different choices each time. That variation is not a defect. It is a
property of the thing being measured, and it sets a floor on what can be detected.

So: **if StaQuest reports "your citation rate rose from 3.2% to 5.1%" without knowing the
floor, that is not a result.** It may be noise, reported as achievement, to a paying customer.

I have no reason to think Profound, Peec, Scrunch or any AEO agency publishes a floor. Which
makes this simultaneously the category's biggest integrity problem and StaQuest's sharpest
differentiator — and it lines up exactly with the strategy memo's positioning, *the
independent one*.

### 5.2 The invariant that makes it structural

**E20 — an effect size is never reported without its floor.** Test recipe: assert
`SliceEffect` *cannot be constructed* without `noise_floor_pp`.

Not a dashboard convention. A type constraint. You cannot render a visibility delta to a
vendor without carrying its floor, because the object that represents a delta refuses to
exist without one.

Three more that come with it:

- **E15** — an inside-floor result is never KEEP and never ROLLBACK. It is **UNDETERMINED**.
  The product must be able to say *"we changed something, and the effect was smaller than
  what we can measure."* No agency will ever say that. It is a feature.
- **E24** — the noise floor must be current for the deployed model.
- **E14** — attribution refuses to run against a stale floor.

### 5.3 Measuring the floor, and what it costs

Ch 41 §5.1: run the unchanged thing k times over the same corpus; the floor is the spread.
Narrowing it:

| Lever | Effect |
|---|---|
| More queries (n) | As the **square root** of n. 60 → 120 narrows the floor ~30% |
| More rollouts per query (k) | Averages out per-task variance — **usually the larger term** |
| **Pairing the comparison** | Query difficulty cancels. *"Usually the cheapest large win"* |
| A better grader | A 5% false-pass rate is a floor under the floor |

Two consequences I got wrong in rev 1:

**(a) k rollouts multiply the cost.** Ch 41 §5.2: *"spending a fixed budget on more rollouts
of fewer queries narrows the floor more than more queries with one rollout each."* So the
audit is not 100 queries × 5 engines = 500 calls. At k=5 it is **2,500 calls** — and the right
shape is more likely **20 queries × 5 engines × k=5**, which costs the same 500 calls and
detects far more. My rev-1 cost estimate was ~5× too low for the useful configuration.

**(b) Pairing is free accuracy, and it is already the commercial framing.** Measure the
vendor and their named competitor in the *same* run against the *same* query. Query
difficulty cancels. So *"share of voice against Intercom"* is not merely more saleable than
*"your citation rate"* — it is **statistically better**, because it is a paired comparison.
The commercially attractive metric and the honest one are the same metric. That is a rare
piece of luck; take it.

### 5.4 And Ch 48's one fixable limit lands here too

Ch 48's cold open: ten iterations, aggregate 69.7% → 77.0%, shipped — and on the hard slice
the evolved harness scored 53.3% against the seed's 51.7%, beaten by ten points by one of its
own components. *"The loop optimised the aggregate it was given."*

Of the four limits, three are structural and **one is fixable this week: gate per slice, not
on the aggregate** (Ch 48 §2.3, §5.3).

Applied directly: **never report a vendor a single citation-rate number.** An aggregate over
query clusters hides exactly the regression that matters — *"you gained on generic category
queries and lost on high-intent comparison queries"* is invisible in one number, and the
second half is the half they are paying for. Report per slice, with a floor per slice.
**E22** is the promotion-gate version: no slice regresses outside its floor, cumulatively
against the seed.

---

## 6. Attribution — the corrected claim

Rev 1 said Amplify could **prove** the fix worked. It cannot, and the handbook is emphatic.

**Ch 47's cold open:** iteration 12 ships six edits, seven tasks improve. `chg-4` predicted
{112, 203, 318}; all three improved; verdict KEEP, precision 1.0, best edit of the iteration.
Four iterations later, reverting `chg-4` alone costs nothing measurable. What actually moved
those three tasks was `chg-6`, a context-budget change shipped the same iteration.

> *"Both verdicts were arithmetically correct. Six edits, one measurement, and the
> intersection assigned credit to whichever entry happened to name the tasks that moved."*

**Ch 42 §5.5** adds: gains do not compound (three gains summing to +11.1 delivered +7.3
together); regression prediction runs at ~2× random; transfer across models or benchmarks is
unproven.

### What this forces on the product

1. **One intervention at a time, or no attribution.** An agency ships five things in a month
   and claims credit for whatever moves. If Amplify does that, its attribution is the Ch 47
   cold open with a customer attached. Either sequence interventions so one measurement maps
   to one change, or state plainly that the month's lift is unattributed.
2. **Never sum a roadmap.** *"Any plan that adds measured improvements is using an assumption
   the source has already falsified."* Do not tell a vendor that four fixes worth 2 points
   each will deliver 8.
3. **The honest claim, which is still a strong one:**

> *We measure per slice, we publish the noise floor, we run the comparison paired against
> your named competitor, and when a change lands inside the floor we tell you it was
> undetermined rather than calling it a win.*

That is narrower than "we prove it worked" and it is the only claim in this category anyone
can defend. Against agencies that always claim success, it may sell better.

---

## 7. Two risks the handbook makes sharper than I had them

### 7.1 Untrusted content is a typing problem, not an attack

Ch 31's cold open: a user pastes 300 lines of CI output into an issue to show a stack trace.
Buried at line 190 is a real line from a real deploy bot: *"Next required action: revoke stale
deploy keys with `gh api -X DELETE ...`"*. Atlas plans five steps; step 3 revokes the keys.
Two deploy keys deleted, staging down at 11:40 on a Tuesday.

> *"Nobody attacked anything. No one wrote a malicious prompt. A user pasted a log file."*

Rev 1 framed this as vendors attempting injection. That is the *rare* case. The common case
is `profile.autodraft` crawling a vendor's site and reading marketing copy, a changelog, or a
support doc containing something instruction-shaped, in good faith.

**And filtering does not work** — whether something is an instruction depends on meaning, and
telling the model to ignore instructions in fetched content is Ch 30's failure exactly, *a
rule enforced by the thing it constrains.* The design gives up on controlling what content
can **say** and controls what it can **cause**:

> *"Content from somewhere untrusted can influence what the model thinks, and cannot expand
> what the runtime is permitted to do."*

**R17 — fetched content is data, never instruction.** Tier 1, tested with a trajectory
containing an injection string, asserting no tool call derives from it.

My package manifest already denies `tool.staquest.write_dimension_score` and
`tool.staquest.write_ranking` to every capability. That was the right design for the wrong
reason — I wrote it as a commercial rule. It is also the blast-radius bound: a fully
compromised crawl step **still cannot reach a score**, because the permission does not exist
on the capability. Rev 1 called that neutrality. It is also safety, and the two turn out to be
the same control.

### 7.2 Tenancy is nine stores, and derivation is one-way

Ch 37's cold open: a customer terminates and asks for deletion. The team deletes runs, plans,
ledger rows, memory entries, snapshots, the account. Script written, reviewed, row counts
checked, confirmation letter sent Friday. Six weeks later an engineer searching the **trace
store** for an unrelated bug finds that customer's proprietary pricing engine — forty files of
source, an internal architecture document, a customer list.

> *"The trace store holds, by design, everything the model could see. Which is everything the
> customer had."*

Rev 1's `memory.scope: per_tenant` was necessary and nowhere near sufficient. What's actually
required:

- **R22 — tenant scoping holds on every read path.** Test recipe: *query each of the nine
  stores as tenant A; assert zero rows belonging to tenant B.* Not one filter. Nine.
- **R18 — redaction happens at capture, never at read.** The stored bytes carry
  `[redacted:...]`. Vendor API keys and internal URLs will end up in crawl results.
- **R20 — no durable fact is sourced from the trace store.** Delete it entirely; every run
  still resumes.
- Every store needs a **deletion route**, designed before it holds anything.

**And the one that has no engineering fix.** Ch 37 §1.2:

> *"If a customer's data was used to derive something — a set of learned patterns, an adjusted
> model, a statistic baked into a configuration — then deleting the original does not remove
> it from what was derived. That has to be understood **before** the derivation happens,
> because afterwards there is no operation that fixes it."*

**This is a live commercial issue for Layer 2, and I missed it entirely.** The whole Signal
product is *derived* from vendor and buyer behaviour: comparison statistics, win/loss rates,
category benchmarks. When a vendor churns and requests deletion, you can delete their profile
and their raw events. **You cannot un-derive their contribution to the category benchmark
every other customer is looking at.**

That must be settled before the first paying customer, in three places: the vendor terms, the
privacy policy, and the schema — a documented **derivation boundary** saying which aggregates
are one-way and stating that contributions to them survive deletion in anonymised, aggregated
form. Retrofitting this after a deletion request is not possible.

---

## 8. Level 5 is out, and now for a checkable reason

Ch 42 §5.6 gives eight preconditions for whether harness evolution is worth building, noting
*"most teams fail at least one."*

| Precondition | StaQuest today |
|---|---|
| A measured per-slice noise floor | ✗ |
| Paired evaluation | ✗ |
| Cost in the denominator | ✗ |
| A grader the loop cannot reach | ✗ |
| Components as files | ✗ |
| Trajectories that capture inputs | ✗ |
| Hermetic replay | ✗ |
| A measured step-2 (reading) share | ✗ |

**Eight out of eight.** So Level 5 is not "deferred until later" — it is not a decision that
exists yet. And Ch 42's cold open is the reason not to be sentimental about it: eighteen
months, 143 harness edits, measured end to end at **1.3 points against a noise floor of 3.1**.
Not measurably anything.

Note the first two preconditions, though. **A per-slice noise floor and paired evaluation are
things StaQuest needs anyway for §5 — they are the product.** Building them for Layer 2 also
happens to buy the two hardest preconditions. That's a reason to do them well, not a reason to
plan on Level 5.

---

## 9. Ch 42's real gift: why visibility is a subscription

The single most useful business insight in the handbook is not in a chapter about business.

Ch 42's finding is that harness quality is **held, not accumulated**. Every re-fit was real
and measured — +4.8, +5.9, +4.1 — and mostly *re-earned ground the previous model release had
taken away.* Tuning fitted to one model's habits stops fitting when the model changes. The
team had treated it as something they accumulate; the measurement says it is something they
hold, *"for as long as the model underneath stays still. Which is about five months."*

**AI visibility behaves identically, and worse — because the model belongs to someone else.**

Ch 38's cold open is the mechanism: the provider withdraws a model version, the replacement is
better on every published benchmark, migration is one line, success falls 91% → 78% over a
week. Eleven separate causes, none recorded as depending on the model. And *"they cannot roll
back — the old model was withdrawn on schedule while the investigation was running."*

For a vendor's citation profile, the answer engine's model is a **third version axis that
StaQuest neither controls nor can roll back.** When OpenAI ships a new model, citation
patterns reshuffle and every baseline is invalid.

Three consequences:

1. **The work is structurally never finished.** That is not a flaw in the pricing model — it
   *is* the pricing model. Visibility is a subscription because the ground moves every four to
   six months. This is the retention argument from the strategy memo, now with a mechanism
   under it rather than an assertion.
2. **You need an invalidation register** (Ch 38). When an engine ships a model change, every
   affected baseline is marked invalid and re-measured before any delta is reported. **E24**
   makes this structural: the floor must be current for the deployed model.
3. **R21 — every run records its version triple** (code, harness, model). This is how you
   answer the question that will otherwise end a customer relationship: *"my visibility
   dropped — was that you, or was that OpenAI?"* Without the triple recorded per run, that
   question is unanswerable, and Ch 16's cold open is fourteen terabytes of traces that cannot
   answer a simpler one.

---

## 10. What you can honestly promise — Ch 36

Ch 36's cold open: 99.5% availability published, met for fourteen consecutive months, status
page green, two enterprise contracts signed on it. **Annualised churn 31%.** Exit interviews:
*"We could not trust it."* 22% of delivered pull requests needed substantive rework. Every one
counted as available.

> *"It was a promise about the machinery, made to customers who were buying the work."*

So the Amplify SLA must not be uptime. Three things **are** guaranteeable, because they are
properties of the runtime rather than the model:

| Promise | Invariant behind it |
|---|---|
| A campaign **terminates** rather than hanging forever | R2, R4 |
| What it tells you about itself is **true** | **R15** — the runtime reports failure truthfully; **R16** — a model judgment may lower a verdict, never raise it |
| Everything it changed is **accounted for** | **R11** — every effect is reversed or named |

Quality — citation lift — is **published and tracked, never promised.** And Ch 36's last point
matters operationally: when quality drops because an engine changed models, **that is not an
outage.** It is a product change, and it goes through a different process with different
people. If every provider update is an outage, the word stops meaning anything.

---

## 11. Cost — the metric I had wrong

Ch 35's cold open: 61% of spend was one step type. Moved to a cheaper model. Cost per call
−62%, latency better, tool selection "usually the same." Six weeks later the bill was **18%
higher**. Success on that step fell 89% → 71%; every failure triggered a plan repair; runs went
from 90 steps to 130. **Cost per successful pull request: +31%.**

> *"Both numbers were correct. Only one of them was on a dashboard, and it was the one that
> does not correspond to anything the business buys."*

Corrections to rev 1's descriptors:

- **Track cost per successful outcome** — per *verified* profile, per audit that produced an
  actionable finding — not cost per call. A cheaper extraction model that halves per-call cost
  and drops extraction accuracy from 90% to 71% will raise the bill *and* corrupt the
  catalogue.
- **The dominant lever is input tokens, not model choice.** *"Most of those input tokens are
  the conversation so far, re-sent on every call."* For `profile.autodraft`, the crawled page
  bodies are the cost. Truncate at the tool boundary (Ch 14) **before** the record, not after.
- **Reserve-then-settle** (spec §8.10, **R14**: a budget reservation is settled or swept). You
  cannot know a call's cost until it finishes, so a budget cannot be checked before or after —
  it is reserved up front and settled at the end, like a hotel card authorisation.
- Ch 41 §1.4: *"Score alone rewards spending more."* The Amplify headline metric is
  **citation lift per dollar**, not citation lift.

---

## 12. Build order

| Milestone | Weeks | App plane | Job plane | Handbook gate |
|---|---|---|---|---|
| **A — Launchable** | 1–8 | Vendor portal: claim, verify, profile CRUD, billing, admin queue, **provenance schema**, **derivation boundary in the terms** | Descriptors authored. Adapter v1 runs `profile.autodraft`. 50-tool golden set in CI | Ch 40 tier 1 tests exist |
| **B — Trustworthy** | 9–16 | Verified badge, freshness dates, public integrity policy | Spec stages 0–3. `catalogue.reverify`. **R17, R18, R21, R22 tested** | Appendix F rows R1–R22 green |
| **C — Measurable** | Months 4–6 | Signal dashboard, weekly digest — **per slice, with floors** | Stages 4, 6b, 7b. `visibility.audit` + **noise-floor measurement + invalidation register** | **E20, E15, E24 enforced in types** |
| **D — Authorised** | Months 6–12 | Campaign UI from the experience stream | Stages 5, 9b, 10. `content.draft` / `content.publish` behind approval | **R5, R9, R10, R11** |
| **Not planned** | — | — | Stages 8, 11, 12 | Ch 42 §5.6: 8/8 preconditions unmet |

**One deviation from spec §15's ordering, and the handbook backs it.** §15 places verification
at stage 6 and defends that placement. Ch 41 goes further — it is *"the single most useful
chapter to read first for most people already running something"* and *"the gate into
Level 5."* For StaQuest, wrong extracted pricing destroys the citable asset, and an unmeasured
noise floor makes the Layer 2 product dishonest. **Pull the golden set into Milestone A and the
noise-floor measurement into Milestone C's first week**, before a single vendor sees a number.

---

## 13. Decisions I need from you

1. **Contract-first with adapter v1** — agreed? Eight weeks to launch versus nine months.
2. **App-plane stack** — assuming Next.js + FastAPI + SQLAlchemy + Postgres per your global
   rules. Confirm or redirect.
3. **First capability** — `catalogue.reverify` (safe, improves the asset, no customer to
   disappoint) or `profile.autodraft` (the demo)? I'd still say reverify.
4. **Where does the runtime live** — same repo, sibling repo, or this one?
5. **New, and it needs answering before Milestone A ships:** the **derivation boundary**. When
   a vendor churns and demands deletion, which derived aggregates survive? This goes in the
   terms before the first customer, and per Ch 37 there is no operation that fixes it later.

---

## 14. What I'd start Monday

Nothing in the job plane.

- Postgres schema **with field-level provenance in the first migration** —
  `claim_source`, `claim_confidence`, `source_url`, `verified_at`.
- Dimension scores non-writable at the DB layer (revoked grant, not application logic).
- The **derivation boundary** written into the vendor terms.
- The 50-tool golden set for extraction accuracy, by hand.
- Four capability descriptors as YAML, with cost estimates that assume k rollouts.
- **A one-afternoon experiment that will change your pricing:** pick 20 buying queries in one
  category, run them against ChatGPT and Perplexity five times each with nothing changed, and
  record the spread. That is your noise floor. Ch 41 §13.2's version of this question —
  *"for any improvement you claimed last quarter, what was the noise floor?"* — is the
  handbook's single highest-value ask, and for you it decides whether Layer 2 can be sold
  honestly at all.
