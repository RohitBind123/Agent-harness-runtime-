# Interlude I — Assembling a Minimal Runtime

*After Chapter 20. Before Level 3.*

---

You have now read twenty chapters describing components one at a time. That is the only way to
explain them and it is not how anybody builds them, so this interlude does the other thing: it builds
a runtime, in order, and stops at the point where Level 3 becomes necessary.

There is no template here, no diagram budget, and no new vocabulary. Everything below has already
been defined. What is new is the sequence — which piece comes first, what each one buys, and what
breaks if you take them in a different order.

The build follows stages 0 through 2 of the architecture roadmap. Stage 3 onward needs Level 3.

---

## Before the first line

Two decisions, and both are cheap now and expensive in a month.

**Decide which generation you are building.** Chapter 0 ended with this and it is the only genuinely
reversible-if-you-do-it-now choice in the book. If your work is one turn, has no irreversible
actions, and finishes inside an HTTP request, stop reading and build that. Chapter 2's disqualifiers
are honest ones. Everything that follows costs weeks and buys properties you may not need.

**Set up the harness as a directory in git.** Not because you need it yet, but because Chapter 43
needs it later and retrofitting it means moving prompts out of source files and tool descriptions out
of decorators, one at a time, while the system is running. Seven directories and a registry file,
today, empty. It costs an afternoon.

```
  workspace/
    agent.yaml
    systemprompt.md
    LongTermMEMORY.md
    tool_descriptions/
    tools/
    middleware/
    skills/
    sub_agents/
```

---

## Stage 0 — The spine

*Outbox, relay, one queue, command port. Chapter 22 covers this properly; the shape is enough here.*

The first thing to build is the least interesting and the most load-bearing: a way for something that
happened to reliably cause something else to happen.

Three tables and one worker.

```sql
CREATE TABLE outbox (
  id           bigserial PRIMARY KEY,
  event_type   text NOT NULL,
  payload      jsonb NOT NULL,
  claimed_by   text,
  claimed_at   timestamptz,
  processed_at timestamptz
);
CREATE INDEX ON outbox (id) WHERE processed_at IS NULL;
```

The relay claims rows rather than tracking a cursor. Chapter 2 flagged the difference as one of the
places a familiar answer is wrong here: a cursor stalls the whole stream behind one poison event,
and a claim isolates it.

**Done when:** you can write a row to `outbox` inside a transaction that also changes something else,
and a separate process picks it up and does work. That is the entire property. Everything durable in
the rest of the system is this mechanism wearing a different name.

**What it buys:** the ability to make a state change and its announcement atomic. Chapter 9 §5.2
called this the one rule that makes the event axis worth having, and every later guarantee about not
losing work depends on it.

**Why first:** because it cannot be added later without rewriting every write path. A system that
grew without an outbox has state changes and notifications in separate transactions everywhere, and
the migration touches all of them.

---

## Stage 1 — The run

*Runs table, lease plus version CAS, episode driver, one hardcoded step. Chapters 5, 17, 18.*

Now build the thing that carries work. Resist making it clever: one step, hardcoded, that does
nothing but increment a counter.

```sql
CREATE TABLE runs (
  id            uuid PRIMARY KEY,
  tenant_id     text NOT NULL,
  goal          jsonb NOT NULL,
  state         text NOT NULL,
  current_step  int  NOT NULL DEFAULT 0,
  version       int  NOT NULL DEFAULT 0,
  lease_owner   text,
  lease_until   timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON runs (lease_until)
  WHERE state NOT IN ('SUCCEEDED','FAILED','CANCELLED','DEAD_LETTERED');
```

Two columns for ownership, one for safety. Chapter 17 argued at length that this is not a lock, and
the argument only becomes visceral when you write the sweeper and discover that recovery is a
`WHERE` clause rather than a subsystem.

Then the loop from Chapter 18, with its four exit conditions, calling nothing. Claim, advance,
checkpoint, release. Perhaps thirty lines, because there are no ports yet to call.

**Done when:** a run advances and survives `kill -9` mid-step. Kill a worker; the run resumes on
another one at the step after its last checkpoint, with no manual intervention and no restart.

That test is the whole of stage 1 and it is worth being pedantic about. Do it with a real signal, not
a graceful shutdown — a drain proves the drain works, and what you are testing is the case where
nothing got to run.

**What it buys:** the run is now independent of every process, which is Chapter 8's two clocks made
real. From here on, worker restarts are routine rather than incidents.

**What to resist:** adding a second step type, a planner, or anything model-shaped. The temptation is
strong because the runtime does nothing visible yet. Every one of those is easier to add once the
recovery property is proven, and impossible to debug if it is not.

---

## Stage 2 — The activity

*Activity ledger, identity hash, lease, abort signal, one real tool. Chapters 13, 14, 15, 21.*

Now the run gets to do something, and this is where the architecture earns its complexity.

```sql
CREATE TABLE activities (
  activity_id  text PRIMARY KEY,     -- the HASH, not a serial
  run_id       uuid NOT NULL,
  state        text NOT NULL,
  result       jsonb,
  attempts     int  NOT NULL DEFAULT 0,
  lease_owner  text,
  lease_until  timestamptz,
  cost_cents   int
);
```

The primary key is the identity from Chapter 10 §5.1 — `hash(run_id, plan_id, step_id, tool_id,
input_digest)` — computed when the step is planned, before anything runs. Chapter 14 §4.2 explained
why that timing is not negotiable: an identity computed at dispatch cannot prevent the duplicate
dispatch that computes the same identity at the same instant.

Build the model port next, and build it properly the first time. Chapter 13's four properties are all
cheap now and all painful to retrofit: one door, metering, a cap taken before the call, and an abort
handle. The one to get right on day one is settling an abandoned call at its reservation rather than
at zero, because the alternative is invisible and Chapter 13's cold open is what invisible costs.

Then one real tool. Make it pure, make it bounded, and give it a description in
`tool_descriptions/`, separate from the implementation — Chapter 14 §2.2's two surfaces, from the
start, because merging them later means splitting a file that everything imports.

**Done when:** a model call runs off-lock, and a replay never re-spends. Concretely: start a run,
kill the worker while a model call is in flight, let it recover, and check the bill. The completed
call's result is reused. The activity ledger shows one charge.

**What it buys:** the determinism quarantine from Chapter 3's MM4. Non-determinism now lives in one
identifiable place, which is what makes everything in Level 3 — replay, rollback, testing —
constructible at all.

**The trap here** is holding a database connection across the model call. It is the natural way to
write it, every other job in your codebase does it, and it is Chapter 2's cold open. The check is
Chapter 18 §5.3's table: while an activity is in flight, the worker holds a semaphore slot and
nothing else.

---

## What you have after three stages

A runtime that accepts a goal, drives it across many workers and many restarts, calls a model
without holding anything scarce, executes one tool, and never pays twice for the same work.

Roughly two thousand lines, most of it SQL and error handling. It is not impressive to look at, and
it has every property that makes the rest of the book possible.

What it does not have yet:

| Missing | Chapter | Symptom you will hit first |
|---|---|---|
| A planner | 10 | one hardcoded step is not a product |
| Context management | 11 | cost per step climbing as runs get longer |
| Gates on effectful tools | 30 | the first time it does something you cannot undo |
| Grading | 28 | you cannot tell whether a change made it better |
| Admission control | 23 | one tenant's slow work starving everyone |
| Observability worth the name | 16, 34 | debugging by reading logs |

---

## The order matters more than the pace

Two things in that list are commonly built early and should not be.

**Do not build the planner before stage 2.** A planner produces steps, and steps without identity are
work you will pay for twice. Chapter 10 §5.1's hash includes `plan_id` for a reason, and retrofitting
identity onto an existing planner means every stored result becomes of unknown reusability — Chapter
2's warning that reliability retrofits well and identity does not.

**Do build grading earlier than feels necessary.** Chapter 0 §16 put it plainly: the failure that
kills an agent product is not pool exhaustion under load, because you will not have load for months.
It is confident, plausible, wrong work that nobody notices. Stage 4 in the roadmap is where grading
sits, and the argument for moving it earlier gets stronger the longer you have been shipping without
it.

---

## A note on what this interlude skipped

Everything about making it survive contact with reality. Retries, dead letters, sweeper tuning,
partition behaviour, admission, fairness, tenancy, the failure table.

That is not an oversight in the ordering — it is Level 3, and it is deliberately after this point.
A system that has stages 0 through 2 working has the properties those chapters build *on*. A system
that tried to build them first would be adding retry policy to something that cannot yet recover from
a restart.

---

**Next:** Level 3 — *Advanced Runtime Architecture.* Durable execution, the event spine, the
scheduler, task graphs, the world model, planning algorithms, failure and rollback, grading,
long-running behaviour, human authority, safety, and distribution. Twelve chapters that take the
runtime you have just assembled and make it survivable.
