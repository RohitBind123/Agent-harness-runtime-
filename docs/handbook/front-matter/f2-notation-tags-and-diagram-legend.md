# F.2 — Notation, Tags, and Diagram Legend

The reference card. Everything here is expanded in [Appendix B](../appendices/b-naming-conventions.md)
and [Appendix C](../appendices/c-diagram-conventions.md); this page is the version worth having open
while reading.

---

## Provenance tags

Every non-obvious claim in the book carries exactly one tag, and §15 of each chapter regroups the
chapter's claims under these five headings with no blending.

| Tag | Means | How to read it |
|---|---|---|
| `[AHE]` | The Agentic Harness Engineering paper states this literally | Cited; check the source |
| `[DAR]` | The durable agent runtime specification states this literally | Cited; check the source |
| `[INF]` | Engineering inference by the handbook | Reasoned, not cited. Argue with it |
| `[BP]` | Established industry practice, attributed | True elsewhere; transferred here |
| `[FUT]` | Future or speculative proposal | Nobody has built this |

**The hard rule:** extrapolating from a source is `[INF]`, never that source's tag. `[AHE]` and
`[DAR]` are co-primary; where they overlap the handbook cites both and names the difference rather
than merging them.

**If a section is mostly `[INF]` and `[FUT]`, treat it as a considered argument rather than a settled
result.** Chapter 25 is the clearest example and says so in its first paragraph.

A section reference inside a tag points into the *source*: `[AHE §3.1]` is the paper's §3.1, not this
book's. References into this book are always qualified — `Chapter 41 §5.7` — or bare when they mean
the current chapter.

---

## Diagram legend

Diagrams are pure 7-bit ASCII, at most 78 columns, and each states its axis in the top-right corner.

### Boxes

```
   +--------------+     kernel component; you do not write this
   +==============+     port; an extension point you implement
   +~~~~~~~~~~~~~~+     external system: provider, sandbox, your domain
   [[          ]]       durable store (a table)
   ((          ))       queue
   <<          >>       event
   {{          }}       a state, in a state diagram
```

### Arrows

```
   ---->     synchronous call; control flows and returns
   ....>     asynchronous message or event; no return
   ====>     bulk data movement; annotate with volume
   --||->    passes through a gate; blocked until resolved
   --X       refused, blocked, or dropped
   <-->      bidirectional / negotiated
   ~~~~>     unreliable or best-effort (telemetry, progress)
```

### The nine diagram types

| Type | Axis | Shows |
|---|---|---|
| D1 High-Level Architecture | LAYER | the subsystem in its surroundings |
| D2 Low-Level Architecture | LAYER | the subsystem opened up |
| D3 Component Diagram | LAYER | named internals and their interfaces |
| D4 Sequence | TIME | one execution, with at least one failure branch |
| D5 Runtime Loop | TIME | the repeating cycle, every exit labelled `E1..En` |
| D6 State Diagram | STATE | legal states, transitions, illegal-transition note |
| D7 Data Flow | LAYER | `====>` only, with volumes |
| D8 Control Flow | TIME | `---->` and decision diamonds only |
| D9 Event Flow | TIME | `....>` only, event names in `<< >>` |

A Full-tier chapter carries all nine; a Core-tier chapter carries five; the Light tier used in
Chapters 0–3 carries two to four and adds a fourth axis, `CONCEPTUAL VIEW`, because foundational
chapters draw models rather than components.

**Numbered wires.** More than four connections means numbered wires `(1)`, `(2)`, … with a
reference table under the caption. Letters `(A)`, `(B)` are reserved for side channels.

**One concern per diagram.** Control flow and data flow are never the same figure. That is why there
are three separate flow types rather than one combined one, and Chapter 9 is about why reading a
runtime along the wrong flow is how agent codebases become unmaintainable.

---

## Naming, in one table

| Thing | Convention | Example |
|---|---|---|
| Subsystem in prose | Title Case, definite article, singular | the Activity Runner |
| The five nouns as concepts | Capitalised | a Run, one Episode |
| A generic instance | lowercase | the run parked |
| Book tier | Level *n* | Level 3 |
| Architecture tier | lowercase | the kernel layer |
| Chapter cross-reference | `Ch NN §M` | Ch 18 §7 |
| Ports | `Protocol`, PascalCase, `Port` suffix | `PlannerPort` |
| Dataclasses | PascalCase, frozen | `Run`, `Verdict` |
| Fields, params | snake_case | `input_digest` |
| Tables / columns | snake_case plural / singular | `activities` / `lease_until` |
| Command | `cmd.<domain>.<verb>` | `cmd.repo.apply_patch` |
| Event | `<domain>.<noun>.<past_verb>` | `run.step.completed` |
| Tool id | `tool.<namespace>.<verb>` | `tool.repo.apply_patch` |
| Metric | `ark_<subsystem>_<measure>_<unit>` | `ark_activity_replay_total` |
| Trace span | `<layer>/<component>/<operation>` | `kernel/activity_runner/dispatch` |

---

## Words the book does not use

Six phrases are banned outside a single definitional mention, because each hides the thing it
appears to name. They are listed here so that their absence reads as a decision.

| Banned | Use instead | Why |
|---|---|---|
| "the agent" as a component | Run, Episode, Planner, Activity Runner | hides which part is meant |
| orchestrator | run driver | overloaded across five vendor meanings |
| workflow | plan, task graph | implies a workflow engine we did not require |
| prompt engineering | context engineering, harness engineering | the prompt is the weakest surface |
| memory, unqualified | short-term / long-term / episodic / procedural | four different subsystems |
| just, simply | — | signals the explanation was skipped |

---

**Next:** [F.3 — The Running System: ARK and Atlas](f3-the-running-system.md)
