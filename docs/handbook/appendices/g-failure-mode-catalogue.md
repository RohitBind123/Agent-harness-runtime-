# Appendix G — Failure Mode Catalogue

> **Generated file. Do not edit by hand.**
>
> Assembled from the chapters by `tools/build_appendices.py`. To change an
> entry, edit the chapter it comes from and regenerate.

Every entry from the *Failure Modes* section of every chapter, in one table. The handbook treats the failure table as a design artefact rather than a postscript (Chapter 27 §14), so this is the closest thing the book has to a single specification of what can go wrong.

478 failure modes across 50 chapters. **34 of them have no detector** — the recurring shape of Levels 3 through 5, where the failure produces no error and often no signal at all.

---

| Chapter | Failure | Trigger | Detector | Recovery |
|---|---|---|---|---|
| [Ch 0](../chapters/00-evolution-of-ai-systems.md) |  | — | — | Not applicable |
| [Ch 0](../chapters/00-evolution-of-ai-systems.md) |  | — | — | Restart from zero |
| [Ch 0](../chapters/00-evolution-of-ai-systems.md) |  | — | — | Continuous lease sweeping, resume at last checkpoint |
| [Ch 0](../chapters/00-evolution-of-ai-systems.md) |  | — | — | Attribution verdict decides keep or revert |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | Fix placed at too weak a level | — | The failure class recurs across iterations | Roll back the edit; re-approach at a stronger level `[AHE App. B.2]` |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | Component created but not registered | — | Configuration validation; runtime logs | Register it; add validation to CI |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | Harness fitted to a superseded model | — | Task completion drops after a model change with no code change | Re-fit the operating point; treat as a versioning event |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | Components interfering | — | Aggregate gain below the sum of individual gains | Measure single-component variants; Ch 48 |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | Prompt bloat | — | System prompt grows monotonically; per-call cost rises with no gain | Migrate rules to enforcing components |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | Memory rot | — | Long-term memory accumulates lessons that no longer hold | Periodic review; Ch 49 |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Worker killed mid-episode | — | run lease expiry | sweeper clears the lease; the run re-drives from its last checkpoint |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Worker killed mid-activity | — | activity lease expiry | the activity becomes re-claimable; identity ensures replay, not re-spend |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Model call hangs | — | the episode deadline | the abort tears down the stream, frees the slot, releases the reservation |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Two workers race a run | — | version check returns zero rows | the loser drops its job; no compensation needed |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Poison event | — | attempt counter reaches its cap | dead-lettered; only that partition is affected |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Run exceeds its budget | — | reservation exceeds the remaining ceiling | the run parks awaiting a budget decision; nothing is spent meanwhile |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Human never answers a gate | — | park age exceeds a policy threshold | escalation or expiry by policy; never silently abandoned |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |  | — | The §2.2 test, run as a CI check | — |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |  | — | An import-graph rule in CI | — |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |  | — | Latency correlation; a lint rule on edge modules | — |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |  | — | Duplicate side effects after rollout | — |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |  | — | Test setup that requires a database | — |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |  | — | Lock-wait metrics by table | — |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |  | — | Reconciliation job; a count mismatch | — |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) | Worker killed mid-episode | — | Run lease expiry | Sweeper clears it; the next relay wake re-drives from the last checkpoint |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) | Worker killed mid-activity | — | Activity lease expiry | Re-claimable; identity ensures a replay rather than a re-spend |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) | Relay worker dies holding claims | — | Claim timestamp older than threshold | The sweeper releases them for re-claim |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) | Two drivers race one run | — | Version check returns zero rows | The loser drops its job; no compensation needed |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) | Edge process dies | — | Load balancer health check | Stateless; another instance serves. No work is affected |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Lease expiry sweep `[DAR §14]` | Re-enqueued from the last checkpoint |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Reservation exceeds the remaining ceiling | Parks awaiting a budget decision |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Steps-per-episode distribution with a mode at 1 `[DAR §15]` | Diagnose: budgets, signal storm, or a park loop |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Version check returns zero rows | The loser drops its job |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Plan identity mismatch at dispatch | The stale dispatch is discarded, not executed |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Sweeper | Re-claimable; identity replays rather than re-spends |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Attempt cap | Dead-lettered; the run replans or escalates |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Same run and position, different plan or inputs | **Alert, never log** `[DAR §6.2]`; it is silent by nature |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | Park age exceeds a policy threshold | Escalation or expiry by policy; never silently abandoned |
| [Ch 5](../chapters/05-five-nouns.md) |  | — | The cold open | Vocabulary, and a dashboard that shows park reason |
| [Ch 6](../chapters/06-state-separation.md) | run → domain | — | Schema check; the 3am incident of Ch 4 | — |
| [Ch 6](../chapters/06-state-separation.md) | domain → run | — | Retention job reveals it | — |
| [Ch 6](../chapters/06-state-separation.md) | model → run | — | Golden-set replay mismatch (Ch 41) | — |
| [Ch 6](../chapters/06-state-separation.md) | model → harness | — | Cache-key audit | — |
| [Ch 6](../chapters/06-state-separation.md) | domain → harness | — | Abstraction check at write; scanning at read | — |
| [Ch 6](../chapters/06-state-separation.md) | domain → harness | — | Secret scanning in CI | — |
| [Ch 6](../chapters/06-state-separation.md) | version skew | — | Pin the harness version at founding (Ch 38) | — |
| [Ch 6](../chapters/06-state-separation.md) | run → harness | — | Lifetime assertion in tests | — |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Client disconnects | — | Support tickets, which is too late | Hydrate-then-subscribe (§6) |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Progress written to the outbox | — | Event-table growth rate vs run rate | Delete it; progress is not a fact |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Duplicate submit | — | Idempotency-key collision metric | The command port replays the original result `[DAR §4.4]` |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Loop in the edge | — | Correlation between p99 latency and model latency | §5.1, §5.2 |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Consumer in the edge | — | Deploy-time anomaly | §5.3 |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Edge unavailable | — | Parked-run count by park reason | Restore; nothing is lost |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Read model leaks internals | — | Contract test on the response shape | Project, do not expose |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Stream fan-out overload | — | Open-subscriber count per instance | Cap subscribers per run; shed to polling |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | Seq gap on reconnect | — | Client-side gap detection | Re-hydrate (§7) |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Orphaned run | worker dies without draining | sweeper, on `lease_until < now` | expire, re-enqueue; one lease period |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Recovery only at boot | recovery implemented as a startup scan | `oldest_expiry_lag_ms` correlating with deploys | move it to the sweeper — the cold open |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Drain that finishes runs | shutdown waits for run completion | deploy duration ~ run duration | finish the step, release the lease |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Drain without release | step 4 of §6.3 omitted | `runs_requeued` = 0 in `DrainReport` | release all leases before exit |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Lease shorter than a step | lease under p99 step duration | two workers advancing one run; version CAS conflicts | lease ≥ 3× p99 step; alert on conflicts |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Lease longer than tolerable | lease sized for comfort | `oldest_expiry_lag_ms` p99 near the lease period | lease is your worst-case recovery latency; choose it as such |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Sweeper wedged | one poison row aborts the batch | `SweepReport` counts flat while lag rises | per-row error isolation; dead-letter the poison row |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Sweeper stampede | every worker sweeps on the same tick | periodic write spikes | jitter the interval per worker |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Park woken by polling | a timer in a worker rather than an event | parks resolving only while workers are healthy | parks resolve on events; the sweeper wakes `wake_at` |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Zombie advance | a partitioned worker resumes after expiry | version CAS returns zero rows | fail closed and abandon; the CAS is the guard |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Wrong-axis reading | a question answered without routing | three plausible contradictory answers | route first — the cold open |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Braided flows | "consolidating" decision, movement, and durability into one path | no diagram can be drawn without three units on an arrow | keep the three separable; refuse the consolidation |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Progress on the event axis | durability applied to telemetry | events table growing with viewer count | progress is never durable (Ch 7) |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Context on the event axis | assembled context persisted as truth | replay produces a transcript, not a replay | context is a projection (Ch 6) |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Event outside its transaction | append after commit, "for clarity" | state changed with no event, rarely, under load | one transaction, always (Ch 22) |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Unbounded tool output | no ceiling at the tool boundary | next step's context spikes | truncate at the boundary (Ch 14) |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Invisible cost | optimising the model choice, not the context | spend per step flat while model price falls | measure per-step context bytes |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Silent stall | a dead driver | **no** error rate change; data flow goes quiet | alert on absence, not on errors (Ch 34) |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Multiple proposers | middleware or tools injecting steps | "why did it do that?" has no single answer | one proposer, three vetoes (§4.1) |
| [Ch 10](../chapters/10-the-planner.md) | Mutable plan | in-place revision on steer | approvals resolving against changed actions | frozen `Plan`, new `plan_id` — the cold open |
| [Ch 10](../chapters/10-the-planner.md) | Approval drift | approval keyed to position, not identity | audit shows approval and action disagree | key approvals to `(plan_id, step_id)` |
| [Ch 10](../chapters/10-the-planner.md) | Identity at dispatch | `activity_id` computed when dispatching | duplicate spend under concurrency | mint at plan time (§4.2) |
| [Ch 10](../chapters/10-the-planner.md) | Repairing validator | validator coerces bad proposals | planner defects never surface; runs quietly degrade | reject and emit `run.plan.rejected` |
| [Ch 10](../chapters/10-the-planner.md) | Model declares its own effect tag | `effect` read from the completion | an effectful step executing with no gate | tag comes from the tool registry |
| [Ch 10](../chapters/10-the-planner.md) | Replan storm | every result triggers `should_replan` | steps-per-plan mode of 1; cost per run climbing | make replanning a decision, not a reflex |
| [Ch 10](../chapters/10-the-planner.md) | Plan longer than the budget | validator does not check step count | budget exhausted mid-plan, always | validate step count against remaining budget |
| [Ch 10](../chapters/10-the-planner.md) | Two current plans | concurrent replan | second insert violates the index | the partial unique index (§7.2) |
| [Ch 10](../chapters/10-the-planner.md) | Planner reads the world | "peeking" at a repository to plan better | planner untestable without a sandbox | propose a pure step instead |
| [Ch 10](../chapters/10-the-planner.md) | Orphaned approval | approval outlives its plan | gate matches nothing; run parks forever | void approvals on supersede (§5.3 step 6) |
| [Ch 11](../chapters/11-the-context-system.md) | Cache prefix broken | volatile content placed in the stable band | cache-hit ratio drops; cost per run rises | the Verifier's prefix assertion — the cold open |
| [Ch 11](../chapters/11-the-context-system.md) | Junk drawer | sources added, none removed | tokens per source trending up; no source at 0 | mandatory `budget_share` summing to 1.0 |
| [Ch 11](../chapters/11-the-context-system.md) | Condensed away a needed fact | summarisation of a span containing a key detail | the model re-derives the same fact repeatedly | condense spans not items; check `context.compacted` |
| [Ch 11](../chapters/11-the-context-system.md) | Silent context gap | a source failed and returned empty | model proceeds confidently; no error anywhere | assert per-source minimum sizes at verify |
| [Ch 11](../chapters/11-the-context-system.md) | Include-or-drop only | no deferral policy | budget states jump COMFORTABLE to COMPACTING | implement Defer (§5.3) |
| [Ch 11](../chapters/11-the-context-system.md) | Truncation in the wrong layer | context system truncating raw tool output | one large result inflates every later call | truncate at the tool boundary (Ch 14) |
| [Ch 11](../chapters/11-the-context-system.md) | Context stored as truth | a `contexts` table appears | replay reproduces transcripts; policy fixes do not apply retroactively | it is model state; wire 8 |
| [Ch 11](../chapters/11-the-context-system.md) | Output reserve omitted | budget computed against the full window | truncated completions near the ceiling | reserve output first (§2.3) |
| [Ch 11](../chapters/11-the-context-system.md) | Tool tax invisible | tool count grows unnoticed | fixed cost per call creeping up | report stable-band tokens as its own metric |
| [Ch 11](../chapters/11-the-context-system.md) | Compaction thrash | horizon too close to the budget | `compactions_this_run` reaching 2 | E3 alert; widen the horizon or defer more |
| [Ch 12](../chapters/12-the-memory-system.md) | Wrong lesson, kept forever | a coincidence recorded as a rule | contradiction events on that entry | confidence floor; contradiction lowers rather than flips — the cold open |
| [Ch 12](../chapters/12-the-memory-system.md) | Recommendation stored as observation | the proposal contains an imperative | proposals containing "should", "always", "ignore" | reject; recommendations belong in skills |
| [Ch 12](../chapters/12-the-memory-system.md) | Immediate authority | a new entry loaded at once | behaviour changing after a single run | the load floor (§5.4) |
| [Ch 12](../chapters/12-the-memory-system.md) | Overwrite on contradiction | most recent observation wins | an entry flip-flopping across runs | contradictions lower confidence; never rewrite |
| [Ch 12](../chapters/12-the-memory-system.md) | Stale entry about a moved world | environment changed; nothing re-checked | contradiction rate rising (E4) | decay from `last_confirmed`; E4 alert |
| [Ch 12](../chapters/12-the-memory-system.md) | Tenancy leak | a specific written verbatim | scan the file for secrets and identifiers | abstraction at write time; git history is unredactable (Ch 37) |
| [Ch 12](../chapters/12-the-memory-system.md) | Unbounded growth | append-only with no curation | file exceeding its Ch 11 budget share | periodic curation; retire, do not delete |
| [Ch 12](../chapters/12-the-memory-system.md) | Vector-store reflex | semantic retrieval instead of a file | nobody can enumerate what is known | keep it small and readable (§2.4) |
| [Ch 12](../chapters/12-the-memory-system.md) | Write blocking a run | `propose` on the critical path | run latency rising at completion | write path is off-path and never raises |
| [Ch 12](../chapters/12-the-memory-system.md) | Episodic fed into a live run | a previous trajectory pushed into context | the model repeating an old run's errors | records are not instructions (§2.3) |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Abandoned call settled at zero | timeout treated as cancellation | spend exceeding the sum of recorded calls | settle at the reservation — the cold open |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Timeout without abort | a deadline with no abort handle | provider bills for calls nothing consumed | fire the abort handle; prefer streaming |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Second door to the provider | SDK imported outside the adapter | a lint rule on the import graph | one import, enforced in CI (§2.2) |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Cap enforced after the fact | spend checked post-call | a single run exceeding its cap | reserve before, settle after |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Leaked reservation | worker died between reserve and settle | run budget shrinking with no spend | reservations expire; the sweeper releases them |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Retry after a lost success | result lost in transit, ledger empty | `retry_after_timeout` rate | cap at one retry; prefer streaming; measure it |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Retrying a content refusal | every non-success treated as transient | repeated identical refusals | E5 is terminal (§6) |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Provider vocabulary escapes | a `finish_reason` string compared upstream | grep for provider literals above the port | normalise at step 6 |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Missing usage coerced to zero | `usage.get("cached", 0)` | cost dashboard too good to be true | nullable fields; `cost_is_estimated` |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Effort tier changed globally | treated as config, not harness version | non-monotone quality change after a deploy | pin the tier with the harness version |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | Sampling drift | temperature set per call site | irreproducible runs; replay diverges | policy resolved from the pinned version only |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Description drift | implementation semantics changed, prose did not | none mechanical; `tool.schema.rejected` only for shape | review rule on any tool diff — the cold open |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Empty means "nothing there" | tool returns empty for a malformed query | model concluding absence from emptiness | `empty_means` in the description (§5.1) |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Silent truncation | result cut with no marker | model reasoning from a subset as if complete | `truncated` + `original_bytes` always set |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Truncation too late | cutting in the context system | 10 MB in the ledger, trajectory, and every replay | truncate at step 9, before record |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Pure tool became effectful | a write added to a read tool | review rule: any write in a pure tool's diff | re-tag; the gate then applies |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Model-declared effect | tag taken from the completion | an effectful step running ungated | tag from the registry only |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Effectful auto-retry | retry policy applied uniformly | duplicate effects | retry is PURE only (§5.3) |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Effect without a record | worker died between invoke and record | the domain event arrives, the result does not | §6.1: idempotent implementations; residual named |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Partial collapsed to failed | two-valued outcome | retries that re-apply completed work | three-valued `Outcome` (§5.6) |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Coerced arguments | validator repairs instead of rejecting | planner defects invisible; runs quietly degrade | reject and emit the event |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Capability by instruction | "do not use tool X" in the prompt | the tool being used | omit it from `descriptions_for` |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | Unbounded tool count | tools added, never removed | Ch 11 stable-band tokens rising | the tool tax is a budget line |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Representation disagreement | two tools address one object differently | silent wrong edits | remove or verify the coordinate — the cold open |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Diagnostic-only errors | "invalid input" with no next step | `error_then_same_error` rate | three-field `ToolError` (§5.4) |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Retry loop | uninstructive error, model repeats itself | `aci.retry_loop.detected` | make the error instructive |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Silent misread result | ambiguous result, confident conclusion | none automatic; outcome quality only | `empty_means`, stable formats, anchors |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | One coarse verb | `run_command` for everything | effect tag cannot be assigned | split by effect and result shape (§5.2) |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Verb sprawl | a tool per operation | Ch 11 stable-band tokens rising | merge tools with identical tag, policy, and usage |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Unit ambiguity | `timeout=30`, meaning unclear | instant timeouts that read as flakiness | put the unit in the name |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Unbounded error text | a stack trace returned to the model | context spikes after failures | bound errors (§5.4) |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Prompt used as the fix | "remember to pass a glob" in instructions | the mistake recurring anyway | route with §5.5's table |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Description growth | richer prose, unbounded | tool tax rising | §12's trade, made explicitly |
| [Ch 16](../chapters/16-the-observation-system.md) | Captured actions, not inputs | tracing built from component outputs | any "what did it see?" question | capture the context span — the cold open |
| [Ch 16](../chapters/16-the-observation-system.md) | No harness version in the envelope | version treated as config, not run data | attribution impossible after any deploy | 16 bytes per span (§5.1) |
| [Ch 16](../chapters/16-the-observation-system.md) | Redaction at read time | a filter in the viewer | any export or backup path bypasses it | redact at capture; irreversible (§5.4) |
| [Ch 16](../chapters/16-the-observation-system.md) | Uniform sampling | service-trace habits | the failures are never in the sample | outcome-weighted retention (§5.5) |
| [Ch 16](../chapters/16-the-observation-system.md) | Capture failing a run | `await observe(...)` with error handling | run failures correlate with store health | fire-and-forget by contract (§4.1) |
| [Ch 16](../chapters/16-the-observation-system.md) | Trajectories in the outbox | trajectory treated as an event | events table growth tracking run count | facts to the outbox, spans to the store |
| [Ch 16](../chapters/16-the-observation-system.md) | Facts read from traces | convenience query against the trace store | retention cannot be shortened without breaking behaviour | nothing durable reads it (§5.6) |
| [Ch 16](../chapters/16-the-observation-system.md) | Unbounded growth | no retention clock | trace store dominating storage cost | clock set at seal (§7) |
| [Ch 16](../chapters/16-the-observation-system.md) | Buffer held to seal | worker memory holding spans | spans lost when a worker releases a run | flush at checkpoint (§7.1) |
| [Ch 16](../chapters/16-the-observation-system.md) | Silent redaction | secrets removed without a marker | reader believes the model saw a gap | leave `[redacted:...]` markers |
| [Ch 16](../chapters/16-the-observation-system.md) | Unaudited automated reads | the Evolve Agent reading directly | nobody can say what it read | audit reads, including machine ones (Ch 49) |
| [Ch 17](../chapters/17-the-state-manager.md) | Ownership as a lock | `FOR UPDATE` or advisory lock | no query answers "who owns this?" | ownership is a value — the cold open |
| [Ch 17](../chapters/17-the-state-manager.md) | Lease without CAS | expiry implemented, version not | two workers advancing one run | add `WHERE version = :expected` |
| [Ch 17](../chapters/17-the-state-manager.md) | CAS without lease | version implemented, expiry not | orphans never reclaimed | add `lease_until` and a sweeper |
| [Ch 17](../chapters/17-the-state-manager.md) | Worker-side clock | expiry compared in application code | skewed fleet, phantom expiries | compare with the DB's `now()` |
| [Ch 17](../chapters/17-the-state-manager.md) | Checkpoint at episode end | "checkpointing every step is wasteful" | crash loses many steps | every step; ~5 ms (§5.1) |
| [Ch 17](../chapters/17-the-state-manager.md) | Signals read outside the txn | a separate polling loop | cancellation latency ~ episode length | fold into checkpoint (§5.4) |
| [Ch 17](../chapters/17-the-state-manager.md) | Lease shorter than a step | floor ignored | CAS conflicts; runs stolen mid-step | ≥ 3× p99 step |
| [Ch 17](../chapters/17-the-state-manager.md) | Wide runs row | large columns on the hot row | write amplification at scale | move growing data out (§7.2) |
| [Ch 17](../chapters/17-the-state-manager.md) | Unbatched sweep | one enormous UPDATE on a backlog | a long transaction blocking writers | `limit`, and repeat |
| [Ch 17](../chapters/17-the-state-manager.md) | Zero rows treated as an error | claim race logged as a failure | error rate tracking worker count | it is a normal outcome |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Signals read at episode end | a separate read outside the checkpoint | cancellation latency ~ episode length | read in the checkpoint — the cold open |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Run to completion | no episode bound | deploys blocked; long crash losses | bound with E1 and E2 |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Transaction around the loop body | "for consistency" | pool exhausted at low concurrency | nothing scarce across a call (§5.3) |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Checkpoint at episode end | "every step is wasteful" | `checkpoints != steps_taken` | the invariant in §9 |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Loop acquires a decision | convenience: it knows the answer | a port with nothing left to decide | §5.2's table |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Step budget 1 in production | left after an incident | steps-per-episode mode of 1 | a dial, not a default (§5.5) |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Writing after Superseded | tidy release on the way out | version conflicts from an abandoned worker | write nothing (§7.1) |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Loop-local cache | avoiding a re-read across episodes | behaviour differing by worker age | hold nothing between episodes (§7.2) |
| [Ch 18](../chapters/18-the-runtime-loop.md) | A fifth exit condition | an `if` added to the loop | episodes ending for unexplained reasons | four, and the evaluator is a component |
| [Ch 18](../chapters/18-the-runtime-loop.md) | Park re-enqueued | uniform treatment of exits | parked runs spinning through the queue | E3 does not re-enqueue |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Decomposed by role | mirroring a human team | hand-offs where the receiver lacks rationale | decompose by context — the cold open |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Parent awaits the child | `await delegate(...)` | worker count scaling with tree depth | park; return a handle (§4.1) |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Unbounded return | `{"result": str}` | parent context growing after delegations | bounded, structured, validated (§5.3) |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Partial read as exhaustive | no `complete` / `unexplored` | confident answers from truncated searches | require both fields |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Budget added, not carved | child cap independent of parent | total spend unbounded in depth | carve from remaining (§5.5) |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Depth clamped silently | recursion capped at the boundary | quality decline with no signal | refuse; emit an event (§5.6) |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Child writes parent state | convenience coupling | parent state changing outside its loop | children return values |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | No cancellation cascade | independent lifecycles | cancelled runs with children still spending | terminal states cascade (§7.2) |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Sub-agent with write tools | inherited the parent's tool set | blast radius equal to the parent's | smallest subset (§5.4) |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | Agents where a graph would do | parallelism sought via delegation | many shallow agents, little context saved | Chapter 24 |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | No per-edit predictions | changes shipped in a batch | a score that moved and cannot be attributed | the manifest — the cold open |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Manifest written after results | convenience | predictions that always look correct | append-only; write before measuring |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Distil before attribute | the natural reading order | errors compounding across iterations | attribute first (§4.1) |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Optimising an uncosted score | quality measured, spend not | scores rising with cost rising faster | cost-normalised metrics (§5.4) |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Fixing at the wrong level | prompt edits for enforcement problems | repeated edits to one prompt, same failure | constraint level (§5.3) |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Editing outside the workspace | a broader action space "to be effective" | protections quietly disappearing | the boundary (§5.5) |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Trusting stacked gains | summing per-component measurements | predicted total exceeding measured | gains do not stack `[AHE §4.4.1]` |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Trusting regression prediction | treating `at_risk` as reliable | breaks in tasks nobody flagged | ~2× random; rollback is automatic |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Loop runs on production | no separation of measurement and serving | a bad iteration reaching users | promote explicitly (Ch 39) |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | Corpus contains secrets | redaction at read rather than capture | an automated reader with broad access | Chapter 16 §5.4 |
| [Ch 21](../chapters/21-durable-execution.md) | Replay that re-executes | one word for three operations | duplicate effects from debugging | the `ExecutionMode` enum — the cold open |
| [Ch 21](../chapters/21-durable-execution.md) | Identity at dispatch | computed when the tool is called | duplicate spend under concurrency | mint at plan time (Ch 10) |
| [Ch 21](../chapters/21-durable-execution.md) | Partial match reused | matching on run and step only | wrong results returned confidently | anomaly, alert, never reuse (§5.3) |
| [Ch 21](../chapters/21-durable-execution.md) | Ledger with a TTL | treating it as a cache | intermittent double-spend after expiry | RECORDED is terminal (§7.1) |
| [Ch 21](../chapters/21-durable-execution.md) | Effectful auto-retry | uniform retry policy | duplicate external effects | pure only (Ch 14 §5.3) |
| [Ch 21](../chapters/21-durable-execution.md) | Non-determinism outside an activity | clock, random, set iteration | replays that diverge | the quarantine (§5.4) |
| [Ch 21](../chapters/21-durable-execution.md) | Plan edited in place | violating Ch 10 | partial-match anomalies appearing | fix the planner; the anomaly is the signal |
| [Ch 21](../chapters/21-durable-execution.md) | No attempt count to the planner | runtime decides silently | effects repeated without anybody choosing | surface `attempts` (§6.1) |
| [Ch 21](../chapters/21-durable-execution.md) | Checkpoint interval widened | "every step is wasteful" | more lost on each crash | the interval IS the loss bound |
| [Ch 21](../chapters/21-durable-execution.md) | Assuming the window is closed | trusting the ledger absolutely | rare duplicate third-party effects | it is a residual; say so (§5.5) |
| [Ch 22](../chapters/22-the-event-spine.md) | Cursor consumer | the obvious stream design | **nothing happens**; no error moves | claim-based relay — the cold open |
| [Ch 22](../chapters/22-the-event-spine.md) | Publish after commit | it looks equivalent | changes with nothing told, rarely | one transaction (§5.1) |
| [Ch 22](../chapters/22-the-event-spine.md) | Silent stall | no alert on absence | oldest unprocessed age rising | alert on it; `relay.stalled` |
| [Ch 22](../chapters/22-the-event-spine.md) | Batch ack | fewer writes | one failure loses or replays successes | ack per row |
| [Ch 22](../chapters/22-the-event-spine.md) | Global ordering | "ordering is safer" | throughput collapsing to serial | partition by `run_id` (§5.2) |
| [Ch 22](../chapters/22-the-event-spine.md) | No dead letter | retry forever | a poison row consuming capacity | attempt cap, then `dead_at` |
| [Ch 22](../chapters/22-the-event-spine.md) | Non-idempotent consumer | assuming exactly-once | duplicated effects after a relay restart | at-least-once; dedup (§5.4) |
| [Ch 22](../chapters/22-the-event-spine.md) | Progress in the outbox | it looks like an event | table growth tracking viewer count | Chapter 7; progress is not a fact |
| [Ch 22](../chapters/22-the-event-spine.md) | Command with a return value | synchronous convenience | the runtime importing domain types | commands are refused via events |
| [Ch 22](../chapters/22-the-event-spine.md) | Outbox shed under load | treating it as telemetry | silent, permanent work loss | it is the last thing to degrade (§7.1) |
| [Ch 23](../chapters/23-the-scheduler.md) | Convoy | one FIFO for all durations | short-run latency tracking long-run arrivals | work classes — the cold open |
| [Ch 23](../chapters/23-the-scheduler.md) | One tenant occupies everything | no per-tenant cap | in-flight concentration by tenant | admission caps |
| [Ch 23](../chapters/23-the-scheduler.md) | Capacity as the fix | scaling out a structural problem | wait times halving, not resolving | §2.4 |
| [Ch 23](../chapters/23-the-scheduler.md) | One concurrency integer | web-server instinct | one resource saturated, others idle | three bounds (§5.4) |
| [Ch 23](../chapters/23-the-scheduler.md) | Priority instead of classes | ordering rather than reservation | low-priority starvation | reserved capacity (§5.3) |
| [Ch 23](../chapters/23-the-scheduler.md) | Reservation that yields | "idle workers are waste" | reservations failing exactly under load | it is a preference then (§4.1) |
| [Ch 23](../chapters/23-the-scheduler.md) | Accept and starve | no deferred state | runs "running" with no progress | visible deferral (§5.5) |
| [Ch 23](../chapters/23-the-scheduler.md) | Deferral modelled as a park | both hold nothing | the runbook cannot distinguish them | separate states (§5.6) |
| [Ch 23](../chapters/23-the-scheduler.md) | Claim before checking the semaphore | natural ordering | leases held by workers that cannot proceed | check first (E5) |
| [Ch 23](../chapters/23-the-scheduler.md) | Cached tenant counters | avoiding a count per submission | caps exceeded under burst | exact, in the admission txn (§7.2) |
| [Ch 23](../chapters/23-the-scheduler.md) | Reclassification mid-flight | "it turned out to be long" | latency unattributable to any class | class is fixed at entry |
| [Ch 24](../chapters/24-the-task-graph.md) | Worker dies holding a claimed node | — | Lease expiry (C17) | Sweeper returns node to `pending`; identity check (C21) prevents duplicate effect on re-run |
| [Ch 24](../chapters/24-the-task-graph.md) | Join tick committed separately from completion | — | None — this is the point | Not recoverable; prevented structurally by `complete()` being one transaction |
| [Ch 24](../chapters/24-the-task-graph.md) | Join `required` updated after first arrival | — | Assertion in the store; alert, not log | Reject the update; a join whose count changed mid-flight is unsound and the run must fail loudly |
| [Ch 24](../chapters/24-the-task-graph.md) | Cyclic graph proposed | — | Admission validator | Reject with the cycle path; planner replans (§5.5) |
| [Ch 24](../chapters/24-the-task-graph.md) | Graph exceeds width cap | — | Admission validator | Reject with the width and the cap; planner decomposes into sub-runs |
| [Ch 24](../chapters/24-the-task-graph.md) | Ready-set query slow | — | Query duration metric on the resolver | Almost always the missing `plan_edges (to_node)` index (§9) |
| [Ch 24](../chapters/24-the-task-graph.md) | Node stuck in `pending` with all predecessors terminal | — | Stall detector: oldest `pending` node age per run | Indicates an unsatisfied join; check `arrived` against `required` and the join's own status |
| [Ch 24](../chapters/24-the-task-graph.md) | All nodes terminal, run not complete | — | Same stall detector | An abandoned join with no propagation; the skip wave of §7.2 did not run |
| [Ch 25](../chapters/25-the-world-model.md) | Belief invalidated by the run's own effect, unnoticed | — | None at the time — this is §1.1 | Prevented structurally: the invalidator consumes the effect stream, not a timer |
| [Ch 25](../chapters/25-the-world-model.md) | Effect with undeterminable scope | — | Scope resolver returns `None` | Mark all beliefs suspect; alert on the rate, because a rising rate means tools are being added without scope declarations |
| [Ch 25](../chapters/25-the-world-model.md) | Probe regularly contradicted | — | `belief.contradicted` count per probe | Usually a probe in the wrong family (§4.2); move to point-lookup or mark `cacheable = False` |
| [Ch 25](../chapters/25-the-world-model.md) | Re-probe unaffordable at point of use | — | `belief.withheld` event | Run continues without the belief, slower; a persistent rate means the probe's cost and the step's budget are mismatched |
| [Ch 25](../chapters/25-the-world-model.md) | Belief store lost entirely | — | Cache miss rate | No recovery needed; re-probe on demand. If anything else breaks, §7.2's test was never run |
| [Ch 25](../chapters/25-the-world-model.md) | Two probes producing overlapping, disagreeing claims | — | Contradiction between beliefs, not against an observation | Delete one. Overlapping probes are a design error and reconciling them at read time is how a world model becomes a database |
| [Ch 25](../chapters/25-the-world-model.md) | Background refresher hiding staleness | — | Absence of `belief.withheld` events despite long sessions | Do not have a background refresher (§3) |
| [Ch 26](../chapters/26-planning-algorithms.md) | Replan with no new information | — | Classifier's guard (§5.5) | Refuse; fail the run with the reason. Never rate-limit instead |
| [Ch 26](../chapters/26-planning-algorithms.md) | Replan storm | — | Replans-per-lineage counter | Cap at a small number; the cap firing is an alert, not a log line |
| [Ch 26](../chapters/26-planning-algorithms.md) | Repair loop on one contract | — | `repairs_by_contract` | Escalate to replan after the first repair for a given contract fails |
| [Ch 26](../chapters/26-planning-algorithms.md) | Contract that cannot be evaluated | — | Contract attacher rejects at plan time | Decompose further (§5.2); a step with no checkable outcome is under-decomposed |
| [Ch 26](../chapters/26-planning-algorithms.md) | Contract weakened to pass | — | Contracts are immutable after mint (§7.2) | Structural; a mutable contract is the failure |
| [Ch 26](../chapters/26-planning-algorithms.md) | Plan built on a stale belief | — | None at plan time — this is Chapter 25 §1.1 | Prevented upstream: only fresh beliefs reach the planner |
| [Ch 26](../chapters/26-planning-algorithms.md) | Steps at wildly inconsistent granularity | — | Max-to-median cost estimate ratio (§5.1) | Decompose the outlier; the ratio names it precisely |
| [Ch 26](../chapters/26-planning-algorithms.md) | Search racing effectful branches | — | Admission validator, via Chapter 24 §5.3 | Rejected at mint; a `FIRST` join over effectful nodes never gets stored |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Tier-2 effect with no compensation registered | — | Registration-time check | Refuse to register the tool. This is the cold open, caught months earlier |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Effect ledger row committed apart from the completion | — | None at run time | Structural: `record` takes the open `Claim` (§8) |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Compensation fails and exhausts attempts | — | Attempt cap | Dead letter with the reversal named; run still reports failed |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Compensation succeeds on the wrong target | — | Usually nothing, until later | Bind `compensation_args` at apply time (§9) |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Attempt cap keyed by node id | — | Attempts-per-identity exceeding the cap across a lineage | Key by activity identity (§4.2) |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Dead letter aging unnoticed | — | Age of oldest row | Alert on age, not count. Owner is a team |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Lease TTL shortened for snappier recovery | — | Duplicate effects appearing after sweeps | TTL is a bound on in-flight effects, not a liveness knob (§4.1) |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Recovery budget unavailable because the run exhausted it | — | Compensation node refused at admission | Reserve compensation budget at admission (§5.2) |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Tier-3 effect reached without a gate | — | Post-hoc, from the ledger | Nothing to do after; audit `escaped` rows against gate records and treat a mismatch as a Chapter 30 defect |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Judge shown the run's reasoning | — | Code review; ideally impossible | Enforce by signature (§8), not by instruction |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Judge attempts to upgrade a failing floor | — | Combiner emits the event | Verdict is correct anyway; the rate is the signal (§4.3) |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Check implemented with a model call | — | Registration-time check on the contract | Reject; move the assessment to the judge (§4.1) |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Contract written after the work | — | Plan-time enforcement (Chapter 26) | Contracts are minted with the plan and immutable |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Golden set edited to make a run pass | — | Changelog review | The rule has no exceptions; add and retire, never edit (§5.2) |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Golden set contains only clean cases | — | Category distribution | Require `superficially_passing` cases; the cold open is one |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | `UNGRADABLE` counted as `FAIL` | — | Separate ranks | Keep them distinct; merging attributes grader outages to runs |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Verdict overwritten on re-grade | — | Append-only store | New grading event, both retained (§7.1) |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Evaluator-isomorphic checks agreeing for one reason | — | Disagreement rate of the non-isomorphic check | Keep at least one check written from the goal (§5.3) |
| [Ch 29](../chapters/29-long-running-agents.md) | Run oscillating between visited states | — | Novelty window (§5.1) | Escalate: observe, replan, park, terminate (§5.2) |
| [Ch 29](../chapters/29-long-running-agents.md) | Progress inferred from step count | — | Nothing — looks healthy | Structural: define progress as novel durable state |
| [Ch 29](../chapters/29-long-running-agents.md) | False stall during a long read phase | — | Stall rate on read-heavy phases | Window over effectful steps only (§5.3) |
| [Ch 29](../chapters/29-long-running-agents.md) | Budget spent early, nothing left to finish | — | Finish reserve engaged with work outstanding | Size the reserve from terminal node costs (§4.2) |
| [Ch 29](../chapters/29-long-running-agents.md) | Compensation unaffordable at failure | — | Chapter 27 §5.2 | Reserve at admission; unspendable by ordinary work |
| [Ch 29](../chapters/29-long-running-agents.md) | Timeouts fitted to benchmark task lengths | — | Invisible in that benchmark — this is the hazard | Derive from tool p99; express budgets relatively; put long tasks in the evaluation set (§5.4) |
| [Ch 29](../chapters/29-long-running-agents.md) | Run cannot survive a deploy | — | Failure rate correlated with deploy times | Chapter 21 in full; a six-hour window will contain a deploy |
| [Ch 29](../chapters/29-long-running-agents.md) | Parked run holding a worker | — | Worker utilisation with many parked runs | A park is a durable row and nothing else (§7.1) |
| [Ch 29](../chapters/29-long-running-agents.md) | Completion notification sent twice | — | Duplicate reports | Tier-3 effect with an identity key (Chapter 27) |
| [Ch 29](../chapters/29-long-running-agents.md) | Terminal record says "budget exceeded" | — | Unactionable postmortems | Report the axis (§4.1) |
| [Ch 30](../chapters/30-human-authority.md) | Rule enforced by the prompt | — | None — it works until it does not | Structural: the check is in the engine (§2.2) |
| [Ch 30](../chapters/30-human-authority.md) | Gate check bypassed by a second path to a tool | — | Effect ledger rows with no corresponding gate record | Audit `escaped` and gated-tier rows against decisions; a mismatch is a bypass, not an anomaly |
| [Ch 30](../chapters/30-human-authority.md) | Park holds a worker or lease | — | Worker utilisation under many parked runs | Park a thousand runs and measure; if anything moves, it holds something (§5.3) |
| [Ch 30](../chapters/30-human-authority.md) | Approval scoped to a tool rather than a call | — | Approval reused across differing arguments | Scope to `arg_hash`; approving one bucket is not approving another (§4.2) |
| [Ch 30](../chapters/30-human-authority.md) | Override recorded as a pass | — | Verdict history shows no failures where operators recall overriding | Verdict is immutable; the override is a separate row (§5.5) |
| [Ch 30](../chapters/30-human-authority.md) | Gate TTL treated as approval | — | Effects applied with no decision row | Expiry fails the run. Silence is never approval (§5.6) |
| [Ch 30](../chapters/30-human-authority.md) | Parks accumulating unresolved | — | Age of oldest pending gate request | Alert before expiry; a park about to expire is a decision nobody knows they owe |
| [Ch 30](../chapters/30-human-authority.md) | Policy failing open on a timeout | — | Absence of gate requests during a database incident | The policy is pure and has no I/O to time out (§4.1) |
| [Ch 30](../chapters/30-human-authority.md) | Notification sent twice by a retry | — | Duplicate pages | Tier-3 effect with an identity key (C27) |
| [Ch 30](../chapters/30-human-authority.md) | Human shown a model-generated summary | — | Review of the notification path | Render deterministically from the arguments (§9) |
| [Ch 30](../chapters/30-human-authority.md) | Steer approving a now-irrelevant call | — | Effects applied that the amended goal did not want | Arg-hash scoping abandons the old gate automatically (§6, branch A) |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Untrusted content read as instruction | — | None — assumed to happen | Bound the consequences (§2.3); do not attempt to prevent the reading |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Run-wide credential broader than any step needs | — | Scope audit: issued scopes versus declared needs | Per-step issuance from declared needs (§5.3) |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Tool whose tier depends on its arguments registered as one tool | — | Effect ledger showing one tool at multiple tiers | Split it. One registration per tier (§5.4) |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Summary of untrusted content treated as clean | — | `derived_from` chain audit | `derive` takes the minimum label (§3.1) |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Observation written without a provenance label | — | Query for null labels | Every one is an ingress path bypassing the tagger (§10) |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Sandbox reused between steps | — | Sandbox age or reuse count above one | Destroy and create fresh; warm pools hold fresh boxes (§4.1) |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | General internet egress from the sandbox | — | Absence of `egress.blocked` events over a long window | Allowlist with an empty default; mirror package installs internally (§5.5) |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Inline capability escalation added for convenience | — | Code review; the broker has no `widen` method | Structural (§8) |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Exfiltration | — | **Nothing.** No error, no failed step, no symptom | Egress policy is the only control; this is why its default must be closed |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Harness editing its own boundary | — | Not solved | §5.6, and Chapter 48 |
| [Ch 32](../chapters/32-distributed-execution.md) | Paused worker resumes and completes an effect | — | `fence.rejected` downstream, if a fence is carried | Fence token (§5.3); identity (C21) where no fence is possible; otherwise at-least-once, stated |
| [Ch 32](../chapters/32-distributed-execution.md) | Worker computes its own lease expiry | — | Code review; clock-skew incidents | `now()` evaluated in the store, in the claim statement (§4.1) |
| [Ch 32](../chapters/32-distributed-execution.md) | Claim decomposed into read-then-write | — | Duplicate claims under load | One statement, always (§4.1) |
| [Ch 32](../chapters/32-distributed-execution.md) | Renewal failure logged and retried | — | Duplicate effects after brief store outages | Renewal failure disarms effects immediately (§4.2) |
| [Ch 32](../chapters/32-distributed-execution.md) | Two claimers on one relay partition after a rebalance | — | Duplicate event delivery | Claim partitions through the store with lease and fence (§5.6) |
| [Ch 32](../chapters/32-distributed-execution.md) | Per-tenant limits enforced per process | — | Tenant using N times its share; convoy at unexpected load | Counters in the store (§5.6) |
| [Ch 32](../chapters/32-distributed-execution.md) | Ordering two events by wall-clock timestamps | — | Ordering anomalies during clock drift | Use the event-log sequence, never two clocks (§5.4) |
| [Ch 32](../chapters/32-distributed-execution.md) | Fence reset or run id reused | — | Silent: a stale request accepted as fresh | Bigint, monotonic forever, ids never reused (§7.2) |
| [Ch 32](../chapters/32-distributed-execution.md) | Lease TTL raised after an incident | — | The incident recurs, more rarely | TTL sets frequency, not window size (§5.5) |
| [Ch 32](../chapters/32-distributed-execution.md) | A system with a lease and nothing else | — | Nothing, until a pause | Name the layer that protects effects, or say at-least-once |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Pool sized from worker count | — | Connection refusals; `max_connections` exhausted | Size from measured hold time (§5.1). The cold open |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Connection held across a model call | — | Bimodal connection hold-time distribution | Check out per operation, not per step (§5.2) |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Sizing from measurements taken under saturation | — | Required capacity growing with provisioned capacity | Separate service time from queue time (§7.1) |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Adding workers to fix a saturated model semaphore | — | Throughput flat while worker count rises | Emit `binding_surface` (§4.2) |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Burst admitted without throttling | — | Step duration p95 climbing, then lease expiries | Admission against commitment (§3.1); the cliff in §6 |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Thundering resume after an outage | — | Second outage minutes after recovery begins | Rate-limit resumption through admission (§5.6) |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Model change without re-measurement | — | Every size derived from a stale distribution | `ServiceTime.model_id` mismatch (§9) |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | High-variance queue at high utilisation | — | Queue wait far worse than utilisation predicts | Latency classes (§5.4) — split the distribution, do not buy headroom |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Merged per-surface capacity state | — | Capacity discussions with no named cause | State per surface, never merged (§7.2) |
| [Ch 34](../chapters/34-observability.md) | Infrastructure healthy, work wrong | — | Signal 9 — verdict distribution | The cold open. Build this one first (§5.2) |
| [Ch 34](../chapters/34-observability.md) | Unbounded label in a metric | — | Metrics backend degradation | Allowlist at the call site (§4.2) |
| [Ch 34](../chapters/34-observability.md) | Uniform trace sampling | — | Detection fast, diagnosis slow (§6 branch) | Always-keep categories (§5.5) |
| [Ch 34](../chapters/34-observability.md) | Identity partial match | — | The detector — nothing else | Page. Four subsystems depend on it (§5.4) |
| [Ch 34](../chapters/34-observability.md) | Safety control quiet for months | — | Rate at zero over a long window | Synthetic probes that deliberately trigger it (§5.3) |
| [Ch 34](../chapters/34-observability.md) | Redaction applied at read | — | Raw material present on disk | Redact at capture; refuse to retain otherwise (§7) |
| [Ch 34](../chapters/34-observability.md) | Retention set by storage cost | — | Chapter 41 finds no usable history | Set it against evaluation needs, in writing (§3.1) |
| [Ch 34](../chapters/34-observability.md) | Always-keep trace dropped under pressure | — | Missing traces for known failures | Block or spill; never drop (§7.1) |
| [Ch 34](../chapters/34-observability.md) | Alerting built on error rate alone | — | Every Level 3 failure passes unnoticed | Alert on ages, absences, and distribution shifts (§5.3) |
| [Ch 34](../chapters/34-observability.md) | Metrics pipeline outage during an incident | — | Loss of visibility at the worst moment | Independent failure domains for the two pipelines |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Optimising cost per call | — | Bill rises while the optimised metric falls | Measure cost per successful outcome (§5.1). The cold open |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Retry multiplier omitted from the denominator | — | Any quality-for-cost trade looks good | Attempts per delivered outcome, from the same join |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | No reservation, only a spent counter | — | Budget exceeded under concurrency; every check was correct | `available = limit - spent - reserved` (§2.2 step 6) |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Orphaned reserves | — | Runs refused for budget while the ledger shows headroom | TTL on every reserve, swept like a lease (§5.3) |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Swept reserve recorded as zero | — | Month-end variance against the invoice | Record as `unknown`; reconcile (§7.1) |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Cache prefix broken by a context change | — | Bill rises ~30%; nothing else moves | Cache hit rate per step type (§5.4) |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Judge spend folded into run spend | — | Cannot answer what evaluation costs | Separate step type (§4.2) |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Repair spend undistinguished | — | Rising bill looks like longer runs for no reason | Tag repairs and replans (§4.2) |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Instruction tokens growing quarter over quarter | — | Instruction share of input | Encode behaviour in tools, not instructions (§5.2) |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Undifferentiated budget exhaustion | — | Investigations start with whoever is on call | Emit the sub-cause (§5.5) |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Availability promised, work sold | — | Churn, not dashboards | Add the honesty objective (§5.1). The cold open |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Quality promised with an error budget | — | Deploy freezes caused by provider changes | Publish quality; promise the three mechanical objectives |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Silent quality degradation under load | — | **Nothing.** No signal at all | Forbid rung 4; require disclosure and a per-run record (§5.3) |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Quality regression paged as an incident | — | On-call with no instrument and no action | Route to evaluation; page only via the honesty objective (§5.4) |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Honesty regression not paged | — | Customers acting on false successes | It is an incident. Audit disagreement rate is the trigger |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Remaining-balance alerting | — | Slow leaks and cliffs treated identically | Burn rate over multiple windows (§4.1) |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Uniform audit sampling | — | Honesty SLI too noisy to act on | Over-sample the suspicious populations (§4.2) |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Calendar-month budget windows | — | End-of-month gaming; incident severity depends on the date | Rolling windows (§7.2) |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Oscillation at a degradation threshold | — | Repeated pages, minutes apart | Hysteresis and minimum dwell time (§7.1) |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Merged service state | — | Cannot tell which promise broke, so cannot tell who responds | State per objective (§7) |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Trace store absent from the deletion path | — | Nothing, until someone searches it | Registry enumeration with reconciled counts (§4.1). The cold open |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Traces classified as telemetry | — | Retention set by storage cost; no owner | Classify by contents, not by the team that built it |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Cross-tenant memory read | — | **Nothing** — a filter returns empty | Tenant in the key; raise rather than filter (§5.2) |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Belief cache shared across tenants by commit | — | Nothing | `(tenant, repo, commit)` — one extra column (§5.2) |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Credential in a tool error message | — | Redactor pattern miss | Redact all captured material; CI test with a deliberate failure (§5.1) |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Redaction applied at read | — | Raw material on disk, in backups, in replicas | Capture-time only; a record written unredacted cannot be repaired (§7) |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Golden case derived from a customer's run | — | Deletion request has no route | Synthesise golden cases; record provenance (§5.5) |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Model tuned on trajectory data | — | No detector, no remedy | Decide before deriving; the transition is one-way (§7) |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Obligation-carrying ledger row deleted | — | The obligation becomes invisible | Refuse and escalate (§6, t=4) |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | New store added without registration | — | Impossible by construction | Persistence-layer enforcement, failing in development (§4.1) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Model changed with the harness tuned against the old one | — | Verdict distribution (C34 signal 9) | The invalidation register, checked before promotion (§5.2). The cold open |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Alias instead of an exact pin | — | Regressions with an empty change log | Pin exactly; treat alias drift as incident-grade (§4.1) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Config read mid-run | — | Behaviour changing inside one run with no trace evidence | Resolve once, freeze, small explicit live set (§4.2) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | File hash instead of resolved hash | — | Two runs "identical" behaving differently | Hash the resolved values (§3.1) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Smoke test substituted for evaluation | — | Nothing — it passes | A smoke test cannot see a 13-point regression (C41 §5.1) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Rollback target withdrawn | — | The date, known from day 0 | Deprecation clock as a scheduling input (§5.4) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Retired triple no longer deployable | — | Discovered on the day it is needed | Exercise rollback on a schedule (§7.1) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Model-conditional workaround unmarked | — | Archaeology during an incident | One comment line at the time (§5.1) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Triple not recorded on runs | — | Every C41 comparison is between unknowns | Four fields on the run record (§3.1) |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Withdrawal date unknown | — | A clock you cannot see | Treat as a stale register entry (§10) |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Harness files bypass the pipeline | — | Nothing, until a regression is noticed weeks later | Same repo, same pipeline; remove the hot-reload path (§7.1). The cold open |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Regression in a slice, diluted in the aggregate | — | Per-slice verdict graphs (§6) | Graph and gate per slice, never only overall |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Gate 2 skipped for a "small" change | — | Nothing | Diff size does not bound blast radius (§7) |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Benchmark trimmed to fit the pipeline | — | It starts passing everything | Protect its size; let promotion be slow (§5.2) |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Blast-radius linter narrowed | — | Regressions in un-run slices | Non-negotiable output (§4.1) |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Review treated as the control | — | A reviewer cannot see absent task types | Empirical gate is primary; review catches what it does not cover (§5.5) |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Revert assumed to undo the damage | — | Effects already shipped | Query runs by harness hash and review them (§5.4) |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Retired harness no longer resolves | — | Discovered on the day it is needed | Exercise revert on a schedule (§7.2) |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Instructions accreting for years | — | Instruction share of input tokens (C35 §13.1) | Removal experiments, one evaluation run each (§5.6) |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | Model calls inside gate 1 | — | Gate 1 taking longer than minutes, and flaking | Deterministic checks only (§4.2) |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Flaky test retried | — | The suite stays green while a bug ships | Lint rule forbidding retries in tiers 1 and 2 (§5.4). The cold open |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Statistical question in CI | — | It flakes, then it is retried | Move it to Chapter 41; it is a measurement, not a test |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Mock instead of replay | — | Bugs concentrated in shapes the mock cannot produce | Replay from the trace store (§5.2) |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Real clock in tests | — | Slow tests, then shortened intervals | Inject the clock; `advance()` explicitly (§4.2) |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Shortened lease TTL "for tests" | — | Tests pass against a configuration not deployed | Controlled clock removes the reason (§6) |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Divergence reported as failure | — | The tier is silenced within a quarter | A distinct third outcome (§5.3) |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Fixtures stale after a model change | — | Divergence wave on migration day | Version fixtures with the triple; refresh in the ladder (§7.1) |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Assertions on generated content | — | Breakage on every model version, then a retry | Assert structure only (§5.5) |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Shared state between tests | — | The commonest flake, misdiagnosed as non-determinism | Fresh store and fresh fakes per test (§7.2) |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Chaos treated as an occasional exercise | — | Silent-failure properties untested | Seeded injection in CI (§5.6) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Decisions made without a floor | — | Nothing, until someone runs the benchmark twice | Measure the floor first (§5.1). The cold open |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Per-slice results over-read | — | Small slices with wide floors | Report the floor beside every number, at every grain (§4.1) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Floor stale after a model change | — | Register entry (C38) | Invalidate on model or corpus change; refuse to report (§7.2) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Single rollout per task | — | Score is a sum of coin flips | k rollouts, `pass@1` averaged (§5.2) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Unpaired comparison | — | Wider floor than necessary, at the same cost | Pair by default (§5.1) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Benchmark task edited | — | Every historical comparison silently invalid | Retire and replace (§5.5) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Corpus drift | — | Slice distribution against traffic, quarterly | Add tasks, never reweight (§5.6) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Score without cost | — | A change that spends triple for two points passes | Cost per success in the report (§5.7) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Grader error term omitted | — | A measurement missing one of its two error sources | Attach the honesty rate (§3.1) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Ceiling or floor tasks retained | — | Cost with no information | Retire them (§7) |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Evaluation starved or starving production | — | Promotion gates taking days, or production latency | Its own work class, reserved and preemptible (§4.2) |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | Fitting assumed cumulative | — | Nothing; the score rises and the reason is not asked | Measure carried advantage against an old version (§5.1) |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | A model change treated as an upgrade | — | The score drops with no error | Chapter 38's register; the fit transitions automatically (§7.1) |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | Score drop attributed to the model | — | Unfalsifiable, so it survives | The counterfactual run; one paired benchmark (§6.2) |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | Re-fit slips past a withdrawal date | — | Days-to-withdrawal, if anyone tracks it (C38 §5.4) | Start at twice the expected duration; record `{{ abandoned }}` |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | Re-fit effort estimated from steps 3 and 4 | — | Estimates that are wrong by a factor of four | Ledger the days as they happen (§5.3) |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | People added to shorten step 2 | — | Colliding edits, unattributable gains | The synthesis does not divide (§4.2) |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | Loop built before the instrument | — | A rising score on its own instrument | The readiness gate; the floor is blocking (§5.6) |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | Loop expected to compound | — | Iteration six flattens and the project is called failed | Gains do not stack `[AHE §4.4.1]`; pace-keeping, not optimisation |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | Model-coupled edits unlabelled | — | Eleven days of archaeology per migration | One-line provenance comment at the time (C38 §5.1) |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | Standing advantage never measured | — | The whole activity is unjustified and nobody notices | Run the seed on today's model once a year (§8) |
| [Ch 43](../chapters/43-component-observability.md) | Two components own one behaviour | — | Nothing, until an edit to one measures zero | Declared tags at build time; probes for the rest (§5.3). The cold open |
| [Ch 43](../chapters/43-component-observability.md) | A file at a mount point nothing loads | — | Loader-versus-filesystem reconciliation | Fail the build, never warn (§4.1) |
| [Ch 43](../chapters/43-component-observability.md) | A registered component with no file | — | Same reconciliation, other direction | Fail the build (§8) |
| [Ch 43](../chapters/43-component-observability.md) | Behaviour living in application code | — | An edit that cannot be addressed at all | Move it into the workspace, or accept it is not editable |
| [Ch 43](../chapters/43-component-observability.md) | Unowned failures routed to the prompt | — | The distribution of `constraint_level` (§5.4) | Escalate a level on the second attempt, never reword |
| [Ch 43](../chapters/43-component-observability.md) | The same level edited three times | — | The manifest's own history | E3 of Figure 43.7; the level is wrong, not the wording |
| [Ch 43](../chapters/43-component-observability.md) | Seed replaced with the production harness | — | Nothing; every number still looks like a number | The seed is the origin, not a starting position (§5.6) |
| [Ch 43](../chapters/43-component-observability.md) | Seed drifts or stops resolving | — | Re-run it on a schedule (§5.7) | Tag it; treat drift as an incident |
| [Ch 43](../chapters/43-component-observability.md) | All seven types are text | — | The constraint-level field is constant | Enforcement levels must actually differ (§3.1) |
| [Ch 43](../chapters/43-component-observability.md) | A probe result read as "dead" | — | It is equally "compensated" | Probe the suspected compensator too (§9) |
| [Ch 43](../chapters/43-component-observability.md) | Components accumulate, none retired | — | Inventory age; nothing touched in twenty iterations | Removal experiments at component grain (§4.2) |
| [Ch 44](../chapters/44-experience-observability.md) | A routing field is not emitted | — | Nothing; the analyses are well-formed and describe the wrong cause | Undroppable set as a schema that blocks (§5.3). The cold open |
| [Ch 44](../chapters/44-experience-observability.md) | Analyses summarise what the model did, not what it saw | — | Rising share of default-owner routing (C43 §5.4) | Context accounting is the first field, not an optional one |
| [Ch 44](../chapters/44-experience-observability.md) | Grouping by prose similarity | — | Clusters that track phrasing rather than cause | Group by field value (§4.2) |
| [Ch 44](../chapters/44-experience-observability.md) | No clean-success contrast | — | Workload properties named as causes | A nonzero success sample (§4.1, C34 §5.5) |
| [Ch 44](../chapters/44-experience-observability.md) | Distilling before attributing | — | The loop diagnoses its own damage | Required argument, not a comment (§8) |
| [Ch 44](../chapters/44-experience-observability.md) | Stale corpus read as current | — | None; it reads correctly | Stamp the harness version; refuse on mismatch (§7.1) |
| [Ch 44](../chapters/44-experience-observability.md) | Corpus budgeted to a fixed token count | — | The long tail of one-off failures silently drops | Budget the overview; let analyses scale (§5.1) |
| [Ch 44](../chapters/44-experience-observability.md) | Pointers that do not resolve | — | Discovered when someone follows one | Trace id, span id, byte range — never prose (§9) |
| [Ch 44](../chapters/44-experience-observability.md) | Verbatim pulled by default | — | Cost, and a wide standing exposure surface | Structural first; verbatim per field (§5.6) |
| [Ch 44](../chapters/44-experience-observability.md) | Superseded corpora deleted | — | Disappearance becomes unmeasurable | Keep them; they are small and structural (§7.2) |
| [Ch 44](../chapters/44-experience-observability.md) | Sub-agent failures summarised twice | — | Routing runs on second-hand evidence | Distil sub-agent runs as first-class tasks (§5.7) — partial |
| [Ch 45](../chapters/45-decision-observability.md) | Predictions name categories, not ids | — | Nothing; precision rises and looks like progress | Sharpness check refuses; width stored at sealing (§5.3). The cold open |
| [Ch 45](../chapters/45-decision-observability.md) | Precision reported without width | — | Same number for hedging and for aiming | One structure carrying both; no method returns precision alone (§8) |
| [Ch 45](../chapters/45-decision-observability.md) | Root cause restates the fix | — | The entry reads reasonably forever | Near-duplicate check; a cause must state a mechanism (§5.2) |
| [Ch 45](../chapters/45-decision-observability.md) | Empty at-risk treated as an absence | — | The loop's known weakness becomes a blank field | Score the null claim; track its miss rate (§5.4) |
| [Ch 45](../chapters/45-decision-observability.md) | Proposal storm | — | Iterations spent, no new evidence consumed | Refuse when every pointer was cited before (§5.1) |
| [Ch 45](../chapters/45-decision-observability.md) | An entry revised after the result | — | None — a revised row and an accurate one are identical | No update method; hash chain; seal bound to a pending run (§5.6) |
| [Ch 45](../chapters/45-decision-observability.md) | Sealing bound to a timestamp | — | The clock is written by the audited party | Bind to a benchmark run id (§7.2) |
| [Ch 45](../chapters/45-decision-observability.md) | Predicted set widened at scoring | — | The claim becomes true retroactively | Width recorded at sealing (§4.2) |
| [Ch 45](../chapters/45-decision-observability.md) | Superseded entries deleted | — | Every ledger trend loses its history | Mark, never remove (§7.1) |
| [Ch 45](../chapters/45-decision-observability.md) | Gate needs judgment | — | A judge the loop can influence | Every check mechanical (§4.1) |
| [Ch 45](../chapters/45-decision-observability.md) | Refusals returned as bare rejections | — | The loop redrafts cosmetically | Refusals are an interface under C15's rules (§6.1) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | A constraint relaxed because it binds | — | Production, later, on a surface the benchmark does not measure | The §5.7 procedure; make the property representable first. The cold open |
| [Ch 46](../chapters/46-the-evolve-agent.md) | Router returns only in-scope classes | — | Displacement becomes invisible; the loop looks unimaginative | Return the true class and refuse (§4.1) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | Diff not checked separately from the entry | — | The manifest records the wrong component, permanently | Scope check against changed paths, last (§3.1) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | Rewording at one level repeatedly | — | The `(pattern, level)` counter (C45 §5.5) | Escalate on the second attempt; refuse on the third (§5.5) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | Three of the verifier's four parts protected | — | The unprotected one is edited and the score rises | All four: golden set, checks, judge config, combiner (§5.2) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | Containment list stored beside the workspace | — | It becomes editable in a refactor | Store it with the verifier (§7.2) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | An entry whose `reward_would` is blank | — | Nothing; it reads like the others | Refuse the entry until the column is filled (§9) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | Contested count reset on relaxation | — | A later reader cannot tell considered from expedient | Keep the count across relaxations (§7.1) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | Relaxation made during an iteration | — | Reasoning at its worst, change at its least visible | Never as an emergency change (§5.7 step 5) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | Seed deleted or improved | — | Nothing that runs breaks | Non-deletable rule; the seed is the measurement origin (§5.1) |
| [Ch 46](../chapters/46-the-evolve-agent.md) | The list assumed complete | — | No detector exists, by construction | Treat it as a lower bound; deny by default (§5.3) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Two edits predict overlapping tasks | — | Disjointness check, if it exists | Check at sealing; ship them in different iterations (§4.2). The cold open |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | An edit credited for another's effect | — | Mechanism check against the next corpus | Both corpora into attribution (§5.2) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Inside-floor movement scored as KEEP | — | Nothing; it looks like a small win | UNDETERMINED; inside the floor is no measurement (§4.1). C41 §5.7's loop bug |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | UNDETERMINED implemented as a soft rollback | — | Good edits disappearing at a steady rate | Reverting on no evidence is as unjustified as keeping (§6.1) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Automatic rollback on a flaky runtime | — | Reverts correlate with nothing in particular | C40's tiers 1 and 2 first; a stable runtime is a precondition (§5.5) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Attribution against a stale floor | — | The floor's age, if it is recorded | Raise, do not warn (§5.5) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Distillation before attribution | — | Corpus growing while the score is flat | The required argument (§10, C44 §8) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Reverted entries or commits pruned | — | The loop re-proposes a refuted hypothesis | Mark, never delete (§7.1) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Trials with tier-2 effects | — | Discovered when a revert does not undo something | Confine trials to tier-1 effects (§5.6, C31) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Collision set not recorded | — | A verdict cannot be re-examined later | Store it with the verdict; it is empty most of the time (§7.2) |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Surprise regressions not tracked | — | The at-risk weakness stays a citation | First-class field (§9) |
| [Ch 48](../chapters/48-limits.md) | A roadmap built on summed single-component gains | — | The quarter's delivery, a third short | Discount by roughly a third; treat the sum as an upper bound (§5.1) |
| [Ch 48](../chapters/48-limits.md) | A slice traded away in sub-floor steps | — | Cumulative per-slice against the seed — and nothing else | Per-slice gate, cumulative, not per-iteration (§5.3, §6.1). The cold open |
| [Ch 48](../chapters/48-limits.md) | Shipping on the aggregate | — | The customer, six weeks later | The worst slice is the headline (§5.3) |
| [Ch 48](../chapters/48-limits.md) | Flattening read as underperformance | — | Constraints relaxed, claims widened, edits per iteration raised | Name the state, with an expected iteration count (§7.1) |
| [Ch 48](../chapters/48-limits.md) | Exhausted read as optimal | — | The benchmark stops producing patterns | Add tasks, not iterations (§7.2) |
| [Ch 48](../chapters/48-limits.md) | Undetermined edits accumulating | — | Resident component count rising with no attributed gains | Removal experiments on the residue (§5.7) |
| [Ch 48](../chapters/48-limits.md) | Indirect boundary erosion | — | Nothing; every edit was permitted and measured positive | Per-slice gating, the mechanism check, and human review (§5.6) |
| [Ch 48](../chapters/48-limits.md) | A containment entry that should exist and does not | — | Nothing, in principle | Deny by default (§5.5) |
| [Ch 48](../chapters/48-limits.md) | Interference mistaken for overlap | — | A component removed because it "did nothing" | Probe distinguishes them; interference is not a defect (§4.1) |
| [Ch 48](../chapters/48-limits.md) | Single-component numbers reused after the harness changed | — | Predictions that were right once | Mechanism shift: a single measured against the seed is a fact about the seed (§5.2) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | The review watches the score | — | Nothing; the score is healthy | A fixed scan of eleven numbers, computed in advance (§5.1). The cold open |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | An agenda item nobody can justify | — | It has never been out of band | Annual removal review of the scan itself (§4.1) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Per-edit approval added | — | Its refusal rate is zero | Measure every gate's refusal rate; delete the ones at zero (§5.2) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Constraints relaxed between meetings | — | The commit, if anyone looks | Gate 2, a named owner outside the reporting line (§5.2) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Relaxation during an iteration | — | `made_during_iteration` | Never as an emergency change (§5.7 of Ch 46, §9 here) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Automated reader with inherited access | — | A customer's question, eleven days later | Read audit including machine readers; structural by default (§5.3) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Cleanup deferred indefinitely | — | Resident component count rising | Standing allocation, not a campaign (§4.2, §5.4) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | The fallback capability decays | — | Nothing until the loop is turned off | Named as unsolved (§2.1, §13.3) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Autonomy promoted on judgment | — | It is never descended | Measured conditions, automatic demotion (§7.1) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Autonomy retained across a model change | — | The evidence was measured on a different model | The deployment event resets the conditions (§7.2) |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Corpus or weighting chosen for what it shows | — | Nothing; every number is correct | Gate them, with a recorded rationale (§5.5) |
