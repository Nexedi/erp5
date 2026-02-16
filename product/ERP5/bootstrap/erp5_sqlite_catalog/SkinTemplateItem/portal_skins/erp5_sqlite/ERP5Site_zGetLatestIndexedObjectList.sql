SELECT
  uid, path
FROM
  catalog
WHERE
  indexation_timestamp >= DATETIME('now', '-' || <dtml-sqlvar delta type="int"> || ' seconds')
