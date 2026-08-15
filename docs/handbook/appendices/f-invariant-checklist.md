# Appendix F — Invariant Checklist

Hand-written. The properties that must hold for the architecture to work, each with a **test recipe**
naming which of Chapter 40's three tiers can check it.

This is the appendix a reviewer uses. Appendix G lists what goes wrong; this lists what must stay
true, which is the shorter and more useful list.

---

## The three tiers, as a reminder

Chapter 40 splits testing at the model port, and the split decides what a given invariant costs to
check.

| Tier | What it is | Cost | In CI? |
|---|---|---|---|
| **1 · Deterministic** | Fake ports — model scripted, tool scripted, clock controlled, store real in a container | Milliseconds | Every commit |
| **2 · Replay** | Recorded trajectories from the trace store: real model behaviour, deterministic execution | Seconds | Every commit |
| **3 · Statistical** | Live model, k rollouts, an effect size with a noise floor | Hours, real money | **No** — a measurement, not a gate |

**Retry is forbidden in tiers 1 and 2.** A test that needs retrying is testing something
non-deterministic that should be above the port, and Chapter 40 §5.4 makes that a lint rule rather
than a convention.

Twelve of the fourteen behaviours Chapter 40 enumerates are below the port. `[INF]` The consequence
for this appendix is the encouraging one: **most invariants here are tier 1**, checkable in
milliseconds, on every commit.

---

## 1. Runtime invariants

### 1.1 Ownership and durability

| # | Invariant | Tier | Test recipe |
|---|---|---|---|
| R1 | Exactly one driver advances a run at any instant | 1 | Two workers, one run, controlled clock. Advance both past the lease boundary; assert exactly one CAS succeeds (Ch 32 §5) |
| R2 | A crash loses at most one in-flight step | 1 | Kill the driver mid-step with a fake model that has already returned; assert the resumed run repeats at most that step (Ch 21 §5) |
| R3 | No scarce resource is held across a model call | 1 | Fake model port that blocks; assert the connection pool's checked-out count is zero while it blocks (Ch 18 §5) |
| R4 | Recovery is continuous, never boot-time only | 1 | Strand a run four hours into a long-lived worker's life; assert the sweeper claims it without a restart (Ch 8 §5) |
| R5 | A parked run holds nothing | 1 | Park a run; assert zero leases, zero pool connections, zero semaphore slots attributable to it (Ch 5, Ch 30 §5) |
| R6 | A state change and its event are one transaction | 1 | Fail the process between the two writes; assert neither is visible (Ch 22 §2.2) |
| R7 | A poison event cannot stall the relay | 1 | Insert an unprocessable row; assert later rows still deliver (Ch 22 §5) |

### 1.2 Identity and effects

| # | Invariant | Tier | Test recipe |
|---|---|---|---|
| R8 | Activity identity is computed at plan time, not at dispatch | 1 | Dispatch the same step twice concurrently; assert one execution and one recorded result (Ch 14 §4.1, Ch 21) |
| R9 | An effectful step never executes unapproved | 1 | Fake gate that never resolves; assert the effectful tool's implementation is never entered (Ch 30 §5) |
| R10 | The effect tag is checked before the ledger, not after | 1 | Replay an effectful step whose result was *not* recorded; assert the gate is evaluated (Ch 14 §4.1) |
| R11 | Every effect is reversed or named | 1 | Fail a run after three effects; assert the ledger's compensations plus dead letters cover all three (Ch 27 §5) |
| R12 | A trial produces tier-1 effects only | 1 | Run a benchmark trial with an egress-denying sandbox; assert no effectful tool reached the network (Ch 47 §5.6, Ch 31) |

### 1.3 Context, cost, and truthfulness

| # | Invariant | Tier | Test recipe |
|---|---|---|---|
| R13 | The cache-stable prefix is byte-identical across calls in a run | 1 | Assert the prefix hash is constant up to `volatile_boundary_offset` (Ch 11 §5) |
| R14 | A budget reservation is settled or swept | 1 | Crash after reserving; assert the sweeper releases it (Ch 35 §5) |
| R15 | The runtime reports failure truthfully | 2 | Replay a trajectory whose grader returned FAIL; assert the run's terminal state is not success (Ch 36 §5) |
| R16 | A model judgment may lower a verdict and never raise it | 1 | Deterministic floor of FAIL plus a judge returning PASS; assert the combined verdict is FAIL (Ch 28 §5) |
| R17 | Fetched content is data, never instruction | 1 | Trajectory containing an injection string in a tool result; assert no tool call derives from it (Ch 31 §5) |

### 1.4 Observation and governance

| # | Invariant | Tier | Test recipe |
|---|---|---|---|
| R18 | Redaction happens at capture, never at read | 1 | Write a trajectory containing a credential pattern; assert the *stored* bytes carry `[redacted:credential]` (Ch 16 §5.4) |
| R19 | Capture never fails a run | 1 | Fake trace store that raises; assert the run completes (Ch 16 §4.1) |
| R20 | No durable fact is sourced from the trace store | 1 | Delete the trace store entirely; assert every run still resumes and completes (Ch 16 §5.6) |
| R21 | Every run records its version triple | 1 | Assert code, harness, and model ids are non-null on every completed run (Ch 38 §3.1) |
| R22 | Tenant scoping holds on every read path | 1 | Query each of the nine stores as tenant A; assert zero rows belonging to tenant B (Ch 37 §5) |

---

## 2. Evolution invariants

These hold only when Level 5 is running. `[INF]` Every one of them protects something the benchmark
score cannot represent, which is why they are invariants rather than preferences — see Chapter 46
§5.2 for the argument and the eleven-entry containment list it produces.

### 2.1 Containment

| # | Invariant | Tier | Test recipe |
|---|---|---|---|
| E1 | The loop writes only inside the workspace | 1 | Propose a diff touching a path outside the write scope; assert refusal, and assert `scope.violated` fires (Ch 46 §3.1) |
| E2 | The scope check runs against the diff, not the entry | 1 | Entry naming a permitted path, diff touching two; assert refusal (Ch 46 §3.1) |
| E3 | The runs directory is read-only to the loop | 1 | Attempt a write through the loop's own path; assert refusal (Ch 46 §5.1) |
| E4 | Seed components cannot be deleted | 1 | Propose a diff removing a seed file; assert refusal (Ch 43 §5.7, Ch 46 §5.1) |
| E5 | None of the eleven contained items is writable | 1 | Table-driven: one refusal assertion per containment entry (Ch 46 §5.2) |
| E6 | The containment policy has no write path from the loop | 1 | Assert `ContainmentPolicy` exposes no mutating method (Ch 46 §7.2) |

### 2.2 Evidence and claims

| # | Invariant | Tier | Test recipe |
|---|---|---|---|
| E7 | Every registered component resolves to a file, and every file at a mount point registers | 1 | Reconcile the loader's list against the filesystem; assert the difference is empty (Ch 43 §4.1) |
| E8 | No two components claim one behaviour tag | 1 | Build-time assertion over declared tags (Ch 43 §5.3) |
| E9 | An analysis cannot be written without an undroppable field | 1 | Analyser fed a trajectory with context accounting stripped; assert it raises (Ch 44 §5.3) |
| E10 | A predicted set is task ids that exist in the corpus | 1 | Draft naming a slice; assert the gate refuses (Ch 45 §5.3) |
| E11 | A manifest entry cannot be edited after sealing | 1 | Assert `ManifestPort` exposes no update method, and that the hash chain breaks on a forced rewrite (Ch 45 §5.6) |
| E12 | An entry seals only against a run that has not started | 1 | Seal against a completed run id; assert it raises (Ch 45 §7.2) |
| E13 | Every proposal cites at least one span no earlier entry cited | 1 | Re-propose from an identical pointer set; assert refusal (Ch 45 §5.1) |

### 2.3 Judgement and rollback

| # | Invariant | Tier | Test recipe |
|---|---|---|---|
| E14 | Attribution refuses to run against a stale floor | 1 | Invalidate the floor via a model change; assert `attribute` raises (Ch 47 §5.5) |
| E15 | An inside-floor result is never KEEP and never ROLLBACK | 1 | Delta below the slice floor; assert UNDETERMINED (Ch 47 §4.1) |
| E16 | Distillation cannot run before attribution | 1 | Call `distil` with `attribution_complete=False`; assert it raises (Ch 44 §8) |
| E17 | A rolled-back entry is marked, never deleted | 1 | Roll back; assert the entry and the reverted commit both persist (Ch 47 §7.1) |
| E18 | Rollback restores the workspace exactly | 2 | Replay a trajectory under the reverted harness; assert byte-identical component files (Ch 27 §5.4) |
| E19 | Automatic rollback is disabled while the runtime is unstable | 1 | Inject a flaky tier-1 suite; assert the loop refuses to auto-revert (Ch 40 §14, Ch 47 §5.5) |

### 2.4 Measurement

| # | Invariant | Tier | Test recipe |
|---|---|---|---|
| E20 | An effect size is never reported without its floor | 1 | Assert `SliceEffect` cannot be constructed without `noise_floor_pp` (Ch 39 §9, Ch 41 §9) |
| E21 | Precision is never reported without claim width | 1 | Assert no `Ledger` method returns precision alone (Ch 45 §8) |
| E22 | No slice regresses outside its floor, cumulatively against the seed | **3** | The promotion gate itself. Requires a seed run and a candidate run; hours (Ch 48 §5.3, §6.1) |
| E23 | The seed still resolves and still scores what it scored | **3** | Scheduled re-run against the current model (Ch 43 §5.7, Ch 42 §8) |
| E24 | The noise floor is current for the deployed model | 1 | Assert the floor's triple matches the deployed triple; raise otherwise (Ch 41 §7.2) |

---

## 3. How to use this list

**Twenty-eight of the thirty-five invariants are tier 1.** They run in milliseconds, on every commit,
against fake ports and a controlled clock. `[INF]` That is the most encouraging fact in this
appendix and it is not obvious in advance — the intuition is that a system built around a model is
mostly untestable, and Chapter 40 §5.1 exists to correct it.

**Two are tier 2** (R15, E18) because they need real model behaviour with deterministic execution:
the shapes a scripted fake cannot produce.

**Three are tier 3** (E22, E23, and by extension anything about whether the loop is working). They
are measurements with noise floors, they are not gates in CI, and treating them as tests is how a
benchmark gets shrunk until it detects nothing (Chapter 39 §5.2).

`[BP]` The review use is table-driven: one parametrised test per row, named for the invariant, so a
failure names the property rather than the mechanism. A suite organised that way survives a refactor
of the mechanism, which is the point.

`[FUT]` Nothing generates this list from the chapters, unlike Appendices D, E, G, H, I, and J. The
invariants are stated across fifty chapters in prose rather than in a structured block, and a marker
convention that made them extractable would be a worthwhile change to the authoring template — and
would let the linter check that every invariant here still has a chapter behind it.

---

**See also:** [Appendix G — Failure Mode Catalogue](g-failure-mode-catalogue.md) for what happens when
one of these does not hold · [Appendix E — Port Signatures](e-port-signatures.md) for the contracts
several of these are asserted against · Chapter 40 for the tiers.
