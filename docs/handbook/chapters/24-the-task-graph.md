```
  Level 3 · Chapter 24
  THE TASK GRAPH
  Requires   C10 The Planner, C17 The State Manager, C18 The Runtime Loop,
             C21 Durable Execution, C22 The Event Spine
  Unlocks    C26 Planning Algorithms, C27 Failure and Rollback,
             C29 Long-Running Agents, C32 Distributed Execution
  Diagrams   Core (5)
```

# Chapter 24 — The Task Graph

---

## 1. Motivation

### 1.1 Cold open

Atlas is migrating `payments-api` off a deprecated HTTP client. Forty files, one edit each, plus a
final step that opens the pull request. The plan is a list of forty-one steps; the run takes
sixty-two minutes.

Someone points out that thirty-eight of those forty edits touch different files and have nothing to
do with one another. The team ships parallel steps: the planner marks independent steps, and the
driver launches them together. The migration drops to nine minutes. Nobody argues with nine minutes.

Three weeks later, run `r_88c1` is seven minutes in when the node it is on is drained during a
routine deploy. Thirty-one of the forty edits have completed. The run resumes on a fresh worker,
reads its plan, sees `step_index = 0` — the driver only ever advanced the index past the parallel
block once *all* of it had finished — and re-runs all forty.

The file edits are content-idempotent, so they are harmless. Nine of those steps also posted a
review comment on the pull request. Nine duplicate comments, on a customer's repository, at 04:00.

The postmortem proposes making `post_comment` idempotent. That is correct, and it is the third time
that quarter someone has fixed this class of bug one tool at a time. The defect is upstream of every
one of those fixes: progress through the fan-out lived in the driver's memory. There were forty
facts to remember — which branches had finished — and the durable record could hold exactly one.

### 1.2 In plain language

A plan is a list of steps in order. That is a fine description right up until you notice that most
of the order is an accident.

When the planner emits "edit file A, edit file B, edit file C", it writes them in *some* sequence
because a list has to have one. It is not saying that B must wait for A. It is saying that it
thought of A first. Two completely different facts — "this must happen after that" and "this was
written down after that" — are riding in the same piece of structure, and nothing distinguishes
them.

A task graph separates them. Each unit of work becomes a node. Each genuine "must happen after"
becomes an edge. Everything with no edge between it is independent, and now says so out loud.

The obvious payoff is speed: things with no edges between them can run at the same time. That is
the least interesting payoff. The real one is that once you have written down what depends on what,
you can answer questions a list cannot answer at all — what can be retried without redoing
everything else, what a human needs to approve before anything downstream moves, which one slow
branch is actually setting the run's total time.

And the hard part is not starting several things at once. Anyone can do that. The hard part is
knowing they have all finished, in a way that survives the machine being switched off halfway.

### 1.3 Why this chapter exists

Chapter 10 established that a plan is immutable and that a replan mints a new plan rather than
editing the old one. It deliberately left the plan's internal shape as a list, because a list was
enough to make that argument, and because introducing a graph at that point would have buried the
identity argument under structure.

The list has now run out. Three separate pressures push against it, and each one arrives from a
different chapter:

- **Chapter 21** needs to know, on resume, exactly what has already happened. A single cursor into
  a list can express "we got to step 17". It cannot express "steps 1 through 16 and 18 through 31
  are done, and 17 failed".
- **Chapter 23** needs work to be individually claimable so it can be admitted, classed, and
  fairly scheduled. A list offers one claimable thing at a time per run, which caps a run's
  parallelism at one regardless of what the scheduler could afford.
- **Chapter 30** needs to hold a specific piece of work at a gate without holding the entire run.
  A list cannot pause its middle.

None of those three is a performance argument. The task graph is often introduced as a throughput
feature and then justified with a speedup number, which is how it acquires a reputation as an
optimisation you can defer. It is not an optimisation. It is the data structure that makes
recovery, gating, and per-unit accounting expressible at all.

### 1.4 What previous framings got wrong

**"A task graph is parallelism."** Parallelism is one consequence. A graph with a single linear
chain of forty nodes is still worth having, because forty durable completion records recover
correctly and one cursor does not. The width of the graph and the value of the graph are
independent.

**"The executor should hold the topological order."** The classic implementation computes a
topological sort at the start and walks it. This is the same mistake as Chapter 22's cursor: it puts
the run's position in a place that a crash erases, and it forces the whole ordering to be recomputed
identically on resume. The alternative is to keep no order at all and ask a question instead —
*which nodes have every predecessor complete?* — which is a query over durable rows and is therefore
correct on a fresh process with no memory of anything.

**"Cycles are a runtime concern."** Detecting a cycle while executing means discovering it after
some of its nodes have already had effects. Because a plan is immutable and minted once
(Chapter 10), the entire graph is known before a single node runs, and acyclicity is checkable at
admission — once, cheaply, before anything has happened. Every executor that carries a cycle
detector is compensating for a validator it did not write.

**"Fan-out and fan-in are two halves of one feature."** They are not comparable in difficulty.
Fan-out is a loop that inserts rows. Fan-in is a distributed counting problem with a durability
requirement, and it is where every real bug in this chapter lives.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A task graph is a build system. You do not tell `make` the order to compile things in; you tell it
that `main.o` depends on `main.c`, and it derives an order — and, given enough cores, derives that
twelve of your files can compile at once. Dependency declaration in, schedule out.

That analogy carries further than most in this book. Ready-set computation, fan-out width, the
critical path, the observation that adding workers past the critical path buys nothing — all of it
transfers directly, and the vocabulary is worth borrowing.

Here is what does not transfer, and it is the half that matters.

A build system's nodes are **pure functions of their inputs**. That single property is what earns it
its best trick: content-address the inputs, and if they have not changed, skip the node entirely and
reuse last time's output. Incremental builds exist because of purity, not because of the graph.

An agent's nodes are not pure. `edit_file(path="client.py", instruction="migrate to the new
client")` run twice does not produce the same diff twice, because the model that executes it is not
a function. And many nodes are effectful in the sense of Chapter 14: running them again is not
merely wasteful, it is visible to somebody outside the system.

So the graph gives you dependency algebra, ready-set computation, and fan-out. It does not give you
skip-if-unchanged, and it does not give you the build system's cheerful willingness to re-run any
node it is unsure about. A build system's default on doubt is *rebuild*. A task graph's default on
doubt must be *check whether this already happened* — which is Chapter 21's activity identity, and
is why the two chapters are adjacent.

### 2.2 Why a graph must exist

```
  (1) Start where Chapter 10 left off: a plan is an ordered list, and the
      executor holds an integer index into it. This works.

  (2) A forty-file migration arrives. Thirty-eight of its steps touch
      disjoint files and have no relationship to each other. The order
      between them is an artefact of how the planner emitted them.

  (3) Run them together. Immediately the run has more than one position,
      and `step_index` is one integer. The representation is now unable
      to describe the state the system is actually in.

  (4) Try holding the set of finished branches in the driver's memory.
      A crash erases it. Resume re-runs completed effectful work --
      this is the cold open, and no amount of care in the driver fixes
      it, because the driver is the thing that disappeared.

  (5) So per-node completion must be durable: one row per unit of work,
      committed by the worker that finished it. Nothing else survives
      the process.

  (6) Once completion is per-node and durable, "what may run next" stops
      being a pointer and becomes a question: which nodes have every
      predecessor complete? That question is answerable from the rows
      alone, by a process that has just started and remembers nothing.

  (7) But that question needs to know what "predecessor" means, and the
      list's position can no longer supply it -- position was exactly
      what step (3) destroyed. Dependencies must therefore be written
      down explicitly, as their own rows.

  (8) Nodes, plus explicit dependency edges, plus a rule forbidding
      cycles, is a directed acyclic graph. It was not selected from
      alternatives. It is what steps (3) through (7) leave behind.
```

The derivation is worth re-reading in one respect: parallelism appears at step (2) and is never
mentioned again. Steps (4) through (7) are entirely about crash recovery. The graph is forced by
durability, and the speedup is change left over.

### 2.3 The three jobs a list was doing

A list of steps was quietly carrying three unrelated responsibilities. The graph's contribution is
to give each one its own home, which is what makes the resulting system easier rather than harder
to reason about despite having more parts.

| Job | Carried in a list by | Carried in a graph by |
|---|---|---|
| **What must happen after what** | position, ambiguously | edges, explicitly |
| **What order a human should read it in** | position | a `rank` on each node, presentational only |
| **Where the run has got to** | the cursor | not stored; derived by query |

The third row is the one that repays attention. In the list model, "where we are" is a stored fact
that must be kept accurate. In the graph model, it is not stored at all — it is recomputed from
completion rows every time anyone asks. There is no cursor to be wrong, no cursor to be lost, no
cursor to be advanced twice. The state that caused the cold open stopped existing.

This is the same move Chapter 22 made when it replaced the relay's cursor with per-event claims, and
the same move Chapter 17 made when it replaced a lock with a version compared on write. Three
chapters, three subsystems, one shape: **replace a remembered position with a question answerable
from durable facts.** When that shape is available it is almost always right, because a question has
no crash semantics to get wrong.

### 2.4 The mental model to carry

A task graph is a set of durable rows and one query. The rows say what work exists, what depends on
what, and what has finished. The query — *nodes with no incomplete predecessor* — is the entire
scheduler-facing surface. Everything else in this chapter is either a detail of how to make that
query fast, or a consequence of the fact that fan-in has to count.

---

## 3. High-Level Architecture

The graph does not execute anything. It answers a question for the runtime loop and records the
answer the loop hands back. The loop from Chapter 18 is unchanged in shape; what changed is where it
gets its next unit of work.

```
                                                            LAYER VIEW

   +~~~~~~~~~~~~~~~~~~+
   |   Goal / issue   |
   +~~~~~~~~~~~~~~~~~~+
            |
            v
   +------------------+     one immutable graph, minted once, validated
   |     Planner      |     at admission: acyclic, connected, bounded
   |      (C10)       |
   +------------------+
            |  (1) INSERT nodes + edges + joins, one transaction
            v
   +------------------------------------------------------------+
   |   [[ plan_nodes ]]   [[ plan_edges ]]   [[ plan_joins ]]    |
   +------------------------------------------------------------+
            ^                          |
            |  (3) completion          |  (2) ready-set query
            |      + join tick,        v
            |      one transaction   +--------------------------+
            |                        |    Ready-set resolver    |
            |                        +--------------------------+
            |                          |  zero..N claimable nodes
            |                          v
            |                        +--------------------------+
            +------------------------|      Runtime loop        |
                                     |          (C18)           |
                                     +--------------------------+
                                                 |
                                                 v
                                          +================+
                                          |   Tool port    |
                                          |     (C14)      |
                                          +================+

  Figure 24.1 -- The task graph in its surroundings (D1 High-Level
                 Architecture)
```

| Wire | Carries | Why it is shaped this way |
|---|---|---|
| (1) | The whole graph | Nodes, edges and join rows are inserted in one transaction, so no worker can ever observe a graph missing an edge and run a node early. |
| (2) | A ready set | A query, not a subscription. The resolver holds nothing between calls and is correct on a process that started one millisecond ago. |
| (3) | One completion | The node's terminal status and every join tick it causes are committed together. Chapter 22's same-transaction rule, applied to counting. |

Three properties of this picture are load-bearing.

**The planner still proposes and nothing else does.** Chapter 9's "one proposer, three vetoes" is
intact. The resolver does not decide what work exists; it decides which of the already-decided work
is currently legal to start. That is a filter, not a proposal.

**The resolver is stateless.** It can be called by any worker, in any process, at any time, and two
concurrent calls returning the same node is not a bug — Chapter 17's lease and version compare make
the second claim fail harmlessly. This is what lets Chapter 32 run one graph across many machines
without adding a coordinator.

**The loop did not learn about graphs.** It asks for work and reports outcomes. Whether the answer
came from a list, a graph, or a single hard-coded step is not a distinction the forty lines of
Chapter 18 can see. That is the point of having kept them decision-free.

---

## 4. Low-Level Decomposition

Opening the box in the middle of Figure 24.1 gives four parts, of which only one has any real
subtlety.

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |                        TASK GRAPH                            |
   |                                                              |
   |  +--------------------+      +----------------------------+  |
   |  |  Admission         |      |  Ready-set resolver        |  |
   |  |  validator         |      |                            |  |
   |  |                    |      |  nodes WHERE status=pending|  |
   |  |  - acyclic         |      |  AND NOT EXISTS (an edge   |  |
   |  |  - node cap        |      |    from an unfinished pred)|  |
   |  |  - width cap       |      |  AND join_open = false     |  |
   |  |  - depth cap       |      |                            |  |
   |  |  runs ONCE, at     |      |  runs on EVERY poll;       |  |
   |  |  mint time         |      |  holds nothing             |  |
   |  +--------------------+      +----------------------------+  |
   |                                                              |
   |  +--------------------+      +----------------------------+  |
   |  |  Completion writer |      |  Join controller           |  |
   |  |                    |      |                            |  |
   |  |  status -> done    |      |  arrived := arrived + 1    |  |
   |  |  + emit event      |      |  satisfied when policy met |  |
   |  |  + tick joins      |      |  ALL / K_OF_N / FIRST      |  |
   |  |  ALL IN ONE TXN    |      |  cancels losers on FIRST   |  |
   |  +--------------------+      +----------------------------+  |
   |                                                              |
   +--------------------------------------------------------------+

  Figure 24.2 -- Inside the task graph (D2 Low-Level Architecture)
```

**The admission validator** runs once, when the planner mints the plan, and never again. It rejects
graphs rather than repairing them, and a rejection is a planning failure that goes back to the
planner with the reason attached — which is Chapter 15's argument about errors being instructions,
applied to a structure rather than a tool call. Its four checks are acyclicity, a cap on node count,
a cap on maximum width, and a cap on maximum depth. The last three are not aesthetic. A graph with
900 parallel nodes is a denial-of-service against the model semaphore of Chapter 23, and the cheapest
place to stop it is before it is stored.

**The ready-set resolver** is one SQL statement. Its shape matters more than its contents: it is a
`NOT EXISTS` over incomplete predecessors, not a join that counts them, because a `NOT EXISTS` can
stop at the first incomplete predecessor it finds and a count cannot.

**The completion writer** is the transactional heart. It writes the node's terminal status, appends
the node-completed event to the outbox of Chapter 22, and increments every join the node feeds — all
inside one transaction. If any part of that fails, none of it happened, and the node is retried.

**The join controller** is the part with genuine design content, and §5 is about it.

### 4.1 What the graph deliberately does not contain

A short list, because each absence is a decision that will look like an oversight:

- **No priority field.** Priority is Chapter 23's, and it belongs to the run, not the node. A node
  inheriting a different priority than its siblings produces a graph that finishes out of order for
  reasons no one can reconstruct three weeks later.
- **No retry counter.** Attempts belong to the attempt record (Chapter 21), not the node. A node is
  a description of work; an attempt is an occurrence of it. Merging them loses the ability to say
  "this succeeded on the third try", which Chapter 34 needs.
- **No timing fields beyond `started_at` and `ended_at`.** Duration is derived. Storing it means
  storing something that can disagree with its inputs.
- **No conditional edges.** An edge means "after". It does not mean "after, if". Conditionality
  lives in the node's own body, which may complete with status `skipped` — and a skipped node
  satisfies its successors exactly as a done one does. Putting predicates on edges turns the
  validator's acyclicity check into a reachability analysis and makes the ready-set query
  unindexable. This is the single most frequently requested feature in this subsystem and it should
  be declined every time.

---

## 5. Fan-Out, Fan-In, and the Durable Join

### 5.1 Fan-out is not the problem

Fan-out is a node with several outgoing edges. Executing it is: the node completes, the resolver's
next call returns several nodes instead of one, and the loop claims as many as its lease budget
allows. There is no fan-out code. It falls out of the ready-set query being a set rather than a
scalar, and it needed no new machinery whatsoever.

It is worth saying this plainly because fan-out is the part that gets demonstrated. It is the part
that produces the nine-minute migration and the graph on the slide. It is also the part with no
engineering in it.

### 5.2 Fan-in is a counting problem with a durability requirement

Fan-in is a node with several incoming edges, and the question it asks is: *have they all
finished?* On one machine with no crashes, that is a counter. Neither of those conditions holds.

The counter must be a durable row, and the increment must be in the same transaction as the
completion that caused it. Consider the two orderings if it is not:

- Increment first, then commit the completion. A crash between them leaves a join that has counted
  a branch that did not finish. The join fires early. Downstream work runs on absent results, and
  nothing anywhere reports an error — the counter is a plausible number.
- Commit the completion first, then increment. A crash between them leaves a branch that is done
  and uncounted. The join never fires. The run stalls at full health, with every node either
  complete or waiting, and no failure to alert on. This is Chapter 22's silent stall, in a different
  subsystem, produced by the same missing transaction.

Both orderings are wrong, and they are wrong in the two directions that are hardest to detect: one
produces confident bad output, the other produces no output at all. There is no third ordering. The
completion and the tick are one write or the system has a gap.

```
                                                             TIME VIEW

   node A ....>  << node.completed A >>  --+
                                          |
   node B ....>  << node.completed B >>  --+---> [[ plan_joins ]]
                                          |      arrived: 0 -> 1 -> 2 -> 3
   node C ....>  << node.completed C >>  --+      required: 3
                                                  |
   each event and its tick commit                 | policy ALL met
   in ONE transaction with the                    v
   node's own status write                 << join.satisfied >>
                                                  |
                                                  v
                                          successors become ready

   ................................................................

   CRASH between B's status write and B's tick, if they were
   separate transactions:

       arrived stays 2, required is 3, B is done
       -> no event is ever emitted
       -> no node is ever ready
       -> the run is neither failed nor progressing
       -> every dashboard is green

  Figure 24.3 -- Fan-in as durable counting, and the gap that opens if
                 the tick is a separate write (D9 Event Flow)
```

### 5.3 Three join policies, and what each owes the losers

`ALL` is the default and covers most cases: every incoming branch must reach a terminal status.
Note *terminal*, not *successful* — a failed branch also arrives, and whether its arrival satisfies
or poisons the join is a policy on the join, not a property of counting. The common setting is that
a failure arrives and marks the join failed, which propagates to successors as `skipped`.

`K_OF_N` fires when *k* branches have succeeded. It exists for the case Chapter 28 calls sampling:
run the same task five ways, take the first three that pass verification. The remaining branches are
allowed to keep running and their results are recorded and ignored.

`FIRST` fires on the first success and cancels the rest. It is the policy with the sharp edge,
because cancellation is not free. A losing branch that has already called an effectful tool has
already had its effect; cancelling it stops future work, not past work. The rule that follows is
narrow and should be enforced in the validator, not in review: **a `FIRST` join may only be fed by
branches whose nodes are all pure.** Chapter 14's effect tag, which was introduced to decide whether
a tool needs a gate, turns out to also decide whether a branch may be raced. One tag, two unrelated
consumers, which is generally a sign the tag was cut in the right place.

### 5.4 Dynamic fan-out

The forty-file migration knows it is forty files only after a search has run. The graph cannot have
contained forty nodes when it was minted, because at mint time the number was unknown.

The available answers are worth stating because the wrong one is very attractive:

- **Mutate the graph mid-run to add the forty nodes.** This is the attractive one, and it destroys
  the immutability that Chapter 10 spent a chapter establishing. A graph that changes has no
  identity, and a plan without identity cannot be replayed, compared, or approved.
- **Make the fan-out node a sub-run.** The search node completes, and its completion mints a *new*
  plan — a new immutable graph with forty nodes — whose parent is the node that produced it. The
  parent graph has one node where the forty are; that node completes when the child graph does.

The second is correct, and it is Chapter 19's sub-agent boundary reappearing as a purely structural
device. A sub-run is not a role, an assistant, or a specialist. It is a scope in which a graph whose
size was unknown can be minted without mutating the graph that asked for it.

The join for the child graph is created by the same transaction that creates the child's nodes, so
`required` is written down at the moment it becomes knowable and never afterwards. A join whose
`required` is updated after any branch has arrived is a race, unconditionally.

### 5.5 Cycles, and why they are never a runtime concern

Acyclicity is checked once by a depth-first traversal over the proposed edges at mint time, in
memory, before a single row is inserted. Cost is linear in edges; a graph large enough for this to
matter has already failed the node cap.

The reason this is worth a subsection rather than a sentence is that models propose cycles. Not
often, and not maliciously — a decomposition that says "write the migration, then run the tests,
then fix the failures, then run the tests" has a cycle in it, and it is a perfectly reasonable thing
for a human to say. The validator rejects it and returns the cycle as a path: `n4 -> n5 -> n4`. The
planner's next attempt unrolls it into a bounded repeat, or converts it into the episode structure
of Chapter 18 where repetition lives in the loop rather than in the plan.

The rejection message is what makes this work. `graph contains a cycle` teaches nothing. `cycle:
run_tests -> fix_failures -> run_tests; repetition belongs in an episode, not an edge` teaches the
model to emit the right shape next time, and the second message costs nothing to produce because the
traversal already has the path in its hand.

---

## 6. Runtime Sequence

The sequence below is the cold open executed correctly, compressed to five branches. The crash is at
the same point and the resume does the right thing for exactly one reason: nothing that mattered was
in the process that died.

```
                                                             TIME VIEW

  t   Worker A          Worker B          Durable store
  --  ---------------   ---------------   ---------------------------
  0   claim ready set                     resolver returns n1 (search)
  1   run n1                              n1: running, lease held
  2   complete n1 -------------------->   n1 done + child graph minted
                                          n2..n6 pending, join j1 open
                                          required=5, arrived=0
  3   claim ready set   claim ready set   both resolvers return
                                          {n2,n3,n4,n5,n6}
  4   claim n2,n3       claim n4,n5,n6    version CAS: no overlap (C17)
  5   run n2, n3        run n4, n5, n6
  6   complete n2 ------------------->    n2 done, j1.arrived = 1
  7                     complete n4 --->  n4 done, j1.arrived = 2
  8   complete n3 ------------------->    n3 done, j1.arrived = 3
  9   *** WORKER A NODE DRAINED ***
      n2, n3 already committed            j1.arrived = 3, durable
      no in-flight work lost but n-none
 10                     complete n5 --->  n5 done, j1.arrived = 4
 11                     complete n6 --->  n6 done, j1.arrived = 5
                                          policy ALL met
                                          << join.satisfied j1 >>
 12                     claim ready set   resolver returns n7 (open PR)
 13                     run n7
 14                     complete n7 --->  n7 done; graph terminal

  FAILURE BRANCH -- worker A dies at t=5, mid-flight on n2 and n3:

      leases on n2, n3 expire after the lease TTL (C17)
      the sweeper (C27) returns them to pending
      j1.arrived is still 1 -- neither ever ticked
      worker B's next resolver call returns {n2, n3}
      n2 and n3 re-run; identity check (C21) finds no prior effect
      the count is correct because it only ever counted commits

  Figure 24.4 -- One graph executed across two workers, with a drain at
                 t=9 and a lease expiry branch (D4 Sequence)
```

Three things in that trace are worth naming, because each is a design decision paying off rather
than an implementation detail.

**At t=3 both workers get the same ready set, and that is fine.** The resolver makes no attempt to
partition work. Two workers claiming the same node is resolved by the version compare at t=4, where
one write wins and the other returns "claimed by someone else" — which the loop treats as a normal,
uninteresting outcome and not an error. Any resolver that tried to hand out disjoint sets would need
to remember what it had handed out, and would be a cursor again.

**At t=9 the drain costs nothing.** Not because the drain was handled, but because by t=8 every
fact worth having was in a row. The worker held a lease and some in-memory state, and neither was
load-bearing. This is Chapter 21's "lose at most one in-flight step" in its concrete form: the run
lost zero steps because both of A's steps had already committed.

**In the failure branch, the count is right by construction.** `arrived` is 1, not 3, because it was
only ever incremented in the same transaction as a commit. There is no reconciliation pass, no
recount, no repair job. The number could not have drifted, because there was no moment at which the
completion and the count were separately observable.

---

## 7. State Management

A node has six states and a join has three. Both machines are small, and both have one illegal
transition that is worth writing on the wall.

```
                                                            STATE VIEW

   NODE

      {{ pending }}
           |  every predecessor terminal, join (if any) satisfied
           v
      {{ ready }}
           |  claim succeeds: lease acquired, version bumped (C17)
           v
      {{ claimed }}------------------+------------------+
           |                         |                  |
           | attempt succeeds        | attempt fails    | lease expires
           v                         v                  |
      {{ succeeded }}           {{ failed }}            |
           |                         |                  |
           |                         | attempts < cap   |
           |                         +------------------+
           |                         |                  |
           |                         | attempts = cap   v
           |                         v            {{ pending }}
           |                    (terminal)
           v
      (terminal)

      {{ skipped }}   entered from pending when a predecessor failed
                      and the join policy propagates; terminal;
                      counts as arrival at any downstream join

      ILLEGAL: {{ claimed }} -> {{ pending }} by any path except lease
      expiry. A worker may not "give a node back". It either commits an
      outcome or it stops existing, and the lease decides which.

   JOIN

      {{ open }} --- arrivals accumulate --->  {{ satisfied }}
           |                                        (terminal)
           | policy is ALL and an arrival is a
           | failure, or the parent run is cancelled
           v
      {{ abandoned }}   (terminal; successors become skipped)

      ILLEGAL: {{ satisfied }} -> {{ open }}. A join that has fired
      cannot un-fire, which is why `required` must be final before
      the first arrival (see 5.4).

  Figure 24.5 -- Node and join states (D6 State Diagram)
```

### 7.1 Why a worker may not release a node

The illegal transition on the node machine — `claimed` back to `pending` by voluntary action — is
the one that gets implemented by accident, usually in a shutdown handler that tries to be polite.
The reasoning is appealing: we are draining, we hold two nodes, we have not started them, let us
hand them back so someone else can pick them up sooner.

The problem is that "we have not started them" is a claim the process is not in a position to make
truthfully. It knows it has not *returned* from the tool call. It does not know whether the tool
call reached the other side. A polite release turns an ambiguous in-flight effect into a node that
is immediately re-claimable, which is the one thing the lease timeout exists to prevent — the
timeout is not slowness, it is the interval during which an unacknowledged effect is allowed to
settle.

Releasing is safe for a node whose tool is tagged pure, and the temptation is to allow it there.
That is a legitimate optimisation and it should be spelled `if node.effect == PURE` in one place,
with a comment pointing at this paragraph, rather than inferred from "we had not started yet".

### 7.2 Skipped is a success for counting purposes

A skipped node satisfies its successors. This surprises people and it is worth being explicit: a
successor's precondition is that its predecessors are *terminal*, not that they *succeeded*. If
skipping did not satisfy successors, a single skipped node would strand every node downstream of it
in `pending` forever, and the run would stall in the mode of §5.2 — healthy, motionless, unalarming.

The propagation rule is therefore: a node whose predecessor failed becomes `skipped`, and its own
successors then also become `skipped`, and the wave runs to the graph's terminal nodes, at which
point the run is complete with a failure. Every node has a terminal status, every join is resolved,
and the graph is a full account of what happened rather than a partial one with a hole in it.

---

## 8. Internal APIs

Four operations, one of which must be transactional. The ports are `typing.Protocol` definitions in
the kernel; every implementation detail below the signature belongs to an adapter.

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class TaskGraphStore(Protocol):
    """Durable storage for a minted plan's nodes, edges, and joins."""

    def mint(self, run_id: str, graph: "PlanGraph") -> str:
        """Validate and insert an entire graph in one transaction.

        Returns the plan_id. Raises GraphRejected with a machine-readable
        reason if the graph is cyclic or exceeds a structural cap. Never
        partially inserts: a caller that sees an exception knows nothing
        was written.
        """

    def ready_nodes(self, run_id: str, limit: int) -> Sequence["NodeRef"]:
        """Nodes whose predecessors are all terminal and whose joins are
        satisfied. Holds no state between calls. Two concurrent callers
        may receive overlapping sets; claim resolves the overlap.
        """

    def claim(self, node_id: str, worker_id: str, lease_s: int) -> "Claim | None":
        """Acquire an exclusive lease via version compare-and-set (C17).
        Returns None if another worker won, which is a normal outcome
        and not an error.
        """

    def complete(
        self,
        claim: "Claim",
        status: "NodeStatus",
        result_ref: str | None,
    ) -> "CompletionResult":
        """Write the terminal status, append the node-completed event to
        the outbox, and tick every join this node feeds -- in ONE
        transaction. Returns which joins became satisfied, so the caller
        can decide whether to poll again immediately rather than wait.

        This is the only method in the handbook whose docstring is
        allowed to shout. If these three writes are ever separated, see
        Chapter 24 section 5.2 for the two failure modes that result.
        """
```

Two notes on the shape.

`ready_nodes` takes a `limit` because an unbounded ready set on a 900-node graph would hand a single
worker more work than its lease budget can hold, and the surplus would sit claimed and idle while
other workers see an empty set. The limit is the worker's remaining lease capacity, not a constant.

`complete` returns which joins fired rather than emitting a callback. The caller then knows whether
new work became available and can poll immediately instead of waiting out a poll interval. This is
worth roughly one poll interval of latency per join in a deep graph, which on a graph of depth
twelve with a two-second poll is twenty-four seconds of pure waiting removed for a two-line change.

---

## 9. Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class NodeStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    CLAIMED = "claimed"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class JoinPolicy(str, Enum):
    ALL = "all"
    K_OF_N = "k_of_n"
    FIRST = "first"


@dataclass(frozen=True)
class PlanNode:
    node_id: str
    plan_id: str
    rank: int                  # presentational order only; never scheduling
    activity: str              # the tool or sub-run to invoke
    arguments: dict
    effect: str                # "pure" | "effectful", copied from registry
    identity_key: str          # C21 activity identity, computed at mint


@dataclass(frozen=True)
class PlanEdge:
    plan_id: str
    from_node: str
    to_node: str
    # No predicate field. See section 4.1.


@dataclass(frozen=True)
class PlanJoin:
    join_id: str
    plan_id: str
    target_node: str
    policy: JoinPolicy
    required: int              # final before the first arrival (5.4)
```

The schema is `snake_case` throughout, and three columns carry the chapter's argument.

`rank` exists so a person reading a plan sees it in the order the planner thought of it, and it is
never consulted by the resolver. Keeping it separate from the edges is what allows the presentation
to be stable while the execution order varies with worker availability.

`effect` is copied from the tool registry at mint time rather than read at execution time. A copy
can go stale; that is the intended trade. If a tool's effect tag changes after a plan is minted, the
plan executes under the tag it was validated against, and the `FIRST`-join restriction of §5.3
cannot be retroactively violated by a registry edit. Chapter 20 §5.5 lists the effect tag among the
things an evolution loop may not touch, and this is where that protection is actually cashed.

`identity_key` is computed once at mint and stored, not recomputed at execution. Chapter 21's whole
argument depends on the identity being stable across attempts, and a value recomputed on each
attempt from live inputs is not stable — it is a function of whatever the inputs happened to be that
time.

**Indexing.** The ready-set query is the hottest statement in the subsystem. It needs a partial index
on `plan_nodes (plan_id, status) WHERE status = 'pending'` and an index on `plan_edges (to_node)`.
Without the second, the `NOT EXISTS` degrades to a scan of the edge table per candidate node, and on
a 900-node graph the resolver becomes the slowest thing in the run — which presents as "the graph is
slow" and is diagnosed as a graph problem rather than a missing index roughly every time.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Planner | Graph store | Synchronous call, one transaction | Whole graph |
| Runtime loop | Resolver | Synchronous query | Ready set, bounded by lease capacity |
| Runtime loop | Graph store | Synchronous call, one transaction | Completion + join ticks + outbox row |
| Graph store | Event spine | Outbox row, same transaction | `node.completed`, `join.satisfied` |
| Graph store | Observability | Derived from events, never a direct call | Node durations, critical path |

The last row is a rule rather than an observation. The graph store does not call a metrics client.
Everything Chapter 34 wants to know about a graph is derivable from the events it already emits, and
adding a metrics call inside the completion transaction would put a network dependency inside the
one transaction this chapter has argued must never fail for an avoidable reason.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Worker dies holding a claimed node | Lease expiry (C17) | Sweeper returns node to `pending`; identity check (C21) prevents duplicate effect on re-run |
| Join tick committed separately from completion | None — this is the point | Not recoverable; prevented structurally by `complete()` being one transaction |
| Join `required` updated after first arrival | Assertion in the store; alert, not log | Reject the update; a join whose count changed mid-flight is unsound and the run must fail loudly |
| Cyclic graph proposed | Admission validator | Reject with the cycle path; planner replans (§5.5) |
| Graph exceeds width cap | Admission validator | Reject with the width and the cap; planner decomposes into sub-runs |
| Ready-set query slow | Query duration metric on the resolver | Almost always the missing `plan_edges (to_node)` index (§9) |
| Node stuck in `pending` with all predecessors terminal | Stall detector: oldest `pending` node age per run | Indicates an unsatisfied join; check `arrived` against `required` and the join's own status |
| All nodes terminal, run not complete | Same stall detector | An abandoned join with no propagation; the skip wave of §7.2 did not run |

The last two rows are the same underlying failure — a run that has stopped without failing — seen
from two ends. It deserves its own alert, distinct from any error rate, because its signature is the
absence of activity rather than the presence of errors. **Alert on the age of the oldest non-terminal
node in a run whose workers are healthy.** That single check catches every variant of the silent
stall in this chapter, and Chapter 22 argued for the identical check on the relay for the identical
reason.

---

## 12. Scalability

**The resolver is the scaling surface, not the executor.** Every worker polling every run's ready
set is an N-by-M query load, and the naive version has each of forty workers running a `NOT EXISTS`
over every active graph every two seconds. The fix is not a faster query; it is to have the
scheduler (Chapter 23) hand a worker a *run* to work on and have the worker resolve only that run's
graph.

**Width is bounded by admission, not by backpressure.** A 900-wide graph does not become safe
because the model semaphore will throttle it. It becomes 900 claimed nodes waiting on a semaphore,
each holding a lease, each renewing that lease, and the lease renewal traffic alone can exceed the
useful work. Cap width at mint.

**Depth sets the floor on latency.** The critical path — the longest chain of dependent nodes — is
the minimum wall-clock time regardless of worker count, and it is computable at mint from the graph
alone, before anything runs. Emitting it as a metric at mint time gives a predicted duration to
compare against the actual, and a systematic gap between them is the single most useful signal about
whether the planner's decompositions are honest.

**The cheapest optimisation is width, and it is usually available.** Planners emit chains out of
narrative habit — "first do this, then that" is how the decomposition was worded, and the edges get
written to match. Measuring the ratio of nodes to critical-path length across a corpus of real plans
gives the average width, and on most first implementations it is close to 1.0 with no dependency
actually requiring it. Chapter 26 addresses this at the source.

---

## 13. Production Engineering

### 13.1 The metrics that pay for themselves

Four, and only the first is obvious:

- **Graph width and depth at mint.** Emitted once per plan, free to compute, and the input to every
  capacity question in Chapter 33.
- **Predicted critical path versus actual duration.** The gap is a measure of planner honesty and of
  scheduler starvation, and separating those two causes is what the next metric is for.
- **Node queue time versus node run time.** A node that was ready for 90 seconds and ran for 4 is a
  scheduling problem. A node that was ready for 1 second and ran for 300 is a decomposition problem.
  Reporting only total duration merges two unrelated diagnoses into one unactionable number.
- **Oldest non-terminal node age, per run.** The stall detector of §11. Alert on it.

### 13.2 The review question

When someone proposes a change to this subsystem, one question separates the safe changes from the
dangerous ones: **does this add a write that could be committed apart from a node's completion?**

Metrics inside the transaction, a cache invalidation after it, a notification between the status
write and the join tick — every serious bug this chapter describes is an instance of that pattern.
The answer to a genuine need for one of those things is the outbox of Chapter 22: write the intent
in the same transaction, act on it afterwards.

### 13.3 Teaching this to a new engineer

The fastest path to understanding is to hand someone the schema and ask them to write the resolver
query, then ask what happens if two workers run it at the same instant. Nearly everyone's first
answer is to add a lock or a `FOR UPDATE SKIP LOCKED`. The second answer, after being told that
overlapping results are acceptable, is the one worth having — because it means they have understood
that the claim, not the query, is where exclusivity lives, and that is the whole design in one
sentence.

---

## 14. Relation to AHE

`[AHE §3.1]` treats a harness edit as a git-granularity change with file-level rollback. The task
graph is where that granularity is decided for the runs *inside* the harness: a node is the unit at
which work is retried, gated, attributed, and rolled back, and choosing the node boundary is
therefore choosing the rollback boundary. Nodes that bundle three tool calls to reduce row count are
cheaper to store and strictly worse to recover, and the trade is not close.

`[AHE App. C]` contract-first planning wants each unit of work to carry a checkable postcondition.
The graph is the natural carrier: a node's postcondition is checked by the completion writer before
the status is set to `succeeded`, which makes a failed contract a node failure rather than a silent
pass — and puts it inside the same transaction, so a contract check cannot pass while the node
records failure or the reverse.

`[INF]` The Evolve Agent of Chapter 20 runs its own trials as graphs, and this is where the width
cap earns its keep a second time: an evolution loop that discovers it can raise its score by
proposing wider graphs is optimising for the benchmark's wall clock rather than the harness's
quality. The width cap is a structural cap outside the workspace, which is the pattern §5.5 of
Chapter 20 collects.

---

## 15. Industry Perspective

**`[BP]` DAG schedulers have converged on this shape.** Airflow, Dagster, and the durable-execution
engines all represent runs as node rows with durable per-node status, all compute readiness by
query, and all put fan-in behind an explicit join object. The convergence is not fashion; it is what
survives contact with a machine that reboots.

**`[AHE]` Trials are graphs, and the trial is the unit of evidence.** The source's evolution loop
scores a harness variant by running a benchmark's tasks independently and aggregating — which is a
fan-out with a `K_OF_N`-shaped join over a fixed corpus. Nothing in that structure is specific to
evolution; it is the same subsystem this chapter describes, which is why Chapter 41 can build
evaluation infrastructure on it without inventing a second execution model.

**`[BP]` Build systems solved the pure case decades ago and it does not transfer whole.** The
dependency algebra transfers. Content-addressed skipping does not, because agent nodes are not pure
(§2.1). Teams that port a build system's mental model wholesale usually implement a result cache
first and then spend a quarter discovering which of their nodes were effectful.

**`[DAR §7.1]`** The same-transaction rule is stated once in the source and applies here in a form
it does not spell out: a join tick is a state change like any other, and the outbox argument covers
it without modification.

**`[INF]` The immutability requirement is stronger here than in most systems.** Airflow permits
dynamic task mapping that expands a DAG at run time. That is a reasonable choice for a system whose
runs are not audited step by step. It is not available to a system where a plan must be approvable
by a human before it executes (Chapter 30), because a plan that can grow after approval was never
what was approved. §5.4's sub-run is the price of keeping approval meaningful.

**`[FUT]` Speculative execution of low-confidence branches** — starting work that a `FIRST` join will
probably discard, to hide latency — is well understood in hardware and largely unexplored here. The
blocker is not the graph. It is that the effect tag makes most interesting branches ineligible to be
raced, and the population of pure-but-slow nodes is smaller than it first appears.

---

## 16. Key Takeaways

1. **A list conflates dependency with sequence.** The graph's job is to separate "must happen
   after" from "was written down after", and everything else follows from having done so.
2. **The graph is forced by durability, not by parallelism.** The derivation in §2.2 reaches a DAG
   through crash recovery; the speedup is change left over. A linear forty-node graph is still worth
   having.
3. **Do not store where the run has got to.** Ask. A ready set computed from durable rows has no
   crash semantics to get wrong, which is the same move Chapter 22 made with claims and Chapter 17
   made with versions.
4. **Fan-out is free; fan-in is the chapter.** A join is a durable counter, and its increment must
   commit in the same transaction as the completion that caused it. Both alternative orderings fail
   silently, in opposite directions.
5. **Overlapping ready sets are correct.** Exclusivity lives in the claim, never in the query. Any
   resolver that hands out disjoint work has grown a memory and become a cursor.
6. **A claimed node is never voluntarily released.** The lease timeout is not slowness; it is the
   interval during which an unacknowledged effect is allowed to settle. Only a pure node may be
   handed back, and only explicitly.
7. **Validate structure at mint, never at run time.** Cycles, width, and depth are all decidable
   before anything happens, and a rejection that names the cycle path teaches the planner something
   a boolean cannot.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Task graph** | A plan represented as nodes plus explicit dependency edges, so that independence is stated rather than inferred from position. | `[INF]` | Ch 26, Ch 32 |
| **Ready set** | The nodes whose predecessors are all terminal and whose joins are satisfied, computed by query and never stored. | `[INF]` | Ch 23, Ch 32 |
| **Fan-out** | A node with several outgoing edges, which requires no mechanism beyond the ready set being a set. | `[BP]` | Ch 29 |
| **Fan-in** | Several branches converging on one successor, which requires a durable counter and is where the subsystem's real difficulty lives. | `[INF]` | Ch 27 |
| **Durable join** | A row holding `required` and `arrived`, ticked in the same transaction as the completion that caused the arrival. | `[DAR]` | Ch 27, Ch 32 |
| **Join policy** | Whether a join fires on all branches, k of n, or the first, where only the last requires every feeding branch to be pure. | `[INF]` | Ch 28 |
| **Critical path** | The longest chain of dependent nodes, which is the floor on a run's wall-clock time regardless of worker count. | `[BP]` | Ch 33 |
| **Admission validation** | Checking acyclicity and structural caps once at mint time, so the executor never needs a cycle detector. | `[INF]` | Ch 26 |
| **Skip propagation** | A failed node marking its successors `skipped` so every node reaches a terminal status and no join waits forever. | `[INF]` | Ch 27 |
| **Sub-run** | A child plan minted by a completing node, used when the number of branches is unknown until run time, so the parent graph stays immutable. | `[INF]` | Ch 29, Ch 32 |
| **Presentational rank** | An ordering field kept for human reading and never consulted by the resolver, which is what lets display order stay stable while execution order varies. | `[INF]` | Ch 34 |

---

**Next:** Chapter 25 — *The World Model.* The runtime has now been given a structure for the work it
intends to do; this chapter asks what it believes about the environment that work will land in, how
those beliefs are acquired, and — the part almost nobody implements — how they are known to have
gone stale. It is also the most speculative chapter in this book, and it says so in its first
paragraph.
