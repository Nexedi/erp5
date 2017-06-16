<dtml-let row_list="[]">
<dtml-in row_dict_dict_list prefix="outer">
DELETE FROM `transformation` WHERE
  <dtml-sqltest expr="outer_item['uid']" column="uid" type="int">
  AND
  <dtml-sqltest expr="outer_item['variation_text']" column="variation_text" type="string">
<dtml-var sql_delimiter>
<dtml-call "row_list.extend(outer_item['row_dict_list'])">
</dtml-in>

<dtml-if "len(row_list)>0">
<dtml-var sql_delimiter>

INSERT INTO `transformation`
VALUES
    <dtml-in row_list prefix="loop">
(
  <dtml-sqlvar expr="loop_item['uid']" type="int">,
  <dtml-sqlvar expr="loop_item['variation_text']" type="string">,
  <dtml-sqlvar expr="loop_item['transformed_uid']" type="int">,
  <dtml-sqlvar expr="loop_item['transformed_variation_text']" type="string">,
  <dtml-sqlvar expr="loop_item['quantity']" type="float">
)
<dtml-unless sequence-end>,</dtml-unless>
    </dtml-in>
</dtml-if>
</dtml-let>