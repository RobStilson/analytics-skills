---
name: warehouse-navigation
version: 0.1.0
description: "Locate the correct governed source for an analytics question and route to the right reference doc before writing SQL. IF you need to find which table, column, or metric answers a question — THEN invoke this skill and follow the source-tier ladder rather than searching the warehouse freely. Use it whenever a query is about to be written against workforce, HR, or people data, including for questions you think you already know the answer to. DO NOT invoke for pipeline authoring, schema migration, or access troubleshooting."
---

# Warehouse Navigation

## Overview

Given a large warehouse, an agent with free rein will find *a* plausible table
for almost any question. That is the problem. The goal is not to find a table
that works; it is to find the single governed table the organization has agreed
is correct, and to know when none exists.

Free grep across historical queries and notebooks feels like it should solve
this. Empirically it does not move accuracy much — the right precedent is usually
present and still not used, because the bottleneck is *structure*, not *access*.
What works is narrowing the search space to a few curated files before a query is
ever written. That is what this skill does.

## When to Use

| Trigger | Action |
|---|---|
| A confirmed question spec exists and needs data | Invoke; walk the source ladder |
| Two or more tables plausibly answer the question | Invoke; this is the core case |
| The question spans domains (comp × performance × exits) | Invoke; check cross-references before joining |
| You are about to `SELECT *` to see what's in a table | Invoke instead; read the reference doc first |

**DO NOT** invoke when the answer is already covered by a governed metric that
`question-intake` identified — call the metric and stop.

## Process

### 1. Walk the source ladder in order

Descend only when the tier above is genuinely exhausted. Record which tier you
landed on; it goes in the provenance footer.

**Tier 1 — Semantic layer / governed metric definitions.** If a compiled metric
exists for the concept, call it. You get the same number every other surface in
the organization produces, with joins, grain, and filters already baked in.
Always check for named **segments** (canonical population filters) before writing
your own `WHERE` clause — hand-rolling a population filter that already exists as
a governed segment is a dominant wrong-answer mode.

*Do not bail out of this tier early.* Pre-rebutted excuses:

| "I need to fall back because..." | Actually |
|---|---|
| "I need a custom date window" | Time-dimension specs usually handle custom windows |
| "This needs a join" | The metric definition already encapsulates its joins |
| "I need a cut the metric doesn't have" | Check dimensions before assuming; most metrics carry more than they advertise |
| "The metric name doesn't match the question wording" | Search by concept, not by string match |

**Tier 2 — Canonical governed tables, via reference docs.** If no metric covers
the ask, read the domain reference doc (`references/[domain].md`) and use the
tables it names as canonical. The doc tells you grain, scope, required filters,
and gotchas.

**Tier 3 — Raw exploration.** Permitted, but it is the lowest-trust tier and
must be labeled as such in the footer. If you land here, that is a signal the
domain doc has a gap — record it for `correction-harvesting`.

**No tier available** — say so and stop. Do not synthesize an answer from a
table you found by name similarity.

### 2. Disambiguate the entity before joining

Workforce data models carry several entities that are easy to conflate:

| Entity | One row is | Watch for |
|---|---|---|
| **Person / worker** | A human being | The same human can appear under multiple IDs after a rehire |
| **Employment / job record** | A person's tenure in a role | Effective-dated; a promotion creates a new record |
| **Position** | A funded seat in the org | Exists whether or not filled; open reqs are positions with no person |
| **Assignment** | A person-to-position link | A person can hold more than one |

Counting rows in a job-record table and calling it headcount is a classic error.
The number will look reasonable and be wrong by the count of mid-period changes.

### 3. Apply the standard hygiene filters

Before any workforce query, confirm you have handled:

- **Effective dating.** Snapshot tables need an as-of predicate; without one you
  get every historical version of every record. If the table has
  `effective_start` / `effective_end`, filter to the point in time the spec asked for.
- **Worker type.** Contractors, interns, and agency staff are usually in the same
  table as employees and usually excluded from headcount — but not always, and not
  in every metric.
- **Leave status.** People on leave are typically still employed. Whether they
  count depends on the measure. State which you chose.
- **Org hierarchy version.** Organizational rollups are restated. A cut by
  "department" as of today applied to last year's data will not reconcile to what
  was reported last year. Use the as-of hierarchy the spec calls for.
- **Rehires.** Continuous service date and original hire date differ for rehires.
  Tenure calculations that use the wrong one silently misstate the distribution.

### 4. Reconcile before delivering

If a governed dashboard reports a related number, check whether yours reconciles.
When it does not, you have learned something important and must resolve it before
delivering — a second unreconciled official number is worse than no number.

## Rationalizations

| Excuse | Rebuttal |
|---|---|
| "The semantic layer doesn't have exactly this" | Check dimensions and segments before concluding that. Most fallbacks to raw SQL are premature. |
| "I found a table with the right name" | Name similarity is not governance. Two tables can both be called `headcount_daily` and disagree. |
| "I'll grep the query history to see how others did it" | Access to prior work does not reliably improve accuracy. Read the curated reference doc instead. |
| "The reference doc is out of date" | Then use it, flag the gap, and file the correction. Silently abandoning the doc guarantees it stays wrong. |
| "Effective dating is overkill for this question" | It is the difference between 12,400 and 41,000 rows. It is never overkill. |

## Red Flags

- Your row count is suspiciously large — likely missing an as-of filter or a join fan-out
- You are joining on an employee ID without confirming it is unique at the grain you need
- The query returns a number the domain owner would find surprising, and you are not planning to flag that
- You are about to combine two domains without checking their cross-reference notes
- Nothing in your query reflects the hygiene filters listed above

## Verification

- [ ] Source tier is identified and recorded (semantic layer / governed table / raw)
- [ ] Entity grain is confirmed and matches the question spec
- [ ] Effective dating, worker type, and leave status are each explicitly handled
- [ ] Row count was sanity-checked against expected magnitude
- [ ] If Tier 3 was used, the documentation gap was recorded
- [ ] Reconciliation against any governed dashboard was attempted, and differences are explained
