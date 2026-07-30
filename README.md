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

## Scope and assumptions

- **Domain:** examples are workforce/HR (headcount, attrition, compensation,
  survey data). The process content is domain-general; the examples are not.
  Contributions in other domains are welcome — see `CONTRIBUTING.md`.
- **Semantic layer:** skills assume one may not exist and degrade gracefully.
  If you have one, Tier 1 of the source ladder applies; if not, the ladder starts at Tier 2.
- **SQL:** warehouse-agnostic ANSI SQL in the prose. Runnable examples target DuckDB.

## Status

Early. These are drafted from published practice and field experience, and have
not yet been benchmarked against an eval set. Treat version 0.1.0 as a starting
point to fork and adapt to your own data model, not a validated artifact.

The `evals/` directory is where that changes. If you use these skills, contributing
evals is more valuable than contributing more skills.

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
