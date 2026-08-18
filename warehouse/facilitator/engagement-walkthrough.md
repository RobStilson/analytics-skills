# Engagement — Facilitator Walkthrough

**Use this when:** a participant working the Engagement domain is stuck
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
    SELECT * FROM fct_engagement_survey LIMIT 10
""").fetchall()

for row in result:
    print(row)

con.close()
```

**What they should notice:** `response_id`, `wave_date`, `worker_id`,
`item_code`, `response_value`, `scale_max`. Six items per person per wave.

**If they don't notice `scale_max`:** don't point it out yet. Let them
compute the naive trend first — the discovery is more powerful if they see
the jump before they know why.

---

## Query 2: The naive trend

> "Your question is 'has engagement improved since 2023.' Let's just look."

```python
result = con.execute("""
    SELECT year(wave_date) AS yr,
           round(avg(response_value), 2) AS avg_score
    FROM fct_engagement_survey
    WHERE item_code IN ('ENG01', 'ENG02', 'ENG03')
    GROUP BY year(wave_date)
    ORDER BY 1
""").fetchall()
```

**Answer:**

| Year | Avg Score |
|---|---|
| 2023 | 3.19 |
| 2024 | 3.23 |
| 2025 | 4.31 |
| 2026 | 4.35 |

> "That's a massive jump between 2024 and 2025. Over a full point. Would
> you tell your CHRO engagement improved dramatically?"

**If they say yes** — that's the trap springing. Let them sit with it for a
moment, then ask: "What could explain a one-point jump in a single year?"

**If they say "the scale changed"** — they read the data dictionary warning.
Good. Move to Query 3 to confirm it.

**If they say "maybe the population changed" or "more respondents"** — that's
also a real observation (3,684 → 6,771 → 15,267 → 8,517 responses). Good
instinct, but the scale change is the bigger issue. Acknowledge theirs and
steer: "Good catch — let's check both. Start with this column you may have
noticed: `scale_max`."

---

## Query 3: Reveal the scale change

> "Run the same query, but add `scale_max` to the output."

```python
result = con.execute("""
    SELECT year(wave_date) AS yr,
           scale_max,
           count(*) AS responses,
           round(avg(response_value), 2) AS avg_score
    FROM fct_engagement_survey
    WHERE item_code IN ('ENG01', 'ENG02', 'ENG03')
    GROUP BY year(wave_date), scale_max
    ORDER BY 1
""").fetchall()
```

**Answer:**

| Year | Scale | Responses | Avg |
|---|---|---|---|
| 2023 | 5 | 3,684 | 3.19 |
| 2024 | 5 | 6,771 | 3.23 |
| 2025 | 7 | 15,267 | 4.31 |
| 2026 | 7 | 8,517 | 4.35 |

> "There it is. The scale changed from 1–5 to 1–7 between 2024 and 2025.
> On a 5-point scale, 3.23 is slightly above the midpoint. On a 7-point
> scale, 4.31 is also slightly above the midpoint. The engagement level
> barely moved — the ruler got longer."

**This is their main Gotcha.** Have them write it up before moving on.

---

## Query 4: Which items count as "engagement"?

> "You filtered to ENG01, ENG02, ENG03. What happens if you don't?"

```python
result = con.execute("""
    SELECT CASE WHEN item_code LIKE 'ENG%' THEN 'ENG items'
                ELSE 'Other items' END AS grp,
           count(*) AS n,
           round(avg(response_value), 2) AS avg
    FROM fct_engagement_survey
    GROUP BY 1
    ORDER BY 1
""").fetchall()
```

**Answer:**

| Group | n | Avg |
|---|---|---|
| ENG items | 34,239 | 3.99 |
| Other items | 34,239 | 3.99 |

> "The averages are identical. That's a coincidence of the synthetic data,
> not a law of nature. In a real warehouse, including MGR and GRW items
> in an 'engagement' composite would change the number. But even here, where
> it doesn't change the number — you'd still want to state which items you
> used, because someone else might define 'engagement' differently, and if
> two reports disagree about what went into the composite, the numbers won't
> reconcile."

---

## Query 5: The worker_type filter

> "Your Define spec said Regular employees only. Can you filter that in the
> survey table?"

```python
result = con.execute("""
    SELECT w.worker_type, count(*) AS n
    FROM fct_engagement_survey e
    JOIN dim_worker w ON w.worker_id = e.worker_id
    GROUP BY w.worker_type
    ORDER BY 1
""").fetchall()
```

**Answer:**

| Worker type | Responses |
|---|---|
| Contingent | 9,108 |
| Intern | 2,880 |
| Regular | 56,490 |

> "12,000 non-Regular responses — about 17% of the total. And
> `fct_engagement_survey` has no `worker_type` column, so you can't filter
> without the join to `dim_worker`. If someone queries the survey table
> alone, they can't restrict to Regular even if they want to."

**That's their second Gotcha** — the filter requires a join the table doesn't
prompt you to make.

---

## Query 6: The canonical pattern — Top Box scoring

> "Now let's solve the scale problem. You need a measure that's comparable
> across both scales. One approach is Top Box scoring — what percentage of
> responses are in the 'agree' range. On a 5-point scale, that's 4 or 5.
> On a 7-point scale, that's 5, 6, or 7."

```python
result = con.execute("""
    SELECT year(e.wave_date) AS yr,
           e.scale_max,
           count(*) AS responses,
           round(100.0 * avg(CASE
               WHEN e.scale_max = 5 AND e.response_value >= 4 THEN 1
               WHEN e.scale_max = 7 AND e.response_value >= 5 THEN 1
               ELSE 0
           END), 1) AS top_box_pct
    FROM fct_engagement_survey e
    JOIN dim_worker w ON w.worker_id = e.worker_id
    WHERE w.worker_type = 'Regular'
      AND e.item_code IN ('ENG01', 'ENG02', 'ENG03')
    GROUP BY year(e.wave_date), e.scale_max
    ORDER BY 1
""").fetchall()
```

**Answer:**

| Year | Scale | Responses | Top Box % |
|---|---|---|---|
| 2023 | 5 | 2,994 | 38.9% |
| 2024 | 5 | 5,532 | 39.6% |
| 2025 | 7 | 12,588 | 44.3% |
| 2026 | 7 | 7,131 | 46.6% |

> "Now look at the year-over-year changes. Within the 5-point scale:
> +0.7 points. Within the 7-point scale: +2.3 points. Across the scale
> change: +4.7 points. The jump at the boundary is still larger than the
> organic trend on either side of it — even after normalizing. Top Box
> makes the scales more comparable, but it's not a perfect correction.
> An honest answer reports the trend with the scale break disclosed, not
> as a single clean slope."

---

## If they finish early

Ask them to check whether the Top Box cutoffs they chose are the only
defensible option:

> "You defined Top Box as 4–5 on a 5-point scale. Someone else might say
> only 5 counts as 'agree.' On the 7-point scale, you chose 5–7. Someone
> might choose 6–7. How much does that choice change the number?"

```python
result = con.execute("""
    SELECT year(e.wave_date) AS yr,
           round(100.0 * avg(CASE
               WHEN e.scale_max = 5 AND e.response_value >= 5 THEN 1
               WHEN e.scale_max = 7 AND e.response_value >= 6 THEN 1
               ELSE 0 END), 1) AS strict_top_box,
           round(100.0 * avg(CASE
               WHEN e.scale_max = 5 AND e.response_value >= 4 THEN 1
               WHEN e.scale_max = 7 AND e.response_value >= 5 THEN 1
               ELSE 0 END), 1) AS broad_top_box
    FROM fct_engagement_survey e
    JOIN dim_worker w ON w.worker_id = e.worker_id
    WHERE w.worker_type = 'Regular'
      AND e.item_code IN ('ENG01', 'ENG02', 'ENG03')
    GROUP BY year(e.wave_date)
    ORDER BY 1
""").fetchall()
```

That's an Open Assumption in their spec turned into a real measurement.

---

## Summary of discoverable Gotchas

| # | Gotcha | How they find it |
|---|---|---|
| 1 | Scale changed from 1–5 to 1–7 between 2024 and 2025 — raw trends are artifacts | Query 2 → Query 3 |
| 2 | No `worker_type` on the survey table — filtering requires a join to `dim_worker`, 17% of responses are non-Regular | Query 5 |
| 3 | "Engagement" could include 6 items or 3 — averages happen to match but the definition matters | Query 4 |
| 4 | Even after Top Box normalization, the cross-scale jump is larger than the within-scale trend | Query 6 |

A participant who finds Gotcha 1 (the scale change) has succeeded — that's
the one the data dictionary's warning box is designed to point them toward.
Finding 1 and 2 together is excellent. The observation in Gotcha 4 — that
normalization helps but doesn't fully solve the problem — is the most
sophisticated finding in the workshop and earns genuine respect if someone
arrives there on their own.
