# StaQuest B2B — 90-day plan

Working plan for the vendor business. Strategy: [`STRATEGY_Vendor_Business_v1.md`](./STRATEGY_Vendor_Business_v1.md).
Send-this-week drafts: [`REPLIES_Inbound_Vendors.md`](./REPLIES_Inbound_Vendors.md).

**The rule that governs every item below: sell everything except the ranking.**

---

## Phase 0 · Weeks 1–2 · Validate with money, build nothing

Gate: **5 paying vendors, $2–5k collected.** Do not start Phase 1 until this clears.

### Measure first (do this before quoting anyone a price)
- [ ] Search Console: monthly impressions/clicks, top 20 landing pages, top queries
- [ ] GA: sessions/mo, and referrals from `chatgpt.com`, `perplexity.ai`, `claude.ai`,
      `gemini.google.com`, `copilot.microsoft.com`
- [ ] Count: how many `/alternatives` and `/compare` pages have any impressions at all
- [ ] Baseline your own AI visibility — run 20 category queries through ChatGPT and
      Perplexity, record whether StaQuest is cited. This is both a benchmark and the
      demo asset for every sales call.

### Sell
- [ ] Reply to **Axel Lavergne** — offer the free report first (highest priority, waiting since 4 July)
- [ ] Reply to **Akash G M / Robylon** — free listing + $299/mo verified
- [ ] Reply to **Harsh Kanani / Kuberns** — decline the link swap, offer merit review + $299/mo
- [ ] Build the manual deliverable once (report template + profile format), reuse for all
- [ ] Pick 15 catalogue vendors with visible budget; send the discovery email
- [ ] Run 15 calls, log answers verbatim to `discovery-notes.md`
- [ ] Stripe payment link — that is the entire billing system for Phase 0

### Decide
- [ ] From Q2 of the discovery script: set the Layer 2 price
- [ ] From Q4: set the ceiling (what they pay G2/Capterra today)
- [ ] Write the **public Integrity Policy** page — what money can and cannot buy.
      **Ship before the first dollar, not after.**

---

## Phase 1 · Weeks 3–10 · Presence (Vendor Portal)

Reuse the PRD wholesale where §9.9 of the strategy says it's sound. Change these:

- [ ] **Payments in v1.** Delete the "no paid listings" non-goal. Stripe + plans + invoices
- [ ] **Field-level provenance** before any vendor write path exists:
      `claim_source`, `claim_confidence`, `source_url`, `verified_at`
- [ ] **Dimension scores are not vendor-writable.** Enforce at the DB layer, not the API
- [ ] Vendor-asserted facts render with distinct visual weight + "vendor-provided" marker
- [ ] Replace the 4-step wizard with **paste-a-URL → agent pre-fills → vendor corrects**
- [ ] Claim + verify flow (DNS TXT / domain email) — PRD spec is good, keep it
- [ ] Verified badge + visible `last_verified_at`
- [ ] Admin review queue + `admin_audit_log` — PRD spec is good, keep it
- [ ] **Answer-Ready Profile**: JSON-LD emission, public structured feed, MCP endpoint
- [ ] Vendor pricing page, terms, refund policy
- [ ] Re-verification SLA job — freshness decay is a real failure mode at 3,415 tools

---

## Phase 2 · Months 3–6 · Signal (the retention engine)

This is the ARPU and the reason anyone stays. Protect it from Phase 1 polish.

**Gate before anything in this phase is sold:** measure the noise floor. Pick 20 buying
queries in one category, run them against ChatGPT and Perplexity five times each with
nothing changed, record the spread (Ch 41 §5.1). If a vendor's citation-rate movement is
smaller than that spread, it is not a result — and reporting it as one would make us
exactly what we are positioning against.

- [ ] Noise floor measured, per slice, and re-measured on every engine model change (E24)
- [ ] `SliceEffect` type cannot be constructed without `noise_floor_pp` (E20)
- [ ] Inside-floor results render as UNDETERMINED, never as a win (E15)
- [ ] Every audit paired against a named competitor — cheapest accuracy win, and it is
      also the metric that sells (Ch 41 §5.1)
- [ ] Per-slice output only; no single aggregate citation rate anywhere in the product
      (Ch 48 §5.3 — the one limit that is fixable)
- [ ] Invalidation register for answer-engine model changes (Ch 38, R21 version triple)

- [ ] Comparison intelligence: matchup counts, win/loss rate, **losing dimension**
- [ ] Shortlist intent: category + company-level demand, anonymised
- [ ] Gap analysis: machine-generated fix list from profile completeness + loss data
- [ ] Cross-engine AI visibility tracking (ChatGPT / Perplexity / Claude / Gemini /
      AI Overviews) against the 100 buying queries per category — **use the real query
      set from platform behaviour, which is the unfair advantage over Profound and Peec**
- [ ] Weekly digest email — the habit loop, and the single highest-retention artifact
- [ ] Analytics on the **write path only**, never the read path
      (`rules/common/data-quality.md` §7)

---

## Phase 3 · Months 6–12 · Amplify (Universal Runtime)

Only capability packages. If it can't be a package with a human approval gate, don't sell it.

- [ ] `audit_ai_visibility`
- [ ] `generate_comparison_asset`
- [ ] `emit_structured_data`
- [ ] Human Authority approval gate on every publish action (spec Ch. 30, §7.6)
- [ ] Cost ceilings per campaign (spec Ch. 35) so fixed pricing stays profitable
- [ ] Attribution + verdicts (spec Ch. 46–47) — churn defence, build it in from day one

---

## Never (keep this list visible)

- Ranking position for sale
- Dimension scores for sale
- Competitor removal or fact suppression
- Slides, ad creative, video production, LinkedIn ghostwriting — refer out, take nothing
- Unlabelled paid placement (FTC Endorsement Guides, and it kills the asset anyway)

---

## Open questions for Rohit

1. Traffic numbers — blocks all pricing
2. Any revenue today on the $19 Pro plan?
3. Real inbound volume: ~3/month or ~30/month?
4. ~~Universal Runtime: spec only, or partially built?~~ **Answered by inspection: spec
   only. No `runtime/`, `contracts/` or `packages/` in the repo.**
5. **The derivation boundary.** When a vendor churns and demands deletion, which derived
   aggregates survive? Ch 37: derivation is one-way and there is no operation that fixes
   it afterwards. This goes in the vendor terms before the first paying customer.
6. Contract-first with adapter v1, or build the runtime properly first? (I recommend
   contract-first — eight weeks to launch vs nine months.)

---

## Review log

_Add outcomes here as phases complete._

- **2026-08-16** — Strategy memo, PRD review and inbound reply drafts written. Phase 0 not
  yet started. No code written by design: the next action is sales, not engineering.
