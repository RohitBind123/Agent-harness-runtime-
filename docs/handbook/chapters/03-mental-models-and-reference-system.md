```
  Level 0 · Chapter 3
  MENTAL MODELS AND THE REFERENCE SYSTEM
  Requires   C0 Evolution of AI Systems, C1 Anatomy of an Agent,
             C2 Why a Runtime Is a Distributed System
  Unlocks    all of Level 1; the reference system is used in every later chapter
  Diagrams   Light (3)
  Variant    Foundational — sections 4-9 describe models, not components
```

# Chapter 3 — Mental Models and the Reference System

---

## 1. Motivation

### 1.1 Cold open

A code review on the Atlas team stalls for three days.

The author has written a run driver that claims a database lease when a run starts and holds it until
the run finishes. The reviewer rejects it. The author asks why, reasonably: the lease guarantees
exactly one worker per run, which is the requirement, and holding it is the simplest way to
guarantee it.

The reviewer says the lease should be renewed at each step instead. The author asks what that buys.
The reviewer says it stops a slow model call from pinning a connection. The author points out that
the lease is a row, not a connection. The reviewer says that is not the point. Neither of them can
say what the point is, and the thread grows to forty comments.

The disagreement is not about leases. The author's mental model is **a job owns its work** — a job is
handed to a worker, the worker does it, the worker reports back. Under that model, holding ownership
for the duration is obviously right. The reviewer's model is **a process is scheduled onto a core** —
the run exists independently of any worker, and a worker borrows it for a slice of time. Under that
model, holding it for the duration is obviously wrong.

Both are reasoning correctly. They cannot converge, because the disagreement lives upstream of the
argument they are having.

### 1.2 In plain language

Engineers rarely disagree about facts. They disagree because they are picturing the system in
different ways and neither has said which picture they are using. The cold open is three days lost
to exactly that: two people arguing about a lease, when the real disagreement was that one pictured
a job being handed to a worker and the other pictured a process being scheduled onto a processor.

This chapter hands you five pictures and tells you which kind of question each one answers. One is
borrowed from operating systems and answers "who runs this, when, and for how long?". One is
borrowed from accounting and answers "did this already happen, and what did it cost?". One is
borrowed from protocol design and answers "where should this rule be enforced?". One is borrowed
from functional programming and answers "why is it safe to run this again?". One is borrowed from
network architecture and answers "why are there two separate paths through this system?".

The second half of the chapter introduces the two names used for the rest of the book: **ARK**, the
runtime being designed, and **Atlas**, the product built on it — a coding agent that fixes real
issues in real repositories. Every later example lives in that one system, so you never have to
work out how a chapter's example connects to the last chapter's.

The practical value is immediate: when a design argument stalls, naming the picture ends it in one
sentence.

### 1.3 Why this chapter exists

Chapters 0 through 2 gave you history, anatomy, and a transfer map. This chapter gives you the
thinking tools, and then the concrete system every remaining chapter will build.

Five mental models. Each borrowed from a discipline you already have, each chosen because it makes a
class of design questions answerable without argument. A good mental model does not summarise what
you have learned; it *predicts* answers to questions you have not been asked yet. Section 4 tests
each one against exactly that standard.

Then ARK and Atlas, specified concretely enough to carry forty-six chapters. Every diagram, failure
story, and code example from Chapter 4 onward lives in this one system. No chapter invents a new
example.

### 1.4 What previous framings got wrong

**"Metaphors are hand-waving."** They are the opposite. The cold open is what an *absent* shared
metaphor costs, and the cost is measured in days. Two engineers with the same model resolve that
review in one comment.

**"You need one unifying metaphor."** You need five, applied deliberately, and the skill is knowing
which one a given question belongs to. A question about scheduling is not answered by the ledger
model, and forcing it produces confident nonsense.

**"The example system is illustrative."** In this handbook it is load-bearing. `[INF]` A book that
switches examples per chapter teaches each chapter and no system; the reader ends with forty-six
components and no idea how they sit together. Atlas exists so that the integration is never left as
an exercise.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Five specialists walking through the same hospital.

The **operations manager** sees beds, shifts, and who is on call: a question about capacity or
scheduling is theirs, and nobody else can answer it well. The **finance officer** sees a ledger of
what was done and what it cost. The **compliance officer** sees which procedures require a signature
and who is permitted to give it. The **infection-control specialist** sees which areas must stay
sealed from which. The **hospital administrator** sees two distinct networks — one that treats
patients, one that decides policy — and knows that mixing them is how a hospital becomes
ungovernable.

None of the five is looking at a different hospital. None is more correct than the others. But if
you ask the finance officer where to put a quarantine boundary, you get a confident, useless answer.
The skill is not having a favourite specialist; it is recognising, within one sentence, whose
question you are asking.

That is exactly what the five mental models are. Process, ledger, contract, quarantine, and planes
are five specialists walking through one runtime.

**Where the analogy breaks.** Hospital specialists are different people, so the handoff is obvious —
you physically fetch someone else. In a design discussion the five live inside one head, and
switching between them is silent. Nobody announces "I have stopped reasoning about cost and started
reasoning about scheduling", which is precisely why the cold open takes three days: both engineers
had already switched, neither noticed, and the models are close enough that each could keep
producing sentences the other found almost reasonable.

### 2.2 Why five models rather than one

Every book of this kind is tempted to offer a single unifying metaphor. Resisting that is a
deliberate choice, and it follows from what a model is for:

```
  1. A mental model earns its place by PREDICTING answers to questions
     you have not yet asked -- not by summarising what you already know.
  2. A model predicts by importing the consequences of a discipline
     that has already solved a class of problem.
  3. Each discipline solved a DIFFERENT class. Operating systems solved
     custody and scheduling. Accounting solved "did this happen, and
     what did it cost". Protocol design solved where to enforce a rule.
  4. So a model imported from one discipline is silent -- or worse,
     confidently wrong -- outside that class.
  5. A single unifying metaphor must therefore either cover one class
     well and mislead everywhere else, or be so general it predicts
     nothing.
  6. Five models, each with a stated range and a stated breaking point,
     dominate one model with an unstated range.
  7. The cost is a new skill: identifying which model a question belongs
     to before answering it. That skill is section 4.
```

Point 6 carries a requirement the rest of the chapter honours: each of the five is presented *with
its breaking point*, not only its uses. A model whose limits are unstated is the thing this section
argues against.

### 2.3 Five lenses on one system

```
                                                       CONCEPTUAL VIEW

                        +---------------------------+
                        |                           |
                        |     THE SAME RUNTIME      |
                        |                           |
                        +---------------------------+
                             ^   ^    ^    ^   ^
             +---------------+   |    |    |   +---------------+
             |          +--------+    |    +--------+          |
             |          |             |             |          |
        +----+----+ +---+-----+ +-----+----+ +------+---+ +----+-----+
        | MM1     | | MM2     | | MM3      | | MM4      | | MM5      |
        | PROCESS | | LEDGER  | | CONTRACT | |QUARANTINE| | CONTROL  |
        |         | |         | |          | |          | | vs DATA  |
        +----+----+ +----+----+ +-----+----+ +-----+----+ +----+-----+
             |           |            |            |           |
        borrowed    borrowed     borrowed     borrowed     borrowed
        from        from         from         from         from
        operating   double-entry protocol     functional   network
        systems     accounting   design       programming  architecture

        answers:    answers:     answers:     answers:     answers:
        "who runs   "did this    "where does  "why can we  "why are
         it, when,   already      enforcement  replay       there two
         and for     happen and   belong?"     safely?"     queues?"
         how long?"  what did
                     it cost?"

  Figure 3.1 -- Five lenses (conceptual)
```

### 2.4 The meta-model

> **Every hard question in this architecture belongs to exactly one of five lenses. Identifying the
> lens is most of the work; the answer usually follows.**

`[INF]` The five are the handbook's own selection. They are not a taxonomy of the architecture — they
are a taxonomy of the *questions*. Chapter 4 onward will occasionally name which lens a decision
belongs to, and by Level 3 you should be doing it without prompting.

---

## 3. High-Level Architecture

### 3.1 Atlas on ARK

```
                                                            LAYER VIEW

  +------------------------------------------------------------------+
  |  ATLAS  -- the product                                           |
  |  a coding agent that resolves issues in customer repositories    |
  |                                                                  |
  |  surface: web app, GitHub app, CLI, Slack                        |
  +----------------------------------+-------------------------------+
                                     |
  +----------------------------------v-------------------------------+
  |  THE SIX PORTS  -- Atlas's code, ARK's interfaces                |
  |                                                                  |
  |  +============+ +============+ +============+                    |
  |  | planner    | | tool       | | model      |                    |
  |  | issue ->   | | repo, test | | provider   |                    |
  |  | patch plan | | shell, PR  | | behind one |                    |
  |  +============+ +============+ +============+                    |
  |  +============+ +============+ +============+                    |
  |  | grader     | | approval   | | domain     |                    |
  |  | tests pass | | ask the    | | Atlas's    |                    |
  |  | patch appl | | tech lead  | | own tables |                    |
  |  +============+ +============+ +============+                    |
  +----------------------------------+-------------------------------+
                                     |
  +----------------------------------v-------------------------------+
  |  ARK  -- the runtime kernel, domain-independent                  |
  |                                                                  |
  |  relay . run driver . activity runner . sweeper . queues         |
  +----------------------------------+-------------------------------+
                                     |
  +----------------------------------v-------------------------------+
  |  SUBSTRATE  -- one transactional database, one queue             |
  +------------------------------------------------------------------+

                                     |
  +----------------------------------v-------------------------------+
  |  ARK/EVOLVE  -- the Level 5 outer loop                           |
  |  reads Atlas's trajectories, edits Atlas's harness               |
  |  never edits ARK                                                 |
  +------------------------------------------------------------------+

  Figure 3.2 -- The reference system (D1 High-Level Architecture)
```

The separation in that last box is deliberate and will be enforced for the rest of the book:
**ARK/Evolve edits the harness, never the kernel.** That boundary is what makes evolution measurable,
and it is a direct application of AHE's controllability constraint `[AHE §3.3]`.

---

## 4. The Five Models

Each model is presented the same way: the borrowing, the mapping, and — the part that matters — the
questions it answers before you have asked them.

### 4.1 MM1 — The Run is a Process

**Borrowed from:** operating systems.

| Runtime concept | Operating-system analogue |
|-----------------|--------------------------|
| Run | Process |
| Episode | Scheduler timeslice |
| Step | Instruction |
| Checkpoint | Context-switch save |
| Lease | Current ownership by a core |
| Park | Blocked on I/O |
| Worker | CPU core |
| Sweeper | Reaper for orphaned processes |
| Queue | Run queue |

The reference architecture makes this analogy explicit, describing a Run as the runtime's equivalent
of a process `[DAR §3.1]`.

**Questions it answers in advance:**

- *Why does a parked run cost nothing?* Because a blocked process holds no core. Nothing about being
  blocked implies occupying anything.
- *Why can there be far more runs than workers?* For the same reason a laptop runs six hundred
  processes on eight cores.
- *Why is the episode budget a dial rather than an architecture?* Because a timeslice is a dial.
  Setting it to one step reproduces strict round-robin exactly `[DAR §5.1]`.
- *Why preempt at step boundaries specifically?* Because that is where the state is consistent enough
  to save — the same reason a kernel preempts between instructions, not during one.
- *And the cold open:* why renew the lease per step rather than hold it? Because a core does not own
  a process; it borrows it for a slice.

**Where it breaks down.** A process's instructions are known before it runs; a run's steps are not
(Chapter 2 §2.2). Do not use MM1 to reason about planning.

### 4.2 MM2 — The System is a Ledger

**Borrowed from:** double-entry accounting.

| Runtime concept | Accounting analogue |
|-----------------|--------------------|
| `events` table | The journal — append-only, never edited |
| `activities` table | The ledger of what happened and what it cost |
| Budget reservation | An encumbrance against a balance |
| Settlement | Posting the actual against the reservation |
| Replay | Reading the journal to reconstruct a balance |
| Change manifest (Level 5) | The evidence ledger of harness edits `[AHE §3.3]` |

**Questions it answers in advance:**

- *Why is the event log append-only?* Because ledgers are. You do not edit a journal entry; you post
  a correcting one.
- *Why reserve before spending rather than record after?* Because otherwise a run can exceed its
  ceiling by everything currently in flight `[DAR §6.4]`. Accountants encumber before they commit for
  exactly this reason.
- *Why does a replan write new step rows rather than update old ones?* Same principle `[DAR §11]`.
  History is not editable.
- *Why monitor the gap between reservation and settlement?* Because a persistent drift means your
  cost estimates are systematically wrong, and therefore your admission decisions are too
  `[DAR §15]`.
- *Why does the activities table answer "has this already happened?"* Because that is what a ledger
  is *for*.

**Where it breaks down.** Ledgers assume entries are comparable and additive. Harness components are
not — three edits that each help do not sum to the sum of their help `[AHE §4.4.1]`. Do not use MM2
to reason about component interaction.

### 4.3 MM3 — Every Boundary is a Contract

**Borrowed from:** protocol and interface design.

| Boundary | The contract | Who might not cooperate |
|----------|-------------|------------------------|
| Model ↔ tool | Input schema | the model |
| Runtime ↔ domain | Command in, event out | the domain |
| Step ↔ grader | Deterministic checks | the model that produced the output |
| Runtime ↔ human | Gate question and signed decision | the human, by never answering |
| Fetched content ↔ run | Data, never instruction | whoever wrote the content |
| Harness edit ↔ next round | Predicted fixes and regressions `[AHE §3.3]` | the edit itself |

**Questions it answers in advance:**

- *Where does enforcement belong?* Where non-compliance is impossible, not where it is requested.
  This is the same conclusion Chapter 1 reached from the constraint hierarchy and the reference
  architecture reaches from the pure/effectful tag `[DAR §8.1]`, arrived at from a third direction.
- *What makes a contract real?* A verifier. A contract nobody checks is a preference.
- *Why must every harness edit carry a prediction?* Because an edit with no falsifiable claim is a
  rationale, and rationales cannot be evaluated. Pairing each edit with a self-declared prediction
  verified against the next round's outcomes is precisely what turns it into a contract
  `[AHE §3.3]`.
- *Why is fetched content never instruction?* Because the contract with a web page is "you supply
  data." Content that alters the plan has broken a contract you never agreed to `[DAR §8.4]`.

`[INF]` The unifying observation, and the reason this model earns a slot: *make the contract
structural rather than advisory*. `[DAR §8.1]` says an effectful tool must be uncallable without a
gate. `[AHE §3.3]` says an edit must be falsifiable by the next evaluation. These are the same move
at two different layers — replacing good intentions with a mechanism that does not require them.

**Where it breaks down.** Contracts assume both parties are identifiable. In a multi-agent run,
responsibility for a failure may be genuinely distributed (Chapter 19).

### 4.4 MM4 — Non-Determinism is Quarantined

**Borrowed from:** functional programming's separation of pure computation from effects, and from
hardware fault containment.

The rule, stated in `[DAR §6.1]`: model calls, network fetches, clock reads, and randomness all live
inside activities and nowhere else. Because every non-deterministic operation is isolated inside an
idempotent, checkpointed construct, the orchestration around it is effectively deterministic given
the run state and the event log.

**Questions it answers in advance:**

- *Why can we replay a run at all?* Because everything outside the quarantine is a function of state
  and events, so resuming replays decisions and reuses results rather than re-rolling the dice.
- *Why is a `time.time()` call in the run driver a bug?* Because it is non-determinism outside the
  quarantine. It will not fail today; it will make a replay disagree with the original in six months.
- *Why is testing this system tractable?* Because the quarantine boundary is exactly where you insert
  a fake (Chapter 40). Everything on the deterministic side is testable by ordinary means.
- *Why is the golden set nearly free to run?* Because activities are idempotent and their results are
  persisted, so replaying a recorded run is a database read rather than a re-spend `[DAR §9.3]`.

**Where it breaks down.** The quarantine contains non-determinism; it does not make it go away.
Two runs of the same task still diverge. Do not use MM4 to reason about evaluation, where variance
is the central problem and the answer is repeated rollouts, not containment.

### 4.5 MM5 — Control Plane and Data Plane

**Borrowed from:** network and cluster architecture.

| Plane | Carries | Characteristics |
|-------|---------|-----------------|
| **Control** | Planning, driving episodes, grading, projections, signal handling | cheap, frequent, must stay responsive |
| **Data** | Model calls, tool execution | expensive, slow, variable, rate-limited |

`[DAR §5.4]` partitions these into fast and slow work classes for this reason: a single queue serving
items of widely different latency produces a convoy, where slow items delay fast ones by up to the
slow item's service time.

**Questions it answers in advance:**

- *Why two queues?* Because mixing them makes control-plane latency a function of data-plane latency.
- *Why must no scarce resource be held across a model call?* Because that is a data-plane operation
  holding a control-plane resource, which couples the planes `[DAR §5.2]`. The custody rule is this
  model's central consequence.
- *Why is fast-queue depth the earliest warning signal?* Because the control plane falling behind is
  the first symptom of almost everything `[DAR §15]`.
- *Why does the edge run no model call?* Because the edge is control plane, and a model call is data
  plane.
- *Why can a person steer a run in under two seconds while a model call takes ninety?* Because
  steering is control-plane work and does not queue behind data-plane work.

**Where it breaks down.** The planes are separated by latency class, not by importance. A data-plane
failure is not less serious; it is differently urgent.

### 4.6 Choosing the lens

| If the question is about… | Use |
|---------------------------|-----|
| Who runs this, when, and for how long | MM1 Process |
| Whether something already happened, and what it cost | MM2 Ledger |
| Where a rule should be enforced | MM3 Contract |
| Why replay, recovery, or testing is sound | MM4 Quarantine |
| Why something is slow, starved, or coupled | MM5 Planes |

---

## 5. The Reference System

### 5.1 ARK — the runtime

**What it is.** A domain-independent agent runtime kernel. Python. One transactional database, one
queue, nothing else on the substrate `[DAR §4.1]`.

**What it contains.** Relay, run driver, activity runner, sweeper, two queues, eight tables.

**What it deliberately does not contain.** Any knowledge of coding, repositories, patches, or
customers. If ARK ever imports from Atlas, we have made a mistake and Chapter 6's structural test
will catch it.

**Its extension surface.** Six ports and nothing else: planner, tool, model, grader, approval, domain
`[DAR §10]`. The handbook treats this as a strict test — if something you need to change is not one
of the six, the architecture is wrong for the product.

**Scale target.** Hundreds of concurrent runs across tens of tenants. Explicitly *not* millions,
which is a disqualifier for building rather than buying `[DAR §2.4]`. Atlas is sized to stay in the
zone where this architecture is the right answer.

### 5.2 Atlas — the product

**What it does.** A customer connects a repository. When an issue is labelled for automation, Atlas
opens a run: it reads the issue, explores the repository, writes a patch, runs the test suite,
iterates until the suite passes, and opens a pull request for a human to review.

**Why a coding agent.** Three reasons, and the third is the real one.

1. Both primary sources live near this domain — AHE evaluates on terminal and repository benchmarks
   `[AHE §4.1]`, and the runtime architecture's examples are repository-flavoured.
2. The reader is a Full Stack AI Engineer and will not need the domain explained.
3. `[INF]` Coding agents have *genuine irreversibility*. Pushing a branch, opening a pull request,
   and running arbitrary shell in a sandbox with network access are all things you cannot take back.
   A reference product without irreversible actions would let us skip half the architecture, and the
   half we skipped is the half that matters.

**Atlas's tools, tagged.** The pure/effectful split from Chapter 1, made concrete:

| Tool | Effect | Notes |
|------|--------|-------|
| `tool.repo.read_file` | pure | |
| `tool.repo.search` | pure | |
| `tool.shell.run_command` | pure *within the sandbox* | see below |
| `tool.test.run_suite` | pure | |
| `tool.repo.apply_patch` | pure | writes to the sandbox working tree only |
| `tool.repo.push_branch` | **effectful** | gated |
| `tool.repo.open_pull_request` | **effectful** | gated |
| `tool.notify.comment_on_issue` | **effectful** | gated; visible to the customer |

`[INF]` The shell row is the interesting one and worth pausing on. A shell inside a fresh, isolated
sandbox is pure *by containment*, not by nature — its effects are real but they die with the sandbox.
This is the same isolation property AHE relies on when it runs every rollout in a fresh remote
sandbox so shell side effects cannot leak between tasks `[AHE App. A]`. The moment that sandbox has
outbound network credentials, the tag is wrong. Chapter 31 turns this into a rule.

**Atlas's harness.** All seven component types from Chapter 1 are present. Chapter 43 exposes them as
files; ARK/Evolve edits them from Chapter 46 onward.

### 5.3 The cast

Three roles recur, so that "a human decides" always has a face.

| Role | Does |
|------|------|
| **The tech lead** at a customer | Resolves gates. Approves the push, or does not. May never answer. |
| **The on-call engineer** at Atlas | Watches dashboards, diagnoses incidents, gets paged by Chapter 34's signals |
| **The harness maintainer** at Atlas | Owns the seven components. Replaced, in Level 5, by ARK/Evolve — under supervision |

### 5.4 What Atlas is not

To keep the reference honest: Atlas is single-region, has no cross-region durable timers, does not
need sub-second latency, and does not run untrusted customer code outside a sandbox. Each of those
would change an answer somewhere in the book, and where a chapter's conclusion depends on one of
them, it will say so.

---

## 6. Runtime Sequence

One Atlas run, narrated once through each lens. Same events, five readings.

```
                                                              TIME VIEW

  the run:  issue labelled -> plan -> explore -> patch -> test ->
            gate -> push -> pull request opened

  MM1 PROCESS
     a process is created, scheduled onto a worker for a 60-second
     timeslice, preempted at a step boundary, rescheduled, blocks on
     I/O at the gate, is woken by an interrupt, terminates

  MM2 LEDGER
     eleven activities posted; $6.40 reserved across them, $4.85
     settled, $1.55 released; four events journalled; one replan
     writes new step rows and edits none

  MM3 CONTRACT
     each tool call validated against its schema; the push is
     structurally blocked until the tech lead's decision is recorded;
     the grader's checks -- patch applies, suite passes -- are the
     contract the output is measured against

  MM4 QUARANTINE
     eleven non-deterministic operations, all inside activities;
     the driver's own decisions are a pure function of run state and
     the event log, which is why the crash at step 7 cost one step

  MM5 PLANES
     eleven data-plane operations at 20-90 seconds each; roughly forty
     control-plane operations at under 5 milliseconds each; the tech
     lead's approval reaches the run in 1.2 seconds because it never
     queues behind a model call

  Figure 3.3 -- One run, five readings (D4 Sequence, abridged)
```

`[INF]` The exercise is not decorative. Each reading surfaces a different question. MM2 asks why
$1.55 was released and whether that gap is systematic. MM5 asks why forty control operations were
needed for eleven data operations. MM1 asks why the timeslice was sixty seconds. None of those
questions occurs to you while holding a different lens.

---

## 7. State Management

What each model says about where state belongs — the five lenses applied to one question.

| Lens | Says |
|------|------|
| MM1 Process | State belongs in the process table, not in the core. A worker holds nothing it cannot lose. |
| MM2 Ledger | State is derivable from the journal. If it is not in the log, it did not happen. |
| MM3 Contract | State crossing a boundary must be explicit in the contract; implicit shared state is a broken interface. |
| MM4 Quarantine | Deterministic state is reconstructible and need not be stored; non-deterministic results must be. |
| MM5 Planes | Control-plane state is small, hot, and transactional. Data-plane state is large, cold, and referenced. |

They agree, which is the point — five independently borrowed models converging on the separation
`[DAR §3.3]` states directly: run state in the runtime, domain truth in the domain, and neither on
the other's side.

---

## 8. Interfaces

ARK's surface, as used throughout the book. Full signatures in Appendix E.

```python
# submission and observation
submit(goal: Goal) -> RunId
stream(run_id: RunId) -> AsyncIterable[Progress]      # telemetry, not facts

# control
signal(run_id: RunId, kind: SignalKind, payload: dict) -> None
resolve(approval_ref: ApprovalRef, decision: Decision, signer: str) -> None

# the six ports Atlas implements
PlannerPort · ToolPort · ModelPort · GraderPort · ApprovalPort · DomainPort
```

`[INF]` Note what is absent: there is no `run_step()`, no `get_state()` that returns mutable
internals, and no way for a caller to advance a run manually. The surface is deliberately narrow
because every additional entry point is another place the one-driver-at-a-time invariant can be
violated.

---

## 9. Data Structures

Atlas-specific shapes, so later chapters have something concrete to name.

| Structure | Fields | First used |
|-----------|--------|-----------|
| `AtlasGoal` | tenant_id, repo_ref, issue_id, base_branch, budget_cap | Ch 8 |
| `PatchStep` | step_id, target_paths, rationale, activity_id | Ch 10 |
| `TestVerdict` | suite_id, passed, failed_names, duration_ms | Ch 28 |
| `PushRequest` | branch_name, commit_sha, approval_ref | Ch 30 |
| `AtlasTrajectory` | run_id, messages, tool_calls, outcome, tokens | Ch 16, Ch 44 |

`AtlasTrajectory` is the one to remember. It is an output of Chapter 16 and the sole input to
Chapter 44, and it is the reason the observation system is a Level 2 concern rather than a Level 4
afterthought.

---

## 10. Communication

Where the reference system's pieces talk, and where they deliberately do not.

| From | To | Carries | Notes |
|------|----|---------|-------|
| Atlas surface | ARK edge | goals, approvals, signals | the only inbound path |
| ARK kernel | Atlas ports | plan, tool, model, grade, ask | the only outbound path |
| Atlas domain | ARK substrate | truth plus its event | one transaction |
| ARK kernel | Atlas surface | progress | direct, never durable |
| Atlas harness | ARK/Evolve | trajectories | read-only, one direction |
| ARK/Evolve | Atlas harness | component edits | write-only, one direction |
| ARK/Evolve | ARK kernel | **nothing** | the boundary that makes evolution measurable |

The last row is a rule, not an observation. AHE's controllability constraint keeps the evolution
agent inside the harness workspace, with the runs directory, tracer, verifier, and model
configuration read-only `[AHE §3.3]` — because an unconstrained self-modifier takes the shortcut of
disabling the verifier or raising the reasoning budget, and every recorded gain stops being
attributable to harness edits.

---

## 11. Failure Modes

Failure modes of the *models*, not of the system. A mental model fails by being applied where it does
not hold, and each failure is quiet.

| Misapplication | Produces | Correct lens |
|----------------|----------|-------------|
| MM1 to planning | Assuming steps are known in advance; static validation and pre-authorisation | MM3 Contract |
| MM2 to component interaction | Assuming edits are additive; stacking fixes and expecting the gains to sum `[AHE §4.4.1]` | Ch 48 directly |
| MM3 to multi-agent failures | Looking for the one party at fault when responsibility is distributed | Ch 19 |
| MM4 to evaluation | Assuming a replay proves the agent will behave; confusing containment with reproducibility | Ch 41 |
| MM5 to prioritisation | Treating data-plane failures as less serious because they are slower | Ch 36 |
| Any model, unstated | The cold open: forty comments and no convergence | say which lens you are using |

`[INF]` The last row is the practical recommendation. In design discussion, name the lens out loud.
"I am reasoning about this as a scheduling question" resolves in one sentence what forty comments
cannot.

---

## 12. Scalability

How each model scales as the system grows — and each has a ceiling worth knowing.

| Model | Holds until |
|-------|------------|
| MM1 Process | Runs need to coordinate with each other. Processes do not, generally; sub-runs (Ch 19) strain the analogy. |
| MM2 Ledger | Entries stop being comparable. Token cost is comparable; harness quality is not. |
| MM3 Contract | The number of boundaries exceeds what anyone tracks. Appendix E exists for this reason. |
| MM4 Quarantine | Non-determinism appears outside activities — a cached model response, a memoised clock read, a library that seeds itself. Chapter 40 tests for it. |
| MM5 Planes | A third class appears. Evaluation workloads (Ch 41) are neither fast control nor per-run data, and Chapter 23 gives them their own class. |

The honest summary: all five models are load-bearing through Level 4 and all five are strained by
Level 5, which is one reason self-evolving systems are genuinely hard rather than merely unfamiliar.

---

## 13. Production Engineering

### 13.1 Best practices

- **Name the lens in design discussions.** Cheapest intervention in this chapter.
- **Keep one reference system in your own documentation, as this book does.** Teams that switch
  examples per document produce engineers who understand every component and no system.
- **Write down what your reference system is not.** §5.4 is short and prevents a class of argument
  where two people are optimising for different unstated requirements.
- **Tag every tool as pure or effectful on the day it is written.** Retrofitting the tag across a
  mature tool surface is an audit, and Chapter 2 §13.2 ranks it as one of the hardest retrofits.

### 13.2 Trade-offs

| Choice | Buys | Costs |
|--------|------|-------|
| Five models rather than one | Each question gets the lens that fits | The reader must choose, and can choose wrong |
| A single reference system | Integration is never left as an exercise | Some conclusions are Atlas-shaped; §5.4 bounds this |
| Sandbox-as-purity for shell | A powerful tool without a gate on every command | One misconfiguration reclassifies it silently |

### 13.3 Anti-patterns

| Anti-pattern | Why it fails | Diagnosed in |
|--------------|-------------|--------------|
| **Metaphor collision** | Two correct models, one unstated disagreement, forty comments | §1.1 |
| **Single-metaphor thinking** | Forcing a scheduling answer onto a contract question | §4.6 |
| **The illustrative example** | A new example per chapter; the reader never sees the system | §1.3 |
| **Purity by assumption** | Tagging a tool pure because it usually is | Ch 31 |
| **Evolution reaching into the kernel** | Every recorded gain stops being attributable | Ch 46 |

---

## 14. Relation to AHE

Two of the five models are load-bearing in Level 5, and one is where AHE breaks the model outright.

**MM3 Contract is AHE's core mechanism.** Decision observability pairs every edit with a self-declared
prediction that the next round verifies, so each edit becomes falsifiable and ineffective ones are
reverted at file granularity `[AHE §3.3]`. That is MM3 applied to an edit rather than to an
interface. Chapter 45 builds it, and the reason it works is the same reason a gate works: the claim
is checked by a mechanism rather than defended by an argument.

**MM2 Ledger is AHE's bookkeeping.** The change manifest is described in the source as the loop's
evidence ledger `[AHE §3.3]`, and each logical edit becomes one commit with file-level diffs and
rollback granularity `[AHE §3.1]`. Append-only history, revertible entries, reconstructible state.

**MM2 also breaks, and the break is a finding.** Ledger entries are additive; harness components are
not. Three positive single-component gains summing to +11.1 points delivered +7.3 combined
`[AHE §4.4.1]`. `[INF]` This is worth flagging now because the ledger model is seductive: it makes
you expect that a sequence of individually-verified improvements accumulates. It does not, and
Chapter 48 is about designing a loop that knows it.

**One model AHE lacks entirely.** There is no MM1 in the evolution loop — no notion of the *outer*
loop as a schedulable, resumable, interruptible process. It runs as a script over ten iterations
`[AHE Alg. 1]`. `[FUT]` Applying this handbook's own runtime to its own evolution loop — making an
evolution campaign a Run, with gates, budgets, and human authority — is a proposal Chapter 49
develops and neither source attempts.

---

## 15. Industry Perspective

### Supported by the attached Durable Runtime architecture `[DAR]`

- A Run described as the runtime's equivalent of a process (§3.1).
- The Episode as a bounded window, with a step budget of one reproducing strict per-step execution
  (§5.1).
- The custody rule and its consequence for scarce resources (§5.2).
- Work-class partitioning to prevent convoying (§5.4).
- Non-determinism quarantined inside activities; orchestration deterministic given state and events
  (§6.1).
- Reserve-then-settle budgeting (§6.4).
- Golden-set replay being nearly free because activities are idempotent and persisted (§9.3).
- A replan writing new step rows rather than editing old ones (§11).
- Effectful tools structurally uncallable without a resolved gate (§8.1).
- Fetched content as data and never instruction (§8.4).
- The six ports as the entire extension surface, and the strictness of that test (§10).
- The substrate being one transactional database and one queue (§4.1).
- Fast-queue depth as the earliest symptom, and reservation-versus-settlement drift as a monitored
  signal (§15).
- Millions of concurrent runs as a disqualifier for building rather than buying (§2.4).
- Run state and domain state separation (§3.3).

### Supported by the attached AHE paper `[AHE]`

- Controllability: the evolution agent writes only inside the harness workspace, with runs, tracer,
  verifier, and model configuration read-only, blocking the shortcuts an unconstrained self-modifier
  would take (§3.3).
- Every edit paired with a self-declared prediction verified next round; ineffective edits reverted
  at file granularity (§3.3).
- The change manifest as the loop's evidence ledger; one commit per logical edit (§3.1, §3.3).
- Positive single-component gains summing to +11.1 points against +7.3 combined (§4.4.1).
- A fresh remote sandbox per rollout so shell side effects cannot leak between tasks (App. A).
- The outer loop as a fixed ten-iteration procedure (Alg. 1).

### Engineering inference `[INF]`

- The selection of these five models, and the claim that they taxonomise *questions* rather than the
  architecture.
- Each model's breakdown boundary, and the misapplication table in §11.
- Naming the lens aloud as a design-discussion practice.
- The load-bearing single reference system as a pedagogical requirement rather than a convenience.
- Shell-in-a-sandbox as pure by containment rather than by nature, and the fragility of that tag.
- The narrow public surface of ARK as a defence of the one-driver invariant.
- The observation that all five models are strained by Level 5.

### Industry best practice `[BP]`

- Process, ledger, contract, quarantine, and control/data-plane framings are all long-established in
  their home disciplines. Nothing about them is novel; the selection and the mapping are the
  contribution.

### Future proposal `[FUT]`

- Running an evolution campaign as a first-class Run inside the same runtime it is evolving, with
  gates, budgets, checkpoints, and human authority. Developed in Chapter 49; attempted by neither
  source.

---

## 16. Key Takeaways

1. **Five lenses, one system.** Process, Ledger, Contract, Quarantine, Planes. They taxonomise the
   questions, not the architecture.
2. **A good model predicts answers you have not asked for.** Each of the five was tested against that
   standard in §4, and each also has a stated breaking point.
3. **Identify the lens before arguing.** The cold open costs three days; naming the lens costs one
   sentence.
4. **They converge on state separation.** Five models borrowed from five disciplines all arrive at
   run state in the runtime and domain truth in the domain.
5. **ARK and Atlas carry the rest of the book.** A domain-independent kernel, a coding agent with
   genuine irreversibility, and a strict rule that evolution edits the harness and never the kernel.
6. **The ledger model is the seductive one.** It makes you expect verified improvements to
   accumulate. Measured, they do not.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Mental model (MM1-MM5)** | One of five borrowed pictures — process, ledger, contract, quarantine, planes — each answering a different class of design question. | `[INF]` | every chapter |
| **MM1 Process model** | Treats a run like an operating-system process that workers borrow for a slice of time, rather than a job a worker owns. | `[INF]` | Ch 5, Ch 17 |
| **MM2 Ledger model** | Treats every effect and every cost as an appended entry that is never edited, so history is auditable. | `[INF]` | Ch 22, Ch 35 |
| **MM3 Contract model** | Asks where a rule is enforced, and insists the answer be a place code runs rather than a sentence in a prompt. | `[INF]` | Ch 14, Ch 30 |
| **MM4 Quarantine model** | Confines everything unpredictable to marked regions, so the rest of the system can be replayed safely. | `[INF]` | Ch 21 |
| **MM5 Control plane vs data plane** | Separates the path that decides what happens from the path that carries the work, because the two have different latency and failure needs. | `[INF]` | Ch 7, Ch 9 |
| **ARK** | The Agent Runtime Kernel designed across this book: domain-independent, knows nothing about any particular product. | `[INF]` | every chapter |
| **Atlas** | The product built on ARK throughout the book: a coding agent that resolves issues in real repositories, with genuinely irreversible actions. | `[INF]` | every chapter |
| **ARK/Evolve** | The outer loop that edits Atlas's harness, introduced in Ch 20 and built in Level 5. It may edit the harness and never the kernel. | `[INF]` | Ch 20, Ch 46 |

---

**Level 0 is complete.** You can now say what an agent is, what part of it is yours, why it is a
distributed system, and which lens to reach for. Level 1 turns that into an architecture.

**Next:** Chapter 4 — *The Complete Runtime: Layers and Process Topology.* Six layers, two process
types, and the full wiring diagram that every remaining chapter zooms into.
