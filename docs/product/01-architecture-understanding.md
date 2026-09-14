# 1 — Architecture Understanding Report

*Recovered from this repository on 2026-09-06. Every claim below cites the file it came from.
Where the repository does not settle a question, this report says so rather than filling the gap.*

---

## 1.1 What this repository actually is

`README.md` states it plainly, and it is the first thing any implementation plan has to absorb:

> "This repository contains all 50 handbook chapters, a detailed runtime specification, a compiled
> handbook draft, source diagrams, and the Agentic Harness Engineering research paper. **It is a
> knowledge base, not an executable runtime implementation.**"

Verified by inspection:

| Artefact | Count | Notes |
|---|---|---|
| Handbook chapters | 50 (`docs/handbook/chapters/00–49`) | 49,972 lines |
| Architecture specification | 1 (`docs/architecture/universal-runtime-v1.0-…md`) | 4,824 lines, revision 4 |
| Appendices / front matter / interludes / levels | 22 | incl. glossary, port signatures, invariant checklist |
| Diagrams | 9 SVG | incl. `six-layer-agent-runtime.svg` |
| Derived DOCX references | 10 | `learning-notes/` |
| **Python source files** | **5** | **all in `tools/`, all handbook build tooling** |
| Product source code | **0** | no `.swift`, `.ts`, `.go`, `.rs`; no runtime `.py` |

**Finding 0 — there is nothing to extend.** "Extend the existing repository" is not an available
option, because no runtime exists in it. This is decisive for Part 8 and is treated there.

---

## 1.2 The six layers — CONFIRMED, and the user's ordering is correct

`docs/handbook/chapters/04-complete-runtime-layers-and-process-topology.md`, Figure 4.1, gives
exactly six horizontal bands in this order:

```
SURFACE     written by YOU   chat · IDE · inbox · dashboard · CLI · webhook · another agent
   │ (1) goals, approvals, signals
EDGE        written by YOU   stateless. accepts intent, streams read-models.
                             runs NO consumer, NO loop, NO model call.
   │ (2) commands + events
SUBSTRATE   OFF THE SHELF    one transactional database · one queue · nothing else
   │ (3) claimed events
KERNEL      THE PART YOU DO NOT WRITE   relay · run driver · activity runner · sweeper · queues
   │ (4) plan, tool, model, grade, ask
PORTS       written by YOU   planner · tool · model · grader · approval · domain
   │ (5) commands
DOMAIN      written by YOU   aggregates · invariants · your tables
                             knows NOTHING about the runtime
   │ (6) truth + event, one transaction  ──> back to SUBSTRATE, closing at (3)
```

Three properties are load-bearing and must survive any port to a new platform:

**The narrow waist.** Ch 4 §2.3: *"Between the runtime and your product, exactly two kinds of message
cross: Commands flow down, Events flow up. Nothing else."* No shared tables, no foreign keys, no
imports either way. Ch 4 §2.2 derives this from debuggability rather than taste: a boundary is only
observable if everything crossing it is enumerable, and a shared table is an unenumerable second
channel.

**The deletion test.** Ch 4 §2.4: *"If you cannot delete the entire runtime and still have a coherent
product, the two have merged."*

**One bit of transparency.** Ch 4 §2.1 is careful here and it matters for a product that mutates user
files: the command container is *"opaque as to contents but not as to consequence — every command
carries one bit the runtime is entitled to read"* — whether the effect is reversible. That bit is the
whole safety model.

---

## 1.3 The five nouns — CONFIRMED

`chapters/05-five-nouns.md` §2.3, described there as "the whole chapter":

| Noun | Lifetime | Holds | Scarcity of what it holds |
|------|----------|-------|--------------------------|
| **Run** | minutes to weeks | one row | abundant |
| **Park** | unbounded | one row | abundant |
| **Activity** | seconds to minutes | a semaphore slot, a budget reservation | scarce (4–6 slots) |
| **Episode** | seconds | one worker | scarce (8–16 workers) |
| **Step** | milliseconds | one database connection, briefly | very scarce (pool of 20) |

The organising rule (§2.4, the *custody gradient*): **scarcity × duration is held roughly constant.
The longer a noun lives, the less scarce the thing it is permitted to hold.**

Activity is defined as *"the only place non-determinism is allowed"* (Appendix A). Park is
*"the general waiting primitive"* — a run suspended as a durable row holding no worker, lease, slot,
connection or timer, *"so that gating costs no capacity."*

---

## 1.4 The conceptual boundaries the brief asked me to keep distinct

These are distinct in the source. Here is the chain, with the chapter that owns each term.

```
OBSERVATION            what the runtime perceived about itself          Ch 16
  │                    "captures how the runtime perceived itself,
  │                     distinct from the monitoring operators use"
  ▼
FACT / EVENT           durable, appended in the same transaction as     Ch 7, Ch 22
  │                    the change it describes. "Something durable
  │                    that a later reader is entitled to rely on;
  │                    the thing progress is deliberately NOT."
  ▼
TRAJECTORY             the full record of one run — every span, with    Ch 16
  │                    what the model COULD SEE at each
  ▼
EVIDENCE               "the retained, DISTILLED SUBSET of trajectories  Ch 16, Ch 44
  │                     that the evolution loop reads"
  ▼
BELIEF / WORLD STATE   claim + provenance + observed-at(event seq)      Ch 25
  │                    + scope. "A disposable cache of beliefs about
  │                    an environment the runtime does not control."
  ▼
MEMORY                 cross-run, tenant-scoped. The model PROPOSES     Ch 12, Ch 37
  │                    at run end and NEVER writes.
  ▼
DECISION               planner-port output; a contract, not a call      Ch 10, spec I21
  ▼
ACTION / ACTIVITY      the quarantine: leased, budgeted, cancellable    Ch 5, Ch 14
  ▼
OUTCOME                graded on a lattice — a judge may LOWER a        Ch 28, spec I18
                       verdict and may never RAISE one
```

Three of these distinctions carry real design weight and are the ones most often collapsed:

- **Observation is not Evidence.** Ch 16 §2.3 separates three kinds of record: metrics/logs (*never*
  durable, loss is fine), facts (*always* durable, loss unacceptable), trajectories (durable with
  retention, 1–10 MB per run, *"the highest-risk dataset"*, loss is expensive but not fatal). Evidence
  is the distilled subset of the third.
- **World state is not Memory.** A belief is disposable by definition and is invalidated by scope
  overlap against the effect stream. Memory is durable, cross-run, and written only through a
  proposal path.
- **Progress is not a Fact.** Ch 7's rule, restated as spec invariant **I20**: *"Progress is never
  written to the event log."*

**Honest gap: "Knowledge" is under-defined.** It is *not* a glossary entry. It appears in the
specification only as the subject of invariant **I18** ("Only verified observations update
knowledge") and as a section heading. Anything the PRD says about a knowledge layer is **new design,
not recovered architecture**, and is marked as such.

---

## 1.5 Mechanisms that a file-mutating product depends on directly

Four, quoted because the PRD builds on them literally.

**Effect tiers (Ch 27 §2.3).** The reason an undo story is possible at all.

| Tier | Name | Available operation | Examples |
|---|---|---|---|
| 1 | **Owned** | Rollback: restore the kept prior version | scratch files, run state, sandbox filesystem |
| 2 | **External, compensable** | Compensation: a new forward action | migration, cloud resource, pull request |
| 3 | **Escaped** | None | email, chat message, published package |

And the sentence the chapter calls the most useful in the section: *"an effect's tier is set by the
most escaped thing it caused, not by the thing it did."* Ch 27 §5.3 adds the restraint rule:
*"compensate when the effect is wrong on its own, and leave it when the effect is merely
incomplete,"* with the honest third option of raising a dead letter instead of guessing.

**The provenance lattice (Ch 31 §5.1).** Trusted / semi-trusted / untrusted, with the rule stated as
the whole mechanism:

> `capability is a function of (step, declared_needs, run) and NEVER of content.`
> Content moves DOWN the lattice freely. Content never moves UP. There is no operation that promotes
> a label, because any such operation would be reachable by the content itself.

§5.2 is equally important and usually missed: untrusted content *may* shape the plan, determine which
files get edited, supply the entire substance of the work. What it may not do is widen scope, alter
policy, authorise an effect, or reach a destination outside the egress allowlist.

**The effect tag (Ch 14, Ch 10).** *"Pure or effectful, held in the registry and never supplied by the
model; the whole of the safety model."* Spec **I15**: unknown third-party effect defaults to
`EFFECTFUL`.

**Activity identity (Ch 21, spec I9).** A fingerprint of run + plan + step + tool + inputs that decides
whether a stored result may be reused instead of re-run. The specification singles it out (§10.7):
*"Every other invariant can be added later at a cost proportional to the work already done. This one
cannot… It is roughly thirty lines. Write it first."*

---

## 1.6 The second architecture in the repository

`docs/architecture/universal-runtime-v1.0-architecture-specification.md` (revision 4) is not a
restatement of the handbook. It is a second, independently coherent design with a different
vocabulary, and it is the more implementation-ready of the two: 14 design rules, 32 numbered
invariants each naming the test that proves it, a full repository tree, and a 13-stage build order.

Its execution model (§5, "three loops, one graph"):

```
OUTER   · CONTROLLER          goal lifecycle · execution graph · scheduling · recovery
          speaks capabilities and intents — never tool names
  MIDDLE  · CAPABILITY EXECUTOR   one capability invocation end to end; a DECLARED recipe
            plans NOTHING — the chain is authored in the package  [I30]
    INNER   · TOOLS               side effects · external systems · raw observations
```

with intent→tool binding resolved *deterministically* above all three, after the Decision Engine and
before the Policy Gate. Design rule 14: **"No reasoning below the Decision Engine. Exactly one box in
the runtime is non-deterministic."** Design rule 13: **"One execution model. The ExecutionGraph is the
plan, the state, the progress, the dependencies and the checkpoint."**

### Finding A — the two architectures are not reconciled, and one must win before code

They overlap heavily but name things differently, and in places divide responsibility differently:

| Handbook | Specification | Same thing? |
|---|---|---|
| Run | Session | Yes — different word |
| Activity | Action | Yes — different word |
| Episode | *(absent)* | The spec has no episode concept |
| Park | `runtime/parking/` (**I17**) | Yes |
| Planner port | Decision Engine + Router | Roughly; the spec splits it |
| Tool port | Capability Executor **+** Tools | **No** — the spec inserts a middle loop the handbook does not have |
| Kernel = relay, run driver, activity runner, sweeper | Controller, binding, policy gate, reconciler | Overlapping, not congruent |
| — | ExecutionGraph | New in the spec; the handbook's Ch 24 task graph is close but not identical |

Neither is wrong. But the specification's invariant list — the thing an implementation would actually
be tested against — references components that do not appear in the handbook's kernel, and the
handbook's five nouns do not appear in the specification's invariants. Shipping against both produces
a codebase that satisfies neither reviewer.

**Recommendation: the specification wins for implementation, the handbook wins for reasoning.** The
specification is closer to code, is versioned with a modification log, and carries testable
invariants. The handbook's derivations remain the justification for those invariants. Where they
conflict on a name, use the specification's. Where they conflict on a *rule*, the handbook's
derivation should be checked, because the specification asserts where the handbook derives.

### Finding B — MCP is absent from the canonical architecture

> **Correction, and the finding as it should have read.** The original text of this finding claimed
> MCP was absent from the handbook *and* from the runtime specification. **The second half was
> wrong.** The grep behind it was run from inside `docs/handbook/` and never searched
> `docs/architecture/`. The specification does mention MCP, in four places.

What is true: **no handbook chapter mentioned MCP.** Confirmed by `grep -ril` across
`docs/handbook/chapters/` — the term appeared only in the compiled DOCX and one blueprint file.

What the **specification** actually contained before this work:

| Where | What |
|---|---|
| §7 tree | `tools/mcp/` with six named modules — `mcp_client`, `mcp_server_registry`, `mcp_tool_adapter`, `mcp_descriptor_translator`, `mcp_effect_inferencer`, `mcp_transport` |
| §7 tree | `contracts/protocols/mcp-bridge-protocol.md` listed among the protocols |
| §7.4.2 | One rule: third-party and MCP tools *of unknown effect* default to `EFFECTFUL` |
| §14 | An *MCP bridge* box in the component block diagram |

So the gap was narrower and more specific than "absent": the specification **named a component and a
contract file, and never wrote either.** Six module names and one default is not a contract.

> **Both halves are now closed.** **Chapter 50 — Third-Party Tool Supply and the Model Context
> Protocol** carries the derivation. Specification **revision 5** adds **§9.9 MCP Bridge Protocol**,
> invariants **I33–I39** in §10.8, and build-order stage **9c**. Revision 5 also corrects §7.4.2's
> framing: a server-supplied effect tag is now *discarded*, not treated as better than silence,
> because the disqualification is about interest rather than availability.
>
> None of this changes the product recommendation below. Chapter 50's own conclusion is that *refuse*
> is the honest default for a third-party tool surface, which is what the PRD's FUTURE classification
> amounts to. Anything the PRD says about MCP is new
design. Given the brief's instruction not to implement MCP unless the existing architecture requires
it: **the existing architecture does not require it, does not mention it, and the PRD classifies it
FUTURE.**

### Finding C — the architecture is server-shaped, and iOS is not a server

This is the most consequential finding in the report, and it is not a criticism of the architecture —
it is correct for what it was written for. But every one of the following is an assumption:

| Assumption in the source | Where | Reality on iOS |
|---|---|---|
| "one transactional database · one queue" | Ch 4 Fig 4.1 | SQLite exists; a queue with independent consumers does not, because there is only one process |
| Relay claims with `FOR UPDATE SKIP LOCKED`, N workers, no coordination | Ch 4 Fig 4.2 | One process, no contention. The entire claim mechanism is answering a problem that does not exist |
| Sweeper "runs continuously, NEVER only at boot" | Ch 4 Fig 4.2 | **No process runs when the app is not foregrounded.** A sweeper cannot exist |
| Episode = a worker borrows a run and gives it back | Ch 5 §2.1 | There is no worker pool. Episode collapses into "the app was open" |
| Lease + version CAS, exactly one driver per session (**I6**) | Ch 17, spec I6 | One driver by construction. The lease protects nothing |
| Park costs no capacity | Ch 5 §5.5 | True, and *more* important here — but resumption requires the user to reopen the app |
| Per-tenant admission, budget ledger, work classes | Ch 23, Ch 33 | One tenant. One user |

Meanwhile iOS introduces failure modes the architecture does not address: the process can be
terminated at any instant with **no drain and no signal**, and security-scoped access is not merely
revocable but *leaks kernel resources if not balanced* (Apple's own documentation, see report 2).

The correct reading is not "the architecture doesn't work on iOS." It is: **roughly half the kernel is
a solution to multi-tenant server contention, and on-device that half should be deleted rather than
ported.** What must survive is the part that is about *correctness under interruption* — activity
identity, the effect ledger, checkpointing, the outbox, the tiers, the lattices. What should not be
ported is the part about *sharing scarce resources between tenants*.

---

## 1.7 Summary of Part 1

| Question | Answer |
|---|---|
| Are the six layers real? | **Yes**, exactly as stated, Ch 4 Fig 4.1 |
| Is the narrow waist real? | **Yes**, and it carries a reversibility bit |
| Are the conceptual boundaries maintained in the source? | **Yes**, except *Knowledge*, which is under-defined |
| Is there a canonical MCP position? | **No** |
| Is there code? | **No** |
| Is the architecture implementation-ready? | The **specification** nearly is; the handbook is a reasoning artefact |
| Does it need to change for iOS? | **Yes, substantially** — see Finding C |
| Does it need to change for macOS? | **Less** — macOS can host a real background process; the server shape mostly survives |
