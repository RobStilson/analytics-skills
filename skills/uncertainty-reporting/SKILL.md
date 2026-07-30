---
name: uncertainty-reporting
version: 0.1.0
description: "Attach honest uncertainty to every rate, percentage, ranking, and group comparison, and suppress cells too small to report. IF the output contains a percentage, a rate, a ranking of groups, a period-over-period change, or any comparison between segments — THEN invoke this skill before delivering. Use it especially for workforce cuts by team, manager, department, or demographic segment, where group sizes are small enough that point estimates are badly misleading. DO NOT skip it because the audience is non-technical; that is when it matters most."
---

# Uncertainty Reporting

## Overview

A bare point estimate is an overclaim. "Engineering attrition is 18%" reads as a
fact; if it rests on 11 people and 2 exits, it is barely distinguishable from
half the rates in the company. Stakeholders act on the number they are shown, and
they cannot supply the uncertainty you left out.

In workforce analytics this bites harder than in most domains, because the
natural units people want to slice by — teams, managers, job families, locations —
are small. A cut that looks like meaningful variation across 40 managers is
usually mostly noise.

There is a second obligation stacked on top of the statistical one: cuts of
person-level data can identify individuals. Small-cell suppression is a privacy
and legal requirement, not a statistical nicety, and it is not negotiable on
grounds of stakeholder preference.

## When to Use

| Output contains | Invoke |
|---|---|
| Any percentage or rate | Yes |
| A ranking or league table of groups | Yes — rankings of small groups are mostly noise |
| A period-over-period change | Yes |
| A comparison between segments | Yes |
| A survey result | Yes — plus response-rate disclosure |
| A raw count with no derived rate | Only if a small-cell risk exists |

**DO NOT** use this skill to bury a real finding in hedging. The goal is calibrated
reporting, not universal doubt. A well-powered, large-magnitude difference should
be stated plainly.

## Process

### 1. Suppress before you report

Apply suppression first, so a suppressed cell never reaches the formatting step.

| Cell size | Treatment |
|---|---|
| **n < 5** | Suppress entirely for any person-level cut. Do not report the count, the rate, or a range that reveals it. Report as "suppressed (n < 5)". |
| **n < 30** | Reportable with a mandatory instability flag and an interval |
| **n ≥ 30** | Report with an interval |

Watch for **complementary disclosure**: if you report a total and all-but-one
subgroup, the suppressed cell is recoverable by subtraction. Suppress a second
cell when that happens.

Cuts by protected characteristics carry additional obligations beyond cell size.
Route those through the governance path rather than deciding thresholds here.

### 2. Always state the denominator

A rate without its denominator is not interpretable. "18% attrition" and
"2 of 11 people left" are the same fact, and only the second one tells the
reader how much to trust it.

ALWAYS render rates as: `rate% (numerator / denominator)`.

### 3. Attach an interval

For proportions, use a **Wilson score interval**, not the normal-approximation
(Wald) interval. Wald behaves badly exactly where workforce data lives — small n
and proportions near 0 or 1 — where it produces intervals that extend below zero
or above one and are far too narrow. Wilson is not much harder and does not
embarrass you on a slide.

For counts of rare events, a Poisson-based interval is usually more appropriate
than a proportion interval.

Present intervals in plain language for non-technical audiences. "Between roughly
5% and 40%" communicates more honestly to an executive than "18% [95% CI: 5.1, 40.3]",
and the width is the message.

### 4. Check multiplicity before declaring a standout

If you sliced by 40 managers and are highlighting the highest and lowest, you did
40 comparisons and are reporting the extremes of a distribution. Some spread would
appear even if every manager were identical.

- State how many comparisons were made.
- Label the analysis exploratory unless the comparison was specified in advance.
- Apply a correction, or use partial pooling / shrinkage toward the overall rate,
  which is usually the more useful move for ranking small groups because it
  reflects that extreme small-group rates are mostly noise.
- Never present a league table of small groups as a performance ranking without
  this treatment.

### 5. Distinguish "no difference" from "no evidence"

An underpowered comparison that fails to detect a difference has not shown
equivalence. Say "this analysis cannot detect differences smaller than X with
n=Y" rather than "there is no difference".

### 6. Survey-specific handling

- Report response rate alongside every survey result. A 4.1 favorability score
  from a 22% response rate is a different object than one from 88%.
- Do not compare items with different response scales, or the same item after a
  wording change, without flagging the break.
- Do not compare group means across segments without considering whether the
  instrument measures the same construct the same way in each — an apparent
  group difference can be a measurement artifact rather than a real one.

### 7. Emit the standard block

```markdown
**[Metric]:** [value]% ([numerator] of [denominator])
**Range:** roughly [lower]% to [upper]% ([method], 95%)
**Stability:** [stable | unstable — small n | suppressed]
**Comparisons made:** [k] — [pre-specified | exploratory]
**Interpretation limit:** [what this analysis cannot detect]
```

## Rationalizations

| Excuse | Rebuttal |
|---|---|
| "Confidence intervals will confuse the executive" | The point estimate already misled them. Say "roughly 5% to 40%" and they will understand it fine. |
| "They asked for one number" | Give them one number *and* its width. The width is what tells them whether to act. |
| "n=11 is what we have, so I'll report it" | Reporting it without the instability flag implies a precision you do not have. Report it flagged, or say the cut is not answerable. |
| "The suppression threshold is inconvenient for this cut" | Suppression is a privacy obligation. Inconvenience does not modify it. |
| "Wald is the standard formula" | It is the *familiar* formula, and it fails precisely at small n and extreme proportions — which is where workforce cuts live. |
| "The top and bottom managers are clearly different" | With 40 comparisons, extremes appear by construction. Shrink the estimates before ranking. |
| "We didn't find a difference, so there isn't one" | Absence of evidence at this sample size is not evidence of absence. State the detectable effect size. |

## Red Flags

- A ranked list of teams or managers with no interval and no shrinkage
- A percentage on a slide with no denominator anywhere
- Period-over-period changes reported to one decimal place on small populations
- A cell you can back out by subtracting the reported subgroups from the reported total
- The phrase "no significant difference" used to mean "the groups are the same"
- A demographic cut produced without going through the governance path
- Survey comparisons across years spanning an instrument change

## Verification

- [ ] Every cell below the suppression threshold is suppressed, and complementary
      disclosure was checked
- [ ] Every rate shows its numerator and denominator
- [ ] Every rate carries an interval computed with a method appropriate to n
- [ ] Groups with n < 30 are flagged as unstable
- [ ] The number of comparisons is stated, and rankings are shrunk or labeled exploratory
- [ ] Null results state what effect size the analysis could have detected
- [ ] Survey results carry response rates and any instrument-change flags
