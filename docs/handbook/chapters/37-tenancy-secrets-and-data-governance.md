```
  Level 4 · Chapter 37
  TENANCY, SECRETS, AND DATA GOVERNANCE
  Requires   C12 The Memory System, C16 The Observation System,
             C25 The World Model, C31 Safety and Sandboxing,
             C34 Observability
  Unlocks    C41 Evaluation Infrastructure, C44 The Evolve Agent,
             C48 Governance
  Diagrams   Core (5)
```

# Chapter 37 — Tenancy, Secrets, and Data Governance

---

## 1. Motivation

### 1.1 Cold open

A customer terminates their contract and asks for their data to be deleted.

The team takes it seriously. They delete the customer's runs, their plans, their effect ledger rows,
their memory entries, their stored repository snapshots, and their account. Someone writes a script,
someone else reviews it, and a third person checks the row counts afterwards. A confirmation letter
goes out on the Friday.

Six weeks later a support engineer is searching the trace store for an unrelated bug — a
`search_files` behaviour on large monorepos — and one of the top results is a trajectory from four
months earlier. In it, verbatim, is the terminated customer's proprietary pricing engine: forty
files of source, an internal architecture document that had been pasted into an issue, and a
customer list that appeared in a test fixture.

Nothing was done wrong by anyone involved. The trace store was built by the observability team, for
debugging. Its retention was set to twelve months against a storage budget. It was never classified
as containing customer data, because it contains *traces* — and it was never in the deletion path,
because nobody who wrote the deletion script knew it needed to be.

The store holds, by design, everything the model could see (Chapter 16). Which is everything the
customer had.

### 1.2 In plain language

Several customers share one system. Keeping their data apart sounds like adding a customer column to
a table and filtering on it.

It is not one table. Information about a customer's work ends up in nine or ten different places:
the run records, the plans, the traces, the memory system, the cached beliefs about their
environment, the ledger of effects, the queue of unresolved problems, the approval decisions. Some of
those were built by different people at different times for different reasons, and two of them are
*designed* to carry information from one run to another — which is exactly what makes them useful
and exactly what makes a leak between customers possible.

Then there is deletion. When a customer asks for their data to be removed, every one of those places
needs a route by which it can be removed. A store with no such route will still hold the data after
the letter goes out, and nobody will find out until somebody searches it for something else.

And there is one thing that cannot be undone at all. If a customer's data was used to derive
something — a set of learned patterns, an adjusted model, a statistic baked into a configuration —
then deleting the original does not remove it from what was derived. That has to be understood
*before* the derivation happens, because afterwards there is no operation that fixes it.

### 1.3 Why this chapter exists

Chapter 16 built the observation system on a strong argument: capture what the model *could see*,
because a corpus recording only what it did explains nothing. Chapter 34 kept that corpus for
months, because Chapter 41 will need it and Chapter 44 will learn from it.

Both were right, and together they built the most sensitive dataset in the architecture without
either chapter being about data protection. This one is.

The specific gap is that a trace store is usually owned by whoever owns observability, classified as
telemetry, and retained against a storage budget. Every one of those is a reasonable default for
telemetry. None of them is right for a verbatim archive of customers' source code, and the
misclassification is invisible because the store's name and its owner both suggest something else.

`[BP]` The single most useful thing in this chapter is a question, and it can be asked this
afternoon: *is our trace store in the deletion path, and has anyone tested that it is?* The answer,
on a system that has not thought about it, is reliably no.

### 1.4 What previous framings got wrong

**"Tenancy is a column."** It is a column on nine stores, two of which are cross-run by design and
where a missing key produces a leak with no error at all.

**"Traces are telemetry."** Latency numbers are telemetry. A trajectory contains, verbatim, whatever
was in context — which is customer source, issue text, log output, and anything a user pasted. The
classification error is the cold open.

**"Redact on read."** Then the raw material exists on disk and every future reader is a new
exposure, every new access path is a new risk, and — the part that gets missed — a deletion request
cannot reach data that was never classified as sensitive in the first place.

**"Deletion is a script."** A script covers the stores its author knew about. A deletion *capability*
is a property each store declares and a test exercises, and the difference shows up six weeks later.

**"We can delete from the training corpus."** You can delete the rows. If a model was tuned on them
or a statistic was derived from them, the deletion does not reach the derived artefact, and there is
no operation that does. §5.5 states this rather than working around it.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A hospital has two places where a patient's information lives, and they are governed completely
differently.

The **medical record** is a formal system. It has access control, an audit log, a retention schedule,
a defined owner, and a process for correction and deletion. Everyone knows it is sensitive and it is
treated accordingly.

The **doctor's own notebook** contains a great deal of the same information. It has no access
control, no retention policy, and no owner beyond the doctor. It is where the actual work happens,
it is more candid than the record, and it is not what anyone thinks of when asked where patient data
is kept.

That is the trace store exactly. The runs table is the medical record — classified, owned, in the
deletion path. The trace store is the notebook: the same information, in richer form, governed by
nobody, and left out of the answer when someone asks where the customer data is.

The break is in scale and reach, and it is what makes the analogy understate the problem rather than
overstate it.

A notebook is **one person's, physically bounded, and illegible to everyone else**. It holds what one
doctor chose to write. Nobody can search every doctor's notebook at once.

A trace store is machine-generated, complete rather than selective, indexed, full-text searchable,
retained for months, and readable by every engineer with a login. The support engineer in the cold
open was not doing anything unusual — searching it is the intended use. The informal-artefact
problem, which was tolerable on paper because paper is small and awkward, becomes the primary
exposure once the artefact is complete, permanent, and queryable.

### 2.2 Why tenancy is a property of every store

```
  (1) Several customers share one runtime. Their data must not
      reach each other.

  (2) Obvious answer: a tenant column on the runs table, filtered
      on every query.

  (3) But a run's information lands in NINE stores, not one:
      runs, plans, traces, memory, world-model beliefs, effect
      ledger, dead letters, authority decisions, and any golden
      set built from real cases.

  (4) Two of those are CROSS-RUN BY DESIGN. Memory (C12) exists
      to carry what one run learned into another. World-model
      beliefs (C25) are shared across runs at the same commit,
      which is the property that makes the expensive probe
      affordable.

  (5) Cross-run within one tenant is the intended behaviour and
      is valuable. Cross-TENANT is a leak -- and it produces no
      error, because from the store's perspective it is doing
      exactly what it was built to do.

  (6) So the tenant key belongs on every store, including the
      derived ones, and must be enforced at WRITE rather than at
      read. A read filter that is forgotten returns other
      people's data; a write key that is missing makes the row
      unwritable.

  (7) Deletion then needs a route through all nine. A store with
      no deletion route holds the data after the letter goes out,
      and nobody discovers it until they search for something
      else.

  (8) And a store whose contents were used to DERIVE something --
      a tuned model, an aggregated statistic, a golden set -- has
      no deletion route in the sense the request means. Deleting
      the rows does not reach the derivative. This must be known
      BEFORE the derivation, because afterwards there is no
      operation that fixes it.
```

Step (5) is the leak nobody catches in testing, because a single-tenant test environment cannot
produce it. Step (8) is the one that has to be decided before Chapter 44 exists.

### 2.3 Nine stores, and the two that are forgotten

| Store | Chapter | Tenant key? | Deletion path? | Usually forgotten |
|---|---|---|---|---|
| Runs and plans | C10, C24 | Obvious | Obvious | No |
| Effect ledger | C27 | Obvious | Needs care — obligations outlive runs | Sometimes |
| Authority decisions | C30 | Obvious | **Retain longer than traces** (C30 §7.2) | Sometimes |
| Dead letters | C27 | Obvious | Needs an owner | Sometimes |
| **Trace store** | C16, C34 | **Frequently absent** | **Frequently absent** | **The cold open** |
| **Memory** | C12 | **Cross-run by design** | Rarely built | **Yes** |
| **World-model beliefs** | C25 | **Shared by commit** | Rarely built | **Yes** |
| Golden set | C28 | If built from real cases | Must not be deletable ad hoc | Yes |
| Derived artefacts | C41, C44 | Not applicable | **No such operation** (§5.5) | Yes |

The three bold rows are where the work is. Everything else has an obvious key and an obvious
deletion path, and teams get them right.

The trace store is missed because of its classification (§1.3). Memory and world-model beliefs are
missed because their cross-run nature is a *feature* that was designed in deliberately, and the
tenant boundary was not part of that design conversation — it came up later, in a different
conversation, with different people.

### 2.4 The mental model to carry

Every store has a tenant key enforced at write, and a declared deletion path that a test exercises.
Sensitive material is redacted at capture, because redaction at read leaves the original and cannot
be reached by a deletion request. Secrets never enter a trajectory at all. And anything derived from
customer data is, for deletion purposes, permanent — which makes it a decision to take deliberately
rather than a consequence to discover.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
   |  Customer material: source, issues, logs, pasted content   |
   +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
                            |
                            | (1) the ONLY ingress (C31 sec 3.1)
                            v
   +--------------------------------------------------------------+
   |     PROVENANCE TAGGER (C31) + REDACTOR + TENANT STAMPER      |
   |                                                              |
   |   redaction happens HERE, at capture. Never at read (5.3).   |
   |   tenant is stamped HERE, and is required to write anywhere. |
   +--------------------------------------------------------------+
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
   +----------+     +---------------+    +------------------+
   | RUN      |     | TRACE STORE   |    | CROSS-RUN STORES |
   | STORES   |     |               |    |                  |
   |          |     | C16, C34      |    | memory     (C12) |
   | runs     |     |               |    | beliefs    (C25) |
   | plans    |     | the HIGHEST-  |    |                  |
   | ledger   |     | RISK data set |    | cross-run WITHIN |
   | letters  |     | in the whole  |    | a tenant: yes    |
   | decisions|     | architecture  |    | cross-TENANT: a  |
   |          |     |               |    | leak with NO     |
   |          |     |               |    | error (2.2)      |
   +----------+     +---------------+    +------------------+
        |                   |                   |
        +-------------------+-------------------+
                            |
                            | (2) every store declares a
                            |     deletion route, and a test
                            |     exercises it
                            v
   +--------------------------------------------------------------+
   |                    DELETION EXECUTOR                         |
   |   enumerates STORES, not tables. A store with no declared    |
   |   route fails the enumeration LOUDLY rather than being       |
   |   skipped silently.                                          |
   +--------------------------------------------------------------+
                            |
                            | (3) and one route that does not exist
                            v
   +==============================================================+
   |  DERIVED ARTEFACTS: tuned models, aggregate statistics,      |
   |  golden sets built from real cases                           |
   |                                                              |
   |  NO DELETION OPERATION EXISTS. Decide before deriving (5.5). |
   +==============================================================+

  Figure 37.1 -- Ingress, nine stores, and the one route that does not
                 exist (D1 High-Level Architecture)

  (1) Chapter 31 already made this the sole ingress path for
      provenance reasons; redaction and tenant stamping ride on it
      for free
  (2) enumeration over stores rather than tables is what catches the
      store somebody built last quarter
  (3) the double border is not decoration: this boundary cannot be
      crossed by any deletion request
```

### 3.1 One ingress, three jobs

Chapter 31 established a single ingress path so that provenance could be labelled at fetch time.
That path now carries three labels rather than one — provenance, tenant, and redaction status — and
the reason to note it explicitly is that the marginal cost is close to zero.

`[BP]` This is worth designing for deliberately rather than discovering. A system with several
ingress paths needs redaction, tenant stamping, and provenance implemented at each, and the fourth
one added next year will have two of the three.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                     GOVERNANCE MACHINERY                       |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |    Capture redactor      |  |     Tenant enforcer       |   |
   |  |                          |  |                           |   |
   |  |  patterns: credentials,  |  |  the key is required to    |  |
   |  |  tokens, keys, known     |  |  WRITE, not applied on     |  |
   |  |  secret shapes           |  |  READ (2.2 step 6)         |  |
   |  |                          |  |                           |   |
   |  |  runs BEFORE the write,  |  |  a forgotten read filter  |   |
   |  |  never after (5.3)       |  |  returns other tenants'    |  |
   |  |                          |  |  data; a missing write key |  |
   |  |  irreversible by design  |  |  makes the row unwritable  |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |   Store registry         |  |    Deletion executor      |   |
   |  |                          |  |                           |   |
   |  |  every store DECLARES:   |  |  enumerates the REGISTRY  |   |
   |  |    tenant key field      |  |                           |   |
   |  |    deletion route        |  |  an undeclared store is a |   |
   |  |    retention window      |  |  LOUD failure, not a      |   |
   |  |    classification        |  |  silent skip              |   |
   |  |                          |  |                           |   |
   |  |  a store not in the      |  |  emits a per-store         |  |
   |  |  registry cannot be      |  |  certificate of deletion   |  |
   |  |  written to              |  |                           |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 37.2 -- Inside the governance machinery (D2 Low-Level
                 Architecture)
```

### 4.1 The store registry is the mechanism that makes this survive

Everything else in this chapter is a policy that decays. Registration is the part that does not,
because it fails at the moment the mistake is made rather than six weeks later.

Every store declares four things: which field carries the tenant, how to delete a tenant's rows,
how long rows are retained, and what classification the contents carry. A store that has not
declared them cannot be written to.

`[BP]` Enforce it at the persistence layer rather than by convention, and make the failure occur in
development. The engineer adding a store next quarter then discovers the requirement in the first
five minutes rather than never, and the deletion executor's enumeration is complete by construction
rather than by diligence.

This is the same technique used four times already — Chapter 26's `repair` without a goal,
Chapter 28's `Judge` without reasoning, Chapter 31's capability without content, Chapter 32's
operations requiring a lease handle. Make the wrong thing unrepresentable rather than discouraged.

### 4.2 Redaction is irreversible and that is the point

The capture redactor destroys rather than encrypts. A redacted credential is gone, not recoverable
with a key, and this is a deliberate choice with a real cost: a debugging session that would have
benefited from seeing the value cannot.

The reason to accept that cost is that reversible redaction is a key-management problem wearing a
data-protection costume. The material still exists, the exposure moves to the key, and the key lives
in a system that will eventually be misconfigured. `[BP]` Redact irreversibly, and when a debugging
session genuinely needs a value, reproduce it in a non-production environment with test credentials
rather than recovering it from production capture.

---

## 5. Secrets, Cross-Run Leakage, and What Cannot Be Deleted

### 5.1 Secrets never enter a trajectory

Chapter 31's capability broker issues short-lived, narrowly scoped credentials per step. The
governance requirement here is one line: **the trajectory records that a credential was used, never
its value.**

Three leak paths, in increasing order of how easily they are missed:

- **The credential passed as a tool argument, and arguments are captured.** Handled by the broker
  injecting into the environment rather than the argument list, and by the redactor as a backstop.
- **A tool echoing its arguments in an error message.** `curl: (22) ... Authorization: Bearer
  sk-live-...` is a real error message from a real tool, and the observation system captures error
  messages verbatim because Chapter 15 argued that errors are instructions.
- **A credential in a file the run read.** A `.env` committed to a repository, a config file, a test
  fixture. The run reads it legitimately, and it enters the trajectory as file content.

`[BP]` The redactor must therefore run over *all* captured material — tool arguments, tool output,
error text, and file content — with a pattern set covering known credential shapes plus the shapes
this system issues. And the second bullet deserves its own test: a deliberate tool failure with a
credential in scope, asserting the trajectory is clean, run in CI.

### 5.2 Cross-tenant leakage through memory and beliefs

This is the leak that produces no error and cannot be found by testing in a single-tenant
environment.

**Memory** (Chapter 12) exists to carry what one run learned into another. Its value is proportional
to how specific the memories are — Chapter 20 §5.5 already noted that specific memories perform
better and leak, and placed the memory abstraction outside the evolvable workspace for that reason.
Here the same tension arrives from the governance side, independently: a memory entry reading *the
payments service uses a house test runner invoked through `make test`* is useful, tenant-specific,
and a leak if it reaches another tenant's run.

**World-model beliefs** (Chapter 25 §12) are shared by `(repo, commit_sha)`, which is what makes the
ninety-second structure probe affordable. That key is tenant-scoped in practice because repositories
are — but only in practice. A shared dependency, a public repository, or a fork produces the same
commit hash across tenants, and the sharing key then crosses the boundary silently.

`[BP]` Two rules, and both are cheap:

- **The tenant is part of the key, always** — in memory lookups and in belief cache keys — even where
  another field appears to imply it. `(tenant, repo, commit)` costs one column and removes the entire
  class.
- **A cross-tenant read is an alert, not a filtered-out row.** If the enforcement is a filter, a
  cross-tenant read looks like an empty result and is indistinguishable from having no data. If it
  raises, it is findable.

The seductive version worth naming: aggregating "learnings" across tenants genuinely improves
quality, and someone will propose it with good measurements behind them. It is a product decision
with contractual consequences and it belongs in front of whoever signs the contracts, not in a
design review.

### 5.3 Redaction at capture, and why read-time redaction fails

Chapter 16 required redaction at capture. Three reasons, of which only the first is usually given:

- **The raw material never exists on disk.** A read-time redactor leaves the original, so every
  future access path is a new exposure — a new query interface, a backup, an export, an engineer
  with database access.
- **A deletion request cannot reach unclassified data.** This is the cold open's mechanism. Data that
  was never marked as sensitive is not in anyone's inventory, so the deletion script's author does
  not know to include it.
- **Read-time redaction has to be correct everywhere, forever.** Capture-time redaction has to be
  correct in one place, once. The second is a far smaller surface, and it is the surface that gets
  reviewed.

`[BP]` The trade is real and should be stated rather than glossed: capture-time redaction
occasionally destroys something a debugging session wanted. That happens a few times a year and is
recoverable by reproduction. The alternative failure happens once and is not recoverable at all.

### 5.4 Retention, and the collision with Chapter 41

Chapter 34 §3.1 argued that the trace retention window is a decision about whether Level 5 is
possible, and that it should be set against evaluation needs rather than storage cost.

This chapter adds the opposing force, and the two do genuinely conflict:

| Pressure | Direction | Source |
|---|---|---|
| Evaluation corpus needs history | Longer | C41 |
| Evolution needs version-partitioned history | Longer | C44 |
| Exposure grows with retention | Shorter | Here |
| Contractual and regulatory limits | Shorter, and fixed | Here |

`[BP]` The resolution that works is to split the store by classification rather than to pick one
window. Redacted, structural material — which tools were called, in what order, with what verdicts,
at what cost — is small, low-risk, and retainable for years, and it is most of what Chapters 41 and
44 actually need. Verbatim content — file bodies, issue text, model output — is large, high-risk,
and retainable for weeks.

That split is worth designing in from the start, because retrofitting it means discovering that the
structural signal and the verbatim content are interleaved in one blob and cannot be separated
without re-deriving the corpus.

### 5.5 What cannot be deleted

The honest section, and the one that has to be read before Chapter 44 is built.

If customer data was used to derive an artefact, deleting the source rows does not remove it from
the derivative. Three cases, in increasing order of how badly they are handled:

- **Aggregate statistics.** A pass rate computed over a corpus that included a customer's runs. Low
  risk, effectively impossible to reverse, and universally accepted as fine — which is worth noting,
  because it establishes that the principle is about degree rather than absolutes.
- **A golden set built from real cases.** Chapter 28 required golden cases to be realistic, and the
  most realistic source is production. A golden case derived from a customer's run contains their
  material, is deliberately immutable (Chapter 28 §5.2 forbids editing it), and is exactly the thing
  a deletion request would demand be removed. **`[BP]` Build golden cases from synthesised or
  consented material, and record the provenance of each one.** This is far cheaper to decide at the
  start than to unpick later.
- **A tuned model.** If Chapter 44's loop ever tunes weights on trajectory data, deletion is not
  available in any meaningful sense. The information is distributed across parameters and there is
  no operation that removes one customer's contribution.

`[BP]` The rule that follows: **derivation from customer data is a decision, made explicitly, with
the deletion consequence stated in the same document.** Not a pipeline someone builds because the
data was there. The trace store is the most useful corpus in the building and it is also somebody
else's material, and those two facts have to be weighed by whoever is entitled to weigh them.

```
                                                            LAYER VIEW

   DELETABLE                          route exists and is tested
   +--------------------------------------------------------------+
   |  runs | plans | effect ledger | dead letters | decisions      |
   |  memory | world-model beliefs                                 |
   |                                                               |
   |  each declares a deletion route in the store registry (4.1)   |
   |  an undeclared store fails enumeration LOUDLY                 |
   +--------------------------------------------------------------+

   DELETABLE, WITH DESIGN                 split by classification
   +--------------------------------------------------------------+
   |  TRACE STORE                                                  |
   |                                                               |
   |    verbatim content    weeks     high risk    deletable       |
   |    structural signal   years     low risk     retained        |
   |                                                               |
   |  the split is what lets C41 and C44 have their history        |
   |  without the exposure growing with it (5.4)                   |
   +--------------------------------------------------------------+

   NOT DELETABLE                      no operation exists
   +==============================================================+
   |  aggregate statistics       accepted, and worth noticing      |
   |  golden cases from real runs   -> synthesise instead (5.5)    |
   |  tuned model weights           -> a decision, not a pipeline  |
   |                                                               |
   |  This boundary is crossed by DERIVING, and it is crossed      |
   |  permanently. There is no request that reverses it.           |
   +==============================================================+

  Figure 37.3 -- Three deletion classes, and the boundary that is
                 one-way (D7 Data Flow)
```

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  A deletion request, executed against a registry.

  t   Request                    Store registry        Result
  --  -------------------------  --------------------  --------------
  0   deletion request for
      tenant t_44
  1   executor enumerates the
      REGISTRY, not a hand-
      written list
  2                              runs           route  deleted 1,204
  3                              plans          route  deleted 3,881
  4                              effect ledger  route  deleted 92
                                 -- but 2 rows are
                                 OUTSTANDING (C27)
                                 -> escalate, do not
                                    silently delete
                                    an unresolved
                                    obligation
  5                              dead letters   route  0 open; deleted
  6                              decisions      route  RETAINED
                                 (C30 sec 7.2: longer
                                  than traces; the
                                  route archives
                                  rather than deletes)
  7                              memory         route  deleted 417
  8                              beliefs        route  deleted 63
                                 keyed (tenant, repo,
                                 commit) -- 5.2
  9                              traces:
                                   verbatim     route  deleted 8,940
                                   structural   route  RETAINED,
                                                       tenant-anonymised
 10                              golden set     NONE   -- 3 cases were
                                                       derived from
                                                       t_44's runs
                                                       -> FLAGGED, not
                                                          deleted (5.5)
 11  certificate issued, naming
      per store: deleted,
      retained, or flagged
 12  the 3 golden cases are
      reviewed by a human and
      replaced with synthesised
      equivalents

  ELAPSED: minutes. Nothing was missed, because the executor
  enumerated a registry rather than somebody's memory of the
  architecture.

  FAILURE BRANCH -- the trace store is not in the registry (the cold
  open):

    t=9   the executor has no entry, so it does nothing
          -- and reports success, because the stores it DID know
             about all returned cleanly
    t=11  certificate issued, honestly, listing eight stores
    +6wk  a support engineer searching for a `search_files` bug
          finds forty files of the customer's source
    -- the certificate was true about everything it named. The
       defect was in the enumeration, and an enumeration built from
       a script author's knowledge is complete only by accident.

  Figure 37.4 -- A deletion request against a registry (D4 Sequence)
```

Two steps carry the design. At t=4 the executor refuses to delete rows carrying unresolved
obligations — because deleting the record of a migration still sitting on staging removes the only
thing that would have told anyone about it, which is Chapter 27's dead letter argument colliding
with a deletion request. At t=10 the golden set has no route, and the correct behaviour is to
*flag* rather than to fail or to skip: a human decides, and the decision is recorded.

---

## 7. State Management

```
                                                            STATE VIEW

   CAPTURED MATERIAL

      {{ ingress }}
          |  tagged (provenance, C31), stamped (tenant),
          |  REDACTED -- all three at capture, one place (3.1)
          v
      {{ classified }}
          |
          +---- verbatim ------> {{ retained_short }}  weeks
          |                            |
          +---- structural ----> {{ retained_long }}   years,
          |                            |               anonymised
          |                            |
          |                            | retention window elapses
          |                            v
          +--------------------> {{ expired }}  (terminal)
                                       ^
          deletion request              |
          {{ classified }} -------------+

      ILLEGAL: {{ ingress }} -> {{ classified }} without redaction.
      A record that reached storage unredacted cannot be repaired by
      redacting it later -- the original was written, and backups,
      replicas, and any reader in between already have it (5.3).

      ILLEGAL: a write to any store not present in the registry.
      Enforced at the persistence layer, failing in development
      (4.1). This is what makes the deletion executor's enumeration
      complete by construction.

   DERIVED ARTEFACT

      {{ not_derived }}
          |  a deliberate decision, with the deletion consequence
          |  stated in the same document (5.5)
          v
      {{ derived }}   (TERMINAL -- there is no transition out)

      This state machine has two states and one transition, and the
      transition is one-way. It is drawn because the one-way-ness is
      the thing people do not believe until they see it as a state
      diagram with no return edge.

  Figure 37.5 -- Capture lifecycle, and the one-way transition (D6
                 State Diagram)
```

### 7.1 Retention is per classification, not per store

The trace store holds two classes of material with retention windows differing by two orders of
magnitude (§5.4). Applying one window to the store means choosing between losing the corpus and
carrying the exposure.

`[BP]` Classification is a column, retention is a policy over classifications, and the store is
partitioned by it. That makes expiry a partition drop rather than a scan-and-delete, which is both
cheaper and — more importantly — verifiable: you can point at a partition and say it is gone.

### 7.2 Authority decisions outlive everything

Chapter 30 §7.2 required decision rows to be retained for as long as the effects they authorised
persist, which is usually longer than any trace. A deletion request therefore has to treat them
differently: the decision that a named person approved a specific action is a record about the
*operator's* accountability as much as about the customer's data.

`[BP]` Archive rather than delete, with the customer-identifying fields reduced to a tenant
reference. The fact that `platform-oncall` approved a deploy-key deletion at 22:41 survives; the
customer's repository name does not need to.

---

## 8. Internal APIs

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

`StoreRegistration` being a declaration each store must satisfy — rather than a config file the
deletion executor reads — is §4.1's argument in the type system. A config file drifts from reality
silently; a declaration that gates writes cannot.

---

## 9. Data Structures

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

`DeletionCertificate` carrying both `stores_enumerated` and `stores_registered` and requiring them
to match is the cold open's defect turned into an assertion. A certificate that names eight stores
when nine are registered is not a certificate; it is a report about eight stores, and the two are
indistinguishable without the second number.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| External material | Tagger + redactor + stamper | The sole ingress path (C31) | Raw bytes, source identity |
| Every store | Store registry | Registration at startup | Tenant field, classification, retention, deletion route |
| Persistence layer | Store registry | Check on every write | Rejection if unregistered |
| Deletion executor | Every store | Enumerated calls | Tenant to delete |
| Deletion executor | Humans | Certificate | Per-store outcome, with counts that must reconcile |
| Retention job | Partitions | Scheduled drop | Expired classification partitions |
| Cross-tenant read attempt | Alerting | Exception, not a filter | The read that should not have been possible (§5.2) |

The last row is a design choice with an operational consequence. `[BP]` A cross-tenant read must
raise rather than return an empty result, because an empty result is indistinguishable from having
no data and produces no signal — which is this handbook's recurring failure shape, appearing one
final time in Level 4.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Trace store absent from the deletion path | Nothing, until someone searches it | Registry enumeration with reconciled counts (§4.1). The cold open |
| Traces classified as telemetry | Retention set by storage cost; no owner | Classify by contents, not by the team that built it |
| Cross-tenant memory read | **Nothing** — a filter returns empty | Tenant in the key; raise rather than filter (§5.2) |
| Belief cache shared across tenants by commit | Nothing | `(tenant, repo, commit)` — one extra column (§5.2) |
| Credential in a tool error message | Redactor pattern miss | Redact all captured material; CI test with a deliberate failure (§5.1) |
| Redaction applied at read | Raw material on disk, in backups, in replicas | Capture-time only; a record written unredacted cannot be repaired (§7) |
| Golden case derived from a customer's run | Deletion request has no route | Synthesise golden cases; record provenance (§5.5) |
| Model tuned on trajectory data | No detector, no remedy | Decide before deriving; the transition is one-way (§7) |
| Obligation-carrying ledger row deleted | The obligation becomes invisible | Refuse and escalate (§6, t=4) |
| New store added without registration | Impossible by construction | Persistence-layer enforcement, failing in development (§4.1) |

Rows three and four are the pair that single-tenant testing cannot produce, and they are worth a
deliberate exercise: `[BP]` run two tenants against the same repository at the same commit in
staging, and assert that neither sees the other's beliefs or memories. It takes an afternoon and it
is the only test that covers the leak with no error.

---

## 12. Scalability

**Redaction is on the capture path and must be fast.** Pattern matching over captured material, in
process, before the write. `[BP]` Compile the pattern set once; a redactor that recompiles per
observation becomes measurable at high step rates and is then proposed for removal.

**Tenant keys add a column and an index everywhere**, which is negligible, and make every query
narrower, which usually improves it.

**Retention by partition drop, not by delete.** Time-partitioned by classification, expiry is a
metadata operation. `[BP]` A scan-and-delete over a multi-terabyte trace store during business hours
is its own incident, and it also cannot be verified — a dropped partition can be pointed at.

**Deletion is bounded by store count, not by data volume**, when routes are per-tenant partitions or
indexed deletes. `[BP]` Index every store on the tenant field; without it a deletion request becomes
a full scan of the largest table in the system.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Registered stores versus enumerated stores.** Must be equal. The cold open is the gap.
- **Writes rejected for missing registration.** Should be nonzero in development and zero in
  production. A nonzero production count means a store shipped without a declaration.
- **Cross-tenant read attempts.** Expected zero, alerted on any. Not filtered — raised.
- **Redaction hit rate by pattern.** A pattern that never fires is either unnecessary or broken, and
  Chapter 34 §5.3's synthetic probe applies here directly.
- **Verbatim partition age, oldest.** The exposure clock. If it exceeds the policy window, expiry is
  not running.

### 13.2 The review question

For every store in the system: **whose data is in here, how would we delete one customer's, and has
anyone run that?**

Three parts, and the third is where it usually falls down. A deletion route that has never been
executed is a function that has never been called, and the cold open's route did not exist at all —
which nobody knew, because nobody had asked the question about that particular store.

### 13.3 Teaching this to a new engineer

Ask them to list every place a customer's data ends up. Most people get four or five: runs, plans,
maybe traces, maybe the database backups.

Then walk the nine of §2.3 with them. Memory and world-model beliefs are the ones that produce the
reaction worth waiting for, because both were designed to be cross-run *on purpose*, and the moment
someone sees that the feature and the leak are the same mechanism is the moment this chapter becomes
memorable rather than procedural.

---

## 14. Relation to AHE

`[AHE]` The source's trials run against benchmark tasks, which are public and carry no tenancy.
Nothing in it addresses data governance, and correctly so — there is no customer data in a benchmark
run.

`[INF]` That changes completely when an evolution loop learns from *production* trajectories, which
is the obvious and valuable next step and is what Chapter 44 contemplates. At that point the loop's
corpus is customer material, and §5.5's one-way boundary is crossed by the act of training. `[BP]`
The decision has to be made before the pipeline is built, with the deletion consequence written down
in the same document, and it belongs to whoever signs the customer contracts.

`[INF]` There is a narrower and safer version worth designing for from the start: **learn from the
structural signal, not the verbatim content.** Which tools were called, in what order, with what
verdicts, at what cost, against what task type — that is most of what an evolution loop needs, it is
the low-risk half of §5.4's split, and it can be retained for years without carrying customer
material. Chapter 44's corpus should be the structural partition by default and the verbatim
partition only with explicit consent.

`[INF]` Chapter 20 §5.5's containment list gains its eighth entry here, and this one arrives from a
direction none of the previous seven did. An evolution loop that can widen memory sharing across
tenants would raise quality — genuinely, measurably — by making memories more specific and more
widely available. It would also be a contractual breach that no benchmark measures. Memory scope
joins the gate policy, the effect tags, the verifier, the golden set, the retention policy, the
temporal parameters, and the concurrency limits outside the evolvable workspace.

---

## 15. Industry Perspective

**`[BP]` Data-subject deletion is a solved problem in mature systems and consistently missed in
observability stores.** The pattern — a registry of stores each declaring a deletion route, with
reconciled counts on a certificate — is standard in regulated industries. It is rarely applied to
telemetry, because telemetry is not usually a verbatim archive of the customer's material.

**`[BP]` Capture-time redaction is well established in payment and health systems** and the
arguments transfer unchanged. The one worth repeating is §5.3's third: capture-time redaction has to
be right in one place, and read-time redaction has to be right everywhere, forever.

**`[INF]` Trace stores in agent systems are systematically misclassified.** The store is built by an
observability team, named after telemetry, retained against a storage budget, and searchable by the
whole engineering organisation. Every one of those is the correct default for latency histograms and
the wrong default for a verbatim copy of a customer's repository.

**`[BP]` Tenant-in-the-key rather than tenant-as-a-filter is old wisdom from multi-tenant
databases.** Row-level security, tenant-scoped connections, and composite keys all encode it. The
agent-specific twist is that two of the stores are cross-run by design, so the boundary has to be
argued for against a feature rather than merely implemented.

**`[FUT]` Machine unlearning is an active research area and is not currently a deployable answer.**
Techniques for removing a training example's influence from a model exist in the literature and none
is reliable enough to satisfy a deletion request. Until that changes, §5.5's boundary is one-way in
practice as well as in principle, and designs should assume it stays that way.

---

## 16. Key Takeaways

1. **The trace store is the highest-risk dataset in the architecture**, and it is misclassified
   almost everywhere — built by the observability team, named after telemetry, retained against a
   storage budget, searchable by everyone.
2. **Tenancy is a property of nine stores, not a column on one.** Two of them — memory and
   world-model beliefs — are cross-run by design, which is the feature and the leak at once.
3. **A cross-tenant read must raise, not filter.** A filter returns an empty result, which is
   indistinguishable from having no data and produces no signal.
4. **Redact at capture, irreversibly.** Read-time redaction leaves the original, has to be correct
   everywhere forever, and cannot be reached by a deletion request for data nobody classified.
5. **Deletion is a registry enumeration, not a script.** Every store declares its route; an
   unregistered store is unwritable; and the certificate reconciles stores enumerated against stores
   registered.
6. **Split the trace store by classification.** Structural signal is small, low-risk, and retainable
   for years — and is most of what Chapters 41 and 44 need. Verbatim content is large, high-risk, and
   retainable for weeks.
7. **Derivation is one-way.** Golden cases from real runs, statistics, and tuned weights cannot be
   un-derived. Decide before building the pipeline, and put the deletion consequence in the same
   document.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Store registry** | A declaration by every store of its tenant field, classification, retention, and deletion route, enforced by making unregistered stores unwritable. | `[BP]` | Ch 41, Ch 48 |
| **Tenant-in-the-key** | Requiring the tenant to write rather than filtering on read, so a missing key fails in development instead of returning someone else's data. | `[BP]` | Ch 44 |
| **Cross-run store** | Memory and world-model beliefs, which carry information between runs by design and are therefore where a tenant leak produces no error. | `[INF]` | Ch 44 |
| **Capture-time redaction** | Irreversible removal of secrets before the write, correct in one place rather than everywhere forever. | `[DAR]` | Ch 40 |
| **Classification split** | Partitioning captured material into verbatim and structural so retention can be weeks for one and years for the other. | `[INF]` | Ch 41, Ch 44 |
| **Structural signal** | Tool names, ordering, verdicts, and cost — the low-risk half of a trajectory, and most of what evaluation and evolution actually need. | `[INF]` | Ch 41, Ch 44 |
| **Deletion certificate** | A per-store record of what was deleted, retained, or flagged, whose enumerated count must reconcile against the registry. | `[BP]` | Ch 48 |
| **Deletion refusal** | Declining to delete a row carrying an unresolved obligation, because that row is the only record of something still outstanding. | `[INF]` | Ch 48 |
| **One-way derivation** | Building a golden case, statistic, or tuned model from customer data, after which no deletion operation reaches the derivative. | `[FUT]` | Ch 44, Ch 48 |
| **Memory scope** | The tenant boundary on cross-run memory, whose widening would genuinely improve quality and would be a contractual breach no benchmark measures. | `[INF]` | Ch 46 |

---

**Next:** Chapter 38 — *Deployment, Versioning, and Configuration.* This chapter governed the data a
running system accumulates. The next one governs the system itself: versioning a harness separately
from the model and the code, and the observation that a model upgrade is not a dependency bump but
an invalidation event for every measurement, every timeout, and every tuned parameter the harness
carries.
