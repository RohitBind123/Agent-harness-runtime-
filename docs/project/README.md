# Project Knowledge System

**Durable project context. The repository is the source of truth; chat history
is not.**

**Start at [`../../PROJECT_BOOTSTRAP.md`](../../PROJECT_BOOTSTRAP.md).** It is
the session-startup document and it links everything here.

---

## The documents

| # | Document | Answers |
|---|---|---|
| — | [`PROJECT_BOOTSTRAP.md`](../../PROJECT_BOOTSTRAP.md) | Everything, briefly. **Read first** |
| 00 | [North Star](00-north-star.md) | What system, what problem, who for, what wedge, what is *not* the product, what would falsify it |
| 01 | [Architecture Map](01-architecture-map.md) | Every component: purpose, owns, does not own, inputs, outputs, dependencies, invariants, status. Plus where the architecture contradicts itself |
| — | [Decisions](decisions/) | 26 architectural decision records |
| 02 | [Domain Model](02-domain-model.md) | The canonical objects, their fields, lifecycles, owners, invariants — and the objects rejected, with reasons |
| 03 | [Lifecycles and State Machines](03-lifecycles-and-state-machines.md) | Every transition: trigger, preconditions, evidence, reversibility, persistence |
| 04 | [Implementation Map](04-implementation-map.md) | Component → files → status → tests → limitations. **The honest one** |
| 05 | [Development Workflow](05-development-workflow.md) | How work actually gets done here |
| 06 | [Validation Strategy](06-validation-strategy.md) | Using the real engineering workflow as the first live environment, without contaminating the general architecture |
| 07 | [Knowledge System Observability](07-brain-observability.md) | The flight recorder, and how correctness is established without asking the knowledge system |
| 08 | [Build Order](08-build-order.md) | The staged roadmap, with seven proposed changes and the reason for each |
| 09 | [DO NOT ASSUME](09-do-not-assume.md) | The dangerous assumptions register. **Mandatory, and short** |
| 10 | [Open Questions](10-open-questions.md) | 16 questions with blocking status and next experiment, plus 7 that are unsolved |
| 11 | [Architecture Change Log](11-architecture-change-log.md) | Every architectural change, dated, with reason and evidence |
| 12 | [Session Handoff Protocol](12-session-handoff-protocol.md) | The format every session ends with |
| 13 | [Audit — 2026-09-14](13-audit-2026-09-14.md) | The full audit this baseline rests on |
| 14 | [Outside-In Review — 2026-09-14](14-outside-in-review-2026-09-14.md) | The 10 highest-leverage assumptions that could make this wrong, each with a cheap experiment |
| 15 | [Vocabulary](15-vocabulary.md) | Every term retired, renamed, or aligned to the handbook, and why — check here before coining a new name |
| — | [`handoffs/`](handoffs/) | One file per session |

---

## The rules this system runs on

1. **Never silently promote a status.** DESIGNED / IMPLEMENTED / PARTIALLY
   IMPLEMENTED / EXPERIMENTAL / PROPOSED / UNKNOWN. Promoting one is an
   architecture change and goes in the change log.
2. **Never invent a rationale.** If a decision's reasoning is unknown, write
   *"Rationale not yet established."*
3. **Never resolve a contradiction silently.** Record both positions, open a
   question.
4. **Never write "as discussed previously."** Explain the thing. These documents
   are for someone who was not here.
5. **A decision needs a reconsideration trigger.** Without one it is a belief.
6. **Every session ends with a handoff.**

---

## Maintaining this

| Event | Do |
|---|---|
| A decision is made | Add an ADR **and** a change-log entry |
| A question is resolved | Move it to Open Questions §4, link the ADR, log the change |
| Something is implemented | Update the Implementation Map with the file path **and** the change log |
| A new question appears | Add it to Open Questions with its blocking status and next experiment |
| A session ends | Write the handoff |
| A document is found stale | **Fix it.** Nothing here fails when it goes stale — that is the whole risk |

Re-run the audit when the status claims are more than a few weeks old. The
*decisions* and *open questions* do not go stale the same way: they change only
when someone changes them.
