# Chapter 6 — State Separation: Run, Domain, Model, and Harness

## Tracking

**CURRENT POSITION**
Level 1 — High-Level Runtime Architecture
Chapter 6 / 49 — State Separation: Run, Domain, Model, and Harness

**COMPLETED**
Ch 0–3 (foundations), Ch 4 (six layers, the narrow waist), Ch 5 (Run, Episode, Step, Activity, Park)

**TODAY**
Chapter 6 — the deletion test from Chapter 4, made precise, plus a third and fourth state category neither source names

**UNLOCKS**
Ch 7 (the edge builds read models the same way this chapter builds model state), Ch 11 (context assembly gets its full mechanics), Ch 12 (memory gets its write path), Ch 17 (state manager), Ch 21 (durable execution), Ch 32 (distributed execution), Ch 37 (tenancy), Ch 47 (attribution)

---

## WHY THIS CHAPTER EXISTS

Atlas finishes a hard run for tenant `acme`. The test suite failed four times before the agent figured out it needed a database URL in the environment. The harness does exactly what it's built to do: it writes the lesson to long-term memory, real hostname and credential fragment included, so no future run wastes forty minutes on the same problem.

Six weeks later, an engineer at a *different* customer opens a pull request Atlas wrote and finds a suggestion referencing `acme`'s internal Postgres host.

Nobody wrote a bug. The run that produced the lesson was scoped to `acme`'s tenant. Its row carried the tenant id. Its sandbox was destroyed on completion. Atlas's domain tables enforce tenant isolation on every query. Every mechanism you'd normally check was fine.

The leak went through the one piece of state that belonged to none of those mechanisms, so none of their rules applied to it.

Chapter 4 gave you a one-line test: delete the runtime, and the product must still be coherent. That test sorts state into exactly two buckets: survives deletion, or doesn't. Two buckets aren't enough — the leak above happened in a bucket the test can't even see.

## THE CORE IDEA — four categories, derived, not assumed

Start from Chapter 4's binary and push on it:

```
Does X survive deleting the runtime?
```

Ask that of the assembled context (what the model sees on one call). No — it doesn't survive deletion. So by the binary, it's run state, meaning it should be persisted like any other run fact.

But persisting it breaks something specific: a replayed run is supposed to *rebuild* its context from stored facts. If you instead stored the literal text blob and treated it as truth, you now have a second source of truth that can silently disagree with the facts it was built from. The binary has no bucket for "derived, must never be stored as truth." That gap is **model state**.

Now ask the same question of a long-term memory note. Yes, it survives deleting the runtime — it's a file. So the binary calls it domain state.

But it isn't a fact about the world, and none of the domain's tenant-isolation rules apply to a markdown file. Filing it as domain state scopes it by nothing at all. That gap is **harness state** — and it's exactly the gap the cold open fell through.

| Category | Answers | Owner | Lifetime |
|---|---|---|---|
| **Domain state** | What is true? | your domain | permanent |
| **Run state** | What is happening? | the runtime | ends with the run |
| **Model state** | What does the model see right now? | the context system | one model call |
| **Harness state** | What has the system learned to do? | the harness | across runs, until edited |

The first two come straight from the reference architecture. The second two are the handbook's own addition, forced by finding two things the binary classified wrong rather than by a preference for a bigger taxonomy.

**The classification procedure — run every field in your schema through this once, in order, first "yes" wins:**

```
Does it survive deleting the entire runtime?
   YES -> DOMAIN STATE
   no
    |
Does it outlive the run that produced it,
without being a fact about the world?
   YES -> HARNESS STATE
   no
    |
Is it fully reconstructible from facts already stored?
   YES -> MODEL STATE   (derive it; never persist it as truth)
   no
    |
   ---> RUN STATE
```

## THE FOUR CATEGORIES, ONE LEVEL DEEPER

### Domain state — what is true

Examples in Atlas: the pull request exists, the branch was pushed, the customer is on the enterprise plan. These stay true whether or not a run ever executed — and would be equally true if a human had done the work by hand. That's a fair test on its own: could a human have produced this fact without any of this runtime existing? If yes, it's domain state.

### Run state — what is happening

You already have this one cold from Chapter 5: the `runs` row (current step, plan_id, lease_owner, lease_until, budget spent), `run_steps`, `activities`, `run_signals`, `approvals`, `budget_ledger`. Add one thing you might not have placed yet: **short-term memory is run state.** Session scratch, dies with the run. That's not an arbitrary rule — it's a state-separation decision doing double duty as an access-control decision, because anything that dies with the run has no business being read by a process (like an evolution loop) reasoning across runs.

**The structural test, restated precisely:** no run state may live on a domain aggregate — no `current_step`, no `lease_owner`, no `plan_id` — and no domain truth may live in the run.

### Model state — the one people get wrong

This is the category worth slowing down on, because "the message list is the run's state" is, per the chapter, the single most damaging error in agent codebases.

**Mechanically, here's what happens at one model call:**
1. The context system reads harness files (system prompt, long-term memory, whichever skills got judged relevant) off a git-backed workspace.
2. It reads run state (`run_steps`, `activities`) from the database.
3. It reads domain facts through a query port — a fetched value, not an owned one.
4. It concatenates all of that, plus middleware injections, into one blob (roughly 50–200 KB in Atlas's numbers) and sends it to the model provider.
5. The completion comes back. The blob that produced it is **discarded**. Nothing about its literal bytes is written to any table.

**Why "just cache it" breaks something real, not just something tidy:** model state has no consistency model because it's derived — two runs at identical checkpoints must produce identical run state, but they don't have to produce identical assembled context, because assembly depends on token budgets, compaction thresholds, and which skills got loaded. If you persist the message list as authoritative anyway, three things follow, and the third one is fatal:

1. It becomes a second source of truth that can disagree with `run_steps` and `activities`.
2. It grows without bound, because nothing owns pruning it.
3. **Replay stops working.** Resumption only works because orchestration is a pure function of state and events. If the model's view is stored instead of derived, you can't reconstruct it after a compaction-policy change, and a replayed run diverges from the original for reasons that have nothing to do with the model's own non-determinism.

**The framing that makes this click:** the assembled context is a **read model for the model** — the same category as the dashboards the edge builds for humans (Chapter 7). Nobody stores a dashboard's rendered HTML as the source of truth for an account balance. Storing the message list as the source of truth for a run is the same mistake with better camouflage.

### Harness state — the gap category, and the cold open's actual cause

Long-term memory, prompts, tool code, middleware, skills. It fails *both* halves of the two-category test at once: delete the runtime and it's still there (so it isn't run state), but it isn't a fact about the world and no domain invariant depends on it (so it isn't domain state either). It sits in the gap, and things in the gap get scoped by nobody.

**The rule that belongs in every harness review:**

> Harness state must be true of the system, never of a customer.

"Test suites in this codebase need a database URL set" is a fact about a customer. "Check whether the test harness requires environment configuration before assuming a suite failure is a code defect" is the same lesson with the tenant removed — and it's *more* useful, because it generalizes to every customer instead of one.

This has to happen **at write time**, not read time. Filtering when a memory is read doesn't help, because the leak has already been committed to a versioned file by then. Chapter 12 puts the abstraction step directly in the write path.

## ONE CONCRETE TRACE — one step, every category marked

Step 7 of run `r-8f2`: the model is asked to revise a failing patch.

```
(1) driver claims the lease
       READS  run state    runs row: version, plan_id, current_step
       WRITES run state    lease_owner, lease_until, version+1
       ~5 ms, one connection, released immediately

(2) context assembly
       READS  harness      systemprompt.md, LongTermMEMORY.md, relevant skills
       READS  run state    run_steps for the plan, activities for prior results
       READS  domain       repo metadata via a query port (fetched, not owned)
       BUILDS model state  ~120 KB assembled context + cache prefix
       PERSISTS            nothing

(3) the model call
       CONSUMES model state
       PRODUCES a completion
       model state is now DISCARDED

(4) result handling
       WRITES run state    activities row: result, cost settled
       WRITES run state    events row: <<activity.completed>>
       one transaction

(5) memory consideration
       middleware judges whether a durable lesson was learned
       IF SO -> WRITES harness state, abstracted, tenant-free
       (in Atlas: a queued proposal, not a direct write — see Ch 12)

(6) checkpoint
       WRITES run state    current_step, version+1, lease renewed
       READS  run state    pending signals, same transaction
       ~5 ms
```

Two things this trace proves:

**Step (2) reads three categories and persists none.** Assembly is a pure projection. If it weren't, step (3) couldn't be replayed later.

**Step (5) is the only place a run writes harness state — and even there, it doesn't write directly.** A run that could append to a versioned, cross-tenant file at will could poison every future run in the system. Chapter 12 routes it through a proposal queue with the abstraction rule applied as a check before anything lands.

## ONE ANALOGY, AND ITS BREAKING POINT

A hospital's records. The **patient's medical record** is domain state: the truth about a person, outliving every admission, still valid if the hospital replaced its entire scheduling system tomorrow. The **whiteboard on the ward** — who's in which bed, whose round it is — is run state: intensely important while true, wiped when the admission ends. The **notes a doctor carries into one consultation**, assembled from the record for that single conversation, are model state: nobody files that page as the medical record, because it's a selection made for one purpose, and filing it would let the two silently disagree later. The **hospital's own protocols** — "in this ward, always check X before Y," learned from experience and written on a laminated card — are harness state: they belong to the institution, not to any patient, and persist across every admission.

The failure mode lives in that last category. Someone writes a genuinely useful protocol, and the protocol names a specific patient's specific circumstances, because that's the case that taught the lesson. Now a fact about one patient sits in the institution's permanent instructions, scoped by nothing. That's the cold open exactly.

**Where the analogy breaks:** hospital staff writing a protocol card know they're producing an institutional document and adjust their language for it. Harness state here gets written by a model mid-run, from a context saturated with one customer's specifics, with no sense of audience at all. Worse — an evolution loop (Chapter 46) rewards specificity, because specific memories measurably work better. The pressure runs *toward* the leak, not away from it. There's no professional instinct to fall back on here, which is exactly why abstraction has to be a checked step rather than a habit.

## IMPORTANT BOUNDARIES

**Model state ≠ Run state.**
Both live "in the runtime," but run state is authoritative and checkpointed — it's what you'd recover after a crash. Model state is a projection *of* run state (plus harness and domain facts), assembled fresh for one consumer and thrown away immediately after. Confusing them is exactly the "message list as truth" error above.

**Domain state ≠ Harness state.**
Both survive deleting the runtime, so the deletion test alone can't split them — that's precisely why the classification procedure needs a *second* question. Domain state is a fact about the world with an invariant behind it (a merged branch, a customer's plan tier). Harness state is a fact about the *system's own behavior* (a lesson, a tool description) with no invariant and, by default, no tenant scoping at all.

**State ≠ Event, restated in this chapter's terms.**
Domain and run state exchange only commands (down) and events (up) — Chapter 4's narrow waist. The event isn't the state; it's the durable announcement that state changed. Model state never gets an event of its own at all, because nothing about it needs to be replayed — it gets rebuilt, every time, from the states that do.

## WHO MAY WRITE WHAT

```
Writer            Domain           Run                  Model      Harness
Edge              via command      founding only         —          —
Run driver        —                yes                   —          —
Activity runner   via command      yes (results, cost)   assembles  proposals only
Ports (planner,
 grader)          —                —                     reads      reads
The model         never directly  never directly         —          never directly
Human operator    via product     signals/approvals      —          reviewed edits
Evolution loop    never           reads only             —          yes — its entire
                                                                     action space
```

The model's row is the safety model restated as a table: a model produces *proposals*. The runtime decides whether a proposal becomes a write. Every gate, schema check, and grader in this book is an implementation of that one row. And the evolution loop's row is the boundary from Chapter 4 §14 written out in full: its entire action space is one column.

## FAILURE MODE

| Failure | What crossed into what | Symptom |
|---|---|---|
| Lease on a domain aggregate | run → domain | Deleting the runtime leaves dangling columns; the Chapter 4 cold open |
| Domain truth in the run row | domain → run | Truth vanishes when a run gets pruned |
| Message list persisted as truth | model → run | Replay diverges after a compaction-policy change |
| **Tenant fact in long-term memory** | domain → harness | **This chapter's cold open** |
| Credential in a harness file | domain → harness | A secret sits in version control, permanently |
| Harness edited under a parked run | version skew | A run resumes against tools its own plan never saw |

**Why the harness leak beats every other row on this list, for four reasons that stack:**

- **It's durable.** A bad run ends. A bad memory entry gets committed to a versioned file and applies to every run that comes after it.
- **It's cross-tenant by construction.** Run state and domain state are scoped by a tenant id somewhere. Harness state, by default, is scoped by nothing.
- **It's invisible.** Nothing errors. The memory component did exactly what it was built to do, and doing that well is what causes the harm.
- **Level 5 amplifies it.** An evolution loop reads trajectories and writes memory, and it's rewarded for encoding specific, hard-won knowledge — the same ablation result from Chapter 1 that made memory the highest-value single component. Specificity is the value. Specificity is also the leak. There's no version of this where you get one without managing the other.

## THE FOUR CI CHECKS

Roughly two hundred lines total, and together they cover the entire failure table above:

1. **Deletion test.** In a test database, drop the runtime's own schema. Run the domain's full test suite. It has to pass.
2. **Column-name check.** Assert no domain table has a column named `current_step`, `lease_owner`, `lease_until`, `plan_id`, `attempt_count`, `budget_used`, or `run_state`.
3. **Import-graph check.** The domain package imports nothing from the runtime. The kernel imports nothing from the domain.
4. **Harness-tenancy check.** Scan every harness file for tenant identifiers, hostnames, credentials, customer names. Fail the build on a match.

The fourth one is the cold open's actual fix, and it's a regex pass over a handful of files.

## CONNECTION TO THE SYSTEM YOU'RE BUILDING TOWARD

```
RUN STATE box        -> exactly the runs/run_steps/activities rows;
                         the ONLY category the run driver may write freely

DATA (model/context)  -> model state: assembled fresh every call,
                         discarded after, never a second source of truth

CONTROL (planner/
 gate/budget)          -> reads run state and harness state, writes neither
                         directly — proposals only

ACTIVITY RESULT        -> the one thing that survives the model call:
                         a completion turned into a run-state row

domain (outside your
 sketch entirely)       -> reached only through a command, gated,
                         after which it writes its own truth + event

harness (also outside
 your sketch)           -> the one category with no tenant boundary
                         by default — the piece you have to add yourself
```

The gap in your original sketch is the same gap the whole chapter is about: nothing in a simple pipeline diagram forces you to draw a box for "what the system learned across runs," so it's easy to build that part without ever deciding who owns it or how it's scoped. This chapter is the argument for drawing that box on purpose, before something leaks through it.

---

**CHAPTER STATUS**
You should now be able to: run any field in a schema through the four-question classification procedure and land on one category; explain mechanically why persisting the assembled context breaks replay rather than just being untidy; and explain why harness state, specifically, is the category most likely to leak across tenants — and why an evolution loop makes that pressure worse, not better.

**KEY TERMS**
- **Domain state** — what's true about the world; owned by your product; unaffected by deleting the runtime.
- **Run state** — what's happening in one run right now; owned by the runtime; gone once the run ends.
- **Model state** — what the model sees on one call; derived, never persisted as truth; discarded immediately after.
- **Harness state** — what the system has learned to do; survives the runtime without being a fact about the world; unscoped by default.
- **Read model / projection** — a view assembled from authoritative facts for one consumer, never itself authoritative.
- **Classification procedure** — the four ordered questions that assign any field to exactly one category.

**CONNECTION TO SYSTEM**
This chapter takes Chapter 4's single deletion test and splits it into the four-question procedure above — the exact tool you'll use in Chapter 37 to design real multi-tenant memory scoping.

**NEXT**
Chapter 7 — The Edge and the Client Contract. Where goals enter, approvals arrive, progress leaves — and the three ways teams accidentally put a loop into a layer that's supposed to hold nothing.

Say "next" when you're ready.
