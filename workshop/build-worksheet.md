# BUILD Worksheet — 45 Minutes

You're about to write a reference doc for one domain in the workshop warehouse.
This sheet is your clock and your prompts. The actual document you're filling in
is `references/domain-doc-template.md` — open both side by side.

**The rule for today: run the query before you write the line.** Every fabricated
number in this pack's own history got caught only by someone executing something
and reading the result. You're joining that habit now, not being warned about it.

---

## 0. Orient — 2 min

Pull up your **Define worksheet** (the question spec) and your **Validate
worksheet** (the assertions and prediction). You picked your domain back in
Define — this block is where you find out what your question spec got right
and wrong.

| Domain | Start here |
|---|---|
| **Attrition** | `fct_separation`, `rpt_attrition_monthly` |
| **Compensation** | `fct_compensation` |
| **Engagement** | `fct_engagement_survey` |

If you're pairing up, confirm you're both still working the same domain you
claimed this morning.

---

## 1. Quick Reference — 5 min

Answer these before touching SQL:

- What does one row of your canonical table represent?
- What's the person key? (Hint: it might not be `worker_id` — check
  `EXAMPLE-headcount.md`'s Gotcha 2 for why.)
- What's the as-of convention — a snapshot, or an activity window over a period?

Write the **Quick Reference** section now, even if it's your best guess. You'll
correct it in step 3.

---

## 2. Required Filters — 5 min

Run your first query with no filters at all. Look at the row count. Now ask:

- Does this table mix worker types, statuses, or currencies that your question
  shouldn't blend together?
- What's the *smallest* change to your `WHERE` clause that meaningfully changes
  the result?

Write the **Required Filters** table with at least two rows.

---

## 3. Gotchas — 15 min ⚠️ the point of the exercise

This is the section a model cannot write for you, because it requires actually
looking. Budget the most time here.

**Before you query:** glance at your Validate worksheet's prediction. You
guessed whether a plain agent would pass or fail your assertions. Keep that
guess in mind — you're about to find out whether the trap you anticipated is
the trap that's actually here.

**The move:** find two plausible ways to answer the same simple question from
your domain, and see if they agree.

- **Attrition** — `rpt_attrition_monthly` gives you a numerator. It does not
  give you a denominator. Compute the rate three defensible ways using
  headcount from `dim_worker_snapshot` (beginning of period? end? average?) and
  see how far apart the three answers land.
- **Compensation** — pull every row's currency. Now compute a naive average
  across all of them. Does that number mean anything?
- **Engagement** — pull one survey item across every wave in the table. Before
  you trend it, check whether every wave measured it the same way.

When you find a discrepancy: **that's your Gotcha.** Write it in the template's
Do/Don't format — the wrong query, what it silently produces, and the right one.

Aim for at least **one** fully-written Gotcha with real numbers from your own
query. One real one beats three guessed ones.

**Stuck after 8 minutes?** Flag the facilitator. Don't spend the whole block
searching — say what you've tried and ask for a nudge.

---

## 4. Measures — 5 min

Name the one measure your domain is really about (an attrition rate, an average
salary, an engagement score). Write down:

- The exact numerator and denominator
- What population is in scope
- Whether you found more than one definition already in use in the data

---

## 5. Query Patterns — 10 min

Write one query that answers the single most common question someone would ask
about your domain — and **run it**. It goes in the doc only if it executed
successfully against the warehouse.

If you have time left, write a second pattern.

---

## 6. Wrap — 5 min

Fill in whatever's left, in this order of priority:

1. **Cross-References** — one row: what domain would someone join yours to, and
   what would go wrong if they weren't careful?
2. **Escalate, Don't Guess** — one line: a question in your domain you should
   route to a human rather than answer.
3. **Open Questions** — anything you didn't get to. An honest gap beats a
   confident guess.

Then run the checklist at the bottom of `domain-doc-template.md`. If you can't
check every box, that's fine — say which one is unchecked when we reconvene.

---

## Share-out — when the facilitator calls time

Be ready to say, in one breath:

> "My domain was ___. My Gotcha is ___. Without it, someone would have gotten
> ___ instead of the right answer."

That's it. If your Gotcha is "I didn't find one yet," say that too — a
documented near-miss is still useful, and it's an honest place to start the
correction-harvesting loop after today.

---

## If you finish early

Open someone else's domain and try to break their Query Pattern with a question
they didn't anticipate. That's a free adversarial-review rep, and it's exactly
what `sql-reviewer` will formalize in the next block.
