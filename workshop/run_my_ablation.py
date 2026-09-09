#!/usr/bin/env python3
"""
Run YOUR OWN ablation: your eval, your reference doc, baseline vs. skill.

This is not the pack's full ablation (evals/run_evals.py) -- that runs 29
evals x 6 slices for the people maintaining the pack. This runs the ONE eval
you wrote in Validate, against the ONE reference doc you wrote in Build, on
your own machine, with your own API key. It's built to finish in well under a
minute so a whole room can run it at the same time without anyone waiting.

Supports three providers, auto-detected from whichever API key is set:
    ANTHROPIC_API_KEY  -> Claude (default, recommended)
    OPENAI_API_KEY     -> OpenAI (GPT-4o or similar)
    GOOGLE_API_KEY     -> Google Gemini

If multiple keys are set, pass --provider to choose explicitly.

Usage (from the repo root or from workshop/):
    python run_my_ablation.py
    python run_my_ablation.py --provider openai
    python run_my_ablation.py --provider gemini

Does NOT touch evals/results/ -- that directory holds the pack's own official
ablation. This writes nowhere by default; pass --save to write a timestamped
file in workshop/.
"""

import argparse
import glob
import json
import os
import re
import sys
import time
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # workshop/ -> repo root
DB = os.path.join(ROOT, "warehouse", "people_analytics.duckdb")

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

EVAL_DEFAULT = os.path.join(ROOT, "evals", "my-eval.json")
KNOWN_DOMAINS = {"attrition.md", "compensation.md", "engagement.md"}

# Default models per provider
MODELS = {
    "anthropic": {"agent": "claude-sonnet-5", "grader": "claude-sonnet-5"},
    "openai": {"agent": "gpt-4o", "grader": "gpt-4o"},
    "gemini": {"agent": "gemini-2.5-flash", "grader": "gemini-2.5-flash"},
}

FATAL_MARKERS = (
    "credit balance is too low",
    "authentication_error",
    "invalid x-api-key",
    "invalid_api_key",
    "permission_error",
    "account has been disabled",
    "quota exceeded",
    "billing",
)

# ---------------------------------------------------------------- SQL tool
def run_sql(query):
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


# ---------------------------------------------------------------- provider: Anthropic
def _call_agent_anthropic(client, prompt, system, model, max_turns=10):
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
            model=model, max_tokens=3000,
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


def _grade_anthropic(client, ev, response, model):
    numbered = "\n".join(f"{i+1}. {a}" for i, a in enumerate(ev["assertions"]))
    msg = client.messages.create(
        model=model, max_tokens=2000,
        messages=[{"role": "user", "content": GRADER_PROMPT.format(
            prompt=ev["prompt"], expected=ev.get("expected_output", ""),
            response=response, assertions=numbered)}])
    raw = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    return json.loads(raw)["results"]


# ---------------------------------------------------------------- provider: OpenAI
def _call_agent_openai(client, prompt, system, model, max_turns=10):
    tools = [{
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": "Execute a read-only SQL query against the DuckDB warehouse.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    }]
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    for _ in range(max_turns):
        resp = client.chat.completions.create(
            model=model, max_tokens=3000,
            tools=tools, messages=messages)
        choice = resp.choices[0]
        messages.append(choice.message)
        if not choice.message.tool_calls:
            break
        for tc in choice.message.tool_calls:
            args = json.loads(tc.function.arguments)
            result = run_sql(args.get("query", ""))
            messages.append({
                "role": "tool", "tool_call_id": tc.id, "content": result,
            })
    return choice.message.content or ""


def _grade_openai(client, ev, response, model):
    numbered = "\n".join(f"{i+1}. {a}" for i, a in enumerate(ev["assertions"]))
    resp = client.chat.completions.create(
        model=model, max_tokens=2000,
        messages=[{"role": "user", "content": GRADER_PROMPT.format(
            prompt=ev["prompt"], expected=ev.get("expected_output", ""),
            response=response, assertions=numbered)}])
    raw = resp.choices[0].message.content or ""
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    return json.loads(raw)["results"]


# ---------------------------------------------------------------- provider: Gemini
def _call_agent_gemini(client, prompt, system, model, max_turns=10):
    # Gemini's genai SDK uses a different interface
    from google import genai
    from google.genai import types

    sql_tool = types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="run_sql",
            description="Execute a read-only SQL query against the DuckDB warehouse.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"query": types.Schema(type="STRING")},
                required=["query"],
            ),
        )
    ])

    chat = client.chats.create(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=system,
            tools=[sql_tool],
        ),
    )

    resp = chat.send_message(prompt)
    for _ in range(max_turns):
        # Check for function calls
        fc_parts = [p for p in resp.candidates[0].content.parts
                     if p.function_call and p.function_call.name]
        if not fc_parts:
            break
        tool_responses = []
        for part in fc_parts:
            result = run_sql(part.function_call.args.get("query", ""))
            tool_responses.append(
                types.Part.from_function_response(
                    name="run_sql", response=json.loads(result)))
        resp = chat.send_message(tool_responses)

    # Extract text from the final response
    return "".join(p.text for p in resp.candidates[0].content.parts if p.text)


def _grade_gemini(client, ev, response, model):
    from google.genai import types
    numbered = "\n".join(f"{i+1}. {a}" for i, a in enumerate(ev["assertions"]))
    resp = client.models.generate_content(
        model=model,
        contents=GRADER_PROMPT.format(
            prompt=ev["prompt"], expected=ev.get("expected_output", ""),
            response=response, assertions=numbered),
        config=types.GenerateContentConfig(max_output_tokens=2000))
    raw = resp.text or ""
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    return json.loads(raw)["results"]


# ---------------------------------------------------------------- provider detection
def detect_provider(explicit=None):
    """Return (provider_name, api_key) or exit with a helpful message."""
    providers = [
        ("anthropic", "ANTHROPIC_API_KEY"),
        ("openai", "OPENAI_API_KEY"),
        ("gemini", "GOOGLE_API_KEY"),
    ]

    if explicit:
        for name, env in providers:
            if name == explicit:
                key = os.getenv(env, "")
                if not key:
                    sys.exit(f"\n--provider {name} was specified but {env} is "
                             f"not set.\n")
                return name, key
        sys.exit(f"\nUnknown provider: {explicit}. "
                 f"Options: anthropic, openai, gemini\n")

    found = [(name, os.getenv(env, "")) for name, env in providers if os.getenv(env)]
    if not found:
        sys.exit(
            "\nNo API key found. Set one of these environment variables:\n\n"
            "  ANTHROPIC_API_KEY   (recommended — Claude)\n"
            "  OPENAI_API_KEY      (GPT-4o)\n"
            "  GOOGLE_API_KEY      (Gemini)\n\n"
            "See the pre-work email or run check_setup.py for help.\n")

    if len(found) > 1:
        names = ", ".join(f[0] for f in found)
        print(f"Multiple API keys found ({names}). Using {found[0][0]}.")
        print(f"  Pass --provider <name> to choose a different one.\n")

    return found[0]


def make_client(provider):
    """Create the appropriate API client."""
    if provider == "anthropic":
        from anthropic import Anthropic
        return Anthropic()
    elif provider == "openai":
        from openai import OpenAI
        return OpenAI()
    elif provider == "gemini":
        from google import genai
        return genai.Client()


def call_agent(client, prompt, system, provider, model, max_turns=10):
    fn = {"anthropic": _call_agent_anthropic,
          "openai": _call_agent_openai,
          "gemini": _call_agent_gemini}[provider]
    return fn(client, prompt, system, model, max_turns)


def grade(client, ev, response, provider, model):
    fn = {"anthropic": _grade_anthropic,
          "openai": _grade_openai,
          "gemini": _grade_gemini}[provider]
    try:
        return fn(client, ev, response, model)
    except Exception as e:
        return [{"assertion": i + 1, "verdict": "ERROR", "reason": str(e)}
                for i in range(len(ev["assertions"]))]


# ---------------------------------------------------------------- file finders
def find_eval(path):
    if not os.path.exists(path):
        # Check for common typos
        d = os.path.dirname(path)
        if os.path.isdir(d):
            import difflib
            candidates = [f for f in os.listdir(d) if f.endswith(".json")]
            near = difflib.get_close_matches(os.path.basename(path), candidates, n=1, cutoff=0.6)
            hint = f"\n\nDid you mean: {os.path.join(d, near[0])}" if near else ""
        else:
            hint = ""
        sys.exit(
            f"\nNo eval found at {path}\n\n"
            f"That's the file you wrote in Validate. Save your JSON there --\n"
            f"see validate-worksheet.md step 3 -- then run this again.{hint}\n")
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


# ---------------------------------------------------------------- run + display
def run_one(client, ev, system, provider, models, repeats):
    runs = []
    last_resp, last_graded = "", []
    for _ in range(repeats):
        resp = call_agent(client, ev["prompt"], system, provider,
                          models["agent"])
        if not resp.strip():
            print("  (a run came back empty — skipping it)")
            continue
        graded = grade(client, ev, resp, provider, models["grader"])
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


def preflight(client, provider, model):
    """One tiny call to catch key/credit problems before the real run."""
    try:
        if provider == "anthropic":
            client.messages.create(model=model, max_tokens=4,
                                   messages=[{"role": "user", "content": "ok"}])
        elif provider == "openai":
            client.chat.completions.create(model=model, max_tokens=4,
                                           messages=[{"role": "user", "content": "ok"}])
        elif provider == "gemini":
            client.models.generate_content(model=model, contents="ok")
    except Exception as e:
        msg = str(e)
        print(f"\nPreflight call failed — not running your ablation.\n\n  {msg[:400]}\n")
        if any(m.lower() in msg.lower() for m in FATAL_MARKERS):
            print("This is an account-level problem (key or credit), not a "
                  "bug in your work. Flag the facilitator.")
        sys.exit(1)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(
        description="Run your own ablation: baseline vs. your reference doc.")
    ap.add_argument("--eval", default=EVAL_DEFAULT, help="path to your eval JSON")
    ap.add_argument("--reference", default=None, help="path to your reference doc")
    ap.add_argument("--provider", default=None, choices=["anthropic", "openai", "gemini"],
                    help="which AI provider to use (auto-detected from API key if not set)")
    ap.add_argument("--repeats", type=int, default=1,
                    help="repeat each condition N times (default: 1)")
    ap.add_argument("--save", action="store_true",
                    help="write a timestamped result file in workshop/")
    args = ap.parse_args()

    # Validate local files first — instant, free, most common thing to be wrong.
    ev = find_eval(args.eval)
    ref_path = find_reference(args.reference)
    ref_text = open(ref_path).read() if ref_path else ""

    try:
        import duckdb  # noqa: F401
    except ImportError:
        sys.exit("\nMissing dependency: duckdb\n"
                 "  python -m pip install duckdb\n")

    provider, _key = detect_provider(args.provider)
    models = MODELS[provider]

    try:
        client = make_client(provider)
    except ImportError as e:
        pkg = {"anthropic": "anthropic", "openai": "openai",
               "gemini": "google-genai"}[provider]
        sys.exit(f"\nMissing dependency for {provider}: {e}\n"
                 f"  python -m pip install {pkg}\n")

    print(f"Provider: {provider}  |  Agent: {models['agent']}  |  "
          f"Grader: {models['grader']}")

    preflight(client, provider, models["agent"])
    print("preflight ok\n")

    print(f"Your question:  {ev['prompt']}")
    print(f"Assertions:     {len(ev['assertions'])}")
    if ref_path:
        print(f"Reference doc:  {os.path.relpath(ref_path, ROOT)}")

    base_system = SCHEMA_PREAMBLE.format(db=DB)

    print("\nRunning baseline (no reference doc)...")
    b_avg, b_tot, b_resp, b_graded = run_one(
        client, ev, base_system, provider, models, args.repeats)

    if ref_path:
        print("Running with your reference doc loaded...")
        s_avg, s_tot, s_resp, s_graded = run_one(
            client, ev, base_system + "\n\n" + ref_text, provider, models,
            args.repeats)
    else:
        s_avg = s_tot = s_resp = s_graded = None

    if b_avg is not None:
        print_result("BASELINE", b_avg, b_tot, b_resp, b_graded)
    else:
        print("\nBASELINE: no valid runs (agent returned empty every time)")

    if s_avg is not None:
        print_result("WITH YOUR REFERENCE DOC", s_avg, s_tot, s_resp, s_graded)
        if b_avg is not None:
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
            "provider": provider, "agent_model": models["agent"],
            "prompt": ev["prompt"], "reference_doc": ref_path,
            "baseline": {"avg": b_avg, "total": b_tot, "response": b_resp},
            "with_doc": ({"avg": s_avg, "total": s_tot, "response": s_resp}
                         if s_avg is not None else None),
        }, open(out, "w"), indent=2)
        print(f"\nSaved -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
