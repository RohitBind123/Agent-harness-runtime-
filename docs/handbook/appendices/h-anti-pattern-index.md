# Appendix H — Anti-Pattern Index

> **Generated file. Do not edit by hand.**
>
> Assembled from the chapters by `tools/build_appendices.py`. To change an
> entry, edit the chapter it comes from and regenerate.

**Semi-generated, and the only appendix that is.** An anti-pattern is named in prose rather than in a structured block, so this is a mechanical sweep for every place the book names one, plus the explicit tables a few chapters carry. It is a curated index over a complete sweep rather than a hand-maintained list, which is the trade that keeps it true as chapters are added.

---

## Named in a table

Chapters 0 through 2 close with an explicit anti-pattern table, which is where the book's named failures were first collected.

| Anti-pattern | Why it fails | Fixed in | Named in |
|---|---|---|---|
| **The G2-in-production** | Shipping an in-process loop inside an HTTP handler and discovering durability at the first deploy | Ch 4, Ch 21 | [Ch 0](../chapters/00-evolution-of-ai-systems.md) |
| **Generation cargo-culting** | Adopting sub-agents or an evolution loop before the runtime beneath them is measurable | Ch 19, Ch 42 | [Ch 0](../chapters/00-evolution-of-ai-systems.md) |
| **Capability substitution** | Answering a systems failure with a better prompt. The cold open cannot be fixed with words | Ch 30, Ch 15 | [Ch 0](../chapters/00-evolution-of-ai-systems.md) |
| **Timeout as cancellation** | Abandoning the caller's wait while the operation continues, leaking resources and landing side effects after everyone gave up `[DAR §5.5]` | Ch 30 | [Ch 0](../chapters/00-evolution-of-ai-systems.md) |
| **Self-graded success** | Letting the system decide whether it succeeded using a check it invented | Ch 28 | [Ch 0](../chapters/00-evolution-of-ai-systems.md) |
| **Prompt as the only surface** | The weakest enforcement level, paid for on every call | §11.1, Ch 11 | [Ch 1](../chapters/01-anatomy-of-an-agent.md) |
| **The tangled harness** | Components that cannot be edited independently cannot be attributed independently | Ch 43 | [Ch 1](../chapters/01-anatomy-of-an-agent.md) |
| **Unversioned harness** | The cold open; a model upgrade silently invalidates a fit | Ch 38 | [Ch 1](../chapters/01-anatomy-of-an-agent.md) |
| **Component hoarding** | Adding components without removing them; interference accumulates invisibly | Ch 48 | [Ch 1](../chapters/01-anatomy-of-an-agent.md) |
| **Editing the wrong region** | Attempting to fix a harness problem by changing sampling parameters, or an environment problem by changing the prompt | Ch 31, Ch 46 | [Ch 1](../chapters/01-anatomy-of-an-agent.md) |
| **Standard retry policy** | Multiplies cost and re-rolls output; the cold open | Ch 21 | [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) |
| **Timeout as cancellation** | Leaks the operation and lets its effects land after everyone gave up | Ch 30 | [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) |
| **Connection held across a model call** | Converts pool scarcity into system-wide latency coupling | Ch 23 | [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) |
| **Authority in the prompt** | A hope with good compliance statistics | Ch 30 | [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) |
| **Boot-only recovery** | A long-lived worker that sweeps at start never notices a run stranded four hours in | Ch 27 | [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) |
| **Progress in the outbox** | Bloats the log, relay, audit trail, and replay path with data nobody reads | Ch 22 | [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) |
| **Metaphor collision** | Two correct models, one unstated disagreement, forty comments | §1.1 | [Ch 3](../chapters/03-mental-models-and-reference-system.md) |
| **Single-metaphor thinking** | Forcing a scheduling answer onto a contract question | §4.6 | [Ch 3](../chapters/03-mental-models-and-reference-system.md) |
| **The illustrative example** | A new example per chapter; the reader never sees the system | §1.3 | [Ch 3](../chapters/03-mental-models-and-reference-system.md) |
| **Purity by assumption** | Tagging a tool pure because it usually is | Ch 31 | [Ch 3](../chapters/03-mental-models-and-reference-system.md) |
| **Evolution reaching into the kernel** | Every recorded gain stops being attributable | Ch 46 | [Ch 3](../chapters/03-mental-models-and-reference-system.md) |
| **The convenient join** | One foreign key from a runtime table to a domain table, and the runtime is no longer removable | §2.2 | [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |
| **The loop in the handler** | The process becomes the system; a deploy becomes a data-loss event | Ch 2 | [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |
| **The god function** | Planning, dispatch, and domain writes in one place; the cold open | §1.1 | [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |
| **Premature process splitting** | Four deployables before a hundred concurrent runs; operational surface with no benefit | §12.3 | [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |
| **Progress in the outbox** | Bloats log, relay, audit trail, and replay path | §10.3 | [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |
| **Boot-only recovery** | The run stranded four hours in is never noticed | §11.2 | [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) |
| **"The agent" as a unit** | Averages five lifetimes; the cold open | §1.1 | [Ch 5](../chapters/05-five-nouns.md) |
| **The pinned run** | Holding a worker or lease for the run's duration; violates the custody gradient | §2.2 | [Ch 5](../chapters/05-five-nouns.md) |
| **The blocking park** | A thread or timer waiting for a human; a redeploy loses it | §5.5 | [Ch 5](../chapters/05-five-nouns.md) |
| **The mutable step** | Editing step rows on replan instead of writing new ones; history becomes unreconstructible | §5.3 | [Ch 5](../chapters/05-five-nouns.md) |
| **The episode with no exit** | Missing one of E1–E4; a run monopolises a worker | Ch 18 | [Ch 5](../chapters/05-five-nouns.md) |
| **Activity identity from position alone** | The worst bug class in the system; silent and confident | Ch 21 | [Ch 5](../chapters/05-five-nouns.md) |
| **The convenient column** | `current_step` on a domain aggregate; the runtime is no longer removable | §5.2 | [Ch 6](../chapters/06-state-separation.md) |
| **The persisted transcript** | Model state stored as truth; replay diverges | §5.3 | [Ch 6](../chapters/06-state-separation.md) |
| **The unscoped lesson** | Harness state true of a customer rather than of the system | §5.5 | [Ch 6](../chapters/06-state-separation.md) |
| **Read-time filtering** | The leak is already in a versioned file | §13.2 | [Ch 6](../chapters/06-state-separation.md) |
| **The memory that only grows** | Dilution, and superfluous re-verification on easy work | §12 | [Ch 6](../chapters/06-state-separation.md) |
| **Version skew across a park** | A run resumes against a harness its plan never saw | §7 | [Ch 6](../chapters/06-state-separation.md) |
| **Stream-only progress** | No view survives a disconnect; the cold open | §6 | [Ch 7](../chapters/07-edge-and-client-contract.md) |
| **Durable progress** | Bloats log, relay, audit, and replay | §10 | [Ch 7](../chapters/07-edge-and-client-contract.md) |
| **The convenience await** | Run latency becomes request latency | §5.1 | [Ch 7](../chapters/07-edge-and-client-contract.md) |
| **The synchronous first step** | A model call in the request path; planning split across layers | §5.2 | [Ch 7](../chapters/07-edge-and-client-contract.md) |
| **The inline consumer** | Deploy-correlated stalls and duplicates | §5.3 | [Ch 7](../chapters/07-edge-and-client-contract.md) |
| **Raw table exposure** | Public contract coupled to schema; internals leaked | §9 | [Ch 7](../chapters/07-edge-and-client-contract.md) |
| **Cancel as DELETE** | Cannot reach an abort controller inside a live call | §8 | [Ch 7](../chapters/07-edge-and-client-contract.md) |
| **Server-generated idempotency keys** | Deduplicates nothing | §13.1 | [Ch 7](../chapters/07-edge-and-client-contract.md) |

---

## Every mention, in order

18 passages across the book name an anti-pattern. The sweep is complete; the phrasing is the chapter's.

| Chapter | Section | Passage |
|---|---|---|
| [Ch 0](../chapters/00-evolution-of-ai-systems.md) | §13 | 13.3 Anti-patterns introduced here |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | §5 | The anti-pattern is specific and common enough to name: |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | §13 | 13.3 Anti-patterns |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | §13 | 13.3 Anti-patterns |
| [Ch 3](../chapters/03-mental-models-and-reference-system.md) | §13 | 13.3 Anti-patterns |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) | §13 | 13.3 Anti-patterns |
| [Ch 5](../chapters/05-five-nouns.md) | §13 | 13.3 Anti-patterns |
| [Ch 6](../chapters/06-state-separation.md) | §13 | 13.4 Anti-patterns |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | §13 | 13.3 Anti-patterns |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | §5 | The anti-pattern the paper names is repeatedly fixing at the wrong level — three iterations of prompt rewording for something a five-line middleware would have settled. |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | §16 | Fix at the weakest level that enforces.** Repeated prompt edits for something middleware would settle is the named anti-pattern, and the prompt is the component that measured *worse* than nothing. 5. |
| [Ch 43](../chapters/43-component-observability.md) | §5 | Record the routing decision, not only the edit.** Chapter 45's manifest has a `constraint_level` field for exactly this, and the useful audit is over the *distribution* of that field rather than over any single entry. - **Treat a second system-prompt edit for the same failure pattern as a routing failure.** Chapter 1 §5.2 named the anti-pattern; this is the mechanical form of it. |
| [Ch 45](../chapters/45-decision-observability.md) | §5 | The manifest is where it is counted. - **The same level three times for one failure pattern** is Chapter 1 §5.2's named anti-pattern. |
| [Ch 45](../chapters/45-decision-observability.md) | §5 | That query is the anti-pattern detector, it costs nothing, and it works only because both fields are mandatory. |
| [Ch 46](../chapters/46-the-evolve-agent.md) | §4 | Chapter 1 §5.2 named the anti-pattern and Chapter 45 §5.5 made it queryable. |
| [Ch 46](../chapters/46-the-evolve-agent.md) | §5 | 5.5 The wrong-level anti-pattern, mechanised |
| [Ch 46](../chapters/46-the-evolve-agent.md) | §5 | `[BP]` The counter is per `(failure pattern, level)` rather than per component, because the pattern is the thing being fixed and a loop that spread three attempts across three files at the same level has done the anti-pattern with extra steps. |
| [Ch 46](../chapters/46-the-evolve-agent.md) | §15 | `[AHE App. B.2]` The wrong-level anti-pattern — repeatedly fixing the same failure at the same level — and the constraint-level hierarchy the escalation rule acts on. |
