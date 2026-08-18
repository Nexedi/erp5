DELETE FROM `measure` WHERE
  <dtml-sqltest uid column="resource_uid" type="int" multiple>

<dtml-let measure_list="[]">
  <dtml-in getMeasureRowList prefix="loop">
    <dtml-call expr="loop_item and measure_list.extend(loop_item)">
  </dtml-in>

  <dtml-if measure_list>
    <dtml-var sql_delimiter>

INSERT INTO `measure`
VALUES
    <dtml-in measure_list prefix="loop">
(
  <dtml-sqlvar expr="loop_item['uid']" type="int">,
  <dtml-sqlvar expr="loop_item['resource_uid']" type="int">,
  <dtml-sqlvar expr="loop_item['variation']" type="string">,
  <dtml-sqlvar expr="loop_item['metric_type_uid']" type="int">,
  <dtml-sqlvar expr="loop_item['quantity']" type="float">
)
<dtml-unless sequence-end>,</dtml-unless>
    </dtml-in>

  </dtml-if>
</dtml-let>
