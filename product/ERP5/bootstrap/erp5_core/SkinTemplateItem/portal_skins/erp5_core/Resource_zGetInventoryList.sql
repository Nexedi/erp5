<dtml-if group_by_time_interval_list>
SELECT slots.time_interval_index, q.* FROM (
</dtml-if>
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
  IFNULL(SUM(ROUND(<dtml-var stock_table_id>.total_price, <dtml-var precision>)), 0) AS total_price
<dtml-else>
  SUM(<dtml-var stock_table_id>.quantity <dtml-if transformed_uid> * transformation.quantity</dtml-if>) AS inventory,
  SUM(<dtml-var stock_table_id>.quantity <dtml-if transformed_uid> * transformation.quantity</dtml-if>) AS total_quantity,
  <dtml-if convert_quantity_result>
    ROUND(SUM(<dtml-var stock_table_id>.quantity * measure.quantity
      <dtml-if quantity_unit_uid> / quantity_unit_conversion.quantity</dtml-if>
      <dtml-if transformed_uid> * transformation.quantity</dtml-if>), 12)
    AS converted_quantity,
  </dtml-if>
  IFNULL(SUM(<dtml-var stock_table_id>.total_price), 0) AS total_price
</dtml-if>
<dtml-if inventory_list>
  ,
  <dtml-var stock_table_id>.node_uid AS node_uid,
  <dtml-var stock_table_id>.section_uid AS section_uid,
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
  <dtml-var stock_table_id>.mirror_date as mirror_date,
  <dtml-var stock_table_id>.simulation_state as simulation_state,
  <dtml-var stock_table_id>.mirror_section_uid as mirror_section_uid,
  <dtml-var stock_table_id>.payment_uid as payment_uid,
  <dtml-var stock_table_id>.mirror_node_uid as mirror_node_uid,
  <dtml-var stock_table_id>.function_uid as function_uid,
  <dtml-var stock_table_id>.project_uid as project_uid,
  <dtml-var stock_table_id>.funding_uid as funding_uid,
  <dtml-var stock_table_id>.ledger_uid as ledger_uid,
  <dtml-var stock_table_id>.payment_request_uid as payment_request_uid,
  catalog.path as path
</dtml-if>
<dtml-if statistic>
  ,
  COUNT(DISTINCT <dtml-var stock_table_id>.variation_text) AS variation_text,
  MAX(<dtml-var stock_table_id>.resource_uid) AS resource_uid,
  COUNT(DISTINCT <dtml-var stock_table_id>.uid) AS stock_uid,
  MAX(<dtml-var stock_table_id>.date) AS date
</dtml-if>
<dtml-if group_by_time_interval_list>, time_interval_index as _time_interval_index</dtml-if>

<dtml-if select_expression>, <dtml-var select_expression></dtml-if>

FROM
<dtml-if from_expression>
  <dtml-var from_expression>
<dtml-else>
  catalog
<dtml-in prefix="table" expr="from_table_list">
  <dtml-if expr="table_key not in ('catalog', stock_table_id)">
  , <dtml-var table_item> AS <dtml-var table_key>
  </dtml-if>
</dtml-in>
, <dtml-var stock_table_id>

   <dtml-if group_by_time_interval_list>
     RIGHT JOIN
       ( <dtml-in prefix="time_interval" expr="_.list(_.enumerate(group_by_time_interval_list))">
         SELECT
           <dtml-sqlvar expr="time_interval_key" type="int"> time_interval_index,
           <dtml-sqlvar expr="time_interval_item.get('from_date')" type="datetime" optional> time_interval_from_date,
           <dtml-sqlvar expr="time_interval_item.get('at_date')" type="datetime" optional> time_interval_at_date,
           <dtml-sqlvar expr="time_interval_item.get('to_date')" type="datetime" optional> time_interval_to_date

         <dtml-unless time_interval_end>UNION ALL</dtml-unless>
       </dtml-in> ) slots
     ON
     <dtml-if group_by_time_interval_list>
     (
       ( time_interval_from_date is not null AND
        ( time_interval_at_date is not null AND
         GREATEST(`stock`.`date`, `stock`.`mirror_date`) >= time_interval_from_date AND
         LEAST(`stock`.`date`, `stock`.`mirror_date`) <= time_interval_at_date
        ) OR (
          (
            time_interval_to_date is not null AND
            GREATEST(`stock`.`date`, `stock`.`mirror_date`) >= time_interval_from_date AND
            LEAST(`stock`.`date`, `stock`.`mirror_date`) < time_interval_to_date
          ) OR (
            GREATEST(`stock`.`date`, `stock`.`mirror_date`) >= time_interval_from_date AND
            time_interval_at_date is null AND time_interval_to_date is null
          )
        )
       ) OR (
         time_interval_from_date is null AND (
           ( time_interval_at_date is not null AND
            ( LEAST(`stock`.`date`, `stock`.`mirror_date`) <= time_interval_at_date )
           ) OR  LEAST(`stock`.`date`, `stock`.`mirror_date`) < time_interval_to_date
         )
       )
     )
     <dtml-else>
     (
       ( time_interval_from_date is null OR stock.date >= time_interval_from_date )
       AND ( time_interval_at_date is null OR stock.date <= time_interval_at_date )
       AND ( time_interval_to_date is null OR stock.date < time_interval_to_date )
     )
     </dtml-if>
   </dtml-if>




</dtml-if>
<dtml-if quantity_unit_uid> <dtml-comment>XXX quantity unit conversion will not work when using implict_join=False</dtml-comment>
  LEFT JOIN quantity_unit_conversion ON
    (quantity_unit_conversion.resource_uid = <dtml-var stock_table_id>.resource_uid
    AND quantity_unit_conversion.quantity_unit_uid = <dtml-sqlvar quantity_unit_uid type=int>)
</dtml-if>
  <dtml-if "selection_domain_from_expression">, <dtml-var "selection_domain_from_expression"> </dtml-if>

  <dtml-if transformed_uid>, transformation, catalog as transformed_resource</dtml-if>

WHERE
  <dtml-var stock_table_id>.uid = catalog.uid
<dtml-if where_expression>
  AND <dtml-var where_expression>
</dtml-if>

<dtml-if transformed_uid>
  AND transformation.uid = <dtml-var stock_table_id>.resource_uid
  AND <dtml-var stock_table_id>.variation_text = transformation.variation_text

  AND transformed_resource.uid = transformation.transformed_uid
  AND <dtml-sqltest transformed_uid column="transformation.transformed_uid" type=int multiple>
  <dtml-if transformed_variation_text>
  AND <dtml-sqltest transformed_variation_text column="transformation.transformed_variation_text" type=string>
  </dtml-if>
</dtml-if>

<dtml-if omit_simulation>
  AND <dtml-var stock_table_id>.portal_type != 'Simulation Movement'
</dtml-if>
<dtml-if only_accountable>
  AND <dtml-var stock_table_id>.is_accountable
</dtml-if>
<dtml-if "selection_domain_where_expression">
  <dtml-in selection_domain_catalog_alias_set>
    AND <dtml-var stock_table_id>.<dtml-var sequence-item>_uid = <dtml-var sequence-item>.uid
  </dtml-in>
  AND <dtml-var "selection_domain_where_expression">
</dtml-if>

<dtml-if convert_quantity_result>
  AND concat(<dtml-var stock_table_id>.variation_text,'\n') REGEXP measure.variation
</dtml-if>

<dtml-if group_by_expression>
GROUP BY
    <dtml-if transformed_uid>transformation.transformed_uid,</dtml-if>
    <dtml-if group_by_time_interval_list>time_interval_index,</dtml-if>
    <dtml-var group_by_expression>

</dtml-if>
<dtml-if order_by_expression>
ORDER BY
  <dtml-var order_by_expression>
<dtml-else>
  <dtml-if group_by_time_interval_list>
    ORDER BY time_interval_index
  </dtml-if>
</dtml-if>
<dtml-if group_by_time_interval_list>
) q
  RIGHT JOIN
    ( <dtml-in prefix="time_interval" expr="_.list(_.enumerate(group_by_time_interval_list))">
      SELECT
        <dtml-sqlvar expr="time_interval_key" type="int"> time_interval_index,
        <dtml-sqlvar expr="time_interval_item.get('from_date')" type="datetime" optional> time_interval_from_date,
        <dtml-sqlvar expr="time_interval_item.get('at_date')" type="datetime" optional> time_interval_at_date,
        <dtml-sqlvar expr="time_interval_item.get('to_date')" type="datetime" optional> time_interval_to_date

      <dtml-unless time_interval_end>UNION ALL</dtml-unless>
    </dtml-in> ) slots ON (q._time_interval_index = slots.time_interval_index)
</dtml-if>
