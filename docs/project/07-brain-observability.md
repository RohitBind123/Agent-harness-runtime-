# Knowledge System Observability — the Flight Recorder

**Status:** **DESIGNED / PROPOSED.** Nothing here is implemented.

**The governing rule, and the reason this document exists:**

> **The knowledge system must not be allowed to declare itself correct.**

A knowledge system's failures are almost all silent. Nothing raises an
exception when a claim is confidently wrong, when two entities never join, when
admission is never applied, or when a private fact reaches someone outside the
channel it came from. **For a knowledge system, invisibility matters more than
severity** — which is why this document ranks failures by how hard they are to
see rather than by how much damage they do.

---

## 1. The traceable chain

Every question the knowledge system answers must be reconstructable end to end, from the
raw observation to the consequence.

```
  WHAT IT SAW          observation_id, source, actor,
                       occurred_at, ingested_at, content hash,
                       permission label
        |
        v
  WHAT IT ADMITTED     admitted or discarded, WHICH RULE decided,
                       deterministic or model stage
        |
        v
  WHAT IT RESOLVED     mention -> entity_id, or UNRESOLVED
                       (unresolved is a recorded outcome,
                        not a silent drop)
        |
        v
  WHAT IT EXTRACTED    proposal_id, extractor_version,
                       proposed claim, kind, predicate
        |
        v
  WHAT IT REJECTED     rejection reason, per proposal
        |               -- and the RATE BY REASON, which is
        |                  the actual signal
        v
  WHAT IT ACCEPTED     claim_id, version, status,
                       source_class, confidence, validity
        |
        v
  WHAT CORROBORATED    which DISTINCT runs, which evidence rows
  / CONTRADICTED IT    which contradiction, what severity
        |
        v
  WHAT IT RETRIEVED    for which Principal, which question,
                       which as_of, which scopes,
                       what was returned AND WHAT WAS DROPPED
        |               for budget
        v
  WHAT CONTEXT IT      the assembled block, with the three
  PROVIDED             un-droppable items present
        |
        v
  WHAT ANSWER          the agent's output, and which claims
  CAME OUT             each atomic assertion mapped to
        |
        v
  WAS IT RIGHT         -- NOT judged by the knowledge system. See sec 3.
        |
        v
  WHAT HAPPENED        the decision taken, the effect applied,
  AFTERWARDS           the outcome measured later by a probe
```

**The chain has one property that makes it worth building: every link is
already required by something else.** Observation ids exist for the rebuild
invariant. Proposal ids exist for identity-keyed extraction. Evidence rows exist
for corroboration and deletion. The only genuinely new durable record is the
**retrieval record** — see §4.

---

## 2. What must be recorded, and where

The runtime's existing telemetry split applies unchanged: **logs** for
debugging, **traces** for causality, **metrics** for alerting, **audit** for
things a person may have to answer for.

| Recorded | Where | Durable? | Why |
|---|---|---|---|
| Observation, verbatim | Observation log | **Yes, always** | The system of record. Everything rebuilds from it |
| Admission verdict + deciding rule | Observation log | Yes | The discard rate is meaningless without which rule fired |
| Entity resolution outcome | Trace | Yes for the mapping, sampled for the reasoning | Fragmentation is invisible without it |
| Proposal + extractor version | Proposals table | Yes | Identity, and reprocessing |
| Rejection reason | Proposals table | Yes | **The rate by reason is a signal**, not a log line |
| Claim + version + evidence | Claim store | Yes | The record itself |
| Contradiction + severity + outcome | Contradiction register | Yes | Precision measurement depends on it |
| **Retrieval record** | New, **sampled** | Sampled | §4 |
| Assembled context | Trace | Sampled | Large. Reconstructable from the retrieval record |
| The answer + claim mapping | Trace | Sampled | The grounding gate already computes the mapping |
| Correctness judgement | **Separate, human or probe** | Yes | §3 |
| Downstream outcome | Outcome ledger | Yes | Probe-measured, later |

**knowledge system events go onto the existing event spine.** `brain.claim.written`,
`brain.contradiction.detected`, `brain.claim.superseded` — no second event
system, no second transport, no change to the replay contract.

---

## 3. How correctness is established — without asking the knowledge system

This is the section the whole document exists for.

### Why the knowledge system cannot judge itself

A model asked to evaluate its own system's output shares a training
distribution, and therefore a set of blind spots, with the model that produced
it. **It leans toward yes, which is the answer you already had.** The same
argument that forbids model self-grading in the runtime forbids it here.

And the specific version for a knowledge system: the knowledge system's confidence in a
claim is a function of corroboration *it* counted, from observations *it*
admitted, extracted by a prompt *it* ran. Every input to its own confidence is
its own output.

### The four instruments that can establish correctness

| # | Instrument | What it establishes | Cost | Bias |
|---|---|---|---|---|
| 1 | **A deterministic probe** | Whether a claim about a system is still true, by inspecting the system | Low, per probe written | **None** — the strongest instrument available |
| 2 | **Independent corroboration from distinct runs** | That several independent observations agree | Free | Vulnerable to a common upstream cause |
| 3 | **A human who owns the subject** | Whether a contradiction was real and worth raising | High, and rate-limited by patience | **The observer-is-the-observed bias** — see `06-validation-strategy.md` §1 |
| 4 | **A held-out question set with known answers** | Temporal and reconciliation accuracy | Built once, from real history | Fixed set; can be overfit |

### The rules

1. **A model judgement may LOWER a verdict and may NEVER RAISE one.** Identical
   to the runtime rule. It makes a model usable here at all, because it can only
   make the system more cautious.
2. **Abstention is a measured success, not a failure.** "I do not know" and
   "this is unresolved" are correct answers. Measure the abstention rate on
   questions whose answer is genuinely absent, **seeded deliberately** so the
   denominator is known.
3. **Contradiction precision is measured as raised-versus-confirmed-by-owner**,
   and the **second number is the one that matters.** A detector with low
   precision gets muted within a week, and then the capability is gone
   regardless of later quality.
4. **The noise floor is measured before any effect size is reported.** Until
   that number exists, every effect size is a number without its error term.
5. **Evaluation runs against a PINNED store snapshot.** A store's contents are a
   function of what runs have happened, so "the same memory" across two subjects
   is only meaningful if it is pinned.

---

## 4. The one new durable record, and its cost

Everything in §1 except one link falls out of records that already exist for
other reasons. The exception is the **retrieval record**: for a given question,
which claims were returned, which were dropped for budget, and under which
`as_of` and scopes.

| | |
|---|---|
| **Why it is needed** | Without it, "the knowledge system gave a bad answer" cannot be separated into *the claim was wrong*, *the right claim was not retrieved*, or *the right claim was retrieved and dropped for budget*. **Those three have completely different fixes** and are indistinguishable afterwards |
| **Why it is expensive** | It is written on the read path, which runs on every model call, and it is proportional to retrieval size rather than to claim count |
| **The resolution** | **Sample it.** A fixed fraction, plus 100% for any question whose answer was later disputed. Sampling is enough for rates and distributions, which is what this is for |

---

## 5. The failures, ranked by how hard they are to see

**Almost none of these produces an error.** That is the point of the ranking.

| # | Failure | What it looks like | Detector | Response |
|---|---|---|---|---|
| 1 | **Confidently wrong current state** | A correct-sounding answer from a claim that stopped being true | Probe loop; contradiction rate | Verification loop; `unverified` as the honest default |
| 2 | **Entity fragmentation** | Claims about one thing scatter across four identities and never join. **Every component works; the system feels useless** | Claims-per-entity distribution; unresolved-mention rate | Anchor on system identifiers; curate aliases; **accept unresolved rather than forcing a match** |
| 3 | **Admission skipped** | The store fills with restatements nothing corroborates. Cost rises with headcount; precision falls | **Discard rate as a headline metric, from before the first source is enrolled** | Make it a metric first, not after |
| 4 | **Authority drift** | The system infers authority from recency or confidence and is wrong exactly when a junior person states something confidently | Ladder is configuration with a named owner | Never let modifiers derive from a model's judgement of tone or seniority |
| 5 | **Self-confirmation through the world** | The agent asserts something, a human internalises it, and later states it as their own belief — a genuine observation from a genuine actor, **indistinguishable from independent corroboration** | Partially detectable via origin tracking | **Not fully solvable.** Recorded as unsolved |
| 6 | **Contradiction fatigue** | Low precision; the detector is muted; capability lost permanently | Raised-vs-confirmed ratio | Conservative `blocking` assignment; measure before volunteering |
| 7 | **Stale claims never re-checked** | An answer from a year-old document with no signal anything is wrong | Verification-status distribution; claim age | The probe loop — **the only proactive mechanism** |
| 8 | **Permission leak through a claim** | A claim extracted from a private channel served to someone outside it. **No error, no log line** | **Only a test** | Capture the permission label at ingest; propagate to every derived claim; **never reconstruct it later** |
| 9 | **Duplicate extraction from redelivery** | Two claims from one text with **different content**, so not recognisable as duplicates | Claims whose evidence cites the same observation twice | Identity-keyed extraction, claimed before the model call |
| 10 | **Extraction prompt regression** | A prompt change quietly halves precision; every downstream number degrades slightly | The reviewed sample, run as a regression test against a measured noise floor | Gate prompt changes on the sample. Reprocess history only after the new extractor beats the old |
| 11 | **Source adapter drift** | An API changes shape; the adapter silently emits fewer observations. **A source that goes quiet looks identical to a quiet team** | Per-source volume, alerted on **absence** | Alert on volume below a per-source floor |
| 12 | **Reprocessing produces a different world** | Replaying the log yields a different claim store than the incremental path did | **The rebuild test, in CI on a seeded log** | Investigate — something downstream holds information never observed |

---

## 6. The signals, and why each is an age, an absence, or a distribution

None of the failures above produces an error, so **none of these alerts on an
error.** Each alerts on an age, an absence, or a distribution shift.

### Day-one signals — build these before any tuning

| Signal | Shape | Detects |
|---|---|---|
| **Discard rate** (per source) | Distribution | Admission skipped, or eating signal |
| **Claims per entity** | Distribution | Entity fragmentation |
| **Contradictions raised vs confirmed** | Ratio | Detector precision, before fatigue sets in |

### Add as the pipeline matures

| Signal | Shape | Detects |
|---|---|---|
| Oldest unprocessed proposal age | **Age** | Pipeline stall |
| Per-source observation volume | **Absence** | Adapter drift |
| Out-of-vocabulary rejection rate | Distribution | Vocabulary needs extending |
| Rejection rate **by reason** | Distribution | Which stage is rejecting, and whether that changed |
| Verification-status distribution | Distribution | Staleness accumulating |
| Promotion rate (provisional → active) | Distribution | Corroboration working, or not |
| Memory tokens per model call | Distribution | Budget creep |
| Scope misses vs vocabulary misses | Two counters, **separately** | Which retrieval fix is warranted — they have different remedies and conflating them makes the trigger unreadable |
| Unresolved-mention rate | Distribution | Entity resolution degrading |
| Poisoning-attempt rate | Rate | Adversarial input |

**Three, not all twenty, on day one.** Each of the three detects a whole failure
class, and a dashboard nobody reads detects nothing.

---

## 7. The debugging walk

The question a flight recorder must answer is *"why did it say that?"* The walk,
given an answer someone disputes:

1. **Which claims did the answer cite?** From the grounding gate's mapping.
2. **For each claim: `brain.why`.** The evidence chain, the source class, the
   decision it rests on, and **what lost**.
3. **Was the right claim in the store at all?** Query the claim store directly,
   ignoring retrieval.
   - **Not present** → an extraction or admission problem. Go to 4.
   - **Present but not retrieved** → a retrieval problem. Go to 5.
   - **Present and retrieved but dropped** → a budget problem. Go to 6.
4. **Find the observation.** Was it ingested? Admitted? Which rule discarded it?
   Was it extracted, and did extraction reject it, and for what reason?
5. **Was it a scope miss or a vocabulary miss?** Different fixes.
6. **What was dropped, and was it one of the three that must never be dropped?**
   Contradictions, provenance pointers, temporal qualifiers.

**Step 3 is the one that requires the retrieval record**, and it is the step
that separates three failures with completely different remedies.

---

## 8. What this design does not detect

Stated plainly, because a flight recorder that implies total coverage is worse
than one that does not.

| Undetected | Why |
|---|---|
| **A claim that is wrong with no contradicting observation and no probe** | Every mechanism except the probe loop is reactive. The runtime cannot feel doubt, so doubt must be manufactured — and manufacturing it for a social fact is unsolved |
| **Self-confirmation mediated through a human** | A person who genuinely believes something the agent told them is a genuine actor making a genuine observation |
| **Causation from organizational outcomes** | A sealed prediction and a measured outcome give the cleanest evidence available at n=1 and **give no causation.** The mechanism check is the only instrument, and only because it was written down first |
| **What the organization does not know** | The knowledge system can say "I have no claims about X", which **conflates three different answers**: nobody has said anything; this does not exist; I cannot see it. The third is a permission fact the asker may not be allowed to learn |
| **Aggregate leakage** | "Three teams are blocked on X" may disclose a private fact. No general solution exists |
