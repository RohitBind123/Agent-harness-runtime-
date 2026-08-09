```
  Level 3 · Chapter 23
  THE SCHEDULER: QUEUES, WORK CLASSES, ADMISSION
  Requires   C17 The State Manager, C18 The Runtime Loop,
             C21 Durable Execution, C22 The Event Spine
  Unlocks    C29 Long-Running Agents, C33 Scalability,
             C36 Reliability and SLOs, C37 Tenancy
  Diagrams   Full (9)
```

# Chapter 23 — The Scheduler: Queues, Work Classes, Admission

---

## 1. Motivation

### 1.1 Cold open

11:40. A customer kicks off a bulk migration: four hundred runs, submitted in about ninety seconds,
each one a slow repository-wide refactor.

11:44. Every other customer's work stops.

Nothing is broken. The queue is FIFO and it is being perfectly fair in the only sense it understands:
first come, first served. Four hundred long runs arrived first, so four hundred long runs are served
first, and the sixteen workers are occupied for the next two hours.

A different customer submits a run at 11:46 that would take forty seconds. It starts at 13:31.

Support escalates it as an outage. It is not an outage — throughput is at its normal ceiling, error
rates are zero, and every one of those four hundred runs is progressing exactly as designed. The
system is doing precisely what it was told to do, at full capacity, for one tenant.

The team's first fix is to raise the worker count. That doubles throughput and changes the forty-
second run's start time from 13:31 to 12:36.

### 1.2 In plain language

The scheduler decides what gets worked on next, and by whom.

That sounds like a queue, and a single queue is what most systems start with. It works until two
things are true at once, and in this system they always are: some work takes vastly longer than
other work, and multiple customers share the same machines.

The cold open is what happens then. A queue serves in arrival order, which is fair in one sense and
catastrophic in the sense customers actually experience: a short job that arrived second waits behind
a long job that arrived first, and four hundred long jobs make everybody else wait for hours.

The fix is not more workers. Doubling capacity halves the wait, which is still hours. The fix is to
stop treating all work as one pool — separate it by how long it takes, so short work is never stuck
behind long work, and by whom it belongs to, so no single customer can occupy everything at once.

There is a third thing, and it is the one this chapter argues is most often got wrong. The system has
several different scarce resources — workers, database connections, and the model provider's rate
limit — and they run out at different times for different reasons. A single number controlling
"concurrency" cannot bound three things that are not the same thing.

### 1.3 Why this chapter exists

Chapters 17 and 18 built claiming and yielding. Every episode ends and returns a run to the pool,
which is what makes scheduling possible at all — a system whose runs held workers to completion would
have nothing to schedule.

This chapter uses that. `[DAR §5.4]` It is where fairness, latency classes, and admission control
live, and it is the chapter that makes the difference between a runtime that works for one customer
and one that works for many.

`[INF]` It is also where a specific and common mistake gets corrected. Teams reach for "max
concurrency" as a single integer because that is what web servers have. Here it must bound three
separate resources with different sizes, different costs, and different exhaustion behaviour, and
§5.4 is about why one number cannot do it.

### 1.4 What previous framings got wrong

**"FIFO is fair."** It is fair to *arrivals* and unfair to *customers*, and the cold open is the
difference. §5.2 gives the fairness definition that matches what people actually mean.

**"Scale out to fix contention."** The cold open's first fix. More workers is more throughput, and
the queueing structure is unchanged, so the waiting is halved rather than removed. Structural
problems do not respond to capacity.

**"One concurrency limit."** `[DAR §5.4]` Three resources, three limits. A single integer sized for
the scarcest starves the others and sized for the most plentiful exhausts the scarcest.

**"Priority queues solve this."** `[INF]` Priority solves *ordering* and creates starvation: low
priority work waits indefinitely while high-priority work keeps arriving. §5.3 uses work classes with
reserved capacity instead, which is a different mechanism with a different failure mode.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A supermarket's checkouts.

One queue for every till is the cold open. Somebody with a full trolley arrives before you and your
two items wait behind their ninety. The queue is scrupulously fair by arrival and everybody with a
small basket has a bad time.

Supermarkets fixed this a long time ago, and with three separate mechanisms rather than one.

**A basket-only till.** That is a work class: capacity reserved for short work, so short work is
never stuck behind long work. Note what it is not — it is not a priority. A full trolley does not get
served *after* baskets; it gets served at a different set of tills entirely.

**A limit on trolleys per customer.** Nobody brings forty trolleys through at once, because the shop
would stop working for everyone else. That is per-tenant admission.

**A queue at the door on Christmas Eve.** When the shop is genuinely full, people are held outside.
It feels worse than being let in, and it is better: inside stays navigable, and the people inside get
served rather than everybody grinding to a halt together. That is admission control, and §5.5 is
about why refusing at the door beats accepting everything.

**Where the analogy breaks.** A supermarket's scarce resource is essentially one thing — checkout
time — and floor space is elastic enough not to matter.

`[INF]` Here there are three scarce resources with different sizes and different exhaustion
behaviours: workers (tens), database connections (tens, held for milliseconds), and the model
provider's rate limit (fixed, external, and the one you cannot buy your way out of on a Friday
afternoon). A till count bounds one thing; §5.4 needs three separate bounds, and the resource that
binds changes with the shape of the work.

### 2.2 Why one number cannot bound three resources

```
  1. A run in flight consumes: a worker slot, a model-semaphore slot
     while an activity runs, and a DB connection for ~5 ms at each
     checkpoint (Ch 18 section 5.3).
  2. Those are held for wildly different durations -- minutes,
     minutes, milliseconds -- so they are exhausted by different
     workloads.
  3. Many short steps exhaust CONNECTIONS while barely touching the
     model limit.
  4. Few long model calls exhaust the MODEL LIMIT while barely
     touching connections.
  5. So the resource that binds depends on the shape of the work,
     and the shape changes hourly.
  6. One integer sized for the scarcest resource starves the others;
     sized for the most plentiful it exhausts the scarcest.
  7. Therefore each resource needs its own bound, and the system runs
     at the minimum of them -- which is a property to MEASURE, not to
     configure.
```

Step 7 is the practical conclusion. `[INF]` There is no single correct concurrency number, and
looking for one is the mistake. What you configure is three limits; what you monitor is which of them
is currently binding, because that tells you what to buy more of.

### 2.3 Three mechanisms, three problems

`[DAR §5.4]` They are independent and each solves something the others cannot:

| Mechanism | Solves | Without it |
|---|---|---|
| **Work classes** | short work stuck behind long work | the cold open's convoy |
| **Per-tenant admission** | one customer occupying everything | the cold open's cause |
| **Resource semaphores** | exhausting a scarce resource | timeouts and provider rate-limit errors |

`[INF]` Teams usually build the third — it is the one that produces visible errors — and skip the
first two, which produce *waiting*. Waiting is not an error, appears on no dashboard by default, and
is what customers experience.

### 2.4 The mental model to carry

> **Throughput is what the system produces. Fairness is how it is distributed. Capacity fixes the
> first and never the second.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  submissions
       |
       v
  +====+=========================================+
  |  ADMISSION            (1) accept / defer /   |
  |   per-tenant in-flight cap    refuse         |
  |   global backpressure                         |
  +====+=========================================+
       | accepted
       v
  +----+-----------------------------------------+
  |  ROUTING              (2) classify by work   |
  |   work class from the goal + history          |
  +--+--------------+--------------+--------------+
     |              |              |
     v              v              v
  (( interactive )) (( standard )) (( bulk ))     (3) one queue
   short, latency-  the default    long, batch,       per class
   sensitive                       cost-tolerant
     |              |              |
     +------+-------+------+-------+
            |              |
            v              v
  +---------+--------------+---------------------+
  |  WORKERS                                     |
  |   reserved capacity per class (4)            |
  |   claim (Ch 17) -> drive (Ch 18) -> release  |
  +---------+---------+---------+----------------+
            |         |         |
       (5)  v    (6)  v    (7)  v
     model       DB pool     sandbox
     semaphore   Ch 33       Ch 31
     4-16        20-30       hosts
       ^           ^           ^
       |           |           |
       +-----------+-----------+
        THREE resources, THREE bounds, and the one
        that binds changes with the work (section 2.2)

  Figure 23.1 -- The scheduler (D1 High-Level Architecture)

  (1) refuse at the door rather than accept and starve (5.5)
  (2) classification happens once, at admission
  (3) separate queues, NOT priorities on one queue (5.3)
  (4) reserved, not preferred: bulk cannot take interactive's share
  (5) the external limit; the one you cannot buy on a Friday
  (6) held for ~5 ms at a time, so it binds on step RATE
  (7) sandbox capacity, if tools need isolation
```

`[INF]` The diagram's important feature is that (5), (6), and (7) are drawn as separate bounds
reached from the same worker pool. A design with one limit has those three collapsed into the arrow
above them, and then the system's behaviour under load depends on which resource happens to run out
first — which is unpredictable, because it depends on the workload mix.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  ADMISSION -- evaluated at submission, before a row exists

  +--------------------------------------------------------------+
  | 1. tenant in-flight count >= tenant cap?                      |
  |      yes -> DEFER: accept the goal, park it QUEUED.           |
  |             The work is not lost; it is not started.          |
  |                                                              |
  | 2. global in-flight >= global cap?                             |
  |      yes -> DEFER, all tenants                                 |
  |                                                              |
  | 3. tenant over budget for the period? (Ch 35)                  |
  |      yes -> REFUSE with a reason. Not a defer: it will not     |
  |             become admissible by waiting.                      |
  |                                                              |
  | 4. otherwise ADMIT                                             |
  +--------------------------------------------------------------+

  ROUTING -- classify once, at admission

  +--------------------------------------------------------------+
  | interactive  a person is waiting; expected minutes            |
  | standard     the default                                       |
  | bulk         batch-submitted, cost-tolerant, expected hours    |
  |                                                              |
  | The class is a property of the RUN, stored on the row, and    |
  | it does not change. A run that turns out slow stays in its    |
  | class -- reclassifying mid-flight makes latency               |
  | unattributable (section 5.3).                                  |
  +--------------------------------------------------------------+

  CLAIMING -- a worker picks a class, then a run

  +--------------------------------------------------------------+
  | reserved: interactive 6, standard 8, bulk 2   (of 16)         |
  |                                                              |
  | a worker holding a reserved interactive slot claims ONLY      |
  | from the interactive queue. It idles rather than taking       |
  | bulk work -- that idleness IS the reservation.                |
  |                                                              |
  | spillover: standard slots may take bulk when standard is      |
  | empty. Interactive slots never spill.                          |
  +--------------------------------------------------------------+

  Figure 23.2 -- Admission, routing, claiming
                 (D2 Low-Level Architecture)
```

### 4.1 Idle workers are the mechanism, not waste

`[INF]` The line teams delete first: a worker holding an interactive slot sits idle while bulk work
waits. That looks like inefficiency and it is the entire reservation. A reservation that yields under
pressure is a preference, and a preference fails exactly when it matters — under load, which is when
the cold open happens.

The honest cost is measurable: reserved-but-idle worker-seconds. `[INF]` If that number is large in
steady state the reservation is oversized, and the fix is to resize it rather than to make it
yielding.

```
                                                            LAYER VIEW

  Components.

   submission
        |
        v
   +----+------------+       +---------------------+
   | Admission       |------>| Tenant counters     |
   |  accept/defer/  |       |  in-flight per      |
   |  refuse         |       |  tenant             |
   +----+------------+       +---------------------+
        |
        v
   +----+------------+       +---------------------+
   | Classifier      |------>| Work-class registry |
   |  once, at entry |       |  reserved shares    |
   +----+------------+       +---------------------+
        |
        v
   (( per-class queues ))
        |
        v
   +----+------------+       +---------------------+
   | Claimer (Ch 17) |<------| Slot allocator      |
   |  by class       |       |  reserved, not      |
   +----+------------+       |  preferred          |
        |                    +---------------------+
        v
   +----+------------+
   | Runtime loop    |
   | (Ch 18)         |
   +----+------------+
        |
   +----+----+----------+----------+
   |         |          |
   v         v          v
 +-+-------+ +-+------+ +-+-------+
 | Model   | | DB     | | Sandbox |
 | semaph. | | pool   | | pool    |
 +---------+ +--------+ +---------+
   THREE independent bounds (section 5.4)

  Figure 23.3 -- Scheduler components (D3 Component Diagram)
```

---

## 5. Fairness, Classes, and Admission

### 5.1 The convoy effect, named

`[BP]` A convoy is what happens when short work queues behind long work in a shared FIFO. The name
comes from disk scheduling and the shape is identical: throughput stays high, and latency for short
work degrades in proportion to the length of whatever is ahead of it.

`[INF]` Agent runtimes are unusually prone to it because run durations span four orders of magnitude
— a lookup that takes twenty seconds and a refactor that takes six hours, submitted through the same
API, by the same customer, on the same day. A web service where every request takes 50-500 ms does
not have this problem, which is why the instinct to use one queue survives so long.

### 5.2 Two definitions of fair

| Definition | Serves | Cold open under it |
|---|---|---|
| **Arrival fairness** | first come, first served | working exactly as designed |
| **Tenant fairness** | each tenant a share of capacity | one tenant capped at its share |

`[INF]` Arrival fairness is what a queue gives you for free and it is almost never what is meant. The
question that separates them: *if one customer submits a thousand runs, should another customer's
single run wait for all of them?* Arrival fairness says yes. Everyone's actual expectation says no.

The mechanism for tenant fairness is per-tenant in-flight caps rather than weighted queueing.
`[INF]` A cap is easier to reason about, easier to explain to a customer, and produces a bounded
answer to "how long will my run wait?" that weighted fair queueing does not.

### 5.3 Work classes, not priorities

The distinction the fourth framing got wrong:

| | Priority queue | Work classes |
|---|---|---|
| Structure | one queue, ordered | separate queues |
| Low-priority work | waits while high-priority arrives | has **reserved** capacity |
| Starvation | yes, unbounded | no, by construction |
| Aging needed | yes, to prevent starvation | no |
| Latency guarantee for the low class | none | bounded by its reservation |

`[INF]` The starvation row is the reason. A priority queue under sustained high-priority load never
serves the low class, and the standard remedy — aging entries into higher priority — reintroduces the
convoy it was meant to prevent, because an aged bulk run now sits ahead of a fresh interactive one.

Reserved capacity has no such failure. Bulk always gets its two workers, however much interactive
work arrives, and interactive always gets its six.

### 5.4 Three semaphores, and the one that binds

`[DAR §5.4]` The bounds, and what each is sized against:

| Resource | Typical | Sized against | Exhaustion looks like |
|---|---|---|---|
| Workers | 8–32 | memory, and cost | queue depth rising with idle DB pool |
| Model semaphore | 4–16 | the **provider's** rate limit | `ModelUnavailable` (Ch 13) |
| DB pool | 20–30 | checkpoint rate (Ch 18 §12.2) | checkpoint latency rising |
| Sandbox | hosts | tool isolation needs (Ch 31) | dispatch queueing on creation |

`[INF]` The model semaphore is the one to size first and the one people size last, because it is the
only bound that is *external*. You can add workers and connections on a bad afternoon; you cannot
add provider quota. Chapter 13 §12.1 already said the model semaphore is the real concurrency bound,
and this is where that becomes a scheduling decision rather than an observation.

**Which one binds is a measurement, not a configuration.** §13.1 makes it a dashboard, and the answer
changes with the workload mix — which is exactly why one integer cannot express it.

### 5.5 Admission: refuse or defer, but decide at the door

`[INF]` When the system is at capacity, three responses, and two are correct:

| Response | When | The customer sees |
|---|---|---|
| **Admit** | there is room | it starts |
| **Defer** | temporarily full | accepted, queued, with a position |
| **Refuse** | it will never be admissible — over budget, over quota | a clear reason, immediately |
| ~~Accept and starve~~ | never | "running" for two hours with no progress |

The fourth row is the cold open's actual behaviour, and it is the worst of the four because it is
indistinguishable from a broken system. `[INF]` A run that is accepted and then does not start looks
exactly like a run that is stuck, and Chapter 8 §13.3's runbook cannot tell them apart. **A deferred
run must be visibly deferred** — a distinct state, with a queue position — or you have converted a
capacity problem into a support ticket.

### 5.6 Deferral is not a park

Chapter 5's Park is a run waiting on an *external* condition: a human, a timer, an event. A deferred
run is waiting on *capacity*, which is internal and requires no event to resolve.

`[INF]` The distinction matters operationally. Parked runs are normal and can last weeks; a deferred
run lasting an hour is a capacity signal. Collapsing them into one state — which is tempting, since
both hold nothing — means Chapter 8's runbook answer "PARKED: nothing is wrong" becomes wrong some
of the time, and the on-call engineer has no way to tell which.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  tenant A     tenant B    admission   queues      workers
     |             |           |          |           |
  11:40  A submits 400 bulk runs         |           |
     |------------------------>|          |           |
     |             |  runs 1-25: ADMIT (tenant cap 25)|
     |             |  runs 26-400: DEFER, state=QUEUED|
     |             |           |-- bulk --->|          |
     |             |           |          |-- claim -->| 2 bulk slots
     |             |           |          |           |  (reserved)
     |             |           |          |           |
  11:46  B submits 1 interactive run     |           |
     |             |---------->|          |           |
     |             |  tenant B in-flight: 0 of 25 -> ADMIT
     |             |           |-- interactive -->|   |
     |             |           |          |-- claim -->| 6 interactive
     |             |           |          |           |  slots, 5 idle
     |             |           |          |           |
  11:46:03  B's run STARTS. Three seconds, not 105 minutes.
     |             |           |          |           |
     |  A's remaining 375 runs drain through 2 bulk slots
     |  plus spillover from standard when standard is idle
     |             |           |          |           |
     |  A can SEE the deferral: 375 QUEUED, position visible
     |  (section 5.5) -- not 375 runs "running" and stuck

  The cold open, for contrast:
     one FIFO queue, 16 workers, no caps.
     B's run is position 401. It starts at 13:31.
     Every dashboard is green throughout.

  Figure 23.4 -- The same submission, scheduled (D4 Sequence)
```

### 6.1 What did the work

Three mechanisms, and removing any one restores the cold open.

**The tenant cap** stopped A occupying everything. Without it, A's 400 runs are all admitted and the
class reservation only slows the damage.

**The class reservation** kept six workers available for interactive work. Without it, A's 25
admitted runs occupy all 16 workers and B waits behind them.

**Visible deferral** is what made this a capacity conversation rather than an incident. A's 375
queued runs are queued, not stuck, and that distinction is the difference between a status page and a
support escalation.

`[INF]` Note that throughput is *unchanged*. The same 400 runs complete in the same total time. All
that changed is who waits, which is the whole of §2.4.

```
                                                             TIME VIEW

  The scheduling cycle, per submission and per claim.

  SUBMISSION
        |
        v
      /   \
     /over   \ yes -> E1 REFUSE with a reason (budget, quota)
     \ quota? /
      \      /
        | no
        v
      /   \
     /tenant \ yes -> E2 DEFER: accept, state=QUEUED, position
     \ at cap?/        visible (section 5.5)
      \      /
        | no
        v
   +----+-----------------+
   | classify + enqueue   |  once, at entry
   +----+-----------------+
        |
        v
      E3 admitted

  CLAIM (a worker with a free slot)
        |
        v
   +----+-----------------+
   | which class is this  |
   | slot reserved for?   |
   +----+-----------------+
        |
        v
      /   \
     /work in \ no -> may I spill? interactive: NO -> E4 idle
     \ class? /        standard: yes -> take bulk
      \      /
        | yes
        v
      /   \
     /model  \ full -> E5 wait on the semaphore, do NOT claim
     \ sem?  /          (claiming would hold a run we cannot drive)
      \     /
        | free
        v
   +----+-----------------+
   | claim (Ch 17)        |
   +----+-----------------+
        |
        v
      E6 driving

  Exits:
    E1  refused: will not become admissible by waiting
    E2  deferred: visibly queued, resolves on capacity
    E3  admitted and enqueued
    E4  reserved idle -- the mechanism, not waste (section 4.1)
    E5  resource-bound; the semaphore is doing its job
    E6  claimed and driving

  Figure 23.5 -- Admission and claiming (D5 Runtime Loop)
```

`[INF]` E5 is subtle and worth the space: a worker checks the model semaphore *before* claiming a
run, not after. Claiming first would take ownership of a run it cannot advance, holding a lease and
blocking other workers while it waits. Check the scarce resource before taking the work.

---

## 7. State Management

```
                                                            STATE VIEW

  A run's scheduling state, orthogonal to Ch 8's run state.

            +---------------------+
            | {{ SUBMITTED }}     |
            +----------+----------+
                       | admission evaluates
          +------------+------------+
          |            |            |
   refused|     deferred|            | admitted
          v            v            v
  +-------+---+  +-----+--------+  +-+---------------+
  |{{REFUSED}}|  |{{ QUEUED }}  |  | {{ ADMITTED }}  |
  +-----------+  +-----+--------+  +-+---------------+
   terminal;      visibly waiting    |
   a reason        on CAPACITY       | claimed
   given           (not a park --    v
                    section 5.6)   +-+---------------+
                       |           | {{ RUNNING }}   |
                       | capacity  +-+---------------+
                       | frees       |
                       +------------>+
                                     |
                                     | episode ends (Ch 18)
                                     v
                            +--------+--------+
                            | {{ ADMITTED }}  |  back to the queue;
                            +-----------------+  the class does NOT
                                                 change (section 5.3)

  Illegal, and enforced:
    * QUEUED presented as RUNNING     -- section 5.5's fourth row
    * class changed mid-flight        -- latency unattributable
    * claiming without a model slot   -- E5; holds a run it cannot
                                         drive
    * a reservation that yields       -- then it is a preference (4.1)

  Figure 23.6 -- Scheduling states (D6 State Diagram)
```

### 7.1 Scheduling state is not run state

`[INF]` A run's Chapter 8 state (`CREATED`, `EXECUTING`, `PARKED`) answers *what is the work doing*.
Its scheduling state answers *why is it not being worked on*. They are independent and both are
needed: `EXECUTING` + `QUEUED` is a run that has started, yielded at an episode boundary, and is
waiting for a slot — which is entirely normal and looks alarming if the two are conflated.

### 7.2 Counters must be exact, and that costs something

Per-tenant in-flight counts are read on every admission decision and updated on every claim and
release. `[INF]` A cached or eventually-consistent counter admits more than the cap under burst,
which is precisely when the cap matters.

The cheap correct answer is a conditional insert against a `SELECT count(*)` in the same transaction
as the admission, indexed on `(tenant_id, state)`. It costs one indexed count per submission, which
is nothing against the run itself.

---

## 8. Internal APIs

```python
from typing import Protocol


class AdmissionPort(Protocol):
    """Decides at the door. The alternative -- accept everything and
    let the queue sort it out -- is the cold open."""

    async def evaluate(
        self, tenant_id: str, goal: Goal
    ) -> AdmissionDecision:
        """ADMIT, DEFER, or REFUSE.

        DEFER accepts the goal and makes the wait VISIBLE (section 5.5).
        REFUSE is for conditions waiting will not fix, and carries a
        reason the caller can act on.
        """


class SchedulerPort(Protocol):
    async def classify(self, goal: Goal, tenant_id: str) -> WorkClass:
        """Once, at admission. The class is stored on the run and does
        not change (section 5.3)."""

    async def claim_for_slot(
        self, worker_id: str, slot: ReservedSlot
    ) -> ClaimedRun | None:
        """Claim from the slot's class, spilling only where the class
        permits. Returns None when the class is empty -- and the worker
        IDLES rather than taking other work, which is the reservation
        (section 4.1)."""


class ResourceBounds(Protocol):
    """Three, not one (section 5.4)."""

    model_semaphore: Semaphore     # sized against the PROVIDER limit
    db_pool: Pool                  # sized against checkpoint rate
    sandbox_pool: Pool             # sized against isolation needs

    def binding_resource(self) -> str:
        """Which bound is currently limiting. A measurement, not a
        configuration -- and the answer changes with the workload."""
```

`[INF]` `binding_resource()` existing as a method rather than a dashboard query is deliberate: it
makes the question answerable from inside the system, which is what lets §13.1 alert on a *change* of
binding resource. A shift from model-bound to connection-bound means the workload's shape changed,
and that is usually the earliest signal that something upstream is different.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class WorkClass(StrEnum):
    INTERACTIVE = "interactive"   # a person is waiting
    STANDARD = "standard"         # the default
    BULK = "bulk"                 # batch, cost-tolerant


class AdmissionOutcome(StrEnum):
    ADMIT = "admit"
    DEFER = "defer"               # visible; resolves on capacity
    REFUSE = "refuse"             # waiting will not help


@dataclass(frozen=True)
class ClassReservation:
    work_class: WorkClass
    reserved_workers: int
    may_spill_to: tuple[WorkClass, ...]   # INTERACTIVE spills nowhere


@dataclass(frozen=True)
class AdmissionDecision:
    outcome: AdmissionOutcome
    reason: str | None            # required on REFUSE and DEFER
    queue_position: int | None    # required on DEFER (section 5.5)
    estimated_start: datetime | None


@dataclass(frozen=True)
class SchedulerPressure:
    """What §13.1 dashboards. Which bound binds is the headline."""
    binding_resource: str
    workers_idle_reserved: int    # the cost of reservations (4.1)
    queued_by_class: Mapping[WorkClass, int]
    deferred_by_tenant: Mapping[str, int]
    oldest_queued_age_ms: int
```

`[INF]` `queue_position` being required on a deferral is the structural form of §5.5. A deferral
without a position is indistinguishable from a stall for the person waiting, and making the field
non-optional means the API cannot express the unhelpful version.

`workers_idle_reserved` is the honest counterpart: it is the price of §4.1, measured, so a
reservation that is too large is visible rather than argued about.

---

## 10. Communication

```
                                                            LAYER VIEW

  submission    edge      ====> admission     ~2-20 KB
  counters      admission <==== [[ runs ]]    one indexed count
  enqueue       admission ====> (( class Q )) ~100 B, id only (Ch 8)
  claim         worker    ====> [[ runs ]]    Ch 17's CAS
  semaphore     worker    <===> in-process    no I/O

  Volume note: scheduling is cheap. The expensive thing it protects
  is worker time, which is why the arithmetic in section 12.1
  favours checking before claiming rather than after.

  Figure 23.7 -- What scheduling moves (D7 Data Flow)
```

```
                                                             TIME VIEW

  edge ----------> admission   evaluate BEFORE creating work
  admission -----> classifier  once; the class is then fixed
  worker --------> semaphore   check BEFORE claiming (E5)
  worker --------> claimer     from its slot's class only
  worker --X       other class REFUSED unless spill is permitted
  bulk --X         interactive REFUSED always: no spill upward
  capacity --X     fairness    more workers does not fix who waits

  Figure 23.8 -- Who decides what runs next (D8 Control Flow)
```

```
                                                             TIME VIEW

  << run.deferred >>        ....> tenant at cap; position recorded.
                                  A FACT: the customer is entitled
                                  to know they are queued
  << run.refused >>         ....> over budget or quota, with reason
  << scheduler.saturated >> ....> a class has been fully occupied
                                  beyond a threshold; capacity signal

  NOT events:
    claims and releases      churn; telemetry
    semaphore waits          telemetry
    queue depth              a metric

  Figure 23.9 -- What scheduling makes durable (D9 Event Flow)
```

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 29 Long-Running | bulk class, and six-hour runs | long work has a home |
| Ch 33 Scalability | which resource binds | sizing starts from the measurement |
| Ch 35 Cost | refusal on budget | the cap is enforced at the door |
| Ch 36 Reliability | deferral is not failure | SLOs must distinguish them |
| Ch 37 Tenancy | per-tenant caps and counters | fairness is a tenancy property |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Convoy | one FIFO for all durations | short-run latency tracking long-run arrivals | work classes — the cold open |
| One tenant occupies everything | no per-tenant cap | in-flight concentration by tenant | admission caps |
| Capacity as the fix | scaling out a structural problem | wait times halving, not resolving | §2.4 |
| One concurrency integer | web-server instinct | one resource saturated, others idle | three bounds (§5.4) |
| Priority instead of classes | ordering rather than reservation | low-priority starvation | reserved capacity (§5.3) |
| Reservation that yields | "idle workers are waste" | reservations failing exactly under load | it is a preference then (§4.1) |
| Accept and starve | no deferred state | runs "running" with no progress | visible deferral (§5.5) |
| Deferral modelled as a park | both hold nothing | the runbook cannot distinguish them | separate states (§5.6) |
| Claim before checking the semaphore | natural ordering | leases held by workers that cannot proceed | check first (E5) |
| Cached tenant counters | avoiding a count per submission | caps exceeded under burst | exact, in the admission txn (§7.2) |
| Reclassification mid-flight | "it turned out to be long" | latency unattributable to any class | class is fixed at entry |

`[INF]` Row seven is the one that generates support load rather than incidents, which is why it
survives. Everything works; some customers' runs never start at all, and the interface says
"running". The fix is a state and a number, and it converts an unexplainable experience into a
capacity conversation.

---

## 12. Scalability

### 12.1 Scheduling is cheap; what it protects is not

One indexed count per submission and one semaphore check per claim, against runs costing dollars and
minutes. `[INF]` That asymmetry is why every check in this chapter happens *before* work is taken
rather than after: the check costs microseconds and the mistake costs a held lease and a blocked
worker.

### 12.2 Sizing the three bounds

| Bound | Start at | Then |
|---|---|---|
| Model semaphore | 60–80% of the provider's concurrent limit | raise until `ModelUnavailable` appears, back off |
| DB pool | Chapter 18 §12.2's checkpoint arithmetic | watch checkpoint latency p99 |
| Workers | model semaphore × 2–4 | most are waiting on activities, holding nothing |
| Class reservations | interactive 40%, standard 50%, bulk 10% | resize from `workers_idle_reserved` |

`[INF]` The workers row is the one that surprises: workers should *exceed* the model semaphore,
often by several times, because a worker awaiting an activity holds a semaphore slot and nothing else
(Chapter 18 §5.3). Sizing workers equal to the model limit leaves the fleet idle whenever runs are
between activities.

### 12.3 Per-tenant caps and the long tail

`[INF]` A cap of 25 in-flight per tenant sounds restrictive and is not, because in-flight is not the
same as accepted. A tenant submitting a thousand runs has 25 running and 975 visibly queued, draining
continuously. Their total completion time is barely different from the unfair case; what changed is
that everybody else is unaffected.

The cap to avoid is one so low that a single tenant cannot use idle capacity. `[INF]` The refinement
is a soft cap that rises when the system is quiet — but it should rise, never the reservation yield,
because the reservation is what protects latency and the cap is what protects share.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| **Which resource binds** | §5.4; the single most useful number here | on a *change* of binding resource |
| Queue wait p50/p99, by class | is each class meeting its promise | interactive p99 above SLO |
| Deferred runs by tenant | fairness working, and capacity pressure | sustained deferral for one tenant |
| `workers_idle_reserved` | the honest cost of reservations (§4.1) | large in steady state — resize |
| Oldest queued age, by class | starvation, if classes were misconfigured | bulk age unbounded |
| In-flight concentration by tenant | the cold open's cause | one tenant above its share |
| `ModelUnavailable` rate | the semaphore is sized too high | any sustained |

`[INF]` Alerting on a *change* of binding resource rather than on any particular one is the
non-obvious recommendation. Each of the three saturating is normal at different times; what is worth
waking up for is the mix shifting, because that means the workload changed and every capacity
assumption downstream is now based on the wrong resource.

### 13.2 The test that catches the cold open

```python
async def test_one_tenant_cannot_starve_another(
    runtime: Runtime, clock: FakeClock
) -> None:
    # Tenant A floods.
    for _ in range(400):
        await runtime.submit(tenant="A", goal=long_goal, work_class=BULK)

    # Tenant B arrives six minutes later with one short run.
    clock.advance(minutes=6)
    b_run = await runtime.submit(tenant="B", goal=short_goal,
                                 work_class=INTERACTIVE)

    started = await runtime.wait_until_started(b_run, timeout=seconds(30))

    # The property: B starts in seconds, not after A's queue drains.
    assert started, "B starved behind A -- the cold open"
    assert await runtime.queue_wait(b_run) < seconds(10)

    # And A's excess is VISIBLY deferred, not silently stuck.
    deferred = await runtime.runs(tenant="A", scheduling_state=QUEUED)
    assert len(deferred) == 400 - TENANT_CAP
    assert all(r.queue_position is not None for r in deferred)
```

`[INF]` The last two assertions are the ones most fairness tests omit. Proving B starts is half the
property; proving A's remainder is *visibly* queued is what stops §5.5's fourth row from being
reintroduced by a later refactor.

### 13.3 The runbook entry

> **A customer says their run has not started.** Read its scheduling state first.
> `QUEUED` — it is deferred. Read the position and the tenant's in-flight count; this is capacity or
> a cap, not a fault.
> `REFUSED` — read the reason; it is budget or quota.
> `ADMITTED` but not `RUNNING` for more than a minute — check which resource is binding, and whether
> its class has any free slots.
> `RUNNING` — this is Chapter 8's runbook, not this one.

---

## 14. Relation to AHE

The scheduler is runtime and the loop does not edit it, but two of its properties determine whether
an evolution iteration means anything.

**Benchmark rollouts must not contend with production.** `[INF]` Chapter 41 runs hundreds of
rollouts; submitting them through the same scheduler as customer work makes the benchmark's timing a
function of production load and makes production a function of the benchmark. Rollouts belong in
their own work class with its own reservation at minimum, and on separate capacity where possible.

**Queue wait must not be inside the measured duration.** `[INF]` If a rollout's recorded duration
includes time spent deferred, then a busy afternoon makes the harness look slower and Chapter 47
attributes an infrastructure artefact to a harness edit. Duration for evaluation purposes is Chapter
8 §5.3's *active time*, and the scheduling state machine in §7 is what makes it separable.

**And the loop can make scheduling worse without touching it.** `[INF]` An edit that increases steps
per run, or moves work from one work class to another by changing how goals are phrased, changes the
system's load shape. Chapter 41 should therefore report cost and duration alongside quality — which
`[AHE App. A]`'s tokens-per-trial already does for cost, and this chapter argues should extend to
scheduling pressure.

---

## 15. Industry Perspective

**`[DAR]`** Supplies work classes and latency-class partitioning, the model semaphore as a distinct
bound, per-tenant admission control, and the observation that one concurrency limit cannot bound
three resources `[DAR §5.4]`.

**`[AHE]`** Nothing directly; the relation is Chapter 41's need for uncontended rollouts.

**`[INF]`** The handbook's own: the two definitions of fairness and the question that separates them,
reserved capacity in preference to priority with starvation as the reason, idle reserved workers as
the mechanism rather than waste, the four admission responses with accept-and-starve named as the
worst, deferral distinguished from a park, checking the semaphore before claiming, and alerting on a
change of binding resource rather than on any one saturating.

**`[BP]`** Convoy effects, admission control, and reserved-capacity scheduling are long-established in
operating systems and storage. The supermarket framing is folklore. The contribution is applying them
to a workload whose durations span four orders of magnitude, where the convoy is unusually severe.

**`[FUT]`** `[FUT]` Classification is done once at admission from the goal and history, which is a
guess. Whether a learned classifier — predicting duration from the goal text — beats the declared
class enough to justify the machinery is unmeasured, and the handbook's position is that a wrong
prediction is worse than a declared class because it is unattributable.

---

## 16. Key Takeaways

1. **FIFO is fair to arrivals, not to customers.** Four hundred long runs from one tenant make
   everybody else wait for hours, and every dashboard stays green throughout.
2. **Capacity does not fix fairness.** Doubling workers halved the cold open's wait from 105 minutes
   to 56. Structural problems need structural fixes.
3. **Work classes, not priorities.** Reserved capacity cannot starve; priority queues can, and the
   standard remedy for starvation reintroduces the convoy.
4. **A reservation that yields is a preference**, and it fails exactly under load, which is when it
   was needed. Idle reserved workers are the mechanism; measure the cost and resize.
5. **Three resources, three bounds.** Workers, the model semaphore, and the connection pool are
   exhausted by different workloads. Which one binds is a measurement that changes hourly.
6. **Decide at the door.** Admit, defer, or refuse — and make a deferral *visible*, with a position.
   Accepting a run that will not start for two hours is indistinguishable from a broken system.
7. **Deferral is not a park.** Both hold nothing, and conflating them makes "PARKED: nothing is
   wrong" false some of the time, with no way for the on-call engineer to tell which.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Convoy effect** | Short work queueing behind long work in a shared FIFO, degrading latency in proportion to what is ahead. | `[BP]` | Ch 33 |
| **Work class** | A category of work with its own queue and reserved capacity, so short work is never stuck behind long. | `[DAR]` | Ch 29, Ch 33 |
| **Reserved capacity** | Workers a class always gets, idling rather than yielding, which is what makes it a reservation. | `[INF]` | Ch 33 |
| **Spillover** | Permission for one class's idle slots to take another's work; never upward into interactive. | `[INF]` | Ch 33 |
| **Tenant fairness** | Each tenant getting a share of capacity, as against arrival fairness which serves whoever queued first. | `[INF]` | Ch 37 |
| **Admission control** | Deciding at submission whether to admit, defer, or refuse, rather than accepting everything. | `[DAR]` | Ch 36, Ch 37 |
| **Deferral** | An accepted run visibly waiting on capacity, with a position, distinct from a park. | `[INF]` | Ch 36 |
| **Model semaphore** | The bound on concurrent model calls, sized against the provider's external limit rather than local hardware. | `[DAR]` | Ch 33 |
| **Binding resource** | Whichever of the three bounds is currently limiting; a measurement rather than a configuration. | `[INF]` | Ch 33 |
| **In-flight cap** | The per-tenant limit on concurrently running work, enforced exactly in the admission transaction. | `[DAR]` | Ch 37 |

---

**Next:** Chapter 24 — *The Task Graph.* From ordered steps to a directed graph: dependency
resolution, parallel steps, durable joins, fan-out and fan-in, and cycle prevention — extending
Chapter 10's linear plan without changing its identity scheme.
