```
  Level 1 · Chapter 8
  REQUEST LIFECYCLE AND RUNTIME LIFECYCLE
  Requires   C4 The Complete Runtime, C5 The Five Nouns,
             C6 State Separation, C7 The Edge
  Unlocks    C9 Three Flows, C17 State Manager, C18 The Runtime Loop,
             C27 Failure and Recovery, C38 Deployment
  Diagrams   Core (5)
```

# Chapter 8 — Request Lifecycle and Runtime Lifecycle

---

## 1. Motivation

### 1.1 Cold open

16:04. Atlas ships a routine deploy, and three runs that had been stuck all afternoon complete
within a minute of it.

Nobody planned that. The on-call engineer notices because a customer escalated one of those runs at
14:30, and the escalation resolves itself while she is still typing a reply.

The recovery routine runs at worker startup. It scans for runs whose lease has expired, clears them,
and re-enqueues. It was written for the case where a worker dies and its runs need rescuing — which
is the right case, and it fires at the wrong time. A worker that is OOM-killed at 02:00 orphans its
runs at 02:00. Nothing boots at 02:00. Those runs wait until something happens to restart a process,
and on a good week the only thing that restarts a process is a deploy.

The team's mental model was that the runtime has a lifecycle — boot, serve, shut down — and that
recovery belongs to boot. The system's actual behaviour is that a run has its own lifecycle,
independent of every process, and a run whose driver died is not waiting for a boot. It is waiting
for somebody to notice.

Ship less often and the defect gets worse. Its severity is inversely proportional to deploy
frequency, which is exactly why it survives staging.

### 1.2 In plain language

There are two different clocks in this system, and confusing them is the subject of this chapter.

The first clock belongs to **the work**. Somebody asks for a goal; it gets planned; steps happen;
maybe it waits a day for a human to approve something; eventually it finishes. That can take a week.

The second clock belongs to **the machines**. A worker process starts, picks up work for a few
hours, and is then shut down by a deploy, a crash, or a scale-down. That happens constantly, and it
is completely unrelated to whether any particular piece of work has finished.

The mistake almost everyone makes is to assume the second clock contains the first — that a piece of
work belongs to the process that started it. It cannot, because the work outlives the process many
times over. So a run is never *owned* by a worker; it is **borrowed**, for a few seconds at a time,
by whichever worker is free.

Borrowing needs a return date, or a worker that dies keeps the work forever. That return date is
called a lease. And a return date only helps if somebody checks whether it has passed — which is the
cold open. The checking cannot happen when a process starts, because the failure happens at 2am when
nothing is starting. It has to be a job that runs continuously, forever, whether or not anything is
wrong.

Two clocks; they touch at exactly two moments.

### 1.3 Why this chapter exists

Chapters 4 through 7 built the architecture in space: layers, nouns, state categories, and the
boundary a client talks to. This chapter builds it in **time**, and time is where the two most
expensive category errors in agent runtimes live.

The first is the cold open: putting recovery on the runtime's clock when it belongs on the run's.
The second is its mirror image — putting deployment safety on the run's clock, by trying to let runs
"finish" before a deploy proceeds. Both come from the same missing distinction, and both produce
systems that appear correct for months and then fail in a way that resists reproduction.

By the end of this chapter you should be able to answer, for any moment in a run's life: which
process is responsible for it right now, what happens if that process disappears this instant, and
how long it takes anybody to find out.

### 1.4 What previous framings got wrong

**"A run is a long request."** The framing that produces every mistake in this chapter. A request
has a caller who is waiting, a connection that defines its lifetime, and a natural cancellation
signal when the caller gives up. A run has none of the three `[DAR §4.1]`. Chapter 7 established
that the run outlives the connection; this chapter establishes that it outlives the *process* too,
which is the part with architectural consequences.

**"Graceful shutdown means finishing what you started."** Correct for a request server and
catastrophic here. A run can take six hours; a deploy cannot wait six hours. Draining means giving
back what you borrowed, not completing it — and §6.3 shows that the difference is about four lines
of code and roughly an hour of deploy latency.

**"Recovery is a startup concern."** `[INF]` The cold open. Recovery is a *continuous* concern
whose correctness must not depend on anything restarting. The sweeper from Chapter 4 is not a
housekeeping detail; it is the only component that closes the loop between a dead worker and a
recoverable run.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A restaurant kitchen during service.

**Orders** have their own life. A ticket is taken, it goes up on the rail, it is cooked, it is
plated, it goes out. Some tickets sit waiting for a table to be ready. A ticket's life is measured
in the thing it is about — this table's dinner — and nothing else.

**Staff** have shifts. A chef clocks in at four, works, and clocks out at eleven. Shifts have
nothing to do with tickets. No sensible kitchen tells a chef "you may not go home until your ticket
is served"; and no sensible kitchen throws away a ticket because the chef who picked it up went
home.

So the rail exists. A ticket on the rail belongs to the kitchen, not to a person. A chef takes one
down, works it, and puts it back — and if a chef walks out mid-service, their ticket does not
vanish. It is still on the rail, and somebody else picks it up.

Now the part that is this chapter's thesis. What actually makes that work is not the rail; it is
the **expeditor** — the person standing at the pass whose entire job is to watch for tickets that
have been sitting too long. They do not do that at shift change. They do it continuously, because
tickets go cold at times unrelated to when anybody clocks in or out.

**Where the analogy breaks.** A kitchen gets its expeditor for free: any competent person standing
at the pass will notice a ticket that has been up for forty minutes, because humans notice things.
A runtime notices nothing. There is no ambient awareness, no peripheral vision, and no colleague who
happens to glance over. If you do not build the expeditor as an explicit, continuously running
process with its own schedule — the sweeper — then nothing whatsoever is watching, and the cold open
is what that silence looks like from the outside: work that mysteriously heals itself whenever
somebody happens to walk through the kitchen.

### 2.2 Why the two lifecycles must be separated

The separation is not a modelling preference. It is forced, and the derivation ends by telling you
exactly where the sweeper comes from:

```
  1. A run can last a week. A worker process lasts until the next
     deploy -- hours, maybe days.
  2. So any given run necessarily spans many process lifetimes.
  3. If the run's progress lives in the process that started it, the
     run dies when that process does. Unacceptable (Ch 2).
  4. Therefore run state lives in durable storage, outside every
     process.
  5. Once the state is outside, no process OWNS the run. A process can
     only borrow it for a while. (This is Ch 3's MM1, and the Ch 3
     cold open.)
  6. A borrower can die mid-borrow. So the borrow must carry an
     expiry, or dead borrowers hold runs forever. That expiry is the
     lease.
  7. An expiry is inert unless something evaluates it. The run cannot
     evaluate its own -- it is not executing; that is the whole
     problem.
  8. And the borrowing process cannot evaluate it either, because the
     case we care about is precisely the one where that process no
     longer exists.
  9. So evaluation must come from somewhere that is running when both
     the run and its borrower are not: a continuously scheduled job
     belonging to the RUNTIME's lifecycle.
 10. That job is the sweeper. It is not optional, and it cannot be a
     startup routine, because step 8 says the failure happens when
     nothing is starting.
```

Step 9 is worth sitting with. The sweeper is the *only* place in the architecture where the
runtime's lifecycle acts on the run's lifecycle without being asked. Everything else in this system
is triggered by an event or a request. The sweeper is triggered by the passage of time alone, which
is why it is the component that closes an otherwise open loop.

### 2.3 Two lifecycles, two meeting points

`[INF]` The organising claim of the chapter:

> **The run lifecycle and the runtime lifecycle are independent state machines. They touch at
> exactly two points: a worker claims a run, and a sweeper releases one. Every other apparent
> interaction between them is a defect.**

That is a strong statement and it is meant to be used as a test. When you find code where a deploy
changes a run's state, or where a run's completion changes a worker's behaviour, you have found a
third meeting point — and third meeting points are where the cold open lives.

| | Run lifecycle | Runtime lifecycle |
|---|---|---|
| Unit | one goal | one process |
| Duration | minutes to weeks | hours to days |
| Lives in | a row in `runs` | memory and a supervisor |
| Ends when | the goal is met, refused, or cancelled | deploy, crash, or scale-down |
| Count | thousands, concurrent | tens |
| Who ends it | the plan, a human, or a budget | an operator or the platform |
| Survives the other? | **yes, always** | irrelevant — it has nothing to survive |

Read the last row twice. The asymmetry is total: runs must survive processes, and processes have no
obligation to runs at all. A worker's correct behaviour on shutdown is to *let go*, not to finish.

### 2.4 The four-quadrant test

`[INF]` A quick diagnostic for any piece of lifecycle code you meet. Ask which clock triggers it and
which clock it changes:

| Triggered by | Changes | Verdict |
|---|---|---|
| run event | run state | normal — the run driver |
| process event | process state | normal — boot, drain, health |
| process event | run state | **only legal at claim and drain-release** |
| time alone | run state | the sweeper — exactly one component |

The cold open is row three used illegally: a process-start event changing run state. It reads as
harmless because it fixes things when it fires. The defect is entirely in when it does not fire.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  RUN LIFECYCLE                          RUNTIME LIFECYCLE
  (thousands, concurrent)                (tens of processes)

  +--------------------------+           +--------------------------+
  |                          |           |  EDGE PROCESS            |
  |   {{ CREATED }}          |           |  boot . serve . drain    |
  |        |                 |           |  stateless; holds no run |
  |        v                 |           +--------------------------+
  |   {{ PLANNING }}         |
  |        |                 |           +--------------------------+
  |        v                 |    (1)    |  WORKER PROCESS          |
  |   {{ EXECUTING }} <------------------|  boot                    |
  |        |     ^           |   claim   |   |                      |
  |        v     |           |           |   v                      |
  |   {{ AWAITING_ACTIVITY }}|           |  serve: claim, drive,    |
  |        |     |           |    (2)    |        checkpoint, release
  |        v     |           |<----------|   |                      |
  |   {{ PARKED }}-----------+  release  |   v                      |
  |        |                 |           |  drain: release ALL,     |
  |        v                 |           |         finish NOTHING   |
  |   {{ SUCCEEDED }}        |           |   |                      |
  |   {{ FAILED }}           |           |   v                      |
  |   {{ CANCELLED }}        |           |  exit                    |
  |   {{ DEAD_LETTERED }}    |           +--------------------------+
  |                          |
  +--------------------------+           +--------------------------+
              ^                   (3)    |  SWEEPER                 |
              +--------------------------|  runs forever, on a      |
                    expire + re-enqueue  |  schedule, owned by      |
                                         |  neither lifecycle       |
                                         +--------------------------+

  Figure 8.1 -- The two lifecycles and their meeting points
                (D1 High-Level Architecture)

  (1) claim: a worker takes a lease on a run it does not own
  (2) release: the worker gives the lease back, at an episode
      boundary or at drain -- in both cases without finishing
  (3) expire: the sweeper acts on elapsed time alone, and is the
      only path by which a dead worker's run becomes available
```

Three wires, and only three. Wire 1 and wire 2 are the two legal meeting points from §2.3. Wire 3 is
the one that exists because wires 1 and 2 can be interrupted by a process disappearing between them.

Note what is *not* on this diagram: there is no arrow from run completion back into the worker
process, and no arrow from deploy into run state. A run finishing is not an event in a worker's life
— the worker loops and claims something else `[DAR §5.1]`.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  THE RUN LIFECYCLE, opened
  +--------------------------------------------------------------+
  | arrival    edge writes runs row + goal, state CREATED,        |
  |            emits << run.created >>, returns 202 + run_id      |
  |            HOLDS: nothing. The edge is already done.          |
  |                                                              |
  | admission  relay claims the event, admission control decides  |
  |            accept / defer / refuse, enqueues if accepted      |
  |                                                              |
  | claim      a worker CASes lease_owner + lease_until           |
  |            exactly one worker wins; the rest move on          |
  |                                                              |
  | episode    N steps, checkpoint after each (Ch 5)              |
  |            exit: E1 wall clock . E2 step budget               |
  |                  E3 park       . E4 signal                    |
  |                                                              |
  | release    final checkpoint, lease cleared, re-enqueue if     |
  |            the run is not terminal                            |
  |                                                              |
  | terminal   SUCCEEDED . FAILED . CANCELLED . DEAD_LETTERED     |
  |            no lease, no queue entry, retained for audit       |
  +--------------------------------------------------------------+

  THE RUNTIME LIFECYCLE, opened
  +--------------------------------------------------------------+
  | boot       load config, pin model + harness version,          |
  |            open pools, register health, start consuming       |
  |            DOES NOT: scan for orphans, mutate any run         |
  |                                                              |
  | serve      loop { claim -> drive one episode -> release }     |
  |                                                              |
  | drain      SIGTERM received:                                  |
  |              1. stop claiming new work        (immediate)     |
  |              2. finish the CURRENT STEP only  (~seconds)      |
  |              3. checkpoint                                    |
  |              4. release every lease held      <-- the key     |
  |              5. re-enqueue those runs                         |
  |              6. exit                                          |
  |            budget: seconds, never the length of a run         |
  |                                                              |
  | exit       process gone; zero runs affected                   |
  +--------------------------------------------------------------+

  THE SWEEPER, opened            belongs to NEITHER lifecycle
  +--------------------------------------------------------------+
  | every T seconds, forever:                                     |
  |   expire run leases    WHERE lease_until < now                |
  |   expire activity leases, same predicate                      |
  |   dead-letter runs whose attempts exceed the cap              |
  |   wake parks whose wake_at has passed                         |
  |   re-enqueue everything it touched                            |
  | idempotent: two sweepers running concurrently is safe         |
  +--------------------------------------------------------------+

  Figure 8.2 -- Each lifecycle, decomposed (D2 Low-Level Architecture)
```

`[INF]` The line worth memorising from the middle block is step 2 of drain: **finish the current
step, not the current run.** A step is milliseconds to seconds because Chapter 5's custody gradient
made it so. That is what allows a drain budget of ten seconds to be honest rather than aspirational,
and it is a direct dividend of a decision made two chapters ago for apparently unrelated reasons.

The sweeper's idempotency, stated in the last block, is what allows you to run it in every worker
rather than electing a leader. Two sweepers expiring the same lease produce the same result as one
`[DAR §5.3]`; the CAS makes the second a no-op. Leader election here would be a scarce, fragile
mechanism bought to solve a problem that idempotency solves for free.

---

## 5. The Two Lifecycles Side by Side

### 5.1 Arrival is not a start

A run's row exists before any process has looked at it. That sounds trivial and it disposes of a
whole class of design. There is no "failed to start" state, because starting is not an event that
can fail — an unclaimed run is `CREATED` and enqueued, which is a resting state rather than a
stalled one. Load shedding therefore loses no work: if admission control defers, the row and the
goal are already durable and only the claiming is postponed `[DAR §5.4]`. And the edge can return
`202 Accepted` with a `run_id` the client may query immediately, because the identity was minted
before any work began (Chapter 7 §9).

### 5.2 A run is claimed, never assigned

Assignment implies a scheduler that knows about workers. This architecture has none: workers pull.
The consequence is that the interesting question is never "which worker should get this run?" but
"what happens when the worker that has it stops existing?" — which is §5.5.

`[DAR §5.3]` The claim is a compare-and-swap, not a lock:

```sql
UPDATE runs
   SET lease_owner = :worker_id,
       lease_until = now() + :lease_duration,
       version     = version + 1
 WHERE id = :run_id
   AND (lease_until IS NULL OR lease_until < now())
   AND version = :expected_version;
```

Zero rows updated means somebody else won; the worker moves on without error. This is the entire
mutual-exclusion mechanism for the system, and it holds no database resource between statements —
which is why Chapter 2's advisory-lock instinct is wrong here.

### 5.3 The run's clock is not wall-clock

`[INF]` A run that has existed for six days has not been *working* for six days. Three durations
matter and teams routinely report the first when they mean the third:

| Duration | Measures | Typical | Used for |
|---|---|---|---|
| Wall age | `now - created_at` | hours to weeks | SLO on the customer's experience |
| Active time | sum of episode durations | seconds to minutes | capacity planning (Ch 33) |
| Parked time | wall age minus active | hours to weeks | approval-latency SLO (Ch 30) |

A run that is 99% parked time is not a slow run; it is a run waiting on a human, and the fix is
never in the runtime. Chapter 34 makes this split a required dashboard, because "p95 run duration"
computed on wall age is a number that measures your customers' meeting schedules.

### 5.4 The runtime's clock has exactly four events

Boot, serve, drain, exit. The discipline is in what is *absent*: no recovery at boot (the sweeper
covers it continuously, and a boot scan is at best a duplicate and at worst — the cold open — a
substitute); no warm-up, because a worker holds nothing about any run between episodes; no "finish
current work" on shutdown, per §6.3; and no leader, because every worker is interchangeable,
including for sweeping.

`[INF]` A worker that has been running for a week and one that booted nine seconds ago are
behaviourally identical. If that is not true of yours, they are holding state that Chapter 6 says
belongs in the substrate.

### 5.5 The interruption matrix

The question §5.2 said was the interesting one. For each point where a process can vanish, what is
lost and who notices:

| Process dies during | Lost | Detected by | Latency to recovery |
|---|---|---|---|
| Before claim | nothing | nothing to detect | none |
| Between claim and first step | nothing | sweeper, on lease expiry | one lease period |
| Mid-step, before checkpoint | that step's in-memory work | sweeper | one lease period |
| Mid-activity (model call in flight) | possibly the spend, never the result | sweeper; activity replay on resume | one lease period |
| After checkpoint, before release | nothing | sweeper | one lease period |
| During drain | nothing | drain released the lease itself | immediate |

Every row's detector is the sweeper, and every row's latency is one lease period. That uniformity is
the design working: there is exactly one recovery mechanism, so there is exactly one number to tune
and exactly one thing to test.

Row four is the one with money attached. A model call in flight when the worker died may have
completed and been billed, with its result never written. Activity identity (Chapter 21) is what
makes the resumed run reuse that result instead of buying it twice — and it works because the
identity was computed at plan time, before the call, rather than derived from it afterwards
`[DAR §6.1]`.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  edge      worker A         worker B         sweeper        runs table
   |            |                |               |                |
   |--- POST goal ------------------------------------------------>|
   |            |                |               |   CREATED, v1   |
   |<-- 202 run_id ---------------------------------------------- |
   |            |                |               |                |
   |            |--- claim CAS ------------------------------------>|
   |            |                |               |  lease=A, v2    |
   |            |  episode 1: 4 steps, checkpoint after each        |
   |            |--- checkpoint ----------------------------------->| v3..v6
   |            |--- release + requeue -------------------------->| lease=NULL
   |            |                |               |                |
   |            |                |--- claim CAS -------------------->|
   |            |                |               |  lease=B, v7    |
   |            |                |  episode 2: step 5 dispatches    |
   |            |                |  an activity, then...            |
   |            |                X   <-- OOM kill, no drain         |
   |            |                                |                |
   |            |                                |  ...lease sits  |
   |            |                                |  until expiry.  |
   |            |                                |  NOTHING boots. |
   |            |                                |                |
   |            |                     (lease_until passes)         |
   |            |                                |--- expire ---->| lease=NULL
   |            |                                |--- re-enqueue   | v8
   |            |                |               |                |
   |            |--- claim CAS ------------------------------------>|
   |            |                |               |  lease=A, v9    |
   |            |  resume at step 5. Activity identity is           |
   |            |  unchanged, so the in-flight model call's         |
   |            |  result is reused, not re-purchased.              |
   |            |--- checkpoint ----------------------------------->| v10
   |            |                |               |                |

  Figure 8.3 -- One run across three worker lifetimes, including an
                undrained death (D4 Sequence)
```

### 6.1 Reading the failure branch

The `X` is the whole chapter. Worker B does not get to run any code — an OOM kill is not a signal
you can handle. So every mechanism that depends on the dying process doing something is unavailable:
no cleanup, no lease release, no error event, no log line worth having.

What survives is the row. The lease has an expiry written into it *before* the work began, by the
claim in §5.2, which is why an expiry is the only recovery mechanism that survives the case you are
actually recovering from.

### 6.2 Why the version numbers matter

Each checkpoint increments `version`, which does two jobs: it is the CAS guard that lets exactly one
worker advance the run, and it is a count of advances that costs no events. Chapter 17 builds the
mechanism. Here it is enough to see that a resumed run continues the sequence rather than restarting
it — v9 follows v8, and no version is ever reused.

### 6.3 Drain, in four lines

The correct shutdown handler, in full:

```python
async def on_sigterm(worker: Worker) -> None:
    worker.stop_claiming()                    # 1. take no new runs
    await worker.current_step_or_timeout(10)  # 2. finish the STEP
    await worker.checkpoint_all()             # 3. persist progress
    await worker.release_all_leases()         # 4. give everything back
```

`[INF]` Line 4 is the one teams omit, and omitting it is not a crash — it is a *slow* deploy.
Without it, every rolled worker's runs wait one full lease period before the sweeper frees them. At
a sixty-second lease and twenty workers rolled over ten minutes, that is a ten-minute window in
which a portion of the fleet's work is sitting idle for no reason. The system still converges, which
is exactly why nobody investigates.

Line 2's timeout must exceed your p99 step duration and must be far below your p50 *activity*
duration — because a step that dispatched an activity does not wait for it (Chapter 5's custody
rule). If those two numbers are not comfortably separated in your system, the custody gradient has
been violated somewhere and §12 will show it as a drain that regularly times out.

---

## 7. State Management

```
                                                            STATE VIEW

                     +-------------+
                     | {{CREATED}} |  row exists, nothing claimed
                     +------+------+
                            | admitted + claimed
                            v
                     +--------------+
              +----->| {{PLANNING}} |<-------------+
              |      +------+-------+              |
              |             | plan minted          | steer:
              |             v                      | new plan_id
              |      +---------------+             |
              |      | {{EXECUTING}} |-------------+
              |      +---+-------+---+
              |          |       | dispatch
    activity  |          |       v
    resolved  |          |  +----------------------+
              +----------|--| {{AWAITING_ACTIVITY}}|
                         |  +----------------------+
                         | gate raised / input needed / timer
                         v
                  +-------------+
                  | {{PARKED}}  |  holds NOTHING
                  +------+------+
                         | resolving event
                         v
        +----------------+-----------------+
        v         v            v           v
  {{SUCCEEDED}} {{FAILED}} {{CANCELLED}} {{DEAD_LETTERED}}

  Illegal transitions, enforced in the run driver:
    * any terminal state -> any state         (terminal is terminal)
    * PARKED -> EXECUTING without an event    (no polling out of a park)
    * EXECUTING -> EXECUTING on a new worker  (needs claim + version CAS)
    * any state -> any state without a version increment

  Figure 8.4 -- Run states and legal transitions (D6 State Diagram)
```

### 7.1 The states are run state, and only run state

Every box above is a value in the `runs` row — Chapter 6's run state category, owned by the runtime,
gone when the run is deleted. None of it is domain state. Atlas's `patches` table has no idea that
`AWAITING_ACTIVITY` exists, and that is the deletion test passing.

`[INF]` A useful smell: if a state name in this machine contains a domain word — `PATCH_REVIEW`,
`AWAITING_MERGE` — the waist has been breached and Chapter 4's narrow-waist rule is being violated
in the state machine rather than in the schema, where it is much harder to see.

### 7.2 The runtime has a state machine too, and it is trivial

```
  boot ----> serving ----> draining ----> exited
              ^   |
              +---+  (claim, drive, release, repeat)
```

Four states, one loop, no branches worth a diagram of their own. The asymmetry between the two
machines is the point: all of the interesting state belongs to the work, and the process is nearly
stateless. A worker with a rich lifecycle is a worker holding something it should have written down.

### 7.3 Where the two machines are allowed to touch

Only two runtime transitions may write run state, and they are the two wires of Figure 8.1: a
worker entering `serving` may claim (`lease_owner`, `lease_until`, `version`), and a worker
entering `draining` may release (`lease_owner := NULL`, re-enqueue). `boot → serving` and
`draining → exited` may touch no run at all — and the cold open is a system where the first of
those two had an effect.

---

## 8. Internal APIs

```python
from typing import Protocol
from datetime import datetime, timedelta


class RunLifecyclePort(Protocol):
    """Transitions on the run's clock. Every method is idempotent and
    every mutation carries a version for CAS."""

    async def create(self, goal: Goal, tenant_id: str) -> RunId: ...

    async def claim(
        self,
        worker_id: str,
        lease: timedelta,
        work_class: str | None = None,
    ) -> ClaimedRun | None:
        """Compare-and-swap a lease onto one eligible run.

        Returns None when no run is available or another worker won the
        race. A lost race is a normal outcome, never an error.
        """

    async def checkpoint(
        self,
        run_id: RunId,
        expected_version: int,
        state: RunState,
        renew_lease_for: timedelta,
    ) -> CheckpointResult:
        """Persist progress, renew the lease, and read pending signals
        in one transaction. Fails closed if expected_version is stale:
        another worker is driving and this one must stop."""

    async def release(
        self,
        run_id: RunId,
        expected_version: int,
        requeue: bool,
    ) -> None: ...


class RuntimeLifecyclePort(Protocol):
    """Transitions on the process's clock. Nothing here may mutate run
    state except drain, which releases and re-enqueues only."""

    async def boot(self) -> None: ...
    async def serve(self) -> None: ...
    async def drain(self, budget: timedelta) -> DrainReport: ...


class SweeperPort(Protocol):
    """Belongs to neither lifecycle. Triggered by elapsed time alone.
    Safe to run concurrently in every worker."""

    async def sweep(self, now: datetime) -> SweepReport: ...
```

`[INF]` The separation into two Protocols is not decoration. It is the boundary that makes the
four-quadrant test of §2.4 checkable by a linter: a module that imports `RuntimeLifecyclePort` and
calls anything on `RunLifecyclePort` other than `claim` or `release` is the defect, and that is a
grep rather than a code review.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class ClaimedRun:
    run_id: RunId
    tenant_id: str
    version: int                 # CAS guard for every later write
    state: RunState
    plan_id: PlanId | None
    current_step: int
    lease_until: datetime
    budget_cap_cents: int
    budget_used_cents: int
    created_at: datetime         # wall age starts here
    active_ms: int               # sum of prior episode durations


@dataclass(frozen=True)
class DrainReport:
    leases_released: int
    runs_requeued: int
    steps_completed_during_drain: int
    timed_out: bool              # true means the custody gradient leaked


@dataclass(frozen=True)
class SweepReport:
    run_leases_expired: int
    activity_leases_expired: int
    parks_woken: int
    dead_lettered: int
    oldest_expiry_lag_ms: int    # the chapter's headline metric
```

`oldest_expiry_lag_ms` — how long the most overdue lease had been overdue when the sweeper reached
it — deserves its place in a structure this small. It is the direct measurement of the cold open. In
a healthy system it sits at roughly half the sweep interval. In the cold open's system, it would
have read six hours, every night, in a field nobody had created.

`timed_out` on `DrainReport` is the same idea for the other lifecycle: a drain that times out means
step 2 of §6.3 waited on something that was not a step.

---

## 10. Communication

```
                                                            LAYER VIEW

  client  ====>  edge          goal, ~1-10 KB
                  |
                  |  ====>  [[ runs ]]        row + goal, ~2-20 KB
                  |  ====>  [[ outbox ]]      << run.created >>, ~1 KB
                  |
  [[ outbox ]] ====>  relay ====>  (( queue ))    run_id only, ~100 B
                                        |
                                        v
                                     worker
                                        |
        claim         ====>  [[ runs ]]      one row, ~2-20 KB
        checkpoint    ====>  [[ runs ]]      ~1-5 KB, once per step
        release       ====>  [[ runs ]]      ~200 B
                                        |
  sweeper  ====>  [[ runs ]]      a SET of rows, batched, ~1 KB each
                                  volume independent of run count;
                                  proportional to FAILURE count

  Figure 8.5 -- What moves at each lifecycle boundary (D7 Data Flow)
```

Two observations the volumes make obvious.

**The queue carries identity, not payload.** A queue message is a `run_id` and nothing else
`[DAR §5.4]`. Everything about the run is read from the row at claim time, which means a message
that sat in the queue for an hour is not stale — it was never carrying state to begin with. This is
what makes re-enqueueing free, and re-enqueueing is what drain and the sweeper both do.

**The sweeper's traffic scales with failures, not with load.** It reads an indexed range over
`lease_until` and touches only expired rows. A healthy system's sweeper does almost nothing forever,
which is a property worth protecting: the moment the sweep query starts scanning, it becomes the
thing that falls over during the incident it exists to resolve.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 17 State Manager | claim, checkpoint, release as one CAS discipline | the mechanism this chapter only names |
| Ch 18 Runtime Loop | the four episode exit conditions | the loop is the `serve` state, opened |
| Ch 27 Failure and Recovery | the interruption matrix of §5.5 | becomes the failure table's spine |
| Ch 33 Scalability | active time vs wall age | capacity is sized on active time only |
| Ch 38 Deployment | drain semantics, model and harness pinning at boot | a deploy is a runtime-lifecycle event that must stay one |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Orphaned run | worker dies without draining | sweeper, on `lease_until < now` | expire, re-enqueue; one lease period |
| Recovery only at boot | recovery implemented as a startup scan | `oldest_expiry_lag_ms` correlating with deploys | move it to the sweeper — the cold open |
| Drain that finishes runs | shutdown waits for run completion | deploy duration ~ run duration | finish the step, release the lease |
| Drain without release | step 4 of §6.3 omitted | `runs_requeued` = 0 in `DrainReport` | release all leases before exit |
| Lease shorter than a step | lease under p99 step duration | two workers advancing one run; version CAS conflicts | lease ≥ 3× p99 step; alert on conflicts |
| Lease longer than tolerable | lease sized for comfort | `oldest_expiry_lag_ms` p99 near the lease period | lease is your worst-case recovery latency; choose it as such |
| Sweeper wedged | one poison row aborts the batch | `SweepReport` counts flat while lag rises | per-row error isolation; dead-letter the poison row |
| Sweeper stampede | every worker sweeps on the same tick | periodic write spikes | jitter the interval per worker |
| Park woken by polling | a timer in a worker rather than an event | parks resolving only while workers are healthy | parks resolve on events; the sweeper wakes `wake_at` |
| Zombie advance | a partitioned worker resumes after expiry | version CAS returns zero rows | fail closed and abandon; the CAS is the guard |

`[INF]` Rows five and six are one dial with a failure at each end, and the honest framing is the one
in row six: **the lease period is the recovery latency you have chosen.** Teams set it for comfort
and then discover they set an SLO. Sixty seconds is a reasonable default; whatever you pick, put it
in the runbook next to "how long can a run be stuck before anybody notices", because they are the
same number.

The zombie advance in the last row is the case that makes people reach for a consensus system. It
does not need one: the partitioned worker's `expected_version` is stale, so its checkpoint updates
zero rows and it stops. Correctness comes from the CAS, not from agreement about who is alive
`[DAR §13]`.

---

## 12. Scalability

### 12.1 What each lifecycle scales with

| Quantity | Scales with | Does not scale with |
|---|---|---|
| Rows in `runs` | total runs, including parked | worker count |
| Worker count | **active** time, not wall age | run count |
| Sweeper cost | failure rate | run count |
| Queue depth | arrival rate minus claim rate | run duration |

The second row is the one that saves money. Chapter 33 does the arithmetic; the shape is that ten
thousand runs of which nine thousand are parked need capacity for one thousand. Sizing on run count
overprovisions by an order of magnitude, and it is the default mistake because run count is the
number already on the dashboard.

### 12.2 Lease period, chosen deliberately

Three constraints, and the window between them is usually wide:

- **Floor:** comfortably above p99 step duration, or a slow step gets its own run stolen from under
  it. Three times is a reasonable margin.
- **Ceiling:** your tolerance for undetected orphans. This is the SLO from §11.
- **Sweep interval:** an order of magnitude below the lease, so expiry lag is small relative to the
  lease rather than doubling it.

`[BP]` Sixty-second lease, five-second sweep, ten-second drain budget is a defensible starting set
for a system whose steps are sub-second and whose activities run tens of seconds. Every number
should move once you have measured; none should move because a dashboard looked untidy.

### 12.3 The parked population is free, and that is a design goal

A parked run holds no worker, no connection, no timer, and no memory anywhere `[DAR §8.2]`. So the
parked population is bounded by storage, and storage is the cheapest thing in the architecture. This
is what allows a product to offer "the agent will wait for your approval as long as you need"
without that promise having an operational cost — and it is a direct consequence of the custody
gradient from Chapter 5 rather than a feature anybody built.

---

## 13. Production Engineering

### 13.1 The signals that matter

| Signal | Why | Alert |
|---|---|---|
| `oldest_expiry_lag_ms` | the cold open, measured | p99 > 2× sweep interval |
| Sweep executions per minute | detects a wedged sweeper | any gap > 3× interval |
| Runs requeued per drain | detects step 4 omitted | zero during a rolling deploy |
| Drain duration p99 | detects §6.3 line 2 waiting on an activity | > drain budget |
| Version CAS conflicts | two drivers on one run | any sustained non-zero |
| Active time / wall age per run | separates slow from parked | reported, not alerted |

The third row is worth setting up before you need it: "runs requeued per drain is zero" is a cheap,
always-on test that the release step still exists, and it survives the refactor that deletes it.

### 13.2 The one test that catches the cold open

```python
async def test_orphan_recovers_without_any_process_restart(
    clock: FakeClock, runtime: Runtime
) -> None:
    run_id = await runtime.submit(goal)
    worker_a = await runtime.spawn_worker()
    await worker_a.claim_and_advance(steps=2)

    await worker_a.kill()              # no drain, no signal handler

    clock.advance(seconds=LEASE_SECONDS + 1)
    await runtime.sweeper.sweep(clock.now())   # nothing has booted

    worker_b = await runtime.spawn_worker()
    assert await worker_b.claim() == run_id
```

`[INF]` The assertion is ordinary; the discipline is in what the test refuses to do. It never
restarts a worker before sweeping, because a boot is exactly the event the cold open's system
depended on. A test that spawns `worker_b` before calling `sweep` passes against the broken
implementation, and that test is the one most people write.

### 13.3 Runbook entry

> **A run is stuck.** Read its state and `lease_until`.
> `EXECUTING` with `lease_until` in the future — a worker is on it; wait one lease period.
> `EXECUTING` with `lease_until` in the past — the sweeper is behind. Check it is running at all.
> `PARKED` — nothing is wrong. Find the resolving condition; it is a person, a timer, or a callback,
> and only the first is ever the problem.
> `AWAITING_ACTIVITY` with an expired activity lease — the activity died; it recovers on the next
> sweep and replays by identity.

That entry exists because of the Chapter 5 cold open: four engineers, four investigations, one word.
The lifecycle vocabulary is what turns "stuck" into a lookup.

---

## 14. Relation to AHE

The evolution loop of Level 5 needs one thing from this chapter: **an iteration must be a bounded,
repeatable unit.** AHE's Algorithm 1 runs the harness over a task set, distils what went wrong,
edits components, and re-runs `[AHE §3.3]`. Every one of those verbs assumes that a rollout either
finished or is known to have failed, and that assumption is exactly what the lifecycle provides.

Three specifics:

- **A stuck run poisons an iteration silently.** If the recovery latency is unbounded — the cold
  open — a rollout that was orphaned looks like a task the harness failed, and the Evolve Agent
  attributes a harness defect to what was actually an infrastructure event. Chapter 47's attribution
  is only as honest as the lifecycle underneath it.
- **Harness version is pinned at boot, never mid-run.** A run that spans a deploy must complete on
  the harness version it started with, or its trajectory describes a configuration that never
  existed. `[INF]` This is the lifecycle consequence of Chapter 1's "the harness is fitted to a
  model": the pin belongs to the run, and it is read at boot into the worker that happens to be
  driving it.
- **Timeout coupling is a lifecycle parameter.** `[AHE Limitations]` reports that step budget and
  per-task timeout, fitted at one operating point, are part of why the measured gain was
  non-monotone across reasoning tiers. Those two numbers live in this chapter's machinery, which
  makes them harness configuration rather than infrastructure constants — a distinction Chapter 38
  turns into a versioning rule.

---

## 15. Industry Perspective

**`[DAR]`** The reference architecture supplies the run states, the lease-plus-version-CAS advance,
the claim/checkpoint/release cycle, the sweeper as a continuous job, and the rule that a park holds
no resource `[DAR §5.1–5.3, §8.2]`. It also states the design goal this chapter serves: a crash
loses at most one in-flight step `[DAR §6.1]`.

**`[AHE]`** Supplies the timeout-coupling hazard and the requirement that an iteration be a bounded
unit `[AHE §3.3, Limitations]`. It does not describe a runtime lifecycle; the harness in that work
runs inside an experiment driver rather than a long-lived service.

**`[INF]`** The handbook's additions in this chapter: the two-lifecycle framing and its two legal
meeting points, the four-quadrant test, the interruption matrix, the wall-age / active-time /
parked-time split, `oldest_expiry_lag_ms` as the direct measurement of boot-only recovery, and the
argument that the lease period *is* the recovery-latency SLO.

**`[BP]`** Draining by releasing rather than completing is standard practice in any pull-based work
system, and predates agents entirely — Sidekiq, Celery, and Temporal all express a version of it.
The starting numbers in §12.2 are conventional rather than derived.

**`[FUT]`** Nothing in this chapter is speculative. It is the most conventional chapter in Level 1,
which is the reason the cold open is a real and common defect: everything here is familiar enough
that teams assume they already have it.

---

## 16. Key Takeaways

1. **Two clocks, not one.** A run's lifecycle and a process's lifecycle are independent state
   machines. Confusing them produces the two most expensive defects in this chapter.
2. **They touch at exactly two points.** A worker claims a run; a worker or the sweeper releases
   one. Any third interaction — a boot that mutates run state, a deploy that waits on a run — is a
   defect, and §2.4 is the test.
3. **Recovery is continuous, never a boot activity.** The failure happens at 2am when nothing is
   starting. A boot-time scan is a recovery mechanism whose trigger is uncorrelated with the fault.
4. **Draining means letting go, not finishing.** Finish the current step, checkpoint, release every
   lease, exit. Ten seconds, not six hours — and the release step is the one everybody omits.
5. **The lease period is the recovery-latency SLO you have chosen.** Set it deliberately, floor it
   above p99 step duration, and write it in the runbook next to "how long can work sit unnoticed".
6. **Correctness comes from the CAS, not from knowing who is alive.** A partitioned worker's
   checkpoint updates zero rows and it stops. No consensus system is required.
7. **Size capacity on active time, not wall age.** Most runs are parked most of the time, and parked
   runs are free by construction. Sizing on run count overprovisions by an order of magnitude.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Run lifecycle** | The life of one goal, from arrival to a terminal state, independent of every process that touches it. | `[DAR]` | Ch 9, Ch 18 |
| **Runtime lifecycle** | The life of one process — boot, serve, drain, exit — which has no obligation to any run. | `[INF]` | Ch 38 |
| **Claim** | A compare-and-swap that puts a time-limited lease on a run, so exactly one worker advances it. | `[DAR]` | Ch 17 |
| **Release** | Giving a lease back at an episode boundary or at drain, without finishing the work. | `[DAR]` | Ch 18 |
| **Drain** | Shutdown that stops claiming, finishes the current step, checkpoints, and releases every lease. | `[BP]` | Ch 38 |
| **Sweeper** | The continuously scheduled job that expires leases on elapsed time alone; the only component belonging to neither lifecycle. | `[DAR]` | Ch 27 |
| **Lease period** | How long a claim lasts, and therefore how long an orphaned run can go unnoticed. | `[DAR]` | Ch 23, Ch 33 |
| **Wall age** | Time since a run was created, including every hour it spent parked. | `[INF]` | Ch 34 |
| **Active time** | The summed duration of a run's episodes; the only figure capacity planning may use. | `[INF]` | Ch 33 |
| **Parked time** | Wall age minus active time; measures human and external latency, never runtime performance. | `[INF]` | Ch 30 |
| **Interruption matrix** | The table of what is lost when a process dies at each point, and how long recovery takes. | `[INF]` | Ch 27 |
| **Zombie advance** | A partitioned worker attempting to continue after its lease expired, stopped by a stale version rather than by consensus. | `[DAR]` | Ch 32 |
| **Expiry lag** | How overdue the most overdue lease was when the sweeper reached it; the direct measurement of recovery health. | `[INF]` | Ch 34 |

---

**Next:** Chapter 9 — *Three Flows: Data, Control, Event.* The same runtime read three ways — who
decides what happens next, what moves and how much of it, and what is durable enough to replay —
and why reading a codebase along the wrong flow is what makes it feel unmaintainable.
