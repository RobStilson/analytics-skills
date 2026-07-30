---
name: skill-freshness-check
version: 0.1.0
description: "Detect and repair drift between analytics skill documentation and the data model it describes. IF a reference doc, metric definition, or skill file is being relied on, or a data-model change is being made — THEN invoke this skill to verify the docs still match reality. Use it on a schedule and on every PR that touches a reporting model, because skill docs describing a live warehouse go wrong within weeks without active maintenance. DO NOT treat this as optional cleanup work; unmaintained skills degrade accuracy faster than having no skills at all is usually assumed to."
---

# Skill Freshness Check

## Overview

Skill docs describe a data model that changes continuously. Without deliberate
maintenance they go stale quickly, and stale docs are worse than absent ones —
an absent doc makes the agent search and flag uncertainty, while a stale doc makes
it confidently route to a table that no longer means what the doc says.

One team measured this directly: offline accuracy drifted from roughly 95% at
launch to roughly 65% over a single month before they treated maintenance as an
engineering problem rather than documentation hygiene. Those are one organization's
internal numbers on their own eval set, not a general benchmark — but the shape
of the decay is the part to take seriously, and the decay is not slow.

The structural fix is **colocation**: the skill markdown lives in the same repo
as the transformation models, so the PR that changes a model is the PR that
updates the doc describing it.

## When to Use

| Trigger | Scope of check |
|---|---|
| A PR touches a reporting model, metric definition, or schema | Targeted — the affected docs only |
| Scheduled cadence (weekly or biweekly) | Full sweep |
| An eval that previously passed now fails | Targeted — trace to the doc that changed |
| A reference doc has not been touched in a quarter | Targeted — presumption of staleness |
| The agent fell back to raw exploration for a documented domain | Targeted — the routing is broken |
| Onboarding a new domain | Full check before the domain goes live to stakeholders |

**DO NOT** run a full sweep as a reflex on every session. It is expensive and
generates noise that trains people to ignore the output.

## Process

### 1. Verify referential integrity

For every reference doc, check mechanically:

- Does every named table still exist?
- Does every named column still exist, with the same type?
- Have any named columns been superseded by a versioned replacement — an
  `org_unit_v2` alongside a still-present but half-populated `department`?
- Are any tables now marked deprecated upstream?
- Do documented join keys still hold uniqueness at the documented grain?

This part is scriptable and should be scripted. Human attention is wasted on it.

### 2. Verify semantic integrity

Harder, and not scriptable. Ask of each doc:

- Does the stated **grain** still match what one row represents?
- Does the stated **scope/exclusion** still match the actual filter logic upstream?
- Has a **business definition** changed without the column changing? A measure
  renamed from "attrition" to "regrettable attrition" upstream leaves the schema
  untouched and the doc silently wrong.
- Are the documented **gotchas** still real? Fixed upstream issues leave behind
  warnings that push the agent away from now-correct tables.
- Has an organizational restatement changed what a hierarchy cut means historically?

### 3. Verify against evals

The most reliable signal. Re-run the domain's eval slice:

- Which previously-passing evals now fail?
- Trace each failure to the specific doc line that is now wrong.
- A failure the docs cannot explain means the eval itself may have drifted — check
  whether it was pinned to a snapshot date, and pin it if not.

### 4. Repair, in the same PR as the change

The fix path must be boring or it will not happen: edit the markdown, merge,
auto-sync everywhere. If updating a doc requires a separate ticket, a separate
review, and a separate deploy, the docs will be stale permanently.

**Enforcement that works:**
- A review hook that flags any reporting-model change not accompanied by a skill-file change
- CI that fails when a doc references a table or column that no longer exists
- Domain ownership: a named human per reference doc, not a shared inbox

### 5. Prune

Freshness is not only about adding. Remove:

- Warnings about failure modes the current model generation no longer exhibits
- Scaffolding written to work around a bug that has been fixed
- Documented workarounds for tables that have been deprecated

Docs that only grow become docs nobody reads. Length is not thoroughness.

## Rationalizations

| Excuse | Rebuttal |
|---|---|
| "The doc is mostly right" | Mostly-right routing docs send the agent confidently to the wrong table. Partial correctness is not graceful here. |
| "I'll update the docs in a follow-up PR" | The follow-up PR is the one that never merges. Same diff or it does not happen. |
| "Nobody has complained, so it must be fine" | Silent wrongness generates no complaints by definition. Absence of complaints is not evidence of accuracy. |
| "Maintenance isn't real work" | It is the work that determines whether all the other work keeps functioning. Budget it explicitly. |
| "The model is smart enough to figure out the doc is stale" | It will trust the doc. That is what the doc is for. |
| "Adding more detail will make it more robust" | Past a point, added detail makes docs longer without making them better, and can make retrieval worse. Prune as well as add. |

## Red Flags

- A reference doc's last commit predates the last schema change to its tables
- Eval pass rate declining gradually over weeks with no single obvious cause
- The agent routing to raw exploration in a domain that has a reference doc
- A doc whose gotchas section has only grown for six months
- Two reference docs describing the same table differently
- Nobody can name the owner of a given reference doc

## Verification

- [ ] Every referenced table and column was checked for existence, ideally by script
- [ ] Grain, scope, and business-definition statements were re-read against current logic
- [ ] The domain eval slice was re-run and failures traced to specific doc lines
- [ ] Repairs shipped in the same PR as the model change that caused them
- [ ] Obsolete scaffolding was pruned, not just supplemented
- [ ] Each doc has a named owner
