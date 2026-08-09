# Interlude II — Anatomy of a Bad Week

*After Chapter 41. No template, no figure budget, no new terminology.*

---

Three incidents, one week, one on-call rotation. None of them raised an error.

The point of reading them together is not that a bad week is instructive — every team has them. It
is that the three failures come from three different chapters, have three different owners, and are
told apart by three different instruments. On a Monday morning with a pager going off, knowing
*which* instrument to look at first is most of the work, and the wrong first look costs hours.

Each one is read here through the surfaces Level 4 built. Nothing is introduced that has not already
been.

---

## Monday, 09:40 — the incident with no errors

The page is a liveness burn-rate alert. Runs are not reaching terminal states within their class
SLA, and the fast window has crossed its threshold.

The first instinct is to look at the error rate, which is 0.4% and flat, exactly where it has been
all month. Nothing is failing. Runs are simply not finishing.

The second look is at step duration p95, and there it is: 4.1 seconds at 09:10, 6.8 at 09:25, 19.4
now. Rising steeply, with no corresponding change in error rate, which is the signature Chapter 33
named — saturation announces itself as a latency distribution ten to twenty minutes before it
announces itself as anything else.

The binding-surface gauge says `model_semaphore`. That single word is what makes the next decision
fast, because it rules out the three things the team would otherwise have argued about. It is not the
database, which is sitting at its usual eleven connections. It is not worker count, and adding
workers would make it worse — more contention for the resource that is already the constraint.
It is not the sandbox pool.

What happened is upstream and mundane. A customer's nightly batch fired four hundred runs at 09:00.
Chapter 23's admission control classified them correctly into the bulk class, and Chapter 33's
commitment estimator did what it was built to do — but the model semaphore is a shared resource, and
the bulk class's reservation was sized against an average day rather than against a burst.

The on-call engineer does not fix the sizing at 09:40. They pull the degradation ladder's second
rung: shed at admission, with a reason and a retry-after, which protects the runs already in flight
and refuses new ones honestly. Latency recovers for admitted work within four minutes. The batch
finishes at 12:20 instead of 10:15.

Nobody switched to a cheaper model, and the postmortem records that as a decision rather than an
omission. It would have protected the latency number by spending quality that was never promised,
and the affected runs would have been indistinguishable from every other run afterwards.

**What told them:** step duration p95, then the binding surface. Two numbers, in that order.
**What would not have:** the error rate, which was correct and flat throughout.

---

## Wednesday, 14:05 — the incident that had been running for nine days

There is no page. Someone is preparing a quarterly review and notices that the verdict distribution
for one slice — dependency upgrades — has been sitting six points below its usual band since the
previous Monday.

Nine days. No alert fired, because the aggregate verdict distribution moved by 1.1 points, which is
inside the noise floor. A regression concentrated in one slice is diluted by every other slice until
it disappears, and the alert was watching the aggregate.

The trace store answers the next question in about four minutes. Chapter 34's always-keep categories
mean every failing run from those nine days is on disk in full, and twenty of them are one click from
the dashboard. Filtering the spans to the control-flow axis shows the same shape in every one: the
planner proposing an exact version pin on a task whose entire purpose is widening a range.

From there it is a `git log` on the harness workspace. A three-sentence addition to the planner's
instructions, nine days earlier, correct for the customer it was written for.

The change had passed everything it was shown to. Gate 1 passed, correctly — nothing was outright
broken. Two reviewers approved it, reading three sentences about version pinning while thinking
about the customer who had complained. It never reached gate 2, because the deploy path treated
`prompts/` as configuration and hot-reloaded it.

The revert takes a minute. The interesting work is what follows: querying the runs that carry the
reverted harness hash. That population — Chapter 38's triple, recorded per run — is exactly what
shipped under the bad instruction, and it is four hundred and sixty pull requests, of which
seventy-one are still open. Someone has to look at them.

**What told them:** the per-slice verdict distribution — eventually, by accident, in a quarterly
review. **What would have told them on day one:** the same number, graphed per slice rather than in
aggregate, which is a grouping key on a chart that already existed.

**What made the cleanup possible:** four fields on the run record.

---

## Friday, 22:14 — the incident that was already over

An alert fires that nobody has seen before: `fence.rejected`, count 1.

Chapter 32 argued for this event on the grounds that its absence is the alarm — a fence path that
never fires is usually a fence path that was never wired. Its presence, once, means something else:
a downstream system has just refused a request from a caller holding a stale token.

The trace is unambiguous. Worker A claimed a run at 22:11 with fence 7 and called `deploy_service`.
Its container came under memory pressure at 22:12 and the process stopped for thirty-eight seconds,
renewal thread included. The lease expired at 22:13, the sweeper returned the node at 22:13, worker
B claimed it with fence 8 at 22:14 and called `deploy_service`. A woke up, its HTTP call still in
flight, and its request arrived at the deploy service carrying fence 7 — behind B's, and refused.

Staging was deployed once.

The version compare-and-set would have rejected A's *write* a minute later regardless, and the
database would have been perfectly consistent either way. That was never the thing at risk. What
prevented the second deploy was a monotonic integer travelling with the request to the only party in
the system positioned to compare them.

The on-call engineer's entire action is to write it up. There is nothing to fix — the mechanism did
exactly what it was built for, in the one situation it exists for, at 22:14 on a Friday.

The postmortem's one recommendation is to check the other effectful tools. Three of eleven carry a
fence. Four more could, because the downstream is internal. Four cannot, because the downstream is a
third party with no concept of anyone's lease, and those four are marked as at-least-once with a gate
in front of them, which is the honest position rather than a gap.

**What told them:** an event whose value is that it fires almost never.
**What would have happened without it:** two deploys, eleven minutes of two replica sets fighting
for a port, and an investigation starting from a symptom with no obvious cause.

---

## What the week says

Three incidents. One paged immediately, one ran for nine days without paging, one was over before
the alert arrived.

The pattern underneath is the one Level 3 established and Level 4 instruments: **none of the three
produced an error.** A saturation cliff is a latency distribution. A quality regression is a
distribution shift below an aggregate's resolution. A duplicate deploy is a request that was
correctly refused.

An operations practice built on error rates would have caught none of them. What caught them was a
percentile, a per-slice grouping, and an event that fires almost never — and the third was only
useful because someone had decided in advance that its silence was worth alerting on.

Three further observations, each of which cost somebody a day this week.

**Granularity decides detection.** Monday's incident was visible in an aggregate because it affected
everything. Wednesday's was invisible in the same aggregate because it affected one slice, and the
fix is a grouping key rather than a new metric. The instrument existed both times; only its
resolution differed.

**Recording is cheaper than reconstructing.** Wednesday's cleanup was possible because every run
carried its version triple. Four fields, added in an afternoon eighteen months earlier by someone who
was not thinking about this, are what turned "something shipped badly for nine days" into a query
returning four hundred and sixty rows.

**The best-behaved mechanism is the one you never see.** Friday's fence token had been in production
for a year and had never fired. Under the reasonable-sounding rule that unused code should be
removed, it would have been deleted months ago — and the argument for deleting it would have been
correct about everything except what it was for.

---

**Next:** Chapter 42 — *The Case for Harness Evolution*, opening Level 5. Everything in Level 4 was
built so that a human team can tell whether a change to the system made it better. The question the
final level asks is what happens when the thing making the changes is not a human team.
