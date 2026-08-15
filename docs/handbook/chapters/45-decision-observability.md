```
  Level 5 · Chapter 45
  DECISION OBSERVABILITY
  Requires   C20 The Self-Evolving Runtime (Overview),
             C26 Planning Algorithms, C41 Evaluation Infrastructure,
             C43 Component Observability,
             C44 Experience Observability
  Unlocks    C46 The Evolve Agent, C47 Attribution and Rollback,
             C49 Continuous Improvement and Governance
  Diagrams   Full (9)
```

# Chapter 45 — Decision Observability

---

## 1. Motivation

### 1.1 Cold open

Atlas's loop reports fix-prediction precision of 89%. It has risen for six iterations and it is the
number the team watches.

An engineer reads the manifest.

Entry `chg-31` predicted *tasks in the dependency-upgrade slice*. The slice has fourteen tasks. Two
improved. The attribution code — written by somebody reasonable, in an afternoon — scored it a hit,
because something in the named slice moved.

Entry `chg-27` predicted *tasks where the model misreads a glob*. Nobody can enumerate that set,
before or after. Also a hit.

Of forty-one entries, twenty-nine name a category rather than a list of task ids. Recomputed against
enumerated sets, precision is 31%.

The 89% was not wrong. It was measuring the width of the loop's claims, and the claims had been
widening — because a wider claim is easier to satisfy, and nothing in the pipeline preferred a narrow
one.

Every entry was written before the result. Every measurement was honest. No prediction was revised
after the fact. The loop had found that vagueness scores well, with no deception anywhere, because
vagueness was the only thing it was free to vary.

### 1.2 In plain language

Suppose you change something and the score goes up. Which change did it? If you shipped five, you
cannot tell — so each change has to come with a written claim about what it will do, recorded before
you look at the result.

That much is straightforward and most people accept it. The hard part is that a claim can be written
down honestly, in advance, and still be worthless, because it was too vague to be wrong.

"This will improve dependency upgrades" cannot fail. Something in a group of fourteen tasks moves
every time, so the claim is satisfied whatever happens. "These four specific tasks will start
passing" can fail, and that is what makes it worth writing.

The same applies in the other direction, and it is the half people skip. A claim about what will get
better says nothing about what might get worse. So each change must also name what it could break —
and if it names nothing, that is itself a claim, and it should be counted like one.

This chapter is about the record where those claims live: what has to be in each entry, why it can
never be edited afterwards, and why a system scored on vague claims will quietly learn to make them.

### 1.3 Why this chapter exists

Chapter 20 introduced the change manifest and its six fields, and said what it is for: an edit is a
falsifiable claim, written before the evidence arrives. Chapter 43 gave the edit an address.
Chapter 44 gave it evidence with pointers that resolve.

None of that makes a claim *checkable*.

`[AHE §3.3]` supplies the manifest's structure — failure evidence, root cause, targeted fix,
predicted fixes, at-risk regressions, constraint level. `[INF]` This chapter's contribution is the
property the field list does not carry on its own: **a prediction has a width, and precision measured
without recording the width reports the width rather than the aim.** The cold open is that failure at
full strength, and its most uncomfortable feature is that nobody did anything wrong.

Chapter 26 §14 left an invariant here, pointing it at the evidence pillar: *a proposal with no new
evidence is refused.* The evidence lives in Chapter 44, but the refusal can only be enforced here,
because deciding whether evidence is new means comparing it against what earlier entries already
cited — and the manifest is the only thing that knows.

### 1.4 What previous framings got wrong

**"Write down what you expect, before you measure."** Necessary, insufficient, and the cold open
satisfies it completely. Forty-one entries, all written in advance, all honest, and the aggregate
they produced was meaningless.

**"Precision is the metric."** Precision without claim width is a measurement of how hard the loop
made its own test. `[INF]` Any scoring rule that rewards being right without also rewarding being
specific selects for vagueness, and it does so without any intent — the loop has no other dial to
turn.

**"The root cause field is documentation."** It is a check. A root cause that restates the fix — *the
description is wrong*, fixed by *fixing the description* — carries no information and cannot be
contradicted by anything, and an entry with one is unfalsifiable in a second, independent way (§5.2).

**"An empty at-risk list means the edit is safe."** It means the edit *claims* to be safe. `[AHE
§4.4.2]` The loop predicts what it will break at roughly twice random against roughly five times for
what it will fix, so an empty list is the field where its weakness concentrates — and an unscored
claim is where a weakness hides.

**"The manifest is a log."** It is the loop's only durable reasoning. Everything else the Evolve Agent
thought is in a trajectory nobody will read. `[INF]` Chapter 49 reviews the manifest and nothing else,
which makes its schema a governance decision rather than a data-modelling one.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A weather forecaster's scorecard.

Forecasting solved this problem, and it had to, because the failure mode is native to the domain. A
forecaster who says *there might be rain somewhere this week* is never wrong. One who says *seventy
percent chance of rain tomorrow in this postcode* can be, repeatedly and measurably. Both are honest;
only one is useful, and the difference is not accuracy.

So forecasting scores two things at once. **Calibration** is whether the stated probabilities match
observed frequencies. **Sharpness** is how narrow the forecasts are. The discipline is *sharpness
subject to calibration*: be as specific as you can while staying honest, because a scoring rule that
rewards only calibration is trivially gamed by hedging, and everybody in that field knows it.

The cold open is a scoring rule with calibration and no sharpness, discovered independently.

**Where it breaks**, in two ways that make the loop's version harder.

A forecaster predicts a **stationary** process over thousands of forecasts, so calibration is
measurable over a long run. This loop makes tens of predictions about a system it is *actively
changing* — the process is non-stationary by construction, because the edits are the point. `[INF]`
There is no long run to calibrate against, and by the time enough predictions have accumulated, they
were made about different harnesses. Chapter 47 has to work with small numbers, and this is why.

And weather has an **unambiguous outcome**: it rained or it did not. A predicted task "passing" is
measured against a noise floor (Chapter 41), so a task that flips between rollouts is neither a hit
nor a miss. `[INF]` The ground truth is itself a distribution, which means the scorecard needs a
third state — *undetermined* — that forecasting does not, and an entry scored without it inherits the
noise as if it were signal.

### 2.2 Why the change manifest must exist

```
  (1) An iteration ships several edits and produces one number.
      N edits, one score: attribution is impossible (C20's cold
      open, which discarded four points of real gain).

  (2) So each edit carries a claim about what it will change.

  (3) A claim written AFTER the result is a description. It must
      be recorded before the benchmark runs, or it can be
      revised to match -- not through dishonesty, but because
      revising is the obvious way to make a metric go up.

  (4) Recording early is not enough. The claim must be
      CHECKABLE, which means the predicted set is enumerable:
      task ids, not categories. A category cannot fail, because
      something in it always moves (1.1).

  (5) And it must be REFUTABLE in the direction that matters. A
      claim naming only improvements cannot be wrong about
      damage -- an edit that fixes three tasks and breaks four
      still "fixed what it predicted". So it must also name what
      it might break.

  (6) It must say WHERE the edit landed and at WHICH enforcement
      level, or C43's routing cannot be audited and C47 cannot
      revert precisely.

  (7) And it must CITE EVIDENCE, or a proposal is a guess.
      C26 sec 14's invariant -- a proposal with no new evidence
      is refused -- is only checkable against the citations
      earlier entries already made.

  (8) Six fields, written before the result, append-only, and
      each one disables a specific check by its absence. That is
      the manifest, and none of it is documentation.
```

Step (4) is the one the cold open failed and the one that reads as pedantry until it costs something.
`[INF]` The difference between *the dependency-upgrade slice* and *tasks 112, 203, 318, and 411* is
not precision of language. It is the difference between a claim that can be intersected with an
observed result and one that requires a judgment call — and a judgment call made by attribution code
written in an afternoon will be generous, every time, in the direction that makes the loop look good.

### 2.3 Six fields, and what each absence costs

| Field | Answers | Without it |
|---|---|---|
| **Failure evidence** | What made this worth doing? | A proposal is a guess; Chapter 26 §14's refusal is unenforceable |
| **Root cause** | Why does the failure happen? | The fix is a symptom patch and nothing detects it (§5.2) |
| **Targeted fix** | What was actually done? | The diff is the only record, and a diff does not state intent |
| **Predicted fixes** | Which tasks improve? | No attribution at all — Chapter 20's cold open |
| **At-risk** | Which tasks might break? | An edit that trades four for three scores as a success (§5.4) |
| **Constraint level** | Which component class, and why that one? | Chapter 43's routing is unauditable and its anti-pattern undetectable |

`[INF]` Read the second column as a set of questions somebody would ask in review, because that is
what it is. The manifest is the review conversation, held in advance, in a form a machine can check —
which is the only version that scales to a loop making hundreds of these.

### 2.4 The mental model to carry

> **A manifest entry is a bet with the odds written down.** If it cannot lose, it is not a bet — and a
> loop scored on bets that cannot lose will learn to make them, with no deception at any point.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |   EVIDENCE CORPUS (C44)                                      |
   |     overview + per-task analyses, every claim carrying a      |
   |     POINTER that resolves                                     |
   +---------------------------+----------------------------------+
                               | (1) pointers, not prose
                               v
   +--------------------------------------------------------------+
   |   EVOLVE AGENT (C46)      proposes one edit                  |
   +---------------------------+----------------------------------+
                               | (2) a draft entry
                               v
   +--------------------------------------------------------------+
   |                     THE ENTRY GATE                           |
   |                                                              |
   |   evidence novelty     cited before? -> REFUSE (C26 sec 14)  |
   |   sharpness            a category, not ids? -> REFUSE (5.3)  |
   |   non-circularity      root cause = fix? -> REFUSE (5.2)     |
   |   address              resolves in the registry? (C43)       |
   |   at-risk present      empty is allowed; it is a CLAIM (5.4) |
   +---------------------------+----------------------------------+
                               | (3) sealed, and bound to the
                               |     benchmark run that will test it
                               v
   +--------------------------------------------------------------+
   |            [[ THE MANIFEST ]]   append-only                  |
   |                                                              |
   |   chg-31  component  tool_desc                               |
   |           path       tool_descriptions/repo_find.tool.yaml   |
   |           evidence   3 pointers                              |
   |           predicted  {112, 203, 318}     width 3             |
   |           at_risk    {090}               width 1             |
   |           sealed_at  before run r-88                         |
   +------+-----------------------------------------+-------------+
          | (4) one iteration later                 | (5) across
          v                                         |     iterations
   +--------------------------+                     v
   |  ATTRIBUTION (C47)       |          +----------------------+
   |   intersect predicted    |          |  THE LEDGER (5.7)    |
   |   with observed; score   |          |   recurring causes,  |
   |   the at-risk claim too  |          |   level distribution,|
   +--------------------------+          |   precision AND      |
                                         |   width together     |
                                         |                      |
                                         |   reviewed by a      |
                                         |   human (C49)        |
                                         +----------------------+

  Figure 45.1 -- The manifest between evidence and attribution
                 (D1 High-Level Architecture)

  (1) an entry cites spans, so a reviewer can check the claim
      rather than trust it
  (2) a draft is not an entry; most refusals happen here
  (3) sealing binds the entry to a specific benchmark run, which
      is what makes "written before" a fact rather than a policy
  (4) C47 can only intersect sets. Anything else is a judgment
      call, and judgment calls are generous (2.2)
  (5) the ledger is the artefact humans actually read (C49)
```

### 3.1 The gate is where this chapter does its work

`[INF]` Every other component in Figure 45.1 existed in some form before this chapter. The gate is new,
it is small, and it is the entire difference between a manifest that supports attribution and one
that accumulates plausible text.

Three of its five checks refuse entries that are *honest and useless*: cited-before evidence, a
category instead of ids, and a root cause that restates the fix. `[BP]` None of them requires
judgment, all of them are cheap, and each corresponds to a specific way the cold open's loop was
allowed to drift.

The fifth check is the interesting one, because it refuses nothing. An empty at-risk list is
permitted — sometimes an edit really does threaten nothing — but recording it as a claim rather than
as an absence is what lets Chapter 47 score it, and scoring it is the only way the loop's known
weakness at predicting damage stays visible instead of becoming a blank field.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                     MANIFEST MACHINERY                         |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |  Sharpness validator     |  |  Evidence novelty checker |   |
   |  |                          |  |                           |   |
   |  |  predicted and at_risk   |  |  do these pointers appear |   |
   |  |  must be TASK IDS that   |  |  in an earlier entry?     |   |
   |  |  exist in the corpus     |  |                           |   |
   |  |                          |  |  if all of them do, this  |   |
   |  |  records WIDTH beside    |  |  is a PROPOSAL STORM      |   |
   |  |  the set, so precision   |  |  (5.1) -- the outer-loop  |   |
   |  |  is never reported       |  |  form of C26's replan     |   |
   |  |  without it (5.3)        |  |  storm                    |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |  Circularity check       |  |  Append-only store        |   |
   |  |                          |  |                           |   |
   |  |  root_cause must not be  |  |  no update method (C20    |   |
   |  |  the targeted_fix        |  |  sec 8), hash-chained,    |   |
   |  |  restated (5.2)          |  |  each entry sealed        |   |
   |  |                          |  |  against a benchmark run  |   |
   |  |  a mechanism, not a      |  |  id (5.6)                 |   |
   |  |  restatement of the      |  |                           |   |
   |  |  defect                  |  |  the LEDGER is a query    |   |
   |  |                          |  |  over this (5.7)          |   |
   |  +--------------------------+  +---------------------------+   |
   +----------------------------------------------------------------+

  Figure 45.2 -- Inside the manifest machinery (D2 Low-Level
                 Architecture)
```

### 4.1 Every check is mechanical, and that is deliberate

`[INF]` A gate that needs judgment gets a judge, a judge needs a model, and a model judging the loop's
own proposals is a verifier the loop can influence — which Chapter 20 §5.5 placed outside the
workspace for exactly this reason.

So the checks are all structural. Are these strings task ids that exist in the corpus? Does this
pointer set intersect any earlier entry's? Is the root cause string a near-duplicate of the fix
string? `[BP]` Each is a few lines, each runs in milliseconds, and none of them can be argued with —
which matters more than their individual value, because the pressure to relax them arrives as a
reasonable-sounding special case every time an entry is refused.

### 4.2 The width is recorded, not derived at scoring time

A small decision with a large consequence. The predicted set's size is written into the entry at
sealing rather than computed later from the set.

`[INF]` The reason is that the set can be *interpreted* later, and interpretation is where the cold
open happened. A category-shaped prediction can be expanded at scoring time into whatever set makes
it true, and nothing in the record contradicts that. A recorded width of 14 next to two observed
improvements is an entry that reads as a near-miss forever, no matter who scores it.

```
                                                            LAYER VIEW

   NAMED INTERNALS AND THEIR INTERFACES

   +--------------------+  propose(draft)   +--------------------+
   |  Evolve Agent      |------------------>|  Entry gate        |
   |  (C46)             |<------------------|  facade            |
   |                    |  Entry | Refusal  |                    |
   |  a REFUSAL is      |                   |  the only path      |
   |  informative: it   |                   |  into the store     |
   |  names which check |                   +--+-------+------+--+
   |  failed (4.1)      |                      |       |      |
   +--------------------+                      |       |      |
                                               v       v      v
   +--------------------+  check(pred, corpus)  |       |      |
   |  Sharpness         |<---------------------+       |      |
   |  validator         |----------------------->      |      |
   |                    |  Width | Refusal              |      |
   |  ids that EXIST    |                              |      |
   +--------------------+                              |      |
                                                       |      |
   +--------------------+  novel(pointers)             |      |
   |  Evidence novelty  |<-----------------------------+      |
   |  checker           |------------------------------>      |
   |                    |  bool | PriorEntryId                |
   |  queries the       |                                     |
   |  store, so it is   |                                     |
   |  the one check     |                                     |
   |  that needs        |                                     |
   |  history           |                                     |
   +--------------------+                                     |
                                                              |
   +--------------------+  seal(entry, run_id)                |
   |  Append-only store |<------------------------------------+
   |                    |------------------------------------->
   |  record(); NO      |  EntrySeal
   |  update(). C20     |
   |  sec 8's rule,     |  consumed by: C47 (scores), C49
   |  enforced by the   |               (reviews), C48 (counts)
   |  absent method     |
   +--------------------+

   NOT an interface here: anything that reads a RESULT. The gate
   runs strictly before the benchmark, and a gate that could see
   an outcome would be a gate that could be tuned to it.

  Figure 45.3 -- Manifest internals (D3 Component Diagram)
```

---

## 5. The Six Fields, Sharpness, and the Ledger

### 5.1 Evidence: pointers, and the novelty rule

`[AHE §3.3]` The first field is the failure evidence the edit responds to. `[INF]` Chapter 44 made it
citable: an entry carries `EvidencePointer`s — trace id, span id, byte range — rather than a
description of what was observed.

That changes the field from a note into a check. A reviewer can follow the citation; Chapter 47 can
re-check it a week later; and, most usefully, the *set* of citations across entries becomes
queryable.

Which is what makes Chapter 26 §14's invariant enforceable. Its wording was **a proposal with no new
evidence is refused**, and it pointed at the evidence pillar. `[INF]` The evidence lives in Chapter 44;
the refusal has to live here, because *new* is a statement about what earlier entries already cited,
and the manifest is the only component that knows.

The failure it prevents is the **proposal storm** — the outer-loop analogue of Chapter 26's replan
storm. An edit measures nothing, the loop re-reads the same corpus, forms a slightly different theory
about the same spans, and proposes again. `[INF]` Each proposal is reasonable, each is honest, and the
sequence is a loop burning iterations on unchanged information at roughly seven hundred million tokens
each (Chapter 20 §12.1).

`[BP]` Refuse when *every* pointer has been cited before, not when any has. A genuinely new theory
about partly-overlapping evidence is exactly what the second attempt should look like, and a stricter
rule would forbid the productive case along with the storm.

### 5.2 Root cause and targeted fix are two fields

They look redundant and are not. `[INF]` The root cause names a mechanism; the fix names an action. An
entry where the two are the same sentence in different words has stated no mechanism, and it is
unfalsifiable in a way distinct from vagueness about task ids.

```
  CIRCULAR        root_cause    "the description is wrong"
                  targeted_fix  "correct the description"
                  -- nothing here can be contradicted by any
                     observation, and the entry will read as
                     reasonable in review forever

  MECHANISM       root_cause    "the description says the
                                 parameter is a directory path;
                                 the implementation takes a glob.
                                 The model passes a path, gets an
                                 empty list, and concludes the
                                 directory is empty."
                  targeted_fix  "state that it is a glob; add a
                                 counter-example; add empty_means"
                  -- this CAN be wrong, and C43's cold open is
                     the case where it was
```

`[INF]` The check that catches the first form is cheap and imperfect: refuse when the root cause is a
near-duplicate of the fix with the polarity flipped. It will miss sophisticated circularity and it
catches the common case, which is a loop under token pressure writing the shortest thing that fills
the field.

The deeper value is that a stated mechanism is what makes the *pivot* possible. Chapter 47's
`rollback_and_pivot` verdict means the edit failed and the next attempt should target a different root
cause — and "the description is wrong" offers nothing to pivot away from.

### 5.3 Predicted fixes must be enumerable

```
                                                            LAYER VIEW

   THE COLD OPEN'S MANIFEST, BY CLAIM WIDTH

   claim shape              entries   scored     honest
                                      as hits    precision
   ----------------------   -------   --------   -------------
   a named SLICE            ====>  17    16       cannot fail:
   "dependency upgrades"                          something in 14
                                                  tasks always moves

   a CATEGORY               ====>  12    10       cannot be
   "tasks where the model                         enumerated at all,
    misreads a glob"                              before or after

   ENUMERATED task ids      ====>  12     5       41% -- the only
   "{112, 203, 318}"                              number here that
                                                  measures aiming

   ----------------------   -------   --------
   TOTAL                          41    31        reported: 89%*
                                                  * = 36/41

   RECOMPUTED against enumerated sets only:   31%

   THE 89% WAS NOT A LIE. It was the fraction of claims that
   were satisfied, and 29 of 41 claims were built so that
   satisfaction was nearly certain. Precision reported without
   width is a measurement of the test, not of the aim.

   AND NOTE THE DIRECTION OF DRIFT. Slice-shaped claims rose
   from 2 of the first 10 entries to 11 of the last 12. Nothing
   selected for that except that it worked.

  Figure 45.4 -- Precision, decomposed by claim width (D7 Data Flow)
```

`[BP]` The rule that follows: **`predicted_fixes` is a tuple of task ids that exist in the current
corpus, or the entry is refused.** Not a slice name, not a description, not a predicate. Chapter 47
intersects sets, and a set is the only thing it can intersect without judgment.

`[INF]` The objection is real and worth answering. Sometimes the loop genuinely believes an edit helps
a class of tasks it cannot enumerate — a description fix that should help wherever that tool is used.
The answer is not to relax the field; it is to enumerate the class *from the corpus*, which is
mechanical: the analyses record which tools each task called (Chapter 44 §9), so "tasks that use
`repo_find`" resolves to a list. A class that cannot be resolved from the corpus is a class the loop
has no evidence about, which is Chapter 26 §14 arriving from a different direction.

`[BP]` And report precision with width, always. A loop with 60% precision at width 3 is aiming; one
with 89% at width 14 is hedging, and the two look identical in a single number.

### 5.4 At-risk is the honest half, and an empty list is a claim

`[AHE §4.4.2]` Fix prediction runs at roughly five times random. Regression prediction runs at roughly
two. The loop is much better at saying what it will repair than what it will damage.

`[INF]` The asymmetry is not a defect to be engineered away, and it is worth being clear about why it
persists. Predicting a fix requires reasoning forward from a diagnosed cause to the tasks that share
it — the evidence corpus is organised around exactly that. Predicting damage requires reasoning about
tasks that are *currently passing*, which appear in the corpus only as a contrast sample (Chapter 44
§4.1) and about which almost nothing is recorded, because nothing went wrong in them.

So the field will keep being weak. What must not happen is for it to become invisible:

- **An empty `at_risk` is a claim** — *this edit breaks nothing* — and Chapter 47 scores it like any
  other. An entry that claimed nothing at risk and broke two tasks is a miss, recorded as one.
- **The claim rate is a signal.** `[BP]` A loop whose entries carry an empty at-risk list ninety
  percent of the time has stopped trying, and that is visible long before the precision figure moves.
- **A wide at-risk list is not free either.** Naming forty tasks as at risk is the same hedge as
  naming a slice as fixed, in the opposite direction, and width is recorded on both fields for the
  same reason.

`[INF]` This is also the field that explains why Chapter 47's rollback is automatic rather than
advisory. A process that predicts damage at twice random cannot be trusted to notice its own damage,
so the response to an unpredicted regression cannot be to ask the process about it.

### 5.5 Constraint level records the routing decision

Chapter 43 §5.3's chain routes a failure to a component class; the entry records which class was
chosen. `[AHE §3.3]` The field is the source's and its value here is entirely in the aggregate.

`[INF]` A single entry's constraint level is uninteresting — it is whatever the routing said. The
distribution across entries is where two failures become visible, and neither has any other detector:

- **Rising system-prompt share** is Chapter 43 §5.4's default-owner decay, and Chapter 44 §5.2 added a
  second cause. The manifest is where it is counted.
- **The same level three times for one failure pattern** is Chapter 1 §5.2's named anti-pattern. The
  manifest is the only place that history exists, because each attempt looks locally reasonable.

`[BP]` Query the manifest for `(root_cause_cluster, constraint_level)` pairs with a count above two.
That query is the anti-pattern detector, it costs nothing, and it works only because both fields are
mandatory.

### 5.6 Write-before-measure is structural, not procedural

```
                                                             TIME VIEW

  Where an entry can and cannot be written.

     draft written by C46
          |
          v
     +----+------------------------+
     |  GATE: five checks (3)      |
     +----+------------------------+
          |
          v
       /       \  any check fails   +--------------------------+
      / gate    \----------------->| REFUSED. The reason names |
      \ passes? /                  | the check, so the next    |
       \       /                   | draft can differ (4.1)    |
          | yes                    +--------------------------+
          v
     +----+------------------------+
     |  SEAL                       |   bound to benchmark run
     |  hash-chained, timestamped, |   r-88, which HAS NOT RUN
     |  bound to the run that will |
     |  test it                    |
     +----+------------------------+
          |
          v
     +----+------------------------+
     |  the benchmark runs         |   <-- the line nothing
     +----+------------------------+       crosses backwards
          |
          v
       /       \  yes              +---------------------------+
      / edit an  \---------------->| IMPOSSIBLE. There is no   |
      \  entry?  /                 | update method (C20 sec 8) |
       \        /                  | and the chain would break |
          | no                     +---------------------------+
          v
     +----+------------------------+
     |  C47 scores it              |
     +-----------------------------+

  THE POINT OF THE SEAL is not that anyone would cheat. It is
  that revising a prediction to match a result is the obvious
  way to make a metric go up, and a loop optimising a metric
  will find obvious things.

  Figure 45.5 -- The line nothing crosses backwards
                 (D8 Control Flow)
```

`[INF]` Chapter 20 §8 made the point structurally by omitting an update method. This chapter adds the
binding: the entry names the benchmark run that will test it, and that run has not started. Without
the binding, "written before" is a claim about timestamps in a system where timestamps are written by
the thing being audited.

`[BP]` Hash-chain the entries. It costs nothing, it makes retroactive insertion detectable, and
Chapter 49's reviewer needs to be able to trust the ordering without trusting the process that
produced it.

### 5.7 The manifest is a ledger, and the ledger is what humans read

`[INF]` One entry answers *why this edit*. The manifest across iterations answers questions nothing
else in the architecture can, and this is where its value compounds:

| Query | What it detects |
|---|---|
| Precision **and mean width**, per iteration | The cold open, before it reaches 89% |
| At-risk claim rate, and its precision | Whether the loop is still trying on the hard half (§5.4) |
| Constraint-level distribution over time | Default-owner decay (§5.5) |
| `(root_cause, level)` counts above two | Fixing at the wrong level (§5.5) |
| Evidence-pointer reuse rate | Proposal storms forming (§5.1) |
| Verdict mix: keep / improve / rollback | Whether the loop is aiming or thrashing |

`[AHE §3.3]` calls the manifest the loop's evidence ledger, and `[INF]` the practical consequence is
about attention rather than analysis. Chapter 49 has a human reviewing an automated process that
makes hundreds of decisions. They cannot read the trajectories, they will not read every entry, and
the six queries above are what a review can actually consist of — each one a number with a direction
that means something.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  One edit, from evidence to sealed entry.

  t     step                          result
  ----  ----------------------------  ----------------------------
  0     C46 reads the overview,
        acts on pattern P2
        (empty-result, 12 tasks)
  1     drafts an entry:
          component  tool_impl
          path       tools/repo_find.py
          evidence   3 pointers
          root cause "empty match returns
                      [] with no message;
                      indistinguishable
                      from an empty
                      directory"
          fix        "return a message
                      distinguishing the
                      two"
          predicted  "the empty-result
                      pattern"
          at_risk    {}
  2     GATE: sharpness                REFUSED. "the empty-result
                                       pattern" is not a set
  3     C46 resolves the class from
        the corpus: which tasks does
        P2 group? (C44 sec 9)          {112, 203, 318, 411, ...}
                                       12 ids
  4     redrafted with the 12 ids;
        width recorded as 12
  5     GATE: evidence novelty         PASS. No earlier entry
                                       cites these spans
  6     GATE: circularity              PASS. The cause states a
                                       mechanism, not the fix
  7     GATE: address resolves (C43)   PASS
  8     GATE: at_risk empty            ALLOWED, recorded as the
                                       claim "breaks nothing"
  9     SEALED, bound to run r-88,
        hash-chained to chg-30
 10     the edit is committed; the
        benchmark runs
  ----  ----------------------------  ----------------------------
  n+1   C47 intersects:
          predicted 12, observed 7     precision 0.58 at width 12
          at_risk {} , observed 1
          broken                       the NULL CLAIM was wrong,
                                       and is scored as a miss

  FAILURE BRANCH -- no sharpness check (the cold open):

    t=2   "the empty-result pattern" is accepted
    n+1   7 tasks improved; attribution finds improvement "in
          the pattern" and scores a hit
    -- precision 1.0, width unrecorded, and the entry is
       indistinguishable in the ledger from one that named 7 ids
       and hit all 7. Do this forty-one times and the reported
       number is 89%.

  FAILURE BRANCH -- no evidence-novelty check:

    n+1   verdict ROLLBACK_AND_PIVOT; the edit is reverted
    n+2   C46 re-reads the SAME corpus, forms a slightly
          different theory about the SAME three spans, proposes
          again
    n+3   and again
    -- a proposal storm: three iterations, ~2.2B tokens, no new
       information consumed at any point (5.1)

  Figure 45.6 -- One entry through the gate (D4 Sequence)
```

### 6.1 A refusal is a useful output

Step 2 refuses and step 3 succeeds, and the loop is better for the round trip. `[INF]` The refusal
names which check failed, which is what lets the next draft differ in the right way — resolving the
class from the corpus rather than rephrasing the description.

That matters more than it sounds. A gate that returned a bare rejection would produce a loop that
retries with cosmetic variation, and Chapter 15's argument about error messages being instructions
rather than diagnoses applies here exactly. `[BP]` The gate's refusals are an interface the Evolve
Agent reads, so they are designed under Chapter 15's rules, not written as validation errors.

```
                                                             TIME VIEW

  The proposal cycle, once per edit.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+------------------+                              |
   | draft an entry        |                              |
   +----+------------------+                              |
        |                                                 |
        v                                                 |
      /   \  fail                                         |
     / gate \ ------> redraft, informed by the check      |
     \  ?   /              that failed (6.1)              |
      \    /                    |                         |
        | pass                  |                         |
        |    <------------------+                         |
        v                                                 |
      /   \  yes                                          |
     /third \ ------------------------> E1 the evidence   |
     \redraft/                             cannot support |
      \     /                              an entry; drop |
        | no                               the pattern    |
        v                                                 |
      /   \  all pointers cited before                    |
     /novel \ ------------------------> E2 proposal storm |
     \  ?   /                              -- stop, and   |
      \    /                               widen the      |
        | yes                              corpus (5.1)   |
        v                                                 |
   +----+------------------+                              |
   | SEAL, bind to run     |                              |
   +----+------------------+                              |
        |                                                 |
        v                                                 |
      /   \  yes                                          |
     /budget \ -------------------------> E3 iteration    |
     \ left? /                               budget spent |
      \     /                                             |
        | no more edits this round                        |
        +-------------------------------------------------+

  Exits:
    E1  three refusals on one pattern means the evidence cannot
        support a falsifiable claim -- which is a finding about
        C44's fields, not about this pattern (C44 sec 5.5's E2)
    E2  every pointer already cited: the loop is re-theorising
        unchanged evidence (C26 sec 14)
    E3  the ordinary exit

  Figure 45.7 -- Drafting until an entry is sealable
                 (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

   A MANIFEST ENTRY

      {{ drafted }}
          |  five checks (3.1)
          +---- any fails ----> {{ refused }}  (not stored; the
          |                                     reason returns to
          |                                     C46)
          v
      {{ sealed }}      hash-chained; bound to a benchmark run
          |             that HAS NOT RUN
          |
          | that run completes
          v
      {{ open }}        awaiting attribution
          |
          v
      {{ scored }} ---- verdict attached (C47): keep, improve,
          |             or rollback_and_pivot
          |
          | a later iteration edits the same component
          v
      {{ superseded }}  never deleted; the ledger is the point

      ILLEGAL, and the first is the one that matters:

        * {{ sealed }} -> {{ sealed }} with different content.
          There is no update method (C20 sec 8) and the hash
          chain would break. Revising a prediction to match a
          result is the obvious way to raise a metric, and this
          is what makes it unavailable rather than discouraged.

        * scoring an entry against a widened predicted set.
          The width is recorded AT SEALING for this reason (4.2);
          a set re-interpreted at scoring time is the cold open
          with an extra step.

        * deleting {{ superseded }} entries. Every ledger query
          in 5.7 is a trend, and a trend needs the history that
          looks least useful -- the entries that were already
          rolled back.

  Figure 45.8 -- Entry states (D6 State Diagram)
```

### 7.1 The entry outlives the edit it describes

`[INF]` An entry whose edit was reverted is not obsolete. It is the record that a hypothesis was
tested and refuted, and it is what stops the loop testing it again — which is Chapter 26 §14's
invariant working through history rather than through a single check.

`[BP]` So `rollback_and_pivot` marks an entry, never removes it, and the reverted commit stays in git
(Chapter 39 §7.2). The pair — a refuted hypothesis and the diff that embodied it — is the most
reusable artefact the loop produces, and it is the one a naive cleanup deletes first.

### 7.2 Sealing binds to a run, not to a clock

Restating §5.6 as a state property because it is the one thing in this chapter that has to be right.

`[INF]` A timestamp says when a row was written according to the system that wrote it. A benchmark run
id says which measurement this claim precedes, and the run either had started or had not. The
ordering is then a fact about two recorded events rather than a fact about a clock, which is the same
reason Chapter 32 preferred fence tokens to wall time — the ordering must not depend on the honesty
of the party being ordered.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence


class EntryGate(Protocol):
    """The only path into the manifest. Every check is mechanical;
    a gate needing judgment would need a judge, and a judge the
    loop can influence is a verifier inside the workspace
    (C20 sec 5.5)."""

    def propose(self, draft: "ChangeDraft", corpus: "CorpusHandle") -> "Entry | Refusal":
        """Five checks: evidence novelty, sharpness,
        non-circularity, address resolution, at-risk recorded.

        A Refusal names the failing check, because C46 reads it
        and redrafts from it. C15's rule applies: an error is an
        instruction, not a diagnosis (6.1).
        """

    def seal(self, entry: "Entry", pending_run_id: str) -> "EntrySeal":
        """Bind the entry to the benchmark run that will test it.

        Raises if that run has already started. The ordering must
        be a fact about two recorded events, not about a clock
        written by the party being audited (7.2).
        """


class SharpnessValidator(Protocol):

    def check(self, predicted: Sequence[str], corpus: "CorpusHandle") -> "Width | Refusal":
        """Task ids that EXIST in the corpus, or refuse.

        Not a slice name, not a predicate, not a description.
        C47 intersects sets; anything else needs a judgment call,
        and judgment calls made by scoring code are generous in
        the direction that flatters the loop (2.2).

        Returns the width, which is STORED beside the set. A width
        derived at scoring time can be derived from a re-read of
        the claim, which is the cold open with an extra step (4.2).
        """


class EvidenceNoveltyChecker(Protocol):

    def novel(self, pointers: Sequence["EvidencePointer"]) -> "bool | str":
        """False (with the prior entry id) when EVERY pointer has
        been cited before -- a proposal storm (5.1).

        Deliberately not 'any pointer'. A new theory about
        partly-overlapping evidence is what a good second attempt
        looks like, and the stricter rule would forbid it.
        """


class Ledger(Protocol):
    """Queries over the manifest. This is what C49's reviewer
    reads; they will not read entries (5.7)."""

    def precision_and_width(self, iterations: int) -> Sequence["IterationStats"]:
        """Never precision alone. A loop at 60% precision and
        width 3 is aiming; one at 89% and width 14 is hedging,
        and a single number cannot tell them apart."""

    def level_distribution(self, iterations: int) -> dict[str, float]:
        """Rising system-prompt share is C43 sec 5.4's decay."""

    def repeated_level_for_cause(self, threshold: int = 2) -> Sequence[tuple[str, str, int]]:
        """(root cause cluster, level, count) above threshold: the
        fix-at-the-wrong-level anti-pattern, detectable only
        because both fields are mandatory (5.5)."""
```

`EntryGate.seal` raising when the run has started is the signature that carries §7.2. `[INF]` It looks
like defensive programming and it is the enforcement of the chapter's central rule — the only one
whose violation leaves no trace in the data, because a revised prediction and an accurate one are the
same row.

`Ledger.precision_and_width` returning both figures in one structure, with no method returning
precision alone, is the same design as Chapter 39's `SliceEffect` carrying its noise floor. `[BP]` If
a caller can obtain the flattering number without the qualifying one, eventually a dashboard will.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Prediction:
    """A claim with its width recorded at sealing (4.2)."""
    task_ids: tuple[str, ...]
    width: int                     # len(task_ids), STORED
    resolved_from: str | None      # the corpus query, when the
                                   # ids were derived from a class
                                   # rather than named (5.3)


@dataclass(frozen=True)
class Entry:
    """C20 sec 9's ChangeEntry, with the fields this chapter adds.
    The six AHE fields are unchanged; sharpness and sealing are
    what make them checkable."""
    change_id: str
    component: "ConstraintLevel"   # C20 sec 9; C43 says it is also
                                   # the address's type
    path: str
    failure_evidence: tuple["EvidencePointer", ...]   # C44
    root_cause: str                # a MECHANISM (5.2)
    targeted_fix: str
    predicted_fixes: Prediction
    at_risk: Prediction            # empty is a CLAIM, not an
                                   # absence (5.4)
    commit_sha: str


@dataclass(frozen=True)
class EntrySeal:
    """What makes 'written before' a fact rather than a policy."""
    change_id: str
    pending_run_id: str            # had not started at seal time
    prev_entry_hash: str           # hash chain (5.6)
    entry_hash: str


@dataclass(frozen=True)
class Refusal:
    """Read by C46 and redrafted from, so it is an interface
    under C15's rules (6.1)."""
    check: str                     # which one, by name
    detail: str                    # what to do differently
    prior_entry_id: str | None     # set only for novelty refusals


@dataclass(frozen=True)
class IterationStats:
    iteration: int
    fix_precision: float
    mean_predicted_width: float    # never reported apart (8)
    at_risk_claim_rate: float      # share of entries claiming
                                   # something at risk (5.4)
    at_risk_precision: float
    null_at_risk_miss_rate: float  # claimed nothing, broke
                                   # something
```

`Prediction.resolved_from` is the field that makes §5.3's objection answerable rather than dismissed.
`[INF]` An entry that named twelve ids by resolving *tasks calling `repo_find`* against the corpus is
carrying both the enumeration attribution needs and the reasoning a reviewer wants, and neither costs
the other.

`IterationStats.null_at_risk_miss_rate` exists as its own field because it is the number that would
otherwise never be computed. `[INF]` An empty at-risk list looks like nothing happened, so it takes a
deliberate metric to notice that the loop claimed safety and was wrong — which is the specific shape
of `[AHE §4.4.2]`'s weakness showing up in production rather than in a paper.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Evidence corpus (C44) | Entry gate | Per draft | Pointers, and the task ids a class resolves to |
| Registry (C43) | Entry gate | Per draft | Whether the path resolves and at which level |
| Entry gate | **Chapter 46** | Refusal | Which check failed and what to change |
| Manifest | **Chapter 47** | One iteration later | Sealed sets to intersect with observed deltas |
| Manifest | **Chapter 48** | Across iterations | Precision with width, and the at-risk record |
| Ledger | **Chapter 49** | Six queries | What a human review actually consists of |
| Seal | Git (C39) | Per entry | The commit the entry describes |

```
                                                             TIME VIEW

  << entry.refused >>        ....> which check, and why. Routine
                                   singly; a SIGNAL in aggregate,
                                   like C44's pointer-follows

  << entry.sealed >>         ....> change id, widths, the pending
                                   run id, the chain hash

  << proposal.storm >>       ....> every pointer already cited.
                                   The loop is re-theorising
                                   unchanged evidence (5.1)

  << claim.width.rising >>   ....> mean predicted width trending
                                   up across iterations. The cold
                                   open, caught at iteration
                                   three instead of forty-one

  << null_at_risk.missed >>  ....> an entry claimed nothing at
                                   risk and something broke

  << entry.scored >>         ....> verdict attached (C47), with
                                   precision AND width

  Figure 45.9 -- What the manifest makes durable (D9 Event Flow)
```

`[INF]` The fourth event is the one this chapter exists to make possible. Every other signal here
reports a discrete thing that happened; `claim.width.rising` reports a *drift*, and drift is what the
cold open was. It is computable from a field that costs one integer per entry, and without that field
there is no version of the alert at all.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Predictions name categories, not ids | Nothing; precision rises and looks like progress | Sharpness check refuses; width stored at sealing (§5.3). The cold open |
| Precision reported without width | Same number for hedging and for aiming | One structure carrying both; no method returns precision alone (§8) |
| Root cause restates the fix | The entry reads reasonably forever | Near-duplicate check; a cause must state a mechanism (§5.2) |
| Empty at-risk treated as an absence | The loop's known weakness becomes a blank field | Score the null claim; track its miss rate (§5.4) |
| Proposal storm | Iterations spent, no new evidence consumed | Refuse when every pointer was cited before (§5.1) |
| An entry revised after the result | None — a revised row and an accurate one are identical | No update method; hash chain; seal bound to a pending run (§5.6) |
| Sealing bound to a timestamp | The clock is written by the audited party | Bind to a benchmark run id (§7.2) |
| Predicted set widened at scoring | The claim becomes true retroactively | Width recorded at sealing (§4.2) |
| Superseded entries deleted | Every ledger trend loses its history | Mark, never remove (§7.1) |
| Gate needs judgment | A judge the loop can influence | Every check mechanical (§4.1) |
| Refusals returned as bare rejections | The loop redrafts cosmetically | Refusals are an interface under C15's rules (§6.1) |

`[INF]` Rows one, two, and six share the property that makes this chapter's failures distinctive: the
detector column is *nothing*, and the artefacts produced are not merely plausible but genuinely
correct. A widened claim is a true claim. A precision figure without width is an accurate figure. The
manifest fills with entries that would survive any review that did not already know what to look for.

---

## 12. Scalability

**The manifest is small and its cost never becomes an issue.** A few kilobytes per entry, tens of
entries per iteration. `[INF]` That is worth stating because it removes the only argument that would
otherwise be made against mandatory fields: nothing here is expensive, so a field is dropped for
tidiness rather than for cost, and tidiness is not a reason.

**Sharpness scales badly with corpus size, in a way that is a feature.** Resolving a class to ids
against a corpus of sixty failures is instant; against six hundred it is still instant, but the
resulting width is ten times larger and the entry is honestly harder to satisfy. `[INF]` A loop
working on a larger benchmark should show lower precision at higher width, and a loop whose precision
holds while width grows is hedging.

**Ledger queries scale with iterations and stay trivial.** Six queries over a few thousand rows.
`[BP]` The constraint is not compute; it is that the queries need history, and history needs the
superseded entries nobody wants to keep (§7.1).

**Review does not scale, and that is Chapter 49's problem.** `[INF]` A human cannot read hundreds of
entries per week and will read none rather than some. The ledger's six numbers are the answer this
chapter can offer, and they are a genuine reduction rather than a summary — each one is a
computation over every entry, so nothing is sampled away.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Fix precision with mean predicted width, together, per iteration.** Never one without the other.
  A rising width at constant precision is the cold open in progress.
- **At-risk claim rate.** The share of entries naming anything at risk. A loop that has stopped
  trying on the hard half shows here first.
- **Null at-risk miss rate.** Claimed nothing, broke something. `[AHE §4.4.2]`'s weakness, in
  production.
- **Evidence-pointer reuse rate.** Rising reuse is a proposal storm forming before it is three
  iterations deep.
- **Refusal rate by check.** A gate refusing nothing is either unnecessary or disabled, and the two
  look identical from the outside.

### 13.2 The review question

For any manifest entry: **what result would have made this entry wrong?**

`[INF]` It takes ten seconds and it is the whole chapter. If the answer requires interpretation, the
entry is not falsifiable; if it is *nothing would have*, the entry is a description wearing a
prediction's fields. Applied to `chg-31` — predicted *the dependency-upgrade slice* — the honest
answer is that no plausible outcome would have contradicted it, which is available before any result
exists and would have caught the drift at entry three.

### 13.3 Teaching this to a new engineer

Show them the 89% and ask whether the loop is aiming well. Everyone says yes; it is a good number and
it has been rising.

Then show them two entries side by side — *the dependency-upgrade slice* and *{112, 203, 318}* — and
ask which one they would rather be judged on.

`[INF]` The instinct that installs is the fourth in this level and the same one each time. Chapter 42
asked *worth what, against what baseline*. Chapter 43 asked *what else could be doing this*.
Chapter 44 asked *what would I have to see to know I am wrong*. This one asks *what would have made
this claim fail* — and a level that keeps arriving at the same question from four directions is
telling you that the question is the discipline.

---

## 14. Relation to the Base Runtime

**What the base runtime supplies.** `[DAR §9.2]` The verdict contract — deterministic checks a model
judgment may downgrade but never upgrade — is the shape this chapter borrows for its gate: mechanical
checks that a proposal must pass, with no model in the path. `[DAR]` The append-only durability
patterns behind Chapter 22's outbox are the same primitives the manifest needs, applied to a store
that is tiny rather than hot.

**What this chapter adds.** `[INF]` The runtime records what happened. The manifest records what was
*expected* to happen, before it did, and nothing in Levels 1 through 4 has an equivalent — a plan
(Chapter 10) states intent about a goal, but no runtime artefact states a falsifiable claim about a
change to the runtime itself. That is the pillar, and the sharpness discipline is what keeps it from
degenerating into intent.

**What the loop owes the runtime.** Every entry names an address that resolves, cites evidence that
resolves, and binds to a run that had not started. `[AHE §3.3]` The manifest is the source's; the
seal, the widths, and the gate are what make its fields carry the weight the source assigns them.

**And the honest limit.** `[INF]` Nothing here makes the loop *better* at predicting damage. The
at-risk field is scored, tracked, and alerted on, and it remains at roughly twice random. This chapter
makes a known weakness visible and measurable; Chapter 48 is where the consequences of designing
around it are faced, and no mechanism in this book closes the gap.

---

## 15. Industry Perspective

**`[AHE §3.3]`** The change manifest and its six fields — failure evidence, root cause, targeted fix,
predicted fixes, at-risk regressions, constraint level — and the manifest as the loop's evidence
ledger. `[AHE §4.4.2]` supplies the asymmetry the at-risk field lives with: fix prediction at roughly
five times random against regression prediction at roughly two.

**`[DAR §9.2]`** The verdict contract's shape — deterministic checks, no model judgment in the
gating path — reused here for the entry gate.

**`[INF]`** The handbook's own: that a prediction has a width and precision reported without it
measures the test rather than the aim; the drift argument, that a scoring rule rewarding correctness
without specificity selects for vagueness with no deception anywhere; circular root causes as a second
independent form of unfalsifiability; the null at-risk claim and its miss rate; sealing bound to a
pending run rather than to a clock; the proposal storm as the outer-loop analogue of Chapter 26's
replan storm, and the argument that the refusal must live in the manifest rather than in the corpus;
and the six ledger queries as what a human review can consist of.

**`[BP]` Sharpness subject to calibration is settled practice in forecasting** and almost unknown in
engineering metrics. Proper scoring rules exist precisely because rewarding correctness alone is
trivially gamed by hedging, and the field learned this the expensive way decades ago. The transfer is
direct and, as far as the handbook can tell, unmade.

**`[BP]` Pre-registration is established in empirical research** and Chapter 20 §15 already credited
it. What that literature also documents, and what is more useful here, is the *failure* mode:
pre-registered predictions drift toward the unfalsifiable when the registration is scored, which is
the cold open with human authors and a decade of examples.

**`[FUT]` Scoring an entry's sharpness automatically is unexplored.** Width is a crude proxy — twelve
ids chosen well is a sharper claim than twelve chosen to cover the field — and a proper scoring rule
over predicted sets, weighting by prior pass rate, would be strictly better. `[FUT]` The data to build
one accumulates automatically in the ledger, and nobody appears to have tried.

---

## 16. Key Takeaways

1. **A manifest entry is a bet with the odds written down.** If no plausible result would have
   contradicted it, it is not a prediction, however honestly and early it was written.
2. **Precision without width measures the test, not the aim.** 89% at width 14 and 60% at width 3 are
   opposite findings, and a single number cannot distinguish them.
3. **A loop scored on vague claims will make vague claims.** No deception is required and none
   occurred in the cold open — vagueness was the only free variable the loop had, and it worked.
4. **Predicted sets are task ids, resolved from the corpus if necessary.** Attribution intersects
   sets; anything else needs a judgment call, and scoring code makes generous ones.
5. **An empty at-risk list is a claim, not an absence.** Score it. The loop predicts damage at about
   twice random, and an unscored field is where that weakness disappears from view.
6. **A root cause that restates the fix is unfalsifiable in a second way**, and it also leaves nothing
   to pivot away from when the edit fails.
7. **Bind the seal to a pending benchmark run, not to a clock.** Revising a prediction to match a
   result is the obvious way to raise a metric, a revised row is indistinguishable from an accurate
   one, and the ordering must not depend on the honesty of the party being ordered.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Sharpness** | How narrow a claim is, which must be scored alongside correctness or the scoring rule rewards hedging. | `[BP]` | Ch 47, Ch 48 |
| **Claim width** | The size of a predicted set, recorded at sealing, without which precision reports the width rather than the aim. | `[INF]` | Ch 47, Ch 48 |
| **Enumerated prediction** | A predicted set given as task ids that exist in the corpus, which is the only form attribution can intersect. | `[INF]` | Ch 47 |
| **Entry seal** | The binding of an entry to a benchmark run that has not started, which makes "written before" a fact rather than a policy. | `[INF]` | Ch 47, Ch 49 |
| **Evidence novelty** | The requirement that a proposal cite at least one span no earlier entry cited, which is what makes Chapter 26's refusal enforceable. | `[INF]` | Ch 46 |
| **Proposal storm** | Repeated proposals re-theorising unchanged evidence; the outer-loop analogue of a replan storm, at roughly a billion tokens each. | `[INF]` | Ch 46, Ch 48 |
| **Circular root cause** | A stated cause that restates the fix, which cannot be contradicted by any observation and leaves nothing to pivot toward. | `[INF]` | Ch 46 |
| **Null at-risk claim** | An empty at-risk list, which asserts that an edit breaks nothing and must be scored like any other claim. | `[INF]` | Ch 47, Ch 48 |
| **Evidence ledger** | The manifest read across iterations, which is the loop's only durable reasoning and the surface a human review can actually cover. | `[AHE]` | Ch 49 |

---

**Next:** Chapter 46 — *The Evolve Agent.* All three pillars now exist: an addressed action space,
evidence that can be read completely and cited exactly, and a record that makes every edit
falsifiable. The next chapter builds the thing that uses them — and spends most of its length on what
it is forbidden to touch, because eight earlier chapters each concluded independently that some
specific thing must sit outside the workspace.
