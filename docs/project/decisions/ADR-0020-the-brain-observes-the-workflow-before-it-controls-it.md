# ADR-0020 — The Brain observes the engineering workflow before it controls it

**Status:** ACCEPTED
**Date / context:** 2026-09-14, stated in the current strategic direction.
Consistent with the Brain review's participation model (§12).

## Context

The engineering workflow that builds this system is itself an organization
producing decisions, implementations, bugs, fixes, tests, verifications and
human corrections. It is available, instrumented, and ours. It is the obvious
first validation environment — and the obvious temptation is to let the Brain
act in it.

## Decision

**The Brain OBSERVES the workflow. It does not control it.**

Participation is a ladder, and the rungs are climbed in order with a
measurement at each:

| Rung | What it may do | Gate to reach it |
|---|---|---|
| 1 | Observe. Write claims. Speak to nobody. | — |
| 2 | Answer when explicitly addressed. | Rung 1 producing claims worth reading |
| 3 | Volunteer unprompted, in one channel. | **Contradiction precision above a threshold registered in advance**, measured at rung 2 where being wrong is cheap |
| 4+ | Broader participation. | Volunteer precision sustained, and a mute rate of zero in the pilot channel |

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Let the Brain act in the workflow from the start | A few bad unprompted interventions and the agent is **muted permanently** — the capability is then gone regardless of later quality. |
| Skip observation, go straight to answering | Answering requires a store worth answering from. |
| A separate synthetic validation environment | The hard problems only appear with real messy input. |

## Evidence and reasoning

**[DESIGN DECISION]** The asymmetry is the whole argument: at rung 2 being
wrong costs one bad answer to someone who asked. At rung 3 being wrong costs
the channel's tolerance, and that is not recoverable by improving later.

The gate must be a **threshold registered in advance**, not judged afterwards —
otherwise the threshold moves to wherever the measurement landed. And the
demotion must be **automatic** if the threshold is not met.

## Consequences

- Two separations must be maintained, and conflating them is the failure this
  ADR most guards against:
  - **Our internal validation environment** versus **the general product
    architecture.** Organization-specific assumptions must not be hard-coded
    into the general design.
  - **Observation** versus **control.**
- The workflow must be instrumented for observation before the Brain can learn
  from it — see `docs/project/06-validation-strategy.md`.
- **Dogfooding is not product validation.** A system that helps its own authors
  has a sample of one team with unusual tolerance for its failures. This
  environment proves the *mechanism*, not the *market*.

## What would cause us to reconsider

Contradiction precision measured at rung 2 that is high enough to justify rung 3
would advance the ladder — which is the trigger working, not a reconsideration.
Evidence that observing our own workflow teaches nothing transferable would
send us to a different validation environment.

## Source

Current strategic direction, 2026-09-14;
`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0019](ADR-0019-one-source-end-to-end-before-breadth.md),
[ADR-0021](ADR-0021-product-direction-is-contested.md)
