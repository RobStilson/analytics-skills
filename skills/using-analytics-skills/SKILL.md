---
name: using-analytics-skills
version: 0.1.0
description: "Router and shared operating rules for the analytics-skills pack. IF the session involves querying a data warehouse, answering a business or workforce question from data, reviewing an analysis, or producing a number a stakeholder will act on — THEN read this skill first to decide which other skills apply. Use this even when the request sounds simple ('just pull headcount'), because the simple-sounding asks are where wrong answers hide. DO NOT invoke for pipeline engineering, access provisioning, or coding tasks with no analytical output."
---

# Using Analytics Skills

## Overview

This pack exists because analytics agents fail differently than coding agents.
Coding has an open-ended solution space with tests and compilers as guardrails.
Analytics usually has exactly one correct answer, drawn from exactly one correct
source, with no deterministic way to prove you found it. A fluent, well-formatted,
confidently wrong number is the default failure mode — and unlike a failing test,
nothing surfaces it.

Three problems cause most wrong answers. Every skill in this pack attacks at least one:

| Failure mode | What it looks like | Skills that address it |
|---|---|---|
| **Entity ambiguity** | Forty plausible tables could answer "headcount"; the agent picks one | `question-intake`, `warehouse-navigation` |
| **Staleness** | The doc, the column, or the definition changed and nobody told the agent | `skill-freshness-check`, `correction-harvesting` |
| **Retrieval failure** | The right answer is documented, but the agent never finds it | `warehouse-navigation`, this router |
| **Silent wrongness** | Plausible output, unstated assumptions, no way for the reader to tell | `adversarial-sql-review`, `causal-claim-guardrail`, `uncertainty-reporting`, `provenance-footer` |

## When to Use

Read this skill at the start of any analytics session. Then route:

| The request is... | Load |
|---|---|
| A new or vaguely-specified question | `question-intake` |
| A question that's clear but needs data located | `warehouse-navigation` |
| A query written and ready to run | `adversarial-sql-review` |
| Output containing "drives", "impact of", "because", "leads to" | `causal-claim-guardrail` |
| A rate, percentage, ranking, or group comparison | `uncertainty-reporting` |
| Any answer about to be delivered to a human | `provenance-footer` |
| A reference doc or skill that may have drifted | `skill-freshness-check` |
| A stakeholder correcting a prior answer | `correction-harvesting` |

Skills compose. A typical full pass loads four or five of them.

**DO NOT** route to these skills for: access requests, pipeline troubleshooting,
dashboard outages, or questions with no data-warehouse component. Escalate those
to the owning team rather than attempting an answer.

## Process

The analytics lifecycle, and where each skill sits:

```
DEFINE ──────▶ BUILD ──────▶ VALIDATE ──────▶ OPERATIONALIZE ──▶ MONITOR
question-      warehouse-    adversarial-      provenance-        skill-freshness-
intake         navigation    sql-review        footer             check
                             causal-claim-                        correction-
                             guardrail                            harvesting
                             uncertainty-
                             reporting
                                    │                                   │
                                    └──────── COMPOUND ◀────────────────┘
                          every correction becomes a doc edit and an eval
```

The **compound** step is what separates this from ordinary AI-assisted analysis.
An analysis that ends when the number is delivered has produced one answer. An
analysis that ends with a reference-doc edit and a new eval has produced a system
that answers better next time. Skipping it means you did traditional analytics
with an AI typing for you.

## Shared Operating Rules

These apply in every skill and override local convenience:

1. **Never invent a column, table, or value.** If the field you need does not
   exist, say so and stop. A fabricated column name that happens to sound right
   is the most expensive kind of error, because it looks like a real answer.
2. **Separate observation from interpretation.** "Voluntary exits rose from 4.1%
   to 6.3%" is an observation. "Morale is declining" is an interpretation. Label
   which is which, always.
3. **Use safe division.** Guard every denominator. A silent divide-by-zero that
   renders as `NULL` reads to a stakeholder as "zero", not as "undefined".
4. **Suppress small cells in person-level data.** Never report a cell with fewer
   than 5 people when the cut could identify individuals — this is a privacy and
   legal exposure issue before it is a statistical one. See `uncertainty-reporting`.
5. **Escalate rather than guess.** Access denied, table missing, definition
   contested, or the question is really a policy question — name the owning team
   and stop. Guessing here produces confident nonsense.
6. **Every delivered answer carries a provenance footer.** No exceptions, including
   for answers that seem trivially simple.

## Rationalizations

Agents skip these steps under predictable pressure. The excuses and their rebuttals:

| Excuse | Rebuttal |
|---|---|
| "The question is simple, intake is overkill" | Simple-sounding questions are exactly where entity ambiguity lives. "How many employees do we have" has at least six defensible answers. |
| "The user is in a hurry" | A wrong number delivered fast gets forwarded, cited in a deck, and discovered three weeks later. The cost of the correction exceeds the cost of the clarification. |
| "I already know what they mean" | You know what the words mean. You do not know which population, which as-of date, or which decision it feeds. Ask. |
| "There's no reference doc for this domain, so I'll just explore" | Raw exploration is permitted, but it is the lowest source tier and must be labeled as such in the footer. Undocumented is not the same as ungoverned. |
| "The review sub-agent will slow things down" | It will. Adversarial review costs meaningfully more tokens and latency. The alternative is that the stakeholder is your reviewer, after the number is in a board deck. |

## Red Flags

Stop and reconsider if you notice yourself:

- Choosing between two similarly-named tables without knowing which is canonical
- Writing a `WHERE` clause that filters a population, when a named segment probably exists
- Reporting a percentage without having stated the denominator
- Using a causal verb about data you did not collect experimentally
- Answering a question about *why* something happened when you only have data on *what* happened
- Producing a number that would surprise the domain owner, without flagging that it would

## Verification

Before delivering any analysis, confirm you can point to evidence for each:

- [ ] The question spec was confirmed, or the ambiguities were explicitly resolved and stated
- [ ] The source tier is known and named
- [ ] The query passed adversarial review, and blocking findings were fixed and re-reviewed
- [ ] Causal language was audited, or no causal language was used
- [ ] Every rate carries a denominator and an uncertainty statement
- [ ] The provenance footer is attached
- [ ] Anything learned that would help next time was written back to a reference doc

"It looks right" is not evidence.
