import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

# List populated tables
print(con.execute("""
    SELECT t.table_name, 
           (SELECT count(*) FROM information_schema.columns c 
            WHERE c.table_name = t.table_name) as cols
    FROM information_schema.tables t 
    WHERE t.table_schema = 'main' 
    ORDER BY 1
""").fetchdf())

# Quick look at any table
print(con.execute("SELECT * FROM fct_separation LIMIT 10").fetchdf())