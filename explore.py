import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

result = con.execute("""
    SELECT * FROM fct_separation LIMIT 5
""").fetchall()

for row in result:
    print(row)

con.close()