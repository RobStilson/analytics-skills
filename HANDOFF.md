# Handoff — 2026-09-28 (end of day)

**Project:** Vibe Analytics workshop + `analytics-skills` repo
**Conference:** 2026-10-01 (3 days away)
**Repo:** https://github.com/RobStilson/analytics-skills (public)

---

## What was done today

### Session 1 (continued from 9/25 context)

**Workshop Q&A preparation** — Prepared facilitator-ready answers for:
- Block 7 (correction harvesting): manual trigger → agent executes → detection can be partially automated via scheduled scanning
- Block 8 (GitHub fork/upload flow): participants upload to GitHub, it makes a copy and sets up the PR

**SQL output walkthrough** — Mapped raw `fct_compensation` query output to the Data Dictionary handout column by column, with `.fetchdf()` vs `.fetchall()` guidance.

**Sample outputs reference doc** — Created `workshop/sample-outputs.md`:
every populated table's 5-row sample output using `.fetchdf()`, organized
into domain starting tables, shared tables, and misleading tables. Column
explanations and trap callouts for each.

**Starter queries update** — Updated `workshop/starter-queries.html`:
- Added `.fetchdf()` tip to the how-to box
- Added green "Here's what you'll see" note boxes with sample output after each domain's Query 1
- Added "Shared Tables — What They Look Like" section (5 tables)
- Added "Tables That Look Useful But Will Mislead You" section (4 tables)
- All existing content preserved
- Regenerated `workshop/starter-queries.pdf` (10 pages, 183KB, visually verified)

### Session 2 (this afternoon)

**Engagement domain answer key** — Full set of worked examples for "Has
engagement improved by 5% year over year?", kept local as facilitator
fallback (not pushed to public repo):

| File | Purpose |
|---|---|
| `workshop/EXAMPLE-define-worksheet-engagement.md` | Filled-in Define worksheet — population choices, scale ambiguity, "5% means what?" |
| `workshop/EXAMPLE-build-worksheet-engagement.md` | Filled-in Build worksheet — real query output, both gotchas (scale trap: fake +33% vs actual -3.11pp; row ≠ respondent), Do/Don't SQL pairs |
| `workshop/EXAMPLE-validate-worksheet-engagement.md` | Filled-in Validate worksheet — 3 assertions, eval JSON, predictions (baseline passes 1/3) |
| `workshop/engagement-eval.json` | Pre-built eval for Block 6 ablation demo |

**Key engagement numbers (all verified against the warehouse):**

| Metric | Value |
|---|---|
| Naive raw AVG, April 2024 → April 2025 | 3.23 → 4.30 (+33% — **wrong**, caused by scale change) |
| Normalized, April 2024 → April 2025 | 64.50% → 61.39% (-3.11 pp — **correct**) |
| Normalized, April 2025 → April 2026 | 61.39% → 61.97% (+0.58 pp — modest recovery) |
| Answer to the question | **No** — engagement has not improved by 5 pp YoY |

**Facilitator cheat sheet for Block 5 circulating:**

| Domain | First trap they'll hit | Second trap |
|---|---|---|
| Engagement | Scale 5→7 across waves | Row count ≠ respondent count (6× inflation) |
| Compensation | USD/EUR/SGD mixed in one column | Historical rows mixed with current |
| Attrition | Contingent + interns included | No denominator for rate; must choose headcount definition |

**"What to do Monday" talking points** for Block 7/8 wrap:
1. Pick one repeated question, write a question spec for it
2. Find the table everyone uses, document one gotcha in Do/Don't format
3. Run with and without the doc, show someone the side-by-side

---

## What's on GitHub vs. what's local-only

### On GitHub (public, participants can see)
- `workshop/starter-queries.html` and `.pdf` (updated with sample outputs)
- `workshop/sample-outputs.md`
- `workshop/EXAMPLE-define-worksheet-headcount.md`
- Everything from prior sessions (skills, warehouse, evals, worksheets, etc.)

### Local only (answer key — NOT on GitHub)
- `workshop/EXAMPLE-define-worksheet-engagement.md`
- `workshop/EXAMPLE-build-worksheet-engagement.md`
- `workshop/EXAMPLE-validate-worksheet-engagement.md`
- `workshop/engagement-eval.json`
- `references/engagement.md` (seen as untracked on Rob's machine)

---

## Complete state of the project

**Everything is on GitHub and passes verification:**
- 11 skills (including `prv-04` fix)
- Synthetic warehouse (44 tables, 11 traps, fixed seed)
- 29 evals, 6 slices, 6 negative tests, offline drift verifier
- Three clean ablation arms (56% → 83% per-slice, 81% load-all)
- Pre-work email (ZIP-first, proxy workaround, plain-language setup)
- Define/Validate/Build worksheets (beginner-proofed, PDFs regenerated)
- `check_eval.py` — friendly eval validator for participants
- `explore.py` — simple starter template
- Failure-demo script with real captured transcripts
- Room-scale ablation script (multi-provider: Anthropic/OpenAI/Gemini)
- Printable data dictionary + starter queries (now with sample outputs)
- 17-slide workshop deck + 13-slide executive briefing deck
- Full facilitator guide (minute-by-minute, both OS variants)
- Dry-run runbook
- Complete facilitator safety net (3 reference docs + 3 walkthroughs)
- `check_setup.py` with multi-Python detection

**Plus local-only engagement answer key** (4 files, described above)

---

## What's left before October 1

| Priority | Item | Status |
|---|---|---|
| 1 | **Send pre-work email** | Template ready, needs `[DATE]` and `[Your name]` filled in |
| 2 | **Prepare 2–3 spare API keys** | With credit loaded, for participants whose keys fail |
| 3 | **Full timed deck read-through, alone, out loud** | Not yet done |
| 4 | **Print materials** | Data dictionary, 3 worksheets, starter queries — one per participant + spares |
| 5 | **Verify `claude-sonnet-5` is the correct current API model string** | Used in `run_my_ablation.py` — may have changed since materials were written |
| 6 | **Smoke test ablation demo with engagement eval** | Copy `engagement-eval.json` to `evals/my-eval.json`, ensure `references/engagement.md` exists, run `python workshop/run_my_ablation.py` |

---

## The fabrication log — still eleven

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

Standing rule: **run the query, read the artifact, confirm the push.**

---

## Setup failures — still seven

| # | What | Fix |
|---|---|---|
| 1 | pip/python pointing at different interpreters | Always `python -m pip` |
| 2 | Missing dependency → raw traceback | `check_setup.py` catches it |
| 3 | Script run from wrong directory | Explicit `cd` in every instruction |
| 4 | Typo in `--skill` silently ran nothing | Fuzzy matching added |
| 5 | API credit exhausted mid-run | Preflight check |
| 6 | VS Code play button uses different Python | "Run from terminal" warning in all materials |
| 7 | Corporate pip mirror returns 401 | `--index-url https://pypi.org/simple/` |

---

## PDF generation notes (for next time)

LibreOffice HTML→PDF conversion quirks that matter:
- **No flexbox** — LibreOffice ignores it; use plain block layout
- **No `position: absolute`** — renders at wrong position
- **Page breaks:** use `<p style="page-break-before: always; margin: 0; padding: 0; font-size: 1pt;">&nbsp;</p>`
- **`<pre>` blocks** get extra line-height (cosmetic, not broken)
- **CSS design system** matches `starter-queries.html`: Segoe UI 9pt body, Cambria serif headings, blue `#2563EB` h2s, Consolas 8pt code, orange `.warn` boxes, green `.note` boxes

Command: `libreoffice --headless --convert-to pdf <file>.html`

---

## Environment

Container resets between sessions. Clone from GitHub, read this file, then:

```bash
python check_setup.py
cd evals && python verify.py
cd .. && python references/verify_sql.py
```

No credentials stored in the repo, none should be.
