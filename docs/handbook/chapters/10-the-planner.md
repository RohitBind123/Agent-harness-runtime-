```
  Level 2 · Chapter 10
  THE PLANNER
  Requires   C5 The Five Nouns, C6 State Separation, C8 Lifecycles,
             C9 Three Flows
  Unlocks    C21 Durable Execution, C24 The Task Graph,
             C26 Planning Algorithms, C30 Human Authority
  Diagrams   Full (9)
```

# Chapter 10 — The Planner

---

## 1. Motivation

### 1.1 Cold open

14:12. A customer steers a running job: *"also update the changelog."* Atlas acknowledges and
carries on.

14:19. Atlas force-pushes to a protected branch.

The gate had been resolved forty minutes earlier, for a different action. Step 7 of the plan had
been `tool.repo.push_branch` targeting a feature branch, and the customer's tech lead approved
exactly that, having read exactly that. When the steer arrived, the planner did the natural thing —
it revised the plan in place — and the revision made step 7 a push to `main`.

Step 7 was still called step 7. The approval record pointed at step 7. The gate checked that step 7
was approved, found that it was, and let it through.

Nobody wrote a bug. The planner revised a plan, which is its job. The gate honoured an approval,
which is its job. The two were individually correct and jointly catastrophic, because a plan was
allowed to be a mutable object.

### 1.2 In plain language

The planner is the part of the system that turns a goal like *"fix this failing test"* into an
ordered list of concrete things to do: read that file, run the suite, write a patch, run it again.
It is also what decides, after each result comes back, whether to continue down the list or think
again.

It is the only component in the runtime allowed to *propose* an action. Everything else can stop or
downgrade what it proposes, but nothing else can invent one. That makes it the place to look first
when a run does something surprising.

The chapter's central idea sounds like bookkeeping and is not. **A plan is never edited.** When
circumstances change — a person redirects the work, a step fails, new information arrives — the
planner does not revise the existing plan. It produces a *new* plan with a new identity, and the old
one is kept, finished, exactly as it was.

That single rule is what the cold open is missing. If plans could not be edited in place, "step 7"
would have meant one specific action forever, an approval for it could not have been silently
transferred to a different action, and the force-push could not have happened.

The same rule turns out to be what makes crash recovery safe, for reasons that are not obvious yet
and are §2.2.

### 1.3 Why this chapter exists

Level 1 built the machinery that carries work. This chapter is the first that decides *what the work
is*, and it sets a pattern the next ten chapters follow: a port with a narrow contract, a piece of
state with a clear owner, and one property that everything downstream depends on.

For the planner, that property is **plan identity**. Chapters 21, 24, and 30 each turn out to rest
on it — durable replay, the task graph, and human authority respectively — and each of them is
unbuildable if a plan can change underneath it. The cold open is what it looks like when one of the
three discovers that late.

### 1.4 What previous framings got wrong

**"The planner is the agent."** The most common conflation, and Chapter 3's naming rules ban the
phrasing for exactly this reason. The planner proposes; the run driver decides whether to act on
the proposal; the gate and the grader can refuse it. Reading the planner as the whole system makes
its three vetoes invisible, and Chapter 9 §4.1 showed those vetoes are where auditability lives.

**"Planning is a prompt."** `[AHE §4.4.1]` measured the system prompt alone *regressing* against a
minimal baseline while tools and memory carried gains. A planner is a component with state, a
contract, an identity scheme, and a failure table. Some of it is a prompt, in the way that some of a
compiler is a lookup table.

**"Replanning means editing the plan."** The cold open. `[DAR §10.1]` is explicit that a replan
mints a new plan; this chapter is largely an argument for why that apparently pedantic rule is
load-bearing.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A construction change order.

A builder works from a drawing. The drawing has a revision number in its corner, and every
instruction on site references that revision. When the client changes their mind — move the door two
metres left — nobody walks to the drawing pinned on the site hut and redraws the door. They issue
**revision C**, and revision B is retained, in the file, exactly as it was.

That looks like bureaucracy until something goes wrong. The building inspector signed off the
staircase against revision B. If revision B could be edited, that sign-off would silently become a
sign-off for whatever the drawing says *now* — which is precisely the cold open, in a domain where
people are more careful because the consequences are physical.

Retaining revisions buys three things, and they are the three this chapter needs. An approval is
attached to a specific revision, so it cannot drift. Work already completed against revision B stays
valid and does not need redoing. And when something is wrong on site, you can establish *which
revision the work was done under*, which is the difference between a diagnosis and an argument.

**Where the analogy breaks.** A construction revision is authored by a human architect who
understands the whole building and issues perhaps four revisions over a year. A plan here is authored
by a model, mid-run, possibly forty times, from a context that is a partial and lossy view of the
situation. So two things do not carry over: the revision rate is high enough that retention has to
be cheap by design rather than by diligence, and the author cannot be trusted to notice when a
revision invalidates earlier work. Both of those are why the identity scheme in §5 is mechanical —
a hash rather than a judgement — instead of relying on the planner to flag what changed.

### 2.2 Why a replan must mint a new plan

The rule looks like naming discipline. It is forced, and the derivation is the spine of the chapter:

```
  1. Work already done must not be redone. A completed model call cost
     real money and a completed tool call may have touched the world.
  2. So the runtime needs to recognise "this exact work has already
     been done" -- an identity for each unit of work (Ch 2).
  3. That identity must be computable BEFORE the work runs, or it
     cannot prevent the work from running twice.
  4. What makes a step's work unique is: which run, which plan, which
     position, which tool, which inputs. So identity is a function of
     those five things.
  5. Now suppose a plan may be edited in place. Editing step 7 changes
     the tool or the inputs, so step 7's identity changes -- while its
     POSITION, the thing everything else refers to, does not.
  6. Anything holding a reference to "step 7" now points at different
     work than when the reference was taken. That includes stored
     results, in-flight activities, and -- the cold open -- approvals
     granted by a human who read the old step 7.
  7. The only way to keep references stable is for the thing they
     point into to be immutable.
  8. Therefore a plan is immutable, and a change produces a NEW plan
     with a NEW id. Step 7 of plan B and step 7 of plan C are
     different steps that happen to share a position.
```

Step 6 is the one that carries the security consequence. Idempotency and human authority are usually
treated as unrelated concerns — one is a durability problem, the other a safety problem — and this
derivation shows they are the same problem. Both are references into a plan, and both break in the
same way if the plan moves under them. `[DAR §8.3]` states the conclusion directly: steering forces
a replan rather than mutating a plan, and that is what unifies redirection with idempotency.

### 2.3 What a planner is, precisely

`[DAR §10.1]` The planner is a port with two responsibilities and a hard boundary around each:

> **Given a goal and the history so far, produce an ordered set of proposed steps. Given a result,
> decide whether the current plan still holds.**

What it does *not* do is as defining:

| The planner does not | Because | Chapter |
|---|---|---|
| execute anything | it proposes; the activity runner dispatches | Ch 14 |
| decide whether a step is allowed | the effect tag and the gate do | Ch 30 |
| judge whether a result was good | the grader does, and may only downgrade | Ch 28 |
| write run state | the run driver does, under CAS | Ch 17 |
| know what a repository is | that is domain knowledge, behind the tool port | Ch 4 |
| choose its own budget | the run's budget is set before it plans | Ch 35 |

`[INF]` A planner that does any of those six has absorbed a veto into the proposer, and Chapter 9's
one-proposer-three-vetoes property is gone. The most common instance is the fourth: a planner that
writes `current_step` directly, because it is right there and it knows the answer.

### 2.4 The mental model to carry

> **A plan is a value, not an object. Values are compared and replaced; objects are mutated. Every
> defect in this chapter is a plan that was treated as an object.**

`[INF]` Chapter 3's naming conventions already require frozen dataclasses for data carriers, and
this is where that convention stops being style. If `Plan` is frozen, the cold open is not a bug you
avoid by being careful — it is a line of code that does not compile.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  KERNEL                                                      |
  |                                                              |
  |   +------------------+   (1) goal + history                  |
  |   | run driver       |------------------+                    |
  |   +--------+---------+                  |                    |
  |        ^   |                            v                    |
  |        |   | (5) proposed plan   +==============+            |
  |        |   +---------------------| PLANNER PORT |            |
  |        |                         +======+=======+            |
  |        |                                | (2)                |
  |        |                                v                    |
  |        |                         +==============+            |
  |        |                         | MODEL PORT   | (3)        |
  |        |                         +======+=======+            |
  |        |                                |                    |
  |        | (6) dispatch step              | (4) completion     |
  |        v                                v                    |
  |   +------------------+          +----------------+           |
  |   | activity runner  |          | plan validator |           |
  |   +------------------+          +----------------+           |
  |                                                              |
  +--------------------------------------------------------------+
              |                                    |
              v (7)                                v (8)
      +~~~~~~~~~~~~~~~+                    [[ run_plans ]]
      | tools, model  |                    every plan, forever
      +~~~~~~~~~~~~~~~+                    append-only

  Figure 10.1 -- The planner in its surroundings
                 (D1 High-Level Architecture)

  (1) goal, prior steps, prior results, and any steer -- never live
      run state; the driver assembles this
  (2) the planner asks the model port; it does not call a provider
  (3) provider identity is invisible above this line (Ch 13)
  (4) a raw completion, unvalidated and untrusted
  (5) a validated, frozen Plan with a fresh plan_id
  (6) the driver -- not the planner -- dispatches
  (7) effects reach the world only from the activity runner
  (8) plans are appended, never updated
```

Wire 5 and wire 8 together are the chapter. The planner hands back a value; the value is appended to
a table that has no `UPDATE` path. Everything in §11 is a consequence of one of those two being
violated.

`[INF]` Note that the planner has no arrow to the world. It cannot read a file or call a service
except by proposing a step that the runner may dispatch. This is what makes the planner cheap to
test — Chapter 40 fakes the model port and the planner becomes a pure function — and it is a
property teams lose the first time they let a planner "just peek" at the repository to plan better.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  PLANNER PORT, opened
  +--------------------------------------------------------------+
  |                                                              |
  |  +---------------------+   the ONLY input. Assembled by the   |
  |  | PlanRequest         |   driver, never fetched by the       |
  |  |  goal               |   planner itself.                    |
  |  |  prior_steps[]      |                                      |
  |  |  prior_results[]    |                                      |
  |  |  steer?             |                                      |
  |  |  constraints        |   budget left, tools available,      |
  |  +----------+----------+   step budget, forbidden effects     |
  |             |                                                |
  |             v                                                |
  |  +---------------------+                                     |
  |  | strategy            |   ReAct | decompose | contract-first |
  |  |  (Ch 26 opens this) |   pluggable; default is not doctrine |
  |  +----------+----------+                                     |
  |             |                                                |
  |             v                                                |
  |  +---------------------+                                     |
  |  | context assembly    |   Ch 11. The single largest data     |
  |  |                     |   movement in the system.            |
  |  +----------+----------+                                     |
  |             |                                                |
  |             v                                                |
  |  +---------------------+                                     |
  |  | model port call     |   metered, capped, abortable (Ch 13) |
  |  +----------+----------+                                     |
  |             |                                                |
  |             v                                                |
  |  +---------------------+   REJECTS, never repairs:            |
  |  | plan validator      |    unknown tool id                   |
  |  |                     |    schema mismatch                   |
  |  |                     |    forbidden effect for this tenant  |
  |  |                     |    step count over budget            |
  |  |                     |    cycle in dependencies             |
  |  +----------+----------+                                     |
  |             |                                                |
  |             v                                                |
  |  +---------------------+                                     |
  |  | identity minting    |   plan_id = fresh ULID               |
  |  |                     |   per step: activity_id = hash(...)  |
  |  +----------+----------+   computed HERE, at plan time        |
  |             |                                                |
  |             v                                                |
  |        frozen Plan                                            |
  +--------------------------------------------------------------+

  Figure 10.2 -- Inside the planner (D2 Low-Level Architecture)
```

```
                                                            LAYER VIEW

  Components and the interfaces between them. Only two cross the
  planner's boundary: PlanRequest in, Plan out.

   PlanRequest                                        Plan (frozen)
       |                                                    ^
       v                                                    |
  +----+-----------------+                    +-------------+------+
  | Strategy             |   PlanDraft        | Identity minter    |
  |  select_method()     |------------------->|  new_plan_id()     |
  +----+-----------------+                    |  activity_id()     |
       | ContextRequest                       +-------------+------+
       v                                                    ^
  +----+-----------------+                                  | ValidPlan
  | Context assembler    |   Context (~50-200 KB)           |
  |  assemble()          |--------+              +----------+-------+
  +----------------------+        |              | Validator        |
       ^                          v              |  check()         |
       | reads                +---+----------+   |  -> Ok | Reject  |
  +----+-----------------+    | Model port   |   +----------+-------+
  | History view         |    |  complete()  |              ^
  |  (read-only, Ch 6)   |    +---+----------+              |
  +----------------------+        |                         |
                                  +-------------------------+
                                        raw completion
                                        (untrusted)

  +----------------------+    consulted by the validator and the
  | Tool registry        |<-- identity minter; supplies effect tags,
  |  effect_of()         |    which never come from the model
  |  schema_of()         |
  +----------------------+

  Figure 10.3 -- Planner components and their interfaces
                 (D3 Component Diagram)
```

`[INF]` Two interface facts are worth stating because they are what keeps the planner testable. The
history view is **read-only** — the planner sees prior steps and results and cannot write them
(Chapter 6's run-state ownership). And the tool registry is consulted by the validator and the
identity minter, never by the strategy: the model may name a tool, but only the registry may say
what that tool *is*.

### 4.1 The validator rejects and never repairs

`[INF]` The most consequential line in that diagram is the word REJECTS. A validator that silently
fixes a malformed proposal — coercing an unknown tool id to the nearest known one, truncating an
over-long plan — destroys the evidence that the planner is misbehaving. The run then succeeds, and
the harness defect that produced the bad proposal is never observed.

Level 5 makes this concrete: the Evolve Agent improves the planner by reading what it got wrong
`[AHE §3.2]`. A repairing validator is a component that hides the training signal. Reject, record
the rejection as a fact, and let the retry produce a clean proposal or a clean failure.

### 4.2 Identity is minted at plan time, not dispatch time

The single most easily-missed line in the chapter, and Chapter 5 §4 already asserted it: the
`activity_id` for every step is computed when the plan is created, not when the step is dispatched.

`[DAR §6.1]` The reason is §2.2 step 3. An identity computed at dispatch cannot prevent a duplicate
dispatch, because the duplicate computes the same identity at the same moment and neither sees the
other. Computed at plan time, the identity exists in a durable row before anything runs, and the
activity ledger has somewhere to collide.

---

## 5. Plan Identity

### 5.1 The three identifiers, and what each is for

| Identifier | Scope | Changes when | Referenced by |
|---|---|---|---|
| `run_id` | one goal | never | everything |
| `plan_id` | one plan, one revision | every replan | steps, approvals, results |
| `activity_id` | one unit of work | any of run, plan, position, tool, inputs changes | the activity ledger, budgets |

`activity_id = hash(run_id, plan_id, step_id, tool_id, input_digest)` `[DAR §6.1]`.

Read that hash against §2.2 step 5 and the design becomes readable. Because `plan_id` is in the
hash, a replan changes every step's identity *automatically*, even for steps whose tool and inputs
are byte-identical. Nothing has to detect what changed. That is the mechanical guarantee the
construction analogy said could not be left to the author's judgement.

### 5.2 The consequence people find surprising

An unchanged step in a new plan gets a new identity, so its result is **not** reused, and it will be
re-executed and re-paid for.

`[INF]` This looks wasteful and is the correct trade. The alternative — carrying results across a
replan by matching on tool and inputs — reintroduces exactly the ambiguity the cold open exploited:
a step that *looks* the same but sits in a plan formed under different assumptions. Chapter 21
records the partial-match case as an anomaly to alert on rather than a cache hit to take
`[DAR §6.1]`, and this is why.

The cost is real and it is bounded by replanning rarely, which §12 turns into a metric.

### 5.3 What a steer does, precisely

`[DAR §8.3]` A steer is a goal amendment, not a plan edit. In full:

1. The steer arrives at the edge and is written to the outbox as intent (Chapter 7).
2. The run driver reads it at the next checkpoint — never mid-step (Chapter 8 §6.3).
3. The driver calls the planner with the *amended goal* and the full history.
4. The planner returns a new plan with a fresh `plan_id`.
5. Steps of the old plan that were in flight are cancelled; steps that completed remain completed
   facts, attributed to the old plan.
6. Every pending approval against the old plan is **void**, because it was granted against a plan id
   that is no longer current.

Step 6 is the cold open's missing line, and stating it as a rule about identity rather than a rule
about approvals is what makes it hard to forget.

### 5.4 Replan triggers

| Trigger | Source | New plan? |
|---|---|---|
| Steer from a human | Ch 7 signal | yes |
| Step failed after retries | activity ledger | yes |
| Grader downgraded a result | Ch 28 | yes |
| Budget reduced mid-run | Ch 35 | yes |
| New information from a pure step | normal execution | **no** — that is what the plan anticipated |
| Tool unavailable | Ch 14 | yes |
| Approval refused | Ch 30 | yes |

`[INF]` Row five is the discriminator worth internalising. A plan that must be replaced every time a
step returns information is not a plan; it is a single-step loop wearing a plan's clothes. §12.2
makes "steps per plan" the metric that detects it, and a distribution with a mode at one means the
planner is not planning.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  driver        planner       model        gate         run_plans
    |              |            |            |               |
    |-- plan(goal, history) --->|            |               |
    |              |-- assemble context ---->|               |
    |              |<-- completion ----------|               |
    |              | validate; REJECT or mint plan_id B      |
    |              |----------------- append plan B -------->|
    |<-- Plan(B, steps 1..9) ---|            |               |
    |                                        |               |
    |  steps 1..6 execute normally                           |
    |                                                        |
    |  step 7 is effectful -> raise gate                     |
    |------------- approval requested for (B, step 7) ------>|
    |  [ run PARKS. Holds nothing. ]                         |
    |                                                        |
    |<------------ approved: (B, step 7) --------------------|
    |                                                        |
    |  ...but a STEER arrived before the driver resumed      |
    |                                                        |
    |-- plan(amended goal, history) -->|                     |
    |              |-- assemble ------>|                     |
    |              |<-- completion ----|                     |
    |              | mint plan_id C                          |
    |              |----------------- append plan C -------->|
    |<-- Plan(C, steps 1..11) --|                            |
    |                                                        |
    |  approval was for (B, step 7). Current plan is C.      |
    |  (C, step 7) has a DIFFERENT activity_id.              |
    |  -> approval does not match. Gate raised again.        |
    |     The human sees the NEW action and decides again.   |
    |                                                        |

  Figure 10.4 -- A steer arriving against a granted approval
                 (D4 Sequence)
```

```
                                                             TIME VIEW

  The plan/replan cycle, and the five ways out of it.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | plan(request)        |  a model call; the largest     |
   +----+-----------------+  payload in the system         |
        |                                                 |
        v                                                 |
      /   \      reject                                   |
     / valid?\----------> retry once, then E5             |
     \       /                                            |
      \     /  ok                                         |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | append plan; mint    |                               |
   | activity ids         |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
   +----+-----------------+   <-- the driver executes;     |
   | steps 1..n execute   |       the planner is idle      |
   +----+-----------------+       for this whole box       |
        |                                                 |
        v                                                 |
      /   \                                               |
     / should\  yes, and the reason is in section 5.4     |
     \replan?/------------------------------------------->+
      \     /
        | no
        v
      /   \
     / more \  yes -> continue executing (no model call)
     \steps?/
      \     /
        | no
        v
      E1 plan complete, goal met

  Exits:
    E1  plan complete and the goal is met      -> run SUCCEEDED
    E2  budget exhausted                       -> park BUDGET_EXHAUSTED
    E3  replan cap reached                     -> run FAILED, thrash
    E4  cancelled by signal                    -> run CANCELLED
    E5  validator rejected twice               -> run FAILED, planner
                                                  defect; emits
                                                  << run.plan.rejected >>

  Figure 10.5 -- The plan/replan cycle and its exits (D5 Runtime Loop)
```

`[INF]` E3 is the exit teams forget to build. Without a replan cap, a planner that has lost the
thread will replan until the budget runs out, and the run then fails as `BUDGET_EXHAUSTED` — which
sends the operator to Chapter 35 to look at cost when the defect is in this chapter. Capping replans
separately makes thrash report itself as thrash.

The wide box in the middle is worth noticing too: for the entire duration of step execution, the
planner does nothing. It is not a loop that runs alongside the work; it is consulted at the top and
then again only if something changes. A planner that is consulted on every step has collapsed into
§12.2's mode-of-one.

### 6.1 Reading the failure branch

The final block of Figure 10.4 is the cold open, prevented. Nothing in that sequence *detects* the
danger; there is no check that says "was this approval for the same action?". The mismatch falls out
of the identity scheme, because the approval was keyed to an identity that no longer exists in the
current plan.

`[INF]` That is the difference between a safeguard and a property. A safeguard is code someone
remembered to write and someone else can refactor away. A property is a consequence of the data
model, and the only way to lose it is to make plans mutable — which is a change large enough that
somebody will notice.

---

## 7. State Management

```
                                                            STATE VIEW

              +----------------+
              | {{ PROPOSED }} |  returned by the planner, not yet
              +--------+-------+  appended
                       | validated + appended
                       v
              +----------------+
              | {{ CURRENT }}  |  exactly one per run, enforced by a
              +--------+-------+  partial unique index
                       |
        +--------------+--------------+
        | replan                      | run reaches a terminal state
        v                             v
  +----------------+          +----------------+
  | {{SUPERSEDED}} |          | {{ FINAL }}    |
  +----------------+          +----------------+
   retained forever            retained forever
   never deleted               the plan the run ended under

  Illegal, and enforced:
    * any state -> PROPOSED         plans are never reopened
    * SUPERSEDED -> CURRENT         no un-superseding; replan forward
    * two CURRENT plans per run     partial unique index on (run_id)
                                    WHERE state = 'CURRENT'
    * UPDATE on a plan's steps      no code path exists

  Figure 10.6 -- Plan states (D6 State Diagram)
```

### 7.1 Plans are run state, and they are never deleted

Chapter 6's categories: a plan is run state — it does not survive deleting the runtime, and Atlas's
domain has no idea plans exist. But unlike most run state, superseded plans are retained after the
run ends.

`[INF]` The retention is not sentiment. Three consumers need it: Chapter 34's debugging ("which plan
was this step under?"), Chapter 30's audit trail (an approval references a plan id that must resolve
forever), and Chapter 44's evidence corpus, where the sequence of plans across one run is the
clearest available signal of whether the planner was converging or thrashing.

### 7.2 Exactly one current plan

The partial unique index is the mechanism, and it is worth writing out because it is the kind of
constraint that is easy to intend and easy to omit:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS uq_run_plans_current
    ON run_plans (run_id)
 WHERE state = 'CURRENT';
```

A replan is then one transaction: supersede the old, insert the new. If two workers replan the same
run concurrently — which the lease should prevent and which you should not rely on the lease to
prevent — the second insert fails at the database rather than producing a run with two live plans.

---

## 8. Internal APIs

```python
from typing import Protocol


class PlannerPort(Protocol):
    """Proposes. Never executes, authorises, grades, or writes run state.

    Implementations are pure with respect to the runtime: given the same
    PlanRequest and the same model responses, they produce the same Plan.
    That is what makes Ch 40's hermetic replay possible.
    """

    async def plan(self, request: PlanRequest) -> Plan:
        """Produce a fresh plan for a goal, or a re-plan after a change.

        Always returns a NEW Plan with a new plan_id. There is
        deliberately no `revise` method: the absence is the contract.
        """

    async def should_replan(
        self,
        plan: Plan,
        completed: StepResult,
    ) -> ReplanDecision:
        """Decide whether the current plan still holds after a result.

        Cheap and usually deterministic: most results do not warrant a
        model call. An implementation that calls the model here on every
        step has turned an N-step plan into N one-step plans (section 12.2).
        """
```

`[INF]` The absence of a `revise` method is the most important line in this section. An interface
that cannot express in-place revision cannot be misused into the cold open, and this is where
Chapter 3's decision to make ports `Protocol`s rather than documentation pays: the constraint is
checked by the type system rather than remembered in review.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class Effect(StrEnum):
    PURE = "pure"
    EFFECTFUL = "effectful"


@dataclass(frozen=True)
class Step:
    step_id: int                 # position; unique within a plan only
    tool_id: str                 # "tool.repo.apply_patch"
    input: Mapping[str, object]
    effect: Effect               # from the tool registry, NOT the model
    activity_id: str             # minted at plan time (section 4.2)
    depends_on: tuple[int, ...] = ()   # Ch 24 opens this


@dataclass(frozen=True)
class Plan:
    plan_id: PlanId              # fresh ULID per plan, never reused
    run_id: RunId
    steps: tuple[Step, ...]      # tuple, not list -- immutability is
                                 # structural, not a convention
    created_at: datetime
    supersedes: PlanId | None    # the revision chain
    reason: ReplanReason         # why this plan exists at all
    strategy: str                # which strategy produced it (Ch 26)
```

Three details carry weight.

**`effect` comes from the tool registry, never from the model.** `[DAR §8.1]` If a model could
declare its own step pure, the safety model would be a request rather than a rule. The planner
proposes a `tool_id`; the runtime looks up the effect tag.

**`steps` is a tuple.** A list would make the cold open reachable by `plan.steps[7] = other_step`.
The type is the enforcement.

**`supersedes` makes the chain walkable.** Given any plan you can walk back to the original, which
is what §7.1's three consumers each need and what Chapter 44 reads as a convergence signal.

---

## 10. Communication

```
                                                            LAYER VIEW

  DATA
  goal + history    driver  ====>  planner        ~5-40 KB
  assembled context planner ====>  model         ~50-200 KB  <-- dominant
  completion        model   ====>  planner        ~5-50 KB
  validated plan    planner ====>  driver         ~2-20 KB
  appended plan     driver  ====>  [[ run_plans ]] ~2-20 KB per replan

  Figure 10.7 -- What moves when planning (D7 Data Flow)
```

```
                                                             TIME VIEW

  driver ----> planner        "propose, given this"
  planner ---> model port     the only outbound call it may make
  planner --X  tools          REFUSED: the planner cannot execute
  planner --X  run state      REFUSED: the driver writes, under CAS
  driver ----> activity runner  dispatch happens HERE, not in the planner

  Figure 10.8 -- Who decides during planning (D8 Control Flow)
```

```
                                                             TIME VIEW

  << run.plan.created >>     ....>  every plan, including the first
  << run.plan.superseded >>  ....>  carries the reason
  << run.plan.rejected >>    ....>  validator refusal; the training
                                    signal of section 4.1

  NOT events:
    a proposal the validator rejected and retried successfully
    intermediate model output during assembly
    the planner's internal reasoning tokens

  Figure 10.9 -- What planning makes durable (D9 Event Flow)
```

`[INF]` `run.plan.rejected` is the event most systems omit, and it is the one Level 5 needs most. A
rejection is direct evidence that the planner produced something invalid — the highest-signal,
lowest-volume observation available about planner quality. Without it, the only trace of a bad
proposal is a slightly slower run.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 21 Durable Execution | `activity_id` minted at plan time | replay reuses results only when identity matches |
| Ch 24 Task Graph | `depends_on`, unused here | the linear plan becomes a DAG without a schema change |
| Ch 26 Planning Algorithms | the `strategy` field | ReAct is one value, not the architecture |
| Ch 28 Grading | a downgrade as a replan trigger | verdicts feed back into planning |
| Ch 30 Human Authority | approvals keyed to `(plan_id, step_id)` | the cold open, prevented structurally |
| Ch 44 Agent Debugger | the plan chain via `supersedes` | thrash is visible as chain length |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Mutable plan | in-place revision on steer | approvals resolving against changed actions | frozen `Plan`, new `plan_id` — the cold open |
| Approval drift | approval keyed to position, not identity | audit shows approval and action disagree | key approvals to `(plan_id, step_id)` |
| Identity at dispatch | `activity_id` computed when dispatching | duplicate spend under concurrency | mint at plan time (§4.2) |
| Repairing validator | validator coerces bad proposals | planner defects never surface; runs quietly degrade | reject and emit `run.plan.rejected` |
| Model declares its own effect tag | `effect` read from the completion | an effectful step executing with no gate | tag comes from the tool registry |
| Replan storm | every result triggers `should_replan` | steps-per-plan mode of 1; cost per run climbing | make replanning a decision, not a reflex |
| Plan longer than the budget | validator does not check step count | budget exhausted mid-plan, always | validate step count against remaining budget |
| Two current plans | concurrent replan | second insert violates the index | the partial unique index (§7.2) |
| Planner reads the world | "peeking" at a repository to plan better | planner untestable without a sandbox | propose a pure step instead |
| Orphaned approval | approval outlives its plan | gate matches nothing; run parks forever | void approvals on supersede (§5.3 step 6) |

`[INF]` Row nine is the one that arrives disguised as an improvement. A planner that can read the
repository directly produces visibly better first plans, and it costs the property in §3 that made
the planner a pure function of its request. The correct version is a pure step — the planner
proposes `tool.repo.map`, the runner executes it, and the result arrives in history for the next
plan. The information is identical; the testability and the audit trail are not.

---

## 12. Scalability

### 12.1 Planning is a model call, and model calls are the budget

Every plan and every replan is a model call carrying the largest payload in the system (Chapter 9
§5.1). So planning cost is `(1 + replans) × context_size`, and the term you control is the second
one.

`[INF]` This makes replan frequency a *cost* metric before it is a quality metric, which is the
opposite of most teams' intuition. A run that replans eleven times has paid for twelve plans, and
almost certainly assembled a larger context each time.

### 12.2 Steps per plan, the diagnostic distribution

| Mode of the distribution | Diagnosis |
|---|---|
| 1 | the planner is not planning; it is a one-step loop (§5.4 row five) |
| 2–3 | ReAct-ish; acceptable, but check the replan reasons |
| 5–15 | healthy planning with genuine lookahead |
| 40+ | over-planning; late steps are speculation that will be replanned away |

`[DAR §15]` records steps-per-episode as a required metric for the same reason. This is its
planning-side twin, and both share the property that a mode of one means a loop has collapsed into
something that no longer earns its structure.

### 12.3 What does not scale with load

Plans are per-run, so `run_plans` grows with runs times replans and nothing else. There is no shared
planner state, no cross-run contention, and no coordination — which means the planner scales
horizontally without discussion. `[INF]` The one thing to watch is `run_plans` growth from §7.1's
retention rule: it is append-only and never pruned, so it wants a partition or an archival policy
before it wants an index.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Replans per run, p50/p99 | the cost and quality lever | p99 above your ceiling |
| Steps per plan, distribution | §12.2's diagnostic | mode of 1 |
| `run.plan.rejected` rate | direct planner-quality signal | any sustained rise |
| Validator rejection reasons | which defect class | reported, not alerted |
| Approvals voided by supersede | steering colliding with gates | reported; a rise means UX friction |
| Plan chain depth at completion | thrash | p99 above your ceiling |

### 13.2 The test that catches the cold open

```python
async def test_steer_voids_a_pending_approval(
    runtime: Runtime, fake_model: FakeModelPort
) -> None:
    run = await runtime.submit(goal)
    plan_b = await runtime.current_plan(run)
    await runtime.approve(plan_b.plan_id, step_id=7)

    await runtime.steer(run, "also update the changelog")

    plan_c = await runtime.current_plan(run)
    assert plan_c.plan_id != plan_b.plan_id
    assert plan_c.supersedes == plan_b.plan_id
    # The property, not a safeguard: identity differs, so nothing matches.
    assert plan_c.steps[6].activity_id != plan_b.steps[6].activity_id
    assert not await runtime.has_valid_approval(plan_c.plan_id, step_id=7)
```

`[INF]` The third assertion is the one worth keeping even if it looks redundant. It tests the
*mechanism* rather than the outcome, so it still fails if somebody later "optimises" identity by
dropping `plan_id` from the hash — a change that would leave the last assertion passing for a while
and then stop.

### 13.3 Choosing a default strategy

`[BP]` ReAct is a reasonable default and is not the architecture. It lives in the `strategy` field
precisely so that Chapter 26 can replace it per work class without touching anything in this chapter.

Start with ReAct, measure §12.2's distribution, and change strategy when the distribution says the
default does not fit the work — not because a newer method was published.

---

## 14. Relation to AHE

The planner is a harness component, which makes it directly editable by the evolution loop — and it
sits at the top of Chapter 1's enforcement hierarchy, where enforcement is weakest.

**It is mostly prose, and prose is the weakest surface.** A planner's behaviour is dominated by a
system prompt and tool descriptions, and `[AHE §4.4.1]` measured the system prompt alone
*regressing* by 2.3 points while tools and memory carried gains. `[INF]` The lesson is a routing
rule: a planner defect that can be fixed in a tool description or the validator should be, because
both enforce, and the prompt only asks.

**The validator is the enforceable half.** `[INF]` "Never propose more steps than the budget allows"
is a sentence in a prompt that the model may ignore, and a rejection in the validator that it
cannot. Chapter 46's constraint-level hierarchy is exactly this choice, and the planner is where it
first becomes concrete.

**`run.plan.rejected` is the training signal.** §10's event is what lets the Evolve Agent see that a
proposal was invalid rather than merely slow. Without it the loop optimises against outcomes only,
and Chapter 48's fix-prediction figures get worse for a reason that has nothing to do with the loop.

**Plan chains are the clearest convergence evidence in the corpus.** `[INF]` A run whose plan chain
is fourteen deep tells the Agent Debugger something no trajectory summary conveys as cheaply: the
planner kept changing its mind. Chapter 44 uses chain depth as a first-pass filter over rollouts for
this reason.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the planner port's two responsibilities, plan identity, the rule that a replan
mints a new plan, `activity_id` as a hash including `plan_id`, steering as goal amendment forcing a
replan, the effect tag coming from the registry, and partial identity match as an anomaly rather
than a cache hit `[DAR §6.1, §8.1, §8.3, §10.1]`.

**`[AHE]`** Supplies the component ablation that places the system prompt last by measured value
`[AHE §4.4.1]`, and contract-first planning as one strategy among several `[AHE App. C]`.

**`[INF]`** The handbook's own: the derivation in §2.2 unifying idempotency and human authority as
one reference-stability problem, "a plan is a value, not an object", the reject-never-repair rule
and its Level 5 justification, the steps-per-plan diagnostic distribution, the argument that a
planner reading the world directly trades testability for first-plan quality, and the routing rule
in §14 for choosing where a planner fix belongs.

**`[BP]`** Immutable revisions with retained history are standard in version control, event
sourcing, and construction documentation alike; the contribution here is noticing that the safety
argument and the idempotency argument are the same argument.

**`[FUT]`** Nothing in this chapter is speculative. Chapter 26 contains the speculative planning
material; this chapter is deliberately confined to the parts that are settled, because everything in
Levels 3 and 5 depends on them.

---

## 16. Key Takeaways

1. **The planner proposes; it does nothing else.** It cannot execute, authorise, grade, or write run
   state. A planner that does any of those has absorbed a veto and taken auditability with it.
2. **A plan is a value, not an object.** Frozen dataclass, tuple of steps, no `revise` method. The
   cold open is not a bug you avoid by being careful; it is a line that does not compile.
3. **A replan mints a new plan id, always.** Steering, failure, downgrade, and budget change all
   produce a new plan. The old one is retained, finished, exactly as it was.
4. **Idempotency and human authority are the same problem.** Both are references into a plan, and
   both break identically if the plan moves underneath them. That is §2.2, and it is why the
   pedantic-sounding rule is load-bearing.
5. **Identity is minted at plan time.** An identity computed at dispatch cannot prevent the
   duplicate dispatch that computes the same identity at the same instant.
6. **The validator rejects and never repairs.** A repairing validator hides the evidence that the
   planner is misbehaving, and that evidence is what Level 5 runs on.
7. **Steps per plan is the diagnostic.** A mode of one means the planner is not planning, and you
   are paying for a plan on every step to get a loop.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Planner** | The only component permitted to propose a step, and permitted to do nothing else. | `[DAR]` | Ch 18, Ch 26 |
| **Plan** | An immutable, ordered set of proposed steps with its own identity; a value rather than an object. | `[DAR]` | Ch 21, Ch 24 |
| **Plan identity** | The `plan_id` that makes every reference into a plan stable, because the plan it points into can never change. | `[DAR]` | Ch 21, Ch 30 |
| **Replan** | Producing a new plan with a new id in response to a steer, failure, downgrade, or budget change — never an edit. | `[DAR]` | Ch 26, Ch 30 |
| **Supersede** | Marking a plan as no longer current while retaining it forever, and voiding every approval that referenced it. | `[INF]` | Ch 30, Ch 44 |
| **Plan validator** | The component that rejects a malformed proposal and never repairs one, so planner defects stay visible. | `[INF]` | Ch 46 |
| **Effect tag** | Whether a step is pure or effectful, read from the tool registry and never from the model. | `[DAR]` | Ch 14, Ch 30 |
| **Strategy** | Which planning method produced a plan; ReAct is one value of this field, not the architecture. | `[BP]` | Ch 26 |
| **Plan chain** | The `supersedes` links from the current plan back to the first; its depth measures thrash. | `[INF]` | Ch 44 |
| **Steps per plan** | The distribution whose mode tells you whether the planner is planning or looping. | `[INF]` | Ch 34 |

---

**Next:** Chapter 11 — *The Context System.* The largest data movement in the runtime, paid once per
step: assembly order, budgets, compaction, cache-stable prefixes, and why context is a managed
resource rather than a string somebody concatenates.
