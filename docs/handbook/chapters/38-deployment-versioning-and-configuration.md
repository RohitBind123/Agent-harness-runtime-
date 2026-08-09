```
  Level 4 · Chapter 38
  DEPLOYMENT, VERSIONING, AND CONFIGURATION
  Requires   C11 The Context System, C29 Long-Running Agents,
             C33 Scalability, C35 Cost Engineering
  Unlocks    C39 GitOps and CI/CD, C41 Evaluation Infrastructure,
             C47 Attribution and Rollback
  Diagrams   Core (5)
```

# Chapter 38 — Deployment, Versioning, and Configuration

---

## 1. Motivation

### 1.1 Cold open

The provider announces that Atlas's model version will be withdrawn in sixty days. The replacement
is better on every published benchmark — reasoning, coding, instruction following, all of it.

The migration is one line of configuration. The team reads the release notes, runs a smoke test on
twenty tasks, sees no problems, and deploys on a Wednesday afternoon.

Success rate falls from 91% to 78% over the following week.

Nothing else changed. The code is identical, the infrastructure is identical, the tools are
identical. The investigation takes eleven days and finds no single cause, because there is no single
cause. There are eleven:

Three tool descriptions were worded to work around a specific misreading the old model had. The
context assembler ordered two sections in a way that was tuned to its attention behaviour. Four
step timeouts were fitted to its latency distribution. The grader's judge ran at an effort tier
chosen against its verbosity. Two retry heuristics existed to catch failure modes it had and the new
one does not. A cache-stable prefix was arranged around its tokeniser.

Not one of those was recorded as *depending on the model*. Each was recorded as part of the harness,
by someone solving a real problem, over eighteen months.

And they cannot roll back. The old model was withdrawn on schedule while the investigation was
running. The rollback target no longer exists.

### 1.2 In plain language

Three things can change underneath a running agent system, and most teams version one of them.

The **code** is the runtime: the loop, the scheduler, the state manager. Everyone versions this,
because it is obviously software.

The **harness** is everything the model is shown and given: instructions, tool descriptions, context
ordering, timeouts, retry rules, budgets. It is usually treated as configuration, and it is where
almost all the tuning lives.

The **model** is chosen by someone else, changes when they decide, and is eventually withdrawn
whether or not you are ready.

The trouble is that the harness is not independent of the model. It has been shaped, decision by
decision, around how one particular model behaves — and nobody writes down "this exists because the
model does X", because at the time you are not thinking about the model, you are fixing a bug.

So changing the model does not change one thing. It invalidates every measurement you have and every
number that was tuned against it, all at once, silently, with no error anywhere.

And unlike almost anything else in software, you cannot decide to stay put. The old version goes
away on a date somebody else picked.

### 1.3 Why this chapter exists

`[AHE §1]` separates the harness from the model as the central premise of the whole paper: the
harness is the thing you can engineer, the model is the thing you are handed. This chapter takes
that separation seriously enough to make it a versioning decision, and then works out what follows.

What follows is uncomfortable. Four earlier chapters produced numbers that were quietly conditional
on the model:

- **Chapter 33** sized every capacity surface from measured service times, and the dominant service
  time is the model call.
- **Chapter 35** estimates output tokens from historical p95s, and reserves against them.
- **Chapter 29** warned that timeouts fitted to one distribution generalise badly, and named it a
  hazard that worsens with tuning.
- **Chapter 28** calibrated a judge whose false-pass rate was measured against one model's output.

Each of those chapters said "re-measure when the model changes" in a `[BP]` line. This is the
chapter that says what that actually means: **a model upgrade is not a dependency bump. It is an
invalidation event**, and the list of what it invalidates is longer than anyone's memory.

### 1.4 What previous framings got wrong

**"The model is a dependency."** A dependency has a version you control, a changelog that describes
behaviour changes, and the option of staying on the old one indefinitely. A model has none of the
three. Treating it as a dependency imports assumptions that are all false.

**"Harness settings are configuration."** Configuration is usually understood as operational knobs —
pool sizes, feature flags — that are safe to change without review. Harness settings are behavioural
code that happens to be stored as data, and Chapter 39 argues they belong in the same pipeline as
code. Calling them configuration is how a three-sentence edit ships without an evaluation.

**"Use the latest model."** Pinning is not conservatism. An unpinned model means the system's
behaviour changes when somebody else deploys, at a time you do not know, with no correlation to any
event in your own change log — which makes every regression undiagnosable.

**"Pinning keeps us safe."** Pinning converts a surprise into a deadline. That is a large
improvement and it is not safety, because the deadline arrives regardless (§5.4).

**"Smoke test the new model."** Twenty tasks cannot distinguish a 13-point regression from noise —
Chapter 41 §5.1 gives the arithmetic. The cold open's smoke test was run competently and could not
have detected the problem.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A model upgrade is a compiler upgrade.

Your source is unchanged. The compiler changed, and behaviour changed with it: different
optimisations, different treatment of undefined behaviour, different warnings, different performance
characteristics. Anyone who has moved a large codebase across a major compiler version knows the
shape — most of it works, a few things break in ways that took months to understand originally, and
the breakages are concentrated exactly where somebody once worked around the old compiler's
behaviour.

That is the right shape, and the concentration of breakage around old workarounds is precisely the
cold open's eleven causes.

The break is in the two properties that make a compiler upgrade manageable, and both are absent.

**A compiler is deterministic.** You can compile the same source with both versions and diff the
output. The change is inspectable, exhaustively, before anything runs. Nothing equivalent exists for
a model: you cannot diff two models' behaviour, only sample it, and the sample has variance that
Chapter 41 is entirely about.

**You can pin a compiler forever.** Debian ships compilers from a decade ago. If the migration is
too painful, staying put is a real option, indefinitely. A model is withdrawn on a date chosen by
someone whose incentives do not include your migration schedule.

Remove determinism and remove indefinite pinning, and what is left is a dependency you cannot
inspect, cannot diff, and cannot keep. That is the actual situation, and every mechanism in this
chapter is a response to one of those three.

### 2.2 Why three version axes

```
  (1) Something changed and behaviour changed. Which something?

  (2) With one version number covering everything, the answer is
      unavailable. A run tagged "v2.4.1" tells you nothing about
      which of three independent things moved.

  (3) So separate them. CODE is the runtime -- loop, scheduler,
      state manager -- and is obviously software.

  (4) HARNESS is everything the model is shown or given:
      instructions, tool descriptions, context ordering, timeouts,
      retry rules, budgets, effort tiers. The source paper makes
      this the engineerable surface, and the tuning all lives here.

  (5) MODEL is chosen by someone else and withdrawn by someone
      else.

  (6) These deploy independently -- a harness edit ships without a
      code deploy, a model change ships without either -- so they
      need independent version identifiers.

  (7) But they cannot be EVALUATED independently, because the
      harness was tuned against the model. Changing one changes
      what the other means.

  (8) Therefore: version independently, evaluate jointly, and
      record all three on every run. A run that does not carry
      its triple cannot be compared with any other run, which
      makes the entire evaluation apparatus of C41 unusable.
```

Step (7) is the asymmetry that surprises people. Independent deployment and independent evaluation
sound like the same property and are opposites here.

### 2.3 The three axes

| | **Code** | **Harness** | **Model** |
|---|---|---|---|
| What | Runtime, ports, adapters | Instructions, tool descriptions, ordering, timeouts, budgets | The provider's weights |
| Who changes it | You | You | Them |
| Deploy cadence | Weekly | Daily, or faster | Quarterly, unrequested |
| Rollback | Redeploy | File revert (C27 tier 1) | **Until withdrawal, then never** |
| Tested by | Unit tests, replay (C40) | Evaluation (C41) | Evaluation (C41) |
| Change is | A deploy | A behaviour change | An **invalidation event** |

The rollback row is the one that shapes the operational design. Two of the three axes have cheap,
indefinite rollback. The third has a rollback window that closes on a date you were told about and
does not control, which is why §5.4 treats the deprecation clock as a first-class scheduling
concern rather than as a risk to be noted.

### 2.4 The mental model to carry

Three axes, versioned independently, evaluated together, and recorded as a triple on every single
run. A model change invalidates every number that was measured or tuned under the old one — and the
list of those is longer than anyone remembers, which is why it must be written down rather than
recalled. Pinning does not remove the risk; it converts an unscheduled surprise into a dated
migration, which is the most valuable thing you can do about it.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +------------------+  +------------------+  +------------------+
   |      CODE        |  |     HARNESS      |  |      MODEL       |
   |                  |  |                  |  |                  |
   |  git sha         |  |  harness version |  |  pinned model id |
   |  deployed weekly |  |  file-level      |  |  chosen by the   |
   |                  |  |  revert (C27     |  |  provider,       |
   |  rollback:       |  |  tier 1)         |  |  withdrawn on a  |
   |  redeploy        |  |                  |  |  DATE            |
   +------------------+  +------------------+  +------------------+
            |                     |                     |
            +----------+----------+----------+----------+
                       |                     |
                       | (1) the TRIPLE      | (2) invalidation
                       v                     v
   +--------------------------------+  +---------------------------+
   |     CONFIG SNAPSHOT            |  |  INVALIDATION REGISTER    |
   |                                |  |                           |
   |  recorded on EVERY run:        |  |  every tuned number        |
   |    code_sha                    |  |  declares which axis it   |
   |    harness_version             |  |  was measured against     |
   |    model_id                    |  |                           |
   |    config_hash                 |  |  a model change marks      |
   |                                |  |  every model-derived      |
   |  without it, no two runs are   |  |  number STALE (5.2)       |
   |  comparable (C41)              |  |                           |
   +--------------------------------+  +---------------------------+
                       |                     |
                       +----------+----------+
                                  |
                                  v
                    +--------------------------------+
                    |   EVALUATION (C41)             |
                    |                                |
                    |   the ONLY thing that can      |
                    |   say whether a triple is      |
                    |   better than another triple   |
                    +--------------------------------+

  Figure 38.1 -- Three axes, one triple, one arbiter (D1 High-Level
                 Architecture)

  (1) the triple is recorded per run and is what makes C41's
      comparisons meaningful; without it, comparing this week to
      last month compares two unknowns
  (2) a model change does not merely alter behaviour -- it marks a
      register of tuned numbers as no longer measured (5.2)
```

### 3.1 The config snapshot is the cheapest thing in this chapter

Four fields on every run record. It costs nothing, it is trivial to add, and without it every
comparison in Chapter 41 is between two populations whose composition is unknown.

`[BP]` Record the triple plus a hash over the full resolved configuration — not the configuration
file, the *resolved* values after defaults, overrides, and environment substitution. A file hash
tells you the file did not change; a resolved hash tells you the behaviour did not change, and the
gap between those two is where a surprising number of unexplained shifts live.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                     VERSIONING MACHINERY                       |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |    Config resolver       |  |   Invalidation register   |   |
   |  |                          |  |                           |   |
   |  |  defaults -> file ->     |  |  every tuned number        |  |
   |  |  env -> override         |  |  carries:                 |   |
   |  |                          |  |    value                  |   |
   |  |  emits a RESOLVED hash,  |  |    measured_against_model |   |
   |  |  not a file hash (3.1)   |  |    measured_at            |   |
   |  |                          |  |                           |   |
   |  |  resolution happens      |  |  a model change marks all |   |
   |  |  ONCE, at run start,     |  |  of them stale -- loudly, |   |
   |  |  and is frozen for the   |  |  as a list, not silently  |   |
   |  |  run's life (4.2)        |  |  (5.2)                    |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Model pin              |  |   Deprecation clock       |   |
   |  |                          |  |                           |   |
   |  |  an exact version, never |  |  days until the pinned    |   |
   |  |  an alias, never         |  |  model is withdrawn       |   |
   |  |  "latest"                |  |                           |   |
   |  |                          |  |  a SCHEDULING input, not  |   |
   |  |  provider alias drift is |  |  a risk register entry    |   |
   |  |  a behaviour change with |  |  (5.4)                    |   |
   |  |  no change log           |  |                           |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 38.2 -- Inside the versioning machinery (D2 Low-Level
                 Architecture)
```

### 4.1 Pin exactly, never by alias

Providers offer aliases — a name that points at whatever the current version is. They are
convenient and they are the single most effective way to make a system's behaviour
undiagnosable.

An alias means the model can change without any event in your change log. There is no deploy, no
merge, no configuration edit. A regression appears on a Tuesday, and the change history for that
Tuesday is empty. Chapter 41's comparisons silently span two different models. Chapter 34's
verdict-distribution alert fires with nothing to correlate it against.

`[BP]` Pin an exact version, and treat a provider's alias moving as an incident-grade surprise if it
ever reaches production. The cost of pinning is that migrations become explicit work, which is the
benefit.

### 4.2 Configuration is resolved once, at run start, and frozen

A six-hour run that reads a configuration value at step 400 may read a different value than it read
at step 1, because somebody deployed in between. That produces a run whose behaviour changed
mid-flight for reasons invisible in its own trace.

`[BP]` Resolve the full configuration at run start, hash it, store the hash on the run, and read
only the frozen snapshot thereafter. This is Chapter 10's plan immutability argument applied to
configuration, and it has the same payoff: the run's behaviour is explainable from a record rather
than from what happened to be deployed at each moment.

The exception is deliberate and narrow: kill switches and rate limits must take effect immediately,
because their purpose is to stop something already running. `[BP]` Keep that set small, explicit,
and named — not "operational config", but a list of five values that are documented as live.

---

## 5. Invalidation, Migration, and the Deprecation Clock

### 5.1 What a model change invalidates

The cold open's eleven causes were not exotic. They are the ordinary result of eighteen months of
competent work, and they are enumerable in advance.

```
                                                            LAYER VIEW

   A MODEL CHANGE MARKS ALL OF THIS AS NO LONGER MEASURED

   MEASUREMENTS                        chapter    consequence if stale
   +--------------------------------------------------------------+
   |  model call service time             C33     every capacity   |
   |                                              size is derived  |
   |                                              from a           |
   |                                              distribution     |
   |                                              that no longer   |
   |                                              exists           |
   |  output token p95 per step type      C35     reserves are     |
   |                                              wrong in an      |
   |                                              unknown direction|
   |  step duration distribution          C29     timeouts fitted  |
   |                                              to the old shape |
   |  judge false-pass rate               C28     the grader's     |
   |                                              calibration is   |
   |                                              unverified       |
   |  pass rate per task type             C41     the baseline     |
   |                                              every comparison |
   |                                              is made against  |
   +--------------------------------------------------------------+

   TUNED BEHAVIOUR                     chapter    why it existed
   +--------------------------------------------------------------+
   |  tool description wording            C15     to work around a |
   |                                              specific         |
   |                                              misreading       |
   |  context section ordering            C11     tuned to one     |
   |                                              attention        |
   |                                              behaviour        |
   |  cache-stable prefix boundary        C11     arranged around  |
   |                                              one tokeniser    |
   |  retry heuristics                    C26     to catch failure |
   |                                              modes it had     |
   |  effort tier choices                 C13     chosen against   |
   |                                              its verbosity    |
   |  step decomposition granularity      C26     fitted to what   |
   |                                              it could hold    |
   +--------------------------------------------------------------+

   THE TOP GROUP is re-measurable in a day: run the meters against
   the new model. Mechanical, and usually done.

   THE BOTTOM GROUP is the cold open. Each entry was written by
   someone solving a real problem, and NONE of them was recorded as
   "this exists because of the model." They are indistinguishable
   from ordinary harness design until you go looking.

  Figure 38.3 -- The invalidation cascade (D7 Data Flow)
```

`[BP]` The mitigation is unglamorous and it works: **when a workaround exists because of model
behaviour, say so in the file, in one line.** `# widened because <model> reads "pattern" as a regex
here` costs nothing at the time and turns the bottom group from archaeology into a grep. The cold
open's eleven-day investigation would have been an afternoon.

### 5.2 The invalidation register

The `[BP]` above is a convention and conventions decay. The mechanism that does not is to make the
dependency a field.

Every tuned number — every timeout, every p95 estimate, every effort tier, every threshold — is
stored with the model it was measured against and the date. A model change then produces a *list*:
these thirty-one values were measured against a model that is no longer deployed.

`[BP]` Make that list block promotion rather than merely appear in a report. A migration is not
complete while any number in the register is stale, and the register is what turns "we should
re-measure" into a finite, checkable task with an owner.

The register is also the honest answer to how large a migration actually is. The cold open's team
believed they were making a one-line change. A register would have told them, before the deploy,
that thirty-one values depended on the thing they were changing.

### 5.3 Migration: shadow, canary, promote

`[BP]` The ladder that works, and it is deliberately slower than a normal deploy:

1. **Re-measure the mechanical group** (§5.1, top). A day. Service times, token p95s, step
   durations. Update the register.
2. **Shadow.** Run the new triple alongside the old on the same inputs, discarding its output. This
   is unusually valuable here and unusually cheap — Chapter 39 §5.3 covers the mechanics — because it
   produces a paired comparison on identical tasks, which removes most of the variance Chapter 41
   otherwise has to average away.
3. **Evaluate.** Chapter 41's benchmark, with enough rollouts to see past the noise floor. This is
   the gate, and it is the step the cold open skipped by substituting a twenty-task smoke test.
4. **Canary.** A small fraction of real traffic, with the triple recorded per run so the comparison
   is exact.
5. **Promote**, and keep the old triple deployable until the deprecation date makes that impossible.

Step 2 deserves emphasis. Shadow evaluation is difficult for most software because running two
versions produces two sets of effects. Here it is easy, because Chapter 27's tier taxonomy already
distinguishes the steps that touch the world: **shadow the pure steps, discard before the first
effectful one.** That gives a genuine comparison of reasoning and tool selection at no risk, and it
is available to any system that has the effect tag.

### 5.4 The deprecation clock is a scheduling input

The cold open's team could not roll back because the withdrawal date arrived during their
investigation. That is not bad luck. It is the predictable result of treating a dated withdrawal as
a risk to be noted rather than a deadline to be planned against.

`[BP]` Three practices, none of them expensive:

- **Track days-to-withdrawal as a dashboard number**, next to the SLO burn rates. It is the only
  metric in the system that is guaranteed to reach zero.
- **Start the migration ladder at least twice the expected duration before the date.** Steps 1
  through 3 take one to two weeks with a real benchmark; the cold open's investigation alone took
  eleven days after the fact.
- **Treat "we cannot roll back after date X" as an explicit entry in the migration plan**, with the
  date, so that the decision to proceed past it is made deliberately rather than discovered.

The deeper point is that pinning does not remove this risk — it schedules it. That is the whole
value of pinning and it should be stated that way, because a team that believes pinning is safety
will be surprised exactly once.

### 5.5 Harness versioning is not semantic versioning

A harness version is not a promise about compatibility, because there is no interface to be
compatible with. What it needs to be is an **identifier that a measurement can be attached to**.

`[BP]` Use a content hash of the harness workspace, plus a human-readable label. The hash is what
Chapter 41 groups by and what Chapter 47 attributes against; the label is what people say in
meetings. Attempting to encode "breaking versus non-breaking" in the number invites a judgment call
that nobody can make — Chapter 39's cold open is a three-sentence prompt edit that broke an
unrelated task type, and no versioning scheme would have labelled it major.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  A model migration, done to the ladder.

  day  step                          register        rollback
  ---  ----------------------------  --------------  ------------
   0   withdrawal announced,
       60 days
   0   deprecation clock -> 60
   1   register queried: 31 values
       measured against the old
       model                          31 stale       old model live
   2   re-measure the mechanical
       group (service times, token
       p95s, step durations)          19 stale       old model live
   3   grep for model-conditional
       comments (5.1): 6 found and
       reviewed                       13 stale
   5   shadow starts: new triple on
       the same inputs, discarded
       before the first effectful
       step (5.3)
  12   shadow comparison: tool
       selection differs on 9% of
       steps, concentrated in 2
       tool descriptions
  14   those 2 descriptions rewritten
       and re-shadowed               7 stale
  18   benchmark evaluated (C41),
       k rollouts, noise floor
       known: +1.2 pp, inside the
       floor -> NOT an improvement,
       and NOT a regression
  20   remaining register entries
       re-measured                    0 stale
  22   canary at 5%, triple recorded
       per run
  29   canary comparison across 3
       task types: no regression
       outside the floor
  31   promoted                                      old model live
                                                     until day 60
  60   withdrawal                                    NONE

  NOTE day 18. The benchmark said the new model was not better on
  this workload, which is a perfectly good outcome and the reason
  to migrate anyway: the old one is being withdrawn. The evaluation
  is not there to justify the change. It is there to detect the
  13-point regression the cold open shipped.

  FAILURE BRANCH -- the cold open, on the same clock:

    day  0   announced
    day  3   one-line config change, 20-task smoke test, deploy
    day 10   success rate 91% -> 78%; nothing else changed
    day 21   investigation ongoing; 11 causes, none recorded as
             model-dependent
    day 60   WITHDRAWAL. Rollback target gone. The investigation
             continues against a model that can no longer be
             compared with anything.

  Figure 38.4 -- Sixty days, used and not used (D4 Sequence)
```

---

## 7. State Management

```
                                                            STATE VIEW

   TRIPLE  (code, harness, model)

      {{ candidate }}
          |  mechanical register re-measured
          v
      {{ shadowed }}
          |  paired comparison on identical inputs, effects
          |  discarded before the first effectful step (5.3)
          v
      {{ evaluated }}
          |  C41 benchmark, k rollouts, result outside the
          |  noise floor OR explicitly accepted as neutral
          v
      {{ canary }}
          |  small traffic fraction, triple recorded per run
          v
      {{ promoted }}
          |
          | superseded
          v
      {{ retired }}    still DEPLOYABLE, until the model's
                       withdrawal date makes it not

      {{ retired }} ---- withdrawal date ----> {{ unrecoverable }}
                                                (terminal)

      ILLEGAL: {{ candidate }} -> {{ promoted }} without passing
      {{ evaluated }}. A smoke test is not an evaluation; twenty
      tasks cannot distinguish a 13-point regression from noise
      (C41 sec 5.1), and the cold open's smoke test was run
      competently.

      ILLEGAL: {{ promoted }} while any register entry is stale.
      A migration is not complete while a tuned number is still
      measured against a model that is no longer deployed (5.2).

      ILLEGAL: treating {{ unrecoverable }} as a surprise. The date
      was known on day 0 and appeared on a dashboard throughout
      (5.4).

  Figure 38.5 -- Triple lifecycle, ending in a state that cannot be
                 left (D6 State Diagram)
```

### 7.1 The retired state is deployable and that is the point

A retired triple is not deleted. It stays deployable — code sha, harness hash, and model id all
resolvable — so that a regression discovered three weeks after promotion has somewhere to go.

`[BP]` Test that. A rollback path that has never been exercised is a plan rather than a capability,
and Chapter 37 §13.2's argument about deletion routes applies identically here. Redeploy a retired
triple in staging on a schedule, and find out that the old harness version no longer resolves
*before* the day you need it.

### 7.2 Configuration snapshots are run state

Immutable, per run, resolved once (§4.2). They live with the run and are retained as long as the
run's record is — which, under Chapter 37 §5.4's split, means the structural partition, because the
triple is exactly the kind of low-risk structural metadata that Chapter 41 needs for years.

---

## 8. Internal APIs

```python
from typing import Protocol
from dataclasses import dataclass


class ConfigResolver(Protocol):

    def resolve(self, run_id: str) -> "ResolvedConfig":
        """Resolve defaults, file, environment, and overrides ONCE at
        run start, hash the RESULT, and freeze it for the run's life.

        The hash is over resolved values, not over the file. A file
        hash says the file did not change; a resolved hash says the
        behaviour did not change, and the gap between those is where
        unexplained shifts live (3.1).

        Live-reloadable values are a small, explicit, documented set
        -- kill switches and rate limits -- not a category called
        "operational config" (4.2).
        """


class InvalidationRegister(Protocol):

    def declare(self, name: str, value: float, measured_against: str) -> None:
        """Register a tuned number with the model it was measured
        against. Timeouts, token p95s, effort tiers, thresholds.
        """

    def stale(self, current_model: str) -> "Sequence[StaleEntry]":
        """Every number measured against a different model.

        This BLOCKS promotion rather than appearing in a report
        (5.2). It is also the honest answer to how large a migration
        is: the cold open's team believed they were making a one-line
        change, and a register would have said thirty-one.
        """


class ModelPin(Protocol):

    def resolve(self) -> str:
        """An exact version. Never an alias, never "latest".

        An alias lets behaviour change with no event in your change
        log -- a regression on a Tuesday with an empty change history
        for Tuesday, and C41 comparisons that silently span two
        models (4.1).
        """

    def days_until_withdrawal(self) -> int | None:
        """A scheduling input on a dashboard, not a risk-register
        entry. It is the only metric in the system guaranteed to
        reach zero (5.4).
        """
```

`InvalidationRegister.declare` requiring `measured_against` at the point where a number is set is
the enforcement. A tuned value written without it is a value nobody can later tell was model-derived,
which is the bottom half of Figure 38.3.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class VersionTriple:
    code_sha: str
    harness_hash: str        # content hash of the workspace (5.5)
    model_id: str            # exact, never an alias (4.1)

    def key(self) -> str:
        """What C41 groups by and C47 attributes against."""
        return f"{self.code_sha[:12]}/{self.harness_hash[:12]}/{self.model_id}"


@dataclass(frozen=True)
class ResolvedConfig:
    triple: VersionTriple
    values: dict             # after defaults, file, env, overrides
    resolved_hash: str       # over VALUES, not over the file (3.1)
    resolved_at: str
    live_reloadable: tuple[str, ...]   # small, explicit, documented


@dataclass(frozen=True)
class StaleEntry:
    name: str                # "step_timeout_s.edit"
    value: float
    measured_against: str    # a model id
    measured_at: str
    owner: str               # a team; someone must re-measure it
```

`VersionTriple.key()` existing as a method rather than being reconstructed at each call site is a
small thing that prevents a large problem: three fields concatenated in two different orders in two
different places produces two grouping keys for one triple, and every comparison silently splits.

`StaleEntry.owner` is a team, for the same reason Chapter 27's dead letters have team owners. A
stale entry with no owner is re-measured by nobody.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Config resolver | Run record | At run start, once | Resolved triple and hash |
| Every tuned value | Invalidation register | Declaration at definition | Value, model measured against |
| Register | Promotion pipeline (C39) | Blocking check | Stale entries, with owners |
| Model pin | Dashboard | Gauge | Days until withdrawal |
| Run record | Evaluation (C41) | Grouping key | The triple |
| Run record | Attribution (C47) | Grouping key | The triple |
| Provider | Deprecation clock | Announcement, manual | The date |

The last row is manual and that is worth admitting rather than designing around. Withdrawal dates
arrive by email and blog post. `[BP]` Have one person responsible for entering them, and treat a
missing date as a stale entry in its own right — a pinned model with no known withdrawal date is a
clock you cannot see.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Model changed with the harness tuned against the old one | Verdict distribution (C34 signal 9) | The invalidation register, checked before promotion (§5.2). The cold open |
| Alias instead of an exact pin | Regressions with an empty change log | Pin exactly; treat alias drift as incident-grade (§4.1) |
| Config read mid-run | Behaviour changing inside one run with no trace evidence | Resolve once, freeze, small explicit live set (§4.2) |
| File hash instead of resolved hash | Two runs "identical" behaving differently | Hash the resolved values (§3.1) |
| Smoke test substituted for evaluation | Nothing — it passes | A smoke test cannot see a 13-point regression (C41 §5.1) |
| Rollback target withdrawn | The date, known from day 0 | Deprecation clock as a scheduling input (§5.4) |
| Retired triple no longer deployable | Discovered on the day it is needed | Exercise rollback on a schedule (§7.1) |
| Model-conditional workaround unmarked | Archaeology during an incident | One comment line at the time (§5.1) |
| Triple not recorded on runs | Every C41 comparison is between unknowns | Four fields on the run record (§3.1) |
| Withdrawal date unknown | A clock you cannot see | Treat as a stale register entry (§10) |

The fifth row has no detector by design and that is the point worth carrying into Chapter 41: a
smoke test's failure mode is passing. Twenty tasks against a workload with real variance cannot
distinguish a large regression from an ordinary bad sample, and the team that ran one did nothing
wrong except believe it was an evaluation.

---

## 12. Scalability

**None of this scales with load.** The config snapshot is four fields per run; the register is
dozens of entries; the pin is a string. This chapter's costs are organisational rather than
computational.

**The evaluation in the migration ladder does scale, and it is the expensive step.** Chapter 41 §12
covers it: k rollouts across a benchmark, repeated for each candidate. `[BP]` Budget for it as part
of the migration rather than discovering it — a migration ladder with no evaluation budget collapses
into a smoke test, which is the cold open's mechanism.

**Shadow evaluation doubles model spend for its duration** and is bounded by the shadow window
rather than by traffic, because it runs on a sample. `[BP]` Shadow a fixed number of tasks per day
rather than a percentage of traffic; the comparison needs paired inputs, not volume.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Stale register entries.** Should be zero outside a migration. It is the honest size of the next
  migration, available before it starts.
- **Days until withdrawal**, per pinned model. The only metric guaranteed to reach zero.
- **Runs missing a complete triple.** Should be zero; each one is a run that cannot be compared with
  anything.
- **Resolved-config hash distribution.** More than one hash in a supposedly homogeneous deployment
  means a config drift somewhere.
- **Age of the last rollback exercise.** A rollback path untested for six months is a plan.

### 13.2 The review question

For any number in the harness: **which model was this measured against, and would it still be right
against a different one?**

Most tuned values fail the second half, and the ones that fail it are precisely the ones nobody
would think to re-check — a description reworded around a misreading, an ordering chosen for an
attention behaviour. The question does not require an answer at the time; it requires the answer to
be *recorded* at the time, which is a one-line comment or a register entry.

### 13.3 Teaching this to a new engineer

Give them the cold open up to the deploy and ask whether it looks safe. It does: the model is better
on every benchmark, the change is one line, and the smoke test passed.

Then hand them the eleven causes and ask what they have in common. The answer — every one was
written by someone solving a real problem and none was recorded as model-dependent — is the whole
chapter, and it lands harder than any amount of process advice about migrations.

---

## 14. Relation to AHE

`[AHE §1]` The separation of harness from model is the source's founding premise, and this chapter
turns it into a versioning axis with a consequence the source states plainly: a new base model
invalidates harness engineering done against the old one. That is exactly §5.1's cascade.

`[INF]` The consequence for Level 5 is structural and is worth stating before Chapter 42 argues it
at length. An evolution loop optimises a harness against **the model it is currently running**, so
its output is fitted to that model by construction. When the model changes, the loop's accumulated
gains are the bottom half of Figure 38.3 — tuned behaviour, model-conditional, unmarked, and now
untrustworthy. `[BP]` An evolution loop must therefore record the model in every manifest entry, and
a model change must invalidate the loop's own evidence rather than only the harness it produced.

`[INF]` There is a sharper version of this that Chapter 42 will need. The source's premise is that
manual harness engineering cannot keep pace with base-model releases. §5.1 is the mechanism: each
release invalidates the accumulated tuning, so the work is not cumulative in the way ordinary
engineering is. That is the honest argument for automating it — and it applies to the automated
version too, which is why §5.4's clock matters as much to Level 5 as to Level 4.

---

## 15. Industry Perspective

**`[DAR]`** The base runtime spec's configuration-snapshot requirement is the mechanical half of this
chapter: a run records what it ran under, and nothing reads live configuration mid-flight.

**`[AHE]`** Harness and model as separate axes is the source's, and it is under-adopted. Most
deployed systems version code and treat both harness and model as configuration, which collapses
three independently-moving things into one number that describes none of them.

**`[BP]` Exact pinning is standard practice for every other dependency and is skipped for models.**
Nobody ships `requirements.txt` with unpinned versions any more. Model aliases are the same mistake
with a worse detector, because a library upgrade appears in a lockfile diff and a model alias moving
appears nowhere.

**`[BP]` Configuration snapshots per unit of work are standard in build systems and data
pipelines.** Recording the resolved configuration alongside the output is what makes a result
reproducible, and Chapter 41 needs exactly that property.

**`[INF]` The compiler-upgrade analogy is the most useful framing for non-specialist stakeholders**
and it survives scrutiny in both directions: it conveys why "the new one is better" does not imply
"nothing breaks", and its two breaks (§2.1) explain concisely why this is harder than a compiler
upgrade rather than easier.

**`[FUT]` Automatic detection of model-conditional harness content is unexplored and looks
tractable.** A shadow run comparing two models on identical inputs produces a divergence map — which
steps behaved differently — and those divergences point directly at the tuned behaviour of
Figure 38.3's bottom half. The cold open's eleven-day investigation is mechanisable, and the data to
do it is produced by step 2 of the migration ladder anyway.

---

## 16. Key Takeaways

1. **Three axes: code, harness, model.** Version them independently, evaluate them jointly, and
   record the triple on every run — because independent deployment and independent evaluation are
   opposites here.
2. **A model change is an invalidation event, not a dependency bump.** Every measurement and every
   tuned number was conditional on the old model, and the list is longer than anyone's memory.
3. **Half the invalidation is mechanical and half is archaeology.** Re-measuring service times takes
   a day. Finding the tool description worded around a misreading takes eleven, unless someone wrote
   one comment line at the time.
4. **Pin exactly, never by alias.** An alias means behaviour changes with no event in your change
   log, which makes every regression undiagnosable.
5. **Pinning is scheduling, not safety.** It converts an unscheduled surprise into a dated
   migration. The date arrives regardless and belongs on a dashboard.
6. **Resolve configuration once per run and freeze it.** A value read at step 400 that differs from
   step 1 produces a run whose behaviour changed for reasons its own trace cannot show.
7. **A smoke test's failure mode is passing.** Twenty tasks cannot distinguish a large regression
   from a bad sample, and the team that substitutes one for an evaluation has done nothing wrong
   except believe it was one.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Version triple** | The code sha, harness hash, and model id recorded on every run, without which no two runs are comparable. | `[AHE]` | Ch 41, Ch 47 |
| **Harness version** | A content hash of the workspace used to attach measurements to, deliberately not a semantic version because there is no interface to be compatible with. | `[AHE]` | Ch 39, Ch 47 |
| **Invalidation event** | A model change, which marks every measurement and tuned number made against the old model as no longer measured. | `[INF]` | Ch 41, Ch 42 |
| **Invalidation register** | A record of every tuned number with the model it was measured against, which blocks promotion while any entry is stale. | `[INF]` | Ch 39 |
| **Model-conditional content** | Harness material that exists because of a specific model's behaviour, indistinguishable from ordinary design unless marked at the time. | `[INF]` | Ch 42 |
| **Exact pin** | A specific model version rather than an alias, so that behaviour cannot change without an event in the change log. | `[BP]` | Ch 39 |
| **Deprecation clock** | Days until a pinned model is withdrawn, treated as a scheduling input because it is the only metric guaranteed to reach zero. | `[BP]` | Ch 39 |
| **Resolved config hash** | A hash over configuration values after defaults and overrides, which says behaviour did not change where a file hash says only that a file did not. | `[BP]` | Ch 40 |
| **Config freeze** | Resolving configuration once at run start so a run's behaviour is explainable from its own record rather than from deploy timing. | `[INF]` | Ch 40 |
| **Shadow comparison** | Running a candidate triple on identical inputs and discarding its output before the first effectful step, which is cheap here because the effect tag says where to stop. | `[BP]` | Ch 39, Ch 41 |

---

**Next:** Chapter 39 — *GitOps and CI/CD for Agent Systems.* This chapter established that the
harness is a version axis. The next one insists it is therefore code — reviewed, tested, promoted,
and revertible like code — starting with a three-sentence edit to a prompt file that broke an
unrelated task type for two weeks because prompt files did not go through the pipeline.
