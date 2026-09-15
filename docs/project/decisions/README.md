# Architectural Decision Records

## What is here

Every decision below was **extracted from existing material** in this
repository — the handbook, the specification, the architecture documents, and
the product research. None was invented for this register.

Where a document states a decision but does not state why, the record says
**"Rationale not yet established."** That is a finding, not a gap to fill with
a plausible-sounding reason.

## How to read a status

| Status | Meaning |
|---|---|
| **ACCEPTED** | Decided, and consistently applied across the documents that depend on it. |
| **ACCEPTED — UNEXECUTED** | Decided, but the thing it commits us to has not been done. |
| **PROPOSED** | One or more documents assume it. Nobody has ratified it. |
| **OPEN** | Actively contested, or explicitly unresolved. |
| **SUPERSEDED** | Replaced. The replacing ADR is named, and the change log records the transition. |

**A decision's status is not evidence that anything is implemented.** Every
decision here is ACCEPTED against a design; almost nothing here is built. See
`PROJECT_BOOTSTRAP.md` §3.

## Writing a new record

Copy the field set from any existing record. All nine fields are required:

1. **Status** and date
2. **Context** — what situation forced a decision
3. **Decision** — what we chose, in the imperative
4. **Alternatives considered** — and why each was rejected
5. **Evidence and reasoning** — with the source, and the evidence class
6. **Consequences** — including the costs, stated honestly
7. **What would cause us to reconsider** — a trigger, ideally measurable
8. **Source** — document and section
9. **Related** — other ADRs

A decision with no reconsideration trigger is a belief, not a decision. If you
cannot state what would change your mind, say so explicitly in that field.

Record the new ADR in the index below **and** add an entry to
`docs/project/11-architecture-change-log.md`.

## Index

| # | Decision | Status | Domain |
|---|---|---|---|
| [0001](ADR-0001-repository-is-knowledge-base-not-implementation.md) | This repository is the justification layer, not the implementation | ACCEPTED | Project |
| [0002](ADR-0002-specification-vocabulary-is-canonical-for-code.md) | Specification vocabulary canonical for code; handbook for principles | **PROPOSED** | Project |
| [0003](ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md) | The knowledge system's core object is a kind-typed claim | ACCEPTED | knowledge system |
| [0004](ADR-0004-observation-log-is-the-system-of-record.md) | The observation log is the system of record | ACCEPTED | knowledge system |
| [0005](ADR-0005-the-world-model-is-a-projection-not-a-store.md) | The world model is a projection, not a store | ACCEPTED | knowledge system |
| [0006](ADR-0006-authority-is-authored-configuration-never-inferred.md) | Authority is authored configuration, never inferred | ACCEPTED — UNEXECUTED | knowledge system |
| [0007](ADR-0007-memory-is-a-mechanism-not-a-state-category.md) | Memory is a mechanism, not a state category | ACCEPTED | Memory |
| [0008](ADR-0008-no-embeddings-in-phase-1.md) | No embeddings in Phase 1 | ACCEPTED | Memory / knowledge system |
| [0009](ADR-0009-no-graph-database.md) | No graph database | ACCEPTED | Memory / knowledge system |
| [0010](ADR-0010-the-model-proposes-and-never-writes.md) | The model proposes and never writes | ACCEPTED | Memory |
| [0011](ADR-0011-standing-is-earned-by-independent-corroboration.md) | Standing is earned by independent corroboration | ACCEPTED | Memory |
| [0012](ADR-0012-the-agent-reaches-the-brain-only-through-tools.md) | The agent reaches the knowledge system only through tools | ACCEPTED | Boundary |
| [0013](ADR-0013-mcp-is-a-projection-of-the-capability-layer.md) | MCP is a projection of the capability layer | ACCEPTED | Boundary |
| [0014](ADR-0014-the-principal-agent-is-a-run-not-a-layer.md) | The Principal Agent is a Run, not a layer | ACCEPTED | Principal Agent |
| [0015](ADR-0015-verification-before-knowledge.md) | Verification before knowledge | ACCEPTED | Runtime |
| [0016](ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md) | Tenant in the key; cross-tenant reads raise | ACCEPTED | Security |
| [0017](ADR-0017-deletion-route-before-retirement.md) | Deletion route before retirement | ACCEPTED | Governance |
| [0018](ADR-0018-identity-keyed-extraction-first.md) | Identity-keyed extraction, built first | ACCEPTED | knowledge system |
| [0019](ADR-0019-one-source-end-to-end-before-breadth.md) | One source end to end before breadth | ACCEPTED | Build order |
| [0020](ADR-0020-the-brain-observes-the-workflow-before-it-controls-it.md) | The knowledge system observes the workflow before it controls it | ACCEPTED | Validation |
| [0021](ADR-0021-product-direction-is-contested.md) | The product direction is contested | **SUPERSEDED by 0026** | Product |
| [0022](ADR-0022-predicate-vocabulary-is-closed-and-reviewed.md) | The predicate vocabulary is closed and reviewed | ACCEPTED | knowledge system |
| [0023](ADR-0023-bitemporal-validity-on-claims.md) | Bitemporal validity on claims | ACCEPTED | Memory / knowledge system |
| [0024](ADR-0024-no-autonomous-knowledge-curation.md) | No autonomous knowledge curation | ACCEPTED | Governance |
| [0025](ADR-0025-no-external-codebase-is-evidence.md) | No external codebase is evidence for this project | ACCEPTED | Project |
| [0026](ADR-0026-product-direction-resolved-prd-is-exploratory.md) | Product direction resolved: `prd.md` is exploratory, not competing | ACCEPTED | Product |
| [0027](ADR-0027-general-purpose-brain-and-runtime-organizational-first.md) | General-purpose agent Brain + Runtime; the Organizational Brain is its first substrate | ACCEPTED | Product |
| [0028](ADR-0028-the-knowledge-core-is-domain-agnostic.md) | The knowledge core is domain-agnostic; organizational logic sits behind a boundary | ACCEPTED | Boundary |
| [0029](ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md) | The 2026-09-05 knowledge system review is not in this repository; ten ADRs cite it | **SUPERSEDED** by 0032 | Provenance |
| [0030](ADR-0030-the-recovered-schema-scopes-runtime-memory.md) | The recovered Memory schema scopes runtime memory; the organizational claim store is unspecified | ACCEPTED | Boundary |
| [0031](ADR-0031-the-phase-1-index-set.md) | The Phase 1 index set is recovered, not invented; two entries are constraints, not lookups | ACCEPTED | Storage |
| [0032](ADR-0032-provenance-of-the-2026-09-05-citations.md) | The 2026-09-05 citations are attribution, not evidentiary basis; the concern is two ADRs, not ten | ACCEPTED | Provenance |
| [0033](ADR-0033-extraction-identity-is-observation-and-extractor-version.md) | An extraction attempt's identity is `(observation_id, extractor_version)`, claimed before the model call | ACCEPTED | Storage |

## Decisions imported by reference

The Memory Management Architecture contains **nineteen** numbered ADRs of its
own (its §37) and the runtime specification contains **fourteen** design rules
(its §3). Those are not duplicated here. The records above capture the ones
that are load-bearing across more than one subsystem, or that a fresh session
would get wrong without them. When implementing the memory subsystem
specifically, read that document's §37 in full — it is the authority for its
own internal decisions.

The three decisions the Memory architecture itself nominates as **most likely
to be wrong**, recorded here so attention lands in the right place:

1. **The controlled predicate vocabulary.** How large it grows before
   maintaining it becomes the bottleneck is genuinely unknown and no consulted
   source answers it. If it grows without limit, [ADR-0008](ADR-0008-no-embeddings-in-phase-1.md) flips earlier than planned.
2. **Inferred valid time.** A model reading a date out of prose is the weakest
   joint in the temporal design. A systematically wrong inferred date would
   produce systematically wrong supersession ordering, and the guard that stops
   inferred time displacing attested time would not catch it.
3. **Human-authority asymmetry.** A human-authored claim that has become false
   stays ACTIVE until a person acts on an alert — a deliberate trade against an
   automated erosion path for human decisions, which means a wrong human claim
   keeps influencing runs for as long as nobody looks.
