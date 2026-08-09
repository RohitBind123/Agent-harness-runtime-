```
  Level 3 · Chapter 27
  FAILURE, RECOVERY, AND ROLLBACK
  Requires   C14 The Tool Execution Engine, C17 The State Manager,
             C21 Durable Execution, C24 The Task Graph,
             C26 Planning Algorithms
  Unlocks    C30 Human Authority, C31 Safety and Sandboxing,
             C39 GitOps and CI/CD, C47 Rollback of Harness Edits
  Diagrams   Core (5)
```

# Chapter 27 — Failure, Recovery, and Rollback

---

## 1. Motivation

### 1.1 Cold open

Atlas is asked to rename `user.email_addr` to `user.email` across `accounts-service`. The plan is
five steps: write the migration, apply it to staging, update the application code, run the suite,
open a pull request.

Steps 1 and 2 succeed. The migration is applied to the staging database at 22:14.

Step 4 fails, and fails correctly — the test suite catches that `billing-service` reads
`email_addr` from the shared staging database and has not been updated. This is exactly the failure
the tests exist to produce.

The run rolls back. It reverts its commits, discards the branch, cleans its scratch directory, and
reports a clean failure with a good explanation. The trace is exemplary. Nothing is left behind in
the workspace.

At 09:00 the next morning, six engineers find staging broken. `billing-service` has been throwing
`UndefinedColumn` for eleven hours. It takes two hours to find the cause, because the run that
caused it is recorded as having rolled back cleanly, and the postmortem starts by ruling it out.

The rollback did everything it was written to do. It reverted every piece of state the runtime
owned, which was the git workspace, and it had no concept of the one piece it did not own. The
schema change was recorded in the trace as `step 2: succeeded`, and nothing anywhere connected that
success to an obligation.

### 1.2 In plain language

A run stops partway through. Some of what it did has already happened. What now?

There are three genuinely different answers, and the mistake in almost every system is to have only
one word for them.

If the thing that changed belongs to the runtime and it kept the old version — files in its own
working copy, its own scratch space, its own records — it can put the old version back. That is
rollback, and it is cheap and reliable.

If the thing that changed belongs to somebody else — a database, a cloud account, a code host — the
old version is gone and cannot be restored by wishing. The only option is to take a *new* action
that approximately undoes the first one: drop the column back, delete the resource, close the pull
request. That is compensation. It is a forward action, it can fail on its own, and somebody has to
have written it.

And if the effect left the system entirely — an email, a message in a chat channel, a webhook that
another company's software already acted on — there is nothing to take. No amount of engineering
produces an un-send.

The whole of this chapter is the consequence of those three being different. Which one applies is a
property of the tool, it is knowable before the tool runs, and a system that has not written it down
is a system that will discover it at 09:00.

### 1.3 Why this chapter exists

Chapter 21 covered surviving a crash: resume, re-run, replay, and the identity check that makes
retry safe. Chapter 26 covered choosing a planning response to a failure. Both assume the run is
going to continue.

This chapter is about the case where it does not — where a run ends with some of its effects applied
and some not, and the question is what the system owes the world it has half-changed.

That case is not exotic. **Partial failure is the normal shape of a failed agent run.** A run that
fails at step 1 is rare and easy. A run that fails at step 7 of 11, having modified a repository,
created a cloud resource, and notified a reviewer, is the ordinary case, and the design question is
not how to avoid it — it cannot be avoided — but whether the system can accurately *describe* the
state it has left behind.

`[DAR §14]` treats the failure table as a design artefact rather than as documentation, and that
framing is the chapter's spine. A failure table is not a list of things that might go wrong. It is a
per-tool contract with a column that most teams never fill in.

### 1.4 What previous framings got wrong

**"Rollback" as a single word.** It covers three operations with different costs, different failure
modes, and different availability. Systems that use one word end up with one implementation, which
is always the cheap one, which always handles only the state the runtime owns. That is the cold open
exactly.

**"Compensation is rollback for external systems."** Compensation is a *forward action*, and every
property that follows from that is inconvenient. It can fail. It needs its own identity so it is not
applied twice. It takes time and budget. It can be gated. It may require the very credentials the
run has already lost. Treating it as a variety of rollback leads to implementations that assume it
always succeeds, and the interesting question — what happens when compensation fails — is never
asked.

**"Retry until it works."** An attempt cap is not a nuisance parameter. Without one, a failure that
is deterministic rather than transient becomes an infinite spend, and the classification in
Chapter 26 §5.5 exists precisely because those two look identical for the first two attempts.

**"The failure table is documentation."** It is a schema. Each row is a field on a tool registration
that the executor reads at run time, and a tool without those fields should fail registration rather
than fail at 22:14.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Recovery is a database transaction. You begin, you do several things, and if any of them fails you
issue `ROLLBACK` and the world is as it was. Nothing partial is ever visible. The property is called
atomicity and it is one of the most useful guarantees in computing.

It is worth understanding precisely why that guarantee is available, because the reason is the same
reason it is unavailable here.

A transaction can roll back because it **owns everything it touched and nobody else could see it**.
The rows it modified were held under lock. The old versions were kept. No other process observed the
intermediate state, so discarding it is undetectable. Atomicity is bought with isolation, and
isolation is bought by controlling every reader.

A run controls no readers. When Atlas applies a migration to staging at 22:14, `billing-service`
sees it at 22:14. There is no lock, no isolation level, no held snapshot. The effect is visible the
instant it happens, to systems that begin reacting immediately, and by the time the run decides to
undo it, other things have already been decided on the basis of it.

There is no isolation level for "I sent an email".

So the transaction model contributes one genuinely useful idea — that partial effects are a problem
worth designing against — and then stops. Everything after that has to be built from a different
starting assumption: **effects are visible immediately and permanently, and the only question is
what forward action can follow.**

### 2.2 Why three tiers must exist

```
  (1) A run fails at step 4 of 11. Steps 1-3 had effects.

  (2) Cheapest response: leave them. This is correct more often
      than it sounds -- an idempotent write that will be repeated
      by the next run costs nothing to leave. Start here and ask
      what forces a different answer.

  (3) What forces it: an effect that is WRONG on its own, without
      the rest of the plan. A migration applied without the code
      change. A resource created and now unowned. A branch pushed
      that reviewers will read as intentional.

  (4) So some effects must be undone. "Undo" now splits, on one
      question: who owns the state?

  (5) The runtime owns it and kept the prior version -- working
      copy, scratch directory, run state. Restore it. This is
      real rollback: cheap, local, reliable, and it cannot
      partially fail because it is a local write.

  (6) Someone else owns it -- a database, a cloud API, a code
      host. The prior version is not ours to restore. The only
      available move is a NEW forward action that approximately
      reverses the effect. It can fail. It needs an identity.
      It costs budget. It is a step, and it belongs in the plan.

  (7) The effect left the system -- email, chat message, webhook
      another company already acted on. No forward action exists.
      Nothing can be written that helps.

  (8) Tiers (5), (6) and (7) are properties of the TOOL, knowable
      at registration, before anything runs. And for tier (7) the
      only available control is BEFORE the call. Which is what
      C30's gate is, and why it sits at the tool boundary rather
      than at the plan boundary.
```

Step (8) is where the chapter connects to the rest of the book. The gate in Chapter 30 is not a
general safety feature applied by taste. It is the sole control available for tier 3, and the tier
is a registry field.

### 2.3 The three tiers, concretely

| Tier | Name | Available operation | Examples | Cost of getting it wrong |
|---|---|---|---|---|
| 1 | **Owned** | Rollback: restore the kept prior version | Git workspace, scratch files, run state, sandbox filesystem | Low. Local, fast, cannot half-fail |
| 2 | **External, compensable** | Compensation: a new forward action | Schema migration, cloud resource, pull request, feature flag | Medium. Can fail; needs identity, budget, sometimes credentials |
| 3 | **Escaped** | None | Email, chat message, outbound webhook, published package, paid invoice | Unbounded. The only control is the gate, before |

The tier boundary that gets misplaced is between 1 and 2, and it moves with deployment details
rather than with intent. A git commit in the runtime's own working copy is tier 1. The same commit
after `git push` is tier 2, because a code host now owns it. After CI has run and notified three
reviewers, the *notification* is tier 3 even though the branch is still tier 2.

That last observation generalises, and it is the most useful single sentence in this section: **an
effect's tier is set by the most escaped thing it caused, not by the thing it did.** A tool that
looks tier 2 but triggers a notification is tier 3, and the registry must say so.

### 2.4 The mental model to carry

Every effectful tool declares a tier and, for tier 2, names its compensation. A failed run walks its
completed effects backwards, restoring tier 1 locally and running tier 2 compensations as real steps
with real failure handling. Tier 3 is not handled after the fact at all; it is handled by refusing
to reach it without authority. Everything mechanical in this chapter — leases, attempt caps,
sweepers, dead letters — exists to make that walk terminate.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +------------------------------------------------------------+
   |                     TOOL REGISTRY (C14)                    |
   |  per tool: effect tag | tier | compensation | attempt cap  |
   +------------------------------------------------------------+
            |  (1) read at registration; refuse incomplete rows
            v
   +------------------+                +----------------------+
   |  Runtime loop    |--- (2) ------->|   Effect ledger      |
   |     (C18)        |   completed    |   [[ applied ]]      |
   +------------------+   effect +     +----------------------+
            |              tier                   |
            | (3) node fails                      | (5) walk back,
            v                                     |     newest first
   +------------------+                           v
   |   Classifier     |               +-------------------------+
   |     (C26)        |               |   Recovery driver       |
   +------------------+               |                         |
            | (4) FAIL_RUN            |  tier 1 -> restore      |
            +------------------------>|  tier 2 -> compensate   |
                                      |  tier 3 -> record only  |
                                      +-------------------------+
                                                  |
                          +-----------------------+---------+
                          |                                 |
                          v                                 v
                +-------------------+          +----------------------+
                |  Compensation as  |          |   Dead-letter store  |
                |  a real step:     |          |   [[ unresolved ]]   |
                |  identity, cap,   |          |                      |
                |  budget, gate     |          |  a HUMAN queue, not  |
                +-------------------+          |  a retry queue       |
                                               +----------------------+

   Independently, and always running:

   +----------------+   lease expiry   +--------------------------+
   |   Sweeper      |----------------->|  claimed nodes whose     |
   |  (C17 leases)  |                  |  worker vanished -> back |
   +----------------+                  |  to pending, attempt++   |
                                       +--------------------------+

  Figure 27.1 -- Recovery machinery in its surroundings (D1 High-Level
                 Architecture)

  (1) a tool missing tier or compensation fails REGISTRATION, not
      its first call at 22:14
  (2) every applied effect is recorded with its tier, in the same
      transaction as the node completion (C24 sec 5.2)
  (3) failure classification is C26's; only FAIL_RUN reaches here
  (4) retry and repair never enter recovery -- the run continues
  (5) newest first, because later effects may depend on earlier ones
```

### 3.1 The effect ledger is the piece most systems lack

The cold open had a trace. It had `step 2: succeeded`. What it did not have was a record saying *and
that success created an obligation*.

The effect ledger is that record: one row per applied effect, carrying the tier, the compensation
reference, and the identity needed to run it. It is written in the same transaction as the node
completion, for exactly the reason Chapter 24 §5.2 gave about join ticks — an effect recorded
separately from its application has a window in which one exists without the other, and both
orderings of that window are silently wrong.

It is not the trace. The trace (Chapter 16) is a projection for humans and for later analysis, and
it may be sampled, truncated, or retained for ninety days. The ledger is run state: small, complete,
and consulted by code.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                    RECOVERY SUBSYSTEM                          |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |        Sweeper           |  |      Attempt policy       |   |
   |  |                          |  |                           |   |
   |  |  finds claimed nodes     |  |  cap keyed by IDENTITY,   |   |
   |  |  with expired leases     |  |  not by node id (4.2)     |   |
   |  |  -> pending, attempt++   |  |                           |   |
   |  |                          |  |  backoff: exponential,    |   |
   |  |  runs on a timer; the    |  |  jittered, capped         |   |
   |  |  ONLY component that     |  |                           |   |
   |  |  may un-claim (C24 7.1)  |  |  cap reached -> node fails|   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |    Recovery driver       |  |   Compensation registry   |   |
   |  |                          |  |                           |   |
   |  |  walks the ledger        |  |  tool -> compensating     |   |
   |  |  newest first            |  |         tool + arg mapping|   |
   |  |  tier 1: restore         |  |                           |   |
   |  |  tier 2: run compensation|  |  a tier-2 tool with no    |   |
   |  |  tier 3: record + alert  |  |  entry fails registration |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +----------------------------------------------------------+  |
   |  |                   Dead-letter store                      |  |
   |  |  work that cannot proceed and cannot be abandoned        |  |
   |  |  a QUEUE FOR PEOPLE: every row is an unresolved          |  |
   |  |  obligation with an owner and an age                     |  |
   |  +----------------------------------------------------------+  |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 27.2 -- Inside the recovery subsystem (D2 Low-Level
                 Architecture)
```

### 4.1 The sweeper is the only component that may un-claim

Chapter 24 §7.1 established that a worker may not voluntarily return a claimed node. The sweeper is
the sole exception, and the reason it is safe is that it acts on evidence the worker cannot have:
the lease expired, meaning nothing has renewed it for the full lease interval, meaning any
in-flight effect has had at least that long to land.

The lease TTL is therefore not a liveness tuning parameter. It is a bound on how long an
unacknowledged effect is allowed to be in flight, and shortening it to make recovery snappier
directly shortens that grace period. `[BP]` Set it from the p99 duration of the slowest effectful
tool plus a margin, and revisit it when a slow tool is added — not from how quickly an operator
would like to see a stuck run recover.

### 4.2 Attempt caps are keyed by identity, not by node

This is a small implementation detail with a large failure attached.

A node has an id. A repaired plan (Chapter 26 §5.3) has *new* node ids for the same work, because
it is a new plan. If the attempt cap is keyed by node id, a repair resets the counter to zero, and a
deterministic failure that survives repair can be retried indefinitely — three attempts per plan,
forever, across a lineage that never converges.

Keying the cap by Chapter 21's activity identity fixes it. The identity is a hash of the inputs, so
the same work in a repaired plan hashes the same, and the attempt count carries across the repair.
The cap then bounds attempts *at the work*, which is what it was always meant to do.

### 4.3 The dead-letter store is a queue for people

A dead letter is work that cannot proceed and must not be forgotten: a tier-2 compensation whose
attempts are exhausted, an effect whose tier is unknown, a node whose identity check found a
contradiction. It is deliberately not a retry queue with a longer timer, and the distinction is
worth being firm about because the two look identical in a schema.

A retry queue implies the system expects to resolve it. A dead-letter row is an admission that it
cannot, and its fields follow from that: what was supposed to happen, what actually happened, what a
person needs to do, and who owns it. `[BP]` The single most useful property to alert on is the age
of the oldest row — not the count. A dead-letter store with forty rows and a maximum age of ten
minutes is healthy. One with two rows aged nine days is an outage nobody has noticed.

---

## 5. Rollback, Compensation, and the Failure Table

### 5.1 The failure table as schema

`[DAR §14]`'s framing: the failure table is a design artefact. Concretely, that means it is a set of
required fields on a tool registration, checked at startup, and a tool missing any of them does not
register.

| Field | Meaning | What goes wrong without it |
|---|---|---|
| `effect` | pure or effectful (C14) | The gate, the race eligibility, and belief invalidation all break (C25 §5.2) |
| `tier` | 1 owned, 2 compensable, 3 escaped | The cold open |
| `compensation` | For tier 2: the tool that reverses it, and how arguments map | Recovery has an obligation and no action |
| `attempt_cap` | Max attempts at one identity | Deterministic failures become unbounded spend |
| `on_partial` | What is true if this fails mid-call | Retry safety cannot be reasoned about |

The last field is the one teams find hardest and it is the one that matters most for tier 2.
`apply_migration` failing halfway leaves *what*? A partially applied DDL statement, a lock held, a
migration table row claiming success? The answer determines whether retry is safe, and it is
knowable — but only by someone who goes and finds out, once, at registration time, rather than by
someone at 22:14.

### 5.2 Compensation is a step, with everything that implies

The strong version of this chapter's claim: **a compensation is not a callback. It is a node.** It
goes into a graph, it is claimed, it has an identity, it has an attempt cap, it consumes budget, and
it can be gated.

The consequences all follow from that, and each one is a bug avoided:

- **Compensation can fail**, and its failure is a normal outcome the system must handle rather than
  an unthinkable one. Exhausted attempts produce a dead letter (§4.3), not a stack trace.
- **Compensation needs identity**, or a retried compensation drops a column twice. The second
  attempt usually errors, which is the good case; the bad case is a compensation that deletes "the
  most recent resource" and deletes a different one on retry.
- **Compensation costs budget**, and a run that has failed by exhausting its budget has none. `[BP]`
  Reserve compensation budget at admission rather than discovering the shortfall at the worst
  moment — the reserve is computable, because tier-2 effects declare their compensations and their
  costs are estimable.
- **Compensation may need a gate.** Dropping a column on staging at 22:14 is probably fine.
  Dropping one in production is not, and "it is a compensation" does not confer authority the
  original action did not have.
- **Compensation runs newest first.** Later effects may depend on earlier ones, and reversing in
  application order can hit a dependency that the earlier effect still supports.

### 5.3 When compensation is worse than the damage

Not every tier-2 effect should be compensated, and reflexive compensation causes its own incidents.

A migration applied to staging at 22:14 and left alone overnight breaks one downstream service until
morning. The same migration reversed at 22:14, *after* another team's run has already written data
under the new schema, loses data. Reversal is a forward action taken with stale information about
what has happened since.

The rule that holds up: **compensate when the effect is wrong on its own, and leave it when the
effect is merely incomplete.** A pushed branch with no pull request is incomplete and harmless —
leave it, and let a sweeper clean stale branches on a schedule. A migration applied without its code
change is wrong on its own — compensate, or gate it so it never applies without the rest.

The honest third option, and often the best one for tier 2 in a shared environment: **do neither,
and raise a dead letter.** A row that says "staging has an unpaired migration, applied at 22:14 by
run r_44f, here is the reverse migration if you want it" gets the engineers of the cold open to the
answer in four minutes instead of two hours, and it does not risk destroying data on a guess.

```
                                                            LAYER VIEW

   TIER 1 -- OWNED                     restore, no thought required
   +----------------------------------------------------------+
   |  git workspace   scratch dir   run state   sandbox fs     |
   |  prior version kept -> write it back. Cannot half-fail.   |
   +----------------------------------------------------------+
                              |
                              | the boundary moves with deployment,
                              | not with intent: `git commit` is
                              | tier 1, `git push` is tier 2
                              v
   TIER 2 -- EXTERNAL, COMPENSABLE     a new forward action; a NODE
   +----------------------------------------------------------+
   |  schema migration    cloud resource    pull request       |
   |  feature flag        uploaded artifact                    |
   |                                                           |
   |  needs: identity | attempt cap | budget | maybe a gate    |
   |  may fail -> dead letter, never silence                   |
   |  DECISION: wrong-on-its-own -> compensate                 |
   |            merely incomplete -> leave                     |
   |            shared and uncertain -> dead letter (5.3)      |
   +----------------------------------------------------------+
                              |
                              | an effect's tier is set by the most
                              | ESCAPED thing it caused, not by the
                              | thing it did (2.3)
                              v
   TIER 3 -- ESCAPED                   no operation exists
   +----------------------------------------------------------+
   |  email    chat message    outbound webhook                |
   |  published package    payment    customer notification    |
   |                                                           |
   |  the ONLY control is BEFORE: the gate (C30)               |
   |  after the fact there is recording, and nothing else      |
   +----------------------------------------------------------+

  Figure 27.3 -- Three tiers of reversibility, and where each is
                 controlled (D7 Data Flow)
```

### 5.4 Rollback of harness edits

`[AHE §3.1]` gives the evolution loop file-level rollback at git granularity over the harness
workspace, and by the taxonomy above that is squarely tier 1: the loop owns the workspace, prior
versions are kept, restoration is a local write that cannot half-fail. It is the cleanest rollback
story in the book, and it is clean precisely because the workspace is owned.

The trap is assuming the property extends to the harness's *effects*. A harness variant that ran a
trial and, during that trial, opened a pull request has produced a tier-2 effect that reverting the
harness file does not touch. Chapter 47 needs this distinction sharply: rolling back a harness edit
restores the code, not the world the code acted on, and an evolution loop whose trials have external
effects needs the whole of this chapter, not the git revert.

`[BP]` The clean answer, and the one worth designing for from the start: **trials produce tier-1
effects only.** Sandbox filesystem, scratch space, and nothing else. That constraint is what makes
`[AHE §3.1]`'s rollback sufficient, and it should be enforced by the sandbox (Chapter 31) rather
than by the benchmark's good manners.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  t   Run                        Effect ledger        Recovery
  --  -------------------------  -------------------  -----------------
  0   plan minted (5 nodes)
  1   n1 write migration file    tier 1, workspace
  2   n2 apply to staging        tier 2, compensation
        SUCCEEDS 22:14           = reverse_migration
                                 identity = h(...)
  3   n3 update code             tier 1, workspace
  4   n4 run suite -> FAILS
        billing-service reads
        the old column
  5   classifier (C26):
        not transient
        repair tried once
        -> FAIL_RUN
  6                                                   walk ledger,
                                                      newest first
  7                              n3 tier 1  ------->  restore workspace
  8                              n2 tier 2  ------->  compensation node
                                                      minted, gated:
                                                      shared env + DDL
  9                                                   gate: auto-approve
                                                      (staging policy)
 10                                                   reverse_migration
                                                      runs, exit 0
 11                              n1 tier 1  ------->  restore workspace
 12   run FAILED, staging clean, one dead letter: none

  FAILURE BRANCH -- reverse_migration fails at t=10 (lock timeout,
  another run holds the table):

      attempt 2 after backoff -> fails
      attempt 3 after backoff -> fails
      attempt cap reached
        |
        v
      DEAD LETTER row:
        what should be true : accounts.user has column email_addr
        what is true        : column is named email
        applied by          : run r_44f, node n2, 22:14
        reversal available  : migrations/0042_down.sql
        owner               : accounts-service on-call
        age                 : alerted at 15 minutes
        |
        v
      the run still reports FAILED, and its failure now NAMES the
      unresolved obligation. Nobody spends two hours at 09:00,
      because the first search for "staging" finds the row.

  Figure 27.4 -- A failed run walking its effects backwards, with
                 compensation itself failing (D4 Sequence)
```

The failure branch is the point of the figure. Compensation failing is not an edge case to be
handled apologetically — it is the case that separates a system that degrades into a known state
from one that degrades into a mystery. The run failed either way. The difference is entirely in
whether the obligation was named.

---

## 7. State Management

```
                                                            STATE VIEW

   ATTEMPT (per activity identity, not per node -- see 4.2)

      {{ none }}
          |  node claimed
          v
      {{ in_flight }} ---- success ----> {{ settled }}  (terminal)
          |      |
          |      | lease expires (worker vanished)
          |      +----------------------------------+
          |                                         |
          | failure returned                        |
          v                                         v
      {{ failed }} --- attempts < cap --------> {{ backoff }}
          |                                         |
          | attempts = cap                          | timer fires
          v                                         v
      {{ exhausted }}  (terminal)             {{ none }}

   EFFECT (per ledger row)

      {{ applied }}
          |                    \
          | tier 1: restored    \  tier 2: compensation exhausted
          | tier 2: compensated  \ or compensation refused (5.3)
          v                       v
      {{ reversed }}         {{ outstanding }}
        (terminal)                |
                                  | a person resolves it
                                  v
                             {{ resolved }}  (terminal)

      {{ applied }} --- tier 3 ---> {{ escaped }}  (terminal)
                                    recorded, never reversed

      ILLEGAL: {{ outstanding }} -> {{ reversed }} without a
      compensation actually having run. An operator marking a dead
      letter "done" moves it to {{ resolved }}, which is a DIFFERENT
      state, because "a human handled it somehow" and "the system
      reversed it" must never be conflated in the record.

      ILLEGAL: any tier-3 effect leaving {{ escaped }}. There is no
      transition. The state machine is where the impossibility is
      written down.

  Figure 27.5 -- Attempt and effect states (D6 State Diagram)
```

### 7.1 Why `resolved` and `reversed` are different states

They both mean the obligation is discharged, and merging them is the obvious simplification. It
should be resisted for one reason: the ratio between them is the measure of how much of this
subsystem actually works.

A system with many `reversed` and few `resolved` is compensating successfully. A system with the
reverse is a system where compensation is nominally implemented and practically performed by people
at 09:00. Both look like "obligations discharged" on a merged counter, and only one of them is the
thing that was built.

### 7.2 Where the ledger lives

Run state, in Chapter 6's sense: owned by the run, durable, never derived, and retained after the
run ends. The retention point is easy to get wrong — a ledger deleted with the run's working data
takes the outstanding-obligation record with it, and outstanding obligations outlive their runs by
definition. `[BP]` Retain ledger rows with outstanding or escaped effects indefinitely; rows fully
reversed may be pruned with the trace.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class EffectLedger(Protocol):

    def record(self, claim: "Claim", effect: "AppliedEffect") -> None:
        """Append an applied effect. MUST be called inside the same
        transaction as the node completion (C24 sec 5.2). An effect
        recorded separately from its application has a window in which
        one exists without the other, and both orderings are silently
        wrong.
        """

    def outstanding(self, run_id: str) -> Sequence["AppliedEffect"]:
        """Applied effects not yet reversed or resolved, newest first.
        Order matters: later effects may depend on earlier ones.
        """


class RecoveryDriver(Protocol):

    def recover(self, run_id: str) -> "RecoveryOutcome":
        """Walk the ledger newest-first and discharge each effect
        according to its tier.

        Tier 1: restore locally.
        Tier 2: mint a compensation node -- a real node, with identity,
                attempt cap, budget, and gate policy. Exhaustion
                produces a dead letter, never a silent pass.
        Tier 3: record and alert. There is no reversal to attempt.

        Returns an outcome that names every unresolved obligation.
        A recovery that reversed nothing and raised no dead letter is
        indistinguishable from one that had nothing to do, so the
        outcome distinguishes them explicitly.
        """


class DeadLetterStore(Protocol):

    def raise_(self, obligation: "Obligation") -> str:
        """File work that cannot proceed and must not be forgotten.
        This is a queue for PEOPLE. Every row carries: what should be
        true, what is true, who applied it, what reverses it if
        anything, and an owner. Alert on the AGE of the oldest row,
        not the count (4.3).
        """
```

The signature that carries the argument is `record`, and specifically its docstring's demand about
the transaction. It is the one place where getting the code wrong produces the cold open exactly, and
it is a demand a type system cannot express — which is why it is stated loudly here and asserted at
run time by passing the `Claim` rather than the ids, so the implementation has the open transaction
in hand and cannot accidentally open its own.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class Tier(int, Enum):
    OWNED = 1          # rollback: restore the kept prior version
    COMPENSABLE = 2    # compensation: a new forward action
    ESCAPED = 3        # nothing exists


class EffectState(str, Enum):
    APPLIED = "applied"
    REVERSED = "reversed"        # the system reversed it
    OUTSTANDING = "outstanding"  # unreversed, owed to a person
    RESOLVED = "resolved"        # a person handled it (see 7.1)
    ESCAPED = "escaped"          # tier 3; terminal on arrival


@dataclass(frozen=True)
class AppliedEffect:
    effect_id: str
    run_id: str
    node_id: str
    identity: str                # C21 activity identity
    tool: str
    tier: Tier
    compensation: str | None     # tool name; required when tier is 2
    compensation_args: dict      # bound at APPLY time, not at reverse
    state: EffectState
    applied_at_seq: int


@dataclass(frozen=True)
class Obligation:
    """A dead-letter row. Written for a person to read."""
    should_be_true: str
    is_true: str
    applied_by: str              # run, node, timestamp
    reversal: str | None         # what would fix it, if anything
    owner: str                   # a team, never a person's name
    raised_at: str
```

`compensation_args` is bound when the effect is applied, not computed when the reversal runs, and
this is the field most likely to be got wrong. A compensation that computes its own arguments at
reversal time reads the world as it is *then* — which is minutes or hours later, after other things
have happened — and that is how "delete the most recent resource" deletes the wrong one. Binding at
apply time means the reversal targets exactly what was created, and if the target no longer exists
the compensation fails loudly rather than succeeding on something else.

`owner` is a team, never an individual. A dead letter aged nine days is usually aged nine days
because its owner was on leave.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Runtime loop | Effect ledger | Synchronous, inside the completion transaction | Applied effect + tier |
| Classifier (C26) | Recovery driver | Synchronous call on `FAIL_RUN` | Run id |
| Recovery driver | Task graph | Mints compensation nodes | A real graph, gated as policy requires |
| Recovery driver | Dead-letter store | Synchronous write | Obligation |
| Sweeper | Task graph | Periodic scan + CAS write | Expired claims returned to pending |
| Dead-letter store | Alerting | Age of oldest row, exported | One gauge |
| Recovery driver | Event spine | Outbox rows | `effect.reversed`, `effect.outstanding`, `dead_letter.raised` |

The sweeper's row is worth noting for what it does *not* carry: it does not talk to the recovery
driver, and it does not know a run is failing. It is a periodic scan over expired leases and nothing
more. Keeping it that dumb is what allows it to be correct — a sweeper that reasons about run state
is a second driver, and Chapter 32 has a great deal to say about why there must be exactly one.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Tier-2 effect with no compensation registered | Registration-time check | Refuse to register the tool. This is the cold open, caught months earlier |
| Effect ledger row committed apart from the completion | None at run time | Structural: `record` takes the open `Claim` (§8) |
| Compensation fails and exhausts attempts | Attempt cap | Dead letter with the reversal named; run still reports failed |
| Compensation succeeds on the wrong target | Usually nothing, until later | Bind `compensation_args` at apply time (§9) |
| Attempt cap keyed by node id | Attempts-per-identity exceeding the cap across a lineage | Key by activity identity (§4.2) |
| Dead letter aging unnoticed | Age of oldest row | Alert on age, not count. Owner is a team |
| Lease TTL shortened for snappier recovery | Duplicate effects appearing after sweeps | TTL is a bound on in-flight effects, not a liveness knob (§4.1) |
| Recovery budget unavailable because the run exhausted it | Compensation node refused at admission | Reserve compensation budget at admission (§5.2) |
| Tier-3 effect reached without a gate | Post-hoc, from the ledger | Nothing to do after; audit `escaped` rows against gate records and treat a mismatch as a Chapter 30 defect |

The last row describes the only genuine audit in the chapter, and it is worth running: every
`escaped` effect should correspond to a gate decision. One that does not means a tool reached tier 3
without authority, and that is a structural failure of Chapter 30's enforcement rather than a
recovery problem.

---

## 12. Scalability

**The sweeper's scan is the one thing that grows with load.** It scans claimed nodes with expired
leases across all active runs, and the naive version is a full scan on a timer. A partial index on
`(status, lease_expires_at) WHERE status = 'claimed'` makes it proportional to the expired set
rather than the active set, which is the difference between a query that costs nothing and one that
becomes the busiest statement in the database at scale.

**Recovery is bounded by effects, not by steps.** A run with 400 nodes and 3 effectful ones has a
three-step recovery. This is a good reason to keep the effectful fraction low and a good argument
against tools that bundle a read and a write.

**Dead letters must not be allowed to accumulate unboundedly**, and the bound is organisational
rather than technical. `[BP]` Alert at an age threshold measured in hours, and treat a persistently
non-empty store as an incident rather than as a backlog. A dead-letter store that everyone has
stopped reading is worse than not having one, because the system is now recording obligations into a
place that creates the appearance of handling them.

**Compensation budget reservation costs admission throughput.** Reserving at admission means
computing the tier-2 effects a plan may produce before it runs, which is a scan of the graph against
the registry. It is cheap, and it is one more reason the graph must be known before execution.

---

## 13. Production Engineering

### 13.1 The four numbers

- **Outstanding-obligation age, oldest.** The single most important number in this chapter. Alert on
  it. Everything else is diagnosis.
- **Reversed-to-resolved ratio (§7.1).** Whether compensation works, or whether people work.
- **Compensation success rate, per tool.** A tool whose compensation fails often has a compensation
  that was written once and never exercised. `[BP]` Exercise them: run the compensation path in
  staging deliberately, on a schedule, because an untested reversal is a plan, not a capability.
- **Attempts per identity, p99.** Rising means deterministic failures are being retried, which
  means the classification in Chapter 26 is mislabelling them as transient.

### 13.2 The review question

When a new effectful tool is proposed: **what is true if this succeeds and the run then fails?**

Not "what if this fails" — that question gets answered. The unasked one is the cold open, and it
takes one sentence to answer at design time and two hours to answer at 09:00. If the answer is
"something is wrong until a person fixes it", the tool needs a compensation or a gate before it
ships.

### 13.3 Teaching this to a new engineer

Hand them §1.1 and ask what the rollback missed. Most people find the migration quickly. Then ask
the follow-up that teaches the chapter: *how would the code have known to reverse it?*

The answer is that nothing in the system knew step 2 had created an obligation, because there was no
place to write that down. Once someone has reached for the effect ledger on their own, the tiers,
the compensation registry, and the dead letter all follow without being taught.

---

## 14. Relation to AHE

`[AHE §3.1]` File-level rollback at git granularity is tier 1 in this chapter's taxonomy, and it is
clean because the harness workspace is owned. The chapter's contribution is to mark the boundary
precisely: reverting a harness edit restores the code and nothing the code did. Chapter 47 depends
on that distinction being sharp, because automatic rollback of a harness edit is safe exactly to the
degree that its trials produced no tier-2 effects.

`[BP]` Which yields a design constraint worth adopting on day one: **trials produce tier-1 effects
only**, enforced by the sandbox rather than by convention (§5.4). Under that constraint the source's
rollback story is sufficient. Without it, an evolution loop needs an effect ledger and a
compensation registry, and the amount of machinery between "we can revert a file" and "we can revert
a trial" is this whole chapter.

`[INF]` The dead-letter store has an evolution-loop analogue that is worth building early: a trial
whose harness variant left the environment in an unknown state must not be scored, and it must not be
silently discarded either. It is an obligation, and an evolution loop that quietly drops its
ambiguous trials is selecting for variants that fail ambiguously.

---

## 15. Industry Perspective

**`[BP]` The saga pattern is this chapter, from a different starting point.** Long-running
distributed transactions with per-step compensating actions is exactly the tier-2 story, and the
literature's hard-won lessons transfer whole: compensations must be idempotent, they must run in
reverse order, and they can fail. What agent runtimes add is tier 3 — sagas generally assume every
step has a compensating action, and an agent's tool surface routinely includes actions that have
none.

**`[BP]` Dead-letter queues are standard in message systems and misused identically everywhere.**
The recurring mistake is treating the store as a retry buffer with a longer timer, which lets rows
age unread. The fix is the same everywhere: alert on age, assign an owner, treat a non-empty store as
an incident.

**`[DAR §14]`** The failure table as a design artefact is specified, and this chapter's addition is
the `tier` and `compensation` columns, which turn a document into something the executor reads.

**`[INF]` Infrastructure-as-code tools have the state-file version of the effect ledger.**
Terraform's state file records what it created so it can destroy it, and its well-known failure mode
— drift between the file and reality — is precisely the ledger failure this chapter designs against
with same-transaction recording.

**`[FUT]` Automatic compensation synthesis is unexplored and looks tractable for narrow domains.**
Reversing a DDL migration is mechanical. Reversing a cloud resource creation is mechanical. Nobody
appears to be generating these, and the reason is probably that the tier and identity metadata this
chapter requires is not usually present to generate from.

---

## 16. Key Takeaways

1. **Rollback, compensation, and nothing are three different operations.** Systems with one word for
   them ship one implementation, and it is always the one that only handles state the runtime owns.
2. **Partial failure is the normal shape of a failed run.** The design question is not how to avoid
   it but whether the system can accurately describe the state it left behind.
3. **An effect's tier is set by the most escaped thing it caused.** A tool that pushes a branch is
   tier 2; the same tool once CI notifies reviewers is tier 3, and the registry must say so.
4. **A compensation is a node, not a callback.** Identity, attempt cap, budget, gate policy, and a
   real failure path ending in a dead letter — everything a step has, because it is one.
5. **Record the effect in the same transaction as the completion.** A ledger written separately has
   a window where one exists without the other, and both orderings fail silently.
6. **Key attempt caps by activity identity, not by node id.** Otherwise a repair resets the counter
   and a deterministic failure retries forever across a lineage.
7. **Alert on the age of the oldest unresolved obligation.** Not the count. A dead-letter store
   nobody reads is worse than not having one, because it creates the appearance of handling.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Effect ledger** | One durable row per applied effect, carrying its tier and compensation, written in the same transaction as the node completion. | `[INF]` | Ch 30, Ch 34 |
| **Reversibility tier** | Whether an effect is owned and restorable, external and compensable, or escaped with no operation available. | `[INF]` | Ch 30, Ch 31 |
| **Rollback** | Restoring a kept prior version of state the runtime owns, which is local, cheap, and cannot half-fail. | `[AHE]` | Ch 39, Ch 47 |
| **Compensation** | A new forward action that approximately reverses an external effect, with its own identity, attempt cap, budget, and failure path. | `[BP]` | Ch 30 |
| **Escaped effect** | An effect that left the system entirely, for which no reversal exists and the only control is the gate before it. | `[INF]` | Ch 30 |
| **Failure table** | The set of registration-time fields — effect, tier, compensation, attempt cap, partial-failure state — without which a tool does not register. | `[DAR]` | Ch 31, Ch 40 |
| **Dead letter** | A durable record of an obligation the system cannot discharge, written for a person, alerted on by age rather than count. | `[BP]` | Ch 34, Ch 36 |
| **Sweeper** | The only component permitted to un-claim a node, acting on lease expiry, which is evidence the worker itself could not have. | `[DAR]` | Ch 32 |
| **Attempt cap** | A bound on retries keyed by activity identity so that a plan repair does not reset it. | `[DAR]` | Ch 32, Ch 35 |
| **Argument binding at apply time** | Recording a compensation's arguments when the effect happens rather than computing them at reversal, so a reversal cannot target the wrong thing. | `[INF]` | Ch 31 |
| **Outstanding obligation** | An applied effect neither reversed nor resolved, whose oldest age is the single number this subsystem must alert on. | `[INF]` | Ch 36 |

---

**Next:** Chapter 28 — *Reflection, Grading, and Self-Correction.* Recovery assumed something could
tell that a step had failed. This chapter is about the cases where nothing can: why a model's
judgment of its own work is unreliable in a specific and predictable direction, and the one contract
that makes model judgment usable anyway — a verdict a model may downgrade but never upgrade.
