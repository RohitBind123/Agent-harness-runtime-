# F.4 — What This Handbook Is Not

A book that says what it covers is making a claim. A book that says what it does not cover is making
a more useful one, because the reader can tell in a minute whether it is the wrong book for them.

---

## It is not a framework

There is no code to install. ARK is a reference architecture with named ports and typed contracts,
and every code block in the book is a signature or a small illustrative implementation, not a
library. Appendix E collects all 109 ports; none of them ships.

`[INF]` The handbook's position is that the architecture is the transferable part and the code is
not. Chapter 21 §14 goes further and names the point at which you should stop growing your own
durable execution and buy an engine.

---

## It is not a survey

Two sources are treated as primary and the rest of the field appears only as `[BP]` — established
practice, attributed, where it transfers. There is no comparison of agent frameworks, no evaluation
of vector databases, and no position on which model to use.

`[INF]` That is a deliberate narrowing. A survey of a field moving this fast is stale before it is
finished; an architecture derived from failures is not.

---

## It is not about model quality

The model is bought, held fixed, and treated as a component with a metered interface (Chapter 13).
Nothing here is about fine-tuning, model selection, or evaluation of models as such. Where model
behaviour appears, it appears as something the harness must work around rather than something to
improve.

The one measurement the book leans on hardest makes the same point from the other side: on a *fixed*
model, editing nothing but harness components moved a published benchmark by more than seven points
(Chapter 42 §5.4).

---

## It is not a safety or alignment text

Chapter 31 handles sandboxing, capability scoping, and untrusted content as engineering problems.
Chapters 46 and 49 handle containment and governance for a system that edits itself. All of it is
operational: what a process may write, what a boundary is worth, who signs off.

`[INF]` The book does not address alignment in the research sense, and Chapter 48 §5.6 is explicit
that its own governance argument has an unclosed gap — a loop that cannot edit a boundary can
propose changes that make it irrelevant, and nothing anyone has built detects that.

---

## It is not finished, and the last level says so loudest

The evolution loop of Level 5 rests on a controlled prototype: one benchmark family, a bounded
iteration count, non-additive gains, and weak regression prediction. Chapter 48 collects the limits
and Chapter 49 §5.5 states the honest position, which is neither *this is solved* nor *this is
unproven*:

- **What is demonstrated.** Harness quality is a large measurable surface, and an automated loop can
  improve it unattended across ten iterations.
- **What is not.** That gains compound, that they transfer across models or benchmarks, that the loop
  can predict its own damage, or that the containment list is complete.

Three limits are the handbook's own admissions rather than the source's: containment is a lower bound
with no completeness argument, indirect boundary erosion is detected by nothing, and the human
ability to re-fit a harness by hand decays exactly as the loop succeeds.

---

## It is not a substitute for measuring your own system

Every number in the book belongs to Atlas or to one of the two sources. `[INF]` The noise floor of
*your* benchmark, the share of *your* re-fit spent reading, and the shape of *your* task mix are the
three quantities most of the book's advice is conditional on, and none of them is transferable.

Chapter 41 §13.2 is the shortest version: for any improvement you have claimed in the last quarter,
what was the noise floor for that measurement? If the answer is unavailable, that is the most
valuable finding this book can give you, and it costs one afternoon.

---

## What it is

A derivation. Fifty chapters, each opening with a specific failure and deriving the mechanism that
prevents it, in dependency order, with every claim marked by where it came from. If you disagree
with a conclusion, the tag tells you whether to argue with the handbook or with a source.

---

**Begin:** [Level 0 — Foundations](../levels/level-0-foundations.md), or pick a track in
[F.1](f1-how-to-read-this-handbook.md).
