# Recovered Architecture Evidence — Architecture Gate 01

**Status:** **RECOVERED EVIDENCE.** This document reports what the repository
can and cannot establish. It decides two things (§2.6, §5.5) and deliberately
decides nothing else.

**Date:** 2026-09-15. **Supersedes no document.** Corrects two.

---

## 0. What this is, and what it is not

**This is not the missing document.** The *"knowledge system architecture
review, 2026-09-05"* is cited by ten ADRs and is not in this repository in any
form. Nothing here reconstructs it, stands in for it, or should ever be cited as
though it were it. Per the recovery policy this session was given, three
categories are kept apart and never merged:

| Category | Meaning | This document |
|---|---|---|
| **HISTORICAL SOURCE** | A document that existed and is now missing | **Never recreated.** §2 states precisely what rested on it |
| **RECOVERED EVIDENCE** | Reconstructed from surviving artifacts — learning notes, ADRs, existing architecture documents, git history | **This is that.** Everything in §§1–9 |
| **CURRENT SYNTHESIS** | A new architecture document consolidating verified decisions | **Not produced this session**, by owner decision. See §11 |

### 0.1 The scorecard

The standing objection to any new document here is
`14-outside-in-review-2026-09-14.md:456`, which lists *"More architecture
documents"* under what should **not** be built, and :374 — *"The most likely
failure mode is not a wrong architecture. It is a correct architecture, more of
it, indefinitely."* This document clears that bar only if it **removes** more
than it adds.

| # | What this gate did | Direction | Where |
|---|---|---|---|
| **1** | **Retired a false alarm.** The finding that ten ADRs rest on an absent document is **overstated**. All ten name readable Sources | **Removes** an architectural concern | §2 |
| **2** | **Found the real defect**, which is one ADR, not ten — and is worse in kind, because it fails against a file that *can* be read | Replaces a large vague worry with a small exact one | §2.5 |
| **3** | **Resolved Q23**, the smallest blocking question on the board, on four concordant readable sources | **Unblocks** the project's proposed first code | §5.5 |
| **4** | **Recovered the Memory/organizational boundary**, stated outright in a readable source nobody had cited for it | **Removes** most of Q7's supposed uncertainty | §7 |
| **5** | **Established `kind` and `source_class` semantics** from primary text, and corrected an imprecise statement in two of our own documents | Corrects | §5, §6 |
| **6** | **Mechanised the citation check** — 34 citation groups across 33 ADRs, now re-runnable | Adds a check, not a document | §2.5 |
| **7** | **Triaged every finding.** Most land in DOCUMENTATION-ONLY | Prevents this becoming a programme | §9 |

**Net: this gate closes more than it opens.** It resolves one blocking question,
downgrades one alarm, and opens one narrow question (§6.5). It writes **two**
ADRs where the previous session wrote three.

### 0.2 What this document does not do

- **It does not write contracts.** Brief §11 was deferred by owner decision (§11).
- **It does not decide Q2, Q5, Q7, Q10, Q11, Q15 or Q16.** Each is named where
  it stops the machine.
- **It does not promote any status.** Zero product code exists; this session
  writes none.
- **It does not modify the recovered migration.** It is quoted, never edited, and
  every quotation carries its author's own `[ILLUSTRATIVE REFERENCE CODE]` label.

---

## 1. The source-of-truth chain

### 1.1 The ordering this gate used

```
  repository artifacts          a file in this repo, readable now
        >
  explicit current decisions    ADRs with ACCEPTED status
        >
  historical notes              learning-notes/*.docx
        >
  model inference               anything I derived
```

**Chat history was not used as an architectural source**, per
`docs/project/README.md:3` — *"The repository is the source of truth; chat
history is not."*

One consequence is worth stating because it bit the previous session: a
**`.docx` in `learning-notes/` is a repository artifact**, not a historical
note, when it is readable. `tools/check_provenance.py:122` has been parsing
these all along. Reading them is retrieval, not recovery.

### 1.2 The distinction the previous session missed

The ADR template (`decisions/README.md`) carries **two different fields** that
answer two different questions:

| Field | Question it answers | Epistemic weight |
|---|---|---|
| **`Date / context`** | *When and in what setting was this decided?* | **Attribution.** It records a meeting, a session, a research pass. It is not required to resolve to a file |
| **`## Source`** | *Which artifact carries the reasoning?* | **Evidence.** This is what ADR-0025 governs |

**The 2026-09-05 string appears in the `Date / context` field.** Every one of the
ten ADRs names a **readable** artifact in its `## Source` field. Conflating the
two is what produced the overstated finding, and §2 is the correction.

### 1.3 The provenance matrix

Statuses: **VERIFIED** (the named artifact is readable and carries the claim) ·
**PARTIALLY VERIFIED** (reasoning readable, attribution unverifiable, or
substance present without the cited section) · **UNVERIFIABLE** (rests solely on
the absent document) · **CONTRADICTED** · **INFERRED** · **OBSOLETE**.

| Architectural claim | Source document | Exact section | Evidence type | Status |
|---|---|---|---|---|
| The repository is a knowledge base, not an implementation | `docs/product/06-mvp-and-implementation-strategy.md`; `docs/product/01-architecture-understanding.md` | §8.1; Finding 0 | Repository artifact | **VERIFIED** |
| The specification's vocabulary is canonical for code | `docs/product/01-architecture-understanding.md`; `docs/architecture/organizational-brain-architecture.md` | Finding A; §1 | Repository artifact | **VERIFIED** |
| The core object is a kind-typed claim | `docs/architecture/organizational-brain-architecture.md` | §5 principle 3; §4 row 9; §2 property 4 | Repository artifact | **VERIFIED** (substance); cited §6.1 **UNVERIFIABLE** |
| The observation log is the system of record | `docs/architecture/organizational-brain-architecture.md` | §2 property 1; §5 principle 10 | Repository artifact | **PARTIALLY VERIFIED** — admission-before-extraction is explicit; *system of record* is not stated in those words |
| The world model is a projection, not a store | `docs/architecture/organizational-brain-architecture.md` | — | **Derivation** | **PARTIALLY VERIFIED** — see §2.4. The phrase *"world model"* **does not occur** in the named source |
| Authority is authored configuration, never inferred | `docs/architecture/organizational-brain-architecture.md` | §3 (whole); §5 principle 1; §2 property 2 | Repository artifact | **VERIFIED** — the strongest of the ten |
| No graph database | `learning-notes/Memory Management Architecture.docx`; `docs/architecture/organizational-brain-architecture.md` | §16.5, §37.3 (ADR 13); §4 row 5 | Historical note + repository artifact | **VERIFIED** |
| The agent reaches the knowledge system only through tools | `docs/architecture/organizational-brain-architecture.md` | §6 row 2 | Repository artifact | **PARTIALLY VERIFIED** — substance present at §6; **the ADR's own cited §13.1/§13.2 do not exist in that file.** §2.5 |
| MCP is a projection of the capability layer | `docs/architecture/organizational-brain-architecture.md` | — | Attribution only | **UNVERIFIABLE** — MCP is not discussed in the named source. §2.4 |
| One source end to end before breadth | `docs/architecture/organizational-brain-architecture.md`; `08-build-order.md` | §8 row 4; stage 1 | Repository artifact | **VERIFIED** |
| An extraction attempt's identity is `(observation_id, extractor_version)` | `docs/architecture/organizational-brain-architecture.md`; `02-domain-model.md`; `07-brain-observability.md` | §7a; §2.2; §1 | Repository artifact ×3 | **VERIFIED** — §5.5 |
| `source_class` is a two-axis authored ranking | `docs/architecture/organizational-brain-architecture.md`; `02-domain-model.md` | §3, §5 principle 1; §2.10 | Repository artifact | **VERIFIED** as a concept; **UNAUTHORED** as content (Q2) |
| The claim store's tables, indexes and constraints | `learning-notes/Memory Management Architecture.docx` | §17.1–§17.6 | Historical note, **self-labelled illustrative** | **VERIFIED as an illustration**; not a ratified schema |
| Memory and organizational knowledge are different subsystems | `learning-notes/Memory Management Architecture.docx` | §30.1 | Historical note, `[CONFIRMED]` by its author | **VERIFIED** — §7 |

---

## 2. The ten-ADR provenance audit

### 2.1 The list, verified independently

`grep -rn "2026-09-05" --include=*.md .` over the whole repository returns the
citation in exactly ten ADRs: **0001, 0002, 0003, 0004, 0005, 0006, 0009, 0012,
0013, 0019.** The previously recorded list is **confirmed** — no ADR was missed
and none was wrongly included.

Two other 2026-09-05 hits exist and are unrelated:
`docs/product/07-organizational-knowledge-landscape.md` is external market
research *conducted* that day and **is in the repository.** That a different
2026-09-05 artifact survives is worth noting: the date is real, and the working
session it names plainly happened.

### 2.2 The corrected finding

**[FACT — in this repository]** All ten ADRs carry a `## Source` field naming
artifacts present in this repository:

| Source named | ADRs |
|---|---|
| `docs/architecture/organizational-brain-architecture.md` | 0003, 0004, 0005, 0006, 0012, 0013, 0019 — and, alongside other sources, 0002 and 0009 |
| `docs/product/*.md` | 0001, 0002 |
| `learning-notes/Memory Management Architecture.docx` | 0009 |

**So the accurate statement is not** *"ten ADRs rest on a document that is not in
this repository."* It is:

> **Ten ADRs attribute their decision to a working session whose record is
> absent, while naming readable artifacts for their substance.** The absent
> document's *section numbering* is unverifiable. Its *content* is, in eight of
> ten cases, independently present in a file anyone can open.

This matters practically. Under the overstated reading, ten accepted decisions
carry a provenance cloud and the natural response is to re-litigate all of them.
Under the verified reading, **two** need attention and the other eight are
ordinary well-sourced ADRs whose date line points at a meeting rather than a
file.

### 2.3 The audit, per ADR

Ten steps were run on each: exact citation · decision · what the absent document
supposedly established · independent repository evidence · learning-notes
evidence · migration evidence · implementation-map evidence · later superseding
ADRs · still active? · provenance status.

| ADR | Decision | Independent readable evidence | Active? | Status |
|---|---|---|---|---|
| **0001** | The repository is a knowledge base, not an implementation | `docs/product/01-architecture-understanding.md:28` — *"Finding 0 — there is nothing to extend."* Plus `organizational-brain-architecture.md` §0 last row and §1 | Yes. Reinforced by ADR-0025 | **VERIFIED.** The 2026-09-05 line says only that the finding was *restated* there |
| **0002** | The specification's vocabulary is canonical for code | `organizational-brain-architecture.md` §1 (present, and the ADR cites §1, which resolves) | Yes | **VERIFIED.** Its date line already says *"Assumed … Never confirmed by a decision"* — the ADR was honest about this from the start |
| **0003** | The core object is a kind-typed claim, six kinds | §5 principle 3 — *"A claim carries its kind, and the kind bounds what it can answer"*; §4 row 9 — *"Decision, Implementation and Outcome as distinct kinds"*; §2 property 4. The enum is spelled at `02-domain-model.md` §2.3 | Yes | **VERIFIED** in substance. §6.1 unverifiable and unnecessary |
| **0004** | The observation log is the system of record | §5 principle 10 *"Admission before extraction"*; §2 property 1. The rebuild invariant appears in `08-build-order.md:266` and `PRD.md:1260` | Yes | **PARTIALLY VERIFIED.** The *log-as-system-of-record* framing is not stated in those words in any readable source. Its consequences are, repeatedly |
| **0005** | The world model is a projection, not a store | **None in the named source.** The string *"world model"* does not occur in `organizational-brain-architecture.md`. The ADR's own reasoning cites the handbook's **Replay test (Ch9)** and ADR-0004, both readable | Yes | **PARTIALLY VERIFIED — the weakest of the ten.** Reasoning readable; attribution unverifiable. §2.4 |
| **0006** | Authority is authored configuration, never inferred | §3 in full — the three-places argument and its rejection of inference — plus §5 principle 1 and §5.1's *"Principle 1 will be attacked first"* | Yes, **ACCEPTED — UNEXECUTED** (Q2) | **VERIFIED.** The best-sourced of the ten |
| **0009** | No graph database | Memory `.docx` §16.5 and §37.3 (ADR 13) — both resolve — plus §4 row 5 of the readable file | Yes | **VERIFIED**, and it never depended on the absent document: it cites 2026-09-02 first |
| **0012** | The agent reaches the knowledge system only through tools | §6 row 2 — *"Tool projection, curried with the Principal at build time … Every containment argument rests on this"* | Yes | **PARTIALLY VERIFIED.** Substance present; **its own Source field cites sections that do not exist.** §2.5 |
| **0013** | MCP is a projection of the capability layer | **None.** MCP is not mentioned anywhere in the named source | Yes | **UNVERIFIABLE.** The named Source does not carry this claim. §2.4 |
| **0019** | One source end to end before breadth | §8 row 4 — *"the one most worth testing early"* — and `08-build-order.md` stage 1, which operationalises it | Yes | **VERIFIED** |

### 2.4 Where the absent document actually did work

**Two ADRs, not ten.**

- **ADR-0013 (MCP is a projection of the capability layer) — UNVERIFIABLE.** Its
  `## Source` names `organizational-brain-architecture.md`, which **does not
  discuss MCP at all.** This is the one ADR in the ten whose substance has no
  readable advocate anywhere. It remains ACCEPTED and nothing in this gate
  disturbs it — but it should be understood as resting on attribution, and
  `10-open-questions.md` **Q9** ("Whose Principal is an MCP caller?") is already
  open next door to it.
- **ADR-0005 (the world model is a projection) — PARTIALLY VERIFIED.** Its core
  proposition is absent from the named source, but its *argument* is readable and
  strong: the Replay test applied to one structure at a time. A decision whose
  reasoning you can check is not in the same condition as one whose reasoning you
  cannot.

**Neither is downgraded by this gate.** Recording provenance precisely is not the
same as reversing a decision, and §9 triages both as DOCUMENTATION-ONLY.

### 2.5 The defect the previous audit could not see

**[FACT — in this repository]** `ADR-0012`'s `## Source` field reads:

> `../../architecture/organizational-brain-architecture.md` (G), §13.1, §13.2.

**That file has sections §0–§10** (plus §5.1 and §7a). **§13.1 and §13.2 do not
exist in it.** The same numbers appear in the ADR's `Date / context` line, which
attributes them to the absent document — so the most economical reading is that
the absent document's section numbers were carried into a Source field pointing
at a different file.

**This is worse in kind than the finding it replaces.** A citation to an absent
document is honestly unverifiable. A citation to a **readable** document that
does not contain the cited section is a citation that *looks* checkable and
silently is not. It survived the previous audit because that audit read the
`Date / context` field.

**The check is now mechanical.** A script walks every `## Source` field in all 33
ADRs, resolves each named file, parses its headings, and reports any cited
section that does not exist:

```
34 citation group(s) checked, 1 not fully resolved
ADR-0012  organizational-brain-architecture.md   UNRESOLVED: §13.1, §13.2
```

**Every other citation in the ADR corpus resolves.** That is a materially
healthier result than the corpus was credited with, and it is now re-runnable
rather than a one-off reading.

> **A note on this check's own reliability.** Its first run flagged **five**
> failures. Four were false — §15, §21, §29, §31 and §38 of the Memory document
> all exist; the heading parser required `15 Title` and the source writes
> `15. Title`. The four were verified individually against the document before
> anything was written down. **A checker is an artifact with a provenance
> problem of its own**, and this one was wrong on its first run.

### 2.6 What this gate decides about the ten

[ADR-0032](decisions/ADR-0032-provenance-of-the-2026-09-05-citations.md)
supersedes ADR-0029 and records the corrected finding. ADR-0029's text is
preserved untouched and its status set to SUPERSEDED — the error stays visible,
per the change discipline this session was given.

---

## 3. The recovered migration inventory

**Source:** `learning-notes/Memory Management Architecture.docx` §17, headed by
its author:

> `SQL - storage/postgres/migrations/0018_create_memory.sql  [ILLUSTRATIVE REFERENCE CODE]`

**That label is the author's, appears seven times in the document, and governs
everything in this section.** This is an illustration of a design, not a ratified
schema. Nothing here is adopted by quoting it. It is **not modified.**

### 3.1 Enums

| Enum | Values | Problem it solves | ADR | Current concept | Valid? | Status |
|---|---|---|---|---|---|---|
| `memory_claim_state` | `provisional`, `active`, `retired` | Standing is earned, not granted on arrival | ADR-0011 | Claim `status` — but the current model has **four** (PROVISIONAL/ACTIVE/SUPERSEDED/RETIRED) | Partly — **`superseded` is missing** | Documented only |
| `memory_origin` | `run`, `human`, `evolve` | Who produced the claim | ADR-0024 | No current equivalent. **These are runtime-lifecycle categories** (§7) | Yes, for runtime memory | Documented only |
| `memory_proposal_state` | `claimed`, `applied`, `rejected`, `abandoned` | The write-path audit | ADR-0018 | Proposal `status` — current model says `PENDING → APPLIED\|REJECTED\|DUPLICATE` | **Conflicts**: `claimed` vs `PENDING`, `abandoned` vs `DUPLICATE` | Documented only |
| `memory_time_tier` | `exact`, `attested`, `inferred` | How well the valid time is known | ADR-0023 | `observed_at_tier` | Yes | Documented only |
| `trust_label` | `trusted`, `semi_trusted`, `untrusted` | Poisoning containment | — | No current equivalent; **not** `source_class` (§6.2) | Yes | Documented only |

### 3.2 Tables

| Table | Purpose, in its own words | The query forcing it | Current concept | Status |
|---|---|---|---|---|
| `memory_claims` | *"Current state, one row per claim identity."* | *"R1 — retrieve every active claim in a scope path, on the hot path. A fold over history cannot serve this"* | Claim (`02-domain-model.md` §2.3) | Documented |
| `memory_claim_versions` | *"Append-only history."* | *"R4 — 'what did we believe at time T'"* | ClaimVersion §2.4 | Documented |
| `memory_evidence` | *"Which runs and steps support a claim."* | *"R5 — find every claim citing a departing tenant's runs. A COUNT column cannot be joined on"* | Evidence §2.5 | Documented |
| `memory_proposals` | *"Idempotency for the write path, and the audit of rejections."* | The at-least-once dedup at §15.3 | Proposal §2.2 | Documented |
| `memory_predicates` | *"The controlled vocabulary and each predicate's cardinality."* Explicitly *"configuration, not memory data"* | §14.2 step 4 | Predicate §2.9 | Documented |
| `decisions` | §30.3, and explicitly **"PHASE 3, not the MVP"** | *"why did we decide to use PostgreSQL?"* vs *"where does PostgreSQL appear in our documents?"* | Decision §2.12, marked **BLOCKED** | Documented |

> **R1/R4/R5 here are the Memory document's own retrieval codes.** They are a
> third namespace, distinct from the knowledge-plane **R1–R4** (retrieval) and
> the handbook **R1–R22** (runtime). Qualified on every use.

**What has no table, in any recovered shape: Entity, Relationship,
Contradiction.** Their only recorded advocate was the absent document. §4 states
what follows.

### 3.3 Indexes

Six in §17, plus the two on `decisions` in §30.3. Seven were ratified by
[ADR-0031](decisions/ADR-0031-the-phase-1-index-set.md) last session; this gate
re-verified the extraction and changes nothing.

| Index | On | Rationale, quoted | Adopted? |
|---|---|---|---|
| `memory_claims_retrieval` | `(tenant_id, scope_path, recorded_at) WHERE state = 'active'` | *"R1, the hot-path query"* | Yes |
| `memory_claims_curation` | — | Serves a decay sweep | **No** — ADR-0031 excludes it; the sweep is unauthorised under ADR-0024 |
| `memory_versions_asof` | `(claim_id, recorded_at DESC)` | As-of reads | Yes |
| `memory_evidence_by_run` | `(tenant_id, run_id)` | *"Ch 37 sec 5.4's deletion route. Without this index, deleting a tenant's runs cannot find the claims that cite them"* | Yes — ADR-0017 |
| `memory_proposals_expiry` | — | Reclaiming abandoned claims | Yes |
| `memory_proposals_signals` | — | Rejection-rate-by-reason | Yes |

### 3.4 Constraints, uniqueness, CAS and temporal

| Item | Recovered form | What it solves | Current invariant |
|---|---|---|---|
| **Claim identity** | `UNIQUE (tenant_id, scope_path, subject, predicate)`, commented *"The OBJECT is deliberately NOT part of the identity"* | A contradiction becomes a **key collision**, not two rows that both retrieve | **CS2**, verbatim in intent |
| **Trust rule** | `CHECK (trust <> 'untrusted' OR state <> 'active')` | Poisoning containment as a structural fact | `08-build-order.md:196`'s *"trust rule as a CHECK constraint"* |
| **One run corroborates once** | `UNIQUE (claim_id, run_id, step_seq)` | *"a run cannot corroborate itself by observing twice"* | ADR-0011 |
| **Version CAS** | `version int NOT NULL DEFAULT 1` — *"A stale writer's UPDATE affects zero rows"* | Lost-update detection | **PS4** |
| **Two `version`s** | §17.4: `memory_claims.version` is *"a concurrency token"*; `memory_claim_versions.version` is *"an audit coordinate"* | *"conflating them is a real bug"* | Not recorded anywhere in `docs/project/` until now |
| **Six temporal fields** | `observed_at`, `observed_at_tier`, `observed_at_seq`, `recorded_at`, `last_confirmed`, `superseded_at` — headed *"TEMPORAL (sec 12). Six fields, three timelines"* | Bitemporality plus decay origin | **ADR-0023's six fields** |
| **Extraction identity** | `memory_proposals.proposal_id` = `hash(run_id, episode_seq, observation_digest)` | Idempotent write path | **Conflicts with ADR-0018.** Resolved at §5.5 |
| **Deletion route** | Retirement sets state; deletion removes the row and cascades — *"Both routes exist and they are different operations"* | Tenant offboarding | ADR-0017 |
| **Tenant isolation** | `tenant_id NOT NULL` + FK + RLS + repository-layer RAISE | §17.5: *"RLS filters. Chapter 37 requires raising"* | **ADR-0016** — and the recovered text argues the same two-layer point the ADR does |

### 3.5 The lineage that was never recorded

**[EVIDENCE]** Seven current invariants appear in this illustration **with their
reasons**, predating the documents that state them: CS2, ADR-0023's six fields,
PS4, ADR-0011, ADR-0016's raise-don't-filter, ADR-0017's deletion route, and
Stage 1's CHECK-constraint trust rule.

**The repository has been designing around a retrieval failure, not an absence.**
That is the same lesson the previous session reached, and it holds after
re-verification.

---

## 4. Domain ↔ storage mapping

**The four-way split matters more than the verdicts.** A domain concept does not
require a physical table, and treating one-concept-one-table as the default is
how a projection silently becomes a second source of truth.

| Concept | Recovered storage | Classification | Should it have a table? |
|---|---|---|---|
| **Observation** | **None.** No observation table exists in any recovered shape | **NOT REPRESENTED** | **Yes — and this is the largest gap.** ADR-0004 makes it the system of record; nothing stores it |
| **Proposal** | `memory_proposals` | **CONFLICTING** — the identity formula differs from ADR-0018 (§5.5) and the state enum differs (§3.1) | Yes — STORAGE RECORD |
| **Claim** | `memory_claims` | **DIRECTLY REPRESENTED**, minus `kind` and `source_class` | Yes — STORAGE RECORD |
| **ClaimVersion** | `memory_claim_versions` | **DIRECTLY REPRESENTED** | Yes — STORAGE RECORD |
| **Evidence** | `memory_evidence` | **DIRECTLY REPRESENTED**, and argued for as a joinable table rather than a count | Yes — STORAGE RECORD |
| **Entity** | **None** | **NOT REPRESENTED** | **Yes**, per ADR-0005 — an identity table (ids, types, aliases, source ids) *"which genuinely is schema"* |
| **Relationship** | **None** | **NOT REPRESENTED** | **UNKNOWN.** Its only advocate was the absent document. ADR-0009 refuses a graph store but does not say what replaces it |
| **Contradiction** | **None** | **NOT REPRESENTED** | **UNKNOWN** — same position. `01-architecture-map.md` §2.9 and principle 4 require it to be *"an object, not a caveat"*, which implies storage |
| **Predicate** | `memory_predicates` | **DIRECTLY REPRESENTED** | Yes — but **configuration**, by its own description, not memory data |
| **SourceClass** | **None** | **NOT REPRESENTED** | **Configuration, not a table in the claim store.** §6 |
| **Authority** | **None** | **NOT REPRESENTED** | **No.** It is the ordering *over* source classes — a versioned file (ADR-0006) |
| **Temporal state** | Six columns on `memory_claims` | **DIRECTLY REPRESENTED** | **No separate table.** Columns, plus `memory_versions_asof` as INDEX |
| **Permission / scope** | `scope_path text`, `tenant_id`, RLS | **INDIRECTLY REPRESENTED** | Partly. `permission_label` (§2.3) has **no recovered column** — Q10 |
| **Principal** | **None** | **NOT REPRESENTED** | **No** — it is a runtime identity, not claim-store state (ADR-0014) |
| **WorldState** | **None** | **NOT REPRESENTED — correctly** | **No.** ADR-0005: it is a DERIVED PROJECTION over claims. *"Delete it. If deleting it loses information, it was not a projection"* |

### 4.1 The four categories, applied

| Category | Members here |
|---|---|
| **DOMAIN CONCEPT** | All fifteen above |
| **STORAGE RECORD** | Observation (missing), Proposal, Claim, ClaimVersion, Evidence, Entity (missing), Predicate |
| **DERIVED PROJECTION** | WorldState — and, per ADR-0005's delete test, anything else that can be rebuilt from claims |
| **INDEX** | The six of §3.3; `memory_versions_asof` is how as-of reads are served without a second table |
| **COMPUTED VIEW** | None specified in any recovered shape |
| **CONFIGURATION** | Predicate registry, SourceClass, Authority ordering. **None of these is memory data**, and the recovered document says so for the first of them |

**The headline:** three concepts the current model treats as central —
**Observation, Entity, Contradiction** — have **no storage in any recovered
shape**, and Observation is the one ADR-0004 calls the system of record.

---

## 5. `kind`

### 5.1 What the repository actually says

`kind` is used as a technical term 171 times in `docs/`. Every occurrence
resolves to one of **two** concepts.

| | **Claim kind** | **Evidence kind** |
|---|---|---|
| **Where** | ADR-0003; `02-domain-model.md` §2.3 | `memory_evidence.kind`, recovered DDL; Memory §11.2 calls it **"Provenance kind"** |
| **Values** | `observation-backed`, `decision`, `implementation-fact`, `outcome`, `constraint`, `term` — six | `run`, `step`, `activity`, `document`, `probe`, `human`, `policy` — seven |
| **Question it answers** | *What does this claim have authority over?* | *What shape of thing is this piece of evidence?* |
| **Enforced by** | `memory_predicates.kinds_allowed` — *"a decision may assert `intended_behaviour` but not `current_behaviour`"* | Nothing; it is descriptive |

**These are different domain concepts sharing a word.** Neither document is
internally inconsistent; the collision is **across** documents, and it becomes a
real hazard the moment both appear in one schema.

### 5.2 The answer

**`kind` means claim kind.** It is ADR-0003's core object property, it is the
project's stated differentiator, and it is what makes *"product says X, code does
Y"* expressible rather than a ranking problem.

### 5.3 A correction to two of our own documents

[ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md) and
`18-brain-mechanism-and-execution-trace.md` §5.3 both state that the recovered
schema **"cannot express `kind`."**

**That is true in substance and misleading as written.** The recovered schema
contains a column literally named `kind` — on `memory_evidence`. The precise
statement is:

> The recovered schema has **no claim-kind column on `memory_claims`.** It has an
> **evidence-kind column on `memory_evidence`**, which is a different concept.

Both documents are corrected, and the distinction is registered in
`15-vocabulary.md` so it is not re-derived.

### 5.4 The five questions, answered

| Question | Answer |
|---|---|
| **Required in the first implementation?** | **Yes.** It is the core object's defining property (ADR-0003) and it is **irreversible** — kind cannot be back-filled onto claims extracted without it, because the classification happens at extraction |
| **Already represented under another name?** | **No.** `memory_origin` (run/human/evolve) is *who produced it*; `trust_label` is *how dangerous it is*; evidence kind is *what shape the evidence is*. None is *what it has authority over* |
| **Is the schema missing it?** | **Yes**, on claims |
| **Intentionally deferred?** | **No.** No document defers it. It is absent because the recovered schema is scoped to runtime memory, where the distinction does not arise (§7) |
| **Used inconsistently?** | **Across documents, yes** — §5.1. Within each document, no |

### 5.5 Q23 resolved: extraction identity

Not strictly a `kind` question, but it is the other place a word names two
things, and it is the one blocking the project's first code.

**Four readable sources agree:**

| Source | Form | Readable? |
|---|---|---|
| `organizational-brain-architecture.md` §7a | *"a deterministic id from `(observation_id, extractor_version)`, made a UNIQUE key, and claimed **before** the model call rather than after. **Retry is not replay.**"* | **Yes** — and not illustrative |
| `02-domain-model.md` §2.2 | *"`proposal_id` — **Deterministic**, derived from `(observation_id, extractor_version)`. UNIQUE"* | Yes |
| `ADR-0018` | Same | Yes |
| `07-brain-observability.md` §1 | Records *"proposal_id, extractor_version"* at the extraction stage | Yes |

**One source differs:** the recovered `memory_proposals.proposal_id` =
`hash(run_id, episode_seq, observation_digest)` — which is
`[ILLUSTRATIVE REFERENCE CODE]`, and which ADR-0030 already scopes to runtime
memory.

**The two are not in conflict once scope is applied.** A runtime subsystem's unit
of work is a **run**; an organizational store's unit is an **observation**. Each
key is right for its own subsystem. Under ADR-0018's key an extractor upgrade
deliberately re-extracts history and a redelivered observation collides; under
the recovered key an upgrade is invisible and the same observation in two runs
produces two attempts.

**Decided:**
[ADR-0033](decisions/ADR-0033-extraction-identity-is-observation-and-extractor-version.md)
— the organizational store's extraction identity is
`(observation_id, extractor_version)`, UNIQUE, claimed before the model call.
**Q23 closes.** The one-week experiment at
`14-outside-in-review-2026-09-14.md:380-385` — *a test that a redelivered
observation produces one claim* — is now writable.

---

## 6. `source_class`

### 6.1 What it is not

**[FACT — in this repository]** `source_class` occurs **zero times across all
nine `learning-notes/*.docx`.** It has no learning-notes lineage whatsoever. Its
readable advocate is `organizational-brain-architecture.md` §3 and §5 principle
1, where it appears as *"source classes"* in prose rather than as a column.

Six adjacent concepts exist and **none of them is this one**:

| Concept | Where it lives | What it answers | Why it is not `source_class` |
|---|---|---|---|
| **Source identity** | `memory_evidence.locator` | *Which exact artifact?* | A URI. Identity, not rank |
| **Source type / evidence kind** | `memory_evidence.kind` | *What shape of thing?* | Descriptive. A `document` does not outrank a `probe` by being a document |
| **Authority** | The ordering **over** source classes | *Which class wins?* | Authority is the **relation**; `source_class` is the **position** |
| **Provenance** | `memory_origin` | *Who produced it — run, human, evolve?* | Lifecycle category |
| **Observation source** | The adapter | *Which system did this arrive from?* | Ingestion routing |
| **Trust** | `trust_label` | *How dangerous is it?* | A **safety** property. `untrusted` blocks ACTIVE; it does not lose an argument |

**The clean definition:** `source_class` is a claim's **position in an authored
precedence ordering**, on **two axes** — authority over *intent* and authority
over *reality* (`02-domain-model.md` §2.10). Two axes, because a decision
outranks an observation on intent and is outranked by it on reality. **That
two-axis shape is the whole reason a single trust tier cannot substitute for it**
— and it is ADR-0003's argument arriving from the other direction.

### 6.2 Where it belongs

| Candidate | Assessment |
|---|---|
| **On Observation** | It **originates** here — the class is a property of where the observation came from, known at ingest |
| **On Evidence** | Defensible: evidence is the join between a claim and its sources | 
| **On ClaimVersion** | **No.** A version is an audit coordinate; precedence is not versioned per row |
| **On Claim** | Where `02-domain-model.md` §2.3 puts it, and where `07-brain-observability.md` §1's *"WHAT IT ACCEPTED"* stage reads it |
| **Derived?** | **Partly.** The *value* is derived from the observation's source at ingest. The *ordering over values* is configuration and is never derived |
| **Configuration?** | The **ordering** is, absolutely — ADR-0006. The **column** is not |

**This gate does not place the column.** It is a genuine design question with two
defensible answers (denormalise onto the claim for a single-query hot path, or
join through evidence for normalisation), and placing it needs the reconciliation
algorithm that Q2 blocks. Registered as **Q24** rather than guessed.

### 6.3 Does it affect reconciliation?

**It is the entire input to reconciliation.** `18-…-execution-trace.md` §11's
resolution needs exactly three things: which claims collide on identity, what
each asserts, and **which source class outranks which, on this axis**. Without
the third, reconciliation has no deterministic answer and the only remaining
option is a model judgement — which is principle 1 lost.

### 6.4 The honest position

**The column is specifiable. Its content is not.** ADR-0006 is **ACCEPTED —
UNEXECUTED**; no policy has been authored; Q2 needs *"a meeting, not a sprint."*
Adding the column does not advance this, and the brief's instruction — *"Do not
add it to the schema simply because it sounds useful"* — is the right one.

**What is safe to state now:** a claim must be able to carry a source class, that
class must resolve to a position on two axes, and the ordering must live outside
anything the agent may edit. **What is not safe to state:** any actual ranking.

### 6.5 New question

**Q24 — where does `source_class` live, and is it denormalised onto the claim?**
Not blocking Phase 1 ingestion; blocking the first reconciliation. Added to
`10-open-questions.md`.

---

## 7. Q7 — the Memory / organizational boundary

### 7.1 What changed

Q7 was recorded as *"two incompatible Phase 1 schemas"*, restated last session as
*"four shapes, no two of them a live disagreement"*, and is now restated a third
time — because **the boundary it asks about is stated outright in a readable
source that had never been cited for it.**

### 7.2 The recovered boundary

**[FACT — in this repository]** `learning-notes/Memory Management Architecture.docx`
§30.1 is headed **"The eight kinds of remembering, kept apart"** and is marked
`[CONFIRMED]` by its author, who writes: *"The Principal Agent architecture
already separates these, and this document adopts the separation unchanged rather
than re-deriving it."*

| What | Category | Written by | Lifetime | Into a live decision? |
|---|---|---|---|---|
| Run memory (short-term) | **RUN** | the running agent | dies with the run | it IS the run |
| Model state | **MODEL** | the context system | one call | it IS the call |
| Harness state | **HARNESS** | humans, and the evolve loop | across runs until edited | yes |
| **Organizational knowledge** | **DOMAIN, org-scoped** | proposed by the agent, applied by the write path | until contradicted | yes, above the load floor |
| **Organizational history** | **DOMAIN, append-only** | the system, transactionally | permanent | **never as a transcript** |
| **Decisions** | **DOMAIN, append-only** | the agent, as a consequence of deciding | permanent | yes — *"as ROWS, by query, never as narrative"* |
| Lessons | DOMAIN or HARNESS | proposed, abstracted, classified, applied | until contradicted | yes, above the floor |
| Policies | **DOMAIN, as configuration** | humans only | until a human changes it | *"as a CONSTRAINT, not as advice"* |

**This is the answer to Q7's boundary question, in the source's own words.** It
was sitting one section away from the DDL the previous session quoted.

### 7.3 What this establishes, and what it does not

**Establishes:**

1. **ADR-0030 is corroborated by the source itself**, not merely inferred from
   its vocabulary. The recovered schema serves RUN/DOMAIN runtime memory; the
   organizational store is a different thing in the same document.
2. **The `decisions` table is explicitly Phase 3** — §30.3 says *"PHASE 3, not the
   MVP"* — and is classified as **history, not memory**: *"It is HISTORY, and
   therefore not memory."* This bears directly on `02-domain-model.md` §2.12,
   which marks Decision **BLOCKED**.
3. **Policies are configuration authored by humans only** — arriving
   independently at ADR-0006 from a different document.
4. **History never enters a live decision as narrative.** *"So history enters a
   decision as ROWS, queried for a specific fact … never as a chapter."*

**Does not establish:**

- **Which schema the organizational store has.** §30 draws the boundary; it does
  not specify the far side of it.
- **Whether entities, relations and a contradiction register belong there.**
  Their only advocate remains absent. §4 records them as UNKNOWN, and they must
  be decided **on their merits** — there is no prior to defer to.
- **The scope-path semantics** shared across the boundary.

### 7.4 Q7, restated a third time

> **What is the organizational claim store's schema, given that the boundary is
> now established and the far side is unspecified?**

**Blocking:** YES, for schema work. **Not blocking** for the observation log and
identity-keyed extraction, which sit on the near side of every shape (§10).

**Next experiment, and it is now executable:** the previous restatement's
experiment could not be run because half its input was missing. This one can be:
**read §30.1 against `02-domain-model.md` §2.1–2.12 and mark each of the eight
categories as in-scope or out-of-scope for Phase 1.** Both inputs are readable.

---

## 8. Architecture consistency audit

Severity: **HIGH** — can cause implementation to encode the wrong model ·
**MEDIUM** — will cost rework · **LOW** — documentation hygiene.

| # | Contradiction | Evidence | Affected | Severity | Action |
|---|---|---|---|---|---|
| **C1** | **Observation has no storage anywhere**, yet ADR-0004 makes the observation log the system of record | §4; no observation table in any recovered shape | ADR-0004, `01-architecture-map.md` §2.3, `08-build-order.md` stage 1 | **HIGH** | Specify it. It is stage 1's first deliverable and nothing downstream is rebuildable without it |
| **C2** | **Claim state enums disagree** — recovered has three (`provisional/active/retired`), current model has four (adds SUPERSEDED) | §3.1 vs `02-domain-model.md` §2.3 | Domain model, lifecycles §4 | **MEDIUM** | Current model wins: without SUPERSEDED, supersession and retirement are indistinguishable |
| **C3** | **Proposal state enums disagree** — `claimed/applied/rejected/abandoned` vs `PENDING/APPLIED/REJECTED/DUPLICATE` | §3.1 vs §2.2 | Domain model, lifecycles §3 | **MEDIUM** | `DUPLICATE` is load-bearing for ADR-0033's redelivery test; `claimed` is the better name for `PENDING` given the claim-before-call rule |
| **C4** | **Extraction identity specified two ways** | §5.5 | ADR-0018, Q23 | **HIGH** | **RESOLVED** — ADR-0033 |
| **C5** | **`kind` names two concepts** | §5.1 | ADR-0003, recovered DDL, doc 18, ADR-0030 | **MEDIUM** | **RESOLVED** — §5.3, plus a vocabulary entry |
| **C6** | **ADR-0012 cites sections that do not exist** in the readable file it names | §2.5 | ADR-0012 | **LOW** | Correct the citation |
| **C7** | **ADR-0013 has no readable advocate** for its claim | §2.4 | ADR-0013, Q9 | **LOW** | Record; do not disturb the decision |
| **C8** | **Decision is BLOCKED in the domain model** while the recovered source specifies its table and calls it **Phase 3** | §7.3 vs `02-domain-model.md` §2.12 | Domain model | **LOW** | Not a contradiction once read: both say *not now* |
| **C9** | **`org_knowledge` stores evidence as `evidence_episodes int`**, which **EV1 forbids in terms** — an evidence count cannot be joined on | `01-architecture-map.md` §4.7 | Q7 | **MEDIUM** | Already registered; the Memory source independently argues the same point (*"A COUNT column cannot be joined on"*) |
| **C10** | **`permission_label` has no recovered column**, and non-partitioned permissions are *"Not designed. Q10"* by the readable source's own admission | §4; `organizational-brain-architecture.md` §4 row 7 | Q10 | **HIGH** *(for Phase 2)* | Unchanged. It is the one gap whose failure mode produces **no error and no log line** |
| **C11** | **Two `version` fields mean different things** and no `docs/project/` file recorded the distinction | §3.4; Memory §17.4 — *"conflating them is a real bug"* | Domain model §2.3, §2.4 | **MEDIUM** | Register it |
| **C12** | **Circular corroboration.** The readable architecture file cites ADRs (0006, 0009, 0023, 0003) that name it as their Source | §2; `organizational-brain-architecture.md` §4, §5 | The ten | **LOW** | Inherent to a co-authored corpus. Worth naming so it is not mistaken for independent support |

---

## 9. Triage

**The test applied:** *can this cause implementation to encode the wrong model?*
If not, it is documentation.

| Bucket | Items |
|---|---|
| **MUST RESOLVE BEFORE IMPLEMENTATION** | **C1** — Observation storage. It is stage 1's deliverable and everything rebuildable depends on it. **Q5** (predicate vocabulary) for anything that writes a claim |
| **CAN RESOLVE DURING IMPLEMENTATION** | **C2**, **C3** — enum reconciliation; both are naming decisions taken when the table is written. **C11** — register the two `version`s before either is coded |
| **CAN DEFER** | **Q24** (§6.5) until the first reconciliation · **Q7's far side** (§7.4) until a schema is written · **C9** until `org_knowledge` is considered for adoption, which nothing proposes |
| **DOCUMENTATION-ONLY** | **C5**, **C6**, **C7**, **C8**, **C12** · the ADR-0029 correction · the `kind` vocabulary entry |
| **HISTORICAL** | The absent 2026-09-05 document itself. **It is not a task.** If it surfaces, ADR-0032 says what to do; if it does not, nothing is blocked |
| **NOT ACTUALLY A PROBLEM** | **The ten ADRs' provenance**, at the scale it was reported. Eight of ten are ordinarily well-sourced · The four `.docx` citation "failures" of §2.5, which were my checker's bug · **C4** and **C5**, resolved in this document |

**Nine of the twelve contradictions are documentation or deferrable.** That is
the finding §9 exists to produce: this is not an architecture programme.

---

## 10. Are we technically ready to implement the first vertical slice?

### **YES, WITH EXPLICIT CONDITIONS.**

**What is now sufficiently established to build:**

| # | Established | On what |
|---|---|---|
| 1 | **The observation log, content-hashed, bitemporal, permission-labelled** | ADR-0004 (VERIFIED in consequence), `08-build-order.md` stage 1. C1 is a *specification* gap, not an evidence gap — nothing contradicts it, it simply has not been written down |
| 2 | **Identity-keyed extraction** — `(observation_id, extractor_version)`, UNIQUE, claimed before the model call | **ADR-0033**, on four concordant readable sources. §5.5 |
| 3 | **The proposal → claim write path**, model-proposes-never-writes | ADR-0010, VERIFIED; `memory_proposals` as the recovered illustration |
| 4 | **Tenant in the key, and cross-tenant reads raise** | ADR-0016, corroborated independently by Memory §17.5 |
| 5 | **The claim identity constraint** — `(tenant_id, scope_path, subject, predicate)`, object excluded | CS2, and the recovered constraint with its reason |
| 6 | **Bitemporal validity**, six fields, three timelines | ADR-0023, matching the recovered temporal block exactly |
| 7 | **Deletion route before retirement**, with its index | ADR-0017 + `memory_evidence_by_run` |
| 8 | **Evidence as a joinable table, never a count** | EV1, argued identically by two independent sources |

**The conditions, each of which is a decision rather than a discovery:**

| # | Condition | Why it blocks | Cost |
|---|---|---|---|
| **A** | **Specify the observation record** — fields, content hash, permission label, bitemporal columns | C1. Nothing is rebuildable without it and it cannot be retrofitted | Hours. It is stage 1's own deliverable |
| **B** | **Decide the Phase 1 predicate set (Q5)** | Only seven candidates exist and none is ratified. A claim cannot be written against an unratified vocabulary; an out-of-vocabulary extraction is *rejected by design* | A meeting |
| **C** | **`kind` is on the claim from the first migration** | Irreversible. Kind is assigned at extraction and cannot be back-filled | Free, if done now |
| **D** | **`source_class` is a column with no ordering** (§6.4) | Knowable at ingest, unrecoverable later. The **ordering** stays blocked on Q2, and no reconciliation ships in this slice | Free, if done now |

**What remains blocked, and is not in this slice:**

- **Reconciliation** — Q2. ADR-0006 is ACCEPTED — UNEXECUTED and *"until the
  policy exists, every downstream mechanism is meaningless."*
- **Entities, relations, contradiction register** — §4, §7.3. No prior, no
  advocate, decided on merits when needed.
- **Non-partitioned permissions** — Q10, C10. Blocking Phase 2, not stage 1.
- **The organizational store's schema** — Q7 §7.4.

**The honest summary.** The blockers that remain are **decisions someone must
take**, not evidence the repository lacks. That is a different and much better
position than this project believed it was in at the start of this session — and
it is the direct result of reading files that were already here.

> **This is not the implementation gate passing.** Per the stop condition, that
> happens in a later session, after the owner has reviewed this report.

---

## 11. Minimum implementation contracts — DEFERRED

**Not produced, by owner decision taken before this investigation began.**

The brief permitted contracts *"ONLY if the evidence supports doing so."* The
owner elected to defer them entirely until this report has been reviewed and the
gate has explicitly passed — the strictest reading of the stop condition.

**This is recorded rather than omitted** so that a future session does not
mistake their absence for an oversight, and does not conclude that the evidence
failed to support them. §10 states what the evidence supports; writing it down as
a contract is the next session's work.

---

## 12. What remains UNKNOWN

Left incomplete because it is incomplete.

| # | Unknown | Could it be resolved here? |
|---|---|---|
| 1 | **What the 2026-09-05 document said**, beyond what is independently present elsewhere | **No.** Not by any means available in this repository. If it exists on someone's disk, producing it is the single most valuable thing anyone could add |
| 2 | **Whether ADR-0013's MCP claim was ever argued**, or was assumed | **No.** No readable source discusses MCP in this context |
| 3 | **Whether entities, relations and a contradiction register were ever specified** | **No.** Their advocate is absent. They are now open questions with no prior |
| 4 | **Where `source_class` belongs physically** | **Not yet** — Q24. Two defensible answers; the tiebreaker is the reconciliation algorithm, which Q2 blocks |
| 5 | **The source-precedence ordering itself** | **No.** Q2 needs a named human and a meeting. No amount of reading produces it |
| 6 | **Whether extraction precision is high enough for the store to be worth trusting** | **No**, and the readable source says so: *"NOT ESTABLISHED — and the one most worth testing early."* Nothing has ever been ingested |
| 7 | **Whether any of this beats a good search box** | **No.** *"GENUINELY OPEN, and worth saying plainly"* |
| 8 | **Whether the runtime spec's `knowledge/world/` is the same subsystem** as the recovered schema | Cheaply testable, not tested here — it has module filenames and no columns |

---

## Related

- [ADR-0032](decisions/ADR-0032-provenance-of-the-2026-09-05-citations.md) — supersedes ADR-0029
- [ADR-0033](decisions/ADR-0033-extraction-identity-is-observation-and-extractor-version.md) — resolves Q23
- [ADR-0029](decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md) · [ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md) · [ADR-0031](decisions/ADR-0031-the-phase-1-index-set.md)
- [`18-brain-mechanism-and-execution-trace.md`](18-brain-mechanism-and-execution-trace.md) — the mechanism trace this gate audits
- [`10-open-questions.md`](10-open-questions.md) — Q2, Q5, Q7, Q10, Q24
- [`11-architecture-change-log.md`](11-architecture-change-log.md)
