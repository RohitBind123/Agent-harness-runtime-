```
  Level 1 · Chapter 7
  THE EDGE AND THE CLIENT CONTRACT
  Requires   C4 The Complete Runtime, C5 The Five Nouns, C6 State Separation
  Unlocks    C8 Lifecycles, C9 Three Flows, C30 Human Authority,
             C34 Observability, C37 Tenancy
  Diagrams   Core (5)
```

# Chapter 7 — The Edge and the Client Contract

---

## 1. Motivation

### 1.1 Cold open

Atlas ships a streaming UI and it demos beautifully. You submit an issue, and a panel fills in
real time: the plan appearing step by step, files being read, a patch taking shape, tests running.
Customers love it in the sales call.

The first support ticket arrives on day three. *"The agent stopped working."*

It had not. The customer had opened a run, watched it for four minutes, closed the laptop for a
stand-up, and come back to a blank panel. The stream was server-sent events, fanned out directly
from the worker that happened to be driving the episode. On reconnect the browser opened a new
stream and received the next progress message — which arrived eleven minutes later, because the run
was in the middle of a long test suite. Between reconnect and that message, the interface had
nothing to show and no way to find out anything.

An engineer proposes the obvious fix: write progress to the event log, so a reconnecting client can
replay it. It works in staging. Two weeks later the events table is fourteen times its previous size,
the relay is claiming batches of tokens nobody consumes, the audit export takes nine minutes, and a
golden-set replay has to skip ninety percent of the log to find the four facts that matter.

Both the bug and the fix came from the same missing idea.

### 1.2 In plain language

The edge is the layer a person actually touches: the HTTP API behind the web app, the CLI, the
GitHub integration. Its job sounds trivial — accept a goal, show what is happening — and this
chapter is about why it is not.

Every API you have written before assumed the client is present for the whole job. You ask, you
wait, you get an answer. Here the job runs for six hours. Somebody watches for four minutes, shuts
their laptop, and opens the page again the next morning on a different device, expecting to
understand what happened while they were gone.

That single fact drives everything else. It means what the client sees must be something it can
**ask for**, not only something that gets **pushed** at it. A live stream is a fast path on top of a
queryable state, never a replacement for it — because a stream can only tell you what happened
while you were listening.

The chapter also draws a sharp line between two things that travel in opposite directions.
**Inbound** — goals, approvals, cancellations — must never be lost: a dropped approval stalls a run
forever. **Outbound** — progress updates — can be dropped freely, because the next one supersedes
it. Teams reliably get this backwards, making progress durable because it is the part they can see,
and treating approvals as best-effort because they are rare. Visibility is not importance.

Finally: the edge must contain no loop, no queue consumer, and no model call. The chapter names the
three well-intentioned ways each one sneaks in anyway.

### 1.3 Why this chapter exists

The edge is one row in Chapter 4's layer table and one line in the reference architecture: stateless,
accepts goals, approvals and signals, streams read-models, runs no consumer, no loop, no model call
`[DAR §4.1]`. That is a correct and complete *specification*, and it is not enough to build from,
because it does not mention the property that makes this layer hard.

**The run outlives the connection.** Every API you have written before assumed a client that exists
for the duration of the work. Here the client watches for four minutes of a six-hour run, disconnects,
reconnects on a different device, and expects to understand what happened while it was gone. That one
property changes the contract, and the cold open is what happens when it is not designed for.

This chapter also carries a second job. The edge is the layer where three specific, well-intentioned
mistakes get made, and each one puts a loop in a place that must not have one.

### 1.4 What previous framings got wrong

**"The edge is a thin HTTP layer."** It is thin, and thinness is a rule rather than an observation.
Section 5 gives the three ways it thickens.

**"Streaming is the interface."** Streaming is an optimisation over a queryable state. A system whose
only representation of progress is a stream has no representation of progress, which is the cold
open's first half.

**"Then make progress durable."** The cold open's second half. Progress has no business meaning and
no consumer that needs durability; writing it to the event log bloats the log, the relay, the audit
trail, and the replay path with data that will never be read again `[DAR §7.1]`.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

The reception desk of a workshop that repairs things.

You bring in a broken instrument. The receptionist takes it, writes a ticket, gives you a stub with
a number on it, and puts the instrument on the rack behind them. They do not repair anything. They
have no opinion about how the repair should go. If you ask "how is it coming along?", they look up
the ticket and read you the current status; they do not walk into the workshop and watch.

That is the edge. Goals come in and become durable tickets. Questions come in and are answered from
the record. No work happens at the desk.

Now the two properties that matter. First, the stub in your pocket is the whole contract: you can
come back in three weeks, on a different day, and be told exactly where things stand, because the
*state is queryable from the ticket number*. Second, if the receptionist happens to shout "they've
opened it up!" across the room as you leave, that is a nice courtesy — and losing it costs nothing,
because the ticket still says everything that matters. Shouted updates are progress. The ticket is
the read model.

The failure in the cold open is a workshop that only shouts and never writes tickets. Stand there
and you learn a lot; step outside and you learn nothing, ever again. The failed fix is a workshop
that decides to solve this by *filing every shout in the permanent archive* — which is why the
events table grew fourteenfold.

**Where the analogy breaks.** A receptionist can decide to walk into the workshop and hurry
something along. The edge structurally cannot: no loop, no consumer, no model call. And there is a
sharper difference on the inbound side. If a receptionist loses a message, the customer eventually
follows up. If the edge loses an approval, nothing follows up — the run parks forever, holding
nothing, silently, and §12 explains why that silence is the dangerous part. Inbound intent has to be
durable in a way no reception desk ever needs to be.

### 2.2 Why the edge must be this thin

"Thin" is a rule here, not a description, and every part of it is a defence against a specific
failure:

```
  1. A run outlives any connection, so the client MUST be able to
     reconstruct its view by asking, not only by listening.
  2. Answering "what is happening?" therefore requires only a query
     against durable state -- no work, no waiting, no model call.
  3. So nothing about serving a client requires the edge to run work.
     The remaining question is whether it MAY.
  4. If the edge runs a loop, the run's progress depends on that
     process staying alive -- and an edge process is the one thing in
     the system that gets rolled, scaled, and killed constantly.
  5. If the edge consumes events, a rolling deploy processes some twice
     and drops others, because two versions consume concurrently.
  6. If the edge calls a model, provider latency becomes HTTP latency,
     and the edge can no longer be scaled on request volume.
  7. Each of 4, 5, 6 destroys a property that has no cheap recovery,
     and none of them buys anything step 2 did not already provide.
     Therefore: no loop, no consumer, no model call.
```

The structure of that argument is worth noting. The three rules are not three separate policies to
remember — they are one conclusion, reached because the edge never *needed* to do work in the first
place, and doing it costs a property each time.

### 2.3 The edge is a translator

> **The edge converts human intent into durable facts, and durable facts into a human view. It
> participates in neither direction.**

Everything in this chapter follows from taking that literally. A translator holds no state, makes no
decisions, and — critically — does not do the work it is describing.

### 2.4 The two directions are not symmetric

`[INF]` The single most useful framing for edge design, and the one the cold open got backwards in
both halves.

| | Inbound (intent) | Outbound (view) |
|---|-----------------|-----------------|
| Examples | goals, approvals, signals | progress, run state, step history |
| Must be | durable, idempotent, ordered | fast, disposable, resumable |
| Loss is | **unacceptable** — a lost approval is a stalled run | **fine** — the next update supersedes it |
| Delivery | exactly-once effect, via idempotency key | best-effort, with a queryable fallback |
| Written to | the outbox, in one transaction | nothing; sent directly `[DAR §7.1]` |
| Failure mode | silent non-execution | a blank panel, recoverable by a query |

Teams reliably get this inverted. They make progress durable because it is visible, and approvals
best-effort because they are rare. Both instincts are wrong for the same reason: **visibility is not
importance.**

### 2.5 The three rules, and why each exists

`[DAR §4.2]` states them as a list. Each is a specific defence:

| Rule | Prevents |
|------|----------|
| **No loop** | The process becoming the system; a deploy becoming a data-loss event |
| **No consumer** | Events processed twice or dropped during a rolling deploy |
| **No model call** | Provider latency becoming HTTP latency; the edge unable to scale independently |

The separation between edge and worker is not an optimisation; it is what prevents a slow model call
from ever touching an HTTP request `[DAR §4.2]`.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +~~~~~~~~~~~~~~~~~~~~~~~~ SURFACE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
  |  web app . GitHub app . CLI . Slack . webhook . another agent  |
  +--+--------+---------+------------------------------+-----------+
     |        |         |                              ^
  (1)| goal (2)| approval (3)| signal              (4) | view
     v        v         v                              |
  +===============================================================+
  |  EDGE                                    STATELESS. RUNS NOTHING.
  |                                                               |
  |  +-------------------+   +-------------------+                |
  |  | INTENT HANDLERS   |   | VIEW SERVICE      |                |
  |  | submit . resolve  |   | read model, then  |                |
  |  | signal            |   | subscribe         |                |
  |  +---------+---------+   +---------+---------+                |
  |            |                       ^                          |
  |            | (5) command +         | (7) NOTIFY -> SSE        |
  |            |     event, ONE txn    |     progress fan-out     |
  |            |                       |                          |
  |            |             +---------+---------+                |
  |            |             | (6) QUERY the     |                |
  |            |             |     runtime tables|                |
  |            |             +---------+---------+                |
  +============|=======================|==========================+
               v                       |
  +---------------------------------------------------------------+
  |  SUBSTRATE     [[ commands ]] [[ events ]] [[ runs ]] ...      |
  +---------------------------------------------------------------+
               |                       ^
               v                       |
  +---------------------------------------------------------------+
  |  KERNEL -- runs in a DIFFERENT PROCESS                        |
  |  relay . run driver . activity runner . sweeper               |
  +---------------------------------------------------------------+

  Figure 7.1 -- The edge, both directions (D1 High-Level Architecture)

  (1)(2)(3) inbound intent  -> durable, idempotent
  (4)       outbound view   -> read model first, then live stream
  (5)       one transaction, always
  (6)       a projection, never the raw tables
  (7)       progress: direct to the client, NEVER the outbox
```

Note wires (6) and (7) are separate paths to the same panel. That separation is the fix for the cold
open, and §6 traces it.

---

## 4. Low-Level Architecture

```
                                                            LAYER VIEW

  +===============================================================+
  |  EDGE PROCESS                                                 |
  |                                                               |
  |  INBOUND                                                      |
  |  +---------------------------------------------------------+  |
  |  | auth -> tenancy -> rate limit -> validate -> idempotency|  |
  |  +----------------------------+----------------------------+  |
  |                               |                               |
  |             +-----------------+-----------------+             |
  |             v                 v                 v             |
  |     +-------------+   +-------------+   +-------------+       |
  |     | submit      |   | resolve     |   | signal      |       |
  |     | -> cmd.run  |   | -> approval |   | -> row in   |       |
  |     |    .found   |   |    decision |   |  run_signals|       |
  |     +------+------+   +------+------+   +------+------+       |
  |            |                 |                 |              |
  |            +--------+--------+--------+--------+              |
  |                     v                 v                       |
  |            +-----------------+  +------------------+          |
  |            | COMMAND PORT    |  | NOTIFY channel   |          |
  |            | dedupe on key   |  | wakes a runner   |          |
  |            | replay result   |  | mid-activity     |          |
  |            | tenancy guard   |  +------------------+          |
  |            | freeze check    |                                |
  |            +--------+--------+                                |
  |                     | change + event, ONE transaction         |
  |                     v                                         |
  |  OUTBOUND       [[ substrate ]]                               |
  |  +---------------------------------------------------------+  |
  |  | READ MODEL BUILDER                                      |  |
  |  |   run header . step timeline . cost . park reason       |  |
  |  |   tenancy-scoped . redacted . shaped for a client       |  |
  |  +----------------------------+----------------------------+  |
  |                               |                               |
  |  +----------------------------v----------------------------+  |
  |  | STREAM FAN-OUT                                          |  |
  |  |   LISTEN on a notification channel                      |  |
  |  |   -> server-sent events, per subscriber                 |  |
  |  |   carries a monotonic seq so a client can resume        |  |
  |  +---------------------------------------------------------+  |
  |                                                               |
  |  HOLDS: nothing across a request. No cache of run state.      |
  +===============================================================+

  Figure 7.2 -- Inside the edge (D2 Low-Level Architecture)
```

The inbound chain ends at the command port because that is where deduplication and the cross-cutting
guards belong — tenancy, freeze states, authorisation, and rate limits all sit naturally on one
guarded, idempotent write path `[DAR §7.4]`. The cost is one indirection on every write; the benefit
is that redelivery, which is guaranteed to happen, is safe by construction rather than by the care of
whoever wrote each handler.

---

## 5. The Three Ways a Loop Gets Into the Edge

`[INF]` Each of these has been written by a competent engineer for a defensible reason. Naming them is
most of the defence.

### 5.1 The convenience await

```python
# it starts here, and it is reasonable
async def submit_and_wait(goal: Goal, timeout_s: int = 30) -> Result:
    run_id = await submit(goal)
    return await poll_until_terminal(run_id, timeout_s)   # <-- the loop
```

**The reason.** Some runs finish in twenty seconds, an integration wants one call, and a `202
Accepted` plus polling is more work for the caller.

**What it costs.** The endpoint's latency is now the run's latency, so it inherits every property
Chapter 2 listed. A deploy during the wait drops the caller. A slow provider becomes an HTTP timeout.
And the timeout does not cancel anything — the run continues, so the caller has abandoned work that
is still spending money `[DAR §5.5]`.

**The fix.** Return the run id. If a synchronous shape is genuinely required by a caller you do not
control, put the waiting in a separate gateway process that is allowed to be slow, and keep it out of
the edge.

### 5.2 The synchronous first step

**The reason.** "We want to show the user the plan immediately, so let us call the planner in the
submit handler and return it." Excellent product instinct.

**What it costs.** A model call in the request path — the third rule, broken for the best reason on
the list. It also splits planning across two layers: the edge plans once, the driver plans again on
its first episode, and now two components must agree on plan identity, which Chapter 21 will explain
is the hardest thing to keep consistent in the system.

**The fix.** Submit, then stream. The first progress message arrives in a second or two carrying the
plan, and the user experience is indistinguishable. The plan is produced exactly once, by the
component that owns planning.

### 5.3 The inline consumer

**The reason.** "The relay is thirty lines and we are already deploying this service. Why run a
second deployable?"

**What it costs.** This is the subtlest of the three and the one that produces the strangest bugs.
The edge scales on request volume; the relay must scale on event volume, and those are uncorrelated.
Worse, edge instances are recycled aggressively by load balancers and rolling deploys — so claimed
events are abandoned mid-processing on every release, and until the sweeper reclaims them, that
partition stalls `[DAR §7.2]`. The symptom is duplicated side effects or delayed runs correlating
with deploys, which nobody thinks to correlate.

**The fix.** One process type for intent, one for work `[DAR §4.2]`. In development, run both roles
in one process (Chapter 4 §12.3); in production, never.

---

## 6. Runtime Sequence: The Client Contract

The cold open, done correctly.

```
                                                              TIME VIEW

  client            edge              substrate         kernel
    |                 |                   |                |
 (1)| POST /runs      |                   |                |
    |---------------->|                   |                |
    |                 | idempotency check |                |
    |                 |------------------>|                |
    |                 | cmd + event, 1txn |                |
    |<----------------|                   |                |
    | 202 { run_id }  |                   |                |
    |                 |                   |--------------->|  work
    |                 |                   |                |  begins
 (2)| GET /runs/{id}  |                   |                |
    |---------------->|  QUERY read model |                |
    |                 |------------------>|                |
    |<----------------|                   |                |
    | { state, steps, cost, seq: 14 }     |                |
    |                                     |                |
 (3)| GET /runs/{id}/stream?since=14      |                |
    |---------------->|  LISTEN           |                |
    |                 |<------------------|<---------------|
    |<~~~~~~~~~~~~~~~~|  progress, seq 15, 16, 17 ...      |
    |                 |                   |                |
    X  laptop closes -- stream dies at seq 23              |
    :                 |                   |                |
    :   ... 47 minutes pass. run continues. edge holds     |
    :       nothing. no session, no buffer, no timer.      |
    :                 |                   |                |
 (4)| GET /runs/{id}  |  <-- reconnect: STATE FIRST        |
    |---------------->|------------------>|                |
    |<----------------|                   |                |
    | { state: PARKED, park_reason: approval,              |
    |   steps: [...], cost: 0.87, seq: 61 }                |
    |                 |                   |                |
 (5)| GET /runs/{id}/stream?since=61                       |
    |---------------->|  LISTEN           |                |
    |<~~~~~~~~~~~~~~~~|  live again, no gap                |
    |                 |                   |                |
 (6)| POST /approvals/{ref}  { decision: approve }         |
    |---------------->|                   |                |
    |                 | event appended    |                |
    |                 |------------------>|--------------->|  run
    |                 |                   |                |  resumes

  Figure 7.3 -- Submit, disconnect, resume (D4 Sequence)
```

**The whole fix is step (4): state first, then stream.** The client never depends on having seen every
message. It asks what is true, then subscribes for changes, and the `seq` cursor makes the handoff
seamless. Progress remains disposable; the *view* is reconstructible because it is a query.

`[INF]` This is not a novel pattern — it is how every well-built collaborative editor and dashboard
works, and it is `[BP]` in that sense. What makes it worth a chapter is that agent systems make the
disconnect window enormous. A dashboard's client is away for seconds. Atlas's client is away for
hours, and during the gap the run may have changed state four times, spent a dollar, and parked.

---

## 7. Client Session States

```
                                                             STATE VIEW

              +----------------+
              | DISCONNECTED   |
              +--------+-------+
                       | open a view
                       v
              +----------------+
              | HYDRATING      |   query the read model
              +--------+-------+   (always first, always)
                       | got state + seq
                       v
              +----------------+
              | SUBSCRIBING    |   open stream with ?since=seq
              +--------+-------+
                       |
                       v
              +----------------+
        +---->| LIVE           |<----+
        |     +--------+-------+     |
        |              |             |
        |   stream drops             | caught up
        |              v             |
        |     +----------------+     |
        +-----| RECONNECTING   |-----+
              +--------+-------+
                       | backoff exceeded, or
                       | seq gap too large
                       v
              +----------------+
              | RE-HYDRATING   |   query again, discard the old view
              +----------------+

  Figure 7.4 -- The client's view lifecycle (D6 State Diagram)

  invariant: a client NEVER renders from stream messages alone.
             every LIVE state is preceded by a hydrate.
```

`[INF]` The invariant at the bottom is the client-side half of the contract, and it belongs in your
SDK rather than in each application. A client library that cannot enter `LIVE` without hydrating
makes the cold open structurally impossible — which is the same move as Chapter 1's constraint
hierarchy, applied to your own client code.

**Two parameters worth naming.** The *seq gap threshold* above which a client re-hydrates rather than
replaying, and the *hydrate-on-focus* behaviour for browser tabs. Both are trivial and both are
routinely missing.

---

## 8. Internal APIs

The complete edge surface. Deliberately small.

```python
# --- inbound: intent -------------------------------------------------
POST   /runs                    -> 202 { run_id }
       body: goal, idempotency_key
POST   /runs/{id}/signals       -> 202
       body: kind in {steer, cancel, pause, answer}, payload
POST   /approvals/{ref}         -> 202
       body: decision, signer

# --- outbound: view --------------------------------------------------
GET    /runs/{id}               -> 200 read model, includes `seq`
GET    /runs/{id}/stream?since= -> SSE, progress + state transitions
GET    /runs?state=&tenant=     -> 200 list projection
```

Six endpoints. Notice what is absent, and why:

| Absent | Why |
|--------|-----|
| Anything below the Run | Only Run is addressable from outside (Chapter 5 §8) |
| `PATCH /runs/{id}` | Run state is advanced by the kernel; a client expresses intent via signals |
| A synchronous `submit_and_wait` | §5.1 |
| Raw table access | The read model is a projection; §9 |
| `DELETE /runs/{id}` | Cancellation is a signal, because it must reach a running activity |

That last row is worth pausing on. `[INF]` A DELETE implies removal; cancellation is a *request to
stop* that must propagate to an abort controller inside a live model call `[DAR §5.5]`. Modelling it
as a signal keeps one delivery path for all four kinds and makes the two-second target achievable.

---

## 9. Data Structures: The Read Model

`[DAR §4.1]` says the edge streams read-models and does not define them. This is the handbook's
`[INF]` shape, and Atlas's is:

```python
@dataclass(frozen=True)
class RunView:
    run_id: str
    state: RunState
    seq: int                      # cursor for stream resumption
    goal_summary: str
    plan: list[StepView]          # current plan only; history on request
    park: ParkView | None         # reason, since, who can resolve
    cost: CostView                # spent, reserved, cap
    updated_at: datetime
```

**Three properties are non-negotiable.**

**It is a projection, never the raw tables.** Exposing `runs` directly couples your public contract to
your schema and leaks fields — `lease_owner`, `version`, `attempt_count` — that mean nothing to a
client and everything to an attacker profiling your system.

**It is where tenancy and redaction are enforced.** Chapter 6 established that each state category has
one owner responsible for scoping it. The read model is the enforcement point for run state on the
way out, and the natural home for the redaction rules Chapter 37 specifies.

**It carries `seq`.** Without a cursor the client cannot resume, and §6 collapses.

### 9.1 Build on read, or materialise

| Approach | Query cost | Freshness | When |
|----------|-----------|-----------|------|
| **Build on read** — query the runtime tables per request | 3–5 indexed reads | perfect | default; correct to a few thousand concurrent runs |
| **Materialise** — a projection table updated by a relay consumer | 1 read | eventually consistent | when the read cost appears in your fast-queue latency |

`[INF]` Start with build-on-read. Materialising adds a consumer, a lag, and a class of "my dashboard
disagrees with reality" bug, in exchange for a cost you probably do not have yet. Chapter 34's
fast-queue latency signal is what tells you the trade has become worth making — not a prediction that
it will.

---

## 10. Communication

```
                                                            LAYER VIEW

  INBOUND -- durable, small, rare
  surface ===> edge      goal              ~1 KB       ~10/min
  surface ===> edge      approval          ~200 B      ~2/min
  surface ===> edge      signal            ~500 B      ~1/min
  edge    ===> substrate command + event   ~1 KB       one transaction

  OUTBOUND -- disposable, large, constant
  substrate => edge      read model query  ~5 KB       ~500/min
  kernel   ~~> edge      NOTIFY            ~200 B      ~2000/min
  edge     ~~> surface   SSE progress      ~200 B      ~2000/min

  NEVER
  edge     -X> model     no model call ever runs here
  edge     -X> outbox    progress is not a fact
  kernel   -X> surface   the kernel never talks to a client directly

  Figure 7.5 -- Edge traffic, both directions (D7 Data Flow)
```

`[INF]` The ratio is the design justification. Outbound traffic outnumbers inbound by roughly two
hundred to one, and *none of it is durable*. Had the cold open's fix shipped, that two-thousand-per-
minute stream would have become two thousand rows per minute in the event log — which is exactly the
fourteen-fold growth the team measured.

### 10.1 The edge is on the critical path for human authority

`[INF]` A consequence that is easy to miss. Gate resolutions arrive through the edge as ordinary
events `[DAR §8.2]`. Therefore:

> **If the edge is unavailable, no gate can be resolved, and every run that reaches one parks
> indefinitely.**

No data is lost and nothing is corrupted — parks are durable and patient. But the system quietly
stops being able to do anything irreversible, and the backlog is invisible until the edge returns.
This makes edge availability a *safety-adjacent* property rather than a purely experiential one, and
it belongs in your SLO document with that framing (Chapter 36). Chapter 34's *time parked by gate
type* signal is what surfaces the backlog after the fact.

---

## 11. Failure Modes

| Failure | Symptom | Detection | Recovery |
|---------|---------|-----------|----------|
| Client disconnects | Blank panel; "the agent stopped" | Support tickets, which is too late | Hydrate-then-subscribe (§6) |
| Progress written to the outbox | Log growth, relay churn, slow audit, unusable replay | Event-table growth rate vs run rate | Delete it; progress is not a fact |
| Duplicate submit | Two runs for one intent, double spend | Idempotency-key collision metric | The command port replays the original result `[DAR §4.4]` |
| Loop in the edge | Request latency tracks provider latency | Correlation between p99 latency and model latency | §5.1, §5.2 |
| Consumer in the edge | Duplicated effects or stalls correlating with deploys | Deploy-time anomaly | §5.3 |
| Edge unavailable | Gate backlog; parked runs accumulate | Parked-run count by park reason | Restore; nothing is lost |
| Read model leaks internals | `lease_owner` visible to a customer | Contract test on the response shape | Project, do not expose |
| Stream fan-out overload | Slow SSE, memory growth in edge processes | Open-subscriber count per instance | Cap subscribers per run; shed to polling |
| Seq gap on reconnect | Client renders a stale view | Client-side gap detection | Re-hydrate (§7) |

### 11.1 The failure with no error

`[INF]` "Client disconnects" has no server-side signal at all. Nothing throws, no metric moves, no
alert fires. The run is healthy; the *view* is broken; and the only detection channel is a customer
telling you the product does not work — where they will describe it, reasonably, as the agent being
broken.

This is a general property of the outbound direction and worth stating once for the whole book:
**disposable data has no failure telemetry, so its correctness must be structural.** You cannot
monitor your way out of a bad client contract. You make it impossible in the SDK (§7) and then you do
not have to.

---

## 12. Scalability

| Dimension | Scales by | Bounded by |
|-----------|-----------|-----------|
| Request volume | Stateless replicas behind a load balancer | Trivial |
| Open streams | Subscribers per instance | File descriptors and memory; cap and shed |
| Notification fan-out | One channel per run, or per tenant | The substrate's notification throughput |
| Read model queries | Indexed reads; materialise when measured | §9.1 |

### 12.1 Backpressure belongs at submit

`[INF]` Chapter 4's admission control sits inside the runner, before the model semaphore
`[DAR §5.4]`. That protects the *provider*. It does not protect the *system* from a tenant submitting
four thousand runs, because those runs are cheap to create and will sit in the fast queue competing
for drivers.

Add a second, coarser check at the edge: a per-tenant cap on concurrent non-terminal runs. Over the
cap, the submit is rejected with a retry hint rather than accepted and starved.

Rejecting at submit is kinder than starving at execution, for a reason worth generalising: **a
rejection is legible and a starvation is not.** The caller can see a 429 and act on it; a run that
sits in `CREATED` for two hours looks identical to a broken system.

---

## 13. Production Engineering

### 13.1 Best practices

- **Ship a client SDK that cannot skip hydration.** Structural, not documented. §7.
- **Require an idempotency key on every inbound write** and reject requests without one, rather than
  generating one server-side — a generated key deduplicates nothing.
- **Put tenancy, freeze, authorisation, and rate limiting on the command port,** not in each handler
  `[DAR §7.4]`.
- **Give the read model a contract test** that asserts the *absence* of internal fields, so a schema
  change cannot quietly widen your public surface.
- **Keep the edge deployable independently** and deploy it more often than the worker. It is the layer
  that changes most and risks least.
- **Emit `seq` in every stream message,** even when you think nobody is resuming.

### 13.2 Trade-offs

| Choice | Buys | Costs |
|--------|------|-------|
| Hydrate-then-subscribe | Correct across any disconnect | An extra request per view open |
| Build-on-read model | Perfect freshness, no consumer | Query cost per request |
| Materialised projection | Cheap reads | Lag, and a disagreement class of bug |
| Per-tenant submit cap | Legible backpressure | A tenant can be blocked while capacity exists |
| SSE over WebSocket | Simpler, proxy-friendly, auto-reconnect | One direction only, which is all that is needed here |

`[INF]` The last row is worth a sentence, since it is a real decision. The edge's outbound path is
strictly one-way and disposable; inbound intent goes through ordinary durable requests. A duplex
channel would tempt someone to send a signal over it, which would bypass the command port and its
guards. Choosing the less capable transport is the point.

### 13.3 Anti-patterns

| Anti-pattern | Why it fails | Diagnosed in |
|--------------|-------------|--------------|
| **Stream-only progress** | No view survives a disconnect; the cold open | §6 |
| **Durable progress** | Bloats log, relay, audit, and replay | §10 |
| **The convenience await** | Run latency becomes request latency | §5.1 |
| **The synchronous first step** | A model call in the request path; planning split across layers | §5.2 |
| **The inline consumer** | Deploy-correlated stalls and duplicates | §5.3 |
| **Raw table exposure** | Public contract coupled to schema; internals leaked | §9 |
| **Cancel as DELETE** | Cannot reach an abort controller inside a live call | §8 |
| **Server-generated idempotency keys** | Deduplicates nothing | §13.1 |

---

## 14. Relation to AHE

The edge is the layer the published loop does not have, and its absence explains two things that
otherwise look like gaps in the source.

**AHE's runs have no client.** Rollouts are dispatched by a harness, executed to completion or
timeout, and scored `[AHE App. A]`. There is no view, no reconnect, no progress, and no human waiting
— so none of this chapter's machinery is required, and the source is right not to build it.

**Nor do they have approvals.** Chapter 5 §14 noted that AHE has no Park; the reason is visible here.
A gate is resolved by a human acting through an edge, and with no edge there is no way to resolve one,
so gates cannot exist. The two absences are one absence.

`[INF]` **What this means for a reader taking Level 5 into production.** Adding an edge to an
evolvable agent changes the loop's measurement in a way the source never had to consider: **a run's
wall-clock duration now includes human latency, and human latency is not a property of the harness.**
If an evolved component causes more gates to be raised, task duration rises and pass rates within a
timeout fall — and the loop will attribute that to the component, correctly in one sense and
misleadingly in another. Chapter 47 needs to separate machine time from parked time before
attributing anything, and Chapter 5's accounting — three minutes of worker time inside six hours of
wall clock — is exactly the measurement that makes the separation possible.

**One thing the edge gives the loop for free.** Every goal, signal, and approval decision is a durable
row with a timestamp and a signer. Chapter 44's evidence corpus can therefore include *human*
behaviour — which gates were slow, which were always approved, which were reversed — a signal class
the published loop has no access to. Chapter 49 argues that an approval that is always granted is a
gate that should be removed, and this is where the data to prove it comes from.

---

## 15. Industry Perspective

### Supported by the attached Durable Runtime architecture `[DAR]`

- The edge as stateless: accepts goals, approvals, and signals; streams read-models; runs no consumer,
  no loop, no model call (§4.1, §4.2).
- The edge/worker separation as a correctness requirement rather than an optimisation (§4.2).
- Progress fanned out over a notification channel to server-sent events (Figure 1).
- A goal may be raised by anything: a person, a schedule, a webhook, another agent (§4.4).
- The edge writing a command through the port, with a duplicate key replaying the prior result
  (§4.4).
- The state change and its event appended in one transaction (§4.4).
- Progress sent straight to the client and never written to the outbox, because it is not a fact
  (§4.4, §7.1).
- The command port deduplicating on an idempotency key and serving as the natural home for tenancy,
  freeze states, authorisation, and rate limits (§7.4).
- Gate resolution arriving as an ordinary event that flows through the relay (§8.2).
- Signals as steer, cancel, pause, and answer, with mid-activity delivery by notification and a
  two-second target from click to the call stopping (§8.3).
- Admission control sitting before the model semaphore in the runner (§5.4).
- A timeout that only abandons the caller leaking the operation (§5.5).

### Supported by the attached AHE paper `[AHE]`

- Rollouts dispatched by a harness and executed to completion or timeout, with no client and no human
  in the loop (App. A).

### Engineering inference `[INF]`

- The inbound/outbound asymmetry table, and the claim that teams reliably invert it because
  visibility is mistaken for importance.
- Hydrate-then-subscribe as the client contract, with `seq` as the handoff cursor, and the client
  session state machine.
- The claim that an SDK which cannot enter a live state without hydrating makes the failure
  structurally impossible.
- The three specific ways a loop enters the edge, their reasons, costs, and fixes.
- The `RunView` shape, and the read model as the enforcement point for tenancy and redaction.
- Build-on-read as the default, with materialisation triggered by a measured fast-queue latency.
- Edge availability as a safety-adjacent property because gate resolution flows through it.
- Disposable data having no failure telemetry, so its correctness must be structural.
- Per-tenant submit caps as legible backpressure, and the claim that rejection is kinder than
  starvation.
- Choosing a one-way transport deliberately so that signals cannot bypass the command port.
- The observation that adding an edge introduces human latency into a metric the evolution loop
  attributes to the harness.
- Human decision records as a signal class available to an evidence corpus only once an edge exists.

### Industry best practice `[BP]`

- Hydrate-then-subscribe is standard in collaborative editors and live dashboards; what is specific
  here is the scale of the disconnect window.
- Server-sent events with a resumption cursor, and exponential backoff on reconnect.
- Contract tests asserting the absence of internal fields in a public response.
- Per-tenant quotas returning a retry hint rather than silently queueing.

### Future proposal `[FUT]`

- None in this chapter.

---

## 16. Key Takeaways

1. **The edge translates and does not participate.** No loop, no consumer, no model call — three rules,
   three specific defences.
2. **The two directions are asymmetric.** Inbound intent must be durable and idempotent; outbound view
   must be fast and disposable. Teams invert this because visibility looks like importance.
3. **The run outlives the connection.** This is the property that makes the edge hard and that no
   ordinary API has.
4. **State first, then stream.** Hydrate from a read model, subscribe with a cursor. A client that can
   never render from stream messages alone cannot produce the cold open.
5. **Making progress durable is the wrong fix.** It bloats the log, the relay, the audit trail, and
   the replay path with data nobody reads.
6. **Three loops try to get in.** The convenience await, the synchronous first step, and the inline
   consumer. Each was written for a good reason.
7. **The edge is on the human-authority critical path.** If it is down, no gate resolves and every
   irreversible action stops. That belongs in your SLO with that framing.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Read model** | A view of a run assembled by the edge for a client, built from durable facts and never authoritative itself. | `[INF]` | Ch 9, Ch 34 |
| **Progress** | Telemetry with no business meaning, streamed straight to a client and never written to the outbox. The opposite of a fact. | `[DAR]` | Ch 34 |
| **Fact** | Something durable that a later reader is entitled to rely on; the thing progress is deliberately not. | `[DAR]` | Ch 22 |
| **Signal** | Out-of-band control over a live run: steer, cancel, pause, or answer. | `[DAR]` | Ch 30 |
| **Steer** | A goal amendment delivered mid-run that forces a replan instead of editing the running plan. | `[DAR]` | Ch 10, Ch 30 |
| **Hydrate-then-subscribe** | Load current state by query first, then attach a stream with a cursor — the contract that survives a disconnect. | `[INF]` | Ch 9 |
| **Cursor (client)** | The position a client resumes a stream from, so a reconnect neither repeats nor skips. | `[INF]` | Ch 9 |
| **Stateless ingress** | An edge that keeps nothing in process memory, so any instance can serve any request and a deploy loses nothing. | `[DAR]` | Ch 33 |
| **Human authority** | The requirement that certain irreversible actions wait for a person, which makes the edge availability-critical. | `[DAR]` | Ch 30 |

---

**Next:** Chapter 8 — *Request Lifecycle and Runtime Lifecycle.* Two lifecycles that are routinely
confused: the life of a goal, and the life of the runtime itself — including the deploy, the drain,
and why recovery must never be a boot-time activity.
