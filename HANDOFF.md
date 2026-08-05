# Handoff — 2026-08-05

**Project:** Vibe Analytics workshop + `analytics-skills` repo
**Conference:** 2026-09-29 · **Materials due:** 2026-09-16 · **Dry run must finish by:** 2026-09-12
**Repo:** https://github.com/RobStilson/analytics-skills (public, current)

Adapted from the `handoff` skill (mattpocock/skills): that skill writes to the OS
temp directory, but the agent's container is wiped between sessions, so the
handoff lives in the repo. Reference-only — artifacts are pointed at, not
summarized.

---

## Start here

The repo is current. Clone it and read this file, then `README.md`.

```bash
git clone https://github.com/RobStilson/analytics-skills.git
cd analytics-skills && pip install -r requirements.txt
python check_setup.py                  # environment + warehouse + API key
cd evals && python verify.py           # 112 pinned values, 29 evals, 6 negative
cd .. && python references/verify_sql.py   # every SQL block in references/
```

All three should pass. If `verify.py` fails, the warehouse changed — rebuild from
the pinned seed with `cd warehouse && python build_warehouse.py`.

| Path | Why |
|---|---|
| `README.md` | Pack overview, three failure modes, measured result |
| `evals/README.md` | The ablation numbers and every caveat that qualifies them |
| `warehouse/facilitator/GROUND_TRUTH.md` | Answer key. **Never distribute pre-session.** |
| `references/domain-doc-template.md` | The 45-minute BUILD-block artifact |
| `workshop/README.md` | Deck sources, and what must NOT run live |

---

## State

**Done:** 11 skills · synthetic DuckDB warehouse (44 tables, 11 engineered traps)
· 29 evals across 6 slices with an offline drift verifier · domain-doc template
plus a deliberately incomplete worked example · analysis-patterns · 16-slide deck
· `check_setup.py` · parallelised eval runner with preflight and fail-fast ·
**one clean full ablation.**

**Not done:** no participant materials (pre-work email, BUILD worksheet, failure-
demo script). No dry run. `prv-04` over-firing unfixed. `--load-all` arm not run.
`eval-writing-guide.md` unwritten.

**Status:** measured once. The effect is real and survives sensitivity analysis,
but it is a single session on a synthetic warehouse using the authors' own evals.

---

## The measured result

Full ablation, claude-sonnet-5, per-slice loading, 3 repeats, 93 assertions both
sides. **56% → 84%.** All six slices positive (+13 to +50).

As 29 paired eval-level observations: mean **+28.2**, median **+27.8**, 95% CI
**+12.0 to +44.3**, sign test p = 0.009.

Three caveats that belong with it, all on deck slide 13:

1. **Skills over-fire.** Negative tests fell 87% → 70%, mean −16.7. `prv-04` at
   −67 is the worst: a full provenance footer attached to a schema lookup.
2. **Five runs died on the turn budget, not at random.** Four of five were in
   `uncertainty-reporting`, the highest-gaining slice. Informative censoring —
   the exact pattern `references/analysis-patterns.md` warns about, hit in our
   own measurement.
3. **Sensitivity:** dropping evals with any failed run gives +22.0; assuming
   every lost run scored zero gives +22.8. The defensible headline is
   **"roughly +20 to +28 with a measurable over-firing cost."**

An earlier run showed −9 and was invalid: the runner injected all six SKILL.md
bodies into every question (11,253 tokens against a 17-token ask). Fixed to
per-slice loading. `--load-all` preserves the old behavior, and running it as a
third arm would turn the routing argument into a measurement.

---

## Decisions worth not relitigating

- **Skills are markdown, not Python.** Solves the mixed-fluency problem.
- **One workflow live**, everything else as take-home reference.
- **Reviewer personas stay thin** — stance and evidence bar; they load workflow skills.
- **Warehouse ships messy with no reference docs.** Writing one is the exercise.
- **Ground truth is generated, never hand-typed.**
- **The full eval suite never runs live.** Numbers go on slides beforehand.

---

## The failure mode this project keeps hitting

Fabricated-but-plausible output. **Nine occurrences**, every one caught only by
executing or reading the actual artifact:

1. An invented performance-tier table in the facilitator answer key
2. A wrong department-drop figure
3. A correct figure (2,008) quoted where the filter made 1,668 right
4. A distributions example implying skew in symmetric synthetic data
5. A `0/0` eval result written to disk and reported as a 0% score
6. A 12s/run time estimate, invented, off by ~8x — cost a 2.5-hour wait
7. An empty agent response graded as a legitimate 0/6
8. A `+22` delta computed by totalling 93 baseline assertions against 48 skills
9. A confident root-cause diagnosis built on an 80-char truncated error, wrong

**Standing rule: run the query, read the artifact. Never assert a number or a
diagnosis from memory or inference, including into documentation that looks
reviewed.** Nine for nine, same cause.

---

## Next session, in order

1. **Pre-work email.** Highest value and longest lead. Must include
   `check_setup.py`, a copy-pasteable setup block, and a two-week lead time.
   Four environment failures hit during development — participants arriving cold
   will hit more. Include "add API credit and verify it."
2. **BUILD-block worksheet.** 45 minutes against `references/domain-doc-template.md`.
   Timing, prompts, and what "done" looks like.
3. **Failure-demo script.** Deck slide 8 still describes the before/after rather
   than showing it. Real text now exists in `evals/results/*.json` — `prv-01`
   going 0/4 → 4/4 is the strongest opening available.
4. **Fix `prv-04` over-firing**, then re-run that slice to confirm. ~2 min.
5. **`--load-all` arm.** ~15 min, makes the routing argument concrete.

**Schedule:**

| By | What |
|---|---|
| Sep 5 | All content and slides drafted |
| Sep 8–12 | Dry run, 3–4 people on own laptops. Last chance to change anything. |
| Sep 15 | Pre-work sent |
| Sep 16 | Materials due |
| Sep 17–26 | Rehearse only. Chase missing API keys. |
| Sep 29 | Workshop |

Recruit dry-run participants in August. At least one should be SQL/BI-native
rather than Python-fluent — that is the participant the design most likely fails.

---

## Suggested skills for the next agent

| Skill | When |
|---|---|
| `skill-freshness-check` | First. This file was stale within a day, twice. |
| `correction-harvesting` | Any time Rob corrects an output. Capture verbatim, then fix. |
| `uncertainty-reporting` | Reading ablation results. It applies to our own numbers. |
| `causal-claim-guardrail` | Any claim about what the skills caused. See fabrication 9. |

---

## Setup failures seen in the wild

All hit during real sessions, all now caught by `check_setup.py` or the runner's
preflight:

1. **`pip` and `python` were different interpreters.** Packages went to a
   Microsoft Store Python 3.9 while scripts ran under 3.14. The traceback's
   `~~~~^^` markers gave it away — 3.11+ only. Always `python -m pip install`.
2. **A missing dependency produced a raw traceback** from five entry points.
3. **Script run from the wrong directory.** Internal paths anchor to the script,
   but `--compare` took shell-relative arguments.
4. **A typo in `--skill` silently ran nothing** and wrote a results file.
5. **API credit ran out mid-run**, and 174 doomed requests were issued before
   anyone noticed. Now preflighted and aborted on the first fatal error.

---

## Environment

The agent's container resets between sessions and CAN clone this public repo
directly — no uploads needed.

DuckDB is not preinstalled: `pip install -r requirements.txt`. Rebuild the
warehouse only if missing or corrupt (fixed seed, reproducible).

Eval runs archive prior results with a timestamp rather than overwriting. Do not
`rm results/*.json` before a run — a completed baseline is data, and one was lost
that way.

No credentials are stored in this repo, and none should be.
