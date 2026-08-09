```
  Level 0 · Chapter 1
  ANATOMY OF AN AGENT: MODEL, HARNESS, ENVIRONMENT
  Requires   C0 Evolution of AI Systems
  Unlocks    C2 Why a Runtime Is a Distributed System, C3 Mental Models,
             C14 Tool Execution Engine, C43 Component Observability
  Diagrams   Light (4)
  Variant    Foundational — sections 4-9 describe models, not components
```

# Chapter 1 — Anatomy of an Agent: Model, Harness, Environment

---

## 1. Motivation

### 1.1 Cold open

The Atlas team upgrades the base model. The new one is better on every published measure: stronger
reasoning, longer context, higher scores on the benchmarks the provider chose to report. The change
is one line of configuration.

Atlas gets worse.

Not catastrophically — a few points of task completion, enough to be visible and not enough to be
obviously a bug. Nobody changed the tools. Nobody changed the prompt. The team spends a week looking
for a regression in code that did not change, and eventually finds it in code that never existed:
the per-step timeout and the step budget were tuned, months earlier, against the *old* model's
pacing. The new model thinks longer per step and takes fewer of them. Under the old budget it now
runs out of turns partway through the tasks it would otherwise have finished.

This is a documented hazard, not a hypothetical one. When the AHE harness was re-evaluated across
reasoning tiers of the same model family, the gain was non-monotone — +2.3 points at one tier, +7.3
at the tier it was tuned on, +2.3 again at the tier above — and the authors attribute part of that
shape to step budget and per-task timeout having been fitted to one operating point `[AHE §4.3,
Limitations]`.

### 1.2 In plain language

When a team says "we built an AI agent", almost none of what they built is the AI. The model is a
fixed thing they rent: it takes text and returns text, it cannot open a file, and it remembers
nothing between calls. Everything that makes it look like it can open a file and remember things is
code somebody wrote around it.

This chapter gives that code a name — the **harness** — and draws its boundaries. There are three
regions. The **model** is rented and unchangeable. The **environment** is the real world the work
happens in: repositories, shells, networks, other people's services. The **harness** is everything
in between, and it is the only one of the three that is simultaneously yours to write, safe to
change, and decisive for how well the system performs.

The chapter then breaks the harness into seven kinds of part, and shows that they are not equally
powerful. Some of them are code, which the model has no choice but to obey. Some of them are
sentences in a prompt, which the model may quietly ignore. Knowing which is which is how you decide
where to put a fix.

What goes wrong without this chapter: you spend your time rewriting prompts, because the prompt is
the only part you can see — and the prompt is measurably the weakest of the seven.

### 1.3 Why this chapter exists

Chapter 0 said the model box never grows and everything added is outside it. That is a slogan until
you can draw the line precisely, and you cannot design a system around a line you cannot draw.

This chapter draws it. Three regions, one boundary that matters most, and a component inventory
specific enough that by the end you can look at any line of code in an agent system and say which
region owns it. That skill is not academic. The entire premise of Level 5 is that one of these three
regions is machine-editable, and an evolution loop that cannot tell the regions apart edits the
wrong one.

### 1.4 What previous framings got wrong

**"The prompt is the agent."** The most durable misconception in the field, and the one with the
cleanest counter-evidence. In a component-level ablation where each layer was swapped into a minimal
baseline in isolation, memory alone, tools alone, and middleware alone each *improved* on the
baseline — and the system prompt alone *regressed*, by 2.3 points `[AHE §4.4.1]`. The prompt is one
of seven surfaces and, measured on its own, the weakest of them.

**"The harness is plumbing."** Plumbing is what you call infrastructure whose quality does not
affect the product. Holding the base model fixed and editing nothing but the surrounding components
moved single-attempt success from 69.7% to 77.0% `[AHE §4.2]` — a larger swing than most teams get
from a model upgrade.

**"Write it once and it is done."** The harness is fitted to a model. The cold open is what that
sentence costs when nobody believes it.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A driver, a car, and a road.

The **driver** is the model. Skilled, rented, and fixed: you can choose which driver you hire and
you can tell them where to go, but you cannot make them a better driver. The **road** is the
environment. You choose the route and you can put up barriers, but you cannot move where the road
goes or stop it being wet. The **car** is the harness — the steering, the mirrors, the dashboard,
the seatbelt, the speed limiter. It is the only one of the three you actually build, and it is
entirely load-bearing: a superb driver in a car with no mirrors will hit things.

The analogy carries further than it first looks. Mirrors are the observation system. The dashboard
is context: what the driver is shown, when. The speed limiter is middleware — a rule enforced by
the machine rather than requested of the person. And the reason "just hire a better driver" is bad
advice is that the car is where most of the recoverable errors live.

**Where the analogy breaks.** Two places, and both matter.

First, a car's controls do not change how good the driver is; a harness does change how well the
model performs. Showing the model different things, in a different order, with different tools
available, changes the quality of its decisions and not merely their execution. The dashboard is
part of the driving.

Second, a human driver adapts to an unfamiliar car in about five minutes. A harness does not
transfer that way: one tuned for a particular model can actively *hurt* a different model, which is
exactly what the cold open describes `[AHE §1]`. There is no equivalent of "any competent driver
can drive any car" here, and Chapter 38 turns that into a versioning rule.

### 2.2 Why the harness must be a named region

Teams routinely build a harness without ever naming it, and then cannot version it, test it, or
measure it. The name is forced:

```
  1. The model is a pure function: text in, text out. It cannot read a
     file, call a service, or remember the previous call.
  2. Real work requires reading files, calling services, and remembering.
  3. So something outside the model must do all three on its behalf.
  4. That something must choose WHAT to show the model, and WHICH actions
     to expose to it. Those are choices, and choices are code.
  5. That code is not the model -- you did not train it. It is not the
     environment -- the repository does not contain it. It sits between
     them and belongs to neither.
  6. Your model provider ships no name for it, because your provider does
     not ship it. So teams call it "the app" and it disappears into the
     product.
  7. What has no name is not versioned, not tested, and not measured.
     Therefore it needs its own name -- harness -- before anything in
     Level 5 is even expressible.
```

Step 7 is the one that pays off latest and matters most. An evolution loop that edits the harness
(Chapter 46) can only exist if the harness is a distinct, addressable thing with its own files and
its own version. Naming it here is what makes that possible forty-five chapters later.

### 2.3 Three regions

```
                                                       CONCEPTUAL VIEW

     +-------------------------------------------------------------+
     |  ENVIRONMENT                                                |
     |  the world the work happens in                              |
     |  filesystem . shell . network . repositories . services     |
     |                                                             |
     |    +-----------------------------------------------------+  |
     |    |  HARNESS                                            |  |
     |    |  everything you write, and the only thing you       |  |
     |    |  can change without changing provider or world      |  |
     |    |                                                     |  |
     |    |      +-----------------------------------------+    |  |
     |    |      |  MODEL                                  |    |  |
     |    |      |  fixed weights behind an API            |    |  |
     |    |      |  tokens in, tokens out                  |    |  |
     |    |      +-----------------------------------------+    |  |
     |    |                                                     |  |
     |    +-----------------------------------------------------+  |
     |                                                             |
     +-------------------------------------------------------------+

  Figure 1.1 -- The three regions (conceptual)
```

Three regions, and three very different relationships to your engineering:

| Region | You can | You cannot |
|--------|---------|-----------|
| **Model** | select it, configure sampling, pin a version | change its weights, its priors, or what it knows |
| **Harness** | write it, version it, test it, evolve it | avoid it — every capability the model has reaches the world through it |
| **Environment** | constrain it, isolate it, observe it | fully control it; it changes underneath you |

### 2.4 The mental model to carry

> **The harness is the only region that is simultaneously yours, editable, and load-bearing.**

The model is load-bearing and not yours. The environment is yours to constrain and not editable in
any meaningful sense — you can put a repository in a sandbox, you cannot make the repository
different. The harness is the intersection, and that is why it is where the engineering lives and
why Level 5 targets it rather than anything else.

Two corollaries worth planting now:

**The harness is model-specific.** A harness tuned for one base model often underperforms on another
and must be re-adapted when the model changes `[AHE §1]`. This is not a defect to be engineered
away; it is a property of the arrangement. The cold open is the consequence, and Chapter 38 turns it
into a versioning rule.

**The harness is where capability becomes behaviour.** `[INF]` A model has capabilities the way a
person has knowledge: latent, unreliable, and dependent on the situation to surface. The harness is
the situation. A model that *can* verify its own work will only *reliably* verify it if something in
the harness makes verification the path of least resistance.

---

## 3. High-Level Architecture

### 3.1 The harness, opened

The harness is not one thing. It is seven orthogonal component types, exposed as explicit files at
fixed mount points in a single workspace `[AHE §3.1]`.

```
                                                            LAYER VIEW

  +~~~~~~~~~~~~~~~~~~~~~~~~ ENVIRONMENT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
  |                                                                  |
  |  +======================== HARNESS ==========================+   |
  |  |                                                           |   |
  |  |  SHAPING          (what the model is told)                |   |
  |  |  +----------------+  +----------------+  +-------------+  |   |
  |  |  | system prompt  |  | skill          |  | long-term   |  |   |
  |  |  |                |  |                |  | memory      |  |   |
  |  |  +--------+-------+  +--------+-------+  +------+------+  |   |
  |  |           |                   |                 |         |   |
  |  |           +---------+---------+-----------------+         |   |
  |  |                     v                                     |   |
  |  |            +~~~~~~~~~~~~~~~~~~+                           |   |
  |  |     (1)    |  MODEL           |    (2)                    |   |
  |  |  --------->|  tokens -> tokens|--------->                 |   |
  |  |            +~~~~~~~~~~~~~~~~~~+                           |   |
  |  |                     |                                     |   |
  |  |  MEDIATING          | (what happens around the call)      |   |
  |  |  +------------------v-----------------------------+       |   |
  |  |  | middleware   before_model / after_model /       |       |   |
  |  |  |              before_tool / after_tool           |       |   |
  |  |  +------------------+-----------------------------+       |   |
  |  |                     | (3)                                 |   |
  |  |  ACTING             v                                     |   |
  |  |  +----------------+  +----------------+  +-------------+  |   |
  |  |  | tool           |  | tool           |  | sub-agent   |  |   |
  |  |  | description    |->| implementation |  | config      |  |   |
  |  |  +----------------+  +-------+--------+  +------+------+  |   |
  |  |                              |                  |         |   |
  |  +==============================|==================|=========+   |
  |                                 | (4)              | (5)         |
  |                                 v                  v             |
  |                        [[ files, shell, network, services ]]     |
  +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+

  Figure 1.2 -- The seven editable component types
                (D1 High-Level Architecture)

  (1) assembled context   (2) reply or tool request   (3) dispatch
  (4) effect on the world (5) delegated run, isolated context
```

### 3.2 Why the decoupling matters

The component types are loosely coupled by design: adding middleware does not require editing the
system prompt, and adding a skill does not require touching any tool `[AHE §3.1]`.

That sounds like ordinary hygiene. It is doing something sharper. When each failure pattern maps to
a single component class, a fix is *localisable* — a change in outcome can be traced to one file
rather than scattered across hundreds of lines of prose `[AHE §3.1]`. For a human maintainer that is
convenience. For the Level 5 evolution loop it is the difference between a clean action space and
guesswork, and it is the first of the three observability pillars.

---

## 4. Low-Level Decomposition: The Seven Component Types

Each type, what it holds, and when it is the right place to put a fix. Mount points follow the
naming convention in Appendix B.

### 4.1 System prompt — `workspace/systemprompt.md`

Advisory text applied to every task. Behavioural rules, working style, general discipline.

Advisory is the operative word: the model may follow it, and under load, late in a long run, with a
full context window, it often will not. Measured alone, the evolved system prompt in the AHE run
encoded 79 lines of general discipline and scored 2.3 points *below* the baseline it was inserted
into `[AHE §4.4.1]`. The authors' reading is that the prompt's rules were executable only because
other components enforced them; alone, the text is advice without a mechanism.

**Use it for:** rules with no natural enforcement point. **Do not use it for:** anything you can
enforce elsewhere.

### 4.2 Tool description — `workspace/tool_descriptions/*.tool.yaml`

The schema and prose the model reads when deciding whether and how to call a verb. Co-located with
the tool, but a separate editable surface from its implementation — a distinction most frameworks
collapse and this one deliberately does not.

**Use it for:** clarifying usage, adding examples, warning about pitfalls at the moment of choice.

### 4.3 Tool implementation — `workspace/tools/**/*.py`

The code that runs. The strongest enforcement surface in the harness, because it does not ask the
model for cooperation.

The evolved shell tool in the AHE run grew to roughly 1,364 lines and, among other things,
automatically surfaced contract hints from files near each command `[AHE §4.4.1]`. Swapped alone
into the baseline it lifted aggregate success by 3.3 points. Note what that tool does: it changes
what the model *sees* as a consequence of acting, without instructing it at all.

**Use it for:** anything that must be true regardless of what the model decides.

### 4.4 Middleware — `workspace/middleware/**/*.py`

Hooks in the loop pipeline: before the model call, after it, before a tool, after a tool. The only
component type with a view across steps.

This is its unique power. A prompt rule cannot notice that the same error class has repeated four
times; middleware can, because it accumulates state across the run and can inject a corrective note
into the next turn `[AHE App. C.2.3]`. Cross-step behaviour is invisible to every other component
type.

**Use it for:** patterns that only exist in the sequence, not in any single step.

### 4.5 Skill — `workspace/skills/<name>/SKILL.md`

A packaged, reusable procedure loaded on demand rather than resident in context. Progressive
disclosure: the model pays for the tokens only when the skill is relevant `[AHE §3.2]`.

**Use it for:** procedures that are long, occasionally needed, and stable.

### 4.6 Sub-agent configuration — `workspace/sub_agents/<name>/agent.yaml`

A delegated execution with its own context. Chapter 19 gives the decision rule; the short version is
that a sub-agent buys context isolation and costs attribution.

**Use it for:** subtasks whose exploration would otherwise flood the parent's context.

### 4.7 Long-term memory — `workspace/LongTermMEMORY.md`

Persistent knowledge that survives across sessions: recurring pitfalls, proven strategies,
environment quirks.

Measured alone, this was the highest-scoring single-component swap in the AHE ablation — 75.3%
against a 69.7% baseline, and on the hardest task tier it exceeded the full evolved harness
`[AHE §4.4.1]`. It contained twelve boundary-case lessons. Twelve. The lesson to draw is not that
memory is magic but that *specific, factual, hard-won knowledge is worth more than general
instruction*, which is the same finding the system prompt result states from the other direction.

**Use it for:** facts the system learned the hard way and must not relearn.

---

## 5. The Constraint Hierarchy

### 5.1 The ordering

The seven types are not interchangeable places to put a fix. They differ in **enforcement strength**
— how much the outcome depends on the model choosing to cooperate.

```
                                                            LAYER VIEW

   STRONGEST                                        model has no choice
       ^     +--------------------------------------------------+
       |     |  tool implementation   code that simply behaves   |
       |     +--------------------------------------------------+
       |     |  middleware            intercepts, cannot be      |
       |     |                        argued with                |
       |     +--------------------------------------------------+
       |     |  sub-agent config      structural isolation       |
       |     +--------------------------------------------------+
       |     |  tool description      read at the decision point |
       |     +--------------------------------------------------+
       |     |  long-term memory      recalled, specific, factual|
       |     +--------------------------------------------------+
       |     |  skill                 loaded when judged relevant|
       |     +--------------------------------------------------+
       |     |  system prompt         always present, easily     |
       v     |                        crowded out                |
   WEAKEST   +--------------------------------------------------+
                                                 model may ignore it

  Figure 1.3 -- Enforcement strength of the seven component types
                (D3 Component Diagram)
```

`[INF]` The ordering as drawn is the handbook's synthesis. An equivalent hierarchy is *posed* in the
AHE materials as a research question for an exploration agent to answer from the literature
`[AHE App. B.3.2]`, and the ablation results in `[AHE §4.4.1]` are consistent with its top and
bottom — implementation-level components carried the gain, prose-level strategy regressed. Treat the
two endpoints as evidenced and the middle ranks as a working heuristic, not a measurement.

### 5.2 The rule this yields

> **Put a fix at the weakest level that can enforce it, and no weaker.**

Weaker than necessary and it will hold in testing and fail under load. Stronger than necessary and
you have written code where a sentence would have done, which is cost you pay on every future edit.

The anti-pattern is specific and common enough to name: **repeatedly re-fixing the same failure at
the same level.** If a failure class survives two rounds of prompt edits, the third prompt edit is
not the answer; the level is wrong `[AHE App. B.2]`.

### 5.3 The measured picture

| Variant | All | Easy | Medium | Hard |
|---------|-----|------|--------|------|
| Baseline (bash-only seed) | 69.7% | 87.5% | 78.2% | 51.7% |
| + long-term memory only | 75.3% | 50.0% | 83.6% | **63.3%** |
| + tool only | 73.0% | 75.0% | **87.3%** | 46.7% |
| + middleware only | 71.9% | **100.0%** | 81.8% | 50.0% |
| + system prompt only | 67.4% | 75.0% | 78.2% | 46.7% |
| Full evolved harness | **77.0%** | **100.0%** | **88.2%** | 53.3% |

Source: `[AHE §4.4.1]`, 89 tasks.

Three things to read out of this table, because it is the empirical backbone of the whole book.

**Components own different failure surfaces.** Memory dominates on Hard and actively hurts on Easy,
where its lessons reduce to redundant re-checking. Middleware clears every Easy task and inflates
turn count on Hard. There is no single best component; there is a best component per failure class.

**The gains do not add.** The three positive single-component swaps sum to +11.1 points. Together
they deliver +7.3 `[AHE §4.4.1]`. Chapter 48 is about why, and the short answer visible here is that
memory, middleware, and the prompt all push toward the same closure-style verification, so stacking
them spends turns re-checking work already checked.

**The full harness is beaten on Hard by one of its own components.** Memory alone scores 63.3% on
Hard; the full harness scores 53.3%. An optimiser tuning an aggregate dominated by Medium tasks
converged to a trade-off that gave back part of the Hard gain. That is not a bug in the loop. It is
what optimising a scalar over a heterogeneous population does, and Chapter 41 is where you decide
which scalar you are willing to have optimised.

---

## 6. Runtime Sequence

One model turn, traced through every component type it touches.

```
                                                              TIME VIEW

  harness            model              tool               environment
     |                 |                  |                     |
  (1)| assemble context
     |   system prompt + long-term memory + loaded skills
     |   + conversation history + any middleware injection
     |                 |                  |                     |
  (2)| middleware.before_model
     |   may inject a reminder from the previous step's analysis
     |---------------->|                  |                     |
  (3)|                 | generate         |                     |
     |<----------------|                  |                     |
  (4)| middleware.after_model
     |   may rewrite or reject the reply
     |                 |                  |                     |
  (5)| reply is a tool request; read the tool DESCRIPTION
     |   to validate arguments against schema
     |                 |                  |                     |
  (6)| middleware.before_tool
     |   may block the call outright
     |                 |----------------->|                     |
  (7)|                 |                  | tool IMPLEMENTATION |
     |                 |                  |-------------------->|
  (8)|                 |                  |<--------------------|
     |                 |<-----------------|                     |
  (9)| middleware.after_tool
     |   may append hints, detect cross-step risk patterns
     |                 |                  |                     |
 (10)| append result to history; possibly write long-term memory
     |                 |                  |                     |
     +-- next turn --> |                  |                     |

  Figure 1.4 -- One turn through the harness (D4 Sequence)
```

Steps (2), (4), (6), and (9) are the middleware hooks, and their placement explains the enforcement
hierarchy better than any argument. Middleware sits *between* every other component and the model.
It does not persuade; it intervenes.

Step (9) is where the AHE run put its most productive cross-step component: a hook that reads the
recent command history alongside the new output, detects one of several recurring risk patterns, and
appends a corrective note so the agent self-corrects on the following turn `[AHE App. C.2.3]`. A
later refinement moved that note from the tool output into the *next* turn's opening context,
because warnings trailing after a tool result were being read past `[AHE App. C.2.4]`. Same
information, different position, materially different outcome. That is harness engineering.

---

## 7. State Management

What each component type holds, and whether it changes at runtime.

| Component type | Holds | Mutable at runtime? | Mutable between runs? |
|----------------|-------|--------------------|-----------------------|
| System prompt | Nothing; it is text | No | Yes — by a human or an evolution loop |
| Tool description | Nothing; schema and prose | No | Yes |
| Tool implementation | Whatever it chooses to keep | Yes, within a run | Yes |
| Middleware | Accumulated cross-step state | **Yes — this is its purpose** | Yes |
| Skill | Nothing; loaded text | No | Yes |
| Sub-agent config | Nothing; the child run holds state | No | Yes |
| Long-term memory | Facts that outlive a run | Written by the running agent | Yes |
| Short-term memory | Session scratch | Yes | Not an evolution target `[AHE App. B.2]` |

Two distinctions this table is enforcing.

**Runtime-mutable versus evolution-mutable are different axes.** Middleware state changes during a
run and is discarded; the middleware *code* changes between runs and persists. Confusing the two is
how teams end up with harness components that quietly accumulate per-tenant state and cannot be
scaled out.

**Short-term memory is deliberately outside the editable set.** In the AHE workspace it is managed
by the running agent and explicitly excluded from the evolution loop's action space `[AHE App. B.2]`.
Chapter 43 explains why an evolution loop must not be able to edit its own scratchpad.

---

## 8. Interfaces

Mount points and contracts. Full signatures in Appendix E.

| Component type | Mount point | Contract |
|----------------|-------------|----------|
| System prompt | `workspace/systemprompt.md` | Text; runtime variables interpolated at assembly |
| Tool description | `workspace/tool_descriptions/<id>.tool.yaml` | Name, description, input schema |
| Tool implementation | `workspace/tools/<pkg>/<fn>.py` | A callable; runtime injects context by signature inspection |
| Middleware | `workspace/middleware/<mod>.py` | A class implementing one or more hooks; registered with parameters |
| Skill | `workspace/skills/<name>/SKILL.md` | Frontmatter plus body; discovered by directory scan |
| Sub-agent | `workspace/sub_agents/<name>/agent.yaml` | Its own model config, tools, and prompt |
| Long-term memory | `workspace/LongTermMEMORY.md` | Free text, read at context assembly |
| Registry | `workspace/agent.yaml` | Declares which of the above are active |

**Creating a file is not enough.** Every component type except memory and the system prompt must be
registered in the agent configuration to take effect `[AHE App. B.2]`. `[INF]` This is worth an
explicit validation step in your build: an unregistered component is a silent no-op, and a silent
no-op inside an evolution loop is an edit that gets credited or blamed for an outcome it had no part
in.

---

## 9. Data Structures

| Structure | Shape | Owner |
|-----------|-------|-------|
| `HarnessComponent` | type, mount_path, content_digest, registered | Ch 43 |
| `ToolSpec` | tool_id, description, input_schema, effect | Ch 14 |
| `MiddlewareSpec` | import_path, params, hook_set, order | Ch 14 |
| `SkillSpec` | name, description, path, load_trigger | Ch 12 |
| `SubAgentSpec` | name, config_path, description | Ch 19 |
| `HarnessVersion` | component set digest + base model identity | Ch 38 |

`[INF]` `HarnessVersion` is the handbook's own construct and the direct answer to the cold open. If
the harness is fitted to a model, then a harness identity that does not include the model identity
is describing something that does not exist. Chapter 38 makes a model upgrade a harness-invalidation
event by construction rather than by discipline.

---

## 10. Communication

| Direction | Carries | Between |
|-----------|---------|---------|
| Inbound to the harness | Goal, prior history, environment state | Edge → context assembly |
| Harness → model | Assembled context | Context system → model port |
| Model → harness | Reply or tool request | Model port → loop |
| Harness → environment | Tool effects | Tool implementation → sandbox, network, services |
| Environment → harness | Results, errors, observations | Sandbox → tool → middleware → history |
| Harness → durable store | Facts worth keeping | Memory writes, trajectory capture |
| Harness → evolution loop | The complete trajectory | Ch 16 → Ch 44 |

**Dependencies the harness has on things it does not own.** The model provider and its rate limits.
The environment's shape, which changes without notice. The runtime's budgets and timeouts, which
`[AHE Limitations]` shows are effectively part of the harness's fit even though they are usually
configured somewhere else entirely. That last one is the cold open, and it is the strongest argument
in this chapter for treating operating-point configuration as a harness component rather than as
infrastructure.

---

## 11. Failure Modes

| Failure | Detected by | Recovery |
|---------|-------------|----------|
| Fix placed at too weak a level | The failure class recurs across iterations | Roll back the edit; re-approach at a stronger level `[AHE App. B.2]` |
| Component created but not registered | Configuration validation; runtime logs | Register it; add validation to CI |
| Harness fitted to a superseded model | Task completion drops after a model change with no code change | Re-fit the operating point; treat as a versioning event |
| Components interfering | Aggregate gain below the sum of individual gains | Measure single-component variants; Ch 48 |
| Prompt bloat | System prompt grows monotonically; per-call cost rises with no gain | Migrate rules to enforcing components |
| Memory rot | Long-term memory accumulates lessons that no longer hold | Periodic review; Ch 49 |

### 11.1 The failure worth dwelling on

**Prompt bloat** deserves more than a table row, because it is the default trajectory of every agent
system with a human maintainer. A failure appears; someone adds a sentence to the prompt; the
sentence is cheap and it works in testing. Repeat for eighteen months.

The cost is not only that prose is the weakest enforcement level. It is that the prompt rides along
on *every* model call, so every rule added for a rare situation is paid for on every common one.
The comparison in `[AHE §4.3]` is direct: prompt-carried strategy distilled on one task surface both
regressed and cost more tokens when moved to another, while behaviour encoded in tools, middleware,
and memory transferred and cut aggregate token spend by 12% against the seed. Encoding behaviour in
code is cheaper at inference time than encoding it in words, and Chapter 35 puts numbers on that.

---

## 12. Scalability

Harness scaling is not a throughput question. It is a question about whether the thing keeps working
as it grows.

| Dimension | Scales well | Scales badly |
|-----------|-------------|--------------|
| Number of tools | Up to the point where selection becomes the bottleneck | Beyond it — the model spends turns choosing |
| Number of skills | Well, by design: loaded on demand, not resident | Only if load triggers are precise |
| Prompt length | Poorly. Linear cost on every call, sub-linear benefit | Always |
| Middleware count | Well, if each owns a distinct pattern | Badly when two hooks push the same behaviour `[AHE §4.4.1]` |
| Long-term memory | Well while entries stay specific and factual | Badly once it becomes general advice |
| Sub-agents | Well for isolation | Badly for attribution; every added agent is a place to hide |

`[INF]` The general shape: **components that are loaded conditionally scale; components that are
always present do not.** The system prompt and resident memory are always present, so their growth
is a tax. Skills, sub-agents, and middleware hints are conditional, so their growth is closer to
free. This is a useful first filter when deciding where a new behaviour belongs.

---

## 13. Production Engineering

### 13.1 Best practices

- **Version the harness as an artifact, with the model identity inside the version.** Not as loose
  files beside the application.
- **Keep component types decoupled.** Adding a middleware should never require touching a prompt
  `[AHE §3.1]`. When it does, one of them is doing the other's job.
- **Validate registration in CI.** An unregistered component is a silent no-op.
- **Prefer the strongest level that is not overkill,** and record why you chose it. Chapter 45 makes
  that record mandatory; doing it by hand now costs nothing and pays immediately.
- **Start minimal.** The AHE seed was deliberately one shell tool and nothing else, because a seed
  already fitted to the target would contaminate the attribution of every later change `[AHE §3.1]`.
  The same logic applies to a human-built harness: components added before there is evidence for
  them cannot be evaluated afterwards.

### 13.2 Trade-offs

| Choice | Buys | Costs |
|--------|------|-------|
| Enforce in tool code | Reliability independent of model cooperation | Rigidity; the model cannot route around a genuinely wrong rule |
| Enforce in the prompt | Flexibility and cheap iteration | Compliance rather than guarantee; per-call token cost forever |
| Many small tools | Precise descriptions, clear errors | Selection overhead |
| One general tool | Low selection cost | Everything happens inside one opaque verb |
| Rich long-term memory | Specific, transferable knowledge | Staleness, and superfluous re-checking on easy tasks |

### 13.3 Anti-patterns

| Anti-pattern | Why it fails | Diagnosed in |
|--------------|-------------|--------------|
| **Prompt as the only surface** | The weakest enforcement level, paid for on every call | §11.1, Ch 11 |
| **The tangled harness** | Components that cannot be edited independently cannot be attributed independently | Ch 43 |
| **Unversioned harness** | The cold open; a model upgrade silently invalidates a fit | Ch 38 |
| **Component hoarding** | Adding components without removing them; interference accumulates invisibly | Ch 48 |
| **Editing the wrong region** | Attempting to fix a harness problem by changing sampling parameters, or an environment problem by changing the prompt | Ch 31, Ch 46 |

---

## 14. Relation to AHE

This chapter *is* the substrate AHE operates on. Three connections carry forward.

**The seven component types are the action space.** Component observability — the first of AHE's
three pillars — is realised by exactly the decoupling described in §3.2: each failure pattern maps
to a single component class, giving the evolution agent a clean action space and localising every
change in outcome to one file `[AHE §3.1]`. Chapter 43 builds it.

**The constraint hierarchy is the choice the evolution agent makes each round.** Every manifest entry
records which level it targeted and why that level rather than another `[AHE App. B.2]`. Chapter 45
gives the schema.

**The model region is deliberately off-limits.** AHE's controllability constraint makes model
configuration read-only — no changing the model, no raising the reasoning budget, no touching the
verifier `[AHE §3.3]`. Without that boundary, an evolution loop optimises the easiest variable rather
than the useful one. This chapter's three-region diagram is what makes the boundary statable at all:
you cannot forbid edits to a region you have not drawn.

### 14.1 Where the two sources disagree by omission

`[INF]` A synthesis worth making explicit now, because it explains why this handbook needs both
sources rather than one. Map the durable runtime's six ports against AHE's seven component types:

| Durable runtime port `[DAR §10]` | AHE component type `[AHE §3.1]` |
|----------------------------------|----------------------------------|
| Planner | no direct equivalent — planning is emergent from prompt and skills |
| Tool | tool description + tool implementation |
| Model | **deliberately non-editable** |
| Grader | partially: middleware finish-hooks; the verifier itself is read-only |
| Approval | **absent** — no human-in-the-loop construct |
| Domain | **absent** — the environment is a benchmark, not a product |
| — | middleware, skill, sub-agent config, long-term memory: **no port equivalent** |

The two sources have complementary blind spots. The runtime architecture has no concept of memory,
skills, or middleware — it assumes the model-facing surface is fixed and concerns itself with
survival. AHE has no concept of human authority or a product domain — it assumes an unattended
benchmark and concerns itself with improvement. A production system needs both halves, which is why
they are co-primary here and why neither is allowed to absorb the other's vocabulary.

---

## 15. Industry Perspective

### Supported by the attached AHE paper `[AHE]`

- The harness is the collection of model-external, editable components mediating how a model
  perceives and acts on its environment (§1, §2.1).
- Seven orthogonal component types exposed as files at fixed mount points; loose coupling such that
  adding middleware requires no prompt edit (§3.1).
- Decoupling maps each failure pattern to a single component class and localises outcome changes to
  one file (§3.1).
- Component-level ablation results, all figures in §5.3 (§4.4.1).
- The system prompt inserted alone regresses by 2.3 points; the evolved prompt was 79 lines (§4.4.1).
- Long-term memory alone scored highest of the single-component swaps and exceeded the full harness
  on the Hard tier; it contained 12 boundary-case lessons (§4.4.1).
- The evolved shell tool reached roughly 1,364 lines and surfaced contract hints from nearby files
  (§4.4.1).
- Positive single-component gains sum to +11.1 points against a combined +7.3 (§4.4.1).
- The optimal harness is model-specific and must be re-adapted as the base model changes (§1).
- Cross-model transfer gains ranged +2.3 to +10.1 points and were non-monotone within one model
  family; step budget and timeout were fitted to one operating point (§4.3, Limitations).
- Prompt-carried strategy regressed and cost more tokens off-target; tool-, middleware-, and
  memory-encoded behaviour transferred and cut aggregate tokens by 12% against the seed (§4.3).
- The minimal seed was chosen so a pre-fitted starting point would not contaminate attribution
  (§3.1).
- Model configuration, verifier, and tracer are read-only to the evolution agent (§3.3).
- Components must be registered in the agent configuration to take effect; short-term memory is
  excluded from the editable set (App. B.2).
- Middleware accumulating cross-step state and injecting corrective notes; the later move of those
  notes into the next turn's opening context (App. C.2.3, C.2.4).

### Supported by the attached Durable Runtime architecture `[DAR]`

- The six-port extension surface used in the comparison in §14.1 (§10).

### Engineering inference `[INF]`

- The three-region model of Figure 1.1 and the claim that the harness is the only region that is
  simultaneously yours, editable, and load-bearing.
- The enforcement-strength ordering of Figure 1.3 as a total order. Its endpoints are evidenced by
  the ablation; the middle ranks are a heuristic.
- The rule "put a fix at the weakest level that can enforce it, and no weaker."
- The conditional-versus-resident scaling filter in §12.
- `HarnessVersion` including model identity, and treating operating-point configuration as a harness
  component.
- The port-to-component mapping in §14.1 and the claim that the two sources have complementary blind
  spots.

### Industry best practice `[BP]`

- Configuration validation in CI as a guard against silently inactive components.
- Separating a tool's schema from its implementation so each can change independently.

### Future proposal `[FUT]`

- None in this chapter.

---

## 16. Key Takeaways

1. **Three regions: model, harness, environment.** The harness is the only one that is yours,
   editable, and load-bearing at the same time. That intersection is why it is the subject of this
   book.
2. **The harness is seven component types, not one prompt.** System prompt, tool description, tool
   implementation, middleware, skill, sub-agent configuration, long-term memory — decoupled, so that
   each failure pattern maps to exactly one of them.
3. **They differ in enforcement strength.** Code enforces; prose requests. Put a fix at the weakest
   level that can enforce it, and no weaker.
4. **The measurement is unambiguous at the endpoints.** Memory, tools, and middleware each carried
   gains alone; the system prompt alone regressed. Specific factual knowledge beats general
   instruction.
5. **Gains do not add.** Components that push toward the same behaviour interfere, and the aggregate
   falls short of the sum.
6. **The harness is fitted to a model.** A harness version that does not include the model identity
   is describing something that does not exist — which is the cold open, and Chapter 38's rule.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Model** | The rented, fixed thing that turns text into text; you select and configure it, you never change it. | `[AHE]` | Ch 13 |
| **Harness** | Everything you write between the model and the world: the only region that is yours, editable, and load-bearing at once. | `[AHE]` | every chapter |
| **Environment** | The real world the work happens in — filesystem, shell, network, repositories — which you can constrain and observe but not control. | `[AHE]` | Ch 25, Ch 31 |
| **Component type** | One of seven kinds of harness part, chosen so that each failure pattern maps to exactly one of them. | `[AHE]` | Ch 43 |
| **System prompt** | Standing instructions sent with every call; the weakest of the seven, because the model may ignore prose. | `[AHE]` | Ch 11 |
| **Tool description** | What the model is told a tool does, as distinct from what the tool actually does. | `[AHE]` | Ch 14, Ch 15 |
| **Tool implementation** | The code that runs when a tool is called; enforces rather than requests. | `[AHE]` | Ch 14 |
| **Middleware** | Code hooked into the loop that intercepts or transforms every pass through it, whether the model wants it or not. | `[AHE]` | Ch 14 |
| **Skill** | A packaged, reusable procedure loaded only when it is relevant, so its tokens are not always resident. | `[AHE]` | Ch 11 |
| **Sub-agent configuration** | The definition of a nested agent used to isolate context, not to build an org chart. | `[AHE]` | Ch 19 |
| **Long-term memory** | Facts kept across runs as a file the model reads, rather than a store it queries. | `[AHE]` | Ch 12 |
| **Enforcement strength** | How hard a component is to ignore: code compels, prose asks. Fixes belong at the weakest level that can still enforce them. | `[INF]` | Ch 46 |
| **Harness version** | The identity of a complete component set, pinned together with the model identity, because neither is meaningful alone. | `[INF]` | Ch 38 |

---

**Next:** Chapter 2 — *Why an Agent Runtime Is a Distributed System.* We take the four properties
that appear the moment work outlives a request, show that each has a well-understood defect and a
well-understood fix, and establish the vocabulary that Level 1 turns into an architecture.
