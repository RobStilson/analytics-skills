# Contributing

Contributions are welcome, particularly **evals** and **analysis patterns** —
both are currently thinner than the process skills.

## What makes a good skill here

A skill in this pack should be:

- **Specific** — actionable steps, not general advice. "Consider data quality"
  is not a skill; "confirm the as-of predicate exists before counting an
  effective-dated table" is.
- **Verifiable** — the Verification section must require evidence, not judgment.
  If a reviewer cannot tell whether the skill was followed, tighten it.
- **Battle-tested** — based on a mistake you have actually seen made, ideally
  more than once. The Gotchas and Red Flags sections are where field experience
  lives, and they are the sections a model cannot generate.
- **Minimal** — only what the agent needs. Length is not thoroughness, and
  over-long docs retrieve worse.

## Skill anatomy

Follow the existing shape:

```markdown
---
name: lowercase-hyphen-name
version: 0.1.0
description: "IF [trigger conditions] — THEN invoke this skill. Use it for
  [specific contexts]. DO NOT invoke for [adjacent cases]."
---

# Title

## Overview          — why this failure mode matters and what it costs
## When to Use       — routing triggers, as a table where possible
## Process           — numbered, imperative steps
## Rationalizations  — excuse | rebuttal table
## Red Flags         — signs something is wrong
## Verification      — checklist of required evidence
```

Notes on the frontmatter description: it is the primary triggering mechanism and
the only part always in context. Under-triggering is a more common failure than
over-triggering, so lean toward explicit `IF … THEN …` phrasing and include the
`DO NOT` clause to bound it.

## Domain examples

Current examples are workforce/HR. Skills for other domains are welcome. If you
contribute one:

- Keep the **process** domain-general
- Put domain-specific gotchas in tables, clearly labeled, so they can be swapped
- Do not assume a semantic layer exists; degrade gracefully to governed tables
- Use warehouse-agnostic ANSI SQL in prose; DuckDB in runnable examples

## Evals matter more than skills right now

The pack has nine skills and no eval coverage. A skill without an eval is an
assertion. If you use these and find a case where a skill helped — or failed to —
that case is worth more than another skill file.

Eval format:

```json
{
  "skill_name": "causal-claim-guardrail",
  "evals": [
    {
      "id": 1,
      "prompt": "The realistic user request",
      "expected_output": "What a correct response does",
      "assertions": ["Objectively checkable claims about the output"]
    }
  ]
}
```

Pin ground truth so it cannot drift: anchor to a snapshot date, write against a
stable fact table, or grade the query rather than the number.

Where you can measure a change, put the before/after delta in the PR description.
It keeps "I improved the docs" honest, and it catches the surprisingly common
case where a well-intentioned addition makes things worse. Negative results are
welcome and worth recording.

## Scope boundaries

Out of scope for this pack:

- Pipeline engineering, orchestration, and schema migration
- Access provisioning and governance policy
- BI tool configuration
- Anything that determines thresholds for protected-class analysis — those route
  to organizational governance, and this repo should not encode a number

## PR expectations

- One skill or one coherent change per PR
- If you change a skill's behavior, say what eval demonstrates it
- If you add a domain doc, name an owner
