---
name: question-intake
version: 0.1.0
description: "Turn a vague stakeholder request into a specific, answerable question spec before writing any SQL. IF a data request arrives without an explicit population, time window, grain, and decision context — THEN invoke this skill first. Use it for requests that sound obvious ('how many people do we have', 'what's our attrition', 'is engagement up'), because those are the ones with the most hidden ambiguity. DO NOT invoke when a confirmed question spec already exists in the session, or when the user is asking a definitional question with no data pull attached."
---

# Question Intake

## Overview

The hard part of agentic analytics is not writing SQL. It is mapping a human
sentence onto specific, governed entities in a data model. Once that mapping is
right, the query is close to trivial. Once it is wrong, no amount of query
elegance recovers it.

This skill front-loads that mapping. It is deliberately slower than jumping to a
query, and that is the point: the time you spend here is time you would otherwise
spend rewriting an analysis after a stakeholder says "that's not what I meant."

## When to Use

Invoke when any of the following is unresolved:

| Trigger | Example |
|---|---|
| Population is unstated | "How many employees?" — including contractors? interns? on leave? |
| Time window is unstated or relative | "This year" — calendar? fiscal? trailing 12? |
| The measure has multiple definitions | "Attrition" — voluntary? regrettable? annualized? |
| The grain is ambiguous | Per person? per position? per FTE? |
| The comparison is implied but unspecified | "Is it high?" — versus what? |

**DO NOT** invoke for questions that arrive already specified, or for pure
definitional questions ("what does regrettable attrition mean?") with no pull attached.

## Process

### 1. Restate the request in one sentence

Say it back before doing anything. Misunderstandings surface here for free.

### 2. Resolve the five ambiguities

Work through each explicitly. Do not silently pick a default.

**Population.** Who counts as a row? In workforce data this is rarely obvious:

| "Employees" could mean | Typically differs by |
|---|---|
| Active regular employees | Excludes contingent workers, interns, and often excludes those on leave |
| All workers | Includes contractors and agency staff, who may have no comp or performance records |
| Headcount vs. FTE | A 0.5 FTE part-timer is one head and half an FTE |
| Benefits-eligible | A different threshold again, and the one Finance usually means |

**Time window.** Workforce data is effective-dated, which makes this harder than
it looks. "As of March 31" and "during Q1" are different questions with different
answers — a point-in-time snapshot versus an activity window. Establish which one
the decision needs.

**Grain.** One row per what? Person, position, job record, or person-month?
A person with a mid-year promotion has multiple job records. Counting rows
instead of people is one of the most common wrong answers in workforce analytics.

**Measure.** Which definition, and whose? Attrition alone has several:

- Voluntary vs. involuntary vs. all separations
- Regrettable vs. non-regrettable (and by whose determination)
- Denominator: beginning headcount, ending headcount, or average headcount
- Annualized vs. period-actual

These produce materially different numbers from the same underlying data.
Pick one, name it, and put the name in the answer.

**Comparison.** A number alone rarely informs a decision. Against last year?
Against another business unit? Against an external benchmark? If the stakeholder
has no comparison in mind, the question may not be ready.

### 3. Surface the decision

Ask: *what will you do differently depending on the answer?*

This question does more work than any other. It reveals the real precision
requirement, exposes questions where no answer would change anything, and
frequently reveals that the stated question is a proxy for a different one.

If the answer is "I just want to know" — that's legitimate, but it lowers the
precision bar, and you should say so rather than over-engineering.

### 4. Set the good-enough bar

Explicitly agree on what precision the decision needs. "Within a point" and
"exactly right, it's going to the board" are different jobs. Over-precision
wastes time; under-precision gets discovered later.

### 5. Check whether it's already answered

Before building anything, check for an existing dashboard, prior analysis, or
governed metric that covers the question. Re-deriving a number that already
exists somewhere else is how organizations end up with two official numbers
that disagree.

### 6. Emit the spec and confirm

ALWAYS use this exact template:

```markdown
## Question Spec

**Restated question:** [one sentence]
**Population:** [who counts, with exclusions named]
**Time basis:** [as-of date | activity window; calendar or fiscal]
**Grain:** [one row per ___]
**Measure:** [named definition, including denominator]
**Comparison:** [against what, or "none — absolute value only"]
**Decision it informs:** [what changes based on the answer]
**Precision needed:** [directional | ±1pt | exact/auditable]
**Existing coverage:** [dashboard or metric that already answers this, or "none found"]
**Open assumptions:** [anything you resolved by choosing a default]
```

Ask the stakeholder to confirm. If they cannot be reached, proceed using the
spec as written and carry the **Open assumptions** into the final answer —
never silently.

## Rationalizations

| Excuse | Rebuttal |
|---|---|
| "Asking questions makes me look slow" | Delivering the wrong population makes you look wrong. One is recoverable in a minute; the other after a week. |
| "I'll pick the most common definition" | The most common definition in your warehouse may not be the one this stakeholder's team uses. Definitions are local. Name yours. |
| "They said 'quick and dirty', so precision doesn't matter" | "Quick and dirty" lowers the precision bar, not the *specification* bar. You still need to know which population. |
| "The spec template is heavy for a one-line question" | Then it takes 30 seconds. The template is a checklist, not an essay. |
| "I'll clarify after I see the data" | The data will look plausible under every definition. It will not tell you which one they wanted. |

## Red Flags

- You are about to write `WHERE status = 'Active'` without knowing what `Active` excludes
- The request contains "just" ("just pull me headcount")
- The stakeholder used a term you have seen defined two ways in this organization
- You cannot articulate what decision the answer feeds
- The question is really asking *why*, but you only have data on *what*
- The request asks for a cut by a protected characteristic — stop and route to the
  appropriate governance path before proceeding

## Verification

- [ ] A written question spec exists in the session
- [ ] Every one of the five ambiguities is explicitly resolved, not silently defaulted
- [ ] The measure definition is named, including its denominator
- [ ] Either the stakeholder confirmed, or open assumptions are recorded for the footer
- [ ] Existing coverage was checked before new work started
