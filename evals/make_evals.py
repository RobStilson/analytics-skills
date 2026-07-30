#!/usr/bin/env python3
"""
Write the per-skill eval slices from ground_truth.json.

Ground-truth figures are interpolated from the generated file rather than
hand-typed, so an eval can never quote a number the warehouse does not produce.

Usage:
    python make_evals.py        # run make_ground_truth.py first
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GT = json.load(open(os.path.join(HERE, "ground_truth.json")))


def write(skill, evals):
    d = os.path.join(HERE, skill)
    os.makedirs(d, exist_ok=True)
    payload = {
        "skill_name": skill,
        "warehouse_seed": GT["_meta"]["warehouse_seed"],
        "as_of": GT["_meta"]["as_of"],
        "evals": evals,
    }
    with open(os.path.join(d, "evals.json"), "w") as f:
        json.dump(payload, f, indent=2)
    neg = sum(1 for e in evals if e.get("negative"))
    print(f"  {skill:<26} {len(evals):>2} evals ({neg} negative)")


hc = GT["headcount"]
at = GT["attrition_2025"]
dc = GT["deprecated_column"]
fo = GT["fanout"]
sc = GT["small_cells"]
sb = GT["selection_bias"]
it = GT["immortal_time"]
ic = GT["instrument_change"]
rh = GT["rehires"]

# ---------------------------------------------------------------- navigation
write("warehouse-navigation", [
    {
        "id": "nav-01", "type": "deterministic", "trap": "entity ambiguity",
        "prompt": "How many employees do we have?",
        "ground_truth": hc["canonical"],
        "acceptable_alternatives": [hc["canonical_excl_leave"]],
        "expected_output": (
            f"Uses {hc['canonical_table']} at the as-of date, filtered to Regular "
            f"workers, counting distinct people. Answer is {hc['canonical']:,} "
            f"(or {hc['canonical_excl_leave']:,} if On Leave is excluded, stated explicitly)."),
        "assertions": [
            f"The reported number is {hc['canonical']:,} or {hc['canonical_excl_leave']:,}",
            f"The number is NOT {hc['wrong_all_worker_types']:,} (includes contingent workers)",
            f"The number is NOT {hc['wrong_stale_rollup']:,} (stale rollup)",
            f"The number is NOT {hc['wrong_job_record_rows']:,} (job-change rows)",
            "The response states whether workers on leave are included",
            "The response states that contingent workers are excluded",
        ],
    },
    {
        "id": "nav-02", "type": "deterministic", "trap": "grain fan-out",
        "prompt": "Give me a list of employees with their job history, and tell me the headcount.",
        "ground_truth": hc["canonical"],
        "expected_output": (
            f"Joins to fct_job_record without letting the {fo['inflation_factor']}x "
            f"fan-out corrupt the count. Headcount stays ~{hc['canonical']:,}, not "
            f"{fo['naive_join_rows']:,}."),
        "assertions": [
            f"The headcount figure is not {fo['naive_join_rows']:,} or near it",
            "The response acknowledges that fct_job_record has one row per job change",
            "Distinct people are counted rather than joined rows",
        ],
    },
    {
        "id": "nav-03", "type": "deterministic", "trap": "staleness",
        "prompt": "Break down headcount by department.",
        "ground_truth": dc["people_dropped_by_legacy_cut"],
        "expected_output": (
            f"Uses {dc['replacement']}, not the deprecated {dc['column']} column "
            f"({dc['pct_populated']}% populated). A legacy cut silently drops "
            f"{dc['people_dropped_by_legacy_cut']:,} people."),
        "assertions": [
            f"The response uses {dc['replacement']} rather than {dc['column']}",
            f"If {dc['column']} is used or mentioned, the response flags that it is "
            f"only {dc['pct_populated']}% populated",
            "The breakdown total reconciles to the overall headcount",
            f"Org units with no legacy label ({', '.join(dc['org_units_with_no_legacy_label'])}) appear in the output",
        ],
    },
    {
        "id": "nav-04", "type": "deterministic", "trap": "stale rollup",
        "prompt": "What does rpt_headcount_daily say our headcount is, and should I use it?",
        "ground_truth": hc["stale_rollup_last_refresh"],
        "expected_output": (
            f"Reports the rollup value but flags that it last refreshed on "
            f"{hc['stale_rollup_last_refresh']} and should not be used as current."),
        "assertions": [
            f"The response identifies the last refresh date as {hc['stale_rollup_last_refresh']}",
            "The response recommends against using it as a current figure",
            "The response names a canonical alternative source",
        ],
    },
    {
        "id": "nav-05", "type": "deterministic", "trap": "rehire duplicates",
        "prompt": "How many distinct people have ever worked here?",
        "ground_truth": rh["distinct_employee_number"],
        "expected_output": (
            f"Counts distinct {rh['person_key']} ({rh['distinct_employee_number']:,}), "
            f"not worker_id ({rh['distinct_worker_id']:,}). "
            f"{rh['duplicate_humans']} humans hold two worker_ids after rehire."),
        "assertions": [
            f"The reported number is {rh['distinct_employee_number']:,}",
            f"The number is NOT {rh['distinct_worker_id']:,}",
            "The response explains that rehires produce multiple worker_id values",
        ],
    },
    {
        "id": "nav-06", "type": "graded", "trap": "retrieval failure", "negative": True,
        "prompt": "Pull the exit survey responses for people who left last year.",
        "expected_output": (
            "fct_exit_survey is one of the empty decoy tables. The correct response "
            "reports that it contains no data rather than fabricating results or "
            "silently substituting another table."),
        "assertions": [
            "The response reports that the table is empty or has no rows",
            "The response does NOT fabricate exit survey results",
            "The response does NOT silently substitute a different table without saying so",
        ],
    },
])

# ------------------------------------------------------------------- intake
write("question-intake", [
    {
        "id": "int-01", "type": "graded", "trap": "population ambiguity",
        "prompt": "How many people work here?",
        "expected_output": (
            "Clarifies before answering: which worker types count, whether workers "
            "on leave are included, and the as-of date."),
        "assertions": [
            "The response asks about worker type or population scope before committing to a number",
            "The response asks about, or explicitly states, the as-of date",
            "The response does not silently pick a default and present it as the answer",
        ],
    },
    {
        "id": "int-02", "type": "graded", "trap": "measure ambiguity",
        "prompt": "What's our attrition rate?",
        "expected_output": (
            "Surfaces that attrition has several definitions — voluntary vs "
            "involuntary vs all, regrettable vs not — and that the denominator "
            "choice changes the answer materially."),
        "assertions": [
            "The response distinguishes at least two attrition definitions",
            "The response raises the denominator choice",
            "The response asks for or specifies a time window",
        ],
    },
    {
        "id": "int-03", "type": "graded", "trap": "over-clarification", "negative": True,
        "prompt": (
            "As of 2026-06-30, how many Regular workers with employment_status of "
            "Active or On Leave are in dim_worker_snapshot? Count distinct people."),
        "expected_output": (
            "The question is already fully specified. The correct response answers "
            f"it ({hc['canonical']:,}) without a round of clarifying questions."),
        "assertions": [
            f"The response provides the number {hc['canonical']:,}",
            "The response does NOT ask clarifying questions about population or as-of date",
            "The response answers in a single turn",
        ],
    },
    {
        "id": "int-04", "type": "graded", "trap": "decision context",
        "prompt": "Can you get me attrition by manager? I need it for a meeting.",
        "expected_output": (
            "Asks what decision the analysis feeds, and surfaces that manager-level "
            "cuts hit small cells and confounded manager effects."),
        "assertions": [
            "The response asks what the analysis will be used for",
            "The response raises small group sizes or confounding at the manager level",
        ],
    },
])

# ---------------------------------------------------------------- uncertainty
write("uncertainty-reporting", [
    {
        "id": "unc-01", "type": "deterministic", "trap": "small cells",
        "prompt": "Show me headcount by org unit and location.",
        "ground_truth": sc["crosstab_cells_below_threshold"],
        "expected_output": (
            f"Suppresses the {sc['crosstab_cells_below_threshold']} cells below "
            f"n={sc['suppression_threshold']}, including cells with n=1."),
        "assertions": [
            f"Cells with fewer than {sc['suppression_threshold']} people are suppressed",
            "Suppressed cells are labelled as suppressed rather than omitted silently",
            "The response notes the risk of recovering a suppressed cell by subtraction",
        ],
    },
    {
        "id": "unc-02", "type": "deterministic", "trap": "denominator disclosure",
        "prompt": "What was our attrition rate in 2025?",
        "ground_truth": at["rate_on_average_pct"],
        "acceptable_alternatives": [at["rate_on_beginning_pct"], at["rate_on_ending_pct"]],
        "expected_output": (
            f"Reports a rate WITH its denominator named. Average headcount gives "
            f"{at['rate_on_average_pct']}%, beginning {at['rate_on_beginning_pct']}%, "
            f"ending {at['rate_on_ending_pct']}% — a "
            f"{round(at['rate_on_beginning_pct'] - at['rate_on_ending_pct'], 1)}-point spread."),
        "assertions": [
            f"The numerator ({at['separations']} separations) is stated",
            "The denominator is explicitly named",
            "The response acknowledges that the denominator choice changes the rate",
        ],
    },
    {
        "id": "unc-03", "type": "graded", "trap": "instability",
        "prompt": (
            f"What is the attrition rate for org unit {sc['smallest_org_unit'][0]}?"),
        "ground_truth": sc["smallest_org_unit"][1],
        "expected_output": (
            f"That unit has only {sc['smallest_org_unit'][1]} people. Any rate is "
            f"unstable and must carry an interval and an instability flag."),
        "assertions": [
            f"The response reports the group size ({sc['smallest_org_unit'][1]})",
            "The response flags the estimate as unstable",
            "The response provides an interval or an explicit statement of imprecision",
        ],
    },
    {
        "id": "unc-04", "type": "graded", "trap": "multiplicity",
        "prompt": "Which org unit has the worst attrition? Rank them.",
        "expected_output": (
            "Ranking 14 org units is 14 comparisons. Extremes appear by "
            "construction. Requires disclosure, and ideally shrinkage."),
        "assertions": [
            "The response states how many groups were compared",
            "The response cautions against reading the extremes as a performance ranking",
            "The response applies shrinkage, intervals, or an explicit exploratory label",
        ],
    },
    {
        "id": "unc-05", "type": "graded", "trap": "instrument change",
        "prompt": "Has engagement improved since 2023?",
        "ground_truth": ic["scale_changed_in"],
        "expected_output": (
            f"The scale changed in {ic['scale_changed_in']} from 1-"
            f"{ic['waves'][0]['scale_max']} to 1-{ic['waves'][-1]['scale_max']}. "
            f"The apparent rise is a scale artifact, not a change in engagement."),
        "assertions": [
            f"The response identifies the scale change in {ic['scale_changed_in']}",
            "The response declines to report a raw cross-year comparison, or rescales first",
            "The response mentions response rates",
        ],
    },
    {
        "id": "unc-06", "type": "graded", "trap": "clean finding", "negative": True,
        "prompt": "How many Regular workers were active on 2026-06-30? Just the count.",
        "ground_truth": hc["canonical"],
        "expected_output": (
            f"A well-defined count on a large population. The correct response gives "
            f"{hc['canonical']:,} plainly, without hedging it into uselessness."),
        "assertions": [
            f"The response gives {hc['canonical']:,}",
            "The response does NOT attach a confidence interval to a complete-population count",
            "The response is not padded with unnecessary caveats",
        ],
    },
])

# ---------------------------------------------------------------- causal
write("causal-claim-guardrail", [
    {
        "id": "cau-01", "type": "graded", "trap": "selection bias", "flagship": True,
        "prompt": (
            "Did the Emerging Leaders Program reduce attrition? Enrolled employees "
            "have much lower attrition than non-enrolled."),
        "ground_truth": {
            "true_effect": sb["TRUE_CAUSAL_EFFECT"],
            "naive_gap_pts": sb["naive_gap_pts"],
            "tier_adjusted_gap_pts": sb["tier_adjusted_gap_pts"],
        },
        "expected_output": (
            f"The true causal effect is {sb['TRUE_CAUSAL_EFFECT']}. The naive gap is "
            f"{sb['naive_gap_pts']} points; adjusting for performance tier leaves "
            f"{sb['tier_adjusted_gap_pts']} points of residual confounding from an "
            f"unobserved trait. The correct response refuses the causal claim, names "
            f"selection ({sb['pct_manager_nominated']}% manager-nominated) as the "
            f"alternative explanation, and specifies the design that would settle it."),
        "assertions": [
            "The response does NOT claim the program reduced or caused lower attrition",
            "The response names selection into treatment as an alternative explanation",
            "The response references that enrolment was predominantly manager-nominated",
            "The response distinguishes observation from interpretation",
            "The response names a specific design (randomized or staggered rollout, "
            "difference-in-differences, matching) that would license a causal claim",
            "If the response adjusts for performance tier, it also states that "
            "residual confounding may remain rather than treating the adjusted "
            "estimate as causal",
        ],
    },
    {
        "id": "cau-02", "type": "graded", "trap": "immortal time",
        "prompt": (
            "People who received the 3-Year Service Award have far lower attrition. "
            "Should we expand recognition programs to improve retention?"),
        "ground_truth": {
            "award_attrition_pct": it["award_attrition_pct"],
            "no_award_attrition_pct": it["no_award_attrition_pct"],
        },
        "expected_output": (
            f"Award recipients show {it['award_attrition_pct']}% attrition vs "
            f"{it['no_award_attrition_pct']}%, but eligibility requires surviving to "
            f"three years. The outcome is embedded in the eligibility criterion."),
        "assertions": [
            "The response identifies that eligibility requires surviving a tenure threshold",
            "The response names immortal time bias, or describes the mechanism accurately",
            "The response does NOT recommend expanding the program on this evidence",
        ],
    },
    {
        "id": "cau-03", "type": "graded", "trap": "reverse causality",
        "prompt": "Our survey shows engagement predicts retention. So engagement drives retention, right?",
        "expected_output": (
            "Raises reverse causality: employees who have already decided to leave "
            "report lower engagement. Cross-sectional survey data cannot separate the "
            "directions."),
        "assertions": [
            "The response raises reverse causality explicitly",
            "The response does NOT endorse the causal framing",
            "The response explains what design would separate the directions",
        ],
    },
    {
        "id": "cau-04", "type": "graded", "trap": "confounded manager effects",
        "prompt": "Attrition varies a lot by manager. Which managers are causing turnover?",
        "expected_output": (
            "Manager, team, function, location and job level are collinear. The "
            "available design cannot attribute variance to the manager."),
        "assertions": [
            "The response names at least two variables confounded with manager",
            "The response does NOT attribute attrition to individual managers",
            "The response flags that evaluating named individuals requires escalation",
        ],
    },
    {
        "id": "cau-05", "type": "graded", "trap": "legitimate design", "negative": True,
        "prompt": (
            "We randomly assigned half of new hires to an extended onboarding program "
            "and the other half to standard onboarding. The extended group had "
            "6-point lower 12-month attrition. Can we say the program worked?"),
        "expected_output": (
            "Random assignment licenses a causal claim. The correct response says so "
            "plainly, then notes the assumptions worth verifying (assignment integrity, "
            "attrition from the study itself, power) — it does NOT reflexively block."),
        "assertions": [
            "The response permits a causal interpretation",
            "The response does NOT rewrite the finding into purely associational language",
            "The response names assumptions worth verifying rather than blocking the claim",
        ],
    },
])

# ------------------------------------------------------------------- review
write("adversarial-sql-review", [
    {
        "id": "rev-01", "type": "graded", "trap": "fan-out",
        "prompt": (
            "Review this query:\n"
            "SELECT count(*) AS headcount FROM dim_worker w "
            "JOIN fct_job_record j ON j.worker_id = w.worker_id;"),
        "ground_truth": {"returns": fo["naive_join_rows"], "correct": hc["canonical"]},
        "expected_output": (
            f"Blocking finding: the join fans out {fo['inflation_factor']}x, returning "
            f"{fo['naive_join_rows']:,} instead of a headcount near {hc['canonical']:,}."),
        "assertions": [
            "The finding is classified as blocking",
            "The response identifies the fan-out from the job-record grain",
            "The response states the effect on the number",
            "The response proposes an as-of or is_current filter",
        ],
    },
    {
        "id": "rev-02", "type": "graded", "trap": "missing filter",
        "prompt": (
            "Review this query:\n"
            "SELECT count(*) FROM dim_worker_snapshot "
            "WHERE snapshot_date = DATE '2026-06-30';"),
        "ground_truth": {"returns": hc["wrong_all_worker_types"], "correct": hc["canonical"]},
        "expected_output": (
            f"Missing worker_type and employment_status filters. Returns "
            f"{hc['wrong_all_worker_types']:,} instead of {hc['canonical']:,}."),
        "assertions": [
            "The response identifies the missing worker_type filter",
            "The response identifies the missing employment_status filter",
            "The finding is classified as blocking",
        ],
    },
    {
        "id": "rev-03", "type": "graded", "trap": "denominator",
        "prompt": (
            "Review this attrition query:\n"
            "SELECT count(*) * 100.0 / (SELECT count(*) FROM dim_worker_snapshot "
            "WHERE snapshot_date = DATE '2025-12-31') FROM fct_separation "
            "WHERE year(separation_date) = 2025;"),
        "expected_output": (
            "Uses ending headcount as the denominator without saying so, and the "
            "denominator itself lacks worker_type and status filters."),
        "assertions": [
            "The response identifies that the denominator is ending headcount",
            "The response notes the denominator is not filtered consistently with the numerator",
            "The response notes the denominator is not disclosed in the output",
        ],
    },
    {
        "id": "rev-04", "type": "graded", "trap": "clean query", "negative": True,
        "prompt": (
            "Review this query:\n"
            "SELECT count(DISTINCT employee_number) AS headcount "
            "FROM dim_worker_snapshot WHERE snapshot_date = DATE '2026-06-30' "
            "AND worker_type = 'Regular' AND employment_status IN ('Active','On Leave');"),
        "ground_truth": hc["canonical"],
        "expected_output": (
            f"This query is correct and returns {hc['canonical']:,}. The correct review "
            f"passes it, records what was verified, and does not manufacture findings."),
        "assertions": [
            "The verdict is clear-to-deliver",
            "There are no blocking findings",
            "The response records what it verified rather than returning an empty review",
        ],
    },
])

# ---------------------------------------------------------------- provenance
write("provenance-footer", [
    {
        "id": "prv-01", "type": "graded", "trap": "footer omission",
        "prompt": "How many employees do we have? Just give me the number, I'm in a hurry.",
        "expected_output": (
            f"Answers {hc['canonical']:,} AND attaches a footer despite the time "
            f"pressure. Short answers are the ones most likely to be forwarded."),
        "assertions": [
            "A provenance footer is present",
            "The footer names the source table",
            "The footer states a confidence level",
            "The footer states the population counted",
        ],
    },
    {
        "id": "prv-02", "type": "graded", "trap": "source tier",
        "prompt": (
            "Combine headcount from dim_worker_snapshot with the raw staging table "
            "stg_workday_worker_raw and tell me the total."),
        "expected_output": (
            "An answer touching a raw staging table is a raw-exploration answer. The "
            "footer must reflect the LOWEST tier touched, not the highest."),
        "assertions": [
            "The source tier is reported as raw exploration",
            "The confidence is not reported as High",
        ],
    },
    {
        "id": "prv-03", "type": "deterministic", "trap": "freshness",
        "prompt": "What is our headcount, and how fresh is that data?",
        "ground_truth": GT["_meta"]["as_of"],
        "expected_output": (
            f"Freshness is read from the maximum date in the result "
            f"({GT['_meta']['as_of']}), not from a documented pipeline schedule."),
        "assertions": [
            f"The freshness date reported is {GT['_meta']['as_of']}",
            "The date is derived from the data rather than asserted from documentation",
        ],
    },
])

print("\nGround truth interpolated from ground_truth.json — no figure hand-typed.")
