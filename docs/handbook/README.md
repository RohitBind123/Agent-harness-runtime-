# Autonomous Agent Architecture Handbook

The handbook teaches the architecture in dependency order. It uses a running reference system named Atlas on an agent runtime named ARK, and applies a consistent sixteen-section chapter template covering motivation, mental models, architecture, state, interfaces, communication, failure modes, scale, and production engineering.

Every chapter is written to be followable by an engineer new to both AI systems and distributed systems: each opens with a plain-language summary and a concrete analogy with its breaking point stated, derives its subject from first principles, and closes with a glossary of the terms it introduced. The rules are in [CONVENTIONS.md](CONVENTIONS.md) and are enforced by `tools/check_handbook.py`.

## Levels

| Level | Opener | Chapters |
| --- | --- | --- |
| 0 — Foundations | [Level 0](levels/level-0-foundations.md) | 0-3 |
| 1 — High-Level Runtime Architecture | [Level 1](levels/level-1-high-level-runtime.md) | 4-9 |
| 2 — Core Runtime Components | [Level 2](levels/level-2-core-components.md) | 10-20 |
| 3 — Advanced Runtime Architecture | [Level 3](levels/level-3-advanced-runtime.md) | 21-32 |

## Available chapters

| Chapter | Level | Focus |
| --- | --- | --- |
| [0. Evolution of AI Systems](chapters/00-evolution-of-ai-systems.md) | Foundations | The progression from completions to tools, loops, autonomy, multi-agent systems, and self-evolution |
| [1. Anatomy of an Agent](chapters/01-anatomy-of-an-agent.md) | Foundations | Model, harness, environment, and the seven editable harness component types |
| [2. Why an Agent Runtime Is a Distributed System](chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Foundations | Durability, expensive non-determinism, external effects, and interruptibility |
| [3. Mental Models and the Reference System](chapters/03-mental-models-and-reference-system.md) | Foundations | Five reasoning lenses and the Atlas/ARK reference system |
| [4. The Complete Runtime](chapters/04-complete-runtime-layers-and-process-topology.md) | High-level runtime | Six layers, two process types, the narrow waist, and the three flows |
| [5. The Five Nouns](chapters/05-five-nouns.md) | High-level runtime | Run, Episode, Step, Activity, Park, and the custody gradient |
| [6. State Separation](chapters/06-state-separation.md) | High-level runtime | Domain, run, model, and harness state ownership |
| [7. The Edge and the Client Contract](chapters/07-edge-and-client-contract.md) | High-level runtime | Stateless ingress, read models, reconnect behavior, and human authority |
| [8. Request Lifecycle and Runtime Lifecycle](chapters/08-request-and-runtime-lifecycles.md) | High-level runtime | Two independent clocks, claim and release, drain, and why recovery must be continuous |
| [9. Three Flows: Data, Control, Event](chapters/09-three-flows-data-control-event.md) | High-level runtime | One runtime read three ways, and routing a question to the axis that answers it |
| [10. The Planner](chapters/10-the-planner.md) | Core components | Plan identity, why a replan mints a new plan, and the validator that rejects rather than repairs |
| [11. The Context System](chapters/11-the-context-system.md) | Core components | Context as a budgeted, cache-keyed resource: assembly order, deferral, compaction, and the junk drawer |
| [12. The Memory System](chapters/12-the-memory-system.md) | Core components | Four subsystems behind one word, and why the only component a run writes to itself needs evidence and decay |
| [13. The Reasoning Engine](chapters/13-the-reasoning-engine.md) | Core components | One metered, capped, abortable door to the model, and why stopping waiting is not stopping spending |
| [14. The Tool Execution Engine](chapters/14-the-tool-execution-engine.md) | Core components | Description and implementation as two surfaces, the effect tag as the safety model, and truncation at the boundary |
| [15. Agent-Computer Interface Design](chapters/15-agent-computer-interface-design.md) | Core components | Verbs, arguments, results, and errors as a designed surface, and why errors are instructions rather than diagnoses |
| [16. The Observation System](chapters/16-the-observation-system.md) | Core components | Capturing what the model could see, redaction at capture, and outcome-weighted retention |
| [17. The State Manager](chapters/17-the-state-manager.md) | Core components | Ownership as a value rather than a lock: lease, version CAS, and recovery as one indexed query |
| [18. The Runtime Loop](chapters/18-the-runtime-loop.md) | Core components | The keystone: bounded episodes, four exit conditions, and nothing scarce held across a model call |
| [19. The Multi-Agent Runtime](chapters/19-the-multi-agent-runtime.md) | Core components | Sub-agents as context boundaries rather than job titles, and when a tool is strictly better |
| [20. The Self-Evolving Runtime (AHE) — Overview](chapters/20-the-self-evolving-runtime-overview.md) | Core components | The closed loop in one chapter: three pillars, the change manifest, and the containment boundary |
| [21. Durable Execution](chapters/21-durable-execution.md) | Advanced runtime | Resume, re-run, and replay as three operations, and the record window that does not close |
| [22. The Event Spine](chapters/22-the-event-spine.md) | Advanced runtime | The outbox as the only durability primitive, and why a cursor is an outage waiting for a bad row |
| [23. The Scheduler](chapters/23-the-scheduler.md) | Advanced runtime | Convoy effects, work classes with reserved capacity, and three resources that need three bounds |
| [24. The Task Graph](chapters/24-the-task-graph.md) | Advanced runtime | Separating dependency from sequence, and why fan-in is a durable counter rather than a feature |
| [25. The World Model](chapters/25-the-world-model.md) | Advanced runtime | Beliefs about the environment, and the run's own effects as the dominant source of staleness |
| [26. Planning Algorithms](chapters/26-planning-algorithms.md) | Advanced runtime | Retry, repair, and replan at 1x, 3x, and 30x, and contracts written before the work |
| [27. Failure, Recovery, and Rollback](chapters/27-failure-recovery-and-rollback.md) | Advanced runtime | Three tiers of reversibility, the effect ledger, and compensation as a real node |
| [28. Reflection, Grading, and Self-Correction](chapters/28-reflection-grading-and-self-correction.md) | Advanced runtime | The verdict lattice: a floor set by checks that a model judgment may lower and never raise |
| [29. Long-Running Agents](chapters/29-long-running-agents.md) | Advanced runtime | Progress as novel durable state, budget allocation over six hours, and timeout coupling |
| [30. Human Authority](chapters/30-human-authority.md) | Advanced runtime | The gate as a park holding nothing, and steering as the same mechanism as crash recovery |
| [31. Safety, Sandboxing, and Untrusted Content](chapters/31-safety-sandboxing-and-untrusted-content.md) | Advanced runtime | Capability that cannot read content, and blast radius as four bounds written down |
| [32. Distributed Execution](chapters/32-distributed-execution.md) | Advanced runtime | What a lease actually guarantees, fence tokens, and exactly-one-driver as an operational property |
| [33. Scalability and Capacity Planning](chapters/33-scalability-and-capacity-planning.md) | Production engineering | Little's Law per surface, and an outage caused by correctly applying the standard pool formula |
| [34. Observability](chapters/34-observability.md) | Production engineering | Two observability systems for two questions, eleven signals, and alerting on absence |
| [35. Cost Engineering and Token Economics](chapters/35-cost-engineering-and-token-economics.md) | Production engineering | Cost per successful outcome, reserve-then-settle, and why input dominates output twenty to one |
| [36. Reliability and SLOs](chapters/36-reliability-and-slos.md) | Production engineering | Promise liveness, honesty, and accounting; publish quality; never degrade it silently |
| [37. Tenancy, Secrets, and Data Governance](chapters/37-tenancy-secrets-and-data-governance.md) | Production engineering | Nine stores, two cross-run by design, and the derivation boundary that is one-way |

## Completion status

| Level | Planned chapters | Available | Status |
| --- | ---: | ---: | --- |
| 0 — Foundations | 0-3 | 4 of 4 | Complete |
| 1 — High-Level Runtime Architecture | 4-9 | 6 of 6 | Complete |
| 2 — Core Runtime Components | 10-20 | 11 of 11 | Complete |
| 3 — Advanced Runtime Architecture | 21-32 | 12 of 12 | Complete |
| 4 — Production Engineering | 33-41 | 5 of 9 | In progress |
| 5 — Self-Evolving Systems | 42-49 | 0 of 8 | Planned |

Levels 0-3 are complete. Level 4 is in progress; Chapter 38, *Deployment, Versioning, and Configuration*, is next in sequence. The batch schedule is in the [Phase 3 completion plan](blueprints/phase-3-completion-plan.md) §5.

## Reference material

- [CONVENTIONS.md](CONVENTIONS.md) — the authoring card: chapter skeleton, the four on-ramp blocks, diagram vocabulary, provenance rules, naming, prohibited words, and the definition of done.
- [Appendix A — Glossary](appendices/a-glossary.md) — every term the handbook defines, generated from the chapters.
- [Interlude I — Assembling a Minimal Runtime](interludes/interlude-1-assembling-a-minimal-runtime.md) — a narrative build of stages 0-2, after Chapter 20.

## Blueprints

- [Phase 1 — Structural Blueprint](blueprints/phase-1-structural-blueprint.md) defines the original book structure, glossary, diagram conventions, naming conventions, and decision log.
- [Phase 2 — Revised Blueprint](blueprints/phase-2-revised-blueprint-v2.md) updates the table of contents, numbering, dependency spine, and roadmaps. It supersedes Phase 1 only where the document explicitly says so.
- [Phase 3 — Completion Plan](blueprints/phase-3-completion-plan.md) is the execution plan for the remaining 42 chapters: scope, the newcomer on-ramp, the production template, batch schedule, and per-chapter briefs.

## Tooling

Run from the repository root:

```bash
python3 tools/check_handbook.py     # convention linter; must exit zero
python3 tools/build_glossary.py     # regenerate Appendix A from the chapters
```

The linter checks figure counts against the declared tier, diagram width and ASCII purity, section structure, on-ramp blocks, header and dependency-spine consistency, prohibited words, provenance tags, cross-reference validity, and the chapter hand-off.

## Compiled edition

The [compiled Word handbook](compiled/next-generation-autonomous-ai-agent-architecture-handbook.docx) is a version 0.8 reading edition containing the Phase 1 and Phase 2 blueprints plus Chapters 0-7. For editable content and reviewable diffs, treat the Markdown files as canonical.
