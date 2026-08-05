# Handoff — 2026-08-05 (end of day)

**Project:** Vibe Analytics workshop + `analytics-skills` repo
**Conference:** 2026-09-29 · **Materials due:** 2026-09-16 · **Dry run must finish by:** 2026-09-12
**Repo:** https://github.com/RobStilson/analytics-skills (public)

Adapted from the `handoff` skill (mattpocock/skills): that skill writes to the
OS temp directory, but the agent's container is wiped between sessions, so the
handoff lives in the repo. Reference-only — artifacts are pointed at, not
summarized.

---

## FIRST: two files are not yet pushed

GitHub is at `855ad0c`. Two files changed locally today and have not reached
GitHub yet:

| File | What changed |
|---|---|
| `evals/run_evals.py` | Softened the skill-loading-mismatch message from "Not comparable" to a note that a deliberate strategy comparison (like `--load-all` vs per-slice) is exactly the intended use |
| `workshop/build_deck.js` | Added the load-all isolation slide (13B) — three-part finding: accuracy, discipline, efficiency |

Apply and push before doing anything else:

```powershell
cd "C:\Agentic AI\Skills\analytics-skills"
git status          # confirm these are the only two files that differ
git add evals/run_evals.py workshop/build_deck.js
git commit -m "Reapply skill-loading wording fix; add load-all deck slide"
git push
```

**Do not commit the `.pptx`.** It's deliberately gitignored — rebuild it
locally with `cd workshop && node build_deck.js` whenever you need it.

A note on how this gap happened: the wording fix was made in a session-local
clone and handed over as a standalone download, but the clone the deck slide
was later built from was a fresh pull from GitHub — so it didn't carry the
fix forward, and there was no confirmation the standalone download had been
applied. It's fixed and reapplied in this session's final state, but it's
worth flagging as a process risk: **a fix that only exists in an ephemeral
clone or a downloaded file, with no confirmed push, can quietly vanish.** When
in doubt, confirm `git status` shows what's expected before moving on.

---

## Read these first

| Path | Why |
|---|---|
| `README.md` | Pack overview, three failure modes, measured result |
| `evals/README.md` | Ablation numbers and every caveat that qualifies them |
| `warehouse/facilitator/GROUND_TRUTH.md` | Answer key. **Never distribute pre-session.** |
| `workshop/pre-work-email.md` | Send by Sep 15; needs `[DATE]` and `[Your name]` filled in |
| `workshop/build-worksheet.md` | The 45-min BUILD-block companion to the domain-doc template |
| `workshop/failure-demo-script.md` | Facilitator script; two `[PASTE...]` slots need your real captured transcript |
| `workshop/README.md` | Deck sources, and what must NOT run live |

---

## State

**Done:** 11 skills (including the `prv-04` over-firing fix) · synthetic
warehouse (44 tables, 11 traps) · 29 evals, 6 slices, offline drift verifier ·
domain-doc template + worked example · analysis-patterns · 17-slide deck ·
`check_setup.py` · parallelised eval runner with preflight, fail-fast, and
archiving · **three complete, clean ablation arms** (baseline, per-slice
skills, load-all skills) · pre-work email · BUILD worksheet · failure-demo
script.

**Not done:** the demo script's two transcript placeholders are unfilled. No
dry run. `references/eval-writing-guide.md` and
`references/analytics-definition-of-done.md` unwritten (not load-bearing).
Full deck read-through not yet done end-to-end.

**Status:** materials-complete for the repo and facilitator side. What's left
is almost entirely rehearsal and real-people testing, not more building.

---

## The measured results — three arms, fully reconciled

All three ran clean after the `prv-04` fix (0 lost runs in baseline or
per-slice; 4 lost to turn-budget exhaustion in load-all only).

| Comparison | Total | Paired mean | 95% CI |
|---|---|---|---|
| Baseline → per-slice skills | 56% → 83% | +26.3 | +12.5 to +40.2 (excludes zero) |
| Baseline → load-all skills | 56% → 81% | +23.3 | +9.2 to +37.3 (excludes zero) |
| **Per-slice → load-all** (isolation) | 83% → 81% | **−3.1** | **−10.3 to +4.2 (crosses zero)** |

The isolation is the important row. Same skills, same model, same warehouse —
only the loading strategy changed. **Raw task accuracy shows no measurable
difference.** The real cost of loading everything shows up elsewhere:

- **Discipline:** negative-test pass rate, monotonic — 87% (baseline) → 83%
  (per-slice) → 74% (load-all)
- **Efficiency:** 4 runs died on the turn budget under load-all; 0 under
  per-slice or baseline

The honest framing, now on deck slide 13B: *loading everything doesn't break
accuracy, it breaks discipline* — a sharper and more defensible claim than the
original inference (drawn from a broken harness run showing −9) that dilution
tanks accuracy outright.

`prv-04` specifically: pre-fix `[1,1,1]` → post-fix `[3,3,3]`, exactly matching
baseline. Fixed with zero cost to `prv-01`/`prv-02` (stayed at ceiling).

---

## Decisions worth not relitigating

- **Skills are markdown, not Python.** Solves the mixed-fluency problem.
- **One workflow live**, everything else as take-home reference.
- **Reviewer personas stay thin** — stance and evidence bar; load workflow skills.
- **Warehouse ships messy with no reference docs.** Writing one is the exercise.
- **Ground truth is generated, never hand-typed.**
- **The full eval suite never runs live.** Numbers go on slides beforehand.
- **Mean and median can diverge — report both.** They agreed at +28.2/+27.8 in
  one run and split to +26.3/+11.1 in another; don't lead with the mean alone.

---

## The failure mode this project keeps hitting

Fabricated-but-plausible output, or a confident claim asserted without
checking. **Ten occurrences now**, every one caught only by executing or
reading the actual artifact:

1. An invented performance-tier table in the facilitator answer key
2. A wrong department-drop figure
3. A correct figure (2,008) quoted where the filter made 1,668 right
4. A distributions example implying skew in symmetric synthetic data
5. A `0/0` eval result written to disk and reported as a 0% score
6. A 12s/run time estimate, invented, off by ~8x
7. An empty agent response graded as a legitimate 0/6
8. A `+22` delta computed by totalling mismatched assertion counts
9. A confident root-cause diagnosis built on an 80-char truncated error, wrong
10. A wording fix made in an ephemeral clone, handed over as a download with
    no confirmed push, silently absent from the next session's working copy

**Standing rule: run the query, read the artifact, confirm the push. Never
assert a number, a diagnosis, or a file's state from memory or inference.**
Ten for ten, same root cause: substituting a plausible belief for a checked fact.

---

## Next session, in order

1. **Push the two files above.** Nothing else matters until this is done.
2. **Fill the failure-demo script's transcript placeholders** from your own
   `evals/results/baseline.json` and `results/skills.json` (`prv-01`).
3. **Full deck read-through**, start to finish, out loud, timed.
4. **Recruit dry-run participants** (3–4 people, Aug) if not already done — at
   least one SQL/BI-native rather than Python-fluent.
5. `references/eval-writing-guide.md` if time allows. Not load-bearing.

**Schedule:**

| By | What |
|---|---|
| Sep 5 | All content and slides drafted |
| Sep 8–12 | Dry run, 3–4 people on own laptops. Last chance to change anything. |
| Sep 15 | Pre-work sent |
| Sep 16 | Materials due |
| Sep 17–26 | Rehearse only. Chase missing API keys. |
| Sep 29 | Workshop |

---

## Suggested skills for the next agent

| Skill | When |
|---|---|
| `skill-freshness-check` | First. This file has gone stale within a day, twice. |
| `correction-harvesting` | Any time Rob corrects an output. Capture verbatim, then fix. |
| `uncertainty-reporting` | Reading any ablation result — applies to our own numbers. |
| `causal-claim-guardrail` | Any claim about what the skills caused, or what caused a bug. |

---

## Setup failures seen in the wild

All hit during real sessions, all now caught by `check_setup.py` or the
runner's preflight:

1. **`pip` and `python` were different interpreters** (Store Python 3.9 vs 3.14).
2. **A missing dependency produced a raw traceback** from five entry points.
3. **Script run from the wrong directory**; `--compare` took shell-relative args.
4. **A typo in `--skill` silently ran nothing** and wrote a results file.
5. **API credit ran out mid-run**; 174 doomed requests were issued before
   anyone noticed. Now preflighted and aborted on the first fatal error.
6. **`Rename-Item` failed on a path-shaped destination** — use `Move-Item` for
   full-path-to-full-path renames, or pass a bare filename to `Rename-Item`.

---

## Environment

The agent's container resets between sessions and CAN clone this public repo
directly — no uploads needed.

DuckDB is not preinstalled: `pip install -r requirements.txt`. Rebuild the
warehouse only if missing or corrupt (fixed seed, reproducible).

Eval runs archive prior results with a timestamp rather than overwriting. Do
not `rm results/*.json` before a run.

No credentials are stored in this repo, and none should be.
