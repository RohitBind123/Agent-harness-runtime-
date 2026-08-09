```
  Level 2 · Chapter 18
  THE RUNTIME LOOP
  Requires   C5 The Five Nouns, C8 Lifecycles, C10 The Planner,
             C13 The Reasoning Engine, C14 The Tool Execution Engine,
             C17 The State Manager
  Unlocks    C21 Durable Execution, C23 The Scheduler,
             C29 Long-Running Agents, C33 Scalability,
             C35 Cost Engineering
  Diagrams   Full (9)
```

# Chapter 18 — The Runtime Loop

---

## 1. Motivation

### 1.1 Cold open

14:02. A customer hits cancel. The interface confirms immediately and the run moves to `CANCELLING`.

14:11. Atlas force-pushes to a protected branch.

The cancel was not lost. It was written durably at 14:02, in the same transaction as the request, and
it sat in the `signals` table with `consumed_at` still null for nine minutes.

The loop reads pending signals when an episode ends. This episode's wall clock was fifteen minutes.

So for nine minutes the system knew it should stop and continued anyway — through a plan step, a
model call, a gate that had been approved earlier for exactly this action, and a push. Nothing
malfunctioned. The signal was not delayed by a queue, blocked by a lock, or lost in a partition. It
was sitting in a table the loop had decided to read later.

Chapter 17 established that reading signals inside the checkpoint transaction costs one indexed
query on a transaction that is already open. The difference between that design and this one is
where a `SELECT` is placed.

### 1.2 In plain language

This is the loop that actually does the work. Everything in the last eight chapters — planning,
context, the model, tools, memory, state — exists to be called from about forty lines of code, and
this chapter is those forty lines.

The idea that makes it work is that the loop does not run for the length of a job. It runs for a
**bounded window** called an episode: a worker picks up a run, takes a handful of steps, writes down
where it got to, and lets go. Another worker — maybe the same one, maybe not — picks it up and does
the next handful.

That sounds like an inefficiency and it is the opposite. A job that runs to completion inside one
loop holds a machine for hours, cannot be redeployed, cannot be cancelled promptly, and loses
everything if the machine dies. A loop that yields every minute or so gives all of that back, and
costs one database write per step.

The loop ends for exactly four reasons: it ran out of wall-clock time, it ran out of its allowance
of steps, the run is waiting for something (a person, a timer, an event), or somebody sent it a
signal. There are no others, and each has a specific consequence, so "why did this run stop?" always
has a precise answer.

The cold open is the fourth reason being checked too late.

### 1.3 Why this chapter exists

This is the keystone. Chapter 4 drew a kernel with four components in it and said the run driver was
one of them. Chapters 5 through 17 built everything that driver calls. This chapter is the driver,
and after it Level 2 has nothing left to assemble.

`[INF]` It is also the chapter where a reader can check their own understanding, because the loop is
short enough to read in full and every line of it is a decision made in an earlier chapter. If a
line looks arbitrary, the chapter it came from was not understood — and §4 names the chapter for each
one.

### 1.4 What previous framings got wrong

**"The loop is the agent."** Chapter 3's naming rules ban the phrasing and this is the clearest
reason: the loop decides nothing. It sequences. Every judgement in it belongs to a port — the
planner proposes, the grader vetoes, the approval port blocks, the model reasons. §5.2 catalogues
what the loop is forbidden from doing, and the list is longer than what it does.

**"Run to completion; it is simpler."** It is simpler for about a week. Then a deploy has to wait
six hours, a cancel takes as long as the job, and a crash at minute fifty costs fifty minutes.
Chapter 8 already established that draining means letting go; the episode is what makes letting go
cheap.

**"Step budget one is safest."** `[INF]` It is the most expensive configuration in the system: every
step pays a queue hop, a claim, and a cold prompt cache (Chapter 11). §5.5 argues it is a dial worth
having and a terrible default.

**"Signals are an interrupt."** They are not delivered; they are *read*. Nothing pushes a
cancellation into a running loop, which is why where the loop reads them determines how fast it
stops — the cold open.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A relay race where the baton is the only thing that matters.

No runner carries the baton for the whole distance. Each takes it, runs a leg, and hands it on inside
a marked zone. The race is continuous; the runners are not. If a runner pulls up injured mid-leg, the
race is in trouble — but only for that leg, and only because the baton is stuck with them.

So the handover zones are what the design is really about. Frequent zones mean a runner can be
replaced quickly, a tiring runner can hand off, and no one runner's failure costs more than one leg.
Infrequent zones mean fewer handovers and a longer distance lost when something goes wrong.

An episode is a leg. A checkpoint is a handover zone — and Chapter 17 made checkpoints cheap
specifically so there can be one after every step, which is a race with a handover zone every few
metres.

**Where the analogy breaks**, and it breaks in the direction that makes this design work.

In a relay, the baton must be physically passed from one runner to the next; there is a moment where
both are holding it and a moment where the race depends on that transfer succeeding. Here there is
no handover at all. The worker writes where it got to and leaves. The baton is a row in a table, and
the next runner picks it up from the table whenever one is free — possibly seconds later, possibly
after a park lasting two days.

`[INF]` That is why the failure mode of a dropped baton does not exist here. A worker that dies
mid-leg has not dropped anything; it has stopped renewing a lease, and Chapter 17's sweeper
makes the run claimable again. **There is no transfer to fail** — which is the property that lets
a run cross an arbitrary number of worker lifetimes without any of them coordinating.

### 2.2 Why the loop must be bounded

```
  1. A run can take six hours. A loop that runs it to completion
     therefore holds a worker for six hours.
  2. That worker cannot be redeployed, so a deploy waits six hours
     or kills work in progress (Ch 8).
  3. And a crash at hour five costs five hours, unless progress was
     written down -- which means checkpointing anyway.
  4. So we are checkpointing regardless. The question becomes: having
     checkpointed, why continue holding the worker?
  5. There is no reason. The run's position is durable; any worker can
     resume from it (Ch 17).
  6. So the loop should yield periodically -- and the only remaining
     question is when.
  7. It must yield on: too much wall clock (fairness), too many steps
     (budget), the run waiting on something external (a park holds
     nothing, Ch 5), or somebody asking it to stop (a signal).
  8. Those four are exhaustive. Anything else is one of them wearing
     a different name.
```

Step 4 is the hinge and it usually goes unnoticed. `[INF]` The argument for episodes is not
primarily about efficiency; it is that **once you have made progress durable, holding the worker
buys nothing.** Teams that resist episodes are usually paying the checkpoint cost already and
receiving none of the benefit.

### 2.3 The four exit conditions

`[DAR §5.1]` Every episode ends for exactly one of these, and the run's next state follows from
which:

| Exit | Trigger | Run afterwards | Re-enqueued? |
|---|---|---|---|
| **E1 wall clock** | the episode's time budget elapsed | `EXECUTING` | yes, immediately |
| **E2 step budget** | took its allowance of steps | `EXECUTING` | yes, immediately |
| **E3 park** | waiting on a gate, timer, input, or callback | `PARKED` | **no** — an event wakes it |
| **E4 signal** | cancel, pause, or steer was pending | per the signal | depends |

`[INF]` E1 and E2 are fairness mechanisms and look alike; the distinction matters because they bound
different things. Wall clock bounds *one run's hold on a worker*, so a run with slow steps cannot
monopolise it. Step budget bounds *work between checkpoints of the whole plan*, which is what makes
cost per episode predictable. A run doing forty fast steps hits E2; a run doing two slow ones hits
E1.

E3 is the one that is not a limit at all. A park is the run saying it has nothing to do until the
world changes, and Chapter 5's custody gradient made it free.

### 2.4 The mental model to carry

> **The loop sequences and never decides. It runs for a bounded window, writes down where it got to
> after every step, and lets go. Four reasons to stop, and one of them is somebody asking.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  KERNEL                                                      |
  |                                                              |
  |   (( queue ))                                                |
  |        | (1) run_id only                                      |
  |        v                                                     |
  |   +====+=========================================+           |
  |   |  THE RUNTIME LOOP  (the run driver)          |           |
  |   |                                              |           |
  |   |   claim -> [ step -> checkpoint ]* -> release|           |
  |   |                                              |           |
  |   +--+------+-------+--------+--------+------+---+           |
  |      |(2)   |(3)    |(4)     |(5)     |(6)   |(7)            |
  |      v      v       v        v        v      v               |
  |  +---+--+ +-+----+ +-+----+ +-+----+ +-+--+ +-+------+       |
  |  |STATE | |PLAN- | |CON-  | |MODEL | |TOOL| |GRADER  |       |
  |  |MGR   | |NER   | |TEXT  | |PORT  | |ENG | |PORT    |       |
  |  |Ch 17 | |Ch 10 | |Ch 11 | |Ch 13 | |Ch14| |Ch 28   |       |
  |  +------+ +------+ +------+ +------+ +----+ +--------+       |
  |                                                              |
  |      every one of them is a PORT. The loop calls; it          |
  |      never judges. (section 5.2)                              |
  +--------------------------------------------------------------+
             |                                    |
        (8)  v                               (9)  v
     [[ runs ]] [[ run_steps ]]           observation (Ch 16)

  Figure 18.1 -- The loop and everything it calls
                 (D1 High-Level Architecture)

  (1) a queue message carrying an id; state is read at claim
  (2) claim, checkpoint, release -- the only writes the loop makes
  (3) propose the next step; a replan mints a new plan (Ch 10)
  (4) assemble what the model may see (Ch 11)
  (5) metered, capped, abortable (Ch 13)
  (6) dispatch, gated by the effect tag (Ch 14)
  (7) may downgrade a result, never upgrade it (Ch 28)
  (8) the checkpoint: one transaction, every step (Ch 17)
  (9) spans, fire-and-forget, never failing the run (Ch 16)
```

`[INF]` Count the arrows leaving the loop: six ports and two stores. That is the whole of Level 2 in
one diagram, and it is the argument for the narrow-waist design from Chapter 4 arriving at its
payoff. The loop knows nothing about repositories, patches, or customers — six interfaces, and every
product-specific decision is behind one of them.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  THE LOOP, in full. Every line names the chapter it came from.

  +--------------------------------------------------------------+
  | claim the run                                     (Ch 17)     |
  |   zero rows -> another worker won; take other work            |
  |                                                              |
  | started = now();  steps = 0                                  |
  |                                                              |
  | LOOP:                                                        |
  |   1. is the run terminal?              -> release, done      |
  |                                                              |
  |   2. do we still have budget?          (Ch 13, Ch 35)        |
  |        no -> park BUDGET_EXHAUSTED     -> E3                 |
  |                                                              |
  |   3. ask the planner for the next step (Ch 10)               |
  |        it PROPOSES; it does not act                          |
  |                                                              |
  |   4. is the step effectful?            (Ch 14)               |
  |        yes and no resolved gate -> park -> E3                |
  |                                                              |
  |   5. dispatch the step                 (Ch 14)               |
  |        identity checked first: a recorded result is           |
  |        REUSED, not re-run                    (Ch 21)         |
  |        NO LEASE, NO CONNECTION HELD          (Ch 5)          |
  |                                                              |
  |   6. grade the result                  (Ch 28)               |
  |        may downgrade; never upgrade                          |
  |                                                              |
  |   7. CHECKPOINT                        (Ch 17)               |
  |        advance + renew lease + append step + READ SIGNALS,   |
  |        all in one transaction                                |
  |        zero rows -> superseded; STOP                         |
  |                                                              |
  |   8. a signal was pending?             -> E4                 |
  |   9. wall clock elapsed?               -> E1                 |
  |  10. steps >= step_budget?             -> E2                 |
  |                                                              |
  |   steps += 1;  continue LOOP                                 |
  |                                                              |
  | release the lease; re-enqueue unless PARKED or terminal      |
  +--------------------------------------------------------------+

  Figure 18.2 -- The loop, opened (D2 Low-Level Architecture)
```

### 4.1 The orderings that are not arbitrary

`[INF]` Four positions in that sequence encode decisions from earlier chapters, and swapping any of
them reintroduces a specific defect.

**Budget before planning (2 before 3).** Planning is itself a model call (Chapter 13 §12.1). Checking
budget afterwards means a run with no money left has already spent more.

**Gate before dispatch (4 before 5).** Chapter 14 §4.1: an effectful step is structurally uncallable
without a resolved gate, and the check must precede the identity lookup so a replay cannot slip past.

**Checkpoint before the exit tests (7 before 8-10).** The exits must be evaluated against *durable*
state. Exiting first and checkpointing afterwards leaves a window where the loop has decided to stop
and the database does not know it.

**Signals read inside the checkpoint (7), tested immediately after (8).** The cold open. Reading them
at 7 costs nothing extra; testing at 8 means cancellation takes one step.

```
                                                            LAYER VIEW

  Components. The loop itself is the small box in the middle.

   (( queue ))
        |
        v
   +----+------------+        +---------------------+
   | Episode driver  |------->| Budget checker      |
   |  ~40 lines      |        |  (Ch 13, Ch 35)     |
   |                 |        +---------------------+
   |  claim          |
   |  loop           |------->+---------------------+
   |  release        |        | Step executor       |
   +----+------------+        |  plan -> gate ->    |
        |                     |  dispatch -> grade  |
        | every step          +----------+----------+
        v                                |
   +----+------------+                   | calls the six ports
   | Checkpointer    |                   v
   |  (Ch 17)        |            +------+----------+
   |  advance        |            | PORTS           |
   |  renew          |            |  planner        |
   |  read signals   |            |  context        |
   +----+------------+            |  model          |
        |                         |  tool           |
        v                         |  grader         |
   +----+------------+            |  approval       |
   | Exit evaluator  |            +-----------------+
   |  E1 wall clock  |
   |  E2 step budget |            +-----------------+
   |  E3 park        |----------->| Observation     |
   |  E4 signal      |            |  (Ch 16)        |
   +-----------------+            |  fire-and-forget|
                                  +-----------------+

  Figure 18.3 -- Loop components (D3 Component Diagram)
```

`[INF]` The Exit evaluator is drawn separately because it is the piece most likely to be inlined and
then quietly extended. Four conditions, evaluated in a fixed order, with nothing else permitted to
end an episode — keeping it a named component is what makes a fifth exit condition a visible design
change rather than an `if` somebody added.

---

## 5. The Episode

### 5.1 What an episode is, and is not

`[DAR §5.1]` An episode is **a function invocation**, not a row. Chapter 5 §4 established this and it
has consequences that surprise people:

- **You cannot query for episodes.** They leave only their side effects — checkpoints, steps, spans.
- **Steps-per-episode is inferred**, from checkpoint timestamps, which is why Chapter 34 makes it a
  metric: it is otherwise invisible.
- **An episode has no identity** anything else refers to. A step belongs to a run and a plan; it does
  not belong to an episode.
- **Episodes are strictly sequential** for one run. Never concurrent, ever. That is Chapter 17's
  lease, and it is the runtime's single most important invariant `[DAR §13]`.

### 5.2 What the loop is forbidden to do

`[INF]` The list is longer than what it does, and it is the reason the loop stays forty lines:

| The loop does not | It calls | Chapter |
|---|---|---|
| decide the next step | the planner | 10 |
| decide what the model sees | the context system | 11 |
| decide whether a step is allowed | the effect tag and the gate | 14, 30 |
| decide whether a result was good | the grader | 28 |
| decide what a tool does | the tool engine | 14 |
| decide what a run costs | the model port's reserve | 13 |
| write domain state | commands, across the waist | 4 |
| retry an effectful step | nothing — that is a replan | 14 |

Every row is a judgement, and every judgement is behind a port. `[INF]` A loop that acquires one of
them has taken a decision out of a replaceable component and put it in the one piece of code that is
hardest to change — and Chapter 46 cannot edit it, because the kernel is outside the Evolve Agent's
workspace.

### 5.3 No scarce resource crosses a model call

Chapter 2's custody rule, Chapter 5's gradient, and here is where it is actually enforced. At step 5
of the loop, while an activity is in flight:

| Held | Not held |
|---|---|
| a row saying who owns the run | a database connection |
| a budget reservation (Ch 13) | a transaction |
| a model semaphore slot | a lock of any kind |
| | the checkpoint's transaction — it committed |

`[DAR §5.2]` This is what allows worker concurrency to exceed connection-pool size by orders of
magnitude. A worker awaiting a ninety-second model call is consuming a slot in a semaphore and
nothing else.

`[INF]` The single most common way to lose this property is to wrap the loop body in a transaction
"for consistency". It looks tidy and it converts every concurrent run into a held connection, which
is Chapter 2's cold open reproduced exactly.

### 5.4 Signals, and why latency is one step

Signals are **read, not delivered**. Nothing pushes into a running loop, and the design is better for
it: a push would need the loop to be addressable, which would pin a run to a worker and undo Chapter
17.

`[DAR §5.3]` The checkpoint reads them because its transaction is already open. So:

```
  cancellation latency  =  time to finish the current step
                        +  one checkpoint (~5 ms)
```

`[INF]` For a run doing sub-second steps, that is sub-second. For one mid-way through a ninety-second
model call, it is up to ninety seconds — and Chapter 13's abort handle is what shortens that, by
abandoning the call rather than waiting for it. The two mechanisms compose: the loop notices at the
next checkpoint, and the abort handle brings that checkpoint forward.

The cold open's system had neither. It noticed at episode end.

### 5.5 Step budget is a dial, and one is a bad default

`[DAR §5.1]` Setting the step budget to 1 turns every step into its own episode. The architecture
still works — which is the point, and why it is a dial — but the cost is real:

| Per step, at budget = 1 | Cost |
|---|---|
| a queue hop | latency, and queue throughput |
| a claim (conditional UPDATE) | a write |
| a cold prompt cache | Chapter 11's cache benefit, lost entirely |
| worker scheduling | context switching across the fleet |

`[INF]` The prompt-cache row is the expensive one and it is invisible in any latency metric. A run of
forty steps at budget 8 pays full price for its context five times; at budget 1, forty times.
Chapter 11's cold open was one line of prompt costing threefold, and this is the same loss arriving
from the loop's configuration instead.

The honest use for budget 1 is debugging and incident response, where per-step observability is worth
the cost. Chapter 34 makes steps-per-episode a metric precisely so that a budget of 1 left on after
an incident shows up as a distribution with a mode at one.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  queue   loop    state   planner  context  model   tool   signals
    |      |        |        |        |       |      |        |
    |-- run_id -->  |        |        |       |      |        |
    |      |-- claim ------->|        |       |      |        |
    |      |<-- ClaimedRun(v12) ------|       |      |        |
    |      |                                                   |
    |      | STEP 1                                            |
    |      |-- budget ok ------------------------------------->|
    |      |-- plan ------->|         |       |      |        |
    |      |               |-- assemble ----->|      |        |
    |      |               |<-- context ------|      |        |
    |      |               |-- complete ------------>|        |
    |      |<-- Plan(C, 9 steps) -----|       |      |        |
    |      |-- checkpoint(v12) ------>|       |      |        |
    |      |<-- v13, signals: none ---|       |      |        |
    |      |                                                   |
    |      | STEP 2  pure tool                                 |
    |      |-- dispatch --------------------------->|         |
    |      |         (NO lease held, NO connection) |         |
    |      |<-- ToolResult(OK) ---------------------|         |
    |      |-- checkpoint(v13) ------>|                        |
    |      |<-- v14, signals: none ---|                        |
    |      |                                                   |
    |      | STEP 3  effectful -> gate not resolved            |
    |      |-- park GATE ------------>|                        |
    |      |<-- v15, state=PARKED ----|                        |
    |      |-- release (no re-enqueue) ->|                     |
    |      |                                                   |
    |      | ... hours pass. The run holds NOTHING. ...        |
    |      |                                                   |
    |      | approval arrives -> event -> relay -> re-enqueue  |
    |      |                                                   |
    |      | NEW EPISODE, possibly a different worker          |
    |      |-- claim ------->|                                 |
    |      |<-- ClaimedRun(v16) ------|                        |
    |      | STEP 3 again: gate now resolved                   |
    |      |-- dispatch --------------------------->|         |
    |      |<-- ToolResult(OK) ---------------------|         |
    |      |-- checkpoint(v16) ------>|                        |
    |      |<-- v17, SIGNALS: [cancel] |                       |
    |      |                                                   |
    |      | E4: exit NOW, one step after it was sent          |
    |      |-- checkpoint(state=CANCELLED) -------->|          |
    |      |-- release ------------->|                         |

  Figure 18.4 -- Two episodes, a park, and a cancel honoured in one
                 step (D4 Sequence)
```

### 6.1 What the sequence demonstrates

Three properties, none of which is visible from the loop's code alone.

**The park costs nothing.** Between release and the approval arriving, the run holds no worker, no
connection, no lease, and no timer. Chapter 5's gradient, delivered.

**The episode boundary is invisible to the run.** Step 3 was attempted in one episode and completed
in another, possibly on a different machine, with no handover. The run's position was in a row the
whole time.

**Cancellation took one step.** The signal was read in the checkpoint at the end of step 3 and acted
on immediately. The cold open's system would have finished the episode first.

```
                                                             TIME VIEW

  THE LOOP. Four exits, and nothing else may end an episode.

        claim
          |
          v
   +------+---------------------------------------------+
   |                                                    |
   v                                                    |
  /  \                                                  |
 /term\ yes -> release, done                            |
 \inal/                                                 |
  \  /                                                  |
   | no                                                 |
   v                                                    |
  /  \                                                  |
 /bud \ no  -> park BUDGET_EXHAUSTED ----------> E3     |
 \get?/                                                 |
  \  /                                                  |
   | yes                                                |
   v                                                    |
 +-+------------------+                                 |
 | plan (Ch 10)       |                                 |
 +-+------------------+                                 |
   |                                                    |
   v                                                    |
  /  \                                                  |
 /gate\ required and unresolved -> park --------> E3    |
 \  ? /                                                 |
  \  /                                                  |
   | ok                                                 |
   v                                                    |
 +-+------------------+                                 |
 | dispatch (Ch 14)   |  no lease, no connection held   |
 | grade    (Ch 28)   |                                 |
 +-+------------------+                                 |
   |                                                    |
   v                                                    |
 +-+------------------+                                 |
 | CHECKPOINT (Ch 17) |  advance + renew + read signals |
 +-+------------------+                                 |
   |                                                    |
   +-- zero rows -> SUPERSEDED, stop (Ch 17 section 5.3)|
   |                                                    |
   v                                                    |
  /  \                                                  |
 /sig \ yes -----------------------------------> E4     |
 \nal?/                                                 |
  \  /                                                  |
   | no                                                 |
   v                                                    |
  /  \                                                  |
 /wall\ elapsed ---------------------------------> E1   |
 \clk?/                                                 |
  \  /                                                  |
   | no                                                 |
   v                                                    |
  /  \                                                  |
 /step\ budget reached ---------------------------> E2  |
 \bdgt/                                                 |
  \  /                                                  |
   | no                                                 |
   +----------------------------------------------------+

  Exits:
    E1  wall clock   -> EXECUTING, re-enqueue immediately
    E2  step budget  -> EXECUTING, re-enqueue immediately
    E3  park         -> PARKED, NOT re-enqueued; an event wakes it
    E4  signal       -> per the signal; cancel is terminal

  Figure 18.5 -- The runtime loop and its four exits (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

  An episode's own states. It is a function invocation, so these live
  in one process and are never stored (section 5.1).

            +---------------------+
            | {{ CLAIMING }}      |
            +----+-----------+----+
                 | won       | lost
                 v           v
            +---------+   +--+------------------+
            |{{DRIVING}}   | {{ NOT STARTED }}  |  normal; take
            +----+----+   +---------------------+  other work
                 |
      +----------+----------+----------+----------+
      | E1/E2    | E3       | E4       | superseded
      v          v          v          v
  +---+------+ +-+------+ +-+------+ +-+----------+
  |{{YIELD}} | |{{PARK}}| |{{SIG}} | |{{ABANDON}}|
  +---+------+ +-+------+ +-+------+ +-+----------+
      |          |          |          |
      | release  | release  | release  | NO release:
      | requeue  | NO       | per      | we do not own
      |          | requeue  | signal   | it any more
      v          v          v          v
   +--+----------+----------+----------+---+
   |          {{ ENDED }}                  |
   +---------------------------------------+

  Illegal, and enforced:
    * two DRIVING episodes for one run   -- the lease (Ch 17)
    * ABANDON followed by any write      -- version CAS refuses it
    * PARK followed by re-enqueue        -- an event wakes a park,
                                            not the queue
    * ENDED without release              -- unless ABANDON, where
                                            the lease is not ours

  Figure 18.6 -- Episode states (D6 State Diagram)
```

### 7.1 The abandon path writes nothing

`[INF]` Worth isolating because it is counter-intuitive. When a checkpoint affects zero rows, the
worker has learned it was superseded — and its correct behaviour is to write *nothing at all*, not
even a release. It does not own the lease; releasing would be writing to a row another worker is
driving.

It stops, logs, and drops the run. Chapter 17's CAS already protected the row; the loop's job is to
not compound the situation.

### 7.2 The loop holds no state between episodes

Everything the loop needs at the start of an episode comes from `ClaimedRun` (Chapter 17 §9). Nothing
is cached in the worker, nothing is carried across, and two workers are interchangeable at every
boundary.

`[INF]` The test is Chapter 8 §5.4's: a worker that has been running a week and one that booted nine
seconds ago must behave identically. Any loop-local cache — an assembled context, a plan, a tool
result — breaks that and reintroduces the run-pinned-to-worker coupling the whole design removes.

---

## 8. Internal APIs

```python
from typing import Protocol
from datetime import timedelta


class RunDriver(Protocol):
    """The loop. Sequences ports; decides nothing (section 5.2)."""

    async def drive_episode(
        self,
        run_id: RunId,
        worker_id: str,
        limits: EpisodeLimits,
    ) -> EpisodeOutcome:
        """Claim, advance under the limits, release.

        Never raises on a lost claim -- that is a normal outcome and
        returns NOT_STARTED. Never raises on Superseded either: it
        returns ABANDONED, having written nothing (section 7.1).
        """


@dataclass(frozen=True)
class EpisodeLimits:
    wall_clock: timedelta        # E1: bounds one run's hold on a worker
    step_budget: int             # E2: bounds work between plan-level
                                 #     checkpoints. 1 is legal and
                                 #     expensive (section 5.5)
    lease: timedelta             # Ch 17 section 5.5
    drain_grace: timedelta       # Ch 8 section 6.3
```

`[INF]` `EpisodeLimits` being one frozen structure rather than four loose parameters is deliberate:
the four numbers interact (Chapter 17 §5.5's floor relates the lease to step duration, and the drain
grace must exceed p99 step), so they are chosen together or they are chosen wrongly. Chapter 38 pins
this structure with the harness version, which is what makes `[AHE §4.3]`'s timeout-coupling hazard a
versioned change rather than a config tweak.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class ExitCondition(StrEnum):
    WALL_CLOCK = "wall_clock"      # E1
    STEP_BUDGET = "step_budget"    # E2
    PARK = "park"                  # E3
    SIGNAL = "signal"              # E4
    TERMINAL = "terminal"          # the run finished
    SUPERSEDED = "superseded"      # we lost the lease; wrote nothing
    NOT_STARTED = "not_started"    # lost the claim race


@dataclass(frozen=True)
class EpisodeOutcome:
    run_id: RunId
    exit: ExitCondition
    steps_taken: int               # Ch 34's steps-per-episode metric
    duration_ms: int
    checkpoints: int               # must equal steps_taken
    final_version: int | None      # None when SUPERSEDED
    cost_cents: int
```

`[INF]` `checkpoints` existing alongside `steps_taken` looks redundant and is a deliberate invariant:
they must be equal, always. A single assertion in the outcome catches "checkpoint at the end"
(Chapter 17 §1.4's framing error) and any future optimisation that skips a checkpoint on a cheap
step. It is the cheapest structural guard in Level 2.

---

## 10. Communication

```
                                                            LAYER VIEW

  queue        ====> loop       ~100 B    run_id only (Ch 8)
  loop         ====> state mgr  ~2-20 KB  claim
  loop         <==== ports      varies    the six of them (Ch 10-14)
  loop         ====> state mgr  ~1-5 KB   CHECKPOINT, once per step
  loop         ====> observation ~2-20 KB spans, fire-and-forget
  loop         ====> queue      ~100 B    re-enqueue on E1/E2

  Per episode of 8 steps:
    1 claim + 8 checkpoints + 1 release  = 10 writes to `runs`
    8 step rows appended
    the model and tool traffic dwarfs all of it (Ch 9)

  Figure 18.7 -- What the loop moves (D7 Data Flow)
```

```
                                                             TIME VIEW

  relay ---------> loop          here is a run to advance
  loop ----------> planner       propose (Ch 10)
  loop ----------> tool engine   dispatch (Ch 14)
  loop ----------> state mgr     claim, checkpoint, release
  loop --X         any decision  REFUSED: it sequences (section 5.2)
  loop --X         domain state  REFUSED: commands cross the waist
  signals --X      the loop      not delivered; READ at checkpoint
  a superseded loop --X the row  zero rows; it writes nothing at all

  Figure 18.8 -- Who advances a run (D8 Control Flow)
```

```
                                                             TIME VIEW

  << run.step.completed >>   ....> in the checkpoint transaction, so
                                   progress and its announcement are
                                   atomic (Ch 9 section 5.2)
  << run.parked >>           ....> with the resolution condition, so
                                   the right event can wake it
  << run.episode.ended >>    ....> exit condition and steps taken;
                                   the input to Ch 34's distribution

  NOT events:
    claims, releases         ownership churn; telemetry
    the loop's iterations    there is no such fact
    exit-condition tests     internal control flow

  Figure 18.9 -- What the loop makes durable (D9 Event Flow)
```

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 21 Durable Execution | checkpoint-per-step; identity checked before dispatch | replay resumes at a step boundary |
| Ch 23 Scheduler | E1 and E2 as fairness mechanisms | the loop yields so admission can act |
| Ch 29 Long-Running | wall clock, step budget, the boredom failure | six-hour runs are many episodes |
| Ch 33 Scalability | steps/sec and checkpoint rate | every capacity number starts here |
| Ch 35 Cost | budget checked before planning | cost per episode is bounded here |
| Ch 38 Deployment | `EpisodeLimits` pinned with the harness | timeout coupling is a versioned change |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Signals read at episode end | a separate read outside the checkpoint | cancellation latency ~ episode length | read in the checkpoint — the cold open |
| Run to completion | no episode bound | deploys blocked; long crash losses | bound with E1 and E2 |
| Transaction around the loop body | "for consistency" | pool exhausted at low concurrency | nothing scarce across a call (§5.3) |
| Checkpoint at episode end | "every step is wasteful" | `checkpoints != steps_taken` | the invariant in §9 |
| Loop acquires a decision | convenience: it knows the answer | a port with nothing left to decide | §5.2's table |
| Step budget 1 in production | left after an incident | steps-per-episode mode of 1 | a dial, not a default (§5.5) |
| Writing after Superseded | tidy release on the way out | version conflicts from an abandoned worker | write nothing (§7.1) |
| Loop-local cache | avoiding a re-read across episodes | behaviour differing by worker age | hold nothing between episodes (§7.2) |
| A fifth exit condition | an `if` added to the loop | episodes ending for unexplained reasons | four, and the evaluator is a component |
| Park re-enqueued | uniform treatment of exits | parked runs spinning through the queue | E3 does not re-enqueue |

`[INF]` Row nine is the quiet one. Every new exit condition seems reasonable in isolation — "yield if
the tenant is over quota", "yield if the model is slow" — and each one makes "why did this episode
end?" harder to answer. Both examples belong somewhere else: the first is admission control
(Chapter 23), the second is the model port's concern (Chapter 13). Keeping the exits at four is
what keeps the loop explicable.

---

## 12. Scalability

### 12.1 The three numbers that set everything downstream

| Number | Bounds | Downstream effect |
|---|---|---|
| Wall clock per episode | one run's hold on a worker | worker fairness (Ch 23) |
| Step budget | work between plan checkpoints | cost per episode (Ch 35) |
| Lease period | undetected orphan time | recovery SLO (Ch 8, Ch 17) |

`[INF]` A defensible starting set for sub-second steps and tens-of-seconds activities: **sixty-second
wall clock, step budget eight, sixty-second lease, ten-second drain.** Every one should move once
measured, and the step budget should move first because it is the one with a cache consequence.

### 12.2 Worker concurrency is not pool size

`[DAR §5.2]` Because §5.3 holds nothing across a model call, a worker awaiting a completion consumes
a model-semaphore slot and no connection. So:

```
  workers          bounded by  memory and the model semaphore
  connections      bounded by  checkpoint rate x checkpoint duration
                               (~5 ms), NOT by concurrent runs
```

`[INF]` At eight workers each driving a run with a ninety-second activity in flight, the connection
pool sees roughly eight five-millisecond writes per step — a load a pool of ten handles comfortably
while a naive reading would demand eight held connections. This is the concrete payoff of the custody
gradient, and it is why Chapter 33's sizing starts from checkpoint rate rather than run count.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Exit condition distribution | why episodes end | E4 rising means cancellations; E1 dominating means slow steps |
| Steps per episode | §5.5's diagnostic | mode of 1 |
| `checkpoints == steps_taken` | the §9 invariant | any violation |
| Cancellation latency p99 | the cold open, measured | above one step's p99 |
| Superseded rate | zombie workers | any sustained non-zero |
| Episode duration vs wall clock | are we hitting E1 constantly | p99 at the limit |
| Claim races lost | too many pollers | high ratio to successful claims |

`[INF]` The exit-condition distribution is the single most informative chart for this chapter, and it
is nearly free — one label on one counter. A healthy system is mostly E2 with some E3; heavy E1 means
steps are slower than the budget assumes, and any E4 that is not a user cancellation means something
is signalling that should not be.

### 13.2 The test that catches the cold open

```python
async def test_cancellation_is_honoured_within_one_step(
    runtime: Runtime, clock: FakeClock
) -> None:
    run = await runtime.submit(long_goal)     # would take many steps
    await runtime.wait_until_step(run, 2)

    await runtime.signal(run, Signal.cancel())
    steps_at_cancel = await runtime.current_step(run)

    outcome = await runtime.drive_until_episode_end(run)

    assert outcome.exit is ExitCondition.SIGNAL
    # The property: at most ONE more step ran after the signal landed.
    assert await runtime.current_step(run) <= steps_at_cancel + 1
    assert (await runtime.state(run)) is RunState.CANCELLED


async def test_every_step_checkpoints(runtime: Runtime) -> None:
    outcome = await runtime.drive_one_episode(run)
    assert outcome.checkpoints == outcome.steps_taken
```

`[INF]` The `<= steps_at_cancel + 1` assertion is the one that fails against the cold open's
implementation and passes against this one. A weaker assertion — that the run eventually cancels —
passes against both, which is why most cancellation tests do not catch this.

---

## 14. Relation to AHE

The loop is kernel, so the Evolve Agent may not edit it. But it is where the loop's *parameters*
live, and that is where the sharpest known hazard sits.

**`EpisodeLimits` is fitted to an operating point.** `[AHE §4.3, Limitations]` reports gains that were
non-monotone across reasoning tiers, with step budget and per-task timeout implicated. `[INF]` Those
two numbers are §8's structure. A harness tuned at one tier encodes assumptions about how many steps
the model takes and how long each takes — both of which change with the tier — so a limits structure
that does not travel with the model identity is describing a configuration that does not exist. That
is Chapter 1's cold open, and this chapter is where the numbers actually live.

**Everything the loop calls is editable; the loop is not.** `[INF]` That split is what makes the
harness evolvable at all. Six ports, each independently replaceable, sequenced by forty lines nobody
may touch. The Evolve Agent can change what the planner proposes, what the model sees, and what the
tools say — and it cannot change the order in which they are consulted, which is where the safety
properties live.

**Episodes make an iteration measurable.** Chapter 41 scores rollouts, and a rollout is a run made of
episodes with a known exit condition each. `[INF]` A run that ended on E3 park awaiting a human is
not a failure and must not be scored as one — a distinction only available because the exit condition
is recorded rather than inferred from the final state.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the episode as a bounded execution window, checkpoint after every step, the four
exit conditions, the rule that no scarce resource is held across a model call, reading signals at the
checkpoint, exactly one driver per run at any instant, and the step budget as a configuration dial
`[DAR §5.1–5.3, §13]`.

**`[AHE]`** Supplies the timeout-coupling hazard and the non-monotone tier result that make
`EpisodeLimits` a versioned artifact `[AHE §4.3, Limitations]`.

**`[INF]`** The handbook's own: the derivation that episodes follow from having checkpointed rather
than from efficiency, the relay analogy and the observation that there is no transfer to fail, the
catalogue of what the loop is forbidden to do, cancellation latency as one step plus a checkpoint,
the argument that step budget 1 is expensive chiefly through cache loss, the
`checkpoints == steps_taken` invariant, the abandon path writing nothing, and the warning that a
fifth exit condition is how the loop becomes inexplicable.

**`[BP]`** Lease-based work distribution with bounded processing windows is standard in queue
workers and stream processors. The contribution is the four-exit taxonomy and the insistence that
signals are read rather than delivered.

**`[FUT]`** Nothing here is speculative. `[FUT]` The one open question is adaptive limits — a step
budget that responds to measured cache-hit ratio and step duration rather than being fixed per work
class. It is plausible and the handbook knows of no production system doing it, so it is stated as an
idea rather than a recommendation.

---

## 16. Key Takeaways

1. **The loop sequences and never decides.** Six ports hold every judgement; the loop is about forty
   lines. A loop that acquires a decision has moved it into the one component nobody may edit.
2. **Episodes follow from checkpointing, not from efficiency.** Once progress is durable, holding the
   worker buys nothing — and teams that resist episodes are usually already paying the checkpoint
   cost.
3. **Four exit conditions, and no fifth.** Wall clock, step budget, park, signal. Each new one makes
   "why did this episode end?" harder to answer, and both tempting candidates belong to other
   chapters.
4. **Checkpoint after every step, and read signals inside it.** That is what makes cancellation
   latency one step rather than one episode — the difference between the two designs is where a
   `SELECT` sits.
5. **Nothing scarce crosses a model call.** No connection, no transaction, no lock. This is why
   worker concurrency is unrelated to pool size, and wrapping the loop body in a transaction destroys
   it.
6. **Step budget 1 is legal and expensive.** Its real cost is the prompt cache, which no latency
   metric shows. Useful for debugging; a poor default.
7. **A superseded worker writes nothing.** Not even a release. It does not own the lease, and the CAS
   has already protected the row.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Runtime loop** | The forty lines that claim a run, advance it under bounded limits, and release it, calling six ports and deciding nothing. | `[DAR]` | Ch 21, Ch 29 |
| **Run driver** | The kernel component that is the runtime loop; Chapter 3's replacement for the banned word. | `[DAR]` | Ch 32 |
| **Episode limits** | Wall clock, step budget, lease, and drain grace, chosen together because they interact, and pinned with the harness version. | `[INF]` | Ch 38 |
| **Exit condition** | One of exactly four reasons an episode ends, recorded rather than inferred. | `[DAR]` | Ch 34, Ch 41 |
| **Wall-clock exit (E1)** | Bounds one run's hold on a worker, so slow steps cannot monopolise it. | `[DAR]` | Ch 23 |
| **Step-budget exit (E2)** | Bounds work between plan-level checkpoints, making cost per episode predictable. | `[DAR]` | Ch 35 |
| **Signal exit (E4)** | Ending an episode because a cancel, pause, or steer was read at a checkpoint. | `[DAR]` | Ch 30 |
| **Cancellation latency** | One step plus a checkpoint; determined entirely by where signals are read. | `[INF]` | Ch 30, Ch 36 |
| **Superseded abandon** | A worker that lost its lease stopping without writing anything, not even a release. | `[INF]` | Ch 32 |
| **Steps per episode** | The distribution whose mode reveals whether the step budget is doing anything. | `[INF]` | Ch 34 |

---

**Next:** Chapter 19 — *The Multi-Agent Runtime.* Sub-agents as context isolation rather than org
charts: delegation contracts, result marshalling, sandbox sharing, nesting limits, and the cases
where a sub-agent is strictly worse than a tool.
