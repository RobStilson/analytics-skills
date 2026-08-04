# Analysis Patterns

The recurring shapes of analytical work, and the specific way each one goes
wrong. Load this when an agent is about to compute a retention curve, explain a
rate change, or compare groups — not for one-off descriptive pulls.

Every SQL block runs against `warehouse/people_analytics.duckdb` as written, and
every figure quoted was executed, not estimated. Examples are workforce data; the
patterns are domain-general.

**Why this file exists:** these five patterns account for a large share of
analytical questions, and each has a characteristic failure that produces a
confident, plausible, wrong answer. An agent that knows the pattern still gets
them wrong, because the failures are not reasoning errors — they are
knowing-what-to-check errors.

| Pattern | Characteristic failure |
|---|---|
| [Cohort construction](#1-cohort-construction) | Cohort defined by something that happens after entry |
| [Retention curves](#2-retention-curves-and-censoring) | Censored observations counted as survivors |
| [Rate decomposition](#3-rate-decomposition-mix-vs-rate) | Mix shift misread as behavior change |
| [Funnel analysis](#4-funnel-and-stage-progression) | Stages measured on different populations |
| [Distributions](#5-distributions-over-means) | A mean reported for a shape that has no middle |

---

## 1. Cohort construction

Everything downstream depends on this. A cohort is a group defined by **when
they entered**, followed forward. Get the entry definition wrong and every
subsequent number inherits the error.

### The rule

**Cohort membership must be determined entirely by information available at
entry.** If a worker's cohort assignment depends on anything that happened
afterward, the cohort is contaminated and comparisons across cohorts are invalid.

### Do

```sql
SELECT year(hire_date) AS cohort_year,
       count(DISTINCT employee_number) AS cohort_size
FROM dim_worker
WHERE worker_type = 'Regular'
GROUP BY 1 ORDER BY 1;
```

Returns 56 / 319 / 670 / 1,057 / 1,522 / 738 for 2021–2026.

### Don't

```sql
-- Cohort defined by an outcome: "employees who completed onboarding"
-- Completion happens AFTER entry, so the cohort excludes early leavers
-- by construction. Retention will look excellent. It is an artifact.
```

### Checks

- [ ] Every cohort criterion is knowable on the entry date
- [ ] Cohort sizes are reported alongside every derived rate
- [ ] Partial cohorts are flagged — 2026 above has 738 people but only half a year of hiring
- [ ] The entry event is the same event for every cohort (hire date, not start date, not offer date)

**Where this bites hardest:** program evaluation. "Participants" is a cohort
defined by an act of enrolment that is itself predicted by the outcome. See
`causal-claim-guardrail`.

---

## 2. Retention curves and censoring

### The failure

Someone hired four months ago has not "survived twelve months." They have not
been *observed* for twelve months. Counting them as a survivor inflates
retention; dropping them silently changes the population. Both are common and
neither is announced by the query.

This is the single most consequential technical error in retention analysis, and
it is invisible — the curve looks fine.

### The rule

**At each time point, the denominator is the number still under observation, not
the original cohort size.** A worker contributes to month 12 only if the data
covers month 12 for them.

### Do

```sql
WITH cohort AS (
  SELECT employee_number, min(hire_date) AS hire_date
  FROM dim_worker
  WHERE worker_type = 'Regular' AND year(hire_date) = 2023
  GROUP BY employee_number
),
obs AS (
  SELECT c.employee_number,
         datediff('month', c.hire_date,
                  COALESCE(s.separation_date, DATE '2026-06-30')) AS months_observed,
         CASE WHEN s.separation_date IS NOT NULL THEN 1 ELSE 0 END AS separated
  FROM cohort c
  LEFT JOIN fct_separation s ON s.employee_number = c.employee_number
)
SELECT m AS month,
       sum(CASE WHEN months_observed >= m THEN 1 ELSE 0 END) AS at_risk,
       sum(CASE WHEN months_observed < m AND separated = 1 THEN 1 ELSE 0 END) AS cumulative_events
FROM obs, (SELECT unnest([0, 6, 12, 18, 24, 30, 36]) AS m)
GROUP BY m ORDER BY m;
```

| Month | At risk | Cumulative events |
|---|---|---|
| 0 | 670 | 0 |
| 12 | 648 | 22 |
| 24 | 609 | 61 |
| 30 | 596 | 74 |
| **36** | **247** | **93** |

**Read the month-36 row.** At-risk collapses from 596 to 247 — not because 349
people left, but because most of the 2023 cohort has not yet been observed for
36 months. Only those hired in the first half of 2023 have reached that mark by
the 2026-06-30 as-of date.

Dividing cumulative events by the original 670 at every month would understate
late-period attrition badly, and the resulting curve would look smooth and
believable.

### Don't

```sql
-- Fixed denominator: every month divided by the original cohort size.
-- Wrong at every point past the observation horizon, and the resulting
-- curve looks smooth and believable.
--   cumulative_events / 670   <- 670 is the cohort size, not the at-risk count
```

### Checks

- [ ] The denominator shrinks over time, and you can explain why
- [ ] The observation horizon is stated ("data through 2026-06-30")
- [ ] Points where at-risk drops sharply are flagged or truncated
- [ ] Curves for different cohorts are compared only over horizons both have reached
- [ ] Competing events are handled — an involuntary exit is not the same event as a voluntary one, and treating them as interchangeable answers a different question than the one asked

**When to escalate to real survival analysis:** if the question involves
covariates, competing risks, or time-varying predictors, a Kaplan-Meier estimate
or Cox model is the right tool and the SQL pattern above is not a substitute.
Say so rather than approximating.

---

## 3. Rate decomposition: mix vs. rate

The most underused pattern here, and the one that most often changes what a
stakeholder concludes.

### The failure

An overall rate moves. Everyone assumes behavior changed. Often the **composition
of the population** changed instead, and no individual group's rate moved at all
— or, worse, the group rates moved *more* than the headline suggests, partially
masked by a mix shift in the opposite direction.

### The rule

**Before explaining why a rate changed, decompose it.** Overall change =
rate effect + mix effect + interaction.

### Do

```sql
WITH pop AS (
  SELECT year(s.snapshot_date) AS yr, s.employee_number,
         CASE WHEN datediff('month', s.hire_date, s.snapshot_date) < 12 THEN '0-1yr'
              WHEN datediff('month', s.hire_date, s.snapshot_date) < 36 THEN '1-3yr'
              ELSE '3yr+' END AS band
  FROM dim_worker_snapshot s
  WHERE s.worker_type = 'Regular'
    AND s.employment_status IN ('Active','On Leave')
    AND s.snapshot_date IN (DATE '2024-06-30', DATE '2025-06-30')
),
sep AS (SELECT employee_number, year(separation_date) AS yr FROM fct_separation),
j AS (
  SELECT p.yr, p.band, count(*) AS n,
         sum(CASE WHEN s.employee_number IS NOT NULL THEN 1 ELSE 0 END) AS events
  FROM pop p
  LEFT JOIN sep s ON s.employee_number = p.employee_number AND s.yr = p.yr
  GROUP BY 1, 2
),
m AS (
  SELECT yr, band, n, events,
         events * 1.0 / n AS rate,
         n * 1.0 / sum(n) OVER (PARTITION BY yr) AS share
  FROM j
),
w AS (
  SELECT a.band, a.share AS s0, a.rate AS r0, b.share AS s1, b.rate AS r1
  FROM m a JOIN m b ON a.band = b.band AND a.yr = 2024 AND b.yr = 2025
)
SELECT round(100 * sum(s0*r0), 2)                                   AS base_2024,
       round(100 * sum(s1*r1), 2)                                   AS actual_2025,
       round(100 * sum(s0*r1) - 100 * sum(s0*r0), 2)                AS rate_effect,
       round(100 * sum(s1*r0) - 100 * sum(s0*r0), 2)                AS mix_effect,
       round(100 * sum(s1*r1) - 100 * sum(s0*r1)
             - 100 * sum(s1*r0) + 100 * sum(s0*r0), 2)              AS interaction
FROM w;
```

**Result — and the story it tells:**

| Component | Value |
|---|---|
| 2024 baseline | 3.58% |
| 2025 actual | 4.74% |
| **Headline change** | **+1.16 pts** |
| Rate effect | **+1.47** |
| Mix effect | **−0.33** |
| Interaction | +0.03 |

The headline says attrition rose 1.2 points. The decomposition says the
underlying rate deterioration was **1.5 points**, partially offset by the
workforce maturing — the 0–1yr share (the highest-attrition band) fell from
57.9% to 47.8%.

**The honest finding is worse than the headline.** Reporting +1.16 without the
decomposition understates the problem, and a stakeholder who later sees hiring
slow down will be surprised when attrition jumps again.

### Checks

- [ ] Components sum to the total change, within rounding
- [ ] The stratifying variable is stated and justified — tenure, function, and level all produce different decompositions of the same headline
- [ ] Group sizes are reported; a mix effect driven by a band of n=9 is noise
- [ ] Small strata are not reported as separate findings — see `uncertainty-reporting`

**Note on the 3yr+ band above:** n=9 in 2024, n=155 in 2025. That band's
contribution is unstable and should be disclosed as such rather than read as a
finding.

---

## 4. Funnel and stage progression

### The failure

Stage counts computed on different populations, then divided by each other. The
conversion rate that results is not a rate of anything.

### The rule

**Every stage must be measured on the same entering cohort, over a window long
enough for that cohort to have reached the final stage.**

### The two questions to answer first

1. **Is the funnel strictly ordered?** If someone can skip a stage or re-enter an
   earlier one, cumulative counts double-count and stage-to-stage rates exceed
   100%.
2. **What is the observation window?** A cohort that entered last week has not
   had time to convert. Including them deflates every downstream rate — the same
   censoring problem as pattern 2, in different clothing.

### Do

- Define the funnel as one cohort, followed forward
- Report both **stage-to-stage** and **cumulative-from-entry** rates; they answer different questions and stakeholders routinely conflate them
- Truncate the cohort to those with a full observation window, and say where you truncated
- Report absolute counts at every stage, not only percentages

### Don't

- Compute each stage as "everyone in that stage this month" — that mixes cohorts
- Report a conversion rate without its denominator
- Present a funnel where stage counts increase at any point without explanation

### Checks

- [ ] Every stage traces to the same entering cohort
- [ ] The observation window is stated and is long enough
- [ ] Stage counts are monotonically non-increasing, or the exception is explained
- [ ] Both rate types are labeled unambiguously

---

## 5. Distributions over means

### The failure

A mean reported for a distribution that has no meaningful middle — bimodal,
heavily skewed, or dominated by a few extreme values. The number is arithmetically
correct and describes nobody.

### The rule

**Look at the distribution before reporting any summary of it.** If the mean and
median differ substantially, the mean is the wrong statistic and the difference
is itself the finding.

### Do

```sql
SELECT count(*)                                                    AS n,
       round(avg(base_salary_local))                               AS mean,
       round(median(base_salary_local))                            AS median,
       round(quantile_cont(base_salary_local, 0.25))               AS p25,
       round(quantile_cont(base_salary_local, 0.75))               AS p75,
       round(stddev(base_salary_local))                            AS sd
FROM fct_compensation
WHERE currency_code = 'USD';
```

Report the shape, not just the center. For compensation specifically, mixing
currencies without conversion produces a mean that is not a salary — note the
`currency_code` filter above, which is doing real work.

**A caveat about this example.** On the workshop warehouse this query returns
n=4,291, mean 111,460, median 111,500 — nearly identical, because the synthetic
salaries were generated from a symmetric distribution. So it does *not*
demonstrate the failure this section describes. Real compensation data is
right-skewed and often multimodal across levels, where the mean-median gap is
large and informative. Use the query pattern; do not use this warehouse to
illustrate skew.

### Checks

- [ ] Mean and median were both computed, and their gap was examined
- [ ] Units are homogeneous — currencies converted, FTE-adjusted or not, stated either way
- [ ] Outliers were inspected rather than silently trimmed; if trimmed, the rule is stated
- [ ] Group comparisons of means account for differing variances and group sizes
- [ ] Percentiles on small groups are suppressed — a p90 on n=7 identifies a person

---

## Composing these

Real questions chain them. "Is retention getting worse?" is patterns 1, 2, and 3
together: build the cohorts, curve them with correct censoring, then decompose
the change to separate behavior from composition.

Order matters. Decomposing before you have correctly censored curves decomposes
an artifact.

## What this file does not cover

Statistical modeling, causal identification, and measurement validity live
elsewhere:

- Causal claims → `causal-claim-guardrail`
- Intervals, suppression, multiplicity → `uncertainty-reporting`
- Construct validity and measurement comparability → `methodologist`

If a question needs a model rather than a pattern, say so. Approximating a Cox
model with a SQL window function is a worse answer than naming the right tool.
