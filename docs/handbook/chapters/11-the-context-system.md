```
  Level 2 · Chapter 11
  THE CONTEXT SYSTEM
  Requires   C6 State Separation, C9 Three Flows, C10 The Planner
  Unlocks    C12 The Memory System, C13 The Reasoning Engine,
             C18 The Runtime Loop, C35 Cost Engineering,
             C44 Experience Observability
  Diagrams   Full (9)
```

# Chapter 11 — The Context System

---

## 1. Motivation

### 1.1 Cold open

09:20. Someone adds one line to Atlas's system prompt, so the model knows what day it is:

```text
Current time: 2026-03-04T09:20:11Z
```

It ships at 11:00. By 18:00 the cost dashboard shows spend per run has roughly tripled and time to
first token has doubled. Nothing else changed: same model, same tools, same plans, same task mix.

The line went at the top, which is where a system prompt naturally goes. Every model call in the
system now begins with a string that is unique to the second, and the provider's prompt cache
matches on an exact prefix. A forty-step run had been paying full price for its first call and a
fraction of that for the next thirty-nine. It now pays full price forty times.

The engineer who added it was not careless. They treated the prompt as a string, and it is not a
string. It is a cache key with a budget attached, and its first character is the most expensive one
in the system.

### 1.2 In plain language

A language model remembers nothing between calls. Every single time you ask it to do something, you
have to hand it everything it needs to know — the goal, what has happened so far, what tools exist,
what it learned last time — all as text, all over again, from scratch.

The context system is the component that builds that text. Not "the prompt": the whole package
assembled fresh for each step of a run.

It has to solve a problem that gets harder as a run goes on. There is a hard ceiling on how much
text fits in one call, and the amount of material that *could* be included grows with every step
taken. By step thirty there is far more history than will fit. So the context system is really
answering three questions, every call: what must always be in here, what should be in here if it is
relevant, and what gets thrown out when there is no room.

Two things make it more than a filtering exercise. Everything included is paid for, on every call —
so a run of forty steps pays for its context forty times. And most providers give you a large
discount when a call begins with exactly the same text as the previous one, which means the *order*
you assemble things in is a cost decision, not a matter of taste.

That is the cold open: a one-line change, in the wrong position, tripled the bill.

### 1.3 Why this chapter exists

Chapter 6 established that assembled context is **model state** — rebuilt from durable facts,
never stored as truth. That told you what context *is not*. This chapter builds what it is.

It matters more than its position in the book suggests. Chapter 9 §5.1 measured context assembly as
the single largest recurring data movement in the runtime, and it is paid per step rather than per
run. Chapter 35 will conclude that the highest-leverage cost work in an agent system is almost
always upstream of the model call. This is that upstream.

It is also where most quality problems actually live. When a run does something inexplicable, the
usual reflex is to look at the planner's instructions. `[AHE §4.4.1]` measured the system prompt
alone *regressing* against a minimal baseline, while components that change what the model can see —
tool descriptions, long-term memory — carried gains. The model did not reason badly. It reasoned
correctly about a context that was missing something.

### 1.4 What previous framings got wrong

**"Context is the prompt."** The prompt is one section of the context, and by measurement the least
valuable one. Everything in §5 is context; only the first block is a prompt.

**"Fill the window."** A window that is 90% full is not 90% used. It is one step from compaction, it
costs full price every call, and long contexts degrade retrieval of material in the middle. `[BP]`
Treat the ceiling as a budget you spend deliberately, not a target to approach.

**"Summarise when it gets long."** Compaction is necessary and summarisation is one of its riskier
forms. A summary is lossy in a way you cannot inspect later, and §11 shows the failure it causes:
the model re-derives a fact that was summarised away, three times, paying for it each time.

**"Context engineering is prompt tuning."** `[INF]` Prompt tuning changes the words. Context
engineering changes *what the model can see, in what order, at what cost*. The cold open changed no
words that mattered and cost more than any rewording could have.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A brief prepared for a barrister who reads it from page one, every time.

A clerk assembles the brief before each hearing. It has a fixed structure, and the structure is not
arbitrary. The standing matter goes at the front: the relevant law, the client's history, the
established facts. That material does not change between hearings. Today's specifics — the latest
correspondence, this morning's development — go at the back.

There is a reason for that order, and it is money. The barrister bills for reading, and only
re-reads from the first point where today's brief differs from yesterday's. An identical front means
they skim to the divergence and start there. Put today's date on page one and they re-read the
entire brief, at full rate, every single time.

There is also a page limit. When the file grows past it, the clerk must decide what is condensed
into a one-paragraph summary and what stays verbatim — and that decision has consequences, because
a fact that was condensed away is a fact the barrister will ask about again.

That is the whole chapter. Assembly order is §5, the page limit is §2.3, the condensing is §5.5, and
the billing rule is the cold open.

**Where the analogy breaks.** In two ways, both of which make the real problem harder.

A barrister *remembers the last hearing*. The model does not — it has total amnesia between calls,
so nothing can be left out on the grounds that it was covered last time. Everything relevant must be
physically present in every brief, which is why the file grows and why the page limit binds so
quickly.

And a barrister will tell you when the brief is missing something. A model will proceed confidently
with the gap, produce something plausible, and give you no signal at all that it was working from
an incomplete file. That asymmetry is why §13 instruments what went *into* the context rather than
relying on outcomes to reveal that something was missing.

### 2.2 Why context must be a managed component

Teams start with a function that concatenates strings, and it works. Here is why it stops working,
and what it must become:

```
  1. The model is stateless. It knows only what is in this request.
  2. Doing real work requires history, long-term memory, tool
     definitions, and the current goal -- none of which the model has.
  3. So something must gather all of it into one request, every call.
     A function that concatenates strings satisfies steps 1-3.
  4. But the request has a hard ceiling, and every token in it is paid
     for on every call.
  5. As a run progresses, the material that COULD be included grows
     without bound. The ceiling does not move.
  6. So by some step N, not everything fits. Inclusion becomes a
     SELECTION problem under a budget.
  7. A selection problem needs a policy: what is always present, what
     is present when relevant, what is dropped first, and what is
     condensed rather than dropped.
  8. Separately: providers discount a call whose prefix exactly matches
     the previous one. So the ORDER of assembly determines the bill,
     independently of the content.
  9. A component that owns a budget, an eviction policy, and an
     ordering contract is not a function that joins strings.
```

Steps 6 and 8 are independent, and that is what makes this component subtle. A team that solves only
the budget problem builds something that fits and costs three times what it should. A team that
solves only the ordering problem builds something cheap that falls over at step thirty. Both are
required, and they pull in different directions: the cheapest order is the most stable one, and the
material you most want to evict is the oldest, which is the most stable.

### 2.3 The budget, and what is left for work

`[INF]` The number people quote is the model's context window. The number that matters is what
remains after the fixed costs:

```
   context window                                    200,000
     - reserved for output                            -8,000
     - system prompt + safety preamble                -2,000
     - tool definitions (grows with tool count)       -6,000
     - long-term memory                               -3,000
     - current goal and plan                          -1,500
     ------------------------------------------------------
   = working budget, for history and evidence        179,500
```

Everything above the line is paid on **every** call whether or not it is used. `[INF]` This is the
number that makes tool-count discipline a cost decision: each additional tool definition is a small
tax levied on every model call in the system, forever. Twenty tools that are never called still cost
more than the run's entire long-term memory.

Chapter 15 makes tool definitions a design surface for exactly this reason, and progressive
disclosure (§5.4) is how the working budget stops shrinking as capability grows.

### 2.4 The mental model to carry

> **Context is not what you say to the model. It is what the model can see, in what order, at what
> price. Assembly order is a cost decision; inclusion is a quality decision; and the two are
> optimised against each other on every call.**

`[INF]` The tension in that last clause is the chapter. The cheapest context is one that never
changes, and a context that never changes contains nothing about the current step. Every design in
§5 is a way of getting most of the cache benefit while still saying something new.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  KERNEL                                                      |
  |                                                              |
  |   +------------------+                                       |
  |   | run driver       |  (1) assemble(run, plan, step)         |
  |   +--------+---------+-----------------+                     |
  |                                        v                     |
  |   sources, all READ-ONLY   +===========================+     |
  |                            |  CONTEXT SYSTEM           |     |
  |   [[ run_steps ]] --(2)--->|                           |     |
  |   [[ activities ]] -(3)--->|   budget                  |     |
  |   +~~~~~~~~~~~~~~+         |   assembly order          |     |
  |   | long-term    |--(4)--->|   compaction              |     |
  |   | memory file  |         |   cache-prefix contract   |     |
  |   +~~~~~~~~~~~~~~+         |                           |     |
  |   +--------------+         +=============+=============+     |
  |   | tool registry|--(5)--->|             |                   |
  |   +--------------+         |             | (6) Context        |
  |   +--------------+         |             |     (a value)      |
  |   | skills index |--(7)--->|             v                    |
  |   +--------------+         |    +================+            |
  |                            |    | MODEL PORT     |            |
  |                            |    +================+            |
  |                                                              |
  +--------------------------------------------------------------+

           (8) nothing is written back. Context is model state.

  Figure 11.1 -- The context system in its surroundings
                 (D1 High-Level Architecture)

  (1) the driver asks; the context system never self-triggers
  (2) prior steps of the CURRENT plan only (Ch 10)
  (3) results, already normalised and truncated by the tool
      engine (Ch 14) -- not raw tool output
  (4) long-term memory, read as a file (Ch 12)
  (5) definitions for tools available to this tenant and work class
  (6) a frozen Context value, with its budget accounting attached
  (7) skill headers only; bodies load on demand (section 5.4)
  (8) no writes, ever. Nothing here is a fact.
```

Wire 8 is the chapter's structural claim, and it is Chapter 6's model-state rule made visible: the
context system has no write path anywhere. It reads five sources and returns a value. If your
implementation has a `context` table, something has been misclassified, and Chapter 21's replay will
stop working for reasons that will take a week to find.

`[INF]` Wire 3 is worth reading twice. The context system consumes *normalised* results, not raw
tool output. A ten-megabyte `grep` result is truncated at the tool boundary (Chapter 14), before it
ever reaches here. If truncation lived in the context system instead, every source would need its
own ceiling and the amplification in Chapter 9 §5.3 would already have happened.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  CONTEXT SYSTEM, opened -- a pipeline, in fixed order
  +--------------------------------------------------------------+
  |                                                              |
  |  1. BUDGET      compute the working budget (section 2.3)      |
  |     |           fixed costs first; what remains is for        |
  |     |           history and evidence                          |
  |     v                                                        |
  |  2. GATHER      pull from the five sources. Cheap: no         |
  |     |           selection yet, only availability.             |
  |     v                                                        |
  |  3. ORDER       arrange by VOLATILITY, not by importance      |
  |     |             stable ......... system, tools, memory      |
  |     |             semi-stable .... goal, plan                 |
  |     |             volatile ....... step history, this step    |
  |     v           section 5.1. This is the cache contract.      |
  |  4. SELECT      include, defer, or drop each candidate        |
  |     |           against the budget. Policy, not heuristics.   |
  |     v                                                        |
  |  5. COMPACT     only if still over budget after SELECT        |
  |     |           evict, then condense; never condense first    |
  |     v                                                        |
  |  6. VERIFY      assertions that must hold before send:        |
  |     |             prefix is byte-identical to last call       |
  |     |               up to the volatile boundary               |
  |     |             total <= window - output reserve            |
  |     |             every referenced tool is defined            |
  |     |             no secret material present (Ch 37)          |
  |     v                                                        |
  |  7. FREEZE      return an immutable Context with its          |
  |                 accounting attached                           |
  +--------------------------------------------------------------+

  Figure 11.2 -- The assembly pipeline (D2 Low-Level Architecture)
```

### 4.1 Order before select, select before compact

`[INF]` The pipeline order is itself a design decision, and two of its three constraints are
non-obvious.

**Ordering precedes selection** because the cache boundary determines what selection is even allowed
to touch. Once the stable prefix is fixed, dropping something from it is expensive in a way that
dropping the same number of tokens from the volatile tail is not — a stable-region eviction
invalidates the cache for every subsequent call in the run, not only this one.

**Selection precedes compaction** because eviction is lossless and condensing is not. A system that
summarises first has destroyed information it might not have needed to touch. Drop what is
droppable, and only then condense what remains.

**Verification is last and is not optional.** Step 6 catches the cold open: an assertion that the
stable prefix is byte-identical to the previous call's would have failed on the first request after
that timestamp shipped, in staging, in under a second.

```
                                                            LAYER VIEW

  Components and their interfaces. Only two cross the boundary:
  an AssemblyRequest in, a frozen Context out.

   AssemblyRequest                                 Context (frozen)
        |                                                 ^
        v                                                 |
   +----+------------+                          +---------+--------+
   | Budgeter        |  Budget                  | Verifier         |
   |  compute()      |------------+             |  assert_prefix() |
   +-----------------+            |             |  assert_size()   |
                                  v             |  assert_clean()  |
   +-----------------+     +------+---------+   +---------+--------+
   | Source registry |     | Orderer        |             ^
   |  gather()       |---->|  by volatility |             |
   +--+--------------+     +------+---------+             |
      |                           |                       |
      | reads                     v                       |
      |                    +------+---------+             |
   +--+--------------+     | Selector       |             |
   | Sources (5)     |     |  include /     |             |
   |  history        |     |  defer / drop  |             |
   |  activities     |     +------+---------+             |
   |  long-term mem  |            |                       |
   |  tool registry  |            v                       |
   |  skills index   |     +------+---------+             |
   +-----------------+     | Compactor      |-------------+
                           |  evict()       |
                           |  condense()    |
                           +----------------+
                                  |
                                  v
                           << context.compacted >>
                           the ONE event this chapter emits

  Figure 11.3 -- Context system components (D3 Component Diagram)
```

`[INF]` The Verifier is drawn as a separate component rather than a few assertions inside the
assembler for a reason that matters in Level 5: it is the enforceable surface. Chapter 46's
constraint hierarchy says a rule belongs at the weakest level that can still enforce it, and "the
stable prefix must not vary" is a rule that code can enforce and prose cannot. An Evolve Agent
editing the system prompt cannot break the cache without the Verifier failing.

---

## 5. Assembly Order and the Selection Policy

### 5.1 Order by volatility, not by importance

The instinct is to put the most important material first. That is exactly backwards.

`[BP]` Providers cache on an exact prefix match. The longer the run of leading bytes that is
identical to the previous call, the larger the discount. So the ordering rule is:

> **Sort by how often it changes, most stable first. Within a stability band, sort by importance.**

| Band | Contents | Changes | Cache effect |
|---|---|---|---|
| Stable | safety preamble, system prompt, tool definitions | per deploy | cached across the whole run |
| Semi-stable | long-term memory, goal, current plan | per replan | cached until a replan |
| Volatile | step history, last result, this step's instruction | every step | never cached |

`[INF]` The consequence people find counter-intuitive: **the current goal does not go first.** It is
the most important thing in the context and it belongs in the middle, because putting it ahead of
the tool definitions would make the tool definitions uncacheable for no benefit. The model does not
read top-to-bottom in the way the ordering implies; position within the window is a cost property,
and importance is expressed by other means — section headers, recency, explicit instruction.

### 5.2 The volatile boundary is a contract

`[INF]` Define one offset in the assembled context and name it: everything before the **volatile
boundary** is asserted byte-identical to the previous call for this run; everything after may change
freely.

That single named concept converts a diffuse performance concern into a testable invariant. The
Verifier asserts it. Chapter 13 reports cache-hit ratio against it. And any change that moves it —
including a well-meaning timestamp — fails a test rather than a budget review six weeks later.

### 5.3 Selection: include, defer, drop

Every candidate gets one of three outcomes, and the policy is explicit rather than heuristic
(Chapter 6's prioritised-resolver discipline applied to context):

| Outcome | Meaning | Example |
|---|---|---|
| Include | present in full | the last three step results |
| Defer | replaced by a reference the model can expand with a tool call | a large file's path and summary line |
| Drop | absent, and its absence recorded in the accounting | step results older than the compaction horizon |

`[INF]` **Defer is the outcome that does the most work and is most often missing.** A deferred item
costs a few tokens now and can be retrieved on demand if it turns out to matter. A dropped item is
gone. Systems that only include-or-drop force every judgement to be final at assembly time, which is
precisely when the least is known about what this step will need.

### 5.4 Progressive disclosure

`[AHE §3.2]` The technique that makes deferral systematic: expose material as a navigable structure
and let the model pull what it needs, rather than pushing everything in advance.

Applied to three sources:

- **Skills.** Load the header of every skill — name, one line on when it applies — and the body of
  none. A skill's full text enters the context on the call after the model asks for it. Twenty
  skills then cost roughly what one used to.
- **Long-term memory.** Section headings always; bodies on request. Chapter 12 builds this.
- **Tool results.** A large result becomes a summary plus a handle, with a tool for reading ranges
  of it.

`[AHE §3.2]` reports the same principle at a larger scale: ten million tokens of raw trajectory
distilled to roughly ten thousand tokens of navigable evidence, with the exploring agent reading
only what it needs. `[INF]` That the identical technique works at both scales is a hint that it is
the general answer to a bounded window, rather than an optimisation.

### 5.5 Compaction: evict, then condense

Only when selection alone cannot fit the budget:

| Stage | Method | Lossy? | Reversible? |
|---|---|---|---|
| 1. Evict | drop the oldest step results beyond the horizon | no — they remain in the store | yes: re-read from `run_steps` |
| 2. Reference | replace an evicted block with a one-line pointer | no | yes |
| 3. Condense | model-generated summary of a span of history | **yes** | **no** |

`[INF]` Stage 3 is the only irreversible operation in the whole component, and it should be treated
with corresponding suspicion. Three rules:

1. **Never condense the current plan or the goal.** Both are small and both are load-bearing.
2. **Condense spans, not individual results.** A summary of steps 4–12 is inspectable; a summary of
   step 7 alone silently replaces a fact.
3. **Emit `context.compacted` with what was condensed.** This is the one event this component
   produces, and §11 explains why omitting it makes a whole class of bug undiagnosable.

### 5.6 The junk drawer

`[INF]` The failure mode that gives this chapter its reputation. Context accretes: someone adds the
repository's README because it helped once; someone adds the last five error messages; someone adds
a list of coding conventions. Each addition is individually justified and nothing is ever removed,
because removing something requires proving it is not helping and nobody can.

Two mechanisms prevent it, and both are structural rather than cultural:

- **Every source declares a budget share**, and adding a source means taking share from another. A
  fixed total forces the trade to be explicit.
- **Every source is attributable.** §9's accounting records tokens per source per call, so "the
  README costs 4% of every call in the system" is a number rather than an argument.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  driver     context sys     sources        verifier      model port
    |             |             |               |              |
    |-- assemble(run, plan, step 31) ---------->|              |
    |             |-- budget --->|              |              |
    |             |<-- 179,500 --|              |              |
    |             |-- gather --->|              |              |
    |             |<-- candidates: 214,000 tokens available    |
    |             |                             |              |
    |             | order by volatility          |              |
    |             | select: include 31 items, defer 6, drop 0  |
    |             |    still 12,400 over budget                |
    |             |                             |              |
    |             | COMPACT stage 1: evict steps 1-18          |
    |             |    -> 9,800 recovered. Still 2,600 over.   |
    |             | COMPACT stage 3: condense steps 19-24      |
    |             |    -> 4,100 recovered. Fits.               |
    |             |.......... << context.compacted >> ........>|
    |             |                             |              |
    |             |-- verify ------------------>|              |
    |             |    prefix identical to call 30?  YES       |
    |             |    total <= window - reserve?    YES       |
    |             |    all referenced tools defined? YES       |
    |             |    no secret material?           YES       |
    |             |<-- ok ----------------------|              |
    |             |                                            |
    |             |-- send ----------------------------------->|
    |             |                        cache hit on 41,200 |
    |             |                        of 47,900 prefix    |
    |<-- Context + accounting ---|                             |

  Failure branch at verify: prefix differs from call 30.
    -> assembly FAILS. The call is not sent.
    -> the run driver records a context defect and fails the step.
    Rationale in section 6.1: sending it would be correct and
    expensive, and correct-and-expensive is the failure that
    hides for six weeks.

  Figure 11.4 -- Assembling context for one step, with compaction
                 (D4 Sequence)
```

### 6.1 Why a prefix mismatch fails the call

`[INF]` This is the chapter's one genuinely contentious design choice, so it is worth stating the
alternative fairly.

A prefix mismatch does not produce a wrong answer. The model receives a valid context and does
correct work. Failing the step therefore trades a working run for a hard error, which looks like a
poor bargain.

It is the right bargain because of what the cold open demonstrated: a cache regression is invisible
in every functional signal and shows up only in aggregate cost, days later, attributed to nothing in
particular. Failing loudly at assembly turns a six-week cost incident into a failing test.

The mitigation for the obvious objection — that this could take down production over a formatting
change — is that the assertion is scoped to *within one run*. Call 31 must match call 30 of the same
run. A deploy that changes the system prompt does not fail existing runs, because those runs pinned
their harness version at claim time (Chapter 8 §14).

```
                                                             TIME VIEW

  The assemble cycle, per step. Entered once per model call.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | compute budget       |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | gather + order       |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     / fits \  yes ------------------------+              |
     \ ?    /                              |              |
      \    /                               |              |
        | no                               |              |
        v                                  |              |
   +----+-----------------+                |              |
   | evict oldest beyond  |                |              |
   | the horizon          |                |              |
   +----+-----------------+                |              |
        |                                  |              |
        v                                  |              |
      /   \                                |              |
     / fits \  yes -----------------------+|              |
     \ ?    /                             ||              |
      \    /                              ||              |
        | no                              ||              |
        v                                 ||              |
   +----+-----------------+               ||              |
   | condense a span      |  E3 if this   ||              |
   | (lossy, emits event) |  runs twice   ||              |
   +----+-----------------+  in one run   ||              |
        |                                 ||              |
        v                                 vv              |
   +----+---------------------------------++--+           |
   | verify                                   |           |
   +----+-------------------------------------+           |
        |                                                 |
        v                                                 |
      E1 send to the model port ------------------------->+
                                        next step

  Exits:
    E1  verified and sent                 -> normal
    E2  cannot fit even after condensing  -> run FAILED,
                                             context exhausted
    E3  condensing twice in one run       -> alert; the horizon
                                             or the budget is wrong
    E4  verify failed                     -> step FAILED,
                                             context defect (6.1)

  Figure 11.5 -- The assemble/compact cycle and its exits
                 (D5 Runtime Loop)
```

`[INF]` E3 is a design smell rather than an error, and it is the most useful signal here. Condensing
once in a long run is normal. Condensing twice means the first condensation did not recover enough,
which almost always means the budget is being consumed by something that should have been deferred.
Alerting on the second condensation catches a junk drawer forming, weeks before it shows up as cost.

---

## 7. State Management

```
                                                            STATE VIEW

  The budget's state within one run. Context itself has no state --
  it is a value, recomputed per call. What has state is the run's
  RELATIONSHIP to its budget.

              +------------------+
              | {{ COMFORTABLE }}|   under 60% of working budget
              +--------+---------+   all history included verbatim
                       | history grows
                       v
              +------------------+
              | {{ SELECTIVE }}  |   60-85%: deferral begins
              +--------+---------+   large items become references
                       | history grows
                       v
              +------------------+
              | {{ COMPACTING }} |   85-100%: eviction each call
              +--------+---------+
                    |     |
       condensed    |     | condensed a SECOND time
                    |     +--------------------+
                    v                          v
           +------------------+     +---------------------+
           | {{ SELECTIVE }}  |     | {{ DEGRADED }}      |
           +------------------+     +---------------------+
            recovered headroom       alert: budget is wrong,
                                     not the run (E3)
                                              |
                                              v
                                     +---------------------+
                                     | {{ EXHAUSTED }}     |
                                     +---------------------+
                                      cannot fit; run FAILED

  Note: these are DERIVED states, computed per call from the
  accounting. They are not stored. Storing them would make context
  a durable fact, which section 3 wire 8 forbids.

  Illegal:
    * EXHAUSTED -> anything      terminal for the run
    * skipping SELECTIVE         deferral is not optional; a run
                                 that jumps to COMPACTING has no
                                 deferral policy (section 5.3)

  Figure 11.6 -- Budget states within one run (D6 State Diagram)
```

### 7.1 Context is model state, and the rule has teeth

Chapter 6 classified assembled context as model state: rebuilt from durable facts, never persisted
as truth. This chapter is where that rule stops being a taxonomy and starts being load-bearing.

`[INF]` Three consequences that follow directly:

- **Replay works.** Chapter 21 replays a run by re-executing from checkpoints. If context were
  stored and replayed verbatim, a replay would reproduce a transcript rather than re-derive the run
  — and any fix to the assembly policy would be invisible to every historical run.
- **A policy change applies retroactively.** Improve deferral today and a run resumed tomorrow gets
  the improvement, because its context is built fresh under the current policy.
- **You cannot query what the model saw.** Chapter 9 §7 flagged this. The only way to answer "what
  was in the context at step 12?" is to have captured it deliberately (Chapter 16), and that capture
  is a trajectory record, not a context table.

### 7.2 What is durable, and it is very little

One event and one accounting record per call. Nothing else. The accounting is small, structured, and
goes to the trace store rather than the outbox — it is telemetry about a projection, and Chapter 9
§5.2 is explicit that neither is a fact.

---

## 8. Internal APIs

```python
from typing import Protocol


class ContextPort(Protocol):
    """Assembles model state for one call. Reads five sources, writes
    nothing, and returns a frozen value with its accounting attached.

    Pure with respect to the runtime: same request plus same sources
    produces a byte-identical Context. That is what lets Ch 40 replay
    a run hermetically and Ch 44 reconstruct what the model saw.
    """

    async def assemble(self, request: AssemblyRequest) -> Context:
        """Build the context for one step.

        Raises ContextVerificationError if the stable prefix differs
        from the previous call in this run (section 6.1), or
        ContextExhausted if it cannot fit after condensing (E2).

        There is deliberately no `append` and no `mutate`: a Context is
        produced whole or not at all.
        """

    def budget_for(self, run: ClaimedRun) -> Budget:
        """The working budget after fixed costs. Cheap, synchronous,
        and callable by the planner so it can size a plan against what
        will actually fit (Ch 10 section 11, plan-longer-than-budget)."""


class ContextSourcePort(Protocol):
    """One contributor of material. Every source declares its share, so
    adding a source means explicitly taking budget from another
    (section 5.6)."""

    name: str
    volatility: Volatility          # STABLE | SEMI_STABLE | VOLATILE
    budget_share: float             # of the working budget; sums to 1.0

    async def candidates(self, request: AssemblyRequest) -> list[Candidate]: ...
```

`[INF]` `budget_share` being a required attribute rather than configuration is the enforcement
mechanism for §5.6. A new source cannot be added without a number, the numbers must sum to one, and
therefore adding a source is structurally a negotiation with the existing ones. That is the junk
drawer prevented by the type system rather than by review discipline.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class Volatility(StrEnum):
    STABLE = "stable"              # per deploy
    SEMI_STABLE = "semi_stable"    # per replan
    VOLATILE = "volatile"          # per step


class Disposition(StrEnum):
    INCLUDED = "included"
    DEFERRED = "deferred"          # replaced by a retrievable reference
    DROPPED = "dropped"
    CONDENSED = "condensed"        # lossy; the only irreversible one


@dataclass(frozen=True)
class Candidate:
    source: str
    volatility: Volatility
    tokens: int
    importance: float              # ordering WITHIN a band only
    reference: str | None          # how to retrieve it if deferred


@dataclass(frozen=True)
class ContextAccounting:
    """Per-call, per-source. The whole of section 13 rests on this."""

    tokens_by_source: Mapping[str, int]
    disposition_by_source: Mapping[str, Disposition]
    working_budget: int
    used: int
    volatile_boundary_offset: int   # section 5.2, the cache contract
    cache_prefix_tokens: int        # asserted identical to last call
    compactions_this_run: int       # E3 fires when this reaches 2


@dataclass(frozen=True)
class Context:
    blocks: tuple[Block, ...]       # tuple: immutability is structural
    accounting: ContextAccounting
    harness_version: str            # what policy built this (Ch 38)
```

Two details carry the chapter.

**`volatile_boundary_offset` is stored on every context.** It is the number the Verifier asserts
against and the number Chapter 13 reports cache-hit ratio against. Naming it in the data structure
is what makes §5.2 a contract rather than an aspiration.

**`harness_version` is on the Context, not only on the run.** `[INF]` Two runs of the same task
under different assembly policies produce different contexts, and Chapter 47's attribution needs to
know which policy produced which. Without it, a Level 5 iteration that changes deferral cannot be
credited or blamed for the result.

---

## 10. Communication

```
                                                            LAYER VIEW

  run_steps      ====>  context system    ~10-80 KB   grows with run
  activities     ====>  context system    ~5-40 KB    already truncated
  long-term mem  ====>  context system    ~3-12 KB    headings, mostly
  tool registry  ====>  context system    ~6-25 KB    FIXED per call
  skills index   ====>  context system    ~1-3 KB     headers only

  context system ====>  model port       ~50-200 KB   <-- the largest
                                                          movement in
                                                          the system,
                                                          paid PER STEP

  context system ====>  trace store       ~1-2 KB     accounting only

  Figure 11.7 -- What moves when assembling (D7 Data Flow)
```

```
                                                             TIME VIEW

  driver ----------> context system    "assemble for this step"
  context system --> sources           read-only queries
  context system --> verifier          may REFUSE the whole assembly
  verifier --X       model port        a failed verify sends nothing
  context system --X run state         REFUSED: no write path (wire 8)
  context system --X tools             REFUSED: it reads results, it
                                       does not produce them
  model --X          context system    the model cannot ask for more
                                       context mid-call; it must
                                       propose a tool call and wait

  Figure 11.8 -- Who decides what the model sees (D8 Control Flow)
```

```
                                                             TIME VIEW

  << context.compacted >>  ....>  span condensed, with what and why.
                                  The ONLY event this chapter emits,
                                  and the only lossy operation it
                                  performs (section 5.5).

  NOT events, deliberately:
    the assembled context     a projection (Ch 6); durable only if
                              captured as a trajectory (Ch 16)
    per-call accounting       telemetry to the trace store
    deferral decisions        recoverable from the accounting
    cache hit ratio           a metric, not a fact

  Figure 11.9 -- What context work makes durable (D9 Event Flow)
```

`[INF]` One event, from the one irreversible operation. That is the correct ratio, and it follows
mechanically from Chapter 9's test: *would a later reader be entitled to rely on this?* Only the
condensation qualifies, because only the condensation destroyed something a later reader might
otherwise have found.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 12 Memory | headings-always, bodies-on-request | progressive disclosure applied to long-term memory |
| Ch 13 Reasoning Engine | `volatile_boundary_offset` | cache-hit ratio is reported against it |
| Ch 14 Tools | results arrive already truncated | truncation at the boundary, not here |
| Ch 15 ACI | each tool definition taxes every call | tool-count discipline is a cost decision |
| Ch 35 Cost | tokens per source per call | the cost lever is upstream of the model |
| Ch 44 Agent Debugger | what was dropped and condensed | most "reasoning failures" are context gaps |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Cache prefix broken | volatile content placed in the stable band | cache-hit ratio drops; cost per run rises | the Verifier's prefix assertion — the cold open |
| Junk drawer | sources added, none removed | tokens per source trending up; no source at 0 | mandatory `budget_share` summing to 1.0 |
| Condensed away a needed fact | summarisation of a span containing a key detail | the model re-derives the same fact repeatedly | condense spans not items; check `context.compacted` |
| Silent context gap | a source failed and returned empty | model proceeds confidently; no error anywhere | assert per-source minimum sizes at verify |
| Include-or-drop only | no deferral policy | budget states jump COMFORTABLE to COMPACTING | implement Defer (§5.3) |
| Truncation in the wrong layer | context system truncating raw tool output | one large result inflates every later call | truncate at the tool boundary (Ch 14) |
| Context stored as truth | a `contexts` table appears | replay reproduces transcripts; policy fixes do not apply retroactively | it is model state; wire 8 |
| Output reserve omitted | budget computed against the full window | truncated completions near the ceiling | reserve output first (§2.3) |
| Tool tax invisible | tool count grows unnoticed | fixed cost per call creeping up | report stable-band tokens as its own metric |
| Compaction thrash | horizon too close to the budget | `compactions_this_run` reaching 2 | E3 alert; widen the horizon or defer more |

`[INF]` Row four is the one that costs the most and appears in no dashboard. A source that fails and
returns nothing produces a context that is smaller, cheaper, and quietly missing the long-term
memory that would have prevented the run from repeating last week's mistake. Nothing errors. The run
completes. It is merely worse, in a way that is only visible if you assert that each source
contributed something.

That is the analogy's second breaking point, made operational: the model will not tell you the brief
was incomplete.

---

## 12. Scalability

### 12.1 Context is the super-linear term

Chapter 9 §12 named it: control and event flow scale roughly linearly with work; data flow does not.
Here is why, precisely.

Step *n*'s context includes history from steps 1 through *n*−1. So without intervention, total
tokens across a run of *N* steps is proportional to *N*², not *N*. A forty-step run does not cost
forty times a one-step run; it costs several hundred times more.

`[INF]` Compaction is what converts that quadratic into something closer to linear, by capping the
per-step context at the budget. **The purpose of the eviction horizon is not to fit; it is to make
cost linear in run length.** A team that raises the horizon whenever a run feels forgetful has
quietly restored the quadratic, and will discover it as a cost incident on their longest tasks.

### 12.2 The numbers that matter

| Quantity | Scales with | Watch |
|---|---|---|
| Tokens per call | budget, which is capped | should be flat across step index |
| Cost per run | steps × budget, once capped | linear in steps; superlinear means the horizon is too wide |
| Cache hit ratio | stability of the stable band | flat and high; a drop is a code change |
| Fixed cost per call | tool count | grows only when tools are added |
| Assembly latency | source count and sizes | small; if it is not, a source is doing work it should not |

`[BP]` "Tokens per call, plotted against step index" is the single most diagnostic chart in this
chapter. Flat is healthy. Rising means compaction is not keeping up. A sawtooth is normal and shows
compaction working; a sawtooth with a rising floor means the stable band is growing.

### 12.3 Assembly itself is cheap and must stay cheap

The context system does string and token work, not I/O of consequence — its sources are indexed
reads. `[INF]` If assembly latency is ever material relative to a model call, a source is doing
something it should not: a network fetch, an embedding query, a directory walk. Sources return
candidates from state that already exists. Anything that must be *computed* belongs in a pure step
the planner proposes (Chapter 10 §11), where it is cached by activity identity and visible in the
trace.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Cache hit ratio, per run | the cold open, measured | any sustained drop |
| Tokens per call vs step index | compaction health | rising floor |
| Tokens by source, per call | junk-drawer detection | any source trending up without a decision |
| Stable-band tokens | the tool tax | step change after a deploy |
| `compactions_this_run` p99 | budget or horizon wrong | reaching 2 (E3) |
| Deferral rate | is Defer implemented and used | near zero means include-or-drop |
| Per-source empty rate | the silent gap of §11 row four | any non-zero |

### 13.2 The test that catches the cold open

```python
async def test_stable_prefix_is_byte_identical_across_steps(
    runtime: Runtime, clock: FakeClock
) -> None:
    run = await runtime.submit(goal)
    contexts = [await runtime.assemble_for_step(run, n) for n in range(1, 6)]

    boundary = contexts[0].accounting.volatile_boundary_offset
    prefix = contexts[0].render()[:boundary]

    for ctx in contexts[1:]:
        assert ctx.render()[:boundary] == prefix

    # The mechanism, not only the outcome: advancing the clock between
    # steps must not change the prefix. This is the assertion the cold
    # open's timestamp would have failed, in staging, in one second.
    clock.advance(hours=3)
    later = await runtime.assemble_for_step(run, 6)
    assert later.render()[:boundary] == prefix
```

`[INF]` The clock advance is the point of the test. Without it, the test passes against a system that
embeds a timestamp, because five assemblies in the same second produce the same string. Most tests
of this property are written without it and are worthless.

### 13.3 The review question

`[BP]` One question for any change touching context:

> Which band does this land in, and if it is stable, does it vary?

Anything that varies belongs after the volatile boundary or nowhere. That single question, asked at
review, is what the cold open's change would not have survived.

---

## 14. Relation to AHE

The context system is the harness surface where the evolution loop has the most leverage and the
least visibility, which is an uncomfortable combination.

**Most leverage.** `[AHE §4.4.1]` measured tool descriptions and long-term memory carrying gains
where the system prompt alone regressed. Both of those are context-shaping components — they change
what the model can see, not how it is instructed. `[INF]` Read through this chapter, that result
stops being surprising: instructions compete with everything else for the model's attention, while
what is present or absent from the context determines what is *possible*.

**Least visibility.** §7.1 established that context is not stored. So an Evolve Agent reading a
failed trajectory sees the model's output and the tools it called, and does not see what it was
looking at when it decided. `[AHE §3.2]`'s trajectory capture is what closes that gap, and it closes
it only if the capture includes the assembled context rather than the messages alone.

**A concrete implication for Chapter 46.** The single highest-value edit available to an evolution
loop is often changing a `budget_share` or a deferral rule — a numeric change to a policy, with a
measurable cost and quality effect. `[INF]` That is a far better-conditioned optimisation target
than prompt wording, and it is only available if the context system exposes those numbers as
configuration rather than burying them in code. §8's `ContextSourcePort` puts them where the loop
can reach them.

**And a limit.** Chapter 48's non-additivity result applies sharply here. Two independently
beneficial context changes — deferring more aggressively, and adding a source — interact through a
single fixed budget, so their combined effect is not the sum of their separate effects. Context
edits are among the least additive in the harness, precisely because they all draw on one number.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the classification of assembled context as non-durable model state, the rule
that it is rebuilt from stored facts rather than persisted, and the model port's metering and cap
against which the budget is computed `[DAR §3.3, §10.3]`.

**`[AHE]`** Supplies progressive disclosure as a token strategy and the ten-million-to-ten-thousand
distillation ratio `[AHE §3.2]`, and the component ablation placing context-shaping components above
the system prompt by measured value `[AHE §4.4.1]`.

**`[INF]`** The handbook's own: ordering by volatility rather than importance and the reasoning for
it, the volatile boundary as a named testable contract, the include/defer/drop policy with defer as
the load-bearing outcome, evict-before-condense, the derived budget-state machine, the junk drawer
and the `budget_share` mechanism that prevents it, failing a call on prefix mismatch, the argument
that compaction exists to linearise cost rather than to fit, and the observation that context edits
are the least additive class of harness edit.

**`[BP]`** Prefix caching is a provider feature with published semantics, and ordering stable
material first is the standard advice that follows from it. The contribution here is treating the
boundary as an asserted invariant rather than a guideline.

**`[FUT]`** Nothing in this chapter is speculative. Its risk is that provider caching semantics are
the one external dependency here that can change without notice; §5.2's boundary is deliberately a
property of *our* assembly, so that a change in provider behaviour alters the discount rather than
the design.

---

## 16. Key Takeaways

1. **Context is not a string; it is a budgeted, cache-keyed resource.** The cold open is a one-line
   change, in the wrong position, tripling the bill without changing a single answer.
2. **Order by volatility, not importance.** Stable material first, so the prefix stays cacheable.
   The goal does not go at the top, and that is correct.
3. **Name the volatile boundary and assert it.** One offset turns a diffuse performance concern into
   a failing test that runs in one second.
4. **Defer is the outcome that does the most work.** Include-or-drop forces every judgement to be
   final at the moment least is known. Progressive disclosure is deferral made systematic.
5. **Evict before condensing.** Eviction is reversible; summarisation is the only irreversible
   operation in the component, and it is the one that makes a model re-derive the same fact three
   times.
6. **Compaction exists to make cost linear, not to make things fit.** Without it, a run of *N* steps
   costs proportional to *N*². Widening the horizon to fix forgetfulness silently restores the
   quadratic.
7. **Every source declares a share of a fixed budget.** That is what makes adding a source a
   negotiation rather than an accretion, and it is the only reliable defence against the junk drawer.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Context system** | The component that assembles, per model call, everything the model is allowed to see, under a budget and an ordering contract. | `[DAR]` | Ch 13, Ch 18 |
| **Working budget** | What remains of the context window after output reserve, system prompt, tool definitions, and long-term memory are paid for. | `[INF]` | Ch 35 |
| **Volatility band** | Whether material changes per deploy, per replan, or per step; the axis assembly order sorts on. | `[INF]` | Ch 13 |
| **Volatile boundary** | The offset before which the context is asserted byte-identical to the previous call in this run. | `[INF]` | Ch 13, Ch 40 |
| **Cache-stable prefix** | The leading span of a request that matches the previous call exactly and is therefore discounted by the provider. | `[BP]` | Ch 35 |
| **Defer** | Replacing material with a reference the model can expand later, rather than including or dropping it now. | `[INF]` | Ch 12, Ch 15 |
| **Progressive disclosure** | Exposing material as navigable structure so the model pulls only what it needs, instead of everything being pushed in advance. | `[AHE]` | Ch 12, Ch 44 |
| **Compaction** | Reducing context to fit the budget: evict first, reference second, condense only as a last resort. | `[INF]` | Ch 18 |
| **Condensation** | A model-generated summary replacing a span of history; the only irreversible operation in this component. | `[INF]` | Ch 44 |
| **Eviction horizon** | How far back history is kept verbatim; the dial that determines whether run cost is linear or quadratic in steps. | `[INF]` | Ch 35 |
| **Budget share** | The fraction of the working budget a source is entitled to; required, and summing to one across all sources. | `[INF]` | Ch 46 |
| **Junk drawer** | Context that accreted because every addition was justified and no removal ever was. | `[INF]` | Ch 46 |
| **Tool tax** | The fixed cost every tool definition levies on every model call, whether or not the tool is used. | `[INF]` | Ch 15 |
| **Context accounting** | Per-call, per-source record of tokens and disposition; the basis of every signal in this chapter. | `[INF]` | Ch 34, Ch 35 |

---

**Next:** Chapter 12 — *The Memory System.* Short-term, long-term, episodic, and procedural memory
as four different subsystems; why the ablation placed long-term memory among the highest-value
components; and why it is a file the model reads rather than a store it queries.
