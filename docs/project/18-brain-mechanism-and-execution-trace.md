# The Knowledge System, Made Mentally Executable

**Status of this document:** **DESIGNED / PROPOSED.** It describes mechanism,
not code. **Zero lines of product code exist**, here or anywhere.

Read `PROJECT_BOOTSTRAP.md` §0 for the meaning of the status and evidence
labels. Read `15-vocabulary.md` before coining a name for anything here.

Doc 16 says how the system is **structured**. This document says what actually
**happens** — to one concrete event, step by step, at the level of rows,
indexes and constraints, so that a reader can run the system in their head.

---

## 0. What this is, and why it is not more architecture

`14-outside-in-review-2026-09-14.md:456` lists **"More architecture
documents"** among the things this project should not build, and :374 gives the
reason:

> The most likely failure mode is not a wrong architecture. **It is a correct
> architecture, more of it, indefinitely.**

That warning is correct, and this document is written against it. A9's test is
not length. It is: **does this reduce the number of unknowns between here and
code, or does it add correct structure that nothing consumes?**

So this document is scoped as **the design input to one specific experiment** —
the one `14-outside-in-review-2026-09-14.md:380-385` already specifies: ship
identity-keyed extraction, roughly thirty lines plus a test that a redelivered
observation does not produce a second claim. That test needs four things: the
observation shape, the proposal identity function, the claim identity
constraint, and the idempotency path. **This document makes all four
mechanically executable, and then stops.**

It is measured by what it settled, not by its length. §22 is the accounting.

### 0.1 The scorecard

| # | Finding | Where | Consequence |
|---|---|---|---|
| **1** | **Ten of twenty-eight ADRs rest on a document that is not in this repository.** The *"knowledge system architecture review, 2026-09-05"* is cited at section precision by ADR-0001, 0002, 0003, 0004, 0005, 0006, 0009, 0012, 0013 and 0019 — and does not exist here in any form | §1 | Collides with `README.md:3` — *"The repository is the source of truth; chat history is not."* [ADR-0029](decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md) |
| **2** | **Q7's stated method is not executable.** `10-open-questions.md:120` says to *"read both §37 and §17.3 together and write one page reconciling them."* Half that input is missing | §1.3 | Q7 is not answered — its **method is invalidated**, which is a stronger result. It must be restated before it can be worked |
| **3** | **`PRD.md:822` carries a mislabelled FACT** — *"two documents **in this repository** specify incompatible Phase 1 schemas"* | §1.2 | Under the repo's own rule (*FACT = point at the file*), this one cannot be pointed at |
| **4** | **A complete claim-store DDL exists and had never been read.** 5 enums, 6 tables, 8 indexes, with rationale per column, in a readable `.docx` | §5.1 | The repository was designing around a **retrieval failure**, not an absence |
| **5** | **There is a fourth schema, registered nowhere.** `org_knowledge`, with real DDL, in a source the repository does cite | §5.4 | `01-architecture-map.md` §4.5 registers a "third" shape. This is a fourth, and it **violates EV1** by storing evidence as an integer count |
| **6** | **The recovered schema cannot express `kind` or `source_class`** | §5.3 | ADR-0003's core object and ADR-0006's authority model — **the project's two differentiators** — have no column in the only readable candidate |
| **7** | **Extraction identity is specified two incompatible ways.** ADR-0018 says `(observation_id, extractor_version)`; the recovered DDL says `hash(run_id, episode_seq, observation_digest)` | §10.2 | These key different things, and X1 is one of the eight irreversible properties. New open question |
| **8** | **The PRD's own worked example misstates a date**, and the error is exactly the one bitemporality exists to prevent | §12.2 | Supplies a **real** `observed_at` / `recorded_at` split, on this repository's data, and exercises `observed_at_tier` — a column no document has ever used |
| **9** | **The question the brief asked cannot be asked.** `authentication_mechanism` is not a predicate and cannot become one without discharging Q5 | §6.2 | Mapping onto `current_behaviour` / `intended_behaviour` **sharpens** the trace: intent and reality become two identities that can disagree without colliding |
| **10** | **One call site needs a model.** Of fifteen candidates, one is REQUIRED, two are USEFUL, twelve are NOT NEEDED | §15 | Re-derived independently, then checked against ADR-0010. It agrees |

### 0.2 What this document deliberately does not specify

Following `17-target-repository-structure.md` §1's discipline:

- **Not a schema.** §5 traces against a recovered illustration and says so in
  every caption. It decides nothing about Q7.
- **Not the predicate vocabulary.** Q5 is blocking and stays blocking. Every
  predicate below is one of Q5's seven **hypothesised** candidates.
- **Not the source-precedence policy.** Q2 is blocking. §11 shows the policy as
  **an input the system does not have**, and stops.
- **Not the entity resolver.** Doc 16 §7 makes Phase 1 *anchoring*, not
  resolution. §9 says what anchoring is and what it must not foreclose.
- **Not numbers.** No budget arithmetic, no confidence floor, no decay
  half-life. Those are Q11.
- **Not the distributed design.** Doc 16 §8.4-8.6 did it. §19 cross-references.

**§21 lists what a reader still cannot mentally execute after reading this, and
names the open question responsible for each.** That section is this document's
integrity check.

---

## 1. The finding that comes first

This has to lead, because it changes what every later section is entitled to
claim.

### 1.1 Ten ADRs cite a document that is not here

**[FACT — verifiable in this repository]** Ten of the twenty-eight ADRs give
their *Date / context* as the **knowledge system architecture review of
2026-09-05**, most at section-level precision:

| ADR | What it decides | Cited section |
|---|---|---|
| ADR-0001 | This repository is a knowledge base, not an implementation | Finding 0 |
| ADR-0002 | The specification's vocabulary is canonical for code | — |
| **ADR-0003** | **The core object is a kind-typed claim** | §6.1 |
| **ADR-0004** | **The observation log is the system of record** | §5.3-5.4 |
| ADR-0005 | The world model is a projection, not a store | §5.2 |
| **ADR-0006** | **Authority is authored configuration, never inferred** | *"the hardest and the blocking"* |
| ADR-0009 | No graph database | — |
| ADR-0012 | The agent reaches the knowledge system only through tools | §13.1 |
| ADR-0013 | MCP is a projection of the capability layer | §14 |
| ADR-0019 | One source end to end before breadth | §17, §20.2 |

**The document is not in this repository.** Verified four ways:

1. **No `.md` file contains it.** The string *"Knowledge System Architecture"*
   appears exactly once in the entire Markdown corpus — at
   `01-architecture-map.md:596`, **inside the table that cites it**. The
   citation is self-referential.
2. **No `.docx` is it.** None of the nine carries a 2026-09-05 creation date
   (`docProps/core.xml`); the nearest are 2026-08-30 and 2026-09-07. The phrase
   *"contradiction register"* returns zero hits across all nine.
3. **The file with that title is not it.**
   `../architecture/organizational-brain-architecture.md` is 272 lines with
   sections 0-10. The citations are to §5.2, §5.3, §6.1, §13.1, §14, §17,
   §17.3 and §20.2 — outside its range. It disclaims the role itself at :14:
   *"This document states why; those state what."* Its own §0 Sources table
   lists four sources and does not include such a document.
4. **Nothing was deleted.** `git log --all --diff-filter=D` finds no matching
   file in any commit on any branch.

**[INFERENCE]** The section numbers are internally consistent across ten
independently written ADRs. That is not the signature of a fabrication; it is
the signature of **a real document that existed in a working session and was
never committed.** No falsifier is stated, so this is inference, not hypothesis.

### 1.2 Why this matters more than a missing citation

`docs/project/README.md:3` states the repository's first rule:

> The repository is the source of truth; chat history is not.

**Ten ADRs — including the three that define the core object, the system of
record and the authority model — currently rest on chat history.**

And the error has already propagated into a labelled claim. `PRD.md:822` reads:

> **FACT: two documents in this repository specify incompatible Phase 1 schemas
> and neither acknowledges the other.**

`14-outside-in-review-2026-09-14.md:17` defines that label as *"Verifiable in
this repository, right now — point at the file or run the command."* **One of
the two files cannot be pointed at.** The same assertion appears at
`01-architecture-map.md:593` as *"a real contradiction between two documents in
this repository"*.

### 1.3 What this does and does not do to Q7

**It does not answer Q7. It invalidates Q7's method**, which is a different and
sharper result.

`10-open-questions.md:120` states Q7's next experiment:

> Read both §37 (Memory ADRs) and §17.3 (knowledge system build list) together
> and write one page reconciling them.

**That experiment cannot be run.** Half its input does not exist. Nobody had
noticed, because nobody had tried to run it.

**And reconciling onto the readable side is not available either.** Repo rule 3
(`README.md:49`) forbids resolving a contradiction silently, and
`09-do-not-assume.md:190` makes *"resolve a contradiction between documents by
picking one silently"* a stop. **Picking the readable one because the other
cannot be read is picking one.** Silence is not evidence.

What *is* available is a scope argument from the readable document's own text,
and §5.3 makes it. Both are recorded — as a finding of fact and as a scope
claim, separately, in
[ADR-0029](decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md)
and
[ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md).

---

## 2. The scenario

### 2.1 Why a second worked example

`00-north-star.md` §2 carries the canonical worked example — three sources
disagreeing about cancellation after approval. It exists to show **why
kind-typed claims are necessary**, and it makes that case completely.

It does not show **how the machine runs**. It has no rows, no constraints, no
sequence. A reader who has fully understood it still cannot say what happens
when a commit lands.

This document supplies that, using two scenarios with different jobs:

- **A didactic spine** (§2.2) — an authentication migration, chosen because it
  exercises supersession, rollback and the intent/reality split cleanly.
- **A real-data anchor** (§12.2, §17) — `PRD.md` §8.1's walk W1, run over this
  repository's own commits, so that at least one part of the trace uses values
  nobody invented.

### 2.2 The events

```
  JANUARY
    commit a1b2c3  "Add OAuth authentication"          dana@project-x
    an ADR file in the repo records:
      "Use Google OAuth for authentication."           2026-01-14

  MARCH
    commit 7a8b9c  "Migrate authentication from Google OAuth to Auth0"
                                                       sam@project-x  03-02
  APRIL
    commit e1f2a3  "Revert to Google OAuth pending Auth0 SSO fix"
                                                       sam@project-x  04-11
  JUNE
    commit b4c5d6  "Re-enable Auth0 now that SSO is fixed"
                                                       sam@project-x  06-20

  AND, NOT IN GIT AT ALL
    the service README, last edited February, still says "Google OAuth"
    the production config, read by a probe, says  provider = auth0
```

Then an agent asks:

> *"Why are we using Google OAuth, who decided it, when was the decision made,
> and is it still the current authentication mechanism?"*

Four questions in one sentence. §8 shows they route to four different
capabilities. The last is the interesting one: **the honest answer is no, and
the system must know that without being told.**

### 2.3 Two things this does not decide

**It does not decide Q6.** `08-build-order.md:196` says Stage 1 ingests *"one
adapter — Jira or Git"*. This trace reads commits because they carry clean
identity, timestamps and authorship, which makes the mechanism legible. **That
is a property of the exposition, not a selection.** If this document is later
read as having decided Q6, that is a misreading, and this sentence is the
correction.

**It does not decide Q5.** See §6.2.

---

## 3. The stages, and what each actually does

The pipeline is doc 16 §5's, unchanged. What follows answers, per stage, the
questions the brief asks: what persists, what is derived, what algorithm runs,
and whether a model is involved.

```
  WORLD ---> SOURCE ---> OBSERVATION ---> ADMISSION ---> ANCHORING
                              |                              |
                              |                              v
                              |                          EXTRACTION
                              |                              |
                              |                              v
                              |                    CLASSIFY / RECONCILE
                              |                              |
                              |                              v
                              |                     CLAIM + EVIDENCE
                              |                              |
                              |                              v
                              |                       WORLD MODEL
                              |                              |
                              |                              v
                              |                 RETRIEVAL --> CONTEXT
                              |                              |
                              |                              v
                              |                           AGENT
                              |                              |
                              |                              v
                              +------ NEW OBSERVATION <-- VERIFICATION
```

The loop closes. That is what makes the system correctable rather than merely
populated, and §18 exercises it.

| Stage | What persists | What is derived | Algorithm | Model? |
|---|---|---|---|---|
| **Source adapter** | Nothing — adapters are stateless (A1) | The normalised payload | Poll or receive; normalise; content-hash | **No** |
| **Observation** | **Everything.** The system of record (ADR-0004) | Nothing yet | Append. The content hash makes re-delivery a no-op (A4) | **No** |
| **Admission** | The verdict and its reason | Whether this can carry a claim at all | Deterministic rules first (AD1) | **Only if the rules are inconclusive** |
| **Anchoring** | The entity row, if new | mention -> entity_id | Exact identifier, then curated alias (knowledge-plane E2) | **No** |
| **Extraction** | The proposal row, **claimed before the call** (X1) | Candidate claims | Structured prompt, schema-validated output | **YES — the one place** |
| **Classify / reconcile** | The classification | new / reinforces / contradicts / supersedes | The predicate's `single_valued`, then authority, then time (C1-C3) | **No** |
| **Claim + evidence** | Claim, version and evidence — **one transaction** (CS1) | The new current state | Version CAS, re-classify on conflict (PS4) | **No** |
| **World model** | Nothing durable (WM1) | The current-state projection | Rebuild | **No** |
| **Retrieval** | The retrieval record, sampled | The ranked claim set | One SQL statement (knowledge-plane R2) | **No** |
| **Context assembly** | Nothing | The assembled block | Budget arithmetic, ordering, citations | **No** |
| **Verification** | An **observation** (V1), never a claim | Agreement or disagreement | Run the probe, compare | **No (VR1)** |

**The answer's shape is already visible: eleven stages, one model call.** §15
makes that precise and defends each of the other ten.

---

## 4. Domain concept is not physical storage

Four different things get casually called "the data", and separating them is
what makes §5 readable.

| | What it is | Test that identifies it |
|---|---|---|
| **DOMAIN CONCEPT** | A noun in the design's vocabulary | You can describe behaviour with it without naming a table |
| **PHYSICAL STORAGE** | Bytes you cannot recompute | **Delete it. Is information lost?** |
| **INDEX** | Makes a query fast, answers nothing | Delete it. Queries slow; **no answer changes** |
| **DERIVED PROJECTION** | A materialised consequence of storage | Delete it. **Only rebuild time is lost** (WM1) |

**A domain concept does not imply a table**, and this is exactly where the two
recorded schema positions differ. `02-domain-model.md` §5 records that one
design holds a contradiction is *"fully represented by a version row on each
claim plus an event"*, while the other requires a register with severity. Both
treat *contradiction* as a first-class **concept**. They disagree only about
**storage**. Reading that as a disagreement about the domain is the error this
distinction prevents.

```
  PHYSICAL STORAGE  (delete => information lost)
    observation log          <- the system of record, ADR-0004
    claim versions           <- history, append-only, CS3
    evidence                 <- a table of references, never a count, EV1
    predicate registry       <- authored configuration, ADR-0022
    source-precedence policy <- authored configuration, ADR-0006
                                DOES NOT EXIST. Q2.

  DERIVED PROJECTION  (delete => only rebuild time lost)
    current claim state      <- one row per identity
    world model              <- WM1's delete test defines it
    contradiction register   <- DISPUTED: storage or projection? Q7

  INDEX  (delete => nothing but speed)
    all eight, in section 7.4

  DOMAIN CONCEPT  (never a table on its own)
    standing, authority, staleness, abstention
```

**Authority is the sharpest case.** It is a domain concept of the first
importance and it is **not a table**. It is a *policy* (storage, authored by a
named human) plus a *resolution rule* (code). ADR-0006's whole argument is that
making it inferred — a model, a score, a learned ranking — is the failure mode.
§11 runs it.

---

## 5. The store

### 5.1 What the recovered schema actually says

`01-architecture-map.md` §4.1 instructs that neither schema be built until Q7
is reconciled. **One of the two documents is readable, and its schema had never
been quoted at column level anywhere in `docs/project/`.**

**[FACT — in this repository]** `learning-notes/Memory Management
Architecture.docx` contains a complete PostgreSQL migration: five enums, six
tables (`memory_predicates`, `memory_claims`, `memory_claim_versions`,
`memory_evidence`, `memory_proposals`, `decisions`) and eight named indexes.

**Its own author labels it `[ILLUSTRATIVE REFERENCE CODE]`** — the string
appears seven times, and the migration is headed `SQL -
storage/postgres/migrations/0018_create_memory.sql  [ILLUSTRATIVE REFERENCE
CODE]`.

> **So it is quoted here as what it is: a worked illustration from this
> project's own earlier design work, recovered and read.** Not a ratified
> schema, not adopted below, and §5.5 states that tracing against it decides
> nothing.

The identity constraint, verbatim:

```sql
CONSTRAINT memory_claims_identity
    UNIQUE (tenant_id, scope_path, subject, predicate),
```

That is **CS2**, with its reason written as a comment in the source:

> The OBJECT is deliberately NOT part of the identity (sec 10.1): two claims
> with the same identity and different objects are the same claim disagreeing
> with itself, which is what makes a contradiction a key collision rather than
> an invisible pair.

Much of the current design is visibly **derived from this document**, which is
why reading it is recovery rather than import:

| Recovered DDL | The invariant it is |
|---|---|
| `UNIQUE (tenant_id, scope_path, subject, predicate)` | **CS2**, and **CS4** (tenant in the key) |
| *"TEMPORAL (sec 12). Six fields, three timelines"* | **ADR-0023's** six fields, exactly |
| `version int` — *"version CAS. A stale writer's UPDATE affects zero rows"* | **PS4** |
| `UNIQUE (claim_id, run_id, step_seq)` — *"one run corroborates a claim at most once"* | **ADR-0011** |
| `CHECK (trust <> 'untrusted' OR state <> 'active')` | **M5**, and Stage 1's *"trust rule as a CHECK constraint"* |
| `CREATE INDEX memory_evidence_by_run` | **ADR-0017's** deletion route, by its own comment |

### 5.2 The state after the January events

Illustrative rows against an illustrative schema — a worked example twice over.

```
memory_predicates
  predicate           single_valued
  ------------------  -------------
  current_behaviour   true
  intended_behaviour  true
       ^ from Q5's candidate seven, which 10-open-questions.md labels
         HYPOTHESES, not a decision. Q5 is BLOCKING and stays open.

observations          (shape from 02-domain-model.md 2.1)
  observation_id   obs_7f3a91
  source           git
  actor            dana@project-x
  raw_payload      {commit:"a1b2c3", message:"Add OAuth authentication"}
  occurred_at      2026-01-12T09:14:00Z   <- author date, from the commit
  ingested_at      2026-01-12T09:31:07Z   <- our clock, when we saw it
  content_hash     sha256:3d91...         <- re-delivery is a no-op (A4)
  permission_label repo:project-x:private <- captured AT INGEST (O4, A3)

memory_proposals      (claimed BEFORE the model call -- X1)
  proposal_id      hash(run_id, episode_seq, observation_digest)
  state            claimed -> applied
  classification   new
  claim_id         cl_44b2

memory_claims         (one row per identity)
  claim_id         cl_44b2
  tenant_id        t_01
  scope_path       /project-x/auth-service
  subject          svc:project-x/auth-service
  predicate        current_behaviour
  object           {"value": "google-oauth"}
  state            active
  confidence       0.62
  origin           run
  trust            trusted
  observed_at      2026-01-12T09:14:00Z
  observed_at_tier attested       <- the commit asserts its own date
  recorded_at      2026-01-12T09:31:09Z
  last_confirmed   2026-01-12T09:31:09Z
  superseded_at    NULL
  version          1

memory_claim_versions (append-only; CS3)
  version_id v_1  claim_id cl_44b2  version 1
  object         {"value":"google-oauth"}
  change_reason  new

memory_evidence       (a TABLE of references, not a count -- EV1)
  evidence_id  ev_9001  claim_id cl_44b2
  kind         document
  locator      git://project-x/commit/a1b2c3
  content_digest sha256:3d91...
  observed_at  2026-01-12T09:14:00Z
```

**The claim and its evidence commit in one transaction** (CS1). A claim without
evidence is not a reachable state.

### 5.3 What it cannot express — and the scope argument that follows

Running §2.2's questions against the recovered schema:

| Question | Answerable? | Why |
|---|---|---|
| *"Is Google OAuth still current?"* | **Yes** | Current-state seek on `memory_claims_retrieval` |
| *"What was true in April?"* | **Yes** | `memory_claim_versions` + `memory_versions_asof`. §12 |
| *"When did it change?"* | **Yes** | The version chain is the answer |
| *"Who decided it, and why?"* | **Partly** | The `decisions` table exists here; `02-domain-model.md` §2.12 marks Decision **BLOCKED**. §13.4 |
| *"Which source wins — README or production?"* | **NO** | **No `source_class` column.** No `intent_rank`, no `reality_rank` |
| *"Is this a decision or an observation?"* | **NO** | **No `kind` column.** ADR-0003's six kinds cannot be expressed |

**The two it cannot answer are the two this project exists to answer.**

`00-north-star.md` §2 says of the cancellation example: *"THAT ANSWER IS THE
PRODUCT. Not the retrieval."* That answer requires knowing a product statement
is a DECISION with authority over intent and none over reality. The recovered
schema has `origin` (`run | human | evolve`) and `trust` (`trusted |
semi_trusted | untrusted`). **Neither is `kind`; neither is `source_class`.**
`origin` says who wrote it, `kind` says what sort of assertion it is,
`source_class` says what it outranks. Three different questions.

**[INFERENCE] The scope argument.** This is positive evidence from the document
about itself, not an inference from the absent document's silence:

- `memory_origin` is `ENUM('run','human','evolve')`.
- Evidence `kind` is `run|step|activity|document|probe|human|policy`.
- There is **no adapter, no observation table, and no mention-to-entity
  mapping anywhere in the DDL.**

Those are **runtime provenance categories**. The document scopes itself to a
runtime memory subsystem in its own vocabulary. That supports
`01-architecture-map.md` §4.1's own Hypothesis A — *"the Memory architecture
scopes a runtime memory subsystem over curated, already-identified entities"* —
which that section records as an inference nobody had written down. **It is
still an inference.** What has changed is that it can now be argued from a
readable text rather than from a summary. Recorded as
[ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md).

### 5.4 There is a fourth shape, and nothing registers it

`01-architecture-map.md` §4.5 registers a *third* `entity_store` / `fact_store`
shape in the runtime specification's `knowledge/world/`. **There is a fourth,
with real DDL, in a source this repository does cite.**

**[FACT — in this repository]** `learning-notes/Principal Agent -
Organizational Intelligence Architecture.docx` contains, tagged `[NEW DESIGN —
organizational knowledge]`:

```sql
CREATE TABLE org_knowledge (
  tenant_id           text NOT NULL,     -- in the KEY. Ch 37
  entry_id            text NOT NULL,
  scope               text NOT NULL,     -- ORG | team:x | repo:y
  heading             text NOT NULL,     -- ~40 tokens, always read
  body                text NOT NULL,     -- on request only
  state               text NOT NULL,
  confidence          double precision NOT NULL,
  evidence_episodes   int NOT NULL DEFAULT 1,
  ...
  PRIMARY KEY (tenant_id, entry_id)
);
```

`grep -rn "org_knowledge" --include=*.md .` returns **zero hits.** It is
described in its own source as *"Ch 12's memory entry, org-scoped"*.

**Two things make it worth registering rather than ignoring.**

**It is heading/body-shaped, not subject/predicate/object-shaped.** Its identity
is `(tenant_id, entry_id)` — a surrogate. So two entries asserting different
things about the same subject **do not collide**. The key-collision mechanism
that CS2 exists to create is absent by construction, and with it the whole
contradiction-as-a-database-event design.

**`evidence_episodes int` is an evidence count.** EV1 states the opposite in
terms: *"Evidence is a **table of references**, never an integer count — a count
cannot be joined on"*, and gives three needs that require the join, one of them
ADR-0017's deletion route. **This is a direct conflict with an accepted
invariant**, in a document the repository cites as a source for the Principal
Agent's objects.

Registered in `01-architecture-map.md` §4.7 and folded into Q7.

### 5.5 The delta, and what this does not decide

What Phase 1 would need that the recovered illustration does not have:

| Gap | Required by | Cost of adding late |
|---|---|---|
| `kind` on the claim | ADR-0003 | A backfill nobody can perform — **the kind of a past claim is not recoverable from its row** |
| `source_class` on the claim | ADR-0006, §11 | Same. Knowable at ingest, unrecoverable later |
| An entity table | knowledge-plane E1 | Claims already written cannot be joined retroactively; `01-architecture-map.md` §2.4 calls joining afterwards *"strictly harder than never splitting them"* |
| A contradiction register | CR1-CR3 | **Genuinely open.** Its only recorded advocate is the absent document. §1 |

> **This decides nothing about Q7.** It establishes what one readable
> illustration contains, and where it falls short of requirements accepted
> elsewhere in this repository. The entities / relations / contradiction-register
> question is now **reopened with no prior**, because its only recorded advocate
> cannot be read.

---

## 6. Understanding the question

### 6.1 Does this need a model?

Take the narrowest of §2.2's questions: *"What authentication mechanism does
Project X currently use?"* The target is a structured query:

```
  subject    = svc:project-x/auth-service
  predicate  = current_behaviour
  scope      = /project-x/auth-service
  as_of      = <the run's clock>
  principal  = <explicit, CL1>
```

Seven ways to get there:

| Method | Gets there? | Cost | Deterministic | Fails by |
|---|---|---|---|---|
| **Rule / grammar parse** | Templated questions only | ~0 | Yes | Rejecting anything unphrased |
| **Structured API** — caller passes the fields | **Always** | 0 | Yes | Not being natural language at all |
| **Predicate match** — lexical, against the registry | Usually, for a closed vocabulary | ~0 | Yes | Synonyms the registry does not carry |
| **Lexical / BM25 over claims** | Finds text, not fields | Low | Yes | Ranking, not routing |
| **Embedding match to predicates** | Usually | One embed call | **No** | Confidently picking a near-miss predicate |
| **Classifier** | After training data exists | Low | No | **No training data exists** |
| **LLM planner** | Nearly always | High, on the read path | **No** | Inventing a predicate not in the registry |

**[DESIGN DECISION]** The boundary that follows:

> **An agent calling the knowledge system passes structured fields. A human
> typing a sentence gets a translation step. The translation never reaches the
> store — it produces a query object, which is validated against the predicate
> registry, and an out-of-vocabulary result is a rejection rather than a guess.**

The reason is not cost. It is that **the registry is closed** (ADR-0022), so a
translator has a finite, enumerable target. Lexical matching against seven to
twenty entries does not need a model, and a model asked to choose from a closed
list will eventually choose something not on it.

**Checked against the existing record — and the record is stronger.** ADR-0012
already requires the agent to reach the knowledge system *only through tools*,
and CL1 requires an explicit Principal on every capability. **A tool call is a
structured query.** So for Phase 1's only consumer, the translation question
does not arise at all. That position was reached first and is better than the
one this section derived independently; §6.1's contribution is to say what
happens *if* a natural-language surface is ever added.

### 6.2 The question the brief asked cannot be asked

A predicate `authentication_mechanism` **does not exist, and inventing one here
would breach a blocking constraint.** Q5 (`10-open-questions.md:83-95`) is
**BLOCKING for extraction**: the vocabulary should be *"roughly twenty, drawn
from real questions people actually ask — not from a taxonomy"*, and **the real
questions have not been collected.** Its seven candidates — `ownership`,
`dependency`, `current_behaviour`, `intended_behaviour`, `process`, `term`,
`constraint` — are labelled **Hypotheses**, not a decision.

So the trace uses `current_behaviour` and `intended_behaviour`. **This is not a
workaround. It is a better trace:**

```
  "authentication_mechanism = google-oauth"
      ONE fact. Says nothing about whether it is true, intended, or stale.

  current_behaviour  = auth0          <- what the system DOES
  intended_behaviour = google-oauth   <- what we DECIDED it should do

      TWO claims at TWO identities. They disagree without colliding,
      and their disagreement is the answer 00-north-star.md 2 calls
      "the product".
```

A predicate named for the domain object collapses intent and reality into one
slot, so the only way for them to differ is a contradiction at a single
identity — which `01-architecture-map.md` §2.6 warns is the *wrong*
classification, because **intent and reality disagreeing is normal and not an
error.**

**[INFERENCE]** Small evidence for ADR-0022's instruction to derive predicates
from questions rather than taxonomies: a taxonomy of an auth service yields
`authentication_mechanism`; the questions people actually ask — *"what does it
do"*, *"what did we decide"* — yield the pair. No falsifier is stated, so this
is inference, not hypothesis.

**And a small result on Q5.** Two predicates are sufficient to demonstrate the
entire mechanism — collision, classification, contradiction. That is evidence
the *"roughly twenty"* figure is a **vocabulary-coverage** question, not a
**mechanism** question. It de-risks Q5 slightly. It does not answer it.

---

## 7. Retrieval

The brief asks four questions — compare architectures, design the pipeline,
design the indexes, say when vectors help. They are facets of one mechanism.

> **Codes, and a namespace collision to watch.** `R1`-`R4` below are the
> **knowledge plane's** retrieval invariants (`01-architecture-map.md` §2.12).
> The handbook uses `R1`-`R22` for **runtime** invariants and `E1`-`E6` for
> **evolution** containment; those are unrelated to the `R1`-`R4` and `E1`-`E2`
> used here. Where a code appears without a qualifier in this document, it is
> the knowledge plane's.

### 7.1 Six architectures

| | Solves | Latency | Determinism | Explainability | Fails by | Phase 1? |
|---|---|---|---|---|---|---|
| **A. Structured** | "The claim at this identity" | One index seek | **Total** | **Total** — the query *is* the explanation | Silence when the subject was never resolved | **Yes** |
| **B. Lexical / BM25** | "Text I half-remember" | Low | Total | High | Vocabulary mismatch; ranks by term stats, not authority | No |
| **C. Embedding** | "Things that mean this" | Embed + ANN walk | **No** | **Low** — "it was near" is not a reason | **Recall collapse under a selective filter** | **No — ADR-0008** |
| **D. Graph traversal** | "What depends on this, two hops out" | Grows with hops | Total | High | Unbounded fan-out | **No — ADR-0009**; recursive CTE instead |
| **E. Hybrid** | Coverage when one path misses | Highest | No | **Lowest** — fused ranks resist explanation | Inherits every failure above, plus the fusion's | No |
| **F. LLM-planned** | "Work out what to query" | Highest | No | Moderate | Invents predicates; cost on every call | No |

**Re-derived verdict: A, and only A, in Phase 1.** Three reasons, by weight:

1. **Structure is exact where it applies.** The scopes are known *before* the
   query rather than inferred from it. Similarity adds nothing to a key lookup.
2. **The one query shape this store always has is the shape ANN handles worst.**
   Every read carries a highly selective tenant predicate. Approximate indexes
   apply metadata filters *after* walking the graph, so under a selective filter
   the walk can return candidates that all fail it and **recall collapses.**
3. **R4 requires the permission predicate to be a pre-filter inside the store.**
   An architecture whose filtering is necessarily post-hoc cannot satisfy R4.

**Checked against the record:** this lands exactly where **ADR-0008** landed,
including reason 2, which that ADR states in nearly these words. That is
**corroboration, not proof** — the same reasoning reaching the same place twice
is weaker evidence than it looks. What it does establish is that the decision
survives re-derivation from a concrete trace rather than from principle.

### 7.2 The pipeline

Retrieval is not "search everything and rank". It is a funnel that narrows
deterministically before anything is ordered.

```
  QUERY OBJECT            principal, scope, subject, predicate, as_of, budget
      |
      v
  NORMALISE               resolve subject -> entity_id; validate predicate
      |                   against the registry.
      |                   OUT OF VOCABULARY -> REJECT, and count it (X2)
      v                                                      deterministic
  CANDIDATE GENERATION    claims whose subject IS this entity, in scope
      v                                                      deterministic
  FILTER                  authorization  -- PRE-filter, in the store (R4)
      |                   validity       -- as_of within the interval
      |                   standing       -- state, confidence floor
      |                   ALL THREE IN ONE SQL STATEMENT (R2)
      v                                                      deterministic
  RANK                    deterministic order. No model, no score that
      v                   cannot be recomputed                deterministic
  EVIDENCE EXPANSION      join memory_evidence per surviving claim
      v                                                      deterministic
  CONTRADICTION EXPANSION open contradictions touching these claims
      |                   NEVER dropped for budget (CA1)
      v                                                      deterministic
  CONTEXT ASSEMBLY        budget arithmetic, ordering, citation format
                                                             deterministic
```

**Every stage is deterministic.** None is statistical, embedding-based or
model-based. That is what §15 has to defend, and it is why the whole read path
can be tested with fixtures rather than an eval set.

**A denied read raises** (R3); it does not return empty. Doc 16 §10.2 records
that another published system reached the opposite design and documented the
resulting footgun in its own material: a scoped read returning empty is
*"indistinguishable from having no data"*, so a bug that should page someone
looks like a quiet afternoon.

### 7.3 What is actually searched

Not "the vector database". Specifically:

| Store | Searched at read time? | Why |
|---|---|---|
| **Claims** (current state) | **Yes — this is the read path** | One row per identity is what the question asks for |
| **Evidence** | **Yes, by join**, after claims are selected | Never searched first; it has no independent question |
| **Contradictions** | **Yes**, expanded from selected claims | CA1 forbids dropping them |
| **Claim versions** | **Only for `as_of` / `history`** | The present is answered by the current-state layer |
| **Entities** | Only to **resolve the subject**, before retrieval proper | Identity is schema, not a claim |
| **Observations** | **No. Never on the read path** | The system of record and the rebuild source, not an index |
| **World model** | Only where the question is about the projection | Authoritative for nothing (WM1) |

**The observation log is never read to answer a question.** It is the most
complete store in the system and the read path ignores it entirely. It exists
for O5: drop everything downstream, replay, arrive at the same state.

### 7.4 The indexes

`04-implementation-map.md` records that no index inventory exists. **It does.**
The recovered migration carries eight, each with its purpose as a comment:

```sql
-- R1, the hot-path query. Partial, mirroring Ch 17's partial expiry
-- index: cost scales with ACTIVE claims, not with all claims ever held.
CREATE INDEX memory_claims_retrieval
    ON memory_claims (tenant_id, scope_path, recorded_at)
    WHERE state = 'active';

-- The as-of read (sec 12.6) and the audit answer.
CREATE INDEX memory_versions_asof
    ON memory_claim_versions (claim_id, recorded_at DESC);

-- Ch 37 sec 5.4's deletion route. Without this index, deleting a
-- tenant's runs cannot find the claims that cite them, and the store
-- fails the enumeration.
CREATE INDEX memory_evidence_by_run ON memory_evidence (tenant_id, run_id);
```

The full set:

| Index | Serves | Note |
|---|---|---|
| `memory_claims_identity` (UNIQUE) | **Contradiction detection** | The mechanism, not an optimisation |
| `memory_claims_retrieval` | The hot read path | **Partial** — scales with active claims, not history |
| `memory_claims_curation` | The decay and retirement sweep | Partial on `provisional, active` |
| `memory_versions_asof` | `as_of` and `history` | §12 depends on it |
| `memory_evidence_one_per_run` (UNIQUE) | **ADR-0011's corroboration count** | An integrity constraint, not a lookup |
| `memory_evidence_by_run` | **ADR-0017's deletion route** | Named as required for the enumeration |
| `memory_proposals_expiry` | Crash recovery of in-flight extractions | Partial on `claimed` |
| `memory_proposals_signals` | The rejection-rate metric | X2's vocabulary-miss signal |

**Three observations the trace forces.**

**The two most important are uniqueness constraints, not lookups.**
`memory_claims_identity` is how a contradiction is *detected at all* — CS2's
"key collision rather than two rows that both retrieve".
`memory_evidence_one_per_run` is how ADR-0011's corroboration cannot be gamed by
one run observing twice. Neither is a performance structure, and a reader
skimming for "the indexes" will mistake both for bookkeeping.

**No index serves authority resolution**, because no column supports it (§5.3).
When `source_class` is added, an index on it is not optional: §11's resolution
is a sort on precedence, and without the column that sort cannot run.

**Two indexes serve a job current decisions have not authorised.**
`memory_claims_curation` serves decay and retirement sweeps. ADR-0024 forbids
autonomous knowledge curation. These are not strictly in conflict — ADR-0024
forbids a *model* rewriting the store, and mechanical confidence decay is a
different act — but the index is evidence the earlier design assumed a sweep
that no current ADR authorises. Recorded in §22.

### 7.5 When a vector index would actually help

Not "when retrieval is bad". Specifically: **when the subject cannot be
resolved, or the predicate cannot be routed.** ADR-0008 already names the
instrumentation that distinguishes them — **scope misses and vocabulary misses,
counted separately**, because they have different remedies.

Applied here: asking about *"the login service"* when the entity is
`svc:project-x/auth-service` and no alias exists is a **scope miss**. Asking
*"which identity provider"* when the registry holds only `current_behaviour` is
a **vocabulary miss**. The first wants alias curation. The second wants a new
predicate. **Neither wants an embedding.**

An embedding earns its place when the miss rate is high *and* alias curation and
vocabulary extension have both been tried and are not keeping up. That is
ADR-0008's pre-registered trigger, and nothing in this trace changes it.

---

## 8. Four questions, four capabilities

§2.2's sentence is four questions. They route differently, which is the argument
for the capability set being more than one `search()`.

| The question | Capability | What runs | Model? |
|---|---|---|---|
| *"Is Google OAuth still current?"* | `entity` | Current-state seek on `memory_claims_retrieval` | No |
| *"Who decided it, and when?"* | `why` | Evidence chain plus the decision record — §13 | No |
| *"When did it change?"* | `history` | The version chain via `memory_versions_asof` | No |
| *"What was true in April?"* | `as_of` | Same chain, bounded by valid time — §12 | No |
| *"Do our sources disagree?"* | `conflicts` | Open contradictions touching these claims | No |
| *"Everything relevant, within a budget"* | `context_for` | The §7.2 funnel end to end | No |

Stage 1 ships **three** — `entity`, `why`, `conflicts` (`08-build-order.md:196`).
`history` and `as_of` are Phase 3, when the bitemporal columns written in Stage 1
start paying.

**Why these are not one capability with a mode flag.** Each returns a
differently-shaped object: `entity` returns claims, `why` an evidence chain and
what lost, `conflicts` pairs with severity, `as_of` a claim set bound to a past
instant. Collapsing them forces a union type whose shape depends on an argument,
which makes CL2 (every capability returns provenance) and CL3 (every result set
is bounded) harder to enforce against.

---

## 9. Entity anchoring — and why this is not entity resolution

Doc 16 §7 makes Phase 1 **anchoring, not resolution**: *"Identity, not
resolution across sources"*, with full resolution triggered by the second
source. So the question *"are `auth-service`, `authentication-service` and
`OAuth service` the same thing?"* is **deliberately not answered in Phase 1**,
and designing the resolver now would be building Phase 2 during Phase 1.

What Phase 1 does:

```
  MENTION IN A PAYLOAD
      |
      v
  EXACT SYSTEM IDENTIFIER?    repo path, service id, issue key
      |  yes -> anchored. Done. No model, no similarity.
      v  no
  CURATED ALIAS?              a human-maintained table, E2
      |  yes -> anchored.
      v  no
  UNRESOLVED                  accept it as unresolved. Do NOT force a match.
```

**The last step is the one that matters.** E2 says *"accept unresolved mentions
rather than forcing a match"*, and E1 says resolution runs **before** extraction,
because *"extraction that does not know which entity it is discussing produces
claims that cannot be joined"* — and joining afterwards is *"strictly harder
than never splitting them"*.

The cheapest reliable sequence is therefore: **exact identifier, then curated
alias, then stop.** Normalisation (case, separators) is free and safe. Fuzzy
matching, embeddings and a model are all **absent by design**, not by omission
— each of them can produce a *confident wrong merge*, and a wrong merge is the
one entity error that is expensive to reverse, because Q16 (the merge/split
lifecycle) **does not exist**.

**What Phase 1 must not foreclose:** the alias table has to be *curated
data*, not inferred, so that resolution can later be added above it without
re-deriving what is already anchored.

---

## 10. Extraction — the one model call

### 10.1 Where the line falls

A commit message says *"Migrate authentication from Google OAuth to Auth0."*
Six ways to turn that into a candidate claim:

| Method | Handles it? | Why it is or is not enough |
|---|---|---|
| **Deterministic field read** | The metadata, completely | Author, date, repo, commit hash need no interpretation, ever |
| **Parser / grammar** | Conventional-commit prefixes | Breaks on the first message not written to the convention |
| **Rules / regex** | Keyword spotting | *"Migrate X to Y"* is tractable; *"switch back for now"* is not |
| **Small classifier** | Routing, after training data exists | **No training data exists.** Circular in Phase 1 |
| **Embedding** | Similarity, not structure | Produces a neighbourhood, not a `(subject, predicate, object)` |
| **LLM** | **Yes** | It is the only method that maps arbitrary prose onto a closed schema |

**So: everything factual is deterministic, and exactly one step is not.** The
metadata — who, when, which commit, which repo, which permission label — never
touches a model. What needs a model is only the mapping from *unstructured
prose* to *a candidate claim in a closed vocabulary*, and the model **proposes**
it (ADR-0010: *"A model proposes candidate claims. It never writes one"*).

### 10.2 The mechanic that makes a crash safe — and a divergence

X1 and ADR-0018 require the extraction row to be **claimed before the model
call, not after**:

```
  1. compute a DETERMINISTIC proposal id
  2. INSERT it -- UNIQUE key. If it already exists, STOP: already done.
  3. ... now call the model ...
  4. validate output against the predicate's object_schema
  5. classify, reconcile, and write claim + evidence in ONE transaction
```

Crash between 2 and 5 and the retry finds the row and does not call the model
twice. Crash before 2 and nothing happened. **The window in which a redelivered
observation could produce a second claim never opens.** That is precisely the
property the one-week experiment at `14-outside-in-review-2026-09-14.md:380-385`
is meant to test, and it is why ADR-0018 says to build it *first*.

**But the deterministic id is specified two incompatible ways.**

| Source | The identity |
|---|---|
| **ADR-0018** (and `02-domain-model.md` §2.2) | `(observation_id, extractor_version)` |
| **The recovered DDL** — `memory_proposals.proposal_id` | `hash(run_id, episode_seq, observation_digest)` |

**These key different things.** ADR-0018's is keyed to *an observation and the
code version that read it*, so re-extracting the same observation with an
improved extractor is a **new** attempt. The recovered form is keyed to *a run,
a position in it, and the content*, so the same observation seen in two runs is
two attempts, and an extractor upgrade is invisible to the key.

**[INFERENCE]** This is consistent with §5.3's scope argument — a runtime memory
subsystem keys by run because runs are its unit; an organizational store keys by
observation because observations are its unit. It is consistent, not proven.

**X1 is one of doc 16 §8.2's eight irreversible properties**, so this is not a
detail to settle during implementation. Registered as a new open question.

---

## 11. Reconciliation

### 11.1 The three-way disagreement

By April, three sources say different things:

```
  the README      (edited February)    "Google OAuth"
  the March commit                     "migrated to Auth0"
  production config (read by a probe)  provider = auth0
```

The machine steps, in order, with no model anywhere:

```
  1. IDENTITY       all three are about (svc:.../auth-service,
                    current_behaviour) in one scope
                    -> the second write is a KEY COLLISION on
                       memory_claims_identity. Not a similarity score.
                       A database event.

  2. CARDINALITY    the predicate registry says single_valued = true
                    -> both cannot be true
                    -> SUPERSESSION or CONTRADICTION, never coexistence
                    (C3: this "cannot be read from two sentences")

  3. AUTHORITY      which source class outranks which, ON REALITY?
                    -> ***THE POLICY DOES NOT EXIST***

  4. TIME           later observation of the same predicate, from a
                    source with authority over reality -> SUPERSEDES
                    -> superseded_at, superseded_by, and a new version
                       row with change_reason = 'supersedes'
```

### 11.2 It is deterministic, and it is blocked

**Steps 1, 2 and 4 need no model and no judgement.** A key collision is a
constraint violation. Cardinality is a column in the registry. Time comparison is
arithmetic on `observed_at` with its tier.

**Step 3 is the whole problem, and it is missing.** ADR-0006 is **ACCEPTED —
UNEXECUTED**, and its consequence line states the situation plainly:

> Until the policy exists, every downstream mechanism — resolution,
> contradiction, retrieval ranking — is meaningless.

Concretely, in this scenario: **is a README an authority on what the system
currently does?** A source-precedence policy would say no — documentation has
authority over *intent* and weak authority over *reality*, while a production
probe has strong authority over reality and none over intent. That ordering is
exactly the two-dimensional ranking (`intent_rank`, `reality_rank`) that
`02-domain-model.md` §2.10 specifies and **that nobody has authored** (Q2,
blocking).

**What an LLM contributes here: nothing at the decision.** ADR-0006 rejected
*"let a model judge authority per conflict"* and states the reason — this
*"cannot be solved by an LLM. It is a GOVERNANCE act."* A model asked which
source should win produces a plausible ordering that nobody agreed to, is not
reproducible across calls, and cannot be appealed. **The value of the authority
model is that a human can be pointed at it and disagree.**

So the honest state of §11: the mechanism is fully specified and fully
deterministic, and it **cannot run**, because one of its four inputs is a file
that does not exist.

---

## 12. Time

### 12.1 The sequence

```
  JAN   google-oauth   commit a1b2c3
  MAR   auth0          commit 7a8b9c
  APR   google-oauth   commit e1f2a3   (rollback)
  JUN   auth0          commit b4c5d6
```

Four questions, four deterministic queries, **no model in any of them**:

| Question | How | Index |
|---|---|---|
| *"What is current?"* | The current-state row, `state = 'active'` | `memory_claims_retrieval` |
| *"What was true in April?"* | Latest version whose valid interval contains 2026-04-20 | `memory_versions_asof` |
| *"When did it change?"* | The version chain itself — four rows, each with `change_reason` | `memory_versions_asof` |
| *"Why do we believe the current one?"* | Its evidence rows plus the version that superseded its predecessor | `memory_evidence` by `claim_id` |

**The rollback is the interesting case, and it is why supersession must not be
deletion.** In April the claim reverts to a value it already held in January.
The version chain does not collapse those into one: `v1 google-oauth`,
`v2 auth0`, `v3 google-oauth`, `v4 auth0` are four distinct versions, and
*"what was true in April"* is answerable only because v3 exists as its own row
with its own interval. **CS3 — append-only versions, retirement is not
deletion — is what makes the rollback legible** rather than looking like the
March migration never happened.

### 12.2 A real bitemporal error, in this repository

The scenario above is constructed. **This one is not**, and it exercises the
same machinery on data anyone can check.

`PRD.md:554` — inside walk W1, the repository's own best test case — records
an observation as:

> prd.md, committed **2026-09-06**

**That is wrong as a git fact.** `prd.md` enters the current history in commit
`b1ec292`, dated **2026-09-14**. 2026-09-06 is the date *written inside* the
document and its sibling research files (`docs/product/README.md:3`:
*"Research conducted 2026-09-06, before the PRD was written"*).

The two dates are not in competition. **They are `observed_at` and
`recorded_at`, and the PRD has conflated them:**

```
  observed_at       2026-09-06   <- what the document says about itself
  observed_at_tier  attested     <- asserted by the source, not verified
  recorded_at       2026-09-14   <- when the log actually saw it
  observed_at_tier  for THAT     <- exact: it is our own commit timestamp
```

This is O3 in one line — *"a log recording only ingestion time can never recover
truth time"* — and it is the first use anywhere in `docs/project/` of
`observed_at_tier`, a column the recovered schema declares `NOT NULL` with
`ENUM('exact','attested','inferred')` and which no document has referenced.

**[EVIDENCE]** That the project's own most carefully written worked example
conflates valid time with transaction time, on its own data, is a small piece of
evidence that ADR-0023's six fields are not over-engineering. The distinction is
easy to lose **even when you are writing the document that argues for it.**

ADR-0023's guard applies directly and would have caught it: *"an **inferred**
valid time may not supersede an **attested** one."* Here the attested date
(2026-09-06) and the exact one (2026-09-14) are both retained, and neither
overwrites the other.

---

## 13. "Why" is five different questions

### 13.1 The senses

| Sense | What is being asked | Can the system answer it? |
|---|---|---|
| **Decision record** | *"Who decided this, when, on what authority?"* | **Yes** — if a Decision exists. §13.4 |
| **Evidence chain** | *"What observations support this claim?"* | **Yes.** `memory_evidence` joined on `claim_id`. This is the one that always works |
| **What lost** | *"What did we believe instead, and why did it stop winning?"* | **Yes.** The version chain plus `change_reason` |
| **Human rationale** | *"What was the reasoning?"* | **Only if someone wrote it down.** It is a stored field, never derived |
| **Inferred explanation** | *"Construct a plausible account"* | **NO, and this is the important refusal** |

**The fifth is the failure mode the whole design exists to prevent.** A model
handed a claim and asked *"why?"* will produce a fluent rationale that reads
exactly like the four retrievable answers and is not connected to anything. That
is `00-north-star.md` §2's warning in a different costume: the output is
confident, well-formed, and its relationship to the evidence is unknowable.

**So `why` retrieves; it does not explain.** When there is no decision record
and no rationale field, the correct output is *"no decision record exists for
this claim"* — an abstention, which `organizational-brain-architecture.md` §5
lists as principle 12 and flags as the second most likely to be abandoned under
pressure.

### 13.2 What `why` returns for our scenario

```
  claim         (svc:project-x/auth-service, current_behaviour) = auth0
  standing      active, confidence 0.71, corroborated by 2 distinct runs
  temporal      observed_at 2026-06-20 (attested)
                recorded_at 2026-06-20
                supersedes v3 (google-oauth, April)
  evidence      git://project-x/commit/b4c5d6   (document)
                probe:prod-auth-config           (probe, 2026-06-21)
  what lost     v3 google-oauth, superseded 2026-06-20,
                change_reason = 'supersedes'
  decision      *** none linked ***
  contradiction the README still asserts google-oauth, UNRESOLVED
                (blocked on the source-precedence policy, Q2)
```

**Everything in that block is a stored value or a join.** Nothing is generated.
That is what §14 means by deterministic assembly.

### 13.3 The decision record, when one exists

The recovered DDL specifies `decisions` with exactly the fields the question
needs, and its comments say why:

> **ALTERNATIVES:** what was considered and not chosen. Without this the record
> cannot answer "why not X", which is half of what "why did we decide" means.

> **AUTHORITY:** on whose authority. A decision without one is a suggestion.

Fields: `statement`, `subject`, `context` (*"Frozen, because the situation is
not re-derivable later"*), `alternatives`, `rationale`, `mechanism`,
`authority_actor`, plus a sealed prediction. This corroborates
`02-domain-model.md` §2.12 closely, including *"a decision has no confidence —
We did not *maybe* decide."*

### 13.4 And in Phase 1 it is not available

`02-domain-model.md` §2.12 marks the Decision object **BLOCKED, not deferred** —
blocked on an organizational act, not on engineering. `08-build-order.md` puts
Decisions in **Stage 7**, gated on goals existing, written by a human, with
measures and baselines: *"Until then this stage cannot start."*

**So `why` ships in Stage 1 and cannot answer the decision sense of "why" until
Stage 7.** What it answers instead is the evidence chain, the temporal standing,
and what lost — which is three of the five senses and is not nothing. But a
reader who expects *"who decided Google OAuth"* to work in Phase 1 will be
disappointed, and no document currently says so. Recorded in §21.

---

## 14. Context assembly

### 14.1 What the agent actually receives

```
  CONTEXT BLOCK  for principal=agent:reviewer, as_of=2026-06-25
  --------------------------------------------------------------
  CLAIM   auth-service current_behaviour = auth0
          active, confidence 0.71, 2 corroborating runs
          valid from 2026-06-20 (attested)
          evidence: commit b4c5d6 | probe prod-auth-config

  CLAIM   auth-service intended_behaviour = google-oauth
          active, confidence 0.55
          valid from 2026-01-14 (attested)
          evidence: decision file in repo

  CONTRADICTION  intent and reality disagree on this service.
                 severity: advisory.  UNRESOLVED.

  NOT FOUND      no decision record links the June change to an author.

  --------------------------------------------------------------
  budget: 412 of 1500 tokens
```

Four properties are load-bearing:

- **Contradictions are present**, and CA1 forbids dropping them for budget.
- **Provenance is present** per claim (CL2), as handles rather than prose.
- **Temporal qualifiers are present** — the third of CA1's three un-droppables.
- **What was *not* found is stated.** `01-architecture-map.md` §3 requires this
  on the upward boundary: *"what was NOT found, and what could not be resolved"*.
  An absence stated is information; an absence omitted is indistinguishable from
  a claim that nothing was missing.

### 14.2 No model assembles this

Assembly is budget arithmetic, a deterministic ordering, and a citation format.
Every value is retrieved. The temptation is to summarise when the budget is
tight — and ADR-0024 forbids exactly that, because a summary is a new,
unattributed assertion with no evidence row, which breaks the chain
`07-brain-observability.md` §1 exists to keep intact.

**When the budget binds, the system drops whole claims — lowest standing first —
and says how many it dropped.** It never compresses one.

**The honest gap:** the ordering *policy* and the budget *arithmetic* are not
specified numerically anywhere, and `13-audit-2026-09-14.md:187` already records
this — *"The three un-droppable items are specified; the actual algorithm is
not."* This document does not close it, because the numbers depend on Q11.

---

## 15. Where the model actually belongs

Fifteen candidate call sites, each classified, with the reason a deterministic
method is insufficient wherever one is.

| # | Call site | Verdict | Why |
|---|---|---|---|
| 1 | **Ingestion** | **NOT NEEDED** | Fetch, normalise, hash. Nothing to interpret |
| 2 | **Parsing** (metadata) | **NOT NEEDED** | Author, date, hash, path are fields, not prose |
| 3 | **Admission** | **USEFUL** | AD1: deterministic rules first, *"a cheap model runs second, and only if the deterministic stage is inconclusive."* The discard rate is a headline metric, so the model's contribution is measurable |
| 4 | **Entity anchoring** | **NOT NEEDED** | Exact identifier, then curated alias, then accept unresolved (E2). A model here produces confident wrong merges, and Q16 has no reversal |
| 5 | **Extraction** | **REQUIRED** | **The one place.** Mapping arbitrary prose onto a closed schema has no deterministic method. Everything factual around it is deterministic |
| 6 | **Classification** | **NOT NEEDED** | C1: *"Deterministic. The first tests use no model."* Cardinality is a registry column |
| 7 | **Reconciliation** | **NOT NEEDED** | ADR-0006: a governance act, not an inference. §11.2 |
| 8 | **Query understanding** | **NOT NEEDED** in Phase 1 | A tool call is already structured (ADR-0012). USEFUL only if a natural-language surface is added — §6.1 |
| 9 | **Query planning** | **NOT NEEDED** | The plan is: resolve subject, validate predicate, filter, order. There is nothing to plan |
| 10 | **Retrieval** | **NOT NEEDED** | One SQL statement (R2) |
| 11 | **Ranking** | **NOT NEEDED** | Deterministic order. A learned ranker cannot be explained, and *"what lost"* is a product requirement |
| 12 | **Context assembly** | **NOT NEEDED** | Arithmetic and formatting. Summarising is forbidden (ADR-0024) |
| 13 | **Answering** | **REQUIRED — but outside** | The consuming agent generates prose. **That is not the knowledge system.** The boundary is exactly here |
| 14 | **Planning / deciding** | **Outside** | The Principal Agent, Stage 6+. P3: it may *propose* a goal, never write one |
| 15 | **Verification interpretation** | **NOT NEEDED** | VR1: *"No model is involved."* VR3: a model judgement may **lower** a passing verdict and may never raise a failing one |

**One REQUIRED inside the boundary. Two USEFUL. Twelve NOT NEEDED.**

**Checked against the record:** ADR-0010 already says *"extraction runs at run
end, off the critical path, as one call per run"*, and `01-architecture-map.md`
§2.5 already calls extraction *"the one place an LLM is unavoidable."* The
enumeration agrees. What the enumeration adds is that **the other fourteen have
now been named**, which matters because ADR-0010 is enforced by *where the calls
are* — and a boundary nobody has enumerated is a boundary nobody can lint.

**The asymmetry at sites 13 and 15 is the design's spine.** A model may write
prose *from* retrieved knowledge (13) and may *lower* a deterministic verdict
(15). It may never write a claim (ADR-0010, X3), never raise a verdict (VR3),
and never raise standing (C4, M4). **Every arrow the model is permitted to push
points toward less confidence, never more.**

---

## 16. Three architectures, briefly

The brief asks for three whole-system alternatives compared and one
recommended. **Most of that comparison has already happened** — §7.1 compared
six retrieval architectures and §15 classified fifteen model call sites, which
between them are what distinguishes these three. So this section states the
alternatives, gives the verdict, and does not rebuild the matrix.

| | **A. Deterministic-first** | **B. Hybrid retrieval** | **C. LLM-heavy semantic** |
|---|---|---|---|
| Retrieval | Structural only | Structural + lexical + vector, fused | Vector, planned by a model |
| Model call sites | 1 required, 2 useful | 3-4 | 8+ |
| Reproducibility | **Total.** Same inputs, same rows | Partial — fusion is stable, the vector leg is not | **None** that matters |
| Explainability | The query *is* the explanation | Fused ranks resist explanation | Post-hoc narration |
| Cost per read | One index seek | Seek + embed + ANN | Embed + ANN + one or more model calls |
| Handles ambiguity | **Badly** — rejects unroutable rather than guessing | Well | Very well |
| Verifiable knowledge | Yes — every claim joins to evidence | Yes, where the structural leg found it | **Weakly** — generated text has no evidence row |
| Rebuildable | Yes (O5) | Yes, plus an index rebuild | Yes, but answers are not reproducible |

**Recommended: A.** The deciding argument is not cost or latency. It is that
**B and C both break `why`.**

This project's differentiator, as `07-organizational-knowledge-landscape.md` §5
states it, is being *"the only organizational brain that can say why it believes
something, which source lost, and when it would refuse to answer."* A fused rank
cannot say which source lost — it can only say which scored higher, and the
score is not a reason. A generated explanation cannot say it either, and is
worse, because it will produce one anyway.

**A's cost is stated plainly, not minimised:** it handles ambiguity badly. A
question phrased outside the vocabulary is rejected rather than approximated,
and ADR-0008 already accepts this consequence in terms — *"Phase 1 cannot find a
claim whose wording differs from what a run is looking for."* The remedy is
alias curation and vocabulary extension, both of which are human work, and
§7.5's counters are what tell you when that work is falling behind.

**Checked against the record:** ADR-0008 (no embeddings), ADR-0009 (no graph
database) and ADR-0010 (the model proposes and never writes) already compose to
architecture A, each with a pre-registered reconsideration trigger. **This
comparison adds no new decision.** What it adds is the observation that the
three ADRs are not independent: they are one architectural position taken three
times, and a future session relaxing any one of them should know it is relaxing
the position, not a local choice.

---

## 17. The trace, end to end

Twenty-two steps. Columns: what goes in, what happens, what comes out, what
persists, which index, whether a model runs, and how it fails.

**Mapped onto `07-brain-observability.md` §1's twelve-stage chain**, so that the
two do not become rival accounts of the same system. The mapping is clean, and
where it is not, that is recorded as a finding in §17.2.

| # | Step | Persists | Index | Model? | Fails by |
|---|---|---|---|---|---|
| **WHAT IT SAW** |||||
| 1 | Commit `7a8b9c` lands in `project-x` | — | — | No | — |
| 2 | Adapter polls, normalises, content-hashes | — | — | No | Adapter outage: a gap with no marker unless the cursor is durable |
| 3 | Observation appended with all four ingest-time fields | **observations** | — | No | **Missing `permission_label` here is unrecoverable (O4)** |
| 4 | Re-delivery of the same commit | nothing — no-op | content hash | No | A non-deterministic hash makes every redelivery a new row |
| **WHAT IT ADMITTED** |||||
| 5 | Deterministic admission rules run | verdict + which rule | — | No | Over-admission floods extraction; the discard rate is the signal (AD2) |
| 6 | Model admission, only if inconclusive | verdict + stage | — | **USEFUL** | A model asked too often turns a cheap stage expensive |
| **WHAT IT RESOLVED** |||||
| 7 | `project-x/auth-service` -> `entity_id` by exact identifier | entity row if new | entity identifier | No | Forcing a match on a near-miss; **unresolved must be recorded, not dropped** |
| **WHAT IT EXTRACTED** |||||
| 8 | **Proposal row claimed BEFORE the call** | **memory_proposals** | PK, deterministic | No | **If this is after the call, a crash re-calls the model and can double-write** |
| 9 | Model proposes candidate claims | — | — | **REQUIRED** | Hallucinated subject; out-of-vocabulary predicate |
| 10 | Output validated against `object_schema` | — | — | No | A permissive schema lets malformed objects through |
| **WHAT IT REJECTED** |||||
| 11 | Out-of-vocabulary -> reject, with a reason | `reject_reason` | `memory_proposals_signals` | No | Rejections not counted by reason: X2's signal is lost |
| **WHAT IT ACCEPTED** |||||
| 12 | Identity computed; write attempted | — | `memory_claims_identity` | No | — |
| 13 | **Key collision detected** | — | the UNIQUE constraint | No | Object in the identity would make this two rows that both retrieve (CS2) |
| 14 | `single_valued` consulted -> supersession or contradiction | — | `memory_predicates` PK | No | Guessing cardinality from text (C3 forbids it) |
| 15 | Authority consulted | — | — | No | **THE POLICY DOES NOT EXIST (Q2). The step cannot run** |
| 16 | Supersession: `superseded_at`, `superseded_by`, new version | **claims + versions** | — | No | Overwriting instead of versioning destroys `as_of` forever |
| 17 | Claim + evidence in **one transaction** | **evidence** | — | No | Two transactions leave claims with no evidence (CS1) |
| **WHAT CORROBORATED / CONTRADICTED** |||||
| 18 | Corroboration counted across **distinct** runs | evidence rows | `memory_evidence_one_per_run` | No | One run observing twice inflates standing (ADR-0011) |
| **WHAT IT RETRIEVED** |||||
| 19 | Agent asks; §7.2's funnel runs | retrieval record, sampled | `memory_claims_retrieval` | No | Permission applied post-hoc instead of as a pre-filter (R4) |
| **WHAT CONTEXT IT PROVIDED** |||||
| 20 | Context assembled; contradictions retained | — | — | No | Dropping a contradiction for budget (CA1) |
| **WHAT ANSWER CAME OUT** |||||
| 21 | The agent reasons over the block | — | — | **Outside the boundary** | Treating retrieved context as instruction rather than evidence |
| **WAS IT RIGHT / WHAT HAPPENED AFTERWARDS** |||||
| 22 | Probe reads production config, writes an **observation** | **observations** | — | **No (VR1)** | A probe writing a claim directly would break O5 and V1 |

**Step 22 re-enters at step 3.** That is the loop closing, and §18 is what
happens when it disagrees.

### 17.1 The four things the one-week experiment needs

Per §0, this document exists to make one experiment executable. Those four
things are steps 3, 8, 12 and 13:

```
  OBSERVATION SHAPE      step 3.  Eight fields; four of them irreversible
                                  if omitted (O3, O4).
  PROPOSAL IDENTITY      step 8.  Deterministic, UNIQUE, claimed BEFORE
                                  the model call.
                                  *** SPECIFIED TWO WAYS. See 10.2. ***
  CLAIM IDENTITY         step 12. UNIQUE (tenant, scope, subject, predicate).
                                  Object excluded, deliberately.
  IDEMPOTENCY PATH       step 4 + step 8. Redelivery is a no-op at the
                                  observation layer AND at the proposal layer.
                                  Two different mechanisms; both required.
```

**The test is: deliver the same commit twice, assert one claim.** Everything
above is what makes that assertion meaningful rather than accidental. **Step 8's
identity must be settled before the test is written**, because the test's
outcome depends on which of the two identities is used — with the recovered
form, the same observation arriving in two different runs produces **two**
proposals and the test fails for a reason that is not a bug.

### 17.2 Where the mapping is not clean

Three mismatches between this trace and the twelve-stage chain, each a finding:

| Mismatch | Detail |
|---|---|
| **The chain requires `kind`** | Stage *WHAT IT EXTRACTED* records *"proposed claim, kind, predicate"*. **The recovered schema has no `kind` column** (§5.3) |
| **The chain requires `source_class`** | Stage *WHAT IT ACCEPTED* records *"claim_id, version, status, source_class, confidence, validity"*. **The recovered schema has no `source_class` column** |
| **The chain sides with ADR-0018 on extraction identity** | It records *"proposal_id, **extractor_version**"*. The recovered DDL's key has no `extractor_version` in it (§10.2) |

**[EVIDENCE]** The observability chain was written independently of this trace
and independently of the recovered schema, and it requires **exactly the two
columns §5.3 found missing plus the identity field §10.2 found divergent.** That
is three independent arrivals at the same delta, which is stronger support for
§5.5's gap list than the trace alone provides.

---

## 18. The failure trace

The system can be wrong. This is what that looks like and how it recovers —
following `PRD.md` §8.4's walk W4 rather than inventing a second debugging
procedure.

**The situation:** the knowledge system believes `current_behaviour = auth0`.
Production is actually running Google OAuth, because the June deploy was rolled
back at the infrastructure level and no commit records it.

```
  1. HOW THE BELIEF FORMED
     Commit b4c5d6 said "Re-enable Auth0". That was TRUE of the code.
     It was never true of production. The claim is not a lie and not a
     bug -- a commit has authority over what the repository contains,
     and no authority over what is deployed.
     *** This is ADR-0003's kind distinction doing real work, and it is
         the distinction the recovered schema cannot express. ***

  2. HOW IT WAS STORED
     claim cl_44b2  object {"value":"auth0"}  state active
     confidence 0.71, corroborated by 2 distinct runs
     evidence: commit b4c5d6, and a probe reading the DEPLOY CONFIG
               (not the running service)
     -> plausible, evidenced, and wrong

  3. HOW RETRIEVAL EXPOSED IT
     The agent asks "is Auth0 current?" and gets auth0, with evidence
     and a validity interval. NOTHING IS ANOMALOUS. Retrieval cannot
     detect this -- the store is internally consistent.
     -> a wrong belief is not a retrieval failure, and no amount of
        better retrieval finds it

  4. HOW VERIFICATION DETECTS IT
     The predicate declares verifiable_by = probe:prod-auth-endpoint.
     The probe reads the RUNNING SERVICE, not the config.
     It observes: google-oauth.
     -> PROBE_DISAGREES

  5. HOW THE NEW OBSERVATION ENTERS
     The probe WRITES AN OBSERVATION (V1). It does not write a claim,
     and it does not edit cl_44b2.
     It re-enters the pipeline at step 3 of section 17 -- the same
     path a commit takes. No privileged write path exists.

  6. HOW STANDING CHANGES
     New observation -> same identity -> KEY COLLISION
     -> single_valued -> supersession or contradiction
     -> a probe has authority over REALITY; a commit does not
     -> SUPERSESSION.
        cl_44b2 v4 (auth0)     superseded_at = now
        cl_44b2 v5 (google-oauth) active, origin=probe
     Confidence on the superseded version is LOWERED, never flipped
     (03-lifecycles-and-state-machines.md 4).

  7. HOW HISTORY IS PRESERVED
     v4 IS STILL THERE. "What did we believe on 1 July, and why?"
     still answers auth0, with its evidence, and now also answers
     "and that was wrong -- superseded on <date> by a probe."
     -> CS3: retirement is not deletion. THE WRONG BELIEF IS PART OF
        THE RECORD, which is what makes the system auditable rather
        than merely current.
```

**Three properties are doing the work, and each is cheap now and impossible to
retrofit:**

- **V1** — a probe writes an observation, never a claim. If probes wrote claims
  directly, the store would contain rows with no observation behind them and
  **O5's rebuild would silently produce a different state.**
- **CS3** — versions are append-only. Overwrite the claim and step 7 becomes
  unanswerable, permanently, for every row already written.
- **ADR-0003's kinds** — step 6's resolution depends on a probe outranking a
  commit *on reality*. Without `kind` and `source_class`, step 6 has nothing to
  decide with and degrades to last-write-wins.

**And the honest limit.** Step 4 is the only mechanism here, and it only fires
for predicates that declare a probe. `01-architecture-map.md` §2.13 states it:
verification is *"the only proactive mechanism in the whole design"*, and it
covers *"only probe-verifiable predicates, which will be a minority."* For
everything else — a decision that quietly stopped being followed, an owner who
left — **noticing that a claim is wrong with no new observation is
`10-open-questions.md` §3's STRUCTURALLY UNSOLVED**, and nothing in this trace
changes that.

---

## 19. Distributed evolution

Doc 16 §8.4-8.6 answers this: twenty distributed properties classified against
the invariant codes, all thirty-nine runtime invariants walked against a
single-writer deployment, and a five-stage topology path. **It is not repeated
here.**

What this trace adds is one observation about *where* the concurrency actually
is. Every step in §17 is single-writer-safe except three, and all three are
already carried by named invariants:

| Step | The concurrency | Held by |
|---|---|---|
| 8 | Two workers extracting the same observation | The proposal's UNIQUE key — **the identity is the lock** |
| 12-16 | Two writers reconciling against the same claim | **PS4: version CAS with *re-classify* on conflict, not retry** |
| 18 | Two runs corroborating simultaneously | `UNIQUE (claim_id, run_id, step_seq)` |

**PS4 is the one worth re-reading.** The rule is re-classify, not retry: if a
CAS fails, the claim changed underneath, so the *classification* — new,
reinforces, contradicts, supersedes — may no longer be the right one. Retrying
the write would apply yesterday's verdict to today's state. That distinction is
invisible at one writer and load-bearing at two, which is precisely doc 16
§8.5's *"defer the machinery, keep the shape."*

---

## 20. What becomes required, and when

### 20.1 The delta against doc 16

Doc 16 §7 already tabulates required-now against required-later per subsystem.
Only the rows this trace changes are listed.

| Item | Doc 16 | After this trace |
|---|---|---|
| Claim-store schema | DISPUTED, pending Q7 | **Still disputed, and Q7's method is invalid.** §1.3 |
| Index set | Not addressed | **Recovered, eight, annotated.** REQUIRED NOW — §7.4, ADR-0031 |
| `kind` and `source_class` | Assumed present | **Named as absent from the only readable candidate.** REQUIRED NOW — irreversible |
| Extraction identity | REQUIRED NOW (X1) | **Still required, and its definition is contested.** §10.2 |
| Query understanding | Not addressed | **NOT REQUIRED.** A tool call is already structured — §6.1 |
| Contradiction register | DISPUTED | **Disputed, with no readable advocate.** §5.5 |
| Decision records | BLOCKED, Stage 7 | Unchanged — but **`why` ships in Stage 1 without them.** §13.4 |

### 20.2 The smallest executable path

```
  observation  ->  durable storage  ->  deterministic extraction
       ->  claim  ->  evidence  ->  structural retrieval  ->  context
```

Each arrow is a step in §17. Nothing else is on the path.

### 20.3 Triggers

The four primitives that already carry triggers in `08-build-order.md` §4 keep
them verbatim; they are not re-derived here. The rest:

| Introduce | Only when | Source |
|---|---|---|
| **Embeddings / vector index** | Scope misses and vocabulary misses, **counted separately**, cross the pre-registered threshold — and alias curation and vocabulary extension have both been tried | ADR-0008 |
| **Graph storage** | A recursive CTE over relations is measurably the bottleneck at a hop depth real questions need | ADR-0009 |
| **LLM extraction** | **Now — it is the one required call site** (§15) | ADR-0010 |
| **LLM query planning** | A natural-language surface exists *and* structured translation demonstrably fails on real questions | §6.1 |
| **Distributed workers / queues** | Ingest lag exceeds the freshness a real question needs, at one writer | Doc 16 §8.6 |
| **MCP** | An external agent needs the capability surface, and Q9 is decided first | ADR-0013, Q9 |
| **Runtime kernel** | Stage 6. **Not before** — doc 16 §9 puts the 39 invariants' activation there | `08-build-order.md` |

---

## 21. What you still cannot mentally execute

The integrity check. Each row is something a reader cannot run in their head
after reading this document, and the reason is an open question rather than an
omission.

| Cannot execute | Why | Blocked on |
|---|---|---|
| **Which source wins a conflict** | The source-precedence policy does not exist. §11.2 shows the step and cannot run it | **Q2**, blocking |
| **What the twenty predicates are** | The real questions have not been collected. §6.2 uses two hypothesised candidates | **Q5**, blocking |
| **Whether a contradiction blocks or advises** | No severity rule exists | **Q15** |
| **Cross-source entity resolution** | Phase 1 is anchoring only; the merge/split lifecycle does not exist | **Q16**, and the phase boundary |
| **What the confidence floor and decay half-life are** | No number has been calibrated; no noise floor measured | **Q11** |
| **How overlapping permissions are modelled** | `scope_path` assumes knowledge nests; real scopes overlap | **Q10** |
| **Which claim-store schema is being built** | §1.3. Q7's method is invalid and must be restated | **Q7** |
| **Which extraction identity is correct** | §10.2. Two incompatible specifications | **New — Q23** |
| **What the budget algorithm is** | Three un-droppables are specified; the arithmetic is not | **Q11**, and `13-audit-2026-09-14.md:187` |

**Seven of nine were already open before this document.** Two are new. That
ratio is the honest measure of what a paper trace can do: it mostly **locates**
existing unknowns precisely, and occasionally finds one nobody had counted.

---

## 22. What this document decided, and what it did not

### 22.1 Decided

| Decision | Where |
|---|---|
| The 2026-09-05 review is not in this repository, and ten ADRs cite it | [ADR-0029](decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md) |
| The recovered schema scopes a runtime memory subsystem, argued from its own text | [ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md) |
| The Phase 1 index set, recovered and ratified | [ADR-0031](decisions/ADR-0031-the-phase-1-index-set.md) |

### 22.2 Not decided, deliberately

- **Q7.** Its method is invalid; restating it is a separate act, and reconciling
  onto the readable side would be picking one silently.
- **The contradiction register.** Now reopened with **no prior**, since its only
  recorded advocate cannot be read.
- **The predicate vocabulary, the precedence policy, every number.** Q5, Q2, Q11.
- **Extraction identity.** §10.2 registers the conflict; choosing between two
  specifications of an irreversible property is an owner's decision.

### 22.3 Registered as new contradictions

| # | What |
|---|---|
| 1 | A fourth claim-store shape, `org_knowledge`, registered nowhere and **violating EV1** by storing evidence as an integer count — §5.4 |
| 2 | Extraction identity specified two incompatible ways — §10.2 |
| 3 | `memory_claims_curation` indexes a decay sweep that no current ADR authorises, and ADR-0024 forbids the adjacent act — §7.4 |

### 22.4 The one thing to do next

**Settle §10.2 — which deterministic identity an extraction attempt has.**

It is the smallest of the open items and it blocks the largest: the one-week
experiment at `14-outside-in-review-2026-09-14.md:380-385` is a test that a
redelivered observation produces one claim, and **that test cannot be written
until this is chosen**, because the two candidate identities give different
correct answers. X1 is one of the eight irreversible properties, so it is also
the cheapest thing on this list to get wrong.

---

## Related

- [16-high-level-implementation-architecture.md](16-high-level-implementation-architecture.md) — structure; this document is mechanism
- [07-brain-observability.md](07-brain-observability.md) — the twelve-stage chain §17 maps onto
- [PRD.md](PRD.md) §8 — walks W1-W4; §18 follows W4's spine
- [10-open-questions.md](10-open-questions.md) — Q2, Q5, Q7, Q10, Q11, Q15, Q16
- [01-architecture-map.md](01-architecture-map.md) — the invariant codes used throughout
- [ADR-0029](decisions/ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md) · [ADR-0030](decisions/ADR-0030-the-recovered-schema-scopes-runtime-memory.md) · [ADR-0031](decisions/ADR-0031-the-phase-1-index-set.md)
