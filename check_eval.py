#!/usr/bin/env python3
"""
check_eval.py — validates your eval file before running the ablation.

Usage:
    python check_eval.py              # checks evals/my-eval.json (the default)
    python check_eval.py my-file.json # checks a specific file

This catches the most common mistakes — missing commas, wrong quotes,
missing fields — and tells you exactly what to fix.
"""

import json
import os
import sys

# ---------------------------------------------------------------- colors
try:
    import os as _os
    _color = _os.name != "nt" or _os.environ.get("WT_SESSION")
except Exception:
    _color = False

GREEN = "\033[32m" if _color else ""
RED = "\033[31m" if _color else ""
YELLOW = "\033[33m" if _color else ""
RESET = "\033[0m" if _color else ""
BOLD = "\033[1m" if _color else ""

def ok(msg):
    print(f"  {GREEN}[OK]{RESET}  {msg}")

def fail(msg):
    print(f"  {RED}[!!]{RESET}  {msg}")

def warn(msg):
    print(f"  {YELLOW}[--]{RESET}  {msg}")

# ---------------------------------------------------------------- main
def main():
    # Find the file
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.path.join("evals", "my-eval.json")

    print(f"\nChecking: {path}\n")

    # Does it exist?
    if not os.path.exists(path):
        fail(f"File not found: {path}")
        print()
        if path == os.path.join("evals", "my-eval.json"):
            print("  Save your eval file from the Validate worksheet as:")
            print(f"    {path}")
            print()
            print("  Make sure you're running this from the analytics-skills folder,")
            print("  not from inside a subfolder.")
        else:
            print(f"  Check the filename and try again.")
        print()
        sys.exit(1)

    # Can we read it?
    try:
        raw = open(path).read()
    except Exception as e:
        fail(f"Can't read the file: {e}")
        sys.exit(1)

    if not raw.strip():
        fail("The file is empty.")
        sys.exit(1)

    # Is it valid JSON?
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"Not valid JSON: {e}")
        print()
        # Give specific help for common mistakes
        line = e.lineno
        col = e.colno
        lines = raw.split("\n")
        if line and line <= len(lines):
            problem_line = lines[line - 1]
            print(f"  Line {line}: {problem_line.rstrip()}")
            print(f"  {' ' * (col + 9)}^")
        print()
        print("  Common fixes:")
        print("  - Remove the comma after the LAST item in a list (before ] or })")
        print("  - Make sure every piece of text is in double quotes \"like this\"")
        print("  - Check that every { has a matching } and every [ has a matching ]")
        print()
        sys.exit(1)

    ok("Valid JSON")

    # Is it an object with an "evals" list?
    if not isinstance(data, dict):
        fail("The file should be a JSON object (starts with {), not a list or string.")
        sys.exit(1)

    evals = data.get("evals")
    if not evals:
        fail('No "evals" list found.')
        print()
        print('  Your file needs an "evals" key with a list inside it.')
        print("  Check it against the template in validate-worksheet.md step 3.")
        print()
        sys.exit(1)

    if not isinstance(evals, list):
        fail('"evals" should be a list (wrapped in [ ]).')
        sys.exit(1)

    ok(f'Found {len(evals)} eval(s)')

    # Check the first eval
    ev = evals[0]
    errors = 0

    # prompt
    if not ev.get("prompt"):
        fail('Missing "prompt" — paste your question from the Define worksheet.')
        errors += 1
    else:
        ok(f'Prompt: "{ev["prompt"][:60]}{"..." if len(ev["prompt"]) > 60 else ""}"')

    # assertions
    assertions = ev.get("assertions")
    if not assertions:
        fail('Missing "assertions" — add your checklist items from step 3.')
        errors += 1
    elif not isinstance(assertions, list):
        fail('"assertions" should be a list (wrapped in [ ]).')
        errors += 1
    else:
        ok(f"{len(assertions)} assertion(s)")
        for i, a in enumerate(assertions, 1):
            if not isinstance(a, str):
                fail(f"  Assertion {i} should be a string in double quotes.")
                errors += 1
            elif len(a.strip()) < 10:
                warn(f"  Assertion {i} is very short — is it specific enough to check?")
            else:
                print(f"         {i}. {a[:70]}{'...' if len(a) > 70 else ''}")

    # expected_output (optional but helpful)
    if ev.get("expected_output"):
        ok(f'Expected output: "{ev["expected_output"][:60]}..."')
    else:
        warn('"expected_output" is empty or missing — optional, but helps the grader.')

    # Summary
    print()
    if errors == 0:
        print(f"  {GREEN}{BOLD}Ready.{RESET} Your eval file looks good.")
        print(f"  Run the ablation with:  python workshop/run_my_ablation.py")
    else:
        print(f"  {RED}{BOLD}{errors} problem(s) to fix.{RESET}")
        print(f"  Check your file against the template in validate-worksheet.md step 3.")
    print()

    sys.exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()
