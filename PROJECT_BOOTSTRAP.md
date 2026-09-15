# PROJECT_BOOTSTRAP

**Read this first, in a fresh session, before doing anything else.**

This file is the durable entry point to the project. It is written so that a
person or an agent with no prior context can reconstruct what this project is,
what exists, what does not, what has been decided, and what to do next —
without access to any previous conversation.

| | |
|---|---|
| **Last full audit** | 2026-09-14 |
| **Audited commit** | `169142e` on branch `claude/repo-access-653473` |
| **Audited by** | Claude Code session (see `docs/project/12-session-handoff-protocol.md`) |
| **Repository** | `RohitBind123/Agent-harness-runtime-` |

If the audit date above is more than a few weeks old, treat the *status*
claims in this document as stale and re-run the audit before relying on them.
The *decisions* and *open questions* do not go stale the same way; they change
only when someone changes them, and that change is recorded in
`docs/project/11-architecture-change-log.md`.

---

## 0. The evidence classification used everywhere in these documents

Every status claim in `docs/project/` carries one of these six labels. They are
not interchangeable and **nothing may be silently promoted from one to
another.** Promoting a label is an architecture change and belongs in the
change log.

| Label | Meaning | How to verify it |
|---|---|---|
| **DESIGNED** | A document says this should exist. Nothing has been built. | Find the document and section. |
| **IMPLEMENTED** | Code exists, runs, and satisfies the design. | Run it. Point at the file. |
| **PARTIALLY IMPLEMENTED** | Code exists but does not yet satisfy the intended design. | Point at the file *and* at the gap. |
| **EXPERIMENTAL** | Built to learn something. Not architecturally committed. | Point at the experiment and the question it answers. |
| **PROPOSED** | An idea we intend to build. Not designed in detail, not built. | Point at where it was proposed. |
| **UNKNOWN** | Cannot be established from evidence available in this repository. | Say what evidence would settle it. |

The handbook uses a second, older set of tags for *claim provenance* —
`[AHE]`, `[DAR]`, `[INF]`, `[BP]`, `[FUT]`. Those describe where a claim came
from. The six labels above describe whether a thing exists. They are different
axes and both are in use. See `docs/project/09-do-not-assume.md` §2.

**A third axis — epistemic status, how confident this particular sentence is —
is used throughout the ADRs, the PRD and the outside-in review, and was never
formally enumerated until now.** It had drifted into 7–8 undefined variants.
The closed set, used from here on:

| Label | Meaning |
|---|---|
| **FACT** | Verifiable right now, in this repository. |
| **EVIDENCE** | External, published research or data cited to support a claim — not independently verified by this project. |
| **INFERENCE** | A reasoned conclusion drawn from a stated premise, with **no** claimed falsification test. |
| **DESIGN DECISION** | A choice justified by its own self-contained argument, not by evidence. |
| **HYPOTHESIS** | An unproven belief that **does** carry a stated falsification test. |
| **REQUIREMENT** | A stated need a design must satisfy. |
| **RECOMMENDATION** | A suggested action, not yet a decision. |

**INFERENCE and HYPOTHESIS are the pair most often confused with each other —
the difference is entirely whether a falsifier is stated.** An ADR's
`[INFERENCE]` that later gains a stated test for being wrong should be
relabelled `[HYPOTHESIS]`, not the reverse.

Three axes, three different questions, none of which answers the others:
*does it exist* (the six labels above) · *where did the claim come from* (the
handbook's `[AHE]`/`[DAR]`/`[INF]`/`[BP]`/`[FUT]`) · *how confident is this
sentence* (this section's seven labels).

**A fourth thing that is not an axis at all, but is easy to confuse for one:**
which *word* names a concept. `docs/project/15-vocabulary.md` is the record of
every term retired, renamed, or aligned to the handbook on 2026-09-14, and why
— check it before coining a new name for something that already has one.

---

## 1. What is this project?

**Short answer: today it is a body of architecture and research. It is not yet
a software system.**

This repository contains, at the audited commit:

- 143 Markdown files
- 10 DOCX architecture and learning documents
- 9 SVG diagrams
- 1 research PDF
- **5 Python files, all of which build and lint the documentation. None is product code.**

There is no runtime, no knowledge system, no memory subsystem, no API, no database
migration, no product test suite. **Zero lines of product code exist in this
repository.** This is the single most important fact for a new session to hold,
because most of the documents here are written in the present tense about
components that have never been built.

**Nothing in this design has been built or validated anywhere.** There is no
prior implementation to draw on, no head start, and no component that can be
assumed to work because something like it worked before. Scope and effort
estimates start from zero. See
[ADR-0025](docs/project/decisions/ADR-0025-no-external-codebase-is-evidence.md).

---

## 2. What are we building, and why?

### The canonical identity

**We are building a general-purpose agent Brain + Runtime.** The
**Organizational Brain is the first major substrate and proving ground** — not
the final product definition. See
[ADR-0027](docs/project/decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md).

*"We are building an organizational knowledge product"* is an **incorrect**
summary of this project, and it is the summary a reader will reconstruct if
nobody says otherwise. The knowledge system is built **first** because a system
cannot be trusted to act until it is reliable about what is true, when it was
true, and on what basis. Execution, the Principal Agent, environment adapters
and controlled autonomy come after that, each on its own trigger.

Two registers, and neither substitutes for the other: **"Brain + Runtime"**
names the product; **"the knowledge system"**, **"the runtime"** and
**"Principal Agent"** name the subsystems in every engineering document. See
`docs/project/15-vocabulary.md` §7.

### The current strategic hypothesis

```
        knowledge system
              |
          knowledge system MCP
              |
   External agents (Claude / Codex)
              |
        Principal Agent
              |
        Agent Runtime
              |
   Controlled autonomous execution
```

The thesis, stated so it can be falsified:

> An agent acting inside an organization must answer questions whose answers
> are **not present in any single source**, and must know when it cannot.

Three properties separate that from document retrieval, and all three are load-bearing:

1. The answer is a **reconciliation** across sources that disagree — a
   decision, an implementation, and an observation, made at different times by
   different people with different authority.
2. The answer is **time-dependent** — not "what is true" but "what is true
   now, what was true then, and what changed in between."
3. The answer must carry its **basis** — because an unsupported organizational
   claim is indistinguishable from a confident wrong one, and the cost of the
   second is measured in decisions.

*Source: `docs/architecture/organizational-brain-architecture.md`*

**This is a hypothesis, but it is the settled, live product direction.**
`prd.md` (2026-09-06) once appeared to describe a competing product — a macOS
personal-paperwork agent — but the project owner clarified (2026-09-14) that
`prd.md` was written to explore a different, curiosity-driven question: how
the agent runtime could be used to control iOS or macOS. It was never a
competing decision. See
[ADR-0026](docs/project/decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md),
which supersedes
[ADR-0021](docs/project/decisions/ADR-0021-product-direction-is-contested.md),
and `docs/project/10-open-questions.md` **Q1 (resolved)**.

### What is explicitly NOT the product

See `docs/project/00-north-star.md` §4 for the full list with reasoning. The
short version:

- Not a RAG system or a search box over company documents.
- Not a general agent **platform** — *as a product to sell or build now.*
  General-purpose is the **architecture's** target ([ADR-0027](docs/project/decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md));
  the Organizational Brain is the product being validated. The original
  warning stands and is the reason the distinction is drawn: *"'Platform'
  requires a third and fourth environment and an abstraction that survives
  contact with them. Anyone pitching it as a platform now is pitching a hope."*
- Not a knowledge graph product.
- Not an MCP server (MCP is a *projection* of a capability layer that does not exist yet).
- Not the macOS/iOS runtime-control exploration in `prd.md` — that is a
  separate, exploratory question, not a rejected alternative to this one.

---

## 3. What exists?

| Thing | Status | Where |
|---|---|---|
| 51-chapter agent-runtime handbook | **IMPLEMENTED** (as documentation) | `docs/handbook/` |
| Universal Runtime v1.0 specification, revision 5, 39 invariants | **DESIGNED** | `docs/architecture/` |
| Memory Management Architecture (19 ADRs, 4-table schema) | **DESIGNED** | `learning-notes/Memory Management Architecture.docx` |
| knowledge system architecture | **DESIGNED** | `docs/architecture/organizational-brain-architecture.md` |
| Principal Agent Architecture | **DESIGNED** | `learning-notes/Principal Agent - Organizational Intelligence Architecture.docx` |
| Agent Evaluation & Measurement Architecture | **DESIGNED** | `learning-notes/Agent Evaluation & Measurement Architecture.docx` |
| Product research + PRD (macOS/iOS runtime-control exploration) | **DESIGNED** — exploratory, does not compete with the live direction. See [ADR-0026](docs/project/decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) | `docs/product/`, `prd.md` |
| **Product Requirements Document (knowledge system — the live direction)** | **DESIGNED** | `docs/project/PRD.md` |
| Documentation build + lint tooling | **IMPLEMENTED**, passing | `tools/` |
| **The knowledge system** | **DESIGNED** — no code | — |
| **The Runtime** | **DESIGNED** — no code | — |
| **The Memory subsystem** | **DESIGNED** — no code | — |
| **The Principal Agent** | **DESIGNED** — no code | — |
| **knowledge system MCP server** | **PROPOSED**, and deliberately deferred | — |
| **Observation ingestion (any source)** | **DESIGNED** — no code | — |
| **Any product test suite** | **Does not exist** | — |

Verified at the audited commit: `tools/check_handbook.py` reports 51 chapters,
0 errors, 14 known warnings. `tools/check_xrefs.py` reports 73 documents, 0
unresolved references.

---

## 4. What does not exist, that documents may imply exists

This section exists because several documents in this repository are written
in the present tense about designs. Read this before trusting a present-tense
sentence anywhere else.

- There is **no** `src/`, no `runtime/`, no `contracts/`, no `packages/`. The
  specification's "complete repository tree" (§7, ~2,000 lines) describes a
  tree that has never been created.
- None of the 39 runtime invariants is enforced, because there is no code to
  enforce them against. They are design commitments, not passing tests.
- The four-table memory schema has no migration.
- The observation log, admission stage, entity table, claim store, and
  contradiction register are all designs.
- No source adapter (Jira, Git, Slack, meetings) has been written.
- The source-precedence policy — which the knowledge system architecture names as
  the single blocking prerequisite — **has not been authored.** It requires a
  named human, not an engineering task. See `docs/project/10-open-questions.md` **Q2**.

---

## 5. What we cannot see from here

**InOrbitX** — named in the current strategic direction as the engineering
workflow that will be the knowledge system's first validation environment — is a **broker
insurance portal, held locally on the owner's desktop** (stated by the project
owner, 2026-09-14). It appears nowhere in this repository, and **this session
cannot read it.**

What that establishes: a domain (insurance brokerage) and a shape (a portal).
What it does not: tech stack, team, which tools emit observations, whether it
uses pull requests, or where decisions are recorded. And it adds a constraint
the architecture has not addressed — **a local-only project is reachable by a
local agent and not by a hosted one.** See
`docs/project/10-open-questions.md` **Q3**.

---

## 6. What decisions have been made?

Full records with alternatives, consequences, and reconsideration triggers are
in `docs/project/decisions/`. The load-bearing ones, compressed:

| # | Decision | Status |
|---|---|---|
| [ADR-0001](docs/project/decisions/ADR-0001-repository-is-knowledge-base-not-implementation.md) | This repository is the justification layer. Implementation happens elsewhere. | **ACCEPTED** |
| [ADR-0002](docs/project/decisions/ADR-0002-specification-vocabulary-is-canonical-for-code.md) | The specification's vocabulary is canonical for code; the handbook is canonical for principles. | **PROPOSED — not ratified.** Two documents assume it; nobody has decided it. |
| [ADR-0003](docs/project/decisions/ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md) | The knowledge system's core object is a claim with a *kind*; the kind determines what it has authority over. | **ACCEPTED** |
| [ADR-0004](docs/project/decisions/ADR-0004-observation-log-is-the-system-of-record.md) | The append-only observation log is the system of record. Everything downstream is derived and rebuildable. | **ACCEPTED** |
| [ADR-0005](docs/project/decisions/ADR-0005-the-world-model-is-a-projection-not-a-store.md) | The world model is a materialised view over claims, not an independently authored store. | **ACCEPTED** |
| [ADR-0006](docs/project/decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md) | The source-precedence policy is human-authored configuration, versioned, outside anything the agent may edit. Never inferred. | **ACCEPTED — and unexecuted.** The policy does not exist. |
| [ADR-0007](docs/project/decisions/ADR-0007-memory-is-a-mechanism-not-a-state-category.md) | Memory is a mechanism operating over several state categories, not a state category and not a store. | **ACCEPTED** |
| [ADR-0008](docs/project/decisions/ADR-0008-no-embeddings-in-phase-1.md) | No embeddings in Phase 1. Retrieval is scope-first and structural. | **ACCEPTED**, with a pre-registered trigger to revisit. |
| [ADR-0009](docs/project/decisions/ADR-0009-no-graph-database.md) | No graph database. A relationship is a claim; multi-hop is a recursive CTE. | **ACCEPTED**, with a measured trigger. |
| [ADR-0010](docs/project/decisions/ADR-0010-the-model-proposes-and-never-writes.md) | The model proposes claims; it never writes them. There is no `remember()` tool. | **ACCEPTED** |
| [ADR-0011](docs/project/decisions/ADR-0011-standing-is-earned-by-independent-corroboration.md) | Standing is earned by corroboration from distinct runs. The gate is on the load, not the write. | **ACCEPTED** |
| [ADR-0012](docs/project/decisions/ADR-0012-the-agent-reaches-the-brain-only-through-tools.md) | The agent reaches the knowledge system only through Principal-curried tools. Never an import. | **ACCEPTED** |
| [ADR-0013](docs/project/decisions/ADR-0013-mcp-is-a-projection-of-the-capability-layer.md) | MCP is a thin projection of a capability layer, not a second API. Do not build the server yet. | **ACCEPTED** |
| [ADR-0014](docs/project/decisions/ADR-0014-the-principal-agent-is-a-run-not-a-layer.md) | The Principal Agent is a *client* of the runtime, implemented as a Run — not a layer inside it. | **ACCEPTED** |
| [ADR-0015](docs/project/decisions/ADR-0015-verification-before-knowledge.md) | Only verified observations update knowledge. A model judgement may lower a verdict, never raise it. | **ACCEPTED** |
| [ADR-0016](docs/project/decisions/ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md) | Tenant in the key. A cross-tenant read raises rather than returning empty. | **ACCEPTED** |
| [ADR-0017](docs/project/decisions/ADR-0017-deletion-route-before-retirement.md) | A store ships with a tested deletion route before it ships retirement. | **ACCEPTED** |
| [ADR-0018](docs/project/decisions/ADR-0018-identity-keyed-extraction-first.md) | Extraction is identity-keyed, and the row is claimed *before* the model call. Build it first. | **ACCEPTED** |
| [ADR-0019](docs/project/decisions/ADR-0019-one-source-end-to-end-before-breadth.md) | One source, end to end, including the skippable-feeling stages — before a second source. | **ACCEPTED** |
| [ADR-0020](docs/project/decisions/ADR-0020-the-brain-observes-the-workflow-before-it-controls-it.md) | The knowledge system observes the engineering workflow. It does not control it. | **ACCEPTED** |
| [ADR-0021](docs/project/decisions/ADR-0021-product-direction-is-contested.md) | The product direction is contested: `prd.md` and the current hypothesis describe different products. | **SUPERSEDED by ADR-0026.** |
| [ADR-0022](docs/project/decisions/ADR-0022-predicate-vocabulary-is-closed-and-reviewed.md) | The predicate vocabulary is closed. Out-of-vocabulary extractions are rejected, and the rejection *rate* is the signal. | **ACCEPTED** |
| [ADR-0023](docs/project/decisions/ADR-0023-bitemporal-validity-on-claims.md) | Valid time and transaction time are separated on every claim. | **ACCEPTED** |
| [ADR-0024](docs/project/decisions/ADR-0024-no-autonomous-knowledge-curation.md) | No autonomous curation, consolidation, or summarisation layer. Decay and probes are deterministic and sufficient. | **ACCEPTED** |
| [ADR-0025](docs/project/decisions/ADR-0025-no-external-codebase-is-evidence.md) | No external codebase is evidence for this project. Scope and effort estimates start from zero. | **ACCEPTED** |
| [ADR-0026](docs/project/decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) | `prd.md` was written to explore runtime-controlled iOS/macOS, not as a competing product decision. There is no product-direction contest. | **ACCEPTED** |

---

## 7. What remains uncertain?

The full register — with why each matters, current hypotheses, available
evidence, and the next experiment — is `docs/project/10-open-questions.md`.

**Q1 (which product) is RESOLVED, 2026-09-14** — see
[ADR-0026](docs/project/decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md).
`prd.md` was exploratory; the knowledge system direction is the live plan.

**Blocking (nothing meaningful proceeds until these are decided):**

- **Q2 — Who authors the source-precedence policy, and who may change
  it?** Not an engineering question. Needs a named human and a meeting.
- **Q3 — What is InOrbitX?** No definition exists in this repository.
- **Q4 — Is the handbook or the specification normative for new code?** Two
  constitutions with no stated relationship.
- **Q5 — What is the initial predicate vocabulary?** Roughly twenty predicates,
  drawn from real questions.
- **Q6 — Which single source is ingested first?** Jira or Git are the
  recommended candidates.

**Hard, decide before Phase 2:** MCP caller identity; aggregate leakage;
human-correction versus human-error; confidence floor and decay half-life;
predicate vocabulary growth limit; taint through schema-validated extraction.

**Unsolved, and not by any current design:** noticing a claim is wrong when
nothing new has been observed; self-confirmation through the world; causation
from organizational outcomes; knowing what the organization does not know;
whether any of this beats a good search box for the majority of questions.

---

## 8. What are we currently working on?

**Stage 0 — architecture and institutional documentation.** That is this
documentation set. No implementation has begun and none should begin until
Q2 is resolved. (Q1 is resolved — see §7.)

The immediately preceding work was a run of architecture and learning
documents (see `docs/project/11-architecture-change-log.md` for the dated
sequence). The most recent was *Systems Foundations for Agent Runtime
Engineering*, committed 2026-09-07.

**Operational note:** pushes from the session environment to
`claude/repo-access-653473` return 403, blocked by a GitHub App authorization
gap at the organization level rather than by anything in the code. Fetch still
works; only write is refused. If a push returns 403, that is this, and it is
not fixed by retrying.

**Trap this note previously fell into.** `origin/…` is a *cached* ref. A
session that has never fetched will read a remote-tracking ref from clone time
and conclude the remote is behind when it is not. **Run `git fetch origin
<branch>` before making any claim about what is published** — a decision to
rewrite history rests on that answer, and getting it wrong turns a contained
rewrite into a divergence from a branch other people may already hold.

---

## 9. What should I NOT assume?

The full register is `docs/project/09-do-not-assume.md`. It is mandatory
reading and it is short. The most dangerous items:

1. **Planned ≠ implemented.** Almost everything here is planned.
2. **A present-tense sentence in a design document is not evidence that
   something exists.** Several documents describe unbuilt systems in the
   present tense.
3. **Memory ≠ truth.** A stored claim is a claim, not a fact.
4. **Model output ≠ evidence.** A model proposes; corroboration from distinct
   sources is what creates standing.
5. **Confidence ≠ correctness.** No confidence number in this project has been
   calibrated against a measured noise floor, because no noise floor has been
   measured.
6. **knowledge system ≠ Memory.** They are separate designs with *overlapping and
   currently incompatible* Phase 1 schemas. See `docs/project/09-do-not-assume.md` §4.
7. **knowledge system ≠ Runtime. Runtime ≠ Principal Agent.**
8. **MCP ≠ product.**
9. **Current architecture ≠ immutable architecture.** It is explicitly
   expected to change when evidence contradicts it — which is why the change
   log exists.
10. **Nothing here has been built or validated anywhere.** There is no prior
    implementation, no head start, and no component that can be assumed to work
    because something like it worked before.
    [ADR-0025](docs/project/decisions/ADR-0025-no-external-codebase-is-evidence.md).
11. **The two architecture documents do not agree with each other.** The
    Memory architecture rejects an entities table in Phase 1; the knowledge system
    architecture requires one in Phase 1. Nobody has reconciled them.

---

## 10. What should I do next?

**If you are starting a fresh session and were given no other instruction:**

1. Read this file (done).
2. Read `docs/project/09-do-not-assume.md`. It is short and it prevents the
   most expensive mistakes.
3. Read `docs/project/10-open-questions.md` §1 (the blocking questions).
4. Read `docs/project/13-audit-2026-09-14.md` for the evidence behind the
   status claims above.
5. Then ask what the session is for. **Do not begin implementation.** Q2 is
   unresolved, and it is a decision a human must make. (Q1 is resolved — read
   [ADR-0026](docs/project/decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md)
   rather than treating `prd.md` as contested.)

**The recommended next build step**, with the reasoning, is in
`docs/project/13-audit-2026-09-14.md` §J–K, updated by the later resolution of
Q1. In one line: *hold the precedence meeting for Q2, and then build one source
end-to-end — not the ingestion framework.*

**Before that, read `docs/project/14-outside-in-review-2026-09-14.md`.** It is an
adversarial review of the premises rather than the design, and it recommends a
two-week experiment programme containing almost no code — because four of the
project's load-bearing assumptions can be falsified for a few days' work each,
and none of them has ever been tested.

**Before you end your session,** write a handoff entry using the format in
`docs/project/12-session-handoff-protocol.md`. The repository is the state.
Chat history is not.

---

## 11. Map of the documentation

| Document | Answers |
|---|---|
| `PROJECT_BOOTSTRAP.md` (this file) | Everything, briefly. Start here. |
| `docs/project/00-north-star.md` | What company/system, what problem, who for, what wedge, what is not the product |
| `docs/project/01-architecture-map.md` | Every component: purpose, owns, does not own, inputs, outputs, dependencies, invariants, status |
| `docs/project/decisions/` | Architectural decision records |
| `docs/project/02-domain-model.md` | The canonical domain objects, their fields, lifecycles, owners, invariants |
| `docs/project/03-lifecycles-and-state-machines.md` | State transitions with triggers, preconditions, evidence requirements, reversibility |
| `docs/project/04-implementation-map.md` | Architectural component → actual files → status → test coverage → known limitations |
| `docs/project/05-development-workflow.md` | How features actually get built here today |
| `docs/project/06-validation-strategy.md` | Using the real engineering workflow as the first live validation environment |
| `docs/project/07-brain-observability.md` | The flight recorder: what the knowledge system saw, extracted, proposed, retrieved, answered, and whether it was right |
| `docs/project/08-build-order.md` | The staged roadmap, with proposed changes to it and the reasons |
| `docs/project/09-do-not-assume.md` | The dangerous assumptions register |
| `docs/project/10-open-questions.md` | Unresolved questions, blocking status, next experiment |
| `docs/project/11-architecture-change-log.md` | Every architectural change, dated, with reason and evidence |
| `docs/project/12-session-handoff-protocol.md` | The format every session ends with |
| `docs/project/13-audit-2026-09-14.md` | The full audit this baseline rests on |
| `docs/project/14-outside-in-review-2026-09-14.md` | The 10 highest-leverage assumptions that could make this wrong, and the cheapest experiment for each |
| `docs/project/15-vocabulary.md` | Every term retired, renamed, or aligned to the handbook, and why. **Check before coining a new name** |
| `docs/project/16-high-level-implementation-architecture.md` | System boundaries, the knowledge pipeline, what is required now versus later, the single-writer invariant profile, and which capabilities become real in which phase |
| `docs/project/17-target-repository-structure.md` | The target repository shape for the implementation repo, by phase, and the register of deferred runtime capabilities with a trigger for each |
| `docs/project/18-brain-mechanism-and-execution-trace.md` | **Mechanism, not structure.** One event traced end to end at row level; the recovered claim-store DDL and index set; where a model is and is not required; the failure trace. **§1.1 is corrected — read doc 19 §2 with it** |
| `docs/project/19-recovered-architecture-evidence.md` | **Architecture Gate 01 — read this before any schema work.** The provenance matrix and the ten-ADR audit; the recovered migration inventory; the domain↔storage map; `kind` and `source_class` settled from primary text; the Memory/organizational boundary recovered; and the readiness verdict with its conditions |
| `docs/project/PRD.md` | **The live Product Requirements Document** — thesis, scope (V0/V1), functional and non-functional requirements, trust model, safety, roadmap, traceability. Covers the knowledge system direction, not `prd.md` |

Existing material, unchanged by this baseline:

| Document | Contents |
|---|---|
| `README.md` | Repository overview. Describes the handbook, not the current strategy |
| `docs/handbook/` | 51 chapters, six levels, two interludes, ten appendices |
| `docs/architecture/` | Universal Runtime v1.0 specification, revision 5 |
| `docs/product/`, `prd.md` | Product research and a PRD exploring how the agent runtime could control iOS/macOS. **Exploratory — does not compete with the live direction.** See [ADR-0026](docs/project/decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) |
| `learning-notes/` | Nine DOCX architecture and learning documents, plus two Markdown chapter drafts |
| `tools/` | Documentation build and lint scripts — the only working code here |
