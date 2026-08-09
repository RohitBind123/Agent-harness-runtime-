# Next-Generation Autonomous AI Agent Architecture Handbook
## PHASE 3 — Completion Plan (Chapters 8–49, Front Matter, Interludes, Appendices)

> **Status:** Plan for execution. Supersedes Phase 2 only on the two items Phase 2 left open
> (chapter length target; interludes). Everything else in Phase 1 and Phase 2 stands.
> **Covers:** the 42 unwritten chapters, the newcomer on-ramp, the production template,
> convention enforcement, the batch schedule, and per-chapter content briefs.
> **Written after:** Chapters 0–7 shipped, so the quality bar below is measured from real
> chapters rather than estimated.

---

## 0. Decisions locked for Phase 3

Phase 2 §8 closed with two open questions and no blocking items. Both are now resolved, along
with two new decisions forced by the accessibility requirement.

| # | Decision | Resolution | Consequence |
|---|----------|-----------|-------------|
| 5 | **Reader floor** | The handbook must be followable by an engineer new to AI systems *and* new to distributed systems. | Four fixed on-ramp blocks added to every chapter (§2). Chapters 0–7 are retrofitted so the book is uniform. |
| 6 | **Chapter length** *(Phase 2 §8.2, open)* | **Hold the shipped band.** Core ≈ 5,500 words, Full ≈ 6,500 words, including on-ramp blocks. | Matches Ch 0–7 (measured 5,396–5,983 words). No retro-tightening of sections 8–10. |
| 7 | **Interludes** *(Phase 2 §8.1, open)* | **Keep both.** They are the only place a reader sees the whole system under load. | Interlude I after Ch 20, Interlude II after Ch 41. Narrative, unnumbered, no template. |
| 8 | **Diagram medium** | ASCII stays canonical for all chapter figures. SVG is reserved for level openers. | ~290 new ASCII figures; 4 new SVGs (L0, L2, L3, L4 — L1 and L5 are already served by existing files). |
| 9 | **Delivery** | Batch by level, review checkpoint and one commit per level. | Seven batches (§5). A convention drift is caught at a level boundary, not at chapter 49. |

**Not reopened.** Provenance tags, the 16-section template, the Atlas/ARK reference system,
Python-throughout, ASCII diagram vocabulary, naming conventions, prohibited words. These are
load-bearing and Chapters 0–7 already depend on them.

---

## 1. Scope: exactly what remains

### 1.1 Chapters

| Level | Chapters | Count | Full tier | Core tier | ASCII figures | Est. words |
|---|---|---:|---:|---:|---:|---:|
| 1 — High-Level Runtime | C8–C9 | 2 | 0 | 2 | 10 | ~11,000 |
| 2 — Core Runtime Components | C10–C20 | 11 | 11 | 0 | 99 | ~71,500 |
| 3 — Advanced Runtime | C21–C32 | 12 | 5 | 7 | 80 | ~71,000 |
| 4 — Production Engineering | C33–C41 | 9 | 0 | 9 | 45 | ~49,500 |
| 5 — Self-Evolving Systems | C42–C49 | 8 | 4 | 4 | 56 | ~48,000 |
| **Total** | **C8–C49** | **42** | **20** | **22** | **290** | **~251,000** |

Figure budget is `Full = 9`, `Core = 5` per Phase 1 §1.4, unchanged.

### 1.2 Non-chapter artifacts

| Artifact | Count | Est. words | Batch |
|---|---:|---:|---|
| Level openers (L0–L5) | 6 | ~3,600 | with each level |
| Front matter F.1–F.4 | 4 | ~4,000 | 6 |
| Interlude I — Assembling a Minimal Runtime | 1 | ~3,000 | 2 |
| Interlude II — Anatomy of a Bad Week | 1 | ~3,000 | 4 |
| Appendices A–J | 10 | ~25,000 | accreted per level, closed in batch 6 |
| On-ramp retrofit of Ch 0–7 | 8 | ~5,600 | 0 |
| New SVGs (L0, L2, L3, L4 openers) | 4 | — | with each level |
| Handbook linter | 1 tool | — | 0 |

**Total new or edited prose: ~295,000 words.** This is a book, not a document. The batch
structure in §5 exists so that it is reviewable in pieces and abandonable at any level boundary
without leaving a half-written level.

---

## 2. The newcomer on-ramp

### 2.1 What "a fresher AI engineer can follow it" means, operationally

Vague accessibility goals produce vague prose. Four testable rules replace the goal:

1. **No undefined term survives its first use.** Every term gets a plain-language gloss in the
   same sentence or the sentence after, even if Appendix A defines it formally. This includes
   terms a senior reader would never question: idempotent, lease, CAS, semaphore, outbox,
   backpressure, quarantine, projection.
2. **Necessity before mechanism.** A component is never introduced by describing what it does.
   It is introduced by showing the failure that exists without it, then deriving it. If a reader
   cannot answer "what breaks if I delete this?", the section failed.
3. **One concrete anchor per abstraction.** Every abstract claim lands on Atlas — a named
   repository, a named issue, a real number. `[INF]` claims that cannot be anchored are a signal
   the claim is not yet understood well enough to write.
4. **The chapter is readable in order, once, without leafing backwards.** Forward references are
   allowed and labelled; backward dependencies are restated in one line rather than cited.

### 2.2 The four on-ramp blocks

These are **sub-blocks inside the existing sections**. The 16 numbered top-level sections do not
change, do not move, and do not gain a seventeenth member.

---

**N1 — `### 1.2 In plain language`** *(new; existing 1.2 and 1.3 shift to 1.3 and 1.4)*

Placement is deliberate: after the cold open, not before it. The cold open earns the reader's
attention; N1 makes sure they can keep it.

- 150–250 words. Zero jargon, zero provenance tags, zero cross-references.
- Answers exactly three questions, in this order: *what is this thing, why does it exist, what
  goes wrong without it.*
- Written so it could be read aloud to someone who has never used an LLM API.
- Must not contradict, and must not merely restate, §16 Key Takeaways.

*Shape (Ch 17, The State Manager):*

> The State Manager is the part of the runtime that writes down where a job has got to, so that
> if the machine running it dies, another machine can pick it up from the last thing it finished
> rather than starting over. It exists because an agent run can last hours and cost real money:
> re-running it from the top after a crash is both slow and expensive, and worse, it can repeat
> actions that touched the outside world. Without it, every restart is a gamble on whether the
> agent sends the same email twice.

---

**N2 — `### 2.1 The analogy, and where it breaks`** *(new; existing §2 content shifts down)*

- One concrete, non-AI analogy: an operating-system process table, a restaurant ticket rail, a
  hospital triage board, a warehouse picking list.
- Immediately followed by an explicit **"where the analogy breaks"** paragraph naming the one
  property the analogy does not carry.
- The second half is mandatory. An unbounded analogy is worse than none: it is the mechanism by
  which readers form confident wrong models.

---

**N3 — `### 2.2 Why this component must exist`** *(new)*

A numbered derivation, 4–7 steps, from a requirement the reader already accepts to the component
being introduced. Each step is a forced move, not a design preference.

*Shape (Ch 22, The Event Spine):*

```
  1. A step changes run state AND must notify something else.
  2. Two writes to two systems cannot be made atomic without a distributed
     transaction, which we have ruled out (Ch 2 §4).
  3. So one of the two writes can succeed while the other fails.
  4. If the notification is lost, the run stalls with no error anywhere.
  5. Therefore the notification must be written to the SAME database, in the
     SAME transaction, as the state change.
  6. Something must then read those rows and deliver them.
  7. Steps 5 and 6 are the outbox and the relay. Nothing else was chosen.
```

Where a design genuinely has alternatives, N3 ends by naming them and stating the one property
that selected the winner — never "it is simpler" or "it is standard".

---

**N4 — `**Terms introduced in this chapter**`** *(unnumbered, at the tail of §16)*

A table, one row per term the chapter defines for the first time:

| Term | In one sentence, no jargon | Tag | First needed again in |
|---|---|---|---|

This lands inside §16, before the `---` and the `**Next:**` line. It keeps the 16-section rule
intact, and it becomes the mechanical input to Appendix A: the glossary is assembled from these
tables rather than written separately at the end.

### 2.3 What does not change

The on-ramp adds ~700–900 words per chapter. It does **not** soften the technical content,
remove `[DAR §n]` citations, replace precise vocabulary with approximate vocabulary, or drop the
failure tables. A fresher-readable chapter and a shallow chapter are different things; the
prohibited-words list (Phase 1 §7.6) already bans the words that produce the second one.

### 2.4 Retrofit of Chapters 0–7

Chapters 0–7 are complete and good, but they are the first eight chapters a newcomer reads and
they currently assume the most. Batch 0 adds N1, N2, N3, and N4 to each, and fixes the two
convention defects found in audit:

- **Ch 1** declares `Diagrams Light (3)` but carries four `Figure` captions. Resolve by promoting
  the header to `Light (4)` or by folding the CONCEPTUAL VIEW block into the LAYER VIEW block —
  decided when editing, with the linter enforcing whichever is chosen.
- **Ch 3 and Ch 4** each have one diagram line at 80 columns against a 78-column rule.

---

## 3. The production template

Every chapter from C8 forward is written against this skeleton. Deviations are defects, not style.

````
  <fence>                                      <- header block, unlabelled fence
    Level N · Chapter NN
    TITLE IN CAPITALS
    Requires   Cx ..., Cy ...                  <- must match Phase 2 §4 spine
    Unlocks    Cz ..., Cw ...
    Diagrams   Full (9) | Core (5)
  </fence>

  # Chapter NN — Title

  ## 1. Motivation
     1.1 Cold open                   concrete Atlas failure, < 150 words
     1.2 In plain language           [N1]  newcomer block
     1.3 Why this chapter exists
     1.4 What previous framings got wrong
  ## 2. High-Level Mental Model
     2.1 The analogy, and where it breaks       [N2]
     2.2 Why this component must exist          [N3]
     2.3+ the chapter's organising model
  ## 3. High-Level Architecture          D1
  ## 4. Low-Level Decomposition          D2 (+ D3 at Full tier)
  ## 5. <chapter-specific deep section>
  ## 6. Runtime Sequence                 D4 (+ D5 at Full tier)
  ## 7. State Management                 D6
  ## 8. Internal APIs                    Python Protocol signatures
  ## 9. Data Structures                  frozen dataclasses, tables
  ## 10. Communication                   D7 / D8 / D9 at Full tier
  ## 11. Failure Modes                   failure table: trigger, detector, recovery
  ## 12. Scalability
  ## 13. Production Engineering
  ## 14. Relation to AHE                 -> "Relation to the Base Runtime" in Level 5
  ## 15. Industry Perspective            claims regrouped under the five tags
  ## 16. Key Takeaways                   7 numbered takeaways
      **Terms introduced in this chapter**      [N4]

  ---
  **Next:** Chapter NN+1 — *Title.* Two-sentence hand-off.
````

`<fence>` above stands for a literal triple-backtick line; the header block is an unlabelled
fence exactly as in Chapters 0–7.

### 3.1 Per-chapter definition of done

A chapter is not done until every box is checked. This list is the linter's specification.

- [ ] Header block present; `Requires` / `Unlocks` match the Phase 2 §4 dependency spine exactly
- [ ] Exactly 16 top-level `## N.` sections, in order, with canonical titles (Level 5 uses the
      §14 variant; no other variants permitted from C8 onward)
- [ ] On-ramp blocks N1, N2, N3, N4 all present
- [ ] Cold open is a specific Atlas incident under 150 words, with a time and a named artifact
- [ ] Figure count equals the declared tier, exactly
- [ ] Every figure: axis label (`LAYER VIEW` / `TIME VIEW` / `STATE VIEW`), a
      `Figure NN.M -- caption (Dn Type)` line, ≤78 columns, pure 7-bit ASCII, and a numbered
      wire table when it has more than four connections
- [ ] Every port introduced appears in §8 as a `typing.Protocol` with full type hints
- [ ] Every data structure in §9 is a frozen dataclass or a named table with typed columns
- [ ] §11 failure table has three columns minimum: trigger, detector, recovery
- [ ] Every non-obvious claim carries exactly one provenance tag; §15 regroups them by tag with
      no blending
- [ ] Naming conventions honoured (Phase 1 §7.2–§7.5, Phase 2 §7.3)
- [ ] No prohibited words (Phase 1 §7.6) outside a single definitional mention
- [ ] Every long edge into this chapter (Phase 2 §4.1) is repaid in §1; every long edge out is
      declared in §10
- [ ] `**Next:**` line names the correct following chapter
- [ ] Word count within ±15% of the tier band
- [ ] `tools/check_handbook.py` exits zero
- [ ] Glossary rows from N4 appended to the Appendix A working file

---

## 4. Convention enforcement: the handbook linter

Forty-two chapters written across many sessions will drift. Reviewing for drift by reading is
unreliable and slow; the conventions in Phase 1 §6 and §7 are almost entirely mechanical, so they
get a script.

**Location:** `tools/check_handbook.py`. Pure standard library, no dependencies.
**Invocation:** `python3 tools/check_handbook.py docs/handbook/chapters/*.md`
**Built in batch 0**, before any new chapter is written, and run at the end of every batch.

Checks, in order of value:

| # | Check | Why it exists |
|---|---|---|
| 1 | Figure caption count equals declared tier | Already found one live defect (Ch 1) |
| 2 | Diagram fences: 7-bit ASCII only, ≤78 columns | Already found two live defects (Ch 3, Ch 4) |
| 3 | Every figure has an axis label and a `(Dn ...)` type | Diagram type discipline decays first |
| 4 | 16 top-level sections, correct order and titles | The template is the book's contract |
| 5 | On-ramp blocks N1–N4 present | The whole point of Phase 3 |
| 6 | Header block parses; `Requires`/`Unlocks` match the spine table | Catches renumbering mistakes |
| 7 | Prohibited words | "just", "simply", "orchestrator", "workflow", bare "the agent" |
| 8 | Unknown or malformed provenance tags; §15 present | Provenance is the handbook's core discipline |
| 9 | Non-diagram code fences carry a language label | Phase 1 §7.2: an unlabelled code block is a defect |
| 10 | Cross-references resolve (`Ch NN` in 0–49, `Appendix A–J`, `Interlude I/II`) | 42 chapters of forward references |
| 11 | Cold open under 150 words | The one rule most likely to erode under deadline |
| 12 | Word count within the tier band | Catches a chapter that quietly became an essay |

The linter reports, it does not rewrite. Diagram authoring stays a human judgement.

---

## 5. Batch plan

One batch per level. Each batch ends with a linter pass, a README status update, and a single
conventional commit. Work does not start on batch *n+1* until batch *n* is reviewed.

Within a batch, chapters are written in dependency order in sub-groups of three to four, so a
style correction inside a level is cheap.

---

### Batch 0 — Foundation *(no new chapters)* — **DELIVERED**

| Deliverable | Detail |
|---|---|
| `tools/check_handbook.py` | 13 convention checks (§4) |
| On-ramp retrofit, Ch 0–7 | N1, N2, N3, N4 added to all eight chapters |
| Convention fixes | Ch 1 figure-count mismatch; Ch 4 80-column line; Ch 1 prohibited word; Ch 2 cold-open length |
| `docs/handbook/CONVENTIONS.md` | One-page authoring card consolidating Phase 1 §6–§7, Phase 2 §7, and this document |
| `tools/build_glossary.py` | **Beyond original scope.** Generates Appendix A from the per-chapter N4 tables, so the glossary cannot drift from the chapters |
| Appendix A | `docs/handbook/appendices/a-glossary.md`, generated |
| L0 level opener + SVG | `docs/assets/diagrams/level-0-evolution.svg` |

**Exit criteria met:** linter exits zero on Ch 0–7; all eight open with a plain-language block;
Appendix A contains every term Ch 0–7 define.

**Why it came first:** every convention defect not caught here is repeated 42 times. The linter
found three real defects in the existing chapters on its first run, and has since caught a
prohibited word or an over-wide diagram in *every* new chapter on first pass — including all three
written after it.

---

### Batch 1 — Finish Level 1 *(Ch 8–9, 2 chapters, Core, 10 figures)* — **DELIVERED**

Completes the high-level architecture. Ch 9 is the synthesis chapter for the whole level; after it,
a reader can draw the runtime from memory.

**Exit criteria met:** Level 1 shows `6 of 6` in the handbook README; L1 level opener written.

---

### Batch 2 — Level 2 *(Ch 10–20, 11 chapters, all Full, 99 figures)* — **7 of 11**

The largest batch and the heart of the book: every core component, each with nine diagrams.
Sub-groups: `C10–C12` (planner, context, memory) → `C13–C15` (reasoning, tools, ACI) →
`C16–C18` (observation, state manager, runtime loop) → `C19–C20` (multi-agent, AHE overview).

C18 is the keystone chapter — the runtime loop is what every prior chapter has been assembling.
It is written last in its sub-group and gets an explicit consistency pass against C5, C6, C17.

Also in this batch: **Interlude I — Assembling a Minimal Runtime**, L2 opener, L2 SVG.

**Exit criteria:** a reader who has read C0–C20 could implement stages 0–2 of the architecture
roadmap. Interlude I references only chapters that precede it and introduces no new terms.

---

### Batch 3 — Level 3 *(Ch 21–32, 12 chapters, 5 Full + 7 Core, 80 figures)*

Durability, the event spine, scheduling, task graphs, world model, planning algorithms, failure
and rollback, grading, long-running behaviour, human authority, safety, distribution.

Two chapters need explicit care:
- **C25 The World Model** carries almost no `[AHE]` or `[DAR]` weight (Phase 1 Decision 4). It
  opens by declaring itself the most speculative chapter in the book, per the resolved
  "keep and re-scope" decision.
- **C30 Human Authority** is where the effectful-tool tag from C14 becomes the entire safety
  model. It must not restate C14; it must consume it.

Also: L3 opener, L3 SVG.

---

### Batch 4 — Level 4 *(Ch 33–41, 9 chapters, all Core, 45 figures)*

Production engineering. C41 Evaluation Infrastructure is the gate into Level 5 and must leave
the reader able to score a harness change before Level 5 asks a machine to make one.

Also: **Interlude II — Anatomy of a Bad Week**, L4 opener, L4 SVG.

---

### Batch 5 — Level 5 *(Ch 42–49, 8 chapters, 4 Full + 4 Core, 56 figures)*

The self-evolving loop. §14 becomes *Relation to the Base Runtime* throughout, per Phase 1 §1.3.

C48 (Limits) is the chapter that keeps the book honest: non-additive component gains, ~5×
fix-prediction, ~2× regression-prediction. It is written before C49 so that governance is framed
as a response to a measured blindness rather than a general precaution.

Also: L5 opener.

---

### Batch 6 — Close the book

| Deliverable | Detail |
|---|---|
| Front matter F.1–F.4 | Written last, because F.1 (how to read this handbook) can only be honest once the tracks exist |
| Appendices A–J | Assembled from the per-chapter N4 tables, port signatures, failure tables, and anti-pattern mentions accumulated across batches 1–5 |
| Full cross-reference pass | Every `Ch NN §M` resolved against the final text |
| Compiled DOCX v1.0 | Regenerated from Markdown, replacing the v0.8 draft |
| README + docs/README + handbook README | Status tables move to complete |

---

## 6. Per-chapter content briefs

Source for each brief: Phase 1 §2 (the question the chapter answers, at old numbering) mapped
through the Phase 2 §3 renumbering table, plus the four chapters Phase 2 added. Tier and figure
budget are from Phase 2 §2.

### 6.1 Level 1 — remaining

| Ch | File | Tier | The question it answers |
|---|---|---|---|
| 8 | `08-request-and-runtime-lifecycles.md` | Core | Two lifecycles routinely confused: the life of *a goal* (arrival, plan, steps, park, completion) and the life of *the runtime* (boot, claim, sweep, drain, deploy). Why recovery must be continuous, never a boot-time activity. |
| 9 | `09-three-flows-data-control-event.md` | Core | The same system read three ways. Control flow = who decides next. Data flow = what moves and how large it is. Event flow = what is durable and replayable. Reading a runtime along the wrong flow is why most agent codebases become unmaintainable. Synthesis chapter for Level 1. |

### 6.2 Level 2 — Core Runtime Components *(all Full tier, 9 figures each)*

| Ch | File | The question it answers |
|---|---|---|
| 10 | `10-the-planner.md` | Turning a goal into ordered steps and deciding what happens after each result `[DAR §10.1]`. Plan identity, replanning, why a replan must mint a new plan id. ReAct as a default, not a religion. |
| 11 | `11-the-context-system.md` | Context as a managed, budgeted resource rather than string concatenation. Assembly order, compaction thresholds, progressive disclosure `[AHE §3.2]`, cache-stable prefixes, and the "context as junk drawer" failure. |
| 12 | `12-the-memory-system.md` | Short-term vs long-term vs episodic vs procedural. Why AHE's ablation ranks long-term memory among the highest-value components `[AHE §4.4.1]` while prompt-only strategy regresses. Memory as a *file*, not a vector-store reflex. |
| 13 | `13-the-reasoning-engine.md` | The model port: one interface, metered, capped, abortable `[DAR §10.3]`. Effort tiers, sampling parameters, tool-call modes, token accounting, and why the provider is never visible above this line. |
| 14 | `14-the-tool-execution-engine.md` | Tool description and tool implementation as separate editable surfaces `[AHE §3.1]`. Schema validation, the pure/effectful tag `[DAR §8.1]`, the middleware pipeline, output normalisation and truncation. |
| 15 | `15-agent-computer-interface-design.md` | `[+]` The tool as the model experiences it: verbs, error messages, output shaping. Why the highest-yield harness edits are ACI edits, and why that is a different discipline from building the tool engine. |
| 16 | `16-the-observation-system.md` | How the runtime perceives itself: tracing, trajectory capture, result envelopes, and the split between *telemetry* (never durable) and *facts* (always durable) `[DAR §7.1]`. The chapter that makes Level 5 possible. |
| 17 | `17-the-state-manager.md` | Checkpointing, the lease plus version-CAS advance `[DAR §5.3]`, the run store, and why an advisory lock is the wrong tool. Recovery as one indexed query. |
| 18 | `18-the-runtime-loop.md` | **Keystone.** The Episode as a bounded execution window: checkpoint after every step, no scarce resource held across a model call `[DAR §5.1–5.2]`. The four exit conditions. Why step-budget = 1 is a dial, not an architecture. |
| 19 | `19-the-multi-agent-runtime.md` | Sub-agents as context isolation, not org charts. Delegation contracts, result marshalling, sandbox sharing, nesting limits `[AHE §3.1]`. When a sub-agent is worse than a tool. |
| 20 | `20-the-self-evolving-runtime-overview.md` | The closed loop in one chapter: three observability pillars, the Evolve Agent, the change manifest, Algorithm 1 `[AHE §3]`. Placed here so the reader carries the evolution frame through Levels 3 and 4. |

### 6.3 Level 3 — Advanced Runtime Architecture

| Ch | File | Tier | The question it answers |
|---|---|---|---|
| 21 | `21-durable-execution.md` | Full | Why a crash must lose at most one in-flight step. Checkpoints, replay, the determinism quarantine `[DAR §6.1]`, and when to stop growing this and buy an engine `[DAR §17]`. |
| 22 | `22-the-event-spine.md` | Full | The transactional outbox as the entire durability story `[DAR §7.1]`. Claim-based relay vs cursor, and why a cursor is a poison-event outage waiting to happen `[DAR §7.2]`. Partition-key selection. The command port, now named in the title. |
| 23 | `23-the-scheduler.md` | Full | Convoy effects, latency-class partitioning, model semaphores, per-tenant admission `[DAR §5.4]`. Why one global concurrency integer cannot bound three different resources. |
| 24 | `24-the-task-graph.md` | Core | From ordered steps to a DAG: dependency resolution, parallel steps, durable joins, fan-out/fan-in, cycle prevention. Extends C10's linear plan. |
| 25 | `25-the-world-model.md` | Core | How the runtime acquires, represents, and invalidates beliefs about its environment: repository maps, environment probes, service topology, staleness detection. Opens by declaring itself the book's most speculative chapter. |
| 26 | `26-planning-algorithms.md` | Core | Beyond ReAct: decomposition, least-to-most, tree search, contract-first planning `[AHE App. C]`, cost-aware plan selection, plan-repair vs replan. |
| 27 | `27-failure-recovery-and-rollback.md` | Core | The failure table as a design artefact `[DAR §14]`. Leases, attempt caps, dead letters, sweepers. Compensation vs rollback. Git-granularity rollback of harness edits `[AHE §3.1]`. |
| 28 | `28-reflection-grading-and-self-correction.md` | Core | Why model self-evaluation fails `[DAR §9.1]`. The Verdict contract: deterministic checks a model judgment may downgrade but never upgrade `[DAR §9.2]`. Golden sets. Evaluator-isomorphic validation `[AHE App. C.1]`. |
| 29 | `29-long-running-agents.md` | Core | Six-hour runs: time budgeting, step budgets, timeout coupling as a generalisation hazard `[AHE Limitations]`, background execution, progress that is not a fact, the boredom failure mode. |
| 30 | `30-human-authority.md` | Full | The gate as a durable park holding nothing `[DAR §8.2]`. Structural enforcement in the runner, never in the prompt `[DAR §8.1]`. Steer as goal amendment forcing a replan, unifying redirection with idempotency `[DAR §8.3]`. |
| 31 | `31-safety-sandboxing-and-untrusted-content.md` | Core | Sandbox lifecycle and isolation `[AHE App. A]`. Fetched content is data, never instruction `[DAR §8.4]`. Blast-radius design, capability scoping, and the self-modification governance gap the source leaves open. |
| 32 | `32-distributed-execution.md` | Full | Many workers, one run: lease + CAS at scale, sharded relays, cross-process fairness, clock assumptions, and the operational meaning of "exactly one driver at any instant" `[DAR §13]`. |

### 6.4 Level 4 — Production Engineering *(all Core tier, 5 figures each)*

| Ch | File | The question it answers |
|---|---|---|
| 33 | `33-scalability-and-capacity-planning.md` | Sizing pools, semaphores, and worker counts from measured service times. Why worker concurrency may exceed pool size `[DAR §5.2]`. Load shapes unique to agents. |
| 34 | `34-observability.md` | The eleven signals that make the runtime operable `[DAR §15]`, extended with trajectory-level tracing `[AHE App. A]`. Identity partial-match anomalies must alert, never log. |
| 35 | `35-cost-engineering-and-token-economics.md` | Reserve-then-settle budgeting `[DAR §6.4]`. Tokens/trial and success-per-million-tokens as first-class metrics `[AHE App. A]`. Why encoding behaviour in tools beats encoding it in prompts, on cost as well as quality. |
| 36 | `36-reliability-and-slos.md` | What to promise for a system that is non-deterministic by design. Liveness, error budgets, degradation modes, and the difference between an unavailable agent and a wrong one. |
| 37 | `37-tenancy-secrets-and-data-governance.md` | `[+]` Tenant isolation across runs, traces, and harness state. Redaction at capture. Retention for the trace store — the highest-risk data set in the architecture. |
| 38 | `38-deployment-versioning-and-configuration.md` | Versioning the harness separately from the model and the code. Config snapshots, model pinning, and why a model upgrade is a harness invalidation event `[AHE §1]`. |
| 39 | `39-gitops-and-cicd-for-agent-systems.md` | The harness workspace as a git repository with file-level diffs and rollback `[AHE §3.1]`. Promotion pipelines, canaries, shadow evaluation. |
| 40 | `40-testing-a-non-deterministic-system.md` | `[+]` Hermetic replay, fake ports, controlled clocks. What a unit test means when the unit calls a model. The prerequisite for trusting automatic rollback in C47. |
| 41 | `41-evaluation-infrastructure.md` | The prerequisite for all of Level 5. Benchmarks and their properties, `pass@1` conventions `[AHE App. A]`, rollouts per task, variance, the golden-set regression harness `[DAR §9.3]`. Build this before tuning anything. |

### 6.5 Level 5 — Self-Evolving Systems *(§14 becomes "Relation to the Base Runtime")*

| Ch | File | Tier | The question it answers |
|---|---|---|---|
| 42 | `42-the-case-for-harness-evolution.md` | Core | Manual harness engineering cannot keep pace with base-model releases `[AHE §1]`. Why the bottleneck is observability, not agent capability. What the ten-iteration result does and does not prove. |
| 43 | `43-component-observability.md` | Full | Seven orthogonal component types as files at fixed mount points `[AHE §3.1]`. Loose coupling, one failure pattern to one component class, the deliberately minimal seed, and why a pre-fitted seed destroys attribution. |
| 44 | `44-experience-observability.md` | Full | Ten million trace tokens to ten thousand tokens of evidence `[AHE §3.2]`. Trajectories as a navigable file environment, per-task analysis reports, the benchmark-level overview, progressive disclosure as a token strategy. |
| 45 | `45-decision-observability.md` | Full | Every edit as a falsifiable contract: failure evidence, root cause, targeted fix, predicted fixes, at-risk regressions, constraint level `[AHE §3.3]`. The manifest as the loop's evidence ledger. |
| 46 | `46-the-evolve-agent.md` | Full | Controllability constraints — workspace-only writes, read-only runs directory, non-deletable seed rules `[AHE §3.3]`. Choosing the right constraint level. The anti-pattern of repeatedly fixing at the wrong level. |
| 47 | `47-attribution-verdicts-and-rollback.md` | Core | Algorithm 1's phase ordering and why attribution runs *before* distillation `[AHE §3.3]`. Intersecting predicted sets with observed deltas. Keep / improve / rollback-and-pivot. |
| 48 | `48-limits.md` | Core | Effective edits do not stack: three positive single-component gains summing to +11.1 pp yield +7.3 pp together `[AHE §4.4.1]`. Fix-prediction ~5× random; regression-prediction ~2× `[AHE §4.4.2]`. Designing around a loop that cannot see what it is about to break. |
| 49 | `49-continuous-improvement-and-governance.md` | Core | Running the loop as production infrastructure. Human review gates on the evolution loop itself, misuse prevention, harness cleanup, and the honest framing of AHE as a controlled prototype `[AHE Limitations]`. |

---

## 7. Non-chapter artifacts

### 7.1 Level openers

One page before each level. Not a chapter: no template, no tier, no figure budget. Contains what
the reader will be able to do at the end of the level, what they must already hold, and the two
or three questions the level answers (Phase 2 §7.2). Each is paired with one SVG.

| Level | Opener file | SVG |
|---|---|---|
| 0 | `docs/handbook/levels/level-0-foundations.md` | `level-0-evolution.svg` *(new)* |
| 1 | `docs/handbook/levels/level-1-high-level-runtime.md` | `six-layer-agent-runtime.svg` *(exists)* |
| 2 | `docs/handbook/levels/level-2-core-components.md` | `level-2-component-map.svg` *(new)* |
| 3 | `docs/handbook/levels/level-3-advanced-runtime.md` | `level-3-advanced-runtime.svg` *(new)* |
| 4 | `docs/handbook/levels/level-4-production.md` | `level-4-production-surfaces.svg` *(new)* |
| 5 | `docs/handbook/levels/level-5-self-evolving.md` | `agentic-harness-engineering-loop.svg` *(exists)* |

### 7.2 Interludes

Unnumbered, no 16-section template, narrative. May reference any preceding chapter; may not
introduce new terminology (Phase 2 §7.2).

- **Interlude I — Assembling a Minimal Runtime** (after Ch 20, batch 2). Walks stages 0–2 of the
  architecture roadmap as one continuous build, so the reader sees C5, C14, C17, C18, C21, C22
  fit together before Level 3 adds depth.
- **Interlude II — Anatomy of a Bad Week** (after Ch 41, batch 4). Three incident shapes with
  their signal signatures, read through the Level 4 observability surfaces.

### 7.3 Appendices

Accreted continuously, closed in batch 6. Each has a working file under
`docs/handbook/appendices/` from batch 0 so that content lands as it is written rather than being
reconstructed at the end.

| # | Appendix | Assembled from |
|---|---|---|
| A | Glossary | The N4 "Terms introduced" table of every chapter |
| B | Naming Conventions | Phase 1 §7 + Phase 2 §7.3, consolidated |
| C | Diagram Conventions and Legend | Phase 1 §6, consolidated |
| D | Reference Schema | The tables named in every §9 |
| E | Port Signatures | The `Protocol` definitions in every §8 |
| F | Invariant Checklist | Runtime invariants + evolution invariants, each with a test recipe cross-linked to C40 |
| G | Failure Mode Catalogue | The §11 failure table of every chapter |
| H | Anti-Pattern Index | Every anti-pattern named in the book, with its diagnosing chapter |
| I | Bibliography and Source Map | Every `[AHE §n]` and `[DAR §n]` citation, reverse-indexed |
| J | Chapter Prerequisites and Unlocks | The dependency graph as a flat table, generated from the header blocks |

Appendices D, E, G, H, I, and J are **generated or semi-generated** from the chapters by the
linter's data model, not hand-maintained. That is the only way they stay true across 50 chapters.

---

## 8. Repository artifacts to keep in sync

At the end of every batch:

| Artifact | Update |
|---|---|
| `docs/handbook/README.md` | Available-chapters table; completion-status table; "next planned" line |
| `docs/README.md` | Artifact map "Current state" column |
| `README.md` | Project-status paragraph (`N of the planned 50 chapters`) |
| `docs/assets/diagrams/README.md` | Any new SVG, with its one-paragraph description |
| Compiled DOCX | Regenerated in batch 6 only; the v0.8 draft is not updated per batch |
| Git | One commit per batch, conventional format: `docs: add Level 2 chapters 10-20` |

The status tables in those three READMEs are currently accurate. They are the first thing a
reader checks and the easiest thing to leave stale; treat a mismatch as a batch failure.

---

## 9. Risks

| Risk | Handling |
|---|---|
| **Convention drift over 42 chapters** | The linter, built in batch 0 and run at every batch boundary. This is the single highest-value item in the plan. |
| **On-ramp blocks decay into filler** | N1 has a hard word band; N2 requires the "where it breaks" half; N3 must be a forced-move derivation. All three are linter-checked for presence and hand-checked for quality at the level review. |
| **Level 2 is 11 Full-tier chapters — the batch is too big to review** | Split into four sub-groups with an internal consistency pass; C18 written last. |
| **Chapter briefs drift from the sources as depth increases** | `[AHE]` and `[DAR]` may only tag statements the source literally makes (Phase 1 §0). Extrapolation is `[INF]`. Appendix I reverse-indexes every citation in batch 6, which surfaces any tag applied to a claim its source does not contain. |
| **C25 World Model has thin provenance** | Already resolved as "keep and re-scope"; the chapter declares its own speculativeness in §1. |
| **Level 5 depends on Level 4 being real** | C41 is the gate. If evaluation infrastructure is thin, Level 5 becomes assertion. Batch 4 does not close until C41 leaves a reader able to score a harness change. |
| **Scale fatigue: the book stalls at 60%** | Batches are level-shaped so any stopping point is a coherent artifact. A handbook that ends cleanly after Level 3 is a usable book; one that ends mid-level is not. |

---

## 9a. Where this stands, and how to resume

**Delivered: batches 0 and 1 in full, plus the first seven chapters of batch 2.** The handbook is at 17 of
50 chapters, Levels 0 and 1 are complete, and the linter reports zero errors across all of them.

| | State |
|---|---|
| Chapters | 0–16 written; Level 0 complete, Level 1 complete, Level 2 at 7 of 11 |
| Tooling | `check_handbook.py` (13 checks), `build_glossary.py` (Appendix A, 110 terms) |
| Conventions | `CONVENTIONS.md` is the single authoring card; four revisions recorded in its §7 |
| Level openers | L0 and L1 written; L2–L5 outstanding |
| SVGs | 5 of the planned 9 (`level-0-evolution.svg` added) |
| Commits | one per batch, on `main` |

**To resume, start at Chapter 17 (The State Manager).** The procedure for any remaining chapter:

1. Read the chapter's brief in §6 of this document, and its `Requires`/`Unlocks` in the Phase 2 §4
   spine.
2. Read `CONVENTIONS.md` — particularly §2 (the four on-ramp blocks) and §8 (definition of done).
3. Write the chapter against the §3 skeleton. Copy the header block from the preceding chapter and
   edit it; the linter checks that `Requires` precede and `Unlocks` follow this chapter's number.
4. Run `python3 tools/check_handbook.py`. It must exit zero.
5. Run `python3 tools/build_glossary.py` to fold the new N4 table into Appendix A.
6. Update the three READMEs' status tables, tick the boxes in §10, and commit.

**Three things learned writing Ch 8, 9, and 10**, which the remaining chapters should carry:

- **Plan the nine figures before writing a Full-tier chapter.** Nine ASCII figures in document order
  cannot be retrofitted cheaply; Ch 10 needed a renumbering pass because two were added late. Decide
  the D1–D9 set and which section each lands in first.
- **Write N3 early, not last.** The forced-move derivation repeatedly surfaced the strongest framing
  in the chapter. In Ch 10 it produced the observation that idempotency and human authority are the
  same problem — which then became the chapter's spine.
- **Expect the linter to fail on first run.** It caught a prohibited word or an over-wide diagram in
  every chapter written so far. That is the tool working, not a nuisance; do not weaken a check to
  make a chapter pass.

---

## 10. Progress tracker

### Batch 0 — Foundation — **complete**
- [x] `tools/check_handbook.py` with all 12 checks
- [x] `docs/handbook/CONVENTIONS.md` authoring card
- [x] Appendix working files created under `docs/handbook/appendices/`
- [x] Ch 0 on-ramp retrofit · [x] Ch 1 · [x] Ch 2 · [x] Ch 3 · [x] Ch 4 · [x] Ch 5 · [x] Ch 6 · [x] Ch 7
- [x] Ch 1 figure-count defect resolved
- [x] Ch 4 80-column diagram line fixed; Ch 1 prohibited word; Ch 2 cold open
- [x] L0 opener + `level-0-evolution.svg`
- [x] Linter exits zero on Ch 0–7
- [x] `tools/build_glossary.py` (beyond scope): Appendix A generated from the chapters

### Batch 1 — Level 1 complete — **complete**
- [x] C8 Request Lifecycle and Runtime Lifecycle
- [x] C9 Three Flows: Data, Control, Event
- [x] L1 opener
- [x] READMEs updated · [x] linter green · [x] commit

### Batch 2 — Level 2 — **7 of 11**
- [x] C10 · [x] C11 · [x] C12 · [x] C13 · [x] C14 · [x] C15 · [x] C16 · [ ] C17 · [ ] C18 · [ ] C19 · [ ] C20
- [ ] Interlude I
- [ ] L2 opener + `level-2-component-map.svg`
- [ ] C18 consistency pass against C5, C6, C17
- [ ] READMEs updated · [ ] linter green · [ ] commit

### Batch 3 — Level 3
- [ ] C21 · [ ] C22 · [ ] C23 · [ ] C24 · [ ] C25 · [ ] C26 · [ ] C27 · [ ] C28 · [ ] C29 · [ ] C30 · [ ] C31 · [ ] C32
- [ ] L3 opener + `level-3-advanced-runtime.svg`
- [ ] READMEs updated · [ ] linter green · [ ] commit

### Batch 4 — Level 4
- [ ] C33 · [ ] C34 · [ ] C35 · [ ] C36 · [ ] C37 · [ ] C38 · [ ] C39 · [ ] C40 · [ ] C41
- [ ] Interlude II
- [ ] L4 opener + `level-4-production-surfaces.svg`
- [ ] READMEs updated · [ ] linter green · [ ] commit

### Batch 5 — Level 5
- [ ] C42 · [ ] C43 · [ ] C44 · [ ] C45 · [ ] C46 · [ ] C47 · [ ] C48 · [ ] C49
- [ ] L5 opener
- [ ] §14 variant applied throughout
- [ ] READMEs updated · [ ] linter green · [ ] commit

### Batch 6 — Close
- [ ] F.1 · [ ] F.2 · [ ] F.3 · [ ] F.4
- [ ] Appendix A · [ ] B · [ ] C · [ ] D · [ ] E · [ ] F · [ ] G · [ ] H · [ ] I · [ ] J
- [ ] Full cross-reference resolution pass
- [ ] Compiled DOCX v1.0
- [ ] All three READMEs report complete
- [ ] Final linter pass across all 50 chapters

---

*End of Phase 3 plan. Batch 0 begins on approval.*
