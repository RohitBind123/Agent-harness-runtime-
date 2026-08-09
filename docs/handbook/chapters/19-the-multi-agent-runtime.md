```
  Level 2 · Chapter 19
  THE MULTI-AGENT RUNTIME
  Requires   C11 The Context System, C14 The Tool Execution Engine,
             C16 The Observation System, C18 The Runtime Loop
  Unlocks    C24 The Task Graph, C29 Long-Running Agents,
             C31 Safety and Sandboxing, C44 Experience Observability
  Diagrams   Full (9)
```

# Chapter 19 — The Multi-Agent Runtime

---

## 1. Motivation

### 1.1 Cold open

The Atlas team splits the system into three: a Researcher that explores the repository, a Coder that
writes the patch, and a Reviewer that checks the work. It mirrors how the team itself operates, and
the first demo is excellent.

Task completion drops four points. Cost per run roughly quadruples.

The trace shows why. The Reviewer rejects a correct patch because it cannot see *why* the Coder chose
that approach — the Researcher's finding that the obvious fix breaks a downstream consumer was in the
Researcher's context, not the Reviewer's. The Coder, given a rejection with no reasoning attached,
tries the obvious fix. The Reviewer accepts it. The build breaks.

Nobody built this badly. Each sub-agent had a clear responsibility, a good prompt, and the right
tools. The defect is in the decomposition: the boundaries were drawn where a human org chart draws
them, and human colleagues share a hallway, a history, and the ability to ask a follow-up question.

Three sub-agents, one of which is now guessing.

### 1.2 In plain language

A sub-agent is a nested run: the system starts a second, smaller job inside the first one, gives it
its own instructions and its own view, lets it work, and takes back a result.

The reason to do that is almost never the reason people think.

The tempting reason is division of labour — a specialist for each part of the job, like a team. That
is the cold open, and it fails because your colleagues are not actually independent. They overhear
things, they remember last week, and when a hand-off is ambiguous they walk over and ask. A sub-agent
can do none of that. It gets what you send it and nothing else.

The good reason is **keeping things out of the way**. Suppose answering one question means reading
four hundred files. Done in the main job, those four hundred files are now in its context, are paid
for on every subsequent step, and crowd out everything else (Chapter 11). Done in a sub-agent, the
reading happens somewhere else and only the answer — a couple of hundred words — comes back.

That is the whole test. A sub-agent is worth it when a large amount of material has to be *looked at*
to produce a small answer. If the material is small, or the answer needs to be large, a tool is
better, cheaper, and easier to debug.

### 1.3 Why this chapter exists

Chapter 18 assembled a runtime that drives one run. This chapter is what happens when a run starts
another one, and it is short on new machinery for a reason: a sub-agent is a run, driven by the same
loop, through the same ports. Nothing in Chapters 10 to 18 changes.

What does change is that the decisions get harder. `[AHE §3.1]` lists sub-agent configuration as one
of the seven editable component types, which means an evolution loop will eventually be adding
sub-agents — and `[INF]` a loop rewarded on outcomes will add them for the cold open's reasons,
because role decomposition is what the training data of human organisations looks like.

So this chapter's main product is a test for when a sub-agent is the wrong answer.

### 1.4 What previous framings got wrong

**"Agents should mirror a team."** The cold open. An org chart is a solution to human coordination
constraints — attention, expertise, hours in a day — and none of those apply here. §5.1 gives the
decomposition that does.

**"More agents, more capability."** Each sub-agent is a full context, a full set of tool definitions,
and its own model calls. Two agents cost more than twice one, because coordination is not free
(§12.1).

**"Sub-agents are how you parallelise."** Sometimes, and Chapter 24's task graph is usually the
better tool. Parallelism is about independent *work*; sub-agents are about independent *context*.
Confusing the two produces a graph of agents where a graph of steps would do.

**"The sub-agent can just report back."** `[INF]` Marshalling is the hard part and gets the least
design. Whatever crosses the boundary is all the parent will ever know, and §5.3 argues the return
shape should be designed before the sub-agent is.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Commissioning a survey.

You are preparing a planning application and you need to know whether the ground can bear the load.
You do not read soil science; you commission a geotechnical survey. Somebody spends three weeks
drilling boreholes, runs laboratory tests, and produces a report whose operative content is one
paragraph: the ground bears this much, subject to these conditions.

That is a good delegation, and the reason is precise: **an enormous amount of material had to be
examined to produce a small, decision-shaped answer**, and you never needed the boreholes. You needed
the paragraph.

Now consider a bad one. You commission a separate survey for drainage, and the drainage surveyor is
not told what the geotechnical survey found. They specify a soakaway that the soil report has already
ruled out. Both reports are competent. The combination is wrong, and it is wrong because the second
commission was scoped as a *role* — "the drainage person" — rather than as a question with the
context needed to answer it.

The cold open is a Reviewer commissioned as a role.

**Where the analogy breaks.** Two surveyors can telephone each other. When the drainage surveyor
reads something odd, they call the geotechnical firm and ask. That channel exists whether or not
anybody designed it, and it silently rescues most badly-scoped commissions in real professional
practice.

`[INF]` Sub-agents have no such channel and cannot be given one cheaply: a sub-agent that can query
its parent mid-run is a sub-agent whose context is no longer isolated, which removes the only reason
it existed. So the brief must be *complete at dispatch*, and §5.2's delegation contract is what
completeness looks like when there is no way to ask a follow-up question.

### 2.2 Why sub-agents exist at all

```
  1. A model call carries a context, and the context has a hard
     ceiling and a per-call price (Ch 11).
  2. Some questions require examining far more material than will fit
     -- four hundred files, a long log, a large diff.
  3. Reading it in the main run puts all of it in the main context,
     where it is paid for on EVERY subsequent step and crowds out
     everything else.
  4. But the ANSWER is usually small: which file, which cause, does
     this hold.
  5. So we want the reading to happen somewhere whose context we can
     discard, and only the answer to survive.
  6. A tool cannot do this when producing the answer requires
     JUDGEMENT across the material -- a tool returns what it found,
     not what it concluded.
  7. So we need something that has its own context, can reason, and
     returns a small result: a nested run.
  8. That is the entire justification. Any other reason for a
     sub-agent is a reason to use a tool, a task graph, or nothing.
```

Step 6 is the discriminator and it is the one worth memorising. `[INF]` If the answer can be produced
by *filtering or transforming* the material, a tool is correct and strictly better. Only when the
answer requires reading the material and *forming a view* is a sub-agent doing something a tool
cannot.

### 2.3 The test

> **Delegate when a large amount of material must be examined to produce a small answer that requires
> judgement. Otherwise do not.**

`[INF]` Applied to the cold open: does reviewing a patch require examining a large amount of material
to produce a small judgement? Reviewing the *diff* does not — the diff is small. So the Reviewer
fails the test and should have been a grader (Chapter 28) operating on the same context as the Coder.
Whereas the Researcher — four hundred files in, a two-hundred-word finding out — passes it cleanly.

One of three was correctly a sub-agent. That ratio is typical.

### 2.4 The mental model to carry

> **A sub-agent is a context boundary, not a job title. It exists so that a lot of reading can happen
> somewhere you are willing to throw away.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +--------------------------------------------------------------+
  |  PARENT RUN                                                  |
  |                                                              |
  |   +------------------+                                       |
  |   | runtime loop     |  (Ch 18) -- unchanged                 |
  |   +--------+---------+                                       |
  |            | (1) dispatches a step whose tool is             |
  |            |     tool.agent.delegate                          |
  |            v                                                 |
  |   +========+=========+                                       |
  |   | TOOL ENGINE      |  (Ch 14) -- delegation is a TOOL      |
  |   +========+=========+                                       |
  |            | (2) DelegationContract                          |
  +------------|-------------------------------------------------+
               v
  +--------------------------------------------------------------+
  |  CHILD RUN            its own row, its own lease, its own     |
  |                       context, its own budget                 |
  |   +------------------+                                       |
  |   | runtime loop     |  (3) THE SAME LOOP                    |
  |   +--------+---------+                                       |
  |            |                                                 |
  |   +--------+-------------------------------+                 |
  |   | ports: planner, context, model, tool   |  (4) same ports |
  |   +----------------------------------------+                 |
  |                                                              |
  |            | (5) a SMALL result crosses back                 |
  +------------|-------------------------------------------------+
               v
       +-------+--------+          +~~~~~~~~~~~~~~~~~+
       | marshalled     |          | SANDBOX         |
       | result, ~200-  |  (6)     | shared or       |
       | 2000 tokens    |<---------| isolated (Ch 31)|
       +----------------+          +~~~~~~~~~~~~~~~~~+

  What does NOT cross the boundary:
     the child's context      the point of the exercise
     the child's tool results the material it examined
     the child's plan         its reasoning is not the parent's

  Figure 19.1 -- A sub-agent is a nested run
                 (D1 High-Level Architecture)

  (1) delegation is dispatched like any other step
  (2) the contract is the entire brief; there is no follow-up
  (3) the same loop, the same exit conditions (Ch 18)
  (4) the same ports, scoped differently (section 5.4)
  (5) marshalling: designed before the sub-agent is (5.3)
  (6) sandbox sharing is a separate decision from context
      isolation, and the two are often confused
```

`[INF]` The diagram's most important feature is how little of it is new. One tool, one contract, one
result shape. A team that finds itself building a message bus between agents, a shared blackboard, or
an agent registry has decomposed by role and is now rebuilding the hallway that human colleagues had
for free.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  DELEGATION, opened

  +--------------------------------------------------------------+
  |                                                              |
  |  1. RESOLVE      sub_agents/<name>/agent.yaml   (Ch 43)       |
  |     |              its own system prompt                      |
  |     |              its own TOOL SUBSET (section 5.4)          |
  |     |              its own model policy (Ch 13)               |
  |     |              its own limits (Ch 18)                     |
  |     v                                                        |
  |  2. CONTRACT     build the brief. Everything the child will   |
  |     |            ever know. No follow-up channel exists.      |
  |     v            section 5.2                                  |
  |  3. BUDGET       carve the child's cap OUT of the parent's    |
  |     |            remaining budget. Not additional.            |
  |     v            section 5.5                                  |
  |  4. DEPTH        check nesting depth against the cap.         |
  |     |            Exceeded -> refuse, do not truncate          |
  |     v                                                        |
  |  5. SPAWN        create a child run row: parent_run_id set,   |
  |     |            same tenant, own lease, own trajectory       |
  |     v                                                        |
  |  6. PARK         the parent PARKS awaiting the child.         |
  |     |            It holds NOTHING while the child runs        |
  |     v            (Ch 5) -- this is the key design choice      |
  |  7. RUN          the child is driven by the ordinary loop,    |
  |     |            claimed by any worker (Ch 18)               |
  |     v                                                        |
  |  8. MARSHAL      the child's terminal result -> the schema    |
  |     |            the contract declared. Validated, not        |
  |     v            coerced (Ch 10 section 4.1)                  |
  |  9. RESUME       << child.completed >> wakes the parent,      |
  |                  which resumes at the delegating step         |
  +--------------------------------------------------------------+

  Figure 19.2 -- One delegation (D2 Low-Level Architecture)
```

### 4.1 The parent parks; it does not wait

`[INF]` Step 6 is the decision that makes this chapter cheap, and it is easy to get wrong.

The obvious implementation has the parent's loop call the child and await it. That holds a worker for
the child's entire duration — and if the child itself delegates, it holds two. A tree of depth three
with a fan-out of three holds thirteen workers, twelve of which are doing nothing but waiting.

Parking instead means the parent holds a row. `[DAR §8.2]` A park is resolved by an event, and
`child.completed` is an event like any other. The parent resumes at the delegating step, finds a
recorded result (Chapter 21), and continues.

The consequence is worth stating plainly: **the cost of a deep agent tree is rows, not workers.**

```
                                                            LAYER VIEW

  Components. Almost all of them are borrowed.

   ProposedToolCall (tool.agent.delegate)
        |
        v
   +----+------------+        +---------------------+
   | Sub-agent       |        | Contract builder    |
   | registry        |------->|  the complete brief |
   |  agent.yaml     |        +----------+----------+
   +-----------------+                   |
        |                                v
        | tool subset         +----------+----------+
        v                     | Budget splitter     |
   +----+------------+        |  carves from parent |
   | Tool registry   |        +----------+----------+
   | (Ch 14)         |                   |
   |  descriptions_  |                   v
   |  for(subset)    |        +----------+----------+
   +-----------------+        | Depth guard         |
                              |  refuse, not clamp  |
   +-----------------+        +----------+----------+
   | Run store       |                   |
   | (Ch 17)         |<------------------+
   |  parent_run_id  |     spawn child run
   +--------+--------+
            |
            v
   +--------+--------+        +---------------------+
   | THE SAME LOOP   |------->| Marshaller          |
   | (Ch 18)         |        |  validate to schema |
   +-----------------+        +----------+----------+
                                         |
                              +----------v----------+
                              | << child.completed >>|
                              |  wakes the parent    |
                              +---------------------+

  Figure 19.3 -- Delegation components (D3 Component Diagram)
```

`[INF]` Five small components and one borrowed loop. If your equivalent diagram contains an agent
supervisor, an inter-agent message router, or a shared memory space, each of those is worth
challenging against §2.2: what question does it answer that a contract and a result shape do not?

---

## 5. Delegation

### 5.1 Decompose by context, not by role

`[INF]` The two decompositions of the same work, side by side:

| By role (the cold open) | By context |
|---|---|
| Researcher, Coder, Reviewer | one run, plus a *codebase-search* sub-agent |
| each has partial information | the main run holds the whole picture |
| hand-offs lose reasoning | nothing is handed off |
| 3 contexts, 3 tool sets, 3 budgets | 1 context, plus a discardable one |
| review has no access to rationale | grading happens in-context (Ch 28) |

The rule that generates the right answer: **draw the boundary around material you want to throw away,
never around a responsibility you want to name.**

`[INF]` A useful sanity check is to ask what the sub-agent's result would look like if the sub-agent
were a person handing you a sheet of paper. "Here are the three files that touch this behaviour, and
why" is a sheet of paper. "I have reviewed your work and rejected it" is not a sheet of paper; it is
a decision that needed the context you did not send.

### 5.2 The delegation contract

Because there is no follow-up channel (§2.1), the brief must be complete at dispatch:

```yaml
# sub_agents/codebase_search/agent.yaml
name: codebase_search
purpose: |
  Find where a behaviour is implemented in a large repository and
  explain how the relevant pieces connect.

returns:
  schema:
    files: [{path: str, role: str}]
    explanation: str          # <= 200 words
    confidence: enum[high, medium, low]
    unexplored: [str]         # what it did NOT look at -- section 5.3
  max_tokens: 600

tools: [repo.find, repo.read_file, repo.grep]   # section 5.4
limits:
  step_budget: 12
  wall_clock: 180s
  budget_share: 0.15          # of the PARENT's remaining (5.5)
```

`[INF]` `unexplored` is the field most contracts lack and the one that prevents the cold open's second
half. A sub-agent that ran out of steps having read forty of four hundred files must be able to say
so, or the parent treats a partial search as exhaustive — the same false-confidence failure Chapter 14
solved with `empty_means`, arriving one layer up.

### 5.3 Marshalling is the design, not the plumbing

Whatever crosses the boundary is everything the parent will ever know. `[INF]` So the return schema
should be written *before* the sub-agent's prompt, because it is the only part of the design with no
recovery from being wrong.

Three rules:

| Rule | Why |
|---|---|
| Bounded size, declared | an unbounded return reintroduces the context problem it solved |
| Structured, validated, never coerced | Chapter 10 §4.1's rule: a malformed return is evidence, not something to repair |
| Include what was *not* covered | partial work must be distinguishable from complete work |

`[INF]` The failure to watch for is a return schema of `{"result": str}`. It passes validation always,
carries whatever the child felt like saying, and makes the boundary untestable. A schema that cannot
fail is not a contract.

### 5.4 The child's tool subset is a capability decision

Chapter 14 §8 established that capability scoping works by *omission* from what the model is shown.
A sub-agent is where that becomes routine: the `codebase_search` agent is given three read tools and
no write tools, so it structurally cannot modify anything.

`[INF]` This is the strongest safety property in the chapter and it is nearly free. A sub-agent
dispatched to read four hundred files has a large blast radius if it can also write; scoped to three
pure tools, its worst case is reading the wrong thing. Chapter 31 builds on this, and the rule it
starts from is: **a sub-agent's tool subset should be the smallest set that can answer its
question**, and for search agents that set contains no effectful tools at all.

### 5.5 Budget is carved, never added

Step 3 of §4. `[INF]` The child's cap comes *out of* the parent's remaining budget, not in addition to
it. Otherwise a run's total spend is unbounded in the depth of its agent tree, and a budget cap
(Chapter 13 §5.3) stops meaning anything.

```
  parent budget remaining        $4.00
  child cap = 15% of remaining   $0.60   <- reserved from the parent
  parent's own remaining         $3.40   <- while the child runs
  child settles at               $0.31
  returned to the parent         $0.29
```

Unused budget returns on completion, so a cheap child does not permanently consume the parent's
allowance. `[INF]` A child that exhausts its cap fails as a child — it does not park the parent
awaiting a budget grant, because the parent may have other options and only it can decide.

### 5.6 Nesting depth: refuse, do not clamp

A depth cap of two or three is normal. When it is exceeded, `[INF]` the delegation must be **refused
as an error the parent sees**, not silently executed at the boundary depth.

The reason is diagnostic. A clamped tree still works, produces slightly worse results, and gives no
signal — so a sub-agent that recursively delegates to itself looks like a quality problem for weeks.
A refusal produces a `SCHEMA_REJECTED`-style event (Chapter 14) and a planner that must choose
something else.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  parent loop   tool eng   child run   child loop   marshaller
      |            |           |           |            |
      | step 6: tool.agent.delegate(codebase_search)     |
      |----------->|           |           |            |
      |            |-- resolve agent.yaml  |            |
      |            |-- build contract      |            |
      |            |-- carve budget: $0.60 of $4.00     |
      |            |-- depth 1 of 2: ok    |            |
      |            |-- spawn ->|           |            |
      |            |           | child run row created  |
      |            |           | parent_run_id = R1     |
      |<-- PARKED awaiting child ---------|            |
      |                                                  |
      |  === parent holds NOTHING. Its worker is free. ===|
      |                                                  |
      |            |           |-- claim ->|            |
      |            |           |  child episode 1: 5 steps
      |            |           |  reads 412 files, 180 KB context
      |            |           |-- claim ->|            |
      |            |           |  child episode 2: 4 steps
      |            |           |  child SUCCEEDS        |
      |            |           |           |-- marshal ->|
      |            |           |           |<-- validated: 3 files,
      |            |           |           |    174-word explanation,
      |            |           |           |    confidence=high,
      |            |           |           |    unexplored=[]
      |            |           |.. << child.completed >> ..>|
      |                                                  |
      |  relay claims the event -> parent re-enqueued     |
      |                                                  |
      |-- claim (a DIFFERENT worker) ------------------->|
      |  resumes at step 6; identity has a recorded      |
      |  result (Ch 21) -> reused, not re-delegated      |
      |  parent context grows by ~500 tokens, NOT 180 KB |
      |  $0.29 unused budget returned                     |

  Failure branch: the child exhausts its step budget at 400 of 412
  files. It returns confidence=low and unexplored=[...]. The parent
  sees a PARTIAL answer and can replan (Ch 10) -- rather than
  treating a truncated search as exhaustive.

  Figure 19.4 -- One delegation, end to end (D4 Sequence)
```

### 6.1 The numbers are the argument

`[INF]` 180 KB of context existed inside the child and never entered the parent. The parent's context
grew by roughly five hundred tokens.

Had the search happened in the main run, those 180 KB would have been in the parent's context on
step 6 — and on step 7, and on every step after, until compaction evicted them (Chapter 11 §5.5). For
a run of forty steps, that is the difference between paying for the search once and paying for it
thirty-four times.

That ratio is the entire economic case for sub-agents, and it evaporates when the delegation is
scoped by role: a Reviewer's context is not large, so isolating it saves nothing and costs a
coordination round-trip.

```
                                                             TIME VIEW

  The delegation cycle, from the parent's side.

   step proposes tool.agent.delegate
          |
          v
   +------+-----------------+
   | resolve + contract     |
   +------+-----------------+
          |
          v
        /   \
       /depth\ exceeded --------------------------> E1 refuse
       \  ?  /
        \   /
          | ok
          v
        /   \
       /budget\ insufficient -----------------------> E2 refuse
       \  ?   /
        \    /
          | ok
          v
   +------+-----------------+
   | spawn child; PARK      |  parent holds nothing
   +------+-----------------+
          |
          v
   +------+-----------------+
   | child runs (Ch 18)     |  ordinary loop, ordinary exits
   +------+-----------------+
          |
    +-----+-----+-----------+------------+
    |           |           |            |
    v           v           v            v
 succeeded   failed    step budget    cancelled
    |           |      exhausted         |
    v           v           v            v
 +--+---------+ +--------+ +---------+ +--------+
 | marshal    | | E4     | | marshal | | E6     |
 | validate   | | child  | | PARTIAL | | cancel |
 +--+---------+ | failed | | conf=low| | cascade|
    |           +--------+ +----+----+ +--------+
    v                           |
  /   \                         |
 /valid\ no -> E5 malformed     |
 \  ?  /       return; evidence  |
  \   /        not repaired      |
    | yes                        |
    v                            v
  E3 result recorded; parent resumes and continues

  Exits:
    E1  depth cap exceeded  -> refused; the planner must replan
    E2  insufficient budget -> refused; the parent decides, not
                               the child (section 5.5)
    E3  clean result        -> recorded by identity; parent resumes
    E4  child failed        -> parent sees the failure and replans
    E5  malformed return    -> rejected, never coerced; emits the
                               training signal (Ch 14)
    E6  parent cancelled    -> cancellation cascades to children
                               (section 7.2)

  Figure 19.5 -- The delegation cycle and its exits (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

  The parent and child, as two independent run state machines with
  exactly two couplings.

  PARENT                              CHILD
  +------------------+
  | {{ EXECUTING }}  |
  +--------+---------+
           | delegates
           v                          +------------------+
  +------------------+   spawn        | {{ CREATED }}    |
  | {{ PARKED }}     |--------------->+--------+---------+
  |  awaiting_child  |                         |
  +--------+---------+                         v
           ^                          +------------------+
           |                          | {{ EXECUTING }}  |
           |                          +--------+---------+
           |                                   |
           |   << child.completed >>           v
           +------------------------- +------------------+
           |          (COUPLING 1)    | {{ SUCCEEDED }}  |
           |                          | {{ FAILED }}     |
           v                          +------------------+
  +------------------+
  | {{ EXECUTING }}  |
  +------------------+

  COUPLING 2: parent CANCELLED  ->  children cancelled (cascade)

  Everything else is independent:
    * the child has its OWN lease, version, and worker
    * the child has its OWN trajectory (Ch 16)
    * the child parking does NOT park the parent further
    * a child failing does NOT fail the parent -- it is a result

  Illegal:
    * a child outliving a terminal parent   -- cascade, always
    * a child writing the parent's run state -- it returns a value
    * a child inheriting the parent's context -- the whole point
    * shared budget without carving          -- section 5.5

  Figure 19.6 -- Parent and child state (D6 State Diagram)
```

### 7.1 A child failing is a result, not a failure

`[INF]` The distinction matters and is easy to lose. When a sub-agent fails, the parent receives that
as the outcome of a step, exactly like a failed tool call (Chapter 14 §5.6). The parent's planner
then decides: retry with a different brief, do the work inline, or give up.

A child failure that propagates automatically to the parent removes that decision and makes the
parent's robustness a function of its most fragile child.

### 7.2 Cancellation cascades; parking does not

Coupling 2, and the asymmetry is deliberate. `[INF]` Cancelling a parent must cancel its children —
otherwise a cancelled run leaves orphaned work spending money, which is Chapter 13's cold open
arriving by inheritance.

But a *parked* parent does not park its children: the parent is parked precisely because a child is
running. And a parked child does not park the parent further — the parent is already waiting on it.

The rule: **terminal states cascade downward; waiting states do not cascade at all.**

---

## 8. Internal APIs

```python
from typing import Protocol


class DelegationPort(Protocol):
    """Sub-agents. Deliberately thin: a sub-agent is a run, driven by
    the loop of Ch 18 through the ports of Ch 10-14."""

    async def delegate(
        self,
        parent: ClaimedRun,
        agent_name: str,
        brief: Brief,
    ) -> DelegationHandle:
        """Spawn a child and PARK the parent (section 4.1).

        Returns a handle, not a result: the parent does not await. It
        resumes when << child.completed >> wakes it.

        Raises DepthExceeded and BudgetInsufficient -- both refusals the
        planner sees, never silently clamped (section 5.6).
        """

    async def marshal(
        self, child: TerminalRun, contract: ReturnContract
    ) -> MarshalledResult:
        """Validate the child's terminal output against the declared
        schema. Rejects; never coerces (Ch 10 section 4.1)."""


class SubAgentRegistry(Protocol):
    """sub_agents/<name>/agent.yaml -- a harness component (Ch 43),
    editable, versioned, and in the Evolve Agent's action space."""

    def resolve(self, name: str) -> SubAgentSpec: ...
```

`[INF]` `delegate` returning a handle rather than a result is the API-level expression of §4.1. A
signature returning `MarshalledResult` would invite `await delegate(...)`, which holds the worker for
the child's duration and turns a depth-three tree into thirteen held workers. The type makes the
cheap design the natural one.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SubAgentSpec:
    name: str
    system_prompt: str
    tool_subset: tuple[str, ...]      # section 5.4: smallest that works
    model_policy: PolicyId            # Ch 13; often cheaper than parent
    limits: EpisodeLimits             # Ch 18
    budget_share: float               # of the parent's REMAINING (5.5)
    return_contract: ReturnContract
    max_depth_from_root: int


@dataclass(frozen=True)
class ReturnContract:
    schema: Mapping[str, object]
    max_tokens: int                   # bounded, declared, enforced
    require_unexplored: bool = True   # section 5.2


@dataclass(frozen=True)
class MarshalledResult:
    payload: Mapping[str, object]
    tokens: int
    complete: bool                    # False when the child ran out
    unexplored: tuple[str, ...]
    child_run_id: RunId               # joins to the child's trajectory
    cost_cents: int
```

Three fields carry the chapter.

**`tool_subset` is a tuple on the spec**, not a runtime argument — capability is a property of the
sub-agent, decided once and reviewable, rather than something a caller chooses per delegation.

**`complete` and `unexplored` together** are what stop a partial search reading as exhaustive. `[INF]`
A parent that ignores `complete` has reintroduced the cold open's second half by a different route.

**`child_run_id`** is what makes the whole tree navigable in Chapter 16's trace store. Without it, a
parent trajectory contains a result that appeared from nowhere, and Chapter 44 cannot follow the
reasoning down.

---

## 10. Communication

```
                                                            LAYER VIEW

  brief          parent ====> child        ~2-8 KB    the whole brief
  child context  (internal to the child)   ~50-200 KB per call, and
                                            NEVER crosses back
  marshalled     child  ====> parent       ~0.5-3 KB  <-- the point
  event          child  ....> outbox       ~300 B     << completed >>

  The compression ratio IS the justification:
     180 KB examined  ->  500 tokens returned
     and the 180 KB is paid ONCE, not on every later step

  Figure 19.7 -- What crosses the boundary (D7 Data Flow)
```

```
                                                             TIME VIEW

  parent planner --> delegation   PROPOSES a delegation, as a step
  delegation -----> child run     spawn, then PARK the parent
  child loop -----> ports         the same six, scoped (section 5.4)
  child --X        parent state   REFUSED: it returns a value
  child --X        parent context REFUSED: that is the whole point
  parent --X       child mid-run  REFUSED: no follow-up channel (2.1)
  parent cancel --> child cancel  cascades downward (section 7.2)

  Figure 19.8 -- Who may delegate, and what may talk back
                 (D8 Control Flow)
```

```
                                                             TIME VIEW

  << child.spawned >>     ....> parent, child, agent name, budget
                                carved. The tree, made durable
  << child.completed >>   ....> wakes the parent; the ONLY channel
                                back
  << delegation.refused >>....> depth or budget; the training signal
                                for a planner that over-delegates

  NOT events:
    the child's steps        its own trajectory (Ch 16)
    the marshalled result    a RESULT, keyed by identity (Ch 21)
    the child's context      never leaves the child

  Figure 19.9 -- What delegation makes durable (D9 Event Flow)
```

### 10.1 Long edges declared here

| To | What travels | Why it matters there |
|---|---|---|
| Ch 24 Task Graph | parallelism is a graph question, not an agent one | the usual better alternative |
| Ch 28 Grading | the Reviewer should have been a grader | in-context judgement |
| Ch 31 Safety | tool subset as blast-radius control | the strongest cheap property here |
| Ch 35 Cost | budget carved, not added | tree spend stays bounded |
| Ch 44 Agent Debugger | `child_run_id` links the tree | a trajectory that can be followed down |
| Ch 46 Evolve Agent | sub-agent configs are editable | it will add agents; §2.3 is the guard |

---

## 11. Failure Modes

| Failure | Trigger | Detector | Recovery |
|---|---|---|---|
| Decomposed by role | mirroring a human team | hand-offs where the receiver lacks rationale | decompose by context — the cold open |
| Parent awaits the child | `await delegate(...)` | worker count scaling with tree depth | park; return a handle (§4.1) |
| Unbounded return | `{"result": str}` | parent context growing after delegations | bounded, structured, validated (§5.3) |
| Partial read as exhaustive | no `complete` / `unexplored` | confident answers from truncated searches | require both fields |
| Budget added, not carved | child cap independent of parent | total spend unbounded in depth | carve from remaining (§5.5) |
| Depth clamped silently | recursion capped at the boundary | quality decline with no signal | refuse; emit an event (§5.6) |
| Child writes parent state | convenience coupling | parent state changing outside its loop | children return values |
| No cancellation cascade | independent lifecycles | cancelled runs with children still spending | terminal states cascade (§7.2) |
| Sub-agent with write tools | inherited the parent's tool set | blast radius equal to the parent's | smallest subset (§5.4) |
| Agents where a graph would do | parallelism sought via delegation | many shallow agents, little context saved | Chapter 24 |

`[INF]` Row ten is the one most likely to survive review, because parallel sub-agents genuinely are
faster and the saving looks real. The test is §2.3: if each parallel agent examines a small amount of
material, the isolation bought nothing and the coordination cost was paid anyway. Independent *work*
belongs in a task graph; independent *context* belongs here.

---

## 12. Scalability

### 12.1 Coordination is not free

`[INF]` A delegation costs, at minimum: a brief assembled and paid for, a child context assembled
from scratch (no cache warmth from the parent), a spawn, a park, an event, a re-enqueue, and a
marshalling call. Call it two extra model calls and two extra round-trips before any work happens.

So the saving has to exceed that. `[INF]` A rough threshold: **delegate when the material to be
examined exceeds roughly ten times the size of the answer**, and the run has enough steps remaining
that the context saving compounds. Below that, inline it.

### 12.2 The tree costs rows, not workers

| Quantity | Scales with | Because |
|---|---|---|
| Workers held | concurrently *executing* runs | parked parents hold nothing (§4.1) |
| Rows | total nodes in all trees | one row per run, parent or child |
| Budget | bounded by the root's cap | carving (§5.5) |
| Context tokens | sum over executing nodes | each child's context is its own |

`[INF]` A tree of depth three and fan-out three has thirteen rows and, at any instant, as few as one
executing run. Compare the awaiting design, where the same tree pins thirteen workers with twelve
idle — a 13× difference in the resource that actually costs money.

---

## 13. Production Engineering

### 13.1 Signals

| Signal | Why | Alert |
|---|---|---|
| Context compression ratio per agent | §6.1's justification, measured | below ~10× means it should be inline |
| Delegations per run | over-delegation | rising without a quality gain |
| `complete=False` rate per agent | children running out of budget | high means limits are too tight |
| Depth-refusal rate | recursive delegation | any sustained non-zero |
| Marshalling rejection rate | contract and child disagree | rising means the schema or prompt drifted |
| Parked parents vs executing children | should be roughly 1:1 | parents outnumbering children badly |
| Child cost as a share of run cost | budget carving working | above the configured share |

`[INF]` The first row is the one that decides whether a sub-agent should exist at all, and it is
computable from data already captured: bytes in the child's contexts over tokens in its marshalled
result. An agent sitting at 2× is a tool that has not been written yet.

### 13.2 The test that catches the cold open

```python
async def test_delegation_does_not_leak_child_context_to_parent(
    runtime: Runtime, traces: TrajectoryReader
) -> None:
    run = await runtime.submit_and_finish(goal_requiring_search)
    parent = await traces.open(run.id, reader=SYSTEM)

    delegations = parent.spans_of(SpanKind.TOOL_CALL, tool="tool.agent.delegate")
    assert delegations

    for d in delegations:
        child = await traces.open(d.result.child_run_id, reader=SYSTEM)
        child_ctx = sum(s.tokens for s in child.spans_of(SpanKind.CONTEXT_ASSEMBLED))
        assert child_ctx > 20_000, "child did little reading; should be a tool"

        # The property: the parent's context grew by the RESULT, not the
        # material. Compare the assembled context before and after.
        before, after = parent.context_around(d.span_id)
        assert after.tokens - before.tokens < 2_000


async def test_parent_holds_no_worker_while_child_runs(runtime: Runtime) -> None:
    run = await runtime.submit(goal_requiring_search)
    await runtime.advance_until_delegation(run)
    assert (await runtime.state(run)) is RunState.PARKED
    assert (await runtime.lease_owner(run)) is None
```

`[INF]` The first assertion in the first test is the unusual one: it fails when a sub-agent read *too
little*. It is a test that the decomposition was justified, not that the code works — and it is the
only mechanical form of §2.3 available.

---

## 14. Relation to AHE

Sub-agent configuration is one of the seven editable component types `[AHE §3.1]`, which makes this
chapter's judgement calls part of the evolution loop's action space.

**The loop will over-delegate, and for a plausible reason.** `[INF]` An Evolve Agent editing
configuration has read an enormous amount of human writing about how teams organise, and role
decomposition is what that writing describes. Adding a Reviewer agent is the most natural edit in the
space. Nothing in an outcome-based reward signal distinguishes it from a good decomposition until the
measurement comes back — by which time the iteration has spent its budget.

`[INF]` The mitigation is §13.1's first metric. A compression ratio per sub-agent is computable
before quality data arrives, and a proposed sub-agent with a projected ratio near 1 can be rejected
mechanically. That is a rare case where an ACI-style structural check can pre-empt an expensive
evaluation.

**Sub-agents complicate attribution.** Chapter 47 attributes an outcome change to an edit. A run with
a three-node tree has three harness configurations in play — the parent's and two children's — and a
quality change may belong to any of them. `[INF]` `child_run_id` on the marshalled result (§9) is
what makes the attribution tractable at all, because it lets the debugger separate the child's
contribution from the parent's.

**Tool subsets are the containment that survives.** Chapter 14 put the effect tag outside the
workspace; here the analogous boundary is that a sub-agent's `tool_subset` may be *narrowed* by the
Evolve Agent and never widened. `[INF]` Widening is how a loop would give a search agent write
access to make it "more capable", which is locally sensible and removes the property §5.4 exists for.

---

## 15. Industry Perspective

**`[AHE]`** Supplies sub-agent configuration as one of the seven editable component types and the
harness workspace layout that holds it `[AHE §3.1]`.

**`[DAR]`** Supplies the park as the mechanism that lets a parent wait while holding nothing, and the
event-resolved resume that wakes it `[DAR §8.2]`.

**`[INF]`** The handbook's own: decomposition by context rather than by role and the test that
generates it, the survey analogy and the observation that professional practice is rescued by a
telephone call that has no analogue here, the requirement that the brief be complete at dispatch,
`unexplored` and `complete` as contract fields, marshalling designed before the sub-agent, budget
carved rather than added, refuse-do-not-clamp on depth, the compression-ratio metric as a
pre-evaluation check on whether a sub-agent should exist, and the rule that tool subsets may be
narrowed but never widened by an evolution loop.

**`[BP]`** Bounded delegation with explicit contracts is ordinary practice in service design, and
"return a handle, not a result" is standard for long-running work. The contribution is the argument
that the *reason* for delegation is context economics rather than division of labour.

**`[FUT]`** `[FUT]` Nothing here lets a sub-agent ask a clarifying question, and §2.1 argues that a
follow-up channel would dissolve the isolation that justified the delegation. Whether a *bounded*
clarification — one question, answered from the parent's existing context, without the child seeing
that context — recovers most of the benefit at acceptable cost is open, and the handbook knows of no
system that has tried it.

---

## 16. Key Takeaways

1. **A sub-agent is a context boundary, not a job title.** It exists so a lot of reading can happen
   somewhere you are willing to throw away.
2. **Decompose by context, never by role.** An org chart solves human coordination constraints that
   do not apply here, and your colleagues have a hallway that sub-agents do not.
3. **The test: much material examined, small answer, judgement required.** If the answer can be
   produced by filtering, write a tool. If the material is small, inline it.
4. **The parent parks; it never awaits.** A tree then costs rows rather than workers — a 13× resource
   difference on a depth-three tree.
5. **The brief is complete at dispatch.** There is no follow-up channel, and adding one would remove
   the isolation that justified delegating.
6. **Design the return before the sub-agent.** Bounded, structured, validated, and carrying what was
   *not* covered — a schema that cannot fail is not a contract.
7. **Carve the budget; refuse on depth.** Added budget makes spend unbounded in tree depth; a
   silently clamped depth turns runaway recursion into an unexplained quality decline.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Sub-agent** | A nested run with its own context, driven by the same loop through the same ports. | `[AHE]` | Ch 31, Ch 46 |
| **Context isolation** | The reason to delegate: examining a lot of material somewhere whose context is discarded. | `[INF]` | Ch 46 |
| **Delegation contract** | The complete brief plus the declared return shape, fixed at dispatch because no follow-up is possible. | `[INF]` | Ch 24 |
| **Marshalling** | Validating a child's terminal output against the declared schema; rejected rather than coerced. | `[INF]` | Ch 44 |
| **Return contract** | The bounded, structured schema a sub-agent's result must satisfy, designed before the sub-agent. | `[INF]` | Ch 46 |
| **Unexplored** | The contract field recording what a child did not cover, so partial work is distinguishable from complete. | `[INF]` | Ch 28 |
| **Budget carving** | Taking a child's cap out of the parent's remaining allowance, so tree spend stays bounded. | `[INF]` | Ch 35 |
| **Nesting depth cap** | The limit on delegation chains, enforced by refusal rather than by silent clamping. | `[INF]` | Ch 31 |
| **Tool subset** | The smallest set of tools a sub-agent needs, which may be narrowed by evolution but never widened. | `[INF]` | Ch 31, Ch 46 |
| **Compression ratio** | Material examined over result returned; the computable check on whether a sub-agent is justified. | `[INF]` | Ch 34, Ch 46 |
| **Cancellation cascade** | Terminal states propagating from parent to children, while waiting states do not propagate at all. | `[INF]` | Ch 30 |

---

**Next:** Chapter 20 — *The Self-Evolving Runtime (AHE), Overview.* The closed loop in one chapter:
three observability pillars, the Evolve Agent, the change manifest, and Algorithm 1 — placed here so
the evolution frame is carried through Levels 3 and 4 rather than met for the first time at the end.
