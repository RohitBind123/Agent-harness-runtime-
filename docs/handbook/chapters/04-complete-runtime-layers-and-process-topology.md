```
  Level 1 · Chapter 4
  THE COMPLETE RUNTIME: LAYERS AND PROCESS TOPOLOGY
  Requires   C0-C3 (all of Level 0)
  Unlocks    C5 Five Nouns, C6 State Separation, C7 The Edge,
             C8 Lifecycles, C9 Three Flows — and every chapter after
  Diagrams   Full (9)
```

# Chapter 4 — The Complete Runtime: Layers and Process Topology

---

## 1. Motivation

### 1.1 Cold open

3:14am. A customer's run has been stuck for ninety minutes. The on-call engineer opens the
dashboard, sees the run in `EXECUTING`, and needs to answer one question before doing anything else:
**is it stuck in our runtime or in our product?**

She cannot tell. The function she is staring at reads the run row, asks the planner for a next step,
writes a row into Atlas's `patches` table, dispatches a tool call, and updates the run's step
pointer — all in one place, all in one transaction. There is no boundary to point at. Every
hypothesis she forms requires reading code in a different concern to eliminate.

She finds it at 7:20. A lock taken on Atlas's `repositories` table, for reasons that made sense
eight months earlier, is held across a model call. The pool is not exhausted; one row is contended.
Four hours, for a defect that would have been visible in ninety seconds if the layers had been
separable enough to bisect.

### 1.2 In plain language

So far the book has argued that a system has to be built around the model. This chapter is the
first one that draws it.

The drawing has six horizontal bands. At the top is the **surface** — the app or terminal a person
actually looks at. Below it the **edge**, a thin layer that accepts goals and hands back progress
and does no thinking of its own. Below that the **kernel**, the small generic engine that actually
drives work forward. Below that the **ports**, which are the plug sockets where your specific
behaviour gets attached: how to plan, which tools exist, which model to call, how to grade, who
approves. Then the **domain**, which is your product — for Atlas, everything about repositories and
patches. Underneath everything, the **substrate**: the database and queues that make the whole thing
survive a restart.

The single most important idea is the one in the middle. The runtime and the product talk to each
other through a deliberately tiny opening: the runtime sends **commands** down ("apply this patch")
and the product sends **events** back up ("the patch was applied"). Nothing else crosses. They share
no tables and neither imports the other's code.

The test for whether you got it right is blunt: delete the runtime entirely, and your product should
still make sense on its own. If it does not, the two have grown together, and every guarantee later
in this book becomes unenforceable — because there is no longer a boundary at which to enforce it.

### 1.3 Why this chapter exists

There is a second cost, quieter and larger. Three weeks after that incident, someone asks whether
the runtime could carry a second product — a support agent, sharing none of Atlas's domain. The
answer is no, and the reason is the same as the 3am reason: the runtime knows what a repository is.
Extracting it is a quarter's work.

Both costs come from one absent property. This chapter installs it: **six layers, and a narrow waist
between the runtime and your product across which exactly two kinds of message travel.** Get this
right and the runtime becomes replaceable, testable, and reusable across products `[DAR §2.2]`. Get
it wrong and every guarantee in the rest of the book becomes unenforceable, because there is no
boundary at which to enforce it.

This is the map chapter. Every remaining chapter zooms into one region of Figure 4.1.

### 1.4 What previous framings got wrong

**"Layers are bureaucracy."** Layers are a debugging affordance. The cold open is a bisection failure:
without boundaries there is nothing to bisect.

**"We'll extract the framework later."** Extraction is a rewrite, because the coupling is not in the
imports — it is in the transactions. A single transaction spanning runtime and domain state cannot be
split without redesigning both sides.

**"More layers, more indirection, more latency."** The layer count is not the cost; the *crossings*
are, and this design has few. A step crosses the waist at most twice. `[INF]` What costs latency in
practice is holding scarce resources across slow operations, which is a custody question (MM5), not a
layering one.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A shipping port.

Ships arrive carrying anything at all — grain, cars, refrigerators, chemicals. The port handles none
of that variety directly. It handles **containers**: one standard box, one standard way to lift it,
one standard way to stack it. The crane operator does not know or care what is inside. That single
constraint is what lets one port serve every industry, and what lets a container move from ship to
train to lorry without anybody unpacking it.

The runtime is the port and your product is the cargo. The kernel lifts containers: it starts runs,
drives steps, dispatches tool calls, and never once needs to know what a repository is. Commands and
events are the containers — two standard shapes, and the only things permitted across the dock.

The layers fall out of the same picture. The **edge** is the gate where lorries are checked in and
turned around quickly, so a slow crane never blocks the entrance. The **substrate** is the yard where
containers sit safely if everyone goes home. The **ports** — the naming overlap is unfortunate and
worth noticing — are the specialised handling equipment you bolt on for your particular cargo.

**Where the analogy breaks.** A shipping container is opaque and the port genuinely never opens it.
The runtime is not quite that pure: it must know whether a command is *reversible*, because an
irreversible one requires a human gate before it may be sent (Chapter 30). So the container is
opaque as to contents but not as to consequence — every command carries one bit the runtime is
entitled to read. That bit is the whole safety model, and it is the one place the analogy would
otherwise lead you to build something unsafe.

### 2.2 Why the waist must be narrow

"Narrow waist" sounds like an aesthetic preference. It is the load-bearing decision of the chapter,
and it is forced by the two costs in the cold open:

```
  1. The runtime must be debuggable by bisection: given a stuck run,
     you must be able to say "runtime" or "product" before reading
     any code.
  2. Bisection requires a boundary that can be observed and tested
     independently on each side.
  3. A boundary is only observable if EVERYTHING crossing it is
     enumerable. If the two sides also share a database table, the
     shared table is an unobservable second channel, and bisection
     fails.
  4. Therefore state must not be shared: the only crossings are
     messages.
  5. Two directions are needed and sufficient. The runtime must ask the
     product to change something (a command, going down), and the
     product must report that something changed (an event, going up).
  6. Anything richer -- the runtime calling arbitrary product functions,
     or the product reaching into run state -- reintroduces the
     unenumerable channel from step 3.
  7. Therefore: commands down, events up, no shared tables, no imports
     either way. Two message kinds is the smallest interface that is
     still sufficient.
```

Step 3 is the one teams skip. Sharing one table "just between the runtime and the domain" feels
harmless and destroys the property, because the coupling that matters is not in the imports — it is
in the transactions, as §1.4 notes. A single transaction spanning both sides cannot be split later
without redesigning both.

### 2.3 The narrow waist

Six layers, and one boundary that matters more than the other five.

> **Between the runtime and your product, exactly two kinds of message cross: Commands flow down,
> Events flow up. Nothing else.**

A Command is a request to change something, imperative, carrying an idempotency key. An Event is a
statement that something has happened, past tense, immutable, appended in the same transaction as the
change it describes `[DAR §3.2]`.

That is the whole interface. No shared tables, no foreign keys, no imports in either direction. The
runtime's tables and your domain's tables are joined by nothing `[DAR §11]`, and that absence is a
feature you must actively defend, because every convenient shortcut in the next two years will
propose adding one join.

### 2.4 The test

`[DAR §3.3]` gives it, and it is the sharpest tool in the chapter:

> **If you cannot delete the entire runtime and still have a coherent product, the two have merged.**

Not "would be inconvenient to delete." Deleted. Your domain tables still make sense, your invariants
still hold, your product still compiles. If a `current_step` column on a domain aggregate goes
dangling, you have failed the test, and the guarantees in Chapter 13 are now unenforceable.

### 2.5 Two of the six are already yours

A framing that lowers the perceived cost of all this. Of the six layers, **two already exist in your
system** — the surface and your domain. **One you buy** — the substrate. **One you do not write at
all** — the kernel, which is generic. Only two are new work, and one of those is an interface
exercise.

| Layer | Status |
|-------|--------|
| Surface | you already have it |
| Edge | mostly new, and thin |
| Kernel | generic; write once, or replace with an engine later |
| Ports | new, but they are interfaces over code you already have |
| Domain | you already have it |
| Substrate | off the shelf |

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +------------------------------------------------------------------+
  |  SURFACE                                          written by YOU  |
  |  chat . IDE . inbox . dashboard . CLI . webhook . another agent   |
  +----------------------------------+-------------------------------+
                                     | (1) goals, approvals, signals
  +----------------------------------v-------------------------------+
  |  EDGE                                             written by YOU  |
  |  stateless. accepts intent, streams read-models.                  |
  |  runs NO consumer, NO loop, NO model call.                        |
  +----------------------------------+-------------------------------+
                                     | (2) commands + events
  +----------------------------------v-------------------------------+
  |  SUBSTRATE                                        OFF THE SHELF   |
  |  one transactional database . one queue . nothing else            |
  +----------------------------------+-------------------------------+
                                     | (3) claimed events
  +----------------------------------v-------------------------------+
  |  KERNEL                              THE PART YOU DO NOT WRITE    |
  |  relay . run driver . activity runner . sweeper . queues          |
  +----------------------------------+-------------------------------+
                                     | (4) plan, tool, model, grade, ask
  +==================================v===============================+
  |  PORTS                                            written by YOU  |
  |  planner . tool . model . grader . approval . domain              |
  +==================================+===============================+
                                     | (5) commands
  +----------------------------------v-------------------------------+
  |  DOMAIN                                           written by YOU  |
  |  aggregates . invariants . your tables                            |
  |  knows NOTHING about the runtime                                  |
  +----------------------------------+-------------------------------+
                                     | (6) truth + event, one transaction
                                     +--> back to SUBSTRATE, closing
                                          the cycle at (3)

  Figure 4.1 -- The six layers (D1 High-Level Architecture)
```

Two things to read out of this before anything else.

**The domain sits at the bottom and knows nothing.** It receives commands, enforces its own
invariants, writes its own tables, emits events, and imports nothing from the runtime `[DAR §10]`.
That is what makes the cold open's second cost — the failed reuse — impossible by construction.

**The cycle closes.** A goal becomes a command, the command's event becomes motion, motion becomes a
tool call, the tool call becomes a fact, and the fact re-enters at the top `[DAR §4.3]`. There is no
terminating branch and no outer loop in code; the loop is the data.

---

## 4. Low-Level Architecture: The Kernel Opened

```
                                                            LAYER VIEW

  +==================================================================+
  |  KERNEL                                                          |
  |                                                                  |
  |  +--------------------+          ((  FAST QUEUE  ))              |
  |  | RELAY              |   (a)    decisions, projections,         |
  |  | claims, never a    |--------> grader checks                   |
  |  | cursor             |          concurrency 8-16                |
  |  | FOR UPDATE         |               |                          |
  |  |   SKIP LOCKED      |   (b)         | (c)                      |
  |  | one in flight      |--------> ((  SLOW QUEUE  ))              |
  |  |   per partition    |          tool and model activities       |
  |  | N workers,         |          model semaphore 4-6             |
  |  |   no coordination  |               |                          |
  |  +--------------------+               |                          |
  |            ^                          |                          |
  |            |                +---------+---------+                |
  |            |                v                   v                |
  |            |     +--------------------+  +--------------------+  |
  |            |     | RUN DRIVER         |  | ACTIVITY RUNNER    |  |
  |            |     | the episode        |  | the quarantine     |  |
  |            |     |                    |  |                    |  |
  |            |     | lease + version    |  | claim by id        |  |
  |            |     |   CAS              |  | reserve budget     |  |
  |            |     | advance N steps    |  | acquire a slot     |  |
  |            |     | checkpoint each    |  | run, settle,       |  |
  |            |     | holds NO connection|  |   append result    |  |
  |            |     |   between steps    |  | abortable          |  |
  |            |     | exits on: clock,   |  | idempotent:        |  |
  |            |     |   steps, park,     |  |   a finished       |  |
  |            |     |   signal           |  |   activity replays |  |
  |            |     +---------+----------+  +---------+----------+  |
  |            |               |                       |             |
  |            |               +-----------+-----------+             |
  |            |                           | (d) results, facts      |
  |            +---------------------------+                         |
  |                                                                  |
  |  +--------------------+                                          |
  |  | SWEEPER            |   a cron, not a subsystem                |
  |  | expired run leases |   runs continuously, NEVER only at boot  |
  |  | expired activity   |                                          |
  |  |   leases           |                                          |
  |  | expired relay      |                                          |
  |  |   claims           |                                          |
  |  | attempt cap ->     |                                          |
  |  |   dead letter      |                                          |
  |  +--------------------+                                          |
  +==================================================================+

  Figure 4.2 -- Inside the kernel (D2 Low-Level Architecture)

  (a) fast-class events   (b) slow-class events
  (c) dispatch            (d) append to the outbox, re-entering at the relay
```

Four components, one of which is a cron job. That is the entire kernel, and its smallness is the
point: `[DAR §4.1]` describes it as the part you do not write, because nothing in it is specific to
any product.

---

## 5. Internal Components

```
                                                            LAYER VIEW

              +---------------------------------------------+
              |                  KERNEL                     |
              +---------------------------------------------+
                     |            |            |
      claims events  |            |            |  expires leases
                     v            v            v
        +------------+--+  +------+-------+  +-+------------+
        | RELAY         |  | RUN DRIVER   |  | SWEEPER      |
        +------+--------+  +------+-------+  +------+-------+
               |                  |                 |
               |    dispatches    |                 |
               |     activities   v                 |
               |          +-------+--------+        |
               |          | ACTIVITY RUNNER|        |
               |          +-------+--------+        |
               |                  |                 |
    +----------+------------------+-----------------+----------+
    |                    reads and writes                      |
    v                                                          v
  [[ events ]] [[ runs ]] [[ run_steps ]] [[ activities ]]
  [[ commands ]] [[ run_signals ]] [[ budget_ledger ]] [[ approvals ]]

           run driver calls              activity runner calls
                  |                              |
      +-----------+-----------+       +----------+----------+
      v           v           v       v          v          v
  +===+====+ +====+===+ +=====+==+ +==+====+ +===+====+ +===+====+
  |planner | | grader | |approval| | tool  | | model  | | domain |
  +========+ +========+ +========+ +=======+ +========+ +========+
      fast class, cheap, frequent      slow class, paid, rate-limited

  Figure 4.3 -- Component interfaces (D3 Component Diagram)
```

| Component | Owns | Calls | Never |
|-----------|------|-------|-------|
| **Relay** | Turning appended events into queued work | the queues | interprets an event's meaning |
| **Run driver** | Advancing one run through an episode | planner, grader, approval | makes a model call directly |
| **Activity runner** | One leased, budgeted, abortable tool invocation | tool, model, domain | decides what to do next |
| **Sweeper** | Reconciling expired leases and stale claims | nothing | runs only at boot |

`[INF]` The "Never" column is the useful one. Each entry is a real temptation with a real cost. A
relay that interprets events becomes a second run driver. A driver that calls a model directly
re-couples the planes. A runner that decides the next step turns the planner into decoration. A
sweeper that runs at boot never notices the run stranded four hours in `[DAR §6.3]`.

---

## 6. Runtime Sequence: The Wire Reference

Follow the numbers once and you have the system.

```
                                                              TIME VIEW

  surface   edge      substrate   kernel    ports     domain
    |         |           |          |        |         |
 (1)|-------->|           |          |        |         |    goal arrives
    |      (2)|---------->|          |        |         |    command written
    |         |        (3)|          |        |         |    change + event,
    |         |           |          |        |         |    ONE transaction
    |         |        (4)|<---------|        |         |    relay claims
    |         |           |       (5)|        |         |    routed by class
    |         |           |       (6)|        |         |    driver takes
    |         |           |          |        |         |    lease, runs
    |         |           |          |        |         |    an episode
    |         |           |       (7)|        |         |    step needs a
    |         |           |          |        |         |    tool -> enqueue
    |         |           |          |        |         |    activity;
    |         |           |          |        |         |    driver does NOT
    |         |           |          |        |         |    wait
    |         |           |       (8)|        |         |    runner claims on
    |         |           |          |        |         |    the slow queue
    |         |           |       (9)|------->|         |    planner, grader
    |         |           |          |        |         |    (fast class)
    |         |           |      (10)|------->|         |    tool -> model;
    |         |           |          |        |         |    abort reaches
    |         |           |          |        |         |    all the way down
    |         |           |      (11)|--------|-------->|    effectful step
    |         |           |          |        |         |    issues a command
    |         |           |          |        |         |    -- ONLY after its
    |         |           |          |        |         |    gate resolved
    |         |        (12)<---------|--------|---------|    domain writes
    |         |           |          |        |         |    truth + event
    |         |           |          |        |         |    closes at (4)
    |         |           |          |        |         |
 (B)|<--------|           |          |        |         |    progress
 (A)|-------->|-----------|--------->|        |         |    signals
    |         |           |      (C) |        |         |    sweeper, always

  Figure 4.4 -- The complete wiring (D4 Sequence)
```

| # | What happens |
|---|-------------|
| 1 | A goal arrives. Anything may raise one: a person, a schedule, a webhook, another agent. |
| 2 | The edge writes a command through the port. A duplicate key replays the prior result rather than acting twice. |
| 3 | The state change and its event are appended in one transaction — the transactional outbox. |
| 4 | The relay claims a batch of events, one in flight per partition. No cursor exists, so no cursor can drift. |
| 5 | Events are routed by latency class. Cheap decisions and slow tool calls never share a queue. |
| 6 | A run driver wakes, takes the lease, reads state, and runs an episode. |
| 7 | A step needing a tool is enqueued as an activity. The driver does not wait; it checkpoints and lets go. |
| 8 | The activity runner picks it up on the slow queue, under a model semaphore and a per-tenant cap. |
| 9 | The driver calls your planner and your grader. Both are cheap and run on the fast queue. |
| 10 | The runner calls your tool, which calls your model. The abort signal reaches all the way down. |
| 11 | An effectful step issues a command — and only after its gate has been resolved. |
| 12 | Your domain writes truth and appends its event. The cycle closes at wire 4. |
| A | Signals: steer, cancel, pause, answer. Read at every checkpoint; delivered mid-activity by notification. |
| B | Progress: telemetry sent straight to the client. Never written to the outbox — it is not a fact. |
| C | Recovery: expired leases and claims are swept continuously, never only at boot. |

Condensed from `[DAR §4.4]`.

**Wire 7 is the one to internalise.** The driver dispatches and lets go. It does not await the
activity, does not hold a connection, and does not stay resident. That single decision is what makes
worker concurrency independent of pool size, and it is the custody rule (MM5) expressed as a wire.

---

## 7. State Management

### 7.1 The run state machine

`[INF]` The reference architecture describes these behaviours without drawing a machine. This is the
handbook's construction, consistent with `[DAR §4.4]` and `[DAR §14]`.

```
                                                             STATE VIEW

                          +-----------+
                          | CREATED   |
                          +-----+-----+
                                |  goal accepted
                                v
                          +-----------+
              +---------->| PLANNING  |<-----------+
              |           +-----+-----+            |
              |                 |  plan committed  | replan
              |                 v                  |
              |           +-----------+            |
              |     +---->| EXECUTING |------------+
              |     |     +--+-----+--+
              |     |        |     |
              |     |        |     | step dispatched
              |     |        |     v
              |     |        |  +--------------------+
              |     |        |  | AWAITING_ACTIVITY  |
              |     |        |  +---------+----------+
              |     |        |            | result appended
              |     |        |<-----------+
              |     |        |
              |     |        | gate required, budget exhausted,
              |     |        | input needed, timer set
              |     |        v
              |     |  +-----------+
              |     +--| PARKED    |  holds NO resource; may last weeks
              |        +-----+-----+
              |              | cancel signal
              |              v
              |        +-----------+   +-----------+   +-----------+
              +------->| SUCCEEDED |   | FAILED    |   | CANCELLED |
                       +-----------+   +-----+-----+   +-----------+
                                             |
                                             | attempt cap reached
                                             v
                                    +-----------------+
                                    | DEAD_LETTERED   |
                                    +-----------------+

  Figure 4.5 -- Run states (D6 State Diagram)

  Illegal transitions, enforced in code:
    * -> EXECUTING without a committed plan
    PARKED -> EXECUTING without a resolution event
    any terminal state -> any other state
```

### 7.2 State by layer

| Layer | Holds | Survives a restart |
|-------|-------|-------------------|
| Surface | Client-side view state | Irrelevant |
| Edge | **Nothing.** Stateless by rule | N/A |
| Kernel | Nothing in process; everything in the substrate | Yes, because it is not in the process |
| Ports | Nothing between calls | N/A |
| Domain | Your product's truth | Yes, independently of the runtime |
| Substrate | All of it | Yes |

The two "Nothing" rows are the design. `[DAR §13]` states the invariant behind them: state is a row,
and a worker is a temporary reader of it.

---

## 8. Internal APIs

Layer crossings, as contracts. Full signatures in Appendix E.

| Crossing | Direction | Contract | Rule |
|----------|-----------|----------|------|
| Surface → Edge | down | `submit`, `resolve`, `signal` | HTTP-shaped, returns immediately |
| Edge → Substrate | down | command write + event append | one transaction, idempotency key required |
| Substrate → Kernel | up | claimed event batch | one in flight per partition |
| Kernel → Ports | down | the six port protocols | fast class: planner, grader, approval; slow class: tool, model |
| Ports → Domain | down | `execute(command, tx)` | returns result and events, both written in one transaction |
| Domain → Substrate | up | event append | same transaction as the change |
| Kernel → Surface | up | progress stream | never durable |

**Two rules that are not negotiable.** The kernel imports nothing from the domain. The domain imports
nothing from the runtime `[DAR §10]`. Everything else in this table is a convention; those two are
the narrow waist, and Chapter 40 makes them a build-time check rather than a review comment.

---

## 9. Data Structures

The eight tables, grouped by what they serve `[DAR §11]`.

| Group | Tables | Purpose |
|-------|--------|---------|
| Messaging spine | `events`, `commands` | The outbox, and the deduplicating write port |
| Run execution | `runs`, `run_steps`, `activities`, `budget_ledger` | What is in flight, what the plan is, what has run, what it cost |
| Control | `run_signals`, `approvals` | Out-of-band human input, and gate decisions |
| **Your domain** | **not shown, not constrained, not joined** | Reachable only through commands and events |

Chapter 11 gives columns and indexes; Appendix D gives the schema.

---

## 10. Communication: The Three Flows

The same wiring, read three ways. Chapter 9 develops this as a discipline; here it is a first pass.

### 10.1 Data flow — what moves, and how much

```
                                                            LAYER VIEW

  goal            surface ===> edge                      ~1 KB
  command         edge    ===> substrate                 ~1 KB
  event           domain  ===> substrate                 ~1 KB
  run state       substrate <==> driver                  ~10 KB per checkpoint
  ASSEMBLED       context  ===> model                    ~50-200 KB   <-- the
  CONTEXT                                                              big one
  completion      model   ===> runner                    ~5-50 KB
  tool output     sandbox ===> runner                    ~1 KB - 10 MB <-- the
                                                                      variable
  trajectory      runner  ===> trace store               ~1-10 MB per run
  progress        kernel  ~~~> surface                   continuous, discarded

  Figure 4.6 -- Data flow (D7)
```

`[INF]` Two rows dominate and both live below the waist. Assembled context is paid on *every* model
call, which is why Chapter 11 treats context as a budget rather than a string. Tool output is the
unbounded one — a single command can return ten megabytes and destroy a context window, which is why
truncation belongs in the tool implementation (Chapter 15) rather than in the prompt.

### 10.2 Control flow — who decides what happens next

```
                                                              TIME VIEW

     goal
      |
      v
   / has a plan? \--no--> PLANNER decides the steps
   \             /
      | yes
      v
   / signals pending? \--yes--> SIGNAL wins; steer forces a replan
   \                  /
      | no
      v
   / next step type? \
   \                 /
      +-- decision --> DRIVER decides, in-process, cheap
      |
      +-- activity --> / effectful? \--yes--> GATE decides (a human)
                       \            /
                            | no
                            v
                         RUNNER executes, then
                         GRADER decides accept / retry / replan / escalate
                            |
                            v
                         PLANNER decides continue / replan / gate / done

  Figure 4.7 -- Control flow (D8)
```

The decision authority is distributed across five actors, and exactly one of them is the model. That
distribution is the safety model: the model proposes, the grader checks, the gate authorises, the
planner routes, the driver enforces.

### 10.3 Event flow — what is durable

```
                                                              TIME VIEW

  << run.founded >>          appended by the edge's command
        |
        v
  << run.plan.committed >>   appended by the driver after planning
        |
        v
  << activity.completed >>   appended by the runner, with cost
        |
        +----> << run.step.completed >>
        |
        v
  << approval.requested >>   appended when a gate is reached
        |
        :  ... park, arbitrary duration ...
        v
  << approval.decided >>     appended by the edge on the human's action
        |
        v
  << repo.branch.pushed >>   appended by the DOMAIN, in the same
        |                    transaction as the push record
        v
  << run.succeeded >>        terminal

  NOT events, deliberately:
    partial model output . token counts mid-stream . heartbeats .
    "the agent is thinking" . retry attempts that changed nothing

  Figure 4.8 -- Event flow (D9)
```

The exclusion list is as important as the inclusion list. Progress updates, partial output, and
streaming tokens have no business meaning and no consumer that needs durability; writing them to the
event log bloats the log, the relay, the audit trail, and the replay path with data that will never
be read again `[DAR §7.1]`.

---

## 11. Failure Modes

### 11.1 Layer violations and their symptoms

`[INF]` This table is the chapter's practical payload. Each violation is invisible in code review and
loud in production.

| Violation | Symptom | Detected by |
|-----------|---------|-------------|
| Run state on a domain aggregate | Deleting the runtime leaves dangling columns; replay disagrees with truth | The §2.2 test, run as a CI check |
| Domain logic in the kernel | The runtime cannot serve a second product | An import-graph rule in CI |
| Model call at the edge | HTTP timeouts correlate with provider latency; the edge cannot be scaled independently | Latency correlation; a lint rule on edge modules |
| Consumer running in the edge process | Events processed twice, or dropped, during a deploy | Duplicate side effects after rollout |
| Port importing from the kernel | The port cannot be unit-tested in isolation | Test setup that requires a database |
| Kernel holding a domain lock | The 3am cold open: one contended row, not an exhausted pool | Lock-wait metrics by table |
| Two transactions where there should be one | An event exists with no corresponding change, or the reverse | Reconciliation job; a count mismatch |

### 11.2 Process-level failures

| Failure | Detected by | Recovery |
|---------|-------------|----------|
| Worker killed mid-episode | Run lease expiry | Sweeper clears it; the next relay wake re-drives from the last checkpoint |
| Worker killed mid-activity | Activity lease expiry | Re-claimable; identity ensures a replay rather than a re-spend |
| Relay worker dies holding claims | Claim timestamp older than threshold | The sweeper releases them for re-claim |
| Two drivers race one run | Version check returns zero rows | The loser drops its job; no compensation needed |
| Edge process dies | Load balancer health check | Stateless; another instance serves. No work is affected |

Condensed from `[DAR §14]`. The last row is the reward for the edge being stateless: an entire layer
whose failure mode is "nothing happens."

---

## 12. Scalability

### 12.1 The worker loop

```
                                                              TIME VIEW

  WORKER PROCESS -- one loop, four roles

  loop forever:
      |
      +--> RELAY:      claim a batch of pending events
      |                FOR UPDATE SKIP LOCKED, one per partition
      |                route each to fast or slow queue
      |
      +--> DRIVER:     pull from the fast queue
      |                lease + CAS a run
      |                run an episode:
      |                    advance a step        (no connection held)
      |                    checkpoint            (~5ms: CAS, renew, release)
      |                    read pending signals  (same transaction, free)
      |                    test exit conditions
      |                exit on: E1 wall clock . E2 step budget
      |                         E3 durable park . E4 signal arrived
      |                final checkpoint, release lease, re-enqueue if
      |                not terminal
      |
      +--> RUNNER:     pull from the slow queue
      |                claim by id, reserve budget, acquire a slot
      |                run the tool, settle, append the result event
      |
      +--> SWEEPER:    expire run leases, activity leases, relay claims
                       dead-letter anything past its attempt cap

  Figure 4.9 -- The worker loop (D5 Runtime Loop)
```

The four exit conditions are from `[DAR §5.1]`; Chapter 18 develops the episode properly.

### 12.2 Scaling each layer

| Layer | Scales by | Coordination needed | Ceiling |
|-------|-----------|--------------------|---------|
| Surface | Whatever you already do | — | — |
| Edge | Stateless replicas | None | Load balancer |
| Kernel — relay | More workers | **None** — the claim is the coordination `[DAR §7.2]` | Substrate write throughput |
| Kernel — driver | More workers | Lease + version CAS | Fast-class throughput |
| Kernel — runner | More workers | Model semaphore, per-tenant admission | Provider limits |
| Kernel — sweeper | More workers | None; claims are atomic | Negligible |
| Ports | With their callers | — | Whatever they wrap |
| Domain | However it already scales | — | Yours |
| Substrate | Vertically, then partition | — | The real ceiling |

### 12.3 Process topology in practice

`[INF]` The reference architecture specifies two process *types* `[DAR §4.2]`. How many process
*instances* is a deployment decision the source leaves open. A working progression for Atlas:

| Stage | Topology | When |
|-------|----------|------|
| Development | One process running edge and all four kernel roles | Always; it must work this way or your tests are slow |
| Small production | Edge replicas + worker replicas, each worker running all four roles | Up to roughly a hundred concurrent runs |
| Isolated slow work | As above, plus a dedicated pool running only the runner role | When model calls start delaying driver wakes |
| Fully separated | One deployable per role | When you can point at a metric that requires it — not before |

The progression exists because each split adds an operational surface, and `[DAR §4.2]` is explicit
that the separation between edge and worker is the one that is *not* an optimisation: it is what
prevents a slow model call from ever touching an HTTP request. Every other split is an optimisation
and should wait for evidence.

---

## 13. Production Engineering

### 13.1 Best practices

- **Enforce the waist in CI, not in review.** An import-graph rule and the delete-the-runtime test.
  Both are cheap; both catch the violations that are invisible to a reader.
- **Give every layer a directory and never cross-import.** Boring, and it makes the 3am bisection
  possible.
- **Keep the edge boring.** No consumer, no loop, no model call `[DAR §4.2]`. If someone needs to add
  one, they need a different layer.
- **Number your wires.** Figure 4.4's numbering is not decorative — during an incident, "we are stuck
  between 7 and 8" is a complete diagnosis.
- **Run all four kernel roles in one process in development.** If that is painful, the roles are
  coupled in a way that will hurt later.

### 13.2 Trade-offs

| Choice | Buys | Costs |
|--------|------|-------|
| Narrow waist (commands and events only) | Replaceable runtime; independently testable domain | One indirection on every write |
| Kernel as generic code | Reuse across products; a clean replacement path to an engine `[DAR §17]` | It cannot use domain knowledge to optimise |
| Stateless edge | Trivial scaling; failure mode is "nothing happens" | Progress must be streamed, not polled from memory |
| Four roles in one process | Simple operations, simple local development | One noisy role can starve another before you split |

### 13.3 Anti-patterns

| Anti-pattern | Why it fails | Diagnosed in |
|--------------|-------------|--------------|
| **The convenient join** | One foreign key from a runtime table to a domain table, and the runtime is no longer removable | §2.2 |
| **The loop in the handler** | The process becomes the system; a deploy becomes a data-loss event | Ch 2 |
| **The god function** | Planning, dispatch, and domain writes in one place; the cold open | §1.1 |
| **Premature process splitting** | Four deployables before a hundred concurrent runs; operational surface with no benefit | §12.3 |
| **Progress in the outbox** | Bloats log, relay, audit trail, and replay path | §10.3 |
| **Boot-only recovery** | The run stranded four hours in is never noticed | §11.2 |

---

## 14. Relation to AHE

Evolution operates on the **ports layer and nothing else**, and this chapter is what makes that
sentence enforceable.

Map AHE's seven editable component types onto Figure 4.1 and every one of them lands in the same
band: the system prompt, tool descriptions, tool implementations, middleware, skills, sub-agent
configurations, and long-term memory are all either ports or the assembly around them
`[AHE §3.1]`. None of them is kernel. None is domain. That is not a coincidence — it is why the loop
can edit them without the runtime's guarantees changing underneath it.

The controllability constraint follows the same lines. AHE's evolution agent writes only inside the
harness workspace, with the runs directory, tracer, verifier, and model configuration read-only
`[AHE §3.3]`, which in this chapter's vocabulary reads: **the evolution loop may write to the ports
layer, may read the substrate, and may not touch the kernel or the edge.**

`[INF]` Two consequences worth stating now.

**The waist protects the experiment.** Because the domain is reachable only through commands, an
evolved tool cannot reach around the runtime to write directly to Atlas's tables — so an edit cannot
accidentally gain capability that the measured configuration did not have. Without the waist, an
evolution loop's action space is the whole codebase and its results are uninterpretable.

**The layer diagram is the action-space diagram.** Chapter 43 will draw the editable surface, and it
is Figure 4.1 with one band highlighted. If you cannot draw your layers, you cannot bound your
evolution loop, which is one more reason this chapter comes forty chapters before that one.

---

## 15. Industry Perspective

### Supported by the attached Durable Runtime architecture `[DAR]`

- The six layers, their responsibilities, and who writes each (§4.1).
- Two process types, with the edge/worker separation being a correctness requirement rather than an
  optimisation; the edge runs no consumer, no loop, no model call (§4.2).
- The closed cycle: goal to command, command's event to motion, motion to tool call, tool call to
  fact, fact re-entering at the top (§4.3).
- The complete wire reference, wires 1 through 12 plus side channels A, B, and C (§4.4).
- Commands flow down carrying an idempotency key; events flow up appended in the same transaction as
  the change (§3.2).
- The narrow waist making the runtime replaceable, testable, and reusable (§2.2).
- The structural test: deleting the runtime must leave a coherent product (§3.3).
- Run state as a row and a worker as a temporary reader of it (§13).
- Claim-based relay with no cursor; N workers with zero coordination (§7.2).
- Progress excluded from the outbox because it is not a fact (§7.1).
- The four episode exit conditions (§5.1).
- Continuous sweeping rather than boot-only recovery (§6.3).
- The eight tables, and domain tables joined to them by nothing (§11).
- Fast and slow work classes with their concurrency ranges (§5.4).
- The failure catalogue condensed in §11.2 (§14).
- Replacing the run driver with a durable-execution engine behind the same interface (§17).

### Supported by the attached AHE paper `[AHE]`

- Seven editable component types exposed as files at fixed mount points (§3.1).
- Controllability: workspace-only writes, with runs, tracer, verifier, and model configuration
  read-only (§3.3).

### Engineering inference `[INF]`

- The run state machine of Figure 4.5, including the illegal-transition list. The source describes
  the behaviours; the machine is the handbook's construction.
- The "Never" column of the component table in §5.
- The layer-violation table in §11.1 and its detection methods.
- The data-flow volume annotations in §10.1 and the claim that assembled context and tool output are
  the dominant rows.
- The four-stage process topology progression in §12.3.
- The claim that the waist protects the evolution experiment by bounding the action space, and that
  the layer diagram is the action-space diagram.
- Numbering wires as an incident-communication practice.

### Industry best practice `[BP]`

- Import-graph enforcement in CI as a layering guard.
- Stateless edge processes behind a load balancer with health checks.
- Running all roles in one process during development to keep the local loop fast.

### Future proposal `[FUT]`

- None in this chapter.

---

## 16. Key Takeaways

1. **Six layers, and only two are new work.** Surface and domain you already have; the substrate you
   buy; the kernel is generic. The edge and the ports are the work.
2. **The narrow waist is the whole design.** Commands down, events up, nothing else crosses. No
   shared tables, no imports either way.
3. **The test is deletion.** If removing the runtime leaves an incoherent product, the layers have
   merged and every later guarantee is unenforceable.
4. **The kernel is four components, one of which is a cron job.** Relay, run driver, activity runner,
   sweeper. Its smallness is why you can replace it later.
5. **Wire 7 is the custody rule as a wire.** The driver dispatches and lets go, which is why worker
   concurrency is independent of pool size.
6. **The edge/worker split is not an optimisation.** It is what keeps a slow model call away from an
   HTTP request. Every other process split should wait for a metric.
7. **The layer diagram is the action-space diagram.** Forty chapters early, this is what will bound
   the evolution loop.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Surface** | The app, terminal, or chat window a person actually looks at. Outside the runtime entirely. | `[DAR]` | Ch 7 |
| **Edge** | A thin stateless layer that accepts goals and streams progress, and deliberately runs no loop, no consumer, and no model call. | `[DAR]` | Ch 7 |
| **Kernel** | The small generic engine that drives work forward — relay, run driver, activity runner, sweeper — and knows nothing about any product. | `[DAR]` | Ch 18 |
| **Port** | One of six plug sockets where product-specific behaviour attaches: planner, tool, model, grader, approval, domain. | `[DAR]` | Ch 10-14 |
| **Domain** | Your product's own logic and tables, which must remain coherent with the runtime deleted. | `[DAR]` | Ch 6 |
| **Substrate** | The durable storage and queues everything else rests on; usually bought rather than built. | `[DAR]` | Ch 22 |
| **Narrow waist** | The deliberately tiny opening between runtime and domain: commands down, events up, nothing else. | `[DAR]` | Ch 6, Ch 22 |
| **Command** | An instruction sent down into the domain asking it to change something, carrying an idempotency key. | `[DAR]` | Ch 22 |
| **Event** | A past-tense statement travelling up that something happened, written in the same transaction as the change itself. | `[DAR]` | Ch 22 |
| **Deletion test** | Delete the runtime; if the product no longer makes sense on its own, the layers have merged. | `[DAR]` | Ch 6 |
| **Run driver** | The kernel component that advances one run, replacing the banned word "orchestrator". | `[DAR]` | Ch 18 |
| **Activity runner** | The kernel component that dispatches a tool call, then releases its resources rather than waiting on them. | `[DAR]` | Ch 14, Ch 21 |
| **Relay** | The kernel component that picks up appended events and turns them back into work. | `[DAR]` | Ch 22 |
| **Sweeper** | The recurring job that expires stale leases and dead-letters exhausted work; the only cron in the kernel. | `[DAR]` | Ch 27 |

---

**Next:** Chapter 5 — *The Five Nouns: Run, Episode, Step, Activity, Park.* We name the units the
whole architecture manipulates, give each a lifetime, and explain why "the agent" is not among them.
