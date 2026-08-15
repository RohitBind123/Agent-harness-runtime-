# Appendix E — Port Signatures

> **Generated file. Do not edit by hand.**
>
> Assembled from the chapters by `tools/build_appendices.py`. To change an
> entry, edit the chapter it comes from and regenerate.

Every `Protocol` the handbook defines, from the *Internal APIs* section of each chapter. A port is an extension point you implement; the handbook uses `typing.Protocol` rather than ABCs throughout, and a signature without type hints is not a contract.

The docstrings are load-bearing. Several ports carry their design argument there — why a method raises rather than warns, why an update method is absent — and those are reproduced in full below.

109 ports across 84 chapters.

---

## Index

| Port | Chapter | Methods | Purpose |
|---|---|---|---|
| `RunLifecyclePort` | [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | `async create`, `async claim`, `async checkpoint`, `async release` | Transitions on the run's clock |
| `RuntimeLifecyclePort` | [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | `async boot`, `async serve`, `async drain` | Transitions on the process's clock |
| `SweeperPort` | [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | `async sweep` | Belongs to neither lifecycle |
| `ControlEdge` | [Ch 9](../chapters/09-three-flows-data-control-event.md) | `async decide` | Control flow: a decision, returning what happens next |
| `DataEdge` | [Ch 9](../chapters/09-three-flows-data-control-event.md) | `async transfer` | Data flow: movement, sized and bounded |
| `EventEdge` | [Ch 9](../chapters/09-three-flows-data-control-event.md) | `async append` | Event flow: durability |
| `PlannerPort` | [Ch 10](../chapters/10-the-planner.md) | `async plan`, `async should_replan` | Proposes |
| `ContextPort` | [Ch 11](../chapters/11-the-context-system.md) | `async assemble`, `budget_for` | Assembles model state for one call |
| `ContextSourcePort` | [Ch 11](../chapters/11-the-context-system.md) | `async candidates` | One contributor of material |
| `MemoryPort` | [Ch 12](../chapters/12-the-memory-system.md) | `async view`, `async body`, `async propose`, `async curate` | Long-term memory |
| `ModelPort` | [Ch 13](../chapters/13-the-reasoning-engine.md) | `async complete`, `async stream`, `abort` | The only way to call a model |
| `ProviderAdapter` | [Ch 13](../chapters/13-the-reasoning-engine.md) | `async invoke`, `normalise_error`, `token_usage` | One per provider |
| `ToolPort` | [Ch 14](../chapters/14-the-tool-execution-engine.md) | `async dispatch` | One dispatch |
| `ToolRegistry` | [Ch 14](../chapters/14-the-tool-execution-engine.md) | `resolve`, `descriptions_for` | The single source for what a tool IS |
| `ToolMiddleware` | [Ch 14](../chapters/14-the-tool-execution-engine.md) | `async around` | Wraps every invocation |
| `ToolDescription` | [Ch 15](../chapters/15-agent-computer-interface-design.md) | — | The prose surface |
| `ArgumentSpec` | [Ch 15](../chapters/15-agent-computer-interface-design.md) | — | ARGUMENTS |
| `ToolError` | [Ch 15](../chapters/15-agent-computer-interface-design.md) | `render` | ERRORS |
| `ObservationPort` | [Ch 16](../chapters/16-the-observation-system.md) | `observe`, `metric`, `async seal` | Capture |
| `RedactionPort` | [Ch 16](../chapters/16-the-observation-system.md) | `redact` | Rules owned by Ch 37, applied here |
| `TrajectoryReader` | [Ch 16](../chapters/16-the-observation-system.md) | `async open`, `async search` | The consumer side: Ch 15's review, Ch 41's evaluation, Ch 44's |
| `StatePort` | [Ch 17](../chapters/17-the-state-manager.md) | `async claim`, `async checkpoint`, `async release`, `async sweep` | Ownership and progress |
| `RunDriver` | [Ch 18](../chapters/18-the-runtime-loop.md) | `async drive_episode` | The loop |
| `DelegationPort` | [Ch 19](../chapters/19-the-multi-agent-runtime.md) | `async delegate`, `async marshal` | Sub-agents |
| `SubAgentRegistry` | [Ch 19](../chapters/19-the-multi-agent-runtime.md) | `resolve` | sub_agents/<name>/agent.yaml -- a harness component (Ch 43), |
| `EvolveLoopPort` | [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | `async iterate` | One iteration of Algorithm 1 |
| `ManifestPort` | [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | `async record`, `async verdicts_for` | The change manifest |
| `ActivityLedger` | [Ch 21](../chapters/21-durable-execution.md) | `async lookup`, `async claim`, `async record`, `async report_partial_match` | Bounds repetition |
| `OutboxPort` | [Ch 22](../chapters/22-the-event-spine.md) | `async append` | The durability boundary |
| `RelayPort` | [Ch 22](../chapters/22-the-event-spine.md) | `async claim_batch`, `async ack`, `async fail` | Claims rows, never a cursor (section 5.3) |
| `CommandPort` | [Ch 22](../chapters/22-the-event-spine.md) | `async send` | The downward half of Ch 4's waist |
| `AdmissionPort` | [Ch 23](../chapters/23-the-scheduler.md) | `async evaluate` | Decides at the door |
| `SchedulerPort` | [Ch 23](../chapters/23-the-scheduler.md) | `async classify`, `async claim_for_slot` | Once, at admission |
| `ResourceBounds` | [Ch 23](../chapters/23-the-scheduler.md) | `binding_resource` | Three, not one (section 5.4) |
| `TaskGraphStore` | [Ch 24](../chapters/24-the-task-graph.md) | `mint`, `ready_nodes`, `claim`, `complete` | Durable storage for a minted plan's nodes, edges, and joins |
| `Probe` | [Ch 25](../chapters/25-the-world-model.md) | `run` | A named, costed, read-only query against the environment |
| `WorldModel` | [Ch 25](../chapters/25-the-world-model.md) | `get`, `invalidate`, `contradict` | Return a FRESH belief, or None |
| `Planner` | [Ch 26](../chapters/26-planning-algorithms.md) | `plan`, `repair` | Produce a candidate graph |
| `FailureClassifier` | [Ch 26](../chapters/26-planning-algorithms.md) | `classify` | Returns FAIL_RUN when a replan would carry no information the previous one did not have |
| `EffectLedger` | [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | `record`, `outstanding` | Append an applied effect |
| `RecoveryDriver` | [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | `recover` | Walk the ledger newest-first and discharge each effect according to its tier |
| `DeadLetterStore` | [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | `raise_` | File work that cannot proceed and must not be forgotten |
| `CheckRunner` | [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | `run` | Evaluate every contract deterministically and return the floor |
| `Judge` | [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | `judge` | Assess the artefact against the goal |
| `ProgressDetector` | [Ch 29](../chapters/29-long-running-agents.md) | `observe`, `is_stalled` | Called after EVERY step |
| `BudgetGovernor` | [Ch 29](../chapters/29-long-running-agents.md) | `allocate`, `may_start_new_work`, `exhausted` | Phase caps plus reserves, derived from the graph's shape at admission |
| `GatePolicy` | [Ch 30](../chapters/30-human-authority.md) | `required` | PURE |
| `DecisionStore` | [Ch 30](../chapters/30-human-authority.md) | `lookup`, `record` | Append-only |
| `ParkManager` | [Ch 30](../chapters/30-human-authority.md) | `park` | Transition the run to `parked` and release EVERYTHING: lease, semaphore slot, worker, connection |
| `ProvenanceTagger` | [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | `tag`, `derive` | Label at FETCH time, before any model sees the bytes |
| `CapabilityBroker` | [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | `issue` | Issue a credential scoped to what the NODE declared at mint time, expiring with the step |
| `EgressPolicy` | [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | `permitted` | Allowlist per step, derived from declared needs |
| `LeaseStore` | [Ch 32](../chapters/32-distributed-execution.md) | `claim`, `renew` | One statement |
| `EffectGateway` | [Ch 32](../chapters/32-distributed-execution.md) | `execute` | Requires the handle |
| `ServiceTimeMeter` | [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | `record`, `percentiles` | Record a hold and the wait that preceded it, SEPARATELY |
| `CapacitySizer` | [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | `required`, `binding_surface` | Little's Law: arrival rate x service time |
| `CommitmentEstimator` | [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | `commitment` | Expected holds per surface over the run's whole lifetime, derived from the graph at mint time (C24) |
| `MetricEmitter` | [Ch 34](../chapters/34-observability.md) | `observe` | Record a measurement |
| `TraceSink` | [Ch 34](../chapters/34-observability.md) | `span`, `finalise` | High-cardinality by design |
| `AnomalyDetector` | [Ch 34](../chapters/34-observability.md) | `identity_partial_match` | PAGE |
| `CostEstimator` | [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | `estimate` | Input tokens are COUNTED, not estimated -- the context has already been assembled |
| `BudgetLedger` | [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | `reserve`, `settle` | Hold against `available = limit - spent - reserved` |
| `CostAttribution` | [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | `record` | Five tags: run, tenant, step type, model, cached fraction |
| `SLIComputer` | [Ch 36](../chapters/36-reliability-and-slos.md) | `sli` | Compute a deterministic ratio over a window |
| `ErrorBudget` | [Ch 36](../chapters/36-reliability-and-slos.md) | `burn_rate` | Rate, not remaining balance |
| `DegradationController` | [Ch 36](../chapters/36-reliability-and-slos.md) | `degrade`, `degrade_with_disclosure` | Rungs 1-3 preserve the honesty promise: the caller knows what they are getting |
| `StoreRegistration` | [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | `delete_tenant` | Every store declares these |
| `CaptureRedactor` | [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | `redact` | Runs BEFORE the write, over ALL captured material: tool arguments, tool output, error text, and file content |
| `DeletionExecutor` | [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | `execute` | Enumerate the REGISTRY, not a list |
| `ConfigResolver` | [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | `resolve` | Resolve defaults, file, environment, and overrides ONCE at run start, hash the RESULT, and freeze it for the run's life |
| `InvalidationRegister` | [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | `declare`, `stale` | Register a tuned number with the model it was measured against |
| `ModelPin` | [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | `resolve`, `days_until_withdrawal` | An exact version |
| `BlastRadiusLinter` | [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | `required_slices` | Map changed files to the benchmark slices that must run |
| `RegressionHarness` | [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | `run` | Gate 1 |
| `EvaluationRunner` | [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | `evaluate` | — |
| `ShadowRunner` | [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | `compare` | Run both on IDENTICAL inputs and stop before the first effectful step (C14's tag says where; C27's tiers say what would have happened past it) |
| `Clock` | [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | `monotonic`, `wall` | A port, injected |
| `ScriptedPort` | [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | `expect` | A fake that asserts its call sequence, not merely its |
| `ReplayHarness` | [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | `load`, `serve` | A real trajectory from C34's trace store: real model behaviour, deterministic execution |
| `NoiseFloorEstimator` | [Ch 41](../chapters/41-evaluation-infrastructure.md) | `measure`, `current` | Run the UNCHANGED harness k times over the corpus and report the spread, PER SLICE |
| `EvaluationRunner` | [Ch 41](../chapters/41-evaluation-infrastructure.md) | `evaluate` | — |
| `CorpusManager` | [Ch 41](../chapters/41-evaluation-infrastructure.md) | `retire`, `drift` | Retire and replace |
| `FitDecayMeter` | [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | `standing_advantage`, `carried_advantage` | Makes the cold open's measurement a routine operation rather |
| `RefitLedger` | [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | `record`, `step_shares` | Where a re-fit's days went, so sec 4's ratio is measured |
| `EvolutionReadiness` | [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | `check` | The sec 5.6 table, as a check that can block rather than a |
| `ComponentRegistry` | [Ch 43](../chapters/43-component-observability.md) | `resolve`, `inventory`, `validate` | The only way anything asks what the harness is made of |
| `OverlapDetector` | [Ch 43](../chapters/43-component-observability.md) | `declared`, `async probe` | Two components claiming the same behaviour tag |
| `SeedPolicy` | [Ch 43](../chapters/43-component-observability.md) | `seed_version`, `is_protected` | The tagged origin of the measurement space (5.6) |
| `Distiller` | [Ch 44](../chapters/44-experience-observability.md) | `async distil` | Ten million tokens in, ten thousand out, with every claim |
| `PerTaskAnalyser` | [Ch 44](../chapters/44-experience-observability.md) | `async analyse` | One trajectory in, one fixed-field analysis out |
| `EvidenceCorpus` | [Ch 44](../chapters/44-experience-observability.md) | `overview`, `analyses_for`, `async follow`, `describes` | A directory, read progressively |
| `EntryGate` | [Ch 45](../chapters/45-decision-observability.md) | `propose`, `seal` | The only path into the manifest |
| `SharpnessValidator` | [Ch 45](../chapters/45-decision-observability.md) | `check` | Task ids that EXIST in the corpus, or refuse |
| `EvidenceNoveltyChecker` | [Ch 45](../chapters/45-decision-observability.md) | `novel` | False (with the prior entry id) when EVERY pointer has been cited before -- a proposal storm (5.1) |
| `Ledger` | [Ch 45](../chapters/45-decision-observability.md) | `precision_and_width`, `level_distribution`, `repeated_level_for_cause` | Queries over the manifest |
| `WriteScope` | [Ch 46](../chapters/46-the-evolve-agent.md) | `permits`, `contains` | Enumerated paths, not a description |
| `Router` | [Ch 46](../chapters/46-the-evolve-agent.md) | `route` | C43 sec 5.3's chain |
| `LevelSelector` | [Ch 46](../chapters/46-the-evolve-agent.md) | `choose` | The weakest level that can enforce it (C1 sec 5.2) |
| `ContainmentPolicy` | [Ch 46](../chapters/46-the-evolve-agent.md) | `entries`, `record_contest` | Read by the agent, written only by a human through C49 |
| `Attributor` | [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | `attribute`, `collisions` | — |
| `VerdictAssigner` | [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | `assign` | Four values |
| `RollbackExecutor` | [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | `async revert` | File-level revert in the workspace (C39) |
| `SliceGate` | [Ch 48](../chapters/48-limits.md) | `blocks` | The fixable limit, as a check |
| `InterferenceEstimator` | [Ch 48](../chapters/48-limits.md) | `expected_combined` | Given single-component gains, what should the combination deliver? |
| `ResidueSweeper` | [Ch 48](../chapters/48-limits.md) | `async sweep` | The only mechanism in Level 5 that makes the harness |
| `ReviewScan` | [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | `compute`, `unused_entries` | Computed before the meeting, in fixed order |
| `Gate` | [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | `decide`, `refusal_rate` | Three of them, and no more (2.3) |
| `AccessAudit` | [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | `reads` | Who read which trajectory, INCLUDING machine readers |
| `AutonomyPolicy` | [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | `level`, `conditions_met`, `demote_on` | Every condition is a MEASUREMENT, never a judgment |

---

## Definitions

### Chapter 8 — Request Lifecycle and Runtime Lifecycle

```python
from typing import Protocol
from datetime import datetime, timedelta


class RunLifecyclePort(Protocol):
    """Transitions on the run's clock. Every method is idempotent and
    every mutation carries a version for CAS."""

    async def create(self, goal: Goal, tenant_id: str) -> RunId: ...

    async def claim(
        self,
        worker_id: str,
        lease: timedelta,
        work_class: str | None = None,
    ) -> ClaimedRun | None:
        """Compare-and-swap a lease onto one eligible run.

        Returns None when no run is available or another worker won the
        race. A lost race is a normal outcome, never an error.
        """

    async def checkpoint(
        self,
        run_id: RunId,
        expected_version: int,
        state: RunState,
        renew_lease_for: timedelta,
    ) -> CheckpointResult:
        """Persist progress, renew the lease, and read pending signals
        in one transaction. Fails closed if expected_version is stale:
        another worker is driving and this one must stop."""

    async def release(
        self,
        run_id: RunId,
        expected_version: int,
        requeue: bool,
    ) -> None: ...


class RuntimeLifecyclePort(Protocol):
    """Transitions on the process's clock. Nothing here may mutate run
    state except drain, which releases and re-enqueues only."""

    async def boot(self) -> None: ...
    async def serve(self) -> None: ...
    async def drain(self, budget: timedelta) -> DrainReport: ...


class SweeperPort(Protocol):
    """Belongs to neither lifecycle. Triggered by elapsed time alone.
    Safe to run concurrently in every worker."""

    async def sweep(self, now: datetime) -> SweepReport: ...
```

### Chapter 9 — Three Flows: Data, Control, Event

```python
from typing import Protocol


class ControlEdge(Protocol):
    """Control flow: a decision, returning what happens next.
    Small payloads, high consequence, always synchronous."""

    async def decide(self, run: ClaimedRun, context: Context) -> Decision: ...


class DataEdge(Protocol):
    """Data flow: movement, sized and bounded. Every implementation
    declares a ceiling, because an unbounded one is Ch 14's failure."""

    max_bytes: int

    async def transfer(self, payload: bytes) -> TransferResult: ...


class EventEdge(Protocol):
    """Event flow: durability. The transaction parameter is not
    optional -- an event written outside its state change's transaction
    is the gap of section 5.2."""

    async def append(self, event: Event, txn: Transaction) -> None: ...
```

### Chapter 10 — The Planner

```python
from typing import Protocol


class PlannerPort(Protocol):
    """Proposes. Never executes, authorises, grades, or writes run state.

    Implementations are pure with respect to the runtime: given the same
    PlanRequest and the same model responses, they produce the same Plan.
    That is what makes Ch 40's hermetic replay possible.
    """

    async def plan(self, request: PlanRequest) -> Plan:
        """Produce a fresh plan for a goal, or a re-plan after a change.

        Always returns a NEW Plan with a new plan_id. There is
        deliberately no `revise` method: the absence is the contract.
        """

    async def should_replan(
        self,
        plan: Plan,
        completed: StepResult,
    ) -> ReplanDecision:
        """Decide whether the current plan still holds after a result.

        Cheap and usually deterministic: most results do not warrant a
        model call. An implementation that calls the model here on every
        step has turned an N-step plan into N one-step plans (section 12.2).
        """
```

### Chapter 11 — The Context System

```python
from typing import Protocol


class ContextPort(Protocol):
    """Assembles model state for one call. Reads five sources, writes
    nothing, and returns a frozen value with its accounting attached.

    Pure with respect to the runtime: same request plus same sources
    produces a byte-identical Context. That is what lets Ch 40 replay
    a run hermetically and Ch 44 reconstruct what the model saw.
    """

    async def assemble(self, request: AssemblyRequest) -> Context:
        """Build the context for one step.

        Raises ContextVerificationError if the stable prefix differs
        from the previous call in this run (section 6.1), or
        ContextExhausted if it cannot fit after condensing (E2).

        There is deliberately no `append` and no `mutate`: a Context is
        produced whole or not at all.
        """

    def budget_for(self, run: ClaimedRun) -> Budget:
        """The working budget after fixed costs. Cheap, synchronous,
        and callable by the planner so it can size a plan against what
        will actually fit (Ch 10 section 11, plan-longer-than-budget)."""


class ContextSourcePort(Protocol):
    """One contributor of material. Every source declares its share, so
    adding a source means explicitly taking budget from another
    (section 5.6)."""

    name: str
    volatility: Volatility          # STABLE | SEMI_STABLE | VOLATILE
    budget_share: float             # of the working budget; sums to 1.0

    async def candidates(self, request: AssemblyRequest) -> list[Candidate]: ...
```

### Chapter 12 — The Memory System

```python
from typing import Protocol


class MemoryPort(Protocol):
    """Long-term memory. A context source on the read side, and the only
    harness component with a write path reachable from inside a run.

    The read path is called on every model call and must stay trivial.
    The write path is called once, at run end, off the critical path.
    """

    async def view(self, scopes: Sequence[Scope], budget: int) -> MemoryView:
        """Headings for every ACTIVE entry in scope, within budget.

        Bodies are NOT included; the model retrieves them with a tool
        call (Ch 11 progressive disclosure). Entries below the load
        floor are excluded here, not filtered later.
        """

    async def body(self, entry_id: EntryId) -> str: ...

    async def propose(self, proposal: MemoryProposal) -> ProposalOutcome:
        """Submit an observation for possible storage.

        Never raises into the run: a failure here is a missed
        improvement, and must not fail a completed run (section 4.1).
        The outcome records which of new / reinforces / contradicts /
        duplicate / rejected applied, and why.
        """

    async def curate(self, now: datetime) -> CurationReport:
        """Periodic, not per run. Decays unconfirmed entries, retires
        those below the floor, and reports when the file exceeds its
        Ch 11 budget share. Never deletes."""
```

### Chapter 13 — The Reasoning Engine

```python
from typing import Protocol, AsyncIterator


class ModelPort(Protocol):
    """The only way to call a model. Metered, capped, abortable, opaque.

    No method takes a provider name, a provider parameter, or a raw
    prompt string. Callers pass a Context (Ch 11) and a policy id; the
    port resolves everything else from the pinned harness version.
    """

    async def complete(
        self,
        call_id: CallId,
        context: Context,
        policy: PolicyId,
    ) -> Completion:
        """Make one call.

        Raises BudgetRefused before making any request when the
        reservation cannot be taken -- the caller parks (section 5.3).
        Raises ModelAborted if the call was abandoned; the exception
        carries the settled amount and whether actual usage is known.
        Raises ModelRefused on a content refusal, which is NOT retried.
        """

    async def stream(
        self,
        call_id: CallId,
        context: Context,
        policy: PolicyId,
    ) -> AsyncIterator[Chunk]:
        """As complete(), but abandonment stops generation physically
        rather than only locally (section 5.4). Prefer this wherever the
        caller can consume it."""

    def abort(self, call_id: CallId) -> None:
        """Fire the abort handle for an in-flight call.

        Synchronous, non-blocking, and BEST EFFORT: it makes no promise
        that the provider stops, and the accounting assumes it did not.
        Safe to call for an unknown or finished call_id.
        """


class ProviderAdapter(Protocol):
    """One per provider. The only place a provider SDK is imported, and
    the only place its vocabulary exists."""

    async def invoke(self, request: ProviderRequest) -> ProviderResponse: ...
    def normalise_error(self, exc: Exception) -> ModelError: ...
    def token_usage(self, response: ProviderResponse) -> TokenUsage:
        """Fields the provider does not report must be None, never 0
        (Ch 6: missing is not zero)."""
```

### Chapter 14 — The Tool Execution Engine

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

### Chapter 15 — Agent-Computer Interface Design

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

### Chapter 16 — The Observation System

```python
from typing import Protocol


class ObservationPort(Protocol):
    """Capture. Never fails a run; never writes a fact.

    Every method is fire-and-forget by contract: implementations
    buffer and return, and a store outage drops spans rather than
    raising (section 4.1).
    """

    def observe(self, envelope: Envelope, payload: SpanPayload) -> None:
        """Record one span. Synchronous, non-blocking, never raises.

        The envelope carries harness_version, which is what makes any
        later question about what the model saw answerable at all.
        """

    def metric(self, name: str, value: float, tags: Mapping[str, str]) -> None:
        """Disposable by construction. Routed to the metrics sink and
        never to the trace store."""

    async def seal(self, run_id: RunId, outcome: RunOutcome) -> SealReport:
        """Close the trajectory, assign a retention class from the
        outcome (section 5.5), build the index, and start the retention
        clock. The only place the retention decision is made."""


class RedactionPort(Protocol):
    """Rules owned by Ch 37, applied here. Runs on raw payloads before
    anything is buffered, and leaves a MARKER rather than a hole."""

    def redact(self, payload: SpanPayload) -> tuple[SpanPayload, int]:
        """Returns the redacted payload and the number of removals, so
        section 13 can alert when a tenant's rate changes."""


class TrajectoryReader(Protocol):
    """The consumer side: Ch 15's review, Ch 41's evaluation, Ch 44's
    debugger. Tenant-scoped on every call, and audited (Ch 37)."""

    async def open(self, run_id: RunId, reader: ReaderIdentity) -> Trajectory: ...
    async def search(self, query: TrajectoryQuery) -> list[TrajectoryRef]: ...
```

### Chapter 17 — The State Manager

```python
from typing import Protocol
from datetime import timedelta


class StatePort(Protocol):
    """Ownership and progress. Every write is a conditional UPDATE, and
    zero rows affected is information rather than an error."""

    async def claim(
        self, worker_id: str, lease: timedelta, work_class: str | None = None
    ) -> ClaimedRun | None:
        """Claim one eligible run. None means no work, or another
        worker won -- both normal."""

    async def checkpoint(
        self,
        run_id: RunId,
        expected_version: int,
        progress: Progress,
        renew_for: timedelta,
    ) -> CheckpointResult:
        """Advance, renew, and read pending signals in ONE transaction.

        Raises Superseded when zero rows were affected: this worker no
        longer owns the run and must stop immediately. That is the only
        way a partitioned worker ever learns it was replaced.
        """

    async def release(
        self, run_id: RunId, expected_version: int, requeue: bool
    ) -> None: ...

    async def sweep(self, now: datetime, limit: int = 500) -> list[RunId]:
        """Expire leases past due. One indexed query; batched so a large
        backlog cannot produce one enormous transaction."""
```

### Chapter 18 — The Runtime Loop

```python
from typing import Protocol
from datetime import timedelta


class RunDriver(Protocol):
    """The loop. Sequences ports; decides nothing (section 5.2)."""

    async def drive_episode(
        self,
        run_id: RunId,
        worker_id: str,
        limits: EpisodeLimits,
    ) -> EpisodeOutcome:
        """Claim, advance under the limits, release.

        Never raises on a lost claim -- that is a normal outcome and
        returns NOT_STARTED. Never raises on Superseded either: it
        returns ABANDONED, having written nothing (section 7.1).
        """


@dataclass(frozen=True)
class EpisodeLimits:
    wall_clock: timedelta        # E1: bounds one run's hold on a worker
    step_budget: int             # E2: bounds work between plan-level
                                 #     checkpoints. 1 is legal and
                                 #     expensive (section 5.5)
    lease: timedelta             # Ch 17 section 5.5
    drain_grace: timedelta       # Ch 8 section 6.3
```

### Chapter 19 — The Multi-Agent Runtime

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

### Chapter 20 — The Self-Evolving Runtime (AHE) — Overview

```python
from typing import Protocol


class EvolveLoopPort(Protocol):
    """One iteration of Algorithm 1. Built in Level 5; named here so
    Levels 3 and 4 can declare what they owe it."""

    async def iterate(self, baseline: HarnessVersion) -> IterationReport:
        """Benchmark, ATTRIBUTE FIRST (section 4.1), distil, edit, commit.

        Halts and raises RegressionHalt when the aggregate drop exceeds
        the configured threshold: E1, a human reviews (Ch 49).
        """


class ManifestPort(Protocol):
    """The change manifest. Append-only; entries are written BEFORE
    results exist and are never edited afterwards (section 6.1)."""

    async def record(self, entry: ChangeEntry) -> None: ...

    async def verdicts_for(
        self, version: HarnessVersion, observed: TaskDeltas
    ) -> dict[ChangeId, Verdict]:
        """Intersect each entry's predicted_fixes and at_risk with what
        was observed. This is Ch 47, and it is impossible without the
        predictions having been recorded in advance."""
```

### Chapter 21 — Durable Execution

```python
from typing import Protocol


class ActivityLedger(Protocol):
    """Bounds repetition. Checkpoints bound loss; these are different
    mechanisms for different problems (section 2.2)."""

    async def lookup(self, activity_id: ActivityId) -> LedgerEntry | None:
        """Called before EVERY dispatch (Ch 14 section 4).

        A RECORDED entry is returned and the tool is not called: that is
        resume, and it is the mechanism's entire purpose.
        """

    async def claim(
        self, activity_id: ActivityId, worker_id: str, lease: timedelta
    ) -> ClaimOutcome:
        """Conditional, like Ch 17's run claim. Returns ALREADY_CLAIMED
        when another worker holds a live lease -- yield, do not
        dispatch."""

    async def record(
        self, activity_id: ActivityId, result: ToolResult, cost_cents: int
    ) -> None:
        """Terminal. There is deliberately no update and no invalidate:
        a recorded result is the answer forever (section 7.1)."""

    async def report_partial_match(
        self, expected: ActivityId, found: PartialMatch
    ) -> None:
        """Never a cache hit. Routed to an alert, because it means the
        planner edited a plan in place (section 5.3)."""
```

### Chapter 22 — The Event Spine: Outbox, Relay, Command Port

```python
from typing import Protocol


class OutboxPort(Protocol):
    """The durability boundary. One method, and its signature is the
    architecture."""

    async def append(
        self, event: Event, partition_key: str, txn: Transaction
    ) -> None:
        """Append inside the caller's transaction.

        `txn` is required and is not created here. An implementation
        that opens its own transaction has reintroduced the gap this
        chapter closes (section 5.1).
        """


class RelayPort(Protocol):
    """Claims rows, never a cursor (section 5.3)."""

    async def claim_batch(
        self, relay_id: str, size: int, lease: timedelta
    ) -> list[OutboxRow]: ...

    async def ack(self, row_id: int) -> None:
        """Per row. Never per batch (section 4.1)."""

    async def fail(self, row_id: int, error: str) -> FailOutcome:
        """Increment attempts and release the claim. Dead-letters past
        the cap. The batch CONTINUES regardless -- one bad row is one
        bad row."""


class CommandPort(Protocol):
    """The downward half of Ch 4's waist."""

    async def send(self, command: Command, txn: Transaction) -> None:
        """Commands are appended to the outbox like events; the relay
        delivers them. They carry an idempotency key and may be
        refused, and a refusal comes back as an event (section 5.5)."""
```

### Chapter 23 — The Scheduler: Queues, Work Classes, Admission

```python
from typing import Protocol


class AdmissionPort(Protocol):
    """Decides at the door. The alternative -- accept everything and
    let the queue sort it out -- is the cold open."""

    async def evaluate(
        self, tenant_id: str, goal: Goal
    ) -> AdmissionDecision:
        """ADMIT, DEFER, or REFUSE.

        DEFER accepts the goal and makes the wait VISIBLE (section 5.5).
        REFUSE is for conditions waiting will not fix, and carries a
        reason the caller can act on.
        """


class SchedulerPort(Protocol):
    async def classify(self, goal: Goal, tenant_id: str) -> WorkClass:
        """Once, at admission. The class is stored on the run and does
        not change (section 5.3)."""

    async def claim_for_slot(
        self, worker_id: str, slot: ReservedSlot
    ) -> ClaimedRun | None:
        """Claim from the slot's class, spilling only where the class
        permits. Returns None when the class is empty -- and the worker
        IDLES rather than taking other work, which is the reservation
        (section 4.1)."""


class ResourceBounds(Protocol):
    """Three, not one (section 5.4)."""

    model_semaphore: Semaphore     # sized against the PROVIDER limit
    db_pool: Pool                  # sized against checkpoint rate
    sandbox_pool: Pool             # sized against isolation needs

    def binding_resource(self) -> str:
        """Which bound is currently limiting. A measurement, not a
        configuration -- and the answer changes with the workload."""
```

### Chapter 24 — The Task Graph

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

### Chapter 25 — The World Model

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class Probe(Protocol):
    """A named, costed, read-only query against the environment."""

    name: str
    cost_estimate_ms: int
    scope_produced: str          # e.g. "api/**" or "service:checkout"
    cacheable: bool              # False means: never store the result

    def run(self, env: "Environment") -> "Belief":
        """Derive a belief. May be slow. Must not mutate anything."""


class WorldModel(Protocol):

    def get(self, probe_name: str, budget_ms: int) -> "Belief | None":
        """Return a FRESH belief, or None.

        If the stored belief is SUSPECT or STALE, re-probe when
        `budget_ms` allows and return the fresh result. When it does
        not allow, return None and emit belief.withheld. Never returns
        a non-fresh belief, with or without a caveat attached.
        """

    def invalidate(self, effect_scope: str | None, seq: int) -> int:
        """Mark every belief whose scope overlaps `effect_scope` as
        SUSPECT. A None scope marks ALL beliefs suspect -- the safe
        direction, deliberately expensive (5.3).

        Returns the number marked, which is the metric Chapter 34
        graphs against contradiction count.
        """

    def contradict(self, probe_name: str, observed: object) -> None:
        """Record that a direct observation disagreed with a stored
        belief. Marks it STALE and emits belief.contradicted. This is
        the subsystem's most valuable diagnostic; never make it a
        silent overwrite (5.5).
        """
```

### Chapter 26 — Planning Algorithms

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class Planner(Protocol):

    def plan(
        self,
        goal: "Goal",
        beliefs: Sequence["Belief"],       # FRESH only (C25)
        failure: "FailureRecord | None",   # None only on the first plan
    ) -> "PlanGraph":
        """Produce a candidate graph. Does not store it, does not
        execute, and does not decide when it was called.

        `failure` being None on anything but the first plan of a
        lineage is a programming error, not a degraded input. Raise.
        That single assertion is the cold open's fix.
        """

    def repair(
        self,
        prior: "PlanGraph",
        executed_prefix: Sequence["NodeRef"],
        failure: "FailureRecord",
    ) -> "PlanGraph":
        """Re-derive the unexecuted tail. The returned graph re-states
        the prefix with identical identity hashes so C21's check
        makes re-execution free.

        The goal is not a parameter, because repair may not change it.
        Changing the goal is a steer (C30) and starts a new lineage.
        """


class FailureClassifier(Protocol):

    def classify(
        self,
        failure: "FailureRecord",
        contract: "Contract | None",
        lineage: "Lineage",
    ) -> "Response":     # RETRY | REPAIR | REPLAN | FAIL_RUN
        """Returns FAIL_RUN when a replan would carry no information
        the previous one did not have. Refusing is correct; a run that
        stops with a clear reason costs less than one that spends its
        budget re-deriving the same plan (5.5).
        """
```

### Chapter 27 — Failure, Recovery, and Rollback

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class EffectLedger(Protocol):

    def record(self, claim: "Claim", effect: "AppliedEffect") -> None:
        """Append an applied effect. MUST be called inside the same
        transaction as the node completion (C24 sec 5.2). An effect
        recorded separately from its application has a window in which
        one exists without the other, and both orderings are silently
        wrong.
        """

    def outstanding(self, run_id: str) -> Sequence["AppliedEffect"]:
        """Applied effects not yet reversed or resolved, newest first.
        Order matters: later effects may depend on earlier ones.
        """


class RecoveryDriver(Protocol):

    def recover(self, run_id: str) -> "RecoveryOutcome":
        """Walk the ledger newest-first and discharge each effect
        according to its tier.

        Tier 1: restore locally.
        Tier 2: mint a compensation node -- a real node, with identity,
                attempt cap, budget, and gate policy. Exhaustion
                produces a dead letter, never a silent pass.
        Tier 3: record and alert. There is no reversal to attempt.

        Returns an outcome that names every unresolved obligation.
        A recovery that reversed nothing and raised no dead letter is
        indistinguishable from one that had nothing to do, so the
        outcome distinguishes them explicitly.
        """


class DeadLetterStore(Protocol):

    def raise_(self, obligation: "Obligation") -> str:
        """File work that cannot proceed and must not be forgotten.
        This is a queue for PEOPLE. Every row carries: what should be
        true, what is true, who applied it, what reverses it if
        anything, and an owner. Alert on the AGE of the oldest row,
        not the count (4.3).
        """
```

### Chapter 28 — Reflection, Grading, and Self-Correction

```python
from typing import Protocol, Sequence
from dataclasses import dataclass
from enum import IntEnum


class Rank(IntEnum):
    UNGRADABLE = 0
    FAIL = 1
    WEAK_PASS = 2
    PASS = 3


class CheckRunner(Protocol):

    def run(self, contracts: Sequence["Contract"], artefact: "Artefact") -> "Floor":
        """Evaluate every contract deterministically and return the
        floor. Makes NO model calls -- a check that needs one is not
        a check (4.1); that assessment belongs in the judge, where it
        can only lower the verdict.

        Returns UNGRADABLE when the checks themselves could not run.
        That is a grader failure, not a run failure, and the two must
        not be merged.
        """


class Judge(Protocol):

    def judge(self, goal: "Goal", artefact: "Artefact", floor: "Floor") -> "Judgment":
        """Assess the artefact against the goal.

        The parameter list is the enforcement. There is no trajectory
        parameter, no reasoning parameter, no self-review parameter --
        the judge cannot be shown them because it cannot receive them
        (3.1). Independence enforced by signature, not instruction.

        Sees the floor so it can explain a failure, not so it can
        agree with a pass.
        """


def combine(floor: "Floor", judgment: "Judgment") -> "Verdict":
    """result = min(floor, judgment) by rank. Never max.

    An attempted upgrade is logged as an event, not swallowed: the
    attempted-upgrade rate is the leading indicator that a judge's
    independence has degraded (4.3).
    """
```

### Chapter 29 — Long-Running Agents

```python
from typing import Protocol
from dataclasses import dataclass


class ProgressDetector(Protocol):

    def observe(self, run_id: str, state: "RunState") -> "Novelty":
        """Called after EVERY step. Computes a novelty hash over the
        workspace, completed node identities, terminal transitions,
        and recorded verdicts -- and NOT over step count, tokens, or
        elapsed time (2.3).

        Cheap by design: a hash and a set lookup. Its value comes
        entirely from being continuous (3.1).
        """

    def is_stalled(self, run_id: str) -> "Stall | None":
        """A stall is K EFFECTFUL steps with no novel state. Reads are
        exempt by construction, which makes the detector both more
        sensitive and less prone to false positives (5.3).
        """


class BudgetGovernor(Protocol):

    def allocate(self, graph: "PlanGraph") -> "Allocation":
        """Phase caps plus reserves, derived from the graph's shape at
        admission. The finish reserve is sized from the measured cost
        of the graph's terminal nodes, not as a percentage (4.2).
        """

    def may_start_new_work(self, run_id: str) -> bool:
        """False past the point of no return. The ready-set resolver
        consults this before returning nodes that open new branches,
        so a long run drains rather than terminating mid-branch (4.3).
        """

    def exhausted(self, run_id: str) -> "BudgetAxis | None":
        """WHICH budget ran out: tokens, wall clock, or steps. Never a
        bare boolean -- the axis is the diagnosis, and the three are
        exhausted by three different failures (4.1).
        """
```

### Chapter 30 — Human Authority

```python
from typing import Protocol
from dataclasses import dataclass
from enum import Enum


class GatePolicy(Protocol):
    """PURE. No model call, no network, no I/O of any kind (4.1)."""

    def required(
        self,
        tool: str,
        tier: "Tier",              # from C27's registry
        args: dict,
        env: str,                  # scratch | staging | production
        run: "RunMeta",
    ) -> bool:
        """Anything unrecognised returns True. An unregistered tool,
        an unknown tier, a malformed argument set -- all gated. The
        cost is a spurious park; the alternative is an unrecognised
        effect executing unattended.
        """


class DecisionStore(Protocol):
    """Append-only. Rows are never updated, only added."""

    def lookup(self, arg_hash: str) -> "Decision | None":
        """Scoped to the exact call. A decision for a different
        argument set does not match, which is the property that makes
        an approval mean what the human read (4.2).
        """

    def record(
        self,
        gate_request_id: str,
        kind: "DecisionKind",
        owner: str,                # a role, not a person's name
        reason: str,               # required for OVERRIDE
        ttl_s: int,
    ) -> "Decision":
        """OVERRIDE does NOT alter the verdict it proceeds past. The
        verdict stays FAIL forever; this row records that a named
        owner accepted the risk (5.5). Anything that edits a verdict
        instead has destroyed the only artefact establishing that a
        human made a judgment call.
        """


class ParkManager(Protocol):

    def park(self, run_id: str, gate_request_id: str) -> None:
        """Transition the run to `parked` and release EVERYTHING:
        lease, semaphore slot, worker, connection. A park that holds
        any of them makes gating cost capacity, and a cost that scales
        with human response time is a cost somebody will eventually
        attack by removing gates (2.2 steps 7-8).
        """
```

### Chapter 31 — Safety, Sandboxing, and Untrusted Content

```python
from typing import Protocol
from dataclasses import dataclass
from enum import IntEnum


class Provenance(IntEnum):
    UNTRUSTED = 0
    SEMI_TRUSTED = 1
    TRUSTED = 2


class ProvenanceTagger(Protocol):

    def tag(self, source: "Source", content: bytes) -> "LabelledContent":
        """Label at FETCH time, before any model sees the bytes.
        There is no other path by which external content becomes an
        observation (3.1).
        """

    def derive(self, inputs: "Sequence[LabelledContent]") -> Provenance:
        """min() over input labels. A summary of untrusted content is
        untrusted. Omitting this creates a laundering path: fetch,
        summarise, and the summary arrives as clean model output.
        """


class CapabilityBroker(Protocol):

    def issue(self, node: "PlanNode", run: "RunMeta") -> "Credential":
        """Issue a credential scoped to what the NODE declared at mint
        time, expiring with the step.

        There is no `content` parameter and there is no `widen`
        method. A step that discovers it needs more scope fails; the
        repair mints a new plan with the wider scope declared, and
        that plan can be gated (5.3).

        The absence of an escalation path is the design. Adding one
        reintroduces content -> capability with extra steps, and it
        is the change most likely to be proposed in review.
        """


class EgressPolicy(Protocol):

    def permitted(self, node: "PlanNode", host: str, run_taint: Provenance) -> bool:
        """Allowlist per step, derived from declared needs. Default
        empty. A tainted run reaching an unlisted host is the one
        failure in this chapter that produces no operational symptom
        at all (5.5), which is why the default must be closed.
        """
```

### Chapter 32 — Distributed Execution

```python
from typing import Protocol
from dataclasses import dataclass


@dataclass(frozen=True)
class LeaseHandle:
    run_id: str
    worker_id: str
    version: int
    fence: int              # monotonic per run, never reset (7.2)
    believes_held_until: str    # named to discourage trusting it (7.1)


class LeaseStore(Protocol):

    def claim(self, run_id: str, seen_version: int, ttl_s: int) -> LeaseHandle | None:
        """One statement. Expiry evaluated by the STORE's clock, in
        the same statement as the write, so no read-then-write gap
        exists (4.1).

        Returns None when another worker holds it. That is a normal
        outcome and not an error -- C24's overlapping ready sets are
        resolved here, by design.
        """

    def renew(self, handle: LeaseHandle) -> "LeaseHandle | LeaseLost":
        """On LeaseLost the caller MUST disarm effects immediately,
        without waiting for the in-flight call to return (4.2).

        This cannot help during a process pause, because nothing is
        running to call it. It covers the more common case of a
        briefly unreachable store, where the worker is alive.
        """


class EffectGateway(Protocol):

    def execute(self, handle: LeaseHandle, call: "ToolCall") -> "Outcome":
        """Requires the handle. Three protections, in order of how
        well they work and inverse order of how often they are
        available:

          1. fence carried to the downstream, which rejects a stale
             token. The ONLY mechanism that works during a pause,
             and the least often available (5.3).
          2. activity identity looked up before the call (C21).
             Requires a queryable downstream.
          3. neither: the effect is at-least-once. Say so. Gate it,
             or make the downstream tolerate duplicates.

        A system with none of the three and a lease does not have
        exactly-once. It has a lease.
        """
```

### Chapter 33 — Scalability and Capacity Planning

```python
from typing import Protocol
from dataclasses import dataclass


class ServiceTimeMeter(Protocol):

    def record(self, surface: str, hold_ms: float, queue_ms: float) -> None:
        """Record a hold and the wait that preceded it, SEPARATELY.

        Service time is the hold; queue time is the wait for
        permission to hold. Only the first belongs in a sizing
        calculation. Merging them produces a number that grows under
        load and justifies whatever capacity produced the load (7.1).
        """

    def percentiles(self, surface: str) -> "ServiceTime":
        """p50, p95, p99 of the HOLD. Re-measured on every model
        change, because the dominant service time is the model call
        and it moves when the model does (5.5).
        """


class CapacitySizer(Protocol):

    def required(self, surface: str, arrival_rate: float) -> float:
        """Little's Law: arrival rate x service time. One
        multiplication per surface, and there is no shared multiplier
        between surfaces -- inventing one is the cold open.
        """

    def binding_surface(self) -> str | None:
        """WHICH surface is currently the constraint. Not a number --
        a name. Every capacity conversation lacking this one output
        degenerates into adding workers, which makes a saturated
        model semaphore worse (4.2).
        """


class CommitmentEstimator(Protocol):

    def commitment(self, graph: "PlanGraph") -> "SurfaceCommitment":
        """Expected holds per surface over the run's whole lifetime,
        derived from the graph at mint time (C24).

        Admission spends this, not current utilisation. A system at
        40% with two hundred admitted six-hour runs is not at 40%
        (3.1).
        """
```

### Chapter 34 — Observability

```python
from typing import Protocol
from dataclasses import dataclass


class MetricEmitter(Protocol):

    def observe(self, name: str, value: float, labels: dict[str, str]) -> None:
        """Record a measurement.

        `labels` is checked against an ALLOWLIST at the call site and
        rejects anything not on it. Not a denylist -- the next
        unbounded label is always one nobody thought of. A run_id in a
        metric label is the most common self-inflicted outage in this
        subsystem, and it takes down infrastructure observability at
        the exact moment it is needed (4.2).
        """


class TraceSink(Protocol):

    def span(self, run_id: str, span: "Span") -> None:
        """High-cardinality by design. Every span carries flow (C9),
        surface (C33), and tenant -- three low-cardinality axes that
        make a 140-span trace readable by someone who was not there.
        """

    def finalise(self, run_id: str, outcome: "RunOutcome") -> "Retention":
        """Apply the sampling policy AT COMPLETION, because a run's
        category is not known until it ends (7.2).

        Always-keep categories are a correctness property, not a
        best-effort behaviour. This method may block or spill; it may
        not silently drop an always-keep record.
        """


class AnomalyDetector(Protocol):

    def identity_partial_match(self, detail: "IdentityAnomaly") -> None:
        """PAGE. Not a log line, not a dashboard, not a daily digest.

        A partial match means C21's identity function is wrong, and
        four subsystems' correctness rests on it -- retry safety,
        free plan repair, attempt caps, and effect protection where
        no fence token exists. None of them will report a problem.
        They will produce duplicate effects at a rate nobody is
        measuring (5.4).
        """
```

### Chapter 35 — Cost Engineering and Token Economics

```python
from typing import Protocol
from dataclasses import dataclass


class CostEstimator(Protocol):

    def estimate(self, assembled: "Context", effort: str, step_type: str) -> int:
        """Input tokens are COUNTED, not estimated -- the context has
        already been assembled.

        Output tokens are estimated from the p95 of this step type at
        this effort tier, NOT the p50. The asymmetry is deliberate:
        under-reserving admits a call that then breaks the budget,
        which is the failure this mechanism exists to prevent;
        over-reserving costs concurrency for a few seconds (4.1).
        """


class BudgetLedger(Protocol):

    def reserve(self, run_id: str, tokens: int, ttl_s: int) -> "Reserve | Refused":
        """Hold against `available = limit - spent - reserved`.

        The third term is why concurrency cannot defeat the budget.
        A ledger that checks only `limit - spent` lets N concurrent
        calls each pass individually and collectively exceed
        (2.2 step 6), and single-threaded tests never show it.

        `ttl_s` is required, not optional. An unswept reserve is
        permanent phantom spend (5.3).
        """

    def settle(self, reserve: "Reserve", usage: "Usage") -> None:
        """Release the hold and record the PROVIDER's reported usage.
        Never estimate after the fact -- the provider knows, and its
        number is the one that will be invoiced.
        """


class CostAttribution(Protocol):

    def record(self, usage: "Usage", tags: "CostTags") -> None:
        """Five tags: run, tenant, step type, model, cached fraction.

        Judge spend is a separate step type, always (4.2). Repair and
        replan spend are separate step types, always -- the cold open
        is invisible without that tag, because repair spend
        undistinguished from ordinary spend looks like runs getting
        longer for no reason.
        """
```

### Chapter 36 — Reliability and SLOs

```python
from typing import Protocol
from dataclasses import dataclass
from enum import Enum


class Objective(str, Enum):
    LIVENESS = "liveness"
    HONESTY = "honesty"
    ACCOUNTING = "accounting"
    # Quality is deliberately absent. It has no budget and no page,
    # for two independent reasons (2.2 step 7).


class SLIComputer(Protocol):

    def sli(self, objective: Objective, window: "Window") -> float:
        """Compute a deterministic ratio over a window.

        All three are properties of the RUNTIME, not of the model,
        which is what makes them promisable. The runtime either
        terminated the run or it did not.
        """


class ErrorBudget(Protocol):

    def burn_rate(self, objective: Objective, window: "Window") -> float:
        """Rate, not remaining balance.

        A slow leak and a cliff both show 40% consumed and need
        opposite responses. Page on the fast window; review the
        balance weekly (4.1).
        """


class DegradationController(Protocol):

    def degrade(self, rung: int, reason: str) -> None:
        """Rungs 1-3 preserve the honesty promise: the caller knows
        what they are getting.

        Rung 4 -- silently reducing quality -- is not implementable
        through this interface. Reducing quality requires
        `degrade_with_disclosure`, which demands a per-run durable
        record and a caller notification, at which point it is
        rung 3 (5.3).
        """

    def degrade_with_disclosure(
        self,
        config: "DegradedConfig",
        record_on_run: bool,       # must be True
        notify_caller: bool,       # must be True
    ) -> None:
        """Both flags are required and both must be True. They are
        parameters rather than internal behaviour so that a code
        review sees them, and so that turning either off is a visible
        edit rather than a missing feature.
        """
```

### Chapter 37 — Tenancy, Secrets, and Data Governance

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class StoreRegistration(Protocol):
    """Every store declares these. A store that has not is not
    writable -- enforced at the persistence layer, failing in
    development (4.1)."""

    name: str
    tenant_field: str
    classification: str            # "verbatim" | "structural"
                                   # | "operational"
    retention_days: int

    def delete_tenant(self, tenant: str) -> "DeletionResult":
        """Remove or archive this tenant's rows.

        May return REFUSED with a reason -- an effect ledger row
        carrying an unresolved obligation must not be silently
        deleted, because that row is the only thing that would have
        told anyone about the migration still on staging (6, t=4).
        """


class CaptureRedactor(Protocol):

    def redact(self, material: bytes, kind: str) -> bytes:
        """Runs BEFORE the write, over ALL captured material: tool
        arguments, tool output, error text, and file content.

        Irreversible by design. Reversible redaction is a
        key-management problem in a data-protection costume -- the
        material still exists and the exposure moves to the key
        (4.2).
        """


class DeletionExecutor(Protocol):

    def execute(self, tenant: str) -> "Certificate":
        """Enumerate the REGISTRY, not a list.

        A store present in the system and absent from the registry is
        impossible by construction (4.1). A store in the registry
        with no deletion route is a LOUD failure, never a silent
        skip.

        Returns a per-store certificate: deleted, retained with a
        reason, or flagged for human decision. A certificate that
        names eight stores is true about eight stores, which is
        exactly the cold open's failure.
        """
```

### Chapter 38 — Deployment, Versioning, and Configuration

```python
from typing import Protocol
from dataclasses import dataclass


class ConfigResolver(Protocol):

    def resolve(self, run_id: str) -> "ResolvedConfig":
        """Resolve defaults, file, environment, and overrides ONCE at
        run start, hash the RESULT, and freeze it for the run's life.

        The hash is over resolved values, not over the file. A file
        hash says the file did not change; a resolved hash says the
        behaviour did not change, and the gap between those is where
        unexplained shifts live (3.1).

        Live-reloadable values are a small, explicit, documented set
        -- kill switches and rate limits -- not a category called
        "operational config" (4.2).
        """


class InvalidationRegister(Protocol):

    def declare(self, name: str, value: float, measured_against: str) -> None:
        """Register a tuned number with the model it was measured
        against. Timeouts, token p95s, effort tiers, thresholds.
        """

    def stale(self, current_model: str) -> "Sequence[StaleEntry]":
        """Every number measured against a different model.

        This BLOCKS promotion rather than appearing in a report
        (5.2). It is also the honest answer to how large a migration
        is: the cold open's team believed they were making a one-line
        change, and a register would have said thirty-one.
        """


class ModelPin(Protocol):

    def resolve(self) -> str:
        """An exact version. Never an alias, never "latest".

        An alias lets behaviour change with no event in your change
        log -- a regression on a Tuesday with an empty change history
        for Tuesday, and C41 comparisons that silently span two
        models (4.1).
        """

    def days_until_withdrawal(self) -> int | None:
        """A scheduling input on a dashboard, not a risk-register
        entry. It is the only metric in the system guaranteed to
        reach zero (5.4).
        """
```

### Chapter 39 — GitOps and CI/CD for Agent Systems

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class BlastRadiusLinter(Protocol):

    def required_slices(self, changed_paths: Sequence[str]) -> "Coverage":
        """Map changed files to the benchmark slices that must run.

        A shared instruction file maps to EVERY slice. There is no
        narrower answer and the result is not advisory -- the
        argument for narrowing it is always available and always
        sounds reasonable at the time (4.1).
        """


class RegressionHarness(Protocol):

    def run(self, harness_hash: str) -> "GateResult":
        """Gate 1. Deterministic, minutes, every commit.

        Every check is deterministic -- no model calls. C28 section
        4.1 gives the correctness reason; here there is a second,
        independent one: gate 1 must finish in minutes and a model
        call is neither fast nor repeatable.

        Cannot see a 6-point regression, and is not supposed to.
        """


class EvaluationRunner(Protocol):

    def evaluate(
        self,
        candidate: "VersionTriple",
        incumbent: "VersionTriple",
        coverage: "Coverage",
        rollouts: int,
    ) -> "EffectReport":
        """Gate 2. Statistical, hours, before promotion.

        Returns effect sizes PER SLICE alongside the noise floor,
        never a bare pass or fail. A regression concentrated in one
        slice is diluted to invisibility in an aggregate (6).
        """


class ShadowRunner(Protocol):

    def compare(self, candidate: str, incumbent: str, tasks: Sequence[str]) -> "Divergence":
        """Run both on IDENTICAL inputs and stop before the first
        effectful step (C14's tag says where; C27's tiers say what
        would have happened past it).

        Paired inputs remove most of the variance gate 2 must
        otherwise average away, which is why this detects a smaller
        effect with far fewer runs (5.3).
        """
```

### Chapter 40 — Testing a Non-Deterministic System

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class Clock(Protocol):
    """A port, injected. Two clocks, separately faked (4.2)."""

    def monotonic(self) -> float: ...
    def wall(self) -> str: ...


class FakeClock(Clock):
    def advance(self, seconds: float) -> None:
        """EXPLICIT time movement.

        Without this, C32's lease expiry, C27's sweeper, C29's stall
        window, C30's gate TTL, and C35's reserve TTL are all
        untestable except by waiting -- or by shortening the
        intervals, which changes the thing under test (6, failure
        branch).
        """


class ScriptedPort(Protocol):
    """A fake that asserts its call sequence, not merely its
    returns."""

    def expect(self, calls: Sequence["ExpectedCall"]) -> None:
        """Declare the calls this port must receive, in order.

        Ordering is a correctness property throughout Levels 2 and 3
        -- identity checked BEFORE the call, the gate consulted
        BEFORE execution, the ledger written INSIDE the completion.
        A value-returning mock cannot express any of them (4.1).
        """


class ReplayHarness(Protocol):

    def load(self, fixture_id: str) -> "Recording":
        """A real trajectory from C34's trace store: real model
        behaviour, deterministic execution. Built from the
        always-keep categories, which are already retained and are
        exactly the interesting shapes (5.2).
        """

    def serve(self, recording: "Recording") -> "ReplayOutcome":
        """PASS | FAIL | DIVERGED.

        DIVERGED is a distinct outcome, never folded into FAIL: most
        divergences are the runtime legitimately improving, and a
        tier that reports those as failures is silenced within a
        quarter (5.3).
        """
```

### Chapter 41 — Evaluation Infrastructure

```python
from typing import Protocol, Sequence
from dataclasses import dataclass


class NoiseFloorEstimator(Protocol):

    def measure(self, corpus_version: str, triple: "VersionTriple", k: int) -> "Floor":
        """Run the UNCHANGED harness k times over the corpus and
        report the spread, PER SLICE.

        This produces no artefact anyone asked for, which is why it
        is skipped and why the cold open happens. It is the first
        thing to build, not the last.

        Small slices have wide floors, and that is where results get
        over-read (4.1).
        """

    def current(self, corpus_version: str, triple: "VersionTriple") -> "Floor | None":
        """None when stale -- a model change or a corpus version
        change invalidates it, and nothing else does (7.2).

        Callers must handle None by refusing to report an effect
        size, not by substituting a remembered number.
        """


class EvaluationRunner(Protocol):

    def evaluate(
        self,
        candidate: "VersionTriple",
        incumbent: "VersionTriple",
        corpus_version: str,
        k: int,
        paired: bool = True,
    ) -> "EffectReport":
        """k rollouts per task; `pass@1` averaged over k, never a
        single run `[AHE App. A]`.

        Paired by default: the same task, both harnesses, identical
        inputs, so task difficulty cancels. This is usually the
        cheapest large narrowing of the floor available (5.1).

        Raises if the floor is stale. A number without its error
        term is not a result.
        """


class CorpusManager(Protocol):

    def retire(self, task_id: str, reason: str) -> str:
        """Retire and replace. NEVER edit.

        Editing a task silently invalidates every historical
        comparison including the floor, which was measured on a
        corpus that then no longer exists (5.5).
        """

    def drift(self) -> "DriftReport":
        """Corpus slice distribution against production traffic.
        When they diverge, ADD tasks -- reweighting breaks
        comparability the same way editing does (5.6).
        """
```

### Chapter 42 — The Case for Harness Evolution

```python
from typing import Protocol


class FitDecayMeter(Protocol):
    """Makes the cold open's measurement a routine operation rather
    than an eighteen-month archaeological dig."""

    def standing_advantage(
        self,
        harness: "HarnessVersion",
        seed: "HarnessVersion",
        corpus_version: str,
        k: int,
    ) -> "Advantage":
        """What the fitted harness is worth against the minimal seed,
        on the CURRENTLY deployed model.

        This is the number that justifies doing any of this. It is
        large and roughly stable (sec 2.3).
        """

    def carried_advantage(
        self,
        harness: "HarnessVersion",
        previous: "HarnessVersion",
        corpus_version: str,
        k: int,
    ) -> "Advantage":
        """How much of the last cycle's fitting survived the model
        change. Usually small, and the only way to know whether the
        fitting compounds or is re-earned (sec 5.1).

        Both methods raise when the floor is stale, for the reason
        C41 sec 8 gives: a number without its error term is not a
        result, and this one will be quoted in a budget meeting.
        """


class RefitLedger(Protocol):
    """Where a re-fit's days went, so sec 4's ratio is measured
    rather than believed."""

    def record(self, entry: "RefitRecord") -> None:
        """Append-only. Written during the re-fit, not reconstructed
        after it -- reconstruction systematically under-counts the
        reading, because reading leaves no artefact.
        """

    def step_shares(self, since: str) -> dict[str, float]:
        """Fraction of elapsed time per step, across recorded
        re-fits. If step 2 is not dominant, this chapter's case is
        weaker for you and should be re-argued (sec 5.3).
        """


class EvolutionReadiness(Protocol):
    """The sec 5.6 table, as a check that can block rather than a
    page in a design document."""

    def check(self, corpus_version: str) -> "ReadinessReport":
        """Evaluates every precondition. The noise-floor row is a
        gate; the rest are graded.

        Intended to be run BEFORE any of C43-C47 is built, and
        again before the loop is allowed to keep an edit without
        review (C49).
        """
```

### Chapter 43 — Component Observability

```python
from typing import Protocol, Sequence


class ComponentRegistry(Protocol):
    """The only way anything asks what the harness is made of.
    Read-only: writes go through the git workspace (C39) so every
    change is a reviewable, revertible commit."""

    def resolve(self, path: str) -> "Component | None":
        """None means the path is not under any mount point, and
        therefore is not a component at all.

        A caller that treats None as "a component I could not
        classify" reintroduces the orphan (7.1). None means the
        file does nothing.
        """

    def inventory(self, kind: "ConstraintLevel | None" = None) -> Sequence["Component"]:
        """What exists, per type, with size and age.

        Built from the LOADER, not from the filesystem. The
        difference between those two lists is the orphan set, and
        it is the report nobody runs (7.1).
        """

    def validate(self) -> "ValidationReport":
        """Gate 1 (C39): every file under a mount point registers,
        and every registered component resolves to a file.

        Fails the build. A warning here is read once and then
        filtered, and the failure it describes has no other symptom.
        """


class OverlapDetector(Protocol):

    def declared(self) -> Sequence["OverlapFinding"]:
        """Two components claiming the same behaviour tag. Free,
        structural, and build-time.

        Catches only KNOWN ownership, which is the point: it makes
        what people already know permanent, so an eleven-month-old
        hook cannot be forgotten (5.3).
        """

    async def probe(self, component_id: str, corpus_version: str, k: int) -> "ProbeResult":
        """Disablement probe: remove the component, re-run, measure.

        Costs one benchmark run. A component whose removal changes
        nothing outside the noise floor is either dead or being
        compensated for, and the two are distinguished by probing
        the suspected compensator as well.

        Raises when the floor is stale (C41 sec 8).
        """


class SeedPolicy(Protocol):

    def seed_version(self) -> str:
        """The tagged origin of the measurement space (5.6). Not a
        branch, not history -- a fixed reference that C42's
        standing_advantage measures against."""

    def is_protected(self, path: str) -> bool:
        """Seed components are non-deletable (C46). Unusual among
        the controllability constraints: this one protects a
        measurement rather than a safety property (7.2)."""
```

### Chapter 44 — Experience Observability

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

### Chapter 45 — Decision Observability

```python
from typing import Protocol, Sequence


class EntryGate(Protocol):
    """The only path into the manifest. Every check is mechanical;
    a gate needing judgment would need a judge, and a judge the
    loop can influence is a verifier inside the workspace
    (C20 sec 5.5)."""

    def propose(self, draft: "ChangeDraft", corpus: "CorpusHandle") -> "Entry | Refusal":
        """Five checks: evidence novelty, sharpness,
        non-circularity, address resolution, at-risk recorded.

        A Refusal names the failing check, because C46 reads it
        and redrafts from it. C15's rule applies: an error is an
        instruction, not a diagnosis (6.1).
        """

    def seal(self, entry: "Entry", pending_run_id: str) -> "EntrySeal":
        """Bind the entry to the benchmark run that will test it.

        Raises if that run has already started. The ordering must
        be a fact about two recorded events, not about a clock
        written by the party being audited (7.2).
        """


class SharpnessValidator(Protocol):

    def check(self, predicted: Sequence[str], corpus: "CorpusHandle") -> "Width | Refusal":
        """Task ids that EXIST in the corpus, or refuse.

        Not a slice name, not a predicate, not a description.
        C47 intersects sets; anything else needs a judgment call,
        and judgment calls made by scoring code are generous in
        the direction that flatters the loop (2.2).

        Returns the width, which is STORED beside the set. A width
        derived at scoring time can be derived from a re-read of
        the claim, which is the cold open with an extra step (4.2).
        """


class EvidenceNoveltyChecker(Protocol):

    def novel(self, pointers: Sequence["EvidencePointer"]) -> "bool | str":
        """False (with the prior entry id) when EVERY pointer has
        been cited before -- a proposal storm (5.1).

        Deliberately not 'any pointer'. A new theory about
        partly-overlapping evidence is what a good second attempt
        looks like, and the stricter rule would forbid it.
        """


class Ledger(Protocol):
    """Queries over the manifest. This is what C49's reviewer
    reads; they will not read entries (5.7)."""

    def precision_and_width(self, iterations: int) -> Sequence["IterationStats"]:
        """Never precision alone. A loop at 60% precision and
        width 3 is aiming; one at 89% and width 14 is hedging,
        and a single number cannot tell them apart."""

    def level_distribution(self, iterations: int) -> dict[str, float]:
        """Rising system-prompt share is C43 sec 5.4's decay."""

    def repeated_level_for_cause(self, threshold: int = 2) -> Sequence[tuple[str, str, int]]:
        """(root cause cluster, level, count) above threshold: the
        fix-at-the-wrong-level anti-pattern, detectable only
        because both fields are mandatory (5.5)."""
```

### Chapter 46 — The Evolve Agent

```python
from typing import Protocol, Sequence


class WriteScope(Protocol):
    """Enumerated paths, not a description. C43's registry is what
    makes this expressible (2.2 step 7)."""

    def permits(self, changed_paths: Sequence[str]) -> "bool | Refusal":
        """Checked against the DIFF, last, after the entry gate.

        An entry naming a permitted path is not the same as a diff
        touching only permitted paths, and a check that trusts the
        entry is checking the loop's description of what it did
        (3.1, 6.1).
        """

    def contains(self, path: str) -> "ContainmentEntry | None":
        """Which containment entry excludes this path, and why.

        Returns the reason so the refusal is informative. C45
        sec 6.1's rule: a refusal is an interface the agent reads
        and redrafts from, so it is written under C15's rules.
        """


class Router(Protocol):

    def route(self, pattern: "Pattern") -> "ComponentClass":
        """C43 sec 5.3's chain. MAY return a class outside the
        write scope.

        Returning only in-scope classes would make every answer
        actionable and make displacement invisible, which is the
        second-worst outcome in this chapter (4.1).
        """


class LevelSelector(Protocol):

    def choose(
        self,
        cls: "ComponentClass",
        pattern_id: str,
        history: "EditHistory",
    ) -> "LevelChoice | Escalation | Refusal":
        """The weakest level that can enforce it (C1 sec 5.2).

        On a second attempt at one failure pattern the level must
        RISE -- rewording at the same level is refused. On a third,
        refuse entirely: the diagnosis is wrong, not the level
        (5.5).

        The counter is per (pattern, level), not per component. A
        loop spreading three attempts across three files at one
        level has done the anti-pattern with extra steps.
        """


class ContainmentPolicy(Protocol):
    """Read by the agent, written only by a human through C49.
    Stored with the verifier, not beside the workspace (7.2)."""

    def entries(self) -> Sequence["ContainmentEntry"]: ...

    def record_contest(self, entry_id: str, pattern_id: str) -> None:
        """The refusal counter. The only signal in the system that
        says the list may be in the wrong place (7.1), and the
        only input that ever justifies revisiting it (5.7)."""
```

### Chapter 47 — Attribution, Verdicts, and Rollback

```python
from typing import Protocol, Sequence


class Attributor(Protocol):

    def attribute(
        self,
        entries: Sequence["Entry"],
        observed: "PerTaskDeltas",
        floor: "Floor",
        corpus_before: "CorpusHandle",
        corpus_after: "CorpusHandle",
    ) -> Sequence["Attribution"]:
        """Intersect each sealed entry's sets with the observed
        deltas, per task and against the per-slice floor.

        Raises when the floor is stale (C41 sec 7.2). A verdict is
        an ACTION, and an action taken on a number without its
        error term is a change made at random (5.5).

        Takes BOTH corpora because the mechanism check compares
        them: an entry whose tasks passed while its pattern
        persisted is right for the wrong reason (5.2).
        """

    def collisions(self, entries: Sequence["Entry"]) -> Sequence[tuple[str, str, str]]:
        """(change_id, change_id, shared_task_id).

        Run at SEALING, not at scoring. Knowing before the
        benchmark that two of six edits will be mutually
        unattributable is actionable -- ship them in different
        iterations (4.2).
        """


class VerdictAssigner(Protocol):

    def assign(self, attribution: "Attribution") -> "Verdict":
        """Four values. The fourth is UNDETERMINED, and it exists
        because an intersection is a total function: without an
        abstention the arithmetic produces a verdict for cases the
        evidence cannot decide (2.2 step 4).

        Inside the floor is UNDETERMINED, never KEEP and never
        ROLLBACK. It is not a small effect; it is no measurement
        (4.1).
        """


class RollbackExecutor(Protocol):

    async def revert(self, change_id: str) -> "RollbackRecord":
        """File-level revert in the workspace (C39). Tier 1: owned
        state, prior version kept, cannot half-fail (C27).

        Restores the CODE, not the world the code acted on. This
        is sufficient only because trials are confined to tier-1
        effects -- sandbox and scratch space, enforced by C31
        rather than by the benchmark's good manners (5.6).

        Marks the manifest entry; never deletes it. The refuted
        hypothesis is what stops the loop re-proposing it (7.1).
        """
```

### Chapter 48 — Limits

```python
from typing import Protocol, Sequence


class SliceGate(Protocol):
    """The fixable limit, as a check. C39 already produces
    per-slice effects with per-slice floors; this reads them."""

    def blocks(
        self,
        candidate: "VersionTriple",
        seed: "VersionTriple",
        floor: "Floor",
    ) -> "SliceVerdict":
        """Compares CUMULATIVELY against the seed, per slice --
        not against the previous iteration.

        A per-iteration rule never fires on a trade made in
        sub-floor steps, which is how ten iterations moved a
        slice ten points without one regression being recorded
        (6.1).

        Requires the seed to be runnable, which is C43's
        non-deletable rule earning its keep a second time.
        """


class InterferenceEstimator(Protocol):

    def expected_combined(self, singles: Sequence["Advantage"]) -> "Range":
        """Given single-component gains, what should the
        combination deliver?

        Returns a RANGE with the naive sum as the upper bound.
        [AHE 4.4.1]'s one data point puts the realised figure at
        about two thirds of the sum; one observation is a thin
        basis for a coefficient, so this is a planning posture
        rather than a model (5.1).
        """


class ResidueSweeper(Protocol):
    """The only mechanism in Level 5 that makes the harness
    smaller (5.7)."""

    async def sweep(self, budget_runs: int) -> Sequence["RemovalResult"]:
        """Removal experiments (C39 sec 5.6) aimed at UNDETERMINED
        edits, oldest first.

        One benchmark run per candidate. An edit whose removal
        changes nothing outside the floor goes -- and the same
        result is also C43's overlap signal, read from the other
        end.
        """
```

### Chapter 49 — Continuous Improvement and Governance

```python
from typing import Protocol, Sequence


class ReviewScan(Protocol):
    """Computed before the meeting, in fixed order. A scan that
    requires someone to run queries live becomes a scan that
    happens when that person is available (5.1)."""

    def compute(self, week: str) -> "ScanReport":
        """Eleven numbers, each with the failure it catches named
        in the report itself.

        Deliberately EXCLUDES the aggregate score. It is monitored
        elsewhere, everyone looks at it anyway, and it is the
        number that can rise while number 1 falls (C48 sec 5.3).
        """

    def unused_entries(self, since: str) -> Sequence[str]:
        """Numbers that have never been out of band. Reviewed
        annually for removal -- agendas accrete exactly the way
        instruction files do (4.1)."""


class Gate(Protocol):
    """Three of them, and no more (2.3)."""

    def decide(self, request: "GateRequest", owner: str) -> "GateDecision":
        """Owner is named and, for Gate 2, outside the loop's
        reporting line. The person who wants a constraint moved is
        the person whose work it is blocking (5.2).
        """

    def refusal_rate(self, since: str) -> float:
        """A gate at zero over six months is theatre, and theatre
        consumes the attention the real gates need. C7 sec 14: an
        approval that is always granted is a gate that should be
        removed."""


class AccessAudit(Protocol):

    def reads(self, since: str, subject: str | None = None) -> Sequence["AccessRecord"]:
        """Who read which trajectory, INCLUDING machine readers.

        Reviewed, not alerted: volume makes alerting useless and
        the question is always asked retrospectively (5.3).

        The cold open's eleven days were spent reconstructing what
        this returns in a query.
        """


class AutonomyPolicy(Protocol):

    def level(self) -> "AutonomyLevel": ...

    def conditions_met(self, target: "AutonomyLevel") -> "ConditionReport":
        """Every condition is a MEASUREMENT, never a judgment
        about readiness (7.1)."""

    def demote_on(self, event: str) -> None:
        """Automatic. A demotion requiring a decision is argued
        about at the moment it is most needed, by the people whose
        work it slows (7.1)."""
```
