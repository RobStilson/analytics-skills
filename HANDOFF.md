# Handoff — 2026-08-03

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
| `references/analysis-patterns.md` | The methods layer — five patterns, all SQL tested |

---

## State

**Complete:** 11 skills · synthetic DuckDB warehouse (44 tables, 11 engineered
traps, verified) · 28 evals across 6 slices with an offline drift verifier ·
domain-doc template + deliberately incomplete worked example.

**Not done:** the ablation has never been run — `evals/run_evals.py` has not
executed a single API call. No participant materials (pre-work, slides,
worksheets). No dry run. `eval-writing-guide.md` and
`analytics-definition-of-done.md` still unwritten.

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
4. A distributions example implying the warehouse showed salary skew, when the
   synthetic data is symmetric (mean 111,460, median 111,500). The doc now says
   so explicitly rather than implying a demonstration it does not make.

This is the pack's own thesis landing on its authors, repeatedly. It is the
single best story for the workshop, and it is worth telling on stage.

**Standing rule for future sessions: run the query. Never type a figure from
memory, including into documentation that looks reviewed.**

---

## Next session

1. **Participant materials** — pre-work email, failure-demo script, BUILD
   worksheet, slides. This is now the critical path.
2. `references/eval-writing-guide.md` if time allows. Not load-bearing for the
   workshop.

Blocked on Rob: run the ablation (`--mode baseline`, then `--mode skills`,
then `--compare`). ~$2–5 in tokens. Expect bugs; it has never run. Do this
before slides are drafted — a small delta changes what the slides claim.

**Schedule (materials due 2026-09-16):**

| By | What |
|---|---|
| Sep 5 | All content and slides drafted |
| Sep 8–12 | Dry run, 3–4 people, own laptops. Last chance to change anything. |
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
(expect: 112 pinned values match, 28 evals, 5 negative). Also run
`python references/verify_sql.py` (expect: PASS) — it executes every SQL block
in the reference docs.

No credentials are stored anywhere in this repo, and none should be.
