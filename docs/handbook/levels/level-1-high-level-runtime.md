# Level 1 — High-Level Runtime Architecture

*Chapters 4–9*

![The six-layer agent runtime](../../assets/diagrams/six-layer-agent-runtime.svg)

---

## What you will be able to do at the end

- Draw the entire runtime from memory — six layers, two process types, and the narrow waist between
  the runtime and your product.
- Name the unit anything belongs to, using five words instead of "the agent": Run, Episode, Step,
  Activity, Park.
- Classify any field in your schema into exactly one of four state categories, and say who is
  responsible for scoping it.
- Design a client contract for work that outlives the connection watching it.
- Place any moment of any run in two independent lifecycles, and say what happens if the process
  driving it disappears this instant.
- Route a design question to the axis that answers it — control, data, or event — before opening a
  file.

## What you must already hold

All of Level 0. Specifically: the harness boundary from Chapter 1, the four properties from Chapter
2, and the five mental models from Chapter 3. Level 1 uses MM1 (process) and MM5 (planes) almost
continuously, and Chapter 6 is essentially MM4 (quarantine) applied to state.

If you skipped Level 0 because you have built distributed systems before, read Chapter 2 §2.3
anyway. It is the map of which instincts transfer and which will cost you money.

## The questions this level answers

**1. What does the whole thing look like?**
Six layers, two process types, and a deliberately tiny opening between the runtime and your product
across which only commands and events travel. Chapter 4 is the map every later chapter zooms into,
and its deletion test is the sharpest single check in the book.

**2. What are the things it manipulates?**
Five nouns with lifetimes from milliseconds to weeks, arranged by a rule Chapter 5 calls the custody
gradient: the longer something lives, the less scarce the resource it may hold. Nearly every
scaling bug in this architecture is a violation of that one sentence.

**3. Who owns which state?**
Four categories — domain, run, model, harness — each with exactly one owner. Chapter 6 shows that
the two the reference architecture does not name are where the interesting failures live, and turns
the whole classification into CI checks.

**4. How does a person interact with work that outlives their connection?**
Chapter 7 builds the edge: a translator that decides nothing, with durable intent going in and
disposable views coming out. Getting that asymmetry backwards is the most common edge defect and the
hardest to see, because the wrong version demos beautifully.

**5. What happens over time, and what happens when a process dies?**
Chapter 8 separates the life of a goal from the life of a process, and shows that recovery must be
continuous rather than a boot-time activity — a defect whose severity is inversely proportional to
how often you deploy.

**6. How do I read all of this without getting lost?**
Chapter 9 gives three readings of one system and a routing table for deciding which one a question
belongs to. It is the synthesis chapter, and the shortest path to being useful in an unfamiliar
agent codebase.

## Reading notes

Chapters 4–9 are the only chapters where you should resist skipping ahead. Level 2 opens eleven
components one at a time, and each of those chapters assumes the vocabulary of Chapter 5, the state
categories of Chapter 6, and the flow routing of Chapter 9 without re-deriving them.

Chapter 4 is `Full` tier with nine diagrams; the rest are `Core` with five. If you read only one,
read Chapter 4 — but you will not be able to read Level 2 from it alone.

## Exit condition

> The reader can draw the whole system from memory before learning any component.

Concretely: given a stuck run, you can name which noun is stuck, which state it is in, which process
is responsible for it right now, what happens if that process dies this instant, how long anyone
takes to find out, and which of the three flows to read to answer why. That sentence is Level 1.

---

**Begin:** [Chapter 4 — The Complete Runtime](../chapters/04-complete-runtime-layers-and-process-topology.md)
