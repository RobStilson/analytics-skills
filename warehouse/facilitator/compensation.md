---
domain: compensation
owner: <!-- TODO: a named human -->
last_verified: 2026-08-11
source_tier: governed-table
---

# Compensation — Reference

## Quick Reference

**Business context:** What the organization pays its workforce — base salary,
bonus targets, and pay grades. Used for comp planning, equity analysis, and
board reporting. Because comp data carries currency codes, any aggregation
across the workforce must account for unit mixing or explicitly restrict to
one currency.

**Canonical source:** `fct_compensation`
**Grain:** one row per worker (5,294 rows; exactly 1:1 with worker_id — no
history, no duplicates)
**Person key:** `worker_id`
**As-of convention:** each row has an `effective_date` — this is the date the
comp record took effect, not when it was loaded. Ranges from 2021-05 to
2026-09.

**Standard filter — apply unless you have a stated reason not to:**

```sql
WHERE c.currency_code = 'USD'
```

Without this filter, three currencies (USD 4,291; EUR 516; SGD 487) are
blended. In this warehouse the averages happen to be nearly identical
(~$111k), which makes the error harder to catch — the number doesn't look
wrong, the methodology is.

---

## Required Filters

| Filter | Why | If omitted |
|---|---|---|
| `currency_code = 'USD'` (or segment by currency) | Three currencies in the table: USD (4,291), EUR (516), SGD (487). Averaging across them is methodologically invalid regardless of whether the numbers happen to be close | Produces a blended average ($111,525) that can't be interpreted in any single currency. In this warehouse the error is ~$65 — invisible, but the practice is indefensible and would fail review |
| `JOIN dim_worker WHERE worker_type = 'Regular'` | Contingent (713) and intern (217) comp records are in the same table | Including them changes the average by ~$1k-2k (Contingent avg $112,519 vs Regular $111,199 in USD). Small numerically, but "average employee salary" should not include contractor rates |

---

## Canonical Tables

### `fct_compensation` — one row per worker

- **Grain:** one row per person, exactly. 5,294 rows = 5,294 distinct worker_ids.
  No comp history — this is current comp only.
- **Row count:** 5,294
- **Join keys:** `worker_id` (unique, joins to `dim_worker` and `dim_worker_snapshot`)
- **Key columns:**
  - `base_salary_local` — DOUBLE, the salary figure. Column name says "local"
    but the values across currencies are suspiciously close (~$111k for USD,
    EUR, and SGD), suggesting they may already be USD-equivalent. Treat
    `currency_code` as the label of record regardless.
  - `currency_code` — `USD` (4,291), `EUR` (516), `SGD` (487)
  - `target_bonus_pct` — DOUBLE, ranges from 0.1 (10%) to 0.3 (30%). "Average
    salary" vs "average total comp" is a $16,646 difference.
  - `pay_grade` — `G4` through `G8`, roughly evenly distributed (~1,050 each)
  - `effective_date` — when this comp took effect

---

## DO NOT USE

| Table | Why not | Use instead |
|---|---|---|
| `dim_compensation_grade` | Empty table — zero rows | `pay_grade` column on `fct_compensation` directly |
| `dim_pay_component` | Empty table — zero rows | Nothing; pay component breakdowns do not exist in this warehouse |

---

## Gotchas

### 1. Three currencies in one column, and the numbers don't look wrong

**What:** `fct_compensation` contains USD, EUR, and SGD records. A naive
`AVG(base_salary_local)` blends all three and produces $111,525. The
per-currency averages are USD $111,460, EUR $111,243, SGD $112,392 — a
spread of only ~$1,100. The blended number looks *fine*, which is exactly
why it's dangerous: no one would question $111,525, but it's an average
across three units that can't be compared.

**Why:** the column name `base_salary_local` implies local-currency values,
but the numbers across currencies are nearly identical — suggesting the
values may already be converted to a common basis. However, `currency_code`
is the field of record, and treating them as interchangeable without
confirming the conversion has happened is a methodology error that would
fail any review.

**Do:**
```sql
-- Segment by currency, or filter to one
SELECT currency_code,
       count(*) AS n,
       round(avg(base_salary_local)) AS avg_salary
FROM fct_compensation
GROUP BY currency_code
ORDER BY 1;
```

**Don't:**
```sql
-- Blends three currencies. Produces ~$111,525 — looks right, isn't defensible.
SELECT round(avg(base_salary_local)) AS avg_salary
FROM fct_compensation;
```

### 2. "Average salary" vs "average total comp" is a $16,646 gap

**What:** `target_bonus_pct` ranges from 10% to 30%. Base salary alone
averages ~$111k (USD). Base plus target bonus averages ~$128k. A stakeholder
asking "what do we pay people" could mean either, and the gap between
them is larger than most org-unit differences.

**Why:** `target_bonus_pct` is on every row but easy to overlook when
answering a salary question. The ambiguity is in the question, not the
data — "average salary" and "average total comp" are both correct answers
to "what do we pay."

**Do:**
```sql
-- State which measure. This is total comp.
SELECT round(avg(base_salary_local * (1 + target_bonus_pct))) AS avg_total_comp
FROM fct_compensation
WHERE currency_code = 'USD';
```

**Don't:**
```sql
-- Answering "what do we pay" with base salary and never mentioning the bonus.
-- The reader can't tell whether the bonus was included or excluded.
SELECT round(avg(base_salary_local)) FROM fct_compensation WHERE currency_code = 'USD';
```

### 3. Small org units fall below suppression thresholds on comp cuts

**What:** Corporate Development has only 3 USD records (7 total across
currencies). Security Engineering has 51 USD. Quality Assurance has 55.
An org-by-org comp breakdown would report an "average salary" for Corporate
Development based on 3 people — meaningless as a statistic and potentially
identifying.

### 4. No worker_type on the comp table

**What:** `fct_compensation` has no `worker_type` column. Filtering to
Regular employees requires joining to `dim_worker`. Without the join, the
930 contingent and intern records are silently included.

---

## Measures

### Average base salary (by currency)

- **Definition:** arithmetic mean of `base_salary_local` for a single currency
- **Numerator:** sum of `base_salary_local`
- **Denominator:** count of records, filtered to one `currency_code`
- **Population:** Regular employees only (join to `dim_worker`)
- **Known variants:**
  - Total comp: `base_salary_local * (1 + target_bonus_pct)` — ~$128k vs
    ~$111k for base alone (USD). State which one.
  - Median vs mean: nearly identical in this warehouse (USD mean $111,460,
    median $111,500) — but report which you used, since comp distributions
    in real warehouses are typically right-skewed
- **Reconciles to:** <!-- TODO: which dashboard or report? -->

---

## Common Query Patterns

### Average base salary by currency (Regular employees)

```sql
SELECT c.currency_code,
       count(*) AS n,
       round(avg(c.base_salary_local)) AS avg_base,
       round(percentile_cont(0.5) WITHIN GROUP (ORDER BY c.base_salary_local)) AS median_base
FROM fct_compensation c
JOIN dim_worker w ON w.worker_id = c.worker_id
WHERE w.worker_type = 'Regular'
GROUP BY c.currency_code
ORDER BY 1;
```

### Average total comp by org unit (Regular, USD only)

```sql
SELECT o.org_unit_name,
       count(*) AS n,
       round(avg(c.base_salary_local)) AS avg_base,
       round(avg(c.base_salary_local * (1 + c.target_bonus_pct))) AS avg_total
FROM fct_compensation c
JOIN dim_worker w ON w.worker_id = c.worker_id
JOIN dim_org_unit o ON o.org_unit_v2 = w.org_unit_v2
WHERE w.worker_type = 'Regular'
  AND c.currency_code = 'USD'
GROUP BY o.org_unit_name
HAVING count(*) >= 5
ORDER BY avg_total DESC;
```

Note the `HAVING count(*) >= 5` — suppresses org units too small to report
a meaningful average. Corporate Development (n=3) is excluded.

---

## Cross-References

| Joining to | On | Watch out for |
|---|---|---|
| Headcount (`dim_worker` / `dim_worker_snapshot`) | `worker_id` | Required for `worker_type = 'Regular'` filter. Comp table is current-state only; snapshot has 42 monthly snapshots — joining without a snapshot date filter fans out 42× |
| Attrition (`fct_separation`) | `worker_id` | Comp records have an `effective_date` that may differ from `separation_date` — a naive join gives comp at last change, not necessarily comp at exit |
| Job (`fct_job_record`) | `worker_id` | Job record has 2.32× the worker count due to transfers — joining without deduplication inflates comp counts |

---

## Escalate, Don't Guess

- Individual-level salary questions about a named person → route to the
  domain owner and HR
- Pay equity analysis by protected class → route to governance; this is a
  legal analysis, not a reporting exercise
- "Are we paying market rate?" → requires external benchmark data not in this
  warehouse

---

## Open Questions

- [ ] Are `base_salary_local` values truly in local currency, or already
      converted to USD? The averages across USD/EUR/SGD are suspiciously close.
- [ ] What determines `pay_grade` assignment? The grades are evenly distributed,
      which is unusual for a real org — is this an artifact of the data generation?
- [ ] Does anyone report median salary rather than mean? Mean and median
      happen to be nearly identical here, but that's not typical of real comp data.
