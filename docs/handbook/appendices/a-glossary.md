# Appendix A — Glossary

> **Generated file. Do not edit by hand.**
>
> Assembled from the *Terms introduced in this chapter* table at the end of every
> chapter by `tools/build_glossary.py`. To change an entry, edit the defining
> chapter's table and regenerate.

Covering 17 chapters and 179 terms.

Provenance tags: `[AHE]` the Agentic Harness Engineering paper · `[DAR]` the durable
runtime specification · `[INF]` handbook inference · `[BP]` industry practice ·
`[FUT]` speculative proposal.

**Jump to:** [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [V](#v) · [W](#w) · [Z](#z)

---

## A

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Abort handle** | The out-of-band mechanism for abandoning an in-flight call; best effort, and never assumed to have worked. | `[DAR]` | Ch 13 |
| **Abstraction at write time** | Stripping customer specifics before an entry is committed, because git history cannot be redacted afterwards. | `[INF]` | Ch 6, Ch 12 |
| **Active time** | The summed duration of a run's episodes; the only figure capacity planning may use. | `[INF]` | Ch 8 |
| **Activity** | One leased, budgeted, cancellable call out to a tool or model — the only place non-determinism is allowed. | `[DAR]` | Ch 5 |
| **Activity identity** | A fingerprint of a tool call — run, plan, step, tool, and inputs — that decides whether a stored result may be reused instead of re-run. | `[DAR]` | Ch 2 |
| **Activity runner** | The kernel component that dispatches a tool call, then releases its resources rather than waiting on them. | `[DAR]` | Ch 4 |
| **Admission control** | Refusing or delaying work at the door so that accepted work can actually be served. | `[BP]` | Ch 2 |
| **Agent-Computer Interface (ACI)** | A tool as the model experiences it — verbs, arguments, results, errors — as distinct from the mechanism that executes it. | `[BP]` | Ch 15 |
| **Amplification** | Untruncated output on the data axis re-entering the next step's context and multiplying, with no decision having changed. | `[INF]` | Ch 9, Ch 14 |
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
| **Capability scoping** | Restricting what a run may do by omitting tools from what the model is shown, rather than by instructing it. | `[INF]` | Ch 14 |
| **Checkpoint** | The few-millisecond write at a step boundary that saves progress, renews the lease, and reads pending signals in one transaction. | `[DAR]` | Ch 5 |
| **Claim** | Marking a row as owned by one consumer, instead of sharing a position marker. Immune to one bad row stalling everyone. | `[DAR]` | Ch 2, Ch 8 |
| **Classification procedure** | Four questions asked in a fixed order, first "yes" wins, that assign any field to exactly one category. | `[INF]` | Ch 6 |
| **Command** | An instruction sent down into the domain asking it to change something, carrying an idempotency key. | `[DAR]` | Ch 4 |
| **Compaction** | Reducing context to fit the budget: evict first, reference second, condense only as a last resort. | `[INF]` | Ch 11 |
| **Component type** | One of seven kinds of harness part, chosen so that each failure pattern maps to exactly one of them. | `[AHE]` | Ch 1 |
| **Condensation** | A model-generated summary replacing a span of history; the only irreversible operation in this component. | `[INF]` | Ch 11 |
| **Confidence** | How much evidence stands behind an entry, raised by corroboration and lowered by contradiction. | `[INF]` | Ch 12 |
| **Content refusal** | A deterministic provider refusal, which is terminal rather than retryable because the same request will be refused again. | `[INF]` | Ch 13 |
| **Context accounting** | Per-call, per-source record of tokens and disposition; the basis of every signal in this chapter. | `[INF]` | Ch 11 |
| **Context span** | The capture of what the model could see for one call: stable digest, semi-stable digest, and the volatile band verbatim. | `[INF]` | Ch 16 |
| **Context system** | The component that assembles, per model call, everything the model is allowed to see, under a budget and an ordering contract. | `[DAR]` | Ch 11 |
| **Contradiction** | A later observation that opposes an existing entry, lowering its confidence rather than rewriting it. | `[INF]` | Ch 12 |
| **Control flow** | The reading that answers what happens next and who decided it; measured in decisions. | `[INF]` | Ch 9 |
| **Counter-example** | An argument example showing wrong usage and its consequence, teaching the boundary rather than the shape. | `[INF]` | Ch 15 |
| **Curation** | The periodic sweep that decays, retires, and reports on size; never per run, and never deletes. | `[INF]` | Ch 12 |
| **Cursor** | A shared position marker in a stream; standard elsewhere, an outage waiting to happen here. | `[BP]` | Ch 2 |
| **Cursor (client)** | The position a client resumes a stream from, so a reconnect neither repeats nor skips. | `[INF]` | Ch 7 |
| **Custody** | Which scarce resource a piece of work is holding, and for how long. Sets the concurrency ceiling. | `[DAR]` | Ch 2 |
| **Custody gradient** | Scarcity times duration stays roughly constant: the longer a noun lives, the less scarce the thing it may hold. | `[INF]` | Ch 5 |

## D

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Data flow** | The reading that answers what moves and how much of it; measured in bytes, and where cost hides. | `[INF]` | Ch 9 |
| **Dead letter** | Terminally failed work parked for a human to look at, so it stops blocking everything behind it. | `[DAR]` | Ch 2 |
| **Decay** | Confidence falling with time since `last_confirmed`, so claims about a moved world lose authority. | `[INF]` | Ch 12 |
| **Defer** | Replacing material with a reference the model can expand later, rather than including or dropping it now. | `[INF]` | Ch 11 |
| **Deletion test** | Remove the runtime; whatever must still make sense is domain state. Necessary but not sufficient on its own. | `[DAR]` | Ch 4, Ch 6 |
| **Description drift** | A tool's behaviour changing while its description does not, producing valid answers to the wrong question. | `[INF]` | Ch 14 |
| **Domain** | Your product's own logic and tables, which must remain coherent with the runtime deleted. | `[DAR]` | Ch 4 |
| **Domain state** | What is true about the world; owned by your product and still valid with the runtime deleted. | `[DAR]` | Ch 6 |
| **Drain** | Shutdown that stops claiming, finishes the current step, checkpoints, and releases every lease. | `[BP]` | Ch 8 |
| **Durability** | The property that progress already made survives a process being killed at any moment. | `[DAR]` | Ch 2 |

## E

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Edge** | A thin stateless layer that accepts goals and streams progress, and deliberately runs no loop, no consumer, and no model call. | `[DAR]` | Ch 4 |
| **Effect tag** | Pure or effectful, held in the registry and never supplied by the model; the whole of the safety model. | `[DAR]` | Ch 10, Ch 14 |
| **Effort tier** | The reasoning-effort setting, pinned with the harness version because gains across tiers are not monotone. | `[AHE]` | Ch 13 |
| **Enforcement strength** | How hard a component is to ignore: code compels, prose asks. Fixes belong at the weakest level that can still enforce them. | `[INF]` | Ch 1 |
| **Environment** | The real world the work happens in — filesystem, shell, network, repositories — which you can constrain and observe but not control. | `[AHE]` | Ch 1 |
| **Episode** | One bounded working session over a run — a worker picks it up, advances it, and puts it down. Not a row; a function invocation. | `[DAR]` | Ch 5 |
| **Episodic memory** | The durable record of what happened in a run, read by people and tools and never fed back into a live run. | `[INF]` | Ch 12 |
| **Estimated cost** | A settled amount the provider never confirmed, tracked separately so aggregate spend shows its own uncertainty. | `[INF]` | Ch 13 |
| **Event** | A past-tense statement travelling up that something happened, written in the same transaction as the change itself. | `[DAR]` | Ch 4 |
| **Event flow** | The reading that answers what is durable and replayable; measured in committed records. | `[DAR]` | Ch 9 |
| **Eviction horizon** | How far back history is kept verbatim; the dial that determines whether run cost is linear or quadratic in steps. | `[INF]` | Ch 11 |
| **Evidence corpus** | The retained, distilled subset of trajectories that the evolution loop reads. | `[AHE]` | Ch 16 |
| **Exit condition** | One of the four reasons an episode ends: wall clock, step budget, park, or signal. | `[DAR]` | Ch 5 |
| **Expiry lag** | How overdue the most overdue lease was when the sweeper reached it; the direct measurement of recovery health. | `[INF]` | Ch 8 |

## F

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Fact** | Something durable that a later reader is entitled to rely on; the thing progress is deliberately not. | `[DAR]` | Ch 7 |
| **Fix routing** | Deciding which surface a model's mistake belongs to, so the fix lands somewhere that can prevent it. | `[INF]` | Ch 15 |
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
| **Instructive error** | An error naming what happened, why, and what to do next, so the following attempt can succeed. | `[INF]` | Ch 15 |
| **Instructiveness ratio** | Errors followed by success over errors followed by the same error; a behavioural measure of error quality. | `[INF]` | Ch 15 |
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
| **Load floor** | The confidence below which an entry stays in the file but is never loaded into context. | `[INF]` | Ch 12 |
| **Long-term memory** | Facts the system learned and kept; the only harness component a run writes to itself. | `[AHE]` | Ch 1, Ch 12 |

## M

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Memory proposal** | An observation submitted at run end for possible storage; the model proposes and never writes. | `[INF]` | Ch 12 |
| **Mental model (MM1-MM5)** | One of five borrowed pictures — process, ledger, contract, quarantine, planes — each answering a different class of design question. | `[INF]` | Ch 3 |
| **Middleware** | Code wrapping every invocation that the model cannot decline, and therefore the strongest enforcement surface in the harness. | `[AHE]` | Ch 1, Ch 14 |
| **MM1 Process model** | Treats a run like an operating-system process that workers borrow for a slice of time, rather than a job a worker owns. | `[INF]` | Ch 3 |
| **MM2 Ledger model** | Treats every effect and every cost as an appended entry that is never edited, so history is auditable. | `[INF]` | Ch 3 |
| **MM3 Contract model** | Asks where a rule is enforced, and insists the answer be a place code runs rather than a sentence in a prompt. | `[INF]` | Ch 3 |
| **MM4 Quarantine model** | Confines everything unpredictable to marked regions, so the rest of the system can be replayed safely. | `[INF]` | Ch 3 |
| **MM5 Control plane vs data plane** | Separates the path that decides what happens from the path that carries the work, because the two have different latency and failure needs. | `[INF]` | Ch 3 |
| **Model** | The rented, fixed thing that turns text into text; you select and configure it, you never change it. | `[AHE]` | Ch 1 |
| **Model policy** | Model id, effort tier, sampling parameters, and output cap, resolved from the pinned harness version rather than per call. | `[INF]` | Ch 13 |
| **Model port** | The single interface through which every model call in the system passes, metered, capped, abortable, and provider-opaque. | `[DAR]` | Ch 13 |
| **Model semaphore** | The concurrency bound that actually binds, sized against the provider's rate limit rather than local hardware. | `[DAR]` | Ch 13 |
| **Model state** | What the model can see on one call — the assembled context. Rebuilt every time, never persisted as truth. | `[INF]` | Ch 6 |

## N

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Narrow waist** | The deliberately tiny opening between runtime and domain: commands down, events up, nothing else. | `[DAR]` | Ch 4 |
| **Normalisation** | Mapping a provider's finish reasons, errors, and usage fields into ours, so its vocabulary stops at this boundary. | `[INF]` | Ch 13 |

## O

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Observation system** | The component that captures how the runtime perceived itself, distinct from the monitoring operators use. | `[DAR]` | Ch 16 |
| **One proposer, three vetoes** | The property that only the planner proposes a step, while budget, gate, and grader may only stop or downgrade one. | `[INF]` | Ch 9 |
| **Outcome-weighted retention** | Deciding at seal what to keep based on how the run ended, rather than sampling uniformly and losing the rare interesting runs. | `[INF]` | Ch 16 |

## P

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Park** | A durable pause that holds no resource at all, ended by an event rather than a timer expiring. | `[DAR]` | Ch 5 |
| **Parked time** | Wall age minus active time; measures human and external latency, never runtime performance. | `[INF]` | Ch 8 |
| **Partial success** | An outcome where the world changed incompletely, requiring a replan rather than a retry. | `[INF]` | Ch 14 |
| **Plan** | An immutable, ordered set of proposed steps with its own identity; a value rather than an object. | `[DAR]` | Ch 10 |
| **Plan chain** | The `supersedes` links from the current plan back to the first; its depth measures thrash. | `[INF]` | Ch 10 |
| **Plan id** | The identity of one plan; a replan mints a new one rather than editing the old, which is what makes steering and idempotency the same mechanism. | `[DAR]` | Ch 5 |
| **Plan identity** | The `plan_id` that makes every reference into a plan stable, because the plan it points into can never change. | `[DAR]` | Ch 10 |
| **Plan validator** | The component that rejects a malformed proposal and never repairs one, so planner defects stay visible. | `[INF]` | Ch 10 |
| **Planner** | The only component permitted to propose a step, and permitted to do nothing else. | `[DAR]` | Ch 10 |
| **Port** | One of six plug sockets where product-specific behaviour attaches: planner, tool, model, grader, approval, domain. | `[DAR]` | Ch 4 |
| **Procedural memory** | How to perform a class of task, packaged as a skill and authored deliberately rather than learned. | `[AHE]` | Ch 12 |
| **Progress** | Telemetry with no business meaning, streamed straight to a client and never written to the outbox. The opposite of a fact. | `[DAR]` | Ch 7 |
| **Progressive disclosure** | Exposing material as navigable structure so the model pulls only what it needs, instead of everything being pushed in advance. | `[AHE]` | Ch 11 |
| **Projection** | Something derived from durable facts and rebuilt on demand — assembled context, read models, progress. | `[INF]` | Ch 6, Ch 9 |
| **Provider adapter** | The one module per provider where its SDK is imported and its vocabulary exists. | `[INF]` | Ch 13 |
| **Provisional entry** | A written but uncorroborated entry, which influences nothing until a later run confirms it. | `[INF]` | Ch 12 |

## Q

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Quote, do not compute** | Preferring arguments the model can copy from a prior result over ones it must derive or count. | `[INF]` | Ch 15 |

## R

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Read model** | A view of a run assembled by the edge for a client, built from durable facts and never authoritative itself. | `[INF]` | Ch 6, Ch 7 |
| **Reasoning tokens** | Internal tokens some models emit before answering; usually billed as output, invisible in the completion, and scaling with the effort tier. | `[BP]` | Ch 13 |
| **Redaction at capture** | Removing secrets as a trajectory is written rather than when it is read, because a store with history cannot be cleaned afterwards. | `[INF]` | Ch 16 |
| **Relay** | The kernel component that picks up appended events and turns them back into work. | `[DAR]` | Ch 4 |
| **Release** | Giving a lease back at an episode boundary or at drain, without finishing the work. | `[DAR]` | Ch 8 |
| **Replan** | Producing a new plan with a new id in response to a steer, failure, downgrade, or budget change — never an edit. | `[DAR]` | Ch 10 |
| **Replay** | Re-running from a checkpoint, reusing stored results rather than re-spending on them. The correct alternative to a blind retry. | `[DAR]` | Ch 2 |
| **Replay test** | Delete every read model, progress message, and cached context; if run state cannot be reconstructed, an axis has leaked. | `[INF]` | Ch 9 |
| **Representation agreement** | The requirement that any two tools addressing the same object address it the same way. | `[INF]` | Ch 15 |
| **Reservation** | Budget held for an in-flight call; always settled or released, never abandoned. | `[DAR]` | Ch 13 |
| **Reserve-then-settle** | Committing the worst-case cost before a call and replacing it with the actual afterwards, so a cap is a limit rather than a report. | `[DAR]` | Ch 13 |
| **Result envelope** | The fixed identity wrapper on every observation, which is what makes a trajectory navigable rather than a pile of records. | `[DAR]` | Ch 16 |
| **Retirement** | Moving an entry below the floor out of use while keeping it resolvable forever. | `[INF]` | Ch 12 |
| **Retry** | Doing the work again from the start. Cheap in ordinary systems, a cost incident here. | `[BP]` | Ch 2 |
| **Retry loop** | A model repeating an identical call because the error taught it nothing; the loud ACI failure. | `[INF]` | Ch 15 |
| **Run** | One goal under execution: a durable, versioned row that lives from minutes to weeks and holds nothing else. | `[DAR]` | Ch 5 |
| **Run driver** | The kernel component that advances one run, replacing the banned word "orchestrator". | `[DAR]` | Ch 4 |
| **Run lifecycle** | The life of one goal, from arrival to a terminal state, independent of every process that touches it. | `[DAR]` | Ch 8 |
| **Run state** | What is happening right now in one run; owned by the runtime and meaningless once the run ends. | `[DAR]` | Ch 6 |
| **Runtime lifecycle** | The life of one process — boot, serve, drain, exit — which has no obligation to any run. | `[INF]` | Ch 8 |

## S

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Same-transaction rule** | A state change and the event announcing it are committed together, or the gap between them is undetectable. | `[DAR]` | Ch 9 |
| **Sandbox profile** | The isolation configuration a tool runs under, named in the registry rather than chosen per call. | `[AHE]` | Ch 14 |
| **Scope** | Whether an entry is about one repository, one tenant, or all work; what makes retrieval unnecessary. | `[INF]` | Ch 12 |
| **Seal** | Closing a trajectory at run end, when the outcome is finally known and the retention class can be assigned. | `[INF]` | Ch 16 |
| **Settlement** | Replacing a reservation with what a call actually cost, or with the reservation itself when the actual is unknowable. | `[INF]` | Ch 13 |
| **Short-term memory** | What the model can see on one call; the assembled context, rebuilt every time. | `[INF]` | Ch 12 |
| **Signal** | Out-of-band control over a live run: steer, cancel, pause, or answer. | `[DAR]` | Ch 7 |
| **Silent misread** | A well-formed result the model draws a wrong conclusion from; the expensive ACI failure, with no automatic detector. | `[INF]` | Ch 15 |
| **Skill** | A packaged, reusable procedure loaded only when it is relevant, so its tokens are not always resident. | `[AHE]` | Ch 1 |
| **Span** | One observed operation inside a run, wrapped in an envelope that carries its identity and harness version. | `[BP]` | Ch 16 |
| **Standing cost** | Tokens an ACI improvement adds to every model call forever, as against a cost paid only on failure. | `[INF]` | Ch 15 |
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
| **Token kinds** | Input, cached, reasoning, and output — priced differently, and meaningless when aggregated into one number. | `[INF]` | Ch 13 |
| **Tombstone** | The envelope that survives when a trajectory's content expires, preserving aggregate answers and an auditable deletion. | `[INF]` | Ch 16 |
| **Tool description** | The prose the model reads and the only thing it knows about a tool; an editable harness surface in its own right. | `[AHE]` | Ch 1, Ch 14 |
| **Tool execution engine** | The single door to the world: resolves, validates, authorises, invokes, normalises, truncates, and records every tool call. | `[DAR]` | Ch 14 |
| **Tool implementation** | The code that runs, editable separately from the description and at a different rate. | `[AHE]` | Ch 1, Ch 14 |
| **Tool registry** | The one source for what a tool is, feeding descriptions to the model and enforcement properties to the runtime. | `[INF]` | Ch 14 |
| **Tool tax** | The fixed cost every tool definition levies on every model call, whether or not the tool is used. | `[INF]` | Ch 11, Ch 14 |
| **Trace store** | The durable home of trajectories; the largest and highest-risk dataset in the architecture. | `[INF]` | Ch 16 |
| **Trajectory** | The full record of one run — every span, with what the model could see at each — and the raw material of the evidence corpus. | `[AHE]` | Ch 16 |
| **Truncation policy** | Per-tool rules for cutting output at the boundary, before it is stored or moved anywhere. | `[INF]` | Ch 14 |

## V

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Verb granularity** | How large each tool is, bounded below by the tool tax and above by the effect tag needing one value. | `[INF]` | Ch 15 |
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
| Ch 12 | Short-term memory, Episodic memory, Procedural memory, Long-term memory, Memory proposal, Abstraction at write time, Confidence, Load floor, Provisional entry, Contradiction, Decay, Retirement, Scope, Curation |
| Ch 13 | Model port, Provider adapter, Reserve-then-settle, Reservation, Settlement, Abort handle, Token kinds, Reasoning tokens, Effort tier, Model policy, Normalisation, Model semaphore, Content refusal, Estimated cost |
| Ch 14 | Tool execution engine, Tool registry, Tool description, Tool implementation, Description drift, Effect tag, Middleware, Truncation policy, Amplification, Partial success, Capability scoping, Sandbox profile, Tool tax |
| Ch 15 | Agent-Computer Interface (ACI), Verb granularity, Representation agreement, Instructive error, Instructiveness ratio, Retry loop, Silent misread, Quote, do not compute, Counter-example, Fix routing, Standing cost |
| Ch 16 | Observation system, Trajectory, Trace store, Span, Result envelope, Context span, Redaction at capture, Outcome-weighted retention, Seal, Tombstone, Evidence corpus |
