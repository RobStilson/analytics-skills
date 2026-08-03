# Domain Reference Doc — Template

Copy this file to `references/<domain>.md` and fill it in. One doc per domain
(headcount, attrition, compensation, engagement), not one per table.

**Who this is for:** an agent that has never seen your warehouse and cannot ask
you a question. Write for that reader. Everything you would say out loud to a new
analyst in their first week belongs here, and nothing else does.

---

## How to fill this in

Work top to bottom. The sections are ordered by how much they reduce wrong
answers, so if you run out of time, the parts you finished are the parts that
mattered most.

| Section | Time | Why it matters |
|---|---|---|
| Quick Reference | 5 min | The routing decision — which table, at what grain |
| Required Filters | 10 min | The single largest source of silently wrong numbers |
| **Gotchas** | **15 min** | **The only section a model cannot generate. This is the doc.** |
| Measures | 10 min | Stops two teams reporting two different "attrition rates" |
| Query Patterns | 10 min | Saves the next person from rebuilding the same join |
| Cross-References | 5 min | Prevents wrong joins into neighbouring domains |

**Write in the imperative, and address the agent.** "Use `dim_worker_snapshot`"
beats "the snapshot table is generally preferred." Directives get followed;
descriptions get skimmed.

**Use `IF … THEN … DO NOT …` for anything load-bearing.** A routing conditional
does more work than a paragraph explaining the difference between two tables,
because it tells the agent what to *do* rather than what is true.

**Shorter is better.** Docs that only grow become docs nobody maintains and
models retrieve from poorly. If a line does not change what the agent does,
delete it.

Delete the `<!-- guidance -->` comments as you go. Delete any section that does
not apply — an honest empty doc beats a padded one.

---

<!-- ============ COPY FROM HERE ============ -->

---
domain: <!-- e.g. headcount -->
owner: <!-- named human, not a team inbox — an unowned doc is an unmaintained doc -->
last_verified: <!-- YYYY-MM-DD — when someone last checked this against the warehouse -->
source_tier: <!-- semantic-layer | governed-table | raw -->
---

# <Domain> — Reference

## Quick Reference

<!-- The routing decision, in under six lines. If an agent reads only this
     section, it should still land on the right table at the right grain. -->

**Business context:** <!-- one sentence: what this domain measures and who uses it -->

**Canonical source:** `<table>`
**Grain:** one row per <!-- person? person-month? job change? event? -->
**Person key:** <!-- the column that identifies a HUMAN, which may not be the obvious one -->
**As-of convention:** <!-- point-in-time snapshot, or activity window? -->

**Standard filter — apply unless you have a stated reason not to:**

```sql
WHERE <!-- the hygiene predicate that must almost always be present -->
```

---

## Required Filters

<!-- Every filter that must be applied, why, and what happens if it isn't.
     Quantify the consequence — "inflates by ~20%" lands harder than "may be
     inaccurate," and gives a reviewer something to check against. -->

| Filter | Why | If omitted |
|---|---|---|
| `<column> = '<value>'` | <!-- what it excludes --> | <!-- quantified consequence --> |
| | | |

---

## Canonical Tables

<!-- Only tables an agent should actually use. Do not inventory the schema. -->

### `<table_name>` — <!-- one-line purpose -->

- **Grain:** one row per <!-- ... -->
- **Row count (approx):** <!-- so an agent can sanity-check magnitude -->
- **Join keys:** <!-- column, and whether it is unique at this grain -->
- **Refresh:** <!-- cadence, and how late it lands -->
- **Key columns:** <!-- only the ones that matter, with what their values mean -->

---

## DO NOT USE

<!-- The highest-value section after Gotchas, and the one most often skipped.
     Every warehouse has plausible-looking tables that produce wrong answers.
     Naming them explicitly is what stops an agent from finding them by name
     similarity and using them in good faith. -->

| Table | Why not | Use instead |
|---|---|---|
| `<table>` | <!-- deprecated / stale / wrong grain / includes populations you don't want --> | `<table>` |
| | | |

---

## Gotchas

<!-- ⚠ THE MOST IMPORTANT SECTION IN THIS DOCUMENT.

     Everything above can be inferred from the schema. This cannot. These are
     the things that are true about YOUR data because of decisions your
     organization made — a migration, a policy change, a system that was
     retired, a column that means something different than its name suggests.

     The prompt that works: what would you tell a new analyst in week one so
     they don't embarrass themselves in front of a stakeholder?

     Write each one as a directive with its consequence. -->

### <!-- Short title, e.g. "The department column is deprecated" -->

**What:** <!-- the trap, stated plainly -->
**Why:** <!-- the organizational history that created it -->
**Do:**
```sql
-- the correct pattern
```
**Don't:**
```sql
-- the tempting wrong pattern, and what it silently produces
```

<!-- Repeat. Aim for 5-10. Prompts, if you're stuck:

     - A column whose name no longer matches its meaning
     - A migration that left two versions of the same thing in place
     - A population that is in the table but shouldn't be in the number
     - A join that looks safe and fans out
     - A date field that isn't the date people assume it is
     - A value that means "not applicable" rather than zero
     - A number that will never reconcile to a dashboard, and why that's expected
     - Something that changed on a specific date, breaking trend comparisons -->

---

## Measures

<!-- The named definitions this domain owns. If two teams compute the same
     measure differently, both definitions go here with their names — do not
     silently pick a winner in a reference doc. That's a governance decision. -->

### <measure name>

- **Definition:** <!-- in words -->
- **Numerator:** <!-- ... -->
- **Denominator:** <!-- beginning / ending / average population — be specific -->
- **Population:** <!-- who is in scope -->
- **Known variants:** <!-- other definitions in use, and who uses them -->
- **Reconciles to:** <!-- which dashboard or report, or "does not reconcile — see Gotchas" -->

---

## Common Query Patterns

<!-- Working SQL for the questions this domain actually gets asked. Each should
     run as written. Copy-paste-able beats illustrative. -->

### <!-- e.g. "Headcount as of a date" -->

```sql

```

---

## Cross-References

<!-- Where this domain meets another, and what breaks at the seam. -->

| Joining to | On | Watch out for |
|---|---|---|
| `<domain>` | `<key>` | <!-- grain mismatch, timing difference, population difference --> |

---

## Escalate, Don't Guess

<!-- Questions this doc does not answer and should not be used to answer. -->

- <!-- e.g. cuts by protected characteristics → route to <governance path> -->
- <!-- e.g. individual-level performance questions → route to <owner> -->

---

## Open Questions

<!-- Honest gaps. A doc that admits what it doesn't cover is more trustworthy
     than one that implies completeness. Each entry is a candidate for the next
     correction-harvesting pass. -->

- [ ] <!-- ... -->

<!-- ============ COPY TO HERE ============ -->

---

## Before you call it done

- [ ] An agent that read **only Quick Reference** would pick the right table
- [ ] Every required filter states what happens if it's omitted, quantified
- [ ] Gotchas contains at least one thing that is **not inferable from the schema**
- [ ] Every measure names its denominator explicitly
- [ ] Query patterns run as written — you executed them, you didn't eyeball them
- [ ] `owner` is a named human
- [ ] Nothing in the doc is stated more than once

Then test it: hand the doc and a question to an agent with no other context, and
see whether it lands on the right table. If it doesn't, the doc is the problem —
that failure is the most useful signal you'll get.
