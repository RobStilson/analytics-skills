# Handoff — 2026-09-09 (end of day)

**Project:** Vibe Analytics workshop + `analytics-skills` repo
**Conference:** 2026-09-29 · **Materials due:** 2026-09-16
**Dry run:** Sep 8–12 (in progress — smoke test started on work machine today)
**Repo:** https://github.com/RobStilson/analytics-skills (public)

---

## FIRST: three cleanup items on GitHub

These are on GitHub right now and should be fixed before the dry run:

| Issue | File | Fix |
|---|---|---|
| **Answer key leaked into participant space** | `references/engagement.md` | Move to `warehouse/facilitator/engagement.md` (it's already there too — just delete the `references/` copy) |
| **Leftover roleplay artifact** | `workshop/my-define-spec.md` | Delete — this was Rob's own Define spec from the engagement walkthrough, not a participant file |
| **Leftover exploration script** | `references/explore_duckdb.py` | Delete — participants create their own `explore.py` in the repo root per the Build worksheet |

```powershell
cd "C:\Agentic AI\Skills\analytics-skills"
Remove-Item references\engagement.md
Remove-Item workshop\my-define-spec.md
Remove-Item references\explore_duckdb.py
git add -A
git commit -m "Remove leaked answer key and leftover artifacts"
git push
```

---

## What was built today

### Multi-provider ablation script
`run_my_ablation.py` now supports Anthropic, OpenAI, and Gemini — auto-
detected from whichever API key is set. Fully self-contained (no longer
imports from `run_evals.py`). Includes fuzzy filename matching for typos
(`my-evals.json` → "Did you mean: my-evals.json"). Triggered by Rob's work
machine not having Anthropic access.

**The OpenAI and Gemini paths have NOT been tested against live APIs.** The
Anthropic path is proven. Rob's work machine with an OpenAI key is the first
real test of the OpenAI path — results not yet available.

### Beginner-proofing of all participant materials
Systematic audit of every participant-facing file assuming zero SQL, Python,
or PowerShell knowledge. 15 issues found and fixed:

- Pre-work email: ZIP download is now primary, git is the alternative;
  "environment variable" explained in plain language
- Validate worksheet: "eval," "assertion," and "JSON" defined in a glossary
  before first use; JSON formatting rules made explicit
- Build worksheet: `explore.py` setup written on the worksheet itself (not
  only delivered verbally); 30-second SQL primer added; starter queries
  referenced as fallback
- Define worksheet: "grain" and "as-of convention" defined in plain language
- Data dictionary: "fan-out" → "multiple rows per person"; "decoys" →
  "deliberately empty"; "immortal time bias" → "survival bias"
- Starter queries: SQL reading guide added

### Corporate proxy workaround
Added `--index-url https://pypi.org/simple/` guidance to the pre-work email,
facilitator guide, and dry-run runbook after hitting a 401 from Lockheed's
internal pip mirror (`nexus.global.lmco.com`) on the work machine. Seventh
setup failure documented.

### Executive briefing deck
13-slide deck for Rob's supervisor on adopting the approach at Lockheed
Martin. Frames the problem in HR terms, shows the measured results with
honest caveats, includes a before/after demo, and lands on a specific ask:
pick one recurring PA question this quarter, one analyst, two weeks.
`workshop/vibe-analytics-exec-briefing.pptx`.

### Compensation domain (complete)
Reference doc (`warehouse/facilitator/compensation.md`) with four Gotchas:
currency mixing (nearly invisible — averages are ~$65 apart), base vs total
comp ($16,646 gap), no worker_type column, small-cell suppression. Plus
step-by-step facilitator walkthrough with 7 verified queries.

### Facilitator walkthroughs for all three domains
`warehouse/facilitator/{attrition,compensation,engagement}-walkthrough.md` —
22 queries total, all verified. Each follows the same structure: numbered
queries in discovery order, "what they should notice" at each step, and a
ranked summary of discoverable Gotchas.

### Full facilitator guide
`workshop/facilitator-guide.md` — minute-by-minute script for all 8 blocks,
every command in both Windows and Mac/Linux variants, error lookup table,
emergency procedures (including "module not found" as the single most common
error).

### Framing + Failure Demo facilitator walkthrough
Slide-by-slide narration script for Blocks 1 and 2 — what to say at each
slide, timing checks, exact verbatim lines for the demo transitions, and
three rehearsed recovery lines for API failure, unexpectedly good baseline,
and worse-than-expected with-skill answer.

### Engagement domain roleplay (complete)
Full participant walkthrough from Define through Ablation. Key finding: the
ablation scored 2/2 baseline and 2/2 with-doc (+0 delta) but the two
responses reached **opposite conclusions** — baseline said engagement hasn't
improved, with-doc said it has. Same warehouse, same question, different
methodologies. The eval measured process transparency, not methodological
correctness. This is the workshop's strongest teaching moment.

### Printable data dictionary
`workshop/data-dictionary.html` — every table, column, row count, date range,
and categorical value extracted from the actual database. Replaces the DuckDB
CLI adventure. The empty-table list was verified after a first draft
fabricated 13 of 28 names (eleventh fabrication in the project).

### Starter-query handout
`workshop/starter-queries.html` — pre-written queries for all three domains
with "Try changing..." prompts. Designed as a fallback for non-SQL
participants. All 16 queries verified.

### Dry-run runbook
`workshop/dry-run-runbook.md` — five-part operational sequence. Smoke test
of `run_my_ablation.py` was started on the work machine today (Anthropic path
confirmed earlier; OpenAI path in progress).

---

## Complete state of the project

**Everything is on GitHub and passes verification:**
- 11 skills (including `prv-04` fix)
- Synthetic warehouse (44 tables, 11 traps, fixed seed)
- 29 evals, 6 slices, 6 negative tests, offline drift verifier
- Three clean ablation arms (56% → 83% per-slice, 81% load-all)
- Pre-work email (ZIP-first, proxy workaround, plain-language setup)
- Define/Validate/Build worksheets (beginner-proofed)
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
| 1 | **Fix the three cleanup items above** | 2-minute task, do first |
| 2 | **Finish the smoke test on the work machine** | OpenAI path started, not completed |
| 3 | **Send dry-run pre-work to volunteers** | People confirmed, pre-work not sent |
| 4 | **Run the dry run (Sep 8–12)** | Runbook at `workshop/dry-run-runbook.md` |
| 5 | **Fix whatever the dry run surfaces** | Unknown until it happens |
| 6 | **Send real pre-work email by Sep 15** | Template ready, needs `[DATE]` and `[Your name]` |
| 7 | **Full timed deck read-through, alone, out loud** | Not yet done |
| 8 | **Print materials** | Data dictionary, 3 worksheets, starter queries — one per participant + spares |
| 9 | **Present exec briefing to supervisor** | Deck ready, meeting not scheduled |

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

## Setup failures — now seven

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

## Key decisions made today

- **Multi-provider support** — the participant script is self-contained and
  works with any of three providers. The pack's own eval runner
  (`run_evals.py`) stays Anthropic-only; it's a maintainer tool, not
  participant-facing.
- **Beginner-first design** — every participant-facing file now assumes zero
  SQL/Python/PowerShell knowledge. SQL primer on the worksheet, JSON
  formatting rules in the Validate worksheet, `explore.py` setup written
  rather than spoken.
- **Starter queries as a behind-the-podium fallback** — not handed out by
  default; given to anyone stuck after a few minutes during Build.
- **The engagement roleplay's +0 delta** is positioned as a feature, not a
  failure — it's the strongest teaching moment about eval design and leads
  directly into the correction-harvesting content in Block 7.

---

## Environment

Container resets between sessions. Clone from GitHub, read this file, then:

```bash
python check_setup.py
cd evals && python verify.py
cd .. && python references/verify_sql.py
```

No credentials stored in the repo, none should be.
