# Worked Example — Define Worksheet (Headcount)

This is what a completed Define worksheet looks like for the **headcount**
domain. Use it as a reference while you fill in your own — but don't copy
the structure of the *answers*. Your domain has different risks, different
ambiguities, and different judgment calls.

**Headcount is the worked example, not an exercise.** Pick Attrition,
Compensation, or Engagement for yours.

---

## 0. Pick your domain

**Headcount.** Starting question: *How many employees do we have?*

---

## 1. Restate and set the population

**Restated question:** How many people are currently employed as regular
workers?

**Population:** Regular employees only — no contractors, no interns. Include
people on leave (they're still employed). Exclude terminated workers.

*Why those choices:* "Employees" usually means regular headcount in board
reporting. Contractors and interns inflate the number by ~20%, and someone
asking this question almost certainly doesn't want that blended in without
knowing. But "include on-leave or not" is genuinely ambiguous — stating the
choice is more important than which way you go.

---

## 2. Time basis and grain

**Time basis:** Point-in-time (as-of a specific date). This is not a
period-of-activity question — it's "how many do we have *right now*," not
"how many did we have *during* a period."

**Grain:** One row per worker per month-end snapshot. That means I need to
filter to a single `snapshot_date` to avoid counting the same person 29 times
(once for every month in the table).

---

## 3. Name the measure

**Measure:** `count(DISTINCT employee_number)` of regular workers who are
Active or On Leave, as of the most recent snapshot date.

Not `worker_id` — rehired workers get a new `worker_id` but keep their
`employee_number`. Using `worker_id` overcounts by 94 people. (I don't know
this yet at Define time — I'll discover it during Build. But the *decision*
to name the key now forces me to check it later.)

Not FTE — headcount counts heads, FTE sums fractional values. They're
different questions (3,647 vs. 3,516.0) and the requester probably means one
or the other, not both.

No denominator — this is a count, not a rate.

---

## 4. Comparison, decision, precision

**Comparison:** None stated in the question — just the absolute number. But
if someone asks headcount, they almost always compare it to something: last
quarter, last year, budget, a target. I'll note that as an open assumption
and ask if I can.

**Decision it informs:** Workforce planning, budget allocation, board
reporting. If headcount is higher or lower than expected, someone adjusts
hiring plans, requisitions, or cost projections.

**Precision needed:** Exact and auditable. Headcount hits the board deck.
A directional answer ("roughly 3,600") will be replaced by whoever can
produce the real number. Worse, if the rough number is close but wrong, it
might *not* be replaced.

---

## 5. Existing coverage and open assumptions

**Existing coverage:** There's a `rpt_headcount_daily` report in the
warehouse, but I haven't verified whether it's current or stale yet. (It
turns out to be four months stale — I'll find that during Build. At Define
time I just note it exists.)

**Open assumptions:**

1. "Employees" means Regular workers only (excluding Contingent and Intern)
2. People on leave are included — they're still employed
3. No comparison period stated — treated as a standalone absolute number
4. Using most recent snapshot date available in the table
5. Counting distinct people, not distinct positions or FTE

---

## The finished spec

```markdown
## Question Spec

**Restated question:** How many people are currently employed as regular workers?
**Population:** Regular workers (excluding Contingent, Intern); Active or On Leave; excluding Terminated
**Time basis:** As-of date (most recent month-end snapshot)
**Grain:** One row per worker per month-end in dim_worker_snapshot — must filter to a single snapshot_date
**Measure:** count(DISTINCT employee_number) — a count, not a rate; no denominator
**Comparison:** None stated — absolute number only
**Decision it informs:** Workforce planning, budget allocation, board reporting
**Precision needed:** Exact and auditable — this number reaches the board deck
**Existing coverage:** rpt_headcount_daily exists but freshness not yet verified
**Open assumptions:** (1) "Employees" = Regular only; (2) On Leave included; (3) no comparison period; (4) latest snapshot date; (5) counting people, not positions or FTE
```

---

## What to notice about this example

**Every field is a decision, not a fact.** "Regular workers only" is a
choice. "Include on-leave" is a choice. "No comparison" is a choice. The
spec doesn't discover truth — it makes the assumptions visible so they can
be confirmed, challenged, or changed before anyone writes a query.

**The open assumptions are the most valuable part.** They're what the
provenance footer will disclose later, and they're what the reference doc
(written in Build) should resolve or explicitly leave open. A spec with
no open assumptions is either trivial or dishonest.

**You don't need the data to fill this in.** Everything here was written
before querying the warehouse. Some of it turned out to be wrong — the
person key assumption, the existing-coverage note — and that's fine. The
spec's job is to be *checkable*, not *correct*. You'll check it in Build.
