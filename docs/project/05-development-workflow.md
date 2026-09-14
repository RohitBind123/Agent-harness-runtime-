# Current Development Workflow

**Status:** this describes the workflow as it is **observably practised**,
reconstructed from git history and repository structure at the audit date. It
is not a proposal. Where the intended workflow differs from the observed one,
both are shown.

This document matters for two reasons. It tells a fresh session how work
actually gets done here. And it is the **specification of the first thing the
knowledge system will observe** — see `06-validation-strategy.md`.

---

## 1. The workflow, as practised

```
   HUMAN ENGINEERING DECISION
     -- scope, direction, constraints, what NOT to do
            |
            v
   CLAUDE CODE SESSION
     -- reads the repository first
     -- produces the artefact (document, research, analysis)
            |
            v
   VALIDATION
     -- repository tooling where it applies (linters, xref checker)
     -- primary-source verification for external claims
     -- visual/QA inspection for rendered artefacts
            |
            v
   GIT COMMIT
     -- one logical deliverable per commit
     -- descriptive subject line, imperative mood
            |
            v
   HUMAN REVIEW / CORRECTION
     -- in conversation, not in the repository
            |
            v
   PUSH  (currently BLOCKED -- see sec 5)
```

### What the git history actually shows

| Period | Author | Commits | Character |
|---|---|---|---|
| 2026-08-04 → 2026-08-16 | `RohitBind123` | ~25 | Handbook construction. Conventional-commit prefixes (`docs:`, `fix:`, `chore:`). Incremental: chapters added in batches, tooling added alongside |
| 2026-08-28 → 2026-09-07 | `Claude` | 18 | Architecture and learning deliverables. Plain imperative subjects. One deliverable per commit |

Both phases show the same shape: **a unit of work is a complete, reviewable
artefact**, not a partial edit. That is worth preserving, and it is what makes
the history legible as an observation stream.

### What is observably true about the practice

| Practice | Evidence |
|---|---|
| **Read before changing** | Every architecture document opens with an explicit account of what was read, and the knowledge system review's central finding came *from* that reading rather than from the brief |
| **Tooling enforces conventions** | `check_handbook.py` and `check_xrefs.py` are run and kept at zero errors; `tools/todo.md` lists them as standing obligations |
| **Claims are classified by provenance** | `[AHE]`, `[DAR]`, `[INF]`, `[BP]`, `[FUT]` markers, preserved across edits by an explicit contributing rule |
| **Findings are recorded, not resolved silently** | Findings A, B and C in the product research are carried forward across documents rather than quietly fixed |
| **External claims get verified against primary sources** | Commit `169142e` is an entire pass doing this, and it corrected two real errors |
| **Disagreement with the brief is surfaced** | Multiple documents explicitly list where they disagree with the instruction that commissioned them |

---

## 2. Where decisions actually get made

**Observed:** in conversation between a human and a Claude Code session, then
written into a document and committed.

**The gap this creates, and it is the reason this documentation set exists:**
until 2026-09-14 there was **no durable record of a decision separate from the
document that assumed it.** Rationale lived in prose inside a deliverable, or in
a conversation that is gone. `docs/project/decisions/` is the fix, and it works
only if it is maintained.

**The rule going forward:** a decision that changes what gets built is recorded
as an ADR **and** as an entry in `11-architecture-change-log.md`. Not in a
commit message, and not only in a deliverable.

---

## 3. What the workflow does NOT currently have

Recorded honestly, because the knowledge system is supposed to observe this workflow and
cannot observe what does not happen.

| Missing | Consequence |
|---|---|
| **Pull requests** | Work goes directly to a branch. There is no review artefact, no diff discussion, no approval record. **An entire class of observation the knowledge system design assumes — PR review comments — does not exist in this workflow today** |
| **CI** | No automated run of the linters on push. They are run manually and by convention |
| **An issue tracker** | `tasks/todo.md` is the only backlog, and it covers the handbook only. Nothing tracks product or knowledge system work |
| **Tests for product code** | There is no product code |
| **A changelog** | Until now |
| **A CLAUDE.md** | No session-startup instructions existed. `PROJECT_BOOTSTRAP.md` is that file's role |

**The PR gap is the most consequential**, and it bears directly on
`06-validation-strategy.md`: the knowledge system's strongest first source is Git/PRs,
because a merge is an implementation fact and a review is a decision with an
author. If the workflow does not produce PRs, that source is thin.

---

## 4. How to do a piece of work here

The sequence a session should follow, derived from what has worked:

1. **Read first.** The repository, then the specific documents the work touches.
   Do not assume the written architecture and any code agree.
2. **Classify what you find.** DESIGNED / IMPLEMENTED / PARTIALLY IMPLEMENTED / EXPERIMENTAL /
   PROPOSED / UNKNOWN. Never silently promote one to another.
3. **Surface contradictions rather than resolving them.** If two documents
   disagree, record both positions and open a question. Picking one silently is
   how a project loses the fact that it was ever contested.
4. **Say what you could not verify.** "Reported, not verified" is a complete and
   acceptable answer.
5. **Produce one complete artefact.** Not a partial edit spread over several
   commits.
6. **Run the tooling.** `check_handbook.py` and `check_xrefs.py` at zero errors;
   `check_provenance.py` at zero findings — **that one applies to every edit,
   not only chapter edits**; regenerate the generated appendices if chapters
   changed.
7. **Record decisions as ADRs and log the change.**
8. **Commit with a descriptive imperative subject.** One deliverable per commit.
9. **Write the handoff** — `12-session-handoff-protocol.md`. The repository is
   the state.

---

## 5. Operational state at the audit date

**Push to the remote is blocked, and it is not a code problem.**

At the audited commit there were **18 commits** on `claude/repo-access-653473`
not present on the remote. The cause is an authorization split:

- `git push` authenticates as the Claude GitHub App identity, which the
  organization has not granted → **403**.
- The MCP GitHub server authenticates as the user's own account and *can* write,
  but that API path cannot carry binary files or preserve commit authorship.

**Retrying does not fix it.** The remedies are: the organization grants the
GitHub App at `https://claude.ai/admin-settings/claude-tag`; or the user
reconnects their own GitHub authorization under claude.ai Settings → Connectors;
or the work is transferred as a git bundle, which needs no access change.

If a future session sees a non-empty `git log origin/<branch>..HEAD` and a 403
on push, this is that — and the session should say so rather than re-diagnosing
it.
