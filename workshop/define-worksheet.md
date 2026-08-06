# DEFINE Worksheet — 20 Minutes

You're about to spec a question before you've looked at any data. That order
matters — it's the whole point of this block. Once you've seen the numbers,
you can't un-see them, and you'll unconsciously write the spec to fit whatever
you found. Specify first.

You'll fill in `skills/question-intake/SKILL.md`'s **Question Spec** template.
Keep it open alongside this sheet.

---

## 0. Pick your domain — 2 min

This choice carries through the rest of the day — the same domain in Define,
Validate, and Build. Pick once, now.

| Domain | Your starting question |
|---|---|
| **Attrition** | What was our attrition rate last year? |
| **Compensation** | What's our average salary? |
| **Engagement** | Has engagement improved since 2023? |

If the room has more than three people, pair up by domain — say your choice
out loud so the facilitator can spread the room across all three.

**Don't pick Headcount** — it's the pre-built worked example
(`references/EXAMPLE-headcount.md`), not an exercise.

---

## 1. Restate and set the population — 3 min

Write your question as one plain sentence, then answer: **who counts?**

For "attrition rate," does that include contractors? People who left in the
first week? For "average salary," everyone, or just people paid in your home
currency? For "engagement improved," respondents only, or everyone who was
invited?

You don't need to know the *right* answer yet — you need to state which one
you're assuming, so it's visible later.

Fill in **Restated question** and **Population** now.

---

## 2. Time basis and grain — 4 min

- **Time basis:** is this a snapshot as of a date, or a window of activity
  over a period? "Last year" could mean either.
- **Grain:** what does one row represent, in the table you'd guess is right?
  A person? A person-month? An event?

You're guessing at this point — you haven't queried anything. That's fine.
Write down your best guess for **Time basis** and **Grain**.

---

## 3. Name the measure — 4 min

Every domain has more than one defensible definition of "the" number:

- **Attrition** — voluntary only? All separations? What's the denominator —
  headcount at the start of the period, the end, or an average?
- **Compensation** — a mean or a median? Does the answer assume one currency,
  or should it handle several?
- **Engagement** — one survey item, or a composite? Does "improved" assume the
  measurement itself stayed consistent across the periods being compared?

Write your best-guess definition in **Measure**, including what you think the
denominator or unit should be. Naming your assumption is the deliverable here
— not getting it right.

---

## 4. Comparison, decision, precision — 5 min

Three fast questions, one line each:

- **Comparison:** against what? Last year? A target? Nothing — just the
  absolute number?
- **Decision it informs:** what would someone actually *do* differently
  depending on the answer? If you can't name one, that's worth noting — it
  might mean the question isn't ready.
- **Precision needed:** does this need to be exactly right, or is a
  directional answer enough?

---

## 5. Existing coverage and open assumptions — 2 min

- **Existing coverage:** is there already a dashboard or report that answers
  this? (For today, "none — this is the exercise" is a fine answer.)
- **Open assumptions:** list everything above that you resolved by guessing
  rather than confirming. Be honest — this list is the most useful thing you
  produce today.

---

## Emit the spec

Copy your answers into the exact template from `question-intake`:

```markdown
## Question Spec

**Restated question:** [...]
**Population:** [...]
**Time basis:** [...]
**Grain:** [...]
**Measure:** [...]
**Comparison:** [...]
**Decision it informs:** [...]
**Precision needed:** [...]
**Existing coverage:** [...]
**Open assumptions:** [...]
```

Keep this. You'll write evals against it next block, and the reference doc
you write in Build should resolve — or explicitly leave open — every
assumption on this list.

---

## Share-out — when the facilitator calls time

One sentence:

> "My question is ___. My biggest open assumption is ___."

That's it. Notice the field name — **Open assumptions**. You'll see it again
on the provenance footer template this afternoon. That's not a coincidence:
what you don't yet know now is exactly what a good answer has to disclose
later. This worksheet and that footer are two ends of the same thread.
