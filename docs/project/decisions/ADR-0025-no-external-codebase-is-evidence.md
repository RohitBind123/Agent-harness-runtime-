# ADR-0025 — No external codebase is evidence for this project

**Status:** **ACCEPTED.**
**Date / context:** 2026-09-14, decided by the project owner.

## Context

This architecture was originally written as a generalisation of external
reference material — codebases outside this repository, which nobody working in
this repository has read. That framing produced three classes of claim that
spread through the corpus:

1. **Evidence claims** — decisions marked as confirmed because some external
   system was reported to do the same thing.
2. **Effort claims** — scope and difficulty estimates expressed as a delta from
   an assumed head start ("reuse this unchanged, generalise that").
3. **Modal claims** — sentences written as *already*, *unchanged*, *inherit*,
   *keep*, *do not relax*, which presuppose a working thing to leave alone.

**An earlier decision excluded that material from scope but left it named and
cited throughout.** That was insufficient: the claims above survived the
exclusion, because most of them never named their source. This ADR supersedes
that position.

## Decision

**No external codebase is evidence for this project.** Concretely:

- **Nothing in this design has been built or validated anywhere.** There is no
  prior implementation, no head start, and no component that may be assumed to
  work because something like it worked elsewhere.
- **Scope, effort and difficulty estimates start from zero.** An estimate
  derived from an assumed head start is void, not adjusted.
- **A decision is supported by the argument stated for it in this repository,
  or it is unsupported.** "Some other system does this" is not support.
- **A quotation whose source is outside this repository is rewritten as an
  assertion in this project's voice, or deleted.** It is never stripped of its
  attribution and kept verbatim — that converts a traceable external claim into
  an untraceable native-sounding one, which is worse than leaving it attributed.
- **Reference material may still be read for ideas.** An idea is not
  contaminated by its origin. What is forbidden is citing an unreadable
  artefact as *evidence*, and writing in a tense that implies it exists here.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Keep the material cited, marked out of scope | Tried, and insufficient. The framing survives without the citation, because most contaminated claims never named a source |
| Delete only the names | Removes roughly the smaller half of the problem. Unnamed paraphrase — an unspecified prior system, a head start, a set of components to carry over — conveys the same false prior with no name attached |
| Keep effort estimates, adjust them downward | There is no defensible multiplier. An estimate with no basis is not improved by scaling it |

## Evidence and reasoning

**[FACT]** Zero product source files have ever been committed to this
repository.

**[DESIGN DECISION]** The corpus is read as startup context by future sessions.
A sentence implying prior art exists is a false prior that inflates confidence
and shrinks perceived scope — and it is exactly the failure this architecture
exists to detect, sitting inside its own governance layer.

## Consequences

- **The project's evidence base is explicitly empty.** See
  `docs/architecture/organizational-brain-architecture.md` §8, which is the
  canonical statement; other documents point at it rather than writing their own.
- Several decisions move from *evidenced* to *reasoned-only*. None was
  invalidated — each is supported by an argument made here.
- Phase 1 has not been estimated, and any number offered for it would be invented.
- **This is enforced, not merely stated:** `tools/check_provenance.py` fails on
  reintroduction. A constraint that binds is working.

## What would cause us to reconsider

Code that this project can actually read, run and test. Reported properties of
an unreadable artefact never qualify, regardless of how detailed the report is.

## Source

Project owner decision, 2026-09-14.

## Related

[ADR-0001](ADR-0001-repository-is-knowledge-base-not-implementation.md),
[ADR-0002](ADR-0002-specification-vocabulary-is-canonical-for-code.md),
[ADR-0015](ADR-0015-verification-before-knowledge.md)
