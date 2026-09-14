# Organizational Knowledge Systems — Competitive Landscape

**Status:** external research, conducted 2026-09-05. **Every claim below is
sourced from public vendor material or third-party write-ups surfaced by
search. None was independently tested**, and §6 states the confidence of each
claim individually.

**Why this document exists.** It is the only market analysis in this
repository. It was preserved when the architecture review it originally sat
inside was retired, because the competitive picture is evidence about the
world rather than about any particular design.

**How to read it.** The useful finding is not what any of these systems does.
It is the property that none of them appears to have.

---

## 1. Enterprise knowledge graphs — Glean, Atlassian Rovo, Microsoft 365 Copilot

| System | Problem it solves | Architecture (as described publicly) | What it does not solve |
|---|---|---|---|
| **Glean** | Find the right thing across every enterprise system, ranked and permission-safe | A real-time crawler feeding an Enterprise Graph over three pillars — content (documents, messages, tickets), identity (users, roles, teams), and activity (interactions, engagement). Permission-aware *"from the very first millisecond"*: ACLs attached to graph facts, and queries run against the graph rather than a flat vector store. Ranking uses graph signals such as document popularity and department affinity | **Authority and truth.** The graph models who-relates-to-what, not which-of-these-is-correct. Two documents that disagree are both retrievable, both cited, and **their disagreement is not an object**. Popularity as a ranking signal is orthogonal to correctness — and in a stale-documentation situation it is *anti-correlated* with it |
| **Atlassian Rovo** | Search and act across work items, docs and code, with native understanding of Atlassian's own object model | The Teamwork Graph: a connected map of Jira work items and owners, Confluence documentation and decisions, and code in Bitbucket or GitHub. Deep native understanding of issue links and dependencies | The same gap, plus a boundary: it is strongest inside Atlassian's object model and treats outside sources as connected content. **It knows a ticket links to a page. It does not know the page is wrong** |
| **Microsoft 365 Copilot** | Bring organizational context into the applications where work is written | Microsoft Graph plus a semantic index over tenant content, surfaced natively inside Office. Reported to treat non-Microsoft sources such as Jira as external content, without the native link understanding Rovo has | Same gap. And its centre of gravity is individual productivity — summarise this, draft that — rather than maintaining a shared model of what the organization currently believes |

## 2. Temporal agent memory — Zep/Graphiti, Mem0, Cognee

| System | What it gets right | What it does not solve |
|---|---|---|
| **Zep / Graphiti** | **The closest published architecture to this problem, and the one worth studying.** Three tiers: episodic nodes (raw messages), semantic entities and facts with **bi-temporal edge validity**, and community summaries. Every fact edge records valid time (`valid_at` / `invalid_at`) and transaction time (`created_at` / `expired_at`). When a fact changes the old one is **invalidated rather than deleted** — *"the agent never has to choose between a stale and a current fact."* Retrieval composes cosine, BM25 and breadth-first graph traversal with RRF, MMR and optional cross-encoder reranking, and the context constructor formats facts **with their validity ranges** | **Authority, and permissions at fact level.** Invalidation is driven by recency and LLM-detected contradiction; there is no notion that a signed contract outranks a chat message, or that a decision has authority over intent while an observation has authority over reality. **It answers *when* a fact changed. It does not answer *which source wins* when two are simultaneously live** |
| **Mem0** | Breadth — vector plus optional graph, easy to bolt onto an existing agent | Depth. On LongMemEval — which tests temporal, multi-hop and knowledge-update queries — an independent evaluation put Mem0 at **49.0%** and Zep at **63%**. Both numbers matter more than their difference: **the best published result on a memory benchmark is around two-thirds**, so this is not a solved problem, and any vendor implying otherwise is selling |
| **Cognee, Letta and similar** | Entity-extraction pipelines and memory layers you attach to your own agent. Useful prior art for the extraction stage specifically | They are **memory layers, not organizational models**. None has a concept of an organization, a decision, an owner, or a permission boundary |
| **SurrealDB Agent Memory** *(added 2026-09-14; formerly "Spectron", still its configuration prefix)* | **Now the closest published architecture to this problem.** Provenance as a structured field on every fact-bearing record — *"no fact-bearing record is anonymous"*; **tri-temporal** (database MVCC · when we first believed it · when it was true) with supersession chains rather than overwrite; conflicts recorded as explicit **uncertainty** rows — *"does not pick a silent winner or apply last-write-wins"*; a confidence floor that stops a low-confidence extraction erasing an established fact; scope enforced **at retrieval, fail-closed**, including on graph edges and on the ranking-feedback signal; and one ACID transaction per write, with *"cross-store stitching rejected as an architectural choice, not a feature gap"* | **Authority over truth, entity resolution, and evidence of quality.** *"Authoritative means curated by you for retrieval — not guaranteed true"* — there is no kind whose type bounds what it has authority over. Entity identity is an exact composite key with *"no fuzzy, phonetic, or embedding-based matching on the write path"*, no alias field and no auto-merge: *"merging them is a decision for the layer above."* Its *"accuracy promise"* page carries **no benchmark and no eval set** — accuracy is reframed from retrieval quality to verifiability. Operationally: no in-process mode, and embeddings are **fixed deployment-wide** to one vendor's model |

## 3. The direct comparable — CentralAgent

CentralAgent describes itself as a tribal-knowledge extraction engine that
captures meetings and agent sessions into one company brain, served to
teammates and to coding agents. Publicly described features: continuous
company-wide capture of meetings and agent sessions; memory modelled on
biological consolidation with per-role structure, explicitly to resist the
degradation-with-growth problem; storage across three different "brain
architectures" whose answers are compared for correctness and privacy before
being served; an MCP endpoint so any compatible agent can use it; private-cloud
deployment.

**What is NOT visible in the public description:** how conflicting statements
are reconciled, whether authority differs by source, whether claims carry
validity intervals, or what happens when a captured decision is later reversed.
Those may exist; they are not what the product leads with.

> **Sourcing.** This is a vendor's own description, surfaced by search and not
> independently verified. **Treat every capability claim as marketing until
> tested.**

## 4. The market's own account of the problem

One datum worth carrying, with its caveat. A 2026 Gartner survey is reported as
finding that **64% of support agents say their internal knowledge base contains
contradictions they discover only after a customer complains** — up from 51%
two years earlier, despite increased spend on documentation tooling.

> **Sourcing note.** That figure reached this review through a secondary
> write-up, **not the survey**. Do not quote it externally without checking.

Its *direction*, however, is corroborated by every source in this section. The
commentary is consistent that **AI does not clean up messy organizational
knowledge — it exposes it**: surfacing stale answers where documents are
outdated, failing to reconstruct reasoning where decisions are undocumented,
and having no principled way to choose a winner where ownership is unclear.

## 5. Where the differentiation actually is

```
  WHAT EVERYONE HAS
    connectors, chunking, embeddings, hybrid retrieval,
    permission-aware indexing, an entity graph, an MCP endpoint
    -> this is now COMMODITY. Building it well buys parity,
       not advantage, and buys it slowly.

  WHAT ZEP HAS AND THE ENTERPRISE PLAYERS DO NOT
    bi-temporal validity on every fact
    invalidation instead of overwrite
    -> answers WHEN

  WHAT GLEAN HAS AND ZEP DOES NOT
    permissions attached to individual facts
    identity and activity as first-class graph dimensions
    -> answers WHO CAN SEE IT and WHO IS INVOLVED

  WHAT NOBODY IN THIS LIST APPEARS TO HAVE
    an AUTHORITY MODEL: a declared, versioned, human-authored
      ordering over SOURCE CLASSES, enforced deterministically
    KIND-TYPED claims, where a decision, an implementation and
      an observation have authority over different questions
    CONTRADICTION AS A FIRST-CLASS OBJECT that can BLOCK an
      action rather than decorate an answer
    the honest refusal: "this is unresolved" as a supported
      terminal state rather than a fallback

  THE DIFFERENTIATION IS NOT "a better knowledge graph".
  It is: THE ONLY ORGANIZATIONAL BRAIN THAT CAN SAY WHY IT
  BELIEVES SOMETHING, WHICH SOURCE LOST, AND WHEN IT WOULD
  REFUSE TO ANSWER.
```

**The load-bearing caveat is in §6:** the last block is an argument from
absence, and it is the weakest claim in this document.

## 6. What is confirmed and what is inference

| Claim in this document | Status |
|---|---|
| Glean's architecture — crawler, three graph pillars, ACLs on facts, graph-not-flat-vector queries, popularity and department-affinity ranking signals | **CONFIRMED** from Glean's own published material and documentation, via search results. Not independently tested |
| Rovo's Teamwork Graph spans Jira, Confluence and code; Copilot treats Jira as external content | **CONFIRMED** from vendor and third-party comparisons, via search. The Copilot characterisation comes from a comparison article, so treat it as **CONTESTED** — it is the kind of claim a competitor-adjacent source overstates |
| Zep/Graphiti's three tiers, bi-temporal edges, invalidation-not-deletion, and hybrid retrieval with RRF/MMR/cross-encoder | **CONFIRMED** — described in the Zep paper (arXiv 2501.13956) and Graphiti's documentation, via search results. **The paper was not opened** |
| Mem0 49.0% / Zep 63% on LongMemEval | **REPORTED**, from a third-party comparison. Directionally useful; **do not cite the specific numbers** without the source |
| SurrealDB Agent Memory's data model, tri-temporal axes, provenance fields, reconciliation behaviour, scope enforcement, retrieval tiers and stated boundaries | **CONFIRMED** from SurrealDB's own documentation source (`github.com/surrealdb/docs.surrealdb.com`), read directly, 2026-09-14. Quotations are verbatim. Not independently tested, and the product is **pre-GA** |
| SurrealDB Agent Memory's commercial terms — pricing, licence, source availability, waitlist gating | **UNVERIFIED.** `surrealdb.com` was unreachable from the session that did this research; these came from search-index summaries only. **Do not rely on them.** Nothing in our architecture rests on them |
| A documented gap inside their own material: prose describes `source.trust`, `source.span` and `attribute.confidence`; the published schema shows only a flat `source_turn` | **REPORTED, and worth knowing.** Either the schema page is abridged or the prose is aspirational. It is a useful reminder that a vendor's architecture page and its shipping schema are different artefacts — the same gap this repository's own audit exists to catch |
| CentralAgent's feature set | **VENDOR DESCRIPTION only. Unverified** |
| Gartner 64% / 51% contradiction figures | **SECONDARY, uncorroborated.** Flagged in §4 |
| *"Nobody has an authority model"* | **INFERENCE, and the weakest claim in this document.** It is an argument from absence: none of the public material describes one. A vendor may have one and not market it. **Test it before putting it in a pitch** — the way to test it is to ask a vendor what happens when a signed contract contradicts a wiki page, and listen for whether the answer is a mechanism or a model |

---

## 7. What this document does not establish

It establishes what competitors **appear** not to do. It does **not** establish
that this project can do it, that anyone will pay for it, or that the gap is
commercially meaningful rather than merely real.

The differentiation argument in §5 rests on §6's weakest row. Any strategic
use of this document should carry that caveat with it.

**Re-running this research is cheap and overdue** — it was conducted on
2026-09-05, several sources were searched rather than fetched, and this is a
market where a shipped feature can close the gap in a quarter.
