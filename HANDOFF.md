# Handoff — 2026-07-30

**Project:** Vibe Analytics workshop + `analytics-skills` repo
**Conference:** 2026-09-29 · **Hard deadline:** 2026-09-12 (pre-work must ship)
**Repo:** https://github.com/RobStilson/analytics-skills

Adapted from the `handoff` skill (mattpocock/skills). That skill writes to the OS
temp directory; here the handoff is committed to the repo instead, because this
container is wiped between sessions and temp would not survive. Per the skill's
reference-only rule, artifacts below are pointed at, not summarized.

---

## Read these first

| Path | Why |
|---|---|
| `README.md` | Pack overview, the three failure modes, honest status |
| `warehouse/facilitator/GROUND_TRUTH.md` | Answer key — every trap, verified figures. **Do not distribute pre-session.** |
| `evals/README.md` | Eval design, what's tested vs. untested |
| `references/EXAMPLE-headcount.md` | The BUILD-block exercise |

---

## State

**Complete:** 11 skills · synthetic DuckDB warehouse (44 tables, 11 engineered
traps, verified) · 28 evals across 6 slices with an offline drift verifier ·
domain-doc template + deliberately incomplete worked example.

**Not done:** the ablation has never been run — `evals/run_evals.py` has not
executed a single API call. `references/analysis-patterns.md` unwritten. No
participant materials (pre-work, slides, worksheets). No dry run.

**Status line for the repo, unchanged:** testable, not tested.

---

## Decisions worth not relitigating

- **Skills are markdown, not Python.** Solves the mixed-fluency problem — a SQL
  analyst and a senior DS both produce a real artifact in 90 minutes.
- **One workflow live, the rest as post-workshop reference.** Depth over coverage.
- **Reviewer personas stay thin.** `sql-reviewer` and `methodologist` carry the
  stance and evidence bar; they load the workflow skills for the checklists.
- **Warehouse ships deliberately messy, with no reference docs.** Writing one is
  the exercise. A clean warehouse teaches nothing.
- **Ground truth is generated, never hand-typed.** See below.

---

## The failure mode this project keeps hitting

Fabricated-but-plausible numbers. Three occurrences so far, all caught only by
executing queries:

1. A facilitator answer key with an **entirely invented** performance-tier table
2. A department-drop figure that was wrong
3. A correct figure (2,008) quoted next to a query whose filter made 1,668 the
   right answer — right number, wrong context

This is the pack's own thesis landing on its authors, repeatedly. It is the
single best story for the workshop, and it is worth telling on stage.

**Standing rule for future sessions: run the query. Never type a figure from
memory, including into documentation that looks reviewed.**

---

## Next session

1. `references/analysis-patterns.md` — retention curves, rate decomposition,
   cohort construction, funnel analysis. Biggest remaining content gap and the
   most reusable thing in the pack.
2. Participant materials — pre-work email, failure-demo script, BUILD worksheet.
3. Slides.

Blocked on Rob: run the ablation (`--mode baseline`, then `--mode skills`,
then `--compare`). ~$2–5 in tokens. Expect bugs; it has never run.

Open question for Rob: does the conference have a materials deadline? If slides
are due 2–4 weeks ahead, the 2026-09-12 freeze moves earlier.

---

## Suggested skills for the next agent

| Skill | When |
|---|---|
| `skill-freshness-check` | First. Docs have already drifted twice — the meta router lost track of two personas within an hour of their being added. |
| `correction-harvesting` | Any time Rob corrects an output. Capture verbatim, then fix. |
| `causal-claim-guardrail` | Drafting `analysis-patterns.md`, especially retention and cohort content. |
| `uncertainty-reporting` | Same. |
| `writing-great-skills` (mattpocock) | If authoring new SKILL.md files. |

---

## Environment

Container resets between sessions. `/home/claude/analytics-skills` does not
persist. To resume: Rob uploads the repo (or points at GitHub), and the agent
reads this file first.

DuckDB is not preinstalled — `pip install duckdb --break-system-packages`.
Rebuild the warehouse from the pinned seed before touching evals:
`cd warehouse && python build_warehouse.py`, then `cd evals && python verify.py`
(expect: 112 pinned values match, 28 evals, 5 negative).

No credentials are stored anywhere in this repo, and none should be.
