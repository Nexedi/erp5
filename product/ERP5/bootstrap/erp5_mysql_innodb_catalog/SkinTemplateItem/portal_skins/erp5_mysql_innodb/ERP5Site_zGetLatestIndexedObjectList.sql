SELECT
  uid, path
FROM
  catalog
WHERE
  indexation_timestamp >= TIMESTAMPADD(SECOND, - <dtml-sqlvar delta type="int">, CURRENT_TIMESTAMP)
