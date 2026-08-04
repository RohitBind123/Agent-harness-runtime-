# Next-Generation Autonomous AI Agent Architecture Handbook
## PHASE 2 — Revised Blueprint (v2)

> **Status:** Draft for approval. Still no handbook content written.
> **Supersedes:** Phase 1 blueprint, for the Table of Contents, dependency graph, roadmaps, and
> chapter numbering. Phase 1 remains authoritative and unchanged for the **glossary (§5)**,
> **diagram conventions (§6)**, and **naming conventions (§7)**, except for the deltas in §7 below.
> **Next:** Phase 3, one chapter at a time, starting with Chapter 0.

---

## 1. What Changed and Why

Four decisions from Phase 1 are locked. Decision 4 is now resolved. Beyond that, this revision is
the result of reading the v1 outline as an adversary: looking for concepts a Full Stack AI Engineer
would need and not find, and for places where a chapter used a word the reader had not been given
yet.

### 1.1 Summary

| Change | Count |
|--------|-------|
| Chapters added | 4 |
| Chapters reordered | 4 (all within Level 1) |
| Chapters retitled / re-scoped | 3 |
| Interludes added | 2 |
| Appendices added | 1 |
| Boundary contracts declared between overlapping chapters | 3 |
| Candidate chapters considered and rejected | 5 |

**New total:** 50 chapters (0–49) · 2 interludes · 10 appendices.

### 1.2 Decision 4, resolved

**Ch 25 (was Ch 23) — The World Model: kept, re-scoped, retitled.**
It now answers exactly one question: *how does the runtime acquire, represent, and invalidate its
beliefs about the environment?* Repository maps, environment probes, service topology, staleness
detection, and belief invalidation on external change. It opens by declaring itself the most
speculative chapter in the book and carries the heaviest `[INF]` / `[BP]` density. Ch 26 (Planning
Algorithms) is hollow without it — a planner that cannot say what it believes is true is just a
text generator with a numbered list.

### 1.3 The flow defect this pass found

In v1's Level 1, **Ch 5 (Request Lifecycle) traced a goal through Runs, Episodes, and Parks — three
chapters before Ch 7 defined them.** The reader would have met the vocabulary inside a narrative
that assumed it. That is precisely the failure the teaching philosophy forbids.

Level 1 is therefore reordered so the nouns and the ownership rules land first, then the boundary
where work enters, then the trace, then the synthesis:

```
  v1:  Layers -> Lifecycles -> Three Flows -> Five Nouns -> State Separation
                    ^^^^^^ uses vocabulary defined two chapters later

  v2:  Layers -> Five Nouns -> State Separation -> Edge -> Lifecycles -> Three Flows
                                                                          ^^^^^^^^^^
                                                            now a synthesis, not a preview
```

Reading the whole system three ways (data, control, event) is a *closing* move for a level, not an
opening one. It only works once there is a system in the reader's head to re-read.

### 1.4 The four added chapters

Each was added because a working engineer would hit it in week one and find nothing in the book.

| New chapter | Why v1 was incomplete without it |
|-------------|----------------------------------|
| **Ch 7 — The Edge and the Client Contract** | v1 described the edge in one row of a layers table and never returned. But the edge is where every goal enters, where every approval arrives, and where the progress-versus-fact distinction `[DAR §7.1]` is either honoured or violated. Teams routinely put the agent loop in the HTTP handler; a table row does not prevent that, a chapter does. |
| **Ch 15 — Agent–Computer Interface Design** | Ch 14 teaches the tool *engine*: registration, schemas, dispatch, middleware. It does not teach how to design a tool a model can actually use — error messages as feedback, output shaping, affordance discovery, failure legibility. This is a distinct discipline `[BP: SWE-agent]` and it is where AHE's largest tool gain lives: an evolved shell that auto-surfaces contract hints from files near each command `[AHE §4.4.1]`. Without this chapter the reader builds a correct engine and bad tools. |
| **Ch 37 — Tenancy, Secrets, and Data Governance** | v1 treated tenancy only as a fairness problem (admission caps) and never as a security or compliance boundary. Meanwhile the architecture stores complete trajectories — AHE's loop consumes roughly ten million tokens of them per iteration `[AHE §3.2]`. Those traces contain every credential, customer record, and file the agent touched. Retention, redaction, and per-tenant isolation of the trace store is a production requirement, not an appendix. |
| **Ch 40 — Testing a Non-Deterministic System** | v1 jumped from CI/CD straight to benchmark evaluation. But a runtime needs ordinary tests too, and they are unusually hard here: you must fake the model port, control the clock, force lease expiry, assert that a replay does not re-spend, and prove `kill -9` at every step boundary is safe. Evaluation scores the *agent*; testing proves the *runtime*. Conflating them is how teams ship a well-scored agent on a runtime that loses work. |

### 1.5 Boundary contracts

Three pairs of chapters risk saying the same thing twice. Each now has an explicit, one-sentence
division of labour, restated in both chapters' section 10 (*Communication*).

| Pair | Division |
|------|----------|
| Ch 17 State Manager ↔ Ch 21 Durable Execution ↔ Ch 32 Distributed Execution | **17** owns checkpoint semantics and the run store on one node. **21** owns crash, replay, and the determinism quarantine. **32** owns many workers contending for one run. The lease is *introduced* once, in 17, and only *applied* in 21 and 32. |
| Ch 28 Grading ↔ Ch 41 Evaluation | **28** grades one step's output inside a live run and returns a Verdict. **41** scores a whole configuration across a benchmark and returns a number. Same discipline, different unit and different consumer. |
| Ch 20 AHE Overview ↔ Level 5 | **20** must be readable as a complete, if shallow, account of the loop. Level 5 may deepen but may not contradict. Any statement in Ch 20 that Level 5 later qualifies is a defect in Ch 20. |

### 1.6 Candidates considered and rejected

Recorded so the omissions are visible as choices rather than oversights.

| Rejected | Reason |
|----------|--------|
| A chapter on RAG and vector retrieval | It is one retrieval strategy inside Ch 12 (Memory), not a runtime subsystem. Elevating it to a chapter would misrepresent the architecture — and both sources locate durable knowledge in files, not embeddings. |
| A chapter on fine-tuning and RL | Out of scope by the book's thesis. AHE frames harness evolution as the *complementary* axis to model-side training `[AHE §5]`; teaching both halves would double the book and blur the argument. |
| A chapter on agent protocols (MCP and similar) | Folded into Ch 14 §10 as a transport and discovery concern. A protocol changes how tools arrive, not what a tool is or how the runtime governs it. |
| A chapter on agent UI and frontend design | Out of scope. Ch 7 specifies the *contract* the surface must satisfy; what the surface looks like is a product question. |
| A chapter on prompt engineering | Refused on thesis grounds. The book's central empirical claim is that the system prompt is the weakest editable surface — the only single-component swap in the AHE ablation that *regresses* `[AHE §4.4.1]`. A prompt-engineering chapter would undercut 49 others. |

---

## 2. Revised Table of Contents

New material marked **`[+]`**. Moved material marked **`[»]`**. Re-scoped marked **`[~]`**.

### Front Matter
- **F.1** How to Read This Handbook — the four tracks
- **F.2** Notation, Tags, and Diagram Legend *(reference card; inside cover)*
- **F.3** The Running System: ARK and Atlas
- **F.4** What This Handbook Is Not

---

### LEVEL 0 — FOUNDATIONS · Ch 0–3
*Exit condition: the reader stops thinking of an agent as a prompt in a while loop.*

| # | Chapter | Tier |
|---|---------|------|
| 0 | Evolution of AI Systems | Light |
| 1 | Anatomy of an Agent: Model, Harness, Environment | Light |
| 2 | Why an Agent Runtime Is a Distributed System | Light |
| 3 | Mental Models and the Reference System | Light |

---

### LEVEL 1 — HIGH-LEVEL RUNTIME ARCHITECTURE · Ch 4–9
*Exit condition: the reader can draw the whole system from memory, and can say which layer any given line of code belongs in.*

| # | Chapter | Note | Tier |
|---|---------|------|------|
| 4 | The Complete Runtime: Layers and Process Topology | | Full |
| 5 | The Five Nouns: Run, Episode, Step, Activity, Park | `[»]` was Ch 7 | Core |
| 6 | State Separation: Run State, Domain State, Model State | `[»]` was Ch 8 | Core |
| 7 | **The Edge and the Client Contract** | `[+]` | Core |
| 8 | Request Lifecycle and Runtime Lifecycle | `[»]` was Ch 5 | Core |
| 9 | Three Flows: Data, Control, Event | `[»]` was Ch 6 | Core |

**Ch 7 scope.** Accepting goals, approvals, and signals. Read models and projections. Streaming
progress over a notification channel, never through the outbox `[DAR §7.1]`. Why the edge runs no
consumer, no loop, and no model call `[DAR §4.2]` — and the three ways teams break that rule.
Backpressure and client reconnection against a run that outlives the connection.

---

### LEVEL 2 — CORE RUNTIME COMPONENTS · Ch 10–20
*Exit condition: the reader can implement each subsystem in isolation and state its contract to every other.*

| # | Chapter | Note | Tier |
|---|---------|------|------|
| 10 | The Planner | | Full |
| 11 | The Context System | | Full |
| 12 | The Memory System | | Full |
| 13 | The Reasoning Engine | | Full |
| 14 | The Tool Execution Engine | | Full |
| 15 | **Agent–Computer Interface Design** | `[+]` | Full |
| 16 | The Observation System | | Full |
| 17 | The State Manager | | Full |
| 18 | The Runtime Loop | keystone | Full |
| 19 | The Multi-Agent Runtime | | Full |
| 20 | The Self-Evolving Runtime (AHE) — Overview | | Full |

**Level 2 reading order, justified.** Decide → remember → think → act → *be usable* → see →
persist → loop → delegate → evolve. The alternative order (persistence first, mirroring the build
sequence in §4) was rejected: build order and reading order optimise different things, and the
handbook says so out loud in the Level 2 opener rather than pretending they coincide.

**Ch 15 scope.** Tools as an interface for a reader that cannot ask questions. Error messages as
the primary feedback channel. Output shaping, truncation, and what to surface unprompted. Affordance
discovery. Idempotent-by-design verbs. The measured result that a 1364-line evolved shell tool
outperforms a bare one `[AHE §4.4.1]`, and what it encoded.

---

### **INTERLUDE I — Assembling a Minimal Runtime** `[+]`
*After Ch 20. Unnumbered, ~8 pages, no chapter template.*

Ten components have been built in isolation. This assembles the smallest honest version of Atlas
that runs: one tool, one planner, one loop, one table, no durability, no safety. Then it breaks it
four ways — kill the worker, double-deliver an event, let the model call hang, let the agent delete
its own output — and names which Level 3 chapter fixes each. The reader carries four concrete
failures into Level 3 instead of four abstractions.

---

### LEVEL 3 — ADVANCED RUNTIME ARCHITECTURE · Ch 21–32
*Exit condition: the reader can keep a six-hour, multi-tenant, irreversible-action agent alive and honest.*

| # | Chapter | Note | Tier |
|---|---------|------|------|
| 21 | Durable Execution | | Full |
| 22 | The Event Spine: Outbox, Relay, Command Port | `[~]` command port now named in the title | Full |
| 23 | The Scheduler: Queues, Work Classes, Admission | | Full |
| 24 | The Task Graph | | Core |
| 25 | The World Model: Environment Belief and Staleness | `[~]` re-scoped, retitled | Core |
| 26 | Planning Algorithms | | Core |
| 27 | Failure, Recovery, and Rollback | | Core |
| 28 | Reflection, Grading, and Self-Correction | | Core |
| 29 | Long-Running Agents and Multi-Step Planning | | Core |
| 30 | Human Authority: Gates, Parks, Signals, Steering | | Full |
| 31 | Safety, Sandboxing, and Untrusted Content | | Core |
| 32 | Distributed Execution | | Full |

---

### LEVEL 4 — PRODUCTION ENGINEERING · Ch 33–41
*Exit condition: the reader can run this for paying customers and know, before the customer does, that it is degrading.*

| # | Chapter | Note | Tier |
|---|---------|------|------|
| 33 | Scalability and Capacity Planning | | Core |
| 34 | Observability: Logging, Metrics, Tracing | | Core |
| 35 | Cost Engineering and Token Economics | | Core |
| 36 | Reliability and SLOs | | Core |
| 37 | **Tenancy, Secrets, and Data Governance** | `[+]` | Core |
| 38 | Deployment, Versioning, and Configuration | | Core |
| 39 | GitOps and CI/CD for Agent Systems | | Core |
| 40 | **Testing a Non-Deterministic System** | `[+]` | Core |
| 41 | Evaluation Infrastructure | gate into Level 5 | Core |

**Ch 37 scope.** The tenant as a security boundary, not only a fairness unit. Credential scoping and
secret injection into sandboxes. Trace stores as the highest-risk data in the system: what a
trajectory contains, redaction at capture time versus at read time, retention windows, and the
tension between deletion policy and the evidence corpus Level 5 depends on.

**Ch 40 scope.** Faking the model port deterministically. Controlling the clock. Forcing lease
expiry, relay redelivery, and mid-activity abort on demand. Hermetic replay of recorded activities.
Property tests for the nine invariants `[DAR §13]`. The `kill -9` matrix: crash at every step
boundary and assert the run resumes exactly once.

---

### **INTERLUDE II — Anatomy of a Bad Week** `[+]`
*After Ch 41. Unnumbered, ~10 pages, no chapter template.*

Three incident shapes traced end to end through the chapters that explain them: a silent
correctness failure (confident wrong output that passed grading), a capacity failure (one tenant
starving the pool), and an authority failure (an effectful call that should not have happened).
Each ends at the invariant that would have prevented it. This is the chapter that converts the
book from a design document into an operational instinct.

---

### LEVEL 5 — SELF-EVOLVING SYSTEMS · Ch 42–49
*Exit condition: the reader can build a loop that improves the harness unattended, and can say precisely where it is blind.*

| # | Chapter | Tier |
|---|---------|------|
| 42 | The Case for Harness Evolution | Core |
| 43 | Component Observability: The Editable Substrate | Full |
| 44 | Experience Observability: The Agent Debugger | Full |
| 45 | Decision Observability: The Change Manifest | Full |
| 46 | The Evolve Agent | Full |
| 47 | Attribution, Verdicts, and Automatic Rollback | Core |
| 48 | Limits: Non-Additive Components and Regression Blindness | Core |
| 49 | Continuous Improvement and the Governance of Self-Modification | Core |

---

### Appendices

| # | Appendix | Note |
|---|----------|------|
| A | Glossary | unchanged from Phase 1, plus §7 deltas below |
| B | Naming Conventions | unchanged, plus §7 deltas below |
| C | Diagram Conventions and Legend | unchanged, plus §7 deltas below |
| D | Reference Schema | + tenancy and retention columns (Ch 37) |
| E | Port Signatures (Python `Protocol`) | |
| F | Invariant Checklist | + test recipe per invariant, cross-linked to Ch 40 `[+]` |
| G | Failure Mode Catalogue | |
| H | Anti-Pattern Index | |
| I | Bibliography and Source Map | |
| **J** | **Chapter Prerequisites and Unlocks** | `[+]` the dependency graph as a flat table |

---

## 3. Renumbering Map

For carrying any notes made against v1.

| v1 | v2 | v1 | v2 | v1 | v2 |
|----|----|----|----|----|----|
| 0–4 | 0–4 | 18 | 20 | 33 | 35 |
| 5 | 8 | 19 | 21 | 34 | 36 |
| 6 | 9 | 20 | 22 | 35 | 38 |
| 7 | 5 | 21 | 23 | 36 | 39 |
| 8 | 6 | 22 | 24 | 37 | 41 |
| 9 | 10 | 23 | 25 | 38 | 42 |
| 10 | 11 | 24 | 26 | 39 | 43 |
| 11 | 12 | 25 | 27 | 40 | 44 |
| 12 | 13 | 26 | 28 | 41 | 45 |
| 13 | 14 | 27 | 29 | 42 | 46 |
| 14 | 16 | 28 | 30 | 43 | 47 |
| 15 | 17 | 29 | 31 | 44 | 48 |
| 16 | 18 | 30 | 32 | 45 | 49 |
| 17 | 19 | 31 | 33 | — | — |
| — | — | 32 | 34 | — | — |

New in v2: **7**, **15**, **37**, **40**.

---

## 4. Revised Dependency Spine

Only the changed regions are redrawn. Level 3 and Level 5 keep their v1 shape at the new numbers.

```
  LEVEL 1
                        +-------------------+
                        | C4  Layers/Topo   |
                        +---------+---------+
                                  |
                  +---------------+---------------+
                  v                               v
        +---------+---------+           +---------+---------+
        | C5  Five Nouns    |---------->| C6  State Separ.  |
        +---------+---------+           +---------+---------+
                  |                               |
                  +---------------+---------------+
                                  v
                        +---------+---------+
                        | C7  The Edge      |   <-- new
                        +---------+---------+
                                  v
                        +---------+---------+
                        | C8  Lifecycles    |
                        +---------+---------+
                                  v
                        +---------+---------+
                        | C9  Three Flows   |   synthesis of Level 1
                        +---------+---------+
  LEVEL 2                         |
     +---------+---------+--------+--------+---------+
     v         v         v                 v         v
  +--+---+ +---+---+ +---+---+         +---+---+ +---+---+
  |C10 Pl| |C11 Cx | |C12 Mem|         |C13 Rsn| |C14 Tls|
  +--+---+ +---+---+ +---+---+         +---+---+ +---+---+
                                                     |
                                              +------v------+
                                              | C15 ACI     |   <-- new
                                              +------+------+
     +---------+---------+--------+--------+---------+
                                  v
                        +---------+---------+
                        | C16 Observation   |
                        +---------+---------+
                                  v
                        +---------+---------+
                        | C17 State Manager |
                        +---------+---------+
                                  v
                        +---------+---------+
                        | C18 Runtime Loop  |   keystone
                        +---------+---------+
                                  |
                        +---------+---------+
                        v                   v
              +---------+------+   +--------+-------+
              | C19 Multi-Agent|   | C20 AHE Overvw |
              +---------+------+   +--------+-------+
                        |                   |
                        +---------+---------+
                                  v
                        ===  INTERLUDE I  ===
                                  v
                             LEVEL 3 (C21-C32)
                                  v
                             LEVEL 4 (C33-C41)
                                  v
                        ===  INTERLUDE II  ===
                                  v
                             LEVEL 5 (C42-C49)
```

### 4.1 Long edges, renumbered and extended

| From | To | Why |
|------|----|-----|
| C6 State Separation | C21, C32, C47 | Rollback and attribution are meaningless if run state leaked into the domain |
| C7 Edge | C30, C34 | Approvals arrive here; progress must never become a fact |
| C10 Planner (plan identity) | C21, C24, C30 | Replan-mints-new-plan is what unifies steering with idempotency |
| C14 Tools (pure/effectful) | C30, C31, C46 | The tag is the entire safety model and the highest-leverage evolution surface |
| **C15 ACI** | **C44, C46** | `[+]` The Evolve Agent's most productive edits are ACI edits; Ch 15 is what makes them legible |
| C16 Observation System | C34, C37, C44 | Trajectory capture is the raw material of the evidence corpus — and of the governance problem |
| C17 State Manager (lease + CAS) | C23, C27, C32 | Concurrency, sweeping, and fairness all reduce to lease semantics |
| C18 Runtime Loop (budgets) | C29, C33, C35 | Step and wall-clock budgets set every capacity and cost number downstream |
| C20 AHE Overview | C34, C39, C41 | Observability, GitOps, and evaluation are built *for* the loop |
| C28 Grading | C41, C45, C47 | A verdict is what makes a manifest prediction falsifiable |
| **C40 Testing** | **C47** | `[+]` Automatic rollback is untrustworthy without a hermetic replay harness |
| C41 Evaluation | all of Level 5 | Without a stable score, evolution is trial-and-error |

### 4.2 Critical path, renumbered

```
C0 -> C1 -> C3 -> C4 -> C5 -> C6 -> C14 -> C17 -> C18 -> C20
   -> C21 -> C22 -> C28 -> C30 -> C41 -> C43 -> C45 -> C47 -> C48
```

19 of 50 chapters. Ch 7, 15, 37, and 40 are depth, not gate — consistent with adding them without
lengthening the minimum path.

---

## 5. Revised Learning Roadmap

| Track | For | Chapters | Est. |
|-------|-----|----------|------|
| **T1 · Orientation** | "I need to speak this language by Friday." | F.1–F.4, C0–C5, C9, C18, C20, C48 | ~1 day |
| **T2 · Build the runtime** | "I am writing this code." | C0–C32 in order + Interlude I, then App. D, E, F | ~5 weeks |
| **T3 · Operate it** | "It exists; make it survivable." | C16, C17, C21–C23, C27, C31–C41 + Interlude II, App. G | ~2 weeks |
| **T4 · Evolve it** | "Make it improve itself." | C14, C15, C16, C20, C28, C39, C40, C41, C42–C49 | ~1 week |

T4 now includes Ch 15 and Ch 40. Both are new prerequisites: an evolution loop edits tool interfaces
constantly, and it cannot be trusted to roll itself back without a replay harness.

---

## 6. Revised Architecture Roadmap

Stage content is unchanged; chapter references are renumbered and two stages gain a chapter.

| Stage | Build | Chapters | Done when |
|-------|-------|----------|-----------|
| 0 · Spine | Outbox, claim relay, one queue, command port | C22 | An event written by the edge wakes a handler in the worker |
| 1 · Run | Runs table, lease + version CAS, episode driver, one hardcoded step | C5, C17, C18 | A run advances and survives `kill -9` mid-step |
| 2 · Activity | Activity ledger, identity hash, lease, abort signal, one real tool | C13, C14, **C15**, C21 | A model call runs off-lock and a replay never re-spends |
| 3 · Gate | Approval port, park, resume on the decision event | C30 | A run parks for a day and resumes at the right step |
| 4 · Grader | Deterministic checks, golden set replayed in CI | C28, **C40**, C41 | You can tell whether a change made the agent better or worse |
| 5 · Control | Signals, cancellation, progress streaming, per-tenant admission | C7, C23, C30 | A person redirects a running agent in under two seconds |
| 6 · Scale | Work-class split, budgets, dead letter, dashboards, soak | C23, C27, C33–C37 | One tenant's slow work is invisible to every other tenant |
| 7 · Substrate | Harness components as files at fixed mount points; git-backed workspace | C14, C39, C43 | A component can be swapped and rolled back without touching runtime code |
| 8 · Loop | Trace distillation, evidence corpus, change manifest, attribution, rollback | C44–C47 | Ten unattended iterations run end to end and rejected edits revert themselves |

---

## 7. Convention Deltas

Phase 1's §5, §6, and §7 stand. These are additions only.

### 7.1 New glossary terms

| Term | Definition | Tag |
|------|------------|-----|
| **Agent–Computer Interface (ACI)** | The design surface of a tool as experienced by a model: its verbs, its error messages, its output shaping. Distinct from the tool engine that executes it. | `[BP]` |
| **Read model** | A projection of run state shaped for a client, built by the edge, never authoritative. | `[INF]` |
| **Progress** | Telemetry with no business meaning, streamed directly to a client and never written to the outbox. The opposite of a fact. | `[DAR]` |
| **Hermetic replay** | Re-executing a recorded run with every port faked and the clock controlled, producing a byte-identical trace. The basis of runtime testing and of golden-set scoring. | `[INF]` |
| **Fake port** | A test double implementing a port `Protocol` with scripted, deterministic responses. Not a mock: it has behaviour, not just expectations. | `[BP]` |
| **Incident shape** | A recurring class of production failure with a characteristic signal signature. Interlude II names three. | `[INF]` |
| **Trace store** | The durable home of raw trajectories. The highest-risk data set in the architecture and the input to experience observability. | `[INF]` |
| **Redaction at capture** | Removing secrets from a trajectory as it is recorded, rather than when it is read. The only approach compatible with an automated evidence corpus. | `[INF]` |
| **Belief staleness** | The gap between what the world model asserts and what the environment currently is. Detected, not assumed. | `[INF]` |
| **Environment probe** | A cheap, pure tool call whose only purpose is to refresh or falsify a belief. | `[INF]` |

### 7.2 New structural conventions

**Chapter header block.** Every chapter opens with a fixed four-line block before section 1, so the
dependency graph is available locally and the reader never has to leaf backwards:

```
  Level 2 · Chapter 15
  AGENT-COMPUTER INTERFACE DESIGN
  Requires   C13 Reasoning Engine, C14 Tool Execution Engine
  Unlocks    C44 Agent Debugger, C46 Evolve Agent
  Diagrams   Full (9)
```

**Cold open.** Section 1 (*Motivation*) of every chapter begins with a concrete failure in Atlas —
a specific bad run, in under 150 words — before any abstraction. The template's "why previous
architectures failed" requirement is satisfied by narrative, not assertion.

**Level openers.** One page before each level: what the reader will be able to do at the end, what
they must already hold, and the two or three questions the level answers. Not a chapter; no template.

**Interludes.** Unnumbered, no 16-section template, no `[Tier]` designation. Written as narrative.
They may reference any chapter that precedes them and may not introduce new terminology.

### 7.3 Naming additions

| Thing | Convention | Example |
|-------|-----------|---------|
| Fake ports in test code | `Fake<Port>` | `FakeModelPort`, `FakeApprovalPort` |
| Test clock | `clock` fixture, never `time.time()` in runtime code | `clock.advance(seconds=90)` |
| Read-model projections | `<noun>_view` | `run_progress_view`, `approval_queue_view` |
| Redaction rules | `redact.<category>` | `redact.credentials`, `redact.customer_pii` |
| Interlude cross-reference | `Interlude I §3` | — |

---

## 8. What I Need From You Before Phase 3

Nothing blocking. Phase 3 can begin with **Chapter 0 — Evolution of AI Systems** on your word.

Two things worth a glance first, since they are cheap to change now and expensive later:

1. **Interludes.** They are the one element with no precedent in your original structure. If you
   want a strictly uniform book, say so and I will delete both and fold Interlude II's incident
   analysis into Ch 36 (Reliability).
2. **Chapter length target.** Not yet set. At Full tier with nine diagrams, a chapter lands around
   6,000–9,000 words. Across 50 chapters that is a genuinely large book. I can hold Full-tier
   chapters to ~5,000 by tightening sections 8–10 (APIs, data structures, communication) into
   reference tables rather than prose. Your call on which way to lean.

---

*End of Phase 2 deliverable. Awaiting approval before Chapter 0.*
