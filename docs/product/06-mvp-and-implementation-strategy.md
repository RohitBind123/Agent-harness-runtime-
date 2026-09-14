# 6 — MVP Definition and Implementation Strategy

---

## Part 7 — The MVP

### 7.1 The one thing the MVP must prove

Not "the agent organises files." The MVP exists to prove the **full loop survives interruption and
produces a verifiable, reversible result**:

```
DISCOVER → OBSERVE → EXTRACT → WORLD MODEL → PLAN → POLICY → EXECUTION GRAPH
    → CAPABILITY → EXECUTE → VERIFY → DURABLE STATE → RECOVERY
```

The acceptance test is one sentence, and it is the definition of done:

> **Point it at a folder of 500 real documents. Approve the plan. Kill the app at a random point
> during execution. Reopen it. It reconciles, finishes, verifies every effect against the filesystem,
> and a single Undo returns the folder byte-identically to its prior state.**

Nothing in the MVP exists that is not required by that sentence.

### 7.2 Platform: macOS only

iOS is **not** in the MVP. Rationale from report 2: the MVP's whole point is recovery and verification
under interruption, and iOS gives no background process to recover *in*. Proving the loop on the
platform where it can actually run is worth more than proving half of it on two.

### 7.3 Exact scope

**In:**

| Area | Scope |
|---|---|
| Environment | One user-selected folder tree, security-scoped, read-write |
| Goal types | Exactly one: *"Organise this folder."* No free-text goals |
| File types | PDF (text layer), PDF (scanned → OCR), PNG/JPEG/HEIC (OCR), `.txt`/`.md`, `.docx` |
| Operations | `create_folder`, `move`, `rename`, `move_to_quarantine`. **That is the complete registry** |
| Inference | Cloud provider (default, opt-in) **or** Foundation Models on-device (Apple-Intelligence Macs) |
| Verification | Deterministic post-conditions over the filesystem |
| Undo | Full-run undo, and per-effect undo, available indefinitely while the ledger exists |
| Persistence | SQLite in the app container |
| Distribution | Sandboxed, Mac App Store |

**Explicitly excluded, and why:**

| Excluded | Why |
|---|---|
| iOS app | Cannot demonstrate recovery. Phase 2 |
| Delete (any form) | Tier 3 in the MVP's threat table. Quarantine is sufficient |
| Shell / git / subprocess | Not needed by the acceptance test; large new threat surface |
| Watching (FSEvents) | The MVP is user-initiated. Watching is Phase 2 |
| Semantic *search* | Apple ships it free in macOS 27. Do not compete there in v1 |
| Multi-folder / multi-scope | One scope keeps the world model honest |
| Cross-device sync | Nothing to sync until iOS exists |
| Free-text goals | An open goal space needs a planner. One goal type needs a recipe |
| Duplicate *deletion* | Detection yes, deletion no |
| The evolution loop (Ch 42–49) | Requires an evaluation harness that requires users that require a product |
| MCP | Absent from our source architecture; nothing requires it |
| Multi-agent (Ch 19) | No second agent |
| Human approval *parking* across days | Approval is synchronous in v1; Park arrives with iOS |

### 7.4 The end-to-end flow, with the data that exists at each stage

This is the section that makes the difference between a PRD and a wish.

```
STAGE            PRODUCES                                    DETERMINISTIC?
─────────────────────────────────────────────────────────────────────────────
DISCOVER         scope_grant{bookmark, root_url}             yes — NSOpenPanel
                 run{id, goal_type, scope_id, created_at}

OBSERVE          file_observation[] per file:                yes — FileManager
                   {path, size, mtime, ctime, uti,
                    content_hash(sha256), inode}
                 → written to `observations`, run-scoped

EXTRACT          extraction[] per file:                      yes — PDFKit/Vision
                   {file_id, text_excerpt(≤N tokens),
                    page_count, has_text_layer,
                    ocr_confidence, provenance=UNTRUSTED}
                 → text is NEVER stored verbatim beyond the run

CLASSIFY         DocumentFacts per file:                     NO — the only model call
                   {category_id, issuer?, doc_date?,           per file
                    amount?, confidence}
                 closed output schema; cannot name a path

WORLD MODEL      belief[] :                                  yes
                   {claim, provenance, observed_at_seq,
                    scope}
                 e.g. claim="folder Statements/ holds 41
                 bank statements", scope="Statements/**"

PLAN             plan{id, nodes[]} where each node is        yes — a declared recipe,
                   {op, src_path, dst_path, reason,            not a model plan
                    effect_tier, activity_identity}
                 dst_path computed by CODE from
                 (category_id, taxonomy, collision policy)

POLICY           gate_decision{allow|require_approval}       yes
                 rules: effectful ⇒ approval;
                        >N files ⇒ approval;
                        any tier-2 effect ⇒ approval

EXECUTION GRAPH  the plan IS the graph (spec I27).           yes
                 node states: PENDING→READY→RUNNING
                 →APPLIED→SETTLED | FAILED | BLOCKED

CAPABILITY       capability `organise.apply` binds to        yes
                 tool `fs.move` at plan time (spec I22)

EXECUTE          per node, in order:                         yes
                   1. write effect_ledger row (APPLIED_UNKNOWN)
                   2. FileManager.moveItem
                   3. update row → APPLIED{dst_hash, at}
                 crash between 1 and 3 is the interesting case

VERIFY           verification_report:                        yes — NO model involved
                   src gone? dst exists? hash matches?
                   count_before == count_after?
                   orphans == 0?
                 any failure ⇒ node FAILED, run PARTIAL

DURABLE STATE    runs, observations, plans, effect_ledger,   yes
                 activities, beliefs, taxonomy — SQLite

RECOVERY         on launch: any run in EXECUTING →           yes
                   reconcile every APPLIED_UNKNOWN row
                   against the filesystem, settle or fail,
                   then resume from the ready set
                 idempotent: two passes over an unchanged
                 graph produce an unchanged graph (I28)
```

**One model call per file, with a closed output schema. Everything else is code.** That is design rule
14 from the specification, and it is also what the 4,096-token Foundation Models limit would force on
us anyway.

### 7.5 Failure handling

| Failure | Response |
|---|---|
| A file cannot be parsed | Node `BLOCKED` with reason; run continues. Never fails the run |
| Model returns low confidence | File left where it is, listed as "needs your decision" |
| Destination collides | Deterministic policy: `name (2).pdf`. Never overwrite. Ever |
| Move fails (permissions, disk full) | Node `FAILED`; run becomes `PARTIAL`; already-applied effects stay applied and remain undoable |
| App killed mid-run | Recovery reconciles on next launch |
| Undo finds a hash mismatch | **Refuse and raise a dead letter.** Chapter 27 §5.3: do not guess |
| Scope revoked between runs | Run `BLOCKED`, prompt for re-grant. No partial execution |

### 7.6 Model architecture and inference

| Concern | Decision |
|---|---|
| What the model does | Exactly one job: bounded text → `DocumentFacts` |
| What the model never does | Compute paths, choose operations, decide order, judge success, name tools |
| Local | Foundation Models, `@Generable` guided generation. 4,096-token session cap ⇒ one file per session, excerpt-bounded |
| Cloud | A frontier model behind the same typed interface, chosen for accuracy on the same schema |
| Which is default | **Cloud, opt-in at onboarding, with local as a first-class alternative.** Report 4's experiment decides whether local is good enough to be the default |
| Networking | Model provider only. No other egress. No telemetry containing paths or content |

---

## Part 8 — Implementation strategy

### 8.1 What to do with this repository

**Option 4: use it primarily as architectural reference.** Not a judgement call — there is no code to
extend, refactor or replace (report 1, Finding 0). The repository becomes the *justification layer*
for a new implementation repository, and stays where it is.

Two pieces of work are owed to it regardless:

1. **Reconcile the two vocabularies** (report 1, Finding A). Adopt the specification's names as
   canonical for code; keep the handbook as the derivation. One ADR, half a day, saves months.
2. **Write down the on-device profile** — which of the 32 invariants apply when there is one user, one
   process and no contention. This is the artefact that does not exist today and is needed before line
   one.

### 8.2 Existing / missing / must-change

| Category | Contents |
|---|---|
| **Existing code** | None (5 handbook build scripts) |
| **Existing specification** | Six layers, narrow waist, five nouns, three loops, ExecutionGraph, 32 invariants, effect tiers, provenance lattice, verdict lattice, build order 0–12 |
| **Missing implementation** | All of it |
| **Portable runtime components** | Activity identity · effect ledger · transactional outbox · checkpointing · effect tags from a registry · provenance lattice · verdict lattice · world model with scoped invalidation · capability/tool split · declared recipes · ExecutionGraph · verification before knowledge |
| **Must change for macOS** | Substrate: Postgres+queue → **SQLite, single writer**. Relay/queues → **in-process dispatch**. Leases and version-CAS → **unnecessary** (one driver by construction). Sweeper → **launch-time reconciler plus a periodic timer**. Multi-tenancy → **deleted** |
| **Must change for iOS** | Everything above, **plus**: no background process ⇒ the run driver only advances while foregrounded; no watching ⇒ scan-on-open; no execution ⇒ the tool registry is a fixed, compiled set; no Trash ⇒ quarantine; Park becomes essential (a run genuinely waits for the user to return) |
| **Platform-specific adapters** | `FileSystemPort` (enumerate/read/move/create/trash) · `ExtractionPort` (PDFKit, Vision) · `InferencePort` (FoundationModels, cloud) · `ScopePort` (bookmarks, security-scoped access) · `ClockPort` |

### 8.3 The keep/drop list

Roughly 15% of the specified architecture goes into the MVP. Being explicit about the 85% is the point.

**Keep — these are the MVP:**

| Component | Source | Why it cannot wait |
|---|---|---|
| Activity identity | spec I9 | Spec §10.7: *"Every other invariant can be added later… This one cannot… roughly thirty lines. Write it first"* |
| Effect ledger | Ch 27 | Undo and recovery are both impossible without it |
| Effect tag from the registry | Ch 14, I15 | The whole safety model |
| Transactional outbox | Ch 22 | Trivial with one SQLite writer; retrofitting is not |
| Checkpoint per step | I12 | The acceptance test is a kill test |
| Provenance lattice | Ch 31 | Retrofitting provenance is impossible — labels are assigned at fetch time or never |
| Verification before knowledge | I18 | The differentiating claim |
| ExecutionGraph as the only plan representation | I27 | A second representation appears the moment you allow one |
| Redact at capture | Ch 16 §5.4 | Cannot be fixed retroactively; git and backups do not forget |
| World model with scope-based invalidation | Ch 25 | Needed by the second run over the same folder |

**Drop from the MVP — with the trigger that brings each back:**

| Component | Bring back when |
|---|---|
| Relay, queues, claims, `SKIP LOCKED` | There is a second process |
| Leases, version-CAS, sweeper | There is a second driver |
| Episode as a distinct noun | There is a worker pool |
| Multi-tenancy, per-tenant admission, budget ledger | There is a server |
| Distributed execution (Ch 32) | Never, for this product |
| Multi-agent runtime (Ch 19) | A second agent has a job |
| Evaluation infrastructure (Ch 41) | Before the *second* model change — sooner than instinct suggests |
| Evolution loop (Ch 42–49) | There is an evaluation harness that knows its noise floor |
| MCP | An external tool ecosystem is needed |
| Human-authority parking across days | iOS ships (approval genuinely spans app launches there) |

### 8.4 Roadmap

Each phase is shippable and each is falsifiable. No phase begins before the previous one's exit
criterion is met.

| Phase | Weeks | Build | Exit criterion |
|---|---|---|---|
| **0 · Evidence** | 1–2 | *No runtime code.* The content-vs-filename experiment on 500 real documents. iOS spikes S1–S4. Vocabulary ADR | Content beats filenames by a margin that would justify the OCR cost and the privacy conversation. **If not, stop and re-scope** |
| **1 · Spine** | 3–6 | SQLite schema, outbox, activity identity, effect ledger, checkpointing, `ExecutionGraph`, recovery-on-launch | A hardcoded three-node graph survives `kill -9` mid-node and completes correctly on relaunch |
| **2 · Vertical slice** | 7–12 | Scope grant, observation, extraction, one model call, declared recipe, policy gate, execute, **verify**, **undo** | **The §7.1 acceptance test passes on 500 real documents** |
| **3 · Product** | 13–20 | Review UI, taxonomy editing, quarantine, duplicate detection, onboarding, local-inference mode, Mac App Store submission | 20 external users complete a real organise run and 15 keep the result |
| **4 · Habit** | 21–28 | FSEvents watching, incremental runs, recurring paperwork rules, memory across runs | Median user runs it ≥ 3 times in 30 days. **This is the real business test** |
| **5 · iOS companion** | 29–40 | iOS app, CloudKit shared Brain, capture-first flows, Park for approvals, honest capability messaging | A user captures on iPhone and finds it correctly filed on the Mac, without a second decision |
| **6 · Harden** | 41–52 | Evaluation harness with a measured noise floor, golden set, trajectory distillation, per-model regression gates | A model swap can be shown to be better or worse, with a number |
| **7 · Second environment** | 2027 | Whichever environment users ask for — probably cloud storage, not Git | The port abstraction survives contact with something that is not a filesystem |

**Do not build phases 6 and 7 early.** Chapter 41's warning applies directly: the failure that kills an
agent product is not that it wedges under concurrency — it is that it produces confident, plausible,
wrong work and nobody notices. But an evaluation harness with no users has no distribution to measure
against.

### 8.5 The single most likely way this goes wrong

Building phase 1 beautifully, for four months, because it is the part that is fully specified and
therefore the most comfortable to build — and arriving at phase 0's experiment far too late to act on
the answer.

**Phase 0 comes first, and it contains no runtime code.**
