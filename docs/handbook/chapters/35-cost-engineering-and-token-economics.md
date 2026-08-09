```
  Level 4 · Chapter 35
  COST ENGINEERING AND TOKEN ECONOMICS
  Requires   C11 The Context System, C13 The Reasoning Engine,
             C28 Grading, C33 Scalability
  Unlocks    C36 Reliability and SLOs, C41 Evaluation Infrastructure,
             C46 Reward Design
  Diagrams   Core (5)
```

# Chapter 35 — Cost Engineering and Token Economics

---

## 1. Motivation

### 1.1 Cold open

Atlas's monthly model bill has grown faster than its revenue for two quarters, and the team is asked
to reduce it.

They profile the spend. Sixty-one percent of it is a single step type: the one that reads a
repository map plus the current file and decides which tool to call next. It runs on the largest
available model, dozens of times per run.

They move that step to a cheaper model. The measurements are clean: cost per call falls 62%, latency
improves, and a hundred-run sample shows the tool selection is "usually the same". Projected saving
is 40% of the total bill. The change ships on a Tuesday.

Six weeks later the bill is 18% *higher* than before the change.

The postmortem is short. Success rate on that step fell from 89% to 71%. Every failure produces a
plan repair (Chapter 26), and a repair re-derives the plan's tail and re-runs it. Runs that used to
finish in ninety steps now take a hundred and thirty. The extra steps are cheap, and there are a
great many of them, and some fraction of runs now fail entirely and are retried from the top by a
human.

Cost per call: down 62%. Cost per successful pull request: up 31%.

Both numbers are correct. Only one of them was on a dashboard, and it was the one that does not
correspond to anything the business buys.

### 1.2 In plain language

Two questions look like the same question and are not.

*What does a call cost?* is easy to measure, easy to reduce, and is what every provider's billing
page shows you. *What does a good outcome cost?* is the one that determines whether the system is
worth running, and it moves in the opposite direction surprisingly often — because anything that
makes the system worse makes it do more work, and more work costs money.

The cold open is that gap. A cheaper model made each step cost less and made the runs longer, and
the second effect was larger than the first.

There is a second problem, mechanical rather than conceptual. You cannot know what a model call will
cost until it has finished, because the cost depends on how much it writes. So a budget cannot be
enforced by checking before each call — there is nothing to check against — and it cannot be enforced
by checking afterwards, because by then the money is spent. The answer is the one hotels use for
your card at check-in: reserve an estimate up front, settle the real amount at the end.

And the third thing worth knowing before reading further: in an agent runtime, almost all of the
money goes on **input** tokens rather than output, and most of those input tokens are the
conversation so far, re-sent on every single call. The biggest cost lever is not which model you use.
It is how much you send it, every time.

### 1.3 Why this chapter exists

Chapter 11 established that context is a budgeted resource assembled fresh for every call, and
Chapter 9 noted that cost hides on the data axis — the one with no decisions on it, which is why
nobody looks there. Chapter 13 metered the model port. All three set up the accounting without doing
it.

`[DAR §6.4]` specifies reserve-then-settle, which is the mechanical half. `[AHE App. A]` supplies
the conceptual half with two metrics — tokens per trial, and success per million tokens — whose
denominators are the entire point.

The two halves meet at something that surprises people: **the cost system cannot compute its own
headline metric without the grading system.** Cost per successful outcome needs a verdict, and the
verdict comes from Chapter 28. A team that builds cost accounting before it builds grading can
measure spend precisely and cannot measure whether the spend was worth anything.

### 1.4 What previous framings got wrong

**"Reduce cost per call."** Cost per call is an input, not an outcome. It can fall while the thing
you are buying gets more expensive, which is the cold open, and the two movements are invisible to
each other on separate dashboards.

**"Use a cheaper model for the easy steps."** Sometimes correct, and it is a hypothesis rather than a
saving. The measurement that settles it is cost per successful outcome over a real corpus, and a
hundred-run sample checking whether the answers are "usually the same" does not settle it — the cold
open's sample was accurate and the conclusion was wrong.

**"Optimise the prompt."** Instruction text is a small and constant part of the input. Trajectory is
the large and growing part. Effort spent shortening a system prompt is effort spent on the wrong
term, and Chapter 11's ordering and truncation decisions dominate it by an order of magnitude.

**"Cap the budget and you are safe."** A cap checked per call lets N concurrent calls each pass
individually and collectively exceed it. Concurrency is what makes reservation necessary (§2.2).

**"Cost is a finance concern."** Cost per successful outcome is the single number that says whether
the architecture works, and it is downstream of context management, plan quality, grading accuracy,
and retry policy. It is an engineering metric that happens to be denominated in currency.

---

## 2. High-Level Mental Model

### 2.1 The analogy, and where it breaks

Budgeting a run is a hotel's pre-authorisation on a credit card.

At check-in the hotel does not know what you will spend. So it reserves an estimate — the room rate
times the nights, plus a margin for incidentals — and that amount becomes unavailable to you even
though it has not been charged. At check-out the reservation is released and the actual amount is
settled.

That is reserve-then-settle exactly, and it exists for the same reason here: the real cost is not
knowable until afterwards, and something must be prevented from being spent twice in the meantime.

The break is in how good the estimate is, and it matters more than it sounds.

A hotel's estimate is close. The room rate is known, the number of nights is known, and incidentals
are a modest fraction. The reservation is a small over-estimate and the cost of holding it is
correspondingly small.

A model call's cost varies by an order of magnitude for reasons known only after the fact. Input
size depends on what Chapter 11 assembled; output size depends on how much the model decides to
write; a reasoning-heavy call and a one-line tool selection differ by fifty times. So the reserve
must be generous — and **a generous reserve is itself a cost**, because reserved budget is budget
that cannot be spent, which reduces the concurrency a given budget supports.

That trade has no clean answer and §5.3 is about managing it. The hotel gives the right mechanism
and understates the price of using it.

### 2.2 Why reservation, and why the denominator is success

```
  (1) Need: do not spend more than the budget.

  (2) Check after each call. Too late: the money is spent, and a
      single runaway call can exceed the budget by itself.

  (3) Check before each call. Against what? The cost is unknown
      until the call returns -- output length is decided during
      generation.

  (4) So ESTIMATE and RESERVE. The budget's available amount is
      reduced when the call starts, not when it ends.

  (5) Estimates are wrong, so SETTLE: on return, release the
      reserve and record the actual. Over the run, settlement
      error averages out; without settlement it compounds.

  (6) Why reservation is not optional: with N concurrent calls,
      checking each against the remaining budget lets all N pass
      -- each is individually affordable and collectively is not.
      Reservation is what makes a budget hold under concurrency,
      and single-threaded testing never shows this.

  (7) Now the harder question: what is the budget FOR? Cost per
      call is not a business quantity. Nobody buys calls. The
      quantity that matters is cost per SUCCESSFUL OUTCOME.

  (8) Which means the cost system needs the VERDICT (C28) to
      compute its own headline number. Cost and quality cannot be
      measured separately, and a team that builds cost accounting
      before grading can measure spend precisely and cannot tell
      whether any of it bought anything.
```

Step (6) is the one that gets discovered in production, because it requires concurrency to
manifest. Step (8) is the one that reorders a roadmap.

### 2.3 Where the money actually goes

| Component | Share of spend | Why | Lever |
|---|---|---|---|
| **Input: trajectory** | ~70% | Re-sent on every call, growing with the run | Chapter 11: truncation, summarisation, ordering |
| **Input: repository / file content** | ~15% | Fetched per step, often re-fetched | Chapter 11 caching; Chapter 25's probe registry |
| **Input: instructions and tool schemas** | ~5% | Constant, cache-stable prefix | Nearly nothing to gain |
| **Output: reasoning and tool calls** | ~8% | What the model writes | Effort tier (Chapter 13) |
| **Grading** | ~2% | Chapter 28's judge, on a cheaper model | Sampling (Chapter 28 §12) |

`[INF]` Shares are illustrative of a coding agent at moderate context sizes; the ordering is the
transferable part and it is stable across every system the handbook's sources describe.

The first row is the whole cost story and it is worth stating plainly. **Input dominates output by
roughly twenty to one, and most of the input is the conversation so far, sent again.** A run of
ninety steps sends its trajectory ninety times, growing each time. That is a quadratic term in the
run's length, and it is the reason Chapter 29's six-hour runs cost what they do.

It also explains why prompt optimisation disappoints. Row three is 5% and constant; rows one and two
are 85% and growing.

### 2.4 The mental model to carry

Reserve an estimate before the call, settle the actual after it, and enforce against reserved-plus-
spent so that concurrency cannot defeat the budget. Attribute every token to a run, a tenant, and a
step type. And measure cost against successful outcomes, which requires the grader — because the
number that can be reduced without limit is the one that does not correspond to anything anyone
buys.

---

## 3. High-Level Architecture

```
                                                            LAYER VIEW

   +--------------------------------------------------------------+
   |                   ADMISSION (C23, C33)                       |
   |   allocates a run budget from the commitment estimate        |
   +--------------------------------------------------------------+
              | (1) budget: tokens, with reserves (C29 sec 4.2)
              v
   +--------------------------------------------------------------+
   |                      BUDGET LEDGER                           |
   |                                                              |
   |   available = limit - spent - RESERVED                       |
   |                              ^^^^^^^^                        |
   |   the third term is what makes concurrency safe (2.2 step 6) |
   +--------------------------------------------------------------+
        ^         |                                    ^
        |         | (2) reserve estimate               | (4) settle
        |         v                                    |     actual
        |  +--------------------------+                |
        |  |   Cost estimator         |                |
        |  |   from assembled context |                |
        |  |   size + effort tier     |                |
        |  +--------------------------+                |
        |         |                                    |
        |         v                                    |
        |  +--------------------------------------------------+
        |  |            MODEL PORT (C13)                      |
        |  |   one metered door; usage returned with the      |
        |  |   response, always                               |
        |  +--------------------------------------------------+
        |                        |
        | (3) refuse if          | (5) usage: input, output,
        |     unaffordable       |     cached-input, per call
        |                        v
        |              +---------------------------+
        +--------------|      ATTRIBUTION          |
                       |  run | tenant | step type |
                       |  | judge (separate!)      |
                       +---------------------------+
                                 |
                                 | (6) joined with VERDICTS (C28)
                                 v
                       +---------------------------+
                       |  cost per SUCCESSFUL      |
                       |  outcome -- the only      |
                       |  number that is a         |
                       |  business quantity        |
                       +---------------------------+

  Figure 35.1 -- The cost path, ending at the only number that
                 matters (D1 High-Level Architecture)

  (1) allocated at admission from C33's commitment estimate
  (2) reserved BEFORE the call, from context size and effort tier
  (3) refusal is a normal outcome; the run parks or fails cleanly
  (4) settled on return, releasing the reserve
  (5) usage is returned by the provider and must never be estimated
      after the fact
  (6) the join with C28 is what turns spend into economics
```

### 3.1 The join at the bottom is the chapter

Everything above wire (6) is accounting: careful, mechanical, and worth doing. Wire (6) is what
makes it mean something.

`[BP]` Build the join early even if the grader is crude. Cost per outcome computed against a rough
verdict is far more useful than cost per call computed precisely, because it points in the right
direction. The cold open's team had exact accounting and no join, which is how a 62% reduction
became an 18% increase without anybody being wrong about a number.

---

## 4. Low-Level Decomposition

```
                                                            LAYER VIEW

   +----------------------------------------------------------------+
   |                       COST MACHINERY                           |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     Cost estimator       |  |     Reserve ledger        |   |
   |  |                          |  |                           |   |
   |  |  input tokens: KNOWN     |  |  available = limit        |   |
   |  |    (context is assembled |  |            - spent        |   |
   |  |     before the call)     |  |            - reserved     |   |
   |  |                          |  |                           |   |
   |  |  output tokens: unknown  |  |  a reserve is HELD, not   |   |
   |  |    -> p95 for this step  |  |  charged; released on     |   |
   |  |       type and effort    |  |  settle                   |   |
   |  |       tier               |  |                           |   |
   |  |                          |  |  ORPHANED reserves are    |   |
   |  |  asymmetric: over-       |  |  the failure mode (5.3)   |   |
   |  |  estimate output         |  |                           |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   |  +--------------------------+  +---------------------------+   |
   |  |     Settler              |  |     Attribution           |   |
   |  |                          |  |                           |   |
   |  |  release reserve,        |  |  every token tagged:      |   |
   |  |  record ACTUAL usage     |  |    run | tenant | step    |   |
   |  |  from the provider       |  |    type | model | cached  |   |
   |  |                          |  |                           |   |
   |  |  never estimates after   |  |  judge cost is a SEPARATE |   |
   |  |  the fact -- the         |  |  line (C28 sec 4.2), or   |   |
   |  |  provider knows          |  |  evaluation spend hides   |   |
   |  +--------------------------+  +---------------------------+   |
   |                                                                |
   +----------------------------------------------------------------+

  Figure 35.2 -- Inside the cost machinery (D2 Low-Level
                 Architecture)
```

### 4.1 Input is known, output is not, and the estimate must be asymmetric

The estimator's job splits cleanly. Input tokens are **known exactly** — the context was assembled
before the call and can be counted. Output tokens are not knowable at all.

`[BP]` Estimate output from the p95 of the same step type at the same effort tier, not the p50. The
asymmetry is deliberate: under-reserving admits a call that then exceeds the budget, which is the
failure the mechanism exists to prevent; over-reserving costs some concurrency, which is recoverable
at settlement a few seconds later. The two errors are not comparable and the estimator should not
treat them as such.

This means reserves are systematically larger than actuals, and that is correct. §5.3 is about
keeping the gap from becoming expensive.

### 4.2 Attribution needs five tags and one separation

Every token gets tagged with the run, the tenant, the step type, the model, and whether it was
served from the provider's cache. Five low-cardinality labels — Chapter 34 §4.2's allowlist admits
all of them, and `run` goes to the trace rather than the metric.

The separation that matters: **the judge's spend is its own line**. Chapter 28 §4.2 gave the reason
from the grading side; here it is the cost side of the same argument. Evaluation spend folded into
run cost makes two questions unanswerable — what fraction of the bill is evaluation, and would
sampling the judge (Chapter 28 §12) actually save anything.

`[BP]` The same applies to Chapter 26's repairs and replans. Tag them, because the cold open is
invisible without that tag: the bill rose because repair spend rose, and repair spend that is not
distinguished from ordinary step spend looks like the runs got longer for no reason.

---

## 5. The Denominator, the Prefix, and the Reserve

### 5.1 Cost per successful outcome

`[AHE App. A]` proposes two metrics whose denominators do the work:

- **Tokens per trial** — total spend divided by attempts. Measures efficiency of the machinery.
- **Success per million tokens** — successful outcomes per unit of spend. Measures whether the
  machinery is buying anything.

The second is the headline and it is the one that moved the wrong way in the cold open. Its
computation is trivial once the join of §3.1 exists: group by task type, sum tokens, count verdicts
at `PASS` or `WEAK_PASS`, divide.

```
                                                            LAYER VIEW

   THE COLD OPEN, in three numbers

                          BEFORE          AFTER        change
                          --------------  -----------  --------
   cost per model call    $0.0180         $0.0068      -62%
   steps per run          90              130          +44%
   success rate           89%             71%          -20%

   cost per RUN           $1.62           $0.88        -46%
   cost per SUCCESS       $1.82           $1.24        -32%   ?!

   -- and yet the bill went UP 18%. The three numbers above are all
   real and all incomplete, because they omit what a failure costs
   AFTER the run ends:

   failed run, retried by a human   +1 full run  ($0.88)
   failed run, abandoned            + the engineer-hours that
                                      motivated buying the system

   cost per DELIVERED pull request
       before:  $1.62 / 0.89                        = $1.82
       after:   ($0.88 x 1.44 attempts) / 0.71      = $2.39   +31%

   The 1.44 is the retry multiplier: at a 71% success rate, a
   delivered outcome takes 1.41 attempts on average, plus the
   fraction that are abandoned and re-submitted differently.

   THE LESSON IS NOT that cheaper models are bad. It is that the
   denominator must include everything a failure causes, and a
   failure causes work OUTSIDE the run that produced it.

  Figure 35.3 -- One change, five metrics, two directions (D7 Data
                 Flow)
```

`[BP]` The retry multiplier is the term teams omit, and it is computable: attempts per delivered
outcome, from the same join. Without it a change that trades success rate for unit cost always looks
good, because the cost of the failures lands in a different row of the ledger and often in a
different quarter.

### 5.2 Behaviour in tools is cheaper than behaviour in instructions

Chapter 30 argued that a rule in the system prompt is not a control. There is a second, entirely
independent argument for the same conclusion, and it is about money.

An instruction lives in the assembled context. It is sent on **every call**, for the whole run. A
ninety-step run pays for it ninety times. It is cache-stable (Chapter 11), so the marginal cost is
the discounted cached-input rate rather than the full rate — but discounted is not free, and the
number of instructions grows monotonically over a system's life because nobody removes them.

The same behaviour encoded in a tool's schema, its argument validation, or the runner's own logic is
paid **once, at the point of use**, or not at all. A tool that refuses an invalid argument costs one
error message. An instruction saying not to pass invalid arguments costs its token count times every
call in every run forever.

`[BP]` Both arguments point the same way, which is unusually convenient: **encode behaviour in tools
and in the runner, not in instructions** — for correctness (Chapter 30) and for cost (here). When two
independent lines of reasoning select the same design, it is worth adopting without further
debate.

The measurement that makes this concrete: `[BP]` track instruction tokens as a share of input, and
watch it over quarters. It only goes up, one well-motivated addition at a time, and nobody owns
reducing it.

### 5.3 The reserve gap, and orphaned reserves

Reserves are systematically larger than actuals (§4.1). Two consequences need managing.

**The gap costs concurrency.** If reserves average 40% above actuals, the effective budget is 40%
smaller than the nominal one. `[BP]` Measure the ratio of reserved to settled, per step type, and
tighten the estimator where the ratio is worst. It is a straightforward calibration exercise and it
recovers real capacity.

**Orphaned reserves are the failure mode.** A worker that dies between reserving and settling leaves
a reserve held against a call that will never complete. Enough of them and the budget is exhausted
by phantom spend, and the symptom is a run refused for lack of budget while the ledger shows plenty
unspent.

`[BP]` Reserves carry a TTL and are swept, exactly like Chapter 27's leases and by the same
component. The TTL is the model call's timeout plus a margin. This is a small piece of work that is
invariably omitted in the first implementation and invariably needed by the third month.

### 5.4 Cached input is a first-class quantity

Providers charge less for input served from their cache, and the discount is large enough to change
design decisions rather than merely reduce a bill.

Chapter 11 already required ordering context by volatility so that the stable prefix stays byte-
identical across calls. That was argued on cache-hit grounds. Here it acquires a number: on a
ninety-step run where the stable prefix is 60% of input, cache hits on that prefix reduce total input
cost by roughly half.

`[BP]` Track cache hit rate as a metric in its own right, per step type. It is the single most
sensitive indicator that something changed in context assembly — a newly-inserted timestamp, a
re-ordered tool list, a memory entry that moved — and each of those silently converts the discounted
portion of the bill back to full price with no other symptom.

That failure has the Level 3 shape one more time: nothing errors, quality is unaffected, and the
bill rises by a third.

### 5.5 Budget exhaustion is a diagnosis, not an outcome

Chapter 29 §4.1 established three budget axes and required reporting which one was exhausted. The
cost axis has its own sub-diagnosis worth capturing, because "token budget exceeded" has at least
four distinct causes:

| Cause | Signature | Fix |
|---|---|---|
| Context grew unbounded | Input tokens per step rising within a run | Chapter 11 truncation |
| Too many steps | Step count high, tokens per step flat | Chapter 26 decomposition, or Chapter 29 stall |
| Repairs consumed it | Repair-tagged spend a large share | Chapter 26 classification |
| Estimate was wrong | Reserved-to-settled ratio far from 1 | §5.3 calibration |

`[BP]` Emit the sub-cause with the exhaustion event. Each of the four sends an investigation to a
different chapter, and the undifferentiated version sends it to whoever is on call.

---

## 6. Runtime Sequence

```
                                                             TIME VIEW

  t   Run                        Budget ledger        Attribution
  --  -------------------------  -------------------  --------------
  0   admitted; budget 500k       limit    500,000
      tokens, of which 15%        spent          0
      reserved (C29 sec 4.2)      reserved       0
                                  available 425,000
                                  (75k held: comp +
                                   finish reserves)
  1   step 1: context assembled
      input = 12,400 tokens
      (known exactly)
  2   estimator: output p95 for
      this step type at this
      effort tier = 900
      estimate = 13,300
  3   reserve 13,300              reserved  13,300
                                  available 411,700
  4   model call issued
  5   returns: input 12,400
      output 610, of which
      cached input 7,900
  6   settle                      spent     13,010
                                  reserved       0    run r_x
                                  available 411,990   tenant t_4
                                                      step select
                                                      cached 64%
  ...
 88  step 88                      spent    448,000
                                  available  1,990
 89  step 89: estimate 14,100
      > available
      REFUSED                                          budget axis
                                                       = TOKENS
                                                       sub-cause =
                                                       step count
 90  finish reserve engaged
      (C29 sec 4.2): the run
      completes its terminal
      nodes and opens the PR
 91  verdict recorded: PASS
 92  JOIN: 462k tokens, PASS
      -> this outcome cost
      $1.24, one attempt

  FAILURE BRANCH -- no reservation, only a spent counter (2.2 step 6):

    t=3   four steps run concurrently on a task graph (C24)
          each checks: available 425,000, my estimate 13,300 -> OK
          all four proceed
    t=4   four calls in flight, none recorded as spending anything
    -- at four concurrent calls this is harmless. At the 40-wide
       fan-out of C24's migration it is 532,000 tokens of committed
       spend against a 425,000 budget, and every individual check
       was correct.

  FAILURE BRANCH -- worker dies at t=4, between reserve and settle:

    reserved stays 13,300 forever
    after 30 such orphans the run is refused for lack of budget
    while `spent` shows 60% remaining
    -- reserves need a TTL and a sweeper, like leases (5.3)

  Figure 35.4 -- Reserve, settle, and two ways to get it wrong (D4
                 Sequence)
```

The first failure branch is the argument for reservation in one picture, and it is worth noting that
every individual check in it is correct. This is the same shape as Chapter 32 §5.6's per-process
fairness counter: a component that is right at concurrency one and wrong by a factor of N, with no
error either way.

---

## 7. State Management

```
                                                            STATE VIEW

   RESERVE

      {{ none }}
          |  estimator produces a figure; ledger holds it
          v
      {{ held }} ------- call returns -------> {{ settled }}
          |                                      (terminal;
          |                                       actual recorded,
          | TTL expires (worker died,             hold released)
          | call never returned)
          v
      {{ swept }}   (terminal; hold released, spend recorded as
                     UNKNOWN rather than zero -- the call may have
                     happened and the provider will bill for it)

      ILLEGAL: {{ held }} with no TTL. An unswept reserve is
      permanent phantom spend, and its symptom is a run refused
      for budget while the ledger shows plenty unspent (5.3).

      ILLEGAL: {{ swept }} recording zero spend. A call that timed
      out may well have been served and charged. Recording zero is
      a reconciliation error that shows up on the invoice and
      nowhere in the system.

   RUN BUDGET

      {{ funded }}
          |  available < next estimate
          v
      {{ exhausted }}  -- with an AXIS and a SUB-CAUSE (5.5)
          |
          +---- finish reserve remains ----> {{ finishing }}
          |                                   terminal nodes only
          |                                   (C29 sec 4.3)
          |
          +---- nothing remains -----------> {{ failed }}

  Figure 35.5 -- Reserve and budget states (D6 State Diagram)
```

### 7.1 A swept reserve is not zero spend

The second illegal transition is the one that produces a quiet discrepancy between the system's
accounting and the provider's invoice.

A call that timed out from the client's perspective may have been served and billed. Recording the
swept reserve as zero makes the internal ledger cheerful and wrong, and the gap surfaces at
month-end as an unexplained variance that nobody can attribute.

`[BP]` Record swept reserves as `UNKNOWN` spend, count them separately, and reconcile against the
provider's usage API where one exists. A rising unknown-spend count is a signal about worker
stability well before it is a signal about money.

### 7.2 The ledger is run state

Durable, owned by the run, and written in the same transaction as the step completion where
possible — Chapter 24 §5.2's argument applies unchanged. A budget ledger updated separately from the
work it accounts for has a window in which one exists without the other, and the two orderings fail
in the two familiar directions: spend recorded for work that did not happen, or work that happened
with no spend recorded.

---

## 8. Internal APIs

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

`BudgetLedger.reserve` requiring a TTL rather than accepting an optional one is the signature
carrying §5.3. An optional TTL is omitted in the first implementation, and the orphan problem is
discovered in the third month by someone debugging a run refused for budget against a ledger showing
60% unspent.

---

## 9. Data Structures

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int    # billed at a lower rate; track it (5.4)
    model_id: str
    provider_request_id: str    # for reconciliation against the invoice


@dataclass(frozen=True)
class CostTags:
    run_id: str                 # trace, not metric label (C34 sec 4.2)
    tenant: str
    step_type: str              # "select" | "edit" | "judge"
                                # | "repair" | "replan"
    model_id: str


@dataclass(frozen=True)
class BudgetState:
    limit: int
    spent: int
    reserved: int               # the term that makes concurrency safe
    unknown: int                # swept reserves; NOT zero (7.1)
    compensation_reserve: int   # C27, unspendable
    finish_reserve: int         # C29, unspendable

    @property
    def available(self) -> int:
        return (self.limit - self.spent - self.reserved - self.unknown
                - self.compensation_reserve - self.finish_reserve)
```

`BudgetState.unknown` as its own term rather than folded into `spent` is §7.1 in the schema. It is
budget that cannot be used and may or may not have been charged, and merging it with either
certainty produces a wrong number in one direction or the other.

The `available` property subtracting six terms rather than two is the whole chapter's mechanics in
one expression, and it is worth reading as such: a budget in an agent runtime is not a limit minus a
counter.

---

## 10. Communication

| From | To | Mechanism | Carries |
|---|---|---|---|
| Admission (C33) | Budget ledger | At run start | Limit, derived from commitment estimate |
| Context assembler (C11) | Estimator | Synchronous | Assembled context, for an exact input count |
| Estimator | Ledger | Synchronous | Reserve request with TTL |
| Ledger | Model port (C13) | Return value | Permission, or a refusal |
| Model port | Ledger | On return | Provider-reported usage |
| Ledger | Attribution | Synchronous | Usage plus five tags |
| Attribution | Chapter 34 metrics | Export | Spend by tenant, step type, model, cached share |
| Attribution + Chapter 28 | Reporting | Join on run id | **Cost per successful outcome** |
| Sweeper (C27) | Ledger | Periodic | Expired reserves released as `unknown` |

The last-but-one row is the one that does not exist in most systems and is the reason this chapter
sits after Chapter 28. `[BP]` It is a join on a key both sides already have, it needs no new
storage, and it is the difference between measuring spend and measuring economics.

---

## 11. Failure Modes

| Trigger | Detector | Recovery |
|---|---|---|
| Optimising cost per call | Bill rises while the optimised metric falls | Measure cost per successful outcome (§5.1). The cold open |
| Retry multiplier omitted from the denominator | Any quality-for-cost trade looks good | Attempts per delivered outcome, from the same join |
| No reservation, only a spent counter | Budget exceeded under concurrency; every check was correct | `available = limit - spent - reserved` (§2.2 step 6) |
| Orphaned reserves | Runs refused for budget while the ledger shows headroom | TTL on every reserve, swept like a lease (§5.3) |
| Swept reserve recorded as zero | Month-end variance against the invoice | Record as `unknown`; reconcile (§7.1) |
| Cache prefix broken by a context change | Bill rises ~30%; nothing else moves | Cache hit rate per step type (§5.4) |
| Judge spend folded into run spend | Cannot answer what evaluation costs | Separate step type (§4.2) |
| Repair spend undistinguished | Rising bill looks like longer runs for no reason | Tag repairs and replans (§4.2) |
| Instruction tokens growing quarter over quarter | Instruction share of input | Encode behaviour in tools, not instructions (§5.2) |
| Undifferentiated budget exhaustion | Investigations start with whoever is on call | Emit the sub-cause (§5.5) |

The sixth row is the Level 3 pattern arriving in the cost domain: a context change breaks the
cache-stable prefix, quality is unaffected, no error is raised, no latency moves, and the bill goes
up by a third. Cache hit rate is the only signal, which is why §5.4 argues for it as a first-class
metric rather than a diagnostic.

---

## 12. Scalability

**The ledger is on the hot path, once per model call.** That is roughly one operation per four
seconds per worker — trivial. `[BP]` Keep it in the same store as run state so reserve and
completion can share a transaction (§7.2), rather than in a separate fast store that reintroduces the
two-write window.

**Attribution volume equals model call volume** and is a metrics-shaped problem: five low-cardinality
tags, aggregated in process, exported periodically. The run id goes to the trace.

**The cost-per-outcome join is analytical, not operational.** It runs on a schedule over the trace
store, grouped by task type and harness version. `[BP]` Compute it daily rather than continuously;
the number is noisy at small samples and a real change takes days to be visible above the variance.

**The provider's rate limit, not cost, is the scaling ceiling** (Chapter 33 §12). Reducing tokens per
successful outcome raises effective throughput against a fixed limit, which is why cost engineering
and capacity planning are the same activity here — an unusual property, and worth exploiting.

---

## 13. Production Engineering

### 13.1 The five numbers

- **Cost per successful outcome, by task type.** The headline. Everything else is diagnosis.
- **Retry multiplier** — attempts per delivered outcome. The term whose omission makes every
  quality-for-cost trade look good.
- **Cache hit rate, per step type.** The most sensitive indicator of an accidental context change,
  and the failure has no other symptom.
- **Reserved-to-settled ratio.** Estimator calibration; a large gap is concurrency being lost to
  over-reservation.
- **Instruction share of input tokens.** It only rises, one reasonable addition at a time, and
  nobody owns reducing it.

### 13.2 The review question

For any proposed cost reduction: **what does this do to cost per successful outcome, measured over a
real corpus?**

Not cost per call, not tokens per step, and not a sample of whether the answers look similar. The
cold open's team measured carefully and measured the wrong quantity, and the question separates the
two in one sentence. If the answer is "we have not measured that", the change is a hypothesis rather
than a saving, and it should ship behind the evaluation harness of Chapter 41.

### 13.3 Teaching this to a new engineer

Give them the cold open's first three numbers — 62% cheaper per call, sample looks fine, ship it —
and ask whether to approve. Everyone approves; it is a good change on the evidence presented.

Then give them the bill six weeks later and ask what was missing. Watching someone reconstruct the
retry multiplier from first principles takes about five minutes and produces a permanent instinct
about denominators, which is the only thing in this chapter that has to be learned rather than
looked up.

---

## 14. Relation to AHE

`[AHE App. A]` Tokens per trial and success per million tokens are the source's, and both are stated
here as consequences of §2.2's derivation rather than as conventions to adopt. The second is the
headline number for an evolution loop as much as for a production system: a harness variant that
raises success and raises cost proportionally has not improved anything an operator can afford.

`[INF]` Which gives Chapter 46 a constraint worth stating early. **An evolution loop optimising
success rate alone will discover that spending more raises it** — a larger model, a higher effort
tier, more retries, more candidate plans. Every one of those is a real improvement on the measured
axis and a real regression on the axis nobody measured. The reward must be denominated in success
per unit spend, not in success.

`[INF]` And the containment note follows directly, joining the seven items Chapter 34 §14 counted.
An evolution loop that can edit budget limits, effort tiers, or the estimator's conservatism can
raise its score by spending more, and no outcome-based reward distinguishes that from getting better.
Budget policy belongs outside the evolvable workspace with the model id and the effort tier that
Chapter 20 §5.5 already placed there — which is unsurprising, since they are three views of the same
lever.

---

## 15. Industry Perspective

**`[DAR §6.4]`** Reserve-then-settle is specified, and §2.2 step (6) supplies the argument the
specification leaves implicit: reservation is not about precision, it is about concurrency. A single
worker never needs it and a fleet always does.

**`[AHE App. A]`** Success per million tokens is the metric that reorders a roadmap. Its dependency
on the grader is the part worth planning for — cost accounting built before grading can be precise
and cannot be meaningful.

**`[BP]` Input-dominated billing is specific to this workload and consistently surprises people.**
Chat applications are output-heavy; agent runtimes are input-heavy by roughly twenty to one, because
the trajectory is re-sent every step. Anyone arriving from a chat background optimises the wrong
term for a quarter.

**`[BP]` Prompt caching is the largest single cost lever available and is fragile in a
characteristic way.** The discount is substantial and the prefix must be byte-identical; a
timestamp, a re-ordered tool list, or a moved memory entry silently ends it. Chapter 11's
volatility ordering is what protects it, and §5.4's metric is what tells you when it broke.

**`[INF]` Per-tenant cost attribution is table stakes for any system that bills, and is usually
retrofitted.** The five tags cost nothing at emission and are painful to reconstruct later, because
the historical usage records do not carry them.

**`[FUT]` Learned cost estimators are an obvious improvement and are rare.** The estimator in §4.1
is a p95 lookup by step type; output length is predictable from context features to a much better
accuracy than that, and the training data is every settled reserve the system has ever recorded.
Nobody appears to be doing it, and the payoff is recovered concurrency rather than reduced spend.

---

## 16. Key Takeaways

1. **The denominator is successful outcomes, not calls.** Cost per call can fall while the thing you
   are buying gets more expensive, and both numbers are correct.
2. **Include what failures cause outside the run.** The retry multiplier is the term whose omission
   makes every quality-for-cost trade look good, and it is computable from the same join.
3. **Reserve before, settle after.** Not for precision — for concurrency. A ledger that checks only
   spent-against-limit lets N concurrent calls each pass individually and collectively exceed.
4. **Every reserve needs a TTL and a sweeper.** An orphaned reserve is permanent phantom spend whose
   symptom is a refusal against a ledger showing headroom.
5. **Input dominates output about twenty to one, and most of it is the trajectory re-sent.** Context
   management is the cost lever; model choice and prompt length are not.
6. **Encode behaviour in tools, not instructions.** Chapter 30 reached this for correctness; the
   cost argument is independent and reaches the same place, because an instruction is paid on every
   call forever.
7. **Cache hit rate is the most sensitive metric in this chapter.** A broken prefix raises the bill
   by a third with no error, no latency change, and no quality effect.

**Terms introduced in this chapter**

| Term | In one sentence | Tag | Next needed in |
|------|-----------------|-----|----------------|
| **Cost per successful outcome** | Total spend divided by delivered results, including the retries that failures caused — the only cost figure that is a business quantity. | `[AHE]` | Ch 41, Ch 46 |
| **Retry multiplier** | Attempts per delivered outcome, the omitted term that makes any quality-for-cost trade look favourable. | `[INF]` | Ch 41 |
| **Reserve-then-settle** | Holding an estimated cost before a call and recording the actual after, which is what makes a budget hold under concurrency. | `[DAR]` | Ch 36 |
| **Reserve gap** | The systematic excess of reserves over actuals, which is deliberate, costs concurrency, and is a calibration exercise. | `[INF]` | Ch 36 |
| **Orphaned reserve** | A hold left by a worker that died before settling, which becomes permanent phantom spend without a TTL and a sweeper. | `[BP]` | Ch 36 |
| **Unknown spend** | A swept reserve recorded as neither spent nor free, because a timed-out call may still have been served and billed. | `[BP]` | Ch 37 |
| **Cached input** | Input served from the provider's cache at a lower rate, protected by a byte-identical stable prefix and broken silently by any change to it. | `[BP]` | Ch 38 |
| **Instruction share** | Instruction tokens as a fraction of input, which rises monotonically over a system's life because nobody owns reducing it. | `[INF]` | Ch 38 |
| **Cost attribution tags** | Run, tenant, step type, model, and cached fraction — with judge, repair, and replan as distinct step types. | `[BP]` | Ch 37, Ch 41 |
| **Budget sub-cause** | Which of context growth, step count, repair spend, or estimator error exhausted a token budget, since each sends the investigation to a different chapter. | `[INF]` | Ch 36 |

---

**Next:** Chapter 36 — *Reliability and SLOs.* This chapter measured what good outcomes cost. The
next one asks what you can honestly promise about a system that is non-deterministic by design —
starting with a team that hit its availability target every month for a year while its customers
left, because "available" and "correct" were never the same promise.
