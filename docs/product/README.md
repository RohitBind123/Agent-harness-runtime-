# Product research and PRD

Research conducted 2026-09-06, before the PRD was written. The PRD (`/prd.md`) is derived from these
documents, not the other way round.

| # | Document | Brief's outputs covered |
|---|---|---|
| 1 | [`01-architecture-understanding.md`](01-architecture-understanding.md) | Output 1 — architecture understanding report (Part 1) |
| 2 | [`02-feasibility-and-capability-matrices.md`](02-feasibility-and-capability-matrices.md) | Outputs 2, 3, 4 — feasibility report, iOS matrix, macOS matrix (Part 2) |
| 3 | [`03-competitive-landscape-and-comparison.md`](03-competitive-landscape-and-comparison.md) | Outputs 5, 6 — competitive landscape, runtime comparison (Parts 3, 4) |
| 4 | [`04-product-thesis-and-decision.md`](04-product-thesis-and-decision.md) | Outputs 7, 11 — product thesis, business analysis, GO/NO-GO (Parts 5, 6, 10, 11) |
| 5 | [`05-security-threat-model.md`](05-security-threat-model.md) | Output 8 — security and threat analysis (Part 9) |
| 6 | [`06-mvp-and-implementation-strategy.md`](06-mvp-and-implementation-strategy.md) | Outputs 9, 10 — MVP definition, implementation strategy (Parts 7, 8) |
| — | [`/prd.md`](../../prd.md) | Output 12 — the final PRD (Parts 12, 13) |

## The decision, in one line

**GO WITH MAJOR CHANGES.** Build the runtime, but macOS first, iOS as an honest companion, paperwork
rather than "file organisation" as the wedge, developer tooling cut, and reversibility as the product
rather than an implementation detail.

## Follow-on work

Report 1's Finding B was acted on rather than left standing — and corrected in the process: the
original claim that the runtime specification was silent on MCP was wrong, and the correction is
recorded in report 1.

- [`chapters/50-third-party-tool-supply-and-mcp.md`](../handbook/chapters/50-third-party-tool-supply-and-mcp.md) — the derivation.
- Specification **revision 5** — §9.9 MCP Bridge Protocol, invariants I33–I39, build stage 9c.

Neither changes the product decision; see PRD §39.

## Research limitations, disclosed

The network egress proxy blocked `arxiv.org`, `apps.apple.com`, `filexai.com`, `makeitsparkle.co`,
`9to5mac.com`, `indiestack.com` and `www.apple.com`. Claims resting on search-result summaries rather
than fetched primary sources are marked as such throughout.
