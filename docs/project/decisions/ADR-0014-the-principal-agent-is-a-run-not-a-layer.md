# ADR-0014 — The Principal Agent is a Run, not a layer

**Status:** ACCEPTED
**Date / context:** 2026-08-30, Principal Agent architecture §2.4, correcting
the layered diagram in the originating brief.

**Not to be confused with** the handbook's **Principal** (session identity —
who is asking, resolved per call). A Principal Agent is a standing Run one
layer above that: it holds a Principal like any other client, but is itself
judged on outcomes across many runs rather than resolved once per call. See
`02-domain-model.md` §2.24.

## Context

The natural way to draw a Principal Agent is as a layer between the Surface and
the Agent Runtime — it receives goals from above and directs the runtime below.
Read as a diagram of **authority**, that is right. Read as a diagram of
**processes and imports**, it breaks two rules the whole architecture rests on.

## Decision

**A Principal Agent is not a layer inside the runtime. It is a CLIENT of the
runtime that is itself implemented as a Run.**

It submits goals through the Edge exactly as any other client does. It observes
outcomes through events and read models exactly as any other client does. Its
own reasoning is a Run — same loop, same ports, same leases, checkpoints,
parks, budgets, and crash recovery.

**A Principal Agent is a Run whose tools found other Runs.**

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| A layer between Surface and Runtime | Puts a decision loop **in the Edge**, which translates and does not participate — no loop, no consumer, no model call. And it puts domain reasoning **inside the kernel**, which is domain-agnostic by construction; the import-graph check fails in CI. |
| A privileged supervisor above the runtime | It would sit above the gate checks by construction, and the entire safety argument would have to be rebuilt from nothing. |
| Its own service with its own execution model | Re-derives idempotency, identity, the executed-prefix carry, and the audit trail — and gets at least one of them wrong. |

## Evidence and reasoning

**[DESIGN DECISION]** Four reasons, in the order they carry weight:

1. **It preserves the narrow waist.** The kernel still knows nothing about
   goals, organisations, or commitments. Those live in a domain reached through
   the domain port.
2. **It inherits Level 3 for free.** Deliberate for an hour, park for three days
   waiting for a human, survive a deploy, resume on a different worker, never
   apply an effect twice — every one of those is already a property of a Run.
3. **It is auditable by machinery that already exists.** Its deliberation is a
   trajectory in the trace store; its tool calls are activity rows; its
   authority checks are gate requests. **No second observability stack.**
4. **Containment becomes mechanical.** Being a Run, it is subject to every
   constraint a run is subject to — including the gate policy, which lives
   outside anything a loop may edit.

## Consequences

- **Two real costs, stated honestly.** (a) Its tenant is the organisation, which
  makes organisational state domain state inside a large and consequential
  tenant. (b) A run has a budget, a lease and an episode structure sized for
  minutes — so a deliberation spanning a quarter is **not one run; it is a
  lineage of runs**, each triggered by an event, each parking when there is
  nothing to do. That trigger structure is the one place this claim needs care
  rather than enthusiasm.
- **Four things a Principal Agent must never do**, each a containment argument
  rather than a policy preference:
  1. **Set its own goals.** One judged on whether goals are met, which can also
     write goals, *will* meet its goals — not by misbehaving, but by optimising
     exactly what it was asked to optimise. Proposing a goal is fine; writing
     one is the line that must not exist.
  2. **Execute work itself.** Its tool set must contain no tool that touches the
     world directly, or every outcome becomes jointly caused by its two roles
     with no way to separate them.
  3. **Grade its own outcomes.** An outcome verdict has a deterministic floor
     from a probe; the Principal Agent may only **lower** it.
  4. **Hold organizational knowledge in harness state.** Harness state must be
     true of the system, never of a customer — and an organisation is a
     customer. This is the most tempting of the four and the highest-damage.

## What would cause us to reconsider

A measured case where the lineage-of-runs trigger structure cannot express a
genuinely long deliberation. That would change the *episode* structure, not the
client relationship.

## Source

`learning-notes/Principal Agent - Organizational Intelligence Architecture.docx`
§2.3, §2.4, §3.5.

## Related

[ADR-0007](ADR-0007-memory-is-a-mechanism-not-a-state-category.md),
[ADR-0015](ADR-0015-verification-before-knowledge.md)
