# Documentation Index

This repository combines three complementary sources: a teaching-oriented handbook, a detailed runtime architecture specification, and research on automatically evolving coding-agent harnesses.

## Choose a reading path

### Learn the system from first principles

Read the [handbook](handbook/README.md) in chapter order. Chapters 0-3 establish the foundations; Chapters 4-9 introduce the runtime layers, execution nouns, state ownership, client boundary, lifecycles, and the three flows; Level 2 opens the components, starting with the planner.

### Design or review a runtime

Start with the [complete runtime diagram](assets/diagrams/complete-agent-runtime.svg), then use the [Universal Runtime v1.0 architecture specification](architecture/universal-runtime-v1.0-architecture-specification.md) for execution graphs, contracts, manifests, ports, policy, state, events, distribution, and diagnostics.

### Build a self-evolving harness

Read the [Agentic Harness Engineering paper](research/agentic-harness-engineering-paper.pdf), then Chapter 1 and the [AHE closed-loop diagram](assets/diagrams/agentic-harness-engineering-loop.svg). Together they cover component, experience, and decision observability.

### Read the compiled edition

Use the [compiled handbook](handbook/compiled/next-generation-autonomous-ai-agent-architecture-handbook.docx) for a single Word document — the v1.0 reading edition, containing the front matter, all fifty chapters in reading order, both interludes, and all ten appendices.

## Artifact map

| Area | Purpose | Current state |
| --- | --- | --- |
| [Handbook chapters](handbook/chapters/) | Progressive explanation and production guidance | All 50 chapters (0-49) available; Levels 0-5 complete |
| [Authoring conventions](handbook/CONVENTIONS.md) | Chapter skeleton, on-ramp blocks, diagram and naming rules, definition of done | Current; enforced by the linter |
| [Front matter](handbook/front-matter/) | The four reading tracks, the notation card, the reference system, and the scope limits | F.1-F.4 complete |
| [Appendices](handbook/appendices/) | Glossary, naming, diagrams, schema, ports, invariants, failure modes, anti-patterns, sources, and the dependency spine | All ten written; A, D, E, G, H, I, J generated from the chapters |
| [Level openers](handbook/levels/) | What each level teaches, what it assumes, and its exit condition | Levels 0-5 available |
| [Handbook blueprints](handbook/blueprints/) | Planned 50-chapter structure, dependency graph, conventions, roadmaps, and the completion plan | Phase 3 is the execution plan |
| [Architecture specification](architecture/universal-runtime-v1.0-architecture-specification.md) | Detailed runtime system design and contracts | v1.0 specification |
| [Research paper](research/agentic-harness-engineering-paper.pdf) | Evidence and method for observability-driven harness evolution | arXiv v4, 18 May 2026 |
| [Diagrams](assets/diagrams/README.md) | Reusable visual summaries | Six SVG figures |

## Provenance legend

The handbook uses compact tags to keep evidence and original synthesis separate:

| Tag | Meaning |
| --- | --- |
| `[AHE]` | Agentic Harness Engineering research paper |
| `[DAR]` | Durable/universal runtime architecture specification |
| `[INF]` | Engineering inference introduced by the handbook |
| `[BP]` | Industry best practice |
| `[FUT]` | Future or speculative proposal |

The distinction matters: architecture requirements, empirical findings, engineering judgment, and future ideas should not be presented as the same kind of claim.
