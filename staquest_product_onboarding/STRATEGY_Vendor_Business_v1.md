# StaQuest B2B: Co-Founder Strategy Memo

**From:** Claude (co-founder seat)
**To:** Rohit
**Date:** 2026-08-16
**Status:** For decision, not for filing
**Supersedes as strategic direction:** `PRD_Staquest_Vendor_Onboarding.md` (which remains valid as an engineering spec for one slice of Phase 1)

---

## 0. The answer in one paragraph

You are not building a vendor onboarding portal, and you should not build a marketing
agency. You own something rarer than either: **9,387 pages of structured, AI-crawlable,
high-commercial-intent comparison data about 3,415 SaaS products** — including 3,415
"X alternatives" pages and 2,001 "X vs Y" pages. In 2026, ChatGPT cites a vendor's own
website only **12%** of the time; the other 88% of citations come from third-party
comparison pages, review sites and community threads. That means **no vendor can fix its
AI visibility by working on its own website.** They have to exist, accurately and richly,
inside sources like yours. You are one of those sources. The business is therefore not
"list your tool" and not "we'll do your marketing" — it is:

> **The independent presence, intelligence, and visibility layer for how B2B software
> gets discovered by humans and by AI models.**

Sell verified presence, sell the buyer-intent signal only you can see, and sell measured
AI visibility. **Never sell the ranking.** The neutrality is the asset that makes
everything else sellable.

---

## 1. What your inbox is actually telling you

You have three inbound messages. They look like the same request. They are three
completely different products, and the ranking of them is the whole strategy.

| # | Who | What they literally asked | What they actually want | Willingness to pay |
|---|-----|---------------------------|-------------------------|-------------------|
| 1 | **Akash G M** — Growth, Robylon AI | "Would you consider adding us?" | Category presence where buyers shortlist | Low → medium. Free-listing framing. |
| 2 | **Harsh Kanani** — Founder, Kuberns | "Feature us on your *Render Alternatives* page — we'll swap backlinks" | A slot on a **specific ranking page** | Medium. Offering barter = has budget, testing if you'll take links instead of cash. |
| 3 | **Axel Lavergne** — Founder, Reviewflowz | *"I found you through Staquest. You rank on an interesting query for me and I'd like to be on the page. What do I need to do? **How much does it cost?**"* | Placement on a page that already ranks | **High. He asked you to name a price, unprompted.** |

Read #3 again. Axel runs **Reviewflowz** — a review-management SaaS. He sells review
strategy for a living. He is the single most sophisticated possible buyer of this product,
he found you organically, and his first instinct was *"how much does it cost."*

**Three independent strangers found you through three different page types** (a tool
profile, an alternatives page, a ranking query) in roughly a month, with zero vendor-facing
marketing. That is the demand signal. It's not "people want a directory listing." It's
**"people want to be on the pages that get found."**

### What you replied

You told Axel onboarding is coming soon and asked for his email. That was the right
holding move a month ago. It is now the thing costing you money — a founder with intent
went cold. **Fixing this is Phase 0 and it starts this week.**

---

## 2. What you actually own (the asset audit)

I pulled your live site to count rather than guess.

### Asset 1 — The inventory

```
staquest.com/sitemap.xml            9,387 URLs

  3,415  /tools/{slug}                  product profiles
  3,415  /tools/{slug}/alternatives     ← "X alternatives" — the highest
                                          commercial-intent query type in B2B software
  2,001  /compare/{a}-vs-{b}            ← "X vs Y" — the second highest
    456  /workflows/{slug}              use-case / stack pages
     75  /category/{slug}
     17  /industry/{slug}
```

Those two bolded page types are **not content**. They are **inventory**. Every one is a
slot in a decision that happens at the exact moment a buyer has narrowed to a shortlist.
G2 monetises precisely this moment and charges a median of ~$27,000/year for it.

### Asset 2 — Structured data, not prose

Your `/compare` pages carry weighted scores across 10 dimensions, dual pricing-tier tables,
a 30-feature matrix, and an explicit verdict with a numeric winner. Your homepage promises
"Real pricing. Honest tiers. Zero surprise paywalls" and you avoid fake zeros — you render
"Contact sales" instead of inventing a number. **This is the single most extractable,
citable format that exists for an LLM.** Prose gets summarised; tables get quoted.

### Asset 3 — You already made the AEO decision correctly

Your `robots.txt` explicitly allows `GPTBot`, `OAI-SearchBot`, `ChatGPT-User`, `ClaudeBot`,
`Claude-Web` — with a comment that says blocking them "removes Staquest from the AI
citation pool entirely." Most publishers got this wrong and are still walling off the
crawlers. You are already in the pool. That is a compounding head start.

### Asset 4 — Demand-side attention with intent

Buyers on StaQuest compare, filter, build stacks, and ask an AI assistant. Every one of
those is an intent event that only you can observe. Hold that thought — it becomes §6.

### Asset 5 — Universal Runtime v1.0

You have a 4,824-line architecture specification for a production-grade autonomous agent
OS: three-loop execution model, single `ExecutionGraph`, durable execution, a
non-bypassable Policy Gate, human-authority approval, cost engineering and token
economics, decision observability, attribution verdicts and rollback, and a self-evolving
harness. That is not a side project — it is the **delivery engine** for §7 and the reason
you can sell a service at software margins. Most people trying to build what I'm about to
describe would have to hand-run it with contractors.

### The one number I could not verify

**I could not establish your actual traffic.** Everything downstream — pricing power,
which tier leads, whether Phase 2 is even viable — depends on it. Pull Search Console and
GA before you price anything. See §12.

---

## 3. The market, with numbers

### 3.1 The category just consolidated — and that is your opening

On **5 February 2026, G2 closed its acquisition of Capterra, Software Advice and GetApp
from Gartner for ~$110M.** The three biggest independent-ish software review destinations
are now one company, with 6M+ reviews and a stated plan for a unified pay-per-lead product.

Critics immediately flagged the obvious: one owner over the whole review layer reduces
competition and shifts pricing and access power to the platform.

Meanwhile the trust position of that platform is weak and has been for years:

- G2's own TrustScore has sat at **3.0–3.4 for two to three years**, with complaints about
  incentive disputes, opaque moderation and pay-to-play rankings unchanged through 2026.
- Category placement is acknowledged to be **influenced by sponsorship**.
- Reviews are frequently vendor-solicited with gift-card incentives, biasing the sample.
- **Over 26% of G2 reviews since ChatGPT launched are likely AI-generated** (peaking at
  34.6% in mid-2023).

**Strategic reading:** the incumbent just got bigger, more expensive, and more obviously
conflicted, in a market where the product being sold is *trust*. There has not been a
better moment in a decade to be the credible independent alternative. Your homepage line —
*"no vendor bias or paid placements"* — is worth more today than it was six months ago.

### 3.2 What vendors pay today

| Product | Price | Source |
|---|---|---|
| G2 paid profile | ~$299/mo entry | G2 seller solutions |
| G2 full contract | **~$27,000/yr median**, $2.3k starter → $32k+ enterprise | Vendr purchasing data |
| G2 Buyer Intent | **$10k–$40k/yr**, add-on only — cannot be bought standalone | Reported mid-market pricing |
| Real example | **$75k/yr** for profile signals + category intent, before tooling to act on it | Mid-market SaaS |
| Capterra PPC | $2/click floor, $20+/click in competitive categories, $500/mo minimum | Capterra |
| Bombora intent | $12k–$40k/yr | Intent market |
| Link insertion / niche edit | **$225 avg**, $100–$500 | 52,671-site analysis |
| Guest post | **$459 avg** (+7.5% YoY), $700–$1,500 on DR60+ with real traffic | 22,000+ placements |
| SaaS link-building spend | **$3,000–$10,000/mo** typical | Agency benchmarks |

Note what Harsh from Kuberns tried to do: acquire a placement worth $225–$1,500 in cash by
offering a link swap instead. **He was arbitraging the fact that you have no price list.**

### 3.3 The AEO/GEO category is real money, fast

| Player | Signal |
|---|---|
| **Profound** | $96M Series C, **$1B valuation** (Feb 2026), 400M+ prompt insights |
| **Peec AI** | $21M Series A, Berlin, ~$95–100/mo entry |
| **Scrunch AI** | ~$19M raised, $250–300/mo entry |
| **Bluefish** | $68M total |
| **Evertune** | $19M |
| Category total | **$200M+ disclosed funding**, 200+ platforms catalogued |
| Incumbents entering | HubSpot AEO, Semrush AI Visibility Toolkit, Conductor AgentStack, Siteimprove |

Pricing: Profound $499/mo → $2,000–$5,000/mo enterprise. Agencies charge **$2,000–$10,000/mo**
typical B2B, $3,500–$15,000/mo for $5–50M ARR SaaS, $25k–$50k+ enterprise.

Gartner forecasts **25% of all search interactions use AI-generated answers by end of 2026,
50% by 2028.**

### 3.4 The stat that defines the whole opportunity

> **ChatGPT cites a recommended SaaS tool's own website only 12% of the time. The other
> 88% comes from external sources — review aggregators, editorial roundups, and community
> discussions.**

Supporting shape of that 88%: the most-cited sources for B2B SaaS are Reddit, G2, PCMag,
Capterra and Gartner. Perplexity leans on Reddit for ~47% of top citations. Analyses of
1,400–1,739 real B2B buying-query citations find that cited brands almost always had strong
third-party presence.

**Every AEO tool on the market can only tell a vendor they are invisible. None of them own
a citable source. You do.** That is the difference between selling a thermometer and
selling the medicine.

### 3.5 And the traffic is worth more per visitor

AI-referred visitors convert **4–5x** better than Google organic across B2B studies;
one 312-firm study found **14.2% vs 2.8%**. B2B SaaS reports 6x–23x lifts. ChatGPT sends
~87% of AI referral visits. (Honest caveat: one study found AI-referred conversions carry
~14% lower AOV — the traffic converts more often, not necessarily bigger.)

---

## 4. Where I disagree with your framing

You wrote, roughly: *vendors want reach, so we help with SEO, AEO, marketing, slides, ads,
videos, LinkedIn and X posts.*

The instinct — "solve the need behind the request" — is right. The execution list is
mostly wrong, and I'd be a bad co-founder if I just nodded.

**Here is the actual 2026 visibility stack, ordered by leverage:**

| Rank | Lever | Why it matters now | Can StaQuest do it? |
|---|---|---|---|
| **1** | **Third-party comparison & listicle presence** | 88% of AI citations. "Top 10 X tools" pages get cited constantly. | **You *are* this.** Own it. |
| **2** | **Structured, extractable data** (JSON-LD, FAQPage, Product schema, comparison tables, answer-first 60 words) | The mechanical difference between being read and being cited | **Yes — natively, at scale, automatable** |
| **3** | **Community proof** (Reddit, HN, niche forums) | ~40–47% of commercial-query citations on Perplexity | Partly. High risk, needs authenticity, do not automate |
| **4** | **Owned comparison/alternatives/pricing depth** | The 12% slice, plus what everyone else quotes | Yes — generate for them |
| **5** | Reviews & quantified case studies | Feeds #1 and #3 | Later |
| **6** | Traditional SEO / backlinks | Still the substrate AI Overviews draw from | Partly (you *are* a link) |
| **7** | Digital PR, data studies, funding news | Earned authority | No |
| **8** | Founder-led social — LinkedIn, X | Brand and pipeline, but **near-zero AI citation weight** | No |
| **9** | Paid ads | Doesn't compound, stops when you stop | No |
| **10** | Slides, videos, ad creative | Sales collateral, not discovery | **No** |

**Your list started at #8, #9 and #10.** Those are the *lowest*-leverage, *highest*-labour,
*most*-competed items in the stack, they have nothing to do with your asset, and they turn
you into an agency: 30–45% gross margin, headcount-linear, 1–3x revenue valuation, and a
job you'd hate. There are ten thousand people who will make a SaaS company a video. There
is **one** person who owns 3,415 alternatives pages that LLMs already read.

**Correction: build 1, 2 and 4. Stay out of 7 through 10 entirely.** They are the moat-free
part, and the good news is they're also the part you were dreading.

---

## 5. The constraint that governs everything

The moment you sell a ranking position, you become G2 — the thing whose weakness is your
entire opening.

The failure sequence is not hypothetical and it is fast:
paid rankings → buyers notice → traffic decays → LLMs stop citing a source that reads
promotional → the inventory that vendors were paying for stops being worth anything →
vendors churn. **You would be selling the asset to buy the revenue.**

So the rule, and it is a hard architectural constraint, not a value statement:

> ### Sell everything except the ranking.

| ✅ Sellable — does not corrupt the ranking | ❌ Never for sale |
|---|---|
| Verification and freshness of your own data | Position in a ranked list |
| Depth: media, docs, security posture, integrations | The dimension scores |
| Buyer intent and comparison analytics | Removal or suppression of a competitor |
| AI-visibility measurement and remediation | Deletion of an unflattering fact |
| Clearly-labelled ad units, structurally separate from organic results | Editing the verdict |
| Qualified lead routing / pay-per-clickout | "Sponsored" content that reads as editorial |

You reached for the Google analogy yourself. Take the *right* lesson from it: Google's
fortune was not built by selling positions in the ten blue links. It was built by selling
**the clearly-marked slot next to them** and defending the organic result with religious
discipline. That separation is what made the ads valuable — because the results stayed
trustworthy.

Three things make this real rather than a slogan:

1. **A public Integrity Policy page**, versioned, stating exactly what money can and cannot
   buy. Publish it before you take the first dollar. It is a marketing asset in a market
   where the incumbent can't write one.
2. **FTC compliance by construction.** The 2023 Endorsement Guides require material
   connections to be disclosed "clearly and conspicuously" — unavoidable in interactive
   media, and native ads must never read as editorial. Label every paid unit at the unit,
   not in a footer.
3. **A field-level trust model in the schema** (see §9.3) so a vendor-asserted claim can
   never be silently rendered as a StaQuest-verified fact.

---

## 6. The product: three layers

### Layer 1 — **Presence** (the wedge)

*"Your product, verified and correct, in the place buyers and AI models both look."*

- Claim + verify (DNS TXT or domain email) — free
- **Auto-drafted profile**: paste your URL, an agent crawls and pre-fills everything, you
  correct it. 60 seconds to value, not a 4-step form. (See §9.7 — this replaces the PRD's
  wizard.)
- Verified badge + visible `last_verified_at` freshness date
- Enriched depth: screenshots, demo video, docs links, integration list, security posture
- **Answer-Ready Profile** — the differentiator: your verified facts are emitted as
  JSON-LD, a public structured feed, and an **MCP endpoint**, so your data propagates to
  models *through* StaQuest rather than dying on a page

**Price:** Free to claim · **$199/mo** verified + enriched

**Why they buy:** it's cheap, it's immediate, and correcting wrong public data about your
own product is an itch every vendor already has.

### Layer 2 — **Signal** (the retention engine)

You asked: *"to retain these companies, what do we need to build?"* **This is the answer,
and it is the most important section in this memo.**

A listing does not retain anyone. Nobody logs in to look at their own profile. What retains
a B2B customer is **a weekly number they cannot get anywhere else and cannot stop looking
at.**

You are sitting on that number and haven't noticed. Here is what only StaQuest can say:

> *"412 buyers put you head-to-head with Intercom this month. You lost 68% of those
> matchups. The dimension you lost on was pricing transparency — you're the only one in
> your category without a public price. 1,240 stack builds included your category; you were
> selected in 78. Buyers filtering for 'has free tier' skipped you — **you have one, it's
> just not in your profile.** And your citation rate in AI answers for 'best AI customer
> support' is 3.2%; Ada is at 19%."*

Every line of that is generated from data you already collect. And the market has already
priced this exact signal:

> *"G2 intent is different from most intent data — someone went to G2, searched your
> category, opened your profile, and clicked 'compare' against your main competitor. That's
> not a guess. That's a buyer with a shortlist."* — and G2 charges **$10k–$40k/yr** for it,
> as an add-on you cannot buy standalone.

**StaQuest generates that signal natively, on every compare page, every stack build, every
AI assistant query.**

Layer 2 ships:
- **Comparison intelligence** — who you're matched against, win/loss rate, losing dimension
- **Shortlist intent** — category and company-level demand signals, anonymised
- **Gap analysis** — the machine-generated fix list ("add pricing, you're losing on it")
- **Cross-engine AI visibility** — your brand across ChatGPT, Perplexity, Claude, Gemini,
  AI Overviews for the 100 buying queries that matter in your category. **You know which
  100 queries matter because you own the category taxonomy and watch real buyers use it.**
  Profound and Peec have to guess.
- **Weekly digest email** — the habit loop

**Price:** **$799/mo** ($9,588/yr — roughly a third of a median G2 contract)

### Layer 3 — **Amplify** (agentic, not agency)

This is where "SEO, AEO, content" belongs — as **software**, not services.

Universal Runtime is purpose-built for this and it is not a coincidence that the fit is
this good:

| What a visibility campaign needs | What your spec already has |
|---|---|
| Long-running, multi-week work that survives restarts | Durable execution, checkpoints, recovery (Ch. 21, 29) |
| Multi-step: audit → generate → review → publish → measure | `ExecutionGraph` — plan, state, progress, checkpoint in one artifact (§6) |
| The vendor must approve everything before it's published | **Human Authority** + non-bypassable Policy Gate + `effect_tag_enforcer` (Ch. 30, §7.6) |
| Predictable unit economics at a fixed price | Cost engineering and token economics (Ch. 35) |
| Reporting honestly whether the campaign worked | Noise floors and per-slice effect sizes (Ch. 41 §5.1, Ch. 48 §5.3, invariants E20/E15). **Corrected:** an earlier draft of this row claimed Ch. 46–47 lets you *prove* a campaign worked. It does not — Ch. 47's cold open is attribution mis-assigning credit with arithmetically correct verdicts, and Ch. 42 §5.5 shows gains do not compound. The defensible claim is measurement with error bars, and saying "undetermined" out loud |
| Untrusted vendor-supplied content | Safety, sandboxing, untrusted content (Ch. 31 — note its cold open has no attacker in it; the risk is a crawled page read as an instruction, and the fix is blast radius, not filtering) |

Capability packages to author: `audit_ai_visibility`, `generate_comparison_asset`,
`draft_answer_first_content`, `emit_structured_data`, `pitch_listicle_inclusion`,
`monitor_citations`, `publish_with_approval`.

**Price:** **$2,500/mo** (vs $2,000–$10,000/mo for an agency doing it by hand)

**The rule that keeps you out of the agency trap:** if a deliverable cannot be produced by
a capability package with a human approving the output, **you do not sell it.** No slides.
No ad creative. No video production. No LinkedIn ghostwriting. If a customer insists,
refer them out and take nothing.

### Plus: Leads (the ad business, later)

Pay-per-qualified-clickout at $8–25 by category, in **labelled slots that never reorder
organic results**. Capterra's model, done honestly. Only turn this on once traffic supports
it, and never before the Integrity Policy is public.

---

## 7. Revenue model

Conservative Year 1, on 3,415 listable tools:

| Tier | Price/mo | Yr-1 customers | MRR |
|---|---|---|---|
| Presence | $199 | 40 | $7,960 |
| Signal | $799 | 15 | $11,985 |
| Amplify | $2,500 | 4 | $10,000 |
| **Total** | | **59 (1.7% of catalogue)** | **≈$30k MRR → ~$360k ARR** |

Year 2 at 5% penetration (170 vendors), blended ARPU ~$700 → **~$1.4M ARR.**

Sanity checks:
- 1.7% of a catalogue converting is low for a directory with real traffic, high if traffic
  is thin. **This model is only as good as §12's first answer.**
- Signal at $9.6k/yr is ~35% of a median G2 contract. That's the pitch: *independent,
  transparent, a third of the price, and it tells you why you're losing.*
- Amplify at 80%+ gross margin because the runtime does the work. An agency doing the same
  scope runs 30–45%.

---

## 8. Sequencing — and the part that starts this week

### Phase 0 · Weeks 1–2 · **Sell it before you build it** ← start here

You have warm inbound including a founder who asked for a price. Build nothing.

1. **Reply to all three today.** Drafts are in `REPLIES_Inbound_Vendors.md`.
2. Offer a **manual** "Verified Profile + AI Visibility Report": $500 one-time or $299/mo.
   Deliver it by hand — you can produce it with Claude in an afternoon.
3. Run **15 discovery calls** with vendors already in your catalogue. One question above
   all: *"What would you pay to know who you're being compared against and why you lose?"*
4. **Success gate: 5 paying vendors and $2–5k collected.** If you cannot sell a manual
   version to warm inbound, no amount of engineering fixes that — and you'll have learned
   it for $0 instead of three months.

This also tells you which layer leads. You cannot learn that from a PRD, and neither of us
can guess it correctly.

### Phase 1 · Weeks 3–10 · Vendor Portal + Presence
The PRD's scope, corrected per §9, **plus a price**. Claim → verify → auto-drafted profile
→ verified badge → structured feed. Payments in v1, not deferred.

### Phase 2 · Months 3–6 · Signal
Comparison intelligence, gap analysis, AI visibility tracking, weekly digest. **This is the
ARPU and the retention. Do not let Phase 1 polish eat it.**

### Phase 3 · Months 6–12 · Amplify on Universal Runtime
First three capability packages, human-approval gates, attribution.

**Do not build all three at once.** The most common way this specific business dies is
building the agency layer first because it feels like the most product.

---

## 9. Honest review of your PRD

You said you can't judge it. Here is the judgment: **it is a well-executed engineering spec
and a wrong product decision.** The state machines, field table, schema and API surface are
genuinely above-average work. The problem is what it's a spec *for*.

### 9.1 It optimises your costs, not vendor value — and it has no revenue in it
Every success metric in G1–G8 is internal efficiency: review TAT, zero copy-paste, form
completion. Not one measures vendor outcome or a dollar. A product whose scorecard contains
no revenue line will not produce revenue.

### 9.2 It explicitly bans the business model
> *Non-Goals: **Payment processing** — No paid listings in V1.*
> *Open Question #4: What is the monetization model? — **OPEN — free for V1.***

There is a founder in your inbox asking *"how much does it cost?"* and the document's answer
is *"it's free."* **This is the single most expensive line in the PRD.** Charging from day
one is also the strongest anti-spam filter you will ever deploy — the PRD spends a whole
error-handling table on spam that a $199 price tag solves for free.

### 9.3 US-4 will destroy the dataset
> *"Changes write directly to the production `tool` table (no moderation queue for edits in
> V1; trust-but-verify)."*

Your entire asset is data integrity. This hands 3,415 vendors write access to it. Vendors
will inflate feature lists, soften pricing, and quietly delete limitations — not
maliciously, just as marketers. Six months in, the data reads like vendor copy, buyers stop
trusting it, LLMs stop citing it.

**Fix — field-level provenance, enforced in the schema:**

```sql
-- every mutable fact carries where it came from and how much to trust it
claim_source     VARCHAR(32) NOT NULL   -- 'staquest_verified' | 'vendor_asserted'
                                        -- | 'crawled' | 'llm_extracted'
claim_confidence NUMERIC(3,2) NOT NULL  -- 0.00–1.00
source_url       TEXT                   -- required when vendor_asserted
verified_at      TIMESTAMPTZ
```

Rules: vendor-asserted facts render with different visual weight and a "vendor-provided"
marker. **Dimension scores are never vendor-writable — ever.** Pricing claims require a
`source_url` and a re-crawl. This is your own `rules/common/data-quality.md` §2 prioritised
resolver, applied to the thing that matters most.

### 9.4 DNS verification proves control, not truth
Passing a DNS TXT check proves you own the domain. It says nothing about whether your
pricing claim is accurate. Ownership verification and claim verification are two different
systems and the PRD only has one.

### 9.5 Analytics is P1 and it's a vanity dashboard
> *"profile views (7d, 30d), comparison appearances, click-throughs"*

**Analytics is not P1. Analytics is the product** (§6, Layer 2). And those three metrics
are the wrong ones — they tell a vendor they were looked at, not what to do. The valuable
artifact is *competitive loss analysis*: who beat you, on which dimension, and the fix.
Views retain nobody. "You lost 68% of matchups against Intercom on pricing transparency"
gets opened every Monday.

### 9.6 Six things missing entirely
1. **AI/LLM visibility** — the largest single value driver in 2026, absent
2. **Structured output** — no JSON-LD, no public feed, no MCP endpoint
3. **An integrity / anti-corruption policy** — no statement of what money can't buy
4. **Vendor pricing page, contracts, refunds, churn, SLAs** — no commercial surface at all
5. **Data freshness decay** — 3,415 tools rot; nothing owns re-verification
6. **Any notion of what the vendor gets that they can measure**

### 9.7 The 4-step wizard is the wrong shape
Robylon sent you a complete product description by email, unprompted, for free. Vendors
will *give* you this data — they just won't fill in a 27-field form to do it.

**Invert it:** vendor pastes a URL → agent crawls site, pricing page, docs, G2 → renders a
pre-filled profile in ~30 seconds → vendor corrects and approves. You get better data,
they get 60-second time-to-value, and the "wow" moment is *"you already knew all this
about us."* This is a natural first Universal Runtime capability package.

### 9.8 The competitor appendix is out of date
It lists G2, Capterra, Product Hunt and StackShare as four separate competitors. **G2 has
owned Capterra since February.** And it doesn't mention the AEO category — Profound at $1B
is a more relevant comparable than StackShare.

### 9.9 What the PRD gets right (keep all of it)
The claim-flow state machine, the submission state machine, the `admin_audit_log`, the
`tool_claim_requests` audit trail, the rate limits, the email matrix, the WCAG commitment,
and the honest listing of open questions. Phase 1 should reuse it nearly wholesale — with
a price attached and §9.3 enforced.

---

## 10. Positioning and naming

**Do not spin up a separate brand.** You floated "Google built separate products." The
lesson from Google is the *ads/organic separation* (§5), not brand proliferation. What
you're selling is literally *"presence on StaQuest"* — the brand equity is the product. A
detached brand throws it away.

Structure it as: **StaQuest** (buyer surface, free, neutral, the thing that generates the
attention) → **StaQuest for Vendors** at `/vendors`, graduating to `vendors.staquest.com`
when it needs its own app shell. One data spine, two audiences, one trust reputation
carefully guarded.

Positioning line, for when the G2/Capterra merger is fresh in every SaaS marketer's mind:

> **The independent one.** Structured, verified, transparently scored — and the only
> comparison layer that shows you why you lose, not just that you were viewed.

---

## 11. Risks — what actually kills this

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | **Traffic is too thin to sell against** | **Critical** | §12 Q1. Measure before pricing. If thin: Phase 0 still works, but Layer 2 leads and you sell *insight*, not *reach* |
| 2 | **Neutrality collapses** | **Critical** | §5 as architecture; public Integrity Policy before dollar one |
| 3 | **Data rot across 3,415 tools** | High | Re-verification SLA; make freshness a paid feature so it funds itself |
| 4 | **G2 (now + Capterra) ships the same AEO product** | High | They can't credibly sell independence — it's the one thing they cannot buy. Move fast on positioning while the merger is raw |
| 5 | **You drift into being an agency** | High | The §6 rule: no deliverable that isn't a capability package. Refer out and take nothing |
| 6 | **Churn — vendor can't see ROI** | High | Layer 2 first; per-slice effect sizes with published noise floors (Ch. 41, E20) from day one. Not "we proved it worked" — see the corrected row in §7 |
| 6b | **You report noise as achievement** | **Critical** | Measure the floor before selling Layer 2 (Ch. 41 §5.1). If a vendor's citation rate moves less than the spread of two unchanged runs, reporting it as a win is the one mistake that would make you exactly what you're positioning against |
| 6c | **A churned vendor demands deletion of derived aggregates** | High | Ch. 37: derivation is one-way and cannot be undone after the fact. Settle the derivation boundary in the vendor terms **before** the first paying customer |
| 7 | **Google/AI Overviews compress comparison-site traffic** | Medium | Structural, industry-wide. Hedge: the MCP/feed layer means you get consumed even when you aren't clicked |
| 8 | **Solo founder, three layers, one runtime** | Medium | Phase gates. Phase 0 costs two weeks and de-risks all of it |

---

## 12. What I need from you before we go further

Four questions. The first one changes everything downstream; the rest change sequencing.

1. **Traffic.** Search Console + GA: monthly sessions, top 20 landing pages, and referrals
   from `chatgpt.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com`. This sets pricing
   power and decides whether Presence or Signal leads.
2. **Revenue today.** Any paying users on the $19 Pro plan? Any revenue at all?
3. **Real inbound volume.** Is it ~3/month or ~30/month? It's the difference between
   founder-led sales and needing self-serve on day one.
4. **Universal Runtime status.** Spec only, or is any of it built? Determines whether
   Phase 3 is six months or eighteen.

---

## 13. The single decision on the table

Everything above reduces to one choice:

> **Are you selling attention, or are you selling intelligence?**

**Selling attention** = listings, placements, ads. Easy to explain, easy to sell, and it
puts you in a knife fight with a company that just spent $110M consolidating the category —
while corroding the neutrality that makes your pages worth appearing on.

**Selling intelligence** = the buyer signal only you can see, plus measured AI visibility,
plus agentic remediation. Harder first sale, far harder to copy, 10x the ARPU, and it
*strengthens* neutrality instead of spending it — because the better and more honest your
data is, the more valuable the signal derived from it becomes.

**My recommendation: sell intelligence. Use presence as the wedge to get them in the door,
and never sell the ranking.**

Start with a reply to Axel. He asked you a month ago.
