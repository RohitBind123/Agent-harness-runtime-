```
  Level 3 · Chapter 32
  DISTRIBUTED EXECUTION
  Requires   C17 The State Manager, C21 Durable Execution,
             C22 The Event Spine, C23 The Scheduler,
             C24 The Task Graph
  Unlocks    C33 Scalability, C34 Observability,
             C36 Reliability and SLOs
  Diagrams   Full (9)
```

# Chapter 32 — Distributed Execution

---

## 1. Motivation

### 1.1 Cold open

Run `r_51ab` is deploying `checkout-service` to staging. Worker A holds the run's lease, TTL thirty
seconds, renewed every ten.

At t=0 worker A calls `deploy_service`. The call takes about ninety seconds.

At t=4 the container A is running in comes under memory pressure. A full garbage collection begins
and the process stops. Every thread stops, including the one that renews the lease.

At t=30 the lease expires. At t=32 the sweeper returns the node to `pending`. At t=34 worker B
claims it, acquires a fresh lease, and calls `deploy_service`.

At t=44 worker A resumes. From inside A, four hundredths of a second have passed since it checked
its own clock. Its HTTP call is still in flight. Nothing has told it anything.

At t=71 A's deploy returns successfully and A writes its completion. The version compare-and-set
rejects the write — the row has moved on. A logs a lost-lease warning and exits cleanly. The
database is in a perfectly consistent state and every invariant holds.

At t=94 B's deploy returns.

Staging was deployed twice, from two different workers, forty seconds apart. The second deploy
landed mid-rollout of the first and left two replica sets fighting for the same port for eleven
minutes.

The lease worked. The compare-and-set worked. Both did precisely what they were built to do, which
was protect the database — and the database was never the thing at risk.

### 1.2 In plain language

Running one job on one machine is easy to reason about. Running thousands of jobs across dozens of
machines, where any machine can vanish at any moment, is the situation every real deployment is
actually in.

The core requirement sounds simple: at any given instant, exactly one worker should be driving any
given run. Two workers driving one run means work happening twice.

The usual tool is a lease — a claim with an expiry. A worker takes the lease, does some work, and
keeps renewing it. If the worker dies, the lease expires on its own and somebody else can pick the
work up. That is the right tool and there is no better one.

What it does not do is stop the first worker. A lease expiring is a fact recorded in a database. It
is not a hand reaching into the old worker and switching it off. A worker that was paused — by
garbage collection, by a hypervisor moving it, by a starved CPU — comes back a moment later
believing it still holds a lease that expired while it was not looking. It has no way to find out
except by trying to write, and by then whatever it was doing has already been done.

So there is always a window where two workers might both act. The design cannot remove it. What it
can do is make the window small, make writes inside it harmless, and make sure the things that reach
the outside world are protected by something other than the lease.

That last part is where most systems have a gap, and this chapter is mostly about it.

### 1.3 Why this chapter exists

Chapter 17 introduced the lease and the version compare-and-set and showed that ownership can be a
value rather than a lock. Chapter 21 introduced activity identity and said that a crash must lose at
most one in-flight step. Chapter 24 said two workers receiving the same ready set is fine because
the claim resolves it. Chapter 22 said the relay claims events rather than tracking a cursor.

Every one of those chapters was written as though there were one process, or as though the
multi-process case was a detail. This chapter is the reckoning: what those mechanisms actually
guarantee when there are forty workers, three availability zones, and clocks that disagree.

`[DAR §13]` requires "exactly one driver at any instant". That sentence is the most demanding in the
specification and it is routinely read as a design claim — assert the property, implement a lease,
done. It is not a design claim. **It is an operational property**, achieved by bounding a window and
making everything inside it safe, and a team that has not identified where its window is has not
achieved it. It has assumed it.

### 1.4 What previous framings got wrong

**"A lease is a distributed lock."** A lock is held until released. A lease is held until it expires,
and expiry is a fact in a database rather than an action taken against the holder. The difference is
invisible until a process pauses, and then it is the whole story.

**"Compare-and-set makes it safe."** It makes *state* safe. The cold open's compare-and-set worked
flawlessly and two deploys happened, because the deploy was not a state write. Every distributed
correctness argument that ends at CAS has proved a property about a database and said nothing about
the world.

**"Use synchronised clocks."** Clocks are not synchronised. They are approximately synchronised most
of the time, with an unknown bound, and every mechanism that relies on two machines agreeing about
"now" fails during the exact incidents — network partitions, VM migrations, NTP drift — when it is
most needed. §5.4 states what may be assumed.

**"The window is theoretical."** A ninety-second call and a thirty-second lease produces the cold
open on any afternoon with memory pressure. The window is the ordinary case for long tool calls, not
an exotic one.

**"Just make the lease longer."** Lengthening the lease shrinks the pause-then-resume window and
lengthens recovery — a genuinely dead worker's run is stuck for the full TTL. It moves the cost, it
does not remove it, and §5.5 gives the actual trade.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A lease is a hotel key card with a checkout time.

At 11:00 on your departure day, the card stops working. You cannot get back into the room. The next
guest's card works, the system is consistent, and nobody had to come and find you.

Now notice what the expiry did and did not do. It stopped you *entering*. It did nothing about you
being *inside*. A guest who is in the room at 11:00 is still in the room at 11:01, holding a card
that no longer works, entirely unaware that anything has changed. Nothing pushed them out. The
expiry was a fact recorded at the front desk.

That is a lease, exactly. Expiry controls acquisition, never presence. A worker holding an expired
lease is a guest in a room with a dead card, and it finds out only when it tries to use the card for
something — which, in the cold open, was at t=71, after the deploy.

The break is where hotels solve this and distributed systems cannot.

A hotel has **an observer with a physical view**. Housekeeping opens the door and sees somebody
there. The new guest walks in and finds the room occupied. There is a shared physical reality that
both parties are embedded in, and awkwardness resolves it within seconds.

Two workers have no shared reality at all. They cannot see each other, cannot signal each other, and
have no channel except the store. The store is the front desk, and the front desk only learns that
somebody is in the room when they walk past it. In the cold open both workers walked past it — at
t=71 and t=94 — and by then both had been in the room.

So the analogy gives the right intuition for what a lease is and withholds the mechanism that makes
the hotel version work. There is no observer. Everything in §5 is about living without one.

### 2.2 Why exactly-one-driver is operational, not structural

```
  (1) One run, many workers. Required for throughput, and required
      for availability -- a run must survive the machine it started
      on.

  (2) Two workers driving one run concurrently duplicates work and
      duplicates effects. So: exclusivity is needed.

  (3) A real lock is held until released. A crashed holder never
      releases, and the run is stuck forever. So the lock needs a
      timeout -- and a lock with a timeout is a lease.

  (4) The timeout is evaluated against a clock. WHOSE clock? Not
      the worker's: a paused worker's clock is paused with it, and
      two workers' clocks disagree by an unknown amount. So the
      store's clock, single-sourced (5.4).

  (5) But expiry is still not eviction. The store recording
      "expired" does not reach into the old worker. A worker
      mid-call does not know, cannot be told, and will not find
      out until it writes.

  (6) So there is a WINDOW in which two workers may both act. It
      cannot be removed. Only bounded.

  (7) Inside the window, STATE is safe: the second write loses the
      version compare-and-set and the loser exits cleanly. This is
      the part that always works, and it is the part everyone
      tests.

  (8) EFFECTS are not safe. A tool call that already reached the
      outside world is not undone by a failed CAS. The cold open
      is entirely contained in the gap between (7) and (8).

  (9) Therefore effects need a SECOND, independent mechanism:
      activity identity so a duplicate is recognised (C21), or a
      fence token so the downstream system rejects the stale
      caller (5.3).

 (10) And where neither is available -- a downstream with no
      idempotency that accepts no token -- the honest position is
      that the window is real, at-least-once is what you have, and
      the effect must be gated (C30) or accepted as such. There is
      no tenth step that closes it.
```

Step (10) is deliberately unsatisfying and it is the truthful ending. Chapter 21 §5.5 said the same
thing about the gap between an effect happening and its record landing: four mitigations, no
closure. This is the same gap seen from the other side, and it is the one place in the runtime where
the correct engineering answer is to bound a risk rather than eliminate one.

### 2.3 Two layers, and what each actually protects

| | **Version CAS** (C17) | **Activity identity** (C21) |
|---|---|---|
| Protects | Durable state | Effects on the outside world |
| Mechanism | The write loses if the row moved | The effect is recognised as already done |
| Fails when | Never, if applied to every write | The downstream cannot be asked "did this happen?" |
| Detects duplication | After the fact, on write | Before the call, on lookup |
| What the cold open had | Working perfectly | Absent |

The row that matters is the last. The cold open's system had one of these layers and it was the one
that protects the database. Every test passed. Every invariant held. The failure was entirely
outside the domain the mechanism covers, and the team's mental model — "we have leases and CAS,
therefore we have exactly-one-driver" — was a category error rather than a bug.

`[BP]` The test that finds this: pause a worker mid-effect for longer than the lease TTL, in
staging, deliberately. `SIGSTOP` the process, wait, `SIGCONT`. Almost nothing about the resulting
behaviour is predictable from reading the code, and every system should have run it once before it
matters.

### 2.4 The mental model to carry

A lease bounds a window of ambiguity; it does not close one. Inside the window, state is protected
by version compare-and-set and effects are protected by identity or by a fence token. Expiry is
evaluated by one clock — the store's — because no two machines agree about now. And "exactly one
driver at any instant" is a property you achieve by making the window small and its contents safe,
which means you must be able to say where your window is and how long it can be.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +-----------+   +-----------+   +-----------+   +-----------+
   | Worker 1  |   | Worker 2  |   | Worker 3  |   | Worker N  |
   |           |   |           |   |           |   |           |
   | loop(C18) |   | loop(C18) |   | loop(C18) |   | loop(C18) |
   +-----------+   +-----------+   +-----------+   +-----------+
        |               |               |               |
        |  (1) claim: lease + version CAS, ONE store clock
        +-------+-------+-------+-------+-------+-------+
                                |
                                v
   +--------------------------------------------------------------+
   |                       DURABLE STORE                          |
   |                                                              |
   |  [[ runs ]]      version, lease_holder, lease_expires_at,    |
   |                  fence_token (monotonic, per run)            |
   |  [[ plan_nodes ]]  status, claim, identity                   |
   |  [[ outbox ]]      partitioned by key                        |
   |  [[ activities ]]  identity -> outcome  (C21)                |
   |                                                              |
   |  THE ONLY shared observation. Workers cannot see each other. |
   +--------------------------------------------------------------+
        ^               ^                       ^
        |               |                       |
        | (2) sweeper   | (3) sharded relays    | (4) global
        |               |                       |     admission
   +----------+    +----------------------+  +---------------------+
   | Sweeper  |    |  Relay shard 0..M    |  |  Cross-process      |
   | (C27)    |    |  one claimer per     |  |  fairness (C23)     |
   |          |    |  partition           |  |  counters in the    |
   +----------+    +----------------------+  |  store, not in RAM  |
                                             +---------------------+
                                |
                                v
                        +==================+
                        |  External world  |
                        |                  |
                        |  protected by    |
                        |  identity (C21)  |
                        |  or a fence      |
                        |  token (5.3) --  |
                        |  NEVER by the    |
                        |  lease           |
                        +==================+

  Figure 32.1 -- One run, many workers, one store (D1 High-Level
                 Architecture)

  (1) claiming is the only coordination primitive; there is no
      worker-to-worker channel anywhere in this figure
  (2) the sweeper is the only component that may un-claim (C27 4.1)
  (3) partitioned so that one poisoned partition cannot stall the
      others (C22)
  (4) fairness counters MUST live in the store; per-process
      counters are wrong by a factor of N (5.6)
```

Three properties of this figure are the chapter.

**There is no worker-to-worker edge.** Not one. Every apparent interaction between workers is
mediated by the store, and the absence of that edge is what makes the system tolerate a worker
disappearing without any other worker noticing or caring.

**The external world hangs off the bottom, and the lease does not reach it.** The dashed protection
on that box is identity or a fence token. Drawing the lease as protecting it is the diagram version
of the cold open's mental model.

**The store's clock is the only clock in the picture.** Workers have clocks and they are used for
local timing — how long to sleep, when to attempt a renewal — and never for deciding whether a lease
is still valid.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                    DISTRIBUTION MACHINERY                      |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     Claim protocol       |  |     Renewal loop          |   |
   |  |                          |  |                           |   |
   |  |  UPDATE ... SET          |  |  renew at TTL/3           |   |
   |  |    lease_holder = me,    |  |                           |   |
   |  |    lease_expires_at =    |  |  renewal FAILURE is not a |   |
   |  |      now() + ttl,        |  |  warning: the worker must |   |
   |  |    version = version+1,  |  |  stop issuing effects     |   |
   |  |    fence = fence + 1     |  |  IMMEDIATELY (5.2)        |   |
   |  |  WHERE version = :seen   |  |                           |   |
   |  |    AND (holder IS NULL   |  |  runs on its own thread,  |   |
   |  |      OR expires < now()) |  |  which is exactly the     |   |
   |  |                          |  |  thread a GC pause stops  |   |
   |  |  now() is the STORE's    |  |                           |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     Fence issuer         |  |    Shard assignment       |   |
   |  |                          |  |                           |   |
   |  |  monotonic per run;      |  |  partition -> claimer     |   |
   |  |  every claim increments  |  |                           |   |
   |  |                          |  |  rebalance is the risky   |   |
   |  |  travels WITH the effect |  |  operation: two claimers  |   |
   |  |  to the downstream, if   |  |  on one partition is the  |   |
   |  |  the downstream will     |  |  cold open at relay scale |   |
   |  |  take it (5.3)           |  |  (5.5)                    |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 32.2 -- Inside the distribution machinery (D2 Low-Level
                 Architecture)
```

### 4.1 The claim statement, and every clause in it

```sql
UPDATE runs
   SET lease_holder     = :worker_id,
       lease_expires_at = now() + :ttl,
       version          = version + 1,
       fence_token      = fence_token + 1
 WHERE run_id  = :run_id
   AND version = :seen_version
   AND (lease_holder IS NULL OR lease_expires_at < now())
RETURNING version, fence_token;
```

Every clause is load-bearing, and the failure each one prevents is specific:

- `now()` is evaluated **by the database**, in both places. A worker computing its own expiry
  timestamp writes a number from a clock nobody else trusts, and a worker whose clock is ten seconds
  fast issues itself ten extra seconds of lease.
- `version = :seen_version` is the compare-and-set. It makes the claim safe against a concurrent
  claim: exactly one of two simultaneous attempts sees its expected version.
- `lease_expires_at < now()` is the expiry check, in the same statement as the claim, so there is no
  read-then-write gap in which the lease could be renewed by its holder.
- `fence_token + 1` is §5.3. It costs one integer column and it is the only thing in this statement
  that can protect anything outside the database.
- `RETURNING` gives the winner its version and fence in the same round trip. A subsequent `SELECT`
  to read them back is a second window.

`[BP]` The whole claim is one statement, and it must stay one statement. Every decomposition into
read-then-write reintroduces a gap, and each gap is small enough that it will not show up in testing
and large enough to fire under load.

### 4.2 Renewal failure is an emergency, not a warning

The renewal loop runs on its own thread and attempts a renewal at roughly one third of the TTL, so
two consecutive failures still leave time to react.

The part that is routinely got wrong is what happens when renewal *fails*. The common implementation
logs a warning and retries. That is exactly backwards. A failed renewal means one of two things: the
store is unreachable, or somebody else holds the lease. In the second case the worker is the cold
open's worker A, and every effect it issues from that moment is a duplicate.

`[BP]` On renewal failure the worker must immediately stop issuing effects, and it must do so
without waiting for the current one to return. Pure work may continue — it harms nothing — but the
tool execution engine should be switched into a refusing state on the spot. This is cheap to
implement and it converts a class of duplicates into a class of clean failures.

The uncomfortable truth underneath: in the cold open the renewal thread was not failing, it was
*stopped*. Nothing ran to notice anything. No amount of care in the renewal path helps when the
renewal path is not executing, which is why §5.3's fence token — carried by the effect itself, to
the far side — is the only mechanism in this chapter that works during a pause.

### 4.3 Named internals

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |  WORKER                                                      |
   |                                                              |
   |   +-------------------+      +---------------------------+   |
   |   |   Claim client    |----->|     Lease handle          |   |
   |   |   one statement   |      |  version | fence | expiry |   |
   |   +-------------------+      +---------------------------+   |
   |            |                          |                      |
   |            |                          | passed to EVERY      |
   |            v                          v write and effect     |
   |   +-------------------+      +---------------------------+   |
   |   |  Renewal thread   |      |  Tool execution engine    |   |
   |   |  every TTL/3      |      |  (C14 + C30 + C31)        |   |
   |   |                   |      |                           |   |
   |   |  on failure:      |----->|  refusing := true         |   |
   |   |  disarm effects   |      |                           |   |
   |   +-------------------+      |  attaches fence to any    |   |
   |                              |  effect that accepts one  |   |
   |                              +---------------------------+   |
   +--------------------------------------------------------------+

   INTERFACES

     claim   : (run_id, seen_version, ttl) -> LeaseHandle | None
     renew   : (LeaseHandle) -> LeaseHandle | LeaseLost
     write   : (LeaseHandle, mutation) -> Ok | VersionConflict
     effect  : (LeaseHandle, call) -> Outcome
               -- fence carried when the downstream accepts one
               -- identity checked when it does not (C21)
     release : (LeaseHandle) -> None      [cooperative only; the
                                           sweeper is authoritative]

  Figure 32.3 -- Named internals and their interfaces (D3 Component
                 Diagram)
```

Every operation takes the `LeaseHandle`. That is the enforcement technique this book has used
repeatedly — Chapter 26's `repair` without a goal, Chapter 28's `Judge` without a trajectory,
Chapter 31's broker without content — applied once more: a write or an effect that cannot be issued
without a handle cannot be issued by a worker that never had one, and the handle carries the version
and fence that make both checks possible without anybody remembering to pass them.

---

## 5. What Leases Guarantee, and What They Do Not

### 5.1 The window, drawn

```
                                                             TIME VIEW

   t=0    A claims. lease_expires_at = 30 (store clock). fence = 7.
   t=0    A calls deploy_service. Expected duration ~90 s.
   t=4    A's process STOPS. GC. Every thread, including renewal.

          |<------------------ THE WINDOW ------------------->|
          t=4                                              t=71

   t=30   lease expires. A is not running and cannot know.
   t=32   sweeper returns the node to pending.
   t=34   B claims. version bumped. fence = 8.
   t=34   B calls deploy_service.        <-- SECOND EFFECT, HERE
   t=44   A resumes. From inside A, 0.04 s have passed.
          A's HTTP call is still in flight. Nothing has told it.
   t=71   A's call returns. A attempts its write.
          version CAS FAILS. A logs and exits cleanly.
   t=94   B's call returns.

   WHAT WORKED                        WHAT DID NOT
   -----------                        ------------
   lease expiry                       nothing stopped A's effect
   sweeper                            fence 7 was never sent
   version CAS at t=71                deploy_service had no
   database consistency                 identity check
   every invariant                    two deploys reached staging

   The window is not the time between t=30 and t=34. It is the time
   between the moment A stops being able to know its lease is valid
   (t=4) and the moment A's effect finishes (t=71). Sixty-seven
   seconds, of which the system could observe none.

  Figure 32.4 -- The cold open, with the real window marked
                 (D4 Sequence)
```

The last paragraph is the correction most worth making. Teams measure the window as "expiry to
reclaim" — four seconds here — and conclude it is negligible. The actual window starts when the
worker stops being able to verify its own lease and ends when its in-flight effect completes. For a
ninety-second tool call and a thirty-second lease, it can be most of the call.

### 5.2 What the correct version looks like

Three changes, none of them large:

**One.** `deploy_service` is registered with an activity identity (Chapter 21). Before calling, the
engine looks up the identity in the `activities` table. At t=34, B's lookup finds A's in-flight
record and B does not call. B waits for A's outcome, or fails the step and lets the attempt cap
handle it.

**Two.** The renewal thread's failure disarms effects (§4.2). This does nothing in the cold open —
the thread was stopped, not failing — and it covers the much more common case where the store is
briefly unreachable and the worker is alive to notice.

**Three.** The fence token travels with the effect (§5.3), where the downstream will take one. This
is the only one of the three that works during a pause, and it is the one most often unavailable.

Note the ordering of value against the ordering of availability. The mechanism that works in the
hardest case is the one you are least likely to be able to use, which is why §2.2 step (10) exists.

### 5.3 Fence tokens, and the cooperation they require

A fence token is a monotonically increasing integer issued with every claim. The idea is simple and
strong: the effect carries the token to the downstream system, and the downstream **rejects any
request whose token is lower than the highest it has seen**.

In the cold open, A carries fence 7 and B carries fence 8. B's deploy arrives first at t=34 and the
deploy service records 8. A's request — which was issued at t=0 with fence 7 — is rejected on
arrival. The second deploy never happens, and it is rejected by the only party in the system that
was in a position to know: the one receiving both.

This is the correct answer. It is also, in practice, frequently unavailable, and the honest
accounting matters:

| Downstream | Fence token available? |
|---|---|
| Your own services | Yes — add a column and a check. Do this |
| A database you own | Yes — a conditional update on a token column |
| Object storage | Sometimes — conditional writes on an ETag or generation |
| A third-party API | Almost never. They have no concept of your lease |
| Sending an email | No. There is nothing to reject with |

`[BP]` Where a fence is available, use it, and prefer it to identity — it is the only mechanism that
functions when the caller is unaware it has lost its lease. Where it is not, fall back to identity
(Chapter 21), which requires the downstream to be queryable. Where neither is available, the
effect is at-least-once and must be treated as such: gate it (Chapter 30), make it tier 3 in
Chapter 27's taxonomy so it always gates, or accept duplicates and design the downstream to tolerate
them.

What must not happen is a system that has none of the three and believes it has exactly-once because
it has a lease.

### 5.4 Clock assumptions, stated precisely

Three statements, and every distributed mechanism in this handbook depends on getting them right.

**You may assume: a monotonic clock within one process.** `CLOCK_MONOTONIC` does not go backwards
and is unaffected by NTP adjustments. Use it for measuring durations locally — how long a call took,
when to attempt the next renewal.

**You may assume: bounded-but-unknown skew across processes.** Two machines' wall clocks differ. The
difference is usually small and is occasionally enormous, and you do not get told which. You may
never write code whose correctness depends on a bound you cannot observe.

**You may not assume: that two machines agree about now.** This rules out more than it appears to:

- A worker computing `lease_expires_at` from its own clock. Ruled out; §4.1 evaluates `now()` in the
  store.
- Comparing timestamps written by two different workers to order two events. Ruled out; use the
  event-log sequence number, which is why Chapter 25 §9 stores `observed_at_seq` alongside a
  human-readable timestamp.
- Deciding "this lease expired" anywhere except in the store's own statement. Ruled out for the
  reason the cold open demonstrates: a paused worker's clock is paused too, so it cannot even detect
  its own lateness.

`[BP]` The rule that follows and is worth stating as a standard: **every ordering and expiry
decision uses one clock or one sequence, never two.** Wall-clock timestamps are for humans reading
logs. The moment one appears in a comparison that affects behaviour, there is a bug waiting for a
clock to drift.

### 5.5 The TTL trade, and why longer is not safer

Lengthening the lease TTL is the first thing everyone proposes after an incident like the cold open,
and it is worth working out what it actually buys.

| Shorter TTL | Longer TTL |
|---|---|
| Faster recovery from a genuinely dead worker | Slower recovery: the run is stuck for the full TTL |
| More frequent renewal traffic | Less renewal traffic |
| **More** pause-then-resume events, because a shorter TTL is easier to exceed | **Fewer** such events |
| Each event's window is bounded by the in-flight effect, not by the TTL | Same |

The third row is the one that makes lengthening attractive and the fourth is the one that makes it
insufficient. A longer TTL makes the cold open rarer and does not make it smaller, because the
window's length is set by the duration of the in-flight effect (§5.1), not by the lease.

`[BP]` Set the TTL from the p99 duration of the slowest effectful tool plus a margin — the same rule
Chapter 27 §4.1 gave for the sweeper, arrived at from the other direction — and treat that as a
floor rather than a tuning knob. Then bound the window properly with §5.3 or identity, which is the
only thing that addresses the magnitude.

### 5.6 Two things that are silently wrong at N workers

Both are correct-looking single-process implementations that become wrong by exactly a factor of N,
and neither produces an error.

**Sharded relays.** Chapter 22's relay claims events rather than tracking a cursor, which was correct
and said nothing about running several relays. At scale the outbox is partitioned and one claimer
runs per partition. The dangerous operation is rebalancing: during a reassignment, two claimers can
believe they own the same partition, and that is the cold open at relay scale, with events being
delivered twice.

`[BP]` Rebalance through the store, with the same claim statement of §4.1 applied to partitions. A
partition is claimed with a lease and a fence exactly as a run is, and the assignment is never held
only in a coordinator's memory.

**Cross-process fairness.** Chapter 23's per-tenant admission control counts concurrent runs per
tenant. Implemented as a process-local counter — the obvious implementation, and the one that passes
every single-process test — a limit of ten per tenant becomes a limit of ten *per worker*, which is
four hundred across forty workers.

Nothing errors. The tenant gets forty times its share, and the symptom is Chapter 23's convoy
effect appearing at a load level the capacity model said was fine. `[BP]` Fairness counters live in
the store, incremented and checked in one statement, and the cost of that round trip is the price of
the property being true.

Both of these are the Level 3 pattern once more: a correct component, deployed in a configuration
its correctness argument did not cover, failing without a signal.

---

## 6. Runtime Sequence

### 6.1 The loop, distributed

```
                                                             TIME VIEW

   +----------------------------------------------------------+
   |  handle = claim(run_id, seen_version, ttl)               |
   |  if handle is None ............................... E0    |
   |  start renewal thread(handle, every ttl/3)               |
   +----------------------------------------------------------+
                          |
                          v
   +----------------------------------------------------------+
   |  LOOP                                                    |
   |                                                          |
   |    ready = resolver(run)                    (C24)        |
   |    if not ready ................................. E1     |
   |    if budget exhausted .......................... E2     |
   |    if cancel_requested .......................... E3     |
   |    if handle.lost ............................... E6     |
   |                                                          |
   |    node    = claim_node(handle, ready[0])                |
   |    outcome = engine.execute(handle, node)                |
   |              -- identity checked BEFORE the call (C21)   |
   |              -- fence carried WITH the call    (5.3)     |
   |              -- refuses entirely if handle.lost (4.2)    |
   |                                                          |
   |    if outcome is PARK ........................... E4     |
   |                                                          |
   |    ok = checkpoint(handle, outcome)         (C21)        |
   |    if not ok .................................... E6     |
   |    if stalled ................................... E5     |
   +----------------------------------------------------------+
                          |
                          v
   +----------------------------------------------------------+
   |  release(handle)   -- cooperative; the sweeper is the    |
   |                       authority (C27 sec 4.1)            |
   +----------------------------------------------------------+

   EXITS
     E0  another worker holds the lease      -> normal, not an error
     E1  graph complete or blocked on a join -> settle
     E2  budget exhausted, axis reported     -> fail  (C29)
     E3  cancellation requested              -> recovery (C27)
     E4  gate required, no decision          -> park  (C30)
     E5  no novel state in the window        -> escalate (C29)
     E6  LEASE LOST                          -> stop immediately,
                                                write nothing,
                                                issue no effects

   E6 is this chapter's addition, and it is reachable from two
   places: the renewal thread noticing, and a checkpoint losing its
   version compare-and-set. Both mean the same thing and both must
   take the same exit.

  Figure 32.5 -- The loop, with lease loss as an exit (D5 Runtime
                 Loop)
```

The loop has now accumulated seven exits across four chapters, and it still makes no decisions —
every exit is a condition evaluated elsewhere and returned to it. That was Chapter 18's design
intent and it has survived Levels 3 intact, which is the strongest available evidence that the
decision-free loop was the right shape.

---

## 7. State Management

```
                                                            STATE VIEW

   RUN OWNERSHIP  (as seen by the STORE, the only authority)

      {{ unowned }}
          |  claim succeeds: holder set, version+1, fence+1
          v
      {{ owned }} ---- renewed ----> {{ owned }}  (version+1 each)
          |
          +---- released cooperatively -----> {{ unowned }}
          |
          +---- lease_expires_at < now() ---> {{ expired }}
                                                   |
                                                   | sweeper
                                                   v
                                              {{ unowned }}

   WORKER'S BELIEF  (which is NOT the same machine)

      {{ believes_owned }}
          |
          +---- renewal succeeds ------> {{ believes_owned }}
          |
          +---- renewal fails ---------> {{ knows_lost }}
          |                               engine disarmed (4.2)
          |
          +---- process paused --------> {{ believes_owned }}
                                          ^^^^^^^^^^^^^^^^^^
                                          STILL. This is the cold
                                          open: the belief does not
                                          change, because nothing
                                          is running to change it.

      THE TWO MACHINES ARE NOT SYNCHRONISED, and no mechanism can
      synchronise them. The store may be in {{ expired }} while the
      worker is in {{ believes_owned }} for as long as the pause
      lasts. Every design in this chapter is an accommodation of
      that fact rather than an attempt to fix it.

      ILLEGAL: treating {{ believes_owned }} as evidence of
      {{ owned }}. A worker's belief about its lease is a cached
      value with no expiry it can enforce.

      ILLEGAL: {{ expired }} -> {{ owned }} for the SAME holder
      without a fresh claim. A worker returning from a pause does
      not resume its lease; it must re-claim, and re-claiming
      increments the fence, which is what makes its old in-flight
      effect identifiable as stale.

  Figure 32.6 -- Two state machines that cannot be synchronised
                 (D6 State Diagram)
```

### 7.1 The two machines are the chapter

Most state diagrams in this book show one machine. This one shows two, side by side, precisely
because the gap between them is the subject.

The store's view is authoritative and complete. The worker's view is a cache with no invalidation
signal available during exactly the failure it needs to detect. Every mechanism in §5 — fence
tokens, identity checks, renewal disarming, one-clock evaluation — exists to make the system behave
correctly while those two views disagree, rather than to make them agree.

`[BP]` Name this in code. A field called `believes_lease_held` reads awkwardly and is honest, and it
stops the next engineer from writing `if lease_held:` before an effect as though it were a fact.

### 7.2 Fence tokens are per run and monotonic forever

The fence never resets, not on release, not on completion, not on a new plan. It is a monotonic
counter over the lifetime of the run, and its only job is that a later claim always produces a higher
number than any earlier one.

`[BP]` Store it as a bigint and never reuse a run id. A wrapped or reused fence is the one failure
that turns the mechanism from a protection into a false one, and both are avoidable by construction
at a cost of zero.

---

## 8. Internal APIs

```python
from typing import Protocol
from dataclasses import dataclass


@dataclass(frozen=True)
class LeaseHandle:
    run_id: str
    worker_id: str
    version: int
    fence: int              # monotonic per run, never reset (7.2)
    believes_held_until: str    # named to discourage trusting it (7.1)


class LeaseStore(Protocol):

    def claim(self, run_id: str, seen_version: int, ttl_s: int) -> LeaseHandle | None:
        """One statement. Expiry evaluated by the STORE's clock, in
        the same statement as the write, so no read-then-write gap
        exists (4.1).

        Returns None when another worker holds it. That is a normal
        outcome and not an error -- C24's overlapping ready sets are
        resolved here, by design.
        """

    def renew(self, handle: LeaseHandle) -> "LeaseHandle | LeaseLost":
        """On LeaseLost the caller MUST disarm effects immediately,
        without waiting for the in-flight call to return (4.2).

        This cannot help during a process pause, because nothing is
        running to call it. It covers the more common case of a
        briefly unreachable store, where the worker is alive.
        """


class EffectGateway(Protocol):

    def execute(self, handle: LeaseHandle, call: "ToolCall") -> "Outcome":
        """Requires the handle. Three protections, in order of how
        well they work and inverse order of how often they are
        available:

          1. fence carried to the downstream, which rejects a stale
             token. The ONLY mechanism that works during a pause,
             and the least often available (5.3).
          2. activity identity looked up before the call (C21).
             Requires a queryable downstream.
          3. neither: the effect is at-least-once. Say so. Gate it,
             or make the downstream tolerate duplicates.

        A system with none of the three and a lease does not have
        exactly-once. It has a lease.
        """
```

`LeaseHandle.believes_held_until` is named that way on purpose (§7.1). A field called
`held_until` invites `if now() < handle.held_until:`, which is a worker consulting its own clock
about a fact only the store knows — the exact mistake §5.4 rules out. Names are cheap enforcement
and they work on the code that has not been written yet.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RunOwnershipRow:
    run_id: str
    version: int                  # bumped by every claim and write
    lease_holder: str | None
    lease_expires_at: str         # written by the STORE's now()
    fence_token: int              # monotonic, bigint, never reset


@dataclass(frozen=True)
class PartitionAssignment:
    """Relay shards are claimed exactly as runs are (5.6)."""
    partition: int
    claimer: str | None
    lease_expires_at: str
    fence_token: int


@dataclass(frozen=True)
class TenantConcurrency:
    """Lives in the STORE. A process-local counter makes a limit of
    ten per tenant into ten per worker (5.6)."""
    tenant_id: str
    active_runs: int
    limit: int
```

Three schema-level statements of arguments made above.

`lease_expires_at` is written by the store and never by the application. `[BP]` Enforce it with a
trigger or a check that rejects a client-supplied value, because the application-supplied version is
one careless refactor away and produces no symptom until a clock drifts.

`fence_token` is a bigint on the same row as the version, incremented by the same statement. Keeping
them together means a claim cannot bump one without the other.

`TenantConcurrency` being its own table rather than a field is what makes §5.6's fix visible in the
schema. A reviewer who sees a concurrency counter in a table asks the right question; one who sees a
Python dictionary does not.

---

## 10. Communication

```
                                                            LAYER VIEW

   WHAT ACTUALLY MOVES BETWEEN MACHINES

   worker ====> store         claim / renew / checkpoint
                              ~200 bytes per operation,
                              a few per second per active run

   worker ====> model         assembled context, C11's rates
                              ~100-300 KB per step
                              THE LARGEST FLOW IN THE SYSTEM

   worker ====> downstream    the effect, plus the fence if it is
                              accepted (5.3)

   worker <==== store         ready sets, lease handles, identity
                              lookups

   worker  X    worker        NOTHING. There is no edge here, at
                              any volume, in any direction.

   The absence of the last row is the design. Every apparent
   interaction between workers is a pair of interactions with the
   store, which is why a worker can vanish without any other worker
   needing to be told.

  Figure 32.7 -- What moves between machines (D7 Data Flow)
```

```
                                                             TIME VIEW

   WHO MAY STOP A RUN FROM PROCEEDING

   +--------------+
   |    Store     |---- refuses a claim ------> another holder
   +--------------+
   +--------------+
   |    Store     |---- refuses a write ------> version conflict
   +--------------+
   +--------------+
   |   Renewal    |---- disarms effects ------> lease lost (4.2)
   +--------------+
   +--------------+
   |  Downstream  |---- rejects a request ----> stale fence (5.3)
   +--------------+
   +--------------+
   |   Sweeper    |---- un-claims -----------> lease expired
   +--------------+

   NOT ON THIS LIST, and this is the point:

   +--------------+
   |   Worker A   |  X   cannot be stopped by anything above
   +--------------+      while it is paused. Every mechanism here
                         acts at a MOMENT OF CONTACT -- a claim, a
                         write, a request arriving. A process that
                         is not running makes no contact and is
                         therefore unreachable by all of them
                         except the last: the downstream, which
                         sees the request whenever it arrives.

  Figure 32.8 -- Who may stop what, and who cannot be stopped
                 (D8 Control Flow)
```

```
                                                             TIME VIEW

   claim    ....>  << run.claimed >>        holder, version, fence
   renew    ....>  (no event; too frequent, and nothing consumes it)
   loss     ....>  << lease.lost >>         holder, at which point
                                            it noticed
   sweep    ....>  << lease.expired >>      emitted by the SWEEPER,
                                            not by the late worker
   fence    ....>  << fence.rejected >>     emitted by the DOWNSTREAM
                                            when it can; the single
                                            highest-value event in
                                            this chapter, because it
                                            is direct evidence a
                                            duplicate was prevented
   conflict ....>  << version.conflict >>   a losing write; normal at
                                            low rates, a signal at
                                            high ones

   THE ONE TO ALERT ON: << fence.rejected >>. Every occurrence is a
   duplicate effect that did not happen. A rate of zero over a long
   window usually means the fence is not being carried, not that
   the situation never arises.

  Figure 32.9 -- What distribution makes durable (D9 Event Flow)
```

The note under Figure 32.9 is Chapter 31 §13.1's observation reappearing: some controls announce
themselves by firing, and a control that never fires is more often unwired than unneeded. `[BP]`
Verify the fence path deliberately in staging rather than inferring its health from silence.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Paused worker resumes and completes an effect | `fence.rejected` downstream, if a fence is carried | Fence token (§5.3); identity (C21) where no fence is possible; otherwise at-least-once, stated |
| Worker computes its own lease expiry | Code review; clock-skew incidents | `now()` evaluated in the store, in the claim statement (§4.1) |
| Claim decomposed into read-then-write | Duplicate claims under load | One statement, always (§4.1) |
| Renewal failure logged and retried | Duplicate effects after brief store outages | Renewal failure disarms effects immediately (§4.2) |
| Two claimers on one relay partition after a rebalance | Duplicate event delivery | Claim partitions through the store with lease and fence (§5.6) |
| Per-tenant limits enforced per process | Tenant using N times its share; convoy at unexpected load | Counters in the store (§5.6) |
| Ordering two events by wall-clock timestamps | Ordering anomalies during clock drift | Use the event-log sequence, never two clocks (§5.4) |
| Fence reset or run id reused | Silent: a stale request accepted as fresh | Bigint, monotonic forever, ids never reused (§7.2) |
| Lease TTL raised after an incident | The incident recurs, more rarely | TTL sets frequency, not window size (§5.5) |
| A system with a lease and nothing else | Nothing, until a pause | Name the layer that protects effects, or say at-least-once |

The last row is the honest summary of the chapter. A lease with no second layer is not a bug in the
usual sense — the code is correct and does what it says. The defect is in the belief about what has
been achieved, and beliefs are not caught by tests.

---

## 12. Scalability

**The store is the coordination point and therefore the bottleneck.** Every claim, renewal, and
checkpoint is a round trip. `[BP]` Budget them: at forty workers with a thirty-second TTL renewing
at ten seconds, renewals alone are four operations per second — trivial. Checkpoints scale with step
rate and are the real load, which is why Chapter 29 §12's cadence question matters more at scale
than in a single process.

**Renewal traffic is negligible and is often optimised prematurely.** The temptation is to batch
renewals across runs, which couples them: one slow batch delays every lease in it, and a delayed
renewal is §4.2's emergency. `[BP]` Do not batch renewals.

**Ready-set polling is the load that grows quadratically** if every worker polls every run.
Chapter 24 §12 gave the fix — the scheduler hands a worker a run, and the worker resolves only that
run's graph — and at N workers it stops being an optimisation and becomes a requirement.

**Sharding the outbox is required past a few thousand events per second**, and §5.6's rebalance
hazard is the cost. `[BP]` Choose a partition count well above the expected claimer count and change
it rarely; repartitioning is the operation during which the guarantee is weakest.

**Cross-zone latency is a real term in the lease TTL.** A store in another availability zone adds
single-digit milliseconds per operation, which is nothing for a claim and material for a renewal
under load. `[BP]` Keep the store's write path in one zone and accept the availability trade
explicitly, rather than discovering it as latency variance.

---

## 13. Production Engineering

### 13.1 The five numbers

- **`fence.rejected` count.** Direct evidence of duplicate effects prevented. Alert if it is zero
  over a long window, because that usually means the fence is not carried.
- **`version.conflict` rate.** Losing writes are normal at low rates — that is overlapping ready
  sets working. A rising rate means claims are contending, usually because the scheduler is handing
  the same run to several workers.
- **Time from lease expiry to reclaim.** The recovery half of §5.5's trade. It should be close to
  the sweeper's period.
- **Renewal latency, p99.** A rising p99 is the leading indicator for §4.2's emergency, and it
  usually moves before any duplicate appears.
- **Longest in-flight effect duration versus lease TTL.** The window (§5.1). If the first exceeds
  the second, the system produces the cold open on any bad afternoon, and this ratio is the one
  number that says so in advance.

The last one deserves emphasis because it is computable today, from data every system already has,
and almost nobody computes it. It converts "could this happen to us" from a discussion into a query.

### 13.2 The review question

For any effect the runtime can perform: **if two workers issued this simultaneously, what stops the
second one — and is it the lease?**

If the answer is the lease, the answer is wrong. The acceptable answers are a fence token, an
identity check, or an explicit acceptance that the effect is at-least-once with a gate or a
duplicate-tolerant downstream behind it.

### 13.3 Teaching this to a new engineer

Walk them through the cold open and ask what was broken. The list they produce is usually: the
lease, the CAS, the sweeper. Then tell them all three worked exactly as designed and watch the
question change from *what is broken* to *what was never covered*.

Then give them the `SIGSTOP` exercise from §2.3 on a staging system. Nothing in this chapter is
believed properly until someone has watched a paused worker wake up and cheerfully finish a job
somebody else already did.

---

## 14. Relation to AHE

`[AHE]` Trials run in isolated sandboxes and are scored independently, which makes them the
easy case for distribution: no shared mutable state, no cross-trial ordering, and — by Chapter 27
§5.4's constraint — no effects outside the sandbox at all. Fan a thousand of them across a fleet and
none of this chapter's difficulty appears.

`[INF]` The difficulty appears in the evolution loop's own state. The harness workspace, the trial
ledger, and the score record are shared mutable state, and two evolution drivers running
concurrently against one workspace is the cold open with a repository instead of a deploy. `[BP]`
The same claim protocol applies: the evolution driver holds a lease on the workspace with a fence,
and every commit carries it.

`[INF]` There is a sharper version of the containment argument here than Chapter 20 §5.5 has stated
so far. An evolution loop rewarded on throughput will find that raising concurrency raises the score,
and raising concurrency is exactly what §5.6's two silent failures punish. A loop that widens a
per-tenant limit or reduces a lease TTL improves its measured numbers and degrades a correctness
property that no benchmark measures. Concurrency parameters belong outside the workspace for the
same reason temporal parameters do (Chapter 29 §14), and the argument is the same one: no
outcome-based reward can tell a well-tuned value from an unsafe one.

---

## 15. Industry Perspective

**`[DAR §13]`** Exactly one driver at any instant is specified, and this chapter's contribution is
insisting on the word *operational*. It is achieved by bounding a window, not by asserting a
property, and a team that cannot say where its window is and how long it can be has not achieved it.

**`[BP]` Fencing tokens are well established and under-deployed.** The technique is decades old,
well documented in the distributed systems literature, and rarely present in application code — not
because it is difficult, but because it requires the downstream to cooperate, and downstream systems
are usually somebody else's. Where you own both sides, adding it is a column and a comparison.

**`[BP]` The lease-is-not-a-lock lesson has been learned repeatedly and independently.** Chubby's
sequencers, ZooKeeper's `zxid`, and every mature lock service ships something fence-shaped, because
each of them discovered that expiry does not evict. A system reaching for a lease without a fence is
re-walking a path with well-marked exits.

**`[BP]` Clock assumptions are the most reliably underestimated risk in distributed systems.**
Spanner spends real money on hardware to make bounded skew a *guarantee* rather than a hope, which
is the strongest available evidence about how hard the problem is when you do not. §5.4's rule —
one clock or one sequence, never two — is what remains available to everyone else.

**`[INF]` Most agent runtimes today run one driver per run in a single process and are correct by
construction.** That is a fine place to be and it is worth knowing it is where you are. The failure
arrives on the day a second replica is added for availability, and it arrives as a duplicate effect
rather than as an error, which makes the deployment change and the incident hard to connect.

**`[FUT]` Duplicate-effect detection after the fact is unexplored and looks tractable.** Chapter 27's
effect ledger records every applied effect with an identity; two rows with the same identity and
different attempts is a query, and running it continuously would turn the cold open from an
eleven-minute outage into an alert at t=94. Nobody appears to be doing it, and the data is already
there.

---

## 16. Key Takeaways

1. **A lease bounds a window; it does not close one.** Expiry controls acquisition, never presence.
   A paused worker holds a dead key card and cannot be told.
2. **The window is longer than it looks.** It runs from the moment a worker stops being able to
   verify its lease to the moment its in-flight effect completes — not from expiry to reclaim. For a
   ninety-second call, that is most of the call.
3. **Compare-and-set protects state; nothing about it protects effects.** The cold open's CAS worked
   perfectly and two deploys happened. Every correctness argument that ends at CAS has proved
   something about a database and nothing about the world.
4. **Effects need a second, independent layer**: a fence token the downstream rejects, or an identity
   check before the call. The fence is the only mechanism that works during a pause and the least
   often available — which is why the honest fallback must be stated rather than assumed away.
5. **One clock or one sequence, never two.** Expiry is evaluated by the store, ordering by the event
   log. Wall-clock timestamps from two machines are for humans reading logs.
6. **A longer TTL changes the frequency, not the size.** The window is set by the effect's duration.
   Set the TTL from the slowest tool's p99 and bound the window with a fence.
7. **Correct components fail silently in configurations their correctness argument did not cover.**
   A per-process fairness counter and a rebalancing relay are both right at N=1 and wrong by a factor
   of N, with no error either time.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Lease** | A claim with a store-evaluated expiry, which controls acquisition and never evicts an existing holder. | `[DAR]` | Ch 33, Ch 36 |
| **Window of ambiguity** | The interval from a worker losing the ability to verify its lease to its in-flight effect completing, during which two workers may both act. | `[INF]` | Ch 36 |
| **Fence token** | A monotonic per-run integer carried with an effect so the downstream can reject a stale caller — the only protection that works during a process pause. | `[BP]` | Ch 36, Ch 43 |
| **Exactly one driver** | An operational property achieved by bounding the window and protecting its contents, never a design claim that a lease establishes. | `[DAR]` | Ch 36 |
| **Store-evaluated expiry** | Deciding lease validity with the store's clock inside the claim statement, because a paused worker's clock is paused with it. | `[DAR]` | Ch 34 |
| **Renewal disarming** | Switching the effect path into a refusing state the instant a renewal fails, rather than logging and retrying. | `[BP]` | Ch 36 |
| **Sharded relay** | Partitioned outbox delivery with one claimer per partition, where rebalancing is the operation during which the guarantee is weakest. | `[INF]` | Ch 33 |
| **Cross-process fairness** | Concurrency limits held in the store rather than per process, because a process-local counter multiplies every limit by the worker count. | `[INF]` | Ch 33, Ch 37 |
| **Clock discipline** | Using one clock or one sequence for any decision, with monotonic clocks for local durations and wall clocks for humans only. | `[BP]` | Ch 34 |
| **Belief versus ownership** | The unsynchronisable gap between what a worker thinks it holds and what the store records, which every mechanism here accommodates rather than fixes. | `[INF]` | Ch 36 |

---

**Level 3 is complete.** You can make a run survive a crash, deliver its events exactly once,
schedule it fairly, express its work as a graph, hold beliefs about its environment and know when
they went stale, plan and repair, recover from partial failure, grade the result without being
fooled by it, run it for six hours and know whether it is moving, put a human in genuine control of
it, bound what a compromised step can reach, and spread all of it across a fleet while being honest
about what that costs.

One property has recurred in every chapter of this level without being planned: **each of these
failures produces no error signal.** A poisoned relay stalls silently. A convoy makes everyone wait
at full throughput. A join that never fires leaves every dashboard green. A stale belief produces a
confident wrong edit. A replan storm looks like diligence. An unpaired migration reports a clean
rollback. A skipped test is a passing suite. A stalled run counts steps. A duplicate deploy passes
every consistency check. Level 2's failures were mostly wrong answers; Level 3's are correct systems
doing exactly what they were told.

**Next:** Chapter 33 — *Scalability and Capacity Planning*, opening Level 4. Everything from here is
about operating what you have built: sizing it from measured service times rather than from guesses,
seeing inside it, paying for it, promising something about it, and — by Chapter 41 — being able to
tell whether a change to it made anything better.
