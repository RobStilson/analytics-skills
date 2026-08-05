#!/usr/bin/env python3
"""
Run the eval set against an agent, with and without skills loaded.

This is the ablation: same questions, same warehouse, skills off then on.
The delta is the measurement.

!! UNTESTED !!
   This script has never been executed against a live API. It was written
   without credentials available. Expect to debug it on first run — treat the
   structure as the contribution and the specifics as a starting point.

Requires:
    pip install anthropic duckdb
    export ANTHROPIC_API_KEY=...

Usage:
    python run_evals.py --mode baseline          # no skills
    python run_evals.py --mode skills            # skills loaded
    python run_evals.py --skill causal-claim-guardrail
    python run_evals.py --compare results/baseline.json results/skills.json

Results land in results/ as JSON telemetry — skill version, model id,
per-assertion pass/fail — so "did that change help?" is a query, not a memory.
"""

import argparse
import json
import os
import re
import sys
import time
import datetime
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "warehouse", "people_analytics.duckdb")
RESULTS = os.path.join(HERE, "results")

SKILLS = [
    "warehouse-navigation", "question-intake", "uncertainty-reporting",
    "causal-claim-guardrail", "adversarial-sql-review", "provenance-footer",
]

# Defaults. Override with --agent-model / --grader-model.
#
# Sonnet 5 is the current Sonnet and is markedly stronger at agentic work, which
# makes it the fairer test: it is the model people would actually use. Note the
# tradeoff — a stronger agent may pass more BASELINE evals unaided, compressing
# the measured delta. That is a real result, not a problem with the measurement.
#
# Sonnet 5 rejects non-default sampling parameters (temperature, top_p) and does
# not accept manual thinking budgets. This script sets none of those.
AGENT_MODEL = "claude-sonnet-5"
GRADER_MODEL = "claude-sonnet-5"

SCHEMA_PREAMBLE = """You have read-only access to a DuckDB warehouse of people
analytics data at {db}. Answer the user's question using it. You may run SQL.
The as-of date for the warehouse is 2026-06-30."""

GRADER_PROMPT = """You are grading an AI assistant's response against assertions.

QUESTION ASKED:
{prompt}

WHAT A CORRECT RESPONSE DOES:
{expected}

THE RESPONSE TO GRADE:
{response}

ASSERTIONS — judge each independently as PASS or FAIL:
{assertions}

Grade strictly. An assertion passes only if the response clearly satisfies it.
Partial credit is not available. If the response is ambiguous, that is a FAIL.

Return ONLY a JSON object, no preamble and no markdown fences:
{{"results": [{{"assertion": 1, "verdict": "PASS", "reason": "..."}}, ...]}}"""


def load_skill_text(names):
    """Concatenate SKILL.md bodies to inject as system context."""
    parts = []
    for n in names:
        p = os.path.join(ROOT, "skills", n, "SKILL.md")
        if os.path.exists(p):
            parts.append(open(p).read())
    return "\n\n---\n\n".join(parts)


def run_sql(query):
    """Execute SQL against the warehouse read-only. Used as the agent's tool."""
    import duckdb
    con = duckdb.connect(DB, read_only=True)
    try:
        cur = con.execute(query)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchmany(200)
        return json.dumps({"columns": cols, "rows": [list(map(str, r)) for r in rows]})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        con.close()


class FatalAPIError(Exception):
    """An account-level problem. Every subsequent request will fail the same
    way, so abort the whole run instead of burning through the batch."""


FATAL_MARKERS = (
    "credit balance is too low",
    "authentication_error",
    "invalid x-api-key",
    "permission_error",
    "Your account has been disabled",
)


def _with_retry(fn, tries=3):
    """Retry transient API failures. Account problems abort; 400s fail fast."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            msg = str(e)
            if any(m.lower() in msg.lower() for m in FATAL_MARKERS):
                raise FatalAPIError(msg)
            transient = any(k in msg for k in
                            ("429", "overloaded", "529", "timeout", "Connection"))
            if not transient or i == tries - 1:
                raise
            time.sleep(2 ** i * 2)


def call_agent(client, prompt, system, max_turns=10):
    """Agentic loop with a single SQL tool."""
    tools = [{
        "name": "run_sql",
        "description": "Execute a read-only SQL query against the DuckDB warehouse.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    }]
    messages = [{"role": "user", "content": prompt}]
    exhausted = True
    for _ in range(max_turns):
        resp = _with_retry(lambda: client.messages.create(
            model=AGENT_MODEL, max_tokens=3000,
            system=system, tools=tools, messages=messages))
        messages.append({"role": "assistant", "content": resp.content})
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            exhausted = False
            break
        results = []
        for tu in tool_uses:
            results.append({
                "type": "tool_result", "tool_use_id": tu.id,
                "content": run_sql(tu.input.get("query", "")),
            })
        messages.append({"role": "user", "content": results})

    text = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text")

    # Turn budget ran out mid-tool-use: the last message is all tool_use blocks
    # and carries no answer. Give one final chance to answer with what it has,
    # WITHOUT tools, rather than returning an empty string that the grader would
    # score as a legitimate zero.
    if exhausted and not text.strip():
        # The loop ends on a user turn carrying tool_result blocks, so a new
        # user message would put two user turns in a row (400). Append the nudge
        # to that existing turn instead. And keep `tools` in the request: the
        # history contains tool_use blocks, and omitting tools is also a 400.
        nudge = ("You have run out of query budget. Answer now, using what you "
                 "have already learned. Do not request more queries.")
        if messages and messages[-1]["role"] == "user" and \
           isinstance(messages[-1]["content"], list):
            messages[-1]["content"] = list(messages[-1]["content"]) + [
                {"type": "text", "text": nudge}]
        else:
            messages.append({"role": "user", "content": nudge})
        final = client.messages.create(
            model=AGENT_MODEL, max_tokens=3000, system=system,
            tools=tools, messages=messages)
        text = "\n".join(b.text for b in final.content
                         if getattr(b, "type", None) == "text")

    return text


def grade(client, ev, response):
    numbered = "\n".join(f"{i+1}. {a}" for i, a in enumerate(ev["assertions"]))
    msg = client.messages.create(
        model=GRADER_MODEL, max_tokens=2000,
        messages=[{"role": "user", "content": GRADER_PROMPT.format(
            prompt=ev["prompt"], expected=ev.get("expected_output", ""),
            response=response, assertions=numbered)}])
    raw = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    try:
        return json.loads(raw)["results"]
    except Exception as e:
        return [{"assertion": i + 1, "verdict": "ERROR", "reason": str(e)}
                for i in range(len(ev["assertions"]))]


def git_sha():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def main():
    global AGENT_MODEL, GRADER_MODEL
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baseline", "skills"], default="skills")
    ap.add_argument("--skill", help="run one slice only")
    ap.add_argument("--compare", nargs=2, metavar=("BASELINE", "SKILLS"))
    ap.add_argument("--agent-model", default=AGENT_MODEL,
                    help=f"model under test (default: {AGENT_MODEL})")
    ap.add_argument("--grader-model", default=GRADER_MODEL,
                    help=f"model doing the grading (default: {GRADER_MODEL})")
    ap.add_argument("--load-all", action="store_true",
                    help="inject ALL skills for every eval instead of just the "
                         "one under test. Measures context dilution, not skill "
                         "quality. Kept for comparison.")
    ap.add_argument("--repeats", type=int, default=1,
                    help="run each eval N times and average (default: 1). "
                         "Single runs are noisy; 3 is a reasonable minimum for "
                         "a result you intend to quote.")
    ap.add_argument("--workers", type=int, default=6,
                    help="parallel API calls (default: 6). Each carries the "
                         "skill text as a system prompt, so high concurrency "
                         "pushes hard on rate limits. Raise cautiously.")
    ap.add_argument("--max-turns", type=int, default=10,
                    help="cap on agent SQL turns per eval (default: 10). Too "
                         "low and skills that add process steps run out of "
                         "budget before answering.")
    args = ap.parse_args()
    AGENT_MODEL, GRADER_MODEL = args.agent_model, args.grader_model

    if args.compare:
        return compare(*args.compare)

    if args.skill:
        if args.skill not in SKILLS:
            print(f"Unknown slice: {args.skill!r}\n")
            print("Available slices:")
            for s_ in SKILLS:
                print(f"  {s_}")
            import difflib
            near = difflib.get_close_matches(args.skill, SKILLS, n=1, cutoff=0.6)
            if near:
                print(f"\nDid you mean:  --skill {near[0]}")
            return 1
        slices = [args.skill]
    else:
        slices = SKILLS

    n_evals = 0
    for sk in slices:
        pth = os.path.join(HERE, sk, "evals.json")
        if os.path.exists(pth):
            n_evals += len(json.load(open(pth))["evals"])
    n_runs = n_evals * args.repeats
    # 60s/run, calibrated against an observed sequential run (~103s/run
    # measured). Agent loops with several SQL turns dominate; the grader call
    # is small by comparison.
    est_min = n_runs * 60 / max(args.workers, 1) / 60
    print(f"{n_evals} evals x {args.repeats} repeat(s) = {n_runs} runs, "
          f"{args.workers} at a time")
    print(f"rough estimate: {est_min:.0f}-{est_min*2:.0f} min")
    if est_min > 25:
        print("  ^ that is a long run. Consider --repeats 1, more --workers,")
        print("    or --skill <one-slice> for a quick check.")
    print()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set.")
        return 1
    try:
        from anthropic import Anthropic
    except ImportError:
        print("Missing dependency: anthropic")
        print("  Install it with:  pip install anthropic")
        return 1
    try:
        import duckdb  # noqa: F401 — needed by the SQL tool
    except ImportError:
        print("Missing dependency: duckdb")
        print("  Install it with:  pip install duckdb")
        return 1

    client = Anthropic()

    base_system = SCHEMA_PREAMBLE.format(db=DB)

    # Preflight with a single tiny call. Cheaper than discovering an account
    # problem 174 requests in.
    try:
        client.messages.create(model=AGENT_MODEL, max_tokens=4,
                               messages=[{"role": "user", "content": "ok"}])
    except Exception as e:
        msg = str(e)
        print("Preflight call failed — not starting the run.\n")
        print(f"  {msg[:400]}\n")
        if any(m.lower() in msg.lower() for m in FATAL_MARKERS):
            print("This is an account-level problem, not a code problem.")
        return 1
    print("preflight ok\n")

    os.makedirs(RESULTS, exist_ok=True)
    t0 = time.time()
    out = {
        "mode": args.mode, "git_sha": git_sha(), "agent_model": AGENT_MODEL,
        "grader_model": GRADER_MODEL,
        "skill_loading": ("n/a" if args.mode == "baseline"
                          else ("all" if args.load_all else "per-slice")),
        "repeats": args.repeats,
        "run_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "slices": {},
    }

    for skill in slices:
        p = os.path.join(HERE, skill, "evals.json")
        if not os.path.exists(p):
            continue
        evals = json.load(open(p))["evals"]
        rows = []

        # Load only the skill under test for this slice, unless --load-all.
        # Loading every skill for every question is not how skills are used in
        # production, and it measures context dilution rather than skill quality.
        if args.mode == "skills":
            to_load = SKILLS if args.load_all else [skill]
            system = base_system + "\n\n" + load_skill_text(to_load)
        else:
            system = base_system

        loaded = "none" if args.mode == "baseline" else (
            "all 6" if args.load_all else skill)
        print(f"\n{skill}  [{args.mode}]  skills loaded: {loaded}")
        def one_run(ev):
            resp = call_agent(client, ev["prompt"], system, args.max_turns)
            if not resp.strip():
                # Grading an empty string produces a zero that looks like a
                # measurement and is not one. Surface it instead.
                raise RuntimeError(
                    "empty response after exhausting the turn budget — "
                    "raise --max-turns")
            graded = grade(client, ev, resp)
            return ev["id"], sum(1 for g in graded if g["verdict"] == "PASS"), resp, graded

        # Every (eval, repeat) pair is independent, so fan them all out at once.
        jobs = [ev for ev in evals for _ in range(args.repeats)]
        collected = {ev["id"]: [] for ev in evals}
        last, errors = {}, {}
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(one_run, ev): ev for ev in jobs}
            done_n = 0
            for fut in as_completed(futures):
                try:
                    eid, npass, resp, graded = fut.result()
                except FatalAPIError as e:
                    print(f"\r\nABORTING — account-level API error:\n")
                    print(f"  {str(e)[:400]}\n")
                    print("Every remaining request would fail the same way, so")
                    print("the run is stopping instead of issuing hundreds more.")
                    print("Fix the account issue, then run:")
                    print("  python check_setup.py    (makes one live call)")
                    pool.shutdown(wait=False, cancel_futures=True)
                    return 1
                except Exception as e:
                    eid = futures[fut]["id"]
                    errors.setdefault(eid, []).append(str(e))
                    # Print the first full error; later ones are usually the
                    # same cause and truncating hid the diagnosis last time.
                    if len(errors) == 1 and len(errors[eid]) == 1:
                        print(f"\r    ! {eid} FAILED:\n      {str(e)[:600]}")
                    else:
                        print(f"\r    ! {eid}: {str(e)[:70]}")
                    continue
                collected[eid].append(npass)
                last[eid] = (resp, graded)
                done_n += 1
                print(f"\r    {done_n}/{len(jobs)} runs complete", end="", flush=True)
        print()

        for ev in evals:
            runs = collected[ev["id"]]
            total = len(ev["assertions"])
            if not runs:
                print(f"      {ev['id']}  NO VALID RUNS — excluded from scoring")
                for m in errors.get(ev["id"], [])[:1]:
                    print(f"           {m}")
                continue
            passed = sum(runs) / len(runs)
            resp, graded = last.get(ev["id"], ("", []))
            rows.append({
                "id": ev["id"], "negative": ev.get("negative", False),
                "trap": ev.get("trap"), "passed": passed, "total": total,
                "runs": runs, "assertions": graded, "response": resp,
            })
            mark = "OK " if passed == total else "   "
            tag = " [neg]" if ev.get("negative") else ""
            nerr = len(errors.get(ev["id"], []))
            spread = f"  runs={runs}" if args.repeats > 1 else ""
            if nerr:
                spread += f"  ({nerr} failed run{'s' if nerr > 1 else ''})"
            shown = f"{passed:.1f}" if args.repeats > 1 else f"{int(passed)}"
            print(f"  {mark} {ev['id']}  {shown}/{total}{tag}{spread}")
        out["slices"][skill] = rows

    tot = sum(r["total"] for s in out["slices"].values() for r in s)
    ps = sum(r["passed"] for s in out["slices"].values() for r in s)

    if tot == 0:
        print("\nNo assertions were evaluated — nothing was run.")
        print("Not writing a results file; an empty run is a failure, not a 0% score.")
        return 1

    path = os.path.join(RESULTS, f"{args.mode}.json")
    if os.path.exists(path):
        # A completed run is data. Keep it rather than silently replacing it.
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        prev = os.path.join(RESULTS, f"{args.mode}.{stamp}.json")
        os.replace(path, prev)
        print(f"   (previous run archived as {os.path.basename(prev)})")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"\n{ps}/{tot} assertions passed ({100*ps/tot:.0f}%) "
          f"in {(time.time()-t0)/60:.1f} min")
    print(f"-> {path}")
    return 0


def _resolve(p):
    """Accept a path relative to CWD, or a bare name under evals/results/."""
    if os.path.exists(p):
        return p
    alt = os.path.join(RESULTS, os.path.basename(p))
    if os.path.exists(alt):
        return alt
    print(f"Results file not found: {p}")
    if os.path.isdir(RESULTS):
        have = sorted(f for f in os.listdir(RESULTS) if f.endswith(".json"))
        print(f"  Looked in: {RESULTS}")
        print(f"  Found there: {', '.join(have) if have else '(none)'}")
    else:
        print(f"  No results directory yet — run a mode first.")
    sys.exit(1)


def compare(a_path, b_path):
    a_path, b_path = _resolve(a_path), _resolve(b_path)
    a, b = json.load(open(a_path)), json.load(open(b_path))
    for tag, d, pth in (("baseline", a, a_path), ("skills", b, b_path)):
        n = sum(r["total"] for s in d.get("slices", {}).values() for r in s)
        if n == 0:
            print(f"{tag} file has no evaluated assertions: {pth}")
            print("Re-run that mode before comparing.")
            return 1
    sa, sb = set(a.get("slices", {})), set(b.get("slices", {}))
    if sa != sb:
        print("WARNING: the two runs cover different slices.")
        if sb - sa:
            print(f"  only in skills run:   {', '.join(sorted(sb - sa))}")
        if sa - sb:
            print(f"  only in baseline run: {', '.join(sorted(sa - sb))}")
        print("  A slice missing from one side shows as 0% there, which will look")
        print("  like a large gain or loss that was never measured. Re-run both")
        print("  modes over the same slices before trusting the delta.\n")

    if a.get("skill_loading") != b.get("skill_loading") and \
       "n/a" not in (a.get("skill_loading"), b.get("skill_loading")):
        print(f"WARNING: different skill-loading strategies — "
              f"{a.get('skill_loading')} vs {b.get('skill_loading')}. "
              f"Not comparable.\n")
    if (a.get("repeats", 1) == 1 and b.get("repeats", 1) == 1):
        print("NOTE: single run per eval. Individual evals flip on rephrasing; "
              "treat slice-level deltas as directional.\n")

    if a.get("agent_model") != b.get("agent_model"):
        print(f"WARNING: different agent models — baseline "
              f"{a.get('agent_model')} vs skills {b.get('agent_model')}. "
              f"The delta is not attributable to skills alone.\n")
    print(f"{'slice':<28}{'baseline':>10}{'skills':>10}{'delta':>10}")
    print("-" * 58)
    ta = tb = na = nb = 0
    incomparable = []
    for skill in sorted(set(a["slices"]) | set(b["slices"])):
        ra, rb = a["slices"].get(skill, []), b["slices"].get(skill, [])
        # Only evals present on BOTH sides can be compared. An eval that failed
        # to run is missing data, not a zero.
        ids_a, ids_b = {r["id"] for r in ra}, {r["id"] for r in rb}
        both = ids_a & ids_b
        missing = (ids_a | ids_b) - both
        ra_c = [r for r in ra if r["id"] in both]
        rb_c = [r for r in rb if r["id"] in both]
        pa, sa = sum(r["passed"] for r in ra_c), sum(r["total"] for r in ra_c)
        pb, sb = sum(r["passed"] for r in rb_c), sum(r["total"] for r in rb_c)
        if not sa or not sb:
            print(f"{skill:<28}{'--':>10}{'--':>10}{'no data':>10}")
            incomparable.append((skill, sorted(missing)))
            continue
        fa, fb = 100 * pa / sa, 100 * pb / sb
        flag = f"  ({len(missing)} eval(s) excluded)" if missing else ""
        print(f"{skill:<28}{fa:>9.0f}%{fb:>9.0f}%{fb-fa:>+9.0f}{flag}")
        if missing:
            incomparable.append((skill, sorted(missing)))
        ta += pa; na += sa; tb += pb; nb += sb
    print("-" * 58)
    if na and nb:
        fa, fb = 100 * ta / na, 100 * tb / nb
        print(f"{'TOTAL':<28}{fa:>9.0f}%{fb:>9.0f}%{fb-fa:>+9.0f}")
        print(f"{'':28}{'':>10}{'':>10}  over {na:.0f} matched assertions")
    else:
        print(f"{'TOTAL':<28}{'--':>10}{'--':>10}{'no data':>10}")

    if incomparable:
        print("\nINCOMPLETE — evals that did not run on both sides were excluded:")
        for skill, miss in incomparable:
            print(f"  {skill}: {', '.join(miss) if miss else 'entire slice'}")
        print("\nThese are missing measurements, not zeros. Re-run the failed")
        print("evals before quoting any number above.")
    print("\nNegative tests (skills should NOT over-fire):")
    for tag, d in (("baseline", a), ("skills", b)):
        rs = [r for s in d["slices"].values() for r in s if r["negative"]]
        p = sum(r["passed"] for r in rs); t = sum(r["total"] for r in rs)
        print(f"  {tag:<10} {p}/{t} ({100*p//t if t else 0}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
