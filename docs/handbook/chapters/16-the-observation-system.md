```
  Level 2 · Chapter 16
  THE OBSERVATION SYSTEM
  Requires   C9 Three Flows, C11 The Context System,
             C13 The Reasoning Engine, C14 The Tool Execution Engine,
             C15 Agent-Computer Interface Design
  Unlocks    C34 Observability, C37 Tenancy and Data Governance,
             C40 Testing, C41 Evaluation Infrastructure,
             C44 Experience Observability
  Diagrams   Full (9)
```

# Chapter 16 — The Observation System

---

## 1. Motivation

### 1.1 Cold open

An engineer is asked a straightforward question: why did Atlas keep passing directory paths to a
tool that wanted globs?

The incident itself is closed — Chapter 15's cold open, fixed eleven days after it started. What the
team wants now is the thing that makes the next one cheap: how long was it happening, how many runs
did it touch, and did anything else regress at the same moment.

The trace store holds fourteen terabytes of trajectories. Every tool call is there, with its
arguments and its result. Every model completion is there. Timestamps, latencies, token counts, run
ids, all of it.

None of it records what the model was *shown*.

The tool descriptions in force at the time are not in the traces, because descriptions are
configuration and configuration is not per-run data. They are in git, which is the right place — but
the harness version each run pinned was never written into its trajectory. So for any given run
there is no way to establish which description it saw without reconstructing the deploy timeline by
hand and hoping nothing was rolled back.

Fourteen terabytes, and the question is unanswerable.

### 1.2 In plain language

The observation system is how the runtime watches itself. It produces three different kinds of
record, and confusing them is where the trouble starts.

**Metrics and logs** are for people watching the system right now: how many runs are active, how
slow things are, what is erroring. They are cheap, they are approximate, and losing them costs
nothing because the next measurement replaces them.

**Facts** are the durable statements that something happened — a patch was applied, an approval was
granted. Small, permanent, and relied upon by other parts of the system.

**Trajectories** are the full record of one run: every step, every tool call, every result, and
every model exchange. They are enormous compared with the other two, they are the only thing that
can answer *why* the system behaved as it did, and they contain everything the run touched — which
means they contain everything sensitive the run touched.

The chapter's central point is that a trajectory is only useful if it records what the model could
*see* at each moment, not merely what it did. The model's view is assembled fresh for each call and
thrown away immediately afterwards. If nobody writes it down at the time, it does not exist later —
and no amount of storage compensates, which is the cold open.

The second point is that this is the most dangerous data the system holds, and the safe moment to
remove secrets from it is while it is being written, not when somebody reads it.

### 1.3 Why this chapter exists

Every improvement mechanism in the rest of this book reads what this chapter writes.

Chapter 15's monthly review needs to see what the model was looking at before each wrong move.
Chapter 28's grading needs the outputs. Chapter 41's evaluation needs runs it can compare. And all
of Level 5 — the agent debugger, the evidence corpus, attribution — is built on trajectories
`[AHE §3.2]`. `[INF]` The observation system is the component with the most downstream dependents
and the least immediate payoff, which is exactly the combination that gets it deferred.

It is also where the book's governance problem originates. `[INF]` A trajectory is the highest-risk
dataset in the architecture: it contains the customer's source code, the contents of files the run
read, whatever a shell command printed, and any credential that passed through any of them. Chapter
37 sets the rules; this chapter is where they must be enforced, because §5.4 argues the only safe
moment is at capture.

### 1.4 What previous framings got wrong

**"Observability means metrics, logs, and traces."** `[BP]` That triad describes what operators need
to run a service, and Chapter 34 builds it. It does not describe what a system needs to *improve
itself*, which is a fourth thing the triad has no name for. §2.3 separates them.

**"Log everything and figure it out later."** Two problems. Volume: trajectories are megabytes per
run and the trace store will outgrow every other store you have. And redaction: everything logged is
logged forever, so "figure it out later" means a secret written today is unremovable tomorrow.

**"Sample traces to control cost."** Correct for service traces and wrong here, in a specific way
§5.5 makes precise: uniform sampling is least likely to retain the runs you will most want, because
the interesting ones are rare.

**"The trajectory is the messages."** The cold open. A message list records what was said. It does
not record the tool descriptions, the memory entries, or the assembled context that produced what
was said — and those are the editable surfaces, which makes them the only ones worth having a record
of.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

An aircraft carries three separate recording systems, and the separation is not accidental.

The **instruments** show the crew what is happening right now — airspeed, altitude, engine
temperature. They are live, continuous, and nothing is kept. Losing an instrument reading costs
nothing, because another arrives a moment later.

The **flight data recorder** keeps a structured record of parameters over time: control positions,
engine settings, discrete events. Small, durable, and the first thing an investigator reads. It
answers *what happened*.

The **cockpit voice recorder** captures what the crew said and heard. It is the only device that can
explain *why* a correct-looking sequence of actions was taken, and it is subject to far stricter
rules than either of the others: limited retention, restricted access, and legal constraints on use.
Its value and its sensitivity come from the same property — it records everything in the room.

Metrics, facts, and trajectories, in that order. `[INF]` The governance asymmetry carries over
exactly: the record that best explains behaviour is the one you can least afford to keep carelessly.

**Where the analogy breaks**, and the break is the cold open.

A voice recorder captures what the crew heard because the sound existed in the room — the microphone
is in the environment, picking up something ambient. A model's room is not ambient. Its entire view
is *assembled* by the runtime immediately before the call and discarded immediately after (Chapter
11), so there is nothing for a microphone to pick up. The only way that view is ever recorded is if
the runtime deliberately writes down what it built.

`[INF]` The cold open is a cockpit voice recorder that captured the pilots' words but not the
instrument readings they were reacting to. Every utterance preserved; the reason for it gone.

### 2.2 Why observation must be a component

```
  1. To improve the system you must know WHY it did what it did.
  2. Why is determined by what the model could perceive, which is
     model state (Ch 6): assembled per call and discarded.
  3. Discarded state cannot be reconstructed afterwards. Descriptions
     were edited, memory entries decayed, the assembly policy
     improved -- so replaying today reproduces today's view, not the
     one the run actually had.
  4. Therefore if it is not written down at the moment of the call,
     the information is gone permanently. There is no later.
  5. But writing it down is expensive (megabytes per run) and
     dangerous (it contains everything the run touched, including
     secrets).
  6. So capture cannot be "log everything". It needs a policy: what,
     at what fidelity, kept how long, readable by whom, with what
     removed.
  7. A policy needs one owner and one enforcement point, or it is a
     convention that decays.
  8. Therefore observation is a component with a contract -- not a
     logging call sprinkled through the code.
```

Step 3 is the one that catches people, because it sounds recoverable and is not. `[INF]` The
instinct is that a run can be re-executed to see what it saw. It cannot: re-running it under today's
harness produces today's context, and the whole question was what *yesterday's* context contained.
Chapter 40's hermetic replay can reproduce a recorded run faithfully, but only from a recording that
captured the inputs — which is this chapter's job, not that one's.

### 2.3 Three kinds of record, and one distinction that matters most

| | Metrics and logs | Facts | Trajectories |
|---|---|---|---|
| Answers | is it healthy? | what happened? | why did it do that? |
| Durable | **never** | **always** | yes, with retention |
| Size per run | bytes | ~1-10 KB | 1-10 MB |
| Written to | metrics backend | the outbox (Ch 9) | the trace store |
| Loss is | fine | **unacceptable** | expensive, not fatal |
| Read by | operators, dashboards | the runtime, auditors | humans, and the Evolve Agent |
| Sensitivity | low | low | **highest in the system** |
| Chapter | 34 | 9, 22 | **this one** |

`[DAR §7.1]` supplies the first distinction — telemetry is never durable, facts always are — and
Chapter 7's cold open is what happens when progress is mistaken for a fact.

`[INF]` The third column is the handbook's addition, and it is a genuinely different kind of thing
from either. It is durable like a fact and voluminous like telemetry; it is read by a machine that
will edit the system based on it; and it is the only one with a governance problem. Treating it as
"very detailed logging" gets every one of those wrong.

### 2.4 The mental model to carry

> **A trajectory must record what the model could see, not only what it did. Everything else in this
> chapter is about affording that: what it costs, how long it is kept, and what must be removed
> before it is written.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  KERNEL                                                      |
  |                                                              |
  |  +----------+  +----------+  +----------+  +----------+      |
  |  | planner  |  | context  |  | model    |  | tool     |      |
  |  | (Ch 10)  |  | (Ch 11)  |  | (Ch 13)  |  | (Ch 14)  |      |
  |  +----+-----+  +----+-----+  +----+-----+  +----+-----+      |
  |       |   (1)       |   (2)       |   (3)       |  (4)       |
  |       v             v             v             v            |
  |  +====+=============+=============+=============+=======+    |
  |  |  OBSERVATION SYSTEM                                  |    |
  |  |                                                      |    |
  |  |    envelope . REDACT . sample . seal                 |    |
  |  |                                                      |    |
  |  +==+=================+==================+==============+    |
  |     | (5)             | (6)              | (7)               |
  |     v                 v                  v                   |
  +-----|-----------------|------------------|-------------------+
        v                 v                  v
  +~~~~~~~~~~~+   +~~~~~~~~~~~~~~+   [[ outbox ]]
  | metrics   |   | TRACE STORE  |   facts only; small
  | backend   |   |              |   (Ch 9, Ch 22)
  |           |   | the highest- |
  | never     |   | risk data in |
  | durable   |   | the system   |
  +~~~~~~~~~~~+   +~~~~~+~~~~~~~~+
                        | (8)
                        v
                 +~~~~~~~~~~~~~~~~~~~~~~+
                 | Ch 44 agent debugger |
                 | Ch 41 evaluation     |
                 | Ch 15 monthly review |
                 +~~~~~~~~~~~~~~~~~~~~~~+

  Figure 16.1 -- The observation system across the runtime
                 (D1 High-Level Architecture)

  (1) plans, and every plan REJECTED by the validator (Ch 10)
  (2) the ASSEMBLED CONTEXT and its accounting -- the cold open's
      missing piece
  (3) completions, token usage, the policy that ran
  (4) tool calls, arguments, results, errors, descriptions in force
  (5) counters and timings; disposable by construction
  (6) the trajectory, redacted before it is written (section 5.4)
  (7) facts go to the outbox, NOT here; this component never
      writes a fact
  (8) the consumers, all of them downstream and none of them
      able to recover what was not captured
```

`[INF]` Wire 2 is what the cold open lacked, and the shape of the diagram says why it was missed:
observation sits below four components and it is tempting to capture each one's *output*. The
context system's output is the thing the model saw, and it is the only one of the four whose output
is discarded rather than passed on — so it is the one a capture built incrementally will omit.

Wire 7 is worth stating too. This component writes no facts. A trajectory is not an event, and the
outbox is for things later readers are entitled to rely on (Chapter 9). Sending trajectories through
the event spine is Chapter 7's cold open at a hundred times the volume.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  OBSERVATION SYSTEM, opened -- one step's capture

  +--------------------------------------------------------------+
  |                                                              |
  |  1. ENVELOPE     wrap the raw observation with identity:      |
  |     |              run_id . plan_id . step_id . activity_id   |
  |     |              tenant_id . HARNESS VERSION <-- cold open  |
  |     |              trace_id . span_id . parent_span_id        |
  |     v                                                        |
  |  2. CLASSIFY     which kind is this (section 2.3):            |
  |     |              metric  -> backend, never durable          |
  |     |              fact    -> NOT here; caller uses the outbox|
  |     |              span    -> trajectory                      |
  |     v                                                        |
  |  3. REDACT       remove secrets NOW, before anything is       |
  |     |            written. Irreversible by design.             |
  |     |            section 5.4                                  |
  |     v                                                        |
  |  4. SHAPE        fidelity per span kind:                      |
  |     |              context   -> digest + accounting, body     |
  |     |                           only if sampled (5.3)         |
  |     |              tool i/o  -> already truncated (Ch 14)     |
  |     |              completion-> full                          |
  |     v                                                        |
  |  5. DECIDE       retain in full, retain shaped, or drop       |
  |     |            (section 5.5 -- never uniform sampling)      |
  |     v                                                        |
  |  6. APPEND       to the run's open trajectory. Buffered,      |
  |     |            fire-and-forget: capture NEVER fails a run   |
  |     v                                                        |
  |  7. SEAL         at run end: close, index, set retention      |
  |                  clock, emit << trajectory.sealed >>          |
  +--------------------------------------------------------------+

  Figure 16.2 -- One step's capture, opened
                 (D2 Low-Level Architecture)
```

### 4.1 Three orderings that matter

`[INF]` **Redact before shape (3 before 4).** Shaping may summarise or digest, and a digest of a
secret is still derived from a secret. Redaction runs on the raw material, once, at the earliest
possible point.

**Shape before decide (4 before 5).** The retention decision needs to know the cost of what it is
retaining, and shaping is what determines that cost. Deciding first means deciding blind.

**Append is fire-and-forget (6).** `[DAR §7.1]` Capture is telemetry-shaped even though its output
is durable: it must never fail a run. A trajectory that could not be written is a lost improvement
opportunity; a run that failed because its trajectory could not be written is an incident. Chapter 2
§8's fire-and-forget rule, applied to the component that most tempts you to break it.

```
                                                            LAYER VIEW

  Components and their interfaces.

   Observation (from any component)
        |
        v
   +----+------------+       +---------------------+
   | Enveloper       |------>| Classifier          |
   |  identity +     |       |  metric/span        |
   |  harness version|       +----------+----------+
   +-----------------+                  |
        ^                    +----------+----------+
        | reads              |                     |
   +----+------------+       v                     v
   | Run context     |   +---+----------+   +------+-------+
   |  (Ch 8)         |   | Metrics sink |   | Redactor     |
   +-----------------+   |  disposable  |   |  rules from  |
                         +--------------+   |  Ch 37       |
                                            +------+-------+
   +-----------------+                             |
   | Redaction rules |---------------------------->|
   |  redact.creds   |                             v
   |  redact.pii     |                      +------+-------+
   +-----------------+                      | Shaper       |
                                            |  per span    |
   +-----------------+                      |  kind        |
   | Retention policy|                      +------+-------+
   |  (Ch 37)        |                             |
   +--------+--------+                             v
            |                              +-------+------+
            +----------------------------->| Sampler      |
                                           |  outcome-    |
                                           |  weighted    |
                                           +-------+------+
                                                   |
                                                   v
                                           +-------+------+
                                           | Appender     |
                                           |  buffered,   |
                                           |  never fails |
                                           +-------+------+
                                                   |
                                                   v
                                           +~~~~~~~+~~~~~~+
                                           | TRACE STORE  |
                                           +~~~~~~~~~~~~~~+

  Figure 16.3 -- Observation system components (D3 Component Diagram)
```

`[INF]` The Redactor takes its rules from Chapter 37 rather than owning them, and that separation is
deliberate: redaction rules are a governance decision with legal weight, and the component that
applies them should not be the component that defines them. The same is true of retention. This
chapter owns the *mechanism* and the *moment*; Chapter 37 owns the policy.

---

## 5. Capturing a Trajectory

### 5.1 What must be in it

`[INF]` The cold open's list, and it is shorter than "everything":

| Captured | Why | Without it |
|---|---|---|
| **Harness version** | pins which descriptions, prompts, and memory were in force | the cold open: nothing is attributable |
| **Assembled context digest** | what the model could see, per call | reasoning failures indistinguishable from context gaps |
| **Context accounting** (Ch 11) | what was included, deferred, dropped, condensed | cannot tell whether a fact was absent or evicted |
| Model completion and policy | what it said, and under which tier | Ch 13's non-monotone tier confound |
| Tool call, arguments, result | what it did | no behaviour record at all |
| **Tool descriptions in force** | Ch 15's surface, as the model read it | ACI defects look like reasoning failures |
| Rejections (plan, schema) | Ch 10 and Ch 14's training signals | the highest-signal evidence, discarded |
| Timings and token counts | cost and latency attribution | no cost-normalised evaluation (Ch 41) |

The three in bold are the ones ordinary tracing omits, because they are configuration rather than
per-request data. `[INF]` The resolution is that **the harness version is per-run data**, even
though the harness is not. A run pins it at claim time (Chapter 8), which makes it a property of the
run, and writing it into the envelope costs sixteen bytes and answers the cold open entirely.

### 5.2 Digest, not duplicate

The assembled context is 50-200 KB per call and there may be forty calls. Capturing all of it
verbatim is 8 MB of mostly-identical text per run, because Chapter 11's stable band is stable by
design.

`[INF]` So capture it the way it is built:

```
  stable band     -> hash + harness version.  Reconstructible from git.
  semi-stable     -> hash + a reference to the plan and memory entries
  volatile band   -> VERBATIM. This is the part that differs per call
                     and the part that explains the call.
```

That reduces per-run context capture from megabytes to tens of kilobytes while remaining fully
reconstructible, and Chapter 11's `volatile_boundary_offset` is the field that makes the split
mechanical rather than a heuristic.

`[INF]` The reconstruction is only sound because the stable band is derived from things under
version control. That is a dependency worth naming: **this technique works because the harness is a
git repository** (Chapter 43). A system whose prompts live in a database with no history cannot
digest, and must store the whole thing.

### 5.3 Result envelopes

`[DAR §7.1]` Every observation is wrapped in the same envelope, which is what makes a trajectory
navigable rather than a pile of records:

```python
@dataclass(frozen=True)
class Envelope:
    trace_id: str            # one per run
    span_id: str
    parent_span_id: str | None
    run_id: RunId
    plan_id: PlanId | None   # Ch 10: which plan was current
    step_id: int | None
    activity_id: str | None  # Ch 21: joins to the ledger
    tenant_id: str           # Ch 37: the scoping key
    harness_version: str     # the cold open's fix
    kind: SpanKind
    flow: Flow               # Ch 9: control | data | event
    started_at: datetime
    duration_ms: int
```

`[INF]` `flow` is carried here because Chapter 9 §9 asked for it: one enum on a record already being
emitted, and a trace can then be filtered to one reading. It is the cheapest field in the structure
and the one that turns Chapter 9's cold open into a query.

### 5.4 Redaction at capture

`[INF]` The rule, stated as strongly as it deserves:

> **Secrets are removed as the trajectory is written, never when it is read. Redaction at read time
> is not redaction; it is a filter in front of a store that still contains the secret.**

Three reasons, and the third is the one that settles it:

1. A trace store is replicated, backed up, and exported. Every copy needs the same filter, and one
   that does not have it is a breach.
2. The Evolve Agent (Chapter 46) reads trajectories directly and automatically. Its access path is
   not a human-facing viewer where a filter could sit.
3. Once written, a secret is in every backup taken since. Removing it later means rewriting history
   across every copy, which in practice means it is never removed.

Chapter 12 made the same argument about long-term memory and git. `[INF]` These are the same
argument: **any store with history cannot be retroactively cleaned, so the only safe moment is
before the write.** That principle now applies in two places, and Chapter 37 generalises it.

What gets removed is a Chapter 37 decision, applied here: credential patterns, customer identifiers,
and anything a tenant has designated. What is left in its place must be a marker rather than a
deletion — `[redacted:credential]` — because a trajectory that silently omits things misleads the
reader about what the model saw, which is the one property this chapter exists to preserve.

### 5.5 Sampling: never uniform

`[INF]` Volume forces a retention decision, and the standard answer is wrong here.

Uniform sampling at 1% is correct for service traces, where every request is much like every other
and the population is what you want to characterise. Trajectories are not like that. The runs worth
keeping are the ones that failed, cost too much, took too many steps, or hit a rejection — and those
are rare, which is precisely why uniform sampling drops them.

Outcome-weighted retention instead:

| Class | Retain | Why |
|---|---|---|
| Failed, dead-lettered, or cancelled | 100%, full fidelity | the evidence corpus is made of these |
| Contains any rejection (plan, schema) | 100% | Ch 10 and Ch 14's training signals |
| Contains a retry loop (Ch 15) | 100% | guaranteed ACI defect |
| Cost or step count above p95 | 100% | the expensive tail |
| Graded below threshold (Ch 28) | 100% | the quality tail |
| Succeeded, unremarkable | 1-5%, shaped | needed only as a baseline |

`[INF]` The retention decision cannot be made when a span is captured, because the outcome is not
known until the run ends. So capture buffers at full fidelity and §4's step 5 decides at **seal**
time — which means the cost of the policy is buffer, not storage, and a run that turns out
uninteresting is cheap to discard.

### 5.6 The trace store is the highest-risk dataset

`[INF]` Stated plainly because it is easy to under-rate. The trace store contains, for every run:
the customer's source code as read, whatever any shell command printed, the full text of every model
exchange, and any credential that passed through any of them before §5.4 caught it.

It is larger than every other store, less structured, read by an automated agent, and retained for
the benefit of a process most of the organisation does not know exists.

| Control | Where |
|---|---|
| Redaction at capture | §5.4, this chapter |
| Tenant scoping on every read | Ch 37 |
| Retention clock set at seal | §7 |
| Access audit, including the Evolve Agent's | Ch 37, Ch 49 |
| No fact ever sourced from it | §3, wire 7 |

The last row is a containment property worth noticing: because nothing durable in the runtime
depends on the trace store, it can be deleted entirely without breaking correctness. `[INF]` That is
a deliberate design outcome — it makes an aggressive retention policy *possible*, where a system
that reads facts out of its traces could never shorten retention without losing behaviour.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  context   model    tool    observation   redactor   trace store
     |        |       |           |            |            |
     |-- assembled, 47.9K tokens ->|           |            |
     |        |       |           |-- envelope: run, plan, step,
     |        |       |           |   tenant, HARNESS VERSION v14.2
     |        |       |           |-- digest stable band (hash)
     |        |       |           |   verbatim volatile band (4.1K)
     |        |       |           |----------->|            |
     |        |       |           |<-- 2 credentials replaced with
     |        |       |           |    [redacted:credential] markers
     |        |       |           |-------- buffer ------->|
     |        |       |           |                        |
     |        |-- completion ---->|                        |
     |        |   + policy(tier=standard) + usage           |
     |        |       |           |-------- buffer ------->|
     |        |       |           |                        |
     |        |       |-- call + result + DESCRIPTION IN FORCE ->|
     |        |       |           |-------- buffer ------->|
     |        |       |           |                        |
     |  ... 38 more steps ...     |                        |
     |        |       |           |                        |
     |  run ends: FAILED          |                        |
     |        |       |           |-- SEAL:                |
     |        |       |           |     outcome = FAILED   |
     |        |       |           |     -> retain 100%,    |
     |        |       |           |        full fidelity   |
     |        |       |           |     -> retention clock |
     |        |       |           |        starts (Ch 37)  |
     |        |       |           |.. << trajectory.sealed >> ..>|
     |        |       |           |                        |

  Failure branch: the trace store is unavailable at buffer time.
     The span is dropped. A counter increments. The RUN CONTINUES.
     Capture is fire-and-forget (section 4.1) -- a lost trajectory
     is a lost improvement, and a failed run is an incident.

  Figure 16.4 -- Capturing one run, with redaction and outcome-weighted
                 sealing (D4 Sequence)
```

### 6.1 What the sequence establishes

Three things that only become visible when the whole run is drawn.

**The harness version is written once, in the envelope, on every span.** Sixteen bytes per span, and
it is the entire fix for the cold open. Every later question of the form "which description did this
run see?" resolves to a git lookup.

**Redaction happens per span, before buffering.** Not at seal, not at read. By the time anything is
buffered the secret is already gone, which is what makes the store safe to replicate.

**The retention decision is made at seal, once, knowing the outcome.** A run that failed is kept
entirely. Had it succeeded unremarkably, most of what was buffered would have been discarded — and
the cost of buffering it was memory, briefly, rather than storage, forever.

```
                                                             TIME VIEW

  The capture cycle, per run.

   run starts
        |
        v
   +----+-----------------+
   | open trajectory      |  trace_id minted; buffer allocated
   +----+-----------------+
        |
        v
        +------------------------------------------+
        |                                          |
        v                                          |
   +----+-----------------+                        |
   | observe one span     |  from any component    |
   +----+-----------------+                        |
        |                                          |
        v                                          |
   +----+-----------------+                        |
   | envelope + classify  |  metric -> sink, E1    |
   +----+-----------------+                        |
        |                                          |
        v                                          |
   +----+-----------------+                        |
   | REDACT               |  irreversible          |
   +----+-----------------+                        |
        |                                          |
        v                                          |
   +----+-----------------+                        |
   | shape + buffer       |  never fails: E2 on    |
   +----+-----------------+  store unavailability  |
        |                                          |
        v                                          |
      /   \                                        |
     / run   \  no ---------------------------------+
     \ over? /
      \     /
        | yes
        v
   +----+-----------------+
   | SEAL                 |  outcome known HERE, and only here
   +----+-----------------+
        |
        v
      /   \
     /outcome\-- interesting ---> E3 retain 100%, full fidelity
     \ class? /-- unremarkable --> E4 retain 1-5%, shaped
      \      /-- over quota -----> E5 retain, alert (section 12)
        |

  Exits:
    E1  metric routed to the disposable sink; never durable
    E2  store unavailable; span dropped, counter incremented,
        THE RUN CONTINUES
    E3  interesting outcome; the evidence corpus (section 5.5)
    E4  unremarkable; shaped baseline sample
    E5  tenant over its trace quota; retained but flagged

  Figure 16.5 -- The capture cycle and its exits (D5 Runtime Loop)
```

`[INF]` E2 is the exit that must never become an error, and it is the one an engineer will be
tempted to "fix" the first time they notice gaps in a trajectory. The gap is the correct behaviour.
The alternative is a system whose runs fail when its observability backend is degraded, which
converts a monitoring outage into a production outage.

---

## 7. State Management

```
                                                            STATE VIEW

  One trajectory's lifecycle.

            +---------------------+
            | {{ OPEN }}          |  run in flight; spans buffering
            +----------+----------+
                       | run reaches a terminal state
                       v
            +---------------------+
            | {{ SEALED }}        |  outcome known; retention class
            +----+-----------+----+  assigned; index built
                 |           |
       interesting|          | unremarkable
                 v           v
   +-------------+---+   +---+-----------------+
   | {{ RETAINED }}  |   | {{ SHAPED }}        |
   +--------+--------+   +---------+-----------+
    full fidelity;        digest only; enough
    the evidence corpus   to count, not to explain
            |                      |
            +----------+-----------+
                       | retention clock expires (Ch 37)
                       v
            +---------------------+
            | {{ EXPIRED }}       |  content deleted; the ENVELOPE
            +---------------------+  survives as a tombstone

  Illegal, and enforced:
    * OPEN -> RETAINED             the outcome is unknown until seal
    * SEALED -> OPEN               a trajectory is never reopened;
                                   a resumed run appends to the SAME
                                   open trajectory, and a run is not
                                   sealed until terminal (Ch 8)
    * EXPIRED -> anything          deletion is real
    * any state -> a fact          nothing durable depends on this
                                   store (section 5.6)

  Figure 16.6 -- A trajectory's lifecycle (D6 State Diagram)
```

### 7.1 A trajectory spans the whole run, not one episode

`[INF]` Worth stating because Chapter 8 established that a run crosses many worker lifetimes. The
trajectory is keyed by `run_id` and stays `OPEN` across every episode, every park, and every worker
that touches it. A run parked for three days awaiting approval has an open trajectory for three
days.

That has a practical consequence: **the buffer cannot be in worker memory.** A worker releases the
run at an episode boundary and may never see it again, so buffered spans must be flushed at
checkpoint. The buffer is a batching optimisation within one episode, not a hold-until-seal
mechanism.

### 7.2 The tombstone

`[INF]` When retention expires, the content is deleted and the envelope is kept: run id, tenant,
harness version, outcome, timings, counts. It is a few hundred bytes and it preserves the ability to
answer aggregate questions — how many runs used harness v14.2, what fraction failed — long after the
detail is gone.

It also means a request to delete a tenant's data has an auditable end state, rather than the
absence of a record being indistinguishable from a record that was never made.

### 7.3 Trajectories are run state that outlives the run

Chapter 6's categories, with an awkward case. A trajectory is not domain state — deleting the
runtime makes it meaningless. It is not model state — it is durable. It is closest to run state,
except that run state's lifetime "ends with the run" and a trajectory deliberately does not.

`[INF]` The honest classification is that a trajectory is **run state under a separate retention
policy**, which is why Chapter 37 governs it separately from everything else the run wrote. It is
the one place the four-category model needs an explicit exception rather than a resolution, and
saying so is better than forcing it into a category it does not fit.

---

## 8. Internal APIs

```python
from typing import Protocol


class ObservationPort(Protocol):
    """Capture. Never fails a run; never writes a fact.

    Every method is fire-and-forget by contract: implementations
    buffer and return, and a store outage drops spans rather than
    raising (section 4.1).
    """

    def observe(self, envelope: Envelope, payload: SpanPayload) -> None:
        """Record one span. Synchronous, non-blocking, never raises.

        The envelope carries harness_version, which is what makes any
        later question about what the model saw answerable at all.
        """

    def metric(self, name: str, value: float, tags: Mapping[str, str]) -> None:
        """Disposable by construction. Routed to the metrics sink and
        never to the trace store."""

    async def seal(self, run_id: RunId, outcome: RunOutcome) -> SealReport:
        """Close the trajectory, assign a retention class from the
        outcome (section 5.5), build the index, and start the retention
        clock. The only place the retention decision is made."""


class RedactionPort(Protocol):
    """Rules owned by Ch 37, applied here. Runs on raw payloads before
    anything is buffered, and leaves a MARKER rather than a hole."""

    def redact(self, payload: SpanPayload) -> tuple[SpanPayload, int]:
        """Returns the redacted payload and the number of removals, so
        section 13 can alert when a tenant's rate changes."""


class TrajectoryReader(Protocol):
    """The consumer side: Ch 15's review, Ch 41's evaluation, Ch 44's
    debugger. Tenant-scoped on every call, and audited (Ch 37)."""

    async def open(self, run_id: RunId, reader: ReaderIdentity) -> Trajectory: ...
    async def search(self, query: TrajectoryQuery) -> list[TrajectoryRef]: ...
```

`[INF]` `observe` returning `None` and being documented as never raising is the enforcement of §4.1.
A signature that could raise invites a caller to `await` it and handle failure, and the first time
someone does that under load, capture becomes a dependency of run completion. The type is the
argument.

`redact` returning a count rather than a boolean is the small decision that makes §13.1's most
useful alert possible: a step change in redaction rate for one tenant means either a new secret is
flowing through the system or a rule stopped matching.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class SpanKind(StrEnum):
    CONTEXT_ASSEMBLED = "context_assembled"   # the cold open's span
    MODEL_CALL = "model_call"
    TOOL_CALL = "tool_call"
    PLAN_CREATED = "plan_created"
    PLAN_REJECTED = "plan_rejected"           # Ch 10 training signal
    SCHEMA_REJECTED = "schema_rejected"       # Ch 14 training signal
    GATE_RAISED = "gate_raised"
    GRADE = "grade"


class RetentionClass(StrEnum):
    EVIDENCE = "evidence"        # interesting outcome; full fidelity
    BASELINE = "baseline"        # sampled, shaped
    TOMBSTONE = "tombstone"      # expired; envelope only


@dataclass(frozen=True)
class ContextSpan:
    """The span the cold open did not have."""

    stable_digest: str               # hash; reconstructible from git
    semi_stable_digest: str
    volatile_body: str               # verbatim: the part that differs
    accounting: ContextAccounting    # Ch 11: included/deferred/dropped
    volatile_boundary_offset: int    # where the split was made


@dataclass(frozen=True)
class ToolSpan:
    tool_id: str
    arguments: Mapping[str, object]
    result: ToolResult
    description_digest: str          # Ch 15's surface, as read
    middleware_applied: tuple[str, ...]


@dataclass(frozen=True)
class SealReport:
    run_id: RunId
    outcome: RunOutcome
    retention: RetentionClass
    spans: int
    bytes_retained: int
    bytes_dropped: int
    redactions: int
```

`[INF]` `ContextSpan` is the structure this whole chapter exists to produce, and its shape is the
answer to §5.2's cost problem: two hashes and one verbatim body. Everything the cold open needed is
in it, at roughly 2% of the naive cost.

`description_digest` on `ToolSpan` is the Chapter 15 payoff. It is a hash rather than the text,
because the text is in git under the harness version already in the envelope — the same
digest-and-reconstruct trick, applied to the other surface that ordinary tracing omits.

---

## 10. Communication

```
                                                            LAYER VIEW

  Per run, per step:
    context digest + volatile  ====> observation   ~4-12 KB
    completion + usage         ====> observation   ~5-50 KB
    tool call + result         ====> observation   ~1-64 KB
    metrics                    ~~~~> metrics sink  ~200 B, disposable

  Per run, sealed:
    trajectory (interesting)   ====> trace store   1-10 MB
    trajectory (unremarkable)  ====> trace store   ~50 KB shaped
    << trajectory.sealed >>    ....> outbox        ~300 B

  The reduction, per run:
    naive full capture ................ ~40 MB
    digest + volatile (section 5.2) ... ~6 MB
    outcome-weighted (section 5.5) .... ~6 MB or ~50 KB

  Figure 16.7 -- Observation volume (D7 Data Flow)
```

```
                                                             TIME VIEW

  every component --> observation   observe(envelope, payload)
  observation -----> redactor       BEFORE buffering, always
  observation -----> trace store    buffered, fire-and-forget
  observation --X    the run        REFUSED: capture never fails a run
  observation --X    the outbox     REFUSED: trajectories are not facts
  trace store --X    the runtime    REFUSED: nothing durable reads it
                                    (section 5.6, the containment
                                     property that makes deletion safe)
  Evolve Agent ----> trace store    read-only, tenant-scoped, audited

  Figure 16.8 -- Who captures, and what may read it
                 (D8 Control Flow)
```

```
                                                             TIME VIEW

  << trajectory.sealed >>       ....>  run id, outcome, retention class,
                                       harness version. Small; the
                                       INDEX to the corpus, not the
                                       corpus
  << trajectory.expired >>      ....>  content deleted, tombstone kept
  << redaction.rate.changed >>  ....>  a tenant's rate moved; either a
                                       new secret is flowing or a rule
                                       stopped matching

  NOT events:
    spans                    the trajectory itself; trace store only
    metrics                  disposable by construction
    trajectory reads         audited (Ch 37), not evented

  Figure 16.9 -- What observation makes durable (D9 Event Flow)
```

`[INF]` Three events, all tiny, and none of them carrying trajectory content. That is the shape
Chapter 7's cold open demands: the event spine carries the *index* to the corpus so that other
components can find a trajectory, and never the corpus itself.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 34 Observability | metrics and spans, for operators | the human-facing half of this |
| Ch 37 Tenancy | redaction rules, retention, access audit | the policy this chapter enforces |
| Ch 40 Testing | recorded inputs make hermetic replay possible | replay needs what was captured |
| Ch 41 Evaluation | comparable runs with cost attached | scoring needs the token counts |
| Ch 44 Agent Debugger | the evidence corpus itself | ten million tokens to ten thousand |
| Ch 46 Evolve Agent | context and description digests | ACI edits need what the model saw |
| Ch 49 Governance | who read which trajectory | the access problem this creates |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Captured actions, not inputs | tracing built from component outputs | any "what did it see?" question | capture the context span — the cold open |
| No harness version in the envelope | version treated as config, not run data | attribution impossible after any deploy | 16 bytes per span (§5.1) |
| Redaction at read time | a filter in the viewer | any export or backup path bypasses it | redact at capture; irreversible (§5.4) |
| Uniform sampling | service-trace habits | the failures are never in the sample | outcome-weighted retention (§5.5) |
| Capture failing a run | `await observe(...)` with error handling | run failures correlate with store health | fire-and-forget by contract (§4.1) |
| Trajectories in the outbox | trajectory treated as an event | events table growth tracking run count | facts to the outbox, spans to the store |
| Facts read from traces | convenience query against the trace store | retention cannot be shortened without breaking behaviour | nothing durable reads it (§5.6) |
| Unbounded growth | no retention clock | trace store dominating storage cost | clock set at seal (§7) |
| Buffer held to seal | worker memory holding spans | spans lost when a worker releases a run | flush at checkpoint (§7.1) |
| Silent redaction | secrets removed without a marker | reader believes the model saw a gap | leave `[redacted:...]` markers |
| Unaudited automated reads | the Evolve Agent reading directly | nobody can say what it read | audit reads, including machine ones (Ch 49) |

`[INF]` Row seven is the subtle one and it is a design property rather than a bug. The moment any
durable behaviour sources a fact from the trace store, retention becomes a correctness constraint
rather than a cost decision — and you can no longer delete traces without changing what the system
does. Keeping that arrow absent (Figure 16.8) is what preserves the freedom to have an aggressive
retention policy at all.

---

## 12. Scalability

### 12.1 The trace store outgrows everything else

`[INF]` The arithmetic is worth doing once, because it surprises people:

```
  10,000 runs/day  x  6 MB/run (digested)  =  60 GB/day
                                           =  ~22 TB/year, undeleted
```

Against a `runs` table measured in megabytes and an outbox measured in gigabytes. The trace store is
two to three orders of magnitude larger than the rest of the system combined, and it is the only
store whose size is driven by how *interesting* the work was rather than how much there was.

| Lever | Effect |
|---|---|
| Digest the stable band (§5.2) | ~85% reduction; no information lost |
| Outcome-weighted retention (§5.5) | ~90% further, on the unremarkable majority |
| Retention clock (§7) | bounds the total rather than the rate |
| Truncation upstream (Ch 14) | the 10 MB tool result never arrives |

`[INF]` The first two compose to roughly a 98% reduction against naive capture, while keeping 100%
of the runs anyone will want to read. That is an unusually good trade and it exists only because the
retention decision is deferred to seal, when the outcome is known.

### 12.2 Capture must not be on the critical path

Buffered, batched, flushed at checkpoint. `[INF]` The budget to hold to is that observation adds no
more than single-digit milliseconds to a step — which is achievable because a step is already
writing a checkpoint (Chapter 8), and the flush rides along with a write that was happening anyway.

The failure to avoid is synchronous per-span writes to a remote store, which turns every step into a
network round-trip and makes the observability backend a latency dependency of every run.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Spans dropped (E2) | store health, without failing runs | sustained non-zero |
| Redactions per tenant per run | a new secret flowing, or a rule that stopped matching | step change either way |
| Trajectories sealed with no context span | the cold open, as a live check | any non-zero |
| Envelopes missing `harness_version` | the same, at the field level | any non-zero |
| Trace store growth vs run count | digesting and retention working | growth outpacing runs |
| Retention class distribution | is "interesting" defined sensibly | evidence share above ~20% |
| Trajectory read audit, by reader | including the Evolve Agent (Ch 49) | reviewed, not alerted |

`[INF]` Row three is the cheapest and most valuable check in the chapter: assert at seal that any
trajectory containing a `MODEL_CALL` span also contains a `CONTEXT_ASSEMBLED` span for it. That
single invariant makes the cold open impossible to reintroduce, and it costs one comparison per run.

### 13.2 The test that catches the cold open

```python
async def test_trajectory_records_what_the_model_could_see(
    runtime: Runtime, traces: TrajectoryReader
) -> None:
    run = await runtime.submit_and_finish(goal)
    trajectory = await traces.open(run.id, reader=SYSTEM)

    model_calls = trajectory.spans_of(SpanKind.MODEL_CALL)
    assert model_calls, "no model calls captured"

    for call in model_calls:
        ctx = trajectory.context_span_for(call.span_id)
        assert ctx is not None, f"no context captured for {call.span_id}"
        assert ctx.volatile_body, "volatile band must be verbatim"
        assert ctx.stable_digest, "stable band must be reconstructible"

    # The cold open's actual fix: every span names the harness version,
    # so the descriptions in force are recoverable from git.
    assert all(s.envelope.harness_version for s in trajectory.spans)

    # And the Ch 15 payoff: tool spans record the description as read.
    for tool_span in trajectory.spans_of(SpanKind.TOOL_CALL):
        assert tool_span.description_digest
```

`[INF]` The last assertion is the one that connects two chapters. Chapter 15's monthly review is
impossible without it, and it would have been easy to omit — a `description_digest` looks like
redundant metadata right up until somebody asks why the model kept doing something.

### 13.3 The redaction rule test

`[BP]` Redaction rules are regexes, regexes rot, and a rule that stops matching fails silently.

```python
@pytest.mark.parametrize("secret", KNOWN_SECRET_SHAPES)
def test_redaction_catches_known_shapes(secret: str, redactor: RedactionPort):
    payload, count = redactor.redact(SpanPayload(text=f"prefix {secret} suffix"))
    assert count == 1
    assert secret not in payload.text
    assert "[redacted:" in payload.text     # a marker, not a hole
```

`[INF]` `KNOWN_SECRET_SHAPES` grows from incidents, and it should include shapes that were *found in
production traces* rather than only ones that were anticipated. A redaction suite written entirely
from imagination tests what you already knew to look for.

---

## 14. Relation to AHE

This chapter is the one Level 5 cannot be built without, and `[AHE §3.2]` is explicit that
experience observability is one of the three pillars the loop stands on.

**Trajectories are the raw material of the evidence corpus.** `[AHE §3.2]` describes distilling
roughly ten million tokens of raw rollout into roughly ten thousand tokens of navigable evidence.
`[INF]` Every reduction in this chapter is upstream of that one: digesting the stable band and
weighting retention by outcome mean the distillation starts from the runs worth reading rather than
from everything.

**What is not captured cannot be evolved.** `[INF]` This is the chapter's hardest claim and it
follows directly from §2.2. An Evolve Agent can only fix what the corpus shows, so a trajectory that
records actions without inputs produces a loop that sees reasoning failures everywhere and edits the
system prompt — the weakest surface (Chapter 1), and the one `[AHE §4.4.1]` measured as regressing.
The cold open is therefore not merely an operational inconvenience; it is a defect that would
systematically misdirect an evolution loop toward the least effective edits.

**The corpus is also the governance problem.** `[INF]` Chapter 46's Evolve Agent reads trajectories
automatically, at scale, without a human in the path. That is a machine with routine read access to
the most sensitive store in the architecture, which is why §5.4 insists on redaction at capture and
why Chapter 49 treats trajectory access as a governance surface rather than an implementation
detail. Phase 2 named the trace store the highest-risk dataset for this reason.

**Rejections are the highest-value spans and the easiest to discard.** `[INF]` `PLAN_REJECTED` and
`SCHEMA_REJECTED` are tiny, rare, and direct evidence that a harness component produced something
invalid. A capture policy tuned only on volume will drop them as noise; §5.5 retains 100% of runs
containing either, because they are the cheapest quality signal in the system.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the telemetry-versus-facts distinction, the result envelope, the rule that
telemetry is never durable and facts always are, and the fire-and-forget discipline for non-critical
capture `[DAR §7.1]`.

**`[AHE]`** Supplies trajectory capture as a pillar of the evolution loop, the distillation ratio
from raw rollouts to navigable evidence, and progressive disclosure as how a corpus is read
`[AHE §3.2, App. A]`.

**`[INF]`** The handbook's own: trajectories as a third kind of record distinct from both telemetry
and facts, the harness version as per-run data and the cold open's fix, digest-the-stable-band as the
capture technique and its dependency on the harness being version-controlled, outcome-weighted
retention deferred to seal, the argument that any store with history cannot be retroactively cleaned,
tombstones on expiry, the containment property that nothing durable reads the trace store, and the
claim that uncaptured inputs systematically misdirect an evolution loop toward prompt edits.

**`[BP]`** Distributed tracing, span hierarchies, and structured envelopes are standard practice;
the flight-recorder separation is borrowed from aviation. Redaction at write time is established in
regulated logging. The contribution here is applying the discipline to a store whose primary reader
is a machine that will edit the system based on it.

**`[FUT]`** `[FUT]` Nothing here measures whether a trajectory was *sufficient* — whether it
contained enough to explain the run. A capture-completeness score, ideally derived from whether a
debugger could reach a root cause from the trajectory alone, would turn §13.1's structural checks
into a quality measure. The handbook knows of no such method, and §13.1's invariants are a
structural proxy for it.

---

## 16. Key Takeaways

1. **Record what the model could see, not only what it did.** The model's view is assembled and
   discarded on every call, so it exists later only if it was written down at the time. Fourteen
   terabytes that omit it answer nothing.
2. **The harness version is per-run data.** Sixteen bytes in every envelope makes every later
   question about descriptions, prompts, and memory a git lookup.
3. **Three kinds of record, not two.** Telemetry is never durable, facts always are, and
   trajectories are a third thing: durable, voluminous, machine-read, and the only one with a
   governance problem.
4. **Redact at capture.** A store with history cannot be retroactively cleaned, so read-time
   filtering is not redaction. Leave a marker, never a hole.
5. **Never sample uniformly.** The runs worth keeping are rare by definition. Decide retention at
   seal, when the outcome is known, and keep 100% of anything that failed, was rejected, or looped.
6. **Capture never fails a run.** Fire-and-forget by contract. A lost trajectory is a lost
   improvement; a run that failed because capture failed is an incident.
7. **Nothing durable may read the trace store.** That containment is what makes an aggressive
   retention policy possible at all — and it is worth defending against the first convenient query.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Observation system** | The component that captures how the runtime perceived itself, distinct from the monitoring operators use. | `[DAR]` | Ch 34, Ch 44 |
| **Trajectory** | The full record of one run — every span, with what the model could see at each — and the raw material of the evidence corpus. | `[AHE]` | Ch 41, Ch 44 |
| **Trace store** | The durable home of trajectories; the largest and highest-risk dataset in the architecture. | `[INF]` | Ch 37, Ch 49 |
| **Span** | One observed operation inside a run, wrapped in an envelope that carries its identity and harness version. | `[BP]` | Ch 34 |
| **Result envelope** | The fixed identity wrapper on every observation, which is what makes a trajectory navigable rather than a pile of records. | `[DAR]` | Ch 34 |
| **Context span** | The capture of what the model could see for one call: stable digest, semi-stable digest, and the volatile band verbatim. | `[INF]` | Ch 44, Ch 46 |
| **Redaction at capture** | Removing secrets as a trajectory is written rather than when it is read, because a store with history cannot be cleaned afterwards. | `[INF]` | Ch 37 |
| **Outcome-weighted retention** | Deciding at seal what to keep based on how the run ended, rather than sampling uniformly and losing the rare interesting runs. | `[INF]` | Ch 41 |
| **Seal** | Closing a trajectory at run end, when the outcome is finally known and the retention class can be assigned. | `[INF]` | Ch 37 |
| **Tombstone** | The envelope that survives when a trajectory's content expires, preserving aggregate answers and an auditable deletion. | `[INF]` | Ch 37 |
| **Evidence corpus** | The retained, distilled subset of trajectories that the evolution loop reads. | `[AHE]` | Ch 44 |

---

**Next:** Chapter 17 — *The State Manager.* Checkpointing, the lease plus version-CAS advance, the
run store, and why an advisory lock is the wrong tool — the mechanism Chapter 8 named and deferred,
built properly, with recovery as one indexed query.
