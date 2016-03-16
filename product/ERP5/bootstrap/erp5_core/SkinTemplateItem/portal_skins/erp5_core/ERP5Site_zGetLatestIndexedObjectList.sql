SELECT
  uid, path
FROM
  catalog
WHERE
  path != 'reserved'
  AND CURRENT_TIMESTAMP - indexation_timestamp <= <dtml-sqlvar delta type="int">
ORDER BY
  indexation_timestamp DESC