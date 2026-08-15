# Appendix B — Naming Conventions

Hand-written. Consolidates Phase 1 §7 and Phase 2 §7.3, which is where the chapters' `Appendix B`
references point. The short version is on the reference card in
[F.2](../front-matter/f2-notation-tags-and-diagram-legend.md); this is the full treatment, with the
reasoning that made each choice.

A naming convention earns its place by making a mistake visible. Every rule below is here because
its absence hid something.

---

## 1. Prose

| Thing | Convention | Example |
|---|---|---|
| A subsystem, in prose | Title Case, definite article, singular | the Activity Runner |
| The five nouns as concepts | Capitalised | a Run, one Episode |
| A generic instance of one | lowercase | the run parked, three episodes |
| Book tier | Level *n* | Level 3 |
| Architecture tier | lowercase | the kernel layer |
| Build order | Stage *n* | Stage 4 |
| Chapter cross-reference | `Ch NN §M` | Ch 18 §7 |

The capitalisation split in rows two and three is doing real work. **A capitalised Run is the
concept; a lowercase run is an instance.** "Every Run has a lease" is a claim about the model; "the
run lost its lease" is a claim about something that happened. Chapter 5 is entirely about the five
nouns as concepts, and mixing the two reads as though it is describing an incident.

---

## 2. Code

**Python throughout.** Ports are `typing.Protocol`, not ABCs — the runtime never inherits from an
extension point, and a Protocol makes that structural. Data carriers are frozen `@dataclass`.

Type hints are mandatory on every signature. `[INF]` A signature without them is not a contract, and
Appendix E's 109 ports exist to be read as contracts.

| Thing | Convention | Example |
|---|---|---|
| Port | `Protocol`, PascalCase, `Port` suffix | `PlannerPort`, `ModelPort` |
| Dataclass | PascalCase, frozen | `Run`, `Verdict`, `Attribution` |
| Enum | PascalCase, `StrEnum` unless ordering matters | `ConstraintLevel`, `Rank(IntEnum)` |
| Field, parameter | snake_case | `input_digest`, `lease_until` |
| Fake port, in tests | `Fake<Port>` | `FakeModelPort` |

**`Port` suffix only on Protocols.** A class named `ModelPort` is an interface; a class named
`ModelClient` is an implementation. Chapter 13's argument that the provider is never visible above
the port line is enforceable only if the line is nameable.

**`StrEnum` unless ordering matters.** A string enum serialises into a manifest, a trace, and a
database column without a codec. `Rank` in Chapter 28 is an `IntEnum` because the verdict lattice
compares ranks, and that comparison is the whole point of the downgrade-only rule.

---

## 3. Storage

| Thing | Convention | Example |
|---|---|---|
| Table | snake_case, plural | `activities`, `events`, `runs` |
| Column | snake_case, singular | `lease_until`, `input_digest` |
| Read-model projection | `<noun>_view` | `run_progress_view` |
| Timestamp column | `<verb>_at` | `superseded_at`, `sealed_at` |
| Boolean column | `is_<adjective>` or `has_<noun>` | `is_current`, `has_effects` |

**`_view` on projections is a durability claim**, not a style preference. Chapter 9's separation of
the three flows depends on a reader being able to tell, from a name alone, whether a thing is a fact
or a derivation. Anything ending `_view` can be dropped and rebuilt; nothing else can.

---

## 4. Messages

Three message kinds, three shapes, and the shapes differ so that a name tells you what it is without
context.

| Kind | Convention | Example | Tense |
|---|---|---|---|
| Command | `cmd.<domain>.<verb>` | `cmd.repo.apply_patch` | Imperative |
| Event | `<domain>.<noun>.<past_verb>` | `run.step.completed` | Past |
| Tool id | `tool.<namespace>.<verb>` | `tool.repo.apply_patch` | Imperative |

**A command is imperative and an event is past tense**, and the discipline is worth enforcing. A
command can be refused; an event cannot, because it has already happened. `[INF]` A name like
`run.step.complete` is a category error that will eventually be handled as though it could fail, and
Chapter 22's outbox is built on events being unarguable.

**Commands and tool ids share a verb deliberately.** `cmd.repo.apply_patch` is the command that
causes `tool.repo.apply_patch` to run. Chapter 22's command port and Chapter 14's tool engine are
different layers, and the shared verb is what makes a trace readable across them.

### Idempotency keys

```
    <command>:<scope>:<digest>
```

The command name, the scope it applies within, and a digest of its inputs. Chapter 22 §5 uses this
to let a domain deduplicate a replayed command; Chapter 21's activity identity is the same idea one
layer down, keyed on `hash(run_id, plan_id, step_id, tool_id, input_digest)`.

`[INF]` The scope segment is the one that gets dropped and should not be. Without it, two tenants
issuing structurally identical commands collide, which is a data-isolation failure wearing an
idempotency costume (Chapter 37).

---

## 5. Observability

| Thing | Convention | Example |
|---|---|---|
| Metric | `ark_<subsystem>_<measure>_<unit>` | `ark_activity_replay_total` |
| Trace span | `<layer>/<component>/<operation>` | `kernel/activity_runner/dispatch` |
| Log field | snake_case, and `request_id` on everything | `run_id`, `harness_version` |

**The `ark_` prefix separates the runtime's own signals from the domain's.** Chapter 34's argument
that there are two observability systems for two questions is unusable if their metrics share a
namespace.

**Unit suffixes are mandatory** — `_total`, `_seconds`, `_bytes`, `_pp` for percentage points.
`[BP]` A metric named `ark_episode_duration` will be read as milliseconds by somebody, and the
graph will be wrong by three orders of magnitude without ever looking wrong.

**Span names are a path, not a sentence.** Three segments: which layer, which component, which
operation. That makes a trace filterable by layer, which is what Chapter 9's flow tag was added to
support.

---

## 6. Harness mount points

The seven component types live at fixed paths, and the paths are part of the contract rather than a
convention. Chapter 43 §3 is why: a change with no address cannot be recorded, predicted, or
reverted.

```
    workspace/
      systemprompt.md                     system prompt
      tool_descriptions/*.tool.yaml       tool description
      tools/**/*.py                       tool implementation
      middleware/**/*.py                  middleware
      skills/<name>/SKILL.md              skill
      sub_agents/<name>/agent.yaml        sub-agent configuration
      LongTermMEMORY.md                   long-term memory
```

`[AHE §3.1]` The layout is the source's. `[INF]` What the handbook adds is that a file *not* under a
mount point is not a component — it is an orphan that reads correctly, reviews well, and does
nothing, with no error at any point (Chapter 43 §4.1).

---

## 7. Change identifiers

| Thing | Convention | Example |
|---|---|---|
| Manifest entry | `chg-<n>`, scoped to an iteration | `chg-31` |
| Harness version | a git sha, never a semantic version | `a3f9c21` |
| Version triple | code · harness · model, recorded together | Chapter 38 §3.1 |
| Corpus version | an identifier for the benchmark's contents | Chapter 41 §5.5 |
| Seed | a tag, not a branch and not history | Chapter 43 §5.7 |

**A harness version is a sha because it is not released, it is promoted.** `[INF]` Semantic
versioning encodes a compatibility promise, and a harness makes none — Chapter 38's whole argument is
that the harness is a version axis whose meaning is defined by what it was measured against, not by
its number.

---

## 8. What is deliberately not named

Six phrases are banned outside a single definitional mention, and their absence is a convention in
its own right. Each hides the thing it appears to name:

| Banned | Use instead |
|---|---|
| "the agent" as a component | Run, Episode, Planner, Activity Runner |
| orchestrator | run driver |
| workflow | plan, task graph |
| prompt engineering | context engineering, harness engineering |
| memory, unqualified | short-term / long-term / episodic / procedural |
| just, simply | — |

The linter enforces five of them and warns on "the agent", because that one is legitimate inside
quotation marks and when naming the Evolve Agent — which is a specific component rather than a vague
one. Every warning in the corpus has been checked by hand for that reason.

---

**See also:** [Appendix C — Diagram Conventions](c-diagram-conventions.md) ·
[Appendix E — Port Signatures](e-port-signatures.md) ·
[CONVENTIONS.md](../CONVENTIONS.md) for the authoring card the linter enforces.
