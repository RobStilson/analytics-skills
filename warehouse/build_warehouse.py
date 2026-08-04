#!/usr/bin/env python3
"""
Build the Vibe Analytics synthetic people-analytics warehouse.

This warehouse is DELIBERATELY MESSY. The ambiguity is the point: a clean
warehouse teaches nothing, because there is nothing for a skill to resolve.

Engineered failure modes (see facilitator/GROUND_TRUTH.md for the answer key):
  1. Grain fan-out        fct_job_record is one row per job CHANGE, not per person
  2. Entity ambiguity     four plausible sources for "headcount", all disagreeing
  3. Staleness            `department` superseded by `org_unit_v2`, half-populated
  4. Worker type          contingent workers sit in the same tables as employees
  5. Rehire duplicates    same human, two worker_ids; employee_number is the person key
  6. Denominator choice   attrition rate varies by which denominator is used
  7. Small cells          several org units below the suppression threshold
  8. Selection bias       leadership program with a TRUE effect of zero
  9. Instrument change    engagement scale moved 1-5 -> 1-7 mid-series
 10. Immortal time        tenure-milestone award requires surviving to eligibility
 11. Retrieval failure    44 tables, most of them plausible decoys

Reproducible: fixed seed. Rebuild with `python build_warehouse.py`.
"""

import os
import sys

try:
    import numpy as np
    import pandas as pd
    import duckdb
except ImportError as e:
    sys.exit(
        f"\nMissing dependency: {e.name or e}\n"
        "  Install them with:  pip install duckdb pandas numpy\n"
        "  (Some systems need: pip install duckdb pandas numpy --break-system-packages)\n")

SEED = 20260730
rng = np.random.default_rng(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "people_analytics.duckdb")

N_WORKERS = 5200
AS_OF = pd.Timestamp("2026-06-30")
HISTORY_START = pd.Timestamp("2021-01-01")

# ---------------------------------------------------------------- reference data

LOCATIONS = [
    ("LOC001", "Atlanta", "GA", "US", "Americas"),
    ("LOC002", "Denver", "CO", "US", "Americas"),
    ("LOC003", "Boston", "MA", "US", "Americas"),
    ("LOC004", "Austin", "TX", "US", "Americas"),
    ("LOC005", "Dublin", None, "IE", "EMEA"),
    ("LOC006", "Singapore", None, "SG", "APAC"),
    ("LOC007", "Remote-US", None, "US", "Americas"),
]

# org_unit_v2 is current. `department` below is the frozen legacy label.
ORG_UNITS = [
    ("OU-1000", "Engineering", "Technology", "Engineering"),
    ("OU-1100", "Platform Engineering", "Technology", "Engineering"),
    ("OU-1200", "Data & Analytics", "Technology", "Engineering"),
    ("OU-1300", "Security Engineering", "Technology", None),          # no legacy label
    ("OU-2000", "Sales", "Go-To-Market", "Sales"),
    ("OU-2100", "Customer Success", "Go-To-Market", "Sales"),
    ("OU-2200", "Marketing", "Go-To-Market", "Marketing"),
    ("OU-3000", "Finance", "Corporate", "Finance"),
    ("OU-3100", "People Operations", "Corporate", "HR"),
    ("OU-3200", "Legal", "Corporate", "Legal"),
    ("OU-3300", "Corporate Development", "Corporate", None),          # small + no legacy
    ("OU-4000", "Manufacturing Ops", "Operations", "Operations"),
    ("OU-4100", "Supply Chain", "Operations", "Operations"),
    ("OU-4200", "Quality Assurance", "Operations", None),             # small
]

JOB_PROFILES = [
    ("JP-01", "Software Engineer I", "Individual Contributor", 1),
    ("JP-02", "Software Engineer II", "Individual Contributor", 2),
    ("JP-03", "Senior Software Engineer", "Individual Contributor", 3),
    ("JP-04", "Staff Engineer", "Individual Contributor", 4),
    ("JP-05", "Engineering Manager", "People Manager", 4),
    ("JP-06", "Data Analyst", "Individual Contributor", 2),
    ("JP-07", "Data Scientist", "Individual Contributor", 3),
    ("JP-08", "Account Executive", "Individual Contributor", 2),
    ("JP-09", "Sales Manager", "People Manager", 4),
    ("JP-10", "Customer Success Manager", "Individual Contributor", 2),
    ("JP-11", "Financial Analyst", "Individual Contributor", 2),
    ("JP-12", "HR Business Partner", "Individual Contributor", 3),
    ("JP-13", "Counsel", "Individual Contributor", 4),
    ("JP-14", "Production Technician", "Individual Contributor", 1),
    ("JP-15", "Supply Chain Analyst", "Individual Contributor", 2),
    ("JP-16", "Director", "People Manager", 5),
    ("JP-17", "Vice President", "Executive", 6),
]

WORKER_TYPES = ["Regular", "Contingent", "Intern"]
EMPLOYMENT_STATUSES = ["Active", "On Leave", "Terminated"]


def build_workers():
    """One row per WORKER_ID. Rehires produce two worker_ids for one human."""
    n = N_WORKERS
    ou_codes = [o[0] for o in ORG_UNITS]

    # Org assignment: deliberately uneven so some units land under the
    # suppression threshold.
    ou_weights = np.array(
        [0.14, 0.10, 0.08, 0.013, 0.15, 0.08, 0.06,
         0.06, 0.04, 0.02, 0.0012, 0.13, 0.09, 0.015]
    )
    ou_weights = ou_weights / ou_weights.sum()

    worker_type = rng.choice(WORKER_TYPES, size=n, p=[0.82, 0.14, 0.04])
    org_unit = rng.choice(ou_codes, size=n, p=ou_weights)
    location = rng.choice([l[0] for l in LOCATIONS], size=n,
                          p=[0.20, 0.14, 0.12, 0.15, 0.10, 0.09, 0.20])
    job_profile = rng.choice([j[0] for j in JOB_PROFILES], size=n)

    # Hire dates spread across the history window, weighted toward recent
    # (a growing company -> depresses average tenure independent of behavior).
    days_span = (AS_OF - HISTORY_START).days
    u = rng.beta(2.6, 1.15, size=n)
    hire_offsets = (u * days_span).astype(int)
    hire_date = [HISTORY_START + pd.Timedelta(days=int(d)) for d in hire_offsets]

    # Latent, UNOBSERVED propensity to stay. Drives both program nomination and
    # attrition, and never appears in the warehouse -> residual confounding that
    # no amount of adjustment can remove.
    latent_commitment = rng.normal(0, 1, size=n)

    # Observed performance tier: correlated with the latent trait, so adjusting
    # for it removes MOST but not all of the confounding.
    perf_noise = rng.normal(0, 1, size=n)
    perf_score = 0.75 * latent_commitment + 0.66 * perf_noise
    perf_tier = np.digitize(perf_score, np.quantile(perf_score, [0.15, 0.50, 0.85])) + 1

    employee_number = np.arange(100000, 100000 + n)

    df = pd.DataFrame({
        "worker_id": [f"W{100000 + i}" for i in range(n)],
        "employee_number": [f"E{e}" for e in employee_number],
        "worker_type": worker_type,
        "home_org_unit": org_unit,
        "location_id": location,
        "job_profile_id": job_profile,
        "hire_date": hire_date,
        "_latent_commitment": latent_commitment,
        "_perf_tier": perf_tier,
    })
    return df


def apply_separations(df):
    """Terminations. Attrition depends on tenure, org, perf tier and the latent trait."""
    n = len(df)
    tenure_days = (AS_OF - pd.to_datetime(df["hire_date"])).dt.days.to_numpy()

    base = -2.05
    logit = (
        base
        - 0.55 * df["_latent_commitment"].to_numpy()
        - 0.22 * (df["_perf_tier"].to_numpy() - 2.5)
        + 0.40 * (tenure_days < 400).astype(float)
        + 0.30 * (df["home_org_unit"].isin(["OU-2000", "OU-4000"])).astype(float)
        + 0.55 * (df["worker_type"] == "Contingent").astype(float)
        + rng.normal(0, 0.45, size=n)
    )
    p_sep = 1 / (1 + np.exp(-logit))
    separated = rng.random(n) < p_sep

    sep_date = []
    for i in range(n):
        if not separated[i]:
            sep_date.append(pd.NaT)
            continue
        hd = pd.Timestamp(df["hire_date"].iloc[i])
        span = (AS_OF - hd).days
        if span <= 45:
            sep_date.append(pd.NaT)
            continue
        off = int(rng.uniform(0.12, 1.0) * span)
        sep_date.append(hd + pd.Timedelta(days=off))

    df = df.copy()
    df["separation_date"] = sep_date
    df["is_separated"] = df["separation_date"].notna()

    # Voluntary vs involuntary; regrettable is a subset of voluntary.
    vol = rng.random(n) < 0.74
    df["separation_type"] = np.where(
        df["is_separated"], np.where(vol, "Voluntary", "Involuntary"), None
    )
    regrettable = (df["_perf_tier"] >= 3) & (df["separation_type"] == "Voluntary")
    df["is_regrettable"] = np.where(df["is_separated"], regrettable, None)

    # Employment status as of AS_OF. ~4% of survivors are on leave and still employed.
    status = np.where(df["is_separated"], "Terminated", "Active")
    on_leave = (~df["is_separated"]) & (rng.random(n) < 0.042)
    status = np.where(on_leave, "On Leave", status)
    df["employment_status"] = status
    return df


def add_rehires(df):
    """~2.2% of separated workers return under a NEW worker_id, same employee_number.

    Counting DISTINCT worker_id overcounts people. employee_number is the person key.
    """
    sep = df[df["is_separated"]].copy()
    n_rehire = int(len(sep) * 0.30)
    picks = sep.sample(n=n_rehire, random_state=SEED)

    rows = []
    for i, (_, r) in enumerate(picks.iterrows()):
        gap = int(rng.uniform(120, 500))
        new_hire = pd.Timestamp(r["separation_date"]) + pd.Timedelta(days=gap)
        if new_hire >= AS_OF - pd.Timedelta(days=30):
            continue
        rows.append({
            "worker_id": f"W{900000 + i}",
            "employee_number": r["employee_number"],   # SAME human
            "worker_type": "Regular",
            "home_org_unit": r["home_org_unit"],
            "location_id": r["location_id"],
            "job_profile_id": r["job_profile_id"],
            "hire_date": new_hire,
            "_latent_commitment": r["_latent_commitment"],
            "_perf_tier": r["_perf_tier"],
            "separation_date": pd.NaT,
            "is_separated": False,
            "separation_type": None,
            "is_regrettable": None,
            "employment_status": "Active",
        })
    return pd.concat([df, pd.DataFrame(rows)], ignore_index=True)


def build_job_records(df):
    """THE FAN-OUT TRAP: one row per job CHANGE, effective-dated.

    A naive COUNT(*) here materially overstates headcount.
    """
    recs = []
    for _, r in df.iterrows():
        hd = pd.Timestamp(r["hire_date"])
        end = pd.Timestamp(r["separation_date"]) if pd.notna(r["separation_date"]) else AS_OF
        span = max((end - hd).days, 1)
        n_changes = int(rng.poisson(0.9 * (span / 365.0)))
        n_changes = min(n_changes, 4)

        starts = [hd]
        for _ in range(n_changes):
            off = int(rng.uniform(0.15, 0.95) * span)
            starts.append(hd + pd.Timedelta(days=off))
        starts = sorted(set(starts))

        for i, s in enumerate(starts):
            e = starts[i + 1] - pd.Timedelta(days=1) if i + 1 < len(starts) else (
                pd.Timestamp(r["separation_date"]) if pd.notna(r["separation_date"])
                else pd.Timestamp("9999-12-31")
            )
            recs.append({
                "job_record_id": f"JR{len(recs) + 1:07d}",
                "worker_id": r["worker_id"],
                "employee_number": r["employee_number"],
                "org_unit_v2": r["home_org_unit"],
                "job_profile_id": r["job_profile_id"],
                "location_id": r["location_id"],
                "worker_type": r["worker_type"],
                "effective_start": s,
                "effective_end": e,
                "is_current": (i == len(starts) - 1) and not r["is_separated"],
                "change_reason": "Hire" if i == 0 else rng.choice(
                    ["Promotion", "Lateral Transfer", "Org Realignment", "Manager Change"]
                ),
            })
    return pd.DataFrame(recs)


def _month_end_freq():
    """'ME' since pandas 2.2; 'M' before that. Python 3.9 may pin an older pandas."""
    try:
        pd.date_range("2023-01-31", "2023-03-31", freq="ME")
        return "ME"
    except ValueError:
        return "M"


def build_snapshot(df):
    """CANONICAL headcount source: one row per worker per month-end."""
    months = pd.date_range("2023-01-31", AS_OF, freq=_month_end_freq())
    legacy_map = {o[0]: o[3] for o in ORG_UNITS}

    rows = []
    for _, r in df.iterrows():
        hd = pd.Timestamp(r["hire_date"])
        sd = pd.Timestamp(r["separation_date"]) if pd.notna(r["separation_date"]) else None
        for m in months:
            if hd > m:
                continue
            if sd is not None and sd <= m:
                continue
            status = "Active"
            if r["employment_status"] == "On Leave" and m == months[-1]:
                status = "On Leave"
            legacy = legacy_map.get(r["home_org_unit"])
            # STALENESS: the legacy `department` column stopped being maintained.
            # Only ~55% of rows carry it, and never for units created later.
            if legacy is not None and rng.random() < 0.55:
                dept = legacy
            else:
                dept = None
            rows.append({
                "snapshot_date": m,
                "worker_id": r["worker_id"],
                "employee_number": r["employee_number"],
                "worker_type": r["worker_type"],
                "employment_status": status,
                "org_unit_v2": r["home_org_unit"],
                "department": dept,          # DEPRECATED, half-populated
                "location_id": r["location_id"],
                "job_profile_id": r["job_profile_id"],
                "hire_date": hd,
                "fte": 1.0 if rng.random() > 0.07 else 0.5,
            })
    return pd.DataFrame(rows)


def build_program(df):
    """SELECTION-BIAS TRAP: Emerging Leaders Program.

    TRUE causal effect on attrition == 0. Nomination depends on performance tier
    (observed) AND latent commitment (unobserved). The naive comparison shows a
    large gap that is entirely selection.
    """
    elig = df[(df["worker_type"] == "Regular")].copy()
    logit = (
        -2.35
        + 0.95 * elig["_perf_tier"].to_numpy()
        + 0.62 * elig["_latent_commitment"].to_numpy()
        + rng.normal(0, 0.5, size=len(elig))
    )
    p = 1 / (1 + np.exp(-logit))
    enrolled = rng.random(len(elig)) < p

    rows = []
    for (_, r), en in zip(elig.iterrows(), enrolled):
        if not en:
            continue
        hd = pd.Timestamp(r["hire_date"])
        start = hd + pd.Timedelta(days=int(rng.uniform(120, 700)))
        if start >= AS_OF:
            continue
        rows.append({
            "enrollment_id": f"EN{len(rows) + 1:06d}",
            "worker_id": r["worker_id"],
            "program_code": "ELP",
            "program_name": "Emerging Leaders Program",
            "enrollment_date": start,
            "completion_status": rng.choice(["Completed", "In Progress", "Withdrawn"],
                                            p=[0.79, 0.15, 0.06]),
            "nomination_source": rng.choice(["Manager Nomination", "Self-Nomination"],
                                            p=[0.86, 0.14]),
        })
    return pd.DataFrame(rows)


def build_survey(df):
    """INSTRUMENT-CHANGE TRAP: scale moved from 1-5 to 1-7 for the 2025 wave."""
    waves = [
        ("2023-04-15", 5), ("2023-10-15", 5),
        ("2024-04-15", 5), ("2024-10-15", 5),
        ("2025-04-15", 7), ("2025-10-15", 7),
        ("2026-04-15", 7),
    ]
    items = ["ENG01", "ENG02", "ENG03", "MGR01", "MGR02", "GRW01"]
    rows = []
    for wave_date, scale in waves:
        wd = pd.Timestamp(wave_date)
        pool = df[pd.to_datetime(df["hire_date"]) < wd].copy()
        pool = pool[pool["separation_date"].isna() |
                    (pd.to_datetime(pool["separation_date"]) > wd)]
        resp_rate = rng.uniform(0.55, 0.79)
        take = pool.sample(frac=min(resp_rate, 1.0), random_state=int(wd.timestamp()) % 10000)
        for _, r in take.iterrows():
            mu = 0.55 + 0.16 * r["_latent_commitment"]
            for it in items:
                raw = np.clip(rng.normal(mu, 0.19), 0.02, 0.98)
                score = int(round(1 + raw * (scale - 1)))
                rows.append({
                    "response_id": f"RS{len(rows) + 1:08d}",
                    "wave_date": wd,
                    "worker_id": r["worker_id"],
                    "item_code": it,
                    "response_value": score,
                    "scale_max": scale,   # present, but easy to ignore
                })
    return pd.DataFrame(rows)


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = duckdb.connect(DB_PATH)

    df = build_workers()
    df = apply_separations(df)
    df = add_rehires(df)

    job_records = build_job_records(df)
    snapshot = build_snapshot(df)
    program = build_program(df)
    survey = build_survey(df)

    legacy_map = {o[0]: o[3] for o in ORG_UNITS}

    # ---- core dimension / fact tables -------------------------------------
    dim_worker = df[[
        "worker_id", "employee_number", "worker_type", "home_org_unit",
        "location_id", "job_profile_id", "hire_date", "employment_status",
    ]].copy()
    dim_worker["department"] = dim_worker["home_org_unit"].map(legacy_map)
    dim_worker.loc[rng.random(len(dim_worker)) > 0.55, "department"] = None
    dim_worker = dim_worker.rename(columns={"home_org_unit": "org_unit_v2"})

    fct_separation = df[df["is_separated"]][[
        "worker_id", "employee_number", "separation_date", "separation_type",
        "is_regrettable", "home_org_unit", "worker_type",
    ]].rename(columns={"home_org_unit": "org_unit_v2"}).copy()
    fct_separation["separation_id"] = [f"SP{i:06d}" for i in range(1, len(fct_separation) + 1)]

    fct_performance_rating = pd.DataFrame({
        "rating_id": [f"PR{i:07d}" for i in range(1, len(df) + 1)],
        "worker_id": df["worker_id"],
        "review_period": "FY2025",
        "performance_tier": df["_perf_tier"],
        "rating_label": pd.Series(df["_perf_tier"]).map(
            {1: "Below", 2: "Meets", 3: "Exceeds", 4: "Outstanding"}).to_numpy(),
    })

    # IMMORTAL-TIME TRAP: award requires surviving to the 3-year mark.
    tenure_days = (AS_OF - pd.to_datetime(df["hire_date"])).dt.days
    eligible = (tenure_days >= 1095) & (~df["is_separated"] | (
        pd.to_datetime(df["separation_date"]) - pd.to_datetime(df["hire_date"])
    ).dt.days.fillna(0).ge(1095))
    fct_tenure_award = pd.DataFrame({
        "award_id": [f"AW{i:06d}" for i in range(1, int(eligible.sum()) + 1)],
        "worker_id": df.loc[eligible, "worker_id"].to_numpy(),
        "award_type": "3-Year Service Award",
        "award_date": (pd.to_datetime(df.loc[eligible, "hire_date"]) +
                       pd.Timedelta(days=1095)).to_numpy(),
    })

    fct_compensation = pd.DataFrame({
        "comp_id": [f"CMP{i:07d}" for i in range(1, len(df) + 1)],
        "worker_id": df["worker_id"],
        "effective_date": pd.to_datetime(df["hire_date"]) + pd.Timedelta(days=90),
        "base_salary_local": np.round(
            rng.normal(112000, 34000, len(df)).clip(48000, 340000), -2),
        "currency_code": np.where(
            df["location_id"] == "LOC005", "EUR",
            np.where(df["location_id"] == "LOC006", "SGD", "USD")),
        "target_bonus_pct": np.round(rng.uniform(0.05, 0.25, len(df)), 3),
        "pay_grade": rng.choice(["G4", "G5", "G6", "G7", "G8"], len(df)),
    })

    # ---- DECOY / TRAP reporting tables ------------------------------------
    latest = snapshot[snapshot["snapshot_date"] == snapshot["snapshot_date"].max()]

    # Decoy 1: includes contingent workers -> inflates headcount
    vw_active_workers = latest[latest["employment_status"].isin(["Active", "On Leave"])][
        ["worker_id", "employee_number", "worker_type", "org_unit_v2",
         "location_id", "employment_status"]].copy()

    # Decoy 2: stale rollup, stopped refreshing in Feb 2026
    stale_cut = pd.Timestamp("2026-02-28")
    rpt_headcount_daily = (
        snapshot[snapshot["snapshot_date"] <= stale_cut]
        .groupby(["snapshot_date", "org_unit_v2"], as_index=False)
        .agg(headcount=("worker_id", "count"))
        .rename(columns={"snapshot_date": "as_of_date"})
    )

    # Decoy 3: attrition rollup using ENDING headcount as denominator
    sep_m = fct_separation.copy()
    sep_m["month"] = pd.to_datetime(sep_m["separation_date"]).dt.to_period("M").dt.to_timestamp("M")
    rpt_attrition_monthly = (
        sep_m.groupby(["month", "org_unit_v2"], as_index=False)
        .agg(separations=("separation_id", "count"))
    )

    # Decoy 4: pre-migration staging copy, frozen
    dim_worker_legacy = dim_worker.sample(frac=0.83, random_state=SEED).copy()
    dim_worker_legacy["source_system"] = "PeopleSoft (retired 2024-03)"

    con.register("_dim_worker", dim_worker)
    con.register("_dim_worker_snapshot", snapshot)
    con.register("_fct_job_record", job_records)
    con.register("_fct_separation", fct_separation)
    con.register("_fct_performance_rating", fct_performance_rating)
    con.register("_fct_program_enrollment", program)
    con.register("_fct_engagement_survey", survey)
    con.register("_fct_compensation", fct_compensation)
    con.register("_fct_tenure_award", fct_tenure_award)
    con.register("_vw_active_workers", vw_active_workers)
    con.register("_rpt_headcount_daily", rpt_headcount_daily)
    con.register("_rpt_attrition_monthly", rpt_attrition_monthly)
    con.register("_dim_worker_legacy", dim_worker_legacy)
    con.register("_dim_location", pd.DataFrame(
        LOCATIONS, columns=["location_id", "city", "state_province", "country_code", "region"]))
    con.register("_dim_org_unit", pd.DataFrame(
        ORG_UNITS, columns=["org_unit_v2", "org_unit_name", "org_group", "department"]))
    con.register("_dim_job_profile", pd.DataFrame(
        JOB_PROFILES, columns=["job_profile_id", "job_title", "job_category", "job_level"]))

    real = {
        "dim_worker": "_dim_worker",
        "dim_worker_snapshot": "_dim_worker_snapshot",
        "fct_job_record": "_fct_job_record",
        "fct_separation": "_fct_separation",
        "fct_performance_rating": "_fct_performance_rating",
        "fct_program_enrollment": "_fct_program_enrollment",
        "fct_engagement_survey": "_fct_engagement_survey",
        "fct_compensation": "_fct_compensation",
        "fct_tenure_award": "_fct_tenure_award",
        "vw_active_workers": "_vw_active_workers",
        "rpt_headcount_daily": "_rpt_headcount_daily",
        "rpt_attrition_monthly": "_rpt_attrition_monthly",
        "dim_worker_legacy": "_dim_worker_legacy",
        "dim_location": "_dim_location",
        "dim_org_unit": "_dim_org_unit",
        "dim_job_profile": "_dim_job_profile",
    }
    for name, view in real.items():
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM {view}")

    # ---- 28 plausible decoy tables: retrieval failure by volume ------------
    decoys = {
        "dim_position": "position_id VARCHAR, job_profile_id VARCHAR, org_unit_v2 VARCHAR, is_filled BOOLEAN, opened_date DATE",
        "dim_cost_center": "cost_center_id VARCHAR, cost_center_name VARCHAR, org_unit_v2 VARCHAR",
        "dim_manager": "manager_worker_id VARCHAR, span_of_control INTEGER, org_unit_v2 VARCHAR",
        "dim_employment_status": "status_code VARCHAR, status_label VARCHAR, counts_in_headcount BOOLEAN",
        "dim_worker_type": "type_code VARCHAR, type_label VARCHAR, is_employee BOOLEAN",
        "dim_pay_component": "component_id VARCHAR, component_name VARCHAR, is_recurring BOOLEAN",
        "dim_benefit_plan": "plan_id VARCHAR, plan_name VARCHAR, plan_year INTEGER",
        "dim_absence_type": "absence_type_id VARCHAR, absence_label VARCHAR, is_paid BOOLEAN",
        "dim_learning_course": "course_id VARCHAR, course_name VARCHAR, delivery_mode VARCHAR",
        "dim_recruiting_source": "source_id VARCHAR, source_name VARCHAR, source_channel VARCHAR",
        "dim_exit_reason": "reason_code VARCHAR, reason_label VARCHAR, is_voluntary BOOLEAN",
        "dim_talent_pool": "pool_id VARCHAR, pool_name VARCHAR, pool_owner VARCHAR",
        "dim_survey_item": "item_code VARCHAR, item_text VARCHAR, construct VARCHAR, scale_max INTEGER",
        "fct_recruiting_requisition": "req_id VARCHAR, org_unit_v2 VARCHAR, opened_date DATE, closed_date DATE, status VARCHAR",
        "fct_recruiting_application": "application_id VARCHAR, req_id VARCHAR, source_id VARCHAR, applied_date DATE, stage VARCHAR",
        "fct_interview_feedback": "feedback_id VARCHAR, application_id VARCHAR, interviewer_worker_id VARCHAR, recommendation VARCHAR",
        "fct_offer": "offer_id VARCHAR, application_id VARCHAR, offer_date DATE, accepted BOOLEAN",
        "fct_internal_mobility": "mobility_id VARCHAR, worker_id VARCHAR, from_org_unit VARCHAR, to_org_unit VARCHAR, move_date DATE",
        "fct_learning_completion": "completion_id VARCHAR, worker_id VARCHAR, course_id VARCHAR, completed_date DATE",
        "fct_payroll_run": "run_id VARCHAR, pay_period_end DATE, gross_amount DECIMAL(12,2), currency_code VARCHAR",
        "fct_benefits_enrollment": "enrollment_id VARCHAR, worker_id VARCHAR, plan_id VARCHAR, plan_year INTEGER",
        "fct_absence_event": "absence_id VARCHAR, worker_id VARCHAR, absence_type_id VARCHAR, start_date DATE, end_date DATE",
        "fct_timeoff_balance": "balance_id VARCHAR, worker_id VARCHAR, as_of_date DATE, hours_accrued DECIMAL(8,2)",
        "fct_headcount_budget": "budget_id VARCHAR, org_unit_v2 VARCHAR, fiscal_year INTEGER, budgeted_headcount INTEGER",
        "fct_exit_survey": "exit_response_id VARCHAR, worker_id VARCHAR, reason_code VARCHAR, would_recommend BOOLEAN",
        "fct_succession_plan": "plan_id VARCHAR, position_id VARCHAR, successor_worker_id VARCHAR, readiness VARCHAR",
        "stg_workday_worker_raw": "raw_id VARCHAR, payload VARCHAR, ingested_at TIMESTAMP",
        "stg_workday_job_raw": "raw_id VARCHAR, payload VARCHAR, ingested_at TIMESTAMP",
    }
    for name, cols in decoys.items():
        con.execute(f"CREATE TABLE {name} ({cols})")

    n_tables = len(real) + len(decoys)

    print(f"Built {DB_PATH}")
    print(f"  tables:            {n_tables}")
    print(f"  dim_worker:        {len(dim_worker):,}")
    print(f"  fct_job_record:    {len(job_records):,}")
    print(f"  snapshot rows:     {len(snapshot):,}")
    print(f"  separations:       {len(fct_separation):,}")
    print(f"  program enrolled:  {len(program):,}")
    print(f"  survey responses:  {len(survey):,}")
    con.close()


if __name__ == "__main__":
    main()
