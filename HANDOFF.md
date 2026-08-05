# Handoff — 2026-08-04

**Project:** Vibe Analytics workshop + `analytics-skills` repo
**Conference:** 2026-09-29 · **Materials due:** 2026-09-16 · **Dry run must finish by:** 2026-09-12
**Repo:** https://github.com/RobStilson/analytics-skills (public)

Adapted from the `handoff` skill (mattpocock/skills): that skill writes to the OS
temp directory, but this container is wiped between sessions, so the handoff is
committed to the repo instead. Reference-only — artifacts are pointed at, not
summarized.

---

## FIRST: the repo is out of sync

GitHub is at `b8feb47`, **19 commits behind** the working state. Everything in
`references/`, `workshop/`, `check_setup.py`, `requirements.txt`, and the eval
runner fixes exists locally and in overlay zips, but has not been pushed.

**Do this before anything else:** apply the latest overlay, `git add -A`, commit,
push. Until that happens a new session must reconstruct from chat history instead
of cloning.

The agent CAN clone the public repo directly — no upload needed once it is current.

---

## Read these first

| Path | Why |
|---|---|
| `README.md` | Pack overview, three failure modes, honest status |
| `warehouse/facilitator/GROUND_TRUTH.md` | Answer key, verified figures. **Never distribute pre-session.** |
| `references/analysis-patterns.md` | Methods layer — five patterns, all SQL executed |
| `references/domain-doc-template.md` | The 45-minute BUILD-block artifact |
| `workshop/README.md` | Deck sources, and what must NOT run live |

---

## State

**Done:** 11 skills · synthetic DuckDB warehouse (44 tables, 11 engineered traps,
all verified) · 29 evals across 6 slices with an offline drift verifier ·
domain-doc template plus a deliberately incomplete worked example ·
analysis-patterns · 16-slide deck (generated, not hand-edited) · `check_setup.py`
· parallelised eval runner.

**Not done:** the full ablation has never completed. No participant materials
(pre-work email, worksheet). No dry run. `eval-writing-guide.md` unwritten.

**Status:** partially measured. One slice ran cleanly; the full run had a known
confound (below) and the corrected version has not been executed.

---

## The measurement so far

| Run | Skills loaded | Result |
|---|---|---|
| `provenance-footer` only | 1 | **+50 pts** (3/8 → 7/8) |
| All six slices | 6 | **−9 pts**, negative tests 93% → 73% |

The runner was injecting **all six SKILL.md bodies into every question** — 11,253
tokens against a 17-token ask, roughly 600x. That measures context dilution, not
skill quality, and the over-firing visible in the negative tests is the expected
consequence. 12 of 28 evals flipped by 60+ points in both directions; only 11
held steady.

Fixed: skills mode now loads only the skill under test per slice. `--load-all`
preserves the old behavior because the contrast is itself the finding.

**This is the workshop's best material.** The room will assume the hard part is
writing good instructions; the data says it is routing. Deck slides 12–13 carry it.

---

## Decisions worth not relitigating

- **Skills are markdown, not Python.** Solves the mixed-fluency problem.
- **One workflow live**, everything else as take-home reference. Depth over coverage.
- **Reviewer personas stay thin** — stance and evidence bar; they load workflow skills for checklists.
- **Warehouse ships messy with no reference docs.** Writing one is the exercise.
- **Ground truth is generated, never hand-typed.**
- **The full eval suite never runs live.** Maintainer's tool; numbers go on slides beforehand.

---

## The failure mode this project keeps hitting

Fabricated-but-plausible numbers. **Six occurrences**, every one caught only by
executing something:

1. An invented performance-tier table in the facilitator answer key
2. A wrong department-drop figure
3. A correct figure (2,008) quoted where the filter made 1,668 right
4. A distributions example implying skew in symmetric synthetic data
5. A `0/0` eval result written to disk and reported as a 0% score
6. A 12s/run time estimate, invented, off by ~8x — cost Rob a 2.5-hour wait

**Standing rule: run the query. Never type a figure from memory, including into
documentation that looks reviewed.** Six for six, same cause.

---

## Next session

1. **Push the repo.** Little else works well until this is done.
2. **Run the corrected ablation:** `--repeats 3 --workers 16`, both modes, ~20
   min total. Update deck slides 12–13 with a number worth quoting. Consider a
   third arm with `--load-all` — that contrast is the strongest slide.
3. **Participant materials** — pre-work email (must include `check_setup.py` with
   a two-week lead time), BUILD-block worksheet, failure-demo script.
4. `references/eval-writing-guide.md` if time allows. Not load-bearing.

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
| `skill-freshness-check` | First. Docs have drifted repeatedly — the meta router lost track of two personas within an hour of adding them. |
| `correction-harvesting` | Any time Rob corrects an output. Capture verbatim, then fix. |
| `uncertainty-reporting` | Reading ablation results. It applies to our own numbers. |
| `causal-claim-guardrail` | Any claim about what the skills caused. |

---

## Setup failures seen in the wild

All hit during real sessions, all now handled by `check_setup.py`:

1. **`pip` and `python` were different interpreters.** Packages went to a
   Microsoft Store Python 3.9 while scripts ran under 3.14. The traceback's
   `~~~~^^` markers gave it away — 3.11+ only. Always `python -m pip install`.
2. **A missing dependency produced a raw traceback** from five entry points.
3. **Script run from the wrong directory** — internal paths anchor to the script,
   but `--compare` took shell-relative arguments. Fixed.
4. **A typo in `--skill` silently ran nothing** and wrote a results file.

If the repo's author hit four environment failures in a week, participants
arriving cold will hit more. Pre-work must include `check_setup.py` with a
two-week lead time.

---

## Environment

Container resets between sessions. `/home/claude/analytics-skills` does not
persist. Once GitHub is current, resume by cloning it and reading this file.

DuckDB is not preinstalled: `pip install -r requirements.txt`.

Verification, all offline and free:

```bash
python check_setup.py                 # environment, warehouse integrity, key
cd evals && python verify.py          # 112 pinned values, 29 evals, 6 negative
python references/verify_sql.py       # every SQL block in references/
```

Rebuild the warehouse only if missing or corrupt: `cd warehouse && python
build_warehouse.py` (fixed seed, reproducible).

No credentials are stored in this repo, and none should be.
