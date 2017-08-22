SELECT DISTINCT
  <dtml-in getCatalogSearchResultKeys> <dtml-var sequence-item><dtml-if sequence-end> <dtml-else>, </dtml-if> </dtml-in>
  <dtml-if select_expression>,<dtml-var select_expression></dtml-if>

FROM
  <dtml-if from_expression>
    <dtml-var from_expression>
  <dtml-else>
    <dtml-in from_table_list> <dtml-var sequence-item> AS <dtml-var sequence-key><dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>
  </dtml-if>

WHERE 
  1 = 1 
<dtml-if where_expression>
  AND <dtml-var where_expression>
</dtml-if>
<dtml-if group_by_expression>
GROUP BY
  <dtml-var group_by_expression>
</dtml-if>
<dtml-if sort_on>
ORDER BY
  <dtml-var sort_on>
</dtml-if>
<dtml-if limit_expression>
LIMIT <dtml-var "limit_expression">
</dtml-if>
