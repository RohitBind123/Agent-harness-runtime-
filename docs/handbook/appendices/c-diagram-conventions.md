# Appendix C — Diagram Conventions and Legend

Hand-written. Consolidates Phase 1 §6, which is where the chapters' `Appendix C` references point.
The one-page card is in [F.2](../front-matter/f2-notation-tags-and-diagram-legend.md); this is the
full specification, including the rules the linter enforces and the reasoning behind the awkward
ones.

The handbook carries roughly 290 figures. They are ASCII rather than rendered images for one reason:
a diagram that lives in the same file as the prose, diffs like the prose, and can be edited by
whoever is editing the sentence next to it stays true. A rendered image is stale within two chapters
and nobody notices.

---

## 1. The hard rules

Five, all mechanically checked by `tools/check_handbook.py`.

| Rule | Why |
|---|---|
| **Pure 7-bit ASCII** | No box-drawing characters, no Unicode arrows, no `§`, no em dashes. A diagram must survive a terminal, a diff, a code review tool, and a DOCX export unchanged |
| **At most 78 columns** | Fits a terminal, a side-by-side diff, and a printed page. Decompose rather than exceed |
| **An axis label, top-right** | `LAYER VIEW`, `TIME VIEW`, `STATE VIEW`, or `CONCEPTUAL VIEW` |
| **A caption, with its type** | `Figure NN.M -- what it shows (Dn Type)`. May wrap onto a second indented line |
| **One concern per diagram** | Control flow and data flow are never the same figure |

The ASCII rule is the one that costs the most and is worth the most. `[INF]` It is why a diagram
cites a section as `C41 sec 5.7` rather than `C41 §5.7`, and why `->` appears where a typographer
would want an arrow. Appendix I normalises the two citation forms back together precisely because
this rule splits them.

---

## 2. Box vocabulary

```
   +--------------+     kernel component; you do not write this
   +==============+     port; an extension point you implement
   +~~~~~~~~~~~~~~+     external system: provider, sandbox, your domain
   [[          ]]       durable store (a table)
   ((          ))       queue
   <<          >>       event
   {{          }}       a state, in a state diagram
```

The distinction that carries the most weight is the first two. `[INF]` A reader looking at a
Level 1 architecture diagram needs to know, without reading the caption, which boxes they will
implement. Chapter 4's narrow waist and Chapter 3 §5.1's "six ports and nothing else" are both
claims about which boxes are `+====+`, and drawing a port as an ordinary component erases the
argument.

`+~~~~+` marks the things you do not control: the model provider, the sandbox, the customer's
repository. Every one of them is a place where Chapter 2's four properties bite.

---

## 3. Arrow vocabulary

```
   ---->     synchronous call; control flows and returns
   ....>     asynchronous message or event; no return
   ====>     bulk data movement; annotate with volume
   --||->    passes through a gate; blocked until resolved
   --X       refused, blocked, or dropped
   <-->      bidirectional / negotiated
   ~~~~>     unreliable or best-effort (telemetry, progress)
```

Three of these encode claims rather than mechanics.

**`....>` means no return**, which is what makes an event different from a call. Chapter 22's outbox
exists because the two writes cannot be atomic; a diagram that draws event delivery as `---->` has
drawn a distributed transaction.

**`====>` must carry a volume.** Chapter 44's whole argument is a ratio — 9.4M tokens in, 11k out —
and a data-flow diagram without numbers is a picture of pipes. `[BP]` If you cannot annotate the
volume, the edge is probably control flow drawn in the wrong figure.

**`--X` is used for refusals that are structural**, not for errors. Chapter 46's Figure 46.1 draws
twelve of them, and each one means *there is no code path*, not *this would fail*. That distinction
is the safety argument of Level 5, and it needs a mark of its own.

---

## 4. The nine types

Every Full-tier chapter carries all nine, once each. Core carries five. The type is declared in the
caption so that a reader skimming figures can find the one they want.

| Type | Axis | Shows | Must contain |
|---|---|---|---|
| **D1** High-Level Architecture | LAYER | the subsystem in its surroundings | the boundary of what this chapter owns |
| **D2** Low-Level Architecture | LAYER | the subsystem opened up | its internal parts, named |
| **D3** Component Diagram | LAYER | named internals and their interfaces | method names on the edges |
| **D4** Sequence | TIME | one execution | **at least one failure branch** |
| **D5** Runtime Loop | TIME | the repeating cycle | every exit labelled `E1..En` |
| **D6** State Diagram | STATE | legal states and transitions | an illegal-transition note |
| **D7** Data Flow | LAYER | `====>` only | volumes |
| **D8** Control Flow | TIME | `---->` and decision diamonds only | no data edges |
| **D9** Event Flow | TIME | `....>` only | event names in `<< >>` |

**D4 must have a failure branch**, and this is the rule most likely to be skipped. `[INF]` A sequence
diagram of the happy path is a restatement of the prose. The chapter's actual content is what happens
when the third step fails, and drawing only the success case is how a design gets shipped with an
unconsidered branch.

**D5's exits must all be labelled.** Chapter 18's four exit conditions are the keystone of the whole
runtime, and an unlabelled loop diagram cannot express "there are exactly four ways out of this".

**D6 must name an illegal transition.** `[INF]` The legal transitions are usually obvious; the
illegal ones are where the chapter's argument is. Chapter 45's `{{ sealed }} -> {{ sealed }} with
different content` is the entire point of that chapter, and it appears nowhere else in the figure.

---

## 5. Numbered wires

More than four connections in one figure means numbered wires and a reference table:

```
   +-------------+  (1)   +-------------+
   |  producer   |------->|  consumer   |
   +-------------+        +-------------+

  Figure 22.1 -- The outbox (D1 High-Level Architecture)

  (1) one row per event, in the same transaction as the state change
```

**Letters are reserved for side channels.** `(A)`, `(B)` mark edges that are out-of-band with
respect to the figure's main flow — a pull rather than a push, a best-effort telemetry path, an
on-demand lookup. Chapter 44's Figure 44.1 uses `(A)` for the pointer-follow, which is the whole
mechanism that makes its reduction lossless and is not part of the pipeline it sits beside.

`[BP]` The wire table is where a diagram's claims live. A caption says what the figure shows; the
numbered notes say what each edge asserts, and they are the part worth reading twice.

---

## 6. The fourth axis

Chapters 0 through 3 use `CONCEPTUAL VIEW`, which the other three axes do not cover.

`[INF]` Foundational chapters draw models rather than components — a taxonomy of system generations,
a mapping between an agent's parts and an operating system's — and those have no layer, no time, and
no state. Forcing them into `LAYER VIEW` would be a false claim about what the figure depicts. The
axis was added after Chapters 0–3 were written, which is recorded in CONVENTIONS.md §7 so that the
blueprints are not silently contradicted.

Light-tier figures use `(conceptual)` as their type in the caption rather than a `Dn` label.

---

## 7. Figure budgets

| Tier | Figures | Used by |
|---|---|---|
| **Full** | exactly 9, one of each type | Level 2 entirely; the heaviest chapters of Levels 3 and 5 |
| **Core** | exactly 5 | Level 4 entirely; most of Level 3; half of Level 5 |
| **Light** | 2–4, declared in the header | Chapters 0–3 |

The count declared in a chapter's header must equal the number of `Figure` captions in it exactly,
and the linter fails the chapter otherwise. `[INF]` That is a stricter rule than it looks: it means a
figure cannot be quietly dropped during editing, and it means adding one is a deliberate act that
changes the header.

**Plan a Full chapter's nine figures before writing it.** `[BP]` Nine ASCII figures in document order
cannot be retrofitted cheaply — Chapter 10 needed a renumbering pass because two were added late.
Decide the D1–D9 set and which section each lands in first.

---

## 8. Where each type usually lands

Not a rule, and consistent enough across fifty chapters to be worth knowing.

| Section | Full tier | Core tier |
|---|---|---|
| §3 High-Level Architecture | D1 | D1 |
| §4 Low-Level Decomposition | D2, D3 | D2 |
| §5 (chapter-specific) | one or two, usually D7 or D8 | one |
| §6 Runtime Sequence | D4, D5 | D4 |
| §7 State Management | D6 | D6 |
| §10 Communication | D7, D8, D9 | — |

---

**See also:** [Appendix B — Naming Conventions](b-naming-conventions.md) ·
[CONVENTIONS.md §3](../CONVENTIONS.md) for the authoring card ·
`tools/check_handbook.py` for what is enforced mechanically.
