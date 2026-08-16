# PRD: Vendor Self-Service Onboarding Platform ("List Your Tool")

**Product:** Staquest Vendor Portal  
**Author:** Product Engineering  
**Date:** 2026-08-13  
**Status:** Draft → Ready for Review  
**Stakeholders:** Engineering, Design, Data, Growth  

---

## 1. Context

Staquest is a SaaS tool discovery and comparison platform. Today, vendors discover Staquest organically and email the team requesting inclusion (e.g., Robylon AI outreach). This is:
- **Unscalable** — manual email triage does not scale to 100+ monthly requests.
- **Unstructured** — emails contain free-text descriptions, making data extraction error-prone.
- **Slow** — vendor → email → manual review → data entry → live listing takes 3–7 days.

We are building a **self-service vendor onboarding platform** that lets vendors submit structured data, track review status, and claim/manage existing profiles.

---

## 2. Problem Statement

> Vendors cannot self-serve their way onto Staquest. The team cannot scale manual ingestion. Buyers suffer from stale or missing data.

**Job-to-be-done (Vendor):** "Get my tool in front of high-intent SaaS buyers with accurate positioning, without emailing back and forth."

**Job-to-be-done (Staquest):** "Ingest high-quality, structured tool data at scale with minimal manual intervention."

---

## 3. Goals & Non-Goals

### Goals (P0 — Must Have)
| # | Goal | Success Metric |
|---|------|----------------|
| G1 | Vendors can submit a tool via a structured form | Form completion rate > 60% |
| G2 | Submissions populate the database schema directly | Zero manual copy-paste for standard fields |
| G3 | Internal team can review/approve/reject in an admin panel | Review TAT < 48 hours |
| G4 | Vendors receive automated status emails | Email delivery rate > 99% |
| G5 | Existing unclaimed tools can be claimed by verified owners | Claim success rate > 80% |

### Goals (P1 — Should Have)
| # | Goal | Success Metric |
|---|------|----------------|
| G6 | Vendors can edit their live profile post-approval | Profile edit latency < 5 min to live |
| G7 | Profile completeness score gamifies data quality | Avg completeness > 70% |
| G8 | Basic analytics (views, clicks, comparison appearances) | Dashboard WAU > 30% of claimed vendors |

### Non-Goals
- **Payment processing** — No paid listings in V1.
- **AI content generation** — Out of scope; reserved for Phase 2.
- **Public vendor profiles** — Vendors do not get a public "vendor page"; they manage tool pages only.
- **Multi-user vendor teams** — Single owner per tool in V1.

---

## 4. User Stories

### US-1: First-time Vendor Submission
> As a vendor (e.g., Akash from Robylon), I want to submit my tool via a form so that I do not have to write cold emails.

**Acceptance Criteria:**
- Form is accessible at `/list-your-tool` without authentication.
- Form is a 4-step wizard: Identity → Pricing → Details → Review.
- Required fields block progression with inline validation.
- Submission creates a `tool_submission` record with status `pending_review`.
- Vendor receives a confirmation email with submission ID.

### US-2: Internal Review
> As a Staquest admin, I want to review submissions in a queue so that I can approve high-quality listings and reject spam.

**Acceptance Criteria:**
- Admin panel at `/admin/submissions` lists all submissions sorted by date.
- Each card shows: tool name, category, pricing model, submitter email, submitted at.
- Actions: Approve → creates/updates `tool` record, status → `live`. Reject → status → `rejected`, optional reason.
- Edit → opens inline form to fix data before approval.
- Approved tools appear on Staquest within 5 minutes.

### US-3: Claim Existing Tool
> As a vendor whose tool is already in Staquest, I want to claim ownership so that I can manage my profile.

**Acceptance Criteria:**
- "Claim this tool" CTA on every unclaimed tool page.
- Verification via domain DNS TXT record OR email to `admin@<domain>`.
- On success, create `vendor_account` linked to `tool`, set `tool.is_claimed = true`.
- Claimed tools show "Verified by vendor" badge.

### US-4: Vendor Dashboard
> As a claimed vendor, I want to edit my tool profile so that buyers see accurate, up-to-date information.

**Acceptance Criteria:**
- Dashboard at `/vendor/dashboard` requires authentication.
- Editable fields: description, pricing tiers, features, integrations, screenshots.
- Changes write directly to the production `tool` table (no moderation queue for edits in V1; trust-but-verify).
- Profile completeness score updates in real time.

### US-5: Analytics (P1)
> As a claimed vendor, I want to see how my tool performs on Staquest so that I understand buyer intent.

**Acceptance Criteria:**
- Dashboard shows: profile views (7d, 30d), comparison appearances, click-throughs to website.
- Data refreshes daily.
- Export to CSV (P1 stretch).

---

## 5. Functional Requirements

### 5.1 Submission Form — Field Specification

| Field | Step | Type | Required | Validation | DB Column | Notes |
|-------|------|------|----------|------------|-----------|-------|
| `tool_name` | 1 | string | Yes | 1–80 chars, unique check | `tools.name` | Case-insensitive unique |
| `website_url` | 1 | URL | Yes | Valid HTTPS URL, reachable | `tools.website_url` | Store canonical URL |
| `tagline` | 1 | string | Yes | 10–120 chars | `tools.tagline` | Shown in search cards |
| `description` | 1 | text | No | Max 2000 chars | `tools.description` | Markdown-lite supported |
| `primary_category` | 1 | enum | Yes | From category table | `tools.category_id` | FK to `categories` |
| `tags` | 1 | string[] | No | Max 10 tags, 20 chars each | `tools.tags` | Normalized to lowercase |
| `pricing_model` | 2 | enum | Yes | `per_seat`, `usage_based`, `flat_rate`, `freemium`, `contact_sales` | `tools.pricing_model` | |
| `starting_price_monthly` | 2 | decimal | No | >= 0, 2 decimal places | `tools.starting_price` | NULL if `contact_sales` |
| `has_free_tier` | 2 | boolean | Yes | | `tools.has_free_tier` | |
| `free_tier_limits` | 2 | text | No | Max 500 chars | `tools.free_tier_limits` | Required if `has_free_tier = true` |
| `pricing_page_url` | 2 | URL | No | Valid URL | `tools.pricing_page_url` | |
| `ideal_team_size` | 3 | enum | No | `solo`, `small`, `mid`, `large`, `enterprise` | `tools.ideal_team_size` | |
| `deployment_type` | 3 | enum | No | `cloud`, `self_hosted`, `hybrid` | `tools.deployment_type` | |
| `integrations` | 3 | string[] | No | Max 20 integrations | `tool_integrations` (junction) | FK to `integrations` table |
| `top_competitors` | 3 | string[] | No | Max 3, free text | `tools.top_competitors` | JSON array of strings |
| `submitter_email` | 4 | email | Yes | Valid email | `tool_submissions.submitter_email` | Used for notifications |
| `submitter_name` | 4 | string | Yes | 1–100 chars | `tool_submissions.submitter_name` | |
| `submitter_role` | 4 | string | No | 1–100 chars | `tool_submissions.submitter_role` | |

### 5.2 Submission State Machine

```
[pending_review] ──(approve)──> [live]
      │
      └──(reject)──> [rejected]
      │
      └──(request_info)──> [needs_info] ──(resubmit)──> [pending_review]
```

**State definitions:**
- `pending_review` — Submitted, awaiting admin review.
- `needs_info` — Admin requested clarification; vendor emailed with link to edit.
- `live` — Approved and visible on Staquest.
- `rejected` — Does not meet quality bar; vendor emailed with reason.

### 5.3 Claim Flow State Machine

```
[unclaimed] ──(initiate claim)──> [claim_pending]
      │
      └──(verify DNS/email)──> [claimed]
      │
      └──(reject/fail)──> [unclaimed]
```

---

## 6. Data Model

### 6.1 New Tables

```sql
-- Vendor accounts (authenticated users who own tools)
CREATE TABLE vendor_accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    name            VARCHAR(100),
    avatar_url      TEXT,
    auth_provider   VARCHAR(50) NOT NULL, -- 'email', 'google', 'github'
    auth_provider_id VARCHAR(255),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Tool submissions (the ingestion pipeline)
CREATE TABLE tool_submissions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Submitter info
    submitter_email     VARCHAR(255) NOT NULL,
    submitter_name      VARCHAR(100) NOT NULL,
    submitter_role      VARCHAR(100),
    -- Tool identity
    tool_name           VARCHAR(80) NOT NULL,
    website_url         TEXT NOT NULL,
    tagline             VARCHAR(120) NOT NULL,
    description         TEXT,
    primary_category_id UUID REFERENCES categories(id),
    tags                TEXT[],
    -- Pricing
    pricing_model       VARCHAR(50) NOT NULL,
    starting_price_monthly DECIMAL(10,2),
    has_free_tier       BOOLEAN NOT NULL DEFAULT FALSE,
    free_tier_limits    TEXT,
    pricing_page_url    TEXT,
    -- Details
    ideal_team_size     VARCHAR(50),
    deployment_type     VARCHAR(50),
    top_competitors     JSONB,
    -- Metadata
    status              VARCHAR(50) NOT NULL DEFAULT 'pending_review',
    admin_notes         TEXT,
    reviewed_by         UUID REFERENCES admin_users(id),
    reviewed_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Junction: submissions to integrations (many-to-many)
CREATE TABLE submission_integrations (
    submission_id UUID REFERENCES tool_submissions(id) ON DELETE CASCADE,
    integration_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (submission_id, integration_name)
);

-- Junction: tools to vendor accounts (one tool can have one owner in V1)
CREATE TABLE tool_ownership (
    tool_id         UUID PRIMARY KEY REFERENCES tools(id) ON DELETE CASCADE,
    vendor_id       UUID NOT NULL REFERENCES vendor_accounts(id),
    claimed_at      TIMESTAMPTZ DEFAULT NOW(),
    verification_method VARCHAR(50) NOT NULL -- 'dns', 'email'
);

-- Claim requests (audit trail)
CREATE TABLE tool_claim_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_id         UUID NOT NULL REFERENCES tools(id),
    vendor_id       UUID NOT NULL REFERENCES vendor_accounts(id),
    email_used      VARCHAR(255) NOT NULL,
    verification_method VARCHAR(50) NOT NULL,
    verification_token VARCHAR(255) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, verified, expired, rejected
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Admin audit log (who did what and when)
CREATE TABLE admin_audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id        UUID NOT NULL REFERENCES admin_users(id),
    action          VARCHAR(50) NOT NULL, -- 'approve', 'reject', 'edit', 'request_info'
    entity_type     VARCHAR(50) NOT NULL, -- 'tool_submission', 'tool'
    entity_id       UUID NOT NULL,
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.2 Modified Tables

```sql
-- Add to existing `tools` table
ALTER TABLE tools ADD COLUMN IF NOT EXISTS is_claimed BOOLEAN DEFAULT FALSE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS pricing_model VARCHAR(50);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS starting_price_monthly DECIMAL(10,2);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS has_free_tier BOOLEAN DEFAULT FALSE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS free_tier_limits TEXT;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS ideal_team_size VARCHAR(50);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS deployment_type VARCHAR(50);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS top_competitors JSONB;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS profile_completeness_score INT DEFAULT 0;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMPTZ;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
```

---

## 7. API Specification

### 7.1 Public APIs (No Auth)

#### `POST /api/v1/submissions`
Create a new tool submission.

**Request:**
```json
{
  "submitter_email": "akash@robylon.ai",
  "submitter_name": "Akash G M",
  "submitter_role": "Growth Team",
  "tool_name": "Robylon AI",
  "website_url": "https://www.robylon.ai",
  "tagline": "Omnichannel AI customer support platform for growing and enterprise businesses",
  "description": "Robylon automates customer conversations across voice, WhatsApp, web chat, email, social media, and ticketing...",
  "primary_category_id": "cat-customer-support",
  "tags": ["ai-chatbot", "voice", "automation", "omnichannel"],
  "pricing_model": "per_seat",
  "starting_price_monthly": null,
  "has_free_tier": false,
  "free_tier_limits": null,
  "pricing_page_url": "https://www.robylon.ai/pricing",
  "ideal_team_size": "mid",
  "deployment_type": "cloud",
  "integrations": ["slack", "zendesk", "salesforce"],
  "top_competitors": ["Ada", "Yellow.ai", "Observe.AI"]
}
```

**Response 201:**
```json
{
  "submission_id": "sub_abc123",
  "status": "pending_review",
  "estimated_review_hours": 48,
  "submission_url": "https://staquest.com/submissions/sub_abc123/status"
}
```

**Response 400:**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "tool_name must be unique",
  "field": "tool_name"
}
```

#### `GET /api/v1/submissions/:id`
Public status check (no auth required, but rate-limited).

**Response 200:**
```json
{
  "submission_id": "sub_abc123",
  "tool_name": "Robylon AI",
  "status": "pending_review",
  "submitted_at": "2026-08-13T15:30:00Z",
  "reviewed_at": null,
  "admin_notes": null
}
```

#### `POST /api/v1/tools/:id/claim`
Initiate a claim request.

**Request:**
```json
{
  "email": "akash@robylon.ai",
  "verification_method": "email"
}
```

**Response 202:**
```json
{
  "claim_request_id": "claim_xyz789",
  "status": "pending",
  "message": "Verification email sent to admin@robylon.ai"
}
```

#### `POST /api/v1/claims/:id/verify`
Verify claim via token (from email link or DNS check).

**Request:**
```json
{
  "token": "ver_123456"
}
```

**Response 200:**
```json
{
  "status": "verified",
  "tool_id": "tool_abc",
  "vendor_dashboard_url": "https://staquest.com/vendor/dashboard"
}
```

### 7.2 Authenticated APIs (Vendor)

#### `GET /api/v1/vendor/me`
Get current vendor profile.

#### `GET /api/v1/vendor/tools`
List tools owned by this vendor.

#### `PATCH /api/v1/vendor/tools/:id`
Update tool profile. Writes directly to `tools` table.

**Request:**
```json
{
  "tagline": "Updated tagline",
  "starting_price_monthly": 49.00,
  "has_free_tier": true,
  "free_tier_limits": "Up to 3 agents, 1,000 conversations/mo"
}
```

**Response 200:**
```json
{
  "tool_id": "tool_abc",
  "updated_fields": ["tagline", "starting_price_monthly", "has_free_tier", "free_tier_limits"],
  "profile_completeness_score": 85,
  "live_at": "2026-08-13T16:00:00Z"
}
```

### 7.3 Admin APIs (Protected)

#### `GET /api/v1/admin/submissions`
Query params: `status`, `category_id`, `sort`, `limit`, `offset`.

**Response:**
```json
{
  "data": [...],
  "pagination": { "total": 142, "page": 1, "per_page": 20 }
}
```

#### `POST /api/v1/admin/submissions/:id/approve`
**Request:**
```json
{
  "tool_id": null, // if null, create new tool
  "admin_notes": "Looks good, approved"
}
```

**Side effects:**
- Upsert `tools` record from submission data.
- Set `tool_submissions.status = 'live'`.
- Send approval email to submitter.
- Write to `admin_audit_log`.

#### `POST /api/v1/admin/submissions/:id/reject`
**Request:**
```json
{
  "reason": "Insufficient differentiation from existing tools in category"
}
```

#### `POST /api/v1/admin/submissions/:id/request-info`
**Request:**
```json
{
  "fields_needed": ["starting_price_monthly", "free_tier_limits"],
  "message": "Please clarify your pricing structure."
}
```

---

## 8. UI/UX Specifications

### 8.1 Public Submission Flow (`/list-your-tool`)

**Layout:** Single-page wizard, 4 steps, progress bar at top.

**Step 1 — Identity:**
- Tool name (text, 80 char limit, live uniqueness check)
- Website URL (URL input, validate HTTPS)
- Tagline (text, 120 char limit, character counter)
- Full description (textarea, 2000 char, optional)
- Primary category (dropdown, from `categories` table)
- Tags (multi-select chips + free text)

**Step 2 — Pricing:**
- Pricing model (radio group: per-seat, usage-based, flat-rate, freemium, contact-sales)
- Starting price /mo (number, disabled if contact-sales)
- Free tier? (toggle: Yes/No)
- Free tier limits (text, shown only if Yes)
- Pricing page URL (URL input)

**Step 3 — Details:**
- Ideal team size (dropdown)
- Deployment type (dropdown)
- Integrations (chip multi-select: Slack, GitHub, Notion, Jira, Salesforce, HubSpot, Zendesk, Stripe + custom text)
- Top 3 competitors (3 text inputs)

**Step 4 — Review & Submit:**
- Summary card of all data entered
- Submitter info: name, email, role
- Terms checkbox (required)
- Analytics opt-in checkbox (default checked)
- Submit button

**Post-submit:**
- Success page with submission ID
- "Check status" link
- "Submit another tool" CTA

### 8.2 Admin Review Panel (`/admin/submissions`)

**Layout:** Kanban-style board OR table view (toggle).

**Columns/Groups:**
- Pending Review
- Needs Info
- Live
- Rejected

**Card Content:**
- Tool name + website favicon
- Category badge
- Pricing model + starting price
- Submitter email + submitted at (relative time)
- Action buttons: Approve | Reject | Edit | Request Info

**Detail Drawer (on click):**
- Full submission data in read-only form
- Inline edit mode
- Admin notes textarea
- Action bar with Approve/Reject/Request Info

### 8.3 Vendor Dashboard (`/vendor/dashboard`)

**Layout:** Sidebar nav + main content.

**Nav Items:**
- My Tools
- Analytics (P1)
- Account Settings

**My Tools Page:**
- List of owned tools with completeness score
- "Edit" button opens form
- "Preview" button opens tool page on Staquest

**Tool Edit Form:**
- Same fields as submission form, but pre-filled
- Auto-save indicator
- Completeness score bar (updates on change)
- "Save & Publish" button

---

## 9. Email Specifications

| Trigger | Recipient | Subject | Content |
|---------|-----------|---------|---------|
| Submission created | Submitter | "Your Staquest submission is under review" | Submission ID, estimated review time, status link |
| Approved | Submitter | "Robylon AI is now live on Staquest" | Tool page URL, share CTA, next steps (claim profile) |
| Rejected | Submitter | "Update needed for your Staquest submission" | Reason, edit link (if needs_info), contact email |
| Claim initiated | Domain admin email | "Verify ownership of [Tool] on Staquest" | Verification link, expires in 24h |
| Claim verified | Vendor | "You now manage [Tool] on Staquest" | Dashboard link, getting started tips |
| Weekly digest (P1) | Claimed vendor | "Your Staquest weekly snapshot" | Views, comparisons, CTR |

**Email provider:** Resend (transactional) or Loops (drip + newsletters).

---

## 10. Non-Functional Requirements

### 10.1 Performance
- Form submission API: p95 < 500ms
- Admin panel load: p95 < 1s for 100 submissions
- Tool page update propagation: < 5 minutes from edit to live

### 10.2 Security
- Rate limit `/api/v1/submissions` to 5 req/hour per IP
- Admin APIs behind SSO + role check (`role = 'admin'`)
- Claim verification tokens: cryptographically random, 24h expiry
- All emails validated via MX check on submission
- No PII in logs

### 10.3 Data Quality
- URL validation: must return 200 OK (soft check, non-blocking)
- Duplicate detection: fuzzy match on name + domain
- Category enforcement: free text not allowed for category
- Pricing: if `has_free_tier = true`, `free_tier_limits` is required

### 10.4 Accessibility
- WCAG 2.1 AA compliance
- Keyboard-navigable wizard
- Screen reader announcements for step changes

---

## 11. Analytics & Telemetry

**Events to track (Segment / PostHog):**

| Event | Properties |
|-------|------------|
| `submission_started` | source (direct, footer, tool_page) |
| `submission_step_completed` | step_number, time_on_step |
| `submission_created` | category, pricing_model, has_free_tier |
| `submission_approved` | review_duration_hours |
| `submission_rejected` | reason_category |
| `claim_initiated` | verification_method |
| `claim_verified` | time_to_verify_hours |
| `vendor_profile_edited` | fields_changed_count |
| `vendor_dashboard_viewed` | days_since_last_visit |

**Metrics dashboard:**
- Submissions per week
- Approval rate %
- Avg time to approve
- Top categories submitted
- Claim rate for live tools

---

## 12. Error Handling

| Scenario | UX Behavior | System Behavior |
|----------|-------------|-----------------|
| Duplicate tool name | Inline error: "A tool with this name already exists" | 400, suggest existing tool page |
| Invalid URL | Inline error + field highlight | 400, log validation fail |
| Rate limit exceeded | Toast: "Too many submissions. Try again in an hour." | 429, log IP |
| Admin approves rejected submission | Not possible in UI; button disabled | 409 if API called directly |
| Claim token expired | Error page: "Link expired. Request a new one." | 410, delete old token |
| DNS verification fails | Inline error with instructions | 400, log TXT record attempted |

---

## 13. Open Questions / Decisions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Do we auto-approve submissions from known domains (e.g., YC companies)? | Growth | OPEN |
| 2 | Should rejected submissions be permanently deleted or kept for analysis? | Data | OPEN — recommend soft delete |
| 3 | Do we allow vendors to upload screenshots/logos during submission? | Design | OPEN — recommend P1 to reduce friction |
| 4 | What is the monetization model for claimed profiles? (Free forever? Freemium?) | Product | OPEN — free for V1 |
| 5 | Do we need a public API for vendors to sync data programmatically? | Eng | OPEN — P2 |

---

## 14. Appendix

### A. Competitor Reference
- **G2:** Crowdsourced reviews, paid placements, noisy data.
- **Capterra:** Similar to G2, lead-gen model.
- **Product Hunt:** Launch-focused, not comparison-focused.
- **StackShare:** Tech stack data, no pricing.

**Staquest differentiation:** Structured, verified, honest pricing data. No paid rankings. AI-powered comparisons.

### B. Future Roadmap (Post-V1)
- **Phase 2:** AI listing optimizer (rewrite descriptions, suggest tags)
- **Phase 3:** Competitive intelligence dashboard (category trends, pricing benchmarks)
- **Phase 4:** AI growth tools (SEO content, review campaigns, social proof generation)
- **Phase 5:** Vendor API for programmatic updates

### C. Schema Diagram (Text)

```
vendor_accounts ||--o{ tool_ownership : owns
tool_ownership ||--|| tools : claims
tool_submissions ||--o{ submission_integrations : has
categories ||--o{ tools : categorizes
tools ||--o{ tool_integrations : integrates_with
admin_users ||--o{ admin_audit_log : performs
```

---

**Sign-off:**

| Role | Name | Date | Status |
|------|------|------|--------|
| Product | — | 2026-08-13 | Draft |
| Engineering Lead | — | — | Pending Review |
| Design | — | — | Pending Review |
| Data | — | — | Pending Review |
