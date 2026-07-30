---
name: causal-claim-guardrail
version: 0.1.0
description: "Audit any analytical output for causal claims that observational data cannot support, and rewrite them into defensible associational language. IF a finding uses words like drives, causes, leads to, results in, improves, reduces, impact of, effect of, because, or due to — THEN invoke this skill before the output reaches a human. Use it especially for workforce questions about what improves retention, engagement, performance, or productivity, because those are the questions stakeholders most want a causal answer to and the data least supports. DO NOT invoke for genuinely experimental data with documented random assignment, though even then verify the assignment claim."
---

# Causal Claim Guardrail

## Overview

Stakeholders do not want to know what is *associated with* attrition. They want
to know what *causes* it, because only a causal claim tells them what to do.
That pressure is the single most reliable source of overreach in people analytics,
and a language model asked to be helpful will supply the causal phrasing the
stakeholder wanted without the design that would justify it.

The output of that failure is not a rounding error. It is a program funded on a
selection effect, or a manager penalized for a confound. This skill exists to
make the gap between what the data shows and what the sentence claims visible
before anyone acts on it.

The rule is narrow and firm: **the strength of the causal language must be
licensed by the study design, not by the size of the correlation or the
confidence of the requester.**

## When to Use

Invoke whenever output contains any of:

| Category | Trigger words |
|---|---|
| Direct causal verbs | causes, drives, leads to, results in, produces, generates |
| Directional change verbs | improves, reduces, increases, decreases, boosts, lowers, moves the needle |
| Causal nouns | impact of, effect of, driver of, lever, root cause, ROI of |
| Causal connectives | because, due to, as a result of, therefore, which is why |
| Counterfactual framing | "if we had", "we would see", "would have prevented" |
| Implicit prescription | "we should do X to get Y" |

Also invoke when the *question* is causal even if the output is not yet phrased
that way — "what's driving our attrition?" invites the failure before any
analysis is run.

**DO NOT** invoke to block legitimately supported causal claims. A well-executed
randomized rollout, a defensible difference-in-differences, or a regression
discontinuity earns causal language. The job is licensing, not prohibition.

## Process

### 1. Extract the claim

State it in its strongest form: X causes Y, in population P, by magnitude M.
Making the claim explicit is usually enough to reveal that nobody intended
to assert it that strongly.

### 2. Ask the four licensing questions

A causal claim requires defensible answers to all four. One failure is enough
to strip the causal language.

**a. What is the counterfactual?** Compared to what would have happened to the
same people, in the same period, without X? If you cannot name the comparison
condition, there is no causal estimate — only a description.

**b. How did people end up in the treated group?** This is the decisive question
in workforce data, because assignment is almost never random. People opt into
training, get promoted for reasons, and receive raises on the basis of exactly
the outcomes you are now measuring.

**c. What could confound this that you have not measured?** Name specific
plausible confounders, not "unobserved factors". If tenure, function, manager,
location, and performance all move together with the treatment, the estimate is
carrying all of them.

**d. Could the arrow run backward?** Reverse causality is endemic here.
Disengaged employees may report low engagement *because* they have already
decided to leave.

### 3. Check the named failure patterns

These recur constantly in workforce analytics. Check each explicitly:

| Pattern | How it shows up | The tell |
|---|---|---|
| **Selection into treatment** | "Employees who attended the leadership program had 12% lower attrition" | Attendees were nominated, applied, or were already high-commitment. The program may have done nothing. |
| **Reverse causality** | "Engagement drives retention" from a cross-sectional survey | Intent to leave depresses engagement scores. Same correlation, opposite arrow. |
| **Confounded manager effects** | "Manager quality explains attrition variance" | Manager, team, function, location, and job level are collinear in almost every org. The estimate cannot separate them. |
| **Survivorship** | "Tenured employees are more engaged" | You only surveyed the people who stayed. The dissatisfied left before measurement. |
| **Immortal time bias** | "5-year vesting participants have lower attrition" | You must survive to five years to be in the group. The outcome is embedded in the eligibility criterion. |
| **Regression to the mean** | "Low scorers improved after coaching" | Extreme scores move toward the mean on remeasurement with no intervention at all. |
| **Range restriction** | "Cognitive ability barely predicts performance here" | Everyone hired already cleared the bar. Restricted variance attenuates the correlation. |
| **Compositional shift** | "Average tenure fell, so retention is worsening" | Rapid hiring lowers average tenure with no change in anyone's behavior. |
| **Common-method variance** | "Engagement predicts self-rated performance" | Both come from the same person on the same instrument on the same day. |

### 4. Rewrite

Downgrade the language to what the design supports:

| Do not write | Write instead |
|---|---|
| "Training reduces attrition by 12%" | "Attrition among program participants was 12 points lower than among non-participants (n=340 vs n=2,100). Participants were nominated by managers, so selection is a plausible alternative explanation." |
| "Manager quality drives retention" | "Attrition varies substantially across managers (range 2%–19%). Manager, team, and location are confounded in this data and cannot be separated with the available design." |
| "Remote work hurts engagement" | "Fully remote employees scored 0.3 points lower on the engagement composite. Function and tenure differ between groups; the gap is not adjusted for either." |
| "Pay increases improve retention" | "Employees receiving above-median increases separated at lower rates. Increases are allocated partly on performance and flight risk, so the direction of the relationship is not identified." |

ALWAYS use this structure for a rewritten finding:

```markdown
**Observation:** [what the data shows, with n and magnitude]
**Interpretation:** [what it might mean — labeled as interpretation]
**Alternative explanations:** [named confounds, not "other factors"]
**What would be needed for a causal claim:** [specific design]
```

### 5. Say what would license the claim

This is the part that makes the skill useful rather than merely obstructive.
Do not stop at "we can't say that." Name the design that would answer it:

- **Staggered rollout** — if the program is being deployed anyway, randomize or
  stagger the order and you get a comparison for free
- **Difference-in-differences** — needs a pre-period and a plausibly parallel
  comparison group; state the parallel-trends assumption explicitly
- **Matched comparison** — reduces observable imbalance, does nothing for
  unobserved motivation, which is usually the confound that matters
- **Regression discontinuity** — usable where a threshold determines eligibility
  (a tenure cutoff, a score cutoff, a band boundary)
- **Instrumental variable** — rarely available in HR data; say so plainly rather
  than reaching for a weak instrument

Framing the answer as "here is what we'd need to run" turns a refusal into a
roadmap, and it is often the most valuable output of the analysis.

## Rationalizations

| Excuse | Rebuttal |
|---|---|
| "The correlation is very strong" | Effect size does not license causal inference. A strong confounded association is still confounded. |
| "The stakeholder needs an actionable answer" | An actionable wrong answer is worse than an honest uncertain one. They will act on it. |
| "Everyone in HR talks this way" | Field convention is not evidence. You can meet them where they are in tone without asserting what the data cannot support. |
| "I controlled for tenure, function, and level" | Controlling for observables does nothing for the unobserved selection process, which in workforce data is usually the dominant confound. |
| "It's just a slide, not a paper" | Slides are what get acted on. Papers get read by people who would have caught it. |
| "The model has high predictive accuracy" | Prediction and causation are different targets. A model can predict attrition perfectly using features you must not intervene on. |
| "I'll add a caveat at the bottom" | The headline is what travels. Fix the headline. |

## Red Flags

- The finding is exactly what the requester hoped to find
- The recommendation section proposes intervening on a variable that was never manipulated
- A predictive model's feature importances are being read as causal effects
- The comparison group was defined after the outcome was known
- Nobody can describe how people ended up in the treated group
- The word "impact" appears in a title over cross-sectional data
- You are computing an ROI for a program with no comparison condition

## Verification

- [ ] Every causal-trigger word in the output was located and adjudicated
- [ ] All four licensing questions have written answers
- [ ] The named failure patterns were each checked, not skimmed
- [ ] Surviving causal claims name their identifying design and its key assumption
- [ ] Downgraded claims use the Observation / Interpretation / Alternatives / What-would-be-needed structure
- [ ] At least one specific alternative explanation is named — "other factors may
      contribute" does not satisfy this
