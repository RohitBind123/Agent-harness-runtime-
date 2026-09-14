# 4 — Product Thesis, Business Analysis, and GO / NO-GO

---

## 5.1 Proposition A — "Build an AI file/document organiser for iPhone and Mac"

**Verdict: unattractive as stated. Do not build this.**

Five reasons, in descending order of how much they should worry you.

**1. The job is a chore, not a habit.** "Organise my files" is done once, in a burst of guilt, and then
not again for a year. Every product in this category has the same retention shape: strong first
session, nothing at day 30. Sparkle's answer is to target Downloads and Desktop — high-traffic folders
where mess regenerates — which is a genuine insight and also an admission that the general version of
the job does not recur.

**2. The price ceiling is already set, at roughly $5/month.** Sparkle at ~$5, The Drive AI at
$4.99–$19.99. A new entrant does not get to charge $20 for the same job description because its
internals are better.

**3. The platform owner is taking the valuable half for free.** macOS 27 and iOS 27 ship this month
with Siri in Spotlight answering natural-language questions across your documents and comparing
multiple PDFs. If your pitch is "find your stuff", you now have a free, pre-installed, better-
distributed competitor.

**4. The category is crowded on iOS and contested on Mac.** At least six live App Store products, plus
DEVONthink with twenty years of local classification and Hazel owning deterministic rules.

**5. The strongest competitor doesn't even read your files.** Sparkle classifies on filenames alone.
Either content understanding is a real gap — or it is a cost centre they correctly avoided. You do not
currently know which, and Proposition A bets the company on the first answer without testing it.

---

## 5.2 Proposition B — "Build a general Agent Brain + Runtime, iOS and macOS as first environments, one subscription"

### The strongest argument AGAINST B

*Stated as harshly as it deserves, because this is the argument that should be hardest to answer.*

You are proposing to build a general-purpose platform whose first application is one of the least
attractive consumer categories in software, and to justify the platform investment by the breadth of
applications it might later support. That is the canonical way engineering-led companies spend two
years and ship nothing anyone wants.

Concretely:

- **Environment abstractions are only correct in hindsight, after the third environment.** You have
  one real environment (macOS) and one crippled one (iOS). Any port boundary you draw now will encode
  the peculiarities of the filesystem, and will be wrong for Git, Gmail and Slack. You will pay for
  generality twice: once to build it, once to tear it out.
- **The two environments are not peers, and pretending otherwise is a product lie.** Report 2 found
  that five of eight runtime properties differ. On macOS you get a real process, real watching, real
  execution, and a Trash. On iOS you get none of those. "One agent across your devices" will be
  experienced as a capable Mac app and a manual iPhone utility that share a login — which is precisely
  the "two unrelated applications" outcome the vision says it wants to avoid.
- **The runtime does not raise willingness to pay by one dollar.** Buyers pay for outcomes. A
  transactional outbox is not an outcome.
- **The differentiation is being commoditised in public.** Staging, snapshots and progressive
  permission were published by Microsoft Research in April 2026. The interesting third of your moat is
  now a paper anyone can implement.
- **Your two biggest competitors are the two companies best positioned to make this irrelevant.**
  Apple ships search in the OS; Anthropic shipped background computer use on macOS this month to an
  installed Pro/Max base.
- **You have no code.** Fifty chapters, 4,824 lines of specification, two unreconciled vocabularies,
  and zero runtime. The distance from here to a shipped MVP is being systematically underestimated
  because the design work *feels* like progress.

### The strongest argument FOR B

The scarce thing in this market is not intelligence. It is **trustworthy mutation.**

Classification is close to solved and close to free. Sparkle demonstrates you can capture most of the
perceived value from filenames alone; Apple is putting document understanding in Spotlight for nothing.
If the product's differentiation is "understands your documents better", it is competing on the axis
that is collapsing fastest.

But nobody has solved letting a model *change* four thousand of your files and being able to live with
the consequences. This is not a hunch — it is measured. Microsoft Research analysed **290 public
reports across 13 frameworks** of agents corrupting data, deleting files and leaking secrets, and
concluded that agents *"have limited information about their filesystem effects and insufficient
control over them."* Their remedy — stage every mutation before commit, snapshot so the agent can
detect and correct its own mistakes, gate progressively instead of prompting constantly — is
independently the same design this architecture already specifies as Chapter 27's effect tiers and
ledger and Chapter 30's gate.

Two unrelated groups reasoning from different starting points arrived at the same three mechanisms.
That is the best available evidence that the design is right.

And the market is moving toward the question the architecture answers. In 2024 the question was *can
it classify?* In 2026, with agents in the OS and in the terminal, the question is *can I let it act?*
That second question is an infrastructure question — verification, provenance, idempotency, reversal —
and infrastructure questions are the only kind this architecture is good at.

Finally: **the runtime is the only asset that survives the product being wrong.** If the file wedge
fails, a runtime with durable execution, real verification and provenance redeploys onto Git, mail and
cloud storage. A file organiser redeploys onto nothing.

### Recommendation

**Neither, as written. Take B's architecture, A's scope discipline, and a different wedge.**

Build the runtime, but let a product pull it into existence one capability at a time. Never build a
port before the second consumer of that port exists. Ship macOS first and iOS as an honest companion.
And choose a wedge where the job recurs on a calendar rather than on a guilt cycle.

---

## Part 6 — The product, restated so it is buildable

**One account. One Brain — memory, taxonomy, preferences, history. Two runtimes, honestly different.**

```
                              USER
                                │
              ┌─────────────────┴─────────────────┐
              │   BRAIN  (portable, per-account)  │
              │   memory · taxonomy · preferences │
              │   world beliefs · trajectories    │
              │   goal contracts · evaluation     │
              └─────────────────┬─────────────────┘
                                │  synced via CloudKit
        ┌───────────────────────┴────────────────────────┐
        │                                                │
   macOS RUNTIME                                    iOS RUNTIME
   full agent loop                                  session agent loop
   • long-lived process                             • runs only while open
   • FSEvents observation                           • scan-on-open observation
   • Trash-backed undo                              • quarantine-backed undo
   • sandboxed subprocesses (later)                 • no execution, ever (2.5.2)
   • cloud or local inference                       • Foundation Models (4k) or cloud
```

The user-visible promise, and it should be printed on the marketing page because it is the whole
product:

> **Nothing changes on your disk until you say so. Everything that changes is written down. Anything
> written down can be undone.**

What the iPhone is genuinely *better* at, and why it earns its place rather than being a shrunken Mac:
**capture**. Paperwork enters your life through the phone — a photographed receipt, a PDF from a
mail attachment, a scanned letter. The phone is where the document is born; the Mac is where the
archive lives. That is a real division of labour, not a compromise.

---

## Part 10 — Business and competitive analysis

**Is the market crowded?** On iOS, yes — six-plus live products, none differentiated. On Mac,
contested but not saturated: Sparkle owns the consumer slot, DEVONthink the professional archive slot,
Hazel the deterministic slot, and **nobody owns "an agent I can trust to change things."**

**Does bundling iOS + macOS create real value?** Yes, but only through *shared state*, not shared
code. The Mac learns your filing conventions from a thousand documents; the iPhone applies them to the
receipt you photograph in a car park; the Mac has it filed correctly when you get home. That is a real
benefit and it is the only honest argument for one subscription. It is **not** a network effect — it
makes the product better for *you*, not for the next user.

**Is the runtime a platform or copyable infrastructure?** Copyable infrastructure, today. It becomes
platform-shaped only if it reaches a third and fourth environment and the environment abstraction
survives contact. That is a 2028 question. Anyone pitching it as a platform in 2026 is pitching a
hope.

**Is there a moat?** Ranked by how much weight each will bear:

| Candidate moat | Strength | Honest assessment |
|---|---|---|
| Accumulated per-user taxonomy and memory | **Weak but real** | Genuine switching cost after ~6 months of use. Does not compound across users |
| Trust / brand around reversibility | **Medium** | The most defensible thing available. Earned slowly, lost in one incident |
| Verification + audit as a *contractual* claim | **Medium** | Becomes strong if it ever becomes a compliance requirement. Speculative |
| The runtime itself | **Weak** | Published, standard, copyable |
| Breadth of environments | **Potentially strong, unproven** | Only if you reach three-plus. Nothing today |
| Distribution | **None** | You have none. Apple and Anthropic have all of it |

**Does one subscription make sense?** Yes — but only if the Mac carries the price. iOS alone cannot
support more than about $5/month. Mac + iOS with shared state can plausibly support $12–15/month for a
professional user. Do not price the bundle off the iPhone.

**Who is the initial buyer?** Not the mainstream consumer. The buyer is the **Mac-primary professional
with document obligations and no assistant** — freelancers, consultants, small-practice
accountants/lawyers, contractors, landlords, researchers. They have recurring paperwork, real
consequences for losing it, existing willingness to pay for tools, and enough technical confidence to
grant a folder scope.

Explicitly *not* the developer/power-user wedge, despite the vision's terminal-and-Git framing. That
is the one segment where Anthropic already ships a better product to an installed base, and where you
have no advantage whatsoever.

**Which wedge is strongest?** Ranked:

| Wedge | Recurrence | Willingness to pay | Competitive exposure | iPhone earns its place | Verdict |
|---|---|---|---|---|---|
| **Personal paperwork agent** (receipts, statements, invoices, contracts, tax) | **High — monthly and annual** | **High** | Medium | **Yes — capture** | **Recommended** |
| Downloads/Desktop cleanup | Medium | Low ($5 ceiling) | **High — Sparkle** | No | No |
| Developer project hygiene | Medium | High | **Very high — Anthropic** | No | No |
| Personal archive / "find anything" | Low | Medium | **Very high — Apple, free** | Partly | No |

**If Apple builds this?** They are already building half of it and will not build the other half.
Search and summarisation are safe for a platform owner; reorganising a user's filesystem is a support
liability Apple has never accepted. Plan for Apple to own *find*, and build on *change*.

**If OpenAI/Anthropic integrate filesystem agents natively?** Anthropic already has, on macOS, this
month. Their exposure is exactly the YoloFS finding: GUI automation with permission prompts, no
staging, no ledger, no undo. They will fix it eventually. Assume 12–18 months, not 5 years. Also
assume they will never ship an iOS equivalent, because 2.5.2 forbids it.

**If Hazel or DEVONthink add an LLM?** **This is the most likely and most dangerous scenario, and it
is under-weighted.** DEVONthink has the archive, the users, the local-ML story and twenty years of
trust; adding an LLM classifier is a point release for them, not a company. The defence is not
technology — it is being the product that *acts* rather than the product that *files*, and having
built the safety machinery they would have to add from scratch.

**Minimum defensible differentiation.** One sentence, and everything else is in service of it:

> Every mutation staged, ledgered with provenance, verified by code rather than by the model, and
> reversible — across Mac and iPhone, under one account.

---

## Part 11 — GO / NO-GO

# GO WITH MAJOR CHANGES

### 11.1 Why

The architecture answers a question the market is about to start asking, and there is independent,
measured evidence (290 incident reports across 13 frameworks) that the question is real. That is
enough to proceed.

But the product as framed would fail, for reasons that have nothing to do with the architecture. Five
changes are required, and they are not negotiable if you want the decision to hold:

**Change 1 — macOS first, iOS as an explicit companion.** Reversed from the brief. macOS is the only
one of the two platforms where the architecture's core loop — observe, decide, act, verify, recover —
can actually run. Build it where it works, then port what survives.

**Change 2 — change the wedge from "organise my files" to "handle my paperwork."** The chore does not
recur; the paperwork does. It also gives the iPhone a job it is genuinely better at.

**Change 3 — cut the terminal / Git / developer-tools environment from the roadmap entirely, for now.**
It is the vision's most exciting element and its worst business decision: maximum competition, zero
advantage, and it drags the whole product into a market where Anthropic already ships.

**Change 4 — build the vertical slice, not the runtime.** Fifty chapters of architecture must be
treated as a library to draw from, not a backlog to complete. Report 6 names the roughly 15% that goes
in the MVP and the 85% that does not.

**Change 5 — make reversibility the product, not an implementation detail.** It is the only claim you
can make that the field cannot. It must be in the onboarding, in the UI, in the marketing, and it must
be true in a way a sceptical user can check.

### 11.2 Biggest technical risk

**iOS is not an environment in the architecture's sense, and the abstraction will leak visibly.** No
background process, no recursive watching, no execution, no reversible delete, a 4,096-token local
model. The mitigation is honesty in the product design — the iPhone runtime is a *session* runtime and
should be described as one — but there is residual risk that "one agent" never feels like one agent.

*Falsified if:* six weeks of a two-platform prototype produces users who describe it as one product.

### 11.3 Biggest product risk

**Sparkle may be right that filenames are enough.** If content understanding does not measurably beat
filename-plus-metadata on real user folders, the entire premise of reading documents — with its OCR
cost, privacy conversation and prompt-injection surface — is a self-inflicted wound.

*Test this in week one, before writing runtime code:* take 500 real documents, classify with (a)
filename + metadata only, (b) full extracted content. If (b) does not win by a wide margin on a task
users care about, change the product.

### 11.4 Biggest competitive risk

**An incumbent with distribution adds the feature before you have users.** Most likely DEVONthink or
Sparkle; most damaging Apple; most capable Anthropic. You have no distribution and no brand.

*Mitigation:* pick the wedge where the incumbents are structurally reluctant — mutation with
consequences — and get to a defensible claim before a general one.

### 11.5 Biggest architectural risk

**Porting a multi-tenant server runtime onto a single-user device.** Roughly half the kernel — relay
claims, leases, sweepers, worker pools, per-tenant admission, budget ledgers — exists to arbitrate
contention that does not exist on a Mac with one user. Porting it wholesale produces a slow, complex
system whose complexity buys nothing. Deleting the wrong half loses the correctness properties that
are the entire point.

Compounding it: **the repository contains two unreconciled architectures** (handbook and
specification) using different names for overlapping concepts. Starting to code before choosing one
guarantees rework.

*Mitigation:* the explicit keep/drop list in report 6, and adopting the specification's vocabulary as
canonical.

### 11.6 What evidence would change this decision

Toward **GO** (unqualified):

- The content-vs-filename experiment (11.3) shows a large, user-visible win.
- The iOS folder-root spike (S1) shows one grant covers a whole provider tree.
- 20+ target users in a diary study re-run the agent at least monthly for three months.
- Five of ten interviewed professionals name reversibility unprompted as a reason they *don't*
  currently trust automation with their documents.

Toward **NO-GO**:

- The content experiment shows filenames within a few points of full content.
- The folder-root spike shows onboarding needs per-folder grants — that alone probably kills the
  consumer version on iOS.
- Apple's macOS 27 Siri turns out to *act* on files, not just search them.
- The diary study shows single-use behaviour, which would mean the wedge is wrong even if the
  technology is right.

### 11.7 If it were NO-GO, the better direction

For the record, since the brief asks: the runtime would be worth more as **developer infrastructure**
than as a consumer app — a durable, verifiable, reversible execution substrate that other agent
builders adopt, positioned exactly where YoloFS points. It is a harder business with a smaller market
and a longer sales cycle, and it is the honest fallback if the consumer wedge fails to show
recurrence. **Do not start there** — infrastructure with no first-party product is how you get an
abstraction nobody wants — but keep it as the pivot, and keep the runtime clean enough to make it
possible.
