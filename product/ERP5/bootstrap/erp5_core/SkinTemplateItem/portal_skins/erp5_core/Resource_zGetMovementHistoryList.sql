SET @running_total_quantity := <dtml-var initial_running_total_quantity>,
    @running_total_price := <dtml-var initial_running_total_price>;
<dtml-var sql_delimiter>

SELECT 
  q1.*,
  @running_total_quantity := q1.total_quantity + 
            @running_total_quantity AS running_total_quantity,
  @running_total_price := IFNULL(q1.total_price, 0) + 
            @running_total_price AS running_total_price
FROM (
SELECT DISTINCT
  catalog.path as path,
  catalog.uid as uid,
  catalog.relative_url as relative_url,
  stock.date AS date_utc,
  stock.mirror_date AS mirror_date_utc,
<dtml-if expr="precision is not None">
  <dtml-if group_by_expression>SUM</dtml-if>(ROUND(stock.quantity, <dtml-var precision>)) AS total_quantity,
  <dtml-if group_by_expression>SUM</dtml-if>(ROUND(stock.total_price, <dtml-var precision>)) AS total_price,
<dtml-else>
  <dtml-if group_by_expression>SUM</dtml-if>(stock.quantity) AS total_quantity,
  <dtml-if group_by_expression>SUM</dtml-if>(stock.total_price) AS total_price,
</dtml-if>
  stock.is_cancellation AS is_cancellation,
  stock.variation_text AS variation_text,
  stock.simulation_state AS simulation_state,
  stock.resource_uid AS resource_uid,
  stock.payment_uid AS payment_uid,
  stock.mirror_section_uid AS mirror_section_uid,
  stock.mirror_node_uid AS mirror_node_uid,
  stock.function_uid AS function_uid,
  stock.project_uid AS project_uid,
  stock.funding_uid AS funding_uid,
  stock.ledger_uid AS ledger_uid,
  stock.payment_request_uid AS payment_request_uid,
  stock.node_uid AS node_uid,
  stock.section_uid AS section_uid
<dtml-if select_expression>
  ,<dtml-var select_expression>
</dtml-if>
FROM
<dtml-if from_expression>
  <dtml-var from_expression>
<dtml-else>
  stock
<dtml-in prefix="table" expr="from_table_list"> 
  <dtml-if expr="table_key != 'stock'">
  , <dtml-var table_item> AS <dtml-var table_key>
  </dtml-if>
</dtml-in>
</dtml-if>
  <dtml-if selection_domain><dtml-let expression="portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_domain, category_table_alias='domain_category')"><dtml-if expression>, <dtml-var expression></dtml-if></dtml-let></dtml-if>
  <dtml-if selection_report><dtml-let expression="portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_report, category_table_alias='report_category')"><dtml-if expression>, <dtml-var expression></dtml-if></dtml-let></dtml-if>

WHERE
  1 = 1
<dtml-if where_expression>
  AND <dtml-var where_expression>
</dtml-if>

<dtml-if omit_simulation>
  AND stock.portal_type != 'Simulation Movement'
</dtml-if>
<dtml-if only_accountable>
  AND stock.is_accountable
</dtml-if>

<dtml-if omit_input>
  AND ( ( stock.is_cancellation AND stock.quantity > 0 )
        OR ( not stock.is_cancellation AND stock.quantity < 0 ))
  AND ( stock.node_uid <> stock.mirror_node_uid
        OR stock.section_uid <> stock.mirror_section_uid
        OR stock.mirror_node_uid IS NULL
        OR stock.mirror_section_uid IS NULL
        OR stock.payment_uid IS NOT NULL )
</dtml-if>
<dtml-if omit_output>
  AND ( ( stock.is_cancellation AND stock.quantity < 0 )
        OR ( not stock.is_cancellation AND stock.quantity > 0 ))
  AND ( stock.node_uid <> stock.mirror_node_uid
        OR stock.section_uid <> stock.mirror_section_uid
        OR stock.mirror_node_uid IS NULL
        OR stock.mirror_section_uid IS NULL
        OR stock.payment_uid IS NOT NULL )
</dtml-if>
<dtml-if omit_asset_increase>
  AND ( ( stock.is_cancellation AND stock.total_price > 0 )
        OR ( not stock.is_cancellation AND stock.total_price < 0 ))
  AND ( stock.node_uid <> stock.mirror_node_uid
        OR stock.section_uid <> stock.mirror_section_uid
        OR stock.mirror_node_uid IS NULL
        OR stock.mirror_section_uid IS NULL
        OR stock.payment_uid IS NOT NULL )
</dtml-if>
<dtml-if omit_asset_decrease>
  AND ( ( stock.is_cancellation AND stock.total_price < 0 )
        OR ( not stock.is_cancellation AND stock.total_price > 0 ))
  AND ( stock.node_uid <> stock.mirror_node_uid
        OR stock.section_uid <> stock.mirror_section_uid
        OR stock.mirror_node_uid IS NULL
        OR stock.mirror_section_uid IS NULL
        OR stock.payment_uid IS NOT NULL )
</dtml-if>

<dtml-if input_simulation_state>
  <dtml-if output_simulation_state>
    <dtml-if "input_simulation_state == output_simulation_state">
      AND (<dtml-in input_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'
        <dtml-unless sequence-end> OR </dtml-unless></dtml-in>)
    <dtml-else>
      AND ((stock.quantity>0
        AND (<dtml-in input_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'
          <dtml-unless sequence-end> OR </dtml-unless></dtml-in>))
      OR (stock.quantity<0
        AND (<dtml-in output_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'
          <dtml-unless sequence-end> OR </dtml-unless></dtml-in>)))
    </dtml-if>
  <dtml-else>
    AND stock.quantity>0
    AND (<dtml-in input_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'
      <dtml-unless sequence-end> OR </dtml-unless></dtml-in>)
  </dtml-if>
<dtml-elif output_simulation_state>
  AND stock.quantity<0
  AND (<dtml-in output_simulation_state>stock.simulation_state = '<dtml-var sequence-item>'
    <dtml-unless sequence-end> OR </dtml-unless></dtml-in>)
</dtml-if>

<dtml-if selection_domain>
  AND <dtml-var "portal_selections.buildSQLExpressionFromDomainSelection(selection_domain, category_table_alias='domain_category', join_table='stock', join_column='node_uid')">
</dtml-if>
<dtml-if selection_report>
  AND <dtml-var "portal_selections.buildSQLExpressionFromDomainSelection(selection_report, category_table_alias='report_category', strict_membership=1)">
</dtml-if>

<dtml-if group_by_expression>
GROUP BY
  <dtml-var group_by_expression>
</dtml-if>

<dtml-if order_by_expression>
ORDER BY
  <dtml-var order_by_expression>
</dtml-if>

<dtml-if limit_expression>
LIMIT
  <dtml-var limit_expression>
</dtml-if>

) AS q1
<dtml-if order_by_expression>
ORDER BY
  <dtml-var order_by_expression>
</dtml-if>
