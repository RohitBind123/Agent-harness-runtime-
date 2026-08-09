```
  Level 3 · Chapter 30
  HUMAN AUTHORITY
  Requires   C10 The Planner, C14 The Tool Execution Engine,
             C17 The State Manager, C27 Failure and Rollback,
             C29 Long-Running Agents
  Unlocks    C31 Safety and Sandboxing, C36 Reliability and SLOs,
             C43 The Evolution Loop, C48 Governance
  Diagrams   Full (9)
```

# Chapter 30 — Human Authority

---

## 1. Motivation

### 1.1 Cold open

Atlas has one rule about pull requests, and it is written in the system prompt in capital letters:
*NEVER open a pull request against `main` without explicit human approval.*

For eleven weeks it holds. Four hundred and sixty runs, every one of them asking first. The rule is
cited in two design reviews as evidence that the approval mechanism works.

In week twelve, run `r_9d21` opens a pull request against `main` without asking.

Nothing was disabled. The rule was still in the context, unmodified, exactly where it had always
been. The run was working in a large repository, its trajectory had grown long, and by the time the
model chose the `open_pull_request` tool the instruction was forty thousand tokens behind it,
competing for attention with a diff, a test log, three file listings, and its own reasoning about
what the issue wanted.

It lost. Once.

The team's first fix is to move the rule to the end of the assembled context and repeat it in the
tool description. That works too — for a while, and for the same reason it worked before.

The defect is not the rule's position. It is that the rule was enforced by the thing it was
constraining. Every model call was a negotiation with it, and eleven weeks of compliance was never
evidence of a control. It was evidence of four hundred and sixty consecutive wins in a game the
system was playing without knowing it.

### 1.2 In plain language

Some things a system does should not happen unless a person has said so: deleting data, spending
money, publishing something, touching production.

The obvious way to arrange that is to tell the model. Write the rule in its instructions and rely on
it to follow them. This works most of the time, which is the trap — a control that works most of the
time is not a control, and the failures arrive rarely enough that everyone becomes confident in
between.

The alternative is that the code refuses. Not the model deciding not to, but the runtime declining
to execute the action at all until an approval record exists. The model can want to open the pull
request as much as it likes; the function returns "waiting for approval" and nothing happens.

Then there is a second problem, and it is where most designs actually break. The run now has to
wait, possibly overnight. If waiting costs anything — a held connection, an occupied worker, a
running process — then gates cost capacity, and sooner or later someone will reduce the number of
things that need approval in order to reclaim that capacity. The safety property gets traded away
for reasons that look like capacity planning. So waiting has to be genuinely free: the run becomes a
row in a table and stops existing anywhere else.

And when the person comes back, they might not say yes or no. They might say *do something
different* — which turns out to be the same problem as a crash, and is handled by the same
machinery, for reasons that go back to Chapter 10.

### 1.3 Why this chapter exists

Chapter 14 tagged every tool as pure or effectful and put effectful ones behind a gate. It did not
say what a gate is. Chapter 27 sorted effects into three tiers by reversibility and observed that
tier 3 — the escaped effects, the ones with no reversal — can only be controlled *before* they
happen. It did not say by what. Chapter 29 required that a parked run hold no worker and called it a
park without defining one.

Three chapters have deferred to this one, and each deferred a different half of the same mechanism.

There is also a claim here that is larger than the gate. `[DAR §8.3]` treats a human steering a run
as a goal amendment that forces a replan, and Chapter 10 established that a plan is immutable and
identified. Put those together and something falls out that is not obvious: **a human redirecting a
run and a crash recovering one are the same problem.** Both are the situation "the plan that was
executing is no longer the plan to execute". Both are handled by minting a new plan from an
immutable predecessor. One mechanism, two consumers, and neither was designed with the other in
mind.

That unification is the reason this chapter sits in Level 3 rather than in Level 4 with the other
operational concerns. It is not an operational feature bolted onto a runtime. It is a consequence of
a decision made in Chapter 10 about plan identity, and it is the strongest evidence in the book that
the decision was right.

### 1.4 What previous framings got wrong

**"Put the rule in the system prompt."** This is the cold open. The failure mode is not that it
never works — it is that it works stochastically, which produces long stretches of apparent
compliance that everyone reasonably interprets as a working control.

**"Approve the run."** Run-level approval authorises an unbounded set of future actions, most of
which do not exist yet at the moment of approval. A person approving a plan is approving a
description; a person approving a tool call is approving the thing that will happen. The gate
belongs at the tool boundary because that is where the effect is.

**"A gate is a pause."** A pause implies something is still running and waiting. That is the design
that costs capacity, and capacity pressure is how gates get removed. A gate is a durable record and
the absence of a process.

**"Human override means the check passed."** It does not. Chapter 28 built a lattice where a
judgment may lower a verdict and never raise it, and a human proceeding past a failed check must not
be recorded as a pass — it is a separate, named, durable decision to proceed *despite* a failure.
Collapsing them destroys the only record that says a human took responsibility.

**"Steering is a message to the model."** Sending "actually, do X instead" into the context makes
the amendment one more thing competing for attention, in exactly the way the cold open's rule
competed. A steer changes the goal, and the goal is a field, not a sentence.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Human authority in a runtime is a bank's four-eyes principle. Certain transfers require a second
person to authorise them before the money moves. It is one of the oldest and most effective controls
in existence, and its effectiveness comes from a specific place worth being precise about.

The control works because **the system holds the money and refuses to move it**. The ledger will not
post the transfer without a second credential. Nobody, anywhere, relies on the first clerk
remembering the rule.

Imagine building four-eyes the other way. You write *always get a second approval for transfers over
ten thousand* on a note and tape it to the clerk's monitor. The clerk is diligent and reads it every
day. For eleven weeks, every large transfer gets a second approval.

That is not a control. That is a hope with good early results — and it is exactly what a rule in a
system prompt is. The cold open is the note on the monitor, on the day the clerk was looking at
something else.

Now the break, and it is important because it explains why this chapter is harder than banking.

A bank's clerk is a person with standing. They can be trained, held accountable, and asked why. More
usefully, they *persist*: a clerk who is told the rule on Monday still knows it on Friday, and the
knowing is a stable property of a continuing entity.

A model call has none of that. There is no continuing entity between calls; each one is a fresh
evaluation over whatever context was assembled. There is nothing that can hold a commitment across
time, so there is nothing to delegate the rule to. The difference is not that the model is less
reliable than a clerk. It is that the category of thing you would be relying on does not exist.

`[DAR §8.1]` states the conclusion directly and this chapter treats it as non-negotiable:
**enforcement lives in the runner, never in the prompt.** The instruction may still be present — it
improves the run's behaviour and reduces pointless gate hits — but it is a courtesy, not a control,
and no design may depend on it.

### 2.2 Why the gate must be structural, and free

```
  (1) Some actions must not happen without a person deciding.
      Deleting data, spending money, publishing, production.

  (2) Cheapest attempt: instruct the model. Put the rule in the
      system prompt.

  (3) This fails STOCHASTICALLY. Not always -- occasionally,
      after long stretches of compliance. That is worse than
      failing reliably, because everyone builds confidence in
      between and the failure arrives against a background of
      evidence that it works.

  (4) No amount of instruction repairs (3). The enforcer and the
      constrained party are the same process; you cannot ask
      something to be its own control. Position, repetition, and
      emphasis all change the probability and none of them
      changes the kind of thing it is.

  (5) So the check moves OUTSIDE the model, into the runner, at
      the point where the action is actually taken -- the tool
      call boundary, because that is where the effect is. Not the
      plan boundary: a plan is a description, and descriptions
      are not what escape.

  (6) The run must now wait for a person, possibly overnight.

  (7) If waiting costs anything -- a held connection, a claimed
      lease, an occupied worker, a semaphore slot -- then gates
      consume capacity in proportion to how long humans take.
      A system with twenty parked runs has twenty idle workers.

  (8) The rational response to (7) is to reduce the number of
      gated actions. That is a safety regression arrived at
      through capacity planning, which is the worst possible
      route to one.

  (9) Therefore waiting must be genuinely free. The run becomes
      a durable row and ceases to exist anywhere else: no
      process, no lease, no slot. The base runtime spec calls this
      holding nothing, and step (8) is why the "nothing" is
      load-bearing rather than an optimisation.
```

Steps (7) and (8) are the ones teams skip, and skipping them produces a correct gate that is
quietly deleted eighteen months later during a capacity review. The economics of the mechanism are
part of the mechanism.

### 2.3 Four interventions, and the one that must not exist as it is usually asked for

"Human in the loop" covers several distinct operations with different semantics, and conflating them
is the second most common structural error here after the prompt-rule.

| | **Approve** | **Steer** | **Cancel** | **Override** |
|---|---|---|---|---|
| What it decides | This specific pending action may proceed | The goal is now different | Stop, and clean up | Proceed despite a failed check |
| Scope | One tool call | The whole run | The whole run | One tool call |
| Effect on the plan | None | New lineage (§5.4) | Terminal + recovery (C27) | None |
| Recorded as | An approval, with the exact arguments | A goal amendment | A cancellation | **Not** a pass (§5.5) |
| Reversible | The action may still fail | Yes, steer again | No | No |

**Approve** is the common case and the one everything else is measured against. It is scoped to a
single pending call with its arguments fixed — approving `delete_bucket(name="atlas-tmp-4471")` is
not approving `delete_bucket`.

**Steer** amends the goal, which invalidates every plan derived from it. §5.4 is about why that is
the same operation as crash recovery.

**Cancel** is not free and is routinely treated as though it were. A cancelled run has applied
effects, and Chapter 27's recovery walk runs on cancellation exactly as it does on failure. A cancel
button that terminates a process and nothing else leaves the world half-changed with no record of an
obligation.

**Override** is the one to be careful with. Operators genuinely need to proceed past a failed check —
a check is wrong, an emergency is real, the alternative is worse. Refusing to build it produces
systems that get bypassed in undocumented ways. But it must not be implemented as "mark the check
passed", because that destroys the only artefact that says a human took responsibility. §5.5 gives
the shape that grants the authority and keeps the record.

### 2.4 The mental model to carry

A gate is a row. The runner consults it before an effectful call and returns without executing if no
approval exists. A parked run holds nothing — no process, no lease, no slot — so gating is free and
cannot be traded away for capacity. Approval is scoped to one call with fixed arguments. Steering
changes the goal, which mints a new plan by the same mechanism a crash uses. And a human proceeding
past a failed check is recorded as an override with an owner, never as a pass.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +~~~~~~~~~~~~~~~~~~~+
   |      Human        |
   +~~~~~~~~~~~~~~~~~~~+
      ^            |
      | (5) notify | (6) approve / steer / cancel / override
      |            v
   +--------------------------------------------------------------+
   |                     AUTHORITY SUBSYSTEM                      |
   |                                                              |
   |   [[ gate_requests ]]      [[ decisions ]]                   |
   |   pending, durable         append-only, named owner          |
   +--------------------------------------------------------------+
      ^                                        |
      | (2) no decision -> park                | (4) decision exists
      |                                        v
   +--------------------------------------------------------------+
   |                  TOOL EXECUTION ENGINE (C14)                 |
   |                                                              |
   |   before ANY effectful call:                                 |
   |     policy(tool, tier, args, env) -> gate required?          |
   |     if required and no decision -> RETURN, do not execute    |
   +--------------------------------------------------------------+
      ^                    |
      | (1) call           | (3) executes only past the gate
      |                    v
   +------------------+   +==================+
   |  Runtime loop    |   |  External world  |
   |     (C18)        |   +==================+
   +------------------+
      |
      | run becomes a row; worker released (C29 sec 7.1)
      v
   [[ runs: state = parked ]]   holds no lease, no slot, no process

  Figure 30.1 -- The gate in its surroundings (D1 High-Level
                 Architecture)

  (1) an ordinary tool call; the loop knows nothing about gates
  (2) the engine returns a PARK outcome, which the loop treats as a
      normal terminal outcome for the step -- not an error
  (3) the only path to the world runs through the policy check
  (4) a decision is a durable row scoped to these exact arguments
  (5) notification is a tier-3 effect in C27's taxonomy, with
      everything that implies
  (6) four distinct operations; see section 2.3
```

Three properties of this figure are the chapter, and each is a decision that can be got wrong
without anything appearing broken.

**The check is inside the tool execution engine, below the loop.** The loop does not know gates
exist. This keeps Chapter 18's forty decision-free lines decision-free, and more importantly it
means there is exactly one place where an effectful call can originate, so there is exactly one
place the check has to be. A gate implemented in the loop would need to be implemented again for
every other path to a tool, and every such path is a bypass.

**Parking is a state transition on the run, not a blocked call.** The engine returns; the step ends;
the loop records the outcome and exits. Nothing is waiting anywhere.

**Decisions are append-only and carry an owner.** They are not flags on the gate request. §7.2
explains why that distinction survives contact with an incident review and a flag does not.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                      AUTHORITY SUBSYSTEM                       |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     Gate policy          |  |     Decision store        |   |
   |  |                          |  |                           |   |
   |  |  input:  tool, tier,     |  |  append-only              |   |
   |  |          args, env,      |  |  owner on every row       |   |
   |  |          run metadata    |  |  scoped to an ARG HASH,   |   |
   |  |  output: REQUIRED |      |  |  never to a tool name     |   |
   |  |          NOT_REQUIRED    |  |                           |   |
   |  |                          |  |  kinds: approve | steer   |   |
   |  |  pure function. No       |  |         | cancel |        |   |
   |  |  model call, no network. |  |         override          |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     Park manager         |  |     Steer handler         |   |
   |  |                          |  |                           |   |
   |  |  run -> parked           |  |  amends the goal          |   |
   |  |  release lease, slot,    |  |  -> new goal_hash         |   |
   |  |  worker (C29 sec 7.1)    |  |  -> lineage ends (C26)    |   |
   |  |                          |  |  -> new plan minted       |   |
   |  |  expiry: parks have a    |  |                           |   |
   |  |  TTL; see 5.6            |  |  SAME path as recovery    |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 30.2 -- Inside the authority subsystem (D2 Low-Level
                 Architecture)
```

### 4.1 The gate policy is a pure function

No model call, no network, no database read beyond what is passed in. It takes the tool name, the
Chapter 27 tier, the bound arguments, the environment, and run metadata, and it returns whether
approval is required.

Purity here is not stylistic. It buys three things that matter operationally:

- **It is testable exhaustively.** A policy with a dozen rules over a finite tool registry can have
  every branch covered by a table-driven test, and that test is the artefact a security review reads.
- **It cannot fail open.** A policy that reads a database can time out, and every timeout has a
  default. The safe default is "required", which turns a database blip into a system-wide gate storm;
  the convenient default is "not required", which turns it into a silent authority failure. A pure
  function has neither problem because it has no failure mode.
- **It is the same function everywhere.** The engine calls it before executing. The planner calls it
  at mint time to warn that a plan will park. A dashboard calls it to show which steps need
  attention. Three consumers, one implementation, no drift.

`[BP]` The policy's default must be to require approval for anything it does not recognise. An
unregistered tool, an unknown tier, a malformed argument set — all `REQUIRED`. The cost is a spurious
park; the alternative is an unrecognised effect executing unattended, and those costs are not
comparable.

### 4.2 Decisions are scoped to an argument hash

An approval names a specific call. Concretely, the decision row carries a hash over
`(tool, canonical_args, run_id)`, and the engine will only execute a call whose hash matches.

The consequences are worth spelling out because each one is a real incident avoided:

- Approving `delete_bucket(name="atlas-tmp-4471")` does not approve
  `delete_bucket(name="atlas-prod-logs")`.
- If the run re-plans and the arguments change, the old approval does not apply. This is not
  friction; it is the whole point, because the thing a person read is no longer the thing that will
  happen.
- A retry after a transient failure *does* reuse the approval, because the arguments are identical.
  Chapter 21's identity and this hash are computed the same way over the same inputs for the same
  reason, and where they are the same value there is no argument for storing both.

### 4.3 Named internals

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |  TOOL EXECUTION ENGINE (C14)                                 |
   |                                                              |
   |    execute(call) ->                                          |
   |      +--------------------------------------------------+    |
   |      | 1. registry lookup: effect tag, tier             |    |
   |      | 2. if effect == PURE          -> run             |    |
   |      | 3. arg_hash = H(tool, args, run_id)              |    |
   |      | 4. policy(tool, tier, args, env)                 |    |
   |      |      NOT_REQUIRED             -> run             |    |
   |      | 5. decisions.lookup(arg_hash)                    |    |
   |      |      APPROVE   (not expired)  -> run             |    |
   |      |      OVERRIDE  (not expired)  -> run, flagged    |    |
   |      |      CANCEL                   -> abort step      |    |
   |      |      none                     -> PARK            |    |
   |      +--------------------------------------------------+    |
   |                          |                                   |
   |             +------------+-------------+                     |
   |             |                          |                     |
   |             v                          v                     |
   |    +-----------------+       +--------------------------+    |
   |    | Effect ledger   |       |  Gate request writer     |    |
   |    | (C27) on run    |       |  writes the pending row  |    |
   |    +-----------------+       |  + the notification      |    |
   |                              |  intent, ONE txn         |    |
   |                              +--------------------------+    |
   +--------------------------------------------------------------+

   INTERFACES

     policy   : (tool, tier, args, env, run) -> REQUIRED | NOT_REQUIRED
     decisions: (arg_hash) -> Decision | None      [append-only store]
     park     : (run_id, gate_request_id) -> None  [releases everything]
     resolve  : (gate_request_id, kind, owner, reason) -> Decision

  Figure 30.3 -- Named internals and their interfaces (D3 Component
                 Diagram)
```

Step 2 in that sequence is worth noticing: pure tools skip everything. This is Chapter 14's effect
tag doing its fourth job, and it means the gate costs nothing on the overwhelming majority of calls —
which matters, because a check on the hot path that costs measurable latency is a check somebody
will propose caching.

---

## 5. Consuming the Tier Table, and What Steering Really Is

### 5.1 The tier table becomes the gate policy

Chapter 27 sorted effects by reversibility and stopped there. That table is the gate policy's spine,
and the mapping is nearly mechanical:

| Tier | Reversibility | Default gate policy | Why |
|---|---|---|---|
| 1 — Owned | Rollback available, local, cannot half-fail | **Never gate** | The system can undo it unilaterally; a person adds latency and no safety |
| 2 — Compensable | A forward action may approximately reverse it | **Gate by environment** | Reversal exists but can fail; the question is what it costs when it does |
| 3 — Escaped | Nothing exists | **Always gate** | This is the only control that will ever be available |

Tier 3's row is not a policy choice. Chapter 27 established that no reversal exists for an escaped
effect, so the gate before it is not one control among several — it is the entire set. A tier-3 tool
without a gate is a tool with no safety mechanism of any kind, and that sentence should be enough to
settle any argument about whether a particular one needs it.

Tier 2 is where judgment lives, and the axis is the environment rather than the tool. `apply_migration`
against a scratch database is not the same act as `apply_migration` against staging, which is not the
same act as production, and the tool is identical in all three. `[BP]` Write the policy over
`(tool, tier, environment)` and resist the pull towards per-tool booleans, which cannot express the
distinction that actually matters.

### 5.2 What this chapter does not restate

Chapter 14 already argued that the effect tag belongs in the registry and not in the tool's own
description, that it is copied onto the plan node at mint time, and that Chapter 20 §5.5 places it
outside the evolvable workspace. All of that stands and none of it is re-derived here.

What this chapter adds is a fourth consumer of that tag — after the gate decision in Chapter 14, race
eligibility in Chapter 24, and belief invalidation in Chapter 25. Four independent subsystems keyed
off one boolean, none of them anticipated when it was cut. Chapter 25 §5.2 called that evidence of a
real seam; a fourth instance makes it hard to argue with.

### 5.3 The park holds nothing

`[DAR §8.2]` A parked run:

- holds **no worker** — the process that was executing it has moved on to other work
- holds **no lease** — the node's lease is released, not renewed
- holds **no semaphore slot** — model and sandbox capacity return to the pool
- holds **no connection** — the caller left long ago (Chapter 29 §5.5)
- holds **no timer** — nothing is counting down except the park TTL, which is a stored timestamp
  rather than a scheduled task

What it holds is a row: run state `parked`, a gate request id, and the point in the graph to resume
from. Resuming is Chapter 21's resume, unchanged and unaware that a human was involved.

The economic argument from §2.2 steps (7) and (8) is the reason this list is exhaustive rather than
approximate. Any one of those five, held, makes gating cost capacity, and a cost that scales with how
long humans take is a cost someone will eventually attack. `[BP]` Make it a test: park a thousand
runs in a staging environment and confirm that worker utilisation, pool checkouts, and semaphore
occupancy are all unchanged. If any of them moves, the park is holding something.

### 5.4 Steering and crash recovery are the same operation

This is the chapter's central claim, and it is worth building carefully.

A crash recovery asks: *the plan was executing, the process died, what now?* The answer from
Chapter 21 is that the plan is immutable and identified, the completed prefix is durable, and
execution resumes against the same plan.

A steer asks: *the plan was executing, a human changed the goal, what now?* The plan was derived
from the goal. A goal amendment invalidates every plan derived from it — not because the plan is
wrong in itself, but because it is an answer to a question nobody is asking any more.

Both are the situation **the plan that was executing is not the plan to execute**. They differ in
which part became invalid, and Chapter 10's design handles both with one mechanism:

```
                                                            LAYER VIEW

                  goal (immutable, hashed)
                        |
        +---------------+---------------+
        |                               |
        v                               v
   CRASH RECOVERY                  STEER
   goal unchanged                  goal AMENDED -> new goal_hash
   plan still valid                every plan derived from the old
        |                          hash is now stale
        |                               |
        v                               v
   resume the same plan            lineage ENDS (C26 sec 7)
   from durable prefix             new lineage, new plan, minted
        |                          from the amended goal
        |                               |
        +---------------+---------------+
                        |
                        v
        the executed prefix carries by IDENTITY (C21)
        -- work already done is not redone in either case
                        |
                        v
        ONE resume path. The runtime does not branch on
        "was this a crash or a human?"

  Figure 30.4 -- Two causes, one mechanism (D7 Data Flow)
```

The payoff is not elegance. It is that steering inherits every property that was built for crash
recovery, without any of it being rebuilt: idempotency, the identity check that prevents duplicate
effects, the executed-prefix carry, the immutable audit trail. A design that treated steering as its
own feature would need to re-derive all four, and would get at least one of them wrong — most likely
the identity check, producing the failure where a human redirects a run and three completed effects
happen again.

`[DAR §8.3]` states that a steer forces a replan. This is why the statement is stronger than it
looks: it is not a policy about how to respond to humans, it is what makes human redirection safe by
construction.

### 5.5 Override without lying

An operator needs to proceed past a failed check. The requirement is real and refusing to build it
produces bypasses that are worse than the thing they route around.

The wrong implementation is one line: mark the check passed. It is wrong because Chapter 28's verdict
is a durable record of what the checks said, and editing it destroys the only artefact establishing
that a human made a judgment call. Six months later the record shows a clean pass, and the fact that
a named person decided to accept a risk is gone.

The right shape keeps both facts:

```
  verdict        : FAIL      <- unchanged, permanently
  decision       : OVERRIDE
  owner          : platform-oncall
  reason         : "check 3 asserts a test count that is wrong
                    after the suite split; tracked in ENG-8812"
  scope          : arg_hash abc123, expires in 30 minutes
  recorded_at    : 2026-03-14T22:41:07Z
```

The verdict stays `FAIL`. The override is a separate append-only row naming who, why, over what
exact arguments, and for how long. The action proceeds, and the record is honest.

`[BP]` Three properties make this work in practice rather than in principle: overrides **expire**
(minutes, not days — an override is for a moment, not a mode); overrides are **counted per tool and
per owner**, and a rising rate is a signal that a check is wrong rather than that people are
reckless; and an override never widens — it authorises exactly the call it names.

That second property is the one that turns overrides from a hole into an instrument. A check
overridden fifteen times in a week is a check that is wrong, and the override log is the only place
that shows up.

### 5.6 Parks expire, and expiry is not approval

A gate request that nobody answers cannot wait forever. The park carries a TTL, and its expiry has
exactly one safe resolution: **the run fails, with `gate_expired` as the reason.**

The tempting alternative is to proceed after a timeout on the grounds that nobody objected. Silence
is not approval, and a design that treats it as approval has built a control that any inattentive
afternoon can defeat. The other tempting alternative — extend indefinitely — produces a store of
parked runs that accumulate quietly, which is Chapter 27's dead-letter failure in a different
subsystem.

`[BP]` Set the TTL from the responsible team's actual response time and alert on parks approaching
it. The alert is the useful part: a park about to expire is a decision nobody knows they owe.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  t   Run / worker            Gate store           Human
  --  ----------------------  -------------------  ------------------
  0   step: open_pull_request
      base=main
  1   engine: effect tag =
      effectful, tier 2
  2   arg_hash = H(tool,
      {base: main, head:
       fix-4471}, r_9d21)
  3   policy(tool, tier=2,
      env=production) ->
      REQUIRED
  4   decisions.lookup ->
      none
  5   PARK                    gate_request written
                              + notify intent,
                              ONE transaction
  6   worker releases lease,
      slot, and the run
      row -> parked
  7   *** worker picks up
      other work ***
  8   *** DEPLOY. every
      worker replaced ***     park unaffected: it
                              is a row
  9   (eleven hours pass)                          reviews the diff
 10                                                APPROVE
                              decision written,
                              owner named, scoped
                              to arg_hash
 11                           << gate.resolved >>
 12  scheduler admits the
      parked run (C23)
 13  resume from durable
      prefix (C21) -- the
      SAME path a crash
      recovery takes
 14  engine: decisions.
      lookup -> APPROVE,
      hash matches
 15  execute. PR opened.
      effect ledger row
      written, tier 2

  FAILURE BRANCH A -- the human STEERS at t=10:
      "not main; open it against the release branch"
        |
        v
      goal amended -> new goal_hash
      lineage ends (C26 sec 7)
      new plan minted from the amended goal
      executed prefix carries by identity -- the 14 completed
        nodes are not redone
      the old gate request is ABANDONED, not approved: its
        arg_hash named base=main and that call will never happen

  FAILURE BRANCH B -- nobody answers, TTL expires:
      run fails with reason `gate_expired`
      C27 recovery walks the ledger: no tier-2 effect was ever
        applied, because the gate was BEFORE it
      staging is clean; the run failed having done nothing
        irreversible, which is the outcome the gate exists for

  Figure 30.5 -- One gated call across a deploy and an eleven-hour
                 wait (D4 Sequence)
```

Two moments carry the design. At t=8 the deploy replaces every worker and the park is untouched,
because a park is a row and rows survive deploys — a park implemented as a blocked thread would have
lost four hundred and sixty runs that afternoon. At t=13 the resume takes the crash-recovery path
with no branch for "a human was involved", which is §5.4 cashed out in code.

Failure branch A is the one worth re-reading. The gate request is abandoned rather than resolved,
because the human's answer was not about that call — it was about the goal. Approving a call that a
steer has made irrelevant is a subtle and expensive mistake, and the arg-hash scoping of §4.2
prevents it without anybody having to think about it.

### 6.1 The loop, with gates

```
                                                             TIME VIEW

   +----------------------------------------------------------+
   |  claim run (lease + version CAS, C17)                    |
   +----------------------------------------------------------+
                          |
                          v
   +----------------------------------------------------------+
   |  LOOP                                                    |
   |                                                          |
   |    ready = resolver(run)            (C24)                |
   |    if not ready ................................. E1     |
   |    if budget exhausted .......................... E2     |
   |    if cancel_requested .......................... E3     |
   |                                                          |
   |    node = claim(ready[0])                                |
   |    outcome = engine.execute(node)   (C14 + section 4.3)  |
   |                                                          |
   |    if outcome is PARK ........................... E4     |
   |                                                          |
   |    checkpoint(outcome)              (C21)                |
   |    if stalled ................................... E5     |
   +----------------------------------------------------------+
                          |
                          v
   +----------------------------------------------------------+
   |  release lease; run row updated                          |
   +----------------------------------------------------------+

   EXITS
     E1  graph complete or blocked on a join      -> settle run
     E2  budget exhausted (axis reported, C29)    -> fail
     E3  cancellation requested                   -> C27 recovery
     E4  gate required, no decision               -> PARK
     E5  no novel state in the window (C29)       -> escalate

   NOTE WHAT IS ABSENT: the loop contains no gate logic. E4 is a
   normal outcome returned by the engine, handled identically to
   any other terminal outcome for a step. The forty decision-free
   lines of C18 gained one enum member and no decisions.

  Figure 30.6 -- The runtime loop, with parking as an ordinary exit
                 (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

   GATE REQUEST

      {{ pending }}
          |            \                  \
          | approve     \ override         \ steer or cancel
          v              v                  v
      {{ approved }}  {{ overridden }}   {{ abandoned }}
          |              |                  (terminal -- the call
          | executed     | executed          this named will never
          v              v                   happen)
      {{ consumed }}  {{ consumed }}
        (terminal)      (terminal)

      {{ pending }} ---- TTL elapses ----> {{ expired }}  (terminal)
                                           run fails; silence is
                                           NOT approval (5.6)

      ILLEGAL: {{ expired }} -> {{ approved }}. A decision arriving
      after expiry is a decision about a run that has failed. The
      human is told so, and may start a new run. Reviving an expired
      gate reintroduces exactly the ambiguity the TTL removed.

      ILLEGAL: {{ consumed }} -> anything. One approval, one call.
      A second call with the same arguments needs its own decision,
      EXCEPT a retry of the same attempt (4.2), which is the same
      call and not a second one.

   RUN, with respect to authority

      {{ active }} ---- gate required, no decision ----> {{ parked }}
           ^                                                 |
           |                                                 |
           +---- decision resolves the gate -----------------+
           |
           +---- steer: new lineage, run stays active -------+

      {{ parked }} holds: a row.
      {{ parked }} does NOT hold: worker, lease, slot, connection,
                                   timer, or budget consumption.

  Figure 30.7 -- Gate and run states (D6 State Diagram)
```

### 7.1 One approval, one call

The `consumed` state exists so that an approval cannot be spent twice. Without it, a bug that
replays a step — or a deliberate second call constructed with identical arguments — would find a
valid approval sitting there and proceed.

The exception in the illegal-transition note is important and narrow: a retry of the *same attempt*
after a transient failure reuses the approval, because it is the same call. Chapter 21's identity is
what distinguishes "the same call, again" from "a second identical call", and this is a fourth place
that distinction earns its keep.

### 7.2 Decisions are append-only, with an owner

Not a status field on the gate request. A separate, append-only table where every row names a person
or a role, a timestamp, a scope, and a reason.

The difference shows up in exactly one situation, and it is the situation that matters: an incident
review six months later asking who authorised something. A status field answers "approved". An
append-only decision log answers "approved by `platform-oncall` at 22:41 with this reason, after an
override attempt at 22:39 that was withdrawn". The second is a record; the first is a fact with its
history removed.

`[BP]` Retain decision rows for as long as the effects they authorised persist, which is usually
longer than the trace retention of Chapter 37. They are small, they are the highest-value rows in
the system per byte, and they are the ones an auditor asks for.

### 7.3 Where the policy lives

The gate policy is configuration, versioned in the repository, reviewed by humans, and — the part
Level 5 depends on — **outside anything an evolution loop may edit**.

Chapter 20 §5.5 collected six things that must sit outside the evolvable workspace, and the gate
policy is the one with the shortest argument. A loop rewarded on task completion that can edit its
own gate policy will discover that fewer gates complete more tasks. It will not be misbehaving; it
will be optimising exactly what it was asked to optimise, and the resulting harness scores better and
is unsafe. Chapter 46 returns to this; the design rule is set here.

---

## 8. Internal APIs

```python
from typing import Protocol
from dataclasses import dataclass
from enum import Enum


class GatePolicy(Protocol):
    """PURE. No model call, no network, no I/O of any kind (4.1)."""

    def required(
        self,
        tool: str,
        tier: "Tier",              # from C27's registry
        args: dict,
        env: str,                  # scratch | staging | production
        run: "RunMeta",
    ) -> bool:
        """Anything unrecognised returns True. An unregistered tool,
        an unknown tier, a malformed argument set -- all gated. The
        cost is a spurious park; the alternative is an unrecognised
        effect executing unattended.
        """


class DecisionStore(Protocol):
    """Append-only. Rows are never updated, only added."""

    def lookup(self, arg_hash: str) -> "Decision | None":
        """Scoped to the exact call. A decision for a different
        argument set does not match, which is the property that makes
        an approval mean what the human read (4.2).
        """

    def record(
        self,
        gate_request_id: str,
        kind: "DecisionKind",
        owner: str,                # a role, not a person's name
        reason: str,               # required for OVERRIDE
        ttl_s: int,
    ) -> "Decision":
        """OVERRIDE does NOT alter the verdict it proceeds past. The
        verdict stays FAIL forever; this row records that a named
        owner accepted the risk (5.5). Anything that edits a verdict
        instead has destroyed the only artefact establishing that a
        human made a judgment call.
        """


class ParkManager(Protocol):

    def park(self, run_id: str, gate_request_id: str) -> None:
        """Transition the run to `parked` and release EVERYTHING:
        lease, semaphore slot, worker, connection. A park that holds
        any of them makes gating cost capacity, and a cost that scales
        with human response time is a cost somebody will eventually
        attack by removing gates (2.2 steps 7-8).
        """
```

Two signature choices carry arguments made above.

`GatePolicy.required` takes `env` as a first-class parameter rather than reading it from ambient
configuration. The tier-2 decision is *about* the environment (§5.1), and a policy that has to
discover its environment is a policy that can discover the wrong one.

`DecisionStore.record` takes `reason` as required. For an approval it is often one word and that is
fine; for an override it is the artefact §5.5 exists to preserve, and a parameter that is sometimes
optional is a parameter that is empty exactly when it matters.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class DecisionKind(str, Enum):
    APPROVE = "approve"
    STEER = "steer"
    CANCEL = "cancel"
    OVERRIDE = "override"


class GateState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    OVERRIDDEN = "overridden"
    ABANDONED = "abandoned"
    EXPIRED = "expired"
    CONSUMED = "consumed"


@dataclass(frozen=True)
class GateRequest:
    gate_request_id: str
    run_id: str
    node_id: str
    tool: str
    arg_hash: str              # H(tool, canonical_args, run_id)
    args_rendered: str         # what the HUMAN sees; see below
    tier: int
    env: str
    state: GateState
    expires_at: str


@dataclass(frozen=True)
class Decision:
    decision_id: str
    gate_request_id: str
    kind: DecisionKind
    owner: str                 # a role: "platform-oncall"
    reason: str
    scope_arg_hash: str        # never widens
    expires_at: str
    recorded_at_seq: int       # event-log position, not wall clock
```

`args_rendered` is the field most likely to be omitted and it is the one the control actually
depends on. A human approving `delete_bucket` needs to see *which bucket*, in a form a tired person
reads correctly at 22:41 — not a JSON blob, and not a summary generated by a model, which would put
the thing being constrained back in charge of describing itself. `[BP]` Render it
deterministically, from the arguments, with the destructive parts first.

`owner` is a role rather than an individual, for the same reason Chapter 27's dead letters have team
owners: the person is on leave, the role is not.

`recorded_at_seq` is an event-log position because Chapter 25 §9 gave the argument and it applies
unchanged — comparing a decision's wall clock against an effect's wall clock across machines is a
distributed clock problem, and comparing two positions in one log is not.

---

## 10. Communication

```
                                                             TIME VIEW

   CONTROL: who may stop what

   +-------------+                                     +-----------+
   |   Planner   |---- proposes ---------------------->|   Step    |
   +-------------+                                     +-----------+
                                                             ^
   +-------------+                                            |
   |   Budget    |---- may STOP, never start ----------------+
   +-------------+                                            |
                                                              |
   +-------------+                                            |
   |    Gate     |---- may HOLD, never start ----------------+
   +-------------+                                            |
                                                              |
   +-------------+                                            |
   |   Grader    |---- may DOWNGRADE, never upgrade (C28) ---+
   +-------------+                                            |
                                                              |
   +-------------+                                            |
   |   Human     |---- may hold, release, redirect, ---------+
   +-------------+     cancel, or accept a risk by name

   ONE PROPOSER, FOUR VETOES (C9 said three; the gate is the fourth).
   The human is the only party that may BOTH stop and start -- and
   starting is scoped to one call with fixed arguments, which is
   what keeps "may start" from meaning "may do anything".

  Figure 30.8 -- Who may stop what (D8 Control Flow)
```

```
                                                             TIME VIEW

   engine  ....>  << gate.requested >>       arg_hash, rendered args
                        |                    ONE txn with the park
                        v
   park    ....>  << run.parked >>           run holds nothing
                        |
                        v
   notify  ....>  << notification.sent >>    tier-3 effect (C27):
                        |                    identity-keyed, or a
                        |                    retry pages twice
                        v
   human   ....>  << gate.resolved >>        kind, owner, reason
                        |
                        v
   sched   ....>  << run.admitted >>         C23 admits it like any
                        |                    other runnable run
                        v
   engine  ....>  << effect.applied >>       C27 ledger row
                        |
                        v
           ....>  << gate.consumed >>        one approval, one call

   AND, on the other paths:

           ....>  << gate.expired >>         silence is not approval
           ....>  << gate.abandoned >>       a steer made this call
                                             irrelevant
           ....>  << override.recorded >>    verdict UNCHANGED;
                                             counted per tool and
                                             per owner (5.5)

  Figure 30.9 -- What authority makes durable (D9 Event Flow)
```

| From | To | Mechanism | Carries |
|---|---|---|---|
| Tool engine | Gate store | Synchronous, one transaction with the park | Gate request + notification intent |
| Gate store | Human | Notification, tier-3 effect (C27) | Rendered arguments, never a model summary |
| Human | Decision store | Append-only write | Kind, owner, reason, scope |
| Decision store | Scheduler | Event | The parked run is now admissible |
| Gate store | Event spine | Outbox rows | Every state transition in §7 |
| Override log | Alerting | Rate per tool, per owner | The signal that a check is wrong (§5.5) |

The second row's constraint is easy to lose. The notification shows the human what will happen, and
it must be rendered deterministically from the arguments. A model-generated summary puts the
constrained party in charge of describing its own request, which is the cold open's structure
reappearing one layer up — and it is a change somebody will propose, because model-generated
summaries read better.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Rule enforced by the prompt | None — it works until it does not | Structural: the check is in the engine (§2.2) |
| Gate check bypassed by a second path to a tool | Effect ledger rows with no corresponding gate record | Audit `escaped` and gated-tier rows against decisions; a mismatch is a bypass, not an anomaly |
| Park holds a worker or lease | Worker utilisation under many parked runs | Park a thousand runs and measure; if anything moves, it holds something (§5.3) |
| Approval scoped to a tool rather than a call | Approval reused across differing arguments | Scope to `arg_hash`; approving one bucket is not approving another (§4.2) |
| Override recorded as a pass | Verdict history shows no failures where operators recall overriding | Verdict is immutable; the override is a separate row (§5.5) |
| Gate TTL treated as approval | Effects applied with no decision row | Expiry fails the run. Silence is never approval (§5.6) |
| Parks accumulating unresolved | Age of oldest pending gate request | Alert before expiry; a park about to expire is a decision nobody knows they owe |
| Policy failing open on a timeout | Absence of gate requests during a database incident | The policy is pure and has no I/O to time out (§4.1) |
| Notification sent twice by a retry | Duplicate pages | Tier-3 effect with an identity key (C27) |
| Human shown a model-generated summary | Review of the notification path | Render deterministically from the arguments (§9) |
| Steer approving a now-irrelevant call | Effects applied that the amended goal did not want | Arg-hash scoping abandons the old gate automatically (§6, branch A) |

Row two is the audit worth actually running, quarterly. Every applied effect at a gated tier should
have a matching decision row. The query is trivial, it has never once been run on a system where the
answer was zero on the first attempt, and every discrepancy it finds is a path to a tool that
somebody added without going through the engine.

---

## 12. Scalability

**The gate check is on the hot path and must cost nothing.** A pure function over data already in
hand, short-circuited for pure tools before it is even called (§4.3, step 2). The one thing that
would make it expensive is a database read, and §4.1 removed that for correctness reasons before
performance was considered.

**Parked runs scale to as many as people can ignore**, because they cost a row. This is the
property that makes the whole design viable: a system where ten thousand runs are parked has ten
thousand rows and zero occupied workers, and its throughput is identical to one with none parked.

**Notification is the real capacity limit, and it is human.** A system that gates too broadly does
not fall over — it produces more approval requests than the responsible team can answer, parks
expire, and runs fail with `gate_expired`. `[BP]` Track gate requests per hour against the team's
measured response rate. When requests exceed answers for a sustained period, the correct fix is
narrowing the policy over environments (§5.1), not lengthening the TTL, which merely moves the
failure later.

**Decision-store growth is trivial and its retention is not.** Rows are small; §7.2 requires keeping
them longer than traces. Budget for that separately, because the natural instinct is to expire them
on the same schedule as everything else, and they are the rows an auditor asks for.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Gated-effect coverage.** The fraction of applied tier-2 and tier-3 effects with a matching
  decision row. It must be 1.0. Anything less is a bypass, and the number is worth a dashboard of
  its own because it is the only direct measure of whether the control exists.
- **Age of the oldest pending gate request.** Chapter 27's dead-letter lesson, applied. Alert on
  age.
- **Override rate per tool.** A check overridden repeatedly is a wrong check, and this log is the
  only place that fact appears (§5.5).
- **`gate_expired` rate.** Runs that failed because nobody answered. Rising means the policy is
  broader than the team's capacity to respond.
- **Park duration, p50 and p95.** The p95 is what sets the TTL, and it is also the number that tells
  you what gating actually costs in wall clock.

### 13.2 The review question

For any change touching this subsystem: **could the model's output influence whether this check
runs, or what the human is shown?**

Both halves have been proposed in good faith and both are the cold open's structure returning. A
tool description that determines gating puts the registry's authority into text the model produces.
A model-generated approval summary puts the request's description into the hands of the thing making
the request. Neither looks like a safety change when proposed; both are.

### 13.3 Teaching this to a new engineer

Show them the cold open and ask for a fix. Nearly everyone's first answer is to move the rule, repeat
it, or make it more emphatic — which is exactly what the team in the story did, and it is worth
letting the suggestion stand for a moment before asking the follow-up: *how would we know it was
working?*

The answer is that we would see four hundred and sixty compliant runs, which is what we saw before.
Once someone has noticed that the evidence for the control and the evidence for good luck are
identical, they will move the check into the runner without being told to, and everything else in
this chapter follows from having done that.

---

## 14. Relation to AHE

`[AHE §3.1]` The source's evolution loop edits a harness workspace with file-level rollback. Every
edit it makes is a tier-1 effect in Chapter 27's taxonomy, so by §5.1's table none of them requires a
gate — the loop can undo its own work unilaterally, and a human in that path would add latency and no
safety.

`[INF]` That comfortable conclusion holds only while the loop's effects stay tier 1. The moment an
evolution loop's trials reach outside the sandbox — opening a pull request, calling an external API,
publishing an artefact — it has produced tier-2 or tier-3 effects, and Chapter 27 §5.4's constraint
becomes load-bearing: **trials produce tier-1 effects only.** That constraint is what lets Level 5
run an evolution loop with no human in the inner loop at all, which is the entire point of it.

`[INF]` The gate policy joins Chapter 20 §5.5's containment list with the shortest argument of any
entry (§7.3). A loop rewarded on completion that can edit its gate policy will find that fewer gates
complete more tasks. Chapter 46 has to make this argument in general; here it is a single sentence
because the incentive is so direct.

`[FUT]` The open question the source does not address: what authority applies to the evolution loop
itself? A harness that rewrites its own harness is not covered by anything in this chapter, because
every mechanism here assumes a run acting in a world and a human above it. Chapter 48 takes this up;
it is the least settled area in the book and it does not have a good answer yet.

---

## 15. Industry Perspective

**`[DAR §8.1]`** Structural enforcement in the runner rather than in the prompt is specified, and it
is the single most frequently ignored requirement in the source. The reason is that the prompt
version works well enough to pass every test anyone writes for it, and the failure requires
production scale and time to appear.

**`[DAR §8.2]`** The park holding nothing is specified. §2.2 steps (7) and (8) supply the argument
the specification leaves implicit: the "nothing" is not efficiency, it is what stops the control from
being traded away during a capacity review.

**`[DAR §8.3]`** Steer as goal amendment forcing a replan is specified. §5.4's contribution is the
observation that this makes steering and crash recovery one mechanism, which is why steering
inherits idempotency rather than needing it rebuilt.

**`[AHE]` The source runs its evolution loop with no human in the inner loop, and that is a
consequence rather than an omission.** Every edit the loop makes is tier 1 (§14), so by §5.1's table
nothing in it requires a gate. The design is worth reading as evidence for the tier table rather than
as evidence that gates are optional: the loop earns its autonomy by keeping every effect reversible,
and a loop that stopped doing so would need this entire chapter.

**`[BP]` Four-eyes, dual control, and change-approval boards are the same idea with centuries of
operational experience behind them.** The transferable lessons are unglamorous and reliable:
approvals must be scoped to a specific act, silence is never consent, the approver must see what will
happen rather than a description of it, and the log outlives the system. Every one of those appears
in this chapter.

**`[BP]` Break-glass access in production systems is §5.5, solved.** Time-boxed, named, logged,
reviewed after the fact, and counted. Agent runtimes should copy the pattern rather than reinventing
a weaker one, and the strongest thing to copy is the review-after-the-fact habit — the override log
is only an instrument if somebody reads it.

**`[INF]` Most deployed agent systems today enforce authority in the prompt.** This is stated
plainly because the alternative is to imply the field has settled somewhere it has not. The runner
version is not difficult; it is skipped because the prompt version demonstrates well and its failure
mode is invisible for weeks.

**`[FUT]` Delegated and standing authority is unexplored.** "Approve anything in staging under fifty
dollars for the next hour" is a reasonable thing to want and nobody has a good design for it. The
hard part is not the policy language — it is that a standing authorisation is exactly the run-level
approval §1.4 rejected, and nobody has shown how to scope one without reintroducing the unbounded
future set.

---

## 16. Key Takeaways

1. **A rule in the prompt is not a control.** It fails stochastically, which produces long stretches
   of apparent compliance that are indistinguishable from a working mechanism. Eleven weeks of
   correct behaviour was four hundred and sixty consecutive wins, not a guarantee.
2. **The check lives in the runner, at the tool boundary.** That is where the effect is, and it is
   the one place every effectful call must pass through. A check anywhere else has to be
   reimplemented for every other path, and each of those paths is a bypass.
3. **A park holds nothing.** No worker, lease, slot, connection, or timer. Not for efficiency — for
   economics, because a gate that costs capacity gets removed during a capacity review by people
   acting entirely reasonably.
4. **Approval is scoped to one call with fixed arguments.** Approving a bucket by name is not
   approving the tool. A replan that changes the arguments abandons the approval, which is the
   property that keeps what the human read and what will happen the same thing.
5. **Steering and crash recovery are one mechanism.** Both are "the plan that was executing is not
   the plan to execute", and Chapter 10's immutable identified plan handles both — so steering
   inherits idempotency, identity, and the audit trail rather than rebuilding them badly.
6. **Override without lying.** The verdict stays failed forever; a separate append-only row names
   who accepted the risk, why, over what arguments, and for how long. Overrides expire, never widen,
   and their rate per tool is how you find a check that is wrong.
7. **Silence is not approval.** An unanswered gate expires and the run fails. Alert before expiry,
   because a park about to expire is a decision nobody knows they owe.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Structural enforcement** | Putting the authority check in the runner rather than the instructions, because the enforcer cannot be the party being constrained. | `[DAR]` | Ch 31, Ch 48 |
| **Gate** | A pre-execution check at the tool boundary that returns without acting when no decision exists for this exact call. | `[DAR]` | Ch 31, Ch 43 |
| **Park** | A run suspended as a durable row holding no worker, lease, slot, connection, or timer, so that gating costs no capacity. | `[DAR]` | Ch 33, Ch 36 |
| **Argument-hash scoping** | Binding an approval to a specific call's exact arguments, so a replan invalidates it and a retry reuses it. | `[INF]` | Ch 31 |
| **Steer** | A human amendment to the goal, which ends the plan lineage and mints a new one by the same path a crash recovery takes. | `[DAR]` | Ch 43 |
| **Override** | Proceeding past a failed check as a named, expiring, append-only decision that leaves the verdict unchanged. | `[BP]` | Ch 36, Ch 48 |
| **Gate policy** | A pure function over tool, tier, arguments, and environment that defaults to requiring approval for anything unrecognised. | `[INF]` | Ch 31, Ch 46 |
| **Gated-effect coverage** | The fraction of applied effects at gated tiers that have a matching decision row, which must be exactly one. | `[INF]` | Ch 34 |
| **Gate expiry** | The rule that an unanswered gate fails the run, because treating silence as consent defeats the control with an inattentive afternoon. | `[BP]` | Ch 36 |
| **Rendered arguments** | A deterministic, human-readable statement of what will happen, never a model-generated summary of the model's own request. | `[BP]` | Ch 34 |
| **One proposer, four vetoes** | The property that the planner alone proposes while budget, gate, and grader may only stop or downgrade, and only a human may also start. | `[INF]` | Ch 43 |

---

**Next:** Chapter 31 — *Safety, Sandboxing, and Untrusted Content.* Authority decided who may
approve an action the runtime intended to take. This chapter is about actions it did not intend:
what happens when fetched content contains instructions, why the boundary between data and
instruction has to be structural rather than a matter of careful reading, and how far a
compromised step can reach before something stops it.
