# Sample Query Outputs — What You'll See in Your Terminal

This companion to the **data dictionary** shows you what each table
actually looks like when you query it. Every output below was run against
the workshop warehouse using this pattern:

```python
import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

df = con.execute("""
    SELECT * FROM table_name LIMIT 5
""").fetchdf()

print(df.to_string())

con.close()
```

> **Tip:** `.fetchdf()` gives you column names. `.fetchall()` gives you
> bare tuples with no labels. Use `.fetchdf()` — it's one word longer and
> saves you from cross-referencing columns by position.

---

## Your domain's starting table

Pick the one that matches the domain you chose in Block 3.

---

### fct_compensation — Compensation domain

**5,294 rows · one row per worker**

```
      comp_id worker_id effective_date  base_salary_local currency_code  target_bonus_pct pay_grade
0  CMP0000001   W100000     2026-08-02            96900.0           USD             0.127        G5
1  CMP0000002   W100001     2025-04-15           140800.0           USD             0.169        G5
2  CMP0000003   W100002     2024-01-17           130500.0           USD             0.218        G8
3  CMP0000004   W100003     2025-10-23           190500.0           EUR             0.176        G8
4  CMP0000005   W100004     2023-06-08           126600.0           USD             0.145        G7
```

**What to notice:**

| Column | What it means | What could go wrong |
|---|---|---|
| `comp_id` | Row identifier — nothing to do with the person | — |
| `worker_id` | The worker this comp record belongs to. Joins to `dim_worker` | Not the same as `employee_number` — rehires get a new `worker_id` |
| `effective_date` | When this salary took effect — not "current salary" | Dates span 2021–2026. Don't assume the latest row is current without checking |
| `base_salary_local` | Salary in **local currency** | Look at the next column before averaging |
| `currency_code` | USD, EUR, or SGD | **Row 3 is EUR.** A naive `AVG(base_salary_local)` blends dollars and euros into one meaningless number |
| `target_bonus_pct` | Bonus target as a decimal (0.127 = 12.7%) | Not a percentage — don't multiply by 100 unless you're displaying it |
| `pay_grade` | Job level band (G5, G7, G8, etc.) | — |

**The trap:** Three currencies are mixed in one column. The currency
distribution is:

```
  currency_code  count
           USD   4291
           EUR    516
           SGD    487
```

A simple `AVG(base_salary_local)` mixes all three. You need to filter to
one currency or convert first.

---

### fct_separation — Attrition domain

**926 rows · one row per separation event**

```
  worker_id employee_number separation_date separation_type  is_regrettable org_unit_v2 worker_type separation_id
0   W100003         E100003      2026-03-25     Involuntary           False     OU-1100     Regular      SP000001
1   W100006         E100006      2026-03-18       Voluntary           False     OU-2100     Regular      SP000002
2   W100009         E100009      2024-04-28       Voluntary           False     OU-4000     Regular      SP000003
3   W100017         E100017      2025-06-24       Voluntary           False     OU-4200     Regular      SP000004
4   W100026         E100026      2025-02-07       Voluntary           False     OU-4100     Regular      SP000005
```

**What to notice:**

| Column | What it means | What could go wrong |
|---|---|---|
| `worker_id` / `employee_number` | Both are here. Use `employee_number` for counting people | Same rehire issue as everywhere — `worker_id` overcounts |
| `separation_date` | When the person left | Dates range from 2022 through 2026 — filter by year or you're combining four years of separations |
| `separation_type` | `Voluntary` (686) or `Involuntary` (240) | "Attrition rate" usually means voluntary only. Does your stakeholder agree? |
| `is_regrettable` | `true` (231) or `false` (695) | This is the organization's judgment, not a fact. State whether you're filtering on it |
| `worker_type` | `Regular` (717), `Contingent` (177), `Intern` (32) | Contractor departures are in here. Are those "attrition"? Depends who's asking |

**The trap:** This table gives you the numerator (separations). It does
**not** give you the denominator (headcount). To compute an attrition
*rate*, you need to get headcount from `dim_worker_snapshot` — and you
need to decide whose headcount: beginning of period, end of period, or
average. Each gives a different rate from the same separations.

---

### fct_engagement_survey — Engagement domain

**68,478 rows · one row per response per survey item**

```
  response_id  wave_date worker_id item_code  response_value  scale_max
0  RS00000001 2023-04-15   W105183     ENG01               4          5
1  RS00000002 2023-04-15   W105183     ENG02               4          5
2  RS00000003 2023-04-15   W105183     ENG03               5          5
3  RS00000004 2023-04-15   W105183     MGR01               5          5
4  RS00000005 2023-04-15   W105183     MGR02               4          5
```

**What to notice:**

| Column | What it means | What could go wrong |
|---|---|---|
| `response_id` | Row identifier | — |
| `wave_date` | Which survey administration (7 waves, 2023–2026) | — |
| `worker_id` | Who responded | Only respondents appear — people who didn't respond are **absent**, not NULL |
| `item_code` | Which question: `ENG01`, `ENG02`, `ENG03`, `GRW01`, `MGR01`, `MGR02` | Each person has up to 6 rows per wave. Don't count rows and call it "respondents" |
| `response_value` | Their answer — a number | **Look at the next column before trending** |
| `scale_max` | 5 or 7 | This is the trap. See below |

**The trap:** The scale changed between waves:

```
   wave_date  scale_max  responses
  2023-04-15          5       2652
  2023-10-15          5       4716
  2024-04-15          5       5940
  2024-10-15          5       7602
  2025-04-15          7      13716
  2025-10-15          7      16818
  2026-04-15          7      17034
```

A "4 out of 5" in 2024 is 80%. A "4 out of 7" in 2025 is 57%.
Averaging raw `response_value` across waves shows engagement "declining"
even if sentiment didn't change. You need to normalize (divide by
`scale_max`, or convert to percentage) before comparing across time.

---

## Tables everyone will use

These are the shared tables — you'll join to them regardless of domain.

---

### dim_worker_snapshot — the main headcount table

**97,705 rows · one row per worker per month-end · 42 monthly snapshots**

```
  snapshot_date worker_id employee_number worker_type employment_status org_unit_v2 department location_id job_profile_id  hire_date  fte
0    2026-05-31   W100000         E100000      Intern            Active     OU-2000      Sales      LOC007          JP-04 2026-05-04  1.0
1    2026-06-30   W100000         E100000      Intern            Active     OU-2000        NaN      LOC007          JP-04 2026-05-04  1.0
2    2025-01-31   W100001         E100001  Contingent            Active     OU-2200        NaN      LOC003          JP-01 2025-01-15  1.0
3    2025-02-28   W100001         E100001  Contingent            Active     OU-2200  Marketing      LOC003          JP-01 2025-01-15  1.0
4    2025-03-31   W100001         E100001  Contingent            Active     OU-2200  Marketing      LOC003          JP-01 2025-01-15  1.0
```

**What to notice:**

- **The same person appears many times.** Worker W100000 is in rows 0
  *and* 1 — once for May, once for June. Without a `WHERE snapshot_date =`
  filter, you get every worker in every month: 97,705 rows instead of
  ~4,300.
- **`department` has NaN values.** Row 1 has no department. This column
  is only 54% populated — if you `GROUP BY department`, you silently drop
  ~2,000 workers. Use `org_unit_v2` instead.
- **`worker_type` includes Interns and Contingent workers.** Row 0 is an
  Intern. If you're counting "employees," you probably want
  `WHERE worker_type = 'Regular'`.
- **`employee_number` vs `worker_id`:** across the full table there are
  5,273 distinct `worker_id` values but only 5,179 distinct
  `employee_number` values — 94 people counted twice if you use
  `worker_id`.

---

### dim_worker — current-state worker table

**5,294 rows · one row per worker**

```
  worker_id employee_number worker_type org_unit_v2 location_id job_profile_id  hire_date employment_status   department
0   W100000         E100000      Intern     OU-2000      LOC007          JP-04 2026-05-04            Active          NaN
1   W100001         E100001  Contingent     OU-2200      LOC003          JP-01 2025-01-15            Active    Marketing
2   W100002         E100002     Regular     OU-2200      LOC003          JP-07 2023-10-19            Active    Marketing
3   W100003         E100003     Regular     OU-1100      LOC005          JP-16 2025-07-25        Terminated  Engineering
4   W100004         E100004     Regular     OU-4000      LOC002          JP-02 2023-03-10            Active          NaN
```

**What to notice:**

- One row per worker, current state — simpler than `dim_worker_snapshot`
  but no historical view.
- **Terminated workers are in here** (row 3). This is not an "active
  workers" table. Filter on `employment_status` if you need active only.
- Same `department` problem — NaN values in rows 0 and 4.

---

### dim_org_unit — org hierarchy lookup

**15 rows · one row per org unit**

```
  org_unit_v2         org_unit_name     org_group   department
0     OU-1000           Engineering    Technology  Engineering
1     OU-1100  Platform Engineering    Technology  Engineering
2     OU-1200      Data & Analytics    Technology  Engineering
3     OU-1300  Security Engineering    Technology          NaN
4     OU-2000                 Sales  Go-To-Market        Sales
```

**What to notice:**

- This is the lookup table — join on `org_unit_v2` to get human-readable
  org names.
- **`OU-1300` has no `department` mapping** — and neither do `OU-3300`
  (Corporate Development) or `OU-4200` (Quality Assurance). Three org
  units vanish entirely if you filter or group by `department`.

---

### dim_job_profile — job title lookup

**20 rows · one row per job profile**

```
  job_profile_id                 job_title            job_category  job_level
0          JP-01       Software Engineer I  Individual Contributor          1
1          JP-02      Software Engineer II  Individual Contributor          2
2          JP-03  Senior Software Engineer  Individual Contributor          3
3          JP-04            Staff Engineer  Individual Contributor          4
4          JP-05       Engineering Manager          People Manager          4
```

**What to notice:**

- Join on `job_profile_id` to get titles and categories.
- `job_level` is a number, `job_category` is `Individual Contributor` or
  `People Manager`.

---

### dim_location — location lookup

**7 rows · one row per location**

```
  location_id     city state_province country_code    region
0      LOC001  Atlanta             GA           US  Americas
1      LOC002   Denver             CO           US  Americas
2      LOC003   Boston             MA           US  Americas
3      LOC004   Austin             TX           US  Americas
4      LOC005   Dublin            NaN           IE      EMEA
```

**What to notice:**

- Join on `location_id`. Seven locations across three regions.
- `state_province` is NaN for non-US locations (row 4, Dublin).
- If you're filtering by `country_code` to get US-only workers, remember
  that non-US workers in EMEA and APAC have different currencies in the
  compensation table.

---

## Tables that look useful but will mislead you

These are in the warehouse on purpose. They're the kind of table that
exists in every real data environment — not wrong enough to delete, not
right enough to trust.

---

### rpt_headcount_daily — stale rollup

**1,600 rows · one row per org per month**

```
  as_of_date org_unit_v2  headcount
0 2023-01-31     OU-1000         78
1 2023-01-31     OU-1100         58
2 2023-01-31     OU-1200         38
3 2023-01-31     OU-1300          3
4 2023-01-31     OU-2000         69
```

**Why it's dangerous:** The most recent date in this table is
**2026-02-28** — four months stale. It returns 4,168 total headcount,
which is plausible enough to look correct and wrong enough to matter.
Use `dim_worker_snapshot` instead.

---

### rpt_attrition_monthly — no denominator

**270 rows · one row per org per month**

```
       month org_unit_v2  separations
0 2022-07-31     OU-1200            1
1 2022-08-31     OU-1100            1
2 2022-09-30     OU-4100            1
3 2023-02-28     OU-2200            1
4 2023-02-28     OU-4200            1
```

**Why it's dangerous:** Three columns — month, org, and separations.
That's a numerator with no denominator. To compute a rate, you'd have to
silently choose a denominator from another table and hope they use the
same population definition. Use `fct_separation` and get headcount from
`dim_worker_snapshot` yourself.

---

### vw_active_workers — too broad

**4,368 rows · one row per worker**

```
  worker_id employee_number worker_type org_unit_v2 location_id employment_status
0   W100000         E100000      Intern     OU-2000      LOC007            Active
1   W100001         E100001  Contingent     OU-2200      LOC003            Active
2   W100002         E100002     Regular     OU-2200      LOC003            Active
3   W100004         E100004     Regular     OU-4000      LOC002            Active
4   W100005         E100005     Regular     OU-1200      LOC002            Active
```

**Why it's dangerous:** The name says "active workers" but it includes
interns and contingent workers (rows 0 and 1). If you count this table
and call it "headcount," you get 4,368 instead of 3,647 — an
overcount of 19.8%.

---

### fct_job_record — fan-out trap

**12,282 rows · one row per job assignment**

```
  job_record_id worker_id employee_number org_unit_v2 job_profile_id location_id worker_type effective_start effective_end  is_current   change_reason
0     JR0000001   W100000         E100000     OU-2000          JP-04      LOC007      Intern      2026-05-04    9999-12-31        True            Hire
1     JR0000002   W100001         E100001     OU-2200          JP-01      LOC003  Contingent      2025-01-15    2025-10-27       False            Hire
2     JR0000003   W100001         E100001     OU-2200          JP-01      LOC003  Contingent      2025-10-28    9999-12-31        True  Manager Change
3     JR0000004   W100002         E100002     OU-2200          JP-07      LOC003     Regular      2023-10-19    2024-07-03       False            Hire
4     JR0000005   W100002         E100002     OU-2200          JP-07      LOC003     Regular      2024-07-04    2025-08-24       False  Manager Change
```

**Why it's dangerous:** Worker W100001 has two rows (rows 1–2). W100002
has at least two (rows 3–4). Across the table: **12,282 rows for 5,294
workers — a 2.32× inflation.** If you join this table to something and
count rows, your number will be more than double the real answer with no
error message. Use `dim_worker_snapshot` for headcount.

---

## Quick reference: the query template

Save this as `explore.py` in the repo root and change the SQL each time:

```python
import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

df = con.execute("""
    SELECT * FROM dim_worker_snapshot LIMIT 5
""").fetchdf()

print(df.to_string())

con.close()
```

Run from the terminal (**not** VS Code's play button):

**Windows:** `python explore.py`
**Mac/Linux:** `python3 explore.py`
