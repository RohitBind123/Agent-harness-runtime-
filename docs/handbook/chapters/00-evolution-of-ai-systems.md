```
  Level 0 · Chapter 0
  EVOLUTION OF AI SYSTEMS
  Requires   nothing
  Unlocks    C1 Anatomy of an Agent, C2 Why a Runtime Is a Distributed System,
             C3 Mental Models and the Reference System
  Diagrams   Light (3)
  Variant    Foundational — sections 4-9 describe models, not components
```

# Chapter 0 — Evolution of AI Systems

---

## 1. Motivation

### 1.1 Cold open

Atlas is asked to fix a failing test in a Django repository. It reads the issue, locates the
regression, writes a patch, runs the suite, and watches it go green. Forty-one minutes of correct
work.

Then it tidies up. It removes the scratch directory it created, and in the same command removes the
patched file, because the file was written into a path the model had earlier reasoned was temporary.
It runs one final check — the shell exit code of the cleanup command — sees `0`, and reports success.

The grader reads the repository. There is no patch. The run is marked failed.

Nothing in that trace is a reasoning failure. The model diagnosed the bug correctly, wrote a correct
patch, and verified it. Every individual decision was defensible. What failed was the *system around
the model*: nothing made the verified state protected, nothing made the final check mirror the
grader, and nothing made the destructive command require a second thought. A documented instance of
exactly this pattern — an agent reaching a passing state and then destroying it during cleanup —
appears in the AHE case studies `[AHE App. C.1.2]`.

### 1.2 Why this chapter exists

You are about to spend forty-nine chapters building the system around the model. Before any of it
makes sense, you need to know why it is shaped the way it is — and the honest answer is that it is
shaped by five successive failures.

Most accounts of agent history are capability histories: the models got better, so the agents got
better. That story is true and it is useless to you, because it explains nothing about why your
runtime needs a lease table. This chapter tells the other story. Each generation of AI system added
one capability and broke one guarantee. The broken guarantee is what the next generation was built
to restore. Follow the breaks and the architecture of Chapter 4 stops looking like an arbitrary pile
of components and starts looking like the only remaining option.

### 1.3 What previous framings got wrong

Three framings you will meet in the wild, and why each misleads:

- **"An agent is an LLM in a loop."** True in the way that "an operating system is a program that
  runs programs" is true. It is a definition that survives contact with a demo and fails contact
  with production, because it names the one part you do not have to build.
- **"Agent quality is model quality."** Contradicted by measurement. Holding the base model fixed
  and changing only the surrounding components moves task completion materially `[AHE §1]`; in one
  reported campaign, ten iterations of editing nothing but those components lifted single-attempt
  success from 69.7% to 77.0% `[AHE §4.2]`. The model was identical on both ends of that range.
- **"Agents are an ML problem."** They start as one and stop being one at roughly the four-minute
  mark. Beyond that horizon the dominant questions are durability, idempotency, concurrency, cost
  ceilings, and human authority — the standard concerns of a distributed system `[DAR §2.1]`.

---

## 2. High-Level Mental Model

### 2.1 Two axes, not one

The single most useful correction to make before Chapter 1: **capability and survivability are
independent axes, and progress along them happened at different times for different reasons.**

```
                                                       CONCEPTUAL VIEW
  survivability
  (what the system
   can survive)
      ^
      |
  high|                                     G3 . . . . . G4 . . . . . G5
      |                                     .
      |                                     .
      |                                     .
      |                                     .   <-- the discontinuity:
      |                                     .       a systems problem
      |                                     .       appears all at once
      |                                     .
   low|  G0 --------- G1 --------- G2 ------'
      |
      +------------------------------------------------------> capability
                                                    (what the model can do)

  Figure 0.1 -- The two axes of agent evolution (conceptual)

  G0 completion     G1 tool use      G2 loop
  G3 autonomy       G4 multi-agent   G5 self-evolution
```

G0 to G2 is a capability story: the model gained grounding, then effect, then control. Almost
nothing about the surrounding system had to change, which is why that era produced so many
impressive demos on so little infrastructure.

G2 to G3 is not a capability story. The model barely changed. What changed is that someone pointed
it at a six-hour task, and four properties appeared at once that ordinary request handling cannot
provide `[DAR §2.1]`. The vertical jump in Figure 0.1 is the subject of this book.

### 2.2 The forced move

The organising idea of this chapter, and the reading habit to carry into every later one:

> **Each generation added a capability by removing a guarantee. The next generation exists to
> restore that guarantee without giving the capability back.**

This is a forced move in the chess sense. Once you let a model decide when to stop, you have given
up bounded termination, and you must now build something that bounds it externally — or accept
unbounded cost. There is no third option and no clever prompt that recovers the guarantee. Every
component in Levels 2 and 3 is a forced move of this kind, and Section 11 lists them.

`[INF]` The five-generation taxonomy, the two-axis model, and the forced-move framing are the
handbook's own organising devices. Neither source proposes them. They are tools for thinking, not
findings.

---

## 3. High-Level Architecture

What accumulates, generation by generation. Read it as one diagram growing outward, not five
diagrams.

```
                                                             LAYER VIEW

  G0  COMPLETION
      +~~~~~~~~~~~~~~+
      |  Model       |          tokens in, tokens out
      +~~~~~~~~~~~~~~+          no state, no effect, one call

  G1  TOOL USE
      +--------------+  (1)  +~~~~~~~~~~~~~~+
      | Caller       |------>|  Model       |
      | (your code)  |<------|              |
      +------+-------+  (2)  +~~~~~~~~~~~~~~+
             | (3)
             v
      +==============+        caller decides everything except
      | Tool         |        which tool to request
      +==============+

  G2  THE LOOP
      +---------------------------------------------+
      |  LOOP  (in your process, in memory)         |
      |                                             |
      |   +--------+  (1)  +~~~~~~~~+               |
      |   | Loop   |------>| Model  |               |
      |   | Driver |<------|        |               |
      |   +---+----+  (2)  +~~~~~~~~+               |
      |       | (3)                                 |
      |       v                                     |
      |   +===+====+     the MODEL now decides      |
      |   | Tool   |     when the loop ends         |
      |   +========+                                |
      +---------------------------------------------+

  G3  AUTONOMY
      +---------------------------------------------------------+
      |  RUNTIME                                                |
      |                                                         |
      |  +----------+  +----------+  +----------+  +---------+  |
      |  | Planner  |  | Context  |  | Memory   |  | Grader  |  |
      |  +----------+  +----------+  +----------+  +---------+  |
      |                                                         |
      |  +-------------------------------------------------+    |
      |  |  LOOP  (bounded episode, checkpointed)          |    |
      |  +-------------------------------------------------+    |
      |                                                         |
      |  +----------+  +----------+  +----------+  +---------+  |
      |  | State    |  | Budget   |  | Gate     |  | Sandbox |  |
      |  | Store    |  | Ledger   |  | (human)  |  |         |  |
      |  +----+-----+  +----------+  +----------+  +---------+  |
      +-------|-------------------------------------------------+
              v
      [[ durable state ]]        the loop is no longer the system;
                                 it is one component of the system

  G4  MULTI-AGENT
      +---------------------------------------------------------+
      |  RUNTIME                                                |
      |    +-------------+        +-------------+               |
      |    | Parent Run  |------->| Child Run   |   isolated    |
      |    +-------------+<-------+-------------+   context     |
      +---------------------------------------------------------+

  G5  SELF-EVOLUTION
      +---------------------------------------------------------+
      |  RUNTIME  (components exposed as editable files)        |
      +---------------------------+-----------------------------+
                                  | traces
                                  v
      +---------------------------+-----------------------------+
      |  EVOLUTION LOOP                                         |
      |  distill evidence -> edit components -> predict ->      |
      |  measure -> keep or revert                              |
      +---------------------------------------------------------+

  Figure 0.2 -- Architectural accumulation across five generations
                (D1 High-Level Architecture)

  (1) request  (2) response, possibly a tool request  (3) execution
```

Two observations to carry forward.

**The model box never grows.** From G0 to G5 it stays the same shape: something that turns tokens
into tokens. Everything added is outside it. That is the harness `[AHE §1]`, and Chapter 1 gives it
a precise definition.

**G3 is where the diagram changes kind.** G0 through G2 are call graphs. G3 onward are system
diagrams with durable stores and out-of-band actors. The moment a box in your diagram is a *table*
rather than a function, you have crossed into this book's subject matter.

---

## 4. Low-Level Decomposition

Foundational variant: we decompose each generation's *structure*, not a component's internals.

### 4.1 G0 — The completion

```python
def complete(messages: list[Message]) -> str: ...
```

A pure function. Deterministic given a seed, no side effects, no memory between calls, no ability to
learn anything it was not told. Its ceiling is the ceiling of what fits in one prompt.

**Guarantee held:** everything. It cannot fail in any interesting way, because it cannot do anything.
**Capability missing:** grounding in current fact, and any effect on the world.

### 4.2 G1 — Tool use

The model gains a structured output channel. Instead of only prose, it may emit a request naming a
verb and its arguments. Your code executes the verb and returns the result.

```python
class ToolRequest(NamedTuple):
    tool_id: str          # e.g. "tool.repo.read_file"
    arguments: dict
```

The control loop is still yours. You called the model once, you executed at most one tool, you
decided the exchange was over.

**Guarantee held:** bounded work. One call, one tool, one return. Cost and latency are known before
you start.
**Guarantee broken:** purity. Something the model requested now touches your systems. `[INF]` This
is the first appearance of the pure-versus-effectful distinction that Chapter 14 turns into the
entire safety model.

### 4.3 G2 — The loop

Wrap G1 in iteration. Feed each tool result back as context and call the model again. Stop when the
model says it is finished.

```python
while True:
    reply = model.complete(messages)
    if reply.is_final:
        return reply
    result = tools.execute(reply.tool_request)
    messages.append(result)
```

Eight lines, and the most consequential eight lines in the history of the field. They move the
program counter out of your code and into a probability distribution.

**Capability gained:** multi-step work. The system can now do things that require discovering
information partway through.
**Guarantees broken — three at once:**

| Broken | Consequence |
|--------|-------------|
| Bounded termination | `is_final` is a model judgement. There is no proof the loop ends. |
| Bounded cost | Unbounded iterations times a per-call price. |
| Durability | The loop's entire state is Python locals. The process is the system. |

The third one is the quiet killer. In G0 and G1 there was nothing to lose on a crash, because the
work was one round trip. In G2 there are forty minutes of accumulated reasoning living in a variable.

### 4.4 G3 — Autonomy

Point the G2 loop at a task that takes hours rather than seconds, give it a filesystem and a shell,
and every one of the following becomes true simultaneously `[DAR §2.1]`:

- **The work outlives the request.** Minutes to days, across restarts and deploys.
- **The work is expensive and non-deterministic.** Retrying naively spends real money and produces
  different output each time.
- **The work touches the world.** Some steps are irreversible and must not happen without a human's
  word.
- **The work must be interruptible.** A person watching it go wrong must be able to redirect it
  without discarding what is already correct.

`[DAR §2.1]` also records how most systems meet these: an in-process loop inside an HTTP handler, a
timeout that abandons rather than cancels, an approval enforced by asking the model to behave, and
recovery that only happens at boot. Each is a specific defect with a specific fix, and the fixes are
Levels 1 through 3 of this book.

G3 therefore adds structure in four directions at once — planning, persistence, budgeting, and
authority. Figure 0.2 shows the result. Note what happened to the loop: it went from *being* the
system to being one bounded component inside it, which is the change Chapter 18 formalises as the
Episode.

### 4.5 G4 — Multi-agent

A run may found another run and wait on its completion. The honest framing, which the marketing
around this generation usually omits:

> `[INF]` The primary engineering benefit of a sub-agent is **context isolation**, not
> collaboration. A sub-agent is a mechanism for keeping two hundred thousand tokens of exploratory
> noise out of a parent's context window while returning a two-hundred-token conclusion.

Where genuine specialisation exists it is worth having, but it is the second reason, not the first.
Chapter 19 gives the decision rule for when a sub-agent is worse than a tool.

**Guarantee broken:** attribution. With one agent, a failure has one cause to find. With five, the
failure may be in an interaction none of them can see. This is the first appearance of a problem
that Level 5 meets again at full strength, where components that each help individually are measured
to interact non-additively `[AHE §4.4.1]`.

### 4.6 G5 — Self-evolution

The components of the harness are exposed as files an agent may read and rewrite. A second loop
wraps the first: run the agent over a task set, distil what went wrong, edit components, predict
what the edit will fix, measure next round, keep or revert `[AHE §3]`.

**Capability gained:** the system improves without a human in the edit loop, and keeps pace with
base-model releases that would otherwise leave a hand-tuned harness behind `[AHE §1]`.
**Guarantee broken:** the system's own account of itself. The loop can say why an edit should help
and be roughly right — its fix predictions land about five times better than chance — but its
predictions about what the same edit will *break* land only about twice better than chance
`[AHE §4.4.2]`. It can see forward but not sideways. Chapter 48 is about designing around that.

---

## 5. The Accumulating Component Inventory

Each generation's contribution to the vocabulary, and the chapter that owns it. This table is the
handbook's spine in miniature.

| Gen | Introduced | Owned by |
|-----|-----------|----------|
| G0 | Model, context window, token budget | Ch 13 |
| G1 | Tool, tool description, tool result, effect classification | Ch 14, Ch 15 |
| G2 | Loop driver, termination condition, trajectory | Ch 18, Ch 16 |
| G3 | Plan, Run, Episode, Step, Activity, Park | Ch 5, Ch 10, Ch 18 |
| G3 | Checkpoint, lease, idempotency key, budget ledger | Ch 17, Ch 21, Ch 35 |
| G3 | Gate, approval, signal, sandbox | Ch 30, Ch 31 |
| G3 | Grader, verdict, deterministic check | Ch 28 |
| G4 | Sub-agent, delegation contract, context isolation | Ch 19 |
| G5 | Harness component, evidence corpus, change manifest, attribution verdict | Ch 43–47 |

Read the left column downward and you have the reason the book is fifty chapters long. Nothing in
it was designed; all of it was forced.

---

## 6. Runtime Sequence

The same task, `fix the failing test`, executed by G2 and by G3. Watch where each one holds
something and where it holds nothing.

```
                                                              TIME VIEW

  G2  IN-PROCESS LOOP                    G3  DURABLE RUN
  ---------------------------            ------------------------------------
  HTTP request arrives                   goal arrives at the edge
    |                                      |
    | holds: connection, thread,           | edge writes a command + event
    |        all state in RAM              | in ONE transaction, then returns
    |                                      |
  loop iteration 1                       relay claims the event
    call model  (20 s)                     |
    execute tool                         run driver takes a lease,
    |                                    runs an EPISODE:
  loop iteration 2                         step -> checkpoint -> step
    call model  (20 s)                     |  (holds no connection
    execute tool                           |   across the model call)
    |                                      |
  ... 60 more iterations ...             activity dispatched to the slow queue
    |                                      |  leased, budgeted, abortable
  process is killed at iteration 41      worker is killed mid-activity
    |                                      |
    X  ALL WORK LOST                      sweeper expires the lease
       no record of 40 minutes            activity is re-claimed
       no record of spend                 identity check: already completed
       no record of what was touched      -> result replayed, NOT re-spent
                                            |
                                          run resumes at its last checkpoint

  Figure 0.3 -- The same task under G2 and G3 (D4 Sequence, abridged)
```

The right-hand column is not more complicated because it is over-engineered. It is more complicated
because it answers a question the left-hand column cannot: *what happens when the process dies?*
Every added box in Figure 0.2 exists to make some version of that answer be "not much."

---

## 7. State Management Across Generations

Where the truth lived, and what killed it.

| Gen | State lives in | Survives a crash? | Characteristic loss |
|-----|---------------|-------------------|---------------------|
| G0 | Nowhere | N/A | Nothing to lose |
| G1 | The caller's stack frame | No | One round trip |
| G2 | Process memory: a `messages` list | No | The entire run |
| G3 | A transactional database; the process is a temporary reader of it | Yes | At most the single in-flight step |
| G4 | Same, plus a parent–child run relationship | Yes | As G3, per run |
| G5 | Same, plus a versioned component workspace under git | Yes | An iteration, revertible at file granularity `[AHE §3.1]` |

The G2-to-G3 row is the whole transition in one line. `[DAR §13]` states it as an invariant the
handbook will hold for the rest of the book: no work outlives the process that started it, because
no work lives in a process — state is a row, and a worker is a temporary reader of it.

Chapter 6 splits this further, because "state" turns out to be three different things with three
different owners: run state, domain state, and model state.

---

## 8. Interfaces Exposed

The public surface each generation offers its caller.

| Gen | Interface | Caller's obligation |
|-----|-----------|---------------------|
| G0 | `complete(messages) -> str` | Supply everything the model needs to know |
| G1 | `complete(messages, tools) -> str \| ToolRequest` | Execute requested verbs; decide when to stop |
| G2 | `run(goal) -> Result` — blocking | Wait; absorb unbounded latency and cost |
| G3 | `submit(goal) -> RunId` + `stream(RunId)` + `signal(RunId, kind)` — non-blocking | Poll or subscribe; answer gates; own the budget ceiling |
| G4 | As G3; sub-runs are internal and not addressable from outside | Unchanged — a virtue, not an omission |
| G5 | As G3, plus an offline loop over recorded runs | Supply a benchmark and a verifier |

The G2-to-G3 signature change is the one to notice. A blocking call that returns a result becomes a
submission that returns an identifier. That is the same change that separates a function from a
process, and it is why Chapter 5 calls a Run "the runtime's equivalent of a process."

---

## 9. Data Structures Introduced

Logical shapes only; fields are given properly in the chapters that own them.

| Structure | Gen | Shape | Owner |
|-----------|-----|-------|-------|
| `Message` | G0 | role, content | Ch 11 |
| `ToolRequest` / `ToolResult` | G1 | tool_id, arguments / content, is_error | Ch 14 |
| `Trajectory` | G2 | ordered messages of one attempt | Ch 16 |
| `Plan` / `Step` | G3 | plan_id, ordered steps / step_id, tool_id, input | Ch 10 |
| `Run` | G3 | id, goal, state, plan_id, version, lease, budget | Ch 17 |
| `Activity` | G3 | activity_id (a hash), state, result, attempts | Ch 21 |
| `Verdict` | G3 | checks, model_judgment, decision | Ch 28 |
| `ChangeManifest` entry | G5 | evidence, root cause, fix, predicted fixes, risk tasks | Ch 45 |

`[INF]` One pattern is worth naming now, because it recurs at four different scales. Every structure
from `Run` downward carries an **identity that determines whether prior work may be reused**. Reuse
without identity is the origin of the most expensive bug class in the architecture: a confident,
well-formed, wrong result with no error and no alert `[DAR §6.2]`. Chapter 21 gives the identity
rule; Chapter 47 applies the same reasoning to harness edits.

---

## 10. Communication

| Gen | Inputs | Outputs | Events | Depends on |
|-----|--------|---------|--------|-----------|
| G0 | prompt | completion | none | model provider |
| G1 | prompt, tool schemas | completion or tool request | none | provider, your verbs |
| G2 | goal | final answer | none — the loop is opaque | provider, verbs, your process staying alive |
| G3 | goal, approvals, signals | streamed progress, terminal result | facts appended to a durable log | database, queue, provider, sandbox, a human |
| G4 | as G3 | as G3 | plus child-run lifecycle facts | as G3 |
| G5 | benchmark, verifier, recorded traces | edited components, a manifest | plus per-iteration attribution verdicts | as G4, plus version control and an evaluation harness |

Two rows deserve attention.

**G2 emits no events.** Its execution is unobservable from outside by construction. You cannot ask a
running G2 loop what it is doing, cannot redirect it, and cannot reconstruct afterwards what it did.
Chapter 16 exists because of this row.

**G3's dependency list contains a human.** That is not a soft dependency. `[DAR §8.1]` is explicit
that an effectful step must be structurally impossible without a resolved approval, enforced in the
code path that invokes tools — a model instructed to ask permission is a model that will *usually*
ask permission, which is a hope with good compliance statistics rather than a control.

---

## 11. Failure Modes

### 11.1 The characteristic failure of each generation

Each generation has a signature failure. Recognising which one you are looking at tells you which
level of this book to open.

| Gen | Characteristic failure | Fixed in |
|-----|----------------------|----------|
| G0 | Confident fabrication — the model asserts what it was never given | Ch 11, Ch 12 |
| G1 | Malformed or hallucinated tool calls; unbounded blast radius from a single verb | Ch 14, Ch 15 |
| G2 | Non-termination; runaway cost; total loss of work on process death | Ch 18, Ch 21 |
| G3 | Silent correctness failure — a well-formed wrong result that passes its own check | Ch 28 |
| G4 | Unattributable failure; interference between components that each work alone | Ch 19, Ch 48 |
| G5 | Regression blindness — the loop breaks what it did not predict it would break | Ch 48 |

### 11.2 The one to fear

`[DAR §9.1]` is unambiguous about which of these actually kills products, and it is not the
reliability defect. Pool exhaustion produces an alert and gets fixed. A confidently wrong run
produces an artifact someone acts on.

The cold open in §1.1 is a G3 silent correctness failure, and it is worth re-reading now that the
taxonomy exists. The reasoning was sound. The tooling executed faithfully. The self-check returned
success. Every layer reported health, and the output was still wrong — because the check the system
performed was not the check that mattered `[AHE App. C.1.1]`. There is no monitoring dashboard that
catches this. There is only a grader whose checks are grounded in something other than a model's
opinion, which is Chapter 28.

### 11.3 Recovery, rollback, retry — by generation

| Gen | Retry | Rollback | Recovery |
|-----|-------|----------|----------|
| G0–G1 | Free and safe: idempotent by nature | Not applicable | Not applicable |
| G2 | Unsafe: re-runs side effects and re-spends | None | Restart from zero |
| G3 | Safe: identity-keyed replay of completed work | Compensation, plus parks for anything irreversible | Continuous lease sweeping, resume at last checkpoint |
| G5 | As G3, plus retry of an *edit* | File-granularity revert of rejected edits via version control `[AHE §3.1]` | Attribution verdict decides keep or revert |

The G2 row is why "just add a retry" is the most expensive four words in this field. Retry is only
safe on top of identity, and identity is only meaningful on top of durable state.

---

## 12. Scalability

| Gen | Unit of scale | Ceiling | What breaks first |
|-----|--------------|---------|-------------------|
| G0 | Stateless replicas | Provider rate limits | Nothing structural |
| G1 | Stateless replicas | Provider limits; tool backend capacity | The tool backend |
| G2 | One process per run | Memory and process count; a run pins a worker for its whole life | Worker exhaustion long before model limits |
| G3 | Runs are rows; workers are interchangeable | Database throughput and provider concurrency | Whichever resource lacks its own budget |
| G4 | As G3; a parent parks while a child runs, holding nothing | As G3 | Fan-out without admission control |
| G5 | Offline and batch; scales with evaluation cost, not serving cost | Wall-clock per iteration; one reported campaign ran ten iterations in roughly 32 hours `[AHE §4.2]` | Benchmark execution, not the loop |

The G2 row states the scaling problem in its purest form: **a run pins a worker for its entire
lifetime.** A six-hour task occupies a process for six hours. Everything in Chapter 23 follows from
refusing that, and the refusal has a name — `[DAR §5.2]` calls it resource custody: a resource that
is both scarce and exclusively held must never be held across an operation whose latency is high and
variable.

---

## 13. Production Engineering

### 13.1 The question to answer before Chapter 1

**Which generation are you actually building?** Getting this wrong in either direction is expensive.

`[DAR §2.4]` gives three honest disqualifiers for the full architecture, and they are worth taking
literally:

- If your work finishes in one turn and nothing irreversible happens, all of this is cost with no
  return. Write the handler and move on.
- If nothing you do is irreversible, roughly half the machinery — gates, budget reservations, the
  effectful tag, the approval port — exists to prevent damage that cannot occur. Delete that half
  rather than implementing it out of completeness.
- If you need cross-region durable timers or millions of concurrent runs, buy a durable-execution
  engine instead of growing one.

`[INF]` A working heuristic: if your longest task is under two minutes, you are building G2 and
should stop reading at Chapter 20. Past ten minutes you are building G3 whether or not you meant to.

### 13.2 Trade-offs

| Choice | Buys | Costs |
|--------|------|-------|
| Model decides termination (G2+) | Genuine multi-step work | Bounded termination and bounded cost, permanently |
| Durable state (G3) | Survivability, observability, interruptibility | A database on the hot path; every step needs an identity |
| Sub-agents (G4) | Context isolation | Attribution, and a second place for failures to hide |
| Self-evolution (G5) | Improvement without human edit cycles | A second system to operate, and a loop blind to its own regressions |

### 13.3 Anti-patterns introduced here

Each is indexed in Appendix H and diagnosed in the chapter named.

| Anti-pattern | Why it fails | Diagnosed in |
|--------------|-------------|--------------|
| **The G2-in-production** | Shipping an in-process loop inside an HTTP handler and discovering durability at the first deploy | Ch 4, Ch 21 |
| **Generation cargo-culting** | Adopting sub-agents or an evolution loop before the runtime beneath them is measurable | Ch 19, Ch 42 |
| **Capability substitution** | Answering a systems failure with a better prompt. The cold open cannot be fixed with words | Ch 30, Ch 15 |
| **Timeout as cancellation** | Abandoning the caller's wait while the operation continues, leaking resources and landing side effects after everyone gave up `[DAR §5.5]` | Ch 30 |
| **Self-graded success** | Letting the system decide whether it succeeded using a check it invented | Ch 28 |

---

## 14. Relation to AHE

Forward reference — this chapter is upstream of the evolution loop rather than shaped by it.

AHE is generation five in this taxonomy, and its central premise reframes everything above. If the
harness is what carries agent capability, and if the optimal harness is specific to a base model and
must be re-adapted as that model changes `[AHE §1]`, then the accumulation shown in Figure 0.2 is not
a finished staircase. It is a surface that has to keep moving.

Three claims from this chapter are the ones AHE later operates on:

1. **The model box never grows** (§3). Everything AHE edits is outside it; the base model is held
   fixed throughout `[AHE §3]`.
2. **Each generation added components** (§5). Those components are AHE's action space, and the loop
   works because each is exposed as a separate file rather than tangled together `[AHE §3.1]`.
3. **G2 emits no events** (§10). The evolution loop consumes trajectories; a generation that cannot
   be observed cannot be evolved. Chapter 16 is the prerequisite that makes Chapter 44 possible.

The chapter also plants the limit. Section 4.6 notes that the loop predicts its fixes far better
than chance and its regressions barely better `[AHE §4.4.2]`. Hold that number. It is the reason
Chapter 49 argues that a self-evolving system needs more human governance than a static one, not
less.

---

## 15. Industry Perspective

Claims in this chapter, separated by provenance. Nothing below is blended.

### Supported by the attached AHE paper `[AHE]`

- The harness is the collection of model-external, editable components mediating how a model
  perceives and acts on its environment (§1).
- Harness design materially shifts task completion with the base model held fixed (§1).
- The optimal harness is model-specific and must be re-adapted as the base model changes (§1).
- Ten evolution iterations lifted single-attempt success on the reported benchmark from 69.7% to
  77.0%, in roughly 32 hours (§4.2).
- Fix predictions land roughly 5× above a random baseline; regression predictions roughly 2×
  (§4.4.2).
- Harness components interact non-additively: individually positive edits do not sum (§4.4.1).
- Exposing components as files yields file-level diffs and rollback granularity (§3.1).
- The documented failure pattern of an agent reaching a verified state and then destroying it during
  cleanup (App. C.1.2), and of closing on a self-invented check rather than the evaluator's
  assertions (App. C.1.1).

### Supported by the attached Durable Runtime architecture `[DAR]`

- The four properties that appear when a product asks for a goal rather than an answer (§2.1).
- The four common accidental implementations and why each is a defect (§2.1).
- The three disqualifiers for adopting the full architecture (§2.4).
- The custody rule for scarce, exclusively held resources (§5.2).
- Timeout is not cancellation (§5.5).
- Identity determines safe reuse; a mismatch produces confident, well-formed, wrong output (§6.2).
- Effectful steps must be structurally uncallable without a resolved approval, enforced in the
  runner and not by instructing the model (§8.1).
- Model self-evaluation shares blind spots with the model that produced the work, and silent
  correctness failure is the dominant real-world failure mode (§9.1).
- State is a row; a worker is a temporary reader of it (§13).

### Engineering inference `[INF]`

- The five-generation taxonomy G0–G5, and the claim that each generation traded a guarantee for a
  capability.
- The two-axis model of Figure 0.1 and the discontinuity at G2→G3.
- Context isolation, rather than collaboration, as the primary engineering benefit of sub-agents.
- The two-minute and ten-minute heuristics in §13.1.
- Identity-determines-reuse as a pattern recurring at four scales.
- The accumulating component inventory of §5 as the handbook's organising spine.

### Industry best practice `[BP]`

- Structured function calling as the standard mechanism for the G1 transition; now near-universal
  across providers.
- The observe–think–act loop pattern, popularised as ReAct, as the default G2 shape. Chapter 26
  treats it as one planning algorithm among several rather than a default.
- Sandboxed execution per run as standard practice for G3 systems.

### Future proposal `[FUT]`

- None in this chapter. The taxonomy stops at what has been built and measured. Speculation about a
  sixth generation is deferred to Chapter 49, where it can be grounded in the specific limits Level 5
  establishes.

---

## 16. Key Takeaways

1. **Capability and survivability are independent axes.** Progress from G0 to G2 was capability;
   progress from G2 to G3 was survivability, and it is the subject of this book.
2. **Each generation traded a guarantee for a capability.** The loop bought multi-step work by
   giving up bounded termination, bounded cost, and durability. Every component in Levels 2 and 3
   is a forced move to restore one of those.
3. **The model box never grows.** From completion to self-evolution, everything added is outside the
   model. That outside is the harness, and it is where your engineering lives.
4. **G3 is where the diagram changes kind.** When a box in your architecture is a table rather than
   a function, you are in distributed-systems territory and should stop reasoning about agents as
   programs.
5. **The failure that kills products is the quiet one.** Not the crash — the confident, well-formed,
   wrong result that passes its own check. Reliability without grading is a well-oiled machine
   driving in the wrong direction `[DAR §16]`.
6. **Which generation you are building is a decision, not a discovery.** Make it before Chapter 4,
   and be willing to answer G2 and stop reading.

---

**Next:** Chapter 1 — *Anatomy of an Agent: Model, Harness, Environment.* We draw the line between
the model and the system precisely, define the seven editable component types, and establish why the
harness is a first-class performance surface rather than plumbing.
