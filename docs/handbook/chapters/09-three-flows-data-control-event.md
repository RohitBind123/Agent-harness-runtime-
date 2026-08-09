```
  Level 1 · Chapter 9
  THREE FLOWS: DATA, CONTROL, EVENT
  Requires   C4 The Complete Runtime, C5 The Five Nouns,
             C6 State Separation, C7 The Edge, C8 Lifecycles
  Unlocks    all of Level 2; C22 The Event Spine, C34 Observability,
             C35 Cost Engineering
  Diagrams   Core (5)
```

# Chapter 9 — Three Flows: Data, Control, Event

---

## 1. Motivation

### 1.1 Cold open

Week two. A new engineer on the Atlas team asks what ought to be an easy question: *where does a run
decide what to do next?*

She gets three answers within the hour, from three people who have each worked on it for a year.

The first points at `run_driver.advance()` — forty lines with the state machine in them. The second
says that is misleading and opens the relay: nothing advances until an event is claimed and turned
back into work, so the relay is where "next" is actually decided. The third says both are downstream
of the real answer and opens the context assembler, because what the model is shown determines what
it proposes, and everything after that is bookkeeping.

All three are correct. They are reading one system along three different axes, and none of them said
which.

She does the reasonable thing with three contradictory answers and writes a design document
proposing to consolidate the decision logic in one place. It would braid three currently separable
flows into one. The review thread that kills the proposal runs to sixty comments, and not one of
them manages to say why, because nobody in it has the vocabulary.

### 1.2 In plain language

This chapter does not add anything to the system. It gives you three ways of reading the system you
already have, and a rule for knowing which one a question belongs to.

**Control flow** answers *what happens next, and who decided*. Follow it when you are debugging a
run that went the wrong way, or when you are asking whether some rule is actually enforced.

**Data flow** answers *what moves, and how big is it*. Follow it when something is slow, or when the
bill is larger than expected. The sizes here span five orders of magnitude — a queue message is a
hundred bytes, a context window is a couple of hundred kilobytes, a trajectory is megabytes — and
almost every performance surprise is one of those numbers appearing somewhere you did not expect.

**Event flow** answers *what is written down permanently, and what could be replayed later*. Follow
it when asking what survives a crash, what an audit can prove, or why a bug cannot be reproduced.

The three overlap in places and diverge in others, and the divergences are the useful part. A signal
that cancels a run is control with almost no data. Progress streaming to a browser is data with no
control and deliberately no event. A run that finishes is all three at once.

The failure this prevents is the cold open: three engineers answering the same question correctly
and incompatibly, because they never said which flow they were reading.

### 1.3 Why this chapter exists

Level 1 has built the runtime in space (Chapter 4), in vocabulary (Chapter 5), in ownership
(Chapter 6), at its boundary (Chapter 7), and in time (Chapter 8). This chapter is the synthesis:
the same six layers, read three ways, so that from here on a question can be routed to an axis
before anybody starts answering it.

It also does something specific for the rest of the book. Level 2 opens eleven components in
sequence, and each of them is easiest to understand along one particular flow — the Planner along
control, the Context System along data, the Observation System along event. Naming the three axes
now is what lets those chapters say "read this one along data flow" in four words instead of
rebuilding the frame each time.

### 1.4 What previous framings got wrong

**"Draw the architecture."** There is no such single drawing. `[INF]` A diagram that shows control,
data, and event on the same arrows has three different units on one edge — a decision, a byte count,
and a durability guarantee — and no edge on it can be read with confidence. Appendix C's
one-concern-per-diagram rule is a consequence rather than a style preference.

**"Follow the data."** Excellent advice in a pipeline and misleading here. In a pipeline, data
movement and control transfer are the same act. Here they routinely are not: the largest data
movement in the system (context assembly into a model call) transfers no control at all, and the
most important control transfer (a human resolving a gate) carries almost no data.

**"Events are just how services talk."** Events here are the durability substrate, not a
communication style `[DAR §7.1]`. Chapter 7 already showed what happens when that distinction
collapses: progress written to the event log because it looked like a message, and an events table
fourteen times its former size.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Three maps of one city.

The **road map** shows how you get from anywhere to anywhere: which streets connect, which are
one-way, where the junctions are. Ask it a routing question and it answers immediately. Ask it how
much freight moves through the port and it is silent.

The **freight map** shows tonnage: which corridors carry what volume, where the bottlenecks are,
which route is cheap and which is congested. It is the map you use when something is slow or
expensive, and it looks nothing like the road map even though it describes the same streets.

The **land registry** shows what is on the permanent record: who owns which parcel, which
transactions completed, what a court would accept as having happened. It is not a map of movement at
all. It is the map of what is *true and provable*, and it is the only one you can use to reconstruct
the past.

Nobody would use the land registry to plan a delivery route, or the road map to settle a boundary
dispute. That routing instinct — which map answers this question? — is the entire skill of this
chapter.

**Where the analogy breaks.** A city's three maps describe genuinely separate things: streets,
tonnage, and deeds are different objects. Here they describe *the same lines of code* seen from
different angles. `run_driver.advance()` is a control-flow decision point, a data-flow near-zero
edge, and an event-flow emitter, all at once and in the same forty lines.

That has a practical consequence the analogy would hide: you cannot navigate this system by asking
"which subsystem owns this?", because the answer is often all three of them. You navigate by asking
"which question am I asking?" first, and only then opening a file. The cold open is three engineers
who skipped that step and went straight to a file.

### 2.2 Why three flows, and not one architecture diagram

The count is not a matter of taste. It falls out of what reading a system is for:

```
  1. Reading a system means answering questions about it.
  2. The questions that matter divide by what a WRONG answer costs:
       "what happens next?"      -> wrong = a correctness bug
       "how much moves here?"    -> wrong = a cost or latency incident
       "what survives a crash?"  -> wrong = data loss or an unprovable
                                    audit
  3. Those three have different units: a decision, a byte count, a
     durability guarantee. They are not convertible.
  4. One diagram carrying all three puts three units on every arrow.
     A reader cannot then tell whether a thick arrow means "decides",
     "moves a lot", or "is durable".
  5. So they must be drawn separately. (Appendix C, one concern per
     diagram, is this step.)
  6. And they genuinely diverge, so a single diagram would also be
     WRONG, not merely crowded:
       control without data ..... a cancel signal
       data without control ..... progress streaming to a browser
       event without either ..... an outbox row nobody has claimed
  7. Therefore three is the number of independent questions the
     architecture has to answer, and the number of readings it needs.
```

Step 6 is the one that turns this from a presentation choice into an architectural claim. If the
three always coincided, one diagram would do and the extra vocabulary would be overhead. They do not
coincide, and every place they come apart is somewhere a team has previously built a bug.

### 2.3 The three questions, and where each is answered

| | Control flow | Data flow | Event flow |
|---|---|---|---|
| Answers | what happens next, and who decided | what moves, and how much | what is durable and replayable |
| Unit | a decision | bytes | a committed record |
| Axis | TIME | LAYER | TIME |
| Arrow | `---->` | `====>` | `....>` |
| Read it when | a run went wrong; is this rule enforced? | it is slow; the bill is wrong | what survives a crash? what can we prove? |
| Wrong answer costs | a correctness bug | a cost or latency incident | data loss, or an audit you cannot pass |
| Owned by | the run driver | the context system and the tool engine | the outbox and the relay |
| Level 2 chapter | Ch 10 Planner, Ch 18 Loop | Ch 11 Context, Ch 14 Tools | Ch 16 Observation, Ch 22 Spine |

`[INF]` The last row is the practical payoff. Every Level 2 component has a *primary* flow, and
reading it along that flow first is reliably the fastest way in. Reading the Context System along
control flow, or the Planner along data flow, produces the sensation that a component is
"overcomplicated" — which is almost always a sign of reading along the wrong axis rather than a fact
about the code.

### 2.4 The mental model to carry

> **Route the question to a flow before opening a file. Three correct answers to one question mean
> three people picked three different flows, not that the system is confused.**

The cold open, inverted. The new engineer's question — *where does a run decide what to do next?* —
has no answer until it is refined into one of three:

- *Which component chooses the next step?* → control flow → the run driver, Chapter 18.
- *What information shapes that choice?* → data flow → the context system, Chapter 11.
- *What made this run runnable at this instant?* → event flow → the relay, Chapter 22.

Each of the three engineers answered a different one of those, accurately. The failure was that the
question had not been routed, and the proposed remedy — consolidate the decision logic — would have
destroyed the separability that makes all three answerable at all.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  The same six layers, three readings. Each column is one flow.

  layer          CONTROL             DATA               EVENT
                 who decides         what moves         what is durable
  ------------------------------------------------------------------
  SURFACE        originates a        renders a view     nothing
                 goal; resolves      (small)            (deliberately)
                 a gate
                    |                   ^                   .
                    v                   |                   .
  EDGE           translates only;    read model out;    writes intent
                 decides NOTHING     progress out       to the outbox
                    |                   ^                   |
                    v                   |                   v
  SUBSTRATE      holds no            small rows         [[ outbox ]]
                 decision            in and out         THE durable
                                                        boundary
                    |                   |                   |
                    v                   v                   v
  KERNEL         run driver          dispatches;        relay claims;
                 DECIDES the         holds little       appends facts
                 next step           itself
                    |                   |                   |
                    v                   v                   v
  PORTS          planner proposes;   model port: the     grader emits
                 grader vetoes;      LARGEST movement    a verdict
                 approval blocks     in the system
                    |                   |                   |
                    v                   v                   v
  DOMAIN         obeys commands;     small payloads     emits events
                 decides nothing     in and out         about itself
                 about the run

  Figure 9.1 -- One runtime, three readings (D1 High-Level Architecture)
```

Three observations that only appear when the columns are side by side.

**Control narrows going down; data bulges in the middle.** Decisions concentrate in the kernel and
the ports, while the largest data movement is one layer lower than the largest decision. That
mismatch is why a system can be architecturally clean and financially ruinous at the same time —
they are different columns.

**The edge is empty in the control column.** That is Chapter 7's three rules, restated as a
structural fact rather than a policy. If your edge column has anything in it, you have a loop where
none belongs.

**The domain decides nothing about the run.** It receives commands and emits events; it never
chooses a next step. This is Chapter 4's narrow waist seen from the control axis, and it is the
property that lets one runtime carry a second product.

---

## 4. Low-Level Decomposition: Control Flow

```
                                                             TIME VIEW

  Who decides what happens next, in order, for one step.

   << run.enqueued >> claimed by the relay
            |
            v
   +--------+---------+
   | run driver       |  the ONLY component that advances run state
   +--------+---------+
            |
            v
        /        \
       / budget   \  no    +-------------------------+
      /  remains?  ------->| park: BUDGET_EXHAUSTED  |--X
      \            /       +-------------------------+
       \          /
        \   yes  /
            |
            v
   +--------+---------+
   | planner port     |  PROPOSES a step. Proposes only.
   +--------+---------+
            |
            v
        /        \
       / effect   \  effectful   +----------------------+
      /  tag?      ------------->| gate: approval port  |--||->
      \            /             +----------------------+   |
       \   pure   /                                          | resolved
        \        /                                           | by a human
            |    <---------------------------------------------+
            v
   +--------+---------+
   | activity runner  |  dispatches; does not decide
   +--------+---------+
            |
            v
   +--------+---------+
   | grader port      |  may DOWNGRADE a result, never upgrade it
   +--------+---------+
            |
            v
   +--------+---------+
   | run driver       |  checkpoint; read signals; test exit conditions
   +--------+---------+

  Figure 9.2 -- Who decides what happens next (D8 Control Flow)
```

### 4.1 Four decision points, three of them refusals

The planner is the only component on that path that proposes anything. The budget check, the gate,
and the grader can each stop or downgrade, and none of them can invent an alternative
`[DAR §8.1, §9.2]`.

`[INF]` That asymmetry is worth naming, because it is what makes the control flow auditable: **one
proposer, three vetoes.** A reader tracing a run that did something unexpected has exactly one place
to look for where the idea came from, and three places to look for why nothing stopped it. Systems
with several proposers — a planner, plus a middleware that can inject steps, plus a tool that can
trigger follow-ups — lose that property, and the cost is paid every time somebody asks "why did it
do that?"

### 4.2 Where control does not flow

Equally instructive, and each is a rule from an earlier chapter seen on this axis:

| Non-edge | Why | From |
|---|---|---|
| edge → run driver | the edge decides nothing; it writes intent and returns | Ch 7 §2.5 |
| domain → run driver | the domain obeys commands and emits events; it never picks a step | Ch 4 |
| model → activity runner | a tool call is a *proposal* the runner may refuse | Ch 14 |
| grader → planner | a verdict downgrades a result; it does not author a new plan | Ch 28 |
| sweeper → run state machine | the sweeper releases leases; it never advances a run | Ch 8 §2.4 |

The last row is subtle and worth the space. The sweeper makes a run *runnable* again, which feels
like advancing it. It is not: it expires a lease and re-enqueues, and the next claim runs the same
decision path from the top. The sweeper appears on the event axis, not this one.

---

## 5. The Three Flows

### 5.1 Data flow: what moves, and how much

```
                                                            LAYER VIEW

  goal            client  ====>  edge              ~1-10 KB
  run row         edge    ====>  [[ runs ]]        ~2-20 KB
  queue message   relay   ====>  (( queue ))       ~100 B    identity only

  ASSEMBLED       context ====>  model             ~50-200 KB  <-- the
  CONTEXT                                                         big one

  completion      model   ====>  runner            ~5-50 KB
  tool output     sandbox ====>  runner            ~1 KB - 10 MB
                                                   <-- the variable one
  normalised      runner  ====>  [[ activities ]]  ~1-20 KB after
  result                                            truncation

  trajectory      runner  ====>  [[ trace store ]] ~1-10 MB per run
  progress        kernel  ~~~>   surface           continuous, discarded
  read model      edge    ====>  client            ~5-50 KB per poll

  Figure 9.3 -- What moves, and how much (D7 Data Flow)
```

Five orders of magnitude on one page, and three consequences that follow from the sizes alone.

**The queue carries identity, not payload.** A hundred bytes, established in Chapter 8 §10. This is
what makes re-enqueueing free and therefore makes both drain and the sweeper cheap.

**Context assembly is the cost centre.** `[INF]` The single largest recurring movement is the
context going into the model, and it is paid *per step*, not per run. A run of forty steps pays it
forty times. This is why Chapter 11 treats context as a budgeted resource rather than string
concatenation, and why Chapter 35 can state that the highest-leverage cost optimisation in the
system is almost always upstream of the model call rather than in the choice of model.

**Tool output is the unbounded one.** Everything else on that list has a predictable size. A
`grep` across a large repository does not. Normalisation and truncation at the tool boundary
(Chapter 14) is what stops a ten-megabyte tool result becoming a ten-megabyte context on the very
next step — an amplification that is invisible on the control diagram, because no decision changed.

### 5.2 Event flow: what is durable and replayable

```
                                                             TIME VIEW

  edge                  domain             kernel           consumers
   |                      |                  |                  |
   |.. << run.created >> .......>[[ outbox ]]                   |
   |                      |                  |                  |
   |                      |          relay CLAIMS a row         |
   |                      |          (never a shared cursor)    |
   |                      |                  |.... enqueue .....>|
   |                      |                  |                  |
   |               cmd.repo.apply_patch <----|                  |
   |                      |                  |                  |
   |            state change + event         |                  |
   |            IN ONE TRANSACTION           |                  |
   |                      |...<< repo.patch.applied >>..>[[ outbox ]]
   |                      |                  |                  |
   |                      |          relay claims, run resumes  |
   |                      |                  |                  |
   |.. << approval.decided >> ...>[[ outbox ]]                  |
   |                      |                  |  park resolves   |
   |                      |                  |                  |

  NOT on this diagram, deliberately:
     progress          telemetry; no business meaning; never durable
     context assembly  a projection, rebuilt on demand (Ch 6)
     read models       derived; can be dropped and recomputed

  Figure 9.4 -- What is durable and replayable (D9 Event Flow)
```

The rule that makes this axis work is one line, and it is the whole of Chapter 22 in advance: **a
state change and the event announcing it are written in the same transaction, or the system has a
gap it cannot detect** `[DAR §7.1]`.

`[INF]` The "not on this diagram" block is as important as the diagram. Three things that look like
events are not events, and each was a real design mistake before it was a rule: progress (Chapter 7's
cold open), assembled context (Chapter 6's model-state category), and read models (Chapter 7 §9).
The test for all three is the same — *would a later reader be entitled to rely on this?* Progress
becomes false within a second of being sent, so nobody may rely on it, so it is not a fact.

### 5.3 Where the three diverge

`[INF]` The catalogue, which is the practical core of the chapter:

| Situation | Control | Data | Event | The lesson |
|---|---|---|---|---|
| Cancel signal | **heavy** — changes everything downstream | ~200 B | one durable record | importance is not size |
| Progress to a browser | none | continuous, large in aggregate | **none, by design** | visibility is not importance |
| Context assembly | none | **the largest movement in the system** | none — it is a projection | cost hides where no decision is made |
| Approval granted | **unblocks an effectful step** | ~1 KB | one durable record | the smallest payload with the largest consequence |
| Trajectory capture | none | megabytes | durable but never replayed *into* a run | the evidence corpus of Level 5 |
| Sweeper expiring a lease | none — it advances nothing | a few rows | one record per touched run | recovery is not a decision |
| Tool returning 10 MB | one step's worth | **enormous, and amplifying** | ~20 KB after truncation | truncation is where the axes reconnect |

Row three is the row that costs the most money in practice, and it is invisible on both of the other
axes. Row seven is the one that costs the most incidents: the tool output arrives on the data axis,
and if nothing truncates it, it re-enters the *next* step's context and multiplies.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  One operation -- "apply the patch" -- traced on all three axes.

  t   CONTROL (---->)          DATA (====>)         EVENT (....>)
  --------------------------------------------------------------
  0   relay claims                100 B queue msg    << run.enqueued >>
      run driver wakes                                claimed
  1   driver reads run           ~8 KB row           --
  2   context assembly           ====> 140 KB        -- (projection)
  3   planner proposes            ~2 KB proposal     --
      "apply patch"
  4   effect tag = effectful     --                  --
      --||-> GATE
  5   [ run parks. Nothing held. Hours pass. ]
  6   human approves             ~400 B              << approval.decided >>
      via the edge                                    committed
  7   relay claims, driver       100 B               claimed
      resumes at step 5
  8   activity runner            ====> 12 KB cmd     --
      dispatches
  9   domain applies             ~30 KB diff         << repo.patch.applied >>
      the patch                                       SAME TRANSACTION
  10  grader checks              ~4 KB verdict       << step.graded >>
  11  driver checkpoints         ~3 KB               << run.step.completed >>

  Failure branch at t=9: the domain commits the patch, then the
  process dies before returning.
      CONTROL  nothing advances -- no one is driving
      DATA     nothing moves
      EVENT    << repo.patch.applied >> IS COMMITTED, because it was
               written in the same transaction as the patch.
      Recovery: the relay claims that event and the run resumes at
      t=10. The patch is not applied twice, because the activity
      identity already has a result.

  Figure 9.5 -- One operation on three axes, with a failure branch
                (D4 Sequence)
```

### 6.1 Reading the failure branch three ways

The same instant, three readings, and only one of them is reassuring:

- **Control:** the system is dead. Nothing is deciding anything, and nothing will until a lease
  expires (Chapter 8).
- **Data:** nothing is moving. From a metrics dashboard this is indistinguishable from an idle
  system, which is why Chapter 34 alerts on *absence* of progress rather than on error rates alone.
- **Event:** the fact survived. The patch was applied and the record of it committed atomically, so
  when anything picks the run up again, it resumes with correct knowledge of the world.

`[INF]` That third line is the entire argument for the outbox, stated as an experience rather than a
mechanism. Durability is not a property you observe when things go well. It is the difference
between an incident that costs a lease period and an incident that costs a customer's repository.

### 6.2 The gap at t=5

Between t=4 and t=6, hours pass and all three axes are empty. No decision, no bytes, no records —
one row in a table with a `PARKED` state.

That emptiness is a design achievement rather than an absence. Chapter 5's custody gradient says a
park may hold nothing precisely because it may last arbitrarily long, and Chapter 8 §12.3 turns that
into the claim that the parked population is free. Here you can see the three axes agreeing, which
they rarely do: a park is cheap on *every* reading, and that is what makes "the agent will wait for
your approval as long as you need" an honest product promise rather than an operational liability.

---

## 7. State Management

The three flows touch state differently, and the differences are the whole of Chapter 6 restated on
a new axis:

| Flow | Reads | Writes | Category (Ch 6) |
|---|---|---|---|
| Control | run row, plan, signals | run state via CAS | run state |
| Data | everything, briefly | almost nothing durable | model state — a projection |
| Event | the outbox | the outbox, transactionally | run state and domain state |

`[INF]` The middle row is the one to internalise. **The data flow is almost entirely
non-persistent.** The largest movement in the system — context assembly — writes nothing at all,
because assembled context is model state and model state is rebuilt rather than stored.

That has a consequence for debugging that catches people out: you cannot answer "what did the model
see on step 12?" by querying anything, unless you captured the trajectory deliberately (Chapter 16).
The data flow leaves no trace by default, which is exactly why trajectory capture has to be an
explicit component rather than a side effect of running.

### 7.1 The replay test

`[INF]` A single question that verifies all three axes are correctly separated:

> Delete every read model, every progress message, and every cached context. Can the system
> reconstruct the current state of every run?

If yes, the flows are separated: everything durable lives on the event axis, and the data axis
carries only derivable things. If no, something on the data axis has become authoritative — which is
Chapter 6's model-state rule violated, and it will surface later as a run that cannot be replayed.

This is a test you can run in staging by truncating the read-model tables, and it takes an afternoon
to build. Chapter 40 makes it part of the hermetic replay harness.

---

## 8. Internal APIs

There is no `ThreeFlowsPort`. The flows are a reading of the architecture, not a component in it,
and the honest way to express them in code is as the shapes the existing ports already have:

```python
from typing import Protocol


class ControlEdge(Protocol):
    """Control flow: a decision, returning what happens next.
    Small payloads, high consequence, always synchronous."""

    async def decide(self, run: ClaimedRun, context: Context) -> Decision: ...


class DataEdge(Protocol):
    """Data flow: movement, sized and bounded. Every implementation
    declares a ceiling, because an unbounded one is Ch 14's failure."""

    max_bytes: int

    async def transfer(self, payload: bytes) -> TransferResult: ...


class EventEdge(Protocol):
    """Event flow: durability. The transaction parameter is not
    optional -- an event written outside its state change's transaction
    is the gap of section 5.2."""

    async def append(self, event: Event, txn: Transaction) -> None: ...
```

`[INF]` The signatures encode the chapter. `decide` returns a value and takes no size limit.
`transfer` carries `max_bytes` as a required attribute rather than a parameter, so an unbounded
implementation cannot be written by accident. `append` requires a transaction it does not own,
making it structurally impossible to write an event outside the state change it describes. Chapter
22 implements the third; Chapter 14 the second.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class Flow(StrEnum):
    CONTROL = "control"
    DATA = "data"
    EVENT = "event"


@dataclass(frozen=True)
class FlowAnnotation:
    """Attached to a trace span so a trace can be filtered to one axis.
    The single highest-value thing in this chapter to actually build."""

    flow: Flow
    bytes_moved: int | None      # data spans only
    decided: str | None          # control spans: what was chosen
    durable: bool                # event spans: did it reach the outbox
```

`[INF]` A trace annotated with `flow` can be filtered to one axis, which turns the cold open into a
dashboard query. "Show me only control spans for this run" is the answer to *where does it decide
what to do next*, produced in seconds rather than in an hour of three people disagreeing.

Chapter 34 makes this a required span attribute. It costs one enum on a structure you were already
emitting, and it is the cheapest item in this book relative to what it saves.

---

## 10. Communication

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 11 Context | context assembly as the dominant data movement | the cost argument for budgeting |
| Ch 14 Tools | truncation as where the data axis reconnects to control | unbounded tool output is the amplifier |
| Ch 16 Observation | the data flow leaves no trace by default | why capture must be explicit |
| Ch 22 Event Spine | the same-transaction rule of §5.2 | that chapter is this axis, opened |
| Ch 34 Observability | `FlowAnnotation` on every span | the routing failure becomes a query |
| Ch 35 Cost | cost lives on the data axis, where no decision is visible | why cost work starts upstream of the model |

### 10.2 The routing table

`[INF]` The chapter as a lookup, for the person who has one question and a large codebase:

| The question | Flow | Start at |
|---|---|---|
| Why did it do that? | control | the planner proposal, then the three vetoes |
| Why is it slow? | data | context assembly, then tool output size |
| Why is the bill so high? | data | context assembly per step, not model choice |
| Why can I not reproduce it? | event | what was durable, and what was only a projection |
| What survives a crash here? | event | which transaction the write shared |
| Is this rule actually enforced? | control | is it code on the path, or prose in a prompt? |
| Why did it stop? | control | budget, gate, exit conditions, in that order |
| Where did this number come from? | data | which port produced it, and what it truncated |
| Can we prove this to an auditor? | event | the outbox, and only the outbox |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Wrong-axis reading | a question answered without routing | three plausible contradictory answers | route first — the cold open |
| Braided flows | "consolidating" decision, movement, and durability into one path | no diagram can be drawn without three units on an arrow | keep the three separable; refuse the consolidation |
| Progress on the event axis | durability applied to telemetry | events table growing with viewer count | progress is never durable (Ch 7) |
| Context on the event axis | assembled context persisted as truth | replay produces a transcript, not a replay | context is a projection (Ch 6) |
| Event outside its transaction | append after commit, "for clarity" | state changed with no event, rarely, under load | one transaction, always (Ch 22) |
| Unbounded tool output | no ceiling at the tool boundary | next step's context spikes | truncate at the boundary (Ch 14) |
| Invisible cost | optimising the model choice, not the context | spend per step flat while model price falls | measure per-step context bytes |
| Silent stall | a dead driver | **no** error rate change; data flow goes quiet | alert on absence, not on errors (Ch 34) |
| Multiple proposers | middleware or tools injecting steps | "why did it do that?" has no single answer | one proposer, three vetoes (§4.1) |

`[INF]` The last row is the one worth defending hardest, because the pressure to add a second
proposer is constant and each individual case is reasonable. A middleware that injects a
verification step after a risky edit is a genuinely good idea; it also means the control flow now
has two authors, and every future "why did it do that?" costs twice as much to answer. Chapter 14
resolves this by making such middleware *modify the proposal* rather than *emit its own*, which
preserves the property at no cost to the feature.

---

## 12. Scalability

| Flow | Scales with | The pressure point |
|---|---|---|
| Control | steps per second across all runs | the run driver's write rate to `runs` |
| Data | steps × context size | context assembly; the only super-linear term |
| Event | facts per second, not messages per second | relay claim throughput and outbox growth |

`[INF]` The data row is the one that surprises. Control and event scale roughly linearly with work.
Data does not: as a run gets longer, its context tends to grow, so step *n* costs more than step 1.
A forty-step run does not cost forty times a one-step run — it costs more, and the excess is exactly
what compaction (Chapter 11) exists to bound.

The event row's distinction matters operationally. The outbox carries facts, and facts are produced
by *state changes*, not by observers. Ten thousand people watching one run produce zero additional
events and considerable additional data. Keeping progress off the event axis is what makes the
watching free — Chapter 7's rule, showing up here as a scaling property.

---

## 13. Production Engineering

### 13.1 Instrument the axis, not only the operation

Tag every span with `Flow` (§9). Three dashboards then come almost free, and each answers one of the
three questions:

| Dashboard | Axis | Headline metric |
|---|---|---|
| Decisions | control | steps/sec, veto rate by cause, time-to-first-step |
| Movement | data | bytes per step p50/p99, context size trend over step index |
| Facts | event | outbox lag, relay claim rate, events per run |

"Context size trend over step index" is the one that pays for itself. A line that rises steeply is a
compaction problem visible before it becomes a bill, and it is not derivable from any control or
event metric.

### 13.2 The review question

`[BP]` One question, added to code review, that prevents most of §11:

> Which flow does this change touch, and does it touch any other by accident?

A change to the planner that also enlarges the context touches control *and* data. That is often
fine and always worth saying out loud, because the data consequence is the one that will not appear
in any test and will appear on the invoice.

### 13.3 Teaching this to a new engineer

`[INF]` The cold open costs an hour of three engineers' time plus a doomed design document, and it
recurs with every hire. The cheap fix is a page in the repository README with §10.2's routing table
and Figure 9.1, handed over on day one. The expensive fix is the design review that catches the
consolidation proposal after it has been written.

---

## 14. Relation to AHE

The evolution loop reads all three axes and edits along only one of them.

**It reads control flow** to find where a run went wrong — which proposal was made, which veto did
not fire. That is what an analysis report is `[AHE §3.2]`.

**It reads data flow** to find what the model was shown, because most harness defects are context
defects rather than reasoning defects. `[INF]` This is why the seven component types are weighted
the way Chapter 1's ablation found: tool descriptions and long-term memory both act on the data
axis, and they carried gains where the system prompt alone regressed.

**It reads event flow** because the trajectory store is the evidence corpus. Ten million trace
tokens distilled to ten thousand tokens of evidence `[AHE §3.2]` is a data-axis operation performed
on event-axis material.

**It edits none of the three directly.** The Evolve Agent changes harness components, which change
what flows — it never changes the flow structure itself, because the kernel is outside its
workspace `[AHE §3.3]`. `[INF]` That containment is only meaningful if the three flows are
separable in the first place. A braided architecture has no boundary at which to say "you may edit
what moves, but not who decides", which makes this chapter a quiet prerequisite for Level 5's entire
safety argument.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the outbox and the same-transaction rule, claim-based relay over a shared
cursor, the progress-is-not-a-fact distinction, the pure/effectful tag that puts the gate on the
control path, and the grader's downgrade-never-upgrade contract `[DAR §7.1, §8.1, §9.2]`.

**`[AHE]`** Supplies the evidence-distillation ratio and the component ablation that motivates
reading the data axis first `[AHE §3.2, §4.4.1]`. It does not name three flows; the framing here is
the handbook's.

**`[INF]`** The handbook's own: the three-flow framing and the derivation in §2.2, the divergence
catalogue in §5.3, the one-proposer-three-vetoes property, the routing table in §10.2, the replay
test in §7.1, `FlowAnnotation` as a span attribute, and the argument that flow separability is a
prerequisite for Level 5's containment.

**`[BP]`** Separating control and data planes is standard network and platform architecture, and
Chapter 3's MM5 borrows it directly. The contribution here is adding the event axis as a third
independent reading rather than treating durability as a property of the data plane.

**`[FUT]`** Nothing in this chapter is speculative. Its risk is the opposite of novelty: the three
flows are individually so familiar that teams assume they have already separated them, which is
precisely the assumption the cold open punishes.

---

## 16. Key Takeaways

1. **One system, three readings.** Control answers what happens next, data answers what moves and
   how much, event answers what is durable. They are not three subsystems; they are three questions
   about the same code.
2. **Route the question before opening a file.** Three correct contradictory answers mean three
   people picked three axes silently — not that the system is confused.
3. **The three genuinely diverge.** A cancel signal is control with no data; progress is data with
   no event; context assembly is the largest movement in the system and makes no decision at all.
   Those divergences are where bugs live.
4. **One proposer, three vetoes.** The planner proposes; budget, gate, and grader can only stop or
   downgrade. Adding a second proposer costs you the answer to "why did it do that?" forever.
5. **Cost hides on the axis with no decisions.** Context assembly is paid per step and writes
   nothing durable, so it is invisible on both other readings. Cost work starts upstream of the
   model call.
6. **An event and its state change share one transaction, or the gap is undetectable.** This is the
   single rule that makes the event axis worth having.
7. **Tag every span with its flow.** One enum on a structure you already emit turns the cold open
   into a dashboard query.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Control flow** | The reading that answers what happens next and who decided it; measured in decisions. | `[INF]` | Ch 10, Ch 18 |
| **Data flow** | The reading that answers what moves and how much of it; measured in bytes, and where cost hides. | `[INF]` | Ch 11, Ch 35 |
| **Event flow** | The reading that answers what is durable and replayable; measured in committed records. | `[DAR]` | Ch 22 |
| **Flow routing** | Deciding which of the three axes a question belongs to before trying to answer it. | `[INF]` | every chapter |
| **One proposer, three vetoes** | The property that only the planner proposes a step, while budget, gate, and grader may only stop or downgrade one. | `[INF]` | Ch 14, Ch 30 |
| **Same-transaction rule** | A state change and the event announcing it are committed together, or the gap between them is undetectable. | `[DAR]` | Ch 22 |
| **Projection** | Something derived from durable facts and rebuilt on demand — assembled context, read models, progress. | `[INF]` | Ch 11 |
| **Replay test** | Delete every read model, progress message, and cached context; if run state cannot be reconstructed, an axis has leaked. | `[INF]` | Ch 40 |
| **Flow annotation** | A span attribute recording which axis a trace span belongs to, so a trace can be filtered to one reading. | `[INF]` | Ch 34 |
| **Amplification** | Untruncated output on the data axis re-entering the next step's context and multiplying, with no decision having changed. | `[INF]` | Ch 14 |

---

**Level 1 is complete.** You can draw the runtime, name the units it manipulates, say who owns every
piece of its state, describe its boundary to a client, place any moment in two independent
lifecycles, and route a question to the axis that answers it. Level 2 opens the components one at a
time, and each one is easiest to read along the flow this chapter named for it.

**Next:** Chapter 10 — *The Planner.* The one component permitted to propose a step: how a goal
becomes ordered work, why a replan must mint a new plan id rather than edit the old one, and why
that single decision is what unifies human steering with idempotent replay.
