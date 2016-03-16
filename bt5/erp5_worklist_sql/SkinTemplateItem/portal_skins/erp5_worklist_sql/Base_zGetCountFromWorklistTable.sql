SELECT
  <dtml-var select_expression>
FROM
  worklist_cache
WHERE
  <dtml-var where_expression>
GROUP BY
  <dtml-var group_by_expression>
