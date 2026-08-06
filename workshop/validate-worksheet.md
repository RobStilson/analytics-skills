# VALIDATE Worksheet — 30 Minutes

You're going to write the test before you write the answer. This feels
backwards the first time. It's the same discipline as test-driven development,
and it's why this pack's own claims are numbers instead of vibes — every skill
in the repo has an eval file that existed before anyone was sure the skill
worked.

**You have not queried the warehouse for your domain yet, and that's correct.**
You're writing assertions about what a *good process* looks like, informed by
what you already know — not assertions about a specific number you haven't
seen. You'll discover the actual data-specific trap empirically next block, in
Build.

Keep your Define worksheet's Question Spec open — you're writing evals
against that exact question.

---

## 1. Recall the failure demo — 5 min

You watched an agent answer "how many employees do we have, I'm in a hurry"
twice this morning — once with no skill, once with `provenance-footer`
loaded.

Write down, in your own words, **two specific things** that made the first
answer worse than the second. Not "it was less good" — specific. Did it state
a source? A population? Did it hedge, or state a number with false confidence?

You're about to turn observations like these into assertions.

---

## 2. Pick one generalizable rule for your domain — 5 min

Every domain in this warehouse has a *pattern-level* risk that generalizes —
you don't need today's specific number to know the risk exists.

| Domain | The pattern to guard against |
|---|---|
| **Attrition** | A rate reported with no stated denominator, or a denominator choice buried instead of disclosed |
| **Compensation** | Values combined across currencies (or other units) without saying so |
| **Engagement** | A trend compared across periods without confirming the instrument stayed the same |

Pick the one matching your domain. This is scaffolding, not the answer — it
tells you *what kind* of thing to check for, not what you'll actually find
when you query the warehouse next block.

---

## 3. Write your assertions — 10 min

Using the schema below, write **2 to 3 assertions** for your Define question.
Each one must be **objectively checkable** — a reader with no context should
be able to look at a response and say pass or fail, not "sort of."

```json
{
  "skill_name": "<your-domain>",
  "evals": [
    {
      "id": 1,
      "prompt": "<paste your restated question from Define, word for word>",
      "expected_output": "<one sentence: what a correct response does>",
      "assertions": [
        "<objectively checkable claim about the response>",
        "<a second one>"
      ]
    }
  ]
}
```

**Weak assertion:** "The response is accurate." Nobody can check that without
already knowing the answer.

**Strong assertion:** "The response states which population is counted" — a
reader can verify this by reading the response, full stop.

At least one assertion should trace directly to your domain's pattern from
step 2 — e.g., for Attrition: *"the response states the denominator used to
compute the rate."*

**Save this as `evals/my-eval.json`** — that's the exact path the Build
block's ablation script looks for by default.

---

## 4. Add one negative consideration — 5 min

This pack keeps at least one negative test per skill — a case the skill
should **not** change. Skipping this is how `provenance-footer` shipped a bug
that attached a full footer to a simple schema lookup; it's in this repo's own
history.

Write one line: what would an answer to your question look like if it were
**overcautious** — padded with process, hedged into uselessness, or answering
something nobody asked? You don't need to formalize this as a full eval today.
Naming it is enough.

---

## 5. Predict — 5 min

Before anyone runs anything: for each assertion you wrote, guess whether a
plain agent with **no skill loaded** would pass or fail it.

```
Assertion 1: [PASS / FAIL] — because ___
Assertion 2: [PASS / FAIL] — because ___
```

Write the guess down now. You'll find out if you were right during the
ablation block at 2:15 — and being wrong is just as useful as being right. If
you guessed PASS and it failed, that's a real gap you didn't know you had.

---

## Share-out — when the facilitator calls time

One sentence:

> "My strongest assertion is ___, and I predict a plain agent will ___ it."

Keep this worksheet. In Build, once you've queried the warehouse and found
your domain's actual Gotcha, come back and check: did the trap you found match
the pattern you guarded against here? If it's different, that's fine — that's
new information you write into the skill, not a sign you did this block wrong.
