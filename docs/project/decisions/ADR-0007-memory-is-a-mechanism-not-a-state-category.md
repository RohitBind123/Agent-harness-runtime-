# ADR-0007 — Memory is a mechanism, not a state category

**Status:** ACCEPTED
**Date / context:** 2026-09-02, Memory Management Architecture, its ADR 2 and
Finding 1.

## Context

The natural reading of the handbook's four-category state model (domain / run /
model / harness) is that memory is harness state — "what the system has learned
to do." That equation is tempting, widely assumed, and false.

## Decision

**Memory is one MECHANISM that operates over more than one state category.**

The mechanism is fixed: **propose → abstract → route → classify → apply**,
carrying confidence, evidence, provenance, scope, and temporal validity. Which
state category a given claim lands in is not memory's decision — it is decided
by running the state-classification procedure on the claim.

**The routing rule:** a learned claim is **harness** state if it is true of the
SYSTEM. It is **domain** state, tenant-scoped, if it is true of a CUSTOMER.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Memory = harness state | Already false against the reference: the handbook's own table places the four memory subsystems in **three** state categories. And the consequence of believing it is a customer fact in a git repository. |
| Memory = its own fifth state category | Creates a category whose membership test is "was it learned?", which cuts across the existing four rather than partitioning anything. |
| One long-term store for everything | Either everything in git (breaks redaction) or everything in a database (discards the file's enumerable/diffable/revertable/line-attributable properties). |

## Evidence and reasoning

**[INFERENCE]** The routing rule is a consequence of reading the handbook's
harness-state rule — *"harness state must be true of the system, never of a
customer"* — as a **routing** question rather than a compliance rule.

**[CONFIRMED]** The consequence is governed by a hard constraint: **git history
cannot be redacted.** A tenant fact committed to a git-tracked memory file is
an unrecoverable governance breach with no deletion route.

## Consequences

- **There are two long-term stores, and that is not a compromise.** System-true
  claims go in the git-tracked file. Customer-true claims go in a database with
  the tenant in the key.
- A routing stage exists in the write path, and **defaulting it either way is a
  defect.**
- Memory owns a write path and a lifecycle. **It owns no facts about the
  world.** It does not become the owner of anything merely by remembering it.
- The word "memory" is never used unqualified in these documents.

## What would cause us to reconsider

A single-tenant deployment with no customer data would collapse the two stores
into one — but that is a deployment profile, not a change to the rule. The rule
would still be the thing that says the collapse is safe.

## Source

`learning-notes/Memory Management Architecture.docx` §1.1 (Findings 1–2), §6,
§37.1 (ADR 2, ADR 3).

## Related

[ADR-0010](ADR-0010-the-model-proposes-and-never-writes.md),
[ADR-0016](ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md)
