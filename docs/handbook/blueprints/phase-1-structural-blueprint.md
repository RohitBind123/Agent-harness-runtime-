# Next-Generation Autonomous AI Agent Architecture Handbook
## PHASE 1 — Structural Blueprint

> **Status:** Draft for approval. No handbook content written yet.
> **Contains:** Table of Contents · Book Structure · Learning Roadmap · Dependency Graph ·
> Architecture Roadmap · Glossary · Terminology · Diagram Conventions · Naming Conventions
> **Next:** Phase 2 (refine this outline) only after your review.

---

## 0. Source Provenance Scheme

Two documents were attached. The handbook treats them as **two distinct primary sources** with
distinct tags, because they answer different questions and must never be conflated.

| Tag | Source | Answers |
|-----|--------|---------|
| `[AHE]` | *Agentic Harness Engineering* (Lin, Liu, Pan et al., preprint) | How does a harness **improve itself**? |
| `[DAR]` | *A Durable Agent Runtime — Reference Architecture v1.0* | How does a runtime **survive and stay safe**? |
| `[INF]` | Engineering inference | Follows from the sources but is not stated by them |
| `[BP]` | Industry best practice | Established outside both sources; attributed to its origin |
| `[FUT]` | Future proposal | Not yet built anywhere the author can verify |

**Hard rule for every chapter:** a claim carries exactly one tag. `[AHE]` and `[DAR]` may only be
applied to statements the source literally makes. Extrapolation from a source is `[INF]`, never the
source's tag. Section 15 of every chapter (*Industry Perspective*) restates the chapter's claims
grouped under these five headings, with no blending.

**Resolved.** `[DAR]` is **co-primary** with `[AHE]`. Both are literal sources of equal standing.
Neither may absorb the other's claims: where the two overlap (tool contracts, observability,
rollback), the handbook cites both separately and names the difference rather than merging them.

---

## 1. Book Structure

### 1.1 Vocabulary of the structure itself

Three organising words are used with fixed, non-interchangeable meanings:

| Word | Refers to | Example |
|------|-----------|---------|
| **Level** | A pedagogical tier of the book (0–5) | "Level 3 — Advanced Runtime Architecture" |
| **Layer** | A tier of the architecture being taught | "the Kernel layer" |
| **Stage** | A step in the incremental build order | "Stage 2 — Activity" |

Confusing Level with Layer is the single most common failure in books of this kind. Every diagram
legend restates which one it is showing.

### 1.2 The running system

Every chapter builds one system, not a series of unrelated examples.

- **ARK** — *Agent Runtime Kernel.* The runtime we design across the book. Domain-independent.
- **Atlas** — the product built on ARK: a coding agent that resolves issues in real repositories.
  Atlas exists so that every abstract port has a concrete implementation to point at.
- **ARK/Evolve** — the Level 5 outer loop that edits Atlas's harness. Introduced in Ch 18,
  built in Ch 38–45.

Nothing else is named. No chapter invents a new example system.

### 1.3 Shape of a chapter

The 16-section template you specified is fixed and applies to every numbered chapter.
Two mechanical exceptions, both required for internal consistency:

- **Section 14 (*Relation to AHE*)** — in Level 5 chapters the subsystem *is* AHE. There, section 14
  becomes **"Relation to the Base Runtime"**: how this evolution component constrains and is
  constrained by Levels 1–4. The section number and position never move.
- **Chapters 0–3** have no runtime subsystem to decompose. Sections 4–9 are retained but describe
  *mental models* rather than components, and section 14 is a forward reference. These four chapters
  are explicitly marked **Foundational Variant** so the reader knows the template is not broken.

### 1.4 Diagram budget per chapter

Not every chapter needs all nine diagrams; forcing them produces filler. Three tiers:

| Tier | Diagrams required | Applies to |
|------|-------------------|------------|
| **Full** | All 9 | Ch 4, 9–18, 19, 20, 21, 28, 30, 39, 40, 41, 42 |
| **Core** | High-Level Arch · Low-Level Arch · Sequence · Data Flow · State | Ch 5–8, 22–27, 29, 31–37, 38, 43–45 |
| **Light** | High-Level Arch · one conceptual diagram | Ch 0–3 |

The nine diagram types and their exact rendering rules are in §6.

---

## 2. Complete Table of Contents

### Front Matter

- **F.1** How to Read This Handbook — the three paths (learn · implement · review)
- **F.2** Notation, Tags, and Diagram Legend *(the reader's reference card; reproduced on the inside cover)*
- **F.3** The Running System: ARK and Atlas
- **F.4** What This Handbook Is Not

---

### LEVEL 0 — FOUNDATIONS
*Goal: the reader stops thinking of an agent as "a prompt in a while loop."*

| # | Chapter | The question it answers | Tier |
|---|---------|------------------------|------|
| **0** | **Evolution of AI Systems** | How did we get from a completion endpoint to a system that runs for six hours unattended? LLM → tool-using model → agent → autonomous agent → multi-agent → self-evolving. What each step added, and what each step broke. | Light |
| **1** | **Anatomy of an Agent: Model, Harness, Environment** | Where does the model end and the system begin? Introduces the harness as the model-external, editable surface `[AHE §1]`, and its seven component types. Establishes why harness quality is a first-class performance lever, not plumbing. | Light |
| **2** | **Why an Agent Runtime Is a Distributed System** | The four properties that appear the moment you ask for a goal instead of an answer: work outlives the request, is expensive and non-deterministic, touches the world, must be interruptible `[DAR §2.1]`. Why the in-process `while` loop fails on all four. | Light |
| **3** | **Mental Models and the Reference System** | Five reusable mental models (process/scheduler, ledger, contract, quarantine, control plane vs data plane). Introduces ARK and Atlas. The reader's map for the next 42 chapters. | Light |

---

### LEVEL 1 — HIGH-LEVEL RUNTIME ARCHITECTURE
*Goal: the reader can draw the whole system from memory before learning any component.*

| # | Chapter | The question it answers | Tier |
|---|---------|------------------------|------|
| **4** | **The Complete Runtime: Layers and Process Topology** | The six layers (Surface · Edge · Kernel · Ports · Domain · Substrate) and the two process types `[DAR §4]`. Why the edge runs no loop, no consumer, and no model call. The full wiring diagram the rest of the book zooms into. | Full |
| **5** | **Request Lifecycle and Runtime Lifecycle** | Two lifecycles that are routinely confused: the lifecycle of *a goal* (arrival → plan → steps → park → completion) and the lifecycle of *the runtime* (boot, claim, sweep, drain, deploy). Why recovery must be continuous rather than boot-only. | Core |
| **6** | **Three Flows: Data, Control, Event** | The same system read three ways. Control flow = who decides next. Data flow = what moves and how large it is. Event flow = what is durable and replayable. Reading a runtime along the wrong flow is why most agent codebases are unmaintainable. | Core |
| **7** | **The Five Nouns: Run, Episode, Step, Activity, Park** | The vocabulary the whole architecture rests on `[DAR §3.1]`, with lifetimes from milliseconds to weeks. Why "the agent" is not a noun in this system. | Core |
| **8** | **State Separation: Run State, Domain State, Model State** | The distinction implementations most often collapse `[DAR §3.3]`, extended with a third category the source does not name: **model state** (context window, cache, reasoning tokens) `[INF]`. The structural test: delete the runtime and the product must still compile. | Core |

---

### LEVEL 2 — CORE RUNTIME COMPONENTS
*Goal: the reader can implement each subsystem in isolation and knows its contract to the others.*

| # | Chapter | The question it answers | Tier |
|---|---------|------------------------|------|
| **9** | **The Planner** | Turning a goal into ordered steps, and deciding what happens after each result `[DAR §10.1]`. Plan identity, replanning, why a replan must mint a new plan id. ReAct as a default, not a religion. | Full |
| **10** | **The Context System** | Context as a managed, budgeted resource rather than a string concatenation. Assembly order, compaction thresholds, progressive disclosure `[AHE §3.2]`, cache-stable prefixes, and the failure mode of "context as junk drawer." | Full |
| **11** | **The Memory System** | Short-term vs long-term vs episodic vs procedural. Why AHE's ablation puts long-term memory among the highest-value components `[AHE §4.4.1]` while prompt-only strategy regresses. Memory as a *file*, not a vector store reflex. | Full |
| **12** | **The Reasoning Engine** | The model port: one interface, metered, capped, abortable `[DAR §10.3]`. Reasoning effort tiers, sampling parameters, tool-call modes, token accounting, and why the provider must never be visible above this line. | Full |
| **13** | **The Tool Execution Engine** | Tool description vs tool implementation as separate editable surfaces `[AHE §3.1]`. Schema validation, the pure/effectful tag `[DAR §8.1]`, the middleware pipeline, output normalisation and truncation. | Full |
| **14** | **The Observation System** | How the runtime perceives itself: tracing, trajectory capture, result envelopes, and the distinction between *telemetry* (never durable) and *facts* (always durable) `[DAR §7.1]`. The chapter that makes Level 5 possible. | Full |
| **15** | **The State Manager** | Checkpointing, the lease plus version-CAS advance `[DAR §5.3]`, the run store, and why an advisory lock is the wrong tool. Recovery as one indexed query. | Full |
| **16** | **The Runtime Loop** | The Episode: a bounded execution window, checkpoint after every step, no scarce resource held across a model call `[DAR §5.1–5.2]`. The four exit conditions. Why step-budget = 1 is a configuration dial, not an architecture. | Full |
| **17** | **The Multi-Agent Runtime** | Sub-agents as context isolation, not as org charts. Delegation contracts, result marshalling, sandbox sharing, nesting limits, and the sub-agent component type `[AHE §3.1]`. When a sub-agent is worse than a tool. | Full |
| **18** | **The Self-Evolving Runtime (AHE) — Overview** | The closed loop in one chapter: three observability pillars, the Evolve Agent, the change manifest, Algorithm 1 `[AHE §3]`. Deliberately placed here so the reader carries the evolution frame through Levels 3 and 4. Depth arrives in Level 5. | Full |

---

### LEVEL 3 — ADVANCED RUNTIME ARCHITECTURE
*Goal: the reader can keep a six-hour, multi-tenant, irreversible-action agent alive and honest.*

| # | Chapter | The question it answers | Tier |
|---|---------|------------------------|------|
| **19** | **Durable Execution** | Why a crash must lose at most one in-flight step. Checkpoints, replay, the determinism quarantine `[DAR §6.1]`, and when to stop growing this and buy an engine `[DAR §17]`. | Full |
| **20** | **The Event Spine: Outbox, Relay, Partitioning** | The transactional outbox as the entire durability story `[DAR §7.1]`. Claim-based relay vs cursor, and why a cursor is a poison-event outage waiting to happen `[DAR §7.2]`. Partition key selection. | Full |
| **21** | **The Scheduler: Queues, Work Classes, Admission** | Convoy effects, latency-class partitioning, model semaphores, and per-tenant admission `[DAR §5.4]`. Why one global concurrency integer cannot bound three different resources. | Full |
| **22** | **The Task Graph** | From ordered steps to a DAG: dependency resolution, parallel steps, durable joins, fan-out/fan-in, and cycle prevention. Extends the linear plan of Ch 9 `[DAR §17]` + `[INF]`. | Core |
| **23** | **The World Model** | What the agent believes is true about its environment, how that belief is refreshed, and how staleness is detected. Environment probing, repository maps, service topology. Largely `[INF]` and `[BP]`; flagged as the least settled chapter in the book. | Core |
| **24** | **Planning Algorithms** | Beyond ReAct: decomposition, least-to-most, tree search, contract-first planning `[AHE App. C]`, cost-aware plan selection, and the plan-repair vs replan decision. | Core |
| **25** | **Failure, Recovery, and Rollback** | The failure table as a design artefact `[DAR §14]`. Leases, attempt caps, dead letters, sweepers. Compensation vs rollback. Git-granularity rollback of harness edits `[AHE §3.1]`. | Core |
| **26** | **Reflection, Grading, and Self-Correction** | Why model self-evaluation fails `[DAR §9.1]`. The Verdict contract: deterministic checks that a model judgment may downgrade but never upgrade `[DAR §9.2]`. Golden sets. Evaluator-isomorphic validation vs proxy validation `[AHE App. C.1]`. | Core |
| **27** | **Long-Running Agents and Multi-Step Planning** | Six-hour runs: time budgeting, step budgets, timeout coupling as a generalisation hazard `[AHE Limitations]`, background execution, progress that is not a fact, and the boredom failure mode. | Core |
| **28** | **Human Authority: Gates, Parks, Signals, Steering** | The gate as a durable park holding nothing `[DAR §8.2]`. Structural enforcement in the runner, never in the prompt `[DAR §8.1]`. Steer as goal amendment forcing a replan, and why that unifies redirection with idempotency `[DAR §8.3]`. | Full |
| **29** | **Safety, Sandboxing, and Untrusted Content** | Sandbox lifecycle and isolation `[AHE App. A]`. Fetched content is data, never instruction `[DAR §8.4]`. Blast-radius design, capability scoping, and the self-modification governance gap the source explicitly leaves open `[AHE Limitations]`. | Core |
| **30** | **Distributed Execution** | Many workers, one run: lease + CAS at scale, sharded relays, cross-process fairness, clock assumptions, and the operational meaning of "exactly one driver at any instant" `[DAR §13]`. | Full |

---

### LEVEL 4 — PRODUCTION ENGINEERING
*Goal: the reader can run this for real customers and know when it is degrading.*

| # | Chapter | The question it answers | Tier |
|---|---------|------------------------|------|
| **31** | **Scalability and Capacity Planning** | Sizing pools, semaphores, and worker counts from measured service times. Why worker concurrency may exceed pool size `[DAR §5.2]`. Load shapes unique to agents. | Core |
| **32** | **Observability: Logging, Metrics, Tracing** | The eleven signals that make the runtime operable `[DAR §15]`, extended with trajectory-level tracing `[AHE App. A]`. Identity partial-match anomalies must alert, never log. | Core |
| **33** | **Cost Engineering and Token Economics** | Reserve-then-settle budgeting `[DAR §6.4]`. Tokens/trial and success-per-million-tokens as first-class metrics `[AHE App. A]`. Why encoding behaviour in tools beats encoding it in prompts, on cost as well as quality. | Core |
| **34** | **Reliability and SLOs** | What to promise for a system that is non-deterministic by design. Liveness, error budgets, degradation modes, and the difference between an unavailable agent and a wrong one. | Core |
| **35** | **Deployment, Versioning, and Configuration** | Versioning the harness separately from the model and the code. Config snapshots, model pinning, and why a model upgrade is a harness invalidation event `[AHE §1]`. | Core |
| **36** | **GitOps and CI/CD for Agent Systems** | The harness workspace as a git repository with file-level diffs and rollback `[AHE §3.1]`. Promotion pipelines, canaries, and shadow evaluation. | Core |
| **37** | **Evaluation Infrastructure** | The prerequisite for everything in Level 5. Benchmarks and their properties, `pass@1` and its conventions `[AHE App. A]`, rollouts per task, variance, and the golden-set regression harness `[DAR §9.3]`. Build this before tuning anything. | Core |

---

### LEVEL 5 — SELF-EVOLVING SYSTEMS
*Goal: the reader can build a loop that improves the harness unattended, and knows exactly where it is blind.*

| # | Chapter | The question it answers | Tier |
|---|---------|------------------------|------|
| **38** | **The Case for Harness Evolution** | Manual harness engineering cannot keep pace with base-model releases `[AHE §1]`. Why the bottleneck is observability, not agent capability. What the ten-iteration result does and does not prove. | Core |
| **39** | **Component Observability: The Editable Substrate** | Seven orthogonal component types as files at fixed mount points `[AHE §3.1]`. Loose coupling, one failure pattern to one component class, the deliberately minimal seed, and why a pre-fitted seed destroys attribution. | Full |
| **40** | **Experience Observability: The Agent Debugger** | Ten million trace tokens to ten thousand tokens of evidence `[AHE §3.2]`. Trajectories as a navigable file environment, per-task analysis reports, the benchmark-level overview, and progressive disclosure as a token strategy. | Full |
| **41** | **Decision Observability: The Change Manifest** | Every edit as a falsifiable contract: failure evidence, root cause, targeted fix, predicted fixes, at-risk regressions, constraint level `[AHE §3.3]`. The manifest as the loop's evidence ledger. | Full |
| **42** | **The Evolve Agent** | Controllability constraints — workspace-only writes, read-only runs directory, non-deletable seed rules `[AHE §3.3]`. Choosing the right constraint level. The anti-pattern of repeatedly fixing at the wrong level. | Full |
| **43** | **Attribution, Verdicts, and Automatic Rollback** | Algorithm 1's phase ordering and why attribution runs *before* distillation `[AHE §3.3]`. Intersecting predicted sets with observed deltas. Keep / improve / rollback-and-pivot. | Core |
| **44** | **Limits: Non-Additive Components and Regression Blindness** | Effective edits do not stack: three positive single-component gains summing to +11.1 pp yield +7.3 pp together `[AHE §4.4.1]`. Fix-prediction is ~5× random; regression-prediction is ~2× `[AHE §4.4.2]`. Designing around a loop that cannot see what it is about to break. | Core |
| **45** | **Continuous Improvement and the Governance of Self-Modification** | Running the loop as production infrastructure. Human review gates on the evolution loop itself, misuse prevention, harness cleanup, and the honest framing of AHE as a controlled prototype `[AHE Limitations]`. Where `[FUT]` proposals belong. | Core |

---

### Appendices

| # | Appendix | Contents |
|---|----------|----------|
| **A** | Glossary | Every defined term, with provenance tag. Master copy; §5 of this document is its seed. |
| **B** | Naming Conventions | Complete reference. Seed in §7 of this document. |
| **C** | Diagram Conventions and Legend | Complete reference. Seed in §6 of this document. |
| **D** | Reference Schema | The runtime's tables, dialect-agnostic `[DAR App. B]` + task-graph and evolution tables `[INF]`. |
| **E** | Port Signatures | All extension interfaces consolidated as Python `Protocol` definitions, translated from `[DAR App. C]` with the original shape footnoted, + harness component contracts `[AHE §3.1]`. |
| **F** | Invariant Checklist | The nine runtime invariants `[DAR §13]` plus evolution-loop invariants `[INF]`, each with a code-level test. |
| **G** | Failure Mode Catalogue | Every failure named in the book, its detector, and its recovery. |
| **H** | Anti-Pattern Index | Every anti-pattern named in the book, with the chapter that diagnoses it. |
| **I** | Bibliography and Source Map | Which claim came from which source. |

**Totals:** 46 chapters · 6 levels · 9 appendices.

---

## 3. Dependency Graph

### 3.1 Spine (hard prerequisites, adjacent)

```
  LEVEL 0
                            +-------------------+
                            | C0  Evolution     |
                            +---------+---------+
                                      |
                  +-------------------+-------------------+
                  v                                       v
      +-----------+-----------+               +-----------+-----------+
      | C1  Model/Harness/Env |               | C2  Distributed Sys   |
      +-----------+-----------+               +-----------+-----------+
                  |                                       |
                  +-------------------+-------------------+
                                      v
                            +---------+---------+
                            | C3  Mental Models |
                            +---------+---------+
  LEVEL 1                             |
                            +---------v---------+
                            | C4  Layers/Topo   |
                            +---------+---------+
                                      |
            +-------------+-----------+-----------+
            v             v                       v
     +------+-----+ +-----+------+       +--------+-------+
     | C5 Lifecyc | | C6 3 Flows |       | C7 Five Nouns  |
     +------+-----+ +-----+------+       +--------+-------+
            |             |                       |
            +-------------+-----------+-----------+
                                      v
                            +---------+---------+
                            | C8  State Separ.  |
                            +---------+---------+
  LEVEL 2                             |
        +---------+---------+---------+---------+---------+
        v         v         v         v         v         v
    +---+---+ +---+---+ +---+---+ +---+---+ +---+---+ +---+---+
    |C9 Plan| |C10 Ctx| |C11 Mem| |C12 Rsn| |C13 Tls| |C14 Obs|
    +---+---+ +---+---+ +---+---+ +---+---+ +---+---+ +---+---+
        |         |         |         |         |         |
        +---------+---------+----+----+---------+---------+
                                 v
                        +--------+--------+
                        | C15 State Mgr   |
                        +--------+--------+
                                 v
                        +--------+--------+
                        | C16 Runtime Loop|  <-- the keystone chapter
                        +--------+--------+
                                 |
                       +---------+---------+
                       v                   v
              +--------+-------+  +--------+-------+
              | C17 Multi-Agent|  | C18 AHE Overvw |
              +--------+-------+  +--------+-------+
  LEVEL 3              |                   |
                       +---------+---------+
                                 v
        +----------+----------+--+-------+----------+----------+
        v          v          v          v          v          v
   +----+---+ +----+---+ +----+---+ +----+---+ +----+---+ +----+---+
   |C19 Dur | |C20 Evnt| |C21 Sched| |C22 Grph| |C23 Wrld| |C24 Plan|
   +----+---+ +----+---+ +----+---+ +----+---+ +----+---+ +----+---+
        |          |          |          |          |          |
        +----------+----+-----+----------+----------+----------+
                        v
        +----------+----+-----+----------+----------+
        v          v          v          v          v
   +----+---+ +----+---+ +----+---+ +----+---+ +----+---+
   |C25 Fail| |C26 Grad| |C27 Long| |C28 HITL| |C29 Safe|
   +----+---+ +----+---+ +----+---+ +----+---+ +----+---+
                        |
                        v
                  +-----+------+
                  | C30 Distr. |
                  +-----+------+
  LEVEL 4               |
        +---------+-----+---+---------+---------+---------+
        v         v         v         v         v         v
    +---+---+ +---+---+ +---+---+ +---+---+ +---+---+ +---+---+
    |C31 Scl| |C32 Obs| |C33 Cst| |C34 Rel| |C35 Dep| |C36 CI |
    +---+---+ +---+---+ +---+---+ +---+---+ +---+---+ +---+---+
        |         |         |         |         |         |
        +---------+---------+----+----+---------+---------+
                                 v
                        +--------+--------+
                        | C37 Evaluation  |  <-- gate into Level 5
                        +--------+--------+
  LEVEL 5                        |
                        +--------v--------+
                        | C38 Case for Ev |
                        +--------+--------+
                                 |
              +----------+-------+-------+----------+
              v          v               v          v
        +-----+----+ +---+------+ +------+---+
        |C39 Compnt| |C40 Experi| |C41 Decisn|
        +-----+----+ +---+------+ +------+---+
              |          |               |
              +----------+-------+-------+
                                 v
                        +--------+--------+
                        | C42 Evolve Agent|
                        +--------+--------+
                                 v
                        +--------+--------+
                        | C43 Attribution |
                        +--------+--------+
                                 v
                        +--------+--------+
                        | C44 Limits      |
                        +--------+--------+
                                 v
                        +--------+--------+
                        | C45 Governance  |
                        +--------+--------+
```

### 3.2 Long edges (non-adjacent dependencies that must be forward-referenced)

These are the edges that break a book if left implicit. Each is declared in the earlier chapter's
section 10 (*Communication*) as a forward reference, and repaid in the later chapter's section 1.

| From | To | Why |
|------|----|-----|
| C8 State Separation | C19, C30, C43 | Rollback and attribution are meaningless if run state leaked into the domain |
| C9 Planner (plan identity) | C19, C22, C28 | Replan-mints-new-plan is what makes steering and idempotency one mechanism |
| C13 Tools (pure/effectful) | C28, C29, C42 | The tag is the entire safety model and the highest-leverage evolution surface |
| C14 Observation System | C32, C40 | Trajectory capture is the raw material of the evidence corpus |
| C15 State Manager (lease + CAS) | C21, C25, C30 | Concurrency, sweeping, and fairness all reduce to lease semantics |
| C16 Runtime Loop (episode) | C27, C31, C33 | Step and wall-clock budgets set every capacity and cost number downstream |
| C18 AHE Overview | C32, C36, C37 | Observability, GitOps, and evaluation are built *for* the loop, not merely near it |
| C26 Grading | C37, C41, C43 | A verdict is what makes a manifest prediction falsifiable |
| C37 Evaluation | all of Level 5 | Without a stable score, evolution is trial-and-error |

### 3.3 Critical path

The minimum chain a reader must hold to understand the final chapter:

```
C0 -> C1 -> C3 -> C4 -> C7 -> C8 -> C13 -> C15 -> C16 -> C18
   -> C19 -> C20 -> C26 -> C28 -> C37 -> C39 -> C41 -> C43 -> C44
```

19 of 46 chapters. Everything else is depth, not gate.

---

## 4. Roadmaps

### 4.1 Learning Roadmap — four tracks

| Track | For | Chapters | Est. |
|-------|-----|----------|------|
| **T1 · Orientation** | "I need to speak this language by Friday." | F.1–F.4, C0–C4, C7, C16, C18, C44 | ~1 day |
| **T2 · Build the runtime** | "I am writing this code." | C0–C30 in order, then Appendix D, E, F | ~4 weeks |
| **T3 · Operate it** | "It exists; make it survivable." | C14, C15, C19–C21, C25, C29–C37, Appendix G | ~1.5 weeks |
| **T4 · Evolve it** | "Make it improve itself." | C13, C14, C18, C26, C36, C37, C38–C45 | ~1 week |

Tracks are cumulative in the order T1 → T2 → T3 → T4. T4 without T3 is the most common and most
expensive mistake: an evolution loop built on an unmeasured runtime optimises noise.

### 4.2 Architecture Roadmap — build order

The order matters more than the pace. Each stage is useless without the one before it and dangerous
without the one after it. Stages 0–6 follow `[DAR §16]`; Stages 7–8 extend it to AHE `[INF]`.

| Stage | Build | Chapters | Done when |
|-------|-------|----------|-----------|
| **0 · Spine** | Outbox, claim relay, one queue, command port | C20 | An event written by the edge wakes a handler in the worker |
| **1 · Run** | Runs table, lease + version CAS, episode driver, one hardcoded step | C7, C15, C16 | A run advances and survives `kill -9` mid-step |
| **2 · Activity** | Activity ledger, identity hash, lease, abort signal, one real tool | C12, C13, C19 | A model call runs off-lock and a replay never re-spends |
| **3 · Gate** | Approval port, park, resume on the decision event | C28 | A run parks for a day and resumes at the right step |
| **4 · Grader** | Deterministic checks, golden set replayed in CI | C26, C37 | You can tell whether a change made the agent better or worse |
| **5 · Control** | Signals, cancellation, progress streaming, per-tenant admission | C21, C28 | A person redirects a running agent in under two seconds |
| **6 · Scale** | Work-class split, budgets, dead letter, dashboards, soak test | C21, C25, C31–C34 | One tenant's slow work is invisible to every other tenant |
| **7 · Substrate** | Harness components as files at fixed mount points; git-backed workspace | C13, C36, C39 | A component can be swapped and rolled back without touching runtime code |
| **8 · Loop** | Trace distillation, evidence corpus, change manifest, attribution, rollback | C40–C43 | Ten unattended iterations run end to end and rejected edits revert themselves |

**On sequencing.** The instinct is to build reliability first and quality last. Stage 4 belongs
where it is `[DAR §16]`. The failure that kills an agent product is not pool exhaustion at high
concurrency — you will not have high concurrency for months. It is confident, plausible, wrong work
that nobody notices.

---

## 5. Glossary (seed — becomes Appendix A)

Terms are grouped by the layer that owns them. Every entry carries a provenance tag. Where the two
sources use different words for the same idea, the handbook picks one and records the alias.

### 5.1 Execution nouns

| Term | Definition | Tag |
|------|------------|-----|
| **Run** | One goal under execution. The durable, versioned unit; the runtime's equivalent of a process. Lifetime: minutes to weeks. | `[DAR]` |
| **Episode** | One bounded execution window over a Run. Many steps, one worker invocation, a checkpoint after each. Lifetime: seconds. | `[DAR]` |
| **Step** | One advance of a Run's state machine: either a cheap decision or the dispatch of an Activity. | `[DAR]` |
| **Activity** | One idempotent, leased, cancellable, budgeted invocation of a Tool. The only place non-determinism is permitted. | `[DAR]` |
| **Park** | A durable pause that holds no resource, resolved by an event. The general waiting primitive. | `[DAR]` |
| **Checkpoint** | The millisecond-scale write at a step boundary that persists progress, renews the lease, and reads pending signals in one transaction. | `[DAR]` |
| **Trajectory** | The full recorded message sequence of one rollout. Raw material for evidence distillation. | `[AHE]` |
| **Rollout** | One complete attempt at one task under one harness configuration. | `[AHE]` |

### 5.2 Messaging and durability

| Term | Definition | Tag |
|------|------------|-----|
| **Command** | An imperative request to change something, carrying an idempotency key. Flows down into a domain. | `[DAR]` |
| **Event** | A past-tense statement that something happened, appended in the same transaction as the change. Flows up. | `[DAR]` |
| **Outbox** | Committing a state change and its event in one transaction. The only durability primitive the architecture requires. | `[DAR]` |
| **Relay** | The worker that claims appended events and turns them back into work. | `[DAR]` |
| **Claim** | Marking an event row as owned by one relay worker, replacing a shared cursor. | `[DAR]` |
| **Partition** | The unit within which event ordering is preserved; typically a run or a tenant. | `[DAR]` |
| **Lease** | A time-bounded, durable claim of ownership over a run or activity, with a queryable expiry. | `[DAR]` |
| **Sweeper** | The continuous job that expires leases and claims and dead-letters exhausted work. | `[DAR]` |
| **Dead letter** | Terminally failed work held for inspection without blocking the run. | `[DAR]` |
| **Activity identity** | `hash(run_id, plan_id, step_id, tool_id, input_digest)`. Determines when a stored result may be reused. | `[DAR]` |
| **Partial match** | Same run and position, different plan or inputs. Must be recorded as an anomaly, never treated as a cache hit. | `[DAR]` |

### 5.3 Ports and extension points

| Term | Definition | Tag |
|------|------------|-----|
| **Port** | One of six extension interfaces: Planner, Tool, Model, Grader, Approval, Domain. If what you need to change is not one of these, the architecture is wrong for your product. | `[DAR]` |
| **Pure** | A tool that only reads, analyses, or drafts. Invocable without a gate. | `[DAR]` |
| **Effectful** | A tool whose action is observable outside the system and not reversible by it. Structurally uncallable without a resolved gate. | `[DAR]` |
| **Gate** | A required human decision before an effectful step. Implemented as a park. | `[DAR]` |
| **Signal** | Out-of-band control over a live run: `steer`, `cancel`, `pause`, `answer`. | `[DAR]` |
| **Steer** | A goal amendment delivered to a running run, forcing a replan rather than mutating the plan. | `[DAR]` |
| **Verdict** | A grading result: deterministic checks plus a model judgment that may downgrade but never upgrade. | `[DAR]` |
| **Golden set** | Recorded runs replayed in CI against deterministic checks; the regression harness. | `[DAR]` |

### 5.4 Harness and evolution

| Term | Definition | Tag |
|------|------------|-----|
| **Harness** | The collection of model-external, editable components that mediate how a model perceives and acts on its environment. | `[AHE]` |
| **Component type** | One of seven orthogonal editable classes: system prompt, tool description, tool implementation, middleware, skill, sub-agent configuration, long-term memory. | `[AHE]` |
| **Middleware** | A component that hooks into the agent loop pipeline to intercept or transform at execution level. | `[AHE]` |
| **Skill** | An on-demand reusable workflow package, loaded when relevant. | `[AHE]` |
| **Seed harness** | The deliberately minimal starting configuration. A seed pre-fitted to the target benchmark contaminates every subsequent attribution. | `[AHE]` |
| **Component observability** | A decoupled, file-level substrate that maps each failure pattern to a single component class. | `[AHE]` |
| **Experience observability** | A layered, drill-down evidence corpus distilled from raw rollouts and indexed for progressive disclosure. | `[AHE]` |
| **Decision observability** | A change manifest pairing every edit with a self-declared prediction that the next round verifies. | `[AHE]` |
| **Agent Debugger** | The component that explores trajectories as a navigable file environment and emits per-task analysis reports plus a benchmark-level overview. | `[AHE]` |
| **Evolve Agent** | The meta-agent that reads the evidence corpus, edits harness components, and records a manifest entry per edit. | `[AHE]` |
| **Change manifest** | The evidence ledger: for each edit, the failure evidence, root cause, targeted fix, predicted fixes, risk tasks, and constraint level. | `[AHE]` |
| **Constraint level** | Which component class an edit targets. Enforcement strength is a hierarchy, not a preference. | `[AHE]` |
| **Attribution** | Intersecting predicted-fix and predicted-regression sets with observed task-level deltas to produce a per-edit verdict. | `[AHE]` |
| **Controllability** | The constraint that the Evolve Agent writes only inside the harness workspace; runs, tracer, verifier, and model config are read-only. | `[AHE]` |
| **Regression blindness** | The loop's demonstrated inability to predict which tasks its own edit will break. | `[AHE]` |
| **Progressive disclosure** | Exposing evidence as navigable files so an agent reads only what it needs. | `[AHE]` |
| **Evaluator-isomorphic validation** | Self-checking against the same assertions the real verifier makes, rather than a surrogate such as a row count or a file-exists test. | `[AHE]` |

### 5.5 Terms the handbook defines (not in either source)

Introduced because the sources leave the concept unnamed. All tagged `[INF]`.

| Term | Definition |
|------|-----------|
| **Model state** | The context window, cache prefix, and reasoning budget for one model call. A third state category alongside run state and domain state; owned by the Context System, never persisted as truth. |
| **Harness version** | The identity of a complete component set, pinned alongside the model identity. A model upgrade invalidates a harness version. |
| **Evolution invariant** | A property the outer loop must preserve across iterations (e.g. the verifier is never editable). |
| **Blast radius** | The set of external effects a run could produce if every guard failed. Sizing it is a design step, not an audit step. |

---

## 6. Diagram Conventions (seed — becomes Appendix C)

### 6.1 Global rules

1. **Pure 7-bit ASCII.** No box-drawing characters, no Unicode arrows. Diagrams must survive a
   terminal, a diff, a code comment, and a plain-text email.
2. **Maximum width 78 columns.** If a diagram exceeds it, decompose it.
3. **Every diagram carries a caption** in the form `Figure C.N — <what it shows> (<diagram type>)`.
4. **Every diagram states its axis:** `LAYER VIEW`, `TIME VIEW`, or `STATE VIEW`, top-right.
5. **Numbered wires.** Where a diagram has more than four connections, label them `(1)`, `(2)`, …
   and follow with a wire-reference table. Letters `(A)`, `(B)` are reserved for side channels.
6. **One concern per diagram.** Control flow and data flow are never drawn on the same figure.

### 6.2 Box vocabulary

```
   +--------------+     Kernel component. You do not write this.
   |              |
   +--------------+

   +==============+     Port. An extension point you implement.
   |              |
   +==============+

   +~~~~~~~~~~~~~~+     External system: provider, sandbox, your domain.
   |              |
   +~~~~~~~~~~~~~~+

   [[            ]]     Durable store (a table).

   ((            ))     Queue.

   <<            >>     Event.

   {{            }}     A state, in a state diagram.

   /               \    Decision point, in a control-flow diagram.
   \               /
```

### 6.3 Arrow vocabulary

```
   ---->     synchronous call; control flows and returns
   ....>     asynchronous message or event; no return
   ====>     bulk data movement; annotate with volume ("~10M tokens")
   --||->    passes through a gate; blocked until resolved
   --X       refused, blocked, or dropped
   <-->      bidirectional / negotiated
   ~~~~>     unreliable or best-effort (telemetry, progress)
```

Vertical equivalents: `|`, `v`, `^`, with the same head semantics (`v` solid, `:` dotted line for
async, `#` for bulk).

### 6.4 The nine diagram types

| Type | Axis | Shows | Mandatory elements |
|------|------|-------|--------------------|
| **D1 High-Level Architecture** | LAYER | The subsystem in its surroundings, one level of nesting | Layer bands, the subsystem highlighted, numbered wires |
| **D2 Low-Level Architecture** | LAYER | The subsystem opened up, two levels of nesting | Internal boxes, stores, queues |
| **D3 Component Diagram** | LAYER | Named internal components and their interfaces | One box per component, interface labels on edges |
| **D4 Sequence Diagram** | TIME | One representative execution, participant lifelines | Lifelines, ordered messages, at least one failure branch |
| **D5 Runtime Loop** | TIME | The repeating cycle and its exit conditions | Loop body, every exit condition labelled `E1..En` |
| **D6 State Diagram** | STATE | Legal states and transitions | Initial state, terminal states, illegal-transition note |
| **D7 Data Flow** | LAYER | What moves and how much | `====>` arrows only, volume annotations |
| **D8 Control Flow** | TIME | Who decides what happens next | `---->` and decision diamonds only |
| **D9 Event Flow** | TIME | What is durable and replayable | `....>` arrows only, event names in `<< >>` |

### 6.5 Worked micro-example (the style all chapters follow)

```
                                                          LAYER VIEW
   +--------------+  (1)   +==============+  (2)   +~~~~~~~~~~~~~~+
   | Activity     |------->| Tool Port    |------->| Provider     |
   | Runner       |        | effect: pure |        | API          |
   +------+-------+        +==============+        +~~~~~~+~~~~~~~
          | (3)                                           :
          v                                               : (A)
   [[ activities ]]                                       :
                                                          v
                                                    ~~~~> progress

   Figure C.1 -- Activity dispatch (D1 High-Level Architecture)

   (1) claim by id, reserve budget, acquire slot
   (2) abort signal forwarded end to end
   (3) result and settled cost appended
   (A) telemetry; never written to the outbox
```

---

## 7. Naming Conventions (seed — becomes Appendix B)

### 7.1 Prose

| Thing | Convention | Example |
|-------|-----------|---------|
| Subsystem in prose | Title Case, definite article, singular | "the Activity Runner", "the Planner" |
| The five nouns | Capitalised when referring to the concept | "a Run", "one Episode" |
| A generic instance | lowercase | "the run parked", "three activities in flight" |
| Book tiers | "Level *n*" | "Level 3" |
| Architecture tiers | "the *X* layer", lowercase | "the kernel layer" |
| Build order | "Stage *n*" | "Stage 4" |
| Chapter cross-reference | `Ch 16 §7` | "checkpointing is covered in Ch 16 §7" |

### 7.2 Code and schema

**Language: Python throughout.** Ports are `typing.Protocol` definitions, not ABCs, so a domain
implementation never imports from the runtime — which is the structural test of §5 Ch 8. Data
carriers are frozen `@dataclass`. Type hints are mandatory on every signature in the book; a
signature without them is not a contract. Async functions are used wherever the source's interface
returns a promise or a stream.

Port signatures reproduced from `[DAR App. C]` are **translated**, not quoted, and each translated
block carries a footnote naming the original TypeScript shape so the reader can diff them.

| Thing | Convention | Example |
|-------|-----------|---------|
| Ports | `Protocol`, `PascalCase`, `Port` suffix | `PlannerPort`, `GraderPort`, `DomainPort` |
| Dataclasses | `PascalCase`, frozen | `Run`, `Step`, `Verdict`, `Check`, `ToolContext` |
| Fields, params, locals | `snake_case` | `activity_id`, `input_digest`, `max_tokens` |
| Modules and packages | `snake_case` | `kernel/activity_runner.py`, `ports/grader.py` |
| Enum classes | `PascalCase`; members `UPPER_SNAKE`; values lowercase strings | `class Effect(StrEnum): PURE = "pure"; EFFECTFUL = "effectful"` |
| Run and activity states | `RunState` / `ActivityState` enums, `UPPER_SNAKE` members | `CREATED`, `PLANNING`, `EXECUTING`, `AWAITING_ACTIVITY`, `PARKED`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `DEAD_LETTERED` |
| Module constants | `UPPER_SNAKE` | `MODEL_SEMAPHORE`, `EPISODE_WALL_CLOCK_MS` |
| Tables | `snake_case`, plural | `runs`, `run_steps`, `activities`, `budget_ledger` |
| Columns | `snake_case`, singular | `lease_until`, `relay_state`, `plan_id` |

Because Python and SQL now share `snake_case`, every code block is labelled `python`, `sql`, or
`yaml` in its fence. An unlabelled block is a defect.

### 7.3 Runtime message names

| Thing | Convention | Example |
|-------|-----------|---------|
| Command | `cmd.<domain>.<imperative_verb>` | `cmd.repo.apply_patch`, `cmd.billing.charge_card` |
| Event | `<domain>.<noun>.<past_tense_verb>` | `repo.patch.applied`, `run.step.completed`, `approval.decided` |
| Tool id | `tool.<namespace>.<imperative_verb>` | `tool.repo.apply_patch`, `tool.shell.run_command` |
| Signal kind | lowercase, closed set | `steer`, `cancel`, `pause`, `answer` |
| Idempotency key | `<command>:<scope>:<digest>` | `repo.apply_patch:run-9f2:8ac31d` |
| Metric | `ark_<subsystem>_<measure>_<unit>` | `ark_relay_claim_latency_ms`, `ark_activity_replay_total` |
| Trace span | `<layer>/<component>/<operation>` | `kernel/activity_runner/dispatch` |

**On the `cmd.` and `tool.` prefixes.** With Python's `snake_case`, a command and the tool that
issues it would otherwise be spelled identically (`repo.apply_patch` both times) while meaning
completely different things — one is a request into your domain, the other is a verb the model may
call. The prefixes make the distinction visible in logs, traces, manifests, and grep. Events need
no prefix: past tense already distinguishes them.

### 7.4 Harness component paths

Mirrors the decoupled substrate `[AHE §3.1]`. Fixed mount points; the Evolve Agent's action space
is exactly this tree.

```
workspace/
  agent.yaml                     component registry
  systemprompt.md                system prompt
  LongTermMEMORY.md              long-term memory
  tool_descriptions/*.tool.yaml  tool description
  tools/**/*.py                  tool implementation
  middleware/**/*.py             middleware
  skills/<name>/SKILL.md         skill
  sub_agents/<name>/agent.yaml   sub-agent configuration
```

### 7.5 Evolution artefacts

| Thing | Convention | Example |
|-------|-----------|---------|
| Change id | `chg-<n>`, scoped to one iteration | `chg-1`, `chg-7` |
| Commit message | `chg-<n>: <short description>` | `chg-2: add per-call shell timeout` |
| Iteration directory | `runs/iteration_<NNN>/` | `runs/iteration_006/` |
| Manifest | `change_manifest.json` at experiment root | — |
| Verdict values | `KEEP`, `IMPROVE`, `ROLLBACK_AND_PIVOT` | — |
| Constraint level values | `middleware`, `tool_impl`, `tool_desc`, `skill`, `prompt`, `memory`, `sub_agent` | — |

### 7.6 Prohibited words

To keep the handbook internally consistent, these are banned outside a single definitional mention:

| Banned | Use instead | Why |
|--------|-------------|-----|
| "the agent" as a system component | Run, Episode, Planner, Activity Runner | It hides which part is meant |
| "orchestrator" | run driver | Overloaded across five vendor meanings |
| "workflow" | plan, task graph | Implies a workflow engine we deliberately did not require |
| "prompt engineering" | context engineering, harness engineering | The handbook's whole thesis is that the prompt is the weakest surface |
| "memory" unqualified | short-term / long-term / episodic / procedural memory | Four different subsystems |
| "just" / "simply" | — | Signals the explanation was skipped |

---

## 8. Decision Log

| # | Decision | Resolution | Consequence in this document |
|---|----------|-----------|------------------------------|
| 1 | Scope | **46 chapters, maximum depth** | TOC unchanged. Level 3 keeps all twelve chapters; Level 4 keeps all seven. |
| 2 | Status of the Durable Runtime document | **Co-primary with AHE** | §0 updated. Overlapping claims are cited twice and differenced, never merged. |
| 3 | Code language | **Python throughout** | §7.2 rewritten. Ports become `Protocol`s; DAR's TypeScript signatures are translated with the original footnoted. `cmd.` / `tool.` prefixes added in §7.3 to keep commands and tools distinguishable once both are `snake_case`. |
| 4 | Chapter 23 (World Model) | **Open** | See below. |

### Decision 4 — the only one still open

Neither source covers a world model. As drafted, Ch 23 would be the single chapter carrying almost
no `[AHE]` or `[DAR]` weight, in a handbook whose central discipline is provenance.

Three options, with the recommendation stated plainly:

- **Keep and re-scope (recommended).** Narrow it to one answerable question — *how does the runtime
  acquire, represent, and invalidate its beliefs about the environment?* — covering repository maps,
  environment probes, service topology, and staleness detection. Real systems in the Devin and
  OpenHands class have this subsystem whether or not they name it, and Ch 24's planning algorithms
  are hollow without it. The chapter opens by declaring itself the book's most speculative, which is
  honest rather than embarrassing.
- **Fold.** Belief acquisition moves into Ch 10 (Context), belief use into Ch 24 (Planning). Costs
  the reader a coherent home for the concept; saves a chapter that will age fastest.
- **Drop.** Cleanest provenance, largest hole.

---

*End of Phase 1 deliverable. Awaiting review before Phase 2.*
