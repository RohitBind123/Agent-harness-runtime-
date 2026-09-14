# ADR-0012 — The agent reaches the knowledge system only through tools

**Status:** ACCEPTED
**Date / context:** 2026-09-05, knowledge system architecture review §13.1.

## Context

An agent needs organizational context. The cheapest way to give it context is
to import the knowledge system's repository object and call it. The cheapest way is wrong.

## Decision

**The agent reaches the knowledge system only through TOOLS.** Not through an import. Not
through a shared repository object. Not through a context injected at graph
build time.

Enforce it with a **lint rule**, the same way the clock discipline is enforced:
the agent package must not import the knowledge system's store.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Direct import of the knowledge system repository | Destroys the containment property — see below. |
| Context injected at graph build | The injected set is fixed at build time and cannot vary with the question, so it is either too broad (leaks) or too narrow (useless). |
| A shared in-process object with its own ACL checks | A second ACL implementation. Two ACL implementations is one ACL implementation that is wrong. |

## Evidence and reasoning

**[DESIGN DECISION]** The containment argument rests entirely on **tool
projection**: tools are curried with the Principal at graph-build time, so an
unauthorised query is **ABSENT FROM THE SCHEMA** rather than refused at runtime.
That property is what makes one agent safe for several roles.

If the agent can import the knowledge system's store directly, the projection stops being
the boundary — and every access-control argument weakens at once. **Not because
someone will misuse it, but because the guarantee changes from structural to
conventional.**

## Consequences

- knowledge system tools live in the agent's tools package, curried like every other tool.
- Each tool returns **evidence handles** rather than bare values, so the
  grounding gate can verify an answer's claims.
- A denied read **raises** rather than returning empty — a filter that returns
  nothing is indistinguishable from having no data and produces no signal.
- The knowledge system is placed as a **peer package**, not inside the agent or the
  knowledge layer.
- Some latency and some ceremony versus a direct call. That is the price of the
  guarantee being structural.

## What would cause us to reconsider

Nothing. This is load-bearing for a security property and is listed among the
things that **must not be modified**.

## Source

`../../architecture/organizational-brain-architecture.md` (G), §13.1, §13.2.

## Related

[ADR-0013](ADR-0013-mcp-is-a-projection-of-the-capability-layer.md),
[ADR-0016](ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md)
