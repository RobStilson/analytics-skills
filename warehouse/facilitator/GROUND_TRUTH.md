# Ground Truth — Facilitator Only

**Do not distribute before the session.** Every number below was verified against
the built warehouse at seed `20260730`. If you rebuild with a different seed,
re-verify — the traps survive but the figures move.

As-of date: **2026-06-30**.

---

## Trap 1 — Grain fan-out

`fct_job_record` is **one row per job change**, not per person.

| Query | Result |
|---|---|
| `SELECT count(*) FROM fct_job_record` | **12,282** |
| `SELECT count(*) FROM dim_worker` | **5,294** |
| Naive join `dim_worker → fct_job_record` | **12,282** (2.32× inflation) |

The join inflation is the demo that lands hardest: a `LEFT JOIN` that "just adds
a column" more than doubles the row count, and every downstream average is wrong.

**Correct handling:** filter `is_current = true`, or apply an effective-date
predicate (`effective_start <= :as_of AND effective_end >= :as_of`).

---

## Trap 2 — Entity ambiguity: four answers to "how many employees?"

| Source | Answer | Why it differs |
|---|---|---|
| `fct_job_record` `COUNT(*)` | **12,282** | No as-of filter; counts job changes |
| `vw_active_workers` | **4,368** | Includes contingent workers and interns |
| `rpt_headcount_daily` (latest row) | **4,168** | Stale — stopped refreshing 2026-02-28 |
| `dim_worker_snapshot`, Regular, distinct person | **3,647** | ✅ Canonical |

The canonical query:

```sql
SELECT count(DISTINCT employee_number)
FROM dim_worker_snapshot
WHERE snapshot_date = DATE '2026-06-30'
  AND worker_type = 'Regular'
  AND employment_status IN ('Active', 'On Leave');
```

Whether to include `'On Leave'` is a legitimate judgment call — the point is that
it must be *stated*, not silently defaulted. `vw_active_workers` inflates by
**19.8%**, which is large enough that nobody notices it is wrong and small enough
that it looks plausible.

---

## Trap 3 — Staleness: `department` superseded by `org_unit_v2`

`department` is the legacy label. It was never dropped and is **54% populated**.

- Latest snapshot: 4,368 rows, **2,360** carry a `department` value — so an
  unfiltered legacy cut drops **2,008 rows**
- Under the standard headcount filter (Regular, Active/On Leave), the legacy cut
  keeps 1,979 of 3,647 people — **1,668 dropped**. Quote whichever matches the
  filter the participant actually ran; the two figures are not interchangeable.
- Three org units (`OU-1300` Security Engineering, `OU-3300` Corporate
  Development, `OU-4200` Quality Assurance) have **no** legacy label at all —
  they were created after the migration and vanish entirely from any legacy cut

This is the trap most likely to reach a stakeholder undetected, because the
output looks complete. There is no null row to notice.

---

## Trap 4 — Worker type

`worker_type ∈ {Regular, Contingent, Intern}`, all in the same tables.
Headcount conventionally means Regular only. Omitting the filter inflates by
roughly 20%.

---

## Trap 5 — Rehire duplicates

**94 humans hold two `worker_id` values.** `employee_number` is the person key.

| Count | Result |
|---|---|
| `count(DISTINCT worker_id)` | 5,294 |
| `count(DISTINCT employee_number)` | 5,200 |

Bites hardest on **tenure** (a rehire's second record has a recent hire date, so
naive tenure understates continuous service) and on **cumulative** counts over a
period. It does *not* bite on a single point-in-time headcount, because the
earlier record is already terminated — worth saying out loud, since participants
will ask why the two numbers match on the snapshot.

---

## Trap 6 — Denominator choice

2025 attrition, same 319 separations:

| Denominator | Rate |
|---|---|
| Beginning headcount (2024-12-31) | **15.9%** |
| Average headcount | **12.1%** |
| Ending headcount (2025-12-31) | **9.7%** |

A 6-point spread from the same numerator. `rpt_attrition_monthly` supplies raw
separation counts with no denominator at all, which invites whichever choice is
convenient.

2024 for reference: 6.5% on average headcount.

---

## Trap 7 — Small cells

At the org-unit level only one unit is small: **`OU-3300` Corporate Development,
n=7** — unstable, but above the n<5 suppression threshold.

Suppression bites properly on a **cross-tab**. `org_unit_v2 × location_id`
produces **9 cells with n<5**, including four cells with **n=1**:

```
OU-3300 × LOC003  n=1        OU-1300 × LOC006  n=3
OU-3300 × LOC006  n=1        OU-3300 × LOC005  n=3
OU-3300 × LOC007  n=1        OU-4200 × LOC005  n=3
OU-3300 × LOC004  n=1        OU-4200 × LOC006  n=3
                              OU-1300 × LOC005  n=4
```

Teaching point: a cut that is safe at one level becomes identifying one slice
deeper, and nothing in the query warns you. Also demonstrate **complementary
disclosure** — report the OU-3300 total plus all-but-one location and the
suppressed cell is recoverable by subtraction.

---

## Trap 8 — Selection bias ⭐ the headline demo

**The Emerging Leaders Program has a TRUE causal effect of exactly zero.** It is
generated with no effect on separation. Every observed difference is selection.

| Group | n | Attrition |
|---|---|---|
| Enrolled | 1,343 | **11.6%** |
| Not enrolled | 3,021 | **18.6%** |
| **Naive gap** | | **−7.0 points** |

Stratifying by `fct_performance_rating.performance_tier` (the *observed*
confounder):

| Tier | Enrolled | Not enrolled | Gap |
|---|---|---|---|
| 1 | n=59, 32.2% | n=604, 29.8% | **+2.4** (reversed, small n) |
| 2 | n=336, 15.2% | n=1,192, 19.3% | −4.1 |
| 3 | n=586, 11.4% | n=932, 13.8% | −2.4 |
| 4 | n=362, 5.2% | n=293, 7.5% | −2.3 |

Note tier 1 **reverses** — enrolled workers separate slightly *more*. With n=59
that is noise, and it is a useful live demonstration of why
`uncertainty-reporting` insists on intervals before anyone reads a stratum gap
as a finding.

**Tier-adjusted gap: −2.3 points.**

Two lessons, and the second is the more important one:

1. Adjusting for the observed confounder removes **most** of the apparent effect
   (−7.0 → −2.3). This is the fix participants will reach for.
2. It does **not** remove all of it. The generator includes a latent commitment
   trait that drives both nomination and retention and **appears nowhere in the
   warehouse**. The residual −2.3 is irreducible confounding. No amount of
   controlling for observables recovers the true zero.

That second point is the whole argument for `causal-claim-guardrail`. A
participant who adjusts for performance tier and then reports "a modest 2-point
effect" has still overclaimed. The defensible output names the design that would
be needed — a staggered or randomized rollout of the next cohort.

Supporting detail: `nomination_source` is **85.6% Manager Nomination**, which is
the visible tell that assignment was not random.

---

## Trap 9 — Instrument change

The engagement survey moved from a **1–5** scale to a **1–7** scale for the 2025
wave. `scale_max` is present on every row and easy to ignore.

| Year | Scale | Mean (ENG01) |
|---|---|---|
| 2023 | 1–5 | 3.21 |
| 2024 | 1–5 | 3.22 |
| 2025 | 1–7 | 4.35 |
| 2026 | 1–7 | 4.41 |

A naive cross-year trend shows engagement "improving 35% in 2025." Nothing
changed but the scale. Response rates also vary by wave (55–79%), which is a
second, quieter disclosure obligation.

---

## Trap 10 — Immortal time bias

The 3-Year Service Award requires surviving to the three-year mark.

| Group | n | Attrition |
|---|---|---|
| Received award | 707 | **2.5%** |
| No award | 4,587 | **19.8%** |

An 8× difference, entirely by construction: the outcome is embedded in the
eligibility criterion. A tempting and completely invalid finding —
"recognition drives retention."

---

## Trap 11 — Retrieval failure

**44 tables.** 16 carry real data; **28 are empty decoys** with plausible names
(`fct_recruiting_application`, `fct_exit_survey`, `dim_talent_pool`,
`stg_workday_worker_raw`, …).

Grep-and-hope fails here, which is the intended lesson: the fix is narrowing the
search space with a curated reference doc, not giving the agent more access.

---

## Running the ablation live

The demo that justifies the workshop. Roughly 10 minutes.

**Round 1 — no skill.** Ask the agent: *"How many employees do we have, and what
was attrition last year?"* Expect a confident answer built on whichever table it
finds first, with no denominator stated and no worker-type filter. Record it.

**Round 2 — participants write the reference doc.** The BUILD block. They
document grain, canonical source, required filters, and gotchas for one domain.

**Round 3 — same question, with the skill loaded.** Expect the canonical source,
a stated denominator, and a provenance footer.

Then run the eval set both ways and show the pass-rate delta.

**Two cautions.** Round 1 is not guaranteed to fail — a capable model sometimes
picks the right table by luck or notices the ambiguity unprompted. Run it once
before the session so you know what you are walking into, and have a screenshot
of a failing run as backup. And when it *does* answer well unprompted, say so
rather than pretending otherwise; "the model caught this one, and here is the
question it still cannot answer without your knowledge" is a more honest and
more durable framing than a rigged demo.

The questions where the model reliably needs human knowledge are Traps 3, 8, and
10 — the renamed column, the selection effect, and the immortal time bias. Those
are not inference failures; they are things the model cannot know about your
organization. Lead with those if the headcount demo lands soft.
