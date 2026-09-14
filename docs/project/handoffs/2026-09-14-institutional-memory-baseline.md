# Session Handoff — 2026-09-14 — Institutional memory baseline (Mission 0)

**Started from commit:** `169142e`
**Ended at commit:** *(this session's commit)*
**Branch:** `claude/repo-access-653473`

## 1. What I investigated

- **Full file inventory** of the repository. Counted by extension, listed every
  non-chapter file, and searched for any product source code.
- **Read in full:** `README.md`, `tasks/todo.md`, `docs/README.md`,
  `docs/product/README.md`, `docs/product/04-product-thesis-and-decision.md`,
  `docs/product/06-mvp-and-implementation-strategy.md`.
- **Read in part:** the runtime specification's §10 (all 39 invariants) and §15
  (build order); handbook chapters 4, 6, 27, 37 for the six layers, the four
  state categories, effect tiers and tenancy.
- **Extracted full text from four DOCX** and read their structure plus key
  sections: Organizational Brain (§1, §2, §5, §6, §13, §14, §15, §17–§20),
  Memory Management (§1, §37 all 19 ADRs, §38 roadmap), Principal Agent (§2.3,
  §2.4, §3.5), Agent Evaluation (structure only).
- **Compared the two uploaded DOCX against the repository copies** —
  byte-identical by md5.
- **Git history:** all 45 commits, with authors and dates.
- **Ran both repository linters.**
- **Searched for** `InOrbitX`, "business brain", "organizational brain" across
  all Markdown.

## 2. What I changed

Added, all new:

- `PROJECT_BOOTSTRAP.md` — the session-startup document.
- `docs/project/` — 14 documents plus an index:
  North Star, Architecture Map, Domain Model, Lifecycles and State Machines,
  Implementation Map, Development Workflow, Validation Strategy, Brain
  Observability, Build Order, DO NOT ASSUME, Open Questions, Architecture Change
  Log, Session Handoff Protocol, Audit.
- `docs/project/decisions/` — an index and **24 ADRs** (ADR-0001 … ADR-0024).
- `docs/project/handoffs/` — this file.

Modified, minimally and only to correct status:

- `README.md` — pointer to `PROJECT_BOOTSTRAP.md`, and a note that the README
  describes the handbook rather than the current product direction.
- `prd.md` — a status banner marking it **CONTESTED, NOT SUPERSEDED**.
- `tasks/todo.md` — a scope note saying it covers the handbook only.

**No handbook chapter, specification section, product research document or DOCX
was altered.**

## 3. What is now implemented

**Nothing. This was an audit and documentation session.** No product code was
written, and none should be until Q1 and Q2 are resolved.

## 4. What remains incomplete

- **Q7 (the Memory/Brain schema conflict) is recorded but not reconciled.** I
  deliberately did not resolve it: both documents are internally coherent, and
  picking one silently is exactly the failure this baseline exists to prevent.
  A plausible reconciliation is written down in `02-domain-model.md` §5 and
  **marked as an inference**.
- **Nine ADRs cover cross-cutting decisions only.** The Memory architecture's
  own 19 ADRs and the specification's 14 design rules are imported by reference,
  not duplicated.
- **The Agent Evaluation architecture was read structurally, not in full.** Its
  detailed contents are not reflected beyond the evaluation invariants.

## 5. Tests run

```
python3 tools/check_handbook.py
python3 tools/check_xrefs.py
md5sum on the two uploaded DOCX vs their repository copies
find/grep file inventory across the repository
```

## 6. Results

```
$ python3 tools/check_handbook.py
51 chapter(s): 0 error(s), 14 warning(s)

$ python3 tools/check_xrefs.py
73 document(s), 51 chapter(s): 0 unresolved reference(s)

$ md5sum ...
cda60c83cb4621535882d678b38ca5c5  uploaded Memory-Management-Architecture.docx
cda60c83cb4621535882d678b38ca5c5  learning-notes/Memory Management Architecture.docx
9872fdf78b72fe02d1915fb0473f944c  uploaded Organizational-Brain-Architecture.docx
9872fdf78b72fe02d1915fb0473f944c  ../../architecture/organizational-brain-architecture.md
```

File inventory: 94 `.md`, 11 `.docx`, 9 `.svg`, 5 `.py`, 1 `.pdf`.
**All five Python files build or lint documentation. No product source file
exists.**

## 7. New discoveries

Ordered by how much they change the picture.

1. **Zero product code exists.** Confirmed by inventory, not inferred. Several
   documents are written in the present tense about systems that have never
   been built — including a ~2,000-line "complete repository tree" for a tree
   that does not exist.
2. **The product direction is contested, and the contradiction had not been
   recorded anywhere.** `prd.md` says GO on a macOS paperwork agent and names as
   non-negotiable *"cut the terminal / Git / developer-tools environment from
   the roadmap entirely."* The current direction points at approximately that
   segment. **That argument has not been answered in any document.**
3. **The Memory and Brain architectures specify incompatible Phase 1 schemas**,
   and **neither acknowledges the other.** Memory rejects an entities table and
   a conflicts table and defers entity resolution; the Brain requires all three
   in Phase 1. They use the same words for different things.
4. **The architecture's stated evidentiary foundation was external material
   this repository does not contain.** Its central finding and its component
   decisions rested on artefacts nobody here has read. *(Withdrawn entirely on
   2026-09-14 — see [ADR-0025](../decisions/ADR-0025-no-external-codebase-is-evidence.md).
   Nothing in this design has been built or validated anywhere.)*
5. **`InOrbitX` appears nowhere in this repository.** No definition, no scope,
   no system inventory. The validation environment is entirely undefined.
6. **The workflow the Brain is meant to observe produces no PRs, no CI, and no
   tickets** — which are precisely the Brain's strongest first sources.
7. **Git history splits cleanly:** human-authored handbook work through
   2026-08-16; Claude-authored architecture deliverables from 2026-08-28.
8. **Two claims I expected to confirm and could not:** that the four
   architecture documents form one coherent design (they conflict — see 3), and
   that the current strategic direction extends the recorded product decision
   (it contradicts it — see 2).

## 8. Architectural decisions

**None made.** Twenty-four were *extracted and recorded* from existing material.
Where a document stated a decision without stating why, the record says
"Rationale not yet established" rather than supplying a plausible reason.

Two records deliberately capture non-decisions:
[ADR-0002](../decisions/ADR-0002-specification-vocabulary-is-canonical-for-code.md)
(PROPOSED, unratified) and
[ADR-0021](../decisions/ADR-0021-product-direction-is-contested.md) (OPEN,
blocking).

## 9. Architectural concerns — raised, not changed

1. **Permissions are the most dangerous under-designed area.** Overlapping,
   non-partitioned audiences are stated as a requirement with **no mechanism
   designed** — and a permission leak produces no error and no log line. Not
   changed because designing it needs the real environment (Q3).
2. **The design-to-code ratio.** ~5,000 lines of specification and 51 chapters
   against zero code, with the project's own estimate that ~15% goes in a first
   build. Not changed because the depth also produced the finding that
   provenance and temporal fields cannot be retrofitted, which will save more
   than it cost.
3. **Depth is unevenly distributed.** The areas that were most enjoyable to
   specify are the deepest; permissions, entity resolution, admission and
   extraction — the four places real data hurts first — are the thinnest.
4. **39 invariants for a single-writer system.** The right response is the
   written profile (Q8), not deletion — deleting the wrong half loses the
   correctness properties that are the point.
5. **No behaviour is specified for a step when the Brain is unavailable.** "The
   read path never fails a step" does not say what a step does with no context.

## 10. Open questions

Sixteen recorded in `10-open-questions.md`, plus seven that are unsolved by any
current design.

**New this session:** Q1 (product direction), Q3 (what is InOrbitX), Q7
(schema reconciliation), Q15 (contradiction severity rules), Q16 (entity
merge/split lifecycle).

**Carried forward from existing findings:** Q2 (authority ladder), Q4
(vocabulary normativity), Q5 (predicate vocabulary), Q6 (first source), Q8
(single-writer invariant profile), Q9 (MCP caller identity), Q10 (overlapping
permissions), Q11 (floors and half-life), Q12 (vocabulary growth), Q13 (human
correction vs human error), Q14 (taint through extraction).

## 11. Risks

- **This documentation set can go stale silently**, because nothing here is
  executed. It is subject to exactly the failure the Brain is designed to
  detect, and this corpus is the least protected thing in the project.
- **The audit's status claims rest on one commit.** They should be re-verified
  rather than trusted if the repository has moved.
- **The architecture's external evidentiary claims could not be verified.**
  *(Resolved 2026-09-14: they are withdrawn, not pending verification.)*
- **Recording the product direction as contested may read as obstruction.** It
  is not: the architecture work is common to both directions and is not wasted.
  Only implementation is blocked.
- **Twenty-four ADRs is a maintenance obligation.** If they are not updated when
  decisions change, they become a second stale source of truth.

## 12. Recommended next action

**Spend one week collecting twenty to fifty real questions from the project's
own history, and hand-run Stage 1's exit test on paper — no code.**

The reasoning is in `13-audit-2026-09-14.md` §J–K. In short: it is the only
candidate next step that can **falsify** the premise rather than assume it; it
produces the predicate vocabulary, the held-out temporal question set, and
evidence on which source is first as by-products; it blocks on nothing; and its
classification step (lookup / why / temporal / contradiction) directly tests the
one thing recorded as genuinely open — whether any of this beats a good search
box for the questions people actually ask.

**Two decisions are needed from a named human and cannot be unblocked by
building:** Q1 (which product) and Q2 (who authors the authority ladder).
