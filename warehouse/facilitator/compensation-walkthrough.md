# Compensation — Facilitator Walkthrough

**Use this when:** a participant working the Compensation domain is stuck
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
    SELECT * FROM fct_compensation LIMIT 10
""").fetchall()

for row in result:
    print(row)

con.close()
```

**What they should notice:** seven columns. `base_salary_local`, a
`currency_code` column, `target_bonus_pct`, `pay_grade`.

**If they don't notice `currency_code`:** ask "what currency are those salary
numbers in?" and let them look.

---

## Query 2: The naive average

> "Okay, your question is 'what's our average salary.' Let's just answer it."

```python
result = con.execute("""
    SELECT round(avg(base_salary_local)) AS avg_salary
    FROM fct_compensation
""").fetchall()
```

**Answer:** $111,525

> "That's a number. Would you send it to your VP? What would you want to know
> first?"

**If they say "which currency"** — they've caught it. Move to Query 3.

**If they don't** — nudge: "Look at the `currency_code` column. What's in it?"

---

## Query 3: Break it out by currency

> "Let's see if that average means what we think it means."

```python
result = con.execute("""
    SELECT currency_code, count(*) AS n,
           round(avg(base_salary_local)) AS avg_salary
    FROM fct_compensation
    GROUP BY currency_code
    ORDER BY 1
""").fetchall()
```

**Answer:**

| Currency | n | Avg |
|---|---|---|
| EUR | 516 | 111,243 |
| SGD | 487 | 112,392 |
| USD | 4,291 | 111,460 |

**The teaching moment:** the averages are nearly identical across three
currencies. This makes the trap *harder* to catch — the blended number
($111,525) looks completely reasonable. But averaging EUR and SGD salaries
with USD salaries is methodologically indefensible regardless of whether the
result happens to be close.

> "The numbers look fine. That's exactly the problem — you'd never question
> $111,525. But if these were truly in local currency, the EUR values should
> be higher (1 EUR > 1 USD) and the SGD values lower (1 SGD < 1 USD). They're
> suspiciously similar. Either the values are already converted, or the data
> generation didn't vary them. Either way, you can't know which from the data
> alone — and 'I averaged three currencies but it happened to work out' won't
> survive a review."

**That's their first Gotcha.** Have them write it up in the Do/Don't format.

---

## Query 4: The second filter they're missing

> "Good — you've handled the currency. What else is in this table that
> shouldn't be in 'average employee salary'?"

```python
result = con.execute("""
    SELECT w.worker_type, count(*) AS n,
           round(avg(c.base_salary_local)) AS avg_salary
    FROM fct_compensation c
    JOIN dim_worker w ON w.worker_id = c.worker_id
    WHERE c.currency_code = 'USD'
    GROUP BY w.worker_type
    ORDER BY 1
""").fetchall()
```

**Answer:**

| Worker type | n | Avg |
|---|---|---|
| Contingent | 578 | 112,519 |
| Intern | 173 | 113,281 |
| Regular | 3,540 | 111,199 |

**Key point:** `fct_compensation` has no `worker_type` column — the filter
requires a join to `dim_worker`. Without the join, you can't filter even if
you know you should. And interns averaging slightly *higher* than regular
employees is suspicious — worth flagging in Open Questions.

---

## Query 5: Base salary vs total comp

> "One more thing. Your stakeholder asked 'what do we pay people.' Is salary
> the same as what we pay?"

```python
result = con.execute("""
    SELECT round(avg(base_salary_local)) AS avg_base,
           round(avg(base_salary_local * (1 + target_bonus_pct))) AS avg_total,
           round(avg(base_salary_local * (1 + target_bonus_pct))) -
           round(avg(base_salary_local)) AS gap
    FROM fct_compensation
    WHERE currency_code = 'USD'
""").fetchall()
```

**Answer:** base ~$111,460, total ~$128,106, gap = **$16,646**

> "That's a $16,000 difference between 'average salary' and 'average total
> comp.' Both are correct answers to 'what do we pay.' Your reference doc
> needs to say which one you're reporting, or the next analyst will pick the
> other one and someone in a meeting will ask why the numbers don't match."

**That's their second Gotcha.** Have them write it up.

---

## Query 6: The canonical pattern

> "Now write the query you'd actually put in the reference doc — the one
> someone copies and runs."

```python
result = con.execute("""
    SELECT c.currency_code,
           count(*) AS n,
           round(avg(c.base_salary_local)) AS avg_base,
           round(percentile_cont(0.5) WITHIN GROUP
                 (ORDER BY c.base_salary_local)) AS median_base
    FROM fct_compensation c
    JOIN dim_worker w ON w.worker_id = c.worker_id
    WHERE w.worker_type = 'Regular'
    GROUP BY c.currency_code
    ORDER BY 1
""").fetchall()
```

**This query has every filter applied:** Regular only (via join), segmented
by currency (not blended), and reports both mean and median.

---

## If they finish early

Point them at the org-unit breakdown:

```python
result = con.execute("""
    SELECT o.org_unit_name,
           count(*) AS n,
           round(avg(c.base_salary_local)) AS avg_base
    FROM fct_compensation c
    JOIN dim_worker w ON w.worker_id = c.worker_id
    JOIN dim_org_unit o ON o.org_unit_v2 = w.org_unit_v2
    WHERE w.worker_type = 'Regular'
      AND c.currency_code = 'USD'
    GROUP BY o.org_unit_name
    ORDER BY avg_base DESC
""").fetchall()
```

Ask: "Corporate Development has 3 people. Would you report their average
salary in a breakdown?" That's the suppression question.

---

## Summary of discoverable Gotchas

| # | Gotcha | How they find it |
|---|---|---|
| 1 | Three currencies blended, result looks fine anyway | Query 2 → Query 3 |
| 2 | Base vs total comp is a $16k gap | Query 5 |
| 3 | No worker_type on the comp table — requires a join to filter | Query 4 |
| 4 | Small org units below suppression threshold | The "finish early" query |

A participant who finds Gotcha 1 has succeeded. Finding 1 and 2 is
excellent. All four is exceptional and probably means they should be
writing skills, not attending a workshop about them.
