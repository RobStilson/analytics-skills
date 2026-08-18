# Attrition — Facilitator Walkthrough

**Use this when:** a participant working the Attrition domain is stuck
during the Build block (1:30–2:15). Walk them through these queries in order.
Each one reveals something they need for their reference doc.

Don't hand them this sheet — walk them through it on their screen, one query
at a time, asking "what do you see?" after each one. The discovery is the
exercise; skipping it by showing them the answer defeats the purpose.

---

## Query 1: What's in the table?

> "Let's start by looking at what you've got."

```python
import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

result = con.execute("""
    SELECT * FROM fct_separation LIMIT 10
""").fetchall()

for row in result:
    print(row)

con.close()
```

**What they should notice:** `worker_id`, `employee_number`, `separation_date`,
`separation_type`, `is_regrettable`, `org_unit_v2`, `worker_type`.

**If they don't notice `worker_type`:** ask "are all of those rows the same
kind of worker?" and let them look at the last few columns.

---

## Query 2: The naive count

> "Okay, your question is 'what was our attrition rate last year.' Step one —
> how many people left in 2025?"

```python
result = con.execute("""
    SELECT count(*) FROM fct_separation
    WHERE year(separation_date) = 2025
""").fetchall()
```

**Answer:** 319

> "That's the numerator. Now — what are you going to divide it by?"

**If they say "headcount"** — good, move to Query 4.

**If they don't hesitate** and immediately start computing a rate — slow them
down. That's the whole trap: the denominator choice is invisible if you don't
stop to think about it.

---

## Query 3: Worker type mix

> "Before we get to the rate — are all 319 of those the same kind of worker?"

```python
result = con.execute("""
    SELECT worker_type, count(*)
    FROM fct_separation
    WHERE year(separation_date) = 2025
    GROUP BY worker_type
    ORDER BY 1
""").fetchall()
```

**Answer:**

| Worker type | Count |
|---|---|
| Contingent | 68 |
| Intern | 10 |
| Regular | 241 |

> "78 of those 319 are contingent workers and interns. Should they be in your
> attrition rate?"

**The teaching moment:** contractors ending assignments and interns completing
internships are structurally different events from Regular employees leaving.
Blending them into one "attrition rate" changes both the numerator and the
denominator — and nobody reading the output can tell which population was
counted.

Have them add `WHERE worker_type = 'Regular'` to their reference doc's
standard filter.

---

## Query 4: The other source table

> "Your data dictionary mentions two tables for attrition. Let's look at the
> other one."

```python
result = con.execute("""
    SELECT * FROM rpt_attrition_monthly
    ORDER BY month DESC
    LIMIT 10
""").fetchall()

for row in result:
    print(row)
```

**What they should notice:** three columns only — `month`, `org_unit_v2`,
`separations`. No denominator. No worker_type. No separation_type.

> "How would you compute a rate from this table?"

**If they say "divide by headcount"** — ask "headcount from where? This table
doesn't have it."

**If they try to join to dim_worker_snapshot** — good instinct, but push:
"Which snapshot date? Beginning of month? End? Average?"

---

## Query 5: Do the two tables agree?

> "Before we worry about the denominator — let's check: do these two tables
> even give you the same numerator?"

```python
result = con.execute("""
    SELECT 'fct_separation' AS source,
           count(*) AS count_2025
    FROM fct_separation
    WHERE year(separation_date) = 2025
    UNION ALL
    SELECT 'rpt_attrition_monthly',
           sum(separations)
    FROM rpt_attrition_monthly
    WHERE year(month) = 2025
""").fetchall()
```

**Answer:** both return 319.

> "They agree. So the rollup table looks validated — it gives the same number.
> But it has no denominator column, no worker_type filter, and no breakdown by
> voluntary vs involuntary. Anyone computing a rate from it has to silently
> pick a denominator from somewhere else, and nobody reading the output can
> tell which one was chosen."

**That's their second Gotcha** (after the worker-type mixing): the rollup
table *looks* right and *invites the wrong workflow*.

---

## Query 6: The denominator spread — the main Gotcha

> "Now the question that actually matters. You have 241 Regular separations
> in 2025. What's the rate?"

```python
result = con.execute("""
    WITH seps AS (
        SELECT count(*) AS n
        FROM fct_separation
        WHERE year(separation_date) = 2025
          AND worker_type = 'Regular'
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
           round(100.0 * seps.n / beg.hc, 1) AS rate_on_beg,
           round(100.0 * seps.n / fin.hc, 1) AS rate_on_end,
           round(100.0 * seps.n / ((beg.hc + fin.hc) / 2.0), 1) AS rate_on_avg
    FROM seps, beg, fin
""").fetchall()
```

**Answer:**

| Separations | Beg HC | End HC | Avg HC | Rate (beg) | Rate (end) | Rate (avg) |
|---|---|---|---|---|---|---|
| 241 | 2,004 | 3,287 | 2,646 | **12.0%** | **7.3%** | **9.1%** |

> "Same 241 separations. Three defensible denominators. Three different rates
> — a **4.7-point spread**. The beginning-of-year rate is nearly double the
> end-of-year rate, and both are arithmetically correct. If someone reports
> '12% attrition' and someone else reports '7% attrition' about the same year,
> neither is wrong — they just chose different denominators and didn't say so."

**This is the main Gotcha.** Have them write it up with the three rates and
the Do/Don't format — "Do: state which denominator. Don't: report a rate
without naming your denominator."

---

## Query 7: Voluntary vs involuntary

> "If you have time — 'attrition rate' could mean all separations, voluntary
> only, or regrettable only. Let's see the breakdown."

```python
result = con.execute("""
    SELECT separation_type, is_regrettable, count(*) AS n
    FROM fct_separation
    WHERE year(separation_date) = 2025
      AND worker_type = 'Regular'
    GROUP BY separation_type, is_regrettable
    ORDER BY 1, 2
""").fetchall()
```

**Answer:**

| Type | Regrettable | Count |
|---|---|---|
| Involuntary | false | 65 |
| Voluntary | false | 121 |
| Voluntary | true | 55 |

> "241 total separations. 176 voluntary. 55 regrettable. A stakeholder asking
> for 'the attrition rate' could mean any of those three numerators, on any of
> the three denominators. That's nine defensible answers to the same question.
> Your reference doc's job is to pick one and say which one it picked."

---

## If they finish early

Point them at the org-unit breakdown to surface the suppression issue:

```python
result = con.execute("""
    SELECT o.org_unit_name, count(*) AS separations
    FROM fct_separation s
    JOIN dim_org_unit o ON o.org_unit_v2 = s.org_unit_v2
    WHERE year(separation_date) = 2025
      AND s.worker_type = 'Regular'
    GROUP BY o.org_unit_name
    ORDER BY 2
""").fetchall()
```

Ask: "Security Engineering had 3 separations. Would you report an attrition
rate for that org unit?" That's the suppression question.

---

## Summary of discoverable Gotchas

| # | Gotcha | How they find it |
|---|---|---|
| 1 | Contingent and intern separations are in the same table | Query 2 → Query 3 |
| 2 | rpt_attrition_monthly has no denominator — invites the wrong workflow | Query 4 → Query 5 |
| 3 | Three denominators produce a 4.7-point spread in the same year's rate | Query 6 |
| 4 | "Attrition rate" could mean 3 numerators × 3 denominators = 9 answers | Query 7 |
| 5 | Small org units below suppression threshold | The "finish early" query |

A participant who finds Gotcha 3 (the denominator spread) has succeeded.
That's the one the entire attrition reference doc is built around. Finding
1 and 3 together is excellent — they've caught both ends of the rate
(numerator and denominator). The nine-answer framing from Query 7 is the
version that tends to make the room go quiet.
