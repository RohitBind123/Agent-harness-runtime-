```
  Level 2 · Chapter 15
  AGENT-COMPUTER INTERFACE DESIGN
  Requires   C13 Reasoning Engine, C14 Tool Execution Engine
  Unlocks    C44 Agent Debugger, C46 Evolve Agent
  Diagrams   Full (9)
```

# Chapter 15 — Agent-Computer Interface Design

---

## 1. Motivation

### 1.1 Cold open

Atlas is asked to add a null check to a 400-line file. It reads the file, works out that the guard
belongs before line 231, and calls `edit_file(path, line=231, text=...)`.

The edit lands at line 231 of the file. The model had counted to 231 in the content it was shown,
which began after a four-line licence header the read tool strips as noise.

The guard is now inside a different function. The file still parses. The tests still pass, because
the new branch is unreachable. Atlas reads the file back, sees its guard present, and reports
success.

Reviewers catch it on the third such pull request, and the team opens a bug against the model's
reasoning. The model reasoned correctly throughout. It was asked to count lines in one
representation and address them in another, and neither tool's description mentioned that the two
representations disagreed about what line 1 was.

Nobody would design a human interface this way.

### 1.2 In plain language

Chapter 14 built the machinery that runs tools. This chapter is about what those tools *feel like*
to the thing using them.

If you have ever used a badly designed form — one that says "invalid input" without saying which
field, or that silently reformats what you typed — you already understand the problem. The form
worked. The database was updated correctly. You still got it wrong three times, because the
interface did not tell you what it needed.

A model is in that position on every single call, and worse off than you were in two respects. It
cannot look at the screen to see what happened; it knows only what the tools hand back. And it
arrives with no memory of having made this mistake before, so it will make it again tomorrow.

This chapter is about designing that surface deliberately: which tools exist and how big each one
is, what arguments the model has to construct, what it gets back, and — most importantly — what it
is told when it gets something wrong.

The reason this has its own chapter is a practical one. When a model keeps making the same mistake,
the instinct is to add a line to the instructions telling it not to. That is the weakest available
fix. Usually the right fix is to change the tool so the mistake is no longer possible.

### 1.3 Why this chapter exists

Chapter 14 can be entirely correct and the system still perform badly. A tool that dispatches,
validates, gates, truncates, and records flawlessly can still be one the model cannot use — and the
resulting failures look like reasoning failures, get attributed to the model, and get "fixed" in the
system prompt, which `[AHE §4.4.1]` measured as the weakest surface there is.

`[BP]` The name comes from the observation that agents interact with computers through an interface
in the same sense that people do, and that the interface is designable. The discipline it borrows
from is human factors, and §2.1 argues the borrowing is closer than it first appears.

`[INF]` There is also a Level 5 reason, and it is why Phase 2 added this chapter at all: **the
Evolve Agent's most productive edits are ACI edits.** Tool descriptions and tool implementations
were two of the highest-value components in the ablation, and most of what a useful edit to either
changes is what this chapter calls the interface rather than the mechanism. A loop that cannot
distinguish an ACI defect from a capability gap will spend its iterations in the wrong place.

### 1.4 What previous framings got wrong

**"The model should have known."** The cold open, as a diagnosis. It is the same claim as "the pilot
should have pulled the right lever", and §2.1 explains why aviation stopped accepting it.

**"Add it to the system prompt."** The default response to a model mistake, and the weakest
enforcement level available (Chapter 1). §5.5 gives the routing rule for where a fix actually
belongs.

**"More tools means more capability."** Every tool definition taxes every model call (Chapter 11
§2.3), and a large flat tool list makes selection harder rather than easier. §5.2 is about
granularity, and the answer is not "more".

**"Errors are for logs."** `[INF]` An error message reaching a model is not a diagnostic record; it
is the only teaching the model will receive, delivered at exactly the moment it is trying to act.
§5.4 treats error text as a first-class design surface, and it is the highest-leverage one in the
chapter.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

An aircraft cockpit.

In the 1940s, experienced pilots kept retracting the landing gear of parked aircraft. Not novices —
competent, trained, careful pilots, repeatedly, across airframes. The investigation that followed
did not conclude that pilots needed more training. It found that the gear lever and the flap lever
were identical toggles mounted side by side, and that after landing a pilot reaching for the flaps
would sometimes reach for the gear.

The fix was to change the levers. The gear control got a small rubber wheel on the end; the flap
control got a small wedge shaped like a flap. The error rate collapsed. `[BP]` This is the founding
example of human factors engineering, and its lesson is one sentence: **when competent operators
repeatedly make the same mistake, the interface is the defect.**

That sentence, applied to a model instead of a pilot, is this entire chapter. The cold open is two
identical levers: a read view that starts at the licence header and a write view that starts at line
1, mounted side by side, with nothing to distinguish them.

**Where the analogy breaks**, in two directions, and both make the model's situation harder.

A pilot accumulates thousands of hours in one cockpit. Familiarity does real work, and a control
that is confusing on day one may be automatic by month six. The model has no such trajectory: it
arrives fresh on every call with no memory of yesterday's mistake, so **the interface must teach
itself at every single use**. There is no learning curve to climb, and no benefit from consistency
across sessions that a memory could exploit.

And a pilot can look out of the window. When an instrument disagrees with reality, there is a
second channel. The model has no window: everything it knows about the environment arrives through
the tools this chapter designs. `[INF]` That makes the interface not merely the control surface but
the entire sensory apparatus, which is why §5.3 treats what a tool *returns* as seriously as what it
does.

### 2.2 Why ACI is a separate discipline

```
  1. Ch 14 built the mechanism: resolve, validate, gate, invoke,
     truncate, record. All of it can be correct.
  2. A correct mechanism can still be unusable. The cold open's tools
     both worked exactly as specified.
  3. The model's behaviour is bounded by what it can PERCEIVE and
     EXPRESS through the tools. That is a property of the interface,
     not of the mechanism.
  4. So there are two independent quality axes: does the tool work,
     and can the model use it correctly.
  5. They are measured by different evidence. Axis one: unit tests.
     Axis two: reading trajectories of runs that went wrong (Ch 44).
  6. They are fixed by different edits. Axis one: change behaviour.
     Axis two: change verbs, argument shapes, return format, and error
     text -- frequently with NO behaviour change at all.
  7. A team with only axis one responds to a model's mistakes by
     editing the prompt or by blaming the model. Both are the wrong
     surface (Ch 1).
  8. Therefore the second axis needs its own name, its own evidence,
     and its own catalogue of edits. That is the ACI.
```

Step 6 is the one that makes this a chapter rather than a paragraph. `[INF]` An ACI edit changes
what the model does without changing what the system can do — the capability is identical before and
after. That is a strange category of change, it is invisible to every functional test, and it is
where a large fraction of achievable improvement sits.

### 2.3 The four surfaces

`[BP]` Everything the model experiences of a tool falls into one of four:

| Surface | The model's question | Failure looks like |
|---|---|---|
| **Verbs** | what can I do? | the wrong tool chosen, or a general tool used for a specific job |
| **Arguments** | what must I construct? | valid-shaped arguments with wrong meaning — the cold open |
| **Results** | what happened? | correct action, wrong conclusion drawn |
| **Errors** | what did I do wrong? | the same mistake repeated; retry loops |

`[INF]` The order is deliberate: it is roughly the order of increasing leverage and decreasing
attention. Teams argue about verbs, occasionally revise arguments, rarely think about result shape,
and almost never design error text — which is the inverse of where the returns are.

### 2.4 The mental model to carry

> **The model is a competent operator with no memory and no window. Every mistake it makes twice is
> an interface defect, and the fix is almost never in the instructions.**

`[INF]` "Twice" is doing real work in that sentence. A single mistake may be a genuine reasoning
failure and is weak evidence. A mistake that recurs across runs, models, or tenants is a property of
the interface, because that is the only thing those runs had in common.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  What the MODEL experiences        |  What the SYSTEM does (Ch 14)
                                    |
  +------------------------------+  |  +---------------------------+
  |  I can do these things       |  |  | registry.descriptions_for |
  |  (VERBS)                     |<-|--|  scoped tool list         |
  +------------------------------+  |  +---------------------------+
              |                     |
              v                     |
  +------------------------------+  |  +---------------------------+
  |  I must construct this       |  |  | schema + argument prose   |
  |  (ARGUMENTS)                 |<-|--|  types, enums, examples   |
  +------------------------------+  |  +---------------------------+
              |                     |
              | proposes            |
              v                     |
  ..............................    |  ...........................
  :  THE ACI BOUNDARY          :    |  : dispatch, gate, invoke  :
  :  everything above this is  :    |  : (Ch 14 sections 4-5)    :
  :  DESIGN; below is MECHANISM:    |  :.........................:
  :............................:    |             |
              ^                     |             v
              |                     |  +---------------------------+
  +------------------------------+  |  | normalise + truncate      |
  |  This is what happened       |<-|--|  shaped for the model     |
  |  (RESULTS)                   |  |  +---------------------------+
  +------------------------------+  |
              ^                     |
              |                     |
  +------------------------------+  |  +---------------------------+
  |  This is what I did wrong    |<-|--| error normalisation       |
  |  (ERRORS)                    |  |  |  the teaching surface     |
  +------------------------------+  |  +---------------------------+
                                    |
     model state (Ch 6)             |     harness + runtime

  Figure 15.1 -- The ACI as the surface between model and mechanism
                 (D1 High-Level Architecture)
```

`[INF]` The diagram has no new components in it, and that is the point worth sitting with. The ACI
is not a layer you build; it is a *view* of components Chapter 14 already built, taken from the
model's side. Every box on the left is produced by a box on the right, and the design question is
always the same: given that the right-hand box must do what it does, what should the left-hand box
look like?

That framing is what makes ACI work tractable. You are not adding machinery. You are choosing the
shape of what already exists.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  THE FOUR SURFACES, opened

  VERBS -- what exists, and at what granularity
  +--------------------------------------------------------------+
  | too coarse:  tool.shell.run_command                           |
  |              one verb, unbounded effect, ungateable,          |
  |              untruncatable, unattributable                    |
  |                                                              |
  | too fine:    40 verbs, one per operation                      |
  |              tool tax on every call (Ch 11); selection        |
  |              becomes the hard problem                         |
  |                                                              |
  | the shape:   6-15 verbs covering the work, each with a        |
  |              clear effect tag and a bounded result            |
  +--------------------------------------------------------------+

  ARGUMENTS -- what the model must construct from what it can see
  +--------------------------------------------------------------+
  | hostile:  line numbers the model must COUNT                   |
  |           offsets into a representation it was not shown       |
  |           free-form strings with implicit syntax (globs)       |
  |                                                              |
  | friendly: anchors the model can QUOTE                         |
  |           enums it can choose from                            |
  |           identifiers a previous result handed it              |
  +--------------------------------------------------------------+

  RESULTS -- what comes back, and what it implies
  +--------------------------------------------------------------+
  | shape it for the DECISION, not for the data:                  |
  |   what changed, not the whole object                          |
  |   what to do next, where there is an obvious next step        |
  |   explicit emptiness (Ch 14 empty_means)                      |
  |   stable formatting, so the same thing reads the same way     |
  +--------------------------------------------------------------+

  ERRORS -- the only teaching the model receives
  +--------------------------------------------------------------+
  | diagnostic (bad):  "Error: invalid input"                     |
  | descriptive:       "Line 231 is out of range; file has 187"   |
  | INSTRUCTIVE (good):"Line 231 is out of range; the file has    |
  |                     187 lines. Line numbers are 1-based over  |
  |                     the FULL file including headers. Call     |
  |                     read_file with show_line_numbers=true to  |
  |                     see them."                                |
  +--------------------------------------------------------------+

  Figure 15.2 -- The four surfaces (D2 Low-Level Architecture)
```

### 4.1 The gradient in each block runs the same way

`[INF]` Read the four blocks together and one pattern repeats: the bad end of each surface asks the
model to *hold state* that it has no way to hold, and the good end lets it *quote something it was
shown a moment ago*.

A line number is state the model must compute and carry. An anchor string is something it can copy
out of the previous result. A tool that returns an opaque handle and accepts that handle back is
requiring no memory at all; a tool that requires an offset is requiring the model to have counted
correctly in a representation nobody guaranteed matched.

That gradient is the closest thing this chapter has to a general rule, and §5.3 turns it into a
design heuristic.

```
                                                            LAYER VIEW

  Where each surface is authored, and who may edit it.

   +---------------------+        +-------------------------+
   | Tool registry       |        | Editable by             |
   | (Ch 14)             |        |                         |
   +----------+----------+        +-------------------------+
              |
     +--------+--------+--------------+--------------+
     |        |        |              |              |
     v        v        v              v              v
  +------+ +------+ +--------+  +-----------+  +-----------+
  |VERBS | | ARGS | |RESULTS |  | ERRORS    |  |EFFECT TAG |
  +---+--+ +---+--+ +----+---+  +-----+-----+  +-----+-----+
      |        |         |            |              |
      |        |         |            |              +--> NOT editable
      |        |         |            |                   by the Evolve
      |        |         |            |                   Agent (Ch 14
      |        |         |            |                   section 14)
      v        v         v            v
  +--------------------------------------------+
  | tool_descriptions/*.tool.yaml   -- prose    |  evolve: YES
  | tools/**/*.py                   -- code     |  evolve: constrained
  | middleware/**/*.py              -- uniform  |  evolve: constrained
  +--------------------------------------------+
              |
              v
   +----------+----------+
   | Context system      |  descriptions become part of every
   | (Ch 11)             |  model call: the tool tax
   +---------------------+

  Figure 15.3 -- Where the ACI is authored (D3 Component Diagram)
```

`[INF]` The important edge is the one at the bottom. Every ACI decision lands in the context on every
call, which means **ACI design and context budget are the same conversation**. A richer error
message costs nothing until it is a tool description; a longer description costs on every call
forever. §12 makes that trade explicit.

---

## 5. Designing the Four Surfaces

### 5.1 Representation agreement: the cold open's rule

`[INF]` The rule the cold open needed, stated generally:

> **Any two tools that address the same object must agree on how it is addressed. If a read tool
> and a write tool disagree about what line 1 is, one of them is wrong regardless of which one you
> change.**

Three ways to satisfy it, in descending order of preference:

1. **Remove the shared coordinate.** `edit_file(path, find, replace)` needs no line numbers at all,
   so the two views cannot disagree. The model quotes text it was shown.
2. **Make the coordinate visible.** If line numbers are unavoidable, `read_file` shows them, so the
   model reads rather than counts.
3. **Make the coordinate checkable.** `edit_file(path, line, expect_line_starts_with=...)` fails
   loudly when the model's belief about line 231 is wrong.

The cold open's system did none of the three, and the third is worth noting even where the first is
available: it converts a silent wrong edit into a loud, instructive failure, which is the difference
between eleven days and one run.

### 5.2 Verb granularity

`[INF]` The two failure directions, and why the middle is not a compromise:

**Too coarse.** One `run_command` tool is maximally capable and destroys everything Chapter 14 built.
It cannot carry a meaningful effect tag, because some commands read and some delete. It cannot be
truncated sensibly, because output shape varies per command. It cannot be gated proportionately,
because gating every shell call makes approval meaningless and gating none is unsafe. And it cannot
be attributed: "the model ran a command" tells Chapter 44 nothing about what it was trying to do.

**Too fine.** Forty verbs cost forty definitions in Chapter 11's stable band on every call, and they
make selection the hard problem — the model now spends its reasoning deciding between
`find_file_by_name` and `find_file_by_pattern` rather than doing the work.

`[INF]` The test that resolves most cases: **can this verb carry one effect tag, one truncation
policy, and one clear description of when to use it?** If a proposed tool needs "it depends" for any
of the three, it is two tools. If two tools have the same answer for all three, they are one tool.

### 5.3 Arguments the model can quote, not compute

The gradient from §4.1, as a design heuristic:

| Prefer | Over | Because |
|---|---|---|
| an anchor string to find | a line number | quotable from the previous result |
| an opaque handle from a prior result | a reconstructed path | no state to carry |
| an enum | a free-form string | the valid set is visible |
| a structured field | embedded syntax (globs, regexes) | no second language to get right |
| explicit units in the name (`timeout_seconds`) | bare numbers (`timeout`) | no unit ambiguity |

`[INF]` The last row looks trivial and is not. A model choosing `timeout=30` for a parameter that
means milliseconds produces a tool that times out instantly, forever, in a way that reads as
flakiness. The name is the only place that ambiguity can be resolved, because the model cannot check
the implementation.

### 5.4 Errors are instructions, not diagnoses

The highest-leverage surface in the chapter, and the one that receives the least design attention.

`[INF]` An error message reaching a model has exactly one job: **make the next attempt correct.** It
is not a log line, not a stack trace, and not a record for a human. Four properties:

| Property | Bad | Good |
|---|---|---|
| **Specific** | "invalid input" | "`pattern` matched no files" |
| **Diagnostic** | "invalid input" | "`src/api` contains no wildcard, so it matched only a literal file of that name" |
| **Instructive** | — | "For a directory's contents, use `src/api/**`" |
| **Bounded** | a 400-line stack trace | the three lines above |

`[INF]` The bounded property matters more than it seems. A stack trace is Chapter 9's amplifier
wearing a disguise: it is large, it enters the context, and it re-enters on every subsequent step.
An error that is longer than the result it replaced has made things worse in two ways at once.

The test for an error message is behavioural, not aesthetic: **would a competent operator who had
never seen this system before get it right on the next attempt?** If not, the message is
incomplete — and unlike a human, the model will not go and read the source.

### 5.5 Where a fix belongs

`[INF]` The routing rule this chapter exists to provide. When a model makes a mistake, the fix goes
at the *weakest level that can actually prevent it* (Chapter 1's hierarchy):

| The mistake | Fix at | Not at |
|---|---|---|
| Chose a tool that cannot do the job | verbs — the right tool does not exist | the prompt |
| Constructed a wrong-but-valid argument | arguments — remove the coordinate (§5.1) | the prompt |
| Drew a wrong conclusion from a result | results — say what emptiness means | the prompt |
| Repeated a mistake after being told | errors — the message was not instructive | the prompt |
| Did something forbidden | middleware or the effect tag — code enforces | the prompt |
| Preferred a worse approach | the prompt, or a skill | — |

`[INF]` Only the last row belongs in the prompt, and it is the only row where the model's choice was
*informed and suboptimal* rather than misinformed. Everything above it is an interface defect wearing
a reasoning-failure costume. That table is the practical payload of the chapter.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  The same failure, through two interfaces.

  A. HOSTILE ACI
  model            tool engine        file
    |                   |               |
    |-- read_file(p) -->|-------------->|
    |<-- 400 lines, no numbers, header stripped ---|
    |  [counts to 231 in what it was shown]        |
    |-- edit_file(p, line=231, text) -->|          |
    |                   |-------------->| writes at TRUE line 231
    |<-- OK ------------|               |
    |  [believes it succeeded; it did not]         |
    |                                              |
    |  cost: 2 calls. Outcome: silently wrong.     |
    |  Detection: a human reviewer, 11 days later. |

  B. INSTRUCTIVE ACI
  model            tool engine        file
    |                   |               |
    |-- read_file(p) -->|-------------->|
    |<-- 400 lines, EACH PREFIXED WITH ITS TRUE NUMBER ---|
    |  [reads 231 rather than counting to it]      |
    |-- edit_file(p, line=231,                     |
    |             expect_starts_with="def check") ->|
    |                   |-------------->| verifies the anchor
    |<-- OK, applied at line 231 -------|
    |                                              |
    |  cost: 2 calls. Outcome: correct.            |

  C. THE SAME MISTAKE, CAUGHT
    |-- edit_file(p, line=227,                     |
    |             expect_starts_with="def check") ->|
    |<-- FAILED: line 227 starts with "# Copyright".|
    |    Line numbers are 1-based over the full     |
    |    file including headers. "def check" is at  |
    |    line 231. Retry with line=231.             |
    |-- edit_file(p, line=231, expect...) --------->|
    |<-- OK ---------------------------------------|
    |                                              |
    |  cost: 3 calls. Outcome: correct, self-       |
    |  corrected, and no human involved.           |

  Figure 15.4 -- One failure through three interfaces (D4 Sequence)
```

### 6.1 What the three branches cost

`[INF]` Branch A is cheapest per run and catastrophic in aggregate. Branch B is the same cost as A
and correct. Branch C costs one extra model call and is the one worth designing for, because it is
the only branch that survives the model being wrong.

That is the asymmetry to hold onto: **B optimises the case where the model gets it right; C
optimises the case where it does not, and the second is the one that determines whether the system
is trustworthy.** An interface that only works when the model is correct is not an interface, it is
a hope.

The extra call in branch C is also the honest cost of the chapter. Instructive errors and verifying
arguments are not free; they trade tokens for correctness, and §12 says when that trade is wrong.

```
                                                             TIME VIEW

  The model's loop through the ACI. This is not a runtime component
  loop -- it is the loop the model is in, which is what the ACI
  designs for.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | PERCEIVE             |  what the last result said     |
   |  (RESULTS surface)   |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | SELECT               |  which verb applies            |
   |  (VERBS surface)     |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | CONSTRUCT            |  build the arguments           |
   |  (ARGUMENTS surface) |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     /accepted\  no --> +---------------------+           |
     \  ?     /         | ERRORS surface      |           |
      \      /          |  instructive? ------|---------->+ E1 corrected
        | yes           |  diagnostic only? --|---------->+ E2 LOOP
        v               +---------------------+             (the failure
   +----+-----------------+                                  mode)
   | effect happens       |                                 |
   +----+-----------------+                                 |
        |                                                   |
        v                                                   |
      /   \                                                 |
     /result \ misread --> E3 silent wrong conclusion       |
     \ clear? /            (the cold open)                  |
      \      /                                              |
        | yes                                               |
        v                                                   |
      E4 progress ------------------------------------------+

  Exits:
    E1  error was instructive; next attempt succeeds
    E2  error was diagnostic only; the model retries the same
        thing. This is the retry loop, and it is measurable
        (section 13.1)
    E3  result was misread; the run continues confidently wrong.
        The most expensive exit, and the hardest to detect
    E4  progress

  Figure 15.5 -- The model's perceive-select-construct loop
                 (D5 Runtime Loop)
```

`[INF]` E2 and E3 are the two ACI failure modes, and they have opposite signatures. E2 is loud and
cheap to detect: the same tool call, repeated, with the same arguments. E3 is silent and shows up
only as a bad outcome much later. A team instrumenting one usually instruments E2, which means the
more expensive failure is the one nobody is watching.

---

## 7. State Management

```
                                                            STATE VIEW

  The model's BELIEF about an object, across a tool interaction.
  This is model state (Ch 6): rebuilt every call, never stored.

            +---------------------+
            | {{ NO BELIEF }}     |  has not looked
            +----------+----------+
                       | read
                       v
            +---------------------+
            | {{ BELIEF FORMED }} |  from what the RESULT said
            +----+-----------+----+
                 |           |
     result was  |           | result was ambiguous or
     unambiguous |           | used a hidden representation
                 |           v
                 |    +------+--------------+
                 |    | {{ FALSE BELIEF }}  |  the cold open
                 |    +------+--------------+
                 |           |
                 |           | acts on it
                 v           v
            +---------------------+
            | {{ ACTED }}         |
            +----+-----------+----+
                 |           |
      verified   |           | not verified
      by an      |           |
      anchor     |           v
                 |    +------+--------------+
                 |    | {{ UNDETECTED }}    |  E3: confidently wrong,
                 |    +---------------------+  no signal anywhere
                 v
            +---------------------+
            | {{ CONFIRMED }}     |
            +---------------------+

  The ACI's job, stated as a state machine: make FALSE BELIEF hard to
  enter, and make UNDETECTED impossible to stay in.
    * section 5.1 removes the shared coordinate  -> fewer false beliefs
    * anchors verify at write time               -> no UNDETECTED
    * section 5.4 instructive errors             -> exit false belief
    * Ch 14 empty_means                          -> fewer false beliefs

  Figure 15.6 -- The model's belief state (D6 State Diagram)
```

### 7.1 There is no ACI state

`[INF]` Worth stating plainly because the diagram invites the opposite reading: nothing in this
chapter is stored anywhere. The ACI is a property of the descriptions, schemas, result formats, and
error strings that Chapter 14's registry already holds, and the belief states above live entirely
inside one model call.

That has a practical consequence. **An ACI change takes effect on the next call, for every run,
with no migration.** It is the cheapest class of change in the system to deploy and the most
expensive to evaluate, because its effect is distributional rather than functional — which is why
§13 measures it with rates rather than with tests.

---

## 8. Internal APIs

There is no `ACIPort`. The ACI is a design property of Chapter 14's registry entries, and the
honest way to express it in code is as the shape those entries are required to have:

```python
from typing import Protocol


class ToolDescription(Protocol):
    """The prose surface. Every field here is an ACI decision."""

    summary: str                      # VERBS: when to reach for this
    when_to_use: str                  # VERBS: and when not to
    arguments: Mapping[str, ArgumentSpec]
    returns: ReturnSpec               # RESULTS: including empty_means
    failure_modes: Mapping[str, str]  # ERRORS: text, per named failure


class ArgumentSpec(Protocol):
    """ARGUMENTS. `examples` must include at least one WRONG usage and
    what it does instead (Ch 14 section 5.1); a spec that only shows
    correct usage teaches the shape and not the boundary."""

    type: str
    required: bool
    description: str
    examples: tuple[str, ...]
    counter_examples: tuple[tuple[str, str], ...]   # (input, what happens)


class ToolError(Protocol):
    """ERRORS. The signature is the argument of section 5.4: a message
    that cannot name what to do next is not finished."""

    what_happened: str        # "line 227 starts with '# Copyright'"
    why: str                  # "line numbers are 1-based over the full file"
    what_to_do: str           # "the anchor 'def check' is at line 231"

    def render(self) -> str:
        """Bounded. Never a stack trace: section 5.4's fourth property."""
```

`[INF]` `ToolError` having three required fields rather than a single `message` is the chapter's one
piece of enforceable design. A developer writing an error must fill in `what_to_do`, and finding
that they cannot is the signal that the failure mode has not been thought through. It is the same
technique Chapter 11 used with `budget_share`: make the required thinking a required field.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ArgumentSpec:
    type: str
    required: bool
    description: str
    examples: tuple[str, ...]
    counter_examples: tuple[tuple[str, str], ...]
    unit: str | None = None           # section 5.3: name the unit


@dataclass(frozen=True)
class ReturnSpec:
    description: str
    empty_means: str                  # Ch 14; the E3 defence
    stable_format: bool               # same input, same rendering
    next_step_hint: str | None        # where there is an obvious one


@dataclass(frozen=True)
class ACIMetrics:
    """Per tool, per window. The only way to measure a surface whose
    effect is distributional rather than functional (section 7.1)."""

    calls: int
    repeated_identical_calls: int     # E2: the retry loop
    schema_rejections: int            # Ch 14's event, by tool
    empty_results: int                # the cold open's fingerprint
    error_then_success: int           # errors that TAUGHT
    error_then_same_error: int        # errors that did not
```

`[INF]` The last two fields are the chapter's central measurement and are worth naming as a ratio:
`error_then_success / (error_then_success + error_then_same_error)` is the **instructiveness** of a
tool's error messages, computed from behaviour rather than from opinion. A tool whose errors are
diagnostic-only sits near zero on it, and no amount of arguing about wording moves the number.

---

## 10. Communication

```
                                                            LAYER VIEW

  descriptions   registry ====> context system  ~6-25 KB  EVERY call
                                                           (the ACI's
                                                            standing cost)
  arguments      model    ====> engine          ~1-5 KB
  results        engine   ====> model           ~1-64 KB  after Ch 14
                                                           truncation
  errors         engine   ====> model           ~0.2-2 KB  <-- bounded
                                                           by section 5.4

  The trade this chapter makes:
     +200 bytes of description, on every call, forever
     -1 wasted tool call, on the runs that would have got it wrong

  Figure 15.7 -- What the ACI costs and returns (D7 Data Flow)
```

```
                                                             TIME VIEW

  registry ------> context system   which verbs exist for this run
  model ---------> engine           selects a verb, constructs args
  engine --------> model            result, shaped for a decision
  engine --------> model            error, shaped for the NEXT attempt
  model --X       verbs             REFUSED: it cannot invent a tool
  model --X       effect tag        REFUSED: registry only (Ch 14)
  prompt --X      enforcement       prose asks; only code compels

  Figure 15.8 -- Who shapes what the model perceives
                 (D8 Control Flow)
```

```
                                                             TIME VIEW

  << tool.schema.rejected >>   ....>  Ch 14's event, read HERE as an
                                      ACI signal rather than a defect
  << tool.result.truncated >>  ....>  result shaping is failing to fit
  << aci.retry_loop.detected >>....>  N identical calls in one run;
                                      E2, made durable because it is
                                      the cheapest evidence of an
                                      uninstructive error

  NOT events:
    an error returned to the model   part of a result; in the trajectory
    a description edit              a git commit (Ch 43)
    ACI metrics                     telemetry, aggregated per window

  Figure 15.9 -- What ACI failure makes durable (D9 Event Flow)
```

`[INF]` `aci.retry_loop.detected` is the one event this chapter adds, and it is deliberately cheap:
three identical tool calls with identical arguments in one run, emitted once. It is the only
automatic detector for E2 in the whole architecture, and Chapter 44 uses it as a first-pass filter
over trajectories, because a run containing one is guaranteed to contain an interface defect.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 11 Context | descriptions are a standing per-call cost | ACI richness is a budget decision |
| Ch 14 Tools | this chapter designs what that one dispatches | mechanism versus surface |
| Ch 34 Observability | `ACIMetrics`, instructiveness ratio | distributional effects need rates |
| Ch 44 Agent Debugger | retry loops as a trajectory filter | where to look first |
| Ch 46 Evolve Agent | ACI edits are the highest-yield edits available | most iterations land here |
| Ch 48 Limits | ACI edits interact through one context budget | non-additivity applies sharply |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Representation disagreement | two tools address one object differently | silent wrong edits | remove or verify the coordinate — the cold open |
| Diagnostic-only errors | "invalid input" with no next step | `error_then_same_error` rate | three-field `ToolError` (§5.4) |
| Retry loop | uninstructive error, model repeats itself | `aci.retry_loop.detected` | make the error instructive |
| Silent misread result | ambiguous result, confident conclusion | none automatic; outcome quality only | `empty_means`, stable formats, anchors |
| One coarse verb | `run_command` for everything | effect tag cannot be assigned | split by effect and result shape (§5.2) |
| Verb sprawl | a tool per operation | Ch 11 stable-band tokens rising | merge tools with identical tag, policy, and usage |
| Unit ambiguity | `timeout=30`, meaning unclear | instant timeouts that read as flakiness | put the unit in the name |
| Unbounded error text | a stack trace returned to the model | context spikes after failures | bound errors (§5.4) |
| Prompt used as the fix | "remember to pass a glob" in instructions | the mistake recurring anyway | route with §5.5's table |
| Description growth | richer prose, unbounded | tool tax rising | §12's trade, made explicitly |

`[INF]` Row four has no automatic detector and, unlike Chapter 14's meaning-drift row, not even a
review rule — because the failure is in the *model's* reading of a well-formed result, which nothing
in the system observes. The only evidence is a run that went wrong for no visible reason, which
makes it Chapter 44's problem rather than a monitoring one. Naming it as undetectable here is more
useful than implying a control exists.

---

## 12. Scalability

### 12.1 ACI richness is bought from the context budget

Every improvement in this chapter has the same cost shape: more prose in the description, paid on
every model call in the system, forever (Chapter 11 §2.3).

| Improvement | Standing cost | Returns |
|---|---|---|
| `empty_means` on a result | ~20 tokens | removes a whole class of false belief |
| A counter-example per argument | ~30 tokens | removes the cold open's class |
| `when_to_use` on a verb | ~25 tokens | fewer wrong-tool selections |
| Instructive error text | **zero** standing cost | paid only when the error fires |

`[INF]` The fourth row is the free lunch and the reason §2.3 ordered the surfaces as it did. Error
text costs nothing until something goes wrong, at which point it replaces text that was going to be
returned anyway. **Improving error messages is the only ACI work with no standing cost**, which
makes it the correct place to start, always.

### 12.2 When the trade goes the wrong way

`[INF]` A description that has grown to 400 tokens to prevent a mistake occurring in 1% of runs is
paying on 100% of calls to fix 1% of them. The arithmetic:

```
  worth it when:   p(mistake) * cost(mistake) > tokens_added * calls
```

Where `cost(mistake)` includes the wasted calls *and* the probability it goes undetected. `[INF]`
That last term is why the cold open's fix is clearly worth it despite being verbose: an undetected
wrong edit reaching a customer's repository has a cost that is not measured in tokens.

Progressive disclosure (Chapter 11 §5.4) is the escape valve: a long description can be a short
summary plus a body the model loads when it selects that tool.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Instructiveness ratio, per tool | §9's measurement of error quality | below target on a high-traffic tool |
| `aci.retry_loop.detected` per run | E2, the loud failure | any sustained rise |
| Repeated identical calls, per tool | the same, per surface | reported, ranked |
| Empty-result rate | the cold open's fingerprint (Ch 14) | step change after a deploy |
| Schema rejection rate, per argument | which argument is hard to construct | ranked, reviewed monthly |
| Wrong-tool rate | selected a verb that cannot do the job | reported |
| Description tokens, per tool | the standing cost | ranked; the top three reviewed |

`[INF]` "Schema rejections ranked by argument" is the single most actionable list in this chapter.
It names, in order, the arguments models find hardest to construct — and every entry on it is an ACI
defect with a known fix from §5.3.

### 13.2 The ACI review, done from trajectories

`[BP]` The practice, once a month, and it is not a code review:

1. Take the runs that failed or took more steps than the median.
2. Read what the model *saw* before each wrong move — the result or error immediately prior.
3. For each, ask §2.4's question: would a competent operator with no memory have got this right?
4. Where the answer is no, write down which of the four surfaces failed.
5. Fix the errors first (no standing cost), then arguments, then results, then verbs.

`[INF]` Step 2 is the part that requires Chapter 16's trajectory capture to have stored the *inputs*
and not only the outputs. A trajectory that records what the model did without recording what it was
looking at cannot support this review at all, which is the practical argument for capturing
assembled context that Chapter 11 §14 made from the other direction.

### 13.3 The test for an error message

```python
@pytest.mark.parametrize("tool_id,bad_input", KNOWN_MISUSES)
async def test_error_messages_are_instructive(
    tool_id: str, bad_input: dict, engine: ToolPort, fake_model: FakeModelPort
) -> None:
    """An error is instructive if a model that receives it succeeds on
    the next attempt. This is measurable, not a matter of taste."""
    first = await engine.dispatch(new_activity(), call(tool_id, bad_input))
    assert first.outcome is Outcome.FAILED

    retry = await fake_model.next_call_given(first.content)
    second = await engine.dispatch(new_activity(), retry)

    assert second.outcome is not Outcome.FAILED, (
        f"{tool_id}: the error did not teach. Message was:\n{first.content}"
    )
```

`[INF]` `KNOWN_MISUSES` is populated from §13.1's schema-rejection ranking, so the test suite grows
from production evidence rather than from imagination. That is the loop this chapter recommends in
miniature, and it is the same loop Chapter 46 automates.

---

## 14. Relation to AHE

This is the chapter Phase 2 added specifically because of Level 5, and the reason is one sentence:
**the Evolve Agent's most productive edits are ACI edits, and it needs them to be legible.**

**Two of the seven component types are ACI surfaces.** `[AHE §3.1]` Tool descriptions are almost
entirely ACI. Tool implementations are partly ACI — result shaping and error text live in code even
though they are interface decisions rather than capability ones. `[AHE §4.4.1]` measured both above
the system prompt, and `[INF]` §2.2 explains why: an ACI edit changes what the model can perceive
and express, while an instruction competes for attention with everything else in the context.

**Most useful edits change no capability.** `[INF]` This is what makes ACI work well-suited to an
automated loop. Rewriting an error message cannot break the tool, cannot widen the blast radius, and
cannot change what the system is able to do. Compared with editing an implementation, it is a
low-variance edit with a measurable effect — which is close to the ideal shape for anything an
unattended loop is allowed to do.

**But the evidence has to exist.** `[INF]` An Evolve Agent can only make an ACI edit if the corpus
shows *what the model was looking at when it went wrong*. Chapter 44's agent debugger reads
trajectories; if those trajectories record tool calls and results but not the descriptions and
errors in force at the time, every ACI defect looks like a reasoning failure and the loop will edit
the prompt instead. §13.2's review depends on the same capture.

**And ACI edits are sharply non-additive.** Chapter 48's result applies here with a specific
mechanism: every ACI improvement adds tokens to the same Chapter 11 budget, so two edits that each
help will, together, help less than their sum — and past some point an additional description
improvement makes things worse by displacing something else. `[INF]` That is a harder interaction
than the general non-additivity result, because it has a known cause and a measurable ceiling.

---

## 15. Industry Perspective

**`[BP]`** The term and the framing come from the observation that agents interact with computers
through a designable interface, and the discipline is borrowed wholesale from human factors
engineering — including the founding lesson that repeated operator error is an interface defect
rather than a training problem.

**`[AHE]`** Supplies tool descriptions and tool implementations as two of the seven editable
component types, the ablation placing both above the system prompt, and progressive disclosure as
the mechanism that keeps rich descriptions affordable `[AHE §3.1, §3.2, §4.4.1]`.

**`[DAR]`** Supplies the effect tag and the registry that this chapter designs around, and the rule
that enforcement lives in the runner rather than in prose `[DAR §8.1]`.

**`[INF]`** The handbook's own: the four-surface taxonomy ordered by leverage, the representation-
agreement rule and its three remedies, the quote-do-not-compute heuristic for arguments, the
three-field `ToolError` that makes "what to do next" a required field, the instructiveness ratio as
a behavioural measurement of error quality, the fix-routing table in §5.5, the observation that error
text is the only ACI improvement with no standing context cost, and the belief-state machine that
makes E3 the expensive undetectable failure.

**`[FUT]`** `[FUT]` Nothing here evaluates an ACI change before deploying it. The instructiveness
ratio and the retry-loop rate are both *post hoc*: they measure an interface already in production.
A way to score a proposed description change offline — against a corpus of recorded misuses, without
a full evaluation run — would make ACI work iterable at the speed the edits themselves allow, and
the handbook knows of no such method.

---

## 16. Key Takeaways

1. **When a competent operator makes the same mistake twice, the interface is the defect.** That is
   the founding lesson of human factors, and it transfers directly. The model is competent; it has
   no memory and no window.
2. **The ACI is four surfaces: verbs, arguments, results, errors.** Attention usually runs in that
   order, and leverage runs in the opposite one.
3. **Errors are instructions, not diagnoses.** Say what happened, why, and what to do next. It is
   the only teaching the model receives, and the only ACI improvement with no standing cost.
4. **Prefer arguments the model can quote over ones it must compute.** Anchors over line numbers,
   handles over reconstructed paths, enums over free-form strings, units in the name.
5. **Any two tools addressing one object must agree on how it is addressed.** The cold open is a
   read view and a write view disagreeing about line 1, with nothing to catch it.
6. **Design for the model being wrong, not for it being right.** The branch that matters is the one
   where a bad argument produces a loud, instructive failure rather than a silent success.
7. **Almost nothing belongs in the prompt.** Wrong tool means the verb is missing; wrong argument
   means the argument is hostile; repeated mistake means the error did not teach. Only an informed
   suboptimal preference is a prompt problem.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Agent-Computer Interface (ACI)** | A tool as the model experiences it — verbs, arguments, results, errors — as distinct from the mechanism that executes it. | `[BP]` | Ch 44, Ch 46 |
| **Verb granularity** | How large each tool is, bounded below by the tool tax and above by the effect tag needing one value. | `[INF]` | Ch 31 |
| **Representation agreement** | The requirement that any two tools addressing the same object address it the same way. | `[INF]` | Ch 46 |
| **Instructive error** | An error naming what happened, why, and what to do next, so the following attempt can succeed. | `[INF]` | Ch 44 |
| **Instructiveness ratio** | Errors followed by success over errors followed by the same error; a behavioural measure of error quality. | `[INF]` | Ch 34 |
| **Retry loop** | A model repeating an identical call because the error taught it nothing; the loud ACI failure. | `[INF]` | Ch 44 |
| **Silent misread** | A well-formed result the model draws a wrong conclusion from; the expensive ACI failure, with no automatic detector. | `[INF]` | Ch 44 |
| **Quote, do not compute** | Preferring arguments the model can copy from a prior result over ones it must derive or count. | `[INF]` | Ch 46 |
| **Counter-example** | An argument example showing wrong usage and its consequence, teaching the boundary rather than the shape. | `[INF]` | Ch 46 |
| **Fix routing** | Deciding which surface a model's mistake belongs to, so the fix lands somewhere that can prevent it. | `[INF]` | Ch 46 |
| **Standing cost** | Tokens an ACI improvement adds to every model call forever, as against a cost paid only on failure. | `[INF]` | Ch 35 |

---

**Next:** Chapter 16 — *The Observation System.* How the runtime perceives itself: tracing,
trajectory capture, result envelopes, and the distinction between telemetry that is never durable
and facts that always are. The chapter that makes Level 5 possible, and the one this chapter's
monthly review depends on.
