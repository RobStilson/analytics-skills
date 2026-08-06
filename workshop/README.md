# Workshop materials

## Deck

`build_deck.js` generates `vibe-analytics-workshop.pptx`. The deck is generated,
not hand-edited, so every figure in it traces to something measured.

```bash
node build_deck.js
python /mnt/skills/public/pptx/scripts/office/validate.py vibe-analytics-workshop.pptx
```

Edit the script, not the .pptx — hand edits are lost on the next rebuild.

Every slide carries speaker notes. Read them; several contain the framing that
makes the slide land, not just a restatement of what is on it.

## Figures used, and where they came from

| Slide | Figure | Source |
|---|---|---|
| Warehouse | 12,282 / 4,368 / 4,168 / 3,647 | `evals/ground_truth.json` |
| Warehouse | 54% populated, 1,668 dropped | `warehouse/facilitator/GROUND_TRUTH.md` |
| Warehouse | 2.32x fan-out | `evals/ground_truth.json` |
| Demo | 0/4 → 4/4 on prv-01 | first ablation, claude-sonnet-5 |
| Result | 56% → 84%, per-slice deltas | clean ablation, claude-sonnet-5 |
| Result | mean +28.2, CI +12 to +44, p=0.009 | 29 paired eval-level observations |
| Caveats | 87% → 70% negative, +22/+23 sensitivity | same run |
| Diagnosis | 11,253 tokens | measured from `skills/*/SKILL.md` |

If you rebuild the warehouse with a different seed, these move. Re-run
`evals/make_ground_truth.py` and update the script.

## What runs live, and what does not

The full eval suite is **not** a workshop activity. Participants make a handful
of API calls, not hundreds.

| Moment | Calls | Time |
|---|---|---|
| Failure demo | 1-2 | ~30 sec |
| Participant tests their own skill | 2-5 | under a minute |
| Ablation on stage | pre-recorded, or `--skill <one>` | ~1-2 min |

Run the full suite yourself beforehand and put the numbers on the slides. A
30-minute wait in a 3-hour session is unrecoverable.

## Participant worksheets

Three timed worksheets cover the hands-on hour and a half (0:40–2:15). They
share one domain per participant, chosen once and carried through:

| Block | Time | Worksheet | Produces |
|---|---|---|---|
| Define | 20 min | `define-worksheet.md` | A question spec, `question-intake`'s template |
| Validate | 30 min | `validate-worksheet.md` | 2-3 assertions saved to `evals/my-eval.json` |
| Build | 45 min | `build-worksheet.md` | A filled `references/<domain>.md`, run against real SQL |
| Ablation | 20 min | none needed — `run_my_ablation.py` | Their own before/after, baseline vs. their doc |

Domain selection happens once, in Define's step 0, and is deliberately not
repeated in Build — Build's step 0 assumes the domain and worksheets from
Define and Validate are already on the table. If you resequence the agenda,
keep the domain-pick step wherever the hands-on portion starts.

The three domains — Attrition, Compensation, Engagement — each carry a
generalizable risk pattern named in Validate (denominator disclosure, unit
mixing, instrument consistency) without stating the specific number or trap
the warehouse has waiting. Participants discover the specific version
empirically in Build's Gotchas step, then can check it against their own
Validate-stage prediction.

## The 2:15 ablation — `run_my_ablation.py`

Not the pack's own ablation (`evals/run_evals.py`, 29 evals x 6 slices, a
maintainer's tool). This runs the ONE eval a participant wrote in Validate
against the ONE reference doc they wrote in Build — baseline vs. with-doc,
on their own machine, their own key, in well under a minute.

It reuses `run_evals.py`'s agent loop, grader, retry logic, and fatal-error
handling by importing it directly rather than reimplementing any of it — that
loop was debugged through several real failures during development (turn
exhaustion, credit errors, empty responses), and a participant-facing script
running live in a room is the last place to reintroduce those bugs.

Defaults, matching the worksheets exactly:
- Eval: `evals/my-eval.json` (Validate step 3's save instruction)
- Reference doc: auto-detected from `references/{attrition,compensation,engagement}.md`
  — an **allowlist**, not a blocklist. A blocklist breaks the first time a new
  file lands in `references/`; this one already did once during testing
  (`analysis-patterns.md` was silently picked up as a candidate doc before the
  fix). An allowlist of the three known domain names can't be broken that way.

Validates local files (the eval JSON, the reference doc) before touching the
network — a broken JSON file shouldn't require an API key to diagnose. Does
NOT write to `evals/results/`; that directory holds the pack's own official
ablation and backs the deck and the failure-demo script. Nothing is written by
default; `--save` writes a timestamped file in `workshop/`, gitignored.

## Status

Materials-complete for facilitator and participant sides, including the
room-scale ablation. Open work:

- [ ] Dry run — none of the four blocks (Define, Validate, the resequenced
      Build, the ablation script) have been tested against a real person's
      timing yet
