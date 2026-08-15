```
  Level 5 · Chapter 47
  ATTRIBUTION, VERDICTS, AND ROLLBACK
  Requires   C27 Failure, Recovery, and Rollback, C40 Testing,
             C41 Evaluation Infrastructure,
             C45 Decision Observability, C46 The Evolve Agent
  Unlocks    C48 Limits,
             C49 Continuous Improvement and Governance
  Diagrams   Core (5)
```

# Chapter 47 — Attribution, Verdicts, and Rollback

---

## 1. Motivation

### 1.1 Cold open

Iteration 12 ships six edits. The next benchmark run improves seven tasks.

Attribution runs. `chg-4` predicted {112, 203, 318}; all three improved. Verdict KEEP, precision 1.0,
and it is the iteration's best-scoring edit — a rewritten tool description, retained.

Four iterations later somebody notices that the pattern `chg-4` targeted is still in the evidence
corpus, unchanged, with the same thirty-one tasks in it. If a description fix had worked, the pattern
should have shrunk.

They probe it. Reverting `chg-4` on its own costs nothing measurable.

What had moved 112, 203, and 318 was `chg-6` — a middleware hook shipped in the same iteration that
widened a context budget. All three were marginal on context. All three were also, coincidentally, in
the set `chg-4` named.

`chg-6` predicted {077}, got it, and was credited with one task instead of four.

Both verdicts were arithmetically correct. Six edits, one measurement, and the intersection assigned
credit to whichever entry happened to name the tasks that moved.

### 1.2 In plain language

An iteration makes several changes at once and then measures once. Deciding which change deserves the
credit is the hard part, and it is harder than it looks.

The method is straightforward: each change said in advance which tasks it would fix, so compare that
list against the tasks that actually improved. Where they overlap, the change worked.

The problem is that overlap is not proof. Two changes shipped together can both plausibly explain the
same improvement, and the arithmetic will hand the credit to whichever one happened to name those
tasks — not to whichever one caused it. The result is a number that is correct and a conclusion that
is wrong.

That matters more here than in most places, because the conclusion is not a report. It is an action.
A change judged to have worked stays in the system; a change judged to have failed is removed
automatically. So a mistake does not produce a misleading dashboard — it changes what the system is.

This chapter is about doing the comparison honestly, knowing when it cannot decide, and undoing a
change safely when it should be undone.

### 1.3 Why this chapter exists

Everything Level 5 has built converges here. Chapter 43 addressed the edits, Chapter 44 supplied the
evidence, Chapter 45 made each edit a claim with an enumerated set, and Chapter 46 constrained where
they may land. This is the step that reads a result and decides what to do about it.

`[AHE §3.3]` supplies the mechanism: intersect each entry's predicted fixes and at-risk tasks with the
observed per-task deltas, and assign keep, improve, or rollback-and-pivot. `[INF]` The chapter's
contribution is what the source's method underdetermines. **Six edits and one measurement do not
determine six verdicts**, and an intersection that always returns an answer will always return one —
including when the evidence cannot support it.

Three earlier chapters left preconditions here and each is load-bearing. Chapter 41 supplied the noise
floor and the distinction between *this helped* and *this was inside the floor and we kept it anyway*.
Chapter 40 supplied the reason automatic rollback is safe at all: a measured regression must be real,
which requires a runtime that is stable when nothing changed. Chapter 27 §5.4 supplied the limit —
reverting a harness edit restores the code, not the world the code acted on.

### 1.4 What previous framings got wrong

**"The intersection is the attribution."** It is the *arithmetic* of attribution. The cold open's two
verdicts were both correct intersections and both wrong about the system, because two edits can
explain one improvement and only one of them named it.

**"A verdict is a report."** It is an action with a side effect on the harness. KEEP retains an edit;
ROLLBACK removes one. `[INF]` That is why the tolerance for an unresolvable case must be a fourth
value rather than a default — arithmetic that cannot say *underdetermined* will say something else.

**"A measured regression means the edit regressed."** Chapter 40 §14: a loop attached to a flaky
runtime will attribute intermittent failures to whatever edit happened to be under test. Automatic
rollback is a mechanism for acting on measurements without review, so it inherits every defect in the
measurement.

**"Rollback undoes the edit, so nothing is at risk."** It restores the workspace. Chapter 27 §5.4 is
explicit that a trial which opened a pull request has produced an effect no git revert touches, and
the answer is a constraint on trials rather than a better rollback (§5.6).

**"More edits per iteration means faster progress."** It means more confounding per measurement. `[INF]`
The cold open is six edits deep; at two edits it would probably not have happened, and the trade
between iteration throughput and attribution quality is a real dial nobody sets deliberately (§12).

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Marketing attribution.

An advertiser runs six campaigns at once and a customer buys something. Which campaign earned it? The
industry has spent decades on this and the honest summary is that every model is partly wrong.
Last-click attribution — credit whichever touch happened to be last — is the simplest, the most
common, and structurally identical to the cold open: it assigns credit by *coincidence of position*
rather than by cause, and it systematically over-credits whatever tends to come last.

The whole vocabulary transfers. Multi-touch models, incrementality testing, holdouts, and the
recurring discovery that the channel everyone believed was working was mostly claiming credit for
demand that already existed.

**Where it breaks**, in two ways, and the second one is why this chapter is careful.

Marketing can run **holdouts** at almost no cost, because impressions are cheap and there are millions
of them. Suppress a campaign in one region, compare, and the causal question is answered directly.
The equivalent here exists and is priced differently: Chapter 43's disablement probe is exactly a
holdout, and it costs one full benchmark run per edit. `[INF]` So the clean answer is available and
cannot be run routinely, which makes the entire chapter an exercise in deciding when to spend it.

And a marketing attribution error is **symmetric and cancels**. Over-crediting one channel and
under-crediting another leaves total spend efficiency unchanged, and the report is wrong in a way that
averages out. Here the error does not cancel, because the verdict is an action: the over-credited edit
is kept and the under-credited one may be rolled back. `[INF]` The system diverges from the one the
measurement described, and the next iteration reasons about a harness that nobody intended.

### 2.2 Why attribution must run first, and must be able to abstain

```
  (1) An iteration ships N edits and produces ONE measurement.

  (2) Each edit carries an enumerated predicted set (C45), so
      credit can be assigned by intersection.

  (3) That is sound only if the predicted sets are DISJOINT and
      effects land where they were predicted. Neither is
      guaranteed, and the cold open is both failing at once.

  (4) So the arithmetic must be able to return UNDETERMINED.
      An intersection that always produces a verdict will
      produce one for cases the evidence cannot decide.

  (5) Verdicts are ACTIONS. Keep retains an edit; rollback
      removes one. An error changes the system rather than the
      report, and the next iteration reasons about the changed
      one.

  (6) Rollback must be AUTOMATIC, because the loop predicts what
      it will break at roughly twice random [AHE 4.4.2] and
      therefore cannot be relied on to notice its own damage.

  (7) Automatic rollback must therefore be SAFE, which requires
      that a measured regression is real -- a stable runtime
      (C40) and a known noise floor (C41). Without both, the
      loop reverts good edits on runtime flakiness.

  (8) And all of it must run BEFORE distillation. Otherwise the
      corpus the next iteration reads still contains failures
      caused by edits already known to be bad, and they are
      diagnosed as fresh defects (C20 sec 4.1).

  Attribute, roll back, then distil. The ordering is the design,
  and step (4) is the part the source's method leaves implicit.
```

Step (4) is where this chapter departs from a straightforward reading of the source. `[INF]` An
intersection is a total function — it returns a number for every input — and the temptation is to let
that number be the verdict. The cold open is what that produces: two confident, arithmetically valid,
causally wrong decisions, both of which changed the harness.

### 2.3 Four things the intersection cannot tell apart

The chapter's analytical spine. An edit whose predicted tasks improved is in one of four states, and
the raw intersection gives the same answer for all four.

| State | What happened | Disambiguated by |
|---|---|---|
| **Real** | The edit caused the improvement, through the claimed mechanism | The pattern disappeared from the corpus (Ch 44 §7.2) |
| **Inside the floor** | The movement is smaller than the benchmark can resolve | The floor, per slice (Ch 41 §4.1) |
| **Credited** | Another edit in the same iteration caused it | Disjointness (§5.3), then a probe (Ch 43 §5.3) |
| **Right for the wrong reason** | It worked, through a mechanism it did not claim | The pattern persisted while the tasks passed (§5.2) |

`[INF]` Only one of the four is a bug in the loop, and Chapter 41 §5.7 named it in advance: keeping an
edit whose movement was inside the floor. The other three are the measurement being harder than the
arithmetic, and treating them as loop defects sends a team looking for a fault that is not there.

Read the fourth row carefully, because it is the one that sounds like pedantry and is not. An edit
that improves the right tasks through an unclaimed mechanism is Chapter 43 §5.2's overlap arriving in
the verdict: something else was compensating, the edit changed which component owns a behaviour, and
the score moved for a reason nobody recorded. Chapter 44's disappearance check is what separates it
from the first row, and it costs nothing.

### 2.4 The mental model to carry

> **A verdict is an action, not a report.** Arithmetic that cannot say *undetermined* will always say
> something — and whatever it says, the harness changes to match.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   BENCHMARK ON v_n (C41)          MANIFEST (C45)
   +---------------------+         +---------------------------+
   | per-task outcomes   |         | sealed entries for v_n:    |
   | with the floor      |         |  predicted sets + widths   |
   | per slice           |         |  at_risk sets              |
   +----------+----------+         |  the null claims           |
              |                    +-------------+-------------+
              | (1) observed                      | (2) claimed
              v                                   v
   +--------------------------------------------------------------+
   |                       ATTRIBUTION                            |
   |                                                              |
   |   intersect predicted with observed, PER ENTRY               |
   |   check each delta against its slice floor (C41)             |
   |   check disjointness across the iteration's entries (5.3)    |
   |   check the MECHANISM: did the pattern disappear? (C44 7.2)  |
   +---------------------------+----------------------------------+
                               | (3) a verdict, with a confidence
                               v
   +--------------------------------------------------------------+
   |   KEEP        IMPROVE        ROLLBACK_AND_PIVOT   UNDETERMINED|
   +------+--------------+---------------+--------------+---------+
          |              |               |              |
          |              |               | (4) revert   | (5) probe,
          |              |               v              |     or carry
          |              |    [[ workspace ]] (C39)     |     forward
          |              |     file-level, one commit   |
          |              |                              |
          |              v                              v
          |    the next iteration refines      one benchmark run
          |    rather than reverting            to disambiguate
          v                                    (C43 sec 5.3)
   +--------------------------------------------------------------+
   |   ONLY THEN: DISTILLATION (C44)                              |
   |   the corpus is built from a harness whose known-bad edits    |
   |   have already been removed (C20 sec 4.1)                     |
   +--------------------------------------------------------------+

  Figure 47.1 -- Attribution between the benchmark and the corpus
                 (D1 High-Level Architecture)

  (1) per-task, never aggregate: a slice-level number cannot be
      intersected with a task-level claim
  (2) sealed before the run that produced (1) -- which is what
      makes this an intersection rather than a rationalisation
  (3) a confidence, because 2.3's four states are not
      distinguishable from the intersection alone
  (4) rollback is automatic (2.2 step 6) and file-level (C39)
  (5) the fourth verdict is not a failure of the loop; it is the
      arithmetic declining to guess
```

### 3.1 The phase boundary at the bottom is the whole of Chapter 20 §4.1

`[AHE §3.3]` Algorithm 1 attributes before it distils, and it reads backwards until the reason is
visible in this figure. `[INF]` The corpus is built from the failures of a benchmark run on `v_n`. If
`chg-2` in `v_n` broke four tasks, those four failures are in that run's trajectories — and if the
corpus is built before `chg-2` is reverted, the next iteration reads four failures caused by a change
already known to be bad and diagnoses them as fresh defects.

The rollbacks are applied *now*, between the measurement and the distillation. `[INF]` That does not
remove the failures from the trajectories, which is worth being precise about — it removes them from
the workspace, so the *next* benchmark run does not reproduce them, and the distiller is told which
task outcomes are attributable to reverted edits so it can exclude them. Both halves are needed; only
the first is obvious.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                        ATTRIBUTION                             |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Intersector            |  |   Floor check             |   |
   |  |                          |  |                           |   |
   |  |  predicted n observed    |  |  every per-task delta      |   |
   |  |  at_risk    n broken     |  |  against ITS SLICE floor   |   |
   |  |                          |  |  (C41 sec 4.1)             |   |
   |  |  reports the intersection|  |                            |   |
   |  |  AND the width it was    |  |  inside the floor is not   |   |
   |  |  taken over (C45 sec 5.3)|  |  a small effect; it is NO  |   |
   |  |                          |  |  MEASUREMENT (C41)         |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Disjointness check     |  |   Mechanism check         |   |
   |  |                          |  |                           |   |
   |  |  do two entries in this  |  |  did the targeted pattern |   |
   |  |  iteration name the same |  |  DISAPPEAR from the next  |   |
   |  |  task? (5.3)             |  |  corpus? (C44 sec 7.2)    |   |
   |  |                          |  |                           |   |
   |  |  if so, BOTH verdicts    |  |  free, structural, and    |   |
   |  |  are guesses -- the cold |  |  the only cheap separator |   |
   |  |  open                    |  |  of "real" from "credited"|   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Verdict assigner       |  |   Rollback executor       |   |
   |  |                          |  |                           |   |
   |  |  four values, and the    |  |  file-level revert (C39); |   |
   |  |  fourth is UNDETERMINED  |  |  the entry is MARKED, not |   |
   |  |  (2.2 step 4)            |  |  deleted (C45 sec 7.1)    |   |
   |  +--------------------------+  +---------------------------+   |
   +----------------------------------------------------------------+

  Figure 47.2 -- Inside attribution (D2 Low-Level Architecture)
```

### 4.1 Inside the floor is not a small effect

The floor check deserves emphasis because the mistake is natural and it is Chapter 41 §5.7's named
loop bug.

`[INF]` A delta of +1.2 points against a slice floor of 6.0 is not a weak improvement. It is *no
measurement*, and treating it as a weak positive is exactly what makes a loop climb noise. The
distinction is binary and the arithmetic must treat it that way: outside the floor, the delta is
evidence; inside it, there is nothing to reason about.

`[BP]` So the verdict for an inside-floor result is UNDETERMINED, never KEEP and never ROLLBACK. The
edit stays in place — reverting on no evidence is as unjustified as keeping on no evidence — and it
carries forward as an open question, which is what §5.4's IMPROVE verdict is for.

### 4.2 The disjointness check is cheap and nobody runs it

`[INF]` Comparing the iteration's predicted sets pairwise is a few lines of code over a few dozen task
ids. It costs nothing and it is the single check that would have caught the cold open, at the moment
the entries were sealed rather than four iterations later.

The result is not a refusal. Two entries naming a shared task is legitimate — two edits genuinely can
target one failure — and the correct response is to mark both verdicts as collided rather than to
forbid the overlap. `[BP]` Run it at sealing time, not at scoring time, so the loop knows before it
spends a benchmark run that two of its six edits will be mutually unattributable. That knowledge is
actionable: ship them in different iterations.

---

## 5. Assigning Credit, Assigning Blame, and Undoing

### 5.1 The intersection, stated precisely

`[AHE §3.3]` For each sealed entry in `v_n`'s manifest, given the per-task deltas from the benchmark
run on `v_n`:

```
  fixed     = predicted_fixes  n  {tasks that improved outside their floor}
  missed    = predicted_fixes  -  fixed
  broke     = at_risk          n  {tasks that regressed outside their floor}
  surprise  = {tasks that regressed outside their floor} - at_risk
```

`[INF]` `surprise` is the term that carries the most information and gets the least attention. A
regression nobody flagged is direct evidence about the loop's weakest faculty — Chapter 45 §5.4's
at-risk field — and its rate is the production measurement of `[AHE §4.4.2]`'s roughly-twice-random
figure.

`[BP]` And every one of the four sets is reported with the width it was taken over. Chapter 45 §5.3
made claim width mandatory for exactly this moment: `fixed` of size 3 out of a predicted 3 and out of
a predicted 14 are different results and the same fraction hides it.

### 5.2 The four states, and how to separate them

```
                                                             TIME VIEW

  An entry's predicted tasks improved. Which of 2.3's four
  states is it in?

     fixed is non-empty
          |
          v
       /       \  no      +---------------------------------------+
      / outside  \------->| UNDETERMINED. Inside the floor is NOT  |
      \ the      /        | a small effect; it is no measurement.  |
       \ floor? /         | Keep the edit, carry the question      |
        \      /          | forward (4.1). C41 sec 5.7's loop bug  |
          | yes           | is scoring this as KEEP.               |
          v               +---------------------------------------+
       /       \  yes     +---------------------------------------+
      / another  \------->| COLLIDED. Both verdicts are guesses.   |
      \ entry    /        | Either probe (one benchmark run) or    |
       \ names   /        | mark both UNDETERMINED and separate    |
        \these? /         | the edits across iterations (5.3).     |
          | no            | The cold open.                        |
          v               +---------------------------------------+
       /       \  no      +---------------------------------------+
      / pattern  \------->| RIGHT FOR THE WRONG REASON. The tasks  |
      \ gone from/        | pass and the mechanism did not change: |
       \ corpus?/         | something else was compensating        |
        \      /          | (C43 sec 5.2). Real gain, wrong root   |
          | yes           | cause -- and the next PIVOT will be    |
          v               | aimed at the wrong thing (5.5).        |
     +----+-----------+   +---------------------------------------+
     |  KEEP          |
     |  real, through |
     |  the claimed   |
     |  mechanism     |
     +----------------+

  ONLY the first branch is a bug in the loop. The other two are
  the measurement being harder than the arithmetic, and a team
  that reads them as loop defects will look for a fault that is
  not there (2.3).

  Figure 47.3 -- Separating the four states (D8 Control Flow)
```

`[INF]` The third branch is the one that has no cheap alternative to Chapter 44's disappearance check.
Without it, an edit that fixed the right tasks for an unclaimed reason is indistinguishable from one
that worked as designed — and the cost is paid later, when the loop builds on a root cause that was
never correct.

### 5.3 Disjointness, and what to do when sets collide

Two entries in one iteration naming the same task make both verdicts guesses. `[INF]` There is no
arithmetic that resolves it, because the measurement contains one number and the question has two
unknowns.

Three responses, in order of cost:

- **Prevent it.** Check disjointness at sealing (§4.2). When two drafts collide, ship one and hold the
  other for the next iteration. Costs one iteration of latency and resolves the ambiguity completely.
- **Probe it.** Chapter 43 §5.3's disablement probe: revert one edit, re-run, measure. One benchmark
  run, a definitive answer, and it is the same machinery as the overlap detector.
- **Abstain.** Mark both UNDETERMINED and carry them forward. `[BP]` Cheapest and least satisfying, and
  correct when the collision is small — two entries sharing one task out of twelve is not the cold
  open.

`[INF]` The trade is worth stating plainly because it is a genuine dial: fewer edits per iteration
gives cleaner attribution and slower progress. The cold open shipped six. At two, the collision would
probably not have occurred; at one, attribution is exact and the loop runs six times slower. Nobody
sets this deliberately, and it is one of the few parameters in Level 5 that a team can reason about
directly.

### 5.4 Three verdicts, one abstention, and what each requires

`[AHE §3.3]` The source's three, plus the one this chapter adds.

| Verdict | Assigned when | Effect on the workspace | Requires |
|---|---|---|---|
| **KEEP** | Predicted tasks improved outside the floor, no collision, pattern disappeared | Nothing; the edit stays | The floor (C41), the corpus (C44) |
| **IMPROVE** | Partial: some predicted tasks improved, others did not, no regressions | Nothing; the next iteration refines it | A per-task result, not an aggregate |
| **ROLLBACK_AND_PIVOT** | Predicted tasks did not improve, or at-risk tasks broke, or a surprise regression is attributable | File-level revert (C39) | A stable runtime (C40) and the floor |
| **UNDETERMINED** | Inside the floor, or collided, or the mechanism check failed | Nothing; the question carries forward | Only honesty |

`[INF]` IMPROVE is the verdict most likely to be dropped from an implementation, because it looks like
an undecided KEEP. It is not. It records that a specific *subset* of the prediction held, which is the
information the next iteration needs to refine rather than restart — and an edit refined from a
partial success is a different action from one re-proposed after a rollback.

The pivot half of ROLLBACK_AND_PIVOT matters as much as the revert. `[INF]` Chapter 45 §5.2 required a
root cause that states a mechanism precisely so there is something to pivot *away from*. The rolled-back
entry stays in the manifest (Chapter 45 §7.1) as a refuted hypothesis, and the next attempt must
target a different cause rather than re-attempt the same one with different wording.

### 5.5 Rollback is automatic, and that is a decision with a precondition

`[AHE §4.4.2]` The loop predicts what it will fix at roughly five times random and what it will break
at roughly two. `[INF]` A process that cannot see its own damage cannot be the thing that decides
whether damage occurred, so the response to a measured regression is mechanical rather than
deliberated. Chapter 20 §5.6 flagged this and this is where it is acted on.

Automatic action on a measurement inherits every defect in the measurement, which gives this chapter
two hard preconditions.

**The runtime must be stable.** Chapter 40 §14 stated it directly: a loop attached to a suite with
forty-one retried tests will attribute intermittent runtime failures to whatever edit happened to be
under test. `[INF]` The failure is worse than random — it is *biased*, because a flaky runtime
produces regressions at a roughly constant rate and the loop reverts whatever it was testing, so good
edits are removed in proportion to how many iterations they survive.

**The floor must be known and current.** Chapter 41 §7.2: a floor is invalidated by a model change or
a corpus change and by nothing else. `[BP]` Attribution refuses to run against a stale floor for the
same reason Chapter 41's evaluator raises rather than warns — the resulting verdicts are actions, and
an action taken on a number without its error term is a change made at random.

`[BP]` And one practice from Chapter 41 §5.7, restated because this is the chapter it was written for:
**log the floor with every verdict.** Distinguishing "this edit helped" from "this edit was inside the
floor and we kept it anyway" is only possible afterwards if the floor travelled with the decision.

### 5.6 Rollback restores the code, not the world

Chapter 27 §5.4 is exact about this and it is the limit of the cleanest rollback story in the book.

`[AHE §3.1]` File-level revert over the harness workspace is tier 1 — owned state, prior version kept,
a local write that cannot half-fail. `[INF]` The trap is assuming the property extends to what the
harness *did*. A trial that ran under `chg-2` and opened a pull request has produced a tier-2 effect,
and reverting `chg-2` does not touch it.

`[BP]` The answer Chapter 27 gives is a constraint on trials rather than a better rollback: **trials
produce tier-1 effects only** — sandbox filesystem, scratch space, nothing else — enforced by the
sandbox (Chapter 31) rather than by the benchmark's good manners. That constraint is what makes
automatic rollback sufficient, and it is the reason an evolution loop must not be pointed at production
traffic without solving a problem this chapter does not solve.

`[INF]` For a loop that does eventually learn from production runs — Chapter 37 §14 calls that the
obvious and valuable next step — Chapter 39 §5.4's affected-population query is the available tool:
the runs carrying the reverted harness hash are exactly what shipped under it, and they are queryable
because Chapter 38 recorded the triple. Reverting is then the start of the work rather than the end
of it.

### 5.7 Why the ordering is the design

Restating §3.1's point as the chapter's own, because it is the one thing here that no implementation
gets right by accident.

`[AHE §3.3]` Attribute, then distil. `[INF]` The natural reading order is the opposite — read what went
wrong, then judge what you did last time — and every implementation that follows the natural order
compounds its errors. The corpus contains failures caused by the previous iteration's bad edits; the
loop diagnoses them as fresh defects; and the fix it proposes is a fix for its own damage, which the
rollback would have removed for free.

`[INF]` The failure has a signature worth recognising: a rising rate of new patterns in successive
corpora while the score is flat or falling. Chapter 44 §12 named that shape from the other direction —
a corpus growing while the score rises is non-additivity — and this is its uglier sibling, where the
corpus grows because the loop is generating the failures it then reads.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  Iteration 12's six edits, attributed.

  t     step                          result
  ----  ----------------------------  ----------------------------
  0     benchmark on v_12 completes   per-task deltas, per-slice
                                      floors, k=5
  1     floor freshness check (C41)   current: model unchanged,
                                      corpus version unchanged
  2     disjointness across the six
        sealed entries                COLLISION: chg-4 predicted
                                      {112,203,318}; chg-6's
                                      middleware plausibly
                                      touches all three
  3     intersect, per entry
          chg-4  fixed 3/3, width 3
          chg-6  fixed 1/1, width 1
          chg-1  fixed 0/4  broke 0
          chg-2  fixed 0/2  broke 1
                 (at_risk hit)
          chg-3  fixed 2/9, width 9
          chg-5  fixed 0/3
                 surprise regression
                 on 415, not flagged
  4     floor check, per task         chg-3's two are +1.9 and
                                      +2.4 against a slice floor
                                      of 6.0 -> INSIDE
  5     mechanism check (C44 sec 7.2) chg-4's pattern PERSISTS in
                                      the new corpus, all 31 tasks
  6     verdicts
          chg-4  UNDETERMINED   collided AND mechanism check
                                failed -- the cold open, caught
          chg-6  KEEP           pattern shrank by 1
          chg-1  ROLLBACK_AND_PIVOT
          chg-2  ROLLBACK_AND_PIVOT   at_risk correctly named
          chg-3  UNDETERMINED   inside the floor (4.1)
          chg-5  ROLLBACK_AND_PIVOT   surprise regression;
                                      null at_risk claim MISSED
                                      (C45 sec 5.4)
  7     reverts applied NOW, to the
        workspace                     three file-level reverts
  8     chg-4 probed next iteration   one benchmark run resolves
                                      the collision
  9     ONLY THEN distil (C44)        the corpus is built from a
                                      workspace whose known-bad
                                      edits are gone (3.1)

  FAILURE BRANCH -- no mechanism check and no disjointness check:

    t=6   chg-4 KEEP, precision 1.0, best edit of the iteration
          chg-6 KEEP, credited with 1 task
    t=16  four iterations later, the pattern is still there and
          somebody probes by hand
    -- and in between, the loop built two more edits on chg-4's
       stated root cause, which was never correct.

  FAILURE BRANCH -- distil before attribute:

    t=9   the corpus is built while chg-1, chg-2, and chg-5 are
          still in the workspace
    t=10  the next iteration reads chg-2's broken task and
          chg-5's surprise regression as NEW failures
    t=11  it proposes fixes for its own damage, which the
          rollback removed for free two steps earlier
    -- and the corpus grows while the score does not (5.7)

  Figure 47.4 -- Six edits, four verdicts, three reverts
                 (D4 Sequence)
```

### 6.1 The interesting verdict is the abstention

`[INF]` Step 6 assigns UNDETERMINED twice, and a reader used to systems that always decide will read
that as a weakness. It is the chapter working. `chg-4` was the iteration's most impressive result on
the arithmetic and is the one thing in the iteration that was definitely not established; `chg-3`
moved two tasks and moved them by less than the instrument can see.

Neither is reverted, and that is deliberate. `[BP]` Reverting on no evidence is exactly as unjustified
as keeping on no evidence, and an implementation that treats UNDETERMINED as a soft rollback has
replaced one bias with another. The edit stays, the question is recorded, and the next iteration
either probes it or leaves it alone.

---

## 7. State Management

```
                                                            STATE VIEW

   AN EDIT, after its manifest entry was sealed (C45 sec 7).

      {{ live }}         committed in v_n, awaiting the benchmark
          |
          | the run completes; attribution runs
          v
      {{ attributed }}
          |
          +-- outside the floor, disjoint, pattern shrank ------+
          |                                                     |
          |                                                     v
          |                                              {{ kept }}
          |
          +-- partial: some predicted improved, none broke ----+
          |                                                     |
          |                                                     v
          |                                            {{ refining }}
          |                                             next iteration
          |                                             edits it further
          |
          +-- predicted missed, or at_risk broke, or a
          |   surprise regression is attributable
          |                                                     |
          |                                                     v
          |                                          {{ reverted }}
          |                                           file-level (C39);
          |                                           the ENTRY is
          |                                           marked, never
          |                                           deleted (C45 7.1)
          |
          +-- inside the floor, or collided, or the
              mechanism check failed
                                                                |
                                                                v
                                                      {{ undetermined }}
                                                       the edit STAYS;
                                                       the question is
                                                       carried forward

      ILLEGAL, and each has shipped somewhere:

        * {{ undetermined }} treated as {{ reverted }}. Reverting
          on no evidence is as unjustified as keeping on no
          evidence, and it biases the loop toward whatever the
          noise happened to do (6.1).

        * {{ reverted }} with the entry deleted. The refuted
          hypothesis is what stops the loop re-proposing it
          (C45 sec 7.1, C26 sec 14).

        * attributing against a stale floor. The verdict is an
          action, and an action on a number without its error
          term is a change made at random (5.5).

        * {{ kept }} without the mechanism check. The score moved;
          nothing establishes that it moved for the stated reason,
          and the next pivot is aimed at the wrong thing.

  Figure 47.5 -- An edit's states after sealing (D6 State Diagram)
```

### 7.1 A reverted edit is a result, not a deletion

`[INF]` The manifest entry, the diff, and the verdict together are the most reusable artefact the loop
produces: a hypothesis, the change that embodied it, and the measurement that refuted it. Chapter 45
§7.1 made the point about the entry; the same argument covers the commit, which stays in git.

`[BP]` A cleanup that removes reverted commits or prunes rolled-back entries destroys exactly the
history Chapter 26 §14's invariant runs on — a proposal with no new evidence is refused, and *no new
evidence* is a statement about what has already been tried.

### 7.2 The verdict carries its conditions or it is not comparable

Same rule as Chapter 41 §7.1, at a different grain. A verdict recorded without the floor it was
measured against, the corpus version, the rollout count, and the collision set is uninterpretable
later — and Chapter 48's non-additivity analysis reads verdicts across many iterations.

`[BP]` Store them with the verdict. `[INF]` The specific field that gets dropped is the collision set,
because it is empty most of the time and looks like noise; it is also the only record that a verdict
was taken in the presence of another edit that could explain it.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence


class Attributor(Protocol):

    def attribute(
        self,
        entries: Sequence["Entry"],
        observed: "PerTaskDeltas",
        floor: "Floor",
        corpus_before: "CorpusHandle",
        corpus_after: "CorpusHandle",
    ) -> Sequence["Attribution"]:
        """Intersect each sealed entry's sets with the observed
        deltas, per task and against the per-slice floor.

        Raises when the floor is stale (C41 sec 7.2). A verdict is
        an ACTION, and an action taken on a number without its
        error term is a change made at random (5.5).

        Takes BOTH corpora because the mechanism check compares
        them: an entry whose tasks passed while its pattern
        persisted is right for the wrong reason (5.2).
        """

    def collisions(self, entries: Sequence["Entry"]) -> Sequence[tuple[str, str, str]]:
        """(change_id, change_id, shared_task_id).

        Run at SEALING, not at scoring. Knowing before the
        benchmark that two of six edits will be mutually
        unattributable is actionable -- ship them in different
        iterations (4.2).
        """


class VerdictAssigner(Protocol):

    def assign(self, attribution: "Attribution") -> "Verdict":
        """Four values. The fourth is UNDETERMINED, and it exists
        because an intersection is a total function: without an
        abstention the arithmetic produces a verdict for cases the
        evidence cannot decide (2.2 step 4).

        Inside the floor is UNDETERMINED, never KEEP and never
        ROLLBACK. It is not a small effect; it is no measurement
        (4.1).
        """


class RollbackExecutor(Protocol):

    async def revert(self, change_id: str) -> "RollbackRecord":
        """File-level revert in the workspace (C39). Tier 1: owned
        state, prior version kept, cannot half-fail (C27).

        Restores the CODE, not the world the code acted on. This
        is sufficient only because trials are confined to tier-1
        effects -- sandbox and scratch space, enforced by C31
        rather than by the benchmark's good manners (5.6).

        Marks the manifest entry; never deletes it. The refuted
        hypothesis is what stops the loop re-proposing it (7.1).
        """
```

`Attributor.attribute` taking two corpora is the signature that carries §5.2's third branch. `[INF]`
It looks like an over-specified argument list and it is the difference between *the score moved* and
*the score moved for the stated reason* — a distinction with no other cheap detector, and one whose
absence compounds because the next pivot is aimed at a root cause that was never right.

`VerdictAssigner.assign` returning a four-valued enum rather than a three-valued one plus a confidence
float is deliberate. `[BP]` A float invites a threshold, a threshold gets tuned, and a tuned threshold
over a noisy measurement is Chapter 41's cold open arriving in the one place where the output is an
action rather than a report.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class Verdict(StrEnum):
    KEEP = "keep"
    IMPROVE = "improve"
    ROLLBACK_AND_PIVOT = "rollback_and_pivot"
    UNDETERMINED = "undetermined"      # this chapter's addition


@dataclass(frozen=True)
class Attribution:
    """One entry's result. Carries its conditions, or it is not
    comparable with any other (7.2)."""
    change_id: str
    fixed: tuple[str, ...]             # predicted n improved
    missed: tuple[str, ...]
    broke: tuple[str, ...]             # at_risk n regressed
    surprise: tuple[str, ...]          # regressed, NOT flagged --
                                       # the production measure of
                                       # AHE 4.4.2's weakness
    predicted_width: int               # C45 sec 5.3; 3-of-3 and
                                       # 3-of-14 are different
    at_risk_width: int
    floor: "Floor"                     # embedded, not referenced
    corpus_version_before: str
    corpus_version_after: str
    pattern_shrank: bool | None        # None when the entry named
                                       # no pattern
    collided_with: tuple[str, ...]     # the field most likely to
                                       # be dropped, and the only
                                       # record that another edit
                                       # could explain this (7.2)
    verdict: Verdict


@dataclass(frozen=True)
class RollbackRecord:
    change_id: str
    reverted_commit: str
    reason: Verdict
    entry_marked: bool                 # never deleted (7.1)
    affected_runs_query: str           # C39 sec 5.4: what shipped
                                       # under the reverted hash,
                                       # queryable because C38
                                       # recorded the triple
```

`Attribution.surprise` being a first-class field rather than derivable is deliberate. `[INF]` It is the
only place in the running system where `[AHE §4.4.2]`'s regression-prediction weakness is measured
rather than cited, and a field that must be computed on demand is a field nobody computes.

`Attribution.collided_with` is empty in most iterations, which is precisely why it disappears from
implementations. `[INF]` The cold open's verdicts would have carried `["chg-6"]` in that field, and the
four-iteration gap between the wrong verdict and its discovery is the cost of the field not existing.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Benchmark (C41) | Attributor | Per iteration | Per-task deltas with per-slice floors |
| Manifest (C45) | Attributor | Sealed entries | Predicted and at-risk sets, with widths |
| Corpus n and n+1 (C44) | Mechanism check | Two handles | Whether the targeted pattern shrank |
| Attributor | Rollback executor | Blocking, before distillation | Which edits to revert, now |
| Rollback executor | Workspace (C39) | File-level revert | One commit per revert |
| Attributor | Distiller (C44) | Ordering constraint | `attribution_complete`, which C44 §8 requires |
| Verdicts | **Chapter 48** | Across iterations | Non-additivity, and the prediction precisions |
| Verdicts | **Chapter 49** | Per iteration | The review surface, with the abstention rate |
| Reverted hash | Affected-population query (C39 §5.4) | On rollback | What shipped under it, if anything did |

The sixth row is the ordering made mechanical. `[INF]` Chapter 44 §8 made `attribution_complete` a
required argument on the distiller precisely so that Chapter 20 §4.1's phase order is a type error
rather than a convention — and this is the component that supplies it.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Two edits predict overlapping tasks | Disjointness check, if it exists | Check at sealing; ship them in different iterations (§4.2). The cold open |
| An edit credited for another's effect | Mechanism check against the next corpus | Both corpora into attribution (§5.2) |
| Inside-floor movement scored as KEEP | Nothing; it looks like a small win | UNDETERMINED; inside the floor is no measurement (§4.1). C41 §5.7's loop bug |
| UNDETERMINED implemented as a soft rollback | Good edits disappearing at a steady rate | Reverting on no evidence is as unjustified as keeping (§6.1) |
| Automatic rollback on a flaky runtime | Reverts correlate with nothing in particular | C40's tiers 1 and 2 first; a stable runtime is a precondition (§5.5) |
| Attribution against a stale floor | The floor's age, if it is recorded | Raise, do not warn (§5.5) |
| Distillation before attribution | Corpus growing while the score is flat | The required argument (§10, C44 §8) |
| Reverted entries or commits pruned | The loop re-proposes a refuted hypothesis | Mark, never delete (§7.1) |
| Trials with tier-2 effects | Discovered when a revert does not undo something | Confine trials to tier-1 effects (§5.6, C31) |
| Collision set not recorded | A verdict cannot be re-examined later | Store it with the verdict; it is empty most of the time (§7.2) |
| Surprise regressions not tracked | The at-risk weakness stays a citation | First-class field (§9) |

`[INF]` Row four is the one most likely to be introduced deliberately, by someone reasoning that an
unproven edit should not be kept. It is a defensible instinct and it produces a loop biased toward
reverting whatever the noise disfavoured — which, over enough iterations, is a random walk that
discards good work at a steady rate while looking cautious.

---

## 12. Scalability

**Attribution is arithmetic and costs nothing.** Set intersections over a few dozen task ids per
entry, a few entries per iteration. `[INF]` Every expensive thing in this chapter is a *disambiguator*
— a probe is one benchmark run, a held edit is one iteration of latency — and the arithmetic itself
never becomes a constraint.

**Edits per iteration is the dial, and it trades throughput against attributability.** `[INF]` Six
edits gives six times the throughput and a collision probability that rises faster than linearly,
because the collisions are pairwise. One edit per iteration makes attribution exact and the loop six
times slower. The cold open is what the top of that range costs, and Chapter 48's non-additivity
finding is an argument for the bottom of it — since edits do not stack anyway, shipping fewer per
iteration loses less than it appears to.

**Probes do not scale and are not meant to.** One benchmark run each. `[BP]` Spend them on collisions
that matter — a shared task in a small predicted set — rather than on every overlap, and let the rest
be UNDETERMINED.

**The verdict history grows with iterations and stays small.** `[INF]` It is also the input Chapter 48
reads across many iterations, so the retention question is the same as Chapter 44's: keep the
structural record, which is tiny, indefinitely.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Abstention rate.** The share of verdicts that are UNDETERMINED. Near zero means the arithmetic is
  guessing; very high means the benchmark cannot resolve the edits being made, which is Chapter 41
  §5.7's gate failing after the fact.
- **Collision rate per iteration.** Pairs of entries sharing a task. Rising with edits per iteration,
  and the input to the §12 dial.
- **Surprise-regression rate.** Regressions nobody flagged, as a share of all regressions. The
  production measurement of `[AHE §4.4.2]`.
- **Mechanism-check pass rate among KEEPs.** How often a kept edit's pattern actually shrank. Below
  about half, the loop is accumulating edits credited for other things.
- **Rollback rate, and the fraction later re-proposed.** A refuted hypothesis returning is Chapter 26
  §14's invariant leaking.

### 13.2 The review question

For any KEEP: **did the pattern it targeted get smaller?**

`[INF]` Two seconds, one lookup, and it separates a real gain from a credited one — which is the
distinction the arithmetic cannot make and the cold open's team took four iterations to ask. It is
also the only question in this chapter that a human can answer faster than the machinery can.

### 13.3 Teaching this to a new engineer

Give them iteration 12's numbers: six edits, seven tasks improved, `chg-4` predicted three and got
three. Ask which edit worked best. Everyone picks `chg-4`, and the arithmetic agrees.

Then show them that `chg-4`'s pattern is still in the corpus.

`[INF]` The instinct that installs is the sixth in this level and it is the same one again, aimed at a
verdict this time. *Worth what, against what baseline* (Chapter 42). *What else could be doing this*
(Chapter 43). *What would I have to see to know I am wrong* (Chapter 44). *What would have made this
claim fail* (Chapter 45). *What is this number not measuring* (Chapter 46). And here: **what else
could have caused this?**

---

## 14. Relation to the Base Runtime

**What the base runtime supplies.** `[DAR]` Chapter 27's tier taxonomy is what makes rollback
analysable rather than hopeful: tier 1 is owned state with a prior version kept, and file-level revert
over an owned workspace is the cleanest instance of it in the book. `[DAR §9.3]` The golden-set
regression harness and the recorded version triple are what let a reverted hash be turned into a query
over exactly what shipped under it.

**What this chapter adds.** `[INF]` The runtime reverts a change; this chapter decides *whether* to,
from a measurement that underdetermines the decision. The additions are the fourth verdict, the
mechanism check as a second attribution signal independent of the score, the disjointness check at
sealing rather than at scoring, and the treatment of inside-floor results as no measurement rather
than as weak evidence.

**What the loop owes the runtime.** Trials confined to tier-1 effects, so that rollback is sufficient
(§5.6). A stable runtime before automatic rollback is enabled at all (Chapter 40 §14). And every
verdict logged with the floor it was measured against, so that Chapter 48 can read them together.

**And the honest limit.** `[INF]` Nothing here resolves a collision without spending a benchmark run.
The arithmetic can detect that it cannot decide, which is a real improvement over deciding wrongly,
and it cannot decide. That leaves a residue of undetermined verdicts in every iteration, and Chapter
48 is where the accumulated effect of that residue on the loop's overall trajectory is faced.

---

## 15. Industry Perspective

**`[AHE §3.3]`** Algorithm 1's phase ordering — attribute before distil — and the three verdicts:
keep, improve, rollback-and-pivot. `[AHE §4.4.2]` supplies the asymmetry that makes rollback automatic:
fix prediction at roughly five times random against regression prediction at roughly two.
`[AHE §3.1]` supplies file-level rollback at git granularity.

**`[DAR]`** The tier taxonomy behind Chapter 27, which is what makes the rollback story analysable,
and the version triple that makes an affected-population query possible.

**`[INF]`** The handbook's own: the fourth verdict and the argument that an intersection is a total
function and will therefore decide cases the evidence cannot; the four states an intersection cannot
separate, and a disambiguator for each; the mechanism check as an attribution signal independent of the
score; disjointness checked at sealing rather than at scoring; inside-floor results as no measurement
rather than weak evidence; the observation that a flaky runtime biases rollback rather than randomising
it; and the edits-per-iteration dial as a deliberate trade between throughput and attributability.

**`[BP]` Marketing attribution is the closest mature analogue** and its lesson is the useful one:
every model is partly wrong, last-click is the one that feels natural and is the most biased, and the
only clean answer is a holdout. The field's other lesson transfers too — that attribution models get
chosen by whoever they flatter, which is a governance problem rather than a statistical one, and
Chapter 49's.

**`[BP]` Automatic rollback on a measurement is standard in progressive delivery**, where a canary
that breaches an error-budget threshold is reverted without a human. The difference is that a canary's
signal is a rate over thousands of requests and this one is a difference over sixty tasks against a
noise floor, which is why the precondition in §5.5 is a precondition rather than good practice.

**`[FUT]` Resolving collisions without a probe is open.** `[FUT]` The available idea is to stagger the
commits *within* an iteration and measure between them, turning one measurement of six edits into six
measurements of one — which costs six benchmark runs and is exactly what the probe costs, so it buys
ordering rather than economy. Whether a cheaper decomposition exists is unstudied, and it is the single
change that would most improve the loop's attribution quality.

---

## 16. Key Takeaways

1. **A verdict is an action, not a report.** KEEP retains an edit and ROLLBACK removes one, so an
   attribution error changes the system rather than the dashboard — and the next iteration reasons
   about a harness nobody intended.
2. **Six edits and one measurement do not determine six verdicts.** The intersection is a total
   function and will decide cases the evidence cannot, which is why the fourth verdict exists.
3. **Four states look identical from the arithmetic:** real, inside the floor, credited to the wrong
   edit, and right for the wrong reason. Only the second is a bug in the loop.
4. **Check the mechanism, not only the score.** A kept edit whose targeted pattern is still in the
   corpus did not work, whatever the number says — and the next pivot will be aimed at a root cause
   that was never correct.
5. **Check disjointness at sealing.** It costs nothing, and knowing before the benchmark that two of
   six edits will be mutually unattributable is actionable in a way that knowing afterwards is not.
6. **Inside the floor is no measurement, not a small effect.** Abstain: reverting on no evidence is as
   unjustified as keeping on no evidence.
7. **Rollback restores the code, not the world.** It is sufficient only because trials are confined to
   tier-1 effects, and that confinement is enforced by the sandbox rather than by the benchmark's good
   manners.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Attribution intersection** | Comparing each entry's sealed predicted and at-risk sets against the observed per-task deltas. | `[AHE]` | Ch 48 |
| **Undetermined verdict** | The fourth verdict, recording that the evidence cannot decide, without which the arithmetic decides anyway. | `[INF]` | Ch 48, Ch 49 |
| **Predicted-set collision** | Two edits in one iteration naming a shared task, which makes both verdicts guesses and is detectable at sealing. | `[INF]` | Ch 48 |
| **Inside-floor keep** | Retaining an edit on a movement smaller than the noise floor — the one of the four states that is a defect in the loop. | `[INF]` | Ch 48 |
| **Mechanism check** | Confirming that the targeted pattern shrank in the next corpus, which separates a real gain from a credited one. | `[INF]` | Ch 48 |
| **Surprise regression** | A task that broke without being named at risk, whose rate is the production measurement of the loop's weakest faculty. | `[INF]` | Ch 48 |
| **Trial effect confinement** | Restricting a trial to tier-1 effects, which is what makes file-level rollback a sufficient undo. | `[BP]` | Ch 49 |
| **Runtime stability precondition** | The requirement that a measured regression be real before rollback is automated, since a flaky runtime biases reverts rather than randomising them. | `[INF]` | Ch 49 |
| **Edits per iteration** | The dial trading loop throughput against attributability, since collisions rise faster than linearly with the count. | `[INF]` | Ch 48 |

---

**Next:** Chapter 48 — *Limits.* The loop now proposes under constraint, records falsifiable claims,
and judges them honestly enough to abstain. The next chapter is the one that keeps the book honest
about what all of that adds up to: three edits that each helped delivering less together than their
sum, a process that predicts what it will fix five times better than what it will break, and a
containment list known to be incomplete.
