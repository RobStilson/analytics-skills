import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

df = con.execute("""
    SELECT * FROM dim_worker_snapshot LIMIT 5
""").fetchdf()

print(df.to_string())

con.close()