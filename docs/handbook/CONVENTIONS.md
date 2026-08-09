# Handbook Authoring Conventions

The single card to work from when writing or editing a chapter. It consolidates
[Phase 1](blueprints/phase-1-structural-blueprint.md) §6–§7,
[Phase 2](blueprints/phase-2-revised-blueprint-v2.md) §7, and
[Phase 3](blueprints/phase-3-completion-plan.md) §2–§3, so that conventions live in one place
rather than three.

Most of what follows is checked automatically by `tools/check_handbook.py`. Run it before
considering a chapter finished:

```bash
python3 tools/check_handbook.py
```

---

## 1. Chapter skeleton

````
  <fence>
    Level N · Chapter NN
    TITLE IN CAPITALS
    Requires   Cx ..., Cy ...
    Unlocks    Cz ..., Cw ...
    Diagrams   Full (9) | Core (5) | Light (2-4)
    Variant    Foundational — ...        (Ch 0-3 only)
  </fence>

  # Chapter NN — Title

  ## 1. Motivation
     ### 1.1 Cold open                    a real Atlas failure, under 250 words
     ### 1.2 In plain language            [N1] newcomer block, 150-250 words
     ### 1.3 Why this chapter exists
     ### 1.4 What previous framings got wrong
  ## 2. High-Level Mental Model
     ### 2.1 The analogy, and where it breaks    [N2]
     ### 2.2 Why <this> must exist              [N3]
     ### 2.3+ the chapter's organising model
  ## 3. High-Level Architecture              D1
  ## 4. Low-Level Decomposition              D2 (+ D3 at Full)
  ## 5. <chapter-specific deep section>
  ## 6. Runtime Sequence                     D4 (+ D5 at Full)
  ## 7. State Management                     D6
  ## 8. Internal APIs                        Protocol signatures
  ## 9. Data Structures
  ## 10. Communication                       D7 / D8 / D9 at Full
  ## 11. Failure Modes                       trigger | detector | recovery
  ## 12. Scalability
  ## 13. Production Engineering
  ## 14. Relation to AHE                     Level 5: "Relation to the Base Runtime"
  ## 15. Industry Perspective                claims regrouped by tag
  ## 16. Key Takeaways                       ~7 numbered
      **Terms introduced in this chapter**   [N4] table

  ---
  **Next:** Chapter NN+1 — *Title.* Two-sentence hand-off.
````

`<fence>` stands for a literal triple-backtick line.

**Sections 5 and 7 are chapter-specific.** Every other section title carries a fixed stem. In the
Foundational Variant (Ch 0–3), sections 4–9 describe mental models rather than components and their
titles are free.

---

## 2. The four on-ramp blocks

The handbook must be followable by an engineer new to AI systems *and* new to distributed systems.
Four rules make that testable:

1. **No undefined term survives its first use** — including idempotent, lease, CAS, semaphore,
   outbox, backpressure, quarantine, projection.
2. **Necessity before mechanism** — never introduce a component by saying what it does. Show the
   failure that exists without it, then derive it.
3. **One concrete anchor per abstraction** — every abstract claim lands on Atlas, with a named
   repository, a named issue, or a real number.
4. **Readable in order, once, without leafing backwards** — forward references are labelled;
   backward dependencies are restated in a line rather than cited.

| Block | Where | What it is |
|---|---|---|
| **N1** | `### 1.2 In plain language` | 150–250 words. No jargon, no tags, no cross-references. Answers: what is this, why does it exist, what goes wrong without it. Placed *after* the cold open — the cold open earns attention, N1 keeps it. |
| **N2** | `### 2.1 The analogy, and where it breaks` | One concrete non-AI analogy, then a mandatory paragraph naming the property the analogy does **not** carry. The second half is not optional: an unbounded analogy is how readers form confident wrong models. |
| **N3** | `### 2.2 Why <this> must exist` | A 4–8 step derivation in a fenced block, each step a forced move. Where real alternatives exist, name them and state the property that selected the winner — never "it is simpler" or "it is standard". |
| **N4** | tail of `## 16` | `**Terms introduced in this chapter**` table: Term / one plain sentence / tag / next needed in. This is the mechanical input to Appendix A. |

The on-ramp adds roughly 700–900 words per chapter. It does not soften technical content, drop
citations, or replace precise vocabulary with approximate vocabulary.

---

## 3. Diagrams

**Budget by tier:** Full = 9, Core = 5, Light = 2–4 (the header's declared count must match the
actual count exactly, whatever the tier).

**Hard rules**

- Pure 7-bit ASCII. No box drawing, no Unicode arrows, no `§`, no em dashes inside a diagram.
- Maximum 78 columns. Decompose rather than exceed.
- Every diagram states its axis top-right: `LAYER VIEW`, `TIME VIEW`, `STATE VIEW`, or
  `CONCEPTUAL VIEW` (Light tier only).
- Every diagram carries a caption: `Figure NN.M -- what it shows (Dn Type)`. The caption may wrap
  onto a second indented line. Light-tier conceptual figures use `(conceptual)` as the type.
- More than four connections means numbered wires `(1)`, `(2)`, … and a wire-reference table.
  Letters `(A)`, `(B)` are reserved for side channels.
- One concern per diagram. Control flow and data flow are never the same figure.

**Box vocabulary**

```
   +--------------+     kernel component; you do not write this
   +==============+     port; an extension point you implement
   +~~~~~~~~~~~~~~+     external system: provider, sandbox, your domain
   [[          ]]       durable store (a table)
   ((          ))       queue
   <<          >>       event
   {{          }}       a state, in a state diagram
```

**Arrow vocabulary**

```
   ---->     synchronous call; control flows and returns
   ....>     asynchronous message or event; no return
   ====>     bulk data movement; annotate with volume
   --||->    passes through a gate; blocked until resolved
   --X       refused, blocked, or dropped
   <-->      bidirectional / negotiated
   ~~~~>     unreliable or best-effort (telemetry, progress)
```

**The nine types**

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

---

## 4. Provenance

Every non-obvious claim carries exactly one tag. Section 15 regroups the chapter's claims under
these five headings with no blending.

| Tag | Means |
|---|---|
| `[AHE]` | the Agentic Harness Engineering paper states this literally |
| `[DAR]` | the durable/universal runtime specification states this literally |
| `[INF]` | engineering inference by the handbook |
| `[BP]` | established industry practice, attributed |
| `[FUT]` | future or speculative proposal |

**Hard rule:** extrapolating from a source is `[INF]`, never that source's tag. `[AHE]` and `[DAR]`
are co-primary; where they overlap, cite both and name the difference rather than merging them.

---

## 5. Naming

| Thing | Convention | Example |
|---|---|---|
| Subsystem in prose | Title Case, definite article, singular | the Activity Runner |
| The five nouns as concepts | Capitalised | a Run, one Episode |
| A generic instance | lowercase | the run parked |
| Book tier | Level *n* | Level 3 |
| Architecture tier | lowercase | the kernel layer |
| Build order | Stage *n* | Stage 4 |
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
| Fake ports in tests | `Fake<Port>` | `FakeModelPort` |
| Read-model projections | `<noun>_view` | `run_progress_view` |

**Code:** Python throughout. Ports are `typing.Protocol`, not ABCs. Data carriers are frozen
`@dataclass`. Type hints mandatory on every signature — a signature without them is not a contract.
Every code fence carries a language label (`python`, `sql`, `yaml`, `json`, `bash`, `diff`);
diagram fences are unlabelled.

---

## 6. Prohibited words

Banned outside a single definitional mention. Quoted text, code spans, and blockquotes are exempt —
the handbook frequently diagnoses these phrases.

| Banned | Use instead | Why |
|---|---|---|
| "the agent" as a component | Run, Episode, Planner, Activity Runner | hides which part is meant |
| orchestrator | run driver | overloaded across five vendor meanings |
| workflow | plan, task graph | implies a workflow engine we did not require |
| prompt engineering | context engineering, harness engineering | the prompt is the weakest surface |
| memory, unqualified | short-term / long-term / episodic / procedural | four different subsystems |
| just, simply | — | signals the explanation was skipped |

---

## 7. Revisions to earlier phases

Recorded here so the blueprints are not silently contradicted.

| Convention | Was | Now | Why |
|---|---|---|---|
| Cold open length | "under 150 words" (Phase 2 §7.2) | **under 250 words** | The estimate predates any written chapter. The eight shipped chapters measured 154–264 words at a quality everyone accepted; a rule violated by 8 of 8 chapters is not a rule. Same reasoning Phase 3 applied to chapter length. |
| Light-tier figure count | "High-Level Arch + one conceptual diagram" (Phase 1 §1.4) | **2–4, declared in the header** | Ch 0, 2, and 3 carry 3; Ch 1 carries 4. The header count is authoritative and the linter enforces header-matches-actual rather than a fixed number. |
| `[AHE]` glossary wording for Skill | "reusable workflow package" | "reusable **procedure** package" | The original wording used a word Phase 1 §7.6 bans. The meaning is unchanged. |
| Axis labels | three (LAYER / TIME / STATE) | **four**, adding `CONCEPTUAL VIEW` | Foundational chapters draw models, not components, so they have no layer, time, or state axis. Already used consistently in Ch 0–3. |

---

## 8. Definition of done

- [ ] Header block; `Requires` precede and `Unlocks` follow this chapter's number
- [ ] 16 top-level sections, in order, correct stems
- [ ] On-ramp blocks N1–N4 present
- [ ] Cold open is a specific Atlas incident under 250 words
- [ ] Figure count equals the declared tier exactly
- [ ] Every figure: axis label, caption with type, ≤78 columns, 7-bit ASCII
- [ ] Ports in §8 are `Protocol`s with full type hints
- [ ] §11 failure table has trigger, detector, recovery
- [ ] One provenance tag per non-obvious claim; §15 regroups by tag
- [ ] No prohibited words outside quotes
- [ ] Long edges in repaid in §1; long edges out declared in §10
- [ ] `**Next:**` names the following chapter
- [ ] `python3 tools/check_handbook.py` exits zero
- [ ] N4 rows appended to `appendices/a-glossary.md`
