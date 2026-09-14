# Architecture Change Log

**Purpose.** The architecture is expected to change when real evidence
contradicts it. This log makes each change visible, dated, and attributable, so
that a change is a decision rather than a drift.

**The rule:** any change to a decision, a boundary, a domain object, a lifecycle,
or a build order gets an entry here. A change that only appears in a commit
message has not been recorded.

## Entry format

```
### YYYY-MM-DD — <short title>

| Field | |
|---|---|
| **Change** | What changed, in one sentence |
| **Previous design** | What it was |
| **New design** | What it is now |
| **Reason** | Why |
| **Evidence** | What made the case. "None — judgement" is acceptable and honest |
| **Impact** | What else must change |
| **Decision owner** | A named person |
| **Status** | PROPOSED / ACCEPTED / IMPLEMENTED / REVERTED |
| **Records** | ADRs added, changed, superseded |
```

---

## 2026-09-14 — Institutional documentation baseline established

| Field | |
|---|---|
| **Change** | Created `PROJECT_BOOTSTRAP.md` and `docs/project/` as the durable project memory: North Star, architecture map, 24 ADRs, domain model, lifecycles, implementation map, workflow, validation strategy, knowledge system observability, build order, do-not-assume register, open-questions register, this log, the handoff protocol, and a full audit |
| **Previous design** | No durable project context existed. Architectural rationale lived inside individual deliverables or in conversations. `tasks/todo.md` covered handbook maintenance only. There was no session-startup document |
| **New design** | The repository is the source of truth for project context. A fresh session reads `PROJECT_BOOTSTRAP.md` and can reconstruct the project without conversation history |
| **Reason** | Work had accumulated across many sessions with no way for a new session to recover why anything was decided. Several decisions existed only as assumptions inside documents that did not state them as decisions |
| **Evidence** | The audit found three unreconciled contradictions, two unverifiable external dependencies, and one wholly undefined term, **none of which was recorded anywhere as an open item** |
| **Impact** | Future sessions read the bootstrap first and end with a handoff. Decisions go in `decisions/`. Changes go here |
| **Decision owner** | *Not yet assigned* |
| **Status** | ACCEPTED |
| **Records** | ADR-0001 through ADR-0024 created |

---

## 2026-09-14 — Product direction recorded as CONTESTED

| Field | |
|---|---|
| **Change** | The project's product direction is recorded as **contested and unresolved**, rather than as either of the two directions that exist |
| **Previous design** | `prd.md` (2026-09-06): **GO WITH MAJOR CHANGES** on a macOS-first personal-paperwork agent, with Change 3 stating that the terminal / Git / developer-tools environment is cut from the roadmap entirely |
| **New design** | **No new direction adopted.** Both directions are recorded, the contradiction is stated, and a decision is required from a named human |
| **Reason** | The current strategic direction (knowledge system → MCP → coding agents) targets approximately the segment `prd.md` ruled out, and **the reasoning `prd.md` gave has not been retired, addressed, or shown to be inapplicable** |
| **Evidence** | `prd.md`; `docs/product/04-product-thesis-and-decision.md` §5.2, Part 10, §11.1; current strategic direction 2026-09-14 |
| **Impact** | **Implementation is blocked** until this is decided. Documentation and architecture work are not — the architecture is largely common to both directions |
| **Decision owner** | *Required — not yet assigned* |
| **Status** | **OPEN** |
| **Records** | [ADR-0021](decisions/ADR-0021-product-direction-is-contested.md); open question Q1 |

---

## 2026-09-14 — Memory/knowledge system schema conflict recorded

| Field | |
|---|---|
| **Change** | Recorded that the Memory Management Architecture and the knowledge system Architecture specify **incompatible Phase 1 schemas** |
| **Previous design** | Both documents presented as compatible parts of one architecture |
| **New design** | Both positions recorded side by side. **Neither adopted.** A plausible reconciliation is offered and explicitly marked as an inference rather than a decision |
| **Reason** | Memory rejects an entities table and a conflicts table in Phase 1 and defers entity resolution; the knowledge system requires all three in Phase 1. **Neither document acknowledges the other.** They use the same words for different things |
| **Evidence** | Memory architecture §37.2 (ADR 6), §37.4 (ADR 19); the knowledge system architecture, §6.4, §17.3 |
| **Impact** | **No schema may be built until reconciled** |
| **Decision owner** | *Required* |
| **Status** | **OPEN** |
| **Records** | `02-domain-model.md` §5; open question Q7 |

---

## 2026-09-14 — InOrbitX partially established; a deployment question surfaced

| Field | |
|---|---|
| **Change** | Q3 moves from **UNKNOWN** to **partially established**. InOrbitX is a **broker insurance portal held locally on the owner's desktop** |
| **Previous design** | The validation environment was entirely undefined — no domain, no shape, no location |
| **New design** | Domain and shape recorded. Tech stack, team, tooling, workflow and observable surface remain unknown. **No architectural change made** |
| **Reason** | Stated by the project owner |
| **Evidence** | The owner's statement. **Not verifiable from this session** — the project is local and unreachable from here |
| **Impact** | Three things. (1) Q3 narrows from "define an unknown environment" to "inventory the tooling around a known project." (2) A **regulated domain** makes the tenancy, redaction, deletion-route and overlapping-permission work a precondition rather than premature — **Q10 moves up**. (3) **A new question surfaced that no document had asked: where does the knowledge system run relative to the sources it observes?** A local-only source is reachable by a local agent and not a hosted one. Recorded in `06-validation-strategy.md` §7 and coupled to Q8 |
| **Decision owner** | *Required for the deployment shape* |
| **Status** | ACCEPTED as a fact; the deployment question is **OPEN** |
| **Records** | Q3 updated; Q10 severity raised; `06-validation-strategy.md` §7 added |

---

## 2026-09-14 — Outside-in review; five product questions raised

| Field | |
|---|---|
| **Change** | Added an adversarial outside-in review identifying the ten highest-leverage assumptions that could make the project technically or commercially wrong, each with an experiment. **No decision was changed** |
| **Previous design** | The corpus argued *for* its own architecture. No document attacked the premises from outside, and three load-bearing assumptions were unexamined: that customers will author a source-precedence policy, that organizational context improves agent output, and that the runtime is on the critical path |
| **New design** | Unchanged. The review raises questions and recommends experiments only |
| **Reason** | Requested as an independent architect review. The audit established *what exists*; this establishes *what could be wrong* |
| **Evidence** | The review's own labelling separates FACT / EVIDENCE / HYPOTHESIS / RECOMMENDATION throughout. Two findings are worth surfacing here: **(1)** the commercial differentiation rests on what the knowledge system architecture itself calls *"the weakest claim in §3"* — an argument from absence in public material; **(2)** the knowledge system architecture states the knowledge system does not need the fifty-chapter runtime, which contradicts the strategic chain and is reconciled nowhere |
| **Impact** | Five new open questions (Q17–Q21). A recommended two-week experiment programme that contains almost no code. **No architecture changed** |
| **Decision owner** | *Required — the experiments need a go/no-go* |
| **Status** | ACCEPTED as a review; its recommendations are **PROPOSED** |
| **Records** | `14-outside-in-review-2026-09-14.md`; Q17–Q21 |

---

## 2026-09-14 — External reference repositories removed as evidentiary basis

| Field | |
|---|---|
| **Change** | A class of external-codebase references, previously treated as the substrate this architecture reused from, is removed. No external codebase is evidence for this project |
| **Previous design** | The 2026-09-14 audit and baseline (`PROJECT_BOOTSTRAP.md` §5, `09-do-not-assume.md` §3, `04-implementation-map.md` §4, `14-outside-in-review-2026-09-14.md` A9) inherited the knowledge system Architecture document's own framing of these repositories as real, relevant, and merely "not accessible to the audit" — with instructions to ask for them to be attached |
| **New design** | The repositories are stale and were never claimed by the project owner to be connected to the current build. Do not cite them as evidence for a reuse decision or a scope estimate; do not ask for them to be attached on the assumption they inform this project |
| **Reason** | The prior framing was carried forward from source material without confirming it was still live project context. It was not |
| **Evidence** | Direct statement from the project owner, this conversation, 2026-09-14 |
| **Impact** | `PROJECT_BOOTSTRAP.md`, `09-do-not-assume.md`, `04-implementation-map.md`, and `14-outside-in-review-2026-09-14.md` corrected to point to the new ADR rather than describe an open verification gap. Any future scope estimate for the knowledge system starts from zero, not from the knowledge system architecture's eleven-reuse / five-generalise / four-do-not-reuse breakdown |
| **Decision owner** | Project owner |
| **Status** | ACCEPTED |
| **Records** | [ADR-0025](decisions/ADR-0025-no-external-codebase-is-evidence.md) |

---

## 2026-09-14 — Product-direction contest resolved: `prd.md` is exploratory

| Field | |
|---|---|
| **Change** | ADR-0021's "contested, blocking" framing is superseded. `prd.md` (the macOS/iOS paperwork agent) was written to explore a curiosity question — how the agent runtime could be used to control iOS or macOS — and was never a competing product decision. Q1 is resolved |
| **Previous design** | ADR-0021 recorded two apparently competing directions and marked deciding between them **OPEN — BLOCKING**, propagated into `PROJECT_BOOTSTRAP.md`, `00-north-star.md`, `10-open-questions.md` Q1, `04-implementation-map.md`, `08-build-order.md`, and `docs/project/PRD.md` (§0.1, §4.2, §20, §21 D1) |
| **New design** | The knowledge system direction (`00-north-star.md`, `docs/project/PRD.md`) is the live, uncontested product direction. `prd.md` is retained as a record of real research into a different question and is no longer described as competing with it. Change 3's argument does not need to be "answered" — it was never blocking a decision that existed |
| **Reason** | The project owner stated the intent behind `prd.md` directly, which is stronger evidence than anything inferable from the documents alone |
| **Evidence** | Direct statement from the project owner, this conversation, 2026-09-14 — the exact evidence class Q1 required: *"a named human picks A, B, C or D"* |
| **Impact** | Q1 moved to Resolved in `10-open-questions.md`. `prd.md`'s banner corrected. `docs/project/PRD.md` no longer hedges on Q1. `08-build-order.md`'s Stage 0 exit criterion is now partially satisfied |
| **Decision owner** | Project owner |
| **Status** | ACCEPTED |
| **Records** | [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md), superseding [ADR-0021](decisions/ADR-0021-product-direction-is-contested.md) |

---

## 2026-09-14 — External provenance purged; the evidence base is explicitly empty

| Field | |
|---|---|
| **Change** | All external-reference provenance is removed from the corpus — not marked out of scope, removed. The architecture document that carried it is converted to purged markdown and the binary deleted. A guard now fails on reintroduction |
| **Previous design** | An earlier entry today excluded the material but left it named and cited throughout. That was insufficient: the contaminating claims mostly never named a source. **29 unnamed paraphrases survived across 14 files**, four ACCEPTED ADRs cited an unreadable artefact as evidence (two labelled `[CONFIRMED]`), and effort estimates were expressed as a delta from an assumed head start |
| **New design** | **No external codebase is evidence for this project.** Nothing here has been built or validated anywhere; scope estimates start from zero; a quotation whose source is outside this repository is rewritten as an assertion or deleted, never de-attributed and kept |
| **Reason** | The corpus is read as startup context by future sessions. A sentence implying prior art is a false prior that inflates confidence and shrinks perceived scope — the exact failure this architecture exists to detect, inside its own governance layer |
| **Evidence** | Project owner decision. **FACT:** zero product source files have ever been committed |
| **Impact** | ADR-0002 loses a candidate (three → two). ADR-0003, ADR-0006 and ADR-0022 keep their decisions and lose their external evidence; two lose a `[CONFIRMED]` marker. Q4 collapses to a two-way question. Q2, Q7 and Q18 have their evidence cells corrected — **Q7's supporting quotation was also found to be misattributed**, which is a genuine correction independent of this purge. `PROJECT_BOOTSTRAP.md` §5, `04-implementation-map.md` §4, `09-do-not-assume.md` §3 and `14-outside-in-review` A9 are deleted as sections. `13-audit` §I is re-tensed from *keep unchanged* to *build this way the first time*, because nothing exists to leave unchanged |
| **Decision owner** | Project owner |
| **Status** | ACCEPTED |
| **Records** | [ADR-0025](decisions/ADR-0025-no-external-codebase-is-evidence.md) (replacing the earlier, weaker position); `docs/architecture/organizational-brain-architecture.md`; `docs/product/07-organizational-knowledge-landscape.md`; `tools/check_provenance.py` |

---

## 2026-09-14 — Learning-derived vocabulary retired *(entered retrospectively)*

**This entry was owed at commit `c011eb3` and was not written.** The vocabulary
pass edited this file only to apply renames inside existing entries; it added no
entry of its own and no handoff. `README.md` ("A decision is made → add an ADR
**and** a change-log entry") and `05-development-workflow.md` both require one,
and no exemption for vocabulary-only changes is written anywhere. Recorded here
rather than left absent, because a change that only appears in a commit message
has not been recorded.

| Field | |
|---|---|
| **Change** | Names inherited from learning-notes research material are retired in favour of standard industry terminology, with the handbook as the source of truth wherever it already names a concept. 45 files |
| **Previous design** | `docs/project/` used "the Organizational Brain" / "the Brain" / "Business Brain" for one referent, "the authority ladder" for a concept the handbook already names twice with other meanings, and 7-8 undefined bracket tags for epistemic status |
| **New design** | **the knowledge system** · **the source-precedence policy** · **predicate schema registry** (mechanism) versus **predicate vocabulary** (content) · always **PARTIALLY IMPLEMENTED**, never the short form. Admission control, load floor, replay test, autonomy ladder and projection/read model are credited to the handbook chapters that already define them. Epistemic tags close to seven labels, defined once in `PROJECT_BOOTSTRAP.md` §0 |
| **Reason** | Project owner: the terminology read as ambiguous and domain-specific where industry-standard terms exist. The learning material is a source of **learning**, not of vocabulary |
| **Evidence** | Project owner decision. **FACT:** "Brain" and "Principal" as an actor-noun appear **zero times** in the handbook — they were docs/project coinages, not handbook leaks |
| **Impact** | No ADR's Status or Decision changed. Three defects were introduced and are fixed in the entry below. `docs/project/handoffs/` was deliberately left untouched, per "never edit a previous session's handoff" |
| **Decision owner** | Project owner |
| **Status** | ACCEPTED |
| **Records** | [`15-vocabulary.md`](15-vocabulary.md); commit `c011eb3` |

---

## 2026-09-14 — Canonical identity is a general-purpose agent Brain + Runtime

| Field | |
|---|---|
| **Change** | The long-term system is stated as a **general-purpose agent Brain + Runtime**, with the **Organizational Brain as its first substrate and proving ground** rather than the product's definition |
| **Previous design** | `00-north-star.md` §1 scoped the system as *"a system that lets an agent act inside an organization"*, and §1's own §6 listed *"a general agent platform"* among the things explicitly **not** the product. `PROJECT_BOOTSTRAP.md` §2 carried the short form |
| **New design** | Two registers, neither substituting for the other: **Brain + Runtime** names the product; **the knowledge system / the runtime / Principal Agent** name the subsystems. The §6 platform row is **narrowed, not retired** — it now scopes to the product sold and built *now*, and its "pitching a hope" warning is kept deliberately as the guard against premature generality |
| **Reason** | Project owner's direction. The corpus stated an identity the owner says is wrong, and future sessions read those documents first |
| **Evidence** | **[REQUIREMENT]** Owner's direction; not derived from evidence in this repository and not presented as such. The corpus already carried the broader reading in three hedged places, which establishes only that it was visible and discounted — **not that it is right.** `00-north-star.md` §4's counter-argument is not retired |
| **Impact** | Two new documents (16, 17) and two new ADRs. `PROJECT_BOOTSTRAP.md` §2, `00-north-star.md` §1 and §6, `PRD.md` §1, `08-build-order.md` §3.1, `09-do-not-assume.md` §1, `15-vocabulary.md` §7 updated. **No build-order stage, no ADR decision and no requirement changed.** Q8 and Q20 gain a proposed artefact; Q7 widens to a third schema; Q22 is new. Two contradictions registered in `01-architecture-map.md` §4.5-§4.6. Seven defects fixed, four of them introduced by the entry above |
| **Decision owner** | Project owner |
| **Status** | ACCEPTED |
| **Records** | [ADR-0027](decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md), [ADR-0028](decisions/ADR-0028-the-knowledge-core-is-domain-agnostic.md); [`16-high-level-implementation-architecture.md`](16-high-level-implementation-architecture.md); [`17-target-repository-structure.md`](17-target-repository-structure.md) |

---

## 2026-09-14 — Ten ADRs found to cite a source that is not in this repository

| Field | |
|---|---|
| **Change** | Tracing the knowledge pipeline against a concrete event established that the *"knowledge system architecture review, 2026-09-05"* — cited as the basis of **ten of twenty-eight ADRs**, most at section precision — **is not in this repository in any form.** Separately, the Memory Management Architecture's complete DDL was read for the first time, a fourth claim-store shape was found unregistered, and the Phase 1 index set was recovered |
| **Previous design** | Q7 was recorded as a tractable reconciliation between *"two documents in this repository"*, with a half-day method. `PRD.md` §11.3 and `01-architecture-map.md` §4.1 both asserted that as **FACT**. `04-implementation-map.md` recorded that no index inventory existed and that the Memory schema had no migration |
| **New design** | Q7 **restated**: one source is absent, the other self-labels its DDL illustrative and scopes itself to runtime memory, a third has no columns, and a fourth was unregistered. The organizational claim store is **unspecified, with no readable advocate** — the entities, relations and contradiction-register questions are reopened **with no prior**. The index set is recovered and ratified |
| **Reason** | Q7's own *Next experiment* — *"read both §37 and §17.3 together"* — was attempted and **cannot be run.** Half its input does not exist. Nobody had tried |
| **Evidence** | **[FACT]** Four independent checks: the string *"Knowledge System Architecture"* occurs once in the whole Markdown corpus, inside the table citing it; no `.docx` carries a 2026-09-05 date, while the *other* column's 2026-09-02 matches its file metadata exactly; the file bearing that title has sections 0-10 and the citations are to §13.1, §17.3, §20.2; `git log --all --diff-filter=D` finds no deletion. **[EVIDENCE]** `07-brain-observability.md` §1's chain, written independently, requires `kind`, `source_class` and `extractor_version` — the two columns the readable schema lacks and the one it spells differently |
| **Impact** | `01-architecture-map.md` §4.1 corrected and §4.7 added; `PRD.md` §11.3's FACT corrected; `10-open-questions.md` Q7 restated and **Q23 added** (extraction identity specified two incompatible ways); `04-implementation-map.md` two rows corrected. **No ADR's Status or Decision changed, and no status was promoted.** Ten ADRs now carry a visible provenance gap; their reasoning is unaffected |
| **Decision owner** | Project owner |
| **Status** | ACCEPTED |
| **Records** | [ADR-0029](decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md), [ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md), [ADR-0031](decisions/ADR-0031-the-phase-1-index-set.md); [`18-brain-mechanism-and-execution-trace.md`](18-brain-mechanism-and-execution-trace.md) |

---

## Prior history, reconstructed from git

Recorded for continuity. These predate this log and were not written as change
entries; the reasons below are reconstructed from commit messages and document
content, and are marked where the rationale is not established.

| Date | Change | Status | Rationale |
|---|---|---|---|
| 2026-08-04 | Repository created as an agent-runtime documentation base | IMPLEMENTED | Stated in the README |
| 2026-08-09 → 08-16 | Handbook built to 50 chapters, six levels, two interludes, ten appendices, front matter; lint and cross-reference tooling added; v1.0 reading edition compiled | IMPLEMENTED | Stated in `tasks/todo.md` |
| 2026-08-28 → 08-30 | Level 1, 2, 4, 5 engineering references produced as DOCX | IMPLEMENTED | Rationale not yet established |
| 2026-08-30 | **Principal Agent architecture.** Key decision: a Principal Agent is a **Run**, not a layer — correcting the originating brief | ACCEPTED | Preserves the narrow waist; inherits durable execution; makes containment mechanical |
| 2026-08-31 | Agent Evaluation & Measurement architecture | ACCEPTED | Rationale not yet established |
| 2026-09-02 | **Memory Management architecture.** 19 ADRs. Key: memory is a mechanism over several state categories, not a state category | ACCEPTED | The equation "memory = harness state" is already false against the handbook's own table, and believing it puts a customer fact in git |
| 2026-09-05 | **knowledge system architecture.** Key: the core object is a kind-typed claim; the observation log is the system of record; the world model is a projection | ACCEPTED | The cancellation example: perfect retrieval still hides the disagreement |
| 2026-09-06 | Product research and PRD. **GO WITH MAJOR CHANGES** on a macOS paperwork agent | **EXPLORATORY, resolved 2026-09-14** | See the 2026-09-14 entry — written to explore runtime-controls-OS, not a competing product decision |
| 2026-09-06 | Chapter 50 added (third-party tool supply and MCP); specification revision 5 adds §9.9 and invariants I33–I39 | IMPLEMENTED | Acting on Finding B — and correcting it: the original claim that the specification was silent on MCP was wrong |
| 2026-09-07 | Systems Foundations learning document; Apple platform claims verified against primary sources, two corrected | IMPLEMENTED | Two claims were found wrong on verification |

### Findings carried forward without resolution

These were recorded when found and have **not** been resolved. They are now
tracked as open questions.

| Finding | Recorded | Now tracked as |
|---|---|---|
| **Finding 0** — no code exists in this repository | 2026-09-06 | Confirmed by the 2026-09-14 audit |
| **Finding A** — two unreconciled vocabularies | 2026-09-06 | Q4, [ADR-0002](decisions/ADR-0002-specification-vocabulary-is-canonical-for-code.md) |
| **Finding B** — MCP specified but classified future | 2026-09-06 | `01-architecture-map.md` §4.4 |
| **Finding C** — the architecture is server-shaped; the targets are not servers | 2026-09-06 | Q8 |
| **The authority problem** — the policy cannot be inferred and does not exist | 2026-09-05 | Q2, [ADR-0006](decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md) |
