# Session Handoff — 2026-09-14 — Product direction resolved; evidentiary basis corrected

**Started from commit:** `0425653`
**Ended at commit:** *(this session's commit)*
**Branch:** `claude/repo-access-653473`

## 1. What I investigated

- Re-read every place in the documentation set that treated external reference
  material as an open verification gap informing this project, and every place
  that treated `prd.md` as a competing, contested product direction
  (ADR-0021, Q1).
- This was not new research — it was locating every propagation point of two
  framings the project owner corrected directly in conversation.

## 2. What I changed

**Added:**

- `decisions/ADR-0025-no-external-codebase-is-evidence.md` *(rewritten later the same day — see the following handoff)*
- `decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md`
- This handoff.

**Modified — correcting the two framings above, not rewriting substance:**

- `decisions/ADR-0021-product-direction-is-contested.md` — marked
  **SUPERSEDED by ADR-0026**, left otherwise unedited as a historical record of
  a genuine ambiguity at the time it was written.
- `decisions/README.md` — index updated: ADR-0021 → SUPERSEDED; ADR-0025 and
  ADR-0026 added.
- `10-open-questions.md` — Q1 moved from §1 Blocking to §4 Resolved, with the
  resolution and its ADR.
- `11-architecture-change-log.md` — two new dated entries; the 2026-09-06
  prior-history row corrected from "NOW CONTESTED" to "EXPLORATORY, resolved."
- `PROJECT_BOOTSTRAP.md` — §2 (strategic hypothesis), §3 (what exists, added the
  new PRD row), §5 (rewritten), §6 (decisions table), §7
  (blocking questions), §8 (Stage 0 note), §9 (do-not-assume summary), §10
  (what to do next), §11 (documentation map, both tables).
- `00-north-star.md` — header, §3 (customer), §5 (the wedge's arguments
  against), §6 (not-the-product table), §8 (falsifiers).
- `04-implementation-map.md` — §4 rewritten, the product
  research/PRD rows, gap #2 marked resolved.
- `09-do-not-assume.md` — §3 and §5 rewritten.
- `08-build-order.md` — Change 2 and the Stage 0 table row.
- `01-architecture-map.md` — the source-adapter status field.
- `13-audit-2026-09-14.md` — a correction note added above the original text.
  **The audit's own findings are not altered** — they were accurate the day
  they were written.
- `14-outside-in-review-2026-09-14.md` — a correction note added to A9. **The
  rest of the review is not altered.**
- `PRD.md` — §0 (new correction note, replacing the old "does not resolve Q1"
  framing), §4.2, §18 (Stage 0 row, Change 2 note), §20.1 (Q1 removed from
  blocking), §21 (D1 rewritten as resolved, D2 retitled), §24.1 (contested-line
  removed), §26 (items 2, 13, 15 marked resolved/moot), Appendix C (source map).
- `prd.md` (root) — banner rewritten from "CONTESTED, NOT SUPERSEDED" to
  "EXPLORATORY. NOT THE LIVE PLAN, NOT CONTESTED, NOT WITHDRAWN."

**Deliberately NOT modified**, per the handoff protocol's own rule against
editing a previous session's record: `handoffs/2026-09-14-institutional-memory-baseline.md`.
I edited it once, then reverted that edit on reviewing the protocol I was
supposed to be following — the correction belongs here, in a new handoff, not
retrofitted into the old one. Anyone reading that handoff should read this one
alongside it.

**Not modified at all:** any handbook chapter, the specification, the product
research documents (`docs/product/`), or any DOCX — this is a correction to
this project's own derived documentation, not to source material.

## 3. What is now implemented

**Nothing. This was a documentation-correction session.**

## 4. What remains incomplete

Nothing from this specific correction. The underlying open questions this
correction did not touch (Q2 the ladder, Q3 InOrbitX's observable surface, Q7
the schema conflict, and Q17–Q21 from the outside-in review) are unchanged and
still open.

## 5. Tests run

```
python3 tools/check_handbook.py
python3 tools/check_xrefs.py
<link-checker script over docs/project/, PROJECT_BOOTSTRAP.md, README.md, prd.md>
```

## 6. Results

```
51 chapter(s): 0 error(s), 14 warning(s)
73 document(s), 51 chapter(s): 0 unresolved reference(s)
```

Link checker: see the next handoff-adjacent commit message for the exact count;
run again before trusting this number if the repository has moved.

## 7. New discoveries

1. **The product-direction contest recorded in ADR-0021 never existed.**
   `prd.md` was written to explore a different question — using the agent
   runtime to control iOS/macOS — and the project owner said so directly. This
   is the single highest-value correction in this session: it resolves what
   `PROJECT_BOOTSTRAP.md` had called *"the highest-priority open question in
   the project."*
2. **External reference material was never claimed by the owner to inform this
   project.** The prior framing — "unverified, ask to attach if needed" — was
   inherited from the architecture document's own self-description, not
   confirmed with the owner, and was wrong to carry forward as live context.
   *(This handoff's remedy was itself insufficient and was superseded later the
   same day by a full purge — see the following handoff.)*
3. **A protocol violation, caught and corrected within this session:** I
   initially edited the prior handoff to add a correction note, then found
   `12-session-handoff-protocol.md`'s own rule — "never edit a previous
   session's handoff" — and reverted it. The correction belongs in this file
   instead. Worth flagging because it is exactly the kind of small
   inconsistency this project's own discipline exists to catch.

## 8. Architectural decisions

Two, both directly from the project owner, both recorded as ADRs before being
propagated anywhere else:

- [ADR-0025](../decisions/ADR-0025-no-external-codebase-is-evidence.md)
- [ADR-0026](../decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md),
  superseding [ADR-0021](../decisions/ADR-0021-product-direction-is-contested.md)

## 9. Architectural concerns — raised, not changed

None new. This session corrected project *context*, not architecture.

## 10. Open questions changed

**Resolved:** Q1 (which product), moved to `10-open-questions.md` §4.

**Unaffected:** Q2 through Q21. In particular, Q2 (the authority ladder) is now
the *only* remaining blocking decision recorded in `PROJECT_BOOTSTRAP.md` §7.

## 11. Risks

- **This correction rests on a conversational statement, not a written,
  independently reviewable artefact** — the same evidentiary standard the
  project applies to everything else. It is recorded as the strongest
  available evidence class for a product decision (a direct statement from the
  person with authority to make it), consistent with how Q1 always said it
  would be resolved: *"a named human picks A, B, C or D."*
- **`prd.md` itself was not rewritten**, only its framing relative to the live
  direction. If the runtime-controls-OS question is picked up again later, the
  research in it is still there to build on.
- **A fresh session that reads only the prior handoff** (not
  `PROJECT_BOOTSTRAP.md` or this file) will still see the old, superseded
  framing. `PROJECT_BOOTSTRAP.md` is the entry point specifically so this
  doesn't matter, but it's worth naming as a residual gap in a document set
  that otherwise tries to leave no stale front door.

## 12. Recommended next action

**Unchanged from the prior handoff, with one blocker now cleared:** the
recommended next step in `13-audit-2026-09-14.md` §J–K and
`14-outside-in-review-2026-09-14.md` §2.6 still stands — the V0 experiment
programme (question-shape study, Wizard-of-Oz context A/B, extraction sample,
the ladder meeting) needs no Q1 resolution to start, and now it doesn't need
one anyway. **The one decision still blocking Stage 0 is Q2** — hold the
ladder meeting.
