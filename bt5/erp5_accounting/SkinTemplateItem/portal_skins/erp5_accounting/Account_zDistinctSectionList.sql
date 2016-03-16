<dtml-let query="portal_catalog.buildSQLQuery(query=portal_catalog.getSecurityQuery())">
SELECT DISTINCT
  catalog.relative_url,
  catalog.path,
  catalog.title,
  catalog.portal_type,
  catalog.validation_state
FROM
  <dtml-in prefix="table" expr="query['from_table_list']">
   <dtml-if "table_key not in ('stock', 'catalog')">
     <dtml-var table_item> AS <dtml-var table_key>,
   </dtml-if>
  </dtml-in>
  catalog,
  stock
WHERE
  stock.mirror_section_uid = catalog.uid
<dtml-if node_uid>
  AND stock.node_uid = <dtml-sqlvar node_uid type="string">
</dtml-if>
<dtml-if at_date>
  AND stock.date <= <dtml-sqlvar at_date type="datetime">
</dtml-if>
<dtml-if simulation_state>
  AND ( stock.simulation_state IN (<dtml-in simulation_state><dtml-sqlvar sequence-item type="string">
                <dtml-unless sequence-end>, </dtml-unless></dtml-in>) )
</dtml-if>

<dtml-if section_uid>
  AND (
    stock.section_uid IN ( <dtml-in section_uid><dtml-sqlvar sequence-item type="int">
        <dtml-unless sequence-end>, </dtml-unless> </dtml-in> )
  )
</dtml-if>

  AND stock.portal_type in ( <dtml-in getPortalAccountingMovementTypeList><dtml-sqlvar
    sequence-item type="string"><dtml-unless sequence-end>, </dtml-unless></dtml-in> )
<dtml-if "query['where_expression']">
  AND <dtml-var "query['where_expression']">
</dtml-if>
ORDER BY
  catalog.portal_type, catalog.title
</dtml-let>