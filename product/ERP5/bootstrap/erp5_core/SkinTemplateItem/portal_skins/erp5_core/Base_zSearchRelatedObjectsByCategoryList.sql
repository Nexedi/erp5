SELECT DISTINCT catalog.uid, path, relative_url, portal_type
FROM catalog, category
WHERE catalog.uid = category.uid
  <dtml-if portal_type>
    AND <dtml-sqltest portal_type type="string" multiple>
  </dtml-if>
  AND (<dtml-var "portal_categories.buildSQLSelector(category_list)">)
  <dtml-if strict_membership>
    AND category.category_strict_membership = 1
  </dtml-if>
  <dtml-if where_expression>
    AND <dtml-var where_expression>
  </dtml-if>
<dtml-if order_by_expression>
ORDER BY
  <dtml-var order_by_expression>
</dtml-if>