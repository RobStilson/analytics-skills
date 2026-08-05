# Analytics Skills

**Production-grade analytics skills for AI agents.**

Skills encode the judgment senior analysts apply before a number leaves their
hands — which source is canonical, what the denominator should be, when a
correlation may not be described as an effect. This pack packages that judgment
so agents apply it consistently instead of producing fluent, plausible, wrong
answers.

```
 DEFINE          BUILD          VALIDATE       OPERATIONALIZE    MONITOR
┌──────┐      ┌──────┐       ┌──────┐        ┌──────┐         ┌──────┐
│ Ask  │ ───▶ │ Find │  ───▶ │Check │  ───▶  │Ship  │  ───▶   │Watch │
│ Spec │      │Query │       │Doubt │        │Trace │         │Repair│
└──────┘      └──────┘       └──────┘        └──────┘         └──────┘
                                   └──────── COMPOUND ◀───────────┘
```

## Why analytics needs its own pack

Coding agents worked first for a structural reason. Coding is an open-ended
solution space where creativity is rewarded and tests, types, and compilers
provide natural guardrails against hallucination.

Analytics is the opposite. There is usually exactly one correct answer, from
exactly one correct source, and no deterministic way to prove you found it. The
query runs cleanly either way. **Data is not software**, and skills written for
software development do not transfer.

Three failure modes account for most wrong answers, and every skill here attacks
at least one:

1. **Entity ambiguity** — the agent cannot map a concept to the single correct
   table, column, and definition among many plausible candidates
2. **Staleness** — definitions and schemas change; docs and agent knowledge rot
3. **Retrieval failure** — the right answer is documented and the agent does not find it

Stacked on top is the one none of them fully catches: **silent wrongness**, where
the answer is wrong, looks plausible, and is used without objection.

## The skills

| Stage | Skill | What it does |
|---|---|---|
| Meta | [`using-analytics-skills`](skills/using-analytics-skills/SKILL.md) | Routes work to the right skill; defines shared operating rules |
| Define | [`question-intake`](skills/question-intake/SKILL.md) | Turns a vague request into a confirmed question spec before any SQL |
| Build | [`warehouse-navigation`](skills/warehouse-navigation/SKILL.md) | Source-tier ladder and entity disambiguation |
| Validate | [`adversarial-sql-review`](skills/adversarial-sql-review/SKILL.md) | Hostile checklist pass before any number is reported |
| Validate | [`sql-reviewer`](skills/sql-reviewer/SKILL.md) | The independent reviewer's stance and evidence bar |
| Validate | [`causal-claim-guardrail`](skills/causal-claim-guardrail/SKILL.md) | Licenses causal language by design, not by correlation size |
| Validate | [`uncertainty-reporting`](skills/uncertainty-reporting/SKILL.md) | Denominators, intervals, small-cell suppression, multiplicity |
| Operationalize | [`provenance-footer`](skills/provenance-footer/SKILL.md) | Standard footer so readers can judge what to trust |
| Monitor | [`skill-freshness-check`](skills/skill-freshness-check/SKILL.md) | Detects and repairs drift between docs and the data model |
| Compound | [`correction-harvesting`](skills/correction-harvesting/SKILL.md) | Turns every stakeholder correction into a doc fix and an eval |

### Reviewer personas

| Persona | Asks | Loads |
|---|---|---|
| [`sql-reviewer`](skills/sql-reviewer/SKILL.md) | Did the query compute what you intended? | `adversarial-sql-review` |
| [`methodologist`](skills/methodologist/SKILL.md) | Does what you measured support the claim you are making? | `causal-claim-guardrail`, `uncertainty-reporting` |
| `stakeholder-translator` *(planned)* | Will the reader understand it as you intend? | — |

Reviewer personas are thin by design: they carry the stance, the evidence bar,
and the output format, and load the workflow skills for the actual checks. The
checklist lives in one place.

## Skill anatomy

Every skill follows the same shape:

```
┌──────────────────────────────────────────────────┐
│  SKILL.md                                        │
│  ┌─ Frontmatter ────────────────────────────┐    │
│  │ name, version                            │    │
│  │ description: IF … THEN invoke.           │    │
│  │              DO NOT invoke for …         │    │
│  └──────────────────────────────────────────┘    │
│  Overview        → why this failure mode matters │
│  When to Use     → routing triggers              │
│  Process         → numbered, imperative steps    │
│  Rationalizations→ excuses + rebuttals           │
│  Red Flags       → signs something is wrong      │
│  Verification    → evidence required to proceed  │
└──────────────────────────────────────────────────┘
```

Design choices worth naming:

- **Routing triggers in the description.** `IF … THEN … DO NOT …` phrasing, because
  under-triggering is the more common failure than over-triggering.
- **Anti-rationalization tables.** Agents skip steps under predictable pressure.
  Each skill pre-rebuts the specific excuses that apply to it.
- **Verification is evidence, not vibes.** "Looks right" never satisfies a
  verification gate.
- **Provenance is mandatory.** Analytics has no compiler, so traceability is the
  substitute for a passing build.

## Setup check

```bash
python check_setup.py
```

Verifies the interpreter, packages, warehouse integrity, and API key, and prints
the exact fix command for anything that fails. It catches the two failures that
waste the most time: a `pip` that installs into a different Python than the one
running your scripts (common on Windows), and a `.duckdb` file truncated in
transfer.

## The warehouse

`warehouse/` holds a synthetic people-analytics warehouse for testing these
skills: 44 tables, ~5,300 workers, five years of history, one DuckDB file with no
server or credentials. It is deliberately messy — eleven failure modes are
engineered in, including a leadership program whose **true causal effect is
exactly zero** but which shows a 7-point attrition gap from selection alone.

```bash
cd warehouse && python build_warehouse.py    # reproducible, fixed seed
```

`warehouse/README.md` orients participants. `warehouse/facilitator/GROUND_TRUTH.md`
is the answer key — **don't hand that out before a session.**

## Scope and assumptions

- **Domain:** examples are workforce/HR (headcount, attrition, compensation,
  survey data). The process content is domain-general; the examples are not.
  Contributions in other domains are welcome — see `CONTRIBUTING.md`.
- **Semantic layer:** skills assume one may not exist and degrade gracefully.
  If you have one, Tier 1 of the source ladder applies; if not, the ladder starts at Tier 2.
- **SQL:** warehouse-agnostic ANSI SQL in the prose. Runnable examples target DuckDB.

## Evals

29 evals across six slices, pinned to the seeded warehouse. Ground truth is
generated from the database, never hand-typed.

Full ablation on claude-sonnet-5: **56% → 84%**, all six slices positive.
Treated as 29 paired observations, mean +28.2 pts, 95% CI +12.0 to +44.3.

Two things belong with that number. Negative tests fell 87% → 70% — the skills
over-fire, and that cost is real. And five runs died on the agent turn budget,
four of them in the slice reporting the largest gain, so the estimate is
optimistic. Under the worst-case assumption the effect is +22.8. See
`evals/README.md`.

```bash
cd evals && python verify.py          # offline drift check, no API key
```

18% of the set are **negative tests** — evals the skill should NOT change. A
causal guardrail that strips causal language from a randomized rollout has
stopped being a guardrail and become an obstacle, and only a negative test
catches that.

## Status

**v0.1.0, measured once.** One clean full ablation, single model, single
session. The effect is positive and survives sensitivity analysis, but a single
run on a synthetic warehouse by the skills' own author is the weakest form of
evidence that counts as evidence at all. Independent evals are worth more than
another skill.

Two weaknesses worth stating plainly. The grader is an LLM judging free text,
and its agreement with human labels has not been measured. And the evals were
written by the same author as the skills, which is the weakest form of
validation available — evals from someone who did not write the skills are worth
more than another slice from the author.

## Prior art

This pack draws directly on three sources, and the debt is worth stating plainly:

- **[agent-skills](https://github.com/addyosmani/agent-skills)** (Addy Osmani) —
  the skill anatomy, the anti-rationalization pattern, and the lifecycle-command structure
- **[Compound Engineering](https://every.to/guides/compound-engineering)** (Every) —
  the plan/work/review/**compound** loop, and the argument that the fourth step is
  where the gains actually accumulate
- **[How Anthropic enables self-service data analytics with Claude](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)** —
  the three failure modes, the source-tier ladder, the pairwise knowledge/runbook
  skill structure, and the provenance footer

The contribution here is the translation to analytics, and the two skills that
have no software-engineering analogue: `causal-claim-guardrail` and
`uncertainty-reporting`.

## License

MIT.
