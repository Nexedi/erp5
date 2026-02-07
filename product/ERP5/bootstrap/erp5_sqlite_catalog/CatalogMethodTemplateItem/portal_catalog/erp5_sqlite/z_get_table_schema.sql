WITH tables AS (
  SELECT name AS table_name
  FROM sqlite_master
  WHERE type='table' AND name NOT LIKE 'sqlite_%'
)
SELECT
  t.table_name,
  c.name AS column_name
FROM tables t,
     pragma_table_info(t.table_name) AS c;