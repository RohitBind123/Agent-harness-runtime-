# Session Handoff — 2026-09-14 — External provenance purged

**Started from commit:** `c2689c6`
**Ended at commit:** *(this session's commit)*
**Branch:** `claude/repo-access-653473`

## 1. What I investigated

- Mapped every occurrence of retired external-reference material across the
  whole repository — text, binary and git history.
- **The key finding, which changed the approach:** direct names were roughly
  **40%** of the problem. **29 unnamed paraphrases across 14 files** carried the
  same false prior with no name attached, and nine of them survived a
  name-only deletion completely intact.
- Read the four ADRs whose stated evidence was an unreadable artefact, and the
  architecture document's structure paragraph by paragraph (2,263 paragraphs)
  to separate its inventory of external code from its claims about
  organizations.

## 2. What I changed

**Added:**

- `docs/architecture/organizational-brain-architecture.md` — the architecture's
  reasoning, converted from the retired binary and purged. Its §8 is now the
  project's canonical evidence statement.
- `docs/product/07-organizational-knowledge-landscape.md` — the competitive
  research, which existed nowhere in markdown and would have been destroyed.
- `tools/check_provenance.py` + `tools/provenance-denylist.txt` — the guard.
- `decisions/ADR-0025-no-external-codebase-is-evidence.md`, replacing the
  earlier and weaker "excluded but still cited" position.
- This handoff.

**Deleted:**

- The contaminated architecture `.docx` (salvaged first — see above).
- `PROJECT_BOOTSTRAP.md` §5, `04-implementation-map.md` §4,
  `09-do-not-assume.md` §3, `14-outside-in-review` A9 — whole sections that
  existed only to discuss the retired material. All renumbered.

**Rewritten rather than deleted:** ADR-0002 (three candidates → two), ADR-0003
and ADR-0022 (`[CONFIRMED]` stripped, decisions intact), ADR-0006 (context
re-derived from first principles), Q2/Q4/Q7/Q18 evidence cells, `PRD.md` risk
register, `13-audit` §I.

## 3. What is now implemented

`tools/check_provenance.py` — a working, tested linter. **The first executable
thing in this repository that is not documentation tooling for the handbook.**
It scans 170 files including `.docx` via `zipfile`, which neither existing
linter reaches.

## 4. What remains incomplete

- The converted architecture document is deliberately **condensed**, not a
  faithful 2,263-paragraph conversion: `docs/project/` already carried 2,468
  lines stating the same design. If something turns out to be missing, it is
  gone — the binary was deleted after salvage.

## 5. Tests run

```
python3 tools/check_provenance.py                 # whole repo, incl. .docx
python3 tools/check_provenance.py <probe file>    # deliberate regression
python3 tools/check_handbook.py
python3 tools/check_xrefs.py
<repo-wide internal link checker>
```

## 6. Results

```
170 file(s): 0 provenance finding(s)
regression probe: 5 findings, exit 1   (guard verified in both directions)
51 chapter(s): 0 error(s), 14 warning(s)
73 document(s), 51 chapter(s): 0 unresolved reference(s)
1165 internal link(s): 0 broken
git log --all -S<each pattern>: no commit outside the denylist file
```

**The guard caught this handoff.** The first clean run was taken before §7 was
written; §7 then quoted three of the denylisted patterns as examples and the
next run failed on them. Recorded here rather than quietly fixed, because it is
the strongest evidence available that the check does something a careful reader
would not.

## 7. New discoveries

1. **Deleting names is not purging provenance.** The framing survives the
   citation. A sentence can appeal to an unreadable artefact, assert that the
   work was done before, offer an inventory to carry over, or quote a measured
   size — all without naming anything, so there is nothing to grep for and the
   false prior lands intact. This is the single most useful thing learned here.
   The patterns themselves are written down in `tools/provenance-denylist.txt`,
   which is deliberately the **only** place in the repository that holds them;
   quoting them in prose — including prose warning against them, as an earlier
   draft of this section did — reintroduces exactly what the guard forbids.
2. **Laundering is worse than contamination.** De-attributing a quotation whose
   source is purged, and keeping the words, converts a traceable external claim
   into an untraceable native-sounding one. Rewrite as an assertion or delete.
3. **Modal verbs encode existence claims.** *Already*, *unchanged*, *inherit*,
   *keep*, *do not relax* all presuppose a working thing. After the purge
   nothing exists to leave alone. `13-audit` §I was titled *"What should remain
   unchanged"* — the ideas survived, the tense did not.
4. **A documentation bug surfaced that has nothing to do with the purge.**
   Q7's schema reconciliation rested on a quotation attributed to the Memory
   Management document. **That quotation is not in that document.** The
   reconciliation is now marked as an inference from each document's scope,
   which is what it always was.
5. **`[CONFIRMED]` carries two meanings in this corpus** — "an in-repo document
   says so" and "someone saw code run." The purge removes exactly the cases
   that meant the second. The marker vocabulary is still undefined in
   `PROJECT_BOOTSTRAP.md` §0, which documents two other vocabularies but not
   this one. **Left open deliberately; recorded here so it is not lost.**

## 8. Architectural decisions

[ADR-0025](../decisions/ADR-0025-no-external-codebase-is-evidence.md) — no
external codebase is evidence for this project. Replaces the earlier position
from the same day, which excluded the material but left it cited.

## 9. Architectural concerns — raised, not changed

**The project's evidence base is now explicitly empty, and that is the honest
state.** Everything the corpus claimed to have validated was validated
elsewhere, by artefacts nobody here has read. Several decisions moved from
*evidenced* to *reasoned-only*. **None was invalidated** — each is supported by
an argument made in this repository — but the corpus no longer implies a head
start it does not have.

The second-order effect is that **no effort estimate in this project has a
basis.** Phase 1 has not been estimated, and any number offered for it would be
invented.

## 10. Open questions changed

**Corrected, not resolved:** Q2 and Q18 lose their evidence (both now read
"None"). Q4 collapses from three candidates to two — option (B) is struck
rather than re-lettered, so existing references to option (C) still resolve.
Q7's evidence is corrected for misattribution.

**Unchanged:** Q2 remains the only blocking decision. Q10 remains the most
under-designed area.

## 11. Risks

- **The condensed conversion may have dropped something.** Mitigated by
  salvaging the competitive research and the architecture's spine first, and by
  the 2,468 lines of `docs/project/` that already stated the design — but the
  binary is gone and this is not reversible from within the repository.
- **The guard names what it forbids.** One file, `provenance-denylist.txt`,
  necessarily contains the strings. It is machine configuration carrying no
  narrative, and it is the only such place. This is an irreducible tension, not
  an oversight.
- **"As if they never existed" is achievable for the working tree and for
  history, but not for anyone's memory of the old commits.** The claim this
  repository can honestly make is: *the material appears in no document
  describing what this project is or plans, and a test enforces it.*

## 12. History rewrite — done in this session

The branch history was rebuilt rather than filtered. Five commits were created
from `e849c8d` by checking out the final purged tree and staging it in path
groups, so no contaminated blob or commit message ever entered the new history.
The old objects were then unreferenced and collected
(`git reflog expire --expire=now --expire-unreachable=now --all`,
`git gc --prune=now`). The resulting tree was verified byte-identical to the
pre-rewrite tree.

This was safe only because nothing had been pushed. **Every SHA changed**, so
any clone or bundle taken before this point is stale and must be replaced
rather than merged.

## 13. Recommended next action

The substantive work is unchanged and unblocked: **Q2, the ladder meeting.** It
is still the only decision blocking Stage 0, and it still needs a named human
rather than a sprint.
