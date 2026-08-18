---
domain: engagement
owner: Rob Stilson
last_verified: 2026-08-11
source_tier: governed-table
---

# Engagement — Reference

## Quick Reference

<!-- The routing decision, in under six lines. If an agent reads only this
     section, it should still land on the right table at the right grain. -->

**Business context:** Measures employee engagement through periodic survey
waves; used by People Ops and leadership to track sentiment and identify
drivers of engagement over time.

**Canonical source:** `fct_engagement_survey`
**Grain:** one row per response per item (a person with 6 items in one wave = 6 rows)
**Person key:** `worker_id`
**As-of convention:** survey waves — each wave has a `wave_date`; this is an
activity window (the period the survey was fielded), not a point-in-time snapshot

**Standard filter — apply unless you have a stated reason not to:**

```sql
WHERE item_code IN ('ENG01', 'ENG02', 'ENG03')
```

---

## Required Filters

| Filter | Why | If omitted |
|---|---|---|
| `item_code IN ('ENG01','ENG02','ENG03')` | The table contains 6 items including manager and growth items that are not part of the engagement composite | Blends engagement with unrelated constructs; hard to catch because averages are similar (~3.98–4.0 across all items) |
| `JOIN dim_worker WHERE worker_type = 'Regular'` | The survey table includes contingent (9,108) and intern (2,880) responses alongside Regular (56,490) | Inflates the respondent count by ~17% with populations that may have structurally different engagement patterns |

---

## Gotchas

<!-- ⚠ THE MOST IMPORTANT SECTION IN THIS DOCUMENT.

     Everything above can be inferred from the schema. This cannot. These are
     the things that are true about YOUR data because of decisions your
     organization made — a migration, a policy change, a system that was
     retired, a column that means something different than its name suggests.

     The prompt that works: what would you tell a new analyst in week one so
     they don't embarrass themselves in front of a stakeholder?

     Write each one as a directive with its consequence. -->

### 1. The survey scale changed between 2024 and 2025

**What:** Waves in 2023–2024 used a 1–5 Likert scale. Waves in 2025–2026
use a 1–7 scale. Raw averages are not comparable across the change — a jump
from 3.23 to 4.31 is almost entirely an artifact of the longer ruler, not
an improvement in engagement.

**Why:** The survey vendor changed instruments. The `scale_max` column
records which scale was used per row, but nothing in the table prevents
someone from trending raw values across the break.

**Do:**
```sql
-- Top Box scoring normalizes across scales
SELECT year(wave_date) AS yr,
       round(100.0 * avg(CASE
           WHEN scale_max = 5 AND response_value >= 4 THEN 1
           WHEN scale_max = 7 AND response_value >= 5 THEN 1
           ELSE 0
       END), 1) AS top_box_pct
FROM fct_engagement_survey
WHERE item_code IN ('ENG01', 'ENG02', 'ENG03')
GROUP BY year(wave_date)
ORDER BY 1;
```

**Don't:**
```sql
-- Raw average across a scale break — the 2025 "jump" is the ruler, not the result
SELECT year(wave_date), round(avg(response_value), 2)
FROM fct_engagement_survey
WHERE item_code IN ('ENG01', 'ENG02', 'ENG03')
GROUP BY year(wave_date)
ORDER BY 1;
```

<!-- Repeat. Aim for 5-10. Prompts, if you're stuck:

     - A column whose name no longer matches its meaning
     - A migration that left two versions of the same thing in place
     - A population that is in the table but shouldn't be in the number
     - A join that looks safe and fans out
     - A date field that isn't the date people assume it is
     - A value that means "not applicable" rather than zero
     - A number that will never reconcile to a dashboard, and why that's expected
     - Something that changed on a specific date, breaking trend comparisons -->

---

## Measures

### Engagement Top Box %

- **Definition:** Percentage of survey responses in the "agree" range across
  the three engagement items (ENG01, ENG02, ENG03), normalized across scale
  changes using Top Box scoring
- **Numerator:** Count of responses where `response_value >= 4` (5-point scale)
  or `response_value >= 5` (7-point scale)
- **Denominator:** Total responses for ENG01, ENG02, ENG03 in the wave
- **Population:** Regular employees who responded to the survey (requires join
  to `dim_worker` — the survey table alone does not carry `worker_type`)
- **Known variants:** raw average of `response_value` is commonly computed but
  NOT comparable across the 2024–2025 scale break. Anyone reporting a raw
  average must note which scale it's on.
- **Filter sensitivity:** Top Box % shifts up to 0.7 pts when contingent and
 intern responses are excluded. The trend shape is unchanged, but the specific
 numbers differ — document which population was used so two analysts reporting
 "engagement" get the same figure.
- **Reconciles to:** <!-- TODO: which dashboard, or "does not reconcile" -->

---

## Common Query Patterns

### Engagement Top Box % by year (Regular employees, normalized across scale change)

```sql
SELECT year(e.wave_date) AS survey_year,
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
ORDER BY 1;
```

**Result (verified 2026-08-11):**

| Year | Scale | Responses | Top Box % |
|---|---|---|---|
| 2023 | 5 | 2,994 | 38.9% |
| 2024 | 5 | 5,532 | 39.6% |
| 2025 | 7 | 12,588 | 44.3% |
| 2026 | 7 | 7,131 | 46.6% |

**To answer "has engagement improved since 2023":** Top Box rose from 38.9% to
46.6% (+7.7 pts). However, the 2024→2025 jump (+4.7 pts) coincides with the
scale change and is larger than both within-scale trends (~1 pt/yr). Report the
trend with the scale break disclosed, not as a single clean slope.

## Cross-References

| Joining to | On | Watch out for |
|---|---|---|
| Headcount (`dim_worker`) | `worker_id` | Required for the `worker_type = 'Regular'` filter — the survey table doesn't carry worker type |
| Attrition (`fct_separation`) | `worker_id` | A separated employee may have left before or after the survey wave — join requires attention to timing, not just key match |

## Escalate, Don't Guess

- Whether the 2024→2025 Top Box jump is "real improvement" or a scale artifact
  is a judgment call, not a statistical one — route to the survey program owner
- Cuts by protected characteristics → route to governance
- "Why is engagement low in [specific team]?" → this is a causal question about
  a named manager's org; route to People Ops, not a reference doc

  ## Open Questions

- [ ] Are the Top Box cutoffs (4–5 on 5pt, 5–7 on 7pt) the organization's
      standard, or does someone else define them differently?
- [ ] Why did the response count jump from ~3,000 to ~5,500 between 2023 and
      2024 on the same scale? Is that a participation increase or a population
      change?
- [ ] Does anyone consume a raw-average engagement score that this doc would
      now contradict? If so, which report?

      ---

## Before you call it done

- [ ] An agent that read **only Quick Reference** would pick the right table
- [ ] Every required filter states what happens if it's omitted, quantified
- [ ] Gotchas contains at least one thing that is **not inferable from the schema**
- [ ] Every measure names its denominator explicitly
- [ ] Query patterns run as written — you executed them, you didn't eyeball them
- [ ] `owner` is a named human
- [ ] Nothing in the doc is stated more than once

Then test it: hand the doc and a question to an agent with no other context, and
see whether it lands on the right table. If it doesn't, the doc is the problem —
that failure is the most useful signal you'll get.
