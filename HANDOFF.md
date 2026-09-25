# Handoff — 2026-09-25 (end of day)

**Project:** Vibe Analytics workshop + `analytics-skills` repo
**Conference:** 2026-09-29 (4 days away)
**Repo:** https://github.com/RobStilson/analytics-skills (public)

---

## What was done today

### Full beginner-friendliness review of all participant materials
Systematic review of every participant-facing file on GitHub, assuming zero
Python/SQL/JSON knowledge. 12 findings organized by severity (Critical, High,
Medium, Low). All Critical and High fixes implemented.

### Fixes applied (2 commits, not yet pushed from this session)

**Commit `7b21d4b`: Fix beginner-friendliness issues found in workshop review**

| Change | File | What |
|---|---|---|
| `explore.py` replaced | `explore.py` | Was a complex engagement query with CASE expressions, JOINs, scale normalization — intimidating for beginners. Replaced with the simple starter template matching the build worksheet |
| Build worksheet updated | `workshop/build-worksheet.md` | (1) "Create this file" → "Open `explore.py` — it's already in the repo"; (2) Added "Before you start — save your reference doc" section with save-as table and exact copy commands; (3) Added DuckDB file-lock warning and Starter Queries file path |
| Validate worksheet updated | `workshop/validate-worksheet.md` | Replaced one-liner JSON validation commands with `check_eval.py` reference |
| `check_eval.py` created | `check_eval.py` | Friendly eval validator (~170 lines). Zero-dependency, ANSI colors with Windows fallback. Checks file exists, valid JSON, has `evals` list, first eval has `prompt` and `assertions`. Gives specific fix suggestions for common JSON mistakes |
| CONTRIBUTING.md updated | `CONTRIBUTING.md` | "nine skills and no eval coverage" → "eleven skills and 29 evals across six slices" |

**Commit `f2524cc`: Regenerate build and validate worksheet PDFs**

| Change | File | What |
|---|---|---|
| Build PDF regenerated | `workshop/build-worksheet.pdf` | 3-page PDF reflecting all markdown changes |
| Validate PDF regenerated | `workshop/validate-worksheet.pdf` | 4-page PDF reflecting all markdown changes |
| HTML sources added | `workshop/build-worksheet.html`, `workshop/validate-worksheet.html` | Source files for PDF generation, styled to match existing workshop design system |

### ⚠️ Commits exist locally but could NOT be pushed

This session lacks push access to `RobStilson/analytics-skills`. The commits
exist in the cloud container (which is ephemeral), and the PDFs were sent
directly to Rob. He needs to:

1. Drop the 4 files (2 PDFs + 2 HTMLs) into `workshop/` locally
2. Commit and push from his machine

If the container has been reclaimed, the markdown changes are already on
GitHub from a previous push (commit `7b21d4b`), but the PDFs and HTML source
files need to be regenerated or placed manually.

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
- `explore.py` — simple starter template (no longer the complex engagement query)
- Failure-demo script with real captured transcripts
- Room-scale ablation script (multi-provider: Anthropic/OpenAI/Gemini)
- Printable data dictionary + starter queries
- 17-slide workshop deck + 13-slide executive briefing deck
- Full facilitator guide (minute-by-minute, both OS variants)
- Dry-run runbook
- Complete facilitator safety net (3 reference docs + 3 walkthroughs)
- `check_setup.py` with multi-Python detection

---

## What's left before September 29

| Priority | Item | Status |
|---|---|---|
| 1 | **Push PDF/HTML files from local machine** | PDFs sent to Rob, needs local commit+push |
| 2 | **Send pre-work email** | Template ready, needs `[DATE]` and `[Your name]` filled in — 10+ days past recommended send date |
| 3 | **Prepare 2–3 spare API keys** | With credit loaded, for participants whose keys fail |
| 4 | **Full timed deck read-through, alone, out loud** | Not yet done |
| 5 | **Print materials** | Data dictionary, 3 worksheets, starter queries — one per participant + spares |
| 6 | **Verify `claude-sonnet-5` is the correct current API model string** | Used in `run_my_ablation.py` — may have changed since materials were written |

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
