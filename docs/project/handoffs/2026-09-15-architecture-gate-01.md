# Session Handoff — 2026-09-15 — Architecture Gate 01: the provenance finding, corrected

**Started from commit:** `92fdd3a`
**Ended at commit:** *(this session's commit)*
**Branch:** `claude/repo-access-653473`

## 1. What I investigated

The owner directed that the previous session's headline finding — **ten of
twenty-eight ADRs cite a document that is not in this repository** — be run to
ground before any implementation. Specifically: verify the ten independently,
recover the claim-store migration, map domain to storage, establish what `kind`
and `source_class` actually mean, reopen Q7 honestly, audit cross-document
consistency, triage everything, and answer *are we ready to implement?*

**I re-derived every finding from the files rather than inheriting it from the
previous session's notes.** That turned out to matter.

## 2. What I changed

**New — four files:**
- `docs/project/19-recovered-architecture-evidence.md` (725 lines)
- `decisions/ADR-0032-provenance-of-the-2026-09-05-citations.md` — supersedes ADR-0029
- `decisions/ADR-0033-extraction-identity-is-observation-and-extractor-version.md` — resolves Q23
- **`tools/check_adr_citations.py`** — the fifth linter, and the first that checks citations

**Corrections:** `ADR-0029` status → SUPERSEDED, **body byte-identical** ·
`ADR-0012`'s Source citation · `18-…-execution-trace.md` §1.1 and §5.3 (dated
blocks, nothing removed) · `01-architecture-map.md` §4.1.

**Registrations:** `15-vocabulary.md` §4a · `10-open-questions.md` (Q23 resolved,
Q7 restated a third time, **Q24 added**) · `11-architecture-change-log.md` ·
`decisions/README.md` · `docs/project/README.md` **and** `PROJECT_BOOTSTRAP.md` §11.

## 3. What is now implemented

**Nothing.** Zero lines of product code exist. No status promoted; the diff adds
zero occurrences of `IMPLEMENTED`. No ADR's Decision section changed.

`tools/check_adr_citations.py` is a documentation linter beside the four that
already exist. It is repository hygiene, not product code, and ADR-0001 is
undisturbed.

## 4. What remains incomplete

- **Contracts were not written** — deferred by owner decision, recorded in doc 19
  §11 rather than silently omitted.
- **Q2, Q5, Q7's far side, Q10, Q11, Q15, Q16, Q24** remain open by design.
- **The commit is not pushed.** `git push` has returned 403 for every session on
  this branch. Delivery is by git bundle.

## 5. Tests run

```
python3 tools/check_provenance.py       # the only linter reaching docs/project/
python3 tools/check_xrefs.py
python3 tools/check_handbook.py
python3 tools/check_adr_citations.py    # NEW - every ## Source section number
ad-hoc internal-link sweep              # no tool exists in tools/; written per session
verbatim-quote diff: 41 quotations re-extracted from source and compared
git diff audits: status promotion - ADR-0029 body integrity - predicate vocabulary
```

## 6. Results

```
185 file(s): 0 provenance finding(s)
73 document(s), 51 chapter(s): 0 unresolved reference(s)
51 chapter(s): 0 error(s), 14 warning(s)
40 citation group(s) checked, 0 unresolved
1342 internal link(s): 0 broken

Quotations checked against source:  41, not verbatim: 0
Status promoted to IMPLEMENTED:      0
ADR-0029 body changed:               no (status line only)
Predicates outside Q5's seven:       none
```

**Two checks earned their place, and both found something.**

**The citation linter found ADR-0012** — whose `## Source` cites *"§13.1, §13.2"*
of a file with sections §0–§10. **A citation that fails against a readable file
is worse than one failing against an absent file**, because it looks checkable.
It survived the previous audit because that audit read the wrong field.

**The verbatim check caught me constructing quotations.** I had joined separate
table cells into sentence-shaped quotes — *"written by the running agent, dies
with the run"* — which is accurate in content and **does not appear anywhere in
the source.** Three instances, all split back into genuine cell quotations. Last
session the same check caught two silently-lowercased opening words. It has now
found a defect in both sessions it has run.

## 7. New discoveries

**The one that matters. The previous session's headline finding is overstated,
and I wrote it.** The ADR template carries **two** fields answering two
questions: `Date / context` (**attribution** — when and where a decision was
taken) and `## Source` (**evidence** — which artifact carries the reasoning).
**The 2026-09-05 string is in the attribution field. All ten ADRs name readable
artifacts in `## Source`** — nine name
`docs/architecture/organizational-brain-architecture.md`, which I read end to end
and which carries the substance of eight of them.

**The provenance concern is two ADRs, not ten.** ADR-0013 (its named source does
not discuss MCP at all) and ADR-0005 (the phrase *"world model"* does not occur in
its named source, though its Replay-test argument is readable and strong).

**Q23 is resolved, and it was resolvable all along.** `organizational-brain-architecture.md`
§7a states it outright: *"a deterministic id from `(observation_id,
extractor_version)`, made a UNIQUE key, and claimed **before** the model call
rather than after. **Retry is not replay.**"* Four readable, non-illustrative
sources agree. The one dissenter is `[ILLUSTRATIVE REFERENCE CODE]` scoped to
runtime memory.

**Q7's boundary was recovered from a section nobody had cited.** Memory §30.1,
**"The eight kinds of remembering, kept apart"**, marked `[CONFIRMED]`, separates
run memory from organizational knowledge as different categories with different
writers and lifetimes. **It sits one section from the DDL the previous session
quoted.** So ADR-0030 is corroborated by the source, not merely inferred from its
vocabulary — and the `decisions` table is marked *"PHASE 3, not the MVP"* and
*"HISTORY, and therefore not memory."*

**`source_class` occurs zero times in all nine `.docx`.** It has no schema
lineage. Its readable advocate is prose in §3 and §5 principle 1.

**`kind` names two different concepts.** Claim kind (six values, ADR-0003) and
evidence kind (seven values, *"Provenance kind"* at Memory §11.2). So our own
*"the recovered schema cannot express `kind`"* is true in substance and
misleading as written — that schema **has** a `kind` column, on the wrong table.

**My own checker was wrong on its first run.** It reported five failures; four
were its heading parser requiring `15 Title` where the source writes `15. Title`.
Each was verified by hand before anything was recorded. **A provenance checker is
an artifact with a provenance problem of its own**, and that limitation is written
into the script's docstring.

## 8. Architectural decisions

[ADR-0032](../decisions/ADR-0032-provenance-of-the-2026-09-05-citations.md) —
supersedes ADR-0029; narrows the finding from ten ADRs to two; downgrades no
status and reverses nothing.
[ADR-0033](../decisions/ADR-0033-extraction-identity-is-observation-and-extractor-version.md)
— extraction identity is `(observation_id, extractor_version)`; **resolves Q23**;
scopes ADR-0018 rather than editing it.

Both have change-log entries. **No existing ADR's Decision changed.**

## 9. Architectural concerns

**The A9 problem, and this time the arithmetic is better.** This session added
**one** document and **two** ADRs, where the previous added two and three. More
to the point, it **removed** an architectural concern rather than adding one:
eight ADRs stopped carrying a provenance cloud, one blocking question closed, and
Q7 lost most of its uncertainty. **That is the first session in this sequence
whose net effect on the architecture surface is negative.**

**The uncomfortable reading, again, and sharper.** The previous session's lesson
was *read what exists before writing more*. This session's is narrower and worse:
**the previous session read the files and still drew the wrong conclusion from
them**, because it read the wrong field of a template it had in front of it. The
binding constraint is not only retrieval — it is **checking the thing you are
about to assert against the artifact that would falsify it.**

**Still no code.** Three sessions, four documents, five ADRs, zero lines.
§10 of doc 19 says the remaining blockers are **decisions, not missing evidence**
— which means the next session has no excuse left.

## 10. Open questions

- **Q23 — RESOLVED.** ADR-0033. Moved to §4 of the register.
- **Q24 — new.** Where `source_class` lives. Not blocking ingestion; blocking the
  first reconciliation, behind Q2 anyway.
- **Q7 — restated a third time.** The boundary is settled; the far side is not.
  Its next experiment is **now executable**, unlike either previous version.
- **Q2, Q5** — unchanged and still blocking. Doc 19 §10 names them as two of the
  four conditions.
- **Q10, Q11, Q15, Q16** — unchanged.

## 11. Risks

- **ADR-0032 gets read as exonerating everything.** It does not. ADR-0013 has no
  readable advocate and ADR-0005's attribution is unverifiable; both stay
  ACCEPTED and both are now visible.
- **Doc 19 §10's "YES, WITH CONDITIONS" gets read as the gate passing.** It is
  not. The stop condition holds until the owner reviews this report.
- **The recovered DDL gets read as a decision.** Unchanged risk, unchanged
  mitigation: every quotation carries its author's `[ILLUSTRATIVE REFERENCE CODE]`
  label.
- **The citation linter gets trusted.** It was wrong on its first run and its
  docstring says so. It checks section *existence*, never whether the section
  supports the claim.
- **The commit is unpushed and this environment is ephemeral.**

## 12. Recommended next action

**Specify the observation record — fields, content hash, permission label,
bitemporal columns — and then write the redelivery test.**

Doc 19 §10 finds exactly one MUST-RESOLVE item: **Observation has no storage in
any recovered shape**, while ADR-0004 makes it the system of record. It is stage
1's own first deliverable, it cannot be retrofitted, and nothing is rebuildable
without it.

Then the test. `14-outside-in-review-2026-09-14.md:380-385` proposes *a test that
a redelivered observation produces one claim* as this project's first code. **Q23
was the only thing blocking it and Q23 is now closed.** The three remaining
conditions (Q5's predicate set; `kind` on the claim; `source_class` as a column
with no ordering) are decisions of a few hours, not investigations.

**The evidence work is done. What is left is deciding and building.**
