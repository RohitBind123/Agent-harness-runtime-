```
  Level 5 · Chapter 48
  LIMITS
  Requires   C31 Safety and Sandboxing, C41 Evaluation Infrastructure,
             C46 The Evolve Agent,
             C47 Attribution, Verdicts, and Rollback
  Unlocks    C49 Continuous Improvement and Governance
  Diagrams   Core (5)
```

# Chapter 48 — Limits

---

## 1. Motivation

### 1.1 Cold open

Atlas's loop finishes ten iterations. Aggregate success moves from 69.7% to 77.0% and the team ships
the evolved harness.

Six weeks later a customer whose work is almost all hard-tier reports that things got worse. The team
checks. On the hard slice the evolved harness scores 53.3%. The seed scored 51.7%.

Ten iterations, and 1.6 points on the tasks that matter most to that customer.

Then somebody runs the single-component variants against the hard slice. Long-term memory alone —
twelve boundary-case lessons, added in iteration two, and nothing else — scores 63.3%.

The full evolved harness is beaten on its hardest tier by one of its own components, by ten points.

Nothing malfunctioned. The loop optimised the aggregate it was given, the aggregate is dominated by
medium-tier tasks, and somewhere around iteration five it accepted a trade that bought medium points
with hard ones. Every edit measured positive. Every verdict was correct.

The trade was never proposed, never recorded, and never visible in any number anybody looked at.

### 1.2 In plain language

This chapter is the one that says what the loop cannot do.

Three things are worth knowing before anyone builds one. Improvements do not add up: three changes
that each helped by a certain amount deliver noticeably less than that total when combined, because
they interfere with each other. The loop is much better at guessing what it will fix than what it
will break, so it walks forward confidently and cannot see the damage behind it. And the list of
things it is forbidden to touch was assembled by people noticing, one at a time, that something
needed protecting — with no argument that they found them all.

The fourth thing is the cold open, and it is the only one that can be fixed. A single score is an
average over different kinds of work. A change that helps common tasks and hurts rare ones raises the
average, so it looks like progress, and nothing distinguishes it from a change that helped
everywhere. Ten iterations of that produces a system that is better overall and worse at the hardest
thing it does.

None of this is a defect. It is what happens when you optimise one number over work that is not all
the same, using components that affect each other, with a predictor that only sees half of its own
effect.

### 1.3 Why this chapter exists

Six chapters have built the loop and every one of them ended with a limit it deferred. Chapter 20
§5.6 said what the ten-iteration result does not show. Chapter 42 §5.5 repeated it as a warning about
expectations. Chapter 43 handed over overlap, Chapter 44 handed over the diffuse pattern, Chapter 46
handed over an admittedly incomplete containment list, and Chapter 47 handed over a residue of
verdicts it could not determine.

`[AHE §4.4.1]` and `[AHE §4.4.2]` supply the two headline findings: gains do not stack, and the loop
predicts fixes at roughly five times random against regressions at roughly two. `[AHE Limitations]`
supplies the framing — a controlled prototype, one benchmark family, a bounded iteration count.

`[INF]` This chapter's contribution is to sort the limits by whether anything can be done about them.
Three are structural and can only be designed around. **One is an artefact of the objective function
and is fixable this week**, and it is the one that produced the cold open. Chapter 31 §5.6 also left
the self-modification governance gap here, explicitly and with the note that a reader wanting a
confident answer should be told there is not one (§5.6).

### 1.4 What previous framings got wrong

**"The loop is not working well enough yet."** It is working exactly as specified. `[INF]` Every
finding in this chapter is a property of the objective, the component structure, or the predictor —
not of the implementation — and a team that reads them as bugs will spend a quarter improving an
optimiser that is already optimising correctly.

**"We measured five improvements, so together they give us eleven points."** `[AHE §4.4.1]` Three
positive single-component gains summing to +11.1 delivered +7.3 together. Any roadmap that adds up
measured improvements is using an assumption the source has already falsified (§5.1).

**"The aggregate went up, so the system got better."** For whom. `[INF]` The aggregate is a weighted
average and the weights are your task mix. The cold open's evolved harness is genuinely better on the
mix it was measured against and worse on the mix one customer actually has.

**"More iterations, more improvement."** The reported curve flattens. `[INF]` Around iteration six the
loop is spending full iterations to find edits inside the noise floor, which is Chapter 47's
undetermined verdict becoming the modal outcome rather than the exception (§7).

**"Containment solves the safety question."** It bounds the direct route. `[INF]` Chapter 31 §5.6
named the indirect one and nothing since has closed it: a loop that cannot edit a boundary can still
propose a change that makes the boundary irrelevant (§5.6).

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A portfolio of correlated strategies.

Three trading strategies are each backtested alone and each shows a positive expected return. Run
together, the portfolio returns less than the sum — sometimes much less — because the strategies are
correlated. They are making overlapping bets, so their gains are not independent contributions to a
total; they are the same gain, counted three times, minus the cost of holding three positions to
capture it once.

That is precisely Chapter 1 §5.3's reading of the ablation: memory, middleware, and the system prompt
all push toward the same closure-style verification, so stacking them spends turns re-checking work
that has already been checked. `[AHE §4.4.1]` Three components, +11.1 apart and +7.3 together, and
correlation is the mechanism.

**Where it breaks**, in two ways, and the second one explains the cold open.

Correlation in a portfolio is **measurable in advance**. You have return series, you compute a
covariance matrix, and the interaction is known before you allocate. Here the equivalent requires
measuring each *pair* together — n(n-1)/2 benchmark runs for n components — so the information exists
and is priced out. `[INF]` A seven-component harness is twenty-one paired runs, which is real money
for a result no one asked for, and that is why nobody has it.

And portfolio arithmetic is **additive and stationary**: adding a fourth asset does not change how the
first three behave. Components are not like that. A middleware hook changes what the model sees, which
changes whether a memory entry is consulted, which changes what the tool is called with. `[INF]` They
modify each other's *mechanism*, not only each other's weight — so "less than the sum" understates it.
The combination can be worse than a single member, which is the cold open on the hard slice, and no
covariance matrix predicts that.

### 2.2 Why these limits are structural

```
  (1) The loop improves the harness by measuring ONE scalar.

  (2) A scalar over a heterogeneous population is a WEIGHTED
      AVERAGE, and the weights are the task mix.

  (3) So an edit that buys points in a heavy slice with points
      in a light one scores POSITIVE -- and no signal in the
      loop distinguishes it from an edit that helped
      everywhere. Ten iterations of that is the cold open.

  (4) Components are not independent contributors. Each changes
      what the model perceives and does, so each changes the
      others' MECHANISM. Gains therefore do not add, and can
      subtract [AHE 4.4.1].

  (5) The loop predicts what it will fix at ~5x random and what
      it will break at ~2x [AHE 4.4.2]. It can aim; it cannot
      see damage. So the damage it does is found by measurement
      afterwards or not at all.

  (6) And the containment list that bounds the worst damage was
      assembled by noticing, chapter by chapter, with no
      completeness argument (C46 sec 5.3, C31 sec 5.6).

  (7) None of (3) through (6) is an implementation defect. They
      are what optimising a scalar over a heterogeneous,
      interacting, partially observable system IS.

  (8) So the response is not to fix the loop. It is to change
      what is measured (3 is fixable), bound what one iteration
      may do (4, 5), and put a human where the loop is blind
      (6) -- which is C49.
```

Step (3) is the one worth dwelling on, because it is the only entry with a cheap fix and it is
routinely mistaken for an unavoidable cost. `[INF]` The loop is optimising the number you gave it. If
that number is a flat average over a mix that does not match your customers, the loop will faithfully
deliver a harness fitted to a mix nobody has.

### 2.3 Four limits, sorted by what can be done

| Limit | Source | Structural? | What helps |
|---|---|---|---|
| **Gains do not stack** | `[AHE §4.4.1]` | Yes | Measure combinations, not components; expect the sum to overstate (§5.1) |
| **Blind to its own damage** | `[AHE §4.4.2]` | Yes | Automatic rollback (Ch 47), score the null at-risk claim (Ch 45 §5.4) |
| **The aggregate hides a trade** | Ch 1 §5.3, and the cold open | **No — fixable** | Gate per slice, not on the aggregate (§5.3) |
| **Containment is a lower bound** | Ch 46 §5.3, Ch 31 §5.6 | Yes | Deny by default; human review of the gap (§5.5, §5.6) |

`[INF]` Read the third row against the other three. It is the only one where the loop is doing
something you did not intend, and it is the only one whose remedy is a configuration change rather
than a design posture. That asymmetry is the single most useful thing in this chapter, and it is
usually filed alongside the others as an inherent limitation.

### 2.4 The mental model to carry

> **The loop is a competent optimiser of exactly the number you gave it.** Every limit here is a
> property of that number, of the components' interaction, or of the predictor's blind half — and
> none of them is a property of the loop being unfinished.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   WHERE EACH LIMIT BITES IN THE LOOP

   +--------------------------------------------------------------+
   |  EVIDENCE (C44)                                              |
   |    LIMIT: the diffuse pattern -- weak in nine task types,     |
   |    obvious in none. Invisible to sampling, slicing, and       |
   |    aggregation alike (C44 sec 5.4)                            |
   +---------------------------+----------------------------------+
                               |
                               v
   +--------------------------------------------------------------+
   |  PROPOSAL (C45, C46)                                         |
   |    LIMIT: regression prediction ~2x random. The at_risk       |
   |    field is written honestly and is mostly wrong (5.4)        |
   |    LIMIT: displacement -- a contained fix becomes a weaker     |
   |    edit, or should become a ticket (C46 sec 5.6)              |
   +---------------------------+----------------------------------+
                               |
                               v
   +--------------------------------------------------------------+
   |  MEASUREMENT (C41)                                           |
   |    LIMIT: the aggregate is a weighted average, so a SLICE     |
   |    TRADE scores positive (5.3)  <-- THE FIXABLE ONE           |
   |    LIMIT: the floor bounds what any edit can demonstrate      |
   +---------------------------+----------------------------------+
                               |
                               v
   +--------------------------------------------------------------+
   |  ATTRIBUTION (C47)                                           |
   |    LIMIT: collisions leave verdicts undetermined; the         |
   |    residue accumulates across iterations (5.7)                |
   +---------------------------+----------------------------------+
                               |
                               v
   +--------------------------------------------------------------+
   |  ACCUMULATION (this chapter)                                 |
   |    LIMIT: gains do not stack [AHE 4.4.1] -- +11.1 apart,      |
   |    +7.3 together (5.1)                                        |
   |    LIMIT: the curve flattens; undetermined becomes the modal  |
   |    verdict (7)                                                |
   +--------------------------------------------------------------+

   AND ACROSS ALL OF IT:
     the containment list is a LOWER BOUND, and the indirect
     route around it is unaddressed (5.5, 5.6)

  Figure 48.1 -- Five stages, six limits (D1 High-Level Architecture)
```

### 3.1 The limits are not independent either

`[INF]` The figure reads as one limit per stage and the interactions are worse than that. Non-additivity
(§5.1) makes attribution harder, because two edits whose combined effect is less than their sum look
like one edit that under-delivered. Blindness to damage (§5.4) makes the slice trade harder to catch,
because a trade *is* damage the loop did not predict. And the undetermined residue (§5.7) grows fastest
in exactly the iterations where non-additivity is biting.

That compounding is why the chapter's conclusion is a posture rather than a fix list, and why
Chapter 49 exists.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   WHY GAINS DO NOT STACK -- three interference mechanisms

   +----------------------------------------------------------------+
   |  1. REDUNDANT CLOSURE                            [AHE 4.4.1]   |
   |                                                                |
   |     Memory, middleware, and the system prompt all push          |
   |     toward the same verification behaviour. Stacked, the        |
   |     model spends turns re-checking work already checked.        |
   |                                                                |
   |     Each is worth something alone. Together they buy the        |
   |     same thing three times and pay for it three times.          |
   +----------------------------------------------------------------+

   +----------------------------------------------------------------+
   |  2. MECHANISM SHIFT                                     [INF]  |
   |                                                                |
   |     A middleware hook changes what the model SEES, which        |
   |     changes whether a memory entry is consulted, which          |
   |     changes what the tool is called with.                       |
   |                                                                |
   |     Component B does not reduce A's effect. It changes the      |
   |     conditions under which A's effect exists at all -- which    |
   |     is why the combination can be WORSE than a member.          |
   +----------------------------------------------------------------+

   +----------------------------------------------------------------+
   |  3. BUDGET CONTENTION                                   [INF]  |
   |                                                                |
   |     Resident components -- the system prompt, loaded memory --  |
   |     consume the same context budget (C11). A second one         |
   |     displaces part of the first, and the displacement is        |
   |     decided by the assembler rather than by either component.   |
   |                                                                |
   |     C1 sec 12: components loaded conditionally scale;           |
   |     components always present do not.                           |
   +----------------------------------------------------------------+

   ONLY THE FIRST is named in the source. The other two are the
   handbook's reading of why the effect is as large as measured,
   and mechanism shift is the one that explains an inversion
   rather than a shortfall (1.1).

  Figure 48.2 -- Three ways components interfere (D2 Low-Level
                 Architecture)
```

### 4.1 Interference is not overlap

Worth separating because the two are easy to conflate and have different remedies.

`[INF]` Chapter 43 §5.2's **overlap** is two components owning the *same behaviour*, which breaks
attribution: an edit to either one measures zero. **Interference** is two components with different
behaviours whose effects do not add. Overlap is a defect in the component structure and is fixable by
assigning ownership; interference is a property of a system whose parts share a model, a context
budget, and a step count, and it is not fixable at all.

`[BP]` The practical distinction: overlap is found with a disablement probe and resolved by removing
an owner. Interference is found by measuring the *combination* and is managed by expecting the sum to
overstate, never by removing a component that measured positive alone.

### 4.2 Budget contention makes non-additivity worse over time

`[INF]` The third mechanism has a direction that the other two do not. Every iteration that adds a
resident component — a paragraph of instruction, a memory entry that loads by default — takes context
budget from everything else already resident, so the interference term grows monotonically with the
number of always-present components.

That predicts something the reported curve shows: the flattening is not a plateau of *no more
improvements available*, it is a plateau where new gains and rising interference cancel. `[BP]` The
countermeasure is Chapter 39 §5.6's removal experiment, run against components rather than sentences,
and it is the only mechanism in this book that reduces interference rather than working around it.

---

## 5. The Four Limits

### 5.1 Gains do not stack

```
                                                            LAYER VIEW

   THE ABLATION, AS AN ARITHMETIC PROBLEM      [AHE 4.4.1], 89 tasks

   variant                     All    delta vs seed
   -------------------------   -----  -------------
   seed (bash-only)            69.7      --
   + long-term memory only     75.3    ====>  +5.6
   + tool only                 73.0    ====>  +3.3
   + middleware only           71.9    ====>  +2.2
   + system prompt only        67.4    ====>  -2.3
                                              -----
   naive sum of the positives                +11.1

   full evolved harness        77.0    ====>  +7.3

   THE GAP IS 3.8 POINTS, or a third of the predicted total.

   A ROADMAP BUILT ON THE SUM
     planned      +11.1   five quarters of work, costed
     delivered     +7.3
     -- and nobody made an error. Each measurement was correct
        and outside its floor. The addition was the assumption.

   WHAT THE PROMPT ROW ADDS
     the one component that regressed ALONE is in the harness
     that gained the most TOGETHER. Removing a negative
     component is not obviously right either, because its
     contribution is conditional on the others (4.1, mechanism
     shift)

  Figure 48.3 -- Eleven point one apart, seven point three
                 together (D7 Data Flow)
```

`[BP]` The planning rule that follows is blunt and holds up: **when adding measured single-component
gains, discount the total by roughly a third, and treat the result as an upper bound rather than a
forecast.** One data point is a thin basis for a coefficient, which is why the rule is stated as a
posture — but planning on the undiscounted sum has a known error and this does not.

### 5.2 Why they do not stack

§4's three mechanisms, and the reason the distinction between them matters for what you do.

**Redundant closure** is `[AHE §4.4.1]`'s own reading and it is the benign case: you paid three times
for one behaviour. `[BP]` It is detectable by removal experiments and the remedy is to keep the
cheapest of the three.

**Mechanism shift** is the case with no remedy. `[INF]` Component B changes the conditions under which
A's effect exists, so A's measured-alone number was never a property of A — it was a property of A in
the seed. Every single-component measurement in Figure 48.3 is a measurement against one specific
harness, and re-measuring the same component in the evolved harness would give a different number.

**Budget contention** is arithmetic and is the one that worsens with time (§4.2).

`[INF]` The three explain different parts of the gap and nobody has decomposed a real gap into them.
That is worth saying plainly: the mechanisms are the handbook's account of *why* +11.1 became +7.3,
and the account is unmeasured.

### 5.3 The aggregate hides a trade — and this one is fixable

The cold open, in the source's numbers.

| Variant | All | Easy | Medium | **Hard** |
|---|---|---|---|---|
| Seed | 69.7% | 87.5% | 78.2% | 51.7% |
| + long-term memory only | 75.3% | **50.0%** | 83.6% | **63.3%** |
| + tool only | 73.0% | 75.0% | 87.3% | 46.7% |
| + middleware only | 71.9% | 100.0% | 81.8% | 50.0% |
| Full evolved | 77.0% | 100.0% | 88.2% | 53.3% |

`[AHE §4.4.1]` Read the memory row first. Alone, it is the best single component on the aggregate —
and it costs **37.5 points on Easy** while gaining 11.6 on Hard. Chapter 1 §5.3's reading is that its
lessons reduce to redundant re-checking on tasks that never needed it.

Then read the last two rows together. The full harness scores 53.3% on Hard; memory alone scores
63.3%. `[INF]` The loop, optimising an aggregate in which Medium is the largest population, accepted a
trade that recovered Easy and Medium at the cost of ten points of Hard. Every edit that composed that
trade measured positive on the aggregate. No edit proposed it. No verdict recorded it. It is
invisible in every number the loop looked at, and it is the largest single effect in the table.

`[BP]` **The fix is to stop gating on the aggregate.** Chapter 39 already produces per-slice effects
with per-slice floors, and Chapter 41 §4.1 already insists a slice delta is never reported without its
floor. The change is to make the promotion rule read them:

- No slice may regress outside its own floor, whatever the aggregate does.
- The headline is the *worst* slice's delta, not the mean.
- A slice's weight in any composite is the customer mix, stated deliberately, rather than the
  benchmark's incidental composition.

`[INF]` That is a configuration change on machinery that already exists, and it converts the cold open
from an invisible drift into a blocked promotion at whichever iteration first proposed the trade. It
is the most actionable paragraph in this chapter.

### 5.4 The loop cannot see what it will break

`[AHE §4.4.2]` Fix prediction at roughly five times random; regression prediction at roughly two.

`[INF]` Chapter 45 §5.4 explained the asymmetry and it is not going to close. Predicting a fix means
reasoning forward from a diagnosed cause to the tasks that share it, and the evidence corpus is
organised around exactly that. Predicting damage means reasoning about tasks that are currently
passing, which appear in the corpus only as a contrast sample and about which almost nothing is
recorded — because nothing went wrong in them.

Three design consequences, all already built and worth collecting here:

- **Rollback is automatic** (Chapter 47 §5.5). A process that cannot see its damage cannot be the one
  that decides whether damage occurred.
- **The null at-risk claim is scored** (Chapter 45 §5.4). An empty list asserts *this breaks nothing*
  and is wrong often enough that its miss rate is a first-class metric.
- **The surprise-regression rate is tracked** (Chapter 47 §9). It is the production measurement of the
  ~2× figure, and without it the weakness stays a citation.

`[INF]` What none of that does is improve the prediction. The loop remains a process that walks forward
confidently and finds its damage by measurement afterwards, and every design decision in Chapters 45
through 47 is an accommodation of that rather than a remedy for it.

### 5.5 The containment list is a lower bound

Chapter 46 §5.2 collected eleven entries and §5.3 said what has to be said about them: every one was
found by an author writing about something else, pausing on a sentence, and noticing.

`[INF]` The trajectory is the argument. Chapter 31 §5.6 recorded the concern when the count was six
and said *six chapters found six items independently, which is not encouraging about the seventh*. By
Chapter 46 the deduplicated count was eleven. Five more entries arrived while nobody was looking for
them, which strengthens the concern rather than settling it: a discovery process still producing at
that rate has not converged.

`[BP]` Two responses, and neither is a solution:

- **Deny by default.** When a component's protection is not representable in the score, it starts
  outside the workspace, and the loop's refusals argue it back in through Chapter 46 §5.7. This is the
  standard posture for capability design and it is right here for a sharper reason than usual — the
  enumeration is known to be incomplete rather than suspected to be.
- **Watch the contested counts.** Chapter 46 §7.1's counter is the only signal that says the boundary
  is in the wrong place, and it says nothing at all about a boundary that should exist and does not.

`[FUT]` Chapter 46 §15 proposed the one mechanical route: for each configuration surface, ask whether
the benchmark's objective is monotonic in it. A surface where more is always better on the benchmark
and sometimes worse in production is a candidate entry, and the data to check is already produced.
Nobody has built it, and it would turn a lower bound into something with a coverage argument.

### 5.6 The self-modification gap

Chapter 31 §5.6 stated this and sent it here, with the instruction that a reader wanting a confident
answer should be told there is not one. That instruction stands.

The direct route is closed: the loop has no write path to the gate policy, the effect tags, the
capability broker's scope rules, the egress allowlist, the verifier, or the golden set. Chapter 46
made that structural rather than procedural, and it is a real answer to a real question.

Three gaps remain, in increasing order of seriousness.

**Nothing verified the write path continuously.** `[INF]` Chapter 31 raised this and Chapter 46 §10
partially closed it: the `scope.violated` event exists and any non-zero value is an incident. That
turns an implementation property into a monitored one, which is progress and is not a proof — the
event fires when a violation reaches the check, and says nothing about a path that does not.

**Nothing bounds indirect erosion.** `[INF]` This is the gap with no answer at all, and it deserves
concrete form because stated abstractly it sounds paranoid:

```
  The GATE POLICY requires approval for effectful tools, and is
  outside the workspace. The loop cannot edit it.

  It CAN edit a tool description so the model prefers a
  different, ungated tool that achieves a similar effect.

  The boundary is intact. It is also irrelevant, and every edit
  that made it so was inside the workspace, measured positive,
  and correctly attributed.
```

The same shape applies elsewhere. Redaction rules are contained; a tool implementation can write the
same content into a field the rules do not cover. The verifier is contained; a skill can shape outputs
toward what the judge scores well without touching the judge, which is Chapter 26 §14's
evaluator-isomorphic hazard arriving from the other direction.

`[INF]` No mechanism in this book detects any of that. The available defences are weak and worth
stating anyway: per-slice gating (§5.3) makes some erosion visible as a slice regression; the
mechanism check (Chapter 47 §5.2) notices when a gain arrives through an unclaimed route; and
Chapter 49's human review is the only thing that reads for intent rather than for effect.

**And the completeness gap sits underneath both.** `[INF]` An indirect route around a boundary that
should exist and does not is not detectable even in principle, and that composition of §5.5 with this
section is the honest floor of the current state of the art.

### 5.7 The undetermined residue

Chapter 47 added a fourth verdict for cases the arithmetic cannot decide, and the residue accumulates.

`[INF]` Each undetermined verdict leaves an edit in the workspace with no established effect. A few
are harmless. Across twenty iterations they become a population of components that are present,
unattributed, and interfering with everything else (§4) — and each one raises the interference term
against which the next edit is measured.

`[BP]` So the residue needs a disposal path, and Chapter 39 §5.6's removal experiment is it, aimed at
undetermined edits specifically. `[INF]` One benchmark run per candidate, spent on the oldest
undetermined edits first, and the ones that measure nothing on removal go. That is the only mechanism
in Level 5 that makes the harness smaller, and a loop without one accumulates monotonically by
construction.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  Ten iterations, and where the hard slice went.

  it    aggregate   Easy   Medium   Hard    what happened
  ----  ---------   ----   ------   -----   --------------------
   0      69.7      87.5    78.2    51.7    seed
   2      74.1      62.0    82.9    62.8    memory added: +11.1
                                            on Hard, -25.5 on
                                            Easy. Aggregate up,
                                            so KEEP.
   3      74.9      71.0    83.4    60.1    a middleware hook
                                            recovers Easy and
                                            costs Hard 2.7.
                                            Aggregate up: KEEP.
   5      75.8      88.0    85.1    56.4    two more Easy/Medium
                                            edits. Hard down
                                            another 3.7, each
                                            step inside the
                                            HARD slice's floor
                                            (6.0) and therefore
                                            never a regression.
   8      76.5      96.0    87.0    54.0
  10      77.0     100.0    88.2    53.3    ship

  THE TRADE, TOTALLED
    Easy    +12.5   Medium  +10.0   Hard  +1.6   aggregate +7.3

  AND THE COUNTERFACTUAL nobody ran
    memory alone, on Hard                    63.3
    the shipped harness, on Hard             53.3

  NOTE WHAT MADE IT INVISIBLE. No single iteration regressed the
  hard slice outside that slice's floor. Ten sub-floor steps in
  one direction sum to ten points, and every one of them was
  correctly judged UNDETERMINED or KEEP on the aggregate.

  FAILURE BRANCH -- what per-slice gating would have done (5.3):

    it 3   Hard -2.7, inside the floor -> permitted
    it 5   Hard cumulative -6.4 against a floor of 6.0
           -> OUTSIDE. PROMOTION BLOCKED.
    -- the rule that catches it is CUMULATIVE per slice against
       the seed, not per iteration against the last one. A
       per-iteration rule never fires, because the trade is
       made in sub-floor steps.

  Figure 48.4 -- Ten iterations, one slice, no alert (D4 Sequence)
```

### 6.1 The drift is sub-floor by construction, not by luck

`[INF]` The failure branch's last note is the transferable finding and it generalises past this
chapter. A per-iteration regression check compares against the previous iteration, so a drift made in
steps smaller than the floor is never detected — and an optimiser working against a noisy instrument
will naturally make small steps, because the large ones get caught.

The rule that works compares **cumulatively against the seed**, per slice. `[BP]` It costs nothing —
the seed's per-slice scores are Chapter 42 §8's standing-advantage measurement, already run on a
schedule — and it converts a class of drift that is undetectable by design into one that trips a gate.

`[INF]` This is also a second, independent argument for Chapter 43's non-deletable seed. Without a
fixed origin there is nothing to accumulate against, and the only available comparison is the
per-iteration one that cannot see the drift.

---

## 7. State Management

```
                                                            STATE VIEW

   THE LOOP'S TRAJECTORY, as a state rather than a curve.

      {{ improving }}      most verdicts KEEP or IMPROVE; the
          |                score rises outside the floor
          |
          |  new gains and rising interference approach
          |  cancellation (4.2)
          v
      {{ flattening }}     KEEP becomes rare; UNDETERMINED
          |                becomes the modal verdict (5.7).
          |                THIS IS NOT A DEFECT -- it is the
          |                search space, and C42 sec 5.5 said
          |                to expect it around iteration six
          |
          +---- the aggregate keeps rising while a slice falls
          |                                          |
          |                                          v
          |                                   {{ trading }}
          |                                    the cold open.
          |                                    Detectable ONLY by
          |                                    cumulative
          |                                    per-slice
          |                                    comparison (6.1)
          |
          v
      {{ exhausted }}      no new patterns in the corpus (C44's
                           E1) or the iteration budget is spent.
                           A statement about THIS BENCHMARK, not
                           about the harness

      ILLEGAL, and all three are ordinary team behaviour:

        * reading {{ flattening }} as a loop defect and
          responding by loosening a constraint (C46's cold open)
          or by widening claims (C45's).

        * shipping from {{ trading }} because the aggregate is
          up. It is up. It is up for one mix.

        * treating {{ exhausted }} as "the harness is optimal".
          It means the benchmark has no more to say, which is a
          fact about the corpus (C41 sec 5.6's drift).

  Figure 48.5 -- The loop's trajectory (D6 State Diagram)
```

### 7.1 Flattening is the expected outcome, and mislabelling it is expensive

`[INF]` A team that reads `{{ flattening }}` as underperformance will do one of three things, and the
book has a cold open for each: relax a containment constraint (Chapter 46), widen the claims so
precision recovers (Chapter 45), or ship more edits per iteration and lose attribution (Chapter 47).
All three make the loop look better and none makes the harness better.

`[BP]` Name the state explicitly in the operating procedure, with an expected iteration count, so that
arriving at it is a scheduled event rather than a disappointment.

### 7.2 Exhausted is a statement about the benchmark

Chapter 44's E1 exit — no new patterns — reads as convergence and is not. `[INF]` It means the corpus
has stopped producing failures the loop can act on, which is a joint fact about the harness *and* the
task corpus. Chapter 41 §5.6's corpus drift is the other half: a benchmark eighteen months old
measures a product the company no longer sells, and a loop that has exhausted it has fitted to
history.

`[BP]` The response to `{{ exhausted }}` is to add tasks, not iterations.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence


class SliceGate(Protocol):
    """The fixable limit, as a check. C39 already produces
    per-slice effects with per-slice floors; this reads them."""

    def blocks(
        self,
        candidate: "VersionTriple",
        seed: "VersionTriple",
        floor: "Floor",
    ) -> "SliceVerdict":
        """Compares CUMULATIVELY against the seed, per slice --
        not against the previous iteration.

        A per-iteration rule never fires on a trade made in
        sub-floor steps, which is how ten iterations moved a
        slice ten points without one regression being recorded
        (6.1).

        Requires the seed to be runnable, which is C43's
        non-deletable rule earning its keep a second time.
        """


class InterferenceEstimator(Protocol):

    def expected_combined(self, singles: Sequence["Advantage"]) -> "Range":
        """Given single-component gains, what should the
        combination deliver?

        Returns a RANGE with the naive sum as the upper bound.
        [AHE 4.4.1]'s one data point puts the realised figure at
        about two thirds of the sum; one observation is a thin
        basis for a coefficient, so this is a planning posture
        rather than a model (5.1).
        """


class ResidueSweeper(Protocol):
    """The only mechanism in Level 5 that makes the harness
    smaller (5.7)."""

    async def sweep(self, budget_runs: int) -> Sequence["RemovalResult"]:
        """Removal experiments (C39 sec 5.6) aimed at UNDETERMINED
        edits, oldest first.

        One benchmark run per candidate. An edit whose removal
        changes nothing outside the floor goes -- and the same
        result is also C43's overlap signal, read from the other
        end.
        """
```

`SliceGate.blocks` taking the seed rather than the incumbent is the whole of §6.1 in a parameter.
`[INF]` Every natural implementation compares against the previous version, because that is what a
promotion gate does everywhere else in software, and that is the version of this check that cannot
work.

`InterferenceEstimator.expected_combined` returning a range rather than a number is deliberate
honesty. `[BP]` A point estimate derived from a single published ablation would be used as a forecast,
and there is no basis for that; a range with the sum as an upper bound carries the one thing actually
established, which is that the sum is too high.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SliceVerdict:
    """Cumulative, per slice, against the seed (6.1)."""
    per_slice_cumulative_pp: dict[str, float]
    per_slice_floor_pp: dict[str, float]
    worst_slice: str                    # the headline, instead of
                                        # the mean (5.3)
    blocks_promotion: bool              # any slice below -floor
    customer_weighted_delta: float      # the mix stated
                                        # deliberately, not the
                                        # benchmark's incidental one


@dataclass(frozen=True)
class InterferenceRecord:
    """What a combination actually delivered against the sum of
    its parts."""
    components: tuple[str, ...]
    singles_sum_pp: float
    combined_pp: float
    shortfall_pp: float                 # +11.1 -> +7.3 is 3.8
    mechanism: str | None               # redundant_closure |
                                        # mechanism_shift |
                                        # budget_contention;
                                        # None because nobody has
                                        # decomposed a real gap (5.2)


@dataclass(frozen=True)
class TrajectoryState:
    iteration: int
    state: str                          # improving | flattening |
                                        # trading | exhausted
    undetermined_share: float           # modal in {{ flattening }}
    resident_component_count: int       # 4.2: interference grows
                                        # with this, monotonically
    worst_slice_cumulative_pp: float    # the cold open's number,
                                        # had anyone computed it
```

`InterferenceRecord.mechanism` defaulting to `None` is the chapter being honest in the type system.
`[INF]` The three mechanisms in §4 are the handbook's account of why the gap is as large as measured,
and no published work decomposes a real gap into them — so a field that forced a choice would
manufacture a confidence nobody has.

`TrajectoryState.worst_slice_cumulative_pp` is the single number that would have prevented the cold
open. `[INF]` It is computable from artefacts that already exist — the seed's per-slice scores and the
current run's — and the reason nobody had it is that no chapter before this one asked for it.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Benchmark (C41) | Slice gate | Per promotion | Per-slice deltas with per-slice floors |
| Seed (C43) | Slice gate | On a schedule | The cumulative baseline (§6.1) |
| Verdict history (C47) | Trajectory state | Across iterations | The undetermined share, and the state |
| Registry (C43) | Trajectory state | Per iteration | Resident component count (§4.2) |
| Undetermined edits (C47) | Residue sweeper | Oldest first | Removal candidates (§5.7) |
| Contested counts (C46) | **Chapter 49** | Standing | The only signal about the boundary's placement |
| This chapter | **Chapter 49** | The whole of it | What a human must be positioned to catch |

`[INF]` The last row is the chapter's actual output. Every limit here that cannot be designed away
becomes a requirement on the review process — which is why Chapter 48 is written before Chapter 49
rather than after it, so that governance is a response to a measured blindness rather than a general
precaution.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| A roadmap built on summed single-component gains | The quarter's delivery, a third short | Discount by roughly a third; treat the sum as an upper bound (§5.1) |
| A slice traded away in sub-floor steps | Cumulative per-slice against the seed — and nothing else | Per-slice gate, cumulative, not per-iteration (§5.3, §6.1). The cold open |
| Shipping on the aggregate | The customer, six weeks later | The worst slice is the headline (§5.3) |
| Flattening read as underperformance | Constraints relaxed, claims widened, edits per iteration raised | Name the state, with an expected iteration count (§7.1) |
| Exhausted read as optimal | The benchmark stops producing patterns | Add tasks, not iterations (§7.2) |
| Undetermined edits accumulating | Resident component count rising with no attributed gains | Removal experiments on the residue (§5.7) |
| Indirect boundary erosion | Nothing; every edit was permitted and measured positive | Per-slice gating, the mechanism check, and human review (§5.6) |
| A containment entry that should exist and does not | Nothing, in principle | Deny by default (§5.5) |
| Interference mistaken for overlap | A component removed because it "did nothing" | Probe distinguishes them; interference is not a defect (§4.1) |
| Single-component numbers reused after the harness changed | Predictions that were right once | Mechanism shift: a single measured against the seed is a fact about the seed (§5.2) |

`[INF]` Rows seven and eight are the two entries in this book whose detector column is *nothing* and
for which no instrument is proposed. Every other undetected failure in the handbook is undetected
because somebody has not built the measurement. These two are undetected because the thing to measure
has not been characterised, and saying so is more useful than proposing a check that would not work.

---

## 12. Scalability

**Nothing in this chapter gets better with scale, and two things get worse.** `[INF]` Interference
grows with the resident component count (§4.2), and the undetermined residue grows with iteration
count (§5.7). Both mean the loop's marginal iteration is less productive than its first, and neither
is fixed by more compute.

**Per-slice gating costs nothing and its cost does not grow.** `[BP]` The per-slice effects are already
computed (Chapter 39), the seed's scores are already re-measured on a schedule (Chapter 42 §8), and
the gate is a comparison. This is the rare case where the fix for the largest problem in the chapter
is free.

**The residue sweep is one benchmark run per candidate** and competes with the loop's own iterations
for the model semaphore. `[BP]` Chapter 41 §4.2's reserved-but-preemptible evaluation class is where
it belongs, and a fixed small allocation — a few sweeps per week — is enough, because the residue
grows slowly.

**Measuring interference properly does not scale at all.** `[INF]` Every pair is a benchmark run:
twenty-one runs for seven components, and every combination is 2^n. That is why §5.1's answer is a
planning posture rather than a measurement, and it will stay one.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Worst-slice cumulative delta against the seed.** The number that would have prevented the cold
  open, computable from artefacts that already exist.
- **Undetermined share of verdicts, per iteration.** The trajectory state, made numeric. Rising past
  about half is `{{ flattening }}`.
- **Resident component count.** Interference's leading indicator (§4.2), and the input to the removal
  schedule.
- **Realised-versus-summed gain, whenever a combination ships.** Every instance is a data point on the
  one coefficient this chapter had to guess.
- **Contested-constraint counts** (Chapter 46 §7.1). Not a limit of the loop, but the only evidence
  about the boundary's placement, and Chapter 49 reads it.

### 13.2 The review question

Before shipping any evolved harness: **which slice got worse, and by how much against the seed?**

`[INF]` The question has an answer or it does not, and if it does not, that is the finding. It is one
query over data that already exists, it takes a minute, and the cold open's team could have asked it
at any point in six weeks.

### 13.3 Teaching this to a new engineer

Give them the ablation table and ask which single component is best. Everyone says long-term memory —
75.3% against a 69.7% seed, the largest single gain.

Then show them the Easy column: 50.0% against a seed's 87.5%.

`[INF]` The instinct that installs is the last in this level and it is the same one, aimed at an
average this time. *Worth what, against what baseline* (Chapter 42). *What else could be doing this*
(Chapter 43). *What would I have to see to know I am wrong* (Chapter 44). *What would have made this
claim fail* (Chapter 45). *What is this number not measuring* (Chapter 46). *What else could have
caused this* (Chapter 47). And here: **who is this average hiding?**

---

## 14. Relation to the Base Runtime

**What the base runtime supplies.** `[DAR §9.2]` The verdict lattice and per-slice grading are what
make §5.3's fix possible at all — a runtime that reported one aggregate quality number could not
express a slice gate. `[DAR]` The version triple makes the seed re-runnable against today's model,
which is what a cumulative comparison requires.

**What this chapter adds.** `[INF]` A sorting of the limits by remediability, which the source does not
attempt; the three interference mechanisms behind the measured non-additivity; the finding that a
slice trade is made in sub-floor steps and therefore needs a cumulative rather than a per-iteration
gate; the undetermined residue and its disposal path; and the trajectory states, so that flattening is
a scheduled event rather than a disappointment.

**What the loop owes the runtime.** Honesty about which of its numbers are aggregates. `[INF]` The
runtime's job in this relationship is to keep producing per-slice measurements even when nothing is
reading them, because the cold open's data existed for ten iterations and nobody computed the
difference.

**And the honest limit, which is this chapter's whole subject.** `[AHE Limitations]` One benchmark
family, a bounded iteration count, non-additive gains, weak regression prediction. `[INF]` The
handbook adds two more: containment is a lower bound with no completeness argument, and indirect
erosion of a boundary is undetected by anything anyone has built. A reader who wants a confident
answer on the last one should be told, as Chapter 31 §5.6 instructed, that there is not one.

---

## 15. Industry Perspective

**`[AHE §4.4.1]`** Non-additivity: three positive single-component gains summing to +11.1 delivering
+7.3 together, the per-tier ablation table, and redundant closure as the source's own explanation.
`[AHE §4.4.2]` Fix prediction at roughly five times random against regression prediction at roughly
two. `[AHE Limitations]` The controlled-prototype framing.

**`[DAR §9.2]`** Per-slice verdicts, without which the fixable limit is not expressible.

**`[INF]`** The handbook's own: sorting the four limits by remediability and identifying the slice
trade as the only one with a cheap fix; mechanism shift and budget contention as the two interference
mechanisms the source does not name, and the observation that mechanism shift explains an inversion
rather than a shortfall; the sub-floor-steps argument and the cumulative-against-seed gate that
follows from it; the undetermined residue and the removal sweep as the only mechanism that shrinks a
harness; the trajectory states; and the concrete form of indirect boundary erosion in §5.6.

**`[BP]` Simpson's paradox is the textbook version of §5.3** and it is taught in every statistics
course, which is a useful thing to know when explaining this to a team: an aggregate can move one way
while every subgroup moves the other. What is specific here is that the aggregate is also the
*objective*, so the effect is not a reporting artefact — it is what the system was asked to maximise.

**`[BP]` Portfolio correlation is the closest mature analogue for non-additivity**, and its practice
transfers: nobody sums backtested strategy returns, everybody expects the combination to
under-deliver, and the discipline is to measure the combination. The part that does not transfer is
the covariance matrix, because measuring it here costs a benchmark run per pair.

**`[FUT]` A coefficient for the discount in §5.1 does not exist.** One published ablation gives one
ratio. `[FUT]` Whether the shortfall scales with component count, with the enforcement levels
involved, or with the resident context share is unmeasured, and every team running this loop generates
the data to answer it without anyone collecting it.

**`[FUT]` Detecting indirect boundary erosion is open and, in the handbook's view, the most important
unsolved problem in this level.** Everything else here is a limit to design around. This one is a
route by which the safety argument becomes false without any of its mechanisms failing.

---

## 16. Key Takeaways

1. **Gains do not stack.** Three positive single-component gains summing to +11.1 points delivered
   +7.3 together. Discount a summed roadmap by roughly a third and treat the sum as an upper bound.
2. **Three mechanisms explain it**, and only the first is in the source: redundant closure, mechanism
   shift, and budget contention. Mechanism shift is why the combination can be *worse* than a member,
   not merely less than the sum.
3. **The aggregate hides a trade, and this is the fixable one.** Gate per slice, cumulatively against
   the seed. Ten iterations moved a slice ten points in sub-floor steps and no iteration recorded a
   regression.
4. **The loop cannot see what it will break.** Roughly five times random forward, two times backward.
   Automatic rollback, a scored null at-risk claim, and a tracked surprise rate are accommodations,
   not remedies.
5. **The containment list is a lower bound.** It went from six entries to eleven while nobody was
   looking for more, which is not evidence of convergence.
6. **Indirect erosion is unaddressed.** A loop that cannot edit a boundary can propose changes that
   make it irrelevant, every edit permitted and measured positive. Nothing detects this, and it is the
   most important open problem in Level 5.
7. **Flattening is the expected outcome, not underperformance.** Reading it as a defect leads to
   relaxing a constraint, widening a claim, or shipping more edits per iteration — three cold opens,
   all of which make the loop look better and none of which makes the harness better.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Interference** | Components whose effects do not add because each changes what the model perceives, and therefore the others' mechanism. | `[INF]` | Ch 49 |
| **Redundant closure** | Several components pushing toward the same behaviour, so stacking them buys it once and pays for it repeatedly. | `[AHE]` | Ch 49 |
| **Mechanism shift** | One component changing the conditions under which another's effect exists, which is why a combination can be worse than a member. | `[INF]` | Ch 49 |
| **Slice trade** | An edit that buys points in a heavy slice with points in a light one, which raises the aggregate and is invisible in it. | `[INF]` | Ch 49 |
| **Sub-floor drift** | A cumulative movement made in steps each smaller than the noise floor, undetectable by any per-iteration check. | `[INF]` | Ch 49 |
| **Per-slice gate** | A promotion rule reading cumulative per-slice deltas against the seed, which is the one cheap fix in this chapter. | `[BP]` | Ch 49 |
| **Undetermined residue** | The accumulating population of edits kept with no established effect, which raises interference against every later measurement. | `[INF]` | Ch 49 |
| **Convergence flattening** | The state in which new gains and rising interference cancel, expected around iteration six and routinely mistaken for a defect. | `[INF]` | Ch 49 |
| **Indirect boundary erosion** | Achieving a contained end by editing something permitted, leaving the boundary intact and irrelevant, detected by nothing. | `[INF]` | Ch 49 |

---

**Next:** Chapter 49 — *Continuous Improvement and Governance.* Every limit in this chapter that
cannot be designed away becomes a requirement on the people around the loop. The final chapter is
about running it as production infrastructure: what a human review consists of when nobody can read
the trajectories, where the gates go, and how to talk about a controlled prototype without either
overselling it or refusing to ship it.
