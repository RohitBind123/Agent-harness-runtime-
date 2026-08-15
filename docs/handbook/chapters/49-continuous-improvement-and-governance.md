```
  Level 5 · Chapter 49
  CONTINUOUS IMPROVEMENT AND GOVERNANCE
  Requires   C30 Human Authority,
             C37 Tenancy, Secrets, and Data Governance,
             C46 The Evolve Agent, C48 Limits
  Unlocks    -- the book ends here
  Diagrams   Core (5)
```

# Chapter 49 — Continuous Improvement and Governance

---

## 1. Motivation

### 1.1 Cold open

Atlas's evolution loop has a weekly review. It is on the calendar, two engineers attend, and it has
never been skipped.

The review looks at four things: the aggregate score, the iteration count, the cost, and the list of
edits shipped. All four have looked healthy for five months.

In month six a compliance question arrives from a customer. Who has read our source code?

The answer takes eleven days to assemble. The distiller has read trajectories from 61,000 runs,
including that customer's, on every iteration since the loop started. It was never granted access. It
inherited it, because the trace store had one read path and the distiller used it.

The review had never asked. Nothing on the agenda was about access, because the agenda was about
whether the loop was working.

While they are in the data, they check the other things nobody had been asked to look at. Three
containment constraints had been relaxed, each by a different engineer, each in a single commit. The
hard slice was down 9.1 points against the seed. Twenty-two edits sat in the workspace with
undetermined verdicts.

Every one of those numbers had existed for months.

None of them was on the agenda, and the agenda was the review.

### 1.2 In plain language

The last chapter listed the things this system cannot do for itself. This one is about the people
standing next to it.

The awkward part is that nobody can supervise it by watching. It makes hundreds of decisions a week,
each one recorded in detail, and reading them is not an option — not because people are lazy but
because there is more material than a person can get through, which is the same problem the loop
itself was built to solve.

So supervision has to be a fixed list of numbers, looked at on a schedule, chosen so that each one
would catch a specific thing going wrong. That sounds bureaucratic and it is the only version that
works. The cold open's review was attentive, regular, and well-intentioned, and it watched four
healthy numbers while four unhealthy ones sat in the same database.

The other half is deciding which choices a machine may never make alone. Not many, and they are
specific: promoting a change to real users, moving one of the boundaries it is not allowed to cross,
and widening what data it can learn from. Everything else it can do by itself.

And one thing this chapter argues that may be counter-intuitive: a system that improves itself needs
*more* human involvement than one that does not, not less.

### 1.3 Why this chapter exists

Chapter 48 sorted the loop's limits and found three that cannot be designed away. Each one ends
somewhere an instrument does not reach: a boundary eroded indirectly, a constraint relaxed by a
person under pressure, an aggregate that hid a trade. `[INF]` Residual risk concentrates exactly where
the measurements stop, which is the definition of what review is for.

The difficulty is that review does not scale, and five earlier chapters said so while deferring the
answer here. Chapter 45 §12: a human cannot read hundreds of manifest entries a week and will read
none rather than some. Chapter 46 §12: the displacement records are the part that a person must act
on. Chapter 16 §10.1: somebody has to be able to say who read which trajectory. Chapter 20 §14: the
two loops are separated by a human decision, and this chapter is about when that separation may be
relaxed and what has to be true first.

`[AHE Limitations]` supplies the framing this chapter has to end on: a controlled prototype, one
benchmark family, a bounded iteration count. `[INF]` The contribution here is the operational shape —
a fixed scan, three gates, one gate to delete, and a staged answer to the autonomy question — plus
the closing proposal Chapter 3 §14 deferred: running the evolution campaign as a Run inside the
runtime it is evolving.

### 1.4 What previous framings got wrong

**"A self-evolving system needs less oversight, because it fixes itself."** Chapter 0 §14 planted the
opposite and Chapter 48 supplied the evidence. `[INF]` A static system's behaviour changes when
someone changes it. This one's changes weekly, from decisions nobody read, with a predictor that sees
half its own effect. That is more supervision, not less — and it is a different *kind*, because
watching is not available.

**"We review the loop's output."** The cold open reviewed the loop's output. Four healthy numbers,
five months, and everything that was wrong was outside the agenda. `[INF]` A review is its agenda;
competence and attendance do not compensate for the wrong list.

**"Add an approval step."** Chapter 7 §14 already named the failure: an approval that is always
granted is a gate that should be removed. `[INF]` Gates that never refuse train everyone to click
through them, and they consume the attention the two or three real gates need.

**"Governance is about preventing misuse."** Mostly it is about noticing drift. `[INF]` Nothing in
this book's failures required a bad actor: the loop optimising its instructions, an engineer moving a
constraint that was binding, a distiller inheriting a read path. Misuse deserves a paragraph (§5.5);
drift deserves the chapter.

**"Ship it when it is finished."** It is a controlled prototype and it will stay one for a while.
`[INF]` The honest position is neither to oversell it nor to refuse to run it — it is to run it inside
a boundary sized to what has actually been demonstrated, and to say plainly which parts are
demonstrated (§5.5).

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

The flight crew of an aircraft on autopilot.

In cruise the crew cannot fly the aircraft better than the automation, and everyone involved knows
it. Their job is not to fly; it is to monitor, to maintain awareness of which mode is engaged, and to
know when to disconnect. The discipline that makes that work is a **scan** — a fixed pattern across a
fixed set of instruments, in the same order, at intervals — because free-form attention drifts toward
whatever is most interesting rather than toward whatever is most likely to be wrong.

And the industry's characteristic accident is not an inattentive crew. It is *automation surprise*: a
competent, attentive crew, monitoring carefully, looking at the wrong indicator while the automation
does something reasonable that nobody expected. That is the cold open, with a different set of dials.

**Where it breaks**, in two ways, and the second is uncomfortable enough that no source raises it.

An aircraft's automation has a **bounded, enumerated mode set**. The crew can know every mode, an
annunciator says which is engaged, and "what is it doing now" has an answer on a panel. This loop's
state is the accumulated content of a harness directory that nobody has read end to end, and there is
no annunciator. `[INF]` Chapter 43's inventory is the closest thing available and it reports shape
rather than behaviour — how many components of each type, not what they collectively do.

And a crew can **disconnect and fly manually**, with that skill maintained by regulation and recurrent
training. Disconnecting here means a team re-fitting the harness by hand, which Chapter 42 §4 measured
at eighteen days with eleven of them needing a person who holds the whole thing in their head.
`[INF]` That capability decays precisely because the loop is doing the work — the harness grows past
what anyone has read, the people who understood it move on, and the fallback that governance assumes
is available quietly stops being. Nobody in this literature has proposed the equivalent of recurrent
training, and this handbook does not have one either (§13.3).

### 2.2 Why governance must be a fixed scan rather than an inspection

```
  (1) The loop makes hundreds of decisions a week and every one
      is recorded. Reading them is not available -- it is the
      same volume problem C44 was built to solve, aimed at a
      person.

  (2) C48 found three limits that cannot be designed away, and
      each ends somewhere no instrument reaches: indirect
      erosion, a constraint relaxed by a person, an aggregate
      hiding a trade.

  (3) So residual risk concentrates exactly where the
      measurements stop. That is what review is for, and it is
      NOT what review usually does.

  (4) But review does not scale. A person given a large surface
      and no list reads the interesting part, which is the
      score, which is the one thing already monitored.

  (5) So review must be a FIXED SCAN over computed numbers,
      each chosen because it catches a specific failure. Not an
      inspection; a checklist.

  (6) And the agenda must include what no number reports --
      access, relaxations, and intent -- because the cold open's
      four healthy numbers coexisted with four unhealthy ones
      that were never on it.

  (7) Separately, a small number of decisions must not be made
      by the loop at all. Not many: promotion to users, moving a
      containment boundary, and widening what it may learn from.

  (8) Fixed scan, three gates, a named owner. Nothing more
      elaborate survives contact with a loop that runs daily.
```

Step (4) is why elaborate governance designs fail quietly. `[INF]` A review defined as "the team looks
at the loop" degenerates within a month into looking at the score, because the score is the one number
that is legible without preparation — and the score is precisely the number Chapter 48 showed can rise
while the thing you care about falls.

### 2.3 Three gates and one scan

| | What it is | Frequency | Who |
|---|---|---|---|
| **Gate 1 — Promotion** | An evolved harness reaching users, with Chapter 48's per-slice cumulative rule | Per promotion | The team that owns the product surface |
| **Gate 2 — Relaxation** | Moving a containment entry (Ch 46 §5.7) | Rare, and never during an iteration | A named owner outside the loop's reporting line |
| **Gate 3 — Scope** | Widening what the loop may learn from, above all production traffic (Ch 37 §14) | Rare | Whoever owns the customer contract |
| **The scan** | A fixed agenda of computed numbers | Weekly | Anyone; the point is the list |

`[INF]` Three gates is deliberately few. Chapter 7 §14's rule — an approval that is always granted is a
gate that should be removed — applies with force to a process running daily: every gate that never
refuses spends attention that the ones which do refuse need. §5.2 covers which gate most organisations
add and should not.

### 2.4 The mental model to carry

> **A review is its agenda.** Everything not on the list is unmonitored, however competent and
> attentive the reviewer — and the number that is legible without preparation is the one that can rise
> while the thing you care about falls.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   THE INNER LOOP (C18)          runs, per second
   +--------------------------------------------------------------+
   |  human authority here is C30's: gates, steers, overrides      |
   +--------------------------------------------------------------+

   THE OUTER LOOP (C46)          iterations, per day
   +--------------------------------------------------------------+
   |  reads evidence, proposes, commits -- unattended               |
   +---+------------------+------------------+--------------------+
       | (1) ledger       | (2) displacement | (3) contested
       |     queries      |     records      |     counts
       v                  v                  v
   +--------------------------------------------------------------+
   |                      THE WEEKLY SCAN                         |
   |   eleven computed numbers, fixed order, fixed list (5.1)      |
   |   -- the ONLY routine human contact with the loop             |
   +---+----------------------------------------------------------+
       |
       | (4) escalations, when a number is out of band
       v
   +----------------+  +-------------------+  +--------------------+
   |  GATE 1        |  |  GATE 2           |  |  GATE 3            |
   |  PROMOTION     |  |  RELAXATION       |  |  SCOPE             |
   |                |  |                   |  |                    |
   |  per-slice,    |  |  a containment    |  |  learning from     |
   |  cumulative    |  |  entry moves      |  |  production        |
   |  vs the seed   |  |  (C46 sec 5.7)    |  |  traffic (C37)     |
   |  (C48 sec 5.3) |  |                   |  |                    |
   |  BLOCKS users  |  |  BLOCKS the edit  |  |  BLOCKS the data   |
   +-------+--------+  +---------+---------+  +---------+----------+
           |                     |                      |
           +---------------------+----------------------+
                                 |
                                 v
                       +-------------------------+
                       |  A NAMED OWNER          |
                       |   outside the loop's    |
                       |   reporting line (2.3)  |
                       +-------------------------+

   NOT A GATE, and this is deliberate:
     --X  approval of individual edits. There are hundreds a
          week; an approval that is always granted is a gate
          that should be removed (C7 sec 14, and 5.2)

  Figure 49.1 -- Where the humans are (D1 High-Level Architecture)

  (1) C45 sec 5.7's six queries -- the manifest read in aggregate
  (2) C46's out-of-scope routings: where a human should be
      changing something the loop may not
  (3) C46 sec 7.1: the only signal about the boundary's placement
  (4) the scan does not decide; it routes to a gate or to nobody
```

### 3.1 The scan does not decide

`[INF]` Figure 49.1's wire (4) is the design decision that keeps the arrangement workable. The scan
is a detector, not a decision forum: its output is either *nothing is out of band* or *this number is,
and it routes to this gate*. Discussion happens at the gate, with the specific decision in front of a
named person.

The alternative — a weekly meeting that both monitors and decides — is what the cold open's review
was, and it has a predictable failure. `[BP]` A forum that can decide will spend its time on whatever
is most discussable, which is never the number nobody understands yet.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                     THE REVIEW FUNCTION                        |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   The scan               |  |   The three gates         |   |
   |  |                          |  |                           |   |
   |  |  eleven numbers, fixed   |  |  promotion, relaxation,   |   |
   |  |  order, computed before  |  |  scope. Each BLOCKS       |   |
   |  |  the meeting starts      |  |  something specific.      |   |
   |  |                          |  |                           |   |
   |  |  each entry names the    |  |  a gate that has never    |   |
   |  |  failure it catches;     |  |  refused is reviewed for  |   |
   |  |  an entry that catches   |  |  DELETION (5.2)           |   |
   |  |  nothing is removed      |  |                           |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Access audit           |  |   Cleanup schedule        |   |
   |  |                          |  |                           |   |
   |  |  who read which          |  |  removal experiments on   |   |
   |  |  trajectory, INCLUDING   |  |  the undetermined residue |   |
   |  |  machine readers         |  |  (C48 sec 5.7), memory    |   |
   |  |  (C16 sec 10.1)          |  |  rot (C1), and            |   |
   |  |                          |  |  instruction accretion    |   |
   |  |  verbatim pull share is  |  |  (C39 sec 5.6)            |   |
   |  |  the cost-and-exposure   |  |                           |   |
   |  |  number (C44 sec 13.1)   |  |  REMOVAL IS A FIRST-CLASS |   |
   |  |                          |  |  OPERATION (C6 sec 12)    |   |
   |  +--------------------------+  +---------------------------+   |
   +----------------------------------------------------------------+

  Figure 49.2 -- Inside the review function (D2 Low-Level
                 Architecture)
```

### 4.1 An entry that has never caught anything is removed

`[INF]` The scan is subject to the same discipline it enforces. A number on the list that has never
been out of band, over a year, is either measuring something that does not vary or measuring it
wrongly — and it costs attention every week either way.

`[BP]` Review the scan annually against what it caught. `[INF]` This is Chapter 39 §5.6's removal
experiment applied to the governance process itself, and the symmetry is not a rhetorical flourish:
agendas accrete exactly the way instruction files do, each addition individually justified, none ever
removed, and the cost paid at every meeting forever.

### 4.2 Cleanup is scheduled work, not a cleanup sprint

Chapter 6 §12 said it before Level 5 existed: **removal is a first-class operation and it is the one
most often left unimplemented.**

`[INF]` Three separate accumulations converge on the same schedule. Chapter 48 §5.7's undetermined
residue — edits kept with no established effect, raising interference against everything measured
afterwards. Chapter 1 §11's memory rot — lessons that no longer hold, diluting the ones that do.
Chapter 39 §5.6's instruction accretion — each addition justified, none removed, paid for on every
call forever.

`[BP]` All three are addressed by the same mechanism, a removal experiment costing one benchmark run,
and all three need a standing allocation rather than a periodic campaign. A few sweeps a week,
oldest-first, in Chapter 41 §4.2's reserved-but-preemptible class. `[INF]` A cleanup sprint is what
happens instead, once a year, when somebody notices the harness has doubled — and by then the
interference it introduced has been in every measurement for months.

---

## 5. The Scan, the Gates, and What Governance Owes

### 5.1 The scan

```
                                                            LAYER VIEW

   ELEVEN NUMBERS, FIXED ORDER, COMPUTED BEFORE THE MEETING

   #   number                        catches                  from
   --  ---------------------------   ----------------------   -----
    1  worst-slice cumulative        the slice trade, in      C48
       delta vs the SEED             sub-floor steps          5.3
    2  undetermined share of         flattening mistaken      C47
       verdicts                      for underperformance     C48
    3  surprise-regression rate      the loop's blind half    C47
    4  mean predicted claim width    claims widening until    C45
       WITH precision                precision is meaningless 5.3
    5  constraint-level              default-owner decay      C43
       distribution                                           C44
    6  contested-constraint counts   the boundary in the      C46
                                     wrong place              7.1
    7  displacement count per        a human should be        C46
       contained class               changing something       5.6
    8  trajectory reads by reader,   the cold open            C16
       including machine readers                              10.1
    9  verbatim pull share           standing exposure,       C44
                                     and cost                 13.1
   10  resident component count      interference, rising     C48
                                     monotonically            4.2
   11  edits outside the write       ANY non-zero is an       C20
       scope                         incident, not a metric   13.1

   ====> total compute: seconds. Every number is a query over
         artefacts that already exist.

   ====> total reading: one page, once a week.

   THE COLD OPEN'S REVIEW watched the score, the iteration
   count, the cost, and the edit list. Numbers 1, 6, 8, and 2
   were all out of band for months and none was on the page.

   AND NOTE WHAT IS ABSENT. The aggregate score is not on this
   list. It is monitored elsewhere, it is the number everyone
   looks at anyway, and it is the one C48 showed can rise while
   number 1 falls.

  Figure 49.3 -- The weekly scan (D7 Data Flow)
```

`[BP]` Two properties matter more than the specific contents. **Computed before the meeting**, so the
time is spent reading rather than gathering — a scan that requires someone to run queries live becomes
a scan that happens when that person is available. And **fixed order**, for the reason aviation fixes
a scan order: attention drifts toward the interesting, and number 8 is never the interesting one until
the day it is.

### 5.2 Three gates, and the one to delete

`[INF]` The gates are few because attention is the scarce resource and every gate spends some.

**Gate 1, promotion.** Chapter 39's pipeline, with Chapter 48 §5.3's rule replacing the aggregate
check: no slice may regress outside its own floor, cumulatively against the seed, whatever the
aggregate does. `[BP]` This is the single highest-value change in this chapter and it costs a
configuration edit, because Chapter 39 already computes per-slice effects and Chapter 42 §8 already
re-runs the seed.

**Gate 2, relaxation.** Chapter 46 §5.7's procedure, gated by a named owner outside the loop's
reporting line. `[INF]` The separation matters for the same reason it matters on a trading desk: the
person who wants the constraint moved is the person whose work it is blocking. The cold open had three
relaxations by three engineers in three single commits, and no step in the process was wrong because
there was no process.

**Gate 3, scope.** Widening what the loop may learn from. `[INF]` Chapter 37 §14 calls learning from
production trajectories the obvious and valuable next step, and it is also the change that moves the
loop from reading a benchmark corpus to reading customer material at scale. That is a contract
question rather than an engineering one, and it belongs with whoever owns the contract.

**And the gate to delete: per-edit approval.** `[INF]` It is the first thing most organisations add and
it fails in the specific way Chapter 7 §14 named. A person cannot meaningfully approve hundreds of
manifest entries a week, so they approve all of them, so the gate never refuses — and Chapter 7's own
observation is that the decision log makes this *measurable*: an approval that is always granted is a
gate that should be removed, and the data to prove it is a durable row with a timestamp and a signer.

`[BP]` Measure every gate's refusal rate. A gate at zero over six months is theatre, and theatre is
not free — it consumes the attention the other gates need and it teaches everyone that gates are
clicked through.

### 5.3 Access is a governance surface

The cold open's actual failure, and it was deferred here by two chapters.

`[INF]` The distiller has standing, automated, high-volume read access to the most sensitive dataset
in the architecture (Chapter 16 §5.6). It was never granted that access. It **inherited** it, because
a read path existed and the component used it — which is how almost every automated reader in every
system acquires its permissions.

Four controls, all of which exist elsewhere in this book and none of which is automatic:

- **Redaction at capture** (Chapter 16 §5.4). Already the rule, and it is the one that limits the
  damage rather than the exposure.
- **Structural by default** (Chapter 44 §5.6). The loop reads calls, order, verdicts, and cost;
  verbatim content is pulled per field, by exception. `[INF]` This makes the standing access narrow, so
  the audit surface is the exceptions rather than everything — which is what makes an audit possible
  at all.
- **The read audit, including machine readers** (Chapter 16 §10.1). `[BP]` Reviewed, not alerted:
  volume makes alerting useless, and the question is always asked retrospectively.
- **Verbatim pull share on the scan** (number 9). Cost and exposure in one number.

`[INF]` The eleven days the cold open's team spent were not spent deciding anything. They were spent
reconstructing a fact that a log would have answered in a query, and the log did not exist because
nobody had asked the question before a customer did.

### 5.4 Cleanup, and why nobody does it

§4.2 gave the mechanism. The reason it is skipped is worth naming because it is structural rather than
cultural.

`[INF]` A removal experiment costs a benchmark run and its best outcome is that nothing happens. There
is no artefact, no gain to report, and a small chance of a regression that must then be explained. It
is the same shape as measuring a noise floor (Chapter 41 §5.1) and running a counterfactual
(Chapter 42 §5.1): work that produces no result anyone asked for, and whose absence has no symptom.

`[BP]` So it is scheduled rather than prioritised. A standing weekly allocation, oldest-first, that
nobody has to justify — because anything requiring justification loses to anything that produces a
number.

`[INF]` And it is the one activity in Level 5 that makes the harness *smaller*, which matters more
than it sounds: every other mechanism in this level adds. A loop without a disposal path accumulates
monotonically by construction, and interference (Chapter 48 §4.2) grows with the pile.

### 5.5 Misuse, and the honest framing

Misuse first, because it is the shorter half.

`[INF]` Nothing in this book's failures required a bad actor, and a design that centres on one will
get the common cases wrong. The realistic misuse is mundane: pointing the loop at a benchmark that
flatters a decision already made, relaxing a constraint before a deadline, or quoting the aggregate to
a customer whose slice went down. `[BP]` Each is addressed by the scan, the gates, and a named owner
rather than by anything specific to intent.

The deliberate case worth naming is **evaluation capture**: choosing the corpus, the weighting, or the
attribution model because of what it will show. Chapter 47 §15 said it plainly for attribution models
and it generalises — they get chosen by whoever they flatter, which is a governance problem rather
than a statistical one. `[BP]` The control is that corpus composition and slice weighting are gated
changes with a recorded rationale, on the same footing as a containment relaxation.

Then the framing, which the book owes its reader at the end.

`[AHE Limitations]` The source is explicit: one benchmark family, a bounded iteration count,
non-additive gains, weak regression prediction. `[INF]` The honest position is neither of the two
comfortable ones. It is not *this is solved and you should run it unattended*, and it is not *this is
unproven and you should wait*. It is:

- **What is demonstrated.** Harness quality is a large measurable surface — over seven points on a
  fixed model — and an automated loop can improve it unattended across ten iterations.
- **What is not.** That gains compound, that they transfer across models or benchmarks, that the loop
  can predict its own damage, or that the containment list is complete.
- **What follows.** Run it inside a boundary sized to what is demonstrated: on a benchmark rather than
  production traffic, proposing rather than deploying, with the three gates and the scan. That is a
  real system doing real work, described accurately.

### 5.6 More governance, not less

Chapter 0 §14 planted this claim before the reader knew what a harness was, and Level 5 is what
grounds it.

`[INF]` The intuition it corrects is natural: a system that improves itself should need less
attention over time, the way a maturing codebase does. The opposite holds, for three reasons this
level established rather than asserted.

**Its behaviour changes without anyone changing it.** A static system moves when someone moves it,
and the review surface is the diff. Here the diff is hundreds of edits a week that nobody reads, and
the harness after twenty iterations is a system no person has read end to end.

**It optimises what it can measure, and the protections are what it cannot.** Chapter 46's eleven
containment entries are eleven instances of one property, and the list is a lower bound. Every
protection outside the reward is a protection the loop is indifferent to by construction.

**Its failure modes produce healthy-looking artefacts.** This is the one that makes ordinary oversight
insufficient. Chapter 45's widened claims, Chapter 47's confident wrong verdicts, Chapter 48's rising
aggregate over a falling slice — every one produces correct, well-formed, plausible output. `[INF]`
Oversight designed to catch things looking wrong catches none of it, which is why §5.1 is a fixed list
of specific numbers rather than a judgment about whether things seem fine.

### 5.7 The campaign as a Run

`[FUT]` The closing proposal, deferred here by Chapter 3 §14 and attempted by neither source.

The evolution loop runs as a script over a fixed iteration count `[AHE Alg. 1]`. `[INF]` It is not
schedulable, not resumable, not interruptible, and not observable in the terms this book spent five
levels building — which is odd, because the runtime it edits has all four properties and the loop's
iterations last hours while a run's steps last seconds.

The proposal is to make an evolution campaign a **Run** inside the same runtime:

| The loop needs | The runtime already has | Chapter |
|---|---|---|
| Iterations that survive a crash | Episodes, checkpointed per step | 18, 21 |
| A budget that is reserved and settled | Reserve-then-settle | 35 |
| To park for a human decision | The gate as a durable park holding nothing | 30 |
| Interruption without loss | Steer as goal amendment forcing a replan | 30 |
| Its own progress made durable | Progress as novel durable state | 29 |
| Scheduling that does not starve production | Reserved-but-preemptible work class | 23, 41 |

`[FUT]` The three gates of §2.3 then stop being process and become **parks** — a campaign that reaches
a relaxation request parks, durably, holding nothing, until a named owner resumes it. `[INF]` That is
strictly better than a meeting, and every mechanism it needs was built for other reasons in Levels 1
through 3.

`[FUT]` The honest caveat: nobody has built this, the handbook has no measurement of it, and the
obvious risk is recursive — a runtime evolving a harness that is also the runtime's own harness needs
a containment argument this book does not make. It is proposed as the natural next architecture, not
as a finished one.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  One week, with the scan.

  day   step                          result
  ----  ----------------------------  ----------------------------
  Mon   scan computed automatically   one page, eleven numbers,
        before anyone arrives         out-of-band flags precomputed
  Mon   read, in fixed order          #1  worst slice -2.1 vs seed
                                          against a 6.0 floor: in
                                          band, and TRENDING
                                      #6  temporal parameters
                                          contested 14 times
                                      #8  trajectory reads: 61,000,
                                          all by the distiller,
                                          98.6% structural
                                      the other eight: in band
  Mon   routing, not deciding (3.1)   #1 -> watch; #6 -> Gate 2
  Wed   GATE 2 convenes on #6         the loop has found 14 times
                                      that the correct fix is a
                                      timeout it may not edit
        step 1: the refusals ARE the  displacement records, per
        evidence (C46 sec 5.7)        pattern
        step 2: what can the reward   latency, cost reserves,
        not see?                      convoy behaviour
        step 3: instrument, or route  DECISION: add p95 latency and
        to a human                    cost-per-success to the
                                      evaluation. Do NOT move the
                                      boundary yet.
        step 5: never as an           the loop is not stuck; it is
        emergency change              reporting
  Thu   the evaluation gains two
        terms; the seed is re-run
        against them
  ----  ----------------------------  ----------------------------
  +3wk  #6 recomputed                 contested 2 times. The
                                      displacement mostly stopped,
                                      because the loop can now show
                                      a timeout change scoring
                                      badly
  +6wk  GATE 2 reconvenes             relaxation approved, SCOPED
                                      to what the reward now
                                      represents (C46 sec 5.7
                                      step 4)

  FAILURE BRANCH -- the cold open's agenda:

    Mon   score up, iterations 12, cost flat, 6 edits shipped
          -- all four healthy, meeting ends in ten minutes
    x5mo  #1 reaches -9.1, #6 reaches 31, #8 has never been
          computed, three relaxations happen between meetings
    +6mo  a customer asks who read their source code
    -- and the review was never wrong about anything it looked
       at.

  Figure 49.4 -- A week, and the alternative (D4 Sequence)
```

### 6.1 The gate resolved a constraint without moving it

`[INF]` Wednesday's outcome is the shape worth extracting, because it is the one that does not occur
to people under pressure. The constraint was contested fourteen times, the loop was demonstrably
blocked, and the decision was to **change what is measured** rather than to move the boundary — which
is Chapter 46 §5.7 step 3, and which took three weeks to pay off and then resolved the contest almost
entirely.

The cold open's engineers made the other decision three times, individually, each in a commit. `[INF]`
Neither group was more careful. One had a procedure and a named owner, and the other had a constraint
that was in the way.

---

## 7. State Management

```
                                                            STATE VIEW

   THE AUTONOMY LADDER. C20 sec 14 deferred the question of when
   the two loops may stop being separated by a human decision.
   This is the answer: in stages, with stated conditions.

      {{ proposes_only }}          the default, and where the
          |                        source's prototype sits.
          |                        Every promotion is Gate 1.
          |
          |  PROMOTE when ALL hold:
          |    - per-slice cumulative gating live (C48 5.3)
          |    - the scan has run 12+ weeks with numbers in band
          |    - surprise-regression rate measured and stable
          |    - rollback exercised on a schedule, not trusted
          |    - trials confined to tier-1 effects (C47 5.6)
          v
      {{ auto_promote_scoped }}    promotes without a human, on
          |                        ONE surface, with a cap on
          |                        edits per week and an
          |                        automatic halt on any slice
          |                        breach
          |
          |  PROMOTE when: 6+ months at the previous level with
          |  no halt, AND an incident review of every halt that
          |  did occur
          v
      {{ auto_promote }}           broader, still surface by
                                   surface. Gates 2 and 3 remain
                                   human AT EVERY LEVEL -- they
                                   are never automated, because
                                   they are the decisions the
                                   reward cannot represent

      DEMOTE IMMEDIATELY, at any level, on:
        * any edit outside the write scope (scan #11)
        * any slice breach that reached users
        * any relaxation made outside Gate 2
        * a scan not run for two consecutive weeks

      ILLEGAL:

        * promoting on the aggregate score. It is not on the
          scan for exactly this reason (5.1).

        * automating Gate 2 or Gate 3 at any level. A loop that
          can widen its own boundary or its own data access has
          neither.

        * treating {{ auto_promote }} as terminal. A model
          change invalidates the fit (C42 sec 7.1) and the
          conditions are re-tested, because the numbers the
          promotion rested on were measured against a model
          that is no longer deployed.

  Figure 49.5 -- The autonomy ladder (D6 State Diagram)
```

### 7.1 The ladder's conditions are all measurements, not judgments

`[INF]` Every promotion condition in Figure 49.5 is something already computed by machinery built in
Chapters 39 through 48. That is deliberate: a ladder whose rungs are judgments about whether the team
feels ready is a ladder that gets climbed under commercial pressure and never descended.

`[BP]` The demotion triggers matter more than the promotions and should be automatic. `[INF]` A
demotion that requires a decision will be argued about at the moment it is most needed, and the
argument will be made by the people whose work it slows.

### 7.2 A model change resets the ladder's evidence

Chapter 42 §7.1 established that fit is a property of the *pair* — harness and deployed model — and
that the transition to `{{ invalidated }}` is derivable the moment a new model is deployed. `[INF]`
The same event invalidates the ladder's evidence, and for the same reason: the surprise-regression
rate, the slice deltas, and the stability record were all measured against a model that is no longer
running.

`[BP]` This is also the trigger Chapter 42 §7.1 said this chapter would hang the loop's schedule on. A
model deployment starts a campaign, and it re-opens the autonomy conditions — one event, two
consequences, and both are derived rather than remembered.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence


class ReviewScan(Protocol):
    """Computed before the meeting, in fixed order. A scan that
    requires someone to run queries live becomes a scan that
    happens when that person is available (5.1)."""

    def compute(self, week: str) -> "ScanReport":
        """Eleven numbers, each with the failure it catches named
        in the report itself.

        Deliberately EXCLUDES the aggregate score. It is monitored
        elsewhere, everyone looks at it anyway, and it is the
        number that can rise while number 1 falls (C48 sec 5.3).
        """

    def unused_entries(self, since: str) -> Sequence[str]:
        """Numbers that have never been out of band. Reviewed
        annually for removal -- agendas accrete exactly the way
        instruction files do (4.1)."""


class Gate(Protocol):
    """Three of them, and no more (2.3)."""

    def decide(self, request: "GateRequest", owner: str) -> "GateDecision":
        """Owner is named and, for Gate 2, outside the loop's
        reporting line. The person who wants a constraint moved is
        the person whose work it is blocking (5.2).
        """

    def refusal_rate(self, since: str) -> float:
        """A gate at zero over six months is theatre, and theatre
        consumes the attention the real gates need. C7 sec 14: an
        approval that is always granted is a gate that should be
        removed."""


class AccessAudit(Protocol):

    def reads(self, since: str, subject: str | None = None) -> Sequence["AccessRecord"]:
        """Who read which trajectory, INCLUDING machine readers.

        Reviewed, not alerted: volume makes alerting useless and
        the question is always asked retrospectively (5.3).

        The cold open's eleven days were spent reconstructing what
        this returns in a query.
        """


class AutonomyPolicy(Protocol):

    def level(self) -> "AutonomyLevel": ...

    def conditions_met(self, target: "AutonomyLevel") -> "ConditionReport":
        """Every condition is a MEASUREMENT, never a judgment
        about readiness (7.1)."""

    def demote_on(self, event: str) -> None:
        """Automatic. A demotion requiring a decision is argued
        about at the moment it is most needed, by the people whose
        work it slows (7.1)."""
```

`ReviewScan.compute` excluding the aggregate score is the most opinionated signature in this chapter.
`[INF]` It will read as an omission and be added back by the first person who notices, which is why
the docstring carries the reason rather than the convention.

`Gate.refusal_rate` existing at all is Chapter 7 §14's observation turned into an interface. `[BP]`
Gates are added easily and removed never; a method that makes their uselessness computable is the only
mechanism that has ever removed one.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class AutonomyLevel(StrEnum):
    PROPOSES_ONLY = "proposes_only"
    AUTO_PROMOTE_SCOPED = "auto_promote_scoped"
    AUTO_PROMOTE = "auto_promote"


@dataclass(frozen=True)
class ScanEntry:
    number: int                      # fixed order (5.1)
    name: str
    value: float
    in_band: bool
    catches: str                     # the failure, named in the
                                     # report. An entry that cannot
                                     # fill this does not belong
    source_chapter: str
    routes_to: str | None            # a gate, or None -- the scan
                                     # does not decide (3.1)


@dataclass(frozen=True)
class ScanReport:
    week: str
    entries: tuple[ScanEntry, ...]
    computed_at: str                 # BEFORE the meeting
    out_of_band: tuple[int, ...]


@dataclass(frozen=True)
class GateDecision:
    gate: str                        # promotion | relaxation | scope
    request_id: str
    owner: str                       # named; Gate 2's is outside
                                     # the loop's reporting line
    granted: bool
    rationale: str                   # recorded, because a later
                                     # reader cannot tell a
                                     # considered decision from an
                                     # expedient one (C46 sec 7)
    made_during_iteration: bool       # Gate 2: must be False
                                      # (C46 sec 5.7 step 5)


@dataclass(frozen=True)
class AccessRecord:
    reader: str                      # "distiller" is a reader
    trajectory_id: str
    tenant_id: str
    partition: str                   # structural | verbatim
    at: str
```

`AccessRecord.reader` naming a component rather than a person is the whole of §5.3 in one field.
`[INF]` Access logs are built to answer *which employee*, so an automated reader with a standing path
appears in them as nothing at all — and the cold open is what that absence costs when the question
finally arrives.

`GateDecision.made_during_iteration` exists to make one specific bad decision visible after the fact.
`[INF]` Chapter 46 §5.7's fifth step says never relax during an iteration, because the pressure arrives
when the loop is stuck and that is when the reasoning is worst. A boolean is the cheapest available
enforcement of a rule about timing.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Ledger (C45 §5.7) | Scan | Six queries | Precision with width, level distribution, verdict mix |
| Attribution (C47) | Scan | Per iteration | Abstention rate, surprise regressions |
| Containment policy (C46) | Scan | Standing | Contested counts, displacement records |
| Trace store (C16) | Access audit | Read log | Who read what, including machine readers |
| Benchmark + seed (C41, C43) | Gate 1 | Per promotion | Per-slice cumulative deltas against the seed |
| Gate 2 | Containment policy (C46) | Write | The only write path to the boundary |
| Gate 3 | Corpus policy (C37, C44) | Write | What the loop may learn from |
| Model deployment (C38) | Autonomy policy | Event | Fit invalidated; the ladder's evidence resets (§7.2) |
| Scan | Nobody | One page, weekly | Whether anything is out of band |

`[INF]` The sixth row is the structural claim underneath this whole chapter. Chapter 46 made the
containment policy readable by the loop and writable only by a human; this is that human, with a name
and a procedure. The boundary is not enforced by anyone's restraint — it is enforced by there being
exactly one write path, and this table is where it ends.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| The review watches the score | Nothing; the score is healthy | A fixed scan of eleven numbers, computed in advance (§5.1). The cold open |
| An agenda item nobody can justify | It has never been out of band | Annual removal review of the scan itself (§4.1) |
| Per-edit approval added | Its refusal rate is zero | Measure every gate's refusal rate; delete the ones at zero (§5.2) |
| Constraints relaxed between meetings | The commit, if anyone looks | Gate 2, a named owner outside the reporting line (§5.2) |
| Relaxation during an iteration | `made_during_iteration` | Never as an emergency change (§5.7 of Ch 46, §9 here) |
| Automated reader with inherited access | A customer's question, eleven days later | Read audit including machine readers; structural by default (§5.3) |
| Cleanup deferred indefinitely | Resident component count rising | Standing allocation, not a campaign (§4.2, §5.4) |
| The fallback capability decays | Nothing until the loop is turned off | Named as unsolved (§2.1, §13.3) |
| Autonomy promoted on judgment | It is never descended | Measured conditions, automatic demotion (§7.1) |
| Autonomy retained across a model change | The evidence was measured on a different model | The deployment event resets the conditions (§7.2) |
| Corpus or weighting chosen for what it shows | Nothing; every number is correct | Gate them, with a recorded rationale (§5.5) |

`[INF]` Row eight is the one this book cannot answer. Every other entry has a mechanism; this one has
a name and a warning. It is also the failure with the longest fuse — a team discovers it at the moment
the loop is turned off, which is the moment it can least afford to.

---

## 12. Scalability

**Governance is the one thing here that does not scale with the loop.** `[INF]` The scan is one page a
week whether the loop runs one iteration or twenty, because every number is an aggregate. That is the
property that makes the arrangement viable and it is a direct consequence of Chapter 45 §5.7 — the
ledger's queries are computations over every entry, so nothing is sampled away.

**The gates scale by rarity rather than by capacity.** `[BP]` Gate 1 fires per promotion, which is
weekly at most. Gates 2 and 3 fire a few times a year. `[INF]` If Gate 2 is firing monthly, the
containment list is in the wrong place and that is the finding, not a staffing problem.

**Multiple loops multiply the scan, not the gates.** `[INF]` Four product surfaces mean four scans and
one containment policy, because the boundary is a property of the organisation rather than of a
harness. A per-loop containment list is how eleven entries become forty-four inconsistent ones.

**And the thing that does not scale at all is understanding.** `[INF]` §2.1's second break: the harness
grows past what anyone has read, and no amount of process substitutes for somebody who could re-fit it
by hand. That is a scaling limit on the *organisation* rather than on the system, and it is the one
this chapter cannot mechanise.

---

## 13. Production Engineering

### 13.1 The five numbers

Eleven are on the scan (§5.1). Five belong to whoever owns the loop as a service:

- **Weeks since the scan last ran.** Two consecutive misses is an automatic demotion (§7).
- **Gate refusal rates.** A gate at zero is theatre (§5.2).
- **Time from a number going out of band to a gate convening.** The scan's value is entirely in what
  follows it.
- **Cleanup throughput** — removal experiments per week, and components removed. The only mechanism
  that shrinks the harness (§5.4).
- **Days since anyone re-fitted a harness by hand.** `[INF]` The proxy for §2.1's second break, and the
  only number here that measures the organisation rather than the system.

### 13.2 The review question

Every week, once: **which number on this page would have caught last quarter's surprise?**

`[INF]` If the answer is *none*, the scan needs an entry and the surprise supplies its definition. This
is how the list of eleven should grow, and it is the only way it should — an entry added because
somebody imagined a failure will never be out of band, and §4.1 will eventually remove it.

### 13.3 Teaching this to a new engineer

Show them the cold open's four numbers and ask whether the loop is healthy. Everyone says yes, because
it is the right answer to the question asked.

Then show them the four numbers that were not on the page.

`[INF]` The instinct that installs is the seventh in this level and the last in the book, and it is the
same one every time, aimed now at the review itself. *Worth what, against what baseline* (Chapter 42).
*What else could be doing this* (Chapter 43). *What would I have to see to know I am wrong* (Chapter
44). *What would have made this claim fail* (Chapter 45). *What is this number not measuring* (Chapter
46). *What else could have caused this* (Chapter 47). *Who is this average hiding* (Chapter 48). And
here: **what is not on the page?**

`[BP]` One more thing worth teaching, and the handbook has no mechanism for it. Have somebody re-fit
the harness by hand once a year — a real re-fit, on a real model change, with the loop switched off.
It is expensive, it produces a harness you will probably discard, and it is the only way the capability
in §2.1's second break stays alive. Aviation calls this recurrent training and requires it. Nobody
here requires anything.

---

## 14. Relation to the Base Runtime

**What the base runtime supplies, and it turns out to be the whole of governance.** `[DAR §8.2]`
Chapter 30's gate is a durable park holding nothing, and every gate in this chapter is that construct
at a different timescale. `[DAR §8.1]` Structural enforcement in the runner rather than in the prompt
is why Chapter 46's boundary holds and why this chapter can be about *deciding* rather than about
*preventing*. `[DAR]` The recorded triple, the decision log, and the read audit are three artefacts
built for recovery, authority, and compliance respectively, and all three are load-bearing here.

**What this chapter adds.** `[INF]` The scan as a fixed agenda rather than an inspection; the argument
that a review is its agenda; three gates and the observation that the fourth one everybody adds should
be deleted; access as a governance surface with the reader named as a component; and the autonomy
ladder, whose rungs are measurements so that it can be descended.

**What the loop owes the runtime, finally.** `[INF]` It runs on a benchmark, proposes rather than
deploys, writes inside one enumerated scope, and cannot move its own boundary or widen its own data
access. Every one of those is a property of the arrangement rather than a promise about behaviour, and
that distinction is the entire safety argument of Level 5.

**And what remains unfinished.** `[AHE Limitations]` The source's own list stands: one benchmark
family, a bounded iteration count, non-additive gains, weak regression prediction. `[INF]` This
handbook adds three of its own — containment is a lower bound with no completeness argument, indirect
boundary erosion is detected by nothing, and the human fallback decays exactly as the loop succeeds.
`[FUT]` And it leaves one proposal on the table: the campaign as a Run (§5.7), which nobody has built.

---

## 15. Industry Perspective

**`[AHE §3.3, Limitations]`** The controllability constraints this chapter gates, and the
controlled-prototype framing §5.5 is built on. `[AHE §4.4.2]` The regression-prediction figure that
Chapter 0 §14 said would be the reason a self-evolving system needs more governance, not less.

**`[DAR §8.1, §8.2]`** The gate as a durable park, structural enforcement in the runner, and the
decision log that makes Chapter 7 §14's always-granted approval measurable rather than anecdotal.

**`[INF]`** The handbook's own: the claim that a review is its agenda and the eleven-number scan that
follows from it; three gates rather than a process, and the argument for deleting per-edit approval;
access inheritance as the way automated readers acquire permissions; removal as scheduled work rather
than a campaign; the autonomy ladder with measured rungs and automatic demotion; and the observation
that the human fallback atrophies in proportion to the loop's success.

**`[BP]` The aviation scan is the transferable practice**, and it transfers more completely than most
analogies in this book. A fixed instrument scan in a fixed order, a checklist that is read rather than
recalled, and the recognition that the characteristic accident involves a competent crew watching the
wrong thing. Every one of those has a direct counterpart in §5.1.

**`[BP]` Separation of duties is the other one**, and it is old. Gate 2's owner sits outside the loop's
reporting line for the same reason a risk function sits outside a trading desk (Chapter 46 §2.1) and
an auditor outside a finance team: the person who wants the constraint moved is the person it is
blocking.

**`[FUT]` The sixth generation.** Chapter 0 deferred its taxonomy's next entry to this chapter, on the
grounds that speculation should be grounded in measured limits rather than in enthusiasm. `[FUT]` With
Level 5's limits in hand, the honest description of what comes after a self-evolving harness is not a
more autonomous loop — it is one that can **measure what it is about to break**. Every limit in Chapter
48 that cannot be designed around traces to the same root: the loop optimises a scalar it can see and
is indifferent to the properties it cannot. A generation that closes that gap would need an objective
that represents the protections, which is a different research problem from anything in this book and
is the one worth naming as next.

**`[FUT]` And the campaign as a Run** (§5.7), deferred here by Chapter 3 and attempted by neither
source.

---

## 16. Key Takeaways

1. **A review is its agenda.** The cold open's reviewers were competent, regular, and watching four
   healthy numbers while four unhealthy ones sat in the same database. Fix the list, not the
   attention.
2. **A fixed scan, computed before the meeting, in fixed order.** Eleven numbers, each with the failure
   it catches named beside it, and the aggregate score deliberately absent — it is the number that can
   rise while the one that matters falls.
3. **Three gates, and delete the fourth.** Promotion, relaxation, scope. Per-edit approval is the one
   everybody adds, it never refuses, and a gate that never refuses spends the attention the real ones
   need.
4. **Access is a governance surface.** An automated reader does not request permissions; it inherits a
   read path. Audit machine readers by name, read structurally by default, and the eleven-day question
   becomes a query.
5. **Removal is a first-class operation and the one most often left unimplemented.** It is the only
   mechanism in Level 5 that makes a harness smaller, and it must be scheduled, because work whose
   best outcome is that nothing happens always loses to work that produces a number.
6. **A self-evolving system needs more governance than a static one.** Its behaviour changes without
   anyone changing it, it is indifferent to every protection outside its reward, and its failures
   produce healthy-looking artefacts.
7. **Say what is demonstrated and what is not.** Harness quality is a large measurable surface and a
   loop can improve it unattended; gains do not compound, transfer is unmeasured, damage is
   unpredicted, and the containment list is a lower bound. Run it inside a boundary sized to the first
   sentence.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Review scan** | A fixed agenda of computed numbers, in fixed order, because a review is its agenda and attention drifts toward the interesting. | `[BP]` | — |
| **Relaxation gate** | The named human decision required to move a containment entry, made outside the loop's reporting line and never during an iteration. | `[INF]` | — |
| **Scope gate** | The decision to widen what the loop may learn from, which is a contract question rather than an engineering one. | `[INF]` | — |
| **Gate refusal rate** | The measure that makes a useless gate visible, since an approval that is always granted is a gate that should be removed. | `[BP]` | — |
| **Access inheritance** | An automated reader acquiring standing access to a sensitive store because a read path existed, without any grant. | `[INF]` | — |
| **Harness cleanup** | Scheduled removal of undetermined edits, rotted memory, and accreted instructions — the only mechanism that shrinks a harness. | `[AHE]` | — |
| **Autonomy ladder** | The staged levels at which the loop may act without a human, with measured promotion conditions and automatic demotion. | `[INF]` | — |
| **Fallback atrophy** | The decay of a team's ability to re-fit a harness by hand, caused by the loop's success and unmeasured by anything. | `[INF]` | — |
| **Evaluation capture** | Choosing a corpus, weighting, or attribution model for what it will show, which is a governance problem rather than a statistical one. | `[BP]` | — |

---

**Level 5 is complete**, and so is the book.

You can now build an agent runtime that survives a crash, distribute it across many workers, operate
it in production, promise something honest about it, and change it safely. And you can put a second
loop on top of it that reads its own traces, edits its own harness under constraint, records every
edit as a claim that can fail, judges those claims honestly enough to abstain, and runs under three
gates and a page of numbers.

The last thing worth saying is the thing Chapter 42 opened with. This is maintenance, not
accumulation. The model underneath will change again in a few months, most of what the loop earned
will stop applying, and the loop will earn it back. That is not a disappointment; it is the job, and
the argument for automating it was never that it produces something permanent — only that the
treadmill has a speed you do not set, and that the scarce thing it consumes is a person reading a
volume no person can read.

Build the instruments first. Measure the floor before you measure anything against it. Write the
prediction down before the result arrives. Keep the seed. And put somebody's name on the page.
