# Chapter 5 — The Five Nouns: Run, Episode, Step, Activity, Park

## Tracking

**CURRENT POSITION**
Level 1 — High-Level Runtime Architecture
Chapter 5 / 49 — The Five Nouns: Run, Episode, Step, Activity, Park

**COMPLETED**
Ch 0–3 (Level 0 — foundations), Ch 4 (six layers, the narrow waist, one full wire trace)

**TODAY**
Chapter 5 — the exact vocabulary every later chapter is written in

**UNLOCKS**
Ch 6 (state separation becomes precise), Ch 8 (two independent lifecycles), Ch 17 (the state manager), Ch 18 (the runtime loop — the episode gets built out in full), Ch 21 (durable execution — activity identity gets its full treatment)

---

## A correction, before anything else

Your notes from before described the five nouns as **"Run, Plan, Step, Activity, Episode."** Now that I've read Chapter 5 directly, here's the precise correction:

**Almost. The boundary is:** the fifth noun is **Park**, not Plan — and Plan isn't one of the five nouns at all. A **Plan** is a *different* concept entirely: it's the artifact the Planner produces (you'll get its full treatment in Chapter 10). A Run can go through *several* plans over its life — every replan mints a new `plan_id` under the same run. So Plan isn't a peer of Run/Episode/Step/Activity/Park; it's something a Run *has*, referenced by a `plan_id` column on the run row. The actual five, exactly as the chapter titles them: **Run, Episode, Step, Activity, Park.**

---

## WHY THIS CHAPTER EXISTS

`#atlas-incidents`, 09:41: *"the agent is stuck on `acme/billing-service`."* Four engineers read that sentence and start four different investigations — one checks the model provider's status page, one greps for crash loops, one queries for long-held leases, one opens the approvals table. Forty minutes later, the fourth one is right: a human hasn't clicked a button yet, on a flight, and the system is doing **exactly what it's supposed to do** — waiting, indefinitely, holding nothing.

Three engineers burned forty minutes each because one word — "stuck," or worse, "the agent" — was being asked to mean five different things with five different fixes. This chapter's entire job is to hand out five words so that never happens to you.

You already have the underlying mechanics — leases, heartbeats, workers, queues. What you're missing is the **vocabulary that tells you which mechanism is in play for a given kind of "waiting."** That's what today adds.

---

## THE CORE IDEA — five nouns, five (resource, duration) pairs

The chapter's central move is derived, not arbitrary. Different things in this system hold wildly different resources for wildly different durations:

```
a pooled DB connection ....... ~5 ms
a worker (a whole process) ... ~60 s
a model concurrency slot ..... 1-2 min
a row ......................... minutes to weeks
nothing ....................... unbounded
```

One word ("the agent") covering all five tells you nothing about *which* scarce resource is actually at risk — and exhaustion is per-resource: a drained connection pool, starved workers, contended model slots, and a human who hasn't answered yet are **four different incidents needing four different responses**. So you need at least one word per (resource, duration) pair. There are exactly five. Hence:

| Noun | Lifetime | Holds | Scarcity of what it holds |
|---|---|---|---|
| **Run** | minutes to weeks | one row | abundant |
| **Park** | unbounded | one row | abundant |
| **Activity** | seconds to minutes | a semaphore slot + budget reservation | scarce (4–6 slots) |
| **Episode** | seconds | one worker | scarce (8–16 workers) |
| **Step** | milliseconds | one DB connection, briefly | very scarce (pool of ~20) |

**The custody gradient** (`[INF]`, the chapter's organizing principle, and the same custody rule from Chapter 2/4 generalized into a property of the *whole noun set*):

> Scarcity × duration is held roughly constant. The longer a noun lives, the less scarce the thing it's allowed to hold.

Every violation you'll ever be tempted to commit is a case of moving one noun up-and-to-the-right on that table — holding a connection across a model call (Step's resource, Activity's duration), or holding a lease across a park (Episode's resource, Park's duration). Same mistake, both times.

---

## THE FIVE NOUNS, ONE LEVEL DEEPER

### Run — one goal, a row, and nothing else

**Plain meaning:** one goal under execution — for Atlas, one labelled issue in one repository.

**Why it's the unit:** it's the *only* noun that's durable, addressable from outside, and versioned. You `submit` a run, `stream` a run, `signal` a run, cancel a run. Everything else in this chapter is internal machinery a caller never names directly.

**Mechanically, it's a row** in the `runs` table:
```
id . tenant_id . goal . state . plan_id . current_step
version          <- CAS counter: exactly one advance commits
lease_owner . lease_until   <- who is driving it, until when
budget_cap . budget_used
```
**Connect to what you know:** `version` is the optimistic-concurrency column you already understand from CAS — a driver attempting to advance the run must supply the version it last read; if another driver already advanced it, the write affects zero rows, and the loser simply drops its attempt. No lock manager, no distributed coordination — the same "let the database's own atomicity do the coordinating" trick you saw in Chapter 4's `FOR UPDATE SKIP LOCKED`, applied here via a CAS write instead of a row lock.

**The property that matters most:** a run costs nothing but a row, so having ten thousand of them, nearly all doing nothing at any instant, is *free*. This is the number that makes the rest of the chapter make sense (see the scalability numbers below).

### Episode — not a row, a function invocation

**Plain meaning:** one bounded *working session* on a run. A worker picks the run up, makes some progress, and puts it back down. Seconds long. Never more than one happening for a given run at once.

**Why it exists — the actual tension it resolves:** durability wants a checkpoint at *every single step* (crash anywhere, lose at most one step). Responsiveness and cost want a *tight in-process loop* (no queue hop, no prompt-cache rebuild, between steps). Those pull in opposite directions. The Episode takes the checkpoint from the first goal and the loop from the second: **every durability property is preserved — a checkpoint still follows every step — what changes is only how often you pay the queue-hop cost.**

**Mechanically, here's the loop a worker process actually runs:**
```
claim the lease                (a CAS write on runs.version + lease_until)
loop:
    advance one step           (no DB connection held during this)
    checkpoint                 (~5ms: version CAS, lease renewal, release)
    read pending signals       (same transaction as the checkpoint — free)
    test exit conditions
exit on: E1 wall clock . E2 step budget . E3 park required . E4 signal
final checkpoint, release lease, re-enqueue if not terminal
```

**Why "read pending signals in the same transaction" is a real engineering decision, not incidental:** if signal-reading were a *separate* round trip, there'd be a window where a signal (say, a human's "cancel") arrives *between* your checkpoint and your signal check — and you'd miss it until the next step. Bundling it into the same transaction as the checkpoint write means there is no such window: the read is atomic with the write that would otherwise have raced it.

**IMPORTANT BOUNDARY — Episode ≠ Run.**
A Run is durable, queryable, addressable — you can ask "what state is run r-8f2 in?" at any time, because it's a row. An Episode is *not* a row at all. It leaves behind only its side effects (the checkpoints it wrote). **You cannot query for episodes.** If you want to know how many steps an episode ran, you infer it from checkpoint timestamps — which is exactly why Chapter 34 turns "steps per episode" into a derived metric rather than a queryable field: a distribution with a mode at 1 means episodes are exiting after a single step, i.e. you're paying the queue-hop cost on every step and getting none of the locality benefit the Episode exists to buy you.

**The dial, not a commitment:** set the step budget to 1, and you've exactly reproduced a strict one-step-per-worker-invocation system. This is a *configuration* knob, not an architectural bet — which is worth remembering, because it means adopting the Episode costs you nothing in optionality; you can always turn the loop back down to zero.

### Step — one advance, milliseconds, a connection held briefly

**Plain meaning:** one small advance of the run's state machine. Two kinds:

| Kind | Does | Costs | Example |
|---|---|---|---|
| **Decision step** | Advances using only what's already known | microseconds, no model call | route to next planned step; mark a check passed |
| **Activity step** | Dispatches an Activity, then lets go | the activity's own cost | run the test suite; ask the model for a patch |

**Why the split matters mechanically:** a decision step is why the fast queue from Chapter 4 exists. Most steps in a healthy run are decisions. If a decision step had to queue behind a 40-second model call, your control plane would move at data-plane speed — exactly the MM5 (control/data plane) coupling you already know is a mistake.

**The "connection held for ~5ms" detail, made concrete:** at a step's checkpoint, the worker takes an already-open, pooled connection (the same TCP socket/fd from Chapter 4's pool), issues one `UPDATE`/`INSERT`, commits, and returns the connection to the pool — all within roughly five milliseconds. Contrast this precisely with the cold-open failure from Chapter 4: holding that *same kind* of connection across a 30-second model call instead of a 5ms write is the exact custody violation the gradient warns you about — same resource, a duration six thousand times longer than it's supposed to be held.

**Steps are history, never edited:** `run_steps` rows are keyed by `(run_id, plan_id, step_id)`. A replan writes *new* rows under a *new* `plan_id` — it never edits the old ones. Old rows are marked `SUPERSEDED`, not deleted.

**IMPORTANT BOUNDARY — Turn ≠ Step**, since this is the one that trips up anyone arriving from a framework that thinks in conversational turns:
```
ONE MODEL TURN                    MAPS TO
model emits a tool request    ->  1 Activity step (the model call itself)
runtime executes the tool     ->  1 Activity step (the tool call)
result appended to history    ->  1 decision step (append, route)
```
One "turn" is typically 2–3 Steps, and can span an Episode boundary if the step budget runs out mid-turn. A turn is a unit of *conversation*; a Step is a unit of *durability*. They are not the same size, and they do not nest cleanly — which is exactly why the handbook counts Steps, not turns.

### Activity — the quarantine, and where identity actually lives

**Plain meaning:** one call out to a model or a tool. The expensive part — seconds to minutes, real money.

**Five non-optional properties:**

| Property | Means | Without it |
|---|---|---|
| Idempotent | Re-claim replays the stored result | A retry re-spends and re-rolls (Ch 2's cost incident) |
| Leased | One runner owns it; expiry makes a crash recoverable | A dead runner's work is stranded forever |
| Cancellable | A deadline/signal aborts the *real* call | A timeout leaks the operation (Ch 2's §4.4) |
| Budgeted | Cost reserved at dispatch, settled at completion | A run overspends by everything in flight |
| Quarantined | The *only* place non-determinism is permitted | Replay stops being sound |

**Mechanically, the identity is a hash, and it's the primary key:**
```
activity_id = hash(run_id, plan_id, step_id, tool_id, input_digest)
```
**Why a hash-as-primary-key is a genuinely clever mechanism, worth sitting with:** because the identity is *computed deterministically from content*, two completely independent workers — say, the original dispatcher and a re-claiming worker after a crash — that are each asked "run this step" will independently compute the *exact same* `activity_id`, without ever having talked to each other. The database's own unique-constraint-on-primary-key does the deduplication for free: if a row with that id already exists and is `COMPLETED`, the second attempt finds it and replays the stored result instead of re-running anything. No coordination service needed — same trick as the CAS and the row-lock, a third time, at a third layer.

**IMPORTANT BOUNDARY — `activity_id` ≠ `plan_id`.**
A `plan_id` identifies *which plan* a step belongs to — it's assigned once, when the planner commits a plan, and a replan mints a brand-new one. An `activity_id` is *downstream* of `plan_id` — it's a hash that *includes* `plan_id` as one of its five ingredients. This is precisely why identity must be computed at **plan** time and not at **dispatch** time: if identity didn't include `plan_id`, a stale activity from a superseded plan could be silently mistaken for a valid one under a new plan — the exact "silent, confident, wrong" failure class Chapter 2 named as the worst bug the system can have.

**IMPORTANT BOUNDARY — this hash-based `activity_id` ≠ the idempotency key from Chapter 2.**
Related mechanisms, different layers. The idempotency key (Chapter 2, at the *edge*) is something the *caller* supplies when submitting a command, so a redelivered command doesn't double-execute. `activity_id` (here, *inside* the kernel) is computed by the *system itself* from the content of a planned step, so a redispatched activity doesn't double-execute. Same underlying goal — dedupe a repeat — solved at two different boundaries, one caller-supplied, one system-computed.

### Park — the general waiting primitive

**Plain meaning:** the run waiting — for a human, a timer, an external reply, a budget grant — and it can last indefinitely because it holds **nothing at all**.

**Mechanically, Park is not even its own table.** It's:
```
runs.state = PARKED
plus ONE of:
    a row in `approvals`     (awaiting a human decision)
    a row in `approvals`     (awaiting a budget grant)
    a pending question       (awaiting missing input)
    a scheduled wake time    (awaiting a timer)
    an expected external event  (awaiting a callback)
```

**This is the important mechanical fact, stated as bluntly as possible:** when a run parks, there is **no thread waiting, no open connection, no in-memory timer object sitting anywhere.** It is a row sitting idle in a database table, indistinguishable at the OS level from any other idle row. The worker that parked it has already released its lease and moved on to serve some *other* run entirely. Waking it up uses the **exact same pipeline as everything else in Chapter 4**: a human clicks "approve" → an event (`approval.decided`) is appended → the relay claims it (the same `FOR UPDATE SKIP LOCKED` claim from Chapter 4) → it's routed to the fast queue → some run driver — quite possibly a *different* worker than the one that parked it, quite possibly on a machine that didn't even exist yet when the park began — claims a fresh lease and resumes from the run's last checkpoint. Nothing about waking a park is special-cased machinery; it's the ordinary event pipeline, triggered by a human instead of a webhook.

**IMPORTANT BOUNDARY — Park ≠ a blocked thread, and Park ≠ a timeout.**
A blocked thread (in the OS sense you already understand) still occupies a stack, still exists as a schedulable entity the OS knows about, and dies with its process. A Park occupies *none* of that — it survives a full redeploy, a worker pool scaled to zero, the machine that created it being gone entirely. This is also **the specific misconception the cold open's team suffered from**: they treated "stuck" and "parked" as the same category, when a park is the system's *correct* behavior, indistinguishable from a genuine hang only because nobody's dashboard said which one it was.

---

## ONE CONCRETE TRACE — the book's own worked run, mentally executed once

This is the exact trace to run through your head, because every number in it is doing work:

```
RUN r-8f2 founded                                  state: CREATED

EPISODE 1 — worker w-3 claims the lease
  step 1  decision   route to planning        ~2 ms
  step 2  ACTIVITY   planner.plan()           1.4 s   $0.02
  step 3  ACTIVITY   tool.repo.search         0.3 s   $0.00
  step 4  ACTIVITY   model: propose a patch   38 s    $0.41
  step 5  decision   grader: patch applies?   ~4 ms
  step 6  ACTIVITY   tool.test.run_suite      52 s    $0.00
  step 7  decision   grader: 3 tests fail     ~4 ms
  step 8  decision   planner: replan -> NEW plan_id
  EXIT E2: step budget spent. Lease released. Worker w-3 now free.

EPISODE 2 — worker w-11 claims the lease (a DIFFERENT worker — normal)
  step 9  ACTIVITY   model: revise the patch  41 s    $0.44
  step 10 ACTIVITY   tool.test.run_suite      49 s    $0.00
  step 11 decision   grader: suite passes     ~4 ms
  step 12 decision   next step is EFFECTFUL -> requires a gate
  EXIT E3: park required. Approval written. Lease released.

PARK — state: PARKED, holding one row, for 6h 12m
  (survived two deploys and a worker pool scale-down to zero)
  resolved by <<approval.decided>>

EPISODE 3 — worker w-2 claims the lease
  step 13 ACTIVITY   tool.repo.push_branch    2.1 s   $0.00
  step 14 ACTIVITY   tool.repo.open_pr        1.8 s   $0.00
  step 15 decision   terminal                        state: SUCCEEDED

totals: 1 run . 3 episodes . 15 steps . 9 activities . 1 park
        worker time: 3 min 6 s          wall-clock: 6 h 19 min
        spend: $0.87
```

Three things this trace proves, not just illustrates:

1. **3 minutes of worker time across 6+ hours of wall clock** — almost all elapsed time was a park, and a park costs one row. This ratio *is* the architecture working as designed.
2. **Three different workers, none of which "owned" the run.** If any of them had died mid-episode, the sweeper would've expired the lease and the *next* relay wake would've re-driven from the last checkpoint — losing at most one step.
3. **$0.87 is a ceiling, not an estimate.** Because every activity is idempotent, replaying this run after a crash at any point would replay stored results rather than re-spending — so no matter how many times this run got interrupted, it could never have cost more than $0.87.

## ONE ANALOGY — and precisely where it breaks

**A legal case working through a court** (the book's own choice). The **case** is the Run — lasts two years, occupies nothing but a folder in a filing cabinet for nearly all of that time. A **hearing** is the Episode — a session in front of a judge, occupying a courtroom (scarce) for an afternoon; the case is adjourned between hearings, and a *different* judge may take the next one. A **ruling entered into the record** is the Step — minutes of work, durably recorded. **Expert testimony commissioned from an outside firm** is the Activity — costs real money, takes weeks, happens outside the court's control, nobody commissions the same report twice by accident. An **adjournment pending a witness's return** is the Park — can last six months, occupies no courtroom at all.

**Where it breaks:** in a real court, the case is *assigned* to a judge, who owns it throughout. Here, **no worker owns a run** — workers *borrow* it for one episode and hand it back. This is precisely the misconception that stalled the Chapter 3 code-review cold open for three days: if you carry over "someone is assigned to this for its duration," you will hold a lease across a park, and rediscover that exact argument from the losing side.

---

## FAILURE MODE

Straight from the chapter's own table, the ones worth carrying forward:

| Noun | Characteristic failure | Detected by |
|---|---|---|
| Run | Stranded — no worker, no lease, no terminal state | Lease-expiry sweep |
| Episode | Exits with zero progress, repeatedly | Steps-per-episode distribution with a mode at 1 |
| Step | Superseded mid-flight by a replan | Plan-identity mismatch at dispatch — discarded, not executed |
| Activity | Identity partial match (same run/position, different plan or inputs) | **Alerted, never merely logged** — it's silent by nature, so logging alone means nobody looks |
| Park | Mistaken for a stall | The cold open, exactly |

And the cold open's actual root cause, worth being precise about: it was **not** a runtime bug. It was a documentation/observability failure — the fix was a dashboard line reading `PARKED (awaiting approval, 2h03m, acme/billing-service, approver: j.chen)` instead of a bare `EXECUTING`, plus a team rule banning the word "stuck" from the incident channel.

---

## CONNECTION TO THE SYSTEM YOU'RE BUILDING TOWARD

```
RUN STATE (your diagram)  -> literally the `runs` row: id, state, plan_id,
                              current_step, version, lease_owner/until,
                              budget_cap/used
QUEUE / WORKER            -> where an EPISODE gets claimed (fast queue) and
                              where an ACTIVITY gets claimed (slow queue)
CONTROL (planner/gate/
  budget)                  -> what a decision STEP consults, in-process
DATA (model/tools/
  context)                  -> what an ACTIVITY step dispatches and awaits
ACTIVITY RESULT            -> the ACTIVITY noun's completed row
NEXT STATE / NEXT STEP     -> what a PARK resolves back into, via the
                              exact same event pipeline as everything else
```

The one box your original sketch didn't have a place for is **Park** — and that's the right gap to notice, because it's the one noun that holds *nothing*, so it doesn't show up as an active box in a pipeline diagram at all. It shows up as an absence: a run sitting quietly between "next state" and "next step," for however long a human takes.

---

**CHAPTER STATUS**
You should now be able to: replace "the agent is stuck" with a sentence naming which noun, in which state; explain why an Episode isn't queryable while a Run, Step, and Activity are; explain mechanically why `activity_id` being a content-hash is what makes replay-instead-of-respend possible with zero coordination; and state precisely why a Park costs nothing at the OS/process level, not just conceptually.

**KEY TERMS**
- **Run** — one goal under execution; a durable, versioned row; the only noun addressable from outside.
- **Episode** — one bounded working session over a run; not a row, a function invocation.
- **Step** — one advance of the state machine; a row; decision or activity-dispatching.
- **Activity** — one leased, budgeted, idempotent, cancellable call to a tool/model; identity is a content hash.
- **Park** — a durable pause holding zero resources; resolved by an event, not a timer expiring.
- **Custody gradient** — scarcity × duration held roughly constant across all five nouns.
- **Checkpoint** — the ~5ms transaction that saves progress, renews the lease, and reads signals, all at once.

**CONNECTION TO SYSTEM**
This is the exact vocabulary Chapter 4's diagram was missing — every box in that diagram now has a precise noun and a precise lifetime attached to it.

**NEXT**
Chapter 6 — State Separation: Run State, Domain State, and Model State. This takes Chapter 4's "deletion test" and makes it mechanically precise — and adds a third state category neither source names on its own.

Say "next" when you're ready.
