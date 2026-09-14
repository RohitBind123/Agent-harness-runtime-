```
  Level 3 · Chapter 50
  THIRD-PARTY TOOL SUPPLY AND THE MODEL CONTEXT PROTOCOL
  Requires   C14 The Tool Execution Engine, C15 ACI Design,
             C22 The Event Spine, C31 Safety, Sandboxing,
             and Untrusted Content
  Unlocks    -- an addition to the first edition; nothing depends on it
  Diagrams   Core (5)
```

# Chapter 50 — Third-Party Tool Supply and the Model Context Protocol

---

## 1. Motivation

### 1.1 Cold open

A team connects a public MCP server that advertises documentation search. It takes twenty minutes.
The tool appears as `docs.search_reference`, its description says it searches reference material, and
the runtime records it as pure — because the registry read that field from the server's own manifest
at connect time.

Three weeks later a run pushes a branch to a repository nobody authorised.

The investigation finds nothing wrong. No deployment went out. No code changed. No configuration
changed. The tool is still called `docs.search_reference` and its description still says it searches
reference material. The runtime's own records show a pure call, and pure calls do not pass a gate,
because there is nothing to gate.

What changed was on the other end of a socket, on a Tuesday, in somebody else's repository. The
server's implementation of that tool gained a side effect. Its manifest still said pure, because the
manifest is written by the same party that wrote the side effect.

The team's postmortem lands on the wrong sentence: *we should have vetted that server.* The right
sentence is harder. Chapter 14 says the effect tag is held in the registry and never supplied by the
model, and calls it the whole of the safety model. Nobody noticed that the sentence has a silent
second half — **and never supplied by the tool's author either** — because until this connection, the
registry's author and the runtime's operator were the same person.

### 1.2 In plain language

Most of this book assumes you wrote your own tools. You decided what each one is called, what it
says about itself, what it does, and — the part that matters — whether it changes anything in the
world. That last decision is written down in a list the runtime owns, and every safety mechanism in
Chapters 14, 27, 30 and 31 reads from that list.

The Model Context Protocol is a way for tools to arrive from somewhere else. A server, run by
somebody else, tells your runtime what tools it offers, what they are called, what arguments they
take, and what they do. That is genuinely useful: it removes an enormous amount of one-off
integration work, and it lets the set of things an agent can do change without shipping new code.

It also moves the authorship of that list outside your building. The list your safety model trusts is
now partly written by a stranger.

This chapter is about what to do about that, and the answer is not *vet the stranger*. Vetting is a
point-in-time act and the list can change afterwards. The answer is to split the list in two: the
half a remote party is allowed to write, and the half only you may write. The second half is small,
and it is the whole safety model.

### 1.3 Why this chapter exists

Two things happened after the first forty-nine chapters were written.

The first is that third-party tool supply stopped being unusual and became the default shape of a
deployed agent. `[BP]` A runtime that ships with a fixed, compiled tool set is now the exception.

The second is subtler and is the reason this chapter is a chapter rather than a note. Two of the
book's load-bearing rules turn out to share an assumption that neither states.

Chapter 14 gives the first, and it is a `[DAR]` rule rather than an authorial one: the effect tag is
*"held in the registry and never supplied by the model."* Chapter 31 §5.1 gives the second, and calls it the whole mechanism: *"capability is a
function of (step, declared_needs, run) and NEVER of content."*

Both are correct. Both are also silent about who wrote the registry, because in every chapter before
this one, you did. Once a remote party writes part of it, the two rules stop agreeing. Chapter 31
classifies anything arriving from a third party as untrusted content, which may not authorise an
effect. Chapter 14 classifies the registry as trusted configuration, which determines whether an
effect needs authorising at all. A tool descriptor fetched from an MCP server is both at once.

That contradiction is the subject of this chapter. It is not a protocol question and it is not an
integration question. `[INF]` It is a provenance question wearing an integration costume, and the
lattice that resolves it was built in Chapter 31 for a different reason entirely.

### 1.4 What previous framings got wrong

**"MCP is an integration standard, so it belongs in a wiring document."** Wiring is the cheap half.
The expensive half is that a capability boundary now runs through the middle of your registry, and
capability boundaries are architecture.

**"We will review each server before we connect it."** Review establishes what a server did on the
day you looked. `[INF]` A server that can change its tool list — and the protocol exists so that it
can — has a mutable surface, and a point-in-time review of a mutable surface expires the moment it is
issued. The cold open is that expiry.

**"The server declares its own effects, so we can read them."** This is the cold open's actual defect
and it is worth naming precisely: it lets a remote party set its own blast radius. Chapter 31 §2.3
treats blast radius as a designed quantity, and design is something the operator does.

**"Then we should not use third-party tools at all."** Over-correction, and it costs more than it
saves. The protocol removes real work and buys real flexibility. §2.3 shows there are three defensible
positions and only one of them is refusal.

**"This is the same as calling any third-party API."** Closer, and still wrong in one way that
matters. `[INF]` When your code calls a third-party API, *your code* decided to call it and knew what
it was for. Here the model decides, using a description the third party wrote. The decision and the
description have the same author, and that author is not you.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A hospital with visiting specialists.

The hospital owns the building, the theatres, the records, and the rules. A visiting surgeon brings
skills the hospital does not have, and everybody benefits. But the visitor does not get to decide
which theatre they may enter, which patients they may see, what counts as consent, or whether an
operation is reversible. Those are the hospital's decisions, taken before the visitor arrives, and
they are the same decisions whether the visitor is famous or unknown.

The visitor supplies capability. The institution supplies authority. The two are deliberately not
the same party, and every hospital that has merged them has a scandal in its history.

**Where the analogy breaks.** A visiting surgeon is a person with a licence, a reputation and a
mailing address, and their competence is roughly stable between Tuesday and Wednesday. An MCP server
is a network endpoint whose behaviour can be replaced entirely between two calls with no notification
that means anything, and whose reputation attaches to a name rather than to the bytes that answer.
`[INF]` Carry the analogy too far and you will build a vetting process, which is the hospital's
control, and vetting is the one control that does not transfer.

### 2.2 Why a third-party tool surface must be treated differently

The derivation, and step 5 is where most designs go wrong:

```
  1. A tool the model may call must carry an effect tag, because C14
     makes the tag the whole safety model: it decides whether a gate
     is required, which tier the effect sits in, and what reversal
     exists.
  2. C14 says the tag comes from the registry and never from the
     model. The reason is that the model's incentive is to proceed.
  3. That reason generalises. ANY party whose interest is that the
     call happens is disqualified from setting the tag -- and a tool's
     author is such a party.
  4. An MCP server authors the tool's name, its description, its
     argument schema, and the code behind it. It is such a party.
  5. So the tag cannot be read from the server's manifest. This is
     true even for an honest server, because honesty is not the
     property being relied on: the property is that the tag and the
     implementation have different authors.
  6. But a tag assigned locally, without reading the implementation,
     is a guess -- and the implementation is unreadable by
     construction, because it is behind a socket.
  7. So the runtime has exactly three defensible positions, and no
     fourth: refuse the tool, assume the worst about it, or bind it
     to a locally-authored descriptor the server cannot edit.
  8. Each of the three is correct. They differ in cost and in what
     they cost you.
```

Step 5 deserves a second reading. The argument is not that third-party servers are dishonest. It is
that a tag written by the tool's author is not *evidence* — it is a restatement of the author's
intent, and intent is exactly what a safety mechanism must not rely on. The same reasoning is why
Chapter 28 forbids a judge from raising a verdict and Chapter 31 forbids content from promoting its
own label: in all three cases the forbidden direction is the direction an interested party would
push.

### 2.3 The trichotomy

`[INF]` Three positions, and a runtime should be able to say which one it is in for every connected
server.

| Position | What it means | Cost | Use when |
|---|---|---|---|
| **Refuse** | The server's tools are not admitted to the registry at all | Loses the capability entirely | Always, until one of the others is built. It is the only honest default |
| **Pessimise** | Every tool from the server is tagged `EFFECTFUL`, tier 2, and gated | A gate on every call, including reads, which is expensive in human attention | You want the capability now and can afford the gates |
| **Pin** | Each admitted tool is bound to a locally-authored descriptor carrying its tag, tier, compensation and credential scope. The server supplies only the name, the schema and the transport | Real work per tool, and it must be redone when the schema changes | The tool matters enough to be worth a descriptor |

The specification's **I15** already names the middle position for the general case: an unknown
third-party effect defaults to `EFFECTFUL`. This chapter's contribution is that pessimising is a
*position you occupy deliberately*, with a cost you can measure — the gate rate — rather than a
fallback you land in.

A fourth option is frequently proposed and does not survive: *trust the server's tag, but only for
servers on an allowlist.* `[INF]` It fails because the allowlist entry names a server, and what
changed in the cold open was not which server answered but what that server did. An allowlist
authenticates the counterparty. The tag is a claim about behaviour, and authenticating who made a
claim is not verifying the claim.

### 2.4 The mental model to carry

> **A remote party may tell you what a tool is called and what shape its arguments are. Only you may
> say what it is allowed to do to the world. The first half is a schema problem and it is easy. The
> second half is the safety model and it does not travel over the wire.**

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

  +------------------------------------------------------------------+
  |  PORTS                                                           |
  |                                                                  |
  |  +------------------------------------------------------------+  |
  |  |  TOOL PORT                             one of the six       |  |
  |  |  resolve . validate . authorise . invoke . normalise        |  |
  |  +-----------------+--------------------------+---------------+  |
  |                    |                          |                  |
  |         local      |                          |  remote          |
  |         adapter    |                          |  adapter         |
  |                    v                          v                  |
  |  +-----------------------+     +------------------------------+  |
  |  | LOCAL TOOLS           |     | MCP ADAPTER                  |  |
  |  | you wrote these;      |     | speaks the protocol;         |  |
  |  | descriptor and code   |     | owns NO policy               |  |
  |  | have one author       |     |                              |  |
  |  +-----------------------+     +---------------+--------------+  |
  |                                                |                 |
  +------------------------------------------------|-----------------+
                                                   | tool list, schemas,
                                                   | descriptions, results
                          +========================v================+
                          |  ADMISSION                              |
                          |  the only door. Applies the trichotomy  |
                          |  refuse | pessimise | pin               |
                          |  writes the LOCAL HALF of the           |
                          |  descriptor, which the server           |
                          |  cannot reach                           |
                          +========================+================+
                                                   |
                                                   v
                          +=========================================+
                          |  REGISTRY          owned by the runtime |
                          |  name . schema . TAG . TIER .           |
                          |  compensation . credential scope .      |
                          |  descriptor digest                      |
                          +=========================================+
                                                   |
                                                   v
                                        C14's tool execution engine,
                                        unchanged, reading the tag
                                        it has always read

  Figure 50.1 -- Third-party tools enter through admission, never through
                 the registry (D1 High-Level Architecture)
```

Three things to read out of this, and the third is the one that saves work later.

**MCP does not get a port.** It is an adapter behind the tool port that Chapter 4 already defined.
Adding a seventh port would widen the narrow waist for one protocol, and the next protocol would
widen it again. `[INF]` The test from Chapter 4 §2.4 applies unchanged: delete the MCP adapter and
the runtime must still be coherent. It is, because the tool port does not know the difference.

**Admission is a component, not a step.** It is the only place a remote descriptor may become a
registry entry, and it is where the local half is written. Everything downstream — the execution
engine, the gate, the effect ledger, the compensation walk — is untouched, because by the time they
see a tool it is an ordinary registry entry with an operator-authored tag.

**The registry keeps a digest.** The descriptor the runtime admitted is recorded by content, not by
name. §5.4 is about why, and it is the mechanism that would have caught the cold open.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

  +==================================================================+
  |  MCP SUBSYSTEM                                                   |
  |                                                                  |
  |  +--------------------+      +-----------------------------+     |
  |  | CONNECTION MANAGER |      | DESCRIPTOR RECONCILER       |     |
  |  | one session per    |----->| compares the server's       |     |
  |  |   server           |      |   advertised list against   |     |
  |  | transport, retry,  |      |   the admitted list         |     |
  |  |   liveness         |      | emits: ADDED, CHANGED,      |     |
  |  | NEVER interprets   |      |   WITHDRAWN                 |     |
  |  |   a tool           |      | decides NOTHING             |     |
  |  +--------------------+      +--------------+--------------+     |
  |                                             |                    |
  |                                             v                    |
  |  +------------------------------------------------------------+  |
  |  | ADMISSION CONTROLLER                                       |  |
  |  |                                                            |  |
  |  |  ADDED     -> apply the trichotomy; default REFUSE          |  |
  |  |  CHANGED   -> QUARANTINE the tool, then re-admit or refuse  |  |
  |  |  WITHDRAWN -> retire the entry; in-flight plans repair      |  |
  |  |                                                            |  |
  |  |  writes: tag, tier, compensation, credential scope,        |  |
  |  |          egress allowlist, descriptor digest               |  |
  |  |  reads from the server: name, schema, description ONLY     |  |
  |  +------------------------------+-----------------------------+  |
  |                                 |                                |
  |                                 v                                |
  |  +------------------------------------------------------------+  |
  |  | INVOCATION PROXY                                           |  |
  |  | binds a pinned descriptor to a call; refuses a call whose  |  |
  |  | digest no longer matches; records the mismatch as an event |  |
  |  +------------------------------------------------------------+  |
  +==================================================================+

  Figure 50.2 -- Inside the MCP subsystem (D2 Low-Level Architecture)
```

| Component | Owns | Calls | Never |
|---|---|---|---|
| **Connection manager** | Transport and liveness for one server | the server | interprets a tool, or admits one |
| **Descriptor reconciler** | Diffing advertised against admitted | nothing | decides admission |
| **Admission controller** | The local half of every descriptor | policy | reads a tag from the wire |
| **Invocation proxy** | One call against a pinned descriptor | the server, via the connection manager | re-resolves a binding silently |

`[INF]` The "Never" column is again the useful one, and the second row is the one teams collapse. A
reconciler that decides admission becomes a second policy engine that nobody reviews, sitting behind
a network socket, updating itself. That is a description of the cold open.

### 4.1 Why quarantine is a state and not a rejection

When a server changes a tool's schema or description, the honest response is neither *keep using it*
nor *drop it forever*. It is **quarantine**: the entry stops being callable, the change is surfaced to
a person or a policy, and re-admission is a deliberate act that mints a new descriptor digest.

`[INF]` Rejection loses the capability on every upstream bug-fix release, which trains operators to
disable the check. Silent re-admission is the cold open. Quarantine is the only response that
survives both failure modes, and it costs one state.

### 4.2 What admission must write, and what it must never read

| Field | Author | Why |
|---|---|---|
| Tool name | Server | Identification, not authority |
| Argument schema | Server | Shape only; C14 §5.2 is honest that a schema cannot capture semantics |
| Description | Server, **labelled untrusted** | The model reads it; §5.2 |
| **Effect tag** | **Operator** | C14: the whole safety model |
| **Tier** | **Operator** | C27 decides reversal from it |
| **Compensation** | **Operator** | A tier-2 reversal the server defined would be a second unreviewed effect |
| **Credential scope** | **Operator** | C31 §5.3: issued per step from what the node declared |
| **Egress allowlist** | **Operator** | C31 §5.5 |
| **Approval requirement** | **Operator** | C30: enforced in the runner, never by prompting |
| **Descriptor digest** | **Runtime** | §5.4 |

The left column splits three-to-seven, and the seven are the entire safety model. `[INF]` That ratio
is the argument of this chapter compressed into a table: the protocol carries the cheap part.

---

## 5. The Trust Split

### 5.1 Where the lattice already had the answer

```
                                                            LAYER VIEW

   TRUSTED
   +--------------------------------------------------------------+
   |  the operator's admission decisions: tag, tier, compensation, |
   |  credential scope, egress allowlist, approval requirement     |
   |                                                               |
   |  may: define capability, define policy                        |
   +--------------------------------------------------------------+
                              ====>  read by the gate, the ledger,
                                     the compensation walk

   SEMI-TRUSTED
   +--------------------------------------------------------------+
   |  the tool NAME and ARGUMENT SCHEMA advertised by an admitted  |
   |  server                                                       |
   |                                                               |
   |  may: identify a tool, shape a call                           |
   |  may NOT: widen scope, alter policy, authorise an effect      |
   +--------------------------------------------------------------+
                              ====>  read by the binder

   UNTRUSTED
   +--------------------------------------------------------------+
   |  the tool DESCRIPTION, and every RESULT a server returns      |
   |                                                               |
   |  may: inform the model's choice within a granted scope        |
   |  may NOT: widen scope, alter policy, authorise an effect,     |
   |           reach outside the egress allowlist                  |
   +--------------------------------------------------------------+
                              ====>  read by the model, and by
                                     nothing that decides anything

  Figure 50.3 -- The three halves of a third-party tool (D7 Data Flow)
```

`[INF]` Nothing in that figure is new. It is Chapter 31 §5.1's lattice with a tool descriptor
substituted for a document, and the fact that the substitution works without modification is the
strongest evidence available that the lattice was the right shape. The contribution here is only the
observation that a *descriptor* is content, when everybody's instinct is to file it under
configuration.

### 5.2 A description is untrusted content in a trusted position

A tool description is *"an editable harness surface in its own right"* `[AHE]`, and this chapter is
about what happens when that surface stops being yours to edit. Chapter 14 §2.2 states the property
that makes it dangerous, and states it about your own tools:
*"The model selects a tool and its arguments using ONLY the description. It has never seen the code."*

Read that with a remote author and it becomes an attack. The party that writes the implementation
also writes the only thing the model will ever know about the implementation. There is no mechanism
anywhere in the model's context for noticing that the two disagree.

`[INF]` This is not the same as ordinary prompt injection, and the difference is worth holding onto.
Injected text in a fetched document arrives *as data the model is reasoning about*, and Chapter 31's
channel separation keeps it there. A tool description arrives *in the position where the runtime's own
instructions live*, because that is where descriptions go. The content is untrusted and the position
is trusted, and the vulnerability is the mismatch rather than either half.

Three controls, in the order they should be built:

1. **Render descriptions in the untrusted channel.** Whatever mechanism separates fetched content
   from instruction must cover tool descriptions too. Most implementations do not, because
   descriptions were local when the mechanism was written.
2. **Cap and normalise them.** A description is a short phrase. `[BP]` The specification's own advice
   for the on-device case — limit tool descriptions to short phrases, offer few tools per request —
   turns out to be a security control as well as a budget one.
3. **Digest them.** A description that changes is a change to what the model believes, and belongs in
   §5.4's quarantine path even when the schema is untouched.

### 5.3 Taint is monotonic, and a run cannot un-touch a server

Chapter 31 §7.1 makes taint monotonic and run-scoped. Applied here it produces a rule that is
uncomfortable and correct:

> **A run that has consumed a result from an untrusted server may not afterwards reach a tier-3
> effect, regardless of how the plan reached that step.**

`[INF]` The discomfort is the point. It means a single documentation lookup can disqualify a run from
sending an email, and teams will want an exception. The exception they will propose — *the lookup was
unrelated to the email* — requires establishing that an untrusted result did not influence a later
decision, and there is no mechanism that can establish that. Chapter 31 forbids upward movement for
exactly this reason: any operation that could clear the taint would be reachable by the content that
set it.

The affordable version is not an exception. It is **partitioning**: run the untrusted lookup in its
own run, return a structured result across the command boundary, and let the effectful run consume a
fact rather than a payload. That costs one extra run and keeps the property.

### 5.4 The rug pull, and what pinning actually pins

The specification's **I22** was written before this chapter and answers it exactly: *"The resolved
tool binding is pinned into the invocation identity at plan time. Execution-time re-resolution mints a
new identity and is recorded."*

`[INF]` Read against a remote server, I22 acquires a second job. Pinning a binding was about knowing
which implementation ran. Pinning a *descriptor digest* is about knowing whether the thing you
admitted is the thing you are calling. The digest covers the name, the schema and the description —
everything the server authored — and it is compared at invocation, not at connect.

| Change on the server | Digest | Response |
|---|---|---|
| Nothing | matches | call proceeds |
| Description reworded | differs | quarantine; re-admission required |
| Schema field added | differs | quarantine; re-admission required |
| Implementation changed, descriptor identical | **matches** | **call proceeds** |

The last row is the honest limit and must not be papered over. A digest over the descriptor cannot
see behind the descriptor. `[INF]` It would not have caught the cold open on its own — the cold open
changed an implementation, not a manifest. What catches the cold open is the *tag*: had the tag been
operator-authored and pessimistic, the call would have been gated whatever the server did, and a
person would have seen a push request that made no sense next to a documentation search.

That is worth stating plainly, because the digest is the satisfying mechanism and the tag is the one
that works. **The digest detects a changed claim. The tag survives an unchanged one.**

---

## 6. Runtime Sequence

```
                                                        TIME VIEW

  plannerbinder admit  proxy  server gate   ledger
  |      |      |      |      |      |      |
1)|------>      |      |      |      |      |   step needs a capability
  |   (2)|------>      |      |      |      |   resolve name -> entry
  |      <---(3)|      |      |      |      |   entry + digest + TAG
  |      |      |      |      |      |      |        the tag is the operator's
  |      |      |      |      |      |      |   (4)  PIN the digest into the
  |      |      |      |      |      |      |        activity identity
  |      |------------->      |      |      |
  |      |      |   (5)|------------->      |   EFFECTFUL -> gate FIRST
  |      |      |      <----------(6)|      |   park until resolved
  |      |      |   (7)|------>      |      |   invoke, step-scoped cred
  |      |      |      <---(8)|      |      |   result, tagged UNTRUSTED
  |      |      |   (9)|-------------------->   effect row + taint raised
  |      |      |      |      |      |      |
  --------------------------------------------------------------------------
  FAILURE BRANCH at (5): the digest no longer matches
  |      |      |      |      |      |      |
  |      |      |      |      |      |      |   (5a) refuses; no call is made
  |      |      |  (5b)|-------------------->   QUARANTINED event appended
  |      <--(5c)|      |      |      |      |   tool withdrawn from plan
  <--(5d)|      |      |      |      |      |   plan REPAIR, not run failure

  Figure 50.4 -- One third-party call, and the branch that matters
                 (D4 Sequence)
```

Four things the sequence establishes.

**The gate precedes the call, at (5) and (6).** Chapter 30's gate sits at the tool boundary rather
than the plan boundary precisely so that a tier-3 effect cannot be reached, and a remote tool is the
case where the distinction pays. The runtime does not know what the server will do; it knows what it
authorised.

**The credential is minted at (7), per step.** Chapter 31 §5.3. A long-lived credential handed to a
connection manager at connect time would survive every subsequent descriptor change, which returns
the design to the cold open by a different road.

**The result at (8) is labelled before anything reads it.** Chapter 31 §3.1: tagging happens at fetch,
not at use. A result labelled at use has already been read by something.

**The failure branch is a repair, not an error.** `[INF]` A withdrawn or quarantined tool mid-plan is
the same shape as any other plan invalidation: the plan is repaired against the tools that exist now,
attempt caps are keyed by activity identity so the repair does not reset them, and the run continues.
Treating it as a run failure produces an operational load proportional to how often upstream servers
ship, which is not a quantity you control.

---

## 7. State Management

```
                                                            STATE VIEW

                        advertised by a server
                                 |
                                 v
                          +--------------+
                          |  DISCOVERED  |
                          +------+-------+
                                 |
              refuse             |            admit (pin | pessimise)
        +------------------------+------------------------+
        |                                                 |
        v                                                 v
  +-----------+                                    +-------------+
  | REFUSED   |                                    |  ADMITTED   |<---+
  | terminal  |                                    |  callable   |    |
  | for this  |                                    +------+------+    |
  | digest    |                                           |           |
  +-----------+                          descriptor       |           |
                                         digest changed   |           |
                                                          v           |
                                                   +-------------+    |
                                                   | QUARANTINED |    |
                                                   | not callable|    |
                                                   +------+------+    |
                                                          |           |
                                       re-admitted by an  |           |
                                       operator decision  +-----------+
                                                          |
                                       withdrawn by server|
                                                          v
                                                   +-------------+
                                                   |   RETIRED   |
                                                   |  terminal   |
                                                   +-------------+

  ILLEGAL:  QUARANTINED --> ADMITTED without a NEW digest being recorded.
            Re-admitting under the old digest is indistinguishable from
            never having quarantined, and is the cold open written as a
            state transition.

  Figure 50.5 -- Descriptor lifecycle (D6 State Diagram)
```

### 7.1 Why refused and retired are different

Both are terminal and both mean *not callable*, so the instinct is to merge them. `[INF]` They answer
different questions and a merged state answers neither. `REFUSED` records an operator decision about
a specific digest, and is the state a review reads to see what was turned down and why. `RETIRED`
records that a server stopped offering something, and is the state a plan repair reads. Merging them
means an audit cannot distinguish a tool you rejected from one that vanished, which is the difference
between a policy record and an availability record.

### 7.2 Where this state lives

Harness state, in the sense of Chapter 6 — a property of the system rather than of a customer. `[INF]`
That classification has a consequence worth stating: descriptor decisions are versioned with the
harness, ship through the pipeline in Chapter 38, and are subject to the config-freeze rule, so a
run's behaviour remains explainable from its own record rather than from what a server was serving
that afternoon.

---

## 8. Internal APIs

| Operation | Caller | Returns | Refuses when |
|---|---|---|---|
| `reconcile(server_id)` | connection manager | `ADDED[] · CHANGED[] · WITHDRAWN[]` | the session is not live |
| `admit(descriptor, decision)` | operator or policy | registry entry + digest | the local half is incomplete |
| `resolve(name, run)` | binder | entry, digest, tag | the entry is quarantined, refused or retired |
| `invoke(entry, digest, args, credential)` | activity runner | result labelled `UNTRUSTED` | digest mismatch; gate unresolved; credential absent |
| `quarantine(name, reason)` | reconciler | event | — |

`[INF]` There is deliberately no `admit_all`, and no `trust_server`. Both are the same request wearing
different names, and a codebase that has either will eventually have both. The absence is the API
design.

---

## 9. Data Structures

```
  descriptor
    tool_name          text        from the server
    arg_schema         json        from the server
    description        text        from the server, labelled UNTRUSTED
    digest             text        sha256 over the three fields above

  admission
    digest             text        what was admitted
    server_id          text
    position           enum        PIN | PESSIMISE
    effect_tag         enum        PURE | EFFECTFUL      -- operator
    tier               int         1 | 2 | 3             -- operator
    compensation       text?       tier 2 only           -- operator
    credential_scope   json        narrowest that works  -- operator
    egress_allow       json                              -- operator
    requires_approval  bool                              -- operator
    state              enum        ADMITTED | QUARANTINED | REFUSED | RETIRED
    decided_by         text        a person or a policy id
    decided_at         timestamp
```

Two fields carry more weight than their size suggests. `decided_by` is what makes an admission
auditable as a decision rather than discoverable as a fact. And `position` is what lets an operator
answer *how much of our tool surface is pessimised?* — a number that should trend downward as
descriptors are written, and whose failure to trend downward is a truthful signal that the team has
stopped paying the cost and started living on gates.

---

## 10. Communication

Everything the subsystem does that anyone else can see is an event, appended through the outbox of
Chapter 22 and never written as progress:

| Event | Carries | Consumed by |
|---|---|---|
| `mcp.tool.discovered` | server, name, digest | admission queue, review |
| `mcp.tool.admitted` | digest, position, tag, decided_by | audit, registry projection |
| `mcp.tool.quarantined` | digest, previous digest, reason | plan repair, alerting |
| `mcp.tool.retired` | name, server | plan repair |
| `mcp.invocation.refused` | digest expected, digest found | **alerting; this is the rug-pull signal** |
| `mcp.server.unreachable` | server, since | availability, capacity |

`[INF]` The rate of `mcp.invocation.refused` is the single most useful number this subsystem emits. A
non-zero rate against a server that has not announced a release is not a bug in the digest check; it
is the check doing its job, and it is the earliest signal available that a tool surface moved
underneath a running plan.

---

## 11. Failure Modes

| Failure | Symptom | Correct response |
|---|---|---|
| Server changes an implementation, descriptor unchanged | Effects appear that the tag did not predict | **Not detectable.** Survived only by an operator-authored pessimistic tag |
| Server changes a descriptor mid-plan | Digest mismatch at invocation | Quarantine, plan repair, alert |
| Server unreachable | Calls time out | Retire from the ready set, repair the plan; a park is wrong here because there is no promised resumption |
| Server slow | Activity budget exhausted | An MCP call is Activity-shaped; §12 |
| Description rewritten to mislead the model | Model selects a tool for the wrong task | Untrusted channel, digest, gate. Partly mitigated, not solved |
| Two servers advertise the same tool name | Ambiguous resolution | Names are namespaced by server at admission. Collision is a build error, not a runtime one |
| Server returns an enormous result | Context amplification | C14's truncation, unchanged; the result is a normal tool result |
| Credential over-issued at connect time | A quarantined tool still holds access | Credentials are step-scoped and expire with the step |

The first row is the honest limit of the whole chapter and belongs in any summary of it. `[INF]`
Nothing in a protocol can tell you that code behind a socket changed its mind. Every mechanism here
is a way of *reducing what that costs*, and the reduction comes almost entirely from having assigned
the tag yourself.

---

## 12. Scalability

`[INF]` The custody gradient of Chapter 5 §2.4 makes a prediction here before any measurement does.
An MCP call is a network round trip to a system you do not control: seconds, sometimes minutes,
failing in ways local code does not. That is Activity-shaped, and it must hold an Activity's
resources — a semaphore slot and a budget reservation — and never a Step's database connection.

The violation to watch for is specific: resolving a descriptor *during* a step, because resolution
feels like a lookup. A lookup that crosses a socket is not a lookup. Descriptors are resolved from the
local registry, and the registry is refreshed by the reconciler on its own schedule.

The second scaling property is the semaphore itself. Servers are independent failure domains, so a
slow one must not consume the slots a fast one needs. One semaphore per server, sized from that
server's measured service time — Chapter 33's rule that a capacity surface is sized from its own
measurement and never from a shared multiplier.

---

## 13. Production Engineering

### 13.1 Best practices

**Start at refuse.** A runtime that cannot enumerate the servers it trusts, per digest, is not ready
to admit one.

**Make the pessimised count visible.** It is the debt figure. A tool surface that is entirely
pessimised is safe and unusable; one that is entirely pinned is a real, ongoing cost. The number
should be argued about at review.

**Never let a connection carry a credential.** Credentials attach to steps.

**Alert on `mcp.invocation.refused`, not on `mcp.tool.quarantined`.** Quarantine is normal and tracks
upstream release cadence. A refused invocation means a plan was already running against a descriptor
that moved.

**Namespace tool names by server at admission.** The alternative is a collision resolved at runtime by
ordering, which is a rug pull anyone can perform by choosing a name.

**Re-read Chapter 31 §5.5 before the first server is connected.** Egress is the bound nobody sets, and
a third-party tool is an egress path with a friendly name.

---

## 14. Relation to the Base Runtime

Nothing in Chapters 1–49 changes. That is the claim this chapter has to earn, and it earns it by
where the new component sits: admission converts a remote descriptor into an ordinary registry entry,
and every existing mechanism reads the registry it always read.

| Chapter | What it contributes here | What it gives up |
|---|---|---|
| C14 Tool Execution | The tag, the description/implementation split | Nothing; the split predicted this |
| C15 ACI Design | The description as an editable surface | The surface is no longer yours to edit |
| C22 Event Spine | Admission decisions as durable events | Nothing |
| C27 Failure Recovery | Tiers and compensations, operator-authored | Nothing |
| C30 Human Authority | The gate, at the tool boundary | Nothing |
| C31 Safety | The lattice, applied to descriptors | Nothing; §5.1 is a substitution |
| C38 Deployment | Config freeze over admissions | Nothing |

`[INF]` One clarification the reader is owed: the specification's **I15** — an unknown third-party
effect defaults to `EFFECTFUL` — already covers the general case, and a reasonable reader may ask what
this chapter adds. It adds three things. It names *who* is disqualified from setting a tag and why
(§2.2 step 3, which generalises the model's disqualification to any interested party). It makes the
default a *position* with a measurable cost rather than a fallback. And it identifies the descriptor
digest as the missing half of I22 when the binding is remote.

The specification has since taken all three. Its revision 5 adds a bridge protocol carrying the
authorship split of §4.2, the three positions of §2.3 and the digest of §5.4, together with seven
invariants covering them and a build-order stage placed after the policy engine rather than before
it. It also corrects its own earlier framing: a server-supplied effect tag is now discarded rather
than preferred to silence, which is §2.2 step 5 stated as a rule. `[INF]` A chapter whose argument
survives contact with an invariant list is in better shape than one that does not, and the reader
should treat that as the check on this chapter rather than as a citation of it.

---

## 15. Industry Perspective

`[BP]` Third-party tool supply is now the ordinary shape of a deployed agent, and the practice around
it is younger than the protocols. What is established: transports differ for local and remote servers,
and a local server launched as a subprocess inherits the caller's process context in a way a remote
one does not — which means the two deserve different default positions in the trichotomy, and a local
server is not automatically the safer of the two.

What is not established, and where this chapter is `[INF]` rather than `[BP]`: whether operator-
authored descriptors are affordable at scale. Writing a local descriptor per tool is real work, and
the honest expectation is that most deployments will pessimise most of their surface and pin the few
tools that matter. `[FUT]` If descriptor authorship is ever mechanised — a registry of reviewed
descriptors, shared the way package advisories are shared — the economics change. Nobody has built
that, and this chapter does not assume it.

The one claim worth resisting is that a marketplace, a review process or a reputation score solves
this. `[INF]` Each of those authenticates a counterparty, and §2.3 gives the reason authentication is
not verification: what changed in the cold open was not who answered.

---

## 16. Key Takeaways

1. **The registry has two authors now, and only one of them is you.** Every safety mechanism in the
   book reads the registry, and every one of them was written when there was one author.
2. **A tool's author is disqualified from setting its effect tag,** for the same reason the model is:
   the disqualification is about interest, not honesty.
3. **Three positions, no fourth.** Refuse, pessimise, pin. Refuse is the honest default. An allowlist
   is not a fourth position, because it authenticates a counterparty rather than verifying a claim.
4. **The protocol carries the cheap half.** Name, schema and description travel; tag, tier,
   compensation, credential scope, egress and approval do not.
5. **A description is untrusted content in a trusted position,** and that mismatch — not the content
   itself — is the vulnerability.
6. **Pin the descriptor digest into the activity identity.** It catches a changed claim. It cannot
   catch an unchanged one, and the tag is what survives that case.
7. **Quarantine, do not reject.** One state absorbs both failure modes.
8. **MCP does not get a port.** It is an adapter behind the tool port, and the runtime stays coherent
   without it.
9. **A third-party call is Activity-shaped.** One semaphore per server, sized from that server's own
   service time.
10. **The limit, stated plainly:** no protocol can tell you that code behind a socket changed its
    mind. Everything here reduces what that costs.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Admission controller** | The only door through which a remote descriptor becomes a registry entry, and the author of every field a server may not write. | `[INF]` | -- |
| **Descriptor digest** | A hash over the name, schema and description a server advertised, pinned into the activity identity so that a changed claim refuses the call. | `[INF]` | -- |
| **The trichotomy** | Refuse, pessimise, pin -- the three defensible positions on a third-party tool, and the argument that there is no fourth. | `[INF]` | -- |
| **Local half** | The operator-authored fields of a descriptor: effect tag, tier, compensation, credential scope, egress allowlist, approval requirement. | `[INF]` | -- |
| **Position** | Which of the three a given tool occupies, recorded so that pessimised debt is a number rather than a habit. | `[INF]` | -- |
| **Rug pull** | A tool whose descriptor or implementation changes underneath a plan that has already resolved it. | `[INF]` | -- |
| **Descriptor quarantine** | The non-terminal state a descriptor enters when its digest changes, from which re-admission requires a new decision and a new digest. | `[INF]` | -- |
---

**Level 3 gains one chapter**, and the rest of the book is unchanged.

The reason it is unchanged is the reason it was worth adding: admission converts a stranger's claim
into an ordinary registry entry, and an ordinary registry entry is what forty-nine chapters already
knew how to handle. If connecting a third-party tool had required editing the gate, the ledger or the
lattice, that would have been evidence the boundary was drawn in the wrong place. It did not, and
that is the strongest thing this chapter has to say about the architecture it was added to.
