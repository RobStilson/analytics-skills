---
domain: attrition
owner: <!-- TODO: a named human, not a team inbox -->
last_verified: 2026-08-06
source_tier: governed-table
---

# Attrition — Reference

## Quick Reference

**Business context:** who is leaving, how fast, and what kind of leaving it is.
Feeds retention strategy, workforce planning, and board reporting. Because
attrition is a *rate*, this domain depends entirely on headcount for its
denominator — an error in headcount propagates here silently.

**Canonical source:** `fct_separation`
**Grain:** one row per separation event (926 rows total; 717 Regular employees)
**Person key:** `employee_number` (in this table, `worker_id` and
`employee_number` are 1:1 — all 926 are unique on both — but use
`employee_number` by default for consistency with `dim_worker_snapshot`, where
they diverge due to rehires)
**As-of convention:** activity window. Attrition is counted over a *period*, not
as of a date.

**Standard filter — apply unless you have a stated reason not to:**

```sql
WHERE worker_type = 'Regular'
```

Without this filter, contingent workers (177) and interns (32) are included.
They separate at different rates for different reasons, and blending them into
an "attrition rate" silently changes both the numerator and the denominator.

---

## Required Filters

| Filter | Why | If omitted |
|---|---|---|
| `worker_type = 'Regular'` | Contingent and intern separations are structurally different events | Inflates the numerator by 209 out of 926 total — a 29% overstatement of Regular attrition events |
| `year(separation_date) = <year>` or a date range | The table spans 2022–2026; an unfiltered count is a cumulative total, not a period rate | Returns 926 instead of a single year's figure |

---

## Canonical Tables

### `fct_separation` — one row per separation event

- **Grain:** one row per person leaving. A person appears at most once.
- **Row count:** 926 total; 717 with `worker_type = 'Regular'`
- **Join keys:** `employee_number` (unique here), `worker_id` (also unique here)
- **Refresh:** as events occur
- **Key columns:**
  - `separation_date` — when they left
  - `separation_type` — `Voluntary` (686) or `Involuntary` (240)
  - `is_regrettable` — `true` (231) or `false` (695). A subset of voluntary
    separations, determined by performance tier
  - `worker_type` — `Regular` (717), `Contingent` (177), `Intern` (32)
  - `org_unit_v2` — current org code at time of separation

---

## DO NOT USE

| Table | Why not | Use instead |
|---|---|---|
| `rpt_attrition_monthly` | Supplies a numerator (`separations`) with **no denominator column at all**. The numbers agree with `fct_separation` (319 = 319 for 2025), but a rate computed from this table requires the analyst to silently pick a denominator — and nobody reading the output can tell which one was chosen. | `fct_separation` for the numerator; `dim_worker_snapshot` for the denominator, stated explicitly |
| `fct_exit_survey` | Empty table — no data. A query against it returns zero rows silently. | Nothing; exit survey data does not exist in this warehouse |

---

## Gotchas

### 1. A rate without a stated denominator is not a rate

**What:** `rpt_attrition_monthly` gives you a numerator and no denominator.
`fct_separation` also gives you only a numerator. Computing an attrition rate
requires joining to `dim_worker_snapshot` for the headcount — and the
denominator you choose changes the answer by **6.2 percentage points**.

**Why:** the three defensible denominator choices for 2025 attrition (319
separations across all worker types — deliberately not filtered to Regular
here, because "what's our attrition rate" as a stakeholder asks it rarely
specifies a worker type, and the point of this Gotcha is the denominator
spread, not the numerator filter) are:

| Denominator | Value | Rate |
|---|---|---|
| Beginning headcount (2024-12-31) | 2,004 | **15.9%** |
| Average headcount | 2,646 | **12.1%** |
| Ending headcount (2025-12-31) | 3,287 | **9.7%** |

A 6.2-point spread from the same 319 events. The ending-headcount rate is
almost half the beginning-headcount rate, and both are arithmetically correct.

**Do:**
```sql
-- State which denominator. This uses average headcount.
WITH seps AS (
  SELECT count(*) AS n
  FROM fct_separation
  WHERE worker_type = 'Regular'
    AND separation_date >= DATE '2025-01-01'
    AND separation_date < DATE '2026-01-01'
),
hc AS (
  SELECT
    (SELECT count(DISTINCT employee_number) FROM dim_worker_snapshot
     WHERE snapshot_date = DATE '2024-12-31' AND worker_type = 'Regular'
       AND employment_status IN ('Active','On Leave'))
    +
    (SELECT count(DISTINCT employee_number) FROM dim_worker_snapshot
     WHERE snapshot_date = DATE '2025-12-31' AND worker_type = 'Regular'
       AND employment_status IN ('Active','On Leave'))
    AS total
)
SELECT round(100.0 * seps.n / (hc.total / 2.0), 1) AS attrition_rate_pct
FROM seps, hc;
```

**Don't:**
```sql
-- No denominator stated. What is this a rate of?
SELECT count(*) * 100.0 / (SELECT count(*) FROM dim_worker_snapshot
  WHERE snapshot_date = DATE '2025-12-31')
FROM fct_separation
WHERE year(separation_date) = 2025;
-- Also: denominator lacks worker_type and employment_status filters,
-- so it's headcount including contingent, on a different basis than
-- the numerator.
```

### 2. Contingent workers are in the same table

**What:** `fct_separation` contains 177 contingent-worker separations and 32
intern separations alongside the 717 Regular ones. No filter is applied by
default.

**Why:** the HRIS records all worker exits in one table regardless of type.

**Do:**
```sql
WHERE worker_type = 'Regular'
```

**Don't:**
```sql
-- No worker_type filter. Numerator now includes contingent/interns,
-- but the denominator (if from dim_worker_snapshot with worker_type='Regular')
-- does not. The rate is incoherent -- numerator and denominator are
-- different populations.
```

### 3. `rpt_attrition_monthly` agrees on the count but invites the wrong workflow

**What:** the table's 2025 sum matches `fct_separation` exactly (319 = 319).
So it looks validated. But it carries no denominator, no `worker_type` filter,
and no `separation_type` breakdown — so any rate computed from it requires
three silent choices the reader can't see.

**Why:** the rollup was built for a dashboard that supplied its own denominator
in the visualization layer. Without that layer, the table is a bare numerator
dressed as a reporting asset.

### 4. One org unit falls below the suppression threshold on attrition cuts

**What:** `OU-1300` (Security Engineering) had 3 separations in 2025. An
attrition rate on n=3 is unstable and, depending on the cross-tab, may require
suppression.

---

## Measures

### Attrition rate (all separations)

- **Definition:** separations in a period divided by the headcount for that period
- **Numerator:** `count(*)` from `fct_separation` where `worker_type = 'Regular'`
  and `separation_date` within the period
- **Denominator:** average of beginning and ending headcount from
  `dim_worker_snapshot` (Regular, Active or On Leave). **State which
  denominator you chose.**
- **Population:** Regular employees only
- **Known variants:**
  - Voluntary attrition: `separation_type = 'Voluntary'` — 2025: 176 of 241
    Regular separations, 6.7% on average HC
  - Involuntary attrition: `separation_type = 'Involuntary'` — 2025: 65 of
    241, 2.5% on average HC
  - Regrettable attrition: `is_regrettable = true` — 2025: 55 of 241, 2.1%
    on average HC. A subset of voluntary, not a separate category.
- **Reconciles to:** <!-- TODO: which dashboard or report? -->

---

## Common Query Patterns

### Attrition rate for a year, with stated denominator

```sql
WITH seps AS (
  SELECT count(*) AS n
  FROM fct_separation
  WHERE worker_type = 'Regular'
    AND separation_date >= DATE '2025-01-01'
    AND separation_date < DATE '2026-01-01'
),
beg AS (
  SELECT count(DISTINCT employee_number) AS hc
  FROM dim_worker_snapshot
  WHERE snapshot_date = DATE '2024-12-31'
    AND worker_type = 'Regular'
    AND employment_status IN ('Active', 'On Leave')
),
fin AS (
  SELECT count(DISTINCT employee_number) AS hc
  FROM dim_worker_snapshot
  WHERE snapshot_date = DATE '2025-12-31'
    AND worker_type = 'Regular'
    AND employment_status IN ('Active', 'On Leave')
)
SELECT seps.n AS separations,
       beg.hc AS beginning_hc,
       fin.hc AS ending_hc,
       round((beg.hc + fin.hc) / 2.0) AS avg_hc,
       round(100.0 * seps.n / ((beg.hc + fin.hc) / 2.0), 1) AS rate_on_avg_hc
FROM seps, beg, fin;
```

### Voluntary attrition rate by org unit

```sql
SELECT o.org_unit_name,
       count(*) AS vol_seps,
       round(100.0 * count(*) / avg_hc.hc, 1) AS vol_rate_pct
FROM fct_separation s
JOIN dim_org_unit o ON o.org_unit_v2 = s.org_unit_v2
CROSS JOIN (
  SELECT round((
    (SELECT count(DISTINCT employee_number) FROM dim_worker_snapshot
     WHERE snapshot_date = DATE '2024-12-31' AND worker_type = 'Regular'
       AND employment_status IN ('Active', 'On Leave'))
    +
    (SELECT count(DISTINCT employee_number) FROM dim_worker_snapshot
     WHERE snapshot_date = DATE '2025-12-31' AND worker_type = 'Regular'
       AND employment_status IN ('Active', 'On Leave'))
  ) / 2.0) AS hc
) avg_hc
WHERE s.worker_type = 'Regular'
  AND s.separation_type = 'Voluntary'
  AND s.separation_date >= DATE '2025-01-01'
  AND s.separation_date < DATE '2026-01-01'
GROUP BY o.org_unit_name, avg_hc.hc
ORDER BY vol_rate_pct DESC;
```

Note: this uses a company-wide denominator for every org unit, not a per-unit
one — a simplification that overstates rates in small units and understates
them in large ones. A per-unit denominator requires joining to a per-unit
headcount snapshot, which is a materially different query.

---

## Cross-References

| Joining to | On | Watch out for |
|---|---|---|
| Headcount (`dim_worker_snapshot`) | `employee_number` | The denominator population **must** use the same `worker_type` and `employment_status` filters as the numerator's scope, or the rate is incoherent — different populations on top and bottom |
| Compensation (`fct_compensation`) | `worker_id` or `employee_number` | Compensation records may have a different effective date than the separation date — joining naively produces the comp at hire, not at exit |
| Engagement (`fct_engagement_survey`) | `worker_id` | Survey responses exist only for people who were surveyed; separated employees may have left before or after the survey wave, so joining requires attention to timing |

---

## Escalate, Don't Guess

- Cuts by protected characteristics → route to governance; suppression
  thresholds are a policy decision, not a statistical one
- Individual-level attrition questions about a named person → route to the
  domain owner
- "Why are people leaving?" → this is a causal question that observational
  separation data cannot answer; route to `causal-claim-guardrail`

---

## Open Questions

- [ ] Which denominator does Finance use for board reporting?
- [ ] Is `is_regrettable` determined by performance tier alone, or does
  manager judgment factor in?
- [ ] Does anyone consume `rpt_attrition_monthly` directly, or is it an
  abandoned dashboard artifact?
- [ ] Should the per-unit rate use a per-unit denominator or a company-wide one?
