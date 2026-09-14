# ADR-0003 — The Brain's core object is a kind-typed claim

**Status:** ACCEPTED
**Date / context:** 2026-09-05, Organizational Brain architecture review §6.1.

## Context

A system reconstructing organizational knowledge must decide what its core
object is. The available candidates are a document, a chunk, an embedding, an
entity — or a claim. The choice determines whether disagreement between sources
is representable at all.

## Decision

**The core object is a CLAIM, and every claim carries a KIND. The kind
determines what the claim has authority over.** Six kinds:

| Kind | Authority over | **No** authority over | Lifecycle |
|---|---|---|---|
| Observation-backed claim | Reality, at the moment observed | Intent; what should happen | Accumulates standing by corroboration; decays; retires |
| Decision | Intent — what the organization committed to | Reality. A decision does not change the code | Append-only. Superseded by a later decision; the old one stays |
| Implementation fact | Reality, more strongly than an observation because it is re-derivable | Intent. Stale the moment the code changes | Re-derivable by a probe — behaves like a belief |
| Outcome | What happened | **Causation** | Append-only, tied to a sealed prediction |
| Constraint / policy | What may be done | What *is* done — a policy and its enforcement are different facts | Human-authored configuration. Not learned |
| Term / definition | Vocabulary | Anything substantive | Effectively permanent |

Two things are explicitly **not** claims: an **observation** (the raw record
that someone *said* something) and an **entity** (a row in an identity table).

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Documents/chunks with similarity ranking | Perfect retrieval still hides the disagreement — the model picks one and states it as fact. The failure is structural, not a ranking-quality problem. |
| A single untyped claim kind with a source tier | Tiers say which *source* wins. They cannot express that a decision has no authority over what the code currently does. |
| Entity-attribute-value with typed attributes | Loses the distinction between "we decided X" and "X is true", which is the whole point. |

## Evidence and reasoning

**[DESIGN DECISION]** The cancellation example (`00-north-star.md` §2) is the proof: a
product statement in Slack, a developer's PR-review observation, and a test
file. In a single-kind store all three are "documents about cancellation" and
their disagreement is a ranking problem. In a kind-typed store the question is
answerable in one sentence — *intent says yes, reality says no, and that gap is
the answer.*

## Consequences

- The predicate registry must carry `kinds_allowed`, so that a *decision* may
  assert `intended_behaviour` but not `current_behaviour`. That one column is
  what enforces this ADR at write time.
- Claim identity is `(subject, predicate)` within a scope, with the **object
  deliberately excluded** — so a contradiction is a key collision rather than
  two rows that both happen to retrieve.
- Extraction becomes harder: it must classify kind, not just extract text.
- Coverage is explicitly bounded and visible, rather than implicitly unbounded
  and invisible.

## What would cause us to reconsider

Measured evidence that the kind classification is unreliable at extraction time
— specifically, that human reviewers disagree with the extractor's kind
assignment often enough that downstream authority resolution is noise. The
reviewed sample (the Brain architecture) is the instrument that would show this.

## Source

`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0022](ADR-0022-predicate-vocabulary-is-closed-and-reviewed.md),
[ADR-0006](ADR-0006-authority-is-authored-configuration-never-inferred.md)
