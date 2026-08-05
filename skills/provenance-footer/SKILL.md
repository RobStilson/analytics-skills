---
name: provenance-footer
version: 0.2.0
description: "Attach a standard provenance footer to every DELIVERED analytical answer — a number, rate, ranking, or finding derived from data — so the reader can judge how much to trust it and whether it is safe to forward. IF an analysis, number, chart, or written finding is about to be delivered to a human — THEN invoke this skill and append the footer. Use it on every such answer including one-line responses in chat, because the answers most likely to be forwarded without scrutiny are the short ones. DO NOT omit it on the grounds that the answer is obvious or the requester is technical. DO NOT invoke it for a schema or metadata question — whether a table or column exists, what a table's grain is — since no analytical finding is being delivered and nothing there needs a source or a confidence level."
---

# Provenance Footer

## Overview

The failure mode nothing else in this pack fully catches is the **silent** one:
the answer is wrong, looks plausible, and is used without objection. There is no
technique that reliably prevents it. The footer is a partial mitigation — it does
not make the answer more correct, but it gives the reader the information they
need to decide whether to verify before forwarding.

A footer that reads "raw table, freshness unknown, unreviewed" is a signal to
check. Without the footer, that answer is visually indistinguishable from one
that came out of a governed semantic layer and passed two review rounds.

The footer also does quiet institutional work. Once every answer carries a source
tier, the share of answers resolving to Tier 1 becomes a measurable quantity, and
that number is one of the better health metrics for an analytics agent program.

## When to Use

Every delivered **analytical answer** — something derived from querying data
that could be forwarded, acted on, or cited: a number, a rate, a ranking, a
chart, a written finding. There is no exemption for:

- Short answers ("just the number")
- Technical requesters
- Answers the requester already knows
- Chat replies as opposed to formal documents
- Iterative back-and-forth *once a number or finding is actually delivered*
  (footer the final answer at minimum, even mid-session)

**DO NOT** attach a footer to intermediate reasoning you are not presenting as
an answer — it becomes noise and people stop reading it.

**DO NOT** attach a footer to a schema or metadata question — "does this table
have column X," "what's the grain of table Y," "what tables exist for this
domain." Those aren't analytical findings. Nothing about a source tier,
confidence level, or population applies to a yes/no about structure, and a
footer on one trains people to skip footers generally.

**The line, precisely:** did this response deliver a number, rate, or finding
computed from data, or did it answer a question about the data's *shape*? The
first needs a footer. The second is a fact about the schema, not a claim about
the world, and gets a direct answer instead.

## Process

### 1. Determine the source tier

| Tier | Meaning | Label |
|---|---|---|
| 1 | Governed semantic layer / compiled metric definition | `semantic layer` |
| 2 | Canonical governed table, per a domain reference doc | `governed table` |
| 3 | Raw exploration; no reference doc covered this | `raw exploration` |
| — | Combination | Name the lowest tier used |

The lowest tier touched sets the label. An answer that joins a governed table to
a raw one is a raw-exploration answer.

### 2. Set the confidence tier

Confidence describes the analytical process, not your feelings about the result:

| Confidence | Criteria |
|---|---|
| **High** | Tier 1 source, spec confirmed, review passed with no blocking findings |
| **Medium** | Tier 2 source, or open assumptions were carried forward, or advisory findings unresolved |
| **Low** | Tier 3 source, unresolved ambiguity, small n, or reconciliation failed |

Never label an answer High because the requester needs it to be.

### 3. Establish freshness from the data

Report the maximum date actually present in the queried data, not the pipeline's
nominal schedule. Tables settle late; "loads daily" and "has yesterday's data"
are different statements.

### 4. Assemble

ALWAYS use this exact template:

```markdown
---
**Source:** [semantic layer | governed table | raw exploration] — `[table or metric name]`
**Confidence:** [High | Medium | Low]
**Reviewed:** [reviewer, round N | not reviewed]
**Freshness:** data through [max date in result]
**Owner:** [team that owns the source]
**Population:** [one-line restatement of who is counted]
**Open assumptions:** [anything resolved by default rather than confirmation, or "none"]
**Caveats:** [unresolved advisory findings, suppressed cells, or "none"]
```

**Example:**

```markdown
---
**Source:** governed table — `dim_worker_snapshot`
**Confidence:** Medium
**Reviewed:** sql-reviewer ✓, round 2
**Freshness:** data through 2026-07-27
**Owner:** People Data Engineering
**Population:** Active regular employees, excluding contingent workers; includes those on leave
**Open assumptions:** "This quarter" interpreted as fiscal Q3, not calendar
**Caveats:** Two department cells suppressed (n < 5)
```

### 5. Escalate rather than footnote

Some things do not belong in a footer at all. If the answer is Low confidence
*and* leadership-bound, get explicit human sign-off before it goes out. A caveat
line is not a substitute for a person taking responsibility for a number that
will be acted on.

## Rationalizations

| Excuse | Rebuttal |
|---|---|
| "The footer is longer than the answer" | Frequently true, and still worth it. The one-line answers are the ones that get forwarded unexamined. |
| "They know where the data came from" | They know where they *assume* it came from. Those diverge, and the divergence is invisible. |
| "It's a rough number, they know not to trust it" | You know that. The third person to receive the screenshot does not. |
| "I'll mark it High, the query was clean" | A clean query on a raw table is still a raw-table answer. Confidence describes the process, not the query. |
| "Freshness is whatever the pipeline schedule says" | Pipelines run late and land partial. Read the max date from the result. |
| "It clutters chat responses" | Then compress it to one line, but keep source, freshness, and confidence. Do not drop it. |
| "They said 'I'm iterating,' and iteration isn't exempt" | Iteration isn't exempt *once a number is delivered*. "Does this column exist" delivers no number — it's a schema question wearing an iteration sentence. Answer it directly. |

## Red Flags

- The confidence label rose after a stakeholder expressed disappointment
- Freshness was copied from documentation rather than read from the data
- The footer says "reviewed" but no findings were recorded anywhere
- An answer combining governed and raw sources is labeled Tier 2
- The population line does not match the question spec
- A Low-confidence, leadership-bound number is going out without human sign-off
- A footer is being attached to a yes/no about whether a column or table exists

## Verification

- [ ] Footer is present on the delivered answer
- [ ] Source tier reflects the lowest tier touched
- [ ] Confidence follows the stated criteria, not the desired outcome
- [ ] Freshness is the maximum date observed in the result data
- [ ] Owner is named
- [ ] Open assumptions from `question-intake` are carried through, not dropped
- [ ] Unresolved advisory findings from review appear as caveats
