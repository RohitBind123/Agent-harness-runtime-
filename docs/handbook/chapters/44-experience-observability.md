```
  Level 5 · Chapter 44
  EXPERIENCE OBSERVABILITY
  Requires   C11 The Context System, C16 The Observation System,
             C34 Observability, C37 Tenancy and Data Governance,
             C43 Component Observability
  Unlocks    C45 Decision Observability, C46 The Evolve Agent,
             C47 Attribution and Rollback
  Diagrams   Full (9)
```

# Chapter 44 — Experience Observability

---

## 1. Motivation

### 1.1 Cold open

A batch of two hundred Atlas tasks produces sixty-one failures and 9.4 million tokens of trajectory.
The distiller reads all of it and writes eleven thousand tokens of evidence.

Its overview names one dominant pattern, in thirty-four of the sixty-one: *the model finishes without
verifying its edits.* Every per-task analysis under that heading says the same thing in different
words. The reading is confident, the evidence is consistent, and the obvious fix is a sentence about
verifying before finishing.

An engineer opens three of the thirty-four trajectories by hand.

In all three, the test file the model would have needed to check was **deferred out of context** by
the budget. It was never in the window. The model did not skip verification; it verified what it
could see, and what it could see did not include the thing that mattered.

The distiller had summarised what the model *did* at every step — the calls, the arguments, the
results, the final state. It had never once recorded what the model *could see*. So a context gap
and a discipline failure produced identical summaries, and thirty-four of one had been reported as
thirty-four of the other.

The proposed fix was a sentence in the system prompt: the weakest component in the harness, and the
one measured below doing nothing at all.

A thousand-to-one reduction, and the column it dropped was the only one that told the two failures
apart.

### 1.2 In plain language

To improve a system you have to know what went wrong, and here the record of what went wrong is
enormous. A single batch of runs produces roughly ten million words of detail — far more than any
reader can hold at once, whether that reader is a person or a model.

So it has to be boiled down. That is not optional, and it is not free: boiling down means throwing
things away, and the whole question is what.

Two obvious answers are both wrong. Reading a sample misses anything that shows up faintly in many
places rather than obviously in one. Cutting each record short loses the tail, which is exactly where
failures live.

The answer that works is to summarise every failure the same way — the same fields, every time,
chosen so that what remains is enough to decide which part of the system is at fault — and to keep a
precise pointer back to the original for everything else. The summary is what gets read; the original
is what gets consulted when the summary raises a question.

The cold open is what happens when the fixed fields are the wrong fields. Everything was recorded,
nothing was broken, the summaries were accurate, and they described the wrong problem.

### 1.3 Why this chapter exists

Chapter 16 built the trajectory: what to capture, what to redact, and which runs to keep. Chapter 34
set retention. Chapter 43 built an action space with addresses to aim at.

Nothing so far turns ten million tokens into something a reader can hold.

`[AHE §3.2]` names the reduction and its ratio: roughly ten million tokens of raw rollout distilled
into roughly ten thousand tokens of navigable evidence, with the reader pulling only what it needs.
Chapter 11 §5.4 already showed the same technique at a different scale — skills as headers with
bodies on request — and observed that the identical mechanism working at both scales suggests it is
the general answer to a bounded window rather than an optimisation.

`[INF]` This chapter's contribution is the part the ratio hides. **Distillation is a routing
decision, not a summary.** Chapter 43 §5.3 built a chain of questions that decides which component
owns a failure; a field may be dropped only if losing it cannot change the answer to any of them.
That rule is derivable rather than a matter of taste, it produces a specific list, and the cold open
is what its absence costs.

Chapter 42 §4 measured why this chapter is where the effort goes: sixty-one percent of a re-fit is
finding the pattern. This is that step, mechanised.

### 1.4 What previous framings got wrong

**"Summarise the trajectories."** A summary is written for a reader who already knows what they are
looking for. A distiller does not — it runs before anyone has a theory of what went wrong, which is
what makes the fixed-field discipline of §5.2 necessary rather than bureaucratic.

**"Read a sample."** Chapter 42 §6.1's point, arriving where it does damage. The patterns a sampled
read misses are not a random subset; they are the *diffuse* ones — a defect that appears slightly in
nine task types and obviously in none — and those are the ones a benchmark aggregate also hides.

**"The model has a long context now, so feed it the traces."** A batch is 9.4 million tokens against
a window one or two orders of magnitude smaller, and the gap widens with batch size rather than
closing. `[INF]` More importantly, a reader with everything in context still has to find the pattern,
and every token of unstructured trajectory competes with the reasoning about it.

**"Distillation is lossy, so it is a compromise."** It is lossy only if the original is unreachable.
With a pointer back to the exact span, nothing is lost — it is deferred, which is Chapter 11's
technique applied one level up (§5.5).

**"The overview is the executive summary."** It is the opposite: the per-task analyses are the local
view, and the overview exists to hold what no single task shows. A pattern spanning nine tasks is
invisible in all nine of them (§5.4).

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Legal discovery.

A large case produces millions of pages, and nobody reads them. What happens instead is a pipeline
with exactly this chapter's shape. Paralegals work through the documents and produce structured
work-product: a chronology, per-issue summaries, and a hot-documents list. The lawyer reads the
work-product, not the documents. And every line of it carries a citation — a Bates number pointing at
one page of one document — so that when a summary raises a question, the original is one lookup away.

The proportions match too. Millions of pages become a few dozen pages that get read, and the
reduction is trusted because the citation makes it checkable rather than because the summariser is
trusted.

**Where it breaks**, in two ways that both bite.

Discovery has a **theory of the case**. The paralegal knows what the dispute is about and summarises
toward it. A distiller runs before anyone knows what went wrong in this batch — that is the thing it
is being run to find out — so it cannot summarise toward a theory. `[INF]` It has to summarise along
fixed dimensions chosen in advance, and choosing those dimensions correctly is the whole engineering
problem. The cold open is a set of dimensions that were reasonable and wrong.

And discovery is **adversarial**. An opposing party is looking for what you left out, and there are
sanctions for omission. Nothing checks a distiller. A field it quietly stops emitting produces
summaries that are shorter, cleaner, and still perfectly plausible, and the only symptom is that
downstream conclusions drift toward whatever the remaining fields can express. `[INF]` In the cold
open that drift had a direction: toward the system prompt, because a summary of what the model *did*
can only ever describe behaviour, and behaviour problems route to instructions.

### 2.2 Why the evidence corpus must exist

```
  (1) The loop must decide WHAT to change, which requires
      evidence about what went wrong.

  (2) That evidence is trajectories. One batch is ~9.4M tokens
      (C20 sec 10), and batch size grows with rollout count.

  (3) No reader holds that. A window is 10^5 to 10^6 tokens; the
      batch is 10^7. The gap WIDENS as the benchmark grows.

  (4) So the material must be reduced, and reduction is lossy.
      The only real question is what gets lost.

  (5) SAMPLING loses diffuse patterns -- the defect appearing
      slightly in nine task types and obviously in none. Those
      are precisely the ones no other instrument finds either
      (C39's aggregate hides them too).

  (6) TRUNCATION loses the tail, and the tail is where failures
      live. C16 sec 5.5 already made that argument for retention;
      it applies again one layer up.

  (7) So the reduction must be STRUCTURAL: every failure
      summarised along the SAME fixed fields.

  (8) Which fields? Not a matter of taste. C43 sec 5.3 routes a
      failure to a component by asking a fixed chain of
      questions. A field may be dropped only if losing it cannot
      change the answer to any of them (5.3). That is the cold
      open, stated as a rule.

  (9) And the reduction must be NAVIGABLE rather than final,
      because the distiller does not know which failures will
      matter. Every claim carries a pointer; the overview is
      pushed, the detail is pulled (C11 sec 5.4).

  Structural summary + pointer + navigation. 10^7 tokens down to
  10^4, with the 10^7 still reachable.
```

Step (8) is the chapter's load-bearing move. `[INF]` Every other treatment of this problem picks
summary fields by judgment, which produces fields that are reasonable, stable, and unfalsifiable.
Deriving them from the routing chain makes the choice checkable: for any proposed field, ask which
routing question becomes unanswerable without it, and if the answer is none, it is optional.

### 2.3 Three grains, three budgets

The corpus is not one artefact. It is three, at three scales, and confusing them is how teams build
something that is either unreadable or useless.

| Grain | What it is | Size | Read |
|---|---|---|---|
| **Trajectory** | One run, every span, what the model could see at each | ~150k tokens | Never whole; consulted by pointer |
| **Per-task analysis** | One failing task, fixed fields | ~300–600 tokens | All of them, always |
| **Benchmark-level overview** | The batch, patterns across tasks | ~2–4k tokens | First, and often only |

`[AHE §3.2]` The middle and top rows are the source's structure. `[INF]` The proportions are what
make it work: sixty-one failures at four hundred tokens each is twenty-four thousand tokens, which is
readable but not comfortably, and the overview exists so that most iterations never need to read them
all.

Note what the top row is *not*. It is not an executive summary of the analyses. It is the only place
a cross-task pattern can exist, because a pattern spanning nine tasks appears in none of the nine
strongly enough to name (§5.4).

### 2.4 The mental model to carry

> **Distillation is a routing decision, not a summary.** Keep every field that could change which
> component a failure belongs to; point at everything else. A summary that describes only what the
> model *did* can only ever blame the model.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   [[ trace store (C16) ]]     one batch: 200 tasks x k rollouts
      outcome-weighted            ~9.4M tokens of trajectory
      retention (C34 sec 5.5)     structural + verbatim (C37 sec 5.4)
              |
              | (1) the failing runs; always-keep classes are
              |     already retained at 100%
              v
   +--------------------------------------------------------------+
   |                       THE DISTILLER                          |
   |                                                              |
   |   per failing task   read the trajectory, write ONE          |
   |                      analysis with FIXED fields (5.2)        |
   |                                                              |
   |   across the batch   write ONE overview naming patterns      |
   |                      that no single task shows (5.4)         |
   +---------------------------+----------------------------------+
                               | (2) roughly 1000 : 1
                               v
   +--------------------------------------------------------------+
   |             THE EVIDENCE CORPUS  (a directory)               |
   |                                                              |
   |     overview.md             ~2-4k tokens    READ FIRST       |
   |     analyses/task_112.md    ~400 tokens     read as needed   |
   |     analyses/task_203.md                                     |
   |     ...                     ~11k tokens total                |
   |                                                              |
   |   every claim carries a POINTER to the span it came from:    |
   |   nothing is lost, only deferred (5.5)                       |
   +------+------------------------------------------+------------+
          | (3) pushed                               | (A) pulled
          v                                          :
   +-------------------------+                       :
   |  EVOLVE AGENT (C46)     |.......................:
   |   routes each pattern   |
   |   to a component (C43)  |    (A) the original span, on demand
   +-----------+-------------+        -- progressive disclosure
               | (4)                     (C11 sec 5.4)
               v
   +-------------------------+
   |  CHANGE MANIFEST (C45)  |
   |   failure_evidence      |
   |   cites pointers, not   |
   |   prose                 |
   +-------------------------+

  Figure 44.1 -- Ten million tokens to ten thousand, and back
                 (D1 High-Level Architecture)

  (1) C16 and C34 decided WHICH runs exist here; this chapter
      decides what is made of them
  (2) the ratio is a budget, not an outcome (5.1)
  (3) the corpus is what C46 reads; it never reads a trajectory
      it was not pointed at
  (4) a manifest entry cites a pointer, which is what makes
      C47's attribution checkable against evidence rather than
      against a recollection
  (A) the side channel that makes the reduction lossless in
      practice: the original is one lookup away
```

### 3.1 The corpus is read by a machine, and that changes the design

`[INF]` Every artefact in Figure 44.1 could be produced for a human debugging a bad week, and some
teams do build exactly this. Three requirements separate the version that serves an evolution loop.

**Fixed fields, not prose.** A human reader tolerates variation and fills gaps from context.
Chapter 46 routes on fields, so a field that is present in some analyses and absent in others
produces routing that silently varies by task.

**Pointers, not references.** "See the shell output around step 7" is fine for a colleague. A pointer
that resolves — trace id, span id, byte range — is what lets Chapter 45's manifest cite evidence and
Chapter 47 re-check the citation a week later.

**Completeness over concision.** A human skims and stops when satisfied. `[INF]` The whole argument
for automating this (Chapter 42 §4.2) was that a machine can read *all* of it, so a distiller that
optimises for brevity by dropping the long tail of one-off failures has thrown away the only
advantage the arrangement had.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                      THE DISTILLER                             |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Selector               |  |   Per-task analyser       |   |
   |  |                          |  |                           |   |
   |  |  which runs enter the    |  |  one trajectory in, one   |   |
   |  |  corpus this iteration   |  |  FIXED-FIELD analysis out |   |
   |  |                          |  |                           |   |
   |  |  failures, rejections,   |  |  reads the STRUCTURAL     |   |
   |  |  retry loops, the        |  |  partition first; pulls   |   |
   |  |  expensive tail, plus a  |  |  verbatim only where a    |   |
   |  |  NONZERO sample of clean |  |  field needs it           |   |
   |  |  successes (C34 5.5)     |  |  (C37 sec 5.4)            |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Pattern finder         |  |   Corpus writer           |   |
   |  |                          |  |                           |   |
   |  |  reads ALL the analyses  |  |  writes the directory:    |   |
   |  |  at once; groups by      |  |  overview + analyses      |   |
   |  |  field, not by prose     |  |                           |   |
   |  |                          |  |  stamps the HARNESS       |   |
   |  |  this is the only place  |  |  VERSION it describes --  |   |
   |  |  a DIFFUSE pattern can   |  |  a corpus goes stale the  |   |
   |  |  become visible (5.4)    |  |  moment an edit lands (7) |   |
   |  +--------------------------+  +---------------------------+   |
   +----------------------------------------------------------------+

  Figure 44.2 -- Inside the distiller (D2 Low-Level Architecture)
```

### 4.1 The selector keeps clean successes, and the reason is not obvious

Chapter 34 §5.5 set retention with an always-keep allowlist plus a low uniform rate over clean
successes, and noted the rate must be nonzero because a corpus of only failures teaches a grader the
wrong prior.

`[INF]` The same rule applies here for a second, independent reason. A distiller looking only at
failures reports every property those failures share, and many of those properties are shared by the
successes too — a tool that is called in an unusual order, a step that always takes four attempts, a
verbose output format. Without a contrast set, the pattern finder cannot tell *characteristic of
failure* from *characteristic of the workload*, and it will name the second as a cause.

`[BP]` Ten to twenty percent of the corpus as clean successes is enough to give the pattern finder a
contrast, and it is cheap because those analyses are short — a task that worked has little to say.

### 4.2 Group by field, never by prose

The pattern finder's one design rule. `[INF]` Grouping summaries by textual similarity produces
clusters of *phrasing*, which is a property of the analyser rather than of the system, and it is how
the cold open's thirty-four analyses ended up in one confident group: they said the same thing
because the same fields were missing from all of them.

Grouping by field value — same failing step kind, same tool, same rejection type, same deferred
source — produces clusters that mean something, and the clusters that are interesting are the ones
that *cut across* prose similarity.

```
                                                            LAYER VIEW

   NAMED INTERNALS AND THEIR INTERFACES

   +-------------------+   select(batch_id)      +------------------+
   |  Selector         |<------------------------|  Distiller       |
   |                   |------------------------>|  facade          |
   |  C34's allowlist  |   tuple[RunId, ...]     |                  |
   |  + a nonzero      |                         |  one call per    |
   |  success sample   |                         |  iteration       |
   +-------------------+                         +---+----------+---+
                                                     |          |
   +-------------------+   analyse(run_id)           |          |
   |  Per-task         |<----------------------------+          |
   |  analyser         |---------------------------->|          |
   |                   |   TaskAnalysis                        |
   |  FIXED fields;    |   (fields derived from C43's          |
   |  undroppable set  |    routing chain -- 5.2)              |
   |  enforced here    |                                       |
   +--------+----------+                                       |
            |  reads                                           |
            v                                                  |
   +--------+----------+                                       |
   | [[ trace store ]] |   structural partition by default;    |
   |   (C16)           |   verbatim only on demand (5.6)       |
   +-------------------+                                       |
                                                               |
   +-------------------+   find(analyses)                      |
   |  Pattern finder   |<--------------------------------------+
   |                   |-------------------------------------->|
   |  groups by FIELD  |   tuple[Pattern, ...]                 |
   |  (4.2)            |                                       |
   +-------------------+                                       |
                                                               |
   +-------------------+   write(analyses, patterns, harness)  |
   |  Corpus writer    |<--------------------------------------+
   |                   |-------------------------------------->
   |  stamps the       |   CorpusHandle
   |  harness version  |
   +-------------------+   consumed by: C46 (reads), C45
                           (cites pointers), C47 (re-checks)

   NOT an interface here: anything that WRITES to the trace
   store. Distillation is strictly a read; C16 owns capture, and
   a distiller that could annotate traces would be editing its
   own evidence.

  Figure 44.3 -- Distiller internals (D3 Component Diagram)
```

---

## 5. Distillation, Navigation, and What Cannot Be Dropped

### 5.1 The ratio is a budget

```
                                                            LAYER VIEW

   ONE BATCH, REDUCED                              [AHE sec 3.2]

   raw trajectories        ====>  ~9.4M tokens   200 tasks x k
                                                  rollouts, failing
                                                  runs only

   structural partition    ====>  ~1.2M tokens   calls, order,
   read by default                                verdicts, cost,
   (C37 sec 5.4)                                  context accounting
                                                  -- ~13% of the raw

   verbatim, pulled        ====>  ~90k tokens    file bodies, model
   only where a field                             output, shell
   needs it                                       output: fetched per
                                                  field, not per run

   per-task analyses       ====>  ~24k tokens    61 failures plus a
                                                  success sample, at
                                                  ~400 tokens each

   the overview            ====>  ~3k tokens     the only artefact
                                                  read every time

   -----------------------------------------------------------------
   THE CORPUS               ~11-27k tokens        roughly 1000 : 1

   READ THE SECOND ROW AGAIN. Most of the reduction happens before
   the distiller summarises anything, because the structural
   partition is a projection rather than a summary -- lossless for
   what it keeps, and the half that C37 allows to be retained for
   years.

   AND THE RATIO IS A BUDGET, NOT AN OUTCOME. A distiller told to
   produce 10k tokens from a batch twice the size will drop
   something, and it will drop the long tail of one-off failures --
   which is the population that has not been fixed yet.

  Figure 44.4 -- Where the thousand-to-one actually comes from
                 (D7 Data Flow)
```

`[INF]` The last note is the one to design against. The overview's size can be fixed; the analyses'
total cannot, because it scales with the failure count and every dropped failure is a defect nobody
will hear about again. `[BP]` Budget the overview and let the analyses grow, then measure the
analyses' total as a signal — a corpus growing faster than the failure count means the analyser is
becoming verbose, and one growing slower means it is dropping tasks.

### 5.2 The fields are derived, not chosen

The per-task analysis has fixed fields, and §2.2 step (8) says where they come from: Chapter 43
§5.3's routing chain asks a fixed sequence of questions to decide which component owns a failure, so
the analysis must answer all of them.

| Routing question (C43 §5.3) | Field the analysis must carry |
|---|---|
| Did the model get what it asked for? | What was in context, and what was **deferred, dropped, or condensed** (Ch 11) |
| Is the result itself wrong? | The tool result verbatim, or a pointer to it, plus the verdict |
| Wrong verb or wrong arguments? | The tool descriptions in force (Ch 15), and the call as issued |
| Only visible across steps? | The step sequence, with repeats and retry loops marked |
| A long procedure done badly? | Where the procedure diverged, by step |
| A hard-won fact the model lacked? | Which memory entries were loaded, and which were not |
| Parent's context flooding? | Sub-agent boundaries and what crossed them |
| — falls through to the default owner — | Nothing; this is the branch that needs no evidence, which is exactly why it is over-used |

`[INF]` Read the first row against the cold open. The routing chain's *first* question cannot be
answered without the context accounting, so a distiller that omits it does not merely lose detail —
it makes the whole chain start at question two, where the earliest available answer is about
behaviour. Every failure then routes to a behavioural cause, which is the drift §2.1 named.

The last row is worth its own note. `[INF]` The default owner is the only destination that requires
no evidence to reach, so it is the cheapest branch for an under-informed distiller to make available.
Chapter 43 §5.4 predicted that unclassified failures decay into instruction text; this is the
mechanism by which a distillation defect causes it.

### 5.3 The undroppable set, and the rule that generates it

> **A field may be summarised away only if losing it cannot change which component the failure routes
> to.**

`[INF]` That is the whole discipline, and it is checkable rather than a matter of taste. For any
proposed omission, name the routing question that becomes unanswerable. If none does, drop it.

Applied, it produces a specific and short list:

- **Context accounting** — included, deferred, dropped, condensed (Chapter 11). The cold open.
- **Tool descriptions in force** — as the model read them (Chapter 15). Without these, an interface
  defect is indistinguishable from a reasoning failure, which is Chapter 16 §5.1's argument arriving
  at the summary layer.
- **Rejections** — plan and schema (Chapters 10 and 14). Tiny, rare, and direct evidence that a
  component produced something invalid.
- **The harness version** — because the corpus describes one (§7).
- **The failing step, not only the failing run.** A run-level verdict routes nowhere; the routing
  chain is about a step.
- **Retry-loop signatures** (Chapter 15) — a guaranteed interface defect, and the cheapest one to
  detect.

`[BP]` Write the list as a schema the analyser cannot emit without, rather than as guidance. A
missing field should fail the analysis, because the alternative failure mode — a field quietly absent
from some analyses — produces routing that varies by task and no error anywhere.

### 5.4 The overview holds what no single task shows

The per-task analyses are local by construction, and some defects are not local.

`[INF]` A tool description that misleads slightly in nine task types and obviously in none produces
nine analyses that each name something else as the primary cause — because in each individual task,
something else *is* the primary cause. The pattern exists only in the set. This is the **diffuse
pattern**, and it is invisible to every other instrument in the book: it is inside the noise floor
per slice (Chapter 41 §4.1), diluted in the aggregate (Chapter 39 §6), and absent from any sample
(Chapter 42 §6.1).

The overview is the only place it can be found, and finding it requires reading all the analyses at
once rather than in sequence. `[INF]` That is the second structural argument for automating this
step, and it is different from the volume argument: a person reading sixty-one analyses over two days
has the same difficulty with diffuse patterns as a person reading sixty-one trajectories, because
neither holds all of them simultaneously.

`[BP]` The overview's useful content is a small number of things, and none of them is a summary:

- Patterns grouped by field value, with counts and the task ids in each group.
- **What is absent.** A routing branch that never fires across sixty-one failures is either a branch
  nobody needs or a field nobody is emitting, and the two look identical from inside.
- The contrast against the clean-success sample (§4.1).
- Anything that changed since the previous corpus — new patterns, and patterns that stopped
  appearing, which is the earliest signal that a previous edit worked.

### 5.5 The corpus is a file environment, not a document

```
                                                             TIME VIEW

  How a reader descends. Nothing is pushed except the overview.

     start
       |
       v
  +----------------------------+
  |  read overview.md   ~3k    |   ALWAYS. This is the only
  +-------------+--------------+   mandatory read.
                |
                v
             /      \   no      +----------------------------+
            / pattern \-------->| stop. Record E2: nothing   |
            \  worth  /         | new this iteration (C20)   |
             \ acting/          +----------------------------+
              \  on?/
                | yes
                v
  +----------------------------+
  |  read the analyses in that |   ~400 tokens each; 4-12 of
  |  pattern's task id list    |   them, not all 61
  +-------------+--------------+
                |
                v
             /      \   yes     +----------------------------+
            / fields  \-------->| ROUTE (C43 sec 5.3) and    |
            \ answer  /         | write the manifest entry   |
             \ the   /          | (C45), citing the pointers |
              \chain/           +----------------------------+
                | no
                v
  +----------------------------+
  |  FOLLOW A POINTER          |   trace id + span id + range.
  |  pull the original span    |   The expensive read, and the
  |  from the trace store      |   one that makes the whole
  +-------------+--------------+   reduction lossless
                |
                v
             /      \   no      +----------------------------+
            / enough  \-------->| E3: the field set is       |
            \  now?   /         | inadequate. Fix the        |
             \       /          | ANALYSER, not this entry   |
              \     /           | (5.3)                      |
                | yes
                v
          route and write

  A reader that follows pointers on most patterns is telling you
  the fixed fields are wrong. That rate is a health metric (13.1).

  Figure 44.5 -- Progressive disclosure over the corpus
                 (D8 Control Flow)
```

`[AHE §3.2]` The technique is the source's, at the source's scale. `[INF]` What the figure adds is
the exit at the bottom: a pointer-follow is not a normal part of reading, it is a *signal*. Chapter
11's progressive disclosure over skills has the same property and nobody measures it there either —
a skill whose body is pulled every time should have been resident.

### 5.6 Learn from the structural partition

Chapter 37 §5.4 split the trace store by classification: structural material — which tools were
called, in what order, with what verdicts, at what cost — is small, low-risk, and retainable for
years; verbatim content is large, high-risk, and retainable for weeks.

`[BP]` The distiller reads the structural partition by default and pulls verbatim only where a field
in §5.3 requires it. Three things follow, and the third is the one that matters most:

- **Most of the reduction is free.** Figure 44.4's second row: the structural partition is a
  projection rather than a summary, so it is lossless for what it keeps.
- **The corpus itself is mostly structural**, which means it inherits the long retention window and
  can be compared across months — which Chapter 47 needs and which verbatim material could never
  support.
- **The loop's exposure is bounded by design rather than by policy.** `[INF]` An automated reader with
  standing access to the most sensitive store in the architecture (Chapter 16 §5.6) is a governance
  problem Chapter 49 has to solve. Reading structurally by default makes the default access narrow,
  so the audit surface is the *exceptions* rather than everything.

### 5.7 Where this still fails

Two limits, stated because the chapter is otherwise a success story.

**Sub-agents.** Chapter 43 §12 flagged this and it lands here. A sub-agent's failures arrive at the
parent already summarised by the sub-agent, so the distiller is summarising a summary and the routing
chain runs against second-hand evidence. `[INF]` The partial answer is to distil sub-agent
trajectories as first-class tasks with their own analyses, linked to the parent's; the unsolved part
is that the parent's *decision to delegate* is itself a step whose evidence lives in both places.
Chapter 19's trade — isolation bought with attribution — is not repealed by better tooling.

**A pattern that has no field.** `[INF]` The routing chain is finite, so a failure mode nobody
anticipated has no field to be visible in, and it will be summarised as whichever nearby field fits.
The detector is §5.4's absence check plus a rising rate of default-owner routing, and the recovery is
to add a field and re-distil — which is possible only because the trajectories are still there.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  One iteration's distillation, after attribution (C20 sec 4.1).

  t     step                          result
  ----  ----------------------------  ----------------------------
  0     benchmark completes on
        harness v_n; 200 tasks,
        61 failures, 9.4M tokens
  1     ATTRIBUTION has already run
        and rolled back chg-2, so
        the corpus will not contain
        failures caused by a known-
        bad edit (C20 sec 4.1)
  2     selector: 61 failures + 14
        clean successes as contrast
        (4.1)
  3     per-task analyser, 75 runs,
        structural partition first    ~1.2M tokens read
  4     verbatim pulled for 23 of
        the 75, where a field
        required it (5.6)             ~90k tokens
  5     75 analyses written, fixed
        fields, every claim carrying
        a pointer                     ~24k tokens
  6     pattern finder, grouping by
        FIELD across all 75 (4.2)     three patterns:
                                        P1 deferred-source, 34
                                        P2 empty-result, 12
                                        P3 long-tail, 29 singles
  7     overview written, stamped
        with harness v_n              ~3k tokens
  8     C46 reads overview only,
        acts on P1, follows two
        pointers (5.5)
  9     manifest entry cites
        span ids, not prose (C45)

  ELAPSED: minutes, and a fraction of one rollout's cost
  (C20 sec 12.1). Distillation is the cheap step; the benchmark
  that produced its input was not.

  FAILURE BRANCH -- the cold open: no context accounting field

    t=5   75 analyses, all describing what the model DID
    t=6   P1 is instead "insufficient verification", 34 tasks --
          same tasks, different name, and the name determines
          the routing
    t=8   routes to the default owner; a sentence is added to
          the system prompt
    t=n+1 measured: inside the floor. Verdict ROLLBACK_AND_PIVOT
    -- and the pivot is to a DIFFERENT root cause for the same
       34 tasks, because the evidence still cannot express the
       real one. The loop will circle this for as long as the
       field is missing, and every iteration will look like
       honest work.

  FAILURE BRANCH -- distillation before attribution

    t=1   skipped; chg-2 is still in place
    t=6   P2 has 19 members instead of 12, seven of them caused
          by chg-2
    t=8   the loop diagnoses its own damage as a new defect and
          proposes a fix for it
    -- C20 sec 4.1's ordering, and the reason it reads backwards
       until you see this.

  Figure 44.6 -- One batch, distilled (D4 Sequence)
```

### 6.1 The first failure branch circles rather than stops

The property worth extracting: a missing field does not produce a wrong answer once. It produces a
sequence of wrong answers that each look like progress.

`[INF]` The loop proposes, measures, fails to see an effect, pivots to a different root cause for the
same tasks, and repeats — and every artefact it emits is well-formed. The manifest fills with honest
entries, the verdicts are correct, the rollbacks work. Chapter 43 §5.4's counter is the detector that
fires here: repeated routing to the default owner for one pattern is a routing failure, and this
chapter adds the second cause of it. The first was that no component owned the failure; the second is
that no field could express it.

```
                                                             TIME VIEW

  The read cycle, once per iteration.

        +-------------------------------------------------+
        |                                                 |
        v                                                 |
   +----+------------------+                              |
   | read overview.md      |                              |
   +----+------------------+                              |
        |                                                 |
        v                                                 |
      /   \  none                                         |
     /new   \ ---------------------------> E1 converged   |
     \pattern/                                for this    |
      \  ?  /                                 benchmark   |
        | yes                                             |
        v                                                 |
   +----+------------------+                              |
   | read that pattern's   |                              |
   | analyses              |                              |
   +----+------------------+                              |
        |                                                 |
        v                                                 |
      /   \  no                                           |
     /fields \ -------> follow pointers ---+              |
     \answer /                             |              |
      \chain/  <----------------------------+             |
        | yes                                             |
        v                                                 |
      /   \  yes                                          |
     /third  \ --------------------------> E2 the FIELD   |
     \ pointer/                               set is      |
      \follow/                                inadequate  |
        | no                                  (5.3)       |
        v                                                 |
   +----+------------------+                              |
   | route (C43) + manifest|                              |
   +----+------------------+                              |
        |                                                 |
        v                                                 |
      /   \  yes                                          |
     /corpus \ -------------------------> E3 STOP. An     |
     \ stale? /                              edit landed; |
      \      /                               re-distil    |
        | no                                  (7)         |
        +-------------------------------------------------+

  Exits:
    E1  no new pattern -- converged for this benchmark, which is
        a statement about the benchmark and not about the harness
    E2  three pointer-follows on one pattern means the fixed
        fields cannot express it; fix the ANALYSER
    E3  the corpus describes harness v_n and the workspace is now
        v_n+1. Everything after this point is about a system that
        no longer exists (7.1)

  Figure 44.7 -- Reading the corpus (D5 Runtime Loop)
```

---

## 7. State Management

```
                                                            STATE VIEW

   AN EVIDENCE CORPUS is bound to one harness version. That
   binding is the whole of this section.

      {{ absent }}
          |  a batch completes and attribution has run
          v
      {{ distilling }}
          |  analyses written, then the overview
          v
      {{ current }}     describes harness v_n, which IS the
          |             workspace right now
          |
          |  an edit lands in the workspace
          v
      {{ stale }}       describes v_n; the workspace is v_n+1
          |
          |  the next benchmark completes
          v
      {{ superseded }}  kept: C47 compares corpora across
                        iterations to see a pattern disappear

      ILLEGAL, and all three have happened:

        * reading {{ stale }} as {{ current }}. The loop
          re-diagnoses a failure its own last edit already
          fixed, and the manifest entry looks identical to a
          good one.

        * distilling before attributing. The corpus then
          contains failures caused by the previous iteration's
          bad edits, and they are diagnosed as new defects
          (C20 sec 4.1, and figure 44.6's second branch).

        * deleting {{ superseded }} corpora. They are small,
          structural, and the only record of what the evidence
          looked like BEFORE an edit -- which is what makes a
          disappearance measurable (5.4).

  Figure 44.8 -- Corpus states (D6 State Diagram)
```

### 7.1 Staleness has no symptom, and the stamp is the whole fix

`[INF]` A stale corpus reads exactly like a current one. The analyses are well-formed, the patterns
are real, the pointers resolve — and every one of them describes a system that has since changed.

The fix is four bytes: the corpus writer stamps the harness version it describes, and the reader
refuses when that version is not the workspace's. `[BP]` Refuse rather than warn, for the same reason
Chapter 41 §8 raises on a stale noise floor: a warning about a document that reads correctly is a
warning nobody acts on.

This is the same shape as Chapter 42 §7.1's fit state and Chapter 41 §7.2's cached floor — a derived
artefact that is expensive to rebuild, correct-looking when stale, and invalidated by a discrete
recorded event. `[INF]` Three chapters have now arrived at the same pattern independently, which
suggests it is worth naming as a class: **an expensive derivation of a versioned thing must carry the
version it was derived from, or it will be read after the thing changes.**

### 7.2 Superseded corpora are the disappearance record

Keeping old corpora looks like hoarding and is not. `[INF]` The evidence that an edit worked is not
only that the score moved — it is that the pattern the edit targeted is *absent* from the next
corpus, in the tasks it was predicted to fix. Chapter 47's attribution intersects predicted task ids
with observed deltas; comparing corpora adds a second, independent check that costs nothing because
the corpora are small and structural.

`[BP]` A pattern that vanishes from the corpus while the score does not move is the most informative
result available: the edit changed the mechanism and something else absorbed the gain, which is a
Chapter 43 §5.2 overlap and would otherwise be invisible.

---

## 8. Internal APIs

```python
from typing import Protocol, Sequence


class Distiller(Protocol):
    """Ten million tokens in, ten thousand out, with every claim
    pointing back at the span it came from."""

    async def distil(
        self,
        batch_id: str,
        harness_version: str,
        attribution_complete: bool,
    ) -> "CorpusHandle":
        """Raises when attribution_complete is False.

        The parameter exists to make C20 section 4.1's ordering
        structural rather than procedural: distilling first means
        the corpus contains failures caused by the previous
        iteration's bad edits, and they are then diagnosed as new
        defects. A comment could not enforce that; a required
        argument can.
        """


class PerTaskAnalyser(Protocol):

    async def analyse(self, run_id: str) -> "TaskAnalysis":
        """One trajectory in, one fixed-field analysis out.

        Reads the STRUCTURAL partition by default and pulls
        verbatim only where a field requires it (C37 sec 5.4).
        That is most of the reduction and all of the exposure
        control.

        Raises on a missing undroppable field (5.3). A field
        quietly absent from some analyses produces routing that
        varies by task, with no error anywhere.
        """


class EvidenceCorpus(Protocol):
    """A directory, read progressively. The overview is pushed;
    everything else is pulled (5.5)."""

    def overview(self) -> str:
        """The only mandatory read, and the only place a diffuse
        pattern can be seen (5.4)."""

    def analyses_for(self, pattern_id: str) -> Sequence["TaskAnalysis"]:
        ...

    async def follow(self, pointer: "EvidencePointer") -> str:
        """Pull the original span. The expensive read, and what
        makes the reduction lossless rather than lossy.

        The RATE of these calls is a health metric: a reader
        following pointers on most patterns is reporting that the
        fixed field set is wrong (13.1).
        """

    def describes(self) -> str:
        """The harness version this corpus was built from.

        Callers compare it against the workspace and refuse when
        it differs. A stale corpus reads exactly like a current
        one (7.1).
        """
```

`Distiller.distil` taking `attribution_complete` as a required argument rather than checking a flag
internally is the signature carrying Chapter 20 §4.1. `[INF]` The phase ordering is the kind of rule
that is obeyed for six months and then quietly broken by someone adding a convenience path, and a
parameter that must be supplied is the cheapest structural defence available.

`EvidenceCorpus.follow` being the only async method on an otherwise synchronous interface is
deliberate signalling. Everything the corpus holds is cheap and local; the one operation that reaches
the trace store is the one that costs, and an interface that hid the difference would encourage
reading the corpus the way one reads a document.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class EvidencePointer:
    """A citation that resolves. Not 'see the shell output around
    step 7' (3.1)."""
    trace_id: str
    span_id: str
    byte_range: tuple[int, int] | None
    partition: str                  # "structural" or "verbatim"


@dataclass(frozen=True)
class TaskAnalysis:
    """Fixed fields, derived from C43's routing chain (5.2).
    Every field here answers one routing question; a field that
    answers none does not belong."""
    task_id: str
    run_id: str
    failing_step: int               # the STEP, never only the run
    context_included: tuple[str, ...]
    context_deferred: tuple[str, ...]   # the cold open
    context_dropped: tuple[str, ...]
    tool_descriptions_in_force: tuple[str, ...]
    call_as_issued: str
    result_pointer: EvidencePointer
    rejections: tuple[str, ...]     # plan, schema -- tiny and rare
    retry_loop_len: int             # C15: a guaranteed ACI defect
    memory_entries_loaded: tuple[str, ...]
    sub_agent_boundary: str | None  # 5.7's unsolved half
    verdict: str
    evidence: tuple[EvidencePointer, ...]


@dataclass(frozen=True)
class Pattern:
    """Grouped by FIELD VALUE, never by prose similarity (4.2)."""
    pattern_id: str
    grouping_field: str             # which field the group shares
    grouping_value: str
    task_ids: tuple[str, ...]
    is_diffuse: bool                # weak in many, strong in none
    contrast_rate: float            # how often the clean-success
                                    # sample shows it too (4.1)


@dataclass(frozen=True)
class CorpusHandle:
    corpus_id: str
    describes_harness: str          # the stamp; the whole of 7.1
    batch_id: str
    total_tokens: int               # a budget to watch, not a
                                    # target to hit (5.1)
    patterns: tuple[Pattern, ...]
    absent_branches: tuple[str, ...]   # routing branches that
                                       # never fired (5.4)
```

`Pattern.contrast_rate` is the field that stops the pattern finder naming a property of the workload
as a cause. `[INF]` A pattern present in sixty percent of failures and fifty-five percent of
successes is a description of Atlas, not of a defect, and without the clean-success sample of §4.1
there is nothing to compute it against.

`CorpusHandle.absent_branches` records what did *not* happen, which is the field most likely to be
dropped as pointless. `[INF]` A routing branch that never fires across sixty-one failures is either a
branch nobody needs or a field nobody is emitting — and the second is the cold open, detected as a
side effect rather than by looking for it.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Trace store (C16) | Distiller | Bulk read, structural first | ~9.4M tokens per batch |
| C34's retention policy | Selector | Standing configuration | Which runs exist to be read |
| C37's classification | Per-task analyser | Per read | Structural by default, verbatim on demand |
| Distiller | **Chapter 46** | The corpus directory | Overview pushed, analyses pulled |
| Corpus | **Chapter 45** | Per manifest entry | Pointers, cited as `failure_evidence` |
| Superseded corpora | **Chapter 47** | Across iterations | Whether a pattern disappeared (§7.2) |
| Corpus writer | Workspace (C43) | Version stamp | The harness version described (§7.1) |
| Pointer-follow rate | Operators | Metric | Whether the fixed fields are adequate (§13.1) |

```
                                                             TIME VIEW

  << corpus.distilled >>       ....> corpus id, batch, harness
                                     version, token total

  << pattern.identified >>     ....> grouping field and value,
                                     task ids, diffuse flag

  << pattern.disappeared >>    ....> present in corpus n, absent
                                     in n+1, for the tasks an edit
                                     predicted. C47's second check
                                     (7.2)

  << corpus.stale >>           ....> an edit landed; the corpus
                                     describes a harness that no
                                     longer exists (7.1)

  << evidence.followed >>      ....> a pointer was pulled. Routine
                                     singly; a SIGNAL in aggregate
                                     (5.5)

  << field.missing >>          ....> an analysis could not be
                                     written without an undroppable
                                     field. Blocks, never warns
                                     (5.3)

  Figure 44.9 -- What distillation makes durable (D9 Event Flow)
```

`[INF]` The third event is the one with no equivalent anywhere else in the book. Every other signal
here reports something that happened; `pattern.disappeared` reports an absence, and it is only
computable because superseded corpora are kept (§7.2). It is also the cheapest evidence available
that an edit worked through the mechanism it claimed.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| A routing field is not emitted | Nothing; the analyses are well-formed and describe the wrong cause | Undroppable set as a schema that blocks (§5.3). The cold open |
| Analyses summarise what the model did, not what it saw | Rising share of default-owner routing (C43 §5.4) | Context accounting is the first field, not an optional one |
| Grouping by prose similarity | Clusters that track phrasing rather than cause | Group by field value (§4.2) |
| No clean-success contrast | Workload properties named as causes | A nonzero success sample (§4.1, C34 §5.5) |
| Distilling before attributing | The loop diagnoses its own damage | Required argument, not a comment (§8) |
| Stale corpus read as current | None; it reads correctly | Stamp the harness version; refuse on mismatch (§7.1) |
| Corpus budgeted to a fixed token count | The long tail of one-off failures silently drops | Budget the overview; let analyses scale (§5.1) |
| Pointers that do not resolve | Discovered when someone follows one | Trace id, span id, byte range — never prose (§9) |
| Verbatim pulled by default | Cost, and a wide standing exposure surface | Structural first; verbatim per field (§5.6) |
| Superseded corpora deleted | Disappearance becomes unmeasurable | Keep them; they are small and structural (§7.2) |
| Sub-agent failures summarised twice | Routing runs on second-hand evidence | Distil sub-agent runs as first-class tasks (§5.7) — partial |

`[INF]` The first two rows share a property that makes them the worst entries in this table: the
system continues to work, produces well-formed artefacts, and generates a stream of plausible
findings. Nothing errors, nothing looks wrong, and the loop does honest work on a false picture for
as long as the field is missing.

---

## 12. Scalability

**Distillation is the cheap step and it is worth restating.** Chapter 20 §12.1 put an iteration at
roughly 720 million tokens, almost all of it the benchmark. Reading 9.4 million tokens once is a
fraction of a single rollout. `[INF]` That asymmetry is the licence to be thorough: there is no
budget argument for sampling, and the only reason to sample would be a distiller written as though
tokens were scarce.

**The corpus grows with failures, not with the batch.** A harness that improves produces fewer
failures and a smaller corpus, so the cost of this step falls as the loop succeeds. `[INF]` The
inverse is the useful signal: a corpus growing while the score rises means new failure modes are
appearing as old ones close, which is what Chapter 48's non-additivity looks like from the evidence
side.

**Analyses parallelise; the pattern finder does not.** Each task's analysis is independent. The
pattern finder must hold all of them at once, which is precisely what makes diffuse patterns
findable, and it is the one step whose input grows linearly with the failure count. `[BP]` At a few
hundred failures the analyses no longer fit comfortably, and the answer is a two-stage grouping —
per-slice patterns first, then patterns across slices — rather than sampling, which would discard the
diffuse population the stage exists to find.

**Retention is the binding constraint, not compute.** `[INF]` Chapter 37 §5.4's split is what makes
this affordable at all: structural material for years, verbatim for weeks. A system that kept
everything verbatim could not retain long enough for Chapter 47 to compare across months, and one
that kept nothing verbatim could not answer the routing chain's second question.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Pointer-follow rate per pattern.** The field-adequacy signal. Following pointers on most patterns
  means the fixed fields cannot express what is happening (§5.5).
- **Default-owner routing share.** Chapter 43 §5.4's metric, which this chapter gives a second cause.
  Rising share means either no component owns the failure or no field describes it.
- **Corpus tokens against failure count.** Growing faster means a verbose analyser; slower means
  dropped tasks (§5.1).
- **Absent routing branches.** A branch that never fires across a whole batch is a question worth
  asking about the analyser, not about the harness (§9).
- **Verbatim pull share.** Cost and exposure in one number, and the thing Chapter 49 audits.

### 13.2 The review question

For any finding the corpus reports: **which field would have to be wrong for this to be the wrong
diagnosis?**

`[INF]` In the cold open the answer is one field, and it was not present, and nobody could have named
it because the question was never asked. Asking it routinely turns an unfalsifiable summary into a
checkable one, and it costs one pointer-follow to settle.

### 13.3 Teaching this to a new engineer

Give them the overview line — *thirty-four tasks: the model finishes without verifying its edits* —
and ask what to change. Everyone reaches for an instruction, and the reasoning is sound given the
evidence.

Then show them one trajectory's context accounting, with the test file in `deferred`.

`[INF]` The instinct that installs is the third in a row across this level, pointed at a new target.
Chapter 42 asked *worth what, against what baseline*. Chapter 43 asked *what else could be doing
this*. This one asks *what would I have to see to know I am wrong* — and all three are the same
discipline, which is refusing to accept a number or a finding without its conditions.

---

## 14. Relation to the Base Runtime

**What the base runtime supplies, and it is nearly everything.** `[DAR §7.1]` The result envelope is
what makes a trajectory navigable rather than a pile of records, and the trace id and span id in it
are literally the pointer format of §9. `[DAR]` The telemetry-versus-facts split is why the trace
store can be read freely by an automated process without any risk to correctness — nothing durable
depends on it, so distillation cannot break the runtime no matter what it does.

**What this chapter adds.** `[INF]` The runtime captures; this chapter decides what a reader is given.
The addition is the derivation in §5.2: the summary fields are not a design choice but a consequence
of Chapter 43's routing chain, which means the corpus schema changes if and only if the action space
does. That coupling is deliberate, and it is what stops the two pillars drifting apart.

**What the loop owes the runtime here.** Read-only, structural by default, verbatim by exception, and
every exception audited. `[AHE §3.3]` The controllability constraints make the runs directory
read-only, and Figure 44.3's note that the distiller cannot write to the trace store is that rule at the
component level: a process that could annotate its own evidence has no evidence.

**And the honest limit.** `[INF]` Nothing here measures how good the distillation is. The corpus is
judged by what the loop does with it, which is a slow and confounded signal, and there is no direct
instrument for "this analysis described the failure correctly". Chapter 41's machinery does not apply
— there is no golden set of correct diagnoses — and building one is the most obvious missing piece in
this level.

---

## 15. Industry Perspective

**`[AHE §3.2]`** Experience observability as one of the three pillars, the ten-million-to-ten-thousand
distillation, per-task analysis reports, the benchmark-level overview, trajectories as a navigable
file environment, and progressive disclosure as the reading discipline. The structure of §2.3 is the
source's.

**`[DAR §7.1]`** The result envelope and the telemetry-versus-facts split, which is what makes the
trace store safe to read automatically and safe to delete entirely.

**`[INF]`** The handbook's own here: that distillation is a routing decision, and the derivation of
the summary fields from Chapter 43's routing chain rather than from judgment; the undroppable-set
rule in §5.3 and its checkability; the observation that a summary of behaviour can only produce
behavioural causes, and therefore drifts toward the default owner; the diffuse pattern as a defect
class invisible to every other instrument in the book; the clean-success contrast as a second,
independent reason for Chapter 34's nonzero sample; the pointer-follow rate as a field-adequacy
metric; and the corpus-staleness pattern in §7.1, which is the third independent instance of a
versioned expensive derivation in this level.

**`[BP]` Structured incident write-ups are the closest established practice**, and the useful part is
what they get right by convention: a fixed template, filled in the same way every time, so that a
year of postmortems can be read as a set rather than as a pile. The difference here is scale and
reader — sixty-one per iteration, read by a machine — which is what turns "a good template" into a
schema that must block on a missing field.

**`[BP]` Citation-backed summarisation is standard in legal and medical review** and is unevenly
practised in software tooling. The property that matters is not that the summary is short; it is that
every claim resolves to a source, which converts a trusted summary into a checkable one.

**`[FUT]` The blast-radius mapping should be derivable from here.** Chapter 39 §4.1's linter maps
changed harness paths to the benchmark slices that must run, and is hand-maintained; Chapter 39 §15
noted the same information is latent in trace data. `[FUT]` The per-task analysis already records the
tool descriptions in force and the memory entries loaded, per task — which is a per-task record of
which harness components were actually exercised, and therefore exactly the mapping, kept current for
free. Nobody appears to have built it, and it is the shortest path from this chapter to a Level 4
improvement.

**`[FUT]` Evaluating a distiller is unsolved.** There is no golden set of correct diagnoses and no
obvious way to build one that does not itself require the judgment being tested.

---

## 16. Key Takeaways

1. **Distillation is a routing decision, not a summary.** A field may be dropped only if losing it
   cannot change which component the failure belongs to, and that rule generates the field list
   instead of leaving it to taste.
2. **A summary of what the model did can only blame the model.** Omit what the model could see and
   every context gap becomes a discipline failure, routed to the weakest component in the harness.
   That is the cold open, and it is a drift with a direction rather than random error.
3. **Three grains, three budgets.** The trajectory is never read whole, the per-task analyses are
   always read, and the overview is read first and often only.
4. **The overview is not an executive summary.** It is the only place a diffuse pattern — weak in
   nine task types, obvious in none — can be seen at all, and no sample, slice, or aggregate will
   find one.
5. **Nothing is lost if the original is reachable.** Every claim carries a resolving pointer, and the
   rate at which readers follow pointers is a measurement of whether the fixed fields are right.
6. **Keep a nonzero sample of clean successes.** Without a contrast set the pattern finder cannot
   distinguish a property of failure from a property of the workload, and it will name the second.
7. **A corpus describes one harness version.** Stamp it and refuse on mismatch, because a stale
   corpus reads exactly like a current one — the third versioned expensive derivation in this level
   with that property.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Per-task analysis** | One structured report per failing task, with fixed fields chosen so that each answers a routing question. | `[AHE]` | Ch 45, Ch 46 |
| **Benchmark-level overview** | The cross-task document, and the only artefact in which a pattern spanning many tasks can be seen. | `[AHE]` | Ch 46 |
| **Evidence pointer** | A citation that resolves to an exact span, which makes a reduction lossless rather than lossy. | `[INF]` | Ch 45, Ch 47 |
| **Undroppable field** | A field the distiller may never summarise away, because losing it changes which component a failure routes to. | `[INF]` | Ch 46 |
| **Diffuse pattern** | A defect appearing slightly in many task types and obviously in none, invisible to sampling, slicing, and aggregation alike. | `[INF]` | Ch 47, Ch 48 |
| **Structural partition** | The redacted, low-risk half of a trajectory — calls, order, verdicts, cost — which is most of what the loop needs and is retainable for years. | `[BP]` | Ch 46, Ch 49 |
| **Distillation ratio** | The roughly thousand-to-one reduction from raw trajectory to evidence, which is a budget to watch rather than a target to hit. | `[AHE]` | Ch 48 |
| **Corpus staleness** | The property that a corpus describes one harness version, so reading it after an edit re-diagnoses what was already fixed. | `[INF]` | Ch 46, Ch 47 |
| **Clean-success contrast** | The nonzero sample of passing runs that lets a pattern finder tell a property of failure from a property of the workload. | `[INF]` | Ch 46 |
| **Context-gap misdiagnosis** | Reading a failure as a reasoning defect when the model never saw the input it needed; the drift that a behaviour-only summary guarantees. | `[INF]` | Ch 46, Ch 48 |

---

**Next:** Chapter 45 — *Decision Observability.* The evidence now exists in a form something can
read completely and cite exactly. The next chapter is about what must be written down at the moment
an edit is made — evidence, root cause, targeted fix, predicted fixes, at-risk regressions,
constraint level — and why a prediction recorded after the result is not a prediction.
