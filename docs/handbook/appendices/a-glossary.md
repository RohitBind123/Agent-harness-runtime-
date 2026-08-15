# Appendix A — Glossary

> **Generated file. Do not edit by hand.**
>
> Assembled from the *Terms introduced in this chapter* table at the end of every
> chapter by `tools/build_glossary.py`. To change an entry, edit the defining
> chapter's table and regenerate.

Covering 50 chapters and 489 terms.

Provenance tags: `[AHE]` the Agentic Harness Engineering paper · `[DAR]` the durable
runtime specification · `[INF]` handbook inference · `[BP]` industry practice ·
`[FUT]` speculative proposal.

**Jump to:** [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) · [W](#w) · [Z](#z)

---

## A

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Abort handle** | The out-of-band mechanism for abandoning an in-flight call; best effort, and never assumed to have worked. | `[DAR]` | Ch 13 |
| **Absence alerting** | Alerting on ages, silences, and distribution shifts rather than rates, because Level 3's failures produce no errors. | `[INF]` | Ch 34 |
| **Abstraction at write time** | Stripping customer specifics before an entry is committed, because git history cannot be redacted afterwards. | `[INF]` | Ch 6, Ch 12 |
| **Access inheritance** | An automated reader acquiring standing access to a sensitive store because a read path existed, without any grant. | `[INF]` | Ch 49 |
| **Accounting objective** | The promise that every effect is reversed or named, which is satisfied by a dead letter and is therefore keepable. | `[INF]` | Ch 36 |
| **Active time** | The summed duration of a run's episodes; the only figure capacity planning may use. | `[INF]` | Ch 8 |
| **Activity** | One leased, budgeted, cancellable call out to a tool or model — the only place non-determinism is allowed. | `[DAR]` | Ch 5 |
| **Activity identity** | A fingerprint of a tool call — run, plan, step, tool, and inputs — that decides whether a stored result may be reused instead of re-run. | `[DAR]` | Ch 2 |
| **Activity ledger** | The table keyed by activity identity that records what has already been done, so it is never done twice. | `[DAR]` | Ch 21 |
| **Activity runner** | The kernel component that dispatches a tool call, then releases its resources rather than waiting on them. | `[DAR]` | Ch 4 |
| **Admission control** | Deciding at submission whether to admit, defer, or refuse, rather than accepting everything. | `[DAR]` | Ch 2, Ch 23 |
| **Admission validation** | Checking acyclicity and structural caps once at mint time, so the executor never needs a cycle detector. | `[INF]` | Ch 24 |
| **Affected-population query** | Finding what shipped under a reverted harness by querying runs on their recorded triple. | `[INF]` | Ch 39 |
| **Agent-Computer Interface (ACI)** | A tool as the model experiences it — verbs, arguments, results, errors — as distinct from the mechanism that executes it. | `[BP]` | Ch 15 |
| **Algorithm 1** | Benchmark, attribute, distil, edit, commit — with attribution deliberately before distillation. | `[AHE]` | Ch 20 |
| **Always-keep category** | A class of run whose trace retention is a correctness property rather than a best-effort behaviour. | `[INF]` | Ch 34 |
| **Amplification** | Untruncated output on the data axis re-entering the next step's context and multiplying, with no decision having changed. | `[INF]` | Ch 9, Ch 14 |
| **Argument binding at apply time** | Recording a compensation's arguments when the effect happens rather than computing them at reversal, so a reversal cannot target the wrong thing. | `[INF]` | Ch 27 |
| **Argument-hash scoping** | Binding an approval to a specific call's exact arguments, so a replan invalidates it and a retry reuses it. | `[INF]` | Ch 30 |
| **ARK** | The Agent Runtime Kernel designed across this book: domain-independent, knows nothing about any particular product. | `[INF]` | Ch 3 |
| **ARK/Evolve** | The outer loop that edits Atlas's harness, introduced in Ch 20 and built in Level 5. It may edit the harness and never the kernel. | `[INF]` | Ch 3 |
| **At-least-once delivery** | The guarantee a relay can make, with consumers responsible for making duplicates harmless. | `[BP]` | Ch 22 |
| **At-risk tasks** | The task ids an edit might break; the honest half, and the one the loop is measurably bad at. | `[AHE]` | Ch 20 |
| **Atlas** | The product built on ARK throughout the book: a coding agent that resolves issues in real repositories, with genuinely irreversible actions. | `[INF]` | Ch 3 |
| **Attempt cap** | A bound on retries keyed by activity identity so that a plan repair does not reset it. | `[DAR]` | Ch 27 |
| **Attempt count** | How many times an activity has been claimed, surfaced to the planner so repetition is a decision. | `[INF]` | Ch 21 |
| **Attempted upgrade** | A judge trying to raise a floor, clamped by the combiner and recorded as an event because its rate signals degrading independence. | `[INF]` | Ch 28 |
| **Attribution contamination** | What a pre-fitted seed does to every subsequent measurement, by moving the origin they are all taken against. | `[INF]` | Ch 43 |
| **Attribution intersection** | Comparing each entry's sealed predicted and at-risk sets against the observed per-task deltas. | `[AHE]` | Ch 47 |
| **Autonomy ladder** | The staged levels at which the loop may act without a human, with measured promotion conditions and automatic demotion. | `[INF]` | Ch 49 |

## B

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Backstop age** | A maximum age used only as a safety net behind event-driven invalidation, never as the primary expiry rule. | `[BP]` | Ch 25 |
| **Behaviour tag** | A declared claim of ownership over one behaviour, where two claimants is a build error rather than a discovery. | `[INF]` | Ch 43 |
| **Belief** | A claim plus its provenance, its event-log position, and the scope it covers — the last three being what make invalidation possible. | `[INF]` | Ch 25 |
| **Belief versus ownership** | The unsynchronisable gap between what a worker thinks it holds and what the store records, which every mechanism here accommodates rather than fixes. | `[INF]` | Ch 32 |
| **Benchmark-level overview** | The cross-task document, and the only artefact in which a pattern spanning many tasks can be seen. | `[AHE]` | Ch 44 |
| **Binding resource** | Whichever of the three bounds is currently limiting; a measurement rather than a configuration. | `[INF]` | Ch 23 |
| **Binding surface** | The name — not the number — of whichever resource is currently the constraint, and the output that stops capacity arguments. | `[INF]` | Ch 33 |
| **Blast radius** | Everything outside the system a run could touch if every guard failed. A quantity you size deliberately, not audit later. | `[INF]` | Ch 2, Ch 31 |
| **Blast-radius linter** | A mapping from changed harness paths to the benchmark slices that must run, whose output is non-negotiable. | `[INF]` | Ch 39 |
| **Budget axis** | Which of tokens, wall clock, or steps was exhausted, reported always because the three name different diagnoses. | `[INF]` | Ch 29 |
| **Budget carving** | Taking a child's cap out of the parent's remaining allowance, so tree spend stays bounded. | `[INF]` | Ch 19 |
| **Budget share** | The fraction of the working budget a source is entitled to; required, and summing to one across all sources. | `[INF]` | Ch 11 |
| **Budget sub-cause** | Which of context growth, step count, repair spend, or estimator error exhausted a token budget, since each sends the investigation to a different chapter. | `[INF]` | Ch 35 |
| **Burn rate** | The speed at which an error budget is consumed, over fast and slow windows, which distinguishes a cliff from a leak where a balance cannot. | `[BP]` | Ch 36 |

## C

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Cache-stable prefix** | The leading span of a request that matches the previous call exactly and is therefore discounted by the provider. | `[BP]` | Ch 11 |
| **Cached input** | Input served from the provider's cache at a lower rate, protected by a byte-identical stable prefix and broken silently by any change to it. | `[BP]` | Ch 35 |
| **Cancellation cascade** | Terminal states propagating from parent to children, while waiting states do not propagate at all. | `[INF]` | Ch 19 |
| **Cancellation latency** | One step plus a checkpoint; determined entirely by where signals are read. | `[INF]` | Ch 18 |
| **Capability** | What the model itself can do — reason, write code, follow an instruction. Bought from a provider, not built by you. | `[INF]` | Ch 0 |
| **Capability scoping** | Issuing the narrowest credential a step declared it needs, expiring with the step, with no path to widen mid-execution. | `[BP]` | Ch 14, Ch 31 |
| **Capacity commitment** | The total future load admitting a run promises, which is what admission should spend rather than current utilisation. | `[INF]` | Ch 33 |
| **Capacity invalidation** | Treating a model change as invalidating every derived size, because the dominant service time moved. | `[BP]` | Ch 33 |
| **Capacity surface** | An independently bounded resource with its own service time, sized from its own measurement and never from a shared multiplier. | `[INF]` | Ch 33 |
| **Capture-time redaction** | Irreversible removal of secrets before the write, correct in one place rather than everywhere forever. | `[DAR]` | Ch 37 |
| **Carried advantage** | How much of the previous cycle's fitting still has value after a model change, which is usually little. | `[INF]` | Ch 42 |
| **Change manifest** | The append-only record of each edit: evidence, root cause, fix, predicted fixes, at-risk tasks, constraint level. | `[AHE]` | Ch 20 |
| **Checkpoint** | The few-millisecond write at a step boundary that saves progress, renews the lease, and reads pending signals in one transaction. | `[DAR]` | Ch 5, Ch 17 |
| **Circular root cause** | A stated cause that restates the fix, which cannot be contradicted by any observation and leaves nothing to pivot toward. | `[INF]` | Ch 45 |
| **Claim** | Marking a row as owned by one consumer, instead of sharing a position marker. Immune to one bad row stalling everyone. | `[DAR]` | Ch 2, Ch 8 |
| **Claim race** | Two workers attempting one run, resolved by one of them affecting zero rows; a normal outcome, never an error. | `[DAR]` | Ch 17 |
| **Claim width** | The size of a predicted set, recorded at sealing, without which precision reports the width rather than the aim. | `[INF]` | Ch 45 |
| **Claim-based consumption** | Marking individual rows as taken, so one unprocessable row cannot halt the stream. | `[DAR]` | Ch 22 |
| **Classification procedure** | Four questions asked in a fixed order, first "yes" wins, that assign any field to exactly one category. | `[INF]` | Ch 6 |
| **Classification split** | Partitioning captured material into verbatim and structural so retention can be weeks for one and years for the other. | `[INF]` | Ch 37 |
| **Clean-success contrast** | The nonzero sample of passing runs that lets a pattern finder tell a property of failure from a property of the workload. | `[INF]` | Ch 44 |
| **Clock discipline** | Using one clock or one sequence for any decision, with monotonic clocks for local durations and wall clocks for humans only. | `[BP]` | Ch 32 |
| **Command** | An instruction sent down into the domain asking it to change something, carrying an idempotency key. | `[DAR]` | Ch 4 |
| **Command port** | The single downward path into a domain, carrying an idempotency key and refusable via an event. | `[DAR]` | Ch 22 |
| **Commit-keyed sharing** | Reusing an expensive structure probe across every run at the same repository commit, which is safe precisely because the key names the commit. | `[FUT]` | Ch 25 |
| **Compaction** | Reducing context to fit the budget: evict first, reference second, condense only as a last resort. | `[INF]` | Ch 11 |
| **Compensation** | A new forward action that approximately reverses an external effect, with its own identity, attempt cap, budget, and failure path. | `[BP]` | Ch 27 |
| **Component inventory** | What exists per type with size and age, built from the loader rather than the filesystem. | `[INF]` | Ch 43 |
| **Component observability** | The harness as separable files, so an edit has somewhere specific to land. | `[AHE]` | Ch 20 |
| **Component registry** | The enumerable list of what exists, where, and at which enforcement level — the first pillar, in one object. | `[INF]` | Ch 43 |
| **Component type** | One of seven kinds of harness part, chosen so that each failure pattern maps to exactly one of them. | `[AHE]` | Ch 1 |
| **Compression ratio** | Material examined over result returned; the computable check on whether a sub-agent is justified. | `[INF]` | Ch 19 |
| **Condensation** | A model-generated summary replacing a span of history; the only irreversible operation in this component. | `[INF]` | Ch 11 |
| **Confidence** | How much evidence stands behind an entry, raised by corroboration and lowered by contradiction. | `[INF]` | Ch 12 |
| **Config freeze** | Resolving configuration once at run start so a run's behaviour is explainable from its own record rather than from deploy timing. | `[INF]` | Ch 38 |
| **Constraint level** | Which component class an edit targets, ordered by enforcement strength. | `[AHE]` | Ch 20 |
| **Constraint relaxation** | The procedure for legitimately moving a containment entry, whose decisive step is making the protected property representable in the evaluation. | `[BP]` | Ch 46 |
| **Containment boundary** | The set of components deliberately outside the workspace because an outcome-based reward would remove their protection. | `[INF]` | Ch 20 |
| **Content refusal** | A deterministic provider refusal, which is terminal rather than retryable because the same request will be refused again. | `[INF]` | Ch 13 |
| **Contested constraint** | A boundary the loop repeatedly proposes across, which is evidence about the harness and never on its own a reason to relax. | `[INF]` | Ch 46 |
| **Context accounting** | Per-call, per-source record of tokens and disposition; the basis of every signal in this chapter. | `[INF]` | Ch 11 |
| **Context isolation** | The reason to delegate: examining a lot of material somewhere whose context is discarded. | `[INF]` | Ch 19 |
| **Context span** | The capture of what the model could see for one call: stable digest, semi-stable digest, and the volatile band verbatim. | `[INF]` | Ch 16 |
| **Context system** | The component that assembles, per model call, everything the model is allowed to see, under a budget and an ordering contract. | `[DAR]` | Ch 11 |
| **Context-gap misdiagnosis** | Reading a failure as a reasoning defect when the model never saw the input it needed; the drift that a behaviour-only summary guarantees. | `[INF]` | Ch 44 |
| **Contract** | A deterministic postcondition attached to a step at plan time, immutable thereafter, and never evaluated by a model. | `[AHE]` | Ch 26 |
| **Contract-first planning** | Deriving postconditions before steps, which makes under-decomposition impossible by construction. | `[AHE]` | Ch 26 |
| **Contradiction** | A direct observation disagreeing with a stored belief, recorded as an event rather than silently overwritten, and the subsystem's best diagnostic. | `[INF]` | Ch 12, Ch 25 |
| **Control flow** | The reading that answers what happens next and who decided it; measured in decisions. | `[INF]` | Ch 9 |
| **Controllability** | The constraint that the Evolve Agent writes only inside the harness workspace. | `[AHE]` | Ch 20 |
| **Controlled clock** | An injected clock with explicit advancement, without which every lease, sweeper, and TTL behaviour is untestable. | `[DAR]` | Ch 40 |
| **Convergence flattening** | The state in which new gains and rising interference cancel, expected around iteration six and routinely mistaken for a defect. | `[INF]` | Ch 48 |
| **Convoy effect** | Short work queueing behind long work in a shared FIFO, degrading latency in proportion to what is ahead. | `[BP]` | Ch 23 |
| **Corpus drift** | The benchmark's slice distribution diverging from production traffic, corrected by adding tasks rather than reweighting. | `[INF]` | Ch 41 |
| **Corpus staleness** | The property that a corpus describes one harness version, so reading it after an edit re-diagnoses what was already fixed. | `[INF]` | Ch 44 |
| **Corpus version** | An identifier for the benchmark's contents, recorded with every result, because editing a task invalidates all prior comparisons. | `[INF]` | Ch 41 |
| **Cost attribution tags** | Run, tenant, step type, model, and cached fraction — with judge, repair, and replan as distinct step types. | `[BP]` | Ch 35 |
| **Cost per successful outcome** | Total spend divided by delivered results, including the retries that failures caused — the only cost figure that is a business quantity. | `[AHE]` | Ch 35 |
| **Counter-example** | An argument example showing wrong usage and its consequence, teaching the boundary rather than the shape. | `[INF]` | Ch 15 |
| **Counterfactual run** | Running an old harness version against today's model to measure what the intervening work is still worth. | `[INF]` | Ch 42 |
| **Critical path** | The longest chain of dependent nodes, which is the floor on a run's wall-clock time regardless of worker count. | `[BP]` | Ch 24 |
| **Cross-process fairness** | Concurrency limits held in the store rather than per process, because a process-local counter multiplies every limit by the worker count. | `[INF]` | Ch 32 |
| **Cross-run store** | Memory and world-model beliefs, which carry information between runs by design and are therefore where a tenant leak produces no error. | `[INF]` | Ch 37 |
| **Curation** | The periodic sweep that decays, retires, and reports on size; never per run, and never deletes. | `[INF]` | Ch 12 |
| **Cursor** | A shared stream position; standard elsewhere, and here an outage waiting for a malformed row. | `[BP]` | Ch 2, Ch 22 |
| **Cursor (client)** | The position a client resumes a stream from, so a reconnect neither repeats nor skips. | `[INF]` | Ch 7 |
| **Custody** | Which scarce resource a piece of work is holding, and for how long. Sets the concurrency ceiling. | `[DAR]` | Ch 2 |
| **Custody gradient** | Scarcity times duration stays roughly constant: the longer a noun lives, the less scarce the thing it may hold. | `[INF]` | Ch 5 |

## D

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Data flow** | The reading that answers what moves and how much of it; measured in bytes, and where cost hides. | `[INF]` | Ch 9 |
| **Dead letter** | A durable record of an obligation the system cannot discharge, written for a person, alerted on by age rather than count. | `[BP]` | Ch 2, Ch 22, Ch 27 |
| **Decay** | Confidence falling with time since `last_confirmed`, so claims about a moved world lose authority. | `[INF]` | Ch 12 |
| **Decision observability** | Every edit paired with a prediction recorded before the result, making it checkable. | `[AHE]` | Ch 20 |
| **Declared needs** | Scopes, egress hosts, and sandbox profile written on the plan node at mint time, which is what makes capability independent of content. | `[INF]` | Ch 31 |
| **Default owner** | The component an unclassified failure lands on, which is the system prompt and therefore the weakest. | `[INF]` | Ch 43 |
| **Defer** | Replacing material with a reference the model can expand later, rather than including or dropping it now. | `[INF]` | Ch 11 |
| **Deferral** | An accepted run visibly waiting on capacity, with a position, distinct from a park. | `[INF]` | Ch 23 |
| **Degradation ladder** | Queue, shed, reduce scope — three moves that preserve the honesty promise, and a fourth that is forbidden because it has no detector. | `[BP]` | Ch 36 |
| **Delegation contract** | The complete brief plus the declared return shape, fixed at dispatch because no follow-up is possible. | `[INF]` | Ch 19 |
| **Deletion certificate** | A per-store record of what was deleted, retained, or flagged, whose enumerated count must reconcile against the registry. | `[BP]` | Ch 37 |
| **Deletion refusal** | Declining to delete a row carrying an unresolved obligation, because that row is the only record of something still outstanding. | `[INF]` | Ch 37 |
| **Deletion test** | Remove the runtime; whatever must still make sense is domain state. Necessary but not sufficient on its own. | `[DAR]` | Ch 4, Ch 6 |
| **Deprecation clock** | Days until a pinned model is withdrawn, treated as a scheduling input because it is the only metric guaranteed to reach zero. | `[BP]` | Ch 38 |
| **Description drift** | A tool's behaviour changing while its description does not, producing valid answers to the wrong question. | `[INF]` | Ch 14 |
| **Determinism quarantine** | The rule that everything outside an activity produces the same outcome given the same recorded results. | `[DAR]` | Ch 21 |
| **Deterministic tier** | Tests of the runtime with fake ports and a controlled clock, covering most of Levels 2 and 3. | `[BP]` | Ch 40 |
| **Diffuse pattern** | A defect appearing slightly in many task types and obviously in none, invisible to sampling, slicing, and aggregation alike. | `[INF]` | Ch 44 |
| **Disablement probe** | Removing a component and re-measuring, which is the only mechanical way to find overlap and costs one benchmark run. | `[BP]` | Ch 43 |
| **Disclosed degradation** | Reducing quality only with a per-run durable record and a caller notification, which converts a forbidden move into a stated reduction in scope. | `[BP]` | Ch 36 |
| **Displacement** | The loop routing a fix to a weaker, writable level because the correct one is contained — the unnamed cost of the boundary. | `[INF]` | Ch 46 |
| **Distillation ratio** | The roughly thousand-to-one reduction from raw trajectory to evidence, which is a budget to watch rather than a target to hit. | `[AHE]` | Ch 44 |
| **Divergence** | The runtime asking for something a recording does not contain, reported as a distinct outcome because most divergences are improvements. | `[INF]` | Ch 40 |
| **Domain** | Your product's own logic and tables, which must remain coherent with the runtime deleted. | `[DAR]` | Ch 4 |
| **Domain state** | What is true about the world; owned by your product and still valid with the runtime deleted. | `[DAR]` | Ch 6 |
| **Downgrade-only** | The constraint that makes a biased judge safe, by permitting movement solely in the direction the bias does not point. | `[DAR]` | Ch 28 |
| **Drain** | Shutdown that stops claiming, finishes the current step, checkpoints, and releases every lease. | `[BP]` | Ch 8 |
| **Draining** | Finishing in-flight work without starting new branches, so a budget-bounded run ends complete rather than fragmented. | `[INF]` | Ch 29 |
| **Durability** | The property that progress already made survives a process being killed at any moment. | `[DAR]` | Ch 2 |
| **Durable execution** | The property that a run resumes from its last checkpoint rather than restarting, with loss and repetition both bounded. | `[DAR]` | Ch 21 |
| **Durable join** | A row holding `required` and `arrived`, ticked in the same transaction as the completion that caused the arrival. | `[DAR]` | Ch 24 |

## E

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Edge** | A thin stateless layer that accepts goals and streams progress, and deliberately runs no loop, no consumer, and no model call. | `[DAR]` | Ch 4 |
| **Edits per iteration** | The dial trading loop throughput against attributability, since collisions rise faster than linearly with the count. | `[INF]` | Ch 47 |
| **Effect ledger** | One durable row per applied effect, carrying its tier and compensation, written in the same transaction as the node completion. | `[INF]` | Ch 27 |
| **Effect log** | What an activity actually changed, recorded alongside its result so a resumed run knows what may already have happened. | `[INF]` | Ch 21 |
| **Effect tag** | Pure or effectful, held in the registry and never supplied by the model; the whole of the safety model. | `[DAR]` | Ch 10, Ch 14 |
| **Effort tier** | The reasoning-effort setting, pinned with the harness version because gains across tiers are not monotone. | `[AHE]` | Ch 13 |
| **Egress allowlist** | A per-step set of permitted destinations defaulting to empty, and the only control over a failure that produces no symptom. | `[BP]` | Ch 31 |
| **Enforcement strength** | How hard a component is to ignore: code compels, prose asks. Fixes belong at the weakest level that can still enforce them. | `[INF]` | Ch 1 |
| **Entry seal** | The binding of an entry to a benchmark run that has not started, which makes "written before" a fact rather than a policy. | `[INF]` | Ch 45 |
| **Enumerated prediction** | A predicted set given as task ids that exist in the corpus, which is the only form attribution can intersect. | `[INF]` | Ch 45 |
| **Environment** | The real world the work happens in — filesystem, shell, network, repositories — which you can constrain and observe but not control. | `[AHE]` | Ch 1 |
| **Episode** | One bounded working session over a run — a worker picks it up, advances it, and puts it down. Not a row; a function invocation. | `[DAR]` | Ch 5 |
| **Episode limits** | Wall clock, step budget, lease, and drain grace, chosen together because they interact, and pinned with the harness version. | `[INF]` | Ch 18 |
| **Episodic memory** | The durable record of what happened in a run, read by people and tools and never fed back into a live run. | `[INF]` | Ch 12 |
| **Escaped effect** | An effect that left the system entirely, for which no reversal exists and the only control is the gate before it. | `[INF]` | Ch 27 |
| **Estimated cost** | A settled amount the provider never confirmed, tracked separately so aggregate spend shows its own uncertainty. | `[INF]` | Ch 13 |
| **Evaluation capture** | Choosing a corpus, weighting, or attribution model for what it will show, which is a governance problem rather than a statistical one. | `[BP]` | Ch 49 |
| **Evaluation gate** | The slow statistical gate before promotion, returning per-slice effect sizes with noise floors rather than a boolean. | `[INF]` | Ch 39 |
| **Evaluation work class** | Reserved-but-preemptible capacity for benchmark runs, so evaluation neither starves nor starves production. | `[BP]` | Ch 41 |
| **Evaluator-isomorphic validation** | Deriving checks from the evaluator's criteria, which works and inherits the evaluator's blind spots exactly. | `[AHE]` | Ch 28 |
| **Event** | A past-tense statement travelling up that something happened, written in the same transaction as the change itself. | `[DAR]` | Ch 4 |
| **Event flow** | The reading that answers what is durable and replayable; measured in committed records. | `[DAR]` | Ch 9 |
| **Event spine** | The outbox, relay, and command port together: how one thing that happened reliably causes the next. | `[DAR]` | Ch 22 |
| **Eviction horizon** | How far back history is kept verbatim; the dial that determines whether run cost is linear or quadratic in steps. | `[INF]` | Ch 11 |
| **Evidence corpus** | The retained, distilled subset of trajectories that the evolution loop reads. | `[AHE]` | Ch 16 |
| **Evidence ledger** | The manifest read across iterations, which is the loop's only durable reasoning and the surface a human review can actually cover. | `[AHE]` | Ch 45 |
| **Evidence novelty** | The requirement that a proposal cite at least one span no earlier entry cited, which is what makes Chapter 26's refusal enforceable. | `[INF]` | Ch 45 |
| **Evidence pointer** | A citation that resolves to an exact span, which makes a reduction lossless rather than lossy. | `[INF]` | Ch 44 |
| **Evolution readiness** | The checkable set of preconditions that must hold before an evolution loop is worth starting. | `[INF]` | Ch 42 |
| **Exact pin** | A specific model version rather than an alias, so that behaviour cannot change without an event in the change log. | `[BP]` | Ch 38 |
| **Exactly one driver** | An operational property achieved by bounding the window and protecting its contents, never a design claim that a lease establishes. | `[DAR]` | Ch 32 |
| **Exit condition** | One of the four reasons an episode ends: wall clock, step budget, park, or signal. | `[DAR]` | Ch 5, Ch 18 |
| **Experience observability** | Trajectories distilled into a navigable evidence corpus the loop can afford to read. | `[AHE]` | Ch 20 |
| **Expiry lag** | How overdue the most overdue lease was when the sweeper reached it; the direct measurement of recovery health. | `[INF]` | Ch 8 |

## F

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Fact** | Something durable that a later reader is entitled to rely on; the thing progress is deliberately not. | `[DAR]` | Ch 7 |
| **Failure classification** | Sorting a failure into transient, asserted, or structural, which selects among retry, repair, and replan. | `[INF]` | Ch 26 |
| **Failure record** | The structured account of what died, its contract, and its classification — the input whose absence causes replan storms. | `[INF]` | Ch 26 |
| **Failure table** | The set of registration-time fields — effect, tier, compensation, attempt cap, partial-failure state — without which a tool does not register. | `[DAR]` | Ch 27 |
| **Fallback atrophy** | The decay of a team's ability to re-fit a harness by hand, caused by the loop's success and unmeasured by anything. | `[INF]` | Ch 49 |
| **False pass** | A grader saying pass when the truth is fail, which corrupts every downstream record and is not comparable to its opposite. | `[BP]` | Ch 28 |
| **Fan-in** | Several branches converging on one successor, which requires a durable counter and is where the subsystem's real difficulty lives. | `[INF]` | Ch 24 |
| **Fan-out** | A node with several outgoing edges, which requires no mechanism beyond the ready set being a set. | `[BP]` | Ch 24 |
| **Fence token** | A monotonic per-run integer carried with an effect so the downstream can reject a stale caller — the only protection that works during a process pause. | `[BP]` | Ch 32 |
| **Finish reserve** | Budget held back and sized from the measured cost of the graph's terminal nodes, so a long run ends with a deliverable. | `[BP]` | Ch 29 |
| **Fit decay** | The loss of harness advantage caused by a model change rather than by any edit, arriving with no error signal. | `[INF]` | Ch 42 |
| **Fix routing** | Deciding which surface a model's mistake belongs to, so the fix lands somewhere that can prevent it. | `[INF]` | Ch 15 |
| **Fixture triple** | The code, harness, and model version a recording was captured under, which is what makes fixture staleness detectable. | `[INF]` | Ch 40 |
| **Floor** | The verdict produced by deterministic checks alone, which nothing may raise. | `[DAR]` | Ch 28 |
| **Flow annotation** | One enum per span recording which of Chapter 9's three axes it belongs to, turning an argument into a filter. | `[INF]` | Ch 9, Ch 34 |
| **Flow routing** | Deciding which of the three axes a question belongs to before trying to answer it. | `[INF]` | Ch 9 |
| **Forced move** | A component you have no choice about once you have granted a capability, because the capability removed a guarantee that must be restored some other way. | `[INF]` | Ch 0 |

## G

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Gate** | A pre-execution check at the tool boundary that returns without acting when no decision exists for this exact call. | `[DAR]` | Ch 30 |
| **Gate expiry** | The rule that an unanswered gate fails the run, because treating silence as consent defeats the control with an inattentive afternoon. | `[BP]` | Ch 30 |
| **Gate policy** | A pure function over tool, tier, arguments, and environment that defaults to requiring approval for anything unrecognised. | `[INF]` | Ch 30 |
| **Gate refusal rate** | The measure that makes a useless gate visible, since an approval that is always granted is a gate that should be removed. | `[BP]` | Ch 49 |
| **Gated-effect coverage** | The fraction of applied effects at gated tiers that have a matching decision row, which must be exactly one. | `[INF]` | Ch 30 |
| **Generation (G0-G5)** | One of five stages of AI system, from a plain completion call to a system that edits its own supporting components. | `[INF]` | Ch 0 |
| **Golden set** | A fixed corpus with known verdicts that grades the grader, never edited to make a run pass. | `[BP]` | Ch 28 |
| **Guarantee** | A promise the system could make before a capability was added, such as "this terminates" or "running it twice is harmless". | `[INF]` | Ch 0 |

## H

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Harness** | Everything around the model that you write: the machinery that turns a text-in/text-out box into a system that does work. Defined properly in Ch 1. | `[AHE]` | Ch 0, Ch 1 |
| **Harness cleanup** | Scheduled removal of undetermined edits, rotted memory, and accreted instructions — the only mechanism that shrinks a harness. | `[AHE]` | Ch 49 |
| **Harness state** | What the system has learned to do, outliving any run without being a fact about the world. | `[INF]` | Ch 6 |
| **Harness version** | A content hash of the workspace used to attach measurements to, deliberately not a semantic version because there is no interface to be compatible with. | `[AHE]` | Ch 1, Ch 38 |
| **Harness workspace** | A git repository with fixed mount points holding everything the model is shown or given, so a diff is meaningful and a revert is exact. | `[AHE]` | Ch 39 |
| **Honesty auditor** | Offline re-grading of sampled completed runs against the golden set, and the only timely signal for the promise that matters most. | `[INF]` | Ch 36 |
| **Honesty objective** | The promise that what a run reports about itself is true, measured by auditing sampled verdicts, and the strictest of the three. | `[INF]` | Ch 36 |
| **Human authority** | The requirement that certain irreversible actions wait for a person, which makes the edge availability-critical. | `[DAR]` | Ch 7 |
| **Hydrate-then-subscribe** | Load current state by query first, then attach a stream with a cursor — the contract that survives a disconnect. | `[INF]` | Ch 7 |

## I

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Idempotency** | Doing something twice leaves the world exactly as doing it once did. | `[DAR]` | Ch 2 |
| **Idempotency key** | The value that lets a receiver recognise a repeat request as the same request, rather than a second one. | `[DAR]` | Ch 2 |
| **Identity partial match** | Any internal inconsistency in the activity-identity function, which is a page rather than a log because four subsystems silently depend on it. | `[DAR]` | Ch 34 |
| **In-flight cap** | The per-tenant limit on concurrently running work, enforced exactly in the admission transaction. | `[DAR]` | Ch 23 |
| **Indirect boundary erosion** | Achieving a contained end by editing something permitted, leaving the boundary intact and irrelevant, detected by nothing. | `[INF]` | Ch 48 |
| **Infrastructure observability** | Aggregate signals answering whether the machinery is working, which is the question that was not failing in the cold open. | `[BP]` | Ch 34 |
| **Inside-floor keep** | Retaining an edit on a movement smaller than the noise floor — the one of the four states that is a defect in the loop. | `[INF]` | Ch 47 |
| **Instruction accretion** | The monotonic growth of instruction files, each addition justified and none removed, paid for on every call forever. | `[INF]` | Ch 39 |
| **Instruction share** | Instruction tokens as a fraction of input, which rises monotonically over a system's life because nobody owns reducing it. | `[INF]` | Ch 35 |
| **Instructive error** | An error naming what happened, why, and what to do next, so the following attempt can succeed. | `[INF]` | Ch 15 |
| **Instructiveness ratio** | Errors followed by success over errors followed by the same error; a behavioural measure of error quality. | `[INF]` | Ch 15 |
| **Interference** | Components whose effects do not add because each changes what the model perceives, and therefore the others' mechanism. | `[INF]` | Ch 48 |
| **Interruption matrix** | The table of what is lost when a process dies at each point, and how long recovery takes. | `[INF]` | Ch 8 |
| **Invalidation event** | A model change, which marks every measurement and tuned number made against the old model as no longer measured. | `[INF]` | Ch 38 |
| **Invalidation register** | A record of every tuned number with the model it was measured against, which blocks promotion while any entry is stale. | `[INF]` | Ch 38 |

## J

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Join policy** | Whether a join fires on all branches, k of n, or the first, where only the last requires every feeding branch to be pure. | `[INF]` | Ch 24 |
| **Judge independence** | Withholding the trajectory, reasoning, and self-review from the grader, enforced by the signature rather than by instruction. | `[INF]` | Ch 28 |
| **Junk drawer** | Context that accreted because every addition was justified and no removal ever was. | `[INF]` | Ch 11 |

## K

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Kernel** | The small generic engine that drives work forward — relay, run driver, activity runner, sweeper — and knows nothing about any product. | `[DAR]` | Ch 4 |

## L

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Label allowlist** | A fixed set of permitted metric label names enforced at the call site, because a denylist cannot anticipate the next unbounded value. | `[BP]` | Ch 34 |
| **Label inheritance** | Derived content taking the minimum label of its inputs, which closes the fetch-then-summarise laundering path. | `[INF]` | Ch 31 |
| **Lease** | A claim with a store-evaluated expiry, which controls acquisition and never evicts an existing holder. | `[DAR]` | Ch 2, Ch 32 |
| **Lease column** | Ownership stored as data — holder and expiry — so it is queryable, indexable, and outlives its holder. | `[DAR]` | Ch 17 |
| **Lease period** | How long a claim lasts, and therefore how long an orphaned run can go unnoticed. | `[DAR]` | Ch 8 |
| **Least-to-most** | Decomposing into sub-goals before steps, which earns its extra model call when a flat plan's step costs are wildly uneven. | `[BP]` | Ch 26 |
| **Level escalation** | Moving a repeated failure to a stronger enforcement level rather than rewording at the same one, refused entirely on a third attempt. | `[INF]` | Ch 46 |
| **Little's Law sizing** | Required concurrency equals arrival rate times service time, applied once per surface with no shared multiplier. | `[BP]` | Ch 33 |
| **Liveness objective** | The promise that a run reaches a definite outcome within its class SLA, which covers stalls, stuck gates, and unfired joins in one ratio. | `[INF]` | Ch 36 |
| **Load floor** | The confidence below which an entry stays in the file but is never loaded into context. | `[INF]` | Ch 12 |
| **Load generator** | A run seen correctly: not a unit of work served and released, but a process emitting load at its own rate for its whole lifetime. | `[INF]` | Ch 33 |
| **Long-term memory** | Facts the system learned and kept; the only harness component a run writes to itself. | `[AHE]` | Ch 1, Ch 12 |

## M

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Marshalling** | Validating a child's terminal output against the declared schema; rejected rather than coerced. | `[INF]` | Ch 19 |
| **Mechanism check** | Confirming that the targeted pattern shrank in the next corpus, which separates a real gain from a credited one. | `[INF]` | Ch 47 |
| **Mechanism shift** | One component changing the conditions under which another's effect exists, which is why a combination can be worse than a member. | `[INF]` | Ch 48 |
| **Memory proposal** | An observation submitted at run end for possible storage; the model proposes and never writes. | `[INF]` | Ch 12 |
| **Memory scope** | The tenant boundary on cross-run memory, whose widening would genuinely improve quality and would be a contractual breach no benchmark measures. | `[INF]` | Ch 37 |
| **Mental model (MM1-MM5)** | One of five borrowed pictures — process, ledger, contract, quarantine, planes — each answering a different class of design question. | `[INF]` | Ch 3 |
| **Merge-is-not-deploy** | Separating the merge of a harness change from the promotion of it, because the gate that matters takes hours. | `[BP]` | Ch 39 |
| **Middleware** | Code wrapping every invocation that the model cannot decline, and therefore the strongest enforcement surface in the harness. | `[AHE]` | Ch 1, Ch 14 |
| **Minimal seed** | The deliberately unfitted starting harness, which is the baseline that makes advantage measurable at all. | `[AHE]` | Ch 42 |
| **Minimum detectable effect** | The smallest change a benchmark can distinguish from its own variability, and the hard limit on what any process built on it can decide. | `[BP]` | Ch 41 |
| **MM1 Process model** | Treats a run like an operating-system process that workers borrow for a slice of time, rather than a job a worker owns. | `[INF]` | Ch 3 |
| **MM2 Ledger model** | Treats every effect and every cost as an appended entry that is never edited, so history is auditable. | `[INF]` | Ch 3 |
| **MM3 Contract model** | Asks where a rule is enforced, and insists the answer be a place code runs rather than a sentence in a prompt. | `[INF]` | Ch 3 |
| **MM4 Quarantine model** | Confines everything unpredictable to marked regions, so the rest of the system can be replayed safely. | `[INF]` | Ch 3 |
| **MM5 Control plane vs data plane** | Separates the path that decides what happens from the path that carries the work, because the two have different latency and failure needs. | `[INF]` | Ch 3 |
| **Model** | The rented, fixed thing that turns text into text; you select and configure it, you never change it. | `[AHE]` | Ch 1 |
| **Model policy** | Model id, effort tier, sampling parameters, and output cap, resolved from the pinned harness version rather than per call. | `[INF]` | Ch 13 |
| **Model port** | The single interface through which every model call in the system passes, metered, capped, abortable, and provider-opaque. | `[DAR]` | Ch 13 |
| **Model semaphore** | The concurrency bound that actually binds, sized against the provider's rate limit rather than local hardware. | `[DAR]` | Ch 13, Ch 23 |
| **Model state** | What the model can see on one call — the assembled context. Rebuilt every time, never persisted as truth. | `[INF]` | Ch 6 |
| **Model-conditional content** | Harness material that exists because of a specific model's behaviour, indistinguishable from ordinary design unless marked at the time. | `[INF]` | Ch 38 |
| **Mount point** | The fixed path a component type lives at, so an edit has a stable address to be recorded and reverted at. | `[AHE]` | Ch 43 |

## N

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Narrow waist** | The deliberately tiny opening between runtime and domain: commands down, events up, nothing else. | `[DAR]` | Ch 4 |
| **Nesting depth cap** | The limit on delegation chains, enforced by refusal rather than by silent clamping. | `[INF]` | Ch 19 |
| **Noise floor** | The spread of scores from running an unchanged harness repeatedly, which sets the minimum effect any decision can be based on. | `[INF]` | Ch 41 |
| **Non-additivity** | The measured finding that individually effective edits deliver less together than the sum of their separate gains. | `[AHE]` | Ch 20 |
| **Non-deletable rule** | A file the loop may not remove, of which the seed is the odd case: it protects a measurement rather than a safety property. | `[AHE]` | Ch 46 |
| **Normalisation** | Mapping a provider's finish reasons, errors, and usage fields into ours, so its vocabulary stops at this boundary. | `[INF]` | Ch 13 |
| **Novel durable state** | The definition of progress: a step makes progress when it leaves the system somewhere it has not been. | `[INF]` | Ch 29 |
| **Novelty window** | The bounded count of recent effectful steps over which novelty is assessed, exempting reads by construction. | `[INF]` | Ch 29 |
| **Null at-risk claim** | An empty at-risk list, which asserts that an edit breaks nothing and must be scored like any other claim. | `[INF]` | Ch 45 |

## O

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Observation system** | The component that captures how the runtime perceived itself, distinct from the monitoring operators use. | `[DAR]` | Ch 16 |
| **Oldest unprocessed age** | The age of the longest-waiting outbox row; the only detector for a silently stalled spine. | `[INF]` | Ch 22 |
| **One proposer, four vetoes** | The property that the planner alone proposes while budget, gate, and grader may only stop or downgrade, and only a human may also start. | `[INF]` | Ch 30 |
| **One proposer, three vetoes** | The property that only the planner proposes a step, while budget, gate, and grader may only stop or downgrade one. | `[INF]` | Ch 9 |
| **One-way derivation** | Building a golden case, statistic, or tuned model from customer data, after which no deletion operation reaches the derivative. | `[FUT]` | Ch 37 |
| **Orphaned component** | A file at a mount point that nothing loads: correct, reviewed, committed, and inert, with no error at any point. | `[INF]` | Ch 43 |
| **Orphaned reserve** | A hold left by a worker that died before settling, which becomes permanent phantom spend without a TTL and a sweeper. | `[BP]` | Ch 35 |
| **Orthogonality** | One behaviour, one owning component, required because a difference measurement needs exactly one thing to have changed. | `[AHE]` | Ch 43 |
| **Outcome-weighted retention** | Deciding at seal what to keep based on how the run ended, rather than sampling uniformly and losing the rare interesting runs. | `[INF]` | Ch 16 |
| **Outer loop** | The iteration that edits the harness, running in hours, as distinct from the runtime loop that advances a run in seconds. | `[AHE]` | Ch 20 |
| **Outstanding obligation** | An applied effect neither reversed nor resolved, whose oldest age is the single number this subsystem must alert on. | `[INF]` | Ch 27 |
| **Overlap** | Two components able to produce the same behaviour, in one of three shapes: compensation, shadowing, or duplication. | `[INF]` | Ch 43 |
| **Override** | Proceeding past a failed check as a named, expiring, append-only decision that leaves the verdict unchanged. | `[BP]` | Ch 30 |

## P

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Pace-keeping** | The honest framing of the loop's purpose: holding fit against model churn rather than optimising without bound. | `[INF]` | Ch 42 |
| **Paired evaluation** | Comparing two harnesses on identical tasks and inputs so task difficulty cancels, which narrows the floor at no extra cost. | `[BP]` | Ch 41 |
| **Park** | A run suspended as a durable row holding no worker, lease, slot, connection, or timer, so that gating costs no capacity. | `[DAR]` | Ch 5, Ch 30 |
| **Parked time** | Wall age minus active time; measures human and external latency, never runtime performance. | `[INF]` | Ch 8 |
| **Parking** | Suspending a run at a gate while it holds no worker, lease, or semaphore slot, so that parking is economically free. | `[DAR]` | Ch 29 |
| **Partial expiry index** | An index on `lease_until` restricted to non-terminal runs, making recovery cost scale with failures rather than runs. | `[INF]` | Ch 17 |
| **Partial match** | An identity agreeing on run and position but differing on plan or inputs; an anomaly, never a cache hit. | `[DAR]` | Ch 21 |
| **Partial success** | An outcome where the world changed incompletely, requiring a replan rather than a retry. | `[INF]` | Ch 14 |
| **Partition key** | The scope within which event ordering is preserved, and deliberately no wider. | `[DAR]` | Ch 22 |
| **Per-slice effect** | A measured change reported per task type, because a regression concentrated in one slice vanishes in an aggregate. | `[INF]` | Ch 39 |
| **Per-slice floor** | A noise floor computed per task type, because small slices have wide floors and that is where results are over-read. | `[INF]` | Ch 41 |
| **Per-slice gate** | A promotion rule reading cumulative per-slice deltas against the seed, which is the one cheap fix in this chapter. | `[BP]` | Ch 48 |
| **Per-task analysis** | One structured report per failing task, with fixed fields chosen so that each answers a routing question. | `[AHE]` | Ch 44 |
| **Plan** | An immutable, ordered set of proposed steps with its own identity; a value rather than an object. | `[DAR]` | Ch 10 |
| **Plan chain** | The `supersedes` links from the current plan back to the first; its depth measures thrash. | `[INF]` | Ch 10 |
| **Plan id** | The identity of one plan; a replan mints a new one rather than editing the old, which is what makes steering and idempotency the same mechanism. | `[DAR]` | Ch 5 |
| **Plan identity** | The `plan_id` that makes every reference into a plan stable, because the plan it points into can never change. | `[DAR]` | Ch 10 |
| **Plan lineage** | The chain of plans derived from one unchanged goal, which is what makes the repair-versus-replan guard answerable. | `[INF]` | Ch 26 |
| **Plan validator** | The component that rejects a malformed proposal and never repairs one, so planner defects stay visible. | `[INF]` | Ch 10 |
| **Planner** | The only component permitted to propose a step, and permitted to do nothing else. | `[DAR]` | Ch 10 |
| **Plans per goal** | The count of plans a lineage consumed, the cheapest available measure of decomposition quality. | `[INF]` | Ch 26 |
| **Point of no return** | The fraction of wall clock past which no new branches start and the run drains what is in flight. | `[BP]` | Ch 29 |
| **Poison event** | A row whose handler cannot succeed; dead-lettered so its blast radius is one row. | `[INF]` | Ch 22 |
| **Port** | One of six plug sockets where product-specific behaviour attaches: planner, tool, model, grader, approval, domain. | `[DAR]` | Ch 4 |
| **Port boundary** | The model port as the test seam, below which the system is ordinary deterministic software. | `[INF]` | Ch 40 |
| **Predicted fixes** | The task ids an edit claims it will repair; the half of the claim that is easy to write. | `[AHE]` | Ch 20 |
| **Predicted-set collision** | Two edits in one iteration naming a shared task, which makes both verdicts guesses and is detectable at sealing. | `[INF]` | Ch 47 |
| **Presentational rank** | An ordering field kept for human reading and never consulted by the resolver, which is what lets display order stay stable while execution order varies. | `[INF]` | Ch 24 |
| **Probe** | A named, costed, read-only query that derives a belief and can always be re-run to refresh it. | `[INF]` | Ch 25 |
| **Procedural memory** | How to perform a class of task, packaged as a skill and authored deliberately rather than learned. | `[AHE]` | Ch 12 |
| **Progress** | Telemetry with no business meaning, streamed straight to a client and never written to the outbox. The opposite of a fact. | `[DAR]` | Ch 7 |
| **Progressive disclosure** | Exposing material as navigable structure so the model pulls only what it needs, instead of everything being pushed in advance. | `[AHE]` | Ch 11 |
| **Projection** | Something derived from durable facts and rebuilt on demand — assembled context, read models, progress. | `[INF]` | Ch 6, Ch 9 |
| **Proposal storm** | Repeated proposals re-theorising unchanged evidence; the outer-loop analogue of a replan storm, at roughly a billion tokens each. | `[INF]` | Ch 45 |
| **Provenance label** | A trust level attached to content at fetch time, before any model sees it, and never recoverable later. | `[DAR]` | Ch 31 |
| **Provenance lattice** | Trusted, semi-trusted, untrusted, with content moving down freely and never up, because any promoting operation would be reachable by the content. | `[INF]` | Ch 31 |
| **Provider adapter** | The one module per provider where its SDK is imported and its vocabulary exists. | `[INF]` | Ch 13 |
| **Provisional entry** | A written but uncorroborated entry, which influences nothing until a later run confirms it. | `[INF]` | Ch 12 |
| **Published statistic** | A tracked quality trend with no target, no budget, and no route to the pager, kept structurally distinct from an objective. | `[INF]` | Ch 36 |

## Q

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Quality regression** | A shift in the verdict distribution, routed to evaluation rather than to the pager unless the honesty objective also breaks. | `[INF]` | Ch 36 |
| **Queue time** | The wait before a hold begins, which belongs in saturation alerts and never in a sizing calculation. | `[BP]` | Ch 33 |
| **Quote, do not compute** | Preferring arguments the model can copy from a prior result over ones it must derive or count. | `[INF]` | Ch 15 |

## R

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Re-fit** | The campaign of harness edits that follows a model change, most of which re-earns ground rather than gaining new. | `[INF]` | Ch 42 |
| **Re-run** | Executing the same goal again from the start, with new identities and every effect repeated. | `[INF]` | Ch 21 |
| **Read model** | A view of a run assembled by the edge for a client, built from durable facts and never authoritative itself. | `[INF]` | Ch 6, Ch 7 |
| **Read-only runs directory** | The rule that the loop cannot edit the evidence it learns from, because a process that can annotate its own evidence has none. | `[AHE]` | Ch 46 |
| **Reading bottleneck** | The measured finding that most of a re-fit is spent locating the failure pattern rather than choosing the fix. | `[INF]` | Ch 42 |
| **Ready set** | The nodes whose predecessors are all terminal and whose joins are satisfied, computed by query and never stored. | `[INF]` | Ch 24 |
| **Reasoning tokens** | Internal tokens some models emit before answering; usually billed as output, invisible in the completion, and scaling with the effort tier. | `[BP]` | Ch 13 |
| **Redaction at capture** | Removing secrets as a trajectory is written rather than when it is read, because a store with history cannot be cleaned afterwards. | `[INF]` | Ch 16 |
| **Redundant closure** | Several components pushing toward the same behaviour, so stacking them buys it once and pays for it repeatedly. | `[AHE]` | Ch 48 |
| **Reflection** | The run reconsidering its own work mid-flight, useful for generation and carrying no authority over any verdict. | `[INF]` | Ch 28 |
| **Regression harness** | The fast deterministic gate on every commit, deliberately unable to see statistical regressions. | `[DAR]` | Ch 39 |
| **Relaxation gate** | The named human decision required to move a containment entry, made outside the loop's reporting line and never during an iteration. | `[INF]` | Ch 49 |
| **Relay** | The worker that claims outbox rows and turns them into work, enqueued, commanded, or published. | `[DAR]` | Ch 4, Ch 22 |
| **Release** | Giving a lease back at an episode boundary or at drain, without finishing the work. | `[DAR]` | Ch 8 |
| **Release cadence** | The provider's schedule, which sets the harness workload and which you do not control. | `[AHE]` | Ch 42 |
| **Removal experiment** | Taking an instruction out and evaluating, which is the only mechanism that ever removes one and is a natural target for automation. | `[BP]` | Ch 39 |
| **Rendered arguments** | A deterministic, human-readable statement of what will happen, never a model-generated summary of the model's own request. | `[BP]` | Ch 30 |
| **Renewal disarming** | Switching the effect path into a refusing state the instant a renewal fails, rather than logging and retrying. | `[BP]` | Ch 32 |
| **Repair** | Re-deriving a plan's unexecuted tail while carrying the executed prefix by identity hash, at roughly a tenth the cost of replanning. | `[INF]` | Ch 26 |
| **Replan** | Minting a new lineage because the decomposition itself was wrong, permitted only when the failure record carries information the last one did not. | `[DAR]` | Ch 10, Ch 26 |
| **Replan storm** | Repeated identical replans from unchanged inputs, structurally impossible once a replan without new information is refused. | `[INF]` | Ch 26 |
| **Replay** | Re-running from a checkpoint, reusing stored results rather than re-spending on them. The correct alternative to a blind retry. | `[DAR]` | Ch 2, Ch 21 |
| **Replay test** | Delete every read model, progress message, and cached context; if run state cannot be reconstructed, an axis has leaked. | `[INF]` | Ch 9 |
| **Replay tier** | Recorded real trajectories served to the runtime, giving real model behaviour with reproducible execution. | `[INF]` | Ch 40 |
| **Representation agreement** | The requirement that any two tools addressing the same object address it the same way. | `[INF]` | Ch 15 |
| **Reservation** | Budget held for an in-flight call; always settled or released, never abandoned. | `[DAR]` | Ch 13 |
| **Reserve gap** | The systematic excess of reserves over actuals, which is deliberate, costs concurrency, and is a calibration exercise. | `[INF]` | Ch 35 |
| **Reserve-then-settle** | Committing the worst-case cost before a call and replacing it with the actual afterwards, so a cap is a limit rather than a report. | `[DAR]` | Ch 13, Ch 35 |
| **Reserved capacity** | Workers a class always gets, idling rather than yielding, which is what makes it a reservation. | `[INF]` | Ch 23 |
| **Resolved config hash** | A hash over configuration values after defaults and overrides, which says behaviour did not change where a file hash says only that a file did not. | `[BP]` | Ch 38 |
| **Result envelope** | The fixed identity wrapper on every observation, which is what makes a trajectory navigable rather than a pile of records. | `[DAR]` | Ch 16 |
| **Resume** | Continuing an interrupted run, reusing recorded results by identity and repeating nothing. | `[INF]` | Ch 21 |
| **Retention as a Level 5 decision** | Choosing the trace retention window against evaluation and evolution needs rather than against storage cost. | `[INF]` | Ch 34 |
| **Retirement** | Moving an entry below the floor out of use while keeping it resolvable forever. | `[INF]` | Ch 12 |
| **Retry** | Doing the work again from the start. Cheap in ordinary systems, a cost incident here. | `[BP]` | Ch 2 |
| **Retry loop** | A model repeating an identical call because the error taught it nothing; the loud ACI failure. | `[INF]` | Ch 15 |
| **Retry multiplier** | Attempts per delivered outcome, the omitted term that makes any quality-for-cost trade look favourable. | `[INF]` | Ch 35 |
| **Retry prohibition** | A lint-enforced ban on retry decorators in the deterministic tiers, achievable only because those tiers really are deterministic. | `[BP]` | Ch 40 |
| **Return contract** | The bounded, structured schema a sub-agent's result must satisfy, designed before the sub-agent. | `[INF]` | Ch 19 |
| **Reversibility tier** | Whether an effect is owned and restorable, external and compensable, or escaped with no operation available. | `[INF]` | Ch 27 |
| **Review scan** | A fixed agenda of computed numbers, in fixed order, because a review is its agenda and attention drifts toward the interesting. | `[BP]` | Ch 49 |
| **Rollback** | Restoring a kept prior version of state the runtime owns, which is local, cheap, and cannot half-fail. | `[AHE]` | Ch 27 |
| **Rolling window** | A budget window that does not reset on a calendar boundary, removing both end-of-month gaming and date-dependent incident severity. | `[BP]` | Ch 36 |
| **Rollouts per task** | Running each task k times and averaging, so a task yields a rate rather than a coin flip. | `[AHE]` | Ch 41 |
| **Run** | One goal under execution: a durable, versioned row that lives from minutes to weeks and holds nothing else. | `[DAR]` | Ch 5 |
| **Run driver** | The kernel component that is the runtime loop; Chapter 3's replacement for the banned word. | `[DAR]` | Ch 4, Ch 18 |
| **Run lifecycle** | The life of one goal, from arrival to a terminal state, independent of every process that touches it. | `[DAR]` | Ch 8 |
| **Run state** | What is happening right now in one run; owned by the runtime and meaningless once the run ends. | `[DAR]` | Ch 6 |
| **Run store** | The narrow, hot table holding one row per run; everything that grows lives elsewhere. | `[INF]` | Ch 17 |
| **Run taint** | A monotonic flag set when untrusted content enters a run, cleared by nothing, and scoped down only by moving the read into a sub-run. | `[INF]` | Ch 31 |
| **Runtime lifecycle** | The life of one process — boot, serve, drain, exit — which has no obligation to any run. | `[INF]` | Ch 8 |
| **Runtime loop** | The forty lines that claim a run, advance it under bounded limits, and release it, calling six ports and deciding nothing. | `[DAR]` | Ch 18 |
| **Runtime stability precondition** | The requirement that a measured regression be real before rollback is automated, since a flaky runtime biases reverts rather than randomising them. | `[INF]` | Ch 47 |

## S

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Same-transaction rule** | A state change and the event announcing it are committed together, or the gap between them is undetectable. | `[DAR]` | Ch 9 |
| **Sandbox lifecycle** | Create fresh, attach, execute, optionally snapshot, destroy — with reuse forbidden because state between units of work is a channel. | `[AHE]` | Ch 31 |
| **Sandbox profile** | The isolation configuration a tool runs under, named in the registry rather than chosen per call. | `[AHE]` | Ch 14 |
| **Saturation poisoning** | Sizing from measurements taken under load, where queueing inflates service time and justifies the overload that produced it. | `[INF]` | Ch 33 |
| **Scope** | The set of things a belief covers or an effect touches, matched by overlap to decide what an effect invalidates. | `[INF]` | Ch 12, Ch 25 |
| **Scope gate** | The decision to widen what the loop may learn from, which is a contract question rather than an engineering one. | `[INF]` | Ch 49 |
| **Seal** | Closing a trajectory at run end, when the outcome is finally known and the retention class can be assigned. | `[INF]` | Ch 16 |
| **Seeded chaos** | Scheduled injection of worker kills, lease expiries, and duplicate events, asserting the properties whose violation is otherwise invisible. | `[BP]` | Ch 40 |
| **Self-invalidation** | The dominant staleness case, in which the run's own committed effects make its own beliefs false. | `[INF]` | Ch 25 |
| **Self-modification gap** | The unsolved question of what prevents a self-editing harness from editing its own safety boundary, answered today only by there being no write path. | `[FUT]` | Ch 31 |
| **Sequence-asserting fake** | A fake port that checks the order of calls made to it, which is how ordering-as-correctness properties become testable. | `[BP]` | Ch 40 |
| **Service time** | The duration a resource is actually held, excluding the wait for permission to hold it. | `[BP]` | Ch 33 |
| **Settlement** | Replacing a reservation with what a call actually cost, or with the reservation itself when the actual is unknowable. | `[INF]` | Ch 13 |
| **Shadow comparison** | Running a candidate triple on identical inputs and discarding its output before the first effectful step, which is cheap here because the effect tag says where to stop. | `[BP]` | Ch 38, Ch 39 |
| **Sharded relay** | Partitioned outbox delivery with one claimer per partition, where rebalancing is the operation during which the guarantee is weakest. | `[INF]` | Ch 32 |
| **Sharpness** | How narrow a claim is, which must be scored alongside correctness or the scoring rule rewards hedging. | `[BP]` | Ch 45 |
| **Short-term memory** | What the model can see on one call; the assembled context, rebuilt every time. | `[INF]` | Ch 12 |
| **Signal** | Out-of-band control over a live run: steer, cancel, pause, or answer. | `[DAR]` | Ch 7 |
| **Signal exit (E4)** | Ending an episode because a cancel, pause, or steer was read at a checkpoint. | `[DAR]` | Ch 18 |
| **Silent misread** | A well-formed result the model draws a wrong conclusion from; the expensive ACI failure, with no automatic detector. | `[INF]` | Ch 15 |
| **Skill** | A packaged, reusable procedure loaded only when it is relevant, so its tokens are not always resident. | `[AHE]` | Ch 1 |
| **Skip propagation** | A failed node marking its successors `skipped` so every node reaches a terminal status and no join waits forever. | `[INF]` | Ch 24 |
| **Slice trade** | An edit that buys points in a heavy slice with points in a light one, which raises the aggregate and is invisible in it. | `[INF]` | Ch 48 |
| **Span** | One observed operation inside a run, wrapped in an envelope that carries its identity and harness version. | `[BP]` | Ch 16 |
| **Spillover** | Permission for one class's idle slots to take another's work; never upward into interactive. | `[INF]` | Ch 23 |
| **Stall** | K effectful steps producing no novel state, which is a healthy run that has stopped moving and is not an error. | `[INF]` | Ch 29 |
| **Stall escalation** | Observe, then replan, then park, then terminate — ordered so the free option is always tried first. | `[BP]` | Ch 29 |
| **Standing advantage** | What a fitted harness is worth right now against the minimal seed, on the currently deployed model. | `[INF]` | Ch 42 |
| **Standing cost** | Tokens an ACI improvement adds to every model call forever, as against a cost paid only on failure. | `[INF]` | Ch 15 |
| **State manager** | The component that records where a run has got to and who is entitled to advance it. | `[DAR]` | Ch 17 |
| **Stateless ingress** | An edge that keeps nothing in process memory, so any instance can serve any request and a deploy loses nothing. | `[DAR]` | Ch 7 |
| **Steer** | A human amendment to the goal, which ends the plan lineage and mints a new one by the same path a crash recovery takes. | `[DAR]` | Ch 7, Ch 30 |
| **Step** | One advance of a run's state machine, taking milliseconds and recorded as a row. | `[DAR]` | Ch 5 |
| **Step budget** | The maximum number of steps one episode may take before it must yield the worker. | `[DAR]` | Ch 5 |
| **Step-budget exit (E2)** | Bounds work between plan-level checkpoints, making cost per episode predictable. | `[DAR]` | Ch 18 |
| **Steps per episode** | The distribution whose mode reveals whether the step budget is doing anything. | `[INF]` | Ch 18 |
| **Steps per plan** | The distribution whose mode tells you whether the planner is planning or looping. | `[INF]` | Ch 10 |
| **Stopping rule** | Decompose until every step has a checkable postcondition and fits one context assembly, then stop. | `[INF]` | Ch 26 |
| **Store registry** | A declaration by every store of its tenant field, classification, retention, and deletion route, enforced by making unregistered stores unwritable. | `[BP]` | Ch 37 |
| **Store-evaluated expiry** | Deciding lease validity with the store's clock inside the claim statement, because a paused worker's clock is paused with it. | `[DAR]` | Ch 32 |
| **Strategy** | Which planning method produced a plan; ReAct is one value of this field, not the architecture. | `[BP]` | Ch 10 |
| **Structural assertion** | Asserting on the shape of what a model produced rather than its content, so a test survives the next model version. | `[BP]` | Ch 40 |
| **Structural enforcement** | Putting the authority check in the runner rather than the instructions, because the enforcer cannot be the party being constrained. | `[DAR]` | Ch 30 |
| **Structural partition** | The redacted, low-risk half of a trajectory — calls, order, verdicts, cost — which is most of what the loop needs and is retainable for years. | `[BP]` | Ch 44 |
| **Structural signal** | Tool names, ordering, verdicts, and cost — the low-risk half of a trajectory, and most of what evaluation and evolution actually need. | `[INF]` | Ch 37 |
| **Sub-agent** | A nested run with its own context, driven by the same loop through the same ports. | `[AHE]` | Ch 19 |
| **Sub-agent configuration** | The definition of a nested agent used to isolate context, not to build an org chart. | `[AHE]` | Ch 1 |
| **Sub-floor drift** | A cumulative movement made in steps each smaller than the noise floor, undetectable by any per-iteration check. | `[INF]` | Ch 48 |
| **Sub-run** | A child plan minted by a completing node, used when the number of branches is unknown until run time, so the parent graph stays immutable. | `[INF]` | Ch 24 |
| **Substrate** | The durable storage and queues everything else rests on; usually bought rather than built. | `[DAR]` | Ch 4 |
| **Success per unit cost** | The evaluation headline, which prevents a change that spends more for a marginal gain from counting as an improvement. | `[AHE]` | Ch 41 |
| **Superficially passing case** | A golden case that satisfies every obvious check while being wrong, which is the only kind that measures whether a grader can be fooled. | `[BP]` | Ch 28 |
| **Supersede** | Marking a plan as no longer current while retaining it forever, and voiding every approval that referenced it. | `[INF]` | Ch 10 |
| **Superseded** | The outcome a worker infers from affecting zero rows: it no longer owns the run and must stop. | `[INF]` | Ch 17 |
| **Superseded abandon** | A worker that lost its lease stopping without writing anything, not even a release. | `[INF]` | Ch 18 |
| **Surface** | The app, terminal, or chat window a person actually looks at. Outside the runtime entirely. | `[DAR]` | Ch 4 |
| **Surprise regression** | A task that broke without being named at risk, whose rate is the production measurement of the loop's weakest faculty. | `[INF]` | Ch 47 |
| **Survivability** | What the system around the model can withstand — a crash, a restart, a six-hour task, a bad decision. Built by you, never bought. | `[INF]` | Ch 0 |
| **Suspect** | The state of a belief that an overlapping effect may have invalidated, from which nothing but an actual re-probe restores trust. | `[INF]` | Ch 25 |
| **Sweep** | The one indexed query that reclaims runs whose leases have expired. | `[DAR]` | Ch 17 |
| **Sweeper** | The continuously scheduled job that expires leases on elapsed time alone; the only component belonging to neither lifecycle. | `[DAR]` | Ch 4, Ch 8, Ch 27 |
| **Synthetic probe** | A scheduled action that deliberately trips a safety control, so a quiet control can be distinguished from a dead one. | `[BP]` | Ch 34 |
| **System prompt** | Standing instructions sent with every call; the weakest of the seven, because the model may ignore prose. | `[AHE]` | Ch 1 |

## T

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Task graph** | A plan represented as nodes plus explicit dependency edges, so that independence is stated rather than inferred from position. | `[INF]` | Ch 24 |
| **Task retirement** | Replacing a benchmark task rather than editing it, preserving the comparability of every historical result. | `[BP]` | Ch 41 |
| **Tenant fairness** | Each tenant getting a share of capacity, as against arrival fairness which serves whoever queued first. | `[INF]` | Ch 23 |
| **Tenant-in-the-key** | Requiring the tenant to write rather than filtering on read, so a missing key fails in development instead of returning someone else's data. | `[BP]` | Ch 37 |
| **The record window** | The gap between an external effect happening and its result being recorded; narrowed by four mitigations and closed by none. | `[INF]` | Ch 21 |
| **Timeout coupling** | Temporal parameters fitted to a benchmark's task lengths, invisible in that benchmark and worsening with tuning. | `[AHE]` | Ch 29 |
| **Token kinds** | Input, cached, reasoning, and output — priced differently, and meaningless when aggregated into one number. | `[INF]` | Ch 13 |
| **Tombstone** | The envelope that survives when a trajectory's content expires, preserving aggregate answers and an auditable deletion. | `[INF]` | Ch 16 |
| **Tool description** | The prose the model reads and the only thing it knows about a tool; an editable harness surface in its own right. | `[AHE]` | Ch 1, Ch 14 |
| **Tool execution engine** | The single door to the world: resolves, validates, authorises, invokes, normalises, truncates, and records every tool call. | `[DAR]` | Ch 14 |
| **Tool implementation** | The code that runs, editable separately from the description and at a different rate. | `[AHE]` | Ch 1, Ch 14 |
| **Tool registry** | The one source for what a tool is, feeding descriptions to the model and enforcement properties to the runtime. | `[INF]` | Ch 14 |
| **Tool subset** | The smallest set of tools a sub-agent needs, which may be narrowed by evolution but never widened. | `[INF]` | Ch 19 |
| **Tool tax** | The fixed cost every tool definition levies on every model call, whether or not the tool is used. | `[INF]` | Ch 11, Ch 14 |
| **Trace store** | The durable home of trajectories; the largest and highest-risk dataset in the architecture. | `[INF]` | Ch 16 |
| **Trajectory** | The full record of one run — every span, with what the model could see at each — and the raw material of the evidence corpus. | `[AHE]` | Ch 16 |
| **Trajectory observability** | Per-run records answering whether the work is good, high-cardinality by construction and built in-house nearly everywhere. | `[AHE]` | Ch 34 |
| **Transactional outbox** | A table written in the same transaction as a state change, making the change and its announcement atomic. | `[DAR]` | Ch 22 |
| **Trial effect confinement** | Restricting a trial to tier-1 effects, which is what makes file-level rollback a sufficient undo. | `[BP]` | Ch 47 |
| **Truncation policy** | Per-tool rules for cutting output at the boundary, before it is stored or moved anywhere. | `[INF]` | Ch 14 |

## U

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Undetermined residue** | The accumulating population of edits kept with no established effect, which raises interference against every later measurement. | `[INF]` | Ch 48 |
| **Undetermined verdict** | The fourth verdict, recording that the evidence cannot decide, without which the arithmetic decides anyway. | `[INF]` | Ch 47 |
| **Undroppable field** | A field the distiller may never summarise away, because losing it changes which component a failure routes to. | `[INF]` | Ch 44 |
| **Unexplored** | The contract field recording what a child did not cover, so partial work is distinguishable from complete. | `[INF]` | Ch 19 |
| **Unfair sampling** | A retention policy that always keeps failures, stalls, overrides, gates, dead letters, and the tail, and samples clean successes. | `[BP]` | Ch 34 |
| **Ungradable** | The state where evaluation itself failed, kept distinct from failure so grader outages are not attributed to runs. | `[INF]` | Ch 28 |
| **Unknown spend** | A swept reserve recorded as neither spent nor free, because a timed-out call may still have been served and billed. | `[BP]` | Ch 35 |
| **Unrepresentable protection** | A property the benchmark's score cannot express, which is the single reason every item is on the containment list. | `[INF]` | Ch 46 |

## V

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Variance-adjusted utilisation** | A lower utilisation target on heavy-tailed surfaces, or — better — splitting the distribution into latency classes. | `[BP]` | Ch 33 |
| **Verb granularity** | How large each tool is, bounded below by the tool tax and above by the effect tag needing one value. | `[INF]` | Ch 15 |
| **Verdict** | Keep, improve, or rollback-and-pivot, assigned by intersecting predictions with observed deltas. | `[AHE]` | Ch 20 |
| **Verdict lattice** | The ranked outcomes plus the rule that deterministic checks set a floor a model judgment may only lower. | `[DAR]` | Ch 28 |
| **Version CAS** | A conditional update guarded by an expected version, so a stale writer's write affects zero rows. | `[DAR]` | Ch 17 |
| **Version triple** | The code sha, harness hash, and model id recorded on every run, without which no two runs are comparable. | `[AHE]` | Ch 38 |
| **Volatile boundary** | The offset before which the context is asserted byte-identical to the previous call in this run. | `[INF]` | Ch 11 |
| **Volatility band** | Whether material changes per deploy, per replan, or per step; the axis assembly order sorts on. | `[INF]` | Ch 11 |

## W

| Term | Definition | Tag | Defined in |
|------|------------|-----|------------|
| **Wall age** | Time since a run was created, including every hour it spent parked. | `[INF]` | Ch 8 |
| **Wall-clock exit (E1)** | Bounds one run's hold on a worker, so slow steps cannot monopolise it. | `[DAR]` | Ch 18 |
| **Window of ambiguity** | The interval from a worker losing the ability to verify its lease to its in-flight effect completing, during which two workers may both act. | `[INF]` | Ch 32 |
| **Withholding** | Omitting a belief the runtime cannot afford to refresh, on the grounds that no map beats a wrong map nothing can detect. | `[INF]` | Ch 25 |
| **Work class** | A category of work with its own queue and reserved capacity, so short work is never stuck behind long. | `[DAR]` | Ch 23 |
| **Working budget** | What remains of the context window after output reserve, system prompt, tool definitions, and long-term memory are paid for. | `[INF]` | Ch 11 |
| **World model** | A disposable cache of beliefs about an environment the runtime does not control, justified only by the cost of re-deriving them. | `[INF]` | Ch 25 |
| **Write scope** | The enumerated set of paths the loop may write, checked against the diff rather than against the entry. | `[AHE]` | Ch 46 |

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
| Ch 17 | State manager, Lease column, Version CAS, Checkpoint, Superseded, Sweep, Partial expiry index, Run store, Claim race |
| Ch 18 | Runtime loop, Run driver, Episode limits, Exit condition, Wall-clock exit (E1), Step-budget exit (E2), Signal exit (E4), Cancellation latency, Superseded abandon, Steps per episode |
| Ch 19 | Sub-agent, Context isolation, Delegation contract, Marshalling, Return contract, Unexplored, Budget carving, Nesting depth cap, Tool subset, Compression ratio, Cancellation cascade |
| Ch 20 | Outer loop, Algorithm 1, Component observability, Experience observability, Decision observability, Change manifest, Predicted fixes, At-risk tasks, Constraint level, Verdict, Controllability, Containment boundary, Non-additivity |
| Ch 21 | Durable execution, Activity ledger, Resume, Re-run, Replay, Partial match, Determinism quarantine, Attempt count, Effect log, The record window |
| Ch 22 | Event spine, Transactional outbox, Relay, Claim-based consumption, Cursor, Partition key, Poison event, Dead letter, Command port, At-least-once delivery, Oldest unprocessed age |
| Ch 23 | Convoy effect, Work class, Reserved capacity, Spillover, Tenant fairness, Admission control, Deferral, Model semaphore, Binding resource, In-flight cap |
| Ch 24 | Task graph, Ready set, Fan-out, Fan-in, Durable join, Join policy, Critical path, Admission validation, Skip propagation, Sub-run, Presentational rank |
| Ch 25 | World model, Belief, Probe, Scope, Self-invalidation, Suspect, Contradiction, Withholding, Backstop age, Commit-keyed sharing |
| Ch 26 | Plan lineage, Repair, Replan, Failure record, Contract, Contract-first planning, Stopping rule, Failure classification, Replan storm, Plans per goal, Least-to-most |
| Ch 27 | Effect ledger, Reversibility tier, Rollback, Compensation, Escaped effect, Failure table, Dead letter, Sweeper, Attempt cap, Argument binding at apply time, Outstanding obligation |
| Ch 28 | Verdict lattice, Floor, Downgrade-only, Reflection, Judge independence, Golden set, Superficially passing case, False pass, Attempted upgrade, Evaluator-isomorphic validation, Ungradable |
| Ch 29 | Novel durable state, Stall, Novelty window, Stall escalation, Budget axis, Finish reserve, Point of no return, Timeout coupling, Parking, Draining |
| Ch 30 | Structural enforcement, Gate, Park, Argument-hash scoping, Steer, Override, Gate policy, Gated-effect coverage, Gate expiry, Rendered arguments, One proposer, four vetoes |
| Ch 31 | Provenance label, Provenance lattice, Label inheritance, Blast radius, Capability scoping, Declared needs, Egress allowlist, Run taint, Sandbox lifecycle, Self-modification gap |
| Ch 32 | Lease, Window of ambiguity, Fence token, Exactly one driver, Store-evaluated expiry, Renewal disarming, Sharded relay, Cross-process fairness, Clock discipline, Belief versus ownership |
| Ch 33 | Capacity surface, Service time, Queue time, Little's Law sizing, Load generator, Capacity commitment, Binding surface, Saturation poisoning, Variance-adjusted utilisation, Capacity invalidation |
| Ch 34 | Infrastructure observability, Trajectory observability, Label allowlist, Flow annotation, Absence alerting, Synthetic probe, Identity partial match, Unfair sampling, Always-keep category, Retention as a Level 5 decision |
| Ch 35 | Cost per successful outcome, Retry multiplier, Reserve-then-settle, Reserve gap, Orphaned reserve, Unknown spend, Cached input, Instruction share, Cost attribution tags, Budget sub-cause |
| Ch 36 | Liveness objective, Honesty objective, Accounting objective, Published statistic, Burn rate, Honesty auditor, Degradation ladder, Disclosed degradation, Quality regression, Rolling window |
| Ch 37 | Store registry, Tenant-in-the-key, Cross-run store, Capture-time redaction, Classification split, Structural signal, Deletion certificate, Deletion refusal, One-way derivation, Memory scope |
| Ch 38 | Version triple, Harness version, Invalidation event, Invalidation register, Model-conditional content, Exact pin, Deprecation clock, Resolved config hash, Config freeze, Shadow comparison |
| Ch 39 | Harness workspace, Regression harness, Evaluation gate, Blast-radius linter, Per-slice effect, Shadow comparison, Merge-is-not-deploy, Removal experiment, Instruction accretion, Affected-population query |
| Ch 40 | Port boundary, Deterministic tier, Replay tier, Divergence, Sequence-asserting fake, Controlled clock, Retry prohibition, Structural assertion, Seeded chaos, Fixture triple |
| Ch 41 | Noise floor, Minimum detectable effect, Rollouts per task, Paired evaluation, Per-slice floor, Corpus version, Task retirement, Corpus drift, Success per unit cost, Evaluation work class |
| Ch 42 | Standing advantage, Carried advantage, Fit decay, Re-fit, Release cadence, Reading bottleneck, Minimal seed, Counterfactual run, Evolution readiness, Pace-keeping |
| Ch 43 | Mount point, Component registry, Component inventory, Orthogonality, Overlap, Disablement probe, Behaviour tag, Orphaned component, Default owner, Attribution contamination |
| Ch 44 | Per-task analysis, Benchmark-level overview, Evidence pointer, Undroppable field, Diffuse pattern, Structural partition, Distillation ratio, Corpus staleness, Clean-success contrast, Context-gap misdiagnosis |
| Ch 45 | Sharpness, Claim width, Enumerated prediction, Entry seal, Evidence novelty, Proposal storm, Circular root cause, Null at-risk claim, Evidence ledger |
| Ch 46 | Write scope, Read-only runs directory, Non-deletable rule, Unrepresentable protection, Displacement, Contested constraint, Level escalation, Constraint relaxation |
| Ch 47 | Attribution intersection, Undetermined verdict, Predicted-set collision, Inside-floor keep, Mechanism check, Surprise regression, Trial effect confinement, Runtime stability precondition, Edits per iteration |
| Ch 48 | Interference, Redundant closure, Mechanism shift, Slice trade, Sub-floor drift, Per-slice gate, Undetermined residue, Convergence flattening, Indirect boundary erosion |
| Ch 49 | Review scan, Relaxation gate, Scope gate, Gate refusal rate, Access inheritance, Harness cleanup, Autonomy ladder, Fallback atrophy, Evaluation capture |
