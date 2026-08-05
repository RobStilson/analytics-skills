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

## Measured result

Full ablation, claude-sonnet-5, per-slice loading, 3 repeats, 93 assertions on
both sides.

| Slice | Baseline | Skills | Delta |
|---|---|---|---|
| `uncertainty-reporting` | 43% | 93% | **+50** |
| `provenance-footer` | 39% | 82% | **+42** |
| `warehouse-navigation` | 61% | 83% | +23 |
| `question-intake` | 61% | 82% | +21 |
| `adversarial-sql-review` | 54% | 72% | +18 |
| `causal-claim-guardrail` | 74% | 87% | +13 |
| **Total** | **56%** | **84%** | **+28** |

Treated as 29 paired eval-level observations: mean **+28.2**, median **+27.8**,
95% CI **+12.0 to +44.3** — excludes zero. 17 evals improved, 5 worsened, 7 flat
(sign test p = 0.009). Mean and median agreeing means it is not one outlier
carrying the result.

### The three caveats that belong with the number

**Skills over-fire.** Negative tests fell 87% → 70%, mean **−16.7 pts** across
the six. `prv-04` is the worst at −67: `provenance-footer` attaches a full footer
to a schema lookup during iteration. That is a real cost, not noise, and it
partly offsets the gains.

**Five runs died on the turn budget, and not at random.** Four of the five were
in `uncertainty-reporting` — the slice reporting the largest gain. `unc-01`'s
+100 rests on a single surviving run. Losing the runs where the agent worked
hardest is informative censoring, exactly the pattern
`references/analysis-patterns.md` warns about.

**Sensitivity analysis:**

| Restriction | n | Mean | 95% CI |
|---|---|---|---|
| All evals | 29 | +28.2 | +12.0 to +44.3 |
| Excluding evals with any failed run | 25 | +22.0 | +5.3 to +38.7 |
| Assuming every lost run scored 0 | 29 | +22.8 | +8.0 to +37.6 |

The finding survives every restriction, but the honest headline is **"roughly
+20 to +28 points, with a measurable over-firing cost"** rather than +28 flat.

**Four evals regressed:** `prv-04` (−67), `nav-03` (−33), `int-03` (−22),
`rev-01` (−17). Two are negative tests, which is the over-firing showing up
again.

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

### A harness bug worth knowing about

The first full run scored `warehouse-navigation` at zero across nav-01 to nav-04,
nine runs, perfectly consistent. That was not the skill failing. The agent loop
exhausted its turn budget while still issuing SQL, so the final message carried
only tool-use blocks and no text. `call_agent` returned an empty string, and the
grader scored it as a legitimate 0.

The instrument fabricated a data point, in a harness built to detect exactly that.

Fixed three ways:
- On turn exhaustion, one final call without tools asks the agent to answer with
  what it has
- An empty response now raises rather than being graded, and the run is excluded
  from scoring and reported
- `--max-turns` default raised 6 → 10, since skills that add process steps need
  more budget than a bare agent

**Any result produced before this fix understates skills mode.** Re-run before
quoting anything.

### Before a run

```bash
python ../check_setup.py     # makes one live API call — catches credit/key problems
```

`run_evals.py` also preflights with a single tiny call and aborts on
account-level errors (credit exhausted, bad key, disabled account) rather than
issuing hundreds of doomed requests. Completed results are archived with a
timestamp rather than overwritten, so a failed run cannot destroy a good one.

Do **not** `rm results/*.json` before a run. The archiving handles it, and a
completed baseline is data worth keeping.

### Run times

The full suite is a maintainer's tool, not a workshop activity. It fans out
across `--workers` threads (default 8) and prints an estimate before starting.

| Command | Runs | Rough time |
|---|---|---|
| `--skill provenance-footer` | 4 | under a minute |
| `--mode baseline` | 29 | 4-7 min |
| `--mode baseline --repeats 3` | 87 | 11-22 min |
| Both modes, `--repeats 3` | 174 | 22-45 min |

Sequentially, that last row took **over 2.5 hours**. If a run is taking that
long, it is not parallelised — check that `--workers` appears in `--help`.

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
