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
import datetime
import subprocess

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


def call_agent(client, prompt, system, max_turns=8):
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
    for _ in range(max_turns):
        resp = client.messages.create(
            model=AGENT_MODEL, max_tokens=3000,
            system=system, tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            break
        results = []
        for tu in tool_uses:
            results.append({
                "type": "tool_result", "tool_use_id": tu.id,
                "content": run_sql(tu.input.get("query", "")),
            })
        messages.append({"role": "user", "content": results})
    return "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text")


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
    args = ap.parse_args()
    AGENT_MODEL, GRADER_MODEL = args.agent_model, args.grader_model

    if args.compare:
        return compare(*args.compare)

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
    slices = [args.skill] if args.skill else SKILLS
    system = SCHEMA_PREAMBLE.format(db=DB)
    if args.mode == "skills":
        system += "\n\n" + load_skill_text(slices)

    os.makedirs(RESULTS, exist_ok=True)
    print(f"agent: {AGENT_MODEL}  |  grader: {GRADER_MODEL}  |  mode: {args.mode}")
    out = {
        "mode": args.mode, "git_sha": git_sha(), "agent_model": AGENT_MODEL,
        "grader_model": GRADER_MODEL,
        "run_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "slices": {},
    }

    for skill in slices:
        p = os.path.join(HERE, skill, "evals.json")
        if not os.path.exists(p):
            continue
        evals = json.load(open(p))["evals"]
        rows = []
        print(f"\n{skill}  [{args.mode}]")
        for ev in evals:
            resp = call_agent(client, ev["prompt"], system)
            graded = grade(client, ev, resp)
            passed = sum(1 for g in graded if g["verdict"] == "PASS")
            rows.append({
                "id": ev["id"], "negative": ev.get("negative", False),
                "trap": ev.get("trap"), "passed": passed,
                "total": len(ev["assertions"]),
                "assertions": graded, "response": resp,
            })
            mark = "OK " if passed == len(ev["assertions"]) else "   "
            tag = " [neg]" if ev.get("negative") else ""
            print(f"  {mark} {ev['id']}  {passed}/{len(ev['assertions'])}{tag}")
        out["slices"][skill] = rows

    path = os.path.join(RESULTS, f"{args.mode}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

    tot = sum(r["total"] for s in out["slices"].values() for r in s)
    ps = sum(r["passed"] for s in out["slices"].values() for r in s)
    print(f"\n{ps}/{tot} assertions passed ({100*ps//tot if tot else 0}%)")
    print(f"-> {path}")
    return 0


def compare(a_path, b_path):
    a, b = json.load(open(a_path)), json.load(open(b_path))
    print(f"{'slice':<28}{'baseline':>10}{'skills':>10}{'delta':>10}")
    print("-" * 58)
    ta = tb = na = nb = 0
    for skill in sorted(set(a["slices"]) | set(b["slices"])):
        ra, rb = a["slices"].get(skill, []), b["slices"].get(skill, [])
        pa, sa = sum(r["passed"] for r in ra), sum(r["total"] for r in ra)
        pb, sb = sum(r["passed"] for r in rb), sum(r["total"] for r in rb)
        fa = 100 * pa / sa if sa else 0
        fb = 100 * pb / sb if sb else 0
        print(f"{skill:<28}{fa:>9.0f}%{fb:>9.0f}%{fb-fa:>+9.0f}")
        ta += pa; na += sa; tb += pb; nb += sb
    print("-" * 58)
    fa = 100 * ta / na if na else 0
    fb = 100 * tb / nb if nb else 0
    print(f"{'TOTAL':<28}{fa:>9.0f}%{fb:>9.0f}%{fb-fa:>+9.0f}")
    print("\nNegative tests (skills should NOT over-fire):")
    for tag, d in (("baseline", a), ("skills", b)):
        rs = [r for s in d["slices"].values() for r in s if r["negative"]]
        p = sum(r["passed"] for r in rs); t = sum(r["total"] for r in rs)
        print(f"  {tag:<10} {p}/{t} ({100*p//t if t else 0}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
