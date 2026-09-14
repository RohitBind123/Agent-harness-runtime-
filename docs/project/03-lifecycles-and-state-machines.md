# Lifecycles and State Machines

**Status:** every transition below is **DESIGNED**. None is implemented.

The purpose of this document is that another engineer can implement these
without reading any previous conversation. Each transition states its
**trigger**, **preconditions**, **state change**, **evidence requirement**,
**reversibility**, and **persistence semantics**.

Where a transition's rules are not established by any source document, it says
**"Not yet established."** Those are entries in
`docs/project/10-open-questions.md`, not gaps to fill by guessing.

---

## 1. How to read these

Three properties hold across every lifecycle here and are stated once:

1. **The write path never fails a run.** Memory and knowledge system writes are off the
   critical path. A failure to record a claim degrades future runs; it does not
   fail the current one.
2. **The read path never fails a step.** A retrieval failure yields less
   context, not an error.
3. **Nothing in any lifecycle raises a claim's standing except independent
   evidence.** No stage, no model, no human assertion at write time.

---

## 2. Observation

```
            adapter emits
                 |
                 v
         +---------------+
         |   RECORDED    |  append-only. terminal for the observation itself.
         +---------------+
                 |
     +-----------+-----------+
     |                       |
     v                       v
  ADMITTED              DISCARDED       <- the admission decision
     |                  (counted, not
     v                   deleted)
  PROCESSED
```

| Transition | Trigger | Preconditions | Evidence required | Reversible? | Persistence |
|---|---|---|---|---|---|
| → RECORDED | An adapter emits an observation | Content hash not already present | None — nothing is interpreted here | **No.** Append-only | Durable, retained longer than derived claims |
| RECORDED → DISCARDED | Admission rejects it | Deterministic rules run first; a cheap model only if inconclusive | None | Yes — reprocessing can re-admit it | The observation **stays**. Only the admission verdict is recorded |
| RECORDED → ADMITTED | Admission accepts | As above | None | Yes | Verdict recorded |
| ADMITTED → PROCESSED | Extraction has run for the current extractor version | An identity-keyed proposal row exists | None | Yes — a new extractor version reprocesses | Keyed by `(observation_id, extractor_version)` |

**Note the shape:** a discarded observation is **not deleted**. It is recorded
as discarded, and the **discard rate is a headline metric** from before the
first source is enrolled. A discard rate that is suspiciously low means
admission is not working; one that is suspiciously high means it is eating
signal. Neither is visible without the counter.

**Re-delivery** is a no-op by content hash. Slack webhooks, Jira polls and
backfills all deliver the same thing more than once, and every one of them will.

---

## 3. Proposal

```
   extraction claims the row BEFORE the model call
                 |
                 v
          +-------------+
          |   PENDING   |
          +------+------+
                 |
     +-----------+-----------+------------+
     v           v           v            v
  APPLIED     REJECTED    DUPLICATE   OUT_OF_VOCABULARY
                 |                         |
          (reason recorded;         (rate is the signal to
           rate by reason           extend the vocabulary)
           is a signal)
```

| Transition | Trigger | Preconditions | Evidence required | Reversible? | Persistence |
|---|---|---|---|---|---|
| → PENDING | Extraction begins | **The row is claimed before the model call.** `proposal_id` is UNIQUE and derived from `(observation_id, extractor_version)` | None | No | Durable. The UNIQUE key is what makes redelivery collide |
| PENDING → OUT_OF_VOCABULARY | Predicate not in the closed registry | — | None | Yes, after a vocabulary migration | Rate tracked per predicate-shape |
| PENDING → REJECTED | A deterministic check fails | Checks include: **the imperative check** ("always do X" is a harness change, not a memory); schema validation; `kinds_allowed` violation; trust-rule violation | None | Yes on reprocess | **Reason recorded.** Rejection rate *by reason* is a signal |
| PENDING → DUPLICATE | Classification finds `same` at this identity | — | — | n/a | Recorded; may still add corroborating evidence |
| PENDING → APPLIED | Classification and reconciliation succeed | Runs in **one transaction** with the claim, its version, its evidence and its outbox event | The evidence row is written in the same transaction | No | Durable |

**The imperative check is one regular expression and is the single
highest-value line in the write path.** A claim that says what *should* be done
is a proposed harness change. It must go through the evaluation gate, not
through memory — because a harness change requires a **measurement** (an effect
size outside a noise floor), which is a different kind of evidence from a
corroborated observation.

---

## 4. Claim

**The load floor** used below is the handbook's own term (Ch12: "confidence
below which an entry stays in the file but is never loaded"), applied here to
claim promotion rather than memory-entry loading.

```
                    proposal APPLIED
                          |
                          v
                  +---------------+
                  |  PROVISIONAL  |  stored, INERT. influences nothing.
                  +-------+-------+
                          |
            corroboration by DISTINCT runs
            crosses the load floor
                          |
                          v
                  +---------------+
      +---------->|    ACTIVE     |<----------+
      |           +---+-------+---+           |
      |               |       |               |
      | re-confirmed  |       | contradicted  | probe agrees
      | (last_confirmed         (confidence     (last_confirmed
      |  moves)       |        LOWERED,         moves)
      |               |        never flipped)
      |               v
      |        +-------------+
      |        | SUPERSEDED  |  a later claim at the same identity,
      |        +-------------+  where the predicate is single_valued.
      |                         interval CLOSED. history KEPT.
      |               
      |        decay from last_confirmed, or
      |        confidence falls below the retire floor
      |               |
      |               v
      |        +-------------+
      +--------|   RETIRED   |  stops influencing runs. STAYS in history.
               +-------------+
                      |
                      |  tenant deletion route ONLY
                      v
               +-------------+
               |   DELETED   |  data gone. a DIFFERENT operation.
               +-------------+
```

| Transition | Trigger | Preconditions | Evidence required | Reversible? | Persistence |
|---|---|---|---|---|---|
| → PROVISIONAL | A proposal is applied and no claim exists at this identity | Predicate in registry; `kinds_allowed` satisfied; tenant in key | One evidence row, same transaction | n/a | Version 1 written |
| PROVISIONAL → ACTIVE | Corroboration crosses the load floor | **Corroboration counted over DISTINCT runs.** Same-run repetition is not corroboration | ≥ 2 evidence rows from distinct runs | Yes — decay can send it back below | New version |
| **Untrusted-derived → ACTIVE** | **Never.** | An untrusted-derived claim may reach PROVISIONAL and never ACTIVE | — | — | Enforced as a **CHECK constraint**, so a future caller cannot bypass it |
| ACTIVE → ACTIVE (reinforced) | A corroborating observation | Same identity, same object | New evidence row | n/a | `last_confirmed` moves; confidence may rise |
| ACTIVE → ACTIVE (contradicted) | A conflicting observation | Same identity, different object | New evidence row | n/a | **Confidence is LOWERED, never flipped.** A contradiction does not make the other claim true |
| ACTIVE → SUPERSEDED | A later claim at the same identity where the predicate is `single_valued` | **`single_valued` is a declared property of the predicate**, not something read from two sentences | The superseding claim's evidence | No — but history is kept | `superseded_at` closes the interval; `superseded_by` set |
| ACTIVE → RETIRED | Decay from `last_confirmed`, or confidence below the retire floor | Applies the predicate's `decay_profile` | None | Yes — a new corroboration can revive it | Version written. **Stays in history** |
| ACTIVE/RETIRED → invalidated | Scope-overlap against the durable ordered effect stream | The run's own effects are the dominant staleness case | The effect stream position | — | Invalidation is by **scope overlap, not a TTL** |
| Any → DELETED | **The tenant deletion route only** | Enumerated across every store | — | **No** | **A different operation from retirement.** See [ADR-0017](decisions/ADR-0017-deletion-route-before-retirement.md) |

### Two things that must not decay

- **Decisions.** Append-only and permanent. A decision is superseded by a later
  decision; it never decays and never retires. We did not *maybe* decide.
- **Terms and definitions.** Effectively permanent, and the highest-value
  low-cost content in the store.

### Concurrency

**Re-classify on conflict, not retry on conflict.** The write is an optimistic
version CAS. On conflict, the correct response is to **re-run classification
against the new current claim** — because retrying re-applies a classification
computed against a stale claim, and silently erases whatever the winning writer
decided.

---

## 5. Contradiction

```
   classification finds conflict at an identity
                 |
                 v
          +-------------+
          |    OPEN     |---- severity: BLOCKING or ADVISORY
          +------+------+
                 |
       +---------+---------+
       v                   v
   RESOLVED            SUPERSEDED
   (new observations   (one side superseded;
    settle it)          contradiction moot)
```

| Transition | Trigger | Preconditions | Evidence required | Reversible? | Persistence |
|---|---|---|---|---|---|
| → OPEN | Two claims at one identity disagree, predicate is `single_valued`, supersession does not apply | Both claims above the load floor | Both claims' evidence | — | Durable, with severity |
| OPEN → RESOLVED | **New observations** settle it | — | The settling observation | Yes, if disagreement recurs | Recorded |
| OPEN → SUPERSEDED | One side is superseded by a later claim | — | — | — | Recorded |

**A contradiction is never resolved by a cleanup job, a model judgement, or a
human editing the store.** It is resolved by the world changing and being
observed.

**Blocking severity gates action minting.** An advisory contradiction is
reported in assembled context. A blocking one refuses the action.

**Two failure modes with opposite shapes:**

- **Contradiction fatigue.** Low precision means the detector gets muted within
  a week, and the capability is then gone regardless of later quality.
  Therefore: measure **raised versus confirmed-real-by-owner**, and treat the
  second number as the one that matters.
- **A blocking contradiction blocking everything.** One unresolved disagreement
  in a busy scope can refuse every action touching it. The severity assignment
  must be conservative about `blocking`.

---

## 6. Evidence

| Transition | Trigger | Preconditions | Reversible? | Persistence |
|---|---|---|---|---|
| → MINTED | A claim version is written | **Server-minted.** No caller-supplied id — that is the whole attack | No | **Same transaction as the claim** |
| MINTED → DETAIL_EXPIRED | Raw payload retention window passes | Structural signal retained | No | The reference survives; the readable detail does not |
| MINTED → DELETED | Tenant deletion route | Found by joining on the departing tenant's runs | No | Requires evidence to be a **joinable table**, not a count |

---

## 7. Verification (of a claim)

```
   +-------------+   a probe exists for this predicate
   | UNVERIFIED  |------------------+
   |  (DEFAULT)  |                  |
   +-------------+                  v
                            +---------------+
                            | PROBE_SCHEDULED|
                            +-------+-------+
                                    |
                        +-----------+-----------+
                        v                       v
                 PROBE_AGREES            PROBE_DISAGREES
                 (last_confirmed          (writes an OBSERVATION,
                  moves)                   which re-enters at the top
                                           and contradicts the claim)
```

| Transition | Trigger | Preconditions | Evidence required | Reversible? | Persistence |
|---|---|---|---|---|---|
| → UNVERIFIED | A claim is written | — | — | — | **The default, and it is honest** |
| UNVERIFIED → PROBE_SCHEDULED | The predicate declares `verifiable_by` | A probe is registered and **read-only** | — | — | Scheduled |
| → PROBE_AGREES | The probe confirms | — | The probe's observation | — | `last_confirmed` moves |
| → PROBE_DISAGREES | The probe contradicts | — | The probe's observation | — | **The probe writes an OBSERVATION, never a claim.** It re-enters the pipeline at the top |

**This is the only proactive mechanism in the entire design.** Every other
mechanism — corroboration, contradiction, decay, invalidation — is *reactive*.
It covers only probe-verifiable predicates, which will be a minority.

**The structurally unsolved case, stated rather than hidden:** noticing a claim
is wrong when **nothing new has been observed about it** and no probe exists.
The runtime cannot feel doubt, so doubt must be manufactured — and manufacturing
it for a social fact is not something anyone has solved.

---

## 8. Execution node (runtime)

```
  PENDING --> READY --> RUNNING --> APPLIED --> SETTLED
                          |
                          +--> FAILED
                          +--> BLOCKED (with a REASON)
```

| Transition | Trigger | Preconditions | Reversible? | Persistence |
|---|---|---|---|---|
| PENDING → READY | Dependencies satisfied | Level-triggered reconciliation | — | Durable |
| READY → RUNNING | The controller invokes the capability | An approval reference is resolved if the effect tier requires one — **in the runner, never by prompting** | — | Checkpointed |
| RUNNING → APPLIED | The effect completed | **The ledger row was written BEFORE the effect.** The crash between the two is the interesting case | Per effect tier | Ledger row updated with result digest |
| APPLIED → SETTLED | Verification passed | **Deterministic post-conditions, no model** | — | Verification report |
| RUNNING → FAILED | The effect failed, or verification failed | — | Tier 1 restore; tier 2 compensation as a real step; **tier 3 is not reversible at all** | Run becomes PARTIAL; applied effects stay applied and remain undoable |
| Any → BLOCKED | A precondition cannot be met | **A reason is mandatory** | Yes, when the reason clears | Durable |

**Invariants.** *Transitions are legal-only and total: every node reaches a
terminal state or is explicitly BLOCKED with a reason.* *A terminal node is
immutable — redoing work creates a new node in a new generation.*
*Reconciliation is idempotent: two consecutive passes over an unchanged graph
produce an unchanged graph.*

**Recovery on launch** reconciles every ledger row in an unknown-applied state
against the world, settles or fails it, then resumes from the ready set.

---

## 9. Run (runtime)

```
  CREATED -> RUNNING <--> PARKED -> SETTLED
                |                     ^
                +-> PARTIAL ----------+
                +-> FAILED -----------+
```

| Transition | Trigger | Preconditions | Reversible? | Persistence |
|---|---|---|---|---|
| CREATED → RUNNING | A controller acquires the lease | **Exactly one controller advances a session at any instant** — lease plus version CAS in one statement | — | Lease recorded |
| RUNNING → PARKED | A gate needs a human, or there is nothing to do | **The park holds no process, no connection, no in-memory timer** | Yes | Durable. Resumes at the right step |
| PARKED → RUNNING | Approval, signal, or event | The resuming worker may be a different one | — | Checkpoint restored |
| RUNNING → SETTLED | The goal is met | Verification passed | No | Terminal |
| RUNNING → PARTIAL | Some nodes failed | Applied effects stay applied and remain undoable | — | Terminal-ish; undo remains available |
| PARKED → FAILED | A gate expires with no answer | **A gate nobody answers expires the run rather than proceeding** | No | Terminal |

---

## 10. Decision, Commitment, Outcome (Principal Agent)

**Status: BLOCKED.** These depend on goal records with measures and baselines,
grants, and authority — organizational structures that do not exist.

| Object | Lifecycle | Key rule |
|---|---|---|
| **Decision** | `DRAFT → SEALED → SUPERSEDED` | **Append-only.** The prediction is sealed *before* the result is knowable. A later decision supersedes; the old one stays |
| **Commitment** | `OPEN → MET \| MISSED \| WITHDRAWN` | Open-age alerting is the point. A commitment outlives the run that created it |
| **Outcome** | `PREDICTED → MEASURED → (BETTER \| WORSE \| UNDETERMINED)` | **Measured by a probe, later — never reported by the run.** UNDETERMINED is first-class |

**Four states that look identical and are not**, which is why UNDETERMINED must
exist: the intervention worked; it did nothing and something else moved the
measure; it did harm masked by something else; and the measure moved for reasons
unrelated to anything we did. A system with only better/worse will report one of
these falsely.

---

## 11. Transitions not yet established

Recorded so that nobody implements a guess as if it were a design.

| Transition | What is missing | Where it is tracked |
|---|---|---|
| The exact load floor and retire floor values | **Not yet established.** Tuning them before the extraction noise floor is measured is fitting to noise | Q11 |
| The decay half-life per profile | **Not yet established.** No consulted source gives a defensible starting value | Q11 |
| How a human correction is distinguished from a human being wrong | **Open and uncomfortable.** The current position — a correction is high authority on *intent* and does not automatically outrank a probe on *reality* — is a starting point, not a settled answer | Q13 |
| Whether a claim inherits taint through a marshalled, schema-validated extraction | **Open.** The provenance lattice says nothing clears taint, absolutely. Whether an enum extracted from an untrusted document is still derived content is a security judgement, not an architectural one | Q14 |
| Contradiction severity assignment rules | **Not yet established.** What makes a contradiction blocking rather than advisory is not specified anywhere | Q15 |
| Entity merge/split lifecycle | **Not yet established.** What happens when two entities turn out to be one, or one turns out to be two, after claims are attached to both | Q16 |
