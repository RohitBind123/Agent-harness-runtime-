```
  Level 4 · Chapter 36
  RELIABILITY AND SLOs
  Requires   C27 Failure and Rollback, C28 Grading,
             C34 Observability, C35 Cost Engineering
  Unlocks    C41 Evaluation Infrastructure, C48 Governance
  Diagrams   Core (5)
```

# Chapter 36 — Reliability and SLOs

---

## 1. Motivation

### 1.1 Cold open

Atlas publishes a 99.5% availability target. For fourteen consecutive months it is met: 99.7, 99.6,
99.5, 99.8. The status page has been green since the previous summer. Two enterprise contracts were
signed on the strength of it.

Annualised churn is 31%.

The exit interviews say variations of the same thing. *We could not trust it.* *We were reviewing
every pull request line by line, which is what we were doing before.* *It was confidently wrong
often enough that we stopped skimming.*

Someone goes and measures. Twenty-two percent of delivered pull requests required substantive
rework — not style comments, but changes that meant the run had misunderstood the task. Every one of
those runs is counted as available. Every one returned HTTP 200, reached a terminal state, produced
an artefact, and reported success.

The SLO's definition of available is in the runbook and it is precise: *the API accepted the request
and the run reached a terminal state within the latency target.* By that definition the measurement
was honest, the target was met, and the number was true every month.

It was a promise about the machinery, made to customers who were buying the work.

### 1.2 In plain language

A service level objective is a promise you make about a system, with a number attached, that you can
be held to.

For ordinary software the promise is availability: the system answers, and answers quickly. That is
the right promise because for ordinary software, answering correctly is assumed — a database that
returns a row returns the right row.

An agent system breaks that assumption. It can answer, quickly, with something wrong, and the
answering was never the hard part. Promising availability for an agent is promising the easy half
and staying quiet about the half the customer is actually buying.

So what can you promise instead? Not that any given run succeeds — the system is non-deterministic
by design and nobody can guarantee a particular result. But three things *are* guaranteeable,
because they are properties of the runtime rather than of the model: that a run finishes rather than
hanging forever, that what it tells you about itself is true, and that anything it changed in the
world is accounted for.

Quality, meanwhile, becomes something you publish and track rather than something you promise. And
that distinction has a consequence worth getting right early: when quality drops, that is not an
outage. It is a product change, and it goes through a different process with different people —
because if every model provider update is an outage, the word stops meaning anything.

### 1.3 Why this chapter exists

Chapter 34 established that there are two observability systems answering two different questions.
This chapter is what happens when you try to make promises using only the first one's signals.

Everything needed to make better promises has already been built. Chapter 28 produces verdicts and a
false-pass rate. Chapter 27 produces outstanding obligations. Chapter 29 produces stalls and
terminal states. Chapter 30 produces gated-effect coverage. Chapter 35 produces cost per outcome.
Five chapters of mechanism, and none of them has yet been turned into something a customer can hold
you to.

There is also a boundary this chapter has to draw that nobody else can. `[INF]` **A quality
regression and an availability incident are different events with different responses**, and
conflating them is the most common structural error in operating these systems. It produces one of
two failures: either every model change becomes an incident and the on-call rotation collapses, or
quality regressions get triaged as ops problems by people with no instrument to see them. §5.4 draws
the line.

### 1.4 What previous framings got wrong

**"Availability is the SLO."** It is *an* SLO and it is the least interesting one for this class of
system. The cold open met it every month for fourteen months while its customers left.

**"Promise a success rate."** You cannot be held to a per-run outcome you do not control, and an
error budget you cannot spend deliberately is not an error budget. Success rate is a published
statistic with a trend, which is a genuinely useful thing to have and is not a promise.

**"Degrade to a cheaper model under load."** This is Chapter 35's cold open executed at incident
speed and called an availability measure. It trades the property you cannot promise for the one you
can, silently, without telling the customer which one they are getting.

**"A quality drop is an incident."** Then a provider's model update is an incident, a change to a
tool description is an incident, and the incident process becomes the change process. §5.4.

**"Error budgets do not apply to non-deterministic systems."** They apply to the mechanical
promises, which are entirely deterministic. The runtime either terminated the run or it did not.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

A courier makes three separate promises and everyone understands them as separate.

**It will arrive by Thursday** — a liveness promise about time. **It will arrive intact** — a
correctness promise about the thing itself. **We will tell you if it is lost** — an honesty promise
about the courier's own reporting. Nobody would accept a courier that hit its delivery times
perfectly while a fifth of the parcels arrived broken, and nobody would describe that courier as
reliable because its trucks ran on schedule.

That three-way split is exactly right, and the cold open is a company that measured only the first
promise while selling the second.

The break is in when you find out, and it is a large break.

A parcel's condition is **observable at delivery, by the recipient, immediately**. You open the box.
The correctness signal is instant, unambiguous, and generated by the party who cares.

A pull request's correctness is not observable at delivery. It looks fine. It passes CI. It gets
reviewed and merged, and three weeks later something breaks in production and somebody bisects back
to it — or, more often, nobody ever connects the two and the cost shows up as a general sense that
the system cannot be trusted, which is what the exit interviews said.

Two consequences follow, and both shape the rest of the chapter.

**The correctness signal arrives late and from someone else.** The customer generates it, weeks
after the run, and usually never reports it. So the internal proxy — Chapter 28's verdict — is the
only timely signal available, which makes the verdict's own accuracy (Chapter 28 §5.4's false-pass
rate) a load-bearing part of the reliability story rather than an evaluation detail.

**An error budget on quality would be spent before you could see it.** By the time three weeks of
correctness signal arrives, three weeks of budget is gone and the decisions it was meant to inform
have all been made. That is the mechanical reason quality is published rather than promised (§5.2),
independent of the non-determinism argument.

### 2.2 Why three promises, and why quality is not one of them

```
  (1) Need: promise customers something, with a number, that you
      can be held to.

  (2) Standard answer: availability. Measurable per request, well
      understood, and every tool supports it.

  (3) But a run that returns 200 and produces a wrong pull request
      is AVAILABLE. The cold open met its target for fourteen
      months while 22% of its output needed rework.

  (4) So promise correctness instead. You cannot. The system is
      non-deterministic by design; no per-run outcome is
      guaranteeable, and a promise you cannot keep on purpose is
      not a promise.

  (5) What CAN be guaranteed is mechanical -- properties of the
      RUNTIME rather than of the model:
          it TERMINATES rather than hanging
          it REPORTS its outcome truthfully
          its EFFECTS are accounted for
      Each is deterministic. The runtime either did it or did not.

  (6) So those three are the SLOs, with error budgets, because
      they can be spent deliberately and observed immediately.

  (7) Quality becomes a PUBLISHED STATISTIC with a trend, not a
      promise with a budget -- for two independent reasons: you
      do not control it per run (4), and you cannot observe it in
      time to act (2.1).

  (8) And therefore a quality regression is a PRODUCT CHANGE, not
      an incident. It goes through evaluation (C41), not through
      the pager. Otherwise a provider's model update is an
      outage and the word stops meaning anything.
```

Step (8) is the boundary that has to be drawn once, early, and defended — because during the first
quality regression everyone's instinct will be to page.

### 2.3 Three promises, one statistic

| | **Liveness** | **Honesty** | **Accounting** | *(Quality)* |
|---|---|---|---|---|
| The promise | A run reaches a terminal state within T | What the run reports about itself is true | Every effect is reversed, resolved, or named | *none* |
| Measured by | Terminal-state rate within T (C29) | Verdict audit against the golden set (C28) | Runs terminating with zero unnamed obligations (C27) | Verdict distribution |
| Deterministic? | Yes | Yes | Yes | No |
| Error budget? | Yes | Yes | Yes | No — published trend |
| Failure is | An outage | **The worst failure in this chapter** | An outage | A product regression |
| Responder | On-call | On-call, immediately | On-call | Product and evaluation |

The honesty row is the one to sit with. A system that fails and says so is usable — the customer
retries, escalates, or does it themselves. A system that fails and reports success is worse than one
that is merely unavailable, because the customer acts on the report. Chapter 28's false-pass rate is
therefore not an evaluation nicety; it is the measurement behind the promise that matters most, and
it belongs on the reliability dashboard rather than only in the evaluation report.

### 2.4 The mental model to carry

Promise the three things the runtime controls: it finishes, it tells the truth about itself, and it
accounts for what it changed. Publish quality as a tracked statistic with a trend. Keep the two
apart operationally, because a quality regression handled as an outage destroys the incident process
and an outage handled as a product issue goes unfixed. And treat honesty as the strictest of the
three, because a false success is worse than a failure.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |                    RUNTIME (C10-C35)                         |
   +--------------------------------------------------------------+
      |             |                |                    |
      | terminal    | verdicts       | obligations        | spend
      | states      | (C28)          | (C27)              | (C35)
      v             v                v                    v
   +--------------------------------------------------------------+
   |                      SLI COMPUTATION                         |
   |                                                              |
   |  LIVENESS    terminal within T           deterministic       |
   |  HONESTY     verdict matches audit       deterministic       |
   |  ACCOUNTING  zero unnamed obligations    deterministic       |
   |  ----------------------------------------------------------- |
   |  quality     verdict distribution        NOT an SLI (2.2)    |
   +--------------------------------------------------------------+
      |                                    |
      | (1) three budgets                  | (2) one trend
      v                                    v
   +---------------------------+   +---------------------------+
   |     ERROR BUDGETS         |   |   PUBLISHED STATISTICS    |
   |                           |   |                           |
   |  burn rate -> paging      |   |  quality by task type     |
   |  exhaustion -> freeze     |   |  cost per outcome (C35)   |
   |                           |   |  reviewed weekly, not     |
   |  ON-CALL owns these       |   |  paged on                 |
   +---------------------------+   +---------------------------+
      |                                    |
      v                                    v
   +---------------------------+   +---------------------------+
   |  DEGRADATION CONTROLLER   |   |  EVALUATION (C41)         |
   |                           |   |                           |
   |  shed | queue | reduce    |   |  a quality regression is  |
   |  scope -- NEVER silently  |   |  a PRODUCT CHANGE and     |
   |  reduce quality (5.3)     |   |  goes here, not to the    |
   +---------------------------+   |  pager (5.4)              |
                                   +---------------------------+

  Figure 36.1 -- Three promises and one statistic, on separate paths
                 (D1 High-Level Architecture)

  (1) budgets are spendable and observable immediately
  (2) the trend is reviewed on a cadence; it has no budget because
      it can be neither controlled per run nor observed in time
```

### 3.1 The two paths must not merge

The figure's most important feature is that the left and right halves never rejoin. That separation
is organisational as much as technical, and it is what §5.4 is about.

`[BP]` Make it structural rather than cultural: quality statistics should not be able to trigger a
page, and error-budget burn should not be able to open a product ticket. Wiring both into one
alerting system means the first quality regression pages somebody at 03:00 who has no instrument to
diagnose it and no action to take, and the second time it happens the alert gets muted.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                    RELIABILITY MACHINERY                       |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     SLI computer         |  |     Error budget          |   |
   |  |                          |  |                           |   |
   |  |  three deterministic     |  |  per objective, per        |  |
   |  |  ratios over a window    |  |  window                   |   |
   |  |                          |  |                           |   |
   |  |  liveness: terminal/T    |  |  BURN RATE, not remaining |   |
   |  |  honesty: audit match    |  |  balance -- a slow leak    |  |
   |  |  accounting: named       |  |  and a cliff need          |  |
   |  |    obligations           |  |  different responses (5.2)|   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |  Degradation controller  |  |   Honesty auditor         |   |
   |  |                          |  |                           |   |
   |  |  ladder, in order:       |  |  samples completed runs   |   |
   |  |   1 queue                |  |  and re-grades them       |   |
   |  |   2 shed (C23 sec 5.5)   |  |  against the golden set   |   |
   |  |   3 reduce SCOPE         |  |  (C28)                    |   |
   |  |                          |  |                           |   |
   |  |  NEVER: reduce quality   |  |  the ONLY timely signal   |   |
   |  |  without saying so (5.3) |  |  for the promise that     |   |
   |  |                          |  |  matters most (2.3)       |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 36.2 -- Inside the reliability machinery (D2 Low-Level
                 Architecture)
```

### 4.1 Burn rate, not remaining balance

A remaining-balance view — *we have used 40% of this month's budget* — is the standard presentation
and it is the wrong one to alert on. Two situations produce 40% consumed and need opposite
responses: a slow leak accumulating over three weeks, and a cliff that consumed 40% in the last
twenty minutes and will consume the rest by lunchtime.

`[BP]` Alert on burn rate over multiple windows — a fast one for cliffs and a slow one for leaks —
and page only on the fast one. The remaining balance belongs on the weekly review, where the
question it answers ("can we afford a risky deploy this month") is the question being asked.

### 4.2 The honesty auditor is the piece most systems lack

Liveness and accounting are computed from data the runtime already emits. Honesty is not: verifying
that a reported verdict is *true* requires re-grading, and re-grading requires a ground truth the
production run did not have.

The mechanism is Chapter 28's golden set plus sampling. A small fraction of completed runs are
re-graded offline against the full check suite and, where available, against a human judgment. The
disagreement rate is the honesty SLI.

`[BP]` Sample deliberately rather than uniformly, following Chapter 34 §5.5: over-sample runs whose
verdict was `PASS` with a `WEAK_PASS`-adjacent judge reason, runs from newly onboarded tenants, and
runs on task types whose false-pass rate has moved. A uniform sample of a 2% dishonesty rate needs a
very large denominator before it says anything.

---

## 5. What to Promise, What to Publish, and How to Degrade

### 5.1 The four objectives

```
                                                            LAYER VIEW

   PROMISED -- error budget, on-call owns, page on fast burn
   +--------------------------------------------------------------+
   |                                                               |
   |  LIVENESS       99.9% of runs reach a terminal state within   |
   |                 their class SLA                               |
   |                 SLI: terminal_within_T / admitted             |
   |                 detects: stalls (C29), stuck gates (C30),     |
   |                          silent joins (C24), poisoned relay   |
   |                          (C22)                                |
   |                                                               |
   |  HONESTY        99.5% of reported verdicts survive audit      |
   |                 SLI: 1 - disagreement_rate (4.2)              |
   |                 detects: grader drift, judge independence     |
   |                          loss (C28), false passes             |
   |                 ** the strictest of the three (2.3) **        |
   |                                                               |
   |  ACCOUNTING     99.99% of runs terminate with zero UNNAMED    |
   |                 obligations                                   |
   |                 SLI: runs with no unnamed obligation / all    |
   |                 detects: the staging migration (C27), gated-  |
   |                          effect gaps (C30)                    |
   |                 NOTE: an obligation that is NAMED in a dead   |
   |                 letter satisfies this. The promise is         |
   |                 accounting, not perfection.                   |
   |                                                               |
   +--------------------------------------------------------------+

   PUBLISHED -- trend, weekly review, NO budget, NO page
   +--------------------------------------------------------------+
   |                                                               |
   |  QUALITY        verdict distribution by task type             |
   |                 cost per successful outcome (C35)             |
   |                 plans per goal (C26)                          |
   |                                                               |
   |                 not promised because: not controllable per    |
   |                 run (2.2 step 4) AND not observable in time   |
   |                 (2.1). Either reason alone would suffice.     |
   |                                                               |
   +--------------------------------------------------------------+

   THE COLD OPEN promised availability, which is a WEAKER form of
   liveness -- it counted a terminal state as success without asking
   whether the terminal state was honest. Adding the honesty
   objective alone would have surfaced the 22% within a fortnight.

  Figure 36.3 -- Three promises, one publication (D7 Data Flow)
```

The accounting objective's note is worth emphasising because it is counter-intuitive and it makes
the objective achievable. A run that leaves a migration on staging **and raises a dead letter naming
it** has satisfied the accounting promise. The promise is not that nothing goes wrong; it is that
nothing goes wrong invisibly. That is a promise a runtime can actually keep, and it is the one
Chapter 27 was built to keep.

### 5.2 Error budgets that can actually be spent

An error budget is only useful if it can be spent deliberately. The three promised objectives
qualify: shipping a risky change, running a load test, or migrating a store all consume liveness
budget in a way the team chooses.

`[BP]` The standard policy transfers unchanged and is worth adopting rather than reinventing:

- **Budget healthy** — ship freely.
- **Burn rate elevated on the fast window** — page, and stop non-essential deploys.
- **Budget exhausted for the window** — freeze feature deploys; reliability work only until it
  recovers.

Quality cannot participate in that policy, and trying to include it breaks the policy rather than
extending it. A team that freezes deploys because the verdict distribution moved has frozen deploys
because a provider changed a model, which is both outside their control and not fixed by not
deploying.

### 5.3 Degradation, in order, and the one that is forbidden

Under load or partial failure, a system must do something other than fall over. The available moves
form a ladder, and the ordering is not arbitrary — it goes from most honest to least.

| Rung | Move | User-visible contract | Honest? |
|---|---|---|---|
| 1 | **Queue** | Slower, same result | Yes — latency is visible |
| 2 | **Shed at admission** (C23 §5.5) | Refused, with a reason | Yes — refusal is explicit |
| 3 | **Reduce scope** | Smaller task, stated up front | Yes, if stated |
| 4 | **Reduce quality silently** | Same interface, worse results | **No** |

Rungs 1 to 3 all preserve the honesty promise: the user knows what they are getting. Rung 4 does
not, and it is the one most likely to be reached for, because it is invisible and it works
immediately.

The concrete form is switching to a cheaper or faster model when the queue grows. That is
Chapter 35's cold open executed at incident speed: it trades the property you cannot promise for the
one you can, without telling anyone which trade was made. And it is worse during an incident than it
was in Chapter 35, because the degraded runs are not labelled — three weeks later nobody can tell
which pull requests came from the degraded period.

`[BP]` If quality-reducing degradation is genuinely needed, two conditions make it acceptable:
**the run is labelled with the degraded configuration in its durable record**, and **the caller is
told at submission**, not afterwards. Then it is rung 3 — a stated reduction in scope — rather than
rung 4. Everything turns on whether the customer knows.

### 5.4 A quality regression is not an incident

This is the boundary that has to be drawn once and then defended, and it will be tested the first
time the verdict distribution drops on a Sunday.

| | **Availability incident** | **Quality regression** |
|---|---|---|
| Signal | Error budget burn on liveness or accounting | Verdict distribution shift (C34 signal 9) |
| Typical cause | Saturation, a bad deploy, a dependency | Model change, tool description, context change |
| Response | Page, mitigate, roll back | Evaluate (C41), decide, ship a fix |
| Timescale | Minutes | Days |
| Owner | On-call | Product and evaluation |
| Roll back? | Almost always | Only after evaluation says it helps |

The dishonest middle case is worth naming: **a quality regression severe enough to break the honesty
promise IS an incident**, because the system is now reporting successes it did not achieve. The
boundary is not "quality never pages" — it is that quality pages through the honesty objective,
which is a promise, rather than through the distribution, which is a statistic.

`[BP]` That gives a clean operational rule. Verdict distribution moves → evaluation. Verdict
distribution moves *and* the audit disagreement rate moves → page, because the grader has stopped
tracking reality and every downstream number is now unreliable.

### 5.5 The SLO for a non-deterministic system, stated honestly to a customer

What all of this adds up to, in the language a contract would use:

> **We promise:** your run will reach a definite outcome within its stated time, we will tell you
> truthfully what that outcome was, and anything we changed outside your run will be either reversed
> or reported to you by name.
>
> **We publish:** the rate at which runs of your task type produce work that passes our checks,
> updated weekly, with its history.
>
> **We do not promise:** that any particular run succeeds.

`[BP]` The third line is the one teams resist and it is the one that builds trust. A customer told
plainly that success is not guaranteed, and shown the actual rate, can plan around it. A customer
promised 99.5% availability who discovers a 22% rework rate concludes they were misled, and the exit
interviews in the cold open are what that sounds like.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  Scenario: a provider degradation raises model latency 3x at 11:00.

  time   state       what happens                what is promised
  -----  ----------  --------------------------  -------------------
  11:00  normal      model p95 4s -> 12s
  11:02  normal      step duration p95 rises
                     (C33's early signal)
  11:05  normal      queue time rises; liveness
                     SLI still within target
  11:08  DEGRADED    degradation ladder rung 1:
                     queue. Callers see higher
                     latency, same results.      liveness at risk;
                                                 honesty intact
  11:14              fast-window burn rate on
                     LIVENESS crosses threshold  PAGE
  11:15  DEGRADED    rung 2: shed at admission
                     (C23 sec 5.5). New runs
                     refused with a reason and
                     a retry-after.              liveness protected
                                                 for admitted runs
  11:16              in-flight runs continue;
                     C29's point of no return
                     lets long runs finish
                     rather than fragment
  12:40  normal      provider recovers; shedding
                     lifted with hysteresis
  12:41              budget review: 22% of the
                     month's liveness budget
                     spent in 100 minutes
                     -> deploy freeze until the
                        burn rate normalises

  WHAT WAS NOT DONE, deliberately: nobody switched to a cheaper
  model. That would have protected the latency number by spending
  the quality that was not promised, and the affected runs would
  have been indistinguishable from the rest afterwards (5.3).

  FAILURE BRANCH -- rung 4 is taken at 11:08 instead:

    11:08  switch to a faster, weaker model
    11:09  latency recovers; liveness SLI green; no page
    11:10  dashboards normal; the incident is "handled"
    12:40  provider recovers; nobody switches back, because
           nothing is wrong
    -- three weeks later, a customer reports a cluster of poor
       pull requests. Nobody can identify which runs were affected,
       because the degraded configuration was never recorded on
       them. The incident produced no signal, cost real quality,
       and is unreconstructable.

  Figure 36.4 -- A provider degradation, handled honestly and not
                 (D4 Sequence)
```

The failure branch is the Level 3 pattern in the operational domain: the *response* to the incident
produced a second failure with no signal at all. And it looked better on every dashboard than the
correct response did, which is why §5.3 makes rung 4 a rule rather than a judgment call.

---

## 7. State Management

```
                                                            STATE VIEW

   SERVICE STATE  (derived, per objective, never merged)

      {{ normal }}
          |  fast-window burn rate elevated
          v
      {{ at_risk }}      page; stop non-essential deploys
          |
          +---- rung 1: queue --------> {{ degraded_honest }}
          |                                  |
          |     rung 2: shed                 | load returns
          |     rung 3: reduce scope         v
          |                             {{ normal }}
          |
          | budget exhausted for the window
          v
      {{ frozen }}       feature deploys blocked; reliability work
          |              only
          | budget recovers
          v
      {{ normal }}

      {{ degraded_quality }}    <-- reachable ONLY when the run
                                    records the degraded config AND
                                    the caller was told at
                                    submission (5.3). Otherwise this
                                    state is forbidden.

      ILLEGAL: {{ degraded_quality }} without a durable per-run
      record of the configuration used. An unlabelled degradation
      is unreconstructable afterwards, which means the quality it
      cost can never be attributed to it (6, failure branch).

      ILLEGAL: merging the three objectives into one service state.
      A system meeting liveness and failing honesty is failing, and
      a merged state cannot say which promise broke -- which is the
      only thing that determines who responds (5.4).

      ILLEGAL: quality statistics transitioning any of these states.
      They have no budget and no page (3.1).

  Figure 36.5 -- Service state per objective (D6 State Diagram)
```

### 7.1 Hysteresis on every threshold

Every transition here needs different thresholds for entering and leaving, or the system oscillates
at exactly the boundary — shedding, recovering, shedding again, each cycle producing a page. This is
Chapter 33 §7's requirement in a different subsystem and for the same reason.

`[BP]` Leave-thresholds meaningfully below enter-thresholds, and add a minimum dwell time in the
degraded states. Ten minutes of unnecessary shedding costs less than four pages in an hour.

### 7.2 SLI windows are rolling, and the window is a decision

A monthly window resets on the first, which means an incident on the 29th is nearly free and one on
the 2nd sets the tone for four weeks. Rolling windows remove that artefact and remove the
end-of-month gaming with it.

`[BP]` Rolling twenty-eight days for the budget, plus fast windows of an hour and six hours for
burn-rate paging. Three windows, one objective, and each answers a different question: can we ship,
is something happening now, and is something leaking.

---

## 8. Internal APIs

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

`DegradationController` splitting into two methods is the signature carrying §5.3. A single
`degrade(level)` method makes rung 4 one integer away from rung 3, reachable at 03:00 by someone
trying to stop a page. Two methods with different names and different required arguments make it a
deliberate act.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceLevelObjective:
    objective: Objective
    target: float               # 0.999, 0.995, 0.9999
    window_days: int            # rolling, not calendar (7.2)
    fast_window_hours: float    # burn-rate paging
    owner: str                  # on-call rotation, always


@dataclass(frozen=True)
class PublishedStatistic:
    """NOT an SLO. No target, no budget, no owner-on-call."""
    name: str                   # "pass_rate", "cost_per_outcome"
    by_task_type: dict[str, float]
    trend_window_days: int
    reviewed_on: str            # a cadence, not a threshold


@dataclass(frozen=True)
class RunReliabilityRecord:
    run_id: str
    reached_terminal: bool
    terminal_within_sla: bool
    reported_verdict: str
    audited_verdict: str | None      # populated by sampling (4.2)
    unnamed_obligations: int         # must be 0 for accounting
    degraded_config: str | None      # REQUIRED if degraded (7.1)
```

`PublishedStatistic` existing as a distinct type from `ServiceLevelObjective` is §3.1 in the schema.
Two types with different fields make it awkward to accidentally page on a statistic, and awkward is
what you want at the point where somebody is wiring an alert.

`RunReliabilityRecord.degraded_config` is nullable and must be non-null whenever a degraded
configuration was used. Without it the failure branch in §6 is unreconstructable, and it is one
string per run.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Runtime | SLI computer | Per-run record at terminal | Terminal state, verdict, obligations |
| Honesty auditor | SLI computer | Offline, sampled | Audited verdict versus reported |
| SLI computer | Error budget | Continuous | Three ratios over three windows |
| Error budget | Paging | Fast-window burn rate | Which objective, and its rate |
| Quality statistics | Weekly review | Scheduled report | Distribution and trend, **no page** |
| Degradation controller | Admission (C23) | Synchronous | Current rung |
| Degradation controller | Run record | Per run | Degraded config, when applicable |
| Quality statistics | Chapter 41 | On regression | A hypothesis to evaluate, not a ticket |

The fifth and eighth rows are the separation of §3.1 expressed as wiring. `[BP]` The quality path
should have no route to the pager at all — not a muted route, not a low-priority route. A route that
exists gets used during the first bad Sunday.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Availability promised, work sold | Churn, not dashboards | Add the honesty objective (§5.1). The cold open |
| Quality promised with an error budget | Deploy freezes caused by provider changes | Publish quality; promise the three mechanical objectives |
| Silent quality degradation under load | **Nothing.** No signal at all | Forbid rung 4; require disclosure and a per-run record (§5.3) |
| Quality regression paged as an incident | On-call with no instrument and no action | Route to evaluation; page only via the honesty objective (§5.4) |
| Honesty regression not paged | Customers acting on false successes | It is an incident. Audit disagreement rate is the trigger |
| Remaining-balance alerting | Slow leaks and cliffs treated identically | Burn rate over multiple windows (§4.1) |
| Uniform audit sampling | Honesty SLI too noisy to act on | Over-sample the suspicious populations (§4.2) |
| Calendar-month budget windows | End-of-month gaming; incident severity depends on the date | Rolling windows (§7.2) |
| Oscillation at a degradation threshold | Repeated pages, minutes apart | Hysteresis and minimum dwell time (§7.1) |
| Merged service state | Cannot tell which promise broke, so cannot tell who responds | State per objective (§7) |

The third row is the honest one and it deserves the emphasis. Silent quality degradation has no
detector — that is what makes it the forbidden rung rather than a discouraged one. The control is
structural: two methods, required flags, and a per-run record, because there is nothing downstream
that would catch it.

---

## 12. Scalability

**SLI computation is an aggregation over per-run records** and scales with run volume, which is
small. One record per run, three ratios, three windows.

**The honesty auditor is the cost**, because re-grading means running the full check suite and
sometimes a human review. `[BP]` Sample at a rate set by the precision needed: to detect a change in
a 2% dishonesty rate you need a few thousand audited runs per window, which at moderate volume is a
sampling rate in the low single-digit percent.

**Error budget computation is trivial and its windows are the design decision** (§7.2), not its cost.

**Degradation decisions are made per admission**, so they are on Chapter 23's hot path. `[BP]` The
controller publishes a rung as a gauge that admission reads; it does not compute anything per
request.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Honesty SLI: audit disagreement rate.** The promise that matters most, the failure that is worse
  than being down, and the number most systems do not have.
- **Liveness SLI: terminal within class SLA.** Covers stalls, stuck gates, unfired joins, and
  poisoned relays in one ratio.
- **Accounting SLI: runs with zero unnamed obligations.** Chapter 27's whole subsystem, as one
  number.
- **Fast-window burn rate, per objective.** The paging signal. Rate, never balance.
- **Verdict distribution by task type** — published, trended, and with no path to the pager.

### 13.2 The review question

For any proposed SLO or alert: **is this a promise the runtime can keep on purpose, or a statistic
about the model?**

Promises get budgets, owners, and pages. Statistics get trends, reviews, and evaluation. Almost
every argument about reliability in these systems is really this question left unasked, and asking
it usually resolves the argument in one exchange.

### 13.3 Teaching this to a new engineer

Show them the cold open: fourteen months of a met target and 31% churn. Ask what the SLO should have
been.

The first answer is almost always "success rate", and the follow-up question is what the error
budget policy would be — do we freeze deploys when a provider changes a model? Watching someone work
out that they have proposed a promise they cannot keep and a budget they cannot spend leads
naturally to the three mechanical objectives, and to the realisation that honesty was always the one
the customer actually needed.

---

## 14. Relation to AHE

`[AHE]` The source evaluates a harness by benchmark score, which is a quality statistic in this
chapter's terms. Nothing in it addresses liveness, honesty, or accounting, because a benchmark
harness does not make promises to anyone — its trials either complete or are discarded.

`[INF]` That gap becomes important the moment an evolution loop's output reaches production. A
harness variant that scores higher on the benchmark may be worse on all three promised objectives:
it may stall more, report more false successes, or leave more unnamed obligations, and none of those
appears in a score. **The evaluation gate for promoting a harness variant must therefore include the
three SLIs, not only the benchmark**, and Chapter 41 is where that gate is built.

`[INF]` The honesty objective has a sharper implication for Level 5 than for production. An
evolution loop optimises against measured outcomes, so a variant that learns to report success more
often scores better — and Chapter 28's downgrade-only lattice is what stops that being trivially
achievable. The honesty SLI is the external check that the lattice is still holding, measured
against a golden set the loop cannot write. Chapter 46 depends on it.

---

## 15. Industry Perspective

**`[DAR]` The base runtime spec's operability signals feed all three objectives directly**: terminal
states, verdicts, and the effect ledger are already emitted, so the SLIs here are aggregations over
data the runtime produces rather than new instrumentation.

**`[BP]` The three-window burn-rate approach is standard practice and transfers unchanged.** Fast
and slow windows, page on fast, review on slow. There is nothing agent-specific about it and no
reason to reinvent it.

**`[BP]` Error budget policy — freeze on exhaustion — also transfers, but only over the mechanical
objectives.** Extending it to quality produces deploy freezes triggered by other people's model
updates, which is a policy that will be abandoned within a quarter and take the rest of the policy's
credibility with it.

**`[INF]` Availability-only SLOs are near-universal in deployed agent products today**, and the cold
open is the predictable result. The reason is not carelessness: availability is what the tooling
measures out of the box, and the honesty objective requires building the auditor of §4.2, which
nothing off the shelf provides.

**`[BP]` The courier framing — on time, intact, and we tell you if it is lost — is worth using with
non-technical stakeholders verbatim.** It gets the three-way split across in one sentence and makes
the cold open's failure obvious without any technical vocabulary.

**`[FUT]` Nobody has a good answer for measuring correctness from downstream signals.** The customer
generates the real correctness signal weeks later — a revert, a follow-up fix, a bisect — and it is
almost never fed back. Mining version-control history for reverts of agent-authored changes looks
tractable and would give a true correctness measure to compare the verdict against. It appears to be
unexplored, and it is the single most valuable missing measurement in this chapter.

---

## 16. Key Takeaways

1. **Availability is a promise about the machinery, made to customers buying the work.** Fourteen
   months of a met target and 31% churn is what that looks like.
2. **Promise what the runtime controls**: it terminates, it reports truthfully, its effects are
   accounted for. All three are deterministic properties of the runtime rather than of the model.
3. **Honesty is the strictest of the three.** A system that fails and says so is usable; one that
   fails and reports success is worse than one that is down, because the customer acts on the
   report.
4. **Quality is published, not promised** — for two independent reasons: you do not control it per
   run, and you cannot observe it in time to spend a budget against it.
5. **A quality regression is a product change, not an incident**, unless it also breaks the honesty
   promise. Otherwise a provider's model update is an outage and the word stops meaning anything.
6. **Silently reducing quality under load is forbidden**, because it has no detector. Make the
   disclosure and the per-run record structural, not a judgment call at 03:00.
7. **Accounting promises visibility, not perfection.** An obligation named in a dead letter
   satisfies it. That is a promise a runtime can actually keep.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Liveness objective** | The promise that a run reaches a definite outcome within its class SLA, which covers stalls, stuck gates, and unfired joins in one ratio. | `[INF]` | Ch 41 |
| **Honesty objective** | The promise that what a run reports about itself is true, measured by auditing sampled verdicts, and the strictest of the three. | `[INF]` | Ch 41, Ch 46 |
| **Accounting objective** | The promise that every effect is reversed or named, which is satisfied by a dead letter and is therefore keepable. | `[INF]` | Ch 41 |
| **Published statistic** | A tracked quality trend with no target, no budget, and no route to the pager, kept structurally distinct from an objective. | `[INF]` | Ch 41 |
| **Burn rate** | The speed at which an error budget is consumed, over fast and slow windows, which distinguishes a cliff from a leak where a balance cannot. | `[BP]` | Ch 41 |
| **Honesty auditor** | Offline re-grading of sampled completed runs against the golden set, and the only timely signal for the promise that matters most. | `[INF]` | Ch 41 |
| **Degradation ladder** | Queue, shed, reduce scope — three moves that preserve the honesty promise, and a fourth that is forbidden because it has no detector. | `[BP]` | Ch 48 |
| **Disclosed degradation** | Reducing quality only with a per-run durable record and a caller notification, which converts a forbidden move into a stated reduction in scope. | `[BP]` | Ch 48 |
| **Quality regression** | A shift in the verdict distribution, routed to evaluation rather than to the pager unless the honesty objective also breaks. | `[INF]` | Ch 41 |
| **Rolling window** | A budget window that does not reset on a calendar boundary, removing both end-of-month gaming and date-dependent incident severity. | `[BP]` | Ch 41 |

---

**Next:** Chapter 37 — *Tenancy, Secrets, and Data Governance.* This chapter promised customers
three things about their runs. The next one is about what the system keeps afterwards — the trace
store that Chapter 34 built for debugging and Chapter 41 will need as a corpus, which is also a
verbatim archive of everything the model could see, belonging to people who did not agree to it
being kept.
