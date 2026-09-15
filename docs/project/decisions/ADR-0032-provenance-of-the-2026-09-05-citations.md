# ADR-0032 — The 2026-09-05 citations are attribution, not evidentiary basis

**Status:** ACCEPTED
**Date / context:** 2026-09-15, Architecture Gate 01. **Supersedes
[ADR-0029](ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md)**, whose
text is preserved unchanged.

## Context

[ADR-0029](ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md), written
2026-09-14, recorded as a finding of fact that ten of twenty-eight ADRs cite a
*"knowledge system architecture review, 2026-09-05"* that is not in this
repository. That finding is correct: the document is absent, verified four ways,
and nothing in this ADR disturbs that.

**But ADR-0029 reads the wrong field, and its framing invites a conclusion the
evidence does not support.** The owner directed that the discovery be run to
ground before implementation. Doing so produced a materially different picture.

The ADR template (`README.md` in this directory) requires **two** fields that
answer **two different questions**:

| Field | Question | Weight |
|---|---|---|
| `Date / context` | *When and in what setting was this decided?* | **Attribution.** A meeting, a session, a research pass. Not required to resolve to a file |
| `## Source` | *Which artifact carries the reasoning?* | **Evidence.** This is what [ADR-0025](ADR-0025-no-external-codebase-is-evidence.md) governs |

**The 2026-09-05 string appears in `Date / context`.** ADR-0029 treated a
section-precision citation in an attribution field as though it were the ADRs'
evidentiary basis.

## Decision

**Record that the ten ADRs' 2026-09-05 citations are historical attribution, not
evidentiary basis — every one of the ten names a readable artifact in its
`## Source` field — and narrow the provenance finding to the two ADRs where the
absent document did real work.**

1. **Eight of the ten are ordinarily well-sourced.** Their substance is
   independently present in `docs/architecture/organizational-brain-architecture.md`,
   `docs/product/*.md`, or `learning-notes/Memory Management Architecture.docx`.
   ADR-0006 is the best-sourced of the ten; ADR-0009 never depended on the absent
   document at all, citing 2026-09-02 first.
2. **[ADR-0013](ADR-0013-mcp-is-a-projection-of-the-capability-layer.md) is
   UNVERIFIABLE.** Its named Source does not discuss MCP anywhere. It is the one
   ADR in the ten whose claim has no readable advocate.
3. **[ADR-0005](ADR-0005-the-world-model-is-a-projection-not-a-store.md) is
   PARTIALLY VERIFIED.** The phrase *"world model"* does not occur in its named
   Source. Its *argument* — the handbook's Replay test (Ch9) applied to one
   structure at a time — is readable and strong.
4. **[ADR-0012](ADR-0012-the-agent-reaches-the-brain-only-through-tools.md)
   carries a citation that fails against a readable file.** Its `## Source` cites
   *"(G), §13.1, §13.2"* of a document with sections §0–§10. Its substance is
   present at §6 row 2. The citation is corrected; the decision is untouched.

**This ADR downgrades no status, reverses no decision, and reopens no question.**
It replaces a large vague concern with a small exact one.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Leave ADR-0029 standing** | It is the front-facing record of this project's provenance and it overstates. A reader acting on it would re-litigate ten accepted decisions instead of two |
| **Edit ADR-0029 in place** | The repository's discipline is that a decision found wrong is superseded, not rewritten. The error is worth keeping visible — it is a good example of how a corpus audit goes wrong |
| **Downgrade the ten ADRs' status** | Nothing justifies it. Eight have readable sources carrying their substance; the remaining two have readable reasoning. Provenance precision is not the same as a reversal |
| **Treat `Date / context` and `## Source` as one field** | They answer different questions, and collapsing them is exactly the error being corrected. A decision taken in a meeting whose minutes are lost is not thereby unevidenced |

## Evidence and reasoning

**[FACT — in this repository]** Extracted both fields from all ten ADRs. Nine
name `docs/architecture/organizational-brain-architecture.md`; ADR-0001 and
ADR-0002 additionally name `docs/product/` files; ADR-0009 additionally names
`learning-notes/Memory Management Architecture.docx` §16.5, §37.3.

**[FACT — in this repository]** The named readable source, read end to end (272
lines), carries the substance of eight: §5 principle 3 and §4 row 9 are
ADR-0003's kinds; §3 in full and §5 principle 1 are ADR-0006; §6 row 2 is
ADR-0012; §1 is ADR-0002; §8 row 4 is ADR-0019; §5 principle 10 and §2 property 1
are ADR-0004's consequences; §4 row 5 is ADR-0009.

**[FACT — in this repository]** A mechanical check over every `## Source` field
in all 33 ADRs resolves each cited section against the file named:
**34 citation groups checked, 1 not fully resolved** — ADR-0012's §13.1, §13.2.

**[EVIDENCE]** That check's first run reported five failures. Four were its own
bug: §15, §21, §29, §31 and §38 of the Memory document exist, and the heading
parser required `15 Title` where the source writes `15. Title`. Each was verified
individually before anything was recorded. **A provenance checker is itself an
artifact with a provenance problem**, and this one was wrong on first run.

**[INFERENCE]** ADR-0012's §13.1/§13.2 most likely carried over from the absent
document's numbering, since the same numbers appear in its `Date / context` line.
**Falsifier:** the absent document surfacing with a §13.1 that is not about tool
projection, or a third document with matching sections.

**[FACT — in this repository]** A **circularity** exists and is worth naming: the
readable architecture file cites ADR-0006, ADR-0009, ADR-0023 and ADR-0003, which
in turn name it as their Source. Co-authored corpora do this. It is not
independent corroboration and should not be counted as such.

## Consequences

- **The provenance concern shrinks from ten ADRs to two**, and from a structural
  worry to two documentation items — both triaged DOCUMENTATION-ONLY in
  `19-recovered-architecture-evidence.md` §9.
- **`Date / context` and `## Source` must not be conflated again.** The
  distinction is now stated in this ADR and in doc 19 §1.2.
- **The citation check is mechanical and re-runnable.** It should run before any
  future provenance claim about this corpus.
- **ADR-0029 stays readable and stays wrong**, which is the point of superseding
  rather than editing.
- **Cost, stated honestly:** two ADRs now exist about the same underlying fact,
  and a reader must read both to get the full picture. The alternative was
  erasing a mistake this project made two days ago.

## What would cause us to reconsider

- **The absent document is produced.** Then its §6.1, §5.2, §5.3–5.4, §13.1, §14,
  §17 and §20.2 become checkable, and any ADR whose content disagrees with it is a
  finding. ADR-0029's instruction stands: it enters as a **new dated artifact**,
  never as a recovered 2026-09-05 source.
- **A readable source for ADR-0013's MCP claim is found**, which would move it
  from UNVERIFIABLE to VERIFIED and make this ADR's item 2 obsolete.
- **The mechanical check is shown to be wrong again** — in either direction. It
  has been wrong once already.

## Source

`19-recovered-architecture-evidence.md` §1.2, §2. Verified against all 33 files
in `docs/project/decisions/`, `docs/architecture/organizational-brain-architecture.md`
(read in full), the nine `learning-notes/*.docx`, and `git log --all --diff-filter=D`.

## Related

[ADR-0029](ADR-0029-the-2026-09-05-review-is-not-in-this-repository.md) — superseded by this ·
[ADR-0025](ADR-0025-no-external-codebase-is-evidence.md) — what may be cited as evidence ·
[ADR-0005](ADR-0005-the-world-model-is-a-projection-not-a-store.md), [ADR-0012](ADR-0012-the-agent-reaches-the-brain-only-through-tools.md), [ADR-0013](ADR-0013-mcp-is-a-projection-of-the-capability-layer.md) — the three named above
