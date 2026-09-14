# ADR-0013 — MCP is a projection of the capability layer, not a second API

**Status:** ACCEPTED. The server is **deliberately not built**.
**Date / context:** 2026-09-05, Brain architecture review §14.

## Context

The strategic direction names "Brain MCP" as the interface through which
external coding agents consume organizational knowledge. MCP is legible,
demonstrable, and easy to build early.

## Decision

**Define a capability layer as a module with typed signatures. MCP is a thin
projection of it, later.** Do **not** write an MCP server now.

Four things to do now, which cost almost nothing:

1. Define the capability layer as a module with typed signatures.
2. Make every capability take an **explicit** Principal, never an ambient one.
3. Make every capability return **provenance**.
4. **Bound every result set.**

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Build the MCP server now | There is nothing to serve, and the identity question is unresolved. Built early it becomes *the thing that constrains the capability layer* rather than a projection of it. |
| MCP as its own API with its own logic | Creates a second ACL surface. |
| Skip the capability layer; project tools directly | Then the *tools* become the definition, and the HTTP and MCP surfaces each re-derive it. |

## Evidence and reasoning

**[DESIGN DECISION]** The capability layer has to exist regardless — it is the
MCP surface, the HTTP surface and the tool surface. Naming it now costs an
afternoon and prevents the tools from becoming the definition.

**Two hard problems MCP creates, neither solved by the transport:**

1. **Identity.** A coding agent connecting on behalf of an engineer means the
   IDE, the agent and the Brain are three parties, and the token must carry an
   identity the Brain can verify **without trusting the middle one.** Either the
   server mints its own Principal from a per-user credential, or it accepts a
   delegated token. Either can work; **letting the client assert an identity is
   the failure.** This must be decided before a server exists, not during. See
   `docs/project/10-open-questions.md` Q9.
2. **Structural containment is lost.** Internally, tool projection makes an
   unauthorised query inexpressible. An MCP client is not projected — it sees
   the same tool list as everyone. Enforcement falls back to runtime checks in
   the capability layer.

## Consequences

- The MCP surface exposes **fewer** capabilities than the internal one, not the
  same set: read-only at first, no `propose_claim`, and no capability whose
  result set is unbounded.
- The four cheap decisions above are effectively free now and a refactor later —
  particularly the explicit Principal, since an MCP call has no session context
  to inherit.
- **This is the second of the two things predicted to be built early anyway.**
  If it is, make it a strict projection with no logic of its own.

## What would cause us to reconsider — the trigger

A **stable capability layer**, plus a **decided answer** to "whose Principal is
an MCP caller." Both, not either.

## Source

`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0012](ADR-0012-the-agent-reaches-the-brain-only-through-tools.md),
[ADR-0016](ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md)
