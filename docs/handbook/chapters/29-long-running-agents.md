```
  Level 3 · Chapter 29
  LONG-RUNNING AGENTS
  Requires   C8 Request and Runtime Lifecycles, C11 The Context System,
             C21 Durable Execution, C24 The Task Graph,
             C26 Planning Algorithms
  Unlocks    C33 Scalability, C35 Cost Engineering,
             C36 Reliability and SLOs
  Diagrams   Core (5)
```

# Chapter 29 — Long-Running Agents

---

## 1. Motivation

### 1.1 Cold open

Atlas is migrating `reporting-service` from one web framework to another. It is a large job — the
team estimated two days of human work — and the run is expected to take six hours.

At hour four everything is healthy. No errors. No timeouts. The step budget is 500 and the run is at
340. Token spend is tracking within forecast. The dashboard shows a steady rise in completed steps
and every operational signal is green.

What the run has actually been doing since hour two is this: run the suite, observe three failures
in `test_report_export.py`, edit `exporters.py` to fix them, run the suite, observe the same three
failures, edit `exporters.py` back towards its previous form, run the suite. It has been oscillating
between two workspace states for a hundred and ninety steps.

Every one of those steps succeeded. Every tool returned cleanly. Every contract that existed
evaluated true, because the contracts were about steps and each step did what it said. The step
counter went up, which is what a step counter does.

Someone notices at 04:50 and kills it. Two hours of wall clock, a hundred and ninety steps, and
about a hundred and eighty dollars, all spent going back and forth between two states the system had
already visited.

Nothing failed. That is the whole problem: for two hours there was nothing to detect, because
progress was never something the system had a definition of.

### 1.2 In plain language

Most of what earlier chapters described assumes a run that takes minutes. When a run takes hours,
three things change, and the third is the one that costs money.

**Budgets stop being safety nets and start being plans.** In a short run you set a generous cap and
never reach it. In a six-hour run the cap is the binding constraint, and something has to decide how
to spend it — because spending it all in the first ninety minutes is a real and common way to fail.

**The connection goes away.** Nobody holds an HTTP request open for six hours. The run has to
survive without a caller attached, be resumable, and be able to answer "how is it going" to someone
who arrives later and was never there for the start.

**And the run can stop making progress without anything going wrong.** This is the expensive one. A
short run that gets stuck hits its cap in ninety seconds and nobody notices. A six-hour run that
gets stuck burns four hours looking completely healthy, because the only thing being counted is
steps, and going in circles produces steps at exactly the same rate as doing useful work.

So the chapter needs an actual definition of progress — something mechanical, something the system
can compute — rather than a proxy that happens to correlate with it on short tasks.

### 1.3 Why this chapter exists

Chapter 8 separated the request lifecycle from the run lifecycle and noted that they diverge.
Long-running work is where the divergence becomes the design rather than a detail: the request is
gone within seconds and the run continues for hours, so every affordance that used to come from
having a caller present — cancellation, progress, the answer to "is this working?" — has to be
rebuilt as durable state.

`[AHE Limitations]` names a second reason, and it is the sharper one. Timeouts and step budgets
tuned against a benchmark of short tasks become part of the harness, and they encode the length of
the tasks they were tuned on. A harness that scores well on ten-minute problems and fails on
six-hour ones may have no capability gap at all — it may have a hyperparameter fitted to the
evaluation distribution. That is a generalisation hazard, it is invisible in the benchmark that
created it, and it is the most likely reason a system that works in evaluation does not work on real
work.

### 1.4 What previous framings got wrong

**"A long run is a short run with a bigger budget."** Scaling the number changes which failures
dominate. Short runs fail by erroring; long runs fail by not finishing, and those need different
detection entirely.

**"Step count is progress."** It is a count of attempts. The cold open produced a hundred and ninety
steps of progress-shaped nothing, and any system that draws a progress bar from a step counter will
draw a confident one.

**"Timeouts are operational tuning."** They are behavioural parameters. A step timeout tells the run
how long it is permitted to think a thing is worth, and a run that has learned everything finishes
in ten minutes will abandon things at ten minutes.

**"Progress reporting is a UI concern."** Progress is an input to admission, to scheduling, and to
the decision to stop. Building it for a dashboard produces something that looks right and cannot be
acted on, which is the cold open's dashboard exactly.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Budgeting a long run is fuel planning for a long-haul flight. You do not take off with "enough
fuel". You take off with a computed quantity: trip fuel, contingency, an alternate, a final reserve,
and a defined point of no return past which diverting is no longer an option. The discipline is
allocation, not sufficiency, and every part of it is decided before departure.

That shape transfers whole. A six-hour run needs its budget divided by phase, needs a reserve it may
not spend on ordinary work, needs the compensation reserve of Chapter 27 §5.2 held back like an
alternate, and benefits enormously from a defined point past which finishing beats starting anything
new.

Now the part that does not transfer, and it is not a small caveat.

A flight has **ground speed**. Fuel burn maps to distance covered, the map is known, and at any
moment the crew can say how far along they are with high confidence. Consumption and progress are
tightly coupled, and that coupling is what makes the whole discipline work.

A run has no ground speed. Tokens burn at a rate that is completely uncoupled from distance covered.
The cold open burned a hundred and eighty dollars of fuel while stationary, and there is no
instrument that reports zero — because the instrument everyone has is the one counting fuel, and it
was working correctly.

So the analogy supplies the allocation discipline and withholds the single measurement that makes it
meaningful. **Building that measurement is the substance of this chapter**, and everything about
budgets is downstream of having it.

### 2.2 Why progress must be defined mechanically

```
  (1) Short run: the budget is a safety cap. Set it generously,
      never reach it, and nothing further is required.

  (2) Long run: the cap becomes the binding constraint. Something
      must decide how to spend it, because spending it all early
      is a real way to fail.

  (3) Try spending uniformly. It fails: exploration steps are
      cheap, integration steps are expensive, and a uniform
      allocation starves whichever phase costs most -- which is
      always the last one.

  (4) So allocate by phase. But phases come from the plan, and
      the plan changes under repair (C26 sec 5.3).

  (5) So allocation must be re-derivable from what remains rather
      than fixed at the start -- budget tracked against remaining
      work, not against elapsed time.

  (6) Which requires knowing how much work remains. And "steps
      completed" cannot supply it, because a step can complete
      and change nothing. The cold open completed 190.

  (7) So progress needs a definition that is not a count of
      attempts. The available one: NOVEL DURABLE STATE. A step
      makes progress when it leaves the system somewhere it has
      not been.

  (8) That is mechanically computable -- hash the workspace, keep
      the set of hashes -- and it makes the most expensive failure
      in long-running systems detectable for the first time: the
      run that is entirely healthy and has stopped moving.
```

Step (7) is the chapter's definition and it is worth stating on its own. **Progress is novel durable
state.** Not steps, not tokens, not elapsed time, not the model's assessment of how it is going.

### 2.3 What counts as novel

The definition needs teeth, and the teeth are in what goes into the hash.

| Included | Why |
|---|---|
| Workspace content hash | The main signal. A run that edits a file back to a previous form has produced a state it has seen |
| Set of distinct node identities completed | Chapter 21's identity; catches re-doing work under new node ids |
| Terminal-status transitions in the graph | A node reaching `succeeded` is progress even if it changed no files |
| Verdicts recorded (Chapter 28) | A new `FAIL` is progress: the system knows something it did not |

| Excluded | Why |
|---|---|
| Step count | The cold open |
| Tokens spent | Measures fuel, not distance |
| Elapsed time | Same |
| Model self-assessment | Chapter 28 §2.3: reflection has no authority, including over this |
| Log volume, observation volume | A run reading the same file repeatedly generates megabytes and learns nothing |

The fourth included row is worth defending because it is counter-intuitive. Discovering that
something fails is progress — the system's knowledge changed and the change is durable. A run that
tries three approaches and records three failures has moved, and a progress definition that calls
that stationary will kill runs that are working correctly on hard problems.

### 2.4 The mental model to carry

A long run allocates its budget by phase against remaining work, holds reserves it may not touch,
and continuously computes whether it is producing novel durable state. When novelty stops for a
bounded window, the run is stalled regardless of how healthy every other signal looks, and stalling
is a first-class outcome with its own handling — not an error, not a success, and not something to
be discovered by a person at 04:50.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +~~~~~~~~~~~~~~~~+   request ends in seconds; run continues (C8)
   |     Client     |----------------------------+
   +~~~~~~~~~~~~~~~~+                            |
          ^                                      v
          | (5) poll / subscribe        +------------------+
          |     to durable progress     |  Admission (C23) |
          |                             +------------------+
   +--------------------------+                  |
   |   Progress projection    |                  | (1) budget
   |   rebuilt from events    |                  |     allocation,
   +--------------------------+                  |     phased
          ^                                      v
          | (4) derived, never                +--------------------+
          |     authoritative                 |   Runtime loop     |
          |                                   |      (C18)         |
   +--------------------------+               +--------------------+
   |     Event spine (C22)    |<-------------------+   |
   +--------------------------+   (3) events        |  | (2) after
          ^                                          |  |  every step
          |                                          |  v
          |                            +-----------------------------+
          +----------------------------|    Progress detector        |
                                       |                             |
                                       |  novelty hash over:         |
                                       |    workspace | identities   |
                                       |    | terminal transitions   |
                                       |    | verdicts               |
                                       |                             |
                                       |  window of K steps with no  |
                                       |  novel state -> STALLED     |
                                       +-----------------------------+
                                                     |
                                                     v
                                       +-----------------------------+
                                       |   Budget governor           |
                                       |   phase caps | reserves     |
                                       |   point of no return        |
                                       +-----------------------------+

  Figure 29.1 -- A run that outlives its request (D1 High-Level
                 Architecture)

  (1) allocation is decided at admission, from the graph's shape
  (2) the detector runs after EVERY step; it is cheap and its value
      comes entirely from being continuous
  (3) stall detection emits an event like any other outcome
  (4) progress shown to humans is a projection -- delete it and
      rebuild it; it is never the thing decisions are made from
  (5) the client left long ago and comes back to a durable answer
```

### 3.1 The progress detector runs after every step

It is drawn on the hot path deliberately. The cost is a hash over the workspace and a set membership
test — single-digit milliseconds against a step that took seconds — and the entire value of the
mechanism comes from being continuous. A detector that runs every ten minutes finds the cold open at
minute ten rather than minute one hundred and ninety, which is a large improvement; a detector that
runs every step finds it at the first repeat, which is a different thing altogether.

### 3.2 Progress shown to humans is a projection

Chapter 9 sorted things into durable facts and projections, and progress belongs firmly in the
second category. The events are the facts; the percentage, the phase label, and the estimated
completion are derived and rebuildable.

This matters more here than elsewhere because long-running work creates enormous pressure to store a
progress record and update it — a caller arrives six hours later and wants an answer, and a stored
number is the obvious way to have one. A stored, incrementally-updated progress number is a cursor
in the sense of Chapter 22, with the same crash semantics and the same tendency to be quietly wrong.
Rebuild it from events.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                  LONG-RUN MACHINERY                            |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |    Budget governor       |  |    Progress detector      |   |
   |  |                          |  |                           |   |
   |  |  phase caps from the     |  |  novelty_hash(state)      |   |
   |  |  graph's shape           |  |  seen: set[hash]          |   |
   |  |                          |  |                           |   |
   |  |  reserves, unspendable:  |  |  stall when the last K    |   |
   |  |   - compensation (C27)   |  |  steps produced no hash   |   |
   |  |   - finish reserve       |  |  outside `seen`           |   |
   |  |                          |  |                           |   |
   |  |  point of no return:     |  |  K scales with phase, not |   |
   |  |  past it, no new work    |  |  a constant (5.3)         |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Timeout policy         |  |   Session checkpointer    |   |
   |  |                          |  |                           |   |
   |  |  per-tool, from measured |  |  the run must survive     |   |
   |  |  p99 -- NOT a global     |  |  worker replacement at    |   |
   |  |  constant tuned on the   |  |  any moment (C21)         |   |
   |  |  benchmark (5.4)         |  |                           |   |
   |  |                          |  |  checkpoint cadence is a  |   |
   |  |  step budget separate    |  |  cost/loss trade, stated  |   |
   |  |  from wall clock         |  |  explicitly               |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 29.2 -- Inside the long-run machinery (D2 Low-Level
                 Architecture)
```

### 4.1 Three budgets, and they are not interchangeable

A long run is bounded on three independent axes, and collapsing them into one number is how systems
end up unable to explain why they stopped.

| Budget | Bounds | Exhausted means |
|---|---|---|
| **Tokens** | Money | The work cost more than it was worth |
| **Wall clock** | Latency, and the user's patience | The answer arrived too late to matter |
| **Steps** | Runaway loops | Something is wrong with the run's structure |

They are exhausted by different failures. A run that spends its token budget in ninety minutes has a
context problem (Chapter 11). A run that spends its wall clock with tokens to spare is waiting on
something — a sandbox, a queue, a rate limit. A run that hits its step cap with both others healthy
is the cold open.

`[BP]` Report which budget was exhausted, always, in the run's terminal record. "Budget exceeded" is
an unactionable message; "step budget exceeded with 61% of tokens and 44% of wall clock remaining"
names the diagnosis.

### 4.2 Reserves are unspendable, and that has to be enforced

Two reserves matter, and both are held back from the ordinary budget rather than hoped for:

- **Compensation reserve** (Chapter 27 §5.2). A run that fails by exhausting its budget has nothing
  left to reverse its effects with, which is the worst possible moment to discover the shortfall.
- **Finish reserve.** The last steps of a long run — integration, verification, opening the pull
  request — are the expensive ones, and a run that arrives at them with 4% remaining produces six
  hours of work and no deliverable.

`[BP]` Size the finish reserve from the measured cost of terminal nodes in the graph, not as a
percentage. The graph is known at admission and its terminal nodes are identifiable, so this is
computable rather than guessed.

### 4.3 The point of no return

Past a defined fraction of the wall-clock budget, the run stops starting new work and spends what
remains finishing what is in flight. Concretely: the ready-set resolver stops returning nodes that
open new branches, and the run drains.

This is worth having for the same reason a flight has one. The alternative — continuing to start
work until the budget runs out — reliably produces a run that terminates with eleven things half
done, which is the state Chapter 27 has to clean up and the state a human finds hardest to take
over.

---

## 5. Progress, Stalling, and the Timeout Hazard

### 5.1 The stall, seen properly

```
                                                             TIME VIEW

  step  action                    workspace hash   novel?  window
  ----  ------------------------  ---------------  ------  --------
  148   edit exporters.py         a4f1...          YES     reset
  149   run suite (3 fail)        a4f1...          no      1
  150   edit exporters.py         9c02...          YES     reset
  151   run suite (3 fail)        9c02...          no      1
  152   edit exporters.py         a4f1...          no  <-- 2
        ^^^ SEEN AT STEP 148                              |
  153   run suite (3 fail)        a4f1...          no      3
  154   edit exporters.py         9c02...          no      4
  155   run suite (3 fail)        9c02...          no      5
  156   edit exporters.py         a4f1...          no      6
  ...                                                      ...
  160   run suite (3 fail)        9c02...          no      10 -> STALL

  DETECTED at step 160. The cold open ran to step 340.

  What every OTHER signal said at step 160:
      errors            0
      tool failures     0
      contracts failed  0
      tokens            within forecast
      wall clock        within forecast
      step counter      rising steadily
      model's own view  "making progress on the export tests"

  The novelty column is the only one that is not green, and it is
  not close: eight of the last ten steps produced a state the run
  had already been in.

  Figure 29.3 -- Two hundred steps of health, and the one column that
                 disagrees (D8 Control Flow)
```

The figure's second half is the argument. Every conventional signal was correct and every one was
useless, because they all measure whether the machinery is working and none of them measures whether
the work is moving. Those are different questions and only one of them has an instrument on most
dashboards.

### 5.2 What to do about a stall

A stall is not an error and should not be treated as one. The run is healthy; it is stuck. `[BP]`
The escalation that works, in order:

1. **Tell the run.** Emit the stall as an observation, naming it concretely: *the last ten steps
   produced two distinct workspace states, both previously visited; `exporters.py` has been edited
   to a prior form three times.* Chapter 15's rule applies — this is an error message, and an error
   message is an instruction. A surprising fraction of stalls break at this step, because the run
   genuinely did not know.
2. **Force a replan** (Chapter 26), with the stall record as the failure record. The oscillation is
   evidence that the decomposition is wrong, and it is exactly the "new information" the replan guard
   requires.
3. **Park at a human gate** (Chapter 30). A run that stalls twice in one lineage has a problem the
   system has demonstrated it cannot solve, and continuing costs money to no end.
4. **Terminate**, with the stall named in the terminal record.

The ordering matters because each step is dramatically cheaper than the next, and because step 1 is
free and works often enough to be worth always trying.

### 5.3 The window is not a constant

The stall window `K` — how many non-novel steps before declaring a stall — cannot be a single
number, and getting this wrong produces false stalls that are worse than the thing they detect.

Legitimate non-novelty happens. A run reading twelve files to understand a subsystem produces no
workspace change for twelve steps and is working correctly. A run waiting on a slow CI check
produces none for as long as the check takes.

`[BP]` Scale `K` by what the steps are doing rather than by counting them uniformly: a window over
*effectful* steps, not all steps. Reading is exempt by construction, because reading is not supposed
to change anything, and the oscillation in §5.1 shows up unmistakably because every second step in
it was an edit.

That refinement makes the detector both more sensitive and less prone to false positives at the same
time, which is unusual enough to be worth noticing — it comes from measuring the right population
rather than from tuning a threshold.

### 5.4 Timeout coupling, the generalisation hazard

`[AHE Limitations]` The failure works like this. A harness is tuned against a benchmark. The
benchmark's tasks take between two and twenty minutes. Every timeout, every step cap, every "this is
taking too long, try something else" heuristic gets fitted to that distribution, because fitting
them improves the score.

The harness now encodes a belief about how long problems take. Deploy it on a six-hour migration and
it abandons approaches at twelve minutes, replans work that was fine, and fails — not from any
capability gap, but because a hyperparameter was fitted to the evaluation set.

The hazard is nasty for three reasons. It is invisible in the benchmark that created it, because
there the parameter is correct. It looks like a capability failure when it appears, so investigation
starts in the wrong place. And it gets *worse* with tuning: the more thoroughly a harness is
optimised against a benchmark, the more tightly its temporal parameters are bound to that
benchmark's task lengths.

`[BP]` Three mitigations, in increasing order of effort and value:

- **Derive timeouts from measured tool behaviour, not from run outcomes.** A tool's timeout comes
  from its own p99 duration. That number is a property of the tool and does not move when the
  benchmark changes.
- **Express budgets in relative terms where possible.** "Abandon an approach after 20% of the
  remaining budget" travels across task lengths; "abandon after 12 minutes" does not.
- **Include long tasks in the evaluation set** (Chapter 41). Expensive, and the only mitigation that
  actually measures the thing. A benchmark with no six-hour tasks cannot detect a harness that fails
  on six-hour tasks, and no amount of care elsewhere substitutes for that.

### 5.5 The run has no caller, and that is a design input

Six hours means nobody is attached. Four consequences, each of which is a small piece of work that
must be done deliberately:

- **Cancellation is durable state, not a connection drop.** A `cancel_requested` flag the loop
  checks at each step boundary, because there is no socket to close.
- **Progress is queryable, not pushed.** Someone arriving at hour four asks a durable projection
  (§3.2), and gets an answer that does not depend on having been present.
- **The run must survive worker replacement**, which is Chapter 21 in full: deploys happen during
  six-hour windows, and a run that cannot cross one is a run that fails on every deploy.
- **Notification is an effect with a tier.** Telling someone the run finished is a Chapter 27 tier-3
  effect, which means it needs the same care as any other escaped effect, and it is the one most
  likely to be sent twice by a well-meaning retry.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  hh:mm  Phase          Budget                Progress detector
  -----  -------------  --------------------  ----------------------
  00:00  admission      alloc from graph:
                          explore   15%
                          implement 45%
                          integrate 25%
                          reserves  15%
                            (comp 5, finish 10)
  00:04  explore        3% spent              novel every step
  00:41  implement      18% spent             novel most steps
  01:58  implement      44% spent             novel
  02:03  implement      45% spent             SEEN a4f1 (step 152)
  02:04                                       window 3
  02:06                                       window 10 -> STALL
  02:06                 no budget change      << run.stalled >>
                                              escalation step 1:
                                              observation to the run
  02:07  implement      45% spent             run tries a different
                                              file; novel again
  03:30  implement      67% spent             novel
  04:10  integrate      79% spent
  04:55  point of no    88% spent             resolver stops
         return                               returning new branches
  05:20  integrate      93% spent             draining in-flight only
  05:38  finish         96% spent             finish reserve engaged
  05:44  PR opened      97% spent             terminal

  COMPARE the cold open: stall at 02:06 vs discovery at 04:50.
  The difference is 164 minutes and ~$170, and the mechanism is a
  hash comparison.

  FAILURE BRANCH -- escalation step 1 does not work:

    02:07  observation delivered; run continues oscillating
    02:11  window 10 again -> second stall in this lineage
           -> escalation step 2: forced replan (C26), with the
              stall record as the failure record
    02:12  p2 minted: decomposition changes -- the export tests
           are split from the framework migration
    02:14  novel again
           IF p2 also stalls -> escalation step 3: park at a human
           gate (C30). The run has now demonstrated twice that it
           cannot solve this, and further spend has no argument
           behind it.

  Figure 29.4 -- Six hours, with the stall caught at 02:06
                 (D4 Sequence)
```

The line at 04:55 is worth its own note. The point of no return fires at 88% of wall clock, and
after it the run finished cleanly with a deliverable. Without it, the same run would have started
one more subsystem at 05:10 and terminated at 06:00 with that subsystem half migrated — six hours of
work producing something a human has to unpick rather than review.

---

## 7. State Management

```
                                                            STATE VIEW

      {{ active }}
        |    ^  novel state produced
        |    |
        |    +-------------------------------+
        |                                    |
        | K effectful steps, no novelty      |
        v                                    |
      {{ stalled }} ---- observation, run recovers ----+
        |
        | second stall in this lineage
        v
      {{ parked }}   waiting at a human gate (C30); consumes NO
        |            budget while parked -- this is the whole
        |            point of parking rather than waiting
        |
        +---- human resumes ----> {{ active }}
        |
        +---- human cancels ----> {{ cancelled }}  (terminal)

      {{ active }} ---- point of no return ----> {{ draining }}
                                                     |
                        no new branches started;     |
                        in-flight work finishes      |
                                                     v
                                              {{ completed }} or
                                              {{ budget_exhausted }}

      ILLEGAL: {{ stalled }} -> {{ completed }}. A stalled run that
      then completes passed through {{ active }}; the transition is
      recorded, because "this run stalled once and recovered" is a
      fact worth keeping and is invisible if the state is overwritten.

      ILLEGAL: {{ parked }} consuming budget. A parked run holds no
      lease, no semaphore slot, and no worker. If parking costs
      anything per unit time, the gate becomes a thing to avoid and
      C30's authority erodes for economic reasons.

  Figure 29.5 -- Long-run states (D6 State Diagram)
```

### 7.1 Parking must be free

The second illegal transition is the one with real consequences. A run parked at a human gate might
wait overnight. If parking holds a worker, a lease, or a model-semaphore slot, then a system with
twenty parked runs has twenty workers doing nothing, and the entirely rational response is to reduce
the number of things that park.

That response is a safety regression arrived at through capacity planning, which is the worst way to
arrive at one. `[BP]` A parked run is a durable row and nothing else — Chapter 30 calls it a park
holding nothing, and this is where the cost of getting it wrong becomes visible.

### 7.2 Novelty state is derived, and bounded

The `seen` set of state hashes is derived: rebuildable by replaying the run's events, and losing it
costs a stall detection window rather than correctness. It also needs a bound — a six-hour run at
one step every twenty seconds produces about a thousand hashes, which is nothing, but a bound should
exist so nobody discovers the exception at hour nine. `[BP]` A bounded ring of the last few thousand
hashes detects every oscillation that matters; genuinely returning to a state visited five thousand
steps ago is rare and is a different problem.

---

## 8. Internal APIs

```python
from typing import Protocol
from dataclasses import dataclass


class ProgressDetector(Protocol):

    def observe(self, run_id: str, state: "RunState") -> "Novelty":
        """Called after EVERY step. Computes a novelty hash over the
        workspace, completed node identities, terminal transitions,
        and recorded verdicts -- and NOT over step count, tokens, or
        elapsed time (2.3).

        Cheap by design: a hash and a set lookup. Its value comes
        entirely from being continuous (3.1).
        """

    def is_stalled(self, run_id: str) -> "Stall | None":
        """A stall is K EFFECTFUL steps with no novel state. Reads are
        exempt by construction, which makes the detector both more
        sensitive and less prone to false positives (5.3).
        """


class BudgetGovernor(Protocol):

    def allocate(self, graph: "PlanGraph") -> "Allocation":
        """Phase caps plus reserves, derived from the graph's shape at
        admission. The finish reserve is sized from the measured cost
        of the graph's terminal nodes, not as a percentage (4.2).
        """

    def may_start_new_work(self, run_id: str) -> bool:
        """False past the point of no return. The ready-set resolver
        consults this before returning nodes that open new branches,
        so a long run drains rather than terminating mid-branch (4.3).
        """

    def exhausted(self, run_id: str) -> "BudgetAxis | None":
        """WHICH budget ran out: tokens, wall clock, or steps. Never a
        bare boolean -- the axis is the diagnosis, and the three are
        exhausted by three different failures (4.1).
        """
```

`exhausted` returning an axis rather than a boolean is a small signature choice with a large payoff
in operations. It converts an unactionable terminal message into one that names where to look, and
it costs one enum.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class BudgetAxis(str, Enum):
    TOKENS = "tokens"
    WALL_CLOCK = "wall_clock"
    STEPS = "steps"


@dataclass(frozen=True)
class Allocation:
    per_phase: dict[str, float]      # fractions, summing with reserves to 1
    compensation_reserve: float      # unspendable by ordinary work (C27)
    finish_reserve: float            # sized from terminal node costs
    point_of_no_return: float        # fraction of wall clock


@dataclass(frozen=True)
class Novelty:
    state_hash: str
    is_novel: bool
    effectful: bool                  # only these count toward the window
    seen_at_step: int | None         # when this state was last visited


@dataclass(frozen=True)
class Stall:
    run_id: str
    window_steps: int
    distinct_states: int             # 2 in the cold open
    repeated_artefacts: tuple[str, ...]   # "exporters.py"
    detected_at_step: int
    lineage_stall_count: int         # drives the 5.2 escalation
```

`Stall` carries `repeated_artefacts` and `distinct_states` because escalation step 1 needs them.
"You appear to be stuck" is a useless observation; "the last ten steps produced two distinct
workspace states and `exporters.py` has been edited to a prior form three times" is specific enough
to act on, and both fields are free — the detector already has them.

`lineage_stall_count` lives on the stall rather than being recomputed, because it is what selects the
escalation tier, and a count derived at read time from a lineage that has been repaired is exactly
the kind of thing that resets when it should not (Chapter 27 §4.2, same mistake, different subsystem).

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Runtime loop | Progress detector | Synchronous, after every step | Run state snapshot |
| Progress detector | Event spine | Outbox row | `run.stalled`, `run.recovered` |
| Progress detector | Runtime loop | Observation, on first stall | The specific repetition (§5.2 step 1) |
| Budget governor | Ready-set resolver | Synchronous predicate | May new branches start |
| Event spine | Progress projection | Ordered consumption | Everything a human sees |
| Client | Progress projection | Query, arriving at any time | No connection assumed |
| Runtime loop | Notification | Chapter 27 tier-3 effect | Completion, gated and identity-keyed |

The third row is the one that pays for the subsystem. Sending the stall back into the run as an
observation costs one message and resolves a meaningful share of stalls without escalation, and it
is the row most likely to be left out of an implementation that treats stalling as an alerting
concern.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Run oscillating between visited states | Novelty window (§5.1) | Escalate: observe, replan, park, terminate (§5.2) |
| Progress inferred from step count | Nothing — looks healthy | Structural: define progress as novel durable state |
| False stall during a long read phase | Stall rate on read-heavy phases | Window over effectful steps only (§5.3) |
| Budget spent early, nothing left to finish | Finish reserve engaged with work outstanding | Size the reserve from terminal node costs (§4.2) |
| Compensation unaffordable at failure | Chapter 27 §5.2 | Reserve at admission; unspendable by ordinary work |
| Timeouts fitted to benchmark task lengths | Invisible in that benchmark — this is the hazard | Derive from tool p99; express budgets relatively; put long tasks in the evaluation set (§5.4) |
| Run cannot survive a deploy | Failure rate correlated with deploy times | Chapter 21 in full; a six-hour window will contain a deploy |
| Parked run holding a worker | Worker utilisation with many parked runs | A park is a durable row and nothing else (§7.1) |
| Completion notification sent twice | Duplicate reports | Tier-3 effect with an identity key (Chapter 27) |
| Terminal record says "budget exceeded" | Unactionable postmortems | Report the axis (§4.1) |

The sixth row has no detector by design, and the table should say so rather than inventing one. A
harness whose timeouts are fitted to its benchmark passes that benchmark. The only instrument that
finds it is a benchmark containing tasks of a length it was not fitted to, which is why §5.4's third
mitigation is the one that counts and the other two are hygiene.

---

## 12. Scalability

**Long runs change the shape of capacity planning entirely.** A hundred six-hour runs occupy workers
for six hours; a hundred two-minute runs occupy them for two minutes. Chapter 33 sizes pools from
service times, and a bimodal service-time distribution — most runs short, a few enormous — is the
distribution that makes single-queue systems behave worst. Chapter 23's latency classes exist for
this, and long runs belong in their own class.

**Checkpoint cadence is a stated trade, not a default.** Checkpointing every step costs writes;
checkpointing every ten costs up to ten steps of work on a crash. Over six hours the difference is
material in both directions. `[BP]` Checkpoint after every effectful step and on a timer otherwise
— the expensive thing to lose is an effect, and pure steps are cheap to redo.

**The `seen` set is bounded and tiny** (§7.2). No scaling concern; the bound exists for tidiness.

**Progress projections are read far more often than they are written** on long runs, because humans
check on them. Build the projection from events once per event, not per query.

---

## 13. Production Engineering

### 13.1 The four numbers

- **Stall rate, and stalls per lineage.** The headline. A rising stall rate in one task type is a
  decomposition problem with an address.
- **Stall recovery rate at escalation step 1.** How often telling the run is enough. A high number
  means the mechanism is cheap and working; a low one means step 1 should be reconsidered rather
  than tuned.
- **Which budget axis was exhausted, by task type.** Three different diagnoses (§4.1), and the
  distribution moves before outcomes do.
- **Reserve engagement rate.** How often the finish reserve was needed. Frequently means allocation
  is systematically under-provisioning the end.

### 13.2 The review question

For any long-running feature: **what does this look like at hour four, with nobody watching?**

Most long-run defects are ordinary short-run behaviour extended past the point where anyone is
present. A retry loop that is fine for ninety seconds is a hundred and eighty dollars over two
hours. A progress bar that is approximately right for ten minutes is confidently wrong for six
hours. The question surfaces both.

### 13.3 Teaching this to a new engineer

Show them the cold open's dashboard — every signal green, step counter rising — and ask what is
wrong. It usually takes a while, because nothing is wrong with any of the signals.

Then ask what a *stationary* run would look like on that dashboard. The answer is: identical. Once
someone has seen that the instrumentation cannot distinguish moving from stuck, the definition of
progress as novel durable state arrives on its own, and so does the reason step count was never
going to work.

---

## 14. Relation to AHE

`[AHE Limitations]` Timeout coupling is named in the source as a generalisation hazard, and §5.4
treats it as the chapter's central operational risk. The addition here is the mitigation ordering
and the observation that the hazard *worsens* with tuning — the more thoroughly a harness is
optimised against a benchmark, the more tightly its temporal parameters bind to that benchmark's task
lengths. That makes it a risk that grows exactly where confidence grows.

`[INF]` For Level 5 the consequence is direct: an evolution loop that may edit timeouts and step
caps will fit them to the evaluation set, because doing so raises the score. This is not
misbehaviour; it is the loop working. Chapter 20 §5.5's containment list gains a candidate — temporal
parameters — and Chapter 46 has to decide whether they sit inside or outside the workspace. The
argument for outside is that no outcome-based reward can distinguish a well-tuned timeout from an
overfitted one.

`[INF]` Progress detection has an evolution-loop analogue that is worth building. A loop proposing
variants that produce no novel *harness* state — the same edit, re-derived — is stalled in exactly
this sense, and Chapter 26 §14 already required that a proposal carry new evidence. The two guards
are the same guard at two grains.

---

## 15. Industry Perspective

**`[BP]` Durable-execution engines solved the survival half.** Temporal, Restate, and their
relatives handle multi-hour and multi-day executions with checkpointing and replay, and Chapter 21
already recommended not rebuilding that. None of them supplies progress detection, because progress
is domain-specific — they cannot know what novel state means for your work, and this chapter's
definition is the piece you have to bring.

**`[BP]` Watchdog timers in embedded systems are the closest prior art to stall detection**, and
their design lesson transfers: the watchdog must be fed by evidence of *work*, not by the scheduler
running. A watchdog fed by "the loop is executing" detects a hung process and misses a spinning one,
which is precisely the distinction between step count and novelty.

**`[INF]` The bimodal service-time problem is well understood in queueing theory and routinely
ignored in practice.** Mixing six-hour and two-minute work in one queue produces the convoy effect of
Chapter 23 at its worst, and the fix — separate classes — is standard, cheap, and skipped because the
long runs are rare enough not to seem worth a class of their own.

**`[FUT]` Progress definitions beyond workspace novelty are unexplored.** Novel durable state is a
sound floor and it is coarse: a run making tiny irrelevant edits registers as progressing. Semantic
progress — is the run closer to the goal — is the obvious next question, and the obvious answer is a
model judgment, which Chapter 28 §2.3 has already disqualified from carrying that authority. This is
open.

---

## 16. Key Takeaways

1. **Progress is novel durable state.** Not steps, not tokens, not elapsed time, not the run's own
   assessment. Everything else in this chapter depends on having a definition that a stationary run
   cannot satisfy.
2. **The expensive long-run failure has no error.** A healthy run going in circles produces steps at
   exactly the rate useful work does, and every conventional signal stays green for as long as you
   let it.
3. **Detect over effectful steps, not all steps.** Reading legitimately changes nothing. This one
   refinement makes the detector both more sensitive and less prone to false positives.
4. **Three budgets, three diagnoses.** Tokens, wall clock, and steps are exhausted by different
   failures. Report which one ended the run.
5. **Reserves must be unspendable and sized, not hoped for.** Compensation and finish reserves are
   computable from the graph at admission; a run that arrives at its last steps with nothing left
   produces six hours of work and no deliverable.
6. **Tell the run first.** A stall delivered back as a specific observation resolves a meaningful
   share of them for the cost of one message, and it is the escalation step most often skipped.
7. **Timeouts fitted to a benchmark encode that benchmark's task lengths.** The hazard is invisible
   where it was created, looks like a capability gap when it appears, and worsens with tuning. Only
   long tasks in the evaluation set detect it.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Novel durable state** | The definition of progress: a step makes progress when it leaves the system somewhere it has not been. | `[INF]` | Ch 34, Ch 36 |
| **Stall** | K effectful steps producing no novel state, which is a healthy run that has stopped moving and is not an error. | `[INF]` | Ch 34, Ch 36 |
| **Novelty window** | The bounded count of recent effectful steps over which novelty is assessed, exempting reads by construction. | `[INF]` | Ch 34 |
| **Stall escalation** | Observe, then replan, then park, then terminate — ordered so the free option is always tried first. | `[BP]` | Ch 30 |
| **Budget axis** | Which of tokens, wall clock, or steps was exhausted, reported always because the three name different diagnoses. | `[INF]` | Ch 35 |
| **Finish reserve** | Budget held back and sized from the measured cost of the graph's terminal nodes, so a long run ends with a deliverable. | `[BP]` | Ch 35 |
| **Point of no return** | The fraction of wall clock past which no new branches start and the run drains what is in flight. | `[BP]` | Ch 36 |
| **Timeout coupling** | Temporal parameters fitted to a benchmark's task lengths, invisible in that benchmark and worsening with tuning. | `[AHE]` | Ch 41, Ch 46 |
| **Parking** | Suspending a run at a gate while it holds no worker, lease, or semaphore slot, so that parking is economically free. | `[DAR]` | Ch 30 |
| **Draining** | Finishing in-flight work without starting new branches, so a budget-bounded run ends complete rather than fragmented. | `[INF]` | Ch 36 |

---

**Next:** Chapter 30 — *Human Authority.* Parking has been referred to in five chapters and defined
in none. This one defines it: the gate as a durable park holding nothing, enforcement that lives in
the runner and never in the instructions, and the argument that a human redirecting a run and a
crash recovering one are the same problem — which is why Chapter 10's immutable plan turns out to
have been about authority all along.
