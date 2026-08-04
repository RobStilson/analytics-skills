# References

Supplementary material that skills pull in on demand, kept out of SKILL.md so it
loads only when needed.

## Planned

| File | Covers | Status |
|---|---|---|
| `domain-doc-template.md` | Fill-in skeleton for a per-domain reference doc | **Ready** |
| `EXAMPLE-headcount.md` | Worked example against the warehouse — deliberately incomplete | **Ready** |
| `analysis-patterns.md` | Cohort construction, retention/censoring, rate decomposition, funnels, distributions | **Ready** |
| `eval-writing-guide.md` | How to write an eval that discriminates and does not drift | Not yet written |
| `analytics-definition-of-done.md` | The standing bar every delivered analysis clears | Not yet written |

`eval-writing-guide.md` is the highest-value remaining gap.

All SQL in these docs is executed against the warehouse by
`references/verify_sql.py` — run it after any edit. Confirmed to catch injected
errors, so a pass means something.

## Using the template

Copy `domain-doc-template.md` to `references/<domain>.md` and work top to bottom;
the sections are ordered by how much they reduce wrong answers.

The **Gotchas** section is the one that matters. Everything else can be inferred
from the schema — Gotchas cannot. It is the organizational history that exists
only in the heads of people who were there, and writing it down is the entire
point of the exercise.

`EXAMPLE-headcount.md` shows the shape, filled against the workshop warehouse.
It is deliberately incomplete: two Gotchas are written out, four are headings
with TODOs. Finishing them is the exercise.
