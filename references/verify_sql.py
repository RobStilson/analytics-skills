#!/usr/bin/env python3
"""
Execute every ```sql block in the reference docs against the warehouse.

Blocks that are comment-only are treated as illustrative and skipped. Anything
else must run. Offline, free, fast — wire it into CI alongside evals/verify.py.

Usage:  python references/verify_sql.py
"""
import re, sys, pathlib

try:
    import duckdb
except ImportError:
    sys.exit("\nMissing dependency: duckdb\n  Install it with:  pip install duckdb\n")

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "warehouse" / "people_analytics.duckdb"
DOCS = sorted((ROOT / "references").glob("*.md"))

def main():
    if not DB.exists():
        print(f"FAIL  warehouse missing at {DB}")
        print("      cd warehouse && python build_warehouse.py")
        return 1
    con = duckdb.connect(str(DB), read_only=True)
    failures = 0
    for doc in DOCS:
        blocks = re.findall(r"```sql\n(.*?)```", doc.read_text(), re.S)
        if not blocks:
            continue
        print(f"\n{doc.name}")
        for i, b in enumerate(blocks, 1):
            stripped = "\n".join(
                l for l in b.splitlines() if not l.strip().startswith("--")).strip()
            if not stripped:
                print(f"  skip  block {i}  (illustrative)")
                continue
            # Non-executable by design: template placeholders, elided code, and
            # bare clause fragments shown as snippets rather than whole queries.
            if "<!--" in stripped or "..." in stripped:
                print(f"  skip  block {i}  (placeholder or elided)")
                continue
            first = stripped.split()[0].upper()
            if first in {"WHERE", "GROUP", "ORDER", "HAVING", "AND", "OR", "JOIN", "FROM"}:
                print(f"  skip  block {i}  (clause fragment)")
                continue
            try:
                n = len(con.execute(stripped).fetchall())
                print(f"  ok    block {i}  {n} rows")
            except Exception as e:
                print(f"  FAIL  block {i}  {str(e)[:80]}")
                failures += 1
    con.close()
    print(f"\n{'PASS' if not failures else str(failures) + ' FAILING BLOCK(S)'}")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
