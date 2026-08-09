```
  Level 3 · Chapter 26
  PLANNING ALGORITHMS
  Requires   C10 The Planner, C13 The Reasoning Engine,
             C24 The Task Graph, C25 The World Model
  Unlocks    C27 Failure and Rollback, C28 Grading,
             C30 Human Authority, C41 Evaluation Infrastructure
  Diagrams   Core (5)
```

# Chapter 26 — Planning Algorithms

---

## 1. Motivation

### 1.1 Cold open

Atlas is asked to add rate limiting to three endpoints in `notifications-api`. It produces an
eleven-step plan. The plan reads well: locate the middleware layer, add a limiter, wire it to the
three routes, add tests, run the suite, open a pull request.

Step 4 fails. The repository does not use pytest; it uses a house test runner invoked through a
`make` target, and `pytest tests/` exits with a usage error.

The runtime replans. The new plan has eleven steps. Nine are word-for-word identical to the first
plan's, and step 4 is `run pytest tests/`.

It fails identically. The runtime replans. Six plans in four minutes, each eleven steps, each dying
at step 4 with the same error, until the budget guard stops the run.

The postmortem finds the defect in one line of the replan path. The planner was called with the
goal, the repository map, and the run's current state. It was not called with the reason the
previous plan had died. Every replan was a fresh derivation from unchanged inputs, so it produced
the same output — correctly, deterministically, six times.

The failure was not that the model planned badly. It planned identically, which is what a function
does when you call it with the same arguments.

### 1.2 In plain language

Chapter 10 said what a plan *is* — an immutable list of steps, minted once, replaced rather than
edited. Chapter 24 said what shape it has — a graph, so independence is written down. Neither said
how the steps get chosen. That is this chapter.

There are really two questions. The first is how to break a goal into steps at all: how far down to
break it, and whether to consider several possible breakdowns before committing to one. The second
is what to do when reality disagrees with the plan you made, which it will, because a plan is a
prediction and predictions about software are wrong routinely.

The second question turns out to be the one that decides whether a system works in production. A
step failing is normal. What matters is the response, and there are three: try the step again, patch
the part of the plan that has not run yet, or throw the plan away and make a new one. They cost
roughly one unit, three units, and thirty units. Picking the expensive one every time burns the
budget without progress — that is the cold open. Picking the cheap one every time produces a run
that keeps politely retrying inside a plan that was never going to work.

Choosing correctly requires knowing *why* the step failed, in a form something other than a human
can act on. And that requirement reaches all the way back into how the plan was written in the
first place.

### 1.3 Why this chapter exists

Chapter 10 deliberately treated the planner as a port: something that takes a goal and returns a
plan, whose internals were out of scope so that the identity and authority arguments could be made
cleanly. That was the right order — the contract does not depend on the algorithm — but it leaves a
gap that shows up the first time a plan is wrong.

This chapter fills it, and it makes one strong claim that shapes the rest: **most of the value in
planning is not in producing the first plan.** The first plan is cheap and, for a competent model on
a well-scoped goal, usually adequate. The value is in the machinery around it — knowing when it has
become wrong, knowing which part is wrong, and knowing the cheapest repair. A team that invests in
search over first plans and neglects the failure path builds a system that plans beautifully and
cannot recover.

### 1.4 What previous framings got wrong

**"Better planning means searching more plans."** Classical planning search assumes a cheap
evaluation function: you can score a candidate plan without executing it. Here you cannot. The only
reliable way to find out whether a plan works is to run it, and running it is the expensive thing
you were trying to avoid. Search is not useless (§5.4) but it is not the default, and treating it as
the default inverts the cost model.

**"Replanning is the general recovery mechanism."** Replanning is the *most expensive* recovery
mechanism, and it is correct in a minority of failures. Most step failures are local: a wrong path,
a wrong command, a missing argument. The plan's structure was fine. Discarding it discards every
correct decision it contained along with the one wrong one.

**"A plan is a list of instructions for the model."** A plan whose steps are natural-language
instructions with no declared postconditions cannot be checked, cannot be repaired precisely, and
cannot be approved meaningfully. `[AHE App. C]`'s contract-first framing is not a refinement of
planning; it is what makes everything downstream of planning decidable.

**"Decomposition depth is a matter of taste."** It has a mechanical stopping rule (§5.2), and teams
that treat it as taste produce plans whose steps are either too coarse to check or so fine that the
graph has four hundred nodes of bookkeeping.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Planning is satellite navigation. You state a destination, the system produces a route, and you
follow it. When you miss a turn it does not recompute your entire journey from your front door — it
reroutes from where you actually are, keeping every part of the original route that is still
reachable and still sensible.

The rerouting instinct is exactly right, and it is the instinct the cold open lacked. A navigation
system that started over from the origin on every missed turn would be recognised immediately as
broken.

The analogy breaks on the thing that makes navigation easy, and it is worth being blunt about how
large that thing is.

A navigation system has a **complete, cheap, accurate map**, and a **metric**. It knows every road
before you set off, it can evaluate any candidate route in milliseconds without driving it, and
"better" is well-defined — fewer minutes. All three properties are what make search the right
algorithm there.

A planner has none of them. The map (Chapter 25) is partial and can be stale. There is no way to
evaluate a candidate plan short of executing it, and executing it is the cost you were minimising.
And "better" has no metric: plan A and plan B differ in ways whose consequences are unknown until
one of them has been run.

So the transferable half is rerouting. The non-transferable half is search, and every planning
design that reaches for tree search first has implicitly assumed a map and a metric it does not
have.

### 2.2 Why planning algorithms must exist

```
  (1) Baseline: no plan at all. Ask the model for the next action,
      execute it, observe, repeat. This works, it is what ReAct
      describes, and for short tasks it is hard to beat.

  (2) But a run with no plan has nothing a human can approve. C30
      needs something to hold at a gate, and "whatever it decides
      next" is not reviewable. Approval requires a plan to exist
      before execution.

  (3) And a run with no plan cannot parallelise. C24's graph needs
      declared independence; a system deciding one step at a time
      never knows about step 7 while it is doing step 2.

  (4) So the runtime plans ahead. This introduces a failure the
      baseline could not have: the plan can be wrong STRUCTURALLY,
      not merely in the execution of one step.

  (5) A structural error found at step 4 has three responses --
      retry the step, repair the plan's unexecuted tail, or mint a
      new plan -- costing roughly 1x, 3x, 30x. Choosing badly is
      expensive in both directions.

  (6) To choose, the system must know WHY step 4 failed, as a
      classification something other than a human can act on.
      A stack trace is not a classification.

  (7) To classify, a step must have declared what it was supposed
      to achieve. "Step 4 failed" is not actionable; "step 4's
      postcondition `tests ran and reported` was not met, and the
      tool exited with a usage error" is.

  (8) Therefore postconditions are written at PLAN time, before
      anything runs. Contract-first planning is not a refinement.
      It is what makes step (5) decidable at all.
```

The derivation's shape is worth noticing: it starts at "how do we plan" and ends at "what must a
plan contain", and the answer to the second question is what determines whether the first has any
good answers.

### 2.3 The three responses, and their real costs

| Response | What it changes | Plan identity | Typical cost | When |
|---|---|---|---|---|
| **Retry** | Nothing | Unchanged | 1x one step | Transient: timeout, rate limit, flaky network |
| **Repair** | The unexecuted tail | New plan, same lineage, parent recorded | ~3x one step | The structure holds; specific steps are wrong |
| **Replan** | Everything not yet done | New plan, new lineage | ~30x one step | The decomposition itself was wrong |

The middle row is the one most systems do not have, and its absence is what forces every non-transient
failure into the thirty-times column. Repair is not a compromise between the other two — it is the
correct answer for the large middle of the distribution, where the plan understood the goal
correctly and got a detail wrong.

Note what stays constant across all three: **no plan is ever edited.** A repair mints a new plan
whose parent is recorded, exactly as Chapter 10 required, and the executed prefix carries over by
identity rather than by copying (§5.3). Repair is cheaper than replan because it re-derives less,
not because it relaxes immutability.

### 2.4 The mental model to carry

A planner is a decomposer that attaches a checkable postcondition to every step, plus a classifier
that turns failures into one of three responses, plus the cheapest of those three that fits the
failure. The decomposer is the part everyone builds. The classifier is the part that decides whether
the system works.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +~~~~~~~~~~~~~+   +---------------+   +------------------+
   | Goal /issue |   | World model   |   |  Failure record  |
   |             |   |   (C25)       |   |  from last plan  |
   +~~~~~~~~~~~~~+   +---------------+   +------------------+
          |                  |                     |
          | (1)              | (2) beliefs,        | (3) THE input
          |                  |     fresh only      |     the cold open
          |                  |                     |     omitted
          v                  v                     v
   +------------------------------------------------------------+
   |                        PLANNER                             |
   |                                                            |
   |   decompose -> attach contracts -> estimate -> select      |
   +------------------------------------------------------------+
          |                                        ^
          | (4) candidate graph                    | (6) reject with
          v                                        |     reason
   +------------------------------------+          |
   |  Admission validator (C24 sec 4)   |----------+
   |  acyclic, width, depth, contracts  |
   +------------------------------------+
          | (5) accepted
          v
   [[ plan_nodes / plan_edges / plan_joins ]]
          |
          v
   +------------------+        +---------------------------+
   |  Runtime loop    |------->|  Failure classifier        |
   |     (C18)        |  step  |  transient / local /       |
   +------------------+  fails |  structural                |
                               +---------------------------+
                                   |        |        |
                                 retry   repair   replan
                                   |        |        |
                                   |        +--------+---> back to (3)
                                   v
                            same plan, same step

  Figure 26.1 -- The planner's inputs, and the loop that returns to it
                 (D1 High-Level Architecture)

  (1) the goal, unchanged across every replan in a lineage
  (2) beliefs, and only FRESH ones -- a stale belief plans a wrong
      plan and nothing downstream can tell (C25 sec 5.4)
  (3) the failure record: what died, its contract, its classification.
      Omitting this wire is the cold open, exactly
  (4) a candidate, not yet stored
  (5) stored in one transaction; only now does the plan exist
  (6) a rejection is a planning input, not an error -- it carries the
      cycle path or the violated cap back for the next attempt
```

Wire (3) is the whole cold open. Everything else in the figure existed in the failing system.

### 3.1 The planner is still a port

None of this changes Chapter 10's contract. The planner receives inputs and returns a candidate
graph; it does not execute, does not observe, and does not decide when it is called. The classifier
sits outside it precisely so that the decision to invoke a replan is made by the runtime under a
budget, not by the component that benefits from being invoked.

That separation matters more than it looks. A planner that decides for itself when to replan is a
component with an unbounded call on the budget, and the cold open is what that looks like when the
model is confident.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                          PLANNER                               |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |      Decomposer          |  |    Contract attacher      |   |
   |  |                          |  |                           |   |
   |  |  goal -> steps           |  |  each step gets a         |   |
   |  |  stopping rule: 5.2      |  |  CHECKABLE postcondition  |   |
   |  |  strategy: flat |        |  |                           |   |
   |  |    least-to-most |       |  |  a step whose contract    |   |
   |  |    contract-first        |  |  cannot be written is     |   |
   |  |                          |  |  under-decomposed         |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     Cost estimator       |  |        Selector           |   |
   |  |                          |  |                           |   |
   |  |  per-step token + tool   |  |  used ONLY when there is  |   |
   |  |  estimate; critical path |  |  more than one candidate  |   |
   |  |  from the graph (C24)    |  |  (5.4). Most runs have    |   |
   |  |                          |  |  exactly one and skip it  |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +----------------------------------------------------------+  |
   |  |                    Repair engine                         |  |
   |  |  input: prior plan + failure record + executed prefix    |  |
   |  |  output: new plan, same lineage, prefix carried by       |  |
   |  |          identity (5.3), tail re-derived                 |  |
   |  +----------------------------------------------------------+  |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 26.2 -- Inside the planner (D2 Low-Level Architecture)
```

### 4.1 The contract attacher is not optional

It is drawn as a separate box because it is a separate obligation, and because making it separate
lets it *reject*. A step whose postcondition cannot be expressed goes back to the decomposer, and
that rejection is the mechanical form of the stopping rule in §5.2.

A postcondition is checkable when it can be evaluated by a deterministic procedure with no model
call. Examples, in increasing order of how much work they took to arrive at:

| Step | Weak postcondition | Checkable postcondition |
|---|---|---|
| Add a limiter | "rate limiting is added" | `grep -q RateLimiter api/middleware.py` exits 0 |
| Wire three routes | "routes are wired" | all three route decorators reference the limiter; count is 3 |
| Run the suite | "tests pass" | the runner exited 0 **and** reported a nonzero test count |
| Open a PR | "PR opened" | a PR number exists and its head SHA equals the local HEAD |

The third row is the cold open's fix hiding in plain sight. `pytest tests/` exiting with a usage
error is exit code 4, not 0 — but a contract written as "the command succeeded" would have caught
it, and a contract written as "tests pass" would have been checked by reading output with a model
and might well have been talked into a pass. **Nonzero test count** is the clause that makes the
difference, and it exists because someone once shipped a green run against zero collected tests.

### 4.2 What the planner deliberately does not do

- **It does not choose when it is called.** §3.1.
- **It does not read the environment.** Beliefs arrive through context (Chapter 25 §10). A planner
  with its own filesystem access is a planner whose inputs are untraceable, and Chapter 16 then
  cannot reconstruct what it saw.
- **It does not estimate its own confidence for consumption downstream.** Cost estimates are used
  by the selector, internally. A confidence score attached to a plan and shown to a human is the
  hedging failure of Chapter 25 §5.4 in a new costume.
- **It does not decide priority, concurrency, or placement.** Those are Chapter 23's, and a plan
  that carries scheduling hints is a plan that will be scheduled inconsistently depending on which
  hints survived.

---

## 5. Decomposition, Repair, and the Cost of Search

### 5.1 Three decomposition strategies, and when each earns its cost

**Flat decomposition.** One model call produces the whole step list. Cheapest, and correct for goals
the model has seen the shape of many times — add an endpoint, fix a failing test, bump a dependency.
Most production traffic is this, and a system optimised for anything else is optimised for its
minority case.

**Least-to-most.** Decompose the goal into sub-goals, then decompose each sub-goal, stopping when
§5.2's rule fires. Two or three model calls instead of one. It earns its cost when the goal spans
subsystems the model cannot hold at once, because a flat decomposition of a wide goal tends to
produce steps at inconsistent granularity — three steps for the part it understood and one step for
the part it did not.

That inconsistency is diagnosable, which makes the choice mechanical rather than intuitive: **if the
estimated cost of the largest step in a flat plan exceeds a few times the median, decompose that
step further.** A plan with one step estimated at 40 minutes among ten steps estimated at 90 seconds
has told you exactly where the model stopped understanding.

**Contract-first.** Write the postconditions before writing the steps. Start from "what will be true
when this is done", derive the checks, then derive the work that satisfies them. `[AHE App. C]`
argues for this as an evaluation-alignment technique, and it has a second benefit the source does not
dwell on: it makes under-decomposition impossible by construction, because a sub-goal you cannot
write a check for never becomes a step.

Its cost is that it is slower and unfamiliar, and models trained on narrative decomposition drift
back to steps-first unless the structure is enforced by the output schema. Enforce it in the schema.

### 5.2 The stopping rule

Decompose until every step satisfies both:

1. **It has a checkable postcondition** (§4.1) — deterministic, no model call.
2. **Its inputs fit one context assembly** under Chapter 11's budget, with room for the observation
   it produces.

Stop as soon as both hold. Do not decompose further, and the reason is concrete: every additional
node is a durable row, a lease, a claim, a checkpoint, and a scheduling decision. Chapter 24's
machinery is not free, and a plan with four hundred trivial nodes spends more on bookkeeping than on
work while making the graph unreadable to the human who has to approve it.

The rule is mechanical and it replaces taste. Two engineers applying it to the same goal will
produce plans of similar granularity, which is worth more than either of them producing a better
plan alone.

### 5.3 Repair: what carries over, and how

Repair produces a new plan with the same lineage. The question that decides whether it is cheap is
what happens to the steps that already ran.

They are **not copied**. They are carried by identity. Chapter 21 gave every activity an identity
hash computed from its inputs, and Chapter 24 stored that hash on the node at mint time. A repaired
plan re-derives its tail and re-emits the prefix; the nodes in the prefix have identical identity
hashes, so when the loop reaches them the identity check reports "already done" and no work occurs.

That is the mechanism, and it has a property worth stating: **repair is safe even if the repair
engine is wrong about the prefix.** Suppose it re-derives a step it thought had not run. The identity
check catches it. Suppose it drops a step that had run — the tail's dependencies will not resolve
and admission rejects the graph. Both error directions are caught by machinery that exists for other
reasons.

What the repair engine actually receives:

```
  prior plan          the graph, with per-node terminal status
  failure record      which node, its contract, the classification,
                      the observation that violated it
  executed prefix     node ids with terminal status, and their
                      identity hashes
  goal                unchanged -- repair never edits the goal
```

The last line is the boundary between repair and Chapter 30's steer. A human amending the goal is a
different operation with different authority, and it forces a full replan because the thing every
plan in the lineage was derived from has changed.

### 5.4 Search, and the narrow band where it pays

Generating several candidate plans and picking one requires a way to pick. Three are available and
two of them are worse than they look.

**Model-as-judge over candidate plans.** Ask the model which plan is better. This is Chapter 28's
territory and Chapter 28's answer applies: a model's judgment of its own output may downgrade a
deterministic verdict, never upgrade one. On plans there is no deterministic verdict to anchor to,
so this is judgment with no floor, and it reliably prefers the plan that reads best.

**Cost estimate.** Pick the cheapest candidate by estimated tokens and critical path. This is
computable and honest, and it is answering a different question than the one asked. The cheapest
plan is often the one that skipped a step.

**Execute-and-verify.** Run several candidates, keep the one whose contracts pass. This actually
works, and it is the only one that does, because it uses the only reliable evaluation function
available. It costs N times as much, and Chapter 24 §5.3 restricts it: a `FIRST` join may only race
branches whose nodes are all pure. Plans that write to the repository cannot be raced.

So the band where search pays is narrow and describable: **the goal is high-value, a cheap
deterministic verifier exists, and the candidate plans are pure or cheaply reversible.** Generating
three test-suite-fixing strategies in three sandboxes and keeping the one that goes green fits.
Racing three plans that each open a pull request does not.

Outside that band, plan once and repair. It is not a compromise; it is the correct response to not
having an evaluation function.

### 5.5 Classifying a failure

The classifier is small, it runs before any of the three responses, and its inputs are the failure
record plus the node's contract.

```
                                                             TIME VIEW

   node fails
       |
       v
   +-------------------------------------------+
   | Did the contract even get evaluated?      |
   +-------------------------------------------+
       | no: tool errored before producing output
       |    |
       |    v
       |  +---------------------------------------+
       |  | Is the error in the transient set?    |
       |  | (timeout, 429, connection reset,      |
       |  |  lease lost, sandbox evicted)         |
       |  +---------------------------------------+
       |      | yes -> RETRY   (attempts < cap)
       |      | no  -> continue below
       v      v
   +-------------------------------------------+
   | Does the failure name something the plan  |
   | asserted?  (wrong path, wrong command,    |
   | missing arg, tool not available)          |
   +-------------------------------------------+
       | yes -> REPAIR: the structure holds, the
       |        detail is wrong. Re-derive the tail.
       |
       | no
       v
   +-------------------------------------------+
   | Has repair already been tried in this     |
   | lineage for this contract?                |
   +-------------------------------------------+
       | yes -> REPLAN: repair is not converging;
       |        the decomposition is the problem
       |
       | no  -> REPAIR (once), then re-enter here

   THE GUARD THAT MATTERS: a replan whose failure record is empty
   is refused. The runtime fails the run instead. A replan with no
   new information is the cold open, and it is better to stop.

  Figure 26.3 -- Classifying a failure into one of three responses
                 (D8 Control Flow)
```

The last block is the fix for §1.1, stated as an invariant rather than a habit: **replanning without
new information is not permitted.** Not discouraged, not rate-limited — refused, with the run failing
and saying why. A rate limit would have turned six identical plans into three identical plans.

`[BP]` Two further bounds belong beside it, and both are cheap: cap replans per lineage at a small
number, and require each replan's failure record to differ from the previous one. Together with the
refusal above they make a replan storm structurally impossible rather than merely unlikely.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  t   Event                          Plan lineage      Cost
  --  -----------------------------  ----------------  -----------
  0   goal received                  --
  1   decompose (flat)               p1 draft          1 model call
  2   attach contracts               p1 draft
        step 4 contract:
        "runner exit 0 AND
         test count > 0"
  3   admission validated            p1 active
  4   steps 1-3 succeed              p1 active
  5   step 4 runs: pytest tests/
        exit 4, usage error
  6   contract not evaluated         --
        (no output produced)
  7   classifier:
        not transient
        names something the plan
        asserted -> REPAIR
  8   repair engine:
        prior plan + failure record  p2 (parent p1)    1 model call
        + executed prefix
        tail re-derived: step 4
        becomes `make test`
  9   admission validated            p2 active
 10   steps 1-3 re-emitted           p2 active         0 -- identity
        identity match, no work                        hit (C21)
 11   step 4: make test -> exit 0,
        41 tests collected
        contract satisfied
 12   steps 5-11 proceed
 13   PR opened                      p2 terminal

  TOTAL: 2 planning calls, 1 wasted step. Compare the cold open:
  6 planning calls, 6 wasted steps, 0 progress.

  FAILURE BRANCH -- suppose `make test` also fails, with the same
  classification:

      classifier reaches "has repair already been tried in this
      lineage for this contract?" -> yes
      -> REPLAN, with a failure record naming BOTH attempts
      -> p3, new lineage, and the planner now has evidence that
         the test-invocation assumption is the problem rather
         than the command
      -> if p3's failure record would be identical to p2's, the
         replan is refused and the run fails loudly

  Figure 26.4 -- The cold open, planned and repaired correctly
                 (D4 Sequence)
```

The line worth dwelling on is t=10: three steps re-emitted, zero work performed, because identity
did what Chapter 21 built it to do. Repair is affordable exactly because a repaired plan can restate
its prefix without paying for it, and that property came from a chapter that was not thinking about
planning at all.

---

## 7. State Management

Plans have states, and a lineage is a chain of them. The chapter's immutability requirement shows up
here as a missing transition rather than a rule in prose.

```
                                                            STATE VIEW

      {{ draft }}
          |  contracts attached, admission validated (C24 sec 4)
          v
      {{ active }} ------------------+-------------------+
          |                          |                   |
          | all terminal nodes       | repair            | replan
          | reached                  |                   |
          v                          v                   v
      {{ completed }}         {{ superseded }}    {{ superseded }}
        (terminal)              parent of the       parent of a NEW
                                next plan in        lineage
                                this lineage
          {{ active }}
                |  goal amended by a human (C30 steer)
                v
          {{ abandoned }}  -- lineage ends; a steer starts a new one
                              because the goal every plan derived
                              from has changed

      ILLEGAL: {{ active }} -> {{ active }} with different nodes.
      There is no edit. A plan that needs to change becomes
      {{ superseded }} and a new plan is minted. This is C10's rule,
      and repair does not weaken it -- repair is cheaper because it
      re-derives less, not because it mutates.

      ILLEGAL: {{ superseded }} -> {{ active }}. A superseded plan is
      never revived, even when the repair turns out to be worse. The
      correct response to a bad repair is another repair, forward.

  Figure 26.5 -- Plan states and lineage (D6 State Diagram)
```

### 7.1 What a lineage is for

A lineage is the chain of plans derived from one unchanged goal. It exists for three consumers, and
each one is a reason not to flatten it:

- **The classifier** (§5.5) asks whether repair has already been tried for this contract in this
  lineage. Without the chain there is no answer, and the replan storm guard cannot function.
- **Chapter 30's approval** attaches to a plan. When a repair produces a new plan, whether the prior
  approval carries over is a policy question, and it is answerable only if the relationship between
  the two plans is recorded. The usual policy: a repair inherits approval if its tail introduces no
  new effectful step, and requires re-approval otherwise.
- **Chapter 41's evaluation** counts how many plans a goal took. Plans-per-goal is one of the most
  direct measures of decomposition quality available, and it is free once lineage exists.

### 7.2 Where the plan lives

Plan rows are run state in Chapter 6's sense: owned by the run, durable, never derived. Contracts
live on the node and are written at mint time, which makes them immutable for the same reason the
plan is — a contract that can be edited after the fact is a contract that will be edited to pass.

That last clause is not hypothetical. Chapter 20 §5.5's containment list has a natural next entry
here: an evolution loop that can weaken postconditions raises its score without improving anything,
and the resulting harness scores well on a benchmark whose checks it wrote itself. Contracts belong
with the verifier, outside the evolvable workspace.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class Planner(Protocol):

    def plan(
        self,
        goal: "Goal",
        beliefs: Sequence["Belief"],       # FRESH only (C25)
        failure: "FailureRecord | None",   # None only on the first plan
    ) -> "PlanGraph":
        """Produce a candidate graph. Does not store it, does not
        execute, and does not decide when it was called.

        `failure` being None on anything but the first plan of a
        lineage is a programming error, not a degraded input. Raise.
        That single assertion is the cold open's fix.
        """

    def repair(
        self,
        prior: "PlanGraph",
        executed_prefix: Sequence["NodeRef"],
        failure: "FailureRecord",
    ) -> "PlanGraph":
        """Re-derive the unexecuted tail. The returned graph re-states
        the prefix with identical identity hashes so C21's check
        makes re-execution free.

        The goal is not a parameter, because repair may not change it.
        Changing the goal is a steer (C30) and starts a new lineage.
        """


class FailureClassifier(Protocol):

    def classify(
        self,
        failure: "FailureRecord",
        contract: "Contract | None",
        lineage: "Lineage",
    ) -> "Response":     # RETRY | REPAIR | REPLAN | FAIL_RUN
        """Returns FAIL_RUN when a replan would carry no information
        the previous one did not have. Refusing is correct; a run that
        stops with a clear reason costs less than one that spends its
        budget re-deriving the same plan (5.5).
        """
```

Two signature decisions carry the chapter.

`plan` takes `failure` as a required parameter rather than an optional context field. Optional
context fields get forgotten at one of the several call sites; a required parameter that must be
`None` only on the first call is checked by the type system and asserted at runtime, and the cold
open becomes unwritable.

`repair` does not take the goal. Not "should not use it" — cannot receive it. The boundary between
repair and steer is enforced by the signature rather than by review, which is the same technique
Chapter 30 applies to authority and for the same reason.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class Response(str, Enum):
    RETRY = "retry"
    REPAIR = "repair"
    REPLAN = "replan"
    FAIL_RUN = "fail_run"


@dataclass(frozen=True)
class Contract:
    """A checkable postcondition, written at plan time."""
    check: str            # a deterministic command or predicate
    description: str      # for humans reviewing the plan
    # No model_judged field. If it needs a model, it is not a
    # contract -- see C28 for what a model judgment may do.


@dataclass(frozen=True)
class FailureRecord:
    node_id: str
    plan_id: str
    contract: Contract | None      # None if the tool never produced output
    observation_ref: str           # pointer into the trace store (C16)
    error_class: str               # transient | asserted | structural
    attempt: int


@dataclass(frozen=True)
class Lineage:
    lineage_id: str
    goal_hash: str        # every plan in a lineage shares this
    plans: tuple[str, ...]         # ordered, oldest first
    repairs_by_contract: dict[str, int]   # drives the 5.5 guard
```

`goal_hash` is what defines a lineage, and it is a hash rather than a reference so that the identity
of "same goal" is a value comparison. When a steer amends the goal the hash changes, the lineage
necessarily ends, and no code has to remember to end it.

`repairs_by_contract` is the smallest structure that makes the classifier's third question
answerable. It is a counter keyed by contract, not by node, because a repair renumbers nodes and the
contract is what persists across the repair.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Runtime loop | Classifier | Synchronous call on node failure | Failure record + contract + lineage |
| Classifier | Planner | Synchronous call, only for repair/replan | Prior plan, prefix, failure record |
| Planner | Admission validator | Synchronous | Candidate graph |
| Validator | Planner | Return value, structured | Rejection with the specific violation |
| Planner | Event spine | Outbox row | `plan.minted`, `plan.superseded`, `replan.refused` |
| Planner | Model port | Chapter 13's single door, metered | Assembled context |

`replan.refused` is worth emitting as its own event rather than folding into a run failure. It is the
signal that a lineage exhausted its information, and its rate per goal type is the most direct
available measure of where decomposition is systematically failing — which is a Chapter 41 input,
and one of the few that costs nothing to produce.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Replan with no new information | Classifier's guard (§5.5) | Refuse; fail the run with the reason. Never rate-limit instead |
| Replan storm | Replans-per-lineage counter | Cap at a small number; the cap firing is an alert, not a log line |
| Repair loop on one contract | `repairs_by_contract` | Escalate to replan after the first repair for a given contract fails |
| Contract that cannot be evaluated | Contract attacher rejects at plan time | Decompose further (§5.2); a step with no checkable outcome is under-decomposed |
| Contract weakened to pass | Contracts are immutable after mint (§7.2) | Structural; a mutable contract is the failure |
| Plan built on a stale belief | None at plan time — this is Chapter 25 §1.1 | Prevented upstream: only fresh beliefs reach the planner |
| Steps at wildly inconsistent granularity | Max-to-median cost estimate ratio (§5.1) | Decompose the outlier; the ratio names it precisely |
| Search racing effectful branches | Admission validator, via Chapter 24 §5.3 | Rejected at mint; a `FIRST` join over effectful nodes never gets stored |

The third row's escalation rule is deliberately aggressive. One repair per contract, then replan.
Two repairs on the same contract nearly always means the classifier mislabelled a structural problem
as a local one, and the second repair is a slower way of arriving at the same replan.

---

## 12. Scalability

**Planning is a model-call cost, and it is bounded per lineage.** With the guards of §5.5 in place, a
lineage costs at most one initial plan plus a small number of repairs plus a capped number of
replans. That is a bounded, predictable spend, and the bound is a configuration value rather than an
emergent property — which is the difference between a cost you can budget and one you discover.

**Contract checks are the cheap part and should stay cheap.** A postcondition that runs the full test
suite is not a check, it is a step. Checks should complete in seconds. When one cannot, the step it
guards is too large.

**Search multiplies everything by N, including the failure paths.** The band in §5.4 is narrow partly
for this reason: three candidate plans is three times the planning cost, three times the execution
cost, and three lineages that can each storm. The guards must be per-lineage, not global, or one
candidate's storm consumes the others' budget.

**Plans-per-goal is the metric that predicts cost.** It is a small integer, it is cheap to record,
and it correlates with total run cost more tightly than step count does. A goal type whose median
plans-per-goal drifts from 1 to 2 has a decomposition problem that will show up in the bill about a
week before it shows up in outcomes.

---

## 13. Production Engineering

### 13.1 The four numbers

- **Plans per goal (median and p95).** The headline. A median above 1.2 means initial plans are
  routinely wrong; a p95 above 3 means some goal type is not decomposable by the current planner.
- **Response distribution: retry / repair / replan.** A system with no repairs is a system where
  repair was never implemented, and every one of those failures paid the thirty-times cost.
- **Contract evaluation rate.** The fraction of completed nodes whose contract was actually
  evaluated. It should be near 1. Anything lower means contracts are being written that cannot run,
  and those steps are unverified regardless of what the plan claimed.
- **`replan.refused` count.** Every occurrence is a run that failed cleanly instead of burning
  budget. Rising is not necessarily bad; rising in one goal type is a decomposition bug with an
  address.

### 13.2 The review question

For any change to this subsystem: **what new information does this give the planner that it did not
have?**

Most proposed improvements to planning are proposals to think harder with the same inputs — a longer
reasoning budget, a better instruction, another candidate. The cold open is the general case of why
that fails. A replan with the same inputs produces the same plan, and no amount of additional effort
changes a function's output on unchanged arguments. Improvements that add an input (the failure
record, a fresh belief, a contract result) work. Improvements that add effort mostly do not.

### 13.3 Teaching this to a new engineer

Give them the cold open and ask for a fix. The first answer is always "detect that the plans are
identical and stop." That is a real improvement and it is a guard, not a fix — it stops the bleeding
without addressing why the second plan was identical to the first.

The second answer is the one to wait for: the planner was called with the same arguments. Once
someone has said that out loud, the entire chapter follows, including why `plan()` takes `failure`
as a required parameter.

---

## 14. Relation to AHE

`[AHE App. C]` Contract-first planning is the source's, and this chapter takes it further than the
source needs to. There it is an alignment technique: writing checks first keeps a harness honest
about what it is optimising. Here it is load-bearing infrastructure — §2.2 derives it as the
precondition for classifying a failure at all, which makes it the thing that decides whether a
production system can recover rather than a technique for improving evaluation fidelity.

`[AHE App. C.1]` Evaluator-isomorphic validation — checking against the same criteria the evaluator
will use — is the same idea aimed at a different target. Its risk is worth naming: a contract that
is isomorphic to the evaluator's check optimises for the evaluator, and if the evaluator is
imperfect the plan inherits its blind spots exactly. The mitigation is Chapter 41's, and it is not
solved by anything in this chapter.

`[INF]` The replan guard has a direct analogue one level up. An evolution loop that proposes a
harness edit, measures no improvement, and proposes again from unchanged evidence is running the
cold open at a larger grain and a higher cost. Chapter 44 needs the same invariant: **a proposal
with no new evidence is refused.**

---

## 15. Industry Perspective

**`[BP]` ReAct-style step-at-a-time remains the right baseline and is under-credited.** It has no
structural failure mode, because it has no structure to be wrong. Everything in this chapter is
paying for the two properties §2.2 identifies — approvability and parallelism — and a system needing
neither should not pay.

**`[BP]` Classical planning's search assumes an evaluation function this domain does not have.**
STRIPS-style planners, hierarchical task networks, and their descendants all rest on cheap state
evaluation. Importing the search without the evaluator produces a system that explores confidently
in a space it cannot score, which is worse than not exploring.

**`[INF]` Tree-of-thought and its relatives are search over reasoning, not over plans.** They can
improve the quality of a single decomposition, and they are orthogonal to everything here. Conflating
them with plan search is common and leads to systems that generate many plans and select among them
by asking the model which it likes.

**`[DAR §8.3]`** The steer-forces-replan rule is specified, and this chapter's contribution is
locating the boundary precisely: repair may not receive the goal, so the distinction is enforced by a
function signature rather than by discipline.

**`[FUT]` Learned failure classification is the obvious next step and is unexplored.** The classifier
in §5.5 is hand-written rules over an error taxonomy, and it is almost certainly leaving accuracy on
the table. The blocker is not modelling — it is that hardly anyone records failure classifications as
labelled data, so there is nothing to learn from. Recording them is cheap and nobody does it.

---

## 16. Key Takeaways

1. **A replan that consumes no new information is a retry with extra steps.** The planner is a
   function; the same arguments produce the same plan. Make `failure` a required parameter and the
   cold open becomes unwritable.
2. **There are three responses, not two.** Retry, repair, replan, at roughly 1x, 3x, and 30x. Most
   systems lack repair, which forces the entire middle of the distribution into the expensive column.
3. **No plan is ever edited.** Repair mints a new plan in the same lineage and is cheap because the
   executed prefix carries by identity hash, not because immutability was relaxed.
4. **Contracts are written at plan time and cannot be model-judged.** A step whose postcondition
   cannot be checked deterministically is under-decomposed, and that is the whole stopping rule.
5. **Search needs an evaluation function you do not have.** It pays only where a cheap deterministic
   verifier exists and the candidates are pure. Outside that band, plan once and repair.
6. **Decomposition depth is mechanical.** Stop when every step has a checkable postcondition and
   fits one context assembly. Further decomposition buys bookkeeping.
7. **Plans per goal is the number to watch.** It is a small integer, free to record, and it moves
   before cost and long before outcomes.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Plan lineage** | The chain of plans derived from one unchanged goal, which is what makes the repair-versus-replan guard answerable. | `[INF]` | Ch 27, Ch 30 |
| **Repair** | Re-deriving a plan's unexecuted tail while carrying the executed prefix by identity hash, at roughly a tenth the cost of replanning. | `[INF]` | Ch 27 |
| **Replan** | Minting a new lineage because the decomposition itself was wrong, permitted only when the failure record carries information the last one did not. | `[DAR]` | Ch 30 |
| **Failure record** | The structured account of what died, its contract, and its classification — the input whose absence causes replan storms. | `[INF]` | Ch 27, Ch 34 |
| **Contract** | A deterministic postcondition attached to a step at plan time, immutable thereafter, and never evaluated by a model. | `[AHE]` | Ch 28, Ch 41 |
| **Contract-first planning** | Deriving postconditions before steps, which makes under-decomposition impossible by construction. | `[AHE]` | Ch 41 |
| **Stopping rule** | Decompose until every step has a checkable postcondition and fits one context assembly, then stop. | `[INF]` | Ch 29 |
| **Failure classification** | Sorting a failure into transient, asserted, or structural, which selects among retry, repair, and replan. | `[INF]` | Ch 27 |
| **Replan storm** | Repeated identical replans from unchanged inputs, structurally impossible once a replan without new information is refused. | `[INF]` | Ch 35 |
| **Plans per goal** | The count of plans a lineage consumed, the cheapest available measure of decomposition quality. | `[INF]` | Ch 41 |
| **Least-to-most** | Decomposing into sub-goals before steps, which earns its extra model call when a flat plan's step costs are wildly uneven. | `[BP]` | Ch 41 |

---

**Next:** Chapter 27 — *Failure, Recovery, and Rollback.* This chapter classified failures in order
to choose a planning response; the next one treats the failure table itself as a design artefact,
and asks the harder question of what to do about the effects that already happened — where
compensation and rollback are different operations, and only one of them is usually available.
