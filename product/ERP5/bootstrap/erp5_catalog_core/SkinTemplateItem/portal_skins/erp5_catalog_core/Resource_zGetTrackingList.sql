SELECT 
  item.aggregate_uid AS uid,
  item_catalog.path AS path,
  item.date AS date,
  item.node_uid AS node_uid,
  item.section_uid AS section_uid,
  item.resource_uid AS resource_uid,
  item.variation_text AS variation_text,
  item.uid AS delivery_uid
FROM
  catalog as item_catalog
<dtml-if from_table_list>
  <dtml-in prefix="table" expr="from_table_list"> 
    <dtml-if expr="table_key != 'item'">, <dtml-var table_item> AS <dtml-var table_key></dtml-if>
  </dtml-in>
</dtml-if>
<dtml-if "selection_domain_from_expression">, <dtml-var "selection_domain_from_expression"> </dtml-if>
, item

<dtml-if join_on_item>
  LEFT JOIN 
    item AS next_item
  ON (
    <dtml-if date_condition_in_join>
    <dtml-if expr="at_date is not None">
       next_item.date <= <dtml-sqlvar at_date type="string">
    <dtml-else>
       next_item.date < <dtml-sqlvar to_date type="string">
    </dtml-if>
    AND
    </dtml-if>
    next_item.aggregate_uid = item.aggregate_uid
  AND
    <dtml-if input>
      next_item.date < item.date
    <dtml-else>
      next_item.date > item.date
    </dtml-if>
  <dtml-if simulation_state_list>
   AND (
    <dtml-in simulation_state_list>
      next_item.simulation_state =  <dtml-sqlvar sequence-item type="string"> 
      <dtml-if sequence-end>
      <dtml-else>
        OR  
      </dtml-if>
    </dtml-in>
    )
  </dtml-if>
  )
</dtml-if>

WHERE
  1 = 1

<dtml-if where_expression>
  AND <dtml-var where_expression>
</dtml-if>

  AND item_catalog.uid = item.aggregate_uid

<dtml-if join_on_item>
  AND next_item.uid IS NULL
</dtml-if>

<dtml-if "selection_domain_where_expression">
  <dtml-in selection_domain_catalog_alias_set>
    AND <dtml-var stock_table_id>.<dtml-var sequence-item>_uid = <dtml-var sequence-item>.uid
  </dtml-in>
  AND <dtml-var "selection_domain_where_expression">
</dtml-if>

<dtml-if group_by_expression>
GROUP BY <dtml-var group_by_expression>
</dtml-if>

<dtml-if order_by_expression>
ORDER BY
  <dtml-var order_by_expression>
<dtml-else>
ORDER BY item.date DESC
</dtml-if>
