<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string>uid\r\n
getQuantityUnitConversionDefinitionRowList\r\n
</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_catalog_quantity_unit_conversion_list</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-let quantity_unit_conversion_dict="{}" value_list="[]">\n
  <dtml-in getQuantityUnitConversionDefinitionRowList\n
 prefix="loop">\n
    <dtml-if loop_item>\n
      <dtml-comment>\n
       Make sure that we get no duplicates, and also aggregate the uids of the modified resources for deletion\n
      </dtml-comment>\n
      <dtml-in loop_item prefix="inner">\n
        <dtml-call expr="quantity_unit_conversion_dict.setdefault(inner_item[\'resource_uid\'], {}).setdefault(inner_item[\'quantity_unit_uid\'], inner_item)">\n
      </dtml-in>\n
    </dtml-if>\n
  </dtml-in>\n
\n
<dtml-if quantity_unit_conversion_dict>\n
DELETE FROM `quantity_unit_conversion` WHERE\n
  <dtml-sqltest "quantity_unit_conversion_dict.keys()" column="resource_uid" type="int" multiple>;\n
\n
\n
  <dtml-var sql_delimiter>\n
\n
<dtml-in "quantity_unit_conversion_dict.values()" prefix="loop">\n
  <dtml-call "value_list.extend(loop_item.values())">\n
</dtml-in>\n
\n
REPLACE INTO `quantity_unit_conversion`\n
VALUES\n
    <dtml-in "value_list" prefix="loop">\n
(\n
  <dtml-sqlvar expr="loop_item[\'uid\']" type="int" optional>,\n
  <dtml-sqlvar expr="loop_item[\'resource_uid\']" type="int">,\n
  <dtml-sqlvar expr="loop_item[\'quantity_unit_uid\']" type="int">,\n
  <dtml-sqlvar expr="loop_item[\'quantity\']" type="float">\n
)\n
<dtml-unless sequence-end>,</dtml-unless>\n
    </dtml-in>\n
</dtml-if>\n
\n
</dtml-let>

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
