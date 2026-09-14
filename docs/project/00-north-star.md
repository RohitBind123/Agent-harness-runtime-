# Project North Star

**Status of this document:** current strategic hypothesis, recorded 2026-09-14.
Every section below is falsifiable, and §7 names what would falsify it.

Read `PROJECT_BOOTSTRAP.md` first. This document records the **live, uncontested
product direction** — see
[ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md).
`prd.md` was written to explore a different, curiosity-driven question (using
the agent runtime to control iOS/macOS) and does not compete with what is
described here.

---

## 1. What company/system are we building?

**A general-purpose agent Brain + Runtime** — a knowledge plane that makes an
agent reliable about what is true, when it was true and on what basis, and an
execution plane that makes its actions verifiable, attributable and reversible.

**The Organizational Brain is the first major substrate and proving ground**,
not the final product definition. The current substrate is a system that lets an
agent act inside an organization with **organizational knowledge that is
reconciled, time-aware, and carries its basis.** That is what is being built and
validated now; it is not what the system is. See
[ADR-0027](decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md),
and `16-high-level-implementation-architecture.md` for the structure.

**Why this order.** The knowledge plane is built first because the execution
plane's guarantees are worth nothing over an unreliable world model. Evidence,
memory, world state, temporal reasoning, authority, contradiction, provenance
and verification have to become reliable before autonomous execution can be
trusted — the same rule as §7's *"legal and measurable before good"*, one level
up.

Decomposed, in the order the strategy assembles them:

| Layer | What it is | Status |
|---|---|---|
| **knowledge system** | A store of kind-typed claims with authority, bitemporal validity, provenance, and contradictions as first-class objects, built over an append-only observation log | DESIGNED |
| **knowledge system MCP** | A thin projection of the knowledge system's capability layer, exposed to external agents | PROPOSED, deliberately deferred |
| **External agents** | Claude, Codex, and similar coding agents, consuming knowledge system context | Exists as third-party products; no integration built |
| **Principal Agent** | The layer that holds authority, makes commitments that outlive a run, and is judged on outcomes rather than delivery | DESIGNED |
| **Agent Runtime** | Durable, verifiable, reversible execution — the 51-chapter handbook and the v1.0 specification | DESIGNED |
| **Controlled autonomous execution** | The end state: work delegated under a carved grant, verified by code, reversible | Not designed in detail |

**The system does not exist.** Every row above marked DESIGNED means a document
describes it and no code implements it.

---

## 2. What problem are we solving?

### The falsifiable statement

> An agent acting inside an organization must answer questions whose answers
> are **not present in any single source**, and must know when it cannot.

*Source: `../architecture/organizational-brain-architecture.md`*

### Why retrieval does not solve it

The worked example, which is the clearest statement of the problem in any
document here:

```
  THE SITUATION
    Product  (Slack, 12 Mar):  "We will support cancellation after approval."
    Developer (PR review, 20 Mar): "The current API rejects cancellation
                                    after approval."
    QA (test file, on main):   test_cancel_after_approval_succeeds

  WHAT A RAG SYSTEM DOES
    Retrieves all three, ranked by similarity, and hands them to a model with
    no structure. The model picks one -- usually the longest or the most
    recent -- and states it as fact. The disagreement is INVISIBLE in the
    output.

    This is not a retrieval-quality failure. PERFECT RETRIEVAL PRODUCES IT TOO.

  WHAT THE KNOWLEDGE SYSTEM MUST DO
    Recognise that these are three different KINDS of thing:

      Product statement -> a DECISION or INTENT.
                           Authority over what SHOULD be true.
                           NO authority over what IS true.
      Developer stmt    -> an OBSERVATION of implementation.
                           Authority over what IS true, at the time observed.
      QA test           -> an ASSERTION that is EXECUTABLE. Its authority
                           depends on whether it passes -- a fourth fact
                           nobody has stated.

    -> and therefore answer:
       "Intent and implementation disagree. As of 20 Mar the API rejects it;
        a decision on 12 Mar says it should not. There is a test asserting
        the intended behaviour -- I do not know whether it passes.
        This is unresolved."

  THAT ANSWER IS THE PRODUCT. Not the retrieval.
```

The structural consequence: **the core object is a claim with a kind, and the
kind determines what the claim has authority over.** Collapsing decisions,
observations, and implementation facts into undifferentiated "sources" is
exactly what makes the contradiction disappear. See
[ADR-0003](decisions/ADR-0003-the-brains-core-object-is-a-kind-typed-claim.md).

---

## 3. Who is the initial customer/user?

**UNKNOWN, and this is a real gap rather than an oversight.**

The current strategic direction names an internal validation environment — the
InOrbitX engineering workflow — but an internal validation environment is not a
customer. No document in this repository identifies a buyer for the knowledge
system direction. This is not blocked on a product-direction decision (that is
resolved — see [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md));
it is a real, separate gap.

**A related observation worth carrying forward, even though it is not a
constraint from a competing product:** `prd.md`'s research (2026-09-06)
identifies a precise buyer for a *different* question — "the Mac-primary
professional with document obligations and no assistant" — and explicitly
rules out the developer/power-user segment as *"the one segment where
Anthropic already ships a better product to an installed base, and where you
have no advantage whatsoever."* That market observation may still be relevant
if the knowledge system's audience turns out to overlap with developer tooling —
but it is a data point to weigh, not an argument this document owes an answer
to, since `prd.md` was never proposing this direction as an alternative.

**Treat "who is the customer" as unanswered until it is answered on its own
terms.** Do not infer one from the architecture, and do not infer one from
`prd.md` either — it was scoped to a different question.

---

## 4. What is the long-term product thesis?

> The scarce thing is not intelligence. It is **trustworthy mutation** — and,
> one layer up, **trustworthy organizational context.**

Classification and retrieval are close to solved and close to free. What nobody
has solved is letting a model act on organizational knowledge and being able to
live with the consequences: knowing where a claim came from, whether it is
still true, what contradicts it, and what happened after the agent acted.

Two supporting arguments, with their evidence class:

- **[EVIDENCE]** Microsoft Research analysed 290 public reports across
  13 frameworks of agents corrupting data, deleting files and leaking secrets,
  and concluded agents "have limited information about their filesystem effects
  and insufficient control over them." Their remedy — stage every mutation,
  snapshot so the agent can detect its own mistakes, gate progressively —
  independently matches the effect tiers, ledger, and gate that this
  architecture already specifies. *Source: `docs/product/04-product-thesis-and-decision.md` §5.2.*
- **[INFERENCE]** The runtime is the asset that survives the product being
  wrong. If one wedge fails, a runtime with durable execution, verification
  and provenance redeploys onto another domain. A point solution redeploys onto
  nothing.

**The honest counter-argument, recorded because it is the one that should be
hardest to answer:** this is a general-purpose platform being justified by the
breadth of applications it might later support, with no code, two unreconciled
vocabularies, and no user. That is the canonical way engineering-led companies
spend two years and ship nothing anyone wants. The counter-argument is stated
in full in `docs/product/04-product-thesis-and-decision.md` §5.2 and it has not
been retired.

---

## 5. What is the current product wedge?

**PROPOSED, unratified.** The current hypothesis is:

> Observe a real engineering workflow, reconstruct organizational knowledge
> from it, and serve that knowledge to the coding agents already working in
> that workflow — through MCP, once a capability layer exists.

The argument for this wedge:

1. The workflow is already instrumented. Git, PRs, CI, and issue trackers emit
   structured, identifier-bearing observations with real timestamps and real
   authors. Entity anchoring is nearly free.
2. The consumer already exists. Claude and Codex are already in the loop, and
   already suffer from missing organizational context.
3. It is measurable. "Did the knowledge system improve the agent's output" is answerable
   with a paired comparison, which is more than most knowledge products can say.
4. It is our own workflow, so the feedback loop is hours rather than a sales cycle.

The arguments against, recorded rather than suppressed:

1. **It overlaps a segment `prd.md`'s research ruled out for a different
   product.** Not a blocker — `prd.md` was never a competing decision — but a
   market observation worth weighing. See §3.
2. **Dogfooding is not product validation.** A system that helps its own authors
   has a sample size of one team with unusual tolerance for its failures.
3. **Most questions are lookups.** The knowledge system's advantage appears on *why*
   questions, *temporal* questions, and *contradictions* — the valuable
   minority. An aggregate quality score will be dominated by lookups and will
   not show the difference. *Source: the knowledge system architecture, which lists this as genuinely open.*

---

## 6. What is explicitly NOT the product?

Each with the reason, because "not yet" without a reason becomes "next sprint."

| Not the product | Why |
|---|---|
| A RAG system / search box over company documents | Perfect retrieval still produces the §2 failure. Different problem. |
| A knowledge graph product | A relationship is a claim. A graph engine is a *second store* with its own consistency story, and the claim, its version, its evidence and its event must commit together. [ADR-0009](decisions/ADR-0009-no-graph-database.md) |
| An MCP server, today | MCP is a projection of a capability layer that does not exist yet. Built first, it becomes the thing that constrains the capability layer. [ADR-0013](decisions/ADR-0013-mcp-is-a-projection-of-the-capability-layer.md) |
| A general agent **platform**, *as a product to sell or build now* | **Narrowed 2026-09-14, not retired** — [ADR-0027](decisions/ADR-0027-general-purpose-brain-and-runtime-organizational-first.md) makes general-purpose the *architecture's* target while the Organizational Brain stays the product being validated. The original reason is unchanged by that and is why the distinction is worth drawing: "Platform" requires a third and fourth environment and an abstraction that survives contact with them. That is a 2028 question. **Anyone pitching it as a platform now is pitching a hope.** |
| An autonomous knowledge curator | A loop that decides which claims to keep, merge or delete is optimising a store against a signal that cannot see what it is destroying. [ADR-0024](decisions/ADR-0024-no-autonomous-knowledge-curation.md) |
| A summarisation/consolidation layer | A summary is not evidence for what it summarises. A claim whose only support is a summary has an evidence chain that does not terminate in an observation. |
| A system that infers authority | Authority inferred from recency, seniority, or confident phrasing is wrong precisely in the cases that matter, and wrong invisibly. [ADR-0006](decisions/ADR-0006-authority-is-authored-configuration-never-inferred.md) |
| An agent that speaks unprompted | A few bad unprompted interventions and the agent is muted permanently. The capability is then gone regardless of later quality. |
| A multi-agent framework | No second agent has a job. |
| The macOS/iOS runtime-control exploration in `prd.md` | **Not a rejected alternative.** It explores a different question — using the agent runtime to control iOS/macOS — and was never proposed as competing with this direction. See [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md). |

---

## 7. What is the current build strategy?

### The ordering principle

> Build the thing that makes the knowledge system's value **visible on one source** before
> building the thing that makes it **general across ten.**

And, from the memory architecture, the complementary rule:

> Build the things that make the store **legal and measurable** before the
> things that make it **good.** Deletion route before retirement. Tenant
> isolation before retrieval quality. Signals before tuning.

### Stage 0 is where we are

Stage 0 is architecture and institutional documentation — this documentation
set. Its exit criterion is a measurement, not a feature list:

> A fresh session, given only `PROJECT_BOOTSTRAP.md`, correctly reconstructs
> what we are building, why, the architecture, what exists, the decisions, the
> open questions, and the next step — without access to any prior conversation.

The full staged roadmap, with the changes proposed to it and the reasoning for
each, is `docs/project/08-build-order.md`.

### The two temptations to resist

**The obvious plan** starts with ingestion breadth — connect Slack, Jira, Git
and meetings, get everything flowing, then figure out what to do with it. It
feels like the foundation and it is legible progress. It is the wrong order,
because every hard problem in this design — entity fragmentation, admission,
vocabulary growth, authority — is invisible until something downstream depends
on getting it right. Four sources of unprocessed observations teach you nothing
except that ingestion works.

**The counter-temptation** — build the reasoning first and fake the data — is
worse, because the hard problems only appear with real messy input.

### The prediction, recorded so it can be checked

The knowledge system architecture predicts that the two things most likely to be built
early despite the argument against them are **the graph database** and **the
MCP server** — because both are legible, both sound like progress, and neither
requires the source-precedence policy, entity resolution, or admission to work. If
either gets built early anyway, the mitigation is the same: make it a strict
projection with no logic of its own, so it can be deleted without losing
anything.

---

## 8. What would falsify this North Star?

| Toward a different product | |
|---|---|
| Most real questions turn out to be lookups where a good search box wins | the knowledge system architecture records this as genuinely open |
| Extraction precision on a reviewed sample is too low for the store to be worth trusting | Named as the thing most worth testing early |
| The predicate vocabulary grows without limit | Would flip [ADR-0008](decisions/ADR-0008-no-embeddings-in-phase-1.md) earlier than planned |
| The project owner decides to actually pursue the `prd.md` runtime-control exploration as a real product | Then this document is superseded, and the change log records it — see [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) for what would cause reconsideration |

| Toward confidence | |
|---|---|
| Five real questions from our own history answered with implementation fact, decision, author, date, and the intent/reality gap stated plainly | the knowledge system architecture's test |
| One contradiction detected between a meeting statement and the code, confirmed by a human as worth raising | the knowledge system architecture — "one confirmed instance is the milestone; it is the whole thesis demonstrated" |
| "What did we believe in June?" answered correctly on a held-out set built from real history | the knowledge system architecture |
