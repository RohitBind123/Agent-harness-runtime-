```
  Level 3 · Chapter 22
  THE EVENT SPINE: OUTBOX, RELAY, COMMAND PORT
  Requires   C4 The Complete Runtime, C9 Three Flows,
             C17 The State Manager, C21 Durable Execution
  Unlocks    C24 The Task Graph, C27 Failure and Recovery,
             C30 Human Authority, C32 Distributed Execution,
             C34 Observability
  Diagrams   Full (9)
```

# Chapter 22 — The Event Spine: Outbox, Relay, Command Port

---

## 1. Motivation

### 1.1 Cold open

09:12. Nothing is wrong. No errors, no alerts, no elevated latency. Every dashboard is green.

09:12 is also when Atlas stopped doing anything at all.

Runs are being accepted. Rows are appearing in `runs`. Approvals are being granted, and the approvals
table shows them arriving. What is not happening is any of the work that those things should have
caused: no run is being claimed, no parked run is waking, no approval is resolving a gate.

The consumer tracks a cursor — the id of the last event it processed. At 09:12 it reached an event
whose handler raised on a field that had been null since a migration three weeks earlier. The
consumer caught the exception, logged it, and did not advance the cursor, because advancing past an
unprocessed event would lose it.

That is the correct instinct and it produced a total outage. One malformed row, and every event
behind it — thousands, across every tenant — is stuck behind a consumer politely retrying the same
failure forever.

Forty minutes to find, because the symptom of a stalled event stream is *nothing happening*, and no
monitoring system alerts on the absence of things.

### 1.2 In plain language

The event spine is how one thing that happened reliably causes the next thing to happen.

That sounds trivial and it is the hardest guarantee in the system, because two things have to be true
at once. If a run's state changes, the notification must not be lost. And if the notification is
sent, the change must really have happened. Getting one without the other gives you either work that
silently never happens, or work that happens for changes that were rolled back.

The trick is not to send a notification at all. Instead, the change and a record saying "this
happened" are written to the same database in the same transaction — so either both land or neither
does. A separate process then reads those records and turns them into work.

The rest of the chapter is about that separate process, and mostly about one decision. It can track
its position in the stream with a bookmark, or it can pick up individual records and mark each one as
taken. The bookmark is the obvious design and it is the cold open: one record it cannot handle, and
everything behind it stops.

There is also a direction question. Events travel *upward* — something happened, past tense. Commands
travel *downward* — please do this, imperative. Keeping them distinct is what stops the runtime and
your product growing into each other.

### 1.3 Why this chapter exists

Chapter 9 named the event axis and gave one rule: a state change and the event announcing it share a
transaction. Chapter 4 drew a narrow waist with commands going down and events coming up. Chapter 21
depended on the outbox to close half of its record window.

This chapter builds all of it, and it is Stage 0 of the architecture roadmap — the first thing to
construct, before there is a run to drive.

`[INF]` It is also the chapter with the highest ratio of consequence to apparent difficulty. The
mechanism is three tables and a worker. The failure modes are outages that present as silence, and
the design decision that separates a good spine from the cold open's is a single choice about how the
reader tracks its position.

### 1.4 What previous framings got wrong

**"Use a message queue."** A queue moves messages between processes and cannot make a message and a
database write atomic. `[DAR §7.1]` The outbox exists because that atomicity is the requirement, and
the queue is what the relay writes *to* afterwards — downstream of the durability boundary, not
instead of it.

**"Track a cursor; that is how streams work."** The cold open. Cursors are correct where every record
is processable and a stall is visible. Here a single poison row halts everything, and §5.3 explains
why claims cost almost nothing more.

**"Events and commands are both just messages."** They differ in direction, tense, addressing, and
failure semantics (§5.5). Collapsing them is how the runtime ends up knowing what a repository is,
which Chapter 4's deletion test then fails.

**"Publish the event after the commit."** `[INF]` The most common version of the mistake, and it looks
safer than it is: the commit succeeds, the process dies before publishing, and the change exists with
nothing having been told. Chapter 9 §5.2's rule is *the same transaction*, not *after it*.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A hospital ward's handover book, versus shouting down the corridor.

Shouting is a message queue without an outbox. The nurse finishing a shift calls out that bed 7 needs
observations at midnight. If the person they meant is out of earshot, or steps away mid-sentence, the
instruction evaporates — and nothing anywhere records that it was ever given.

The handover book is the outbox. The nurse writes it down in the same act as updating the patient's
chart: one pen, one moment, both entries or neither. The book is not a communication channel; it is
the durable record from which communication is *derived*. Somebody comes along afterwards and works
through it.

Now the design decision, and this is the cold open. That somebody can work through the book two ways.
They can keep a bookmark and read strictly in order — and if entry 41 is illegible, they stop at 41
and the whole book stalls, including the forty entries after it that are perfectly clear. Or they can
tick each entry as they take it, in whatever order they can act on, leaving the illegible one for
somebody who can read the handwriting.

Bookmark or ticks. That is cursor or claim, and it is most of §5.3.

**Where the analogy breaks.** A ward has a charge nurse who will notice within the hour that nothing
on the book has been ticked. There is ambient supervision: people walk past, patients ring bells, a
doctor asks why observations were not done.

`[INF]` The spine has none of that. A stalled relay produces no errors, no failed requests, and no
elevated anything — the symptom is that things stop happening, and monitoring is almost universally
built to alert on events rather than on their absence. Forty minutes in the cold open is fast. The
mitigation is §13.1's first row and it has to be built deliberately, because nothing about the system
will volunteer the information.

### 2.2 Why the outbox, derived

```
  1. A step changes run state AND something else must learn about it.
  2. Two writes to two systems cannot be made atomic without a
     distributed transaction, which Ch 2 ruled out.
  3. So one can succeed while the other fails, in either order:
       commit then publish -> the process dies; nobody is told
       publish then commit -> the commit fails; a lie was published
  4. Both are unacceptable, and no ordering of two systems fixes it.
  5. So the notification must go to the SAME system as the state
     change, in the SAME transaction. Then they land together or
     not at all.
  6. That makes the notification a row in a table -- the outbox.
  7. But a row does nothing. Something must read those rows and turn
     them into work.
  8. That reader is the relay, and steps 6 and 7 together are the
     entire durability story of this architecture.
```

Step 4 is the one worth dwelling on. `[INF]` Teams reach step 3, notice both orderings are broken,
and conclude the problem needs a stronger primitive — two-phase commit, a transactional broker, a
distributed lock. It does not. It needs the observation that if both writes go to one system the
problem disappears, and that observation costs a table.

### 2.3 Commands down, events up

`[DAR §7.1]` Two message kinds, and the differences are not stylistic:

| | Command | Event |
|---|---|---|
| Direction | down, into a domain | up, out of one |
| Tense | imperative: `cmd.repo.apply_patch` | past: `repo.patch.applied` |
| Addressed to | one specific handler | nobody in particular |
| Recipient may refuse | yes | no — it already happened |
| Delivery need | exactly-once *effect*, via idempotency key | at-least-once, deduped by the consumer |
| If nobody handles it | an error | fine; nobody was listening |
| Carries | intent | fact |

`[INF]` The naming convention (Appendix B) exists to keep these visible in logs and traces, and
the test for whether you have them right is the refusal row: if your "event" can be rejected by its
recipient, it is a command that was named wrongly, and something upstream is about to depend on a
response that events do not have.

### 2.4 The mental model to carry

> **The outbox is not a messaging feature. It is the only durability primitive this architecture
> requires, and everything else that survives a crash survives because of it.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  EDGE / KERNEL / DOMAIN -- anything that changes state        |
  |                                                              |
  |     state change  +  << event >>   in ONE transaction  (1)   |
  +---------------------------+----------------------------------+
                              v
                       [[ outbox ]]        (2) the durability
                              |                boundary
                              | (3) CLAIM, never a cursor
                              v
                    +=========+=========+
                    |  RELAY            |
                    |   claim . dispatch|
                    |   . ack . retry   |
                    +==+======+======+==+
                       |(4)   |(5)   |(6)
          +------------+      |      +-------------+
          v                   v                    v
    (( run queue ))    +======+======+      +~~~~~~~~~~~~~~+
    Ch 8, Ch 18        | COMMAND     |      | external     |
                       | PORT        |      | subscribers  |
                       +======+======+      +~~~~~~~~~~~~~~+
                              | (7) cmd.<domain>.<verb>
                              v
                    +~~~~~~~~~~~~~~~~~~~~+
                    | YOUR DOMAIN         |
                    |  applies, then      |
                    |  emits its OWN      | (8)
                    |  event, same txn ---+---> [[ outbox ]]
                    +~~~~~~~~~~~~~~~~~~~~+

  Figure 22.1 -- The spine (D1 High-Level Architecture)

  (1) Ch 9 section 5.2's rule; everything else depends on it
  (2) one table; the only durability primitive required
  (3) section 5.3 -- the cold open is this arrow as a cursor
  (4) most events become work: a run to claim, a park to wake
  (5) some become commands into a domain (Ch 4's waist)
  (6) some go outward, to subscribers the runtime knows nothing of
  (7) imperative, idempotency-keyed, refusable
  (8) the domain's own event closes the loop -- and this is what
      closes Ch 21's record window for domain effects
```

`[INF]` Wire 8 is the one that makes Chapter 21 §5.5's first mitigation work. The domain applies the
patch and emits `repo.patch.applied` in the same transaction as the change, so even if the runtime's
worker dies before recording the activity result, the *fact* survives and the relay delivers it. The
run learns what happened from the event rather than from its own bookkeeping.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  THE OUTBOX -- one table, and the shape matters

  +--------------------------------------------------------------+
  | id            bigserial PRIMARY KEY                           |
  | event_type    text        'run.step.completed'                |
  | partition_key text        ORDERING is preserved WITHIN this   |
  | payload       jsonb                                           |
  | created_at    timestamptz                                     |
  |                                                              |
  | claimed_by    text        NULL until a relay takes it         |
  | claimed_until timestamptz a LEASE, exactly as Ch 17          |
  | attempts      int                                             |
  | processed_at  timestamptz NULL until done                     |
  | dead_at       timestamptz NULL unless poisoned                |
  +--------------------------------------------------------------+

  CREATE INDEX ON outbox (id)
    WHERE processed_at IS NULL AND dead_at IS NULL;

  THE RELAY LOOP

  +--------------------------------------------------------------+
  |  1. CLAIM a batch -- not a cursor read                        |
  |       UPDATE outbox SET claimed_by = :me,                     |
  |              claimed_until = now() + :lease                   |
  |        WHERE id IN (                                          |
  |          SELECT id FROM outbox                                |
  |           WHERE processed_at IS NULL AND dead_at IS NULL      |
  |             AND (claimed_until IS NULL                        |
  |                  OR claimed_until < now())                    |
  |           ORDER BY id                                          |
  |           LIMIT :batch                                         |
  |           FOR UPDATE SKIP LOCKED    <-- no relay blocks another|
  |        ) RETURNING *;                                          |
  |                                                              |
  |  2. GROUP by partition_key; ordering holds within a key only  |
  |                                                              |
  |  3. DISPATCH each -- enqueue, command, or publish             |
  |                                                              |
  |  4. ACK    processed_at = now(), per row                       |
  |                                                              |
  |  5. FAIL   attempts + 1, release the claim, back off.          |
  |            attempts > cap -> dead_at = now()                   |
  |            THE BATCH CONTINUES. One bad row is one bad row.    |
  +--------------------------------------------------------------+

  Figure 22.2 -- Outbox and relay (D2 Low-Level Architecture)
```

### 4.1 Step 5 is the whole chapter

`[INF]` Everything else here is conventional. The line that separates this design from the cold
open's is *the batch continues*: a row that fails is released and left behind, the rest of the batch
proceeds, and after the attempt cap the row is dead-lettered rather than retried forever.

`SKIP LOCKED` in step 1 is what makes it safe to run many relays with no coordination — each takes
rows nobody else holds, and no relay waits on another. That is the same coordination-free pattern as
Chapter 17's claim, and it is not a coincidence: both are "ownership as a value with an expiry".

```
                                                            LAYER VIEW

  Components.

   state change (anywhere)
        |
        v
   +----+------------+
   | Outbox writer   |  MUST share the caller's transaction --
   |  append(txn)    |  the signature enforces it (Ch 9 section 8)
   +----+------------+
        |
        v
   [[ outbox ]]
        |
        v
   +----+------------+       +---------------------+
   | Claimer         |------>| Partitioner         |
   |  SKIP LOCKED    |       |  group by key;      |
   |  batch + lease  |       |  order within only  |
   +-----------------+       +----------+----------+
                                        |
        +-------------------------------+
        |               |               |
        v               v               v
   +----+-------+ +-----+------+ +------+-------+
   | Enqueuer   | | Command    | | Publisher    |
   |  run queue | | port       | |  external    |
   +----+-------+ +-----+------+ +------+-------+
        |               |               |
        +-------+-------+---------------+
                v
   +------------+------------+      +-------------------+
   | Acknowledger            |      | Dead letter       |
   |  per row, never batch   |----->|  visible, not     |
   +-------------------------+      |  blocking (Ch 27) |
                                    +-------------------+

  Figure 22.3 -- Spine components (D3 Component Diagram)
```

`[INF]` The Acknowledger acking *per row rather than per batch* is a small decision with a large
consequence. Batch acking means one failure either loses the successes or replays them, and both are
worse than a slightly chattier write pattern.

---

## 5. The Spine

### 5.1 The rule, and the signature that enforces it

`[DAR §7.1]` The state change and its event share one transaction. Chapter 9 §8 already gave the
enforcement:

```python
class EventEdge(Protocol):
    async def append(self, event: Event, txn: Transaction) -> None:
        """The transaction parameter is not optional. An event written
        outside its state change's transaction is the gap this whole
        chapter exists to close."""
```

`[INF]` Requiring a transaction the method does not own is what makes "publish after commit"
unwritable. A developer who has no transaction to hand has not yet made the state change, and one who
has committed already no longer has it — in both cases the type system asks the question that review
would otherwise have to.

### 5.2 Partition keys: ordering where it matters, nowhere else

Ordering is expensive to guarantee globally and rarely needed globally. `[DAR §7.2]` So it is
preserved *within a partition key* and not across keys.

| Key | Ordering guaranteed for | Concurrency |
|---|---|---|
| `run_id` | events about one run | high — runs are independent |
| `tenant_id` | everything for one customer | low — a busy tenant serialises |
| global | everything | none |

`[INF]` `run_id` is almost always right, and the reasoning is that the only orderings that matter are
within a run: step 4 completed before step 5, the gate was raised before it was resolved. Two runs
have no causal relationship, and forcing one on them converts an embarrassingly parallel stream into
a serial one.

The exception is any consumer that maintains cross-run state for a tenant — a quota counter, an audit
sequence. `[INF]` The right move there is usually to make that consumer order-independent rather than
to widen the partition key, because widening it slows every run down to fix one consumer.

### 5.3 Claim, not cursor

The cold open, and the comparison in full:

| | Cursor | Claim |
|---|---|---|
| Position tracked by | one shared integer | a column per row |
| One unprocessable row | **halts everything behind it** | is left behind; the rest proceed |
| Multiple consumers | need partitioning or locking | `SKIP LOCKED`; no coordination |
| Poison isolation | none | dead-letter after the attempt cap |
| Detecting a stall | the cursor stops moving — if watched | oldest unprocessed age, directly |
| Cost | one row updated per batch | one row updated per event |
| Reprocessing after a bug | rewind the cursor | reset `processed_at` on a selected set |

`[INF]` The cost row is the only one favouring cursors, and it is a write per event against an
outage per poison row. The last row is the underrated one: a claim-based spine lets you reprocess
*exactly the affected events* after fixing a handler bug, with a `WHERE` clause. Rewinding a cursor
reprocesses everything since, and the consumer had better be idempotent.

### 5.4 Delivery is at-least-once, and consumers dedup

`[BP]` A relay that dispatches and then dies before acking will dispatch again. That is unavoidable
without distributed transactions, so the guarantee is at-least-once and the consumer's job is to make
duplicates harmless.

`[INF]` Three consumer shapes, in order of preference:

| Shape | Dedup by | Example |
|---|---|---|
| Naturally idempotent | nothing needed | re-enqueue a `run_id` |
| Keyed | the event id, stored | credit a quota once |
| Conditional | a state check | wake a park only if still parked |

The first is why queue messages carry an id and nothing else (Chapter 8 §10): enqueueing the same run
twice is harmless, so the most common consumer needs no dedup machinery at all.

### 5.5 The command port

`[DAR §7.1]` Commands are the downward half of Chapter 4's waist, and they differ from events in the
ways §2.3 tabulated. Three properties:

**They carry an idempotency key.** `<command>:<scope>:<digest>` (Appendix B). The domain dedups
on it, which is what makes at-least-once delivery safe for something that changes the world.

**They may be refused.** A domain that rejects a command emits a rejection event, and the run learns
about it the same way it learns about anything else. `[INF]` This is the property that keeps the
waist narrow: the runtime never calls a domain function and inspects a return value, so it never
needs to know what the domain's return types are.

**They are the only downward path.** No shared tables, no imports. Chapter 4's deletion test is
enforced by there being exactly one arrow.

### 5.6 Poison events, and what to do about them

`[INF]` A poison event is one whose handler cannot succeed — malformed payload, a bug, a schema
change. It is not rare, and the design question is entirely about blast radius:

| Design | Blast radius of one poison event |
|---|---|
| Cursor | **the entire stream** |
| Claim, retry forever | that row, plus wasted capacity |
| Claim, attempt cap, dead-letter | **that row alone** |

`[INF]` Dead-lettering is not giving up. The row is preserved with its payload and its error, it is
visible in a queryable table, and it can be replayed after a fix by clearing `dead_at`. What it stops
doing is consuming relay capacity and hiding behind a retry loop.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  domain    outbox    relay-1   relay-2   run queue   dead letter
     |         |         |         |          |            |
  A patch is applied:
     |-- BEGIN                                             |
     |-- UPDATE repos ...                                  |
     |-- INSERT outbox: repo.patch.applied, key=run-9f2    |
     |-- COMMIT   <-- both, or neither                     |
     |         |         |         |          |            |
     |         |<-- claim batch (SKIP LOCKED) |            |
     |         |    ids 4101..4140, lease 30s |            |
     |         |         |<-- claim batch     |            |
     |         |         |    ids 4141..4180 -- NO WAIT    |
     |         |         |         |          |            |
     |         |         | 4101 -> enqueue -->|            |
     |         |         | ack 4101           |            |
     |         |         |                    |            |
     |         |         | 4102 -> handler RAISES          |
     |         |         |    attempts=1, claim released    |
     |         |         |    THE BATCH CONTINUES          |
     |         |         |                    |            |
     |         |         | 4103 -> enqueue -->|            |
     |         |         | ack 4103           |            |
     |         |         | ... 4104..4140 all proceed       |
     |         |         |                    |            |
     |   (4102 is retried on later batches, backing off)    |
     |         |         | attempts=5 > cap                 |
     |         |         |------------- dead_at = now() --->|
     |         |         |                    |            |
     |   the stream is unaffected throughout                |

  The cold open, for contrast:
     a cursor consumer reaches 4102, raises, does not advance.
     4103 through 4180 and everything after are stuck.
     No error rate rises. No latency moves. Nothing happens.

  Figure 22.4 -- One poison event, isolated (D4 Sequence)
```

### 6.1 Two relays, no coordination

`[INF]` Relay-1 and relay-2 claimed disjoint batches without knowing about each other, because
`SKIP LOCKED` skips rows another transaction holds rather than waiting on them.

There is no leader, no partition assignment, and no rebalancing. Adding a third relay requires
starting a process. That is the same property Chapter 17 established for run claims and Chapter 32
extends to workers generally: **coordination-free horizontal scaling, bought with a conditional
update.**

```
                                                             TIME VIEW

  The relay cycle.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | claim a batch        |  SKIP LOCKED, lease, ORDER BY |
   +----+-----------------+                               |
        |                                                 |
        +-- empty --> E1 idle; sleep and poll             |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | group by partition   |  ordering within a key only   |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | dispatch one event   |                               |
   +----+-----------------+                               |
        |                                                 |
        +-- ok --> ack that row --------------------------+
        |                                                 |
        v                                                 |
      /   \                                               |
     /attempts\ over cap -> dead-letter -> E2 -----------> +
     \  ?     /                                            |
      \      /                                             |
        | under                                            |
        v                                                  |
   +----+-----------------+                                |
   | release claim,       |  the batch CONTINUES with the  |
   | back off             |  next row (section 4.1)        |
   +----+-----------------+                                |
        |                                                  |
        +--------------------------------------------------+

  Exits:
    E1  nothing to do -- the healthy steady state
    E2  dead-lettered: preserved, queryable, replayable after
        a fix, and no longer consuming capacity
    E3  lease expired mid-batch -> another relay reclaims those
        rows; at-least-once, and consumers dedup (section 5.4)

  Figure 22.5 -- The relay cycle and its exits (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

  An outbox row's states.

            +---------------------+
            | {{ PENDING }}       |  written in the state change's
            +----------+----------+  transaction
                       | claimed
                       v
            +---------------------+
            | {{ CLAIMED }}       |  claimed_by set, lease running
            +--+-------+-------+--+
               |       |       |
     dispatched|       |       | lease expired (relay died)
     and acked |       |       v
               |       |   +---+-----------------+
               |       |   | {{ PENDING }}       |  reclaimable;
               |       |   +---------------------+  MAY have been
               |       |                            dispatched --
               |       | failed, attempts > cap     at-least-once
               |       v
               |   +---+-----------------+
               |   | {{ DEAD }}          |  visible, queryable,
               |   +---+-----------------+  replayable after a fix
               |       |
               |       | dead_at cleared by an operator
               |       v
               |   +---+-----------------+
               |   | {{ PENDING }}       |
               |   +---------------------+
               v
            +---------------------+
            | {{ PROCESSED }}     |  terminal; retained for audit
            +---------------------+  then pruned (section 12.2)

  Illegal, and enforced:
    * an event written outside its change's transaction  -- 5.1
    * PROCESSED -> anything                              -- terminal
    * a cursor anywhere                                  -- 5.3
    * batch ack                                          -- per row

  Figure 22.6 -- An outbox row's states (D6 State Diagram)
```

### 7.1 The outbox is the only thing that must not be lost

`[INF]` Chapter 16 established that trajectories can be dropped, Chapter 9 that progress can be
dropped, Chapter 13 that telemetry can be dropped. This table cannot. Every durability guarantee in
the architecture reduces to rows in it being written atomically with their state changes and
eventually processed.

That has an operational consequence worth stating: **the outbox's storage is the last thing you
degrade under pressure.** Shed trace writes, shed metrics, shed progress streaming — never shed this.

### 7.2 Retention

| Rows | Keep | Why |
|---|---|---|
| `PENDING`, `CLAIMED` | until processed | the work has not happened |
| `DEAD` | until resolved | somebody must look |
| `PROCESSED` | days to weeks | audit and replay-after-a-fix |

`[INF]` Pruning processed rows is necessary — the table is high-churn — and the window should be
whatever makes §5.3's last row usable. If you might discover a handler bug a week later and want to
reprocess exactly the affected events, keep two weeks.

---

## 8. Internal APIs

```python
from typing import Protocol


class OutboxPort(Protocol):
    """The durability boundary. One method, and its signature is the
    architecture."""

    async def append(
        self, event: Event, partition_key: str, txn: Transaction
    ) -> None:
        """Append inside the caller's transaction.

        `txn` is required and is not created here. An implementation
        that opens its own transaction has reintroduced the gap this
        chapter closes (section 5.1).
        """


class RelayPort(Protocol):
    """Claims rows, never a cursor (section 5.3)."""

    async def claim_batch(
        self, relay_id: str, size: int, lease: timedelta
    ) -> list[OutboxRow]: ...

    async def ack(self, row_id: int) -> None:
        """Per row. Never per batch (section 4.1)."""

    async def fail(self, row_id: int, error: str) -> FailOutcome:
        """Increment attempts and release the claim. Dead-letters past
        the cap. The batch CONTINUES regardless -- one bad row is one
        bad row."""


class CommandPort(Protocol):
    """The downward half of Ch 4's waist."""

    async def send(self, command: Command, txn: Transaction) -> None:
        """Commands are appended to the outbox like events; the relay
        delivers them. They carry an idempotency key and may be
        refused, and a refusal comes back as an event (section 5.5)."""
```

`[INF]` `CommandPort.send` also taking a transaction is the detail that keeps the waist honest. A
command issued outside a transaction is a runtime calling into a domain synchronously, which is the
shared-channel Chapter 4 §2.2 spent a derivation ruling out.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class OutboxState(StrEnum):
    PENDING = "pending"
    CLAIMED = "claimed"
    PROCESSED = "processed"    # terminal
    DEAD = "dead"              # poisoned; queryable and replayable


@dataclass(frozen=True)
class Event:
    """Past tense, addressed to nobody, cannot be refused."""
    event_type: str            # <domain>.<noun>.<past_verb>
    payload: Mapping[str, object]
    occurred_at: datetime


@dataclass(frozen=True)
class Command:
    """Imperative, addressed to one handler, may be refused."""
    command_type: str          # cmd.<domain>.<imperative_verb>
    payload: Mapping[str, object]
    idempotency_key: str       # <command>:<scope>:<digest>
    reply_with: str            # the event type expected back


@dataclass(frozen=True)
class OutboxRow:
    id: int
    event_type: str
    partition_key: str         # ordering within this, and no wider
    payload: Mapping[str, object]
    attempts: int
    claimed_until: datetime | None
```

`[INF]` `Command.reply_with` naming the event expected back is what lets the runtime park on a command
without knowing anything about the domain that handles it. The run parks awaiting
`repo.patch.applied`, the domain emits it, the relay wakes the run — and at no point does the runtime
import a domain type or call a domain function.

---

## 10. Communication

```
                                                            LAYER VIEW

  state change + event   any   ====> [[ outbox ]]   ~1-5 KB, ONE txn
  claim                  relay ====> [[ outbox ]]   ~200 B per row
  enqueue                relay ====> (( queue ))    ~100 B, id only
  command                relay ====> domain         ~1-20 KB
  domain's own event     domain ====> [[ outbox ]]  ~1-5 KB, ONE txn
  external publish       relay ====> subscribers    varies

  Volume: the outbox sees one row per durable fact. Ch 7's cold open
  was progress written here -- which multiplies the row count by
  viewer count and is why progress is not a fact.

  Figure 22.7 -- What moves through the spine (D7 Data Flow)
```

```
                                                             TIME VIEW

  anything -----> outbox     append, inside a transaction
  relay --------> queue      most events become work
  relay --------> domain     as commands, across the waist
  domain -------> outbox     its own events, its own transaction
  runtime --X     domain     REFUSED: no synchronous calls (5.5)
  domain --X      runs table REFUSED: no shared state (Ch 4)
  relay --X       a cursor   REFUSED: claims only (5.3)
  handler --X     the batch  a failure stops one row, not the batch

  Figure 22.8 -- Who may cause work (D8 Control Flow)
```

```
                                                             TIME VIEW

  Everything durable in the system flows here. Representative:

  << run.created >>            ....> the edge, at submission
  << run.step.completed >>     ....> the checkpoint txn (Ch 17)
  << run.parked >>             ....> with its resolution condition
  << approval.decided >>       ....> the edge; wakes a gate (Ch 30)
  << repo.patch.applied >>     ....> the DOMAIN, its own txn
  << outbox.event.dead >>      ....> a poison row; somebody must look
  << relay.stalled >>          ....> oldest unprocessed age exceeded
                                     -- the cold open's missing alert

  Figure 22.9 -- The spine's own events (D9 Event Flow)
```

`[INF]` `relay.stalled` being an event the spine emits about *itself* is deliberate. §2.1's breaking
point was that nothing volunteers the information that nothing is happening; a relay that checks the
oldest unprocessed row's age on every cycle and emits when it exceeds a threshold is the cheapest
possible fix, and it costs one query per batch on an index that already exists.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 21 Durable Execution | the domain's event survives a dead worker | closes half the record window |
| Ch 24 Task Graph | join completion as an event | durable joins need durable facts |
| Ch 27 Failure | dead-letter semantics | the same pattern as activities |
| Ch 30 Human Authority | `approval.decided` wakes a park | the gate's resolution path |
| Ch 32 Distributed | `SKIP LOCKED` claims, no coordination | many relays add nothing |
| Ch 34 Observability | oldest-unprocessed age | alerting on absence |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Cursor consumer | the obvious stream design | **nothing happens**; no error moves | claim-based relay — the cold open |
| Publish after commit | it looks equivalent | changes with nothing told, rarely | one transaction (§5.1) |
| Silent stall | no alert on absence | oldest unprocessed age rising | alert on it; `relay.stalled` |
| Batch ack | fewer writes | one failure loses or replays successes | ack per row |
| Global ordering | "ordering is safer" | throughput collapsing to serial | partition by `run_id` (§5.2) |
| No dead letter | retry forever | a poison row consuming capacity | attempt cap, then `dead_at` |
| Non-idempotent consumer | assuming exactly-once | duplicated effects after a relay restart | at-least-once; dedup (§5.4) |
| Progress in the outbox | it looks like an event | table growth tracking viewer count | Chapter 7; progress is not a fact |
| Command with a return value | synchronous convenience | the runtime importing domain types | commands are refused via events |
| Outbox shed under load | treating it as telemetry | silent, permanent work loss | it is the last thing to degrade (§7.1) |

`[INF]` Row three deserves its own alerting story because it is the only failure in this book whose
symptom is the absence of symptoms. Every other row in every other chapter produces an error, a
latency change, or a wrong answer. A stalled spine produces green dashboards and a system that has
stopped. **Alert on the age of the oldest unprocessed row**, and treat that alert as page-worthy.

---

## 12. Scalability

### 12.1 Relays scale by starting more of them

`SKIP LOCKED` means no relay waits on another and none needs to know how many exist. `[INF]` The
practical limits, in the order you hit them:

| Limit | Symptom | Fix |
|---|---|---|
| Claim contention | claims returning fewer rows than asked | smaller batches, more relays |
| Write throughput on the outbox | insert latency rising | partition the table by time |
| Handler throughput | claims fine, acks slow | scale the consumers, not the relay |
| Ordering within a hot key | one partition serialising | narrower key, if causality allows |

`[INF]` The third row is the common one and it is misdiagnosed as a relay problem. If the relay is
claiming happily and the queue is growing, the relay is fine and something downstream is not.

### 12.2 The outbox is high-churn and must be pruned

Every durable fact writes a row; every processed row becomes dead weight. `[BP]` A partitioned table
by `created_at` with old partitions dropped is the standard answer, and it turns pruning into a
metadata operation rather than a large delete.

`[INF]` The retention window is set by §7.2's reprocessing use case rather than by storage cost. Two
weeks of processed events is small and is what makes "fix the handler, reprocess exactly the affected
rows" possible.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| **Oldest unprocessed row age** | the cold open, and the only detector for it | **page** above threshold |
| Dead-lettered rows | poison events needing a human | any, daily digest |
| Claim batch fill ratio | contention between relays | consistently under-filled |
| Attempts distribution | handlers failing intermittently | a rising tail |
| Events per second, by type | the system's actual heartbeat | a drop is as bad as a spike |
| Relay lease expiries | relays dying mid-batch | any sustained |
| Outbox row count | pruning working | monotonic growth |

`[INF]` Row five deserves a note. "Events per second by type" dropping is often the *first* visible
sign of the cold open, and it is a signal most teams have and none alert on, because monitoring
convention is to alert on things going up.

### 13.2 The test that catches the cold open

```python
async def test_one_poison_event_does_not_stall_the_stream(
    spine: Spine, handlers: FakeHandlers
) -> None:
    handlers.raise_on(event_type="repo.patch.applied", payload_id=42)

    for i in range(100):
        await spine.append(event(i), partition_key=f"run-{i}", txn=txn)

    await spine.relay.run_until_idle()

    # The property: 99 of 100 processed. The cold open processed 41.
    assert await spine.processed_count() == 99
    assert await spine.dead_count() == 1
    assert (await spine.dead_rows())[0].payload_id == 42


async def test_event_and_state_change_are_atomic(spine: Spine, db) -> None:
    with pytest.raises(DeliberateFailure):
        async with db.transaction() as txn:
            await db.execute("UPDATE runs SET state='X' WHERE id=$1", rid, txn)
            await spine.append(event, partition_key=rid, txn=txn)
            raise DeliberateFailure()

    # Neither landed.
    assert await db.state_of(rid) != "X"
    assert await spine.pending_count() == 0
```

`[INF]` The second test is the one that fails against "publish after commit", and it is three lines.
It is worth writing on the first day the outbox exists, because the defect it catches is invisible
until a process dies at exactly the wrong microsecond — which happens rarely, and eventually.

### 13.3 The runbook entry

> **Nothing is happening and nothing is erroring.** Check the age of the oldest unprocessed outbox
> row first, before anything else. If it is rising, the relay is stalled or dead — check that any
> relay is claiming at all, then look for a row with high `attempts`. If the age is normal, the spine
> is fine and the problem is downstream.

---

## 14. Relation to AHE

The spine is runtime, not harness, and the loop does not edit it. What it provides is the property
that makes an iteration measurable at all.

**Every fact the loop reads originates here.** `[INF]` Chapter 41's per-task outcomes, Chapter 47's
observed deltas, and Chapter 45's manifest verification all rest on runs having reached terminal
states and those states being durable. A spine that loses events produces runs that never finish,
which an evaluation harness records as failures — and the loop then attributes an infrastructure
defect to a harness component.

**Dead letters are a data-quality signal for evaluation.** `[INF]` A benchmark run whose spine
dead-lettered events has rollouts that stalled for reasons unrelated to harness quality. Chapter 41
should treat a non-zero dead-letter count during a benchmark as a reason to discard the run rather
than score it, and that is only possible because dead-lettering is visible rather than hidden inside
a retry loop.

**The command port is what keeps the domain out of the loop's reach.** Chapter 46's Evolve Agent
edits harness components; the domain is not one. `[INF]` Because the only path into the domain is a
command crossing the waist, and commands are issued by kernel code the agent cannot edit, there is no
edit available to it that changes what the product does to the world. That containment is structural
rather than enforced by a rule.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the transactional outbox as the sole required durability primitive, claim-based
relay in preference to a cursor, partition-key selection, the command and event distinction with
their naming conventions, and the requirement that the runtime never call a domain synchronously
`[DAR §7.1, §7.2]`.

**`[AHE]`** Nothing directly. This is runtime; its contribution to the loop is the reliability that
makes measurement trustworthy.

**`[INF]`** The handbook's own: the derivation that both orderings of two writes are broken and one
system fixes it, the handover-book analogy with ambient supervision as its breaking point, the
observation that a stalled spine is the one failure whose symptom is the absence of symptoms, the
argument that dead-lettering bounds blast radius to one row, per-row acking, the claim that the
outbox is the last thing to shed under pressure, and `relay.stalled` as a self-emitted alert.

**`[BP]`** The transactional outbox, `SKIP LOCKED` work claiming, dead-letter queues, and
at-least-once delivery with consumer-side dedup are all long-established. The contribution is
assembling them as a single spine and being explicit that the cursor alternative is an outage
waiting for a malformed row.

**`[FUT]`** Nothing here is speculative. This is the most conventional chapter in Level 3 and
deliberately so: it is Stage 0 of the build order, everything rests on it, and novelty would be a
liability.

---

## 16. Key Takeaways

1. **The state change and its event share one transaction.** Both orderings of two separate writes
   are broken, and no stronger primitive is needed — only the observation that one system fixes it.
2. **Claim rows; never track a cursor.** One unprocessable row halts a cursor-based stream entirely.
   With claims it is left behind, dead-lettered, and everything else proceeds.
3. **A stalled spine is silent.** No error rate moves, no latency changes, every dashboard stays
   green. Alert on the age of the oldest unprocessed row, and page on it.
4. **Order within a partition key, never globally.** `run_id` is almost always right, because the
   only causal orderings that matter are within a run.
5. **Delivery is at-least-once; consumers dedup.** The most common consumer — re-enqueue a run id —
   is naturally idempotent, which is why queue messages carry an id and nothing else.
6. **Commands go down and may be refused; events go up and cannot.** If your event can be rejected,
   it is a command that was named wrongly.
7. **The outbox is the last thing you degrade.** Shed traces, metrics, and progress under pressure.
   Every durability guarantee in the architecture is rows in this table.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Event spine** | The outbox, relay, and command port together: how one thing that happened reliably causes the next. | `[DAR]` | Ch 27, Ch 32 |
| **Transactional outbox** | A table written in the same transaction as a state change, making the change and its announcement atomic. | `[DAR]` | Ch 21, Ch 30 |
| **Relay** | The worker that claims outbox rows and turns them into work, enqueued, commanded, or published. | `[DAR]` | Ch 32 |
| **Claim-based consumption** | Marking individual rows as taken, so one unprocessable row cannot halt the stream. | `[DAR]` | Ch 32 |
| **Cursor** | A shared stream position; standard elsewhere, and here an outage waiting for a malformed row. | `[BP]` | Ch 27 |
| **Partition key** | The scope within which event ordering is preserved, and deliberately no wider. | `[DAR]` | Ch 32 |
| **Poison event** | A row whose handler cannot succeed; dead-lettered so its blast radius is one row. | `[INF]` | Ch 27 |
| **Dead letter** | A terminally failed row preserved, queryable, and replayable after a fix, without consuming capacity. | `[DAR]` | Ch 27 |
| **Command port** | The single downward path into a domain, carrying an idempotency key and refusable via an event. | `[DAR]` | Ch 30 |
| **At-least-once delivery** | The guarantee a relay can make, with consumers responsible for making duplicates harmless. | `[BP]` | Ch 32 |
| **Oldest unprocessed age** | The age of the longest-waiting outbox row; the only detector for a silently stalled spine. | `[INF]` | Ch 34 |

---

**Next:** Chapter 23 — *The Scheduler.* Convoy effects, latency-class partitioning, model semaphores,
and per-tenant admission — and why one global concurrency integer cannot bound three different
resources.
