# Reading Map

**What this is:** a one-paragraph summary of every chapter, in plain language, so you can decide
where to start without reading anything twice. For the four structured reading tracks, see
[F.1 — How to Read This Handbook](front-matter/f1-how-to-read-this-handbook.md).

**What the book is:** how to build, operate, and improve the software that runs an AI agent — the
*harness*, as distinct from the model. All fifty chapters are written (0–49).

**How chapters are built:** every chapter opens with a real failure, explains the idea in plain
language before any jargon, derives the mechanism instead of asserting it, and ends with the terms
it introduced. If a chapter feels like it is over-explaining, the plain-language section (§1.2) and
the takeaways (§16) are the two-minute version.

---

## Where to start

Pick the row that sounds most like you.

| If you… | Start at | Then |
|---|---|---|
| **Are new to all of this** | [Ch 0](chapters/00-evolution-of-ai-systems.md) and read forward | Stop after Ch 9 and decide whether to continue |
| **Want the shortest useful path** | [Ch 1](chapters/01-anatomy-of-an-agent.md), [Ch 5](chapters/05-five-nouns.md), [Ch 18](chapters/18-the-runtime-loop.md) | Three chapters, and you can read the rest in any order |
| **Are about to build one** | [Ch 4](chapters/04-complete-runtime-layers-and-process-topology.md) → Level 2 in order → [Interlude I](interludes/interlude-1-assembling-a-minimal-runtime.md) | Interlude I builds it end to end with no new ideas |
| **Already have one in production** | [Ch 41](chapters/41-evaluation-infrastructure.md), then [Ch 34](chapters/34-observability.md) | Ch 41 is short and may change what you do next week |
| **Are debugging something weird** | [Ch 9](chapters/09-three-flows-data-control-event.md), then [Interlude II](interludes/interlude-2-anatomy-of-a-bad-week.md) | Ch 9 tells you which of three ways to read the system |
| **Care most about safety and control** | [Ch 30](chapters/30-human-authority.md), [Ch 31](chapters/31-safety-sandboxing-and-untrusted-content.md), [Ch 27](chapters/27-failure-recovery-and-rollback.md) | Read in that order; each consumes the previous |
| **Are evaluating whether to invest** | [Ch 20](chapters/20-the-self-evolving-runtime-overview.md) and [Ch 41](chapters/41-evaluation-infrastructure.md) | Between them they say what this costs and what it needs |

**The single most useful chapter to read first, for most people already running something:**
[Chapter 41](chapters/41-evaluation-infrastructure.md). Its cold open is three numbers and its
conclusion is actionable this week.

---

## The six levels

| Level | Chapters | In one line | Status |
|---|---|---|---|
| **0 — Foundations** | 0–3 | What an agent actually is, and why running one is a distributed-systems problem | Complete |
| **1 — High-level runtime** | 4–9 | The whole system at arm's length: its parts, its units of work, its boundaries | Complete |
| **2 — Core components** | 10–20 | Each component opened up, one at a time | Complete |
| **3 — Advanced runtime** | 21–32 | Making it survive crashes, contention, hostile input, and many machines | Complete |
| **4 — Production engineering** | 33–41 | Operating it, paying for it, promising things about it, changing it safely | Complete |
| **5 — Self-evolving systems** | 42–49 | A second agent that rewrites the first one's harness | Complete |

---

## Level 0 — Foundations *(Ch 0–3)*

Where the ideas come from and what the words mean. No implementation.

**0. Evolution of AI Systems** — How we got from "complete this text" to systems that plan, act, and
improve themselves. Read it if the field's vocabulary feels like it appeared overnight.

**1. Anatomy of an Agent** — The three parts: the model (you are handed it), the harness (you build
it), the environment (it pushes back). Almost everything in the book is about the middle one.

**2. Why an Agent Runtime Is a Distributed System** — The argument that you cannot avoid distributed
systems problems here, even on one machine, because a model call is a network call that takes
seconds and can fail halfway.

**3. Mental Models and Reference System** — Introduces ARK (the kernel this book describes) and
Atlas (a coding agent built on it). Every failure story in the book happens to Atlas.

---

## Level 1 — High-Level Runtime *(Ch 4–9)*

The whole system, from far enough back to see all of it. Read in order; it is short.

**4. The Complete Runtime** — Every layer and every process, on one page. The map you will keep
returning to.

**5. The Five Nouns** — Run, Plan, Step, Activity, Episode. Five words that make the rest of the
book unambiguous. If you read one chapter of Level 1, read this.

**6. State Separation** — Four categories of state, and which component owns each. Most confusing
bugs are two components believing they own the same thing.

**7. The Edge and Client Contract** — What the outside world is allowed to ask for, and what it gets
back.

**8. Request and Runtime Lifecycles** — Two clocks: the caller's request lasts seconds, the run
lasts hours. Everything awkward about agent systems lives in that gap.

**9. Three Flows** — One system, three ways to read it: what happens next (control), what moves and
how big (data), what is permanently written down (event). Three engineers gave three correct and
contradictory answers because nobody said which one they were reading.

---

## Level 2 — Core Components *(Ch 10–20)*

Eleven components, each opened up. This is the level you implement from. Nine diagrams each.

**10. The Planner** — The only part allowed to decide what happens next. Plans are never edited; a
change mints a new plan. That one decision turns out to solve human control and crash recovery at
the same time.

**11. The Context System** — Choosing what the model sees, under a hard budget, on every single
call. The largest data movement in the system and the place most of the money goes.

**12. The Memory System** — Four different things people mean by "memory", only one of which a run
writes about itself.

**13. The Reasoning Engine** — Exactly one door to the model, metered and abortable. Stopping
waiting is not the same as stopping spending.

**14. The Tool Execution Engine** — How the system touches the world. Introduces one tag —
pure or effectful — that turns out to answer four unrelated questions later in the book.

**15. Agent-Computer Interface Design** — Designing tools a model can actually use. Error messages
are instructions, not diagnostics.

**16. The Observation System** — Record what the model *could have seen*, not just what it did.
Without this, Levels 4 and 5 are impossible.

**17. The State Manager** — Ownership as a value rather than a lock, which is what makes recovery
possible.

**18. The Runtime Loop** — The keystone. About forty lines that sequence everything above and decide
nothing themselves. Short, and every line comes from an earlier chapter.

**19. The Multi-Agent Runtime** — When one agent is not enough, and the answer is narrower than
expected. A sub-agent is a context boundary, never a job title.

**20. The Self-Evolving Runtime — Overview** — The destination, described early so you can carry it
through everything else. Also collects six places where earlier chapters independently concluded
that something must sit outside what a self-improving system may edit.

**[Interlude I — Assembling a Minimal Runtime](interludes/interlude-1-assembling-a-minimal-runtime.md)**
— Builds a working runtime end to end using only what you have read. No template, no new ideas,
just the assembly.

---

## Level 3 — Advanced Runtime *(Ch 21–32)*

Making it survive reality. **Every failure in this level produces no error message** — that is the
level's whole character.

**21. Durable Execution** — Surviving a crash. "Resume", "re-run", and "replay" are three different
operations wearing one word, and confusing them opened three duplicate pull requests.

**22. The Event Spine** — Making sure every recorded fact gets delivered exactly once. One malformed
row stopped everything, silently, with every dashboard green.

**23. The Scheduler** — Deciding what runs next, fairly. One customer's 400 jobs blocked everyone
else for two hours at full throughput. Adding capacity fixed nothing.

**24. The Task Graph** — Writing down what depends on what, instead of implying it with a list.
Starting several things is easy; knowing they have all finished after a crash is the whole chapter.

**25. The World Model** — What the system believes about its environment, and how it finds out it is
wrong. The most speculative chapter in the book, and it says so in its first paragraph.

**26. Planning Algorithms** — What actually goes inside the planner. Three responses to a failure
costing roughly 1x, 3x, and 30x — and a system that replans from unchanged inputs produces the same
plan six times.

**27. Failure, Recovery, and Rollback** — What you owe the world when you stop halfway. "Undo" is
three different operations, and one of them does not exist.

**28. Reflection, Grading, and Self-Correction** — How to tell whether the work was any good, given
that asking the model produces an optimistic answer. One rule — checks set a floor a judgment may
lower and never raise — makes model judgment safe to use.

**29. Long-Running Agents** — Six-hour runs. A run that goes in circles produces steps at exactly
the rate useful work does, so "progress" needs a definition that a stationary run cannot satisfy.

**30. Human Authority** — Putting a person genuinely in control. A rule in the instructions held for
eleven weeks and 460 runs, then lost once. Also shows that a human redirecting a run and a crash
recovering one are the same problem.

**31. Safety, Sandboxing, and Untrusted Content** — What happens when text the system read contains
something that reads like an instruction. The example has no attacker in it at all.

**32. Distributed Execution** — Many machines, one job. A lease and a database check both worked
perfectly and the deployment happened twice.

---

## Level 4 — Production Engineering *(Ch 33–41)*

Running it for real. Every chapter here is **a measurement whose absence has no symptom**.

**33. Scalability and Capacity Planning** — How much of everything you need. The standard formula
for database connections, applied correctly, caused an outage.

**34. Observability** — There are two questions — is the machinery working, and is the work any good
— and they share almost no signals. Most teams have instruments for the first one only.

**35. Cost Engineering** — Cost per call fell 62% and the bill went up 18%. Both numbers were right;
only one was on a dashboard.

**36. Reliability and SLOs** — What you can honestly promise about a system that is
non-deterministic on purpose. Fourteen months of a met availability target, and 31% churn.

**37. Tenancy, Secrets, and Data Governance** — Where customer data actually ends up. A deletion
request that was carried out carefully and missed the largest store.

**38. Deployment, Versioning, and Configuration** — Three things change underneath you — your code,
your harness, and the model — and a model change invalidates every number you ever measured.

**39. GitOps and CI/CD** — Shipping harness changes like code, because they are. Three sentences in
a prompt file broke an unrelated task type for sixteen days.

**40. Testing a Non-Deterministic System** — What a test means when the thing under test calls a
model. Fourteen hundred green tests, forty-one of them configured to pass.

**41. Evaluation Infrastructure** — Whether a change made anything better. Three months of decisions
turned out to be smaller than the measurement's own error. **This chapter is the gate into
Level 5**, and it is the one to read first if you already run something.

**[Interlude II — Anatomy of a Bad Week](interludes/interlude-2-anatomy-of-a-bad-week.md)** — Three
incidents in one week, none of which raised an error, read through the instruments Level 4 built.

---

## [Level 5 — Self-Evolving Systems](levels/level-5-self-evolving.md) *(Ch 42–49)*

A second agent that reads the first one's traces and rewrites its harness.

**42. The Case for Harness Evolution** — Why hand this job to a machine at all. Eighteen months and
a hundred and forty-three harness edits netted 1.3 points, because almost none of the tuning
survives a model change. **Read this before deciding whether the rest of Level 5 is for you.**

**43. Component Observability** — Making the harness into something an edit can land on. Three weeks
of correct edits measured zero, because a middleware hook nobody remembered was quietly doing the
job of the file being edited.

**44. Experience Observability** — Turning ten million tokens of traces into ten thousand a reader
can hold. Thirty-four failures were reported as a discipline problem; the model had never been shown
the file it was supposed to check.

**45. Decision Observability** — Every edit as a claim that can be wrong. A loop reported 89%
accuracy at predicting its own fixes; the real figure was 31%, and the gap was the width of the
claims rather than dishonesty anywhere.

**46. The Evolve Agent** — The loop itself, and the eleven things it may not touch. An engineer
correctly diagnosed that the loop was fixing at the wrong level, moved the right level inside the
boundary, and broke three production limits the benchmark could not see.

**47. Attribution, Verdicts, and Rollback** — Deciding whether an edit helped, and undoing it if not.
Six edits shipped together, one measurement came back, and the credit went to whichever entry
happened to name the tasks that moved.

**48. Limits** — What the loop cannot do. Three edits that each helped delivered a third less
together, and ten iterations of rising scores hid a ten-point regression on the hardest slice.
**Read this before deciding what to promise anyone.**

**49. Continuous Improvement and Governance** — Running it in production, with humans above it. A
weekly review that was never skipped watched four healthy numbers for five months while four
unhealthy ones sat in the same database.

---

## Reference material

- **[Front matter F.1-F.4](front-matter/f1-how-to-read-this-handbook.md)** — the four tracks, the
  notation card, the reference system, and what the book is not.
- **[Appendix A — Glossary](appendices/a-glossary.md)** — every term the book defines, with the
  chapter that introduced it. Generated from the chapters, so it cannot drift.
- **[Appendix F — Invariant Checklist](appendices/f-invariant-checklist.md)** — the 35 properties
  that must hold, each with a test recipe. The page to review against.
- **[CONVENTIONS.md](CONVENTIONS.md)** — how the chapters are written: structure, diagram rules,
  vocabulary. Read only if you intend to write one.
- **[Completion plan](blueprints/phase-3-completion-plan.md)** — how the book was built, batch by batch.

## Notation you will meet

Claims carry a tag saying where they come from:

| Tag | Means |
|---|---|
| `[AHE]` | From the Agentic Harness Engineering paper |
| `[DAR]` | From the durable agent runtime specification |
| `[INF]` | Inferred by this handbook — reasoned, not cited |
| `[BP]` | Established best practice from adjacent fields |
| `[FUT]` | Speculative; an open problem, flagged as such |

If a section is mostly `[INF]` and `[FUT]`, treat it as a considered argument rather than a settled
result. Chapter 25 is the clearest example and says so directly.
