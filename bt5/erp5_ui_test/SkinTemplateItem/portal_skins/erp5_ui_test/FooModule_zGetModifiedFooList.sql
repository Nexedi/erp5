SELECT
  uid, path, CONCAT('Foo ', title) AS title
FROM
  catalog
WHERE
  portal_type = 'Foo'
  AND parent_uid = <dtml-var "context.getUid()">
ORDER BY
  id
LIMIT 1000
