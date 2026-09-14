# DO NOT ASSUME

**Mandatory reading. It is short on purpose.**

Every item below is an assumption that is (a) natural to make, (b) wrong here,
and (c) expensive. Items marked **[PROJECT-SPECIFIC]** were discovered during
the 2026-09-14 audit and are not generic advice.

---

## 1. The general ones

| Do not assume | Because |
|---|---|
| **Planned = implemented** | Almost everything in this project is planned. Zero product code exists |
| **Memory = truth** | A stored claim is a claim. It has a source, a confidence, a validity interval and possibly a contradiction |
| **Model output = evidence** | A model **proposes**. Standing comes from independent corroboration across distinct runs |
| **Confidence = correctness** | No confidence number here has been calibrated, because no noise floor has been measured |
| **knowledge system ≠ Memory** | Different designs, different scopes, and **currently incompatible Phase 1 schemas.** §3 |
| **knowledge system ≠ Runtime** | The knowledge system is a consumer of runtime primitives, never a modifier of them |
| **Runtime ≠ Principal Agent** | The Principal Agent is a *client* of the runtime, implemented as a Run — not a layer inside it |
| **MCP ≠ product** | MCP is a transport projection of a capability layer that does not exist yet |
| **Current architecture ≠ immutable architecture** | It is expected to change when evidence contradicts it. That is why the change log exists |
| **Prototype behaviour ≠ committed contract** | Nothing here has shipped, so nothing here is a contract |

---

## 2. [PROJECT-SPECIFIC] A present-tense sentence is not evidence of existence

**This is the single most dangerous property of this repository.**

Several documents describe unbuilt systems in the present tense, because they
are specifications and that is how specifications are written. The runtime
specification's §7 contains a ~2,000-line "complete repository tree" for a tree
that has never been created. The handbook says what the runtime *does*. The
memory architecture says what the write path *does*.

**None of it does anything. There is no code.**

When you read a present-tense claim in this repository, check
`04-implementation-map.md` before acting on it.

### Two status vocabularies are in use and they are different axes

- **`[AHE]` `[DAR]` `[INF]` `[BP]` `[FUT]`** — where a *claim* came from.
- **DESIGNED / IMPLEMENTED / PARTIALLY IMPLEMENTED / EXPERIMENTAL / PROPOSED / UNKNOWN** —
  whether a *thing* exists.

A claim can be `[DAR]` (supported by the specification) and the thing it
describes still be DESIGNED. Do not read the first set as implying the second.

---

## 3. [PROJECT-SPECIFIC] The two architecture documents disagree

The Memory Management Architecture (2026-09-02) and the knowledge system
Architecture (2026-09-05) specify **overlapping and incompatible Phase 1
schemas**, and **neither acknowledges the other**:

- Memory **rejects** an entities table in Phase 1; knowledge system **requires** one.
- Memory **defers** entity resolution; knowledge system calls it Phase 1 and the component
  most likely to be underestimated.
- Memory **rejects** a conflicts table; knowledge system **requires** a contradiction
  register with severity.

They use the same words — `claims`, `evidence`, "Phase 1" — for different
things.

**Do not build either schema until this is reconciled.** A plausible
reconciliation exists (`02-domain-model.md` §5) but it is an **inference, not a
decision.**

---

## 4. [PROJECT-SPECIFIC] `prd.md` is exploratory, not a rejected or contested alternative — corrected 2026-09-14

`prd.md` (2026-09-06) documents a GO decision on a macOS personal-paperwork
agent. This was previously read as competing with the knowledge system
direction, which points at approximately the segment `prd.md`'s Change 3 ruled
out.

**Do not assume that anymore.** The project owner states directly (2026-09-14)
that `prd.md` was written to explore a different, curiosity-driven question —
using the agent runtime to control iOS/macOS — and was never a competing
product decision. There was no contest. See
[ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md),
which supersedes
[ADR-0021](decisions/ADR-0021-product-direction-is-contested.md).

---

## 5. [PROJECT-SPECIFIC] "InOrbitX" is only partly defined, and is not readable from here

Established 2026-09-14: it is a **broker insurance portal, held locally on the
owner's desktop.** That is a domain and a shape. It is **not** a tech stack, a
team, a tool inventory, or a workflow description, and **this session cannot
read it.**

Do not infer the rest from the domain name. In particular, do not assume it has
pull requests, CI, an issue tracker, or a chat history the knowledge system could ingest —
the workflow that *this* repository shows has none of those, and that is the
only workflow anyone here has observed.

Do assume, until shown otherwise, that a regulated domain means **real customer
data with real confidentiality boundaries** — which moves Q10 (overlapping
permissions) from "under-designed" to "blocking before the first non-public
source."

---

## 6. [PROJECT-SPECIFIC] The two vocabularies are not translations of each other

The handbook and the specification describe overlapping concepts with different
names, and **neither states its relationship to the other.** The consequence:
*every architectural argument can be won by citing the other one.*

Do not assume a handbook term and a specification term mean the same thing
because they sound alike. And do not assume the working assumption —
specification canonical for code, handbook canonical for principles — has been
ratified. It has not.

---

## 7. [PROJECT-SPECIFIC] Things that are BLOCKED, not deferred

Four Principal Agent objects — Decision records, Goal records, Commitments,
Outcome probes — depend on organizational structures that do not exist: goal
records with measures and baselines, grants, and authority.

**No amount of memory or knowledge system work brings them closer.** Do not put them in a
plan as if they were the next thing after the current thing.

---

## 8. [PROJECT-SPECIFIC] The handbook being "complete" says nothing about the product

`tasks/todo.md` says the handbook is complete, and it is — 51 chapters, zero
lint errors, zero unresolved cross-references. **That is a documentation status,
not a project status.** The same file contains no product or knowledge system work at all,
because it predates both.

---

## 9. [PROJECT-SPECIFIC] The repository can drift from reality silently

**Nothing here is executed against code, so nothing fails when a document goes
stale.** Every other engineering artefact has some mechanism that complains
when it stops matching reality — a test, a build, a type checker. This corpus
has none, because there is no code for it to disagree with. A status line here
can be wrong for months and produce no signal.

**That is precisely the failure this architecture exists to detect, and this
documentation set is the least protected thing in the project.** If what you find
contradicts what you read here, **the document is wrong.** Fix it and record the
fix in `11-architecture-change-log.md`.

---

## 10. Things to build this way the first time

**None of these exists yet.** Each protects a security or correctness property,
and each is easy to build slightly weaker without noticing — which changes a
guarantee from **structural** to **conventional**. Build each as stated, or
record why not.

| Build it this way | What breaks otherwise |
|---|---|
| Tool projection as the knowledge system boundary | Every access-control argument at once |
| Clock discipline, with a CI test | Temporal correctness. Once it exists, widen the allowlist per module with a comment rather than relaxing the test |
| Server-minted evidence handles | A caller-chosen id **is the whole attack** |
| The ACL predicate living **inside** the store | Pre-filter becomes post-filter; recall collapses under a selective predicate, and leaks stop producing signals |
| A denied read **raising** rather than returning empty | An empty result is indistinguishable from having no data and produces no signal |
| The closed predicate vocabulary | Nothing collides, so nothing contradicts |
| The imperative check in the write path | An imperative becomes a harness change with no evaluation gate |
| The load floor and the retire floor | A loop could move the floor instead of improving the claims |
| A third-party descriptor never supplying the local half | A talkative server becomes more trusted than a silent one |
| "A model judgement may lower, never raise" | The only thing making model judgement safe to use |

---

## 11. If you are about to do any of these, stop

- Begin implementation before Q2 (source-precedence policy) is resolved. (Q1, product
  direction, is resolved — see ADR-0026.)
- Build a schema before the Memory/knowledge system schema conflict is reconciled.
- Build an MCP server before the capability layer is stable and the caller-
  identity question is decided.
- Add a graph database, embeddings, or a summarisation layer without the
  measured trigger that each ADR names.
- Infer the source-precedence policy from data.
- Write a confidence threshold or a decay half-life without a measured noise
  floor.
- Promote a status label — DESIGNED → IMPLEMENTED especially — without pointing
  at the code.
- Resolve a contradiction between documents by picking one silently.
