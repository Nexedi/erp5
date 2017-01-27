DELETE FROM `measure` WHERE
<<<<<<< HEAD
  <dtml-sqltest uid column="resource_uid" type="int" multiple>
=======
  <dtml-sqltest uid column="resource_uid" type="int" multiple>;
>>>>>>> 3ce2fc0... bt5_prototype: Move erp5_mysql_innodb_catalog back to BT5 type

<dtml-let measure_list="[]">
  <dtml-in getMeasureRowList prefix="loop">
    <dtml-call expr="loop_item and measure_list.extend(loop_item)">
  </dtml-in>

  <dtml-if measure_list>
    <dtml-var sql_delimiter>

<<<<<<< HEAD
INSERT INTO `measure`
=======
REPLACE INTO `measure`
>>>>>>> 3ce2fc0... bt5_prototype: Move erp5_mysql_innodb_catalog back to BT5 type
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
