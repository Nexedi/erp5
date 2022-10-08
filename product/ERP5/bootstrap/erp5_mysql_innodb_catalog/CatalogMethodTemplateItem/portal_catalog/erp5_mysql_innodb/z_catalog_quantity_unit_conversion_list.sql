<dtml-let quantity_unit_conversion_dict="{}" value_list="[]">
  <dtml-in getQuantityUnitConversionDefinitionRowList
 prefix="loop">
    <dtml-if loop_item>
      <dtml-comment>
       Make sure that we get no duplicates, and also aggregate the uids of the modified resources for deletion
      </dtml-comment>
      <dtml-in loop_item prefix="inner">
        <dtml-call expr="quantity_unit_conversion_dict.setdefault(inner_item['resource_uid'], {}).setdefault(inner_item['quantity_unit_uid'], inner_item)">
      </dtml-in>
    </dtml-if>
  </dtml-in>

<dtml-if quantity_unit_conversion_dict>
DELETE FROM `quantity_unit_conversion` WHERE
  <dtml-sqltest expr="set(quantity_unit_conversion_dict.keys())" column="resource_uid" type="int" multiple>

  <dtml-var sql_delimiter>

<dtml-in "quantity_unit_conversion_dict.values()" prefix="loop">
  <dtml-call "value_list.extend(loop_item.values())">
</dtml-in>

INSERT INTO `quantity_unit_conversion` VALUES
    <dtml-in "value_list" prefix="loop">
(
  <dtml-sqlvar expr="loop_item['uid']" type="int" optional>,
  <dtml-sqlvar expr="loop_item['resource_uid']" type="int">,
  <dtml-sqlvar expr="loop_item['quantity_unit_uid']" type="int">,
  <dtml-sqlvar expr="loop_item['quantity']" type="float">
)
<dtml-unless sequence-end>,</dtml-unless>
    </dtml-in>
</dtml-if>

</dtml-let>