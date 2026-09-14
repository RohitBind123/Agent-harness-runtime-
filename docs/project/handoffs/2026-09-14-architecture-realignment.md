# Session Handoff — 2026-09-14 — Canonical identity realigned; architecture documented

**Started from commit:** `c011eb3`
**Ended at commit:** *(this session's commit)*
**Branch:** `claude/repo-access-653473`

## 1. What I investigated

- The repository's stated product identity, across `PROJECT_BOOTSTRAP.md`,
  `00-north-star.md`, `PRD.md` and `docs/product/`.
- **Where the "universal-runtime reference structure" actually is.** It is not a
  separate artefact: it is §7 of
  `docs/architecture/universal-runtime-v1.0-architecture-specification.md`
  (5,059 lines, revision 5), a ~2,000-line specified-not-built tree. Its §3
  (design rules), §5 (three loops), §10 (39 invariants), §11 (distributed
  runtime) and §13 (dependency rules) were read in full.
- **SurrealDB Agent Memory**, against its published documentation source
  (`github.com/surrealdb/docs.surrealdb.com`). **`surrealdb.com` itself is
  blocked by this session's egress proxy** — claims about commercial terms are
  search-index-derived, are labelled as such, and nothing rests on them.
- The full knowledge-plane invariant set (O1-O5 … CL1-CL4, PS1-PS4) and the
  runtime's 39, in order to answer Q8 rather than invent a parallel taxonomy.
- The guardrails: `tools/check_provenance.py`, its denylist, ADR-0025's three
  contamination classes, and the three labelling axes.

## 2. What I changed

**New — four files:**
- `docs/project/16-high-level-implementation-architecture.md`
- `docs/project/17-target-repository-structure.md`
- `decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md`
- `decisions/ADR-0028-the-knowledge-core-is-domain-agnostic.md`

**Identity:** `PROJECT_BOOTSTRAP.md` §2 and `00-north-star.md` §1 now state the
canonical identity. `00-north-star.md` §6's "general agent platform" row is
**narrowed, not retired** — its "pitching a hope" warning is kept verbatim.

**Supporting:** `PRD.md` §1 scope note · `08-build-order.md` new §3.1 (the phase
table itself untouched) · `09-do-not-assume.md` two rows · `10-open-questions.md`
Q7 widened, Q8/Q20 given a proposed artefact, Q22 added ·
`01-architecture-map.md` §4.3 updated and §4.5/§4.6 added ·
`15-vocabulary.md` §7 · `decisions/README.md` · `docs/project/README.md` ·
`docs/product/07-organizational-knowledge-landscape.md` §2 and §6 ·
`11-architecture-change-log.md` **two** entries.

**Seven defects fixed.** Four were mine, from commit `c011eb3` eight hours
earlier: `00-north-star.md:101` ("Business knowledge system" — a find-replace
across a line break), `PRD.md:74` ("An knowledge system"),
`docs/project/README.md:1` (titled "Project Knowledge System", colliding with
two other meanings of the phrase — retitled **Durable Project Context**), and
`15-vocabulary.md` missing from the `PROJECT_BOOTSTRAP.md` §11 map. One survived
the provenance purge: `01-architecture-map.md:250` cited *"an existing design
intent in the referenced (unverified) codebase"*, which dodged the guard because
the denylist matches `the (reference|working|existing) codebase` and this read
*"the referenced (unverified) codebase"*. Two predate both: a stale ADR-0021
reference in the root `README.md`, and a wrong `learning-notes/` file count.

## 3. What is now implemented

**Nothing.** Zero lines of product code exist. Every status label in every file
touched is unchanged; nothing was promoted.

## 4. What remains incomplete

- **The single-writer invariant profile is PROPOSED, not ratified.** Q8 and Q20
  stay open. Writing it was the experiment; accepting it is the decision, and
  that is the owner's.
- **Q7 is not only unresolved, it widened** — see §7.
- The two domain leaks named in ADR-0028 (claim `kind` enum values, `scope` as a
  materialised path inside claim identity) are **recorded, not fixed.** Both are
  schema decisions blocked behind Q7.
- **The commit is not pushed.** `git push` returns 403 for this session, as it
  has all session — delivery is by git bundle.

## 5. Tests run

```
python3 tools/check_provenance.py
python3 tools/check_xrefs.py
python3 tools/check_handbook.py
ad-hoc internal-link sweep (no tool exists in tools/; written per session)
git diff checks: status promotion · build-order table · ADR Status/Decision lines
grep audit: ADR-0025 class-3 modal forms in the four new files
```

## 6. Results

```
175 file(s): 0 provenance finding(s)
73 document(s), 51 chapter(s): 0 unresolved reference(s)
51 chapter(s): 0 error(s), 14 warning(s)
1237 internal link(s): 0 broken

=== Any status promoted to IMPLEMENTED? ===
  none
=== 08-build-order: does the phase table change? ===
 docs/project/08-build-order.md | 22 ++++++++++++++++++++++
 1 file changed, 22 insertions(+)
  no lines removed -> table untouched
=== Any existing ADR Status or Decision line changed? ===
  none
```

The class-3 modal audit returned 30 hits across the four new files; **every one
refers to an in-repo artefact** — the specification, the build order, an ADR,
the validation strategy — not to an outside system.

## 7. New discoveries

**The most important one, and it corrected my own plan.** I had written that the
Brain/Runtime dependency direction was *"already specified"*, citing the
specification §13's `knowledge ──X──> runtime`. **That is wrong, and it was
load-bearing.** §13's `knowledge/` is the **runtime's own** world-state and
memory tier (§8.15), not the Organizational Brain. ADR-0012 says so in a
consequence line: *"The knowledge system is placed as a **peer package**, not
inside the agent or the knowledge layer."* The plane rule is therefore a **new
decision**, and doc 16 §4.2 argues it from scratch rather than citing.

That correction surfaced **a third `entity_store` / `fact_store` shape** — the
specification's `knowledge/world/` ships `entity_store.py`, `entity_resolver.py`
and `fact_store.py`, the same nouns as the claim store, a third time. **No
document named this.** Registered as `01-architecture-map.md` §4.5 and folded
into Q7.

**The specification contradicts itself about `tools`.** §13's LAYERS block puts
`tools` below `runtime` (importable); its FORBIDDEN EDGES list bans
`runtime ──X──> tools`; design rule 4 sides with the ban. Two of three agree, so
the resolution is not in doubt — but the layer-stack diagram is the most quotable
of the three and is the wrong one. `01-architecture-map.md` §4.6.

**`packages/` cannot hold the domain split.** The runtime specification's §4.5
makes `evolution/` write to `packages/registry/` **and nowhere else**. Putting
the source-precedence policy there would place authority configuration inside
the evolvable surface, contradicting ADR-0006 and `02-domain-model.md` §2.10's
*"outside anything the agent may edit."* ADR-0028 uses three buckets instead of
two for exactly this reason.

**Q8's own hypotheses expected a different answer than the walk produced.** They
name leases, version-CAS, relay claims, sweepers, worker pools and budget
ledgers as candidates to drop; the walk drops **none of the 39**. The
reconciliation is that the hypotheses name **components** and the invariants are
mostly **properties**: 36 apply unchanged, 3 weaken, 0 drop. *Defer the
machinery, keep the shape.*

**`c011eb3` owed a change-log entry and a handoff and wrote neither.** Recorded
retrospectively rather than left absent.

**SurrealDB's scope check returns empty where ADR-0016 requires a raise** — and
their own docs name the resulting failure: *"the symptom is quiet: scoped reads
return empty, not refused, so a client that polls for its own writes waits
instead of failing."* ADR-0016's alternatives table rejected that design in
almost the same words. Two designs, same failure mode, opposite directions.

## 8. Architectural decisions

[ADR-0027](../decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md) —
general-purpose agent Brain + Runtime; Organizational Brain as first substrate.
[ADR-0028](../decisions/ADR-0028-the-knowledge-core-is-domain-agnostic.md) —
domain-agnostic knowledge core, three buckets, two named leaks.

Both have change-log entries. Neither changes any existing ADR's Status or
Decision.

## 9. Architectural concerns

**The one worth reading twice.** ADR-0027 makes the project easier to over-build.
`14-outside-in-review-2026-09-14.md` lists *"More architecture documents"* among
things not to build, because *"the most likely failure mode is not a wrong
architecture — it is a correct architecture, more of it, indefinitely."* **This
session added two architecture documents and two ADRs into exactly that failure
mode's path.** Doc 17 was deliberately cut short for this reason; doc 16 was not,
because the Q8 walk is content the repository has been explicitly waiting for.
The honest position: **this session produced no code, and the project still has
none.**

The two domain leaks are carried openly, which means a future reader will see an
enum that looks settled. Named in ADR-0028 and doc 17 §4 to make the cost visible
rather than latent.

## 10. Open questions

- **Q8 / Q20** — the profile exists and is unratified.
- **Q7** — widened to three schemas.
- **Q22** — new: adopt an existing agent-memory engine instead of building the
  claim store? Current assessment is build, on fit. Three named re-check
  triggers.
- **Q10** — unchanged, and now visibly load-bearing: `scope` sits inside claim
  identity while no complete permission model exists.

## 11. Risks

- **The profile in doc 16 §8.5 gets treated as ratified** because it is written
  down and detailed. It is marked PROPOSED in three places; that may not be
  enough.
- **The two registers ("Brain" the product, "the knowledge system" the
  subsystem) get collapsed again** by a future session reading only one
  document. `15-vocabulary.md` §7 exists to catch that.
- **The commit is unpushed and this environment is ephemeral.** Delivery is by
  bundle; if the bundle is not applied, the work is lost with the container.

## 12. Recommended next action

**Ratify or reject the single-writer invariant profile in
`16-high-level-implementation-architecture.md` §8.5.** It is the artefact Q8 and
Q20 have both been blocked on, both are marked blocking, and Q8 is blocking
*before line one of runtime code*. Reading it is an hour; the decision is the
owner's and nothing downstream should be built against it until it is made.
