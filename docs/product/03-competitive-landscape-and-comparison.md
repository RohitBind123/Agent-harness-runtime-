# 3 — Competitive Landscape + Runtime Comparison

*Research 2026-09-06. Several vendor sites (`apps.apple.com`, `filexai.com`, `makeitsparkle.co`,
`9to5mac.com`) were blocked by the network egress proxy, so some entries rest on search-result
summaries and reviewer coverage rather than fetched primary sources. Every such entry is marked.
Nothing below is asserted as DEMONSTRATED unless a source describes an observed behaviour.*

## Claim taxonomy

| Level | Meaning |
|---|---|
| **MARKETING** | On a landing page or store listing; no mechanism described |
| **DOCUMENTED** | Vendor documentation or a peer-reviewed/technical write-up describes the mechanism |
| **DEMONSTRATED** | An independent party observed it working, or the vendor published measurements |
| **INFERRED** | Our reading of what must be true given the platform constraints |

---

## 3.1 Tier 1 — the platform owner

### Apple (macOS 27 "Golden Gate", shipping this month; iOS 27 alongside)

| Dimension | Finding | Level |
|---|---|---|
| What it does | Siri in Spotlight answers natural-language questions over your documents and email, can query the contents of multiple files at once, and can compare information across multiple PDFs and generate a comparison table | MARKETING → search coverage of WWDC 2026; `www.apple.com` was blocked so this is not a fetched primary source |
| Platforms | macOS 27, iOS 27 | DOCUMENTED |
| File access model | System-level. No sandbox, no grant, no picker | INFERRED (it is the OS) |
| Semantic understanding | Yes, over document contents | MARKETING |
| Mutation | **No evidence of any.** Search, summarise, compare — not move, rename or reorganise | INFERRED |
| Memory / world model / planning / verification / recovery / audit / undo | Not described | — |
| Price | Free, pre-installed | DOCUMENTED |

**Why this matters more than any startup on the list.** Apple is taking the *find my stuff* half of
the value, for free, in the OS, on both platforms, with distribution nobody can match. Any product
whose core promise is "search your documents semantically" is now competing with a system feature.
Apple is **not** taking the *change my stuff* half, and there is a structural reason: a platform owner
that reorganises your filesystem and gets it wrong owns a support catastrophe. Apple has never shipped
destructive automation. That asymmetry is the gap.

---

## 3.2 Tier 2 — frontier-lab desktop agents

### Anthropic — Claude Cowork / Claude Code, background computer use on macOS

Announced early September 2026, days before this analysis.

| Dimension | Finding | Level |
|---|---|---|
| What it does | Controls the Mac in the background — clicking, typing, opening apps — while the user does something else | DOCUMENTED (vendor announcement, via reporting; `9to5mac.com` blocked) |
| Platforms | macOS 15+ for background mode; desktop app on macOS and Windows | DOCUMENTED |
| File access model | Prefers direct connectors (e.g. Slack); falls back to **screen capture and input simulation** when no API exists | DOCUMENTED |
| Permissions | Explicit user permission before the first action in a session; app-level granular control | DOCUMENTED |
| Sandbox | **None between the model and the desktop.** Anthropic's own safety material is reported as warning that computer use carries materially higher exposure than sandboxed code execution or permissioned file access | DOCUMENTED |
| Memory | Yes (Claude memory / project files) | DOCUMENTED |
| Planning, execution | Yes | DEMONSTRATED |
| Verification of real-world outcomes | Not described as a system property | — |
| Undo / rollback / effect ledger | **Not described** | — |
| Availability | Pro and Max tiers | DOCUMENTED |
| **iOS equivalent** | **None, and structurally cannot exist** — guideline 2.5.2 and the absence of background execution | INFERRED, and this inference is strong |

This is the most serious competitor for the macOS half. It is also the clearest illustration of the
gap: GUI automation with permission prompts and no staging, no per-effect ledger, and no undo. That is
exactly the failure class the Microsoft Research paper below measured.

### OpenAI — ChatGPT Agent (Operator merged in, July 2025); Atlas browser agent

Browser-and-VM shaped rather than local-filesystem shaped. Weaker overlap with this product than
Anthropic's. **DOCUMENTED.**

---

## 3.3 Tier 3 — Mac file organisers

### Sparkle (Every) — the most direct macOS competitor

| Dimension | Finding | Level |
|---|---|---|
| What it does | Builds a personalised folder system and files new and old documents into it; targets Downloads and Desktop | MARKETING |
| **Semantic understanding** | **Filenames only.** Reported repeatedly: it uses GPT-4 to analyse *filenames* and **never opens or reads the contents of your files** | DOCUMENTED (reviewer coverage; vendor site blocked) |
| Processing | Filenames sent to servers, retained up to 30 days; a fully offline version is described as roadmap-dependent | DOCUMENTED |
| Undo | **Everything goes to Trash first** — a real, if coarse, safety model | DOCUMENTED |
| World model / planning / verification / recovery / audit / MCP | Not described | — |
| Price | ~$5/month, 15-day trial | DOCUMENTED |
| Platforms | Mac only | DOCUMENTED |

**The most useful competitive fact in this entire report.** The strongest consumer Mac organiser
deliberately does not read file contents. Two readings, and both matter:

1. **Optimistic:** content understanding is genuinely open. Filenames cannot distinguish an insurance
   policy from a lease, and cannot extract a date, counterparty or amount.
2. **Sobering:** they may have found that filenames are *enough* for most perceived value at a
   fraction of the cost and risk — no injection surface, no privacy conversation, no OCR bill. If that
   is true, content understanding is a cost centre, not a differentiator, and the differentiation has
   to come from somewhere else. **This is a hypothesis the MVP must actually test.**

### DEVONthink — the twenty-year incumbent

Local machine-learning classification that suggests which group a document belongs in, improving after
a few hundred documents; deep archive and search. **DOCUMENTED** via long-standing reviewer coverage.
It is not agentic, has no planning or verification layer, and is a heavyweight professional tool — but
it has done "semantic filing on a Mac, locally, privately" longer than anyone, and a new entrant
should not claim to have invented the category.

### Hazel — deterministic rules

Conditional rule-based routing. Cannot interpret a document — it can find a string in a PDF but cannot
tell you it is an invoice from Acme for $1,250 dated June 3. **DOCUMENTED.** Relevant as the baseline
that already solves the easy half, cheaply and predictably.

---

## 3.4 Tier 4 — iOS AI file organisers

Search of the App Store surfaced at least six live products: **Filex AI**, **The Drive AI**,
**AI File Organizer** (Arxyn), **AI File Organizer Pro**, **AI Media Organizer (Peakto)**, plus
Mac-side entrants (NameQuick, Sortio, FilesDesk, 1dot.ai) marketing into the same query space.

| Product | Claim | Level |
|---|---|---|
| Filex AI | Reads every file you *import*, organises into smart folders, renames, plain-English search, links files to people/organisations/locations mentioned inside them; iPhone, iPad, Android, web | **MARKETING** — store listing blocked; description via search summaries |
| The Drive AI | "Agentic workspace"; AI file agents create, share, move, delete, transform and analyse documents by plain-English command; browser sidebar over Google Drive/OneDrive/Dropbox; Free / $4.99 / $9.99 / $19.99 per month | **MARKETING**, except pricing which is **DOCUMENTED** |

**The structural observation that matters more than any individual listing.** Note the word *import*
in the Filex description. Given the iOS constraints established in report 2 — no recursive watching, no
background scanning, no access outside a granted scope — the only way to build a *continuously useful*
file product on iOS is to have the user import files into your own container, which you then manage
and expose back through a File Provider extension. That is a different product from "an agent that
organises your existing Files app". It is a **destination**, not an **agent**. Every iOS entrant is
very likely solving the platform constraint the same way. **INFERRED, but strongly.**

None of these products publish anything about memory, world models, planning, verification,
reconciliation, idempotency, recovery, audit trails or rollback. Absence of publication is not
absence of capability — but for twenty consecutive dimensions across six products, it is evidence.

---

## 3.5 Tier 5 — research and open source

### YoloFS — *"Don't Let AI Agents YOLO Your Files"* (Microsoft Research, arXiv, April 2026)

Zhong, Liao, Liu, Zheng, Arpaci-Dusseau & Arpaci-Dusseau. The single most important external source
in this report. Abstract, verbatim from the Microsoft Research publication page:

> "AI coding agents operate directly on users' filesystems, where they regularly corrupt data, delete
> files, and leak secrets. Current approaches force a tradeoff between safety and autonomy:
> unrestricted access risks harm, while frequent permission prompts burden users and block agents. To
> understand this problem, we conduct the first systematic study of agent filesystem misuse, analyzing
> **290 public reports across 13 frameworks**. Our analysis reveals that today's agents have limited
> information about their filesystem effects and insufficient control over them. We therefore argue
> for shifting this information and control to the filesystem itself. Based on this principle, we
> design YoloFS, an agent-native filesystem with three techniques. **Staging** isolates all mutations
> before commit, giving users corrective control. **Snapshots** extend this control to agents, letting
> them detect and correct their own mistakes. **Progressive permission** provides users with
> preventive control by gating access with minimal interaction. … On **11 tasks with hidden side
> effects, YoloFS enables agent self-correction in 8** while keeping all effects staged and reviewable.
> On **112 routine tasks, YoloFS requires fewer user interactions while matching the baseline success
> rate**."

**DEMONSTRATED**, with numbers. Two consequences, and they cut in opposite directions:

- It is *independent, measured confirmation* that the problem this architecture solves is real, and
  that the shape of the solution — stage before commit, keep a reversible record, gate progressively
  rather than prompt constantly — is the right shape. Chapter 27's tier-1 rollback and effect ledger
  and Chapter 30's gate are the same three ideas, derived separately.
- It is also **the moat being published**. As of April 2026, staging + snapshots + progressive
  permission is in the literature, from a lab with the standing to get it adopted. Anyone can now
  build it. Treating "we stage mutations" as a defensible secret would be a mistake.

### LSFS — LLM-based Semantic File System for AIOS (ICLR 2025)

Natural-language file management over a vector-indexed semantic layer. **DOCUMENTED.** Research-grade;
no product, no safety layer, no verification.

### Filesystem-based memory for LLM agents (arXiv, 2026)

Notes convergence on the filesystem as the interface for agent memory, citing Anthropic's memory tool
as a directory of files, Claude Code's indexed memory folder, and repository markdown at ecosystem
scale. **DOCUMENTED.** Relevant because it is independent support for Chapter 12's "a file, not a
vector store" position for *harness* memory.

---

## 4 — Our runtime versus the field

Scoring: ● published mechanism · ◐ partial or implied · ○ nothing found. "Ours" is the *specified*
architecture, not built code — that distinction is the point of the last row.

| Dimension | Apple | Anthropic | Sparkle | DEVONthink | iOS organisers | YoloFS | **Ours (specified)** |
|---|---|---|---|---|---|---|---|
| Observation model (perception separated from telemetry) | ○ | ○ | ○ | ○ | ○ | ◐ | ● Ch 16 |
| Evidence / provenance labelling | ○ | ○ | ○ | ○ | ○ | ◐ | ● Ch 31 lattice |
| World model with scoped invalidation | ○ | ○ | ○ | ○ | ○ | ○ | ● Ch 25 |
| Durable state / checkpointing | ◐ | ◐ | ○ | ● | ◐ | ● | ● Ch 17, 21 |
| Memory (cross-run, propose-never-write) | ◐ | ● | ○ | ◐ | ◐ | ○ | ● Ch 12 |
| Planning as a contract | ○ | ◐ | ○ | ○ | ○ | ○ | ● Ch 10, I21 |
| Single execution graph | ○ | ○ | ○ | ○ | ○ | ○ | ● spec I27 |
| Capability abstraction above tools | ○ | ◐ | ○ | ○ | ○ | ○ | ● spec §5, I23 |
| Policy engine / effect tags from a registry | ○ | ◐ | ○ | ○ | ○ | ● | ● Ch 14, I15 |
| Approval model with parking | ○ | ◐ prompts | ○ | ○ | ○ | ● progressive | ● Ch 30 |
| **Verification of real-world outcomes** | ○ | ○ | ○ | ○ | ○ | ◐ | ● Ch 28, I18 |
| Reconciliation / level-triggered idempotence | ○ | ○ | ○ | ○ | ○ | ○ | ● I28 |
| Idempotency by action identity | ○ | ○ | ○ | ○ | ○ | ○ | ● I9 |
| Failure recovery, three effect tiers | ○ | ○ | ◐ Trash | ○ | ○ | ● | ● Ch 27 |
| Event history as system of record | ○ | ○ | ○ | ○ | ○ | ◐ | ● Ch 22 |
| Trajectory capture | ○ | ◐ | ○ | ○ | ○ | ◐ | ● Ch 16 |
| Evaluation infrastructure with a noise floor | ○ | ◐ | ○ | ○ | ○ | ● | ● Ch 41 |
| Evolution loop | ○ | ○ | ○ | ○ | ○ | ○ | ● Ch 42–49 |
| Environment abstraction | ● OS | ◐ | ○ | ○ | ○ | ○ | ● ports |
| MCP | ○ | ● | ○ | ○ | ○ | ○ | **○ — absent from our source** |
| Cross-environment portability | ● | ◐ | ○ | ○ | ○ | ○ | ● in principle |
| **Shipping code** | **●** | **●** | **●** | **●** | **●** | **●** | **○** |

### The verdict: **C — significant technical differentiation**, not D

Argued rather than asserted.

**Why not A (no differentiation).** The column is not close. On verification, idempotency,
reconciliation, effect tiers and event history, the entire commercial field scores zero. This is not
because those things are unnecessary — YoloFS measured 290 public incidents that happen precisely
because they are missing.

**Why not D (defensible platform-level differentiation).** Four reasons, and each alone would be
enough:

1. **It is published.** The most valuable third of the design — staging, snapshots, progressive
   permission — appeared in an MSR paper in April 2026. Effect ledgers, outboxes, idempotency keys and
   verdict lattices are all standard distributed-systems practice. Nothing here is a secret.
2. **It is invisible at the point of sale.** No consumer has ever paid more because a product had a
   transactional outbox. The differentiation converts to money only through an *observable promise* —
   "every change is reviewable and reversible" — and a competitor can make that promise with a much
   cruder implementation. Sparkle already does, with "everything goes to Trash first".
3. **There is no data or network effect.** Per-user taxonomy creates switching cost, which is real
   but weak, and creates nothing that makes the product better for the *next* user.
4. **The last row.** Every competitor ships. We have 50 chapters and 4,824 lines of specification and
   zero lines of runtime. Differentiation that exists only as a document is a hypothesis.

**What C actually buys.** One defensible *claim*, testable and hard to imitate quickly:

> Every change the agent makes to your files is staged before it happens, recorded as a reversible
> effect with its provenance, verified against the filesystem afterwards by code rather than by the
> model's own say-so, and undoable months later.

Anthropic cannot make that claim today about GUI automation. Sparkle can make a weaker version. Apple
does not mutate. The iOS organisers have published nothing. It is a twelve-to-eighteen-month lead on a
*claim*, not a permanent moat on a *mechanism* — and it is worth exactly as much as the number of
buyers who care about it, which report 4 argues is smaller than it feels but not zero.
