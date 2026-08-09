```
  Level 4 · Chapter 39
  GITOPS AND CI/CD FOR AGENT SYSTEMS
  Requires   C27 Failure and Rollback, C28 Grading,
             C38 Deployment and Versioning
  Unlocks    C40 Testing, C41 Evaluation Infrastructure,
             C47 Attribution and Rollback
  Diagrams   Core (5)
```

# Chapter 39 — GitOps and CI/CD for Agent Systems

---

## 1. Motivation

### 1.1 Cold open

A customer reports that Atlas keeps loosening a version constraint they need pinned. An engineer
adds three sentences to `prompts/planner/instructions.md`:

> When the task mentions a specific version, prefer an exact pin over a range. Widening a constraint
> the user has stated is a change they did not ask for. Preserve the form the user wrote.

It is correct. It is reviewed in a chat thread by two people, tested by hand against the customer's
case, and merged. The deploy pipeline treats `prompts/` as configuration and hot-reloads it within
the minute.

Sixteen days later someone notices that a different task type — routine dependency upgrades — has a
success rate of 79%, down from 85%, and that the drop starts on the afternoon of the merge.

Nobody connected them. The change was to a Markdown file, so nothing compiled and no unit test ran.
The evaluation suite runs on code changes, and this was not one. The reviewers read three sentences
about version pinning while thinking about the customer who had complained.

A dependency upgrade's entire purpose is to widen a constraint the user wrote. The instruction was
right for the case it was written for and precisely inverted for a task type nobody in the thread
was thinking about.

The system's highest-leverage behavioural surface had no pipeline, and the fact that it had no
pipeline was not a decision anyone made.

### 1.2 In plain language

Every team has a process for changing code: it goes in version control, someone reviews it, tests
run, it deploys in stages, and it can be reverted.

The instructions and tool descriptions that shape an agent's behaviour usually do not go through any
of that. They are text files. They look like configuration. Changing them feels like changing a
setting, not like changing code — and they often deploy faster than code precisely because nothing
needs building.

That is backwards. A three-sentence edit to an instruction file can change behaviour across every
task the system does, which is a wider blast radius than most code changes have. It is the surface
that most needs a pipeline and it is the one that most often lacks one.

The complication is that the usual pipeline does not fit. You cannot write a unit test for a
sentence. The only way to find out what an instruction change does is to run real tasks and measure
the results — which takes minutes or hours, costs money, and gives you a noisy number rather than
pass or fail.

So the pipeline has a different shape: a fast, cheap check that runs on every change and catches
outright breakage, and a slow, expensive measurement that runs before anything is promoted. And
review, which everyone relies on, turns out to be the weakest part — because nobody reading three
sentences about version pinning is thinking about dependency upgrades.

### 1.3 Why this chapter exists

Chapter 38 established the harness as a version axis with its own identity and its own rollback
story. That was about *identifying* changes. This chapter is about *shipping* them.

`[AHE §3.1]` treats the harness workspace as a git repository with file-level diffs and rollback,
which is the correct primitive and is usually described as an implementation detail of the
evolution loop. It is not. It is what a human team should already have before any loop exists,
because Chapter 47 will ask a machine to make these changes automatically and no automation improves
a pipeline that is not there.

The specific gap this chapter closes is that **the harness bypasses the pipeline by accident, not by
decision.** Nobody chooses to ship instructions without review. It happens because the files are
text, the directory looks like config, the deploy path is faster, and there is no test to run — four
reasonable-looking local facts that add up to an unreviewed deployment surface.

### 1.4 What previous framings got wrong

**"Prompts are configuration."** Configuration changes operational parameters. These change
behaviour on every task the system performs. The categorisation is the cold open's root cause and it
is made by directory layout rather than by anyone's judgment.

**"Review catches it."** Review catches what the reviewer is thinking about. Nobody reading a
version-pinning instruction is thinking about dependency upgrades, and no amount of diligence fixes
that — the effect is on task types absent from the diff (§5.5).

**"Test it manually against the case."** The cold open's engineer did exactly this, correctly, and
it verified the change worked for the case it was written for. That is necessary and it says nothing
about the cases it was not written for.

**"Run the evaluation on every commit."** A benchmark with enough rollouts to see past the noise
floor takes hours and costs real money. Gating every commit on it means either a very slow pipeline
or — far more likely — a benchmark quietly reduced until it is fast, at which point it cannot detect
anything (§5.2).

**"Reverting the file undoes the change."** It restores the harness. It does not restore the world
the harness acted on for sixteen days, and Chapter 27's tier taxonomy is what says which parts are
recoverable.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A harness change is a database migration.

Migrations are the closest thing most teams already have to this problem. They are data-shaped
rather than code-shaped. They live in the repository. They are reviewed with particular care because
their blast radius is wider than ordinary code. They are tested against a snapshot rather than by
unit tests. They deploy in a controlled order and have an explicit rollback story that everyone
knows is imperfect.

Every one of those instincts transfers, and a team that treats `prompts/` the way it treats
`migrations/` will avoid the cold open.

The break is in what "test it" means, and it is total.

A migration's effect is **deterministic and inspectable**. Run it against a copy of production, diff
the schema, and you know exactly what it does — completely, before it touches anything real.
Chapter 27 §5.4's whole migration-safety discipline rests on that inspectability.

An instruction change's effect is a **distribution over behaviours across every task type**, and
there is no run-it-and-diff. You can sample it. Sampling gives a noisy estimate whose noise floor
Chapter 41 spends a chapter measuring, and the effect you care about may be concentrated in a task
type your sample barely covers — which is the cold open exactly, where the regression was in a task
type nobody would have thought to include in a targeted test.

So the migration analogy gives the right process discipline and withholds the verification step
entirely. Everything in §5 is about what replaces it.

### 2.2 Why the pipeline has two gates

```
  (1) The harness changes daily, and every change changes
      behaviour across every task type.

  (2) Code changes go through review, tests, staged deploy, and
      revert. Harness changes usually go through none of it,
      because the files are text and the directory looks like
      configuration.

  (3) That is inverted. The blast radius is WIDER, not narrower:
      an instruction affects every task, where a code change
      affects one path.

  (4) So harness changes need the pipeline. But the pipeline's
      test step does not exist -- there is no unit test for a
      sentence.

  (5) The only real test is empirical: run tasks, measure
      outcomes. Slow, expensive, and STATISTICAL rather than
      pass-or-fail.

  (6) A slow statistical test cannot gate every commit. Making
      it fast enough to do so means shrinking it, and a shrunk
      benchmark cannot see past its own noise floor (C41).

  (7) So SPLIT the gate. A fast deterministic check on every
      commit -- the golden set (C28) -- catching outright
      breakage. A slow statistical evaluation before promotion,
      catching regressions.

  (8) And because review cannot predict effects on task types
      absent from the diff (5.5), the empirical gate is the
      PRIMARY control. Review catches what the benchmark does
      not cover, which is the reverse of the usual relationship.
```

Step (8) inverts the normal understanding of review and testing, and it is worth sitting with,
because it changes who is accountable for a bad harness change.

### 2.3 What lives in the harness workspace

`[AHE §3.1]` The workspace is a git repository. Its contents are everything the model is shown or
given, at fixed locations, so that a diff is meaningful and a revert is exact.

| Contents | Example | Blast radius |
|---|---|---|
| Instructions | `prompts/planner/instructions.md` | **Every task type** |
| Tool descriptions | `tools/search_files.yaml` | Every task using that tool |
| Context assembly policy | `context/ordering.yaml` | Every call; also the cache prefix (C35 §5.4) |
| Timeouts and budgets | `limits/step_budgets.yaml` | Latency and cost, per task type |
| Retry and classification rules | `recovery/classifier.yaml` | Failure handling everywhere |
| Effort tiers | `models/effort.yaml` | Cost and quality, everywhere |

The first row is the one that produces the cold open, and its blast radius column is why. `[BP]`
Order the review checklist by that column: a change to a shared instruction warrants more scrutiny
and a wider evaluation than a change to one tool's description, and the directory tells you which is
which.

### 2.4 The mental model to carry

The harness is code, in the repository, through the same pipeline, with file-level revert. The
pipeline has two gates because the real test is slow and statistical: a fast deterministic check on
every change and an empirical evaluation before promotion. Review is necessary and is not the
control, because a reviewer cannot see the task types the diff does not mention.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |          HARNESS WORKSPACE  (a git repository)               |
   |                                                              |
   |   prompts/   tools/   context/   limits/   recovery/         |
   |                                                              |
   |   fixed mount points, so a diff is meaningful and a revert    |
   |   is exact  `[AHE 3.1]`                                       |
   +--------------------------------------------------------------+
                            |
                            | (1) a change: human, or later a loop
                            v
   +--------------------------------------------------------------+
   |                        REVIEW                                |
   |   necessary; NOT the control. A reviewer cannot see the task |
   |   types the diff does not mention (5.5)                      |
   +--------------------------------------------------------------+
                            |
                            v
   +--------------------------------------------------------------+
   |   GATE 1: REGRESSION HARNESS        fast, deterministic      |
   |   golden set (C28), every commit, minutes                    |
   |   catches: outright breakage, schema violations, contract     |
   |            failures                                          |
   |   BLOCKS MERGE                                               |
   +--------------------------------------------------------------+
                            |
                            v
   +--------------------------------------------------------------+
   |   SHADOW              paired comparison on identical inputs, |
   |                       discarded before the first effectful   |
   |                       step (C38 sec 5.3)                     |
   +--------------------------------------------------------------+
                            |
                            v
   +--------------------------------------------------------------+
   |   GATE 2: EVALUATION                slow, statistical         |
   |   benchmark (C41), k rollouts, hours                         |
   |   catches: regressions on task types nobody was thinking     |
   |            about -- the cold open                            |
   |   BLOCKS PROMOTION                                           |
   +--------------------------------------------------------------+
                            |
                            v
   +------------------+   +------------------+   +----------------+
   |     CANARY       |-->|    PROMOTED      |-->|    RETIRED     |
   |  small traffic   |   |  full traffic    |   |  revertible    |
   |  triple recorded |   |                  |   |  (C38 sec 7.1) |
   +------------------+   +------------------+   +----------------+
                                  |
                                  | (2) revert is file-level and
                                  |     cheap -- and restores the
                                  |     HARNESS, not the world it
                                  |     acted on (5.6)
                                  v
                           [[ git history ]]

  Figure 39.1 -- The harness pipeline, with two gates (D1 High-Level
                 Architecture)

  (1) the same path whether a human or Chapter 47's loop makes the
      change; that is the point of building it now
  (2) file-level revert is C27 tier 1 and is the cleanest rollback
      in the book -- for the harness only
```

### 3.1 Build this before the loop, not with it

Every box in Figure 39.1 is something a human team needs. Chapter 47 will ask an evolution loop to
propose harness changes, and the loop's proposals go through this same pipeline — the same gates, the
same shadow, the same revert.

`[BP]` That is the argument for building it now rather than as part of Level 5. A loop attached to a
pipeline that does not exist produces changes that nothing evaluates, which is the cold open at
machine speed and volume. The pipeline is the thing that makes automation safe, and it is useful on
its own eighteen months earlier.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                      PIPELINE MACHINERY                        |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Regression harness     |  |    Evaluation runner      |   |
   |  |                          |  |                           |   |
   |  |  golden set (C28)        |  |  benchmark (C41)          |   |
   |  |  DETERMINISTIC checks    |  |  k rollouts per task      |   |
   |  |  no model judgment       |  |  reports effect size AND  |   |
   |  |                          |  |  the noise floor          |   |
   |  |  minutes; every commit   |  |                           |   |
   |  |  BLOCKS MERGE            |  |  hours; before promotion  |   |
   |  |                          |  |  BLOCKS PROMOTION         |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |    Shadow runner         |  |   Blast-radius linter     |   |
   |  |                          |  |                           |   |
   |  |  candidate + incumbent   |  |  which files changed ->   |   |
   |  |  on IDENTICAL inputs     |  |  which task types are at  |   |
   |  |                          |  |  risk -> which benchmark  |   |
   |  |  paired comparison       |  |  slices MUST be run       |   |
   |  |  removes most variance   |  |                           |   |
   |  |                          |  |  a shared instruction     |   |
   |  |  stops before the first  |  |  change requires the FULL |   |
   |  |  effectful step (C27)    |  |  benchmark, not a slice   |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 39.2 -- Inside the pipeline machinery (D2 Low-Level
                 Architecture)
```

### 4.1 The blast-radius linter is the cold open's direct fix

It is a small piece of software with an outsized effect: a mapping from changed paths to the
benchmark slices that must be run before promotion.

- `tools/search_files.yaml` changed → run the slices whose tasks use that tool.
- `limits/step_budgets.yaml` changed → run the long-task slices.
- `prompts/planner/instructions.md` changed → **run everything.** A shared instruction has no
  narrower blast radius, and no reviewer can argue it down.

The cold open's change was to the last category and was evaluated against one hand-run case. `[BP]`
Make the linter's output non-negotiable in the pipeline rather than advisory, because the argument
for narrowing it is always available and always sounds reasonable at the time.

### 4.2 The regression harness must stay fast, which means it must stay deterministic

Gate 1 runs on every commit, so it has to complete in minutes. That budget is only achievable if
every check is deterministic — Chapter 28 §4.1's rule that a check needing a model call is not a
check applies here for a second, independent reason.

`[BP]` Keep the golden set for gate 1 small and adversarial rather than large and representative:
the superficially-passing cases of Chapter 28 §5.2, a case per known past regression, and a
schema-validity check on every harness file. Representativeness is gate 2's job and it is what gate
2's hours are for.

---

## 5. Two Gates, Shadow, and the Limits of Review

### 5.1 What each gate is for

```
                                                            LAYER VIEW

   GATE 1  REGRESSION HARNESS                        BLOCKS MERGE
   +--------------------------------------------------------------+
   |  runs      every commit                                      |
   |  takes     minutes                                           |
   |  costs     negligible                                        |
   |  answer    PASS / FAIL, deterministic                        |
   |                                                              |
   |  catches   a malformed tool schema                           |
   |            an instruction that breaks a known past case      |
   |            a contract that no longer evaluates               |
   |            a context ordering that breaks the cache prefix   |
   |                                                              |
   |  MISSES    anything statistical. It cannot see a 6-point     |
   |            regression, and it is not supposed to.            |
   +--------------------------------------------------------------+

   GATE 2  EVALUATION                            BLOCKS PROMOTION
   +--------------------------------------------------------------+
   |  runs      before promotion, and on a schedule               |
   |  takes     hours                                             |
   |  costs     real money (C35)                                  |
   |  answer    an effect size, WITH a noise floor (C41)          |
   |                                                              |
   |  catches   the cold open: a regression on a task type the    |
   |            author was not thinking about                     |
   |            a cost regression (C35 sec 5.1)                   |
   |            an SLI regression (C36 sec 14)                    |
   |                                                              |
   |  MISSES    anything outside the benchmark's coverage --      |
   |            which is why the blast-radius linter forces the   |
   |            right slices (4.1) and why coverage is a          |
   |            standing concern rather than a solved one         |
   +--------------------------------------------------------------+

   THE SPLIT EXISTS because merging (6) and (7) in either
   direction fails:
     - gate 2 on every commit -> hours per commit, or a benchmark
       shrunk until it detects nothing
     - gate 1 only -> the cold open ships, having passed

  Figure 39.3 -- Two gates, two jobs (D7 Data Flow)
```

### 5.2 Why the benchmark cannot gate every commit

The arithmetic is Chapter 41's and the consequence is this chapter's. Detecting a change of a few
percentage points against a workload with real variance needs hundreds of task-runs at several
rollouts each. That is hours of wall clock and a meaningful model bill, per commit.

Teams that try it reach the same place within a month: the benchmark gets trimmed to fit the
pipeline's time budget. A trimmed benchmark has a wider noise floor, so it stops detecting the
changes it was trimmed to keep detecting, and it now passes everything — while still being called a
gate.

`[BP]` Protect the benchmark's size explicitly, and let the pipeline be slow at the promotion step.
A gate that takes four hours and works is better than one that takes four minutes and does not, and
the four hours are not on the critical path of a developer's inner loop — gate 1 is.

### 5.3 Shadow evaluation, and why it is cheap here

Chapter 38 §5.3 introduced shadowing; here is why it is worth more in this domain than in most.

Run the candidate harness and the incumbent on **identical inputs**, and compare. That pairing
removes most of the variance that gate 2 otherwise has to average away — the same task, the same
repository state, the same issue text, differing only in the harness. A paired comparison detects a
smaller effect with far fewer runs than two independent samples do.

And it is safe, for a reason this handbook already built: **stop before the first effectful step.**
Chapter 14's effect tag says exactly where that boundary is, and Chapter 27's tier taxonomy says
what would have happened past it. The shadow run does all the reasoning, all the tool selection, and
all the pure work, and is discarded at the moment it would touch anything.

`[BP]` Shadow on a fixed number of tasks per day rather than a percentage of traffic. The comparison
needs paired inputs and coverage of the blast radius, not volume — and a percentage-of-traffic
shadow over-samples whatever the busiest customer happens to be doing.

The limitation is worth stating: shadowing cannot compare anything downstream of an effect. A change
whose consequence appears only after a file is written and the tests are run is invisible to it.
That is gate 2's job, and it is why shadowing narrows the evaluation rather than replacing it.

### 5.4 Rollback is file-level, and stops at the harness

`[AHE §3.1]` File-level revert in a git workspace is the cleanest rollback story in this handbook:
Chapter 27 tier 1, owned state, prior version kept, a local write that cannot half-fail.

Its limit is exact and worth restating whenever someone reaches for it as reassurance. Reverting
`prompts/planner/instructions.md` restores the instruction. It does not restore the sixteen days of
dependency upgrades that shipped with the wrong constraint behaviour, some of which are merged into
customers' repositories.

`[BP]` A harness revert should therefore trigger a **scoped review of what shipped under it**: the
run records carrying that harness hash (Chapter 38's triple) are exactly the affected population,
and they are queryable. The cold open's team could not do this, because the harness version was not
recorded on runs — which is the one-line fix in Chapter 38 §3.1 paying for itself in a different
chapter.

### 5.5 Review is necessary and is not the control

The uncomfortable claim, stated plainly: **a reviewer cannot evaluate a harness change, and no
amount of care changes that.**

The cold open's reviewers were competent, the change was three sentences, and they read it carefully
in the context they had. The failure was in a task type that appears nowhere in the diff, is not
mentioned in the discussion, and would only occur to someone who had independently thought about
what "prefer an exact pin" means for a job whose purpose is widening pins.

That is not a diligence problem. The space of affected behaviours is every task type the system
performs, and a diff shows one.

So what is review *for*? Three things it does well, and they are the things gates do badly:

- **Catching what the benchmark does not cover.** A reviewer who knows a customer segment is absent
  from the benchmark can say so; the benchmark cannot.
- **Catching intent errors.** The instruction says something the author did not mean, or contradicts
  another instruction two files away.
- **Catching the category error.** "This is a code fix wearing an instruction costume" — the
  behaviour belongs in a tool, not in text (Chapter 30 and Chapter 35 both argue for this, and a
  reviewer is where it gets noticed).

`[BP]` Write the review checklist around those three rather than around "does this look right",
because the third question in particular is where the most valuable rejections come from.

### 5.6 Instruction changes accrete and nobody removes them

A slow failure worth designing against, and Chapter 35 §5.2 already gave the cost half of it.

Instruction files only grow. Each addition solves a real case, each is individually justified, and
none is ever removed because removing one risks regressing the case it was added for. After two
years the planner's instructions are four thousand tokens of accumulated special cases, several of
which contradict each other, and the cost is paid on every call forever.

`[BP]` Two practices help, and the second is the one that works:

- **A comment naming the case each addition was for**, so a future reader can tell whether it still
  applies — the same discipline Chapter 38 §5.1 asks for model-conditional content.
- **Periodic removal experiments.** Take an instruction out, run gate 2, and see whether anything
  moves. If nothing does outside the noise floor, it goes. This is the only mechanism that removes
  instructions, it costs one evaluation run each, and it is far easier once the pipeline exists.

The second practice is also the clearest early example of what Level 5 automates. An evolution loop
running removal experiments continuously is doing something a human team does approximately never,
and it is a genuinely good use of the machinery.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  The cold open's change, through the pipeline.

  t     step                          result
  ----  ----------------------------  ---------------------------
  0     engineer edits
        prompts/planner/
        instructions.md, +3 sentences
  1     opens a pull request in the
        SAME repository as the code
  2     blast-radius linter (4.1):
        shared instruction ->
        FULL benchmark required,
        no slice permitted
  3     GATE 1 regression harness:
        18 golden cases, 4 minutes    PASS -- correctly. Nothing
                                      is outright broken.
  4     review (5.5): two reviewers
        read it against the customer
        case                          approved
  5     merged to main; NOT deployed
  6     shadow starts: candidate and
        incumbent on 200 paired
        tasks, stopping before the
        first effectful step
  7     shadow comparison, 3 hours:
        tool selection identical on
        94% of steps
        DIVERGENCE concentrated in
        one slice: dependency
        upgrades, where the candidate
        proposes an exact pin on 71%
        of steps where the incumbent
        proposed a range
  8     that divergence is enough to
        stop here -- but the pipeline
        does not rely on someone
        noticing it
  9     GATE 2 evaluation, k=5
        rollouts, full benchmark:
          overall        -1.1 pp   inside the noise floor
          dep-upgrade    -6.4 pp   OUTSIDE it
                                      PROMOTION BLOCKED
 10     the instruction is scoped:
        "...unless the task is
        explicitly a dependency
        upgrade"
 11     re-evaluated:
          overall        +0.3 pp
          dep-upgrade    -0.2 pp   inside the floor
          the customer's case fixed
 12     canary 5%, triple recorded
 14     promoted

  ELAPSED: about two days, most of it waiting on gate 2.
  COMPARE the cold open: shipped in an hour, regressed for
  sixteen days, and was found by someone looking at an unrelated
  dashboard.

  FAILURE BRANCH -- gate 2 is skipped because the change is "only
  a prompt":

    t=5   merged and hot-reloaded within the minute
    t=16d verdict distribution alert on the dep-upgrade slice
          (C34 signal 9) -- IF that slice is graphed separately.
          If only the aggregate is graphed, -6.4 pp on one slice
          is -1.1 pp overall, which is inside the noise floor and
          invisible.
    -- the cold open's team had the aggregate only. That is why
       the regression survived sixteen days: not because nothing
       was watching, but because the watching was at the wrong
       granularity.

  Figure 39.4 -- One instruction change through two gates (D4
                 Sequence)
```

The failure branch's last note is the transferable one. `[BP]` **Graph the verdict distribution per
task type, not only in aggregate.** A regression concentrated in one slice is diluted by every other
slice until it disappears, and slices are exactly how the benchmark is organised already.

---

## 7. State Management

```
                                                            STATE VIEW

   HARNESS CHANGE

      {{ proposed }}
          |  blast-radius linter determines required coverage (4.1)
          v
      {{ gate_1 }} ---- fail ----> {{ rejected }}  (terminal)
          |  pass: minutes, deterministic
          v
      {{ reviewed }}
          |  necessary, not the control (5.5)
          v
      {{ merged }}       merged is NOT deployed
          |
          v
      {{ shadowed }}     paired comparison, no effects (5.3)
          |
          v
      {{ gate_2 }} ---- regression outside the floor ----+
          |  pass                                        |
          v                                              v
      {{ canary }}                             {{ revised }}
          |  no regression at 5%                    |
          v                                          | back to gate 1
      {{ promoted }}                                 |
          |                                          |
          | superseded, or reverted                  |
          v                                          |
      {{ retired }}  <----------------------------- -+
        revertible while its model lives (C38 sec 7.1)

      ILLEGAL: {{ merged }} -> {{ promoted }}. Merging and
      deploying are separate for the harness precisely because they
      are usually the same, and the sameness is what let the cold
      open reach production in under an hour.

      ILLEGAL: {{ gate_2 }} skipped for a "small" change. Size in
      the diff does not bound blast radius: the cold open is three
      sentences affecting every task type (2.3).

      ILLEGAL: narrowing the blast-radius linter's required slices
      to make gate 2 finish sooner. The argument is always
      available and always sounds reasonable (4.1).

  Figure 39.5 -- Harness change states (D6 State Diagram)
```

### 7.1 Merged is not deployed

For code, merge-then-deploy is usually one motion and that is fine. For the harness it must be two,
because the gate that matters is slow: gate 2 runs on the merged candidate, and promotion is a
separate act that consumes its result.

`[BP]` The practical form is that the deployed harness hash is a pointer, updated by promotion, not
by merge. Hot-reloading `prompts/` from the main branch is the mechanism that made the cold open a
one-hour incident, and removing it is a small change with a large effect.

### 7.2 Retired harnesses stay revertible

Same argument as Chapter 38 §7.1 and the same test: revert to a retired harness hash in staging on a
schedule, and discover that it no longer resolves *before* the day it is needed. A harness workspace
that references a tool schema which has since been deleted from the code repository does not
resolve, and that is exactly the kind of thing that is discovered under pressure.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class BlastRadiusLinter(Protocol):

    def required_slices(self, changed_paths: Sequence[str]) -> "Coverage":
        """Map changed files to the benchmark slices that must run.

        A shared instruction file maps to EVERY slice. There is no
        narrower answer and the result is not advisory -- the
        argument for narrowing it is always available and always
        sounds reasonable at the time (4.1).
        """


class RegressionHarness(Protocol):

    def run(self, harness_hash: str) -> "GateResult":
        """Gate 1. Deterministic, minutes, every commit.

        Every check is deterministic -- no model calls. C28 section
        4.1 gives the correctness reason; here there is a second,
        independent one: gate 1 must finish in minutes and a model
        call is neither fast nor repeatable.

        Cannot see a 6-point regression, and is not supposed to.
        """


class EvaluationRunner(Protocol):

    def evaluate(
        self,
        candidate: "VersionTriple",
        incumbent: "VersionTriple",
        coverage: "Coverage",
        rollouts: int,
    ) -> "EffectReport":
        """Gate 2. Statistical, hours, before promotion.

        Returns effect sizes PER SLICE alongside the noise floor,
        never a bare pass or fail. A regression concentrated in one
        slice is diluted to invisibility in an aggregate (6).
        """


class ShadowRunner(Protocol):

    def compare(self, candidate: str, incumbent: str, tasks: Sequence[str]) -> "Divergence":
        """Run both on IDENTICAL inputs and stop before the first
        effectful step (C14's tag says where; C27's tiers say what
        would have happened past it).

        Paired inputs remove most of the variance gate 2 must
        otherwise average away, which is why this detects a smaller
        effect with far fewer runs (5.3).
        """
```

`EvaluationRunner.evaluate` returning per-slice effect sizes with a noise floor, rather than a
boolean, is the signature that carries the chapter. A boolean gate invites a threshold, a threshold
invites tuning, and a tuned threshold on a noisy measurement is Chapter 41's cold open.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Coverage:
    """Which benchmark slices a change requires."""
    slices: tuple[str, ...]
    reason: str                  # which changed path forced this
    is_full: bool                # a shared instruction forces True


@dataclass(frozen=True)
class SliceEffect:
    slice_name: str
    delta_pp: float              # candidate minus incumbent
    noise_floor_pp: float        # from C41; the minimum detectable
    rollouts: int
    outside_floor: bool          # the only field a gate reads


@dataclass(frozen=True)
class EffectReport:
    per_slice: tuple[SliceEffect, ...]
    overall: SliceEffect
    blocks_promotion: bool       # any slice regressing outside its floor


@dataclass(frozen=True)
class Divergence:
    """A shadow comparison."""
    steps_compared: int
    steps_diverged: int
    by_slice: dict[str, float]   # divergence rate per slice
    first_effectful_step_reached: int   # where each run stopped
```

`SliceEffect.outside_floor` being the only field a gate reads is deliberate. It forces the noise
floor into the same structure as the effect, so a gate cannot be written that compares a delta
against a hard-coded threshold without the floor being right there — which is the mistake
Chapter 41 exists to prevent.

`Divergence.by_slice` is what would have caught the cold open at step 7 of §6, before gate 2 was
even needed. A shadow run's divergence concentrated in one slice is an early, cheap signal, and it
costs nothing extra to compute.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Harness workspace | Blast-radius linter | On pull request | Changed paths |
| Linter | Evaluation runner | Required coverage | Slices, non-negotiable |
| Regression harness | Merge gate | Blocking | Deterministic pass or fail |
| Shadow runner | Reviewers | Report | Per-slice divergence, before gate 2 |
| Evaluation runner | Promotion gate | Blocking | Per-slice effects with noise floors |
| Promotion | Deployed pointer | Update | Harness hash — merge does not (§7.1) |
| Revert | Run query | On rollback | Runs carrying the reverted hash (§5.4) |
| Chapter 47's loop | This entire pipeline | The same path | A proposed harness change |

The last row is why the chapter is in Level 4. `[BP]` Every mechanism here is exercised by humans
first, which means that by the time an evolution loop proposes changes, the gates have been
calibrated by a year of real use rather than being built speculatively alongside the thing they are
meant to constrain.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Harness files bypass the pipeline | Nothing, until a regression is noticed weeks later | Same repo, same pipeline; remove the hot-reload path (§7.1). The cold open |
| Regression in a slice, diluted in the aggregate | Per-slice verdict graphs (§6) | Graph and gate per slice, never only overall |
| Gate 2 skipped for a "small" change | Nothing | Diff size does not bound blast radius (§7) |
| Benchmark trimmed to fit the pipeline | It starts passing everything | Protect its size; let promotion be slow (§5.2) |
| Blast-radius linter narrowed | Regressions in un-run slices | Non-negotiable output (§4.1) |
| Review treated as the control | A reviewer cannot see absent task types | Empirical gate is primary; review catches what it does not cover (§5.5) |
| Revert assumed to undo the damage | Effects already shipped | Query runs by harness hash and review them (§5.4) |
| Retired harness no longer resolves | Discovered on the day it is needed | Exercise revert on a schedule (§7.2) |
| Instructions accreting for years | Instruction share of input tokens (C35 §13.1) | Removal experiments, one evaluation run each (§5.6) |
| Model calls inside gate 1 | Gate 1 taking longer than minutes, and flaking | Deterministic checks only (§4.2) |

Row two deserves emphasis because it is the reason the cold open lasted sixteen days rather than
two. The monitoring existed and was correct; it was aggregated at a granularity coarser than the
failure. **A regression concentrated in one slice is invisible in an average**, and the fix is a
grouping key on a graph that already exists.

---

## 12. Scalability

**Gate 1 must stay in minutes**, which bounds the golden set's size and forbids model calls. It runs
on every commit from every engineer and later on every proposal from an evolution loop.

**Gate 2 is the expensive component and its cost is the benchmark's size times the rollout count
times the model rate.** Chapter 41 §12 sizes it. `[BP]` Budget it as a standing operational cost
rather than as per-change overhead, because a per-change budget is the pressure that shrinks the
benchmark (§5.2).

**Shadow costs one extra model call per shadowed step**, bounded by a fixed daily task count rather
than by traffic (§5.3).

**Volume is where Level 5 changes the arithmetic.** A human team proposes a handful of harness
changes a week. An evolution loop proposes many more, and each wants gate 2. `[BP]` That is a
capacity planning problem for Chapter 33's model semaphore and it should be given its own work
class — reserved so the loop is not starved, preemptible so production wins during a burst.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Fraction of harness changes that ran gate 2.** Should be 1.0. Anything less names a bypass path.
- **Gate 1 duration, p95.** The moment it exceeds a few minutes, engineers start looking for ways
  around it, and they will find one.
- **Per-slice effect at promotion.** Kept as a record, so a regression found later can be checked
  against what the gate said at the time.
- **Time from merge to promotion.** Not a number to minimise — a number to know, because it is the
  window during which a merged change is not yet evaluated.
- **Instruction token count, per file, over quarters.** §5.6's accretion, made visible.

### 13.2 The review question

For any change to a harness file: **which task types could this affect, and which of them is in the
evaluation that will run?**

The first half is what a reviewer can genuinely contribute. The second half is what the
blast-radius linter answers mechanically. Where they disagree — the reviewer names a task type the
linter did not require — the reviewer wins and the coverage widens, which is exactly the division of
labour §5.5 argues for.

### 13.3 Teaching this to a new engineer

Show them the three sentences and ask what could go wrong. Almost nobody says dependency upgrades,
and that is the lesson rather than a failure of the exercise.

Then ask what process would have caught it. The answers arrive in a useful order: better review
(no — nobody thinks of it), a test for the customer's case (already done, and it passed), and
finally running the whole benchmark — at which point the two-gate structure and its cost follow on
their own.

---

## 14. Relation to AHE

`[AHE §3.1]` The harness workspace as a git repository with file-level diffs and rollback is the
source's, and this chapter's contribution is to insist that it is a *human* practice first. The
source describes it as infrastructure for the evolution loop; it is equally the correct way for a
team to ship harness changes, and building it early means Level 5 attaches to something proven.

`[INF]` Chapter 47's attribution depends on this pipeline in a specific way. Attributing an
improvement to a particular edit requires that the edit was isolated, evaluated, and recorded with
its triple — which is what the pipeline produces as a side effect. A team shipping harness changes
without it has no attribution history to hand an evolution loop, and the loop's first task becomes
recovering information that was discarded.

`[INF]` §5.6's removal experiments are worth flagging forward as the clearest early example of what
automation is genuinely good at. Humans do not run them, because each one risks a regression for no
visible gain and the payoff is diffuse. A loop running them continuously against the accretion of
years is doing something valuable that nobody was going to do, and it needs no new mechanism beyond
this pipeline.

---

## 15. Industry Perspective

**`[AHE §3.1]`** File-level harness diffs and rollback are the source's primitive and the right one.
The gap between the source and common practice is not the primitive; it is that most teams do not
have the workspace under version control with fixed mount points at all.

**`[BP]` Treating prompts as code is now widely recommended and unevenly practised.** The
recommendation is easy to agree with and the practice fails on the mechanical details — the
directory that hot-reloads, the deploy path that skips CI, the file type with no test. Each is a
small local convenience and together they are the cold open.

**`[BP]` Two-tier testing is standard everywhere.** Fast unit tests on every commit, slow
integration or end-to-end suites before release. The twist specific to agent systems is that the slow tier is
statistical rather than deterministic, so its output is an effect size and a noise floor rather than
a pass or fail — and a gate that reduces it to a boolean loses the only information that made it
trustworthy.

**`[INF]` Shadow evaluation is under-used given how cheap the effect tag makes it.** Most systems
that could shadow do not, and the usual reason given is the risk of double effects — which
Chapter 14's tag and Chapter 27's tiers resolve precisely, by naming the step to stop before.

**`[FUT]` Automatic blast-radius inference is unexplored.** The linter in §4.1 is a hand-maintained
path-to-slice mapping. The same information is derivable from trace data — which slices actually
exercised which harness files — and would keep itself current as the benchmark and the workspace
both change. It is a straightforward piece of work and nobody appears to have built it.

---

## 16. Key Takeaways

1. **The harness is code and bypasses the pipeline by accident, not by decision.** Four
   reasonable-looking local facts — text files, a config-shaped directory, a faster deploy path, no
   test to run — add up to an unreviewed surface with the widest blast radius in the system.
2. **Two gates, because the real test is slow and statistical.** A fast deterministic check on every
   commit, and an empirical evaluation before promotion. Merging either into the other fails in a
   predictable direction.
3. **Review is necessary and is not the control.** A reviewer cannot see the task types absent from
   the diff, and the cold open's failure was in one of them.
4. **Diff size does not bound blast radius.** Three sentences in a shared instruction affect every
   task type, and the blast-radius linter's answer must be non-negotiable.
5. **Graph and gate per slice.** A 6-point regression in one slice is a 1-point move in the
   aggregate, which is inside the noise floor and invisible.
6. **Shadow is cheap here because the effect tag says where to stop.** Paired inputs detect a
   smaller effect with far fewer runs than independent samples.
7. **Reverting the harness does not revert the world.** Query the runs carrying the reverted hash;
   that population is exactly what shipped under it, and it is only queryable if the triple was
   recorded.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Harness workspace** | A git repository with fixed mount points holding everything the model is shown or given, so a diff is meaningful and a revert is exact. | `[AHE]` | Ch 43, Ch 47 |
| **Regression harness** | The fast deterministic gate on every commit, deliberately unable to see statistical regressions. | `[DAR]` | Ch 41 |
| **Evaluation gate** | The slow statistical gate before promotion, returning per-slice effect sizes with noise floors rather than a boolean. | `[INF]` | Ch 41, Ch 47 |
| **Blast-radius linter** | A mapping from changed harness paths to the benchmark slices that must run, whose output is non-negotiable. | `[INF]` | Ch 41 |
| **Per-slice effect** | A measured change reported per task type, because a regression concentrated in one slice vanishes in an aggregate. | `[INF]` | Ch 41, Ch 47 |
| **Shadow comparison** | Running candidate and incumbent on identical inputs and stopping before the first effectful step, which pairs the samples and removes most variance. | `[BP]` | Ch 41 |
| **Merge-is-not-deploy** | Separating the merge of a harness change from the promotion of it, because the gate that matters takes hours. | `[BP]` | Ch 47 |
| **Removal experiment** | Taking an instruction out and evaluating, which is the only mechanism that ever removes one and is a natural target for automation. | `[BP]` | Ch 43, Ch 47 |
| **Instruction accretion** | The monotonic growth of instruction files, each addition justified and none removed, paid for on every call forever. | `[INF]` | Ch 43 |
| **Affected-population query** | Finding what shipped under a reverted harness by querying runs on their recorded triple. | `[INF]` | Ch 47 |

---

**Next:** Chapter 40 — *Testing a Non-Deterministic System.* Both gates in this chapter assumed
tests that mean something. The next one asks what a test is when the thing under test calls a model
— starting with a suite of fourteen hundred green tests, forty of which had been configured to pass
and therefore deleted.
