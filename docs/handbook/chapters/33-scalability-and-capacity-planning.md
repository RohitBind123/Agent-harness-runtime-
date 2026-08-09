```
  Level 4 · Chapter 33
  SCALABILITY AND CAPACITY PLANNING
  Requires   C23 The Scheduler, C29 Long-Running Agents,
             C32 Distributed Execution
  Unlocks    C35 Cost Engineering, C36 Reliability and SLOs,
             C41 Evaluation Infrastructure
  Diagrams   Core (5)
```

# Chapter 33 — Scalability and Capacity Planning

---

## 1. Motivation

### 1.1 Cold open

The Atlas team is sizing for launch. They have twenty worker processes per replica and three
replicas, and they apply the formula every backend engineer knows: connection pool equals workers
times two, plus half that again in overflow.

Twenty times two is forty, plus twenty overflow, is sixty per replica. Three replicas is a hundred
and eighty connections.

Postgres is configured for `max_connections = 200`. There is a background job runner, a metrics
exporter, two engineers with psql sessions open, and the migration runner that fires on deploy.

At 14:20 on launch day the deploy rolls the third replica. Connection number 201 is refused. Then
so is every subsequent one, including the ones the *first two replicas* need to renew their leases.
Leases expire across the fleet. The sweeper cannot run, because the sweeper needs a connection.
Every run in the system stalls at once, and the recovery path is unavailable for the same reason the
failure happened.

The postmortem measures what the workers were actually doing. Across a step, a worker holds a
database connection for about five milliseconds and waits on a model call for about four seconds.
Peak measured concurrent connection demand across all sixty workers is **eleven**.

They provisioned a hundred and eighty. The outage was caused by over-provisioning, arrived at by
correctly applying a formula that was built for a different kind of system.

### 1.2 In plain language

Capacity planning asks how much of everything you need: how many worker processes, how big the
database connection pool, how many concurrent calls the model provider will allow, how many sandbox
hosts.

The usual shortcut is to size everything from the number of workers. That works for a web server,
where a request grabs a connection, does some database work, and returns — the connection is busy
for most of the request's life, so connections and requests scale together.

An agent runtime is not shaped like that. A single step spends a few milliseconds talking to the
database and several seconds waiting for a model to answer. Those two resources are busy for
wildly different fractions of the time, so the amount you need of each differs by roughly the same
factor. One formula cannot produce both numbers, and using one produces the cold open — either
starvation or, as here, an outage from asking for far too much.

The fix is not a better formula. It is measuring how long each resource is actually held, and
sizing each one from its own number.

There is a second difference that matters more. A web request arrives, is served, and leaves. A run
arrives and then *generates load for hours* — hundreds of model calls, thousands of database
operations, a sandbox held the whole time. Admitting a run is not serving a request. It is taking
on a commitment, and capacity planning for commitments is a different exercise from capacity
planning for requests.

### 1.3 Why this chapter exists

Chapter 23 built the scheduler and established that one global concurrency integer cannot bound
three different resources. It said what to bound. It did not say *how much*.

Chapter 29 established that runs can last six hours, which makes the service-time distribution
heavy-tailed. Chapter 32 established that leases, renewals, and fairness counters all cost store
round trips that scale with worker count. Both left numbers unspecified.

This chapter supplies the method, and it is deliberately arithmetic rather than architectural.
Nothing here is subtle. The reason it needs a chapter is that the arithmetic is almost never done —
the formula is applied instead, and the formula encodes assumptions about service time that are
wrong by two to three orders of magnitude in this domain.

`[DAR §5.2]`'s observation that worker concurrency may exceed pool size reads as a curiosity until
you compute the ratio. Then it reads as the central fact about sizing an agent runtime.

### 1.4 What previous framings got wrong

**"Pool size equals workers times two."** This encodes an assumption — that a worker holds a
connection for most of its working life — which is true of web servers and false here by a factor
of around eight hundred. The formula is not wrong; it is being applied outside its domain.

**"A run is a request."** A request is served and leaves. A run is admitted and then generates load
for its entire lifetime. Capacity models that count runs the way they count requests understate
sustained demand and overstate instantaneous demand at the same time.

**"Add workers until throughput stops improving."** That finds the binding constraint by exhausting
it, which in a shared system means finding it by causing an incident. Little's Law finds the same
number from measurements taken while everything is healthy.

**"Target 80% utilisation."** That target comes from systems with well-behaved service times. Agent
service times are heavy-tailed by construction, and on a heavy-tailed distribution queueing at 80%
is not slightly worse than at 70% — it is qualitatively different (§5.4).

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Capacity planning for an agent runtime is capacity planning for a hospital, not for a restaurant.

A restaurant has one dominant resource — tables — and everything else scales roughly with it.
Kitchen capacity, waiters, and plates all track covers per hour closely enough that sizing from one
number works.

A hospital does not work that way, and nobody would suggest it should. Beds, operating theatres,
imaging machines, and reception desks have service times that differ by orders of magnitude: a
reception interaction is three minutes, a bed is four days, a theatre is ninety minutes with a
strict serialisation constraint. Nobody sizes an intensive care unit from the number of
receptionists, because the absurdity is visible.

That is the whole point of the analogy. The cold open is exactly that absurdity, made invisible by a
formula. `pool_size = workers * 2` is sizing the ICU from the receptionists, and it does not look
absurd because both numbers are integers in the same configuration file.

Where the analogy breaks is on predictability, and the break matters.

A hospital's service times are **actuarially known**. Length of stay for a given procedure has a
distribution measured over decades, and while individual cases vary, the distribution is stable
enough to plan against.

Agent service times are not stable and the instability is not noise. A model upgrade changes them.
A change to a tool description changes them. A new customer with larger repositories changes them.
And the tail — the six-hour runs of Chapter 29 — is not an outlier to be trimmed but frequently the
most valuable work the system does.

So the hospital gives the right structure: measure each resource separately, size each from its own
service time. It withholds the assumption that last quarter's measurements describe next quarter,
which means §5.5's re-measurement discipline is not optional hygiene. It is the part that keeps the
rest true.

### 2.2 Why one formula cannot size four resources

```
  (1) Need: how many workers, how many DB connections, how many
      concurrent model calls, how many sandbox hosts.

  (2) Standard answer: derive them all from worker count. This is
      correct for web servers, where a request holds a connection
      for most of its life, so connections and requests move
      together.

  (3) Measure an agent STEP instead of assuming:
          DB connection held      ~5 ms
          model slot held         ~4 s
          sandbox held            ~40 s (whole node, not step)
          worker held             ~4 s (the whole step)
      The ratio between the first two is about 1:800.

  (4) Little's Law: the concurrency required at any resource is
      arrival rate x service time. Same arrival rate, service
      times differing by 800x, therefore required concurrency
      differing by 800x.

  (5) So one formula cannot produce both numbers. Any formula
      that does is right for at most one of them and wrong by
      up to three orders of magnitude for the others.

  (6) Size each surface from ITS OWN measured service time. This
      is the whole method and it is one multiplication per
      resource.

  (7) But arrival rate at each surface is not the run arrival
      rate. A run generates model calls at its own rate for its
      whole life -- a run is a LOAD GENERATOR, not a request.
      So the arrival rate at each surface is derived: runs per
      second x that surface's operations per run-second.

  (8) Which makes admission (C23) a capacity COMMITMENT rather
      than an instantaneous check. Admitting a six-hour run
      commits every surface it will touch for six hours, and a
      capacity model that checks the instant is measuring the
      wrong thing.
```

Step (7) is the reframing that makes the rest work, and step (8) is where it changes a decision
someone actually makes.

### 2.3 Four surfaces, four service times

| Surface | Service time per hold | Typical concurrency at 10 runs/min | Bounded by |
|---|---|---|---|
| **Worker** | ~4 s (a step) | Runs in flight, not steps | Process count, memory |
| **DB connection** | ~5 ms (a checkpoint) | Single digits | `max_connections`, and it is shared |
| **Model slot** | ~4 s (a call) | Tens to low hundreds | The provider's limit — the one you cannot buy on a Friday |
| **Sandbox host** | ~40 s (a node, not a step) | Tens | Hosts, and their start-up cost |

`[INF]` The numbers are illustrative of a mid-sized coding agent and are given to convey ratios
rather than to be quoted. The ratios are the transferable part, and the ratio that matters is the
one between rows two and three: **the database is nearly idle while the model is saturated**, in
almost every agent runtime, at almost every scale.

That single observation explains the cold open, explains why adding workers rarely helps, and
explains why the first capacity investigation of any new agent system should start at the model
semaphore rather than at the database.

### 2.4 The mental model to carry

Every resource has its own service time, measured rather than assumed, and its own required
concurrency by Little's Law. A run is a load generator whose commitment extends over its whole
lifetime, so admission is a promise about future capacity rather than a check on present capacity.
And because service times are heavy-tailed, the utilisation you can safely target is lower than
general engineering intuition suggests.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   arrival: runs per minute
        |
        v
   +--------------------------------------------------------------+
   |                    ADMISSION (C23)                           |
   |                                                              |
   |   NOT "is there capacity now?"                               |
   |   BUT "can we commit this run's whole future load?"          |
   |                                                              |
   |   commitment = expected_steps x per-surface holds            |
   +--------------------------------------------------------------+
        |
        | admitted runs become LOAD GENERATORS
        v
   +--------------------------------------------------------------+
   |                      RUNS IN FLIGHT                          |
   |   each emits, per run-second:                                |
   |     ~0.25 model calls | ~0.25 checkpoints | 1 sandbox-second |
   +--------------------------------------------------------------+
        |               |                |                |
        | (1)           | (2)            | (3)            | (4)
        v               v                v                v
   +----------+  +-------------+  +--------------+  +--------------+
   | Workers  |  | DB pool     |  | Model        |  | Sandbox      |
   |          |  |             |  | semaphore    |  | hosts        |
   | hold: 4s |  | hold: 5 ms  |  | hold: 4 s    |  | hold: 40 s   |
   | size:    |  | size:       |  | size:        |  | size:        |
   |  runs in |  |  Little's   |  |  provider    |  |  Little's    |
   |  flight  |  |  Law, ~11   |  |  limit       |  |  Law         |
   +----------+  +-------------+  +--------------+  +--------------+
        ^               ^                ^                ^
        |               |                |                |
        +---------------+----------------+----------------+
                        |
              each sized from ITS OWN service time.
              There is no shared multiplier. The cold open
              is what happens when one is invented.

  Figure 33.1 -- Four capacity surfaces, four service times (D1
                 High-Level Architecture)

  (1) workers are the only surface whose count tracks runs
  (2) the DB is nearly idle; sizing it from workers is the cold open
  (3) the model semaphore is almost always the binding constraint
  (4) sandbox holds span a whole node, not a step, which is why its
      service time is ten times the others
```

### 3.1 Admission is where the commitment is made

The box at the top is the chapter's structural claim. Chapter 23 built admission as a fairness and
classification mechanism; this chapter adds that it is also the only place where a capacity decision
can be made with any leverage.

Once a run is admitted it will generate load until it finishes. Refusing it later means killing it,
which wastes everything already spent. Every other control — the model semaphore, the pool, the
worker count — bounds *instantaneous* demand and can only queue or throttle. Admission is the one
that bounds *committed* demand, and it is therefore the only one that can prevent overcommitment
rather than absorb it.

`[BP]` Admit against expected total commitment, not against current utilisation. A system at 40%
utilisation with two hundred admitted six-hour runs is not at 40% — it is at 40% now and committed
to considerably more later, and the difference between those two readings is the difference between
a capacity model and a gauge.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                   CAPACITY MACHINERY                           |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Service-time meter     |  |   Commitment estimator    |   |
   |  |                          |  |                           |   |
   |  |  per surface, per hold:  |  |  from the graph at mint    |  |
   |  |    p50, p95, p99         |  |  time (C24):              |   |
   |  |                          |  |    node count             |   |
   |  |  THE input to every      |  |    critical path          |   |
   |  |  number in this chapter  |  |    effectful fraction     |   |
   |  |                          |  |                           |   |
   |  |  re-measured on every    |  |  -> expected holds per    |   |
   |  |  model change (5.5)      |  |     surface               |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Little's Law sizer     |  |   Saturation detector     |   |
   |  |                          |  |                           |   |
   |  |  required = lambda x S   |  |  per surface:             |   |
   |  |  headroom = required /   |  |    checked_out / size     |   |
   |  |             target_util  |  |    queue wait p95         |   |
   |  |                          |  |                           |   |
   |  |  target_util accounts    |  |  names WHICH surface is   |   |
   |  |  for the tail (5.4)      |  |  binding, which is the    |   |
   |  |                          |  |  only actionable output   |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 33.2 -- Inside the capacity machinery (D2 Low-Level
                 Architecture)
```

### 4.1 The service-time meter is the whole input

Everything else in this chapter is arithmetic over numbers this component produces. If the
measurement is wrong, every derived size is wrong, and the failure is silent because the arithmetic
is correct.

`[BP]` Measure the *hold*, not the operation. A database connection checked out for five
milliseconds of query and then held for four seconds across a model call has a service time of four
seconds, not five milliseconds, and the two implementations look nearly identical in code. This is
the single most common measurement error in this domain and it inverts the cold open's conclusion
entirely — a system that holds connections across model calls genuinely does need a large pool, and
the correct fix is to stop holding them rather than to size for it.

### 4.2 The saturation detector names one surface

Its output is not a number. It is a name: *which surface is binding right now*.

That matters because every capacity conversation that lacks it degenerates into adding workers. A
saturated model semaphore and a saturated database look identical from the outside — runs are slow —
and the responses are opposite. More workers make a saturated model semaphore worse, because they
add contention for a resource that is already the constraint while consuming the memory that might
have gone somewhere useful.

`[BP]` Emit `binding_surface` as a gauge with one label per surface, sampled every few seconds. It
costs nothing, and it converts the most common operational argument in this area into a lookup.

---

## 5. Sizing, Arithmetic, and the Tail

### 5.1 Little's Law, applied four times

```
                                                            LAYER VIEW

   L = lambda x W        concurrency = arrival rate x service time

   Given: 10 runs/min admitted, each ~24 min, ~90 steps
          => 240 runs in flight at steady state
          => 240 runs x 90 steps / 24 min = 900 steps/min = 15 steps/s

   SURFACE          arrival (lambda)   service (W)    required (L)
   --------------   ----------------   ------------   -------------
   Worker            10 runs/min        24 min         240 runs
                     -- but a worker holds a RUN, so: 240 workers?
                     NO: a worker holds a run only while STEPPING.
                     Parked, waiting, and gated runs hold nothing
                     (C30 sec 5.3). Effective: ~15 steps/s x 4 s
                     = 60 workers.

   DB connection     15 steps/s         5 ms          0.075  -> 1
                     plus lease renewals: 60 workers / 10 s = 6/s
                     x 3 ms = 0.018
                     plus sweeper, relays, admission
                     TOTAL measured peak: ~11

   Model slot        15 steps/s         4 s            60 slots
                     -- and this is the number the provider caps

   Sandbox host      10 runs/min        24 min         240 run-slots
                     at ~8 runs per host: 30 hosts

   THE COLD OPEN, in one line:
       DB required ~11.   DB provisioned 180.   max_connections 200.

   AND the number that actually matters:
       Model slots required 60. If the provider grants 40, then 40
       is the system's throughput ceiling and no amount of workers,
       connections, or hosts changes it.

  Figure 33.3 -- Little's Law applied to four surfaces (D7 Data Flow)
```

The second observation at the bottom is the one to internalise. In nearly every agent runtime the
model semaphore is the binding constraint, it is set by somebody else, and it cannot be raised by
spending money quickly. Every other surface should be sized comfortably above its requirement,
because the marginal cost of doing so is small and the marginal benefit of getting it exactly right
is zero — the system is going to be waiting on the model regardless.

`[BP]` Which yields a blunt planning heuristic worth stating: **size everything else generously,
size the model semaphore honestly, and treat the provider's limit as the system's capacity.**

### 5.2 Why worker concurrency may exceed pool size

`[DAR §5.2]` states this and it reads as a curiosity until §5.1's arithmetic. Sixty workers need
about eleven database connections, because each worker's database service time is a thousandth of
its step time.

Two conditions make it true, and both must hold:

- **Connections are checked out per operation, not per step.** Acquire, query, release, in
  milliseconds. A connection held for the duration of a step destroys the property.
- **No network I/O inside a transaction.** A transaction open across a model call has a service
  time of seconds, and sixty workers then genuinely need sixty connections.

`[BP]` Both conditions are testable. Instrument connection hold duration and alert when p99 exceeds
a small multiple of p50; a bimodal hold-time distribution is the signature of a connection being
held across something slow, and it is visible long before it causes an incident.

### 5.3 A run is a load generator

The web-request model of capacity gets two things wrong at once, in opposite directions.

**It understates sustained demand.** Ten runs per minute sounds small. At twenty-four minutes each,
that is two hundred and forty runs in flight, each producing model calls at its own rate — fifteen
steps per second in aggregate, sustained. The instantaneous arrival rate says nothing about the load.

**It overstates instantaneous demand.** Two hundred and forty runs in flight does not mean two
hundred and forty concurrent model calls. Runs are parked, gated, waiting on tools, or between
steps. The concurrent demand is set by the step rate and the model service time, and it is a
quarter of the run count in the example above.

Both errors come from treating a run as a unit of work rather than as a process with a duration and
an internal rate. `[BP]` The two numbers a capacity model needs per run type are **expected
lifetime** and **operations per run-second per surface**, and both are derivable from the graph at
mint time plus a service-time history.

### 5.4 The tail, and why 70% is not a rounding of 80%

General engineering intuition says to target seventy or eighty percent utilisation and treat the
difference as a matter of taste. On a heavy-tailed service-time distribution it is not.

Queueing delay grows as roughly `1 / (1 - utilisation)` for well-behaved service times — at 80%
utilisation, delay is about five times the service time, which is unpleasant and bounded. When the
service-time distribution has high variance, the multiplier is scaled by that variance, and Chapter
29's six-hour runs mixed with two-minute runs produce variance that is enormous.

The practical consequence is Chapter 23's convoy effect with a number attached: a small number of
very long holds at high utilisation produces queueing delays that are not five times worse than at
low utilisation but tens of times worse, and the system appears to fall off a cliff at a load level
the plan said was fine.

`[BP]` Two responses, and the second is worth more than the first:

- **Target lower utilisation on shared surfaces** — 60% rather than 80% on the model semaphore is a
  reasonable starting point, and the cost is real.
- **Reduce the variance instead.** Chapter 23's latency classes exist for exactly this: separate
  queues for long and short work turns one high-variance distribution into two low-variance ones,
  and each can then run at high utilisation. This is strictly better than buying headroom, and it is
  why Chapter 29 §12 recommended putting long runs in their own class.

### 5.5 Re-measure on every model change

Every number in this chapter derives from measured service times, and the dominant service time —
the model call — changes whenever the model does.

A model upgrade can move step duration substantially in either direction, and it moves other things
with it. A faster model raises the step rate, which raises the arrival rate at every other surface;
the database that needed eleven connections may need eighteen, and the sandbox hosts turn over
faster. A model that reasons longer per call lowers the step rate and raises the hold time, which
changes which surface binds.

`[BP]` Treat a model change as a capacity-invalidating event, in the same way Chapter 38 treats it
as a harness-invalidating event. The re-measurement is cheap — it is a day of running the existing
meter against the new model — and skipping it means every size in the configuration is derived from
a distribution that no longer exists.

### 5.6 Two numbers that do not come from Little's Law

Little's Law sizes steady-state concurrency. Two things it does not size, and both bite:

**Burst headroom.** Little's Law describes averages. A batch job submitting four hundred runs at
09:00 is not an average, and the correct response is Chapter 23's admission control rather than
provisioning for the burst — but admission needs a queue depth, and that is a separate number chosen
from how long a burst may reasonably wait.

**Recovery capacity.** After an outage, every stalled run resumes at once. A fleet sized for
steady-state arrival has no headroom for a thundering resume, and the resume is exactly when the
system is least able to absorb one. `[BP]` Rate-limit resumption after a mass failure — admit
recovered runs through the same admission path as new ones, rather than letting the sweeper release
them all at once. This is one of the few places where a deliberate slowdown prevents a second
outage.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  Scenario: a batch of 400 runs is submitted at 09:00 into a system
  sized for 10 runs/min steady state.

  time   admitted  in flight  model slots  binding surface
  -----  --------  ---------  -----------  ----------------------
  09:00      0         0          0/60     none
  09:00    400 submitted -- admission control (C23) engages
  09:00     10        10          3/60     none
  09:01     20        20          6/60     none
  09:05     50        50         14/60     none
  09:10    100       100         28/60     none
  09:15    150       148         42/60     model semaphore (70%)
  09:18    170       167         52/60     model semaphore (87%)
                                            queue wait p95 climbing
  09:19    ADMISSION THROTTLES: committed load exceeds target
           utilisation on the binding surface (3.1)
  09:19    170       167         57/60     model semaphore (95%)
  09:25    170       160         56/60     model semaphore
  09:40    185       152         55/60     -- steady, throttled
  10:30    260       148         54/60     -- draining
  11:50    400       90          33/60     none
  12:20    400        0           0/60     complete

  TOTAL: 400 runs in 3h20m. The system never exceeded its bound and
  never dropped a run.

  FAILURE BRANCH -- admission does NOT throttle (the common case,
  because admission was built for fairness and not for commitment):

    09:19    400       398        60/60    model semaphore SATURATED
    09:20    every step queues behind the semaphore
             step duration p95: 4 s -> 71 s
             run duration: 24 min -> 4h+
             C29's stall detector fires on runs that are moving,
             because "moving" now takes 71 s per step and the
             novelty window is measured in steps
    09:35    lease renewals start missing their deadlines: the
             renewal thread competes for the same worker pool
             (C32 sec 4.2)
    09:40    leases expire under load. The sweeper returns nodes
             to pending. They are re-claimed and re-queued behind
             the same saturated semaphore.
    -- this is the cliff. Nothing failed; everything queued, and
       the queueing produced a second failure that looks unrelated.

  Figure 33.4 -- A burst, absorbed and not absorbed (D4 Sequence)
```

The failure branch is worth reading twice. Saturation did not produce an error. It produced a
seventeen-fold increase in step duration, which then produced lease expiries, which then produced
re-queuing, which then produced more saturation. Every component behaved correctly at every step.

This is the Level 3 pattern arriving in Level 4: the incident's signature is not an error rate but
a latency distribution, and by the time it is visible as failures it has been compounding for
twenty minutes.

---

## 7. State Management

```
                                                            STATE VIEW

   PER-SURFACE CAPACITY STATE

      {{ headroom }}          utilisation < target
          |
          | utilisation crosses target
          v
      {{ at_target }}         admission throttles new commitments
          |                   (3.1) -- in-flight work is untouched
          |
          | utilisation crosses a hard ceiling
          v
      {{ saturated }}         queue wait grows without bound;
          |                   every OTHER surface's measurements
          |                   are now contaminated
          |
          | sustained saturation
          v
      {{ shedding }}          admission REFUSES rather than queues
                              (C23 sec 5.5: refuse at the door
                              rather than accept and starve)

      Recovery is the same path in reverse, with hysteresis: the
      thresholds for leaving a state are lower than for entering it,
      or the system oscillates between throttling and admitting at
      exactly the boundary.

      ILLEGAL: sizing decisions made from measurements taken in
      {{ saturated }}. Service times measured under saturation
      include queueing delay, so feeding them back into Little's
      Law produces a number that justifies the saturation. This is
      a feedback loop that converges on a permanently overloaded
      system, and it is easy to build by accident.

      ILLEGAL: {{ shedding }} without naming the binding surface.
      Shedding with an unnamed cause produces a capacity discussion
      about workers regardless of which surface was actually full
      (4.2).

  Figure 33.5 -- Capacity states per surface (D6 State Diagram)
```

### 7.1 Measurements taken under saturation are poison

The first illegal transition is subtle and it has ended more than one capacity investigation in the
wrong place.

Service time measured at the client includes queueing. A model call that takes four seconds of
provider time and waits sixty-seven seconds for a semaphore slot measures as seventy-one seconds. Put
seventy-one into Little's Law and it says the system needs seventeen times more capacity than it
does — which, if provisioned, is the cold open in a different resource.

`[BP]` Measure service time and queue time as separate quantities, always. Service time is the hold
itself; queue time is the wait for permission to hold. Only the first belongs in a sizing
calculation, and only the second belongs in a saturation alert.

### 7.2 Capacity state is derived and per-surface

Nothing here is durable. Utilisation is computed from live gauges, the state is recomputed
continuously, and losing all of it costs nothing beyond a moment of blindness. It is per surface
because a system in `headroom` on three surfaces and `saturated` on one is saturated, and a merged
state cannot say which.

---

## 8. Internal APIs

```python
from typing import Protocol
from dataclasses import dataclass


class ServiceTimeMeter(Protocol):

    def record(self, surface: str, hold_ms: float, queue_ms: float) -> None:
        """Record a hold and the wait that preceded it, SEPARATELY.

        Service time is the hold; queue time is the wait for
        permission to hold. Only the first belongs in a sizing
        calculation. Merging them produces a number that grows under
        load and justifies whatever capacity produced the load (7.1).
        """

    def percentiles(self, surface: str) -> "ServiceTime":
        """p50, p95, p99 of the HOLD. Re-measured on every model
        change, because the dominant service time is the model call
        and it moves when the model does (5.5).
        """


class CapacitySizer(Protocol):

    def required(self, surface: str, arrival_rate: float) -> float:
        """Little's Law: arrival rate x service time. One
        multiplication per surface, and there is no shared multiplier
        between surfaces -- inventing one is the cold open.
        """

    def binding_surface(self) -> str | None:
        """WHICH surface is currently the constraint. Not a number --
        a name. Every capacity conversation lacking this one output
        degenerates into adding workers, which makes a saturated
        model semaphore worse (4.2).
        """


class CommitmentEstimator(Protocol):

    def commitment(self, graph: "PlanGraph") -> "SurfaceCommitment":
        """Expected holds per surface over the run's whole lifetime,
        derived from the graph at mint time (C24).

        Admission spends this, not current utilisation. A system at
        40% with two hundred admitted six-hour runs is not at 40%
        (3.1).
        """
```

`ServiceTimeMeter.record` taking two arguments rather than one is the signature carrying §7.1's
argument. A single `duration_ms` parameter is the natural API, it is what every timing library
offers, and it makes the poisonous measurement the default.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceTime:
    surface: str
    p50_ms: float
    p95_ms: float
    p99_ms: float
    measured_at: str
    model_id: str          # the measurement is only valid for this


@dataclass(frozen=True)
class SurfaceCommitment:
    """What admitting this run commits, over its whole lifetime."""
    expected_steps: int
    expected_duration_s: float
    model_calls: int
    db_operations: int
    sandbox_seconds: float


@dataclass(frozen=True)
class CapacityTarget:
    surface: str
    size: int                    # provisioned
    required: float              # Little's Law at current arrival
    target_utilisation: float    # LOWER than intuition on shared,
                                 # heavy-tailed surfaces (5.4)
    hard_ceiling: float          # above this: shed, do not queue
```

`ServiceTime.model_id` is the field that makes §5.5 enforceable rather than aspirational. A
measurement carries the model it was taken against, and a sizer asked to use a measurement whose
model no longer matches the deployed one can refuse — or at minimum warn — instead of silently
producing numbers derived from a distribution that no longer exists.

`target_utilisation` is per surface rather than global. The model semaphore's heavy tail argues for
60%; the database's tiny, tightly-distributed service time is fine at 85%.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Every surface | Service-time meter | In-process, on release | Hold and queue durations, separately |
| Planner / graph | Commitment estimator | At mint time | Node count, critical path, effectful fraction |
| Commitment estimator | Admission (C23) | Synchronous | Expected lifetime commitment |
| Saturation detector | Admission | Gauge | Binding surface, current utilisation |
| Meter | Observability (C34) | Metrics export | Percentiles per surface, tagged with model id |
| Capacity state | Alerting | Gauge | Per-surface state, never merged |

The first row's "separately" is doing the work of a whole section. `[BP]` It is worth enforcing at
the type level (§8) rather than by convention, because every timing helper in every language offers
a one-number API and the one-number API is wrong here.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Pool sized from worker count | Connection refusals; `max_connections` exhausted | Size from measured hold time (§5.1). The cold open |
| Connection held across a model call | Bimodal connection hold-time distribution | Check out per operation, not per step (§5.2) |
| Sizing from measurements taken under saturation | Required capacity growing with provisioned capacity | Separate service time from queue time (§7.1) |
| Adding workers to fix a saturated model semaphore | Throughput flat while worker count rises | Emit `binding_surface` (§4.2) |
| Burst admitted without throttling | Step duration p95 climbing, then lease expiries | Admission against commitment (§3.1); the cliff in §6 |
| Thundering resume after an outage | Second outage minutes after recovery begins | Rate-limit resumption through admission (§5.6) |
| Model change without re-measurement | Every size derived from a stale distribution | `ServiceTime.model_id` mismatch (§9) |
| High-variance queue at high utilisation | Queue wait far worse than utilisation predicts | Latency classes (§5.4) — split the distribution, do not buy headroom |
| Merged per-surface capacity state | Capacity discussions with no named cause | State per surface, never merged (§7.2) |

The fifth row is the one that produces incidents rather than inefficiency, and its signature is
worth memorising: **step duration p95 rising while error rate stays flat.** That is saturation, it
precedes every other symptom by ten to twenty minutes, and it is the earliest actionable signal this
chapter produces.

---

## 12. Scalability

This chapter is about scalability, so this section covers what scales the capacity machinery itself.

**Metering is per hold and must be free.** A histogram observation per release, in process, exported
periodically. `[BP]` Never a network call per measurement — the meter would then have its own
service time and would contend for the resource it measures.

**Commitment estimation is per plan mint and is trivial** — a scan of the graph against a
service-time table, once per run.

**The saturation detector samples gauges every few seconds.** Its cost is constant in run count,
which is what allows it to run continuously rather than on demand.

**The genuinely hard scaling problem is not in this machinery at all — it is the provider limit.**
Every surface here can be bought. The model semaphore is granted, negotiated over weeks, and is the
system's actual ceiling. `[BP]` Plan capacity *around* it: latency classes so long work does not
starve short work, admission so commitment stays under it, and — Chapter 35's territory — reducing
tokens per successful outcome so the same limit yields more work.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Binding surface**, as a gauge with a label. The single most useful output of this chapter, and
  it converts the most common operational argument into a lookup.
- **Service time and queue time, separately, per surface.** Merging them poisons every sizing
  decision downstream (§7.1).
- **Committed load versus provisioned capacity.** Utilisation shows the present; this shows what has
  been promised.
- **Connection hold-time p99 over p50.** A rising ratio is a connection being held across something
  slow, visible long before it causes anything (§5.2).
- **Step duration p95.** The earliest saturation signal, ten to twenty minutes ahead of everything
  else (§11).

### 13.2 The review question

For any capacity number in the configuration: **what measurement is this derived from, and when was
it taken?**

Numbers with no measurement behind them are formulas applied outside their domain, which is the cold
open. Numbers derived from measurements taken before the current model was deployed are derived from
a distribution that no longer exists. Both are common, both look identical to a correct number in a
YAML file, and this question separates them in about thirty seconds.

### 13.3 Teaching this to a new engineer

Ask them to size the database pool for sixty workers. Nearly everyone answers a hundred and twenty
in a few seconds, because the formula is genuinely well known and usually right.

Then ask how long a worker actually holds a connection. Watching someone work out that the answer is
five milliseconds, and then work out what that does to the number, is the whole chapter in ninety
seconds — including the part that matters most, which is that the original answer was not careless.
It was a correct answer to a question about a different system.

---

## 14. Relation to AHE

`[AHE]` Trials are the friendly capacity case: independent, sandboxed, and embarrassingly
parallel. Their capacity question is the plainest in the book — how many concurrent trials — and
Little's Law answers it in one line given a measured trial duration.

`[INF]` What is not plain is that an evolution loop's trials contend with production runs for the
same model semaphore, which is the surface that cannot be bought (§12). A loop running a thousand
trials to evaluate one harness change is consuming exactly the resource that limits the system's
real work, and the trade is invisible unless the trials are admitted through the same admission path
with their own latency class.

`[BP]` Give evolution trials their own work class with reserved-but-preemptible capacity. Reserved,
so a loop cannot be starved indefinitely and stall Level 5 entirely; preemptible, so production work
takes priority during a burst. Chapter 23's class machinery already supports this and it needs no
new mechanism.

`[INF]` There is a containment note here consistent with Chapters 29 and 32. An evolution loop
rewarded on wall-clock throughput will find that raising concurrency limits raises its score, and
§5.4 shows that raising them past the variance-adjusted target degrades a property no benchmark
measures. Concurrency and utilisation targets belong outside the evolvable workspace, for the same
reason temporal parameters do.

---

## 15. Industry Perspective

**`[DAR]`** Worker concurrency exceeding pool size is specified in the base runtime spec, and §5.1's arithmetic is what
turns it from a curiosity into the central sizing fact. The two conditions in §5.2 are the ones that
make it true, and both are easy to break by accident.

**`[BP]` Little's Law is a hundred years old and is under-applied everywhere, not only here.** It
needs one measurement and one multiplication, and it replaces the entire genre of capacity planning
by trial and incident. The barrier is almost never the mathematics; it is that nobody measured the
hold.

**`[BP]` Heavy-tailed service times are well understood in queueing theory and consistently
surprising in practice.** The result that matters — that variance multiplies queueing delay, so a
mixed workload behaves far worse than its average suggests — is the formal statement of Chapter 23's
convoy effect, and the standard fix is the same one: separate the classes.

**`[INF]` Web-derived sizing heuristics are the dominant failure mode in new agent systems.** Every
backend engineer carries `pool = workers * 2` and it has served them well for a decade. It is not
carelessness; it is a correct heuristic meeting a workload whose service-time profile differs by
three orders of magnitude, and the resulting number looks entirely reasonable.

**`[FUT]` Automatic sizing from continuous measurement looks tractable and is rare.** Everything
needed is present: the meter, Little's Law, and the arrival rate. A control loop adjusting pool
sizes and semaphore targets from live percentiles is a small piece of software, and the reason it is
uncommon appears to be that most systems do not separate service time from queue time — without
which the loop's feedback is the poisoned measurement of §7.1 and it converges on overload.

---

## 16. Key Takeaways

1. **One formula cannot size four resources.** A database connection is held for milliseconds and a
   model slot for seconds; their required concurrencies differ by the same factor. The cold open is
   an outage caused by correctly applying a formula from another domain.
2. **Measure the hold, not the operation.** A connection held across a model call has a service time
   of seconds, and the two implementations look nearly identical in code.
3. **A run is a load generator, not a request.** It understates sustained demand and overstates
   instantaneous demand to count runs the way you count requests.
4. **Admission is the only control that bounds committed load.** Everything else bounds the instant
   and can only queue. A system at 40% with two hundred six-hour runs admitted is not at 40%.
5. **Separate service time from queue time, always.** Merged, they grow under load and justify the
   capacity that produced the load — a feedback loop that converges on permanent overload.
6. **The tail changes the utilisation target, and splitting the distribution beats buying
   headroom.** Latency classes turn one high-variance queue into two low-variance ones, each of
   which can run hot.
7. **A model change invalidates every capacity number.** The dominant service time moved, so every
   size derived from it is now derived from a distribution that no longer exists.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Capacity surface** | An independently bounded resource with its own service time, sized from its own measurement and never from a shared multiplier. | `[INF]` | Ch 35, Ch 36 |
| **Service time** | The duration a resource is actually held, excluding the wait for permission to hold it. | `[BP]` | Ch 34, Ch 36 |
| **Queue time** | The wait before a hold begins, which belongs in saturation alerts and never in a sizing calculation. | `[BP]` | Ch 34 |
| **Little's Law sizing** | Required concurrency equals arrival rate times service time, applied once per surface with no shared multiplier. | `[BP]` | Ch 35 |
| **Load generator** | A run seen correctly: not a unit of work served and released, but a process emitting load at its own rate for its whole lifetime. | `[INF]` | Ch 35, Ch 36 |
| **Capacity commitment** | The total future load admitting a run promises, which is what admission should spend rather than current utilisation. | `[INF]` | Ch 36 |
| **Binding surface** | The name — not the number — of whichever resource is currently the constraint, and the output that stops capacity arguments. | `[INF]` | Ch 34 |
| **Saturation poisoning** | Sizing from measurements taken under load, where queueing inflates service time and justifies the overload that produced it. | `[INF]` | Ch 34 |
| **Variance-adjusted utilisation** | A lower utilisation target on heavy-tailed surfaces, or — better — splitting the distribution into latency classes. | `[BP]` | Ch 36 |
| **Capacity invalidation** | Treating a model change as invalidating every derived size, because the dominant service time moved. | `[BP]` | Ch 38 |

---

**Next:** Chapter 34 — *Observability.* This chapter's earliest saturation signal was a latency
percentile that no error rate would have shown. The next one is about that gap in general: why an
agent runtime needs two observability systems that share almost no signals, what eleven of them are,
and the one anomaly that must page a human rather than write a log line.
