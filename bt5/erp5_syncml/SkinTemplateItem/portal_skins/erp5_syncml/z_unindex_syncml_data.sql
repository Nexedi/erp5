DELETE FROM syncml
WHERE
  path like <dtml-sqlvar path type="string">
