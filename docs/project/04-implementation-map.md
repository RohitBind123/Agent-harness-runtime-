# Current Implementation Map

**Audited:** 2026-09-14, at commit `169142e` on `claude/repo-access-653473`.

**This document maps architectural components to actual files.** It does not
claim something exists because an architecture document says it should. Where a
component has no files, the row says so.

---

## 1. The headline

```
  ARCHITECTURAL COMPONENTS DESCRIBED : ~24
  ARCHITECTURAL COMPONENTS IMPLEMENTED IN THIS REPOSITORY : 0

  PRODUCT SOURCE FILES : 0
  PRODUCT TESTS        : 0
  DATABASE MIGRATIONS  : 0

  WORKING CODE IN THIS REPOSITORY : 5 Python files, all of which
                                    build or lint documentation.
```

Verified by file inventory at the audited commit:

| Extension | Count | What they are |
|---|---|---|
| `.md` | 143 | Handbook chapters, appendices, specification, architecture, product research, this documentation set |
| `.docx` | 10 | Learning documents; one compiled handbook edition |
| `.svg` | 9 | Diagrams |
| `.py` | 5 | Documentation tooling |
| `.pdf` | 1 | The Agentic Harness Engineering research paper |

---

## 2. Component → files → status

| Architectural component | Actual files | Status | Test coverage | Known limitations |
|---|---|---|---|---|
| Source adapters | — | **DESIGNED** | None | No adapter written. Observation shape not fixed |
| Observation log | — | **DESIGNED** | None | No schema, no migration |
| Admission | — | **DESIGNED** | None | Discard-rate metric not defined numerically |
| Entity resolution | — | **DESIGNED** | None | **Disputed between two documents** — see `02-domain-model.md` §5 |
| Extraction | — | **DESIGNED** | None | No predicate vocabulary authored |
| Classify + reconcile | — | **DESIGNED** | None | Depends on the unauthored source-class ladder |
| Claim store | — | **DESIGNED** | None | **Two incompatible Phase 1 schemas specified** |
| Evidence / provenance | — | **DESIGNED** | None | Evidence must outlive the run (EV3); no conflicting position exists in this corpus |
| Contradiction register | — | **DESIGNED** | None | **Disputed**; severity assignment rules unspecified |
| World model | — | **DESIGNED** | None | Projection only; nothing to project from |
| Memory subsystem | — | **DESIGNED** | None | Four-table schema has no migration |
| Retrieval | — | **DESIGNED** | None | Scope-first; no scopes exist |
| Context assembly | — | **DESIGNED** | None | Budget arithmetic unspecified numerically |
| Verification loop (probes) | — | **DESIGNED** | None | No probe registered; `verifiable_by` vocabulary empty |
| Capability layer | — | **DESIGNED** | None | Seven capabilities named; none has a typed signature written |
| Brain MCP server | — | **PROPOSED** | None | Deliberately not built. Caller-identity question unresolved |
| Principal Agent | — | **DESIGNED** | None | Four of its objects are **BLOCKED**, not deferred |
| Agent Runtime | — | **DESIGNED** | None | **None of the 39 invariants is enforced** — there is nothing to enforce them against |
| Environment adapters | — | **DESIGNED** | None | Port signatures specified in Appendix E; no implementation |
| Evaluation | — | **DESIGNED** | None | Noise floor never measured. Without it no effect size has an error term |
| Persistence | — | **DESIGNED** | None | No migration in any repository we can see |
| External-agent integration | — | **PROPOSED** | None | Requires the MCP server |
| **Documentation lint** | `tools/check_handbook.py` | **IMPLEMENTED** | Self-checking; no unit tests | 14 known, accepted warnings |
| **Cross-reference resolver** | `tools/check_xrefs.py` | **IMPLEMENTED** | Self-checking | — |
| **Glossary generator** | `tools/build_glossary.py` | **IMPLEMENTED** | `--check` mode | — |
| **Appendix generator** | `tools/build_appendices.py` | **IMPLEMENTED** | `--check` mode | Appendix F is the one that could be generated and is not |
| **DOCX compiler** | `tools/compile_handbook.py` | **IMPLEMENTED** | Manual | — |
| **Provenance guard** | `tools/check_provenance.py`, `tools/provenance-denylist.txt` | **IMPLEMENTED** | Verified against a deliberate regression | Whole repo incl. `.docx`; the only linter that reaches outside `docs/handbook/` |

### Verification of the "IMPLEMENTED" rows

Run at the audited commit:

```
$ python3 tools/check_handbook.py
51 chapter(s): 0 error(s), 14 warning(s)

$ python3 tools/check_xrefs.py
73 document(s), 51 chapter(s): 0 unresolved reference(s)
```

The 14 warnings are accepted: they are uses of "the agent" that legitimately
name the Evolve Agent or the agent debugger.

---

## 3. Documentation assets, by status

| Asset | Files | State |
|---|---|---|
| Handbook chapters | `docs/handbook/chapters/00..50` (51) | Complete; linted; cross-references resolve |
| Level openers | `docs/handbook/levels/` (6) | Complete |
| Interludes | `docs/handbook/interludes/` (2) | Complete |
| Front matter | `docs/handbook/front-matter/f1..f4` | Complete |
| Appendices | `docs/handbook/appendices/a..j` (10) | Complete; A, D, E, G, H, I, J generated from the chapters |
| Runtime specification | `docs/architecture/universal-runtime-v1.0-...md` | Revision 5; 39 invariants; build order 0–12 |
| Product research | `docs/product/01..06` | Complete as of 2026-09-06. **Exploratory** — see [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) |
| PRD (runtime-controls-OS exploration) | `prd.md` | Complete. **Exploratory**, does not compete with the live direction |
| **PRD (Organizational Brain — the live direction)** | `docs/project/PRD.md` | **Complete.** The project's actual PRD |
| Architecture — Organizational Brain | `docs/architecture/organizational-brain-architecture.md` | Complete |
| Learning documents | `learning-notes/*.docx` (9) | Complete as deliverables |
| Diagrams | `docs/assets/diagrams/*.svg` (9) | Complete |
| Research paper | `docs/research/*.pdf` | External source |

---

## 4. Gaps between design and any implementation

Ordered by how much they block.

| # | Gap | Blocks | Notes |
|---|---|---|---|
| 1 | **The source-class ladder does not exist** | Everything in the Brain | Not an engineering task. Needs a named human. Q2 |
| 2 | ~~The product direction is undecided~~ **RESOLVED 2026-09-14** | — | [ADR-0026](decisions/ADR-0026-product-direction-resolved-prd-is-exploratory.md) — `prd.md` was exploratory; no contest existed |
| 3 | **Two incompatible Phase 1 schemas** | The claim store | `02-domain-model.md` §5, Q7 |
| 4 | **No predicate vocabulary** | Extraction, identity, contradiction | Q5 — roughly twenty predicates from real questions |
| 5 | **No observation shape fixed** | Every adapter | Four properties are unrecoverable if omitted |
| 6 | **No first source chosen** | Phase 1 | Q6 — Jira or Git recommended |
| 7 | **No single-writer invariant profile** | Any deployment that is not a multi-tenant server | Q8 — which of the 39 apply with one writer |
| 8 | **No measured noise floor** | Every confidence number, every effect size | Q11 |
| 9 | **No MCP caller-identity decision** | The MCP server | Q9 — decide before the server, not during |
| 10 | **Two runtime vocabularies** | Module naming, every architectural argument | [ADR-0002](decisions/ADR-0002-specification-vocabulary-is-canonical-for-code.md), Q4 |

---

## 5. What "test coverage" would mean here

There is nothing to cover. Recorded so the column above is not read as an
oversight: when code exists, these are the tests the architecture already names,
and they are *specified* rather than *invented later*.

| Test | What it protects |
|---|---|
| The rebuild test | Replay the observation log; arrive at the same claim store. Run in CI on a seeded log |
| The reconstruction test | Rebuild current claims from version history |
| The tenant-isolation test | A cross-tenant read **raises**. The only way to detect a permission leak, because nothing else produces a signal |
| The deletion-route test | Enumerate every store; a store with no route fails loudly |
| Identity-replay test | A redelivered observation does not produce a second claim |
| Idempotent-reconcile test | Two consecutive passes over an unchanged graph produce an unchanged graph |
| Kill-mid-step test | `kill -9` mid-step; relaunch completes correctly |
| Judgement-cannot-upgrade test | A model judgement may lower a verdict and never raise it |
| Import-boundary tests | The agent package must not import the Brain store; the kernel must not import upward |
| Clock-discipline test | Wall-clock calls banned outside an allowlist; **widen the allowlist per module with a comment, never by relaxing the test** |
| The reviewed extraction sample | A few hundred observations, extracted, reviewed once, committed — then run as a regression test against a measured noise floor |

**And one rule about the suite itself:** retrying is forbidden. A test that
passes on the second attempt is reporting a defect as a success.
