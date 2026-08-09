# TODO

Working checklist for the remaining handbook work. **Per-chapter briefs live in
[`docs/handbook/blueprints/phase-3-completion-plan.md`](../docs/handbook/blueprints/phase-3-completion-plan.md)
§6.5 — that document is the source of truth for scope.** This file tracks status only.

**Where things stand:** Chapters 0–41 written, both interludes, five level openers, five level SVGs.
Linter green at 42 chapters. Appendix A at 415 terms. Levels 0–4 complete.

**Next up:** Chapter 42 — *The Case for Harness Evolution*.

---

## Level 5 — Self-Evolving Systems (Ch 42–49)

The final level. A second agent that reads the first one's traces and rewrites its harness. Four
chapters are Full tier (nine figures); four are Core (five figures). Section 14 becomes *Relation to
the Base Runtime* rather than *Relation to AHE*, since the source is the subject rather than a
reference.

- [ ] **42 — The Case for Harness Evolution** · Core
      Why manual harness engineering cannot keep pace with base-model releases `[AHE §1]`. The
      bottleneck is observability, not agent capability. What the ten-iteration result does and does
      not prove.
      *Consumes: Ch 38 §5.1 (a model change invalidates accumulated tuning, so the work is not
      cumulative), Ch 41 §5.7 (the gate).*

- [ ] **43 — Component Observability** · Full
      Seven orthogonal component types as files at fixed mount points `[AHE §3.1]`. Loose coupling,
      one failure pattern to one component class, the deliberately minimal seed, and why a
      pre-fitted seed destroys attribution.
      *Consumes: Ch 39 (the harness workspace already exists as a git repository).*

- [ ] **44 — Experience Observability** · Full
      Ten million trace tokens to ten thousand tokens of evidence `[AHE §3.2]`. Trajectories as a
      navigable file environment, per-task analysis reports, the benchmark-level overview,
      progressive disclosure as a token strategy.
      *Consumes: Ch 34 (retention and always-keep categories), Ch 37 §5.4 (learn from the structural
      partition, not the verbatim one).*

- [ ] **45 — Decision Observability** · Full
      Every edit as a falsifiable contract: failure evidence, root cause, targeted fix, predicted
      fixes, at-risk regressions, constraint level `[AHE §3.3]`. The manifest as the loop's evidence
      ledger.
      *Consumes: Ch 26 §14 (a proposal with no new evidence is refused).*

- [ ] **46 — The Evolve Agent** · Full
      Controllability constraints: workspace-only writes, read-only runs directory, non-deletable
      seed rules `[AHE §3.3]`. Choosing the right constraint level. The anti-pattern of repeatedly
      fixing at the wrong level.
      *Must consume the containment list — see below.*

- [ ] **47 — Attribution, Verdicts, and Rollback** · Core
      Algorithm 1's phase ordering, and why attribution runs *before* distillation `[AHE §3.3]`.
      Intersecting predicted sets with observed deltas. Keep / improve / rollback-and-pivot.
      *Consumes: Ch 40 (automatic rollback is only safe if a measured regression is real),
      Ch 41 (the noise floor), Ch 27 §5.4 (reverting a harness edit restores the code, not the world).*

- [ ] **48 — Limits** · Core
      Effective edits do not stack: three positive single-component gains summing to +11.1 pp yield
      +7.3 pp together `[AHE §4.4.1]`. Fix-prediction ~5× random; regression-prediction ~2×
      `[AHE §4.4.2]`. Designing around a loop that cannot see what it is about to break.
      *Also owns the self-modification governance gap left open in Ch 31 §5.6.*

- [ ] **49 — Continuous Improvement and Governance** · Core
      Running the loop as production infrastructure. Human review gates on the evolution loop
      itself, misuse prevention, harness cleanup, and the honest framing of AHE as a controlled
      prototype `[AHE Limitations]`.

- [ ] Level 5 opener (`docs/handbook/levels/level-5-self-evolving.md`), paired with the existing
      `agentic-harness-engineering-loop.svg`

---

## The containment list — carry this into Ch 46

Eight places where a chapter about something else independently concluded that a specific thing must
sit **outside** what an evolution loop may edit. Each was found the same way: by noticing that an
outcome-based reward would remove a protection. Chapter 46 has to collect them, and Chapter 48 has
to admit the list is not known to be complete.

- [ ] 1. **Memory abstraction** (Ch 12, Ch 20 §5.5) — specific memories perform better and leak
- [ ] 2. **Model id and effort tier** (Ch 13, Ch 28 §4.2) — raise the tier, spend more, score better
- [ ] 3. **The effect tag** (Ch 14) — re-tag effectful as pure and a slow gate disappears; now
         load-bearing for four subsystems, so a mis-tag has four blast radii
- [ ] 4. **Redaction rules** (Ch 16, Ch 37 §5.3)
- [ ] 5. **The verifier** (Ch 28 §7.2) — concretely four things: golden set, check definitions, the
         judge's configuration, and the combiner
- [ ] 6. **The gate policy** (Ch 30 §7.3) — fewer gates complete more tasks
- [ ] 7. **Temporal and concurrency parameters** (Ch 29 §14, Ch 32 §14, Ch 33 §14) — no
         outcome-based reward distinguishes a well-tuned timeout from an overfitted one
- [ ] 8. **Retention and sampling policy, and memory scope** (Ch 34 §14, Ch 37 §14) — a corpus with
         fewer failures produces better-looking aggregates; wider memory sharing genuinely raises
         quality and is a contractual breach

---

## Closing the book (after Level 5)

- [ ] Front matter F.1–F.4
- [ ] Appendices B and C — hand-written (naming conventions; diagram legend)
- [ ] Appendices D, E, G, H, I, J — generated from the chapters via the linter's data model, as
      Appendix A already is
- [ ] Full cross-reference pass: every `Chapter NN §M` reference resolves to a section that exists
- [ ] Recompile the DOCX reading edition
- [ ] Final README, docs index, and reading-map refresh

---

## Standing tasks

- [ ] Keep `tools/check_handbook.py` green — currently 42 chapters, 0 errors, 14 warnings (all
      verified "the agent" uses that legitimately name the Evolve Agent or the agent debugger)
- [ ] Regenerate Appendix A after every batch (`python3 tools/build_glossary.py`)
- [ ] Update the three READMEs and the completion-plan tracker with each batch

## Known deferred items

- [ ] Appendix F (Invariant Checklist) needs a test recipe per invariant, cross-linked to Ch 40's
      three tiers — the tiers now exist, so this is unblocked
- [ ] The blast-radius linter of Ch 39 §4.1 is described as hand-maintained; Ch 39 §15 notes it
      could be derived from trace data. Worth a `[FUT]` cross-reference from Ch 44 when written
