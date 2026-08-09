```
  Level 4 · Chapter 34
  OBSERVABILITY
  Requires   C9 Three Flows, C16 The Observation System,
             C21 Durable Execution, C33 Scalability
  Unlocks    C36 Reliability and SLOs, C37 Tenancy and Governance,
             C41 Evaluation Infrastructure
  Diagrams   Core (5)
```

# Chapter 34 — Observability

---

## 1. Motivation

### 1.1 Cold open

At 09:15 on a Thursday, Atlas's success rate is 94%. By 13:30 it is 71%.

The on-call engineer opens the dashboards. Request latency: normal. Error rate: 0.3%, normal. Model
call latency p95: normal. Token spend per run: normal. Database connections: eleven, as always.
Queue depth: flat. Sandbox host utilisation: 40%. No deploy alerts, no infrastructure alerts, no
provider incidents.

Every signal the team has says the system is healthy, and roughly one run in four is producing a
useless pull request.

It takes four hours. The cause is a tool description edited in the 09:10 deploy: `search_files` had
its `pattern` parameter documented as accepting a regular expression, where previously the example
had shown a glob. The model began passing regexes. `search_files` treats its input as a glob, found
nothing, and returned an empty list — which is a perfectly valid result, returned with exit code
zero, in eleven milliseconds.

The runs then proceeded on the conclusion that the files did not exist. They wrote new
implementations of code that was already there. Every step succeeded. Every tool returned cleanly.
The infrastructure was, throughout, in excellent health.

The team had first-rate observability of the machinery and none at all of the work.

### 1.2 In plain language

There are two completely different questions you can ask about a running system, and they need
different instruments.

The first is *is the machinery working?* Are requests fast, are errors rare, are the queues short,
is anything running out of room. Every engineer knows how to answer this and there is excellent
off-the-shelf tooling for it.

The second is *is the work any good?* Did the run understand the task, did it see what it needed to
see, did it produce something useful. In the cold open the answer was no for a quarter of the runs,
and every instrument measuring the first question said everything was fine — because everything
*was* fine, by the standards of the first question.

The two share almost no signals. Latency does not tell you whether a search returned the right
files. Error rate does not move when a tool succeeds and returns nothing useful. A team with only
the first set of instruments is in the position of the on-call engineer: looking at a wall of green
while a quarter of the output is wrong.

The second question also needs a different *shape* of data. Aggregate numbers can tell you a rate is
falling; they cannot tell you what any particular run saw and did. For that you need a record of
individual runs, and individual runs are expensive to store because there is one per run and each is
large. So the second system is a sampling problem as much as a measurement problem, and the sampling
has to be deliberately unfair — because the runs worth keeping are the rare ones.

### 1.3 Why this chapter exists

Chapter 16 built the observation system and made the strongest argument in it: capture what the
model *could see*, not merely what it did. That chapter was about capture. This one is about what
happens to the captured material afterwards — what gets aggregated, what gets kept, what gets
alerted on, and who reads it.

`[DAR §15]` specifies a set of signals that make a runtime operable, and this chapter takes them
seriously enough to derive rather than list them: §5.1 shows eleven, each traced back to the chapter
whose failure it detects. That derivation matters more than the list, because a signal adopted
without its failure attached becomes a graph nobody looks at.

There is also a dependency running forward. Chapter 41 needs a corpus to evaluate against and
Chapter 44 needs one to learn from, and both consume what this chapter decides to retain. **A
retention policy set here by disk cost is a decision about whether Level 5 is possible**, made
eighteen months earlier, by someone optimising a storage bill. Chapter 37 adds the other half of
that decision, which is that the same corpus is the highest-risk data in the architecture.

### 1.4 What previous framings got wrong

**"Observability means metrics, logs, and traces."** Those are three data types. They are not three
questions, and organising by data type is how a team ends up with excellent coverage of one question
and none of the other. Organise by what you are trying to find out.

**"Trace everything."** Chapter 16 already measured what that costs: fourteen terabytes that explain
nothing. Full-fidelity capture of every run is affordable at small scale, unaffordable at large
scale, and unhelpful at both — because the volume is the reason nobody reads it.

**"Sample uniformly."** Uniform sampling keeps a representative population, and the runs worth
keeping are unrepresentative by definition. A 1% uniform sample of a 4% failure rate keeps four
failures in ten thousand runs, which is not enough to characterise anything.

**"Alert on error rate."** Every failure in Level 3 produces no errors, and the cold open produces
none either. An alerting strategy built on error rate is blind to the entire class of failure this
handbook has spent twelve chapters describing.

**"Add a dashboard for it."** A signal with no attached failure and no threshold is a graph
somebody made. §5.1's derivation exists to prevent that: every signal here names the failure it
detects and what to do about it.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

An aircraft carries two entirely separate recording systems and nobody confuses them.

The **instruments** tell the crew what is happening right now: airspeed, altitude, engine
temperature, fuel flow. They are aggregate, low-cardinality, continuously watched, and they exist to
support decisions in the next few seconds.

The **flight data recorder** captures everything, per flight, at high fidelity. Nobody watches it. It
is read afterwards, by people reconstructing a specific sequence of events, and its value is
entirely in being able to answer questions that were not anticipated.

Both exist on every aircraft. Neither substitutes for the other, and no engineer has ever proposed
replacing the altimeter with a recorder or the recorder with a gauge. That is the correct structure,
and it is the structure this chapter argues for.

The break is in what happens to the recorder's contents, and it is a large break with two
consequences.

An aircraft's recorder is read **rarely, by investigators, after an accident**. Its contents are
bounded — one flight — and its use is exceptional.

A trajectory store is read **continuously, by engineers, during ordinary work**, and it is also the
corpus that Chapter 41 evaluates against and Chapter 44 learns from. That changes two things at
once. Its retention economics are different, because it is an asset with ongoing value rather than
an insurance policy. And its risk profile is completely different, because it contains, verbatim,
everything the model could see — which is customer source code, issue text, log output, and whatever
else was in context (Chapter 37).

So the analogy gives the right two-system structure and understates what the second system becomes.
It is not a black box. It is a growing archive of other people's material that many people read.

### 2.2 Why two systems, and why the second must sample unfairly

```
  (1) Something is wrong. Two genuinely different questions:
      is the MACHINERY working, and is the WORK good?

  (2) Infrastructure signals answer the first: latency, errors,
      saturation, queue depth. Well understood, off the shelf,
      and the team already has them.

  (3) They cannot answer the second, and this is not a gap to be
      closed by adding more of them. In the cold open every
      infrastructure signal was normal while 29% of the output
      was wrong -- because the machinery WAS healthy.

  (4) Answering the second requires knowing what a particular run
      saw and what it did. Not a rate; a record.

  (5) Records are high-cardinality by construction. There is one
      per run and run ids are unbounded, which is precisely what
      a metrics system cannot hold.

  (6) So: two stores. Bounded-cardinality metrics for aggregates,
      per-run traces for individuals. Two systems because two
      shapes of data, not because two teams.

  (7) Full-fidelity traces for every run are enormous (C16). So a
      sampling policy is forced.

  (8) And it CANNOT be uniform. The runs worth keeping -- the
      failures, the stalls, the long tail, the overrides -- are
      rare by definition. Uniform sampling keeps a representative
      population and discards exactly the population you needed.
```

Step (8) is the one that gets implemented wrong most often, because uniform sampling is what every
tracing library does by default and it is correct for the workload those libraries were built for.

### 2.3 Two systems, side by side

| | **Infrastructure observability** | **Trajectory observability** |
|---|---|---|
| Question | Is the machinery working? | Is the work good? |
| Shape | Aggregates, bounded cardinality | Records, one per run |
| Watched | Continuously | On demand, after a question |
| Volume | Kilobytes per minute | Megabytes per run |
| Retention | Weeks | Months to years (Ch 41 needs it) |
| Risk | Low | The highest in the architecture (Ch 37) |
| Alerts on | Thresholds and rates | Distributions and absences |
| Cold open | All green | Would have shown it in minutes |
| Tooling | Excellent, off the shelf | You are building it |

The last row is the honest one. The first column is a solved problem with mature vendors. The second
is not, and a team that adopts an observability platform and considers the topic handled has bought
an excellent solution to the question that was not failing.

### 2.4 The mental model to carry

Two systems, two shapes, two questions. Aggregates tell you a rate moved; records tell you why.
Every signal is adopted with a named failure and a threshold, or it is a graph nobody reads. And the
sampling policy for records is deliberately unfair: keep every failure, keep the tail, keep anything
a human touched, and sample the successes.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |            RUNTIME (every component, C10-C32)                |
   +--------------------------------------------------------------+
          |                                        |
          | (1) counters, gauges, histograms       | (2) spans and
          |     bounded cardinality                |     observations
          v                                        v
   +------------------------+          +---------------------------+
   |   METRICS PIPELINE     |          |    TRACE PIPELINE         |
   |                        |          |                           |
   |  labels: surface,      |          |  one record per run       |
   |    work class, tool,   |          |  what the model COULD see |
   |    verdict, tenant     |          |    (C16)                  |
   |                        |          |                           |
   |  NEVER: run_id,        |          |  redacted AT CAPTURE      |
   |    node_id, user_id    |          |    (C16, C37)             |
   |    -- unbounded (4.2)  |          |                           |
   +------------------------+          +---------------------------+
          |                                        |
          | (3)                                    | (4) sampling:
          v                                        |     unfair, on
   +------------------------+                      |     purpose
   |   ALERTING             |                      v
   |                        |          +---------------------------+
   |  thresholds AND        |          |    TRACE STORE            |
   |  ABSENCES (5.3)        |          |                           |
   +------------------------+          |  the corpus C41 evaluates |
                                       |  against and C44 learns   |
                                       |  from -- and the highest  |
                                       |  risk data set in the     |
                                       |  architecture (C37)       |
                                       +---------------------------+
                                                   |
                          +------------------------+---------+
                          |                                  |
                          v                                  v
                 +------------------+            +---------------------+
                 | Humans debugging |            | C41 evaluation      |
                 | one run          |            | C44 evolution       |
                 +------------------+            +---------------------+

  Figure 34.1 -- Two pipelines, two shapes, two audiences (D1
                 High-Level Architecture)

  (1) aggregates only; a label with unbounded values destroys a
      metrics backend and is the single most common outage this
      subsystem causes
  (2) per-run records, captured whole
  (3) alerts fire on thresholds AND on absences -- every Level 3
      failure is detected by an absence
  (4) sampling is where the cost is decided, and where a uniform
      policy throws away the entire useful population
```

### 3.1 The trace store has three consumers and only one of them is present today

Engineers debugging a run are the obvious consumer and the one that drives the design. The other two
arrive later and have different requirements:

- **Chapter 41's evaluation** needs a corpus with known outcomes, which means traces must retain the
  verdict alongside the trajectory, and must be queryable by task type rather than only by run id.
- **Chapter 44's evolution loop** needs enough history to distinguish a real improvement from noise,
  which is a retention question measured in months.

`[BP]` Both requirements cost almost nothing if designed in and are expensive to retrofit — mostly
because retrofitting means the months of history you would have wanted do not exist. Decide the
retention window against Chapter 41's needs, not against the storage bill, and write down which
decision was made and why.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                    OBSERVABILITY MACHINERY                     |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Metric emitters        |  |   Span annotator          |   |
   |  |                          |  |                           |   |
   |  |  in-process, free        |  |  every span carries:      |   |
   |  |  histograms for          |  |    flow (C9): control |   |
   |  |  durations, counters     |  |      data | event         |   |
   |  |  for events              |  |    surface (C33)          |   |
   |  |                          |  |    tenant                 |   |
   |  |  LABEL ALLOWLIST, not    |  |                           |   |
   |  |  a denylist (4.2)        |  |  one enum turns C9's cold |   |
   |  |                          |  |  open into a query        |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Sampling policy        |  |   Anomaly detectors       |   |
   |  |                          |  |                           |   |
   |  |  ALWAYS keep:            |  |  identity partial match   |   |
   |  |   failures, stalls,      |  |    -> PAGE, never log     |   |
   |  |   overrides, gates,      |  |    (5.4)                  |   |
   |  |   dead letters, the      |  |                           |   |
   |  |   duration tail          |  |  absence detectors: ages, |   |
   |  |  SAMPLE: clean successes |  |  and controls that have   |   |
   |  |                          |  |  gone quiet (5.3)         |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 34.2 -- Inside the observability machinery (D2 Low-Level
                 Architecture)
```

### 4.1 The span annotator, and one enum

Chapter 9 opened with three engineers giving three correct and incompatible answers to "where does a
run decide what to do next", because each was reading the system along a different axis without
saying which. It proposed one fix: tag every span with the flow it belongs to.

That fix belongs here, and it is nearly free — one enum on a structure the system already emits. Its
payoff is that "show me the control-flow spans for this run" becomes a filter rather than an
argument, and a trace of a hundred and forty spans becomes readable by someone who was not there.

`[BP]` Add `surface` (Chapter 33) and `tenant` alongside it. Three low-cardinality labels turn the
trace store from a pile of spans into something queryable along every axis the book has established.

### 4.2 Label cardinality is an allowlist, not a denylist

The most common self-inflicted outage in this subsystem is a metric labelled with something
unbounded — a run id, a node id, a file path, an error message. Each distinct value creates a time
series; a million runs creates a million series; the metrics backend falls over, and it takes the
infrastructure observability of the *other* system with it at the exact moment it is needed.

A denylist does not work, because the next unbounded label is one nobody thought of.

`[BP]` Enforce an allowlist in the emitter: a fixed set of permitted label names, with anything else
rejected at the call site rather than at the backend. It is twenty lines, it fails loudly in
development, and it removes a whole class of production incident permanently.

High-cardinality identifiers belong in traces, where one record per run is the design rather than an
accident.

---

## 5. Eleven Signals, and What They Detect

### 5.1 Derived, not listed

`[DAR §15]` calls for a set of signals that make a runtime operable. Presenting them as a list
invites adoption without understanding, which produces dashboards. Each one below names the chapter
whose failure it detects — and every one of those failures, from Level 3, produces no error.

```
                                                            LAYER VIEW

   INFRASTRUCTURE -- is the machinery working?
   +--------------------------------------------------------------+
   |  1. step duration p95                  C33  saturation, 10-20 |
   |                                             min before        |
   |                                             anything else     |
   |  2. binding surface (a NAME)           C33  ends the "add     |
   |                                             workers" argument |
   |  3. queue time by class and tenant     C23  convoy effects    |
   |  4. age of oldest unclaimed event      C22  the silent stall  |
   |  5. pool checkout / semaphore          C33  headroom, and     |
   |     occupancy                               saturation onset  |
   +--------------------------------------------------------------+

   RUNTIME CORRECTNESS -- is the state machine sound?
   +--------------------------------------------------------------+
   |  6. age of oldest non-terminal node    C24  an unfired join;  |
   |     in a healthy run                        every dashboard   |
   |                                             green             |
   |  7. age of oldest outstanding          C27  the migration     |
   |     obligation                              left on staging   |
   |  8. identity partial-match count       C21  the identity      |
   |                                             function is       |
   |                                             WRONG -- page,    |
   |                                             never log (5.4)   |
   +--------------------------------------------------------------+

   TRAJECTORY -- is the work good?
   +--------------------------------------------------------------+
   |  9. verdict distribution + false-pass  C28  the grader, and   |
   |     rate against the golden set             the work          |
   | 10. novel-state rate; stall rate       C29  a healthy run     |
   |                                             going in circles  |
   | 11. gated-effect coverage (must be     C30  a bypass around   |
   |     exactly 1.0)                             the authority     |
   |                                             mechanism         |
   +--------------------------------------------------------------+

   THE COLD OPEN would have been caught by signal 9 within minutes:
   the verdict distribution shifted from 94% PASS to 71% at 09:15,
   which is a step change in a low-cardinality aggregate. The team
   had signals 1 through 5 and none of 6 through 11.

   NOTE the shape of six of the eleven. Signals 4, 6, 7, and parts
   of 10 and 11 are AGES and ABSENCES, not rates. That is not a
   stylistic preference; it is what Level 3's failures require
   (5.3).

  Figure 34.3 -- Eleven signals, each with the failure it detects
                 (D7 Data Flow)
```

### 5.2 Which of the eleven to build first

All eleven eventually; three of them immediately, and the ordering is not obvious.

**Signal 9 first — the verdict distribution.** It is the cheapest of the eleven to build, it detects
the entire class of failure in the cold open, and it is the only one that answers the question that
matters to whoever is paying. A counter keyed by verdict rank, with a step-change alert.

**Signal 1 second — step duration p95.** The earliest warning of saturation, ahead of everything
else by ten to twenty minutes (Chapter 33 §11).

**Signal 8 third — identity partial matches.** Rare, catastrophic, and silent (§5.4).

`[BP]` The signals not to build first are the ages (4, 6, 7), not because they matter less but
because they detect failures that require the corresponding subsystems to be under real load before
they can occur. Build them before the second production quarter, not before the first customer.

### 5.3 Alert on absence

Every failure in Level 3 announces itself by something *not* happening, which makes a threshold
alarm useless. Six patterns, and they cover the whole level:

| Pattern | Example | Alert |
|---|---|---|
| **Age of oldest X** | Unclaimed event, non-terminal node, unresolved obligation, pending gate | Age crosses a bound |
| **A control that has gone quiet** | `egress.blocked`, `capability.denied`, `fence.rejected` all at zero | Rate is zero over a long window |
| **A distribution that has shifted** | Verdict mix, plan-per-goal, response mix | Step change, not threshold |
| **A ratio that must be exact** | Gated-effect coverage | Anything other than 1.0 |
| **A count that must be zero** | Observations with no provenance label; identity partial matches | Anything above zero |
| **Novelty that stopped** | Novel durable state per effectful step | Zero over a window |

The second row is the counter-intuitive one and it has been noted three times now — in Chapters 31
and 32 and again here. **A safety control that never fires is more often unwired than unneeded.** A
year of zero `egress.blocked` events is not a year of well-behaved runs; it is usually a year of an
allowlist that was widened to `*` during an incident and never narrowed.

`[BP]` For every control of that shape, add a synthetic probe: a scheduled run that deliberately
triggers it, in staging, and alerts if it does not fire. It is the only way to distinguish a quiet
control from a dead one.

### 5.4 Identity partial matches page a human

This one deserves its own subsection because its severity is wildly out of proportion to its
frequency.

Chapter 21's activity identity is a hash over an activity's inputs, used to decide whether work has
already been done. A **partial match** is any state where the identity function's behaviour is
internally inconsistent: the same identity recorded with two different outcomes, or two identities
for what the recorded inputs say is the same work, or an identity present with no corresponding
outcome after a completed attempt.

Any of those means the identity function is wrong. And the identity function is what makes retry
safe, what makes plan repair free (Chapter 26 §5.3), what bounds attempt counts (Chapter 27 §4.2),
and what protects effects when no fence token is available (Chapter 32 §5.3). Four subsystems'
correctness rests on it, and none of them will report a problem — they will produce duplicate
effects, silently, at a rate nobody is measuring.

`[BP]` This is a page, not a log line, not a dashboard, and not a daily digest. The expected count
is zero, the observed count should be zero, and a single occurrence means one of the runtime's
foundational assumptions is not holding. Treat the first one as an incident even if nothing visible
has broken yet, because by the time something visible breaks the duplicates will be weeks old.

### 5.5 Sampling, deliberately unfair

Full trace retention is unaffordable and uniform sampling discards the useful population. The policy
that works is a small allowlist of always-keep categories, plus a low uniform rate over everything
else:

```
  ALWAYS keep the full trace:
    - any run whose verdict is FAIL or UNGRADABLE     (C28)
    - any run that stalled, even if it recovered      (C29)
    - any run with an override, a gate, or a steer    (C30)
    - any run that raised a dead letter               (C27)
    - any run in the top 1% by duration or by cost    (C29, C35)
    - any run whose tenant is newly onboarded         [BP]

  SAMPLE at a low rate:
    - clean successes

  Rationale: every category above is either rare, expensive, or
  the thing you will be asked about. Clean successes are the
  population you have the most of and learn the least from -- but
  the rate must be NONZERO, because C41 needs positive examples
  and a corpus of only failures teaches a grader the wrong prior.
```

`[BP]` The newly-onboarded-tenant rule is worth the line it costs. The first two weeks of a new
customer's traffic is when unfamiliar repository shapes, unusual tool usage, and everything nobody
anticipated arrives — and it is exactly when a uniform sampler has the least of it.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  The cold open, with signal 9 present.

  time   event                          what fires
  -----  -----------------------------  --------------------------
  09:10  deploy: tool description
         edited
  09:12  first runs on the new
         description
  09:14  verdict counter: PASS 94% ->
         91% over the last 100 runs
  09:17  verdict counter: 84%          step-change detector fires
                                        on signal 9: "verdict
                                        distribution shifted more
                                        than 2 sigma in 5 min"
  09:18  on-call opens the alert
  09:18  alert links to: 20 sampled
         FAIL traces from the last
         10 minutes (always-keep
         category, 5.5)
  09:20  engineer opens one trace,
         filters spans to flow=data
         (C9, section 4.1)
  09:21  sees: search_files(pattern=
         "^test_.*\\.py$") -> []
         and the next span shows the
         model concluding the files
         are absent
  09:22  diffs against a PASS trace
         from 09:05: same tool,
         pattern="test_*.py" -> 41
         results
  09:23  rollback initiated

  ELAPSED: 8 minutes from first degradation to rollback, of which
  6 were the detector waiting for enough samples to be confident.

  COMPARE the cold open: 4 hours 15 minutes, and the diagnosis came
  from someone remembering that a deploy had happened.

  FAILURE BRANCH -- signal 9 exists but traces are sampled
  UNIFORMLY at 1%:

    09:17  alert fires correctly
    09:18  on-call looks for failing traces
           4% failure rate x 1% sampling = 4 traces per 10,000 runs
           at 40 runs/min, that is one failing trace every 25 min
    09:43  first failing trace available
    -- the detection was fast and the diagnosis was not, because
       the sampler kept a representative population and the useful
       population is not representative (2.2 step 8).

  Figure 34.4 -- Eight minutes instead of four hours (D4 Sequence)
```

The failure branch is the point of the figure. Detection and diagnosis are separate capabilities
with separate designs, and a system can be excellent at the first and useless at the second. Signal 9
is aggregate and cheap; what turned it into a rollback in five more minutes was having twenty
complete failing traces already on disk.

---

## 7. State Management

```
                                                            STATE VIEW

   TRACE LIFECYCLE

      {{ capturing }}
          |  run in flight; observations written as they occur,
          |  REDACTED AT CAPTURE (C16, C37) -- never at read
          v
      {{ complete }}
          |
          +---- matches an always-keep category (5.5) --+
          |                                             |
          +---- sampled in at the low rate -------------+
          |                                             |
          |                                             v
          |                                    {{ retained }}
          | not sampled                             |
          v                                         | retention window
      {{ discarded }}  (terminal)                   | (C37, and C41's
          summary metrics were already              |  needs, not disk
          emitted; the RECORD is gone               |  cost)
                                                    v
                                             {{ expired }} (terminal)

      ILLEGAL: {{ complete }} -> {{ retained }} for a record that
      was not redacted during {{ capturing }}. Redaction at read
      time means the raw material exists on disk and every future
      reader is a new exposure. C37 makes this argument in full;
      it is stated here because this is where the transition is
      implemented.

      ILLEGAL: {{ discarded }} for anything in an always-keep
      category, including when the sampler is under memory
      pressure. The always-keep set is a correctness property of
      the observability system, not a best-effort behaviour.

  Figure 34.5 -- Trace lifecycle (D6 State Diagram)
```

### 7.1 Metrics are derived and traces are not

Metrics can be recomputed from traces; traces cannot be recomputed from anything. That asymmetry
sets the priority under pressure: if the metrics pipeline is backed up, drop metrics. If the trace
pipeline is backed up, apply backpressure or spill to disk — but do not drop an always-keep trace,
because the run it belongs to happened once.

`[BP]` This is worth encoding rather than intending. Two pipelines with two different overflow
policies: metrics drop, traces block-then-spill.

### 7.2 The sampling decision is made at the end, not the beginning

A run's category is not known until it finishes — you cannot know at step 3 that it will fail at
step 40. So capture is unconditional and sampling is applied at completion.

That has a cost worth naming: a run's full trace is buffered until it terminates, and a six-hour run
buffers for six hours. `[BP]` Spill to cheap storage during the run and promote or delete at
completion, rather than holding it in memory. The alternative — deciding to sample at the start —
means the failing runs you needed were decided against before anything went wrong.

---

## 8. Internal APIs

```python
from typing import Protocol
from dataclasses import dataclass


class MetricEmitter(Protocol):

    def observe(self, name: str, value: float, labels: dict[str, str]) -> None:
        """Record a measurement.

        `labels` is checked against an ALLOWLIST at the call site and
        rejects anything not on it. Not a denylist -- the next
        unbounded label is always one nobody thought of. A run_id in a
        metric label is the most common self-inflicted outage in this
        subsystem, and it takes down infrastructure observability at
        the exact moment it is needed (4.2).
        """


class TraceSink(Protocol):

    def span(self, run_id: str, span: "Span") -> None:
        """High-cardinality by design. Every span carries flow (C9),
        surface (C33), and tenant -- three low-cardinality axes that
        make a 140-span trace readable by someone who was not there.
        """

    def finalise(self, run_id: str, outcome: "RunOutcome") -> "Retention":
        """Apply the sampling policy AT COMPLETION, because a run's
        category is not known until it ends (7.2).

        Always-keep categories are a correctness property, not a
        best-effort behaviour. This method may block or spill; it may
        not silently drop an always-keep record.
        """


class AnomalyDetector(Protocol):

    def identity_partial_match(self, detail: "IdentityAnomaly") -> None:
        """PAGE. Not a log line, not a dashboard, not a daily digest.

        A partial match means C21's identity function is wrong, and
        four subsystems' correctness rests on it -- retry safety,
        free plan repair, attempt caps, and effect protection where
        no fence token exists. None of them will report a problem.
        They will produce duplicate effects at a rate nobody is
        measuring (5.4).
        """
```

`AnomalyDetector.identity_partial_match` is a method rather than a metric on purpose. A counter can
be incremented and ignored; a method whose contract is "this pages" states the severity where the
code is written, and there is no threshold to be tuned downward later by someone who found it noisy.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class Flow(str, Enum):
    CONTROL = "control"
    DATA = "data"
    EVENT = "event"


@dataclass(frozen=True)
class Span:
    span_id: str
    parent_id: str | None
    name: str
    flow: Flow                  # C9, section 4.1 -- one enum, large payoff
    surface: str | None         # C33: which capacity surface
    tenant: str
    started_at_seq: int         # event-log position, not wall clock
    duration_ms: float
    queue_ms: float             # SEPARATE from duration (C33 sec 7.1)
    attributes: dict            # unbounded here, and only here


@dataclass(frozen=True)
class Retention:
    keep: bool
    reason: str                 # which always-keep category, or "sampled"
    expires_at: str | None      # from C41's needs, not from disk cost
    redacted_at_capture: bool   # must be True to be retained (7)


@dataclass(frozen=True)
class IdentityAnomaly:
    kind: str                   # "same_identity_two_outcomes"
                                # | "two_identities_same_inputs"
                                # | "identity_without_outcome"
    identity: str
    run_ids: tuple[str, ...]
    detected_at_seq: int
```

`Span.attributes` being the only unbounded field, and being in the trace rather than the metric, is
the structural statement of §4.2. High-cardinality material has exactly one home.

`Retention.reason` records *why* a trace was kept. Six months later, when someone asks whether the
corpus is biased, the distribution of retention reasons is the answer — and it cannot be
reconstructed from the traces themselves.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Every component | Metric emitter | In-process, free | Counters and histograms, allowlisted labels |
| Every component | Trace sink | In-process, buffered, spilled | Spans with flow, surface, tenant |
| Trace sink | Trace store | Batched write at completion | Retained records only |
| Metrics | Alerting | Scrape or push | Thresholds, ages, absences, distribution shifts |
| Anomaly detector | Paging | Direct | Identity partial matches (§5.4) |
| Trace store | Chapter 41 | Query by task type and verdict | The evaluation corpus |
| Trace store | Chapter 44 | Query by harness version | The evolution corpus |

The last two rows do not exist yet in most systems and are the reason the retention decision belongs
to Chapter 41 rather than to a storage budget (§3.1). `[BP]` Make the trace store queryable by task
type and verdict from the start. Adding those indexes later is trivial; wishing you had the last six
months of data is not.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Infrastructure healthy, work wrong | Signal 9 — verdict distribution | The cold open. Build this one first (§5.2) |
| Unbounded label in a metric | Metrics backend degradation | Allowlist at the call site (§4.2) |
| Uniform trace sampling | Detection fast, diagnosis slow (§6 branch) | Always-keep categories (§5.5) |
| Identity partial match | The detector — nothing else | Page. Four subsystems depend on it (§5.4) |
| Safety control quiet for months | Rate at zero over a long window | Synthetic probes that deliberately trigger it (§5.3) |
| Redaction applied at read | Raw material present on disk | Redact at capture; refuse to retain otherwise (§7) |
| Retention set by storage cost | Chapter 41 finds no usable history | Set it against evaluation needs, in writing (§3.1) |
| Always-keep trace dropped under pressure | Missing traces for known failures | Block or spill; never drop (§7.1) |
| Alerting built on error rate alone | Every Level 3 failure passes unnoticed | Alert on ages, absences, and distribution shifts (§5.3) |
| Metrics pipeline outage during an incident | Loss of visibility at the worst moment | Independent failure domains for the two pipelines |

The last row is worth acting on rather than noting. `[BP]` The two pipelines should not share a
backend, a network path, or a failure mode. An observability system that fails together with the
system it observes is available exactly when it is not needed.

---

## 12. Scalability

**Metric emission is free and must stay free.** In-process histograms, exported periodically. `[BP]`
Never a network call per measurement — Chapter 33 §12 made the same point about the service-time
meter and the reason is identical.

**Trace volume is the cost, and sampling is the control.** Chapter 16 measured full capture at
fourteen terabytes; the always-keep categories of §5.5 plus a low uniform rate typically land at a
few percent of that while retaining more of what anyone reads.

**Buffering long runs is the operational cost of §7.2.** A six-hour run buffers for six hours. Spill
to object storage during the run, promote or delete at completion.

**Query patterns determine the store, not volume.** Debugging is a point lookup by run id.
Chapter 41 is an analytical scan by task type and verdict. Chapter 44 is a scan by harness version
over months. `[BP]` The first is served by anything; the second and third want columnar storage and
the right partition key, and choosing that at the start costs nothing.

---

## 13. Production Engineering

### 13.1 The five numbers

Of the eleven signals, five belong on the wall:

- **Verdict distribution**, as a stacked rate. The cold open, and the only signal that answers the
  question a customer would ask.
- **Step duration p95.** Saturation, ten to twenty minutes early.
- **Binding surface**, as a name. Ends the recurring capacity argument (Chapter 33 §4.2).
- **The four ages**: oldest unclaimed event, oldest non-terminal node, oldest outstanding
  obligation, oldest pending gate. One panel, four lines, and it covers the majority of Level 3.
- **Identity partial matches.** Expected zero, and its presence on the wall is a statement about how
  seriously it is taken.

### 13.2 The review question

For every signal in the system: **what failure does this detect, and what is the threshold?**

A signal without both is a graph. That is not a criticism of graphs — exploratory dashboards are
useful — but they should be distinguished from operational signals, and the distinction is exactly
these two answers. Applying the question to an existing dashboard usually retires half of it.

### 13.3 Teaching this to a new engineer

Show them the cold open's dashboards, all green, and ask what is wrong. Give them as long as they
want. There is nothing to find, and the frustration is the lesson — every instrument was working and
every one was measuring the wrong question.

Then ask what they would need to see to catch it. Most people arrive at "what did the model
actually get back from that tool", which is a per-run record rather than an aggregate, and the
two-system structure follows from there without being taught.

---

## 14. Relation to AHE

`[AHE App. A]` Trajectory-level tracing is the source's, and it is a precondition rather than a
feature: an evolution loop reasoning about harness behaviour needs to see what runs saw, and cannot
work from aggregates. Everything in this chapter's second column is what that requires in practice.

`[INF]` The forward dependency is the reason this chapter sits before Chapter 41 rather than beside
it. Chapter 41 needs a corpus with verdicts, task types, and enough history to separate signal from
noise. Chapter 44 needs the same corpus partitioned by harness version. Both are consumers of a
retention decision made here, and a retention window chosen against a storage bill in the first
quarter forecloses Level 5 in the sixth.

`[INF]` There is a containment point consistent with the rest of Level 3 and 4. An evolution loop
that can edit the sampling policy can improve its measured results by retaining fewer failures —
not by deceiving anyone, but because a corpus with fewer failures in it produces better-looking
aggregates. The sampling policy, the retention window, and the signal thresholds belong outside the
evolvable workspace, joining the gate policy, the effect tags, the verifier, and the golden set.

That list is now seven items long and every one of them was found the same way: by noticing, in a
chapter about something else, that an outcome-based reward would remove a protection. Chapter 46 has
to decide whether that method has found all of them. It has not.

---

## 15. Industry Perspective

**`[DAR §15]`** The operable-runtime signal set is specified. §5.1's contribution is deriving each
one from the failure it detects rather than presenting a list, because a signal adopted without its
failure becomes a graph nobody reads.

**`[BP]` The three-pillars framing — metrics, logs, traces — organises by data type and is why the
cold open happens.** Organising by question instead produces two systems that happen to use all
three data types, and immediately reveals which question has no instruments.

**`[BP]` Cardinality discipline is a solved problem that every team relearns.** The allowlist in
§4.2 is twenty lines and prevents a recurring outage. That it is not standard practice is a
consistent and mildly surprising observation across the industry.

**`[BP]` Tail-based sampling is well supported by modern tracing systems and is under-configured.**
The always-keep categories of §5.5 are expressible in most collectors today. Most deployments run
head-based uniform sampling because it is the default.

**`[INF]` Trajectory observability has no mature tooling and the gap is widening.** Evaluation
platforms are emerging, but the operational side — the thing an on-call engineer opens at 09:18 —
is still built in-house nearly everywhere. Budget for building it; do not budget for buying it.

**`[FUT]` Automatic diagnosis from trace differences is the obvious next step.** The 09:22 step in
§6 — diff a failing trace against a passing one from an hour earlier — is mechanical, and the data
to do it is present. Nobody appears to be doing it automatically, and it would have turned eight
minutes into two.

---

## 16. Key Takeaways

1. **Two questions, two systems.** Is the machinery working, and is the work good. They share almost
   no signals, and a team with only the first watches a wall of green while a quarter of the output
   is wrong.
2. **Build signal 9 first.** The verdict distribution is the cheapest of the eleven, detects the
   cold open's entire failure class, and answers the question a customer would ask.
3. **Alert on ages, absences, and distribution shifts.** Every Level 3 failure produces no errors,
   so an alerting strategy built on error rate is blind to all of them.
4. **A control that never fires is usually unwired.** Add synthetic probes that deliberately trigger
   each safety control, or a year of silence will be read as a year of good behaviour.
5. **Identity partial matches page a human.** Four subsystems' correctness rests on the identity
   function, none of them will complain, and the failure is duplicate effects at an unmeasured rate.
6. **Sample unfairly.** Keep every failure, stall, override, gate, dead letter, and tail run;
   sample clean successes at a low but nonzero rate. Uniform sampling keeps a representative
   population and discards exactly the one you needed.
7. **The retention window is a decision about whether Level 5 is possible**, made years earlier by
   whoever was looking at the storage bill. Set it against Chapter 41's needs and write down why.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Infrastructure observability** | Aggregate signals answering whether the machinery is working, which is the question that was not failing in the cold open. | `[BP]` | Ch 36 |
| **Trajectory observability** | Per-run records answering whether the work is good, high-cardinality by construction and built in-house nearly everywhere. | `[AHE]` | Ch 41, Ch 44 |
| **Label allowlist** | A fixed set of permitted metric label names enforced at the call site, because a denylist cannot anticipate the next unbounded value. | `[BP]` | Ch 37 |
| **Flow annotation** | One enum per span recording which of Chapter 9's three axes it belongs to, turning an argument into a filter. | `[INF]` | Ch 41 |
| **Absence alerting** | Alerting on ages, silences, and distribution shifts rather than rates, because Level 3's failures produce no errors. | `[INF]` | Ch 36 |
| **Synthetic probe** | A scheduled action that deliberately trips a safety control, so a quiet control can be distinguished from a dead one. | `[BP]` | Ch 36, Ch 40 |
| **Identity partial match** | Any internal inconsistency in the activity-identity function, which is a page rather than a log because four subsystems silently depend on it. | `[DAR]` | Ch 40 |
| **Unfair sampling** | A retention policy that always keeps failures, stalls, overrides, gates, dead letters, and the tail, and samples clean successes. | `[BP]` | Ch 41 |
| **Always-keep category** | A class of run whose trace retention is a correctness property rather than a best-effort behaviour. | `[INF]` | Ch 41 |
| **Retention as a Level 5 decision** | Choosing the trace retention window against evaluation and evolution needs rather than against storage cost. | `[INF]` | Ch 37, Ch 41 |

---

**Next:** Chapter 35 — *Cost Engineering and Token Economics.* This chapter measured whether the
work is good; the next one asks what it cost to be good, and shows why the two questions cannot be
separated — a team that reduced its cost per call by 40% and raised its cost per successful outcome
at the same time, without either number being wrong.
