```
  Level 2 · Chapter 17
  THE STATE MANAGER
  Requires   C5 The Five Nouns, C6 State Separation, C8 Lifecycles,
             C9 Three Flows
  Unlocks    C18 The Runtime Loop, C21 Durable Execution,
             C23 The Scheduler, C27 Failure and Recovery,
             C32 Distributed Execution
  Diagrams   Full (9)
```

# Chapter 17 — The State Manager

---

## 1. Motivation

### 1.1 Cold open

03:40. Six runs have not progressed in over an hour. The on-call engineer needs one thing before she
can do anything: which of them currently have an owner, and which are orphaned?

There is no query that answers it.

Ownership is expressed as a row lock — `SELECT * FROM runs WHERE id = $1 FOR UPDATE` — which is
correct, standard, and was the obvious primitive. But a lock is not a value. It appears in no column,
it cannot be indexed, and it disappears with the connection that held it, leaving nothing behind to
say it ever existed. `pg_locks` reports which sessions hold what right now; it is silent about a
session that died at 02:15.

The runbook's answer is to restart the workers and see which runs come back.

It works. It also cancels every in-flight model call across the fleet, and it is the only diagnostic
the system has.

### 1.2 In plain language

The state manager is the part of the runtime that writes down where a run has got to, so that if the
machine driving it dies, another machine can pick it up from the last finished step rather than
starting over.

It has to solve three problems at once, and they pull in different directions.

**Exactly one machine may advance a run at a time.** Two workers driving one run would duplicate
work and corrupt its position. But the obvious way to enforce that — take a lock — fails the other
two requirements.

**Ownership must survive the machine that holds it.** A run lasts days; a process lasts hours. So
ownership cannot be a thing a process holds; it has to be a thing written down, with an expiry, that
outlives whoever wrote it.

**You have to be able to ask about it.** The cold open is a system where ownership is real and
invisible. If you cannot query which runs are owned and until when, you cannot find orphans, you
cannot measure recovery, and your only tool is turning things off and on.

The answer to all three is the same: **make ownership a value in a row, not a lock on a row.** Two
columns — who owns it, and until when — and every question above becomes a query. That one change is
most of this chapter.

### 1.3 Why this chapter exists

Chapter 8 named the mechanism and deferred it: claim, checkpoint, release, and a sweeper that acts on
elapsed time. This chapter builds it, and it is the last component Chapter 18 needs before the
runtime loop can be assembled.

`[INF]` It is also where the book's cheapest large win lives. Almost every property Level 3 depends
on — durable execution, fair scheduling, recovery, distribution across many workers — reduces to
lease semantics plus a version compare-and-swap. Getting those two right here means five later
chapters are describing consequences rather than introducing mechanisms.

### 1.4 What previous framings got wrong

**"Use a lock; that is what locks are for."** The cold open. Locks express mutual exclusion between
*concurrent sessions*. What is needed here is ownership that survives a session ending, is visible
to anybody who asks, and expires on its own. A lock does none of the three.

**"Checkpoint at the end."** A checkpoint is not a save; it is the point at which work becomes
recoverable. Checkpointing once per episode means a crash loses everything since the episode began,
which Chapter 2's design goal — lose at most one in-flight step — forbids.

**"Optimistic concurrency is for high contention."** `[BP]` Here it is for *correctness under
partition*. §5.3 shows a version CAS stopping a partitioned worker that a lock could not, because the
partitioned worker still believes it holds the lock.

**"Recovery is a background process that scans for stale work."** A scan is what you write when
staleness is not a column. With `lease_until` indexed, recovery is one query with a `WHERE` clause,
and §12 shows it stays one query at any scale.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A library's lending record, versus standing in the aisle holding a book.

Holding the book is a lock. While you have it, nobody else can, and that much works. But nobody can
find out who has it, when they will be done, or whether they left the building with it. If you walk
out and vanish, the book is gone — there is no record that anybody ever took it, so nothing
can notice it is missing.

A lending record is a lease. It is a row: this book, this borrower, due back on this date. It does
not physically prevent anything, and it does not need to, because everything that matters is now a
question you can ask. Who has it? Query. What is overdue? Query, on an index. Who had it in March?
Query. And when a borrower disappears, the due date passes on its own and the book becomes
reclaimable without anybody having to notice.

That is the whole substitution this chapter makes, and the cold open is a library that decided
lending records were unnecessary because possession was self-evident.

**Where the analogy breaks.** A library relies on the borrower returning the book, and on nobody
else being able to read it meanwhile. Here, an expired lease does not stop the old owner — a
partitioned worker whose lease expired ten seconds ago still believes it holds the run, is still
executing, and may still try to write.

So a due date alone is not enough. Something must make the late borrower's write *fail* rather than
merely be discouraged. That is the version compare-and-swap in §5.3, and it is the part of the design
that has no counterpart in the analogy: the record does not only say who has the book, it makes the
wrong person physically unable to write in it.

### 2.2 Why ownership must be a value, not a lock

```
  1. Exactly one worker may advance a run at a time.
  2. A run lasts days; a worker lasts hours. So ownership must
     outlive the worker that has it.
  3. A lock is held by a session. When the session ends, the lock is
     gone -- and so is every trace that it existed.
  4. So with a lock you cannot answer "who owns this run?" after the
     owner has died, which is exactly when you need to ask.
  5. Nor can you answer it in aggregate: locks are not columns, so
     "which runs are orphaned?" has no index and no query.
  6. Therefore ownership must be DATA: a column saying who, and a
     column saying until when.
  7. But data does not exclude anything by itself. A worker whose
     lease expired can still attempt a write.
  8. So the write must carry proof that the writer's view is current.
     A version, checked and incremented in the same statement, makes
     a stale writer's update affect zero rows.
  9. Lease answers "who should be driving"; version CAS answers "did
     this writer still have the right to". Both are required, and
     neither substitutes for the other.
```

Step 9 is the sentence to keep. `[INF]` Teams routinely implement one and assume it covers the
other. A lease without a CAS permits a zombie writer; a CAS without a lease gives you correctness
with no way to schedule, because nothing says who *should* pick a run up.

### 2.3 The two columns and the two guarantees

| Column | Answers | Guarantees |
|---|---|---|
| `lease_owner`, `lease_until` | who should be driving, until when | liveness: an abandoned run becomes claimable |
| `version` | was this writer's view current | safety: a stale writer cannot advance the run |

`[DAR §5.3]` Both live on the `runs` row. Neither is a separate table, a separate service, or a
coordination system.

`[INF]` That last point is worth stating because the instinct at this stage is to reach for one.
Nothing in this chapter needs consensus, a distributed lock manager, or leader election. The
guarantees come from a single-row conditional update, which every relational database provides, and
Chapter 32 shows the same two columns carrying the design to many workers without addition.

### 2.4 The mental model to carry

> **A worker never owns a run. It borrows it, with a receipt that expires, and every write it makes
> must prove the receipt was still valid.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  KERNEL                                                      |
  |                                                              |
  |   +------------------+       +------------------+            |
  |   | run driver       |       | sweeper (Ch 8)   |            |
  |   +--------+---------+       +---------+--------+            |
  |            | (1) claim                 | (4) expire          |
  |            | (2) checkpoint            |                     |
  |            | (3) release               |                     |
  |            v                           v                     |
  |   +========+===========================+========+            |
  |   |  STATE MANAGER                              |            |
  |   |                                             |            |
  |   |    claim . checkpoint . release . sweep     |            |
  |   |    every write is a conditional UPDATE      |            |
  |   +====+==========+===========+==========+======+            |
  |        | (5)      | (6)       | (7)      | (8)               |
  +--------|----------|-----------|----------|-------------------+
           v          v           v          v
     [[ runs ]]  [[ run_    ]] [[ signals ]] (( queue ))
      the only    [[ steps  ]]  read in the   re-enqueue
      row with                  SAME txn      on release
      a lease                   as the
                                checkpoint

  Figure 17.1 -- The state manager in its surroundings
                 (D1 High-Level Architecture)

  (1) claim: conditional UPDATE; zero rows means somebody else won
  (2) checkpoint: advance, renew lease, read signals, one txn
  (3) release: clear the lease, re-enqueue if not terminal
  (4) sweep: expire leases on elapsed time alone (Ch 8)
  (5) the runs row is the only place ownership exists
  (6) step rows are append-only; a replan writes new ones (Ch 10)
  (7) signals are read inside the checkpoint transaction, which is
      what makes cancellation cost nothing (section 5.4)
  (8) re-enqueue carries an id, never state (Ch 8 section 10)
```

`[INF]` The diagram's shape carries the argument: four operations, one table with the lease, and no
coordination component anywhere. If your equivalent diagram has a lock service, a leader, or a
heartbeat topic in it, §2.3 says those are solving a problem this design does not have.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  THE FOUR OPERATIONS, as SQL. All four are conditional updates.

  CLAIM -- take ownership of an eligible run
  +--------------------------------------------------------------+
  | UPDATE runs                                                   |
  |    SET lease_owner = :worker, lease_until = now() + :lease,   |
  |        version = version + 1                                  |
  |  WHERE id = :run_id                                           |
  |    AND (lease_until IS NULL OR lease_until < now())           |
  |    AND state NOT IN ('SUCCEEDED','FAILED','CANCELLED',        |
  |                      'DEAD_LETTERED')                          |
  | RETURNING *;                                                  |
  |                                                              |
  | zero rows = another worker won. NOT an error (Ch 8 section 5.2)|
  +--------------------------------------------------------------+

  CHECKPOINT -- advance one step; the hot path, ~5 ms
  +--------------------------------------------------------------+
  | BEGIN;                                                        |
  |   UPDATE runs                                                 |
  |      SET state = :state, current_step = :step,                |
  |          plan_id = :plan, budget_used = :used,                |
  |          lease_until = now() + :lease,                        |
  |          version = version + 1                                |
  |    WHERE id = :run_id                                         |
  |      AND version = :expected      <-- THE SAFETY GUARD        |
  |      AND lease_owner = :worker;                               |
  |   -- zero rows here: STOP. Another worker owns this run.      |
  |                                                              |
  |   INSERT INTO run_steps (...) VALUES (...);                   |
  |                                                              |
  |   SELECT * FROM signals                                       |
  |    WHERE run_id = :run_id AND consumed_at IS NULL             |
  |      FOR UPDATE SKIP LOCKED;   <-- free: same txn (5.4)       |
  | COMMIT;                                                       |
  +--------------------------------------------------------------+

  RELEASE -- give the lease back without finishing (Ch 8)
  +--------------------------------------------------------------+
  | UPDATE runs                                                   |
  |    SET lease_owner = NULL, lease_until = NULL,                |
  |        version = version + 1                                  |
  |  WHERE id = :run_id AND version = :expected                   |
  |    AND lease_owner = :worker;                                 |
  +--------------------------------------------------------------+

  SWEEP -- recovery, as ONE INDEXED QUERY
  +--------------------------------------------------------------+
  | UPDATE runs                                                   |
  |    SET lease_owner = NULL, lease_until = NULL,                |
  |        version = version + 1                                  |
  |  WHERE lease_until < now()          <-- indexed               |
  |    AND state NOT IN (terminal states)                         |
  | RETURNING id;          -- re-enqueue these                    |
  +--------------------------------------------------------------+

  Figure 17.2 -- The four operations (D2 Low-Level Architecture)
```

### 4.1 What the SQL is doing that prose cannot say

`[INF]` Three details are load-bearing and easy to lose in a paraphrase.

**`AND version = :expected` appears in checkpoint and release, not in claim.** Claim has no prior
version to check — it is establishing ownership rather than continuing it. The predicate that makes
claim safe is `lease_until < now()`, and the two predicates are doing different jobs.

**`AND lease_owner = :worker` is belt and braces.** The version check alone is sufficient for safety.
The owner check converts a confusing outcome (zero rows, unclear why) into a diagnosable one, and
costs nothing.

**The signal read is inside the checkpoint transaction.** It is a query the transaction was already
open for, on a row set the worker already had reason to touch. `[DAR §5.3]` Reading pending signals
"comes free" at a checkpoint, and §5.4 explains why that single fact determines the system's
cancellation latency.

```
                                                            LAYER VIEW

  Components and their interfaces.

   ClaimRequest                                     ClaimedRun (frozen)
        |                                                    ^
        v                                                    |
   +----+------------+                            +----------+------+
   | Claimer         |  conditional UPDATE        | Run store       |
   |  claim()        |--------------------------->|  [[ runs ]]     |
   +-----------------+                            |                 |
                                                  |  ONE row per    |
   +-----------------+                            |  run; the only  |
   | Checkpointer    |  UPDATE ... WHERE version  |  place a lease  |
   |  advance()      |--------------------------->|  exists         |
   |  renew lease    |                            +----------+------+
   |  read signals   |                                       ^
   +--------+--------+                                       |
            |                                                |
            v                                                |
   +--------+--------+     +----------------+     +----------+------+
   | Step writer     |     | Signal reader  |     | Sweeper         |
   |  append-only    |     |  same txn      |     |  one indexed    |
   +--------+--------+     +--------+-------+     |  query          |
            |                       |             +----------+------+
            v                       v                        ^
     [[ run_steps ]]         [[ signals ]]                   |
                                                   +---------+------+
                                                   | Clock          |
                                                   |  DB now(), not |
                                                   |  worker time   |
                                                   +----------------+

  Figure 17.3 -- State manager components (D3 Component Diagram)
```

`[INF]` The Clock is drawn as a component to make one rule visible: **every timestamp comparison uses
the database's clock, never a worker's.** A fleet with skewed clocks and worker-side expiry
comparisons will have workers that believe leases are live when they are not. Using `now()` inside
the statement means there is exactly one clock in the system, and Chapter 32 depends on that when
the fleet spans regions.

---

## 5. Leases, Versions, and Checkpoints

### 5.1 The checkpoint is the unit of recoverability

`[DAR §5.1]` A checkpoint does four things in one transaction: persists progress, renews the lease,
reads pending signals, and increments the version. It runs after **every** step.

`[INF]` The cost objection is worth answering with a number. A checkpoint is a single-row update plus
one insert on an indexed table — roughly five milliseconds. A step that dispatched an activity took
seconds to minutes. Checkpointing every step therefore costs well under one percent of step time,
and buys the guarantee that a crash loses at most one in-flight step.

The alternative — checkpoint at episode end — saves nothing measurable and loses everything since the
episode began.

### 5.2 The lease is a promise about time, not a lock

Three properties, and each one is something a lock cannot do:

| Property | Consequence |
|---|---|
| It is a value | queryable, indexable, aggregatable. The cold open's missing capability |
| It expires on its own | recovery needs no notification, no heartbeat, no failure detector |
| It survives its holder | ownership is knowable after the owner is gone |

`[INF]` The second property is the one that removes an entire subsystem. A lock-based design needs
something to notice that a holder died — a heartbeat, a health check, a session watchdog. A lease needs
nothing to notice anything: the clock does the work, and the sweeper is a query rather than a
detector.

### 5.3 The version CAS is what makes a zombie harmless

The case a lease alone does not cover, and it is not exotic:

```
  t=0    worker A claims run, lease 60s, version 7
  t=15   A dispatches an activity; network partition begins
  t=60   lease expires. A does not know: it cannot reach anything
  t=65   sweeper clears the lease. Run re-enqueued
  t=70   worker B claims it. version 8
  t=95   B checkpoints. version 9
  t=120  partition heals. A returns, still believing it owns the run,
         and attempts to checkpoint with expected_version = 7

         UPDATE runs SET ... WHERE id=:id AND version = 7
         -> ZERO ROWS. A stops.
```

`[DAR §13]` A updates zero rows, learns from that alone that it no longer owns the run, and abandons
without needing to be told by anybody.

`[INF]` This is the design's most important property and it is worth naming what is absent: there is
no consensus protocol, no fencing token service, no failure detector, and no agreement about who is
alive. Correctness comes from a stale writer's write failing, not from anybody knowing that A had
died. Chapter 32 scales this to many workers and adds nothing to it.

### 5.4 Signals ride along, and that sets cancellation latency

`[INF]` Because the checkpoint transaction is already open, reading pending signals costs one extra
query on an indexed column — effectively free, as §4.1 noted. The consequence is larger than it
sounds:

> **Cancellation latency equals one step, not one episode.**

Chapter 18's cold open is a system that reads signals at episode end instead. The difference between
those two designs is where a `SELECT` is placed, and it is the difference between cancelling in
seconds and cancelling in fifteen minutes.

### 5.5 Choosing the lease period

Chapter 8 §12.2 established the constraints; here is the mechanism's side of them.

| Constraint | Rule |
|---|---|
| Floor | ≥ 3× p99 step duration, or a slow step loses its own run |
| Ceiling | your tolerance for an undetected orphan — this *is* the SLO |
| Renewal | at every checkpoint, so a healthy run never approaches expiry |
| Sweep interval | an order of magnitude below the lease |

`[INF]` The renewal rule is what makes the floor a soft constraint in practice. A run that
checkpoints every few seconds is continuously extending its lease, so the lease period only has to
cover the *longest single gap between checkpoints* — which is one step, not one episode. That is why
the same sixty-second default works for runs lasting a week.

### 5.6 When the checkpoint must write more than the run

A checkpoint sometimes has to advance the run *and* record something outside it — an activity result,
a domain change, an event. Chapter 9 §5.2's same-transaction rule and this chapter's CAS have to
coexist, and the ordering that works is narrow:

```sql
BEGIN;
  UPDATE runs SET ... WHERE id = :id AND version = :expected;   -- FIRST
  -- zero rows -> ROLLBACK immediately. Write nothing else.
  INSERT INTO run_steps ...;
  INSERT INTO outbox   ...;                                     -- the event
COMMIT;
```

`[INF]` The CAS goes first so that a superseded worker discovers it before writing anything else. A
transaction that appends an event and *then* checks the version has already produced a fact on
behalf of a worker that turned out not to own the run — and because the outbox is the durable
boundary (Chapter 22), that fact will be delivered even though the write it described was rolled
back alongside it.

The rule generalises to one sentence: **prove you still own the run before you write anything that
outlives the transaction.**

### 5.7 Why not an advisory lock, specifically

`[BP]` Postgres advisory locks are the tool most often reached for here, so the rejection deserves to
be explicit:

| | Advisory lock | Lease column |
|---|---|---|
| Queryable | only `pg_locks`, and only live holders | any SQL |
| Survives holder | no | yes |
| Expires | no — held until released or session ends | yes |
| Indexable for recovery | no | yes |
| Works across databases | no | yes |
| Holds a connection | session-scoped ones do | no |

The last row is the one that connects to Chapter 2's cold open: a session-scoped advisory lock held
across a model call holds a pooled connection for the duration, which is the custody violation
Chapter 5 named. `[INF]` A lease column holds nothing at all — it is a timestamp — which is why
worker concurrency can exceed pool size by orders of magnitude.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  worker A     worker B     state mgr    sweeper    runs row
     |            |             |           |          |
     |-- claim -->|             |           |  v7 -> v8, lease=A
     |<-- ClaimedRun(v8) -------|           |          |
     |            |             |           |          |
     |  step 1: decide          |           |          |
     |-- checkpoint(expected=8) |           |  v8 -> v9, lease renewed
     |<-- ok, v9 ---------------|           |  signals: none
     |            |             |           |          |
     |  step 2: dispatch activity           |          |
     |-- checkpoint(expected=9) |           |  v9 -> v10
     |<-- ok, v10 --------------|           |  signals: none
     |            |             |           |          |
     |  === PARTITION. A is isolated. ===   |          |
     |            |             |           |          |
     |            |             |  (lease_until passes)|
     |            |             |<-- sweep -|  v10 -> v11, lease=NULL
     |            |             |           |  re-enqueued
     |            |             |           |          |
     |            |-- claim --->|           |  v11 -> v12, lease=B
     |            |<-- ClaimedRun(v12) -----|          |
     |            |  resumes at step 3      |          |
     |            |-- checkpoint(expected=12) -------->|  v12 -> v13
     |            |             |           |          |
     |  === PARTITION HEALS. A returns. === |          |
     |            |             |           |          |
     |-- checkpoint(expected=10) ---------------------->|
     |<-- ZERO ROWS ------------|           |          |
     |  A stops. It was not told; it INFERRED it from   |
     |  a write that affected nothing.                  |

  Figure 17.4 -- A partition, resolved without consensus (D4 Sequence)
```

### 6.1 What is absent from that sequence

`[INF]` No heartbeat. No failure detector. No quorum. No fencing token issued by a third party. No
message telling A it had been superseded — A could not have received one, since it was partitioned.

The only mechanism is that A's `WHERE version = 10` matched nothing. That is the entire distributed
correctness argument of this architecture, and it fits in a `WHERE` clause.

```
                                                             TIME VIEW

  The state manager's cycle, per episode.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | claim               |  conditional UPDATE            |
   +----+-----------------+                               |
        |                                                 |
        +-- zero rows --> E1 someone else won; move on    |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | drive one step       |  no lease held? NO -- the     |
   | (Ch 18)              |  lease is a ROW, not a hold   |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | checkpoint:          |                               |
   |  advance + renew +   |                               |
   |  read signals        |                               |
   +----+-----------------+                               |
        |                                                 |
        +-- zero rows --> E2 superseded; STOP immediately |
        |                                                 |
        v                                                 |
      /   \                                               |
     /signal?\  cancel/steer -> E3 handle now, not later  |
     \       /                                            |
      \     /                                             |
        | none                                            |
        v                                                 |
      /   \                                               |
     / exit  \  no --------------------------------------->+
     \ cond? /                                             |
      \     /                                              |
        | yes                                              |
        v                                                  |
   +----+-----------------+                                |
   | release + re-enqueue |                                |
   +----+-----------------+                                |
        |                                                  |
        v                                                  |
      E4 episode ends; the run continues elsewhere

  Exits:
    E1  lost the claim race -- a normal outcome, never an error
    E2  version CAS failed -- this worker is a zombie; stop
    E3  a signal was pending -- acted on within ONE STEP (5.4)
    E4  clean release at an exit condition (Ch 18)

  Figure 17.5 -- The claim-drive-checkpoint cycle (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

  A run row's OWNERSHIP, independent of its run state (Ch 8).

            +---------------------+
            | {{ UNOWNED }}       |  lease_owner NULL; claimable
            +----------+----------+
                       | claim succeeds (version + 1)
                       v
            +---------------------+
            | {{ LEASED }}        |  lease_owner set, lease_until
            +--+-------+-------+--+  in the future
               |       |       |
    checkpoint |       |       | lease_until passes
    (renews)   |       |       v
               |       |   +---+-----------------+
               +-------+   | {{ EXPIRED }}       |  still "owned" on
                       |   +---+-----------------+  paper; the holder
       release         |       | swept              may not know
                       |       v
                       v   +---+-----------------+
            +---------------------+              |
            | {{ UNOWNED }}       |<-------------+
            +---------------------+

  The version is orthogonal and MONOTONIC: it increases on every
  transition above and never resets. That is what makes a stale
  writer detectable regardless of which transition it missed.

  Illegal, and enforced by the SQL itself:
    * two rows LEASED for one run     -- one row, one lease
    * a write from a stale version    -- zero rows affected
    * a lease renewed by a non-owner  -- lease_owner predicate
    * version decreasing              -- only ever +1

  Figure 17.6 -- Ownership states (D6 State Diagram)
```

### 7.1 Run state and ownership state are independent

`[INF]` A run can be `EXECUTING` and unowned — that is precisely an orphan awaiting sweep. It can be
`PARKED` and unowned, which is normal and permanent until an event arrives. What it cannot be is
owned by two workers, and that is the only combination the design forbids.

Keeping the two machines separate is what lets Chapter 8's four-quadrant test work: a process event
may change ownership state and may not change run state, except at claim and release.

### 7.2 What the runs row holds, and what it does not

| On the row | Not on the row |
|---|---|
| `lease_owner`, `lease_until`, `version` | the plan (its own table, Ch 10) |
| `state`, `current_step`, `plan_id` | step history (append-only, `run_steps`) |
| `budget_cap`, `budget_used` | activity results (the ledger, Ch 21) |
| `tenant_id`, `created_at` | the trajectory (trace store, Ch 16) |

`[INF]` The discipline is that the runs row must stay small and hot. It is updated on every
checkpoint of every run in the system, so a wide row with large columns turns the highest-frequency
write in the architecture into a page-splitting one. Anything that grows belongs in a table that is
appended to rather than updated.

---

## 8. Internal APIs

```python
from typing import Protocol
from datetime import timedelta


class StatePort(Protocol):
    """Ownership and progress. Every write is a conditional UPDATE, and
    zero rows affected is information rather than an error."""

    async def claim(
        self, worker_id: str, lease: timedelta, work_class: str | None = None
    ) -> ClaimedRun | None:
        """Claim one eligible run. None means no work, or another
        worker won -- both normal."""

    async def checkpoint(
        self,
        run_id: RunId,
        expected_version: int,
        progress: Progress,
        renew_for: timedelta,
    ) -> CheckpointResult:
        """Advance, renew, and read pending signals in ONE transaction.

        Raises Superseded when zero rows were affected: this worker no
        longer owns the run and must stop immediately. That is the only
        way a partitioned worker ever learns it was replaced.
        """

    async def release(
        self, run_id: RunId, expected_version: int, requeue: bool
    ) -> None: ...

    async def sweep(self, now: datetime, limit: int = 500) -> list[RunId]:
        """Expire leases past due. One indexed query; batched so a large
        backlog cannot produce one enormous transaction."""
```

`[INF]` `checkpoint` returning pending signals rather than offering a separate `read_signals` method
is the API-level expression of §5.4. A separate method would be called at whatever cadence somebody
chose, and the first performance review would move it out of the hot path — reintroducing Chapter
18's cold open. Folding it into the return value makes the cheap thing the only thing.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ClaimedRun:
    run_id: RunId
    tenant_id: str
    version: int              # carry this into every subsequent write
    state: RunState
    plan_id: PlanId | None
    current_step: int
    lease_until: datetime
    budget_cap_cents: int
    budget_used_cents: int


@dataclass(frozen=True)
class CheckpointResult:
    version: int              # the NEW version; use it next time
    lease_until: datetime
    pending_signals: tuple[Signal, ...]   # section 5.4: free, here


@dataclass(frozen=True)
class SweepReport:
    expired: int
    requeued: int
    oldest_expiry_lag_ms: int   # Ch 8: the recovery-health headline
```

`[INF]` `version` on `ClaimedRun` and again on `CheckpointResult` is the whole protocol expressed in
two fields: you are handed a version, you must present it to write, and you are handed a new one.
A caller that stores the version anywhere other than the value it was last handed has already
introduced the bug this design prevents.

---

## 10. Communication

```
                                                            LAYER VIEW

  claim        worker ====> [[ runs ]]       one row, ~2-20 KB
  checkpoint   worker ====> [[ runs ]]       ~1-5 KB, ONCE PER STEP
               worker ====> [[ run_steps ]]  ~1-3 KB, append
               worker <==== [[ signals ]]    ~0-1 KB, same txn
  release      worker ====> [[ runs ]]       ~200 B
  sweep        sweeper ==> [[ runs ]]        a SET, batched

  Volume note: checkpoint is the highest-frequency write in the whole
  architecture -- once per step, per run, forever. Everything about
  the runs row (section 7.2) follows from that one fact.

  Figure 17.7 -- What moves (D7 Data Flow)
```

```
                                                             TIME VIEW

  run driver ----> state manager   claim, checkpoint, release
  sweeper --------> state manager   expire, on elapsed time alone
  state manager --> the DB          conditional UPDATEs only
  state manager --X the run's logic REFUSED: it stores, never decides
  worker --X       another worker   no messages; no agreement needed
  a stale worker --X the runs row   zero rows: the CAS refuses it

  Figure 17.8 -- Who may advance a run (D8 Control Flow)
```

```
                                                             TIME VIEW

  << run.step.completed >>  ....> written in the checkpoint txn, so
                                  progress and its announcement are
                                  atomic (Ch 9 section 5.2)
  << run.lease.expired >>   ....> the sweeper reclaimed a run; the
                                  input to Ch 8's recovery metrics

  NOT events:
    claim and release       ownership churn; telemetry
    version increments      derivable from the row
    lease renewals          the common case, and uninteresting

  Figure 17.9 -- What state management makes durable (D9 Event Flow)
```

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 18 Runtime Loop | checkpoint returns signals | cancellation latency is one step |
| Ch 21 Durable Execution | version as the replay guard | a replayed run continues the sequence |
| Ch 23 Scheduler | claim with a work class | fairness is a predicate on claim |
| Ch 27 Failure | sweep as the single recovery path | one mechanism, one number to tune |
| Ch 32 Distributed | lease + CAS, unchanged at scale | many workers add nothing to this |
| Ch 33 Scalability | checkpoint is the hottest write | sizing starts here |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Ownership as a lock | `FOR UPDATE` or advisory lock | no query answers "who owns this?" | ownership is a value — the cold open |
| Lease without CAS | expiry implemented, version not | two workers advancing one run | add `WHERE version = :expected` |
| CAS without lease | version implemented, expiry not | orphans never reclaimed | add `lease_until` and a sweeper |
| Worker-side clock | expiry compared in application code | skewed fleet, phantom expiries | compare with the DB's `now()` |
| Checkpoint at episode end | "checkpointing every step is wasteful" | crash loses many steps | every step; ~5 ms (§5.1) |
| Signals read outside the txn | a separate polling loop | cancellation latency ~ episode length | fold into checkpoint (§5.4) |
| Lease shorter than a step | floor ignored | CAS conflicts; runs stolen mid-step | ≥ 3× p99 step |
| Wide runs row | large columns on the hot row | write amplification at scale | move growing data out (§7.2) |
| Unbatched sweep | one enormous UPDATE on a backlog | a long transaction blocking writers | `limit`, and repeat |
| Zero rows treated as an error | claim race logged as a failure | error rate tracking worker count | it is a normal outcome |

`[INF]` Rows two and three are the pair from §2.2 step 9, and they are the most common serious defect
in this chapter because each looks complete on its own. A lease-only system passes every test until a
partition; a CAS-only system is correct and never recovers anything.

---

## 12. Scalability

### 12.1 Recovery stays one query

```sql
CREATE INDEX IF NOT EXISTS idx_runs_lease_expiry
    ON runs (lease_until)
 WHERE state NOT IN ('SUCCEEDED','FAILED','CANCELLED','DEAD_LETTERED');
```

`[INF]` A partial index on the expiry column, restricted to non-terminal runs. The sweeper's query
touches only rows that are actually overdue, so its cost is proportional to the number of *failures*
rather than to the number of runs — Chapter 8 §10's observation, here as an index definition.

At ten million runs of which forty are orphaned, the sweep reads forty rows.

### 12.2 The checkpoint is the hottest write in the system

| Quantity | Scales with | Watch |
|---|---|---|
| Checkpoint rate | steps/sec across all runs | the single highest write rate |
| Runs row width | fields added over time | keep it narrow (§7.2) |
| Claim contention | workers polling for work | claim by queue message, not by scan |
| Sweep cost | orphan count | flat under health |

`[INF]` The third row is a trap worth naming. A worker that finds work by scanning `runs` for
claimable rows creates contention proportional to worker count. The queue (Chapter 8 §10) exists so
that a worker is *told* which run to claim and the claim is a primary-key update — which is why the
queue message carries an id and nothing else.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Version CAS conflicts | two drivers on one run | any sustained non-zero |
| `oldest_expiry_lag_ms` | recovery health (Ch 8) | p99 > 2× sweep interval |
| Checkpoint latency p99 | the hot path | above a few tens of ms |
| Claims returning zero rows | contention, or too many pollers | high ratio to successful claims |
| Runs leased with expiry in the past | sweeper not keeping up | any sustained count |
| Lease renewals per step | should be exactly one | anything else means a bug |

### 13.2 The test that catches the cold open

```python
async def test_ownership_is_queryable_after_the_owner_dies(
    state: StatePort, clock: FakeClock, db: Database
) -> None:
    run = await submit()
    claimed = await state.claim("worker-a", lease=timedelta(seconds=60))
    assert claimed is not None

    await kill_worker("worker-a")          # no drain, no signal

    # The property the cold open lacked: ownership survives its holder
    # as DATA, so this question has an answer at all.
    row = await db.fetch_one("SELECT lease_owner, lease_until FROM runs "
                             "WHERE id = $1", claimed.run_id)
    assert row["lease_owner"] == "worker-a"

    clock.advance(seconds=61)
    orphans = await db.fetch_all(
        "SELECT id FROM runs WHERE lease_until < now() "
        "AND state NOT IN ('SUCCEEDED','FAILED','CANCELLED','DEAD_LETTERED')")
    assert claimed.run_id in [r["id"] for r in orphans]


async def test_stale_worker_cannot_advance(state: StatePort) -> None:
    claimed = await state.claim("worker-a", lease=timedelta(seconds=60))
    stale_version = claimed.version

    await state.sweep(now_plus(61))
    b = await state.claim("worker-b", lease=timedelta(seconds=60))
    await state.checkpoint(b.run_id, b.version, progress, renew_for=LEASE)

    with pytest.raises(Superseded):
        await state.checkpoint(claimed.run_id, stale_version, progress,
                               renew_for=LEASE)
```

`[INF]` The first test asserts against raw SQL deliberately. It is testing that ownership is
*visible in the database*, which is a property of the schema rather than of the port — and a port-level
assertion would pass against a lock-based implementation that answered from process memory.

---

## 14. Relation to AHE

The state manager is runtime, not harness: it is not editable by the Evolve Agent, and it should not
be. But it constrains the loop in three ways worth naming.

**An iteration is bounded because runs terminate.** `[INF]` Chapter 8 §14 argued that an unbounded
recovery latency poisons an iteration silently. The mechanism that bounds it is here — the lease, the
sweeper, and the indexed expiry query — so the evolution loop's ability to say "this rollout failed"
rather than "this rollout is still running" rests on this chapter.

**The version is the ordering that makes a trajectory reconstructible.** Chapter 16's spans carry
identity; the version sequence is what orders them unambiguously across worker handovers. `[INF]` A
trajectory whose spans came from three workers is only readable in order because every write went
through a monotonic counter.

**Harness version is pinned at claim.** Chapter 8 §14's rule is implemented here: the claim reads the
pinned version onto `ClaimedRun`, so a run that spans a deploy completes under the harness it
started with. Without it, Chapter 47's attribution compares runs that were partly one configuration
and partly another.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the lease plus version-CAS advance, the checkpoint as a single transaction that
persists progress and reads signals, the rule that a crash loses at most one in-flight step, the
sweeper, and the invariant that exactly one driver advances a run at any instant
`[DAR §5.1–5.3, §6.1, §13]`.

**`[AHE]`** Nothing directly. This is runtime rather than harness, and the paper's contribution here
is indirect: bounded, terminating runs are a precondition for the iteration structure it describes.

**`[INF]`** The handbook's own: the argument that ownership must be a value because a lock is not
queryable, the lending-record analogy and its precise breaking point, the explicit pairing that a
lease provides liveness and a CAS provides safety with neither substituting for the other, the
observation that lease renewal at every checkpoint reduces the floor constraint to one step rather
than one episode, the advisory-lock comparison table, and the discipline that the runs row must stay
narrow because it is the hottest write in the system.

**`[BP]`** Optimistic concurrency with a version column, lease-based ownership with expiry, and
partial indexes for recovery queries are all long-established. The contribution is the insistence
that both mechanisms are present, and the framing of why each alone is insufficient.

**`[FUT]`** Nothing in this chapter is speculative. It is the most conventional chapter in Level 2,
and deliberately so: everything in Level 3 rests on it, and novelty here would be a liability.

---

## 16. Key Takeaways

1. **Ownership is a value, not a lock.** A lock is invisible, dies with its holder, and cannot be
   indexed. Two columns — who, and until when — turn every question the cold open could not answer
   into a query.
2. **A lease gives liveness; a version CAS gives safety.** Neither substitutes for the other, and
   each looks complete on its own, which is why implementing one is the most common serious defect
   here.
3. **A stale writer stops because its write affects nothing.** No consensus, no fencing service, no
   failure detector — the whole distributed correctness argument is a `WHERE` clause.
4. **Checkpoint after every step.** About five milliseconds against a step measured in seconds, and
   it buys the guarantee that a crash loses at most one in-flight step.
5. **Signals ride along with the checkpoint.** One extra indexed query inside a transaction that was
   already open, and it is the difference between cancelling in seconds and cancelling in minutes.
6. **One clock, and it belongs to the database.** Comparing expiry in application code across a
   skewed fleet produces workers that believe dead leases are live.
7. **Recovery is one indexed query.** A partial index on `lease_until` makes sweep cost proportional
   to failures rather than to runs — forty rows out of ten million.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **State manager** | The component that records where a run has got to and who is entitled to advance it. | `[DAR]` | Ch 18, Ch 21 |
| **Lease column** | Ownership stored as data — holder and expiry — so it is queryable, indexable, and outlives its holder. | `[DAR]` | Ch 23, Ch 32 |
| **Version CAS** | A conditional update guarded by an expected version, so a stale writer's write affects zero rows. | `[DAR]` | Ch 21, Ch 32 |
| **Checkpoint** | The single transaction that advances a run, renews its lease, appends a step, and reads pending signals. | `[DAR]` | Ch 18 |
| **Superseded** | The outcome a worker infers from affecting zero rows: it no longer owns the run and must stop. | `[INF]` | Ch 32 |
| **Sweep** | The one indexed query that reclaims runs whose leases have expired. | `[DAR]` | Ch 27 |
| **Partial expiry index** | An index on `lease_until` restricted to non-terminal runs, making recovery cost scale with failures rather than runs. | `[INF]` | Ch 33 |
| **Run store** | The narrow, hot table holding one row per run; everything that grows lives elsewhere. | `[INF]` | Ch 33 |
| **Claim race** | Two workers attempting one run, resolved by one of them affecting zero rows; a normal outcome, never an error. | `[DAR]` | Ch 23 |

---

**Next:** Chapter 18 — *The Runtime Loop.* The keystone: the Episode as a bounded execution window,
the four exit conditions, why no scarce resource is held across a model call, and why a step budget
of one is a configuration dial rather than an architecture.
