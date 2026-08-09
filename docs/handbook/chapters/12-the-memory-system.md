```
  Level 2 · Chapter 12
  THE MEMORY SYSTEM
  Requires   C6 State Separation, C10 The Planner, C11 The Context System
  Unlocks    C16 The Observation System, C25 The World Model,
             C37 Tenancy and Data Governance, C43 Component Observability,
             C46 The Evolve Agent
  Diagrams   Full (9)
```

# Chapter 12 — The Memory System

---

## 1. Motivation

### 1.1 Cold open

Atlas spends fifty minutes on an integration test in `acme/checkout`. It fails, passes on retry,
fails again, and eventually passes. The run completes successfully.

Before finishing, the harness records what it learned, exactly as designed:

```text
Integration tests in this repository are unreliable. If
test_checkout_flow fails, re-run it; a second failure can be ignored.
```

Six weeks later a genuine regression lands in the checkout flow. `test_checkout_flow` fails. Atlas
re-runs it. It fails again. Atlas notes that a second failure can be ignored and opens a pull
request describing the change as verified.

The note was written from a real observation and was wrong about the cause. The test had been
unreliable that afternoon because a shared staging database was mid-migration. It was not unreliable
in general. Nothing re-examined the conclusion, because nothing in the system was capable of
re-examining it: a written note is true by default, forever, until a person deletes it.

Long-term memory is among the highest-value components in the ablation `[AHE §4.4.1]`, and it is the
only component a run edits from the inside. Those two facts are the same fact.

### 1.2 In plain language

"Memory" in an agent system means four different things, and treating them as one is how systems get
into trouble.

**Short-term memory** is what the model can see on this one call — the context from Chapter 11. It
lasts for the duration of a single request and then it is gone.

**Episodic memory** is the record of what actually happened: which steps ran, what they returned,
what the model said. It is written for every run and read by people and by debugging tools, but it
is never fed back into a running job.

**Procedural memory** is how to do a kind of task — the packaged procedures Chapter 1 called skills.
Somebody writes them deliberately; a run does not.

**Long-term memory** is facts the system learned and wants to keep: this repository needs that
environment variable, this customer prefers small pull requests. It is the only one of the four that
a run writes to itself, while it is running, based on what it concluded from the work it did.

That last sentence is the whole chapter. Everything valuable about long-term memory and everything
dangerous about it comes from the same property: the system is drawing its own conclusions and
keeping them. A conclusion that was right becomes a permanent advantage. A conclusion that was
wrong — the cold open — becomes a permanent defect, applied confidently, to every future run.

### 1.3 Why this chapter exists

Chapter 11 built the component that decides what the model sees on one call. This chapter builds one
of its sources, and it is the source that behaves least like the others.

Every other source of context is a read of something a person or the runtime wrote. Long-term memory
is a read of something a *previous run* wrote. That closes a loop inside the harness, forty chapters
before Level 5 closes the outer one, and it inherits the same problems in miniature: attribution,
staleness, and the impossibility of noticing you have learned something false.

The measurement makes it unavoidable. `[AHE §4.4.1]` swapped each component into a minimal baseline
in isolation; long-term memory carried one of the largest single gains while the system prompt alone
regressed. `[INF]` Building an agent system without long-term memory is leaving the largest measured
single-component gain on the table. Building it without the controls in §5 is the cold open.

### 1.4 What previous framings got wrong

**"Memory means a vector database."** The most expensive reflex in this chapter. Semantic retrieval
answers "what is similar to this?" and long-term memory needs to answer "what do I know about this
repository?" — a question with a small, enumerable, human-readable answer. §2.4 argues the file, and
§11 catalogues what the vector store gets wrong.

**"More memory is better."** Every entry is paid for on every call (Chapter 11 §2.3) and competes
for the same budget. An unbounded memory is a junk drawer that also happens to be authoritative.

**"A memory is a fact."** It is a *claim*, written by a model, from one observation, with no
statistical basis. The cold open is what happens when the system's data model cannot express the
difference.

**"Write memories at the end of a successful run."** Reasonable and insufficient. The cold open's run
succeeded. Success is not evidence that the lesson drawn from it was correct.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A field engineer's notebook.

An engineer who services equipment across many sites carries several distinct kinds of note, and
never confuses them.

There is **what is on the bench right now** — the readings taken in the last ten minutes, held in
their head, discarded when they pack up. There is the **job log**: what was done at each site, on
each visit, filed and occasionally consulted when something goes wrong. There is the **manual**: the
standard procedure for servicing this class of machine, written by the manufacturer, revised
deliberately and rarely. And there is the **notebook of hard-won specifics**: *the unit at the
Croydon depot has a sticking relay, tap it before testing.*

Four kinds, four lifetimes, four authors. The bench readings are theirs and momentary. The job log
is a record, not an instruction. The manual is somebody else's, and authoritative. The notebook is
theirs, accumulated, and the most valuable thing they own — the reason a ten-year engineer is worth
more than a competent new one.

The notebook is also the one that can go quietly wrong. A note written after a bad afternoon can
encode a coincidence as a rule.

**Where the analogy breaks**, and it breaks in the place that matters most. A human engineer carries
their notes with *doubt attached*. They remember writing that line, they remember they were tired,
and when the relay behaves differently twice they revise it. The note in their head has a
provenance, a confidence, and an implicit expiry, none of which are written down.

A file has none of that. Everything in it reads as equally true, equally current, and equally
well-founded. Nothing in the system carries the memory of having been unsure. That is precisely the
gap the cold open fell into, and it is why §9 puts confidence, provenance, and evidence count into
the data structure: what a human carries implicitly, this system must carry explicitly or not at
all.

### 2.2 Why four subsystems and not one

The word "memory" is doing four jobs, and the four differ on every axis that matters:

```
  1. Something must hold what the model sees on THIS call. It lives
     for one request and is rebuilt every time. (Ch 11)
  2. Something must record what actually happened, for people and for
     debugging. It is durable, and it is never fed back into a live
     run -- that would make a record into an instruction.
  3. Something must hold how to perform a class of task. It is
     authored deliberately, reviewed, and versioned.
  4. Something must hold facts learned along the way, so that run 900
     does not repeat the mistake of run 4.
  5. Those four have different lifetimes (one call / forever / per
     release / until contradicted), different owners (context system /
     observation / humans and the evolve loop / the run itself), and
     different state categories (model / run / harness / harness).
  6. Critically, only ONE of them is written from inside a run. That
     one can be wrong in a way the other three structurally cannot.
  7. If all four share a name, you cannot say which one leaked, which
     one went stale, or which one to fix. The Ch 6 cold open is a
     tenancy failure in exactly one of them.
  8. Therefore four names, four owners, four sets of rules.
```

Step 6 is why this chapter spends most of its length on one of the four. Short-term memory is
Chapter 11. Episodic memory is Chapter 16. Procedural memory is skills, built in Chapter 14 and
edited in Chapter 46. Long-term memory is here, because it is the one with a write path from inside
a run.

### 2.3 The four, side by side

| | Short-term | Episodic | Procedural | Long-term |
|---|---|---|---|---|
| Holds | this call's context | what happened | how to do a task | learned facts |
| Lifetime | one model call | forever | per release | until contradicted |
| Written by | context system | observation system | humans, evolve loop | **a run, itself** |
| Read by | the model | people, debuggers | the context system | the context system |
| Category (Ch 6) | model state | run state | harness state | harness state |
| Fed back into a live run? | it *is* the run | **never** | yes | yes |
| Chapter | 11 | 16 | 14, 46 | **this one** |
| Can be wrong forever? | no | no | yes, but reviewed | **yes, unreviewed** |

`[INF]` The "never" in row six is worth defending. It is tempting to feed a previous run's trajectory
into a current run as evidence — it is right there, and it is relevant. Do not: a trajectory is a
record of what happened, including everything the model got wrong along the way, and pushing it into
a live context re-teaches the errors alongside the successes. The distilled, deliberate output of
episodic material is a long-term memory entry, and it goes through §5's write path like everything
else.

### 2.4 A file, not a vector store

`[AHE §3.1]` Long-term memory is a file at a fixed mount point — `LongTermMEMORY.md` — read as text,
edited as text, versioned in git alongside every other harness component.

`[INF]` The reasoning, since the reflex to reach for embeddings is strong:

| Requirement | File | Vector store |
|---|---|---|
| A human can read the whole thing | yes | no |
| A diff shows exactly what changed | yes | no |
| Roll back one bad entry | `git revert` | rebuild the index |
| Attribute a behaviour change to an entry | yes, by line | approximately |
| Enumerate everything known about a repository | yes | only by querying and hoping |
| Scales to 10⁶ entries | no | yes |

The last row is the honest trade, and it is a trade you should decline. `[INF]` A long-term memory
that has grown to a million entries has stopped being learned knowledge and become an unmanaged
corpus. The right response to memory growth is curation, not retrieval — because every entry is paid
for out of Chapter 11's budget, and an entry nobody can enumerate is an entry nobody can delete.

Chapter 25's world model is where genuinely large environmental state belongs. Long-term memory is
for the small number of hard-won specifics that change how work is done.

### 2.5 The mental model to carry

> **A long-term memory is a claim, not a fact: written by a model, from one observation, about a
> world that will change. Store the claim with its evidence, and design for it being wrong.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  KERNEL                                                      |
  |                                                              |
  |   +------------------+                                       |
  |   | run driver       |                                       |
  |   +--------+---------+                                       |
  |            |                                                 |
  |     (1)    v                       (2) headings always,      |
  |   +========+=========+                 bodies on request     |
  |   | CONTEXT SYSTEM   |<--------------------------+           |
  |   +========+=========+                           |           |
  |            |                                     |           |
  |            v                            +========+========+  |
  |   +================+                    | MEMORY SYSTEM   |  |
  |   | MODEL PORT     |                    |                 |  |
  |   +================+                    |  read path      |  |
  |            |                            |  write path     |  |
  |            | (3) proposes an entry      |  curation       |  |
  |            +--------------------------->|                 |  |
  |                                         +========+========+  |
  |                                                  | (4)       |
  +--------------------------------------------------|-----------+
                                                     v
                              +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
                              | HARNESS WORKSPACE (git)       |
                              |  LongTermMEMORY.md            |
                              |  skills/<name>/SKILL.md       |
                              +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
                                                     ^
                                                (5)  |
                              +~~~~~~~~~~~~~~~~~~~~~~+~~~~~~~~+
                              | humans, and the Evolve Agent   |
                              | (Ch 46) -- the other authors   |
                              +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+

  Elsewhere, and deliberately NOT here:
     [[ run_steps ]] + trace store ....... episodic (Ch 16)
     assembled context ................... short-term (Ch 11)

  Figure 12.1 -- The memory system in its surroundings
                 (D1 High-Level Architecture)

  (1) the driver asks the context system to assemble
  (2) memory is a context SOURCE; it obeys Ch 11's budget share
  (3) the model may PROPOSE an entry; it cannot write one
  (4) writes go through curation and land in a git-tracked file
  (5) humans and the evolve loop edit the same file, by the same
      mechanism, with the same diffs
```

`[INF]` Wire 3 and wire 5 pointing at the same file is the design's most important structural
property. A model-proposed memory and a human-authored one are the same kind of object, in the same
file, with the same review surface. There is no separate "learned" store that behaves differently
from the "authored" one — which is what makes `git log` a complete account of how the harness's
knowledge changed, and what makes Chapter 47's rollback work on memory exactly as it works on code.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  LongTermMEMORY.md -- structured so that headings can be loaded
  without bodies (Ch 11 progressive disclosure)

  +--------------------------------------------------------------+
  | # Long-term memory                                            |
  |                                                              |
  | ## acme/checkout                     <-- scope: one repo      |
  |                                                              |
  | ### Test suite needs a database URL                           |
  |   confidence: 0.9   evidence: 4 runs   last confirmed: 2026-02|
  |   Integration tests require POSTGRES_URL set before running.  |
  |                                                              |
  | ### Prefers small pull requests       <-- scope: one customer |
  |   confidence: 0.7   evidence: 2 runs   last confirmed: 2026-01|
  |   Reviewers here reject PRs over ~400 lines.                  |
  |                                                              |
  | ## General                            <-- scope: all work     |
  |                                                              |
  | ### Prefer ripgrep over find                                  |
  |   confidence: 1.0   evidence: authored   last confirmed: --   |
  +--------------------------------------------------------------+

  READ PATH                            WRITE PATH
  +----------------------+             +----------------------+
  | 1. select by scope   |             | 1. PROPOSE (model)   |
  |    repo, tenant,     |             |    at run end, from  |
  |    general           |             |    what it observed  |
  | 2. headings first    |             | 2. ABSTRACT          |
  |    (~40 tokens each) |             |    strip customer    |
  | 3. bodies on request |             |    specifics (Ch 6)  |
  |    via a tool call   |             | 3. CLASSIFY          |
  | 4. respect the       |             |    new / reinforces  |
  |    budget share      |             |    / contradicts     |
  |    (Ch 11)           |             | 4. APPLY             |
  +----------------------+             |    commit to git     |
                                       +----------------------+
     cheap, every call                    expensive, once per run,
                                          OFF the critical path

  Figure 12.2 -- The memory file and its two paths
                 (D2 Low-Level Architecture)
```

### 4.1 The asymmetry between the paths

`[INF]` Read is cheap and constant; write is expensive and rare. That asymmetry should be visible in
the code, because it drives two decisions.

The read path runs on **every model call in the system** and must therefore do no work beyond
selecting by scope and emitting headings. Anything cleverer — ranking by relevance, embedding the
current goal — is a per-call cost multiplied by every step of every run, paid to solve a problem that
a small enumerable file does not have.

The write path runs **once per run, after the work is done, off the critical path**. It can afford a
model call of its own, an abstraction pass, and a contradiction check against existing entries. It
must never block the run completing: a memory that failed to write is a missed improvement, and a
run that failed to finish because a memory could not be written is an incident.

```
                                                            LAYER VIEW

  Components and their interfaces.

   AssemblyRequest                                MemoryView (frozen)
   (from Ch 11)                                            ^
        |                                                  |
        v                                                  |
   +----+------------+                            +--------+-------+
   | Scope resolver  |  scopes[]                  | Budget filter  |
   |  for(run)       |--------------+             |  fit(share)    |
   +-----------------+              |             +--------+-------+
                                    v                      ^
   +-----------------+       +------+---------+            |
   | Memory file     |------>| Heading loader |------------+
   |  read()         |       +----------------+
   |  write(commit)  |
   +--+--------------+       +----------------+
      ^                      | Body loader    |<--- tool call, on demand
      |                      +----------------+
      | commit
      |
   +--+--------------+  +----------------+  +------------------+
   | Applier         |<-| Classifier     |<-| Abstractor       |
   |  git commit     |  |  new           |  |  strip specifics |
   |  << written >>  |  |  reinforces    |  |  (Ch 6, Ch 37)   |
   +-----------------+  |  contradicts   |  +--------+---------+
                        |  duplicate     |           ^
                        +----------------+           |
                                                MemoryProposal
                                                (from the model,
                                                 at run end)

  Figure 12.3 -- Memory system components (D3 Component Diagram)
```

`[INF]` The Abstractor sits between the model and the Classifier deliberately: abstraction happens
*before* the contradiction check, so that two entries about different customers with the same
underlying lesson are recognised as the same entry rather than stored twice. That ordering is also
what makes the Chapter 6 tenancy leak structurally hard — a specific never reaches the file, so it
cannot leak from it.

---

## 5. The Write Path

### 5.1 The model proposes; it does not write

`[DAR §8.1]`'s pure/effectful discipline applies here in a form worth stating explicitly: **writing a
memory is an effectful act on the harness**, and the model is not permitted to perform it directly.
It emits a proposal; the system decides.

`[INF]` The alternative — a `remember(text)` tool the model calls whenever it feels it learned
something — is common and is the cold open with fewer safeguards. It puts an unreviewed, unabstracted,
unclassified claim into a file that will be read on every future call, at the moment of least
reflection, from inside the run that produced it.

### 5.2 Abstraction at write time

Chapter 6 §5.4 established the rule; this is where it is enforced. The Abstractor removes anything
that is true of a *customer* rather than of the *system*:

| Proposed | Stored |
|---|---|
| `POSTGRES_URL=postgres://ci:hunter2@pg-3.acme.corp/billing` | "This repository's integration tests require `POSTGRES_URL` to be set." |
| "acme's tech lead Priya rejects PRs over 400 lines" | "Reviewers on this repository reject pull requests over roughly 400 lines." |
| "The Fenwick migration broke checkout on 4 March" | *(rejected: an event, not a lesson)* |

`[INF]` Filtering at read time is too late, and the reason is mechanical rather than philosophical:
the file is committed to git. Once a secret is in the history, redacting the working copy does not
remove it, and Chapter 37's retention rules have already been violated. The only correct place is
before the write.

### 5.3 Classification against what is already known

Four outcomes, and the third is the one the cold open needed:

| Outcome | Condition | Action |
|---|---|---|
| **New** | no existing entry on this claim | append, confidence from evidence count |
| **Reinforces** | an existing entry says the same | increment evidence, raise confidence, update `last_confirmed` |
| **Contradicts** | an existing entry says the opposite | **do not overwrite** — §5.4 |
| **Duplicate** | textually near-identical | discard the proposal |

### 5.4 Contradiction is the interesting case

`[INF]` When a run's observation contradicts an existing entry, the naive responses are both wrong.
Overwriting means the most recent single observation always wins, so one bad afternoon erases four
runs of evidence. Discarding means an entry can never be corrected, and the cold open is permanent.

The rule that works:

> **A contradiction lowers confidence; it does not flip the claim. An entry whose confidence falls
> below the floor is retired, not rewritten.**

So the cold open's entry would have been written with `confidence: 0.4, evidence: 1` — one
observation, no corroboration. The first run that found `test_checkout_flow` failing for a real
reason would have contradicted it, dropping confidence below the floor and retiring it. The
regression would have been caught on the second occurrence rather than never.

`[INF]` And an entry below a confidence threshold is not loaded into context at all, which means a
freshly-written, single-observation memory does not influence behaviour until something corroborates
it. That one rule converts long-term memory from "the last thing that happened is now policy" into
something closer to evidence accumulation.

### 5.5 Staleness: entries about a world that moves

Confidence decays with time since `last_confirmed`, not with time since written. `[INF]` An entry
confirmed by a run last week is current; one last confirmed eight months ago is a claim about a
repository that has had eight months of commits.

| Signal | Effect |
|---|---|
| Reinforced by a run | `last_confirmed` = now; confidence up |
| Contradicted | confidence down |
| Not seen for N runs where it was in scope | slow decay |
| Below the floor | retired: moved to a retired section, not deleted |

Retirement rather than deletion matters for the same reason Chapter 10 retains superseded plans: an
entry that shaped a decision six months ago must still be resolvable when somebody asks why that
decision was made.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  run        memory sys    abstractor   classifier   git       context
   |             |             |            |         |           |
   |  ---- during the run: READ path, every single call ----      |
   |             |                                               |
   |             |<-- headings for scope(acme/checkout) ----------|
   |             |--- 6 headings, ~240 tokens ------------------->|
   |             |                                               |
   |             |<-- body of "Test suite needs a database URL" --|
   |             |    (model asked, via a tool call)              |
   |             |--- 90 tokens --------------------------------->|
   |             |                                               |
   |  ---- run completes. WRITE path, off the critical path ----  |
   |             |             |            |         |           |
   |-- propose ->|             |            |         |           |
   |  "integration tests here are unreliable; a second           |
   |   failure can be ignored"                                    |
   |             |-- abstract ->|            |         |           |
   |             |<-- "Integration tests on this repository       |
   |             |     are intermittently unreliable." ----------|
   |             |              (the "ignore a second failure"    |
   |             |               inference was STRIPPED: it is a  |
   |             |               recommendation, not an           |
   |             |               observation -- section 6.1)      |
   |             |-------------- classify -->|         |           |
   |             |<-- NEW, evidence=1, confidence=0.4 -|           |
   |             |------------------------- commit --->|           |
   |             |.. << memory.entry.written >> .......|           |
   |             |                                               |
   |  ---- and on the next run, six weeks later ----              |
   |             |                                               |
   |             |  confidence 0.4 is BELOW the load floor (0.5)  |
   |             |  -> not loaded into context at all             |
   |             |  -> the regression is not explained away       |

  Figure 12.4 -- Writing a memory, with the cold open prevented
                 (D4 Sequence)
```

### 6.1 Two independent defences

The sequence shows the cold open failing twice, which is deliberate.

**The Abstractor strips the inference.** "A second failure can be ignored" is not something the run
observed; it is a rule the model derived from an observation. `[INF]` Memories record observations,
not recommendations — an observation can be contradicted by evidence, and a recommendation quietly
becomes policy. That distinction is checkable: if a proposed entry contains an imperative, it is a
recommendation and belongs in a skill (procedural memory), where it gets reviewed.

**The confidence floor keeps it out of context.** Even had the inference survived, a single
observation yields `confidence: 0.4`, below the load floor, so the entry sits in the file
accumulating or losing evidence without influencing any run until something corroborates it.

`[INF]` Two independent defences for one failure is proportionate here, because this is the only
component that writes to itself. A defect in the read path costs one run; a defect in the write path
costs every future run.

```
                                                             TIME VIEW

  The cross-run cycle. Not a loop within a run -- a loop BETWEEN runs.

        +----------------------------------------------------+
        |                                                    |
        v                                                    |
   +----+------------------+                                 |
   | run N reads memory    |  headings always                |
   | (every model call)    |  bodies on demand               |
   +----+------------------+                                 |
        |                                                    |
        v                                                    |
   +----+------------------+                                 |
   | run N does its work   |                                 |
   +----+------------------+                                 |
        |                                                    |
        v                                                    |
      /   \                                                  |
     / learned\  no -----------------------------+           |
     \ anything?/                                |           |
      \       /                                  |           |
        | yes                                    |           |
        v                                        |           |
   +----+------------------+                     |           |
   | propose -> abstract   |                     |           |
   +----+------------------+                     |           |
        |                                        |           |
        v                                        |           |
      /   \                                      |           |
     /classify\--- duplicate ------------------->|           |
     \        /--- contradicts --> confidence    |           |
      \      /                     DOWN -------->|           |
        |                                        |           |
        | new / reinforces                       |           |
        v                                        |           |
   +----+------------------+                     |           |
   | commit to git         |                     |           |
   | << entry.written >>   |                     |           |
   +----+------------------+                     |           |
        |                                        |           |
        v                                        v           |
   +----+----------------------------------------+--+        |
   | curation sweep (periodic, not per run):        |        |
   |   decay unconfirmed entries                    |        |
   |   retire entries below the floor               |        |
   |   flag the file if over its budget share       |        |
   +----+-------------------------------------------+        |
        |                                                    |
        +----------------------------------------------------+
                          run N+1

  Exits:
    E1  nothing learned                  -> normal; most runs
    E2  proposal rejected as an event    -> discarded, logged
    E3  file exceeds its budget share    -> curation required;
                                            alert, do not auto-delete
    E4  contradiction rate above ceiling -> the environment moved;
                                            a human should look

  Figure 12.5 -- The cross-run memory cycle (D5 Runtime Loop)
```

`[INF]` E4 is the signal worth building early. A sustained rise in contradictions is not a memory
defect — it means the world the entries describe has changed, and no automated decay will notice
that as fast as the contradiction rate will. It is the closest thing this chapter has to a smoke
alarm.

---

## 7. State Management

```
                                                            STATE VIEW

  One memory entry's lifecycle.

              +------------------+
              | {{ PROPOSED }}   |  emitted by the model at run end
              +--------+---------+
                       | abstracted + classified as new
                       v
              +------------------+
              | {{ PROVISIONAL }}|  in the file, confidence below the
              +--------+---------+  load floor: NOT loaded into context
                  |         ^
     corroborated |         | contradicted
                  v         |
              +--------------------+
              | {{ ACTIVE }}       |  loaded into context, within its
              +--------+-----------+  scope and budget share
                  |         ^
    contradicted  |         | reinforced
    or decayed    v         |
              +------------------+
              | {{ PROVISIONAL }}|
              +--------+---------+
                       | falls below the retire floor
                       v
              +------------------+
              | {{ RETIRED }}    |  kept in the file, never loaded,
              +------------------+  resolvable forever (section 5.5)

  Illegal, and enforced:
    * PROPOSED -> ACTIVE          a new entry is never immediately
                                  authoritative; one observation is
                                  not evidence
    * RETIRED -> ACTIVE           a retired entry is re-proposed as
                                  new, with fresh evidence; it is not
                                  un-retired
    * any state -> deleted        entries are retired, not removed;
                                  git history is the audit trail
    * a write during a run        the write path runs at run end only

  Figure 12.6 -- A memory entry's lifecycle (D6 State Diagram)
```

### 7.1 Memory is harness state, with all that implies

Chapter 6 classified long-term memory as **harness state**: it outlives any run without being a fact
about the world. Three consequences land here.

**It is tenanted, and by nothing else's rules.** The Chapter 6 cold open leaked because harness
state is scoped by neither the run's tenant id nor the domain's isolation. §5.2's abstraction is the
scoping mechanism, and Chapter 37 makes it a governance requirement rather than a convention.

**It is versioned with the harness, not with the run.** A run pins its harness version at claim time
(Chapter 8 §14), so a run in flight reads the memory file as it was when the run started. `[INF]`
Without that, a memory written by run A could change run B's behaviour mid-flight, and B's
trajectory would describe a configuration that never existed as a whole.

**It is in the Evolve Agent's action space.** Chapter 46's workspace includes `LongTermMEMORY.md`,
which means the evolution loop can add, edit, and retire entries. That is the highest-leverage edit
available to it and the one with the longest tail if it is wrong.

---

## 8. Internal APIs

```python
from typing import Protocol


class MemoryPort(Protocol):
    """Long-term memory. A context source on the read side, and the only
    harness component with a write path reachable from inside a run.

    The read path is called on every model call and must stay trivial.
    The write path is called once, at run end, off the critical path.
    """

    async def view(self, scopes: Sequence[Scope], budget: int) -> MemoryView:
        """Headings for every ACTIVE entry in scope, within budget.

        Bodies are NOT included; the model retrieves them with a tool
        call (Ch 11 progressive disclosure). Entries below the load
        floor are excluded here, not filtered later.
        """

    async def body(self, entry_id: EntryId) -> str: ...

    async def propose(self, proposal: MemoryProposal) -> ProposalOutcome:
        """Submit an observation for possible storage.

        Never raises into the run: a failure here is a missed
        improvement, and must not fail a completed run (section 4.1).
        The outcome records which of new / reinforces / contradicts /
        duplicate / rejected applied, and why.
        """

    async def curate(self, now: datetime) -> CurationReport:
        """Periodic, not per run. Decays unconfirmed entries, retires
        those below the floor, and reports when the file exceeds its
        Ch 11 budget share. Never deletes."""
```

`[INF]` `propose` returning an outcome rather than a boolean is what makes §13's signals possible.
"How often does a proposal contradict what we already believe?" is the health metric of this
component, and it only exists if the classification decision is returned rather than swallowed.

Note also what is absent: there is no `write`, no `remember`, and no `forget`. The model can propose
and read; it cannot store, and it cannot delete.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class EntryState(StrEnum):
    PROVISIONAL = "provisional"    # below the load floor
    ACTIVE = "active"
    RETIRED = "retired"


class Classification(StrEnum):
    NEW = "new"
    REINFORCES = "reinforces"
    CONTRADICTS = "contradicts"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"          # an event or a recommendation


@dataclass(frozen=True)
class MemoryEntry:
    entry_id: EntryId
    scope: Scope                   # repository, tenant, or GENERAL
    heading: str                   # ~40 tokens; always loaded
    body: str                      # loaded on request only
    state: EntryState

    confidence: float              # 0.0-1.0
    evidence_runs: int             # how many runs corroborated it
    first_written: datetime
    last_confirmed: datetime       # decay is measured from HERE
    contradicted_count: int

    origin: str                    # "run:9f2c" | "human" | "evolve:chg-7"


@dataclass(frozen=True)
class MemoryProposal:
    observation: str               # what happened, not what to do
    scope_hint: Scope
    run_id: RunId
    evidence: tuple[StepRef, ...]  # which steps support this
```

Three fields carry the chapter.

**`last_confirmed`, not `written_at`, drives decay.** An entry confirmed last week is current
regardless of when it was first written, and §5.5 is unimplementable without the distinction.

**`origin` distinguishes a run's claim from a human's.** `[INF]` A human-authored entry starts at
confidence 1.0 and does not decay; a run-authored one starts at 0.4 and must earn its way up.
Chapter 47's attribution also needs to know whether an entry came from an evolution iteration, and
`evolve:chg-7` is that link.

**`evidence` is a tuple of step references, not prose.** The proposal points at the steps that
support it, so a human reviewing the file can go and read what actually happened. Without it, the
cold open's entry is unfalsifiable — a confident sentence with nothing behind it.

---

## 10. Communication

```
                                                            LAYER VIEW

  READ, every model call
  memory file  ====>  context system   ~1-4 KB   headings only
  memory file  ====>  context system   ~0.5 KB   one body, on request

  WRITE, once per run, off the critical path
  run          ====>  memory system    ~1 KB     the proposal
  memory sys   ====>  model port       ~4-10 KB  abstraction call
  memory sys   ====>  git              ~1 KB     one commit

  CURATION, periodic
  memory file  ====>  curator          ~10-60 KB the whole file
  curator      ====>  git              ~2 KB     decay + retirements

  Figure 12.7 -- What moves (D7 Data Flow)
```

```
                                                             TIME VIEW

  context system ---> memory system   "headings for this scope"
  model ------------> memory system   "body of entry 4" (a tool call)
  run (at end) -----> memory system   propose(observation)
  memory system ----> abstractor      strip specifics BEFORE classify
  memory system ----> git             commit; the only write
  model --X          memory file      REFUSED: propose, never write
  memory system --X  run state        REFUSED: no write path
  memory system --X  the run's outcome  a write failure never fails
                                        a completed run

  Figure 12.8 -- Who decides what is remembered (D8 Control Flow)
```

```
                                                             TIME VIEW

  << memory.entry.written >>      ....>  new or reinforced, with
                                         classification and confidence
  << memory.entry.contradicted >> ....>  what contradicted what, and
                                         which run observed it
  << memory.entry.retired >>      ....>  fell below the floor
  << memory.proposal.rejected >>  ....>  an event or a recommendation;
                                         the training signal (Ch 46)

  NOT events:
    reads                    every call; telemetry only
    body retrievals          a tool call, already in the trajectory
    decay recalculation      derived from last_confirmed

  Figure 12.9 -- What memory work makes durable (D9 Event Flow)
```

`[INF]` Four events, and all four describe a change to the harness rather than to the world. That is
the correct shape: this component's durable output is not knowledge, it is *changes to what the
system believes*, which is precisely what Chapter 47 needs to attribute a behaviour change to a
cause.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 16 Observation | episodic is never fed into a live run | the boundary of §2.3 row six |
| Ch 25 World Model | large environmental state belongs there, not here | keeps this file enumerable |
| Ch 37 Tenancy | abstraction at write time, git history | a leak here is unredactable |
| Ch 43 Component Observability | memory as a file at a fixed mount point | the substrate that makes it editable |
| Ch 46 Evolve Agent | memory is in the action space | the highest-leverage edit available |
| Ch 47 Attribution | `origin`, and the four events | which iteration changed what belief |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Wrong lesson, kept forever | a coincidence recorded as a rule | contradiction events on that entry | confidence floor; contradiction lowers rather than flips — the cold open |
| Recommendation stored as observation | the proposal contains an imperative | proposals containing "should", "always", "ignore" | reject; recommendations belong in skills |
| Immediate authority | a new entry loaded at once | behaviour changing after a single run | the load floor (§5.4) |
| Overwrite on contradiction | most recent observation wins | an entry flip-flopping across runs | contradictions lower confidence; never rewrite |
| Stale entry about a moved world | environment changed; nothing re-checked | contradiction rate rising (E4) | decay from `last_confirmed`; E4 alert |
| Tenancy leak | a specific written verbatim | scan the file for secrets and identifiers | abstraction at write time; git history is unredactable (Ch 37) |
| Unbounded growth | append-only with no curation | file exceeding its Ch 11 budget share | periodic curation; retire, do not delete |
| Vector-store reflex | semantic retrieval instead of a file | nobody can enumerate what is known | keep it small and readable (§2.4) |
| Write blocking a run | `propose` on the critical path | run latency rising at completion | write path is off-path and never raises |
| Episodic fed into a live run | a previous trajectory pushed into context | the model repeating an old run's errors | records are not instructions (§2.3) |

`[INF]` Row two deserves the emphasis §6.1 gave it. The distinction between "integration tests here
are unreliable" and "ignore a second failure" is the distinction between a fact that can be
disproved and a policy that cannot. The first invites contradiction; the second instructs the model
to disregard the very evidence that would contradict it. A memory system that cannot tell them apart
will eventually write down a rule that suppresses its own correction, which is the cold open's
precise mechanism.

---

## 12. Scalability

### 12.1 Memory is a fixed cost on every call

Chapter 11 §2.3 counted long-term memory among the fixed costs paid before any work fits. So its
size is not a storage question; it is a tax on every model call in the system.

| Quantity | Scales with | Watch |
|---|---|---|
| Read cost per call | entries in scope, headings only | flat; a rise means scoping is too broad |
| Write cost | one model call per run | negligible against the run |
| Curation cost | total entries | periodic; never per call |
| File size | entries minus retirements | should plateau, not grow |

`[INF]` "Should plateau" is the property to defend. A memory that grows linearly with runs forever
is not learning; it is accumulating. A healthy file reaches a size that reflects how much there is
to know about the systems in scope and stays there, with entries turning over as the world moves.

### 12.2 Scoping is what keeps it flat

Three scopes — repository, tenant, and general — and the read path loads only those in play. `[INF]`
A thousand customers with ten entries each is ten thousand entries in the file and perhaps fifteen
loaded on any given call. Without scoping, the same file is unusable at a fraction of that size.

This is also the answer to "why not a vector store at scale": scoping does the work retrieval would
have done, exactly, cheaply, and enumerably — because the scopes are known before the query, rather
than inferred from it.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Contradiction rate | the world moved (E4) | sustained rise |
| Proposals rejected as recommendations | the model is writing policy | rising share |
| Entries promoted PROVISIONAL to ACTIVE | is anything being corroborated? | near zero means memory is write-only |
| Memory tokens per call | the Ch 11 tax | above its budget share |
| File size over time | plateau vs accumulation | monotonic growth |
| Retirement rate | is curation running | zero over a long window |
| Entries never loaded in N runs | dead weight | reported, for curation |

`[INF]` Row three is the one that reveals an ineffective memory system fastest. If nothing is ever
promoted from provisional to active, the system is writing observations nothing ever corroborates —
which usually means the scope is too narrow (every entry is about a situation that recurs once) or
the abstraction is too weak (each entry is phrased so specifically that no later run matches it).

### 13.2 The test that catches the cold open

```python
async def test_single_observation_does_not_become_policy(
    memory: MemoryPort, runtime: Runtime
) -> None:
    outcome = await memory.propose(MemoryProposal(
        observation="test_checkout_flow failed, then passed on retry",
        scope_hint=Scope.repo("acme/checkout"),
        run_id=run.id,
        evidence=(StepRef(run.id, 12),),
    ))
    assert outcome.classification is Classification.NEW
    assert outcome.entry.state is EntryState.PROVISIONAL
    assert outcome.entry.confidence < LOAD_FLOOR

    # The property: a fresh single-observation entry changes nothing.
    view = await memory.view([Scope.repo("acme/checkout")], budget=4000)
    assert outcome.entry.entry_id not in {e.entry_id for e in view.entries}


async def test_recommendations_are_rejected(memory: MemoryPort) -> None:
    outcome = await memory.propose(MemoryProposal(
        observation="If the test fails twice, ignore it and proceed",
        scope_hint=Scope.repo("acme/checkout"),
        run_id=run.id,
        evidence=(),
    ))
    assert outcome.classification is Classification.REJECTED
    assert "recommendation" in outcome.reason
```

`[INF]` The second test is the one that would have prevented the incident outright, and it is worth
noticing that it needs no model and no run — it is a property of the write path, checkable in
milliseconds.

### 13.3 Read the file

`[BP]` The cheapest practice in this chapter: a human reads `LongTermMEMORY.md` end to end, once a
month. It is a few hundred lines by construction, and it is the only harness component whose
contents were written by a machine and never reviewed by anybody.

`[INF]` That this is *possible* is the argument of §2.4 in one sentence. A vector store cannot be
read end to end, which means the equivalent review does not happen, which means an entry like the
cold open's survives indefinitely and nobody ever sees it.

---

## 14. Relation to AHE

Long-term memory is where this chapter and Level 5 meet most directly, and the meeting is
double-edged.

**It is among the highest-value components measured.** `[AHE §4.4.1]` found long-term memory
carrying one of the largest single-component gains when swapped into a minimal baseline, while the
system prompt alone regressed. `[INF]` Read through this chapter, that result is explicable rather
than surprising: memory supplies *specific facts about the situation*, and specific facts change
what is possible, whereas general instruction competes for attention with everything else in the
context.

**Specificity is exactly what makes it dangerous.** Chapter 6 §16 already stated the tension: the
property that makes memory work is the property that makes it leak. §5.2's abstraction is the
mechanism for having one without the other, and it is genuinely lossy — some of the value is in the
specifics being stripped.

**The evolution loop optimises toward the danger.** `[INF]` An Evolve Agent measuring outcomes will
find that more specific memories perform better, because they do. Nothing in the reward signal
represents the tenancy risk. This is the clearest instance in the book of an optimisation target
that is correct locally and wrong globally, and Chapter 46's controllability constraints are the
answer: abstraction is enforced by the write path, which is runtime code, and the Evolve Agent's
workspace does not include it.

**Memory edits are the least additive of all.** Chapter 48's non-additivity result bites hardest
here, for a reason specific to this chapter: two memory entries that each improve behaviour may
address the same failure by different routes, and both then compete for the same Chapter 11 budget
share while providing overlapping benefit. Summing their measured individual gains will overstate
the pair, reliably.

---

## 15. Industry Perspective

**`[AHE]`** Supplies long-term memory as one of seven component types, its location as a file at a
fixed mount point in the harness workspace, the ablation result placing it among the highest-value
components while prompt-only regressed, and progressive disclosure as the loading discipline
`[AHE §3.1, §3.2, §4.4.1]`.

**`[DAR]`** Supplies the state-category framework this chapter classifies against and the
propose-versus-perform discipline that keeps the model from writing directly `[DAR §3.3, §8.1]`.

**`[INF]`** The handbook's own: the four-way split with its owners and lifetimes, observations versus
recommendations as the rejection criterion, confidence and evidence count on every entry,
contradiction lowering confidence rather than flipping a claim, the load floor that keeps
single-observation entries out of context, decay measured from `last_confirmed`, retirement rather
than deletion, scoping as the alternative to retrieval, and the observation that an evolution loop
optimises toward specificity while nothing in its reward signal represents tenancy risk.

**`[BP]`** Confidence-weighted knowledge bases with provenance and decay are long-standing practice
in expert systems and in threat intelligence, and monthly human review of a small file is ordinary
operational hygiene. The contribution here is applying both to a store that a model writes to itself.

**`[FUT]`** The confidence floor, decay rate, and retirement threshold in §5 are stated as
mechanisms without defensible default values. `[FUT]` A principled way to set them — ideally derived
from measured contradiction rates per scope rather than chosen — is open, and is the most obvious
piece of missing work in this chapter.

---

## 16. Key Takeaways

1. **Four subsystems, not one word.** Short-term is context, episodic is the record, procedural is
   skills, long-term is learned facts. They differ in lifetime, owner, state category, and write
   path, and only one of them is written from inside a run.
2. **A memory is a claim, not a fact.** Written by a model, from one observation, about a world that
   moves. Store the evidence with it and design for it being wrong.
3. **Observations, never recommendations.** "Tests here are unreliable" can be contradicted;
   "ignore a second failure" instructs the model to disregard the evidence that would contradict it.
   The cold open is the second kind.
4. **One observation is not evidence.** A new entry is provisional and is not loaded into context
   until something corroborates it. That single rule is most of the safety.
5. **Contradiction lowers confidence; it does not flip the claim.** Overwriting lets one bad
   afternoon erase four runs of evidence; discarding makes an error permanent.
6. **Abstract at write time.** The file is committed to git, so a specific that reaches it cannot be
   redacted later. Filtering on read is already too late.
7. **A file, not a vector store.** Small enough to enumerate, diff, review, and roll back. If it has
   grown past that, the answer is curation, not retrieval.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Short-term memory** | What the model can see on one call; the assembled context, rebuilt every time. | `[INF]` | Ch 11 |
| **Episodic memory** | The durable record of what happened in a run, read by people and tools and never fed back into a live run. | `[INF]` | Ch 16 |
| **Procedural memory** | How to perform a class of task, packaged as a skill and authored deliberately rather than learned. | `[AHE]` | Ch 14, Ch 46 |
| **Long-term memory** | Facts the system learned and kept; the only harness component a run writes to itself. | `[AHE]` | Ch 46 |
| **Memory proposal** | An observation submitted at run end for possible storage; the model proposes and never writes. | `[INF]` | Ch 46 |
| **Abstraction at write time** | Stripping customer specifics before an entry is committed, because git history cannot be redacted afterwards. | `[INF]` | Ch 37 |
| **Confidence** | How much evidence stands behind an entry, raised by corroboration and lowered by contradiction. | `[INF]` | Ch 47 |
| **Load floor** | The confidence below which an entry stays in the file but is never loaded into context. | `[INF]` | Ch 46 |
| **Provisional entry** | A written but uncorroborated entry, which influences nothing until a later run confirms it. | `[INF]` | Ch 46 |
| **Contradiction** | A later observation that opposes an existing entry, lowering its confidence rather than rewriting it. | `[INF]` | Ch 47 |
| **Decay** | Confidence falling with time since `last_confirmed`, so claims about a moved world lose authority. | `[INF]` | Ch 25 |
| **Retirement** | Moving an entry below the floor out of use while keeping it resolvable forever. | `[INF]` | Ch 47 |
| **Scope** | Whether an entry is about one repository, one tenant, or all work; what makes retrieval unnecessary. | `[INF]` | Ch 37 |
| **Curation** | The periodic sweep that decays, retires, and reports on size; never per run, and never deletes. | `[INF]` | Ch 46 |

---

**Next:** Chapter 13 — *The Reasoning Engine.* The model port: one interface, metered, capped, and
abortable; reasoning-effort tiers and sampling parameters as configuration rather than code; and why
the provider must never be visible above this line.
