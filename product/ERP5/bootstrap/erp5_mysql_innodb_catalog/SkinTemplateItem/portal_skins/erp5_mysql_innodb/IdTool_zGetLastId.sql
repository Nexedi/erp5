SELECT
  last_id AS `LAST_INSERT_ID`
FROM portal_ids
WHERE
  `id_group` = <dtml-sqlvar id_group type="string">
