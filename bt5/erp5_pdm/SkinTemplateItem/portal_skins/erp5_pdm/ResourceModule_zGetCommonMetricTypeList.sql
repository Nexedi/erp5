SELECT catalog.*
FROM (SELECT metric_type_uid,
             COUNT(DISTINCT resource_uid) AS resource_count
      FROM measure
      WHERE <dtml-sqltest resource_uid type="int" multiple>
      GROUP BY metric_type_uid
     ) AS measure,
     catalog
WHERE catalog.uid = measure.metric_type_uid
  AND <dtml-sqltest column="measure.resource_count"
                    expr="_.len(resource_uid)"
                    type="int">
