```
  Level 1 · Chapter 5
  THE FIVE NOUNS: RUN, EPISODE, STEP, ACTIVITY, PARK
  Requires   C4 The Complete Runtime
  Unlocks    C6 State Separation, C8 Lifecycles, C17 State Manager,
             C18 The Runtime Loop, C21 Durable Execution
  Diagrams   Core (5)
```

# Chapter 5 — The Five Nouns: Run, Episode, Step, Activity, Park

---

## 1. Motivation

### 1.1 Cold open

`#atlas-incidents`, 09:41. A customer's automation has produced nothing for two hours.

> **support:** the agent is stuck on `acme/billing-service`

Four people read that sentence and start four different investigations.

The first checks the model provider's status page, because "stuck" means a hanging call. The second
greps the worker logs for exceptions, because "stuck" means a crash loop. The third queries for
long-held leases, because "stuck" means a worker died holding one. The fourth opens the approvals
table, because "stuck" means somebody has not clicked a button.

Forty minutes later the fourth one is right. A gate was raised at 07:38 and the customer's tech lead
is on a flight. Nothing is wrong. The system is doing precisely what it was built to do — waiting,
indefinitely, holding nothing — and there was no word available that said so.

Three engineers spent forty minutes each because one sentence contained a noun that means five
things.

### 1.2 Why this chapter exists

Chapter 4 gave you the layers. This chapter gives you the units those layers manipulate, and it is
the shortest chapter in Level 1 with the longest tail: **every subsequent chapter is written in this
vocabulary.**

Five nouns `[DAR §3.1]`. Each exists because it has a distinct lifetime and a distinct relationship
to scarce resources, and no two can be merged without losing a property the architecture depends on.
By the end you should be able to replace "the agent is stuck" with a sentence that names which noun,
in which state, and therefore what to do.

### 1.3 What previous framings got wrong

**"The agent is the unit."** It is not a unit at all. It is a category error that averages five
things with lifetimes spanning nine orders of magnitude, from a millisecond step to a park that can
outlast a quarter. Chapter 3's naming conventions ban the word for this reason, and this chapter is
the justification.

**"A run is a job."** The Chapter 3 cold open. A job is owned by a worker; a run is a row that
workers borrow. The distinction determines whether you hold the lease for the duration.

**"Steps and turns are the same thing."** A model turn is a conversational unit; a step is an advance
of a state machine. Section 5.6 maps between them, and they do not line up one to one.

---

## 2. High-Level Mental Model

### 2.1 The table that is the whole chapter

| Noun | Lifetime | Holds | Scarcity of what it holds |
|------|----------|-------|--------------------------|
| **Run** | minutes to weeks | one row | abundant |
| **Park** | unbounded | one row | abundant |
| **Activity** | seconds to minutes | a semaphore slot, a budget reservation | scarce (4–6 slots) |
| **Episode** | seconds | one worker | scarce (8–16 workers) |
| **Step** | milliseconds | one database connection, briefly | very scarce (a pool of 20) |

Read the two right-hand columns together and the design falls out.

### 2.2 The custody gradient

`[INF]` The organising principle of this chapter, and a prediction machine for the rest of the book:

> **Scarcity times duration is held roughly constant. The longer a noun lives, the less scarce the
> thing it is permitted to hold.**

A Step holds the scarcest resource in the system — a pooled connection — for about five milliseconds.
An Episode holds a worker for sixty seconds. An Activity holds one of a handful of model slots for a
minute or two. A Run holds a row for a week, and a Park holds a row for as long as a human takes.

Nothing violates the gradient, and every violation you will be tempted to commit is a case of moving
one noun up and to the right: holding a connection across a model call (Step's resource, Activity's
duration), or holding a lease across a park (Episode's resource, Park's duration). Both are the same
mistake, and the gradient names it before you make it.

This is Chapter 2's custody rule `[DAR §5.2]` generalised from one rule about connections into a
property of the whole noun set.

### 2.3 Why not fewer nouns

Each merge that looks tempting, and what it costs:

| Merge | Loses |
|-------|-------|
| Run + Episode | The ability to advance a run on any worker. The run becomes pinned. |
| Episode + Step | Prompt-cache locality and a queue hop per step, for no durability gain (§5.2) |
| Step + Activity | The determinism quarantine. Non-determinism spreads into orchestration `[DAR §6.1]` |
| Activity + Run | Identity. A result could never be replayed independently of the run's position |
| Park + anything | The ability to wait indefinitely while holding nothing |

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  RUN  ................................. one goal, minutes to weeks
  +----------------------------------------------------------------+
  |                                                                |
  |  EPISODE ....... seconds        EPISODE            EPISODE     |
  |  +---------------------+     +-------------+    +-----------+  |
  |  |                     |     |             |    |           |  |
  |  | STEP STEP STEP STEP |     | STEP  STEP  |    |  STEP     |  |
  |  |  |    |    |    |   |     |  |     |    |    |   |       |  |
  |  |  o    o    A    o   |     |  A     o    |    |   o       |  |
  |  +---------------------+     +-------------+    +-----------+  |
  |          |                       |                             |
  |          |  worker released      |  worker released            |
  |          v                       v                             |
  |     (re-enqueued)          PARK ..........................     |
  |                            +---------------------------+       |
  |                            | holds NOTHING             |       |
  |                            | one row, unbounded time   |       |
  |                            | resolved by an event      |       |
  |                            +---------------------------+       |
  +----------------------------------------------------------------+

     o = a decision step: cheap, in-process, no dispatch
     A = an ACTIVITY step: leased, budgeted, abortable, quarantined

  cardinality
     1 Run     : N Episodes   sequential, NEVER concurrent
     1 Episode : 1..8 Steps   bounded by the step budget
     1 Step    : 0..1 Activity
     1 Run     : N Parks      sequential
     1 Activity: 0..N executions, exactly 1 billed

  Figure 5.1 -- Nesting and cardinality (D1 High-Level Architecture)
```

The two structural facts worth memorising: **episodes are sequential, never concurrent** — exactly
one driver advances a run at any instant `[DAR §13]` — and **a park sits between episodes, not inside
one**. A park is what an episode exits into, which is why it can hold nothing: the worker is already
gone.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  RUN                              row in [[ runs ]]
  +--------------------------------------------------------------+
  | id . tenant_id . goal . state . plan_id . current_step        |
  | version   <-- CAS: exactly one advance commits                |
  | lease_owner . lease_until   <-- who is driving, until when    |
  | budget_cap . budget_used    <-- the ceiling and the spend     |
  +--------------------------------------------------------------+

  EPISODE                          NOT a row. A function invocation.
  +--------------------------------------------------------------+
  | claim the lease            (milliseconds, release connection) |
  | loop:                                                         |
  |   advance one step         (no connection held)               |
  |   checkpoint               (~5ms: CAS, renew lease, release)  |
  |   read pending signals     (same transaction -- free)         |
  |   test exit conditions                                        |
  | exit on E1 wall clock . E2 step budget . E3 park . E4 signal  |
  | final checkpoint, release lease, re-enqueue if not terminal   |
  +--------------------------------------------------------------+

  STEP                             row in [[ run_steps ]]
  +--------------------------------------------------------------+
  | run_id . plan_id . step_id . seq . tool_id . input            |
  | activity_id   <-- computed at PLAN time, not dispatch time    |
  | status                                                        |
  | a replan writes NEW rows; it never edits old ones             |
  +--------------------------------------------------------------+

  ACTIVITY                         row in [[ activities ]]
  +--------------------------------------------------------------+
  | activity_id  = hash(run_id, plan_id, step_id, tool_id,        |
  |                     input_digest)          <-- PK             |
  | state . result . attempts                                     |
  | lease_owner . lease_until                                     |
  | the single source of "has this already run, and what did it   |
  | cost?"                                                        |
  +--------------------------------------------------------------+

  PARK                             NOT a table. A run state plus a
                                   resolution condition.
  +--------------------------------------------------------------+
  | runs.state = PARKED                                           |
  | plus ONE of:                                                  |
  |   a row in [[ approvals ]]      awaiting a human decision     |
  |   a row in [[ approvals ]]      awaiting a budget grant       |
  |   a pending question            awaiting missing input        |
  |   a scheduled wake time         awaiting a timer              |
  |   an expected external event    awaiting a callback           |
  +--------------------------------------------------------------+

  Figure 5.2 -- Each noun, decomposed (D2 Low-Level Architecture)
```

`[INF]` Note which nouns are rows and which are not. Run, Step, and Activity are durable records.
Episode is a function invocation that leaves only its side effects. Park is a *state*, not an entity
— which is why `[DAR §8.2]` can describe five different waits as one construct.

That asymmetry is deliberate and worth stating: **you cannot query for episodes.** If you want to
know how many steps an episode ran, you infer it from checkpoint timestamps. Chapter 34 makes
steps-per-episode a metric precisely because it is otherwise invisible, and a distribution with a
mode at one means you have lost the loop `[DAR §15]`.

---

## 5. The Five Nouns

### 5.1 Run — one goal under execution

> One goal under execution. The durable, versioned unit — the runtime's equivalent of a process
> `[DAR §3.1]`.

**Lifetime:** minutes to weeks. **Holds:** a row.

**In Atlas:** one labelled issue in one repository. `AtlasGoal(tenant_id, repo_ref, issue_id,
base_branch, budget_cap)`.

**What makes it the unit.** It is the only noun that is durable, addressable from outside, and
versioned. You submit a run, stream a run, signal a run, cancel a run. Everything else in this
chapter is internal machinery that a caller never names.

**The property that matters most:** a run holds nothing but a row, so it costs nothing to have ten
thousand of them, and almost all of them can be doing nothing at any given moment.

### 5.2 Episode — one bounded execution window

> One bounded execution window over a Run. Many steps, one worker invocation, a checkpoint after each
> step `[DAR §3.1]`.

**Lifetime:** seconds. **Holds:** one worker.

**Why it exists — the tension it resolves.** This is the noun that most often gets designed away, so
the argument is worth having in full `[DAR §5.1]`.

Durability wants a checkpoint and a process boundary at *every* step: crash anywhere, lose at most
one step. Responsiveness and prompt-cache economics want a *tight in-process loop*: no queue hop
between steps, no cache prefix rebuilt.

Those pull in opposite directions, and the naive resolutions are both bad. One step per worker
invocation gives perfect durability and pays a queue hop plus a cache miss on every step. An
unbounded in-process loop gives perfect locality and is Chapter 0's G2 — the whole run in memory.

The Episode takes the checkpoint from the first and the loop from the second. Every durability
property is preserved, because a checkpoint still follows every step; what changes is only how often
the queue-hop cost is paid.

**The dial.** Setting the step budget to one reproduces a strict one-step-per-invocation runtime
exactly `[DAR §5.1]`. That is the sentence that makes this a configuration decision rather than an
architectural commitment — you can always turn the loop off, so keeping it costs you nothing in
optionality.

**The four exit conditions.** Wall-clock budget spent (default 60s), step budget spent (default 8), a
durable park required, or a signal has arrived `[DAR §5.1]`. Chapter 18 develops each.

### 5.3 Step — one advance of the state machine

> One advance of the Run's state machine: either a cheap decision, or the dispatch of an Activity
> `[DAR §3.1]`.

**Lifetime:** milliseconds to seconds. **Holds:** a connection, for about five milliseconds, at the
checkpoint.

**Two kinds, and the distinction is load-bearing:**

| Kind | Does | Costs | Example in Atlas |
|------|------|-------|------------------|
| **Decision step** | Advances state using only what is already known | microseconds; no model call | route to the next planned step; mark a check passed |
| **Activity step** | Dispatches an Activity and lets go | the Activity's cost | run the test suite; ask the model for a patch |

A decision step is why the fast queue exists. Most steps in a healthy run are decisions, and if they
had to queue behind model calls the control plane would move at data-plane speed.

**A replan writes new step rows and edits none** `[DAR §11]`. Steps are history, not working state.

### 5.4 Activity — the quarantine

> One idempotent, leased, cancellable, budgeted invocation of a Tool. All non-determinism lives here
> `[DAR §3.1]`.

**Lifetime:** seconds to minutes. **Holds:** a semaphore slot and a budget reservation.

Five properties, none optional:

| Property | Means | Without it |
|----------|-------|-----------|
| **Idempotent** | Re-claim replays the stored result | A retry re-spends and re-rolls |
| **Leased** | One runner owns it; expiry makes a crash recoverable | A dead runner's work is stranded |
| **Cancellable** | A deadline or signal aborts the real call | A timeout leaks the operation `[DAR §5.5]` |
| **Budgeted** | Cost reserved at dispatch, settled at completion | A run exceeds its ceiling by everything in flight |
| **Quarantined** | The only place non-determinism is permitted | Replay stops being sound `[DAR §6.1]` |

**Identity is computed at plan time, not dispatch time** `[DAR §6.2]`, so it is auditable and dispatch
cannot silently disagree with planning about what a step is. Chapter 21 gives the full rule and the
failure it prevents.

### 5.5 Park — the general waiting primitive

> A durable pause that holds no resource: awaiting an approval, an answer, a timer, or a budget grant
> `[DAR §3.1]`.

**Lifetime:** unbounded. **Holds:** nothing.

The unification is the point. `[DAR §8.2]` states it directly: parks are the general waiting
primitive, and approvals, missing input, external callbacks, scheduled delays, and budget grants are
all the same construct with different resolution conditions.

| Park reason | Resolved by | Atlas example |
|-------------|-------------|---------------|
| Approval | A human decision event | the tech lead approves the push |
| Missing input | An answer signal | which base branch? |
| External callback | A third-party event | CI finishes on the pushed branch |
| Timer | A scheduled wake | retry the flaky suite in ten minutes |
| Budget grant | A budget decision event | the run hit its ceiling mid-task |

When a run parks it writes the question, transitions to a parked state, releases its lease, and stops
existing as anything but a row — no process, no connection, no in-memory timer `[DAR §8.2]`. The
pause may last an hour, a week, or across a redeploy; the mechanism is identical and requires nothing
to stay running.

**This is what the cold open's fourth engineer found.** A park is not a stall. It is the system's
correct behaviour, and the reason nobody could name it is that the team's vocabulary had no word for
"waiting correctly."

### 5.6 What is deliberately not a noun

| Word | Why not | Say instead |
|------|---------|-------------|
| **Agent** | Averages all five; the cold open | name the noun |
| **Task** | Ambiguous between a goal and a step | Run, or Step |
| **Job** | Implies worker ownership | Run |
| **Session** | Implies a connection | Run |
| **Conversation** | Model state, not run state | assembled context |
| **Turn** | A model-loop unit, not a state-machine advance | see below |

`[INF]` **Turn versus Step**, because the mismatch confuses people who arrive from agent frameworks:

```
  ONE MODEL TURN                     MAPS TO
  ------------------------------     ---------------------------------
  model emits a tool request         1 Activity step (the model call)
  runtime executes the tool          1 Activity step (the tool call)
  result appended to history         1 decision step (append, route)

  so: one "turn" is typically 2-3 Steps, and may span an episode
      boundary if the step budget runs out between them
```

A turn is a unit of conversation. A step is a unit of durability. They are not the same size and
they do not nest cleanly, which is why the handbook counts steps.

---

## 6. Runtime Sequence

One Atlas run, with the noun boundaries marked.

```
                                                              TIME VIEW

  RUN r-8f2 founded                                 state: CREATED
  |
  +-- EPISODE 1 ............... worker w-3 claims the lease
  |   |
  |   +-- STEP 1  decision   route to planning       ~2 ms
  |   +-- STEP 2  ACTIVITY   planner.plan()          1.4 s   $0.02
  |   |            checkpoint: plan committed        state: EXECUTING
  |   +-- STEP 3  ACTIVITY   tool.repo.search        0.3 s   $0.00
  |   +-- STEP 4  ACTIVITY   model: propose a patch  38 s    $0.41
  |   +-- STEP 5  decision   grader: patch applies?  ~4 ms
  |   +-- STEP 6  ACTIVITY   tool.test.run_suite     52 s    $0.00
  |   +-- STEP 7  decision   grader: 3 tests fail    ~4 ms
  |   +-- STEP 8  decision   planner: replan
  |   |            NEW plan_id -> new step rows, old rows untouched
  |   |
  |   EXIT E2: step budget spent. Final checkpoint. Lease released.
  |   Run re-enqueued. Worker w-3 is now free for any other run.
  |
  +-- EPISODE 2 ............... worker w-11 claims the lease
  |   |                         (a DIFFERENT worker -- this is normal)
  |   +-- STEP 9  ACTIVITY   model: revise the patch 41 s    $0.44
  |   +-- STEP 10 ACTIVITY   tool.test.run_suite     49 s    $0.00
  |   +-- STEP 11 decision   grader: suite passes    ~4 ms
  |   +-- STEP 12 decision   next step is EFFECTFUL
  |   |            tool.repo.push_branch requires a gate
  |   |
  |   EXIT E3: park required. Approval written. Lease released.
  |
  +-- PARK ..................... state: PARKED
  |   |
  |   |   holds: one row
  |   |   duration: 6 h 12 min  (the tech lead was on a flight)
  |   |   survived: two deploys, one worker pool scale-down to zero
  |   |
  |   resolved by << approval.decided >>
  |
  +-- EPISODE 3 ............... worker w-2 claims the lease
      |
      +-- STEP 13 ACTIVITY   tool.repo.push_branch   2.1 s   $0.00
      +-- STEP 14 ACTIVITY   tool.repo.open_pr       1.8 s   $0.00
      +-- STEP 15 decision   terminal                state: SUCCEEDED

  totals: 1 run . 3 episodes . 15 steps . 9 activities . 1 park
          worker time: 3 min 6 s        wall-clock: 6 h 19 min
          spend: $0.87

  Figure 5.3 -- One run through all five nouns (D4 Sequence)
```

Three numbers in that footer carry the chapter.

**Three minutes of worker time across six hours of wall clock.** The ratio is the architecture
working. Almost all of the elapsed time was a park, and a park costs a row.

**Three different workers.** No worker owns the run. Each borrowed it for an episode. If any of them
had died mid-episode, the sweeper would have expired the lease and the next relay wake would have
re-driven from the last checkpoint, losing one step.

**Nine activities, and only the paid ones cost anything.** A replay of any of them — after a crash,
after a re-claim — would return the stored result rather than re-spending. The `$0.87` is a ceiling
on what this run can ever have cost, no matter how many times it was interrupted.

---

## 7. State Management

Each noun has its own state, and only three of them are persisted.

```
                                                             STATE VIEW

  RUN            (persisted -- see Figure 4.5 for the full machine)
     CREATED -> PLANNING -> EXECUTING -> {AWAITING_ACTIVITY | PARKED}
             -> SUCCEEDED | FAILED | CANCELLED | DEAD_LETTERED

  STEP           (persisted)
     +---------+     +-----------+     +-----------+
     | PLANNED |---->| DISPATCHED|---->| COMPLETED |
     +----+----+     +-----+-----+     +-----------+
          |                |
          |                +---------> +-----------+
          |                            | FAILED    |
          +--------------------------> +-----------+
                superseded by a replan  | SUPERSEDED|
                                        +-----------+
     superseded rows are never deleted and never edited

  ACTIVITY       (persisted)
     +---------+     +---------+     +-----------+
     | PENDING |---->| RUNNING |---->| COMPLETED |  result stored,
     +---------+     +----+----+     +-----------+  cost settled
                          |
                          +--------> +-----------+
                          |          | FAILED    |--> attempts++
                          |          +-----------+     |
                          |                            v
                          |          lease expiry  +--------------+
                          +--------> re-claimable  | DEAD_LETTERED|
                                                   +--------------+

  EPISODE        (NOT persisted -- a function invocation)
     entered -> looping -> exited via E1 | E2 | E3 | E4

  PARK           (NOT a separate entity -- runs.state = PARKED
                  plus a resolution condition)

  Figure 5.4 -- State per noun (D6 State Diagram)
```

`[INF]` The rule the diagram encodes: **a noun is persisted if and only if losing it would lose
information you cannot reconstruct.** Run, Step, and Activity all carry facts. An Episode carries
nothing that its checkpoints have not already written, and a Park is a condition rather than a thing.

This is also why Chapter 34's steps-per-episode metric must be derived rather than queried, and why
`[DAR §15]` flags a distribution with a mode at one as a symptom: it means episodes are exiting after
a single step, and you are paying for the loop without getting it.

---

## 8. Internal APIs

How each noun is created, advanced, and ended. Full signatures in Appendix E.

| Noun | Created by | Advanced by | Ended by |
|------|-----------|-------------|----------|
| Run | `submit(goal)` at the edge | a driver taking the lease | a terminal state, or a cancel signal |
| Episode | a driver claiming from the fast queue | its own step loop | one of E1–E4 |
| Step | the planner, at plan time | dispatch, then result | completion, failure, or supersession |
| Activity | a step's dispatch | the runner claiming by id | settle, dead letter, or abort |
| Park | a driver exiting on E3 | — (it does not advance) | a resolution event |

**One asymmetry to notice.** Only Run is addressable from outside the runtime. There is no
`advance_episode()`, no `retry_step()`, no `cancel_activity()` in the public surface. Chapter 3 §8
gave the reason: every additional entry point is another place the one-driver-at-a-time invariant can
be violated. Operators act on runs; the kernel acts on everything else.

---

## 9. Data Structures

| Noun | Table | Primary key | Chapter |
|------|-------|-------------|---------|
| Run | `runs` | `id` | Ch 17 |
| Step | `run_steps` | `(run_id, plan_id, step_id)` | Ch 10 |
| Activity | `activities` | `activity_id` — a hash | Ch 21 |
| Park | `runs.state` + `approvals` or a wake time | — | Ch 30 |
| Episode | **none** | — | Ch 18 |

Note the step table's composite key. It includes `plan_id`, which is what allows a replan to write a
fresh set of rows for the same logical positions without colliding with history `[DAR §11]`.

---

## 10. Communication

```
                                                            LAYER VIEW

  GOAL ===> RUN            one row created; ~1 KB
    |
    v
  RUN ===> EPISODE         run state + pending signals read at claim;
    |                      ~10 KB
    v
  EPISODE ===> STEP        in-process; nothing crosses a boundary
    |
    v
  STEP ===> ACTIVITY       tool_id + resolved inputs + identity;
    |                      ~1-50 KB
    v
  ACTIVITY ===> TOOL       inputs + an abort signal
    |
    v
  TOOL ===> MODEL          ASSEMBLED CONTEXT, 50-200 KB    <-- dominant
    |
    v
  MODEL ===> ACTIVITY      completion, 5-50 KB
    |
    v
  ACTIVITY ===> RUN        result event + settled cost; ~1-10 KB
    |                      appended to the outbox, re-entering at the relay
    v
  RUN ===> PARK            a question; ~1 KB, then silence

  Figure 5.5 -- What each noun passes to the next (D7 Data Flow)
```

The gradient in that diagram runs the opposite way to the custody gradient in §2.2, and the two
together explain the shape of the system: **the nouns that move the most data hold the fewest
resources for the longest, and the nouns that move the least data hold the scarcest resources for the
shortest.** A step moves almost nothing and touches the pool. A model call moves two hundred
kilobytes and touches nothing scarce except a semaphore slot.

---

## 11. Failure Modes

| Noun | Characteristic failure | Detected by | Recovery |
|------|----------------------|-------------|----------|
| **Run** | Stranded — no worker, no lease, no terminal state | Lease expiry sweep `[DAR §14]` | Re-enqueued from the last checkpoint |
| **Run** | Exceeds budget | Reservation exceeds the remaining ceiling | Parks awaiting a budget decision |
| **Episode** | Exits with zero progress, repeatedly | Steps-per-episode distribution with a mode at 1 `[DAR §15]` | Diagnose: budgets, signal storm, or a park loop |
| **Episode** | Two drivers race | Version check returns zero rows | The loser drops its job |
| **Step** | Superseded mid-flight by a replan | Plan identity mismatch at dispatch | The stale dispatch is discarded, not executed |
| **Activity** | Lease expires mid-call | Sweeper | Re-claimable; identity replays rather than re-spends |
| **Activity** | Poison — fails every attempt | Attempt cap | Dead-lettered; the run replans or escalates |
| **Activity** | Identity partial match | Same run and position, different plan or inputs | **Alert, never log** `[DAR §6.2]`; it is silent by nature |
| **Park** | Nobody ever answers | Park age exceeds a policy threshold | Escalation or expiry by policy; never silently abandoned |
| **Park** | Mistaken for a stall | The cold open | Vocabulary, and a dashboard that shows park reason |

### 11.1 The failure the cold open actually was

`[INF]` "Park mistaken for a stall" is a documentation and observability failure, not a runtime one,
and it is worth taking seriously because it is common and cheap to fix. Two changes would have saved
those forty minutes:

- A run-state dashboard that distinguishes `PARKED (awaiting approval, 2h 03m, acme/billing-service,
  approver: j.chen)` from `EXECUTING`.
- A team vocabulary in which "stuck" is not a permitted word in an incident channel.

Chapter 34 makes *time parked, by gate type* a first-class signal, and its stated purpose is to tell
you which approval to remove or delegate `[DAR §15]` — humans as the bottleneck is a measurable
condition, not a vibe.

---

## 12. Scalability

Cardinality at Atlas's target scale: five hundred concurrent runs across forty tenants.

| Noun | Count at any instant | Bounded by |
|------|---------------------|-----------|
| Run | 500 | rows; effectively unbounded |
| Park | ~380 | rows; effectively unbounded |
| Episode | ~12 | fast-class worker concurrency |
| Activity | ~5 | the model semaphore |
| Step | ~1 in a transaction | connection pool |

`[INF]` The distribution is the finding. **At any instant, roughly three quarters of runs are parked
and fewer than three percent are executing.** That is not a sign of a slow system; it is what a
human-supervised architecture looks like, and it is why the parked-holds-nothing property is worth
more than any throughput optimisation in the book.

It also sets your capacity model. You size workers for the *executing* population, not the *live*
population, and the two differ by more than an order of magnitude. A team that sizes for five hundred
provisions forty times what it needs; a team that watches only the executing count is blind to a
gate backlog. Chapter 33 needs both numbers.

---

## 13. Production Engineering

### 13.1 Best practices

- **Ban "the agent" in incident channels and code comments.** Replace with the noun. The cold open is
  the return on that rule.
- **Show park reason and park age on the primary dashboard.** A parked run should never look like a
  stuck one.
- **Derive and alert on steps-per-episode.** A mode at one means you are paying for the loop without
  getting it `[DAR §15]`.
- **Keep episodes short enough that a deploy is boring.** Sixty seconds of wall clock means a rolling
  deploy costs at most one step per in-flight run.
- **Never add a public API below the Run.** Operators act on runs.

### 13.2 Trade-offs

| Choice | Buys | Costs |
|--------|------|-------|
| Larger step budget | Fewer queue hops, better cache locality | Longer to notice a signal; more work in flight during a deploy |
| Smaller step budget | Faster signal response; smaller crash blast radius | A queue hop and a possible cache miss per step |
| Longer lease | Fewer renewals | Slower recovery from a dead worker |
| Shorter lease | Fast recovery | Renewal churn, and false expiry if a step exceeds it |
| Parks for everything that waits | One mechanism, five uses | Every wait needs a resolution event, including timers |

`[INF]` The lease-versus-step-time relationship is the one that bites. If a single step can exceed the
lease duration, the sweeper will expire a lease held by a live worker, and two drivers will briefly
believe they own the run. The version check makes that safe rather than corrupting `[DAR §5.3]`, but
it wastes work. Set the lease to comfortably exceed your slowest *step*, not your slowest *episode*.

### 13.3 Anti-patterns

| Anti-pattern | Why it fails | Diagnosed in |
|--------------|-------------|--------------|
| **"The agent" as a unit** | Averages five lifetimes; the cold open | §1.1 |
| **The pinned run** | Holding a worker or lease for the run's duration; violates the custody gradient | §2.2 |
| **The blocking park** | A thread or timer waiting for a human; a redeploy loses it | §5.5 |
| **The mutable step** | Editing step rows on replan instead of writing new ones; history becomes unreconstructible | §5.3 |
| **The episode with no exit** | Missing one of E1–E4; a run monopolises a worker | Ch 18 |
| **Activity identity from position alone** | The worst bug class in the system; silent and confident | Ch 21 |

---

## 14. Relation to AHE

The evolution loop consumes and produces these nouns, and two mismatches between the source and this
vocabulary are worth naming precisely.

**What AHE calls a rollout is a Run.** The loop generates k traces per task `[AHE §3.2]`, and each
trace is one run's trajectory. The unit of measurement in Level 5 is therefore the unit of execution
in Level 1, which is what makes the two levels composable.

**AHE has no Episode and no Park.** Its runs are unattended and bounded by a per-task timeout of one
hour `[AHE §4.1]`; nothing waits for a human, so nothing needs the general waiting primitive. `[INF]`
This is the clearest illustration of the complementary blind spots identified in Chapter 1 §14.1 —
the evolution research assumes an unsupervised benchmark, and a production system does not have that
luxury. When you add gates to an agent you intend to evolve, you add a noun the published loop has
never had to reason about, and its wall-clock accounting stops meaning what it meant.

**The timeout is a Run-level budget, and it is part of the harness fit.** AHE's step budget and
per-task timeout were fitted to one model's operating point, which the authors flag as a
generalisation hazard `[AHE Limitations]`. In this chapter's vocabulary: the Episode's step budget
and the Run's wall-clock cap are harness parameters, not infrastructure settings. Chapter 38 versions
them alongside the components, and Chapter 1's cold open is what happens when you do not.

---

## 15. Industry Perspective

### Supported by the attached Durable Runtime architecture `[DAR]`

- The five nouns, their definitions, and their stated lifetimes (§3.1).
- The Episode resolving the tension between per-step durability and in-process locality; step budget
  of one reproducing a strict per-step runtime (§5.1).
- The four episode exit conditions and the checkpoint-plus-signal-read pattern (§5.1).
- The custody rule for scarce, exclusively held resources (§5.2).
- Exactly one driver advancing a run at any instant, via lease and version check (§5.3, §13).
- All non-determinism quarantined inside activities (§6.1).
- Activity identity computed at plan time, including the plan id; partial matches as anomalies
  (§6.2).
- Activity properties: leased, attempt-capped, dead-lettered, swept continuously (§6.3).
- Reserve-then-settle budgeting, and parking when a reservation exceeds the ceiling (§6.4).
- Parks holding no process, connection, or in-memory timer; surviving restarts; the general waiting
  primitive with five resolution conditions (§8.2).
- A replan writing new step rows rather than editing old ones (§11).
- Steps-per-episode as a monitored distribution, with a mode at one indicating a lost loop (§15).
- Time parked by gate type as a signal identifying humans as the bottleneck (§15).
- The failure catalogue drawn on in §11 (§14).

### Supported by the attached AHE paper `[AHE]`

- k traces generated per task, each a rollout of one harness configuration (§3.2).
- A per-task timeout of one hour in the reference campaign (§4.1).
- Step budget and per-task timeout fitted to one model's operating point, flagged as a generalisation
  hazard (Limitations).

### Engineering inference `[INF]`

- The custody gradient: scarcity times duration held roughly constant across the five nouns, and its
  use as a violation detector.
- The merge table in §2.3 — what each tempting simplification costs.
- The persistence rule: a noun is persisted if and only if losing it loses unreconstructible
  information.
- The turn-to-step mapping, and the claim that they do not nest cleanly.
- The cardinality distribution in §12, and the consequence that capacity is sized for the executing
  population rather than the live one.
- The lease-must-exceed-slowest-step guidance in §13.2.
- The observation that adding gates to an agent intended for evolution introduces a noun the
  published loop has never reasoned about.
- Park-mistaken-for-stall as a vocabulary and observability failure with two specific fixes.

### Industry best practice `[BP]`

- Deriving metrics for entities that are not persisted, rather than persisting them to make them
  queryable.
- Restricting a public API surface to the smallest addressable unit.

### Future proposal `[FUT]`

- None in this chapter.

---

## 16. Key Takeaways

1. **Five nouns, five lifetimes, spanning nine orders of magnitude.** Run, Episode, Step, Activity,
   Park. Every later chapter is written in this vocabulary.
2. **The custody gradient governs all of them.** Scarcity times duration is roughly constant; the
   longer a noun lives, the less scarce the thing it may hold. Every custody violation is a case of
   moving one noun up and to the right.
3. **The Episode is a dial, not a commitment.** Step budget one reproduces strict per-step execution,
   so keeping the loop costs no optionality.
4. **A Park holds nothing.** Approvals, input, callbacks, timers, and budget grants are one construct
   with five resolution conditions — and a park that lasts six hours costs one row.
5. **Only Run is addressable from outside.** Operators act on runs; the kernel acts on everything
   else.
6. **Most runs are parked most of the time.** Size capacity for the executing population, and watch
   the parked one for a gate backlog.
7. **"The agent" is not a noun.** Three engineers, forty minutes each. Name the noun.

---

**Next:** Chapter 6 — *State Separation: Run State, Domain State, Model State.* We take the deletion
test from Chapter 4, make it precise, and add a third state category that neither source names.
