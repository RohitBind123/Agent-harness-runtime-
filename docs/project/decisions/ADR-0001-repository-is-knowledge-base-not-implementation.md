# ADR-0001 — This repository is the justification layer, not the implementation

**Status:** ACCEPTED
**Date / context:** 2026-09-06, in the product research pass. Restated in the
Organizational Brain review, 2026-09-05, as its Finding 0.

## Context

By September 2026 this repository held 51 handbook chapters, a ~5,000-line
runtime specification, ten architecture and learning documents, and no product
code. The question "what do we do with this repository — extend it, refactor
it, replace it?" was raised as an implementation-strategy question and answered
as a category question.

## Decision

**Treat this repository as the justification layer for implementation that
happens elsewhere.** New code goes in a separate implementation repository.
This repository holds the derivation, the specification, the decisions, and —
from 2026-09-14 — the institutional memory.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Extend this repository into the implementation | There is nothing to extend. "Extend, refactor or replace" all presuppose code that does not exist. |
| Refactor the documents into a codebase | Documents are not a codebase in an early state; they are a different artefact. |
| Delete the documents and start fresh | Discards the derivation that makes the design arguable rather than asserted, and the provenance markers that separate evidence from inference. |

## Evidence and reasoning

**[CONFIRMED — verified by this audit at commit `169142e`]** The repository
contains 94 Markdown files, 11 DOCX, 9 SVG, 1 PDF, and 5 Python files. All five
Python files build or lint documentation. No product source file exists.

Stated in `docs/product/06-mvp-and-implementation-strategy.md` §8.1: *"use it
primarily as architectural reference. Not a judgement call — there is no code
to extend, refactor or replace."*

## Consequences

- The repository's value is that a design decision can be traced to the
  argument that produced it. Preserving provenance markers is therefore a real
  obligation, not editorial taste.
- **The repository can drift from the implementation without anything failing.**
  Nothing here is executed against code. This is the exact failure mode the
  Brain is designed to detect, and this repository is subject to it.
- Two pieces of work are owed regardless of where code lands: reconcile the two
  vocabularies ([ADR-0002](ADR-0002-specification-vocabulary-is-canonical-for-code.md)), and write down the single-writer profile of the 39
  invariants (see `docs/project/10-open-questions.md` Q8).

## What would cause us to reconsider

Implementation beginning *in* this repository — which would be a deliberate
change of role and should be recorded as such, not allowed to happen by a first
commit of a `src/` directory.

## Source

`docs/product/06-mvp-and-implementation-strategy.md` §8.1;
`docs/product/01-architecture-understanding.md` Finding 0;
`../../architecture/organizational-brain-architecture.md`

## Related

[ADR-0002](ADR-0002-specification-vocabulary-is-canonical-for-code.md)
