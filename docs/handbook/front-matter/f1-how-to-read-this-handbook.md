# F.1 — How to Read This Handbook

This is a fifty-chapter book about the software around a model. Almost nobody should read it in
order, and this page exists so that not reading it in order is a decision rather than a drift.

---

## What the book is about

An agent is a model plus a **harness** — the instructions, tools, middleware, memory, and loop
machinery that decide what the model sees and what it can do — running against an **environment**.
The model is bought. The environment is given. The harness is the part you write, and it is where
essentially all the engineering is.

Two sources are treated as co-primary. The **Agentic Harness Engineering** paper supplies the
harness's component structure and the evolution loop that edits it. The **durable agent runtime**
specification supplies the runtime that keeps a long-running, expensive, partly irreversible process
alive across crashes. Neither is allowed to absorb the other's vocabulary, because they have
complementary blind spots: the runtime specification has no concept of memory or skills, and the
paper has no concept of human authority or a product domain.

---

## The four tracks

Pick the row that matches why you are here. Each is a complete path; none requires the others.

| Track | For | Read | Time |
|---|---|---|---|
| **T1 · Orientation** | "I need to speak this language by Friday." | F.1–F.4, Ch 0–5, Ch 9, Ch 18, Ch 20, Ch 48 | ~1 day |
| **T2 · Build the runtime** | "I am writing this code." | Ch 0–32 in order, then Interlude I, then Appendices D, E, F | ~5 weeks |
| **T3 · Operate it** | "It exists; make it survivable." | Ch 16, Ch 17, Ch 21–23, Ch 27, Ch 31–41, Interlude II, Appendix G | ~2 weeks |
| **T4 · Evolve it** | "Make it improve itself." | Ch 14, Ch 15, Ch 16, Ch 20, Ch 28, Ch 39, Ch 40, Ch 41, Ch 42–49 | ~1 week |

T4 includes Chapter 15 and Chapter 40 because both are prerequisites rather than context: an
evolution loop edits tool interfaces constantly, and it cannot be trusted to roll itself back
without a replay harness.

**If you already run an agent system in production**, read Chapter 41 first regardless of track. It
is short, its cold open is three numbers, and its conclusion is actionable this week.

---

## How a chapter is built

Every chapter follows the same sixteen-section template, and four of its parts are there
specifically so the book is followable by an engineer new to AI systems *and* new to distributed
systems.

| Where | What it is |
|---|---|
| §1.1 **Cold open** | A specific failure in the reference system, under 250 words. Not an illustration — the chapter is usually an answer to it. |
| §1.2 **In plain language** | 150–250 words, no jargon, no tags, no cross-references. What this is, why it exists, what goes wrong without it. |
| §2.1 **The analogy, and where it breaks** | One concrete non-AI analogy, followed by a mandatory paragraph naming the property it does *not* carry. The second half is not optional: an unbounded analogy is how readers form confident wrong models. |
| §2.2 **Why this must exist** | A numbered derivation in which each step is a forced move. Where real alternatives exist, they are named along with the property that selected the winner. |
| §16 **Key Takeaways** | About seven numbered claims, followed by the terms the chapter introduced. |

**The two-minute version of any chapter is §1.2 and §16.** If a chapter feels like it is
over-explaining, read those two and move on.

Sections 5 and 7 are chapter-specific; every other section title is fixed, so the same question is
always in the same place. Looking for what breaks? §11, always a table of trigger, detector, and
recovery. Looking for the interface? §8. What it costs at scale? §12.

---

## What to skip, deliberately

- **The diagrams, on a first pass.** There are roughly 290 of them. They are reference material and
  they repay a second reading more than a first.
- **Section 15 (Industry Perspective)**, unless you are deciding what to trust. It regroups the
  chapter's claims by where they came from, which matters when you are evaluating rather than
  learning.
- **Levels 3 and 4 entirely**, if you are prototyping. They are about surviving crashes, contention,
  and production, and none of it is load-bearing until something is running.
- **Level 5 entirely**, unless Chapter 41's gate is satisfied. Chapter 42 §5.6 makes that checkable,
  and the honest answer for most teams is not yet.

---

## The one thing to carry

Every level converges on the same question from a different direction, and by Level 5 it has been
asked seven times: **what is this number measured against?** Not a technique — a habit. If the book
installs only that, it has done most of its job.

---

**Next:** [F.2 — Notation, Tags, and Diagram Legend](f2-notation-tags-and-diagram-legend.md)
