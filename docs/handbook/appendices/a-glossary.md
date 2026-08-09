# Appendix A — Glossary

> **Generated file. Do not edit by hand.**
>
> Assembled from the *Terms introduced in this chapter* table at the end of every
> chapter by `tools/build_glossary.py`. To change an entry, edit the defining
> chapter's table and regenerate.

Covering 12 chapters and 124 terms.

Provenance tags: `[AHE]` the Agentic Harness Engineering paper · `[DAR]` the durable
runtime specification · `[INF]` handbook inference · `[BP]` industry practice ·
`[FUT]` speculative proposal.

**Jump to:** [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [R](#r) · [S](#s) · [T](#t) · [V](#v) · [W](#w) · [Z](#z)

---

## A

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Abstraction at write time** | Removing customer specifics as a memory is written, because filtering when it is read is already too late. | `[INF]` | Ch 6 |
| **Active time** | The summed duration of a run's episodes; the only figure capacity planning may use. | `[INF]` | Ch 8 |
| **Activity** | One leased, budgeted, cancellable call out to a tool or model — the only place non-determinism is allowed. | `[DAR]` | Ch 5 |
| **Activity identity** | A fingerprint of a tool call — run, plan, step, tool, and inputs — that decides whether a stored result may be reused instead of re-run. | `[DAR]` | Ch 2 |
| **Activity runner** | The kernel component that dispatches a tool call, then releases its resources rather than waiting on them. | `[DAR]` | Ch 4 |
| **Admission control** | Refusing or delaying work at the door so that accepted work can actually be served. | `[BP]` | Ch 2 |
| **Amplification** | Untruncated output on the data axis re-entering the next step's context and multiplying, with no decision having changed. | `[INF]` | Ch 9 |
| **ARK** | The Agent Runtime Kernel designed across this book: domain-independent, knows nothing about any particular product. | `[INF]` | Ch 3 |
| **ARK/Evolve** | The outer loop that edits Atlas's harness, introduced in Ch 20 and built in Level 5. It may edit the harness and never the kernel. | `[INF]` | Ch 3 |
| **Atlas** | The product built on ARK throughout the book: a coding agent that resolves issues in real repositories, with genuinely irreversible actions. | `[INF]` | Ch 3 |

## B

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Blast radius** | Everything outside the system a run could touch if every guard failed. A quantity you size deliberately, not audit later. | `[INF]` | Ch 2 |
| **Budget share** | The fraction of the working budget a source is entitled to; required, and summing to one across all sources. | `[INF]` | Ch 11 |

## C

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Cache-stable prefix** | The leading span of a request that matches the previous call exactly and is therefore discounted by the provider. | `[BP]` | Ch 11 |
| **Capability** | What the model itself can do — reason, write code, follow an instruction. Bought from a provider, not built by you. | `[INF]` | Ch 0 |
| **Checkpoint** | The few-millisecond write at a step boundary that saves progress, renews the lease, and reads pending signals in one transaction. | `[DAR]` | Ch 5 |
| **Claim** | Marking a row as owned by one consumer, instead of sharing a position marker. Immune to one bad row stalling everyone. | `[DAR]` | Ch 2, Ch 8 |
| **Classification procedure** | Four questions asked in a fixed order, first "yes" wins, that assign any field to exactly one category. | `[INF]` | Ch 6 |
| **Command** | An instruction sent down into the domain asking it to change something, carrying an idempotency key. | `[DAR]` | Ch 4 |
| **Compaction** | Reducing context to fit the budget: evict first, reference second, condense only as a last resort. | `[INF]` | Ch 11 |
| **Component type** | One of seven kinds of harness part, chosen so that each failure pattern maps to exactly one of them. | `[AHE]` | Ch 1 |
| **Condensation** | A model-generated summary replacing a span of history; the only irreversible operation in this component. | `[INF]` | Ch 11 |
| **Context accounting** | Per-call, per-source record of tokens and disposition; the basis of every signal in this chapter. | `[INF]` | Ch 11 |
| **Context system** | The component that assembles, per model call, everything the model is allowed to see, under a budget and an ordering contract. | `[DAR]` | Ch 11 |
| **Control flow** | The reading that answers what happens next and who decided it; measured in decisions. | `[INF]` | Ch 9 |
| **Cursor** | A shared position marker in a stream; standard elsewhere, an outage waiting to happen here. | `[BP]` | Ch 2 |
| **Cursor (client)** | The position a client resumes a stream from, so a reconnect neither repeats nor skips. | `[INF]` | Ch 7 |
| **Custody** | Which scarce resource a piece of work is holding, and for how long. Sets the concurrency ceiling. | `[DAR]` | Ch 2 |
| **Custody gradient** | Scarcity times duration stays roughly constant: the longer a noun lives, the less scarce the thing it may hold. | `[INF]` | Ch 5 |

## D

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Data flow** | The reading that answers what moves and how much of it; measured in bytes, and where cost hides. | `[INF]` | Ch 9 |
| **Dead letter** | Terminally failed work parked for a human to look at, so it stops blocking everything behind it. | `[DAR]` | Ch 2 |
| **Defer** | Replacing material with a reference the model can expand later, rather than including or dropping it now. | `[INF]` | Ch 11 |
| **Deletion test** | Remove the runtime; whatever must still make sense is domain state. Necessary but not sufficient on its own. | `[DAR]` | Ch 4, Ch 6 |
| **Domain** | Your product's own logic and tables, which must remain coherent with the runtime deleted. | `[DAR]` | Ch 4 |
| **Domain state** | What is true about the world; owned by your product and still valid with the runtime deleted. | `[DAR]` | Ch 6 |
| **Drain** | Shutdown that stops claiming, finishes the current step, checkpoints, and releases every lease. | `[BP]` | Ch 8 |
| **Durability** | The property that progress already made survives a process being killed at any moment. | `[DAR]` | Ch 2 |

## E

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Edge** | A thin stateless layer that accepts goals and streams progress, and deliberately runs no loop, no consumer, and no model call. | `[DAR]` | Ch 4 |
| **Effect tag** | Whether a step is pure or effectful, read from the tool registry and never from the model. | `[DAR]` | Ch 10 |
| **Enforcement strength** | How hard a component is to ignore: code compels, prose asks. Fixes belong at the weakest level that can still enforce them. | `[INF]` | Ch 1 |
| **Environment** | The real world the work happens in — filesystem, shell, network, repositories — which you can constrain and observe but not control. | `[AHE]` | Ch 1 |
| **Episode** | One bounded working session over a run — a worker picks it up, advances it, and puts it down. Not a row; a function invocation. | `[DAR]` | Ch 5 |
| **Event** | A past-tense statement travelling up that something happened, written in the same transaction as the change itself. | `[DAR]` | Ch 4 |
| **Event flow** | The reading that answers what is durable and replayable; measured in committed records. | `[DAR]` | Ch 9 |
| **Eviction horizon** | How far back history is kept verbatim; the dial that determines whether run cost is linear or quadratic in steps. | `[INF]` | Ch 11 |
| **Exit condition** | One of the four reasons an episode ends: wall clock, step budget, park, or signal. | `[DAR]` | Ch 5 |
| **Expiry lag** | How overdue the most overdue lease was when the sweeper reached it; the direct measurement of recovery health. | `[INF]` | Ch 8 |

## F

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Fact** | Something durable that a later reader is entitled to rely on; the thing progress is deliberately not. | `[DAR]` | Ch 7 |
| **Flow annotation** | A span attribute recording which axis a trace span belongs to, so a trace can be filtered to one reading. | `[INF]` | Ch 9 |
| **Flow routing** | Deciding which of the three axes a question belongs to before trying to answer it. | `[INF]` | Ch 9 |
| **Forced move** | A component you have no choice about once you have granted a capability, because the capability removed a guarantee that must be restored some other way. | `[INF]` | Ch 0 |

## G

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Generation (G0-G5)** | One of five stages of AI system, from a plain completion call to a system that edits its own supporting components. | `[INF]` | Ch 0 |
| **Guarantee** | A promise the system could make before a capability was added, such as "this terminates" or "running it twice is harmless". | `[INF]` | Ch 0 |

## H

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Harness** | Everything around the model that you write: the machinery that turns a text-in/text-out box into a system that does work. Defined properly in Ch 1. | `[AHE]` | Ch 0, Ch 1 |
| **Harness state** | What the system has learned to do, outliving any run without being a fact about the world. | `[INF]` | Ch 6 |
| **Harness version** | The identity of a complete component set, pinned together with the model identity, because neither is meaningful alone. | `[INF]` | Ch 1 |
| **Human authority** | The requirement that certain irreversible actions wait for a person, which makes the edge availability-critical. | `[DAR]` | Ch 7 |
| **Hydrate-then-subscribe** | Load current state by query first, then attach a stream with a cursor — the contract that survives a disconnect. | `[INF]` | Ch 7 |

## I

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Idempotency** | Doing something twice leaves the world exactly as doing it once did. | `[DAR]` | Ch 2 |
| **Idempotency key** | The value that lets a receiver recognise a repeat request as the same request, rather than a second one. | `[DAR]` | Ch 2 |
| **Interruption matrix** | The table of what is lost when a process dies at each point, and how long recovery takes. | `[INF]` | Ch 8 |

## J

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Junk drawer** | Context that accreted because every addition was justified and no removal ever was. | `[INF]` | Ch 11 |

## K

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Kernel** | The small generic engine that drives work forward — relay, run driver, activity runner, sweeper — and knows nothing about any product. | `[DAR]` | Ch 4 |

## L

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Lease** | A time-limited, durable claim that one worker owns a piece of work, with an expiry others can see. | `[DAR]` | Ch 2 |
| **Lease period** | How long a claim lasts, and therefore how long an orphaned run can go unnoticed. | `[DAR]` | Ch 8 |
| **Long-term memory** | Facts kept across runs as a file the model reads, rather than a store it queries. | `[AHE]` | Ch 1 |

## M

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Mental model (MM1-MM5)** | One of five borrowed pictures — process, ledger, contract, quarantine, planes — each answering a different class of design question. | `[INF]` | Ch 3 |
| **Middleware** | Code hooked into the loop that intercepts or transforms every pass through it, whether the model wants it or not. | `[AHE]` | Ch 1 |
| **MM1 Process model** | Treats a run like an operating-system process that workers borrow for a slice of time, rather than a job a worker owns. | `[INF]` | Ch 3 |
| **MM2 Ledger model** | Treats every effect and every cost as an appended entry that is never edited, so history is auditable. | `[INF]` | Ch 3 |
| **MM3 Contract model** | Asks where a rule is enforced, and insists the answer be a place code runs rather than a sentence in a prompt. | `[INF]` | Ch 3 |
| **MM4 Quarantine model** | Confines everything unpredictable to marked regions, so the rest of the system can be replayed safely. | `[INF]` | Ch 3 |
| **MM5 Control plane vs data plane** | Separates the path that decides what happens from the path that carries the work, because the two have different latency and failure needs. | `[INF]` | Ch 3 |
| **Model** | The rented, fixed thing that turns text into text; you select and configure it, you never change it. | `[AHE]` | Ch 1 |
| **Model state** | What the model can see on one call — the assembled context. Rebuilt every time, never persisted as truth. | `[INF]` | Ch 6 |

## N

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Narrow waist** | The deliberately tiny opening between runtime and domain: commands down, events up, nothing else. | `[DAR]` | Ch 4 |

## O

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **One proposer, three vetoes** | The property that only the planner proposes a step, while budget, gate, and grader may only stop or downgrade one. | `[INF]` | Ch 9 |

## P

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Park** | A durable pause that holds no resource at all, ended by an event rather than a timer expiring. | `[DAR]` | Ch 5 |
| **Parked time** | Wall age minus active time; measures human and external latency, never runtime performance. | `[INF]` | Ch 8 |
| **Plan** | An immutable, ordered set of proposed steps with its own identity; a value rather than an object. | `[DAR]` | Ch 10 |
| **Plan chain** | The `supersedes` links from the current plan back to the first; its depth measures thrash. | `[INF]` | Ch 10 |
| **Plan id** | The identity of one plan; a replan mints a new one rather than editing the old, which is what makes steering and idempotency the same mechanism. | `[DAR]` | Ch 5 |
| **Plan identity** | The `plan_id` that makes every reference into a plan stable, because the plan it points into can never change. | `[DAR]` | Ch 10 |
| **Plan validator** | The component that rejects a malformed proposal and never repairs one, so planner defects stay visible. | `[INF]` | Ch 10 |
| **Planner** | The only component permitted to propose a step, and permitted to do nothing else. | `[DAR]` | Ch 10 |
| **Port** | One of six plug sockets where product-specific behaviour attaches: planner, tool, model, grader, approval, domain. | `[DAR]` | Ch 4 |
| **Progress** | Telemetry with no business meaning, streamed straight to a client and never written to the outbox. The opposite of a fact. | `[DAR]` | Ch 7 |
| **Progressive disclosure** | Exposing material as navigable structure so the model pulls only what it needs, instead of everything being pushed in advance. | `[AHE]` | Ch 11 |
| **Projection** | Something derived from durable facts and rebuilt on demand — assembled context, read models, progress. | `[INF]` | Ch 6, Ch 9 |

## R

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Read model** | A view of a run assembled by the edge for a client, built from durable facts and never authoritative itself. | `[INF]` | Ch 6, Ch 7 |
| **Relay** | The kernel component that picks up appended events and turns them back into work. | `[DAR]` | Ch 4 |
| **Release** | Giving a lease back at an episode boundary or at drain, without finishing the work. | `[DAR]` | Ch 8 |
| **Replan** | Producing a new plan with a new id in response to a steer, failure, downgrade, or budget change — never an edit. | `[DAR]` | Ch 10 |
| **Replay** | Re-running from a checkpoint, reusing stored results rather than re-spending on them. The correct alternative to a blind retry. | `[DAR]` | Ch 2 |
| **Replay test** | Delete every read model, progress message, and cached context; if run state cannot be reconstructed, an axis has leaked. | `[INF]` | Ch 9 |
| **Retry** | Doing the work again from the start. Cheap in ordinary systems, a cost incident here. | `[BP]` | Ch 2 |
| **Run** | One goal under execution: a durable, versioned row that lives from minutes to weeks and holds nothing else. | `[DAR]` | Ch 5 |
| **Run driver** | The kernel component that advances one run, replacing the banned word "orchestrator". | `[DAR]` | Ch 4 |
| **Run lifecycle** | The life of one goal, from arrival to a terminal state, independent of every process that touches it. | `[DAR]` | Ch 8 |
| **Run state** | What is happening right now in one run; owned by the runtime and meaningless once the run ends. | `[DAR]` | Ch 6 |
| **Runtime lifecycle** | The life of one process — boot, serve, drain, exit — which has no obligation to any run. | `[INF]` | Ch 8 |

## S

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Same-transaction rule** | A state change and the event announcing it are committed together, or the gap between them is undetectable. | `[DAR]` | Ch 9 |
| **Signal** | Out-of-band control over a live run: steer, cancel, pause, or answer. | `[DAR]` | Ch 7 |
| **Skill** | A packaged, reusable procedure loaded only when it is relevant, so its tokens are not always resident. | `[AHE]` | Ch 1 |
| **Stateless ingress** | An edge that keeps nothing in process memory, so any instance can serve any request and a deploy loses nothing. | `[DAR]` | Ch 7 |
| **Steer** | A goal amendment delivered mid-run that forces a replan instead of editing the running plan. | `[DAR]` | Ch 7 |
| **Step** | One advance of a run's state machine, taking milliseconds and recorded as a row. | `[DAR]` | Ch 5 |
| **Step budget** | The maximum number of steps one episode may take before it must yield the worker. | `[DAR]` | Ch 5 |
| **Steps per plan** | The distribution whose mode tells you whether the planner is planning or looping. | `[INF]` | Ch 10 |
| **Strategy** | Which planning method produced a plan; ReAct is one value of this field, not the architecture. | `[BP]` | Ch 10 |
| **Sub-agent configuration** | The definition of a nested agent used to isolate context, not to build an org chart. | `[AHE]` | Ch 1 |
| **Substrate** | The durable storage and queues everything else rests on; usually bought rather than built. | `[DAR]` | Ch 4 |
| **Supersede** | Marking a plan as no longer current while retaining it forever, and voiding every approval that referenced it. | `[INF]` | Ch 10 |
| **Surface** | The app, terminal, or chat window a person actually looks at. Outside the runtime entirely. | `[DAR]` | Ch 4 |
| **Survivability** | What the system around the model can withstand — a crash, a restart, a six-hour task, a bad decision. Built by you, never bought. | `[INF]` | Ch 0 |
| **Sweeper** | The continuously scheduled job that expires leases on elapsed time alone; the only component belonging to neither lifecycle. | `[DAR]` | Ch 4, Ch 8 |
| **System prompt** | Standing instructions sent with every call; the weakest of the seven, because the model may ignore prose. | `[AHE]` | Ch 1 |

## T

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Tool description** | What the model is told a tool does, as distinct from what the tool actually does. | `[AHE]` | Ch 1 |
| **Tool implementation** | The code that runs when a tool is called; enforces rather than requests. | `[AHE]` | Ch 1 |
| **Tool tax** | The fixed cost every tool definition levies on every model call, whether or not the tool is used. | `[INF]` | Ch 11 |

## V

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Volatile boundary** | The offset before which the context is asserted byte-identical to the previous call in this run. | `[INF]` | Ch 11 |
| **Volatility band** | Whether material changes per deploy, per replan, or per step; the axis assembly order sorts on. | `[INF]` | Ch 11 |

## W

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Wall age** | Time since a run was created, including every hour it spent parked. | `[INF]` | Ch 8 |
| **Working budget** | What remains of the context window after output reserve, system prompt, tool definitions, and long-term memory are paid for. | `[INF]` | Ch 11 |

## Z

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Zombie advance** | A partitioned worker attempting to continue after its lease expired, stopped by a stale version rather than by consensus. | `[DAR]` | Ch 8 |

---

## Terms by chapter

| Chapter | Terms introduced |
|---------|------------------|
| Ch 0 | Generation (G0-G5), Capability, Survivability, Forced move, Guarantee, Harness |
| Ch 1 | Model, Harness, Environment, Component type, System prompt, Tool description, Tool implementation, Middleware, Skill, Sub-agent configuration, Long-term memory, Enforcement strength, Harness version |
| Ch 2 | Durability, Idempotency, Idempotency key, Activity identity, Replay, Retry, Lease, Claim, Cursor, Dead letter, Custody, Blast radius, Admission control |
| Ch 3 | Mental model (MM1-MM5), MM1 Process model, MM2 Ledger model, MM3 Contract model, MM4 Quarantine model, MM5 Control plane vs data plane, ARK, Atlas, ARK/Evolve |
| Ch 4 | Surface, Edge, Kernel, Port, Domain, Substrate, Narrow waist, Command, Event, Deletion test, Run driver, Activity runner, Relay, Sweeper |
| Ch 5 | Run, Episode, Step, Activity, Park, Custody gradient, Checkpoint, Plan id, Step budget, Exit condition |
| Ch 6 | Domain state, Run state, Model state, Harness state, Read model, Projection, Classification procedure, Deletion test, Abstraction at write time |
| Ch 7 | Read model, Progress, Fact, Signal, Steer, Hydrate-then-subscribe, Cursor (client), Stateless ingress, Human authority |
| Ch 8 | Run lifecycle, Runtime lifecycle, Claim, Release, Drain, Sweeper, Lease period, Wall age, Active time, Parked time, Interruption matrix, Zombie advance, Expiry lag |
| Ch 9 | Control flow, Data flow, Event flow, Flow routing, One proposer, three vetoes, Same-transaction rule, Projection, Replay test, Flow annotation, Amplification |
| Ch 10 | Planner, Plan, Plan identity, Replan, Supersede, Plan validator, Effect tag, Strategy, Plan chain, Steps per plan |
| Ch 11 | Context system, Working budget, Volatility band, Volatile boundary, Cache-stable prefix, Defer, Progressive disclosure, Compaction, Condensation, Eviction horizon, Budget share, Junk drawer, Tool tax, Context accounting |
