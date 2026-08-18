import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

result = con.execute("""
    SELECT year(e.wave_date) AS survey_year,
           e.scale_max,
           count(*) AS responses,
           round(100.0 * avg(CASE
               WHEN e.scale_max = 5 AND e.response_value >= 4 THEN 1
               WHEN e.scale_max = 7 AND e.response_value >= 5 THEN 1
               ELSE 0
           END), 1) AS top_box_pct
    FROM fct_engagement_survey e
    JOIN dim_worker w ON w.worker_id = e.worker_id
    WHERE w.worker_type = 'Regular'
      AND e.item_code IN ('ENG01', 'ENG02', 'ENG03')
    GROUP BY year(e.wave_date), e.scale_max
    ORDER BY 1
""").fetchall()

for row in result:
    print(row)

con.close()