# Failure Demo Script — 20 Minutes (0:20–0:40)

Purpose: the room needs to *see* an agent get something wrong before they'll
believe the rest of the workshop matters. This is that moment.

**Read this whole script once before the workshop.** It tells you exactly what
to type, what to say while it's thinking, and — critically — what to do if the
live demo doesn't cooperate. Assume it won't, and you'll be fine either way.

---

## Before you run this for real people: fill in the blanks

This script has two placeholder blocks marked **[PASTE YOUR CAPTURED RESPONSE
HERE]**. Those are not written for you, on purpose — inventing sample dialogue
and presenting it as a real transcript is exactly the failure mode this whole
pack exists to prevent, and it would be a strange way to open this workshop.

You already have the real thing. Pull it from your own ablation run:

```powershell
cd evals
python -c "import json; d=json.load(open('results/baseline.json')); print(next(r['response'] for r in d['slices']['provenance-footer'] if r['id']=='prv-01'))"
python -c "import json; d=json.load(open('results/skills.json'));  print(next(r['response'] for r in d['slices']['provenance-footer'] if r['id']=='prv-01'))"
```

Copy the two outputs into the placeholders below **and** onto a backup slide
(see "If the live demo fails," below). Do this at least once during your dry
run, not for the first time the morning of.

---

## Choose your format

**Live (recommended if your dry run went well):** run it in front of the room.
More impact, more risk.

**Pre-recorded (recommended if you're at all unsure about wifi or API
reliability):** a screen recording or a static slide of your captured
transcript. Say plainly that it's pre-recorded — the room doesn't need to
believe it's live, they need to believe it's real, and telling them the truth
about which one it is costs you nothing.

Either way, **have the pre-recorded version ready as backup**, even if you plan
to run live. Screenshot both responses now, while everything works.

---

## The script

### Setup (1 min)

Say to the room:

> "Before we talk about why this matters, I want to show you it mattering. I'm
> going to ask an AI agent a simple question against our workshop data
> warehouse — the same warehouse you'll use all day — with no special
> instructions. Then I'm going to ask the exact same question with one skill
> loaded, and we'll look at the difference."

Have the warehouse connected and ready. If you're running this in Claude Code
or a similar tool, have it pointed at `warehouse/people_analytics.duckdb`
already, so you're not fumbling with setup live.

### Part 1 — no skill (3–4 min)

Type or paste, exactly:

> **"How many employees do we have? Just give me the number, I'm in a hurry."**

That exact wording matters — it's the real eval prompt (`prv-01`), and the
time-pressure framing is deliberate. It's testing whether the agent still does
the right thing when nudged to skip it.

**While it's thinking, talk — don't just watch a spinner:**

> "Notice I didn't tell it which table to use, what counts as an employee, or
> what confidence to have. That's normal. That's how most of these questions
> actually get asked."

**When the answer comes back**, it will likely be a bare number with no
qualification. Read it out loud, then ask the room:

> "Would you forward this number to your VP? What would you need to know
> first?"

Let a few people answer. Someone will say "where did it come from" or "is that
current." Good — that's the setup for what's next.

**[PASTE YOUR CAPTURED "NO SKILL" RESPONSE HERE]**

```
<the actual response text from results/baseline.json, prv-01>
```

### Part 2 — with the skill (3–4 min)

Load `skills/provenance-footer/SKILL.md` and ask the identical question again,
word for word.

> "Same question, same warehouse, same time pressure. One skill loaded."

**When this answer comes back**, it should carry a source table, a confidence
level, and a stated population — attached *despite* the "I'm in a hurry"
framing. Read the footer out loud, slowly. That's the part that lands.

**[PASTE YOUR CAPTURED "WITH SKILL" RESPONSE HERE]**

```
<the actual response text from results/skills.json, prv-01>
```

### The turn (4–5 min)

Now show the numbers, not just the vibe. Say:

> "Here's why the footer matters, concretely. This warehouse has **four
> different plausible answers** to 'how many employees do we have,' and they're
> all defensible if you don't ask the right questions first."

Put these on screen or say them aloud — every one is verified against the
actual warehouse, not estimated:

| Source | Answer | Why it's wrong (or right) |
|---|---|---|
| A stale reporting rollup | **4,168** | Stopped refreshing 2026-02-28. Looks current. Isn't. |
| A view that includes contractors | **4,368** | Real data, wrong population for "employees" |
| The canonical snapshot, correctly filtered | **3,647** | ✅ This one |

> "Without a footer, you can't tell which of these you got. With one, you can
> check it in ten seconds instead of finding out three weeks later in a board
> meeting."

### Close and transition (2–3 min)

> "Everything we do for the rest of today is in service of that footer, and
> the four other failure modes just like it that this warehouse has waiting
> for you. You're about to go find your own."

Transition directly into the DEFINE block — don't take questions here, take
them after the BUILD block when people have hands-on context.

---

## If the live demo fails

Something will go wrong at least once today — it did during development, more
than once. Have a plan and don't apologize for using it.

**API error or timeout:** say "let's not wait on this," switch immediately to
your pre-recorded version or screenshots. One sentence, no drama:
"Here's what I captured earlier — same result."

**The no-skill answer is unexpectedly good:** this happens sometimes — the
model occasionally catches the ambiguity unprompted. Don't fight it. Say:

> "Interesting — it did better than usual there. That's a fair result too:
> these models are good, not infallible, and the skill is insurance for the
> times it doesn't catch it. Let's look at a case it reliably can't get right
> without you."

Then pivot to a harder question — the Emerging Leaders Program one below is a
good backup, because no model can know your organization's selection effects
without being told.

**The with-skill answer is somehow worse:** also happens — over-firing is a
real, documented cost in this pack (see `evals/README.md`). If it happens live,
that's an honest teaching moment, not a disaster:

> "That's actually a known failure mode called over-firing — skills aren't
> free, they can add process where none was needed. We measured this. It's in
> the deck later."

---

## Backup question, if you need a harder failure

If the headcount question doesn't land — model answers it well, or the demo
audience has seen it before — this one is more reliably a clean miss, because
it requires organizational knowledge no model can infer:

> "The Emerging Leaders Program shows a **7-point** attrition gap between
> enrolled and non-enrolled employees. Did the program cause that?"

The honest answer requires knowing that enrollment was **85.6% manager-
nominated** — a fact about your organization, not a data quality issue a model
can catch on its own. This is `causal-claim-guardrail` territory rather than
`provenance-footer`, so only use it as backup if you're prepared to talk about
selection bias instead of source tiers. See `warehouse/facilitator/GROUND_TRUTH.md`
for the full numbers — **facilitator-only, do not display this slide's source
data to the room.**

---

## Timing checkpoint

If you're past minute 15 and still on Part 1, cut Part 2 short — skip straight
to showing the captured "with skill" screenshot rather than running it live,
and move on. The BUILD block losing time is worse than this block running long.
