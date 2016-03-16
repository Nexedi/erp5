SELECT
<dtml-if expr="precision is not None">
  SUM(ROUND(stock.quantity, <dtml-var precision>)) AS inventory,
  SUM(ROUND(stock.quantity, <dtml-var precision>)) AS total_quantity,
  SUM(ROUND(stock.total_price, <dtml-var precision>)) AS total_price,
<dtml-else>
  SUM(stock.quantity) AS inventory,
  SUM(stock.quantity) AS total_quantity,
  SUM(stock.total_price) AS total_price,
</dtml-if>
  COUNT(DISTINCT stock.variation_text) AS variation_text,
  MAX(stock.resource_uid) AS resource_uid,
  COUNT(DISTINCT stock.uid) AS stock_uid,
  MAX(stock.date) AS date

FROM
  stock
<dtml-in prefix="table" expr="from_table_list"> 
  <dtml-if expr="table_key != 'stock'">
  , <dtml-var table_item> AS <dtml-var table_key>
  </dtml-if>
</dtml-in>
  <dtml-if selection_domain>,
    <dtml-var "portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_domain)"> </dtml-if>
  <dtml-if selection_report>,
    <dtml-var "portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_report)"> </dtml-if>

WHERE
  1 = 1
<dtml-if where_expression>
  AND <dtml-var where_expression>
</dtml-if>

<dtml-if omit_simulation>
  AND stock.portal_type != 'Simulation Movement'
</dtml-if>

<dtml-if omit_input>
  AND ( ( stock.is_cancellation AND stock.quantity > 0 )
        OR ( not stock.is_cancellation AND stock.quantity < 0 ))
  AND (  stock.node_uid <> stock.mirror_node_uid
        OR stock.section_uid <> stock.mirror_section_uid
        OR stock.mirror_node_uid IS NULL
        OR stock.mirror_section_uid IS NULL
        OR stock.payment_uid IS NOT NULL )
</dtml-if>
<dtml-if omit_output>
  AND ( ( stock.is_cancellation AND stock.quantity < 0 )
        OR ( not stock.is_cancellation AND stock.quantity > 0 ))
  AND (  stock.node_uid <> stock.mirror_node_uid
        OR stock.section_uid <> stock.mirror_section_uid
        OR stock.mirror_node_uid IS NULL
        OR stock.mirror_section_uid IS NULL
        OR stock.payment_uid IS NOT NULL )
</dtml-if>

<dtml-if input_simulation_state>
  <dtml-if output_simulation_state>
    <dtml-if "input_simulation_state == output_simulation_state">
      AND (<dtml-in input_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'<dtml-unless sequence-end> OR </dtml-unless></dtml-in>)
    <dtml-else>
      AND ((stock.quantity>0
        AND (<dtml-in input_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'<dtml-unless sequence-end> OR </dtml-unless></dtml-in>))
      OR (stock.quantity<0
        AND (<dtml-in output_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'<dtml-unless sequence-end> OR </dtml-unless></dtml-in>)))
    </dtml-if>
  <dtml-else>
    AND stock.quantity>0
    AND (<dtml-in input_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'<dtml-unless sequence-end> OR </dtml-unless></dtml-in>)
  </dtml-if>
<dtml-elif output_simulation_state>
  AND stock.quantity<0
  AND (<dtml-in output_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'<dtml-unless sequence-end> OR </dtml-unless></dtml-in>)
</dtml-if>

<dtml-if selection_domain>
  AND <dtml-var "portal_selections.buildSQLExpressionFromDomainSelection(selection_domain, join_table='stock', join_column='node_uid')">
</dtml-if>
<dtml-if selection_report>
  AND <dtml-var "portal_selections.buildSQLExpressionFromDomainSelection(selection_report, strict_membership=1)">
</dtml-if>

<dtml-if group_by_expression>
GROUP BY <dtml-var group_by_expression>
</dtml-if>
<dtml-if order_by_expression>
ORDER BY
  <dtml-var order_by_expression>
</dtml-if>

