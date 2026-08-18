# Handoff — 2026-08-11 (end of day)

**Project:** Vibe Analytics workshop + `analytics-skills` repo
**Conference:** 2026-09-29 · **Materials due:** 2026-09-16 · **Dry run:** Sep 8–12
**Repo:** https://github.com/RobStilson/analytics-skills (public)

---

## FIRST: two commits not yet pushed

GitHub is at `739c562`. Two commits with the facilitator walkthrough and
reference doc materials are local only:

| Commit | What |
|---|---|
| `eaefe68` | Compensation reference doc + walkthrough |
| `52c3270` | All three domain walkthroughs + attrition/engagement reference docs |

These go to `warehouse/facilitator/` — answer-key material, correctly
quarantined from participants. Push:

```powershell
cd "C:\Agentic AI\Skills\analytics-skills"
git add warehouse/facilitator/
git commit -m "Add complete facilitator safety net: all three domain walkthroughs and reference docs"
git push
```

---

## What was built today

### Facilitator walkthrough materials (the big deliverable)

Three complete step-by-step query sequences, one per workshop domain, for
unsticking a stuck participant during the Build block. Each follows the same
structure: numbered queries in discovery order, "what they should notice" and
"if they don't, say this" at each step, and a ranked summary of discoverable
Gotchas at the end.

| Domain | Reference doc | Walkthrough | Queries | All verified |
|---|---|---|---|---|
| Attrition | `warehouse/facilitator/attrition.md` | `attrition-walkthrough.md` | 8 | ✅ |
| Compensation | `warehouse/facilitator/compensation.md` | `compensation-walkthrough.md` | 7 | ✅ |
| Engagement | `warehouse/facilitator/engagement.md` | `engagement-walkthrough.md` | 7 | ✅ |

Plus `GROUND_TRUTH.md` (already there). Seven facilitator files total.

### The Engagement domain was walked through end-to-end as a participant

A full roleplay of the workshop from Define through Ablation, with Rob as a
participant. Findings that matter for the real workshop:

- **The ablation scored 2/2 baseline and 2/2 with-doc — a +0 delta** that
  hides the most interesting result: the two responses reached **opposite
  conclusions** about whether engagement improved (baseline said no, with-doc
  said yes) because they used different methodologies, items, and populations.
  Both passed the eval because the assertions measured process transparency,
  not methodological correctness.
- **This is a better teaching moment than a clean +50.** The reference doc
  absolutely changed the answer — it just didn't show up in the score. A
  third assertion (e.g. "uses Top Box scoring") would have caught it. That's
  correction harvesting in action.
- **The Define block worked well** — Rob's spec was sophisticated (Top Box
  scoring for both scale lengths, 3-point threshold, ENG items only) and the
  open-assumptions prompt surfaced real choices.
- **The Validate prediction was half right** — he predicted PASS on "states
  items" (correct) and FAIL on "addresses scale consistency" (wrong — baseline
  caught the scale change on its own). Sonnet 5 is good enough to notice
  `scale_max` without being told. That's a real finding about where skills
  add value for a capable model.

### Other materials built today

- **Printable data dictionary** (`workshop/data-dictionary.html` + `.pdf`) —
  every table, column, row count, categorical value, and date range extracted
  from the database. Replaces the DuckDB CLI adventure that consumed 20 minutes
  of a prior session fighting file locks, PATH issues, and smart-quote parser
  errors. The empty-table list was verified after a first draft fabricated 13
  of 28 table names from memory (eleventh fabrication in the project).
- **Full facilitator guide** (`workshop/facilitator-guide.md`) — minute-by-
  minute script for all 8 blocks, every command in both Windows and Mac/Linux,
  error lookup table for the ablation script, emergency procedures, quick-
  reference tables for every file participants touch.
- **Dry-run runbook** (`workshop/dry-run-runbook.md`) — five-part operational
  sequence: pre-session smoke test (including run_my_ablation.py's first-ever
  live API execution, confirmed working), compressed pre-work message, block-
  by-block facilitator notes with specific "watch for" items, a live timing
  log, structured debrief questions, and a priority order for post-dry-run
  fixes.
- **`run_my_ablation.py` smoke test completed** — first live API execution
  ever, worked cleanly. Reference doc auto-detection, preflight, baseline vs
  with-doc comparison all confirmed.
- **Attrition reference doc** (`attrition.md`) built with all SQL verified.
  Gotcha 1's numerator was initially stated as "319 Regular separations" —
  it's 319 all worker types, 241 Regular. Fixed before shipping.

---

## Complete state of the project

**Everything a participant touches is built, verified, and on GitHub:**
- 11 skills (including the `prv-04` over-firing fix)
- Synthetic warehouse (44 tables, 11 engineered traps)
- 29 evals, 6 slices, offline drift verifier
- Three clean ablation arms (baseline 56%, per-slice 83%, load-all 81%)
- Pre-work email, Define/Validate/Build worksheets
- Failure-demo script with real captured transcripts
- Room-scale ablation script (`run_my_ablation.py`)
- Printable data dictionary
- 17-slide deck with real measured numbers
- `check_setup.py`

**Everything a facilitator needs is built and quarantined:**
- `GROUND_TRUTH.md`
- Three complete reference docs (attrition, compensation, engagement)
- Three step-by-step walkthroughs (one per domain)
- Full facilitator guide with minute-by-minute script
- Dry-run runbook

**Status: materials-complete.** What's left is rehearsal and testing against
real people, not more building.

---

## What's left before September 29

| Priority | Item | Status |
|---|---|---|
| 1 | **Push the two pending commits** | Local only — 6 facilitator files |
| 2 | **Send dry-run pre-work to your confirmed volunteers** | People confirmed, pre-work not sent |
| 3 | **Run the dry run (Sep 8–12)** | The runbook is at `workshop/dry-run-runbook.md` |
| 4 | **Fix whatever the dry run surfaces** | Unknown until it happens |
| 5 | **Send the real pre-work email by Sep 15** | Template at `workshop/pre-work-email.md`, needs `[DATE]` and `[Your name]` |
| 6 | **Full timed deck read-through, alone, out loud** | Not yet done |
| 7 | **Print materials** | Data dictionary, 3 worksheets — one copy per participant plus spares |

---

## Decisions made today

- **SQL querying via Python scripts, not DuckDB CLI or VS Code extensions.**
  The CLI had PATH issues, the extension had file locks, and both wasted
  significant session time. The `explore.py` pattern (one file, `read_only=True`,
  change the SQL string) works on every platform with no tooling beyond what
  `requirements.txt` already installs.
- **All facilitator materials quarantined in `warehouse/facilitator/`.** Not in
  `references/`, where participants would see completed docs before discovering
  the Gotchas themselves.
- **Reference doc auto-detection uses an allowlist, not a blocklist.** A
  blocklist approach was tried first and broke immediately — `analysis-patterns.md`
  was silently picked up as a participant's domain doc. An allowlist of the
  three known domain names (`attrition.md`, `compensation.md`, `engagement.md`)
  can't be broken by future files landing in `references/`.

---

## The fabrication log — now eleven

| # | What | Caught by |
|---|---|---|
| 1 | Invented performance-tier table | Running the query |
| 2 | Wrong department-drop figure | Running the query |
| 3 | Correct figure in wrong context | Running the query |
| 4 | Skew example with symmetric data | Running the query |
| 5 | 0/0 result written as 0% score | Reading the output |
| 6 | 12s/run estimate, off by ~8× | The 2.5-hour wait |
| 7 | Empty response graded as legitimate 0/6 | Reading the JSON |
| 8 | +22 delta from mismatched assertion counts | Reading the compare output |
| 9 | Confident diagnosis from truncated error | The full error text |
| 10 | Wording fix in ephemeral clone, silently lost | Checking git status |
| 11 | 13 of 28 empty-table names fabricated | Verification script |

Standing rule, unchanged: **run the query, read the artifact, confirm the
push.** Eleven for eleven, same root cause.

---

## Environment

The agent's container resets between sessions. Clone from GitHub and read
this file first. All verification is offline and free:

```bash
python check_setup.py
cd evals && python verify.py
cd .. && python references/verify_sql.py
```

No credentials are stored in this repo, and none should be.
