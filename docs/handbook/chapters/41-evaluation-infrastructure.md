```
  Level 4 · Chapter 41
  EVALUATION INFRASTRUCTURE
  Requires   C28 Grading, C34 Observability, C36 Reliability and SLOs,
             C38 Deployment and Versioning, C39 GitOps and CI/CD,
             C40 Testing
  Unlocks    all of Level 5
  Diagrams   Core (5)
```

# Chapter 41 — Evaluation Infrastructure

---

## 1. Motivation

### 1.1 Cold open

The Atlas team has a benchmark: sixty tasks drawn from real issues, run end to end, scored on
whether the pull request passes review. It takes forty minutes. They use it for every harness
change.

In March a change to the context assembler measures **+4 points**. It ships.

In April a change to the retry classifier measures **-2 points**. It is reverted, and the engineer
who wrote it spends a week on a different approach.

In May somebody adds a caching layer and, while waiting for it, runs the benchmark twice against the
*unchanged* harness. The two runs come back at 71 and 76.

A five-point spread with nothing changed at all.

They go back through the change log. Every decision made against that benchmark since January had an
effect size smaller than the spread. The +4 was inside the noise. The -2 was inside the noise. Three
months of shipping, reverting, and re-approaching had been driven by a measurement whose resolution
was worse than every effect it was used to detect.

Nobody had ever run the benchmark twice on the same harness, because there had never been a reason
to.

### 1.2 In plain language

Once a system stops being deterministic, "did this change help?" stops having a yes-or-no answer and
becomes a measurement — and measurements have error bars.

Run the same harness on the same tasks twice and you get different scores, because the model makes
different choices each time. That variation is not a defect to be fixed. It is a property of the
thing being measured, and it sets a floor on what you can detect. If two identical runs can differ
by five points, then a change that moves the score by three points is invisible, no matter how
carefully you measured it.

Almost nobody measures that floor, because doing so means running the benchmark repeatedly on a
harness you have not changed — which feels like paying for nothing. The cold open is what happens
when you skip it: three months of confident decisions about numbers that were noise.

This is the last chapter before the book turns to systems that change themselves, and the connection
is direct. An evolution loop is something that makes this exact judgment — did that edit help? —
thousands of times, automatically, with no human looking at any individual number. If a careful team
cannot tell signal from noise on one change, a loop making a thousand of them will climb whatever
gradient the noise happens to have, confidently and fast.

That is why this chapter is the gate.

### 1.3 Why this chapter exists

Chapter 39 built a pipeline whose promotion gate returns per-slice effect sizes with noise floors,
and did not say where the floor comes from. Chapter 40 established that statistical questions are
measurements rather than tests and moved them out of CI, without saying where they go. Chapter 38's
migration ladder had an evaluation step that everything else depended on. Chapter 36 published
quality as a tracked statistic and needed something to track it with.

Four chapters deferred to this one, and the thing they all deferred is the same: **a number, and how
much to trust it.**

`[AHE App. A]` supplies the conventions — rollouts per task, `pass@1` averaged rather than taken
once, tokens per trial, success per million tokens. `[DAR §9.3]` supplies the golden-set regression
harness. This chapter's job is to put them together into infrastructure a team runs continuously,
and then to state plainly what Level 5 needs from it that a human-driven process does not.

### 1.4 What previous framings got wrong

**"The benchmark said +4."** A benchmark says +4 ± something, and without the second term the first
is not a result. The cold open's team was not careless; they had a number and no reason to doubt it.

**"Run more tasks."** More tasks reduces the noise floor, and only as the square root. Going from
sixty tasks to a hundred and twenty narrows the floor by about thirty percent, which is real and is
usually not enough on its own — rollouts per task (§5.2) often buy more.

**"Use a public benchmark."** Public benchmarks are useful for comparing systems and poor at
detecting your regressions, because their task distribution is not your traffic. The cold open's
dependency-upgrade regression in Chapter 39 appears in no public benchmark.

**"Score is the metric."** Score alone rewards spending more (Chapter 35 §14). The headline is
success per unit cost, and a harness that gains two points for triple the tokens has not improved
anything an operator can afford.

**"The evaluation is the gate."** It is one of two. The fast deterministic regression harness
(Chapter 39 §5.1) catches different things and catches them in minutes, and a team with only the
slow one has an unusable inner loop.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Evaluating a harness change is measuring an effect in a clinical trial.

The vocabulary transfers almost completely, and it is worth borrowing deliberately rather than
reinventing it under other names. You have a **population** of tasks, an **intervention** (the
harness change), an **outcome measure** (the verdict), **variance** between subjects, and a
**minimum detectable effect** set by your sample size. You worry about **selection bias** in the
population, about **multiple comparisons** when you test many things, and about the temptation to
peek at partial results and stop when they look good.

Every one of those has a direct counterpart here, and teams that have not borrowed the vocabulary
tend to rediscover each hazard the expensive way.

The break is in what a subject costs, and it changes which techniques are available.

A clinical trial's subjects are scarce, slow, and ethically constrained. You cannot run the same
patient through the trial twice. Enormous statistical machinery exists precisely because you get one
observation per subject and cannot repeat it.

Here a subject is a task, and you can run it as many times as you can afford. **Repeated measurement
on the same subject is available**, which is a large advantage — it converts a between-subject
comparison into a paired one, and Chapter 39 §5.3's shadow evaluation exploits exactly that.

The cost is money and wall clock rather than ethics, which means the constraint is a budget rather
than a hard limit. That is better, and it is also why the discipline erodes: nothing stops a team
running one rollout per task except that it is cheaper, and the cold open is the result.

### 2.2 Why the noise floor comes first

```
  (1) Question: did this harness change help?

  (2) Measure it: run a benchmark before and after, compare.

  (3) The two numbers differ. But two runs of the UNCHANGED
      harness also differ, because the model makes different
      choices each time.

  (4) So the comparison is meaningless until you know how much
      it differs WITHOUT a change. That quantity is the noise
      floor, and it is a property of the benchmark, not of the
      change.

  (5) Measuring it costs k runs of an unchanged harness --
      which feels like paying for nothing, which is why almost
      nobody does it. The cold open is the consequence.

  (6) Once known, the floor sets the MINIMUM DETECTABLE EFFECT.
      Any change smaller than it is a coin flip, and shipping on
      one is indistinguishable from shipping at random.

  (7) The floor can be narrowed: more tasks (as the square
      root), more rollouts per task, or pairing the comparison
      so that task difficulty cancels (2.1). Pairing is usually
      the cheapest large win.

  (8) And this is what Level 5 needs. An evolution loop makes
      this judgment thousands of times with nobody reading any
      individual number. Below the floor, its gradient is the
      noise's gradient -- and it will follow it, confidently,
      because that is what optimisation does.
```

Step (8) is the reason this chapter is positioned as the gate rather than as one more production
concern.

### 2.3 Two gates, restated with their statistics

Chapter 39 §5.1 established the split. Here is what each one is measuring.

| | **Regression harness** | **Benchmark** |
|---|---|---|
| Source | `[DAR §9.3]` golden set | `[AHE App. A]` conventions |
| Question | Did anything break outright? | Did the distribution of outcomes move? |
| Answer | Deterministic pass or fail | An effect size with a floor |
| Noise | None — that is the design | The subject of this chapter |
| Runs | Every commit, minutes | Before promotion, hours |
| Cost | Negligible | Real (§12) |
| Fails by | Being incomplete | Being too small to detect anything |

The bottom row names the characteristic failure of each. A regression harness fails by not
containing the case that broke; a benchmark fails by having a noise floor wider than the effects it
is used to judge. `[BP]` They need different maintenance: the golden set grows by one case per
incident, and the benchmark grows by rollouts and by task coverage.

### 2.4 The mental model to carry

Measure the noise floor before measuring anything else, and re-measure it whenever the model changes.
Report every result as an effect size against that floor, per slice. Pair the comparison where you
can, because pairing buys more than sample size does. And denominate the headline in success per unit
cost rather than in score, because score alone rewards spending more.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |                      TASK CORPUS                             |
   |                                                              |
   |   slices by task type; each task has a deterministic          |
   |   contract (C26) and a golden verdict where one exists        |
   |                                                              |
   |   drawn from real traffic (C34's trace store), consented      |
   |   or synthesised (C37 sec 5.5)                                |
   +--------------------------------------------------------------+
                            |
                            | (1) k rollouts per task
                            v
   +--------------------------------------------------------------+
   |                     EVALUATION RUNNER                        |
   |                                                              |
   |   candidate triple (C38) vs incumbent triple                 |
   |   PAIRED on identical tasks where possible (2.1)             |
   +--------------------------------------------------------------+
                            |
                            | (2) verdicts, per run
                            v
   +--------------------------------------------------------------+
   |                       GRADER (C28)                           |
   |   deterministic floor + downgrade-only judge                 |
   |   -- the evaluation is only as honest as this is             |
   +--------------------------------------------------------------+
                            |
                            v
   +---------------------------+     +---------------------------+
   |    NOISE FLOOR ESTIMATOR  |     |    EFFECT REPORTER        |
   |                           |     |                           |
   |  k runs of the UNCHANGED  |---->|  per slice:               |
   |  harness                  | (3) |    delta                  |
   |                           |     |    floor                  |
   |  re-run on every MODEL    |     |    outside_floor          |
   |  change (C38 sec 5.1)     |     |    cost per success (C35) |
   +---------------------------+     +---------------------------+
                                                 |
                    +----------------------------+-------------+
                    |                            |             |
                    v                            v             v
          +------------------+      +------------------+  +----------+
          | C39 promotion    |      | C36 published    |  | LEVEL 5  |
          | gate             |      | quality trend    |  |          |
          +------------------+      +------------------+  +----------+

  Figure 41.1 -- Evaluation, with the floor as a first-class input
                 (D1 High-Level Architecture)

  (1) k rollouts, not one: `pass@1` averaged over k (5.2)
  (2) the grader's own accuracy bounds everything downstream; a
      benchmark cannot be more honest than its verdicts (C28)
  (3) the floor is an INPUT to every comparison, not a footnote
```

### 3.1 The evaluation is bounded by the grader

Wire (2) deserves more than a caption. Every number this chapter produces is a count of verdicts, so
a grader with a five percent false-pass rate produces a benchmark that cannot distinguish changes
smaller than that, regardless of how many rollouts are run.

`[BP]` Chapter 36's honesty auditor measures exactly this, and its output belongs in the evaluation
report rather than only on the reliability dashboard. A benchmark result reported without the
grader's current disagreement rate is a measurement without one of its two error terms.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                    EVALUATION MACHINERY                        |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Noise floor estimator  |  |    Rollout scheduler      |   |
   |  |                          |  |                           |   |
   |  |  k runs, unchanged       |  |  k rollouts x n tasks     |   |
   |  |  harness, same corpus    |  |                           |   |
   |  |                          |  |  its own work class (C23),|   |
   |  |  reports spread PER      |  |  reserved but preemptible |   |
   |  |  SLICE -- small slices   |  |  so it neither starves    |   |
   |  |  have wider floors, and  |  |  nor starves production   |   |
   |  |  that is where teams     |  |  (C33 sec 14)             |   |
   |  |  over-read results       |  |                           |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |    Effect reporter       |  |   Corpus manager          |   |
   |  |                          |  |                           |   |
   |  |  delta, floor, and       |  |  slices, coverage, and    |   |
   |  |  outside_floor per slice |  |  provenance per task      |   |
   |  |                          |  |                           |   |
   |  |  never a bare pass/fail; |  |  tasks retire, never      |   |
   |  |  a boolean invites a     |  |  silently change (5.5)    |   |
   |  |  threshold and a tuned   |  |                           |   |
   |  |  threshold on a noisy    |  |  drift detector: has the  |   |
   |  |  measurement is the      |  |  corpus stopped resembling|   |
   |  |  cold open               |  |  traffic? (5.6)           |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 41.2 -- Inside the evaluation machinery (D2 Low-Level
                 Architecture)
```

### 4.1 Floors are per slice, and small slices have wide ones

A benchmark of sixty tasks split into six slices has ten tasks per slice. The overall floor might be
three points; a ten-task slice's floor is far wider — plausibly fifteen.

That asymmetry is where over-reading happens, and it happens in a predictable direction: a team
looks at the per-slice breakdown, sees "dependency upgrades: -9", and treats it as a finding when it
is well inside that slice's floor.

`[BP]` Report the floor next to every number, at every granularity, and refuse to display a slice
delta without one. Chapter 39's `SliceEffect` structure carries `noise_floor_pp` for exactly this
reason — the floor and the effect travel together so a consumer cannot read one without the other.

### 4.2 Evaluation gets its own work class

`[BP]` A benchmark run is hundreds of tasks times k rollouts against the same model semaphore that
production uses, which Chapter 33 §12 identified as the surface that cannot be bought. Left in the
default class it either starves or starves production.

Chapter 23's machinery already handles this: a reserved-but-preemptible class, sized so a promotion
gate completes in hours rather than days, yielding to production during a burst. This is also the
arrangement Level 5 needs, at a much higher volume, so building it here is not premature.

---

## 5. Noise, Rollouts, Corpus, and What Level 5 Requires

### 5.1 Measure the floor, and re-measure it

The procedure is embarrassingly simple and the reason it is skipped is that it produces no artefact
anyone wanted.

```
                                                            LAYER VIEW

   MEASURING THE NOISE FLOOR

   run the UNCHANGED harness k times over the same corpus
   record the score each time
   the floor is the spread you must exceed to claim an effect

   THE COLD OPEN, measured:
     run 1   71
     run 2   76
     run 3   72
     run 4   75
     run 5   71
     ----------------------------------------------------------
     spread  71 - 76        floor ~= 5 points at this k and n

   WHICH MEANS
     March's +4    inside the floor    NOT an improvement
     April's -2    inside the floor    NOT a regression
     -- and both decisions were coin flips dressed as measurements

   NARROWING THE FLOOR                    effect on the floor
   +--------------------------------------------------------------+
   |  more tasks (n)              as the SQUARE ROOT of n. Sixty   |
   |                              to a hundred and twenty narrows  |
   |                              it by about 30%.                 |
   |                                                               |
   |  more rollouts per task (k)  averages out per-task variance,  |
   |                              which is usually the LARGER term |
   |                              in agent workloads (5.2)         |
   |                                                               |
   |  PAIRING the comparison      task difficulty cancels: the     |
   |                              same task, both harnesses, same  |
   |                              inputs. Usually the cheapest     |
   |                              large win (C39 sec 5.3)          |
   |                                                               |
   |  a better grader             a 5% false-pass rate is a floor  |
   |                              under the floor (3.1)            |
   +--------------------------------------------------------------+

   RE-MEASURE THE FLOOR WHEN THE MODEL CHANGES. It is a property
   of the model's variability as much as of the corpus, and C38's
   invalidation register should carry it as an entry.

  Figure 41.3 -- The noise floor, measured and narrowed (D7 Data Flow)
```

`[BP]` Run the floor measurement on a schedule — monthly, and on every model change — rather than
once. It drifts, and a floor believed to be three points when it is actually six produces exactly
the cold open with more confidence.

### 5.2 Rollouts per task

`[AHE App. A]` `pass@1` is reported as an average over k rollouts rather than a single run, and the
convention matters more than it sounds.

A single rollout per task gives each task a binary outcome, so the score is a sum of coin flips
whose bias you are trying to estimate. Five rollouts per task gives each task a rate — 0, 0.2, 0.4,
0.6, 0.8, or 1.0 — which carries far more information per task and averages out the per-task
variance that usually dominates.

`[BP]` The trade is that k rollouts cost k times as much. As a rule of thumb, when per-task variance
dominates — which it does in most agent workloads, because some tasks are genuinely borderline and
flip between runs — **spending a fixed budget on more rollouts of fewer tasks narrows the floor more
than spending it on more tasks with one rollout each.** Measure both on your own corpus before
committing; the ratio is workload-specific and the measurement is one afternoon.

The exception is coverage. Fewer tasks means fewer task types, and Chapter 39's blast-radius linter
needs slices that exist. Coverage is a constraint on how far the trade can be pushed, not a term in
it.

### 5.3 What makes a benchmark useful

Five properties, and the last two are the ones that get missed.

- **Task diversity.** Enough distinct task types to have slices, because a regression concentrated in
  one slice vanishes in an aggregate (Chapter 39 §6).
- **A spread of difficulty.** No ceiling and no floor. Tasks everything passes and tasks nothing
  passes contribute nothing but cost — they cannot move.
- **Failures for different reasons.** A corpus where every failure is a timeout measures timeouts.
- **Tasks of the length you actually run.** Chapter 29 §5.4's timeout-coupling hazard is invisible
  in a benchmark of ten-minute tasks, and it is the most likely reason a harness that evaluates well
  fails in production. `[BP]` Include long tasks even though they dominate the runtime cost — a
  handful is enough to detect the hazard.
- **Contracts, not judgments.** Each task carries a deterministic contract (Chapter 26). A benchmark
  scored primarily by model judgment inherits that judge's bias into every number, and Chapter 28's
  lattice bounds it only if there is a deterministic floor underneath.

### 5.4 Two gates, two maintenance rhythms

The regression harness and the benchmark decay in different ways and need different upkeep.

**The regression harness grows by incident.** Every production failure that the golden set would
have caught becomes a golden case, permanently. `[BP]` Make it a step in the postmortem template;
it is the cheapest institutional memory available and it costs one case per incident.

**The benchmark grows by coverage and by rollouts.** New task types as the product widens; more
rollouts as the floor becomes the binding constraint on decisions. `[BP]` Neither happens
spontaneously, and both need an owner — the benchmark is the thing everyone relies on and nobody is
assigned to.

### 5.5 Corpus tasks retire, never silently change

Chapter 28 §5.2 forbade editing the golden set to make a run pass, and the same rule applies here
with an addition: a benchmark task whose expected behaviour changes must be **retired and replaced**,
not edited.

The reason is comparability. Every historical result was measured against the corpus as it was, and
editing a task silently invalidates every prior comparison — including the noise floor, which was
measured on a corpus that no longer exists.

`[BP]` Version the corpus, record the corpus version alongside the triple in every result, and treat
a corpus change as invalidating the floor. Chapter 38's register is the right home for that
dependency.

### 5.6 Corpus drift

The slower failure: the corpus was drawn from traffic eighteen months ago and traffic has moved. The
benchmark still runs, still produces numbers, and measures a product the company no longer sells.

`[BP]` Compare the corpus's slice distribution against production traffic's quarterly. When they
diverge, add tasks rather than reweighting — reweighting changes historical comparability the same
way editing does, and adding is the operation that preserves it.

### 5.7 What Level 5 requires that a human process does not

This is the chapter's purpose and the handoff to Level 5.

A human team makes a handful of harness decisions a week, each read by someone who can apply
judgment, notice that a result looks odd, and go and check. An evolution loop makes thousands, reads
none of them, and applies the same rule to every one.

Four requirements follow, and none is optional:

| Requirement | Why | Without it |
|---|---|---|
| **A measured floor, per slice** | The loop's decision rule is "is this outside the floor" | It follows the noise gradient, confidently |
| **Paired comparison** | Variance dominates at small effect sizes | Every marginal edit is a coin flip |
| **Cost in the denominator** | Score alone rewards spending more (C35 §14) | It discovers that a bigger model scores better |
| **A grader the loop cannot reach** | Its score is a sum of verdicts (C28 §7.2) | It optimises the verifier rather than the work |

`[BP]` And one practice: **the loop's own decisions are measured against the floor and logged with
it.** Chapter 47's attribution needs to distinguish "this edit helped" from "this edit was inside
the floor and we kept it anyway", and only the second is a bug in the loop.

The blunt version, worth stating because it determines whether Level 5 is worth starting: **if your
benchmark cannot reliably detect the size of effect a single harness edit produces, an evolution
loop will not work.** It will produce motion and a rising score on its own instrument, and neither
will correspond to anything. That is not a Level 5 problem to solve later; it is a Level 4
prerequisite, and this is the chapter that says so.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  A harness change evaluated properly.

  t     step                          result
  ----  ----------------------------  ---------------------------
  0     candidate harness hash from
        C39's pipeline; gate 1 passed
  1     blast-radius linter: shared
        instruction -> full corpus,
        all 6 slices
  2     floor lookup: measured 9 days
        ago, model unchanged
          overall     3.1 pp
          dep-upgrade 8.4 pp   (10 tasks -- WIDE, 4.1)
          refactor    7.9 pp
          ...
  3     paired run: candidate and
        incumbent, same 60 tasks,
        same inputs, k=5 rollouts
        = 600 runs
  4     3h20m, own work class (4.2),
        preempted twice by production
  5     grader honesty rate attached:
        disagreement 1.2% (3.1)
  6     effect report:
          overall     +2.4 pp   floor 3.1  INSIDE  -> not an
                                                      improvement
          dep-upgrade +1.1 pp   floor 8.4  INSIDE
          refactor    +9.8 pp   floor 7.9  OUTSIDE -> real
          triage      -1.2 pp   floor 6.0  INSIDE
          cost/success -4%                 outside its own floor
  7     PROMOTION: allowed. One slice
        improved outside its floor, no
        slice regressed outside its
        floor, and cost per success
        fell.
  8     recorded: triple, corpus
        version, floor, k, and the
        grader's disagreement rate

  NOTE t=6. The overall number is +2.4 and is NOT the result. The
  result is that one slice moved and the others did not, which is
  a far more useful thing to know and is invisible in an aggregate.

  FAILURE BRANCH -- the cold open's process on the same change:

    t=3   one run of the candidate: 76
          one run of the incumbent from last week: 72
    t=4   "+4 points" -> ship
    -- and the +4 is the same measurement that produced 71 and 76
       on an unchanged harness. The number is real. It measures
       nothing.

  FAILURE BRANCH -- an evolution loop on the same benchmark:

    a loop proposes 200 edits over a week
    each is evaluated with one rollout, no floor
    ~half measure positive by chance
    the loop keeps those, reports a rising score, and its
      accumulated "gains" are a random walk with a positive
      selection bias
    -- and it is FASTER and more confident than the humans were,
       which is what makes it worse rather than better (5.7)

  Figure 41.4 -- One change, measured against its floor (D4 Sequence)
```

The second failure branch is the whole argument for this chapter's position in the book. The loop
does nothing wrong. It applies a decision rule to a measurement, which is what it was built to do,
and the measurement cannot support the rule.

---

## 7. State Management

```
                                                            STATE VIEW

   NOISE FLOOR

      {{ unmeasured }}        the default, and the cold open
          |  k runs of the unchanged harness over the corpus
          v
      {{ measured }}  --- corpus version changes -----> {{ stale }}
          |     ^                                          |
          |     |                                          |
          |     +------------- re-measured ----------------+
          |
          | model changes (C38's invalidation event)
          v
      {{ stale }}

      ILLEGAL: reporting an effect size while the floor is
      {{ stale }} or {{ unmeasured }}. The report is a number
      without its error term, which is what every decision in the
      cold open was made on.

   BENCHMARK TASK

      {{ active }}
          |
          +---- expected behaviour changed ----> {{ retired }}
          |                                       (terminal;
          |                                        replaced by a
          |                                        NEW task)
          |
          +---- always passes / always fails --> {{ retired }}
                                                  contributes cost
                                                  and no information

      ILLEGAL: {{ active }} -> {{ active }} with edited content.
      Editing a task invalidates every historical comparison
      including the floor, silently (5.5).

   RESULT

      {{ recorded }}   carries: triple (C38), corpus version, k,
                       floor per slice, grader disagreement rate

      A result missing any of those is not comparable with any
      other result, which is the same failure as a run without a
      triple (C38 sec 3.1) at a different grain.

  Figure 41.5 -- Floor, task, and result states (D6 State Diagram)
```

### 7.1 A result carries its conditions or it is not a result

The `{{ recorded }}` state's field list is the chapter in one place. Six months later, comparing two
results requires knowing they were measured under the same model, the same corpus, the same rollout
count, and a grader of the same accuracy. Any of those differing makes the comparison meaningless,
and none of them is recoverable after the fact.

`[BP]` Store them with the result, not in a wiki page describing how evaluations are run. The wiki
page describes how they are run *now*.

### 7.2 The floor is derived and expensive, so it is cached with a validity condition

Unlike most derived state in this book, re-deriving the floor costs hours and real money. So it is
cached — and a cache needs an invalidation rule, which is Chapter 25's argument arriving in a new
place.

`[BP]` The floor is invalidated by a model change or a corpus version change, and by nothing else.
Both are discrete, both are recorded, and both are exactly the kind of event Chapter 38's register
was built to track. A floor invalidated by a timer instead would be re-measured pointlessly most
months and stale in the month that mattered.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class NoiseFloorEstimator(Protocol):

    def measure(self, corpus_version: str, triple: "VersionTriple", k: int) -> "Floor":
        """Run the UNCHANGED harness k times over the corpus and
        report the spread, PER SLICE.

        This produces no artefact anyone asked for, which is why it
        is skipped and why the cold open happens. It is the first
        thing to build, not the last.

        Small slices have wide floors, and that is where results get
        over-read (4.1).
        """

    def current(self, corpus_version: str, triple: "VersionTriple") -> "Floor | None":
        """None when stale -- a model change or a corpus version
        change invalidates it, and nothing else does (7.2).

        Callers must handle None by refusing to report an effect
        size, not by substituting a remembered number.
        """


class EvaluationRunner(Protocol):

    def evaluate(
        self,
        candidate: "VersionTriple",
        incumbent: "VersionTriple",
        corpus_version: str,
        k: int,
        paired: bool = True,
    ) -> "EffectReport":
        """k rollouts per task; `pass@1` averaged over k, never a
        single run `[AHE App. A]`.

        Paired by default: the same task, both harnesses, identical
        inputs, so task difficulty cancels. This is usually the
        cheapest large narrowing of the floor available (5.1).

        Raises if the floor is stale. A number without its error
        term is not a result.
        """


class CorpusManager(Protocol):

    def retire(self, task_id: str, reason: str) -> str:
        """Retire and replace. NEVER edit.

        Editing a task silently invalidates every historical
        comparison including the floor, which was measured on a
        corpus that then no longer exists (5.5).
        """

    def drift(self) -> "DriftReport":
        """Corpus slice distribution against production traffic.
        When they diverge, ADD tasks -- reweighting breaks
        comparability the same way editing does (5.6).
        """
```

`EvaluationRunner.evaluate` raising on a stale floor rather than warning is the enforcement that
matters. A warning is read once and then filtered; an exception makes the missing measurement a
blocking condition, which is the only thing that gets the floor measured before it is needed rather
than after an incident.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Floor:
    corpus_version: str
    triple: "VersionTriple"       # a floor belongs to a model
    k: int
    per_slice_pp: dict[str, float]
    overall_pp: float
    measured_at: str


@dataclass(frozen=True)
class BenchmarkTask:
    task_id: str
    slice_name: str
    contract: "Contract"          # deterministic (C26), not a judgment
    expected_duration_s: float    # include long ones (5.3)
    provenance: str               # consented, synthesised, or public
    retired_at: str | None        # retired, never edited (5.5)


@dataclass(frozen=True)
class EvaluationResult:
    """Carries its conditions, or it is not comparable (7.1)."""
    candidate: "VersionTriple"
    incumbent: "VersionTriple"
    corpus_version: str
    k: int
    floor: Floor
    per_slice_delta_pp: dict[str, float]
    cost_per_success_delta: float          # C35's headline
    grader_disagreement_rate: float        # C36's honesty SLI
    ran_at: str

    def outside_floor(self, slice_name: str) -> bool:
        return abs(self.per_slice_delta_pp[slice_name]) > self.floor.per_slice_pp[slice_name]
```

`EvaluationResult` embedding the whole `Floor` rather than referencing it by id is deliberate. A
result that outlives the floor it was measured against becomes uninterpretable, and a reference can
dangle while an embedded value cannot.

`outside_floor` being a method on the result — the only place the comparison is expressed — means no
consumer writes its own threshold check. Chapter 39's gate calls this; Chapter 47's loop calls this;
neither gets to invent a rule.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Trace store (C34) | Corpus manager | Curation, with provenance | Candidate tasks from real traffic |
| Corpus manager | Evaluation runner | Versioned read | Tasks and slices |
| Floor estimator | Evaluation runner | Blocking lookup | The floor, or a refusal |
| Grader (C28) | Evaluation runner | Per run | Verdicts |
| Honesty auditor (C36) | Effect reporter | Current rate | The grader's own error term |
| Effect reporter | Promotion gate (C39) | Blocking | Per-slice effects with floors |
| Effect reporter | Published quality (C36) | Scheduled | The tracked trend |
| Effect reporter | **Level 5** | Every proposal | The decision rule the loop applies |

The first row carries Chapter 37's constraint and it is worth restating here because it is easy to
lose: benchmark tasks drawn from real traffic are customer material, they are a derived artefact,
and derivation is one-way (Chapter 37 §5.5). `[BP]` Prefer synthesised or consented tasks, and record
provenance per task so the question is answerable later rather than archaeological.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Decisions made without a floor | Nothing, until someone runs the benchmark twice | Measure the floor first (§5.1). The cold open |
| Per-slice results over-read | Small slices with wide floors | Report the floor beside every number, at every grain (§4.1) |
| Floor stale after a model change | Register entry (C38) | Invalidate on model or corpus change; refuse to report (§7.2) |
| Single rollout per task | Score is a sum of coin flips | k rollouts, `pass@1` averaged (§5.2) |
| Unpaired comparison | Wider floor than necessary, at the same cost | Pair by default (§5.1) |
| Benchmark task edited | Every historical comparison silently invalid | Retire and replace (§5.5) |
| Corpus drift | Slice distribution against traffic, quarterly | Add tasks, never reweight (§5.6) |
| Score without cost | A change that spends triple for two points passes | Cost per success in the report (§5.7) |
| Grader error term omitted | A measurement missing one of its two error sources | Attach the honesty rate (§3.1) |
| Ceiling or floor tasks retained | Cost with no information | Retire them (§7) |
| Evaluation starved or starving production | Promotion gates taking days, or production latency | Its own work class, reserved and preemptible (§4.2) |

The first row's detector — *nothing* — is the honest entry and it explains why this failure is so
common. There is no signal that a benchmark's resolution is inadequate. The numbers look the same
either way, and the only way to find out is to deliberately spend money measuring nothing.

---

## 12. Scalability

**Cost is n tasks × k rollouts × 2 harnesses, against the model semaphore.** A sixty-task corpus at
k=5, paired, is six hundred runs per evaluation. At a few minutes each and meaningful concurrency,
that is hours and a real bill — and it is the dominant operational cost in Level 4.

**The floor measurement is k runs of one harness**, so roughly half an evaluation, and it is
amortised across every comparison until invalidated.

**Pairing is free and narrows the floor**, which makes it the highest-return optimisation available
here. It costs nothing extra because both harnesses were going to be run anyway.

**Level 5 multiplies this by proposal volume**, which is the real scaling question. `[BP]` A loop
proposing hundreds of edits cannot afford a full evaluation each. The available structure is
staged: a cheap slice-targeted evaluation to reject the obviously-inside-the-floor majority, and a
full paired evaluation for survivors. That is Chapter 47's problem and the class it needs
(§4.2) is built here.

---

## 13. Production Engineering

### 13.1 The five numbers

- **The noise floor, per slice, with its age.** The number every other number is read against.
- **Minimum detectable effect versus typical effect size.** If the effects you are trying to detect
  are routinely smaller than the floor, the benchmark cannot support the decisions being made on it,
  and that is a fact about the instrument rather than about the changes.
- **Cost per successful outcome, as a tracked delta.** Chapter 35's headline, and the term that stops
  the loop discovering that spending more works.
- **Corpus drift against traffic**, quarterly.
- **Grader disagreement rate.** The floor under the floor.

### 13.2 The review question

For any claimed improvement: **what is the floor for that slice, and is this outside it?**

Two clauses, both mechanical, and together they retire most of the arguments that otherwise happen
in review. The cold open's team could not have answered either, not through carelessness but because
nobody had produced the number.

### 13.3 Teaching this to a new engineer

Give them March's +4 and April's -2 and ask which change was better. Everyone answers, and the answer
is confident.

Then give them the May result — 71 and 76, unchanged harness — and watch the two earlier numbers
dissolve. It is the fastest way to install the instinct this chapter exists to install, and the
instinct is a question rather than a technique: *compared to what spread?*

---

## 14. Relation to AHE

`[AHE App. A]` The conventions are the source's: rollouts per task, `pass@1` averaged rather than
taken once, tokens per trial, success per million tokens. This chapter's contribution is to place
the noise floor before all of them, because the conventions describe how to report a number and the
floor determines whether the number means anything.

`[AHE §4.4]` The source's own results are the strongest available argument for this discipline.
Effective edits do not stack — three positive single-component gains summing to +11.1 points yield
+7.3 together — and fix prediction runs at roughly five times random. Both findings are measurements
of effects small enough that they exist only relative to a known floor. A team reproducing that work
on an unmeasured benchmark would report whatever their noise happened to do.

`[INF]` §5.7 is the handoff, and it is the sharpest thing this chapter says. An evolution loop is a
mechanism for making thousands of small statistical judgments without human review. Below the noise
floor it does not fail loudly; it produces motion, a rising score on its own instrument, and
accumulated edits that are a random walk with a positive selection bias. **The prerequisite for
Level 5 is not more capability. It is a benchmark whose resolution exceeds the size of the effects a
single edit produces** — and if that is not true, the honest answer is to improve the instrument
before building the loop.

---

## 15. Industry Perspective

**`[AHE App. A]`** Averaged `pass@1` over k rollouts is the source's convention and is now common in
agent evaluation. What remains uncommon is reporting the spread alongside it, which is the half that
makes the average interpretable.

**`[DAR]`** The golden-set regression harness is specified in the base runtime spec, and its
distinctness from the benchmark is the part most often collapsed. They answer different questions at different speeds and
decay in different ways (§2.3).

**`[BP]` The clinical-trial vocabulary is worth adopting deliberately.** Minimum detectable effect,
paired comparison, multiple comparisons, stopping rules — every one has a direct counterpart, and
teams that have not borrowed the words rediscover each hazard at their own expense. The multiple-
comparisons hazard in particular is live: testing six slices means six chances for one to look
significant, and §5.1's per-slice floors are the honest handling.

**`[BP]` Public benchmarks compare systems and detect regressions poorly.** Their task distribution
is not your traffic, and the regressions that matter are in the slices your customers exercise.
Both are worth having, for different purposes, and substituting one for the other is a common
mistake in both directions.

**`[INF]` Almost nobody measures their noise floor.** It costs money, produces no artefact, and its
absence has no symptom. It is also the single highest-return thing a team in this position can do,
and it can be started this week with the benchmark that already exists.

**`[FUT]` Adaptive sampling — spending rollouts where the variance is, rather than uniformly — is
well understood in other fields and unexplored here.** Tasks that pass or fail consistently need one
rollout; borderline tasks need many. A runner that allocated k per task by observed variance would
narrow the floor substantially at the same cost, and the data to do it accumulates automatically.

---

## 16. Key Takeaways

1. **Measure the noise floor before measuring anything else.** Run the unchanged harness k times.
   Until you have that number, every effect size is a number without its error term.
2. **The floor has no symptom when it is too wide.** The results look identical either way, which is
   why three months of decisions can be noise without anyone noticing.
3. **Report the floor beside every number, at every granularity.** Small slices have wide floors,
   and per-slice breakdowns are where results get over-read.
4. **Pair the comparison.** The same task, both harnesses, identical inputs. It costs nothing extra
   and usually narrows the floor more than adding tasks does.
5. **k rollouts per task, `pass@1` averaged.** A single rollout makes each task a coin flip; five
   make it a rate, and per-task variance is usually the larger term.
6. **Retire tasks, never edit them.** An edit silently invalidates every historical comparison
   including the floor.
7. **This is the gate into Level 5.** A loop makes thousands of these judgments with nobody reading
   any of them. Below the floor it will follow the noise gradient — faster and more confidently than
   the humans it replaced. If the benchmark cannot detect the size of effect one edit produces, fix
   the instrument before building the loop.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Noise floor** | The spread of scores from running an unchanged harness repeatedly, which sets the minimum effect any decision can be based on. | `[INF]` | Ch 44, Ch 47 |
| **Minimum detectable effect** | The smallest change a benchmark can distinguish from its own variability, and the hard limit on what any process built on it can decide. | `[BP]` | Ch 47 |
| **Rollouts per task** | Running each task k times and averaging, so a task yields a rate rather than a coin flip. | `[AHE]` | Ch 44 |
| **Paired evaluation** | Comparing two harnesses on identical tasks and inputs so task difficulty cancels, which narrows the floor at no extra cost. | `[BP]` | Ch 47 |
| **Per-slice floor** | A noise floor computed per task type, because small slices have wide floors and that is where results are over-read. | `[INF]` | Ch 47 |
| **Corpus version** | An identifier for the benchmark's contents, recorded with every result, because editing a task invalidates all prior comparisons. | `[INF]` | Ch 47 |
| **Task retirement** | Replacing a benchmark task rather than editing it, preserving the comparability of every historical result. | `[BP]` | Ch 46 |
| **Corpus drift** | The benchmark's slice distribution diverging from production traffic, corrected by adding tasks rather than reweighting. | `[INF]` | Ch 46 |
| **Success per unit cost** | The evaluation headline, which prevents a change that spends more for a marginal gain from counting as an improvement. | `[AHE]` | Ch 46 |
| **Evaluation work class** | Reserved-but-preemptible capacity for benchmark runs, so evaluation neither starves nor starves production. | `[BP]` | Ch 44 |

---

**Level 4 is complete.** You can size a runtime from measurement rather than formula, see both what
the machinery is doing and whether the work is good, know what a good outcome costs, promise a
customer something you can keep, govern the data the system accumulates, version and ship the
harness as code, test a system whose unit calls a model, and — now — tell whether a change to any of
it made anything better.

That last capability is the one Level 5 is built on top of, and it is the one most teams do not
have.

**Next:** *Interlude II — Anatomy of a Bad Week*, which reads three incidents through the surfaces
this level built, and then Chapter 42, which opens Level 5 by asking why a machine should be doing
any of this at all.
