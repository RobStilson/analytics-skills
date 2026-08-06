#!/usr/bin/env python3
"""
Run YOUR OWN ablation: your eval, your reference doc, baseline vs. skill.

This is not the pack's full ablation (evals/run_evals.py) -- that runs 29
evals x 6 slices for the people maintaining the pack. This runs the ONE eval
you wrote in Validate, against the ONE reference doc you wrote in Build, on
your own machine, with your own API key. It's built to finish in well under a
minute so a whole room can run it at the same time without anyone waiting.

It reuses evals/run_evals.py's agent loop and grader rather than
reimplementing them -- that loop was debugged through several real failures
during development (turn-budget exhaustion, credit errors, empty responses),
and a participant-facing script is the wrong place to reintroduce those bugs.

Usage (from the repo root or from workshop/):
    python run_my_ablation.py

Looks for:
    evals/my-eval.json          the eval you wrote in Validate
    references/<domain>.md      the reference doc you wrote in Build
                                 (auto-detected; pass --reference to override)

Does NOT touch evals/results/ -- that directory holds the pack's own official
ablation and is used by the deck and the failure-demo script. This writes
nowhere by default; pass --save to write a timestamped file in workshop/.
"""

import argparse
import glob
import json
import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # workshop/ -> repo root

# Reuse the pack's own agent loop, grader, retry logic, and error handling
# rather than reimplementing them here.
sys.path.insert(0, os.path.join(ROOT, "evals"))
try:
    import run_evals as core
except ImportError as e:
    sys.exit(
        f"\nCouldn't import evals/run_evals.py: {e}\n"
        f"Run this script from the repo root or from workshop/, and make sure\n"
        f"evals/run_evals.py exists there.\n")

EVAL_DEFAULT = os.path.join(ROOT, "evals", "my-eval.json")
# The only legitimate participant-produced domain docs, per define-worksheet.md
# and build-worksheet.md. An ALLOWLIST, not a blocklist: a blocklist breaks
# every time a new file lands in references/ (this one already did, on the
# first test run -- analysis-patterns.md was silently picked up as a
# candidate). A new pack-infrastructure file can never be mistaken for a
# participant's doc under an allowlist; it simply isn't on it.
KNOWN_DOMAINS = {"attrition.md", "compensation.md", "engagement.md"}


def find_eval(path):
    if not os.path.exists(path):
        sys.exit(
            f"\nNo eval found at {path}\n\n"
            f"That's the file you wrote in Validate. Save your JSON there --\n"
            f"see validate-worksheet.md step 3 -- then run this again.\n")
    try:
        data = json.load(open(path))
    except json.JSONDecodeError as e:
        sys.exit(
            f"\n{path} isn't valid JSON: {e}\n\n"
            f"Common fixes: a trailing comma after the last item in a list,\n"
            f"or a missing closing brace. Check it against the example in\n"
            f"validate-worksheet.md step 3.\n")
    evals = data.get("evals")
    if not evals:
        sys.exit(f"\n{path} has no \"evals\" list. Check it matches the schema "
                 f"in validate-worksheet.md.\n")
    ev = evals[0]
    for field in ("prompt", "assertions"):
        if not ev.get(field):
            sys.exit(f"\nYour eval is missing \"{field}\". Check it against "
                     f"the schema in validate-worksheet.md.\n")
    return ev


def find_reference(explicit):
    if explicit:
        if not os.path.exists(explicit):
            sys.exit(f"\n{explicit} doesn't exist.\n")
        return explicit
    candidates = [
        p for p in glob.glob(os.path.join(ROOT, "references", "*.md"))
        if os.path.basename(p) in KNOWN_DOMAINS
    ]
    if not candidates:
        print("\nNo reference doc found in references/ yet.")
        print("That's the file you wrote in Build -- saved as one of:")
        print(f"  {', '.join(sorted(KNOWN_DOMAINS))}")
        print("Running baseline-only, which still shows you what the agent")
        print("does with no help at all. Run again once your doc is saved.\n")
        return None
    if len(candidates) > 1:
        candidates.sort(key=os.path.getmtime, reverse=True)
        print(f"Found {len(candidates)} reference docs; using the most "
              f"recently saved: {os.path.basename(candidates[0])}")
        print(f"  (pass --reference <path> to pick a different one)\n")
    return candidates[0]


def run_one(client, ev, system, repeats):
    """One or more repeats of one condition. Returns (avg_pass, total, last_response, runs)."""
    runs = []
    last_resp, last_graded = "", []
    for _ in range(repeats):
        resp = core.call_agent(client, ev["prompt"], system)
        if not resp.strip():
            print("  (a run came back empty after exhausting the query budget "
                  "-- skipping it)")
            continue
        graded = core.grade(client, ev, resp)
        runs.append(sum(1 for g in graded if g["verdict"] == "PASS"))
        last_resp, last_graded = resp, graded
    if not runs:
        return None, len(ev["assertions"]), "", []
    return sum(runs) / len(runs), len(ev["assertions"]), last_resp, last_graded


def print_result(label, avg, total, resp, graded):
    print(f"\n{'-'*60}")
    print(f"{label}   {avg:.1f}/{total}")
    print(f"{'-'*60}")
    for g in graded:
        mark = "PASS" if g["verdict"] == "PASS" else "FAIL"
        print(f"  [{mark}] {g['reason']}")
    print(f"\n  Full response:")
    for line in resp.splitlines():
        print(f"    {line}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", default=EVAL_DEFAULT, help="path to your eval JSON")
    ap.add_argument("--reference", default=None, help="path to your reference doc")
    ap.add_argument("--repeats", type=int, default=1,
                    help="repeat each condition N times (default: 1 -- one is "
                         "plenty for a 20-minute room exercise)")
    ap.add_argument("--save", action="store_true",
                    help="write a timestamped result file in workshop/")
    args = ap.parse_args()

    # Validate local files first -- instant, free, and the most common thing
    # to be wrong. No reason to make someone set up an API key before finding
    # out their JSON has a trailing comma.
    ev = find_eval(args.eval)
    ref_path = find_reference(args.reference)
    ref_text = open(ref_path).read() if ref_path else ""

    try:
        import duckdb  # noqa: F401 -- needed by the SQL tool
        from anthropic import Anthropic
    except ImportError as e:
        sys.exit(f"\nMissing dependency: {e.name or e}\n"
                 f"  pip install -r requirements.txt\n")

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("\nANTHROPIC_API_KEY not set. Run check_setup.py first.\n")

    client = Anthropic()

    # Preflight -- one tiny call, so a credit or key problem is caught in two
    # seconds instead of after you've explained your results to a neighbour.
    try:
        client.messages.create(model=core.AGENT_MODEL, max_tokens=4,
                               messages=[{"role": "user", "content": "ok"}])
    except Exception as e:
        msg = str(e)
        print(f"\nPreflight call failed -- not running your ablation.\n\n  {msg[:400]}\n")
        if any(m.lower() in msg.lower() for m in core.FATAL_MARKERS):
            print("This is an account-level problem (key or credit), not a "
                  "bug in your work. Flag the facilitator.")
        sys.exit(1)

    print(f"\nYour question:  {ev['prompt']}")
    print(f"Assertions:     {len(ev['assertions'])}")
    if ref_path:
        print(f"Reference doc:  {os.path.relpath(ref_path, ROOT)}")

    base_system = core.SCHEMA_PREAMBLE.format(db=core.DB)

    print("\nRunning baseline (no reference doc)...")
    try:
        b_avg, b_tot, b_resp, b_graded = run_one(
            client, ev, base_system, args.repeats)
    except core.FatalAPIError as e:
        sys.exit(f"\nStopped -- account-level API error: {str(e)[:300]}\n")

    if ref_path:
        print("Running with your reference doc loaded...")
        try:
            s_avg, s_tot, s_resp, s_graded = run_one(
                client, ev, base_system + "\n\n" + ref_text, args.repeats)
        except core.FatalAPIError as e:
            sys.exit(f"\nStopped -- account-level API error: {str(e)[:300]}\n")
    else:
        s_avg = s_tot = s_resp = s_graded = None

    print_result("BASELINE", b_avg, b_tot, b_resp, b_graded)
    if s_avg is not None:
        print_result("WITH YOUR REFERENCE DOC", s_avg, s_tot, s_resp, s_graded)
        delta = (s_avg - b_avg) / b_tot * 100 if b_tot else 0
        print(f"\n{'='*60}")
        print(f"  {b_avg:.1f}/{b_tot} -> {s_avg:.1f}/{s_tot}   ({delta:+.0f} pts)")
        print(f"{'='*60}")

    print("\nCompare this against your Validate worksheet prediction.")
    print("Were you right about which assertions would fail? A miss there is")
    print("just as informative as a hit -- it's a gap you didn't know you had.")

    if args.save:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out = os.path.join(HERE, f"my-ablation-{stamp}.json")
        json.dump({
            "prompt": ev["prompt"], "reference_doc": ref_path,
            "baseline": {"avg": b_avg, "total": b_tot, "response": b_resp},
            "with_doc": ({"avg": s_avg, "total": s_tot, "response": s_resp}
                        if s_avg is not None else None),
        }, open(out, "w"), indent=2)
        print(f"\nSaved -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
