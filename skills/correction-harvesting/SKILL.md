---
name: correction-harvesting
version: 0.1.0
description: "Convert every stakeholder correction into a reference-doc fix and a new eval, so the same mistake cannot recur. IF someone says the agent used the wrong table, missed a filter, misdefined a metric, or produced a number that disagrees with a known-good source — THEN invoke this skill immediately, before moving on to the corrected answer. Use it even for corrections that seem trivial or one-off, because the corpus of trivial corrections is where domain knowledge actually lives. DO NOT treat a correction as merely something to apologize for and fix in place."
---

# Correction Harvesting

## Overview

This is the compound step. Everything else in the pack produces an answer; this
skill produces a system that answers better next time. An analytics practice that
fixes each wrong answer individually has, after a year, fixed a year of wrong
answers. One that harvests each correction has a reference corpus encoding what
its senior analysts know.

The economics are asymmetric in an unusual way. A stakeholder correction is the
single highest-value signal available — it is a labeled error, diagnosed for free
by someone with domain authority. Discarding it after patching the immediate
answer wastes the most expensive input in the entire loop.

Two artifacts come out of every correction: **a doc edit** so the agent routes
correctly next time, and **an eval** so the fix cannot silently regress.

## When to Use

Invoke on any correction signal, including these phrasings:

| Signal | Example |
|---|---|
| Wrong source | "that's not the table we use for that" |
| Missing filter | "you need to exclude the contingent workers" |
| Wrong definition | "we count regrettable differently" |
| Reconciliation failure | "that doesn't match the dashboard" |
| Stale knowledge | "we renamed that field last quarter" |
| Scope error | "that shouldn't include people on leave" |
| Implicit correction | The stakeholder restates the question with a constraint you did not apply |

That last row matters. Many corrections are never phrased as corrections — the
stakeholder simply asks again with more specificity. Treat the added specificity
as the correction it is.

**DO NOT** invoke for disagreements about interpretation or recommendation. If a
stakeholder disputes what a finding *means* rather than what the data *says*, that
is a discussion, not a documentation defect.

## Process

### 1. Capture before fixing

Record the correction verbatim before producing the corrected answer. Once you
have moved on to the fix, the specific wording of what went wrong is lost, and
the wording is the diagnostic.

```markdown
**What I produced:** [the wrong output]
**What they said:** [verbatim correction]
**Domain:** [which reference doc owns this]
```

### 2. Classify the failure mode

Different failure modes need different repairs:

| Mode | Symptom | Repair target |
|---|---|---|
| **Entity ambiguity** | Wrong table chosen among plausible candidates | Add a routing trigger to the domain doc |
| **Missing gotcha** | Right table, missing required filter | Add to the doc's Gotchas section |
| **Definition drift** | Metric computed to an outdated definition | Update the definition; check the semantic layer too |
| **Retrieval failure** | The doc was correct and not found | Fix the router entry, not the domain doc |
| **Genuine gap** | Nothing documented this domain | Create a new reference doc |

Misclassifying here produces a repair that does not prevent recurrence. If the
doc was right and the agent did not find it, editing the doc changes nothing.

### 3. Draft the smallest sufficient edit

Prefer one line to one paragraph. Reference docs that grow without bound become
docs the agent retrieves poorly from and humans stop maintaining.

Write for retrieval by a model, not for a human reader's narrative comfort. Use
explicit routing conditionals:

```markdown
- IF the question concerns headcount as of a date THEN use `dim_worker_snapshot`
  with an effective-date predicate. DO NOT use `fct_job_record` — its grain is
  one row per job change, which double-counts mid-period promotions.
```

That form does more work than a paragraph explaining the difference between the
two tables, because it tells the agent what to do rather than what is true.

### 4. Write the eval

The doc edit fixes it now; the eval keeps it fixed. Write a question/answer pair
that would have failed before the edit and passes after.

- **Pin the ground truth** so it cannot drift: anchor to a snapshot date, write
  against a stable fact table, or grade the *query* rather than the number.
- Store it in the domain's eval slice.
- Where practical, verify the eval fails against the pre-edit doc. An eval that
  passes either way is not testing anything.

### 5. Ship it as a PR to the owner

Keep the path deliberately boring — edit markdown, merge, auto-sync. Tag the
domain owner. If harvesting a correction requires a design discussion, it will
not happen at volume, and volume is the entire point.

Where a scheduled agent can scan stakeholder channels for correction language and
open draft PRs automatically, that closes the loop without human initiation. The
domain owner reviews a one-line diff rather than authoring one.

### 6. Note what did not work

Keep a short running list of repairs that were tried and failed to help — an
added section that made retrieval worse, a rewrite that did not move the eval.
Negative results are cheap to record and prevent the next person from repeating
the experiment. Where a doc edit can be measured, put the before/after eval delta
in the PR description; it keeps "I improved the docs" honest and catches the
surprisingly common case where a well-intentioned addition makes things worse.

## Rationalizations

| Excuse | Rebuttal |
|---|---|
| "It was a one-off, not worth documenting" | The corpus of one-offs *is* the domain knowledge. Every gotcha started as a one-off. |
| "I'll just remember for next session" | There is no next session. Context does not persist. The doc is the memory. |
| "The stakeholder was being picky" | They were being correct. Their pickiness is the labeled training signal you cannot buy. |
| "Fixing the answer is what they asked for" | It is what they asked for and half of what the moment is worth. The other half costs two minutes. |
| "Writing the eval is overkill for a small fix" | Without the eval the fix regresses silently on the next doc rewrite, and nobody notices. |
| "I'll batch the corrections and file them weekly" | Batched corrections lose their context and get filed as vague generalities, if they get filed at all. |

## Red Flags

- The same correction has arrived more than once — the earlier repair targeted the wrong layer
- Corrections are being handled entirely in chat with no artifact produced
- The doc grew by a paragraph for a one-line problem
- An eval was written that would have passed before the fix
- Nobody owns the domain doc the correction belongs to
- Correction volume is falling while stakeholder trust is also falling — people
  have stopped bothering to correct, which is worse than being corrected

## Verification

- [ ] The correction was captured verbatim before the fix was produced
- [ ] The failure mode was classified, and the repair targets that layer
- [ ] A doc edit exists and is as small as it can be while still sufficient
- [ ] An eval exists, is pinned against drift, and demonstrably fails pre-edit
- [ ] A PR is open and tagged to the named domain owner
- [ ] Failed repair attempts were recorded rather than silently abandoned
