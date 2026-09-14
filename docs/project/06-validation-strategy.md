# Real-World Validation Strategy

**Status:** **PROPOSED.** Nothing described here is instrumented or running.

**The one thing to get right in this document** is the separation between:

> **OUR INTERNAL VALIDATION ENVIRONMENT** — a specific organization, with
> specific tools, specific people, and specific quirks
>
> and
>
> **THE GENERAL PRODUCT ARCHITECTURE** — which must not encode any of that.

Every section below is written to keep those apart, because collapsing them is
how a product becomes an internal tool that only works for the team that built
it.

---

## 1. The proposal

Use the real engineering workflow — the one described in
`05-development-workflow.md` — as the first live environment the Brain observes.

**The Brain observes. It does not control.** See
[ADR-0020](decisions/ADR-0020-the-brain-observes-the-workflow-before-it-controls-it.md).

### Why this environment

| Property | Why it matters |
|---|---|
| **Already instrumented** | Git, PRs, CI and issue trackers emit structured, identifier-bearing observations with real timestamps and real authors. Entity anchoring is nearly free |
| **High claim density** | Every merge is an implementation fact. Every review is an observation with an author. Every decision record is a decision |
| **Real messiness** | Entity fragmentation, admission and vocabulary growth appear here the way they appear anywhere. Synthetic data does not produce them |
| **The consumer is present** | Coding agents already work in this workflow and already suffer from missing organizational context |
| **Feedback in hours** | Not a sales cycle |
| **We can check the answers** | The people who know whether a claim is true are available to say so |

### The honest limits, stated before the benefits are relied on

1. **Dogfooding is not product validation.** A system that helps its own authors
   has a sample of one team with unusual tolerance for its failures. **This
   environment proves the mechanism, not the market.**
2. **This workflow is unusual.** It currently has no pull requests, no CI, and
   no issue tracker — see `05-development-workflow.md` §3. A Brain tuned to it
   would be tuned to an unrepresentative case.
3. **One team is not an organization.** Overlapping permissions, conflicting
   authority, and cross-team contradiction — the problems the design exists for
   — barely appear at this scale.
4. **The observer is the observed.** The people evaluating whether a
   contradiction was worth raising are the people who wrote the claims. That is
   a real bias and it should be measured against an external judgement at some
   point.

---

## 2. What is observed

| Signal | Source | Claim kinds it yields | Available today? |
|---|---|---|---|
| Commits | Git | Implementation fact | **Yes** |
| Diffs | Git | Implementation fact | **Yes** |
| Commit messages | Git | Weak decision / intent | **Yes** |
| Branches, merges | Git | Implementation fact | **Yes** |
| **PR reviews** | GitHub | **Observation, decision** | **No — the workflow produces no PRs** |
| **PR discussion** | GitHub | Decision, rationale | **No** |
| **CI results** | GitHub Actions | Implementation fact — and the fact that resolves a test's conditional authority | **No CI configured** |
| Issues / tickets | Tracker | Intent, decision, status | **No tracker** |
| Documents committed | Repository | Decision, constraint, term | **Yes** |
| **ADRs** | `docs/project/decisions/` | **Decision** — the highest-value kind | **Yes, from 2026-09-14** |
| Session handoffs | `docs/project/` | Observation, decision, open question | **Yes, from 2026-09-14** |
| Agent interactions | Claude Code transcripts | Observation of reasoning | **UNKNOWN** — see §5 |
| Human corrections | Conversation | High-authority observation on **intent** | **Not captured** |

**The immediate finding:** the highest-value sources for this design — PR
reviews, CI results, and tickets — **are the ones this workflow does not
currently produce.** Adopting this validation environment therefore implies
changing the workflow first, which is a real cost and should be decided rather
than drifted into.

---

## 3. What the Brain must reconstruct to have succeeded

The test is not "did it ingest." It is whether it can produce an answer a
document search structurally cannot.

**The exit test, from the Brain architecture:**

> Take five real questions from our own history. For each, the Brain must
> return: the **implementation fact** with its verification date; the
> **decision** with its author, date and rationale; whether they agree; and if
> they do not, **that gap stated plainly.**

Concrete questions this project can already ask of itself:

1. *"Do we use embeddings?"* — a decision says no
   ([ADR-0008](decisions/ADR-0008-no-embeddings-in-phase-1.md)) with a
   pre-registered trigger; no implementation exists to contradict it. The
   correct answer states both.
2. *"Which product are we building?"* — **two decisions disagree.** The correct
   answer surfaces the contradiction, not one of the two answers. This is the
   single best test case this project contains.
3. *"Is there an entities table in Phase 1?"* — two documents disagree. Same
   shape.
4. *"What did we believe about MCP in September?"* — a temporal question with a
   known answer.
5. *"Why is verification before scale in the build order?"* — a *why* question
   whose answer is in a chapter and a specification section, not in either alone.

**Question 2 is the milestone.** If the Brain can detect that `prd.md` and the
current strategic direction describe different products — from observations
alone, without being told — then the thesis is demonstrated on real data.

---

## 4. Keeping the general architecture clean

The failure mode: organization-specific facts leak into the product design and
the product only works for us.

| Must stay general | Must stay local |
|---|---|
| The observation shape | Which sources are enrolled |
| The predicate registry **mechanism** | The specific twenty predicates |
| The source-class ladder **mechanism** | Our ladder's contents and its owner |
| The kind model (six kinds) | Our claim contents |
| Admission **stages** | Our admission rules and thresholds |
| Entity **identity** mechanism | Our entities and aliases |
| The capability layer | Our tool wiring |
| Claim, version, evidence, contradiction semantics | Our data |

**The test to apply to any proposed addition:** *would another organization with
different tools need this, or only us?* If only us, it is configuration, not
architecture — and it goes in a file the architecture reads, not in the
architecture.

**Two concrete traps for this specific environment:**

- **Git-shaped assumptions.** A predicate registry that assumes commits, or an
  entity model that assumes repositories, will not transfer to an organization
  whose decisions live in a wiki and a chat tool.
- **Single-tenant assumptions.** One team means one permission domain, which is
  exactly the case where the overlapping-permissions problem
  ([ADR-0016](decisions/ADR-0016-tenant-in-the-key-and-cross-tenant-reads-raise.md),
  Q10) stays invisible until it is expensive.

---

## 5. What is UNKNOWN about this environment

| Question | Status |
|---|---|
| **What is InOrbitX?** | **PARTIALLY ESTABLISHED (2026-09-14):** a **broker insurance portal**, held **locally on the owner's desktop**. Stated by the project owner. Tech stack, team, tooling and workflow remain unknown. Q3 |
| **Can the Brain reach it?** | **NO, not from a hosted session.** It is local-only. **The architecture has not addressed where the Brain runs relative to the sources it observes** — see §7 |
| Which systems does this organization actually use? | **UNKNOWN.** Git is evident from *this* repository. Whether the portal uses a Git host, an issue tracker, chat or CI is unestablished |
| Are Claude Code interactions capturable as observations? | **UNKNOWN.** Transcripts exist per session; whether they are retrievable, and under what permission, is unestablished |
| How many engineers? Which teams? | **UNKNOWN** |
| Is there an existing knowledge system to compare against? | **UNKNOWN** |
| What are the real questions people ask? | **UNKNOWN — and it is a blocker.** The predicate vocabulary is supposed to be derived from real questions people actually ask, not from a taxonomy. Nobody has collected them |

**Consequence:** this validation strategy is a **proposal shaped by architecture
rather than by evidence about the environment.** The first work is not
instrumentation — it is finding out what the environment is.

---

## 6. Sequence

Each step's exit is a measurement, because a step whose exit is "it's built"
always exits.

| Step | Do | Exit criterion |
|---|---|---|
| **V0** | Answer Q3. Write down what InOrbitX is: systems, teams, tools, where decisions live | A document another engineer can read and know what they are instrumenting |
| **V1** | Collect **real questions**. Twenty to fifty that people actually asked and had to dig for | A list, from real history, not invented |
| **V2** | Derive the predicate vocabulary from V1. Roughly twenty predicates | Each predicate traces to a question in V1 |
| **V3** | Hold the ladder meeting (Q2). Rank source classes on intent and on reality, with an owner | A reviewed file with a named owner — **or** the disagreement written down as an open question |
| **V4** | Fix the observation shape and enrol **one** source | Observations flowing, discard rate real rather than hypothetical. **No extraction yet** |
| **V5** | Extraction, claim store, contradiction detection — the full Phase 1 pipeline | The §3 exit test: five real questions answered with fact, decision, author, date, and the gap |
| **V6** | A second source | **One** contradiction detected across sources that a human confirms was worth raising. That single instance is the whole thesis demonstrated |

**V0 through V3 contain no code.** That is deliberate, and it is the step most
likely to be skipped because it does not feel like progress.


---

## 7. The deployment constraint this surfaces

**[NEW — 2026-09-14]** InOrbitX being local-only exposes a question the
architecture has never asked: **where does the Brain run, relative to the
sources it observes?**

Every document here assumes observations arrive from network-reachable sources —
a Slack API, a Jira instance, a Git host. A project on a developer's desktop is
reachable by an agent running **on that desktop** and not by one running
anywhere else.

Three shapes, and they are materially different systems:

| Shape | What it means | Consequence |
|---|---|---|
| **Local Brain** | The Brain runs on the same machine as the source | The single-writer profile (Q8) becomes the *primary* deployment, not a special case. Most of the contention machinery is dead weight. Multi-tenancy is irrelevant. **This is closest to what the local-only constraint implies** |
| **Hosted Brain, local collector** | A thin local agent emits observations to a hosted Brain | Adds an egress boundary, a trust boundary, and a permission question about what leaves the machine. **In a regulated domain this is a governance decision, not a deployment detail** |
| **Hosted Brain, hosted sources** | What every document assumes | Requires the sources to be hosted, which the portal is not |

**This is not decided anywhere**, and it changes which invariants apply, whether
multi-tenancy exists at all, and whether customer data ever leaves a developer's
machine. It should be resolved alongside Q8 (the single-writer invariant
profile), because the two answers constrain each other.

Recorded as part of **Q3**.