SELECT DISTINCT
  catalog.uid, catalog.path
FROM
  catalog, category
WHERE
  catalog.path != 'deleted'
AND  catalog.uid = category.uid
AND  category.category_uid = <dtml-sqlvar category_uid type="int">