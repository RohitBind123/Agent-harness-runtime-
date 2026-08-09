```
  Level 3 · Chapter 25
  THE WORLD MODEL
  Requires   C11 The Context System, C12 The Memory System,
             C14 The Tool Execution Engine, C22 The Event Spine,
             C24 The Task Graph
  Unlocks    C26 Planning Algorithms, C31 Safety and Sandboxing,
             C34 Observability
  Diagrams   Core (5)
```

# Chapter 25 — The World Model

---

## 1. Motivation

### 1.1 Cold open

Atlas is asked to add a `currency` field to the checkout API's response. At session start it builds a
repository map of `payments-api`: modules, entry points, and where response shapes are defined. The
map takes ninety seconds and says response shapes live in `api/serializers.py`.

That was true when the map was built.

Twenty minutes into the session, Atlas completes an unrelated refactor step from the same plan — a
cleanup the issue asked for — which moves response shapes out of `api/serializers.py` and into
`api/schemas/response.py`. The map is not rebuilt, because rebuilding it costs ninety seconds and
nothing signalled that it needed to be.

Forty minutes in, Atlas adds `currency` to `api/serializers.py`. The file still exists. It still has
a class with the right name. It has tests, and they pass, because the tests import it directly. What
no longer exists is any code path from the running service to that file.

The pull request is well-formed. The diff is correct in isolation. Review approves it. The field
does not appear in the API, and the ticket is reopened four days later by a customer.

Nothing failed. No tool errored, no assertion tripped, no budget was exceeded. The run acted on a
belief that had been true, that it had itself made false, and that it had no mechanism for
doubting.

### 1.2 In plain language

Before a run can do anything useful it has to know things about the place it is working in: what
files exist, which service talks to which, whether the test suite is currently green, what the
database schema looks like. Call that collection of knowledge a world model — beliefs about an
environment the runtime does not control.

The obvious way to get a belief is to look. Read the directory, run the query, call the health
endpoint. That is always correct, and for cheap questions it is the right answer and there is
nothing more to say.

Some questions are not cheap. Working out how a large repository fits together can take minutes.
Doing that before every step would cost more than the work. So the answer gets kept and reused —
and the moment an answer is kept rather than re-derived, it can be wrong, because the world does not
consult you before changing.

The hard part is not gathering these beliefs. It is knowing when to stop trusting one. And the most
common reason a belief goes bad is not that somebody else changed something. It is that the run
changed it, itself, three steps ago, and had no way to connect the change it made to the belief it
was holding.

### 1.3 Why this chapter exists, and what it does not claim

This is the most speculative chapter in the book, and it opens by saying so.

Everything in Chapters 21 through 24 rests on a specification or a paper. This chapter does not. The
source material has essentially nothing to say about environment representation, and the systems
shipping today mostly do not have a world model in any recognisable sense — they have a repository
map, sometimes a cached directory listing, and otherwise they look things up when they need them.
Almost every claim here is tagged `[INF]` or `[FUT]`, and the few `[BP]` claims are borrowed from
caching and configuration management rather than from agent systems.

It is included for two reasons.

First, because the failure in §1.1 is real and common, and it is currently handled by convention
rather than by design. Teams discover it, add an ad-hoc "rebuild the map after a refactor" rule, and
then discover the next case. Naming the problem is worth doing even where the solution is unsettled.

Second, because there is one part of this that is not speculative at all: **the invalidation signal
already exists**. Chapter 22 made every effect durable and ordered. Chapter 14 tagged every tool as
pure or effectful. A system with both of those already has everything it needs to know which beliefs
have been undermined, and mostly does not use it. That specific claim is defensible today.

A reader who takes nothing else from this chapter should take the negative result: **the default
should be to not have a world model.** Look it up. A cache over the environment is justified by a
measured cost, and a team that has not measured that cost is carrying a correctness risk to solve a
problem it has not confirmed it has.

### 1.4 What previous framings got wrong

**"The world model is the agent's memory of the environment."** Chapter 12's memory subsystems store
what a run learned that is worth keeping. Beliefs about the environment are not that. A memory
entry is a claim about the past and stays true — "this repository's tests were flaky in March" is
permanently true of March. A belief is a claim about the present and expires. Filing environment
facts in a memory store produces a system that confidently reports last month's directory structure,
and the store has no vocabulary for saying it should not.

**"Staleness is a time-to-live problem."** A TTL encodes the assumption that a fact's lifetime is a
function of the clock. Here it is a function of what happened. A repository map is valid for six
months in a quiet repository and invalid four seconds after a refactor, and no TTL is right for
both. Time-based expiry is not useless — it is a floor, a backstop against invalidation signals you
failed to wire — but as the primary mechanism it is guessing.

**"More context is a better world model."** Loading the whole repository into context is not a world
model; it is the absence of one, paid for at Chapter 11's rates on every call. A world model exists
to answer a question in a few hundred bytes that would otherwise cost a hundred kilobytes, and a
design that grows context is failing at the only thing it was for.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A world model is the mental map an engineer builds in their first week on an unfamiliar codebase.
They read for a few days, form a picture of where things live and what calls what, and then work
from the picture rather than re-reading. The picture is not the code; it is a lossy, useful summary
that makes every subsequent question cheaper.

The analogy carries the useful parts: the picture is built by exploration, it is worth the
investment, it is specific to this codebase, and it decays.

Here is where it stops.

A human holding a stale picture has a felt sense of friction. The file is not where they expected.
The function has a parameter they do not recognise. Something is *off*, and that feeling is a
signal — it triggers re-reading, asking someone, checking git log. The correction loop is driven by
discomfort, and discomfort is what a person gets for free when reality and belief disagree.

A runtime holding a stale belief has no such signal. `api/serializers.py` existed. The class was
there. The edit applied cleanly. Every observable outcome was consistent with the belief being
correct, because a stale belief is not usually a belief about something that has vanished — it is a
belief about something that is still present and no longer load-bearing. There is no friction to
notice, and so there is no correction.

That is the whole design constraint. **Because the runtime cannot feel doubt, doubt has to be
mechanically produced.** Every subsequent section is a way of manufacturing the signal a human
would have had for nothing.

### 2.2 Why a world model must exist

```
  (1) A step needs an environment fact: where response shapes live.

  (2) Cheapest correct answer: look it up now. Read the directory,
      grep the source. Always available, always current, and for
      cheap questions this is the end of the discussion.

  (3) Some lookups are not cheap. Deriving module structure across
      400k lines takes ~90 s. Forty steps, forty derivations, and
      the lookups cost more than the work they inform.

  (4) So the answer is kept and reused. That store of kept answers
      IS a world model, whether or not anyone names it. Note that
      nobody decided to have one; it appeared as soon as a lookup
      was too expensive to repeat.

  (5) A kept answer needs an expiry rule. Time is the available
      default and is wrong here: a repository map survives six
      months of quiet and dies four seconds after a refactor. The
      lifetime is not a function of the clock.

  (6) It is a function of what happened. And what happened is not
      hidden -- the runtime performed most of it, through tools
      the registry already tags as effectful (C14).

  (7) So the invalidation signal is the effect stream, not a timer.
      That stream is already durable and ordered, because C22 made
      it so for unrelated reasons.

  (8) Therefore the world model is a projection over the event log,
      not an independent store. It is rebuildable from events, it
      may be deleted at any time, and deleting it costs latency and
      never correctness.
```

Step (8) is the load-bearing conclusion, and it is worth stating on its own: **a world model must be
disposable.** If deleting the whole thing loses information, it is not a world model, it is a
database of record with no owner, and Chapter 6's state categories say it should not exist.

### 2.3 A belief is a fact plus three pieces of bookkeeping

The single most consequential design decision here is not what to store but what to store *around*
it. A world model implemented as a dictionary of facts cannot be invalidated, because invalidation
needs to ask questions the dictionary cannot answer.

Every belief carries four fields, and the last three are what make the first usable.

| Field | Example | Why it must be there |
|---|---|---|
| **Claim** | `response shapes live in api/schemas/` | The fact itself; useless alone. |
| **Provenance** | `derived by module_map probe at step 3` | Says how to re-derive it, and how much to trust it. |
| **Observed at** | `2026-03-14T09:02:11Z, event seq 4471` | An event sequence, not only a wall clock — this is what lets an effect be compared against a belief. |
| **Scope** | `paths under api/` | What set of things the claim covers, which is what an invalidation event is matched against. |

Scope is the field teams leave out and then need. Without it, an effect on `api/schemas/response.py`
can only be matched against beliefs by exact key, so it invalidates nothing, or by a blunt "any
write invalidates everything", which throws away the entire map on every edit and returns the system
to §2.2 step (3). Scope is what makes selective invalidation possible, and selective invalidation is
what makes the cache worth having.

### 2.4 The mental model to carry

The world model is a projection over the effect stream, holding beliefs that are too expensive to
re-derive, each tagged with how it was obtained and what it covers. Its correctness rests entirely
on one loop: an effect happens, its scope is matched against beliefs, and the overlapping ones stop
being trusted. Everything else is caching detail.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +~~~~~~~~~~~~~~~~~~~~~~+       +~~~~~~~~~~~~~~~~~~~~~~+
   |  Repository / VCS    |       |  Deployed services   |
   +~~~~~~~~~~~~~~~~~~~~~~+       +~~~~~~~~~~~~~~~~~~~~~~+
              ^                              ^
              | (1) probe                    | (1) probe
              |                              |
   +----------------------------------------------------+
   |                   PROBE REGISTRY                   |
   |   named, costed, re-runnable environment queries   |
   +----------------------------------------------------+
              | (2) belief + provenance + scope
              v
   +----------------------------------------------------+
   |                   BELIEF STORE                      |
   |            [[ beliefs ]]   disposable               |
   +----------------------------------------------------+
        ^                |                    ^
        |                | (4) fresh beliefs  | (3) invalidate
        |                |     only           |     by scope
        |                v                    |
        |     +--------------------+   +-------------------+
        |     |  Context assembler |   |   Invalidator     |
        |     |       (C11)        |   +-------------------+
        |     +--------------------+            ^
        |                                       | effects, in order
        |                                +------+------------+
        +--------------------------------|   Event spine     |
          (5) re-probe on demand         |      (C22)        |
                                         +-------------------+

  Figure 25.1 -- The world model in its surroundings (D1 High-Level
                 Architecture)

  (1) probes read the environment; they never write to it
  (2) a belief is stored with provenance and scope, never bare
  (3) the ONLY input that removes trust; see section 5
  (4) a stale belief is never handed to the assembler -- it is
      re-probed or omitted, and omission is an acceptable outcome
  (5) re-probing is initiated by the reader, not by a background job
```

Three properties of this picture are decisions rather than drawings.

**Probes only read.** A probe that writes is a tool, and it belongs behind Chapter 14's gate with an
effect tag. Keeping this line sharp is what allows probes to be run freely, in parallel, and
speculatively — none of which is safe for something that can act.

**The invalidator is downstream of the event spine, not of the tool engine.** It reacts to committed
effects, in order, rather than to tool calls as they are issued. This costs a little latency and
buys the property that the world model can be rebuilt by replaying the same events, which is what
makes it disposable in the sense of §2.2 step (8).

**Nothing refreshes in the background.** There is no daemon keeping beliefs warm. A stale belief is
re-probed when someone asks for it and not before, because a background refresher does work for
beliefs that will never be read, and — worse — hides staleness by making the store look healthy
while the freshness that matters is the freshness at the moment of use.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                        WORLD MODEL                             |
   |                                                                |
   |  +-------------------------+   +---------------------------+   |
   |  |     Probe registry      |   |      Belief store         |   |
   |  |                         |   |                           |   |
   |  |  name                   |   |  claim                    |   |
   |  |  cost_estimate_ms       |   |  provenance (probe name)  |   |
   |  |  scope_produced         |   |  observed_at_seq          |   |
   |  |  fn() -> Belief         |   |  scope (path/service set) |   |
   |  |                         |   |  status                   |   |
   |  |  registered, not        |   |                           |   |
   |  |  invented per call      |   |  disposable; rebuildable  |   |
   |  +-------------------------+   +---------------------------+   |
   |                                                                |
   |  +-------------------------+   +---------------------------+   |
   |  |      Invalidator        |   |    Freshness policy       |   |
   |  |                         |   |                           |   |
   |  |  effect -> scope        |   |  per-probe max age, as a  |   |
   |  |  scope overlap ->       |   |  BACKSTOP only            |   |
   |  |    mark SUSPECT         |   |                           |   |
   |  |  unknown scope ->       |   |  read of a SUSPECT belief |   |
   |  |    mark ALL suspect     |   |  forces re-probe or omit  |   |
   |  +-------------------------+   +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 25.2 -- Inside the world model (D2 Low-Level Architecture)
```

### 4.1 The probe registry, and why probes are registered

A probe is a named, costed, re-runnable query against the environment. Registration is not
ceremony. It exists so that three things are knowable without executing anything:

- **What it costs.** A planner deciding whether to consult a belief or read a file directly needs
  the price. An unregistered probe has no price until it has been paid.
- **What scope it produces.** The invalidator matches effects against scopes. A probe that does not
  declare what it covers produces beliefs that can only be invalidated wholesale.
- **How to re-derive it.** A belief whose provenance names a registered probe can be refreshed
  automatically. A belief whose provenance is "somebody put this here" can only be deleted.

The registry is also where the honest answer lives for most questions. A probe with a cost of
40 ms should not have its result cached at all — the registry marks it `always_probe`, the belief
store never holds it, and the correctness risk of §1.1 is avoided by not taking it. **The most
valuable entries in the probe registry are the ones that say do not cache this.**

### 4.2 Four probe families, and their honest cost

`[INF]` The categories below are the ones that recur; the costs are illustrative of a mid-sized
service repository and are meant to convey ratios, not to be quoted.

| Family | Example | Typical cost | Cache? |
|---|---|---|---|
| **Structure** | Module map, import graph, where a symbol is defined | 30–120 s | Yes, and this is the family the chapter is about |
| **Point lookup** | Does this file exist; what is in this directory | 5–50 ms | No. Probe every time |
| **Liveness** | Is the test suite green; is the service healthy | 1–600 s | Only with an explicit, short backstop age |
| **Topology** | Which services call this one; what the schema is | minutes, often manual | Yes, and treat as low-confidence — this family is mostly `[FUT]` |

The point-lookup row is the one worth internalising. A large fraction of what teams put in a world
model belongs in that row, where the correct implementation is to read the filesystem and the
correct amount of machinery is none.

---

## 5. Invalidation, and the Runtime as Its Own Adversary

### 5.1 Where staleness actually comes from

The intuitive picture of staleness is external: somebody else merges to main, someone redeploys a
dependency, the world moves while the run is not looking. That happens, and it is the case every
caching discussion starts from.

It is not the dominant case here. In a session of any length, the largest source of environment
change is **the run's own effects**. A coding session's whole purpose is to modify the repository it
built a map of. It is a cache that systematically invalidates itself and is uniquely positioned to
know it.

That reframing produces the chapter's one non-speculative claim. The invalidation signal is not a
guess about how fast the world moves. It is the effect stream, which is already durable, already
ordered, and already tagged.

```
                                                             TIME VIEW

   step 3   probe:module_map  ---->  belief B1
                                     scope: api/**
                                     observed_at_seq: 4471
                                     status: FRESH

   step 7   edit_file(api/schemas/response.py)
                |
                | effect committed, seq 4502
                v
            +---------------------+
            |    Invalidator      |
            +---------------------+
                | scope of effect: api/schemas/response.py
                | overlaps scope of B1 (api/**)?  YES
                v
            B1.status := SUSPECT

   step 12  context assembler needs "where response shapes live"
                |
                +--> read B1: status is SUSPECT
                |
                +--> decision point:
                     |
                     +-- probe cost affordable?  ---> re-probe, B1 FRESH
                     |
                     +-- not affordable?         ---> OMIT the belief
                                                      and say so in context

   NOTE the branch that is missing: there is no path from SUSPECT to
   being used. A suspect belief is refreshed or withheld. It is never
   handed over with a caveat, because a caveat in context is advice
   and the model is free to disregard advice.

  Figure 25.3 -- An effect invalidating a belief the run itself made
                 false (D8 Control Flow)
```

### 5.2 The effect tag, doing a third job

Chapter 14 introduced the pure/effectful tag to decide whether a tool call needs a gate. Chapter 24
found that the same tag decides whether a branch may be raced by a `FIRST` join. Here it decides
whether a tool call can invalidate a belief.

Three consumers, one tag, and none of them was anticipated when it was cut. That is worth pausing
on, because it is the strongest available evidence that the pure/effectful boundary is a real seam
in the domain rather than an implementation convenience. Distinctions that keep turning out to
answer questions nobody asked them are usually load-bearing.

It also raises the stakes on Chapter 20 §5.5's containment argument. An evolution loop that re-tags
an effectful tool as pure does not merely remove a gate — it silently switches off belief
invalidation for everything that tool touches, and the resulting failure appears weeks later as a
wrong edit to a dead file. The tag was already outside the evolvable workspace. This is the third
independent reason.

### 5.3 Scope matching, and the honest fallback

Invalidation is a set-overlap test: does the scope of this effect intersect the scope of this
belief? For filesystem scopes that is prefix matching and is cheap. For service topology it is
membership in a named set. For anything else it is guesswork, and guesswork must fail in a specific
direction.

**An effect whose scope cannot be determined marks every belief suspect.** Not "leaves them alone" —
suspect. This is the expensive answer and it is the only safe one, because the alternative is a
class of effect that silently preserves beliefs it invalidated, which is §1.1 with extra steps.

The cost of that rule is real: a single unscoped effect can dump the whole map. Which is exactly why
it should hurt, and why the fix is to give effects scopes rather than to soften the rule. A tool
that cannot say what it touches is a tool whose blast radius is unknown, and Chapter 31 has a
stronger objection to it than this chapter does.

### 5.4 Confidence is not a substitute for staleness

A tempting design attaches a confidence score to each belief, decays it over time and on nearby
effects, and passes low-confidence beliefs to the model with a hedge attached: *this may be out of
date*.

It does not work, and the reason is worth being precise about. A hedge in context is a token
sequence competing with every other token sequence for influence. It is not a control. Chapter 30
makes the same argument about authority — a rule in the prompt is a request, a rule in the runner is
a constraint — and staleness is the same shape. The system either withholds the belief or it does
not; asking the model to weigh it appropriately is a design that works in testing, where the hedge
is unusual and salient, and stops working in production, where hedges are everywhere and carry no
information.

Confidence *is* useful for one thing: ranking which belief to re-probe first when the budget allows
only some. That is a scheduling use, internal to the world model, and it never reaches context.

### 5.5 Contradiction is a first-class outcome

Sometimes a belief is not stale but wrong — the probe misread, the environment was mid-deploy, two
probes disagree. The discipline that matters is what happens when a step's actual observation
contradicts a stored belief.

The wrong answer is to overwrite the belief and continue. That loses the fact that a contradiction
occurred, which is the single most valuable diagnostic this subsystem produces. A probe that is
regularly contradicted is a probe that should be deleted, and only the contradiction record tells
you which one.

The right answer: mark the belief stale, emit a `belief.contradicted` event with the probe name, the
stored claim, and the observation, and let the reader re-probe. Chapter 34 counts those events per
probe. A probe with a rising contradiction rate is not a bug to be fixed in place — it is usually a
probe whose family (§4.2) is wrong, most often a structure probe caching something that belonged in
the point-lookup row.

---

## 6. Runtime Sequence

The trace below is §1.1 executed correctly. The plan is unchanged, the refactor still happens, and
the outcome differs at exactly one point.

```
                                                             TIME VIEW

  t   Run                    World model             Belief B1
  --  ---------------------  ----------------------  -----------------
  0   session start
  1   probe:module_map ----> derive, 90 s            FRESH
                             scope api/**            seq 4471
  2   plan minted (C24)
  3   step: read config
  4   step: refactor
        edit api/schemas/
        response.py
  5                          effect seq 4502
                             scope overlap -> yes    SUSPECT
  6   step: add currency
        needs "where do
        response shapes
        live?"
  7                          read B1 -> SUSPECT
                             probe cost 90 s
                             remaining budget 22 min
                             -> affordable, re-probe
  8                          derive, 90 s            FRESH
                             api/schemas/            seq 4507
  9   edit api/schemas/
        response.py  <---- correct file
 10   tests pass, PR opened, field appears in the API

  FAILURE BRANCH -- at t=7, budget remaining is 40 s and the probe
  costs 90 s:

      B1 is NOT handed over. It is omitted from context entirely.
      The step proceeds without a structural belief, and the model
      does what it does with no map: it searches. That is slower and
      it is correct.

      The run emits << belief.withheld probe=module_map reason=budget >>
      which is the signal that the cost model needs revisiting -- a
      belief the run could not afford to refresh AND could not afford
      to be wrong about is a probe in the wrong family (4.2).

  Figure 25.4 -- The cold open, run correctly, with the budget-exhausted
                 branch (D4 Sequence)
```

The failure branch is the part worth defending, because omitting a belief looks like a regression.
It is not. The comparison is not "map versus no map"; it is "no map versus a map that is wrong in a
way nothing downstream can detect". Searching costs minutes. The cold open cost four days and a
customer's trust, and it presented as a successful run the entire time.

---

## 7. State Management

```
                                                            STATE VIEW

      {{ absent }}
           |  probe runs, belief stored with scope + seq
           v
      {{ fresh }}
           |                                    \
           | effect overlapping scope,           \  max_age exceeded
           | or unscoped effect (5.3)             \ (backstop only)
           v                                       v
      {{ suspect }} <-----------------------------+
           |
           +---- read + budget allows re-probe ----> {{ fresh }}
           |
           +---- read + budget denies re-probe ----> withheld;
           |                                         belief stays
           |                                         {{ suspect }}
           |
           +---- observation contradicts it -------> {{ stale }}
                                                          |
      {{ stale }} --- explicit re-probe only -----> {{ fresh }}
           |
           | store pressure / session end
           v
      {{ absent }}

      ILLEGAL: {{ suspect }} -> {{ fresh }} by anything except a probe
      actually running. Not by a timer, not by a read, not by a step
      completing without incident. Nothing restores trust except
      re-derivation.

      ILLEGAL: any state -> handed to the context assembler, unless
      that state is {{ fresh }}. There is no "used with a caveat"
      path (5.4).

  Figure 25.5 -- Belief states (D6 State Diagram)
```

### 7.1 Why suspect and stale are different states

`suspect` means *something happened that may have invalidated this*. `stale` means *we have
positive evidence this is wrong*. Collapsing them loses the distinction between a belief that will
probably survive a re-probe and one that certainly will not, and that distinction drives two
different decisions: whether to re-probe eagerly, and whether to record a contradiction against the
probe (§5.5).

There is also a blunt operational reason. The ratio of suspect-to-fresh transitions to
contradiction events is a direct measure of whether scope matching is too broad. Lots of suspicion
and almost no contradictions means the invalidator is throwing away beliefs that were fine, which is
a tuning problem with a number attached. One state cannot produce that ratio.

### 7.2 The store owns nothing

Chapter 6 sorted state into four categories, and the belief store falls squarely into the derived
category: rebuildable, disposable, never the record of anything. That has a testable consequence,
and it belongs in the test suite rather than in a design document — **delete every belief mid-run
and the run must still complete correctly, only slower.** If it cannot, something has been filed
here that belongs in run state or in memory, and it should be moved before the next incident finds
it.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class Probe(Protocol):
    """A named, costed, read-only query against the environment."""

    name: str
    cost_estimate_ms: int
    scope_produced: str          # e.g. "api/**" or "service:checkout"
    cacheable: bool              # False means: never store the result

    def run(self, env: "Environment") -> "Belief":
        """Derive a belief. May be slow. Must not mutate anything."""


class WorldModel(Protocol):

    def get(self, probe_name: str, budget_ms: int) -> "Belief | None":
        """Return a FRESH belief, or None.

        If the stored belief is SUSPECT or STALE, re-probe when
        `budget_ms` allows and return the fresh result. When it does
        not allow, return None and emit belief.withheld. Never returns
        a non-fresh belief, with or without a caveat attached.
        """

    def invalidate(self, effect_scope: str | None, seq: int) -> int:
        """Mark every belief whose scope overlaps `effect_scope` as
        SUSPECT. A None scope marks ALL beliefs suspect -- the safe
        direction, deliberately expensive (5.3).

        Returns the number marked, which is the metric Chapter 34
        graphs against contradiction count.
        """

    def contradict(self, probe_name: str, observed: object) -> None:
        """Record that a direct observation disagreed with a stored
        belief. Marks it STALE and emits belief.contradicted. This is
        the subsystem's most valuable diagnostic; never make it a
        silent overwrite (5.5).
        """
```

The signature that carries the argument is `get`, in two respects. It takes a budget, because
whether to re-derive is a cost decision and the caller is the only party that knows what it can
afford. And it returns `Belief | None` rather than a belief with a freshness field, because a
freshness field is an invitation to use the belief anyway — an optional return makes "not available"
the thing the caller must handle, which is the outcome §5.4 argues must not be papered over.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class BeliefStatus(str, Enum):
    FRESH = "fresh"
    SUSPECT = "suspect"
    STALE = "stale"


@dataclass(frozen=True)
class Belief:
    probe_name: str              # provenance: how to re-derive
    claim: dict                  # the fact itself
    scope: str                   # what it covers; drives invalidation
    observed_at_seq: int         # event-log position, not wall clock
    observed_at: str             # wall clock, for humans only
    status: BeliefStatus
    max_age_s: int | None        # backstop, never the primary rule
```

Two columns encode the chapter's arguments.

`observed_at_seq` is an event sequence number, and it is the reason the invalidator can be correct.
Comparing a belief's wall clock against an effect's wall clock across two machines is a distributed
clock problem with no good answer; comparing two positions in the same durable log is unambiguous.
Chapter 32 depends on this more heavily than this chapter does.

`max_age_s` is nullable and most probes should leave it null. A non-null value is a statement that
this belief can go bad without any effect in this system causing it — an externally-mutated
resource. When most beliefs in a store carry a max age, the invalidation wiring is not being trusted,
and the right fix is upstream in scope declaration rather than in shorter timeouts.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Event spine | Invalidator | Ordered consumption of committed effects | Effect scope + sequence |
| Context assembler | World model | Synchronous `get` with a budget | Probe name |
| World model | Environment | Probe execution, read-only | Whatever the probe reads |
| World model | Event spine | Outbox rows | `belief.contradicted`, `belief.withheld` |
| World model | Planner | Nothing, directly | — |

The last row is the interesting one. The planner does not consult the world model, and this is
deliberate: beliefs reach the planner the same way everything else does, through assembled context
under Chapter 11's budget. Giving the planner a private channel to the belief store would create a
second path by which environment facts enter a decision, one of them unbudgeted and untraced, and
Chapter 16 would then be unable to reconstruct what the planner could see.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Belief invalidated by the run's own effect, unnoticed | None at the time — this is §1.1 | Prevented structurally: the invalidator consumes the effect stream, not a timer |
| Effect with undeterminable scope | Scope resolver returns `None` | Mark all beliefs suspect; alert on the rate, because a rising rate means tools are being added without scope declarations |
| Probe regularly contradicted | `belief.contradicted` count per probe | Usually a probe in the wrong family (§4.2); move to point-lookup or mark `cacheable = False` |
| Re-probe unaffordable at point of use | `belief.withheld` event | Run continues without the belief, slower; a persistent rate means the probe's cost and the step's budget are mismatched |
| Belief store lost entirely | Cache miss rate | No recovery needed; re-probe on demand. If anything else breaks, §7.2's test was never run |
| Two probes producing overlapping, disagreeing claims | Contradiction between beliefs, not against an observation | Delete one. Overlapping probes are a design error and reconciling them at read time is how a world model becomes a database |
| Background refresher hiding staleness | Absence of `belief.withheld` events despite long sessions | Do not have a background refresher (§3) |

The second row deserves a threshold rather than a shrug. `[BP]` Alert when the fraction of effects
with undeterminable scope exceeds a small percentage of all effects over an hour. That number
degrades quietly as tools are added, and by the time it is visible in outcomes it has been climbing
for months.

---

## 12. Scalability

**Probe cost is the only real scaling axis.** The belief store is small — hundreds of rows per
session, not millions — and its query load is trivial. Everything that hurts is on the probe side.

**Structure probes scale with the repository, not with traffic.** A module map over 400k lines
costs the same whether one run or a hundred are active, and the correct response is to share it: the
same repository at the same commit yields the same map, so key the belief by `(repo, commit_sha)`
and let every run at that commit reuse it. That turns the worst probe in the system from per-session
to per-commit, which is the largest single win available here and is available on day one.

Sharing across runs has one condition, and it is the whole reason it is safe: the key includes the
commit. A run that has made uncommitted edits has diverged from the shared belief, and its own
invalidator has already marked its copy suspect. Shared beliefs are read-only and per-commit;
per-run divergence is tracked per run.

**Invalidation is O(beliefs) per effect in the naive form**, which is fine at hundreds of beliefs
and stops being fine if a design ever grows to thousands. Prefix-indexed scopes make it
logarithmic. Reaching that point is more likely a signal that too much is being cached than a
signal that an index is needed.

---

## 13. Production Engineering

### 13.1 The four numbers

- **Probe cost, measured, per probe.** The registry's `cost_estimate_ms` must be checked against
  reality, because every budget decision in §8 is made against the estimate. An estimate that has
  drifted low turns "affordable" into a timeout.
- **Contradiction rate per probe.** The one number that says a belief is not merely stale but
  wrong. Rising means the probe is in the wrong family.
- **Suspect-to-contradiction ratio.** Broad scopes produce lots of suspicion and few contradictions.
  Narrow ones produce the reverse, which is worse. Tune towards a small but non-zero contradiction
  rate; zero contradictions across a large corpus usually means the invalidator is too aggressive
  and the cache is doing nothing.
- **`belief.withheld` rate.** Every occurrence is a step that ran with less information than the
  system had available. Some are correct trades. A rising rate is a cost-model failure.

### 13.2 The review question

For any proposed addition to the belief store: **what effect, in this system, makes this false — and
is that effect's scope declared?**

If the answer to the first half is "nothing we do", the fact belongs in configuration, not here. If
the answer to the second half is no, the addition should be blocked until the tool declares a scope,
because an undeclarable scope means every write invalidates it anyway (§5.3) and the cache will
never hit.

### 13.3 Teaching this to a new engineer

Show them §1.1 and ask where the bug is. Nearly everyone says the map should have been rebuilt after
the refactor. Then ask *what would have told it to*, and watch the answer arrive: the system already
knew, because it did the refactor. The gap was never information. It was that nobody had connected
the effect stream to the cache, and both had existed the whole time.

---

## 14. Relation to AHE

`[AHE]` The source has no world model and does not need one: its benchmark tasks are self-contained,
and the harness under evolution is small enough to read whole. That is a property of the evaluation
setting, not a general result, and it is why this chapter cannot lean on it.

`[INF]` Where the two connect is the invalidation argument. An evolution loop that edits the harness
is doing exactly what §5.1 describes — modifying the environment it holds beliefs about — one level
up. Any cached analysis of the harness (its module structure, its tool inventory, its measured
costs) is invalidated by the loop's own commits, and the loop has the same access to its own effect
stream that a run has to its own. The failure mode is identical and arrives with more leverage,
since a stale belief about the harness misdirects every subsequent trial rather than one step.

`[INF]` Chapter 20 §5.5's containment list gains its third entry-by-implication here. The effect tag
protects the gate, the race eligibility, and — as §5.2 argues — belief invalidation. A single
mis-tag now has three distinct blast radii, which raises the argument for keeping it outside the
evolvable workspace from strong to close to unarguable.

---

## 15. Industry Perspective

**`[BP]` Cache invalidation by event rather than by TTL is settled practice elsewhere.** Write-
through invalidation, change-data-capture, and cache-key versioning all encode the same insight:
expire on what happened, not on how long ago. The transfer to agent runtimes is not novel; the
observation that the runtime generates most of its own invalidating events is what is specific here.

**`[DAR]` The ordered, durable effect stream is the one piece of this chapter that is specified
rather than inferred.** The outbox guarantees that every committed state change has exactly one
corresponding record, in order, with a sequence number. This chapter adds no requirement to that
contract; it consumes it. A team that has already built the spine has already built the hard half of
belief invalidation and can wire it in an afternoon.

**`[BP]` Configuration management systems learned the probe/apply split decades ago.** Puppet's
facts and Ansible's gathered variables are probes in this chapter's sense: named, read-only,
re-runnable, and separate from the things that change state. That separation is worth copying
wholesale, including its strictness.

**`[INF]` Retrieval systems are not world models and the confusion is expensive.** A vector index
over a repository answers "what is similar to this query" and is refreshed on ingestion. A world
model answers "what is currently true" and is invalidated on effect. Systems that serve the second
question from the first inherit the index's refresh cadence as their staleness bound, which is
usually minutes to hours and is unrelated to when the fact actually changed.

**`[FUT]` Shared, commit-keyed structure probes are the obvious next step and are rare.** The
economics are compelling (§12) and the correctness argument is simple. The reason it is uncommon
appears to be that most systems have not separated provenance from claim, and without provenance
there is no safe key.

**`[FUT]` Everything about service topology in this chapter is a sketch.** Repository structure is
tractable because the ground truth is a filesystem. "Which services call this one" has no
equivalently cheap authority, and the honest current answer is a hand-maintained document that is
wrong in a way nobody measures. This is the least solved area in the book.

---

## 16. Key Takeaways

1. **The default is to look it up.** A world model is a cache over the environment, and a cache is
   justified by a measured cost. Most facts teams put in one belong in a 20 ms filesystem read.
2. **The hard problem is invalidation, not acquisition.** Gathering beliefs is engineering.
   Knowing when to stop trusting one is the design.
3. **The dominant source of staleness is the run itself.** A coding session's purpose is to change
   the repository it mapped. It is a cache that systematically invalidates itself and is uniquely
   positioned to notice.
4. **The invalidation signal already exists.** Durable, ordered effects (Chapter 22) plus the
   pure/effectful tag (Chapter 14) is everything needed. Most systems have both and wire neither.
5. **A bare fact cannot be invalidated.** Store provenance, an event-log position, and a scope
   alongside every claim; scope is what makes invalidation selective rather than total.
6. **Never hand over a stale belief with a caveat.** A hedge in context is a token sequence, not a
   control. Re-probe or withhold — and withholding is an acceptable outcome that costs time and
   never correctness.
7. **Deleting the whole store must cost only latency.** Put that in the test suite. If anything
   breaks, something is filed here that belongs in run state or in memory.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **World model** | A disposable cache of beliefs about an environment the runtime does not control, justified only by the cost of re-deriving them. | `[INF]` | Ch 26, Ch 31 |
| **Belief** | A claim plus its provenance, its event-log position, and the scope it covers — the last three being what make invalidation possible. | `[INF]` | Ch 26 |
| **Probe** | A named, costed, read-only query that derives a belief and can always be re-run to refresh it. | `[INF]` | Ch 31, Ch 40 |
| **Scope** | The set of things a belief covers or an effect touches, matched by overlap to decide what an effect invalidates. | `[INF]` | Ch 31 |
| **Self-invalidation** | The dominant staleness case, in which the run's own committed effects make its own beliefs false. | `[INF]` | Ch 34 |
| **Suspect** | The state of a belief that an overlapping effect may have invalidated, from which nothing but an actual re-probe restores trust. | `[INF]` | Ch 34 |
| **Contradiction** | A direct observation disagreeing with a stored belief, recorded as an event rather than silently overwritten, and the subsystem's best diagnostic. | `[INF]` | Ch 34, Ch 41 |
| **Withholding** | Omitting a belief the runtime cannot afford to refresh, on the grounds that no map beats a wrong map nothing can detect. | `[INF]` | Ch 29 |
| **Backstop age** | A maximum age used only as a safety net behind event-driven invalidation, never as the primary expiry rule. | `[BP]` | Ch 33 |
| **Commit-keyed sharing** | Reusing an expensive structure probe across every run at the same repository commit, which is safe precisely because the key names the commit. | `[FUT]` | Ch 33 |

---

**Next:** Chapter 26 — *Planning Algorithms.* Chapter 10 gave the planner a contract and Chapter 24
gave it a data structure; this chapter is about what actually goes inside. Decomposition strategies,
tree search and when its cost is repaid, contract-first planning, and the distinction that matters
most in production — whether a surprise calls for repairing the plan you have or minting a new one.
