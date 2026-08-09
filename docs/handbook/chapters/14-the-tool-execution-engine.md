```
  Level 2 · Chapter 14
  THE TOOL EXECUTION ENGINE
  Requires   C9 Three Flows, C10 The Planner, C11 The Context System,
             C13 The Reasoning Engine
  Unlocks    C15 Agent-Computer Interface Design, C18 The Runtime Loop,
             C21 Durable Execution, C30 Human Authority,
             C31 Safety and Sandboxing, C46 The Evolve Agent
  Diagrams   Full (9)
```

# Chapter 14 — The Tool Execution Engine

---

## 1. Motivation

### 1.1 Cold open

Atlas stops finding files.

Not everywhere — only in `acme/platform`, and only for about a third of its searches. The runs still
complete. The pull requests are smaller than they used to be, and nobody notices for eleven days.

Somebody had improved `tool.repo.find`. It used to take a directory path and list the files beneath
it; now it takes a glob, which is strictly more useful and handles the monorepo's layout properly.
The implementation was updated, tested, and shipped.

The description was not. It still told the model the parameter was a directory path, so the model
kept sending `src/platform/api`. As a glob, that matches exactly one thing: a file with that literal
name. There is no such file. The tool returned an empty list — correctly — and the model concluded
the directory was empty and moved on.

No error was raised. No schema was violated. No test failed, because the implementation's tests
passed a glob and got the right answer.

The only broken thing was a sentence, and nothing in the system treats a sentence as code.

### 1.2 In plain language

A tool is two things that are easy to mistake for one.

There is **the code**: the function that actually runs, reads the file, applies the patch, calls the
service. And there is **the description**: the text the model is shown, telling it that this tool
exists, what it is for, and what arguments it takes.

The model only ever sees the description. It chooses which tool to use and what to pass based
entirely on that text. The code then does whatever it does. When the two disagree, the model is not
reasoning badly — it is being misinformed, and it has no way to find that out.

That is why this chapter treats them as two separate things you edit, test, and version. It also
explains why a failure here looks so different from an ordinary bug: bad code raises an exception
and something catches it, while a bad description returns a perfectly valid answer to the wrong
question.

The other half of the chapter is about what happens around the call. Some tools only look at things;
others change the world, and those cannot be allowed to run without a person agreeing first. A tool
can return ten megabytes, which will not fit anywhere useful. And a tool can be asked to do the same
thing twice after a crash, which must not mean doing it twice.

### 1.3 Why this chapter exists

Chapter 13 built the door to the model. This is the door to everything else — the filesystem, the
shell, the network, your product's own commands — and it is the layer where the system stops
thinking and starts acting.

Three things converge here that have been promised since Level 1.

Chapter 5 defined an Activity as the only place non-determinism is permitted; this chapter builds
it. Chapter 10 established that the effect tag comes from the tool registry rather than from the
model; this is that registry. And Chapter 9 §5.3 flagged untruncated tool output as the amplifier
that turns one large result into a large context on every subsequent step; §5.5 is where that is
stopped.

`[AHE §4.4.1]` also puts it among the highest-value components: tool implementations and tool
descriptions are two of the seven editable types, and both carried gains in the ablation where the
system prompt alone regressed. `[INF]` Two of the seven surfaces live in this chapter, which makes
it the densest concentration of evolvable material in the runtime.

### 1.4 What previous framings got wrong

**"A tool is a function."** A function has a signature and a body. A tool has a signature, a body,
a description, an effect tag, a schema, a truncation policy, an identity, and a failure vocabulary.
The function is the part that is already easy.

**"The description is documentation."** Documentation is read by people who can ask a follow-up
question. A tool description is the *only* thing the model knows about the tool, consumed with no
opportunity to clarify. The cold open is what that difference costs.

**"Validate the arguments and you are safe."** Schema validation catches the arguments being the
wrong *shape*. The cold open passed validation: `src/platform/api` is a perfectly good string. What
was wrong was the meaning, and no schema expresses meaning.

**"Truncate the output before it goes in the context."** Correct, and one layer too late. `[INF]`
Truncation belongs at the tool boundary, because a ten-megabyte result that reaches the context
system has already been carried across a process boundary, stored in an activity ledger, and
recorded in a trajectory.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A machine with a control panel.

The machine does what it does. The panel is a row of switches with labels above them, and the
operator works entirely from the labels. That arrangement is normal, sensible, and it contains a
specific failure mode: if somebody rewires a switch without relabelling it, the operator does
exactly the wrong thing while following the label perfectly.

Note where the fault is *not*. The machine is fine — it does precisely what it was rewired to do,
and every test of the machine passes. The operator is fine — they read the label and acted on it
correctly. The fault is in the relationship between two artifacts that nothing checks against each
other, which is the cold open exactly.

Two more features of the panel carry over. Some switches have a hinged guard over them, because
they do something that cannot be undone; you have to lift the guard deliberately, and that is the
effect tag and the gate. And the panel has a readout, which is bounded — there is only so much
display — so a machine that produces more output than the readout can show must summarise it
somehow, which is truncation.

**Where the analogy breaks**, and this is the asymmetry that makes tool descriptions unusually
dangerous.

A human operator eventually notices. They flip the switch, watch the machine do something
unexpected, and re-examine the label. They have a channel the panel does not control: they can see
the machine.

The model has no such channel. It sees only what the tool returns, and in the cold open the tool
returned an empty list, which is indistinguishable from a true "there is nothing there". `[INF]`
A model cannot detect a mislabelled tool from its output, because a wrong answer to the question it
thinks it asked looks exactly like a right answer to that question. That is why §5.2 puts the
checkable part of the contract into a schema and §13 puts the uncheckable part into a test that
exercises the description rather than the code.

### 2.2 Why description and implementation are two surfaces

```
  1. The model selects a tool and its arguments using ONLY the
     description. It has never seen the code.
  2. What actually happens is determined ONLY by the code. It has
     never seen the description.
  3. So there are two artifacts, with two audiences, that must agree
     about one thing.
  4. They fail differently. Bad code raises, and something catches it.
     Bad prose returns a valid answer to the wrong question, silently.
  5. They are corrected at different rates by different processes. A
     description can be rewritten and shipped in minutes, and an
     evolution loop may rewrite it unattended (Ch 46). A change to the
     code is a code review.
  6. They have different enforcement strength (Ch 1): code compels,
     prose asks. A rule that must hold belongs in the code; a rule
     that guides belongs in the description.
  7. If they were one artifact, you could not reword without
     redeploying, and you could not tell a capability gap ("the tool
     cannot do this") from a communication gap ("the model does not
     know it can").
  8. Therefore: two surfaces, versioned together, with the part that
     CAN be checked mechanically -- the argument schema -- generated
     from one source so it cannot drift.
```

Step 8 is the cold open's fix and it is narrower than it looks. A schema cannot capture that a
string is a glob rather than a path; §5.2 is honest about that. What it can capture is names, types,
requiredness, and enumerated values, and generating the description's schema *from* the
implementation's signature removes the entire class of drift where those disagree.

### 2.3 The two-by-two that organises the chapter

`[INF]` Every tool sits in one of four cells, and the cell determines almost everything about how it
is treated:

| | Bounded output | Unbounded output |
|---|---|---|
| **Pure** (reads, analyses, drafts) | `tool.repo.read_file` — the easy case | `tool.shell.run_command` — truncation matters most |
| **Effectful** (changes the world) | `cmd.repo.apply_patch` — gate, identity, no retry | `tool.shell.run_command` with writes — the hard case |

The vertical axis is the safety model (§5.3). The horizontal axis is the cost model (§5.5). `[INF]`
The bottom-right cell is where every genuinely difficult tool lives, and it is worth noticing that
`run_command` appears twice: a shell is not one tool, it is a family of tools wearing one name, and
Chapter 31 argues that is the root of most sandbox design.

### 2.4 The mental model to carry

> **A tool is a contract with two readers who never meet. The code is read by the machine; the
> description is read by the model. The engine's job is to make them agree, to make effects
> deliberate, and to make output finite.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  KERNEL                                                      |
  |                                                              |
  |   +------------------+  (1) dispatch(step)                    |
  |   | run driver       |------------------+                     |
  |   +------------------+                  |                     |
  |            ^                            v                     |
  |            |                  +=========+===============+     |
  |            | (7) result       |  TOOL EXECUTION ENGINE  |     |
  |            +------------------|                         |     |
  |                               |  registry . validate    |     |
  |   +------------------+  (2)   |  gate . middleware      |     |
  |   | tool registry    |------->|  invoke . normalise     |     |
  |   |  description     |        |  truncate . record      |     |
  |   |  schema          |        +==+======+=========+=====+     |
  |   |  effect tag      |           |      |         |           |
  |   |  truncation      |       (3) |  (4) |     (5) |           |
  |   +------------------+           v      v         v           |
  |                          +=======+=+ [[ activi- ]] +=======+  |
  |                          |APPROVAL | [[ ties    ]] |  (6)  |  |
  |                          |  PORT   |               | TOOL  |  |
  |                          +=========+               | IMPL  |  |
  |                                                    +===+===+  |
  +--------------------------------------------------------|-----+
                                                           v
                                        +~~~~~~~~~~~~~~~~~~~~~~~~+
                                        | SANDBOX / NETWORK /    |
                                        | YOUR DOMAIN (Ch 31)    |
                                        +~~~~~~~~~~~~~~~~~~~~~~~~+

  Figure 14.1 -- The tool engine in its surroundings
                 (D1 High-Level Architecture)

  (1) the driver dispatches a step the planner PROPOSED (Ch 10)
  (2) description, schema, effect tag and truncation policy all
      come from the registry -- never from the model
  (3) effectful steps pass through a gate; pure steps do not
  (4) identity checked and result recorded BEFORE and AFTER
  (5) middleware wraps every invocation (section 5.4)
  (6) the implementation; the only part that touches the world
  (7) a normalised, truncated result returns to the driver
```

`[INF]` The registry feeding wire 2 is the structural claim of this chapter. Description, schema,
effect tag, and truncation policy are *properties of the tool*, held in one place, and none of them
is negotiable per call. A model that could name its own effect tag would make the gate advisory; a
caller that could raise its own truncation limit would make the amplifier reappear one layer up.

Note also that the engine sits between the driver and the world with no bypass. Chapter 13 made the
same argument about the model port; this is its twin, and the same one-import lint rule applies to
whatever library actually touches the filesystem or the network.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  TOOL EXECUTION ENGINE, opened -- one dispatch, in fixed order

  +--------------------------------------------------------------+
  |                                                              |
  |  1. RESOLVE      tool_id -> registry entry. Unknown tool is   |
  |     |            a planner defect, not a runtime error        |
  |     v                                                        |
  |  2. VALIDATE     arguments against the schema. REJECT; never  |
  |     |            coerce (Ch 10 section 4.1, same rule)        |
  |     v                                                        |
  |  3. AUTHORISE    effect tag from the registry:                |
  |     |              pure      -> continue                      |
  |     |              effectful -> require a resolved gate for   |
  |     |                           THIS activity_id (Ch 30)      |
  |     v            no gate, no call. Structural, not advisory.  |
  |  4. IDENTITY     activity_id was minted at plan time (Ch 10). |
  |     |            Look it up:                                  |
  |     |              recorded result -> RETURN IT, no call      |
  |     |              in flight       -> another worker has it   |
  |     |              absent          -> claim and proceed       |
  |     v                                                        |
  |  5. RESERVE      budget for tools that cost money             |
  |     |                                                        |
  |     v                                                        |
  |  6. MIDDLEWARE   the pipeline wraps the invocation (5.4)      |
  |     |                                                        |
  |     v                                                        |
  |  7. INVOKE       the implementation runs, with a deadline and |
  |     |            an abort handle, holding no lease (Ch 5)     |
  |     v                                                        |
  |  8. NORMALISE    exit codes, exceptions, and partial results  |
  |     |            -> our ToolResult vocabulary                 |
  |     v                                                        |
  |  9. TRUNCATE     apply the registry's policy HERE, before the |
  |     |            result is stored or moved (section 5.5)      |
  |     v                                                        |
  | 10. RECORD       result to the activity ledger; effect events |
  |                  to the outbox in the same transaction        |
  +--------------------------------------------------------------+

  Figure 14.2 -- One dispatch, opened (D2 Low-Level Architecture)
```

### 4.1 Three orderings that are not arbitrary

`[INF]` The sequence encodes three decisions worth stating, because each has a plausible-looking
alternative.

**Authorise before identity (3 before 4).** A gate is checked before the ledger is consulted, so a
replayed effectful step cannot slip past on the grounds that its result already exists. It will find
the recorded result at step 4 and return it without calling — but if the gate had been skipped, a
step whose result was *not* recorded would execute unapproved after a crash.

**Identity before invoke (4 before 7).** Chapter 13 §5.5's rule, applied to tools: always check the
ledger before doing the work. This is what makes a resumed run reuse a completed `apply_patch`
rather than applying it twice.

**Truncate before record (9 before 10).** The ten-megabyte result is cut *before* it is stored,
because storage is where it becomes permanent — in the activity ledger, in the trajectory, and in
every replay of that run forever.

```
                                                            LAYER VIEW

  Components and their interfaces.

   ProposedToolCall                                ToolResult (frozen)
   (from the planner)                                        ^
        |                                                    |
        v                                                    |
   +----+------------+                             +---------+-------+
   | Registry        |  RegistryEntry              | Truncator       |
   |  resolve(id)    |--------------+              |  by policy      |
   |  descriptions() |              |              +---------+-------+
   +-----------------+              v                        ^
        |                    +------+---------+              |
        | descriptions       | Validator      |     +--------+-------+
        v                    |  schema check  |     | Normaliser     |
   +----+------------+       |  REJECT only   |     |  exit codes    |
   | Context system  |       +------+---------+     |  partials      |
   | (Ch 11)         |              |               +--------+-------+
   +-----------------+              v                        ^
                             +------+---------+              |
   +-----------------+       | Authoriser     |     +--------+-------+
   | Approval port   |<------|  effect tag    |     | Middleware     |
   | (Ch 30)         |       |  -> gate       |     | pipeline       |
   +-----------------+       +------+---------+     +--------+-------+
                                    |                        ^
                                    v                        |
   +-----------------+       +------+---------+     +--------+-------+
   | Activity ledger |<----->| Identity       |---->| Invoker        |
   | (Ch 21)         |       |  check + claim |     |  deadline      |
   +-----------------+       +----------------+     |  abort handle  |
                                                    +--------+-------+
                                                             |
                                                             v
                                                    +~~~~~~~~+~~~~~~+
                                                    | tool impl     |
                                                    +~~~~~~~~~~~~~~~+

  Figure 14.3 -- Tool engine components (D3 Component Diagram)
```

`[INF]` The Registry has two outbound edges and that is the whole of §2.2 drawn as a diagram. It
feeds descriptions *up* to the context system, so the model learns what exists; it feeds schema,
effect tag, and truncation policy *across* to the engine, so the runtime knows what to enforce. One
source, two consumers, and the cold open is what happens when those two consumers are fed from
different places.

---

## 5. The Tool Contract

### 5.1 What a registry entry contains

```yaml
# tool_descriptions/repo_find.tool.yaml
id: tool.repo.find
effect: pure

description: |
  Find files in the repository whose path matches a glob pattern.
  Use `**` to match across directories. To list a directory's
  contents, pass `path/to/dir/**`.
  Returns matching paths, one per line, sorted.

arguments:
  pattern:
    type: string
    required: true
    description: |
      A glob, NOT a directory path. `src/api` matches only a file
      literally named `src/api`. For a directory, use `src/api/**`.
    examples: ["src/**/*.py", "src/api/**", "**/test_*.py"]

returns:
  description: Matching paths, newline-separated, sorted. Empty if none.
  empty_means: |
    No path matched the glob. This does NOT mean the directory is
    empty -- check the pattern before concluding anything.

truncation:
  max_bytes: 65536
  strategy: head_tail
  on_truncate: "Showing first and last 200 matches of {total}."

failure_modes:
  - not_a_glob: |
      If the pattern contains no wildcard and matches nothing, say so
      explicitly rather than returning an empty list.
```

`[AHE §3.1]` The description and the implementation are separate files, separately editable, both in
the harness workspace. Everything above except the `effect` tag is in the Evolve Agent's action
space; the effect tag is not, for reasons §14 gives.

`[INF]` Three fields in that file exist purely because of the cold open, and they are the fields
most tool definitions lack:

- **`empty_means`.** The cold open's model concluded "the directory is empty" from an empty list.
  A description that says what emptiness does *not* mean removes the inference.
- **`examples` showing the failure.** `src/api` is listed as an example of what the parameter is
  *not*. Examples that only show correct usage teach the shape and not the boundary.
- **`failure_modes.not_a_glob`.** The implementation is asked to distinguish "matched nothing" from
  "you probably meant a directory". That is Chapter 15's subject and it starts here.

### 5.2 The schema is the checkable overlap, and it is narrow

`[INF]` Generate the schema from the implementation's signature, so names, types, requiredness, and
enums cannot drift. Then be honest about what remains unchecked:

| Drift | Caught by the schema? |
|---|---|
| Parameter renamed | yes |
| Type changed `str` to `int` | yes |
| Parameter became required | yes |
| New parameter added | yes |
| Allowed values changed (enum) | yes |
| **Meaning changed: path became glob** | **no** |
| **Return semantics changed** | **no** |
| **Side effect added** | **no** |

The three unchecked rows are the dangerous ones, and they share a shape: the *type* is unchanged and
the *meaning* is not. §13.2 is a test for the second row, §5.3 is the control for the third, and the
first — the cold open's row — has no mechanical defence at all. `[INF]` The honest position is that
a description review is required whenever an implementation's semantics change, and the only
enforcement available is a checklist on the pull request that touches a tool.

### 5.3 The effect tag is the entire safety model

`[DAR §8.1]` Two values, from the registry, never from the model:

| | Pure | Effectful |
|---|---|---|
| Definition | reads, analyses, drafts | produces an effect outside the system that the system cannot reverse |
| Gate | none | **required**, resolved, and matched to this `activity_id` |
| Retry | free | never automatically |
| Replay | re-run or reuse, both safe | reuse only; never re-run |
| Sandbox | may be shared | isolated (Ch 31) |

`[INF]` The classification rule that resolves most arguments: **can the system itself undo this
without asking anyone?** Writing to a scratch directory inside a sandbox that will be destroyed is
pure. Writing to the customer's repository is effectful. Sending an email is effectful in the
strongest sense, because it is not merely irreversible — it is observed.

The failure to watch for is a tool that *becomes* effectful. A search tool that gains a
result-caching side effect, a read tool that starts recording analytics: the tag stays `pure`
because nobody thought of it as a change in kind. `[INF]` The defence is a review rule rather than a
mechanism, and it is short enough to remember: **if a diff to a pure tool adds a write of any kind,
the tag is now wrong.**

### 5.4 Middleware wraps every invocation

`[AHE §3.1]` Middleware is one of the seven component types, and its defining property is that it
is not optional from the model's point of view. The model cannot decline to be wrapped.

`[INF]` That makes it the strongest enforcement surface in the harness, and Chapter 1's hierarchy
says a rule belongs at the weakest level that can still enforce it — so the question for any rule is
whether prose can carry it:

| Rule | Belongs in | Why |
|---|---|---|
| "Prefer ripgrep over find" | description | a preference; prose can carry it |
| "Never run a command longer than 120s" | middleware | must hold; prose cannot enforce it |
| "Redact credentials from every result" | middleware | must hold, and must be uniform |
| "Retry a network read once" | middleware | policy, applied identically everywhere |
| "This repo needs POSTGRES_URL" | long-term memory | a fact, not a rule (Ch 12) |

A middleware pipeline that is ordered and declared per tool class gives you per-call timeouts,
redaction, retry policy, and instrumentation without any of them being repeated in a tool
implementation — and, more importantly, without any of them being *forgettable* in the next tool
somebody writes.

### 5.5 Truncation belongs here, and nowhere else

Chapter 9 §5.3 named the amplifier: a large tool result enters the next step's context, which enters
the step after that, with no decision having changed. Chapter 11 §3 declared that the context system
consumes results already truncated. This is where that happens.

`[INF]` The policy is per tool, because the right answer differs:

| Strategy | For | Keeps |
|---|---|---|
| `head` | logs, streams | the beginning, where errors usually are |
| `head_tail` | search results, listings | the shape of the result at both ends |
| `summarise` | large structured output | a model-generated digest, plus a handle |
| `handle_only` | files, archives | a reference and a size; the model reads ranges |

Every truncation must say so in the result, with the original size. `[INF]` A silently truncated
result is worse than a large one: the model treats a partial listing as complete and reasons from a
subset, which is the cold open's failure mode arriving by a different route.

### 5.6 Partial success is a distinct outcome

`[INF]` A tool that applies three of five hunks has neither succeeded nor failed, and forcing that
into a boolean loses the only information that matters. Three outcomes, not two:

| Outcome | Means | Planner should |
|---|---|---|
| `OK` | did everything asked | continue |
| `PARTIAL` | did some of it; state changed | **replan** — the world moved (Ch 10 §5.4) |
| `FAILED` | did nothing; state unchanged | retry or replan |

The distinction between `PARTIAL` and `FAILED` is whether the world changed. `[INF]` Collapsing them
is what produces a retry that re-applies three hunks that were already applied, and it is why the
effectful-retry rule in §5.3 says *never automatically*: only a planner with the partial result in
hand can decide what to do next.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  driver   engine   registry   gate    ledger   middleware   impl
    |         |        |        |        |          |         |
    |-- dispatch(step 7: cmd.repo.apply_patch) ---->|         |
    |         |-- resolve ->|   |        |          |         |
    |         |<-- effect: EFFECTFUL, truncate: head_tail     |
    |         |-- validate args vs schema: OK                 |
    |         |                 |        |          |         |
    |         |-- gate for activity_id 8ac31d? ---->|         |
    |         |<-- RESOLVED, approved by u:priya at 09:14 ----|
    |         |   (Ch 10: keyed to plan_id + step_id, so a    |
    |         |    replan would have voided this)             |
    |         |                          |          |         |
    |         |-- ledger lookup 8ac31d ->|          |         |
    |         |<-- absent; claimed ------|          |         |
    |         |                                     |         |
    |         |-- invoke through middleware ------->|         |
    |         |                        timeout 120s |-------->|
    |         |                        redaction on |         |
    |         |                                     |<-- exit 0,
    |         |                                     |    3 of 5 hunks
    |         |<-- normalise: PARTIAL, not OK ------|         |
    |         |-- truncate: 2.1 MB -> 64 KB, noted in result  |
    |         |-- record result + << repo.patch.applied >>    |
    |         |   in ONE transaction ---------------------->  |
    |<-- ToolResult(PARTIAL, applied=3, failed=2) ---|         |
    |                                                         |
    | driver: PARTIAL means the world changed -> replan (Ch 10)|

  Failure branch: the worker dies between invoke and record.
    The patch WAS applied; the result was not recorded.
    On resume: identity lookup at step 4 finds nothing, so the
    engine would re-invoke -- and apply_patch is effectful.
    This is why the implementation must be idempotent on its own
    terms (section 11, row 8), and why << repo.patch.applied >>
    is written in the same transaction as the domain change
    (Ch 9 section 5.2): the EVENT survives even when the result
    record does not.

  Figure 14.4 -- One effectful dispatch, with partial success
                 (D4 Sequence)
```

### 6.1 Reading the failure branch

`[INF]` This is the hardest honest case in the chapter and it is worth not glossing.

The identity check at step 4 prevents a *duplicate dispatch* when a result was recorded. It does not
prevent a duplicate *effect* when the effect happened and the record did not. That window is small
and it is real.

Three things narrow it, and none closes it:

- The event and the domain change share a transaction (Chapter 9 §5.2), so the *event* survives even
  when the engine's result record does not — and the relay will deliver it, so the run learns the
  patch was applied.
- Effectful tools are asked to be idempotent on their own terms: `apply_patch` that detects an
  already-applied hunk and reports it as such turns a duplicate into a `PARTIAL` with zero applied.
- Effectful steps are never retried automatically (§5.3), so the second attempt is a planner
  decision made with the situation visible.

`[INF]` What remains is a genuine residual, in the same family as Chapter 13's lost-completion
double-billing: the system cannot make an external side effect and a local record atomic. Naming it
is better than a diagram that implies otherwise.

```
                                                             TIME VIEW

  The dispatch cycle and its exits.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | resolve + validate   |  invalid -> E1                |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     /effect\  effectful   +----------------------+       |
     \ tag? /------------->| gate resolved for    |       |
      \    /               | THIS activity_id?    |       |
        | pure             +----+-------------+---+       |
        |                       | no          | yes       |
        |                       v             |           |
        |                    E2 park          |           |
        v                                     v           |
   +----+-------------------------------------+---+       |
   | identity lookup                              |       |
   +----+-----------------------------------------+       |
        |                                                 |
        +-- recorded result --> E3 replay, no call, no cost|
        |                                                 |
        v                                                 |
   +----+-----------------+                               |
   | reserve + middleware |                               |
   | + invoke             |                               |
   +----+-----------------+                               |
        |                                                 |
        v                                                 |
      /   \                                               |
     /outcome\-- FAILED, transient --> retry (PURE only)-->+
     \       /-- FAILED, terminal ---> E5                  |
      \     /-- PARTIAL ------------> E6                   |
        |                                                  |
        | OK                                               |
        v                                                  |
   +----+-----------------+                                |
   | normalise, truncate, |                                |
   | record               |                                |
   +----+-----------------+                                |
        |                                                  |
        v                                                  |
      E4 result returned                                   |

  Exits:
    E1  schema rejection      -> planner defect; emits an event
    E2  no resolved gate      -> run PARKS holding nothing (Ch 30)
    E3  replay hit            -> stored result reused, zero cost
    E4  OK                    -> result returned
    E5  terminal failure      -> driver may replan (Ch 10 section 5.4)
    E6  PARTIAL               -> driver MUST replan; the world moved

  Figure 14.5 -- The dispatch cycle and its exits (D5 Runtime Loop)
```

`[INF]` The retry arrow is annotated `PURE only` because that is the single most important
restriction in the diagram. An automatic retry of an effectful tool is how one email becomes two,
and no amount of care elsewhere recovers from it.

---

## 7. State Management

```
                                                            STATE VIEW

  One activity's states. The activity is the durable record; the
  invocation is not.

            +------------------+
            | {{ PROPOSED }}   |  in the plan; identity minted at
            +--------+---------+  plan time (Ch 10)
                     |
        +------------+------------+
        | pure                    | effectful
        v                         v
        |                +------------------+
        |                | {{ AWAITING_     |  a park; holds nothing
        |                |    APPROVAL }}   |
        |                +--------+---------+
        |                         | gate resolved
        +------------+------------+
                     v
            +------------------+
            | {{ CLAIMED }}    |  leased by one worker
            +--------+---------+
                     |
                     v
            +------------------+
            | {{ INVOKING }}   |  unbounded duration; holds no lease
            +--+----+-------+--+
               |    |       |
        OK /   |    |       | lease expired (worker died)
     PARTIAL   |    |       v
               |    |   +---+--------------+
               |    |   | {{ CLAIMED }}    |  another worker; the
               |    |   +------------------+  effect may have happened
               |    |                          (section 6.1)
               |    | FAILED, transient, PURE only
               |    v
               |  +---+--------------+
               |  | {{ RETRYING }}   |  attempt cap applies
               |  +---+--------------+
               v
      +--------+---------+        +------------------+
      | {{ RECORDED }}   |        | {{ DEAD_LETTER }}|
      +------------------+        +------------------+
       result in the ledger;       attempts exhausted;
       replay returns it            visible, not blocking

  Illegal, and enforced:
    * effectful, INVOKING without a resolved gate  -- structural
    * effectful -> RETRYING automatically          -- section 5.3
    * RECORDED -> INVOKING                         -- replay reuses
    * INVOKING holding a run lease                 -- Ch 5 custody

  Figure 14.6 -- An activity's states (D6 State Diagram)
```

### 7.1 The activity is run state; the effect is domain state

Chapter 6's categories, applied where they matter most. The activity row — identity, claim, result,
attempts — is run state, and it disappears when the run is deleted. The patch in the repository is
domain state, and it does not.

`[INF]` That asymmetry is the reason effectful tools need a gate rather than a rollback. The runtime
can undo everything it owns and none of what it caused, so authority to cause it has to be obtained
in advance. Chapter 30 builds the mechanism; this is the reason it exists.

### 7.2 What is durable

The activity record and its result, in the activity ledger. The effect event, written in the same
transaction as the domain change. And the trajectory entry, in the trace store.

Nothing else. The invocation itself — the process, the sandbox handle, the middleware state — is
gone the moment it returns, which is what allows `INVOKING` to hold no lease and lets a different
worker pick the run up mid-flight.

---

## 8. Internal APIs

```python
from typing import Protocol


class ToolPort(Protocol):
    """One dispatch. Resolves, validates, authorises, checks identity,
    invokes through middleware, normalises, truncates, and records.

    No method accepts an effect tag, a truncation limit, or a schema
    from the caller: all three come from the registry, so neither the
    model nor a caller can widen them.
    """

    async def dispatch(
        self,
        activity_id: ActivityId,
        call: ProposedToolCall,
    ) -> ToolResult:
        """Execute one proposed tool call.

        Raises GateRequired when the tool is effectful and no resolved
        approval exists for THIS activity_id -- the caller parks.
        Raises SchemaRejected when arguments do not validate; the
        arguments are never coerced.
        Returns a recorded result without invoking when identity
        already has one (replay, Ch 21).
        """


class ToolRegistry(Protocol):
    """The single source for what a tool IS. Feeds descriptions to the
    context system and enforcement properties to the engine."""

    def resolve(self, tool_id: str) -> RegistryEntry: ...

    def descriptions_for(
        self, tenant: str, work_class: str
    ) -> list[ToolDescription]:
        """What the model is shown. A tool absent from this list cannot
        be proposed, which makes capability scoping a registry
        question rather than a prompt instruction (Ch 31)."""


class ToolMiddleware(Protocol):
    """Wraps every invocation. The model cannot decline to be wrapped,
    which is what makes this the strongest enforcement surface in the
    harness (section 5.4)."""

    order: int

    async def around(
        self, ctx: ToolContext, call_next: Callable[[], Awaitable[RawResult]]
    ) -> RawResult: ...
```

`[INF]` `descriptions_for(tenant, work_class)` is the quiet one. Capability scoping — which tools
this tenant's runs may use at all — is enforced by *not describing* the tool, so the model never
learns it exists. A prompt saying "do not use the deploy tool" is a request; a registry that omits
it is a fact, and Chapter 31 builds on this rather than on instruction.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import StrEnum


class Effect(StrEnum):
    PURE = "pure"
    EFFECTFUL = "effectful"


class Outcome(StrEnum):
    OK = "ok"
    PARTIAL = "partial"        # the world changed, incompletely
    FAILED = "failed"          # the world did not change


class TruncationStrategy(StrEnum):
    HEAD = "head"
    HEAD_TAIL = "head_tail"
    SUMMARISE = "summarise"
    HANDLE_ONLY = "handle_only"


@dataclass(frozen=True)
class RegistryEntry:
    tool_id: str
    effect: Effect                       # never from the model
    schema: Mapping[str, object]         # generated from the signature
    description: ToolDescription         # the editable prose surface
    truncation: TruncationPolicy
    middleware_classes: tuple[str, ...]
    sandbox_profile: str                 # Ch 31


@dataclass(frozen=True)
class ToolResult:
    outcome: Outcome
    content: str
    truncated: bool
    original_bytes: int | None           # None when not measured
    handle: str | None                   # for HANDLE_ONLY, or ranges
    effects: tuple[EffectRecord, ...]    # what actually changed
    duration_ms: int
    attempt: int
```

Three fields carry the chapter.

**`outcome` is three-valued.** §5.6's argument, encoded so that a caller cannot write
`if result.ok:` and lose the partial case.

**`truncated` and `original_bytes` travel together.** A truncated result that does not say so is
§5.5's silent failure. `original_bytes` is nullable because some sources genuinely cannot report a
total, and Chapter 6's rule applies: unknown is not zero.

**`effects` records what actually changed**, not what was requested. `[INF]` For a `PARTIAL`, this
is the only account of which three hunks landed — and it is what the planner needs in order to
replan rather than guess.

---

## 10. Communication

```
                                                            LAYER VIEW

  descriptions   registry ====> context system   ~6-25 KB   EVERY call
                                                             (Ch 11 tool tax)
  arguments      planner  ====> engine           ~1-5 KB
  raw output     impl     ====> engine           ~1 KB - 10 MB  <-- the
                                                     unbounded one
  truncated      engine   ====> ledger           ~1-64 KB   after step 9
  result         engine   ====> driver           ~1-64 KB
  effect event   engine   ====> outbox           ~1 KB
  trajectory     engine   ====> trace store      ~2-20 KB

  The amplifier, stopped:
     10 MB raw --> 64 KB stored --> 64 KB in the NEXT context
     Without step 9: 10 MB in the next context, and the one after,
     and the one after that (Ch 9 section 5.3).

  Figure 14.7 -- What moves through the tool engine (D7 Data Flow)
```

```
                                                             TIME VIEW

  planner --------> engine     PROPOSES a call; does not dispatch
  driver ---------> engine     dispatches, having released its lease
  engine ---------> registry   effect tag, schema, truncation policy
  engine ---------> gate       effectful only; blocks until resolved
  engine --||----> impl        the gate is on this edge, structurally
  model --X        effect tag  REFUSED: from the registry (Ch 10)
  caller --X       truncation  REFUSED: registry policy, not per call
  impl --X         run state   REFUSED: tools return, they do not write
                               run state

  Figure 14.8 -- Who decides that an effect happens (D8 Control Flow)
```

```
                                                             TIME VIEW

  << repo.patch.applied >>      ....>  a DOMAIN event, written in the
                                       same transaction as the change
  << tool.schema.rejected >>    ....>  planner defect; the training
                                       signal for Ch 46
  << tool.result.truncated >>   ....>  with original size; makes the
                                       amplifier visible before it
                                       becomes a cost
  << tool.gate.required >>      ....>  an effectful step parked

  NOT events:
    a pure tool's result       a RESULT, keyed by identity, to the
                               activity ledger (Ch 21)
    middleware timings         telemetry
    retry attempts             recoverable from the ledger

  Figure 14.9 -- What tool execution makes durable (D9 Event Flow)
```

`[INF]` `tool.schema.rejected` is the counterpart of Chapter 10's `run.plan.rejected`, and for the
same reason: a rejection is direct, low-volume, high-signal evidence that a description and a model's
understanding of it have diverged. It is the closest thing this chapter has to an automated detector
for the cold open, and it only fires when the drift is a *shape* change rather than a meaning change.

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 15 ACI | descriptions, error messages, `empty_means` | this chapter builds the mechanism; that one designs the surface |
| Ch 21 Durable Execution | identity check before invoke; §6.1's residual | replay correctness rests on it |
| Ch 30 Human Authority | the effect tag and the gate on wire `--||->` | the tag is the whole safety model |
| Ch 31 Safety | `sandbox_profile`, `descriptions_for` as scoping | capability is a registry question |
| Ch 35 Cost | tool tax on every call; truncation as a cost control | Ch 11 §2.3's fixed cost |
| Ch 46 Evolve Agent | descriptions and implementations are two of seven surfaces | the densest evolvable material in the runtime |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Description drift | implementation semantics changed, prose did not | none mechanical; `tool.schema.rejected` only for shape | review rule on any tool diff — the cold open |
| Empty means "nothing there" | tool returns empty for a malformed query | model concluding absence from emptiness | `empty_means` in the description (§5.1) |
| Silent truncation | result cut with no marker | model reasoning from a subset as if complete | `truncated` + `original_bytes` always set |
| Truncation too late | cutting in the context system | 10 MB in the ledger, trajectory, and every replay | truncate at step 9, before record |
| Pure tool became effectful | a write added to a read tool | review rule: any write in a pure tool's diff | re-tag; the gate then applies |
| Model-declared effect | tag taken from the completion | an effectful step running ungated | tag from the registry only |
| Effectful auto-retry | retry policy applied uniformly | duplicate effects | retry is PURE only (§5.3) |
| Effect without a record | worker died between invoke and record | the domain event arrives, the result does not | §6.1: idempotent implementations; residual named |
| Partial collapsed to failed | two-valued outcome | retries that re-apply completed work | three-valued `Outcome` (§5.6) |
| Coerced arguments | validator repairs instead of rejecting | planner defects invisible; runs quietly degrade | reject and emit the event |
| Capability by instruction | "do not use tool X" in the prompt | the tool being used | omit it from `descriptions_for` |
| Unbounded tool count | tools added, never removed | Ch 11 stable-band tokens rising | the tool tax is a budget line |

`[INF]` Row one has no mechanical detector and the table should not pretend otherwise. The schema
catches shape drift; nothing catches meaning drift. The available defences are a review rule, the
description tests in §13.2, and `empty_means` making the most common misreading explicit. That is
weaker than the rest of this chapter, and it is the honest state of the art.

---

## 12. Scalability

### 12.1 Tools are the parallel part

`[INF]` Unlike model calls, tool invocations are usually cheap, bounded, and parallelisable. Chapter
24's task graph exists largely to exploit that: five independent file reads should not be five
sequential steps.

| Bound by | Typical | Symptom when wrong |
|---|---|---|
| Sandbox capacity | containers per host | dispatch queueing behind sandbox creation |
| Per-tool concurrency | varies; network tools lowest | rate limits at a third party |
| Truncation cost | proportional to raw output | CPU on large results |
| Ledger writes | one per activity | fine until tool calls per run get large |

`[INF]` Sandbox creation is the one that surprises. A tool call is milliseconds and a cold sandbox
is seconds, so a system that creates one per call has made its cheapest operation its slowest.
Chapter 31 covers lifecycle; the number to watch here is sandbox reuse rate.

### 12.2 The tool tax

Chapter 11 §2.3 counted tool definitions among the fixed costs paid on every model call. So the tool
*count* is a cost that scales with every step of every run, forever, whether or not the tools are
used.

`[INF]` Twenty tools that are never called still cost more per run than the entire long-term memory.
That makes tool curation a cost activity as much as a design one, and it makes `descriptions_for`
returning a *scoped* list — rather than everything — one of the better-value optimisations available.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| `tool.schema.rejected` by tool | shape drift, and planner confusion | any sustained rise |
| Empty-result rate by tool | the cold open's fingerprint | a step change after a deploy |
| Truncation rate and `original_bytes` p99 | the amplifier | rising p99 |
| `PARTIAL` rate by tool | tools that half-succeed | reported; a rise means fragility |
| Gate wait time p50/p99 | humans are the bottleneck (Ch 30) | above the approval SLO |
| Effectful retries | should be zero, always | any non-zero |
| Sandbox reuse rate | §12.1's surprise | falling |
| Description edits without impl edits, and the reverse | drift risk | reported at review, not alerted |

`[INF]` Row two is the closest thing to a detector for the cold open. An empty-result rate that
steps up after a deploy, on one tool, in one repository, is exactly the signature — and it was
observable for eleven days before anybody noticed, because nobody was looking at it.

### 13.2 Test the description, not only the code

```python
async def test_description_examples_actually_work(
    registry: ToolRegistry, sandbox: Sandbox
) -> None:
    """Every example in every tool description must execute and return
    what the description says it returns.

    This is the test the cold open needed. The implementation's own
    tests passed a glob and got the right answer; nothing executed the
    example from the DESCRIPTION, which was a directory path.
    """
    for entry in registry.all():
        for arg_name, spec in entry.description.arguments.items():
            for example in spec.examples:
                result = await dispatch_in_sandbox(entry, {arg_name: example})
                assert result.outcome is not Outcome.FAILED, (
                    f"{entry.tool_id}: example {example!r} for {arg_name} "
                    f"does not work"
                )
```

`[INF]` This is the highest-value test in the chapter and it is unusual enough to be worth naming:
it tests the *documentation* by executing it. It would not have caught the cold open on its own —
`src/api` as a glob returns empty rather than failing — which is why §5.1 also requires an example
that shows the wrong usage, and why the assertion above should be tightened per tool to check the
result is non-empty where the example implies it should be.

### 13.3 The review rule

`[BP]` One line on the pull-request template for any change under `tools/`:

> Did the tool's behaviour change in a way its description does not say? If the description was not
> edited, explain why not.

`[INF]` It is a weak control and it is the only one available for §5.2's three unchecked rows. A
weak control that fires on every relevant diff beats a strong control that does not exist.

---

## 14. Relation to AHE

Two of the seven editable component types live in this chapter, and they behave very differently
under an evolution loop.

**Tool descriptions are the highest-yield surface.** `[AHE §4.4.1]` measured tool components
carrying gains where the system prompt alone regressed, and `[INF]` the reason is legible from §2.2:
a description change alters what the model *knows it can do*, which changes the space of plans,
whereas an instruction competes for attention with everything else in the context. Chapter 15 is
about designing that surface deliberately; Chapter 46 is about a machine editing it.

**Tool implementations are a stronger but riskier surface.** Code enforces where prose asks
(Chapter 1), so a fix in the implementation holds. But an Evolve Agent editing implementations is
editing the code that touches the world, and Chapter 46's constraint hierarchy therefore treats
`tool_impl` edits as a higher constraint level than `tool_desc` edits.

**The effect tag is not editable, and this is the sharpest boundary in the harness.** `[INF]` If the
Evolve Agent could re-tag a tool from effectful to pure, it could remove a gate that was slowing its
iterations down — and it would be locally correct to do so, because gates cost wall-clock time and
show up as worse throughput. Nothing in an outcome-based reward signal represents the authority the
gate was protecting. So the tag lives in runtime-enforced registry data, outside the workspace, for
the same reason Chapter 12 put memory abstraction outside it.

**`tool.schema.rejected` is training signal.** §10's event is the evidence that a description and
the model's reading of it diverged. `[INF]` A harness that discards rejections and retries silently
is throwing away the cleanest per-tool quality measurement it has.

---

## 15. Industry Perspective

**`[DAR]`** Supplies the pure/effectful tag as the safety model, the rule that an effectful step is
structurally uncallable without a resolved gate, activity identity as the precondition for any
invocation, and the requirement that the runner enforce rather than the prompt request
`[DAR §6.1, §8.1, §8.2]`.

**`[AHE]`** Supplies tool description and tool implementation as two distinct editable component
types, middleware as a third, and the ablation placing tool components above the system prompt by
measured value `[AHE §3.1, §4.4.1]`.

**`[INF]`** The handbook's own: the derivation that descriptions and implementations must be separate
surfaces, the schema as the narrow checkable overlap with an explicit list of what it cannot catch,
`empty_means` and negative examples as description fields, three-valued outcomes with `PARTIAL`
meaning the world moved, truncation at step 9 rather than in the context system, capability scoping
by omission from `descriptions_for`, the review rule for pure tools gaining writes, testing
descriptions by executing their examples, and the argument that the effect tag must sit outside the
Evolve Agent's workspace because an outcome-based reward would remove gates.

**`[BP]`** Middleware pipelines, schema-validated interfaces, and output truncation are ordinary
practice in web frameworks and RPC systems. The contribution here is treating the description as a
first-class, separately-tested artifact rather than as documentation.

**`[FUT]`** Meaning drift between a description and an implementation has no mechanical detector
(§11 row one). `[FUT]` A useful direction would be property-based agreement testing — generating
inputs from the description's stated semantics and checking the implementation agrees — but the
handbook knows of no production system doing this, and states it as a gap rather than a
recommendation.

---

## 16. Key Takeaways

1. **A tool is two artifacts with two readers who never meet.** The model reads only the
   description; the machine runs only the code. When they disagree, the model is misinformed rather
   than wrong, and it cannot detect the difference.
2. **The schema is the checkable overlap, and it is narrow.** Generate it from the signature so
   names and types cannot drift — then accept that meaning, return semantics, and new side effects
   are not covered, and control them with review rather than pretending otherwise.
3. **The effect tag is the entire safety model.** Two values, from the registry, never from the
   model, and structurally enforced: no resolved gate, no call.
4. **A pure tool that gains a write is now effectful.** The tag does not change itself, and this is
   the most common way the safety model quietly stops holding.
5. **Truncate at the tool boundary, before recording.** Later is too late: the result is already in
   the ledger, the trajectory, and every replay of that run forever.
6. **`PARTIAL` is not `FAILED`.** The distinction is whether the world changed, and collapsing it
   produces retries that redo completed work.
7. **Capability is a registry question, not an instruction.** A tool omitted from what the model is
   shown cannot be proposed. "Do not use tool X" in a prompt is a request.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Tool execution engine** | The single door to the world: resolves, validates, authorises, invokes, normalises, truncates, and records every tool call. | `[DAR]` | Ch 18, Ch 21 |
| **Tool registry** | The one source for what a tool is, feeding descriptions to the model and enforcement properties to the runtime. | `[INF]` | Ch 31, Ch 46 |
| **Tool description** | The prose the model reads and the only thing it knows about a tool; an editable harness surface in its own right. | `[AHE]` | Ch 15, Ch 46 |
| **Tool implementation** | The code that runs, editable separately from the description and at a different rate. | `[AHE]` | Ch 46 |
| **Description drift** | A tool's behaviour changing while its description does not, producing valid answers to the wrong question. | `[INF]` | Ch 15 |
| **Effect tag** | Pure or effectful, held in the registry and never supplied by the model; the whole of the safety model. | `[DAR]` | Ch 30, Ch 31 |
| **Middleware** | Code wrapping every invocation that the model cannot decline, and therefore the strongest enforcement surface in the harness. | `[AHE]` | Ch 31, Ch 46 |
| **Truncation policy** | Per-tool rules for cutting output at the boundary, before it is stored or moved anywhere. | `[INF]` | Ch 11, Ch 35 |
| **Amplification** | An untruncated result re-entering each subsequent context, growing cost with no decision having changed. | `[INF]` | Ch 35 |
| **Partial success** | An outcome where the world changed incompletely, requiring a replan rather than a retry. | `[INF]` | Ch 27 |
| **Capability scoping** | Restricting what a run may do by omitting tools from what the model is shown, rather than by instructing it. | `[INF]` | Ch 31, Ch 37 |
| **Sandbox profile** | The isolation configuration a tool runs under, named in the registry rather than chosen per call. | `[AHE]` | Ch 31 |
| **Tool tax** | The fixed context cost every tool definition levies on every model call, used or not. | `[INF]` | Ch 15, Ch 35 |

---

**Next:** Chapter 15 — *Agent-Computer Interface Design.* This chapter built the machinery; that one
designs the surface the model actually experiences — verbs, error messages, and output shaping — and
argues that the most productive harness edits available are edits to it.
