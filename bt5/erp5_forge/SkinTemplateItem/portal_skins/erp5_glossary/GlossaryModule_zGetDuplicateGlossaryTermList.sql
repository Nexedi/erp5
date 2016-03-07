<dtml-let query="portal_catalog.buildSQLQuery(query=portal_catalog.getSecurityQuery(**selection_params), **selection_params)">

select distinct
  catalog.path, catalog.uid, count(*)-1 as num_of_duplicates
from
  <dtml-in prefix="table" expr="query['from_table_list']">
    <dtml-if "table_key not in ('catalog',)">
      <dtml-var table_item> AS <dtml-var table_key>,
    </dtml-if>
  </dtml-in>
  catalog
where
  catalog.portal_type='Glossary Term'
  and catalog.validation_state in ('draft', 'validated')
  and related_language_title_category.category_strict_membership = 1
  and related_business_field_title_category.category_strict_membership = 1
  <dtml-if "query['where_expression']">
    AND <dtml-var "query['where_expression']">
  </dtml-if>
group by
  catalog.reference, related_language_title_category.category_uid, related_business_field_title_category.category_uid
having
  count(*) > 1
<dtml-if "query['order_by_expression']">
  order by <dtml-var "query['order_by_expression']">
</dtml-if>
</dtml-let>