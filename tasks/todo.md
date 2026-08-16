# TODO

**The handbook is complete.** Fifty chapters (0–49) across six levels, two interludes, six level
openers each paired with its SVG, front matter F.1–F.4, all ten appendices, and a v1.0 compiled
reading edition.

| Check | State |
|---|---|
| `tools/check_handbook.py` | 50 chapters, **0 errors**, 14 warnings |
| `tools/check_xrefs.py` | 72 documents, **0 unresolved references** |
| `tools/build_glossary.py --check` | Appendix A current, 489 terms |
| `tools/build_appendices.py --check` | D, E, G, H, I, J current |
| `tools/compile_handbook.py` | DOCX v1.0, 57,127 source lines |

The per-chapter briefs and the batch history are in
[`docs/handbook/blueprints/phase-3-completion-plan.md`](../docs/handbook/blueprints/phase-3-completion-plan.md).

---

## Other workstreams

- **StaQuest B2B vendor business** —
  [`staquest_product_onboarding/todo.md`](../staquest_product_onboarding/todo.md).
  Strategy memo, PRD review and inbound reply drafts live in the same folder. Phase 0 is
  sales, not engineering.

---

## Standing tasks

Maintenance obligations, not outstanding work. Run them after any chapter edit.

- [ ] Keep `tools/check_handbook.py` at zero errors. The 14 warnings are all verified "the agent"
      uses that legitimately name the Evolve Agent or the agent debugger — Ch 42–49 add none, because
      Ch 44 says "the distiller" and Ch 46 says "the Evolve Agent" in full for this reason.
- [ ] Keep `tools/check_xrefs.py` at zero unresolved references.
- [ ] Regenerate Appendix A (`python3 tools/build_glossary.py`) and D, E, G, H, I, J
      (`python3 tools/build_appendices.py`). Both take `--check` for CI.
- [ ] Rebuild the compiled edition (`python3 tools/compile_handbook.py`) before shipping a release.
- [ ] Keep the three READMEs and the reading map in step with any structural change.

---

## Known gaps, recorded rather than pending

Each is a deliberate limit stated in the book itself, not an item someone forgot.

**In the architecture.** Chapter 48 §5.6 leaves indirect boundary erosion undetected by anything — a
loop that cannot edit a boundary can propose changes that make it irrelevant, with every edit
permitted and measured positive. The handbook names it as the most important open problem in Level 5
and offers only human review against it. Chapter 46 §5.3 states that the eleven-entry containment
list is a lower bound found by a method with no stopping condition. Chapter 49 §2.1 names fallback
atrophy — the team's ability to re-fit a harness by hand decaying because the loop succeeds — with no
mechanism proposed.

**In the tooling.** Appendix F is the one appendix that could be generated and is not. Invariants are
stated across fifty chapters in prose rather than in a structured block; a marker convention in the
authoring template would make them extractable, and would let the linter check that every invariant
still has a chapter behind it. Appendix F §3 records this as `[FUT]`.

**In the sources.** Chapter 39 §15 and Chapter 44 §15 both propose deriving the blast-radius linter
from trace data rather than maintaining it by hand — the per-task analysis already records which
harness components each task exercised, which is the mapping. Nobody has built it.

---

## If you are extending the book

1. Read the chapter's brief in the completion plan §6, and its `Requires`/`Unlocks` in the Phase 2 §4
   spine.
2. Read [`CONVENTIONS.md`](../docs/handbook/CONVENTIONS.md) — §2 for the four on-ramp blocks, §8 for
   the definition of done.
3. Write against the §3 skeleton. Copy the header block from the preceding chapter and edit it; the
   linter checks that `Requires` precede and `Unlocks` follow.
4. Plan a Full-tier chapter's nine figures *before* writing. Nine ASCII figures in document order
   cannot be retrofitted cheaply.
5. Write the §2.2 derivation early, not last. It repeatedly surfaces the strongest framing in the
   chapter.
6. Expect the linter to fail on the first run. It catches a prohibited word or an over-wide diagram
   in almost every chapter — that is the tool working. Do not weaken a check to make a chapter pass.
7. Regenerate the appendices, re-run both checkers, and update the three READMEs.
