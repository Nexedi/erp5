SELECT
<dtml-if expr="precision is not None">
  SUM(ROUND(<dtml-var stock_table_id>.quantity
    <dtml-if transformed_uid> * transformation.quantity</dtml-if>, <dtml-var precision>)) AS inventory,
  SUM(ROUND(<dtml-var stock_table_id>.quantity
    <dtml-if transformed_uid> * transformation.quantity</dtml-if>, <dtml-var precision>)) AS total_quantity,
  <dtml-if convert_quantity_result>
    SUM(ROUND(<dtml-var stock_table_id>.quantity * measure.quantity
      <dtml-if quantity_unit_uid> / quantity_unit_conversion.quantity</dtml-if>
      <dtml-if transformed_uid> * transformation.quantity</dtml-if>, <dtml-var precision>))
    AS converted_quantity,
  </dtml-if>
  SUM(ROUND(<dtml-var stock_table_id>.total_price, <dtml-var precision>)) AS total_price
<dtml-else>
  SUM(<dtml-var stock_table_id>.quantity <dtml-if transformed_uid> * transformation.quantity</dtml-if>) AS inventory,
  SUM(<dtml-var stock_table_id>.quantity <dtml-if transformed_uid> * transformation.quantity</dtml-if>) AS total_quantity,
  <dtml-if convert_quantity_result>
    ROUND(SUM(<dtml-var stock_table_id>.quantity * measure.quantity
      <dtml-if quantity_unit_uid> / quantity_unit_conversion.quantity</dtml-if>
      <dtml-if transformed_uid> * transformation.quantity</dtml-if>), 12)
    AS converted_quantity,
  </dtml-if>
  SUM(<dtml-var stock_table_id>.total_price) AS total_price
</dtml-if>
<dtml-if inventory_list>
  ,node.title AS node_title,
  node.uid AS node_uid,
  node.relative_url AS node_relative_url,
  section.title AS section_title,
  section.uid AS section_uid,
  section.relative_url AS section_relative_url,
  resource.title AS resource_title,
  resource.relative_url AS resource_relative_url,
<dtml-if transformed_uid>
  transformed_resource.title AS transformed_resource_title,
  transformed_resource.relative_url AS transformed_resource_relative_url,
  transformation.transformed_uid AS transformed_resource_uid,
  transformation.transformed_variation_text AS transformed_variation_text,
</dtml-if>
  <dtml-var stock_table_id>.resource_uid AS resource_uid,
  <dtml-var stock_table_id>.variation_text AS variation_text,
  <dtml-var stock_table_id>.sub_variation_text AS sub_variation_text,
  <dtml-var stock_table_id>.uid AS stock_uid,
  <dtml-var stock_table_id>.date as date,
  <dtml-var stock_table_id>.simulation_state as simulation_state,
  <dtml-var stock_table_id>.mirror_section_uid as mirror_section_uid,
  <dtml-var stock_table_id>.payment_uid as payment_uid,
  <dtml-var stock_table_id>.mirror_node_uid as mirror_node_uid,
  <dtml-if expr="stock_table_id == 'stock'">
    <dtml-var stock_table_id>.explanation_uid as explanation_uid,
  </dtml-if>
  catalog.path as path
</dtml-if>
<dtml-if statistic>
  ,
  COUNT(DISTINCT node.title) AS node_title,
  COUNT(DISTINCT node.relative_url) AS node_relative_url,
  COUNT(DISTINCT section.title) AS section_title,
  COUNT(DISTINCT section.relative_url) AS section_relative_url,
  COUNT(DISTINCT resource.title) AS resource_title,
  COUNT(DISTINCT resource.relative_url) AS resource_relative_url,
  COUNT(DISTINCT <dtml-var stock_table_id>.variation_text) AS variation_text,
  MAX(<dtml-var stock_table_id>.resource_uid) AS resource_uid,
  COUNT(DISTINCT <dtml-var stock_table_id>.uid) AS stock_uid,
  MAX(<dtml-var stock_table_id>.date) AS date
</dtml-if>
<dtml-if select_expression>, <dtml-var select_expression></dtml-if>

FROM
  catalog, <dtml-var stock_table_id>
  <dtml-if section_filtered> INNER <dtml-else> LEFT </dtml-if>
       JOIN catalog AS section ON (section.uid = <dtml-var stock_table_id>.section_uid)
<dtml-if quantity_unit_uid>
  LEFT JOIN quantity_unit_conversion ON
    (quantity_unit_conversion.resource_uid = <dtml-var stock_table_id>.resource_uid
    AND quantity_unit_conversion.quantity_unit_uid = <dtml-sqlvar quantity_unit_uid type=int>)
</dtml-if>
<dtml-in prefix="table" expr="from_table_list">
  <dtml-if expr="table_key not in ('catalog', 'node', stock_table_id)">
  , <dtml-var table_item> AS <dtml-var table_key>
  </dtml-if>
</dtml-in>
  <dtml-if "selection_domain_from_expression">, <dtml-var "selection_domain_from_expression"> </dtml-if>
  , catalog as node, catalog as resource <dtml-if transformed_uid>, transformation, catalog as transformed_resource</dtml-if>

WHERE
  <dtml-var stock_table_id>.uid = catalog.uid
<dtml-if where_expression>
  AND <dtml-var where_expression>
</dtml-if>

  AND node.uid = <dtml-var stock_table_id>.node_uid

<dtml-if transformed_uid>
  AND transformation.uid = <dtml-var stock_table_id>.resource_uid
  AND resource.uid = transformation.uid
  AND <dtml-var stock_table_id>.variation_text = transformation.variation_text

  AND transformed_resource.uid = transformation.transformed_uid
  AND <dtml-sqltest transformed_uid column="transformation.transformed_uid" type=int multiple>
  <dtml-if transformed_variation_text>
  AND <dtml-sqltest transformed_variation_text column="transformation.transformed_variation_text" type=string>
  </dtml-if>
<dtml-else>
  AND resource.uid = <dtml-var stock_table_id>.resource_uid
</dtml-if>

<dtml-if omit_simulation>
  AND catalog.portal_type != 'Simulation Movement'
</dtml-if>

<dtml-if "selection_domain_where_expression">
  AND <dtml-var "selection_domain_where_expression">
</dtml-if>

<dtml-if convert_quantity_result>
  AND concat(<dtml-var stock_table_id>.variation_text,'\n') REGEXP measure.variation
</dtml-if>


<dtml-if group_by_expression>
GROUP BY
    <dtml-if transformed_uid>transformation.transformed_uid,</dtml-if>
    <dtml-var group_by_expression>
</dtml-if>
<dtml-if order_by_expression>
ORDER BY
  <dtml-var order_by_expression>
</dtml-if>
