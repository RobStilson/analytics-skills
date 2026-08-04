#!/usr/bin/env python3
"""
Verify the eval set has not drifted from the warehouse.

Regenerates ground truth from the current database and diffs it against the
committed ground_truth.json. Any difference means the warehouse changed and the
eval set is now asserting figures the data no longer produces.

Runs offline. No API key, no model calls, no cost. Wire it into CI.

Exit codes:
    0  ground truth matches, every eval reference resolves
    1  drift detected, or an eval quotes a figure not in ground truth

Usage:
    python verify.py
"""

import io
import json
import os
import re
import sys
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SKILLS = [
    "warehouse-navigation", "question-intake", "uncertainty-reporting",
    "causal-claim-guardrail", "adversarial-sql-review", "provenance-footer",
]


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def main():
    gt_path = os.path.join(HERE, "ground_truth.json")
    if not os.path.exists(gt_path):
        print("FAIL  ground_truth.json missing — run make_ground_truth.py")
        return 1

    db = os.path.join(HERE, "..", "warehouse", "people_analytics.duckdb")
    if not os.path.exists(db):
        print("FAIL  warehouse not found at warehouse/people_analytics.duckdb")
        print("      Rebuild it:  cd ../warehouse && python build_warehouse.py")
        return 1
    if os.path.getsize(db) < 1_000_000:
        print(f"FAIL  warehouse file is only {os.path.getsize(db):,} bytes —")
        print("      expected ~6.8 MB. It likely did not survive transfer.")
        print("      Rebuild it:  cd ../warehouse && python build_warehouse.py")
        return 1

    committed = json.load(open(gt_path))

    # Regenerate from the live warehouse into a temp file, then compare.
    try:
        import make_ground_truth
    except ImportError as e:
        print(f"FAIL  cannot import make_ground_truth: {e}")
        print("      Install dependencies:  pip install duckdb")
        return 1
    tmp = gt_path + ".verify"
    orig_out = make_ground_truth.OUT
    make_ground_truth.OUT = tmp
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            make_ground_truth.main()
        fresh = json.load(open(tmp))
    finally:
        make_ground_truth.OUT = orig_out
        if os.path.exists(tmp):
            os.remove(tmp)

    fc, ff = flatten(committed), flatten(fresh)
    drift = []
    for k in sorted(set(fc) | set(ff)):
        if k.startswith("_meta"):
            continue
        a, b = fc.get(k, "<missing>"), ff.get(k, "<missing>")
        if a != b:
            drift.append((k, a, b))

    print("=" * 62)
    print("GROUND TRUTH")
    print("=" * 62)
    if drift:
        print(f"  DRIFT DETECTED — {len(drift)} value(s) changed\n")
        for k, a, b in drift[:25]:
            print(f"    {k}\n      committed: {a}\n      current:   {b}")
        print("\n  The warehouse no longer produces the figures the evals assert.")
        print("  Rebuild the warehouse from the pinned seed, or regenerate the")
        print("  eval set and re-review every assertion that changed.")
    else:
        print(f"  OK — {len(fc)} pinned values all match the current warehouse")

    # Every numeric figure quoted in an eval must exist in ground truth.
    print()
    print("=" * 62)
    print("EVAL SLICES")
    print("=" * 62)
    known = set()
    for v in fc.values():
        if isinstance(v, (int, float)):
            known.add(round(float(v), 1))
            known.add(float(int(v)) if float(v).is_integer() else float(v))

    total = neg = orphan = 0
    for skill in SKILLS:
        p = os.path.join(HERE, skill, "evals.json")
        if not os.path.exists(p):
            print(f"  MISSING  {skill}/evals.json")
            orphan += 1
            continue
        data = json.load(open(p))
        evals = data["evals"]
        total += len(evals)
        n = sum(1 for e in evals if e.get("negative"))
        neg += n

        ids = [e["id"] for e in evals]
        dupes = {i for i in ids if ids.count(i) > 1}
        problems = []
        if dupes:
            problems.append(f"duplicate ids {sorted(dupes)}")
        for e in evals:
            if not e.get("assertions"):
                problems.append(f"{e['id']} has no assertions")
            # Figures quoted in assertions should trace to ground truth.
            for a in e["assertions"]:
                for m in re.findall(r"\b(\d{1,3}(?:,\d{3})+|\d+\.\d)\b", a):
                    val = float(m.replace(",", ""))
                    if val not in known:
                        problems.append(f"{e['id']} quotes {m}, not in ground truth")

        status = "OK " if not problems else "FAIL"
        print(f"  {status} {skill:<26} {len(evals):>2} evals, {n} negative")
        for pr in problems[:4]:
            print(f"         - {pr}")
        if problems:
            orphan += len(problems)

    print()
    print("=" * 62)
    print(f"  {total} evals, {neg} negative ({100*neg//total if total else 0}%)")
    if neg == 0:
        print("  WARNING: no negative tests. A skill that fires on everything")
        print("  is indistinguishable from a skill that works.")
    print("=" * 62)

    return 1 if (drift or orphan) else 0


if __name__ == "__main__":
    sys.exit(main())
