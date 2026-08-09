# Architecture Diagrams

These SVGs are the reusable visual summaries for the handbook and architecture material. Chapter
figures are ASCII inside the chapters themselves (see [CONVENTIONS.md](../../handbook/CONVENTIONS.md)
§3); SVG is reserved for level openers and cross-cutting reference figures.

## Five generations (Level 0 opener)

![Five generations: what each added, what each broke](level-0-evolution.svg)

Plots the five generations on the capability and survivability axes, and tabulates what each
generation added, which guarantee it broke, and the components that restore it. Read right-to-left
it is the dependency order of the book.

## Six-layer agent runtime

![Six-layer agent runtime](six-layer-agent-runtime.svg)

Shows the surface, stateless edge, durable substrate, generic kernel, six extension ports, product domain, and the narrow command/event waist between runtime and domain.

## Agentic Harness Engineering loop

![Agentic Harness Engineering closed loop](agentic-harness-engineering-loop.svg)

Connects component observability, experience observability, and decision observability into an evaluate-evolve-verify loop with file-level attribution and rollback.

## Five nouns and custody gradient

![Five nouns and custody gradient](five-nouns-custody-gradient.svg)

Relates Run, Episode, Step, Activity, and Park to lifetime and the scarcity of the resources each may hold.

## Complete agent runtime

![Complete agent runtime](complete-agent-runtime.svg)

Provides the end-to-end reference: ingress, substrate, worker kernel, ports, human gate, domain boundary, state machine, state ownership, invariants, and execution sequence.
