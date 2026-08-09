```
  Level 2 · Chapter 13
  THE REASONING ENGINE
  Requires   C6 State Separation, C9 Three Flows, C11 The Context System
  Unlocks    C14 The Tool Execution Engine, C18 The Runtime Loop,
             C21 Durable Execution, C35 Cost Engineering,
             C38 Deployment and Versioning
  Diagrams   Full (9)
```

# Chapter 13 — The Reasoning Engine

---

## 1. Motivation

### 1.1 Cold open

A customer cancels a run. The interface confirms within a second, the run row moves to `CANCELLED`,
and the dashboard shows no active work for that tenant.

The next morning, finance flags that the tenant's spend for the day exceeded their cap — on a day
when they cancelled almost everything they started.

The model port had a sixty-second timeout, implemented the way timeouts usually are: a wait with a
deadline around the request. When it fired, the coroutine was cancelled, the connection was dropped,
and the runtime moved on. The provider did not. It had accepted the request, and it generated the
completion to the end and billed for every token, because a client disconnecting is not a
cancellation. It is a client disconnecting.

Each abandoned call was invisible twice. It never returned, so no tokens were recorded against the
run's budget. And it never failed in a way anything counted, because from the runtime's point of
view nothing had gone wrong.

The system believed it had spent less than it had, on work nobody would ever read.

### 1.2 In plain language

The reasoning engine is the one place in the whole system that talks to a language model. Every
other component that needs the model asks this one to do it.

Having exactly one door matters for four reasons, and they are the whole chapter.

**Money.** Model calls are where the cost is. If there is one door, you can count what is spent and
refuse to spend more than a run is allowed. If there are two doors, the second one has no cap.

**Time.** A model call is the slowest thing in the system and it has no predictable duration. It is
the one operation that must be abandonable partway through, and — the cold open — abandoning your
end of it is not the same as stopping it.

**Unpredictability.** The model is the only part of the system that gives a different answer to the
same question. Confining that to one place is what lets everything else be replayed and tested.

**Portability.** Providers change. A new one has different parameter names, different error codes,
different ways of saying "you asked for too many tokens". If any of that vocabulary escapes past
this component, swapping providers means touching the whole codebase instead of one file.

The chapter is mostly about doing those four things properly, and about the gap the cold open
exposed: the difference between stopping *waiting* and stopping *spending*.

### 1.3 Why this chapter exists

Chapter 11 built what goes into a model call. This chapter builds the call itself, and it is the
component where three of the book's running themes converge on one function signature.

Chapter 2's custody rule says no scarce resource is held across a model call. Chapter 3's quarantine
model says non-determinism is confined to marked regions. Chapter 5's Activity is defined as the
only place non-determinism is permitted. All three are statements about this component, and none of
them is enforceable unless every model call in the system goes through it.

`[INF]` The practical test is a one-line grep: the provider's SDK should be importable in exactly
one module. If a second module imports it, the cap, the abort, the accounting, and the quarantine
all have a bypass, and the bypass is where the incident will come from.

### 1.4 What previous framings got wrong

**"It is a thin wrapper around the SDK."** A wrapper forwards. This component meters, reserves,
caps, aborts, normalises, and accounts. The cold open is what a thin wrapper produces: correct
behaviour on the happy path and no answer at all for the case that costs money.

**"A timeout is a cancellation."** The cold open, stated as a belief. A timeout stops you waiting.
Whether it stops the provider generating is a separate question with a provider-specific answer, and
§5.4 is about closing the gap between them.

**"Retry the model call like any other request."** A retried HTTP GET returns the same thing. A
retried model call returns a *different sample*, costs again, and may be a second charge for work
that already succeeded. §5.5 separates retry from replay, and they are not the same operation.

**"Sampling parameters are tuning."** `[INF]` Temperature, effort tier, and max tokens are harness
configuration pinned alongside the model identity (Chapter 1). Changing one is a harness version
change, and Chapter 1's cold open is what happens when that is not treated as one.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A company's single procurement desk.

Every department that wants to buy something from outside goes through one desk. Nobody has their
own supplier account. That is inconvenient, and it is the point, because four things become possible
that are impossible otherwise.

The desk **knows the budget** and refuses a request that would exceed it — which only works because
there is no second way to buy. It **records every order**, so the month's spend is a fact rather
than an estimate. It **can cancel an order** and confirm the cancellation with the supplier. And it
**knows which supplier** is being used, so a department asks for "500 units of part X" rather than
naming a vendor, and switching vendors changes one desk rather than forty departments.

Metering, capping, aborting, and provider-independence: the four properties of §1.2, arrived at from
the other direction.

**Where the analogy breaks**, in the place the cold open lives.

A procurement desk can telephone the supplier and genuinely cancel an order. Model providers
frequently cannot be cancelled: on many APIs, once generation has begun, disconnecting stops the
bytes arriving but does not stop the meter. The desk can stop *waiting for delivery*; it cannot
always stop *being charged*.

`[INF]` That distinction has a structural consequence, and it is why §5.3's accounting is designed
the way it is. A cancelled call must be assumed to have cost full price until the provider says
otherwise. Anything else understates spend precisely when a system is under stress and cancelling
things — which is exactly when an accurate number matters most.

### 2.2 Why exactly one door

```
  1. Model calls are where money is spent per unit of work. Nothing
     else in the runtime has a marginal cost worth capping.
  2. Spend must be capped per run and per tenant, or one run can
     consume a budget that belonged to everybody.
  3. A cap is only enforceable at a point every call passes through.
  4. Separately: a model call has unbounded latency, so it is the one
     operation that must be abandonable partway (Ch 5 custody).
  5. Separately again: it is the only source of non-determinism, and
     Ch 3's quarantine model requires that to be confined somewhere
     nameable.
  6. Metering, capping, aborting, and quarantining are four different
     properties, and every one of them requires a chokepoint.
  7. If a second path to the provider exists, all four are
     unenforceable -- not weakened, unenforceable, because the second
     path is not subject to any of them.
  8. Therefore: one port, and the provider SDK is importable in
     exactly one module. That import restriction is the architecture,
     stated as a lint rule.
```

Step 7 is stronger than it first reads and worth dwelling on. A second path does not halve the
effectiveness of a budget cap; it removes it, because the calls that bypass the cap are exactly the
ones that are not counted against it. Partial enforcement of a cap is not partial protection — it is
an incorrect number that people will trust.

### 2.3 The four properties, and what each forbids

| Property | Means | Forbids |
|---|---|---|
| **Metered** | every call's tokens are recorded, including failed and abandoned ones | fire-and-forget calls; uncounted retries |
| **Capped** | a call that would exceed the run or tenant budget is refused before it is made | optimistic spending with reconciliation afterwards |
| **Abortable** | an in-flight call can be abandoned, and the abandonment is accounted for | timeouts that leak; cancellation that only stops waiting |
| **Opaque** | no provider vocabulary escapes upward | provider error codes, finish reasons, or parameter names above this line |

`[DAR §10.3]` states the first three. `[INF]` The fourth is the handbook's addition and the one most
often skipped, because its cost is deferred: nothing breaks until the second provider arrives, and
then everything does at once.

### 2.4 The mental model to carry

> **The model port is the system's only meter, its only spending limit, its only abort handle, and
> its only quarantine boundary. Four unrelated-sounding requirements that all reduce to: there must
> be exactly one way to call a model.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  KERNEL                                                      |
  |                                                              |
  |   +------------------+   +------------------+                |
  |   | planner (Ch 10)  |   | grader (Ch 28)   |   the callers   |
  |   +--------+---------+   +--------+---------+                |
  |            |                      |                          |
  |        (1) |                      | (1)                      |
  |            v                      v                          |
  |   +========+======================+=========+                |
  |   |  MODEL PORT                             |                |
  |   |                                         |                |
  |   |   reserve -> call -> settle -> normalise|                |
  |   |                                         |                |
  |   +====+==========+==========+==========+===+                |
  |        | (2)      | (3)      | (4)      | (5)                |
  |        v          v          v          v                    |
  |  [[ budget  ]]  abort     [[ trace ]]  provider              |
  |  [[ ledger  ]]  signal      store      adapter               |
  |                   ^                       |                  |
  |                   | (6) from the run      |                  |
  |                   |     driver            |                  |
  +-------------------|-----------------------|------------------+
                      |                       | (7)
                      |                       v
                      |            +~~~~~~~~~~~~~~~~~~~~~~~+
                      |            | PROVIDER API          |
                      |            | the only place its    |
                      |            | vocabulary exists     |
                      |            +~~~~~~~~~~~~~~~~~~~~~~~+

  Figure 13.1 -- The model port in its surroundings
                 (D1 High-Level Architecture)

  (1) callers pass a Context (Ch 11) and a policy; never a provider
      name, never provider parameters
  (2) reserve before the call, settle after -- section 5.3
  (3) an abort signal the caller may fire; delivery is best-effort
      and the accounting assumes it failed (section 2.1)
  (4) token accounting and timings; telemetry, never facts (Ch 9)
  (5) exactly one adapter per provider, behind one interface
  (6) cancellation originates with the run driver, from a signal
      (Ch 7) or a budget refusal
  (7) the ONLY import of a provider SDK anywhere in the system
```

`[INF]` The shape worth noticing is that the port has four outbound edges and only one of them goes
to a provider. Three quarters of this component is bookkeeping, and that ratio is correct: the
call itself is a single HTTP request, and everything difficult about it is what surrounds the
request.

Wire 3 is drawn as a signal rather than a return path deliberately. The caller does not *ask* the
port to cancel and wait for confirmation; it fires a signal and the port makes a best effort. §5.4
explains why the design cannot promise more than that.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  MODEL PORT, opened -- one call, in fixed order

  +--------------------------------------------------------------+
  |                                                              |
  |  1. RESOLVE POLICY   model id, effort tier, sampling params,  |
  |     |                max output tokens -- from the pinned     |
  |     |                harness version (Ch 38), never a default |
  |     v                                                        |
  |  2. ESTIMATE         input tokens from the Context; output    |
  |     |                bounded by max_output_tokens             |
  |     v                                                        |
  |  3. RESERVE          take worst-case cost from the budget     |
  |     |                ledger. REFUSED -> raise, do not call    |
  |     v                section 5.3                             |
  |  4. TRANSLATE        our request -> this provider's shape.    |
  |     |                The only place that mapping exists.      |
  |     v                                                        |
  |  5. CALL             with a deadline AND an abort handle.     |
  |     |                Holds no connection, no lock (Ch 5).     |
  |     v                                                        |
  |  6. NORMALISE        provider response -> our Completion.     |
  |     |                finish reasons, errors, and token counts |
  |     |                all mapped to our vocabulary here.       |
  |     v                                                        |
  |  7. SETTLE           replace the reservation with actual      |
  |     |                cost. On abort: settle at the RESERVED   |
  |     |                amount, not zero (section 5.4).          |
  |     v                                                        |
  |  8. ACCOUNT          tokens by kind, cache hit ratio,         |
  |                      latency, to the trace store              |
  +--------------------------------------------------------------+

  Figure 13.2 -- One model call, opened (D2 Low-Level Architecture)
```

### 4.1 Reserve before, settle after

`[DAR §6.4]` The ordering of steps 3 and 7 is the chapter's most consequential structural decision,
and it exists because of an asymmetry: you know what a call *might* cost before making it, and what
it *did* cost only afterwards.

If the budget is checked only after the fact, a run with one dollar left can make a fifty-dollar
call, and the cap is a report rather than a limit. Reserving the worst case first means a call that
cannot be afforded is never made.

`[INF]` The cost of this is that reservations are pessimistic — most calls settle for less than they
reserved — so a run's *reserved* spend runs ahead of its *actual* spend, and a run can be refused a
call it could in fact have afforded. That is the correct direction to be wrong in, and Chapter 35
tunes the gap.

### 4.2 Normalisation is where the provider stops existing

Step 6 is the whole of property four. Everything provider-shaped is mapped here, in both directions:

| Provider concept | Our vocabulary |
|---|---|
| `finish_reason: "length"` / `"max_tokens"` / `"MAX_TOKENS"` | `Truncation.OUTPUT_LIMIT` |
| a rate-limit status, by whichever code this vendor uses | `ModelUnavailable(retry_after=...)` |
| a content filter refusal | `ModelRefused(category=...)` |
| `prompt_tokens` / `input_tokens` / `promptTokenCount` | `tokens.input` |
| cached-prefix accounting, where reported at all | `tokens.cached` |
| reasoning or thinking tokens, where reported | `tokens.reasoning` |

`[INF]` The last two rows are the ones that make this more than string mapping. Providers differ in
whether cached and reasoning tokens are reported at all, let alone how they are billed. A normaliser
must therefore represent *"this provider does not tell us"* as a distinct value from *"zero"* —
Chapter 6's missing-is-not-zero rule, arriving in the place it costs the most, because a silent zero
here produces a cost dashboard that is confidently wrong.

```
                                                            LAYER VIEW

  Components and their interfaces.

   ModelRequest                                   Completion (frozen)
   (Context + policy)                                       ^
        |                                                   |
        v                                                   |
   +----+------------+                            +---------+-------+
   | Policy resolver |  ModelPolicy               | Accountant      |
   |  for(run, call) |-------------+              |  settle()       |
   +-----------------+             |              |  record()       |
                                   v              +---------+-------+
   +-----------------+      +------+---------+              ^
   | Budget ledger   |<-----| Reserver       |              |
   |  reserve()      |      |  estimate()    |              |
   |  settle()       |      +------+---------+              |
   +-----------------+             |                        |
                                   v                        |
   +-----------------+      +------+---------+     +--------+-------+
   | Abort registry  |----->| Caller         |---->| Normaliser     |
   |  handle(call_id)|      |  deadline +    |     |  to Completion |
   +-----------------+      |  abort handle  |     |  to our errors |
        ^                   +------+---------+     +----------------+
        |                          |                        ^
        | signal from              v                        |
        | the run driver    +------+---------+              |
                            | Provider       |--------------+
                            | adapter        |  raw response
                            |  (one per      |
                            |   provider)    |
                            +------+---------+
                                   |
                                   v
                            +~~~~~~+~~~~~~~~+
                            | provider SDK  |  <-- the only import
                            +~~~~~~~~~~~~~~~+

  Figure 13.3 -- Model port components (D3 Component Diagram)
```

`[INF]` The Abort registry is drawn as a component rather than a parameter because cancellation
arrives *out of band*. The run driver receives a cancel signal at a checkpoint (Chapter 8) and must
be able to reach an in-flight call it does not hold a reference to. A registry keyed by call id is
the smallest thing that makes that possible, and without it "abortable" is a property the interface
claims and cannot deliver.

---

## 5. Metering, Capping, Aborting

### 5.1 Token kinds are not one number

`[INF]` Four kinds, priced differently, and conflating them makes cost work impossible:

| Kind | What it is | Typical relative price |
|---|---|---|
| `input` | context sent, not served from cache | baseline |
| `cached` | context served from the provider's prefix cache | a fraction of input |
| `reasoning` | internal tokens some models emit before answering | often priced as output |
| `output` | the completion returned | highest |

Chapter 11's entire argument — order by volatility, assert the volatile boundary — is an argument
about moving tokens from the first row to the second. `[INF]` That optimisation is invisible unless
the accounting separates them, which makes this table a prerequisite for the cold-open prevention in
Chapter 11 §13.1. A system reporting one aggregate token count cannot tell you whether its cache is
working.

`reasoning` deserves its own row because it is the one that surprises. It is frequently billed at
output rates, is not visible in the completion, and scales with the effort tier — so raising the
tier can multiply cost without changing a single visible token.

### 5.2 Effort tiers are policy, not a parameter

`[BP]` Models increasingly expose a reasoning-effort dial. Treating it as a per-call argument is the
mistake; it belongs in the pinned policy alongside the model id.

| Tier | Use for | Cost shape |
|---|---|---|
| minimal | classification, extraction, routing | cheapest; often adequate |
| standard | most planning and tool selection | the default |
| high | hard debugging, novel plans, final verification | reasoning tokens dominate |

`[AHE §4.3, Limitations]` reports gains that were non-monotone across reasoning tiers of one model
family — +2.3 points at one tier, +7.3 at the tier the harness was tuned on, +2.3 above it — with
step budget and timeout coupling implicated. `[INF]` The lesson for this chapter is narrow and
strong: **the effort tier is part of the harness version.** A run that starts under one tier
finishes under it, and changing the tier is a harness change subject to Chapter 38's rules, not a
configuration tweak.

### 5.3 Reserve-then-settle, and what a refusal means

```
  reserve  = (estimated_input + max_output) * price_for(policy)
  settle   = (actual_input_uncached * p_in)
           + (actual_cached        * p_cached)
           + (actual_reasoning     * p_reason)
           + (actual_output        * p_out)
```

A refusal at step 3 is not an error in the run; it is a **park**. `[DAR §8.2]` The run has hit its
budget cap, which is a condition a human can resolve by granting more, so it parks holding nothing
and waits — exactly like an approval gate. `[INF]` Treating budget exhaustion as a failure rather
than a park throws away work that a fifty-cent decision would have let finish, and it is a common
and expensive default.

### 5.4 Abort: stopping waiting is not stopping spending

The cold open, addressed directly. Three separate mechanisms, and the design assumes all of them may
fail:

1. **A deadline** on our side. Stops us waiting. Costs nothing to implement and solves nothing about
   spend.
2. **A provider cancellation**, where the API offers one. Best-effort, and its semantics vary: some
   providers stop billing at the cancellation point, some bill the full generation, and some accept
   the request and do neither.
3. **Streaming**, which converts an abort from a binary into a partial. If tokens arrive
   incrementally, abandoning at token 400 of a possible 4,000 means the provider generated 400 —
   whatever the billing model, the physical work stopped.

`[INF]` The accounting rule that follows is the important part, and it is deliberately pessimistic:

> **On abort, settle at the reserved amount unless the provider reports actual usage. Never settle
> at zero.**

Settling an abandoned call at zero is what made the cold open invisible. The tenant's spend was
under-reported by exactly the calls that had been abandoned, which is to say by exactly the calls
that were hardest to see. A pessimistic settle over-reports slightly and is correct in the direction
that matters: it makes cancellation *look* expensive, which it is.

`[INF]` This is also the strongest architectural argument for streaming that has nothing to do with
user experience. Streaming makes abandonment physically real rather than merely local.

### 5.5 Retry is not replay

The distinction the third framing in §1.4 got wrong, and it matters because the two look identical
at the call site:

| | Replay (Ch 21) | Retry (here) |
|---|---|---|
| Trigger | a run resumed after a crash | a call failed transiently |
| Identity | same `activity_id` | same `activity_id` |
| Result | the **stored** result is reused | a **new sample** is drawn |
| Cost | zero | full price, again |
| Determinism | guaranteed | none |

`[DAR §6.1]` A replay looks up the activity ledger and finds a result. A retry happens when there is
no result to find — the call never completed. So the ordering rule is: **always check the ledger
before calling; never retry a call whose result was recorded.**

`[INF]` The dangerous case sits between them, and it is the cold open's cousin: a call that
*succeeded at the provider* and whose result was lost in transit. The ledger has no result, so the
runtime retries, and the tenant is billed twice for one logical step. There is no clean fix — the
provider has no idempotency key for generation — so the mitigations are partial and worth naming
honestly: cap retries at one, prefer streaming so a partial result is still a result, and count
`retry_after_timeout` as its own metric because it is the rate at which you are probably
double-paying.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  driver     model port    ledger      adapter     provider   trace
    |            |            |           |           |          |
    |-- call(context, policy) |           |           |          |
    |            |-- resolve policy from pinned harness version  |
    |            |-- estimate: 47,900 in + 8,000 max out         |
    |            |-- reserve --->|           |           |        |
    |            |<-- ok, $0.62 held --------|           |        |
    |            |-- translate ->|           |           |        |
    |            |               |-- request ----------->|        |
    |            |               |                       |        |
    |            |          [ 41 seconds pass ]          |        |
    |            |                                       |        |
    |<== cancel signal arrives at the driver's checkpoint |        |
    |-- abort(call_id) --------->|           |           |        |
    |            |-- registry: fire handle -->|           |        |
    |            |               |-- cancel ------------->|        |
    |            |               |<-- accepted; usage NOT reported |
    |            |                                       |        |
    |            |-- settle at RESERVED $0.62 ---------->|        |
    |            |   (not zero -- section 5.4)           |        |
    |            |.......... << model.call.aborted >> ...|------->|
    |<-- ModelAborted(reserved=$0.62, actual=unknown) ---|        |

  Happy path, for contrast:
    |            |               |<-- completion --------|        |
    |            |-- normalise: finish=STOP,                      |
    |            |   tokens{in 6,700, cached 41,200,              |
    |            |          reasoning 2,100, out 900}             |
    |            |-- settle actual $0.19; release $0.43 --------->|
    |<-- Completion -------------|                                |

  Figure 13.4 -- One model call, with an abort branch (D4 Sequence)
```

### 6.1 Reading the abort branch

Three things in that branch are the chapter.

**The provider accepted the cancellation and reported nothing.** That is the common case, not a
degraded one. The port cannot know what was spent, so §5.4's rule applies and the reservation stands
as the settled cost.

**`actual=unknown` is propagated, not erased.** Chapter 6's missing-is-not-zero rule: the return
value distinguishes "we know it cost $0.62" from "we reserved $0.62 and never found out". Chapter 35
aggregates these separately, so a tenant with many aborts shows a visible band of uncertainty rather
than a precise-looking wrong number.

**One event, and it is about spend rather than about reasoning.** `model.call.aborted` is durable
because a later reader — an auditor, a cost report, an attribution pass — is entitled to rely on the
fact that money was committed. The completion itself is not an event; it flows to the activity
ledger as a result (Chapter 21).

```
                                                             TIME VIEW

  One call's cycle, and the six ways out.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | check ledger for a   |  found -> E1 replay, no call, |
   | recorded result      |          no cost              |
   +----+-----------------+                               |
        | not found                                       |
        v                                                 |
   +----+-----------------+                               |
   | resolve policy       |                               |
   | estimate + reserve   |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \  refused                                      |
     /budget\----------------------> E2 park,             |
     \  ok? /                           BUDGET_EXHAUSTED  |
      \    /                                              |
        | yes                                             |
        v                                                 |
   +----+-----------------+                               |
   | translate + call     |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     /outcome\--- aborted -----> settle RESERVED -> E3     |
     \       /--- unavailable -> retry once ------->+      |
      \     /--- refused ------> E5 (no retry)      |      |
        |                                           |      |
        | completed                                 |      |
        v                                           |      |
   +----+-----------------+                         |      |
   | normalise + settle   |                         |      |
   | + account            |                         |      |
   +----+-----------------+                         |      |
        |                                           |      |
        v                                           +------+
      E4 Completion returned

  Exits:
    E1  replay hit; result reused, zero cost      (Ch 21)
    E2  budget refused; run PARKS holding nothing (section 5.3)
    E3  aborted; settled at the reservation, actual unknown
    E4  completed; settled at actual
    E5  provider refused on content grounds; NOT retried, because
        the same request will be refused again
    E6  retry exhausted (one attempt); activity fails to the
        run driver, which may replan (Ch 10 section 5.4)

  Figure 13.5 -- The call cycle and its exits (D5 Runtime Loop)
```

`[INF]` E5 existing separately from E6 is a small decision with a large cost consequence. A content
refusal is deterministic: the same context will be refused again, so retrying buys nothing and pays
twice. Systems that treat every non-success as retryable spend real money rediscovering that.

---

## 7. State Management

```
                                                            STATE VIEW

  One call's states. All of this lives for the duration of one call
  and then is gone -- the port holds nothing between calls.

            +------------------+
            | {{ RESERVED }}   |  budget committed, nothing sent
            +--------+---------+
                     | request accepted by the provider
                     v
            +------------------+
            | {{ IN_FLIGHT }}  |  the ONLY state with unbounded
            +--+----+-------+--+  duration; holds no connection,
               |    |       |     no lock, no lease (Ch 5)
     completed |    |       | aborted
               |    |       |
               |    | provider unavailable
               |    v       |
               |  +---------+--------+
               |  | {{ RETRYING }}   |  at most once
               |  +---------+--------+
               |            |
               |            v  (back to IN_FLIGHT, or give up)
               v
      +--------+--------+        +------------------+
      | {{ SETTLED }}   |        | {{ ABANDONED }}  |
      +-----------------+        +------------------+
       actual cost known          settled at RESERVED,
                                  actual UNKNOWN

  Illegal, and enforced:
    * RESERVED -> gone            a reservation is always settled or
                                  released; a leaked reservation
                                  silently shrinks the run's budget
    * ABANDONED -> settled at 0   section 5.4; this is the cold open
    * IN_FLIGHT holding a lease   Ch 5's custody rule; the driver
                                  released the lease before dispatch
    * RETRYING -> RETRYING        one retry, not a loop

  Figure 13.6 -- One call's states (D6 State Diagram)
```

### 7.1 The port is stateless between calls

`[INF]` Everything above lives for one call. The port holds no conversation, no session, no
accumulated history — Chapter 11 rebuilds all of that from durable facts on every call, and Chapter
6 classified it as model state precisely so that this component can be stateless.

The consequence worth stating: **any two model ports are interchangeable at any moment.** A call can
be made by any worker, and a worker that dies mid-call loses a reservation rather than a session.
The leaked reservation is then cleaned by the sweeper (Chapter 8), which is why the illegal
transition `RESERVED -> gone` is listed: a reservation with no owner and no expiry silently reduces
a run's budget forever.

### 7.2 What is durable

The reservation and the settlement, in the budget ledger — those are facts, and Chapter 35 builds on
them. The completion itself goes to the activity ledger as a result (Chapter 21), keyed by activity
identity. Token accounting and latency go to the trace store as telemetry.

Nothing else. `[INF]` In particular the request is not stored by this component: reconstructing what
was sent is Chapter 16's trajectory capture, and duplicating it here would produce a second copy of
the most sensitive data in the system, in a component whose retention rules nobody has written.

---

## 8. Internal APIs

```python
from typing import Protocol, AsyncIterator


class ModelPort(Protocol):
    """The only way to call a model. Metered, capped, abortable, opaque.

    No method takes a provider name, a provider parameter, or a raw
    prompt string. Callers pass a Context (Ch 11) and a policy id; the
    port resolves everything else from the pinned harness version.
    """

    async def complete(
        self,
        call_id: CallId,
        context: Context,
        policy: PolicyId,
    ) -> Completion:
        """Make one call.

        Raises BudgetRefused before making any request when the
        reservation cannot be taken -- the caller parks (section 5.3).
        Raises ModelAborted if the call was abandoned; the exception
        carries the settled amount and whether actual usage is known.
        Raises ModelRefused on a content refusal, which is NOT retried.
        """

    async def stream(
        self,
        call_id: CallId,
        context: Context,
        policy: PolicyId,
    ) -> AsyncIterator[Chunk]:
        """As complete(), but abandonment stops generation physically
        rather than only locally (section 5.4). Prefer this wherever the
        caller can consume it."""

    def abort(self, call_id: CallId) -> None:
        """Fire the abort handle for an in-flight call.

        Synchronous, non-blocking, and BEST EFFORT: it makes no promise
        that the provider stops, and the accounting assumes it did not.
        Safe to call for an unknown or finished call_id.
        """


class ProviderAdapter(Protocol):
    """One per provider. The only place a provider SDK is imported, and
    the only place its vocabulary exists."""

    async def invoke(self, request: ProviderRequest) -> ProviderResponse: ...
    def normalise_error(self, exc: Exception) -> ModelError: ...
    def token_usage(self, response: ProviderResponse) -> TokenUsage:
        """Fields the provider does not report must be None, never 0
        (Ch 6: missing is not zero)."""
```

`[INF]` `abort` returning `None` synchronously is a deliberate refusal to lie. An `async def abort()
-> bool` would suggest the caller can await a confirmed cancellation, and no provider offers that
guarantee. The signature encodes §2.1's breaking point, so a reader who never gets to that paragraph
still cannot write code that assumes cancellation succeeded.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class FinishReason(StrEnum):
    STOP = "stop"                    # the model finished
    OUTPUT_LIMIT = "output_limit"    # hit max_output_tokens
    TOOL_CALL = "tool_call"          # stopped to call a tool
    REFUSED = "refused"              # content refusal
    ABORTED = "aborted"              # we abandoned it


@dataclass(frozen=True)
class TokenUsage:
    """None means the provider did not report it. Never coerce to 0."""

    input: int | None
    cached: int | None               # served from the prefix cache
    reasoning: int | None            # internal; often billed as output
    output: int | None

    @property
    def is_complete(self) -> bool:
        return all(v is not None for v in
                   (self.input, self.cached, self.reasoning, self.output))


@dataclass(frozen=True)
class ModelPolicy:
    """Pinned with the harness version (Ch 38). Not per-call tuning."""

    model_id: str
    effort: EffortTier
    temperature: float
    max_output_tokens: int
    tool_choice: ToolChoice


@dataclass(frozen=True)
class Completion:
    text: str
    tool_calls: tuple[ProposedToolCall, ...]
    finish: FinishReason
    usage: TokenUsage
    cost_settled_cents: int
    cost_is_estimated: bool          # True when usage was incomplete
    latency_ms: int
    policy: ModelPolicy              # what actually ran, for Ch 47
```

Three fields carry the chapter.

**`TokenUsage` fields are nullable.** A provider that does not report cached tokens produces `None`,
not `0`, so a cost dashboard can show "unknown" rather than a confident understatement. This is
Chapter 6's rule in the one place where breaking it produces a number a finance team will act on.

**`cost_is_estimated` travels with the completion.** Chapter 35 sums estimated and known costs
separately. Without the flag, one aggregate hides how much of the total is guesswork.

**`policy` records what actually ran.** `[INF]` Chapter 47's attribution needs to know which effort
tier produced a result; an iteration that changed the tier and one that changed a prompt are
indistinguishable otherwise, and §5.2's non-monotone finding means the tier is exactly the variable
you cannot afford to lose track of.

---

## 10. Communication

```
                                                            LAYER VIEW

  context      ====>  model port    ~50-200 KB  the dominant movement
                                                 in the system (Ch 9)
  model port   ====>  provider      ~50-200 KB  translated, same order
  provider     ====>  model port    ~5-50 KB    completion
  model port   ====>  ledger        ~200 B      reserve, then settle
  model port   ====>  trace store   ~1 KB       usage, latency, cache

  streaming:   provider ~~~> model port ~~~> caller
               chunk by chunk; abandonment is physical, not local

  Figure 13.7 -- What moves through the model port (D7 Data Flow)
```

```
                                                             TIME VIEW

  planner --------> model port    "complete this context"
  grader ---------> model port    same door, same cap
  run driver -----> model port    abort(call_id), out of band
  model port -----> ledger        reserve BEFORE the request
  model port --X    provider      REFUSED when the reservation fails
  model port --X    run state     no write path; the driver settles
  provider --X      anything above the port    its vocabulary stops
                                               at the normaliser
  caller --X        provider      REFUSED: one import, one door

  Figure 13.8 -- Who decides that a model call happens
                 (D8 Control Flow)
```

```
                                                             TIME VIEW

  << model.call.aborted >>    ....>  money was committed and the work
                                     was discarded; auditors and cost
                                     reports rely on this
  << model.budget.refused >>  ....>  a run parked on its cap; a human
                                     may grant more

  NOT events:
    the completion          a RESULT, keyed by activity identity,
                            written to the activity ledger (Ch 21)
    token usage             telemetry to the trace store
    latency, cache ratio    metrics
    retries                 recoverable from the trace

  Figure 13.9 -- What the model port makes durable (D9 Event Flow)
```

`[INF]` Two events, and both are about money rather than about reasoning. That is the correct
selection under Chapter 9's test — *is a later reader entitled to rely on this?* A completion is
relied upon, but as a result rather than as an event, which is why it goes to the activity ledger
where replay can find it by identity.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 14 Tools | `tool_calls` are proposals, not dispatches | the runner may refuse them |
| Ch 18 Runtime Loop | calls hold no lease; the driver already let go | worker concurrency exceeds pool size |
| Ch 21 Durable Execution | check the ledger before calling; retry is not replay | double-billing is the failure |
| Ch 35 Cost | reserve/settle, four token kinds, `cost_is_estimated` | every cost number originates here |
| Ch 38 Deployment | policy is pinned with the harness version | changing the effort tier is a version change |
| Ch 47 Attribution | `policy` on every completion | which tier produced which result |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Abandoned call settled at zero | timeout treated as cancellation | spend exceeding the sum of recorded calls | settle at the reservation — the cold open |
| Timeout without abort | a deadline with no abort handle | provider bills for calls nothing consumed | fire the abort handle; prefer streaming |
| Second door to the provider | SDK imported outside the adapter | a lint rule on the import graph | one import, enforced in CI (§2.2) |
| Cap enforced after the fact | spend checked post-call | a single run exceeding its cap | reserve before, settle after |
| Leaked reservation | worker died between reserve and settle | run budget shrinking with no spend | reservations expire; the sweeper releases them |
| Retry after a lost success | result lost in transit, ledger empty | `retry_after_timeout` rate | cap at one retry; prefer streaming; measure it |
| Retrying a content refusal | every non-success treated as transient | repeated identical refusals | E5 is terminal (§6) |
| Provider vocabulary escapes | a `finish_reason` string compared upstream | grep for provider literals above the port | normalise at step 6 |
| Missing usage coerced to zero | `usage.get("cached", 0)` | cost dashboard too good to be true | nullable fields; `cost_is_estimated` |
| Effort tier changed globally | treated as config, not harness version | non-monotone quality change after a deploy | pin the tier with the harness version |
| Sampling drift | temperature set per call site | irreproducible runs; replay diverges | policy resolved from the pinned version only |

`[INF]` Row six has no clean fix and should be stated as such rather than dressed up. When a
completion succeeds at the provider and is lost before it reaches the ledger, there is no key by
which a retry can be recognised as a repeat — generation APIs do not offer idempotency keys. The
honest position is that this class of double-charge is a known residual, bounded by capping retries
at one and by preferring streaming, and measured so that its size is a number rather than an
assumption.

---

## 12. Scalability

### 12.1 The model port is where concurrency is actually bounded

`[DAR §5.4]` A model semaphore, not a connection pool, is the binding constraint. Chapter 5's
custody gradient placed an Activity as holding a scarce model slot for seconds to minutes, and this
is that slot.

| Bound by | Typical | Symptom when wrong |
|---|---|---|
| Provider rate limit | requests or tokens per minute | `ModelUnavailable` under load |
| Model semaphore | 4–16 concurrent, per work class | queue depth rising with idle workers |
| Budget, per tenant | dollars per period | parks at the cap |

`[INF]` The second row is the one that decouples this system from ordinary web-service intuition. A
worker waiting on a model call holds no connection and no lease, so worker concurrency may exceed
pool size by orders of magnitude (Chapter 4 §16). What it does hold is a semaphore slot, and *that*
is the number to size — against the provider's rate limit rather than against your own hardware.

### 12.2 Cost scales with context, not with calls

Chapter 11 §12.1 established that context grows with run length until compaction caps it. Since
input dominates the token mix on most calls, **cost per call is roughly proportional to context
size**, and the number of calls is the smaller lever.

`[INF]` The practical consequence for anyone optimising: halving the number of steps helps less than
halving the context per step, and the cache ratio is a larger lever than either. A run that moves
41,200 of its 47,900 input tokens into the cached column has cut its input cost by most of that
fraction without changing a single step.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Reserved minus settled, aggregate | reservation accuracy | a widening gap wastes budget headroom |
| `cost_is_estimated` share | how much of spend is guesswork | any sustained rise |
| Aborted calls per hour, and their settled cost | the cold open, measured | any non-zero without matching cancellations |
| `retry_after_timeout` rate | probable double-billing | any sustained non-zero |
| Cache ratio (`cached / (input + cached)`) | Chapter 11's boundary, measured here | a drop is a code change |
| Semaphore saturation | the real concurrency bound | sustained at the ceiling |
| Refusal rate by category | content refusals, not transient errors | reported, not alerted |
| Leaked reservations released by the sweeper | §7.1's illegal transition | any non-zero |

### 13.2 The test that catches the cold open

```python
async def test_abort_settles_at_the_reservation_not_zero(
    port: ModelPort, ledger: FakeBudgetLedger, provider: FakeProvider
) -> None:
    provider.accepts_cancellation_but_reports_no_usage()

    call = asyncio.create_task(port.complete(CALL_ID, context, POLICY))
    await provider.wait_until_in_flight()
    reserved = ledger.reserved_for(CALL_ID)

    port.abort(CALL_ID)

    with pytest.raises(ModelAborted) as err:
        await call

    # The property: an abandoned call costs what we committed, not zero.
    assert err.value.settled_cents == reserved
    assert err.value.actual_usage_known is False
    assert ledger.settled_for(CALL_ID) == reserved
```

`[INF]` `provider.accepts_cancellation_but_reports_no_usage()` is the fake's most important
behaviour, and it should be the **default** for the fake provider rather than an opt-in. A fake that
politely reports usage on cancellation models a provider that may not exist, and every test written
against it passes while the real system under-reports spend.

### 13.3 The import rule, enforced

```bash
# One provider SDK import, in one module. Anything else is the
# second door of section 2.2.
git grep -l -E '^(from|import) (anthropic|openai|google\.genai)' -- '*.py' \
  | grep -v '^runtime/ports/model/adapters/' \
  && echo "FAIL: provider SDK imported outside an adapter" && exit 1
```

`[BP]` Three lines in CI, and it is the only mechanism in this chapter that cannot be eroded by good
intentions. Every other property here is enforced by code that a well-meaning change can route
around; this one fails the build.

---

## 14. Relation to AHE

The model is the one part of the system the evolution loop may not touch, and this chapter is the
boundary that makes that enforceable.

**The model is outside the harness.** Chapter 1 drew the line: weights and provider are selected,
not written. `[AHE §3.3]`'s controllability constraints make model configuration read-only to the
Evolve Agent for exactly this reason — an agent permitted to raise its own effort tier would improve
its measured score by spending more money, which is not the improvement anybody was looking for.

**But the policy is harness state, and that is a genuine tension.** `[INF]` The effort tier and the
sampling parameters live in the pinned harness version, which is editable, while the model id is
not. The correct split is that the Evolve Agent may not change the model or the tier, because both
change cost in a way that confounds attribution, and Chapter 47's verdicts compare quality at fixed
cost.

**Non-monotone tier results are a warning about generalisation.** `[AHE §4.3, Limitations]` measured
gains that did not increase with reasoning effort, and implicated step budget and timeout coupling.
`[INF]` Read through this chapter, that is a statement about *this component's* parameters: a
harness fitted at one tier encodes assumptions about how many steps the model takes and how long
each takes, and both change with the tier. An evolution loop that optimises at one tier produces a
harness that is fitted to it, which Chapter 48 would classify as a generalisation limit rather than
a defect.

**The accounting is what makes cost-normalised evaluation possible at all.** `[INF]` "Success per
million tokens" `[AHE App. A]` is only computable if tokens are counted correctly — including
abandoned calls. A loop optimising against an under-reported denominator will prefer harnesses that
abort more, which is the cold open's incentive structure, industrialised.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the model port as a single metered, capped, abortable interface, the
reserve-then-settle budgeting discipline, the model semaphore as the real concurrency bound, the
rule that no scarce resource is held across a model call, and activity identity as the check that
precedes any call `[DAR §5.2, §5.4, §6.1, §6.4, §10.3]`.

**`[AHE]`** Supplies the non-monotone reasoning-tier result and the timeout-coupling hazard
`[AHE §4.3, Limitations]`, the controllability constraint making model configuration read-only to the
Evolve Agent `[AHE §3.3]`, and success-per-million-tokens as an evaluation metric `[AHE App. A]`.

**`[INF]`** The handbook's own: provider opacity as a fourth property alongside the three from the
source, the argument that partial cap enforcement is not partial protection, the four token kinds as
a prerequisite for measuring Chapter 11's cache work, settling an abort at the reservation rather
than zero, treating budget refusal as a park rather than a failure, the retry-versus-replay table
and the honest statement that lost-success double-billing has no clean fix, and the observation that
under-reported denominators give an evolution loop an incentive to abort.

**`[BP]`** Reserve-then-settle is standard practice in payments and capacity systems. The one-import
lint rule is ordinary dependency hygiene. Streaming as the mechanism that makes cancellation physical
is well understood in media delivery and applies here for the same reason.

**`[FUT]`** Generation APIs offer no idempotency key, so a completion lost in transit cannot be
recognised as already-purchased on retry (§11, row six). `[FUT]` A provider-side idempotency key for
generation would close the last real double-billing hole in this architecture, and nothing in the
handbook's design can close it from the client side.

---

## 16. Key Takeaways

1. **Exactly one door.** Metering, capping, aborting, and quarantining each require a chokepoint. A
   second path to the provider does not weaken them; it removes them, because the bypassing calls
   are exactly the uncounted ones.
2. **Stopping waiting is not stopping spending.** A deadline protects your latency. Only a provider
   cancellation or streaming affects the bill, and neither is guaranteed.
3. **Settle an abort at the reservation, never at zero.** The cold open was invisible because
   abandoned calls contributed nothing to the recorded spend. Over-reporting is the correct direction
   to be wrong in.
4. **Reserve before, settle after.** A cap checked after the call is a report, not a limit. And a
   refusal is a park, not a failure — a human can grant more budget.
5. **Retry is not replay.** Replay reuses a stored result at zero cost; retry draws a new sample at
   full price. Always check the ledger first, and never retry a content refusal.
6. **Missing token counts are not zero.** A provider that does not report cached tokens must produce
   `None`, or your cost dashboard is confidently wrong in the direction finance will notice.
7. **The effort tier is part of the harness version.** Measured gains across tiers were non-monotone;
   a harness is fitted to an operating point, and changing that point is a version change, not a
   configuration tweak.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Model port** | The single interface through which every model call in the system passes, metered, capped, abortable, and provider-opaque. | `[DAR]` | Ch 18, Ch 21 |
| **Provider adapter** | The one module per provider where its SDK is imported and its vocabulary exists. | `[INF]` | Ch 38 |
| **Reserve-then-settle** | Committing the worst-case cost before a call and replacing it with the actual afterwards, so a cap is a limit rather than a report. | `[DAR]` | Ch 35 |
| **Reservation** | Budget held for an in-flight call; always settled or released, never abandoned. | `[DAR]` | Ch 35 |
| **Settlement** | Replacing a reservation with what a call actually cost, or with the reservation itself when the actual is unknowable. | `[INF]` | Ch 35 |
| **Abort handle** | The out-of-band mechanism for abandoning an in-flight call; best effort, and never assumed to have worked. | `[DAR]` | Ch 30 |
| **Token kinds** | Input, cached, reasoning, and output — priced differently, and meaningless when aggregated into one number. | `[INF]` | Ch 35 |
| **Reasoning tokens** | Internal tokens some models emit before answering; usually billed as output, invisible in the completion, and scaling with the effort tier. | `[BP]` | Ch 35 |
| **Effort tier** | The reasoning-effort setting, pinned with the harness version because gains across tiers are not monotone. | `[AHE]` | Ch 38, Ch 46 |
| **Model policy** | Model id, effort tier, sampling parameters, and output cap, resolved from the pinned harness version rather than per call. | `[INF]` | Ch 38, Ch 47 |
| **Normalisation** | Mapping a provider's finish reasons, errors, and usage fields into ours, so its vocabulary stops at this boundary. | `[INF]` | Ch 38 |
| **Model semaphore** | The concurrency bound that actually binds, sized against the provider's rate limit rather than local hardware. | `[DAR]` | Ch 23, Ch 33 |
| **Content refusal** | A deterministic provider refusal, which is terminal rather than retryable because the same request will be refused again. | `[INF]` | Ch 31 |
| **Estimated cost** | A settled amount the provider never confirmed, tracked separately so aggregate spend shows its own uncertainty. | `[INF]` | Ch 35 |

---

**Next:** Chapter 14 — *The Tool Execution Engine.* Tool description and tool implementation as two
separate editable surfaces, the pure/effectful tag that is the entire safety model, the middleware
pipeline, and why truncation belongs at the tool boundary rather than anywhere downstream of it.
