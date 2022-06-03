SELECT
  uid, path
FROM
  catalog
WHERE
  path != 'reserved'
  AND TIMESTAMPDIFF(SECOND, indexation_timestamp, CURRENT_TIMESTAMP) <= <dtml-sqlvar delta type="int">
