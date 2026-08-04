# The Warehouse

A synthetic people-analytics warehouse: 44 tables, ~5,300 workers, five years of
history, one DuckDB file. No server, no credentials, works offline.

**It is deliberately messy.** A clean warehouse teaches nothing, because there is
nothing for a skill to resolve. This one has the same ambiguities a real HRIS
model accumulates — several plausible answers to simple questions, a column that
was renamed but not removed, rollups that stopped refreshing, and filters that
change the answer materially when you forget them.

Nobody has written the reference documentation. That is the exercise.

## Setup

```bash
pip install -r ../requirements.txt
# or just: pip install duckdb
# Some systems need: pip install duckdb --break-system-packages
```

If a script reports a missing dependency, it will tell you exactly what to
install. If it reports the warehouse file is too small, the `.duckdb` file did
not survive transfer — rebuild it with `python build_warehouse.py`.

```python
import duckdb
con = duckdb.connect("people_analytics.duckdb", read_only=True)
con.execute("SELECT count(*) FROM dim_worker").fetchall()
```

Or from the CLI: `duckdb people_analytics.duckdb`

R users:

```r
install.packages("duckdb")
con <- DBI::dbConnect(duckdb::duckdb(), "people_analytics.duckdb", read_only = TRUE)
```

## Orientation

The as-of date for the whole warehouse is **2026-06-30**. History starts 2021-01-01.

Naming follows a common convention, loosely:

| Prefix | Usually means |
|---|---|
| `dim_` | Descriptive attributes |
| `fct_` | Events or measures |
| `rpt_` | Pre-aggregated reporting output |
| `vw_` | A view-like convenience table |
| `stg_` | Raw staging from the source system |

Loosely is doing real work in that sentence. Conventions in warehouses are
aspirational, and this one is no more disciplined than average.

## Finding your way

```sql
-- What exists?
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'main' ORDER BY table_name;

-- What's in it?
DESCRIBE dim_worker_snapshot;

-- How big?
SELECT table_name, estimated_size FROM duckdb_tables() ORDER BY estimated_size DESC;
```

Several tables are empty. Several are decoys. Some are both. Deciding which is
part of the work.

## Suggested starting questions

These look simple. That is the point — each has more than one defensible answer,
and the gap between them is where the workshop lives.

1. **How many employees do we have?**
2. **What was our attrition rate last year?**
3. **Which departments have the highest attrition?**
4. **Did the Emerging Leaders Program reduce attrition?**
5. **Has engagement improved since 2023?**

Before you query, write down what you expect. Then query. Then compare the number
you got to the number you expected, and to the number the person next to you got.

## Rebuilding

The warehouse is generated from a fixed seed, so it is reproducible:

```bash
python build_warehouse.py
```

Editing `build_warehouse.py` changes the data. If you are running this as a
workshop, rebuild before the session so everyone starts identical, and do not
read the generator beforehand — the failure modes are commented in it, and
reading them first turns the exercise into a reading-comprehension test.

## A note on what this is not

The data is synthetic. Names, orgs, and numbers are generated, and no real person
or organization is represented. Effect sizes were chosen to be pedagogically
legible, not to reflect published base rates — do not cite anything you find here
as a finding about real workforces.
