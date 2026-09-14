# Session Handoff — 2026-09-14 — The knowledge system traced; a provenance failure found

**Started from commit:** `05dd491`
**Ended at commit:** *(this session's commit)*
**Branch:** `claude/repo-access-653473`

## 1. What I investigated

- **How the knowledge system actually runs**, at the level of rows, constraints
  and indexes, rather than boundaries — the gap doc 16 leaves deliberately.
- **The `.docx` sources in `learning-notes/`, read as text for the first time.**
  `check_provenance.py:122` already reads them this way; no project document
  ever had. This turned out to be the session's most productive act.
- **The provenance of the ADR corpus** — specifically, whether the documents the
  ADRs cite as their basis exist.
- The retrieval, extraction, reconciliation, temporal and verification designs,
  re-derived from first principles and then checked against the accepted ADRs.

## 2. What I changed

**New — four files:**
- `docs/project/18-brain-mechanism-and-execution-trace.md` (1,600+ lines)
- `decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md`
- `decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md`
- `decisions/ADR-0031-the-phase-1-index-set.md`

**Corrections to verified defects:** `01-architecture-map.md` §4.1 (asserted a
contradiction between "two documents in this repository" when one is absent) ·
`PRD.md` §11.3 (a **FACT** label on an unverifiable claim) ·
`04-implementation-map.md` two rows (the Memory schema *does* have a migration;
the index set *does* exist).

**Registrations:** `01-architecture-map.md` §4.7 (a fourth claim-store shape) ·
`10-open-questions.md` Q7 **restated** and **Q23 added** · `docs/project/README.md`
and `PROJECT_BOOTSTRAP.md` §11 both updated — the previous session missed one of
these for doc 15 · `decisions/README.md` · `11-architecture-change-log.md`.

## 3. What is now implemented

**Nothing.** Zero lines of product code exist. No status label was promoted; the
diff adds zero occurrences of `IMPLEMENTED`. No existing ADR's Status or
Decision section changed.

## 4. What remains incomplete

- **Q7 is restated, not answered**, and the organizational claim store now has
  **no specified design and no readable advocate.** That is a more accurate and
  less comfortable position than the register previously described.
- **Q23 is new and blocking** the smallest thing on the board — see §12.
- **The entities / relations / contradiction-register question is reopened with
  no prior**, since its only recorded advocate cannot be read.
- **The commit is not pushed.** `git push` has returned 403 all session, as it
  has for every session on this branch. Delivery is by git bundle.

## 5. Tests run

```
python3 tools/check_provenance.py        # the only linter that reaches docs/project/
python3 tools/check_xrefs.py
python3 tools/check_handbook.py
ad-hoc internal-link sweep               # no tool exists in tools/; written per session
verbatim-quote diff: every quoted DDL line re-extracted from the .docx and
                     compared, rather than trusted from notes
git diff audits: status promotion - existing ADR Status/Decision lines -
                 predicate vocabulary - R/E namespace collision
```

## 6. Results

```
180 file(s): 0 provenance finding(s)
73 document(s), 51 chapter(s): 0 unresolved reference(s)
51 chapter(s): 0 error(s), 14 warning(s)
1287 internal link(s): 0 broken

SQL/comment lines checked against source: 34, not verbatim: 0
Status promoted to IMPLEMENTED:           0
Existing ADRs modified:                   none (index README +3 rows only)
Predicates used outside Q5's seven:       none
  (authentication_mechanism appears 4x, every one explaining it does NOT exist)
```

**The verbatim check earned its place.** It caught two real defects — quotations
where I had silently lowercased the source's opening word. Both were fixed. A
quotation that is 99% right is a quotation that is wrong, and nothing else in
the toolchain would have caught it.

## 7. New discoveries

**The one that matters. Ten of twenty-eight ADRs cite a document that is not in
this repository.** The *"knowledge system architecture review, 2026-09-05"* is
given as the basis of ADR-0001, 0002, 0003, 0004, 0005, 0006, 0009, 0012, 0013
and 0019 — most at section precision (§6.1, §5.3-5.4, §5.2, §13.1, §14, §17,
§20.2). Among them are the three that define **the core object, the system of
record, and the authority model.**

Verified four ways: the string occurs **once** in the entire Markdown corpus,
inside the table citing it; no `.docx` carries a 2026-09-05 date, while the
*other* column's 2026-09-02 matches its file metadata exactly; the file bearing
that title has sections 0-10 while citations run to §20.2; and
`git log --all --diff-filter=D` finds no deletion.

This collides directly with `docs/project/README.md:3` — *"The repository is the
source of truth; chat history is not."*

**Q7's stated method is not executable.** Its *Next experiment* is *"read both
§37 and §17.3 together and write one page reconciling them."* Half that input
does not exist. **Nobody had tried it.** That is a sharper result than an
answer would have been.

**A complete claim-store DDL existed and had never been read** — 5 enums, 6
tables, 8 indexes, with rationale in comments. The repository has been designing
around a **retrieval failure**, not an absence. `04-implementation-map.md`'s "no
index inventory" row was simply wrong.

**Much of the current design is visibly derived from it.** CS2's identity
constraint, ADR-0023's six temporal fields, PS4's version CAS, ADR-0011's
one-run-corroborates-once, the trust rule as a CHECK constraint, and ADR-0017's
deletion-route index all appear there with their reasons. That lineage was
nowhere recorded.

**But the recovered schema cannot express `kind` or `source_class`** — ADR-0003's
core object and ADR-0006's authority model, this project's two differentiators.
**And `07-brain-observability.md` §1's chain, written independently, requires
exactly those two columns plus an `extractor_version` the DDL spells
differently.** Three independent arrivals at the same delta.

**A fourth claim-store shape, registered nowhere.** `org_knowledge`, real DDL,
in a source this repository cites. It is heading/body-shaped with a surrogate
key — so contradictions **cannot collide** — and its `evidence_episodes int` is
an evidence count, which **EV1 forbids in terms.**

**Extraction identity is specified two incompatible ways** (Q23). ADR-0018 says
`(observation_id, extractor_version)`; the recovered DDL says
`hash(run_id, episode_seq, observation_digest)`. These key different things.

**The PRD's own best worked example misstates a date.** `PRD.md:554` records
`prd.md` as *"committed 2026-09-06"*; it enters the history on **2026-09-14**,
and 2026-09-06 is the document's self-attested date. That is precisely the
`observed_at` / `recorded_at` confusion bitemporality exists to prevent, made by
the document arguing for bitemporality. It supplied the trace's temporal example
on real data.

## 8. Architectural decisions

[ADR-0029](../decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md)
— a finding of fact; selects no schema, reverses nothing.
[ADR-0030](../decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md)
— the recovered schema scopes runtime memory, argued from its own vocabulary
rather than from the absent document's silence.
[ADR-0031](../decisions/ADR-0031-the-phase-1-index-set.md) — the index set,
recovered and ratified, with two entries marked as constraints rather than
lookups.

All three have change-log entries. No existing ADR changed.

## 9. Architectural concerns

**The A9 problem, honestly.** `14-outside-in-review-2026-09-14.md:456` lists
*"More architecture documents"* as the highest-prior failure mode, and the
previous session already added two documents and two ADRs into that path. **This
session added another document and three more ADRs.** Doc 18 is scoped as the
design input to one specific experiment and says so in §0, and §21 lists what a
reader still cannot execute — but the honest position is unchanged: **this
session produced no code, and the project still has none.**

**A stronger, uncomfortable reading.** The most valuable thing this session did
was **read files that were already here.** The DDL, the index set, the decision
table and the fourth schema were all sitting in `learning-notes/` in a format the
provenance linter has been parsing all along. That suggests the binding
constraint on this project has not been missing design — it has been **not
reading what exists before writing more.**

**Ten ADRs now carry a visible provenance gap.** Their reasoning is written out
and unaffected; what is unavailable is the source it was drawn from. Whether
that warrants any status change is the owner's call and this session did not
make it.

## 10. Open questions

- **Q23 — new, blocking.** Extraction identity, specified two ways. §12.
- **Q7 — restated.** Not two schemas in conflict: one absent source, one
  self-labelled illustrative, one with no columns, one unregistered.
- **Q2, Q5** — unchanged and still blocking. The trace shows exactly where each
  one stops the machine (§11.2, §6.2).
- **Q10, Q11, Q15, Q16** — unchanged; doc 18 §21 names which part of the
  mechanism each one leaves un-executable.

## 11. Risks

- **The recovered DDL gets read as a decision.** It is labelled
  `[ILLUSTRATIVE REFERENCE CODE]` by its own author, and doc 18 repeats that in
  every caption and ADR-0031 says it adopts seven index shapes and nothing else.
  A reader skimming §5.2's populated rows may still take them for a schema.
- **ADR-0029 gets read as an attack on ten ADRs.** It is a finding of fact and
  changes no status. But it is the kind of finding that invites over-correction.
- **The absent document may exist on someone's disk.** If so, producing it is
  the single most valuable thing anyone could add to this repository, and
  ADR-0029 says so.
- **The commit is unpushed and this environment is ephemeral.** If the bundle is
  not applied, the work is lost with the container.

## 12. Recommended next action

**Decide Q23 — what deterministic identity an extraction attempt has.**

It is the smallest open item and it blocks the largest: the one-week experiment
`14-outside-in-review-2026-09-14.md:380-385` proposes as this project's first
code is *a test that a redelivered observation produces one claim*, and **that
test cannot be written until this is chosen** — the two candidate identities
give different correct answers to it. X1 is one of the eight irreversible
properties, so it is also the cheapest thing on the board to get wrong.

An hour, not a day. Everything else can wait behind it.
