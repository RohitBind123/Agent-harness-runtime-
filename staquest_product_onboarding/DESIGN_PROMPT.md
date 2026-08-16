# Design prompt — StaQuest for Vendors

> Paste everything below into Claude. It specifies *what* to build, not how it should look.
> All visual direction — palette, type, layout, motion, density — is yours to decide.

---

Design the complete UI for **StaQuest for Vendors**, end to end. I want to see every screen
and every state before we build anything, so prioritise coverage and flow over polish on any
single screen.

Make all visual and typographic decisions yourself. Do not ask me about look and feel — pick
a direction that fits the product and apply it consistently.

---

## 1. What the product is

**StaQuest** (staquest.com) is a SaaS discovery and comparison platform used by software
buyers. It covers 3,415 products with 3,415 "X alternatives" pages, 2,001 "X vs Y" comparison
pages, and scores every product across 10 weighted dimensions. It is free for buyers and
deliberately neutral.

**StaQuest for Vendors** is the new B2B product. Software companies pay to be represented
accurately on StaQuest, to see who buyers compare them against and why they lose, and to
measure whether AI answer engines (ChatGPT, Perplexity, Claude, Gemini, Google AI Overviews)
recommend them.

**Who uses it:** a growth lead, product marketer, or founder at a B2B SaaS company. They are
busy, sceptical, and already pay G2 or Capterra roughly $27k a year. They log in weekly at
most.

**The one-line pitch:** *We show you where you stand with buyers and with AI — and we don't
sell rankings.*

### Plans

| Plan | Price | What it is |
|---|---|---|
| **Claim** | Free | Verify you own the product, correct your data |
| **Presence** | $199/mo | Verified badge, enriched profile, freshness guarantee, structured data feed |
| **Signal** | $799/mo | Comparison intelligence + AI visibility measurement + weekly digest |
| **Amplify** | $2,500/mo | Automated visibility campaigns, every action approved by the vendor |

---

## 2. Five product principles that must be visible in the UI

These are not style notes. Each one has to show up as something a user can see.

**1. Missing data is never zero.** A product with no public price shows "Contact sales" or an
em-dash, never "$0". A missing score shows "Not scored", never 0/10. Charts drop null
dimensions rather than plotting them at zero. If filtering nulls leaves too few points to
plot, show a written empty state instead of a chart.

**2. Every fact shows where it came from.** Fields are one of: *StaQuest verified*,
*Vendor provided*, *Crawled from site*, or *Not available*. These must be visually
distinguishable at a glance — vendor-provided claims must never read as though StaQuest
verified them. Show a "last verified" date wherever data freshness matters.

**3. Scores and rankings are not editable, and the UI says so out loud.** In the profile
editor, the 10 dimension scores appear read-only with a short, unapologetic explanation:
rankings and scores are never for sale, at any price. This is a selling point, not a
limitation — design it as one. Link to a public Integrity Policy page.

**4. Measurements carry error bars, and "undetermined" is a real result.** Every visibility
number is a measurement of a non-deterministic system, so it has a noise floor. A change
smaller than the floor renders as **UNDETERMINED — smaller than what we can measure**, not as
a win. This state needs a proper design; it will appear often and it is the thing that makes
the product trustworthy.

**5. Long-running work is visible and interruptible.** Profile drafting takes ~30 seconds.
A visibility audit takes tens of minutes. A campaign runs for weeks and pauses for days
waiting on approval. None of these can be a spinner. Show what stage it's at, what's done,
what's waiting, and let the user leave and come back without losing anything.

---

## 3. Screens

Organised by build milestone. Design all four; mark which milestone each screen belongs to so
I can see the phasing.

### Milestone A — Onboarding and profile

**A1 · Vendor landing page** (`/vendors`, public)
The pitch and the plan comparison. Must handle the two entry points differently: "my product
is already on StaQuest" (claim it) and "my product isn't listed" (submit it). Include the
neutrality promise prominently — it's the main differentiator against G2. A short section on
what money does and doesn't buy.

**A2 · Find your product** (public)
Search across 3,415 products. Results show product name, category, current claim status
(Unclaimed / Claimed / Verified), and a "This is us" action. Include the empty state: "We
don't have your product yet → add it."

**A3 · Claim & verify** (public)
Two verification methods, user picks one:
- **DNS TXT record** — show the exact record to add, a copy button, a "Check now" action, and
  clear states for pending / not found / verified.
- **Domain email** — send a link to an address at the product's domain. Show which address it
  went to. Handle expiry (24h) and resend.

Show a progress indicator across: choose method → verify → create account. Verification can
fail; design the failure state with what to do next, not just an error.

**A4 · Paste your URL** (the onboarding wedge)
Instead of a long form, the vendor pastes their product URL. Single input, one button. Set
the expectation that we're about to go read their site.

**A5 · Drafting in progress** (~30 seconds, long-running)
We crawl the homepage, pricing page and docs in parallel, then extract a structured profile.
Show the real stages as they complete — "Reading pricing page ✓", "Reading docs…" — not a
generic loader. Must survive the user navigating away and coming back. Show elapsed time
anchored to when it actually started, not when the component mounted.

**A6 · Review your draft** (the wow moment)
A fully pre-filled profile the vendor corrects rather than fills in. This is the most
important screen in Milestone A.

Fields: product name, tagline, description, category, tags, pricing model, pricing tiers with
prices, free tier + its limits, deployment type, ideal team size, integrations, competitors,
security/compliance (SOC 2, GDPR), docs links, screenshots.

Every field shows its provenance and a confidence indicator. Fields we couldn't determine are
explicitly marked "We couldn't find this" with a prompt to supply it — never silently blank
and never guessed. Fields extracted with low confidence are flagged for review first. Show a
profile completeness meter. Editing a field flips its provenance to "Vendor provided".

**A7 · Choose a plan & checkout**
Four options including Free. Show clearly what's free forever versus paid. Standard
card checkout, invoices, VAT/tax fields.

**A8 · Submit a new product** (not currently listed)
Same paste-URL flow as A4–A6, ending in a "submitted for review" state with a submission ID
and a status link. Show expected review time.

**A9 · Submission status** (public, no auth)
Status of a submission: Pending review / More info needed / Live / Not accepted. When more
info is needed, show exactly which fields and let them supply them inline. When not accepted,
show the reason plainly.

---

### Milestone B — The verified profile

**B1 · Vendor home / dashboard**
The screen they see weekly. Above the fold: the single most useful thing that changed since
their last visit. Below: profile health, verification status, freshness date, and anything
needing attention (stale data, low completeness, an unanswered approval).

Design for the case where nothing has changed — that will be common and must not look broken.

**B2 · Profile editor**
Full edit of everything in A6, plus media upload. Autosave with a clear saved/saving
indicator. Dimension scores shown **read-only** with the integrity explanation (principle 3).
Preview link to the live public page. Completeness meter with specific next actions
("Add pricing tiers — 3 of your 4 competitors show public pricing").

**B3 · Verification & freshness**
When each field was last verified, by whom, and against what source URL. A "Request
re-verification" action. This screen is the product for Presence-tier customers — it's the
proof they're paying for.

**B4 · Integrity Policy** (public page)
What money can and cannot buy, stated plainly in two columns. Never-for-sale list: ranking
position, dimension scores, competitor removal, fact suppression. This page should feel
confident and be genuinely readable — it's a marketing asset, not legalese.

---

### Milestone C — Signal (the retention engine)

**C1 · Comparison intelligence**
The core value. Answers: who are buyers comparing us against, and why do we lose?

Show head-to-head matchups with real volume — e.g. *412 buyers compared you against Intercom
this month; you lost 68%*. For each matchup, the dimension where the loss concentrates.
Trend over time. Ranked list of competitors by matchup volume.

Include the actionable version: *"Buyers filtering for 'has free tier' skipped you — you have
one, it's not in your profile"* with a direct link to fix it.

**C2 · AI visibility**
How often answer engines name this product, measured per slice.

Requirements that shape this screen:
- Results are grouped by **query slice** (e.g. "generic category queries", "high-intent
  comparison queries", "pricing queries") — **never one aggregate number**. A gain on one
  slice and a loss on another must be impossible to miss.
- Every number carries its **noise floor** (± X points).
- Changes smaller than the floor render as **UNDETERMINED**, visually distinct from both
  gains and losses.
- Per engine: ChatGPT, Perplexity, Claude, Gemini, AI Overviews. An engine that failed to
  respond shows **"Not measured"** — never "not mentioned". These mean different things and
  the UI must not blur them.
- Share of voice against named competitors, side by side.
- A banner state for **"Baseline invalidated — ChatGPT changed models on 12 Aug, remeasuring"**.
  This will happen every few months and needs to look like normal operation, not an error.

Example content: *"'best AI customer support' — you: 3.2% (±2.1), Ada: 19.4% (±2.1)"*.

**C3 · Audit in progress** (tens of minutes)
Fan-out across hundreds of probes. Show progress by slice and engine, running cost against
budget, and completed results as they land. Fully resumable — the user will close the tab.

**C4 · Weekly digest** (email design)
The habit loop. One email: the number that changed, the matchup that mattered, the single
recommended action. Design it as an email, not a web page.

---

### Milestone D — Amplify (campaigns under vendor authority)

**D1 · Campaigns list**
Each campaign with its state: Draft / Running / **Waiting on you** / Completed / Stopped.
Anything waiting on the vendor must be unmissable — the whole product promise is that nothing
gets published without their click.

**D2 · Campaign detail**
A campaign is a multi-week sequence of steps with dependencies. Show what's done, what's
running, what's blocked and on what, and what's waiting for approval. Include cost spent
against the budget ceiling. A campaign can sit parked for days — that's normal, and the UI
should say so rather than looking stalled.

**D3 · Approval request**
The vendor reviews a specific artifact (a comparison page, a content draft, an outreach
message) and approves, rejects with a reason, or requests changes. Show exactly what will
happen on approval and where it will be published. Approvals can be reached from email.

**D4 · Campaign results**
Per-slice effect sizes with noise floors, same rules as C2. Where an effect is inside the
floor, say so. Where several changes shipped together, state plainly that the lift cannot be
attributed to one of them — do not invent attribution. Headline metric is **lift per dollar**,
not lift.

**D5 · Billing & plan**
Current plan, usage against limits, invoice history, upgrade/downgrade, cancel. On cancel,
show what happens to their data — including a plain statement that anonymised contributions
to aggregate category benchmarks cannot be removed.

**D6 · Settings**
Account, team members and roles, notification preferences, API/feed access, delete account.

---

### Internal (admin)

**E1 · Submission review queue**
Internal reviewers approve/reject/request-info on new submissions. Show the submitted data
next to anything we already crawled, with differences highlighted. Bulk actions. Review
turnaround target is 48 hours — surface anything aging.

**E2 · Vendor accounts**
Search, plan, status, verification state, support actions.

---

## 4. Flows to show end to end

Draw these as connected sequences, not isolated screens:

1. **Cold vendor → paying customer:** landing → find product → claim → verify → paste URL →
   drafting → review draft → choose plan → checkout → dashboard
2. **Not listed → live:** landing → search (no result) → paste URL → drafting → review →
   submit → status page → approved → claim
3. **Weekly return visit:** email digest → dashboard → comparison intelligence → fix a
   profile gap → back to dashboard
4. **Approval:** email "waiting on you" → approval request → review artifact → approve →
   campaign resumes
5. **Baseline invalidated:** engine changes model → banner on AI visibility → remeasure →
   new baseline

---

## 5. States every screen needs

Show these explicitly rather than assuming them:

- **Empty** — new account, no data yet, no comparisons recorded, no campaigns
- **Partial** — some fields verified, others unknown; some engines measured, others failed
- **Loading** — including long-running work that outlives the page
- **Undetermined** — a measurement smaller than its noise floor
- **Stale** — data past its freshness window, baseline invalidated
- **Waiting on the user** — approvals, verification, requested info
- **Error** — verification failed, site unreachable, payment declined, budget ceiling hit.
  Every error says what to do next.

---

## 6. Do not build

- Any UI for buying ranking position, scores, or competitor removal — it doesn't exist
- A single aggregate "AI visibility score" — per slice only
- Any number rendered without its noise floor
- Red ✗ marks for absent features. Use a neutral dash: absence in our data is not proof the
  product lacks the feature. Confirmed support gets high visual weight; unknown gets low.
- A long multi-step form as the primary onboarding path. Paste-a-URL is the path.
- Vanity metrics as the headline (profile views, impressions). The headline is who you were
  compared against and why you lost.

---

## 7. Deliverable

Responsive (desktop-first; the approval flow must work on mobile because it arrives by
email). Use realistic content throughout — real product names (Intercom, Ada, Yellow.ai,
Render, Railway, Robylon AI, Reviewflowz, Kuberns), realistic numbers, realistic copy. No
lorem ipsum and no placeholder labels.

Show the screens in flow order with brief notes on interaction and state transitions where
they aren't obvious from the visuals.
