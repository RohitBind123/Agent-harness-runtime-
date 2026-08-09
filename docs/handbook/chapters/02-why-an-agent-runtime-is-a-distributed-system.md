```
  Level 0 · Chapter 2
  WHY AN AGENT RUNTIME IS A DISTRIBUTED SYSTEM
  Requires   C0 Evolution of AI Systems, C1 Anatomy of an Agent
  Unlocks    C3 Mental Models, and all of Level 1
  Diagrams   Light (3)
  Variant    Foundational — sections 4-9 describe models, not components
```

# Chapter 2 — Why an Agent Runtime Is a Distributed System

---

## 1. Motivation

### 1.1 Cold open

The Atlas team knows how to build backend systems. When the in-process loop stops being viable, they
do the obvious correct thing: put it on a job queue. Workers, retries with exponential backoff, a
dead-letter queue, structured logging, a dashboard. The same shape they have shipped a dozen times.

Three weeks in, three things have happened.

The finance dashboard shows a spend spike nobody can explain. A class of task was timing out at
ninety minutes, retrying three times as configured, each retry a complete re-execution costing
roughly forty dollars in model calls. The retry policy was correct by every standard the team had
ever applied. It was also, here, a way to multiply a failure by four.

The connection pool wedges under moderate load. Adding connections helps for two days. The workers
hold a pooled connection for the duration of each model call, because that is what every other job
in the codebase does — and no other job has ever spent ninety seconds inside one step.

And a customer reports that Atlas force-pushed to a branch it should not have touched. The system
prompt asked it to confirm before destructive operations. It usually did.

Nothing in that list is exotic. Each is a specific, well-understood defect with a specific,
well-understood fix — a framing this handbook takes directly from the reference architecture
`[DAR §2.1]`. What makes them worth a chapter is that a competent backend team walked into all three
while doing what competence normally recommends.

### 1.2 In plain language

An ordinary web request is short. Code starts, does its work, sends an answer, and forgets
everything. If the machine dies halfway through, the person presses refresh and nothing has really
been lost.

An agent run is not short. It can take six hours, spend hundreds of dollars in model calls, change
files in somebody's repository, and need a human to approve something in the middle. The moment
work lasts that long, four things become true that were not true before:

- the work outlives the request that asked for it, so it cannot live inside that request;
- every attempt costs real money, and no two attempts are the same, so "try again" is a financial
  decision rather than a free one;
- the work changes things outside your system that you cannot undo by forgetting them;
- a person may need to stop it, or redirect it, while it is still running.

Each of those four has a standard, well-understood solution that databases and job systems worked
out decades ago, and this chapter names the solution for each one. It also names the places where
the standard solution is *wrong* here — which happens mostly because ordinary systems assume that
retrying is cheap and repeatable, and here it is neither.

If you have built backend systems before, this chapter is the one that tells you which of your
instincts to keep and which will cost you money.

### 1.3 Why this chapter exists

You already know distributed systems. That is an advantage and a trap.

The advantage is that roughly eighty percent of this architecture is machinery you have built
before: outboxes, leases, idempotency keys, dead letters, admission control. Chapter 4 onward will
feel less like learning and more like recognising.

The trap is the other twenty percent, where the familiar answer is wrong in a way that does not
announce itself. A retry policy that is correct for an HTTP call is a cost incident here. A cursor
that is correct for a log consumer is an outage here. A timeout that is correct anywhere else leaks
resources here. This chapter is the map: what transfers unchanged, what transfers with a twist, and
the three places where agent workloads genuinely differ from every other long-running job you have
run.

### 1.4 What previous framings got wrong

**"It is a job queue with a model call in it."** The cold open is what that assumption costs. The
differences are not in the queue; they are in the properties of the work the queue is carrying.

**"It is a data pipeline."** A pipeline's stages are known before it runs. An agent's steps are
authored during execution by the thing executing them. That single difference invalidates
pre-validation, pre-authorisation, and static cost estimation — the three techniques a pipeline
relies on most.

**"We will add reliability later."** Reliability retrofits well; *identity* does not. If activities
were not identity-keyed from the start, every stored result in the system is of unknown reusability,
and the migration is a rewrite. Section 13 gives the ordering that avoids this.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Ordering a coffee, versus renovating a building.

Ordering a coffee is a web request. You stand at the counter, it takes ninety seconds, and if
something goes wrong you order again. Nothing needs to be written down, because nothing survives the
transaction. Every technique that works here — retry on failure, hold your place in the queue, time
out and give up — works because starting over is cheap and harmless.

A renovation is an agent run. It takes months. Subcontractors do irreversible things: once a wall is
down, it is down. It costs enough that doing it twice by accident is a serious event. Some steps
legally require a permit before they may begin. And the owner may walk in on a Tuesday and change
their mind.

Look at what a renovation therefore needs, none of which a coffee order needs: a written schedule
that outlives any one worker's shift, a site log recording what was actually done, a permit process
that blocks specific steps until a human signs, a change-order procedure for when the owner
redirects mid-project, and a way to halt work today rather than at the end. That list is this book's
table of contents. The plan is Chapter 10, the site log is Chapter 22, the permit is Chapter 30, the
change order is steering, and the halt is cancellation.

**Where the analogy breaks.** A renovation is planned before work begins, by an architect who is not
one of the builders. The plan is a document you can price, approve, and validate in advance.

An agent's plan is written *during* the work, *by* the thing doing the work. That single difference
is the third of the three genuine differences in §2.4, and it is why three standard project
techniques do not transfer: you cannot pre-validate a plan that does not exist yet, you cannot
pre-authorise steps nobody has proposed, and you cannot pre-budget work whose shape is unknown. Gates
(Chapter 30), budget reservations (Chapter 35), and plan identity (Chapter 10) are what replace them.

### 2.2 Why the in-process loop must be abandoned

Most teams start with a loop inside a request handler, and the move away from it feels like a
scaling decision made for performance reasons. It is not. It is forced, and it is forced early:

```
  1. A loop inside a request handler lives exactly as long as the
     request does.
  2. Agent work routinely outlives any request timeout you would be
     willing to configure.
  3. So the loop must run somewhere that outlives the request. Call
     that a worker.
  4. A worker can be killed at any moment -- deploy, crash, spot
     reclaim. If the loop's progress exists only in that worker's
     memory, the kill loses all of it.
  5. Starting over is not free here. It re-spends money already spent,
     and it may repeat effects already applied to the outside world.
  6. Therefore progress must be written to durable storage at points
     from which resuming is provably safe.
  7. Two processes coordinating through shared durable state, where
     either may die at any point, IS a distributed system. There is no
     lighter-weight name for it.
```

The conclusion is worth stating flatly, because it is the thesis of the chapter: **you do not choose
whether to build a distributed system. You choose only whether to admit it.** A team that has not
admitted it still has leases, retries, and partial failure — but has them by accident, spelled
differently, and without the vocabulary to debug them.

### 2.3 What transfers, and what does not

```
                                                       CONCEPTUAL VIEW

   WHAT YOU ALREADY KNOW              WHAT IS ACTUALLY DIFFERENT
   (transfers unchanged)              (three properties, no analogue)
   +--------------------------+       +------------------------------+
   | transactional outbox     |       | 1. NON-DETERMINISM IS THE    |
   | leases and expiry        |       |    PAYLOAD                   |
   | idempotency keys         |       |    retry re-rolls, it does   |
   | dead-letter queues       |       |    not reproduce             |
   | work-class partitioning  |       +------------------------------+
   | admission control        |       | 2. AN ATTEMPT COSTS REAL     |
   | optimistic concurrency   |       |    MONEY                     |
   | structured tracing       |       |    retry policy is a         |
   +--------------------------+       |    financial decision        |
                                      +------------------------------+
   WHAT TRANSFERS WITH A TWIST        | 3. THE WORK IS AUTHORED BY   |
   +--------------------------+       |    THE THING DOING IT        |
   | retry -> replay, gated   |       |    you cannot pre-validate,  |
   |          by identity     |       |    pre-authorise, or         |
   | timeout -> real abort    |       |    pre-budget what does not  |
   | cursor -> claim          |       |    exist yet                 |
   | compensation -> gates    |       +------------------------------+
   +--------------------------+

  Figure 2.1 -- The transfer map (conceptual)
```

### 2.4 The three genuine differences

`[INF]` The left column of Figure 2.1 is standard practice. The right column is what this book is
actually about, and it is worth stating each one carefully.

**One. Non-determinism is the payload, not a fault.** Everywhere else in your career, non-determinism
has been something to eliminate: flaky tests, race conditions, unstable builds. Here it is the
product. The same input produces different output by design, and that inverts the meaning of retry.
Retrying a failed HTTP call reproduces the attempt. Retrying an agent step *re-rolls the dice*, which
means a retry can succeed for reasons unrelated to the fix you deployed, and can fail for reasons
unrelated to anything. The architectural response is containment rather than elimination: all
non-determinism is quarantined inside one construct, so that everything around it becomes a function
of state and events again `[DAR §6.1]`.

**Two. An attempt costs real money.** Not CPU-seconds — money, at a scale that appears on a finance
dashboard. This changes retry from an engineering default into a policy decision, makes an unbounded
loop a financial risk rather than a latency risk, and makes "record the cost afterwards" insufficient:
a run can exceed its ceiling by the cost of everything currently in flight, which with several
concurrent calls is not a rounding error `[DAR §6.4]`.

**Three, and this is the deep one. The work is authored by the thing doing it.** Every other
long-running system you have built knew its steps before it started. A deployment pipeline, a batch
import, a saga — the stages are in the code. Here, step four is written after step three returns, by
a model, based on what it found. The consequences cascade:

| Because the plan does not exist in advance… | …you cannot |
|---------------------------------------------|-------------|
| Steps are discovered, not declared | statically validate the work |
| Effects are chosen at runtime | pre-authorise what will be touched |
| Step count is unknown | pre-compute a cost |
| The plan can be replaced mid-run | assume a stored result still applies |

Each row has a component answer later in the book — gates for the second, budget reservation for the
third, plan identity for the fourth. All four exist because of this one property.

### 2.5 The mental model to carry

> **An agent runtime is an ordinary distributed system executing an extraordinary workload: one whose
> steps are unknown in advance, whose retries are non-reproducible, and whose attempts are
> expensive.**

The machinery is familiar. The workload is not. Almost every mistake in this space comes from
applying a correct pattern to a workload it was not designed for.

---

## 3. High-Level Architecture

### 3.1 The accidental architecture, and the deliberate one

```
                                                            LAYER VIEW

  THE ACCIDENTAL ARCHITECTURE          THE DELIBERATE ONE
  (four defects, each independently
   reasonable)

  +~~~~~~~~~~~~~~~~+                   +~~~~~~~~~~~~~~~~+
  | client         |                   | client         |
  +-------+--------+                   +-------+--------+
          | holds the connection               | returns immediately
          v   for the whole run                v
  +----------------+                   +----------------+
  | HTTP handler   |                   | edge           | stateless
  |                |                   +-------+--------+ no loop
  |  +----------+  |  D1                       | (1)      no model call
  |  |   loop   |  |  loop lives in            v
  |  |          |  |  the request        [[ command + event ]]
  |  +----+-----+  |                           | one transaction
  |       |        |                           v (2)
  |       | holds a DB connection       +----------------+
  |       | across the model call  D3   | relay          | claims events
  |       v        |                    +-------+--------+
  |  +----------+  |                            | (3)
  |  | model    |  |                            v
  |  | call     |  |  D2                 +----------------+
  |  +----------+  |  timeout abandons   | run driver     | lease + CAS
  |                |  but does not abort +-------+--------+ checkpoints
  +----------------+                             | (4)     holds nothing
          |                                      v
          | D4                            +----------------+
          v   "please confirm before      | activity runner| leased
  +----------------+   destructive ops"   +-------+--------+ budgeted
  | effectful call |   enforced in prose  |       | (5)     abortable
  +----------------+                      |       v
                                          |  +----------+
  recovery: at process boot, if           |  | model /  |
  anyone remembers to write it            |  | tool     |
                                          |  +----------+
                                          |
                                    (6)   v
                                   +----------------+
                                   | gate           | effectful steps
                                   +----------------+ structurally blocked
                                                      until resolved

                                   sweeper runs continuously, not at boot

  Figure 2.2 -- Four defects and their fixes (D1 High-Level Architecture)

  D1 the loop inside the request handler
  D2 a timeout that abandons the caller rather than aborting the call
  D3 a scarce resource held across a high-latency operation
  D4 authority enforced by instructing the model
```

The four defects are named as such in the reference architecture, which observes that most systems
meet the demands of agentic work by accident rather than by design: an in-process loop inside an
HTTP handler, a timeout that abandons rather than cancels, an approval enforced by asking the model
to behave, and recovery that only happens at boot `[DAR §2.1]`.

Each fix is small in isolation. The right-hand column is not a more sophisticated system; it is the
same system with four specific accidents removed.

---

## 4. Low-Level Decomposition: The Four Properties

The four properties that appear the moment a product asks a model to pursue a goal rather than answer
a question `[DAR §2.1]`, each with its defect and its fix.

### 4.1 The work outlives the request

Minutes to days, across restarts and deploys.

**Defect.** The loop lives inside the request handler, so the process is the system. A deploy is a
data-loss event. The client's connection is a dependency of the work completing.

**Fix.** The unit of work becomes a durable, versioned row rather than a stack frame. A worker
becomes a temporary reader of that row rather than its owner. The invariant is stated bluntly in
`[DAR §13]`: no work outlives the process that started it, because no work lives in a process.

**What this costs you.** A database on the hot path of every step, and the discipline of making every
step's state serialisable. Chapter 17 makes it cheap — the write is milliseconds — but it is not free.

### 4.2 The work is expensive and non-deterministic

Retrying naively spends real money and produces different output each time.

**Defect.** Standard retry semantics. Three attempts with backoff, which for a ninety-minute task is
six hours and four full charges.

**Fix.** Two mechanisms, and they are separate. *Identity* determines when a stored result may be
reused, so a re-claim replays rather than re-spends `[DAR §6.2]`. *Reservation* debits the projected
cost at dispatch and settles the actual at completion, so the ceiling holds even with several calls
in flight `[DAR §6.4]`.

**What this costs you.** Every step needs a stable identity computed before dispatch, and getting
that identity wrong produces the single worst failure the system can have: confident, well-formed,
wrong output, with no error and no alert `[DAR §6.2]`. Chapter 21 is largely about this.

### 4.3 The work touches the world

Some steps are irreversible and must not happen without a human's word.

**Defect.** The instruction lives in the prompt. It works most of the time, which is worse than never
working, because it produces a compliance statistic that looks like a control.

**Fix.** Every tool declares whether it changes the world outside the system, and the check that an
effectful tool has a resolved approval lives in the code path that invokes tools — where omitting it
is a type error rather than an oversight `[DAR §8.1]`.

**Why compensation is not enough.** `[INF]` The saga pattern you would reach for handles this
elsewhere: act, and compensate if it goes wrong. It works because the effects are yours to reverse.
Here they are frequently not. You cannot un-send an email, un-merge into someone else's mainline, or
un-charge a card without the counterparty's cooperation. The architecture therefore prefers
prevention to compensation, and prevention requires the human decision to happen *before* the
effect — which requires a way to wait indefinitely while holding nothing.

### 4.4 The work must be interruptible

A person watching work go the wrong way must be able to redirect it without losing what is already
correct.

**Defect.** Two options: wait for it to finish being wrong, or kill it and lose everything, including
the parts that were right.

**Fix.** Signals delivered at checkpoints and mid-activity, with four kinds — steer, cancel, pause,
answer `[DAR §8.3]`. A steer is a goal amendment that forces a replan rather than a mutation of the
running plan, which means it composes with the identity rule rather than fighting it.

**What this costs you.** Every step boundary becomes a place that reads pending control input. In
practice this is free, because the checkpoint write was happening anyway and the read rides in the
same transaction `[DAR §8.3]`.

### 4.5 The seven goals, each with a falsification test

`[DAR §2.3]` pairs each design goal with an experiment that would disprove it. This is the right
model for architectural claims, and the handbook adopts it throughout — Appendix F turns each
invariant into a test.

| Goal | Verified by |
|------|-------------|
| Liveness — every run reaches a terminal or parked state | continuous lease sweep; no run sits past its lease |
| Isolation — one tenant's slow work does not delay another's fast work | work-class queues plus per-tenant admission |
| Durability — killing a worker loses no committed decision | `kill -9` under load; the run resumes at its last checkpoint |
| Idempotency — redelivery produces the same result and the same spend | replay an activity; exactly one charge |
| Authority — no irreversible action without a human decision | call an effectful tool without a gate; the runner refuses |
| Interruptibility — a person can redirect running work without discarding it | signal delivered mid-activity in under two seconds |
| Accountability — every step, cost, and decision is attributable afterwards | the activity ledger and event log reconstruct any run |

If you cannot run the right-hand column, you have not built the left-hand column. You have written
it down.

---

## 5. The Translation Table

Concept you know, its form here, and whether the familiar answer survives.

| You know | Here it becomes | Verdict |
|----------|-----------------|---------|
| Transactional outbox | Unchanged. State change and its event in one transaction | **Transfers** — and it is the only durability primitive required `[DAR §7.1]` |
| Lease with expiry | Unchanged, claimed in the same statement as a version check | **Transfers** `[DAR §5.3]` |
| Optimistic concurrency | Unchanged. Version CAS alone is sufficient for safety | **Transfers** — and an advisory lock alongside it is one mechanism too many `[DAR §5.3]` |
| Dead-letter queue | Unchanged, applied to both events and activities | **Transfers** |
| Work-class partitioning | Unchanged. Fast decisions and slow model calls never share a queue | **Transfers** `[DAR §5.4]` |
| Idempotency key | A hash over run, **plan**, step, tool, and resolved inputs | **Twist** — the plan must be in the key, or a replan inherits stale work `[DAR §6.2]` |
| Retry with backoff | Retry is permitted; *re-execution* is not, unless identity says the prior result no longer applies | **Twist** — retry means replay first, re-run second |
| Timeout | Must abort the real call, not abandon the wait | **Twist** — a timeout that only stops waiting leaks the operation and lets its effects land later `[DAR §5.5]` |
| Saga / compensation | Prevention via gates, because many effects cannot be compensated | **Twist** — §4.3 |
| Circuit breaker | A model semaphore plus error classification at the model port | **Twist** — you are bounding a paid external resource, not protecting a peer |
| Backpressure | Per-tenant admission before the semaphore | **Twist** — a global semaphore of four to six slots is one busy tenant away from starving everyone `[DAR §5.4]` |
| Consumer cursor / offset | A per-row claim instead | **Inverted** — see below |

### 5.1 The one place the familiar answer is worse

Cursors are the standard way to consume an append-only log, and here they are the weaker choice. The
comparison from `[DAR §7.2]`:

| Property | Cursor | Claim |
|----------|--------|-------|
| Scaling | Single writer; a throughput ceiling to monitor | N workers, zero coordination |
| Poison event | Stalls the global cursor, and therefore every tenant | Blocks one partition only |
| Drift | Multiple stores must stay consistent, and fail silently | Nothing to drift |
| Starvation | Needs a dedicated connection as mitigation | The claim is a fast transaction |
| Recovery | Cursor repair, often manual | Stale claims expire; the existing sweeper handles it |

`[INF]` The reason the familiar answer loses here is workload-specific. A cursor is excellent when
events are cheap, uniform, and fast to process. Agent events are none of those: one of them may
trigger a ninety-second model call, and a single poison event can be a task that reliably crashes a
tool. Under those conditions the cursor's global ordering — its main virtue elsewhere — becomes a
global coupling.

---

## 6. Runtime Sequence

The same retry, done the familiar way and the correct way.

```
                                                              TIME VIEW

  THE FAMILIAR RETRY                    THE CORRECT RETRY
  --------------------------            ------------------------------------
  worker claims job                     worker claims the activity BY ID
    |                                     |
    | executes step 1  ($12)             | identity = hash(run, plan, step,
    | executes step 2  ($15)             |            tool, resolved inputs)
    | executes step 3  ($13)             |
    |                                     | ledger lookup on that identity
  worker dies at step 4                   |
    |                                     +-- found, completed?
  job returns to the queue                |     -> replay the stored result
    |                                     |        no model call, no charge
  retry: worker claims it                 |
    |                                     +-- found, running, lease expired?
    | executes step 1 AGAIN  ($12)        |     -> re-claim; the prior
    | executes step 2 AGAIN  ($15)        |        attempt aborted, so
    | executes step 3 AGAIN  ($13)        |        re-run is correct
    | executes step 4        ($14)        |
    |                                     +-- not found?
  succeeds                                |     -> run it, reserve budget
    |                                     |        first, settle after
  total spend: $94                        |
  outputs of steps 1-3 differ           run resumes at step 4 only
  from the first attempt                total spend: $54
                                        steps 1-3 byte-identical to before

  Figure 2.3 -- A retry, two ways (D4 Sequence)
```

Two details in the right-hand column matter more than they look.

**The identity is computed at plan time, not at dispatch time** `[DAR §6.2]`. This makes it auditable
and prevents dispatch from silently disagreeing with planning about what a step is.

**A partial match is an anomaly, not a hit.** Same run and position, different plan or inputs, must
be recorded and alerted rather than treated as a cache hit `[DAR §6.2]`. That single rule converts an
invisible bug class into a metric — one of the eleven that Chapter 34 says must be measured.

---

## 7. State Management

Where state lives, and the rule that governs it.

| State | Lives in | Owner | Survives a worker death |
|-------|----------|-------|------------------------|
| Run state — current step, plan, lease, attempts, budget spent | the runtime's tables | the runtime | yes |
| Domain state — the merged branch, the shipped order, the balance | your product's tables | your domain | yes, independently |
| Model state — assembled context, cache prefix, reasoning budget | memory, for the duration of one call | the context system | no, and correctly so |
| In-flight step | one worker's memory | nobody | no — and it is the only thing you may lose |

`[DAR §3.3]` gives the structural test for the first two, and it is worth internalising before
Chapter 6 formalises it: no run state may live on a domain aggregate — no current step, no lease, no
retry count, no plan id — and no domain truth may live in the run. If you cannot delete the entire
runtime and still have a coherent product, the two have merged.

`[INF]` The third row is the handbook's addition. Model state is neither run state nor domain truth:
it is derived, reconstructible, and deliberately not persisted. Teams that persist it discover they
have created a third source of truth that drifts from the other two.

---

## 8. Interfaces

What an agent runtime must expose that a job queue does not.

| Interface | A job queue offers | A runtime must also offer | Why |
|-----------|-------------------|---------------------------|-----|
| Submit | `enqueue(job) -> id` | `submit(goal) -> run_id` | Same shape |
| Observe | terminal status | live progress stream, plus a durable step history | The work takes hours; status is not enough |
| Control | cancel, sometimes | `signal(run_id, kind)` for steer, cancel, pause, answer | Redirection without discarding correct work |
| Decide | nothing | `resolve(approval_ref, decision, signer)` | Authority is a first-class input |
| Account | duration, sometimes | per-step cost, attributable after the fact | Attempts cost money |

`[INF]` The presence of the third and fourth rows is a reasonable test for whether you have built a
runtime or a queue with model calls in it. A system that cannot be steered and cannot be asked is a
submission form.

---

## 9. Data Structures

A preview only; Chapter 11 and Appendix D give the schema. Eight tables `[DAR §11]`: two for the
messaging spine, four for run execution, two for control.

| Table | Answers |
|-------|---------|
| `events` | What has happened? (the outbox) |
| `commands` | What was requested, and what did it return? (deduplication) |
| `runs` | What is in flight, and who holds it? |
| `run_steps` | What is the plan, and what were the previous plans? |
| `activities` | Has this already run, and what did it cost? |
| `run_signals` | What has a human asked for out of band? |
| `budget_ledger` | What is reserved, and what settled? |
| `approvals` | What was asked, who decided, and when? |

Your domain's tables sit outside this set and are joined to it by nothing, which is precisely what
makes the runtime removable `[DAR §11]`.

---

## 10. Communication

| Direction | Carries | Notes |
|-----------|---------|-------|
| Edge → substrate | Commands, and the events describing them | One transaction, always |
| Substrate → kernel | Claimed events | One in flight per partition |
| Kernel → ports | Plan requests, tool invocations, grading requests | Slow and fast classes separated |
| Ports → external | Model calls, tool effects | The abort signal reaches all the way down |
| Domain → substrate | Truth, plus the event describing it | One transaction, always |
| Kernel → client | Progress | Direct, never through the outbox — it is not a fact `[DAR §7.1]` |
| Human → kernel | Signals and approval decisions | Arrive as ordinary events |

The last two rows are a pair worth noticing. Progress flows out without durability because nothing
downstream needs to replay it. Decisions flow in *with* durability because everything downstream
depends on them. Getting this backwards — writing token-by-token progress into the event log —
bloats the log, the relay, the audit trail, and the replay path with data nobody will read again.

---

## 11. Failure Modes

| Failure | Detected by | Recovery |
|---------|-------------|----------|
| Worker killed mid-episode | run lease expiry | sweeper clears the lease; the run re-drives from its last checkpoint |
| Worker killed mid-activity | activity lease expiry | the activity becomes re-claimable; identity ensures replay, not re-spend |
| Model call hangs | the episode deadline | the abort tears down the stream, frees the slot, releases the reservation |
| Two workers race a run | version check returns zero rows | the loser drops its job; no compensation needed |
| Poison event | attempt counter reaches its cap | dead-lettered; only that partition is affected |
| Run exceeds its budget | reservation exceeds the remaining ceiling | the run parks awaiting a budget decision; nothing is spent meanwhile |
| Human never answers a gate | park age exceeds a policy threshold | escalation or expiry by policy; never silently abandoned |

Condensed from `[DAR §14]`, which gives the full catalogue. The pattern to notice: every row has a
named detector. A failure mode with no detection row is one you will learn about from a customer.

### 11.1 The failure whose symptom lies

Pool exhaustion is the instructive one. It presents as a database problem, and the instinct is to add
connections. That helps for a day or two.

The cause is custody, not capacity `[DAR §5.2]`. A resource that is both scarce and exclusively held
must never be held across an operation whose latency is high and variable — and a model call is the
canonical high-latency variable operation. Holding a pooled connection across one converts the
scarcity of the pool into a system-wide latency coupling: one slow call in one tenant's work stalls
every tenant's control plane.

`[INF]` This is the clearest example of why the twenty percent matters. Every diagnostic instinct a
good backend engineer has points at the pool. The pool is fine. The custody is wrong, and adding
connections only moves the failure further out.

---

## 12. Scalability

### 12.1 The custody corollary

Because no worker holds a connection across its slow operation, **worker concurrency may safely
exceed the database pool size** `[DAR §5.2]`. A pool of twenty comfortably serves far more than
twenty concurrent activities when each touches a connection only for millisecond-scale writes at step
boundaries.

This is the economic argument for the whole design, and it is worth stating as a number the reader
can check: if a step holds a connection for five milliseconds and a model call takes thirty seconds,
one connection can serve six thousand concurrent activities before contention. Custody, not capacity,
is what determines the ceiling.

### 12.2 Budgets must be per-resource

A single concurrency integer cannot simultaneously bound database connections, provider rate limits,
and fast-work parallelism `[DAR §5.4]`. Each constrained resource needs its own budget, and the axes
are independent precisely because the custody rule removed the coupling between them.

| Resource | Bounded by |
|----------|-----------|
| Database connections | pool size; touched only at step boundaries |
| Provider capacity | a model semaphore sized to provider limits, typically 4–6 |
| Fast-path work | CPU and short-transaction throughput, concurrency 8–16 |
| Per-tenant share | an admission check *before* the semaphore |

---

## 13. Production Engineering

### 13.1 When not to build this

The architecture earns its complexity only under specific conditions, and `[DAR §2.4]` is refreshingly
direct about the disqualifiers. Reproduced because a handbook that never says "do not" is a sales
document.

- **Your work finishes in one turn.** If a request is answered by a single model call and nothing
  irreversible happens, all of this is cost with no return. Write the handler and move on.
- **Nothing you do is irreversible.** Roughly half the machinery here — gates, budget reservations,
  the effectful tag, the approval port — exists to stop damage. If damage is not possible in your
  domain, delete that half rather than implementing it out of completeness.
- **You need cross-region durable timers, or millions of concurrent runs.** Buy a durable-execution
  engine rather than growing one. The seam is drawn so the run driver can be replaced without any
  port or any domain changing — do that on a measured need, not a predicted one.

### 13.2 Ordering: what retrofits and what does not

`[INF]` Not all of this can be added later, and knowing which is which is worth more than knowing any
individual technique.

| Concern | Retrofits? | Why |
|---------|-----------|-----|
| Metrics and dashboards | Easily | Additive |
| Per-tenant admission | Easily | One check before an existing semaphore |
| Dead letters | Easily | Additive |
| Work-class split | With effort | A routing change |
| Gates and approvals | With difficulty | Requires the pure/effectful tag on every tool, which is an audit of the whole surface |
| Durable state | Painfully | Touches every step |
| **Activity identity** | **Effectively not** | Every stored result becomes of unknown reusability; the migration is a rewrite |

Build identity first, even in the prototype. It is roughly thirty lines and it is the one decision
that cannot be deferred.

### 13.3 Anti-patterns

| Anti-pattern | Why it fails | Diagnosed in |
|--------------|-------------|--------------|
| **Standard retry policy** | Multiplies cost and re-rolls output; the cold open | Ch 21 |
| **Timeout as cancellation** | Leaks the operation and lets its effects land after everyone gave up | Ch 30 |
| **Connection held across a model call** | Converts pool scarcity into system-wide latency coupling | Ch 23 |
| **Authority in the prompt** | A hope with good compliance statistics | Ch 30 |
| **Boot-only recovery** | A long-lived worker that sweeps at start never notices a run stranded four hours in | Ch 27 |
| **Progress in the outbox** | Bloats the log, relay, audit trail, and replay path with data nobody reads | Ch 22 |

---

## 14. Relation to AHE

Evolution is downstream of this chapter in a way that is easy to miss: **an evolution loop can only
improve what it can measure, and it can only measure a runtime that produces comparable results.**

Three dependencies run from here to Level 5.

**Reproducible isolation.** The AHE experiments run every rollout inside a fresh remote sandbox
specifically so that shell side effects cannot leak between tasks `[AHE App. A]`. Without that, a
score difference between iterations could be contamination rather than signal, and every attribution
verdict in Chapter 47 would be unsound.

**Faithful accounting of failure.** Trials that abort on infrastructure exceptions count as failures
rather than being dropped — a deliberately harsher convention `[AHE App. A]`. `[INF]` A loop that
excluded infrastructure failures would learn to produce harnesses that crash the infrastructure,
because crashes would be free. Your runtime's failure semantics become the evolution loop's reward
shaping whether or not you intended that.

**Traceability as a precondition.** The AHE authors point to a parallel infrastructure track around
coding-agent benchmarks — packaged runtimes and verifiers whose attention to reproducible, traceable,
verifiable execution directly motivates the observation system the loop is built on `[AHE §2.1]`.
Chapter 16 builds that observation system, and it is the reason Chapter 44 has anything to read.

The short version: Level 5 is not a layer you add on top. It is a payoff you become eligible for by
building Levels 1 through 4 correctly.

---

## 15. Industry Perspective

### Supported by the attached Durable Runtime architecture `[DAR]`

- The four properties that appear when work becomes a goal rather than an answer (§2.1).
- The four accidental implementations named as specific defects with specific fixes (§2.1).
- The seven design goals, each paired with a falsification test (§2.3).
- The three disqualifiers for adopting the architecture (§2.4).
- Run state versus domain state, and the structural test for their separation (§3.3).
- The custody rule; pool exhaustion presenting as capacity while caused by custody; worker
  concurrency safely exceeding pool size (§5.2).
- Version CAS alone being sufficient for safety, with an advisory lock being one mechanism too many
  (§5.3).
- Per-resource budgets; work-class partitioning; per-tenant admission before the semaphore (§5.4).
- Timeout must abort the real call, not abandon the wait (§5.5).
- Non-determinism quarantined inside activities, making orchestration a function of state and events
  (§6.1).
- Identity computed at plan time including the plan id; partial matches recorded as anomalies (§6.2).
- Reserve-then-settle budgeting, and the in-flight overspend it prevents (§6.4).
- The outbox as the only required durability primitive; progress excluded from it (§7.1).
- The cursor-versus-claim comparison (§7.2).
- Effectful tools structurally uncallable without a resolved gate, enforced in the runner (§8.1).
- Signals as steer, cancel, pause, answer, read at checkpoints in the same transaction (§8.3).
- The eight-table data model and the deliberate absence of joins to domain tables (§11).
- The invariant that no work lives in a process (§13).
- The failure catalogue condensed in §11 (§14).

### Supported by the attached AHE paper `[AHE]`

- A fresh remote sandbox per rollout so side effects cannot leak between tasks (App. A).
- Infrastructure-aborted trials counted as failures rather than discarded (App. A).
- The infrastructure track around coding-agent benchmarks, whose reproducibility and traceability
  motivated the observation system the loop depends on (§2.1).

### Engineering inference `[INF]`

- The transfer map of Figure 2.1, and the three genuine differences in §2.2.
- The claim that "the work is authored by the thing doing it" is the deepest of the three, and the
  four consequences derived from it.
- Why compensation is insufficient here and prevention is preferred (§4.3).
- Model state as a third state category, derived and deliberately unpersisted (§7).
- The workload-specific explanation for why cursors lose to claims (§5.1).
- The retrofit-ordering table, and the claim that activity identity is the one decision that cannot
  be deferred (§13.2).
- The observation that a runtime's failure semantics become an evolution loop's reward shaping
  (§14).
- The steerability-and-approval test for distinguishing a runtime from a queue (§8).

### Industry best practice `[BP]`

- Exponential backoff, dead-letter queues, and structured tracing as baseline expectations; they
  transfer unchanged and are not re-taught here.
- Pairing architectural claims with falsification tests rather than assertions.

### Future proposal `[FUT]`

- None in this chapter.

---

## 16. Key Takeaways

1. **Eighty percent of this transfers from what you already know.** Outboxes, leases, idempotency,
   dead letters, admission control — unchanged. Chapter 4 onward should feel like recognition.
2. **The other twenty percent is where the familiar answer is actively wrong.** Retry, timeout,
   cursor, and compensation each need a different answer here, and none of them announces itself.
3. **Three properties have no analogue in work you have done before.** Non-determinism is the
   payload; an attempt costs real money; and the work is authored by the thing doing it.
4. **That third property is the source of most of the architecture.** You cannot pre-validate,
   pre-authorise, or pre-budget a plan that does not exist yet — hence gates, reservations, and plan
   identity.
5. **Custody, not capacity, sets your ceiling.** No connection and no lock across a model call, and
   worker concurrency may then exceed pool size by orders of magnitude.
6. **Build activity identity first.** Everything else retrofits. Identity does not.
7. **Know the disqualifiers.** One-turn work, no irreversible actions, or a genuine need for
   cross-region durability at scale all mean you should be building something else.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Durability** | The property that progress already made survives a process being killed at any moment. | `[DAR]` | Ch 21 |
| **Idempotency** | Doing something twice leaves the world exactly as doing it once did. | `[DAR]` | Ch 21 |
| **Idempotency key** | The value that lets a receiver recognise a repeat request as the same request, rather than a second one. | `[DAR]` | Ch 22 |
| **Activity identity** | A fingerprint of a tool call — run, plan, step, tool, and inputs — that decides whether a stored result may be reused instead of re-run. | `[DAR]` | Ch 21 |
| **Replay** | Re-running from a checkpoint, reusing stored results rather than re-spending on them. The correct alternative to a blind retry. | `[DAR]` | Ch 21 |
| **Retry** | Doing the work again from the start. Cheap in ordinary systems, a cost incident here. | `[BP]` | Ch 27 |
| **Lease** | A time-limited, durable claim that one worker owns a piece of work, with an expiry others can see. | `[DAR]` | Ch 17 |
| **Claim** | Marking a row as owned by one consumer, instead of sharing a position marker. Immune to one bad row stalling everyone. | `[DAR]` | Ch 22 |
| **Cursor** | A shared position marker in a stream; standard elsewhere, an outage waiting to happen here. | `[BP]` | Ch 22 |
| **Dead letter** | Terminally failed work parked for a human to look at, so it stops blocking everything behind it. | `[DAR]` | Ch 27 |
| **Custody** | Which scarce resource a piece of work is holding, and for how long. Sets the concurrency ceiling. | `[DAR]` | Ch 5 |
| **Blast radius** | Everything outside the system a run could touch if every guard failed. A quantity you size deliberately, not audit later. | `[INF]` | Ch 31 |
| **Admission control** | Refusing or delaying work at the door so that accepted work can actually be served. | `[BP]` | Ch 23 |

---

**Next:** Chapter 3 — *Mental Models and the Reference System.* We consolidate five reusable mental
models, introduce ARK and Atlas properly, and give you the map you will carry through the remaining
forty-six chapters.
