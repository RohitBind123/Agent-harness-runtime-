# ADR-0006 — Authority is authored configuration, never inferred

**Status:** **ACCEPTED — UNEXECUTED.** The decision is settled. The ladder does
not exist.
**Date / context:** 2026-09-05. Recorded as the hardest and the blocking
design question in this architecture.

## Context

Deterministic precedence between conflicting sources requires a well-founded
ordering over source classes. That ordering can come from exactly three places:

1. **Published inside the corpus being read.** The special case: it holds for
   corpora that are themselves regulatory or contractual, where the documents
   state their own precedence.
2. **Authored outside it**, by a named human.
3. **Inferred** — from recency, author seniority, or confident phrasing.

**Case 1 does not generalise. A general organization publishes no such rule.**
There is no sentence anywhere in a company that says a signed agreement beats
an SOP beats a product guide beats a deprecated policy beats a closed ticket.
Case 3 is rejected in the alternatives below. Therefore case 2.

## Decision

**The source-class ladder is CONFIGURATION: authored by a named human,
versioned, reviewed, and outside anything the agent may edit.** The Brain
*enforces* a ladder. It does not *learn* one.

Authority resolution is two-dimensional — a source class has a position on
**intent** and a separate position on **reality**. A decision outranks an
observation on intent and is outranked by it on reality.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Infer authority from recency | Wrong precisely when a junior person states something confidently and recently. |
| Infer from author seniority | Encodes org chart as epistemics, and breaks the moment the most knowledgeable person is junior. |
| Infer from how confidently something is written | Rewards assertive phrasing. Actively adversarial to the property being measured. |
| Let a model judge authority per conflict | Non-deterministic precedence means the same two claims can resolve differently on two runs. |

## Evidence and reasoning

**[DESIGN DECISION]** *"That is not an engineering problem and it cannot be
solved by an LLM. It is a GOVERNANCE act."*

The failure mode of inference is not that it is wrong sometimes — it is that it
is **wrong invisibly, and wrong in exactly the cases that matter.** A system
that infers authority produces a confident answer in precisely the situations
where a human would have hesitated.

## Consequences

- **A blocking prerequisite that is not an engineering task.** It needs a named
  human, a meeting, and a versioned file. Expect the meeting to surface genuine
  disagreement about how the organization works — *that disagreement is the
  finding*, and it is better discovered in a meeting than in production.
- The ladder lives outside the evolvable workspace. Nothing the agent runs may
  edit it.
- Confidence modifiers derive from claims, never from a model's judgement of
  tone or seniority.
- **Until the ladder exists, every downstream mechanism — resolution,
  contradiction, retrieval ranking — is meaningless.** This is why it is Q2 and
  why it blocks Phase 1.

## What would cause us to reconsider

Nothing about the *authored* property. The *shape* (how many classes, which
axes) should change freely as the ladder is used — that is a configuration
change, and the change log records it.

## Source

`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0003](ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md),
[ADR-0024](ADR-0024-no-autonomous-knowledge-curation.md)
