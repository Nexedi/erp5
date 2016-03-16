<dtml-if select_expression>
SELECT count(*) from (

SELECT DISTINCT
  <dtml-in getCatalogSearchResultKeys> <dtml-var sequence-item><dtml-if sequence-end> <dtml-else>, </dtml-if> </dtml-in>
  <dtml-if select_expression>,<dtml-var select_expression></dtml-if>
<dtml-else>
SELECT COUNT(DISTINCT(catalog.uid)) 
</dtml-if>
FROM
  <dtml-if from_expression>
    <dtml-var from_expression>
  <dtml-else>
    <dtml-in from_table_list> <dtml-var sequence-item> AS <dtml-var sequence-key><dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>
  </dtml-if>
  <dtml-if selection_domain>
    <dtml-let expression="portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_domain, category_table_alias = 'domain_category')">
      <dtml-if expression> , <dtml-var expression> </dtml-if>
    </dtml-let>
  </dtml-if>
  <dtml-if selection_report>
    <dtml-let expression="portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_report, category_table_alias = 'report_category')">
      <dtml-if expression> , <dtml-var expression> </dtml-if>
    </dtml-let>
  </dtml-if>
WHERE
  1 = 1
<dtml-if where_expression>
  AND <dtml-var where_expression>
</dtml-if>
<dtml-if selection_domain>
  <dtml-let expression="portal_selections.buildSQLExpressionFromDomainSelection(selection_domain, category_table_alias = 'domain_category')">
    <dtml-if expression> AND <dtml-var expression> </dtml-if>
  </dtml-let>
</dtml-if>
<dtml-if selection_report>
  <dtml-let expression="portal_selections.buildSQLExpressionFromDomainSelection(selection_report, strict_membership=1, category_table_alias = 'report_category')">
    <dtml-if expression> AND <dtml-var expression> </dtml-if>
  </dtml-let>
</dtml-if>
<dtml-if sort_on>
ORDER BY
  <dtml-var sort_on>
</dtml-if>
<dtml-if group_by_expression>
GROUP BY
  <dtml-var group_by_expression>
</dtml-if>
<dtml-if select_expression>
) as q
</dtml-if>

<dtml-comment>XXX what is the meaning of limit_expression while counting ? -jerome</dtml-comment>
<dtml-if limit_expression>
LIMIT <dtml-var "limit_expression">
</dtml-if>
