#!/usr/bin/env python3
"""
Check that this machine is ready for the workshop.

Run this BEFORE the session. It verifies the Python environment, the packages,
the warehouse, and (optionally) that your API key works.

    python check_setup.py

Everything it reports is actionable. If it says PASS across the board, you are
ready. If not, it tells you the exact command to fix it.

Deliberately depends on nothing outside the standard library, so it runs even
when the environment is broken.
"""

import importlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if os.name == "nt" and not os.environ.get("WT_SESSION"):
    GREEN = RED = YELLOW = DIM = RESET = ""   # older consoles mangle ANSI

results = []


def check(name, ok, detail="", fix=""):
    tag = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
    print(f"  [{tag}] {name}")
    if detail:
        print(f"         {DIM}{detail}{RESET}")
    if not ok and fix:
        print(f"         {YELLOW}fix: {fix}{RESET}")
    results.append(ok)
    return ok


def warn(name, detail="", fix=""):
    print(f"  [{YELLOW}WARN{RESET}] {name}")
    if detail:
        print(f"         {DIM}{detail}{RESET}")
    if fix:
        print(f"         {YELLOW}{fix}{RESET}")


print("\nWorkshop setup check")
print("=" * 62)

# ---------------------------------------------------------------- interpreter
print("\nPython")
v = sys.version_info
check("Python 3.9 or newer",
      v >= (3, 9),
      f"running {v.major}.{v.minor}.{v.micro}",
      "install Python 3.9+ from python.org")
print(f"         {DIM}interpreter: {sys.executable}{RESET}")

# THE most common Windows failure: pip and python are different interpreters.
try:
    out = subprocess.run([sys.executable, "-m", "pip", "--version"],
                         capture_output=True, text=True, timeout=30)
    this_pip = out.stdout.strip()
except Exception as e:
    this_pip = f"(could not run: {e})"

try:
    out2 = subprocess.run(["pip", "--version"], capture_output=True,
                          text=True, timeout=30, shell=(os.name == "nt"))
    bare_pip = out2.stdout.strip()
except Exception:
    bare_pip = ""

if bare_pip and this_pip and bare_pip != this_pip:
    warn("`pip` and `python -m pip` are different installations",
         f"python -m pip -> {this_pip}\n         bare pip      -> {bare_pip}",
         "Always use: python -m pip install <package>\n"
         "         Packages installed with bare `pip` may be invisible to this Python.")

# ---------------------------------------------------------------- packages
print("\nPackages")
for mod, why, optional in [
    ("duckdb", "querying the warehouse", False),
    ("anthropic", "running the eval ablation", True),
]:
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, "__version__", "unknown")
        check(f"{mod} installed", True, f"version {ver}")
    except ImportError:
        if optional:
            warn(f"{mod} not installed",
                 f"only needed for {why}",
                 f"install with: {os.path.basename(sys.executable)} -m pip install {mod}")
        else:
            check(f"{mod} installed", False, f"needed for {why}",
                  f"{os.path.basename(sys.executable)} -m pip install {mod}")

# ---------------------------------------------------------------- warehouse
print("\nWarehouse")
db = os.path.join(HERE, "warehouse", "people_analytics.duckdb")
exists = os.path.exists(db)
if check("warehouse file present", exists, db,
         "cd warehouse && python build_warehouse.py"):
    size = os.path.getsize(db)
    check("warehouse file is a plausible size",
          size > 1_000_000,
          f"{size:,} bytes (expect roughly 6-7 MB)",
          "file was likely truncated in transfer — rebuild it:\n"
          "         cd warehouse && python build_warehouse.py")
    try:
        import duckdb
        con = duckdb.connect(db, read_only=True)
        n = con.execute("SELECT count(*) FROM information_schema.tables "
                        "WHERE table_schema='main'").fetchone()[0]
        hc = con.execute("""
            SELECT count(DISTINCT employee_number) FROM dim_worker_snapshot
            WHERE snapshot_date = DATE '2026-06-30' AND worker_type = 'Regular'
              AND employment_status IN ('Active','On Leave')""").fetchone()[0]
        con.close()
        check("warehouse opens and queries", True, f"{n} tables, headcount check = {hc:,}")
        check("warehouse data matches expected build", hc == 3647,
              f"got {hc:,}, expected 3,647",
              "rebuild from the pinned seed: cd warehouse && python build_warehouse.py")
    except ImportError:
        pass
    except Exception as e:
        check("warehouse opens and queries", False, str(e)[:70],
              "cd warehouse && python build_warehouse.py")

# ---------------------------------------------------------------- api key
print("\nAPI key")
key = os.environ.get("ANTHROPIC_API_KEY", "")
if not key:
    warn("ANTHROPIC_API_KEY not set",
         "needed only for the hands-on agent exercises",
         'set it with:  $env:ANTHROPIC_API_KEY = "sk-ant-..."   (PowerShell)\n'
         '                export ANTHROPIC_API_KEY=sk-ant-...     (macOS/Linux)')
else:
    check("ANTHROPIC_API_KEY is set", True, f"starts {key[:7]}..., length {len(key)}")
    try:
        from anthropic import Anthropic
        print(f"         {DIM}testing a live call...{RESET}")
        Anthropic().messages.create(
            model="claude-sonnet-4-6", max_tokens=8,
            messages=[{"role": "user", "content": "Reply with the word ok."}])
        check("API key works", True, "test call succeeded")
    except ImportError:
        warn("cannot test the key", "anthropic package not installed")
    except Exception as e:
        msg = str(e)
        hint = "check the key is correct and has credit"
        if "credit" in msg.lower() or "billing" in msg.lower():
            hint = "the key is valid but the account needs credit added"
        elif "model" in msg.lower():
            hint = "the model name may have changed — check the API docs"
        check("API key works", False, msg[:70], hint)

# ---------------------------------------------------------------- verdict
print("\n" + "=" * 62)
if all(results):
    print(f"  {GREEN}Ready.{RESET} Everything required is working.\n")
    sys.exit(0)
print(f"  {RED}{results.count(False)} check(s) failed.{RESET} "
      f"See the fix lines above.\n")
sys.exit(1)
