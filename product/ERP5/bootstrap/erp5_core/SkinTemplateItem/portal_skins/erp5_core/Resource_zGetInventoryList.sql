<dtml-let interpolation_ratio="SimulationTool_zGetInterpolationMethod(
  stock_table_id=stock_table_id,
  interpolation_method=interpolation_method,
  interpolation_method_from_date=interpolation_method_from_date,
  interpolation_method_to_date=interpolation_method_to_date,
  interpolation_method_at_date=interpolation_method_at_date,
  group_by_time_sequence_list=group_by_time_sequence_list,
  src__=1)">

SELECT
<dtml-if expr="precision is not None">
  SUM(ROUND(
    <dtml-var stock_table_id>.quantity
    <dtml-if transformed_uid> * transformation.quantity</dtml-if>
    * <dtml-var interpolation_ratio>, <dtml-var precision>)) AS inventory,
  SUM(ROUND(
    <dtml-var stock_table_id>.quantity
    <dtml-if transformed_uid> * transformation.quantity</dtml-if>
    * <dtml-var interpolation_ratio>, <dtml-var precision>)) AS total_quantity,
  <dtml-if convert_quantity_result>
    SUM(ROUND(<dtml-var stock_table_id>.quantity * measure.quantity
      <dtml-if quantity_unit_uid> / quantity_unit_conversion.quantity</dtml-if>
    * <dtml-var interpolation_ratio>, <dtml-var precision>))
    AS converted_quantity,
  </dtml-if>

  IFNULL(SUM(ROUND(
    <dtml-var stock_table_id>.total_price * <dtml-var interpolation_ratio>, <dtml-var precision>)), 0) AS total_price
<dtml-else>
  SUM(<dtml-var stock_table_id>.quantity
      <dtml-if transformed_uid> * transformation.quantity</dtml-if>
      * <dtml-var interpolation_ratio>
     ) AS inventory,
  SUM(<dtml-var stock_table_id>.quantity
      <dtml-if transformed_uid> * transformation.quantity</dtml-if>
      * <dtml-var interpolation_ratio>
     ) AS total_quantity,
  <dtml-if convert_quantity_result>
    ROUND(SUM(<dtml-var stock_table_id>.quantity * measure.quantity
      <dtml-if quantity_unit_uid> / quantity_unit_conversion.quantity</dtml-if>
      <dtml-if transformed_uid> * transformation.quantity</dtml-if> * <dtml-var interpolation_ratio>), 12)
    AS converted_quantity,
  </dtml-if>
  IFNULL(SUM(<dtml-var stock_table_id>.total_price * <dtml-var interpolation_ratio>), 0) AS total_price
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
<dtml-if group_by_time_sequence_list>, slot_index </dtml-if> <dtml-comment>XXX is this really needed? are empty slots returned ? </dtml-comment>

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

   <dtml-if group_by_time_sequence_list>
     RIGHT JOIN
       ( <dtml-in prefix="time_slot" expr="_.list(_.enumerate(group_by_time_sequence_list))">
         SELECT
           <dtml-sqlvar expr="time_slot_key" type="int"> slot_index,
           <dtml-sqlvar expr="time_slot_item.get('from_date')" type="datetime" optional> slot_from_date,
           <dtml-sqlvar expr="time_slot_item.get('at_date')" type="datetime" optional> slot_at_date,
           <dtml-sqlvar expr="time_slot_item.get('to_date')" type="datetime" optional> slot_to_date

         <dtml-unless time_slot_end>UNION ALL</dtml-unless>
       </dtml-in> ) slots
     ON
     <dtml-if group_by_time_sequence_list>
     (
       ( slot_from_date is not null AND
        ( slot_at_date is not null AND
         GREATEST(`stock`.`date`, `stock`.`mirror_date`) >= slot_from_date AND
         LEAST(`stock`.`date`, `stock`.`mirror_date`) <= slot_at_date
        ) OR (
          (
            slot_to_date is not null AND
            GREATEST(`stock`.`date`, `stock`.`mirror_date`) >= slot_from_date AND
            LEAST(`stock`.`date`, `stock`.`mirror_date`) < slot_to_date
          ) OR (
            GREATEST(`stock`.`date`, `stock`.`mirror_date`) >= slot_from_date AND
            slot_at_date is null AND slot_to_date is null
          )
        )
       ) OR (
         slot_from_date is null AND (
           ( slot_at_date is not null AND
            ( LEAST(`stock`.`date`, `stock`.`mirror_date`) <= slot_at_date )
           ) OR  LEAST(`stock`.`date`, `stock`.`mirror_date`) < slot_to_date
         )
       )
     )
     <dtml-else>
     (
       ( slot_from_date is null OR stock.date >= slot_from_date )
       AND ( slot_at_date is null OR stock.date <= slot_at_date )
       AND ( slot_to_date is null OR stock.date < slot_to_date )
     )
     </dtml-if>
   </dtml-if>




</dtml-if>
<dtml-if quantity_unit_uid> <dtml-comment>XXX quantity unit conversion will not work when using implict_join=False</dtml-comment>
  LEFT JOIN quantity_unit_conversion ON 
    (quantity_unit_conversion.resource_uid = <dtml-var stock_table_id>.resource_uid
    AND quantity_unit_conversion.quantity_unit_uid = <dtml-sqlvar quantity_unit_uid type=int>)
</dtml-if>
  <dtml-if selection_domain><dtml-let expression="portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_domain, category_table_alias='domain_category')"><dtml-if expression>, <dtml-var expression></dtml-if></dtml-let></dtml-if>
  <dtml-if selection_report><dtml-let expression="portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_report, category_table_alias='report_category')"><dtml-if expression>, <dtml-var expression></dtml-if></dtml-let></dtml-if>
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
<dtml-if selection_domain>
  AND <dtml-var "portal_selections.buildSQLExpressionFromDomainSelection(selection_domain, category_table_alias='domain_category', join_table=stock_table_id, join_column='node_uid')">
</dtml-if>
<dtml-if selection_report>
  AND <dtml-var "portal_selections.buildSQLExpressionFromDomainSelection(selection_report, category_table_alias='report_category', strict_membership=1)">
</dtml-if>

<dtml-if convert_quantity_result>
  AND concat(<dtml-var stock_table_id>.variation_text,'\n') REGEXP measure.variation
</dtml-if>

<dtml-if group_by_expression>
GROUP BY
    <dtml-if transformed_uid>transformation.transformed_uid,</dtml-if>
    <dtml-if group_by_time_sequence_list>slot_index,</dtml-if>
    <dtml-var group_by_expression>

</dtml-if>
<dtml-if order_by_expression>
ORDER BY
  <dtml-var order_by_expression>
<dtml-else>
  <dtml-if group_by_time_sequence_list>
    ORDER BY slot_index
  </dtml-if>
</dtml-if>
</dtml-let>
