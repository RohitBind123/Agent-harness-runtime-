# Vocabulary

**Why this document exists.** `docs/project/` was originally written against
learning-notes research material (Organizational Brain Architecture, Memory
Management Architecture, Principal Agent Architecture), and inherited that
material's invented names along with its ideas. On 2026-09-14 the project
owner asked for those names to be retired in favor of standard, industry-
recognized terminology — the way a principal engineer would document a real
system — with the handbook (`docs/handbook/`) as the one actual source of
truth for vocabulary where it already names a concept.

This document is the durable record of that pass: what changed, what didn't,
and why — so a future session checks here before coining another name rather
than reintroducing what was just retired.

**Scope note.** `docs/project/handoffs/` was deliberately left untouched.
Handoffs are a dated record of what a past session said, per
`12-session-handoff-protocol.md`'s "never edit a previous session's handoff" —
a vocabulary preference is not an error to correct, so the old names remain
there as history. Everywhere else in `docs/project/` and
`docs/architecture/organizational-brain-architecture.md` uses the vocabulary
below.

---

## 1. Renamed

| Was | Now | Why |
|---|---|---|
| "the Organizational Brain" / "the Brain" / "Business Brain" | **the knowledge system** | Two names for one referent, neither used consistently, both a rebrand rather than a description. A plain descriptive name, not a proper noun |
| "the authority ladder" / "source-class ladder" / "the ladder" | **the source-precedence policy** | Standard conflict-resolution/access-control vocabulary. Also frees the word "ladder" from a third, unrelated meaning — see §2 |
| "predicate registry" (used inconsistently for both the mechanism and its content) | **predicate schema registry** for the mechanism; **predicate vocabulary** kept for its content (the ~20 actual predicates) | Formalizes a split the corpus already gestured at but didn't hold consistently. "Schema registry" is recognized data-engineering vocabulary for this pattern |
| document-maturity **"PARTIAL"** (short form) | always **"PARTIALLY IMPLEMENTED"** | The short form collided with an unrelated handbook concept — see §3 |

## 2. Aligned to the handbook

The handbook already names these; docs/project now cites it instead of
treating them as fresh coinages.

| Concept | Handbook term | Where |
|---|---|---|
| The stage deciding whether an observation is worth processing | **Admission control** | Ch2, Ch23 |
| The confidence threshold below which a claim stays inert | **Load floor** | Ch12 — identical definition, previously uncredited |
| "Delete it; if information is lost, it wasn't a projection" | **Replay test** | Ch9 — covers both docs/project's "delete test" (one structure) and its "rebuild invariant" (the whole derived layer) |
| Participation staged through gated permission levels, each with a pre-registered threshold and automatic demotion | **Autonomy ladder** | Ch49 — the same staged/measured/demoted pattern, applied here to speaking rather than acting. **Kept as "ladder"/"rungs"**, not renamed, once the unrelated source-precedence "ladder" above was renamed away and the word became unambiguous again |
| A queryable projection of current state, rebuilt from durable facts | **Projection** / **Read model** | Ch6, Ch7, Ch9 — the general pattern the knowledge system's own World Model instantiates |

## 3. Kept as-is

Already standard industry vocabulary; renaming would make things worse.

| Term | Why |
|---|---|
| **Principal Agent** | "Principal-agent" is itself standard terminology (economics/governance). The one real issue is that it sits one word from the handbook's unrelated **Principal** (session identity) — resolved with a disambiguation note in `02-domain-model.md` §2.24 and `decisions/ADR-0014`, not a rename |
| **claim** / **kind-typed claim** / **kind** | "Claim" is standard claims-based-identity/KR vocabulary; "kind" as a formal type tag is literally type-theory terminology |
| **observation log** | Deliberately not "event log" — an observation is pre-validation; the handbook's own "Event" means already-true. Renaming would destroy that distinction and collide with the handbook's Event/Fact discipline. (The corpus's substantive divergence from the handbook here — ADR-0004 makes this log authoritative for durable fact, where the handbook's R20 forbids that — is a design question, not a naming one, and is unchanged by this pass) |
| **entity resolution**, **the claim store**, **capability layer**, **bitemporal validity**, **evidence handle**, **tool projection** | Each already standard, or as plain as a name gets |

## 4. Fixed as an inconsistency, not renamed

| Bug | Fix |
|---|---|
| "World Model" (most files) vs. "WorldState" (`02-domain-model.md` §2.17) — one object, two names | Consolidated on **World Model** |
| ADR-0003's six-kind labels ("Constraint / policy") vs. `02-domain-model.md`'s compact `kind` field ("constraint") | Not actually a conflict — one is prose, one is a schema enum value. Cross-referenced explicitly instead of forced to match verbatim |

## 4a. One word, two domain concepts — `kind`

**Registered 2026-09-15 (Architecture Gate 01).** Unlike the row above, this one
**is** a real collision: two different domain concepts share a word across two
documents, and it becomes a schema hazard the moment both appear in one migration.

| | **Claim kind** | **Evidence kind** |
|---|---|---|
| **Where** | [ADR-0003](decisions/ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md); `02-domain-model.md` §2.3 | `memory_evidence.kind` in the recovered DDL; called **"Provenance kind"** at `learning-notes/Memory Management Architecture.docx` §11.2 |
| **Values** | `observation-backed`, `decision`, `implementation-fact`, `outcome`, `constraint`, `term` — **six** | `run`, `step`, `activity`, `document`, `probe`, `human`, `policy` — **seven** |
| **Answers** | *What does this claim have authority over?* | *What shape of thing is this evidence?* |
| **Enforced by** | `memory_predicates.kinds_allowed` | Nothing — it is descriptive |

**Ruling.** Unqualified **`kind` means claim kind.** It is the core object's
defining property and the project's stated differentiator. Evidence kind is
**always written qualified** — `evidence_kind`, or `memory_evidence.kind` when
quoting the recovered DDL.

**A consequence worth stating**, because two of our own documents got it slightly
wrong: *"the recovered schema cannot express `kind`"*
([ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md),
`18-brain-mechanism-and-execution-trace.md` §5.3) is true in substance and
misleading as written — that schema **does** have a column named `kind`, on the
wrong table, meaning something else. The precise form is **"no claim-kind column
on `memory_claims`"**. Both documents now carry the correction. See
[`19-recovered-architecture-evidence.md`](19-recovered-architecture-evidence.md) §5.

**Not to be confused with** `source_class` (position in an authored precedence
ordering), `memory_origin` (`run|human|evolve` — who produced it), or
`trust_label` (`trusted|semi_trusted|untrusted` — a safety property). Four
distinct concepts; doc 19 §6.1 tabulates all of them.

## 5. Sequenced, not renamed

**"contradiction register" vs. "conflicts table"** sits on top of an
unresolved design disagreement (Q7/D4: one merged store or two), not two
labels for one settled thing. Naming stays open until that's decided; the
candidates on file are **"conflict register"** or **"conflict log"**.

## 6. Epistemic-status tags — closed vocabulary

Previously 7–8 undefined ADR-only bracket-tag variants, plus a separately-
defined PRD/review scheme, never reconciled. Now one closed set, defined in
`PROJECT_BOOTSTRAP.md` §0:

**FACT · EVIDENCE · INFERENCE · DESIGN DECISION · HYPOTHESIS · REQUIREMENT ·
RECOMMENDATION**

This is a different axis from the six DESIGNED/IMPLEMENTED/…/UNKNOWN status
labels (does a thing exist) and from the handbook's `[AHE]`/`[DAR]`/`[INF]`/
`[BP]`/`[FUT]` (where a claim came from). All three axes are in use and none
substitutes for another.

## 7. "Brain" and "the knowledge system" — two registers, not a contradiction

Added 2026-09-14, after
[ADR-0027](decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md)
made the canonical product identity a **general-purpose agent Brain + Runtime**.
Read carelessly that looks like a reversal of §1's rename. It is not, and this
section exists so nobody re-litigates it.

| Register | Term | Where it is used |
|---|---|---|
| **Product identity** | **general-purpose agent Brain + Runtime** | `PROJECT_BOOTSTRAP.md` §2, `00-north-star.md` §1, ADR-0027. The sentence a person says about what this is |
| **Current substrate** | **Organizational Brain** | Named as the *first* substrate and proving ground — never as the system's definition |
| **Engineering subsystem** | **the knowledge system** · **the runtime** · **Principal Agent** · **environment adapters** · **capability layer** | Every ADR, the architecture map, the domain model, docs 16-17 |

**Nothing from §1 is reverted.** "The Organizational Brain" is still not the
subsystem's name; "the knowledge system" still is. What changed is that the
project acquired a product-level name it did not previously have, and the two
live at different distances from the code.

**A collision this pass introduced, and has now fixed.** §1's rename left
"knowledge system" naming three things: the product, the subsystem, and
*this documentation set* (`docs/project/README.md` was titled "Project Knowledge
System"). The documentation set was the intruder and has been retitled **Durable
Project Context**.

**Identifier surfaces still carry the retired name.** `brain.claim.written`,
`brain.contradiction.detected`, `brain.claim.superseded`, and the field names
`brain_scope` / `brain_query` appear in `01-architecture-map.md` and
`07-brain-observability.md`. They are **not** renamed, because renaming an event
taxonomy is a design change and not a vocabulary fix. **Rename them when the
event taxonomy is first written — nothing consumes them today.** The same
applies to filenames that carry the old slug (`07-brain-observability.md`, three
ADR filenames): a file rename breaks every existing cross-reference for no
gain while the corpus is the only consumer.
