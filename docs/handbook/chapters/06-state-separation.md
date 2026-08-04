```
  Level 1 · Chapter 6
  STATE SEPARATION: RUN, DOMAIN, MODEL — AND HARNESS
  Requires   C4 The Complete Runtime, C5 The Five Nouns
  Unlocks    C7 The Edge, C11 Context, C12 Memory, C17 State Manager,
             C21 Durable Execution, C32 Distributed Execution,
             C37 Tenancy, C47 Attribution
  Diagrams   Core (5)
```

# Chapter 6 — State Separation: Run, Domain, Model — and Harness

---

## 1. Motivation

### 1.1 Cold open

Atlas finishes a hard run on `acme/billing-service`. The test suite had failed four times before the
agent worked out that it needed a database URL in the environment, and the harness — behaving exactly
as designed — records the lesson so no future run wastes forty minutes on it. One line appended to
long-term memory:

> *Test suites in this codebase need `POSTGRES_URL` set before running; e.g.
> `postgres://ci:••••@pg-internal-3.acme.corp:5432/billing_test`.*

A useful, specific, hard-won fact. Precisely the kind of thing the memory component exists to keep,
and the reason it measured as the highest-value single component in Chapter 1's ablation.

Six weeks later, an engineer at a completely different customer opens a pull request Atlas authored
and finds, in the body, a suggestion to check whether their integration tests need something like
`postgres://ci:...@pg-internal-3.acme.corp:5432`.

Nobody wrote a bug. Every component did its job. The run that wrote the lesson was scoped to
`acme`'s tenant, its run row carried the tenant id, its sandbox was destroyed on completion, and
Atlas's domain tables enforce tenant isolation on every query.

The leak happened through the one piece of mutable state that belonged to none of those categories
and was therefore scoped by none of their rules.

### 1.2 Why this chapter exists

Chapter 4 gave you a one-sentence test: delete the runtime and the product must still be coherent
`[DAR §3.3]`. That test is correct and it is not sufficient, because it only separates *two*
categories. Real systems have four, and the two that the reference architecture does not name are
where the interesting failures live.

This chapter classifies every piece of state in an agent system into exactly one of four categories,
gives each its owner, lifetime, consistency model, and deletion behaviour, and turns the whole thing
into checks you can run in CI rather than principles you can violate in review.

### 1.3 What previous framings got wrong

**"State is state."** Four categories with four owners, four lifetimes, and four consistency models.
Treating them uniformly is how a lease ends up on a domain aggregate and a credential ends up in a
harness file.

**"The message list is the run's state."** The most common and most damaging error in agent codebases.
The assembled context is a *projection*, not a source of truth. Section 5.3 makes the case; the
consequence is that a system which persists it as authoritative cannot replay.

**"Memory is just a file."** It is the only mutable state that crosses run boundaries without being
domain truth. The cold open is what that means when nobody has said whose it is.

---

## 2. High-Level Mental Model

### 2.1 Four questions, four categories

| Category | Answers | Owner | Lifetime |
|----------|---------|-------|----------|
| **Domain state** | *What is true?* | your domain | permanent |
| **Run state** | *What is happening?* | the runtime | ends with the run |
| **Model state** | *What does the model see right now?* | the context system | one model call |
| **Harness state** | *What has the system learned to do?* | the harness | across runs, until edited |

The first two are `[DAR §3.3]` verbatim. The third and fourth are `[INF]` — the handbook's additions,
and §5.3 and §5.4 argue for each.

### 2.2 The classification procedure

`[INF]` Four questions, asked in order. The first "yes" wins.

```
   Does it survive deleting the entire runtime?
      YES -> DOMAIN STATE
      no
       |
   Does it outlive the run that produced it,
   without being a fact about the world?
      YES -> HARNESS STATE
      no
       |
   Is it fully reconstructible from facts already stored?
      YES -> MODEL STATE   (derive it; do not persist it)
      no
       |
      ---> RUN STATE
```

Run every field in your schema through it once. The exercise takes an afternoon and it is the
cheapest audit in this book.

### 2.3 The mental model to carry

> **Each category has exactly one owner, and the owner is responsible for scoping it. State that
> belongs to no category is scoped by nobody.**

The cold open is that sentence. Run state is tenant-scoped because the run row carries a tenant id.
Domain state is tenant-scoped because the domain enforces it. Long-term memory was scoped by nothing,
because nobody had decided what kind of state it was.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +----------------------------------------------------------------+
  |  DOMAIN STATE                       owner: your domain         |
  |  the merged branch . the open PR . the customer record         |
  |  strong, transactional, invariant-guarded                      |
  |  PERMANENT -- unaffected by deleting the runtime               |
  +----------------------------------------------------------------+
                    ^                            |
        commands    |                            |  events
                    |                            v
  +----------------------------------------------------------------+
  |  RUN STATE                          owner: the runtime         |
  |  current step . plan . lease . attempts . budget spent         |
  |  eventually consistent, checkpointed, recoverable              |
  |  ENDS WITH THE RUN -- gone on deletion, and correctly so       |
  +----------------------------------------------------------------+
                    |                            ^
        assembled   |                            |  written back
        into        v                            |  selectively
  +----------------------------------------------------------------+
  |  MODEL STATE                        owner: the context system  |
  |  assembled context . cache prefix . reasoning budget           |
  |  no consistency model -- it is DERIVED                         |
  |  ONE MODEL CALL -- never persisted as truth                    |
  +----------------------------------------------------------------+
                    ^
        contributes |
        to          |
  +----------------------------------------------------------------+
  |  HARNESS STATE                      owner: the harness         |
  |  long-term memory . prompts . tools . middleware . skills      |
  |  versioned, git-backed, human- or loop-edited                  |
  |  ACROSS RUNS -- survives the runtime; is not domain truth      |
  +----------------------------------------------------------------+

  Figure 6.1 -- Four categories and their flows (D1 High-Level Architecture)
```

The arrows are as important as the boxes. **Domain and run state exchange only commands and events**
— Chapter 4's narrow waist. **Model state is assembled downward and never written back directly**;
what flows back up is a selected fact, not the context that produced it. **Harness state contributes
to model state and is written by a different loop entirely**, at a different cadence.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  DOMAIN STATE
  +--------------------------------------------------------------+
  | atlas.repositories . atlas.pull_requests . atlas.customers    |
  | atlas.subscriptions . atlas.audit_log                         |
  |                                                              |
  | MUST NOT CONTAIN: current_step . lease_owner . attempt_count  |
  |                   plan_id . budget_used . run_state           |
  +--------------------------------------------------------------+

  RUN STATE
  +--------------------------------------------------------------+
  | runs        id . tenant_id . goal . state . plan_id           |
  |             current_step . version . lease_owner . lease_until|
  |             budget_cap . budget_used                          |
  | run_steps   the current plan and every superseded one         |
  | activities  what ran, what it returned, what it cost          |
  | run_signals out-of-band control                               |
  | approvals   gate questions and signed answers                 |
  | budget_ledger  reserved and settled                           |
  |                                                              |
  | + SHORT-TERM MEMORY -- session scratch, dies with the run     |
  |                                                              |
  | MUST NOT CONTAIN: a merged branch . an invoice . a customer   |
  +--------------------------------------------------------------+

  MODEL STATE                          NOT PERSISTED AS TRUTH
  +--------------------------------------------------------------+
  | system prompt (from harness)                                  |
  | + long-term memory (from harness)                             |
  | + loaded skills (from harness)                                |
  | + conversation history (PROJECTED from run state)             |
  | + tool results (PROJECTED from activities)                    |
  | + middleware injections (computed)                            |
  | = the assembled context, plus a cache prefix and a token      |
  |   budget                                                      |
  |                                                              |
  | reconstructible from the four rows above; therefore derived   |
  +--------------------------------------------------------------+

  HARNESS STATE                        versioned, git-backed
  +--------------------------------------------------------------+
  | systemprompt.md . LongTermMEMORY.md                           |
  | tool_descriptions/ . tools/ . middleware/ . skills/           |
  | sub_agents/ . agent.yaml                                      |
  |                                                              |
  | MUST NOT CONTAIN: anything tenant-specific.                   |
  |                   See the cold open.                          |
  +--------------------------------------------------------------+

  Figure 6.2 -- What belongs where (D2 Low-Level Architecture)
```

Each block's "MUST NOT CONTAIN" line is a CI check in §13.1, not a wish.

---

## 5. The Four Categories

### 5.1 Domain state — what is true

`[DAR §3.3]`, reproduced as a contract:

| Property | Value |
|----------|-------|
| Answers | What is true? |
| Examples | the balance, the merged branch, the shipped order, the customer record |
| Owner | your domain |
| Lifetime | permanent |
| Consistency | strong, transactional, invariant-guarded |
| On deleting the runtime | unaffected |

**In Atlas:** the pull request exists. The branch was pushed. The customer is on the enterprise plan.
These remain true whether or not a run ever executed, and they would be equally true if a human had
done the work by hand — which is a serviceable test on its own.

### 5.2 Run state — what is happening

| Property | Value |
|----------|-------|
| Answers | What is happening? |
| Examples | the current step, the plan, the lease, the attempt count, the budget spent |
| Owner | the runtime |
| Lifetime | ends with the run |
| Consistency | eventually consistent, checkpointed, recoverable |
| On deleting the runtime | gone, and correctly so |

**The structural test** `[DAR §3.3]`: no run state may live on a domain aggregate — no current step,
no lease, no retry count, no plan id — and no domain truth may live in the run.

`[INF]` **Short-term memory is run state.** In the AHE workspace it is session-scoped scratch managed
by the running agent, and it is explicitly excluded from the evolution loop's editable set
`[AHE App. B.2]`. That exclusion is a state-separation decision wearing a permissions costume:
short-term memory dies with the run, so an evolution loop reasoning across runs has no business
touching it.

### 5.3 Model state — what the model sees right now

`[INF]` The handbook's third category, and the one most likely to be argued with, so here is the
argument.

| Property | Value |
|----------|-------|
| Answers | What does the model see on this call? |
| Examples | assembled context, cache prefix, token budget, reasoning effort |
| Owner | the context system (Chapter 11) |
| Lifetime | one model call |
| Consistency | none — it is derived |
| On deleting the runtime | irrelevant; it is rebuilt |

**Why it is not run state.** Run state is authoritative and checkpointed. Model state is a
*projection* of run state, harness state, and domain facts, assembled for one consumer. Two runs at
identical checkpoints must produce identical run state; they need not produce identical assembled
context, because assembly depends on token budgets, compaction thresholds, and which skills the
loader judged relevant.

**Why this matters more than it sounds.** The `messages` list feels like the run's state — it is the
thing you print when debugging, and it is what a G2 loop actually stored. Persisting it as
authoritative has three consequences, and the third is fatal:

1. It becomes a second source of truth that can disagree with `run_steps` and `activities`.
2. It grows without bound, because nothing owns pruning it.
3. **Replay stops working.** Resumption is sound only because orchestration is a function of state
   and events `[DAR §6.1]`. If the model's view is stored rather than derived, you cannot reconstruct
   it after a compaction-policy change, and a replayed run diverges from the recorded one for reasons
   that have nothing to do with the model.

**The framing that makes it obvious.** `[INF]` The assembled context is a **read model for the
model** — exactly the same category as the read models the edge builds for humans (Chapter 7). Both
are projections. Neither is authoritative. Nobody would store a dashboard's rendered HTML as the
source of truth for an account balance; storing the message list as the source of truth for a run is
the same error with better camouflage.

### 5.4 Harness state — what the system has learned to do

`[INF]` The fourth category. Neither source names it, and the cold open is what its absence costs.

| Property | Value |
|----------|-------|
| Answers | What has the system learned to do? |
| Examples | long-term memory, prompts, tool code, middleware, skills |
| Owner | the harness, and whoever is permitted to edit it |
| Lifetime | across runs, until edited |
| Consistency | versioned; git-backed, one commit per logical edit `[AHE §3.1]` |
| On deleting the runtime | **survives** — and is not domain truth |

**It fails both halves of the two-category test.** Delete the runtime and long-term memory is still
there, so it is not run state. But it is not domain truth either — a customer's product is entirely
coherent without it, and no invariant depends on it. It sits in the gap, and things in the gap get
scoped by nobody.

**The short-term / long-term split is exactly the run/harness boundary.** The AHE workspace holds
both: short-term memory managed by the running agent, long-term memory as persistent cross-session
knowledge that the evolution loop may modify `[AHE App. B.2]`. Two files, two categories, two owners,
two lifetimes. That the source separates them at the file level without naming the underlying
distinction is reasonable — it did not need the distinction, because it had one tenant and one
benchmark.

**You have more than one tenant.**

### 5.5 The rule the cold open needed

`[INF]` One line, and it belongs in every harness review:

> **Harness state must be true of the system, never of a customer.**

"Test suites in this codebase need a database URL set" is a fact about a customer. "Check whether the
test harness requires environment configuration before assuming a suite failure is a code defect" is
a fact about the system. The second is the same lesson with the tenant removed, and it is *more*
useful, because it generalises.

Note what this implies. Lessons must be **abstracted before they are written**, not filtered when
they are read. Filtering at read time fails because the leak has already been committed to a
versioned file, and Chapter 37 has to treat that file as a data-retention surface. Chapter 12 puts
the abstraction step in the memory write path, where it can be tested.

---

## 6. Runtime Sequence

One step, with every state category touched marked.

```
                                                              TIME VIEW

  STEP 7 of run r-8f2: ask the model to revise a failing patch

  (1) driver claims the lease
         READS  run state    runs row: version, plan_id, current_step
         WRITES run state    lease_owner, lease_until, version+1
         ~5 ms, one connection, released immediately

  (2) context assembly
         READS  harness      systemprompt.md, LongTermMEMORY.md,
                             skills judged relevant
         READS  run state    run_steps for the plan,
                             activities for prior results
         READS  domain       repo metadata via a query port
                             (a fact, fetched -- not owned)
         BUILDS model state  ~120 KB assembled context + cache prefix
         PERSISTS            nothing

  (3) the model call
         CONSUMES model state
         PRODUCES a completion
         model state is now DISCARDED

  (4) result handling
         WRITES run state    activities row: result, cost settled
         WRITES run state    events row: << activity.completed >>
         one transaction

  (5) memory consideration
         the middleware judges whether a durable lesson was learned
         IF SO -> WRITES harness state, abstracted, tenant-free
         (in Atlas this is a queued proposal, not a direct write --
          see Ch 12)

  (6) checkpoint
         WRITES run state    current_step, version+1, lease renewed
         READS  run state    pending signals, same transaction
         ~5 ms

  Figure 6.3 -- State touched by one step (D4 Sequence)
```

Two observations.

**Step (2) reads three categories and persists none.** Assembly is a pure projection. If it were not,
step (3) could not be replayed.

**Step (5) is the only place a run writes harness state,** and in Atlas it does not write it directly.
`[INF]` A run that can append to a versioned, cross-tenant, cross-run file at will is a run that can
poison every future run in the system. Chapter 12 routes it through a proposal queue with the
abstraction rule of §5.5 applied as a check.

---

## 7. State Lifetimes

```
                                                             STATE VIEW

  time ------------------------------------------------------------->

  DOMAIN     |=================================================...
             created                                       forever

  HARNESS    |==========|          |=====================...
             v1         v2 (edited between runs)
                        ^ version bump; old version recoverable

  RUN        .....|===================================|.......
                  founded                        terminal
                  |  |  |  |  |  |  |  |  |  |  |
                  checkpoints -- recoverable at each

  MODEL      ......|.|.....|.|........|.|.......|.|..........
                   ^ ^     ^ ^        ^ ^       ^ ^
                   one per model call; discarded immediately

  PARK       ...........|=========================|..........
                        run state persists,
                        model state does not exist,
                        no resource held

  Figure 6.4 -- Lifetimes, to scale (D6 State Diagram)
```

`[INF]` The park band is the one to study. During a six-hour park, domain state is untouched, run
state sits in a row, harness state may be edited *underneath the parked run*, and model state does
not exist.

That third item is a real hazard and neither source addresses it: **a run can park under harness v1
and resume under v2.** The plan it committed was produced by a prompt that no longer exists, and the
tool it is about to call may have different behaviour. Chapter 38 gives the rule — pin the harness
version on the run row at founding, and resume against the pinned version — but the reason the rule
is needed is visible right here, in a lifetime diagram.

---

## 8. Internal APIs

Who may write what.

| Writer | Domain | Run | Model | Harness |
|--------|--------|-----|-------|---------|
| Edge | via command port | founding only | — | — |
| Run driver | — | yes | — | — |
| Activity runner | via command port | yes (results, cost) | assembles, discards | proposals only |
| Ports (planner, grader) | — | — | reads | reads |
| The model | **never directly** | **never directly** | — | **never directly** |
| Human operator | via the product | signals and approvals | — | reviewed edits |
| Evolution loop | **never** | reads only | — | **yes — this is its action space** |

The two "never" rows for the model are the safety model restated in state terms. A model produces
*proposals*; the runtime decides whether a proposal becomes a write. Every gate, schema check, and
grader in this book is an implementation of that row.

The bottom row is Chapter 4 §14 in state terms: the evolution loop's entire action space is one
column `[AHE §3.3]`.

---

## 9. Data Structures

| Category | Where it lives | Versioned | Tenant-scoped by |
|----------|---------------|-----------|------------------|
| Domain | your tables | by your rules | your domain's own enforcement |
| Run | the eight runtime tables | by `version` (CAS) | `runs.tenant_id` |
| Model | memory, for one call | no | inherited from the run |
| Harness | a git-backed workspace | by commit | **nothing, by default — this is the gap** |

That last cell is the cold open in one word: *nothing*. Chapter 37 closes it, and the options are
worth previewing — a per-tenant memory namespace, a shared memory with a mandatory abstraction check,
or both. Atlas uses both, because the abstraction check is what keeps the shared namespace useful and
the namespace is what limits the damage when the check misses.

---

## 10. Communication

```
                                                            LAYER VIEW

  HARNESS ======> MODEL STATE        prompt, memory, skills
                                     ~8-20 KB, every call

  RUN STATE ====> MODEL STATE        history, prior results
                                     ~30-150 KB, grows with the run

  DOMAIN =======> MODEL STATE        facts, fetched through a port
                                     ~1-10 KB, on demand

  MODEL STATE ==> the model          the assembled context
                                     50-200 KB   <-- the dominant flow

  the model ====> RUN STATE          a completion, becoming an
                                     activity result
                                     5-50 KB

  RUN STATE ====> DOMAIN             a COMMAND, and only after a gate
                                     ~1 KB

  RUN STATE ====> HARNESS            a memory PROPOSAL, abstracted
                                     ~200 bytes, rare

  DOMAIN =======> RUN STATE          an EVENT, in the same transaction
                                     as the change
                                     ~1 KB

  Figure 6.5 -- Flows between categories (D7 Data Flow)
```

`[INF]` The asymmetry is the design. **Everything flows *into* model state and almost nothing flows
out of it** — one completion, which immediately becomes run state. And the two flows that cross into
durable, shared territory are the two narrowest: a command into the domain (gated) and a proposal
into the harness (abstracted). The system is deliberately generous about what the model may see and
miserly about what it may change.

---

## 11. Failure Modes

| Failure | Category error | Symptom | Detection |
|---------|---------------|---------|-----------|
| Lease on a domain aggregate | run → domain | Deleting the runtime leaves dangling columns; domain locks held across model calls | Schema check; the 3am incident of Ch 4 |
| Domain truth in the run row | domain → run | Truth vanishes when a run is pruned | Retention job reveals it |
| Message list persisted as truth | model → run | Replay diverges after a compaction change; unbounded growth | Golden-set replay mismatch (Ch 41) |
| Context cached across runs | model → harness | One tenant's context primes another's call | Cache-key audit |
| **Tenant fact in long-term memory** | domain → harness | **The cold open** | Abstraction check at write; scanning at read |
| Credential in a harness file | domain → harness | Secret in version control, permanently | Secret scanning in CI |
| Harness edited under a parked run | version skew | A run resumes against tools its plan never saw | Pin the harness version at founding (Ch 38) |
| Short-term memory outliving a run | run → harness | Cross-run contamination of scratch | Lifetime assertion in tests |

### 11.1 Why the harness leak is the worst of them

`[INF]` Rank these by damage and the memory leak wins, for four reasons that compound:

- **It is durable.** A bad run ends. A bad memory entry is committed to a versioned file and applies
  to every subsequent run.
- **It is cross-tenant by construction.** Run state and domain state are scoped; harness state, by
  default, is not.
- **It is invisible.** Nothing errors. The memory component is doing exactly what it was built to do,
  and doing it well is what causes the harm.
- **It is amplified by Level 5.** An evolution loop reads trajectories and writes memory
  `[AHE §3.1]`. If tenant facts are in the trajectories, and the loop is rewarded for encoding
  specific hard-won knowledge — which the ablation shows is precisely what makes memory valuable
  `[AHE §4.4.1]` — then the loop is being optimised toward the leak.

That last point deserves to be stated plainly, because it is a genuine tension rather than a bug:
**the property that makes long-term memory the highest-value component is the same property that
makes it the highest-risk one.** Specificity is the value. Specificity is the leak. Chapter 12 and
Chapter 37 split the difference with the abstraction rule; there is no version of this where you get
the value without managing the risk.

---

## 12. Scalability

| Category | Grows with | Bounded by | Pruning |
|----------|-----------|-----------|---------|
| Domain | Your product's success | Your product's design | Yours |
| Run | Concurrent and historical runs | Retention policy | **Required** — Ch 37 |
| Model | Nothing; rebuilt each call | Context window and token budget | Compaction, Ch 11 |
| Harness | Edits, not usage | Nothing, by default | **Required and usually absent** |

`[INF]` Two unbounded-by-default rows, and they fail differently.

**Run state grows with volume** and the failure is operational — a table that is slow to query and
expensive to store. It is boring, visible, and gets fixed.

**Harness state grows with edits** and the failure is behavioural. A long-term memory that has
accumulated four hundred lessons is not slow; it is *worse*. Every lesson rides into context on every
call, the useful ones are diluted, and the ablation's Easy-tier result shows the mechanism — memory
that helps on hard tasks reduces to superfluous re-verification on simple ones `[AHE §4.4.1]`.

Harness state therefore needs a curation policy in the way that run state needs a retention policy,
and the AHE loop's own design anticipates this: components carry no special protection, and the
evolution agent may keep, refine, or remove them based on observed rollouts `[AHE §3.3]`. Removal is
a first-class operation. Chapter 49 argues it is the one most often left unimplemented.

---

## 13. Production Engineering

### 13.1 The four checks, in CI

`[INF]` Each of these is a genuine test, not a review guideline. Together they are perhaps two hundred
lines and they catch the entire failure table in §11.

| Check | Implementation |
|-------|----------------|
| **The deletion test** | In a test database, drop the runtime schema. Run the domain's full test suite. It must pass. |
| **The column-name check** | Assert no domain table has a column named `current_step`, `lease_owner`, `lease_until`, `plan_id`, `attempt_count`, `budget_used`, or `run_state`. |
| **The import-graph check** | Domain imports nothing from the runtime. The kernel imports nothing from the domain. |
| **The harness-tenancy check** | Scan every harness file for tenant identifiers, hostnames, credentials, and customer names. Fail the build on a match. |

The fourth is the cold open's fix and the one nobody has. It is a regex pass over eight files.

### 13.2 Best practices

- **Run the classification procedure (§2.2) over your whole schema once,** and record the answer per
  field. Disagreements found in that session are cheap; found in production they are the cold open.
- **Derive model state, always.** If you are tempted to cache the assembled context, cache the
  *prefix* for provider-side reuse and rebuild the rest.
- **Abstract before writing to memory, not when reading it.** A leak filtered at read time has
  already been committed.
- **Pin the harness version on the run row at founding.** Parks make version skew inevitable, not
  hypothetical.
- **Give harness state a curation policy on the day you give it a write path.**

### 13.3 Trade-offs

| Choice | Buys | Costs |
|--------|------|-------|
| Deriving model state every call | Sound replay; no drift | Assembly cost per call; a compaction policy to maintain |
| Per-tenant memory namespaces | Leak containment | Lessons do not generalise across customers |
| Shared memory with abstraction | Lessons generalise; fewer, better entries | An abstraction step that can fail silently |
| Pinning harness version per run | Reproducible parks and replays | Old versions must remain loadable |
| Aggressive memory curation | Signal stays high | Genuine lessons can be pruned by a policy that cannot tell |

### 13.4 Anti-patterns

| Anti-pattern | Why it fails | Diagnosed in |
|--------------|-------------|--------------|
| **The convenient column** | `current_step` on a domain aggregate; the runtime is no longer removable | §5.2 |
| **The persisted transcript** | Model state stored as truth; replay diverges | §5.3 |
| **The unscoped lesson** | Harness state true of a customer rather than of the system | §5.5 |
| **Read-time filtering** | The leak is already in a versioned file | §13.2 |
| **The memory that only grows** | Dilution, and superfluous re-verification on easy work | §12 |
| **Version skew across a park** | A run resumes against a harness its plan never saw | §7 |

---

## 14. Relation to AHE

State separation is what makes attribution possible, and this chapter names two places where the
published loop's assumptions do not survive contact with a multi-tenant product.

**Attribution requires that only one category changed.** The AHE loop measures a pass-rate delta
between iterations and attributes it to the harness edits of the round `[AHE §3.3]`. That inference
is valid only if nothing else moved. The loop enforces this by holding the base model fixed and
making the tracer, verifier, and model configuration read-only. In this chapter's vocabulary:
**harness state is the independent variable, and run state, domain state, and model state must be
controlled.** A benchmark gives you that for free — fresh sandboxes, no domain, no tenants
`[AHE App. A]`. A production system does not, and Chapter 47 has to work harder for the same
conclusion.

**The loop's action space is exactly one column of §8.** It writes harness state and reads run state.
It never writes run state or domain state, which is what keeps every recorded gain attributable to
harness edits rather than to a disabled verifier or a raised reasoning budget `[AHE §3.3]`.

**And the gap the loop inherits.** `[INF]` AHE's memory component is unscoped because it does not need
scoping — one benchmark, no tenants, no customer data in the traces. Port that design into a
multi-tenant product unchanged and you have built the cold open deliberately. This is not a criticism
of the source; it is the single most important adaptation a reader must make when taking Level 5 into
production, and Chapter 43 states it as a precondition rather than a caveat.

---

## 15. Industry Perspective

### Supported by the attached Durable Runtime architecture `[DAR]`

- Domain state and run state as distinct categories, with their answers, examples, owners, lifetimes,
  consistency models, and deletion behaviour (§3.3).
- The structural test: no run state on a domain aggregate — no current step, lease, retry count, or
  plan id — and no domain truth in the run (§3.3).
- The consequence that merged state makes the architecture's guarantees unenforceable (§3.3).
- Orchestration being a function of state and events, which is what makes resumption sound (§6.1).
- Commands and events as the only messages crossing between the runtime and a domain (§3.2).
- Parks holding no resource while run state persists (§8.2).

### Supported by the attached AHE paper `[AHE]`

- Long-term memory as persistent cross-session knowledge, modifiable by the evolution agent;
  short-term memory as session scratch, excluded from the editable set (App. B.2).
- One commit per logical edit, giving file-level diffs and rollback granularity (§3.1).
- Components carrying no special protection; the evolution agent may keep, refine, or remove them
  (§3.3).
- Controllability: workspace-only writes, with runs, tracer, verifier, and model configuration
  read-only, keeping gains attributable (§3.3).
- Memory's value coming from specific boundary-case lessons; the same lessons reducing to superfluous
  re-verification on easy tasks (§4.4.1).
- Fresh isolated sandboxes per rollout (App. A).

### Engineering inference `[INF]`

- Model state and harness state as the third and fourth categories, and the argument for each.
- The four-question classification procedure.
- The assembled context as a read model for the model, in the same category as the edge's read models
  for humans.
- The claim that persisting the message list as truth breaks replay specifically, not merely
  hygiene.
- The rule that harness state must be true of the system and never of a customer, with abstraction at
  write time rather than filtering at read time.
- Harness state as unscoped by default, and this being the gap through which the cold open occurs.
- Version skew across a park, and pinning the harness version at founding.
- The tension that specificity is simultaneously long-term memory's value and its risk, amplified by
  an evolution loop optimising for it.
- Harness state needing a curation policy the way run state needs a retention policy.
- The four CI checks in §13.1.

### Industry best practice `[BP]`

- Secret scanning in CI over any file committed to version control.
- Schema-level assertions as a guard against ownership drift between services.
- Per-tenant namespacing of any shared mutable store.

### Future proposal `[FUT]`

- None in this chapter. The tenancy treatment of harness state is developed in Chapter 37 and remains
  within established practice.

---

## 16. Key Takeaways

1. **Four categories, not two.** Domain, run, model, and harness. The reference architecture names
   two; the other two are where the interesting failures live.
2. **Ask four questions in order.** Survives deleting the runtime → domain. Outlives the run without
   being a fact about the world → harness. Reconstructible from stored facts → model, so derive it.
   Otherwise → run.
3. **Each category has exactly one owner, and the owner scopes it.** State belonging to no category is
   scoped by nobody, which is the cold open.
4. **The assembled context is a read model.** Persist it as truth and replay stops working — not as
   a hygiene concern, as a mechanism.
5. **Harness state must be true of the system, never of a customer.** Abstract at write time;
   filtering at read time is already too late.
6. **The most valuable component is the riskiest one.** Specificity is what makes long-term memory
   work and what makes it leak, and an evolution loop optimises directly toward it.
7. **Four CI checks catch the whole failure table.** Deletion test, column names, import graph,
   harness tenancy. About two hundred lines.

---

**Next:** Chapter 7 — *The Edge and the Client Contract.* The layer where goals enter, approvals
arrive, and progress leaves — and the three ways teams put a loop in it anyway.
