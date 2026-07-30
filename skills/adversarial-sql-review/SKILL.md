---
name: adversarial-sql-review
version: 0.1.0
description: "Aggressively challenge a query and its result before the number reaches a human. IF a query has been written and is about to be run, or a result is about to be reported — THEN invoke this skill and review adversarially against the checklist. Use it for every analytical query without exception, including short ones, because short queries fail silently just as often. DO NOT self-certify: when a separate reviewer sub-agent is available, spawn it rather than reviewing your own work."
---

# Adversarial SQL Review

## Overview

Analytics has no compiler and no test suite. A query with a fan-out join, a wrong
denominator, or a missing hygiene filter runs cleanly and returns a number that
looks exactly like a correct one. The only available guardrail is a deliberate,
hostile pass over the query before anyone acts on it.

Treat this as a blocking gate, not a suggestion. Adversarial review has a real
cost — meaningfully more tokens and noticeably more latency. That cost buys the
only defense there is against silent wrongness.

## When to Use

Invoke before **every** result is reported. There is no size threshold; the
one-line `COUNT(*)` is a frequent offender because nobody reviews it.

Also invoke when:
- A number differs from a prior reported figure and you are about to explain why
- You are combining two domains in a single query
- The result will be forwarded, pasted into a deck, or shown to leadership

**Escalate rather than review** if the query touches restricted or protected-class
data — route to the governance path instead.

## Process

### 1. Spawn a separate reviewer

When sub-agents are available, spawn one and give it the query, the question spec,
and the reference doc. Do not review your own query in the same context: you will
reproduce your own assumptions. Cheaper models make poor reviewers here — most of
the accuracy benefit disappears, for little real speedup.

If no sub-agent is available, at minimum re-read the query against the checklist
with the question spec open, stating each check explicitly rather than scanning.

### 2. Run the checklist

**Grain and fan-out**
- Does one row of the result mean what the spec said it should?
- Does any join multiply rows? Check every join key for uniqueness at the joined grain.
- Effective-dated tables fan out silently. Confirm the as-of predicate exists.

**Population**
- Does the `WHERE` clause reproduce the population from the spec, exactly?
- Was a governed segment available that you replaced with a hand-rolled filter?
- Are contractors, interns, leave-status workers, and rehires handled deliberately?

**Denominators**
- Is the denominator stated in the output, not just used in the calculation?
- For rates over a period: beginning, ending, or average population? Does it match the named measure?
- Is division guarded against zero and null?

**Dates**
- Calendar or fiscal? Complete periods or trailing-N?
- "Last month" means the last *complete* month, not trailing 30 days, unless the spec says otherwise.
- Is the timezone convention explicit, and does the data settle late? Anchor on the
  actual maximum date present, not on "yesterday".

**Nulls**
- What does a null mean in each column used — missing, not applicable, or zero?
- Do nulls silently drop rows via an inner join or a comparison predicate?
- Are nulls being counted in a denominator they should be excluded from, or vice versa?

**Deduplication**
- Are you counting distinct people, or rows?
- Do rehires produce duplicate person records under different IDs?

**Result plausibility**
- Is the magnitude within an order of magnitude of expectation?
- Does the trend break at a point that coincides with a known system migration
  rather than a real event?
- Would the domain owner be surprised? If yes, that is a finding, not a discovery.

### 3. Classify findings

| Severity | Meaning | Action |
|---|---|---|
| **Blocking** | Would change the number or its interpretation | Fix and re-review. Do not deliver. |
| **Advisory** | Would not change the number but weakens confidence | Fix if cheap; otherwise disclose in the footer |
| **Note** | Style, readability, or efficiency | Optional |

### 4. Re-review after fixes

A fix can introduce a new problem — repairing a fan-out by adding `DISTINCT`
often masks the underlying grain error rather than resolving it. Re-run the
checklist on the corrected query. Record the review round in the footer.

## Rationalizations

| Excuse | Rebuttal |
|---|---|
| "It's a simple count, review is overkill" | Simple counts are where missing as-of filters and rehire duplicates live. They are the highest-risk queries precisely because nobody checks them. |
| "The number looks about right" | Looking right is the failure mode, not the pass criterion. Wrong numbers that looked wrong would already have been caught. |
| "I wrote it carefully, so I'll self-certify" | You will reproduce your own assumptions. That is what a separate reviewer is for. |
| "A cheaper model can do the review to save latency" | Most of the accuracy gain disappears when the reviewer is weakened, and the latency saving is small. |
| "I'll flag the caveats instead of fixing it" | Caveats are for things that cannot be fixed. A fixable grain error is not a caveat. |
| "Re-reviewing after the fix is redundant" | The fix is new, unreviewed code. It gets the same treatment as the original. |

## Red Flags

- `SELECT DISTINCT` used to make a count come out right
- A `LEFT JOIN` where the row count grew
- Any percentage in the output whose denominator does not appear anywhere in the output
- A filter that hardcodes a value the reference doc says is deprecated
- The query runs against a table that the reference doc does not mention at all
- You are tempted to explain the result rather than verify it

## Verification

Evidence required before the result may be delivered:

- [ ] A review pass was performed by a reviewer separate from the author, or the
      checklist was walked explicitly item by item
- [ ] Every checklist section returned an explicit finding or an explicit pass
- [ ] All blocking findings are fixed
- [ ] The corrected query was re-reviewed, and the round number is recorded
- [ ] Advisory findings that were not fixed appear in the provenance footer

"Reviewed, looks good" without per-section findings does not count as a review.
