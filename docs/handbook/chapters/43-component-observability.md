```
  Level 5 · Chapter 43
  COMPONENT OBSERVABILITY
  Requires   C1 Anatomy of an Agent, C14 The Tool Execution Engine,
             C39 GitOps and CI/CD,
             C42 The Case for Harness Evolution
  Unlocks    C44 Experience Observability, C45 Decision Observability,
             C46 The Evolve Agent
  Diagrams   Full (9)
```

# Chapter 43 — Component Observability

---

## 1. Motivation

### 1.1 Cold open

Atlas's `repo_find` tool takes a glob. Its description calls the parameter a directory path. The
model passes `src/handlers`, gets an empty list back, and concludes the directory is empty. It shows
up in four benchmark tasks.

An engineer fixes the description: names the parameter a glob, adds a counter-example, adds a note
about what an empty result means. Gate 2 measures +0.2 points. Inside the floor.

They rewrite it more forcefully. +0.1.

On the third attempt someone opens a trajectory and reads what the model actually sent. It sent
`src/handlers`. The tool received `src/handlers/**`.

A middleware hook added eleven months earlier normalises a bare path into a glob before dispatch. The
description had been wrong and harmless the entire time. Every edit to it was correct, well-argued,
and measured exactly nothing, because the behaviour it described had already been overridden two
directories away by someone who has since left.

The real failure was somewhere else again. When a glob matches nothing, `repo_find` returns an empty
list with no message, and an empty list is indistinguishable from an empty directory. That is the
tool implementation, not its description.

Three weeks of edits at the wrong address. Not through carelessness — because two components quietly
owned the same behaviour, and nothing in the harness said so.

### 1.2 In plain language

If you want a machine to improve a system, the system has to be made of labelled parts. Otherwise
"improve it" has nowhere to land.

That sounds obvious and most teams believe they already have it, because their instruction files are
in version control. Version control gives you a diff. It does not tell you which part of the system
is responsible for a given behaviour, and that is the property that matters here.

The reason is measurement. Deciding whether a change helped means comparing before and after, and a
comparison only means something if exactly one thing changed. When two parts can both produce the
same behaviour, editing either one produces no measurable difference — the other part quietly
compensates — and the edit looks worthless when it was merely invisible. That is the cold open, and
it is what three weeks of correct work bought.

So this chapter is about three things: giving every part a fixed address, making sure each behaviour
has exactly one part responsible for it, and starting from a deliberately bare system rather than
your best one — because you cannot measure a gain against a starting point that already contains it.

### 1.3 Why this chapter exists

Chapter 1 introduced the seven component types as anatomy: what a harness is made of, and which parts
the model must obey versus which it may ignore. Chapter 39 put those parts in a git repository with a
pipeline around them.

Neither made them an **action space**.

An action space needs three things a git repository does not supply. Every component needs a *fixed
address*, so that a change can be named before it is made and reverted after. Each behaviour needs
*exactly one owning component*, so that a measured difference can be attributed to a change rather
than to whatever else was involved. And the starting point needs to be *unfitted*, so that gains
measured against it are real.

`[AHE §3.1]` supplies all three: seven orthogonal component types as files at fixed mount points,
loosely coupled, over a deliberately minimal seed. `[INF]` This chapter's contribution is to show
that the middle property — orthogonality — is not tidiness. It is the precondition for every
measurement Chapters 45 and 47 depend on, and the cold open is what its absence costs.

This is the first of the three pillars, and it is the one every team believes it already has.

### 1.4 What previous framings got wrong

**"We have this already — the harness is in git."** Chapter 39 built exactly that, and the cold
open's harness had all of it: version control, fixed paths, two gates, per-slice effects. It still
took three weeks, because none of that machinery knows that a middleware hook and a tool description
are both describing the same argument.

**"Orthogonality is code hygiene."** It is an attribution property. Non-orthogonal components produce
two specific measurement failures — a correct edit that measures zero, and an incorrect edit that
measures positive for a reason nobody recorded — and Chapter 47's verdicts are wrong in both cases.

**"Start from our best harness."** The most natural decision available and the one that quietly
ruins the experiment. A seed that already contains a fix cannot show that fix being earned, and a
seed built by people encodes their guesses about which component owns which failure — which is
precisely the thing the loop is supposed to discover (§5.6).

**"Seven types is a taxonomy; ours will differ."** The number is not sacred. The properties are:
separately editable, distinct enforcement strength, a fixed address, and one owner per behaviour. A
harness with five types satisfying those is fine; one with seven that do not is the cold open.

**"The registry is a config file."** It is the pillar. `[AHE §3.1]` An unregistered component is a
silent no-op — a file that exists, reads correctly, is reviewed, and does nothing — and that failure
produces no error at any point (Chapter 1 §13.1).

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A labelled electrical panel.

The panel is the reason an electrician can work on a house safely. Each breaker owns one circuit,
the label says which, and flipping one produces a known, bounded, reversible change. The
discipline is unglamorous and entirely about attribution: you can work on the kitchen because you
know the kitchen is behind one switch and nothing else is.

The failures are instructive too, and they are the cold open's shape. An **unlabelled** panel means
flipping breakers until the right light goes out — expensive, and you learn nothing durable. A
**shared circuit**, where two breakers feed the same run of wire, is worse: you cut one, the lights
stay on, and you conclude the breaker is dead when it is being backfed by the other. Electricians
have a name for that hazard and a rule against it, because it has killed people.

The instinct transfers exactly. Fixed addresses, one owner per behaviour, and a labelled map of both.

**Where it breaks**, in two ways, and both make the harness problem harder.

A circuit's wiring is physically discoverable. You can trace the cable, and the topology is static —
the same at 3am on a Tuesday as at noon. Component overlap is *behavioural and conditional*.
Middleware compensates for some inputs and not others; a skill loads only when the model judges it
relevant; long-term memory applies only when recalled. `[INF]` There is no cable to trace, so overlap
cannot be read off the workspace. It can only be found by running the system and watching what
changes when something is removed, which is §5.3.

And flipping a breaker gives an instant, certain answer. Removing a component gives a distribution
measured over hours against a noise floor (Chapter 41). `[INF]` So the diagnostic that makes the
analogy work is available here, and it costs a benchmark run each time — which is why the structural
discipline matters so much more here than in a house. Prevention is cheap; diagnosis is not.

### 2.2 Why component observability must exist

```
  (1) An evolution loop must edit SOMETHING. "Improve the harness"
      has no action space unless the harness has parts.

  (2) Parts are not enough. A manifest entry (C45) names what it
      changed BEFORE the result is known, so each part needs a
      fixed ADDRESS that is stable across iterations.

  (3) Addresses are not enough. A verdict (C47) is a difference
      measurement, and a difference measurement means nothing
      unless exactly one thing changed.

  (4) So the parts must be ORTHOGONAL: one behaviour, one owning
      component. Not for tidiness -- because two components that
      can both produce a behaviour make an edit to either one
      unmeasurable. The cold open.

  (5) Orthogonality is not free and does not hold by default. Two
      components can grow into the same behaviour over months,
      each edit locally reasonable, neither declaring it. So
      something must DETECT overlap rather than assume it away.

  (6) The parts must also differ in ENFORCEMENT STRENGTH, or
      "fix at the weakest level that enforces" (C1 sec 5.2) has
      no levels to choose between and the loop cannot record why
      it chose one.

  (7) And the starting point must be UNFITTED. Gains are measured
      against a baseline; a baseline that already contains the
      fix cannot show it being earned, and a baseline built by
      people encodes their guess about which component owns what.

  (8) Seven orthogonal types, at fixed mount points, ranked by
      enforcement, over a deliberately minimal seed. Every clause
      in that sentence is load-bearing, and (4) is the one teams
      assume rather than check.
```

Step (5) is the one that has no analogue in ordinary software design. `[INF]` Most modularity
disciplines are about change cost — keeping edits local. This one is about *measurement validity*,
and the two come apart: a harness can be perfectly pleasant to edit and completely unmeasurable,
which is the cold open's harness exactly.

### 2.3 The four properties

Component observability is one word for four requirements, and a workspace can satisfy any three and
still be useless for Level 5.

| Property | Means | Violated when | Costs you |
|---|---|---|---|
| **Addressable** | Every component is at a fixed mount point | Behaviour lives in application code, or in a file nothing loads | A change cannot be named, recorded, or reverted |
| **Orthogonal** | One behaviour, one owning component | Two components can produce the same behaviour | Attribution — the edit measures zero, or measures for the wrong reason |
| **Ranked** | Each type has a known enforcement strength | All behaviour is instruction text | The constraint-level choice has no levels (Ch 1 §5.2) |
| **Unfitted at the start** | The seed contains as little as possible | The seed is your production harness | Every later measurement, permanently (§5.6) |

`[INF]` Read the last column. Only the first row's failure is visible — someone tries to edit
something and cannot find it. The other three fail silently and produce numbers that look exactly
like results, which is Level 4's recurring shape (Chapter 41 §11) arriving at the harness grain.

### 2.4 The mental model to carry

> **A component is an address with exactly one owner.** If two components can produce the same
> behaviour, neither one can be measured — and the harness will not tell you which pairs those are.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   THE HARNESS WORKSPACE AS AN ADDRESS SPACE        [AHE 3.1]
   one git repository (C39); seven types; fixed mount points

   +--------------------------------------------------------------+
   |  workspace/                                                  |
   |                                                              |
   |  ENFORCING -- code; the model has no choice                  |
   |    tools/**/*.py                  tool implementation        |
   |    middleware/**/*.py             middleware                 |
   |    sub_agents/<name>/agent.yaml   sub-agent configuration    |
   |                                                              |
   |  SHAPING -- text; the model may or may not comply            |
   |    tool_descriptions/*.tool.yaml  tool description           |
   |    LongTermMEMORY.md              long-term memory           |
   |    skills/<name>/SKILL.md         skill                      |
   |    systemprompt.md                system prompt              |
   +--------------------------+-----------------------------------+
                              |
      +-----------------------+------------------------+
      | (1) read at assembly  | (2) executed           | (3) enumerated
      v                       v                        v
   +-------------+     +----------------+     +--------------------+
   | context     |     | tool engine    |     | COMPONENT REGISTRY |
   | system      |     | (C14) and the  |     |  what exists,      |
   | (C11)       |     | middleware     |     |  where, at which   |
   |             |     | pipeline       |     |  level, how large  |
   +-------------+     +----------------+     +---------+----------+
                                                        | (4)
                                                        v
                                              +--------------------+
                                              | THE ACTION SPACE   |
                                              |  C45's manifest    |
                                              |  names a path from |
                                              |  this list, and    |
                                              |  nothing else      |
                                              +--------------------+

   OUTSIDE the workspace, and not addressable at all:
     the model and its effort tier        the verifier
     the kernel loop (C18)                redaction rules
     the effect tag (C14)                 -- the full list is C46's

  Figure 43.1 -- Seven types, seven addresses, one registry
                 (D1 High-Level Architecture)

  (1) shaping components enter the context; C11 assembles them
  (2) enforcing components run as code, with no model consent
  (3) the registry IS the pillar -- an enumerable list of what may
      be edited
  (4) an edit with no address cannot be recorded, predicted, or
      reverted, which is C45 and C47 both failing at once
```

### 3.1 The split that matters is enforcement, not file type

Figure 43.1 groups the seven types by whether the model can decline. `[AHE §4.4.1]` That grouping is
not stylistic: it predicts the measured results. The three enforcing types carried gains in the
ablation; the purely instructional one scored 2.3 points *below* the seed it was added to.

`[INF]` The practical reading for this chapter is narrower than Chapter 1's. A workspace whose seven
directories all contain text has seven addresses and one enforcement level, which means the
constraint-level field in Chapter 45's manifest degenerates to a constant and Chapter 46's central
decision has nothing to decide.

### 3.2 What is deliberately unaddressable

The bottom block of Figure 43.1 is the containment boundary, and Chapter 46 owns the full list and
the argument for each entry. It appears here because of a structural point that belongs to this
chapter: **you cannot forbid edits to a region you have not drawn.**

`[INF]` Component observability is what makes the boundary statable. Before the workspace has fixed
mount points, "the loop may not edit the verifier" is a policy nobody can enforce, because there is
no enumerable list of what it *may* edit to check the verifier's absence from.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                     COMPONENT REGISTRY                         |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Mount point resolver   |  |    Schema validator       |   |
   |  |                          |  |                           |   |
   |  |  path -> type, and       |  |  every file under a mount |   |
   |  |  therefore -> level      |  |  point parses and         |   |
   |  |                          |  |  registers, or gate 1     |   |
   |  |  a file NOT under a      |  |  fails (C39)              |   |
   |  |  mount point is not a    |  |                           |   |
   |  |  component. It is a      |  |  deterministic, minutes,  |   |
   |  |  silent no-op (4.1)      |  |  every commit             |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Inventory              |  |    Overlap detector       |   |
   |  |                          |  |                           |   |
   |  |  per type: what exists,  |  |  DECLARED overlap:        |   |
   |  |  its size, its age, the  |  |   two components claiming |   |
   |  |  iteration that added it |  |   the same behaviour tag  |   |
   |  |                          |  |   -- free, structural     |   |
   |  |  the FIRST thing the     |  |                           |   |
   |  |  Evolve Agent reads,     |  |  MEASURED overlap:        |   |
   |  |  and the only complete   |  |   disablement probes      |   |
   |  |  picture of the action   |  |   -- one benchmark run    |   |
   |  |  space (C46)             |  |   each (5.3)              |   |
   |  +--------------------------+  +---------------------------+   |
   +----------------------------------------------------------------+

  Figure 43.2 -- Inside the registry (D2 Low-Level Architecture)
```

### 4.1 An unregistered file is a silent no-op

The failure with no error, and it is the most common way a workspace stops being an address space.

A `SKILL.md` in a directory the loader does not scan. A middleware module never added to the
pipeline. A tool description for a tool that was renamed. Each file exists, reads correctly, passes
review, is diffed and committed — and has no effect on anything.

`[BP]` Registration must be verified mechanically and must fail the build, not warn. Chapter 39's
gate 1 is the right home: it is deterministic, it runs in minutes on every commit, and it is already
validating schemas. The check is small — every file under a mount point resolves to a registered
component, and every registered component resolves to a file — and it catches a class of failure
that otherwise surfaces as a harness edit that mysteriously does nothing.

`[INF]` It also matters more under automation than under people. An engineer whose edit does nothing
eventually investigates. A loop whose edit does nothing records a manifest entry, measures no effect,
assigns `rollback_and_pivot`, and moves on to a different root cause — having learned something false
about the system.

### 4.2 The inventory is what the loop reads first

Chapter 46's agent begins each iteration by reading what exists. `[INF]` Not the file contents —
those are far too large — but the shape of the action space: which types are populated, how many of
each, how large, and how recently each was touched.

That listing does real work beyond navigation. Three signals fall out of it directly:

- **An empty type is a hint.** No middleware at all, after six iterations, usually means cross-step
  patterns are being fixed in the system prompt instead, which is the wrong level (§5.4).
- **A growing system prompt is a warning.** Chapter 39 §5.6's accretion, visible as a number rather
  than as a feeling.
- **A component nothing has touched in twenty iterations is a removal candidate**, which is Chapter
  39 §5.6's removal experiment applied to a component rather than to a sentence.

```
                                                            LAYER VIEW

   NAMED INTERNALS AND THEIR INTERFACES

   +-------------------+      resolve(path)      +------------------+
   |  Mount point      |<------------------------|  Registry        |
   |  resolver         |------------------------>|  facade          |
   |                   |   Component | None      |                  |
   |  MOUNTS: a table, |                         |  the only way    |
   |  not a convention |                         |  anything asks   |
   +-------------------+                         |  "what exists?"  |
                                                 +---+----------+---+
   +-------------------+      validate(ws)           |          |
   |  Schema validator |<----------------------------+          |
   |                   |---------------------------->|          |
   |  gate 1 (C39)     |   ValidationReport                     |
   +-------------------+                                        |
                                                                |
   +-------------------+      list(kind=None)                   |
   |  Inventory        |<---------------------------------------+
   |                   |--------------------------------------->|
   |  per type, with   |   tuple[Component, ...]                |
   |  size and age     |                                        |
   +-------------------+                                        |
                                                                |
   +-------------------+      declared() / probe(component)     |
   |  Overlap detector |<---------------------------------------+
   |                   |--------------------------------------->
   |  declared: free   |   tuple[OverlapFinding, ...]
   |  measured: costs  |
   |  a benchmark run  |   consumed by: C45 (before an edit),
   +-------------------+                 C47 (explaining a zero)

   NOT an interface here: anything that WRITES. The registry is
   read-only by design; writes go through the git workspace (C39)
   so that every change is a reviewable, revertible commit.

  Figure 43.3 -- Registry internals (D3 Component Diagram)
```

---

## 5. Orthogonality, Ownership, and the Seed

### 5.1 Orthogonality is an attribution property

`[AHE §3.1]` The source states the requirement as loose coupling: adding middleware does not require
editing the system prompt, and adding a skill does not require touching a tool.

`[INF]` That phrasing understates what is at stake, because it sounds like a statement about edit
convenience. The load-bearing version is about measurement:

> Attribution is a difference measurement. A difference measurement is meaningful only when exactly
> one thing changed. Two components that can produce the same behaviour mean that changing one of
> them does not change the behaviour — so the difference is zero and the conclusion is wrong.

The cold open is the pure case. Three correct edits, three honest measurements, three true numbers,
and a conclusion — "the description does not matter" — that is false about the system and would have
been recorded in a manifest as a rejected hypothesis.

### 5.2 Three shapes of overlap, and how each measures

Overlap is not one failure. It has three shapes with different signatures, and telling them apart is
what makes the diagnosis tractable.

| Shape | What it is | An edit to the weaker one measures | Found by |
|---|---|---|---|
| **Compensation** | A stronger component silently corrects the weaker one's defect | Zero. The defect never reaches the model | Disablement probe on the *stronger* one |
| **Shadowing** | A stronger component pre-empts the weaker entirely, correct or not | Zero, always | Reading the pipeline order |
| **Duplication** | Two components independently encode the same rule | Half an effect, unstably — sometimes one fires, sometimes both | Divergence between two probes that should agree |

`[INF]` Compensation is the cold open and the most expensive of the three, because the system is
*working*. Nothing is broken, no error appears, the benchmark score is fine, and the only symptom is
that a whole component has quietly stopped mattering. A team can carry a compensating pair for years
without cost — right up to the moment someone tries to measure one of them.

Duplication is the one that damages the loop rather than the humans. `[INF]` An edit to a duplicated
rule measures a partial, unstable effect, which reads exactly like a marginal improvement near the
noise floor — and a loop that keeps marginal improvements accumulates a harness in which the same
rule is now encoded three times.

### 5.3 Detecting overlap costs a benchmark run, so declare what you can

Two detectors, and the cheap one should carry as much of the load as possible.

**Declared overlap is free.** Each component declares the behaviours it owns as tags —
`glob_normalisation`, `empty_result_semantics`, `retry_on_timeout`. Two components claiming a tag is
a build-time error. `[BP]` This catches nothing that is unknown, which is the point: it makes the
known ownership explicit and permanent, so the eleven-month-old middleware hook in the cold open
would have collided with the description's tag on the day someone tried to edit it.

**Measured overlap costs a run.** Remove a component, run the benchmark, and look at what moves. This
is the **disablement probe**, and it is the same mechanism as Chapter 39 §5.6's removal experiment at
component granularity — and the same mechanism as Chapter 42's counterfactual run, at a different
grain again. `[BP]` The signature to look for is a component whose removal changes nothing: either it
is dead, or something else is doing its job.

`[INF]` The probe is what Level 5 can afford and a human team cannot. Seven types over a workspace of
thirty components is thirty benchmark runs — weeks of a person's attention and a real bill, for a
result with no artefact anyone requested. It is a few hours of unattended compute for a loop that is
already running benchmarks continuously, and it is one of the clearest cases in this book of
automation doing something valuable that nobody was ever going to do.

```
                                                             TIME VIEW

  A failure pattern arrives from the evidence corpus (C44).
  Which component class owns it?

     failure pattern
          |
          v
       /       \   no     the environment or the task is at fault.
      / did the \-------> NOT a harness edit; C31 owns this, and
      \ model   /         proposing one here is how a loop learns
       \ get   /          something false
        \what /
         \it /
          \ /  yes
           v
       /       \   yes    +--------------------------------------+
      / is the  \-------->| TOOL IMPLEMENTATION                  |
      \ RESULT  /         | wrong, empty, or unreadable output;  |
       \wrong? /          | error text that does not instruct    |
        \     /           | (C15). The cold open's real answer.  |
         \   /            +--------------------------------------+
          | no
          v
       /       \   yes    +--------------------------------------+
      / wrong   \-------->| TOOL DESCRIPTION                     |
      \ verb or /         | read at the moment of choice; the    |
       \ args? /          | highest-yield surface (C15)          |
        \     /           +--------------------------------------+
          | no
          v
       /        \  yes    +--------------------------------------+
      / only     \------->| MIDDLEWARE                           |
      \ visible  /        | the ONLY type with a cross-step view |
       \ ACROSS /         | -- same error four times, budget     |
        \steps?/          | drift, repeated dead ends            |
          | no            +--------------------------------------+
          v
       /        \  yes    +--------------------------------------+
      / a long   \------->| SKILL                                |
      \ procedure/        | packaged, loaded on demand           |
       \ done   /         +--------------------------------------+
        \badly?/
          | no
          v
       /        \  yes    +--------------------------------------+
      / a hard-  \------->| LONG-TERM MEMORY                     |
      \ won FACT /        | specific and factual, never general  |
       \       /          | advice (C12)                         |
        \     /           +--------------------------------------+
          | no
          v
       /        \  yes    +--------------------------------------+
      / parent's \------->| SUB-AGENT CONFIGURATION              |
      \ context  /        | isolation, at the cost of            |
       \floods?/          | attribution (C19)                    |
        \     /           +--------------------------------------+
          | no
          v
  +----------------------------------------------------------------+
  |  SYSTEM PROMPT -- the DEFAULT OWNER, and the weakest.          |
  |  Measured 2.3 points BELOW the seed on its own [AHE 4.4.1].    |
  |  Arriving here TWICE for the same pattern means the routing    |
  |  was wrong, not that the wording was (5.4).                    |
  +----------------------------------------------------------------+

  Figure 43.4 -- Which component owns this failure (D8 Control Flow)
```

### 5.4 The unowned failure lands on the weakest component

Figure 43.4's last box is a design flaw that every harness has, and naming it is most of the fix.

`[INF]` The routing chain is a sequence of "is it this?" questions, and anything that answers no to
all of them still needs somewhere to go. It goes to the system prompt, because the system prompt is
the one component that accepts any content. That makes it the default owner by construction, and the
default owner is the component the ablation measured *below doing nothing at all*.

The result is a specific, predictable decay. Every failure the routing could not classify becomes a
sentence. The sentences accumulate (Chapter 39 §5.6), each one individually justified, and the
component that grows fastest is the one with the least enforcement and the highest per-call cost.

`[BP]` Two practices, and the second is the one with teeth:

- **Record the routing decision, not only the edit.** Chapter 45's manifest has a `constraint_level`
  field for exactly this, and the useful audit is over the *distribution* of that field rather than
  over any single entry.
- **Treat a second system-prompt edit for the same failure pattern as a routing failure.** Chapter 1
  §5.2 named the anti-pattern; this is the mechanical form of it. The third edit is never the answer,
  and the loop is measurably prone to it because instruction text is the cheapest thing to write.

### 5.5 The seed is deliberately minimal

```
                                                            LAYER VIEW

   THE SEED, AND WHAT TEN ITERATIONS MADE OF IT   [AHE 4.2, 4.4.1]

   type                  seed        after ten iterations
   -------------------   ---------   ------------------------------
   tool implementation   one bash    ====> ~1,364 lines; surfaces
                         tool              contract hints from files
                                           near each command
   middleware            none        ====> cross-step hooks
   long-term memory      empty       ====> 12 boundary-case lessons
   system prompt         minimal     ====> 79 lines of discipline
   tool description      one         ====> per-tool, with examples
   skill                 none        ====> packaged procedures
   sub-agent config      none        ====> delegated contexts

   MEASURED ALONE against the 69.7% seed, 89 tasks   [AHE 4.4.1]

     + long-term memory only      75.3     12 specific facts
     + tool only                  73.0     ~1,364 lines
     + middleware only            71.9
     + system prompt only         67.4     BELOW the seed
     full evolved harness         77.0

   READ THE LAST TWO COLUMNS TOGETHER
     the LARGEST artefact by line count is not the largest gain
     the SMALLEST -- twelve specific facts -- is
     the one that is pure instruction scored below doing nothing

   AND NOTE WHAT THE SEED IS NOT
     it is not a recommended production harness (5.7)
     it is an INSTRUMENT: the fixed point every later measurement
     in Levels 5 is taken against

  Figure 43.5 -- Seed, evolved harness, and what each was worth
                 (D7 Data Flow)
```

`[AHE §3.1]` The seed was one shell tool and nothing else. `[INF]` The instinct to improve on that is
strong and completely wrong, and it is worth being precise about why, because "start minimal" as
advice is easy to agree with and easy to abandon under a deadline.

### 5.6 Why a pre-fitted seed destroys attribution

Three separate mechanisms, and only the first is obvious.

**A gain already present cannot be earned.** If the seed contains the fix, the loop's edit that would
have introduced it measures zero, and the fix is attributed to nobody. Every measurement in
Chapter 42 §2.3's standing-advantage column is taken against the seed, so a fitted seed does not
merely lose one data point — it moves the origin of the whole coordinate system.

**A fitted seed encodes a human's ownership guesses.** This is the subtle one. A production harness
already places each behaviour in a component, and those placements were decided by people under
deadline pressure. `[INF]` Seeding with it hands the loop a routing table it did not derive and
cannot question, and the loop will spend its iterations refining placements rather than discovering
them. Whatever it finds is then a fact about your team's habits rather than about the problem.

**A fitted seed hides overlap it already contains.** The cold open's compensating middleware would be
in the seed, so the description's irrelevance would be a property of the baseline rather than a
finding — invisible, permanent, and inherited by every measurement taken afterwards.

`[INF]` Together these say something stronger than "start minimal". The seed is not a starting
position in a search; it is the **origin of the measurement space**, and the properties you want from
an origin are that it is simple, that it is documented, and that nobody optimised it.

### 5.7 The seed is an instrument, not a recommendation

A distinction the source does not need to make and a production reader does.

`[INF]` A bash-only harness scoring 69.7% is a fine experimental baseline and a poor product. Nobody
should ship it, and the honest framing is that the seed and the deployed harness are two different
artefacts with two different jobs: the seed exists to make measurement possible, and the deployed
harness exists to do the work.

`[BP]` The practical arrangement is to keep the seed in the workspace permanently, as a tagged
version rather than as history, and to re-run it against the current model on a schedule — which is
Chapter 42 §8's `standing_advantage` and the reason its `seed` parameter exists. A seed that has
drifted, been quietly improved, or stopped resolving against the current tool schemas is a broken
instrument, and it breaks silently.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  The cold open, replayed against a registry that has the four
  properties of 2.3.

  t     step                          result
  ----  ----------------------------  ----------------------------
  0     failure pattern from the
        corpus (C44): "model treats
        empty result as empty
        directory", 4 tasks
  1     routing (5.3): result itself
        is wrong -> TOOL
        IMPLEMENTATION, not its
        description
  2     registry.declared() on the
        glob_normalisation tag        TWO owners:
                                        middleware/paths.py
                                        tool_descriptions/
                                          repo_find.tool.yaml
                                      -> flagged before any edit
  3     the overlap is resolved
        first: the description is
        corrected to DESCRIBE what
        middleware actually does,
        and the tag is assigned to
        middleware alone
  4     the real edit lands on the
        implementation: an empty
        match returns a message
        distinguishing "no matches"
        from "empty directory"
  5     manifest entry (C45) written
        BEFORE the result:
          component  tool_impl
          path       tools/repo_find.py
          predicted  4 task ids
          at_risk    1 task id
  6     gate 1, then gate 2 (C39)     +3.1 pp on the affected
                                      slice, outside its floor
  7     verdict KEEP (C47), and the
        overlap finding is recorded
        against the workspace, not
        the edit

  ELAPSED: one iteration. The cold open took three weeks and
  ended with the wrong conclusion recorded.

  FAILURE BRANCH -- no declared tags, so step 2 finds nothing:

    t=2   no overlap detected; the routing at t=1 is still
          correct, so the implementation edit still lands
    t=6   +3.1 pp, KEEP
    -- the edit works. What is LOST is the finding: the
       description is still wrong, still harmless, and still
       waiting for the next person who tries to fix something
       through it. Overlap detection does not fix edits; it
       stops the SECOND kind of failure, which is a correct
       hypothesis rejected on a true measurement.

  FAILURE BRANCH -- no registry at all, which is the cold open:

    t=1   routing is a guess, because nothing enumerates the
          types or says which owns what
    t=2   the description is edited, because it is the file whose
          text is visibly wrong
    t=6   +0.2 pp, inside the floor
    t=..  repeat twice more, each time more forcefully
    -- three true measurements, one false conclusion, and the
       real defect untouched two files away.

  Figure 43.6 -- One failure, routed and attributed (D4 Sequence)
```

### 6.1 The second failure branch is the one to sit with

The middle branch produces a good outcome — the right edit, a real gain, a correct verdict — and
still loses something the loop needed.

`[INF]` A harness accumulates dead surfaces: components that once mattered and now do not, kept alive
because nothing measures them. Every one is a trap for a future edit, and the cost is paid by whoever
next forms a correct hypothesis about it. The loop pays that cost at machine speed, which means a
harness with three compensating pairs will burn iterations on all three, repeatedly, and record three
false findings about which components matter.

```
                                                             TIME VIEW

  Component selection, once per proposed edit.

        +--------------------------------------------------+
        |                                                  |
        v                                                  |
   +----+-------------------+                              |
   | a failure pattern      |  from the corpus (C44)       |
   +----+-------------------+                              |
        |                                                  |
        v                                                  |
      /   \  no owner in the chain                          |
     /route\ ---------------------------> E1 default owner  |
     \ 5.3 /                                  (system       |
      \   /                                    prompt)      |
        | one class                                         |
        v                                                   |
      /   \  yes                                            |
     /over- \ -------------------------> E2 resolve the     |
     \ lap? /                               overlap FIRST;  |
      \   /                                 no edit this    |
        | no                                round           |
        v                                                   |
   +----+-------------------+                               |
   | choose the WEAKEST     |  C1 sec 5.2                   |
   | level that enforces    |                               |
   +----+-------------------+                               |
        |                                                   |
        v                                                   |
      /   \  yes                                            |
     /same  \ ------------------------> E3 routing failure;  |
     \level /                              escalate a level, |
      \3rd /                               do not reword     |
       \time?                                                |
        | no                                                 |
        v                                                    |
   +----+-------------------+                                |
   | edit + manifest (C45)  |                                |
   +----+-------------------+                                |
        |                                                    |
        +----------------------------------------------------+

  Exits:
    E1  no class owns it -- the failure becomes a sentence, and
        the distribution of E1 exits is a health metric (13.1)
    E2  two owners; resolving ownership is itself the edit
    E3  the same level three times for one pattern is the named
        anti-pattern (C1 sec 5.2), and the loop is prone to it

  Figure 43.7 -- The component-selection cycle (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

   A COMPONENT'S LIFECYCLE in the workspace

      {{ absent }}
          |  an iteration adds a file at a mount point
          v
      {{ registered }}  the resolver finds it; gate 1 passes
          |
          |  -- and NOT registering is its own state:
          |     {{ orphaned }}  a file at no mount point, or a
          |                     mount point with no loader.
          |                     Reads fine. Does nothing. No
          |                     error, ever (4.1)
          v
      {{ live }} <-----------------------+
          |    ^                         |
          |    |  edited                 | overlap resolved:
          |    +---------+               | one owner keeps the tag
          |              |               |
          | probe shows  |               |
          | no effect    |               |
          v              |               |
      {{ suspect }}------+          {{ overlapping }}
          |   removal changes nothing         ^
          |                                   | two components
          v                                   | claim one tag
      {{ retired }}                           |
        kept in git; revertible (C39)  -------+

      ILLEGAL, and each has happened:

        * {{ orphaned }} treated as {{ live }}. Every edit to it
          measures zero and the conclusion drawn is about the
          component rather than about the loader.

        * deleting a SEED component. The seed is the origin of
          the measurement space (5.6); the non-deletable rule is
          C46's and this is why it exists.

        * {{ overlapping }} -> {{ live }} by editing both. The
          resolution is to REMOVE an owner, not to make the two
          agree -- two components that agree today are a
          duplication pair tomorrow (5.2).

  Figure 43.8 -- Component states (D6 State Diagram)
```

### 7.1 `{{ orphaned }}` is the state with no signal

Every other transition in Figure 43.8 is observable. This one is the exception and it is the reason
§4.1 insists the check blocks the build.

`[INF]` The orphan is worse than a missing component, because a missing component is a gap somebody
notices. An orphan is a file that reviews well, diffs cleanly, appears in the inventory listing if
the listing walks the filesystem rather than the loader, and produces measurements that are all
correct and all about the wrong thing.

`[BP]` Build the inventory from the **loader**, not from the filesystem, and reconcile the two. The
difference between those lists is exactly the orphan set, and it is a one-line report that most
workspaces have never run.

### 7.2 Retired is not deleted, and the seed is neither

Chapter 39 §7.2's rule applies unchanged: a retired component stays in git and stays revertible, and
the revert should be exercised on a schedule rather than trusted.

The seed is a third thing and needs saying separately. `[INF]` It is not live, not retired, and not
editable — it is a tagged version that exists to be re-run. Chapter 46's controllability constraints
make it non-deletable for that reason, and the constraint is unusual: most of that list protects
against an outcome-based reward removing a *protection*, while this one protects against it removing
a *measurement*.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence


class ComponentRegistry(Protocol):
    """The only way anything asks what the harness is made of.
    Read-only: writes go through the git workspace (C39) so every
    change is a reviewable, revertible commit."""

    def resolve(self, path: str) -> "Component | None":
        """None means the path is not under any mount point, and
        therefore is not a component at all.

        A caller that treats None as "a component I could not
        classify" reintroduces the orphan (7.1). None means the
        file does nothing.
        """

    def inventory(self, kind: "ConstraintLevel | None" = None) -> Sequence["Component"]:
        """What exists, per type, with size and age.

        Built from the LOADER, not from the filesystem. The
        difference between those two lists is the orphan set, and
        it is the report nobody runs (7.1).
        """

    def validate(self) -> "ValidationReport":
        """Gate 1 (C39): every file under a mount point registers,
        and every registered component resolves to a file.

        Fails the build. A warning here is read once and then
        filtered, and the failure it describes has no other symptom.
        """


class OverlapDetector(Protocol):

    def declared(self) -> Sequence["OverlapFinding"]:
        """Two components claiming the same behaviour tag. Free,
        structural, and build-time.

        Catches only KNOWN ownership, which is the point: it makes
        what people already know permanent, so an eleven-month-old
        hook cannot be forgotten (5.3).
        """

    async def probe(self, component_id: str, corpus_version: str, k: int) -> "ProbeResult":
        """Disablement probe: remove the component, re-run, measure.

        Costs one benchmark run. A component whose removal changes
        nothing outside the noise floor is either dead or being
        compensated for, and the two are distinguished by probing
        the suspected compensator as well.

        Raises when the floor is stale (C41 sec 8).
        """


class SeedPolicy(Protocol):

    def seed_version(self) -> str:
        """The tagged origin of the measurement space (5.6). Not a
        branch, not history -- a fixed reference that C42's
        standing_advantage measures against."""

    def is_protected(self, path: str) -> bool:
        """Seed components are non-deletable (C46). Unusual among
        the controllability constraints: this one protects a
        measurement rather than a safety property (7.2)."""
```

`ComponentRegistry.resolve` returning `None` rather than an "unknown component" object is the
signature carrying §7.1. `[INF]` An unknown-component type would let a caller keep going, which is
the exact behaviour that makes an orphan survive review.

`OverlapDetector.probe` being async and taking a corpus version is the honest interface. It is not a
lookup — it is a benchmark run, and a signature that hid that would be used casually in a loop that
cannot afford it.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Component:
    """One editable thing, at one address, at one enforcement level."""
    component_id: str
    kind: "ConstraintLevel"        # C20 sec 9; the level IS the type
    path: str                      # the mount point; C45 records this
    owns_tags: tuple[str, ...]     # behaviours claimed; two claims
                                   # of one tag is a build error (5.3)
    size_bytes: int
    added_in_iteration: int | None  # None means it came from the seed
    is_seed: bool                   # non-deletable (C46)


@dataclass(frozen=True)
class OverlapFinding:
    tag: str
    components: tuple[str, ...]     # two or more claimants
    shape: str                      # compensation | shadowing |
                                    # duplication (5.2)
    detected_by: str                # "declared" or "probe"


@dataclass(frozen=True)
class ProbeResult:
    """What a component is worth, measured by removing it."""
    component_id: str
    delta_pp: float                 # WITHOUT it, minus with it
    floor_pp: float                 # C41; travels with the delta
    corpus_version: str
    k: int

    @property
    def matters(self) -> bool:
        """Inside the floor means dead OR compensated -- and the
        two are not distinguishable from this result alone."""
        return abs(self.delta_pp) > self.floor_pp


@dataclass(frozen=True)
class ValidationReport:
    orphaned_paths: tuple[str, ...]      # files at no mount point
    unresolved_registrations: tuple[str, ...]   # loaded, no file
    duplicate_tags: tuple[OverlapFinding, ...]

    @property
    def blocks_build(self) -> bool:
        return bool(self.orphaned_paths or self.unresolved_registrations
                    or self.duplicate_tags)
```

`Component.kind` reusing Chapter 20's `ConstraintLevel` rather than introducing a parallel enum is
deliberate, and it encodes the chapter's central claim. `[INF]` The component type and the constraint
level are the same fact seen twice: the type says where an edit lives, and the level says how much
enforcement it buys. A workspace where those are two independent fields has lost the property that
makes Chapter 46's choice a choice.

`ProbeResult.matters` returning a single boolean that deliberately conflates *dead* with
*compensated* is honest rather than lazy. Both look identical from one probe, distinguishing them
needs a second probe on the suspected compensator, and an API that implied otherwise would produce
confident wrong findings.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Harness workspace (C39) | Registry | Load at boot | Files at mount points |
| Registry | Gate 1 (C39) | Blocking | Orphans, unresolved registrations, duplicate tags |
| Registry | **Chapter 46** | Read, per iteration | The inventory — the whole action space |
| Registry | **Chapter 45** | Per edit | The path and level a manifest entry names |
| Overlap detector | **Chapter 47** | On a zero result | Whether the zero means "no effect" or "compensated" |
| Benchmark (C41) | Overlap detector | Per probe | What changed when a component was removed |
| Seed policy | **Chapter 46** | Blocking | Which paths may not be deleted |
| Inventory | C42's fit meters | Annual | The seed, for standing advantage |

```
                                                             TIME VIEW

  << component.registered >>    ....> a file became live; carries
                                      path, kind, and the iteration

  << component.orphaned >>      ....> at a mount point, not loaded.
                                      An INCIDENT, not a warning --
                                      it has no other symptom (7.1)

  << overlap.declared >>        ....> two components claimed one
                                      tag; blocks the build (5.3)

  << overlap.measured >>        ....> a probe found a component
                                      whose removal changed nothing

  << component.retired >>       ....> removed from live, kept in
                                      git, revertible (C39 sec 7.2)

  << seed.drifted >>            ....> the tagged seed no longer
                                      resolves or no longer scores
                                      what it scored. The
                                      measurement space moved (5.7)

  Figure 43.9 -- What the registry makes durable (D9 Event Flow)
```

The last event is the one with the longest reach and the least obvious consequence. `[INF]` A drifted
seed does not break anything that runs. It changes the origin against which every standing-advantage
number in Chapter 42 and every gain in Chapter 47 was measured, silently and retroactively, and the
only way to notice is to re-run it.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Two components own one behaviour | Nothing, until an edit to one measures zero | Declared tags at build time; probes for the rest (§5.3). The cold open |
| A file at a mount point nothing loads | Loader-versus-filesystem reconciliation | Fail the build, never warn (§4.1) |
| A registered component with no file | Same reconciliation, other direction | Fail the build (§8) |
| Behaviour living in application code | An edit that cannot be addressed at all | Move it into the workspace, or accept it is not editable |
| Unowned failures routed to the prompt | The distribution of `constraint_level` (§5.4) | Escalate a level on the second attempt, never reword |
| The same level edited three times | The manifest's own history | E3 of Figure 43.7; the level is wrong, not the wording |
| Seed replaced with the production harness | Nothing; every number still looks like a number | The seed is the origin, not a starting position (§5.6) |
| Seed drifts or stops resolving | Re-run it on a schedule (§5.7) | Tag it; treat drift as an incident |
| All seven types are text | The constraint-level field is constant | Enforcement levels must actually differ (§3.1) |
| A probe result read as "dead" | It is equally "compensated" | Probe the suspected compensator too (§9) |
| Components accumulate, none retired | Inventory age; nothing touched in twenty iterations | Removal experiments at component grain (§4.2) |

`[INF]` The first and seventh rows are the two that matter most, and they share a property with every
Level 4 failure: the detector column says *nothing*. A harness with overlapping components and a
fitted seed runs correctly, scores well, passes both gates, and produces a stream of measurements
that are individually true and collectively meaningless.

---

## 12. Scalability

**The action space grows with the component count, and so does the overlap surface.** `[INF]` Overlap
is pairwise: thirty components have four hundred and thirty-five pairs, and declared tags are what
keep that from becoming a search. The tags scale linearly with components; the pairs do not.

**Probes scale badly and are the reason declaration matters.** One benchmark run each, so a full
probe sweep over thirty components is thirty runs. `[BP]` Probe on a rotation rather than
exhaustively — the oldest-unprobed component, plus whatever an edit most recently measured zero
against — and treat a full sweep as a quarterly exercise rather than a per-iteration one.

**Types scale differently, and Chapter 1 §12 gave the shape.** Conditionally loaded components —
skills, sub-agents, middleware hints — grow closer to free. Always-present ones — the system prompt,
resident memory — are a tax on every call. `[INF]` The registry makes that visible as a number: the
share of resident tokens by component type, tracked over iterations, is the earliest signal that a
loop is routing everything to the default owner.

**Sub-agents are the one type that degrades observability as it grows.** Chapter 19's trade stands:
isolation is bought with attribution. `[INF]` Each sub-agent is a nested harness whose components are
addressable but whose failures arrive at the parent already summarised, so the routing chain in
Figure 43.4 runs against second-hand evidence. Chapter 44 inherits this problem and does not fully
solve it.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Orphan count.** Should be zero and usually is not on first measurement. It is a one-line report
  against a list most systems already build.
- **Declared-tag coverage.** The fraction of components declaring at least one owned behaviour.
  Low coverage means the cheap detector is not working and every overlap costs a probe.
- **`constraint_level` distribution across iterations.** §5.4's health metric. A rising share of
  system-prompt edits means routing is failing, not that instructions are needed.
- **Components never probed, and oldest probe age.** The dead-and-compensated surface, made
  countable.
- **Seed score against the current model, re-measured on a schedule.** The origin. If it has moved,
  every comparison in Level 5 has moved with it.

### 13.2 The review question

For any proposed harness edit: **which component owns this behaviour, and is there a second one that
also could?**

`[INF]` The first half is answerable from the routing chain in ten seconds. The second half is the
one that would have saved the cold open three weeks, and it is answerable from declared tags in
about the same time — if the tags exist. Where they do not, the honest answer is "unknown", and
recording that is more useful than guessing, because a run of unknowns is what justifies a probe
sweep.

### 13.3 Teaching this to a new engineer

Give them the cold open's first two measurements, +0.2 and +0.1, and ask what they mean. Everyone
says the description does not matter, and the reasoning is sound.

Then show them the trace: sent `src/handlers`, received `src/handlers/**`.

`[INF]` The instinct that installs is a question rather than a technique — *what else could be doing
this?* — and it is the same instinct Chapter 42 §13.3 installs one chapter earlier, pointed at a
different baseline. Level 5's whole discipline is asking what a number is being measured against.

---

## 14. Relation to the Base Runtime

**What the base runtime already supplies.** `[DAR §2.2]` The port structure is what makes components
separable in the first place: a tool is behind a port, so its implementation and its description can
be two files rather than one function. `[DAR]` Chapter 14's split between description and
implementation, and the effect tag that accompanies it, are runtime decisions that turn out to define
two of the seven addresses.

**What this chapter adds that the runtime does not have.** A runtime needs its components to be
*separable*; a loop needs them to be *enumerable, addressable, and non-overlapping*. `[INF]` Those
are strictly stronger, and the gap between them is where the cold open lives — a system can satisfy
every architectural boundary in Levels 1 through 4 and still have two components silently owning one
behaviour.

**What the loop owes the runtime here.** It writes only at mount points, only through git, and never
to the seed. `[AHE §3.3]` Chapter 46 states the controllability constraints properly; the reason they
are expressible at all is this chapter's address space, which is the structural point §3.2 makes.

**And what remains unfinished.** `[INF]` Nothing in the source or in this handbook measures how often
overlap occurs in real harnesses, what the distribution of the three shapes in §5.2 is, or whether
declared tags are sufficient in practice. The cold open is one incident, the mechanism is clear, and
the frequency is unmeasured — which is the honest state of most of Level 5.

---

## 15. Industry Perspective

**`[AHE §3.1]`** Seven orthogonal component types exposed as files at fixed mount points, loosely
coupled so that adding middleware requires no prompt edit, each failure pattern mapping to a single
component class, over a deliberately minimal seed chosen so a pre-fitted starting point would not
contaminate attribution. `[AHE §4.4.1]` supplies the per-component ablation in Figure 43.5, including
the system prompt scoring 2.3 points below the seed it was inserted into.

**`[DAR §2.2]`** The port structure the separability rests on. The specification does not discuss
component observability and does not need to; the property it built for testability is the one this
chapter requires for attribution.

**`[INF]`** The handbook's own here: that orthogonality is an attribution property rather than
hygiene, and the derivation in §2.2 showing why; the three shapes of overlap and their distinct
measurement signatures; the disablement probe as the only mechanical detector, and the observation
that it is affordable to a loop and not to a team; the default-owner argument in §5.4 and its
prediction that unclassified failures decay into instruction text; the three mechanisms by which a
fitted seed destroys attribution; and the seed-as-instrument distinction in §5.7.

**`[BP]` Ownership declarations are ordinary practice under other names.** Code owners files, service
catalogues, and single-writer rules in data systems all encode "exactly one thing is responsible for
this". The twist here is the reason: elsewhere the goal is clear accountability, and here it is that
a difference measurement needs exactly one thing to have changed.

**`[BP]` Ablation is standard in machine learning and rare in systems engineering.** Removing a
component and re-measuring is routine for model architectures and almost never done for
configuration. The barrier has always been cost — and a system that runs benchmarks continuously has
already paid most of it.

**`[FUT]` Automatic overlap discovery is open.** Declared tags catch what is known; probes cost a run
each. `[FUT]` The obvious middle path is inference from trajectories — which components were actually
consulted on the steps where a behaviour appeared — and it is the same derivation Chapter 39 §15
proposed for the blast-radius linter, from the same data. Nobody appears to have built either.

---

## 16. Key Takeaways

1. **A component is an address with exactly one owner.** Version control gives you a diff; it does
   not tell you which part is responsible for a behaviour, and that is the property attribution
   needs.
2. **Orthogonality is an attribution property, not hygiene.** A difference measurement is meaningful
   only when exactly one thing changed. Two components that can produce the same behaviour make an
   edit to either one unmeasurable.
3. **Overlap has three shapes and they measure differently.** Compensation and shadowing produce a
   flat zero; duplication produces an unstable partial effect that reads as a marginal gain — which
   a loop will keep.
4. **The cheap detector is declaration; the complete one costs a benchmark run.** Declared tags make
   known ownership permanent. Disablement probes find the rest, and are affordable to a loop and not
   to a team.
5. **An unregistered file is a silent no-op.** It reads correctly, reviews well, diffs cleanly, and
   does nothing. Fail the build on it, because it has no other symptom.
6. **Unowned failures land on the weakest component.** The system prompt accepts any content, so it
   is the default owner by construction — and it is the one that measured below doing nothing at all.
   A second edit there for one pattern is a routing failure.
7. **The seed is the origin of the measurement space, not a starting position.** A pre-fitted seed
   cannot show a gain being earned, hands the loop a human's ownership guesses, and hides the overlap
   it already contains. Keep it tagged, keep it non-deletable, and re-run it when the model changes.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Mount point** | The fixed path a component type lives at, so an edit has a stable address to be recorded and reverted at. | `[AHE]` | Ch 45, Ch 46 |
| **Component registry** | The enumerable list of what exists, where, and at which enforcement level — the first pillar, in one object. | `[INF]` | Ch 46 |
| **Component inventory** | What exists per type with size and age, built from the loader rather than the filesystem. | `[INF]` | Ch 46 |
| **Orthogonality** | One behaviour, one owning component, required because a difference measurement needs exactly one thing to have changed. | `[AHE]` | Ch 47, Ch 48 |
| **Overlap** | Two components able to produce the same behaviour, in one of three shapes: compensation, shadowing, or duplication. | `[INF]` | Ch 47, Ch 48 |
| **Disablement probe** | Removing a component and re-measuring, which is the only mechanical way to find overlap and costs one benchmark run. | `[BP]` | Ch 47, Ch 48 |
| **Behaviour tag** | A declared claim of ownership over one behaviour, where two claimants is a build error rather than a discovery. | `[INF]` | Ch 46 |
| **Orphaned component** | A file at a mount point that nothing loads: correct, reviewed, committed, and inert, with no error at any point. | `[INF]` | Ch 46 |
| **Default owner** | The component an unclassified failure lands on, which is the system prompt and therefore the weakest. | `[INF]` | Ch 46, Ch 48 |
| **Attribution contamination** | What a pre-fitted seed does to every subsequent measurement, by moving the origin they are all taken against. | `[INF]` | Ch 47, Ch 48 |

---

**Next:** Chapter 44 — *Experience Observability.* The action space now exists and has addresses. The
next chapter supplies what aims at it: roughly ten million tokens of trajectory per batch, distilled
into ten thousand tokens of evidence, in a form something can afford to read completely rather than
sample.
