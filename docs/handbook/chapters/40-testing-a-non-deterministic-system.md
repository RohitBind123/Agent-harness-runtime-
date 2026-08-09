```
  Level 4 · Chapter 40
  TESTING A NON-DETERMINISTIC SYSTEM
  Requires   C13 The Reasoning Engine, C21 Durable Execution,
             C32 Distributed Execution, C34 Observability,
             C39 GitOps and CI/CD
  Unlocks    C41 Evaluation Infrastructure, C47 Attribution and Rollback
  Diagrams   Core (5)
```

# Chapter 40 — Testing a Non-Deterministic System

---

## 1. Motivation

### 1.1 Cold open

Atlas has fourteen hundred tests and they are green. They have been green for months. The team is
proud of the suite and cites it in onboarding.

A change ships that breaks resume for any run holding more than one in-flight node. Every affected
run re-executes work it had already completed. It takes four days to find, and the fix is two lines.

The postmortem asks the obvious question and gets an uncomfortable answer.

Forty-one of the fourteen hundred tests are wrapped in a retry decorator. Each was added the same
way: a test that called the model port started failing intermittently — three percent, five percent
— somebody investigated, found nothing obviously wrong, and added `@retry(3)` so the build would stop
breaking. Every one of those decisions was made by a competent engineer under deadline pressure, and
every one was locally reasonable.

Nine of the forty-one covered resume behaviour with concurrent nodes. All nine had been failing
intermittently for five weeks, because the bug was intermittent — it depended on which node
completed first. Retried three times, each one passed.

The suite was not green. Forty-one tests had been configured to pass, and nine of them had been
telling the truth the whole time.

### 1.2 In plain language

Testing normally rests on one assumption: run the same thing twice, get the same answer. Everything
about how tests are written, run, and trusted comes from that.

An agent system breaks it in exactly one place — the model. Ask it the same question twice and the
answers differ. Any test whose path goes through a model call is therefore a test that sometimes
fails for no reason at all.

That creates a pressure nobody quite decides to give in to. A test that fails five percent of the
time breaks the build one morning in twenty, so somebody makes it retry. It goes green. It stays
green forever after — including when it starts failing for a real reason, because a real
intermittent bug looks exactly like the flakiness the retry was added for.

A retried test is a deleted test. It is worse than a deleted test, because a deleted test does not
appear in the count.

The way out is to notice that almost none of the system is actually non-deterministic. The loop, the
scheduler, the lease logic, the state machine, the recovery walk — all of that is ordinary software
that behaves the same way every time. The non-determinism enters at one place, through one port, and
if you draw the test boundary there you get a large deterministic system you can test normally, and
a small non-deterministic one that needs a completely different kind of measurement.

### 1.3 Why this chapter exists

Chapter 39 built a pipeline with two gates and assumed both meant something. This chapter is about
what makes the fast one trustworthy, and it turns out to depend on a boundary decision that has to
be made early.

There is also a forward dependency that is easy to miss. Chapter 47 asks an evolution loop to
automatically roll back a harness change when it measures a regression. That is only safe if a
measured regression is real — which requires knowing what the system does when *nothing* changed.
A test suite that cannot distinguish a real intermittent failure from noise is a suite that cannot
establish that baseline, and an automatic rollback built on it will roll back changes that were
fine and keep changes that were not.

`[BP]` The single most useful thing in this chapter is a policy: **retrying a test is forbidden.**
Not discouraged. Everything in §5 exists so that the policy is achievable rather than merely
aspirational, because a prohibition without a mechanism produces a suite full of tests marked
`@skip` instead.

### 1.4 What previous framings got wrong

**"The system is non-deterministic, so tests are unreliable."** One component is non-deterministic.
Levels 2 and 3 built a large amount of ordinary software — leases, joins, ledgers, state machines —
whose behaviour is entirely repeatable, and which is where most bugs live.

**"Mock the model."** Necessary and insufficient. A mock returning a fixed response tests the code
around the port and never tests behaviour under the shapes a real model produces — parallel tool
calls, malformed arguments, truncated output, a sudden change of approach mid-run.

**"Retry the flaky ones."** This is the cold open. A retried test cannot distinguish flakiness from
an intermittent bug, and intermittent bugs are the most expensive kind.

**"Assert the model's output."** Any assertion on generated text is either so loose it passes
anything or so tight it breaks on the next model version. Chapter 28's lattice already established
that model output is judged, not asserted, and the same applies in a test.

**"Statistical tests belong in CI."** A test that runs fifty rollouts to establish a rate belongs in
Chapter 41's evaluation, not in a gate that must finish in minutes. Putting it in CI produces either
a very slow build or a sample too small to mean anything.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Testing an agent runtime is testing a system with a hardware random number generator in it.

Nobody says such a system is untestable. They draw a line around the generator, replace it with a
seeded source for testing, and test everything else normally. The randomness is real, it is
localised, and localising it is what makes the remaining ninety-nine percent of the system ordinary.

That is exactly the right move, and §5.1's port boundary is it.

The break is in what the replacement can be, and it is the difference between an afternoon and a
chapter.

A seeded generator is a **faithful substitute**. It produces values from the same distribution, in
the same format, with the same statistical properties — the only difference is reproducibility.
Code that works against the seeded source works against the real one, because they are
interchangeable in every respect that matters.

A mocked model is not a faithful substitute for a real one. A fixed response has no distribution. It
never returns three tool calls at once, never proposes a plan with a subtle dependency error, never
changes approach halfway, never emits arguments in a form the schema accepts and the tool
misinterprets. Code that works against a mock routinely fails against reality, and the failure is
concentrated in exactly the behaviours the mock could not produce.

So localisation transfers and substitution does not. What fills the gap is **replay** (§5.2):
recorded real trajectories, replayed deterministically. Real distribution, reproducible execution —
which is the property the seeded generator had for free and this domain has to build.

### 2.2 Why the boundary is the port

```
  (1) Testing assumes repeatability. Agent systems appear to
      break it.

  (2) But look at what is actually non-deterministic. The loop,
      scheduler, lease logic, joins, ledger, recovery walk,
      state machines -- all ordinary software, all repeatable.

  (3) The non-determinism enters at ONE place: the model port
      (C13's single door). That was built as a metering and
      budgeting boundary, and it turns out to be the test
      boundary too.

  (4) So draw the line there. Everything below it is tested
      normally, with ordinary assertions, and that is most of
      Levels 2 and 3.

  (5) Above the line, a mock is not a faithful substitute (2.1):
      it produces no distribution and never generates the shapes
      that break things.

  (6) What does: RECORDED trajectories, replayed. Real model
      behaviour, deterministic execution. The recordings already
      exist -- C34's trace store was built for debugging and is
      a test corpus for free.

  (7) And for the genuinely statistical questions -- does this
      change improve the pass rate -- no test answers them. That
      is a measurement with a confidence interval, it belongs in
      C41, and putting it in CI produces either an hours-long
      build or a sample too small to mean anything.

  (8) Therefore three tiers, not one: deterministic tests below
      the port, replay tests across it, and statistical
      evaluation outside CI entirely. A suite that mixes them is
      the cold open, because the statistical ones flake and the
      flakes get retried.
```

Step (8) names the mechanism behind the cold open precisely. The forty-one retried tests were
statistical questions living in a deterministic gate, and the retry decorator was the only tool
available for resolving that mismatch.

### 2.3 Three tiers

| | **Deterministic** | **Replay** | **Statistical** |
|---|---|---|---|
| Tests | The runtime: leases, joins, ledger, state machines, recovery | The runtime against real model behaviour | Whether a change improves outcomes |
| Model | Not involved | Recorded, replayed | Live |
| Repeatable | Yes | Yes | **No** |
| Speed | Milliseconds | Seconds | Hours |
| Where | CI, every commit | CI, every commit | Chapter 41, not CI |
| Assertion | Exact | Exact | An effect size with a floor |
| Retry policy | **Forbidden** | **Forbidden** | Not applicable — it is a sample |
| Share of bugs caught | Most | The expensive ones | Regressions in quality |

The retry row is the chapter's policy. In the first two tiers a retry is always wrong, because both
are deterministic and an intermittent failure is a real bug. In the third the concept does not apply
— you are taking a sample, and a sample is not something that passes or fails.

`[BP]` Enforce it mechanically: fail the build if a retry decorator appears in the first two tiers.
That is a lint rule, and it converts a policy that erodes under deadline pressure into one that does
not.

### 2.4 The mental model to carry

The non-determinism enters at one port. Below it is ordinary software, tested ordinarily, and that
is most of the system. Across it, replay recorded trajectories so that real model behaviour meets
deterministic execution. Beyond it, statistical questions are measurements rather than tests and
they live outside CI. And a retry in either deterministic tier is a deleted test that still counts
itself.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |   TIER 3  STATISTICAL          hours, live model, C41         |
   |   "does this change improve the pass rate?"                  |
   |   NOT IN CI. An effect size with a noise floor, not a test.  |
   +--------------------------------------------------------------+
                              ^
                              | not a gate; a measurement
                              |
   ===============================================================
                    THE MODEL PORT  (C13's single door)
   ===============================================================
                              |
        +---------------------+---------------------+
        |                                           |
        v                                           v
   +---------------------------+     +---------------------------+
   |  TIER 2  REPLAY           |     |  TIER 1  DETERMINISTIC    |
   |                           |     |                           |
   |  recorded trajectories    |     |  fake ports:              |
   |  from C34's trace store   |     |    model  -> scripted     |
   |                           |     |    tool   -> scripted     |
   |  REAL model behaviour,    |     |    clock  -> controlled   |
   |  DETERMINISTIC execution  |     |    store  -> real, in a   |
   |                           |     |              container    |
   |  catches: the shapes a    |     |                           |
   |  mock cannot produce      |     |  catches: leases, joins,  |
   |  (parallel calls, mid-run |     |  ledger, recovery walk,   |
   |  changes of approach,     |     |  state machines, budget   |
   |  malformed-but-valid      |     |  reservation -- most of   |
   |  arguments)               |     |  Levels 2 and 3           |
   |                           |     |                           |
   |  seconds; every commit    |     |  milliseconds; every       |
   |  RETRY FORBIDDEN          |     |  commit. RETRY FORBIDDEN  |
   +---------------------------+     +---------------------------+
        |                                           |
        +---------------------+---------------------+
                              |
                              v
                    +---------------------------+
                    |  GATE 1 (C39 sec 5.1)     |
                    |  minutes, deterministic,  |
                    |  blocks merge             |
                    +---------------------------+

  Figure 40.1 -- Three tiers, one boundary (D1 High-Level
                 Architecture)
```

### 3.1 The port was built for something else and pays twice

Chapter 13 argued for exactly one door to the model, on metering and budgeting grounds: one place to
count tokens, one place to enforce a cap, one place to abort. Chapter 35 used it for
reserve-then-settle.

It is also the test seam, and it is the only reason tier 1 is large. A system with model calls
scattered across a dozen call sites has no boundary to substitute at, and its deterministic tier
shrinks to whatever happens not to touch a model — which in practice is the utility functions.

`[BP]` This is worth noticing as a general property rather than a coincidence. A well-placed port
tends to serve several unrelated purposes, and the number of purposes it ends up serving is a decent
retrospective signal that the boundary was cut in the right place. Chapter 14's effect tag now
answers four questions; Chapter 13's port answers three.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                       TEST MACHINERY                           |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     Fake ports           |  |    Controlled clock       |   |
   |  |                          |  |                           |   |
   |  |  model: scripted turns   |  |  advance() is EXPLICIT    |   |
   |  |  tool:  scripted results |  |                           |   |
   |  |         + failures       |  |  without it, C32's lease  |   |
   |  |                          |  |  expiry cannot be tested  |   |
   |  |  each fake ASSERTS its   |  |  at all -- you would have |   |
   |  |  call sequence, so a     |  |  to wait 30 real seconds  |   |
   |  |  test fails when the     |  |  per assertion (4.2)      |   |
   |  |  runtime calls in the    |  |                           |   |
   |  |  wrong order             |  |  monotonic and wall clock |   |
   |  |                          |  |  are SEPARATE fakes       |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |    Replay harness        |  |    Chaos injector         |   |
   |  |                          |  |                           |   |
   |  |  loads a recorded        |  |  kills workers mid-effect |   |
   |  |  trajectory (C34) and    |  |  expires leases early     |   |
   |  |  serves its turns in     |  |  duplicates events        |   |
   |  |  order                   |  |  pauses a process (C32's  |   |
   |  |                          |  |    SIGSTOP exercise)      |   |
   |  |  DIVERGENCE is the       |  |                           |   |
   |  |  interesting outcome:    |  |  deterministic when       |   |
   |  |  the runtime asked for   |  |  seeded -- the failures    |  |
   |  |  something the recording |  |  are scheduled, not       |   |
   |  |  does not have (5.3)     |  |  random                   |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 40.2 -- Inside the test machinery (D2 Low-Level
                 Architecture)
```

### 4.1 Fakes assert their call sequence

A fake port that returns canned values tests that the runtime handles those values. A fake that also
*asserts the sequence of calls made to it* tests something much more valuable: that the runtime
called the right things in the right order.

That matters here more than in most systems, because Levels 2 and 3 are full of ordering
requirements that are correctness properties rather than style: the completion and the join tick in
one transaction (Chapter 24 §5.2), the effect ledger write inside the completion (Chapter 27 §8),
identity checked *before* the call rather than after (Chapter 21), the gate consulted before
execution (Chapter 30 §4.3).

`[BP]` Every one of those is a test that a sequence-asserting fake can express and a value-returning
mock cannot. They are also, collectively, the properties whose violation produces the silent
failures of Level 3 — so this is the tier that catches the failures with no error signal.

### 4.2 The clock must be controllable or half of Level 3 is untestable

Chapter 32's lease expiry, Chapter 27's sweeper, Chapter 29's stall window, Chapter 30's gate TTL,
Chapter 35's reserve TTL — every one is a time-dependent behaviour with a real-world interval
measured in seconds to minutes.

Testing them against a real clock means either waiting or shortening the intervals for tests, and
shortening intervals changes the thing under test.

`[BP]` Inject the clock as a port, with an explicit `advance()`. Then Chapter 32's whole cold open —
worker pauses, lease expires, second worker claims, first worker returns — is a deterministic test
that runs in a millisecond, and it is the test that most needs writing because the behaviour is
otherwise only observable under production memory pressure.

Two clocks, separately faked: monotonic for durations, wall for timestamps. Chapter 32 §5.4 required
them to be distinguished in production, and a test that conflates them will not catch a production
bug that depends on the distinction.

---

## 5. The Port Boundary, Replay, and the Retry Prohibition

### 5.1 What tier 1 covers, which is more than expected

The instinct is that a system built around a model is mostly untestable. Enumerating what is
actually below the port corrects it.

| Behaviour | Chapter | Deterministic? |
|---|---|---|
| Lease acquisition, renewal, expiry, fencing | C17, C32 | Yes |
| Ready-set resolution, join counting, skip propagation | C24 | Yes |
| Activity identity and duplicate detection | C21 | Yes |
| Outbox write, relay claim, poison handling | C22 | Yes |
| Admission, work classes, per-tenant fairness | C23 | Yes |
| Effect ledger, compensation ordering, dead letters | C27 | Yes |
| Verdict combination, the downgrade-only rule | C28 | Yes |
| Novelty hashing and stall detection | C29 | Yes |
| Gate policy, argument-hash scoping, park and resume | C30 | Yes |
| Capability scoping, provenance lattice, egress | C31 | Yes |
| Budget reservation, settlement, sweeping | C35 | Yes |
| Config resolution and freezing | C38 | Yes |
| **Whether the model chooses a good tool** | C13 | **No** |
| **Whether a plan is a good decomposition** | C26 | **No** |

Two rows out of fourteen. The non-deterministic part is real and it is small, and every mechanism
this handbook spent Levels 2 and 3 building is in the top group.

`[BP]` That is worth saying to a team that believes its system is untestable, because the belief
leads directly to the cold open: if testing is hopeless, a retry decorator is a reasonable response
to a failing test.

```
                                                            LAYER VIEW

   ABOVE THE PORT -- non-deterministic, 2 of 14
   +--------------------------------------------------------------+
   |  does the model choose a good tool?              C13          |
   |  is this a good decomposition?                   C26          |
   |                                                               |
   |  no test at any tier answers these. They are MEASUREMENTS,    |
   |  with confidence intervals, and they live in C41.             |
   +--------------------------------------------------------------+

   =============== THE MODEL PORT (C13's single door) =============

   BELOW THE PORT -- deterministic, 12 of 14
   +--------------------------------------------------------------+
   |  leases, renewal, expiry, fencing            C17, C32         |
   |  ready sets, join counting, skip propagation      C24         |
   |  activity identity, duplicate detection           C21         |
   |  outbox write, relay claim, poison handling       C22         |
   |  admission, work classes, tenant fairness         C23         |
   |  effect ledger, compensation order, dead letters  C27         |
   |  verdict combination, downgrade-only              C28         |
   |  novelty hashing, stall detection                 C29         |
   |  gate policy, arg-hash scoping, park and resume   C30         |
   |  capability scoping, provenance, egress           C31         |
   |  budget reserve, settle, sweep                    C35         |
   |  config resolution and freezing                   C38         |
   |                                                               |
   |  ordinary software. ordinary assertions. milliseconds.        |
   |  AND it is where the silent failures of Level 3 live, which   |
   |  is why the sequence-asserting fakes of 4.1 matter more here  |
   |  than value-returning mocks ever could.                       |
   +--------------------------------------------------------------+

  Figure 40.3 -- What is actually non-deterministic (D7 Data Flow)
```

### 5.2 Replay: real behaviour, deterministic execution

Tier 2 is the tier most systems lack and it is nearly free once Chapter 34 exists.

A recorded trajectory is a sequence of model turns captured from a real run: the exact responses,
in order, including the awkward ones. Replaying it means serving those turns to the runtime in place
of a live model. Real distribution, real shapes, deterministic execution.

What it catches that a mock does not:

- **Parallel tool calls.** A model returning three at once exercises Chapter 24's fan-out and
  Chapter 30's per-call gating in a way a single-call mock never does.
- **Mid-run changes of approach.** The model abandons a line of attack at step 12, which exercises
  Chapter 26's repair path with a real trigger.
- **Arguments that are schema-valid and semantically wrong.** The cold open of Chapter 34 — a regex
  where a glob was expected — passes every validator and produces an empty result.
- **Malformed output that is nearly valid.** Truncation, a trailing comma, a tool name that differs
  by case.

`[BP]` Build the corpus from Chapter 34 §5.5's always-keep categories: every failure, every stall,
every override, every dead letter. Those are already retained, they are exactly the interesting
shapes, and turning them into replay fixtures is a script rather than a project.

### 5.3 Divergence is the interesting outcome

Replay has a failure mode with no analogue in ordinary testing, and it is the most informative thing
the tier produces.

The runtime asks for something the recording does not contain — a fourth turn where the recording
has three, or a call at a point where the recording moved on. That means the runtime's behaviour has
changed relative to when the recording was made.

Sometimes that is the bug. Sometimes it is a legitimate improvement and the recording is stale.
Distinguishing them requires a human, which is fine, because divergence is rare.

`[BP]` Report divergence as a distinct outcome from failure — `PASS`, `FAIL`, `DIVERGED` — and treat
a rising divergence rate as a signal that the corpus needs refreshing. A tier that reports divergence
as failure will be silenced within a quarter, because most divergences are the runtime legitimately
improving.

### 5.4 The retry prohibition, and what makes it achievable

The policy: **no retry decorator in tier 1 or tier 2.** A lint rule, enforced in the pipeline.

A prohibition alone produces `@skip` instead of `@retry`, which is the same outcome with a clearer
conscience. What makes it achievable is that both tiers are genuinely deterministic — so an
intermittent failure has a cause, and the cause is findable.

`[BP]` The three causes, in order of frequency:

- **Shared state between tests.** A store not reset, a module-level cache, a fake carrying its
  sequence into the next test. This is the majority and it is ordinary test hygiene.
- **Real time leaking in.** A `sleep`, a timeout against a wall clock, an ordering dependent on how
  fast the machine is. §4.2's controlled clock removes it.
- **A real intermittent bug.** The valuable case, and the one the cold open's nine tests were
  reporting for five weeks.

The order matters operationally. An engineer facing a flaky test who has been told the first two are
usual will look for them, and finding one costs an hour. The retry decorator costs five minutes,
which is why it wins whenever the policy is a suggestion.

### 5.5 What a unit test means when the unit calls a model

It does not. The unit under test ends at the port.

That sounds like an evasion and it is a precise statement of scope. `PlanRepairer.repair()` can be
unit-tested exhaustively — given this prior plan, this executed prefix, and this failure record, does
it produce a graph whose prefix carries by identity and whose tail is re-derived? All of that is
deterministic. What cannot be unit-tested is whether the model's re-derivation is *good*, and no
test at any tier answers that. It is Chapter 41's measurement.

`[BP]` The practical rule: **assert on structure, never on generated content.** A test may assert
that a plan is acyclic, that its nodes carry identity hashes, that its contracts are checkable, that
its declared scopes are narrow. It may not assert that step 3 is "edit the file". The first set is
stable across model versions; the second breaks on the next one and gets a retry decorator.

### 5.6 Chaos as a scheduled test, not a game day

Chapter 32 §2.3 recommended a `SIGSTOP` exercise, and Chapter 34 §5.3 recommended synthetic probes
that deliberately trip safety controls. Both belong here as tier-1 tests rather than as occasional
exercises.

The failures worth injecting are exactly the ones this handbook says produce no signal:

| Injection | Asserts | Chapter |
|---|---|---|
| Kill a worker between effect and record | The identity check prevents a duplicate | C21, C32 |
| Expire a lease mid-effect | A fence token or an identity check stops the second actor | C32 §5.3 |
| Deliver an event twice | The relay's claim makes it idempotent | C22 |
| Fail a compensation to exhaustion | A dead letter is raised, with an owner | C27 §5.2 |
| Trip the egress policy | It fires, and it is wired at all | C31 §5.5 |
| Present an expired gate decision | The run fails rather than proceeding | C30 §5.6 |

`[BP]` All six are deterministic when the injector is seeded, they run in milliseconds, and each
asserts a property whose violation is otherwise invisible until production. This is the highest-value
block of tests in the chapter and it is usually absent, because chaos testing is culturally
associated with occasional exercises rather than with CI.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  The cold open's bug, caught by a tier-1 test that exists.

  t   test                          fake ports            assertion
  --  ----------------------------  --------------------  -----------
  0   arrange: a plan graph with
      5 nodes, 3 of them ready
      concurrently (C24)
  1   worker A claims n2, n3         clock at T=0
  2   worker B claims n4             lease TTL 30 s
  3   A completes n2                 model fake: turn 1
                                     tool fake: asserts
                                     it was called once
                                     with these args
  4   clock.advance(10 s)            EXPLICIT -- no sleep
  5   A completes n3
  6   clock.advance(25 s)            A's lease now expired
                                     without renewal
  7   sweeper runs                                        n2, n3 remain
                                                          SUCCEEDED;
                                                          only CLAIMED
                                                          nodes return
                                                          to pending
  8   worker C resumes the run       replay of the
                                     recorded turns
  9   C resolves the ready set                            expects {n5}
                                                          NOT {n2,n3,n5}
 10   THE BUG: resume recomputed
      readiness from the plan's
      step index rather than from
      node status, so n2 and n3
      appear ready again
 11                                                       FAIL, on the
                                                          first run,
                                                          deterministically

  ELAPSED: 2 milliseconds. The clock advanced 35 seconds without
  anything waiting.

  WHY THE COLD OPEN'S SUITE MISSED IT: its resume tests used a
  single in-flight node, because a mock returning one tool call
  cannot produce two. The multi-node case existed only in the nine
  tests that went through a live model -- which flaked, and were
  retried, and passed.

  FAILURE BRANCH -- the same test, written against a real clock:

    t=4  time.sleep(10)
    t=6  time.sleep(25)
    -- the test now takes 35 seconds. Someone shortens the lease
       TTL to 3 seconds "for tests", which changes the interval
       under test, and the version that runs in CI no longer
       exercises the production timing at all.

  Figure 40.4 -- A deterministic test for a concurrency bug (D4
                 Sequence)
```

The failure branch is the ordinary path a team takes without a controlled clock, and its cost is
subtle: the test still exists and still passes, and it is now testing a configuration that is not
deployed.

---

## 7. State Management

```
                                                            STATE VIEW

   TEST OUTCOME

      {{ pass }}      (terminal)

      {{ fail }}
          |
          | tier 1 or 2: DETERMINISTIC, so there is a cause
          v
      one of three (5.4):
          shared state | real time leaking in | a real bug

      {{ diverged }}   replay only (5.3)
          |            the runtime asked for something the
          |            recording does not have
          |
          +---- runtime regressed -----> investigate as {{ fail }}
          |
          +---- runtime improved ------> refresh the recording

      ILLEGAL: {{ fail }} -> {{ pass }} by retry, in tier 1 or 2.
      Both tiers are deterministic; an intermittent failure has a
      cause and the cause is findable. This is enforced by a lint
      rule, not by a policy document, because the retry costs five
      minutes and finding the cause costs an hour (5.4).

      ILLEGAL: {{ diverged }} reported as {{ fail }}. Most
      divergences are the runtime legitimately improving, and a
      tier that cries wolf on those is silenced within a quarter.

      ILLEGAL: a statistical question in tier 1 or 2 at all. It
      will flake, it will be retried, and the retry will hide a
      real bug. That is the cold open's mechanism exactly (2.2
      step 8).

  Figure 40.5 -- Test outcomes, and the transition that is banned
                 (D6 State Diagram)
```

### 7.1 Fixtures are versioned with the harness

A replay recording captures a model's behaviour under a specific harness and a specific model
version — Chapter 38's triple. When either changes, the recording describes a system that no longer
exists, and divergence rates climb for reasons that have nothing to do with the code under test.

`[BP]` Store the triple on every fixture and refresh the corpus as part of the migration ladder
(Chapter 38 §5.3). A model migration that does not refresh the replay corpus will produce a wave of
divergences on the first day, which is confusing exactly when attention is most needed elsewhere.

### 7.2 Test state is reset, not reused

The first and most common cause of flakiness in §5.4 is shared state, and it is worth designing
against rather than debugging repeatedly. `[BP]` Every test gets a fresh store — a container, a
transaction rolled back, a temporary schema — and every fake is constructed per test rather than
module-level. The cost is a few milliseconds per test; the benefit is that the retry prohibition
becomes practical rather than aspirational.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class Clock(Protocol):
    """A port, injected. Two clocks, separately faked (4.2)."""

    def monotonic(self) -> float: ...
    def wall(self) -> str: ...


class FakeClock(Clock):
    def advance(self, seconds: float) -> None:
        """EXPLICIT time movement.

        Without this, C32's lease expiry, C27's sweeper, C29's stall
        window, C30's gate TTL, and C35's reserve TTL are all
        untestable except by waiting -- or by shortening the
        intervals, which changes the thing under test (6, failure
        branch).
        """


class ScriptedPort(Protocol):
    """A fake that asserts its call sequence, not merely its
    returns."""

    def expect(self, calls: Sequence["ExpectedCall"]) -> None:
        """Declare the calls this port must receive, in order.

        Ordering is a correctness property throughout Levels 2 and 3
        -- identity checked BEFORE the call, the gate consulted
        BEFORE execution, the ledger written INSIDE the completion.
        A value-returning mock cannot express any of them (4.1).
        """


class ReplayHarness(Protocol):

    def load(self, fixture_id: str) -> "Recording":
        """A real trajectory from C34's trace store: real model
        behaviour, deterministic execution. Built from the
        always-keep categories, which are already retained and are
        exactly the interesting shapes (5.2).
        """

    def serve(self, recording: "Recording") -> "ReplayOutcome":
        """PASS | FAIL | DIVERGED.

        DIVERGED is a distinct outcome, never folded into FAIL: most
        divergences are the runtime legitimately improving, and a
        tier that reports those as failures is silenced within a
        quarter (5.3).
        """
```

`ReplayOutcome` having three values rather than two is the signature carrying §5.3. A boolean forces
divergence into one of the existing buckets, and whichever bucket it lands in makes the tier either
noisy or blind.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class Tier(int, Enum):
    DETERMINISTIC = 1
    REPLAY = 2
    STATISTICAL = 3        # not in CI; C41 owns it


class ReplayOutcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    DIVERGED = "diverged"  # distinct, always (5.3)


@dataclass(frozen=True)
class Recording:
    fixture_id: str
    triple: "VersionTriple"      # C38: fixtures age with the harness
    turns: tuple[dict, ...]      # model responses, in order
    source_run_id: str           # provenance back to the real run
    category: str                # "failure" | "stall" | "override" ...


@dataclass(frozen=True)
class ExpectedCall:
    port: str                    # "tool" | "model" | "store"
    method: str
    args_matcher: dict           # structural, never on generated text
    must_precede: tuple[str, ...]   # ordering assertions (4.1)
```

`ExpectedCall.args_matcher` being structural is §5.5's rule in the schema. A matcher that can only
express structure cannot be used to assert on generated content, which is the assertion that breaks
on the next model version and then acquires a retry decorator.

`Recording.triple` is what makes §7.1 enforceable: a fixture whose triple no longer matches the
deployed one can be flagged rather than silently producing divergences.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Trace store (C34) | Replay corpus | Scheduled export | Always-keep trajectories as fixtures |
| Fixtures | Replay harness | Load per test | Recorded turns plus the triple |
| Chaos injector | Runtime | Seeded schedule | Worker kills, lease expiries, duplicate events |
| Fake clock | Runtime | Port injection | Explicit time |
| Tiers 1 and 2 | Gate 1 (C39) | Blocking | Deterministic pass or fail |
| Tier 3 | Chapter 41 | Not a gate | A measurement |
| Lint rule | CI | Blocking | Rejection of retry decorators in tiers 1 and 2 |

The first row is the one that makes tier 2 cheap. `[BP]` The export is a scheduled job over data
Chapter 34 already retains, and it keeps the corpus current without anyone curating it — which
matters, because a hand-curated fixture set ages into a museum of last year's failures.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Flaky test retried | The suite stays green while a bug ships | Lint rule forbidding retries in tiers 1 and 2 (§5.4). The cold open |
| Statistical question in CI | It flakes, then it is retried | Move it to Chapter 41; it is a measurement, not a test |
| Mock instead of replay | Bugs concentrated in shapes the mock cannot produce | Replay from the trace store (§5.2) |
| Real clock in tests | Slow tests, then shortened intervals | Inject the clock; `advance()` explicitly (§4.2) |
| Shortened lease TTL "for tests" | Tests pass against a configuration not deployed | Controlled clock removes the reason (§6) |
| Divergence reported as failure | The tier is silenced within a quarter | A distinct third outcome (§5.3) |
| Fixtures stale after a model change | Divergence wave on migration day | Version fixtures with the triple; refresh in the ladder (§7.1) |
| Assertions on generated content | Breakage on every model version, then a retry | Assert structure only (§5.5) |
| Shared state between tests | The commonest flake, misdiagnosed as non-determinism | Fresh store and fresh fakes per test (§7.2) |
| Chaos treated as an occasional exercise | Silent-failure properties untested | Seeded injection in CI (§5.6) |

The second row is the mechanism behind the first and is worth separating. The cold open's forty-one
tests were not badly written; they were statistical questions placed in a deterministic gate, and
the retry decorator was the only tool available for reconciling that. Removing the retries without
moving those tests to tier 3 would have produced a permanently red build.

---

## 12. Scalability

**Tier 1 must stay in milliseconds per test**, which means fresh state per test has to be cheap.
`[BP]` A transaction rolled back beats a container per test by two orders of magnitude, and a schema
per worker beats both for tests that need real DDL.

**Tier 2 costs seconds per fixture** and scales with corpus size. `[BP]` Cap the corpus by
always-keep category and sample within it — a few hundred fixtures covering the interesting shapes
beats thousands covering the same shapes repeatedly.

**Chaos injection is free when seeded**, because it is a scheduling decision rather than a wait.

**Tier 3 is Chapter 41's cost** and is out of CI entirely, which is what keeps gate 1 in minutes
(Chapter 39 §5.2).

**The corpus export grows with retention** and is bounded by Chapter 37 §5.4's classification split:
fixtures need the structural signal and the model turns, and can be built from the redacted
partition where the verbatim content has aged out.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Retry decorators in tiers 1 and 2.** Must be zero, enforced by lint. The cold open's forty-one
  would have been visible from day one.
- **Divergence rate in tier 2.** Rising means the corpus is stale, usually after a harness or model
  change.
- **Tier 1 duration, p95.** The moment it leaves the minutes budget, engineers route around gate 1.
- **Fixture corpus age, oldest.** A corpus of last year's failures tests last year's system.
- **Chaos assertions passing.** Six properties (§5.6) that are otherwise invisible until production.

### 13.2 The review question

For any new test: **which tier is this, and is it deterministic in that tier?**

A test that cannot answer the second half is a statistical question in the wrong place, and it will
acquire a retry decorator within two months. Catching it at review costs nothing; catching it after
the retry costs the four days in the cold open.

### 13.3 Teaching this to a new engineer

Show them the suite: fourteen hundred tests, green, and a bug that shipped. Ask how that is
possible.

Then show them the retry decorators and the nine tests that had been failing for five weeks. The
sentence that lands is *a retried test is a deleted test that still counts itself* — and once
somebody has felt that, the port boundary and the three tiers follow as the obvious way to make the
prohibition survivable rather than as process.

---

## 14. Relation to AHE

`[AHE]` The source's evolution loop measures a harness variant by running benchmark tasks, which is
tier 3 in this chapter's terms. It has no equivalent of tiers 1 and 2 because the harness under
evolution is small and the runtime beneath it is fixed.

`[INF]` For a production system that is not true, and the gap matters for Chapter 47. **Automatic
rollback requires knowing that a measured regression is real**, which requires a baseline of what
the system does when nothing changed. Tiers 1 and 2 establish that the runtime itself is stable, so
a measured change can be attributed to the harness edit rather than to the runtime being flaky. A
loop attached to a suite with forty-one retried tests will attribute intermittent runtime failures
to whatever harness edit happened to be under test.

`[INF]` There is also a corpus relationship worth designing for. Chapter 47's attribution wants to
know which past failures a harness edit was meant to fix, and §5.2's replay fixtures — built from
always-keep failures with their provenance recorded — are exactly that set. `[BP]` Keeping
`Recording.source_run_id` makes a fixture traceable back to the run that motivated it, which turns
the replay corpus into an evidence base rather than only a test suite.

---

## 15. Industry Perspective

**`[BP]` Localising non-determinism behind a port is standard practice** wherever randomness,
clocks, or external services appear, and it transfers unchanged. The observation specific to this domain is
how *much* of the system ends up below the line — §5.1's fourteen rows, twelve of them deterministic.

**`[BP]` Retry-on-flake is near-universal and near-universally regretted.** The literature on flaky
tests is clear that retries hide real intermittent bugs, and the practice persists because the retry
takes five minutes and the investigation takes an hour. The only durable fix is mechanical
enforcement plus a place for the genuinely statistical tests to live.

**`[BP]` Record-and-replay is well established for HTTP interactions** and is under-applied to model
calls, despite the trace store usually already existing. The gap appears to be that traces are built
for debugging and nobody thinks of them as fixtures.

**`[INF]` Controlled clocks are the single highest-return investment in testing a durable system**
and are frequently retrofitted painfully. Every time-dependent behaviour in Levels 3 and 4 —
leases, sweepers, stall windows, gate TTLs, reserve TTLs — is untestable without one.

**`[FUT]` Automatic fixture generation from divergence is unexplored.** When a replay diverges
because the runtime improved, the correct response is a refreshed recording — which the system could
capture automatically from the next live run of the same task. Nothing appears to do this, and it
would keep a replay corpus current with no curation at all.

---

## 16. Key Takeaways

1. **A retried test is a deleted test that still counts itself.** Forty-one retries, nine of them
   reporting a real bug for five weeks, in a suite everyone trusted.
2. **The non-determinism enters at one port.** Below it is most of Levels 2 and 3 — leases, joins,
   ledgers, gates, budgets — all ordinary deterministic software.
3. **A mock is not a faithful substitute.** It produces no distribution and never generates the
   shapes that break things: parallel calls, mid-run changes of approach, schema-valid nonsense.
4. **Replay gives real behaviour with deterministic execution**, and the corpus already exists in
   the trace store's always-keep categories.
5. **Divergence is a third outcome.** Most divergences are the runtime legitimately improving, and a
   tier that reports them as failures gets silenced.
6. **Control the clock or half of Level 3 is untestable** — except by waiting, or by shortening the
   intervals, which tests a configuration that is not deployed.
7. **Statistical questions are measurements, not tests.** Put one in CI and it will flake, and the
   flake will be retried, and the retry will hide something real.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Port boundary** | The model port as the test seam, below which the system is ordinary deterministic software. | `[INF]` | Ch 41 |
| **Deterministic tier** | Tests of the runtime with fake ports and a controlled clock, covering most of Levels 2 and 3. | `[BP]` | Ch 41 |
| **Replay tier** | Recorded real trajectories served to the runtime, giving real model behaviour with reproducible execution. | `[INF]` | Ch 41, Ch 47 |
| **Divergence** | The runtime asking for something a recording does not contain, reported as a distinct outcome because most divergences are improvements. | `[INF]` | Ch 47 |
| **Sequence-asserting fake** | A fake port that checks the order of calls made to it, which is how ordering-as-correctness properties become testable. | `[BP]` | Ch 41 |
| **Controlled clock** | An injected clock with explicit advancement, without which every lease, sweeper, and TTL behaviour is untestable. | `[DAR]` | Ch 41 |
| **Retry prohibition** | A lint-enforced ban on retry decorators in the deterministic tiers, achievable only because those tiers really are deterministic. | `[BP]` | Ch 41 |
| **Structural assertion** | Asserting on the shape of what a model produced rather than its content, so a test survives the next model version. | `[BP]` | Ch 41 |
| **Seeded chaos** | Scheduled injection of worker kills, lease expiries, and duplicate events, asserting the properties whose violation is otherwise invisible. | `[BP]` | Ch 41 |
| **Fixture triple** | The code, harness, and model version a recording was captured under, which is what makes fixture staleness detectable. | `[INF]` | Ch 47 |

---

**Next:** Chapter 41 — *Evaluation Infrastructure.* The last chapter of Level 4, and the gate into
Level 5. It opens with a team that shipped one change on +4 points, reverted the next on -2, and
then discovered that running the unchanged harness twice produced a 5-point spread — which means
every decision they had made for three months was a coin flip, and it raises the question Level 5
has to answer before it starts.
