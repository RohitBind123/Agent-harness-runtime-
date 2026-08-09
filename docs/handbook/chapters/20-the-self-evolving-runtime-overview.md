```
  Level 2 · Chapter 20
  THE SELF-EVOLVING RUNTIME (AHE) -- OVERVIEW
  Requires   C14 The Tool Execution Engine, C15 ACI Design,
             C16 The Observation System, C18 The Runtime Loop,
             C19 The Multi-Agent Runtime
  Unlocks    C34 Observability, C39 GitOps, C41 Evaluation
             Infrastructure, and all of Level 5
  Diagrams   Full (9)
```

# Chapter 20 — The Self-Evolving Runtime (AHE) — Overview

---

## 1. Motivation

### 1.1 Cold open

The Atlas team spends a fortnight improving the harness. Six changes ship together: two tool
descriptions rewritten, a middleware timeout added, the system prompt tightened, a skill introduced,
and a long-term memory entry seeded.

The benchmark moves from 69.7% to 74.1%. Everybody is pleased.

Two weeks later a new base model arrives, the score drops to 71.2%, and the obvious question has no
answer: **which of the six should be reverted?**

Nobody knows. The six shipped in one commit, against one benchmark run, with no record of what each
was expected to fix. The middleware timeout was tuned to the old model's pacing and is now almost
certainly hurting — but so might the tightened prompt be, and the skill was written for a failure
mode that may no longer occur.

The team reverts all six and starts again, discarding four percentage points of genuine improvement
along with whatever was wrong.

Fourteen days of work, and the only thing they learned was the total.

### 1.2 In plain language

Everything so far has assumed a person improves the system. They read some failures, form a theory,
change something, and see if the score moves.

That works, and it does not keep up. Base models ship every few months, and each one arrives needing
the surrounding machinery re-fitted — different pacing, different strengths, different failure modes.
The people who understand the harness well enough to re-fit it are the scarce resource, not the
compute.

This chapter is about handing that loop to the machine: a second agent whose job is to read what went
wrong in a batch of runs, edit the harness, and measure whether it helped.

It is not magic and it is not a black box. It works because of three things the earlier chapters have
already built, and it fails without any of them.

The system must be made of **separate, replaceable parts**, so an edit can be attributed to one of
them. It must **record what actually happened**, in enough detail to explain why — which is what
Chapter 16 was for. And every edit must come with **a written prediction** of what it will fix, so
the next round can check whether the prediction held.

That third one is the cold open. Six changes shipped with no predictions, so a four-point gain
carried no information about which change earned it.

### 1.3 Why this chapter exists

This is the last chapter of Level 2 and it is placed here deliberately. Level 5 builds the evolution
loop properly, twenty-nine chapters from now. If a reader met the idea for the first time there, they
would have read all of Levels 3 and 4 without knowing what any of it was *for*.

`[INF]` Almost every decision in the next twenty chapters is easier to justify once you know the loop
exists. Chapter 34's observability, Chapter 39's GitOps, Chapter 40's replay harness, and Chapter
41's evaluation infrastructure are not general good practice that happens to be useful — they are the
loop's prerequisites, and this chapter is what makes that legible while there is still time to build
them properly.

### 1.4 What previous framings got wrong

**"The agent improves itself."** It does not. `[AHE §3.3]` A separate agent edits the harness — the
components outside the model — while the model, the runtime kernel, and the verifier stay fixed. The
distinction is the whole safety argument, and §5.5 makes it precise.

**"It learns."** Nothing is trained. Weights do not move. What changes is a directory of files
(Chapter 43), version-controlled, diffable, and revertible. `[INF]` Every intuition from machine
learning about gradients and convergence is misleading here; the right intuition is a colleague
editing configuration and measuring.

**"Give it the benchmark and let it optimise."** The cold open with a faster treadmill. Without
per-edit predictions there is no attribution, and without attribution the loop is doing random search
over a large space with a slow, noisy evaluation.

**"Observability is for operators."** Chapter 16 §1.4 separated the two, and this chapter is why it
matters: the loop's primary consumer is a machine that will change the system based on what it reads.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A clinical trial protocol, run by the department that treats the patients.

A hospital wants to improve outcomes. It does not change six protocols at once and check the annual
mortality figure — that is the cold open, and medicine abandoned it long ago. Instead each proposed
change is registered *in advance* with a specific, falsifiable claim: this change is expected to
reduce this complication, in this population, by roughly this much. The registration happens before
the data arrives, which is the entire point.

Then the intervention runs, the outcomes come back, and each registered prediction is checked against
what happened. A change that predicted its effect and delivered it is kept. One that predicted an
effect and produced nothing is reverted. And a change whose *unpredicted* harms show up elsewhere is
the most informative result of all.

Three things make that work: the treatments are separable, the outcomes are recorded in detail, and
every change is paired with a prediction made beforehand. Those are the three pillars of §2.3, in the
same order.

**Where the analogy breaks**, in a way that matters for Level 5.

A clinical trial has a control arm, randomisation, and a statistician who will tell you the effect is
within noise. This loop has none of those. It runs a benchmark, sees a number move, and must decide
what the movement meant — with a small sample, a non-deterministic system, and changes that interact.

`[INF]` So the honest framing is not "a trial" but "a trial protocol applied without the statistical
apparatus that makes trials trustworthy". That is why Chapter 48 exists: the loop's limits are not
implementation defects, they are what remains when you keep the registration discipline and drop the
inference machinery. Chapter 41's job is to give back as much of that machinery as is affordable.

### 2.2 Why the loop needs three pillars and not one

```
  1. To improve the harness automatically, something must decide
     WHAT to change. That needs evidence about what went wrong.
  2. Raw trajectories are far too large to reason over directly --
     millions of tokens per batch.
  3. So the evidence must be distilled into something navigable.
     -> EXPERIENCE observability (Ch 44)
  4. An edit must land somewhere specific. If the harness is one
     tangled artifact, "improve the harness" has no action space.
  5. So the harness must be separable parts, each mapping to a class
     of failure.
     -> COMPONENT observability (Ch 43)
  6. Now a change ships and the score moves. Which change did it?
     With N changes and one number, you cannot tell -- the cold open.
  7. So every edit must carry a prediction, recorded BEFORE the
     result, that the next round can check.
     -> DECISION observability (Ch 45)
  8. Three pillars, and removing any one collapses the loop into
     something else: without (3) it cannot see, without (5) it cannot
     aim, without (7) it cannot learn.
```

Step 8 is the shape worth carrying. `[INF]` Teams that attempt this usually build the first pillar,
sometimes the second, and almost never the third — which produces a loop that generates plausible
edits and can never tell whether any of them worked.

### 2.3 The three pillars

`[AHE §3]` The loop stands on three kinds of visibility, and each is a later chapter:

| Pillar | Question | Artifact | Chapter |
|---|---|---|---|
| **Component** observability | what can be changed, and where does a failure belong? | seven component types as files at fixed paths | 43 |
| **Experience** observability | what actually happened, and why? | the evidence corpus, distilled from trajectories | 44 |
| **Decision** observability | what did we expect this edit to do? | the change manifest | 45 |

`[INF]` Read the three questions in order and they are what any competent engineer asks when
improving a system: what can I change, what went wrong, and what do I expect my change to do. The
loop's contribution is making all three *machine-readable*, and the third one is where the discipline
is unusual — human engineers rarely write down their prediction, because they can hold it in their
head and revise it silently.

### 2.4 The mental model to carry

> **An edit is a falsifiable claim. Write the claim down before the evidence arrives, and the next
> round can tell you whether you were right.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  THE INNER LOOP (Ch 18) -- everything so far
  +--------------------------------------------------------------+
  |   runs, driven by the runtime loop, through six ports         |
  |   producing trajectories (Ch 16)                              |
  +---------------------------+----------------------------------+
                              | (1) trajectories
                              v
  THE OUTER LOOP -- this chapter, built in Level 5
  +--------------------------------------------------------------+
  |                                                              |
  |  +---------------------+  (2)   +----------------------+     |
  |  | AGENT DEBUGGER      |------->| EVIDENCE CORPUS      |     |
  |  |  distils 10M tokens |        |  ~10k tokens,        |     |
  |  |  (Ch 44)            |        |  navigable files     |     |
  |  +---------------------+        +----------+-----------+     |
  |                                            | (3)             |
  |                                            v                 |
  |  +---------------------+  (4)   +----------+-----------+     |
  |  | CHANGE MANIFEST     |<-------| EVOLVE AGENT         |     |
  |  |  per edit:          |        |  reads evidence,     |     |
  |  |   evidence          |        |  edits components    |     |
  |  |   root cause        |        |  (Ch 46)             |     |
  |  |   the fix           |        +----------+-----------+     |
  |  |   PREDICTED fixes   |                   | (5)             |
  |  |   AT-RISK tasks     |                   v                 |
  |  |  (Ch 45)            |        +----------+-----------+     |
  |  +----------+----------+        | HARNESS WORKSPACE    |     |
  |             |                   |  7 component types   |     |
  |             | (7) verify        |  as files, in git    |     |
  |             |     predictions   |  (Ch 43)             |     |
  |             v                   +----------+-----------+     |
  |  +----------+----------+                   |                 |
  |  | ATTRIBUTION         |<------------------+ (6) re-run      |
  |  |  keep / improve /   |                     the benchmark   |
  |  |  rollback-and-pivot |                     (Ch 41)         |
  |  |  (Ch 47)            |                                     |
  |  +---------------------+                                     |
  +--------------------------------------------------------------+
             |
             | (8) NEVER edited by the loop:
             v      the model, the kernel, the verifier,
                    the effect tag, redaction, the graders

  Figure 20.1 -- The two loops (D1 High-Level Architecture)

  (1) the raw material; Ch 16 is what makes it exist
  (2) distillation, roughly 1000:1
  (3) the corpus is READ, progressively (Ch 11 technique)
  (4) one manifest entry per edit, written BEFORE the result
  (5) edits land as file diffs in a git workspace
  (6) the benchmark re-runs on the edited harness
  (7) predictions are checked against observed deltas
  (8) the containment boundary -- section 5.5
```

`[INF]` The two loops run at completely different rates: the inner loop advances a run every few
seconds, the outer loop completes an iteration in hours. That separation is what makes the outer loop
safe to get wrong — a bad iteration costs a benchmark run and a revert, not a production incident,
because nothing it edits is live until it is promoted (Chapter 39).

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  ALGORITHM 1, one iteration                        [AHE section 3.3]

  +--------------------------------------------------------------+
  |                                                              |
  |  0. BASELINE     run the benchmark on harness v_n            |
  |     |              N tasks, k rollouts each (Ch 41)          |
  |     v              -> per-task outcomes, trajectories        |
  |                                                              |
  |  1. ATTRIBUTE    <-- FIRST, not last. Section 4.1            |
  |     |              for each edit in v_n's manifest:          |
  |     |                predicted fixes  n observed fixes?      |
  |     |                predicted at-risk n observed breaks?    |
  |     |              -> verdict per edit:                      |
  |     |                 KEEP | IMPROVE | ROLLBACK_AND_PIVOT    |
  |     v              apply rollbacks NOW                       |
  |                                                              |
  |  2. DISTIL       agent debugger reads the trajectories        |
  |     |              of failures, writes per-task analyses      |
  |     |              plus a benchmark-level overview            |
  |     v              ~10M tokens -> ~10k tokens                 |
  |                                                              |
  |  3. EVOLVE       the Evolve Agent reads the corpus and        |
  |     |              edits components in the workspace.         |
  |     |              For EACH edit it writes a manifest entry   |
  |     |              BEFORE seeing any result:                  |
  |     |                failure evidence                         |
  |     |                root cause                               |
  |     |                the targeted fix                         |
  |     |                PREDICTED fixes  (task ids)              |
  |     |                AT-RISK regressions (task ids)           |
  |     |                constraint level                         |
  |     v                                                        |
  |  4. COMMIT       one git commit per edit: chg-<n>            |
  |     |              -> harness v_(n+1)                         |
  |     v                                                        |
  |  5. LOOP         back to 0 with the new version               |
  +--------------------------------------------------------------+

  Figure 20.2 -- Algorithm 1 (D2 Low-Level Architecture)
```

### 4.1 Attribution runs before distillation, and the order is the design

`[AHE §3.3]` Step 1 comes before step 2, which reads backwards until you see why.

`[INF]` If distillation ran first, the Evolve Agent would read a corpus that still contains failures
caused by the *previous* iteration's bad edits — and would diagnose them as harness defects needing
new fixes, compounding the error. Attributing and rolling back first means the corpus the agent reads
describes a harness whose known-bad changes have already been removed.

The ordering is the difference between a loop that converges and one that accumulates.

```
                                                            LAYER VIEW

  Components, and which chapter builds each.

   trajectories (Ch 16)
        |
        v
   +----+------------+       +---------------------+
   | Agent Debugger  |------>| Evidence corpus     |
   |  Ch 44          |       |  per-task analyses  |
   +-----------------+       |  overview           |
                             +----------+----------+
   +-----------------+                  |
   | Benchmark       |                  v
   | Ch 41           |       +----------+----------+
   |  N tasks x k    |------>| Evolve Agent        |
   +--------+--------+       |  Ch 46              |
            ^                +----+-----------+----+
            |                     |           |
            | re-run              | edits     | writes
            |                     v           v
   +--------+--------+   +--------+----+  +---+-------------+
   | Harness         |<--| Workspace   |  | Change manifest |
   | workspace       |   |  7 types    |  |  Ch 45          |
   | Ch 43           |   |  git        |  +---+-------------+
   +-----------------+   +-------------+      |
            ^                                 v
            |                        +--------+--------+
            +------------------------| Attribution     |
                 rollback            |  Ch 47          |
                                     +-----------------+

   NOT in this diagram, and deliberately:
     the model         selected, never edited (Ch 1)
     the kernel        Ch 18's loop; outside the workspace
     the verifier      Ch 28; the loop may not grade itself
     redaction         Ch 16; outside the workspace
     the effect tag    Ch 14; outside the workspace

  Figure 20.3 -- The outer loop's components (D3 Component Diagram)
```

---

## 5. The Loop

### 5.1 What the seven component types are

`[AHE §3.1]` Chapter 1 introduced them; this is where they become an action space:

| Component | Enforcement | Typical edit |
|---|---|---|
| System prompt | asks | rewording guidance |
| Tool description | asks | Chapter 15's ACI surface |
| Tool implementation | compels | behaviour, error text, output shape |
| Middleware | compels | timeouts, redaction, retry policy |
| Skill | asks, on demand | a packaged procedure |
| Sub-agent configuration | structural | Chapter 19's contracts and subsets |
| Long-term memory | asks | Chapter 12's learned facts |

`[AHE §4.4.1]` measured them individually against a minimal baseline: tools, middleware, and memory
each carried gains, while the system prompt alone regressed by 2.3 points.

`[INF]` Read alongside Chapter 15, that ordering stops being surprising. The components that carried
gains are the ones that change *what the model can perceive and do*; the one that regressed changes
what it is *told*. An evolution loop's action space is therefore most productive at its ACI end,
which is why Phase 2 added Chapter 15 at all.

### 5.2 The change manifest is the load-bearing artifact

`[AHE §3.3]` One entry per edit, written before any result is known:

```json
{
  "change_id": "chg-4",
  "component": "tool_desc",
  "path": "tool_descriptions/repo_find.tool.yaml",
  "failure_evidence": ["task_112 step 7", "task_203 step 4"],
  "root_cause": "description says 'directory path'; implementation
                 takes a glob. Model passes paths, gets empty results,
                 concludes the directory is empty.",
  "targeted_fix": "state that the parameter is a glob; add a
                  counter-example; add empty_means.",
  "predicted_fixes": ["task_112", "task_203", "task_318"],
  "at_risk": ["task_090"],
  "constraint_level": "tool_desc"
}
```

`[INF]` `predicted_fixes` and `at_risk` are what convert an edit from an opinion into a claim. The
cold open had neither: six edits, one aggregate number, no way to attribute. With them, the next
iteration intersects predictions against observed per-task deltas and produces a verdict per edit —
which is Chapter 47, and which is impossible without this file.

The manifest is also the loop's only durable reasoning. Everything else the Evolve Agent thought is
in a trajectory nobody will read; the manifest is what a human reviews.

### 5.3 Constraint level: fix at the weakest level that enforces

`[AHE §3.3]` Every edit declares which component class it targets, and the classes form a hierarchy
by enforcement strength (Chapter 1).

`[INF]` The rule from Chapter 15 §5.5, generalised: **fix at the weakest level that can actually
prevent the failure.** A model ignoring an instruction is not fixed by a firmer instruction; it is
fixed by middleware that makes the instruction unnecessary. The anti-pattern the paper names is
repeatedly fixing at the wrong level — three iterations of prompt rewording for something a five-line
middleware would have settled.

### 5.4 What the loop measures, and why it is hard

Chapter 41 builds this properly. The shape:

| Quantity | Why it is difficult |
|---|---|
| `pass@1` per task | the system is non-deterministic; one rollout is noise |
| k rollouts per task | k is a cost multiplier on every iteration |
| Aggregate score | small samples move for reasons unrelated to the edit |
| Cost per task | an edit that improves quality by spending more is not an improvement |

`[AHE App. A]` records tokens per trial and success per million tokens as first-class metrics.
`[INF]` Chapter 13's cold open is the reason: a loop optimising an under-reported denominator prefers
harnesses that abandon calls. Cost-normalised scoring is not a refinement; it is what stops the loop
finding the wrong optimum.

### 5.5 The containment boundary

`[AHE §3.3]` The Evolve Agent writes only inside the harness workspace. The runs directory, the
tracer, the verifier, and the model configuration are read-only.

`[INF]` Three chapters have now arrived at the same boundary independently, and the convergence is
the strongest argument in this chapter:

| Chapter | Outside the workspace | Because an outcome-based reward would |
|---|---|---|
| 12 Memory | abstraction at write time | prefer specific memories; they perform better and they leak |
| 13 Reasoning | model id and effort tier | raise the tier and spend more for a better score |
| 14 Tools | the effect tag | re-tag effectful as pure to remove a slow gate |
| 16 Observation | redaction rules | keep more context; it explains more |
| 19 Multi-agent | widening a tool subset | give a search agent write access to be "more capable" |
| 28 Grading | the verifier | grade itself more generously |

Every row is a locally correct optimisation that removes a protection. `[INF]` None of them is
malicious and none requires the agent to be deceptive — each is exactly what a competent engineer
would do if their only feedback signal were the benchmark score. The boundary exists because the
reward signal cannot represent what is being protected, and Chapter 49 is about governing it.

### 5.6 What the ten-iteration result does and does not show

`[AHE §4.2]` Ten iterations of editing nothing but harness components moved single-attempt success
from 69.7% to 77.0%, with the base model identical throughout.

`[INF]` What it establishes: harness quality is a large, measurable performance surface, and an
automated loop can improve it unattended. That is a substantial result and it is the premise of
Level 5.

What it does not establish: that the gains compound indefinitely, that they transfer across models or
benchmarks, or that the loop can be trusted without review. `[AHE §4.4.1]` reports that effective
edits do not stack — three positive single-component gains summing to +11.1 points yielded +7.3
together — and `[AHE §4.4.2]` reports fix-prediction running about 5× better than random while
regression-prediction managed only about 2×.

`[INF]` The second figure is the one to carry through Levels 3 and 4: **the loop is much better at
predicting what it will fix than what it will break.** Chapter 48 is about designing around a
process that cannot see its own damage, and it is the reason Chapter 47's rollback is automatic
rather than advisory.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  benchmark   attribution   debugger   evolve agent   workspace   git
      |            |            |           |             |        |
  ITERATION n                                                      |
      |-- run 200 tasks x 3 rollouts on harness v_n                |
      |   -> per-task outcomes + trajectories (Ch 16)              |
      |            |            |           |             |        |
      |-- outcomes ->|          |           |             |        |
      |            | for each edit in v_n's manifest:              |
      |            |   chg-1 predicted {112,203,318}               |
      |            |         observed fixed {112,203}  -> KEEP     |
      |            |   chg-2 predicted {077}                       |
      |            |         observed fixed {} , broke {091}       |
      |            |                          -> ROLLBACK_AND_PIVOT|
      |            |-- revert chg-2 -------------------->|-------->|
      |            |            |           |             |        |
      |-- failing trajectories ->|          |             |        |
      |            |            |  reads 9.4M tokens      |        |
      |            |            |  writes per-task analyses        |
      |            |            |  + overview: ~11k tokens|        |
      |            |            |-- corpus ->|             |        |
      |            |            |           | reads progressively  |
      |            |            |           | (Ch 11 technique)    |
      |            |            |           |             |        |
      |            |            |           |-- edit chg-5 ------->|
      |            |            |           |   manifest entry FIRST|
      |            |            |           |   predicted {112,318}|
      |            |            |           |   at_risk   {090}    |
      |            |            |           |-- commit ---------->|
      |            |            |           |             |        |
  ITERATION n+1                                                    |
      |-- run the same 200 tasks on harness v_(n+1) --------------->|
      |   ... and chg-5's predictions are checked HERE, not now     |

  Figure 20.4 -- One iteration (D4 Sequence)
```

### 6.1 The prediction is checked one iteration later

`[INF]` The property that makes the manifest work: an edit's claim is written in iteration *n* and
verified in iteration *n+1*. The Evolve Agent cannot see the result when it writes the prediction,
which is what makes the prediction falsifiable rather than a description.

The cold open's team predicted nothing and measured once. This loop predicts every time and measures
every time, and the difference is not diligence — it is that one produces attributable information
and the other produces a single number.

```
                                                             TIME VIEW

  The outer loop.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | benchmark on v_n     |  Ch 41                        |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | ATTRIBUTE first      |  Ch 47; rollbacks applied NOW |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     /score \  regressed badly -> E1 halt for review      |
     \ delta?/                                            |
      \     /                                             |
        | acceptable                                      |
        v                                                 |
   +----+-----------------+                               |
   | distil evidence      |  Ch 44                        |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     /new    \  no ------------------------------> E2 dry |
     \failures?/                                          |
      \       /                                           |
        | yes                                             |
        v                                                 |
   +----+-----------------+                               |
   | edit + manifest      |  Ch 45, Ch 46                 |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     /budget \  exhausted -> E3 stop                      |
     \ left?  /                                           |
      \      /                                            |
        | yes                                             |
        +-------------------------------------------------+

  Exits:
    E1  a large regression -> halt; a human reviews (Ch 49)
    E2  no new failures found -> converged, for this benchmark
    E3  iteration budget exhausted -> stop and report

  Figure 20.5 -- The outer loop and its exits (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

  A harness version's lifecycle. This is git, with verdicts attached.

            +---------------------+
            | {{ PROPOSED }}      |  edits made; manifest written;
            +----------+----------+  NOT yet measured
                       | benchmark runs
                       v
            +---------------------+
            | {{ MEASURED }}      |  per-task outcomes exist
            +----+-----------+----+
                 |           |
   predictions   |           | predictions failed, or
   held          |           | at-risk tasks broke
                 v           v
        +--------+----+  +---+--------------------+
        | {{ KEPT }}  |  | {{ ROLLED BACK }}      |
        +------+------+  +---+--------------------+
               |             |
               |             | the agent PIVOTS: a different
               |             | root cause, at a different
               |             | constraint level (section 5.3)
               v             v
        +------+-------------+----+
        | {{ BASELINE for n+1 }}  |
        +-------------------------+

  {{ IMPROVE }} is a third verdict: the edit helped partially, and
  the next iteration refines it rather than reverting or keeping.

  Illegal:
    * PROPOSED -> KEPT without measurement   -- the cold open
    * rolling back without recording why     -- the pivot needs it
    * editing outside the workspace          -- section 5.5
    * a manifest entry written after results -- section 6.1

  Figure 20.6 -- A harness version's states (D6 State Diagram)
```

### 7.1 Harness state, at a different timescale

Chapter 6 classified harness components as **harness state**: outliving any run, without being facts
about the world. This chapter is that category's other consumer.

`[INF]` Chapter 12's long-term memory is harness state edited by a *run*, in seconds. Everything here
is harness state edited by an *iteration*, in hours. The same category, two writers, two timescales —
and the same governance question, which is why Chapter 12's abstraction rule and §5.5's containment
boundary are the same idea.

### 7.2 A run pins its harness version

Chapter 8 §14's rule, now load-bearing. A run pins the harness version at claim and completes under
it, so a benchmark run measures one configuration rather than a mixture.

`[INF]` Without the pin, an iteration that deploys mid-benchmark produces rollouts partly on v_n and
partly on v_(n+1), and every attribution downstream is comparing a blend against a blend. The pin is
four bytes on a row and it is what makes the outer loop measurable at all.

---

## 8. Internal APIs

```python
from typing import Protocol


class EvolveLoopPort(Protocol):
    """One iteration of Algorithm 1. Built in Level 5; named here so
    Levels 3 and 4 can declare what they owe it."""

    async def iterate(self, baseline: HarnessVersion) -> IterationReport:
        """Benchmark, ATTRIBUTE FIRST (section 4.1), distil, edit, commit.

        Halts and raises RegressionHalt when the aggregate drop exceeds
        the configured threshold: E1, a human reviews (Ch 49).
        """


class ManifestPort(Protocol):
    """The change manifest. Append-only; entries are written BEFORE
    results exist and are never edited afterwards (section 6.1)."""

    async def record(self, entry: ChangeEntry) -> None: ...

    async def verdicts_for(
        self, version: HarnessVersion, observed: TaskDeltas
    ) -> dict[ChangeId, Verdict]:
        """Intersect each entry's predicted_fixes and at_risk with what
        was observed. This is Ch 47, and it is impossible without the
        predictions having been recorded in advance."""
```

`[INF]` `record` having no update method is the enforcement of §6.1. A manifest entry that could be
edited after results arrived would let the loop revise its prediction to match the outcome — which is
not dishonesty so much as the obvious way to make a metric go up, and exactly what the
write-before-measure ordering exists to prevent.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class ConstraintLevel(StrEnum):
    MIDDLEWARE = "middleware"      # compels
    TOOL_IMPL = "tool_impl"        # compels
    SUB_AGENT = "sub_agent"        # structural
    TOOL_DESC = "tool_desc"        # asks, but shapes perception
    SKILL = "skill"                # asks, on demand
    MEMORY = "memory"              # asks, with evidence
    PROMPT = "prompt"              # asks, weakest (AHE 4.4.1)


class Verdict(StrEnum):
    KEEP = "keep"
    IMPROVE = "improve"
    ROLLBACK_AND_PIVOT = "rollback_and_pivot"


@dataclass(frozen=True)
class ChangeEntry:
    change_id: str                      # chg-<n>, scoped to an iteration
    component: ConstraintLevel
    path: str
    failure_evidence: tuple[str, ...]   # task + step references
    root_cause: str
    targeted_fix: str
    predicted_fixes: tuple[str, ...]    # task ids -- the CLAIM
    at_risk: tuple[str, ...]            # task ids -- the honest half
    commit_sha: str


@dataclass(frozen=True)
class IterationReport:
    version: HarnessVersion
    score: float
    cost_per_task_cents: int            # section 5.4: not optional
    verdicts: Mapping[str, Verdict]
    fix_prediction_precision: float     # ~5x random (AHE 4.4.2)
    regression_prediction_precision: float   # ~2x random
```

`[INF]` `at_risk` is the field that separates this from optimisation. An agent that only predicts
successes has written an advertisement; one that also names what it might break has written a
hypothesis. `[AHE §4.4.2]`'s finding that regression prediction is weak is *measured from this
field* — the loop knows it is bad at this because it wrote down its guesses and they were checked.

---

## 10. Communication

```
                                                            LAYER VIEW

  trajectories   trace store ====> debugger      ~10 MB per run,
                                                  ~9-12M tokens/batch
  corpus         debugger    ====> evolve agent  ~10-15k tokens
                                                  <-- ~1000:1
  edits          evolve      ====> workspace     ~1-20 KB per edit
  manifest       evolve      ====> git           ~2 KB per entry
  outcomes       benchmark   ====> attribution   ~50 KB per iteration

  Figure 20.7 -- The outer loop's volumes (D7 Data Flow)
```

```
                                                             TIME VIEW

  benchmark ------> attribution   outcomes, per task
  attribution ----> workspace     rollbacks, applied FIRST
  debugger -------> evolve agent  the corpus, read progressively
  evolve agent ---> workspace     edits, inside the boundary only
  evolve agent --X  the model     REFUSED (Ch 1, Ch 13)
  evolve agent --X  the kernel    REFUSED (Ch 18)
  evolve agent --X  the verifier  REFUSED (Ch 28)
  evolve agent --X  its own manifest, after results   REFUSED (6.1)

  Figure 20.8 -- Who may change the harness (D8 Control Flow)
```

```
                                                             TIME VIEW

  << harness.version.committed >> ....> one per edit; the git sha
  << iteration.completed >>       ....> score, cost, verdicts
  << change.verdict.assigned >>   ....> keep / improve / rollback
  << evolution.halted >>          ....> E1: a regression a human
                                        must look at (Ch 49)

  Figure 20.9 -- What evolution makes durable (D9 Event Flow)
```

### 10.1 What Levels 3 and 4 owe this chapter

The reason it is placed here rather than at Chapter 42:

| Chapter | Owes the loop |
|---|---|
| Ch 28 Grading | a verdict the loop may not influence |
| Ch 34 Observability | per-component metrics, and flow-tagged spans |
| Ch 37 Tenancy | redaction the loop cannot widen |
| Ch 38 Deployment | harness version pinned per run (§7.2) |
| Ch 39 GitOps | file-level diffs and revert as a first-class operation |
| Ch 40 Testing | hermetic replay, so a rollback can be trusted |
| Ch 41 Evaluation | a stable, cost-normalised score |

`[INF]` Every row is something a reader would otherwise build for general reasons and size wrongly.
Knowing the loop is coming changes how each is specified — most sharply Chapter 41, which is the
difference between a benchmark you run occasionally and one an automated process depends on.

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| No per-edit predictions | changes shipped in a batch | a score that moved and cannot be attributed | the manifest — the cold open |
| Manifest written after results | convenience | predictions that always look correct | append-only; write before measuring |
| Distil before attribute | the natural reading order | errors compounding across iterations | attribute first (§4.1) |
| Optimising an uncosted score | quality measured, spend not | scores rising with cost rising faster | cost-normalised metrics (§5.4) |
| Fixing at the wrong level | prompt edits for enforcement problems | repeated edits to one prompt, same failure | constraint level (§5.3) |
| Editing outside the workspace | a broader action space "to be effective" | protections quietly disappearing | the boundary (§5.5) |
| Trusting stacked gains | summing per-component measurements | predicted total exceeding measured | gains do not stack `[AHE §4.4.1]` |
| Trusting regression prediction | treating `at_risk` as reliable | breaks in tasks nobody flagged | ~2× random; rollback is automatic |
| Loop runs on production | no separation of measurement and serving | a bad iteration reaching users | promote explicitly (Ch 39) |
| Corpus contains secrets | redaction at read rather than capture | an automated reader with broad access | Chapter 16 §5.4 |

`[INF]` Row seven deserves the emphasis. Measuring three components individually and adding the
results overestimated the combination by nearly four points in the reported data. Any plan built on
"we measured these five improvements, so together they give us X" is making an assumption the source
has already falsified.

---

## 12. Scalability

### 12.1 An iteration is expensive, and that sets everything

```
  200 tasks  x  3 rollouts  x  ~1.2M tokens/rollout   =  ~720M tokens
                                                          per iteration
```

`[INF]` So the loop's cost is dominated entirely by the benchmark, not by the Evolve Agent's own
reasoning, which is a rounding error by comparison. Three consequences follow:

- **k is the expensive dial.** Rollouts per task trade variance against cost linearly, and Chapter 41
  is largely about spending them well.
- **Distillation is nearly free.** Reading ten million tokens once per iteration costs a fraction of
  one rollout, which is why the debugger can afford to be thorough.
- **Benchmark size bounds iteration count.** A fixed evolution budget divides into iterations; more
  tasks per iteration means fewer iterations.

### 12.2 The loop does not scale by running it harder

`[INF]` Because gains do not stack (§5.6) and regression prediction is weak, doubling the iteration
count does not double the improvement. The reported curve flattens. The realistic reading is that the
loop is a way to keep pace with base-model churn and to harvest a bounded set of harness improvements
— not an unbounded optimiser.

Chapter 48 is the chapter that says this properly; it is worth carrying the expectation from here.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Score and cost per task, together | §5.4: quality bought with spend is not quality | either moving alone |
| Fix-prediction precision | is the loop learning to aim | falling toward random |
| Regression-prediction precision | ~2× random is the baseline | reported, expected to be poor |
| Verdict distribution | mostly rollbacks means bad aiming | rollback share rising |
| Constraint-level distribution | §5.3's anti-pattern | prompt edits dominating |
| Iterations since the last KEEP | convergence, or being stuck | rising |
| Edits outside the workspace | should be structurally impossible | any non-zero is an incident |

### 13.2 What to build before the loop

`[INF]` The honest prerequisite list, in order, since this chapter arrives twenty-nine chapters early
precisely so it can be built into the plan:

1. **Trajectories that capture inputs** (Chapter 16). Without them the loop edits prompts.
2. **Components as files in git** (Chapter 43). Without them there is no action space.
3. **A stable, cost-normalised benchmark** (Chapter 41). Without it, noise.
4. **Hermetic replay** (Chapter 40). Without it, a rollback cannot be trusted.
5. **The manifest** (Chapter 45). Without it, the cold open.

Items 1 and 2 are cheap if designed in and expensive to retrofit. Item 3 is the one teams
underestimate, and Chapter 41 explains why.

---

## 14. Relation to AHE

This chapter *is* the relation, so the section inverts: what does the base runtime owe the loop, and
what does the loop owe the runtime?

**The runtime owes it separability.** Every containment boundary in §5.5 was arrived at
independently, by a chapter solving its own problem, and they turn out to be one property: the
components that must not be editable are exactly those whose protection the reward signal cannot
represent.

**The runtime owes it measurability.** Pinned harness versions, bounded runs, recorded exit
conditions, and cost attached to every rollout. Each is a Level 1 or 2 decision that looked like
ordinary hygiene and is in fact a precondition.

**The loop owes the runtime restraint.** `[INF]` It runs on a benchmark, not on production traffic;
it proposes rather than deploys; and its output is a git commit that a promotion pipeline (Chapter
39) moves forward. The two loops are separated by a human decision, and Chapter 49 is about when that
separation may be relaxed and what has to be true first.

**And both owe the reader honesty about the state of the art.** `[AHE Limitations]` is explicit that
this is a controlled prototype: one benchmark family, a bounded iteration count, non-additive gains,
and weak regression prediction. `[INF]` The correct posture entering Level 3 is that the loop is
real, measured, useful, and considerably less finished than the architecture around it.

---

## 15. Industry Perspective

**`[AHE]`** Supplies essentially all of the mechanism: the three observability pillars, Algorithm 1
and its phase ordering, the seven component types, the change manifest and its fields, the
constraint-level hierarchy, controllability constraints, the 69.7% to 77.0% ten-iteration result, the
non-additivity finding, and the fix- and regression-prediction precisions
`[AHE §3.1–3.3, §4.2, §4.4.1, §4.4.2, Limitations]`.

**`[DAR]`** Supplies the runtime the loop edits and the properties that make it measurable: pinned
configuration, bounded runs, and the port structure that makes components separable `[DAR §2.2]`.

**`[INF]`** The handbook's own: the clinical-trial framing and its explicit breaking point, the
derivation that three pillars are each necessary, the observation that six independently-derived
containment boundaries are one property, the argument that the loop's action space is most productive
at its ACI end, the prerequisite ordering in §13.2, and the framing of the loop as pace-keeping
against model churn rather than unbounded optimisation.

**`[BP]`** Pre-registration of hypotheses is standard in clinical research and increasingly in
empirical computer science. The contribution here is applying it to automated configuration search,
where the pre-registration is machine-written and machine-checked.

**`[FUT]`** `[FUT]` The loop as described improves one harness against one benchmark family. Whether
improvements transfer across benchmarks, across products, or across model families is unmeasured, and
the handbook treats any claim of transfer as speculative until Chapter 48's limits are addressed.

---

## 16. Key Takeaways

1. **An edit is a falsifiable claim.** Write the prediction before the evidence arrives, or a score
   that moves carries no information about which change earned it.
2. **Three pillars, all required.** Component observability gives an action space, experience
   observability gives evidence, decision observability gives attribution. Remove one and the loop
   cannot aim, cannot see, or cannot learn.
3. **Attribute before you distil.** Otherwise the corpus still contains failures caused by the last
   iteration's bad edits, and the loop diagnoses its own damage as new defects.
4. **Fix at the weakest level that enforces.** Repeated prompt edits for something middleware would
   settle is the named anti-pattern, and the prompt is the component that measured *worse* than
   nothing.
5. **Six chapters arrived at the same boundary independently.** Memory abstraction, model config,
   effect tags, redaction, tool subsets, and the verifier are all outside the workspace — because in
   each case a locally correct optimisation would remove a protection the reward cannot represent.
6. **Gains do not stack.** Three edits summing to +11.1 points delivered +7.3 together. Any roadmap
   that adds up measured improvements is using an assumption the data contradicts.
7. **The loop predicts fixes far better than regressions.** About 5× random versus about 2×. It
   cannot see what it is about to break, which is why rollback is automatic rather than advisory.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Outer loop** | The iteration that edits the harness, running in hours, as distinct from the runtime loop that advances a run in seconds. | `[AHE]` | Ch 46 |
| **Algorithm 1** | Benchmark, attribute, distil, edit, commit — with attribution deliberately before distillation. | `[AHE]` | Ch 47 |
| **Component observability** | The harness as separable files, so an edit has somewhere specific to land. | `[AHE]` | Ch 43 |
| **Experience observability** | Trajectories distilled into a navigable evidence corpus the loop can afford to read. | `[AHE]` | Ch 44 |
| **Decision observability** | Every edit paired with a prediction recorded before the result, making it checkable. | `[AHE]` | Ch 45 |
| **Change manifest** | The append-only record of each edit: evidence, root cause, fix, predicted fixes, at-risk tasks, constraint level. | `[AHE]` | Ch 45, Ch 47 |
| **Predicted fixes** | The task ids an edit claims it will repair; the half of the claim that is easy to write. | `[AHE]` | Ch 47 |
| **At-risk tasks** | The task ids an edit might break; the honest half, and the one the loop is measurably bad at. | `[AHE]` | Ch 47, Ch 48 |
| **Constraint level** | Which component class an edit targets, ordered by enforcement strength. | `[AHE]` | Ch 46 |
| **Verdict** | Keep, improve, or rollback-and-pivot, assigned by intersecting predictions with observed deltas. | `[AHE]` | Ch 47 |
| **Controllability** | The constraint that the Evolve Agent writes only inside the harness workspace. | `[AHE]` | Ch 46, Ch 49 |
| **Containment boundary** | The set of components deliberately outside the workspace because an outcome-based reward would remove their protection. | `[INF]` | Ch 46, Ch 49 |
| **Non-additivity** | The measured finding that individually effective edits deliver less together than the sum of their separate gains. | `[AHE]` | Ch 48 |

---

**Level 2 is complete.** You can now build every component the runtime needs and say what each owes
the others. Level 3 takes the same system and makes it survive: durability, the event spine,
scheduling, task graphs, failure and rollback, grading, human authority, safety, and distribution
across many workers.

**Next:** *Interlude I — Assembling a Minimal Runtime.* Before Level 3 adds depth, a narrative pass
that builds stages 0 through 2 of the architecture roadmap end to end, so the pieces of Level 2 are
seen fitting together rather than described one at a time.
