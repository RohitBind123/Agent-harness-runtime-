# F.3 — The Running System: ARK and Atlas

Every abstract claim in this book lands on one system. There is no chapter whose examples are
hypothetical, and no failure mode that is not attributed to a specific thing going wrong in a
specific place. This page is who they are.

Chapter 3 §5 introduces them properly. This is the card.

---

## ARK — the runtime

**What it is.** A domain-independent agent runtime kernel. Python. One transactional database, one
queue, and nothing else on the substrate.

**What it contains.** A relay, a run driver, an activity runner, a sweeper, two queues, eight tables.

**What it deliberately does not contain.** Any knowledge of coding, repositories, patches, or
customers. If ARK ever imports from Atlas, something has gone wrong, and Chapter 6's structural test
is what catches it.

**Its extension surface.** Six ports and nothing else: planner, tool, model, grader, approval,
domain. The handbook treats this as a strict test — if the thing you need to change is not one of
the six, the architecture is wrong for your product.

**Scale target.** Hundreds of concurrent runs across tens of tenants. Explicitly *not* millions,
which is a disqualifier for building this rather than buying an execution engine (Chapter 21 §14).

---

## Atlas — the product

**What it does.** A customer connects a repository. When an issue is labelled for automation, Atlas
opens a run: it reads the issue, explores the repository, writes a patch, runs the test suite,
iterates until the suite passes, and opens a pull request for a human to review.

**Why a coding agent**, and the third reason is the real one:

1. Both primary sources live near this domain.
2. The intended reader will not need the domain explained.
3. Coding agents have **genuine irreversibility**. Pushing a branch, opening a pull request, and
   running arbitrary shell in a sandbox with network access are all things you cannot take back. A
   reference product without irreversible actions would let the book skip half the architecture, and
   the half it skipped is the half that matters.

**Atlas's tools, tagged.** The pure/effectful split, made concrete:

| Tool | Effect | Notes |
|---|---|---|
| `tool.repo.read_file` | pure | |
| `tool.repo.search` | pure | |
| `tool.shell.run_command` | pure *within the sandbox* | pure by containment, not by nature |
| `tool.test.run_suite` | pure | |
| `tool.repo.apply_patch` | pure | writes to the sandbox working tree only |
| `tool.repo.push_branch` | **effectful** | gated |
| `tool.repo.open_pull_request` | **effectful** | gated |
| `tool.notify.comment_on_issue` | **effectful** | gated; visible to the customer |

The shell row is the interesting one. A shell inside a fresh, isolated sandbox is pure *by
containment* — its effects are real and they die with the sandbox. The moment that sandbox has
outbound network credentials, the tag is wrong, and Chapter 31 turns that into a rule.

---

## The cast

Three roles recur, so that "a human decides" always has a face.

| Role | Does |
|---|---|
| **The tech lead** at a customer | Resolves gates. Approves the push, or does not. May never answer. |
| **The on-call engineer** at Atlas | Watches dashboards, diagnoses incidents, is paged by Chapter 34's signals |
| **The harness maintainer** at Atlas | Owns the seven harness components — and is replaced, from Chapter 46, by an evolution loop under supervision |

---

## Atlas's numbers

The reference system carries consistent figures across fifty chapters, so a claim in one chapter can
be checked against a measurement in another. The recurring ones:

| Quantity | Value | First established |
|---|---|---|
| Benchmark size | 60 tasks, k=5 rollouts | Ch 41 |
| Overall noise floor | ~3.1 percentage points | Ch 41 §5.1 |
| Trajectory volume | ~9.4M tokens per batch | Ch 20 §10 |
| Evidence corpus | ~11k tokens after distillation | Ch 44 §5.1 |
| One evolution iteration | ~720M tokens, almost all benchmark | Ch 20 §12.1 |
| A manual harness re-fit | ~18 days, 11 of them a scarce person's | Ch 42 §4 |
| Model release cadence | every four to six months | Ch 42 §5.2 |

---

## What Atlas is not

To keep the reference honest. Atlas is single-region, has no cross-region durable timers, does not
need sub-second latency, and does not run untrusted customer code outside a sandbox.

Each of those would change an answer somewhere in this book, and where a chapter's conclusion
depends on one of them, that chapter says so rather than leaving it implied.

---

**Next:** [F.4 — What This Handbook Is Not](f4-what-this-handbook-is-not.md)
