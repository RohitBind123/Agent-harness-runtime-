```
  Level 5 · Chapter 42
  THE CASE FOR HARNESS EVOLUTION
  Requires   C20 The Self-Evolving Runtime (Overview),
             C38 Deployment and Versioning,
             C41 Evaluation Infrastructure
  Unlocks    C43 Component Observability, C46 The Evolve Agent,
             C49 Continuous Improvement and Governance
  Diagrams   Core (5)
```

# Chapter 42 — The Case for Harness Evolution

---

## 1. Motivation

### 1.1 Cold open

Atlas has run the same sixty-task benchmark for eighteen months. Eighteen months ago it scored 71.4.
Last week it scored 78.9.

In between: three base-model migrations and a hundred and forty-three harness edits, each one in git
with a note.

A new engineer asks which of the two earned the seven points, the models or the edits. Nobody knows,
so they check. They check out the harness as it stood eighteen months ago, before any of the hundred
and forty-three edits, and run it against the model deployed today.

It scores 77.6.

Eighteen months of harness engineering, measured end to end, is worth 1.3 points against a noise
floor of 3.1. Not measurably anything.

The work was not bad. Every re-fit was measured when it shipped and every one was outside the floor
at the time: +4.8, +5.9, +4.1. Those gains were real. They were also, mostly, re-earning ground the
previous model release had taken away — the timeout fitted to one model's pacing, the tool
description written around one model's misreading, the context ordering arranged for one model's
attention.

The team had been treating harness quality as something they accumulate. The measurement says it is
something they hold, for as long as the model underneath it stays still.

Which is about five months.

### 1.2 In plain language

The software around the model — the instructions, the tool descriptions, the retry rules, the small
accumulated fixes — is worth a lot. On a fixed model, improving only that software moved a published
benchmark by more than seven points. Nobody disputes that it matters.

The problem is that it does not stay improved. When the model underneath changes, a large part of
that tuning stops fitting, because much of it was shaped around one specific model's habits. So the
work has to be done again, on a schedule set by the model provider rather than by you.

That makes it maintenance rather than progress. And it is expensive maintenance, because it can only
be done by the few people who understand the whole system, and because most of the time is not spent
deciding what to change — it is spent reading through enormous amounts of recorded activity looking
for the pattern that explains the failures.

This chapter argues that this specific job should be handed to a machine, and it is careful about
which part of the argument is the real one. It is not that a machine has better ideas. It is that the
slow step is reading, the volume is millions of tokens per batch, and a machine can read all of it
while a person can read a fraction of one percent.

### 1.3 Why this chapter exists

Chapter 20 introduced the evolution loop twenty-two chapters ago and answered *what it is*: three
kinds of observability, a second agent that edits the harness, a manifest of falsifiable predictions,
and a phase ordering. It was placed early so that Levels 3 and 4 could be specified knowing the loop
was coming.

This chapter answers the different question: *should you run one, and what would it be for.*

That was not answerable in Level 2, and is now, because two of its terms have been supplied since.
Chapter 38 §5.1 enumerated what a model change invalidates, making the decay concrete rather than
anecdotal. Chapter 41 §5.7 supplied the instrument and the condition under which the loop is worth
building at all.

`[INF]` This chapter puts those together and adds a third thing neither supplies: a measurement of
where the effort actually goes during a re-fit. That answer determines what kind of automation is
worth building, and it is not the kind most teams reach for.

### 1.4 What previous framings got wrong

**"Models keep improving, so the harness matters less."** The measured direction is the opposite.
`[AHE §4.2]` reports over seven points from harness edits alone with the base model held fixed, and
every new model arrives needing to be fitted to. A faster release cadence *increases* the harness
workload; it does not retire it.

**"Automate it because people are too slow."** Not the argument, and getting this wrong leads to
building the wrong thing. A re-fit takes weeks mostly because the reading takes weeks (§4.1). What
the loop contributes is throughput on the reading step, not better judgment on the deciding step.

**"The loop replaces the engineer."** It replaces the *re-earning*. The containment boundary
(Chapter 20 §5.5), the constraint on which components may be edited at all, and the review gate on
the loop's own behaviour are human decisions, and Chapter 49 argues they must stay that way.

**"We will build it when we have capacity."** The prerequisite is not capacity. It is a benchmark
whose resolution exceeds the effect a single edit produces (Chapter 41 §5.7). A team with spare
capacity and an unmeasured noise floor will build a loop that climbs its own noise, faster and more
confidently than the people it replaced.

**"Our harness is not model-specific."** Almost every harness believes this, because the
model-specific parts were written by different people at different times to fix real problems and
none of them was labelled. Chapter 38 §5.1's bottom group is exactly that list, and the cold open's
team took eleven days to reconstruct it.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Hand-tuned query hints against a database optimiser that gets replaced every release.

The practice is old and the shape is exact. Someone who understands the optimiser adds hints, forces
a join order, pins a plan. The queries get fast, and the gains are real. The hints accumulate over
years, each written by someone solving a specific problem on a specific version, and none recorded
as *version-specific* because at the time there was only one version.

Then a major upgrade lands. The optimiser is better on average and different in particular: some
hints are now redundant, some neutral, and a few are forcing a worse plan than the new optimiser
would have chosen unaided. Nothing fails. The queries return correct results, more slowly, and the
team spends weeks working out which hints to remove.

Everything in that story transfers — gains that are real when made, invisible version-coupling,
decay that arrives with no error, and a re-fit costing more than the original fitting.

**Where it breaks**, in two ways that both make the harness case harder than the database one.

A query optimiser ships with release notes, so you can read what changed and derive which hints are
suspect. A base model ships with benchmark cards and no change log for the behaviours your harness
was fitted to, because those behaviours were never documented — they were discovered by your
engineers and worked around. `[INF]` The derivation from *what changed* to *what is now wrong* is
unavailable, so the only route is empirical: run it and look at the failures.

And you can pin the old optimiser; databases stay supported for years. A model has a published
withdrawal date (Chapter 38 §5.4), after which the old behaviour is not purchasable at any price.
The treadmill has a speed you do not set and no stop button.

### 2.2 Why the evolution loop must exist

```
  (1) Harness quality is a large performance surface. On a FIXED
      base model, editing nothing but harness components moved
      single-attempt success from 69.7% to 77.0% [AHE 4.2].

  (2) Fitting that surface requires finding out what is going
      wrong, which means reading trajectories: millions of tokens
      across hundreds of runs per batch.

  (3) A model release invalidates a large fraction of the fitting
      (C38 sec 5.1). The gains do not carry, so the work is not
      cumulative -- it is a rate that must be sustained, not a
      stock that grows.

  (4) The rate is set externally. Releases arrive every few months
      and withdrawals have dates; a re-fit takes weeks of the two
      or three people who hold the whole harness in their heads.

  (5) So there are four options, and three of them have a ceiling:
        (a) Do not re-fit. Costs points continuously, and the cost
            is invisible because nothing errors.
        (b) Add people. The constraint is shared understanding of
            one harness, which does not divide across headcount --
            two engineers editing one prompt file is worse than
            one.
        (c) Reduce the harness's model-coupling. Genuinely helps,
            and Chapter 38's one-line provenance comment is the
            cheapest version. It has a floor: some coupling is the
            fitting, and removing all of it is the same as not
            fitting.
        (d) Automate the fitting.

  (6) (d) is selected by the property (a) through (c) lack: it is
      the only one whose throughput rises with the release cadence
      instead of being consumed by it.

  (7) But automating it needs the loop to SEE what a person sees.
      That is instruments, not intelligence: component boundaries
      to aim at, distilled evidence to read, and predictions to
      check (C20's three pillars).

  (8) And a measurement good enough to decide on, thousands of
      times, unattended (C41 sec 5.7).

  Instruments and a measurement -- in that order, and neither of
  them is a better model. That is the shape of Level 5.
```

Step (5b) is the one teams discover the expensive way. `[INF]` Harness fitting looks like work that
parallelises, because it is a list of edits. It is not, because the artefact is small, shared, and
interacting: two people fitting the same harness against the same benchmark produce edits that
collide and gains that cannot be attributed to either of them, which is the cold open of Chapter 20
with more staff.

### 2.3 Standing advantage and carried advantage

The chapter's organising distinction, and the reason the cold open's 1.3 points is not the
indictment it first appears to be.

Two different quantities get called "what the harness is worth":

| | **Standing advantage** | **Carried advantage** |
|---|---|---|
| Question | What is a fitted harness worth *right now*? | How much of the last cycle's fitting survived a model change? |
| Baseline | The minimal seed, on today's model | The previous harness, on today's model |
| Measured | `[AHE §4.2]`: about +7.3 points | The cold open: +1.3 points |
| Behaviour | Large and roughly stable | Decays with each release |
| If you stop | You lose all of it, over a few releases | You lose it immediately |

`[INF]` These are routinely conflated, and conflating them produces both of the wrong conclusions.
Read the cold open as a statement about standing advantage and you conclude harness engineering does
not work — but the cold open never measured against an unfitted harness, only against an
eighteen-month-old fitted one. Read it as a statement about carried advantage, which is what it
measured, and the conclusion is the correct one: **the fitting is worth a great deal and almost none
of it carries.**

That combination is precisely the profile of maintenance. A bridge that is repainted every year is
not evidence that painting is pointless.

### 2.4 The mental model to carry

> **Harness fit is a rate, not a stock.** It is worth a lot at any instant, it decays on someone
> else's schedule, and the scarce resource it consumes is the reading, not the deciding.

Everything in Level 5 follows from taking that sentence literally. `[INF]` If fit were a stock, the
right investment would be a careful one-time engineering effort. Because it is a rate, the right
investment is a machine that sustains it, and the first thing that machine needs is not judgment but
eyes.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +~~~~~~~~~~~~~~~~~~~~~~~~~+
   |   MODEL PROVIDER        |   the clock you do not set
   |   releases every ~5 mo  |
   |   withdrawal has a date |
   +------------+------------+
                |
                | (1) a new model: an invalidation event, not an
                |     upgrade (C38)
                v
   +--------------------------------------------------------------+
   |                     THE FITTING ACTIVITY                     |
   |                                                              |
   |     read failures --> form a theory --> edit --> measure     |
   |                                                              |
   |   today: the two or three people who hold the harness in     |
   |   their heads. Level 5 replaces the loop, not the people.    |
   +--+--------------------------------------------------+--------+
      |                                                   |
      | (2) reads                                         | (3) edits
      v                                                   v
   [[ trace store (C16, C34) ]]              [[ harness workspace ]]
      ~9.4M tokens per batch                    7 component types
      a person reads ~40k          (A)          as files, in git (C39)
      -- 0.4% of it                 :                    |
                                    :                    | (4)
                                    :                    v
                                    :        +-----------------------+
                                    :        |  BENCHMARK (C41)      |
                                    :........|  60 tasks, k=5        |
                                       (A)   |  floor 3.1 pp overall |
                                             +-----------+-----------+
                                                         |
                                                         | (5)
                                                         v
                                             +-----------------------+
                                             |  A DECISION           |
                                             |  keep / revert /      |
                                             |  try again            |
                                             +-----------------------+

  Figure 42.1 -- Harness fitting as it exists before Level 5
                 (D1 High-Level Architecture)

  (1) the event that resets part of the fitting; nothing errors
  (2) the bottleneck, and the only wire whose volume is absurd
  (3) file-level edits, revertible, one commit each (C39)
  (4) the instrument, and the gate on whether any of this is
      measurable at all (C41 sec 5.7)
  (5) the output of a whole cycle is one decision per edit
  (A) side channel: the benchmark's failures are themselves
      trajectories, so wire (2)'s volume grows with wire (4)'s
      rollout count
```

### 3.1 The only thing Level 5 changes in this picture

Every box in Figure 42.1 exists already. The trace store is Chapter 16's, the workspace is Chapter
39's git repository, the benchmark is Chapter 41's, and the decision is one a human currently makes.

`[INF]` Level 5 replaces exactly one box — the fitting activity — and adds one artefact, the manifest
that makes wire (5)'s decision attributable. That is a smaller change than the phrase "self-evolving
runtime" suggests, and the smallness is the argument: a system that already has separable components,
captured trajectories, a versioned harness, and a measured benchmark is most of the way there, and a
system missing any of them is not close.

Wire (2) is where the chapter's case lives. `[AHE §3.2]` puts the volume at roughly ten million
tokens of trajectory per batch. `[INF]` A person working through failures reads a few dozen thousand
of those, selected by hand from a search — which is not a criticism of the person. It is a ratio of
about 1 in 250, and no amount of diligence closes it.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   ONE RE-FIT, OPENED UP        Atlas's three migrations, averaged
                                (sec 5.3). Total: about 18 days.

   +--------------------------------------------------------------+
   |  1. RE-MEASURE THE MECHANICAL GROUP        ~1 day        6%   |
   |     service times, token p95s, step durations, judge          |
   |     calibration (C38 sec 5.1, top group)                      |
   |     scriptable, and the part everyone does                    |
   +--------------------------------------------------------------+

   +--------------------------------------------------------------+
   |  2. FIND WHAT BROKE                        ~11 days     61%   |
   |     read failing trajectories until a pattern appears         |
   |                                                               |
   |     9.4M tokens exist. A person reads ~40k, chosen by hand.   |
   |     No tool tells you which 40k. THIS IS THE BOTTLENECK.      |
   +--------------------------------------------------------------+

   +--------------------------------------------------------------+
   |  3. FORM A THEORY AND CHOOSE A LEVEL       ~2 days      11%   |
   |     which component class can actually prevent it             |
   |     (C20 sec 5.3). Skilled, fast, and not the constraint.     |
   +--------------------------------------------------------------+

   +--------------------------------------------------------------+
   |  4. EDIT                                   ~1 day        6%   |
   |     usually small: a description, a threshold, a rule         |
   +--------------------------------------------------------------+

   +--------------------------------------------------------------+
   |  5. MEASURE                                ~3 days      16%   |
   |     paired benchmark run, k=5 (C41). Mostly waiting, and      |
   |     it does not consume the scarce person.                    |
   +--------------------------------------------------------------+

   READ IT AS A RATIO
     the step that needs a SCARCE PERSON and does not scale:  2
     the step that needs SCARCE JUDGMENT:                     3
     the steps that need MONEY:                            1, 5
     the step everyone pictures when they say "harness work": 4

  Figure 42.2 -- Where a re-fit's time actually goes (D2 Low-Level
                 Architecture)
```

### 4.1 The bottleneck is reading, and that changes what to build

Step 2 is sixty-one percent of the elapsed time and it is the step nobody plans for. `[INF]` Ask a
team how long a re-fit takes and they will estimate steps 3 and 4, because those are the steps that
feel like the work.

Chapter 38's cold open put a number on step 2 without naming it as a step: eleven days to reconstruct
which of eleven causes explained a regression, after the fact, on a system whose traces were all
present. Nothing was missing. Everything was recorded. It took eleven days because reading is what it
takes.

This has a direct consequence for what Level 5 builds first, and it is the reason Chapters 43 and 44
come before Chapter 46. `[INF]` If the bottleneck were step 3 — judgment about what to change — the
right investment would be a better proposer, and the loop would be a search over edits. It is not.
The right investment is *distillation*: turning ten million tokens into ten thousand tokens of
evidence that a reader can actually hold. Chapter 44 is that chapter, and this figure is why it is
Full tier while this one is Core.

### 4.2 Why adding people does not move step 2

The reading does not divide cleanly, for a reason worth stating precisely.

`[INF]` Two people reading different halves of the failures each see half of any pattern that spans
them, and the patterns that matter usually do span them — a tool description that misleads in three
different task types produces three unrelated-looking failures. The synthesis step is where the value
is, and synthesis is exactly the part that has to happen in one head.

That is also the strongest structural argument for the loop, and it is not about speed. `[INF]` A
process that reads *all* of the evidence before proposing anything sees cross-cutting patterns that a
sampled read cannot, whatever the sampler's skill.

---

## 5. The Treadmill, the Bottleneck, and the Evidence

### 5.1 The cold open, as the ledger records it

```
                                                            LAYER VIEW

   EIGHTEEN MONTHS OF ATLAS. Sixty-task benchmark, k=5,
   overall floor 3.1 pp throughout.

   month  event                       harness  model  score  delta
   -----  --------------------------  -------  -----  -----  ------
    0     baseline                    v0       A       71.4    --
    0-5   41 edits                    v1       A       76.2   +4.8
    5     model B deployed            v1       B       72.0   -4.2
    5-11  52 edits                    v2       B       77.9   +5.9
   11     model C deployed            v2       C       74.8   -3.1
   11-18  50 edits                    v3       C       78.9   +4.1
   -----  --------------------------  -------  -----  -----  ------
                                      143 edits        +7.5 total

   THE COUNTERFACTUAL, run last week
     v0 (the harness before any of the 143 edits) on model C
                                      v0       C       77.6

   SO, DECOMPOSED
     carried advantage of v3 over v0         +1.3   INSIDE 3.1
     the 143 edits, measured when shipped   +14.8
     the model improvement alone, v0 A->C    +6.2
     therefore lost to decay                -13.5
     -----------------------------------------------
     observed over eighteen months           +7.5

   ONLY 7.3 OF THE 13.5 arrived as the two visible step changes
   at deploy, and even those are decay NET of the new model being
   better. The other six points went nowhere in particular:
   edits that fixed a model A behaviour and were neutral on C,
   edits re-derived twice under different names, edits fitted to
   a failure mode that stopped occurring.

   VOLUME MOVED, per re-fit
     trajectories available   ====>  ~9.4M tokens
     trajectories read        ====>  ~40k tokens      (0.4%)
     evidence written down    ====>  ~3k tokens
     edits produced           ====>  41-52 files

  Figure 42.3 -- Eighteen months, and where the gains went
                 (D7 Data Flow)
```

`[INF]` The counterfactual run is the whole measurement, and it costs one paired benchmark run
against a harness you already have in git. Almost nobody does it, for the same reason almost nobody
measures a noise floor (Chapter 41 §5.1): it produces no artefact anyone wanted and it can only
deliver bad news.

It is also the only way to know whether the fitting is compounding or being re-earned, and those two
worlds call for completely different investments.

### 5.2 The release cadence sets the workload

Chapter 38 §5.1 split what a model change invalidates into two groups. The top group — service times,
token distributions, step durations, judge calibration — is mechanical and re-measurable in a day.
The bottom group is the problem: tool description wording, context section ordering, cache prefix
boundaries, retry heuristics, effort tiers, step granularity. Every entry written by someone solving
a real problem, none recorded as model-dependent.

`[AHE §1]` states the consequence directly: manual harness engineering cannot keep pace with base
model releases. `[INF]` The arithmetic behind that sentence is the entire economic case:

- A re-fit takes about eighteen days of elapsed time, eleven of which need a scarce person (§4).
- Releases arrive every four to six months, and a withdrawal date makes at least one non-optional.
- So the harness is *fitted to the deployed model* for perhaps seventy percent of the calendar; the
  rest is spent either re-fitting or running knowingly unfitted.
- Two or three people can hold one harness. An organisation with four product surfaces has four
  harnesses and does not have twelve such people.

`[INF]` None of those numbers is exotic and none improves on its own. The cadence is set by the
provider and has been getting faster, not slower.

### 5.3 The measurement behind Figure 42.2

The per-step figures in §4 are Atlas's, from three migrations, and they are the kind of number teams
have but never aggregate.

`[BP]` The practice that produces them is unglamorous: when a re-fit begins, record what each day
went on, against five buckets. Chapter 38's invalidation register is the natural home, since it
already knows when a migration started and what it touched.

`[INF]` Do this before deciding to build an evolution loop, not after. If step 2 is not your dominant
term — a small harness, well-organised traces, concentrated failures — the case in this chapter is
weaker for you, and better trace tooling may get most of the benefit at a fraction of the cost.

### 5.4 What the ten-iteration result proves

`[AHE §4.2]` Ten iterations of an automated loop, editing nothing but harness components, moved
single-attempt success from 69.7% to 77.0% with the base model identical throughout.

Three things follow, and they are enough to justify the rest of Level 5:

**Harness quality is a large, measurable surface.** Seven points is not a rounding error, and it was
obtained with the model held fixed, so it cannot be attributed to anything else.

**The fitting can be done unattended.** Not proposed unattended — *done*: read the evidence, choose
the component, make the edit, measure, keep or revert. That closed loop ran without a person in it.

**The bottleneck really was the instruments.** `[INF]` The loop used the same class of model that had
been available to the engineers doing this by hand. What it had that they did not was distilled
evidence at a scale a person cannot read and a manifest that made every edit checkable. That is the
chapter's thesis, and it is the strongest available evidence for it.

### 5.5 What it does not prove

An honest reading is shorter on claims than the headline suggests, and Chapter 48 is the chapter that
holds this line properly.

**Not that gains compound.** `[AHE §4.4.1]` Three positive single-component gains summing to +11.1
points delivered +7.3 together. Any plan that adds measured improvements is using an assumption the
source has already falsified.

**Not that the loop knows what it is breaking.** `[AHE §4.4.2]` Fix prediction runs at roughly five
times random; regression prediction at roughly two. `[INF]` It is much better at predicting what it
will repair than what it will damage, which is why Chapter 47's rollback is automatic rather than
advisory.

**Not that it transfers.** One benchmark family, one harness, a bounded iteration count. `[AHE
Limitations]` says so plainly, and any claim of transfer across models, products, or benchmarks is
speculative until measured.

**Not that it can run without review.** The containment boundary exists because an outcome-based
reward would remove protections the reward cannot represent (Chapter 20 §5.5). Nothing in the result
addresses that, and Chapter 49 is where it is governed.

`[INF]` The correct summary is narrower than the headline and still sufficient: **the loop is a way
to keep pace with model churn and to harvest a bounded set of harness improvements.** It is not an
unbounded optimiser, and a team that expects one will be disappointed at roughly iteration six, when
the curve flattens.

### 5.6 The decision: is it worth building here

The preconditions are checkable, they are all things Levels 3 and 4 already built, and the honest
posture is that most teams fail at least one of them.

| Precondition | Chapter | The check |
|---|---|---|
| A measured per-slice noise floor | 41 §5.1 | Run the unchanged harness k times. Is the floor narrower than a typical edit's effect? |
| Paired evaluation | 41 §5.1 | Same tasks, both harnesses, same inputs |
| Cost in the denominator | 35 §14 | Does a change that spends triple for two points fail? |
| A grader the loop cannot reach | 28 §7.2 | Is the verifier outside the workspace? |
| Components as files | 39, 43 | Can one edit be reverted without reverting five others? |
| Trajectories that capture inputs | 16 | Do you record what the model *could see*, not what it said? |
| Hermetic replay | 40 | Can a rollback be trusted to restore behaviour? |
| A measured step-2 share | §5.3 | Is reading actually your bottleneck? |

`[INF]` The first row is a gate rather than a preference and Chapter 41 §5.7 makes the argument: a
loop is a mechanism for making thousands of small statistical judgments unattended, and below the
floor it produces motion, a rising score on its own instrument, and an accumulation of edits that is
a random walk with a positive selection bias.

### 5.7 When the answer is no

`[INF]` Three situations where the case in this chapter does not apply, stated because a chapter that
argues for something should say where the argument stops:

**The model is pinned and will stay pinned.** Some regulated deployments freeze a model version for
years. The treadmill is switched off, fit becomes a stock rather than a rate, and a careful one-time
fitting is the right investment.

**The harness is small.** A handful of tools, one system prompt, no sub-agents. Standing advantage is
still real, but step 2 is an afternoon and there is nothing to distil.

**The benchmark cannot resolve a single edit.** Not a "not yet" — a "not this". Fix the instrument
first; it is cheaper, it is useful regardless of what you decide about the loop, and it can be
started this week.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  One model change, handled two ways. Same event, same harness.

  day   MANUAL RE-FIT (today)          AUTOMATED (Level 5)
  ----  -----------------------------  ----------------------------
   0    provider announces model D,    same announcement; the
        withdrawal in 60 days          register lists 31 stale
                                       values (C38 sec 5.2)
   1    re-measure the mechanical      same, scripted
        group; register updated
   2    shadow run on pure steps       shadow run; failing
        (C38 sec 5.3); 340 failures    trajectories captured
   3    a person starts reading        distillation: 9.4M tokens
        |                              -> ~11k of evidence, ALL of
        |                              it read (C44)
   4    |                              iteration 1: 6 edits, each
   .    | reads ~40k tokens of         with predicted fixes and
   .    | 9.4M, chosen by search       at-risk tasks written FIRST
   .    |                              (C45); benchmark re-runs
  13    pattern found: three tool       iteration 2: attribute
        descriptions and a timeout      first (C20 sec 4.1), 2
  14    theory, level chosen            reverted, 4 kept, 5 new
  15    edits made                      edits proposed
  18    paired benchmark: +4.6 pp      ...
        -> ship                        iteration 6: curve flattens
  ----  -----------------------------  ----------------------------
        18 days, 11 of them a scarce   ~4 days wall clock, no
        person's                       scarce person, ~4.3B tokens

  FAILURE BRANCH -- the manual path, when the clock runs out:

    day  0   announcement, withdrawal in 60 days
    day 40   the re-fit has not started; the person who holds the
             harness is on the incident that quarter
    day 55   forced deploy of an UNFITTED harness. Score drops
             by about what sec 5.1's model B row cost: 4.2 pp.
             Nothing errors.
    day 55+  the drop is attributed to "the new model being worse
             for our use case", which is unfalsifiable and wrong.
             It was never measured against a re-fit that did not
             happen.

  FAILURE BRANCH -- the automated path, with an unmeasured floor:

    the loop runs 6 iterations, keeps every edit that measured
    positive at k=1, and reports +9 pp
    a later paired run at k=5 reproduces +1
    -- and the loop did nothing wrong. It applied a decision rule
       to a measurement that could not support it (C41 sec 5.7).

  Figure 42.4 -- The same model change, two ways (D4 Sequence)
```

### 6.1 The comparison is not speed for its own sake

`[INF]` Eighteen days against four is the wrong headline, because a re-fit that takes three weeks is
survivable. Two other things in that column matter more.

**The eleven scarce-person days are the resource that does not exist twice.** They are why a second
product surface cannot be fitted in parallel, and why a re-fit slips when an incident lands in the
same quarter — the first failure branch.

**The automated column read all of the evidence.** The manual column read 0.4% and found a real
pattern in it, which is a testament to the reader rather than the process. `[INF]` The patterns a
sampled read misses are not the ones it happens to skip; they are the diffuse ones — a description
that misleads slightly in nine task types and obviously in none.

### 6.2 The unfalsifiable attribution

The first failure branch ends somewhere worth naming, because it is common and it hides the whole
problem. When an unfitted harness underperforms on a new model, the conclusion recorded is that the
new model is worse for this use case.

`[INF]` That claim is not testable without the re-fit that did not happen, so it survives. It also
predicts, incorrectly, that the next release will be worse again — and a team holding that belief
stops migrating early, which makes the following migration harder. Chapter 38's counterfactual
measurement (§5.1 here) is the cheapest available refutation and takes one paired run.

---

## 7. State Management

```
                                                            STATE VIEW

   THE FIT -- a property of (harness, deployed model), not of the
   harness alone. This is why it has states at all.

      {{ unfitted }}          the minimal seed, or a harness whose
          |                   model changed underneath it
          |  a fitting cycle: read, theorise, edit, measure
          v
      {{ fitted }}  <----------------------------+
          |                                      |
          | a model is deployed (C38)            | re-fit completes
          | -- NOT an error, NOT an alert        | and is MEASURED
          v                                      |
      {{ invalidated }} ---------------------->  |
          |        ^        re-fit starts        |
          |        |                             |
          |        +--- carried advantage measured, and it is
          |             usually small (sec 5.1)
          |
          | withdrawal date passes with no re-fit
          v
      {{ abandoned }}    running knowingly unfitted; the score is
                         paid every day and charged to the model

   ILLEGAL, and each one is a real practice:

     * {{ invalidated }} -> {{ fitted }} without measurement.
       The re-fit "feels done". Nothing distinguishes the two
       states from inside the system.

     * treating {{ invalidated }} as {{ fitted }} because nothing
       alerted. There is no signal. This is Level 4's recurring
       shape (C41 sec 11, row 1) at the harness grain.

     * entering {{ fitted }} on a benchmark whose floor is
       unmeasured. The state is then an opinion.

  Figure 42.5 -- The fit, and the states it actually has
                 (D6 State Diagram)
```

### 7.1 The fit is not a property of the harness

The figure's first line is the whole of §7 and it is the thing most version schemes get wrong.
Chapter 38 established the version triple — code, harness, model — precisely so that a run records
all three. `[DAR §2.2]` The fit is a property of the *pair*, and a harness version alone cannot tell
you whether it is fitted, because the question is meaningless without naming the model.

`[INF]` The practical consequence: `{{ invalidated }}` is derivable, cheaply and automatically. The
moment a new model is deployed, every harness version's fit state transitions, and nothing has to
notice or decide. That transition is the trigger Chapter 49 hangs the loop's schedule on.

### 7.2 `{{ abandoned }}` is a state, not a failure

Running a knowingly unfitted harness is sometimes correct. The re-fit may cost more than the points
are worth on a low-traffic surface, or the next model may be two months out and worth waiting for.

`[BP]` What is not acceptable is being in that state without recording it. An abandoned fit costs a
measurable number of points per day, and if it is not written down, the cost is silently charged to
the model, which is §6.2's unfalsifiable attribution arriving through a different door.

---

## 8. Internal APIs

```python
from typing import Protocol


class FitDecayMeter(Protocol):
    """Makes the cold open's measurement a routine operation rather
    than an eighteen-month archaeological dig."""

    def standing_advantage(
        self,
        harness: "HarnessVersion",
        seed: "HarnessVersion",
        corpus_version: str,
        k: int,
    ) -> "Advantage":
        """What the fitted harness is worth against the minimal seed,
        on the CURRENTLY deployed model.

        This is the number that justifies doing any of this. It is
        large and roughly stable (sec 2.3).
        """

    def carried_advantage(
        self,
        harness: "HarnessVersion",
        previous: "HarnessVersion",
        corpus_version: str,
        k: int,
    ) -> "Advantage":
        """How much of the last cycle's fitting survived the model
        change. Usually small, and the only way to know whether the
        fitting compounds or is re-earned (sec 5.1).

        Both methods raise when the floor is stale, for the reason
        C41 sec 8 gives: a number without its error term is not a
        result, and this one will be quoted in a budget meeting.
        """


class RefitLedger(Protocol):
    """Where a re-fit's days went, so sec 4's ratio is measured
    rather than believed."""

    def record(self, entry: "RefitRecord") -> None:
        """Append-only. Written during the re-fit, not reconstructed
        after it -- reconstruction systematically under-counts the
        reading, because reading leaves no artefact.
        """

    def step_shares(self, since: str) -> dict[str, float]:
        """Fraction of elapsed time per step, across recorded
        re-fits. If step 2 is not dominant, this chapter's case is
        weaker for you and should be re-argued (sec 5.3).
        """


class EvolutionReadiness(Protocol):
    """The sec 5.6 table, as a check that can block rather than a
    page in a design document."""

    def check(self, corpus_version: str) -> "ReadinessReport":
        """Evaluates every precondition. The noise-floor row is a
        gate; the rest are graded.

        Intended to be run BEFORE any of C43-C47 is built, and
        again before the loop is allowed to keep an edit without
        review (C49).
        """
```

`FitDecayMeter` raising on a stale floor is inherited deliberately from Chapter 41 §8 rather than
re-decided here. `[INF]` These two numbers are the ones that end up on a slide, which makes them the
ones most likely to be quoted without their error term.

`EvolutionReadiness.check` returning a report with one blocking row rather than a single boolean is
the same design as Chapter 41's `SliceEffect`: a consumer that receives a bare pass/fail will invent
a threshold, and a threshold invented over a noisy measurement is the failure this whole level is
built to avoid.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Advantage:
    """A measured difference between two harnesses on one model."""
    subject: "HarnessVersion"
    baseline: "HarnessVersion"
    model_id: str                 # the fit is a property of the PAIR
    corpus_version: str
    k: int
    delta_pp: float
    floor_pp: float               # C41; travels with the delta
    cost_per_success_delta: float

    @property
    def outside_floor(self) -> bool:
        return abs(self.delta_pp) > self.floor_pp


@dataclass(frozen=True)
class RefitRecord:
    """One re-fit, as it happened. Written during, not after."""
    migration_id: str
    from_model: str
    to_model: str
    days_measuring_mechanical: float      # step 1
    days_reading: float                   # step 2 -- the bottleneck
    days_theorising: float                # step 3
    days_editing: float                   # step 4
    days_benchmarking: float              # step 5
    scarce_person_days: float             # steps 2 and 3, mostly
    edits_shipped: int
    measured_gain_pp: float               # at the time it shipped


@dataclass(frozen=True)
class ReadinessReport:
    noise_floor_measured: bool            # the gate (C41 sec 5.7)
    paired_evaluation: bool
    cost_in_denominator: bool
    verifier_outside_workspace: bool
    components_are_files: bool
    trajectories_capture_inputs: bool
    replay_is_hermetic: bool
    reading_share: float                  # sec 5.3

    @property
    def blocked(self) -> bool:
        """One row is a gate. The rest are gradients -- a loop with
        weak component separation is worse, not impossible."""
        return not self.noise_floor_measured
```

`Advantage` carrying `model_id` is the §7.1 rule expressed where it cannot be forgotten. `[INF]` An
advantage recorded without the model it was measured on is uninterpretable six months later, and it
is exactly the kind of field that gets dropped as redundant because "we only run one model" — which
is true until the day the chapter is about.

`RefitRecord.scarce_person_days` being separate from the day counts is the field that carries §6.1's
point. Eighteen days of elapsed time and eleven days of one specific person are different costs, and
only the second explains why a second product surface cannot be fitted at the same time.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Provider release feed | Invalidation register (C38) | Announcement, dated | The transition to `{{ invalidated }}` |
| Invalidation register | Fit decay meter | On model deploy | Which harness versions to re-measure |
| Benchmark (C41) | Fit decay meter | Paired run | Standing and carried advantage |
| Fit decay meter | Budget and planning | Quarterly | Whether the fitting compounds |
| Refit ledger | This chapter's case | Per migration | Where the days went (§5.3) |
| Readiness check | Level 5 build decision | Blocking | Whether to build any of C43–C47 |
| Trace store (C16) | **Chapter 44** | Bulk read | The volume that makes the case |
| Component boundaries (C39) | **Chapter 43** | Structural | The action space an edit lands in |

The last two rows are this chapter's long edges out, and they are declared here rather than assumed.
`[INF]` The case made here is only actionable because two things already exist: trajectories that
record what the model could see, and a harness whose parts are separate files in git. A reader who
accepts the argument and has neither is three chapters of work away from starting, not three days.

The fourth row is the one that is usually missing entirely. `[BP]` Whether harness fitting compounds
is a planning input — it determines whether the harness team is an investment or a maintenance line
— and it is measurable with one paired run against a version already in the repository.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Fitting assumed cumulative | Nothing; the score rises and the reason is not asked | Measure carried advantage against an old version (§5.1) |
| A model change treated as an upgrade | The score drops with no error | Chapter 38's register; the fit transitions automatically (§7.1) |
| Score drop attributed to the model | Unfalsifiable, so it survives | The counterfactual run; one paired benchmark (§6.2) |
| Re-fit slips past a withdrawal date | Days-to-withdrawal, if anyone tracks it (C38 §5.4) | Start at twice the expected duration; record `{{ abandoned }}` |
| Re-fit effort estimated from steps 3 and 4 | Estimates that are wrong by a factor of four | Ledger the days as they happen (§5.3) |
| People added to shorten step 2 | Colliding edits, unattributable gains | The synthesis does not divide (§4.2) |
| Loop built before the instrument | A rising score on its own instrument | The readiness gate; the floor is blocking (§5.6) |
| Loop expected to compound | Iteration six flattens and the project is called failed | Gains do not stack `[AHE §4.4.1]`; pace-keeping, not optimisation |
| Model-coupled edits unlabelled | Eleven days of archaeology per migration | One-line provenance comment at the time (C38 §5.1) |
| Standing advantage never measured | The whole activity is unjustified and nobody notices | Run the seed on today's model once a year (§8) |

`[INF]` Rows one, three, and ten share a detector column that says *nothing*, and that repetition is
this chapter's inheritance from Level 4. Every failure here is a measurement that was never taken, and
each one is cheap: a paired run against a version already in git.

---

## 12. Scalability

**The manual process scales in the wrong resource.** A re-fit consumes about eleven days of a person
who holds the whole harness in their head, and that resource does not divide (§4.2) or hire (§2.2
step 5b). One harness is fine. Four product surfaces on independent harnesses is not, and it fails by
re-fits slipping rather than by anything visibly breaking.

**The loop scales in money.** Chapter 20 §12.1 put an iteration at roughly 720 million tokens, almost
all of it the benchmark rather than the reasoning. `[INF]` That is a real bill and it is a *buyable*
resource, which is the entire difference. Doubling the harness count doubles the compute; it does not
require doubling a population of people that does not exist.

**But it does not scale by running it harder.** Because gains do not stack `[AHE §4.4.1]` and the
reported curve flattens, ten iterations is not twice five iterations' worth of improvement. `[INF]`
The realistic operating model is one loop run per model change plus a periodic maintenance pass, not
a continuously running optimiser — which also keeps the cost proportional to the release cadence,
where the workload actually comes from.

**The reading step is where the asymmetry lives.** A person reads about 40k tokens of 9.4M. Chapter
44's distillation reads all of it, and the cost of doing so is a fraction of one rollout (Chapter 20
§12.1). `[INF]` This is the one place in the entire book where the machine's advantage is not
judgment, speed, or availability — it is that the volume is beyond a person and not beyond a
context budget.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Standing advantage, measured annually.** What the fitted harness is worth against the seed, on
  today's model. This is the number that justifies the activity existing, and almost no team has it.
- **Carried advantage, measured at every model change.** How much of the last cycle survived. It
  tells you whether you are compounding or re-earning, and the two call for different budgets.
- **Reading share of re-fit time.** §5.3's measurement. Above about half, this chapter's case applies
  to you; well below, it does not.
- **Days-to-withdrawal**, from Chapter 38 §5.4. The only metric in the system guaranteed to reach
  zero.
- **Days spent in `{{ invalidated }}` or `{{ abandoned }}`** per year. The fraction of the calendar
  the system runs knowingly unfitted, which is a cost nobody bills.

### 13.2 The review question

For any harness improvement claimed in the last year: **is it still worth anything on the model
deployed today?**

`[INF]` The question is answerable in one paired run and it is uncomfortable, which is why it is not
asked. It also has two acceptable answers. If the answer is yes, the fitting compounds and the
harness team is building an asset. If the answer is no, the fitting is maintenance and the correct
response is to automate it — which is the rest of this level.

### 13.3 Teaching this to a new engineer

Show them the cold open's first two numbers, 71.4 and 78.9, and ask what earned the difference.
Everyone answers "both, roughly evenly", and the answer is confident.

Then show them the third number, 77.6, and let the hundred and forty-three edits dissolve into 1.3
points inside a 3.1-point floor.

`[INF]` The instinct that installs is not cynicism about harness work — it is the habit of asking
*worth what, against what baseline, on which model.* That habit is the difference between a team that
runs an evolution loop and a team that has one running.

---

## 14. Relation to the Base Runtime

Level 5 inverts the relationship the previous levels had with their sources. Chapters 1 through 41
described a runtime and cited `[AHE]` where the evolution loop touched it; from here, the loop is the
subject and the runtime is the thing it acts on. Section 14 changes accordingly.

**What the base runtime supplies, and none of it was built for this.** `[DAR §2.2]` The version
triple makes fit a property of a recorded pair rather than a belief (§7.1). Bounded episodes and
recorded exit conditions make a benchmark run measurable. Ports make components separable, which is
what gives an edit somewhere to land. `[INF]` Every one of those was specified for ordinary reasons —
recovery, cost accounting, testability — and each turns out to be a precondition for this chapter's
argument being actionable rather than aspirational.

**What this chapter asks of it that it does not yet provide.** Two things, both small and both new:
the counterfactual measurement (§5.1), which needs nothing but an old harness version and a paired
run; and the re-fit ledger (§5.3), which needs someone to write down where the days went. `[INF]`
Neither is architecture. Both are the difference between a decision made on evidence and one made on
a slide.

**What the loop owes the runtime, stated before it is built.** It runs against a benchmark, never
production traffic; it proposes rather than deploys; its output is a git commit that Chapter 39's
pipeline moves forward under human gates. `[AHE §3.3]` The controllability constraints are the
source's, and Chapter 46 makes them concrete.

**And the honest framing.** `[AHE Limitations]` describes a controlled prototype: one benchmark
family, a bounded iteration count, non-additive gains, weak regression prediction. `[INF]` The
posture to carry into Chapters 43 through 49 is that the loop is real, measured, useful, bounded, and
considerably less finished than the runtime it edits — and that the case for building it rests on the
treadmill being real, not on the loop being finished.

---

## 15. Industry Perspective

**`[AHE §1]`** The premise is the source's and is stated directly there: manual harness engineering
cannot keep pace with base-model releases. `[AHE §4.2]` supplies the ten-iteration result, 69.7% to
77.0% on a fixed base model. `[AHE §4.4.1]` and `[AHE §4.4.2]` supply the two findings that bound it
— non-additive gains, and regression prediction at roughly twice random against fix prediction at
roughly five times. `[AHE §3.2]` supplies the trajectory volume that makes the reading bottleneck a
number rather than an impression.

**`[DAR]`** The version triple and the port structure are the base runtime's `[DAR §2.2]`, and they
are what make fit measurable as a property of a pair. The specification does not discuss harness
evolution; the properties it required for recovery and testability happen to be the ones this
chapter needs.

**`[INF]`** The handbook's own contributions here are the standing/carried advantage distinction and
the claim that conflating them produces both wrong conclusions; the derivation that the loop is
selected by throughput rising with cadence rather than by being faster; the measurement that reading
dominates a re-fit and the consequence that distillation is the first thing to build; the observation
that harness fitting does not parallelise because synthesis has to happen in one head; the framing of
fit as a rate rather than a stock; and the unfalsifiable-attribution failure in §6.2.

**`[BP]`** The pattern is old and well documented outside AI. Hand-tuned query hints against a
replaced optimiser is the closest analogue (§2.1) and databases have institutional memory about it.
Autotuned numerical libraries — FFTW and its successors — made the same move a generation earlier:
when the hardware underneath changes faster than experts can hand-tune kernels for it, the tuning
gets automated and the experts move to the search space rather than the search. `[BP]` Recording
provenance for a version-specific workaround at the moment it is written is standard practice in both
fields and is skipped in both.

**`[FUT]`** Whether harness fitting can be made *portable* across models — a description written once
that does not need re-fitting — is open and would remove most of the treadmill if solved. Chapter 15's
argument suggests a partial answer, since interface-level edits appear to carry better than
instruction-level ones, but the handbook has no measurement of that and treats it as speculation.
`[FUT]` A second open question: whether carried advantage can be *predicted* at edit time, so an
engineer or a loop could prefer edits likely to survive the next release. Nothing measures this today.

---

## 16. Key Takeaways

1. **Harness fit is a rate, not a stock.** It is worth a great deal at any instant and almost none of
   it carries across a model change. The cold open's hundred and forty-three edits netted 1.3 points
   against a 3.1-point floor, and every one of them was a genuine gain when it shipped.
2. **Standing advantage and carried advantage are different numbers.** Conflating them produces
   either "harness engineering does not work" or "our improvements accumulate", and both are wrong.
   Measure each against a stated baseline on a stated model.
3. **The bottleneck is reading, not deciding.** Sixty-one percent of a re-fit is finding the pattern
   in trajectories nobody can read all of; the edit itself is a day. This is why Chapter 44 is the
   first substantial thing Level 5 builds.
4. **Adding people does not fix it.** The synthesis has to happen in one head, and two readers each
   see half of any pattern that spans them.
5. **The ten-iteration result proves three things and not a fourth.** Harness quality is a large
   measurable surface, the fitting can run unattended, and the instruments were the constraint. It
   does not prove that gains compound, transfer, or can run without review.
6. **The floor is a gate, not a preference.** If the benchmark cannot resolve a single edit's effect,
   a loop will climb its own noise faster and more confidently than the people it replaced. Fix the
   instrument first; that is worth doing regardless.
7. **The counterfactual run is the cheapest important measurement in this book.** One paired
   benchmark against a harness version already in git tells you whether your harness team is building
   an asset or performing maintenance — and the answer determines whether the rest of this level is
   for you.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Standing advantage** | What a fitted harness is worth right now against the minimal seed, on the currently deployed model. | `[INF]` | Ch 43, Ch 48 |
| **Carried advantage** | How much of the previous cycle's fitting still has value after a model change, which is usually little. | `[INF]` | Ch 47, Ch 48 |
| **Fit decay** | The loss of harness advantage caused by a model change rather than by any edit, arriving with no error signal. | `[INF]` | Ch 47 |
| **Re-fit** | The campaign of harness edits that follows a model change, most of which re-earns ground rather than gaining new. | `[INF]` | Ch 49 |
| **Release cadence** | The provider's schedule, which sets the harness workload and which you do not control. | `[AHE]` | Ch 49 |
| **Reading bottleneck** | The measured finding that most of a re-fit is spent locating the failure pattern rather than choosing the fix. | `[INF]` | Ch 44 |
| **Minimal seed** | The deliberately unfitted starting harness, which is the baseline that makes advantage measurable at all. | `[AHE]` | Ch 43 |
| **Counterfactual run** | Running an old harness version against today's model to measure what the intervening work is still worth. | `[INF]` | Ch 47 |
| **Evolution readiness** | The checkable set of preconditions that must hold before an evolution loop is worth starting. | `[INF]` | Ch 49 |
| **Pace-keeping** | The honest framing of the loop's purpose: holding fit against model churn rather than optimising without bound. | `[INF]` | Ch 48, Ch 49 |

---

**Level 5 has a premise now.** The treadmill is real, its speed is set elsewhere, the work it demands
is maintenance rather than accumulation, and the scarce thing it consumes is a person reading a
volume no person can read. The next four chapters build the instruments that change that, in the
order the bottleneck dictates rather than the order the loop runs in.

**Next:** Chapter 43 — *Component Observability.* Before anything can read evidence or predict a
result, an edit needs somewhere specific to land: seven orthogonal component types as files at fixed
paths, and a seed deliberately left unfitted so that what the loop adds can be attributed to it.
