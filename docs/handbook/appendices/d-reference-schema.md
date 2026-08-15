# Appendix D — Reference Schema

> **Generated file. Do not edit by hand.**
>
> Assembled from the chapters by `tools/build_appendices.py`. To change an
> entry, edit the chapter it comes from and regenerate.

Every data structure the handbook defines, from the *Data Structures* section of each chapter. Frozen dataclasses are the handbook's data carriers; enums are the closed vocabularies. Ports live in [Appendix E](e-port-signatures.md).

35 structures across 46 chapters.

---

## Index

| Structure | Kind | Chapter | Purpose |
|---|---|---|---|
| `Flow` | enum | [Ch 9](../chapters/09-three-flows-data-control-event.md) | Attached to a trace span so a trace can be filtered to one axis |
| `Effect` | enum | [Ch 10](../chapters/10-the-planner.md) | — |
| `Volatility` | enum | [Ch 11](../chapters/11-the-context-system.md) | — |
| `Disposition` | enum | [Ch 11](../chapters/11-the-context-system.md) | — |
| `EntryState` | enum | [Ch 12](../chapters/12-the-memory-system.md) | — |
| `Classification` | enum | [Ch 12](../chapters/12-the-memory-system.md) | — |
| `FinishReason` | enum | [Ch 13](../chapters/13-the-reasoning-engine.md) | — |
| `Effect` | enum | [Ch 14](../chapters/14-the-tool-execution-engine.md) | — |
| `Outcome` | enum | [Ch 14](../chapters/14-the-tool-execution-engine.md) | — |
| `TruncationStrategy` | enum | [Ch 14](../chapters/14-the-tool-execution-engine.md) | — |
| `SpanKind` | enum | [Ch 16](../chapters/16-the-observation-system.md) | — |
| `RetentionClass` | enum | [Ch 16](../chapters/16-the-observation-system.md) | The span the cold open did not have |
| `ExitCondition` | enum | [Ch 18](../chapters/18-the-runtime-loop.md) | — |
| `ConstraintLevel` | enum | [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | — |
| `Verdict` | enum | [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | — |
| `ActivityState` | enum | [Ch 21](../chapters/21-durable-execution.md) | The vocabulary the cold open lacked (section 2.3) |
| `ExecutionMode` | enum | [Ch 21](../chapters/21-durable-execution.md) | The vocabulary the cold open lacked (section 2.3) |
| `OutboxState` | enum | [Ch 22](../chapters/22-the-event-spine.md) | — |
| `WorkClass` | enum | [Ch 23](../chapters/23-the-scheduler.md) | — |
| `AdmissionOutcome` | enum | [Ch 23](../chapters/23-the-scheduler.md) | — |
| `NodeStatus` | enum | [Ch 24](../chapters/24-the-task-graph.md) | — |
| `JoinPolicy` | enum | [Ch 24](../chapters/24-the-task-graph.md) | — |
| `BeliefStatus` | enum | [Ch 25](../chapters/25-the-world-model.md) | — |
| `Response` | enum | [Ch 26](../chapters/26-planning-algorithms.md) | — |
| `Tier` | enum | [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | — |
| `EffectState` | enum | [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | — |
| `BudgetAxis` | enum | [Ch 29](../chapters/29-long-running-agents.md) | — |
| `DecisionKind` | enum | [Ch 30](../chapters/30-human-authority.md) | — |
| `GateState` | enum | [Ch 30](../chapters/30-human-authority.md) | — |
| `Flow` | enum | [Ch 34](../chapters/34-observability.md) | — |
| `Classification` | enum | [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Required to WRITE |
| `Tier` | enum | [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | — |
| `ReplayOutcome` | enum | [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | — |
| `Verdict` | enum | [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | — |
| `AutonomyLevel` | enum | [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | — |

---

## Definitions

### Chapter 9 — Three Flows: Data, Control, Event

```python
from dataclasses import dataclass
from enum import StrEnum


class Flow(StrEnum):
    CONTROL = "control"
    DATA = "data"
    EVENT = "event"


@dataclass(frozen=True)
class FlowAnnotation:
    """Attached to a trace span so a trace can be filtered to one axis.
    The single highest-value thing in this chapter to actually build."""

    flow: Flow
    bytes_moved: int | None      # data spans only
    decided: str | None          # control spans: what was chosen
    durable: bool                # event spans: did it reach the outbox
```

### Chapter 10 — The Planner

```python
from dataclasses import dataclass
from enum import StrEnum


class Effect(StrEnum):
    PURE = "pure"
    EFFECTFUL = "effectful"


@dataclass(frozen=True)
class Step:
    step_id: int                 # position; unique within a plan only
    tool_id: str                 # "tool.repo.apply_patch"
    input: Mapping[str, object]
    effect: Effect               # from the tool registry, NOT the model
    activity_id: str             # minted at plan time (section 4.2)
    depends_on: tuple[int, ...] = ()   # Ch 24 opens this


@dataclass(frozen=True)
class Plan:
    plan_id: PlanId              # fresh ULID per plan, never reused
    run_id: RunId
    steps: tuple[Step, ...]      # tuple, not list -- immutability is
                                 # structural, not a convention
    created_at: datetime
    supersedes: PlanId | None    # the revision chain
    reason: ReplanReason         # why this plan exists at all
    strategy: str                # which strategy produced it (Ch 26)
```

### Chapter 11 — The Context System

```python
from dataclasses import dataclass
from enum import StrEnum


class Volatility(StrEnum):
    STABLE = "stable"              # per deploy
    SEMI_STABLE = "semi_stable"    # per replan
    VOLATILE = "volatile"          # per step


class Disposition(StrEnum):
    INCLUDED = "included"
    DEFERRED = "deferred"          # replaced by a retrievable reference
    DROPPED = "dropped"
    CONDENSED = "condensed"        # lossy; the only irreversible one


@dataclass(frozen=True)
class Candidate:
    source: str
    volatility: Volatility
    tokens: int
    importance: float              # ordering WITHIN a band only
    reference: str | None          # how to retrieve it if deferred


@dataclass(frozen=True)
class ContextAccounting:
    """Per-call, per-source. The whole of section 13 rests on this."""

    tokens_by_source: Mapping[str, int]
    disposition_by_source: Mapping[str, Disposition]
    working_budget: int
    used: int
    volatile_boundary_offset: int   # section 5.2, the cache contract
    cache_prefix_tokens: int        # asserted identical to last call
    compactions_this_run: int       # E3 fires when this reaches 2


@dataclass(frozen=True)
class Context:
    blocks: tuple[Block, ...]       # tuple: immutability is structural
    accounting: ContextAccounting
    harness_version: str            # what policy built this (Ch 38)
```

### Chapter 12 — The Memory System

```python
from dataclasses import dataclass
from enum import StrEnum


class EntryState(StrEnum):
    PROVISIONAL = "provisional"    # below the load floor
    ACTIVE = "active"
    RETIRED = "retired"


class Classification(StrEnum):
    NEW = "new"
    REINFORCES = "reinforces"
    CONTRADICTS = "contradicts"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"          # an event or a recommendation


@dataclass(frozen=True)
class MemoryEntry:
    entry_id: EntryId
    scope: Scope                   # repository, tenant, or GENERAL
    heading: str                   # ~40 tokens; always loaded
    body: str                      # loaded on request only
    state: EntryState

    confidence: float              # 0.0-1.0
    evidence_runs: int             # how many runs corroborated it
    first_written: datetime
    last_confirmed: datetime       # decay is measured from HERE
    contradicted_count: int

    origin: str                    # "run:9f2c" | "human" | "evolve:chg-7"


@dataclass(frozen=True)
class MemoryProposal:
    observation: str               # what happened, not what to do
    scope_hint: Scope
    run_id: RunId
    evidence: tuple[StepRef, ...]  # which steps support this
```

### Chapter 13 — The Reasoning Engine

```python
from dataclasses import dataclass
from enum import StrEnum


class FinishReason(StrEnum):
    STOP = "stop"                    # the model finished
    OUTPUT_LIMIT = "output_limit"    # hit max_output_tokens
    TOOL_CALL = "tool_call"          # stopped to call a tool
    REFUSED = "refused"              # content refusal
    ABORTED = "aborted"              # we abandoned it


@dataclass(frozen=True)
class TokenUsage:
    """None means the provider did not report it. Never coerce to 0."""

    input: int | None
    cached: int | None               # served from the prefix cache
    reasoning: int | None            # internal; often billed as output
    output: int | None

    @property
    def is_complete(self) -> bool:
        return all(v is not None for v in
                   (self.input, self.cached, self.reasoning, self.output))


@dataclass(frozen=True)
class ModelPolicy:
    """Pinned with the harness version (Ch 38). Not per-call tuning."""

    model_id: str
    effort: EffortTier
    temperature: float
    max_output_tokens: int
    tool_choice: ToolChoice


@dataclass(frozen=True)
class Completion:
    text: str
    tool_calls: tuple[ProposedToolCall, ...]
    finish: FinishReason
    usage: TokenUsage
    cost_settled_cents: int
    cost_is_estimated: bool          # True when usage was incomplete
    latency_ms: int
    policy: ModelPolicy              # what actually ran, for Ch 47
```

### Chapter 14 — The Tool Execution Engine

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

### Chapter 16 — The Observation System

```python
from dataclasses import dataclass
from enum import StrEnum


class SpanKind(StrEnum):
    CONTEXT_ASSEMBLED = "context_assembled"   # the cold open's span
    MODEL_CALL = "model_call"
    TOOL_CALL = "tool_call"
    PLAN_CREATED = "plan_created"
    PLAN_REJECTED = "plan_rejected"           # Ch 10 training signal
    SCHEMA_REJECTED = "schema_rejected"       # Ch 14 training signal
    GATE_RAISED = "gate_raised"
    GRADE = "grade"


class RetentionClass(StrEnum):
    EVIDENCE = "evidence"        # interesting outcome; full fidelity
    BASELINE = "baseline"        # sampled, shaped
    TOMBSTONE = "tombstone"      # expired; envelope only


@dataclass(frozen=True)
class ContextSpan:
    """The span the cold open did not have."""

    stable_digest: str               # hash; reconstructible from git
    semi_stable_digest: str
    volatile_body: str               # verbatim: the part that differs
    accounting: ContextAccounting    # Ch 11: included/deferred/dropped
    volatile_boundary_offset: int    # where the split was made


@dataclass(frozen=True)
class ToolSpan:
    tool_id: str
    arguments: Mapping[str, object]
    result: ToolResult
    description_digest: str          # Ch 15's surface, as read
    middleware_applied: tuple[str, ...]


@dataclass(frozen=True)
class SealReport:
    run_id: RunId
    outcome: RunOutcome
    retention: RetentionClass
    spans: int
    bytes_retained: int
    bytes_dropped: int
    redactions: int
```

### Chapter 18 — The Runtime Loop

```python
from dataclasses import dataclass
from enum import StrEnum


class ExitCondition(StrEnum):
    WALL_CLOCK = "wall_clock"      # E1
    STEP_BUDGET = "step_budget"    # E2
    PARK = "park"                  # E3
    SIGNAL = "signal"              # E4
    TERMINAL = "terminal"          # the run finished
    SUPERSEDED = "superseded"      # we lost the lease; wrote nothing
    NOT_STARTED = "not_started"    # lost the claim race


@dataclass(frozen=True)
class EpisodeOutcome:
    run_id: RunId
    exit: ExitCondition
    steps_taken: int               # Ch 34's steps-per-episode metric
    duration_ms: int
    checkpoints: int               # must equal steps_taken
    final_version: int | None      # None when SUPERSEDED
    cost_cents: int
```

### Chapter 20 — The Self-Evolving Runtime (AHE) — Overview

```python
from dataclasses import dataclass
from enum import StrEnum


class ConstraintLevel(StrEnum):
    MIDDLEWARE = "middleware"      # compels
    TOOL_IMPL = "tool_impl"        # compels
    SUB_AGENT = "sub_agent"        # structural
    TOOL_DESC = "tool_desc"        # asks, but shapes perception
    SKILL = "skill"                # asks, on demand
    MEMORY = "memory"              # asks, with evidence
    PROMPT = "prompt"              # asks, weakest (AHE 4.4.1)


class Verdict(StrEnum):
    KEEP = "keep"
    IMPROVE = "improve"
    ROLLBACK_AND_PIVOT = "rollback_and_pivot"


@dataclass(frozen=True)
class ChangeEntry:
    change_id: str                      # chg-<n>, scoped to an iteration
    component: ConstraintLevel
    path: str
    failure_evidence: tuple[str, ...]   # task + step references
    root_cause: str
    targeted_fix: str
    predicted_fixes: tuple[str, ...]    # task ids -- the CLAIM
    at_risk: tuple[str, ...]            # task ids -- the honest half
    commit_sha: str


@dataclass(frozen=True)
class IterationReport:
    version: HarnessVersion
    score: float
    cost_per_task_cents: int            # section 5.4: not optional
    verdicts: Mapping[str, Verdict]
    fix_prediction_precision: float     # ~5x random (AHE 4.4.2)
    regression_prediction_precision: float   # ~2x random
```

### Chapter 21 — Durable Execution

```python
from dataclasses import dataclass
from enum import StrEnum


class ActivityState(StrEnum):
    PENDING = "pending"
    CLAIMED = "claimed"
    RECORDED = "recorded"      # terminal
    DEAD = "dead"


class ExecutionMode(StrEnum):
    """The vocabulary the cold open lacked (section 2.3)."""
    RESUME = "resume"          # continue; reuse by identity
    RERUN = "rerun"            # new run, new ids, effects repeat
    REPLAY = "replay"          # execute NOTHING (Ch 40)


@dataclass(frozen=True)
class LedgerEntry:
    activity_id: ActivityId
    state: ActivityState
    result: ToolResult | None
    attempts: int
    cost_cents: int
    effect_log: tuple[EffectRecord, ...]   # what actually changed
    first_attempted_at: datetime
    recorded_at: datetime | None


@dataclass(frozen=True)
class PartialMatch:
    """Same run and position, different plan or inputs. An anomaly."""
    expected_id: ActivityId
    found_id: ActivityId
    differing_field: str        # plan_id | input_digest
```

### Chapter 22 — The Event Spine: Outbox, Relay, Command Port

```python
from dataclasses import dataclass
from enum import StrEnum


class OutboxState(StrEnum):
    PENDING = "pending"
    CLAIMED = "claimed"
    PROCESSED = "processed"    # terminal
    DEAD = "dead"              # poisoned; queryable and replayable


@dataclass(frozen=True)
class Event:
    """Past tense, addressed to nobody, cannot be refused."""
    event_type: str            # <domain>.<noun>.<past_verb>
    payload: Mapping[str, object]
    occurred_at: datetime


@dataclass(frozen=True)
class Command:
    """Imperative, addressed to one handler, may be refused."""
    command_type: str          # cmd.<domain>.<imperative_verb>
    payload: Mapping[str, object]
    idempotency_key: str       # <command>:<scope>:<digest>
    reply_with: str            # the event type expected back


@dataclass(frozen=True)
class OutboxRow:
    id: int
    event_type: str
    partition_key: str         # ordering within this, and no wider
    payload: Mapping[str, object]
    attempts: int
    claimed_until: datetime | None
```

### Chapter 23 — The Scheduler: Queues, Work Classes, Admission

```python
from dataclasses import dataclass
from enum import StrEnum


class WorkClass(StrEnum):
    INTERACTIVE = "interactive"   # a person is waiting
    STANDARD = "standard"         # the default
    BULK = "bulk"                 # batch, cost-tolerant


class AdmissionOutcome(StrEnum):
    ADMIT = "admit"
    DEFER = "defer"               # visible; resolves on capacity
    REFUSE = "refuse"             # waiting will not help


@dataclass(frozen=True)
class ClassReservation:
    work_class: WorkClass
    reserved_workers: int
    may_spill_to: tuple[WorkClass, ...]   # INTERACTIVE spills nowhere


@dataclass(frozen=True)
class AdmissionDecision:
    outcome: AdmissionOutcome
    reason: str | None            # required on REFUSE and DEFER
    queue_position: int | None    # required on DEFER (section 5.5)
    estimated_start: datetime | None


@dataclass(frozen=True)
class SchedulerPressure:
    """What §13.1 dashboards. Which bound binds is the headline."""
    binding_resource: str
    workers_idle_reserved: int    # the cost of reservations (4.1)
    queued_by_class: Mapping[WorkClass, int]
    deferred_by_tenant: Mapping[str, int]
    oldest_queued_age_ms: int
```

### Chapter 24 — The Task Graph

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

### Chapter 25 — The World Model

```python
from dataclasses import dataclass
from enum import Enum


class BeliefStatus(str, Enum):
    FRESH = "fresh"
    SUSPECT = "suspect"
    STALE = "stale"


@dataclass(frozen=True)
class Belief:
    probe_name: str              # provenance: how to re-derive
    claim: dict                  # the fact itself
    scope: str                   # what it covers; drives invalidation
    observed_at_seq: int         # event-log position, not wall clock
    observed_at: str             # wall clock, for humans only
    status: BeliefStatus
    max_age_s: int | None        # backstop, never the primary rule
```

### Chapter 26 — Planning Algorithms

```python
from dataclasses import dataclass
from enum import Enum


class Response(str, Enum):
    RETRY = "retry"
    REPAIR = "repair"
    REPLAN = "replan"
    FAIL_RUN = "fail_run"


@dataclass(frozen=True)
class Contract:
    """A checkable postcondition, written at plan time."""
    check: str            # a deterministic command or predicate
    description: str      # for humans reviewing the plan
    # No model_judged field. If it needs a model, it is not a
    # contract -- see C28 for what a model judgment may do.


@dataclass(frozen=True)
class FailureRecord:
    node_id: str
    plan_id: str
    contract: Contract | None      # None if the tool never produced output
    observation_ref: str           # pointer into the trace store (C16)
    error_class: str               # transient | asserted | structural
    attempt: int


@dataclass(frozen=True)
class Lineage:
    lineage_id: str
    goal_hash: str        # every plan in a lineage shares this
    plans: tuple[str, ...]         # ordered, oldest first
    repairs_by_contract: dict[str, int]   # drives the 5.5 guard
```

### Chapter 27 — Failure, Recovery, and Rollback

```python
from dataclasses import dataclass
from enum import Enum


class Tier(int, Enum):
    OWNED = 1          # rollback: restore the kept prior version
    COMPENSABLE = 2    # compensation: a new forward action
    ESCAPED = 3        # nothing exists


class EffectState(str, Enum):
    APPLIED = "applied"
    REVERSED = "reversed"        # the system reversed it
    OUTSTANDING = "outstanding"  # unreversed, owed to a person
    RESOLVED = "resolved"        # a person handled it (see 7.1)
    ESCAPED = "escaped"          # tier 3; terminal on arrival


@dataclass(frozen=True)
class AppliedEffect:
    effect_id: str
    run_id: str
    node_id: str
    identity: str                # C21 activity identity
    tool: str
    tier: Tier
    compensation: str | None     # tool name; required when tier is 2
    compensation_args: dict      # bound at APPLY time, not at reverse
    state: EffectState
    applied_at_seq: int


@dataclass(frozen=True)
class Obligation:
    """A dead-letter row. Written for a person to read."""
    should_be_true: str
    is_true: str
    applied_by: str              # run, node, timestamp
    reversal: str | None         # what would fix it, if anything
    owner: str                   # a team, never a person's name
    raised_at: str
```

### Chapter 29 — Long-Running Agents

```python
from dataclasses import dataclass
from enum import Enum


class BudgetAxis(str, Enum):
    TOKENS = "tokens"
    WALL_CLOCK = "wall_clock"
    STEPS = "steps"


@dataclass(frozen=True)
class Allocation:
    per_phase: dict[str, float]      # fractions, summing with reserves to 1
    compensation_reserve: float      # unspendable by ordinary work (C27)
    finish_reserve: float            # sized from terminal node costs
    point_of_no_return: float        # fraction of wall clock


@dataclass(frozen=True)
class Novelty:
    state_hash: str
    is_novel: bool
    effectful: bool                  # only these count toward the window
    seen_at_step: int | None         # when this state was last visited


@dataclass(frozen=True)
class Stall:
    run_id: str
    window_steps: int
    distinct_states: int             # 2 in the cold open
    repeated_artefacts: tuple[str, ...]   # "exporters.py"
    detected_at_step: int
    lineage_stall_count: int         # drives the 5.2 escalation
```

### Chapter 30 — Human Authority

```python
from dataclasses import dataclass
from enum import Enum


class DecisionKind(str, Enum):
    APPROVE = "approve"
    STEER = "steer"
    CANCEL = "cancel"
    OVERRIDE = "override"


class GateState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    OVERRIDDEN = "overridden"
    ABANDONED = "abandoned"
    EXPIRED = "expired"
    CONSUMED = "consumed"


@dataclass(frozen=True)
class GateRequest:
    gate_request_id: str
    run_id: str
    node_id: str
    tool: str
    arg_hash: str              # H(tool, canonical_args, run_id)
    args_rendered: str         # what the HUMAN sees; see below
    tier: int
    env: str
    state: GateState
    expires_at: str


@dataclass(frozen=True)
class Decision:
    decision_id: str
    gate_request_id: str
    kind: DecisionKind
    owner: str                 # a role: "platform-oncall"
    reason: str
    scope_arg_hash: str        # never widens
    expires_at: str
    recorded_at_seq: int       # event-log position, not wall clock
```

### Chapter 34 — Observability

```python
from dataclasses import dataclass
from enum import Enum


class Flow(str, Enum):
    CONTROL = "control"
    DATA = "data"
    EVENT = "event"


@dataclass(frozen=True)
class Span:
    span_id: str
    parent_id: str | None
    name: str
    flow: Flow                  # C9, section 4.1 -- one enum, large payoff
    surface: str | None         # C33: which capacity surface
    tenant: str
    started_at_seq: int         # event-log position, not wall clock
    duration_ms: float
    queue_ms: float             # SEPARATE from duration (C33 sec 7.1)
    attributes: dict            # unbounded here, and only here


@dataclass(frozen=True)
class Retention:
    keep: bool
    reason: str                 # which always-keep category, or "sampled"
    expires_at: str | None      # from C41's needs, not from disk cost
    redacted_at_capture: bool   # must be True to be retained (7)


@dataclass(frozen=True)
class IdentityAnomaly:
    kind: str                   # "same_identity_two_outcomes"
                                # | "two_identities_same_inputs"
                                # | "identity_without_outcome"
    identity: str
    run_ids: tuple[str, ...]
    detected_at_seq: int
```

### Chapter 37 — Tenancy, Secrets, and Data Governance

```python
from dataclasses import dataclass
from enum import Enum


class Classification(str, Enum):
    VERBATIM = "verbatim"        # file bodies, issue text, model output
    STRUCTURAL = "structural"    # tool names, order, verdicts, cost
    OPERATIONAL = "operational"  # decisions, obligations, audit


@dataclass(frozen=True)
class TenantKey:
    """Required to WRITE. Not applied as a read filter (2.2 step 6).

    A forgotten read filter returns other tenants' data. A missing
    write key makes the row unwritable, which fails in development.
    """
    tenant: str


@dataclass(frozen=True)
class BeliefCacheKey:
    """C25 shares expensive probes by (repo, commit). The tenant is
    part of the key ANYWAY -- a shared dependency, a public
    repository, or a fork produces the same commit across tenants,
    and the sharing key then crosses the boundary silently (5.2)."""
    tenant: str
    repo: str
    commit_sha: str


@dataclass(frozen=True)
class DeletionCertificate:
    tenant: str
    per_store: dict[str, str]     # "deleted: 1204" | "retained: ..."
                                  # | "flagged: 3 golden cases"
    stores_enumerated: int
    stores_registered: int        # MUST be equal to the above
    issued_at: str
```

### Chapter 40 — Testing a Non-Deterministic System

```python
from dataclasses import dataclass
from enum import Enum


class Tier(int, Enum):
    DETERMINISTIC = 1
    REPLAY = 2
    STATISTICAL = 3        # not in CI; C41 owns it


class ReplayOutcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    DIVERGED = "diverged"  # distinct, always (5.3)


@dataclass(frozen=True)
class Recording:
    fixture_id: str
    triple: "VersionTriple"      # C38: fixtures age with the harness
    turns: tuple[dict, ...]      # model responses, in order
    source_run_id: str           # provenance back to the real run
    category: str                # "failure" | "stall" | "override" ...


@dataclass(frozen=True)
class ExpectedCall:
    port: str                    # "tool" | "model" | "store"
    method: str
    args_matcher: dict           # structural, never on generated text
    must_precede: tuple[str, ...]   # ordering assertions (4.1)
```

### Chapter 47 — Attribution, Verdicts, and Rollback

```python
from dataclasses import dataclass
from enum import StrEnum


class Verdict(StrEnum):
    KEEP = "keep"
    IMPROVE = "improve"
    ROLLBACK_AND_PIVOT = "rollback_and_pivot"
    UNDETERMINED = "undetermined"      # this chapter's addition


@dataclass(frozen=True)
class Attribution:
    """One entry's result. Carries its conditions, or it is not
    comparable with any other (7.2)."""
    change_id: str
    fixed: tuple[str, ...]             # predicted n improved
    missed: tuple[str, ...]
    broke: tuple[str, ...]             # at_risk n regressed
    surprise: tuple[str, ...]          # regressed, NOT flagged --
                                       # the production measure of
                                       # AHE 4.4.2's weakness
    predicted_width: int               # C45 sec 5.3; 3-of-3 and
                                       # 3-of-14 are different
    at_risk_width: int
    floor: "Floor"                     # embedded, not referenced
    corpus_version_before: str
    corpus_version_after: str
    pattern_shrank: bool | None        # None when the entry named
                                       # no pattern
    collided_with: tuple[str, ...]     # the field most likely to
                                       # be dropped, and the only
                                       # record that another edit
                                       # could explain this (7.2)
    verdict: Verdict


@dataclass(frozen=True)
class RollbackRecord:
    change_id: str
    reverted_commit: str
    reason: Verdict
    entry_marked: bool                 # never deleted (7.1)
    affected_runs_query: str           # C39 sec 5.4: what shipped
                                       # under the reverted hash,
                                       # queryable because C38
                                       # recorded the triple
```

### Chapter 49 — Continuous Improvement and Governance

```python
from dataclasses import dataclass
from enum import StrEnum


class AutonomyLevel(StrEnum):
    PROPOSES_ONLY = "proposes_only"
    AUTO_PROMOTE_SCOPED = "auto_promote_scoped"
    AUTO_PROMOTE = "auto_promote"


@dataclass(frozen=True)
class ScanEntry:
    number: int                      # fixed order (5.1)
    name: str
    value: float
    in_band: bool
    catches: str                     # the failure, named in the
                                     # report. An entry that cannot
                                     # fill this does not belong
    source_chapter: str
    routes_to: str | None            # a gate, or None -- the scan
                                     # does not decide (3.1)


@dataclass(frozen=True)
class ScanReport:
    week: str
    entries: tuple[ScanEntry, ...]
    computed_at: str                 # BEFORE the meeting
    out_of_band: tuple[int, ...]


@dataclass(frozen=True)
class GateDecision:
    gate: str                        # promotion | relaxation | scope
    request_id: str
    owner: str                       # named; Gate 2's is outside
                                     # the loop's reporting line
    granted: bool
    rationale: str                   # recorded, because a later
                                     # reader cannot tell a
                                     # considered decision from an
                                     # expedient one (C46 sec 7)
    made_during_iteration: bool       # Gate 2: must be False
                                      # (C46 sec 5.7 step 5)


@dataclass(frozen=True)
class AccessRecord:
    reader: str                      # "distiller" is a reader
    trajectory_id: str
    tenant_id: str
    partition: str                   # structural | verbatim
    at: str
```
