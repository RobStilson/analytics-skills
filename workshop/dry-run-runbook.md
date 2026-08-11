# Dry Run Runbook

This is the actual sequence for running the dry run — not a rehearsal of the
workshop content, a test of whether the workshop *works*. Treat every minute
as data. If a block runs long, that's the finding, not a problem to paper
over before the real thing.

**Everything in Define, Validate, Build's resequencing, and the ablation
script is untested against real people.** That's the whole point of doing
this now instead of finding out on September 29.

---

## Part A — This week, before you invite anyone

### A1. Smoke-test the ablation script yourself, alone, first

`run_my_ablation.py` has never been run against a live API by anyone,
including you. Don't let its first real execution happen in front of your
guests. Do this now:

```powershell
cd "C:\Agentic AI\Skills\analytics-skills"
python check_setup.py
```

Then create a throwaway eval and reference doc to exercise the real path:

```powershell
cd evals
```

Save this as `evals/my-eval.json`:

```json
{
  "skill_name": "smoke-test",
  "evals": [
    {
      "id": 1,
      "prompt": "How many employees do we have?",
      "expected_output": "States a source and a population.",
      "assertions": [
        "The response states which table the number came from",
        "The response states which worker types are counted"
      ]
    }
  ]
}
```

Copy `references/domain-doc-template.md` to `references/attrition.md` and
just fill in the Quick Reference section — doesn't need to be complete, you're
testing the script, not writing a real doc.

```powershell
cd ../workshop
python run_my_ablation.py
```

Watch for: does it find the eval, find the reference doc, run baseline, run
with-doc, print a clean comparison? If anything breaks here, it breaks the
same way for four people simultaneously next week — better to know now.

Delete the throwaway files when done (`evals/my-eval.json`,
`references/attrition.md`) so they don't confuse the real dry run.

### A2. Full timed read-through of the deck, alone, out loud

This has not been done yet. Fifteen-plus slides plus your own narration will
almost certainly run long or short of what the agenda promises. Time it.
Adjust your talking points, not the deck's numbers — the numbers are
measured and shouldn't move without a reason.

### A3. Rebuild the warehouse fresh and re-verify

```powershell
cd warehouse
python build_warehouse.py
cd ..\evals
python verify.py
cd ..
python references\verify_sql.py
```

All three should pass clean. This confirms what you're about to hand four
people is exactly what's in the repo, not a locally-drifted copy.

### A4. Recruit confirmation and room logistics

- Confirm your 3–4 people, times, and that at least one is SQL/BI-native
  rather than Python-fluent — if your current group skews all-Python, that's
  worth flagging now, since that's the participant this design is most
  likely to fail for.
- Confirm wifi will hold up if it's not everyone's own hotspot.
- Block 3 full hours, not "around 3 hours." A dry run that gets rushed at the
  end doesn't tell you anything about the real timing.

---

## Part B — Send compressed pre-work, 3–5 days out

You can't give two weeks' notice for a dry run happening this month. Send a
shortened version — same content, different framing:

> Subject: Quick favor — 3 hours, testing a workshop before I run it live
>
> Thanks for helping test this. Please do the setup below **before we meet** —
> if anything breaks, better to find out this week than while I'm watching.
>
> 1. Clone: `git clone https://github.com/RobStilson/analytics-skills.git`
> 2. `pip install -r requirements.txt` (use `python -m pip` if you have more
>    than one Python installed)
> 3. Get an API key at console.anthropic.com and **add a few dollars of
>    credit** — a key with no credit fails in a way that looks like a bug
> 4. Set `ANTHROPIC_API_KEY` as an environment variable
> 5. Run `python check_setup.py` and confirm it says **Ready**
>
> Reply if step 5 doesn't say Ready. I'd rather fix it now than lose time
> Tuesday.

Track responses. If someone hasn't confirmed "Ready" by the day before,
follow up directly — don't assume silence means success. (This is the exact
mistake the real pre-work email warns against; the dry run is where you find
out if the warning is warranted.)

---

## Part C — Day of: the runbook

Bring this section open on a second screen. For each block: what you do,
what they do, what's specifically at risk, and what to write down.

**Before anything starts:** open a blank note. You'll fill in the *Actual*
column of the timing log below as you go — not from memory afterward.

### Timing log — fill this in live

| Block | Planned | Actual | Notes |
|---|---|---|---|
| Framing | 20 min | | |
| Failure demo | 20 min | | |
| Define | 20 min | | |
| Validate | 30 min | | |
| Build | 45 min | | |
| Ablation | 20 min | | |
| Operationalize | 15 min | | |
| Contribute | 10 min | | |

---

### 0:00–0:20 — Framing

**You:** present deck slides 1–9.
**Them:** listen.

**Watch for:** this is the block most likely to run long on a first read — no
one has timed it end to end. If you're past 0:20 and still on slide 9, cut
toward the failure demo rather than protecting the framing; the demo is more
persuasive than any slide.

### 0:20–0:40 — Failure demo

**You:** run `failure-demo-script.md` exactly as written.
**Them:** watch, answer your discussion prompts.

**Watch for:** the script already has contingency plans built in for API
failure, an unexpectedly good no-skill answer, and a worse-than-expected
with-skill answer — read those sections before you start, not during. This
is genuinely lower-risk than what follows; it's been through several review
passes already.

### 0:40–1:00 — Define

**You:** introduce `question-intake`'s spec template briefly, then circulate.
**Them:** work `define-worksheet.md` — pick a domain, spec the seed question.

**Watch for — this block is new, watch closely:**
- Does 20 minutes feel right, or does everyone hit "Emit the spec" with time
  left over or none at all?
- Does the domain table make sense on first read, or do people hesitate on
  which to pick?
- Note literally how long each of the six steps takes for at least one
  person — the worksheet's per-step budget is a guess, not yet a measurement.

**Capture:** ask each person to hold up their finished spec — a visual check
that everyone actually reached "Emit the spec" rather than stalling mid-way.

### 1:00–1:30 — Validate

**You:** introduce evals-before-skill, circulate.
**Them:** work `validate-worksheet.md` — 2–3 assertions, one negative
consideration, a written prediction. **No querying yet.**

**Watch for — the highest-risk conceptual block:**
- This is the one asking people to reason about data they haven't looked at
  yet. Watch whether that instruction actually holds, or whether people
  start opening the warehouse early out of habit. If everyone does, that's
  a real finding about the worksheet's framing, not a discipline problem
  with your participants.
- Does the JSON schema trip anyone up? A syntax error here is exactly what
  `run_my_ablation.py`'s error messages are supposed to catch gracefully at
  2:15 — if someone's JSON is broken now, that's useful, you'll see the
  error message do its job later.

**Capture:** collect (or have them keep) their written predictions — you'll
want to check these against the ablation's real results at 2:15.

### 1:30–2:15 — Build

**You:** circulate, answer "stuck after 8 minutes" flags from the Gotchas
section.
**Them:** work `build-worksheet.md` — query the real warehouse, find their
domain's actual trap, fill in `references/<domain>.md`.

**Watch for:**
- The 15-minute Gotchas budget is the one part of this block that's been
  tested — by the person who wrote it, not by someone discovering it cold.
  Watch whether 15 minutes is enough for a first-timer to find the
  discrepancy unprompted, or whether the hints need to be more direct.
- Confirm the domain carried through correctly from Define — someone
  starting Build on a different domain than they specced is a sign the
  hand-off between blocks isn't as obvious as it reads on paper.

**Capture:** for each participant, note whether they found a real Gotcha
with actual numbers, or ran out of time first. This is the single most
important data point from the whole dry run — it's the exercise the entire
workshop is built around.

### 2:15–2:35 — Ablation

**You:** introduce `run_my_ablation.py`, then let everyone run it on their
own laptop simultaneously.
**Them:** run it against their own `evals/my-eval.json` and
`references/<domain>.md`.

**Watch for — second-highest technical risk, after your own smoke test:**
- Does everyone's preflight succeed? A credit or key problem here should
  produce the script's specific error message pointing at "flag the
  facilitator" — watch whether that actually happens cleanly.
- Does the auto-detected reference doc match what each person actually
  wrote? (This is the allowlist logic — should be solid, but four
  simultaneous real runs is still more than it's had before.)
- Have people compare the result against their Validate-stage prediction out
  loud — that comparison is the payoff of the whole 90 minutes before it,
  and it's easy to let it pass by silently if the room is focused on just
  getting the script to run.

**Capture:** did anyone's script error out? Exact error text, not a summary
— you'll want it verbatim if something needs fixing before September.

### 2:35–2:50 — Operationalize and compound

**You:** explain the provenance footer and correction-harvesting loop.
**Them:** mostly listening — **there's no worksheet for this block yet.**

**Watch for:** this is the block most likely to feel thin, precisely because
it has no hands-on material. Note whether that's actually a problem in
practice — sometimes a shorter, talk-through block is fine, and you don't
want to build a worksheet nobody needed. Let the dry run tell you rather than
guessing.

### 2:50–3:00 — Contribute and wrap

**You:** walk through opening a PR against the real repo.
**Them:** open one if time allows — **also no dedicated worksheet.**

**Watch for:** same as above — is 10 minutes enough to explain a PR flow to
people who've never contributed to this repo, or does it need a cheat sheet?

---

## Part D — Immediately after: debrief

Do this the same day, while it's fresh — not next week. Ask each person,
in order:

1. **"Which block ran the longest relative to what you expected, and why?"**
   — not "which was too long," the *why* is the actionable part.
2. **"Where did you feel lost, even briefly?"** — people under-report
   confusion unless asked directly and specifically.
3. **"Read me your Gotcha."** — if it's vague or generic, the Build block's
   guidance needs sharpening, not the participant.
4. **"Did your Validate prediction match what the ablation actually showed?"**
   — a mismatch is fine and interesting; total silence on this question
   means the comparison didn't land as a moment during the session.
5. **"What would you cut if this had to be 2.5 hours instead of 3?"** — a
   good stress test for what's actually load-bearing versus nice-to-have.

Write down answers verbatim where you can. Paraphrasing at this stage loses
the specific phrasing that tells you *why* something confused someone.

---

## Part E — Before September 16

Bring your timing log and debrief notes back and work through them block by
block — the worksheets, the deck, and the agenda times should all be treated
as adjustable based on what actually happened, not defended because they were
carefully designed. A design that doesn't survive contact with real people
isn't a design yet.

Priority order for fixes, if time is short before the materials deadline:

1. Anything that broke technically (script errors, setup failures) — these
   block the workshop outright
2. Timing corrections to the agenda and deck — these are cheap to fix and
   visible to everyone in the room if wrong
3. Worksheet clarity issues — moderate cost, high value, since confusion
   here eats time from later blocks
4. Whether Operationalize/Contribute need worksheets at all — lowest
   priority, and only build them if the dry run actually showed a need
