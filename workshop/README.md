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

## Status

Draft. Built after the first ablation. Open work:

- [x] Re-run the ablation with `--repeats 3` and per-slice loading — done, slides
      12 and 13 carry the real numbers
- [ ] Add the `--load-all` arm as a third comparison — the contrast is the point
      and would make the loading-strategy argument concrete
- [ ] Paste real response text into the demo slide instead of describing it
- [ ] Pre-work email and setup instructions
- [ ] BUILD-block worksheet
