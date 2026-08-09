```
  Level 3 · Chapter 21
  DURABLE EXECUTION
  Requires   C5 The Five Nouns, C8 Lifecycles, C14 The Tool Execution
             Engine, C17 The State Manager, C18 The Runtime Loop
  Unlocks    C27 Failure and Recovery, C32 Distributed Execution,
             C40 Testing, C47 Attribution
  Diagrams   Full (9)
```

# Chapter 21 — Durable Execution

---

## 1. Motivation

### 1.1 Cold open

A customer reports that Atlas did something inexplicable on `acme/platform`. The engineer does the
obvious thing: replays the run to watch it happen.

The replay succeeds. She runs it again; it fails, differently. A third time, it succeeds again.

Two hours later, three duplicate pull requests appear on the customer's repository, each opened by a
replay.

The replay was not a replay. It re-executed every step from the beginning — including the model
calls, which returned different samples each time, and including `repo.open_pull_request`, which does
exactly what it says. What the team had built was a *re-run under the original goal*, which is a
useful thing and is not what anybody meant when they typed `replay`.

The word was doing the damage. Everyone assumed replay meant "show me what happened". It meant "do it
all again".

### 1.2 In plain language

Durable execution is the property that a run survives things going wrong: a process being killed, a
machine disappearing, a deploy landing mid-flight. The run picks up from where it was rather than
starting over.

Three chapters have already built most of it. Checkpoints record where a run got to, leases decide
who may continue it, and identity decides whether a piece of work has already been done. This chapter
is what those add up to, and it spends most of its length on one distinction the cold open shows is
easy to lose.

**Resuming** is continuing a run that was interrupted. It reuses everything already done and carries
on from the next step. Nothing is repeated, nothing is re-paid for, and nothing touches the outside
world twice.

**Re-running** is starting the same goal again from the beginning. It does everything afresh —
different model outputs, real effects repeated. Sometimes that is exactly what you want.

**Replaying** is neither. It is stepping through a recorded run without executing anything, to see
what happened. It touches nothing and costs nothing.

Three operations, and the cold open is a system that offered one word for all three.

### 1.3 Why this chapter exists

Level 2 built the mechanisms; this chapter states the guarantee they produce, tests it, and is honest
about where it stops.

`[DAR §6.1]` The guarantee is: **a crash loses at most one in-flight step.** That is a stronger claim
than "the run survives", and it is worth stating precisely because everything in Level 3 is
calibrated against it — Chapter 27's retry policy, Chapter 32's partition behaviour, and Chapter 40's
replay harness all assume it holds.

`[INF]` It is also the chapter where the honest limits appear. Durable execution here is built from
a database and a discipline, not from a durable-execution engine, and §12.3 is about when that
stops being the right trade.

### 1.4 What previous framings got wrong

**"Replay means run it again."** The cold open. Three distinct operations wearing one word, and the
one people assume is the safe one is the one that opens duplicate pull requests.

**"Idempotency means the tool is safe to retry."** Almost. Idempotency is a property of the
*identity* plus the tool, not of the tool alone. `repo.apply_patch` called twice with the same
activity id is safe because the second call never happens; called twice with different ids it applies
twice, however carefully it was written.

**"Durability is a database feature."** `[INF]` Durability of a *write* is a database feature.
Durability of an *execution* is a design property: it requires that every point at which the system
can stop is a point it can be resumed from, which is a statement about where checkpoints are, not
about the storage engine.

**"Adopt an engine instead."** `[DAR §17]` A reasonable position, and §12.3 says when it becomes
the right one. The argument for building it is that the parts you need are three columns and a
discipline; the argument against is that the parts you need *next* are considerable.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A ship's log, versus the ship's wake.

A log is written as you go: position, heading, and what was done, entered at fixed intervals. If the
watch changes — or the officer collapses — the next person reads the log and continues from the last
entry. They do not re-sail the voyage. The log is not a description of the journey; it is the
mechanism by which the journey survives its crew.

The wake is what actually happened, and it is gone. You cannot re-enter it and you certainly cannot
un-sail it.

Those are resume and effect. Resuming means reading the log and carrying on. And the reason you can
never "start again" is the wake: the ship has already been where it has been, and in this
system that means the pull request exists, the branch was pushed, the money was spent.

The log's interval is the design decision. Entries every hour mean up to an hour of position
uncertainty after a handover. Entries every few minutes cost more ink and lose almost nothing.
Chapter 17 made the ink cheap — roughly five milliseconds — which is why the interval here is *every
step*.

**Where the analogy breaks.** A ship's log records a journey through a world that does not care what
is written down. Here, the log and the world are coupled in a specific and dangerous way: the log
records that a pull request was opened, and if that entry is lost, the resumed run will open a second
one. The wake and the log can disagree.

`[INF]` That disagreement is the entire residual risk of this chapter, named honestly in Chapter 14
§6.1 and again in §5.5 here. Durable execution makes the log reliable and the log-versus-world gap
small. It does not close it, because no client-side mechanism can make an external effect and a local
write atomic.

### 2.2 Why one guarantee, stated precisely

```
  1. A worker can stop at any instant, without warning.
  2. So the run's position must be recoverable from durable state
     alone -- nothing in the dead process is available (Ch 8).
  3. Recovery therefore resumes from the last CHECKPOINT, since that
     is the last durable position.
  4. Work done since that checkpoint is not recorded, so it will be
     attempted again.
  5. If that work was a model call, attempting it again costs money.
     If it was effectful, attempting it again touches the world twice.
  6. So the checkpoint interval bounds the LOSS, and the identity
     ledger bounds the REPETITION -- two different mechanisms for two
     different problems.
  7. Making the interval one step (Ch 17) bounds loss at one step.
     Making identity plan-time (Ch 10) bounds repetition at the
     work not yet recorded.
  8. Therefore: a crash loses at most one in-flight step, and repeats
     at most the effects of that one step.
```

Step 6 is the pairing that matters and is routinely collapsed. `[INF]` Checkpointing frequently
without identity means a resumed run re-pays for everything since the checkpoint. Identity without
frequent checkpointing means a resumed run has to re-derive a great deal of position before it finds
work it can reuse. The guarantee needs both.

### 2.3 Three operations, three meanings

`[INF]` The vocabulary the cold open lacked:

| | Resume | Re-run | Replay |
|---|---|---|---|
| Purpose | continue an interrupted run | do the goal again | inspect what happened |
| Executes anything? | the remaining steps | everything | **nothing** |
| Uses recorded results? | yes, by identity | no — new ids | reads them only |
| Model calls | only the unrecorded ones | all of them, new samples | none |
| External effects | only the unrecorded ones | **all of them, again** | **none** |
| Costs money | only the remainder | full price | nothing |
| Same plan id? | yes | no — a new run entirely | yes |
| Where | this chapter | Chapter 41's rollouts | Chapter 40's harness |

`[INF]` The row to memorise is *external effects*. Resume repeats at most the last in-flight step.
Re-run repeats everything. Replay repeats nothing. The cold open's `replay` command was doing the
middle one under the name of the last one.

### 2.4 The mental model to carry

> **Durability is not that nothing is lost. It is that the amount lost is bounded, known, and the
> same every time.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  THE THREE MECHANISMS, and what each bounds                  |
  |                                                              |
  |  +---------------------+   bounds LOSS                        |
  |  | CHECKPOINTS  Ch 17  |   -> at most one in-flight step      |
  |  +----------+----------+                                      |
  |             | (1) every step, ~5 ms                           |
  |             v                                                 |
  |        [[ runs ]]                                             |
  |                                                              |
  |  +---------------------+   bounds REPETITION                  |
  |  | IDENTITY     Ch 10  |   -> recorded work is never redone   |
  |  +----------+----------+                                      |
  |             | (2) hash minted at PLAN time                    |
  |             v                                                 |
  |     [[ activities ]]  <-- the ledger; this chapter's table    |
  |                                                              |
  |  +---------------------+   bounds NON-DETERMINISM             |
  |  | QUARANTINE   Ch 3   |   -> confined to activities alone    |
  |  +----------+----------+                                      |
  |             | (3)                                             |
  |             v                                                 |
  |   +==================+  the ONLY place a result can           |
  |   | ACTIVITY         |  differ between two executions          |
  |   +==================+                                        |
  +--------------------------------------------------------------+
                    |                         |
              (4)   v                   (5)   v
        +~~~~~~~~~~~~~~~~~+        +~~~~~~~~~~~~~~~~~~~~+
        | model, tools    |        | THE WORLD           |
        | (Ch 13, Ch 14)  |        | effects that no     |
        +~~~~~~~~~~~~~~~~~+        | rollback can undo   |
                                   +~~~~~~~~~~~~~~~~~~~~+

  Figure 21.1 -- Three mechanisms, three bounds
                 (D1 High-Level Architecture)

  (1) Ch 17: the checkpoint interval IS the loss bound
  (2) Ch 10: minted before execution, or it cannot prevent
      a duplicate (Ch 14 section 4.2)
  (3) Ch 3 MM4: everything outside an activity is deterministic
      given the same recorded results
  (4) where non-determinism enters
  (5) where irreversibility enters -- and these are different
      properties that happen to share a boundary
```

`[INF]` Wires 4 and 5 leaving the same box is worth pausing on. Non-determinism and irreversibility
are independent — a model call is non-deterministic and reversible, a `git push` is deterministic and
irreversible — and both are confined to activities. That is not a coincidence: an activity is defined
as the boundary at which the runtime stops being able to reason about what happens.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  THE ACTIVITY LEDGER -- this chapter's one new table

  +--------------------------------------------------------------+
  | activity_id   PRIMARY KEY                                     |
  |   = hash(run_id, plan_id, step_id, tool_id, input_digest)     |
  |   minted at PLAN time (Ch 10 section 5.1)                      |
  |                                                              |
  | state         PENDING | CLAIMED | RECORDED | DEAD             |
  | result        jsonb, NULL until RECORDED                      |
  | attempts      int                                             |
  | lease_owner   text          <-- an activity has its own lease |
  | lease_until   timestamptz       independent of the run's      |
  | cost_cents    int                                             |
  | effect_log    jsonb         <-- what actually changed (Ch 14) |
  +--------------------------------------------------------------+

  THE LOOKUP, before any dispatch (Ch 14 section 4, step 4)

  +--------------------------------------------------------------+
  |  SELECT state, result FROM activities WHERE activity_id = $1  |
  |                                                              |
  |   RECORDED -> return the result. No call. No cost.            |
  |               This is RESUME.                                 |
  |                                                              |
  |   CLAIMED, lease live -> another worker has it. Wait or       |
  |               yield; do NOT dispatch.                          |
  |                                                              |
  |   CLAIMED, lease expired -> the previous attempt died. The     |
  |               effect MAY have happened (section 5.5).          |
  |               Claim it, increment attempts, dispatch only      |
  |               if PURE or if attempts < cap and the tool         |
  |               declares itself safe.                            |
  |                                                              |
  |   PENDING or absent -> claim and dispatch. First attempt.      |
  |                                                              |
  |   DEAD -> attempts exhausted. Return the failure; the          |
  |               planner replans (Ch 10 section 5.4).             |
  +--------------------------------------------------------------+

  Figure 21.2 -- The ledger and the lookup
                 (D2 Low-Level Architecture)
```

### 4.1 An activity has its own lease, and that is not redundant

`[INF]` The run has a lease (Chapter 17) and so does each activity, which looks like duplication until
you consider durations. A run's lease is renewed every step, so it is sized for one step. An activity
may run for minutes — a long shell command, a slow model call — and its lease must cover that.

They also expire independently, and the combination is what the sweeper acts on. A run whose lease
expired mid-activity is reclaimed; the activity's lease expires separately and reveals whether the
work was in flight when it happened.

```
                                                            LAYER VIEW

  Components. Almost all borrowed; one new.

   ProposedToolCall (Ch 10, carrying its activity_id)
        |
        v
   +----+------------+       +---------------------+
   | Identity        |       | ACTIVITY LEDGER     |
   | verifier        |------>|  lookup             |  <-- new here
   |  recompute the  |       |  claim              |
   |  hash; compare  |       |  record             |
   +-----------------+       +----------+----------+
        |                               |
        | mismatch = PARTIAL MATCH      |
        | -> anomaly, never a hit       |
        v                               v
   +----+------------+          +-------+---------+
   | Anomaly channel |          | Dispatch (Ch 14)|
   |  alert, not log |          +-------+---------+
   +-----------------+                  |
                                        v
   +-----------------+          +-------+---------+
   | Determinism     |<---------| Result recorder |
   | boundary        |          |  + effect_log   |
   |  (Ch 3 MM4)     |          +-------+---------+
   +-----------------+                  |
                                        v
                              +---------+---------+
                              | Replay reader     |
                              |  Ch 40; executes  |
                              |  NOTHING          |
                              +-------------------+

  Figure 21.3 -- Durable execution components
                 (D3 Component Diagram)
```

`[INF]` The Anomaly channel exists because of one specific case §5.3 covers: an identity that matches
on run and position but differs on plan or inputs. `[DAR §6.1]` is explicit that this must be
recorded as an anomaly and never treated as a cache hit — and routing it to an alert rather than a
log is the difference between noticing in an hour and noticing in a quarter.

---

## 5. The Guarantee

### 5.1 What "at most one in-flight step" means, exactly

`[DAR §6.1]` Unpacked, because the phrase is doing a lot of work:

| Lost on a crash | Not lost |
|---|---|
| the current step's in-memory computation | every recorded activity result |
| an in-flight activity's *local* result | the run's position, plan, and budget |
| anything since the last checkpoint | anything before it |

`[INF]` And what is **not** guaranteed, stated as plainly: an in-flight *effect* may have happened. If
the worker died between the tool changing the world and the ledger recording it, the world moved and
the ledger does not know. §5.5 is about narrowing that window and being honest that it does not close.

### 5.2 Resume, in full

```
  1. The sweeper expires the run's lease (Ch 17)
  2. Another worker claims it, reads current_step from the row
  3. The loop asks the planner for the step at that position
     -- the SAME plan, so the same activity_id (Ch 10)
  4. The ledger lookup finds RECORDED -> the result is returned
     without calling anything
  5. The loop checkpoints and moves on
```

`[INF]` Step 3 is why plan immutability (Chapter 10) is a durability property and not only a safety
one. If the plan could change during recovery, the recomputed identity would differ, the ledger would
miss, and the work would be redone. The chapter that argued for immutable plans on human-authority
grounds turns out to have been arguing for this too.

### 5.3 Partial match is an anomaly, not a hit

`[DAR §6.1]` The identity is a hash of five things. Three failure shapes:

| Match | Meaning | Action |
|---|---|---|
| All five | the same work | reuse the result |
| Run and step, different plan | a replan happened | **anomaly** — do not reuse |
| Run and step, different inputs | the plan changed underneath | **anomaly** — do not reuse |

`[INF]` The second row should be impossible, because a replan mints a new plan id and therefore new
identities for every step. So observing it means something upstream is violating Chapter 10 — the
plan was edited in place. That makes partial-match detection a *conformance check on the planner*,
which is why it alerts rather than logs.

### 5.4 The determinism quarantine

`[DAR §6.1]` Chapter 3's MM4, now a testable property:

> **Given the same recorded activity results, everything outside an activity produces the same
> outcome.**

`[INF]` That is what makes Chapter 40's hermetic replay possible at all, and it constrains the loop
in ways worth naming:

| Forbidden outside an activity | Because |
|---|---|
| reading the wall clock | two executions differ |
| generating a random value or an id | the same |
| reading environment or config directly | it may have changed |
| a network call | it is an activity by definition |
| iterating an unordered collection | order becomes execution-dependent |

The last row is the one that catches people. `[INF]` A loop over a set, producing steps in whatever
order the runtime chose, makes a replay diverge for no reason anybody will find quickly. Sorted
collections everywhere inside the quarantine is a cheap discipline with a large payoff.

### 5.5 The window that does not close

Chapter 14 §6.1 named it; here is its size and its mitigations.

```
  t=0   tool begins
  t=1   the world changes  (the PR is opened)
  t=2   the ledger records the result   <-- the window is t=1 to t=2
  worker dies at t=1.5
     -> the world moved; the ledger says CLAIMED with no result
     -> a resumed run finds no result and may dispatch again
```

`[INF]` Four mitigations, none of which closes it:

1. **The effect event shares the domain's transaction** (Chapter 9 §5.2). So for effects that go
   *through* your own domain, the event survives and the run learns what happened — this closes the
   window for domain commands and not for third-party calls.
2. **Effectful tools are asked to be idempotent on their own terms.** `open_pull_request` that
   detects an existing identical PR and returns it turns a duplicate into a no-op.
3. **Effectful activities are never retried automatically** (Chapter 14 §5.3). The second attempt is
   a planner decision made with the situation visible.
4. **The attempt count is visible.** A resumed effectful activity with `attempts > 0` is presented to
   the planner as such, so "this may already have happened" is information rather than a surprise.

`[INF]` The honest summary: for effects inside your own domain, the outbox closes the window. For
effects on third-party systems, it does not, and the residual is real. This is the same shape as
Chapter 13's lost-completion double-billing, and it has the same cause — no client-side mechanism
makes an external action and a local write atomic.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  worker A    ledger    tool     world     worker B    runs row
     |           |        |        |          |           |
  STEP 7, effectful, activity_id = 8ac31d               |
     |-- lookup 8ac31d ->|        |          |           |
     |<-- absent --------|        |          |           |
     |-- claim ---------->| CLAIMED, lease 5m           |
     |-- dispatch ------->|------->|          |           |
     |           |        |  PR #412 OPENED  |           |
     |           |        |        |          |           |
     |    X  worker A dies here. The window.  |           |
     |           |        |        |          |           |
     |     (run lease expires; sweeper clears it)         |
     |           |        |        |          |-- claim ->| v14
     |           |        |        |          |           |
     |           |<-- lookup 8ac31d ----------|           |
     |           |--> CLAIMED, lease EXPIRED, attempts=1  |
     |           |                            |           |
     |     effectful + attempts>0 -> NOT auto-retried     |
     |     the planner is told: "may already have         |
     |     happened", with the effect_log empty           |
     |           |                            |           |
     |     the tool is idempotent on its own terms:       |
     |     open_pull_request finds PR #412 already open   |
     |     for this branch and returns it                 |
     |           |<-- record: OK, existing=#412 ----------|
     |           |                            |-- checkpoint -> v15

  Contrast -- a PURE step in the same position:
     lookup finds CLAIMED/expired, attempts=1, effect=pure
     -> re-dispatched immediately. Nothing was lost but time.

  Figure 21.4 -- The window, and how it is narrowed
                 (D4 Sequence)
```

### 6.1 What made that recovery work

Three things, none of them the ledger alone.

**The identity was unchanged**, because the plan was unchanged. Worker B recomputed `8ac31d` and
found the row.

**The tool was idempotent on its own terms.** Nothing in the runtime could have prevented a second
PR; the tool declining to open one is what did.

**The attempt count travelled.** The planner saw `attempts=1` on an effectful step and could have
chosen differently — asked a human, verified first, given up. The runtime did not decide for it.

`[INF]` If the tool had not been idempotent, the outcome would have been a duplicate PR and a correct
runtime. That is the residual, and no amount of ledger design removes it.

```
                                                             TIME VIEW

  The durable-execution cycle, per step.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | recompute identity   |  Ch 10; from the CURRENT plan |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | ledger lookup        |                               |
   +----+-----------------+                               |
        |                                                 |
        +-- RECORDED ------------------> E1 reuse; no cost |
        |                                                 |
        +-- partial match -------------> E2 ANOMALY; alert |
        |                                 do not reuse     |
        |                                                 |
        +-- CLAIMED, live -------------> E3 yield; another |
        |                                 worker has it    |
        v                                                 |
      /   \                                               |
     /claimed\ expired -> +---------------------+         |
     \expired?/           | effectful?          |         |
      \      /            +----+-----------+----+         |
        | no                   | yes       | no           |
        |                      v           v              |
        |              +-------+----+  re-dispatch        |
        |              | attempts   |                     |
        |              | > 0 -> tell|                     |
        |              | the planner|                     |
        |              +-------+----+                     |
        |                      |                          |
        v                      v                          |
   +----+-----------------+    |                          |
   | claim + dispatch     |<---+                          |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     /result \ no --> E4 DEAD after the attempt cap        |
     \ ok?   /                                             |
      \     /                                              |
        | yes                                              |
        v                                                  |
   +----+-----------------+                                |
   | record + effect_log  |                                |
   +----+-----------------+                                |
        |                                                  |
        v                                                  |
      E5 recorded; the loop checkpoints (Ch 18)             |

  Exits:
    E1  replay hit: reused, zero cost -- the common case
    E2  partial match: a planner conformance failure (5.3)
    E3  another worker holds it; yield rather than duplicate
    E4  attempts exhausted -> DEAD; the planner replans
    E5  first execution, recorded

  Figure 21.5 -- The lookup-dispatch-record cycle (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

  An activity's states. Independent of the run's (Ch 8) and of the
  episode's (Ch 18).

            +---------------------+
            | {{ PENDING }}       |  identity minted at plan time;
            +----------+----------+  nothing attempted
                       | claimed
                       v
            +---------------------+
            | {{ CLAIMED }}       |  own lease, own expiry
            +--+-------+-------+--+
               |       |       |
       result  |       |       | lease expired
               |       |       v
               |       |   +---+-----------------+
               |       |   | {{ CLAIMED }}       |  reclaimable;
               |       |   |   attempts + 1      |  the effect MAY
               |       |   +---+-----------------+  have happened
               |       |       |
               |       | attempts > cap
               |       v
               |   +---+-----------------+
               |   | {{ DEAD }}          |  visible, not blocking
               |   +---------------------+
               v
            +---------------------+
            | {{ RECORDED }}      |  TERMINAL. The result is the
            +---------------------+  answer, forever.

  Illegal, and enforced:
    * RECORDED -> anything          a recorded result is final; this
                                    is what makes resume free
    * dispatch without a lookup     Ch 14 section 4 ordering
    * effectful auto-retry          section 5.5, mitigation 3
    * reusing a partial match       section 5.3

  Figure 21.6 -- An activity's states (D6 State Diagram)
```

### 7.1 RECORDED is terminal, and that is the whole feature

`[INF]` Once a result is written, it is the answer forever — for this run, this plan, this step, these
inputs. No expiry, no invalidation, no cache semantics.

That is unusual and deliberate. A cache is a performance optimisation whose entries may be discarded;
the activity ledger is a *correctness* mechanism whose entries may not. Adding a TTL to it, which
looks like sensible hygiene, reintroduces the possibility of paying twice and of repeating an effect.

Retention is bounded by the run's own retention (Chapter 37), not by the ledger's usefulness.

### 7.2 Where the state lives

| State | Table | Lifetime |
|---|---|---|
| run position, plan, budget | `runs` | Chapter 17 |
| step sequence | `run_steps` | append-only |
| **activity results** | **`activities`** | **terminal once recorded** |
| what actually changed | `effect_log` on the activity | audit |
| what the model saw | trace store (Chapter 16) | retention policy |

`[INF]` Note that the ledger holds results and not reasoning. Reconstructing *why* a step was taken
is Chapter 16's job; the ledger's only question is whether this exact work has been done.

---

## 8. Internal APIs

```python
from typing import Protocol


class ActivityLedger(Protocol):
    """Bounds repetition. Checkpoints bound loss; these are different
    mechanisms for different problems (section 2.2)."""

    async def lookup(self, activity_id: ActivityId) -> LedgerEntry | None:
        """Called before EVERY dispatch (Ch 14 section 4).

        A RECORDED entry is returned and the tool is not called: that is
        resume, and it is the mechanism's entire purpose.
        """

    async def claim(
        self, activity_id: ActivityId, worker_id: str, lease: timedelta
    ) -> ClaimOutcome:
        """Conditional, like Ch 17's run claim. Returns ALREADY_CLAIMED
        when another worker holds a live lease -- yield, do not
        dispatch."""

    async def record(
        self, activity_id: ActivityId, result: ToolResult, cost_cents: int
    ) -> None:
        """Terminal. There is deliberately no update and no invalidate:
        a recorded result is the answer forever (section 7.1)."""

    async def report_partial_match(
        self, expected: ActivityId, found: PartialMatch
    ) -> None:
        """Never a cache hit. Routed to an alert, because it means the
        planner edited a plan in place (section 5.3)."""
```

`[INF]` The absence of `invalidate` is the enforceable form of §7.1. An interface offering it would be
used the first time somebody wanted to force a step to re-run during debugging — and the correct tool
for that is a re-run under a new plan id, which produces new identities and leaves the record intact.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class ActivityState(StrEnum):
    PENDING = "pending"
    CLAIMED = "claimed"
    RECORDED = "recorded"      # terminal
    DEAD = "dead"


class ExecutionMode(StrEnum):
    """The vocabulary the cold open lacked (section 2.3)."""
    RESUME = "resume"          # continue; reuse by identity
    RERUN = "rerun"            # new run, new ids, effects repeat
    REPLAY = "replay"          # execute NOTHING (Ch 40)


@dataclass(frozen=True)
class LedgerEntry:
    activity_id: ActivityId
    state: ActivityState
    result: ToolResult | None
    attempts: int
    cost_cents: int
    effect_log: tuple[EffectRecord, ...]   # what actually changed
    first_attempted_at: datetime
    recorded_at: datetime | None


@dataclass(frozen=True)
class PartialMatch:
    """Same run and position, different plan or inputs. An anomaly."""
    expected_id: ActivityId
    found_id: ActivityId
    differing_field: str        # plan_id | input_digest
```

`[INF]` `ExecutionMode` being an enum in the codebase rather than a word in a runbook is the cold
open's structural fix. A CLI that takes `--mode` from this enum cannot offer an operation whose
meaning is ambiguous, and the three values force whoever adds the fourth to think about what it does
to the world.

`effect_log` is what lets §6.1's recovery be honest: an empty log on a claimed-and-expired effectful
activity means the runtime genuinely does not know whether the effect happened.

---

## 10. Communication

```
                                                            LAYER VIEW

  lookup       loop   ====> [[ activities ]]   ~200 B, EVERY dispatch
  claim        loop   ====> [[ activities ]]   ~300 B
  result       loop   ====> [[ activities ]]   ~1-64 KB (truncated,
                                                 Ch 14 section 5.5)
  effect_log   loop   ====> [[ activities ]]   ~1-5 KB
  domain event loop   ====> [[ outbox ]]       ~1 KB, SAME txn

  On resume, per reused step:
     one indexed lookup, ~200 B  --  versus a model call at
     ~50-200 KB and real money. The ledger pays for itself on
     the first recovery.

  Figure 21.7 -- What durability costs (D7 Data Flow)
```

```
                                                             TIME VIEW

  loop ----------> ledger      lookup BEFORE any dispatch
  ledger --X       the tool    a RECORDED entry means no call at all
  loop ----------> tool        only when the ledger says to
  sweeper -------> ledger      expire activity leases (Ch 8)
  loop --X         invalidate  REFUSED: recorded is terminal (7.1)
  partial match --> alert      never to a cache-hit path (5.3)

  Figure 21.8 -- Who decides that work happens twice
                 (D8 Control Flow)
```

```
                                                             TIME VIEW

  << activity.recorded >>       ....> result and settled cost; the
                                      input to Ch 35
  << activity.dead_lettered >>  ....> attempts exhausted; visible,
                                      not blocking (Ch 27)
  << identity.partial_match >>  ....> a planner conformance failure;
                                      ALERTS (section 5.3)

  NOT events:
    lookups and hits        the common case; telemetry
    claims                  ownership churn
    the result itself       a RESULT in the ledger, not an event

  Figure 21.9 -- What durable execution makes durable
                 (D9 Event Flow)
```

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 22 Event Spine | the effect event shares the domain transaction | mitigation 1 of §5.5 |
| Ch 27 Failure | attempt caps, DEAD, and the sweeper | the failure table's spine |
| Ch 32 Distributed | identity is the coordination-free dedup | many workers add nothing |
| Ch 40 Testing | the determinism quarantine | hermetic replay depends on §5.4 |
| Ch 41 Evaluation | re-run semantics for rollouts | a rollout is a re-run, not a resume |
| Ch 47 Attribution | cost per activity, per run | cost-normalised verdicts |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Replay that re-executes | one word for three operations | duplicate effects from debugging | the `ExecutionMode` enum — the cold open |
| Identity at dispatch | computed when the tool is called | duplicate spend under concurrency | mint at plan time (Ch 10) |
| Partial match reused | matching on run and step only | wrong results returned confidently | anomaly, alert, never reuse (§5.3) |
| Ledger with a TTL | treating it as a cache | intermittent double-spend after expiry | RECORDED is terminal (§7.1) |
| Effectful auto-retry | uniform retry policy | duplicate external effects | pure only (Ch 14 §5.3) |
| Non-determinism outside an activity | clock, random, set iteration | replays that diverge | the quarantine (§5.4) |
| Plan edited in place | violating Ch 10 | partial-match anomalies appearing | fix the planner; the anomaly is the signal |
| No attempt count to the planner | runtime decides silently | effects repeated without anybody choosing | surface `attempts` (§6.1) |
| Checkpoint interval widened | "every step is wasteful" | more lost on each crash | the interval IS the loss bound |
| Assuming the window is closed | trusting the ledger absolutely | rare duplicate third-party effects | it is a residual; say so (§5.5) |

`[INF]` Row six is the one that only appears when you first build Chapter 40's replay harness, often
months later. A `set` iterated in the loop, a `uuid4()` for a correlation id, a `datetime.now()` in a
log line that becomes part of a hash — each makes replay diverge, and the divergence is reported as
"replay is broken" rather than "the quarantine leaks". Sorting collections and injecting a clock from
day one costs almost nothing.

---

## 12. Scalability

### 12.1 The ledger is read far more than written

One lookup per dispatch, one write per completion, and lookups outnumber writes whenever anything
recovers. Both are primary-key operations on a table whose key is a hash — well-distributed by
construction, which is convenient and also means no useful range scans exist on it.

| Quantity | Scales with | Note |
|---|---|---|
| Lookups | dispatches | every one, indexed |
| Writes | completions | one per activity |
| Row count | activities across all runs | the largest transactional table |
| Result size | truncation policy (Ch 14) | why §5.5 of that chapter matters here |

`[INF]` The ledger will be your biggest non-trace table. Its size is bounded by run retention rather
than by anything this chapter controls, which is the argument for Chapter 14's truncation happening
*before* the record.

### 12.2 Recovery cost is proportional to what was lost

`[INF]` A resumed run pays one indexed lookup per already-completed step to discover it can skip it.
For a run interrupted at step 38, that is 37 lookups — roughly ten milliseconds — against 37 model
calls it does not make. The asymmetry is the point, and it is why nobody optimises resume.

### 12.3 When to stop building this and buy an engine

`[DAR §17]` The honest threshold, and it is a real one.

What you have here is durable execution built from three columns and a discipline. It handles crash
recovery, deduplication, and bounded loss. What it does not handle:

| You need | This chapter | An engine <!-- lint-ok: naming the product category --> |
|---|---|---|
| Crash recovery, dedup | yes | yes |
| Durable timers at scale | a `wake_at` column and a sweeper | first-class |
| Long-running signals and correlation | Chapter 7's signals | first-class |
| Versioned execution across deploys | Chapter 38's pinning | first-class, with migration |
| Cross-region durability | **no** | some |
| Visual execution history | build it | included |

`[INF]` The recommendation: build it if your needs stop at the top three rows, which most agent
runtimes do. Adopt an engine when you find yourself building versioned execution migration or
cross-region durability — both are large, both are solved elsewhere, and neither is where an agent
product's differentiation lives.

The cost of switching later is real but bounded, because the concepts transfer: activity identity,
checkpoints, and the determinism quarantine are what every such engine is built from.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Ledger hit rate on resume | the mechanism working | a drop means identities are changing |
| Partial-match anomalies | planner conformance (§5.3) | **any**, immediately |
| Effectful activities with `attempts > 0` | the §5.5 window, in production | reported; a rise is worth investigating |
| DEAD activities per hour | attempt caps being hit | rising |
| Recorded-result size p99 | truncation working upstream | above the policy |
| Replay divergence rate | the quarantine leaking (§5.4) | any, once Ch 40 exists |
| Cost avoided by resume | the mechanism's value, quantified | reported |

`[INF]` The last row is worth building because durable execution is invisible when it works. "This
month, resume avoided $N of re-execution" is the only number that makes the ledger's existence
legible to anybody outside the team.

### 13.2 The test that catches the cold open

```python
async def test_resume_reuses_and_replay_executes_nothing(
    runtime: Runtime, world: FakeWorld
) -> None:
    run = await runtime.submit(goal_with_effectful_step)
    await runtime.advance_until_step(run, 8)
    effects_before = world.effect_count()
    cost_before = await runtime.cost(run)

    await runtime.kill_worker()
    await runtime.recover_and_finish(run)          # RESUME

    # Resume repeats nothing already recorded.
    assert world.effect_count() == effects_before + expected_remaining
    assert await runtime.cost(run) < cost_before * 1.2

    # Replay executes NOTHING. This is the assertion the cold open
    # needed: no model call, no tool call, no effect.
    world.reset_counters()
    trace = await runtime.replay(run)              # REPLAY
    assert world.effect_count() == 0
    assert world.model_call_count() == 0
    assert trace.steps == expected_step_count
```

`[INF]` The `replay` assertions are the ones that would have failed against the cold open's
implementation on the first run, in a test taking under a second. The reason nobody wrote them is
that "replay" sounded self-evidently safe.

### 13.3 The determinism check

```python
async def test_nothing_outside_an_activity_is_non_deterministic(
    runtime: Runtime, clock: FakeClock
) -> None:
    """Same recorded results in, same execution out (section 5.4)."""
    recorded = await runtime.execute_and_record(goal)

    first = await runtime.replay(recorded.run_id)
    clock.advance(hours=5)                  # the clock must not matter
    second = await runtime.replay(recorded.run_id)

    assert first.step_sequence == second.step_sequence
    assert first.activity_ids == second.activity_ids
```

`[BP]` Advancing the clock between replays is the cheap way to catch the most common quarantine leak,
and it costs one line.

---

## 14. Relation to AHE

Durable execution is what makes an evolution iteration a measurement rather than an anecdote.

**A rollout must be a re-run, never a resume.** `[INF]` Chapter 41 scores `pass@1` across k rollouts,
and a rollout that resumed from a previous attempt's recorded activities would be measuring a
different thing entirely — cheaper, faster, and not what the benchmark claims. §2.3's vocabulary is
therefore load-bearing for evaluation: rollouts are re-runs, with new run ids and new identities.

**Replay is what makes a rollback trustworthy.** Chapter 47 reverts an edit when its predictions
fail. `[INF]` Trusting that revert requires knowing the harness returned to a known state, and
Chapter 40's hermetic replay is the check — which exists only because of §5.4's quarantine. A loop
that cannot replay cannot verify its own rollbacks, and is then doing unverified automated changes to
production configuration.

**Cost per activity is what makes scoring honest.** `[AHE App. A]` uses tokens per trial and success
per million tokens. `[INF]` Those come from `cost_cents` on ledger rows, and Chapter 13's insistence
that abandoned calls settle at their reservation is what stops the denominator being understated.

**And the residual matters to the loop specifically.** `[INF]` §5.5's window means a small fraction
of benchmark rollouts may have repeated an external effect. On a coding benchmark that is usually
harmless; on any benchmark with real side effects it is a source of noise the loop will interpret as
signal. Chapter 41 sandboxes rollouts for exactly this reason.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the guarantee that a crash loses at most one in-flight step, activity identity
as the dedup key, partial match as an anomaly rather than a cache hit, the determinism quarantine,
and the honest guidance on when to adopt an engine rather than continue building
`[DAR §6.1, §17]`.

**`[AHE]`** Supplies the evaluation metrics whose denominators come from the ledger `[AHE App. A]`.

**`[INF]`** The handbook's own: the resume/re-run/replay vocabulary and `ExecutionMode` as its
structural fix, the pairing of checkpoints bounding loss with identity bounding repetition, the
ship's-log analogy and the observation that the log and the world can disagree, the four mitigations
of §5.5 with an explicit statement that they do not close the window, the set-iteration quarantine
leak, and the argument that resume's asymmetry is why nobody optimises it.

**`[BP]`** Idempotency keys, at-least-once delivery with dedup, and event-sourced recovery are
established practice. The contribution is naming the three operations separately and treating the
conflation as the defect it is.

**`[FUT]`** `[FUT]` The window in §5.5 is closed for domain effects by the outbox and open for
third-party ones. A general solution would need providers to accept an idempotency key for
side-effecting operations — which some do and most do not — and the handbook has no client-side
answer beyond the four partial mitigations.

---

## 16. Key Takeaways

1. **Resume, re-run, and replay are three operations.** Resume reuses by identity, re-run repeats
   everything including effects, replay executes nothing. One word for all three opened three
   duplicate pull requests.
2. **Checkpoints bound loss; identity bounds repetition.** Two mechanisms, two problems, and each
   alone leaves the other unsolved.
3. **A crash loses at most one in-flight step.** That is the guarantee, and it is worth stating
   precisely because all of Level 3 is calibrated against it.
4. **A recorded result is terminal.** No TTL, no invalidation. The ledger is a correctness mechanism
   wearing a cache's shape, and treating it as a cache reintroduces double-spend.
5. **Partial match is a planner conformance failure.** It should be impossible, so observing it means
   a plan was edited in place. Alert on it; never treat it as a hit.
6. **The quarantine leaks through small things.** A clock read, a random id, an unordered iteration —
   each makes replay diverge, and the divergence is always reported as replay being broken.
7. **The window between effect and record does not close.** The outbox closes it for your own domain
   and not for third parties. Four mitigations narrow it; the residual is real and should be named.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Durable execution** | The property that a run resumes from its last checkpoint rather than restarting, with loss and repetition both bounded. | `[DAR]` | Ch 27, Ch 32 |
| **Activity ledger** | The table keyed by activity identity that records what has already been done, so it is never done twice. | `[DAR]` | Ch 27, Ch 35 |
| **Resume** | Continuing an interrupted run, reusing recorded results by identity and repeating nothing. | `[INF]` | Ch 27 |
| **Re-run** | Executing the same goal again from the start, with new identities and every effect repeated. | `[INF]` | Ch 41 |
| **Replay** | Stepping through a recorded run while executing nothing at all. | `[INF]` | Ch 40 |
| **Partial match** | An identity agreeing on run and position but differing on plan or inputs; an anomaly, never a cache hit. | `[DAR]` | Ch 32 |
| **Determinism quarantine** | The rule that everything outside an activity produces the same outcome given the same recorded results. | `[DAR]` | Ch 40 |
| **Attempt count** | How many times an activity has been claimed, surfaced to the planner so repetition is a decision. | `[INF]` | Ch 27 |
| **Effect log** | What an activity actually changed, recorded alongside its result so a resumed run knows what may already have happened. | `[INF]` | Ch 27, Ch 30 |
| **The record window** | The gap between an external effect happening and its result being recorded; narrowed by four mitigations and closed by none. | `[INF]` | Ch 27 |

---

**Next:** Chapter 22 — *The Event Spine.* The transactional outbox as the entire durability story,
claim-based relay against the cursor that turns one bad row into an outage, partition-key selection,
and the command port that carries intent across the narrow waist.
