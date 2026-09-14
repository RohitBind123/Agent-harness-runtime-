# Session Handoff Protocol

**The rule: the repository is the state. Chat history is not.**

Every session ends by writing a handoff. A session that ends without one has
lost whatever it learned that did not make it into a committed artefact.

---

## 1. Where handoffs go

Append to `docs/project/handoffs/YYYY-MM-DD-<short-slug>.md`. One file per
session. Never edit a previous session's handoff — if it turned out to be wrong,
say so in yours.

If the handoff records a decision, it **also** gets an ADR in
`decisions/` and an entry in `11-architecture-change-log.md`. A handoff is a
record of a session; it is not where decisions live.

---

## 2. The format

Copy this verbatim. All twelve sections are required. **"Nothing" is a complete
and acceptable answer** to any of them — an empty section is information.

```markdown
# Session Handoff — YYYY-MM-DD — <short title>

**Started from commit:** <sha>
**Ended at commit:** <sha>
**Branch:** <branch>

## 1. What I investigated
What I read, what I searched, what I ran. Enough that the next session does
not repeat it.

## 2. What I changed
Files added, modified, deleted. Why each.

## 3. What is now implemented
Only things that IMPLEMENTED is true of. If nothing was implemented, say
"Nothing. This was a <documentation / research / audit> session."

## 4. What remains incomplete
Started and not finished, and what state it is in.

## 5. Tests run
Command and result. If none were run, say so and say why.

## 6. Results
What the tests/tools/checks actually said. Paste the output, not a summary
of it.

## 7. New discoveries
Things now known that were not known before. Include things that turned out
to be FALSE. A disproved assumption is a finding.

## 8. Architectural decisions
Decisions made this session. Each needs an ADR. If none, say "None."

## 9. Architectural concerns
Things that look wrong, fragile, over-built, under-designed, or contradictory
— that I did NOT change. Say why I did not change them.

## 10. Open questions
New questions raised, and existing questions this session moved. Cross-
reference `10-open-questions.md` by number.

## 11. Risks
What could go wrong because of, or in spite of, this session's work.

## 12. Recommended next action
ONE concrete next step, with the reason it is the highest-value one. Not a
list. If the next step is a decision a human must make, say who and what.
```

---

## 3. The rules that make a handoff useful

1. **Write it for someone who was not here.** No "as discussed", no "the
   existing design", no "see the previous session". Explain the thing.
2. **Distinguish what you verified from what you were told.** If you did not run
   it, read it, or check it, say "reported, not verified."
3. **Record disproved assumptions.** The most valuable line in a handoff is
   often *"X turned out not to be true."*
4. **Do not promote a status label to make progress look better.** DESIGNED
   stays DESIGNED until you can point at code.
5. **Say what you did not do, and why.** Scope you deliberately left is
   information. Scope you ran out of time for is different information. Say
   which.
6. **One recommended next action, not a backlog.** A list of ten next steps
   communicates nothing about priority.
7. **Report failures faithfully.** If tests failed, paste the failure. If a step
   was skipped, say it was skipped.

---

## 4. Starting a session

The mirror image, and it is short:

1. Read `PROJECT_BOOTSTRAP.md`.
2. Read `09-do-not-assume.md`.
3. Read the **most recent handoff**, and any earlier one it points at.
4. Check `10-open-questions.md` §1 — if a blocking question is still open, the
   work you are about to do may be blocked by it.
5. Verify the status claims you are about to rely on. **Documents go stale
   silently here** — nothing fails when they do.

---

## 5. What a handoff is not

- **Not a commit message.** Commits say what changed; handoffs say what was
  learned.
- **Not a decision record.** Decisions go in `decisions/`.
- **Not a status report.** Nobody is being reported to. It is a letter to the
  next session.
- **Not a place to be optimistic.** An honest "I could not establish this" is
  worth more than a confident guess, because the next session will act on it.
