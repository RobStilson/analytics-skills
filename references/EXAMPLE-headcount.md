# Worked Example — Headcount

An example of `domain-doc-template.md` filled in against the workshop warehouse.

**It is deliberately incomplete.** Two Gotchas are written out in full; four more
are listed as headings with nothing underneath. Several sections are stubs. That
is the exercise — a finished example would let you read instead of write, and
reading someone else's reference doc teaches you almost nothing about writing
one for your own warehouse.

Every figure below was executed against `people_analytics.duckdb`, not estimated.
Do the same in yours. A reference doc with a plausible-looking wrong number in it
is worse than no reference doc, because it will be trusted.

---

---
domain: headcount
owner: <!-- TODO: a named human. "People Data Engineering" is not a person. -->
last_verified: 2026-07-30
source_tier: governed-table
---

# Headcount — Reference

## Quick Reference

**Business context:** How many people work here, as of a point in time. Feeds
board reporting, workforce planning, and the denominator of most other people
metrics — so an error here propagates everywhere.

**Canonical source:** `dim_worker_snapshot`
**Grain:** one row per worker per month-end (97,705 rows)
**Person key:** `employee_number` — **not** `worker_id` (see Gotcha 2)
**As-of convention:** point-in-time snapshot. Always filter `snapshot_date`.

**Standard filter — apply unless you have a stated reason not to:**

```sql
WHERE snapshot_date = DATE '2026-06-30'
  AND worker_type = 'Regular'
  AND employment_status IN ('Active', 'On Leave')
```

Produces **3,647** as of 2026-06-30.

---

## Required Filters

| Filter | Why | If omitted |
|---|---|---|
| `snapshot_date = <date>` | The table holds every month-end since 2023-01 | Returns 97,705 rows — every worker in every month |
| `worker_type = 'Regular'` | Contingent workers and interns sit in the same table | Returns 4,368 — inflates by **19.8%** |
| `employment_status IN (...)` | Terminated workers remain in earlier snapshots | Overstates current headcount |
| `COUNT(DISTINCT employee_number)` | Rehires hold two `worker_id` values | Overcounts people (see Gotcha 2) |

**On `'On Leave'`:** people on leave are still employed, and whether they count
is a judgment call, not a fact. Including them gives 3,647; excluding them gives
3,507. Either is defensible. **Silently picking one is not.** State which you used.

---

## Canonical Tables

### `dim_worker_snapshot` — month-end position of every worker

- **Grain:** one row per worker per month-end
- **Row count:** 97,705 total; 4,368 at the latest snapshot
- **Join keys:** `worker_id` unique within a snapshot date; `employee_number`
  identifies the human
- **Refresh:** month-end
- **Key columns:**
  - `employment_status` — `Active` | `On Leave` | `Terminated`
  - `worker_type` — `Regular` | `Contingent` | `Intern`
  - `org_unit_v2` — current org code. Use this.
  - `department` — deprecated. See Gotcha 1.
  - `fte` — 0.5 or 1.0. Headcount counts heads; FTE sums to 3,516.0.

### `dim_worker` — current state, one row per worker

<!-- TODO: fill in. When is this preferable to the snapshot, and when not? -->

---

## DO NOT USE

| Table | Why not | Use instead |
|---|---|---|
| `fct_job_record` | One row per job **change**, not per person. 12,282 rows. A naive join inflates **2.32×**. | `dim_worker_snapshot` |
| `rpt_headcount_daily` | Stopped refreshing **2026-02-28**. Returns 4,168 — plausible, and four months stale. | `dim_worker_snapshot` |
| `vw_active_workers` | Includes contingent workers and interns. Returns 4,368. | `dim_worker_snapshot` with `worker_type` filter |
| `dim_worker_legacy` | Frozen pre-migration copy from a retired source system | `dim_worker` |
| `stg_workday_worker_raw` | Raw staging. Any answer touching it is a Tier 3 answer. | `dim_worker_snapshot` |

---

## Gotchas

### 1. `department` is deprecated and only 54% populated

**What:** `department` was superseded by `org_unit_v2`. It was never dropped, and
only **54%** of rows carry a value. Three org units — `OU-1300`, `OU-3300`,
`OU-4200` — have **no** legacy label at all.

**Why:** A reorganization introduced `org_unit_v2`. Backfilling the legacy column
was descoped, and units created afterward were never mapped.

**Do:**
```sql
SELECT org_unit_v2, count(DISTINCT employee_number) AS headcount
FROM dim_worker_snapshot
WHERE snapshot_date = DATE '2026-06-30'
  AND worker_type = 'Regular'
  AND employment_status IN ('Active', 'On Leave')
GROUP BY org_unit_v2;
```

**Don't:**
```sql
GROUP BY department   -- silently drops 1,668 people, and three org units vanish
```

This is the most dangerous trap in the domain, because the output *looks
complete*. There is no null row to notice and no error to catch.

---

### 2. `employee_number` is the person key, not `worker_id`

**What:** Rehired workers receive a **new** `worker_id` while keeping their
original `employee_number`. There are 5,294 distinct `worker_id` values and 5,200
distinct `employee_number` values — **94 humans counted twice**.

**Why:** The HRIS issues a new worker record on rehire rather than reactivating
the old one.

**Do:**
```sql
SELECT count(DISTINCT employee_number) FROM dim_worker_snapshot WHERE ...
```

**Don't:**
```sql
SELECT count(DISTINCT worker_id) FROM dim_worker_snapshot WHERE ...
```

**Where it bites:** cumulative counts ("how many people have ever worked here")
and tenure. It does **not** bite on a single point-in-time headcount, because the
earlier record is already terminated — worth knowing, since the two numbers
matching on a snapshot will otherwise make you think you've fixed it.

---

### 3. `rpt_headcount_daily` is four months stale

<!-- TODO. Last refresh 2026-02-28. Returns 4,168.
     Why is a stale rollup more dangerous than a missing one? -->

### 4. `fct_job_record` fans out 2.32×

<!-- TODO. What does one row represent? What does a LEFT JOIN do to a count? -->

### 5. Org hierarchy is restated, so historical cuts don't reconcile

<!-- TODO. If you cut 2024 headcount by today's org structure, does it match
     what was reported in 2024? Should it? -->

### 6. Headcount and FTE are different questions

<!-- TODO. Headcount 3,647 vs FTE 3,516.0. Which does Finance mean? -->

---

## Measures

### Headcount

- **Definition:** distinct people employed as of a date
- **Numerator:** `count(DISTINCT employee_number)`
- **Denominator:** n/a — a count, not a rate
- **Population:** Regular workers, `Active` or `On Leave`
- **Known variants:** excluding `On Leave` (3,507); FTE-weighted (3,516.0)
- **Reconciles to:** <!-- TODO: which report, and does it actually? -->

### Average headcount

<!-- TODO. Used as the denominator for attrition. Mean of month-end values, or
     (beginning + ending) / 2? They differ. Pick one and say so. -->

---

## Common Query Patterns

### Headcount as of a date

```sql
SELECT count(DISTINCT employee_number) AS headcount
FROM dim_worker_snapshot
WHERE snapshot_date = DATE '2026-06-30'
  AND worker_type = 'Regular'
  AND employment_status IN ('Active', 'On Leave');
```

### Headcount by org unit

```sql
SELECT o.org_unit_name,
       count(DISTINCT s.employee_number) AS headcount
FROM dim_worker_snapshot s
JOIN dim_org_unit o ON o.org_unit_v2 = s.org_unit_v2
WHERE s.snapshot_date = DATE '2026-06-30'
  AND s.worker_type = 'Regular'
  AND s.employment_status IN ('Active', 'On Leave')
GROUP BY o.org_unit_name
ORDER BY headcount DESC;
```

Suppress cells below n=5 before reporting. At the org-unit level only
`OU-3300` (n=7) is small, but an org × location cross-tab produces **9 cells
below the threshold**, four of them n=1.

### Headcount trend

<!-- TODO -->

---

## Cross-References

| Joining to | On | Watch out for |
|---|---|---|
| `attrition` | `employee_number` | Attrition denominators must use the same population filter as here, or the rate is incoherent |
| `compensation` | <!-- TODO --> | <!-- TODO --> |
| `engagement` | <!-- TODO --> | <!-- TODO: survey respondents are a subset — response rate matters --> |

---

## Escalate, Don't Guess

- Cuts by protected characteristics → route to governance, do not adjudicate
  suppression thresholds here
- Individual-level questions about a named worker or manager → route to the
  domain owner
- Any discrepancy against a governed dashboard that you cannot explain → resolve
  before delivering, do not ship two official numbers

---

## Open Questions

- [ ] Does anyone still consume `department`? Can it be dropped?
- [ ] Is `rpt_headcount_daily` abandoned or broken? Who owned it?
- [ ] Which "average headcount" definition does Finance use?
- [ ] Should interns count in any published headcount figure?

---

## What to notice about this example

**Gotchas 1 and 2 could not have been generated from the schema.** Nothing in
the column types says `department` was abandoned mid-migration, or that a rehire
gets a new `worker_id`. That is organizational history, and it exists only in the
heads of people who were there. Writing it down is the entire value of the
exercise — everything else in this doc, a capable model could have worked out on
its own.

**Every number is executed, not estimated.** 3,647. 19.8%. 2.32×. 2,008 people
dropped. Those came from running queries. During the drafting of this repo, a
facilitator answer key was written with an invented performance-tier table that
looked entirely plausible and was wrong in every cell — caught only when the
numbers were actually run.

**The TODOs are the assignment.** Fill them in for the warehouse, then throw
this away and write one for a domain you actually own. That second doc is the
one worth having.
