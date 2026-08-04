# Evals

29 evals across six skill slices, pinned to a fixed warehouse seed.

Without these, every claim this pack makes about improving accuracy is an
assertion. With them, it is a measurement — or a refutation, which is equally
useful and considerably more likely on a first run.

## Layout

```
evals/
├── make_ground_truth.py     generates ground_truth.json FROM the warehouse
├── ground_truth.json        112 pinned values — do not hand-edit
├── make_evals.py            writes the slices, interpolating ground truth
├── verify.py                offline drift check — no API key, wire into CI
├── run_evals.py             the ablation runner — UNTESTED, see below
└── <skill>/evals.json       one slice per skill
```

| Slice | Evals | Negative |
|---|---|---|
| `warehouse-navigation` | 6 | 1 |
| `uncertainty-reporting` | 6 | 1 |
| `causal-claim-guardrail` | 5 | 1 |
| `question-intake` | 4 | 1 |
| `adversarial-sql-review` | 4 | 1 |
| `provenance-footer` | 4 | 1 |

## No figure is hand-typed

`ground_truth.json` is generated from the warehouse. `make_evals.py`
interpolates from it. `verify.py` regenerates and diffs.

This is not ceremony. Hand-typed figures are how fabricated numbers reach
documentation that looks reviewed — including, during the drafting of this repo,
a facilitator answer key whose performance-tier table was invented wholesale and
looked entirely plausible until the numbers were run.

## First measured result

One slice, `provenance-footer`, run on claude-sonnet-5:

| | baseline | skills | delta |
|---|---|---|---|
| Assertions passed | 3/8 (38%) | 7/8 (88%) | **+50 pts** |

Read that with the caution it deserves: **8 assertions, one slice, one run.**
A 50-point delta is four assertions changing. Directional, not conclusive.

The more useful detail is that `prv-03` **regressed**, 2/2 to 1/2. Baseline read
the freshness date from the data unaided; with the skill loaded it did not. That
is a candidate defect in the skill — plausibly the footer template inviting a
convention-filled field instead of a lookup — and it surfaced in the first eight
assertions ever run.

A headline delta that hides a regression is the failure this pack exists to
prevent. Report both.

## Negative tests are 21% of the set, deliberately

A skill that fires on everything is indistinguishable from a skill that works.
Each slice carries at least one eval the skill should NOT change:

| Eval | Tests that the skill does not |
|---|---|
| `int-03` | interrogate an already-specified question |
| `unc-06` | attach an interval to a complete-population count |
| `cau-05` | strip causal language from a genuine randomized design |
| `rev-04` | manufacture findings on a correct query |
| `nav-06` | invent data for an empty table |
| `prv-04` | footer a schema lookup during iteration |

`cau-05` is the important one. A causal guardrail that blocks a randomized
rollout has stopped being a guardrail and become an obstacle.

`prv-04` was added after the first real run: `provenance-footer` originally had
no negative test, so its ablation reported `0/0` on over-firing and could not
have detected it. Every slice now has at least one.

## Running

```bash
pip install -r ../requirements.txt
```

**Drift check** — offline, free, fast:

```bash
python make_ground_truth.py    # only after rebuilding the warehouse
python verify.py               # exit 1 on drift
```

`verify.py` catches two failure modes: the warehouse no longer producing the
figures the evals assert, and an eval quoting a number that traces to nothing.
Both were confirmed to fire by deliberately corrupting the ground truth.

**The ablation** — needs `ANTHROPIC_API_KEY`:

Defaults to `claude-sonnet-5` for both agent and grader. Override with
`--agent-model` / `--grader-model`. Model IDs change; verify against the
[models docs](https://platform.claude.com/docs/en/about-claude/models/overview)
before a run that matters.

A stronger agent may pass more *baseline* evals unaided, compressing the
measured delta. That is a real result about where skills add value for a given
model, not a flaw in the measurement — report it rather than switching to a
weaker model to manufacture a bigger number.

```bash
python run_evals.py --mode baseline    # skills off
python run_evals.py --mode skills      # skills on
python run_evals.py --compare results/baseline.json results/skills.json
```

## run_evals.py is untested

It has never been executed against a live API — it was written without
credentials available. The syntax parses and `--compare` works on fixtures; the
agent loop and grader path have not run once. Expect to debug it. Treat the
structure as the contribution and the specifics as a starting point.

`verify.py`, by contrast, is tested, including its failure path.

## Two known weaknesses

**The grader is an LLM judging free text.** Assertions are written to be
objectively checkable, but "the response flags the estimate as unstable" still
requires judgment. Grader agreement has not been measured against human labels.
Treat single-run deltas under about 10 points as noise until it has, and treat
any single-slice result as directional regardless of size.

**The evals were written by the same author as the skills.** They test what the
skills were built to do, which is the weakest form of validation available.
Evals contributed by someone who did not write the skills are worth more than
another slice from the author.

## Contributing

See `../CONTRIBUTING.md`. Two rules matter most:

1. **Pin ground truth** — anchor to the seeded warehouse, or grade the query
   rather than the number.
2. **Verify the eval discriminates.** An eval that passes with and without the
   skill tests nothing. Run the baseline.
